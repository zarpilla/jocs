/**
 * Pont entre el nucli narratiu i Benne (part instantània, sense accions amb temps).
 *
 * Aquest fitxer es copia a `src/game/narrative/` del projecte Benne amb
 * `npm run benne:sync`. No l'editis allà: edita `adapters/benne/runtime/`.
 */
import { HotspotHandle, PropHandle, ambient, camera, defineVars, events, game, inventory, player, setOutfit, shade, type FallbackTarget, type VarValue } from '@benne/script';
import { characters, dialogs, guis, items, rooms } from '@game';
import { Narrative, type StageCue, type Condition, type Effect, type GameContent, type InteractionTarget, type LocaleTable, type WorldPort } from '@aventura/narrative-core';
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
/** Amplada de la pantalla del joc (game-config.json, via el sync). */
export const AMPLADA = (mapping as { resolucio?: { width?: number } }).resolucio?.width ?? 480;

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

// ─── Veus ────────────────────────────────────────────────────────────────────
// Les genera `npm run veus` (tools/veus.py) a `game/audio/voice/` i el sync les copia a `assets/audio/voice/`.
// Cada fitxer és `<personatge de Benne><número>`, i el número surt de la clau del text: si la frase canvia de
// lloc o d'ordre, la veu la segueix. Benne fa sonar la veu si la línia comença amb `|<número>|`, i la bafarada dura
// el que duri l'àudio.

/**
 * Si han de sonar: `veus` del mapping (el posa el sync segons `"actiu"` de veus.json). Amb `'url'`, només amb
 * `?voices=on` a l'adreça; amb `'sempre'`, sempre, tret de `?voices=off`.
 */
const voicesOn = (() => {
  const mode = (mapping as { veus?: 'sempre' | 'url' | null }).veus ?? null;
  const param = typeof location === 'undefined' ? null : new URLSearchParams(location.search).get('voices');
  return mode === 'sempre' ? param !== 'off' : mode === 'url' && param === 'on';
})();

const voiceStems = new Set(
  Object.keys(import.meta.glob('../assets/audio/voice/*.{mp3,ogg,wav}', { query: '?url', import: 'default' }))
    .map((path) => path.slice(path.lastIndexOf('/') + 1).replace(/\.[^.]+$/, '')),
);

/** El número de veu d'una clau de text: FNV-1a de 32 bits, en decimal (el mateix que calcula tools/veus.py). */
export function voiceNumber(key: string): string {
  let h = 0x811c9dc5;
  for (const byte of new TextEncoder().encode(key)) h = Math.imul(h ^ byte, 0x01000193) >>> 0;
  return String(h);
}

/**
 * El número de la veu que `benneId` té gravada per a una línia, o `null`. Primer per la clau; les línies amb variables
 * («{observacions} de 12») es graven un cop per valor, amb el número de la clau i el text tal com surt (`clau|5 de 12`).
 */
function recordedVoiceNumber(benneId: string, key: string | undefined, text: string | undefined): string | null {
  if (!key || !voicesOn || !voiceStems.size) return null;
  for (const n of [voiceNumber(key), ...(text === undefined ? [] : [voiceNumber(`${key}|${text}`)])]) {
    if (voiceStems.has(`${benneId}${n}`)) return n;
  }
  return null;
}

/** El text d'una línia amb la marca de veu davant, si `benneId` la té gravada. */
export function voiced(benneId: string, key: string | undefined, text: string): string {
  const n = recordedVoiceNumber(benneId, key, text);
  return n === null ? text : `|${n}| ${text}`;
}

/** La veu (`<personatge de Benne><número>`) d'una línia, si n'hi ha i han de sonar. */
function lineVoiceStem(who: string, key: string | undefined, text: string | undefined): string | null {
  const benneId = who === 'player' ? player.id : who === 'narrator' ? 'narrator' : benneCharacter(who)?.id;
  if (!benneId) return null;
  const n = recordedVoiceNumber(benneId, key, text);
  return n === null ? null : `${benneId}${n}`;
}

/**
 * Demana al motor, per endavant, les veus d'unes línies que es diran tot seguit (una interacció, un pas de diàleg, les
 * opcions que es poden triar). Benne no les carrega en arrencar: així, quan arriba la línia, ja hi són.
 */
