/**
 * Jugador sense gràfics: un adaptador mínim que fa el que faria un motor
 * (moure's de sala, canviar de protagonista, conduir diàlegs) però en text.
 * Serveix per als tests, per provar el guió de cap a peus i, si cal, per a una
 * versió de text del joc.
 */
import type { ResolvedLine } from './dialogue.js';
import type { InteractionResult, InteractionTarget, Narrative } from './narrative.js';
import { MemoryWorld } from './ports.js';
import type { Id } from './types.js';

export interface HeadlessOptions {
  /** Nom de l'esdeveniment `{ "event": ... }` que canvia de protagonista (arg `id`). */
  switchEvent?: string;
}

export class HeadlessPlayer {
  /** Tot el que s'ha dit, en ordre (per depurar o per a una transcripció). */
  readonly transcript: string[] = [];
  private pendingSwitch: Id | null = null;
  /**
   * Si és cert, els diàlegs que obre una interacció no es juguen sols: queden a
   * `pendingDialogue` perquè els condueixi qui fa servir el jugador (p. ex. un terminal).
   */
  deferDialogues = false;
  pendingDialogue: Id | null = null;

  readonly narrative: Narrative;
  readonly world: MemoryWorld;

  constructor(narrative: Narrative, world: MemoryWorld, opts: HeadlessOptions = {}) {
    this.narrative = narrative;
    this.world = world;
    narrative.on(world.listener);
    narrative.on((e) => {
      if (e.type === 'custom' && e.name === (opts.switchEvent ?? 'protagonista')) this.pendingSwitch = String(e.args.id);
    });
  }

  /** Partida nova: inventaris i sales inicials, i entra a la sala de la primera protagonista. */
  newGame(): ResolvedLine[] {
    const starts = this.narrative.newGame();
    const first = this.narrative.content.manifest.protagonists[0]!;
    for (const [who, room] of Object.entries(starts)) this.world.rooms.set(who, room);
    this.world.active = first;
    return this.goTo(starts[first]!);
  }

  get room() {
    return this.world.room;
  }

  get active() {
    return this.world.active;
  }

  /** Entra a una sala (i n'executa l'`onEnter`). */
  goTo(room: Id): ResolvedLine[] {
    this.world.enter(room);
    this.narrative.worldChanged();
    return this.play(this.narrative.enterRoom(room));
  }

  /** Canvia de protagonista; si és la primera vegada que hi és, entra a la seva sala. */
  switchTo(who: Id): ResolvedLine[] {
    const firstTime = !this.world.rooms.has(who) || !this.world.visited.has(this.world.rooms.get(who)!);
    this.world.switchTo(who);
    this.narrative.worldChanged();
    if (firstTime && this.world.room) return this.goTo(this.world.room);
    return this.play(this.world.room ? this.narrative.enterRoom(this.world.room) : null);
  }

  /** Un verb sobre una cosa de la sala (o un objecte de l'inventari amb `kind: 'item'`). */
  do(verb: Id, target: Id | InteractionTarget, item?: Id): ResolvedLine[] {
    const t: InteractionTarget = typeof target === 'string' ? { kind: this.kindOf(target), id: target } : target;
    if (t.kind !== 'item' && this.world.room && !this.narrative.isHotspotVisible(this.world.room, t.id)) {
      throw new Error(`"${t.id}" no és visible a ${this.world.room} ara mateix.`);
    }
    if (item && !this.world.hasItem(item)) throw new Error(`${this.active} no té "${item}".`);
    const result = this.narrative.interact({ verb, target: t, item });
    return result ? this.play(result) : this.say([this.narrative.defaultLine(verb)]);
  }

  /** Fer servir un objecte de l'inventari amb una cosa. */
  use(item: Id, target: Id | InteractionTarget): ResolvedLine[] {
    return this.do('use', target, item);
  }

  /** Tria opcions en ordre dins el diàleg que estigui obert (o l'obre). */
  talk(dialogue: Id, ...choices: Id[]): ResolvedLine[] {
    let step = this.narrative.startDialogue(dialogue);
    const lines = this.say(step.lines);
    for (const choice of choices) {
      if (!step.choices.some((c) => c.id === choice)) {
        throw new Error(`Opció "${choice}" no disponible a ${dialogue}/${step.node}. Hi ha: ${step.choices.map((c) => c.id).join(', ')}`);
      }
      step = this.narrative.choose(dialogue, choice);
      lines.push(...this.say(step.lines));
    }
    if (!step.ended) this.narrative.endDialogue(dialogue);
    return lines;
  }

  inventory(who?: Id) {
    return this.world.items(who);
  }

  private kindOf(id: Id): InteractionTarget['kind'] {
    return this.narrative.content.characters[id] ? 'character' : 'hotspot';
  }

  private play(result: InteractionResult | null): ResolvedLine[] {
    if (!result) return [];
    const lines = this.say(result.lines);
    if (result.dialogue) {
      if (this.deferDialogues) this.pendingDialogue = result.dialogue;
      else lines.push(...this.talk(result.dialogue));
    }
    if (this.pendingSwitch) {
      const who = this.pendingSwitch;
      this.pendingSwitch = null;
      lines.push(...this.switchTo(who));
    } else if (result.goTo) {
      lines.push(...this.goTo(result.goTo));
    }
    return lines;
  }

  /** Afegeix línies a la transcripció i hi resol `player` (per a qui condueix els diàlegs pel seu compte). */
  say(lines: ResolvedLine[]): ResolvedLine[] {
    // `player` es resol ara: si després es canvia de protagonista, la línia continua sent de qui la va dir.
    const resolved = lines.map((l) => (l.who === 'player' ? { ...l, who: this.active } : l));
    for (const l of resolved) this.transcript.push(`${l.who}: ${l.text}`);
    return resolved;
  }
}
