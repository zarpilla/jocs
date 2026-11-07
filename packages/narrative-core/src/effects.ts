import type { NarrativeEvent } from './ports.js';
import type { NarrativeState } from './state.js';
import type { Effect, GameContent } from './types.js';

export interface EffectContext {
  content: GameContent;
  state: NarrativeState;
  emit(event: NarrativeEvent): void;
}

const clamp = (v: number, min = -Infinity, max = Infinity) => Math.min(max, Math.max(min, v));

export function applyEffect(effect: Effect, ctx: EffectContext): void {
  const { state, content, emit } = ctx;

  if ('setFlag' in effect) {
    state.flags[effect.setFlag] = effect.value ?? true;
  } else if ('setVar' in effect) {
    state.vars[effect.setVar] = effect.value;
  } else if ('addVar' in effect) {
    state.vars[effect.addVar] = Number(state.vars[effect.addVar] ?? 0) + effect.amount;
  } else if ('giveItem' in effect) {
    emit({ type: 'giveItem', item: effect.giveItem });
  } else if ('takeItem' in effect) {
    emit({ type: 'takeItem', item: effect.takeItem });
  } else if ('remember' in effect) {
    const mem = memoryOf(state, effect.remember.who);
    mem.facts[effect.remember.fact] = (mem.facts[effect.remember.fact] ?? 0) + 1;
  } else if ('forget' in effect) {
    delete memoryOf(state, effect.forget.who).facts[effect.forget.fact];
  } else if ('relation' in effect) {
    const { who, change } = effect.relation;
    const mem = memoryOf(state, who);
    const limits = content.characters[who]?.relation;
    mem.relation = clamp(mem.relation + change, limits?.min, limits?.max);
  } else if ('startQuest' in effect) {
    const q = state.quests[effect.startQuest];
    if (q && q.status === 'inactive') {
      q.status = 'active';
      emit({ type: 'questStarted', quest: effect.startQuest });
    }
  } else if ('completeObjective' in effect) {
    const { quest, objective } = effect.completeObjective;
    const q = state.quests[quest];
    if (q && !q.objectives[objective]) {
      q.objectives[objective] = true;
      emit({ type: 'objectiveCompleted', quest, objective });
    }
  } else if ('completeQuest' in effect) {
    finishQuest(effect.completeQuest, 'completed', ctx);
  } else if ('failQuest' in effect) {
    finishQuest(effect.failQuest, 'failed', ctx);
  } else if ('ending' in effect) {
    state.ending = effect.ending;
    emit({ type: 'ending', ending: effect.ending });
  } else if ('event' in effect) {
    emit({ type: 'custom', name: effect.event, args: effect.args ?? {} });
  } else {
    throw new Error(`Efecte desconegut: ${JSON.stringify(effect)}`);
  }
}

export function applyEffects(effects: Effect[] | undefined, ctx: EffectContext): void {
  for (const e of effects ?? []) applyEffect(e, ctx);
}

export function finishQuest(id: string, status: 'completed' | 'failed', ctx: EffectContext) {
  const q = ctx.state.quests[id];
  if (!q || q.status === 'completed' || q.status === 'failed') return;
  q.status = status;
  const def = ctx.content.quests[id];
  ctx.emit(status === 'completed' ? { type: 'questCompleted', quest: id } : { type: 'questFailed', quest: id });
  applyEffects(status === 'completed' ? def?.onComplete : def?.onFail, ctx);
}

function memoryOf(state: NarrativeState, who: string) {
  return (state.memory[who] ??= { facts: {}, relation: 0 });
}
