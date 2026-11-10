/**
 * Pont entre el nucli narratiu i Benne (part instantània, sense accions amb temps).
 *
 * Aquest fitxer es copia a `src/game/narrative/` del projecte Benne amb
 * `npm run benne:sync`. No l'editis allà: edita `adapters/benne/runtime/`.
 */
import { HotspotHandle, PropHandle, defineVars, events, game, inventory, player, type VarValue } from '@benne/script';
import { characters, dialogs, guis, items, rooms } from '@game';
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

/**
 * Nom de l'opció de Benne per a una opció d'un node (el genera el sync).
 * Ha de ser aquí i no a `narrative.script.ts`: allà el plugin BenneScript converteix totes les
 * funcions en asíncrones i retornaria una `Promise` en lloc del nom.
 */
export const optionName = (node: string, choice: string) => `${node}__${choice}`;

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

const { content, locales, locale, zones } = bundle as unknown as {
  content: GameContent;
  locales: Record<string, LocaleTable>;
  locale: string;
  /** Coses amb `visibleIf` que a Benne són zones (hotspots), no props. Sala → ids. */
  zones: Record<string, string[]>;
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

/** Esdeveniment de contingut que acaba el joc amb el final que toca (`{ "event": "final" }`). */
export const ENDING_EVENT = 'final';
let pendingEnding = false;
/** Si l'última interacció ha acabat el joc (i ho esborra). */
export function takePendingEnding() {
  const yes = pendingEnding;
  pendingEnding = false;
  return yes;
}

// ─── Persistència: l'estat narratiu viatja dins les partides de Benne ───────

const store = defineVars({
  narrativeState: null as VarValue,
  /**
   * La partida ja s'ha preparat (`newGame`). No n'hi ha prou amb `narrativeState`: qualsevol
   * `stateChanged` (p. ex. el `worldChanged` en entrar a la primera sala) el desa abans d'hora.
   */
  started: false as VarValue,
  /** Última sala de cada protagonista: per tornar-hi en canviar de protagonista. */
  protagonistRooms: {} as VarValue,
  /** Resolució amb què es van desar les posicions dels personatges (null: partida de 352×198). */
  resolucio: null as VarValue,
});

/** L'últim estat narratiu que hem desat a la partida (en JSON), per saber si algú l'ha substituït. */
let persisted: string | null = null;

function persist() {
  const snapshot = narrative.snapshot();
  store.narrativeState = snapshot as unknown as VarValue;
  persisted = JSON.stringify(snapshot);
}

/**
 * Si la partida porta un estat narratiu que no és el que hi hem desat (s'ha carregat una partida o
 * se n'ha començat una de nova), el carrega. Cal fer-ho abans de reaccionar a qualsevol canvi:
 * en carregar, Benne avisa del canvi de sala i d'inventari abans que de `gameState:replaced`, i
 * si llavors reavaluéssim el món amb l'estat vell, el desaríem damunt del carregat.
 */
export function adoptLoadedState() {
  const saved = store.narrativeState;
  // Sense estat a la partida no hi ha res a adoptar: una partida nova la prepara `ensureStarted`.
  if (!saved) return;
  const json = JSON.stringify(saved);
  if (json === persisted) return;
  console.info('[Ferro-9] Estat narratiu adoptat de la partida', describeState(saved));
  persisted = json;
  narrative.load(saved);
  historial.length = 0;
}

/** Resum curt d'un estat narratiu per als missatges de la consola. */
function describeState(state: unknown) {
  const flags = ((state as { flags?: Record<string, boolean> })?.flags ?? {});
  return Object.keys(flags).filter((f) => flags[f]).join(', ') || '(cap flag)';
}

narrative.on((e) => {
  switch (e.type) {
    case 'stateChanged':
      persist();
      applySwitchButton();
      applyHotspotVisibility();
      applyAppearances();
      break;
    case 'giveItem':
      bagOf(e.who).add(itemRef(e.item));
      break;
    case 'takeItem':
      bagOf(e.who).remove(itemRef(e.item));
      break;
    case 'custom':
      if (e.name === SWITCH_EVENT) pendingSwitch = String(e.args.id);
      if (e.name === ENDING_EVENT) pendingEnding = true;
      events.emit(`narrative:${e.name}`, e.args);
      break;
    default:
      events.emit(`narrative:${e.type}`, e);
  }
});

// ─── Partides desades a 352×198 ─────────────────────────────────────────────
// Benne desa dins la partida la posició de cada personatge a cada sala, i en tornar-hi la fa servir.
// Les partides d'abans de passar a 480×270 les tenen en coordenades velles: els personatges quedarien
// enlairats (i els que no es mouen, com el capatàs, les arrossegarien per sempre). S'escalen una vegada.
const RESOLUCIO = 480;
const ESCALA_ANTIGA = RESOLUCIO / 352;
/** Per sota d'aquesta alçada no hi ha cap peu a 480×270 (el terra comença més avall). */
const TERRA_MINIM = 155;

function migrateOldPositions() {
  if (store.resolucio === RESOLUCIO) return;
  for (const room of Object.keys(content.rooms)) {
    for (const id of Object.keys(content.characters)) {
      const key = `room:${toBenne('rooms', room)}:character:${toBenne('characters', id)}:position`;
      const saved = defineVars({ [key]: null as VarValue });
      const pos = saved[key] as { x?: number; y?: number } | null;
      if (!pos || typeof pos.x !== 'number' || typeof pos.y !== 'number' || pos.y >= TERRA_MINIM) continue;
      saved[key] = { x: Math.round(pos.x * ESCALA_ANTIGA), y: Math.round(pos.y * ESCALA_ANTIGA) };
    }
  }
  store.resolucio = RESOLUCIO;
}

// Partida carregada (o nova: aleshores l'estat és buit i `ensureStarted` la prepara en entrar a la primera sala).
events.on('gameState:replaced', () => {
  migrateOldPositions();
  adoptLoadedState();
  applyLocalizedNames();
});

/** Partida nova: reparteix els inventaris inicials (game.json → start). Només la primera vegada. */
export function ensureStarted() {
  if (store.started) return;
  console.info('[Ferro-9] Partida nova: estat narratiu inicial i inventaris inicials');
  store.started = true;
  store.resolucio = RESOLUCIO;
  narrative.newGame();
  applyLocalizedNames();
}

// ─── Protagonistes: cada sala és d'una protagonista ─────────────────────────
// A Benne, `player.switchTo` només funciona amb personatges de la mateixa sala, i l'Iri i la Vet
// no coincideixen mai (120 anys!). Per això, canviar de protagonista = anar a la seva sala; en
// entrar-hi, prenem el control de la protagonista d'aquella sala.

/** La protagonista d'una sala (`protagonist` al JSON de la sala). */
export const roomProtagonist = (room: string) => content.rooms[room]?.protagonist ?? null;

/** La música d'ambient de les sales d'una protagonista (`music` a `adapters/benne/mapping.json`). */
export const protagonistMusic = (who: string) => (mapping as { music?: Record<string, string> }).music?.[who] ?? null;

/** On és (o era) cada protagonista. */
export function protagonistRoom(who: string): string | null {
  const rooms = (store.protagonistRooms ?? {}) as Record<string, string>;
  return rooms[who] ?? content.manifest.start?.[who]?.room ?? null;
}

export function rememberProtagonistRoom(who: string, room: string) {
  store.protagonistRooms = { ...((store.protagonistRooms ?? {}) as Record<string, string>), [who]: room };
}
// Canvis al món que poden completar missions o mostrar coses.
events.on('gameState:inventoryChanged', () => {
  adoptLoadedState();
  narrative.worldChanged();
});
events.on('gameState:roomContextChanged', () => {
  boundHotspots = {};
  adoptLoadedState();
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

// ─── Girar-se cap a la cosa clicada ─────────────────────────────────────────

type Point = { x: number; y: number };
type RoomThing = { id: string; lookAtPoint?: Point; points?: Point[]; collider?: { points: Point[] } };
type RoomFile = { id: string; hotspots: RoomThing[]; props: RoomThing[] };
const roomFiles = Object.values(import.meta.glob<RoomFile>('../rooms/*/*.room.json', { eager: true, import: 'default' }));

const centre = (pts: Point[]) => ({ x: pts.reduce((a, p) => a + p.x, 0) / pts.length, y: pts.reduce((a, p) => a + p.y, 0) / pts.length });

/** On mira una cosa de la sala o un personatge (en píxels de la sala), o `null` si no se sap. */
function lookPoint(kind: 'prop' | 'hotspot' | 'character', benneId: string): Point | null {
  if (kind === 'character') {
    const handle = benneCharacter(fromBenne('characters', benneId)) as { position?: Point } | undefined;
    return handle?.position ?? null;
  }
  const room = roomFiles.find((r) => r.id === toBenne('rooms', world.currentRoom() ?? ''));
  const thing = (kind === 'prop' ? room?.props : room?.hotspots)?.find((t) => t.id === benneId);
  if (!thing) return null;
  const pts = thing.collider?.points ?? thing.points;
  return thing.lookAtPoint ?? (pts?.length ? centre(pts) : null);
}

/** Cap on s'ha de girar la protagonista (des d'on és ara) per mirar la cosa, o `null`. */
export function facingToward(kind: 'prop' | 'hotspot' | 'character' | 'item', benneId: string): 'U' | 'D' | 'L' | 'R' | null {
  if (kind === 'item') return null;
  const to = lookPoint(kind, benneId);
  if (!to) return null;
  const from = player.position;
  const dx = to.x - from.x;
  const dy = to.y - from.y;
  if (Math.hypot(dx, dy) < 2) return null;
  return Math.abs(dx) >= Math.abs(dy) ? (dx < 0 ? 'L' : 'R') : dy < 0 ? 'U' : 'D';
}

// ─── Coses condicionals ─────────────────────────────────────────────────────
// Les coses amb `visibleIf` són props a Benne (el sync les crea així): es mostren o
// s'amaguen soles cada vegada que canvia l'estat. Si a Benne ja eren zones (hotspots), s'activen o
// es desactiven.

type Showable = { visible: boolean } | { active: boolean };
let boundHotspots: Record<string, Showable> = {};

/** Per a casos especials: lliga a mà una cosa amb `visibleIf` a un handle concret (hotspot, personatge...). */
export function bindHotspots(handles: Record<string, Showable>) {
  boundHotspots = { ...boundHotspots, ...handles };
  applyHotspotVisibility();
}

/**
 * El botó «Canvia» (a la barra de verbs i al menú) només hi és quan el jugador pot canviar de
 * protagonista (`switchWhen` a game.json).
 */
export function applySwitchButton() {
  const pot = narrative.canSwitch();
  guis.verbs.controls.canviaBtn.visible = pot;
  guis.gameMenu.controls.canviar.visible = pot;
}

export function applyHotspotVisibility() {
  const room = world.currentRoom();
  if (!room) return;
  for (const { id, visible } of narrative.hotspotsIn(room)) {
    // Un personatge amb `visibleIf` (p. ex. la Directora a la cel·la a l'Acte 3) s'amaga o es mostra sencer.
    const character = content.characters[id] ? (benneCharacter(id) as Showable | undefined) : undefined;
    const zone = zones[room]?.includes(id) ? new HotspotHandle(toBenne('rooms', room), toBenne('hotspots', id)) : undefined;
    const handle = boundHotspots[id] ?? character ?? zone ?? new PropHandle(toBenne('rooms', room), toBenne('hotspots', id));
    if ('visible' in handle) handle.visible = visible;
    else handle.active = visible;
  }
}

// ─── Aspecte dels personatges segons l'estat (`appearance` a characters.json) ──

export function applyAppearances() {
  for (const [id, def] of Object.entries(content.characters)) {
    if (!def.appearance?.length) continue;
    // Les animacions del JSON són text; Benne les tipa amb les etiquetes del sprite.
    const handle = benneCharacter(id) as { animation: string; stopAnimation(): void } | undefined;
    if (!handle) continue;
    const anim = narrative.appearanceOf(id);
    if (anim) {
      if (handle.animation !== anim) handle.animation = anim;
    } else if (def.appearance.some((a) => a.anim === handle.animation)) {
      handle.stopAnimation();
    }
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

// ─── Historial: les últimes línies dites, per tornar a llegir les que han passat massa de pressa ──

const HISTORIAL_MAX = 80;
const historial: { who: string | null; text: string }[] = [];

/** Apunta una línia a l'historial (els títols no). `who`: un personatge, `player` o `narrator`. */
export function recordLine(who: string, text: string) {
  if (who === 'title') return;
  const id = who === 'player' ? narrative.world.activeProtagonist() : who;
  historial.push({ who: who === 'narrator' ? null : narrative.characterName(id), text });
  if (historial.length > HISTORIAL_MAX) historial.shift();
}

/**
 * Les últimes línies de l'historial que caben en `rows` files de `perRow` caràcters, la més nova
 * a baix. Si no n'hi ha cap, `empty`.
 */
export function historyText(empty: string, rows: number, perRow: number) {
  const out: string[] = [];
  let used = 0;
  for (let i = historial.length - 1; i >= 0; i--) {
    const { who, text } = historial[i]!;
    const line = who ? `${who}: ${text}` : text;
    const n = Math.ceil(line.length / perRow);
    if (used + n > rows && out.length) break;
    out.unshift(line);
    used += n;
  }
  return out.length ? out.join('\n') : empty;
}
