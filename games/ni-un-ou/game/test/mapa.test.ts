/**
 * El plànol de l'Arenga (logic/mapa.ts): no obre cap porta que no s'obri caminant.
 */
import { describe, expect, it } from 'vitest';
import { accessibles, viatge } from '../logic/mapa.js';
import { amb, anar, escena1, escena2, escena3, escena4, escena5, escena7, escena8, escena9, item, partida, type Jugador } from './partida.js';

/** Fins a l'inici de l'Escena 6 (la Vet a la cuina, l'Iri a màquines). */
function finsEscena6(o: { aliats?: boolean } = {}) {
  const r = partida({ checkHints: true });
  escena1(r.p);
  escena2(r.p, o);
  escena3(r.p, o);
  escena4(r.p);
  escena5(r.p, o);
  expect(r.n.getVar('escena')).toBe(6);
  return r;
}

/** Va a una sala amb el plànol (on digui el viatge). */
function ambPlanol(p: Jugador, cap: string) {
  const v = viatge(p.narrative, cap);
  expect(v.sala, `Amb el plànol, de ${p.room} a ${cap}: ${v.linies.map((l) => l.text).join(' ')}`).toBe(cap);
  p.goTo(v.sala!);
}

describe('El plànol', () => {
  it("abans de l'Escena 6 no se'n pot agafar cap", () => {
    const { p } = partida();
    escena1(p);
    escena2(p);
    escena3(p);
    // Escena 4: l'Iri, al passadís
    anar(p, 'passadis');
    p.do('pickUp', 'planol');
    expect(p.inventory()).not.toContain('mapa');
  });

  it("a l'Escena 6, la Vet l'agafa al passadís; una sola còpia", () => {
    const { n, p } = finsEscena6();
    amb(p, 'vet', 'passadis');
    expect(n.flag('planol_vist')).toBe(true);
    p.do('pickUp', 'planol');
    expect(p.inventory()).toContain('mapa');
    p.do('pickUp', 'planol');
    expect(p.inventory().filter((i) => i === 'mapa')).toHaveLength(1);
    amb(p, 'iri', 'passadis');
    p.do('pickUp', 'planol');
    expect(p.inventory()).not.toContain('mapa');
  });

  it('obrir-lo és un esdeveniment, i no diu res', () => {
    const { n, p } = finsEscena6();
    amb(p, 'vet', 'passadis');
    p.do('pickUp', 'planol');
    const events: string[] = [];
    n.on((e) => { if (e.type === 'custom') events.push(e.name); });
    expect(p.do('use', item('mapa'))).toEqual([]);
    expect(events).toEqual(['mapa']);
  });

  it("Escena 6: cadascuna va a les seves sales (guio.md, «Regles del món · 9»)", () => {
    const { n, p } = finsEscena6();
    amb(p, 'iri', 'laboratori');
    amb(p, 'vet', 'passadis');
    const vet = accessibles(n);
    // On és l'Iri, no: no les han de veure juntes (logic/separades.ts).
    expect(vet.has('laboratori')).toBe(false);
    for (const s of ['coberta_popa', 'cabina_capitana', 'menjador', 'cuina', 'infermeria']) expect(vet.has(s), s).toBe(true);
    // El pont, la coberta de baix i, a l'Escena 6, la proa són de l'Iri.
    for (const s of ['pont', 'sala_radio', 'pal', 'coberta_proa', 'caixa_cadenes', 'pallol', 'taller', 'sala_bombes', 'camarot_iri', 'rebost', 'sala_maquines', 'diposit2']) {
      expect(vet.has(s), s).toBe(false);
    }
    // La porta que la tanca diu per què.
    expect(viatge(n, 'coberta_proa').linies).toEqual([{ who: 'player', text: 'sala.passadis.porta_proa.3' }]);
    expect(viatge(n, 'pont').linies).toEqual([{ who: 'player', text: 'sala.passadis.escala_amunt.8' }]);
    expect(viatge(n, 'rebost').linies).toEqual([{ who: 'player', text: 'sala.passadis.escala_avall.2' }]);
    expect(viatge(n, 'passadis')).toEqual({ sala: null, linies: [{ who: 'player', text: 'mapa.aqui' }] });

    amb(p, 'iri', 'passadis');
    const iri = accessibles(n);
    for (const s of ['coberta_proa', 'pallol', 'taller', 'sala_bombes', 'pont', 'sala_radio', 'camarot_iri', 'rebost', 'sala_maquines', 'laboratori']) {
      expect(iri.has(s), s).toBe(true);
    }
    for (const s of ['menjador', 'cuina', 'coberta_popa', 'cabina_capitana', 'infermeria', 'caixa_cadenes', 'diposit2', 'pal']) {
      expect(iri.has(s), s).toBe(false);
    }
    expect(viatge(n, 'caixa_cadenes').sala).toBeNull();
    expect(viatge(n, 'cuina').linies).toEqual([{ who: 'player', text: 'sala.coberta_proa.popa.3' }]);
    expect(viatge(n, 'infermeria').linies).toEqual([{ who: 'player', text: 'sala.passadis.porta_infermeria.6' }]);
  });

  it('Escena 6: mentre la Vet aprèn el nus a popa, no se\'n pot anar (ni amb el plànol)', () => {
    const { n, p } = finsEscena6();
    amb(p, 'vet', 'passadis');
    p.do('pickUp', 'planol');
    ambPlanol(p, 'coberta_popa');
    p.talk('bastida', 'nus');
    expect(n.flag('nus_lico')).toBe(true);
    expect([...accessibles(n)]).toEqual(['coberta_popa']);
    const v = viatge(n, 'infermeria');
    expect(v.sala).toBeNull();
    // la frase de la porta que la tanca
    expect(v.linies).toEqual([{ who: 'player', text: 'sala.coberta_popa.porta.1' }]);
  });

  it('una sala de pas on ha de passar alguna cosa atura el viatge', () => {
    const { n, p } = finsEscena6();
    amb(p, 'vet');
    expect(p.room).toBe('cuina');
    // De la cuina a la infermeria es passa pel passadís, on la Vet encara no ha vist el plànol.
    expect(viatge(n, 'infermeria').sala).toBe('passadis');
    // A popa no cal passar pel passadís.
    expect(viatge(n, 'coberta_popa').sala).toBe('coberta_popa');
  });

  it("Escena 5: el plànol tampoc no deixa l'Iri anar a la cuina (els paperets)", () => {
    const { n, p } = partida();
    escena1(p);
    escena2(p);
    escena3(p);
    escena4(p);
    expect(n.getVar('escena')).toBe(5);
    expect(p.room).toBe('laboratori');
    expect(viatge(n, 'cuina').sala).toBeNull();
    expect(viatge(n, 'menjador').sala).toBeNull();
    // de nit, a coberta tampoc
    expect(viatge(n, 'coberta_proa').sala).toBeNull();
    expect(viatge(n, 'rebost').sala).toBe('rebost');
  });

  it("Escenes 8 i 9: l'Iri no baixa del pont ni la Vet surt de màquines", () => {
    const { n, p } = finsEscena6();
    escena6AmbPlanol(p);
    escena7(p);
    expect(n.getVar('escena')).toBe(8);
    amb(p, 'iri');
    expect(p.room).toBe('pont');
    expect(viatge(n, 'passadis').sala).toBeNull();
    amb(p, 'vet');
    escena8(p);
    expect(n.getVar('escena')).toBe(9);
    amb(p, 'vet');
    expect(p.room).toBe('sala_maquines');
    expect(viatge(n, 'passadis_baix').sala).toBeNull();
    amb(p, 'iri');
    expect(viatge(n, 'passadis').sala).toBeNull();
    amb(p, 'vet');
    escena9(p);
    expect(n.flag('enviat')).toBe(true);
  });
});

