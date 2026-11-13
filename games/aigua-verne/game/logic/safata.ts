/**
 * La safata de les copes (Acte 3): al palau, l'Iri (al saló) i la Vet (al servei) no es poden veure. L'Iri deixa
 * una cosa a la safata (acció `safata.posar`) i els cambrers la baixen al passaplats del servei, on la Vet la
 * recull (`safata.recollir`). La safata és una variable (`safata`: l'objecte que hi ha, o buit).
 */
import type { ActionResult, Narrative } from '@aventura/narrative-core';

export const SAFATA_TEXTS = ['safata.posa', 'safata.plena', 'safata.no', 'safata.recull', 'safata.buida'];

const player = (text: string, params?: Record<string, string>) => ({ who: 'player' as const, text, params });

export function posar(n: Narrative, item: string): ActionResult {
  const props = n.content.items[item]?.props ?? {};
  if (props.mosca !== true) return { lines: [player('safata.no')] };
  if (String(n.getVar('safata') ?? '')) return { lines: [player('safata.plena')] };
  n.apply([{ takeItem: item }, { setVar: 'safata', value: item }]);
  return { lines: [player('safata.posa', { objecte: n.t(`obj.${item}.amb_article`) })] };
}

export function recollir(n: Narrative): ActionResult {
  const item = String(n.getVar('safata') ?? '');
  if (!item) return { lines: [player('safata.buida')] };
  n.apply([{ setVar: 'safata', value: '' }, { giveItem: item }]);
  return { lines: [player('safata.recull', { objecte: n.t(`obj.${item}.amb_article`) })] };
}

export function installSafata(n: Narrative) {
  n.registerAction('safata.posar', ({ args }) => posar(n, String(args.item ?? '')));
  n.registerAction('safata.recollir', () => recollir(n));
}
