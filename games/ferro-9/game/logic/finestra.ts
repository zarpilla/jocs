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
 *  - I només els que la història necessita a l'altra banda, i en el sentit que toca (`finestra: "vet"`
 *    o `"iri"`, qui l'envia; `true`, totes dues): així no es pot gastar una encesa per error.
 *  - Cada transferència gasta una encesa.
 *  - El ritual sencer (posar, armar, canviar, sincronitzar) només es fa una vegada: quan l'Iri
 *    rep el primer enviament fet a mà (la segona transferència; la primera és l'accident), deixa
 *    la cambra sincronitzada (flag `sincronia_automatica`). Des d'aleshores, posar un objecte a la
 *    cambra ho fa tot: l'envia, canvia de protagonista i l'objecte apareix a l'inventari de l'altra.
 *  - Però només si l'altra és a la seva cambra (`CAMBRES`). Si no hi és, a l'altra banda no hi ha ningú: el camp
 *    queda armat amb l'objecte a dins, i l'objecte li arriba quan hi entri.
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
  'finestra.rebuig.no_cal_iri', 'finestra.rebuig.no_cal_vet', 'finestra.rebuig.no_cal_vet_abans', 'finestra.rebuig.no_cal_iri_abans', 'finestra.rebuig.no_cal_iri_res', 'finestra.espera.iri', 'finestra.espera.vet', 'finestra.boto_automatic',
  ...frasesPerObjecte(),
];

/** Els objectes que envia cada protagonista (`finestra` a items.json): les seves frases de la cambra, una per objecte. */
function frasesPerObjecte() {
  const envia: Record<string, string[]> = {
    vet: ['nota_vet', 'nota_pany', 'nota_mida', 'pols_rovell', 'molla', 'nota_pressio', 'nota_massa', 'nota_vet_nom', 'mapa_fuga'],
    iri: ['imant_ferro9', 'nota_iri', 'tram_biga_1', 'tram_biga_2', 'tram_biga_3', 'nota_amagatall', 'diapaso', 'nota_iri_nom', 'tub_amb_llibreta'],
  };
  const claus = ['finestra.posat.nota_vet', 'finestra.rebut.clau_anglesa'];
  for (const [qui, items] of Object.entries(envia)) {
    for (const item of items) claus.push(`finestra.enviat.${item}`, `finestra.espera.${qui}.${item}`, `finestra.rebut.${item}`);
  }
  return claus;
}

/**
 * Les frases de posar, enviar, deixar en espera i rebre tenen una versió per a cada objecte que passa per la
 * finestra (`finestra.enviat.molla`), perquè es puguin gravar amb veu: res de `{objecte}`. Si un objecte no en té,
 * es diu la genèrica, que no l'anomena.
 */
function perObjecte(n: Narrative, base: string, item: string) {
  const k = `${base}.${item}`;
  return n.i18n.has(k) ? k : base;
}

/** La sala de la cambra de cada protagonista: a l'altra banda hi ha algú si hi és. */
export const CAMBRES: Record<string, string> = { iri: 'fabrica_cambra', vet: 'gavina_cella' };

const v = {
  automatica: 'sincronia_automatica',
  armada: 'finestra_armada',
  enceses: 'enceses_restants',
  transferencies: 'transferencies',
  objecte: (costat: string) => `finestra_objecte_${costat}`,
};

const line = (text: string, params?: Record<string, string | number>, sound?: string) => ({ who: 'player' as const, text, params, sound });

/** Sons de la cambra (`game/audio/sfx/`). */
export const SONS_FINESTRA = { posar: 'cambra_posa', armar: 'cambra_arma', fase: 'fase' };

export function estatFinestra(n: Narrative) {
  return {
    armada: String(n.getVar(v.armada) ?? ''),
    enceses: Number(n.getVar(v.enceses) ?? 0),
    objecte: (costat: string) => String(n.getVar(v.objecte(costat)) ?? ''),
  };
}

/** Si una protagonista (la que juga o l'altra) és ara mateix a la sala de la seva cambra. */
export function aLaCambra(n: Narrative, who: string): boolean {
  const room = who === n.world.activeProtagonist() ? n.world.currentRoom() : n.world.protagonistRoom?.(who) ?? null;
  return room !== null && room === CAMBRES[who];
}

/**
 * Sincronia: l'objecte de la cambra de qui ha armat arriba a `costat`. Gasta una encesa. La segona transferència
 * deixa la sincronia automàtica.
 */
function rebre(n: Narrative, costat: string) {
  const emissora = estatFinestra(n).armada;
  const item = estatFinestra(n).objecte(emissora);
  n.apply([
    { setVar: v.armada, value: '' },
    { setVar: v.objecte(emissora), value: '' },
    { addVar: v.enceses, amount: -1 },
    { addVar: v.transferencies, amount: 1 },
    ...(item ? [{ giveItem: item, who: costat }] : []),
    { event: 'finestra.transferencia', args: { de: emissora, a: costat, objecte: item } },
  ]);
  const lines = [line(item ? perObjecte(n, 'finestra.rebut', item) : 'finestra.rebut_res', undefined, SONS_FINESTRA.fase)];
  if (!n.flag(v.automatica) && Number(n.getVar(v.transferencies)) >= TRANSFERENCIES_RITUAL) {
    n.apply({ setFlag: v.automatica });
    lines.push(line('finestra.automatica'));
  }
  return lines;
}

