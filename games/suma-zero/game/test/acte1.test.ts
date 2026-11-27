/** L'Acte 1 jugat sencer, per tots els camins, amb una pista disponible a cada pas. */
import { describe, expect, it } from 'vitest';
import {
  barComandament, barRecepta, barTap, item, jugarActe1, jugarAeroport, jugarBar, jugarPis, partida, texts,
} from './partida.js';

describe('Acte 1 · camins', () => {
  for (const sacrifici of ['caixa', 'auricular', 'pizza'] as const) {
    it(`de cap a peus, distraient en Diu amb ${sacrifici}`, () => {
      const { n, p, world } = partida({ checkHints: true });
      jugarActe1(p, { sacrifici });
      expect(n.getVar('sacrifici')).toBe(sacrifici);
      expect(n.flag('acte1_fet')).toBe(true);
      // L'avió ja no acaba el joc: porta la Vet al vestíbul del BCMU i l'Iri, al moll de càrrega.
      expect(n.resolveEnding()).toBe(null);
      expect(p.room).toBe('bcmu_vestibul');
      expect(world.rooms.get('iri')).toBe('bcmu_moll');
      expect(world.items('vet')).toContain('acreditacio');
      expect(world.items('iri')).toContain('acreditacio');
      expect(world.items('iri')).not.toContain('acreditacions');
    });
  }

  it("amb l'entrepà, el tap tornat i la preparació d'auditora", () => {
    const { n, p, world } = partida({ checkHints: true });
    jugarActe1(p, { entrepa: true, tap: true, preparacio: true });
    for (const i of ['entrepa', 'clau_casa', 'maleti', 'recepta']) expect(world.items('vet')).toContain(i);
    expect(world.items('vet')).not.toContain('ulleres');   // se les posa: les porta a la cara, no a la bossa
    expect(world.items('vet')).not.toContain('tap');
    expect(n.flag('ulleres_posades')).toBe(true);
    expect(n.flag('iri_sap_neta')).toBe(true);    // a l'avió, el vestit surt d'objectes perduts «ja que hi era pel maletí»
    expect(p.transcript.join(' ')).toContain('Ja que hi era pel maletí');
  });

  it("al bar, en un altre ordre (el comandament primer): les pistes porten a la recepta i després al tap", () => {
    const { n, p } = partida({ checkHints: true });
    jugarPis(p);
    p.talk('marcel');
    expect(n.activeHints()[0]).toBe('vet_comandament');
    barComandament(p);
    expect(n.activeHints()[0]).toBe('vet_recepta');
    barRecepta(p);
    expect(n.activeHints()[0]).toBe('vet_tap');
    barTap(p);
    expect(n.getVar('donats')).toBe(3);
  });

  it("amb en Tomàs al rebost (telèfon ocupat), la pista diu de donar el comandament a en Marcel", () => {
    const { n, p } = partida({ checkHints: true });
    jugarPis(p);
    p.talk('marcel');
    p.do('use', 'porta_rebost');
    p.do('look', 'calaix');
    p.do('use', 'porta');
    p.talk('trucada', 'pany', 'adeu');
    expect(n.activeHints()[0]).toBe('vet_dir_contrasenya');
    p.talk('tomas', 'comandament', 'adeu');
    p.talk('trucada', 'trucada', 'adeu');
    p.switchTo('iri');
    p.do('use', 'ordinadors');
    p.switchTo('vet');
    expect(n.flag('tomas_rebost')).toBe(true);
    expect(n.activeHints()[0]).toBe('vet_agafar_comandament');
    p.do('pickUp', 'comandament_barra');
    expect(n.activeHints()[0]).toBe('vet_tomas_rebost');
    p.do('give', 'marcel', 'comandament');
    expect(n.activeHints()[0]).toBe('vet_dir_contrasenya');
  });

  it('amb un codi dolent: la porta xiula i la Vet plora més fort', () => {
    const { n, p } = partida({ checkHints: true });
    jugarPis(p);
    jugarBar(p);
    p.talk('soler', 'fill', 'nom_curt', 'edat_curt', 'roba_curt');
    p.switchTo('iri');
    p.do('use', 'teclat');
    expect(n.activeHints()[0]).toBe('iri_alarma'); // no «la Vet el veu»: primer, que plori
    p.switchTo('vet');
    expect(n.activeHints()[0]).toBe('vet_plorar');
    p.talk('soler', 'plorar');
    p.do('look', 'taulell');
    p.switchTo('iri');
    p.do('use', 'teclat');
    p.do('use', 'terminal');
    expect(n.activeHints()[0]).toBe('iri_impressora');
    p.do('push', 'impressora');
    expect(n.activeHints()[0]).toBe('iri_acreditacions');
    p.do('pickUp', 'impressora');
    p.do('use', 'porta');
    p.switchTo('vet');
    p.do('talkTo', 'nen');
    expect(n.flag('aeroport_fet')).toBe(true);
    expect(n.getVar('reinicis_aeroport')).toBe(0);
  });
});

