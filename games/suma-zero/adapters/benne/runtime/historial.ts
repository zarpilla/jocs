/**
 * L'historial de Suma Zero: una pantalla sencera amb les línies dites, que es pot recórrer amb la
 * roda i les fletxes (GUI `historial`, la crea games/suma-zero/adapters/benne/joc.ts).
 *
 * Es copia a `src/game/narrative/` amb `npm run benne:sync`, i `narrative.ts` el torna a exportar.
 * No l'editis allà: edita `games/suma-zero/adapters/benne/runtime/`.
 */
import { guis } from '@game';
import { narrative } from './narrative';
import mapping from './mapping.generated.json';
import fontXml from '../assets/fonts/suma-regular.xml?raw';

// ─── Historial: les últimes línies dites, per tornar-les a llegir ───────────

/** Les línies dites des que s'ha obert el joc (no es desa: és per a les que t'acabes de perdre). */
const historial: { name: string; text: string }[] = [];
const HISTORIAL_MAX = 200;

/** Apunta una línia a l'historial (es crida en començar-la). Els títols no hi van. */
export function recordLine(who: string, text: string) {
  if (who === 'title' || !text) return;
  const id = who === 'player' ? narrative.world.activeProtagonist() : who;
  historial.push({ name: who === 'narrator' ? '' : narrative.characterName(id), text });
  if (historial.length > HISTORIAL_MAX) historial.splice(0, historial.length - HISTORIAL_MAX);
}

// Amplada de cada lletra de la font de les línies (xadvance del .xml), per partir-les com les pinta Benne.
const ADVANCE = new Map<number, number>();
for (const m of fontXml.matchAll(/<char id="(\d+)"[^>]*xadvance="(-?\d+)"/g)) ADVANCE.set(Number(m[1]), Number(m[2]));
const textWidth = (text: string) => [...text].reduce((w, ch) => w + (ADVANCE.get(ch.codePointAt(0)!) ?? 6), 0);

/** Parteix un text en línies que no passin de `max` píxels (per paraules). */
function wrap(text: string, max: number): string[] {
  const lines: string[] = [];
  let line = '';
  for (const word of text.split(/\s+/)) {
    const next = line ? `${line} ${word}` : word;
    if (line && textWidth(next) > max) {
      lines.push(line);
      line = word;
    } else {
      line = next;
    }
  }
  if (line) lines.push(line);
  return lines;
}

// Mides de la GUI `historial` (joc.ts): pantalla sencera, amb marges ×AMPLADA/480. L'alçada de línia és la de la font.
// L'amplada, del mapping (no de narrative.ts: s'importen l'un a l'altre i encara no hi seria).
const AMPLADA = (mapping as { resolucio?: { width?: number } }).resolucio?.width ?? 480;
const K = AMPLADA / 480;
// L'alçada de disseny de la GUI (la mínima, si la pantalla s'adapta: adapters/benne/tactil).
const RES = (mapping as { resolucio?: { height?: number; minHeight?: number } }).resolucio;
const ALT = RES?.minHeight ?? RES?.height ?? Math.round(AMPLADA * 9 / 16);
const LINIA = Number(fontXml.match(/lineHeight="(\d+)"/)?.[1] ?? 12);
const HISTORIAL_AMPLE = AMPLADA - Math.round(28 * K);
const HISTORIAL_FILES = Math.floor((ALT - Math.round((15 + 4 + 24) * K)) / LINIA);
let historialEnrere = 0;

/** Omple la GUI de l'historial: les últimes línies a baix; `historialEnrere` files més amunt. */
function renderHistory() {
  const files: { nom: string; text: string }[] = [];
  for (const e of historial) {
    if (e.name) files.push({ nom: e.name, text: '' });
    for (const l of wrap(e.text, HISTORIAL_AMPLE)) files.push({ nom: '', text: l });
  }
  historialEnrere = Math.max(0, Math.min(historialEnrere, files.length - HISTORIAL_FILES));
  const fi = files.length - historialEnrere;
  const visibles = files.slice(Math.max(0, fi - HISTORIAL_FILES), fi);
  const c = guis.historial.controls;
  c.titol.text = narrative.t('ui.historial.titol');
  c.peu.text = narrative.t('ui.historial.peu');
  c.noms.text = visibles.map((f) => f.nom).join('\n');
  c.linies.text = files.length ? visibles.map((f) => f.text).join('\n') : narrative.t('ui.historial.buit');
}

/** Obre l'historial (botó del menú o tecla H). */
export function showHistory() {
  historialEnrere = 0;
  renderHistory();
  guis.historial.show();
}

const historyOpen = () => guis.historial.visible;
const hideHistory = () => guis.historial.hide();
// (`async`: és instantani, i així Benne no avisa que no ha passat pel connector de BenneScript)
guis.historial.controls.fons.onClick(async () => hideHistory());

// La tecla H obre i tanca l'historial, si no hi ha cap menú obert (al de desar s'hi escriu). Obert, la
// roda i les fletxes van enrere i endavant, i Esc el tanca.
const MENUS = ['gameMenu', 'saveMenu', 'loadMenu', 'settingsMenu', 'portada'] as const;
if (typeof window !== 'undefined') {
  window.addEventListener('keydown', (ev) => {
    if (historyOpen()) {
      if (ev.key === 'h' || ev.key === 'H' || ev.key === 'Escape') hideHistory();
      else if (ev.key === 'ArrowUp' || ev.key === 'PageUp') { historialEnrere += ev.key === 'PageUp' ? HISTORIAL_FILES - 1 : 1; renderHistory(); }
      else if (ev.key === 'ArrowDown' || ev.key === 'PageDown') { historialEnrere -= ev.key === 'PageDown' ? HISTORIAL_FILES - 1 : 1; renderHistory(); }
      return;
    }
    // Esc tanca el menú del joc, com el botó Continua.
    if (ev.key === 'Escape' && guis.gameMenu.visible) {
      guis.gameMenu.hide();
      return;
    }
    if (ev.key !== 'h' && ev.key !== 'H') return;
    const all = guis as unknown as Record<string, { visible: boolean } | undefined>;
    if (MENUS.some((m) => all[m]?.visible)) return;
    showHistory();
  });
  window.addEventListener('wheel', (ev) => {
    if (!historyOpen()) return;
    historialEnrere += ev.deltaY < 0 ? 2 : -2;
    renderHistory();
  });
}

/** Partida carregada: l'historial d'abans ja no hi té res a veure. */
export function resetHistory() {
  historial.length = 0;
}
