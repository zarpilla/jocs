/** L'Acte 3 jugat sencer, per tots els camins, amb una pista disponible a cada pas. */
import { describe, expect, it } from 'vitest';
import { jugarActe1, jugarActe2, jugarActe3, jugarDespatx, partida, passarPons, texts } from './partida.js';

/** Una partida amb els actes 1 i 2 jugats: l'Iri al Llibre Major, amb el virus en marxa, i la Vet a seguretat. */
function ambElVirus(o: { aliats?: boolean } = {}) {
  const r = partida({ checkHints: true, fins: 'escapada' });
  jugarActe1(r.p, { entrepa: true, sacrifici: 'pizza' });
  jugarActe2(r.p, { aliats: o.aliats });
  return r;
}

describe('Acte 3 · camins', () => {
  it('només amb la Pons (cal escoltar-la per passar): la Vet distreu el Director sola, i el final és «Hores extres»', () => {
    const { n, p, world } = ambElVirus();
    expect(p.room).toBe('bcmu_escombraries');
    jugarActe3(p);
    expect(n.flag('virus_aturat')).toBe(true);
    expect(n.flag('repartit')).toBe(false);
    expect(n.getVar('reinicis_mobil')).toBe(0);
    expect(n.getVar('aliats')).toBe(1);
    expect(n.resolveEnding()).toBe('final_hores');
    // al bar del final, dels quatre aliats només la Pons (la colla de sempre no té condició: hi és sempre)
    const alBar = n.hotspotsIn('final_bar');
    expect(alBar.map((h) => h.id).sort()).toEqual(['ballester', 'neta', 'pons', 'rius', 'tele_apagada']);
    expect(alBar.filter((h) => h.visible).map((h) => h.id)).toEqual(['pons']);
    // en Diu, a la cistella; quan mossega el cable (una línia del final), al moble de la regleta, i la tele s'apaga
    expect(n.placeOf('diu', 'final_bar')).toMatchObject({ x: 573 });
    const mossegada = n.ending('final_hores').scene.find((l) => l.key === 'final.diu1')!;
    n.apply(mossegada.effects!);
    expect(n.placeOf('diu', 'final_bar')).toMatchObject({ x: 539 });
    expect(n.hotspotsIn('final_bar').find((h) => h.id === 'tele_apagada')?.visible).toBe(true);
    // Acaba al contenidor, de lluny; al bar del final (el motor hi entra amb qui juga), sense roba.
    expect(n.outfitOf('vet')).toBe('Lluny');
    world.enter('final_bar');
    expect(n.outfitOf('vet')).toBe('');
    const estat = Object.fromEntries(n.quests().map((q) => [q.id, q.status]));
    expect(estat).toMatchObject({ acte3: 'completed', senyora_pons: 'completed' });
  });

  it('repartir-ho tot passa per la cinemàtica del repartiment i, de tornada a la sala d\'escombraries, segueix el diàleg', () => {
    const { n, p } = ambElVirus({ aliats: true });
    const abans = p.transcript.length;
    jugarActe3(p, { mobil: 'pons', repartir: true, neta: true });
    const dit = p.transcript.slice(abans).join('\n');
    const ordre = ['COMPTE PONT → TOTS ELS COMPTES', 'Fase 3: repartir-ho tot', 'El mariner deixa la baieta',
      'a les dotze, cobra tothom', 'COMPTE ZERO', 'Ens trobem al carrer'];
    const llocs = ordre.map((t) => dit.indexOf(t));
    expect(llocs.every((i) => i >= 0), dit).toBe(true);
    expect([...llocs].sort((a, b) => a - b)).toEqual(llocs);
    expect(n.flag('virus_aturat')).toBe(true);
  });

  it('tornant-ho al banc no hi ha cinemàtica del repartiment', () => {
    const { n, p } = ambElVirus({ aliats: true });
    const abans = p.transcript.length;
    jugarActe3(p, { neta: true });
    expect(p.transcript.slice(abans).join('\n')).not.toContain('Fase 3');
    expect(n.flag('virus_aturat')).toBe(true);
  });

  it('amb tots quatre aliats i repartint-ho tot: «La taula llarga»', () => {
    const { n, p } = ambElVirus({ aliats: true });
    jugarActe3(p, { mobil: 'pons', repartir: true, neta: true });
    expect(n.getVar('aliats')).toBe(4);
    expect(n.flag('repartit')).toBe(true);
    expect(n.resolveEnding()).toBe('final_taula');
    // i al bar, tots quatre aliats a la taula
    expect(n.hotspotsIn('final_bar').filter((h) => h.id !== 'tele_apagada').every((h) => h.visible)).toBe(true);
    const escena = texts(n.ending('final_taula').scene);
    for (const t of ['taula llarga', 'Un tallat', 'Taula tres', 'fitxat a l\'hora', 'augment', 'tothom té el mateix', 'Contrasenya?']) expect(escena).toContain(t);
    // el bar, els crèdits i els postcrèdits, en aquest ordre; i el so de la mossegada d'en Diu
    const final = n.ending('final_taula');
    expect(final.scene.filter((l) => l.room).map((l) => l.room)).toEqual(['final_bar', 'credits', 'postcredits']);
    expect(final.scene.some((l) => l.sound === 'mossegada')).toBe(true);
    expect(final.text).toBe('Tot torna a començar.');
  });

  it('en Ballester immobilitza el Director i diu el compte de les nòmines', () => {
    const { n, p } = ambElVirus({ aliats: true });
    jugarActe3(p, { mobil: 'ballester', repartir: true, neta: true });
    expect(n.flag('ballester_compte')).toBe(true);
    expect(n.resolveEnding()).toBe('final_taula');
  });

  it("el Director, després: «tornen a ser on eren» si es torna al banc; si es reparteix, «tothom té el mateix que jo»", () => {
    for (const repartir of [false, true]) {
      const { p } = ambElVirus({ aliats: true });
      jugarDespatx(p, { mobil: 'pons', repartir });
      p.switchTo('vet');
      const dit = texts(p.do('talkTo', 'bonfill'));
      expect(dit).toContain(repartir ? 'Tothom té el mateix que jo' : 'tornen a ser on eren');
      expect(dit).not.toContain(repartir ? 'tornen a ser on eren' : 'Tothom té el mateix que jo');
    }
  });

  it('amb aliats però tornant-ho tot: «Hores extres»', () => {
    const { n, p } = ambElVirus({ aliats: true });
    jugarActe3(p, { neta: true });
    expect(n.resolveEnding()).toBe('final_hores');
    expect(texts(n.ending('final_hores').scene)).not.toContain('pensions del món');
  });
});

