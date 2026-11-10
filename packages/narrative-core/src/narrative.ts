import { evaluate, type ConditionContext } from './conditions.js';
import { DialogueSessions, type DialogueStep, type ResolvedChoice, type ResolvedLine } from './dialogue.js';
import { applyEffects, finishQuest, type EffectContext } from './effects.js';
import { Localizer, type TextParams } from './i18n.js';
import type { NarrativeEvent, NarrativeListener, WorldPort } from './ports.js';
import { chosenKey, createInitialState, migrateState, seenKey, type NarrativeState } from './state.js';
import type {
  Condition,
  DialogueChoiceDef,
  DialogueDef,
  Effect,
  GameContent,
  Id,
  InteractionDef,
  LocaleTable,
  QuestDef,
  Scalar,
  SpeakerId,
  TextKey,
} from './types.js';

/** Què ha de fer el motor després d'una interacció. */
export interface InteractionResult {
  lines: ResolvedLine[];
  /** Diàleg a començar després de les línies. */
  dialogue?: Id;
  /** Sala on anar al final. */
  goTo?: Id;
  /** Entrada caminant des d'un costat (només a l'`onEnter`). */
  walkIn?: 'left' | 'right';
}

/** Una cosa sobre la qual es pot fer un verb. */
export interface InteractionTarget {
  /** `item` = objecte de l'inventari; la resta, coses de la sala. */
  kind: 'hotspot' | 'character' | 'item';
  id: Id;
}

export interface InteractionRequest {
  verb: Id;
  target: InteractionTarget;
  /** Objecte de l'inventari fet servir ("fer servir X amb..."). */
  item?: Id;
  /** Per defecte, la sala actual del món. */
  room?: Id;
}

export interface ActionContext {
  narrative: Narrative;
  args: Record<string, Scalar>;
  request?: InteractionRequest;
}

/** El que torna una acció de joc: línies per dir (claus de text). */
export interface ActionResult {
  lines?: { who: SpeakerId; text: TextKey; params?: TextParams; sound?: string }[];
}

export type GameAction = (ctx: ActionContext) => ActionResult | void;

/**
 * Què acaba de fer el jugador, per a les regles que han de reaccionar a **cada** acció (p. ex. una
 * sincronia per torns, on cada acció gasta un torn): una interacció que ha encaixat, o una opció de diàleg.
 */
export type PlayerAction =
  | { kind: 'interaction'; room: Id | null; verb: Id; target: InteractionTarget; item?: Id }
  | { kind: 'choice'; room: Id | null; dialogue: Id; choice: Id };

/** El que torna una regla d'«acció feta»: línies per afegir i, en un diàleg, si cal tancar-lo. */
export interface AfterActionResult extends ActionResult {
  endDialogue?: boolean;
}

export type AfterActionHook = (action: PlayerAction, narrative: Narrative) => AfterActionResult | void;

export interface NarrativeOptions {
  content: GameContent;
  locales: Record<string, LocaleTable>;
  world: WorldPort;
  locale?: string;
}

export interface QuestView {
  id: Id;
  kind: QuestDef['kind'];
  status: NarrativeState['quests'][string]['status'];
  title: string;
  description?: string;
  objectives: { id: Id; text: string; done: boolean; optional: boolean }[];
}

export interface HintView {
  id: Id;
  /** Text del nivell actual. */
  text: string;
  level: number;
  levels: number;
  /** Encara hi ha una pista més explícita. */
  hasMore: boolean;
}

export interface EndingView {
  id: Id;
  title: string;
  /** L'escena, ja filtrada per les condicions de cada línia. `room`: sala de fons des d'aquesta línia. */
  scene: (ResolvedLine & { room?: Id })[];
  text: string;
  /** Sala de fons per al text final, si en canvia. */
  textRoom?: Id;
}

/**
 * Façana del motor narratiu. És l'únic objecte que fa servir l'adaptador del
 * motor gràfic. Tot el que fa és pur i síncron: llegeix i escriu `state` i
 * emet `NarrativeEvent`s.
 */
export class Narrative {
  readonly content: GameContent;
  readonly i18n: Localizer;
  readonly world: WorldPort;
  private _state: NarrativeState;
  private listeners = new Set<NarrativeListener>();
  private sessions = new DialogueSessions();
  private actions = new Map<string, GameAction>();
  private afterHooks: AfterActionHook[] = [];
  /** Dins un lot d'efectes: es retarda `stateChanged` fins al final. */
  private batchDepth = 0;

