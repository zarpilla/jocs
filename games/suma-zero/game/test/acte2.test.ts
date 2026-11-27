/** L'Acte 2 jugat sencer, per tots els camins, amb una pista disponible a cada pas. */
import { describe, expect, it } from 'vitest';
import {
  jugarActe1, jugarActe2, jugarCollaret, jugarTercerPis, jugarVestibul, partida, texts, type OpcionsActe1, type OpcionsActe2,
} from './partida.js';

/** Una partida amb l'Acte 1 ja jugat: la Vet al vestíbul i l'Iri, al moll. */
function aGinebra(o1: OpcionsActe1 = {}) {
  const r = partida({ checkHints: true, fins: 'acte2_fet' });
  jugarActe1(r.p, o1);
  return r;
}

describe('Acte 2 · camins', () => {
  it('amb els tres aliats: la Rius, NETA-3 i en Ballester', () => {
    const { n, p, world } = aGinebra();
    jugarActe2(p, { aliats: true });
    expect(n.flag('acte2_fet')).toBe(true);
    // girar la clau ja no acaba el joc: comença l'Acte 3, amb l'Iri al Llibre Major i la Vet a seguretat
    expect(n.resolveEnding()).toBe(null);
    expect(n.flag('cal_director')).toBe(true);
    expect(n.getVar('aliats')).toBe(3);
    for (const f of ['aliada_rius', 'aliat_neta', 'aliat_ballester']) expect(n.flag(f), f).toBe(true);
    expect(world.items('iri')).toContain('compte_nomines');
    expect(world.items('iri')).toContain('clau_llibre');
    expect(world.items('vet')).toContain('clau_casa');
    const estat = Object.fromEntries(n.quests().map((q) => [q.id, q.status]));
    expect(estat).toMatchObject({ acte2: 'completed', subcontractats: 'completed', hores_neta: 'completed', veritat_ballester: 'completed' });
  });

  for (const robot of ['entrepa', 'maquina', 'ballester'] as const) {
    it(`sense aliats, aturant el robot amb ${robot === 'entrepa' ? "l'entrepà de casa" : robot === 'maquina' ? "l'entrepà de la màquina" : "l'entrepà d'en Ballester"}`, () => {
      const { n, p, world } = aGinebra({ entrepa: robot === 'entrepa' });
      const o: OpcionsActe2 = { robot };
      jugarActe2(p, o);
      expect(n.flag('acte2_fet')).toBe(true);
      expect(n.getVar('aliats')).toBe(0);
      expect(n.getVar('robot')).toBe('entrepa');
      expect(n.flag('clau_canviada')).toBe(true);
      expect(world.items('vet')).not.toContain('clau_casa'); // ara la porta en Ballester al coll
      const estat = Object.fromEntries(n.quests().map((q) => [q.id, q.status]));
      // Ningú no ha preguntat per l'aplicació de la Rius: la missió no ha començat.
      expect(estat).toMatchObject({ acte2: 'completed', subcontractats: 'inactive', veritat_ballester: 'inactive', hores_neta: 'inactive' });
    });
  }

  it("en l'altre ordre: l'Iri arriba al Llibre Major abans que la Vet parli amb el Director", () => {
    const { n, p } = aGinebra();
    jugarTercerPis(p, { aliats: true });
    expect(p.room).toBe('bcmu_escombraries');
    expect(texts(p.do('use', 'llibre'))).toContain('Vet, on ets?');
    expect(n.flag('sync_collaret')).toBe(false);
    jugarVestibul(p);
    jugarCollaret(p, { aliats: true });
    expect(n.flag('acte2_fet')).toBe(true);
  });

  it("amb la preparació de l'aeroport, el Director no pregunta pel maletí ni per l'edat", () => {
    const { n, p } = aGinebra({ preparacio: true });
    p.do('look', 'retrat');
    const lines = texts(p.talk('bonfill', 'cor', 'rockefeller', 'seguretat'));
    expect(lines).toContain('Una auditora de les de debò');
    expect(lines).not.toContain('sense maletí');
    expect(n.getVar('sospita_max')).toBe(5);
    expect(n.flag('auditoria_acceptada')).toBe(true);
  });
});

