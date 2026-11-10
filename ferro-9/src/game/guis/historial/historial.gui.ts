// Creat per adapters/benne (benne-content.ts): l'historial de línies.
import { guis } from '@game';
import { gui, linies, tanca } from './historial.ids';
import { historyText, narrative } from '../../narrative/narrative';

/** Files de text que hi caben i caràcters per fila (la lletra fa uns 5 px; es deixa marge pels salts de paraula). */
const FILES = 15;
const PER_FILA = 72;

gui.onShow(() => {
  linies.text = historyText(narrative.t('ui.historial.buit'), FILES, PER_FILA);
});

tanca.onClick(() => gui.hide());

// Tecla H: obre o tanca l'historial (Esc el tanca des del motor). No mentre s'escriu el nom d'una partida.
const w = window as unknown as { __ferroHistorialKey?: (e: KeyboardEvent) => void };
if (w.__ferroHistorialKey) window.removeEventListener('keydown', w.__ferroHistorialKey);
w.__ferroHistorialKey = (e: KeyboardEvent) => {
  if (e.ctrlKey || e.metaKey || e.altKey || e.repeat) return;
  if (e.key !== 'h' && e.key !== 'H') return;
  const focus = document.activeElement;
  if (focus instanceof HTMLInputElement || focus instanceof HTMLTextAreaElement) return;
  if (guis.saveMenu.visible) return;
  if (gui.visible) gui.hide();
  else gui.show();
};
window.addEventListener('keydown', w.__ferroHistorialKey);
