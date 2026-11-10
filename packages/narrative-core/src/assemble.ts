import type { GameContent, LocaleTable } from './types.js';

/**
 * Munta el contingut a partir dels fitxers JSON, vinguin d'on vinguin
 * (`import.meta.glob` a Vite, `fs` a les eines de línia d'ordres).
 *
 * `files`: camí relatiu a `game/` (p. ex. `data/quests.json`) → JSON ja parsejat.
 */
export function assembleGame(files: Record<string, unknown>): {
  content: GameContent;
  locales: Record<string, LocaleTable>;
} {
  const strip = <T>(json: unknown): T => {
    const { $schema: _ignored, ...rest } = json as Record<string, unknown>;
    return rest as T;
  };
  const file = <T>(path: string): T => {
    const json = files[path];
    if (json === undefined) throw new Error(`Falta el fitxer de contingut game/${path}`);
    return strip<T>(json);
  };

  const dialogues: GameContent['dialogues'] = {};
  const rooms: GameContent['rooms'] = {};
  const locales: Record<string, LocaleTable> = {};

  for (const [path, json] of Object.entries(files)) {
    const dlg = path.match(/^data\/dialogues\/([^/]+)\.json$/);
    if (dlg) {
      const def = strip<GameContent['dialogues'][string]>(json);
      dialogues[dlg[1]!] = def;
      continue;
    }
    const room = path.match(/^data\/rooms\/([^/]+)\.json$/);
    if (room) {
      rooms[room[1]!] = strip<GameContent['rooms'][string]>(json);
      continue;
    }
    const loc = path.match(/^locales\/([^/]+)\/[^/]+\.json$/);
    if (loc) {
      const table = strip<LocaleTable>(json);
      const target = (locales[loc[1]!] ??= {});
      for (const [key, value] of Object.entries(table)) {
        if (key in target) throw new Error(`Clau de text repetida "${key}" (${path})`);
        target[key] = value;
      }
    }
  }

  return {
    content: {
      manifest: file('data/game.json'),
      state: file('data/state.json'),
      characters: file('data/characters.json'),
      items: file('data/items.json'),
      rooms,
      quests: file('data/quests.json'),
      hints: file('data/hints.json'),
      endings: file('data/endings.json'),
      dialogues,
    },
    locales,
  };
}
