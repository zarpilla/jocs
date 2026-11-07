import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join, relative, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { assembleGame } from '../game/assemble.js';

export const GAME_DIR = fileURLToPath(new URL('../game/', import.meta.url));

function walk(dir: string): string[] {
  return readdirSync(dir).flatMap((name) => {
    const full = join(dir, name);
    return statSync(full).isDirectory() ? walk(full) : full.endsWith('.json') ? [full] : [];
  });
}

/** Tots els JSON de `data/` i `locales/`: camí relatiu a `game/` → JSON. */
export function readGameFiles(dir = GAME_DIR) {
  const files: Record<string, unknown> = {};
  for (const sub of ['data', 'locales']) {
    for (const full of walk(join(dir, sub))) {
      const rel = relative(dir, full).split(sep).join('/');
      try {
        files[rel] = JSON.parse(readFileSync(full, 'utf8'));
      } catch (e) {
        throw new Error(`JSON mal format a game/${rel}: ${(e as Error).message}`);
      }
    }
  }
  return files;
}

/** Llegeix el contingut del joc des del disc (per a eines de Node). */
export function loadGameFromDisk(dir = GAME_DIR) {
  return assembleGame(readGameFiles(dir));
}
