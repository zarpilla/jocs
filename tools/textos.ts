/**
 * `npm run textos` (des de games/<joc>/): porta als locales els textos escrits directament al contingut.
 *
 * Per escriure de pressa, a qualsevol camp de text de `game/data/` (una línia, una opció, un nom, una pista...)
 * es pot posar la clau i el text alhora:
 *
 *   { "who": "iri", "text": "sala.taller.tauler.look=Hi falta la clau de vàlvules." }
 *
 * Aquesta eina hi deixa només la clau (`"sala.taller.tauler.look"`) i posa el text al fitxer de l'idioma per
 * defecte que toca pel prefix (`sala.` → sales.json, `dlg.` → dialegs.json...). Si la clau ja hi era, el text
 * nou la substitueix. Després, `npm run validate`.
 */
import { existsSync, readFileSync, readdirSync, statSync, writeFileSync } from 'node:fs';
import { join, relative } from 'node:path';
import { gameDir } from './joc.js';

const INLINE = /^([a-z][a-z0-9_]*(?:\.[a-z0-9_]+)+)=([\s\S]+)$/;
/** Fitxer de textos segons el primer tros de la clau. */
const FITXERS: Record<string, string> = {
  sala: 'sales', dlg: 'dialegs', obj: 'objectes', pj: 'personatges', mis: 'missions', pista: 'pistes',
  final: 'finals', ui: 'interficie',
};
const fitxer = (key: string) => FITXERS[key.split('.')[0]!] ?? 'general';

const game = gameDir();
const manifest = JSON.parse(readFileSync(join(game, 'data/game.json'), 'utf8')) as { defaultLocale: string };
const localeDir = join(game, 'locales', manifest.defaultLocale);

const tables = new Map<string, Record<string, string>>();
function table(name: string) {
  let t = tables.get(name);
  if (!t) {
    const path = join(localeDir, `${name}.json`);
    t = existsSync(path) ? (JSON.parse(readFileSync(path, 'utf8')) as Record<string, string>) : {};
    tables.set(name, t);
  }
  return t;
}

let moguts = 0;
let canviats = 0;
function extract(value: unknown): unknown {
  if (typeof value === 'string') {
    const m = INLINE.exec(value);
    if (!m) return value;
    const [, key, text] = m as unknown as [string, string, string];
    const t = table(fitxer(key));
    if (t[key] !== undefined && t[key] !== text) canviats++;
    t[key] = text;
    moguts++;
    return key;
  }
  if (Array.isArray(value)) return value.map(extract);
  if (value && typeof value === 'object') {
    return Object.fromEntries(Object.entries(value).map(([k, v]) => [k, extract(v)]));
  }
  return value;
}

const walk = (dir: string): string[] =>
  readdirSync(dir).flatMap((f) => {
    const p = join(dir, f);
    return statSync(p).isDirectory() ? walk(p) : f.endsWith('.json') ? [p] : [];
  });

for (const path of walk(join(game, 'data'))) {
  const before = moguts;
  const data = extract(JSON.parse(readFileSync(path, 'utf8')));
  if (moguts !== before) {
    writeFileSync(path, JSON.stringify(data, null, 2) + '\n');
    console.log(`· ${relative(game, path)}: ${moguts - before} textos`);
  }
}
for (const [name, t] of tables) writeFileSync(join(localeDir, `${name}.json`), JSON.stringify(t, null, 2) + '\n');
console.log(`✔ ${moguts} textos als locales${canviats ? ` (${canviats} ja hi eren i s'han substituït)` : ''}.`);
