/**
 * La sincronia per torns (regles a guio/guio.md, «Regles del món · 1»).
 *
 * Mentre un pas de sincronia està en marxa (el seu flag `actiu`), **cada acció** del jugador a les
 * sales del pas gasta un torn del rellotge: una interacció que fa alguna cosa o una opció de diàleg.
 * Mirar, caminar i obrir una conversa no en gasten; canviar de protagonista, tampoc.
 *
 * Quan el rellotge arriba a zero (o salta una alarma que ningú no ha tapat, o una variable arriba al seu
 * límit, com la sospita d'en Ballester), es torna a començar el pas: línies de gràcia i efectes de
 * reinici. Mai no hi ha derrota.
 *
 * Lògica del joc, no del motor: l'estat és a `state.json` (es desa amb la partida), i els textos, als
 * locales. El contingut hi afegeix el que sigui propi de cada pas amb efectes normals (p. ex. una
 * resposta massa llarga resta un torn més: `addVar` sobre el rellotge).
 */
import type { Condition, Effect, Narrative, PlayerAction } from '@aventura/narrative-core';

export interface PasSincronia {
  /** Flag que diu que el pas està en marxa. */
  actiu: string;
  /** Sales on compten les accions. */
  sales: string[];
  /** Variable amb els torns que queden (si el pas té rellotge). */
  rellotge?: string;
  /** Torns del pas (el valor del rellotge en començar i en reiniciar). */
  torns?: number;
  /** Un límit: quan la variable arriba al màxim, es reinicia el pas (la sospita d'en Ballester). */
  limit?: { var: string; max: number };
  /**
   * Una alarma que s'ha de tapar: mentre el `flag` és cert, cada torn resta 1 a `var`; si arriba a
   * zero, es reinicia el pas. El contingut l'encén (flag + var) i la tapa (flag a fals).
   */
  alarma?: { flag: string; var: string; /** Si el reinici ve de l'alarma: aquestes línies en lloc de les del reinici. */ linies?: Linia[] };
  /** Avisos del rellotge: quan queden aquests torns, la línia (amb `{torns}`). */
  avisos?: Record<number, string>;
  /**
   * Una regla pròpia de cada torn (el Director que mira el mòbil): es crida després de cada acció que gasta
   * torn i, si torna cert, es reinicia el pas amb les línies de la regla en lloc de les del rellotge.
   */
  regla?: { torn: (n: Narrative) => boolean; linies: Linia[] };
  /** En reiniciar: línies i efectes, a més de tornar el rellotge a `torns` i apagar l'alarma. */
  reinici: { linies: Linia[]; efectes: Effect[] };
  /**
   * Línies del reinici (del rellotge o de l'alarma) que només es diuen si es compleix la condició, just abans de
   * l'última: on s'ha quedat cadascuna quan tot torna a començar.
   */
  liniesSi?: { si: Condition; linia: Linia }[];
}

/** Una línia de reinici: una clau (la diu el narrador) o qui la diu i la clau. */
export type Linia = string | { who: string; text: string };

/** Els passos de sincronia del joc. */
export const PASSOS: Record<string, PasSincronia> = {
  aeroport: {
    actiu: 'sync_aeroport',
    sales: ['aeroport_terminal', 'aeroport_personal', 'aeroport_oficina'],
    rellotge: 'cigarreta',
    torns: 12,
    alarma: {
      flag: 'alarma_porta',
      var: 'alarma',
      linies: ['sync.aeroport.xiulet_reinici1', 'sync.aeroport.reinici2', 'sync.aeroport.reinici3'],
    },
    avisos: { 6: 'sync.aeroport.queden', 3: 'sync.aeroport.queden', 1: 'sync.aeroport.ultima' },
    reinici: {
      linies: ['sync.aeroport.reinici1', 'sync.aeroport.reinici2', 'sync.aeroport.reinici3'],
      efectes: [
        { setFlag: 'sync_aeroport', value: false },
        { setFlag: 'soler_distret', value: false },
        { setFlag: 'imprimint', value: false },
        { setFlag: 'acreditacions_llestes', value: false },
        { addVar: 'reinicis_aeroport', amount: 1 },
      ],
    },
    // Si l'Iri ja era a l'oficina, s'hi queda: el vigilant torna a ser a l'altra banda de la porta.
    liniesSi: [{ si: { inRoom: 'aeroport_oficina', who: 'iri' }, linia: 'sync.aeroport.reinici_oficina' }],
  },
  // L'Escena 8: el mòbil del Director. Quan l'Iri ja ha demanat el codi, al final de cada torn en què el
  // Director no està distret, mira el mòbil i cancel·la l'aturada (per protocol). Si la senyora Pons o en
  // Ballester se n'encarreguen (`mobil_resolt`), ja no el pot mirar.
  mobil: {
    actiu: 'sync_mobil',
    sales: ['bcmu_escombraries', 'bcmu_despatx'],
    rellotge: 'torns_mobil',
    torns: 9,
    avisos: { 3: 'sync.mobil.queden', 1: 'sync.mobil.ultima' },
    regla: {
      torn: (n) => {
        if (n.flag('mobil_resolt')) return false;
        const coberta = Number(n.getVar('coberta_mobil') ?? 0);
        if (n.flag('codi_demanat') && coberta <= 0) return true;
        if (coberta > 0) n.apply({ setVar: 'coberta_mobil', value: coberta - 1 });
        return false;
      },
      linies: [
        'sync.mobil.mira1',
        { who: 'bonfill', text: 'sync.mobil.mira2' },
        { who: 'vet', text: 'sync.mobil.mira3' },
        { who: 'bonfill', text: 'sync.mobil.mira4' },
        'sync.mobil.caducat',
      ],
    },
    reinici: {
      linies: [{ who: 'bonfill', text: 'sync.mobil.reinici1' }, 'sync.mobil.caducat'],
      efectes: [
        ...['codi_demanat', 'codi_llegit', 'reunio1', 'reunio2', 'gos_preguntat'].map((f) => ({ setFlag: f, value: false })),
        { setVar: 'coberta_mobil', value: 0 },
        { addVar: 'codi_n', amount: 1 },
        { addVar: 'reinicis_mobil', amount: 1 },
      ],
    },
  },
  // L'Escena 6: no hi ha rellotge, sinó la sospita d'en Ballester. A la tercera, tot torna a començar
  // pel primer codi, i totes les eines de la Vet tornen (cantar, els acudits, el got, la sèrie).
  collaret: {
    actiu: 'sync_collaret',
    sales: ['bcmu_escombraries', 'bcmu_seguretat'],
    limit: { var: 'sospita_ballester', max: 3 },
    reinici: {
      linies: ['sync.collaret.reinici1', 'sync.collaret.reinici2', 'sync.collaret.reinici3'],
      efectes: [
        { setVar: 'sospita_ballester', value: 0 },
        { setVar: 'codis', value: 0 },
        { setVar: 'coberta', value: 0 },
        ...['cantat', 'acudit1', 'acudit2', 'acudit3', 'violi_dit', 'vidua_dita', 'got_trencat'].map((f) => ({ setFlag: f, value: false })),
        { addVar: 'reinicis_collaret', amount: 1 },
      ],
    },
  },
};