export function preloadLineVoices(lines: readonly { who: string; key?: string; text?: string }[]) {
  const stems = lines.map((l) => lineVoiceStem(l.who, l.key, l.text)).filter((s): s is string => s !== null);
  if (stems.length) game.preloadVoices(stems);
}

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

/**
 * Objectes que una interacció ha donat i que encara no són a l'inventari. Els efectes s'apliquen abans de dir les
 * línies, i l'objecte sortia mentre la protagonista encara deia la línia d'abans de rebre'l (el salabre d'en Joanet):
 * entren a l'inventari quan el joc deixa d'estar ocupat (s'acaben les línies, la conversa o l'escena). Per a l'estat,
 * ja hi són (`hasItem`).
 */
/** De qui és una bossa: `bagOf` torna un objecte nou a cada crida, i sense `who` és la de qui juga ara. */
const ownerOf = (who?: string) => who ?? fromBenne('characters', player.id);
const pendingGives: { owner: string; item: string; replaces?: string }[] = [];
const isPendingGive = (who: string | undefined, item: string) => {
  const owner = ownerOf(who);
  return pendingGives.findIndex((g) => g.owner === owner && g.item === item);
};

/**
 * Objectes que una interacció ha tret i que un objecte donat a la mateixa interacció substituirà (el formulari que passa
 * a segellat): per a l'estat ja no hi són, però es queden a la seva casella fins que hi entra el nou, perquè la jugadora
 * el trobi on tenia l'altre i la resta no canviï de lloc.
 */
const pendingTakes: { owner: string; item: string; paired: boolean }[] = [];
const isPendingTake = (who: string | undefined, item: string) => {
  const owner = ownerOf(who);
  return pendingTakes.some((t) => t.owner === owner && t.item === item);
};

/** Al final dels efectes d'una interacció: cada objecte tret s'aparella amb un de donat a la mateixa bossa, o surt. */
function resolvePendingTakes() {
  for (let i = pendingTakes.length - 1; i >= 0; i--) {
    const t = pendingTakes[i];
    if (t.paired) continue;
    const g = pendingGives.find((g) => g.owner === t.owner && g.replaces === undefined);
    if (g) {
      g.replaces = t.item;
      t.paired = true;
    } else {
      pendingTakes.splice(i, 1);
      bagOf(t.owner).remove(itemRef(t.item));
    }
  }
}

/** Posa `item` a la bossa al lloc de `old` (si hi és), i deixa la resta d'objectes on eren. */
function replaceInBag(bag: ReturnType<typeof bagOf>, old: string, item: string) {
  const oldId = toBenne('items', old);
  const slot = bag.items.findIndex((e) => e.item.id === oldId);
  if (slot >= 0) bag.remove(itemRef(old));
  bag.add(itemRef(item));
  if (slot < 0) return;
  const newId = toBenne('items', item);
  // Benne només afegeix al final: els que anaven darrere de l'antic tornen a entrar darrere del nou.
  for (const e of bag.items.slice(slot)) {
    if (e.item.id === newId) continue;
    bag.remove(e.item, e.quantity);
    bag.add(e.item, e.quantity);
  }
}

/** Posa a l'inventari els objectes donats que esperaven. */
export function flushPendingGives() {
  for (const g of pendingGives.splice(0)) {
    if (g.replaces === undefined) {
      bagOf(g.owner).add(itemRef(g.item));
      continue;
    }
    const t = pendingTakes.findIndex((t) => t.owner === g.owner && t.item === g.replaces);
    if (t >= 0) pendingTakes.splice(t, 1);
    replaceInBag(bagOf(g.owner), g.replaces, g.item);
  }
}

function giveWhenIdle() {
  const tick = () => {
    if (!pendingGives.length) return;
    if (game.isBusy) window.setTimeout(tick, 150);
    else flushPendingGives();
  };
  // Una mica més tard que de seguida: les línies de la interacció comencen just després dels efectes.
  window.setTimeout(tick, 200);
}

