/**
 * La Conjura de l'Avet de punta a punta: el contingut no té errors, la partida comença on diu el guió, i el camí
 * sencer (cami.ts) s'acaba amb una pista disponible a cada pas.
 */
import { describe, expect, it } from 'vitest';
import { validateContent } from '@aventura/narrative-core';
import { content, locales } from '../index.js';
import { GAME_ACTIONS, gameTextKeys } from '../logic/index.js';
import { partida } from './partida.js';
import { acte1, acte2, acte3, acte4, tutorial } from './cami.js';

describe("La Conjura de l'Avet: la partida", () => {
  it('el contingut no té errors', () => {
    const errors = validateContent(content, locales, { actions: GAME_ACTIONS, textKeys: gameTextKeys(content) }).filter((i) => i.level === 'error');
    expect(errors).toEqual([]);
  });

  it("comença amb la Iri a l'avet, i no es pot canviar fins que arriba la Vet", () => {
    const { n, p } = partida();
    expect(p.active).toBe('iri');
    expect(p.room).toBe('mur_avet');
    expect([...p.inventory('iri')].sort()).toEqual(['destral', 'guants', 'olla']);
    expect(n.canSwitch()).toBe(false);
  });

  it('es juga sencera, amb una pista a cada pas', () => {
    const { n, p } = partida({ checkHints: true });
    acte1(p, n);
    expect(n.quests().find((q) => q.id === 'acte1')?.status).toBe('completed');
    acte2(p, n);
    expect(n.quests().find((q) => q.id === 'acte2')?.status).toBe('completed');
    acte3(p, n);
    expect(n.quests().find((q) => q.id === 'acte3')?.status).toBe('completed');
    acte4(p, n);
    expect(n.quests().find((q) => q.id === 'acte4')?.status).toBe('completed');
    expect(n.resolveEnding()).toBe('avet');
  });

  it("a l'acte 1, el pont es pot fer abans que la plaça, i la Vet no hi entra", () => {
    const { n, p } = partida({ checkHints: true });
    tutorial(p, n);
    p.do('walkTo', 'cami_riu');
    p.use('destral', 'sobreeixidor');
    p.use('pot_resina', 'barca');
    p.use('salabre', 'comporta');
    expect(n.flag('serra_treta')).toBe(true);
    p.switchTo('vet');
    p.do('walkTo', 'cami_riu');
    expect(p.room).toBe('mur_avet');
    p.do('walkTo', 'porta_monestir');
    expect(p.room).toBe('claustre');
  });

  it("la Iri no entra al claustre a l'acte 1, ni a l'apotecaria a l'acte 2", () => {
    const { n, p } = partida();
    tutorial(p, n);
    p.do('walkTo', 'porta_monestir');
    expect(p.room).toBe('mur_avet');
  });
});
