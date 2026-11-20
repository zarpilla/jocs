/**
 * La llibreta de camp: 12 observacions opcionals (la Iri, amb la lupa; la Vet, pel walkie). El camí sencer, recollint-les
 * totes, acaba amb la llibreta plena; sense recollir-ne cap, el final ho diu igualment, i res no queda bloquejat.
 */
import { describe, expect, it } from 'vitest';
import { partida } from './partida.js';
import { acte1, acte2, acte3 } from './cami.js';

const OBS: Record<string, [string, string][]> = {
  vora_bosc: [['lupa', 'bolets'], ['lupa', 'gespa']],
  centraleta: [['lupa', 'fils_paret'], ['lupa', 'corn']],
  campament_fades: [['walkie', 'catapulta'], ['walkie', 'flor']],
  toll_gripaus: [['lupa', 'toll'], ['lupa', 'tap_plastics']],
  caseta_obra: [['walkie', 'maqueta'], ['walkie', 'cartell']],
  zona_mati: [['walkie', 'sensors']],
  zona_zero: [['lupa', 'soques']],
};

describe("L'Última Arrel: la llibreta de camp", () => {
  it('es poden apuntar les 12 observacions, i el final ho diu', () => {
    const { n, p } = partida({ checkHints: true });
    const fetes = new Set<string>();
    const recull = () => {
      const sala = p.room ?? '';
      if (fetes.has(sala)) return;
      fetes.add(sala);
      for (const [eina, cosa] of OBS[sala] ?? []) {
        const abans = n.getVar('observacions');
        const lines = p.use(eina, cosa);
        expect(n.getVar('observacions'), `${eina} → ${cosa}`).toBe(Number(abans) + 1);
        expect(lines.at(-1)?.text).toContain(`${n.getVar('observacions')} observacions de 12`);
        // La segona vegada ja no suma.
        p.use(eina, cosa);
        expect(n.getVar('observacions')).toBe(Number(abans) + 1);
      }
    };
    const jugador = new Proxy(p, {
      get(target, prop, receiver) {
        const value = Reflect.get(target, prop, receiver);
        if (typeof value !== 'function' || !['do', 'use', 'talk'].includes(String(prop))) return value;
        return (...args: unknown[]) => { recull(); return (value as (...a: unknown[]) => unknown).apply(target, args); };
      },
    });
    acte1(jugador, n);
    acte2(jugador, n);
    acte3(jugador, n);
    expect(n.getVar('observacions')).toBe(12);
    const final = n.ending('taula').scene.map((l) => l.key);
    expect(final).toContain('final.taula.llibreta.plena');
    expect(final).not.toContain('final.taula.llibreta');
  });

  it('sense cap observació, el final diu que en queden', () => {
    const { n, p } = partida();
    acte1(p, n);
    acte2(p, n);
    acte3(p, n);
    expect(n.getVar('observacions')).toBe(0);
    const final = n.ending('taula').scene;
    expect(final.map((l) => l.key)).toContain('final.taula.llibreta');
    expect(final.find((l) => l.key === 'final.taula.llibreta')?.text).toContain('0 observacions de 12');
  });

  it("la sorpresa de l'àvia parla de l'avi", () => {
    const { n, p } = partida();
    const dites: string[] = [];
    const jugador = new Proxy(p, {
      get(target, prop, receiver) {
        const value = Reflect.get(target, prop, receiver);
        if (typeof value !== 'function' || !['do', 'use', 'talk'].includes(String(prop))) return value;
        return (...args: unknown[]) => {
          const lines = (value as (...a: unknown[]) => { key: string }[]).apply(target, args);
          dites.push(...lines.map((l) => l.key));
          return lines;
        };
      },
    });
    acte1(jugador, n);
    acte2(jugador, n);
    acte3(jugador, n);
    const i = dites.indexOf('sala.bosc_obert.secret.4');
    expect(i).toBeGreaterThan(-1);
    expect(dites.slice(i + 1, i + 7)).toEqual([1, 2, 3, 4, 5, 6].map((k) => `sala.bosc_obert.avi.${k}`));
  });
});
