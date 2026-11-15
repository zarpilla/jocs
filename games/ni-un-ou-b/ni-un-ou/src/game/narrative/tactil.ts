// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
/**
 * La interfície tàctil (sense barra de verbs), part instantània (l'estat del menú d'accions, on s'ha premut,
 * l'encaminador). Les funcions amb temps (fer la interacció, obrir i triar al menú) són a `tactil.script.ts`.
 *
 *  - Tocar (clic) una cosa (`queFaElToc`, runtime/accions.ts): la primera vegada, la mira; després, si té una sola
 *    acció la fa, i si en té més d'una obre el menú d'accions (el jugador tria el verb). Les sortides, s'hi va.
 *  - Mantenir premut (o clic dret): el menú d'accions, amb «Mira» i les accions que té la cosa ara mateix.
 *  - Tocar un objecte de l'inventari: el pren a la mà (ho fa el motor: `toca` és un verb d'objecte). Llavors
 *    tocar una cosa el fa servir amb ella, o li dona si és un personatge. Tocar el mateix objecte o el terra, el deixa.
 *    Si l'objecte es fa servir sol (el contingut no el combina mai amb res: el plànol), el motor fa el seu
 *    `defaultVerb`, `fes` (el posa el sync), i tocar-lo en fa l'acció (`queFaElTocObjecte`).
 *
 * Els clics arriben al pont compartit (`routeInteraction`, narrative.script.ts) i aquest encaminador (que registra
 * el bloc generat de globalScript.ts) se'ls queda; la interacció del JSON la fa `performInteraction`, com sempre.
 * Compartida (adapters/benne/tactil/runtime/): `npm run benne:sync` la copia a `src/game/narrative/` dels jocs amb
 * `tactil: true`. No l'editis allà.
 */
import type { FallbackTarget } from '@benne/script';
import type { TouchRouter } from './narrative';
import { narrative } from './narrative';
import { routeTouch } from './tactil.script';

/** Els dos verbs de la interfície (game-config.json, els posa adapters/benne/tactil/index.ts). */
export const TOCA = 'toca';
export const MENU = 'accions';
/** El verb que fa tocar un objecte sol de l'inventari (el seu `defaultVerb`): en fa l'acció en lloc de prendre'l. */
export const FES = 'fes';

// ─── El dit que ha obert el menú ────────────────────────────────────────────

/** Si hi ha un dit (o el botó esquerre) premut ara mateix. */
let prement = false;
/** El menú s'ha obert mantenint premut: el dit encara no s'ha aixecat. */
let esperantAixecar = false;
/** L'aixecament del dit que ha obert el menú: els botons del menú no l'han de prendre per un clic. */
let empassaFins = 0;

if (typeof window !== 'undefined') {
  window.addEventListener('pointerdown', (e) => {
    if (e.button === 0) prement = true;
  }, true);
  const aixeca = (e: PointerEvent) => {
    if (e.button !== 0) return;
    prement = false;
    if (esperantAixecar) {
      esperantAixecar = false;
      empassaFins = performance.now() + 400;
    }
  };
  window.addEventListener('pointerup', aixeca, true);
  window.addEventListener('pointercancel', aixeca, true);
}

/** Si aquest clic d'un botó del menú és, de fet, el dit que s'aixeca després d'obrir-lo (s'ha d'ignorar). */
export const isOpeningRelease = () => performance.now() < empassaFins;

// ─── El menú d'accions ──────────────────────────────────────────────────────

export interface Opcio {
  text: string;
  /** El verb que es fa, o `null` per prendre a la mà l'objecte de l'inventari. */
  verb: string | null;
}

export interface Menu {
  target: FallbackTarget;
  titol: string;
  opcions: Opcio[];
  /** On s'ha premut, en píxels de la pantalla del joc (el menú va al costat). */
  x: number;
  y: number;
}

let menu: Menu | null = null;

/** El menú obert (el llegeix accions.gui.ts per pintar-lo), o `null`. */
export const openMenu = () => menu;

/** Posa (o treu) el menú. En obrir-lo mantenint premut, el dit que s'aixeca no compta com a clic. */
export function setMenu(m: Menu | null) {
  menu = m;
  esperantAixecar = m !== null && prement;
  empassaFins = 0;
}

/** El text d'una opció del menú (`ui.accio.<verb>`). */
export const label = (verb: string) => narrative.t(`ui.accio.${verb}`);

// ─── L'encaminador ──────────────────────────────────────────────────────────

export const touchRouter: TouchRouter = {
  // `toca`, `fes` i `accions` són seus; i, amb un objecte a la mà, decideix entre donar i fer servir.
  takes: (verb, _target, item) => verb === TOCA || verb === FES || verb === MENU || item !== undefined,
  route: (verb, target, item) => routeTouch(verb, target, item),
};
