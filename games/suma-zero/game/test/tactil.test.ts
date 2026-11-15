/**
 * Suma Zero, sense barra de verbs: el joc sencer (per dos camins de partida.ts) jugat amb la interfície tàctil.
 * Què es compta: adapters/benne/tactil/mesura.ts. Si alguna interacció del camí no es pot fer de cap manera, falla.
 * Amb TACTIL=1 escriu el recompte i la llista dels passos que no són un toc.
 */
import { describe, expect, it } from 'vitest';
import { jugarActe1, jugarActe2, jugarActe3, partida, type Jugador } from './partida.js';
import { mesura } from '../../../../adapters/benne/tactil/mesura.js';

const camins: { nom: string; jugar: (p: Jugador) => void }[] = [
  {
    nom: 'sense aliats',
    jugar: (p) => {
      jugarActe1(p, { entrepa: true, sacrifici: 'pizza' });
      jugarActe2(p);
      jugarActe3(p);
    },
  },
  {
    nom: 'amb tots els aliats',
    jugar: (p) => {
      jugarActe1(p, { entrepa: true, tap: true, preparacio: true });
      jugarActe2(p, { aliats: true });
      jugarActe3(p, { pons: true, mobil: 'pons', repartir: true, neta: true });
    },
  },
];

describe('Suma Zero: el camí, sense barra de verbs', () => {
  for (const cami of camins) {
    it(cami.nom, () => {
      const { n, p } = partida();
      const m = mesura(n);
      cami.jugar(m.jugador(p));
      expect(n.resolveEnding()).not.toBeNull();
      if (process.env.TACTIL) console.log(m.resum(cami.nom));
      expect(m.impossibles).toEqual([]);
      expect(m.passos.filter((x) => x.com === 'toc').length).toBeGreaterThan(0);
    });
  }
});
