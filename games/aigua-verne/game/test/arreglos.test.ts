/**
 * Coses que es van trobar jugant en mode tàctil i que no han de tornar: donar en persona el que la Mosca no pot
 * portar, i la subhasta (obrir el menú no gasta lots, cap opció hi perd, i els avisos surten encara que el rellotge
 * salti).
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

  it('subhasta: el menú no gasta lots, cap opció hi perd, i els avisos surten', () => {
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
    expect(n.getVar('lots')).toBe(9);

    amb(p, 'iri');
    p.do('use', 'escenari');
    p.talk('subhasta', 'adeu');
    expect(n.getVar('lots')).toBe(9);
    for (const opcio of ['cava', 'peixos']) {
      const abans = n.getVar('lots') as number;
      p.do('use', 'escenari');
      p.talk('subhasta', opcio);
      expect(n.getVar('lots')).toBeGreaterThan(abans);
    }

    amb(p, 'vet');
    let dit = '';
    for (const v of ['t2', 'aqua', 'ferrum']) {
      dit += textos(p.use('claus', `pany_${v}`));
      dit += textos(p.do('open', `pany_${v}`));
    }
    expect(n.getVar('preu_aigua')).toBe(31);
    // A cada vàlvula el rellotge salta dos lots: l'avís de la Lia (6) i el d'en Tomàs (3) no s'han de perdre.
    expect(dit).toMatch(/Tot en ordre/);
    expect(dit).toMatch(/Aquí el mecànic/);
  });
});
