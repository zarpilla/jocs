/** La regla del toc (adapters/benne/tactil/runtime/accions.ts) amb un contingut mínim. */
import { describe, expect, it } from 'vitest';
import { HeadlessPlayer, MemoryWorld, Narrative, type GameContent } from '@aventura/narrative-core';
import { content, locales } from '../../../packages/narrative-core/test/fixture.js';
import { haFet, marcaMirat, queFaElToc } from '../tactil/runtime/accions.js';

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
    // el que fa el runtime: apunta abans de mirar, mira, i apunta el que queda (`acted`)
    marcaMirat(n, t);
    p.do('look', t);
    marcaMirat(n, t);
    expect(queFaElToc(n, t)).toEqual({ fa: 'accio', verb: 'push' });
  });

  /** Una palanca: es mira diferent abans i després d'estirar-la; després d'estirar-la, s'empeny. `far_ences` la pot canviar des de fora. */
  function palanca() {
    const c: GameContent = structuredClone(content);
    c.rooms.moll!.hotspots.palanca = {
      interactions: [
        { verb: 'look', if: { flag: 'estirada', is: false }, lines: [{ who: 'player', text: 'pescador.look' }] },
        { verb: 'look', lines: [{ who: 'player', text: 'caixa.buida' }] },
        { verb: 'pull', if: { flag: 'estirada', is: false }, lines: [{ who: 'player', text: 'caixa.obrir' }], effects: [{ setFlag: 'estirada' }] },
        { verb: 'push', if: { flag: 'far_ences', is: false }, lines: [{ who: 'player', text: 'caixa.obrir' }], effects: [{ setFlag: 'far_ences' }] },
        { verb: 'push', lines: [{ who: 'player', text: 'caixa.buida' }], effects: [{ addVar: 'monedes', amount: 1 }] },
      ],
    };
    const world = new MemoryWorld();
    const n = new Narrative({ content: c, locales, world });
    const p = new HeadlessPlayer(n, world);
    p.newGame();
    const t = { kind: 'hotspot' as const, id: 'palanca' };
    const toca = (verb: string) => { marcaMirat(n, t); p.do(verb, t); haFet(n, t, 'moll'); };
    return { n, p, t, toca };
  }

  it('després de fer-hi alguna cosa, el toc no torna a mirar (encara que la descripció hagi canviat)', () => {
    const { n, t, toca } = palanca();
    expect(queFaElToc(n, t)).toEqual({ fa: 'mira' });
    toca('look');
    expect(queFaElToc(n, t)).toEqual({ fa: 'menu' });
    toca('pull'); // ara es mira diferent i només s'empeny
    expect(queFaElToc(n, t)).toEqual({ fa: 'accio', verb: 'push' });
  });

  it('si canvia des de fora, només torna a mirar quan han canviat la descripció i les accions', () => {
    const { n, t, toca } = palanca();
    toca('look');
    n.apply({ setFlag: 'estirada' }); // canvien totes dues (des de fora): torna a mirar
    expect(queFaElToc(n, t)).toEqual({ fa: 'mira' });
    toca('look');
    n.apply({ setFlag: 'far_ences' }); // canvia l'acció però no la descripció: no
    expect(queFaElToc(n, t)).toEqual({ fa: 'accio', verb: 'push' });
  });

  it('cada protagonista mira els personatges per primer cop', () => {
    const world = new MemoryWorld();
    const n = new Narrative({ content, locales, world });
    const p = new HeadlessPlayer(n, world);
    p.newGame();
    const t = { kind: 'character' as const, id: 'pescador' };
    marcaMirat(n, t);
    expect(queFaElToc(n, t).fa).not.toBe('mira');
    p.switchTo('bo');
    expect(queFaElToc(n, t)).toEqual({ fa: 'mira' });
  });

  it('una descripció que fa alguna cosa (una prova) es mira encara que se n\'acabi de fer una acció', () => {
    const c: GameContent = structuredClone(content);
    c.rooms.moll!.hotspots.panell = {
      interactions: [
        { verb: 'look', if: { all: [{ flag: 'obert' }, { flag: 'sang', is: false }] }, lines: [{ who: 'player', text: 'pescador.look' }], effects: [{ setFlag: 'sang' }] },
        { verb: 'look', lines: [{ who: 'player', text: 'caixa.buida' }] },
        { verb: 'open', if: { flag: 'obert', is: false }, lines: [{ who: 'player', text: 'caixa.obrir' }], effects: [{ setFlag: 'obert' }] },
        { verb: 'close', lines: [{ who: 'player', text: 'caixa.obrir' }] },
      ],
    };
    const world = new MemoryWorld();
    const n = new Narrative({ content: c, locales, world });
    const p = new HeadlessPlayer(n, world);
    p.newGame();
    const t = { kind: 'hotspot' as const, id: 'panell' };
    marcaMirat(n, t);
    p.do('look', t);
    haFet(n, t, 'moll');
    p.do('open', t);
    haFet(n, t, 'moll');
    expect(queFaElToc(n, t)).toEqual({ fa: 'mira' });
  });
});
