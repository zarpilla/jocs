/**
 * Pont entre el nucli narratiu i Benne (part instantània, sense accions amb temps).
 *
 * Aquest fitxer es copia a `src/game/narrative/` del projecte Benne amb
 * `npm run benne:sync`. No l'editis allà: edita `adapters/benne/runtime/`.
 */
import { defineVars, events, game, inventory, player, type VarValue } from '@benne/script';
import { characters, dialogs, items, rooms } from '@game';
import { Narrative, type GameContent, type InteractionTarget, type LocaleTable, type WorldPort } from '@aventura/narrative-core';
import { installGameLogic } from '@aventura/game/logic';
import bundle from './content.generated.json';
import mapping from './mapping.generated.json';

// ─── Correspondència d'identificadors (nostres ↔ Benne) ─────────────────────
// Per defecte són iguals. Les excepcions es posen a `adapters/benne/mapping.json`.

type Kind = 'characters' | 'items' | 'rooms' | 'hotspots';
const maps = mapping as Partial<Record<Kind, Record<string, string>>>;
export const toBenne = (kind: Kind, id: string) => maps[kind]?.[id] ?? id;
export const fromBenne = (kind: Kind, benneId: string) =>
  Object.entries(maps[kind] ?? {}).find(([, b]) => b === benneId)?.[0] ?? benneId;

type WithId = { readonly id: string };
const byId = <T extends WithId>(all: object, id: string): T | undefined =>
  (Object.values(all) as T[]).find((h) => h.id === id);

export const benneCharacter = (who: string) => byId<(typeof characters)[keyof typeof characters]>(characters, toBenne('characters', who));
export const benneRoom = (id: string) => byId<(typeof rooms)[keyof typeof rooms]>(rooms, toBenne('rooms', id));
export const benneDialog = (id: string) => byId<(typeof dialogs)[keyof typeof dialogs]>(dialogs, id);

/** Inventari d'una protagonista (sense `who`, la que juga ara). */
const bagOf = (who?: string) => (who ? (benneCharacter(who)?.inventory ?? inventory) : inventory);
const itemRef = (id: string) => ({ id: toBenne('items', id) });

// ─── El món tal com el veu Benne ────────────────────────────────────────────

const world: WorldPort = {
  hasItem: (item, who) => bagOf(who).has(itemRef(item)),
  hasVisited: (room) => benneRoom(room)?.hasVisited ?? false,
  currentRoom: () => {
    const id = game.currentRoom?.id;
    return id ? fromBenne('rooms', id) : null;
  },
  activeProtagonist: () => fromBenne('characters', player.id),
};

const { content, locales, locale } = bundle as unknown as {
  content: GameContent;
  locales: Record<string, LocaleTable>;
  locale: string;
};

export const narrative = new Narrative({ content, locales, locale, world });
installGameLogic(narrative);

/** Esdeveniment de contingut que canvia de protagonista (`{ "event": "protagonista", "args": { "id": "vet" } }`). */
export const SWITCH_EVENT = 'protagonista';
let pendingSwitch: string | null = null;
/** El canvi de protagonista demanat per l'última interacció (i l'esborra). */
export function takePendingSwitch() {
  const who = pendingSwitch;
  pendingSwitch = null;
  return who;
}

// ─── Persistència: l'estat narratiu viatja dins les partides de Benne ───────

const store = defineVars({ narrativeState: null as VarValue });

narrative.on((e) => {
  switch (e.type) {
    case 'stateChanged':
      store.narrativeState = narrative.snapshot() as unknown as VarValue;
      applyHotspotVisibility();
      break;
    case 'giveItem':
      bagOf(e.who).add(itemRef(e.item));
      break;
    case 'takeItem':
      bagOf(e.who).remove(itemRef(e.item));
      break;
    case 'custom':
      if (e.name === SWITCH_EVENT) pendingSwitch = String(e.args.id);
      events.emit(`narrative:${e.name}`, e.args);
      break;
    default:
      events.emit(`narrative:${e.type}`, e);
  }
});

// Partida carregada o nova. Sense estat desat = partida nova: inventaris inicials.
events.on('gameState:replaced', () => {
  if (store.narrativeState) narrative.load(store.narrativeState);
  else narrative.newGame();
  applyLocalizedNames();
});
// Canvis al món que poden completar missions o mostrar coses.
events.on('gameState:inventoryChanged', () => narrative.worldChanged());
events.on('gameState:roomContextChanged', () => {
  boundHotspots = {};
  narrative.worldChanged();
});

// ─── Interaccions: d'un clic de Benne a una petició al nucli ────────────────

/** Benne anomena les coses de sala `<sala>-hotspot-<nom>` o similar: en traiem el nostre id. */
export function targetFromBenne(kind: 'prop' | 'hotspot' | 'character' | 'item', benneId: string): InteractionTarget {
  if (kind === 'item') return { kind: 'item', id: fromBenne('items', benneId) };
  if (kind === 'character') return { kind: 'character', id: fromBenne('characters', benneId) };
  const room = world.currentRoom() ?? '';
  const mapped = fromBenne('hotspots', benneId);
  const stripped = mapped.replace(new RegExp(`^${toBenne('rooms', room)}-(hotspot|prop)-`), '');
  return { kind: 'hotspot', id: stripped };
}

// ─── Coses condicionals ─────────────────────────────────────────────────────

type Showable = { visible: boolean } | { active: boolean };
let boundHotspots: Record<string, Showable> = {};

/**
 * Des de l'`onEnter` d'una sala: lliga les coses amb `visibleIf` del JSON de la
 * sala als props/hotspots de Benne. Es mostren o s'amaguen sols.
 *
 *   room.onEnter(() => { bindHotspots({ segell, plomall }) })
 */
export function bindHotspots(handles: Record<string, Showable>) {
  boundHotspots = { ...boundHotspots, ...handles };
  applyHotspotVisibility();
}

function applyHotspotVisibility() {
  const room = world.currentRoom();
  if (!room) return;
  for (const [id, handle] of Object.entries(boundHotspots)) {
    const visible = narrative.isHotspotVisible(room, id);
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
