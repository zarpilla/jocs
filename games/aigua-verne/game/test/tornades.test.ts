/**
 * Tornar-hi és part del joc (guio.md, «Regles del món · 2»): el que no s'agafa la primera vegada s'agafa a la segona,
 * «per si de cas»; i si no, quan s'hi torna el lloc ha canviat (el lot 9 d'Aqua, el graner precintat, el favor de la
 * Rosa). I els trencaclosques que fan servir la lògica de Verne contra Verne: la Mosca contractada i el tractor de
 * l'avi. El camí sencer de cada variant és a partida.test.ts; aquí, els detalls.
 */
import { describe, expect, it } from 'vitest';
import type { ResolvedLine } from '@aventura/narrative-core';
import { amb, partida } from './partida.js';

const textos = (lines: ResolvedLine[]) => lines.map((l) => l.text).join('\n');

describe('Aigua Verne: tornar-hi', () => {
  it('la sorra: a la segona, per si de cas; amb el lot 9, cal mirar les boies', () => {
    const { n, p } = partida();
    p.goTo('aqua_fons');
    expect(textos(p.do('pickUp', 'sorra'))).toMatch(/mig quilo a les botes/);
    expect(p.inventory()).not.toContain('sorra');
    expect(textos(p.do('pickUp', 'sorra'))).toMatch(/Per si de cas/);
    expect(p.inventory()).toContain('sorra');

    const b = partida();
    b.n.apply([{ setFlag: 'lot9' }, { setFlag: 'cal_sorra' }, { setVar: 'escena', value: 4 }]);
    b.p.goTo('aqua_fons');
    expect(textos(b.p.do('pickUp', 'sorra'))).toMatch(/LOT 9/);
    expect(b.p.inventory()).not.toContain('sorra');
    expect(textos(b.p.do('pickUp', 'sorra'))).toMatch(/LOT 9/);
    expect(b.n.activeHints()).toContain('lot9');
    expect(textos(b.p.do('look', 'boies'))).toMatch(/línia de l'aigua de dimarts/);
    expect(textos(b.p.do('pickUp', 'sorra'))).toMatch(/no és del lot 9/);
    expect(b.p.inventory()).toContain('sorra');
    expect(n.flag('lot9_vist')).toBe(false);
  });

  it('el graner precintat: l\'escriptura o el tornavís de cap de flor; el contracte 7.788, no', () => {
    const { n, p } = partida();
    n.apply([{ setVar: 'escena', value: 5 }, { setFlag: 'cal_reg' }, { giveItem: 'contracte_7788' }, { giveItem: 'escriptura' }]);
    p.goTo('granja_pati');
    p.do('walkTo', 'porta_graner');
    expect(p.room).toBe('granja_pati');
    expect(textos(p.use('contracte_7788', 'porta_graner'))).toMatch(/No de qui és la finca/);
    expect(n.flag('graner_obert')).toBe(false);
    expect(n.activeHints()).toContain('precinte');
    p.use('escriptura', 'porta_graner');
    expect(n.flag('graner_obert')).toBe(true);
    p.do('walkTo', 'porta_graner');
    expect(p.room).toBe('granja_graner');

    const b = partida();
    b.n.apply([{ setVar: 'escena', value: 5 }, { giveItem: 'tornavis_flor', who: 'vet' }]);
    amb(b.p, 'vet');
    b.p.goTo('granja_pati');
    expect(textos(b.p.use('tornavis_flor', 'porta_graner'))).toMatch(/excepte jo/);
    expect(b.n.flag('graner_obert')).toBe(true);
  });

  it('el reg i el quart sac: a la segona, sense haver de tornar', () => {
    const { n, p } = partida();
    p.goTo('granja_graner');
    expect(textos(p.do('pickUp', 'reg'))).toMatch(/no es toca/);
    expect(textos(p.do('pickUp', 'reg'))).toMatch(/per si de cas/);
    expect(p.inventory()).not.toContain('reg');
    expect(textos(p.talk('pare', 'reg'))).toMatch(/après de mi/);
    p.do('pickUp', 'reg');
    expect(p.inventory()).toContain('reg');

    n.apply([{ setFlag: 'permis_pare' }]);
    p.do('pickUp', 'llavors');
    expect(textos(p.do('pickUp', 'llavors'))).toMatch(/es queda aquí/);
    expect(textos(p.do('pickUp', 'llavors'))).toMatch(/No va dir on/);
    expect(p.inventory()).toContain('sac_llavors');
    // A Verdant, en Nil (amb qui parla la Vet) ja no ens fa tornar a buscar-lo.
    n.apply([{ setFlag: 'tomaquera_vista' }]);
    amb(p, 'vet');
    expect(textos(p.talk('nil', 'tomaquera'))).toMatch(/En portem un/);
    expect(n.activeHints()).not.toContain('reg');
  });

  it('el vestit: per si de cas, la Rosa el deixa; set dies després, vol que baixi en Tomàs', () => {
    const { n, p } = partida();
    n.apply([{ setVar: 'escena', value: 4 }]);
    p.goTo('ferrum_sindicat');
    expect(textos(p.do('pickUp', 'bagul'))).toMatch(/ni morta/);
    expect(textos(p.do('pickUp', 'bagul'))).toMatch(/Per si de cas/);
    expect(p.inventory()).not.toContain('vestit');
    p.goTo('ferrum_carrer');
    expect(textos(p.talk('rosa', 'vestit_cas'))).toMatch(/espera un cas/);
    p.goTo('ferrum_sindicat');
    p.do('pickUp', 'bagul');
    expect(p.inventory()).toContain('vestit');
    // A la trucada, l'Iri ja el té.
    expect(textos(p.talk('trucada', 'no'))).toMatch(/Tinc el vestit de reina/);

    const b = partida();
    b.n.apply([{ setVar: 'escena', value: 6 }, { setFlag: 'cal_gala' }, { setVar: 'planeta', value: 'aqua' }]);
    b.p.goTo('ferrum_carrer');
    b.p.talk('rosa', 'vestit');
    expect(b.n.flag('rosa_permis')).toBe(false);
    expect(b.n.activeHints()).toContain('gala_tomas');
    b.p.goTo('cantimplora_bodega');
    // Amb la nau a un altre planeta, en Tomàs no pot baixar al piquet.
    expect(() => b.p.talk('tomas', 'mare')).toThrow(/no disponible/);
    b.n.apply([{ setVar: 'planeta', value: 'ferrum' }]);
    b.p.talk('tomas', 'mare');
    expect(b.p.inventory()).toContain('vestit');
    expect(b.n.flag('rosa_permis')).toBe(true);
  });
});

describe('Aigua Verne: la lògica de Verne contra Verne', () => {
  it('cap persona no passa el formulari de la font; la Mosca, sí; i la seva targeta engega el condensador', () => {
    const { n, p } = partida();
    n.apply([{ setVar: 'escena', value: 4 }, { setFlag: 'bru_set' }]);
    amb(p, 'vet');
    p.goTo('ferrum_carrer');
    expect(textos(p.do('use', 'condensador'))).toMatch(/targeta de treballador actiu/);
    // Sense haver despertat la Mosca, la pista porta al calaix de la Vet, no a la font.
    expect(n.activeHints()).toContain('mosca_targeta_vet');
    expect(n.activeHints()).not.toContain('targeta_vet');
    n.apply([{ setFlag: 'mosca_activa' }, { giveItem: 'mosca', who: 'vet' }]);
    expect(textos(p.talk('contractacio', 'si'))).toMatch(/denegada/);
    expect(textos(p.talk('contractacio', 'no', 'h9'))).toMatch(/denegada/);
    expect(textos(p.talk('contractacio', 'no', 'h24', 'aigua_no'))).toMatch(/no li cal/);
    expect(p.inventory()).not.toContain('targeta_verne');
    expect(n.activeHints()).toContain('targeta_vet');
    expect(textos(p.use('mosca', 'font'))).toMatch(/Benvinguda a la família Verne/);
    // A la font, la targeta de la Mosca dona la ració de la Mosca: zero litres.
    expect(textos(p.use('targeta_verne', 'font'))).toMatch(/zero litres/);
    expect(n.flag('canalla_beu')).toBe(false);
    p.use('targeta_verne', 'condensador');
    expect(n.flag('canalla_beu')).toBe(true);
    // A en Bru, li ho explica l'Iri, al sindicat.
    amb(p, 'iri');
    expect(textos(p.talk('bru', 'canalla'))).toMatch(/esquirola amb hèlices/);
  });

  it('en Fidel: el tractor de l\'avi val el que Verne en va pagar, però només un cop se sap com valora', () => {
    const { n, p } = partida();
    n.apply([{ setVar: 'escena', value: 5 }, { giveItem: 'contracte_7788' }, { giveItem: 'escriptura' }]);
    p.goTo('verdant_jardi');
    expect(() => p.talk('fidel', 'inversora', 'tractor')).toThrow(/no disponible/);
    expect(textos(p.talk('fidel', 'inversora', 'escriptura'))).toMatch(/Última operació/);
    expect(textos(p.talk('fidel', 'inversora', 'tractor'))).toMatch(/Els actius no arrenquen/);
    expect(n.flag('fidel_admet')).toBe(true);
    expect(p.inventory()).toContain('contracte_7788');
    // El Magnat ho sap per en Tomàs, i ho diu.
    expect(textos(p.talk('trucada', 'no'))).toMatch(/un tractor valorat en un milió[^]*el tractor\.\.\./);
  });
  it('el primer vol: la Cantimplora tus i s\'enlaira al port de Terra-2, i després ja no', () => {
    const { n, p } = partida();
    n.apply([{ setFlag: 'aqua_oberta' }]);
    p.goTo('cantimplora_mapa');
    const vol = textos(p.do('use', 'aqua'));
    expect(vol).toMatch(/tus, tremola, s'enlaira[^]*aterra al port d'Aqua/);
    expect(p.room).toBe('aqua_port');
    expect(n.flag('primer_vol')).toBe(true);
    expect(n.flag('enlairant')).toBe(false);
    expect(n.getVar('planeta')).toBe('aqua');
    // la segona vegada, el vol de sempre, pel mapa
    p.goTo('cantimplora_mapa');
    p.do('use', 'terra2');
    expect(p.room).toBe('port_terra2');
    p.goTo('cantimplora_mapa');
    p.do('use', 'aqua');
    expect(p.room).toBe('aqua_port');
  });
});
