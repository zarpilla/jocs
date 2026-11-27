/**
 * El motor dona el clic a la cosa de zIndex més alt (i, amb el mateix, al punt abans que al prop). Un punt que tapa
 * del tot el collider d'un prop clicable el deixa sense clic (a La Conjura de l'Avet, el forat tapava la cera i la
 * partida no es podia acabar), i un que en tapa el mig fa que el cercle del botó de punts doni el punt (el rètol de
 * l'epíleg). Aquest test mira totes les sales de tots els jocs.
 */
import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import { describe, expect, it } from 'vitest';
import { coveredProps, puntsSobreCapes } from '../benne-content';

const GAMES = join(__dirname, '../../../games');
const rect = (x0: number, y0: number, x1: number, y1: number) =>
  [{ x: x0, y: y0 }, { x: x1, y: y0 }, { x: x1, y: y1 }, { x: x0, y: y1 }];

// Pendents, amb la tasca que les arregla.
const PENDENTS: Record<string, string> = {};

describe('props clicables tapats per un punt', () => {
  it('detecta un prop tapat', () => {
    const room = {
      hotspots: [{ id: 'forat', zIndex: 8, points: rect(0, 0, 100, 50) }],
      props: [
        { id: 'cera', zIndex: 3, clickable: true, collider: { points: rect(10, 10, 20, 20) } },
        { id: 'bo', zIndex: 9, clickable: true, collider: { points: rect(10, 10, 20, 20) } },
      ],
    };
    expect(coveredProps(room)).toHaveLength(1);
    expect(coveredProps(room)[0]).toContain('cera');
  });

  it('detecta un prop tapat pel mig (on va el cercle dels punts)', () => {
    const room = {
      hotspots: [{ id: 'forat', zIndex: 4, points: [{ x: 0, y: 20 }, { x: 100, y: 20 }, { x: 100, y: 50 }, { x: 0, y: 50 }] }],
      props: [
        // Mig (15, 18): a 2 px del forat, dins del marge del cercle.
        { id: 'rotul', zIndex: 3, clickable: true, collider: { points: [{ x: 10, y: 10 }, { x: 20, y: 10 }, { x: 20, y: 26 }, { x: 10, y: 26 }] } },
        // Mig (15, 5): lluny del forat.
        { id: 'lliure', zIndex: 3, clickable: true, collider: { points: [{ x: 10, y: 0 }, { x: 20, y: 0 }, { x: 20, y: 10 }, { x: 10, y: 10 }] } },
      ],
    };
    expect(coveredProps(room)).toHaveLength(1);
    expect(coveredProps(room)[0]).toContain('rotul');
  });

  for (const joc of readdirSync(GAMES)) {
    const rooms = join(GAMES, joc, joc, 'src/game/rooms');
    if (!existsSync(rooms)) continue;
    for (const id of readdirSync(rooms)) {
      const path = join(rooms, id, `${id}.room.json`);
      if (!existsSync(path) || PENDENTS[`${joc}/${id}`]) continue;
      it(`${joc}/${id}`, () => {
        expect(coveredProps(JSON.parse(readFileSync(path, 'utf8')))).toEqual([]);
      });
    }
  }
});

describe('punts per sobre dels personatges en una sala amb capes del davant (tasca 280)', () => {
  const punts = [{ id: 'baix', zIndex: 9 }, { id: 'alt', zIndex: 10 }];
  it('avisa dels punts de zIndex 10 o més si hi ha capes del davant', () => {
    const w = puntsSobreCapes({ hotspots: punts, props: [{ id: 'davant', zIndex: 20, baseline: 200 }] });
    expect(w).toHaveLength(1);
    expect(w[0]).toContain('alt');
  });
  it('no en diu res sense capes del davant', () => {
    expect(puntsSobreCapes({ hotspots: punts, props: [{ id: 'BG', zIndex: 0 }] })).toEqual([]);
  });
});
