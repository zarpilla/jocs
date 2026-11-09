/**
 * Ferro-9, Acte 2 (primera part, «La comporta»), jugat sense gràfics: les dues rutes del guió per
 * aconseguir una palanca de dos metres a través d'una finestra on no hi passa res de més de 2 kg.
 */
import { describe, expect, it } from 'vitest';
import { estatFinestra } from '../logic/index.js';
import { jugarActe1, keys, partida, texts } from './partida.js';

const item = (id: string) => ({ kind: 'item' as const, id });
/** Els sons de les línies (el motor els fa sonar en dir-les). */
const sounds = (lines: { sound?: string }[]) => lines.flatMap((l) => (l.sound ? [l.sound] : []));

/** De la sortida de la cel·la fins que l'Iri sap quina palanca necessita la Vet. */
function finsMida(checkHints = true, fins?: string) {
  const s = partida({ checkHints, fins });
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

  // ── Iri: abans de la biga, la marca del pilar 7 (sense gastar cap encesa) ──
  expect(texts(p.do('pickUp', 'biga_acer'))).toContain('pilar 7');
  p.do('pickUp', 'llima');
  expect(texts(p.use('llima', 'pilar'))).toContain('rebut');
  expect(n.flag('marca_pilar')).toBe(true);
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
    // En tornar a l'hangar, la Vet hi troba la marca de l'Iri: el passat ha canviat el present sense la finestra.
    expect(n.flag('vet_ha_vist_marca')).toBe(true);
    expect(texts(p.do('look', 'pilar'))).toContain('bústia');
    expect(n.getVar('sospita_sic')).toBe(1); // només la de l'Acte 1
    // Acte 1: 9 enceses. Aquí: la nota de la mida i els tres trams.
    expect(estatFinestra(n).enceses).toBe(24 - 9 - 1 - 3);
  });

  it('camí llarg amb ferro-9: arriba perfecta, però el Sic ho sabrà', () => {
    const { p, n } = finsMida();
    expect(texts(p.do('pickUp', 'biga_ferro9'))).toContain('Sic');
    expect(n.getVar('sospita_sic')).toBe(2);
    p.use('biga_ferro9', 'trapa');
    p.use('llapis', item('llibreta_torn'));
    p.goTo('fabrica_calderes');
    p.goTo('fabrica_cambra');
    p.use('nota_amagatall', 'cambra');
    expect(p.active).toBe('vet');
    // Sense llegir la nota, una reixa qualsevol no diu res.
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

/** Primera part sencera (per peces): la Vet acaba al moll de l'hangar amb la comporta oberta. */
function finsComporta(fins = 'pany_sonic_obert') {
  const s = finsMida(true, fins);
  s.p.do('pickUp', 'serra');
  s.p.use('serra', 'biga_acer');
  enviarTramsIObrir(s);
  expect(s.n.flag('comporta_oberta')).toBe(true);
  return s;
}

/** L'Iri, amb la molla ja llegida, aconsegueix un diapasó del Cargol (formulari per triplicat). */
function demanarDiapaso(p: ReturnType<typeof partida>['p']) {
  p.goTo('fabrica_calderes');
  p.do('pickUp', 'tauler');
  p.use('segell', item('formulari_27b'));
  p.use('segell', item('formulari_segellat'));
  p.goTo('fabrica_magatzem');
  return p.talk('cargol', 'diapaso');
}

describe('Ferro-9 · Acte 2 · El diapasó', () => {
  it('la nota del pany viatja dins una molla i torna dins un diapasó (sempre amb alguna pista)', () => {
    const { p, n } = finsComporta();
    // ── Vet: el pany sònic ──
    expect(n.isHotspotVisible('gavina_hangar', 'pany')).toBe(false); // encara no l'ha vist
    p.do('look', 'llancadora');
    expect(texts(p.do('push', 'pany'))).toContain('nnnnng');
    expect(sounds(p.do('push', 'pany'))).toEqual(['pany']);
    p.do('open', 'porta_passadis');
    p.do('open', 'porta_cella');
    p.do('pickUp', 'llitera');
    expect(p.inventory()).toContain('molla');
    p.do('open', 'porta');
    p.do('open', 'porta_hangar');
    // ── Vet: afina la molla ──
    expect(texts(p.use('molla', 'pany'))).toContain('més greu');
    // Se sent d'oïda: el pany i després la molla, a la tensió d'ara (comença a 1; el pany és la 3).
    expect(sounds(p.use('molla', 'pany'))).toEqual(['pany_molla_1']);
    expect(sounds(p.do('pull', item('molla')))).toEqual(['molla_2']);
    for (let i = 0; i < 2; i++) p.do('pull', item('molla'));
    expect(texts(p.use('molla', 'pany'))).toContain('més aguda');
    p.do('push', item('molla'));
    expect(texts(p.use('molla', 'pany'))).toContain('mateixa nota');
    expect(texts(p.do('pull', item('molla')))).toContain('no la toco');
    // ── Vet: l'envia ──
    p.do('open', 'porta_passadis');
    p.do('open', 'porta_cella');
    p.use('molla', 'panell');
    expect(p.active).toBe('iri');
    expect(texts(p.do('look', item('molla')))).toContain('diapasó');
    // ── Iri: el diapasó, amb paperassa ──
    expect(texts(demanarDiapaso(p))).toContain('Diapasó de ferro-9');
    expect(p.inventory()).toContain('diapaso');
    p.goTo('fabrica_calderes');
    p.do('open', 'porta_moll');
    p.use('llima', item('diapaso'));
    expect(texts(p.use('diapaso', item('molla')))).toContain('més greu');
    expect(sounds(p.use('diapaso', item('molla')))).toEqual(['molla_diapaso_1']);
    p.use('llima', item('diapaso'));
    expect(texts(p.use('diapaso', item('molla')))).toContain('mateixa nota');
    // ── Iri: l'envia; Vet: obre el pany ──
    p.goTo('fabrica_calderes');
    p.goTo('fabrica_cambra');
    p.use('diapaso', 'cambra');
    expect(p.active).toBe('vet');
    p.do('open', 'porta');
    p.do('open', 'porta_hangar');
    expect(texts(p.use('diapaso', 'pany'))).toContain('Clac');
    expect(n.flag('pany_sonic_obert')).toBe(true);
    expect(n.state.quests.acte2!.objectives.diapaso).toBe(true);
    expect(estatFinestra(n).enceses).toBe(24 - 9 - 1 - 3 - 2);
  });

  it('si l\'Iri llima de més, el diapasó xiula i n\'ha de demanar un altre', () => {
    const { p, n } = finsComporta();
    p.do('look', 'llancadora');
    p.do('push', 'pany');
    p.do('open', 'porta_passadis');
    p.do('open', 'porta_cella');
    p.do('pickUp', 'llitera');
    for (let i = 0; i < 2; i++) p.do('pull', item('molla'));
    p.do('open', 'porta');
    p.do('open', 'porta_hangar');
    p.use('molla', 'pany');
    p.do('open', 'porta_passadis');
    p.do('open', 'porta_cella');
    p.use('molla', 'panell');
    p.do('look', item('molla'));
    demanarDiapaso(p);
    p.goTo('fabrica_calderes');
    p.do('open', 'porta_moll');
    for (let i = 0; i < 2; i++) p.use('llima', item('diapaso'));
    expect(texts(p.use('llima', item('diapaso')))).toContain('tetera');
    expect(p.inventory()).toContain('diapaso_espatllat');
    expect(texts(p.talk('cargol', 'diapaso'))).toContain('per triplicat'); // sense formulari
    expect(p.inventory()).not.toContain('diapaso');
    expect(texts(demanarDiapaso(p))).toContain('xiulava');
    expect(p.inventory()).toContain('diapaso');
    expect(p.inventory()).not.toContain('diapaso_espatllat');
    expect(n.getVar('diapaso_to')).toBe(0);
  });
});

/** Fins a la porta de la llançadora oberta, per la ruta curta de cada part. */
function finsDiapaso(fins = 'motor_engegat') {
  const s = finsComporta(fins);
  const { p } = s;
  p.do('look', 'llancadora');
  p.do('push', 'pany');
  p.do('open', 'porta_passadis');
  p.do('open', 'porta_cella');
  p.do('pickUp', 'llitera');
  for (let i = 0; i < 2; i++) p.do('pull', item('molla'));
  p.do('open', 'porta');
  p.do('open', 'porta_hangar');
  p.use('molla', 'pany');
  p.do('open', 'porta_passadis');
  p.do('open', 'porta_cella');
  p.use('molla', 'panell');
  p.do('look', item('molla'));
  demanarDiapaso(p);
  p.goTo('fabrica_calderes');
  p.do('open', 'porta_moll');
  for (let i = 0; i < 2; i++) p.use('llima', item('diapaso'));
  p.use('diapaso', item('molla'));
  p.goTo('fabrica_calderes');
  p.goTo('fabrica_cambra');
  p.use('diapaso', 'cambra');
  p.do('open', 'porta');
  p.do('open', 'porta_hangar');
  p.use('diapaso', 'pany');
  expect(s.n.flag('pany_sonic_obert')).toBe(true);
  return s;
}

/** La Vet escriu en un tros nou del cartell i ho envia des de la cel·la (acaba amb l'Iri). */
function escriureIEnviar(p: ReturnType<typeof partida>['p'], nota: string) {
  p.do('open', 'porta_passadis');
  p.do('pickUp', 'cartell');
  p.use('llapis_ulls', item('tros_cartell'));
  expect(p.inventory()).toContain(nota);
  p.do('open', 'porta_cella');
  p.use(nota, 'panell');
  expect(p.active).toBe('iri');
}

describe('Ferro-9 · Acte 2 · La vàlvula', () => {
  it('massa pressió inunda el present, i el reajust ho arregla (sempre amb alguna pista)', () => {
    const { p, n } = finsDiapaso();
    expect(texts(p.do('push', 'llancadora'))).toContain('no té pressió');
    expect(texts(p.do('look', 'conducte'))).toContain('zero');
    // ── Vet → Iri: el conducte ──
    escriureIEnviar(p, 'nota_pressio');
    expect(texts(p.do('look', item('nota_pressio')))).toContain('cent vint anys');
    p.goTo('fabrica_calderes');
    p.do('open', 'porta_moll');
    expect(texts(p.do('close', 'conducte'))).toContain('del tot');
    // ── Vet: el reajust (mal de cap i inundació) ──
    p.switchTo('vet');
    p.do('open', 'porta');
    expect(texts(p.do('open', 'porta_hangar'))).toContain("ple d'aigua");
    expect(texts(p.do('look', 'conducte'))).toContain('Rebentat');
    expect(texts(p.do('push', 'llancadora'))).toContain("s'escapa");
    expect(texts(p.do('open', 'escala'))).toContain('banyador');
    // Un camí que s'obre: la caixa de l'arxiu sura.
    p.do('pickUp', 'caixa_flotant');
    expect(texts(p.do('look', item('fitxa_mira')))).toContain('Potser es coneixen');
    expect(n.isHotspotVisible('gavina_hangar', 'caixa_flotant')).toBe(false);
    // ── Vet → Iri: MASSA ──
    escriureIEnviar(p, 'nota_massa');
    expect(texts(p.do('look', item('nota_massa')))).toContain('una mica');
    p.goTo('fabrica_calderes');
    p.do('open', 'porta_moll');
    p.do('open', 'conducte');
    expect(n.getVar('valvula')).toBe('mig');
    // ── Vet: un altre reajust, i engega ──
    p.switchTo('vet');
    p.do('open', 'porta');
    expect(texts(p.do('open', 'porta_hangar'))).toContain('me\'n recordo');
    expect(texts(p.do('push', 'llancadora'))).toContain('arrenca');
    expect(n.flag('motor_engegat')).toBe(true);
    expect(n.state.quests.acte2!.objectives.pressio).toBe(true);
    expect(n.state.quests.acte2!.objectives.components).toBe(true);
    expect(n.state.quests.acte2!.status).toBe('active'); // queda l'arxiu
    expect(estatFinestra(n).enceses).toBe(24 - 9 - 1 - 3 - 2 - 2);
  });

  it('la fitxa de la Mira depèn del passat: si el Sic sospita, diu que la van acomiadar', () => {
    const { p, n } = finsDiapaso();
    escriureIEnviar(p, 'nota_pressio');
    p.do('look', item('nota_pressio'));
    p.goTo('fabrica_calderes');
    p.do('open', 'porta_moll');
    p.do('close', 'conducte');
    p.switchTo('vet');
    p.do('open', 'porta');
    p.do('open', 'porta_hangar');
    p.do('pickUp', 'caixa_flotant');
    n.apply({ addVar: 'sospita_sic', amount: 1 }); // com si l'Iri hagués robat la biga de ferro-9
    expect(texts(p.do('look', item('fitxa_mira')))).toContain('Acomiadada');
  });

  it("sense tocar la vàlvula, o tornant-la a obrir del tot, la llançadora no engega", () => {
    const { p, n } = finsDiapaso();
    escriureIEnviar(p, 'nota_pressio');
    p.do('look', item('nota_pressio'));
    p.goTo('fabrica_calderes');
    p.do('open', 'porta_moll');
    p.do('close', 'conducte');
    p.do('open', 'conducte');
    p.do('open', 'conducte');
    expect(n.getVar('valvula')).toBe('oberta');
    p.switchTo('vet');
    p.do('open', 'porta');
    p.do('open', 'porta_hangar');
    expect(texts(p.do('push', 'llancadora'))).toContain('no té pressió');
    expect(n.flag('motor_engegat')).toBe(false);
  });
});

/** Fins a la llançadora engegada (la ruta curta de cada part). */
function finsMotor(fins = 'acte2_acabat') {
  const s = finsDiapaso(fins);
  const { p } = s;
  escriureIEnviar(p, 'nota_pressio');
  p.do('look', item('nota_pressio'));
  p.goTo('fabrica_calderes');
  p.do('open', 'porta_moll');
  p.do('close', 'conducte');
  p.switchTo('vet');
  p.do('open', 'porta');
  p.do('open', 'porta_hangar');
  escriureIEnviar(p, 'nota_massa');
  p.do('look', item('nota_massa'));
  p.goTo('fabrica_calderes');
  p.do('open', 'porta_moll');
  p.do('open', 'conducte');
  p.switchTo('vet');
  p.do('open', 'porta');
  p.do('open', 'porta_hangar');
  p.do('push', 'llancadora');
  expect(s.n.flag('motor_engegat')).toBe(true);
  return s;
}

/** L'Iri roba els plànols del despatx (amb un altre imant del Cargol). */
function robarPlanols(p: ReturnType<typeof partida>['p']) {
  p.goTo('fabrica_magatzem');
  p.do('open', 'porta_despatx');
  expect(texts(p.do('open', 'calaix'))).toContain('M-3');
  p.goTo('fabrica_calderes');
  p.do('pickUp', 'tauler');
  p.use('segell', item('formulari_27b'));
  p.use('segell', item('formulari_segellat'));
  p.goTo('fabrica_magatzem');
  expect(texts(p.talk('cargol', 'imant2'))).toContain('altre imant');
  p.do('open', 'porta_despatx');
  expect(texts(p.use('imant_ferro9', 'calaix'))).toContain('Plànols');
  expect(texts(p.do('look', item('planols')))).toContain('em va triar');
}

describe("Ferro-9 · Acte 2 · L'arxiu i el despatx", () => {
  it("l'arxiu, la carta d'en Mos i els noms: fins al final de l'acte (sempre amb alguna pista)", () => {
    const { p, n } = finsMotor();
    // ── Vet: l'arxiu ──
    expect(texts(p.do('open', 'escala'))).toContain('cadena');
    p.use('clau_anglesa', 'escala');
    p.do('open', 'escala');
    expect(p.room).toBe('gavina_arxiu');
    expect(n.state.quests.acte2!.objectives.arxiu).toBe(true);
    expect(texts(p.do('look', 'expedient_iri'))).toContain('tres dies');
    expect(texts(p.do('look', 'planols'))).toContain('sincronitzadors');
    p.do('open', 'arxivador');
    expect(p.inventory()).toContain('carta_mos');
    // ── Vet: la carta, a en Mos ──
    p.do('open', 'escala_hangar');
    p.do('open', 'porta_passadis');
    p.do('open', 'porta_cella');
    expect(texts(p.use('carta_mos', 'mos'))).toContain('no els reciclen');
    expect(n.state.quests.carta_mos!.status).toBe('completed');
    // ── Els noms ──
    p.do('open', 'porta');
    p.do('pickUp', 'cartell');
    p.use('llapis_ulls', item('tros_cartell'));
    p.do('open', 'porta_cella');
    p.use('nota_vet_nom', 'panell');
    expect(p.active).toBe('iri');
    expect(texts(p.do('look', item('nota_vet_nom')))).toContain('Es diu Vet');
    p.use('llapis', item('llibreta_torn'));
    p.goTo('fabrica_calderes');
    p.goTo('fabrica_cambra');
    p.use('nota_iri_nom', 'cambra');
    expect(p.active).toBe('vet');
    expect(texts(p.do('look', item('nota_iri_nom')))).toContain("FI DE L'ACTE 2");
    expect(n.state.quests.acte2!.status).toBe('completed');
    expect(estatFinestra(n).enceses).toBe(24 - 9 - 1 - 3 - 2 - 2 - 2);
  });

  it("els plànols del despatx fan que el Sic acusi la Mira; falsificar l'inventari la salva, i l'arxiu ho recorda", () => {
    const { p, n } = finsMotor();
    p.switchTo('iri');
    robarPlanols(p);
    expect(n.getVar('sospita_sic')).toBe(2);
    expect(texts(p.do('look', 'expedient_sic'))).toContain('M. Alsina');
    expect(n.state.quests.salvar_mira!.status).toBe('active');
    p.use('segell', 'llibre_inventari');
    expect(n.flag('mira_salvada')).toBe(true);
    expect(n.getVar('sospita_sic')).toBe(0);
    expect(n.state.quests.salvar_mira!.status).toBe('completed');
    expect(texts(p.do('look', 'expedient_sic'))).toContain('rovell');
    // Al present, l'arxiu ha canviat.
    p.switchTo('vet');
    p.use('clau_anglesa', 'escala');
    p.do('open', 'escala');
    expect(texts(p.do('look', 'arxivador'))).toContain('besneta');
  });

  it("si la Mira no se salva, l'arxiu la recorda condemnada; si l'Iri confessa, el seu expedient ho diu", () => {
    const s = finsMotor();
    const { p, n } = s;
    p.switchTo('iri');
    robarPlanols(p);
    p.do('look', 'expedient_sic');
    p.switchTo('vet');
    p.use('clau_anglesa', 'escala');
    p.do('open', 'escala');
    expect(texts(p.do('look', 'arxivador'))).toContain('Condemnada');
    p.switchTo('iri');
    expect(texts(p.use('llapis', 'expedient_sic'))).toContain('Ho vaig fer jo');
    expect(n.flag('mira_salvada')).toBe(true);
    p.switchTo('vet');
    expect(texts(p.do('look', 'expedient_iri'))).toContain('confessió');
    expect(texts(p.do('look', 'arxivador'))).toContain('besneta');
  });
});
