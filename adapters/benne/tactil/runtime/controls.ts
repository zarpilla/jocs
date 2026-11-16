/**
 * La targeta «Com es juga» (GUI `controls`; l'art i el .gui.json els fa tactil/controls.py des del hud.py de cada joc,
 * i el script és tactil/guis/controls/controls.gui.ts): com es juga amb el dit o amb el ratolí.
 *
 *  - Surt quan es prem «Comença», «Continua» o «Carrega una partida» a la portada (una vegada per sessió; en tancar-la
 *    es fa el que s'havia triat: controls.script.ts), fins que el jugador marca «No ho tornis a mostrar» (una
 *    preferència de cada joc i de cada aparell: preferencies.ts).
 *  - Amb el ratolí, s'hi pot triar què fa cada botó (per defecte, l'esquerre fa i el dret mira), i els textos ho diuen a l'acte.
 *  - Es pot tornar a veure des de les opcions («Controls»), i en tancar-la es torna a les opcions.
 *  - Ensenya el dit o el ratolí segons l'aparell: el de l'última pulsació, o, si encara no se n'ha fet cap, si la
 *    pantalla és tàctil.
 *
 * Compartida (adapters/benne/tactil/runtime/): `npm run benne:sync` la copia a `src/game/narrative/`. No l'editis allà.
 */
import { guis } from '@game';
import { narrative } from './narrative';
import { esDit, haPremut } from './tactil';
import { esquerreMira, preferencies } from './preferencies';

/** El que s'ha triat a la portada, que es fa en tancar la targeta. */
export type Despres = 'comenca' | 'continua' | 'carrega';

let jaMostrada = false;
let tornaAOpcions = false;
let despres: Despres | null = null;

/** Si cal ensenyar la targeta abans de jugar: la primera vegada de la sessió, si no s'ha dit que no. */
export const calMostrarControls = () => !jaMostrada && !preferencies().noMostrisControls;

/** Mostra la targeta. Des de les opcions, en tancar-la s'hi torna; des de la portada, es fa el que s'havia triat. */
export function mostraControls(desDeLesOpcions = false, i?: Despres) {
  tornaAOpcions = desDeLesOpcions;
  despres = i ?? null;
  jaMostrada = true;
  guis.controls.show();
}

/** El que s'havia triat a la portada (i ja no hi és). */
export function treuDespres(): Despres | null {
  const que = despres;
  despres = null;
  return que;
}

export function tancaControls() {
  guis.controls.hide();
  if (tornaAOpcions) guis.settingsMenu.show();
  tornaAOpcions = false;
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

/** Els textos de les tres files (`ui.controls.*`), per a l'aparell d'ara. */
export function filesControls(): string[] {
  if (ambElDit()) return [0, 1, 2].map((i) => narrative.t(`ui.controls.dit.${i}`));
  const inv = esquerreMira();
  return [
    narrative.t(inv ? 'ui.controls.ratoli.esquerre.mira' : 'ui.controls.ratoli.esquerre'),
    narrative.t(inv ? 'ui.controls.ratoli.dret.fa' : 'ui.controls.ratoli.dret'),
    narrative.t('ui.controls.ratoli.punts'),
  ];
}
