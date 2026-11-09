/**
 * Ferro-9, Acte 3 («La finestra»), jugat sense gràfics.
 */
import { describe, expect, it } from 'vitest';
import { estatFinestra } from '../logic/index.js';
import { jugarActe1, jugarActe2, keys, partida, texts } from './partida.js';

const item = (id: string) => ({ kind: 'item' as const, id });

describe('Ferro-9 · Acte 3 · Acorralades', () => {
  it("la Directora pren la cel·la, el Brau vigila la cambra i la Vet troba una ruta a la Sala de la Memòria (sempre amb alguna pista)", () => {
    const { p, n } = partida({ checkHints: true, fins: 'fugida_completada' });
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

    // ── Vet: el conducte comença a la seva cel·la, però la reixa és soldada pel rovell ──
    p.do('open', 'porta_passadis');
    p.do('open', 'porta_cella');
    expect(p.room).toBe('gavina_cella');
    expect(texts(p.use('llapis_ulls', item('fullet_memoria')))).toContain('on, exactament');
    expect(texts(p.do('look', 'reixa'))).toContain('Comença aquí');
    expect(texts(p.do('open', 'reixa'))).toContain('Soldada');
    p.use('llapis_ulls', item('fullet_memoria'));
    expect(p.inventory()).toContain('mapa_fuga');
    expect(texts(p.do('look', item('mapa_fuga')))).toContain("d'aquí a cent vint anys");

    // ── Vet: fa veure que accepta el pacte, però a l'altra banda no hi ha ningú ──
    expect(texts(p.use('mapa_fuga', 'panell'))).toContain('Ara és meu');
    p.talk('directora', 'pacte');
    expect(n.flag('pacte_acceptat')).toBe(true);
    expect(texts(p.use('mapa_fuga', 'panell'))).toContain('no vibra');

    // ── Iri: enganya el Brau i torna a la cambra ──
    p.switchTo('iri');
    expect(p.room).toBe('fabrica_calderes');
    p.talk('brau', 'enganyar');
    expect(n.flag('brau_distret')).toBe(true);
    expect(n.isHotspotVisible('fabrica_calderes', 'brau')).toBe(false);
    expect(texts(p.do('open', 'porta_cambra'))).toContain('molts racons');
    expect(p.room).toBe('fabrica_cambra');
    expect(texts(p.use('llima', 'reixa'))).toContain('formulari');

    // ── Vet: envia el mapa, i la Directora fa tancar la cel·la ──
    p.switchTo('vet');
    const enceses = estatFinestra(n).enceses;
    const envia = texts(p.use('mapa_fuga', 'panell'));
    expect(envia).toContain('reformat');
    expect(envia).toContain('tanca la cel·la');
    expect(estatFinestra(n).enceses).toBe(enceses - 1);
    expect(p.active).toBe('iri');
    expect(n.state.quests.acte3!.objectives.mapa).toBe(true);

    // ── Iri: llegeix la postdata i deixa la reixa a punt per a d'aquí a cent vint anys ──
    expect(texts(p.do('look', item('mapa_fuga')))).toContain('llimo');
    expect(texts(p.use('llima', 'reixa'))).toContain('meva marca');
    expect(n.flag('reixa_preparada')).toBe(true);
    expect(n.state.quests.acte3!.objectives.reixa).toBe(true);

    // ── Vet: reajust. La porta és tancada, però la reixa s'obre i el conducte porta a l'hangar ──
    expect(texts(p.switchTo('vet'))).toContain('reajust');
    expect(texts(p.do('open', 'porta'))).toContain('MARE');
    expect(p.room).toBe('gavina_cella');
    expect(texts(p.do('open', 'reixa'))).toContain('pilar 7');
    expect(n.flag('reixa_oberta')).toBe(true);
    p.do('open', 'reixa');
    expect(p.room).toBe('gavina_hangar');
    expect(texts(p.do('open', 'porta_passadis'))).toBeDefined();
    expect(texts(p.do('open', 'porta_cella'))).toContain('conducte');
    p.do('open', 'porta_hangar');
    p.do('open', 'sortida_conducte');
    expect(p.room).toBe('gavina_cella');

    // ── Iri: un tub de ferro-9 (el Cargol no demana formularis als fugitius) i la llibreta a dins ──
    p.switchTo('iri');
    expect(texts(p.use('llapis', 'cambra'))).toContain('no li fa cap falta');
    p.goTo('fabrica_calderes');
    p.goTo('fabrica_magatzem');
    expect(texts(p.talk('cargol', 'tub'))).toContain('fugitius');
    p.goTo('fabrica_calderes');
    p.goTo('fabrica_cambra');
    expect(texts(p.use('tub_ferro9', 'cambra'))).toContain('llibreta');
    p.use('llibreta_torn', item('tub_ferro9'));
    expect(p.inventory()).toContain('tub_amb_llibreta');
    expect(keys(p.use('tub_amb_llibreta', 'cambra'))).toContain('finestra.enviat');
    expect(estatFinestra(n).enceses).toBe(enceses - 2);

    // ── Vet: la Directora el vol; fuig per la reixa, munta el tub i marxa ──
    expect(p.active).toBe('vet');
    expect(texts(p.switchTo('vet'))).toBeDefined();
    expect(texts(p.do('open', 'reixa'))).toContain('Atureu-la');
    expect(p.room).toBe('gavina_hangar');
    expect(texts(p.do('push', 'llancadora'))).toContain('Sense el tub');
    expect(texts(p.use('tub_amb_llibreta', 'llancadora'))).toContain('proves');
    expect(p.inventory()).toContain('llibreta_torn');
    expect(texts(p.do('push', 'llancadora'))).toContain('Ara et toca a tu');
    expect(p.active).toBe('iri');

    // ── Iri: segueix les seves fletxes fins al moll i fuig amb la llançadora nova ──
    p.do('open', 'reixa');
    expect(p.room).toBe('fabrica_moll');
    expect(texts(p.do('use', 'llancadora'))).toContain('Desapareguda');
    expect(n.flag('fugida_completada')).toBe(true);
    expect(n.state.quests.acte3!.objectives.fugida).toBe(true);
    expect(n.resolveEnding()).toBe('fugida');
  });

  it("només s'envia el que l'altra necessita, i en el sentit que toca", () => {
    const { p, n } = partida({ fins: 'acte2_acabat' });
    jugarActe1(p);
    p.switchTo('iri');
    const enceses = estatFinestra(n).enceses;
    n.apply({ giveItem: 'nota_vet', who: 'iri' });
    expect(keys(p.use('nota_vet', 'cambra'))).toEqual(['finestra.rebuig.no_cal_iri']);
    expect(estatFinestra(n).enceses).toBe(enceses);
  });
});
