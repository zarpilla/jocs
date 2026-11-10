/**
 * Sons: els que fa servir el contingut i el codi del joc han d'existir a `game/audio/sfx/`
 * (`npm run sons` els genera), i el validador avisa si en falta algun.
 */
import { describe, expect, it } from 'vitest';
import { validateContent } from '@aventura/narrative-core';
import { fileURLToPath } from 'node:url';
import { gameSounds, loadGameFromDisk } from '../../../../tools/load-game.js';
import { GAME_ACTIONS, GAME_TEXT_KEYS } from '../logic/index.js';

const GAME = fileURLToPath(new URL('..', import.meta.url));

describe('Sons', () => {
  it('tots els sons del contingut i del codi existeixen', () => {
    const { content, locales } = loadGameFromDisk(GAME);
    const errors = validateContent(content, locales, { actions: GAME_ACTIONS, textKeys: GAME_TEXT_KEYS, sounds: gameSounds(GAME) })
      .filter((i) => i.level === 'error')
      .map((i) => i.message);
    expect(errors).toEqual([]);
  });
});
