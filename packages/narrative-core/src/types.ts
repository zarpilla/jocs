/**
 * Tipus del contingut del joc (el que hi ha als JSON de `game/data/`).
 *
 * Aquest fitxer NO coneix cap motor gràfic. Tot el que és text visible és una
 * clau de traducció (`TextKey`), mai el text mateix.
 */

/** Clau d'un text a `game/locales/<idioma>/*.json`, p. ex. `"dlg.pescador.hola"`. */
export type TextKey = string;

export type Id = string;

export type Scalar = number | string | boolean;

export type CompareOp = '==' | '!=' | '>' | '>=' | '<' | '<=';

// ─── Condicions ──────────────────────────────────────────────────────────────
// Es poden posar a qualsevol "if" del contingut. Forma compacta: una clau
// principal diu de quin tipus és.

export type Condition =
  | { flag: Id; is?: boolean }
  | { var: Id; op: CompareOp; value: Scalar }
  /** Sense `who`, mira l'inventari de la protagonista activa. */
  | { hasItem: Id; who?: Id; is?: boolean }
  /** Quina protagonista controla ara el jugador. */
  | { protagonist: Id }
  | { remembers: { who: Id; fact: Id; atLeast?: number }; is?: boolean }
  | { relation: { who: Id; op: CompareOp; value: number } }
  | { quest: Id; status: QuestStatus | QuestStatus[] }
  | { objective: { quest: Id; objective: Id }; is?: boolean }
  | { visited: Id; is?: boolean }
  | { inRoom: Id }
  | { seen: { dialogue: Id; node: Id }; is?: boolean }
  | { chosen: { dialogue: Id; node: Id; choice: Id }; is?: boolean }
  | { all: Condition[] }
  | { any: Condition[] }
  | { not: Condition };

// ─── Efectes ─────────────────────────────────────────────────────────────────
// Canvis d'estat. Els que toquen el món (objectes a l'inventari, esdeveniments
// propis) es tradueixen a `NarrativeEvent` perquè els executi l'adaptador.

export type Effect =
  | { setFlag: Id; value?: boolean }
  | { setVar: Id; value: Scalar }
  | { addVar: Id; amount: number }
  /** Sense `who`, a/de la protagonista activa. */
  | { giveItem: Id; who?: Id }
  | { takeItem: Id; who?: Id }
  | { remember: { who: Id; fact: Id } }
  | { forget: { who: Id; fact: Id } }
  | { relation: { who: Id; change: number } }
  | { startQuest: Id }
  | { completeObjective: { quest: Id; objective: Id } }
  | { completeQuest: Id }
  | { failQuest: Id }
  | { ending: Id }
  /** Esdeveniment lliure per al motor gràfic (animació, so, canvi de sala...). */
  | { event: string; args?: Record<string, Scalar> };

// ─── Joc ─────────────────────────────────────────────────────────────────────

export interface GameManifest {
  id: Id;
  title: TextKey;
  defaultLocale: string;
  locales: string[];
  /** Personatges que pot controlar el jugador. La primera és la inicial. */
  protagonists: Id[];
  /** On comença cada protagonista i què porta a l'inventari. */
  start?: Record<Id, { room: Id; items?: Id[] }>;
}

/** Declaració de flags i variables amb el seu valor inicial (`state.json`). */
export interface StateDeclaration {
  flags: Record<Id, boolean>;
  vars: Record<Id, Scalar>;
}

// ─── Personatges i memòria ───────────────────────────────────────────────────

export interface CharacterDef {
  name: TextKey;
  /** Fets que aquest personatge pot recordar. Serveix per validar el contingut. */
  facts?: Id[];
  relation?: { initial?: number; min?: number; max?: number };
  /** Descripció per a "mirar" (opcional). */
  description?: TextKey;
  /** Interaccions amb aquest personatge a qualsevol sala (una sala les pot substituir). */
  interactions?: InteractionDef[];
}

// ─── Objectes ────────────────────────────────────────────────────────────────

export interface ItemDef {
  name: TextKey;
  description?: TextKey;
  /** Propietats lliures que fa servir la lògica del joc (pes, material...). */
  props?: Record<Id, Scalar>;
  /** Interaccions amb l'objecte a l'inventari (mirar-lo, combinar-lo amb un altre...). */
  interactions?: InteractionDef[];
}

// ─── Sales i interaccions ────────────────────────────────────────────────────

/**
 * Què passa quan el jugador fa un verb sobre alguna cosa. S'agafa la primera
 * interacció de la llista que encaixi (verb, objecte, condició, `once`).
 */
