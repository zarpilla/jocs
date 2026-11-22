/**
 * Donar un objecte a l'altra protagonista quan són a la mateixa sala (les sales són compartides):
 * «Dona el travesser a l'Iri». Acció `donar`, a les interaccions de l'Iri i la Vet a characters.json.
 */
import type { ActionResult, Narrative } from '@aventura/narrative-core';

import { OBJECTES_DONAR, perObjecte } from './perobjecte.js';

export const DONAR_TEXTS = ['donar.dona', ...OBJECTES_DONAR.map((item) => `donar.dona.${item}`)];

export function donar(n: Narrative, item: string): ActionResult {
  const who = n.world.activeProtagonist();
  const other = n.content.manifest.protagonists.find((p) => p !== who)!;
  const props = n.content.items[item]?.props ?? {};
  // Només el que no es pot donar de cap manera (el comunicador, la Mosca). El que no pot portar la Mosca (pesa
  // massa, és aigua), en persona sí que es dona.
  if (props.no_donar === true && typeof props.no_mosca === 'string') return { lines: [{ who: 'player', text: props.no_mosca }] };
  n.apply([{ takeItem: item }, { giveItem: item, who: other }]);
  return { lines: [{ who: 'player', text: perObjecte(n, 'donar.dona', item) }] };
}

export function installDonar(n: Narrative) {
  n.registerAction('donar', ({ args }) => donar(n, String(args.item ?? '')));
}