describe("Acte 1 · la sincronia de l'aeroport", () => {
  function finsAeroport() {
    const r = partida({ checkHints: true });
    jugarPis(r.p);
    jugarBar(r.p);
    return r;
  }

  it("si la Vet no plora després del xiulet, es torna a començar el pas (i es pot tornar a fer)", () => {
    const { n, p } = finsAeroport();
    p.talk('soler', 'fill', 'nom_curt', 'edat_curt', 'roba_curt');
    p.switchTo('iri');
    p.do('use', 'teclat'); // xiula
    const lines = texts(p.do('look', 'teclat').concat(p.do('use', 'teclat'))); // mirar no compta; tornar-hi (sense que la Vet plori), sí
    expect(lines).toContain('Una hora i una cigarreta més tard');
    // el reinici ve del xiulet, no de la cigarreta
    expect(lines).toContain('El vigilant sent el xiulet');
    expect(lines).not.toContain('llença la burilla');
    expect(n.flag('sync_aeroport')).toBe(false);
    expect(n.getVar('cigarreta')).toBe(12);
    expect(n.getVar('reinicis_aeroport')).toBe(1);
    p.switchTo('vet');
    // el vigilant recorda que ja l'havia buscat
    expect(texts(p.talk('soler', 'fill', 'nom_curt', 'edat_curt', 'roba_curt'))).toContain("Aquest nen s'escapa molt");
    p.do('look', 'taulell');
    p.switchTo('iri');
    p.do('use', 'teclat');
    p.do('use', 'terminal');
    p.do('push', 'impressora');
    p.do('pickUp', 'impressora');
    p.do('use', 'porta');
    p.switchTo('vet');
    p.do('talkTo', 'nen');
    expect(n.flag('aeroport_fet')).toBe(true);
  });

  it("parlar massa gasta la cigarreta: amb totes les respostes llargues i una acció perduda, s'acaba", () => {
    const { n, p } = finsAeroport();
    p.talk('soler', 'fill', 'nom_llarg', 'edat_llarg', 'roba_llarg');
    expect(n.getVar('cigarreta')).toBe(12 - 4 - 3);
    p.do('look', 'taulell');
    p.switchTo('iri');
    p.do('use', 'teclat');
    p.do('use', 'terminal');
    p.do('push', 'impressora');
    p.do('use', 'terminal'); // «Ja som a la llista»: un torn perdut
    const lines = texts(p.do('pickUp', 'impressora'));
    expect(lines).toContain('Una hora i una cigarreta més tard');
    expect(n.flag('soler_distret')).toBe(false);
    // L'Iri té les acreditacions, però el vigilant torna a ser a la porta: no pot sortir fins que la Vet el distregui.
    expect(texts(p.do('use', 'porta'))).toContain('El vigilant em veuria sortir');
    p.switchTo('vet');
    p.talk('soler', 'fill', 'nom_curt', 'edat_curt', 'roba_curt');
    p.switchTo('iri');
    p.do('use', 'porta');
    p.switchTo('vet');
    p.do('talkTo', 'nen');
    expect(n.flag('aeroport_fet')).toBe(true);
  });

  it("mirar i canviar de protagonista no gasten torns", () => {
    const { n, p } = finsAeroport();
    p.talk('soler', 'fill', 'nom_curt', 'edat_curt', 'roba_curt');
    const abans = n.getVar('cigarreta');
    p.do('look', 'vidriera');
    p.do('look', 'taulell');
    p.switchTo('iri');
    p.do('look', 'teclat');
    p.switchTo('vet');
    expect(n.getVar('cigarreta')).toBe(abans);
  });
});

