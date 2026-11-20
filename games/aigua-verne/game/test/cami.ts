/**
 * El camí de la partida, escena per escena (el fan servir els tests i les proves d'exploració).
 */
import { expect } from 'vitest';
import type { Narrative } from '@aventura/narrative-core';
import { amb, anar, item, viatjar, type Jugador } from './partida.js';

/** Per a les captures: es crida en alguns punts de la partida (no fa res si no s'hi posa res). */
export const punt: { f: (tag: string) => void } = { f: () => {} };

/**
 * Com es juga l'Acte 2 (i, amb `previsora`, també l'Acte 1):
 * - `barril`: la canalla beu de l'últim barril; si no, del condensador (amb la targeta de la Mosca).
 * - `tractor`: en Fidel admet l'Iri pel tractor de l'avi (contracte 7.788); si no, pel quart sac de llavors.
 * - `previsora`: les quatre coses que es veuen i no s'agafen (el reg, el quart sac, la sorra, el vestit) s'agafen
 *   a la segona, «per si de cas», i després no cal tornar a buscar-les.
 */
export interface Cami { barril?: boolean; tractor?: boolean; previsora?: boolean }

export function acte1(p: Jugador, n: Narrative, cami: Cami = {}) {
  // Escena 1: la granja
  punt.f('e1');
  expect(p.room).toBe('granja_pati');
  anar(p, n, 'granja_casa');
  p.do('use', 'videotelefon');
  p.talk('pare', 'escriptura');
  p.do('push', 'quadre');
  expect(n.flag('quadre_apartat')).toBe(true);
  p.talk('pare', 'contrasenya');
  p.do('look', 'bol');
  p.do('open', 'caixa_forta');
  p.talk('teclat', 'titus');
  expect(n.flag('caixa_oberta')).toBe(true);
  amb(p, 'vet');
  anar(p, n, 'granja_graner');
  p.do('open', 'caixa_eines');
  p.use('punta_flor', item('tornavis'));
  if (cami.previsora) {
    // El reg: «no es toca, que encara serveix». A la segona, la Vet ho demana al pare: «per si de cas».
    p.do('pickUp', 'reg');
    p.do('pickUp', 'reg');
    expect(n.flag('reg_volgut')).toBe(true);
    anar(p, n, 'granja_casa');
    p.do('use', 'videotelefon');
    p.talk('pare', 'reg');
    anar(p, n, 'granja_graner');
    p.do('pickUp', 'reg');
    expect(p.inventory('vet')).toContain('reg');
  }
  anar(p, n, 'granja_pati');
  p.use('tornavis_flor', 'bomba');
  expect(n.getVar('escena')).toBe(2);
  // Escena 2: la Cantimplora
  anar(p, n, 'cantimplora_pont');
  p.talk('capitana', 'aigua');
  p.talk('capitana', 'portar');
  p.do('use', 'radio');
  p.talk('radio_juana', 'feina');
  anar(p, n, 'cantimplora_bodega');
  p.do('open', 'calaix');
  expect(n.flag('mosca_activa')).toBe(true);
  p.do('look', 'motor');
  p.do('pickUp', 'motor');
  p.talk('tomas', 'clau');
  anar(p, n, 'granja_casa');
  p.talk('pare', 'llavors');
  anar(p, n, 'granja_graner');
  p.do('pickUp', 'llavors');
  if (cami.previsora) {
    // El quart sac: «el pare ha dit que en guardem un»... No va dir on.
    p.do('pickUp', 'llavors');
    expect(p.inventory()).not.toContain('sac_llavors');
    p.do('pickUp', 'llavors');
    expect(p.inventory('vet')).toContain('sac_llavors');
  }
  p.use('oli', 'tractor');
  p.use('clau_anglesa', 'tractor');
  anar(p, n, 'cantimplora_bodega');
  p.use('injector', 'motor');
  p.use('sacs_llavors', 'carrega');
  anar(p, n, 'cantimplora_pont');
  p.do('use', 'radio');
  p.talk('radio_juana', 'albara');
  p.talk('capitana', 'entrego');
  expect(n.flag('capitana_accepta')).toBe(true);
  punt.f('e2');
  viatjar(p, n, 'aqua');
  // Escena 3: Aqua
  anar(p, n, 'aqua_port');
  p.do('look', 'grua');
  amb(p, 'vet');
  anar(p, n, 'cantimplora_bodega');
  p.do('pickUp', 'fusibles');
  p.talk('tomas', 'paper');
  p.use('fusible', item('paper_plata'));
  anar(p, n, 'aqua_port');
  p.use('fusible_apanyat', 'grua');
  p.do('walkTo', 'cistella');
  expect(p.room).toBe('aqua_fons');
  anar(p, n, 'casa_juana');
  punt.f('e3');
  p.talk('juana', 'mar', 'on', 'tornar', 'bru');
  expect(n.getVar('escena')).toBe(4);
  if (cami.previsora) {
    // La sorra: «en porto mig quilo a les botes»... i a la segona, un sac.
    amb(p, 'iri');
    anar(p, n, 'aqua_fons');
    p.do('pickUp', 'sorra');
    expect(p.inventory()).not.toContain('sorra');
    p.do('pickUp', 'sorra');
    expect(p.inventory('iri')).toContain('sorra');
  }
}

