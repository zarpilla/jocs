/**
 * El plànol de l'Arenga (guio/guio.md, «Regles del món · 8»): des de l'Escena 6, qui el porta pot anar a una
 * sala clicant-la al plànol, en lloc de caminar-hi porta a porta.
 *
 * La regla és una: **el plànol no obre cap porta que no s'obri caminant.** El camí es calcula amb les mateixes
 * portes del JSON, i a cada porta es mira què passaria si s'hi caminés ara (`peekInteraction`, el primer que
 * encaixa, com quan es clica). Així, tots els bloquejos de les escenes (la nit, els paperets de l'Escena 5, la Vet
 * que entreté en Bastida a popa...) valen igual amb el plànol, sense cap regla repetida:
 *
 *  - Una porta deixa passar si el que hi passaria ara és un `goTo` sense objecte. Les que demanen un objecte (la
 *    cisalla al cadenat, la clau d'en Tomàs al registre) no es fan mai des del plànol.
 *  - Si no s'hi pot arribar, la protagonista diu la frase de la porta que la tanca (si és una frase seva i la
 *    porta no fa res més); si no, una de genèrica.
 *  - Una sala de pas que, en entrar-hi, faria alguna cosa (un `onEnter` pendent) atura el viatge: s'hi va i
 *    hi passa el que hi havia de passar, com si s'hi hagués arribat caminant.
 *
 * Fer servir el plànol és caminar: no gasta torn a les sincronies (no passa per `onAfterAction`).
 */
import type { Narrative } from '@aventura/narrative-core';

export const MAPA_ITEM = 'mapa';

export const MAPA_TEXTS = ['mapa.aqui', 'mapa.tancat'];

/** Una línia que diu la protagonista (clau de text). */
export interface LiniaMapa {
  who: 'player';
  text: string;
}

export interface Viatge {
  /** On s'ha d'anar (la sala triada, o una sala de pas on passa alguna cosa). `null`: no es va enlloc. */
  sala: string | null;
  /** El que diu la protagonista si no hi pot anar. */
  linies: LiniaMapa[];
}

/** Les sales del plànol: les sales jugables (les compartides), no les cinemàtiques. */
export function salesDelPlanol(n: Narrative): string[] {
  return Object.entries(n.content.rooms)
    .filter(([, r]) => !r.cutscene && (r.protagonists?.length ?? 0) > 0)
    .map(([id]) => id);
}

/** Les portes d'una sala: cada cosa amb alguna interacció que porta a una altra sala sense objecte. */
function portes(n: Narrative, sala: string): { id: string; cap: string }[] {
  const out: { id: string; cap: string }[] = [];
  for (const [id, h] of Object.entries(n.content.rooms[sala]?.hotspots ?? {})) {
    const cap = h.interactions?.find((i) => i.goTo && !i.item)?.goTo;
    if (cap) out.push({ id, cap });
  }
  return out;
}

/** Si es pot passar ara per una porta (el que passaria en caminar-hi és anar a l'altra sala). */
function obertaAra(n: Narrative, sala: string, porta: string) {
  if (!n.isHotspotVisible(sala, porta)) return false;
  const i = n.peekInteraction(sala, porta, 'walkTo');
  return !!i?.goTo && !i.item;
}

/** Camí més curt (sales, sense l'origen) per les portes obertes; `aturades` no es travessen (s'hi pot acabar). */
function cami(n: Narrative, des: string, cap: string, opts: { obertes: boolean; aturades?: Set<string> }): string[] | null {
  const prev = new Map<string, string>([[des, '']]);
  const cua = [des];
  while (cua.length) {
    const r = cua.shift()!;
    if (r === cap) break;
    if (r !== des && opts.aturades?.has(r)) continue;
    for (const p of portes(n, r)) {
      if (prev.has(p.cap) || (opts.obertes && !obertaAra(n, r, p.id))) continue;
      prev.set(p.cap, r);
      cua.push(p.cap);
    }
  }
  if (!prev.has(cap)) return null;
  const out: string[] = [];
  for (let r = cap; r !== des; r = prev.get(r)!) out.unshift(r);
  return out;
}

/** Les sales on es pot arribar ara des d'on és la protagonista que juga (per mostrar-les al plànol). */
export function accessibles(n: Narrative): Set<string> {
  const des = n.world.currentRoom();
  const out = new Set<string>();
  if (!des) return out;
  for (const sala of salesDelPlanol(n)) if (sala === des || cami(n, des, sala, { obertes: true })) out.add(sala);
  return out;
}

const player = (text: string): LiniaMapa => ({ who: 'player', text });

/** Què passa si la protagonista que juga tria `cap` al plànol. */
export function viatge(n: Narrative, cap: string): Viatge {
  const des = n.world.currentRoom();
  if (!des || des === cap) return { sala: null, linies: [player('mapa.aqui')] };
  const pas = cami(n, des, cap, { obertes: true });
  if (!pas) return { sala: null, linies: perQueNo(n, des, cap) };
  // Les sales de pas on, en entrar-hi, passaria alguna cosa: millor un camí que no hi passi; si no n'hi ha, s'hi
  // va i s'hi queda (hi passa el que hi havia de passar).
  const aturades = new Set(salesDelPlanol(n).filter((s) => s !== cap && s !== des && n.peekEnter(s)));
  if (!pas.some((s) => aturades.has(s)) || cami(n, des, cap, { obertes: true, aturades })) return { sala: cap, linies: [] };
  return { sala: pas.find((s) => aturades.has(s))!, linies: [] };
}

/**
 * Per què no s'hi pot anar: la primera porta tancada del camí que hi hauria si totes fossin obertes. La seva frase,
 * si és de la protagonista i la porta no fa res més (cap efecte, ni diàleg, ni acció); si no, la genèrica.
 */
function perQueNo(n: Narrative, des: string, cap: string): LiniaMapa[] {
  const pas = cami(n, des, cap, { obertes: false }) ?? [];
  let r = des;
  for (const s of pas) {
    const porta = portes(n, r).find((p) => p.cap === s);
    if (porta && !obertaAra(n, r, porta.id)) {
      const i = n.peekInteraction(r, porta.id, 'walkTo');
      const quiet = i && !i.effects?.length && !i.action && !i.dialogue && !(i.lines ?? []).some((l) => l.effects?.length);
      const linies = (i?.lines ?? []).filter((l) => n.check(l.if));
      if (quiet && linies.length && linies.every((l) => l.who === 'player')) return linies.map((l) => player(l.text));
      break;
    }
    r = s;
  }
  return [player('mapa.tancat')];
}
