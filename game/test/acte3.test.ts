/**
 * Ferro-9, Acte 3 («La finestra»), jugat sense gràfics.
 */
import { describe, expect, it } from 'vitest';
import { jugarActe1, jugarActe2, partida, texts } from './partida.js';

describe('Ferro-9 · Acte 3 · Acorralades', () => {
  it("la Directora pren la cel·la, el Brau vigila la cambra i la Vet troba una ruta a la Sala de la Memòria (sempre amb alguna pista)", () => {
    const { p, n } = partida({ checkHints: true, fins: 'fullet_memoria_agafat' });
    jugarActe1(p);
    // A l'Acte 2, la Sala de la Memòria encara és tancada.
    expect(texts(p.do('open', 'porta_memoria'))).toContain('dimarts');
    jugarActe2(p);
    expect(n.flag('acte2_acabat')).toBe(true);
    expect(n.flag('acte3_iniciat')).toBe(true);
    expect(n.state.quests.acte3!.status).toBe('active');

    // ── Vet: la Directora, a la cel·la ──
    expect(p.room).toBe('gavina_cella');
    expect(n.isHotspotVisible('gavina_cella', 'directora')).toBe(true);
    expect(texts(p.do('push', 'panell'))).toContain('Ara és meu');
    expect(texts(p.talk('directora', 'que_vol', 'iri'))).toContain('besavi');

    // ── Iri: descoberta ──
    const descoberta = texts(p.switchTo('iri'));
    expect(descoberta).toContain('Sé què ha fet amb la meva cambra');
    expect(descoberta).toContain('fora de la cambra');
    expect(p.room).toBe('fabrica_calderes');
    expect(n.isHotspotVisible('fabrica_calderes', 'brau')).toBe(true);
    expect(texts(p.do('open', 'porta_cambra'))).toContain('Ni un pas');
    expect(texts(p.talk('brau', 'que_passa'))).toContain('zing');

    // ── Vet: la Sala de la Memòria ──
    p.switchTo('vet');
    p.do('open', 'porta');
    p.do('open', 'porta_memoria');
    expect(p.room).toBe('gavina_memoria');
    expect(texts(p.do('look', 'foto'))).toContain('desapareguda');
    expect(texts(p.do('look', 'vitrina'))).toContain('Lot 1');
    expect(texts(p.do('look', 'mapa'))).toContain('Conducte de servei');
    p.do('pickUp', 'fullets');
    expect(p.inventory()).toContain('fullet_memoria');
    expect(n.state.quests.acte3!.objectives.memoria).toBe(true);
    expect(n.state.quests.acte3!.objectives.ruta).toBe(true);
  });
});
