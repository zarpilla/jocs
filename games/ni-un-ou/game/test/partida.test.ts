/** El joc sencer, jugat de cap a peus, amb una pista disponible a cada pas. */
import { describe, expect, it } from 'vitest';
import { amb, anar, escena1, escena2, escena3, escena4, escena5, escena6, escena7, escena8, jugarTot, partida } from './partida.js';

describe('Partida sencera', () => {
  it('amb tots els aliats: primera plana', () => {
    const { n, p } = partida({ checkHints: true });
    jugarTot(p);
    expect(n.flag('enviat')).toBe(true);
    expect(n.getVar('aliats')).toBe(4);
    expect(n.resolveEnding()).toBe('final_primera');
  });

  it('sense cap aliat: pàgina 4', () => {
    const { n, p } = partida({ checkHints: true });
    jugarTot(p, { aliats: false });
    expect(n.getVar('aliats')).toBe(0);
    expect(n.resolveEnding()).toBe('final_pagina4');
  });

  it("amb les frontisses de l'Iri en lloc de la clau d'en Tomàs", () => {
    const { n, p } = partida({ checkHints: true });
    jugarTot(p, { frontisses: true });
    expect(n.flag('tomas_content')).toBe(false);
    expect(n.resolveEnding()).toBe('final_primera');
  });
});

it("Escena 6: la Nadia aliada allunya en Bastida", () => {
  const { n, p } = partida({ checkHints: true });
  jugarTot(p, { nadia: true });
  expect(n.flag('bastida_baixa')).toBe(true);
  expect(n.resolveEnding()).toBe('final_primera');
});

describe('Acte 1', () => {
  it("la paciència d'en Bastida: amb les distraccions de la Vet, no s'acaba", () => {
    const { n, p } = partida({ checkHints: true });
    escena1(p);
    escena2(p);
    escena3(p);
    expect(n.getVar('escena')).toBe(4);
    expect(n.getVar('reinicis_radio')).toBe(0);
    expect(n.getVar('paciencia')).toBeLessThan(6);
  });

  it("l'Iri sola no pot arreglar la ràdio: en Bastida s'aixeca i es torna a començar", () => {
    const { n, p } = partida();
    escena1(p);
    escena2(p);
    amb(p, 'iri');
    p.do('open', 'panell');
    p.do('pickUp', 'cable');
    anar(p, 'pallol');
    p.do('pickUp', 'prestatges');
    anar(p, 'sala_radio');
    p.use('cable_nou', 'panell');
    p.use('cable_nou', 'panell');
    p.do('use', 'radio');
    expect(n.getVar('reinicis_radio')).toBe(1);
    expect(n.flag('radio_feta')).toBe(false);
  });
});

describe('Atzucacs (primera repassada)', () => {
  it("Escena 3: l'Iri no pot quedar atrapada a la infermeria", () => {
    const { p } = partida();
    escena1(p);
    escena2(p);
    amb(p, 'iri');
    anar(p, 'passadis');
    p.do('use', 'porta_infermeria');
    expect(p.room).toBe('passadis');
  });

  it('Escena 5: obrir el muntacàrregues en lloc d\'agafar la safata també llegeix la nota', () => {
    const { n, p } = partida();
    escena1(p); escena2(p); escena3(p); escena4(p);
    anar(p, 'rebost');
    p.use('llibreta', 'munta');
    amb(p, 'vet');
    p.do('open', 'munta');
    expect(n.flag('nota_llegida')).toBe(true);
    amb(p, 'iri');
    p.do('open', 'munta');
    expect(n.flag('pla_fet')).toBe(true);
  });

  it('Escena 8: es pot deixar la reunió i tornar-hi', () => {
    const { n, p } = partida();
    escena1(p); escena2(p); escena3(p); escena4(p); escena5(p); escena6(p); escena7(p);
    anar(p, 'menjador');
    p.do('use', 'taula');
    p.talk('reunio', 'bastida', 'cisalla', 'enrere');
    p.do('use', 'taula');
    p.talk('reunio', 'bastida', 'pipa', 'correu', 'iri');
    expect(n.getVar('escena')).toBe(9);
  });
});

