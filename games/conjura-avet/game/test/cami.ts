/**
 * El camí de la partida, acte per acte (el fan servir els tests i les proves d'exploració). Als trams oberts, aquest
 * és un dels ordres possibles: `ordres.ts` en prova un altre.
 */
import { expect } from 'vitest';
import type { Narrative } from '@aventura/narrative-core';
import { item, type Jugador } from './partida.js';

/** Tutorial: l'Iri a l'avet, fins que detenen el pare i arriba la Vet. */
export function tutorial(p: Jugador, n: Narrative) {
  expect(p.room).toBe('mur_avet');
  expect(p.active).toBe('iri');
  p.use('guants', 'branques');
  p.use('olla', 'branca_trencada');
  p.do('look', 'arrels');
  p.do('pickUp', 'cera');
  p.do('look', 'ordre');
  p.talk('ponc');
  expect(n.flag('pare_detingut')).toBe(true);
  expect(n.getVar('fase')).toBe(1);
  expect(n.canSwitch()).toBe(true);
}

export function acte1(p: Jugador, n: Narrative) {
  tutorial(p, n);
  p.do('give', 'vet', 'cera');
  // La Vet llegeix l'ordre.
  p.switchTo('vet');
  expect(p.room).toBe('mur_avet');
  p.talk('ponc', 'privat');
  expect(n.flag('ordre_llegida')).toBe(true);
  // La plaça: totes dues.
  p.do('walkTo', 'carrer');
  expect(p.room).toBe('placa_sant_pol');
  p.do('look', 'campanar');
  p.talk('sanca', 'canem', 'tracte', 'adeu');
  p.switchTo('iri');
  p.do('walkTo', 'carrer');
  expect(p.room).toBe('placa_sant_pol');
  p.switchTo('vet');
  p.do('give', 'iri', 'canem');
  p.switchTo('iri');
  p.use('canem', 'campanar');
  p.do('pull', 'campanar');
  expect(n.flag('bonfill_campanar')).toBe(true);
  p.switchTo('vet');
  p.do('look', 'queixa');
  expect(n.flag('queixa_copiada')).toBe(true);
  // El pont: l'Iri.
  p.switchTo('iri');
  p.do('walkTo', 'carrer');
  p.do('walkTo', 'cami_riu');
  expect(p.room).toBe('pont_ter');
  p.use('destral', 'sobreeixidor');
  p.use('pot_resina', 'barca');
  p.use('salabre', 'comporta');
  expect(p.inventory('iri')).toContain('serra');
  p.do('walkTo', 'cami');
  // La Vet torna a l'avet, i l'Iri li dona la serra.
  p.switchTo('vet');
  p.do('walkTo', 'carrer');
  expect(p.room).toBe('mur_avet');
  p.switchTo('iri');
  p.do('give', 'vet', 'serra');
  // El claustre: la Vet.
  p.switchTo('vet');
  p.do('walkTo', 'porta_monestir');
  expect(p.room).toBe('claustre');
  p.use('cera', 'pica');
  p.use('carbonet', item('cera'));
  expect(p.room).toBe('calc');
  p.do('use', 'pergami'); p.do('use', 'pergami'); p.do('use', 'pergami');
  expect(p.room).toBe('claustre');
  expect(n.flag('segell_emma_vist')).toBe(true);
  p.talk('gueraula', 'canta', 'sencera', 'adeu');
  p.talk('ingilberga', 'arxiu', 'adeu');
  p.do('give', 'ingilberga', 'tauleta');
  p.do('give', 'ingilberga', 'serra');
  p.talk('ingilberga', 'ordre', 'entrar', 'monges');
  expect(n.flag('abadessa_convencuda')).toBe(true);
  expect(n.getVar('fase')).toBe(2);
}

