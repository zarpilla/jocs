// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
/**
 * Aigua Verne B, sense barra de verbs: què vol dir tocar una cosa, i quines accions té el menú de mantenir premut.
 *
 * TS pur (només el nucli): el fan servir el runtime de Benne (`tactil.script.ts`) i els tests
 * (`game/test/accions.test.ts`). El contingut no canvia: els JSON continuen dient `verb: ["use", "open"]`;
 * aquí es decideix, en cada moment, quins d'aquests verbs fan alguna cosa i quin és el principal.
 */
import type { InteractionDef, InteractionTarget, Narrative } from '@aventura/narrative-core';

/** Els verbs que poden sortir al menú (a part de «mira»), en l'ordre en què hi surten. */
export const VERBS_ACCIO = ['walkTo', 'talkTo', 'pickUp', 'open', 'close', 'push', 'pull', 'use', 'give'] as const;

export interface Accio {
  /** El verb que es farà (el primer de `VERBS_ACCIO` que porta a aquesta interacció). */
  verb: string;
  /** Tots els verbs que porten a la mateixa interacció (p. ex. una porta: walkTo, open, use). */
  verbs: string[];
  /** La interacció no canvia res (només diu línies): una broma, un «no puc». */
  inert: boolean;
}

/** Si una interacció només diu coses: ni efectes, ni acció, ni diàleg, ni canvi de sala. */
export function isInert(i: InteractionDef): boolean {
  return !i.effects?.length && !i.action && !i.dialogue && !i.goTo && !(i.lines ?? []).some((l) => l.effects?.length);
}

/**
 * Les accions que té ara mateix una cosa (sense objecte a la mà), sense «mira»: un verb per a cada interacció
 * diferent que encaixaria ara (condicions, `once` ja gastats). Els verbs que porten a la mateixa interacció
 * són una sola acció.
 */
export function accions(narrative: Narrative, target: InteractionTarget, room?: string): Accio[] {
  const out: (Accio & { def: InteractionDef })[] = [];
  for (const verb of VERBS_ACCIO) {
    const def = narrative.peek({ verb, target, room });
    if (!def) continue;
    const same = out.find((a) => a.def === def);
    if (same) same.verbs.push(verb);
    else out.push({ verb, verbs: [verb], inert: isInert(def), def });
  }
  return out.map(({ def: _def, ...a }) => a);
}

/**
 * El verb d'un toc: l'acció que canvia alguna cosa abans que la que només diu línies (si una cosa es pot
 * empènyer per fer-hi una broma i fer servir per obrir-la, el toc l'obre), i entre iguals, l'ordre de
 * `VERBS_ACCIO` (anar-hi, parlar, agafar, obrir...). Si no n'hi ha cap, mirar.
 */
export function verbDelToc(narrative: Narrative, target: InteractionTarget, room?: string): string {
  const totes = accions(narrative, target, room);
  const util = totes.find((a) => !a.inert);
  return (util ?? totes[0])?.verb ?? 'look';
}

/**
 * Fer servir un objecte amb una cosa: si és un personatge i hi ha una interacció de donar-l'hi, donar; si no,
 * fer-lo servir. (Sense barra ja no es tria entre «Dona» i «Usa».)
 */
export function verbAmbObjecte(narrative: Narrative, target: InteractionTarget, item: string, room?: string): string {
  if (target.kind === 'character' && narrative.peek({ verb: 'give', target, item, room })) return 'give';
  if (narrative.peek({ verb: 'use', target, item, room })) return 'use';
  if (narrative.peek({ verb: 'give', target, item, room })) return 'give';
  return 'use';
}