describe('Acte 1 · coherència', () => {
  it("no es pot canviar a la Vet fins que l'Iri li demana alguna cosa", () => {
    const { n, p } = partida();
    expect(n.canSwitch()).toBe(false);
    p.do('open', 'caixa');
    p.do('open', 'passaplats');
    p.talk('passaplats', 'cable');
    expect(n.canSwitch()).toBe(true);
  });

  it("el passaplats tancat: no s'hi passa res, i parlar-hi l'obre; obert des d'un costat, és obert per a les dues", () => {
    const { n, p, world } = partida();
    p.do('open', 'caixa');
    expect(texts(p.use('cable_xarxa', 'passaplats'))).toContain("Primer l'hauria d'obrir");
    expect(world.hasItem('cable_xarxa', 'iri')).toBe(true);
    expect(texts(p.do('talkTo', 'passaplats'))).toContain('Obert');
    expect(n.flag('passaplats_obert')).toBe(true);
    expect(n.flag('cable_demanat')).toBe(false);
    p.talk('passaplats', 'cable');
    p.switchTo('vet');
    p.do('pickUp', 'cafetera');
    p.use('cable_alimentacio', 'passaplats');
    expect(world.hasItem('cable_alimentacio', 'iri')).toBe(true);
  });

  it("la Vet no pot marxar del pis fins que l'Iri ha trobat el servidor", () => {
    const { n, p } = partida();
    p.do('open', 'caixa');
    p.do('open', 'passaplats');
    p.talk('passaplats', 'cable');
    p.switchTo('vet');
    expect(texts(p.do('use', 'porta'))).toContain('Encara no');
    expect(n.flag('vet_marxa')).toBe(false);
  });

  it("l'Iri no sap els capítols de la sèrie d'en Ballester: només que hi ha «un tal Ballester i una sèrie»", () => {
    const { p } = partida();
    jugarActe1(p);
    const iri = p.transcript.filter((l) => l.startsWith('iri:')).join('\n');
    expect(iri).not.toContain('violí');
    expect(iri).not.toContain('vídua');
  });

  it("en Tomàs només pregunta pel tap si no l'hi han tornat", () => {
    const amb = partida();
    jugarActe1(amb.p, { tap: true });
    expect(amb.p.transcript.join('\n')).not.toContain('On és el meu tap?');
    const sense = partida();
    jugarActe1(sense.p);
    expect(sense.p.transcript.join('\n')).toContain('On és el meu tap?');
  });

  it('el rebost és tancat mentre en Tomàs hi discuteix amb la seva dona inexistent', () => {
    const { n, p } = partida();
    jugarPis(p);
    p.talk('marcel');
    p.talk('tomas', 'comandament', 'adeu');
    p.talk('trucada', 'trucada', 'adeu');
    p.switchTo('iri');
    p.do('use', 'ordinadors');
    p.switchTo('vet');
    expect(n.flag('tomas_rebost')).toBe(true);
    expect(texts(p.do('use', 'porta_rebost'))).toContain('divorciant-se');
    expect(p.room).toBe('bar_sala');
  });

  it('cada objecte té un nom amb article i les protagonistes el poden mirar', () => {
    const { n } = partida();
    for (const id of Object.keys(n.content.items)) {
      expect(n.t(`obj.${id}.amb_article`)).not.toMatch(/^⟦/);
    }
    void item;
  });
});

describe('Acte 1 · la roba de la Vet', () => {
  it('canvia a cada escena: casa, bar, aeroport i, a Ginebra, auditora', () => {
    const { n, p } = partida({ checkHints: true });
    expect(n.outfitOf('vet')).toBe('');
    jugarPis(p);
    expect(n.outfitOf('vet')).toBe('Franela');
    jugarBar(p);
    expect(n.outfitOf('vet')).toBe('Bomber');
    jugarAeroport(p);
    expect(n.outfitOf('vet')).toBe('Auditora');
    expect(n.outfitOf('iri')).toBe('');
  });

  it('amb les ulleres posades, se li veuen', () => {
    const { n, p } = partida({ checkHints: true });
    jugarPis(p);
    jugarBar(p);
    jugarAeroport(p, { preparacio: true });
    expect(n.outfitOf('vet')).toBe('AuditoraUlleres');
  });
});

