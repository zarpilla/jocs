// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
/**
 * La targeta «Com es juga» (GUI `controls`; l'art i el .gui.json els fa tactil/controls.py des del hud.py de cada joc,
 * i el script és tactil/guis/controls/controls.gui.ts): com es juga amb el dit o amb el ratolí.
 *
 *  - Surt sola un cop a cada partida nova («Comença»), quan ja es pot jugar: després del pròleg, de les cinemàtiques i
 *    de les converses i línies de l'entrada (`vigilaControls`, cada fotograma). En tancar-la, es juga.
 *  - També s'obre des de les opcions («Controls»), i aleshores en tancar-la es torna a les opcions.
 *  - Amb el ratolí, s'hi pot triar què fa cada botó (per defecte, l'esquerre mira i el dret fa), i els textos ho diuen a l'acte.
 *  - L'última fila diu on es demana una pista (`ui.controls.pista`, de cada joc: al menú o al botó de la pista).
 *  - Ensenya el dit o el ratolí segons l'aparell: el de l'última pulsació, o, si encara no se n'ha fet cap, si la
 *    pantalla és tàctil.
 *
 * Compartida (adapters/benne/tactil/runtime/): `npm run benne:sync` la copia a `src/game/narrative/`. No l'editis allà.
 */
import { guis } from '@game';
import { game } from '@benne/script';
import { narrative } from './narrative';
import { onNewGame } from './narrative.script';
import { esDit, haPremut } from './tactil';
import { esquerreMira } from './preferencies';

/** Si s'ha obert des de les opcions (en tancar-la, s'hi torna). */
let desDeLesOpcions = false

/** S'ha clicat «Comença» i la targeta encara no ha sortit. */
let pendent = false

/** Des de quan (ms) es pot jugar sense interrupció: entre línia i línia d'una escena hi ha un instant lliure. */
let lliureDes: number | null = null

/** Quanta estona (ms) s'ha de poder jugar seguit abans que surti. */
const CALMA = 700

/** Les GUI que, obertes, volen dir que encara no és el moment (menús, la portada, el menú d'accions...). */
const OCUPADES = ['portada', 'gameMenu', 'settingsMenu', 'loadMenu', 'saveMenu', 'historial', 'accions', 'mapa']

onNewGame(() => {
  pendent = true
  lliureDes = null
})

/** Mostra la targeta (des de les opcions: en tancar-la s'hi torna). */
export function mostraControls() {
  desDeLesOpcions = true
  guis.controls.show();
}

/** «D'acord»: es tanca i, si s'havia obert des de les opcions, s'hi torna. */
export function tancaControls() {
  guis.controls.hide();
  if (desDeLesOpcions) guis.settingsMenu.show();
  desDeLesOpcions = false
}

/** Ja es pot jugar: una sala jugable, amb la barra a la vista, sense res que parli, ni cinemàtica, ni cap menú obert. */
function esPotJugar(): boolean {
  const sala = narrative.world.currentRoom()
  if (!sala || sala === narrative.content.manifest.cover || narrative.content.rooms[sala]?.cutscene) return false
  if (game.isBusy || game.isCutsceneActive || !guis.verbs.visible || guis.controls.visible) return false
  const totes = guis as unknown as Record<string, { visible: boolean } | undefined>
  return !OCUPADES.some((id) => totes[id]?.visible)
}

/** Cada fotograma: després de «Comença», la targeta surt sola quan ja fa una estona que es pot jugar. */
export function vigilaControls() {
  if (!pendent) return
  if (!esPotJugar()) {
    lliureDes = null
    return
  }
  const ara = Date.now()
  lliureDes ??= ara
  if (ara - lliureDes < CALMA) return
  pendent = false
  lliureDes = null
  desDeLesOpcions = false
  guis.controls.show();
}

/** Amb el dit o amb el ratolí (què ensenya la targeta). */
export function ambElDit(): boolean {
  if (haPremut()) return esDit();
  try {
    return typeof matchMedia !== 'undefined' && matchMedia('(pointer: coarse)').matches;
  } catch {
    return false;
  }
}

/**
 * Els textos de les cinc files (`ui.controls.*`), per a l'aparell d'ara: tocar o clicar, mantenir premut o l'altre
 * botó, l'inventari, els punts i la pista (aquesta, igual per a tots dos). Cada fila diu una sola cosa: la de la icona.
 */
export function filesControls(): string[] {
  const pista = narrative.t('ui.controls.pista');
  if (ambElDit()) return [...[0, 1, 2, 3].map((i) => narrative.t(`ui.controls.dit.${i}`)), pista];
  const mira = esquerreMira();
  return [
    narrative.t(mira ? 'ui.controls.ratoli.esquerre.mira' : 'ui.controls.ratoli.esquerre'),
    narrative.t(mira ? 'ui.controls.ratoli.dret.fa' : 'ui.controls.ratoli.dret'),
    narrative.t('ui.controls.ratoli.inventari'),
    narrative.t('ui.controls.ratoli.punts'),
    pista,
  ];
}