/** L'Escena 6 feta amb el plànol: la Vet l'agafa i el dona a l'Iri, que va amb el plànol a tot arreu. */
function escena6AmbPlanol(p: Jugador) {
  // El plànol és per a la Vet, que no coneix el vaixell; l'Iri se'l sap de memòria i camina.
  amb(p, 'vet', 'passadis');
  p.do('pickUp', 'planol');
  ambPlanol(p, 'cabina_capitana');
  // a màquines hi ha l'Iri: no les han de veure juntes (logic/separades.ts), ni amb el plànol
  expect(viatge(p.narrative, 'sala_maquines').sala).toBeNull();
  amb(p, 'iri', 'taller');
  p.do('pickUp', 'cisalla');
  anar(p, 'pallol');
  p.do('look', 'inventari');
  p.talk('marcel', 'gat', 'guardar');
  anar(p, 'coberta_proa');
  p.do('look', 'escotilla');
  amb(p, 'vet');
  ambPlanol(p, 'coberta_popa');
  p.talk('bastida', 'nus');
  amb(p, 'iri');
  p.use('cisalla', 'escotilla');
  expect(p.room).toBe('caixa_cadenes');
  p.do('look', 'juana');
  // per sortir de la caixa cal l'escotilla (Escena 7), no el plànol
  amb(p, 'vet');
  expect(viatge(p.narrative, 'passadis').sala).toBeNull();
  amb(p, 'iri');
  p.do('use', 'escotilla');
}

it("Partida sencera amb el plànol a l'Escena 6: primera plana", () => {
  const { n, p } = finsEscena6();
  escena6AmbPlanol(p);
  escena7(p);
  escena8(p);
  escena9(p);
  expect(n.resolveEnding()).toBe('final_primera');
});
