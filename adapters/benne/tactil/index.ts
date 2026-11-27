/**
 * La interfície tàctil (sense barra de verbs, pensada per al mòbil), per als jocs amb `tactil: true` al seu joc.ts.
 *
 *  - Tocar una cosa amb el dit: la primera vegada la mira; després, si té una sola acció la fa, i si en té més d'una
 *    obre el menú d'accions. Amb el ratolí, per defecte el clic esquerre mira i el dret fa l'acció (o obre el menú).
 *    Mantenir premut (el dit o el botó esquerre): el menú d'accions. Regla: `queFaElToc` (runtime/accions.ts).
 *  - L'alçada de la pantalla s'adapta a l'aparell (de 640×288, un mòbil 20:9, a 640×360, un monitor 16:9), i el HUD
 *    es col·loca segons quanta franja queda sota l'escena (guis/verbs/hud.ts).
 *
 * Què hi ha aquí i on va (ho fa `npm run benne:sync`, vegeu sync.ts):
 *
 *   runtime/         → src/game/narrative/ (al costat del pont; el runtime propi del joc encara el pot substituir)
 *   guis/            → src/game/guis/ (els scripts del HUD `verbs`, del menú `accions` i de la targeta `controls`)
 *   opcionsTactils   → el menú d'opcions: «clic esquerre per fer» (girar els botons) i el botó «Controls»
 *   menuDialeg       → la GUI `menu-dialeg`: el botó del menú, a sobre del panell de les opcions d'una conversa
 *   dialegTauler     → el panell de les opcions d'una conversa: opcions més baixes, i la GUI `fons-dialeg` (el fons del
 *                      panell mentre algú parla, al tauler)
 *   controls.py      → per al hud.py de cada joc: l'art i el .gui.json de la targeta «Com es juga»
 *   GLOBAL_SCRIPT    → al bloc generat de globalScript.ts (l'encaminador dels clics)
 *   configuraTactil  → game-config.json (resolució adaptable, els verbs `toca` i `accions`, el perfil d'entrada)
 *   mesura.ts        → per als tests: com es juga un camí sencer amb el toc (games/<joc>/game/test/tactil.test.ts)
 *
 * El que fa cada joc: l'art i els .gui.json del HUD i del menú (`tools/hd640/hud.py`, amb els ids i les mides que
 * esperen els scripts de guis/, i la targeta amb controls.py), la pantalla adaptable de sales i GUI
 * (`tools/hd640/pantalla.py`), i els textos `ui.accio.*`, `ui.verb.toca`/`accions`/`fes`, `ui.controls.*` i
 * `ui.opcions.*` a game/locales.
 */
