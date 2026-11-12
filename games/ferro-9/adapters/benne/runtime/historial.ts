/**
 * L'historial de Ferro-9: les línies dites, per pàgines que caben al panell de la GUI `historial` (la crea
 * games/ferro-9/adapters/benne/joc.ts; el joc s'atura mentre és oberta, amb `pauseGame`). Es pot tirar enrere
 * amb la roda del ratolí o les fletxes.
 *
 * Es copia a `src/game/narrative/` amb `npm run benne:sync`, i `narrative.ts` el torna a exportar.
 * No l'editis allà: edita `games/ferro-9/adapters/benne/runtime/`.
 */
import { narrative } from './narrative';

// ─── Historial: les últimes línies dites, per tornar a llegir les que han passat massa de pressa ──

const HISTORIAL_MAX = 400;
const historial: { who: string | null; text: string }[] = [];

/** Apunta una línia a l'historial (els títols no). `who`: un personatge, `player` o `narrator`. */
export function recordLine(who: string, text: string) {
  if (who === 'title') return;
  const id = who === 'player' ? narrative.world.activeProtagonist() : who;
  historial.push({ who: who === 'narrator' ? null : narrative.characterName(id), text });
  if (historial.length > HISTORIAL_MAX) historial.shift();
}

/** Una pàgina de l'historial. `above`/`below`: encara hi ha línies més antigues / més noves. */
export interface HistoryPage {
  text: string;
  above: boolean;
  below: boolean;
}

/**
 * Una pàgina de l'historial que cap en `rows` files de `perRow` caràcters, la línia més nova a baix. `scroll`:
 * quantes de les línies més noves se salten (0 = les últimes). Si n'hi ha més amunt o més avall, la primera o
 * l'última fila és la marca `marks.above` o `marks.below`. Si no s'ha dit res, `marks.empty`.
 */
export function historyPage(rows: number, perRow: number, scroll: number, marks: { empty: string; above: string; below: string }): HistoryPage {
  if (!historial.length) return { text: marks.empty, above: false, below: false };
  const end = Math.max(1, historial.length - Math.max(0, scroll));
  const below = end < historial.length;
  const room = rows - (below ? 1 : 0);
  const out: string[] = [];
  let used = 0;
  let i = end - 1;
  for (; i >= 0; i--) {
    const { who, text } = historial[i]!;
    const line = who ? `${who}: ${text}` : text;
    const n = Math.ceil(line.length / perRow);
    if (used + n > room && out.length) break;
    out.unshift(line);
    used += n;
  }
  const above = i >= 0;
  // La marca de dalt també ocupa una fila: si no hi cap, fora la línia més antiga (sempre en queda una).
  if (above && used + 1 > room && out.length > 1) out.shift();
  return {
    text: [...(above ? [marks.above] : []), ...out, ...(below ? [marks.below] : [])].join('\n'),
    above,
    below,
  };
}

/** Partida carregada: l'historial d'abans ja no hi té res a veure. */
export function resetHistory() {
  historial.length = 0;
}
