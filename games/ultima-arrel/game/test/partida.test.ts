/**
 * L'Última Arrel de punta a punta: el contingut no té errors, la partida comença on diu el guió, no es pot canviar de
 * germana, i el camí sencer (cami.ts) s'acaba amb una pista disponible a cada pas.
 */
import { describe, expect, it } from 'vitest';
import { validateContent } from '@aventura/narrative-core';
import { content, locales } from '../index.js';
import { GAME_ACTIONS, gameTextKeys } from '../logic/index.js';
import { partida } from './partida.js';
import { acte1, acte2, acte3 } from './cami.js';
import { item } from './partida.js';

describe("L'Última Arrel: la partida", () => {
  it('el contingut no té errors', () => {
    const errors = validateContent(content, locales, { actions: GAME_ACTIONS, textKeys: gameTextKeys(content) }).filter((i) => i.level === 'error');
    expect(errors).toEqual([]);
  });

  it("comença amb l'Iri a la vora del bosc, i no es pot canviar de germana", () => {
    const { n, p, world } = partida();
    expect(p.active).toBe('iri');
    expect(p.room).toBe('vora_bosc');
    expect(world.rooms.get('vet')).toBe('campament_fades');
    expect([...p.inventory('iri')].sort()).toEqual(['centim', 'llibreta', 'llimona', 'lupa', 'walkie']);
    expect([...p.inventory('vet')].sort()).toEqual(['pot_melmelada', 'walkie']);
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
    expect(n.resolveEnding()).toBe('taula');
  });

  it("a la caseta, la Vet no fa sortir la Pla fins que n'ha rebut el kit (el necessita a la 6a)", () => {
    const { n, p } = partida({ checkHints: true });
    acte1(p, n);
    p.talk('urtica', 'naturaplus', 'adeu'); p.do('give', 'urtica', 'pot_melmelada'); p.do('use', 'gronxador'); p.use('pot_buit', 'flor');
    p.talk('bufo', 'paper', 'adeu'); p.use('estaca', 'tap_plastics'); p.do('use', 'comporta'); p.talk('gripau', 'ajuda'); p.talk('bufo');
    expect(p.room).toBe('caseta_obra');
    p.do('pull', 'arbre_wifi');
    expect(n.flag('pla_fora')).toBe(false);
    p.talk('pla', 'adeu');
    p.do('pull', 'arbre_wifi');
    p.use('walkie', 'altaveu'); p.do('use', 'altaveu');
    expect(p.room).toBe('zona_mati');
    p.do('talkTo', 'urtica');
    p.do('open', item('kit'));
    expect(p.inventory('vet')).toContain('caseta_paper');
  });
});