const world: WorldPort = {
  hasItem: (item, who) =>
    (bagOf(who).has(itemRef(item)) && !isPendingTake(who, item)) || isPendingGive(who, item) >= 0,
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
  pendingGives.length = 0;
  pendingTakes.length = 0;
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
      // d'acabar de parlar, i qui arriba no ha de sortir abans. `playLines` ho posa al dia en acabar.
      applyHotspotVisibility({ keepSpeakers: true });
      applyAppearances();
      break;
    case 'giveItem':
      pendingGives.push({ owner: ownerOf(e.who), item: e.item });
      if (pendingGives.length === 1) giveWhenIdle();
      break;
    case 'takeItem': {
      const i = isPendingGive(e.who, e.item);
      if (i >= 0) pendingGives.splice(i, 1);
      else if (!isPendingTake(e.who, e.item)) {
        // Encara no surt: si la mateixa interacció dona un altre objecte, aquest ocuparà la seva casella.
        pendingTakes.push({ owner: ownerOf(e.who), item: e.item, paired: false });
        queueMicrotask(resolvePendingTakes);
      }
      break;
    }
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

// ─── Partides desades a una altra resolució ─────────────────────────────────
// Benne desa dins la partida la posició de cada personatge a cada sala, i en tornar-hi la fa servir.
// Les partides d'una resolució anterior (352×198 a Ferro-9; 480×270 a Ni un ou abans de passar a 640×360) les
// tenen en coordenades velles: els personatges quedarien fora de lloc. S'escalen una vegada. `store.resolucio`
// és l'amplada amb què es va desar (les de 352 no en tenien).
const RESOLUCIO = AMPLADA;
/** Les de 352×198: per sota d'aquesta alçada (a 480×270) no hi ha cap peu; les que ja hi són, ja estaven escalades. */
const TERRA_MINIM_352 = 155;

function migrateOldPositions() {
  const abans = typeof store.resolucio === 'number' ? store.resolucio : 352;
  if (abans === RESOLUCIO) return;
  const k = RESOLUCIO / abans;
  for (const room of Object.keys(content.rooms)) {
    for (const id of Object.keys(content.characters)) {
      const key = `room:${toBenne('rooms', room)}:character:${toBenne('characters', id)}:position`;
      const saved = defineVars({ [key]: null as VarValue });
      const pos = saved[key] as { x?: number; y?: number } | null;
      if (!pos || typeof pos.x !== 'number' || typeof pos.y !== 'number') continue;
      if (abans === 352 && pos.y >= TERRA_MINIM_352 * (RESOLUCIO / 480)) continue;
      saved[key] = { x: Math.round(pos.x * k), y: Math.round(pos.y * k) };
    }
  }
  store.resolucio = RESOLUCIO;
}

// Partida carregada (o nova: aleshores l'estat és buit i `ensureStarted` la prepara en entrar a la primera sala).
// (els gestors d'`events.on` d'aquest fitxer són `async` perquè Benne no avisi que no han passat pel connector de
// BenneScript: són instantanis, el cos s'executa sencer de seguida)
events.on('gameState:replaced', async () => {
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
 * Una cinemàtica amb coses per tocar (la carta de navegació d'Aigua Verne): no hi ha protagonista, però en acabar
 * l'`onEnter` es poden tocar les coses visibles, i el toc les fa sense que ningú hi camini. Compten les coses amb
 * interaccions: el pròleg i els finals també tenen `hotspots`, però només per mostrar o amagar els personatges.
 */
export const isClickableCutscene = (room: string | null | undefined) => {
  const def = room ? content.rooms[room] : undefined;
  return !!def?.cutscene && Object.values(def.hotspots ?? {}).some((h) => (h.interactions?.length ?? 0) > 0);
};

/** El text de l'`onEnter` d'una cinemàtica amb coses per tocar («On anem?»): el HUD el posa a la frase quan no hi ha res a sota. */
let prompt = '';
export const clickablePrompt = () => prompt;
export const setClickablePrompt = (text: string) => {
  prompt = text;
};

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

const music = (mapping as { music?: Record<string, string | MusicCase[]> }).music ?? {};
/**
 * La música d'ambient d'una sala (`music` al mapping.json del joc): la de la sala, o si no en té, la de
 * la seva protagonista. `null`: continua la que sonava (p. ex. a les cinemàtiques).
 */
export function roomMusic(room: string): string | null {
  const who = roomProtagonist(room);
  const def = (music as Record<string, string | MusicCase[] | undefined>)[room] ?? (who ? music[who] : undefined);
  if (!def || typeof def === 'string') return def ?? null;
  // Una llista de casos `{ "if": condició, "track": peça }`, com l'ambient: el primer que es compleix.
  return def.find((c) => !c.if || narrative.check(c.if))?.track ?? null;
}
type MusicCase = { if?: Condition; track: string };
/**
 * El so de fons de cada sala (`ambient` al mapping.json del joc, fitxers a game/audio/sfx/): un so en bucle
 * (mar, motor, vent) que sona sota la música. Cada sala té un nom de so o una llista de casos
 * `{ "if": condició, "sound": so, "volume": 0–1 }` (el primer que es compleix; sense `if`, sempre).
 * `sound: null` o una sala que no hi és: silenci.
 */
type AmbientCase = { if?: Condition; sound: string | null; volume?: number };
const ambients = (mapping as { ambient?: Record<string, string | AmbientCase[]> }).ambient ?? {};
export function roomAmbient(room: string): { sound: string; volume: number } | null {
  const def = ambients[room];
  if (!def || typeof def === 'string') return def ? { sound: def, volume: 1 } : null;
  const match = def.find((c) => !c.if || narrative.check(c.if));
  return match?.sound ? { sound: match.sound, volume: match.volume ?? 1 } : null;
}
/** Posa el so de fons que toca a la sala d'ara (o el treu): en entrar-hi i quan l'estat canvia. */
export function applyAmbientSound() {
  if (!('ambient' in mapping)) return;
  const room = world.currentRoom();
  const now = room ? roomAmbient(room) : null;
  if (now) ambient.play(now.sound, { volume: now.volume, fadeSeconds: 1.5 });
  else if (ambient.current) ambient.stop();
}

/**
 * La foscor de les sales (`fosc` al mapping.json del joc): una capa de color damunt de la sala i dels personatges,
 * per sota de la interfície i del text. Una llista de casos `{ "rooms": [sales], "if": condició, "alpha": 0–1,
 * "color": "#rrggbb" }`: el primer que inclou la sala d'ara i es compleix. Cap: sense foscor.
 * En entrar a una sala es posa de cop; si canvia l'estat dins la sala (es treu o es posa un relé), es fon.
 */
type ShadeCase = { rooms: string[]; if?: Condition; alpha: number; color?: string };
const shades = (mapping as { fosc?: ShadeCase[] }).fosc ?? [];
let shadeRoom: string | null = null;
export function roomShade(room: string): { alpha: number; color: number } | null {
  const match = shades.find((c) => c.rooms.includes(room) && (!c.if || narrative.check(c.if)));
  return match ? { alpha: match.alpha, color: parseInt((match.color ?? '#000000').slice(1), 16) } : null;
}
export function applyRoomShade() {
  if (!shades.length) return;
  const room = world.currentRoom();
  const now = room ? roomShade(room) : null;
  const seconds = room === shadeRoom ? 1.5 : 0;
  shadeRoom = room;
  if (now) shade.set(now.alpha, { color: now.color, seconds });
  else shade.set(0, { seconds });
}

/**
 * El so de cada sortida (`doors` al mapping.json del joc): `"sala.cosa": so`. Sona en arribar a la sala
 * nova, mentre s'hi entra (si sonés en sortir, el canvi de sala el tallaria).
 */
const doors = (mapping as { doors?: Record<string, string> }).doors ?? {};
let pendingDoor: string | null = null;
export function setDoorSound(room: string | null, hotspot: string) {
  pendingDoor = (room && doors[`${room}.${hotspot}`]) || null;
}
export function takeDoorSound() {
  const sound = pendingDoor;
  pendingDoor = null;
  return sound;
}

/** Si totes les pistes duren el mateix i, en canviar-ne, la nova continua al mateix punt (`musicSync`). */
export const musicSync = (mapping as { musicSync?: boolean }).musicSync === true;
/** Si el botó «Canvia» del HUD és sempre el de la pista (`botoPista` del joc: L'Última Arrel, on no es pot canviar). */
export const botoPista = (mapping as { botoPista?: boolean | string }).botoPista === true;
/** Si el botó és la pista només quan no es pot canviar (`botoPista: 'mixt'`: La Conjura de l'Avet). */
export const botoPistaMixt = (mapping as { botoPista?: boolean | string }).botoPista === 'mixt';
/** Si ara mateix el botó «Canvia» del HUD fa de pista. */
export const botoEsPista = () => botoPista || (botoPistaMixt && !narrative.canSwitch());

/** On és (o era) cada protagonista. */
export function protagonistRoom(who: string): string | null {
  const rooms = (store.protagonistRooms ?? {}) as Record<string, string>;
  return rooms[who] ?? content.manifest.start?.[who]?.room ?? null;
}

export function rememberProtagonistRoom(who: string, room: string) {
  store.protagonistRooms = { ...((store.protagonistRooms ?? {}) as Record<string, string>), [who]: room };
}
// Canvis al món que poden completar missions o mostrar coses.
events.on('gameState:inventoryChanged', async () => {
  adoptLoadedState();
  narrative.worldChanged();
});
events.on('gameState:roomContextChanged', async () => {
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
type RoomThing = { id: string; lookAtPoint?: Point; walkToPoint?: Point; points?: Point[]; collider?: { points: Point[] } };
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

type CharacterFile = { id: string; walkToPoint?: Point; feet?: Point; animations?: Record<string, unknown> };
const characterFiles = Object.values(import.meta.glob<CharacterFile>('../characters/*/*.character.json', { eager: true, import: 'default' }));

/**
 * De costat cap a `dx`: en 3/4 de cara (`DL`/`DR`) si el full del personatge en té (`IdleDL` i `TalkDL`), si no de
 * perfil (`L`/`R`). En una conversa de costat, els dos es miren però s'obren a la càmera, com al teatre: el perfil
 * estricte queda pla i amaga mitja cara.
 */
function sideFacing(benneId: string, dx: number): 'L' | 'R' | 'DL' | 'DR' {
  const anims = characterFiles.find((c) => c.id === benneId)?.animations;
  const tresQuarts = !!(anims?.IdleDL && anims?.TalkDL);
  if (dx < 0) return tresQuarts ? 'DL' : 'L';
  return tresQuarts ? 'DR' : 'R';
}

/** Cap on s'ha de girar la protagonista (des d'on és ara) per mirar la cosa, o `null`. Un personatge de costat, en 3/4 (`sideFacing`). */
export function facingToward(kind: 'prop' | 'hotspot' | 'character' | 'item', benneId: string): 'U' | 'D' | 'L' | 'R' | 'DL' | 'DR' | null {
  if (kind === 'item') return null;
  const to = lookPoint(kind, benneId);
  if (!to) return null;
  const from = player.position;
  const dx = to.x - from.x;
  const dy = to.y - from.y;
  if (Math.hypot(dx, dy) < 2) return null;
  if (Math.abs(dx) >= Math.abs(dy)) return kind === 'character' ? sideFacing(player.id, dx) : dx < 0 ? 'L' : 'R';
  return dy < 0 ? 'U' : 'D';
}

/**
 * Cap on s'ha de girar un personatge per mirar la protagonista quan li parla o li dona alguna cosa (en 3/4 si en
 * té, vegeu `sideFacing`), o `null` si no s'ha de girar: no té animacions de costat, o el seu `walkToPoint` no és
 * el de per defecte (just a la dreta dels peus) perquè està posat a propòsit (assegut a una taula, d'esquena, de
 * cara a algú).
 */
export function npcFacingPlayer(benneId: string): 'L' | 'R' | 'DL' | 'DR' | null {
  const def = characterFiles.find((c) => c.id === benneId);
  if (!def?.animations?.IdleL || !def.walkToPoint || !def.feet) return null;
  if (def.walkToPoint.x <= def.feet.x || def.walkToPoint.y !== def.feet.y) return null;
  const handle = benneCharacter(fromBenne('characters', benneId)) as { position?: Point } | undefined;
  const at = handle?.position;
  if (!at) return null;
  const dx = player.position.x - at.x;
  return Math.abs(dx) < 2 ? null : sideFacing(benneId, dx);
}

/** Les capes de l'art lligades a la cosa `id` d'una sala (props `<id>__<capa>`): es mostren i s'amaguen amb ella. */
function linkedLayers(room: string, id: string): PropHandle[] {
  const file = roomFiles.find((r) => r.id === toBenne('rooms', room));
  const prefix = `${toBenne('hotspots', id)}__`;
  return (file?.props ?? []).filter((p) => p.id.startsWith(prefix)).map((p) => new PropHandle(toBenne('rooms', room), p.id));
}

/** La capa `id` del decorat d'una sala (un prop de l'art, p. ex. el títol de la portada), si la sala la té. */
export function roomProp(room: string, id: string): PropHandle | undefined {
  const file = roomFiles.find((r) => r.id === toBenne('rooms', room));
  return file?.props.some((p) => p.id === id) ? new PropHandle(toBenne('rooms', room), id) : undefined;
}

// ─── Indicacions d'escena (`stage` a les línies) ─────────────────────────────

type Actor = {
  position: Point; visible: boolean; animation: string; stopAnimation(): void; moveTo(p: Point): void;
  face: { now(d: 'L' | 'R' | 'U' | 'D'): unknown }; facing: string;
};

/** Qui fa una indicació: un personatge, o la protagonista que juga (`player`). */
export function stageActor(who: string): Actor | undefined {
  return (who === 'player' ? player : benneCharacter(who)) as unknown as Actor | undefined;
}

/**
 * On apareix qui entra a `room` venint de `from`: el punt d'arribada de la porta (la cosa que hi torna). Benne desa la
 * posició de cada personatge a cada sala; si n'havia sortit sense passar per la porta (l'altra protagonista se l'ha
 * enduta amb `situar`), en tornar-hi apareixeria on l'havia deixada. `null` si no hi ha cap porta que hi torni.
 */
export function doorPoint(room: string, from: string): Point | null {
  const def = content.rooms[room];
  if (!def || def.cutscene) return null;
  const porta = Object.entries(def.hotspots ?? {}).find(([, h]) => (h.interactions ?? []).some((i) => i.goTo === from && !i.item));
  if (!porta) return null;
  const file = roomFiles.find((r) => r.id === toBenne('rooms', room));
  const id = toBenne('hotspots', porta[0]);
  return file?.hotspots.find((t) => t.id === id)?.walkToPoint ?? null;
}

/** On és un lloc d'una indicació: un punt, o el punt d'arribada d'una cosa de la sala (o on és un personatge). */
export function stagePoint(to: string | Point): Point | null {
  if (typeof to === 'object') return to;
  if (content.characters[to]) return stageActor(to)?.position ?? null;
  const room = roomFiles.find((r) => r.id === toBenne('rooms', world.currentRoom() ?? ''));
  const id = toBenne('hotspots', to);
  const thing = room?.hotspots.find((t) => t.id === id) ?? room?.props.find((t) => t.id === id);
  return thing?.walkToPoint ?? null;
}

/**
 * Embolica la crida que resol unes línies (`primeStage(narrative.choose(...))`): als `*.script.ts`, una crida soleta
 * és un pas que espera el seu torn (p. ex. que la Iri acabi de dir l'opció), i ha de passar en el mateix moment.
 *
 * Els efectes s'apliquen abans de les línies, i un decorat amb `visibleIf` sortiria de cop (l'aigua del toll, la porta
 * del roure). Les línies que el volen mostrar més tard l'amaguen al `stage` de la primera; aquí, aquestes capes
 * s'amaguen ja, abans fins i tot de l'opció que diu la protagonista. Només la primera línia (`skip`: la de l'opció, que
 * no en porta mai, se salta), i només amagar: el que es mostra o canvia més endavant espera la seva línia.
 */
export function primeStage<T extends { lines: readonly { stage?: StageCue[] }[] } | null | undefined>(resolved: T, skip = 0): T {
  for (const cue of resolved?.lines[skip]?.stage ?? []) {
    if (cue.prop !== undefined && cue.visible === false) applyStageNow({ prop: cue.prop, visible: false });
  }
  return resolved;
}

/** El que una indicació fa de cop (tot menys caminar i esperar). */
export function applyStageNow(cue: StageCue) {
  // Una sacsejada suau: ~2 píxels a 640 (la sala és tota la pantalla, i més es veurien les vores).
  if (cue.shake) camera.shake(0.004, cue.shake, true);
  if (cue.prop !== undefined) {
    // Una capa del decorat (un prop de l'art, que el joc no coneix): es mostra o s'amaga i canvia d'animació.
    const room = world.currentRoom();
    if (!room) return;
    const prop = new PropHandle(toBenne('rooms', room), cue.prop);
    if (cue.visible === true && cue.fade) {
      prop.alpha = 0;
      prop.visible = true;
      prop.fade.now(1, cue.fade);
    } else if (cue.visible !== undefined) prop.visible = cue.visible;
    if (typeof cue.anim === 'string' && prop.animation !== cue.anim) prop.animation = cue.anim;
    return;
  }
  if (cue.who === undefined) return;
  const actor = stageActor(cue.who);
  if (!actor) return;
  const at = cue.at !== undefined ? stagePoint(cue.at) : null;
  if (at) actor.moveTo(at);
  if (cue.visible !== undefined) actor.visible = cue.visible;
  if (cue.anim === null) actor.stopAnimation();
  else if (cue.anim !== undefined && actor.animation !== cue.anim) actor.animation = cue.anim;
  if (cue.face) actor.face.now(cue.face);
  if (cue.gest === null) actor.stopAnimation();
  else if (cue.gest !== undefined) {
    // El gest, amb la roba de la sala (`Lluny`, `LlunyGala`...) i cap on mira: R, UR i DR fan el mirall de L, UL i DL
    // (el sprite ja està girat: l'animació forçada no el torna a girar).
    const id = cue.who === 'player' ? world.activeProtagonist() : cue.who;
    const dir = ({ R: 'L', UR: 'UL', DR: 'DL' } as Record<string, string>)[actor.facing] ?? actor.facing;
    const tag = `${id ? narrative.outfitOf(id) : ''}${cue.gest}${dir}`;
    if (actor.animation !== tag) actor.animation = tag;
  }
}

/**
 * Les capes del decorat que les indicacions d'escena d'una sala fan anar (`{"prop": ..., "anim": ...}`) tornen a la seva
 * animació de base. El motor desa l'animació de cada capa, però la d'una cinemàtica no és estat de la partida: en
 * tornar al port d'Aqua, la cistella ha de tornar a penjar de la grua, no quedar-se a l'últim fotograma de la baixada.
 * (Les sales de cinemàtica no hi passen: no s'hi torna.)
 */
export function resetStageAnims(room: string) {
  const def = content.rooms[room];
  if (!def || def.cutscene) return;
  const props = new Set<string>();
  const walk = (o: unknown): void => {
    if (Array.isArray(o)) o.forEach(walk);
    else if (o && typeof o === 'object') {
      const r = o as Record<string, unknown>;
      for (const k of ['stage', 'stageAfter']) {
        for (const c of (r[k] as StageCue[] | undefined) ?? []) if (c.prop !== undefined && typeof c.anim === 'string') props.add(c.prop);
      }
      Object.values(r).forEach(walk);
    }
  };
  walk(def);
  if (!props.size) return;
  const file = roomFiles.find((r) => r.id === toBenne('rooms', room));
  for (const id of props) {
    const thing = file?.props.find((p) => p.id === id) as (RoomThing & { tag?: string }) | undefined;
    if (!thing) continue;
    const prop = new PropHandle(toBenne('rooms', room), id);
    const base = thing.tag ?? id;
    if (prop.animation !== base) prop.animation = base;
  }
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
 * Una interfície pròpia del joc (p. ex. la tàctil d'Aigua Verne, sense barra de verbs) pot quedar-se alguns
 * clics abans que vagin al JSON (`routeInteraction`, narrative.script.ts): verbs seus (tocar, el menú d'accions) o
 * decidir quin verb fa un objecte. `takes` ha de ser instantània; `route` pot ser una funció de pas, i per fer la
 * interacció del JSON crida `performInteraction`. Sense encaminador, cada clic va directe al JSON.
 */
export interface TouchRouter {
  takes(verb: string, target: FallbackTarget, item?: string): boolean;
  route(verb: string, target: FallbackTarget, item?: string): unknown;
  /**
   * Just després que el nucli resolgui una interacció (abans de dir-ne les línies): la tàctil apunta què s'ha vist.
   * `room` és la sala on era la cosa (abans de l'acció, que pot haver canviat de sala).
   */
  acted?(verb: string, target: FallbackTarget, room: string | null): void;
}
let router: TouchRouter | null = null;
export function setTouchRouter(r: TouchRouter | null) {
  router = r;
}
export const touchRouter = () => router;

/** Si el botó «Canvia» del HUD hi ha de ser (es pot canviar, o és el de la pista). */
export function switchButtonWanted(pot = narrative.canSwitch()): boolean {
  return pot || !!botoPista || !!botoPistaMixt;
}

/**
 * El botó «Canvia» (a la barra de verbs i, si el joc el té, al menú) només hi és quan el jugador pot
 * canviar de protagonista (`switchWhen` a game.json).
 */
export function applySwitchButton() {
  const pot = narrative.canSwitch();
  guis.verbs.controls.canviaBtn.visible = switchButtonWanted(pot);
  const menu = guis.gameMenu.controls as unknown as Record<string, { visible: boolean } | undefined>;
  if (menu.canviar) menu.canviar.visible = pot;
}

/**
 * `keepSpeakers`: els personatges amb `visibleIf` no canvien fins que `playLines` acabi. Qui s'ha d'amagar
 * encara pot parlar, i qui ha d'aparèixer no surt abans del que s'hi diu («truquen a la porta»); si és ell
 * qui parla, `showSpeaker` el mostra just abans.
 */
export function applyHotspotVisibility({ keepSpeakers = false } = {}) {
  const room = world.currentRoom();
  if (!room) return;
  for (const { id, visible } of narrative.hotspotsIn(room)) {
    // Un personatge amb `visibleIf` (p. ex. la Directora a la cel·la a l'Acte 3) s'amaga o es mostra sencer.
    const character = content.characters[id] ? (benneCharacter(id) as Showable | undefined) : undefined;
    if (keepSpeakers && character) continue;
    const zone = zones[room]?.includes(id) ? new HotspotHandle(toBenne('rooms', room), toBenne('hotspots', id)) : undefined;
    const handle = boundHotspots[id] ?? character ?? zone ?? new PropHandle(toBenne('rooms', room), toBenne('hotspots', id));
    if ('visible' in handle) handle.visible = visible;
    else handle.active = visible;
    // Les capes de l'art que l'acompanyen (`<id>__<capa>`): la versió d'una capa del davant amb aquell decorat (p. ex.
    // el timó de dia, `dia__davant_timo`). La capa del davant és un retall del fons i, si no, el taparia.
    for (const layer of linkedLayers(room, id)) layer.visible = visible;
  }
  applyCharacterVisibility(room, keepSpeakers);
  // El so de fons també depèn de l'estat (p. ex. el generador parat).
  applyAmbientSound();
  // I la llum.
  applyRoomShade();
}

/** Abans que parli un personatge que ha d'aparèixer però encara no es veu (vegeu `keepSpeakers`). */
export function showSpeaker(who: string) {
  const room = world.currentRoom();
  if (!room || !content.rooms[room]?.hotspots[who]?.visibleIf) return;
  if (!narrative.hotspotsIn(room).some((h) => h.id === who && h.visible)) return;
  const handle = (boundHotspots[who] ?? benneCharacter(who)) as Showable | undefined;
  if (!handle) return;
  if ('visible' in handle) handle.visible = true;
  else handle.active = true;
}

/**
 * Mentre la pantalla és a negre per un títol («Onze de la nit»): qui ha d'aparèixer ja hi és quan torna la
 * imatge, en lloc de sortir-hi de cop. Qui ha de marxar es queda fins al final (encara pot parlar).
 */
export function showDueCharacters() {
  const room = world.currentRoom();
  if (!room) return;
  for (const { id, visible } of narrative.hotspotsIn(room)) if (visible && content.characters[id]) showSpeaker(id);
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
