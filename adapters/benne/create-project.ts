/**
 * `npm run benne:create -- --from <checkout de Benne> [--motor] [--out <carpeta>] [--force]`
 * (des de games/<joc>/, o `-w <joc>` des de l'arrel)
 *
 * Crea el projecte Benne del joc fent el mateix que l'ordre "BENNE: Create New Game" de
 * l'extensió (benne-editor/src/gameCreationScaffolding.ts), però sense VS Code:
 *  - copia la plantilla 9-verb, sense el contingut de demostració (sales, personatges,
 *    objectes, diàleg, música), amb les fonts del joc i a 480×270;
 *  - escriu package.json (amb les dependències del nucli i del joc), .benne-project, etc.;
 *  - hi copia el motor compartit (packages/benne, `npm run motor`).
 *
 * Amb `--motor`, a més, **actualitza el motor compartit** (packages/benne) des del checkout de Benne
 * i hi aplica els pegats propis (patches/motor-benne.patch, tots els canvis nostres; `npm run benne:pegat` el refà).
 * Afecta tots els jocs: revisa el diff abans de fer-ne commit.
 *
 * No executa cap codi de Benne: només copia fitxers. Després: `npm run benne:sync -- --init`
 * i, dins del projecte, `npm install && npm run dev`.
 */
import { cpSync, existsSync, mkdirSync, readFileSync, readdirSync, rmSync, writeFileSync } from 'node:fs';
import { dirname, join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseArgs } from 'node:util';
import { spawnSync } from 'node:child_process';
import { jocAdapterDir, loadJocBenne } from './joc-benne.js';
import { SHARED_DIRS, SHARED_FILES } from './motor-paths.js';
import { ROOT, jocDir } from '../../tools/joc.js';

const HERE = dirname(fileURLToPath(import.meta.url));
const MOTOR = join(ROOT, 'packages/benne');
const joc = await loadJocBenne();