  constructor(opts: NarrativeOptions) {
    this.content = opts.content;
    this.world = opts.world;
    this.i18n = new Localizer(opts.content.manifest.defaultLocale, opts.locales);
    if (opts.locale) this.i18n.setLocale(opts.locale);
    this._state = createInitialState(opts.content);
  }

  // ─── Estat ────────────────────────────────────────────────────────────────

  get state(): Readonly<NarrativeState> {
    return this._state;
  }

  /** Còpia per desar. */
  snapshot(): NarrativeState {
    return structuredClone(this._state);
  }

  /** Restaura una partida desada (o comença de zero si `saved` és buit). */
  load(saved: unknown) {
    this._state = migrateState(this.content, structuredClone(saved ?? null));
    this.sessions.clear();
    this.notify();
  }

  reset() {
    this.load(null);
  }

  /**
   * Partida nova: estat inicial i inventaris inicials (`game.json` → `start`).
   * Retorna on ha de començar cada protagonista.
   */
  newGame(): Record<Id, Id> {
    this.load(null);
    const rooms: Record<Id, Id> = {};
    this.batch(() => {
      for (const [who, start] of Object.entries(this.content.manifest.start ?? {})) {
        rooms[who] = start.room;
        for (const item of start.items ?? []) this.emit({ type: 'giveItem', item, who });
      }
    });
    return rooms;
  }

  on(listener: NarrativeListener): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  // ─── Lectures ràpides per als scripts ─────────────────────────────────────

  /** Si el jugador pot canviar de protagonista quan vulgui (`switchWhen` a game.json). */
  canSwitch(): boolean {
    return this.check(this.content.manifest.switchWhen);
  }

  check(cond: Condition | undefined): boolean {
    return evaluate(cond, this.condCtx());
  }

  flag(id: Id): boolean {
    return this._state.flags[id] === true;
  }

  getVar(id: Id): Scalar | undefined {
    return this._state.vars[id];
  }

  remembers(who: Id, fact: Id): number {
    return this._state.memory[who]?.facts[fact] ?? 0;
  }

  relation(who: Id): number {
    return this._state.memory[who]?.relation ?? 0;
  }

  // ─── Canvis ───────────────────────────────────────────────────────────────

  /** Aplica efectes (des d'un script de sala, p. ex.) i revisa missions. */
  apply(effects: Effect | Effect[]) {
    this.batch(() => applyEffects(Array.isArray(effects) ? effects : [effects], this.effectCtx()));
  }

  /** Avís de l'adaptador: alguna cosa ha canviat al món (inventari, sala). */
  worldChanged() {
    this.batch(() => {});
  }

  // ─── Textos ───────────────────────────────────────────────────────────────

  /** Tradueix una clau. Les variables de l'estat estan disponibles com a `{nom}`. */
  t(key: TextKey, params?: TextParams): string {
    return this.i18n.t(key, { ...(this._state.vars as TextParams), ...params });
  }

  setLocale(locale: string) {
    this.i18n.setLocale(locale);
    this.notify();
  }

  characterName(id: Id): string {
    const def = this.content.characters[id];
    return def ? this.t(def.name) : id;
  }

  /** L'animació que ha de fer un personatge segons l'estat (`appearance`), o `null` per a la normal. */
  appearanceOf(id: Id): string | null {
    return this.content.characters[id]?.appearance?.find((a) => this.check(a.if))?.anim ?? null;
  }

  /** La roba que porta un personatge segons l'estat (`outfit`), o `''` per a la normal. */
  outfitOf(id: Id): string {
    return this.content.characters[id]?.outfit?.find((o) => this.check(o.if))?.name ?? '';
  }

  itemName(id: Id): string {
    const def = this.content.items[id];
    return def ? this.t(def.name) : id;
  }

  // ─── Diàlegs ──────────────────────────────────────────────────────────────

  startDialogue(id: Id): DialogueStep {
    const def = this.dialogueDef(id);
    const start = typeof def.start === 'string'
      ? def.start
      : def.start.find((e) => this.check(e.if))?.node;
    if (!start) throw new Error(`El diàleg "${id}" no té cap node inicial vàlid ara mateix.`);
    return this.batch(() => this.enterNode(def, start, []));
  }

