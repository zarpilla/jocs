/**
 * A Benne, algunes crides acaben la funció que les fa: `dialog.end()`, `room.goTo()`, `saves.load()` i
 * `unhandled()` llancen per dins, i el codi que ve després no s'executa mai. Els tests de partida no ho poden
 * veure (juguen sense Benne), i el joc es queda penjat o a negre. Aquest test llegeix els scripts de Benne
 * (els de l'adaptador i els que genera el `sync` a cada joc) i falla si hi ha codi darrere d'una d'aquestes
 * crides.
 *
 * Si de debò cal continuar, la crida va dins d'un `try` (vegeu `endDialog` a `runtime/narrative.script.ts`).
 */
import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join, relative } from 'node:path';
import ts from 'typescript';
import { describe, expect, it } from 'vitest';

const ARREL = join(import.meta.dirname, '../../..');

/** Els fitxers que Benne compila com a scripts (el mateix patró que `bennescriptSteps.mjs`). */
const SCRIPT = /(?:^|[/\\])(?:[^/\\]+\.(?:room|character|inventory|dialog|gui|script)\.ts|globalScript\.ts)$/;

function scripts(dir: string, out: string[] = []): string[] {
  for (const nom of readdirSync(dir)) {
    if (nom === 'node_modules' || nom === 'dist' || nom === 'engine' || nom.startsWith('.')) continue;
    const ruta = join(dir, nom);
    if (statSync(ruta).isDirectory()) scripts(ruta, out);
    else if (SCRIPT.test(ruta)) out.push(ruta);
  }
  return out;
}

function fitxers(): string[] {
  const out = scripts(join(ARREL, 'adapters/benne'));
  for (const joc of readdirSync(join(ARREL, 'games'))) {
    const src = join(ARREL, 'games', joc, joc, 'src/game');
    try {
      if (statSync(src).isDirectory()) scripts(src, out);
    } catch {
      // Un joc sense projecte de Benne.
    }
  }
  return out;
}

/** Si una sentència és una crida que acaba la funció. */
function acaba(s: ts.Statement): string | null {
  if (!ts.isExpressionStatement(s) || !ts.isCallExpression(s.expression)) return null;
  const callee = s.expression.expression;
  if (ts.isIdentifier(callee) && callee.text === 'unhandled') return 'unhandled()';
  if (!ts.isPropertyAccessExpression(callee)) return null;
  const metode = callee.name.text;
  if (metode === 'end' || metode === 'goTo') return `.${metode}()`;
  if (metode === 'load' && ts.isIdentifier(callee.expression) && callee.expression.text === 'saves') return 'saves.load()';
  return null;
}

/** Les crides que acaben amb codi darrere, dins d'un mateix bloc (fora dels `try`, que ho aturen a posta). */
function codiMort(ruta: string, codi = readFileSync(ruta, 'utf8')): string[] {
  const font = ts.createSourceFile(ruta, codi, ts.ScriptTarget.Latest, true);
  const errors: string[] = [];
  const revisa = (sentencies: readonly ts.Statement[]) => {
    sentencies.forEach((s, i) => {
      const crida = acaba(s);
      if (!crida) return;
      // Darrere només hi pot haver un `return` sol, que no fa res.
      const resta = sentencies.slice(i + 1);
      if (resta.every((r) => ts.isReturnStatement(r) && !r.expression)) return;
      const linia = font.getLineAndCharacterOfPosition(s.getStart()).line + 1;
      errors.push(`${relative(ARREL, ruta)}:${linia}: ${crida} acaba la funció, i el que ve després no es fa mai`);
    });
  };
  const visita = (n: ts.Node, dinsTry: boolean) => {
    if (ts.isTryStatement(n)) {
      visita(n.tryBlock, true);
      if (n.catchClause) visita(n.catchClause, dinsTry);
      if (n.finallyBlock) visita(n.finallyBlock, dinsTry);
      return;
    }
    // Una funció nova: el `try` de fora ja no l'atura.
    if (ts.isFunctionLike(n)) dinsTry = false;
    if (!dinsTry && (ts.isBlock(n) || ts.isSourceFile(n) || ts.isCaseClause(n) || ts.isDefaultClause(n))) revisa(n.statements);
    ts.forEachChild(n, (c) => visita(c, dinsTry));
  };
  visita(font, false);
  return errors;
}

describe('scripts de Benne', () => {
  const tots = fitxers();

  it('en troba (els de l\'adaptador i els de cada joc)', () => {
    expect(tots.some((f) => f.endsWith('runtime/narrative.script.ts'))).toBe(true);
    expect(tots.length).toBeGreaterThan(5);
  });

  it('no hi ha codi darrere de dialog.end(), goTo(), saves.load() ni unhandled()', () => {
    expect(tots.flatMap((f) => codiMort(f))).toEqual([]);
  });

  it('detecta el cas que deixava la pantalla a negre, i deixa passar el try', () => {
    const abans = 'function f() {\n  if (step.ended) {\n    dialog.end()\n    followUp()\n  }\n}';
    expect(codiMort(join(ARREL, 'x.script.ts'), abans)).toEqual(['x.script.ts:3: .end() acaba la funció, i el que ve després no es fa mai']);
    const ara = 'function f() {\n  try {\n    dialog.end()\n    x()\n  } catch {}\n  followUp()\n}';
    expect(codiMort(join(ARREL, 'x.script.ts'), ara)).toEqual([]);
    expect(codiMort(join(ARREL, 'x.script.ts'), 'function f() {\n  room.goTo()\n}')).toEqual([]);
    expect(codiMort(join(ARREL, 'x.script.ts'), 'function f() {\n  if (a) {\n    room.goTo()\n    return\n  }\n}')).toEqual([]);
  });
});
