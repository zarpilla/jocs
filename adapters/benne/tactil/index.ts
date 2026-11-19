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
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
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