describe('Acte 3 · pistes', () => {
  it("la pista de la contrasenya no parla de «el meu millor amic» fins que l'Iri ho ha vist al Llibre Major", () => {
    const { n, p } = ambElVirus({ aliats: true });
    p.switchTo('vet');
    p.do('use', 'ascensor');
    passarPons(p);
    p.do('use', 'porta');
    p.switchTo('iri');
    expect(n.activeHints()[0]).toBe('iri_contrasenya_mirar');
    p.talk('llibre');
    expect(n.flag('pista_contrasenya')).toBe(true);
    expect(n.activeHints()[0]).toBe(!n.flag('sap_rockefeller') ? 'iri_gos' : n.flag('sap_any_gos') ? 'iri_contrasenya' : 'iri_any');
  });
});

describe('Acte 3 · el mòbil del Director', () => {
  it('si l\'Iri demana el codi sense que la Vet el distregui, el Director el cancel·la i es torna a començar', () => {
    const { n, p } = ambElVirus();
    p.switchTo('vet');
    p.do('use', 'ascensor');
    passarPons(p);
    p.do('use', 'porta');
    p.do('look', 'bol');
    p.switchTo('iri');
    p.talk('llibre', 'rockefeller_any');
    const lines = texts(p.do('use', 'llibre'));
    expect(lines).toContain('Intent d\'aturada no autoritzat');
    expect(n.flag('codi_demanat')).toBe(false);
    expect(n.flag('sync_mobil')).toBe(true);
    expect(n.getVar('codi_n')).toBe(1);
    // i ara bé, amb un codi nou
    p.switchTo('vet');
    p.talk('despatx', 'reunio');
    p.switchTo('iri');
    p.do('use', 'llibre');
    p.switchTo('vet');
    expect(texts(p.do('pickUp', 'mobil'))).toContain('2-8-0-5');
  });

  it('agafar el mòbil sense distreure el Director també el fa mirar', () => {
    const { n, p } = ambElVirus();
    p.switchTo('vet');
    p.do('use', 'ascensor');
    passarPons(p);
    p.do('use', 'porta');
    p.do('look', 'bol');
    p.switchTo('iri');
    p.talk('llibre', 'rockefeller_any');
    p.switchTo('vet');
    p.talk('despatx', 'gos'); // un sol torn de marge
    p.switchTo('iri');
    p.do('use', 'llibre'); // demana: tapat
    p.switchTo('vet');
    expect(texts(p.do('pickUp', 'mobil'))).toContain('Intent d\'aturada');
    expect(n.getVar('reinicis_mobil')).toBe(1);
  });

  it('sense la placa del retrat, el nom del gos surt al despatx (cap atzucac)', () => {
    const { n, p } = ambElVirus();
    n.apply({ setFlag: 'sap_rockefeller', value: false });
    p.switchTo('vet');
    p.do('use', 'ascensor');
    passarPons(p);
    p.do('use', 'porta');
    p.do('look', 'bol');
    p.switchTo('iri');
    expect(() => p.talk('llibre', 'rockefeller_any')).toThrow();
    expect(n.flag('pista_contrasenya')).toBe(true);
    p.switchTo('vet');
    expect(texts(p.do('look', 'foto'))).toContain('Rockefeller');
    p.switchTo('iri');
    p.talk('llibre', 'bonfill', 'rockefeller_any');
    expect(n.flag('contrasenya_ok')).toBe(true);
  });

  it("el nom del gos sol no n'hi ha prou: cal l'any del bol (030)", () => {
    const { n, p } = ambElVirus();
    p.switchTo('vet');
    p.do('use', 'ascensor');
    passarPons(p);
    p.do('use', 'porta');
    p.switchTo('iri');
    const pista = texts(p.talk('llibre', 'rockefeller', 'adeu'));
    expect(pista).not.toContain('Rockefeller2016');
    expect(pista).toContain('CONTRASENYA INCORRECTA. FORMAT REQUERIT: NOM I ANY, TOT JUNT. COM ELS ADULTS.');
    expect(n.flag('contrasenya_ok')).toBe(false);
    expect(n.activeHints()[0]).toBe('iri_any');
    expect(() => p.talk('llibre', 'rockefeller_any')).toThrow();
    p.switchTo('vet');
    expect(texts(p.do('look', 'bol'))).toContain('2016');
    p.switchTo('iri');
    p.talk('llibre', 'rockefeller_any');
    expect(n.flag('contrasenya_ok')).toBe(true);
  });

  it('la sincronia no comença fins que la Vet és al despatx', () => {
    const { n, p } = ambElVirus();
    expect(texts(p.do('use', 'llibre'))).toContain('la Vet no és amb ell');
    expect(n.flag('sync_mobil')).toBe(false);
  });
});

