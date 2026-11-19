/**
 * `npm run benne:pegat [-- --from <checkout de Benne>]` (des de games/<joc>/, o `-w <joc>` des de l'arrel)
 *
 * Refà patches/motor-benne.patch: tots els canvis propis de packages/benne respecte del Benne d'on surt
 * (BENNE_BASE a motor-paths.ts). Sense `--from`, en baixa aquesta versió de GitHub a una carpeta temporal;
 * amb `--from`, el checkout ha de ser d'aquesta versió.
 *
 * Després comprova que el pegat, aplicat sobre aquest Benne, dona exactament packages/benne. Cal fer-ho
 * cada vegada que es toca el motor, perquè `benne:create --motor` no perdi res en actualitzar-lo.
 */
import { cpSync, existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseArgs } from 'node:util';
import { spawnSync } from 'node:child_process';
import { BENNE_BASE, SHARED_DIRS, SHARED_FILES } from './motor-paths.js';

const HERE = dirname(fileURLToPath(import.meta.url));
const MOTOR = resolve(HERE, '../../packages/benne');
const PATCH = join(HERE, 'patches/motor-benne.patch');

const { values } = parseArgs({ options: { from: { type: 'string' } } });

function run(cmd: string, args: string[], cwd?: string) {
  const r = spawnSync(cmd, args, { cwd, encoding: 'utf8', maxBuffer: 256 * 1024 * 1024, env: { ...process.env, LC_ALL: 'C' } });
  if (r.error) throw r.error;
  return r;
}

const tmp = mkdtempSync(join(tmpdir(), 'benne-pegat-'));
try {
  let src: string;
  if (values.from) {
    src = resolve(values.from);
  } else {
    src = join(tmp, 'benne');
    const r = run('git', ['clone', '-q', '--depth', '1', '--branch', BENNE_BASE, 'https://github.com/Bennethon/benne.git', src]);
    if (r.status !== 0) {
      console.error(`✖ No s'ha pogut baixar Benne ${BENNE_BASE}:\n${r.stderr}`);
      process.exit(1);
    }
  }
  const version = JSON.parse(readFileSync(join(src, 'benne-editor/package.json'), 'utf8')).version;
  if (`v${version}` !== BENNE_BASE) {
    console.error(`✖ ${src} és Benne ${version}, però el motor surt de ${BENNE_BASE} (motor-paths.ts).`);
    process.exit(1);
  }

  // Els dos arbres, només amb el que és motor: a = Benne, b = el nostre.
  const a = join(tmp, 'a');
  const b = join(tmp, 'b');
  for (const [from, to] of [[src, a], [MOTOR, b]] as const) {
    for (const p of [...SHARED_DIRS, ...SHARED_FILES]) {
      if (!existsSync(join(from, p))) continue;
      mkdirSync(dirname(join(to, p)), { recursive: true });
      cpSync(join(from, p), join(to, p), { recursive: true });
    }
  }

  const changed = run('diff', ['-rqN', 'a', 'b'], tmp).stdout
    .split('\n')
    .filter(Boolean)
    .map((line) => {
      const m = /^Files a\/(.+) and b\/.+ differ$/.exec(line);
      if (!m) throw new Error(`diff inesperat: ${line}`);
      return m[1]!;
    })
    .sort();

  let patch = '';
  for (const f of changed) {
    patch += `diff -ruN ${f} ${f}\n`;
    patch += run('diff', ['-uN', '--label', f, '--label', f, join('a', f), join('b', f)], tmp).stdout;
  }
  writeFileSync(PATCH, patch);

  // Comprovació: Benne + pegat = el nostre motor.
  const v = join(tmp, 'v');
  cpSync(a, v, { recursive: true });
  const applied = run('patch', ['-s', '-p0', '--forward', '--batch', '-i', PATCH], v);
  const same = run('diff', ['-rq', 'v', 'b'], tmp);
  if (applied.status !== 0 || same.status !== 0) {
    console.error(`✖ El pegat no reprodueix packages/benne:\n${applied.stdout}${applied.stderr}${same.stdout}`);
    process.exit(1);
  }
  console.log(`✔ ${relative(process.cwd(), PATCH)}: ${changed.length} fitxers respecte de Benne ${BENNE_BASE}; aplicat dona packages/benne exacte.`);
} finally {
  rmSync(tmp, { recursive: true, force: true });
}
