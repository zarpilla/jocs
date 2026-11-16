/**
 * La targeta «Com es juga», part amb temps (BenneScript): els botons de la portada hi passen abans de jugar. Quan surt
 * i què diu: controls.ts.
 *
 * Compartida (adapters/benne/tactil/runtime/): `npm run benne:sync` la copia a `src/game/narrative/`. No l'editis allà.
 */
import { saves } from '@benne/script';
import { guis } from '@game';
import { AUTOSAVE } from './narrative';
import { startFromCover } from './narrative.script';
import { calMostrarControls, mostraControls, tancaControls, treuDespres, type Despres } from './controls';

/** Un botó de la portada: la primera vegada (si cal), la targeta; i, en tancar-la, el que s'havia triat. */
export function abansDeJugar(que: Despres) {
  if (calMostrarControls()) {
    mostraControls(false, que);
    return;
  }
  juga(que);
}

/** «D'acord» a la targeta: es tanca i, si venia de la portada, es fa el que s'havia triat. */
export function tancaIJuga() {
  const que = treuDespres();
  tancaControls();
  if (que) juga(que);
}

function juga(que: Despres) {
  if (que === 'comenca') startFromCover();
  else if (que === 'continua') saves.load(AUTOSAVE);
  else guis.loadMenu.show();
}