describe('Acte 1 · revisió de coherència', () => {
  it("el tap no es pot tornar a en Tomàs abans que en Marcel l'hagi vist (si no, atzucac)", () => {
    const { n, p, world } = partida();
    jugarPis(p);
    p.talk('marcel');
    p.talk('tomas', 'cafe', 'adeu');
    p.do('pickUp', 'tap_barra');
    expect(texts(p.do('give', 'tomas', 'tap'))).toContain("Primer l'ha de veure en Marcel");
    expect(n.flag('tap_tornat')).toBe(false);
    expect(world.items('vet')).toContain('tap');
  });

  it("a en Diu se li poden donar les coses, no només fer-les servir amb ell (la pizza és «per al gat»)", () => {
    const { n, p } = partida();
    p.do('open', 'caixa');
    p.use('cable_xarxa', 'router'); // en Diu el mossega
    p.do('open', 'passaplats');
    p.talk('passaplats', 'pizza');
    p.switchTo('vet');
    p.do('open', 'nevera');
    p.do('pickUp', 'pizza_nevera');
    p.use('pizza', 'passaplats');
    p.switchTo('iri');
    expect(texts(p.do('give', 'diu', 'pizza'))).toContain('La pizza de demà');
    expect(n.getVar('sacrifici')).toBe('pizza');
  });

  it("la recepta es pot tornar a en Tomàs (després que en Marcel l'hagi vista)", () => {
    const { p, world } = partida();
    jugarPis(p);
    const abans = p.transcript.length;
    jugarBar(p, { recepta: true });
    // en tornar a la Vet després de la trucada, es diu on és en Tomàs
    expect(p.transcript.slice(abans).join(' ')).toContain("En Tomàs s'ha tancat al rebost");
    expect(p.transcript.slice(abans).join(' ')).toContain('Com ha sortit del calaix');
    expect(world.items('vet')).not.toContain('recepta');
  });

  it("pistes del pis: amb en Diu distret però sense el cable d'alimentació, la pista diu d'on treure'l", () => {
    const { n, p } = partida();
    p.do('use', 'fibra'); // en Diu la mossega
    expect(n.activeHints()[0]).toBe('iri_cable_cafetera'); // abans que en Diu: primer, els cables
    p.do('open', 'passaplats');
    p.talk('passaplats', 'pizza');
    p.switchTo('vet');
    p.do('open', 'nevera');
    p.do('pickUp', 'pizza_nevera');
    expect(n.activeHints()[0]).toBe('vet_passar_pizza'); // ja la té la Vet: ara, passar-la
    p.use('pizza', 'passaplats');
    p.switchTo('iri');
    p.do('give', 'diu', 'pizza');
    expect(n.flag('diu_distret')).toBe(true);
    expect(n.activeHints()[0]).toBe('iri_cable_cafetera');
    expect(n.t('pista.iri_cable_cafetera.2')).toContain('cafetera');
  });

  it("la pista de plegar del bar només parla del tap si la Vet el porta", () => {
    const { n, p } = partida();
    jugarPis(p);
    n.apply([{ setFlag: 'resum_fet' }]);
    n.apply({ giveItem: 'tap', who: 'vet' });
    expect(n.activeHints()[0]).toBe('vet_plegar_tap');
    n.apply({ takeItem: 'tap', who: 'vet' });
    expect(n.activeHints()[0]).toBe('vet_plegar');
  });

  it('en Marcel no torna a comptar el que ja ha vist', () => {
    const { n, p } = partida();
    jugarPis(p);
    jugarBar(p);
    p.do('give', 'marcel', 'recepta');
    expect(n.getVar('donats')).toBe(3);
  });

  it('amb la Vet al bar, el passaplats ja no la porta', () => {
    const { p } = partida();
    jugarPis(p);
    p.switchTo('iri');
    expect(texts(p.do('talkTo', 'passaplats'))).toContain('La Vet és al bar');
  });

  it("si en Diu es queda els auriculars, els torna mossegats quan la Vet marxa; a l'aeroport, la Vet porta un dels de botó", () => {
    const { n, p, world } = partida();
    expect(world.items('iri')).toEqual(expect.arrayContaining(['auriculars', 'auriculars_boto']));
    const pis = texts(jugarPisAmbLinies(p));
    expect(pis).toContain('forats de dent');
    expect(world.items('iri')).toContain('auriculars');
    jugarBar(p);
    expect(n.flag('auricular_compartit')).toBe(true);
    p.switchTo('iri');
    expect(texts(p.do('look', item('auriculars')))).toContain('forats de dent');
    expect(texts(p.do('look', item('auriculars_boto')))).toContain("L'altre el porta la Vet");
  });

  it('mentre en Diu té els auriculars, l\'Iri no els porta (ni al sprite)', () => {
    const { n, p, world } = partida();
    p.do('open', 'caixa');
    p.use('cable_xarxa', 'router');
    expect(texts(p.use('auriculars_boto', 'diu'))).toContain('recanvi');
    p.use('auriculars', 'diu');
    p.use('auriculars', 'diu');
    expect(world.items('iri')).not.toContain('auriculars');
    expect(n.outfitOf('iri')).toBe('SenseAuriculars');
  });
});

function jugarPisAmbLinies(p: Parameters<typeof jugarPis>[0]) {
  const lines: { text: string }[] = [];
  const original = p.do.bind(p);
  p.do = ((...args: Parameters<typeof original>) => {
    const r = original(...args);
    lines.push(...r);
    return r;
  }) as typeof p.do;
  jugarPis(p, { sacrifici: 'auricular' });
  p.do = original;
  return lines;
}
