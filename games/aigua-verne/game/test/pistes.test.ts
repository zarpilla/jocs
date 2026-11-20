/**
 * Les pistes de l'Acte 3 (el palau): que no s'hi encallin les del vestit, i que la subhasta expliqui com es guanya.
 */
import { describe, expect, it } from 'vitest';
import type { MemoryWorld, Narrative } from '@aventura/narrative-core';
import { amb, anar, partida } from './partida.js';
import { acte1, acte2 } from './cami.js';

/** La pista que tindria `who` si jugués ara (sense gastar-ne cap nivell). */
function pista(n: Narrative, world: MemoryWorld, who: string) {
  const [active, room] = [world.active, world.room];
  world.active = who;
  world.room = world.rooms.get(who) ?? null;
  const id = n.activeHints()[0] ?? null;
  [world.active, world.room] = [active, room];
  return id;
}

describe('Aigua Verne: pistes del palau', () => {
  it("les del vestit s'apaguen en entrar al palau, i la subhasta té les seves", () => {
    const { n, p, world } = partida();
    acte1(p, n);
    acte2(p, n, true);
    expect(n.getVar('escena')).toBe(7);
    const totes = () => [pista(n, world, 'iri'), pista(n, world, 'vet')];
    const ids = new Set<string | null>();
    const mira = () => { for (const id of totes()) ids.add(id); };

    expect(totes()).toEqual(['lia', 'lia_vet']);
    p.talk('lia', 'pare');
    mira();
    amb(p, 'iri');
    anar(p, n, 'palau_salo');
    p.talk('holm', 'llavors');
    mira();
    p.use('nota_lia', 'safata');
    amb(p, 'vet');
    p.do('pickUp', 'safates');
    p.talk('lia', 'nota');
    mira();
    amb(p, 'iri');
    p.use('claus', 'safata');
    amb(p, 'vet');
    p.do('pickUp', 'safates');
    mira();
    anar(p, n, 'palau_control');
    expect(n.flag('sync_subhasta')).toBe(true);
    expect(totes()).toEqual(['subhasta_iri', 'subhasta_vet']);
    expect([...ids].filter((id) => !id || id.startsWith('gala'))).toEqual([]);

    // La Vet sola no hi arriba: els lots s'acaben i es torna a començar. La pista ho ha de dir.
    for (const v of ['t2', 'aqua', 'ferrum']) {
      p.use('claus', `pany_${v}`);
      p.do('push', `pany_${v}`);
    }
    expect(n.getVar('reinicis_subhasta')).toBe(1);
    expect(n.getVar('valvules')).toBe(0);
    expect(totes()).toEqual(['subhasta_sola', 'subhasta_sola']);
    expect(n.requestHint()!.text).toMatch(/Vet sola/);

    // Amb la primera objecció, cadascuna torna a la seva: l'Iri, les objeccions; la Vet, l'ordre dels dipòsits.
    amb(p, 'iri');
    p.do('use', 'escenari');
    p.talk('subhasta', 'c7788');
    expect(totes()).toEqual(['subhasta_iri', 'subhasta_vet']);
    expect(n.requestHint()!.text).toMatch(/Què tinc/);
    amb(p, 'vet');
    expect(n.requestHint()!.text).toMatch(/Símptoma/);
    for (const v of ['t2', 'ferrum']) {
      p.use('claus', `pany_${v}`);
      p.do('push', `pany_${v}`);
    }
    amb(p, 'iri');
    p.do('use', 'escenari');
    p.talk('subhasta', 'anima');
    amb(p, 'vet');
    p.use('claus', 'pany_aqua');
    p.do('push', 'pany_aqua');
    expect(n.getVar('valvules')).toBe(3);
    expect(totes()).toEqual(['reserva', 'reserva_vet']);
  });
});
