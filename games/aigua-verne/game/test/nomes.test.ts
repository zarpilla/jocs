/**
 * Les sales i les converses d'una sola protagonista (guio.md, annex D 19): l'altra no hi entra ni hi parla, i ho diu
 * amb una excusa. Qui fa cadascuna és el `jugadora` de veus.json (la veu amb què es graven).
 *
 * `HeadlessPlayer.goTo` i `talk` salten les portes i els videotelèfons: aquí es passa per on passaria qui juga.
 * Primer, que totes les entrades (portes, objectes i personatges que obren la sala o la conversa) tinguin l'excusa
 * davant, o siguin en una sala que ja és d'ella. Després, cada porta, provada.
 */
import { describe, expect, it } from 'vitest';
import type { Condition, Effect, InteractionDef } from '@aventura/narrative-core';
import { amb, item, NOMES, partida } from './partida.js';
import { content } from '../index.js';

const altra = (qui: string) => (qui === 'iri' ? 'vet' : 'iri');
const verbs = (i: InteractionDef) => (Array.isArray(i.verb) ? i.verb : [i.verb]);
/** Les condicions d'un `if`, com a llista (les d'un `all` de dalt de tot). */
const parts = (c: Condition | undefined): string[] => {
  if (!c) return [];
  const all = (c as { all?: Condition[] }).all;
  return (all ?? [c]).map((x) => JSON.stringify(x));
};
const nomesDe = (c: Condition | undefined, qui: string) => parts(c).includes(JSON.stringify({ protagonist: qui }));

/** La sala és d'una sola protagonista (al palau, `protagonist`; a la resta, `jugadora` de veus.json). */
const salaDe = (sala: string) => content.rooms[sala]?.protagonist ?? (content.rooms[sala] ? NOMES[sala] : undefined);

/** On hi ha cada personatge (les sales on es juga que el tenen entre les coses; les cinemàtiques, no). */
const onEs = (pj: string) => Object.entries(content.rooms)
  .filter(([, r]) => pj in (r.hotspots ?? {}) && (r.protagonist || r.protagonists?.length)).map(([id]) => id);

interface Entrada { on: string; llista: InteractionDef[]; i: number; cap: string; salaOn: string[] }

function entrades(): Entrada[] {
  const out: Entrada[] = [];
  for (const [sala, r] of Object.entries(content.rooms)) {
    for (const [h, hs] of Object.entries(r.hotspots ?? {})) {
      const llista = hs.interactions ?? [];
      llista.forEach((x, i) => {
        for (const cap of [x.goTo, x.dialogue]) if (cap && NOMES[cap]) out.push({ on: `${sala}/${h}`, llista, i, cap, salaOn: [sala] });
      });
    }
  }
  for (const [pj, c] of Object.entries(content.characters)) {
    const llista = c.interactions ?? [];
    llista.forEach((x, i) => {
      if (x.dialogue && NOMES[x.dialogue]) out.push({ on: `pj/${pj}`, llista, i, cap: x.dialogue, salaOn: onEs(pj) });
    });
  }
  return out;
}

