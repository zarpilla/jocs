import type { GameContent, Id, QuestStatus, Scalar } from './types.js';

/**
 * Tot l'estat narratiu, en un objecte JSON pla. L'adaptador el desa dins les
 * partides guardades del motor (a Benne, dins una variable).
 */
export interface NarrativeState {
  version: 1;
  flags: Record<Id, boolean>;
  vars: Record<Id, Scalar>;
  /** Memòria de cada personatge: quantes vegades ha passat cada fet + relació. */
  memory: Record<Id, CharacterMemory>;
  quests: Record<Id, QuestState>;
  dialogue: {
    /** `"<diàleg>/<node>"` → vegades vist. */
    seen: Record<string, number>;
    /** `"<diàleg>/<node>/<opció>"` → vegades triada. */
    chosen: Record<string, number>;
  };
  /** Pista → quants nivells s'han mostrat. */
  hints: Record<Id, number>;
  ending: Id | null;
}

export interface CharacterMemory {
  facts: Record<Id, number>;
  relation: number;
}

export interface QuestState {
  status: QuestStatus;
  objectives: Record<Id, boolean>;
}

export const STATE_VERSION = 1;

export function createInitialState(content: GameContent): NarrativeState {
  const memory: Record<Id, CharacterMemory> = {};
  for (const [id, def] of Object.entries(content.characters)) {
    memory[id] = { facts: {}, relation: def.relation?.initial ?? 0 };
  }
  const quests: Record<Id, QuestState> = {};
  for (const id of Object.keys(content.quests)) {
    quests[id] = { status: 'inactive', objectives: {} };
  }
  return {
    version: STATE_VERSION,
    flags: { ...content.state.flags },
    vars: { ...content.state.vars },
    memory,
    quests,
    dialogue: { seen: {}, chosen: {} },
    hints: {},
    ending: null,
  };
}

/**
 * Carrega un estat desat i el completa amb el que hagi afegit el contingut
 * després (flags, personatges o missions noves no trenquen partides antigues).
 */
export function migrateState(content: GameContent, saved: unknown): NarrativeState {
  const fresh = createInitialState(content);
  if (!saved || typeof saved !== 'object') return fresh;
  const s = saved as Partial<NarrativeState>;
  return {
    version: STATE_VERSION,
    flags: { ...fresh.flags, ...s.flags },
    vars: { ...fresh.vars, ...s.vars },
    memory: { ...fresh.memory, ...s.memory },
    quests: { ...fresh.quests, ...s.quests },
    dialogue: {
      seen: { ...s.dialogue?.seen },
      chosen: { ...s.dialogue?.chosen },
    },
    hints: { ...s.hints },
    ending: s.ending ?? null,
  };
}

export const seenKey = (dialogue: Id, node: Id) => `${dialogue}/${node}`;
export const chosenKey = (dialogue: Id, node: Id, choice: Id) => `${dialogue}/${node}/${choice}`;