  choose(dialogueId: Id, choiceId: Id, opts: { node?: Id } = {}): DialogueStep {
    const def = this.dialogueDef(dialogueId);
    const node = opts.node ?? this.sessions.get(dialogueId);
    if (!node) throw new Error(`El diàleg "${dialogueId}" no està en curs.`);
    const choice = def.nodes[node]?.choices?.find((c) => c.id === choiceId);
    if (!choice) throw new Error(`Opció "${choiceId}" no existeix al node "${dialogueId}/${node}".`);

    return this.batch(() => {
      const key = chosenKey(dialogueId, node, choiceId);
      this._state.dialogue.chosen[key] = (this._state.dialogue.chosen[key] ?? 0) + 1;
      const lines: ResolvedLine[] = choice.silent
        ? []
        : [{ who: 'player', key: choice.text, text: this.t(choice.text) }];
      applyEffects(choice.effects, this.effectCtx());

      let step: DialogueStep;
      if (choice.next) {
        step = this.enterNode(def, choice.next, lines);
        if (choice.end) step = this.endStep(def.id, step.node, step.lines);
      } else if (choice.end) {
        step = this.endStep(def.id, node, lines);
      } else {
        step = this.stepAt(def, node, lines);
      }
      const after = this.runAfterHooks({ kind: 'choice', room: this.world.currentRoom(), dialogue: dialogueId, choice: choiceId });
      if (after.lines.length || after.end) {
        step = { ...step, lines: [...step.lines, ...after.lines] };
        if (after.end && !step.ended) step = this.endStep(def.id, step.node, step.lines);
        else if (!step.ended) step = { ...step, choices: this.availableChoices(def, step.node) };
      }
      return step;
    });
  }

  /** Les opcions disponibles ara al node actual (per refrescar la llista). */
  currentChoices(dialogueId: Id): ResolvedChoice[] {
    const node = this.sessions.get(dialogueId);
    return node ? this.availableChoices(this.dialogueDef(dialogueId), node) : [];
  }

  endDialogue(dialogueId: Id) {
    this.sessions.end(dialogueId);
  }

  // ─── Missions ─────────────────────────────────────────────────────────────

  quests(filter?: { kind?: QuestDef['kind']; status?: QuestView['status'][] }): QuestView[] {
    return Object.entries(this.content.quests)
      .filter(([, def]) => !filter?.kind || def.kind === filter.kind)
      .map(([id, def]) => {
        const qs = this._state.quests[id]!;
        return {
          id,
          kind: def.kind,
          status: qs.status,
          title: this.t(def.title),
          description: def.description ? this.t(def.description) : undefined,
          objectives: def.objectives.map((o) => ({
            id: o.id,
            text: this.t(o.text),
            done: qs.objectives[o.id] === true,
            optional: o.optional === true,
          })),
        };
      })
      .filter((q) => !filter?.status || filter.status.includes(q.status));
  }

  // ─── Pistes ───────────────────────────────────────────────────────────────

  /** Les pistes que ara mateix són útils, de més a menys prioritàries. */
  activeHints(): Id[] {
    return Object.entries(this.content.hints)
      .filter(([, h]) => this.check(h.when) && !this.check(h.doneWhen))
      .sort(([, a], [, b]) => (b.priority ?? 0) - (a.priority ?? 0))
      .map(([id]) => id);
  }

  /**
   * Demana una pista: la primera vegada dona el nivell 1 (vague); cada nova
   * petició sobre la mateixa pista és més explícita. `null` si no n'hi ha cap.
   */
  requestHint(): HintView | null {
    const id = this.activeHints()[0];
    if (!id) return null;
    const def = this.content.hints[id]!;
    return this.batch(() => {
      const level = Math.min((this._state.hints[id] ?? 0) + 1, def.levels.length);
      this._state.hints[id] = level;
      return { id, level, levels: def.levels.length, text: this.t(def.levels[level - 1]!), hasMore: level < def.levels.length };
    });
  }

  // ─── Finals ───────────────────────────────────────────────────────────────

  /** El final que toca segons l'estat (el de més prioritat que es compleixi). */
  resolveEnding(): Id | null {
    if (this._state.ending) return this._state.ending;
    const found = Object.entries(this.content.endings)
      .filter(([, e]) => e.when && this.check(e.when))
      .sort(([, a], [, b]) => (b.priority ?? 0) - (a.priority ?? 0))[0];
    return found?.[0] ?? null;
  }

