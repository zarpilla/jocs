/**
 * Aigua Verne B, sense barra de verbs: el joc sencer (els dos camins de cami.ts) jugat amb la interfície tàctil.
 *
 * A cada `do` i `use` del camí es mira què hauria fet el jugador sense barra:
 *  - toc: tocar la cosa (o tocar-la amb l'objecte a la mà) fa exactament la mateixa interacció;
 *  - menú: cal mantenir premut i triar al menú d'accions (hi ha de ser);
 *  - mirar: és un «mira» d'una cosa que té altres accions (tocar-la faria l'acció): «Mira» és al menú.
 * Si alguna interacció del camí no es pot fer de cap manera, falla. Amb TACTIL=1 escriu el recompte i la llista.
 */
import { describe, expect, it } from 'vitest';
import type { InteractionTarget, Narrative } from '@aventura/narrative-core';
import { partida } from './partida.js';
import { acte1, acte2, acte3 } from './cami.js';
import { accions, verbAmbObjecte, verbDelToc } from '../../adapters/benne/runtime/accions.js';

type Com = 'toc' | 'menú' | 'mirar';

describe('Aigua Verne B: el camí, sense barra de verbs', () => {
  for (const barril of [true, false]) {
    it(barril ? "amb l'últim barril" : 'amb el condensador', () => {
      const { n, p } = partida();
      const passos: { com: Com; on: string }[] = [];
      const kind = (id: string): InteractionTarget['kind'] => (n.content.characters[id] ? 'character' : 'hotspot');
      const target = (t: string | InteractionTarget): InteractionTarget => (typeof t === 'string' ? { kind: kind(t), id: t } : t);

      const mira = (verb: string, t: InteractionTarget, item?: string) => {
        const room = p.room ?? undefined;
        const on = `${room}: ${verb} ${t.id}${item ? ` amb ${item}` : ''}`;
        const volgut = n.peek({ verb, target: t, item });
        if (!volgut) return; // el camí fa una cosa que no fa res (la frase per defecte): no compta
        if (item) {
          const amb = verbAmbObjecte(n, t, item);
          expect(n.peek({ verb: amb, target: t, item }), `amb l'objecte a la mà no es pot: ${on}`).toBe(volgut);
          passos.push({ com: 'toc', on });
          return;
        }
        if (verb === 'look') {
          // Si la cosa no té cap altra acció, tocar-la ja la mira; si no, «Mira» és al menú.
          passos.push({ com: verbDelToc(n, t) === 'look' ? 'toc' : 'mirar', on });
          return;
        }
        if (n.peek({ verb: verbDelToc(n, t), target: t }) === volgut) {
          passos.push({ com: 'toc', on });
          return;
        }
        const menu = accions(n, t).map((a) => n.peek({ verb: a.verb, target: t }));
        expect(menu, `no és al menú d'accions: ${on}`).toContain(volgut);
        passos.push({ com: 'menú', on });
      };

      const jugador = new Proxy(p, {
        get(obj, prop, receiver) {
          const value = Reflect.get(obj, prop, receiver);
          if (prop === 'do') return (verb: string, t: string | InteractionTarget, item?: string) => {
            mira(verb, target(t), item);
            return value.call(obj, verb, t, item);
          };
          if (prop === 'use') return (item: string, t: string | InteractionTarget) => {
            mira('use', target(t), item);
            return value.call(obj, item, t);
          };
          return typeof value === 'function' ? value.bind(obj) : value;
        },
      });

      acte1(jugador, n as Narrative);
      acte2(jugador, n as Narrative, barril);
      acte3(jugador, n as Narrative);
      expect(n.getVar('lots')).toBeGreaterThan(0);

      const compte = (c: Com) => passos.filter((x) => x.com === c).length;
      if (process.env.TACTIL) {
        console.log(`${barril ? 'barril' : 'condensador'}: ${passos.length} passos; toc ${compte('toc')}, menú ${compte('menú')}, mirar ${compte('mirar')}`);
        for (const x of passos.filter((x) => x.com !== 'toc')) console.log(`  ${x.com}: ${x.on}`);
      }
      expect(compte('toc')).toBeGreaterThan(0);
    });
  }
});
