/**
 * Lògica pròpia d'aquest joc, independent del motor gràfic. Qualsevol
 * adaptador (Benne o un altre) la instal·la sobre el `Narrative`.
 */
import type { GameContent, Narrative } from '@aventura/narrative-core';
import { DONAR_TEXTS, installDonar } from './donar.js';
import { ESCENES_TEXTS, installEscenes } from './escenes.js';
import { MUNTA_TEXTS, installMuntacarregues } from './muntacarregues.js';
import { SINCRONIA_TEXTS, installSincronia } from './sincronia.js';

export * from './escenes.js';
export * from './muntacarregues.js';
export * from './sincronia.js';

/** Totes les accions que el contingut pot fer servir (`"action": { "name": ... }`). */
export const GAME_ACTIONS: string[] = ['munta.enviar', 'munta.recollir', 'munta.nota', 'donar'];

/** Claus de text que fa servir el codi del joc. */
export const GAME_TEXT_KEYS: string[] = [...SINCRONIA_TEXTS, ...MUNTA_TEXTS, ...DONAR_TEXTS, ...ESCENES_TEXTS];

/** Les de `GAME_TEXT_KEYS` més les que depenen del contingut: el nom amb article de cada objecte. */
export function gameTextKeys(content: GameContent) {
  const noMunta = Object.values(content.items).map((i) => i.props?.no_munta).filter((k): k is string => typeof k === 'string');
  return [...GAME_TEXT_KEYS, ...noMunta, ...Object.keys(content.items).map((id) => `obj.${id}.amb_article`)];
}

export function installGameLogic(n: Narrative) {
  installSincronia(n);
  installMuntacarregues(n);
  installDonar(n);
  installEscenes(n);
}
