import type { Id, SpeakerId, StageCue, TextKey } from './types.js';

/** Una línia ja resolta: condicions avaluades, efectes aplicats, text traduït. */
export interface ResolvedLine {
  who: SpeakerId;
  key: TextKey;
  text: string;
  /** So que ha de fer el motor en dir la línia (ja amb les variables posades). */
  sound?: string;
  /** Moviment abans de dir-la (vegeu `DialogueLineDef.stage`). */
  stage?: StageCue[];
  /** Moviment en acabar de dir-la (vegeu `DialogueLineDef.stageAfter`). */
  stageAfter?: StageCue[];
}

export interface ResolvedChoice {
  id: Id;
  /** Node on viu l'opció (els motors que tenen llistes planes d'opcions ho necessiten). */
  node: Id;
  key: TextKey;
  text: string;
}

/** El que el motor ha de fer després d'un pas de conversa. */
export interface DialogueStep {
  dialogue: Id;
  node: Id;
  /** Per ordre: primer la frase del jugador (si n'hi ha) i després les respostes. */
  lines: ResolvedLine[];
  /** Opcions disponibles ara. Buit si la conversa ha acabat. */
  choices: ResolvedChoice[];
  ended: boolean;
}

/** Converses en curs (no es desa: cap motor deixa desar enmig d'una conversa). */
export class DialogueSessions {
  private current = new Map<Id, Id>();

  get(dialogue: Id) {
    return this.current.get(dialogue);
  }
  set(dialogue: Id, node: Id) {
    this.current.set(dialogue, node);
  }
  end(dialogue: Id) {
    this.current.delete(dialogue);
  }
  clear() {
    this.current.clear();
  }
}
