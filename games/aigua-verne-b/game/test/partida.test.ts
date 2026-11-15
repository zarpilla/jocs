/**
 * El joc sencer, de cap a peus, pels dos camins de l'Escena 4 (l'últim barril o el condensador), i amb una pista
 * disponible a cada pas.
 */
import { describe, expect, it } from 'vitest';
import { partida } from './partida.js';
import { acte1, acte2, acte3 } from './cami.js';

describe('Aigua Verne, de cap a peus', () => {
  for (const barril of [true, false]) {
    it(barril ? "amb l'últim barril" : 'amb el condensador', async () => {
      const { n, p } = partida({ checkHints: true });
      try {
        acte1(p, n);
        acte2(p, n, barril);
        acte3(p, n);
      } catch (e) {
        console.log(p.transcript.slice(-25).join('\n'));
        throw e;
      }
      expect(n.getVar('lots')).toBeGreaterThan(0);
      if (process.env.TRANSCRIPCIO) (await import('node:fs')).writeFileSync(`${process.env.TRANSCRIPCIO}-${barril ? 'barril' : 'condensador'}.txt`, p.transcript.join('\n'));
    });
  }
});
