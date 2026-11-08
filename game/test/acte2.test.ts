/**
 * Ferro-9, Acte 2 (primera part, «La comporta»), jugat sense gràfics: les dues rutes del guió per
 * aconseguir una palanca de dos metres a través d'una finestra on no hi passa res de més de 2 kg.
 */
import { describe, expect, it } from 'vitest';
import { estatFinestra } from '../logic/index.js';
import { jugarActe1, keys, partida, texts } from './partida.js';

const item = (id: string) => ({ kind: 'item' as const, id });

/** De la sortida de la cel·la fins que l'Iri sap quina palanca necessita la Vet. */
function finsMida(checkHints = true) {
  const s = partida({ checkHints });
  const { p, n } = s;
  jugarActe1(p);
  expect(p.room).toBe('gavina_passadis');
  expect(n.state.quests.acte2!.status).toBe('active');

  // ── Vet: troba l'hangar ──
  p.do('open', 'porta_hangar');
  expect(p.room).toBe('gavina_hangar');
  expect(texts(p.do('push', 'comporta'))).toContain('palanca');

  // ── Vet: recupera la clau anglesa i mesura l'encaix ──
  p.do('open', 'porta_passadis');
  p.do('open', 'porta_cella');
  expect(keys(p.do('pickUp', 'panell'))).toContain('sala.gavina_cella.panell.recuperar2');
  expect(p.inventory()).toContain('clau_anglesa');
  p.do('open', 'porta');
  p.do('pickUp', 'cartell');
  p.do('open', 'porta_hangar');
  expect(texts(p.use('clau_anglesa', 'comporta'))).toContain('Sis claus angleses i mitja');
  p.use('llapis_ulls', item('tros_cartell'));
  expect(p.inventory()).toContain('nota_mida');

  // ── Vet: ho envia (un sol pas) i l'Iri ho llegeix ──
  p.do('open', 'porta_passadis');
  p.do('open', 'porta_cella');
  expect(keys(p.use('nota_mida', 'panell'))).toEqual(['finestra.enviat']);
  expect(p.active).toBe('iri');
  expect(texts(p.do('look', item('nota_mida')))).toContain('dos metres');
  expect(n.state.quests.acte2!.objectives.mida).toBe(true);

  // ── Iri: al moll de càrrega ──
  p.goTo('fabrica_calderes');
  p.do('open', 'porta_moll');
  expect(p.room).toBe('fabrica_moll');
  return s;
}

/** L'Iri envia els tres trams i la Vet els munta i obre la comporta. */
function enviarTramsIObrir(s: ReturnType<typeof partida>) {
  const { p } = s;
  p.goTo('fabrica_calderes');
  p.goTo('fabrica_cambra');
  for (const n of [1, 2, 3]) {
    p.use(`tram_biga_${n}`, 'cambra');
    expect(p.active).toBe('vet');
    if (n < 3) p.switchTo('iri');
  }
  expect(texts(p.use('tram_biga_1', item('tram_biga_2')))).toContain('dos metres');
  expect(p.inventory()).toContain('biga_muntada');
  p.do('open', 'porta');
  p.do('open', 'porta_hangar');
  return texts(p.use('biga_muntada', 'comporta'));
}

