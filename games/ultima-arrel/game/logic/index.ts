/**
 * Lògica pròpia de L'Última Arrel, independent del motor gràfic. Qualsevol adaptador (Benne o un altre) la instal·la
 * sobre el `Narrative`. De moment no n'hi ha cap: tot el joc es diu amb el JSON de `data/`.
 */
import type { GameContent, Narrative } from '@aventura/narrative-core';

/** Totes les accions que el contingut pot fer servir (`"action": { "name": ... }`). */
export const GAME_ACTIONS: string[] = [];

/** Claus de text que fa servir el codi del joc. */
export const GAME_TEXT_KEYS: string[] = [];

/** Les de `GAME_TEXT_KEYS` més les que depenen del contingut (cap, de moment). */
export function gameTextKeys(_content: GameContent): string[] {
  return [...GAME_TEXT_KEYS];
}

export function installGameLogic(_n: Narrative): void {
  // Cap regla pròpia encara.
}
