/**
 * Canvis d'escena automàtics: quan es compleix una condició (després de qualsevol acció del jugador), una
 * sola vegada, unes línies i uns efectes. Serveix per als finals d'escena que no depenen d'una sola acció
 * (p. ex. l'Escena 2 s'acaba quan la Vet ha fet les revisions i ha parlat amb la Juana, en qualsevol ordre).
 *
 * Cada canvi es fa una vegada: el flag `trans_<id>` (declarat a state.json) el marca com a fet. Els efectes
 * poden moure les protagonistes (`situar`, `protagonista`, `anar`): es fan quan s'acaben de dir les línies.
 */
import type { Condition, Effect, Narrative, PlayerAction } from '@aventura/narrative-core';
import type { Linia } from './sincronia.js';

export interface Transicio {
  id: string;
  when: Condition;
  linies: Linia[];
  efectes: Effect[];
}

const escena = (n: number): Condition => ({ var: 'escena', op: '==', value: n });

export const TRANSICIONS: Transicio[] = [
  // Escena 2 → 3: l'Arenga salpa cap a Port Hallen, i la ràdio no funciona.
  {
    id: 'esc2',
    when: {
      all: [
        escena(2), { flag: 'juana_explica' }, { flag: 'revisio_capitana' },
        { var: 'revisions', op: '>=', value: 4 }, { var: 'pacient', op: '==', value: '' },
      ],
    },
    linies: [
      'esc.salpa1',
      { who: 'title', text: 'esc.falten22' },
      'esc.salpa2',
      { who: 'capitana', text: 'esc.salpa3' },
      { who: 'bastida', text: 'esc.salpa4' },
      { who: 'capitana', text: 'esc.salpa5' },
      // Una sola pantalla de títol: l'hora i que ara calen les dues.
      { who: 'title', text: 'esc.onze' },
    ],
    efectes: [
      { setVar: 'escena', value: 3 },
      { setVar: 'hores', value: 22 },
      { event: 'situar', args: { who: 'iri', room: 'sala_radio' } },
      { event: 'anar', args: { room: 'infermeria' } },
    ],
  },
];

export const ESCENES_TEXTS = TRANSICIONS.flatMap((t) => t.linies.map((l) => (typeof l === 'string' ? l : l.text)));

export function despresDAccioEscenes(n: Narrative, action: PlayerAction) {
  for (const t of TRANSICIONS) {
    const flag = `trans_${t.id}`;
    if (n.flag(flag) || !n.check(t.when)) continue;
    n.apply([{ setFlag: flag }, ...t.efectes]);
    return {
      lines: t.linies.map((l) => (typeof l === 'string' ? { who: 'narrator' as const, text: l } : { who: l.who, text: l.text })),
      // Un canvi d'escena acaba la conversa en curs (però no talla el que obre una interacció).
      endDialogue: action.kind === 'choice',
    };
  }
  return undefined;
}

export function installEscenes(n: Narrative) {
  n.onAfterAction((action) => despresDAccioEscenes(n, action));
}
