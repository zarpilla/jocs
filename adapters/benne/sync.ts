/**
 * `npm run benne:sync -- --project ../ferro-9 [--locale ca] [--watch]`
 *
 * Porta el contingut del joc a un projecte Benne:
 *  1. Valida el contingut (si hi ha errors, no escriu res).
 *  2. Copia el pont (runtime/) a `src/game/narrative/`, i els sons de `game/audio/sfx/` als de Benne.
 *  3. Empaqueta dades + textos a `src/game/narrative/content.generated.json`.
 *  4. Genera un diàleg de Benne per cada diàleg nostre (`src/game/dialogs/<id>/`).
 *
 *  5. Genera a Benne les sales, personatges i objectes que hi falten (amb art provisional),
 *     i posa tots els textos de Benne (verbs, menús, noms) en l'idioma triat.
 *  6. Amb `--init`, instal·la `globalScript.ts` (encamina les interaccions cap al JSON).
 *
 * Tot el que escriu porta la marca GENERAT. Mai no sobreescriu fitxers sense marca
 * (llevat de `--init`, que abans en fa una còpia `.bak`).
 */
import { spawnSync } from 'node:child_process';
import { copyFileSync, existsSync, mkdirSync, readFileSync, readdirSync, watch, writeFileSync } from 'node:fs';
import { basename, dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseArgs } from 'node:util';
import { validateContent, type DialogueDef, type GameContent, type LocaleTable } from '@aventura/narrative-core';
import { GAME_ACTIONS, GAME_TEXT_KEYS } from '../../game/logic/index.js';
import { writeBenneContent } from './benne-content.js';
import { GAME_DIR, gameSoundFiles, gameSounds, loadGameFromDisk } from '../../tools/load-game.js';

const HERE = dirname(fileURLToPath(import.meta.url));
const MARK = 'GENERAT per adapters/benne/sync.ts';

const { values } = parseArgs({
  options: {
    project: { type: 'string', default: process.env.BENNE_PROJECT ?? join(HERE, '../../ferro-9') },
    locale: { type: 'string' },
    watch: { type: 'boolean', default: false },
    /** Substitueix el globalScript.ts de Benne pel de l'adaptador (en fa còpia de seguretat). */
    init: { type: 'boolean', default: false },
  },
});

const project = resolve(values.project!);
const gameDir = join(project, 'src/game');

/** `owner`: fitxer que porta la marca (per als JSON de Benne, que no admeten comentaris). */
function writeGenerated(path: string, body: string, kind: 'ts' | 'json', owner = path) {
  if (existsSync(path) && (!existsSync(owner) || !readFileSync(owner, 'utf8').includes(MARK))) {
    throw new Error(`No sobreescric ${path}: no és un fitxer generat. Mou-lo o esborra'l primer.`);
  }
  mkdirSync(dirname(path), { recursive: true });
  if (kind === 'ts') body = `// ${MARK}. No l'editis aquí.\n${body}`;
  writeFileSync(path, body);
}

const json = (value: object, mark = true) =>
  JSON.stringify(mark ? { $comment: MARK, ...value } : value, null, 2) + '\n';

function benneDialog(d: DialogueDef, text: LocaleTable, fallback: LocaleTable) {
  const options = Object.entries(d.nodes).flatMap(([node, n]) =>
    (n.choices ?? []).map((c) => ({
      id: `${node}__${c.id}`,
      scriptName: `${node}__${c.id}`,
      text: text[c.text] ?? fallback[c.text] ?? c.text,
      enabled: false,
      say: false, // la frase del jugador la diu el pont, en l'idioma actiu
    })),
  );
  return { id: d.id, displayName: d.id, options };
}

function benneDialogScript(d: DialogueDef) {
  const handlers = Object.entries(d.nodes).flatMap(([node, n]) =>
    (n.choices ?? []).map(
      (c) => `options.${node}__${c.id}.onChoose(() => {\n  chooseNarrativeOption('${d.id}', dialog, '${node}', '${c.id}')\n})`,
    ),
  );
  return `import { dialog, options } from './${d.id}.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('${d.id}', dialog)
})

${handlers.join('\n\n')}
`;
}

