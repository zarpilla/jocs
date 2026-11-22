/** Regressions de la revisió externa: l'auricular no gasta torn, la porta amb l'Iri fora, el comandament d'en Tomàs. */
import { describe, expect, it } from 'vitest';
import { partida } from './partida.js';

describe('Revisió', () => {
  it('usar l\'auricular a la sincronia del mòbil no gasta torn (com parlar-hi)', () => {
    const { n, p, world } = partida();
    p.goTo('bcmu_despatx');
    n.apply([{ setFlag: 'sync_mobil' }, { setVar: 'torns_mobil', value: 8 }, { setFlag: 'auricular_compartit' }, { giveItem: 'auricular_boto', who: world.active }]);
    p.do('use', { kind: 'item', id: 'auricular_boto' });
    expect(n.getVar('torns_mobil')).toBe(8);
  });

  it('la porta de personal, amb l\'Iri ja fora, no diu que cal el codi', () => {
    const { n, p } = partida();
    p.goTo('aeroport_personal');
    n.apply([{ setFlag: 'porta_oberta' }, { setFlag: 'iri_fora' }]);
    const text = p.do('use', 'porta').map((l) => l.text).join(' ');
    expect(text).not.toMatch(/Cal el codi/);
  });
});
