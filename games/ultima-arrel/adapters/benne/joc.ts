/**
 * L'Última Arrel a Benne: el que aquest joc fa diferent (vegeu adapters/benne/joc-benne.ts). De moment, el mateix
 * que Aigua Verne (sense barra de verbs, pantalla adaptable), amb les fonts i els colors propis.
 *
 * Sense botó «Canvia»: una escena, una germana. No es configura aquí sinó amb `switchWhen` a game/data/game.json
 * (una condició que no es compleix mai), i el pont amaga el botó del HUD.
 */
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { readJson, writeJson, type Json } from '../../../../adapters/benne/benne-content.js';
import type { JocBenne } from '../../../../adapters/benne/joc-benne.js';

export default {
  nom: "L'Última Arrel",
  projecte: 'ultima-arrel',
  paquet: 'ultima-arrel-benne',
  fonts: { regular: 'ultimaarrel-regular', negreta: 'ultimaarrel-negreta', script: 'tools/font/ultimaarrel_font.py' },
  colorsVeu: {
    iri: '#f2a65c', vet: '#7fd8e6', avia: '#e8d8a8', espora: '#5ee0c8', urtica: '#a6e08a', pica: '#f090c0',
    card: '#c0d0f0', bufo: '#c8b070', gripau: '#a0c070', pla: '#ffffff', txell: '#f09080',
  },
  // La Vet parla pel walkie a les sales de l'Iri (i a l'inrevés).
  veusProtagonistes: true,
  // Sense barra de verbs, pensat també per al mòbil (adapters/benne/tactil). L'art del HUD i del menú d'accions:
  // tools/hd640/hud.py; les sales i les GUI a l'alçada adaptable: tools/hd640/pantalla.py.
  tactil: true,
  // Totes les peces de música duren el mateix (tools/musica.py): en canviar de sala, la nova continua al mateix punt.
  musicaSincronitzada: true,
  // No es pot canviar de germana: el botó «Canvia» del HUD és la lupa (la pista, amb els filaments).
  botoPista: true,
  textosGui: {
    'game-menu': { historial: 'ui.menu.historial', pista: 'ui.menu.pista' },
  },
  configura(config, t) {
    // Temps de lectura: Benne talla les línies a 4,5 s. Amb un clic se salten, de manera que val més que es quedin
    // prou estona. Els primers 350 ms d'una línia, però, un clic no la salta.
    config.speech = { ...(config.speech as Json), clickToSkip: true, minDurationMs: 2200, msPerCharacter: 75, maxDurationMs: 14000, clickProtectMs: 350 };
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
      const own = names.split(',').map((n) => n.trim()).filter((n) => n && !['canviar', 'historial', 'pista', 'quit'].includes(n));
      return `import { ${[...own, 'historial', 'pista', 'quit'].join(', ')} } from './game-menu.ids';
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

// «Surt»: a l'escriptori tanca l'aplicació; al navegador torna a l'arrel del web (els jocs viuen a malaherbasoft.cat/<joc>/).
quit.onClick(() => {
  if (game.isDesktop) game.quit()
  else window.location.href = '/'
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
        font: 'ultimaarrel-regular', fontSize: 8, textColor: '#ffffff', backgroundTag: '', backgroundColor: '#060a14',
        backgroundColorStates: { hover: '#060a14', pressed: '#060a14', disabled: '#060a14' }, zIndex: 1,
      },
      text('titol', k(14), k(8), 'ultimaarrel-negreta', '#e8c260'),
      text('noms', k(14), k(HISTORIAL_TOP), 'ultimaarrel-negreta', '#ff963c'),
      text('linies', k(14), k(HISTORIAL_TOP), 'ultimaarrel-regular', '#e2d6b4'),
      { ...text('peu', W - k(14), H - k(15), 'ultimaarrel-regular', '#8a9aa8', 'right'), anchorY: 'bottom' },
    ],
  });
}

/** On comencen les línies de l'historial (y), i quantes n'hi caben: ho fa servir el runtime. */
const HISTORIAL_TOP = 24; // ha de coincidir amb runtime/narrative.ts (HISTORIAL_FILES)