describe('Aigua Verne: sales i converses d\'una sola', () => {
  it('cada entrada té l\'excusa de l\'altra al davant (o és en una sala que ja és d\'ella)', () => {
    const totes = entrades();
    // Hi són totes: cada sala i conversa de veus.json té almenys una entrada (o és al palau, o és un diàleg que obre
    // el codi del joc).
    for (const cap of Object.keys(NOMES)) {
      if (content.rooms[cap]?.protagonist) continue;
      expect(totes.some((e) => e.cap === cap), `${cap}: no s'hi entra per enlloc?`).toBe(true);
    }
    const errors: string[] = [];
    for (const e of totes) {
      const qui = NOMES[e.cap]!;
      if (e.salaOn.length && e.salaOn.every((s) => salaDe(s) === qui)) continue;
      const x = e.llista[e.i]!;
      if (nomesDe(x.if, qui)) continue;
      // Una interacció que només hi és en una sala d'ella (en Nil al palau, el Magnat a la galeria).
      if (parts(x.if).some((c) => { const s = (JSON.parse(c) as { inRoom?: unknown }).inRoom; return typeof s === 'string' && salaDe(s) === qui; })) continue;
      const propies = parts(x.if);
      for (const v of verbs(x)) {
        const excusa = e.llista.slice(0, e.i).find((y) => !y.item && !y.goTo && !y.dialogue
          && (verbs(y).includes(v) || verbs(y).includes('*'))
          && nomesDe(y.if, altra(qui))
          && parts(y.if).every((p) => p === JSON.stringify({ protagonist: altra(qui) }) || propies.includes(p))
          && (y.lines ?? []).some((l) => l.who === altra(qui) || l.who === 'player'));
        if (!excusa) errors.push(`${e.on} (${v}) → ${e.cap}: ${altra(qui)} hi passa sense excusa`);
      }
    }
    expect(errors).toEqual([]);
  });

  // Les portes, provades: l'altra es queda on és (i ho diu), i la que toca hi passa.
  const PORTES: { qui: string; sala: string; porta: string; cap: string; estat: Effect[] }[] = [
    { qui: 'iri', sala: 'aqua_port', porta: 'cistella', cap: 'aqua_fons', estat: [{ setVar: 'escena', value: 3 }, { setFlag: 'grua_arreglada' }] },
    { qui: 'iri', sala: 'aqua_port', porta: 'cistella', cap: 'aqua_fons', estat: [{ setVar: 'escena', value: 4 }, { setFlag: 'grua_arreglada' }, { setFlag: 'baixada_feta' }, { setFlag: 'lot9' }] },
    { qui: 'iri', sala: 'fosa_forn', porta: 'pas', cap: 'fosa_colada', estat: [{ setVar: 'escena', value: 4 }, { setFlag: 'promesa_lia' }] },
    { qui: 'iri', sala: 'ferrum_carrer', porta: 'porta_sindicat', cap: 'ferrum_sindicat', estat: [{ setVar: 'escena', value: 4 }] },
    { qui: 'iri', sala: 'ferrum_carrer', porta: 'porta_sindicat', cap: 'ferrum_sindicat', estat: [{ setVar: 'escena', value: 6 }, { setFlag: 'rosa_permis' }] },
    { qui: 'vet', sala: 'verdant_jardi', porta: 'porta_cobert', cap: 'verdant_cobert', estat: [{ setVar: 'escena', value: 5 }] },
    { qui: 'vet', sala: 'verdant_jardi', porta: 'porta_cobert', cap: 'verdant_cobert', estat: [{ setVar: 'escena', value: 5 }, { setFlag: 'cal_reg' }, { giveItem: 'reg', who: 'iri' }] },
    { qui: 'iri', sala: 'verdant_jardi', porta: 'porta_residencia', cap: 'verdant_residencia', estat: [{ setVar: 'escena', value: 5 }, { setFlag: 'fidel_admet' }] },
  ];
  for (const c of PORTES) {
    it(`${c.sala}/${c.porta} → ${c.cap}: només ${c.qui} (${JSON.stringify(c.estat.slice(1))})`, () => {
      const { n, p } = partida();
      n.apply(c.estat);
      for (const who of [c.qui, altra(c.qui)]) { amb(p, who); p.goTo(c.sala); }
      const dit = p.do('walkTo', c.porta);
      expect(p.room).toBe(c.sala);
      expect(dit.some((l) => l.who === altra(c.qui) && /\w/.test(l.text))).toBe(true);
      amb(p, c.qui);
      p.do('walkTo', c.porta);
      expect(p.room).toBe(c.cap);
    });
  }

  const CONVERSES: { qui: string; sala: string; cosa: string; verb: string; dialeg: string; estat: Effect[] }[] = [
    { qui: 'iri', sala: 'granja_casa', cosa: 'videotelefon', verb: 'use', dialeg: 'pare', estat: [] },
    { qui: 'iri', sala: 'granja_casa', cosa: 'videotelefon', verb: 'talkTo', dialeg: 'pare', estat: [{ setVar: 'escena', value: 5 }, { setFlag: 'cal_reg' }] },
    { qui: 'iri', sala: 'granja_casa', cosa: 'caixa_forta', verb: 'open', dialeg: 'teclat', estat: [{ setFlag: 'quadre_apartat' }, { setFlag: 'bol_vist' }] },
    { qui: 'iri', sala: 'cantimplora_pont', cosa: 'radio', verb: 'use', dialeg: 'radio_juana', estat: [{ setVar: 'escena', value: 2 }, { setFlag: 'cap_condicions' }] },
    { qui: 'vet', sala: 'verdant_jardi', cosa: 'nil', verb: 'talkTo', dialeg: 'nil', estat: [{ setVar: 'escena', value: 5 }] },
  ];
  for (const c of CONVERSES) {
    it(`${c.sala}/${c.cosa} (${c.verb}) → ${c.dialeg}: només ${c.qui}`, () => {
      const { n, p } = partida();
      n.apply(c.estat);
      for (const who of [c.qui, altra(c.qui)]) { amb(p, who); p.goTo(c.sala); }
      p.deferDialogues = true;
      const dit = p.do(c.verb, c.cosa);
      expect(p.pendingDialogue).toBeNull();
      expect(dit.some((l) => l.who === altra(c.qui))).toBe(true);
      amb(p, c.qui);
      p.do(c.verb, c.cosa);
      expect(p.pendingDialogue).toBe(c.dialeg);
    });
  }

  it('la colada comença amb la Vet al forn i l\'Iri a la colada (i al revés no hi poden ser)', () => {
    const { n, p } = partida();
    n.apply([{ setVar: 'escena', value: 4 }, { setFlag: 'motlle_preparat' }]);
    amb(p, 'iri'); p.goTo('fosa_forn');
    amb(p, 'vet'); p.goTo('fosa_forn');
    p.do('walkTo', 'pas');
    expect(p.room).toBe('fosa_forn');
    expect(n.flag('sync_colada')).toBe(false);
    amb(p, 'iri');
    p.do('walkTo', 'pas');
    expect(p.room).toBe('fosa_colada');
    expect(n.flag('sync_colada')).toBe(true);
  });

  // El que porta l'altra hi ha d'arribar: amb la Mosca (al mateix planeta) o en mà (el que no hi cap).
  const iri = { kind: 'character' as const, id: 'iri' };
  const vet = { kind: 'character' as const, id: 'vet' };
  const textos = (ls: { text: string }[]) => ls.map((l) => l.text).join('\n');

  it('la carta de la Juana, si la porta la Vet: en Bru no escolta l\'Iri, i la Mosca l\'hi porta', () => {
    const { n, p } = partida();
    n.apply([{ setVar: 'escena', value: 4 }, { setVar: 'planeta', value: 'ferrum' }, { setFlag: 'juana_claus' }, { setFlag: 'juana_fet' },
      { giveItem: 'carta_juana', who: 'vet' }]);
    amb(p, 'vet'); p.goTo('ferrum_carrer');
    amb(p, 'iri'); p.goTo('ferrum_sindicat');
    expect(textos(p.do('talkTo', 'bru'))).toMatch(/la porta la Vet/);
    expect(n.flag('bru_set')).toBe(false);
    amb(p, 'vet');
    p.use('carta_juana', item('mosca'));
    amb(p, 'iri');
    p.do('talkTo', 'bru');
    expect(n.flag('bru_set')).toBe(true);
  });

  it('el motlle i la sorra, si els porta la Vet: el motlle, en mà al forn; la sorra, amb la Mosca; i la colada comença', () => {
    const { n, p } = partida();
    n.apply([{ setVar: 'escena', value: 4 }, { setVar: 'planeta', value: 'ferrum' }, { setFlag: 'promesa_lia' }, { setFlag: 'sorra_agafada' },
      { giveItem: 'motlle', who: 'vet' }, { giveItem: 'sorra', who: 'vet' }]);
    amb(p, 'iri'); p.goTo('fosa_forn');
    amb(p, 'vet'); p.goTo('fosa_forn');
    expect(textos(p.use('motlle', item('mosca')))).not.toBe('');
    expect(p.inventory('vet')).toContain('motlle');
    p.do('give', iri, 'motlle');
    expect(p.inventory('iri')).toContain('motlle');
    amb(p, 'iri');
    p.do('walkTo', 'pas');
    expect(p.room).toBe('fosa_colada');
    expect(textos(p.use('motlle', 'llit'))).toMatch(/la porta l'altra/);
    amb(p, 'vet');
    p.use('sorra', item('mosca'));
    amb(p, 'iri');
    p.use('sorra', 'llit');
    expect(n.flag('motlle_preparat')).toBe(true);
    expect(n.flag('sync_colada')).toBe(false);
    // La Vet ja era al forn: en tornar-hi (canviar a ella), hi són totes dues.
    amb(p, 'vet');
    expect(n.flag('sync_colada')).toBe(true);
  });

  it('el reg i la galleda plena, si els porta l\'Iri: el reg, amb la Mosca; la galleda, en mà al jardí', () => {
    const { n, p } = partida();
    n.apply([{ setVar: 'escena', value: 5 }, { setVar: 'planeta', value: 'verdant' }, { setFlag: 'cal_reg' }, { setFlag: 'reg_agafat' },
      { giveItem: 'reg', who: 'iri' }, { giveItem: 'galleda_plena', who: 'iri' }]);
    amb(p, 'iri'); p.goTo('verdant_jardi');
    amb(p, 'vet'); p.goTo('verdant_jardi');
    amb(p, 'iri');
    p.do('give', vet, 'galleda_plena');
    amb(p, 'vet');
    p.do('walkTo', 'porta_cobert');
    expect(p.room).toBe('verdant_cobert');
    amb(p, 'iri');
    p.use('reg', item('mosca'));
    amb(p, 'vet');
    expect(p.inventory('vet')).toEqual(expect.arrayContaining(['reg', 'galleda_plena']));
    p.use('reg', 'tomaquera');
    expect(n.flag('cal_agulla')).toBe(true);
  });
});
