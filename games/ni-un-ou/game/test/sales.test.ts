/**
 * Cada sala és d'una sola protagonista (guio.md, «Regles del món · 9»): així cada línia es grava amb una sola veu.
 * L'altra no hi entra caminant: les portes la paren amb una excusa, i el plànol (que és caminar) tampoc no l'hi porta.
 *
 * Es comprova jugant: després de cada acció de cada partida, per a cada protagonista (la que juga i l'altra), les sales
 * on podria arribar ara per les portes (`accessibles`, el mateix càlcul que el plànol) i la sala on és. No es fa servir
 * `HeadlessPlayer.goTo`, que teletransporta: només les portes.
 */
import { describe, expect, it } from 'vitest';
import type { Narrative } from '@aventura/narrative-core';
import { accessibles } from '../logic/mapa.js';
import { amb, escena1, escena2, escena3, escena4, escena5, escena6, escena7, escena8, jugarTot, partida } from './partida.js';

type Qui = 'iri' | 'vet';

/** Les sales de cada protagonista: l'altra no hi entra mai. */
const NOMES: Record<Qui, string[]> = {
  iri: ['pont', 'sala_radio', 'pal', 'camarot_iri', 'passadis_baix', 'sala_maquines', 'taller', 'rebost', 'diposit2', 'pallol', 'sala_bombes'],
  vet: ['infermeria', 'cuina', 'menjador', 'coberta_popa', 'cabina_capitana'],
};

/** Sales on no pot ser `qui` ara mateix. */
function vedades(n: Narrative, qui: Qui) {
  const altra: Qui = qui === 'iri' ? 'vet' : 'iri';
  const out = new Set(NOMES[altra]);
  const escena = Number(n.getVar('escena'));
  // A l'Escena 6, la proa (i la caixa de cadenes, fins que l'Iri talla el cadenat) és de l'Iri.
  if (qui === 'vet' && escena === 6) out.add('coberta_proa');
  return out;
}

/** Excepcions de guió: on hi posa una escena (`situar`), i d'on no es pot moure. */
function excepcio(n: Narrative, qui: Qui, sala: string) {
  const escena = Number(n.getVar('escena'));
  if (qui === 'vet' && sala === 'sala_maquines' && escena === 9) return true; // amb en Bastida i el relé
  if (qui === 'iri' && sala === 'menjador' && escena === 8 && n.flag('reunio_comencada')) return true; // la reunió
  if (qui === 'vet' && sala === 'caixa_cadenes' && escena === 6) return true; // arriba corrents quan l'Iri talla
  return false;
}

function comprova(r: ReturnType<typeof partida>, on: string) {
  const { n, world } = r;
  const actiu = world.active as Qui;
  for (const qui of ['iri', 'vet'] as Qui[]) {
    if (qui !== actiu) { world.switchTo(qui); n.worldChanged(); }
    try {
      const sala = world.room;
      if (!sala) continue;
      const no = vedades(n, qui);
      const ok = excepcio(n, qui, sala);
      expect(ok || !no.has(sala), `${qui} és a ${sala} (escena ${n.getVar('escena')}) després de ${on}`).toBe(true);
      const pot = [...accessibles(n)].filter((s) => s !== sala);
      const dolentes = pot.filter((s) => no.has(s) && !excepcio(n, qui, s));
      expect(dolentes, `${qui}, des de ${sala} (escena ${n.getVar('escena')}), arriba caminant a ${dolentes} després de ${on}`).toEqual([]);
      // La Vet, a màquines a l'Escena 9, no en surt: ni cap al passadís ni cap al taller o el rebost, que són de l'Iri.
      if (qui === 'vet' && sala === 'sala_maquines') expect(pot, `la Vet surt de màquines després de ${on}`).toEqual([]);
    } finally {
      if (qui !== actiu) { world.switchTo(actiu); n.worldChanged(); }
    }
  }
}

