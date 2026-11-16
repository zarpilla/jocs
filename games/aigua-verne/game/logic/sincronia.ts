/**
 * La sincronia per torns (guio/guio.md, «Regles del món · 4»), com a Suma Zero i Ni un ou.
 *
 * Mentre un pas de sincronia està en marxa (el seu flag `actiu`), **cada acció** del jugador a les sales del pas
 * gasta un torn: una interacció que fa alguna cosa o una opció de diàleg. Mirar, caminar, obrir una conversa (i
 * deixar-la) i parlar pel comunicador no en gasten; canviar de protagonista, tampoc.
 *
 * Dos rellotges:
 *  - **la temperatura del forn** (Escena 4, la colada): comença a 8 i baixa 1 per torn; la manxa la fa pujar.
 *    A 0, el metall s'endureix i es torna a començar el pas.
 *  - **els lots de la subhasta** (Escena 8): en queden 9 i se'n remata 1 per torn (i un de més a cada vàlvula,
 *    que el Magnat corre). L'Iri en pot afegir allargant la subhasta. A 0, es torna a començar el pas.
 *
 * Els textos (avisos i reinicis) són a `sincronies.json`, que escriu el contingut.
 */
import type { Effect, Narrative, PlayerAction } from '@aventura/narrative-core';
import SINC from './sincronies.json' with { type: 'json' };

export interface Linia { who: string; text: string }

interface TextosPas { avisos: Record<string, Linia>; reinici: Linia[] }

export interface PasSincronia {
  actiu: string;
  /** El flag que diu que el pas ja està resolt: d'aquí en endavant, cap avís. */
  resolt: string;
  sales: string[];
  /** Què passa a cada torn. Torna cert si s'ha de tornar a començar el pas. */
  torn(n: Narrative): boolean;
  avisos: { var: string; linies: Record<string, Linia> };
  reinici: { linies: Linia[]; efectes: Effect[] };
}

const num = (n: Narrative, v: string) => Number(n.getVar(v) ?? 0);
const TX = SINC as Record<string, TextosPas>;
const off = (flags: string[]): Effect[] => flags.map((f) => ({ setFlag: f, value: false }));

export const PASSOS: Record<string, PasSincronia> = {
  colada: {
    actiu: 'sync_colada',
    resolt: 'claus_fetes',
    sales: ['fosa_forn', 'fosa_colada'],
    torn(n) {
      n.apply({ addVar: 'temperatura', amount: -1 });
      return num(n, 'temperatura') <= 0 && !n.flag('claus_fetes');
    },
    avisos: { var: 'temperatura', linies: TX.colada!.avisos },
    reinici: {
      linies: TX.colada!.reinici,
      efectes: [{ setVar: 'temperatura', value: 8 }, ...off(['manxa_oberta', 'metall_carregat', 'escoria_treta', 'colat']),
        { addVar: 'reinicis_colada', amount: 1 }],
    },
  },
  subhasta: {
    actiu: 'sync_subhasta',
    resolt: 'reserva_oberta',
    sales: ['palau_salo', 'palau_control'],
    torn(n) {
      n.apply({ addVar: 'lots', amount: -1 });
      return num(n, 'lots') <= 0 && !n.flag('reserva_oberta');
    },
    avisos: { var: 'lots', linies: TX.subhasta!.avisos },
    reinici: {
      linies: TX.subhasta!.reinici,
      efectes: [{ setVar: 'lots', value: 9 }, { setVar: 'valvules', value: 0 }, { setVar: 'preu_aigua', value: 112 },
        ...off(['clau_t2', 'clau_aqua', 'clau_ferrum', 'obert_t2', 'obert_aqua', 'obert_ferrum', 'oferta_feta',
          'contracte_llegit', 'cava_vessat', 'peixos_preguntat']),
        { addVar: 'reinicis_subhasta', amount: 1 }],
    },
  },
};

const LLIURES = new Set(['look', 'walkTo', 'talkTo']);
const DIALEGS_LLIURES = new Set(['comunicador', 'tauler']);

export const SINCRONIA_TEXTS = ['sync.titol', ...Object.values(TX).flatMap((p) => [...Object.values(p.avisos), ...p.reinici].map((l) => l.text))];

export function pasActiu(n: Narrative): PasSincronia | null {
  return Object.values(PASSOS).find((p) => n.flag(p.actiu)) ?? null;
}

function gastaTorn(n: Narrative, pas: PasSincronia, action: PlayerAction) {
  if (!action.room || !pas.sales.includes(action.room)) return false;
  if (action.kind === 'interaction') {
    if (LLIURES.has(action.verb)) return false;
    if (action.inert) return false;
    if (action.target.kind === 'item' && !action.item) return false;
    if (action.item) return true;
    // Obrir un menú (l'escenari de la subhasta) és com obrir una conversa: no gasta torn; en gasta l'opció triada.
    if (n.peek({ verb: action.verb, target: action.target, room: action.room })?.dialogue) return false;
    const thing = n.content.rooms[action.room]?.hotspots[action.target.id];
    return !thing?.interactions?.some((i) => i.goTo && !i.item);
  }
  return !DIALEGS_LLIURES.has(action.dialogue) && action.choice !== 'adeu';
}

/**
 * El valor del rellotge després de l'últim torn comptat. Una acció pot fer saltar el rellotge més d'un pas (a cada
 * vàlvula, el Magnat remata un lot de més), i l'avís no s'ha de perdre pel salt: surt si el rellotge ha passat per
 * sota de la seva marca des de l'últim torn.
 */
const darrer = new WeakMap<Narrative, { pas: string; valor: number }>();

export function despresDAccio(n: Narrative, action: PlayerAction) {
  const pas = pasActiu(n);
  if (!pas || !gastaTorn(n, pas, action)) return;
  const prev = darrer.get(n);
  const abans = Math.max(prev?.pas === pas.actiu ? prev.valor : -Infinity, num(n, pas.avisos.var));
  if (pas.torn(n)) {
    n.apply(pas.reinici.efectes);
    darrer.delete(n);
    return { lines: pas.reinici.linies.map((l) => ({ ...l })), endDialogue: true };
  }
  const ara = num(n, pas.avisos.var);
  darrer.set(n, { pas: pas.actiu, valor: ara });
  if (n.flag(pas.resolt)) return;
  // La marca més baixa que s'ha travessat (si se n'han saltat dues, la més urgent).
  const marques = Object.keys(pas.avisos.linies).map(Number).filter((k) => k >= ara && k < abans).sort((a, b) => a - b);
  const avis = marques.length ? pas.avisos.linies[String(marques[0])] : undefined;
  return avis ? { lines: [{ ...avis }] } : undefined;
}

export function installSincronia(n: Narrative) {
  n.onAfterAction((action) => despresDAccio(n, action));
}
