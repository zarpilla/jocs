/**
 * `npm run validate`: comprova que el contingut del joc és coherent
 * (referències, identificadors, textos traduïts). Surt amb codi 1 si hi ha errors.
 */
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { Ajv } from 'ajv';
import { assembleGame, validateContent, type ValidationIssue } from '@aventura/narrative-core';
import { gameDir, loadGameLogic } from './joc.js';
import { gameDuplicateKeys, gameSounds, readGameFiles } from './load-game.js';

const { GAME_ACTIONS, gameTextKeys } = await loadGameLogic();

const files = readGameFiles();

// 1. Forma de cada fitxer (JSON Schema).
const ajv = new Ajv({ allErrors: true, strict: false });
const schemaFor = (path: string) => {
  if (path.startsWith('locales/')) return 'locale';
  if (path.startsWith('data/dialogues/')) return 'dialogue';
  if (path.startsWith('data/rooms/')) return 'room';
  return path.match(/^data\/(\w+)\.json$/)?.[1];
};
const shapeIssues: ValidationIssue[] = [];
for (const [path, json] of Object.entries(files)) {
  const name = schemaFor(path);
  if (!name) continue;
  const schema = JSON.parse(readFileSync(join(gameDir(), 'schemas', `${name}.schema.json`), 'utf8'));
  const check = ajv.compile(schema);
  if (!check(json)) {
    for (const e of check.errors ?? []) {
      shapeIssues.push({ level: 'error', where: `game/${path}${e.instancePath}`, message: `${e.message} ${JSON.stringify(e.params)}` });
    }
  }
}

// Claus repetides: el JSON es queda amb l'última i l'altra desapareix sense avís.
for (const [path, keys] of Object.entries(gameDuplicateKeys())) {
  for (const k of keys) shapeIssues.push({ level: 'error', where: `game/${path}`, message: `clau repetida: «${k}» (només compta l'última)` });
}

// 2. Coherència del contingut (només si la forma és correcta).
const { content, locales } = assembleGame(files);
const issues = shapeIssues.length ? shapeIssues : validateContent(content, locales, { actions: GAME_ACTIONS, textKeys: gameTextKeys(content), sounds: gameSounds() });
const errors = issues.filter((i) => i.level === 'error');
const warnings = issues.filter((i) => i.level === 'warning');

for (const i of [...errors, ...warnings]) {
  console.log(`${i.level === 'error' ? '✖' : '⚠'} ${i.where}: ${i.message}`);
}

const count = (o: object) => Object.keys(o).length;
console.log(
  `\n${count(content.dialogues)} diàlegs, ${count(content.characters)} personatges, ${count(content.quests)} missions, ` +
    `${count(content.hints)} pistes, ${count(content.endings)} finals, idiomes: ${Object.keys(locales).join(', ')}`,
);
console.log(errors.length ? `✖ ${errors.length} errors, ${warnings.length} avisos` : `✔ Cap error (${warnings.length} avisos)`);
process.exit(errors.length ? 1 : 0);
