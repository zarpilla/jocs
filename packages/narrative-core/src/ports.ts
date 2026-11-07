import type { Id, Scalar } from './types.js';

/**
 * El que el nucli necessita saber del món i que només el motor gràfic sap.
 * Cada motor (Benne, un altre, els tests) en dona una implementació.
 */
export interface WorldPort {
  hasItem(item: Id): boolean;
  hasVisited(room: Id): boolean;
  currentRoom(): Id | null;
}

/**
 * Coses que han passat i que el motor gràfic ha d'executar o mostrar.
 * El nucli mai no toca l'inventari ni la pantalla: només emet això.
 */
export type NarrativeEvent =
  | { type: 'giveItem'; item: Id }
  | { type: 'takeItem'; item: Id }
  | { type: 'questStarted'; quest: Id }
  | { type: 'objectiveCompleted'; quest: Id; objective: Id }
  | { type: 'questCompleted'; quest: Id }
  | { type: 'questFailed'; quest: Id }
  | { type: 'ending'; ending: Id }
  | { type: 'custom'; name: string; args: Record<string, Scalar> }
  /** L'estat ha canviat: cal desar-lo i refrescar el que en depèn (objectes visibles...). */
  | { type: 'stateChanged' };

export type NarrativeListener = (event: NarrativeEvent) => void;

/** Món buit per a tests i eines (validació, simulació). */
export class MemoryWorld implements WorldPort {
  items = new Set<Id>();
  visited = new Set<Id>();
  room: Id | null = null;

  hasItem(item: Id) {
    return this.items.has(item);
  }
  hasVisited(room: Id) {
    return this.visited.has(room);
  }
  currentRoom() {
    return this.room;
  }
  enter(room: Id) {
    this.room = room;
    this.visited.add(room);
  }
  /** Aplica els esdeveniments d'inventari, com faria un motor real. */
  readonly listener: NarrativeListener = (e) => {
    if (e.type === 'giveItem') this.items.add(e.item);
    if (e.type === 'takeItem') this.items.delete(e.item);
  };
}
