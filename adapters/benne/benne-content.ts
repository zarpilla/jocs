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
import { fileURLToPath } from 'node:url';
import type { GameContent, InteractionDef, LocaleTable, RoomDef } from '@aventura/narrative-core';

const HERE = dirname(fileURLToPath(import.meta.url));
/** Resolució del joc. Les mides de disseny (com a tools/escala.py) són de 352×198 i s'escalen amb `s()`. */
const W = 480;
const H = 270;
const S = W / 352;
const s = (v: number) => Math.round(v * S);
/** Per sota d'aquesta línia hi ha la barra de verbs. */
const FLOOR_BOTTOM = s(148);

type Json = Record<string, unknown>;
/** Peticions d'art provisional per a draw_placeholders.py (fora d'assets/, perquè Benne no les llegeixi). */
export const requestsDir = (gameDir: string) => join(gameDir, '../../.benne-provisional');
const readJson = (p: string) => JSON.parse(readFileSync(p, 'utf8')) as Json;
const writeJson = (p: string, v: unknown) => {
  mkdirSync(dirname(p), { recursive: true });
  writeFileSync(p, JSON.stringify(v, null, 2) + '\n');
};

export interface BenneContentReport {
  created: string[];
  updated: string[];
  needsArt: string[];
}

/** Colors de parla per personatge. */
const SPEECH: Record<string, string> = {
  iri: '#f0a050', vet: '#60d8d8', cargol: '#a8f0c0', capatas: '#d8a878', mos: '#c8b8f0', mare: '#ff90c8',
};
/** Camps del .character.json que venen del sprite (mides, peus, animacions). */
const SPRITE_FIELDS = ['walkSpeed', 'walkToPoint', 'talkPoint', 'feet', 'collider', 'animations', 'clickable', 'display'];

/**
 * Sprite provisional d'un personatge: el seu propi a placeholder-art/<id> (draw_characters.py),
 * o un de la plantilla de Benne si no en té (les protagonistes necessiten caminar).
 */
function placeholderSprite(id: string, protagonist: boolean) {
  if (existsSync(join(HERE, 'placeholder-art', id, `${id}.png`))) return id;
  return protagonist ? 'hank' : 'penny';
}
const NPC_COLORS = ['#c8c8c8', '#c89060', '#b8a8e0', '#ff90c8', '#90d890', '#e8e070'];

/** Textos de les GUI de la plantilla 9-verb: GUI → control → clau de text. */
const GUI_TEXTS: Record<string, Record<string, string>> = {
  verbs: {
    GiveBtn: 'ui.verb.give', OpenBtn: 'ui.verb.open', CloseBtn: 'ui.verb.close', PickUpBtn: 'ui.verb.pickUp',
    TalkToBtn: 'ui.verb.talkTo.boto', LookAtBtn: 'ui.verb.look', UseBtn: 'ui.verb.use', PushBtn: 'ui.verb.push',
    PullBtn: 'ui.verb.pull', verbLineText: 'ui.verb.walkTo',
  },
  'game-menu': {
    title: 'ui.menu.titol', save: 'ui.menu.desar', load: 'ui.menu.carregar', settings: 'ui.menu.opcions',
    quit: 'ui.menu.sortir', resume: 'ui.menu.continuar', 'title-screen': 'ui.menu.inici',
    canviar: 'ui.menu.canviar', pista: 'ui.menu.pista',
  },
  'load-menu': { title: 'ui.menu.carregar', instructions: 'ui.carregar.instruccions', 'load-btn': 'ui.menu.carregar', 'back-btn': 'ui.menu.tornar' },
  'save-menu': { title: 'ui.menu.desar', instructions: 'ui.desar.instruccions', 'save-btn': 'ui.menu.desar', 'back-btn': 'ui.menu.tornar' },
  'settings-menu': {
    title: 'ui.menu.opcions', 'click-to-skip': 'ui.opcions.clic_salta', 'sound-effects-volume': 'ui.opcions.volum_efectes',
    'music-volume': 'ui.opcions.volum_musica', back: 'ui.menu.tornar', 'dialog-text-speed': 'ui.opcions.velocitat_text',
  },
};

