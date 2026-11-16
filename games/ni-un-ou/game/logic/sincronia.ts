/**
 * La sincronia per torns (guio/guio.md, «Regles del món · 1»), com a Suma Zero.
 *
 * Mentre un pas de sincronia està en marxa (el seu flag `actiu`), **cada acció** del jugador a les sales del
 * pas gasta un torn: una interacció que fa alguna cosa o una opció de diàleg. Mirar, caminar, obrir una
 * conversa (i deixar-la) i parlar pel walkie o pel tub no en gasten; canviar de protagonista, tampoc.
 *
 * Dos rellotges:
 *  - **la paciència d'en Bastida** (Escena 3): puja 1 a cada torn que no cobreix una distracció de la Vet. Una
 *    distracció (`coberta_nova`) no es cobreix a si mateixa: cobreix els torns següents. A 6, es torna a
 *    començar el pas.
 *  - **el senyal del satèl·lit** (Escena 9): 12 torns. A 0, el satèl·lit se'n va i es torna a començar el pas.
 *
 * Mai no hi ha derrota: el reinici té línies de gràcia, i el que s'ha après es recorda. L'estat és a
 * `state.json` (es desa amb la partida) i els textos, als locales.
 */
import type { Effect, Narrative, PlayerAction } from '@aventura/narrative-core';

/** Una línia: una clau (la diu el narrador) o qui la diu i la clau. */
export type Linia = string | { who: string; text: string };

export interface PasSincronia {
  /** Flag que diu que el pas està en marxa. */
  actiu: string;
  /** Sales on compten les accions. */
  sales: string[];
  /** Què passa a cada torn. Torna cert si s'ha de tornar a començar el pas. */
  torn(n: Narrative): boolean;
  /** Si el pas ja s'ha resolt (la ràdio parla, les dades han sortit): llavors cap acció no gasta torn. */
  resolt(n: Narrative): boolean;
  /** Avisos: després d'un torn, si `var` val una d'aquestes xifres (i ha canviat), la línia. */
  avisos?: { var: string; linies: Record<number, Linia> };
  /** En reiniciar: línies i efectes. */
  reinici: { linies: Linia[]; efectes: Effect[] };
}

const num = (n: Narrative, v: string) => Number(n.getVar(v) ?? 0);

/** Els passos de sincronia del joc. */
export const PASSOS: Record<string, PasSincronia> = {
  // Escena 3: l'Iri arregla la ràdio mentre la Vet entreté en Bastida a la infermeria.
  radio: {
    actiu: 'sync_radio',
    sales: ['infermeria', 'sala_radio', 'pallol'],
    torn(n) {
      const coberta = num(n, 'coberta');
      if (coberta > 0) n.apply({ setVar: 'coberta', value: coberta - 1 });
      else n.apply({ addVar: 'paciencia', amount: 1 });
      const nova = num(n, 'coberta_nova');
      // Una distracció nova se suma al que quedava de l'anterior.
      if (nova > 0) n.apply([{ addVar: 'coberta', amount: nova }, { setVar: 'coberta_nova', value: 0 }]);
      return num(n, 'paciencia') >= 6;
    },
    resolt: (n) => n.flag('radio_feta'),
    avisos: {
      var: 'paciencia',
      linies: { 3: 'sync.radio.paciencia3', 4: 'sync.radio.paciencia4', 5: 'sync.radio.paciencia5' },
    },
    reinici: {
      linies: [
        { who: 'bastida', text: 'sync.radio.reinici1' },
        { who: 'vet', text: 'sync.radio.reinici2' },
        'sync.radio.reinici3',
      ],
      efectes: [
        { setVar: 'paciencia', value: 0 },
        { setVar: 'coberta', value: 0 },
        { setVar: 'coberta_nova', value: 0 },
        { setVar: 'empalmat', value: 0 },
        ...['panell_obert', 'eina_temporal', 'eina_tensio', 'eina_mans', 'radio_feta'].map((f) => ({ setFlag: f, value: false })),
        { addVar: 'reinicis_radio', amount: 1 },
      ],
    },
  },
  // Escena 9: l'Iri envia les dades des del pont mentre la Vet convenç en Bastida de tornar el relé.
  satellit: {
    actiu: 'sync_satellit',
    sales: ['pont', 'pal', 'sala_maquines'],
    torn(n) {
      n.apply({ addVar: 'senyal', amount: -1 });
      return num(n, 'senyal') <= 0 && !n.flag('enviat');
    },
    resolt: (n) => n.flag('enviat'),
    avisos: {
      var: 'senyal',
      linies: { 6: 'sync.satellit.queden6', 3: 'sync.satellit.queden3', 1: 'sync.satellit.queden1' },
    },
    reinici: {
      linies: [
        { who: 'iri', text: 'sync.satellit.reinici1' },
        { who: 'vet', text: 'sync.satellit.reinici2' },
        'sync.satellit.reinici3',
      ],
      efectes: [
        { setVar: 'senyal', value: 12 },
        { setVar: 'paquets', value: 0 },
        { setVar: 'sai', value: 2 },
        { setFlag: 'enviament_iniciat', value: false },
        { setFlag: 'enviat', value: false },
        ...['dubte_veritat', 'dubte_iri', 'dubte_cafe', 'dubte_arengades', 'dubte_mentida', 'dubte_diners'].map((f) => ({ setFlag: f, value: false })),
        { addVar: 'reinicis_satellit', amount: 1 },
      ],
    },
  },
};

