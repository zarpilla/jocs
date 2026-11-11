/**
 * Ferro-9 a Benne: el que aquest joc fa diferent (vegeu adapters/benne/joc-benne.ts).
 */
import { copyFileSync, existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { W, readJson, writeJson, type Json } from '../../../../adapters/benne/benne-content.js';
import type { JocBenne } from '../../../../adapters/benne/joc-benne.js';

export default {
  nom: 'Ferro-9',
  projecte: 'ferro-9',
  paquet: 'ferro9-benne',
  fonts: { regular: 'ferro-regular', negreta: 'ferro-negreta', script: 'tools/font/ferro_font.py' },
  colorsVeu: { iri: '#f0a050', vet: '#60d8d8', cargol: '#a8f0c0', capatas: '#d8a878', mos: '#c8b8f0', mare: '#ff90c8' },
  textosGui: {
    'game-menu': { canviar: 'ui.menu.canviar', pista: 'ui.menu.pista', historial: 'ui.menu.historial' },
    historial: { titol: 'ui.menu.historial', tanca: 'ui.menu.tornar' },
  },
  guis(gameDir) {
    addGameMenuButtons(gameDir);
    addHistoryGui(gameDir);
  },
} satisfies JocBenne;

// ─── Botons «Canvia» i «Pista» al menú del joc ──────────────────────────────

/**
 * La plantilla té un botó «Title Screen» sense funció: el convertim en dos botons de mitja
 * amplada, canviar de protagonista i demanar una pista. Només una vegada.
 */
function addGameMenuButtons(gameDir: string) {
  const dir = join(gameDir, 'guis/game-menu');
  const jsonPath = join(dir, 'game-menu.gui.json');
  const tsPath = join(dir, 'game-menu.gui.ts');
  if (!existsSync(jsonPath) || !existsSync(tsPath)) return;
  const def = readJson(jsonPath);
  const controls = (def.controls as Json[]) ?? [];
  if (!controls.some((c) => c.id === 'canviar')) {
    const index = controls.findIndex((c) => c.id === 'title-screen');
    const half = controls.find((c) => c.id === 'save');
    if (index < 0 || !half) return;
    const row = (controls[index]!.gridPlacement as Json).row;
    const button = (id: string, align: string) => ({
      ...structuredClone(half), id, gridPlacement: { ...(half.gridPlacement as Json), row, align },
    });
    controls.splice(index, 1, button('canviar', 'center-left'), button('pista', 'center-right'));
    writeJson(jsonPath, def);
  }
  const script = readFileSync(tsPath, 'utf8');
  if (!script.includes('switchProtagonist')) {
    const imports = script.replace(
      /import \{ ([^}]*) \} from '\.\/game-menu\.ids';/,
      (_m, names: string) => `import { ${names.trim()}, canviar, pista } from './game-menu.ids';\nimport { sayHint, switchProtagonist } from '../../narrative/narrative.script';`,
    );
    writeFileSync(tsPath, `${imports.trimEnd()}

// Afegit per adapters/benne (benne-content.ts): canviar de protagonista i demanar una pista.
canviar.onClick(() => {
  gui.hide()
  switchProtagonist()
})

pista.onClick(() => {
  gui.hide()
  sayHint()
})
`);
  }
}

// ─── Historial: les últimes línies dites ────────────────────────────────────

/**
 * Una GUI `historial` amb les últimes línies dites (la mostra el botó «Historial» del menú o la
 * tecla H), i el botó al menú: «Continua» passa a mitja amplada i «Historial» va al seu costat.
 * Només una vegada. El fons és el del menú (se'n copia el full d'art). Mentre és obert, el joc
 * s'atura (`pauseGame`): la línia que s'estava dient espera.
 */
