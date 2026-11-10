/**
 * La sincronia per torns (regles a guio/guio.md, «Regles del món · 1»).
 *
 * Mentre un pas de sincronia està en marxa (el seu flag `actiu`), **cada acció** del jugador a les
 * sales del pas gasta un torn del rellotge: una interacció que fa alguna cosa o una opció de diàleg.
 * Mirar, caminar i obrir una conversa no en gasten; canviar de protagonista, tampoc.
 *
 * Quan el rellotge arriba a zero (o salta una alarma que ningú no ha tapat), es torna a començar el
 * pas: línies de gràcia i efectes de reinici. Mai no hi ha derrota.
 *
 * Lògica del joc, no del motor: l'estat és a `state.json` (es desa amb la partida), i els textos, als
 * locales. El contingut hi afegeix el que sigui propi de cada pas amb efectes normals (p. ex. una
 * resposta massa llarga resta un torn més: `addVar` sobre el rellotge).
 */
import type { Effect, Narrative, PlayerAction } from '@aventura/narrative-core';

export interface PasSincronia {
  /** Flag que diu que el pas està en marxa. */
  actiu: string;
  /** Sales on compten les accions. */
  sales: string[];
  /** Variable amb els torns que queden. */
  rellotge: string;
  /** Torns del pas (el valor del rellotge en començar i en reiniciar). */
  torns: number;
  /**
   * Una alarma que s'ha de tapar: mentre el `flag` és cert, cada torn resta 1 a `var`; si arriba a
   * zero, es reinicia el pas. El contingut l'encén (flag + var) i la tapa (flag a fals).
   */
  alarma?: { flag: string; var: string };
  /** Avisos del rellotge: quan queden aquests torns, la línia (amb `{torns}`). */
  avisos?: Record<number, string>;
  /** En reiniciar: línies (narrador) i efectes, a més de tornar el rellotge a `torns` i apagar l'alarma. */
  reinici: { linies: string[]; efectes: Effect[] };
}

/** Els passos de sincronia del joc. */
export const PASSOS: Record<string, PasSincronia> = {
  aeroport: {
    actiu: 'sync_aeroport',
    sales: ['aeroport_terminal', 'aeroport_personal', 'aeroport_oficina'],
    rellotge: 'cigarreta',
    torns: 12,
    alarma: { flag: 'alarma_porta', var: 'alarma' },
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
  },
};

/** Verbs que no gasten torn. */
const LLIURES = new Set(['look', 'walkTo', 'talkTo']);

export const SINCRONIA_TEXTS = [
  'sync.aeroport.queden', 'sync.aeroport.ultima', 'sync.aeroport.reinici1', 'sync.aeroport.reinici2', 'sync.aeroport.reinici3',
];

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

  const queden = Number(n.getVar(pas.rellotge) ?? pas.torns) - 1;
  n.apply({ setVar: pas.rellotge, value: queden });

  let alarmaEsgotada = false;
  if (pas.alarma && n.flag(pas.alarma.flag)) {
    const a = Number(n.getVar(pas.alarma.var) ?? 0) - 1;
    n.apply({ setVar: pas.alarma.var, value: a });
    alarmaEsgotada = a <= 0;
  }

  if (queden <= 0 || alarmaEsgotada) {
    n.apply([
      ...pas.reinici.efectes,
      { setVar: pas.rellotge, value: pas.torns },
      ...(pas.alarma ? [{ setFlag: pas.alarma.flag, value: false }, { setVar: pas.alarma.var, value: 0 }] as Effect[] : []),
    ]);
    return { lines: pas.reinici.linies.map((t) => narrador(t)), endDialogue: true };
  }
  const avis = pas.avisos?.[queden];
  return avis ? { lines: [narrador(avis, { torns: queden })] } : undefined;
}

export function installSincronia(n: Narrative) {
  n.onAfterAction((action) => despresDAccio(n, action));
}
