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
 *  - **els lots de la subhasta** (Escena 8): n'hi ha 12 i se'n remata 1 per torn. A cada vàlvula, el Magnat en
 *    remata uns quants més, corrent (`cuita`: 2, 3 o 4, segons com de prop de la ratlla vermella veu el preu). Les
 *    objeccions de l'Iri aturen el martell uns torns (`pausa`): el que s'hauria de rematar es menja primer la pausa,
 *    i mentrestant el lot de l'escenari (`lot`, de l'1 al 12) no canvia. A 0, es torna a començar el pas.
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
  /** Converses on una opció que no fa res (un moviment de la grua que no es pot fer) no gasta torn. */
  refusLliure?: string[];
  /**
   * Opcions que només gasten torn si encerten: l'opció (`<diàleg>.<opció>`) i el flag que posa quan toca. Una objecció
   * de l'Iri al lot que no és el del faristol («els peixos són més tard») no fa avançar la subhasta.
   */
  encerts?: Record<string, string>;
  reinici: { linies: Linia[]; efectes: Effect[] };
}

const num = (n: Narrative, v: string) => Number(n.getVar(v) ?? 0);
const TX = SINC as Record<string, TextosPas>;
const off = (flags: string[]): Effect[] => flags.map((f) => ({ setFlag: f, value: false }));
/** Els lots de la subhasta: del 1 (el subsòl de Terra-2) al 12 (els peixos d'Aqua). */
export const LOTS = 12;

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
    refusLliure: ['grua'],
    reinici: {
      linies: TX.colada!.reinici,
      efectes: [{ setVar: 'temperatura', value: 8 }, ...off(['manxa_oberta', 'metall_carregat', 'escoria_treta', 'colat', 'gresol_ple', 'gresol_brut']),
        { addVar: 'reinicis_colada', amount: 1 }],
    },
  },
  subhasta: {
    actiu: 'sync_subhasta',
    resolt: 'reserva_oberta',
    sales: ['palau_salo', 'palau_control'],
    torn(n) {
      // El torn i el que el Magnat corre (`cuita`) es mengen primer la pausa de l'Iri, i després els lots.
      let resta = 1 + num(n, 'cuita');
      const pausa = Math.min(num(n, 'pausa'), resta);
      resta -= pausa;
      const lots = num(n, 'lots') - resta;
      n.apply([{ setVar: 'cuita', value: 0 }, { setVar: 'pausa', value: num(n, 'pausa') - pausa },
        { setVar: 'lots', value: lots }, { setVar: 'lot', value: Math.min(LOTS, Math.max(1, LOTS + 1 - lots)) }]);
      return lots <= 0 && !n.flag('reserva_oberta');
    },
    avisos: { var: 'lots', linies: TX.subhasta!.avisos },
    encerts: { 'subhasta.c7788': 'objeccio_7788', 'subhasta.anima': 'objeccio_anima', 'subhasta.peixos': 'objeccio_peixos' },
    reinici: {
      linies: TX.subhasta!.reinici,
      efectes: [{ setVar: 'lots', value: LOTS }, { setVar: 'lot', value: 1 }, { setVar: 'pausa', value: 0 },
        { setVar: 'cuita', value: 0 }, { setVar: 'valvules', value: 0 }, { setVar: 'preu_aigua', value: 112 },
        { setVar: 'ordre_valvules', value: '' },
        ...off(['clau_t2', 'clau_aqua', 'clau_ferrum', 'obert_t2', 'obert_aqua', 'obert_ferrum', 'objeccio_7788',
          'objeccio_anima', 'objeccio_peixos']),
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
  if (pas.refusLliure?.includes(action.dialogue) && senseEfecte(n, action.dialogue, action.choice)) return false;
  const encert = pas.encerts?.[`${action.dialogue}.${action.choice}`];
  if (encert) return n.flag(encert);
  return !DIALEGS_LLIURES.has(action.dialogue) && action.choice !== 'adeu';
}

/** L'opció no canvia res: ni efectes ni acaba la conversa (la grua diu «Primer, amunt» i prou). */
function senseEfecte(n: Narrative, dialogue: string, choice: string) {
  const nodes = Object.values(n.content.dialogues[dialogue]?.nodes ?? {});
  const c = nodes.flatMap((nd) => nd.choices ?? []).find((x) => x.id === choice);
  return !!c && !c.effects?.length && !c.end;
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

/** Les vàlvules dels dipòsits de la subhasta (els flags `obert_<vàlvula>`). */
export const VALVULES = ['t2', 'ferrum', 'aqua'] as const;

/**
 * L'ordre en què s'han obert les vàlvules (`ordre_valvules`, p. ex. `"aqua_t2"`), que fa servir el gràfic del preu del
 * saló per dibuixar el camí que ha fet el preu: 47 és 102 → 47 (T2 i després Aqua) o 57 → 47 (Aqua i després T2). Es
 * treu dels flags `obert_*` després de cada acció: s'hi afegeixen les que s'acaben d'obrir, i se'n treuen les que un
 * reinici ha tornat a tancar.
 */
export function anotaOrdre(n: Narrative) {
  const abans = String(n.getVar('ordre_valvules') ?? '');
  const ordre = abans.split('_').filter((v) => (VALVULES as readonly string[]).includes(v) && n.flag(`obert_${v}`));
  for (const v of VALVULES) if (n.flag(`obert_${v}`) && !ordre.includes(v)) ordre.push(v);
  const ara = ordre.join('_');
  if (ara !== abans) n.apply({ setVar: 'ordre_valvules', value: ara });
}

export function installSincronia(n: Narrative) {
  n.onAfterAction((action) => {
    const r = despresDAccio(n, action);
    anotaOrdre(n);
    return r;
  });
}
