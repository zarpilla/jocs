/**
 * Donar un objecte a l'altra protagonista quan són a la mateixa sala (les sales de l'Arenga són compartides):
 * «Dona el travesser a l'Iri». Acció `donar`, a les interaccions de l'Iri i la Vet a characters.json.
 */
import type { ActionResult, Narrative } from '@aventura/narrative-core';

import { OBJECTES_MUNTA } from './muntacarregues.js';

/** Una frase per objecte (`donar.dona.<objecte>`), perquè es pugui gravar; si no n'hi ha, la genèrica. */
export const DONAR_TEXTS = ['donar.dona', ...OBJECTES_MUNTA.map((item) => `donar.dona.${item}`)];

export function donar(n: Narrative, item: string): ActionResult {
  const who = n.world.activeProtagonist();
  const other = n.content.manifest.protagonists.find((p) => p !== who)!;
  const props = n.content.items[item]?.props ?? {};
  if (typeof props.no_munta === 'string') return { lines: [{ who: 'player', text: props.no_munta }] };
  n.apply([{ takeItem: item }, { giveItem: item, who: other }]);
  const k = `donar.dona.${item}`;
  return { lines: [{ who: 'player', text: n.i18n.has(k) ? k : 'donar.dona' }] };
}

export function installDonar(n: Narrative) {
  n.registerAction('donar', ({ args }) => donar(n, String(args.item ?? '')));
}