describe('Acte 2 · la sospita i el Dia de la Marmota', () => {
  it('a 100, el Director truca a seguretat; la Vet torna a començar amb opcions noves i el que ha après', () => {
    const { n, p } = aGinebra();
    const lines = texts(p.talk('bonfill', 'avio', 'acreditacio')); // 30 + 40 + 30
    expect(lines).toContain('Dia de la Marmota');
    expect(lines).toContain('es posa bé la corbata');
    expect(n.getVar('marmota')).toBe(1);
    expect(n.flag('planta_retallada')).toBe(true);
    expect(n.flag('auditoria')).toBe(false);
    expect(n.flag('auditoria_acceptada')).toBe(false);
    expect(n.getVar('sospita_max')).toBe(100);
    // La segona vegada: «Bon dia. Una auditora?», i les respostes noves.
    const segona = texts(p.talk('bonfill', 'nuvols', 'crema', 'dacord', 'tecnics'));
    expect(segona).toContain('Una auditora?');
    expect(n.flag('auditoria_acceptada')).toBe(true);
    expect(n.flag('mentida_corporativa')).toBe(true);
    expect(n.getVar('sospita')).toBe(10);
    expect(texts(p.do('look', 'plantes'))).toContain('retallada');
  });

  it('les respostes noves no hi són abans del primer reinici, i la sospita mai no baixa de 0', () => {
    const { n, p } = aGinebra({ preparacio: true });
    p.do('look', 'retrat');
    expect(() => p.talk('bonfill', 'tecnics')).toThrow(/no disponible/);
    p.talk('bonfill', 'dacord', 'rockefeller', 'seguretat');
    expect(n.getVar('sospita')).toBe(0);
  });

  it('preguntar per les caixes o pels comptes repeteix la pregunta', () => {
    const { n, p } = aGinebra();
    const lines = texts(p.talk('bonfill', 'secrets', 'directives', 'cor', 'caixes', 'seguretat'));
    expect(lines).toContain('Doncs què vol veure, de debò?');
    expect(n.getVar('sospita')).toBe(30 + 5 + 5 + 20);
    expect(n.flag('auditoria_acceptada')).toBe(true);
  });
});

describe('Acte 2 · el tub pneumàtic', () => {
  it("només hi passa el que hi cap i el que l'altra necessita, i al moll no hi arriba", () => {
    const { n, p, world } = aGinebra({ entrepa: true });
    expect(texts(p.use('entrepa', 'tub'))).toContain('encara és al moll');
    expect(world.items('vet')).toContain('entrepa');
    expect(texts(p.use('clau_casa', 'tub'))).toContain('dormim al replà');
    expect(texts(p.use('acreditacio', 'tub'))).toContain('No li fa cap falta');
    p.switchTo('iri');
    p.talk('rius', 'cafe');
    p.do('use', 'ascensor');
    expect(texts(p.use('auriculars', 'tub'))).toContain('no et sento');
    p.do('pickUp', 'galleda');
    expect(texts(p.use('galleda', 'tub'))).toContain('No hi cap');
    p.switchTo('vet');
    const enviat = texts(p.use('entrepa', 'tub'));
    expect(enviat).toContain('A la càpsula, i cap amunt');
    expect(enviat).toContain("Ha arribat l'entrepà de tonyina");
    expect(world.items('iri')).toContain('entrepa');
    expect(p.active).toBe('vet');
    // Un cop aturat el robot, l'entrepà ja no li fa falta.
    p.switchTo('iri');
    p.talk('neta', 'descansa');
    p.use('entrepa', 'tub');
    expect(world.items('vet')).not.toContain('entrepa');
    expect(n.flag('robot_aturat')).toBe(true);
  });
});

