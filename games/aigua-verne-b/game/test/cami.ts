/**
 * El camí de la partida, escena per escena (el fan servir els tests i les proves d'exploració).
 */
import { expect } from 'vitest';
import type { Narrative } from '@aventura/narrative-core';
import { amb, anar, item, viatjar, type Jugador } from './partida.js';

/** Per a les captures: es crida en alguns punts de la partida (no fa res si no s'hi posa res). */
export const punt: { f: (tag: string) => void } = { f: () => {} };

export function acte1(p: Jugador, n: Narrative) {
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
}

export function acte2(p: Jugador, n: Narrative, barril: boolean) {
  // Escena 4: Ferrum
  viatjar(p, n, 'ferrum');
  anar(p, n, 'ferrum_sindicat');
  p.talk('bru');
  expect(n.flag('bru_set')).toBe(true);
  amb(p, 'vet');
  if (barril) {
    anar(p, n, 'cantimplora_bodega');
    p.do('push', 'barril');
    p.talk('barril', 'mirar');
  } else {
    anar(p, n, 'ferrum_carrer');
    p.do('look', 'condensador');
    p.use('clau_anglesa', 'font');
    anar(p, n, 'cantimplora_bodega');
    p.do('pickUp', 'cafetera');
    anar(p, n, 'ferrum_carrer');
    p.use('corretja', 'condensador');
    p.use('filtre', 'condensador');
    p.do('push', 'condensador');
  }
  expect(n.flag('canalla_beu')).toBe(true);
  amb(p, 'iri');
  p.talk('bru', 'canalla', 'promesa');
  expect(n.flag('promesa_lia')).toBe(true);
  anar(p, n, 'fosa_colada');
  p.use('motlle', 'llit');
  expect(n.flag('cal_sorra')).toBe(true);
  viatjar(p, n, 'aqua');
  anar(p, n, 'aqua_fons');
  p.do('pickUp', 'sorra');
  viatjar(p, n, 'ferrum');
  anar(p, n, 'fosa_colada');
  p.use('motlle', 'llit');
  expect(n.flag('motlle_preparat')).toBe(true);
  amb(p, 'vet');
  anar(p, n, 'fosa_forn');
  expect(n.flag('sync_colada')).toBe(true);
  p.do('push', 'manxa');
  punt.f('e4');
  p.do('pickUp', 'metall');
  p.do('use', 'rascle');
  amb(p, 'iri');
  p.do('pull', 'gresol');
  p.use('sorra', 'llit');
  expect(n.flag('claus_fetes')).toBe(true);
  expect(n.getVar('escena')).toBe(5);
  // Escena 5: Verdant
  viatjar(p, n, 'verdant');
  punt.f('e5');
  anar(p, n, 'verdant_jardi');
  p.talk('fidel', 'inversora', 'res');
  expect(n.flag('cal_aval')).toBe(true);
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
  viatjar(p, n, 'terra2');
  anar(p, n, 'granja_casa');
  p.talk('pare', 'reg');
  anar(p, n, 'granja_graner');
  p.do('pickUp', 'reg');
  p.do('pickUp', 'llavors');
  expect(p.inventory()).toContain('sac_llavors');
  viatjar(p, n, 'verdant');
  anar(p, n, 'verdant_jardi');
  p.talk('fidel', 'inversora', 'sac');
  expect(n.flag('fidel_admet')).toBe(true);
  p.use('reg', item('mosca'));
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
  viatjar(p, n, 'ferrum');
  anar(p, n, 'ferrum_carrer');
  p.talk('rosa', 'vestit');
  anar(p, n, 'ferrum_sindicat');
  p.do('pickUp', 'bagul');
  p.use('vestit', item('mosca'));
  amb(p, 'vet');
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
  amb(p, 'iri');
  p.do('use', 'escenari');
  p.talk('subhasta', 'oferta');
  p.talk('subhasta', 'contracte');
  amb(p, 'vet');
  for (const v of ['t2', 'aqua', 'ferrum']) {
    p.use('claus', `pany_${v}`);
    p.do('push', `pany_${v}`);
  }
  expect(n.getVar('preu_aigua')).toBe(31);
  punt.f('e8');
  p.do('pull', 'palanca');
  expect(n.flag('reserva_oberta')).toBe(true);
}

