/**
 * La interfície tàctil (sense barra de verbs, pensada per al mòbil), per als jocs amb `tactil: true` al seu joc.ts.
 *
 *  - Tocar una cosa amb el dit: la primera vegada la mira; després, si té una sola acció la fa, i si en té més d'una
 *    obre el menú d'accions. Amb el ratolí, el clic esquerre fa el mateix sense mirar primer, i el clic dret mira.
 *    Mantenir premut (el dit o el botó esquerre): el menú d'accions. Regla: `queFaElToc` (runtime/accions.ts).
 *  - L'alçada de la pantalla s'adapta a l'aparell (de 640×288, un mòbil 20:9, a 640×360, un monitor 16:9), i el HUD
 *    es col·loca segons quanta franja queda sota l'escena (guis/verbs/hud.ts).
 *
 * Què hi ha aquí i on va (ho fa `npm run benne:sync`, vegeu sync.ts):
 *
 *   runtime/         → src/game/narrative/ (al costat del pont; el runtime propi del joc encara el pot substituir)
 *   guis/            → src/game/guis/ (els scripts del HUD `verbs` i del menú `accions`)
 *   GLOBAL_SCRIPT    → al bloc generat de globalScript.ts (l'encaminador dels clics)
 *   configuraTactil  → game-config.json (resolució adaptable, els verbs `toca` i `accions`, el perfil d'entrada)
 *   mesura.ts        → per als tests: com es juga un camí sencer amb el toc (games/<joc>/game/test/tactil.test.ts)
 *
 * El que fa cada joc: l'art i els .gui.json del HUD i del menú (`tools/hd640/hud.py`, amb els ids i les mides que
 * esperen els scripts de guis/), la pantalla adaptable de sales i GUI (`tools/hd640/pantalla.py`), i els textos
 * `ui.accio.*` i `ui.verb.toca`/`ui.verb.accions` a game/locales.
 */
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

type Json = Record<string, unknown>;
type Translate = (key: string | undefined, def?: string) => string;

export const TACTIL_DIR = dirname(fileURLToPath(import.meta.url));
export const TACTIL_RUNTIME = join(TACTIL_DIR, 'runtime');

/** Els scripts de GUI (camí dins src/game/, igual que dins guis/ d'aquí). */
export const TACTIL_GUIS = ['guis/verbs/hud.ts', 'guis/verbs/verbs.gui.ts', 'guis/accions/accions.gui.ts'];

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
