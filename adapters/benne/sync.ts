/**
 * `npm run benne:sync -- --project ../joc-benne [--locale ca] [--watch]`
 *
 * Porta el contingut del joc a un projecte Benne:
 *  1. Valida el contingut (si hi ha errors, no escriu res).
 *  2. Copia el pont (runtime/) a `src/game/narrative/`.
 *  3. Empaqueta dades + textos a `src/game/narrative/content.generated.json`.
 *  4. Genera un diàleg de Benne per cada diàleg nostre (`src/game/dialogs/<id>/`).
 *
 * Tot el que escriu porta la marca GENERAT. Mai no sobreescriu fitxers sense marca.
 */
import { existsSync, mkdirSync, readFileSync, readdirSync, watch, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseArgs } from 'node:util';
import { validateContent, type DialogueDef, type GameContent, type LocaleTable } from '@aventura/narrative-core';
import { GAME_DIR, loadGameFromDisk } from '../../tools/load-game.js';

const HERE = dirname(fileURLToPath(import.meta.url));
const MARK = 'GENERAT per adapters/benne/sync.ts';

const { values } = parseArgs({
  options: {
    project: { type: 'string', default: process.env.BENNE_PROJECT ?? join(HERE, '../../joc-benne') },
    locale: { type: 'string' },
    watch: { type: 'boolean', default: false },
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
  const errors = validateContent(content, locales).filter((i) => i.level === 'error');
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

  // 3. Diàlegs
  for (const d of Object.values(content.dialogues)) {
    const dir = join(gameDir, 'dialogs', d.id);
    const script = join(dir, `${d.id}.dialog.ts`);
    writeGenerated(join(dir, `${d.id}.dialog.json`), json(benneDialog(d, table, fallback), false), 'json', script);
    writeGenerated(script, benneDialogScript(d), 'ts');
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