/** Verbs que no gasten torn. */
const LLIURES = new Set(['look', 'walkTo', 'talkTo']);
/** Les boques del tub de veu (i el passaplats, que la deixa sentir des del menjador). */
const TUB = new Set(['boca', 'passaplats']);
/** Diàlegs que no gasten torn: parlar pel walkie o pel tub. */
const DIALEGS_LLIURES = new Set(['walkie', 'tub']);

export const SINCRONIA_TEXTS = [
  'sync.radio.paciencia3', 'sync.radio.paciencia4', 'sync.radio.paciencia5',
  'sync.radio.reinici1', 'sync.radio.reinici2', 'sync.radio.reinici3',
  'sync.satellit.queden6', 'sync.satellit.queden3', 'sync.satellit.queden1',
  'sync.satellit.reinici1', 'sync.satellit.reinici2', 'sync.satellit.reinici3',
];

const linia = (l: Linia) => (typeof l === 'string' ? { who: 'narrator' as const, text: l } : { who: l.who, text: l.text });

/** El pas de sincronia en marxa (si n'hi ha cap). */
export function pasActiu(n: Narrative): PasSincronia | null {
  return Object.values(PASSOS).find((p) => n.flag(p.actiu)) ?? null;
}

/** Si una acció gasta torn. */
function gastaTorn(n: Narrative, pas: PasSincronia, action: PlayerAction) {
  if (!action.room || !pas.sales.includes(action.room)) return false;
  if (action.kind === 'interaction') {
    if (LLIURES.has(action.verb)) return false;
    // Una resposta que no fa res («Encara no», «Morta») no és una acció.
    if (action.inert) return false;
    // Fer servir el walkie o el quadern (objectes de l'inventari, sense res més) i parlar pel tub no són accions.
    if (action.target.kind === 'item' && !action.item) return false;
    if (TUB.has(action.target.id)) return false;
    // Les portes són caminar: anar d'una sala a l'altra no gasta torn.
    const thing = n.content.rooms[action.room]?.hotspots[action.target.id];
    return !!action.item || !thing?.interactions?.some((i) => i.goTo && !i.item);
  }
  // Deixar la conversa («adeu») tampoc no és cap acció.
  return !DIALEGS_LLIURES.has(action.dialogue) && action.choice !== 'adeu';
}

/** Què ha de passar després d'una acció: torn gastat, avís, o reinici. Exportada per als tests. */
export function despresDAccio(n: Narrative, action: PlayerAction) {
  const pas = pasActiu(n);
  if (!pas || !gastaTorn(n, pas, action)) return;
  // L'acció que acaba de resoldre el pas (la ràdio ja parla) no el pot reiniciar: un cop resolt, ja no compta res.
  if (pas.resolt(n)) return;
  const abans = pas.avisos ? num(n, pas.avisos.var) : 0;
  if (pas.torn(n)) {
    n.apply(pas.reinici.efectes);
    // Satèl·lit: el dubte d'en Bastida torna a 5, o es queda on era si era més baix.
    if (pas === PASSOS.satellit && num(n, 'dubte') > 5) n.apply({ setVar: 'dubte', value: 5 });
    return { lines: pas.reinici.linies.map(linia), endDialogue: true };
  }
  if (!pas.avisos) return;
  const ara = num(n, pas.avisos.var);
  const avis = ara !== abans ? pas.avisos.linies[ara] : undefined;
  return avis ? { lines: [linia(avis)] } : undefined;
}

export function installSincronia(n: Narrative) {
  n.onAfterAction((action) => despresDAccio(n, action));
}
