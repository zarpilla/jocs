/**
 * Aigua Verne, sense barra de verbs: el joc sencer (els dos camins de cami.ts) jugat amb la interfície tàctil.
 * Què es compta: adapters/benne/tactil/mesura.ts. Si alguna interacció del camí no es pot fer de cap manera, falla. Amb el dit (el primer toc mira) i amb
 * el ratolí (el clic dret mira). Amb TACTIL=1 escriu
 * el recompte i la llista dels passos que no són un toc.
 */
import { describe, expect, it } from 'vitest';
import type { Narrative } from '@aventura/narrative-core';
import { partida } from './partida.js';
import { acte1, acte2, acte3 } from './cami.js';
import { mesura } from '../../../../adapters/benne/tactil/mesura.js';

describe('Aigua Verne: el camí, sense barra de verbs', () => {
  for (const mode of ['dit', 'ratoli'] as const) for (const barril of [true, false]) {
    it(`${barril ? "amb l'últim barril" : 'amb el condensador'} (${mode})`, () => {
      const { n, p } = partida();
      const m = mesura(n as Narrative, mode);
      const jugador = m.jugador(p);
      acte1(jugador, n as Narrative);
      acte2(jugador, n as Narrative, barril);
      acte3(jugador, n as Narrative);
      expect(n.getVar('lots')).toBeGreaterThan(0);
      if (process.env.TACTIL) console.log(m.resum(barril ? 'barril' : 'condensador'));
      expect(m.impossibles).toEqual([]);
      expect(m.passos.filter((x) => x.com === 'toc').length).toBeGreaterThan(0);
    });
  }
});
