/**
 * `npm run validate`: comprova que el contingut del joc és coherent
 * (referències, identificadors, textos traduïts). Surt amb codi 1 si hi ha errors.
 */
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { Ajv } from 'ajv';
import { validateContent, type ValidationIssue } from '@aventura/narrative-core';
import { assembleGame } from '../game/assemble.js';
import { GAME_DIR, readGameFiles } from './load-game.js';

const files = readGameFiles();

// 1. Forma de cada fitxer (JSON Schema).
const ajv = new Ajv({ allErrors: true, strict: false });
const schemaFor = (path: string) => {
  if (path.startsWith('locales/')) return 'locale';
  if (path.startsWith('data/dialogues/')) return 'dialogue';
  return path.match(/^data\/(\w+)\.json$/)?.[1];
};
const shapeIssues: ValidationIssue[] = [];
for (const [path, json] of Object.entries(files)) {
  const name = schemaFor(path);
  if (!name) continue;
  const schema = JSON.parse(readFileSync(join(GAME_DIR, 'schemas', `${name}.schema.json`), 'utf8'));
  const check = ajv.compile(schema);
  if (!check(json)) {
    for (const e of check.errors ?? []) {
      shapeIssues.push({ level: 'error', where: `game/${path}${e.instancePath}`, message: `${e.message} ${JSON.stringify(e.params)}` });
    }
  }
}

// 2. Coherència del contingut (només si la forma és correcta).
const { content, locales } = assembleGame(files);
const issues = shapeIssues.length ? shapeIssues : validateContent(content, locales);
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
