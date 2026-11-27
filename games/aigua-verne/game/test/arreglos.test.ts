/**
 * Coses que es van trobar jugant en mode tàctil i que no han de tornar: donar en persona el que la Mosca no pot
 * portar, i la subhasta (obrir el menú no gasta lots, les objeccions de l'Iri només valen al seu lot, l'ordre de les
 * vàlvules compta, i els moments de la història hi són igualment).
 */
import { describe, expect, it } from 'vitest';
import type { ResolvedLine } from '@aventura/narrative-core';
import { amb, anar, partida, viatjar } from './partida.js';
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
    // Una objecció fora del seu lot no para el martell, però tampoc no gasta el torn (tasca 141), i l'opció hi continua.
    expect(iri('peixos')).toMatch(/més tard/);
    expect(n.flag('objeccio_peixos')).toBe(false);
    expect([n.getVar('lots'), n.getVar('lot'), n.getVar('pausa')]).toEqual([12, 1, 0]);
    // Al seu lot, sí: el martell s'atura tres torns (el de l'objecció, inclòs).
    expect(iri('c7788')).toMatch(/tractor/);
    expect([n.getVar('lots'), n.getVar('lot'), n.getVar('pausa')]).toEqual([12, 1, 2]);

    // Aqua primer: el preu baixa de cop per sota de 60 i el Magnat corre de debò a cada vàlvula. Ni amb les tres
    // objeccions al seu lot no s'hi arriba. Els moments de la història hi són igualment (la Lia, seguretat, en Tomàs).
    let dit = valvula('aqua');
    expect(n.getVar('preu_aigua')).toBe(57);
    expect(n.getVar('ordre_valvules')).toBe('aqua');
    expect(dit).toMatch(/quatre lots/);
    expect(dit).toMatch(/Tot en ordre/);
    expect([n.getVar('lots'), n.getVar('lot')]).toEqual([8, 5]);
    p.use('claus', 'pany_t2');
    expect(iri('anima')).toMatch(/Ànima/);
    dit = valvula('t2');
    expect(n.getVar('preu_aigua')).toBe(47);
    // (el gràfic del saló dibuixa el camí: 112 → 57 → 47, no 112 → 102 → 47)
    expect(n.getVar('ordre_valvules')).toBe('aqua_t2');
    expect(dit).toMatch(/Seguretat és al moll/);
    expect(n.getVar('lot')).toBe(9);
    expect(iri('peixos')).toMatch(/compta els peixos/);
    dit = valvula('ferrum');
    expect(dit).toMatch(/Aquí el mecànic/);
    expect(dit).toMatch(/descomptat/);
    expect(n.getVar('reinicis_subhasta')).toBe(1);
    expect([n.getVar('lots'), n.getVar('lot'), n.getVar('pausa'), n.getVar('preu_aigua')]).toEqual([12, 1, 0, 112]);
    expect(n.getVar('ordre_valvules')).toBe('');
    expect(n.flag('objeccio_7788') || n.flag('objeccio_anima') || n.flag('objeccio_peixos')).toBe(false);
  });
  it("la Capitana accepta l'albarà encara que el porti l'altra germana, si és al pont (tasca 083)", () => {
    const { n, p } = partida();
    // l'Acte 1 fins just abans que l'Iri doni l'albarà: el porta l'Iri, al pont; la Vet ha posat l'injector
    const parar = Symbol('parar');
    const talk = p.talk.bind(p);
    p.talk = ((who: string, ...opts: string[]) => {
      if (who === 'capitana' && opts[0] === 'entrego') throw parar;
      return talk(who, ...opts);
    }) as typeof p.talk;
    try { acte1(p, n); } catch (e) { if (e !== parar) throw e; }
    p.talk = talk;
    expect(p.inventory('iri')).toContain('albara');
    amb(p, 'vet');
    anar(p, n, 'cantimplora_pont');
    expect(p.inventory('vet')).not.toContain('albara');
    const r = p.talk('capitana', 'recorda');
    expect(textos(r)).toContain('el porta la teva germana');
    p.talk('capitana', 'entrego_iri');
    expect(n.flag('capitana_accepta')).toBe(true);
    expect(p.inventory('iri')).not.toContain('albara');
  });
  it('la caixa forta: la paraula es tecleja lletra a lletra, i una de dolenta no elimina res (tasca 075)', () => {
    const { n, p } = partida();
    n.apply([{ setFlag: 'quadre_apartat' }]);
    amb(p, 'iri');
    p.goTo('granja_casa');
    const lletres = (w: string) => [...w].map((c, i) => `c${i + 1}_${c.toLowerCase()}`);
    // MARIA, dues vegades (no s'elimina), i VERNE: no obren
    p.talk('teclat', 'tecleja', ...lletres('MARIA'), 'accepta_no', 'tecleja', ...lletres('MARIA'), 'accepta_no');
    p.talk('teclat', 'tecleja', ...lletres('VERNE'), 'accepta_no');
    expect(n.flag('caixa_oberta')).toBe(false);
    // TITUS, sense haver vist el bol: també obre (la paraula s'ha de saber, no desbloquejar)
    p.talk('teclat', 'tecleja', ...lletres('TITUS'), 'accepta');
    expect(n.flag('caixa_oberta')).toBe(true);
    expect(p.inventory('iri')).toContain('escriptura');
  });
  it('donar o fer servir la carta de la Juana amb en Bru obre la conversa (tasca 114)', () => {
    const { n, p, world } = partida();
    acte1(p, n);
    viatjar(p, n, 'ferrum');
    anar(p, n, 'ferrum_sindicat');
    const bru = { kind: 'character' as const, id: 'bru' };
    for (const verb of ['give', 'use']) {
      expect(n.peek({ verb, target: bru, item: 'carta_juana', room: world.room! })?.dialogue).toBe('bru');
    }
  });

  it('la colada: la grua només ofereix els moviments que es poden fer, i hi caben tots (tasques 110 i 111)', () => {
    const { n, p } = partida();
    n.apply([{ setFlag: 'sync_colada' }, { setVar: 'temperatura', value: 8 }, { setVar: 'gresol', value: 'llit' }]);
    amb(p, 'iri');
    p.goTo('fosa_colada');
    expect(n.startDialogue('grua').choices.map((c) => c.id)).toEqual(['esquerra', 'avall', 'adeu']);
    n.choose('grua', 'avall', { node: 'menu' });
    expect(n.startDialogue('grua').choices.map((c) => c.id)).toEqual(['amunt', 'bolca_buit', 'adeu']);
    expect(n.getVar('temperatura')).toBe(7);
  });
  it('el mapa aterra directament al port del planeta, sense passar pel pont ni la bodega (tasca 126)', () => {
    const { n, p, world } = partida();
    acte1(p, n);
    viatjar(p, n, 'terra2');
    expect(world.room).toBe('port_terra2');
    viatjar(p, n, 'aqua');
    expect(world.room).toBe('aqua_port');
  });
  it('subhasta a 31: la pista i la Vet apunten a la reserva (tasca 140)', () => {
    const { n, p } = partida();
    n.apply([{ setFlag: 'sync_subhasta' }, { setVar: 'valvules', value: 3 }, { setVar: 'preu_aigua', value: 31 }]);
    amb(p, 'vet');
    p.goTo('palau_control');
    expect(n.activeHints()).toContain('reserva_vet');
    expect(textos(p.do('look', 'palanca'))).toMatch(/no baixa de trenta/);
  });
  it("la pista del tractor sap si ja hi ha oli o la clau, i la grua, si ja es té el fusible embolicat (tasca 224)", () => {
    const { n, p } = partida();
    n.apply([{ setFlag: 'injector_vist' }]);
    expect(n.activeHints()).toContain('tractor');
    n.apply([{ setFlag: 'tractor_oliat' }]);
    expect(n.activeHints()).toContain('tractor_clau');
    expect(n.activeHints()).not.toContain('tractor');
    n.apply([{ setFlag: 'clau_donada' }]);
    expect(n.activeHints()).toContain('tractor_treu');
    expect(n.activeHints()).not.toContain('tractor_clau');
    n.apply([{ setFlag: 'tractor_oliat', value: false }]);
    expect(n.activeHints()).toContain('tractor_oli');

    amb(p, 'vet');
    p.goTo('aqua_port');
    expect(textos(p.do('look', 'grua'))).toMatch(/Paper de plata, per exemple/);
    n.apply({ giveItem: 'fusible_apanyat', who: 'vet' });
    const dit = textos(p.do('look', 'grua'));
    expect(dit).not.toMatch(/Paper de plata, per exemple/);
    expect(dit).toMatch(/Només cal posar-l'hi/);
  });
  it('la clau anglesa es torna a en Tomàs, i el tornavís amb el tractor té resposta (tasca 226)', () => {
    const { n, p } = partida();
    const tomas = { kind: 'character' as const, id: 'tomas' };
    n.apply([{ setVar: 'escena', value: 2 }, { giveItem: 'clau_anglesa', who: 'vet' }, { giveItem: 'tornavis', who: 'iri' }]);
    amb(p, 'vet');
    p.goTo('cantimplora_bodega');
    expect(textos(p.do('give', tomas, 'clau_anglesa'))).toMatch(/Te la tornaré/);
    expect(p.inventory('vet')).toContain('clau_anglesa');
    n.apply([{ setFlag: 'injector_tret' }]);
    expect(textos(p.do('give', tomas, 'clau_anglesa'))).toMatch(/Ningú no em torna mai res/);
    expect(p.inventory('vet')).not.toContain('clau_anglesa');

    n.apply([{ setFlag: 'injector_tret', value: false }]);
    amb(p, 'iri');
    p.goTo('granja_graner');
    expect(textos(p.use('tornavis', 'tractor'))).toMatch(/Amb un tornavís no hi faig res/);
  });
});
