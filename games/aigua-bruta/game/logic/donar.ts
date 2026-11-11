/**
 * Donar un objecte a l'altra protagonista quan són a la mateixa sala (les sales de l'Arenga són compartides):
 * «Dona el travesser a l'Iri». Acció `donar`, a les interaccions de l'Iri i la Vet a characters.json.
 */
import type { ActionResult, Narrative } from '@aventura/narrative-core';

export const DONAR_TEXTS = ['donar.dona'];

export function donar(n: Narrative, item: string): ActionResult {
  const who = n.world.activeProtagonist();
  const other = n.content.manifest.protagonists.find((p) => p !== who)!;
  const props = n.content.items[item]?.props ?? {};
  if (typeof props.no_munta === 'string') return { lines: [{ who: 'player', text: props.no_munta }] };
  n.apply([{ takeItem: item }, { giveItem: item, who: other }]);
  return { lines: [{ who: 'player', text: 'donar.dona', params: { objecte: n.t(`obj.${item}.amb_article`) } }] };
}

export function installDonar(n: Narrative) {
  n.registerAction('donar', ({ args }) => donar(n, String(args.item ?? '')));
}
