/**
 * Frases d'un objecte concret («Mosca: porta el tornavís a l'Iri.»), en lloc d'un text amb `{objecte}`, perquè es
 * puguin gravar amb veu. Les claus són `<base>.<objecte>[.<més>]`; si no n'hi ha, es diu la genèrica, que no
 * anomena l'objecte. Quins objectes en tenen surt d'items.json: el que porta la Mosca (`mosca: true`) i el que es pot
 * donar (tot menys el que té `no_donar` i `no_mosca`).
 */
import type { Narrative } from '@aventura/narrative-core';

import ITEMS from '../data/items.json' with { type: 'json' };

type Props = { mosca?: boolean; no_donar?: boolean; no_mosca?: string };
const objectes = Object.entries(ITEMS as Record<string, unknown>)
  .filter(([, v]) => typeof v === 'object' && v !== null)
  .map(([id, v]) => ({ id, props: ((v as { props?: Props }).props ?? {}) as Props }));

/** El que porta la Mosca i passa per la safata del saló. */
export const OBJECTES_MOSCA = objectes.filter((o) => o.props.mosca === true).map((o) => o.id);
/** El que es pot donar en mà. */
export const OBJECTES_DONAR = objectes.filter((o) => !(o.props.no_donar === true && typeof o.props.no_mosca === 'string')).map((o) => o.id);

/** La clau més concreta que existeix: `<base>.<parts...>`, o la genèrica. */
export function perObjecte(n: Narrative, base: string, ...parts: string[]) {
  const k = [base, ...parts].join('.');
  return n.i18n.has(k) ? k : base;
}