export function acte2(p: Jugador, n: Narrative, barril: boolean, cami: Cami = {}) {
  // Escena 4: Ferrum
  viatjar(p, n, 'ferrum');
  anar(p, n, 'ferrum_sindicat');
  p.talk('bru');
  expect(n.flag('bru_set')).toBe(true);
  if (cami.previsora) {
    // El vestit: «ni morta». A la segona, per si de cas... però és de la Rosa: l'hi demanen.
    p.do('pickUp', 'bagul');
    p.do('pickUp', 'bagul');
    expect(n.flag('vestit_volgut')).toBe(true);
    anar(p, n, 'ferrum_carrer');
    p.talk('rosa', 'vestit_cas');
    anar(p, n, 'ferrum_sindicat');
    p.do('pickUp', 'bagul');
    expect(p.inventory('iri')).toContain('vestit');
  }
  amb(p, 'vet');
  if (barril) {
    anar(p, n, 'cantimplora_bodega');
    p.do('push', 'barril');
    p.talk('barril', 'mirar');
  } else {
    // El condensador només s'engega amb una targeta de treballador actiu de Verne. Verne contracta, però cap persona
    // no passa el formulari (vint-i-quatre hores, cap vaga, cap aigua). La Mosca, sí.
    anar(p, n, 'ferrum_carrer');
    p.do('look', 'condensador');
    expect(n.flag('cal_targeta')).toBe(true);
    p.do('use', 'font');
    p.talk('contractacio', 'no', 'h24', 'aigua_si');
    expect(n.flag('contractacio_vista')).toBe(true);
    p.use('mosca', 'font');
    expect(p.inventory()).toContain('targeta_verne');
    p.use('targeta_verne', 'condensador');
  }
  expect(n.flag('canalla_beu')).toBe(true);
  amb(p, 'iri');
  p.talk('bru', 'canalla', 'promesa');
  expect(n.flag('promesa_lia')).toBe(true);
  anar(p, n, 'fosa_colada');
  p.use('motlle', 'llit');
  if (!cami.previsora) {
    expect(n.flag('cal_sorra')).toBe(true);
    // A Aqua, la platja ara és el lot 9 de Verne, «de la línia de l'aigua de dimarts cap amunt». I el mar ha baixat.
    viatjar(p, n, 'aqua');
    anar(p, n, 'aqua_fons');
    p.do('pickUp', 'sorra');
    expect(n.flag('lot9_vist')).toBe(true);
    expect(p.inventory()).not.toContain('sorra');
    p.do('look', 'boies');
    p.do('pickUp', 'sorra');
    expect(p.inventory()).toContain('sorra');
    viatjar(p, n, 'ferrum');
    anar(p, n, 'fosa_colada');
    p.use('motlle', 'llit');
  }
  expect(n.flag('motlle_preparat')).toBe(true);
  amb(p, 'vet');
  anar(p, n, 'fosa_forn');
  expect(n.flag('sync_colada')).toBe(true);
  p.do('push', 'manxa');
  punt.f('e4');
  p.do('pickUp', 'metall');
  p.do('use', 'rascle');
  amb(p, 'iri');
  p.do('use', 'gresol');
  p.use('sorra', 'llit');
  expect(n.flag('claus_fetes')).toBe(true);
  expect(n.getVar('escena')).toBe(5);
  // Escena 5: Verdant
  viatjar(p, n, 'verdant');
  punt.f('e5');
  anar(p, n, 'verdant_jardi');
  if (cami.previsora) {
    // El sac el porta la Vet des de l'Escena 2.
    amb(p, 'vet');
    anar(p, n, 'verdant_jardi');
    p.do('give', { kind: 'character', id: 'iri' }, 'sac_llavors');
    amb(p, 'iri');
    p.talk('fidel', 'inversora', 'sac');
  } else if (cami.tractor) {
    // En Fidel valora les coses per l'última operació: la granja, un crèdit (l'oferta de Verne). El tractor, un pou.
    p.talk('fidel', 'inversora', 'escriptura');
    expect(n.flag('fidel_norma')).toBe(true);
    p.talk('fidel', 'inversora', 'tractor');
  } else {
    p.talk('fidel', 'inversora', 'res');
    expect(n.flag('cal_aval')).toBe(true);
  }
  amb(p, 'vet');
  anar(p, n, 'verdant_jardi');
  p.talk('nil', 'palau');
  anar(p, n, 'verdant_cobert');
  p.do('look', 'tomaquera');
  p.do('pickUp', 'galleda');
  anar(p, n, 'verdant_jardi');
  p.talk('nil', 'tomaquera');
  expect(n.flag('cal_reg')).toBe(true);
  amb(p, 'iri');
  if (!cami.previsora) {
    // A Terra-2, Verne ha precintat el graner: «només hi pot entrar la propietat». L'escriptura ho demostra.
    viatjar(p, n, 'terra2');
    anar(p, n, 'granja_casa');
    p.talk('pare', 'reg');
    anar(p, n, 'granja_pati');
    p.do('walkTo', 'porta_graner');
    expect(p.room).toBe('granja_pati');
    expect(n.flag('precinte_vist')).toBe(true);
    p.use('escriptura', 'porta_graner');
    expect(n.flag('graner_obert')).toBe(true);
    anar(p, n, 'granja_graner');
    p.do('pickUp', 'reg');
    if (!cami.tractor) {
      p.do('pickUp', 'llavors');
      expect(p.inventory()).toContain('sac_llavors');
    }
    viatjar(p, n, 'verdant');
    anar(p, n, 'verdant_jardi');
    if (!cami.tractor) p.talk('fidel', 'inversora', 'sac');
    p.use('reg', item('mosca'));
  }
  expect(n.flag('fidel_admet')).toBe(true);
  anar(p, n, 'verdant_residencia');
  p.do('open', 'calaixera');
  p.do('look', 'paperera');
  p.do('open', 'arxivador');
  amb(p, 'vet');
  expect(p.inventory()).toContain('reg');
  anar(p, n, 'verdant_cobert');
  p.use('reg', 'tomaquera');
  expect(n.flag('cal_agulla')).toBe(true);
  anar(p, n, 'cantimplora_bodega');
  p.do('open', 'calaix');
  p.use('agulla', item('reg'));
  anar(p, n, 'verdant_cobert');
  p.use('reg_foradat', 'tomaquera');
  anar(p, n, 'verdant_jardi');
  p.use('galleda', 'reixa');
  anar(p, n, 'verdant_cobert');
  p.use('galleda_plena', 'tomaquera');
  anar(p, n, 'verdant_jardi');
  p.talk('nil', 'regada');
  expect(n.getVar('escena')).toBe(6);
  // Escena 6: la trucada
  expect(p.room).toBe('cantimplora_pont');
  p.talk('trucada', 'no');
  expect(n.flag('cal_espia')).toBe(true);
  anar(p, n, 'cantimplora_bodega');
  p.do('look', 'carmanyola');
  p.do('open', 'nevera');
  p.use('pernil', 'carmanyola');
  p.do('open', 'carmanyola');
  expect(n.flag('tomas_descobert')).toBe(true);
  amb(p, 'iri');
  anar(p, n, 'cantimplora_bodega');
  p.talk('tomas', 'per_que', 'volar');
  expect(n.flag('tomas_girat')).toBe(true);
  anar(p, n, 'cantimplora_pont');
  p.talk('capitana', 'contracte');
  expect(n.flag('capitana_si')).toBe(true);
  if (cami.previsora) {
    // El vestit ja és a bord: la Vet l'arregla i el torna a l'Iri.
    p.use('vestit', item('mosca'));
  } else {
    // A Ferrum, la Rosa el deixa... si en Tomàs, que fa una setmana que no baixa la rampa, el va a buscar ell.
    viatjar(p, n, 'ferrum');
    anar(p, n, 'ferrum_carrer');
    p.talk('rosa', 'vestit');
    expect(n.flag('rosa_vol_tomas')).toBe(true);
    expect(n.flag('rosa_permis')).toBe(false);
    amb(p, 'vet');
    p.talk('tomas', 'mare');
    expect(n.flag('tomas_baixa')).toBe(true);
  }
  amb(p, 'vet');
  expect(p.inventory()).toContain('vestit');
  p.use('agulla', item('vestit'));
  p.use('vestit_arreglat', item('mosca'));
  expect(n.getVar('escena')).toBe(7);
}

