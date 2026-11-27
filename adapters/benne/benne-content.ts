/**
 * Genera el contingut que Benne necessita a partir del nostre JSON (el fa servir sync.ts):
 *
 *  - game-config.json: protagonista i sala inicials, verbs i frase per defecte en l'idioma triat;
 *  - textos de les GUI de la plantilla (menús, botons de verbs) en l'idioma triat;
 *  - sales, personatges i objectes que encara no existeixen a Benne, amb una disposició
 *    automàtica i art provisional (que dibuixa tools/draw_placeholders.py);
 *  - noms (descripcions) de totes les coses, cada vegada, en l'idioma triat.
 *
 * Regla d'or: el que ja existeix a Benne (sales dibuixades, polígons retocats a l'editor) no es
 * sobreescriu mai. Només s'hi actualitzen els textos.
 */
import { copyFileSync, existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import type { DialogueLineDef, GameContent, InteractionDef, LocaleTable, RoomDef } from '@aventura/narrative-core';
import { jocAdapterDir, type JocBenne } from './joc-benne.js';
import { configuraTactil, FES, opcionsTactils, TACTIL_TEXTOS } from './tactil/index.js';
import { objecteSol } from './tactil/runtime/accions.js';
import { filaVolumVeus } from './volum-veus.js';

/** Art provisional dels personatges del joc (games/<joc>/adapters/benne/placeholder-art/). */
const placeholderArt = (...parts: string[]) => join(jocAdapterDir(), 'placeholder-art', ...parts);
/**
 * Resolució del joc: la de game-config.json del projecte (480×270 si no en té; Ni un ou és a 640×360). La fixa
 * writeBenneContent. La disposició automàtica de les sales noves es va escriure en mides de 352×198 (Ferro-9) i
 * s'escala amb `s()`.
 */
export let W = 480;
export let H = 270;
let S = W / 352;
const s = (v: number) => Math.round(v * S);
/** Per sota d'aquesta línia hi ha la barra de verbs. */
let FLOOR_BOTTOM = s(148);

function setResolution(config: Json) {
  const r = config.resolution as { width?: number; height?: number } | undefined;
  W = r?.width ?? 480;
  H = r?.height ?? 270;
  S = W / 352;
  FLOOR_BOTTOM = s(148);
}

export type Json = Record<string, unknown>;
/** Peticions d'art provisional per a draw_placeholders.py (fora d'assets/, perquè Benne no les llegeixi). */
export const requestsDir = (gameDir: string) => join(gameDir, '../../.benne-provisional');
export const readJson = (p: string) => JSON.parse(readFileSync(p, 'utf8')) as Json;
export const writeJson = (p: string, v: unknown) => {
  mkdirSync(dirname(p), { recursive: true });
  writeFileSync(p, JSON.stringify(v, null, 2) + '\n');
};

export interface BenneContentReport {
  created: string[];
  updated: string[];
  needsArt: string[];
}

/** Camps del .character.json que venen del sprite (mides, peus, animacions). */
const SPRITE_FIELDS = ['walkSpeed', 'walkToPoint', 'talkPoint', 'feet', 'collider', 'animations', 'clickable', 'display', 'artScale', 'idleActions'];

/**
 * Sprite provisional d'un personatge: el seu propi a placeholder-art/<id> (draw_characters.py),
 * o un de la plantilla de Benne si no en té (les protagonistes necessiten caminar).
 */
function placeholderSprite(id: string, protagonist: boolean) {
  if (existsSync(placeholderArt(id, `${id}.png`))) return id;
  return protagonist ? 'hank' : 'penny';
}
/**
 * Qui camina en un `stage`/`stageAfter` (`walk`) i no té cap animació `Walk…` al sprite: Benne el faria lliscar
 * dret, sense moure les cames. Les protagonistes (i `player`) ja caminen sempre.
 */
function warnWalkersWithoutWalk(gameDir: string, content: GameContent, protagonists: string[]) {
  const walkers = new Set<string>();
  const visit = (o: unknown): void => {
    if (Array.isArray(o)) return o.forEach(visit);
    if (!o || typeof o !== 'object') return;
    for (const key of ['stage', 'stageAfter']) {
      const cues = (o as Json)[key];
      if (!Array.isArray(cues)) continue;
      for (const c of cues as Json[]) if (c?.walk !== undefined && typeof c.who === 'string') walkers.add(c.who);
    }
    Object.values(o).forEach(visit);
  };
  visit(content);
  for (const id of walkers) {
    if (id === 'player' || protagonists.includes(id)) continue;
    const path = join(gameDir, 'characters', id, `${id}.character.json`);
    if (!existsSync(path)) continue;
    const anims = Object.keys((readJson(path).animations as Json | undefined) ?? {});
    if (!anims.some((a) => a.includes('Walk'))) {
      console.warn(`⚠ characters/${id}: camina en un stage però el sprite no té animacions Walk (lliscarà sense moure les cames).`);
    }
  }
}

const NPC_COLORS = ['#c8c8c8', '#c89060', '#b8a8e0', '#ff90c8', '#90d890', '#e8e070'];

/** Textos de les GUI de la plantilla 9-verb: GUI → control → clau de text (cada joc n'hi pot afegir). */
const GUI_TEXTS: Record<string, Record<string, string>> = {
  verbs: {
    GiveBtn: 'ui.verb.give', OpenBtn: 'ui.verb.open', CloseBtn: 'ui.verb.close', PickUpBtn: 'ui.verb.pickUp',
    TalkToBtn: 'ui.verb.talkTo.boto', LookAtBtn: 'ui.verb.look', UseBtn: 'ui.verb.use', PushBtn: 'ui.verb.push',
    PullBtn: 'ui.verb.pull', verbLineText: 'ui.verb.walkTo',
  },
  portada: { continua: 'ui.portada.continua', comenca: 'ui.portada.comenca', carrega: 'ui.portada.carrega' },
  'game-menu': {
    title: 'ui.menu.titol', save: 'ui.menu.desar', load: 'ui.menu.carregar', settings: 'ui.menu.opcions',
    quit: 'ui.menu.sortir', resume: 'ui.menu.continuar', 'title-screen': 'ui.menu.inici',
  },
  'load-menu': { title: 'ui.menu.carregar', instructions: 'ui.carregar.instruccions', 'load-btn': 'ui.menu.carregar', 'back-btn': 'ui.menu.tornar' },
  'save-menu': { title: 'ui.menu.desar', instructions: 'ui.desar.instruccions', 'save-btn': 'ui.menu.desar', 'back-btn': 'ui.menu.tornar' },
  'settings-menu': {
    title: 'ui.menu.opcions', 'click-to-skip': 'ui.opcions.clic_salta', 'sound-effects-volume': 'ui.opcions.volum_efectes',
    'music-volume': 'ui.opcions.volum_musica', 'voice-volume': 'ui.opcions.volum_veus', back: 'ui.menu.tornar', 'dialog-text-speed': 'ui.opcions.velocitat_text',
  },
};

export function writeBenneContent(gameDir: string, content: GameContent, text: LocaleTable, fallback: LocaleTable, joc: JocBenne): BenneContentReport {
  const report: BenneContentReport = { created: [], updated: [], needsArt: [] };
  const t = (key: string | undefined, def = '') => (key ? (text[key] ?? fallback[key] ?? def) : def);
  const protagonists = content.manifest.protagonists;
  const first = protagonists[0]!;

  // ── game-config.json ────────────────────────────────────────────────────
  const configPath = join(gameDir, 'game-config.json');
  const config = readJson(configPath);
  setResolution(config);
  config.name = content.manifest.id;
  config.startingPlayerCharacter = first;
  config.startingRoomId = content.manifest.cover ?? content.manifest.intro ?? content.manifest.start?.[first]?.room ?? config.startingRoomId;
  // Els inventaris inicials els reparteix el nucli (game.json → start).
  config.initialGameState = { flags: {}, variables: {}, inventory: [] };
  config.defaultFallbackLine = t('ui.defecte', String(config.defaultFallbackLine ?? ''));
  if (joc.tactil) configuraTactil(config, t);
  joc.configura?.(config, t);
  for (const verb of (config.verbs as Json[]) ?? []) {
    verb.label = t(`ui.verb.${verb.id}`, String(verb.label));
    if (verb.preposition !== undefined) verb.preposition = t(`ui.verb.${verb.id}.prep`, String(verb.preposition));
  }
  writeJson(configPath, config);
  report.updated.push('game-config.json');

  // ── GUI ─────────────────────────────────────────────────────────────────
  joc.guis?.(gameDir);
  if (joc.tactil) opcionsTactils(gameDir);
  filaVolumVeus(gameDir);  // després d'opcionsTactils, que esborra el que hi ha sota la seva marca
  if (addSwitchButton(gameDir)) report.needsArt.push('guis/verbs');
  if (content.manifest.cover && addCoverGui(gameDir, joc)) report.needsArt.push('guis/portada');
  const guiTexts = structuredClone(GUI_TEXTS);
  // La interfície tàctil no té barra de verbs: la frase la posa el HUD (tactil/guis/verbs/hud.ts), que comença buida.
  if (joc.tactil) delete guiTexts.verbs;
  if (joc.tactil) for (const [gui, extra] of Object.entries(TACTIL_TEXTOS)) guiTexts[gui] = { ...guiTexts[gui], ...extra };
  for (const [gui, extra] of Object.entries(joc.textosGui ?? {})) guiTexts[gui] = { ...guiTexts[gui], ...extra };
  for (const [gui, controls] of Object.entries(guiTexts)) {
    const path = join(gameDir, 'guis', gui, `${gui}.gui.json`);
    if (!existsSync(path)) continue;
    const def = readJson(path);
    const walk = (list: Json[] = []) => {
      for (const c of list) {
        const key = controls[String(c.id)];
        if (key && typeof c.text === 'string') c.text = t(key, c.text);
        walk(c.children as Json[]);
      }
    };
    walk(def.controls as Json[]);
    writeJson(path, def);
  }

  // ── Personatges ─────────────────────────────────────────────────────────
  const npcs = Object.keys(content.characters).filter((id) => !protagonists.includes(id));
  for (const [id, def] of Object.entries(content.characters)) {
    const dir = join(gameDir, 'characters', id);
    const path = join(dir, `${id}.character.json`);
    const art = join(gameDir, 'assets/images/characters', id);
    const isNew = !existsSync(path);
    // Art provisional: es posa la primera vegada i s'actualitza mentre hi hagi la marca `.provisional`.
    if (isNew || existsSync(join(art, '.provisional'))) {
      const sprite = placeholderSprite(id, protagonists.includes(id));
      const template = readJson(placeholderArt(sprite, `${sprite}.character.json`));
      const current = isNew ? {} : readJson(path);
      const fromSprite = Object.fromEntries(SPRITE_FIELDS.filter((k) => k in template).map((k) => [k, template[k]]));
      if (!('artScale' in template)) delete current.artScale;   // un full a 1× (p. ex. si es torna enrere)
      writeJson(path, {
        ...template, ...current, ...fromSprite, id,
        speechColor: (current.speechColor as string) ?? joc.colorsVeu?.[id] ?? NPC_COLORS[npcs.indexOf(id) % NPC_COLORS.length],
        defaultVerb: (current.defaultVerb as string) ?? template.defaultVerb ?? (protagonists.includes(id) ? 'look' : 'talkTo'),
      });
      mkdirSync(art, { recursive: true });
      copyFileSync(placeholderArt(sprite, `${sprite}.png`), join(art, `${id}.png`));
      const sheet = readJson(placeholderArt(sprite, `${sprite}.json`));
      (sheet.meta as Json).image = `${id}.png`;
      writeJson(join(art, `${id}.json`), sheet);
      writeFileSync(join(art, '.provisional'), "Art provisional: esborra aquest fitxer quan el sprite sigui definitiu.\n");
      if (isNew) report.created.push(`characters/${id}`);
    }
    const character = readJson(path);
    character.name = t(def.name, id);
    character.description = t(def.description ?? def.name, id);
    writeJson(path, character);
  }
  warnWalkersWithoutWalk(gameDir, content, protagonists);

  // ── Objectes d'inventari ────────────────────────────────────────────────
  for (const [id, def] of Object.entries(content.items)) {
    const path = join(gameDir, 'inventory', id, `${id}.inventory.json`);
    const item = existsSync(path)
      ? readJson(path)
      : { id, onVerb: {}, stackable: false, animations: {}, display: { aseprite: 'shared' } };
    if (!existsSync(path)) report.created.push(`inventory/${id}`);
    item.name = t(def.name, id);
    item.description = t(def.name, id);
    // Interfície tàctil: els objectes que es fan servir sols (el plànol) no es prenen a la mà en tocar-los.
    if (joc.tactil) {
      if (objecteSol(content, id)) item.defaultVerb = FES;
      else if (item.defaultVerb === FES) delete item.defaultVerb;
    }
    writeJson(path, item);
  }
  // Full d'objectes provisional: es redibuixa mentre no hi hagi art de debò.
  const invArt = join(gameDir, 'assets/images/inventory');
  if (!existsSync(join(invArt, 'inventory.png')) || existsSync(join(invArt, '.provisional'))) {
    writeJson(join(requestsDir(gameDir), 'inventory.json'), {
      items: Object.entries(content.items).map(([id, def]) => ({ id, label: t(def.name, id) })),
    });
    report.needsArt.push('inventory');
  }

  // ── Sales ───────────────────────────────────────────────────────────────
  const manifestPath = join(gameDir, 'rooms/rooms.manifest.json');
  const manifest = existsSync(manifestPath) ? readJson(manifestPath) : { rooms: [] };
  const listed = new Set(((manifest.rooms as Json[]) ?? []).map((r) => r.id));
  for (const [id, room] of Object.entries(content.rooms)) {
    const path = join(gameDir, 'rooms', id, `${id}.room.json`);
    if (!existsSync(path)) {
      const { room: benneRoom, request } = layoutRoom(id, room, content, t, joc);
      writeJson(path, benneRoom);
      writeJson(join(requestsDir(gameDir), 'rooms', `${id}.json`), request);
      report.created.push(`rooms/${id}`);
      report.needsArt.push(`rooms/${id}`);
    } else {
      // Sala existent: només els textos.
      const benneRoom = readJson(path);
      benneRoom.name = t(room.name, id);
      for (const thing of [...((benneRoom.hotspots as Json[]) ?? []), ...((benneRoom.props as Json[]) ?? [])]) {
        const def = room.hotspots[String(thing.id)];
        if (def?.name) thing.description = t(def.name);
      }
      // Decorats nous: s'afegeixen com a props no clicables (cal art nou).
      const props = ((benneRoom.props as Json[]) ??= []);
      for (const [did, def] of Object.entries(room.decor ?? {})) {
        const existing = props.find((p) => p.id === did);
        if (existing) {
          // Només si el contingut ho diu (`sota`): si no, es respecta el que s'hagi retocat a l'editor. Tampoc si
          // l'art l'ha posat damunt d'una capa del davant (porta la línia base de la capa): baixat, la capa el taparia.
          if (def.sota !== undefined && existing.baseline === undefined) existing.zIndex = decorZ(def.sota);
          continue;
        }
        props.push(decorProp(did, def.sota));
        report.created.push(`rooms/${id}: decorat ${did}`);
        // Amb art definitiu, el fotograma l'ha d'afegir qui dibuixa (etiqueta = id del decorat).
        if (!existsSync(join(gameDir, 'assets/images/rooms', id, '.provisional'))) {
          console.warn(`⚠ rooms/${id}: falta el fotograma «${did}» a l'art de la sala.`);
        }
      }
      // Coses noves del contingut (una porta, un objecte...): s'afegeixen amb la disposició
      // automàtica. Si la sala té disseny propi (room_designs.py), l'art provisional les recol·loca.
      const hotspots = ((benneRoom.hotspots as Json[]) ??= []);
      const has = (thingId: unknown) => hotspots.some((h) => h.id === thingId) || props.some((p) => p.id === thingId);
      const fresh = layoutRoom(id, room, content, t, joc).room;
      for (const h of fresh.hotspots as Json[]) {
        if (has(h.id)) continue;
        hotspots.push(h);
        report.created.push(`rooms/${id}: ${String(h.id)}`);
      }
      for (const p of fresh.props as Json[]) {
        if (has(p.id)) continue;
        props.push(p);
        report.created.push(`rooms/${id}: ${String(p.id)}`);
      }
      // Personatges nous a la sala (p. ex. algú que hi arriba en un acte posterior).
      const spawns = ((benneRoom.characters as Json[]) ??= []);
      for (const c of fresh.characters as Json[]) {
        if (spawns.some((x) => x.definition === c.definition)) continue;
        spawns.push(c);
        report.created.push(`rooms/${id}: ${String(c.definition).split('/')[0]}`);
      }
      writeJson(path, benneRoom);
      for (const w of coveredProps(benneRoom)) console.warn(`⚠ rooms/${id}: ${w}`);
      // Art encara provisional: es redibuixa (els dissenys poden haver canviat).
      if (existsSync(join(gameDir, 'assets/images/rooms', id, '.provisional'))) report.needsArt.push(`rooms/${id}`);
    }
    if (!listed.has(id)) {
      (manifest.rooms as Json[]).push({ id, definition: `${id}/${id}.room.json` });
    }
  }
  manifest.startRoomId = config.startingRoomId;
  writeJson(manifestPath, manifest);

  return report;
}

// ─── Botó «Canvia» a la barra de verbs ──────────────────────────────────────

/**
 * Un botó «Canvia» a l'esquerra dels verbs, damunt del botó del menú: canviar de protagonista no pot
 * quedar amagat dins el menú. Retorna si cal dibuixar-ne la casella a la imatge de la barra.
 */
function addSwitchButton(gameDir: string): boolean {
  const dir = join(gameDir, 'guis/verbs');
  const jsonPath = join(dir, 'verbs.gui.json');
  const tsPath = join(dir, 'verbs.gui.ts');
  if (!existsSync(jsonPath) || !existsSync(tsPath)) return false;
  const def = readJson(jsonPath);
  const controls = (def.controls as Json[]) ?? [];
  const model = controls.find((c) => c.id === 'GiveBtn');
  if (model && !controls.some((c) => c.id === 'CanviaBtn')) {
    const menu = controls.findIndex((c) => c.id === 'MenuBtn');
    controls.splice(menu, 0, {
      ...structuredClone(model), id: 'CanviaBtn', x: 3, y: 211, width: 43, height: 32,
      backgroundTag: 'CanviaBtn', backgroundAnchor: 'screen', text: '',
    });
    writeJson(jsonPath, def);
  }
  const script = readFileSync(tsPath, 'utf8');
  if (!script.includes('switchProtagonist')) {
    const withImports = script.replace(
      /import \{([^}]*)\} from '\.\/verbs\.ids';/,
      (_m, names: string) => `import {${names.trimEnd()} canviaBtn,\n} from './verbs.ids';\nimport { switchProtagonist } from '../../narrative/narrative.script';`,
    );
    writeFileSync(tsPath, `${withImports.trimEnd()}

// Afegit per adapters/benne (benne-content.ts): canviar de protagonista.
canviaBtn.onClick(() => switchProtagonist())
`);
  }
  const sheet = join(gameDir, 'assets/images/guis/verbs/verbs.json');
  if (!existsSync(sheet)) return false;
  const tags = ((readJson(sheet).meta as Json).frameTags as Json[]) ?? [];
  return !tags.some((t) => t.name === 'CanviaBtn') || existsSync(join(gameDir, 'assets/images/guis/verbs/.canvia-provisional'));
}

