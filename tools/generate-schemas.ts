/**
 * `npm run schemas`: genera `game/schemas/*.schema.json` a partir dels tipus
 * TypeScript del nucli. Així els JSON tenen autocompletat i errors a VS Code,
 * i `npm run validate` els comprova.
 */
import { writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { gameDir } from './joc.js';
import { createGenerator } from 'ts-json-schema-generator';

/** Fitxers que són un sol objecte. */
const single: Record<string, string> = { game: 'GameFile', state: 'StateFile', dialogue: 'DialogueFile', room: 'RoomFile' };
/** Fitxers que són una taula `id → definició`. */
const tables: Record<string, string> = {
  characters: 'CharacterDef',
  items: 'ItemDef',
  quests: 'QuestDef',
  hints: 'HintDef',
  endings: 'EndingDef',
};

const generator = createGenerator({
  path: fileURLToPath(new URL('./schema-files.ts', import.meta.url)),
  tsconfig: fileURLToPath(new URL('../tsconfig.json', import.meta.url)),
  skipTypeCheck: true,
  additionalProperties: false,
});

const ID = '^[a-z][a-z0-9_]*$';

function write(name: string, schema: object) {
  const out = join(gameDir(), 'schemas', `${name}.schema.json`);
  writeFileSync(out, JSON.stringify(schema, null, 2) + '\n');
  console.log(`✔ game/schemas/${name}.schema.json`);
}

for (const [name, type] of Object.entries(single)) write(name, generator.createSchema(type));

for (const [name, type] of Object.entries(tables)) {
  const schema = generator.createSchema(type);
  write(name, {
    $schema: schema.$schema,
    definitions: schema.definitions,
    type: 'object',
    properties: { $schema: { type: 'string' } },
    patternProperties: { [ID]: { $ref: `#/definitions/${type}` } },
    additionalProperties: false,
  });
}

write('locale', {
  $schema: 'http://json-schema.org/draft-07/schema#',
  type: 'object',
  properties: { $schema: { type: 'string' } },
  patternProperties: { '^[a-zA-Z0-9_]+(\\.[a-zA-Z0-9_]+)+$': { type: 'string' } },
  additionalProperties: false,
});