describe('Acte 2 · el tercer pis', () => {
  function alPassadis(o1: OpcionsActe1 = {}) {
    const r = aGinebra(o1);
    r.p.switchTo('iri');
    r.p.talk('rius', 'cafe');
    r.p.do('use', 'ascensor');
    return r;
  }

  it('amb el robot en marxa, el que es posa a les càmeres torna al seu lloc', () => {
    const { n, p, world } = alPassadis();
    p.do('pickUp', 'cartell');
    expect(texts(p.use('cartell', 'camera1'))).toContain('Desfà més ràpid que jo');
    expect(n.flag('camera1_tapada')).toBe(false);
    expect(world.items('iri')).not.toContain('cartell');
    expect(n.isHotspotVisible('bcmu_passadis', 'cartell')).toBe(true);
  });

  it("cada cosa a la seva càmera; l'extintor no; i sense les dues tapades no s'entra", () => {
    const { n, p } = alPassadis();
    p.talk('neta', 'descansa');
    p.do('pickUp', 'cartell');
    p.do('pickUp', 'galleda');
    p.do('pickUp', 'extintor');
    expect(texts(p.use('galleda', 'camera1'))).toContain('massa alta');
    expect(texts(p.use('cartell', 'camera2'))).toContain('és un racó');
    expect(texts(p.use('extintor', 'camera1'))).toContain('Massa dramàtic');
    p.use('cartell', 'camera1');
    expect(texts(p.do('use', 'porta_neteja'))).toContain('Primer, les càmeres');
    expect(p.room).toBe('bcmu_passadis');
    p.use('galleda', 'camera2');
    p.do('use', 'porta_neteja');
    expect(p.room).toBe('bcmu_escombraries');
    expect(n.flag('sap_cartell')).toBe(true);
  });

  it("aturat amb l'entrepà, el robot no deixa canviar-li l'horari (i la missió no comença)", () => {
    const { n, p } = alPassadis({ entrepa: true });
    p.switchTo('vet');
    p.use('entrepa', 'tub');
    p.switchTo('iri');
    p.use('entrepa', 'neta');
    expect(texts(p.do('talkTo', 'neta'))).toContain('Molla quatre-cents');
    p.do('pickUp', 'cartell');
    p.use('cartell', 'camera1');
    p.do('pickUp', 'galleda');
    p.use('galleda', 'camera2');
    p.do('use', 'porta_neteja');
    expect(texts(p.do('use', 'panell'))).toContain('comptant molles');
    expect(n.flag('aliat_neta')).toBe(false);
    expect(n.quests().find((q) => q.id === 'hores_neta')?.status).toBe('inactive');
  });

  it("si l'Iri sap el problema de la Rius i puja sense arreglar-l'hi, la missió falla", () => {
    const { n, p } = aGinebra();
    p.switchTo('iri');
    p.talk('rius', 'mobil', 'cafe');
    expect(n.quests().find((q) => q.id === 'subcontractats')?.status).toBe('active');
    p.do('use', 'ascensor');
    expect(n.quests().find((q) => q.id === 'subcontractats')?.status).toBe('failed');
  });

  it("la Rius: si l'Iri ja té la targeta i li arregla l'aplicació, és aliada igual", () => {
    const { n, p, world } = aGinebra();
    p.switchTo('iri');
    p.talk('rius', 'cafe');
    p.do('look', 'maquina');
    const lines = texts(p.talk('rius', 'mobil', 'arreglar'));
    expect(lines).toContain("Ja l'havies agafada");
    expect(n.flag('aliada_rius')).toBe(true);
    expect(world.items('iri').filter((i) => i === 'targeta')).toHaveLength(1);
    expect(world.items('iri')).toContain('compte_nomines');
  });
});

