/**
 * Canvis d'escena automàtics: quan es compleix una condició (després de qualsevol acció del jugador, o en entrar a
 * una sala: un viatge canvia el planeta des de l'`onEnter` de la cinemàtica, i això no és cap acció), una sola
 * vegada, unes línies i uns efectes. Les transicions són a `transicions.json`, que escriu el contingut. Cada una es
 * fa una vegada: el flag `trans_<id>` la marca com a feta.
 */
import type { Condition, Effect, Narrative, PlayerAction } from '@aventura/narrative-core';
import DADES from './transicions.json' with { type: 'json' };
import type { Linia } from './sincronia.js';

export interface Transicio { id: string; when: Condition; linies: Linia[]; efectes: Effect[] }

export const TRANSICIONS = DADES as unknown as Transicio[];

export const ESCENES_TEXTS = TRANSICIONS.flatMap((t) => t.linies.map((l) => l.text));

function transicioPendent(n: Narrative) {
  for (const t of TRANSICIONS) {
    const flag = `trans_${t.id}`;
    if (n.flag(flag) || !n.check(t.when)) continue;
    n.apply([{ setFlag: flag }, ...t.efectes]);
    return t.linies.map((l) => ({ ...l }));
  }
  return undefined;
}

export function despresDAccioEscenes(n: Narrative, action: PlayerAction) {
  const lines = transicioPendent(n);
  return lines && { lines, endDialogue: action.kind === 'choice' };
}

export function installEscenes(n: Narrative) {
  n.onAfterAction((action) => despresDAccioEscenes(n, action));
  n.onEnterRoom(() => {
    const lines = transicioPendent(n);
    return lines && { lines };
  });
}
