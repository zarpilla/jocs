// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
/**
 * La interfície tàctil (sense barra de verbs): què vol dir tocar una cosa, i quines accions té el menú de mantenir
 * premut.
 *
 * TS pur (només el nucli): el fan servir el runtime de Benne (`tactil.script.ts`) i el mesurador dels tests
 * (`adapters/benne/tactil/mesura.ts`). El contingut no canvia: els JSON continuen dient `verb: ["use", "open"]`;
 * aquí es decideix, en cada moment, quins d'aquests verbs fan alguna cosa i quin és el principal.
 */
import type { GameContent, InteractionDef, InteractionTarget, Narrative } from '@aventura/narrative-core';

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
 * diferent que encaixaria ara (condicions, `once` ja gastats). Els verbs que porten a la mateixa interacció (o a una
 * que fa exactament el mateix) són una sola acció.
 */
export function accions(narrative: Narrative, target: InteractionTarget, room?: string): Accio[] {
  const out: (Accio & { def: InteractionDef; que: string })[] = [];
  for (const verb of VERBS_ACCIO) {
    const def = narrative.peek({ verb, target, room });
    if (!def) continue;
    // La mateixa interacció, o una que fa exactament el mateix (el walkie: «parla» i «fes servir» obren el mateix
    // diàleg, escrits per separat): una sola acció.
    const que = queFa(def);
    const same = out.find((a) => a.def === def || a.que === que);
    if (same) same.verbs.push(verb);
    else out.push({ verb, verbs: [verb], inert: isInert(def), def, que });
  }
  return out.map(({ def: _def, que: _que, ...a }) => a);
}

/** El que fa una interacció, sense el verb: dues amb el mateix «què fa» són la mateixa acció. */
function queFa(def: InteractionDef): string {
  const { verb: _verb, ...resta } = def;
  return JSON.stringify(resta);
}

/** El flag que recorda que ja s'ha mirat una cosa (un personatge, a qualsevol sala; una cosa, a la seva sala). */
/**
 * Quina de les descripcions d'una cosa toca ara (la posició, a les llistes d'interaccions, del «mira» que faria),
 * o `null` si no en té cap.
 */
function miraDeAra(narrative: Narrative, target: InteractionTarget, room?: string): number | null {
  const def = narrative.peek({ verb: 'look', target, room });
  if (!def) return null;
  const sala = room ?? narrative.world.currentRoom() ?? '';
  const { rooms, characters, items } = narrative.content;
  const llistes = [
    target.kind !== 'item' ? rooms[sala]?.hotspots[target.id]?.interactions : undefined,
    target.kind === 'character' ? characters[target.id]?.interactions : undefined,
    target.kind === 'item' ? items[target.id]?.interactions : undefined,
  ];
  for (let l = 0; l < llistes.length; l++) {
    const i = (llistes[l] ?? []).indexOf(def);
    if (i >= 0) return l * 1000 + i;
  }
  return 0;
}

/**
 * El flag que recorda que ja s'ha vist la descripció d'ara d'una cosa (un personatge, a qualsevol sala; una cosa, a
 * la seva sala). Va per descripció: quan una cosa en té una de nova (ha canviat alguna cosa), el primer toc la torna
 * a mirar.
 */
export function flagMirat(narrative: Narrative, target: InteractionTarget, room?: string): string {
  const on = target.kind === 'character' ? 'personatge' : target.kind === 'item' ? 'objecte' : (room ?? narrative.world.currentRoom() ?? '');
  return `mirat.${on}.${target.id}.${miraDeAra(narrative, target, room) ?? 0}`;
}

export const isMirat = (narrative: Narrative, target: InteractionTarget, room?: string) =>
  narrative.flag(flagMirat(narrative, target, room));

/** Apunta que s'ha mirat una cosa (va a l'estat del nucli: es desa amb la partida). */
export function marcaMirat(narrative: Narrative, target: InteractionTarget, room?: string) {
  const flag = flagMirat(narrative, target, room);
  if (!narrative.flag(flag)) narrative.apply({ setFlag: flag });
}

/** Totes les interaccions del contingut (de les coses de les sales, dels personatges i dels objectes). */
function totes(content: GameContent): InteractionDef[] {
  const out: InteractionDef[] = [];
  for (const room of Object.values(content.rooms)) {
    for (const h of Object.values(room.hotspots ?? {})) out.push(...(h.interactions ?? []));
  }
  for (const c of Object.values(content.characters)) out.push(...(c.interactions ?? []));
  for (const it of Object.values(content.items)) out.push(...(it.interactions ?? []));
  return out;
}