const { values } = parseArgs({
  options: {
    from: { type: 'string' },
    out: { type: 'string', default: join(jocDir(), joc.projecte) },
    template: { type: 'string', default: '9-verb' },
    motor: { type: 'boolean', default: false },
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
if (existsSync(join(out, 'src/game/game-config.json')) && !values.force && !values.motor) {
  console.error(`✖ ${out} ja té un joc. Per actualitzar el motor compartit, fes servir --motor.`);
  process.exit(1);
}
const benneVersion = JSON.parse(readFileSync(join(src, 'benne-editor/package.json'), 'utf8')).version;

// ─── 1. Motor compartit (només amb --motor; com scripts/bundle-extension-scaffold.mjs) ─

if (values.motor) {
  for (const dir of SHARED_DIRS) {
    rmSync(join(MOTOR, dir), { recursive: true, force: true });
    cpSync(join(src, dir), join(MOTOR, dir), { recursive: true });
  }
  for (const file of SHARED_FILES) {
    if (!existsSync(join(src, file))) continue;
    mkdirSync(dirname(join(MOTOR, file)), { recursive: true });
    cpSync(join(src, file), join(MOTOR, file));
  }
  // Pegats propis al motor (vegeu README.md): s'apliquen sobre el motor acabat de copiar.
  const patch = join(HERE, 'patches/motor-benne.patch');
  const applied = spawnSync('patch', ['-p0', '--forward', '--batch', '-i', patch], { cwd: MOTOR, stdio: 'inherit' });
  if (applied.status !== 0) {
    console.error(`✖ El pegat ${relative(ROOT, patch)} no s'aplica net sobre aquest Benne: revisa'l.`);
    process.exit(1);
  }
  console.log(`✔ Motor compartit actualitzat a Benne ${benneVersion} i pegats aplicats: revisa \`git diff packages/benne\``);
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
  replaceTemplateFonts(gameDir);
  // La plantilla és de 352×198: el joc és a 480×270 des del primer dia (game-config, GUI i imatges de GUI).
  const migra = spawnSync('python3', [join(jocAdapterDir(), 'tools/migra_resolucio.py'), gameDir], { stdio: 'inherit' });
  if (migra.status !== 0) {
    console.error('✖ No s\'ha pogut passar la plantilla a 480×270 (tools/migra_resolucio.py)');
    process.exit(1);
  }
  console.log(`✔ Plantilla ${values.template} copiada (sense la demo)`);

  // ─── 3. package.json i fitxers del projecte (com gameCreationScaffolding.ts) ─
  // Els scripts i les dependències del motor els posa `npm run motor` (packages/benne/package.base.json).
  const pkgPath = join(out, 'package.json');
  const existing = existsSync(pkgPath) ? JSON.parse(readFileSync(pkgPath, 'utf8')) : {};
  writeFileSync(pkgPath, JSON.stringify({
    name: joc.paquet,
    private: true,
    version: '0.0.0',
    benne: { displayName: joc.nom },
    ...existing,
    dependencies: {
      '@aventura/narrative-core': `file:${relative(out, join(ROOT, 'packages/narrative-core'))}`,
      '@aventura/game': `file:${relative(out, join(jocDir(), 'game'))}`,
      ...existing.dependencies,
    },
  }, null, 2) + '\n');
  writeFileSync(join(out, '.benne-project'), JSON.stringify({
    scaffoldVersion: benneVersion,
    extensionVersion: benneVersion,
    templateId: values.template,
    projectName: joc.paquet,
    createdAt: new Date().toISOString(),
    createdBy: 'adapters/benne/create-project.ts',
  }, null, 2) + '\n');
  writeFileSync(join(out, '.gitignore'), 'node_modules/\ndist/\n.benne/\nreleases/\n\n# Generats per Benne (npm run generate:game-ids)\nsrc/game/**/*.ids.ts\n');
  writeFileSync(join(out, 'README.md'), `# ${joc.nom} · projecte Benne

Projecte de [Benne](https://benne.games/) del joc. **La història no és aquí**: és a \`../game/\`.
Aquí hi ha l'art i el que genera \`npm run benne:sync\`. El motor (\`src/engine\`, \`scripts/\`,
\`electron/\`...) és una còpia de només lectura de \`packages/benne\`, que fa \`npm run motor\`
(sol, abans de \`dev\` i \`build\`): el motor s'edita allà, i val per a tots els jocs.

\`\`\`bash
npm install      # la primera vegada
npm run dev      # juga al navegador
\`\`\`

Plantilla ${values.template} de Benne ${benneVersion}, copiada amb \`npm run benne:create\`.
`);

  // Llicències: el joc amb tots els drets reservats i els avisos MIT de Benne i Phaser. Va a public/,
  // perquè Vite el copiï a dist/ (i d'aquí al zip d'itch.io i a la versió d'escriptori).
  const llicencies = join(jocDir(), 'LLICENCIES.txt');
  if (existsSync(llicencies)) {
    mkdirSync(join(out, 'public'), { recursive: true });
    cpSync(llicencies, join(out, 'public/LLICENCIES.txt'));
  }
} else {
  console.log(`· src/game ja existeix: el joc no es toca`);
}

// ─── 4. El motor compartit, copiat al projecte ───────────────────────────────

const copia = spawnSync('node', [join(MOTOR, 'copia.mjs')], { cwd: out, stdio: 'inherit' });
if (copia.status !== 0) process.exit(1);

console.log(`✔ Projecte Benne a ${relative(ROOT, out) || out}`);
console.log(`  Ara: npm run benne:sync -- --init   i després   cd ${relative(process.cwd(), out)} && npm install && npm run dev`);

/**
 * Les fonts de la plantilla (LucasArts, Sierra...) tenen llicència no comercial: es treuen i les GUI
 * passen a les fonts del joc (`fonts` al seu joc.ts): negreta per als verbs i el que diuen els
 * personatges; regular per a la línia d'acció, els menús i les caixes de text.
 */
function replaceTemplateFonts(gameDir: string) {
  const FONTS: Record<string, string> = { 'lucasarts-scumm-solid': joc.fonts.negreta, 'lucasfont-alternate': joc.fonts.regular };
  const fontsDir = join(gameDir, 'assets/fonts');
  for (const f of readdirSync(fontsDir)) {
    if (f !== 'BENNE bitmap font export.bmfc') rmSync(join(fontsDir, f));
  }
  const fonts = Object.fromEntries([joc.fonts.regular, joc.fonts.negreta].map((id) => [id, { textureFile: `${id}_0.png`, dataFile: `${id}.xml` }]));
  writeFileSync(join(fontsDir, 'fonts.json'), JSON.stringify(fonts, null, 2) + '\n');
  const walk = (dir: string): string[] =>
    readdirSync(dir, { withFileTypes: true }).flatMap((e) => (e.isDirectory() ? walk(join(dir, e.name)) : e.name.endsWith('.json') ? [join(dir, e.name)] : []));
  for (const file of walk(gameDir)) {
    const text = readFileSync(file, 'utf8');
    const next = text.replace(/"font": *"([^"]+)"/g, (m, id: string) => (FONTS[id] ? `"font": "${FONTS[id]}"` : m));
    if (next !== text) writeFileSync(file, next);
  }
  const font = spawnSync('python3', [join(jocDir(), joc.fonts.script), fontsDir], { stdio: 'inherit' });
  if (font.status !== 0) console.error('✖ No s\'ha pogut generar la font (npm run font)');
}
