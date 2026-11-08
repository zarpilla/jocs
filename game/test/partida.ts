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

/** La Vet escriu en un tros nou del cartell i ho envia des de la cel·la (acaba amb l'Iri). */
function escriureIEnviar(p: Jugador, nota: string) {
  p.do('open', 'porta_passadis');
  p.do('pickUp', 'cartell');
  p.use('llapis_ulls', item('tros_cartell'));
  p.do('open', 'porta_cella');
  p.use(nota, 'panell');
}

/**
 * L'Acte 2 sencer pel camí més curt (la palanca per peces, sense plànols ni Mira): comença amb la Vet
 * al passadís i acaba amb la Vet a la cel·la, just quan comença l'Acte 3.
 */
export function jugarActe2(p: Jugador) {
  // La comporta
  p.do('open', 'porta_hangar');
  p.do('open', 'porta_passadis');
  p.do('open', 'porta_cella');
  p.do('pickUp', 'panell');
  p.do('open', 'porta');
  p.do('pickUp', 'cartell');
  p.do('open', 'porta_hangar');
  p.use('clau_anglesa', 'comporta');
  p.use('llapis_ulls', item('tros_cartell'));
  p.do('open', 'porta_passadis');
  p.do('open', 'porta_cella');
  p.use('nota_mida', 'panell');
  p.do('look', item('nota_mida'));
  p.goTo('fabrica_calderes');
  p.do('open', 'porta_moll');
  p.do('pickUp', 'serra');
  p.use('serra', 'biga_acer');
  p.goTo('fabrica_calderes');
  p.goTo('fabrica_cambra');
  for (const n of [1, 2, 3]) {
    p.use(`tram_biga_${n}`, 'cambra');
    if (n < 3) p.switchTo('iri');
  }
  p.use('tram_biga_1', item('tram_biga_2'));
  p.do('open', 'porta');
  p.do('open', 'porta_hangar');
  p.use('biga_muntada', 'comporta');
  // El diapasó
  p.do('push', 'llancadora');
  p.do('open', 'porta_passadis');
  p.do('open', 'porta_cella');
  p.do('pickUp', 'llitera');
  p.do('pull', item('molla'));
  p.do('pull', item('molla'));
  p.do('open', 'porta');
  p.do('open', 'porta_hangar');
  p.use('molla', 'llancadora');
  p.do('open', 'porta_passadis');
  p.do('open', 'porta_cella');
  p.use('molla', 'panell');
  p.do('look', item('molla'));
  p.goTo('fabrica_calderes');
  p.do('pickUp', 'tauler');
  p.use('segell', item('formulari_27b'));
  p.use('segell', item('formulari_segellat'));
  p.goTo('fabrica_magatzem');
  p.talk('cargol', 'diapaso');
  p.goTo('fabrica_calderes');
  p.do('open', 'porta_moll');
  p.do('pickUp', 'llima');
  p.use('llima', item('diapaso'));
  p.use('llima', item('diapaso'));
  p.use('diapaso', item('molla'));
  p.goTo('fabrica_calderes');
  p.goTo('fabrica_cambra');
  p.use('diapaso', 'cambra');
  p.do('open', 'porta');
  p.do('open', 'porta_hangar');
  p.use('diapaso', 'llancadora');
  // La vàlvula
  escriureIEnviar(p, 'nota_pressio');
  p.do('look', item('nota_pressio'));
  p.goTo('fabrica_calderes');
  p.do('open', 'porta_moll');
  p.do('close', 'conducte');
  p.switchTo('vet');
  p.do('open', 'porta');
  p.do('open', 'porta_hangar');
  escriureIEnviar(p, 'nota_massa');
  p.do('look', item('nota_massa'));
  p.goTo('fabrica_calderes');
  p.do('open', 'porta_moll');
  p.do('open', 'conducte');
  p.switchTo('vet');
  p.do('open', 'porta');
  p.do('open', 'porta_hangar');
  p.do('push', 'llancadora');
  // L'arxiu i els noms
  p.use('clau_anglesa', 'escala');
  p.do('open', 'escala');
  p.do('look', 'expedient_iri');
  p.do('open', 'escala_hangar');
  escriureIEnviar(p, 'nota_vet_nom');
  p.do('look', item('nota_vet_nom'));
  p.use('llapis', item('llibreta_torn'));
  p.goTo('fabrica_calderes');
  p.goTo('fabrica_cambra');
  p.use('nota_iri_nom', 'cambra');
  p.do('look', item('nota_iri_nom'));
}
