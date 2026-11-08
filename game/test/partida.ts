/**
 * Ajudes per als tests de partida: una partida sense gràfics i el recorregut sencer de l'Acte 1.
 */
import { expect } from 'vitest';
import { HeadlessPlayer, MemoryWorld, Narrative } from '@aventura/narrative-core';
import { content, locales } from '../index.js';
import { installGameLogic } from '../logic/index.js';

export const keys = (lines: { key: string }[]) => lines.map((l) => l.key);
export const texts = (lines: { text: string }[]) => lines.map((l) => l.text).join(' ');

/**
 * Partida nova. Amb `checkHints`, després de cada acció del jugador hi ha d'haver alguna pista per
 * a l'una o l'altra protagonista, fins que es compleixi `fins` (per defecte, obrir la comporta).
 */
export function partida(opts: { checkHints?: boolean; fins?: string } = {}) {
  const world = new MemoryWorld();
  const n = new Narrative({ content, locales, world });
  installGameLogic(n);
  const player = new HeadlessPlayer(n, world);
  player.newGame();
  const fins = opts.fins ?? 'comporta_oberta';
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

type Jugador = ReturnType<typeof partida>['p'];
const item = (id: string) => ({ kind: 'item' as const, id });

/** L'Acte 1 sencer, pel camí més curt: acaba amb la Vet al passadís. */
export function jugarActe1(p: Jugador) {
  p.do('pickUp', 'tauler');
  p.goTo('fabrica_magatzem');
  p.talk('cargol', 'clau');
  p.do('pickUp', 'plomall');
  p.goTo('fabrica_calderes');
  p.use('plomall', 'capatas');
  p.do('pickUp', 'segell');
  p.use('segell', item('formulari_27b'));
  p.goTo('fabrica_magatzem');
  p.talk('cargol', 'clau', 'dia');
  p.goTo('fabrica_calderes');
  p.use('clau_cambra', 'porta_cambra');
  p.use('clau_anglesa', 'palanca');
  p.do('push', 'panell');
  p.use('clau_anglesa', 'panell');
  p.use('clau_anglesa', 'panell');
  p.do('pickUp', 'avis');
  p.talk('mos', 'familia', 'llapis_demanar', 'elogiar');
  p.use('llapis_ulls', item('avis_reciclatge'));
  p.use('nota_vet', 'panell');
  p.do('push', 'panell');
  p.switchTo('iri');
  p.do('push', 'boto');
  p.do('look', item('nota_vet'));
  p.use('llapis', item('llibreta_torn'));
  p.use('nota_iri', 'cambra');
  p.do('look', item('nota_iri'));
  p.do('look', 'porta');
  p.do('pickUp', 'llitera');
  p.use('llapis_ulls', item('fullet_reeducacio'));
  p.use('nota_pany', 'panell');
  p.do('look', item('nota_pany'));
  p.goTo('fabrica_calderes');
  p.do('pickUp', 'tauler');
  p.goTo('fabrica_magatzem');
  p.use('segell', item('formulari_27b'));
  p.use('segell', item('formulari_segellat'));
  p.talk('cargol', 'imant');
  p.goTo('fabrica_calderes');
  p.goTo('fabrica_cambra');
  p.use('imant_ferro9', 'cambra');
  p.use('imant_ferro9', 'porta');
}