describe('Coherència (segona repassada)', () => {
  it("Escena 2: sense la revisió del Marcel, l'Arenga no salpa", () => {
    const { n, p } = partida();
    escena1(p);
    anar(p, 'infermeria');
    p.talk('fitxes', 'capitana');
    p.talk('capitana', 'gasoil', 'fi');
    p.talk('fitxes', 'tomas');
    p.talk('tomas', 'fi');
    p.talk('fitxes', 'nadia');
    p.talk('nadia', 'fi');
    anar(p, 'coberta_proa');
    p.talk('juana', 'valvula');
    expect(n.getVar('escena')).toBe(2);
    anar(p, 'infermeria');
    p.talk('fitxes', 'marcel');
    p.talk('marcel', 'fi');
    expect(n.getVar('escena')).toBe(3);
  });

  it("Escena 7: si l'Iri no ha passat pel pallol, el secret del Marcel encara hi és", () => {
    const { n, p } = partida();
    escena1(p); escena2(p); escena3(p); escena4(p); escena5(p);
    amb(p, 'iri', 'taller');
    p.do('pickUp', 'cisalla');
    anar(p, 'coberta_proa');
    p.do('look', 'escotilla');
    amb(p, 'vet', 'coberta_popa');
    p.talk('bastida', 'nus');
    amb(p, 'iri');
    p.use('cisalla', 'escotilla');
    p.do('use', 'escotilla');
    expect(n.getVar('escena')).toBe(7);
    amb(p, 'iri', 'pallol');
    p.talk('marcel', 'gat', 'guardar');
    expect(n.flag('aliat_marcel')).toBe(true);
  });
});

describe('Que no us vegin juntes (logic/separades.ts)', () => {
  it("abans que les escoltin, poden ser a la mateixa sala", () => {
    const { p } = partida();
    escena1(p);
    amb(p, 'iri', 'menjador');
    amb(p, 'vet', 'menjador');
    expect(p.room).toBe('menjador');
  });

  it("de l'Escena 4 a la reunió, cap no entra on és l'altra; pels passadissos, sí que es creuen", () => {
    const { p, world } = partida();
    escena1(p); escena2(p); escena3(p); escena4(p); escena5(p);
    amb(p, 'iri', 'laboratori');
    amb(p, 'vet', 'passadis');
    const linies = p.do('use', 'porta_laboratori');
    expect(p.room).toBe('passadis');
    expect(linies.map((l) => l.key)).toEqual(['separades.vet', 'separades.1', 'separades.tub']);
    amb(p, 'iri', 'passadis');
    expect(world.protagonistRoom?.('vet')).toBe('passadis');
  });

  it("a l'Escena 7, la Vet no baixa a màquines si hi ha l'Iri", () => {
    const { n, p } = partida();
    escena1(p); escena2(p); escena3(p); escena4(p); escena5(p); escena6(p);
    expect(n.getVar('escena')).toBe(7);
    amb(p, 'vet', 'passadis_baix');
    p.do('use', 'porta_maquines');
    expect(p.room).toBe('passadis_baix');
  });

  it('quan la Capitana les reuneix, tornen a estar juntes: al menjador, i després a tot arreu', () => {
    const { n, p, world } = partida();
    escena1(p); escena2(p); escena3(p); escena4(p); escena5(p); escena6(p); escena7(p);
    amb(p, 'vet', 'cabina_capitana');
    p.talk('capitana', 'reunir');
    expect(p.room).toBe('menjador');
    expect(world.protagonistRoom?.('iri')).toBe('menjador');
    // Si la Vet surt de la reunió, hi pot tornar encara que hi hagi l'Iri.
    anar(p, 'passadis');
    anar(p, 'menjador');
    expect(p.room).toBe('menjador');
    expect(n.flag('reunio_comencada')).toBe(true);
  });

  it('el joc sencer acaba amb les dues juntes', () => {
    const { n, p } = partida();
    escena1(p); escena2(p); escena3(p); escena4(p); escena5(p); escena6(p); escena7(p); escena8(p);
    expect(n.getVar('escena')).toBe(9);
    expect(n.check({ flag: 'reunio_comencada' })).toBe(true);
  });
});
