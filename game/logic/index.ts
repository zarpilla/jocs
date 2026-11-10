/**
 * Lògica pròpia d'aquest joc, independent del motor gràfic. Qualsevol
 * adaptador (Benne o un altre) la instal·la sobre el `Narrative`.
 *
 * Les regles de Suma Zero (p. ex. la sincronització per torns) s'hi afegeixen com a mòduls a part.
 */
import type { GameContent, Narrative } from '@aventura/narrative-core';

/** Totes les accions que el contingut pot fer servir (`"action": { "name": ... }`). */
export const GAME_ACTIONS: string[] = [];

/** Claus de text que fa servir el codi del joc. */
export const GAME_TEXT_KEYS: string[] = [];

/** Les de `GAME_TEXT_KEYS` més les que depenen del contingut: el nom amb article de cada objecte. */
export function gameTextKeys(content: GameContent) {
  return [...GAME_TEXT_KEYS, ...Object.keys(content.items).map((id) => `obj.${id}.amb_article`)];
}

export function installGameLogic(_n: Narrative) {}