// ─── Portada: «Continua», «Comença» i «Carrega» ─────────────────────────────

/** Els botons de la portada (coordenades de pantalla a 480×270; s'escalen a la resolució del joc). Els dibuixa draw_placeholders.py. */
const COVER_BUTTONS = [
  // Només es veu si hi ha una partida desada sola (vegeu portada.gui.ts).
  { id: 'continua', x: 165, y: 168, width: 150, height: 22 },
  { id: 'comenca', x: 165, y: 196, width: 150, height: 22 },
  { id: 'carrega', x: 165, y: 224, width: 150, height: 22 },
];

/**
 * Una GUI `portada` amb els botons de la portada, si encara no hi és. Es mostra només a la sala
 * `cover` (ho fa el runtime). Retorna si cal dibuixar-ne l'art.
 */
/** Una caixa de la disposició de 480×270 a la resolució del joc. */
function scaled480<T extends { x: number; y: number; width: number; height: number }>(b: T): T {
  const k = W / 480;
  return { ...b, x: Math.round(b.x * k), y: Math.round(b.y * k), width: Math.round(b.width * k), height: Math.round(b.height * k) };
}

const PORTADA_MARCA = '// Creat per adapters/benne (benne-content.ts): els botons de la portada.';

function addCoverGui(gameDir: string, joc: JocBenne): boolean {
  const dir = join(gameDir, 'guis/portada');
  const jsonPath = join(dir, 'portada.gui.json');
  const tsPath = join(dir, 'portada.gui.ts');
  if (!existsSync(jsonPath)) {
    mkdirSync(dir, { recursive: true });
    writeJson(jsonPath, {
      id: 'portada', name: 'Portada', description: 'Botons de la portada (adapters/benne).', visible: false,
      display: { aseprite: true },
      controls: COVER_BUTTONS.map((b) => scaled480(b)).map((b) => ({
        type: 'button', ...b, backgroundAnchor: 'screen', text: b.id,
        font: joc.fonts.negreta, fontSize: 8, textColor: '#10908e', textAlign: 'center', textOffsetX: 0, textOffsetY: 0,
        textColorStates: { hover: '#28c074' }, textOutline: { enabled: true, color: '#132243', sides: 'bottomRight' },
        backgroundTag: `${b.id}`, states: { hover: `${b.id}-hover` },
      } as Record<string, unknown>)).concat([{
        // La versió del joc, a la cantonada de baix a la dreta (el text el posa portada.gui.ts).
        type: 'text', id: 'version', x: W - 6, y: H - 11, text: '', font: joc.fonts.regular, fontSize: 8,
        color: '#10908e', align: 'right', textOutline: { enabled: true, color: '#132243', sides: 'bottomRight' },
      }]),
    });
  }
  // (si és el generat, porta la marca i es torna a fer: així s'hi treu el que hi posava abans la interfície tàctil)
  if (!existsSync(tsPath) || readFileSync(tsPath, 'utf8').startsWith(PORTADA_MARCA)) {
    writeFileSync(tsPath, `${PORTADA_MARCA}
import { game, saves } from '@benne/script';
import { guis } from '@game';
import { gui, continua, comenca, carrega, version } from './portada.ids';
import { AUTOSAVE } from '../../narrative/narrative';
import { startFromCover } from '../../narrative/narrative.script';

// «Continua» carrega la partida que es desa sola a cada sala; només surt si n'hi ha una.
function syncContinua() {
  continua.visible = saves.get(AUTOSAVE) != null
}

continua.onClick(() => saves.load(AUTOSAVE))
comenca.onClick(() => startFromCover())
carrega.onClick(() => guis.loadMenu.show())

gui.onBuilt(() => {
  version.text = \`v\${game.version}\`
  syncContinua()
})
gui.onShow(() => syncContinua())
`);
  }
  const art = join(gameDir, 'assets/images/guis/portada');
  return !existsSync(join(art, 'portada.png')) || existsSync(join(art, '.provisional'));
}

