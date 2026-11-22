/** El joc sencer, jugat de cap a peus, amb una pista disponible a cada pas. */
import { describe, expect, it } from 'vitest';
import { amb, anar, escena1, escena2, escena3, escena4, escena5, escena6, escena7, escena8, item, jugarTot, keys, partida } from './partida.js';

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
    const linies = p.do('use', 'radio').map((l) => l.key);
    expect(n.getVar('reinicis_radio')).toBe(1);
    expect(n.flag('radio_feta')).toBe(false);
    // No diu que la ràdio funciona abans de tornar a començar.
    expect(linies).not.toContain('sala.sala_radio.radio.4');
    expect(linies).toContain('sala.sala_radio.radio.9');
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

  it('Escena 5: obrir la safata en lloc d\'agafar-la també llegeix la nota', () => {
    const { n, p } = partida();
    escena1(p); escena2(p); escena3(p); escena4(p);
    anar(p, 'rebost');
    p.use('llibreta', 'munta');
    amb(p, 'vet');
    p.do('open', 'safata');
    expect(n.flag('nota_llegida')).toBe(true);
    amb(p, 'iri');
    p.do('open', 'safata');
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
    // A l'Escena 4 la Vet no juga, però la regla és aquesta: fins que no roben el portàtil, no s'amaguen.
    const { p } = partida();
    escena1(p); escena2(p); escena3(p);
    expect(p.room).toBe('laboratori');
    amb(p, 'vet', 'laboratori');
    expect(p.room).toBe('laboratori');
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

  it("a l'Escena 7, la Vet no baixa a màquines: la clau baixa pel muntacàrregues", () => {
    const { n, p } = partida();
    escena1(p); escena2(p); escena3(p); escena4(p); escena5(p); escena6(p);
    expect(n.getVar('escena')).toBe(7);
    amb(p, 'vet', 'passadis');
    expect(keys(p.do('use', 'escala_avall'))).toEqual(['sala.passadis.escala_avall.2']);
    expect(p.room).toBe('passadis');
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

describe('Pistes (revisió)', () => {
  it("Escena 2: si a la revisió no se li ha preguntat per la Juana, en Tomàs ho diu a la cuina", () => {
    const { n, p } = partida();
    escena1(p);
    anar(p, 'infermeria');
    p.talk('fitxes', 'tomas');
    p.talk('tomas', 'fi');
    expect(n.flag('sap_raco')).toBe(false);
    anar(p, 'cuina');
    p.talk('tomas');
    expect(n.flag('sap_raco')).toBe(true);
  });

  it("Escena 5: la llibreta pel muntacàrregues del pont diu que millor des del rebost", () => {
    const { n, p } = partida();
    escena1(p); escena2(p); escena3(p); escena4(p);
    amb(p, 'iri', 'pont');
    const linies = p.use('llibreta', 'munta');
    expect(linies.map((l) => l.key)).toEqual(['sala.pont.munta.nota']);
    expect(n.flag('nota_enviada')).toBe(false);
  });

  it("Escena 7: la clau i la mostra que esperen a la safata tenen pista", () => {
    const { n, p } = partida();
    escena1(p); escena2(p); escena3(p); escena4(p); escena5(p); escena6(p);
    anar(p, 'cuina');
    p.talk('tomas', 'clau7', 'entrepa7');
    p.use('clau_tomas', 'munta');
    // La safata del rebost és cosa de l'Iri: la Vet no en té cap, i el botó diu «canviem».
    expect(n.activeHints()).not.toContain('clau_safata');
    expect(n.hintForOther()).toBe('iri');
    amb(p, 'iri');
    expect(n.activeHints()[0]).toBe('clau_safata');
    anar(p, 'rebost');
    p.do('pickUp', 'safata');
    expect(n.activeHints()[0]).toBe('obrir');
    p.use('clau_tomas', 'registre');
    p.do('open', 'filtre');
    expect(n.activeHints()[0]).toBe('tornar');
    anar(p, 'rebost');
    p.use('mostra7', 'munta');
    expect(n.hintForOther()).toBe('vet');
    amb(p, 'vet');
    expect(n.activeHints()[0]).toBe('mostra_safata');
  });

  it("Escena 7: la pista de les frontisses segueix la clau de tubs", () => {
    const { n, p } = partida();
    escena1(p); escena2(p); escena3(p); escena4(p); escena5(p); escena6(p);
    amb(p, 'iri', 'taller');
    expect(n.activeHints()[0]).toBe('frontisses');
    p.do('pickUp', 'clau_tubs');
    expect(n.activeHints()[0]).toBe('frontisses_clau');
    anar(p, 'rebost');
    p.use('clau_tubs', 'registre');
    expect(n.activeHints()[0]).toBe('frontissa2');
  });

  it("Escena 1: a la cuina, la pista del muntacàrregues no explica com s'hi va", () => {
    const { n, p } = partida();
    p.do('pickUp', 'maceta');
    anar(p, 'passadis_baix');
    p.do('look', 'repetidor');
    p.use('maceta', 'porta_maquines');
    p.do('look', 'valvula');
    p.do('look', 'quadre');
    anar(p, 'taller');
    p.do('look', 'tauler');
    p.do('talkTo', item('walkie'));
    p.do('pickUp', 'llitera');
    expect(n.activeHints()[0]).toBe('vet_munta');
    anar(p, 'cuina');
    expect(n.activeHints()[0]).toBe('vet_munta_cuina');
  });

  it("Escena 9: dalt del pal, la pista ja no diu que hi pugi", () => {
    const { n, p } = partida();
    escena1(p); escena2(p); escena3(p); escena4(p); escena5(p); escena6(p); escena7(p); escena8(p);
    amb(p, 'iri');
    expect(n.activeHints()[0]).toBe('pal');
    anar(p, 'pal');
    expect(n.activeHints()[0]).toBe('pal_antena');
  });

  it("Escena 8: si l'USB el té la Vet, la pista li diu que el pugi al pont", () => {
    const { n, p } = partida();
    escena1(p); escena2(p); escena3(p); escena4(p); escena5(p); escena6(p); escena7(p);
    amb(p, 'iri');
    n.apply([{ takeItem: 'usb', who: 'iri' }, { giveItem: 'usb', who: 'vet' }]);
    expect(n.activeHints()).not.toContain('imprimir');
    amb(p, 'vet', 'cuina');
    expect(n.activeHints()[0]).toBe('usb_amunt');
    p.use('usb', 'munta');
    amb(p, 'iri');
    expect(n.activeHints()[0]).toBe('usb_safata');
  });

  it("Escena 5: qui envia el seu paper pel muntacàrregues diu «la meva nota» o «la resposta»", () => {
    const { p } = partida();
    escena1(p); escena2(p); escena3(p); escena4(p);
    anar(p, 'rebost');
    expect(p.use('llibreta', 'munta').map((l) => l.text)).toContain('Envio la meva nota a la cuina.');
    amb(p, 'vet');
    expect(p.do('pickUp', 'safata').map((l) => l.text)).toContain('Envio la resposta al rebost.');
  });

  it("Escena 7: el registre sense frontisses és una porta, i no diu que és tancat", () => {
    const { n, p } = partida();
    escena1(p); escena2(p); escena3(p); escena4(p); escena5(p); escena6(p);
    amb(p, 'iri', 'taller');
    p.do('pickUp', 'clau_tubs');
    anar(p, 'rebost');
    p.use('clau_tubs', 'registre');
    expect(p.do('open', 'registre').map((l) => l.key)).toEqual(['sala.rebost.registre.21']);
    p.use('clau_tubs', 'registre');
    expect(n.peek({ verb: 'pull', target: { kind: 'hotspot', id: 'registre' } })).toBeUndefined();
  });
});
