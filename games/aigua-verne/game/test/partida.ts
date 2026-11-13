/**
 * Ajudes per als tests de partida: una partida sense gràfics, i caminar per les portes.
 */
import { expect } from 'vitest';
import { HeadlessPlayer, MemoryWorld, Narrative } from '@aventura/narrative-core';
import { content, locales } from '../index.js';
import { installGameLogic } from '../logic/index.js';

export const item = (id: string) => ({ kind: 'item' as const, id });

/** Partida nova. Amb `checkHints`, després de cada acció hi ha d'haver alguna pista per a una de les dues. */
export function partida(opts: { checkHints?: boolean } = {}) {
  const world = new MemoryWorld();
  const n = new Narrative({ content, locales, world });
  installGameLogic(n);
  const player = new HeadlessPlayer(n, world);
  player.newGame();
  const p = !opts.checkHints ? player : new Proxy(player, {
    get(target, prop, receiver) {
      const value = Reflect.get(target, prop, receiver);
      if (typeof value !== 'function' || !['do', 'use', 'talk', 'goTo', 'switchTo'].includes(String(prop))) return value;
      return (...args: unknown[]) => {
        const result = (value as (...a: unknown[]) => unknown).apply(target, args);
        if (!n.flag('reserva_oberta')) {
          const any = n.activeHints().length > 0 || altraTePista(n, world);
          expect(any, `Sense pistes després de ${String(prop)}(${JSON.stringify(args)}) a ${world.room}`).toBe(true);
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

const MAPA: Record<string, Record<string, string>> = {
  granja_pati: { granja_casa: 'porta_casa', granja_graner: 'porta_graner', port_terra2: 'cami_port' },
  granja_casa: { granja_pati: 'porta' },
  granja_graner: { granja_pati: 'porta' },
  port_terra2: { granja_pati: 'cami_granja', cantimplora_bodega: 'rampa' },
  cantimplora_bodega: { cantimplora_pont: 'escala', port_terra2: 'rampa', aqua_port: 'rampa', ferrum_carrer: 'rampa', verdant_jardi: 'rampa' },
  cantimplora_pont: { cantimplora_bodega: 'escala' },
  aqua_port: { cantimplora_bodega: 'rampa', aqua_fons: 'cistella' },
  aqua_fons: { aqua_port: 'cistella', casa_juana: 'porta_juana' },
  casa_juana: { aqua_fons: 'porta' },
  ferrum_carrer: { cantimplora_bodega: 'rampa', ferrum_sindicat: 'porta_sindicat', fosa_forn: 'porta_fosa' },
  ferrum_sindicat: { ferrum_carrer: 'porta' },
  fosa_forn: { ferrum_carrer: 'porta', fosa_colada: 'pas' },
  fosa_colada: { fosa_forn: 'pas' },
  verdant_jardi: { cantimplora_bodega: 'rampa', verdant_residencia: 'porta_residencia', verdant_cobert: 'porta_cobert' },
  verdant_cobert: { verdant_jardi: 'porta' },
  verdant_residencia: { verdant_jardi: 'porta' },
  palau_galeria: { palau_salo: 'porta_salo' },
  palau_salo: { palau_galeria: 'porta_galeria' },
  palau_servei: { palau_control: 'ascensor' },
  palau_control: { palau_servei: 'ascensor' },
};
const PORT: Record<string, string> = { terra2: 'port_terra2', aqua: 'aqua_port', ferrum: 'ferrum_carrer', verdant: 'verdant_jardi' };

function veins(n: Narrative, r: string) {
  const v = { ...(MAPA[r] ?? {}) };
  if (r === 'cantimplora_bodega') {
    for (const k of Object.values(PORT)) delete v[k];
    v[PORT[String(n.getVar('planeta'))]!] = 'rampa';
  }
  return v;
}

/** Camina fins a una sala per les portes. */
export function anar(p: Jugador, n: Narrative, cap: string) {
  const prev = new Map<string, string>([[p.room!, '']]);
  const cua = [p.room!];
  while (cua.length) {
    const r = cua.shift()!;
    if (r === cap) break;
    for (const s of Object.keys(veins(n, r))) if (!prev.has(s)) { prev.set(s, r); cua.push(s); }
  }
  if (!prev.has(cap)) throw new Error(`No hi ha camí de ${p.room} a ${cap}`);
  const cami: string[] = [];
  for (let r = cap; r !== p.room; r = prev.get(r)!) cami.unshift(r);
  for (const s of cami) {
    const porta = veins(n, p.room!)[s]!;
    p.do('walkTo', porta);
    if (p.room !== s) throw new Error(`No s'ha pogut passar de ${p.room} a ${s} per «${porta}»: ${p.transcript.slice(-3).join(' | ')}`);
  }
}

/** Viatja amb la Cantimplora (l'Iri, des del pont). */
export function viatjar(p: Jugador, n: Narrative, planeta: string) {
  if (p.active !== 'iri') p.switchTo('iri');
  anar(p, n, 'cantimplora_pont');
  p.do('use', 'mapa');
  // el mapa és un diàleg: el condueix `talk`
  p.talk('mapa', planeta);
  expect(n.getVar('planeta')).toBe(planeta);
}

export function amb(p: Jugador, who: string) {
  if (p.active !== who) p.switchTo(who);
}
