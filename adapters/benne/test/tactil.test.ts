/** La regla del toc (adapters/benne/tactil/runtime/accions.ts) amb un contingut mínim. */
import { describe, expect, it } from 'vitest';
import { HeadlessPlayer, MemoryWorld, Narrative, type GameContent } from '@aventura/narrative-core';
import { content, locales } from '../../../packages/narrative-core/test/fixture.js';
import { marcaMirat, queFaElToc } from '../tactil/runtime/accions.js';

describe('interfície tàctil: el toc', () => {
  it('una mirada `once` seguida de la de sempre no fa mirar dues vegades', () => {
    const c: GameContent = structuredClone(content);
    c.rooms.moll!.hotspots.bitlla = {
      interactions: [
        { verb: 'look', once: true, lines: [{ who: 'player', text: 'pescador.look' }] },
        { verb: 'look', lines: [{ who: 'player', text: 'caixa.buida' }] },
        { verb: 'push', lines: [{ who: 'player', text: 'caixa.obrir' }], effects: [{ setFlag: 'far_ences' }] },
      ],
    };
    const world = new MemoryWorld();
    const n = new Narrative({ content: c, locales, world });
    const p = new HeadlessPlayer(n, world);
    p.newGame();
    const t = { kind: 'hotspot' as const, id: 'bitlla' };
    expect(queFaElToc(n, t)).toEqual({ fa: 'mira' });
    // el que fa el runtime: apunta abans de mirar, mira, i apunta el que queda (`looked`)
    marcaMirat(n, t);
    p.do('look', t);
    marcaMirat(n, t);
    expect(queFaElToc(n, t)).toEqual({ fa: 'accio', verb: 'push' });
  });
});
