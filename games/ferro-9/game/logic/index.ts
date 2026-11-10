/**
 * Lògica pròpia d'aquest joc, independent del motor gràfic. Qualsevol
 * adaptador (Benne o un altre) la instal·la sobre el `Narrative`.
 */
import type { GameContent, Narrative } from '@aventura/narrative-core';
import { FINESTRA_TEXTS, installFinestra } from './finestra.js';

export * from './finestra.js';

/** Totes les accions que el contingut pot fer servir (`"action": { "name": ... }`). */
export const GAME_ACTIONS = ['finestra.posar', 'finestra.treure', 'finestra.boto'];

/** Claus de text que fa servir el codi del joc. */
export const GAME_TEXT_KEYS = [...FINESTRA_TEXTS];

/** Les de `GAME_TEXT_KEYS` més les que depenen del contingut: el nom amb article de cada objecte. */
export function gameTextKeys(content: GameContent) {
  return [...GAME_TEXT_KEYS, ...Object.keys(content.items).map((id) => `obj.${id}.amb_article`)];
}

export function installGameLogic(n: Narrative) {
  installFinestra(n);
}
