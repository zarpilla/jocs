/**
 * Pont entre el nucli narratiu i Benne (part instantània, sense accions amb temps).
 *
 * Aquest fitxer es copia a `src/game/narrative/` del projecte Benne amb
 * `npm run benne:sync`. No l'editis allà: edita `adapters/benne/runtime/`.
 */
import { defineVars, events, game, inventory, type VarValue } from '@benne/script';
import { characters, items, rooms } from '@game';
import { Narrative, type GameContent, type LocaleTable, type WorldPort } from '@aventura/narrative-core';
import bundle from './content.generated.json';
import mapping from './mapping.generated.json';

// ─── Correspondència d'identificadors (nostres → Benne) ─────────────────────
// Per defecte són iguals. Les excepcions es posen a `adapters/benne/mapping.json`.

type Kind = 'characters' | 'items' | 'rooms';
const maps = mapping as Record<Kind, Record<string, string>>;
const toBenne = (kind: Kind, id: string) => maps[kind]?.[id] ?? id;
const fromBenne = (kind: Kind, benneId: string) =>
  Object.entries(maps[kind] ?? {}).find(([, b]) => b === benneId)?.[0] ?? benneId;

type WithId = { readonly id: string };
const byId = <T extends WithId>(all: object, id: string): T | undefined =>
  (Object.values(all) as T[]).find((h) => h.id === id);

export const benneCharacter = (who: string) => byId<(typeof characters)[keyof typeof characters]>(characters, toBenne('characters', who));

// ─── El món tal com el veu Benne ────────────────────────────────────────────

const world: WorldPort = {
  hasItem: (item) => inventory.has({ id: toBenne('items', item) }),
  hasVisited: (room) => byId<{ id: string; hasVisited: boolean }>(rooms, toBenne('rooms', room))?.hasVisited ?? false,
  currentRoom: () => {
    const id = game.currentRoom?.id;
    return id ? fromBenne('rooms', id) : null;
  },
};

const { content, locales, locale } = bundle as unknown as {
  content: GameContent;
  locales: Record<string, LocaleTable>;
  locale: string;
};

export const narrative = new Narrative({ content, locales, locale, world });

// ─── Persistència: l'estat narratiu viatja dins les partides de Benne ───────

const store = defineVars({ narrativeState: null as VarValue });

narrative.on((e) => {
  switch (e.type) {
    case 'stateChanged':
      store.narrativeState = narrative.snapshot() as unknown as VarValue;
      applyObjectVisibility();
      break;
    case 'giveItem':
      inventory.add({ id: toBenne('items', e.item) });
      break;
    case 'takeItem':
      inventory.remove({ id: toBenne('items', e.item) });
      break;
    default:
      events.emit(`narrative:${e.type}`, e);
  }
});

// Partida carregada o nova: recuperem el nostre estat (buit = partida nova).
events.on('gameState:replaced', () => narrative.load(store.narrativeState));
// Canvis al món que poden completar missions o mostrar objectes.
events.on('gameState:inventoryChanged', () => narrative.worldChanged());
events.on('gameState:roomContextChanged', () => {
  boundObjects = {};
  narrative.worldChanged();
});

// ─── Objectes condicionals ──────────────────────────────────────────────────

type Showable = { visible: boolean } | { active: boolean };
let boundObjects: Record<string, Showable> = {};

/**
 * Des de l'`onEnter` d'una sala: lliga els objectes de `objects.json` als
 * props/hotspots de la sala. Es mostren o s'amaguen sols quan canvia l'estat.
 *
 *   room.onEnter(() => { bindObjects({ esquer_al_moll: esquer }) })
 */
export function bindObjects(handles: Record<string, Showable>) {
  boundObjects = { ...boundObjects, ...handles };
  applyObjectVisibility();
}

function applyObjectVisibility() {
  for (const [id, handle] of Object.entries(boundObjects)) {
    const visible = narrative.isObjectVisible(id);
    if ('visible' in handle) handle.visible = visible;
    else handle.active = visible;
  }
}

// ─── Noms traduïts al text de sota el cursor ────────────────────────────────

/** Posa els noms de personatges i objectes en l'idioma actiu. */
export function applyLocalizedNames() {
  for (const id of Object.keys(content.characters)) {
    const handle = benneCharacter(id) as { description?: string } | undefined;
    if (handle) handle.description = narrative.characterName(id);
  }
  for (const id of Object.keys(content.items)) {
    const handle = byId<WithId & { description: string }>(items, toBenne('items', id));
    if (handle) handle.description = narrative.itemName(id);
  }
}

export function setLanguage(locale: string) {
  narrative.setLocale(locale);
  applyLocalizedNames();
}