/**
 * Si hi ha algun comodí `*` que fa alguna cosa (no una broma de «qualsevol objecte»): un canal que porta objectes
 * (el muntacàrregues, el tub, la Mosca, la safata) o donar-lo a l'altra protagonista. Llavors qualsevol objecte s'hi
 * pot voler fer servir.
 */
export function hiHaComodi(content: GameContent): boolean {
  return totes(content).some((i) => i.item === '*' && !isInert(i));
}

/**
 * Si un objecte es fa servir sol: el contingut no el combina mai amb res (cap interacció el demana, ni ell en
 * demana cap; el comodí `*`, les bromes de «qualsevol objecte», no compta). Llavors tocar-lo a l'inventari no el
 * pren a la mà: en fa l'acció (el plànol s'obre d'un toc). Ho fa servir el sync (`defaultVerb` de l'objecte).
 *
 * Un comodí que fa coses (`hiHaComodi`: la mostra al muntacàrregues, la nota a la safata) sí que compta, però
 * només per als objectes que no tenen cap acció pròpia: un paper es pren a la mà (no té res més a fer), i el
 * comunicador, que s'obre sol, continua sent sol (es pot prendre a la mà des del menú: `potAnarALaMa`).
 */
export function objecteSol(content: GameContent, item: string): boolean {
  const demana = (list: InteractionDef[] | undefined) => (list ?? []).some((i) => i.item === item);
  if (demana(totes(content))) return false;
  const propies = content.items[item]?.interactions ?? [];
  if (propies.some((i) => i.item !== undefined && i.item !== '*')) return false;
  const actua = propies.some((i) => i.item === undefined && [i.verb].flat().some((v) => v !== 'look'));
  if (!actua && hiHaComodi(content)) return false;
  return true;
}

/** Si un objecte es pot prendre a la mà (per fer-lo servir amb una altra cosa): el toc o, si és sol, el menú. */
export function potAnarALaMa(content: GameContent, item: string): boolean {
  return !objecteSol(content, item) || hiHaComodi(content);
}

/** Què fa un toc: mirar, fer una acció, o obrir el menú perquè triï el jugador. */
export type Toc = { fa: 'mira' } | { fa: 'accio'; verb: string } | { fa: 'menu' };

/**
 * Què fa tocar una cosa:
 *  1. Amb el dit (`mirarPrimer`), si encara no s'ha mirat mai (i té alguna cosa a dir), la mira: la descripció,
 *     amb l'humor i les pistes, surt sense cap gest de més. Les sortides (que només es poden travessar) no: anar-hi
 *     no ha de costar dos tocs. Amb el ratolí no: el clic dret ja mira.
 *  2. Si té una sola acció, la fa.
 *  3. Si en té més d'una (encara que alguna sigui una broma), obre el menú: el joc no tria per tu quin verb
 *     resol el trencaclosques (empènyer o estirar).
 *  Sense cap acció, la mira.
 */
export function queFaElToc(
  narrative: Narrative, target: InteractionTarget, room?: string, opts: { mirarPrimer?: boolean } = {},
): Toc {
  if (target.kind === 'item') return queFaElTocObjecte(narrative, target);
  const mirarPrimer = opts.mirarPrimer ?? true;
  const totes = accions(narrative, target, room);
  const unica = totes.length === 1 ? totes[0] : undefined;
  const sortida = unica?.verbs.includes('walkTo') === true;
  const teMira = narrative.peek({ verb: 'look', target, room }) !== undefined;
  if (mirarPrimer && teMira && !sortida && !isMirat(narrative, target, room)) return { fa: 'mira' };
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

/**
 * Tocar un objecte sol (`objecteSol`) a l'inventari: si té una sola acció, la fa (sense mirar-lo abans: ja és a la
 * safata, amb el nom); si en té més d'una, obre el menú; si no en té cap, el mira.
 */
export function queFaElTocObjecte(narrative: Narrative, target: InteractionTarget): Toc {
  const totes = accions(narrative, target);
  if (totes.length === 1) return { fa: 'accio', verb: totes[0]!.verb };
  if (totes.length > 1) return { fa: 'menu' };
  return { fa: 'mira' };
}