function sync() {
  if (!existsSync(join(gameDir, 'game-config.json'))) {
    throw new Error(`${project} no sembla un projecte Benne (falta src/game/game-config.json).`);
  }
  const { content, locales } = loadGameFromDisk();
  const errors = validateContent(content, locales, { actions: GAME_ACTIONS, textKeys: GAME_TEXT_KEYS, sounds: gameSounds() }).filter((i) => i.level === 'error');
  if (errors.length) {
    for (const e of errors) console.error(`✖ ${e.where}: ${e.message}`);
    throw new Error(`El contingut té ${errors.length} errors. Arregla'ls (npm run validate) abans de sincronitzar.`);
  }
  const locale = values.locale ?? content.manifest.defaultLocale;
  const table = locales[locale];
  if (!table) throw new Error(`No hi ha textos per a "${locale}".`);
  const fallback = locales[content.manifest.defaultLocale]!;

  // 1. Pont
  const narrativeDir = join(gameDir, 'narrative');
  for (const file of readdirSync(join(HERE, 'runtime'))) {
    writeGenerated(join(narrativeDir, file), readFileSync(join(HERE, 'runtime', file), 'utf8'), 'ts');
  }
  const { $comment: _c, ...mapping } = JSON.parse(readFileSync(join(HERE, 'mapping.json'), 'utf8'));
  writeGenerated(join(narrativeDir, 'mapping.generated.json'), json(mapping), 'json');

  // 2. Contingut
  const bundle: { content: GameContent; locales: Record<string, LocaleTable>; locale: string } = { content, locales, locale };
  writeGenerated(join(narrativeDir, 'content.generated.json'), json(bundle), 'json');

  // 2b. Sons: els de `game/audio/sfx/` van a `assets/audio/sfx/` (Benne els carrega tots en arrencar).
  const sfxDir = join(gameDir, 'assets/audio/sfx');
  mkdirSync(sfxDir, { recursive: true });
  for (const file of gameSoundFiles()) copyFileSync(file, join(sfxDir, basename(file)));

  // 3. Diàlegs
  for (const d of Object.values(content.dialogues)) {
    const dir = join(gameDir, 'dialogs', d.id);
    const script = join(dir, `${d.id}.dialog.ts`);
    writeGenerated(join(dir, `${d.id}.dialog.json`), json(benneDialog(d, table, fallback), false), 'json', script);
    writeGenerated(script, benneDialogScript(d), 'ts');
  }

  // 4. Sales, personatges, objectes, configuració i GUI de Benne
  const report = writeBenneContent(gameDir, content, table, fallback);
  for (const c of report.created) console.log(`  + ${c}`);
  if (report.needsArt.length) {
    const draw = spawnSync('python3', [join(HERE, 'tools/draw_placeholders.py'), gameDir], { stdio: 'inherit' });
    if (draw.error) {
      console.warn(`⚠ No s'ha pogut dibuixar l'art provisional (cal python3 amb Pillow). Falta: ${report.needsArt.join(', ')}`);
    } else if (draw.status !== 0) {
      // Un error de Python en dibuixar (p. ex. a room_designs.py) no pot passar per un sync correcte.
      throw new Error(`L'art provisional ha fallat (draw_placeholders.py, codi ${draw.status}): mira l'error de Python de més amunt.`);
    }
  }

  // 5. globalScript.ts: el bloc generat es regenera sempre; el que hi hagi a sota es conserva.
  const global = join(gameDir, 'globalScript.ts');
  const BEGIN = `// ── ${MARK}: inici. No l'editis. ──`;
  const END = `// ── ${MARK}: fi. Pots afegir codi a sota. ──`;
  const block = `${BEGIN}\n${readFileSync(join(HERE, 'templates/globalScript.ts'), 'utf8').trimEnd()}\n${END}\n`;
  const current = existsSync(global) ? readFileSync(global, 'utf8') : '';
  if (current.includes(BEGIN) && current.includes(END)) {
    writeFileSync(global, block + current.slice(current.indexOf(END) + END.length).replace(/^\n/, ''));
  } else if (values.init || current.includes(MARK)) {
    if (current && !current.includes(MARK)) {
      copyFileSync(global, `${global}.bak`);
      console.log(`  (còpia de l'antic globalScript.ts a globalScript.ts.bak)`);
    }
    writeFileSync(global, block);
  } else {
    console.warn(`⚠ globalScript.ts encara no encamina les interaccions cap al JSON. Executa una vegada amb --init.`);
  }

  console.log(`✔ Sincronitzat amb ${project} (${Object.keys(content.dialogues).length} diàlegs, idioma de les llistes: ${locale})`);
}

try {
  sync();
} catch (e) {
  console.error(`✖ ${(e as Error).message}`);
  if (!values.watch) process.exit(1);
}

if (values.watch) {
  console.log(`Vigilant ${GAME_DIR} …`);
  let timer: NodeJS.Timeout | undefined;
  watch(GAME_DIR, { recursive: true }, () => {
    clearTimeout(timer);
    timer = setTimeout(() => {
      try {
        sync();
      } catch (e) {
        console.error(`✖ ${(e as Error).message}`);
      }
    }, 200);
  });
}
