/**
 * Ajudes per als tests de partida: una partida sense gràfics que, si es vol, comprova que després de cada acció hi
 * hagi alguna pista per a qui juga (a L'Última Arrel no es pot canviar de germana: la pista ha de ser de qui juga).
 */
import { expect } from 'vitest';
import { HeadlessPlayer, MemoryWorld, Narrative } from '@aventura/narrative-core';
import { content, locales } from '../index.js';
import { installGameLogic } from '../logic/index.js';

export const item = (id: string) => ({ kind: 'item' as const, id });

export function partida(opts: { checkHints?: boolean } = {}) {
  const world = new MemoryWorld();
  const n = new Narrative({ content, locales, world });
  installGameLogic(n);
  const player = new HeadlessPlayer(n, world);
  player.newGame();
  const p = !opts.checkHints ? player : new Proxy(player, {
    get(target, prop, receiver) {
      const value = Reflect.get(target, prop, receiver);
      if (typeof value !== 'function' || !['do', 'use', 'talk', 'goTo'].includes(String(prop))) return value;
      return (...args: unknown[]) => {
        const result = (value as (...a: unknown[]) => unknown).apply(target, args);
        if (!n.flag('final_taula')) {
          expect(n.activeHints().length, `Sense pistes després de ${String(prop)}(${JSON.stringify(args)}) a ${world.room}`).toBeGreaterThan(0);
        }
        return result;
      };
    },
  });
  return { n, p, world };
}

export type Jugador = ReturnType<typeof partida>['p'];
