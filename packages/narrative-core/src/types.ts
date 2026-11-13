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
  /** La sala d'ara (o una de la llista). Amb `who`, on és aquella protagonista, encara que no jugui. */
  | { inRoom: Id | Id[]; who?: Id }
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
  /**
   * Sala on comença la partida abans de la de la primera protagonista: un pròleg fet de sales
   * `cutscene` que es porten l'una a l'altra amb `goTo`.
   */
  intro?: Id;
  /**
   * Portada: la sala on s'obre el joc, amb el títol i els botons «Comença» i «Carrega» (els posa
   * l'adaptador). «Comença» porta a `intro` (o a la sala de la primera protagonista).
   */
  cover?: Id;
  /**
   * Quan pot el jugador canviar de protagonista quan vulgui (botó «Canvia»). Sense, sempre. Els canvis
   * que fa la història (`{ "event": "protagonista" }`) no en depenen.
   */
  switchWhen?: Condition;
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
  /**
   * Aspecte segons l'estat: la primera entrada que es compleixi diu quina animació (etiqueta
   * del sprite) ha de fer el personatge. Si no se'n compleix cap, la normal.
   * Ex.: el capatàs deixa anar el segell → `{ "if": { "flag": "segell_caigut" }, "anim": "DormSenseSegell" }`.
   */
  appearance?: { if?: Condition; anim: string }[];
  /**
   * Vestuari segons l'estat: la primera entrada que es compleixi diu quina roba porta (el prefix de les
   * etiquetes del sprite: `Bar` → `BarIdleD`, `BarWalkL`...). Si no se'n compleix cap, la normal.
   * A diferència d'`appearance`, no és una animació fixa: el personatge camina i parla igual.
   */
  outfit?: { if?: Condition; name: string }[];
  /**
   * On és dins una sala segons l'estat: la primera entrada d'aquella sala que es compleixi diu on ha de ser
   * (peus, en píxels de la sala). Si l'estat canvia mentre s'hi és, hi camina; en entrar-hi, ja hi és.
   * Ex.: el vigilant deixa la porta per buscar el nen → `{ "if": { "flag": "soler_distret" }, "room": "aeroport_terminal", "x": 430, "y": 190 }`,
   * i una última entrada sense `if` amb el seu lloc de sempre.
   */
  place?: { if?: Condition; room: Id; x: number; y: number }[];
  /**
   * Ronda dins una sala segons l'estat: mentre es compleixi, el personatge va i ve pels punts de `path`, per
   * ordre i tornant a començar, i s'atura `pause` segons a cada punt (per defecte, 1,5). Mentre passa alguna
   * cosa (una línia, una conversa, una cinemàtica), s'atura on és, i després continua.
   * Ex.: en Bastida fa la ronda a popa → `{ "if": { "var": "escena", "op": "==", "value": 6 }, "room": "coberta_popa",
   * "path": [{ "x": 150, "y": 228 }, { "x": 470, "y": 228, "face": "U" }] }`.
   */
  patrol?: PatrolDef[];
}

export interface PatrolDef {
  if?: Condition;
  room: Id;
  /** Els punts (peus, en píxels de la sala). `face`: cap on es gira en arribar-hi. */
  path: (StagePoint & { face?: 'L' | 'R' | 'U' | 'D' })[];
  pause?: number;
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
  /**
   * Només a l'`onEnter`: la protagonista entra caminant des de fora de la pantalla, per aquest costat,
   * fins al seu lloc de la sala, i després diu les línies.
   */
  walkIn?: 'left' | 'right';
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
  /**
   * Sala compartida: hi pot entrar qualsevol d'aquestes protagonistes, i les dues hi poden ser alhora (es
   * veuen l'una a l'altra). Qui hi entra és qui juga; en canviar de protagonista, es va on és l'altra.
   * Substitueix `protagonist`.
   */
  protagonists?: Id[];
  /** En entrar-hi, s'executa la primera que encaixi (el `verb` s'ignora: posa `*`). */
  onEnter?: InteractionDef[];
  /** Coses de la sala: props, zones i personatges, amb l'id que tenen al motor. */
  hotspots: Record<Id, HotspotDef>;
  /**
   * Decorats condicionals: dibuixos que es veuen quan es compleix `visibleIf`, però no es poden
   * clicar (p. ex. un panell obert damunt del panell tancat). Els clics passen a la cosa de sota.
   */
  decor?: Record<Id, DecorDef>;
  /**
   * Sala de cinemàtica (p. ex. el pròleg): no hi ha res per clicar ni cap protagonista, l'adaptador
   * amaga la interfície, i l'`onEnter` es reprodueix sol fins al `goTo`. Si el jugador la salta,
   * es va directament a `skipTo`.
   */
  cutscene?: { skipTo?: Id };
}

