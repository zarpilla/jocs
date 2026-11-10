/**
 * Historial de línies per defecte: no en guarda cap. Un joc que en vulgui en posa el seu a
 * `games/<joc>/adapters/benne/runtime/historial.ts`, amb les mateixes funcions (i les que vulgui
 * més); `npm run benne:sync` copia el del joc en lloc d'aquest.
 */

/** Apunta una línia a l'historial (es crida en començar-la). */
export function recordLine(_who: string, _text: string) {}

/** Partida carregada: s'oblida l'historial d'abans. */
export function resetHistory() {}
