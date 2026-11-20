/**
 * El joc sencer, de cap a peus, per tots els camins: l'Escena 4 amb l'últim barril o amb el condensador (la targeta
 * de la Mosca), en Fidel amb el quart sac o amb el tractor de l'avi, i la partida «previsora», que agafa a la segona
 * el que no es vol agafar la primera vegada (el reg, el quart sac, la sorra, el vestit) i no ha de tornar a buscar-ho.
 * A cada pas hi ha d'haver una pista disponible.
 */
import { describe, expect, it } from 'vitest';
import { partida } from './partida.js';
import { acte1, acte2, acte3, type Cami } from './cami.js';

const CAMINS: [string, Cami][] = [
  ["amb l'últim barril i el quart sac", { barril: true }],
  ['amb el condensador i el tractor', { barril: false, tractor: true }],
  ['previsora (sense tornar enrere), amb el condensador', { barril: false, previsora: true }],
];

describe('Aigua Verne, de cap a peus', () => {
  for (const [nom, cami] of CAMINS) {
    it(nom, async () => {
      const { n, p } = partida({ checkHints: true });
      try {
        acte1(p, n, cami);
        acte2(p, n, cami.barril ?? true, cami);
        acte3(p, n);
      } catch (e) {
        console.log(p.transcript.slice(-25).join('\n'));
        throw e;
      }
      expect(n.getVar('lots')).toBeGreaterThan(0);
      if (cami.previsora) {
        // No ha calgut tornar: ni el lot 9 d'Aqua, ni el precinte del graner, ni el favor de la Rosa.
        expect([n.flag('lot9_vist'), n.flag('precinte_vist'), n.flag('rosa_vol_tomas')]).toEqual([false, false, false]);
      }
      const nomFitxer = nom.split(' ')[0] === 'previsora' ? 'previsora' : cami.barril ? 'barril' : 'condensador';
      if (process.env.TRANSCRIPCIO) (await import('node:fs')).writeFileSync(`${process.env.TRANSCRIPCIO}-${nomFitxer}.txt`, p.transcript.join('\n'));
    });
  }
});
