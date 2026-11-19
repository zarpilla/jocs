/**
 * El camí de la partida, escena per escena (el fan servir els tests i les proves d'exploració).
 */
import { expect } from 'vitest';
import type { Narrative } from '@aventura/narrative-core';
import { item, type Jugador } from './partida.js';

export function acte1(p: Jugador, n: Narrative) {
  // Escena 1: la vora del bosc (Iri)
  expect(p.room).toBe('vora_bosc');
  expect(p.active).toBe('iri');
  p.do('look', 'cartell');
  p.do('pickUp', 'cargol');
  p.do('use', 'campaneta');
  expect(n.flag('espora_respon')).toBe(true);
  p.do('pull', 'estaca');
  p.do('push', 'estaca');
  p.do('pull', 'estaca');
  expect(p.room).toBe('centraleta');
  // Escena 2: la centraleta
  p.use('centim', item('llimona'));
  p.use('cargol', item('llimona_centim'));
  p.use('pila_llimona', 'radar');
  expect(n.flag('radar_ences')).toBe(true);
  p.do('pickUp', 'fil_saba');
  p.use('lupa', 'arrel_1');
  p.use('lupa', 'arrel_2');
  p.use('fil_saba', 'arrel_2');
  expect(n.flag('xarxa_encesa')).toBe(true);
  p.do('use', 'corn');
  p.use('walkie', 'corn');
  expect(n.flag('crit_gravat')).toBe(true);
  expect(p.active).toBe('vet');
}

export function acte2(p: Jugador, n: Narrative) {
  // Escena 3: el campament de les fades (Vet)
  expect(p.room).toBe('campament_fades');
  p.talk('urtica', 'naturaplus', 'adeu');
  p.do('give', 'urtica', 'pot_melmelada');
  expect(n.flag('fades_amigues')).toBe(true);
  p.do('use', 'gronxador');
  expect(n.flag('pol_len_collit')).toBe(true);
  expect(p.active).toBe('iri');
  expect(p.inventory('vet')).toContain('xiulet');
  // Escena 4: el toll dels gripaus (Iri)
  expect(p.room).toBe('toll_gripaus');
  p.talk('bufo', 'paper', 'adeu');
  p.do('pull', 'tap_plastics');
  p.use('estaca', 'tap_plastics');
  p.do('use', 'comporta');
  p.talk('gripau', 'ajuda');
  expect(n.flag('aigua_tornada')).toBe(true);
  p.talk('bufo');
  expect(n.flag('plans_segellats')).toBe(true);
  expect(p.active).toBe('vet');
  // Escena 5: la caseta d'obra (Vet)
  expect(p.room).toBe('caseta_obra');
  p.talk('pla', 'altaveu', 'adeu');
  p.do('pull', 'arbre_wifi');
  expect(n.flag('pla_fora')).toBe(true);
  p.use('walkie', 'altaveu');
  expect(n.flag('altaveu_canal7')).toBe(true);
  expect(p.active).toBe('iri');
}

export function acte3(p: Jugador, n: Narrative) {
  // Escena 6: la Zona Zero (Iri)
  expect(p.room).toBe('zona_zero');
  expect(p.inventory('iri')).toContain('xiulet');
  expect(n.getVar('discurs')).toBe(1);
  p.use('xiulet', 'sensors');
  expect(n.getVar('discurs')).toBe(2);
  p.do('talkTo', 'bufo');
  expect(n.getVar('discurs')).toBe(3);
  p.use('walkie', 'altaveu');
  expect(n.flag('presentacio_feta')).toBe(true);
  // Escena 7: el bosc obert (Vet)
  expect(p.active).toBe('vet');
  expect(p.room).toBe('bosc_obert');
  p.do('use', 'taula');
  expect(n.flag('final_taula')).toBe(true);
}