/** Per què un objecte no pot passar (clau de text), o `null` si pot. `costat`: qui l'envia. */
export function motiuRebuig(n: Narrative, item: string, costat: string): string | null {
  const props = n.content.items[item]?.props ?? {};
  if (props.viu === true) return 'finestra.rebuig.viu';
  if (props.liquid === true) return 'finestra.rebuig.liquid';
  if (typeof props.pes !== 'number') return 'finestra.rebuig.no_hi_cap';
  if (props.pes >= PES_MAXIM) return 'finestra.rebuig.massa_pesat';
  if (props.finestra !== true && props.finestra !== costat) {
    // Abans de saber qui hi ha a l'altra banda, la Vet no pot parlar de «la I.»...
    if (costat === 'vet' && !n.flag('sap_que_es_temps')) return 'finestra.rebuig.no_cal_vet_abans';
    // I l'Iri no sap que hi ha algú fins que no llegeix la primera nota, ni que es diu «V.» fins al dibuix del pany.
    if (costat === 'iri' && !n.flag('nota_vet_llegida')) return 'finestra.rebuig.no_cal_iri_res';
    if (costat === 'iri' && !n.flag('iri_sap_pany')) return 'finestra.rebuig.no_cal_iri_abans';
    return `finestra.rebuig.no_cal_${costat}`;
  }
  return null;
}

export function installFinestra(n: Narrative) {
  /** Posar un objecte a la cambra de la protagonista activa. Args: `item`. */
  n.registerAction('finestra.posar', ({ args }): ActionResult => {
    const costat = n.world.activeProtagonist();
    const item = String(args.item ?? '');
    const estat = estatFinestra(n);
    if (estat.objecte(costat)) return { lines: [line('finestra.ple')] };
    if (estat.armada === costat) return { lines: [line('finestra.ja_armat')] };
    const rebuig = motiuRebuig(n, item, costat);
    if (rebuig) return { lines: [line(rebuig)] };
    if (n.flag(v.automatica)) {
      // Un sol pas: posar-lo ja és enviar-lo. Un camp armat buit (partides d'abans) no ha d'encallar res.
      if (estat.armada && !estat.objecte(estat.armada)) n.apply({ setVar: v.armada, value: '' });
      if (estatFinestra(n).armada) return { lines: [line('finestra.ja_armat')] };
      if (estat.enceses <= 0) return { lines: [line('finestra.esgotada')] };
      const altra = n.content.manifest.protagonists.find((p) => p !== costat)!;
      if (!aLaCambra(n, altra)) {
        // A l'altra banda no hi ha ningú: queda armat, i passarà quan hi entri (vegeu `onEnterRoom`, a sota).
        n.apply([{ takeItem: item, who: costat }, { setVar: v.objecte(costat), value: item }, { setVar: v.armada, value: costat }]);
        return { lines: [line(perObjecte(n, `finestra.espera.${costat}`, item), undefined, SONS_FINESTRA.armar)] };
      }
      n.apply([
        { takeItem: item, who: costat },
        { giveItem: item, who: altra },
        { addVar: v.enceses, amount: -1 },
        { addVar: v.transferencies, amount: 1 },
        { event: 'finestra.transferencia', args: { de: costat, a: altra, objecte: item } },
        { event: 'protagonista', args: { id: altra } },
      ]);
      return { lines: [line(perObjecte(n, 'finestra.enviat', item), undefined, SONS_FINESTRA.fase)] };
    }
    n.apply([{ takeItem: item, who: costat }, { setVar: v.objecte(costat), value: item }]);
    return { lines: [line(perObjecte(n, 'finestra.posat', item), undefined, SONS_FINESTRA.posar)] };
  });

  /** Treure l'objecte de la cambra (si no està armada). */
  n.registerAction('finestra.treure', (): ActionResult => {
    const costat = n.world.activeProtagonist();
    const estat = estatFinestra(n);
    const item = estat.objecte(costat);
    if (!item) return { lines: [line('finestra.buida')] };
    if (estat.armada === costat) return { lines: [line('finestra.tancada')] };
    n.apply([{ setVar: v.objecte(costat), value: '' }, { giveItem: item, who: costat }]);
    return { lines: [line('finestra.tret')] };
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
      // Amb la sincronia automàtica, armar el camp buit només encallaria el següent enviament.
      if (n.flag(v.automatica)) return { lines: [line('finestra.boto_automatic')] };
      if (estat.enceses <= 0) return { lines: [line('finestra.esgotada')] };
      n.apply({ setVar: v.armada, value: costat });
      return { lines: [line(estat.objecte(costat) ? 'finestra.armat' : 'finestra.armat_buit', undefined, SONS_FINESTRA.armar)] };
    }

    // Sincronia: l'objecte de la cambra de qui ha armat arriba aquí.
    return { lines: rebre(n, costat) };
  });

  /**
   * Amb la sincronia automàtica, el que l'altra ha deixat armat (perquè aquí no hi havia ningú) arriba en entrar a
   * la cambra. No si l'`onEnter` se l'emporta tot seguit a una altra sala (p. ex. l'Iri descoberta a l'Acte 3), ni
   * si el camp és buit: una encesa per rebre aire seria una trampa.
   */
  n.onEnterRoom((room): ActionResult | void => {
    const costat = n.world.activeProtagonist();
    const estat = estatFinestra(n);
    if (!n.flag(v.automatica) || CAMBRES[costat] !== room) return;
    if (!estat.armada || estat.armada === costat || !estat.objecte(estat.armada)) return;
    if (n.peekEnter(room)?.goTo) return;
    return { lines: rebre(n, costat) };
  });
}
