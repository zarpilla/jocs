/**
 * `npm run benne:create -- --from <checkout de Benne> [--out joc-benne] [--force]`
 *
 * Crea el projecte Benne del joc fent el mateix que l'ordre "BENNE: Create New Game" de
 * l'extensió (benne-editor/src/gameCreationScaffolding.ts), però sense VS Code:
 *  - copia el motor, l'editor, els tipus i les configuracions d'un checkout de Benne;
 *  - copia la plantilla 9-verb, sense el contingut de demostració (sales, personatges,
 *    objectes, diàleg, música);
 *  - escriu package.json (amb les dependències del nucli i del joc), .benne-project, etc.
 *
 * No executa cap codi de Benne: només copia fitxers. Després: `npm run benne:sync -- --init`
 * i, dins del projecte, `npm install && npm run dev`.
 */
import { cpSync, existsSync, mkdirSync, readFileSync, readdirSync, rmSync, writeFileSync } from 'node:fs';
import { dirname, join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseArgs } from 'node:util';

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(HERE, '../..');

const { values } = parseArgs({
  options: {
    from: { type: 'string' },
    out: { type: 'string', default: join(ROOT, 'joc-benne') },
    template: { type: 'string', default: '9-verb' },
    force: { type: 'boolean', default: false },
  },
});

if (!values.from) {
  console.error('✖ Cal --from <camí a un checkout de https://github.com/Bennethon/benne>');
  process.exit(1);
}
const src = resolve(values.from);
const out = resolve(values.out!);
const templateDir = join(src, 'game-templates', values.template!);

if (!existsSync(join(src, 'src/engine')) || !existsSync(join(templateDir, 'game-config.json'))) {
  console.error(`✖ ${src} no sembla un checkout de Benne amb la plantilla ${values.template}.`);
  process.exit(1);
}
if (existsSync(out) && readdirSync(out).length > 0 && !values.force) {
  console.error(`✖ ${out} ja existeix i no és buit. Fes servir --force per substituir el motor (el joc no es toca).`);
  process.exit(1);
}

// ─── 1. Motor i fitxers compartits (com scripts/bundle-extension-scaffold.mjs) ─

const SHARED_DIRS = ['src/engine', 'src/editor', 'src/types', 'electron', 'scripts/lib'];
const SHARED_FILES = [
  'src/main.ts', 'src/style.css',
  'scripts/generate-game-ids.mjs', 'scripts/resolveBennePreviewOutDir.mjs', 'scripts/package-itch.mjs',
  'scripts/prepare-desktop.mjs', 'scripts/smoke-desktop.cjs', 'scripts/run-electron-test.cjs', 'scripts/test-webgl-recovery.cjs',
  'electron-builder.config.cjs',
  'vite.config.ts', 'vite.room-preview.config.ts', 'vite.character-preview.config.ts', 'vite.gui-preview.config.ts',
  'vite.inventory-preview.config.ts', 'vite.benne-play.config.ts', 'vite-plugin-bennegame-ids.ts', 'vite-plugin-bennescript.ts',
  'tsconfig.json', 'index.html', 'room-editor.html', 'character-editor.html', 'gui-editor.html', 'inventory-editor.html',
  'benne-play.html', '.claude/skills/bennescript/SKILL.md', '.agents/skills/bennescript/SKILL.md',
];

mkdirSync(out, { recursive: true });
for (const dir of SHARED_DIRS) {
  rmSync(join(out, dir), { recursive: true, force: true });
  cpSync(join(src, dir), join(out, dir), { recursive: true });
}
for (const file of SHARED_FILES) {
  if (!existsSync(join(src, file))) continue;
  mkdirSync(dirname(join(out, file)), { recursive: true });
  cpSync(join(src, file), join(out, file));
}

// ─── 2. La plantilla, sense la demo (només si el joc encara no existeix) ─────

const gameDir = join(out, 'src/game');
const DEMO = [
  'rooms/apartment', 'rooms/outside', 'characters/hank', 'characters/penny', 'characters/henry',
  'inventory', 'dialogs/chatwithpenny', 'pdcs/demo',
  'assets/images/rooms', 'assets/images/characters', 'assets/images/inventory', 'assets/audio',
];
if (!existsSync(join(gameDir, 'game-config.json'))) {
  cpSync(templateDir, gameDir, {
    recursive: true,
    filter: (path) => {
      const rel = relative(templateDir, path).split('\\').join('/');
      return !DEMO.some((d) => rel === d || rel.startsWith(`${d}/`)) && !rel.endsWith('.gitkeep');
    },
  });
  for (const d of ['rooms', 'characters', 'inventory', 'dialogs', 'assets/audio/sfx', 'assets/audio/music', 'assets/images/rooms', 'assets/images/characters', 'assets/images/inventory']) {
    mkdirSync(join(gameDir, d), { recursive: true });
  }
  for (const d of ['assets/audio/sfx', 'assets/audio/music']) writeFileSync(join(gameDir, d, '.gitkeep'), '');
  writeFileSync(join(gameDir, 'rooms/rooms.manifest.json'), JSON.stringify({ startRoomId: '', rooms: [] }, null, 2) + '\n');
  writeFileSync(join(gameDir, 'state.ts'), `/**
 * Flags i variables de Benne. Els del joc són a game/data/state.json (nucli narratiu):
 * aquí només hi ha el que faci falta per a scripts propis de Benne.
 */
import { defineFlags, defineVars } from '@benne/script';

export const flags = defineFlags({});

export const vars = defineVars({});
`);
  console.log(`✔ Plantilla ${values.template} copiada (sense la demo)`);
} else {
  console.log(`· src/game ja existeix: només s'ha actualitzat el motor`);
}

