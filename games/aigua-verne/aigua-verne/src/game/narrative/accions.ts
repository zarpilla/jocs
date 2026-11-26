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
  // L'etiqueta és el primer verb que l'autor ha escrit a la interacció (`["open", "use", "pickUp"]` → «Obre»), no
  // el primer de `VERBS_ACCIO`: si no, tot el que també es pot «agafar» diria «Agafa». Una porta (per on es pot
  // anar), però, sempre diu «Ves-hi».
  for (const a of out) {
    const preferit = a.verbs.includes('walkTo') ? 'walkTo' : [a.def.verb].flat().find((v) => a.verbs.includes(v));
    if (preferit) a.verb = preferit;
  }
  return out.map(({ def: _def, que: _que, ...a }) => a);
}

/** El que fa una interacció, sense el verb: dues amb el mateix «què fa» són la mateixa acció. */
function queFa(def: InteractionDef): string {
  const { verb: _verb, ...resta } = def;
  return JSON.stringify(resta);
}

/** On és una interacció a les llistes d'una cosa (la sala, el personatge, l'objecte), per anomenar-la en un flag. */
function posicio(narrative: Narrative, target: InteractionTarget, def: InteractionDef, room?: string): number {
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

/** Quina de les descripcions d'una cosa toca ara, o `null` si no en té cap. */
function miraDeAra(narrative: Narrative, target: InteractionTarget, room?: string): number | null {
  const def = narrative.peek({ verb: 'look', target, room });
  return def ? posicio(narrative, target, def, room) : null;
}

/** Les accions d'ara d'una cosa, com a text curt (quines interaccions faria): per saber si han canviat. */
function firmaAccions(narrative: Narrative, target: InteractionTarget, room?: string): string {
  const defs: InteractionDef[] = [];
  for (const verb of VERBS_ACCIO) {
    const def = narrative.peek({ verb, target, room });
    if (def && !defs.includes(def)) defs.push(def);
  }
  return defs.map((d) => posicio(narrative, target, d, room)).join('-');
}

/**
 * El prefix dels flags de «ja mirat» d'una cosa: un personatge, a qualsevol sala però per a cada protagonista (cada
 * germana el veu amb els seus ulls: la seva frase); una cosa, a la seva sala.
 */
function prefixMirat(narrative: Narrative, target: InteractionTarget, room?: string): string {
  const on = target.kind === 'character' ? `personatge.${narrative.world.activeProtagonist()}`
    : target.kind === 'item' ? 'objecte' : (room ?? narrative.world.currentRoom() ?? '');
  return `mirat.${on}.${target.id}`;
}

/**
 * El flag que recorda que ja s'ha vist la descripció d'ara d'una cosa. Va per descripció: quan una cosa en té una
 * de nova (ha canviat alguna cosa), pot tornar a tocar mirar-la (`isMirat`).
 */
export function flagMirat(narrative: Narrative, target: InteractionTarget, room?: string): string {
  return `${prefixMirat(narrative, target, room)}.${miraDeAra(narrative, target, room) ?? 0}`;
}

/** El flag que recorda que ja s'ha vist una cosa amb les accions que té ara. */
function flagAccions(narrative: Narrative, target: InteractionTarget, room?: string): string {
  return `${prefixMirat(narrative, target, room)}.a${firmaAccions(narrative, target, room)}`;
}

/**
 * Si ja s'ha vist una cosa tal com és ara: se n'ha vist la descripció d'ara, o, si la descripció és nova, la cosa
 * encara fa el mateix que quan es va veure. Només es torna a mirar quan han canviat totes dues: la descripció i el
 * que s'hi pot fer (el panell que no es pot tornar a obrir, el Llibre Major d'una fase a l'altra, no).
 */
export function isMirat(narrative: Narrative, target: InteractionTarget, room?: string): boolean {
  if (narrative.flag(flagMirat(narrative, target, room))) return true;
  // una descripció que fa alguna cosa (la sang del panell: és una prova) s'ha de veure, faci el que faci la cosa
  return miraInerta(narrative, target, room) && narrative.flag(flagAccions(narrative, target, room));
}

/** Si la descripció d'ara d'una cosa només diu coses (o no en té). */
function miraInerta(narrative: Narrative, target: InteractionTarget, room?: string): boolean {
  const def = narrative.peek({ verb: 'look', target, room });
  return !def || isInert(def);
}

/**
 * Apunta que s'ha vist una cosa tal com és ara (va a l'estat del nucli: es desa amb la partida). Es crida en mirar
 * (abans i després: la descripció que queda també és vista) i després de fer-hi qualsevol cosa (`haFet`).
 */
export function marcaMirat(narrative: Narrative, target: InteractionTarget, room?: string) {
  for (const flag of [flagMirat(narrative, target, room), flagAccions(narrative, target, room)]) {
    if (!narrative.flag(flag)) narrative.apply({ setFlag: flag });
  }
}

/**
 * Després de fer una cosa sobre una cosa (mirar-la, obrir-la, fer-hi servir un objecte): el que en queda ja és vist,
 * perquè el jugador acaba de veure què ha passat. El toc següent no la torna a mirar (el panell que l'Iri «ha de
 * tancar ara mateix»). `room` és la sala on era la cosa (si l'acció ha canviat de sala, ja no és l'actual).
 */
export function haFet(narrative: Narrative, target: InteractionTarget, room?: string) {
  if (target.kind !== 'item' && room !== undefined && room !== narrative.world.currentRoom()) return;
  // una descripció que fa alguna cosa no es dona per vista sense haver-la vist (`isMirat`)
  const flags = [flagAccions(narrative, target, room)];
  if (miraInerta(narrative, target, room)) flags.push(flagMirat(narrative, target, room));
  for (const flag of flags) if (!narrative.flag(flag)) narrative.apply({ setFlag: flag });
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
 * comunicador, que s'obre sol, continua sent sol (es pot prendre a la mà des del menú: `potAnarALaMa`). Un objecte
 * `lookOnly` (el quadern, que només es llegeix) també és sol.
 */
export function objecteSol(content: GameContent, item: string): boolean {
  const demana = (list: InteractionDef[] | undefined) => (list ?? []).some((i) => i.item === item);
  if (demana(totes(content))) return false;
  if (content.items[item]?.lookOnly) return true;
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
  const sortida = esSortida(narrative, target, room);
  const teMira = narrative.peek({ verb: 'look', target, room }) !== undefined;
  if (mirarPrimer && teMira && !sortida && !isMirat(narrative, target, room)) return { fa: 'mira' };
  if (unica) return { fa: 'accio', verb: unica.verb };
  if (totes.length === 0) return { fa: 'mira' };
  return { fa: 'menu' };
}

/** Si és una sortida (la seva única acció és anar-hi): s'hi va, no es mira, també amb el clic que mira. */
export function esSortida(narrative: Narrative, target: InteractionTarget, room?: string): boolean {
  if (target.kind === 'item') return false;
  const totes = accions(narrative, target, room);
  return totes.length === 1 && totes[0]!.verbs.includes('walkTo');
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
