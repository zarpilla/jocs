/**
 * Suma Zero a Benne: el que aquest joc fa diferent (vegeu adapters/benne/joc-benne.ts).
 */
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { readJson, writeJson, type Json } from '../../../../adapters/benne/benne-content.js';
import type { JocBenne } from '../../../../adapters/benne/joc-benne.js';

export default {
  nom: 'Suma Zero',
  projecte: 'suma-zero',
  paquet: 'suma-zero-benne',
  fonts: { regular: 'suma-regular', negreta: 'suma-negreta', script: 'tools/font/suma_font.py' },
  colorsVeu: { iri: '#f0a050', vet: '#60d8d8' },
  veusProtagonistes: true,
  musicaSincronitzada: true,
  textosGui: {
    'game-menu': { historial: 'ui.menu.historial', pista: 'ui.menu.pista' },
  },
  configura(config, t) {
    // Temps de lectura: Benne talla les línies a 4,5 s, i les llargues (en Marcel) no es poden llegir.
    // Amb un clic se salten, de manera que val més que es quedin prou estona. Els primers 500 ms d'una
    // línia, però, un clic no la salta (un doble clic no se'n menja cap sense llegir).
    config.speech = { ...(config.speech as Json), clickToSkip: true, minDurationMs: 1500, msPerCharacter: 75, maxDurationMs: 14000, clickProtectMs: 500 };
    // «Walk to» de la línia de verbs (walkToLabel).
    config.walkToLabel = t('ui.verb.walkTo', String(config.walkToLabel ?? 'Walk to'));
  },
  guis(gameDir) {
    addGameMenuButtons(gameDir);
    addHistoryGui(gameDir);
  },
} satisfies JocBenne;

// ─── Botons «Historial» i «Pista» al menú del joc ────────────────────────────

/**
 * La plantilla té un botó «Title Screen» sense funció: el convertim en dos botons de mitja amplada,
 * l'historial de línies i demanar una pista. (Abans hi havia «Canvia», que ara és a la barra de verbs:
 * si hi és, es reaprofita.) Es pot tornar a executar: el codi afegit al script es regenera.
 */
const MENU_MARK = '// Afegit per adapters/benne (benne-content.ts)';

function addGameMenuButtons(gameDir: string) {
  const dir = join(gameDir, 'guis/game-menu');
  const jsonPath = join(dir, 'game-menu.gui.json');
  const tsPath = join(dir, 'game-menu.gui.ts');
  if (!existsSync(jsonPath) || !existsSync(tsPath)) return;
  const def = readJson(jsonPath);
  const controls = (def.controls as Json[]) ?? [];
  const old = controls.find((c) => c.id === 'canviar');
  if (old) {
    old.id = 'historial';
    writeJson(jsonPath, def);
  } else if (!controls.some((c) => c.id === 'historial')) {
    const index = controls.findIndex((c) => c.id === 'title-screen');
    const half = controls.find((c) => c.id === 'save');
    if (index < 0 || !half) return;
    const row = (controls[index]!.gridPlacement as Json).row;
    const button = (id: string, align: string) => ({
      ...structuredClone(half), id, gridPlacement: { ...(half.gridPlacement as Json), row, align },
    });
    controls.splice(index, 1, button('historial', 'center-left'), button('pista', 'center-right'));
    writeJson(jsonPath, def);
  }
  // el script: fora el que hi havíem afegit abans, i s'hi torna a posar
  let script = readFileSync(tsPath, 'utf8');
  const mark = script.indexOf(MENU_MARK);
  if (mark >= 0) script = script.slice(0, mark);
  script = script
    .replace(/\nimport \{[^}]*\} from '\.\.\/\.\.\/narrative\/narrative(\.script)?';/g, '')
    .replace(/import \{ ([^}]*) \} from '\.\/game-menu\.ids';/, (_m, names: string) => {
      const own = names.split(',').map((n) => n.trim()).filter((n) => n && !['canviar', 'historial', 'pista'].includes(n));
      return `import { ${[...own, 'historial', 'pista'].join(', ')} } from './game-menu.ids';
import { sayHint } from '../../narrative/narrative.script';
import { showHistory } from '../../narrative/narrative';`;
    });
  writeFileSync(tsPath, `${script.trimEnd()}

${MENU_MARK}: l'historial de línies i demanar una pista.
historial.onClick(() => {
  gui.hide()
  showHistory()
})

pista.onClick(() => {
  gui.hide()
  sayHint()
})
`);
}

// ─── L'historial de línies ──────────────────────────────────────────────────

/**
 * La GUI `historial`: un fons que ocupa tota la pantalla (clicar-lo la tanca), el títol, el peu i dos
 * textos superposats, un per als noms (en negreta) i un per a les línies, que omple
 * `runtime/narrative.ts` (`showHistory`) amb el text ja partit en línies. Sense art: només colors.
 */
function addHistoryGui(gameDir: string) {
  const dir = join(gameDir, 'guis/historial');
  mkdirSync(dir, { recursive: true });
  const { width: W, height: H } = (readJson(join(gameDir, 'game-config.json')).resolution as { width: number; height: number });
  const text = (id: string, x: number, y: number, font: string, color: string, align = 'left') =>
    ({ type: 'text', id, x, y, text: '', font, fontSize: 8, color, align, zIndex: 2 });
  writeJson(join(dir, 'historial.gui.json'), {
    id: 'historial', name: 'Historial', description: "Les últimes línies dites (adapters/benne/benne-content.ts).",
    visible: false, display: { aseprite: false }, modal: true, zIndex: 110,
    controls: [
      {
        type: 'button', id: 'fons', x: 0, y: 0, width: W, height: H, backgroundAnchor: 'top-left', text: '',
        font: 'suma-regular', fontSize: 8, textColor: '#ffffff', backgroundTag: '', backgroundColor: '#0b0a12',
        backgroundColorStates: { hover: '#0b0a12', pressed: '#0b0a12', disabled: '#0b0a12' }, zIndex: 1,
      },
      text('titol', 14, 8, 'suma-negreta', '#f0dc8c'),
      text('noms', 14, HISTORIAL_TOP, 'suma-negreta', '#7fd6c4'),
      text('linies', 14, HISTORIAL_TOP, 'suma-regular', '#e6e2ee'),
      text('peu', W - 14, H - 15, 'suma-regular', '#8a8598', 'right'),
    ],
  });
}

/** On comencen les línies de l'historial (y), i quantes n'hi caben: ho fa servir el runtime. */
const HISTORIAL_TOP = 24; // ha de coincidir amb runtime/narrative.ts (HISTORIAL_FILES)

