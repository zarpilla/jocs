/**
 * Sons: els que fa servir el contingut i el codi del joc han d'existir a `game/audio/sfx/`
 * (`npm run sons` els genera), i el validador avisa si en falta algun.
 */
import { describe, expect, it } from 'vitest';
import { validateContent } from '@aventura/narrative-core';
import { fileURLToPath } from 'node:url';
import { gameSounds, loadGameFromDisk } from '../../../../tools/load-game.js';
import { GAME_ACTIONS, GAME_TEXT_KEYS, SONS_FINESTRA } from '../logic/index.js';

const GAME = fileURLToPath(new URL('..', import.meta.url));

const errors = (sounds: string[]) => {
  const { content, locales } = loadGameFromDisk(GAME);
  return validateContent(content, locales, { actions: GAME_ACTIONS, textKeys: GAME_TEXT_KEYS, sounds })
    .filter((i) => i.level === 'error')
    .map((i) => i.message);
};

describe('Ferro-9 · Sons', () => {
  it('tots els sons del contingut i del codi existeixen', () => {
    expect(errors(gameSounds(GAME))).toEqual([]);
    for (const so of Object.values(SONS_FINESTRA)) expect(gameSounds(GAME)).toContain(so);
  });

  it('cada valor possible de la molla i del diapasó té el seu so', () => {
    const sons = gameSounds(GAME);
    for (let i = 0; i <= 5; i++) expect(sons).toContain(`molla_${i}`), expect(sons).toContain(`pany_molla_${i}`);
    for (let i = 0; i <= 2; i++) expect(sons).toContain(`pany_diapaso_${i}`), expect(sons).toContain(`molla_diapaso_${i}`);
  });

  it('el validador detecta els sons que falten', () => {
    const sense = gameSounds(GAME).filter((s) => s !== 'clac' && !s.startsWith('pany_molla_'));
    const msgs = errors(sense).join('\n');
    expect(msgs).toContain('So desconegut "clac"');
    expect(msgs).toContain('So desconegut "pany_molla_{molla_tensio}"');
  });
});