// ─── Disposició automàtica d'una sala nova ──────────────────────────────────

/** Un decorat (`decor` a la sala): un prop que es veu o no segons l'estat, però no es pot clicar. */
/**
 * Props clicables que no es poden clicar: el motor dona el clic a la cosa de zIndex més alt, i un punt (hotspot) més
 * amunt que tapi del tot el collider d'un prop se'l queda sempre (la cera del forat, a La Conjura de l'Avet).
 */
export function coveredProps(room: Json): string[] {
  type Box = [number, number, number, number];
  const box = (pts: Json[] | undefined): Box | null => {
    if (!pts?.length) return null;
    const xs = pts.map((p) => Number(p.x)), ys = pts.map((p) => Number(p.y));
    return [Math.min(...xs), Math.min(...ys), Math.max(...xs), Math.max(...ys)];
  };
  const hotspots = ((room.hotspots as Json[]) ?? []).filter((h) => h.active !== false)
    .map((h) => ({ id: String(h.id), z: Number(h.zIndex ?? 0), b: box(h.points as Json[]) }));
  const props = ((room.props as Json[]) ?? []).filter((p) => p.clickable)
    .map((p) => ({ id: String(p.id), z: Number(p.zIndex ?? 0), b: box((p.collider as Json | undefined)?.points as Json[]) }));
  const out: string[] = [];
  for (const p of props) {
    if (!p.b) continue;
    for (const h of hotspots) {
      if (!h.b || h.z < p.z) continue; // amb el mateix zIndex també guanya el punt
      if (h.b[0] <= p.b[0] && h.b[1] <= p.b[1] && h.b[2] >= p.b[2] && h.b[3] >= p.b[3]) {
        out.push(`el prop «${p.id}» (zIndex ${p.z}) queda tapat pel punt «${h.id}» (zIndex ${h.z}): no es pot clicar. Puja el zIndex del prop o baixa el del punt.`);
      }
    }
  }
  return out;
}

