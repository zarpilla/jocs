// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
/**
 * La interfície tàctil (sense barra de verbs): què vol dir tocar una cosa, i quines accions té el menú de mantenir
 * premut.
 *
 * TS pur (només el nucli): el fan servir el runtime de Benne (`tactil.script.ts`) i el mesurador dels tests
 * (`adapters/benne/tactil/mesura.ts`). El contingut no canvia: els JSON continuen dient `verb: ["use", "open"]`;
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

/** El flag que recorda que ja s'ha mirat una cosa (un personatge, a qualsevol sala; una cosa, a la seva sala). */
export function flagMirat(narrative: Narrative, target: InteractionTarget, room?: string): string {
  const on = target.kind === 'character' ? 'personatge' : (room ?? narrative.world.currentRoom() ?? '');
  return `mirat.${on}.${target.id}`;
}

export const isMirat = (narrative: Narrative, target: InteractionTarget, room?: string) =>
  narrative.flag(flagMirat(narrative, target, room));

/** Apunta que s'ha mirat una cosa (va a l'estat del nucli: es desa amb la partida). */
export function marcaMirat(narrative: Narrative, target: InteractionTarget, room?: string) {
  const flag = flagMirat(narrative, target, room);
  if (!narrative.flag(flag)) narrative.apply({ setFlag: flag });
}

/** Què fa un toc: mirar, fer una acció, o obrir el menú perquè triï el jugador. */
export type Toc = { fa: 'mira' } | { fa: 'accio'; verb: string } | { fa: 'menu' };

/**
 * Què fa tocar una cosa:
 *  1. Si encara no s'ha mirat mai (i té alguna cosa a dir), la mira: la descripció, amb l'humor i les pistes,
 *     surt sense cap gest de més. Les sortides (que només es poden travessar) no: anar-hi no ha de costar dos tocs.
 *  2. Si té una sola acció, la fa.
 *  3. Si en té més d'una (encara que alguna sigui una broma), obre el menú: el joc no tria per tu quin verb
 *     resol el trencaclosques (empènyer o estirar).
 *  Sense cap acció, la mira.
 */
export function queFaElToc(narrative: Narrative, target: InteractionTarget, room?: string): Toc {
  const totes = accions(narrative, target, room);
  const unica = totes.length === 1 ? totes[0] : undefined;
  const sortida = unica?.verbs.includes('walkTo') === true;
  const teMira = narrative.peek({ verb: 'look', target, room }) !== undefined;
  if (teMira && !sortida && !isMirat(narrative, target, room)) return { fa: 'mira' };
  if (unica) return { fa: 'accio', verb: unica.verb };
  if (totes.length === 0) return { fa: 'mira' };
  return { fa: 'menu' };
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
