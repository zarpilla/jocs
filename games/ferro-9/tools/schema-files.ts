/** Forma de cada fitxer JSON del joc, per generar-ne els JSON Schema. */
export type {
  CharacterDef, EndingDef, HintDef, ItemDef, QuestDef,
} from '../packages/narrative-core/src/types.js';
import type { DialogueDef, GameManifest, RoomDef, StateDeclaration } from '../packages/narrative-core/src/types.js';

type WithSchema = { $schema?: string };

export type GameFile = WithSchema & GameManifest;
export type StateFile = WithSchema & StateDeclaration;
export type DialogueFile = WithSchema & DialogueDef;
export type RoomFile = WithSchema & RoomDef;
