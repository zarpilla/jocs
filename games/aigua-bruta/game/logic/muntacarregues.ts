/**
 * El muntacàrregues de l'Arenga (guio/guio.md, «Regles del món · 3»): l'única manera de passar objectes entre
 * l'Iri i la Vet sense que es trobin. Té tres parades, la cuina, el rebost i el pont, i una safata a cada una.
 *
 * - «Usar objecte amb el muntacàrregues» (acció `munta.enviar`) el posa a la safata d'una altra parada: del
 *   rebost i del pont, sempre a la cuina; de la cuina, al pont si l'altra protagonista hi és, i si no, al rebost.
 * - La safata de cada parada és una variable (`munta_<parada>`: l'objecte que hi ha, o buit). La que el rep
 *   l'agafa (acció `munta.recollir`).
 *
 * Què hi cap és una propietat de cada objecte (`items.json`): `munta: true`. Sense la marca, no hi cap.
 * `no_munta: "<clau>"`: no s'hi posa mai, i aquesta és la raó (el walkie, el quadern).
 */
import type { ActionResult, Narrative } from '@aventura/narrative-core';

export const PARADES = ['cuina', 'rebost', 'pont'] as const;
export type Parada = (typeof PARADES)[number];

export const MUNTA_TEXTS = [
  'munta.envia', 'munta.retorna', 'munta.no_hi_cap', 'munta.ple', 'munta.recull', 'munta.buit', 'munta.cap.cuina', 'munta.cap.rebost', 'munta.cap.pont',
  // Línies pròpies d'alguns objectes (vegeu `extra`).
  'munta.travesser.envia', 'munta.travesser.recull', 'munta.registre.recull',
];

const player = (text: string, params?: Record<string, string>) => ({ who: 'player' as const, text, params });

export const safata = (p: Parada) => `munta_${p}`;

/** La parada de la sala on és la protagonista activa (les tres parades es diuen com la seva sala). */
function paradaActual(n: Narrative): Parada | null {
  const room = n.world.currentRoom();
  return (PARADES as readonly string[]).includes(room ?? '') ? (room as Parada) : null;
}

/** On va el que s'envia des d'una parada. */
export function desti(des: Parada, altraSala: string | null): Parada {
  if (des !== 'cuina') return 'cuina';
  return altraSala === 'pont' ? 'pont' : 'rebost';
}

export function enviar(n: Narrative, item: string, altraSala: string | null): ActionResult {
  const des = paradaActual(n);
  if (!des) return {};
  const props = n.content.items[item]?.props ?? {};
  if (typeof props.no_munta === 'string') return { lines: [player(props.no_munta)] };
  if (props.munta !== true) return { lines: [player('munta.no_hi_cap')] };
  const cap = desti(des, altraSala);
  if (String(n.getVar(safata(cap)) ?? '')) return { lines: [player('munta.ple', { parada: n.t(`munta.cap.${cap}`) })] };

  n.apply([{ takeItem: item }, { setVar: safata(cap), value: item }]);
  const objecte = n.t(`obj.${item}.amb_article`);
  return { lines: [{ ...player('munta.envia', { objecte, parada: n.t(`munta.cap.${cap}`) }), sound: 'muntacarregues' }, ...extra(n, `munta.${item}.envia`)] };
}

export function recollir(n: Narrative): ActionResult {
  const aqui = paradaActual(n);
  if (!aqui) return {};
  const item = String(n.getVar(safata(aqui)) ?? '');
  if (!item) return { lines: [player('munta.buit')] };
  n.apply([{ setVar: safata(aqui), value: '' }, { giveItem: item }]);
  const objecte = n.t(`obj.${item}.amb_article`);
  return { lines: [player('munta.recull', { objecte }), ...extra(n, `munta.${item}.recull`)] };
}

/**
 * Un paper que s'envia sense ser a l'inventari (les notes de l'Escena 5): va a la safata de `parada`. Si la safata ja
 * tenia alguna cosa, torna a qui l'envia (no es pot trepitjar res).
 */
export function nota(n: Narrative, item: string, parada: Parada): ActionResult {
  const lines: NonNullable<ActionResult['lines']> = [];
  const abans = String(n.getVar(safata(parada)) ?? '');
  if (abans) {
    // El que hi havia a la safata baixa (o puja) fins a la parada de qui envia la nota: no es perd res.
    const aqui = paradaActual(n);
    if (aqui && !String(n.getVar(safata(aqui)) ?? '')) n.apply({ setVar: safata(aqui), value: abans });
    else n.apply({ giveItem: abans });
    lines.push(player('munta.retorna', { objecte: n.t(`obj.${abans}.amb_article`) }));
  }
  n.apply({ setVar: safata(parada), value: item });
  lines.push({ ...player('munta.envia', { objecte: n.t(`obj.${item}.amb_article`), parada: n.t(`munta.cap.${parada}`) }), sound: 'muntacarregues' });
  return { lines };
}

/** Línies pròpies d'un objecte en enviar-lo o recollir-lo (`munta.<objecte>.envia`, `.recull`, `.recull2`...). */
function extra(n: Narrative, key: string) {
  const lines: NonNullable<ActionResult['lines']> = [];
  for (const k of [key, `${key}2`, `${key}3`]) {
    if (!n.i18n.has(k)) break;
    lines.push({ who: 'player', text: k });
  }
  return lines;
}

/** On és la protagonista que no juga. */
export function altraSala(n: Narrative) {
  const who = n.content.manifest.protagonists.find((p) => p !== n.world.activeProtagonist())!;
  return n.world.protagonistRoom?.(who) ?? null;
}

export function installMuntacarregues(n: Narrative) {
  n.registerAction('munta.enviar', ({ args }) => enviar(n, String(args.item ?? ''), altraSala(n)));
  n.registerAction('munta.recollir', () => recollir(n));
  n.registerAction('munta.nota', ({ args }) => nota(n, String(args.item ?? ''), String(args.parada ?? 'cuina') as Parada));
}