// Per sobre dels props clicables (zIndex 3): un decorat pot canviar l'aspecte d'un prop. No es pot clicar.
// Amb `sota`, per sota (zIndex 2): fa de fons d'altres coses clicables.
const decorZ = (sota?: boolean) => (sota ? 2 : 4);
const decorProp = (id: string, sota?: boolean) => ({ id, tag: id, animations: { [id]: {} }, zIndex: decorZ(sota), visible: false, alpha: 1, clickable: false });

interface Box { id: string; label: string; x: number; y: number; w: number; h: number; kind: 'hotspot' | 'prop' | 'exit' }

const rect = (b: { x: number; y: number; w: number; h: number }) => [
  { x: b.x, y: b.y }, { x: b.x + b.w, y: b.y }, { x: b.x + b.w, y: b.y + b.h }, { x: b.x, y: b.y + b.h },
];

/**
 * Personatges que parlen en una sala sense ser-hi com a cosa (p. ex. la MARE per l'altaveu), o que hi
 * apareixen només en una indicació d'escena (`stage`: en Sic, que entra a buscar l'Iri i se l'emporta).
 */
function voicesIn(room: RoomDef, content: GameContent, joc: JocBenne): string[] {
  const who = new Set<string>();
  const line = (l: DialogueLineDef) => {
    who.add(l.who);
    for (const c of [...(l.stage ?? []), ...(l.stageAfter ?? [])]) if (c.who) who.add(c.who);
  };
  const scan = (list: InteractionDef[] = []) => {
    for (const i of list) {
      for (const l of i.lines ?? []) line(l);
      if (i.dialogue) {
        const d = content.dialogues[i.dialogue];
        if (d) {
          who.add(d.with);
          for (const n of Object.values(d.nodes)) for (const l of n.lines ?? []) line(l);
        }
      }
    }
  };
  scan(room.onEnter);
  for (const h of Object.values(room.hotspots)) scan(h.interactions);
  // Si el joc ho vol, una protagonista també pot ser una veu a la sala de l'altra (la Vet des de la cuina).
  const protagonists = content.manifest.protagonists;
  return [...who].filter((w) =>
    content.characters[w] && !(w in room.hotspots) && !room.protagonists?.includes(w)
    && (joc.veusProtagonistes ? w !== room.protagonist : !protagonists.includes(w)));
}

