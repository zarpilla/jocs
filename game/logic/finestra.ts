/**
 * La finestra de fase (regles a guio/guio.md).
 *
 * Lògica del joc, no del motor: només fa servir el nucli narratiu. L'estat va
 * a variables de `state.json`, i per tant es desa amb la partida.
 *
 *  - Cada protagonista té la seva cambra. Qui ARMA el camp és qui envia.
 *  - L'altra el SINCRONITZA i rep l'objecte que hi hagi a la cambra de qui l'ha armat.
 *  - Un camp armat espera indefinidament la sincronia.
 *  - Només objectes de < 2 kg, inerts, no vius i no líquids (propietats a items.json).
 *  - Cada transferència gasta una encesa.
 *  - El ritual sencer (posar, armar, canviar, sincronitzar) només es fa una vegada: quan l'Iri
 *    rep el primer enviament fet a mà (la segona transferència; la primera és l'accident), deixa
 *    la cambra sincronitzada (flag `sincronia_automatica`). Des d'aleshores, posar un objecte a la
 *    cambra ho fa tot: l'envia, canvia de protagonista i l'objecte apareix a l'inventari de l'altra.
 */
import type { ActionResult, Narrative } from '@aventura/narrative-core';

export const PES_MAXIM = 2;
/** Transferències fetes amb el ritual sencer abans que la sincronia sigui automàtica. */
export const TRANSFERENCIES_RITUAL = 2;

/** Textos que fa servir aquest mòdul (el validador comprova que existeixin). */
export const FINESTRA_TEXTS = [
  'finestra.posat', 'finestra.ple', 'finestra.ja_armat', 'finestra.tancada', 'finestra.buida', 'finestra.tret',
  'finestra.armat', 'finestra.armat_buit', 'finestra.esgotada', 'finestra.rebut', 'finestra.rebut_res',
  'finestra.enviat', 'finestra.automatica', 'finestra.rebuig.massa_pesat', 'finestra.rebuig.viu', 'finestra.rebuig.liquid', 'finestra.rebuig.no_hi_cap',
];

const v = {
  automatica: 'sincronia_automatica',
  armada: 'finestra_armada',
  enceses: 'enceses_restants',
  transferencies: 'transferencies',
  objecte: (costat: string) => `finestra_objecte_${costat}`,
};

const line = (text: string, params?: Record<string, string | number>) => ({ who: 'player' as const, text, params });

export function estatFinestra(n: Narrative) {
  return {
    armada: String(n.getVar(v.armada) ?? ''),
    enceses: Number(n.getVar(v.enceses) ?? 0),
    objecte: (costat: string) => String(n.getVar(v.objecte(costat)) ?? ''),
  };
}

/** Per què un objecte no pot passar (clau de text), o `null` si pot. */
export function motiuRebuig(n: Narrative, item: string): string | null {
  const props = n.content.items[item]?.props ?? {};
  if (props.viu === true) return 'finestra.rebuig.viu';
  if (props.liquid === true) return 'finestra.rebuig.liquid';
  if (typeof props.pes !== 'number') return 'finestra.rebuig.no_hi_cap';
  if (props.pes >= PES_MAXIM) return 'finestra.rebuig.massa_pesat';
  return null;
}

export function installFinestra(n: Narrative) {
  /** Posar un objecte a la cambra de la protagonista activa. Args: `item`. */
  n.registerAction('finestra.posar', ({ args }): ActionResult => {
    const costat = n.world.activeProtagonist();
    const item = String(args.item ?? '');
    const estat = estatFinestra(n);
    if (estat.objecte(costat)) return { lines: [line('finestra.ple', { objecte: n.itemName(estat.objecte(costat)) })] };
    if (estat.armada === costat) return { lines: [line('finestra.ja_armat')] };
    const rebuig = motiuRebuig(n, item);
    if (rebuig) return { lines: [line(rebuig, { objecte: n.itemName(item) })] };
    if (n.flag(v.automatica)) {
      // Un sol pas: posar-lo ja és enviar-lo.
      if (estat.armada) return { lines: [line('finestra.ja_armat')] };
      if (estat.enceses <= 0) return { lines: [line('finestra.esgotada')] };
      const altra = n.content.manifest.protagonists.find((p) => p !== costat)!;
      n.apply([
        { takeItem: item, who: costat },
        { giveItem: item, who: altra },
        { addVar: v.enceses, amount: -1 },
        { addVar: v.transferencies, amount: 1 },
        { event: 'finestra.transferencia', args: { de: costat, a: altra, objecte: item } },
        { event: 'protagonista', args: { id: altra } },
      ]);
      return { lines: [line('finestra.enviat', { objecte: n.itemName(item) })] };
    }
    n.apply([{ takeItem: item, who: costat }, { setVar: v.objecte(costat), value: item }]);
    return { lines: [line('finestra.posat', { objecte: n.itemName(item) })] };
  });

  /** Treure l'objecte de la cambra (si no està armada). */
  n.registerAction('finestra.treure', (): ActionResult => {
    const costat = n.world.activeProtagonist();
    const estat = estatFinestra(n);
    const item = estat.objecte(costat);
    if (!item) return { lines: [line('finestra.buida')] };
    if (estat.armada === costat) return { lines: [line('finestra.tancada')] };
    n.apply([{ setVar: v.objecte(costat), value: '' }, { giveItem: item, who: costat }]);
    return { lines: [line('finestra.tret', { objecte: n.itemName(item) })] };
  });

  /**
   * El botó (o el cop de puny, o la palanca): arma si ningú no ho ha fet;
   * sincronitza si l'altra ja ha armat.
   */
  n.registerAction('finestra.boto', (): ActionResult => {
    const costat = n.world.activeProtagonist();
    const estat = estatFinestra(n);

    if (estat.armada === costat) return { lines: [line('finestra.ja_armat')] };

    if (!estat.armada) {
      if (estat.enceses <= 0) return { lines: [line('finestra.esgotada')] };
      n.apply({ setVar: v.armada, value: costat });
      return { lines: [line(estat.objecte(costat) ? 'finestra.armat' : 'finestra.armat_buit')] };
    }

    // Sincronia: l'objecte de la cambra de qui ha armat arriba aquí.
    const emissora = estat.armada;
    const item = estat.objecte(emissora);
    n.apply([
      { setVar: v.armada, value: '' },
      { setVar: v.objecte(emissora), value: '' },
      { addVar: v.enceses, amount: -1 },
      { addVar: v.transferencies, amount: 1 },
      ...(item ? [{ giveItem: item, who: costat }] : []),
      { event: 'finestra.transferencia', args: { de: emissora, a: costat, objecte: item } },
    ]);
    const lines = [line(item ? 'finestra.rebut' : 'finestra.rebut_res', { objecte: item ? n.itemName(item) : '' })];
    if (!n.flag(v.automatica) && Number(n.getVar(v.transferencies)) >= TRANSFERENCIES_RITUAL) {
      n.apply({ setFlag: v.automatica });
      lines.push(line('finestra.automatica'));
    }
    return { lines };
  });
}
