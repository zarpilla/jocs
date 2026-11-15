/**
 * Ni un ou a Benne: el que aquest joc fa diferent (vegeu adapters/benne/joc-benne.ts).
 */
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { readJson, writeJson, type Json } from '../../../../adapters/benne/benne-content.js';
import type { JocBenne } from '../../../../adapters/benne/joc-benne.js';

export default {
  nom: 'Ni un ou B',
  projecte: 'ni-un-ou',
  paquet: 'ni-un-ou-b-benne',
  fonts: { regular: 'niunou-regular', negreta: 'niunou-negreta', script: 'tools/font/niunou_font.py' },
  colorsVeu: {
    iri: '#f2b25c', vet: '#7fd8e6', bastida: '#96c8f0', capitana: '#e4e4dc', juana: '#a6e08a', nadia: '#f29ac4',
    marcel: '#e8c070', tomas: '#f4dca8', lind: '#c4a6f2', rut: '#d0d0d0', tele: '#b4b4b4', diu: '#e0e0e0',
  },
  veusProtagonistes: true,
  musicaSincronitzada: true,
  // Versió B: sense barra de verbs, pensada per al mòbil (adapters/benne/tactil). L'art del HUD i del menú d'accions:
  // tools/hd640/hud.py; les sales i les GUI a l'alçada adaptable: tools/hd640/pantalla.py (el plànol, mapa.py).
  tactil: true,
  textosGui: {
    'game-menu': { historial: 'ui.menu.historial', pista: 'ui.menu.pista' },
  },
  configura(config, t) {
    // Temps de lectura: Benne talla les línies a 4,5 s, i les llargues (en Marcel) no es poden llegir.
    // Amb un clic se salten, de manera que val més que es quedin prou estona. Els primers 500 ms d'una
    // línia, però, un clic no la salta (un doble clic no se'n menja cap sense llegir).
    config.speech = { ...(config.speech as Json), clickToSkip: true, minDurationMs: 1500, msPerCharacter: 75, maxDurationMs: 14000, clickProtectMs: 350 };
    // «Walk to» de la línia de verbs (walkToLabel).
    config.walkToLabel = t('ui.verb.walkTo', String(config.walkToLabel ?? 'Walk to'));
  },
  guis(gameDir) {
    addGameMenuButtons(gameDir);
    addHistoryGui(gameDir);
    addMapaScript(gameDir);
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
        font: 'niunou-regular', fontSize: 8, textColor: '#ffffff', backgroundTag: '', backgroundColor: '#060a14',
        backgroundColorStates: { hover: '#060a14', pressed: '#060a14', disabled: '#060a14' }, zIndex: 1,
      },
      text('titol', k(14), k(8), 'niunou-negreta', '#e8c260'),
      text('noms', k(14), k(HISTORIAL_TOP), 'niunou-negreta', '#ff963c'),
      text('linies', k(14), k(HISTORIAL_TOP), 'niunou-regular', '#e2d6b4'),
      { ...text('peu', W - k(14), H - k(15), 'niunou-regular', '#8a9aa8', 'right'), anchorY: 'bottom' },
    ],
  });
}

/** On comencen les línies de l'historial (y), i quantes n'hi caben: ho fa servir el runtime. */
const HISTORIAL_TOP = 24; // ha de coincidir amb runtime/narrative.ts (HISTORIAL_FILES)

// ─── El plànol de l'Arenga ──────────────────────────────────────────────────

/**
 * El script de la GUI `mapa` (el plànol d'emergència): cada sala del plànol, en clicar-la, hi va (o la protagonista
 * diu per què no); en passar-hi per sobre, el peu en diu el nom. La GUI i l'art els fa tools/hd640/mapa.py, i la
 * lògica és a runtime/mapa.ts i runtime/mapa.script.ts. Les sales surten dels botons de la GUI (la seva etiqueta
 * de fons és l'id de la sala).
 */
function addMapaScript(gameDir: string) {
  const dir = join(gameDir, 'guis/mapa');
  const jsonPath = join(dir, 'mapa.gui.json');
  if (!existsSync(jsonPath)) {
    console.warn('⚠ Falta la GUI del plànol: python3 adapters/benne/tools/hd640/mapa.py');
    return;
  }
  const sales = ((readJson(jsonPath).controls as Json[]) ?? [])
    .filter((c) => c.type === 'button' && typeof c.backgroundTag === 'string' && c.backgroundTag)
    .map((c) => ({ id: String(c.id), sala: String(c.backgroundTag) }));
  const handlers = sales.map(({ id, sala }) => [
    `${id}.onClick(() => viatjaAmbMapa('${sala}'))`,
    `${id}.onMouseEnter(() => peuMapa('${sala}'))`,
    `${id}.onMouseLeave(() => peuMapa(null))`,
  ].join('\n'));
  writeFileSync(join(dir, 'mapa.gui.ts'), `// Creat per games/ni-un-ou-b/adapters/benne/joc.ts: el plànol de l'Arenga. No l'editis aquí.
// La lògica és a narrative/mapa.ts i narrative/mapa.script.ts (games/ni-un-ou-b/adapters/benne/runtime/).
import { tanca, ${sales.map((s) => s.id).join(', ')} } from './mapa.ids';
import { peuMapa, tancaMapa } from '../../narrative/mapa';
import { viatjaAmbMapa } from '../../narrative/mapa.script';

tanca.onClick(() => tancaMapa())

${handlers.join('\n\n')}
`);
}