/** Verbs que no gasten torn. */
const LLIURES = new Set(['look', 'walkTo', 'talkTo']);

/** Objectes que, fets servir sols, només obren una conversa (l'auricular): no gasten torn amb cap verb. */
const DE_CONVERSA = new Set(['auriculars', 'auricular_boto']);

export const SINCRONIA_TEXTS = [
  'sync.aeroport.queden', 'sync.aeroport.ultima', 'sync.aeroport.reinici1', 'sync.aeroport.reinici2', 'sync.aeroport.reinici3',
  'sync.aeroport.xiulet_reinici1', 'sync.aeroport.reinici_oficina',
  'sync.collaret.reinici1', 'sync.collaret.reinici2', 'sync.collaret.reinici3',
  'sync.mobil.queden', 'sync.mobil.ultima', 'sync.mobil.mira1', 'sync.mobil.mira2', 'sync.mobil.mira3', 'sync.mobil.mira4',
  'sync.mobil.caducat', 'sync.mobil.reinici1',
];

const linia = (l: Linia) => (typeof l === 'string' ? narrador(l) : { who: l.who, text: l.text });

const narrador = (text: string, params?: Record<string, string | number>) => ({ who: 'narrator' as const, text, params });

/** El pas de sincronia en marxa (si n'hi ha cap). */
export function pasActiu(n: Narrative): PasSincronia | null {
  return Object.values(PASSOS).find((p) => n.flag(p.actiu)) ?? null;
}

/** Què ha de passar després d'una acció: torn gastat, avís, o reinici. Exportada per als tests. */
export function despresDAccio(n: Narrative, action: PlayerAction) {
  const pas = pasActiu(n);
  if (!pas) return;
  if (!action.room || !pas.sales.includes(action.room)) return;
  if (action.kind === 'interaction' && LLIURES.has(action.verb)) return;
  if (action.kind === 'interaction' && !action.item && action.target.kind === 'item' && DE_CONVERSA.has(action.target.id)) return;

  let queden = Infinity;
  if (pas.rellotge) {
    queden = Number(n.getVar(pas.rellotge) ?? pas.torns) - 1;
    n.apply({ setVar: pas.rellotge, value: queden });
  }

  let alarmaEsgotada = false;
  if (pas.alarma && n.flag(pas.alarma.flag)) {
    const a = Number(n.getVar(pas.alarma.var) ?? 0) - 1;
    n.apply({ setVar: pas.alarma.var, value: a });
    alarmaEsgotada = a <= 0;
  }
  const limitAssolit = !!pas.limit && Number(n.getVar(pas.limit.var) ?? 0) >= pas.limit.max;
  const reglaTrencada = !!pas.regla && pas.regla.torn(n);

  if (queden <= 0 || alarmaEsgotada || limitAssolit || reglaTrencada) {
    n.apply([
      ...pas.reinici.efectes,
      ...(pas.rellotge ? [{ setVar: pas.rellotge, value: pas.torns ?? 0 }] as Effect[] : []),
      ...(pas.alarma ? [{ setFlag: pas.alarma.flag, value: false }, { setVar: pas.alarma.var, value: 0 }] as Effect[] : []),
    ]);
    let linies = reglaTrencada ? pas.regla!.linies
      : alarmaEsgotada && pas.alarma?.linies ? pas.alarma.linies
      : pas.reinici.linies;
    const extra = reglaTrencada ? [] : (pas.liniesSi ?? []).filter((l) => n.check(l.si)).map((l) => l.linia);
    if (extra.length) linies = [...linies.slice(0, -1), ...extra, ...linies.slice(-1)];
    return { lines: linies.map(linia), endDialogue: true };
  }
  const avis = pas.avisos?.[queden];
  return avis ? { lines: [narrador(avis, { torns: queden })] } : undefined;
}

export function installSincronia(n: Narrative) {
  n.onAfterAction((action) => despresDAccio(n, action));
}
