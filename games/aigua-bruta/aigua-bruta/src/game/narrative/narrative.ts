// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
/**
 * Pont entre el nucli narratiu i Benne (part instantània, sense accions amb temps).
 *
 * Aquest fitxer es copia a `src/game/narrative/` del projecte Benne amb
 * `npm run benne:sync`. No l'editis allà: edita `adapters/benne/runtime/`.
 */
import { HotspotHandle, PropHandle, defineVars, events, game, inventory, player, setOutfit, type VarValue } from '@benne/script';
import { characters, dialogs, guis, items, rooms } from '@game';
import { Narrative, type Condition, type Effect, type GameContent, type InteractionTarget, type LocaleTable, type WorldPort } from '@aventura/narrative-core';
import { installGameLogic } from '@aventura/game/logic';
import bundle from './content.generated.json';
import mapping from './mapping.generated.json';
import { resetHistory } from './historial';
import { installStats } from './estadistiques';

// L'historial de línies és de cada joc (runtime/historial.ts del joc, o el buit per defecte).
export * from './historial';

/** El nom del joc, per als missatges de la consola. */
const JOC = (mapping as { nom?: string }).nom ?? 'Joc';
/** La carpeta del joc (`games/<id>`), per a les estadístiques. */
const JOC_ID = (mapping as { id?: string }).id ?? '';

// ─── Correspondència d'identificadors (nostres ↔ Benne) ─────────────────────
// Per defecte són iguals. Les excepcions es posen a `adapters/benne/mapping.json`.

type Kind = 'characters' | 'items' | 'rooms' | 'hotspots';
const maps = mapping as Partial<Record<Kind, Record<string, string>>>;
/**
 * La partida que es desa sola en entrar a cada sala (la carrega el botó «Continua» de la portada).
 * És aquí i no a narrative.script.ts perquè BenneScript tracta tot el que s'importa d'un .script.ts
 * com una funció de passos.
 */
export const AUTOSAVE = 'Autosave'

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
  protagonistRoom: (who) => protagonistRoom(who),
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
installStats(narrative, JOC_ID);

/** Esdeveniment de contingut que canvia de protagonista (`{ "event": "protagonista", "args": { "id": "vet" } }`). */
export const SWITCH_EVENT = 'protagonista';
let pendingSwitch: string | null = null;
/** El canvi de protagonista demanat per l'última interacció (i l'esborra). */
export function takePendingSwitch() {
  const who = pendingSwitch;
  pendingSwitch = null;
  return who;
}

/** Esdeveniment de contingut que porta la protagonista activa a una sala (`{ "event": "anar", "args": { "room": "pont" } }`). */
let pendingGoTo: string | null = null;
/** La sala on ha d'anar la protagonista per l'última interacció o diàleg (i l'esborra). */
export function takePendingGoTo() {
  const room = pendingGoTo;
  pendingGoTo = null;
  return room;
}
/**
 * Si, en acabar el que s'està dient, es canviarà de sala (una sala nova, un canvi de protagonista cap a una
 * altra sala o un final): llavors un títol al final s'ha de quedar a negre.
 */
export function leavesRoom(goTo?: string) {
  if (pendingEnding || goTo || pendingGoTo) return true;
  return pendingSwitch !== null && protagonistRoom(pendingSwitch) !== world.currentRoom();
}

/** Esdeveniment de contingut que acaba el joc amb el final que toca (`{ "event": "final" }`). */
export const ENDING_EVENT = 'final';
let pendingEnding = false;
/** Si l'última interacció ha acabat el joc (sense esborrar-ho). */
export function hasPendingEnding() {
  return pendingEnding;
}
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
  console.info(`[${JOC}] Estat narratiu adoptat de la partida`, describeState(saved));
  persisted = json;
  narrative.load(saved);
  resetHistory();
}

/** Resum curt d'un estat narratiu per als missatges de la consola. */
function describeState(state: unknown) {
  const flags = ((state as { flags?: Record<string, boolean> })?.flags ?? {});
  return Object.keys(flags).filter((f) => flags[f]).join(', ') || '(cap flag)';
}