export interface DecorDef {
  visibleIf: Condition;
  /**
   * Es dibuixa per sota de les coses clicables, no per sobre (p. ex. l'interior d'una nevera oberta,
   * amb els objectes de dins com a props). Per defecte, per sobre: un decorat canvia l'aspecte d'una cosa.
   */
  sota?: boolean;
}

// ─── Diàlegs ─────────────────────────────────────────────────────────────────

/**
 * `player` = el protagonista, `narrator` = text de narració, `title` = pantalla de títol (p. ex. el
 * canvi d'acte): la pantalla es fon a negre, s'hi mostra el text i torna la imatge.
 */
export type SpeakerId = Id | 'player' | 'narrator' | 'title';

export interface DialogueLineDef {
  who: SpeakerId;
  text: TextKey;
  if?: Condition;
  effects?: Effect[];
  /**
   * So que fa en dir la línia: un fitxer de `game/audio/sfx/` sense extensió. Pot dur variables
   * entre claus, que es posen en acabar la interacció: `"molla_{molla_tensio}"` → `molla_3`.
   */
  sound?: SoundId;
  /**
   * Moviment abans de dir la línia (qui camina, s'asseu, apareix o marxa), per ordre. Només és visual:
   * l'estat no en sap res, i en acabar les línies el motor torna a posar cada personatge com diu l'estat.
   * A l'`onEnter`, el de la primera línia (menys el que camina) ja es fa abans que es vegi la sala.
   */
  stage?: StageCue[];
  /** Moviment en acabar de dir la línia (p. ex. qui diu «me'n vaig» i després marxa), com `stage`. */
  stageAfter?: StageCue[];
}

/**
 * Una indicació d'escena: `who` (un personatge, o `player` per a la protagonista que juga) i què fa,
 * en aquest ordre: es posa a `at`, es mostra o s'amaga (`visible`), canvia d'animació (`anim`), es gira
 * (`face`) i camina fins a `walk`. Els llocs són una cosa o un personatge de la sala (hi va al seu punt
 * d'arribada) o un punt.
 *
 * En lloc de `who`, `prop`: una capa del decorat de la sala que no és al JSON del joc (l'art del motor, p. ex. la
 * zòdiac del pròleg de Ni un ou), que només es mostra o s'amaga (`visible`) i canvia d'animació (`anim`).
 *
 * `shake` sacseja la pantalla (p. ex. la paret que vibra al pròleg de Ferro-9); pot anar sol, sense `who` ni `prop`.
 */
export interface StageCue {
  who?: Id | 'player';
  /** Una capa del decorat (un prop del motor), en lloc d'un personatge. */
  prop?: Id;
  /**
   * Després de la indicació, s'espera aquests segons sense text (p. ex. mentre dura l'animació d'un prop).
   * En saltar la cinemàtica, no s'espera.
   */
  hold?: number;
  /** Sacseja la pantalla aquests segons (no s'espera). */
  shake?: number;
  /** S'hi posa de cop. */
  at?: Id | StagePoint;
  /** Hi camina. */
  walk?: Id | StagePoint;
  /** Amb `walk`: `false` = no s'espera que hi arribi (camina mentre es diu la línia). Per defecte, s'espera. */
  wait?: boolean;
  face?: 'L' | 'R' | 'U' | 'D';
  /** Animació del sprite (p. ex. `Seu`); `null` la treu (torna a estar dret). */
  anim?: string | null;
  visible?: boolean;
}

export interface StagePoint {
  x: number;
  y: number;
}

/** Nom d'un so de `game/audio/sfx/` (sense extensió), amb `{variable}` opcionals. */
export type SoundId = string;

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
  /**
   * Només surt a la llista quan es compleix (o quan ja és fet). Sense, surt sempre. Per no anunciar coses que
   * les protagonistes encara no saben (p. ex. «Trobar la Juana» abans que la Juana falti).
   */
  showWhen?: Condition;
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

/** Una línia de l'escena d'un final. */
export interface EndingLineDef extends DialogueLineDef {
  /**
   * Sala de fons (una `cutscene` sense `onEnter`) des d'aquesta línia: com al pròleg, el text surt
   * damunt la imatge. Sense cap `room`, el final es llegeix sobre negre.
   */
  room?: Id;
}

export interface EndingDef {
  title: TextKey;
  text: TextKey;
  /**
   * Escena entre el títol i el text final: línies (de narrador, títols o personatges) amb `if`
   * opcional, per explicar què passa després segons el que s'ha fet. No hi ha efectes.
   */
  scene?: EndingLineDef[];
  /** Sala de fons per a `text` (si no, la de l'última línia de l'escena que en tingui). */
  textRoom?: Id;
  /**
   * Crèdits: línies que van després de `text`, amb `room` com a l'escena (si no, continuen sobre la
   * sala del text). Acaben amb el «Fi».
   */
  credits?: EndingLineDef[];
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