describe("Acte 2 · sense el codi de NETA-3 (la Vet no ho va preguntar a en Marcel)", () => {
  for (const entrepa of [true, false]) {
    it(entrepa ? "la Vet porta l'entrepà de casa: la pista és enviar-lo pel tub" : "la Vet no té menjar: la pista és buscar-ne (l'entrepà d'en Ballester)", () => {
      const { n, p } = partida({ checkHints: true, fins: 'acte2_fet' });
      jugarActe1(p, { sensNeta: true, entrepa });
      expect(n.flag('iri_sap_neta')).toBe(false);
      jugarVestibul(p);
      p.switchTo('iri');
      p.talk('rius', 'cafe');
      p.do('use', 'ascensor');
      expect(n.flag('iri_sap_neta')).toBe(false);
      expect(n.activeHints()[0]).toBe('iri_robot');
      p.switchTo('vet');
      expect(n.activeHints()[0]).toBe(entrepa ? 'vet_enviar_menjar' : 'vet_buscar_menjar');
      if (!entrepa) p.do('pickUp', 'entrepa');
      const menjar = entrepa ? 'entrepa' : 'entrepa_ballester';
      p.use(menjar, 'tub');
      p.switchTo('iri');
      p.use(menjar, 'neta');
      expect(n.flag('robot_aturat')).toBe(true);
      // i la resta de l'acte, igual
      p.do('pickUp', 'cartell');
      p.use('cartell', 'camera1');
      p.do('pickUp', 'galleda');
      p.use('galleda', 'camera2');
      p.do('use', 'porta_neteja');
      jugarCollaret(p);
      expect(n.flag('acte2_fet')).toBe(true);
    });
  }
});

describe('Acte 2 · la sincronia del collaret', () => {
  function finsAlLlibre() {
    const r = aGinebra();
    jugarVestibul(r.p);
    jugarTercerPis(r.p, { aliats: true });
    r.p.do('use', 'llibre');
    return r;
  }

  it('el primer bip és lliure i ensenya la regla', () => {
    const { n } = finsAlLlibre();
    expect(n.flag('sync_collaret')).toBe(true);
    expect(n.flag('regla_bips')).toBe(true);
    expect(n.getVar('codis')).toBe(1);
    expect(n.getVar('sospita_ballester')).toBe(0);
  });

  it('un bip sense cobrir no compta i puja la sospita; a la tercera, es torna a començar pel primer codi i les eines tornen', () => {
    const { n, p } = finsAlLlibre();
    p.switchTo('vet');
    p.talk('ballester', 'cantar', 'adeu');
    p.switchTo('iri');
    p.do('use', 'llibre'); // tapat pel cant
    expect(n.getVar('codis')).toBe(2);
    expect(texts(p.do('use', 'llibre'))).toContain('el codi caduca');
    expect(n.getVar('codis')).toBe(2);
    expect(n.getVar('sospita_ballester')).toBe(1);
    p.do('use', 'llibre');
    const reinici = texts(p.do('use', 'llibre'));
    expect(reinici).toContain('torna a començar pel primer codi');
    expect(n.getVar('codis')).toBe(0);
    expect(n.getVar('sospita_ballester')).toBe(0);
    expect(n.getVar('reinicis_collaret')).toBe(1);
    expect(n.flag('cantat')).toBe(false);
    // Torna a començar: el primer codi, lliure; i la Vet pot tornar a cantar.
    expect(texts(p.do('use', 'llibre'))).toContain('Una altra vegada');
    expect(n.getVar('codis')).toBe(1);
    p.switchTo('vet');
    p.talk('ballester', 'cantar', 'violi', 'adeu');
    p.switchTo('iri');
    p.do('use', 'llibre');
    p.do('use', 'llibre');
    expect(n.flag('cal_clau')).toBe(true);
    expect(n.flag('sync_collaret')).toBe(false);
  });

  it("el got tapa un bip però puja la sospita; «La vídua del Liceu» només la puja; l'acudit de l'auditor no tapa res", () => {
    const { n, p } = finsAlLlibre();
    p.switchTo('vet');
    p.do('use', 'got');
    expect(n.getVar('coberta')).toBe(1);
    expect(n.getVar('sospita_ballester')).toBe(1);
    p.talk('ballester', 'vidua', 'auditor', 'adeu');
    expect(n.getVar('coberta')).toBe(1);
    expect(n.getVar('sospita_ballester')).toBe(2);
    expect(texts(p.do('use', 'got'))).toContain('Ja està trencat');
  });

  it("«El violí mut» tapa un sol bip: el tercer codi necessita una altra eina", () => {
    const { n, p } = finsAlLlibre();
    p.switchTo('vet');
    p.talk('ballester', 'violi', 'adeu');
    expect(n.getVar('coberta')).toBe(1);
    expect(n.flag('ballester_relaxat')).toBe(true);
  });

  it("sense haver-lo relaxat amb la sèrie, en Ballester no s'obre: només hi ha la mentida", () => {
    const { n, p } = finsAlLlibre();
    p.switchTo('vet');
    p.talk('ballester', 'cantar', 'banquers', 'adeu');
    p.switchTo('iri');
    p.do('use', 'llibre');
    p.do('use', 'llibre');
    p.switchTo('vet');
    expect(n.activeHints()[0]).toBe('vet_clau'); // no promet la veritat: només el collaret
    expect(() => p.talk('ballester', 'veritat')).toThrow(/no disponible/);
    p.talk('ballester', 'or');
    expect(n.flag('clau_canviada')).toBe(true);
    expect(n.quests().find((q) => q.id === 'veritat_ballester')?.status).toBe('inactive');
  });

  it('relaxat i amb la mentida: la missió d\'en Ballester falla', () => {
    const { n, p } = finsAlLlibre();
    p.switchTo('vet');
    p.talk('ballester', 'violi', 'cantar', 'adeu');
    p.switchTo('iri');
    p.do('use', 'llibre');
    p.do('use', 'llibre');
    p.switchTo('vet');
    expect(n.activeHints()[0]).toBe('vet_clau_relaxat');
    expect(texts(p.talk('ballester', 'mentida'))).toContain('hipoteca');
    expect(n.quests().find((q) => q.id === 'veritat_ballester')?.status).toBe('failed');
    expect(n.flag('aliat_ballester')).toBe(false);
  });

  it("durant la sincronia, la Vet no pot marxar i l'Iri no pot tocar el panell de NETA-3", () => {
    const { p } = finsAlLlibre();
    expect(texts(p.do('use', 'panell'))).toContain('també fa bip');
    p.switchTo('vet');
    expect(texts(p.do('use', 'ascensor'))).toContain('Ara no puc');
    expect(p.room).toBe('bcmu_seguretat');
  });
});

