import type { WorldPort } from './ports.js';
import { chosenKey, seenKey, type NarrativeState } from './state.js';
import type { CompareOp, Condition, Scalar } from './types.js';

export interface ConditionContext {
  state: NarrativeState;
  world: WorldPort;
}

export function compare(a: Scalar | undefined, op: CompareOp, b: Scalar): boolean {
  switch (op) {
    case '==': return a === b;
    case '!=': return a !== b;
    case '>': return (a as number) > (b as number);
    case '>=': return (a as number) >= (b as number);
    case '<': return (a as number) < (b as number);
    case '<=': return (a as number) <= (b as number);
  }
}

/** Avalua una condició. Sense condició (`undefined`) és certa. */
export function evaluate(cond: Condition | undefined, ctx: ConditionContext): boolean {
  if (!cond) return true;
  const { state, world } = ctx;
  const expect = (value: boolean, is: boolean | undefined) => value === (is ?? true);

  if ('all' in cond) return cond.all.every((c) => evaluate(c, ctx));
  if ('any' in cond) return cond.any.some((c) => evaluate(c, ctx));
  if ('not' in cond) return !evaluate(cond.not, ctx);
  if ('flag' in cond) return expect(state.flags[cond.flag] === true, cond.is);
  if ('var' in cond) return compare(state.vars[cond.var], cond.op, cond.value);
  if ('hasItem' in cond) return expect(world.hasItem(cond.hasItem, cond.who), cond.is);
  if ('protagonist' in cond) return world.activeProtagonist() === cond.protagonist;
  if ('remembers' in cond) {
    const { who, fact, atLeast = 1 } = cond.remembers;
    return expect((state.memory[who]?.facts[fact] ?? 0) >= atLeast, cond.is);
  }
  if ('relation' in cond) {
    const { who, op, value } = cond.relation;
    return compare(state.memory[who]?.relation ?? 0, op, value);
  }
  if ('quest' in cond) {
    const status = state.quests[cond.quest]?.status ?? 'inactive';
    return Array.isArray(cond.status) ? cond.status.includes(status) : status === cond.status;
  }
  if ('objective' in cond) {
    const { quest, objective } = cond.objective;
    return expect(state.quests[quest]?.objectives[objective] === true, cond.is);
  }
  if ('visited' in cond) return expect(world.hasVisited(cond.visited), cond.is);
  if ('inRoom' in cond) return world.currentRoom() === cond.inRoom;
  if ('seen' in cond) {
    const { dialogue, node } = cond.seen;
    return expect((state.dialogue.seen[seenKey(dialogue, node)] ?? 0) > 0, cond.is);
  }
  if ('chosen' in cond) {
    const { dialogue, node, choice } = cond.chosen;
    return expect((state.dialogue.chosen[chosenKey(dialogue, node, choice)] ?? 0) > 0, cond.is);
  }
  throw new Error(`Condició desconeguda: ${JSON.stringify(cond)}`);
}