export function acte2(p: Jugador, n: Narrative) {
  // La preparació: l'Iri a la bugaderia, la Vet a l'apotecaria.
  p.switchTo('iri');
  expect(p.room).toBe('claustre');
  p.do('give', 'vet', 'pot_resina');
  expect(p.inventory('vet')).toContain('pegot');
  p.do('walkTo', 'porta_bugaderia');
  expect(p.room).toBe('bugaderia');
  p.do('open', 'bagul');
  p.use('clofolles', 'tina');
  p.do('pickUp', 'llenya_alzina');
  p.use('alzina', 'fogo');
  p.use('pot_resina', 'fogo');
  p.do('pickUp', 'tisores');
  p.do('walkTo', 'porta');
  p.switchTo('vet');
  p.do('walkTo', 'porta_apotecaria');
  expect(p.room).toBe('apotecaria');
  p.talk('gueraula', 'tint', 'dormir', 'veu', 'adeu2');
  p.do('pickUp', 'atramentum');
  p.do('pickUp', 'cardo');
  p.do('pickUp', 'mel');
  p.do('pickUp', 'llar');
  p.use('mel', item('carbo'));
  p.do('use', 'flasco_sense_nom');
  p.use('ploma', item('pergamins'));
  p.use('pegot', item('salconduit_brut'));
  p.use('cera', item('salconduit_resina'));
  p.do('walkTo', 'porta');
  expect(p.room).toBe('claustre');
  p.do('give', 'iri', 'caparros');
  p.switchTo('iri');
  p.do('walkTo', 'porta_bugaderia');
  p.use('caparros', 'tina');
  p.use('tuniques', 'tina');
  p.use('tisores', item('habits'));
  p.do('walkTo', 'porta');
  p.do('give', 'vet', 'retalls');
  p.switchTo('vet');
  p.do('walkTo', 'porta_apotecaria');
  p.use('cardo', item('retalls'));
  p.use('pegot', item('llana'));
  p.talk('gueraula', 'llest');
  expect(n.flag('disfressades')).toBe(true);
  // La porteria: l'Iri.
  expect(p.active).toBe('iri');
  expect(p.room).toBe('porteria');
  expect(n.canSwitch()).toBe(false);
  p.talk('bonfill', 'tres', 'dona', 'tos');
  // La cuina: la Vet.
  expect(p.active).toBe('vet');
  expect(p.room).toBe('cuina');
  p.talk('sunifred', 'ofici', 'adeu_c');
  expect(n.flag('signe_vist')).toBe(true);
  p.use('mocador', 'pila_olles');
  p.use('valeriana', 'gerra');
  p.do('use', 'gerra');
  expect(n.flag('sunifred_dorm')).toBe(true);
  p.use('ploma', 'sunifred');
  expect(n.flag('claus_agafades')).toBe(false);
  p.talk('sunifred');
  p.talk('sunifred');
  p.use('ploma', 'sunifred');
  expect(p.room).toBe('scriptorium');
}

export function acte3(p: Jugador, n: Narrative) {
  p.use('tauleta', 'gombau');
  p.use('rascador', 'espelma_hores');
  expect(n.flag('canonges_fora')).toBe(true);
  p.use('carbonet', 'pergami');
  expect(p.room).toBe('calc');
  p.do('use', 'pergami'); p.do('use', 'pergami'); p.do('use', 'pergami');
  expect(p.room).toBe('scriptorium');
  expect(p.inventory('vet')).toContain('carta_calcada');
  p.use('claus', 'porta_capitular');
  expect(n.getVar('fase')).toBe(5);
  // L'arxiu: l'Iri; els canonges tornen i la Vet se'ls treu de sobre.
  p.switchTo('iri');
  expect(p.room).toBe('arxiu');
  p.do('look', 'bagul_sunifred');
  p.use('claus', 'bagul_sunifred');
  p.do('use', 'bagul_sunifred');
  p.do('pull', 'tapis');
  p.do('push', 'estendard');
  p.do('pull', 'contrapes');
  expect(n.flag('canonges_tornen')).toBe(true);
  p.switchTo('vet');
  p.use('tauleta', 'gombau');
  expect(n.flag('canonges_tornen')).toBe(false);
  p.switchTo('iri');
  p.do('open', 'bagul_sunifred');
  p.do('pickUp', 'cofre');
  expect(n.getVar('fase')).toBe(6);
  p.do('push', 'banc_fons');
  p.do('use', 'trapa');
  // El molí.
  expect(p.room).toBe('moli');
  p.do('talkTo', 'finestra_dalt');
  p.use('carta_emma', item('pot_apotecari'));
  p.use('pot_resina', item('pot_cartes'));
  p.use('destral', 'falca');
  p.do('push', 'pastera');
  p.do('talkTo', 'finestra_dalt');
  expect(n.getVar('fase')).toBe(7);
  expect(p.room).toBe('mur_avet');
}

export function acte4(p: Jugador, n: Narrative) {
  // El matí: tres testimonis i un segell.
  p.switchTo('vet');
  p.do('give', 'ponc', 'cera');
  expect(n.flag('segell_acceptat')).toBe(true);
  p.do('walkTo', 'carrer');
  p.talk('sanca', 'creu');
  expect(n.flag('testimoni_sanca')).toBe(true);
  p.switchTo('iri');
  p.do('walkTo', 'cami_riu');
  p.do('push', 'comporta');
  p.talk('ermessenda');
  p.do('push', 'barca');
  p.talk('joanet');
  expect(n.flag('testimoni_joanet')).toBe(true);
  p.do('walkTo', 'cami');
  p.talk('ponc');
  // El judici: la Vet.
  expect(p.active).toBe('vet');
  expect(p.room).toBe('judici');
  p.do('give', 'ponc', 'serra');
  p.do('give', 'ponc', 'tauleta');
  p.do('talkTo', 'iri');
  p.do('give', 'ponc', 'carta_emma');
  p.do('give', 'ponc', 'carta_calcada');
  expect(n.flag('judici_guanyat')).toBe(true);
  // L'epíleg: l'Iri.
  expect(p.active).toBe('iri');
  expect(p.room).toBe('epileg');
  p.do('pickUp', 'carretilla');
  p.do('talkTo', 'sunifred');
  p.use('pala', 'forat_nou');
  p.use('cofre', 'forat_nou');
  p.use('planco', 'forat_nou');
  p.do('look', 'rotul');
  expect(n.flag('final_avet')).toBe(true);
}
