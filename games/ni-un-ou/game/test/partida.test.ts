/** El joc sencer, jugat de cap a peus, amb una pista disponible a cada pas. */
import { describe, expect, it } from 'vitest';
import { amb, anar, escena1, escena2, escena3, escena4, escena5, escena6, escena7, jugarTot, partida } from './partida.js';

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