export interface InteractionDef {
  /** Necessari si `once`: identifica la interacció a les partides desades. */
  id?: Id;
  /** Verb o verbs del motor (`look`, `use`, `pickUp`...), o `*` per a qualsevol. */
  verb: Id | Id[];
  /** Amb un objecte de l'inventari ("fer servir X amb..."). `*` = qualsevol objecte. */
  item?: Id;
  if?: Condition;
  /** Només passa una vegada. */
  once?: boolean;
  lines?: DialogueLineDef[];
  effects?: Effect[];
  /** Acció de la lògica del joc (codi), p. ex. la finestra de fase. `"$item"` als args = l'objecte fet servir. */
  action?: { name: string; args?: Record<string, Scalar> };
  /** Comença aquest diàleg després de les línies. */
  dialogue?: Id;
  /** Va a aquesta sala al final. */
  goTo?: Id;
}

export interface HotspotDef {
  name?: TextKey;
  /** Si no es compleix, no es veu ni es pot tocar. */
  visibleIf?: Condition;
  interactions?: InteractionDef[];
}

export interface RoomDef {
  name: TextKey;
  /** De quina protagonista és la sala (informatiu, i per validar). */
  protagonist?: Id;
  /** En entrar-hi, s'executa la primera que encaixi (el `verb` s'ignora: posa `*`). */
  onEnter?: InteractionDef[];
  /** Coses de la sala: props, zones i personatges, amb l'id que tenen al motor. */
  hotspots: Record<Id, HotspotDef>;
}

// ─── Diàlegs ─────────────────────────────────────────────────────────────────

/** `player` = el protagonista, `narrator` = text de narració. */
export type SpeakerId = Id | 'player' | 'narrator';

export interface DialogueLineDef {
  who: SpeakerId;
  text: TextKey;
  if?: Condition;
  effects?: Effect[];
}

export interface DialogueChoiceDef {
  id: Id;
  /** El que es veu a la llista d'opcions (i el que diu el jugador). */
  text: TextKey;
  if?: Condition;
  /** Desapareix un cop triada. */
  once?: boolean;
  /** El jugador no repeteix el text en veu alta (p. ex. "(Marxar)"). */
  silent?: boolean;
  effects?: Effect[];
  /** Node següent. Sense `next`, es torna al mateix node. */
  next?: Id;
  /** Acaba la conversa després de les línies del node `next` (si n'hi ha). */
  end?: boolean;
}

export interface DialogueNodeDef {
  lines?: DialogueLineDef[];
  /** Efectes en entrar al node. */
  effects?: Effect[];
  choices?: DialogueChoiceDef[];
  /** Sense opcions disponibles: salta a aquest node o acaba la conversa. */
  goto?: Id;
}

export interface DialogueEntryDef {
  if?: Condition;
  node: Id;
}

export interface DialogueDef {
  id: Id;
  /** Personatge principal (amb qui parles). */
  with: Id;
  /**
   * Node inicial. Si és una llista, s'agafa el primer que compleixi la condició:
   * així un personatge et saluda diferent segons el que recorda.
   */
  start: Id | DialogueEntryDef[];
  nodes: Record<Id, DialogueNodeDef>;
}

// ─── Missions ────────────────────────────────────────────────────────────────

export type QuestStatus = 'inactive' | 'active' | 'completed' | 'failed';

export interface QuestObjectiveDef {
  id: Id;
  text: TextKey;
  /** Es marca sol quan es compleix (es revisa després de cada canvi d'estat). */
  completeWhen?: Condition;
  optional?: boolean;
}

export interface QuestDef {
  title: TextKey;
  description?: TextKey;
  kind: 'main' | 'side';
  /** S'activa sola quan es compleix. */
  startWhen?: Condition;
  objectives: QuestObjectiveDef[];
  /** Per defecte, es completa quan tots els objectius no opcionals ho estan. */
  completeWhen?: Condition;
  failWhen?: Condition;
  onComplete?: Effect[];
  onFail?: Effect[];
}

// ─── Pistes ──────────────────────────────────────────────────────────────────

export interface HintDef {
  /** Quan és rellevant aquesta pista (el trencaclosques està "obert"). */
  when: Condition;
  /** Quan ja no cal (el trencaclosques està resolt). */
  doneWhen: Condition;
  /** Més prioritat = es mostra abans. */
  priority?: number;
  /** De més vaga a més explícita. */
  levels: TextKey[];
}

// ─── Finals ──────────────────────────────────────────────────────────────────

export interface EndingDef {
  title: TextKey;
  text: TextKey;
  /** Per triar-ne un automàticament amb `resolveEnding()`. */
  when?: Condition;
  priority?: number;
}

// ─── Paquet complet ──────────────────────────────────────────────────────────

export interface GameContent {
  manifest: GameManifest;
  state: StateDeclaration;
  characters: Record<Id, CharacterDef>;
  items: Record<Id, ItemDef>;
  rooms: Record<Id, RoomDef>;
  dialogues: Record<Id, DialogueDef>;
  quests: Record<Id, QuestDef>;
  hints: Record<Id, HintDef>;
  endings: Record<Id, EndingDef>;
}

/** Textos d'un idioma: clau → text. */
export type LocaleTable = Record<TextKey, string>;
