import { existsSync, readFileSync, readdirSync, statSync } from 'node:fs';
import { join, relative, sep } from 'node:path';
import { assembleGame } from '@aventura/narrative-core';
import { gameDir } from './joc.js';

function walk(dir: string): string[] {
  return readdirSync(dir).flatMap((name) => {
    const full = join(dir, name);
    return statSync(full).isDirectory() ? walk(full) : full.endsWith('.json') ? [full] : [];
  });
}

/** Tots els JSON de `data/` i `locales/`: camí relatiu a `game/` → JSON. */
export function readGameFiles(dir = gameDir()) {
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

/**
 * Claus repetides dins d'un mateix objecte JSON. `JSON.parse` es queda amb l'última sense dir res,
 * i un text o una pista poden desaparèixer sense que se'n adoni ningú.
 */
export function duplicateKeys(text: string): string[] {
  const found: string[] = [];
  const stack: (Set<string> | null)[] = []; // un Set per objecte, null per llista
  let i = 0;
  while (i < text.length) {
    const ch = text[i]!;
    if (ch === '"') {
      let j = i + 1;
      while (text[j] !== '"') j += text[j] === '\\' ? 2 : 1;
      const str = JSON.parse(text.slice(i, j + 1)) as string;
      let k = j + 1;
      while (/\s/.test(text[k] ?? '')) k++;
      const keys = stack[stack.length - 1];
      if (text[k] === ':' && keys) {
        if (keys.has(str)) found.push(str);
        keys.add(str);
      }
      i = j + 1;
      continue;
    }
    if (ch === '{') stack.push(new Set());
    else if (ch === '[') stack.push(null);
    else if (ch === '}' || ch === ']') stack.pop();
    i++;
  }
  return found;
}

/** Fitxers del joc amb claus repetides: camí relatiu a `game/` → claus. */
export function gameDuplicateKeys(dir = gameDir()) {
  const out: Record<string, string[]> = {};
  for (const sub of ['data', 'locales']) {
    for (const full of walk(join(dir, sub))) {
      const dups = duplicateKeys(readFileSync(full, 'utf8'));
      if (dups.length) out[relative(dir, full).split(sep).join('/')] = dups;
    }
  }
  return out;
}

/** Llegeix el contingut del joc des del disc (per a eines de Node). */
export function loadGameFromDisk(dir = gameDir()) {
  return assembleGame(readGameFiles(dir));
}

export const SOUND_EXTENSIONS = ['.ogg', '.mp3', '.wav'];

/** Fitxers de so de `game/audio/sfx/` (els genera `npm run sons`). */
export function gameSoundFiles(dir = gameDir()) {
  const sfx = join(dir, 'audio', 'sfx');
  if (!existsSync(sfx)) return [];
  return readdirSync(sfx).filter((f) => SOUND_EXTENSIONS.some((e) => f.endsWith(e))).map((f) => join(sfx, f));
}

/** Pistes de música de `game/audio/music/` (les genera `npm run musica`). */
export function gameMusicFiles(dir = gameDir()) {
  const music = join(dir, 'audio', 'music');
  if (!existsSync(music)) return [];
  return readdirSync(music).filter((f) => SOUND_EXTENSIONS.some((e) => f.endsWith(e))).map((f) => join(music, f));
}

/** Noms dels sons (sense extensió), el que va al camp `sound` de les línies. */
export function gameSounds(dir = gameDir()) {
  return gameSoundFiles(dir).map((f) => f.slice(f.lastIndexOf(sep) + 1).replace(/\.[^.]+$/, ''));
}