narrative.on((e) => {
  switch (e.type) {
    case 'ending':
      // Un efecte `{ "ending": ... }` (p. ex. l'avió, al final de l'Acte 1) també acaba el joc.
      pendingEnding = true;
      break;
    case 'stateChanged':
      persist();
      applySwitchButton();
      // Els efectes s'apliquen abans de dir les línies: qui marxa (p. ex. el Director a «acceptada») ha
      // d'acabar de parlar. `playLines` l'amaga quan ja s'ha dit tot.
      applyHotspotVisibility({ keepSpeakers: true });
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
      if (e.name === 'anar') pendingGoTo = String(e.args.room);
      if (e.name === ENDING_EVENT) pendingEnding = true;
      // `situar`: una protagonista passa a ser en una altra sala (s'hi anirà en canviar-hi). Per a la que juga,
      // només té sentit si tot seguit es canvia a l'altra (en entrar a una sala, se'n torna a apuntar la sala).
      if (e.name === 'situar') rememberProtagonistRoom(String(e.args.who), String(e.args.room));
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
  console.info(`[${JOC}] Partida nova: estat narratiu inicial i inventaris inicials`);
  store.started = true;
  store.resolucio = RESOLUCIO;
  narrative.newGame();
  applyLocalizedNames();
}

// ─── Protagonistes: cada sala és d'una protagonista ─────────────────────────
// A Benne, `player.switchTo` només funciona amb personatges de la mateixa sala, i l'Iri i la Vet
// no coincideixen mai (120 anys!). Per això, canviar de protagonista = anar a la seva sala; en
// entrar-hi, prenem el control de la protagonista d'aquella sala.

/** La protagonista d'una sala (`protagonist` al JSON de la sala). Les sales compartides no en tenen cap de fixa. */
export const roomProtagonist = (room: string) => content.rooms[room]?.protagonist ?? null;
/** Si hi poden ser les dues protagonistes (`protagonists` al JSON de la sala). */
export const isSharedRoom = (room: string) => (content.rooms[room]?.protagonists?.length ?? 0) > 0;

/**
 * Qui entrarà a la sala següent, quan es canvia de protagonista cap a una sala compartida: en entrar-hi
 * no es pot saber per la sala (hi pot ser qualsevol de les dues). Ho posa `goToProtagonist`.
 */
let entering: string | null = null;
export function setEnteringProtagonist(who: string | null) {
  entering = who;
}
export function takeEnteringProtagonist() {
  const who = entering;
  entering = null;
  return who;
}

const music = (mapping as { music?: Record<string, string> }).music ?? {};
/**
 * La música d'ambient d'una sala (`music` al mapping.json del joc): la de la sala, o si no en té, la de
 * la seva protagonista. `null`: continua la que sonava (p. ex. a les cinemàtiques).
 */
export function roomMusic(room: string): string | null {
  const who = roomProtagonist(room);
  return music[room] ?? (who ? music[who] : undefined) ?? null;
}
/** Si totes les pistes duren el mateix i, en canviar-ne, la nova continua al mateix punt (`musicSync`). */
export const musicSync = (mapping as { musicSync?: boolean }).musicSync === true;

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
 * El botó «Canvia» (a la barra de verbs i, si el joc el té, al menú) només hi és quan el jugador pot
 * canviar de protagonista (`switchWhen` a game.json).
 */
export function applySwitchButton() {
  const pot = narrative.canSwitch();
  guis.verbs.controls.canviaBtn.visible = pot;
  const menu = guis.gameMenu.controls as unknown as Record<string, { visible: boolean } | undefined>;
  if (menu.canviar) menu.canviar.visible = pot;
}

/** `keepSpeakers`: els personatges que s'han d'amagar es queden fins que `playLines` acabi (poden parlar). */
export function applyHotspotVisibility({ keepSpeakers = false } = {}) {
  const room = world.currentRoom();
  if (!room) return;
  for (const { id, visible } of narrative.hotspotsIn(room)) {
    // Un personatge amb `visibleIf` (p. ex. la Directora a la cel·la a l'Acte 3) s'amaga o es mostra sencer.
    const character = content.characters[id] ? (benneCharacter(id) as Showable | undefined) : undefined;
    if (keepSpeakers && character && !visible) continue;
    const zone = zones[room]?.includes(id) ? new HotspotHandle(toBenne('rooms', room), toBenne('hotspots', id)) : undefined;
    const handle = boundHotspots[id] ?? character ?? zone ?? new PropHandle(toBenne('rooms', room), toBenne('hotspots', id));
    if ('visible' in handle) handle.visible = visible;
    else handle.active = visible;
  }
  applyCharacterVisibility(room, keepSpeakers);
}

/**
 * Benne desa si un personatge es veu per personatge, no per sala: si en Tomàs es mostra al bar, la seva
 * veu (invisible) a l'estudi també sortiria. Per això, a cada sala es torna a decidir qui es veu: els
 * personatges que hi són com a cosa i la protagonista, sí; la resta (les veus), no.
 */
function applyCharacterVisibility(room: string, keepSpeakers = false) {
  const def = content.rooms[room];
  if (!def) return;
  for (const id of Object.keys(content.characters)) {
    // Els que tenen `visibleIf` ja els ha decidit `applyHotspotVisibility`.
    if (def.hotspots[id]?.visibleIf) continue;
    // La protagonista de la sala, no la que juga ara: en entrar, el canvi de protagonista encara no s'ha fet
    // i l'altra (que aquí és una veu) sortiria. A les sales sense protagonista (cinemàtiques, finals) les
    // protagonistes només hi són com a veus: no s'hi veu ningú que no sigui a `hotspots`.
    let visible = id in def.hotspots || id === def.protagonist;
    // A una sala compartida, l'altra protagonista es veu si també hi és.
    if (def.protagonists?.includes(id)) visible = id === world.activeProtagonist() || protagonistRoom(id) === room;
    const handle = benneCharacter(id) as { visible: boolean } | undefined;
    // L'altra protagonista se'n va (`situar`) mentre parla: s'amaga quan acabi (`playLines`).
    if (keepSpeakers && !visible && handle?.visible && def.protagonists?.includes(id)) continue;
    if (handle && handle.visible !== visible) handle.visible = visible;
  }
}

// ─── Aspecte dels personatges segons l'estat (`appearance` a characters.json) ──

export function applyAppearances() {
  for (const [id, def] of Object.entries(content.characters)) {
    // La roba (`outfit`): el motor (pegat) busca `<roba><Idle|Walk|Talk><dir>` abans que les normals.
    if (def.outfit?.length) setOutfit(toBenne('characters', id), narrative.outfitOf(id));
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

// ─── On és cada personatge segons l'estat (`place` a characters.json) ────────

type Movable = { position: { x: number; y: number }; moveTo(p: { x: number; y: number }): void; walkTo: { now(p: { x: number; y: number }): unknown } };

/**
 * Posa cada personatge de la sala on diu `place`. Amb `walk`, hi camina (l'estat ha canviat mentre s'hi era);
 * si no, hi és de cop (en entrar a la sala o carregar una partida). Benne desa la posició amb la partida.
 */
export function applyPlaces(walk: boolean) {
  const room = world.currentRoom();
  if (!room) return;
  for (const id of Object.keys(content.characters)) {
    const to = narrative.placeOf(id, room);
    if (!to) continue;
    const handle = benneCharacter(id) as unknown as Movable | undefined;
    if (!handle) continue;
    const at = handle.position;
    if (Math.hypot(at.x - to.x, at.y - to.y) < 2) continue;
    if (walk) handle.walkTo.now(to);
    else handle.moveTo(to);
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

// ─── Provar una situació (només en desenvolupament) ───────────────────────────

/** Una situació de partida: l'estat narratiu, on és cada protagonista, què porta i qui juga. */
export interface Situacio {
  state: unknown;
  rooms: Record<string, string>;
  items: Record<string, string[]>;
  active: string;
}

/**
 * Posa la partida en una situació concreta (la que deixa un test de partida a mig jugar), per veure-la sense
 * jugar-la. La fa servir `window.__aventura.provar(...)` (només amb `npm run dev`); torna la sala on s'ha d'anar.
 */
export function prepareSituation(s: Situacio): string {
  ensureStarted();
  narrative.load(s.state);
  persist();
  store.protagonistRooms = { ...s.rooms } as VarValue;
  for (const who of content.manifest.protagonists) {
    const bag = bagOf(who);
    for (const id of Object.keys(content.items)) if (bag.has(itemRef(id))) bag.remove(itemRef(id));
    for (const id of s.items[who] ?? []) bag.add(itemRef(id));
  }
  return s.rooms[s.active] ?? '';
}

export function setLanguage(locale: string) {
  narrative.setLocale(locale);
  applyLocalizedNames();
}

// ─── Provar els finals (`?final=` a l'adreça, només en desenvolupament) ──────

/**
 * Per veure un final sense jugar-lo: una partida nova amb l'estat que el fa sortir. Es compleix sola la
 * condició del final (`when`), i a l'adreça s'hi pot afegir més estat, per a les línies i els personatges
 * que depenen d'altres coses:
 *   `flags=a,b,!c`         marques (amb `!`, a fals)
 *   `vars=aliats:4,x:text`  variables (si és un número, com a número)
 * Ex.: `?final=final_taula&flags=aliat_ballester,aliat_neta,aliada_rius,aliada_pons,tap_tornat`
 */
export function prepareEndingPreview(id: string, query: URLSearchParams) {
  ensureStarted()
  const effects: Effect[] = [...satisfy(content.endings[id]?.when)]
  for (const f of (query.get('flags') ?? '').split(',').map((x) => x.trim()).filter(Boolean)) {
    effects.push(f.startsWith('!') ? { setFlag: f.slice(1), value: false } : { setFlag: f })
  }
  for (const pair of (query.get('vars') ?? '').split(',').map((x) => x.trim()).filter(Boolean)) {
    const [k, v = ''] = pair.split(':')
    if (k) effects.push({ setVar: k, value: v !== '' && !Number.isNaN(Number(v)) ? Number(v) : v })
  }
  if (effects.length) narrative.apply(effects)
  console.info(`[final] ${id}:`, effects)
}

/** Els efectes que fan complir una condició (els casos senzills: marques, variables, `all`, `any`). */
function satisfy(c: Condition | undefined): Effect[] {
  if (!c) return []
  if ('all' in c) return c.all.flatMap(satisfy)
  if ('any' in c) return satisfy(c.any[0])
  if ('flag' in c) return [{ setFlag: c.flag, value: c.is ?? true }]
  if ('var' in c) {
    const n = typeof c.value === 'number' ? c.value : null
    if (c.op === '>' && n !== null) return [{ setVar: c.var, value: n + 1 }]
    if (c.op === '<' && n !== null) return [{ setVar: c.var, value: n - 1 }]
    if (c.op === '==' || c.op === '>=' || c.op === '<=') return [{ setVar: c.var, value: c.value }]
  }
  return []
}
