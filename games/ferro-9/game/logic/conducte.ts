/**
 * El conducte de servei (guio/guio.md, Acte 3, «La ruta del conducte»).
 *
 * Lògica del joc, no del motor: només fa servir el nucli narratiu, i l'estat va a variables de
 * `state.json` (es desa amb la partida).
 *
 *  - La ruta són cinc signes (← esquerra, ↑ recte, → dreta), triats a l'atzar una vegada per partida.
 *    Es guarden com a signes (`ruta_conducte`, p. ex. «↑ → ← ← ↑»), que no són text de cap idioma: així els
 *    textos els poden mostrar amb `{ruta_conducte}`.
 *  - La Vet els troba al mapa de la Sala de la Memòria i els copia al fullet que envia a l'Iri.
 *  - L'Iri entra al conducte i, a cada revolt (`fabrica_conducte`), tria per on va. Entre revolt i revolt
 *    passa per `fabrica_conducte_revolt`, que decideix on surt: al revolt següent, al moll (els cinc encertats)
 *    o, si se n'ha equivocat algun, per la mateixa reixa per on ha entrat («m'he perdut»).
 *  - No es diu mai quin revolt s'ha fallat: només, al final, que no s'ha arribat enlloc.
 */
import type { Narrative } from '@aventura/narrative-core';

/** Quants revolts té el conducte (i quants signes té la ruta). */
export const REVOLTS = 5;

/** Els signes de cada direcció. */
export const SIGNES = { esquerra: '←', recte: '↑', dreta: '→' } as const;
export type Direccio = keyof typeof SIGNES;
const DIRECCIONS = Object.keys(SIGNES) as Direccio[];

export const CONDUCTE_VARS = {
  /** La ruta bona, en signes separats per espais. Buida fins que es tria. */
  ruta: 'ruta_conducte',
  /** Quants revolts ha passat l'Iri en aquest intent (0–5). */
  pas: 'conducte_pas',
  /** Quants n'ha fallat en aquest intent. */
  errades: 'conducte_errades',
  /**
   * El revolt que es veu (0–4): el detall que canvia d'un revolt a l'altre. Va a part de `pas` perquè no
   * canviï fins que s'arriba al revolt següent (si no, el detall canviaria abans del fos).
   */
  vista: 'conducte_vista',
};

/** Una ruta nova a l'atzar: cinc direccions. */
export function novaRuta(random: () => number = Math.random): Direccio[] {
  return Array.from({ length: REVOLTS }, () => DIRECCIONS[Math.floor(random() * DIRECCIONS.length)]!);
}

/** La ruta de la partida com a direccions (buida si encara no s'ha triat). */
export function rutaConducte(n: Narrative): Direccio[] {
  const text = String(n.getVar(CONDUCTE_VARS.ruta) ?? '');
  return text.split(' ').map((s) => DIRECCIONS.find((d) => SIGNES[d] === s)).filter((d): d is Direccio => !!d);
}

/** Tria la ruta si encara no n'hi ha (també per a les partides desades d'abans que existís). */
export function asseguraRuta(n: Narrative) {
  if (rutaConducte(n).length === REVOLTS) return;
  n.apply({ setVar: CONDUCTE_VARS.ruta, value: novaRuta().map((d) => SIGNES[d]).join(' ') });
}

export function installConducte(n: Narrative) {
  // La ruta existeix des del primer moment de la partida (i de les partides desades d'abans que existís): cada
  // canvi d'estat, també el d'una partida nova o carregada, la tria si encara no n'hi ha.
  n.on((e) => {
    if (e.type === 'stateChanged') asseguraRuta(n);
  });

  /** L'Iri tria per on va en un revolt. Args: `dir` (`esquerra`, `recte`, `dreta`). */
  n.registerAction('conducte.tria', ({ args }) => {
    asseguraRuta(n);
    const pas = Number(n.getVar(CONDUCTE_VARS.pas) ?? 0);
    const bona = rutaConducte(n)[pas];
    n.apply([
      { setVar: CONDUCTE_VARS.pas, value: pas + 1 },
      ...(args.dir === bona ? [] : [{ addVar: CONDUCTE_VARS.errades, amount: 1 }]),
    ]);
  });

  /** En arribar al revolt següent: el detall que es veu passa a ser el d'aquest revolt. */
  n.registerAction('conducte.revolt', () => {
    n.apply({ setVar: CONDUCTE_VARS.vista, value: Number(n.getVar(CONDUCTE_VARS.pas) ?? 0) });
  });
}
