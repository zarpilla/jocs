/**
 * Sons: els que fa servir el contingut i el codi del joc han d'existir a `game/audio/sfx/`
 * (`npm run sons` els genera), i el validador avisa si en falta algun.
 */
import { describe, expect, it } from 'vitest';
import { validateContent } from '@aventura/narrative-core';
import { gameSounds, loadGameFromDisk } from '../../tools/load-game.js';
import { GAME_ACTIONS, GAME_TEXT_KEYS } from '../logic/index.js';

describe('Sons', () => {
  it('tots els sons del contingut i del codi existeixen', () => {
    const { content, locales } = loadGameFromDisk();
    const errors = validateContent(content, locales, { actions: GAME_ACTIONS, textKeys: GAME_TEXT_KEYS, sounds: gameSounds() })
      .filter((i) => i.level === 'error')
      .map((i) => i.message);
    expect(errors).toEqual([]);
  });
});
