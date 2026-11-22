/**
 * La Conjura de l'Avet, sense barra de verbs: el camí sencer (cami.ts) jugat amb la interfície tàctil
 * (adapters/benne/tactil), amb el dit (el primer toc mira) i amb el ratolí. Si alguna interacció del camí no es pot
 * fer de cap manera, falla. Amb TACTIL=1 escriu el recompte i la llista dels passos que no són un toc.
 */
import { describe, expect, it } from 'vitest';
import type { Narrative } from '@aventura/narrative-core';
import { partida } from './partida.js';
import { acte1, acte2, acte3, acte4 } from './cami.js';
import { mesura } from '../../../../adapters/benne/tactil/mesura.js';

describe("La Conjura de l'Avet: el camí, sense barra de verbs", () => {
  for (const mode of ['dit', 'ratoli'] as const) {
    it(`es pot jugar sencer (${mode})`, () => {
      const { n, p } = partida();
      const m = mesura(n as Narrative, mode);
      const j = m.jugador(p);
      acte1(j, n as Narrative);
      acte2(j, n as Narrative);
      acte3(j, n as Narrative);
      acte4(j, n as Narrative);
      if (process.env.TACTIL) console.log(m.resum(mode));
      expect(m.impossibles).toEqual([]);
    });
  }
});
