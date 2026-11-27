/**
 * Suma Zero a Benne: el que aquest joc fa diferent (vegeu adapters/benne/joc-benne.ts).
 */
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { readJson, writeJson, type Json } from '../../../../adapters/benne/benne-content.js';
import type { JocBenne } from '../../../../adapters/benne/joc-benne.js';
import { PASSOS } from '../../game/logic/sincronia.js';

export default {
  nom: 'Suma Zero',
  projecte: 'suma-zero',
  paquet: 'suma-zero-benne',
  fonts: { regular: 'suma-regular', negreta: 'suma-negreta', script: 'tools/font/suma_font.py' },
  colorsVeu: { iri: '#f0a050', vet: '#60d8d8' },
  veusProtagonistes: true,
  musicaSincronitzada: true,
  // Sense barra de verbs, pensat també per al mòbil (adapters/benne/tactil). L'art del HUD i del menú d'accions:
  // tools/hd640/hud.py; les sales i les GUI a l'alçada adaptable: tools/hd640/pantalla.py.
  tactil: true,
  textosGui: {
    'game-menu': { historial: 'ui.menu.historial', pista: 'ui.menu.pista' },
  },
  configura(config, t) {
    // Temps de lectura: Benne talla les línies a 4,5 s, i les llargues (en Marcel) no es poden llegir.
    // Amb un clic se salten, de manera que val més que es quedin prou estona. Els primers 500 ms d'una
    // línia, però, un clic no la salta (un doble clic no se'n menja cap sense llegir).
    config.speech = { ...(config.speech as Json), clickToSkip: true, minDurationMs: 2200, msPerCharacter: 75, maxDurationMs: 14000, clickProtectMs: 350 };
    // «Walk to» de la línia de verbs (walkToLabel).
    config.walkToLabel = t('ui.verb.walkTo', String(config.walkToLabel ?? 'Walk to'));
  },
  guis(gameDir) {
    addGameMenuButtons(gameDir);
    addHistoryGui(gameDir);
    addIndicadorGui(gameDir);
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
      const own = names.split(',').map((n) => n.trim()).filter((n) => n && !['canviar', 'historial', 'pista', 'quit'].includes(n));
      return `import { ${[...own, 'historial', 'pista', 'quit'].join(', ')} } from './game-menu.ids';
import { sayHint, quitAfterSaving } from '../../narrative/narrative.script';
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

// «Surt»: a l'escriptori tanca l'aplicació; al navegador torna a l'arrel del web (els jocs viuen a malaherbasoft.cat/<joc>/).
quit.onClick(() => {
  // Abans de marxar, desa on és la partida: «Continua» hi torna (tasca 108). Amb el menú tancat, el joc no és aturat.
  gui.hide()
  quitAfterSaving(() => {
    if (game.isDesktop) game.quit()
    else window.location.href = '/'
  })
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
  // A l'alçada mínima (la pantalla pot ser més alta: el fons s'estira i el peu va a baix, amb `anchorY`).
  const res = readJson(join(gameDir, 'game-config.json')).resolution as { width: number; height: number; minHeight?: number };
  const W = res.width;
  const H = res.minHeight ?? res.height;
  const k = (v: number) => Math.round(v * W / 480);   // els marges es van fer a 480×270
  const text = (id: string, x: number, y: number, font: string, color: string, align = 'left') =>
    ({ type: 'text', id, x, y, text: '', font, fontSize: 8, color, align, zIndex: 2 });
  writeJson(join(dir, 'historial.gui.json'), {
    id: 'historial', name: 'Historial', description: "Les últimes línies dites (adapters/benne/benne-content.ts).",
    visible: false, display: { aseprite: false }, modal: true, zIndex: 110,
    controls: [
      {
        type: 'button', id: 'fons', x: 0, y: 0, width: W, height: H, anchorY: 'stretch', backgroundAnchor: 'top-left', text: '',
        font: 'suma-regular', fontSize: 8, textColor: '#ffffff', backgroundTag: '', backgroundColor: '#0b0a12',
        backgroundColorStates: { hover: '#0b0a12', pressed: '#0b0a12', disabled: '#0b0a12' }, zIndex: 1,
      },
      text('titol', k(14), k(8), 'suma-negreta', '#f0dc8c'),
      text('noms', k(14), k(HISTORIAL_TOP), 'suma-negreta', '#7fd6c4'),
      text('linies', k(14), k(HISTORIAL_TOP), 'suma-regular', '#e6e2ee'),
      { ...text('peu', W - k(14), H - k(15), 'suma-regular', '#8a8598', 'right'), anchorY: 'bottom' },
    ],
  });
}

/** On comencen les línies de l'historial (y), i quantes n'hi caben: ho fa servir el runtime. */
const HISTORIAL_TOP = 24; // ha de coincidir amb runtime/narrative.ts (HISTORIAL_FILES)


// ─── L'indicador de les sincronies ──────────────────────────────────────────

/**
 * La GUI `indicador` (tasca 016): la placa de dalt a la dreta que diu quants torns queden en una sincronia (o la
 * sospita d'en Ballester, al collaret), amb l'estil de la barra «SOSPITA» del vestíbul. Rectangles de color, sense
 * art: la placa (vora daurada, fons fosc), l'etiqueta i, per a cada mida de pas (els torns o el límit de cada pas de
 * game/logic/sincronia.ts), una tira de segments en quatre colors. Tot a x = 0: el runtime (runtime/indicador.ts)
 * posa la placa a lloc i diu quins segments es veuen. Els rectangles són botons sense res a fer (un
 * botó desactivat el motor el pinta mig transparent).
 */
function addIndicadorGui(gameDir: string) {
  const dir = join(gameDir, 'guis/indicador');
  mkdirSync(dir, { recursive: true });
  // ha de coincidir amb runtime/indicador.ts
  const W = 156, H = 15, Y = 4;
  const TRACK = { x: 66, y: Y + 4, w: W - 66 - 5, h: 7 };
  const COLORS: Record<string, string> = { Buit: '#28243a', Groc: '#fad23c', Taronja: '#f69628', Vermell: '#e63228' };
  const rect = (id: string, x: number, y: number, width: number, height: number, color: string, zIndex: number) => ({
    type: 'button', id, x, y, width, height, backgroundAnchor: 'top-left', text: '', font: 'suma-regular', fontSize: 8,
    textColor: '#ffffff', backgroundTag: '', backgroundColor: color,
    backgroundColorStates: { hover: color, pressed: color, disabled: color }, zIndex,
  });
  const controls: Json[] = [
    rect('vora', 0, Y, W, H, '#f0c85a', 1),
    rect('vora2', 1, Y + 1, W - 2, H - 2, '#463a28', 2),
    rect('fons', 2, Y + 2, W - 4, H - 4, '#0e0c16', 3),
    { type: 'text', id: 'etiqueta', x: 7, y: Y, text: '', font: BOLD_FONT, fontSize: 8, color: '#f0dc8c', align: 'left', zIndex: 4 },
    rect('guia', TRACK.x - 1, TRACK.y - 1, TRACK.w + 2, TRACK.h + 2, '#786e82', 4),
  ];
  const mides = [...new Set(Object.values(PASSOS).map((p) => p.rellotge ? p.torns ?? 0 : p.limit?.max ?? 0).filter((m) => m > 0))];
  for (const n of mides) {
    const w = Math.floor((TRACK.w - (n - 1)) / n);
    const x0 = TRACK.x + Math.floor((TRACK.w - (w * n + n - 1)) / 2);
    for (let i = 0; i < n; i++) {
      for (const [nom, color] of Object.entries(COLORS)) controls.push(rect(`t${n}s${i}${nom}`, x0 + i * (w + 1), TRACK.y, w, TRACK.h, color, 5));
    }
  }
  writeJson(join(dir, 'indicador.gui.json'), {
    id: 'indicador', name: 'Indicador', description: "Els torns que queden en una sincronia (games/suma-zero/adapters/benne/joc.ts).",
    visible: false, display: { aseprite: false }, zIndex: 20, controls,
  });
  writeFileSync(join(dir, 'indicador.gui.ts'), `// Creat per games/suma-zero/adapters/benne/joc.ts: l'indicador de les sincronies. No l'editis aquí.
// La lògica és a narrative/indicador.ts (games/suma-zero/adapters/benne/runtime/).
import { onUpdate } from '@benne/script';
import { actualitzaIndicador } from '../../narrative/indicador';

onUpdate(() => actualitzaIndicador())
`);
}

const BOLD_FONT = 'suma-negreta';
