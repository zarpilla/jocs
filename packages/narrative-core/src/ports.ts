import type { Id, Scalar } from './types.js';

/**
 * El que el nucli necessita saber del món i que només el motor gràfic sap.
 * Cada motor (Benne, un altre, els tests) en dona una implementació.
 */
export interface WorldPort {
  /** Sense `who`, la protagonista activa. */
  hasItem(item: Id, who?: Id): boolean;
  hasVisited(room: Id): boolean;
  currentRoom(): Id | null;
  activeProtagonist(): Id;
  /** On és (o era, l'última vegada) una protagonista, encara que ara no jugui. */
  protagonistRoom?(who: Id): Id | null;
}

/**
 * Coses que han passat i que el motor gràfic ha d'executar o mostrar.
 * El nucli mai no toca l'inventari ni la pantalla: només emet això.
 */
export type NarrativeEvent =
  /** `who`: a qui (sense `who`, la protagonista activa). */
  | { type: 'giveItem'; item: Id; who?: Id }
  | { type: 'takeItem'; item: Id; who?: Id }
  | { type: 'questStarted'; quest: Id }
  | { type: 'objectiveCompleted'; quest: Id; objective: Id }
  | { type: 'questCompleted'; quest: Id }
  | { type: 'questFailed'; quest: Id }
  | { type: 'ending'; ending: Id }
  | { type: 'custom'; name: string; args: Record<string, Scalar> }
  /** L'estat ha canviat: cal desar-lo i refrescar el que en depèn (objectes visibles...). */
  | { type: 'stateChanged' };

export type NarrativeListener = (event: NarrativeEvent) => void;

/** Món en memòria per a tests i eines: inventari per protagonista, sales visitades. */
export class MemoryWorld implements WorldPort {
  inventories = new Map<Id, Set<Id>>();
  visited = new Set<Id>();
  room: Id | null = null;
  /** Sala on és cada protagonista. */
  rooms = new Map<Id, Id>();

  active: Id;

  constructor(active: Id = 'player') {
    this.active = active;
  }

  private bag(who: Id = this.active) {
    let bag = this.inventories.get(who);
    if (!bag) this.inventories.set(who, (bag = new Set()));
    return bag;
  }

  hasItem(item: Id, who?: Id) {
    return this.bag(who).has(item);
  }
  hasVisited(room: Id) {
    return this.visited.has(room);
  }
  currentRoom() {
    return this.room;
  }
  activeProtagonist() {
    return this.active;
  }
  protagonistRoom(who: Id) {
    return who === this.active ? this.room : this.rooms.get(who) ?? null;
  }
  items(who?: Id) {
    return [...this.bag(who)];
  }
  give(item: Id, who?: Id) {
    this.bag(who).add(item);
  }
  enter(room: Id) {
    this.room = room;
    this.visited.add(room);
    this.rooms.set(this.active, room);
  }
  /** Canvia de protagonista i torna a la sala on era. */
  switchTo(who: Id) {
    this.active = who;
    this.room = this.rooms.get(who) ?? null;
  }
  /** Aplica els esdeveniments d'inventari, com faria un motor real. */
  readonly listener: NarrativeListener = (e) => {
    if (e.type === 'giveItem') this.bag(e.who).add(e.item);
    if (e.type === 'takeItem') this.bag(e.who).delete(e.item);
  };
}
