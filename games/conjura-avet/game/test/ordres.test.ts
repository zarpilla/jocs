import { describe, expect, it } from 'vitest';
import { partida } from './partida.js';
import { ordres } from './ordres.js';

describe('ordres', () => {
  it('es juga sencera en un altre ordre (ordres.ts), amb una pista a cada pas', () => {
    const { n, p } = partida({ checkHints: true });
    ordres(p, n);
    expect(n.resolveEnding()).toBe('avet');
  });
});
