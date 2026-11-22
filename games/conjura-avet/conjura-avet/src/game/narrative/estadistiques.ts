// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
/**
 * Estadístiques anònimes: quantes partides es comencen, fins a quin acte arriben, a quin final i
 * quanta estona es juga. El servidor només suma comptadors per dia; no hi ha cap identificador.
 *
 * Res no es desa al dispositiu (ni galetes ni localStorage) i no s'envia res si el navegador demana
 * no ser seguit (Global Privacy Control o Do Not Track), ni des d'un robot o un navegador automatitzat
 * (cercadors, eines d'auditoria, scripts de proves), ni des de localhost (`npm run dev` o un build
 * provat en local): les proves no compten.
 *
 * Es copia a `src/game/narrative/` amb `npm run benne:sync`. No l'editis allà.
 */
import type { Narrative } from '@aventura/narrative-core';

/** Adreça completa: el joc pot ser a malaherbasoft.cat, a itch.io o a l'escriptori. */
const ENDPOINT = 'https://malaherbasoft.cat/api/e';
/** Sense cap tecla, clic ni toc durant aquesta estona, el temps deixa de comptar. */
const INACTIU_MS = 2 * 60_000;

type Esdeveniment = 'nova' | 'continua' | 'acte' | 'final' | 'temps';

let joc = '';
let actiu = false;
const navegador = typeof navigator === 'object' ? (navigator as Navigator & { globalPrivacyControl?: boolean }) : undefined;
const local = typeof location === 'object' && /^(localhost|127\.0\.0\.1|\[::1\])$/.test(location.hostname);
/** Robots i navegadors automatitzats: `webdriver` el posen Selenium, Puppeteer, Playwright i Chrome headless. */
const robot =
  navegador?.webdriver === true || /bot\b|crawl|spider|slurp|headless|lighthouse/i.test(navegador?.userAgent ?? '');
const desactivat =
  import.meta.env.DEV || local || robot || !navegador || navegador.globalPrivacyControl === true || navegador.doNotTrack === '1';

function envia(ev: Esdeveniment, v: string | number = '') {
  if (desactivat || !joc) return;
  const cos = JSON.stringify({ joc, ev, v: String(v) });
  // sendBeacon arriba encara que es tanqui la pestanya; si no hi és, fetch amb keepalive.
  const blob = new Blob([cos], { type: 'text/plain' });
  if (navegador?.sendBeacon?.(ENDPOINT, blob)) return;
  // La resposta no ens cal: `no-cors` evita que el navegador demani permís a l'altre domini.
  fetch(ENDPOINT, { method: 'POST', body: cos, keepalive: true, mode: 'no-cors' }).catch(() => {});
}

// ─── Temps de joc ────────────────────────────────────────────────────────────
// Compta el temps amb la pestanya visible i alguna acció recent. S'envia el que s'ha acumulat cada
// cop que la pestanya s'amaga o es tanca (el servidor ho suma).

let acumulat = 0;
let desDe: number | null = null;
let darreraAccio = 0;

function talla(ara = Date.now()) {
  if (desDe === null) return;
  // Si fa estona que no es fa res, només compta fins a la darrera acció (més el marge).
  acumulat += Math.max(0, Math.min(ara, darreraAccio + INACTIU_MS) - desDe);
  desDe = ara - darreraAccio < INACTIU_MS ? ara : null;
}

function buidaTemps() {
  talla();
  // Amagada o tancada: no compta fins que torni a ser visible.
  if (document.visibilityState !== 'visible') desDe = null;
  const segons = Math.round(acumulat / 1000);
  acumulat = 0;
  if (segons >= 5) envia('temps', segons);
}

function accio() {
  if (!actiu) return;
  const ara = Date.now();
  talla(ara);
  darreraAccio = ara;
  if (desDe === null && document.visibilityState === 'visible') desDe = ara;
}

function comencaTemps() {
  if (actiu || desactivat || typeof document !== 'object') return;
  actiu = true;
  darreraAccio = Date.now();
  desDe = document.visibilityState === 'visible' ? darreraAccio : null;
  for (const tipus of ['pointerdown', 'keydown']) addEventListener(tipus, accio, { passive: true, capture: true });
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden') buidaTemps();
    else accio();
  });
  addEventListener('pagehide', buidaTemps);
}

// ─── Ganxos (des del pont) ───────────────────────────────────────────────────

/** Una vegada, en crear la narrativa: `id` és la carpeta del joc (`games/<id>`). */
export function installStats(narrative: Narrative, id: string) {
  joc = id;
  narrative.on((e) => {
    const acte = e.type === 'questStarted' && /^acte(\d+)$/.exec(e.quest)?.[1];
    // L'acte 1 ja és la partida nova.
    if (acte && acte !== '1') envia('acte', acte);
  });
}

/** El botó «Comença» de la portada. */
export function statsNewGame() {
  envia('nova');
  comencaTemps();
}

let continuada = false;
/** S'ha carregat una partida desada (una vegada per pàgina). */
export function statsLoadedGame() {
  if (continuada || actiu) return;
  continuada = true;
  envia('continua');
  comencaTemps();
}

/** Comença l'escena d'un final. */
export function statsEnding(id: string) {
  envia('final', id);
}
