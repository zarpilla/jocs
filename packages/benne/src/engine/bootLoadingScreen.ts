/**
 * La pantalla de càrrega de l'index.html (`#carregant`): es veu des del primer moment, mentre es baixa el
 * JavaScript. Quan Phaser comença a carregar, la barra en segueix el progrés; quan arrenca la primera sala,
 * s'esvaeix. Als editors i a les previsualitzacions no hi és, i aquí no fa res.
 */
const element = (): HTMLElement | null =>
  typeof document === 'undefined' ? null : document.getElementById('carregant');

/** `value`: de 0 a 1 (l'esdeveniment `progress` del loader de Phaser). */
export function setBootLoadingProgress(value: number): void {
  const el = element();
  if (!el) return;
  el.classList.add('amb-progres');
  // A blocs sencers (n'hi ha 16, vegeu .barra a index.html)
  el.style.setProperty('--progres', String(Math.floor(Math.max(0, Math.min(1, value)) * 16) / 16));
}

export function hideBootLoadingScreen(): void {
  const el = element();
  if (!el || el.classList.contains('fet')) return;
  setBootLoadingProgress(1);
  el.classList.add('fet');
  window.setTimeout(() => el.remove(), 500);
}
