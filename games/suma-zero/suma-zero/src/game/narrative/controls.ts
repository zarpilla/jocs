// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
/**
 * La targeta «Com es juga» (GUI `controls`; l'art i el .gui.json els fa tactil/controls.py des del hud.py de cada joc,
 * i el script és tactil/guis/controls/controls.gui.ts): com es juga amb el dit o amb el ratolí.
 *
 *  - No surt sola: s'obre des de les opcions («Controls»), i en tancar-la es torna a les opcions.
 *  - Amb el ratolí, s'hi pot triar què fa cada botó (per defecte, l'esquerre mira i el dret fa), i els textos ho diuen a l'acte.
 *  - Ensenya el dit o el ratolí segons l'aparell: el de l'última pulsació, o, si encara no se n'ha fet cap, si la
 *    pantalla és tàctil.
 *
 * Compartida (adapters/benne/tactil/runtime/): `npm run benne:sync` la copia a `src/game/narrative/`. No l'editis allà.
 */
import { guis } from '@game';
import { narrative } from './narrative';
import { esDit, haPremut } from './tactil';
import { esquerreMira } from './preferencies';

/** Mostra la targeta (des de les opcions: en tancar-la s'hi torna). */
export function mostraControls() {
  guis.controls.show();
}

/** «D'acord»: es tanca i es torna a les opcions. */
export function tancaControls() {
  guis.controls.hide();
  guis.settingsMenu.show();
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
  const mira = esquerreMira();
  return [
    narrative.t(mira ? 'ui.controls.ratoli.esquerre.mira' : 'ui.controls.ratoli.esquerre'),
    narrative.t(mira ? 'ui.controls.ratoli.dret.fa' : 'ui.controls.ratoli.dret'),
    narrative.t('ui.controls.ratoli.punts'),
  ];
}