describe('Acte 3 · la sortida', () => {
  it('sense coixí no salta, i la porta de l\'escala és plena', () => {
    const { p } = ambElVirus();
    jugarDespatx(p);
    expect(texts(p.do('use', 'conducte'))).toContain('Primer provaré');
    p.do('use', 'porta');
    expect(texts(p.use('clau_llibre', 'porta_escala'))).toContain('plena de guardes');
    p.do('use', 'porta_neteja');
    expect(texts(p.do('use', 'conducte'))).toContain('Primer, coixí');
  });

  it('la Vet no pot obrir el contenidor fins que l\'Iri ha fet el coixí', () => {
    const { n, p } = ambElVirus();
    jugarDespatx(p);
    p.switchTo('vet');
    expect(n.activeHints()[0]).toBe('vet_baixar');
    p.do('use', 'porta');
    p.do('use', 'ascensor');
    expect(n.activeHints()[0]).toBe('vet_sortir'); // ja és al vestíbul: no «la porta gran és al vestíbul»
    p.do('use', 'sortida');
    expect(texts(p.do('open', 'contenidor'))).toContain('Encara no');
    expect(n.flag('escapada')).toBe(false);
  });

  it('si el Director va sospitar molt, la recepcionista la reconeix i l\'ha d\'enredar', () => {
    const { n, p } = ambElVirus();
    n.apply({ setVar: 'sospita_max', value: 60 });
    jugarDespatx(p);
    p.switchTo('vet');
    p.do('use', 'porta');
    p.do('use', 'ascensor');
    expect(texts(p.do('use', 'sortida'))).toContain('no em treu l\'ull');
    p.talk('recepcionista', 'altra', 'font');
    p.do('use', 'sortida');
    expect(p.room).toBe('bcmu_contenidor');
  });
});
