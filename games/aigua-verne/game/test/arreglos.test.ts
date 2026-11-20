/**
 * Coses que es van trobar jugant en mode tàctil i que no han de tornar: donar en persona el que la Mosca no pot
 * portar, i la subhasta (obrir el menú no gasta lots, les objeccions de l'Iri només valen al seu lot, l'ordre de les
 * vàlvules compta, i els moments de la història hi són igualment).
 */
import { describe, expect, it } from 'vitest';
import type { ResolvedLine } from '@aventura/narrative-core';
import { amb, anar, partida } from './partida.js';
import { acte1, acte2 } from './cami.js';

const vet = { kind: 'character' as const, id: 'vet' };
const textos = (lines: ResolvedLine[]) => lines.map((l) => l.text).join('\n');

describe('Aigua Verne: arreglos de la passada tàctil', () => {
  it('en persona, es dona el que la Mosca no pot portar (però el comunicador, no)', () => {
    const { n, p } = partida();
    n.apply({ giveItem: 'galleda_plena', who: 'iri' });
    p.do('give', vet, 'galleda_plena');
    expect(p.inventory('vet')).toContain('galleda_plena');
    expect(p.inventory('iri')).not.toContain('galleda_plena');

    const abans = p.inventory('vet').filter((i) => i === 'comunicador').length;
    p.do('give', vet, 'comunicador');
    expect(p.inventory('iri')).toContain('comunicador');
    expect(p.inventory('vet').filter((i) => i === 'comunicador').length).toBe(abans);
  });

  it('subhasta: el menú no gasta lots, cada objecció només val al seu lot, i amb Aqua primer no s\'hi arriba', () => {
    const { n, p } = partida();
    acte1(p, n);
    acte2(p, n, true);
    p.talk('lia', 'pare');
    amb(p, 'iri');
    anar(p, n, 'palau_salo');
    p.talk('holm', 'llavors');
    p.use('nota_lia', 'safata');
    amb(p, 'vet');
    p.do('pickUp', 'safates');
    p.talk('lia', 'nota');
    amb(p, 'iri');
    p.use('claus', 'safata');
    amb(p, 'vet');
    p.do('pickUp', 'safates');
    anar(p, n, 'palau_control');
    expect(n.flag('sync_subhasta')).toBe(true);
    expect(n.getVar('lots')).toBe(12);

    const iri = (opcio: string) => { amb(p, 'iri'); p.do('use', 'escenari'); return textos(p.talk('subhasta', opcio)); };
    const valvula = (v: string) => { amb(p, 'vet'); return textos(p.use('claus', `pany_${v}`)) + textos(p.do('open', `pany_${v}`)); };

    // Obrir el menú i esperar no gasta res.
    iri('adeu');
    expect(n.getVar('lots')).toBe(12);
    // Una objecció fora del seu lot no para el martell: gasta el torn, i l'opció hi continua.
    expect(iri('peixos')).toMatch(/més tard/);
    expect(n.flag('objeccio_peixos')).toBe(false);
    expect([n.getVar('lots'), n.getVar('lot'), n.getVar('pausa')]).toEqual([11, 2, 0]);
    // Al seu lot, sí: el martell s'atura tres torns (el de l'objecció, inclòs).
    expect(iri('c7788')).toMatch(/tractor/);
    expect([n.getVar('lots'), n.getVar('lot'), n.getVar('pausa')]).toEqual([11, 2, 2]);

    // Aqua primer: el preu baixa de cop per sota de 60 i el Magnat corre de debò a cada vàlvula. Ni amb les tres
    // objeccions al seu lot no s'hi arriba. Els moments de la història hi són igualment (la Lia, seguretat, en Tomàs).
    let dit = valvula('aqua');
    expect(n.getVar('preu_aigua')).toBe(57);
    expect(dit).toMatch(/quatre lots/);
    expect(dit).toMatch(/Tot en ordre/);
    expect([n.getVar('lots'), n.getVar('lot')]).toEqual([7, 6]);
    p.use('claus', 'pany_t2');
    expect(iri('anima')).toMatch(/Ànima/);
    dit = valvula('t2');
    expect(n.getVar('preu_aigua')).toBe(47);
    expect(dit).toMatch(/Seguretat és al moll/);
    expect(n.getVar('lot')).toBe(10);
    expect(iri('peixos')).toMatch(/compta els peixos/);
    dit = valvula('ferrum');
    expect(dit).toMatch(/Aquí el mecànic/);
    expect(dit).toMatch(/descomptat/);
    expect(n.getVar('reinicis_subhasta')).toBe(1);
    expect([n.getVar('lots'), n.getVar('lot'), n.getVar('pausa'), n.getVar('preu_aigua')]).toEqual([12, 1, 0, 112]);
    expect(n.flag('objeccio_7788') || n.flag('objeccio_anima') || n.flag('objeccio_peixos')).toBe(false);
  });
});
