/**
 * La interfície tàctil (sense barra de verbs), part amb temps (BenneScript). Què fa cada gest: `tactil.ts`.
 * Compartida (adapters/benne/tactil/runtime/): `npm run benne:sync` la copia a `src/game/narrative/` dels jocs amb
 * `tactil: true`. No l'editis allà.
 */
import { guis } from '@game';
import { pointer } from '@benne/script';
import type { FallbackTarget } from '@benne/script';
import { fromBenne, narrative, targetFromBenne } from './narrative';
import { performInteraction } from './narrative.script';
import { accions, marcaMirat, objecteSol, queFaElToc, verbAmbObjecte } from './accions';
import { MENU, esClicDret, esDit, label, openMenu, setMenu, type Opcio } from './tactil';

/** Fa el que vol dir un clic de la interfície tàctil (vegeu tactil.ts). */
export function routeTouch(verb: string, target: FallbackTarget, item?: string) {
  if (item !== undefined) {
    // Tocar l'objecte que ja tens a la mà: el deixes.
    if (target.kind === 'item' && target.id === item) {
      pointer.item = null;
      return;
    }
    const amb = verbAmbObjecte(narrative, targetFromBenne(target.kind, target.id), fromBenne('items', item));
    performInteraction(amb, target, item);
    return;
  }
  if (verb === MENU) {
    // el clic dret del ratolí mira; mantenir premut (el dit o el botó esquerre) obre el menú
    if (esClicDret()) doVerb('look', target);
    else openActions(target);
    return;
  }
  const toc = queFaElToc(narrative, targetFromBenne(target.kind, target.id), undefined, { mirarPrimer: esDit() });
  if (toc.fa === 'menu') {
    openActions(target);
    return;
  }
  doVerb(toc.fa === 'mira' ? 'look' : toc.verb, target);
}

/** Fa un verb sobre una cosa (si és mirar, apunta que ja s'ha mirat). */
function doVerb(verb: string, target: FallbackTarget) {
  if (verb === 'look') marcaMirat(narrative, targetFromBenne(target.kind, target.id));
  performInteraction(verb, target);
}

/**
 * Obre el menú d'accions d'una cosa: «Mira», «Usa-ho amb...» (si és un objecte de l'inventari que es pot combinar
 * amb alguna cosa) i les seves accions d'ara.
 */
export function openActions(target: FallbackTarget) {
  const opcions: Opcio[] = [{ text: label('look'), verb: 'look' }];
  if (target.kind === 'item' && !objecteSol(narrative.content, fromBenne('items', target.id))) {
    opcions.push({ text: label('armar'), verb: null });
  }
  const totes = accions(narrative, targetFromBenne(target.kind, target.id));
  for (const a of totes) opcions.push({ text: label(a.verb), verb: a.verb });
  const on = pointer.screen;
  setMenu({ target, titol: target.name, opcions, x: on.x, y: on.y });
  guis.accions.show();
}

/** Tria l'opció `i` del menú: el tanca i la fa. */
export function chooseOption(i: number) {
  const m = openMenu();
  closeMenu();
  const opcio = m?.opcions[i];
  if (!m || !opcio) return;
  if (opcio.verb === null) {
    pointer.item = { id: m.target.id };
    return;
  }
  doVerb(opcio.verb, m.target);
}

export function closeMenu() {
  setMenu(null);
  guis.accions.hide();
}
