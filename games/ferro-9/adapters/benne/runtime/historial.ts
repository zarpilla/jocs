/**
 * L'historial de Ferro-9: les últimes línies que caben al panell de la GUI `historial` (la crea
 * games/ferro-9/adapters/benne/joc.ts; el joc s'atura mentre és oberta, amb `pauseGame`).
 *
 * Es copia a `src/game/narrative/` amb `npm run benne:sync`, i `narrative.ts` el torna a exportar.
 * No l'editis allà: edita `games/ferro-9/adapters/benne/runtime/`.
 */
import { narrative } from './narrative';

// ─── Historial: les últimes línies dites, per tornar a llegir les que han passat massa de pressa ──

const HISTORIAL_MAX = 80;
const historial: { who: string | null; text: string }[] = [];

/** Apunta una línia a l'historial (els títols no). `who`: un personatge, `player` o `narrator`. */
export function recordLine(who: string, text: string) {
  if (who === 'title') return;
  const id = who === 'player' ? narrative.world.activeProtagonist() : who;
  historial.push({ who: who === 'narrator' ? null : narrative.characterName(id), text });
  if (historial.length > HISTORIAL_MAX) historial.shift();
}

/**
 * Les últimes línies de l'historial que caben en `rows` files de `perRow` caràcters, la més nova
 * a baix. Si no n'hi ha cap, `empty`.
 */
export function historyText(empty: string, rows: number, perRow: number) {
  const out: string[] = [];
  let used = 0;
  for (let i = historial.length - 1; i >= 0; i--) {
    const { who, text } = historial[i]!;
    const line = who ? `${who}: ${text}` : text;
    const n = Math.ceil(line.length / perRow);
    if (used + n > rows && out.length) break;
    out.unshift(line);
    used += n;
  }
  return out.length ? out.join('\n') : empty;
}

/** Partida carregada: l'historial d'abans ja no hi té res a veure. */
export function resetHistory() {
  historial.length = 0;
}