describe('Ferro-9 · Acte 2 · La comporta', () => {
  it('ruta per peces: tres trams per la finestra, sense rastre (sempre amb alguna pista)', () => {
    const s = finsMida();
    const { p, n } = s;
    p.do('pickUp', 'serra');
    expect(texts(p.do('pickUp', 'biga_acer'))).toContain('capatàs'); // també la podria amagar...
    p.use('biga_acer', 'trapa');
    p.do('open', 'trapa'); // ...però s'ho repensa
    p.use('serra', item('biga_acer'));
    expect(p.inventory()).toEqual(expect.arrayContaining(['tram_biga_1', 'tram_biga_2', 'tram_biga_3']));
    expect(n.isHotspotVisible('fabrica_moll', 'biga_acer')).toBe(false);
    const obrir = enviarTramsIObrir(s);
    expect(obrir).toContain('llançadora');
    expect(n.flag('comporta_oberta')).toBe(true);
    expect(n.state.quests.acte2!.objectives.comporta).toBe(true);
    expect(n.isHotspotVisible('gavina_hangar', 'llancadora')).toBe(true);
    expect(n.getVar('sospita_brau')).toBe(1); // només la de l'Acte 1
    // Acte 1: 9 enceses. Aquí: la nota de la mida i els tres trams.
    expect(estatFinestra(n).enceses).toBe(24 - 9 - 1 - 3);
  });

  it('camí llarg amb ferro-9: arriba perfecta, però el Brau ho sabrà', () => {
    const { p, n } = finsMida();
    expect(texts(p.do('pickUp', 'biga_ferro9'))).toContain('Brau');
    expect(n.getVar('sospita_brau')).toBe(2);
    p.use('biga_ferro9', 'trapa');
    p.use('llapis', item('llibreta_torn'));
    p.goTo('fabrica_calderes');
    p.goTo('fabrica_cambra');
    p.use('nota_amagatall', 'cambra');
    expect(p.active).toBe('vet');
    // Sense llegir la nota, una placa qualsevol no diu res.
    p.do('open', 'porta');
    p.do('open', 'porta_hangar');
    expect(texts(p.do('open', 'placa_terra'))).toContain('qualsevol');
    p.do('look', item('nota_amagatall'));
    expect(texts(p.do('open', 'placa_terra'))).toContain('Ferro-9');
    expect(texts(p.use('biga_ferro9', 'comporta'))).toContain('llançadora');
    expect(n.flag('comporta_oberta')).toBe(true);
    expect(estatFinestra(n).enceses).toBe(24 - 9 - 1 - 1);
  });

  it("camí llarg amb acer: arriba rovell, i l'Iri ho torna a provar a trossos", () => {
    const s = finsMida();
    const { p, n } = s;
    p.do('pickUp', 'biga_acer');
    p.use('biga_acer', 'trapa');
    p.use('llapis', item('llibreta_torn'));
    p.goTo('fabrica_calderes');
    p.goTo('fabrica_cambra');
    p.use('nota_amagatall', 'cambra');
    p.do('look', item('nota_amagatall'));
    p.do('open', 'porta');
    p.do('open', 'porta_hangar');
    expect(texts(p.do('open', 'placa_terra'))).toContain('pols vermella');
    expect(p.inventory()).toContain('pols_rovell');
    // El rovell, cap a l'Iri.
    p.do('open', 'porta_passadis');
    p.do('open', 'porta_cella');
    p.use('pols_rovell', 'panell');
    expect(p.active).toBe('iri');
    expect(texts(p.do('look', item('pols_rovell')))).toContain('cent vint anys');
    // Recupera la biga del passat i la serra.
    p.goTo('fabrica_calderes');
    p.do('open', 'porta_moll');
    p.do('open', 'trapa');
    expect(p.inventory()).toContain('biga_acer');
    p.do('pickUp', 'serra');
    p.use('serra', item('biga_acer'));
    expect(p.inventory()).not.toContain('biga_acer');
    expect(enviarTramsIObrir(s)).toContain('llançadora');
    expect(n.flag('comporta_oberta')).toBe(true);
  });

  it('un tram sol no fa palanca, i dos tampoc', () => {
    const s = finsMida(false);
    const { p } = s;
    p.do('pickUp', 'serra');
    p.use('serra', 'biga_acer');
    p.goTo('fabrica_calderes');
    p.goTo('fabrica_cambra');
    p.use('tram_biga_1', 'cambra');
    p.switchTo('iri');
    p.use('tram_biga_2', 'cambra');
    expect(texts(p.use('tram_biga_1', item('tram_biga_2')))).toContain('me\'n falta un');
    p.do('open', 'porta');
    p.do('open', 'porta_hangar');
    expect(texts(p.use('tram_biga_1', 'comporta'))).toContain('tres');
  });
});