  ending(id: Id): EndingView {
    const def = this.content.endings[id];
    if (!def) throw new Error(`Final desconegut: ${id}`);
    const scene = (def.scene ?? [])
      .filter((line) => this.check(line.if))
      .map((line) => ({ who: line.who, key: line.text, text: this.t(line.text), ...(line.room ? { room: line.room } : {}) }));
    return { id, title: this.t(def.title), scene, text: this.t(def.text), ...(def.textRoom ? { textRoom: def.textRoom } : {}) };
  }

  // ─── Sales, coses i interaccions ──────────────────────────────────────────

  /** Registra una acció de joc (codi del joc, no del motor). */
  registerAction(name: string, action: GameAction) {
    if (this.actions.has(name)) throw new Error(`Acció repetida: ${name}`);
    this.actions.set(name, action);
  }

  /**
   * Regla que s'executa després de cada acció del jugador que ha fet alguna cosa (una interacció que ha
   * encaixat o una opció de diàleg). Les frases per defecte («No es mou») no compten com a acció.
   */
  onAfterAction(hook: AfterActionHook): () => void {
    this.afterHooks.push(hook);
    return () => {
      this.afterHooks = this.afterHooks.filter((h) => h !== hook);
    };
  }

  private runAfterHooks(action: PlayerAction): { lines: ResolvedLine[]; end: boolean } {
    const lines: ResolvedLine[] = [];
    let end = false;
    for (const hook of this.afterHooks) {
      const r = hook(action, this) ?? {};
      for (const l of r.lines ?? []) lines.push({ who: l.who, key: l.text, text: this.t(l.text, l.params), ...(l.sound && { sound: l.sound }) });
      end ||= !!r.endDialogue;
    }
    return { lines, end };
  }

  get actionNames(): string[] {
    return [...this.actions.keys()];
  }

  /** Executa una acció de joc fora d'una interacció (p. ex. des d'un script). */
  runAction(name: string, args: Record<string, Scalar> = {}): ResolvedLine[] {
    return this.batch(() => this.callAction(name, args));
  }

  isHotspotVisible(room: Id, hotspot: Id): boolean {
    const def = this.content.rooms[room]?.hotspots[hotspot];
    return def ? this.check(def.visibleIf) : true;
  }

  /** Visibilitat de les coses condicionals d'una sala (les que tenen `visibleIf`) i dels decorats. */
  hotspotsIn(room: Id): { id: Id; visible: boolean }[] {
    const def = this.content.rooms[room];
    return [
      ...Object.entries(def?.hotspots ?? {})
        .filter(([, h]) => h.visibleIf)
        .map(([id]) => ({ id, visible: this.isHotspotVisible(room, id) })),
      ...Object.entries(def?.decor ?? {}).map(([id, d]) => ({ id, visible: this.check(d.visibleIf) })),
    ];
  }

  /**
   * El jugador fa un verb sobre alguna cosa. Busca la interacció a la sala,
   * després al personatge o a l'objecte. `null` = cap interacció: el motor
   * diu la frase per defecte (`defaultLine`).
   */
  interact(req: InteractionRequest): InteractionResult | null {
    const room = req.room ?? this.world.currentRoom() ?? '';
    const lists: [string, InteractionDef[] | undefined][] = [];
    if (req.target.kind !== 'item') {
      lists.push([`${room}/${req.target.id}`, this.content.rooms[room]?.hotspots[req.target.id]?.interactions]);
    }
    if (req.target.kind === 'character') {
      lists.push([`character/${req.target.id}`, this.content.characters[req.target.id]?.interactions]);
    }
    if (req.target.kind === 'item') {
      lists.push([`item/${req.target.id}`, this.content.items[req.target.id]?.interactions]);
      // Combinar A amb B ha de funcionar en tots dos sentits.
      if (req.item) {
        lists.push([`item/${req.item}`, this.content.items[req.item]?.interactions]);
      }
    }
    for (const [scope, list = []] of lists) {
      // En combinar A amb B des de B, l'objecte "fet servir" passa a ser A.
      const item = scope === `item/${req.item}` ? req.target.id : req.item;
      const found = this.findInteraction(scope, list, req.verb, item);
      if (found) {
        return this.batch(() => {
          const result = this.runInteraction(scope, list, found, { ...req, item });
          const after = this.runAfterHooks({ kind: 'interaction', room, verb: req.verb, target: req.target, item: req.item });
          return after.lines.length ? { ...result, lines: [...result.lines, ...after.lines] } : result;
        });
      }
    }
    // Mirar un objecte de l'inventari sense cap "look" propi: la seva descripció.
    const description = req.target.kind === 'item' && req.verb === 'look' && !req.item
      ? this.content.items[req.target.id]?.description
      : undefined;
    if (description) return { lines: [{ who: 'player', key: description, text: this.t(description) }] };
    return null;
  }