describe('Acte 2 · coherència', () => {
  it("l'Iri només sap el codi del robot si la Vet l'hi ha dit; si no, la Vet l'hi diu en veure el robot", () => {
    const { n, p } = aGinebra();
    expect(n.flag('iri_sap_neta')).toBe(true); // ho va saber a la trucada del bar
    n.apply({ setFlag: 'iri_sap_neta', value: false });
    p.switchTo('iri');
    p.talk('rius', 'cafe');
    expect(texts(p.do('use', 'ascensor'))).toContain('NETA, descansa');
    expect(n.flag('iri_sap_neta')).toBe(true);
  });

  it("amb l'Iri al Llibre Major abans que la Vet arribi a seguretat: l'Iri l'avisa, i la pista de la Vet no diu que l'Iri no hi és", () => {
    const { n, p } = aGinebra();
    jugarTercerPis(p, { aliats: true });
    expect(n.flag('iri_a_llibre')).toBe(true);
    const abans = p.transcript.length;
    jugarVestibul(p);
    expect(p.transcript.slice(abans).join(' ')).toContain('Jo ja soc al Llibre Major');
    const pistes = n.activeHints();
    expect(pistes).toContain('vet_comencar');
    expect(pistes).not.toContain('vet_espera_iri');
  });

  it('la roba: la Vet continua d\'auditora a tot l\'acte', () => {
    const { n, p } = aGinebra();
    jugarActe2(p, { aliats: true });
    expect(n.outfitOf('vet')).toBe('Auditora');
  });

  it('cada objecte nou té un nom amb article i es pot mirar', () => {
    const { n } = partida();
    for (const id of ['entrepa_suis', 'entrepa_ballester', 'targeta', 'compte_nomines', 'galleda', 'cartell', 'extintor', 'clau_llibre', 'clauer']) {
      expect(n.t(`obj.${id}.amb_article`)).not.toMatch(/^⟦/);
      expect(n.content.items[id]?.interactions?.some((i) => i.verb === 'look')).toBe(true);
    }
  });
});