/** Una partida que, després de cada acció, comprova on pot anar cadascuna. */
function vigilada() {
  const r = partida({ checkHints: true });
  let comptades = 0;
  const p = new Proxy(r.p, {
    get(t, prop, rec) {
      const v = Reflect.get(t, prop, rec);
      if (typeof v !== 'function' || !['do', 'use', 'talk', 'switchTo'].includes(String(prop))) return v;
      return (...a: unknown[]) => {
        const res = (v as (...x: unknown[]) => unknown).apply(t, a);
        comptades++;
        comprova(r, `${String(prop)}(${JSON.stringify(a)})`);
        return res;
      };
    },
  });
  comprova(r, 'el començament');
  return { ...r, p, comptades: () => comptades };
}

describe("Cada sala, d'una sola protagonista", () => {
  for (const [nom, o] of [
    ['amb tots els aliats', {}],
    ['sense aliats', { aliats: false }],
    ['amb les frontisses', { frontisses: true }],
    ['amb la Nadia aliada', { nadia: true }],
  ] as const) {
    it(`partida sencera ${nom}: ningú no entra on no li toca`, () => {
      const r = vigilada();
      jugarTot(r.p, o);
      expect(r.n.flag('enviat')).toBe(true);
      expect(r.comptades()).toBeGreaterThan(100);
    });
  }

  it("les excuses: cada porta tancada diu per què", () => {
    const { p } = partida();
    escena1(p); escena2(p); escena3(p); escena4(p); escena5(p);
    // Escena 6
    amb(p, 'vet', 'passadis');
    const diu = (porta: string) => p.do('use', porta).map((l) => l.key);
    expect(diu('escala_amunt')).toEqual(['sala.passadis.escala_amunt.8']);
    expect(diu('escala_avall')).toEqual(['sala.passadis.escala_avall.2']);
    expect(diu('porta_proa')).toEqual(['sala.passadis.porta_proa.3']);
    expect(p.room).toBe('passadis');
    amb(p, 'iri', 'passadis');
    expect(diu('porta_infermeria')).toEqual(['sala.passadis.porta_infermeria.6']);
    expect(diu('porta_menjador')).toEqual(['sala.passadis.porta_menjador.5']);
    expect(diu('porta_capitana')).toEqual(['sala.passadis.porta_capitana.6']);
    expect(p.room).toBe('passadis');
    p.do('use', 'porta_proa');
    expect(p.room).toBe('coberta_proa');
    expect(diu('popa')).toEqual(['sala.coberta_proa.popa.3']);
    expect(p.room).toBe('coberta_proa');
  });

  it("Escena 9: la Vet no surt de màquines, ni abans ni després del relé", () => {
    const { n, p } = partida();
    escena1(p); escena2(p); escena3(p); escena4(p); escena5(p); escena6(p); escena7(p); escena8(p);
    amb(p, 'vet');
    expect(p.room).toBe('sala_maquines');
    for (const porta of ['porta_passadis', 'porta_taller', 'porta_rebost']) {
      expect(p.do('use', porta).map((l) => l.key)).toEqual(['sala.sala_maquines.porta_passadis.2']);
    }
    p.talk('bastida', 'veritat', 'diners'); // amb la Capitana aliada, el dubte comença a 4
    expect(n.flag('rele_posat')).toBe(true);
    for (const porta of ['porta_passadis', 'porta_taller', 'porta_rebost']) {
      expect(p.do('use', porta).map((l) => l.key)).toEqual(['sala.sala_maquines.porta_passadis.4']);
    }
    expect(p.room).toBe('sala_maquines');
    escena9Iri(p);
    expect(n.flag('enviat')).toBe(true);
  });
});

/** El final de l'Escena 9, amb el relé ja posat: l'Iri al pal i al terminal. */
function escena9Iri(p: ReturnType<typeof partida>['p']) {
  amb(p, 'iri', 'pal');
  while (!p.narrative.flag('antena_ok')) p.do('use', 'antena');
  amb(p, 'iri', 'pont');
  while (!p.narrative.flag('enviat')) p.do('use', 'terminal');
}