export function writeBenneContent(gameDir: string, content: GameContent, text: LocaleTable, fallback: LocaleTable): BenneContentReport {
  const report: BenneContentReport = { created: [], updated: [], needsArt: [] };
  const t = (key: string | undefined, def = '') => (key ? (text[key] ?? fallback[key] ?? def) : def);
  const protagonists = content.manifest.protagonists;
  const first = protagonists[0]!;

  // ── game-config.json ────────────────────────────────────────────────────
  const configPath = join(gameDir, 'game-config.json');
  const config = readJson(configPath);
  config.name = content.manifest.id;
  config.startingPlayerCharacter = first;
  config.startingRoomId = content.manifest.intro ?? content.manifest.start?.[first]?.room ?? config.startingRoomId;
  // Els inventaris inicials els reparteix el nucli (game.json → start).
  config.initialGameState = { flags: {}, variables: {}, inventory: [] };
  config.defaultFallbackLine = t('ui.defecte', String(config.defaultFallbackLine ?? ''));
  for (const verb of (config.verbs as Json[]) ?? []) {
    verb.label = t(`ui.verb.${verb.id}`, String(verb.label));
    if (verb.preposition !== undefined) verb.preposition = t(`ui.verb.${verb.id}.prep`, String(verb.preposition));
  }
  writeJson(configPath, config);
  report.updated.push('game-config.json');

  // ── GUI ─────────────────────────────────────────────────────────────────
  addGameMenuButtons(gameDir);
  for (const [gui, controls] of Object.entries(GUI_TEXTS)) {
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
      const template = readJson(join(HERE, 'placeholder-art', sprite, `${sprite}.character.json`));
      const current = isNew ? {} : readJson(path);
      const fromSprite = Object.fromEntries(SPRITE_FIELDS.filter((k) => k in template).map((k) => [k, template[k]]));
      writeJson(path, {
        ...template, ...current, ...fromSprite, id,
        speechColor: (current.speechColor as string) ?? SPEECH[id] ?? NPC_COLORS[npcs.indexOf(id) % NPC_COLORS.length],
        defaultVerb: (current.defaultVerb as string) ?? template.defaultVerb ?? (protagonists.includes(id) ? 'look' : 'talkTo'),
      });
      mkdirSync(art, { recursive: true });
      copyFileSync(join(HERE, 'placeholder-art', sprite, `${sprite}.png`), join(art, `${id}.png`));
      const sheet = readJson(join(HERE, 'placeholder-art', sprite, `${sprite}.json`));
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

  // ── Objectes d'inventari ────────────────────────────────────────────────
  for (const [id, def] of Object.entries(content.items)) {
    const path = join(gameDir, 'inventory', id, `${id}.inventory.json`);
    const item = existsSync(path)
      ? readJson(path)
      : { id, onVerb: {}, stackable: false, animations: {}, display: { aseprite: 'shared' } };
    if (!existsSync(path)) report.created.push(`inventory/${id}`);
    item.name = t(def.name, id);
    item.description = t(def.name, id);
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
      const { room: benneRoom, request } = layoutRoom(id, room, content, t);
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
      for (const did of Object.keys(room.decor ?? {})) {
        if (props.some((p) => p.id === did)) continue;
        props.push(decorProp(did));
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
      const fresh = layoutRoom(id, room, content, t).room;
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

// ─── Botons «Canvia» i «Pista» al menú del joc ──────────────────────────────

/**
 * La plantilla té un botó «Title Screen» sense funció: el convertim en dos botons de mitja
 * amplada, canviar de protagonista i demanar una pista. Només una vegada.
 */
function addGameMenuButtons(gameDir: string) {
  const dir = join(gameDir, 'guis/game-menu');
  const jsonPath = join(dir, 'game-menu.gui.json');
  const tsPath = join(dir, 'game-menu.gui.ts');
  if (!existsSync(jsonPath) || !existsSync(tsPath)) return;
  const def = readJson(jsonPath);
  const controls = (def.controls as Json[]) ?? [];
  if (!controls.some((c) => c.id === 'canviar')) {
    const index = controls.findIndex((c) => c.id === 'title-screen');
    const half = controls.find((c) => c.id === 'save');
    if (index < 0 || !half) return;
    const row = (controls[index]!.gridPlacement as Json).row;
    const button = (id: string, align: string) => ({
      ...structuredClone(half), id, gridPlacement: { ...(half.gridPlacement as Json), row, align },
    });
    controls.splice(index, 1, button('canviar', 'center-left'), button('pista', 'center-right'));
    writeJson(jsonPath, def);
  }
  const script = readFileSync(tsPath, 'utf8');
  if (!script.includes('switchProtagonist')) {
    const imports = script.replace(
      /import \{ ([^}]*) \} from '\.\/game-menu\.ids';/,
      (_m, names: string) => `import { ${names.trim()}, canviar, pista } from './game-menu.ids';\nimport { sayHint, switchProtagonist } from '../../narrative/narrative.script';`,
    );
    writeFileSync(tsPath, `${imports.trimEnd()}

// Afegit per adapters/benne (benne-content.ts): canviar de protagonista i demanar una pista.
canviar.onClick(() => {
  gui.hide()
  switchProtagonist()
})

pista.onClick(() => {
  gui.hide()
  sayHint()
})
`);
  }
}

// ─── Disposició automàtica d'una sala nova ──────────────────────────────────

/** Un decorat (`decor` a la sala): un prop que es veu o no segons l'estat, però no es pot clicar. */
// Per sobre dels props clicables (zIndex 3): un decorat pot canviar l'aspecte d'un prop. No es pot clicar.
const decorProp = (id: string) => ({ id, tag: id, animations: { [id]: {} }, zIndex: 4, visible: false, alpha: 1, clickable: false });

interface Box { id: string; label: string; x: number; y: number; w: number; h: number; kind: 'hotspot' | 'prop' | 'exit' }

const rect = (b: { x: number; y: number; w: number; h: number }) => [
  { x: b.x, y: b.y }, { x: b.x + b.w, y: b.y }, { x: b.x + b.w, y: b.y + b.h }, { x: b.x, y: b.y + b.h },
];

/** Personatges que parlen en una sala sense ser-hi com a cosa (p. ex. la MARE per l'altaveu). */
function voicesIn(room: RoomDef, content: GameContent): string[] {
  const who = new Set<string>();
  const scan = (list: InteractionDef[] = []) => {
    for (const i of list) {
      for (const l of i.lines ?? []) who.add(l.who);
      if (i.dialogue) {
        const d = content.dialogues[i.dialogue];
        if (d) {
          who.add(d.with);
          for (const n of Object.values(d.nodes)) for (const l of n.lines ?? []) who.add(l.who);
        }
      }
    }
  };
  scan(room.onEnter);
  for (const h of Object.values(room.hotspots)) scan(h.interactions);
  return [...who].filter(
    (w) => content.characters[w] && !content.manifest.protagonists.includes(w) && !(w in room.hotspots),
  );
}

function layoutRoom(id: string, room: RoomDef, content: GameContent, t: (k?: string, d?: string) => string) {
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
    ...Object.keys(room.decor ?? {}).map(decorProp),
  ];

  const spawn: Json[] = [];
  const protagonist = room.protagonist;
  if (protagonist) {
    spawn.push({ instanceId: `${protagonist}-1`, definition: `${protagonist}/${protagonist}.character.json`, x: W / 2, y: s(136), initialFacing: 'D', initialAnimation: 'Idle', visible: true, zIndex: 10 });
  }
  characters.forEach((c, n) => {
    const x = characters.length === 1 ? s(270) : s(70) + n * ((W - s(140)) / Math.max(1, characters.length - 1));
    spawn.push({ instanceId: `${c}-1`, definition: `${c}/${c}.character.json`, x: Math.round(x), y: s(130), initialFacing: 'D', initialAnimation: 'Idle', visible: true, zIndex: 9 });
  });
  voicesIn(room, content).forEach((c, n) => {
    // Una veu: hi és perquè pugui parlar, però no es veu ni es pot clicar.
    spawn.push({ instanceId: `${c}-veu`, definition: `${c}/${c}.character.json`, x: s(40 + n * 30), y: s(70), initialFacing: 'D', initialAnimation: 'Idle', visible: false, clickable: false, zIndex: 1 });
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
    era: protagonist ?? '',
    floorTop: s(112),
    floorBottom: FLOOR_BOTTOM,
    boxes,
    characters: characters.map((c) => t(content.characters[c]?.name, c)),
  };
  return { room: benneRoom, request };
}