// ─── 3. package.json i fitxers del projecte (com gameCreationScaffolding.ts) ─

const pkgPath = join(out, 'package.json');
const existing = existsSync(pkgPath) ? JSON.parse(readFileSync(pkgPath, 'utf8')) : {};
const pkg = {
  name: 'ferro9-benne',
  private: true,
  version: '0.0.0',
  type: 'module',
  main: 'electron/main.cjs',
  benne: { displayName: 'Ferro-9' },
  ...existing,
  scripts: {
    'generate:game-ids': 'node scripts/generate-game-ids.mjs',
    predev: 'npm run generate:game-ids',
    dev: 'vite',
    prebuild: 'npm run generate:game-ids',
    build: 'tsc && vite build',
    'build:itch': 'npm run build && node scripts/package-itch.mjs',
    desktop: 'npm run build && electron .',
    'build:windows': 'npm run build && node scripts/prepare-desktop.mjs && electron-builder --config electron-builder.config.cjs --win --x64',
    'prebuild:room-preview': 'npm run generate:game-ids',
    'build:room-preview': 'tsc && vite build --config vite.room-preview.config.ts',
    'prebuild:character-preview': 'npm run generate:game-ids',
    'build:character-preview': 'tsc && vite build --config vite.character-preview.config.ts',
    'prebuild:gui-preview': 'npm run generate:game-ids',
    'build:gui-preview': 'tsc && vite build --config vite.gui-preview.config.ts',
    'prebuild:inventory-preview': 'npm run generate:game-ids',
    'build:inventory-preview': 'tsc && vite build --config vite.inventory-preview.config.ts',
    'prebuild:benne-play': 'npm run generate:game-ids',
    'build:benne-play': 'tsc && vite build --config vite.benne-play.config.ts',
    preview: 'vite preview',
    ...existing.scripts,
  },
  // Versions de benne-editor/src/scaffoldPayload.ts
  devDependencies: {
    electron: '^44.4.5',
    'electron-builder': '^26.15.3',
    eslint: '^10.12.0',
    'magic-string': '^1.4.2',
    'png-to-ico': '^3.0.2',
    pngjs: '^7.0.0',
    typescript: '~5.9.3',
    'typescript-eslint': '^8.71.0',
    vite: '^8.0.1',
    ...existing.devDependencies,
  },
  dependencies: {
    phaser: '4.0.0-rc.7',
    '@aventura/narrative-core': 'file:../packages/narrative-core',
    '@aventura/game': 'file:../game',
    ...existing.dependencies,
  },
};
writeFileSync(pkgPath, JSON.stringify(pkg, null, 2) + '\n');

const benneVersion = JSON.parse(readFileSync(join(src, 'benne-editor/package.json'), 'utf8')).version;
writeFileSync(join(out, '.benne-project'), JSON.stringify({
  scaffoldVersion: benneVersion,
  extensionVersion: benneVersion,
  templateId: values.template,
  projectName: 'ferro9-benne',
  createdAt: new Date().toISOString(),
  createdBy: 'adapters/benne/create-project.ts',
}, null, 2) + '\n');
writeFileSync(join(out, 'eslint.config.mjs'), `// ESLint del joc (npm run lint). Les regles de BenneScript són a scripts/lib/.
import tseslint from 'typescript-eslint';
import { gameScriptsConfig } from './scripts/lib/eslint-plugin-bennescript.mjs';

export default [gameScriptsConfig({ parser: tseslint.parser, tsconfigRootDir: import.meta.dirname })];
`);
writeFileSync(join(out, '.gitignore'), 'node_modules/\ndist/\n.benne/\nreleases/\n\n# Generats per Benne (npm run generate:game-ids)\nsrc/game/**/*.ids.ts\n');
mkdirSync(join(out, '.vscode'), { recursive: true });
writeFileSync(join(out, '.vscode/settings.json'), JSON.stringify({ 'typescript.tsc.autoDetect': 'off' }, null, 2) + '\n');
writeFileSync(join(out, 'README.md'), `# Ferro-9 · projecte Benne

Projecte de [Benne](https://benne.games/) del joc. **La història no és aquí**: és a \`../game/\`.
Aquí hi ha el motor (\`src/engine\`, no es toca), l'art, i el que genera \`npm run benne:sync\`
des de l'arrel del repositori.

\`\`\`bash
npm install      # la primera vegada
npm run dev      # juga al navegador
\`\`\`

Motor copiat de Benne ${benneVersion} (plantilla ${values.template}) amb \`npm run benne:create\`.
`);

console.log(`✔ Projecte Benne a ${relative(ROOT, out) || out} (motor de Benne ${benneVersion})`);
console.log(`  Ara: npm run benne:sync -- --init   i després   cd ${relative(ROOT, out)} && npm install && npm run dev`);
