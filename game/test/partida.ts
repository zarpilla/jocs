/**
 * Ajudes per als tests de partida: una partida sense gràfics.
 */
import { expect } from 'vitest';
import { HeadlessPlayer, MemoryWorld, Narrative } from '@aventura/narrative-core';
import { content, locales } from '../index.js';
import { installGameLogic } from '../logic/index.js';

export const keys = (lines: { key: string }[]) => lines.map((l) => l.key);
export const texts = (lines: { text: string }[]) => lines.map((l) => l.text).join(' ');

/**
 * Partida nova. Amb `checkHints`, després de cada acció del jugador hi ha d'haver alguna pista per
 * a l'una o l'altra protagonista, fins que es compleixi el flag `fins`.
 */
export function partida(opts: { checkHints?: boolean; fins?: string } = {}) {
  const world = new MemoryWorld();
  const n = new Narrative({ content, locales, world });
  installGameLogic(n);
  const player = new HeadlessPlayer(n, world);
  player.newGame();
  const fins = opts.fins ?? 'aeroport_fet';
  const p = !opts.checkHints ? player : new Proxy(player, {
    get(target, prop, receiver) {
      const value = Reflect.get(target, prop, receiver);
      if (typeof value !== 'function' || !['do', 'use', 'talk', 'goTo', 'switchTo'].includes(String(prop))) return value;
      return (...args: unknown[]) => {
        const result = (value as (...a: unknown[]) => unknown).apply(target, args);
        if (!n.flag(fins)) {
          const any = n.activeHints().length > 0 || altraTePista(n, world);
          expect(any, `Sense pistes després de ${String(prop)}(${JSON.stringify(args)})`).toBe(true);
        }
        return result;
      };
    },
  });
  return { n, p, world };
}

function altraTePista(n: Narrative, world: MemoryWorld) {
  const current = world.active;
  world.active = n.content.manifest.protagonists.find((x) => x !== current)!;
  const has = n.activeHints().length > 0;
  world.active = current;
  return has;
}

export type Jugador = ReturnType<typeof partida>['p'];
export const item = (id: string) => ({ kind: 'item' as const, id });

export interface OpcionsActe1 {
  /** Què es dona a en Diu per distreure'l. */
  sacrifici?: 'caixa' | 'auricular' | 'pizza';
  /** La Vet es fa l'entrepà abans de marxar. */
  entrepa?: boolean;
  /** La Vet li torna el tap a en Puig. */
  tap?: boolean;
  /** La Vet recupera el maletí i les ulleres a l'aeroport. */
  preparacio?: boolean;
  /** L'Iri prova un codi a l'atzar abans que la Vet llegeixi el pòsit (i la Vet ha de plorar). */
  codiDolent?: boolean;
}

/** L'escena 1: de la partida nova fins que la Vet surt de casa. */
export function jugarPis(p: Jugador, o: OpcionsActe1 = {}) {
  p.do('open', 'caixa');
  p.use('cable_xarxa', 'router'); // en Diu el mossega
  p.do('open', 'passaplats');
  p.talk('passaplats', 'cable');
  p.switchTo('vet');
  p.do('pickUp', 'cafetera');
  p.use('cable_alimentacio', 'passaplats');
  p.switchTo('iri');
  if ((o.sacrifici ?? 'caixa') === 'caixa') {
    p.do('pickUp', 'caixa');
    p.use('caixa_cartro', 'diu');
  } else if (o.sacrifici === 'auricular') {
    p.use('auriculars', 'diu');
    p.use('auriculars', 'diu');
  } else {
    p.talk('passaplats', 'pizza');
    p.switchTo('vet');
    p.do('open', 'nevera');
    p.do('pickUp', 'pizza_nevera');
    p.use('pizza', 'passaplats');
    p.switchTo('iri');
    p.use('pizza', 'diu');
  }
  p.do('pickUp', 'fibra');
  p.use('cable_xarxa', 'router');
  p.use('cable_alimentacio', 'router');
  p.switchTo('vet');
  if (o.entrepa) {
    p.do('open', 'nevera');
    p.do('pickUp', 'tonyina');
  }
  p.do('use', 'porta');
}

/** L'escena 2: del bar fins a l'aeroport. */
export function jugarBar(p: Jugador, o: OpcionsActe1 = {}) {
  p.talk('marcel');
  // el tap
  p.talk('puig', 'cafe', 'adeu');
  p.do('pickUp', 'tap_barra');
  p.do('give', 'marcel', 'tap');
  // la recepta
  p.do('use', 'porta_rebost');
  p.do('look', 'calaix');
  p.do('use', 'porta');
  p.talk('trucada', 'pany', 'adeu');
  p.do('look', 'retol');
  p.talk('trucada', 'contrasenya', 'adeu');
  p.switchTo('iri');
  p.do('use', 'ordinadors');
  p.switchTo('vet');
  p.do('use', 'porta_rebost');
  p.do('open', 'calaix');
  p.do('use', 'porta');
  p.do('give', 'marcel', 'recepta');
  // el comandament
  p.talk('puig', 'comandament', 'adeu');
  p.talk('trucada', 'trucada', 'adeu');
  p.switchTo('iri');
  p.do('use', 'ordinadors');
  p.switchTo('vet');
  p.do('pickUp', 'comandament_barra');
  p.do('give', 'marcel', 'comandament');
  // el que sap en Marcel, i la trucada a l'Iri
  p.talk('marcel', 'servidor', 'clau', 'tub', 'vol', 'ballester', 'neta', 'gracies');
  p.talk('trucada', 'resum', 'robot', 'adeu');
  if (o.tap) p.do('give', 'puig', 'tap');
  p.do('use', 'porta');
}

/** L'escena 3: l'aeroport, fins a l'avió (i el final provisional de l'Acte 1). */
export function jugarAeroport(p: Jugador, o: OpcionsActe1 = {}) {
  if (o.preparacio) {
    p.do('look', 'maleti');
    p.talk('empleat', 'maleti', 'llimona', 'adeu');
    p.do('pickUp', 'ulleres');
  }
  p.talk('soler', 'fill', 'nom_curt', 'edat_curt', 'roba_curt');
  if (o.codiDolent) {
    p.switchTo('iri');
    p.do('use', 'teclat');
    p.switchTo('vet');
    p.talk('soler', 'plorar');
  }
  p.do('look', 'taulell');
  p.switchTo('iri');
  p.do('use', 'teclat');
  p.do('use', 'terminal');
  p.do('push', 'impressora');
  p.do('pickUp', 'impressora');
  p.do('use', 'porta');
  p.switchTo('vet');
  p.do('talkTo', 'nen');
}

export function jugarActe1(p: Jugador, o: OpcionsActe1 = {}) {
  jugarPis(p, o);
  jugarBar(p, o);
  jugarAeroport(p, o);
}
