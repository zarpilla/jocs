/**
 * El tub pneumàtic del BCMU (regles a guio/guio.md, «Regles del món · 3»): l'única via per passar
 * objectes entre l'Iri i la Vet dins del banc.
 *
 * «Usar objecte amb el tub» (acció `tub.enviar`, a l'estació de cada sala) l'envia a l'altra
 * protagonista, que ho diu per l'auricular. El joc no canvia de protagonista. Què hi cap i a qui li fa
 * falta són propietats de cada objecte (`items.json`):
 *
 * - `cap_al_tub: true`: hi cap (claus, papers, l'entrepà...). Sense la marca, no hi cap.
 * - `tub_per: "iri"`: a qui li fa falta. Si no és l'altra, «No li fa cap falta».
 * - `tub_fins: "<flag>"`: li fa falta fins que el flag és cert (l'entrepà, fins que el robot s'atura).
 * - `no_enviar: "<clau de text>"`: no s'envia mai, i aquesta és la raó (els auriculars, la clau de casa).
 *
 * Al moll de càrrega no hi ha estació: mentre l'Iri hi és, no li arriba res.
 */
import type { ActionResult, Narrative } from '@aventura/narrative-core';

export const TUB_TEXTS = [
  'tub.envia', 'tub.rep', 'tub.no_hi_cap', 'tub.no_cal', 'tub.moll',
  'tub.entrepa_ballester.rep', 'tub.entrepa_ballester.rep2', 'tub.clau_llibre.rep', 'tub.auriculars', 'tub.auriculars_boto', 'tub.clau_casa',
];

/** Qui rep el que envia `who`. */
const altra = (n: Narrative, who: string) => n.content.manifest.protagonists.find((p) => p !== who)!;

export function enviarPelTub(n: Narrative, item: string): ActionResult {
  const who = n.world.activeProtagonist();
  const other = altra(n, who);
  const props = n.content.items[item]?.props ?? {};
  const player = (text: string, params?: Record<string, string>) => ({ who: 'player' as const, text, params });

  if (typeof props.no_enviar === 'string') return { lines: [player(props.no_enviar)] };
  if (props.cap_al_tub !== true) return { lines: [player('tub.no_hi_cap')] };
  const fins = typeof props.tub_fins === 'string' ? props.tub_fins : null;
  if (props.tub_per !== other || (fins && n.flag(fins))) return { lines: [player('tub.no_cal')] };
  if (other === 'iri' && !n.flag('iri_al_tercer')) return { lines: [player('tub.moll')] };

  n.apply([{ takeItem: item }, { giveItem: item, who: other }]);
  const objecte = n.t(`obj.${item}.amb_article`);
  const rep = n.i18n.has(`tub.${item}.rep`) ? `tub.${item}.rep` : 'tub.rep';
  const lines: NonNullable<ActionResult['lines']> = [
    { who: 'player', text: 'tub.envia', params: { objecte }, sound: 'tub_envia' },
    { who: other, text: rep, params: { objecte }, sound: 'tub_rep' },
  ];
  if (n.i18n.has(`tub.${item}.rep2`)) lines.push({ who, text: `tub.${item}.rep2` });
  return { lines };
}

export function installTub(n: Narrative) {
  n.registerAction('tub.enviar', ({ args }) => enviarPelTub(n, String(args.item ?? '')));
}
