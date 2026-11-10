/**
 * El joc sobre el qual treballen les eines compartides (tools/, adapters/benne/).
 *
 * Es tria així, per ordre:
 *  1. la variable d'entorn `JOC` (el nom d'una carpeta de games/, o un camí);
 *  2. la carpeta des d'on s'executa, o una de les de sobre, que tingui `game/data/game.json`.
 *
 * Les ordres de cada joc (`npm run validate` dins games/suma-zero/, o `npm run validate -w suma-zero`
 * des de l'arrel) s'executen des de la carpeta del joc, així que normalment no cal res més.
 */
import { existsSync, readdirSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import type { GameContent, Narrative } from '@aventura/narrative-core';

export const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
export const GAMES = join(ROOT, 'games');

const isGame = (dir: string) => existsSync(join(dir, 'game/data/game.json'));

function findJoc(): string {
  const env = process.env.JOC;
  if (env) {
    const dir = isGame(join(GAMES, env)) ? join(GAMES, env) : resolve(env);
    if (!isGame(dir)) throw new Error(`JOC=${env}: no és cap joc (no hi ha game/data/game.json).`);
    return dir;
  }
  for (let dir = process.cwd(); ; dir = dirname(dir)) {
    if (isGame(dir)) return dir;
    if (dirname(dir) === dir) break;
  }
  const jocs = existsSync(GAMES) ? readdirSync(GAMES).filter((d) => isGame(join(GAMES, d))) : [];
  throw new Error(
    `No sé de quin joc parles. Executa l'ordre des de la carpeta del joc, amb -w (p. ex. \`npm run validate -w ${jocs[0] ?? '<joc>'}\`) o amb JOC=<joc>. Jocs: ${jocs.join(', ')}.`,
  );
}

let joc: string | undefined;
/** La carpeta del joc: games/<joc>/ (es decideix la primera vegada que es demana). */
export function jocDir(): string {
  return (joc ??= findJoc());
}
/** El contingut del joc: games/<joc>/game/. */
export const gameDir = () => join(jocDir(), 'game');

/** El que exporta `game/logic/index.ts` de cada joc (les regles pròpies). */
export interface GameLogic {
  GAME_ACTIONS: string[];
  GAME_TEXT_KEYS: string[];
  gameTextKeys(content: GameContent): string[];
  installGameLogic(n: Narrative): void;
}

/** Carrega les regles pròpies del joc (`game/logic/`). */
export async function loadGameLogic(): Promise<GameLogic> {
  return (await import(pathToFileURL(join(gameDir(), 'logic/index.ts')).href)) as GameLogic;
}
