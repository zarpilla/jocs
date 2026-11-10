/** Contingut mínim: el repositori arrenca i es pot arribar a un final. */
import { describe, expect, it } from 'vitest';
import { partida } from './partida.js';

describe('contingut mínim', () => {
  it("l'Iri connecta el router amb la caixa i arriba al final de prova", () => {
    const { n, p } = partida({ checkHints: true });
    p.do('pickUp', 'caixa');
    p.use('caixa_cartro', 'router');
    expect(n.flag('router_connectat')).toBe(true);
  });
});