  /** En entrar a una sala: la primera entrada d'`onEnter` que encaixi. */
  enterRoom(room: Id): InteractionResult | null {
    const list = this.content.rooms[room]?.onEnter ?? [];
    const found = this.findInteraction(`${room}/@enter`, list, '*');
    return found ? this.batch(() => this.runInteraction(`${room}/@enter`, list, found)) : null;
  }

  /**
   * Frase quan una interacció no està prevista. Busca, per ordre:
   * `ui.defecte.<verb>.<protagonista>`, `ui.defecte.<verb>`, `ui.defecte`.
   */
  defaultLine(verb: Id): ResolvedLine {
    const who = this.world.activeProtagonist();
    const key = [`ui.defecte.${verb}.${who}`, `ui.defecte.${verb}`, 'ui.defecte'].find((k) => this.i18n.has(k) || this.i18n.has(k, this.i18n.defaultLocale)) ?? 'ui.defecte';
    return { who: 'player', key, text: this.t(key) };
  }

  // ─── Intern ───────────────────────────────────────────────────────────────

  private interactionKey(scope: string, list: InteractionDef[], i: InteractionDef) {
    return `${scope}/${i.id ?? list.indexOf(i)}`;
  }

  private findInteraction(scope: string, list: InteractionDef[], verb: Id, item?: Id): InteractionDef | undefined {
    return list.find((i) => {
      const verbs = Array.isArray(i.verb) ? i.verb : [i.verb];
      if (!verbs.includes('*') && !verbs.includes(verb)) return false;
      // Amb objecte només encaixen les que en demanen; sense objecte, les que no.
      if (item ? i.item !== '*' && i.item !== item : i.item !== undefined) return false;
      if (i.once && (this._state.interactions[this.interactionKey(scope, list, i)] ?? 0) > 0) return false;
      return this.check(i.if);
    });
  }

  private runInteraction(scope: string, list: InteractionDef[], i: InteractionDef, req?: InteractionRequest): InteractionResult {
    if (i.once) {
      const key = this.interactionKey(scope, list, i);
      this._state.interactions[key] = (this._state.interactions[key] ?? 0) + 1;
    }
    const lines: ResolvedLine[] = [];
    for (const line of i.lines ?? []) {
      if (!this.check(line.if)) continue;
      applyEffects(line.effects, this.effectCtx());
      lines.push({ who: line.who, key: line.text, text: this.t(line.text), ...(line.sound && { sound: line.sound }) });
    }
    applyEffects(i.effects, this.effectCtx());
    // Les variables del so es posen al final: «estira la molla» ha de sonar amb la tensió nova.
    for (const line of lines) if (line.sound) line.sound = this.soundName(line.sound);
    if (i.action) {
      const args = Object.fromEntries(
        Object.entries(i.action.args ?? {}).map(([k, v]) => [k, v === '$item' ? (req?.item ?? '') : v]),
      );
      lines.push(...this.callAction(i.action.name, args, req));
    }
    return { lines, dialogue: i.dialogue, goTo: i.goTo, ...(i.walkIn ? { walkIn: i.walkIn } : {}) };
  }

  private callAction(name: string, args: Record<string, Scalar>, request?: InteractionRequest): ResolvedLine[] {
    const action = this.actions.get(name);
    if (!action) throw new Error(`Acció de joc no registrada: ${name}`);
    const result = action({ narrative: this, args, request }) ?? {};
    return (result.lines ?? []).map((l) => ({ who: l.who, key: l.text, text: this.t(l.text, l.params), ...(l.sound && { sound: l.sound }) }));
  }

  /** `"molla_{molla_tensio}"` → `"molla_3"`, amb les variables d'ara. */
  private soundName(sound: string): string {
    return sound.replace(/\{(\w+)\}/g, (_, v: string) => String(this._state.vars[v] ?? ''));
  }

  private dialogueDef(id: Id): DialogueDef {
    const def = this.content.dialogues[id];
    if (!def) throw new Error(`Diàleg desconegut: ${id}`);
    return def;
  }

