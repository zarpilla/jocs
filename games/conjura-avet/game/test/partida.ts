/**
 * Ajudes per als tests de partida: una partida sense gràfics que, si es vol, comprova que després de cada acció hi
 * hagi alguna pista, per a qui juga o per a l'altra (als trams oberts, «ara li toca a l'altra»).
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
      if (typeof value !== 'function' || !['do', 'use', 'talk', 'goTo', 'switchTo'].includes(String(prop))) return value;
      return (...args: unknown[]) => {
        const result = (value as (...a: unknown[]) => unknown).apply(target, args);
        if (!n.flag('final_avet')) {
          const hi = n.activeHints().length > 0 || n.hintForOther() !== null;
          expect(hi, `Sense pistes després de ${String(prop)}(${JSON.stringify(args)}) a ${world.room} (${world.active})`).toBe(true);
        }
        return result;
      };
    },
  });
  return { n, p, world };
}

export type Jugador = ReturnType<typeof partida>['p'];
