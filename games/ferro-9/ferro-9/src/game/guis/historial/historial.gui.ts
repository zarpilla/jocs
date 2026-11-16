// Creat per adapters/benne (benne-content.ts): l'historial de línies.
import { guis } from '@game';
import { gui, linies, tanca } from './historial.ids';
import { historyPage, narrative } from '../../narrative/narrative';

/** Files de text que hi caben i caràcters per fila (la lletra fa uns 5 px; es deixa marge pels salts de paraula). */
const FILES = 15;
const PER_FILA = 72;

/** Quantes de les línies més noves se salten: 0 = les últimes. La roda o les fletxes ho canvien. */
let scroll = 0;
let above = false;

function show() {
  const page = historyPage(FILES, PER_FILA, scroll, {
    empty: narrative.t('ui.historial.buit'),
    above: narrative.t('ui.historial.amunt'),
    below: narrative.t('ui.historial.avall'),
  });
  linies.text = page.text;
  above = page.above;
}

/** `+1`: una línia més enrere; `-1`: una més endavant. */
function move(delta: number) {
  if (delta > 0 && !above) return;
  scroll = Math.max(0, scroll + delta);
  show();
}

gui.onShow(() => {
  scroll = 0;
  show();
});

tanca.onClick(() => gui.hide());

// Tecla H: obre o tanca l'historial (Esc el tanca des del motor). No mentre s'escriu el nom d'una partida.
// Amb l'historial obert, les fletxes (o Re Pàg / Av Pàg) i la roda del ratolí hi van amunt i avall.
const w = window as unknown as { __ferroHistorialKey?: (e: KeyboardEvent) => void; __ferroHistorialWheel?: (e: WheelEvent) => void };
if (w.__ferroHistorialKey) window.removeEventListener('keydown', w.__ferroHistorialKey);
if (w.__ferroHistorialWheel) window.removeEventListener('wheel', w.__ferroHistorialWheel);
w.__ferroHistorialKey = (e: KeyboardEvent) => {
  if (e.ctrlKey || e.metaKey || e.altKey) return;
  const focus = document.activeElement;
  if (focus instanceof HTMLInputElement || focus instanceof HTMLTextAreaElement) return;
  if (gui.visible) {
    const delta = { ArrowUp: 1, ArrowDown: -1, PageUp: 5, PageDown: -5 }[e.key];
    if (delta) {
      e.preventDefault();
      move(delta);
      return;
    }
  }
  // Esc tanca el menú del joc, com el botó Continua.
  if (e.key === 'Escape' && guis.gameMenu.visible) {
    guis.gameMenu.hide();
    return;
  }
  if (e.repeat || (e.key !== 'h' && e.key !== 'H')) return;
  if (guis.saveMenu.visible) return;
  if (gui.visible) gui.hide();
  else gui.show();
};
w.__ferroHistorialWheel = (e: WheelEvent) => {
  if (!gui.visible || e.deltaY === 0) return;
  move(e.deltaY < 0 ? 1 : -1);
};
window.addEventListener('keydown', w.__ferroHistorialKey);
window.addEventListener('wheel', w.__ferroHistorialWheel, { passive: true });