function addHistoryGui(gameDir: string) {
  const menuDir = join(gameDir, 'guis/game-menu');
  const menuJson = join(menuDir, 'game-menu.gui.json');
  const menuTs = join(menuDir, 'game-menu.gui.ts');
  if (!existsSync(menuJson) || !existsSync(menuTs)) return;
  const menu = readJson(menuJson);
  const controls = (menu.controls as Json[]) ?? [];
  const resume = controls.find((c) => c.id === 'resume');
  const half = controls.find((c) => c.id === 'save');
  if (resume && half && !controls.some((c) => c.id === 'historial')) {
    const row = (resume.gridPlacement as Json).row;
    resume.width = half.width;
    resume.gridPlacement = { ...(resume.gridPlacement as Json), align: 'center-left' };
    controls.splice(controls.indexOf(resume) + 1, 0, {
      ...structuredClone(half), id: 'historial', gridPlacement: { ...(half.gridPlacement as Json), row, align: 'center-right' },
    });
    writeJson(menuJson, menu);
  }
  const script = readFileSync(menuTs, 'utf8');
  if (!script.includes('historial')) {
    const imports = script.replace(
      /import \{ ([^}]*) \} from '\.\/game-menu\.ids';/,
      (_m, names: string) => `import { ${names.trim()}, historial } from './game-menu.ids';`,
    );
    writeFileSync(menuTs, `${imports.trimEnd()}

// Afegit per adapters/benne (benne-content.ts): l'historial de línies.
historial.onClick(() => {
  gui.hide()
  guis.historial.show()
})
`);
  }

  const dir = join(gameDir, 'guis/historial');
  const jsonPath = join(dir, 'historial.gui.json');
  const tsPath = join(dir, 'historial.gui.ts');
  const bg = controls.find((c) => c.type === 'nineSliceImage');
  const HISTORIAL = historialPanel();
  if (!existsSync(jsonPath) && half && bg) {
    writeJson(jsonPath, {
      id: 'historial', name: 'Historial', description: "Les últimes línies dites (adapters/benne).", visible: false,
      display: { aseprite: true }, modal: true, pauseGame: true, zIndex: 102,
      controls: [
        { ...structuredClone(bg), id: 'fons', x: HISTORIAL.x, y: HISTORIAL.y, width: HISTORIAL.width, height: HISTORIAL.height },
        { type: 'text', id: 'titol', x: W / 2, y: HISTORIAL.y + k(9), text: 'Historial', font: 'ferro-negreta', fontSize: 8, color: '#d8b46a', align: 'center', zIndex: 2 },
        {
          type: 'text', id: 'linies', x: HISTORIAL.x + k(16), y: HISTORIAL.y + k(27), text: '', font: 'ferro-regular', fontSize: 8,
          color: '#ffffff', align: 'left', wordWrapWidth: HISTORIAL.width - k(32), zIndex: 2,
        },
        {
          ...structuredClone(half), id: 'tanca', x: W / 2 - Number(half.width) / 2, y: HISTORIAL.y + HISTORIAL.height - k(28),
          gridPlacement: undefined, text: 'Torna',
        },
      ],
    });
  }
  if (!existsSync(tsPath)) {
    writeFileSync(tsPath, `// Creat per adapters/benne (benne-content.ts): l'historial de línies.
import { guis } from '@game';
import { gui, linies, tanca } from './historial.ids';
import { historyText, narrative } from '../../narrative/narrative';

/** Files de text que hi caben i caràcters per fila (la lletra fa uns 5 px; es deixa marge pels salts de paraula). */
const FILES = ${HISTORIAL.rows};
const PER_FILA = ${HISTORIAL.perRow};

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
`);
  }
  const art = join(gameDir, 'assets/images/guis/historial');
  const menuArt = join(gameDir, 'assets/images/guis/game-menu');
  if (!existsSync(join(art, 'historial.png')) && existsSync(join(menuArt, 'game-menu.png'))) {
    mkdirSync(art, { recursive: true });
    copyFileSync(join(menuArt, 'game-menu.png'), join(art, 'historial.png'));
    const sheet = readJson(join(menuArt, 'game-menu.json'));
    (sheet.meta as Json).image = 'historial.png';
    writeJson(join(art, 'historial.json'), sheet);
  }
}

/** Una mida de pantalla feta a 480×270, a la resolució del joc (×4/3 a 640×360). */
const k = (v: number) => Math.round(v * W / 480);

/**
 * Panell de l'historial (coordenades de pantalla) i quant text hi cap. Fet a 480×270 i escalat: a 640×360 la lletra
 * també és un terç més gran (16 px de línia), així que hi caben les mateixes files i caràcters.
 */
function historialPanel() {
  return { x: k(16), y: k(8), width: W - k(32), height: k(254), rows: 15, perRow: 72 };
}

