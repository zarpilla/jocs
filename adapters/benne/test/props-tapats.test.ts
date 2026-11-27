/**
 * El motor dona el clic a la cosa de zIndex més alt (i, amb el mateix, al punt abans que al prop). Un punt que tapa
 * del tot el collider d'un prop clicable el deixa sense clic: a La Conjura de l'Avet, el forat tapava la cera i la
 * partida no es podia acabar. Aquest test mira totes les sales de tots els jocs.
 */
import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import { describe, expect, it } from 'vitest';
import { coveredProps } from '../benne-content';

const GAMES = join(__dirname, '../../../games');

// Pendents, amb la tasca que les arregla.
const PENDENTS: Record<string, string> = {
  'ni-un-ou/pont': 'tasca 168',
};

describe('props clicables tapats per un punt', () => {
  it('detecta un prop tapat', () => {
    const room = {
      hotspots: [{ id: 'forat', zIndex: 8, points: [{ x: 0, y: 0 }, { x: 100, y: 50 }] }],
      props: [
        { id: 'cera', zIndex: 3, clickable: true, collider: { points: [{ x: 10, y: 10 }, { x: 20, y: 20 }] } },
        { id: 'bo', zIndex: 9, clickable: true, collider: { points: [{ x: 10, y: 10 }, { x: 20, y: 20 }] } },
      ],
    };
    expect(coveredProps(room)).toHaveLength(1);
    expect(coveredProps(room)[0]).toContain('cera');
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