function layoutRoom(id: string, room: RoomDef, content: GameContent, t: (k?: string, d?: string) => string, joc: JocBenne) {
  const characters = Object.keys(room.hotspots).filter((h) => content.characters[h]);
  const things = Object.entries(room.hotspots).filter(([h]) => !content.characters[h]);
  const exits = things.filter(([, h]) => (h.interactions ?? []).some((i) => i.goTo));
  const others = things.filter((e) => !exits.includes(e));

  const boxes: Box[] = [];
  exits.forEach(([hid, h], n) => {
    const side = n % 2 === 0 ? 'left' : 'right';
    const level = Math.floor(n / 2);
    boxes.push({ id: hid, label: t(h.name, hid), kind: 'exit', w: s(34), h: s(66 - level * 8), x: side === 'left' ? s(6 + level * 40) : W - s(40 + level * 40), y: s(52 + level * 8) });
  });
  const span = { from: s(50), to: W - s(50) };
  const slot = (span.to - span.from) / Math.max(1, others.length);
  others.forEach(([hid, h], n) => {
    const w = Math.min(s(54), Math.floor(slot) - s(6));
    const cx = span.from + slot * n + slot / 2;
    const tall = n % 2 === 1; // alternem alçades perquè les etiquetes no es toquin
    // A la part alta de la paret: els personatges (87 px) queden a sota, sense tapar-les.
    boxes.push({ id: hid, label: t(h.name, hid), kind: h.visibleIf ? 'prop' : 'hotspot', w, h: s(24), x: Math.round(cx - w / 2), y: s(tall ? 14 : 42) });
  });

  const walkTo = (b: Box) => ({ x: Math.round(b.x + b.w / 2), y: s(b.kind === 'exit' ? 132 : 126) });
  const hotspots = boxes.filter((b) => b.kind !== 'prop').map((b, n) => ({
    id: b.id, active: true, description: b.label, zIndex: n, points: rect(b), walkToPoint: walkTo(b),
    lookAtPoint: { x: Math.round(b.x + b.w / 2), y: b.y + b.h }, ...(b.kind === 'exit' ? { defaultVerb: 'open' } : {}),
  }));
  const props = [
    { id: 'BG', tag: 'BG', animations: { BG: {} }, zIndex: 0, visible: true, alpha: 1 },
    ...boxes.filter((b) => b.kind === 'prop').map((b) => ({
      id: b.id, tag: b.id, animations: { [b.id]: {} }, zIndex: 3, visible: true, alpha: 1, clickable: true,
      collider: { points: rect(b) }, walkToPoint: walkTo(b), lookAtPoint: { x: Math.round(b.x + b.w / 2), y: b.y + b.h }, description: b.label,
    })),
    ...Object.entries(room.decor ?? {}).map(([did, def]) => decorProp(did, def.sota)),
  ];

  const spawn: Json[] = [];
  const protagonist = room.protagonist;
  // Una sala compartida té totes les seves protagonistes (el pont mostra només les que hi són).
  (room.protagonists ?? (protagonist ? [protagonist] : [])).forEach((p, n) => {
    spawn.push({ instanceId: `${p}-1`, definition: `${p}/${p}.character.json`, x: W / 2 + n * s(40), y: s(136), initialFacing: 'D', initialAnimation: 'Idle', visible: true, zIndex: 10 });
  });
  characters.forEach((c, n) => {
    const x = characters.length === 1 ? s(270) : s(70) + n * ((W - s(140)) / Math.max(1, characters.length - 1));
    spawn.push({ instanceId: `${c}-1`, definition: `${c}/${c}.character.json`, x: Math.round(x), y: s(130), initialFacing: 'D', initialAnimation: 'Idle', visible: true, zIndex: 9 });
  });
  voicesIn(room, content, joc).forEach((c, n) => {
    // Una veu: hi és perquè pugui parlar, però no es veu ni es pot clicar. Té el zIndex dels
    // personatges perquè, si un `stage` la fa entrar, les baselines (el que tapa) li funcionin igual.
    spawn.push({ instanceId: `${c}-veu`, definition: `${c}/${c}.character.json`, x: s(40 + n * 30), y: s(70), initialFacing: 'D', initialAnimation: 'Idle', visible: false, clickable: false, zIndex: 9 });
  });

  const benneRoom = {
    id,
    name: t(room.name, id),
    size: { width: W, height: H },
    scrollBounds: { x: 0, y: 0, width: W, height: H },
    walkable: {
      polygons: [{ id: 'walk-1', active: true, points: [{ x: s(14), y: s(118) }, { x: W - s(14), y: s(118) }, { x: W - s(6), y: FLOOR_BOTTOM }, { x: s(6), y: FLOOR_BOTTOM }], holes: [] }],
    },
    hotspots,
    points: [],
    regions: [],
    props,
    characters: spawn,
  };
  const request = {
    width: W,
    height: H,
    title: t(room.name, id),
    era: protagonist ?? room.protagonists?.[0] ?? '',
    floorTop: s(112),
    floorBottom: FLOOR_BOTTOM,
    boxes,
    characters: characters.map((c) => t(content.characters[c]?.name, c)),
  };
  return { room: benneRoom, request };
}
