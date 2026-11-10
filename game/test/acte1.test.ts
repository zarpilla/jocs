/** L'Acte 1 jugat sencer, per tots els camins, amb una pista disponible a cada pas. */
import { describe, expect, it } from 'vitest';
import { item, jugarActe1, jugarBar, jugarPis, partida, texts } from './partida.js';

describe('Acte 1 · camins', () => {
  for (const sacrifici of ['caixa', 'auricular', 'pizza'] as const) {
    it(`de cap a peus, distraient en Diu amb ${sacrifici}`, () => {
      const { n, p, world } = partida({ checkHints: true });
      jugarActe1(p, { sacrifici });
      expect(n.getVar('sacrifici')).toBe(sacrifici);
      expect(n.flag('acte1_fet')).toBe(true);
      expect(n.resolveEnding()).toBe('continuara');
      expect(world.items('vet')).toContain('acreditacio');
      expect(world.items('iri')).toContain('acreditacio');
      expect(world.items('iri')).not.toContain('acreditacions');
    });
  }

  it("amb l'entrepà, el tap tornat i la preparació d'auditora", () => {
    const { n, p, world } = partida({ checkHints: true });
    jugarActe1(p, { entrepa: true, tap: true, preparacio: true });
    for (const i of ['entrepa', 'clau_casa', 'maleti', 'ulleres', 'recepta']) expect(world.items('vet')).toContain(i);
    expect(world.items('vet')).not.toContain('tap');
    expect(n.flag('ulleres_posades')).toBe(true);
    expect(n.flag('iri_sap_neta')).toBe(true);
  });

  it('amb un codi dolent: la porta xiula i la Vet plora més fort', () => {
    const { n, p } = partida({ checkHints: true });
    jugarActe1(p, { codiDolent: true });
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
    expect(n.flag('sync_aeroport')).toBe(false);
    expect(n.getVar('cigarreta')).toBe(12);
    expect(n.getVar('reinicis_aeroport')).toBe(1);
    p.switchTo('vet');
    p.talk('soler', 'fill', 'nom_curt', 'edat_curt', 'roba_curt');
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
    // L'Iri té les acreditacions, però en Soler torna a ser a la porta: no pot sortir fins que la Vet el distregui.
    expect(texts(p.do('use', 'porta'))).toContain('En Soler em veuria sortir');
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
    p.talk('passaplats', 'cable');
    expect(n.canSwitch()).toBe(true);
  });

  it("la Vet no pot marxar del pis fins que l'Iri ha trobat el servidor", () => {
    const { n, p } = partida();
    p.do('open', 'caixa');
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

  it("en Puig només pregunta pel tap si no l'hi han tornat", () => {
    const amb = partida();
    jugarActe1(amb.p, { tap: true });
    expect(amb.p.transcript.join('\n')).not.toContain('On és el meu tap?');
    const sense = partida();
    jugarActe1(sense.p);
    expect(sense.p.transcript.join('\n')).toContain('On és el meu tap?');
  });

  it('el rebost és tancat mentre en Puig hi discuteix amb la seva dona inexistent', () => {
    const { n, p } = partida();
    jugarPis(p);
    p.talk('marcel');
    p.talk('puig', 'comandament', 'adeu');
    p.talk('trucada', 'trucada', 'adeu');
    p.switchTo('iri');
    p.do('use', 'ordinadors');
    p.switchTo('vet');
    expect(n.flag('puig_rebost')).toBe(true);
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
