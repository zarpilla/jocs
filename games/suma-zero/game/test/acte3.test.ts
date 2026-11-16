/** L'Acte 3 jugat sencer, per tots els camins, amb una pista disponible a cada pas. */
import { describe, expect, it } from 'vitest';
import { jugarActe1, jugarActe2, jugarActe3, jugarDespatx, partida, texts } from './partida.js';

/** Una partida amb els actes 1 i 2 jugats: l'Iri al Llibre Major, amb el virus en marxa, i la Vet a seguretat. */
function ambElVirus(o: { aliats?: boolean } = {}) {
  const r = partida({ checkHints: true, fins: 'escapada' });
  jugarActe1(r.p, { entrepa: true, sacrifici: 'pizza' });
  jugarActe2(r.p, { aliats: o.aliats });
  return r;
}

describe('Acte 3 · camins', () => {
  it('sense aliats: la Vet distreu el Director sola, i el final és «Ni caos ni paradís»', () => {
    const { n, p } = ambElVirus();
    expect(p.room).toBe('bcmu_escombraries');
    jugarActe3(p);
    expect(n.flag('virus_aturat')).toBe(true);
    expect(n.flag('repartit')).toBe(false);
    expect(n.getVar('reinicis_mobil')).toBe(0);
    expect(n.resolveEnding()).toBe('final_base');
    // al bar del final, sense aliats, cap dels quatre (la colla de sempre no té condició: hi és sempre)
    const alBar = n.hotspotsIn('final_bar');
    expect(alBar.map((h) => h.id).sort()).toEqual(['ballester', 'neta', 'pons', 'rius', 'tele_apagada']);
    expect(alBar.some((h) => h.visible)).toBe(false);
    // en Diu, a la cistella; quan mossega el cable (una línia del final), damunt la barra i la tele s'apaga
    expect(n.placeOf('diu', 'final_bar')).toMatchObject({ x: 430 });
    const mossegada = n.ending('final_base').scene.find((l) => l.key === 'final.diu1')!;
    n.apply(mossegada.effects!);
    expect(n.placeOf('diu', 'final_bar')).toMatchObject({ x: 404 });
    expect(n.hotspotsIn('final_bar').find((h) => h.id === 'tele_apagada')?.visible).toBe(true);
    expect(n.outfitOf('vet')).toBe('');
    const estat = Object.fromEntries(n.quests().map((q) => [q.id, q.status]));
    expect(estat).toMatchObject({ acte3: 'completed', senyora_pons: 'failed' });
  });

  it('amb tots quatre aliats i repartint-ho tot: «La taula llarga»', () => {
    const { n, p } = ambElVirus({ aliats: true });
    jugarActe3(p, { pons: true, mobil: 'pons', repartir: true, neta: true });
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
    expect(n.flag('aliada_pons')).toBe(false);
    expect(n.resolveEnding()).toBe('final_taula');
  });

  it("el Director, després: «tornen a ser on eren» si es torna al banc; si es reparteix, «tothom té el mateix que jo»", () => {
    for (const repartir of [false, true]) {
      const { p } = ambElVirus({ aliats: true });
      jugarDespatx(p, { pons: true, mobil: 'pons', repartir });
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
    p.talk('pons', 'ue');
    p.do('use', 'porta');
    p.switchTo('iri');
    expect(n.activeHints()[0]).toBe('iri_contrasenya_mirar');
    p.talk('llibre');
    expect(n.flag('pista_contrasenya')).toBe(true);
    expect(n.activeHints()[0]).toBe(n.flag('sap_rockefeller') ? 'iri_contrasenya' : 'iri_gos');
  });
});

describe('Acte 3 · el mòbil del Director', () => {
  it('si l\'Iri demana el codi sense que la Vet el distregui, el Director el cancel·la i es torna a començar', () => {
    const { n, p } = ambElVirus();
    p.switchTo('vet');
    p.do('use', 'ascensor');
    p.talk('pons', 'ue');
    p.do('use', 'porta');
    p.switchTo('iri');
    p.talk('llibre', 'rockefeller');
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
    p.talk('pons', 'ue');
    p.do('use', 'porta');
    p.switchTo('iri');
    p.talk('llibre', 'rockefeller');
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
    p.talk('pons', 'ue');
    p.do('use', 'porta');
    p.switchTo('iri');
    expect(() => p.talk('llibre', 'rockefeller')).toThrow();
    expect(n.flag('pista_contrasenya')).toBe(true);
    p.switchTo('vet');
    expect(texts(p.do('look', 'foto'))).toContain('Rockefeller');
    p.switchTo('iri');
    p.talk('llibre', 'bonfill', 'rockefeller');
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
