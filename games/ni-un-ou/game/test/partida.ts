/**
 * Ajudes per als tests de partida: una partida sense gràfics, i cada escena jugada pel camí més habitual.
 */
import { expect } from 'vitest';
import { HeadlessPlayer, MemoryWorld, Narrative } from '@aventura/narrative-core';
import { content, locales } from '../index.js';
import { installGameLogic } from '../logic/index.js';

export const keys = (lines: { key: string }[]) => lines.map((l) => l.key);
export const texts = (lines: { text: string }[]) => lines.map((l) => l.text).join(' ');
export const item = (id: string) => ({ kind: 'item' as const, id });

/**
 * Partida nova. Amb `checkHints`, després de cada acció del jugador hi ha d'haver alguna pista per a l'una o
 * l'altra protagonista, fins que s'envien les dades (`enviat`).
 */
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
        if (!n.flag('enviat')) {
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

/** Va d'una sala a una altra seguint les portes (el camí més curt). */
const MAPA: Record<string, Record<string, string>> = {
  camarot_iri: { passadis_baix: 'porta' },
  passadis_baix: { camarot_iri: 'porta_camarot', sala_maquines: 'porta_maquines', pallol: 'porta_pallol', sala_bombes: 'escotilla', passadis: 'escala' },
  sala_maquines: { passadis_baix: 'porta_passadis', taller: 'porta_taller', rebost: 'porta_rebost' },
  taller: { sala_maquines: 'porta' },
  rebost: { sala_maquines: 'porta', diposit2: 'registre' },
  diposit2: { rebost: 'registre' },
  pallol: { passadis_baix: 'porta' },
  sala_bombes: { passadis_baix: 'escotilla' },
  passadis: { menjador: 'porta_menjador', infermeria: 'porta_infermeria', laboratori: 'porta_laboratori', cabina_capitana: 'porta_capitana', pont: 'escala_amunt', passadis_baix: 'escala_avall', coberta_proa: 'porta_proa' },
  menjador: { passadis: 'porta_passadis', cuina: 'porta_cuina', coberta_popa: 'porta_popa' },
  cuina: { menjador: 'porta' },
  infermeria: { passadis: 'porta' },
  laboratori: { passadis: 'porta' },
  cabina_capitana: { passadis: 'porta' },
  pont: { passadis: 'escala', sala_radio: 'porta_radio', pal: 'escala_pal' },
  sala_radio: { pont: 'porta' },
  pal: { pont: 'escala' },
  coberta_popa: { menjador: 'porta', coberta_proa: 'proa' },
  coberta_proa: { coberta_popa: 'popa', passadis: 'porta', caixa_cadenes: 'escotilla' },
  caixa_cadenes: { coberta_proa: 'escotilla' },
};

function cami(des: string, cap: string): string[] {
  const prev = new Map<string, string>([[des, '']]);
  const cua = [des];
  while (cua.length) {
    const r = cua.shift()!;
    if (r === cap) break;
    for (const s of Object.keys(MAPA[r] ?? {})) if (!prev.has(s)) { prev.set(s, r); cua.push(s); }
  }
  const out: string[] = [];
  for (let r = cap; r !== des; r = prev.get(r)!) out.unshift(r);
  return out;
}

/** Camina fins a una sala. */
export function anar(p: Jugador, cap: string) {
  for (const s of cami(p.room!, cap)) {
    const des = p.room!;
    p.do('use', MAPA[des]![s]!);
    expect(p.room, `De ${des} a ${s}`).toBe(s);
  }
}

/** Amb qui juga, i on (canvia de protagonista si cal). */
export function amb(p: Jugador, who: 'iri' | 'vet', sala?: string) {
  if (p.active !== who) p.switchTo(who);
  if (sala) anar(p, sala);
}

export interface Opcions {
  /** Totes les missions dels aliats (per defecte, sí). */
  aliats?: boolean;
}

/** Escena 1: la vàlvula. */
export function escena1(p: Jugador) {
  anar(p, 'sala_maquines');
  p.do('look', 'valvula');
  p.do('look', 'quadre');
  anar(p, 'taller');
  p.do('look', 'tauler');
  p.do('pickUp', 'cisalla');
  anar(p, 'sala_maquines');
  p.use('cisalla', 'quadre');
  p.do('talkTo', item('walkie')); // la Vet es desperta, i el joc hi canvia
  expect(p.active).toBe('vet');
  p.do('pickUp', 'llitera');
  anar(p, 'cuina');
  p.use('travesser', 'munta');
  amb(p, 'iri', 'rebost');
  p.do('pickUp', 'safata');
  anar(p, 'sala_maquines');
  p.use('travesser', 'valvula');
  p.talk('vies', 'borda', 'separador');
  p.do('use', 'quadre'); // en Bastida, i l'Escena 2
}

/** Escena 2: les revisions i la Juana. */
export function escena2(p: Jugador, _o: Opcions = {}) {
  expect(p.active).toBe('vet');
  expect(p.room).toBe('coberta_popa');
  p.do('look', 'plataforma');
  p.talk('bastida', 'mar', 'adeu');
  anar(p, 'infermeria');
  p.talk('fitxes', 'capitana');
  p.talk('capitana', 'juana', 'gasoil', 'fi');
  p.talk('fitxes', 'tomas');
  p.talk('tomas', 'juana', 'clau', 'nit', 'fi');
  p.talk('fitxes', 'nadia');
  p.do('look', 'nadia');
  p.talk('nadia', 'mareig', 'fi');
  p.talk('fitxes', 'marcel');
  p.do('look', 'marcel');
  p.talk('marcel', 'fi');
  anar(p, 'coberta_proa');
  p.talk('juana', 'valvula'); // l'Arenga salpa: Escena 3
}

/** Escena 3: la ràdio (sincronia). */
export function escena3(p: Jugador, o: Opcions = {}) {
  expect(p.room).toBe('infermeria');
  p.talk('bastida', 'temporal', 'adeu');
  if (o.aliats !== false) p.talk('bastida', 'mans', 'adeu');
  amb(p, 'iri');
  expect(p.room).toBe('sala_radio');
  p.do('open', 'panell');
  p.do('look', 'panell');
  p.do('pickUp', 'cable');
  anar(p, 'pallol');
  p.do('pickUp', 'prestatges');
  anar(p, 'sala_radio');
  amb(p, 'vet');
  p.talk('bastida', 'tensio', 'adeu');
  amb(p, 'iri');
  p.use('cable_nou', 'panell');
  p.use('cable_nou', 'panell');
  p.do('use', 'radio');
  p.do('close', 'panell'); // Acte 2
}

/** Escena 4: el portàtil. */
export function escena4(p: Jugador) {
  expect(p.active).toBe('iri');
  expect(p.room).toBe('laboratori');
  p.do('look', 'nota');
  p.do('look', 'llibre');
  p.do('talkTo', item('walkie'));
  p.talk('portatil', 'pili', 'pilar');
  anar(p, 'pont');
  p.use('usb', 'terminal');
  anar(p, 'sala_bombes');
  p.do('look', 'llibre'); // Escena 5
}

/** Escena 5: el parany. */
export function escena5(p: Jugador, o: Opcions = {}) {
  expect(p.room).toBe('laboratori');
  anar(p, 'rebost');
  p.use('llibreta', 'munta');
  amb(p, 'vet');
  expect(p.room).toBe('cuina');
  p.do('pickUp', 'safata');
  amb(p, 'iri');
  p.do('pickUp', 'safata');
  p.talk('paperets', 'flam', 'ernest', 'postres');
  p.do('talkTo', item('walkie'));
  amb(p, 'vet');
  p.do('open', 'armari');
  p.talk('nadia', o.aliats === false ? 'denunciar' : 'aliar'); // Escena 6
}

/** Escena 6: on és la Juana. */
export function escena6(p: Jugador, o: Opcions & { nadia?: boolean } = {}) {
  amb(p, 'iri', 'taller');
  p.do('pickUp', 'cisalla');
  anar(p, 'pallol');
  p.do('look', 'inventari');
  p.talk('marcel', 'gat', o.aliats === false ? 'veritat' : 'guardar');
  anar(p, 'coberta_proa');
  p.do('look', 'escotilla');
  if (o.nadia) {
    amb(p, 'vet', 'menjador');
    p.talk('nadia', 'soroll');
  } else {
    amb(p, 'vet', 'coberta_popa');
    p.talk('bastida', 'nus');
  }
  amb(p, 'iri');
  p.use('cisalla', 'escotilla');
  expect(p.room).toBe('caixa_cadenes');
  p.do('look', 'juana');
  p.do('use', 'escotilla'); // Escena 7
}

/** Escena 7: on ningú no beu. */
export function escena7(p: Jugador, o: { frontisses?: boolean } = {}) {
  expect(p.active).toBe('vet');
  expect(p.room).toBe('infermeria');
  if (o.frontisses) {
    amb(p, 'iri', 'taller');
    p.do('pickUp', 'clau_tubs');
    anar(p, 'rebost');
    p.use('clau_tubs', 'registre');
    p.use('clau_tubs', 'registre');
    anar(p, 'diposit2');
    p.do('open', 'filtre');
    anar(p, 'infermeria');
    return;
  }
  anar(p, 'cuina');
  p.talk('tomas', 'clau7', 'entrepa7');
  anar(p, 'rebost');
  p.do('look', 'registre');
  p.use('clau_tomas', 'registre');
  expect(p.room).toBe('diposit2');
  p.do('open', 'filtre');
  anar(p, 'infermeria'); // Acte 3
}

/** Escena 8: la reunió (amb la Capitana, si hi ha aliats). */
export function escena8(p: Jugador, o: Opcions = {}) {
  expect(p.active).toBe('vet');
  if (o.aliats !== false) {
    amb(p, 'iri');
    expect(p.room).toBe('pont');
    p.use('usb', 'impressora');
    p.use('registre', 'munta');
    amb(p, 'vet', 'cuina');
    p.do('pickUp', 'safata');
    anar(p, 'cabina_capitana');
    p.use('registre', 'contracte');
  }
  amb(p, 'vet', 'menjador');
  p.do('use', 'taula');
  p.talk('reunio', 'marcel', 'bastida', 'gat', 'cisalla', 'pipa', 'correu', 'iri'); // Escena 9
}

/** Escena 9: el satèl·lit (sincronia). */
export function escena9(p: Jugador, o: Opcions = {}) {
  expect(p.room).toBe('sala_maquines');
  amb(p, 'iri');
  expect(p.room).toBe('pont');
  anar(p, 'pal');
  p.do('use', 'antena');
  if (o.aliats === false) p.do('use', 'antena');
  anar(p, 'pont');
  p.do('use', 'terminal');
  amb(p, 'vet');
  // Sense aliats, tampoc la veritat (seria un aliat): l'Iri, el cafè, les arengades i els diners.
  if (o.aliats === false) p.talk('bastida', 'iri', 'cafe', 'arengades', 'diners');
  else p.talk('bastida', 'veritat', 'iri');
  amb(p, 'iri');
  while (!p.narrative.flag('enviat')) p.do('use', 'terminal');
}

export function jugarTot(p: Jugador, o: Opcions & { frontisses?: boolean; nadia?: boolean } = {}) {
  escena1(p);
  escena2(p, o);
  escena3(p, o);
  escena4(p);
  escena5(p, o);
  escena6(p, o);
  escena7(p, o);
  escena8(p, o);
  escena9(p, o);
}