import { copyFileSync, existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

type Json = Record<string, unknown>;
type Translate = (key: string | undefined, def?: string) => string;

export const TACTIL_DIR = dirname(fileURLToPath(import.meta.url));
export const TACTIL_RUNTIME = join(TACTIL_DIR, 'runtime');

/** Els scripts de GUI (camí dins src/game/, igual que dins guis/ d'aquí). */
export const TACTIL_GUIS = [
  'guis/verbs/hud.ts', 'guis/verbs/verbs.gui.ts', 'guis/accions/accions.gui.ts', 'guis/controls/controls.gui.ts',
];

/** Els textos fixos de les GUI de la interfície tàctil (GUI → control → clau), que el sync posa dels locales. */
export const TACTIL_TEXTOS: Record<string, Record<string, string>> = {
  controls: {
    titol: 'ui.controls.titol', dacord: 'ui.controls.dacord', intercanviaText: 'ui.controls.intercanvia',
  },
  'settings-menu': { 'botons-text': 'ui.opcions.botons', controls: 'ui.opcions.controls' },
};

/**
 * El verb dels objectes que es fan servir sols (el contingut no els combina mai amb res: `objecteSol`): el sync el
 * posa de `defaultVerb`, i tocar-los a l'inventari en fa l'acció en lloc de prendre'ls a la mà.
 */
export const FES = 'fes';

/** L'alçada mínima: 20:9 (un mòbil apaisat). */
const MOBIL = 9 / 20;

/** game-config.json d'un joc tàctil. */
export function configuraTactil(config: Json, t: Translate) {
  // L'alçada s'adapta a la pantalla (motor: `resolution.minHeight`): de 20:9 en un mòbil fins a l'alçada del joc
  // (16:9) en un monitor. Les GUI es dissenyen a la mínima i s'enganxen a dalt, al mig o a baix (`anchorY`).
  const res = (config.resolution as { width: number; height: number } | undefined) ?? { width: 640, height: 360 };
  config.resolution = { width: res.width, height: res.height, minHeight: Math.round(res.width * MOBIL) };
  // Tres verbs de la interfície, que no surten mai al contingut: `toca` (un toc o clic: el runtime tria què fa; és
  // d'objecte, perquè tocar un objecte de l'inventari el pren a la mà) i `accions` (mantenir premut o clic dret: el
  // menú d'accions), i `fes` (tocar un objecte que es fa servir sol). Els nou verbs de sempre es queden: són els del
  // contingut i els del menú.
  const verbs = ((config.verbs as Json[]) ?? []).filter((v) => !['toca', 'accions', FES].includes(String(v.id)));
  config.verbs = [
    { id: 'toca', label: t('ui.verb.toca', 'Toca'), usesItem: true },
    { id: 'accions', label: t('ui.verb.accions', 'Accions') },
    { id: FES, label: t('ui.verb.fes', 'Fes') },
    ...verbs,
  ];
  config.inputProfile = { primaryButtonVerb: 'toca', secondaryButtonVerb: 'accions', holdVerb: 'accions', holdMs: 450 };
}

/** Al bloc generat de globalScript.ts: la interfície tàctil es queda els clics de tocar i del menú d'accions. */
export const GLOBAL_SCRIPT = `
// La interfície tàctil (adapters/benne/tactil): es queda els clics de tocar i del menú d'accions, i tria entre donar
// i fer servir quan hi ha un objecte a la mà (narrative/tactil.script.ts).
import { setTouchRouter } from './narrative/narrative'
import { touchRouter } from './narrative/tactil'
setTouchRouter(touchRouter)
`;

// ─── Les opcions: «clic esquerre per fer» i «Controls» ────────────────────

const OPCIONS_MARCA = '// Afegit per adapters/benne/tactil (index.ts, opcionsTactils)';

type Control = Json & { id?: string; x?: number; y?: number; height?: number; rows?: number; gridPlacement?: Json };

/**
 * Afegeix al menú d'opcions (GUI `settings-menu` de la plantilla) una fila més, «clic esquerre per fer» (girar els
 * botons del ratolí: per defecte, l'esquerre mira i el dret fa), i el botó «Controls» (la targeta «Com es juga») al
 * costat de «Torna». Es pot tornar a
 * executar: si ja hi són, només es regenera el codi afegit al script.
 */
export function opcionsTactils(gameDir: string) {
  const dir = join(gameDir, 'guis/settings-menu');
  const jsonPath = join(dir, 'settings-menu.gui.json');
  const tsPath = join(dir, 'settings-menu.gui.ts');
  if (!existsSync(jsonPath) || !existsSync(tsPath)) return;
  const def = JSON.parse(readFileSync(jsonPath, 'utf8')) as Json;
  const controls = (def.controls as Control[]) ?? [];
  const per = (id: string) => controls.find((c) => c.id === id);
  const grid = per('settings-layout');
  const fons = per('settings-BG');
  const torna = per('back');
  const casella = per('musicEnabled');
  const etiqueta = per('click-to-skip');
  if (grid && fons && torna && casella && etiqueta && !per('intercanvia')) {
    const files = Number(grid.rows ?? 4);
    const alt = Math.round(Number(grid.height ?? 116) / files);     // l'alçada d'una fila
    const puja = Math.round(alt / 2);                                // per tornar-ho a centrar
    for (const c of [fons, per('title'), grid]) if (c && typeof c.y === 'number') c.y -= puja;
    fons.height = Number(fons.height) + alt;
    grid.rows = files + 1;
    grid.height = Number(grid.height) + alt;
    const fila = (c: Control) => ({ ...(c.gridPlacement as Json), row: files });
    controls.push(
      { ...structuredClone(etiqueta), id: 'botons-text', gridPlacement: fila(etiqueta) },
      { ...structuredClone(casella), id: 'intercanvia', checked: false, gridPlacement: fila(casella) },
    );
    // «Controls» i «Torna», l'un al costat de l'altre, a sota de tot
    const ample = Number(torna.width ?? 91);
    const centre = Number(torna.x) + ample / 2;
    torna.y = Number(torna.y) + alt - puja;
    controls.push({ ...structuredClone(torna), id: 'controls', x: Math.round(centre - ample - 7) });
    torna.x = Math.round(centre + 7);
    writeFileSync(jsonPath, JSON.stringify(def, null, 2) + '\n');
  }
  let script = readFileSync(tsPath, 'utf8');
  const marca = script.indexOf(OPCIONS_MARCA);
  if (marca >= 0) script = script.slice(0, marca);
  writeFileSync(tsPath, `${script.trimEnd()}

${OPCIONS_MARCA}: què fa cada botó del ratolí (una preferència
// de cada joc i de cada aparell) i la targeta «Com es juga».
import { intercanvia, controls } from './settings-menu.ids'
import { mostraControls } from '../../narrative/controls'
import { preferencies, setPreferencia } from '../../narrative/preferencies'

gui.onShow(() => {
  intercanvia.checked = preferencies().esquerreFa
})

intercanvia.onChange((on: boolean) => {
  setPreferencia('esquerreFa', on)
})

controls.onClick(() => {
  gui.hide()
  mostraControls()
})
`);
}

// ─── El botó del menú durant una conversa ─────────────────────────────────

/**
 * La GUI `menu-dialeg` (tasca 198): durant una conversa, el motor amaga el HUD, i el panell de les opcions tapa el lloc
 * del botó del menú; sense teclat (la tecla H), no es podia obrir l'historial per repassar què s'havia dit abans de
 * triar. Aquesta GUI és només el botó del menú del HUD (el mateix control i la mateixa art: es copia el full de
 * `verbs`), a la dreta, just a sobre del panell de les opcions, i es veu només mentre les opcions són a la vista.
 * Ancorada a baix, com el panell (`dialog`), perquè hi quedi enganxada a qualsevol alçada de pantalla. Es pot tornar a
 * executar.
 */
export function menuDialeg(gameDir: string) {
  const llegeix = (rel: string) => (existsSync(join(gameDir, rel)) ? JSON.parse(readFileSync(join(gameDir, rel), 'utf8')) as Json : null);
  const verbs = llegeix('guis/verbs/verbs.gui.json');
  const dialeg = llegeix('guis/dialog/dialog.gui.json');
  const boto = ((verbs?.controls as Control[]) ?? []).find((c) => c.id === 'MenuBtn');
  if (!verbs || !dialeg || !boto) return;
  // la vora de dalt del panell: el primer control de les opcions (les fletxes i la graella), a l'alçada de disseny
  const dalt = Math.min(...((dialeg.controls as Control[]) ?? []).map((c) => Number(c.y)).filter((y) => y > 0)) - 4;
  const res = (llegeix('game-config.json')?.resolution ?? {}) as { width?: number };
  const W = res.width ?? 640;
  const mida = Number(boto.width ?? 25);
  for (const ext of ['png', 'json']) {
    const de = join(gameDir, `assets/images/guis/verbs/verbs.${ext}`);
    if (!existsSync(de)) return;
    mkdirSync(join(gameDir, 'assets/images/guis/menu-dialeg'), { recursive: true });
    const a = join(gameDir, `assets/images/guis/menu-dialeg/menu-dialeg.${ext}`);
    if (ext === 'png') copyFileSync(de, a);
    else writeFileSync(a, readFileSync(de, 'utf8').replace(/verbs\.png/g, 'menu-dialeg.png'));
  }
  const dir = join(gameDir, 'guis/menu-dialeg');
  mkdirSync(dir, { recursive: true });
  writeFileSync(join(dir, 'menu-dialeg.gui.json'), JSON.stringify({
    id: 'menu-dialeg', name: 'Menú (conversa)',
    description: "El botó del menú a sobre de les opcions d'una conversa (adapters/benne/tactil/index.ts, menuDialeg).",
    visible: false, display: { aseprite: true }, anchorY: 'bottom', zIndex: 95,
    controls: [{ ...structuredClone(boto), id: 'MenuBtn', x: W - 4 - mida, y: dalt - 4 - Number(boto.height ?? mida) }],
  }, null, 2) + '\n');
  writeFileSync(join(dir, 'menu-dialeg.gui.ts'), `// Creat per adapters/benne/tactil/index.ts (menuDialeg). No l'editis aquí.
// El botó del menú durant una conversa: es veu només amb les opcions a la vista (el motor amaga el HUD).
import { onUpdate } from '@benne/script'
import { guis } from '@game'
import { gui, menuBtn } from './menu-dialeg.ids'

menuBtn.onClick(() => {
  gui.hide()
  guis.gameMenu.show()
})

onUpdate(() => {
  const on = guis.dialog.visible && !guis.gameMenu.visible
  if (gui.visible !== on) {
    if (on) gui.show()
    else gui.hide()
  }
})
`);
}


// ─── Les converses al tauler ──────────────────────────────────────────────

/** L'alçada de cada opció d'una conversa (com a Suma Zero): en els 86 px del panell n'hi caben 4, no 3 (tasca 220). */
const OPCIO_H = 20;

/**
 * El panell de les opcions d'una conversa (GUI `dialog`, l'art i el .gui.json els fa el gui_rest.py de cada joc):
 *
 *  - Opcions de {@link OPCIO_H} px com a molt (a 25 només n'hi cabien 3, i la de sortir quedava sola a la pàgina
 *    següent).
 *  - La GUI `fons-dialeg`: només el fons del panell (el mateix control i la mateixa art, es copia el full de
 *    `dialog`), sota del panell. Mentre algú parla dins d'una conversa, el motor amaga les opcions i el HUD, i la
 *    franja de sota l'escena quedava negra a cada pregunta (tasca 241). Al tauler, el fons s'hi queda: el panell
 *    es veu buit mentre es parla, i les opcions hi tornen a sortir a sobre, sense pampallugues.
 *
 * Es pot tornar a executar.
 */
export function dialegTauler(gameDir: string) {
  const path = join(gameDir, 'guis/dialog/dialog.gui.json');
  if (!existsSync(path)) return;
  const dialeg = JSON.parse(readFileSync(path, 'utf8')) as Json;
  const controls = (dialeg.controls as Control[]) ?? [];
  let canviat = false;
  for (const c of controls) {
    if ((c.id === 'Dialog-Option' || c.id === 'Option-Grid') && Number(c.height) > OPCIO_H) {
      c.height = OPCIO_H;
      canviat = true;
    }
  }
  if (canviat) writeFileSync(path, JSON.stringify(dialeg, null, 2) + '\n');

  const fons = controls.find((c) => c.id === 'DialogBG');
  if (!fons) return;
  for (const ext of ['png', 'json']) {
    const de = join(gameDir, `assets/images/guis/dialog/dialog.${ext}`);
    if (!existsSync(de)) return;
    mkdirSync(join(gameDir, 'assets/images/guis/fons-dialeg'), { recursive: true });
    const a = join(gameDir, `assets/images/guis/fons-dialeg/fons-dialeg.${ext}`);
    if (ext === 'png') copyFileSync(de, a);
    else writeFileSync(a, readFileSync(de, 'utf8').replace(/dialog\.png/g, 'fons-dialeg.png'));
  }
  const dir = join(gameDir, 'guis/fons-dialeg');
  mkdirSync(dir, { recursive: true });
  writeFileSync(join(dir, 'fons-dialeg.gui.json'), JSON.stringify({
    id: 'fons-dialeg', name: 'Fons (conversa)',
    description: "El fons del panell d'una conversa mentre algú parla, al tauler (adapters/benne/tactil/index.ts, dialegTauler).",
    // (per sota del panell `dialog`, que és a 0: amb el mateix zIndex, l'ordre seria per l'id)
    visible: false, display: { aseprite: true }, anchorY: dialeg.anchorY ?? 'bottom', zIndex: -1,
    controls: [{ ...structuredClone(fons), id: 'Fons', clickable: false }],
  }, null, 2) + '\n');
  writeFileSync(join(dir, 'fons-dialeg.gui.ts'), `// Creat per adapters/benne/tactil/index.ts (dialegTauler). No l'editis aquí.
// El fons del panell d'una conversa, al tauler: mentre algú parla, el motor amaga les opcions i el HUD, i la franja de
// sota l'escena quedaria negra. Es veu quan el HUD no hi és en una sala jugable (una conversa); a sobre, el panell.
import { onUpdate } from '@benne/script'
import { guis } from '@game'
import { gui } from './fons-dialeg.ids'
import { modeTauler } from '../verbs/hud'
import { narrative } from '../../narrative/narrative'

onUpdate(() => {
  const sala = narrative.world.currentRoom()
  const jugable = !!sala && sala !== narrative.content.manifest.cover && !narrative.content.rooms[sala]?.cutscene
  const on = jugable && modeTauler() && !guis.verbs.visible
  if (gui.visible !== on) {
    if (on) gui.show()
    else gui.hide()
  }
})
`);
}