  private enterNode(def: DialogueDef, nodeId: Id, lines: ResolvedLine[], depth = 0): DialogueStep {
    if (depth > 50) throw new Error(`Bucle de "goto" al diàleg "${def.id}" (node "${nodeId}").`);
    const node = def.nodes[nodeId];
    if (!node) throw new Error(`Node "${nodeId}" no existeix al diàleg "${def.id}".`);

    applyEffects(node.effects, this.effectCtx());

    for (const line of node.lines ?? []) {
      if (!this.check(line.if)) continue;
      applyEffects(line.effects, this.effectCtx());
      lines.push({ who: line.who, key: line.text, text: this.t(line.text), ...(line.sound && { sound: this.soundName(line.sound) }) });
    }

    // Es marca després de les línies: dins el node, `seen` vol dir "en una visita anterior".
    const key = seenKey(def.id, nodeId);
    this._state.dialogue.seen[key] = (this._state.dialogue.seen[key] ?? 0) + 1;

    const step = this.stepAt(def, nodeId, lines);
    if (step.choices.length === 0 && node.goto) return this.enterNode(def, node.goto, lines, depth + 1);
    return step;
  }

  private stepAt(def: DialogueDef, node: Id, lines: ResolvedLine[]): DialogueStep {
    const choices = this.availableChoices(def, node);
    if (choices.length === 0) return this.endStep(def.id, node, lines);
    this.sessions.set(def.id, node);
    return { dialogue: def.id, node, lines, choices, ended: false };
  }

  private endStep(dialogue: Id, node: Id, lines: ResolvedLine[]): DialogueStep {
    this.sessions.end(dialogue);
    return { dialogue, node, lines, choices: [], ended: true };
  }

  private availableChoices(def: DialogueDef, nodeId: Id): ResolvedChoice[] {
    return (def.nodes[nodeId]?.choices ?? [])
      .filter((c) => this.isChoiceAvailable(def.id, nodeId, c))
      .map((c) => ({ id: c.id, node: nodeId, key: c.text, text: this.t(c.text) }));
  }

  private isChoiceAvailable(dialogue: Id, node: Id, c: DialogueChoiceDef) {
    if (c.once && (this._state.dialogue.chosen[chosenKey(dialogue, node, c.id)] ?? 0) > 0) return false;
    return this.check(c.if);
  }

  private condCtx(): ConditionContext {
    return { state: this._state, world: this.world };
  }

  private effectCtx(): EffectContext {
    return {
      content: this.content,
      state: this._state,
      emit: (e) => this.emit(e),
    };
  }

  /** Executa `fn`, després revisa missions i avisa d'un sol `stateChanged`. */
  private batch<T>(fn: () => T): T {
    this.batchDepth++;
    try {
      const result = fn();
      if (this.batchDepth === 1) this.updateQuests();
      return result;
    } finally {
      this.batchDepth--;
      if (this.batchDepth === 0) this.notify();
    }
  }

  /** Activa, avança, completa i falla missions segons les seves condicions. */
  private updateQuests() {
    const ctx = this.effectCtx();
    for (let pass = 0, changed = true; changed && pass < 20; pass++) {
      changed = false;
      for (const [id, def] of Object.entries(this.content.quests)) {
        const qs = this._state.quests[id]!;
        if (qs.status === 'inactive' && def.startWhen && this.check(def.startWhen)) {
          applyEffects([{ startQuest: id }], ctx);
          changed = true;
        }
        if (qs.status !== 'active') continue;
        for (const o of def.objectives) {
          if (!qs.objectives[o.id] && o.completeWhen && this.check(o.completeWhen)) {
            applyEffects([{ completeObjective: { quest: id, objective: o.id } }], ctx);
            changed = true;
          }
        }
        if (def.failWhen && this.check(def.failWhen)) {
          finishQuest(id, 'failed', ctx);
          changed = true;
        } else if (this.isQuestDone(def, qs)) {
          finishQuest(id, 'completed', ctx);
          changed = true;
        }
      }
    }
  }

  private isQuestDone(def: QuestDef, qs: NarrativeState['quests'][string]) {
    if (def.completeWhen) return this.check(def.completeWhen);
    const required = def.objectives.filter((o) => !o.optional);
    return required.length > 0 && required.every((o) => qs.objectives[o.id]);
  }

  private emit(e: NarrativeEvent) {
    for (const l of this.listeners) l(e);
  }

  private notify() {
    this.emit({ type: 'stateChanged' });
  }
}
