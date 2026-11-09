/**
 * Ferro-9, Acte 3 («La finestra»), jugat sense gràfics.
 */
import { describe, expect, it } from 'vitest';
import { estatFinestra } from '../logic/index.js';
import { jugarActe1, jugarActe2, jugarActe3, keys, partida, texts } from './partida.js';

const item = (id: string) => ({ kind: 'item' as const, id });

describe('Ferro-9 · Acte 3 · Acorralades', () => {
  it("la Directora pren la cel·la, el Sic vigila la cambra i la Vet troba una ruta a la Sala de la Memòria (sempre amb alguna pista)", () => {
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
    expect(n.isHotspotVisible('fabrica_calderes', 'sic')).toBe(true);
    expect(texts(p.do('open', 'porta_cambra'))).toContain('Ni un pas');
    expect(texts(p.talk('sic', 'que_passa'))).toContain('zing');

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

    // ── Iri: enganya el Sic i torna a la cambra ──
    p.switchTo('iri');
    expect(p.room).toBe('fabrica_calderes');
    p.talk('sic', 'enganyar');
    expect(n.flag('sic_distret')).toBe(true);
    expect(n.isHotspotVisible('fabrica_calderes', 'sic')).toBe(false);
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
    // La Directora marxa: ja no hi és quan la Vet obre la reixa.
    expect(n.isHotspotVisible('gavina_cella', 'directora')).toBe(false);

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
    const tub = keys(p.use('tub_amb_llibreta', 'cambra'));
    expect(tub).toContain('finestra.enviat');
    expect(tub).toContain('sala.gavina_cella.tub0');
    expect(estatFinestra(n).enceses).toBe(enceses - 2);

    // ── Vet: la Directora el vol; fuig per la reixa, munta el tub i marxa ──
    expect(p.active).toBe('vet');
    expect(n.isHotspotVisible('gavina_cella', 'directora')).toBe(true);
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

describe('Ferro-9 · Acte 3 · Els finals', () => {
  it('sense res de més, el final 1: la fugida', () => {
    const { p, n } = partida({ checkHints: true, fins: 'fugida_completada' });
    jugarActe1(p);
    jugarActe2(p);
    jugarActe3(p);
    expect(n.flag('fugida_completada')).toBe(true);
    expect(n.resolveEnding()).toBe('fugida');
  });

  it("la Mira salvada rep els plànols (final 2), i el Cargol vell recupera el nom (final 3)", () => {
    const { p, n } = partida({ checkHints: true, fins: 'fugida_completada' });
    jugarActe1(p);
    jugarActe2(p, { mira: true, cargol: true });
    expect(n.flag('mira_salvada')).toBe(true);
    expect(n.flag('cargol_reparat')).toBe(true);
    expect(n.flag('cargol_gravat')).toBe(true);
    expect(n.state.quests.memoria_cargol!.objectives.nom).toBe(true);
    jugarActe3(p, {
      vet: () => {
        // La Guàrdia d'Orís, al passadís; la placa, a la vitrina del museu.
        p.do('open', 'porta_passadis');
        expect(n.isHotspotVisible('gavina_passadis', 'guardia')).toBe(true);
        expect(texts(p.talk('guardia', 'qui'))).toContain('una tal I.');
        p.do('open', 'porta_memoria');
        expect(texts(p.do('look', 'vitrina'))).toContain('CARGOL');
        expect(texts(p.do('open', 'vitrina'))).toContain('Tancada');
        expect(texts(p.talk('cargol_vell', 'qui'))).toContain('conserge');
        p.do('open', 'porta_passadis');
        expect(texts(p.talk('guardia', 'vitrina'))).toContain('se m\'ha caigut');
        p.do('open', 'porta_memoria');
        p.use('clau_vitrina', 'vitrina');
        expect(p.inventory()).toContain('placa_cargol');
        expect(texts(p.use('placa_cargol', 'cargol_vell'))).toContain('Era la meva feina');
        expect(n.flag('cargol_memoria')).toBe(true);
        p.do('open', 'porta_passadis');
        p.do('open', 'porta_hangar');
      },
      iri: () => {
        expect(n.isHotspotVisible('fabrica_magatzem', 'mira')).toBe(true);
        expect(texts(p.use('planols', 'mira'))).toContain('fes-los públics');
        expect(n.flag('planols_lliurats')).toBe(true);
      },
    });
    expect(n.flag('fugida_completada')).toBe(true);
    expect(n.resolveEnding()).toBe('correspondencia');
    const final = n.ending('correspondencia');
    expect(texts(final.scene)).toContain('CARGOL');
    expect(texts(final.scene)).toContain('Tinc la sensació que et conec');
  });

  it("amb la Mira salvada però sense la memòria del Cargol, el final 2; la placa sense nom no li diu res", () => {
    const { p, n } = partida({ fins: 'fugida_completada' });
    jugarActe1(p);
    jugarActe2(p, { mira: true });
    jugarActe3(p, {
      vet: () => {
        p.do('open', 'porta_passadis');
        p.do('open', 'porta_memoria');
        expect(texts(p.do('look', 'vitrina'))).not.toContain('CARGOL');
        p.do('open', 'porta_passadis');
        p.talk('guardia', 'vitrina');
        p.do('open', 'porta_memoria');
        p.use('clau_vitrina', 'vitrina');
        expect(texts(p.use('placa_cargol', 'cargol_vell'))).toContain('No em diu res');
        expect(n.flag('cargol_memoria')).toBe(false);
        p.do('open', 'porta_passadis');
        p.do('open', 'porta_hangar');
      },
      iri: () => { p.use('planols', 'mira'); },
    });
    expect(n.resolveEnding()).toBe('veritat');
  });

  it('si la Mira no es va salvar, al passat no hi és i al present no hi ha cap guàrdia', () => {
    const { p, n } = partida({ fins: 'fugida_completada' });
    jugarActe1(p);
    jugarActe2(p);
    n.apply({ addVar: 'sospita_sic', amount: 5 });
    jugarActe3(p, {
      vet: () => {
        p.do('open', 'porta_passadis');
        expect(n.isHotspotVisible('gavina_passadis', 'guardia')).toBe(false);
        p.do('open', 'porta_hangar');
      },
    });
    expect(n.isHotspotVisible('fabrica_magatzem', 'mira')).toBe(false);
    expect(n.resolveEnding()).toBe('fugida');
  });
});

describe('Ferro-9 · Missions secundàries', () => {
  it("el formulari 27-B: amb dos triplicats, el carnet d'usuària exemplar (signat pel capatàs dormint) estalvia formularis", () => {
    const { p, n } = partida({ checkHints: true, fins: 'fugida_completada' });
    jugarActe1(p);
    jugarActe2(p);
    expect(n.getVar('formularis_arxivats')).toBe(2);
    expect(n.state.quests.formulari_27b!.objectives.triplicat).toBe(true);
    p.switchTo('iri');
    p.goTo('fabrica_magatzem');
    expect(texts(p.talk('cargol', 'carnet'))).toContain('27-B/E');
    p.goTo('fabrica_calderes');
    expect(texts(p.use('formulari_27be', 'capatas'))).toContain('Cinc minuts més, mare');
    p.goTo('fabrica_magatzem');
    expect(texts(p.talk('cargol', 'carnet_lliurar'))).toContain('sense formularis');
    expect(n.state.quests.formulari_27b!.status).toBe('completed');
    // Sense cap formulari, un altre imant (per al calaix del despatx).
    p.do('open', 'porta_despatx');
    p.do('open', 'calaix');
    p.goTo('fabrica_magatzem');
    const imant = texts(p.talk('cargol', 'imant2'));
    expect(imant).toContain('sense paperassa');
    expect(imant).not.toContain('Sense excepcions');
    expect(p.inventory()).toContain('imant_ferro9');
  });

  it("les notes perdudes: cinc amagatalls, i la d'en Mos torna a en Mos", () => {
    const { p, n } = partida({ checkHints: true, fins: 'fugida_completada' });
    jugarActe1(p);
    jugarActe2(p);
    expect(p.room).toBe('gavina_cella');
    expect(texts(p.do('pickUp', 'esquerda'))).toContain('Interna 4');
    expect(p.inventory()).toContain('notes_perdudes');
    expect(n.state.quests.notes_perdudes!.status).toBe('active');
    p.do('open', 'porta');
    expect(texts(p.do('pickUp', 'rajola'))).toContain('paper bo');
    p.do('open', 'porta_hangar');
    expect(texts(p.do('open', 'caixa_recanvis'))).toContain('Interna 23');
    p.do('open', 'escala');
    expect(texts(p.do('pickUp', 'carpeta'))).toContain('reciclatge');
    p.do('open', 'escala_hangar');
    p.do('open', 'porta_passadis');
    p.do('open', 'porta_memoria');
    expect(texts(p.do('open', 'socol'))).toContain('En Mos');
    expect(n.getVar('notes_trobades')).toBe(5);
    expect(n.isHotspotVisible('gavina_memoria', 'socol')).toBe(false);
    expect(texts(p.do('look', { kind: 'item', id: 'notes_perdudes' }))).toContain('any 80');
    p.do('open', 'porta_passadis');
    p.do('open', 'porta_cella');
    expect(texts(p.use('nota_mos', 'mos'))).toContain('Ets un sol');
    expect(n.state.quests.notes_perdudes!.status).toBe('completed');
  });

  it("la drecera d'en Mos: amb la carta tornada, es desmaia de mentida i la Vet no ha d'acceptar el pacte", () => {
    const { p, n } = partida({ checkHints: true, fins: 'fugida_completada' });
    jugarActe1(p);
    jugarActe2(p);
    jugarActe3(p, {
      inici: () => {
        // La carta d'en Mos, de l'arxiu (ja obert a l'Acte 2) a en Mos.
        p.do('open', 'porta');
        p.do('open', 'porta_hangar');
        p.do('open', 'escala');
        p.do('open', 'arxivador');
        p.do('open', 'escala_hangar');
        p.do('open', 'porta_passadis');
        p.do('open', 'porta_cella');
        p.use('carta_mos', 'mos');
      },
      mos: true,
    });
    expect(n.flag('mos_distreu')).toBe(true);
    expect(n.flag('pacte_acceptat')).toBe(false);
    expect(n.flag('cella_tancada')).toBe(true);
    expect(n.resolveEnding()).toBe('fugida');
    const scene = texts(n.ending('fugida').scene);
    expect(scene).toContain('Nura');
    expect(scene).not.toContain('Mira');
  });
});