export function acte3(p: Jugador, n: Narrative) {
  expect(p.room).toBe('palau_servei');
  p.talk('lia', 'pare');
  amb(p, 'iri');
  expect(p.room).toBe('palau_galeria');
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
  punt.f('e7');
  // L'Iri para el martell amb cada objecció al seu lot; la Vet obre els dipòsits de petit a gran (Aqua, l'últim).
  const objeccio = (opcio: string) => { amb(p, 'iri'); p.do('use', 'escenari'); p.talk('subhasta', opcio); amb(p, 'vet'); };
  const valvula = (v: string) => { p.use('claus', `pany_${v}`); p.do('push', `pany_${v}`); };
  expect(n.getVar('lot')).toBe(1);
  objeccio('c7788');
  expect(n.flag('objeccio_7788')).toBe(true);
  valvula('t2');
  valvula('ferrum');
  expect(n.getVar('lot')).toBe(7);
  objeccio('anima');
  expect(n.flag('objeccio_anima')).toBe(true);
  valvula('aqua');
  expect(n.getVar('preu_aigua')).toBe(31);
  expect(n.getVar('ordre_valvules')).toBe('t2_ferrum_aqua');      // (el camí del gràfic del saló: 112, 102, 86, 31)
  expect(n.getVar('lot')).toBe(11);
  objeccio('peixos');
  expect(n.flag('objeccio_peixos')).toBe(true);
  punt.f('e8');
  p.do('pull', 'palanca');
  expect(n.flag('reserva_oberta')).toBe(true);
}

