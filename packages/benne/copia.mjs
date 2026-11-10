#!/usr/bin/env node
/**
 * `npm run motor` (des del projecte Benne d'un joc, p. ex. games/suma-zero/suma-zero/)
 *
 * El motor de Benne és un de sol, aquí a packages/benne/. Cada joc en té una còpia dins el seu
 * projecte Benne perquè Vite, tsc, Electron i l'extensió de VS Code el trobin on l'esperen
 * (src/engine, scripts/, electron/...). Aquesta ordre fa la còpia:
 *
 *  - copia tots els fitxers de packages/benne/ (menys els d'aquesta carpeta que no són del motor);
 *  - els deixa de només lectura, perquè no s'editin per error: el motor s'edita aquí;
 *  - esborra els que ja no hi són (llista a `.motor-copiat.json`);
 *  - posa al dia el bloc del motor al .gitignore del projecte (les còpies no van a git);
 *  - posa al dia scripts i dependències del package.json des de `package.base.json`.
 *
 * Es fa sola abans de `dev`, `build` i les previsualitzacions. Amb `npm run dev`, a més, Vite
 * torna a copiar cada fitxer del motor que canviï (vegeu vite.config.ts).
 */
import { chmodSync, copyFileSync, existsSync, mkdirSync, readFileSync, readdirSync, rmSync, statSync, writeFileSync } from 'node:fs';
import { dirname, join, relative, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

export const MOTOR = dirname(fileURLToPath(import.meta.url));

/** Fitxers d'aquesta carpeta que no es copien als jocs. */
const PROPIS = new Set(['copia.mjs', 'package.base.json', 'README.md', 'node_modules']);
const MANIFEST = '.motor-copiat.json';
const GITIGNORE_BEGIN = '# >>> motor compartit (packages/benne, npm run motor): no editar';
const GITIGNORE_END = '# <<< motor compartit';

function walk(dir) {
  return readdirSync(dir, { withFileTypes: true }).flatMap((e) => {
    const full = join(dir, e.name);
    return e.isDirectory() ? walk(full) : [full];
  });
}

/** Camins (relatius, amb `/`) de tots els fitxers del motor. */
export function motorFiles() {
  return readdirSync(MOTOR)
    .filter((name) => !PROPIS.has(name))
    .flatMap((name) => {
      const full = join(MOTOR, name);
      return statSync(full).isDirectory() ? walk(full) : [full];
    })
    .map((full) => relative(MOTOR, full).split(sep).join('/'));
}

/** Copia un fitxer del motor al projecte (només lectura). Torna `true` si ha canviat. */
export function copyOne(project, rel) {
  const from = join(MOTOR, rel);
  const to = join(project, rel);
  const data = readFileSync(from);
  if (existsSync(to) && readFileSync(to).equals(data)) return false;
  mkdirSync(dirname(to), { recursive: true });
  rmSync(to, { force: true });
  copyFileSync(from, to);
  chmodSync(to, 0o444);
  return true;
}

function updateGitignore(project, files) {
  const path = join(project, '.gitignore');
  const current = existsSync(path) ? readFileSync(path, 'utf8') : '';
  // Una línia per entrada de primer nivell (src/engine, scripts...), no per fitxer.
  const tops = [...new Set(files.map((f) => (f.startsWith('src/') ? f.split('/').slice(0, 2).join('/') : f.split('/')[0])))].sort();
  const block = [GITIGNORE_BEGIN, ...tops.map((t) => `/${t}`), `/${MANIFEST}`, GITIGNORE_END].join('\n');
  const start = current.indexOf(GITIGNORE_BEGIN);
  const end = current.indexOf(GITIGNORE_END);
  const next = start >= 0 && end > start
    ? current.slice(0, start) + block + current.slice(end + GITIGNORE_END.length)
    : `${current.trimEnd()}\n\n${block}\n`;
  if (next !== current) writeFileSync(path, next);
}

/** Scripts i dependències del motor; el nom, `benne` i les dependències pròpies són del joc. */
function updatePackageJson(project) {
  const path = join(project, 'package.json');
  const pkg = JSON.parse(readFileSync(path, 'utf8'));
  const base = JSON.parse(readFileSync(join(MOTOR, 'package.base.json'), 'utf8'));
  const next = {
    name: pkg.name,
    private: true,
    version: pkg.version ?? '0.0.0',
    type: base.type,
    main: base.main,
    benne: pkg.benne,
    scripts: base.scripts,
    devDependencies: base.devDependencies,
    dependencies: { ...base.dependencies, ...Object.fromEntries(Object.entries(pkg.dependencies ?? {}).filter(([k]) => !(k in base.dependencies))) },
  };
  const text = JSON.stringify(next, null, 2) + '\n';
  if (text === readFileSync(path, 'utf8')) return false;
  writeFileSync(path, text);
  return true;
}

export function copyMotor(project) {
  const files = motorFiles();
  const manifestPath = join(project, MANIFEST);
  const before = existsSync(manifestPath) ? JSON.parse(readFileSync(manifestPath, 'utf8')).files ?? [] : [];
  let changed = 0;
  for (const rel of files) if (copyOne(project, rel)) changed++;
  const keep = new Set(files);
  let removed = 0;
  for (const rel of before) {
    if (keep.has(rel)) continue;
    rmSync(join(project, rel), { force: true });
    removed++;
  }
  writeFileSync(manifestPath, JSON.stringify({ origen: relative(project, MOTOR).split(sep).join('/'), files }, null, 2) + '\n');
  updateGitignore(project, files);
  const pkgChanged = updatePackageJson(project);
  return { changed, removed, pkgChanged, total: files.length };
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  const project = process.cwd();
  if (!existsSync(join(project, 'src/game/game-config.json'))) {
    console.error(`✖ ${project} no és un projecte Benne (no hi ha src/game/game-config.json).`);
    process.exit(1);
  }
  const r = copyMotor(project);
  console.log(`✔ Motor: ${r.changed} fitxers copiats, ${r.removed} esborrats (${r.total} en total)`);
  if (r.pkgChanged) console.log("  ⚠ package.json ha canviat (scripts o dependències del motor): fes `npm install`.");
}
