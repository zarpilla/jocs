/**
 * Ferro-9, Acte 1, jugat de cap a peus sense gràfics.
 * Si un canvi al guió trenca la història, aquest test ho diu.
 */
import { describe, expect, it } from 'vitest';
import { HeadlessPlayer, MemoryWorld, Narrative, validateContent } from '@aventura/narrative-core';
import { content, locales } from '../index.js';
import { GAME_ACTIONS, GAME_TEXT_KEYS, estatFinestra, installGameLogic } from '../logic/index.js';

function start(opts: { checkHints?: boolean } = {}) {
  const world = new MemoryWorld();
  const n = new Narrative({ content, locales, world });
  installGameLogic(n);
  const player = new HeadlessPlayer(n, world);
  player.newGame();
  // Opcional: després de cada acció, el jugador ha de tenir alguna pista disponible.
  const p = !opts.checkHints ? player : new Proxy(player, {
    get(target, prop, receiver) {
      const value = Reflect.get(target, prop, receiver);
      if (typeof value !== 'function' || !['do', 'use', 'talk', 'goTo', 'switchTo'].includes(String(prop))) return value;
      return (...args: unknown[]) => {
        const result = (value as (...a: unknown[]) => unknown).apply(target, args);
        if (!n.flag('acte1_acabat')) {
          // Les pistes depenen de la protagonista: n'ha de tenir alguna l'una o l'altra.
          const any = n.activeHints().length > 0 || otherHasHint(n, world);
          expect(any, `Sense pistes després de ${String(prop)}(${JSON.stringify(args)})`).toBe(true);
        }
        return result;
      };
    },
  });
  return { n, p, world };
}

function otherHasHint(n: Narrative, world: MemoryWorld) {
  const current = world.active;
  const other = n.content.manifest.protagonists.find((x) => x !== current)!;
  world.active = other;
  const has = n.activeHints().length > 0;
  world.active = current;
  return has;
}

const keys = (lines: { key: string }[]) => lines.map((l) => l.key);
const texts = (lines: { text: string }[]) => lines.map((l) => l.text).join(' ');

/** Juga fins que la Vet ha rebut la clau anglesa i ha arreglat el panell. */
function finsPanellReparat() {
  const s = start();
  const { p } = s;
  p.do('pickUp', 'tauler');
  p.goTo('fabrica_magatzem');
  p.do('pickUp', 'plomall');
  p.goTo('fabrica_calderes');
  p.use('plomall', 'capatas');
  p.do('pickUp', 'segell');
  p.use('segell', { kind: 'item', id: 'formulari_27b' });
  p.goTo('fabrica_magatzem');
  p.talk('cargol', 'clau');
  p.goTo('fabrica_calderes');
  p.use('clau_cambra', 'porta_cambra');
  p.use('clau_anglesa', 'palanca'); // → canvia a la Vet
  p.do('push', 'panell');
  p.use('clau_anglesa', 'panell');
  p.use('clau_anglesa', 'panell');
  return s;
}

describe('Ferro-9 · contingut', () => {
  it('és vàlid i no té textos sense traduir', () => {
    const issues = validateContent(content, locales, { actions: GAME_ACTIONS, textKeys: GAME_TEXT_KEYS });
    expect(issues).toEqual([]);
  });
});

describe('Ferro-9 · Acte 1', () => {
  it('comença amb l\'Iri al torn de nit i la missió activa', () => {
    const { p, n } = start();
    expect(p.active).toBe('iri');
    expect(p.room).toBe('fabrica_calderes');
    expect(p.inventory().sort()).toEqual(['clau_anglesa', 'llapis', 'llibreta_torn']);
    expect(n.state.quests.acte1!.status).toBe('active');
    expect(n.requestHint()!.text).toContain('Cargol');
  });

  it('partida completa: de la primera alarma a fora de la cel·la (sempre amb alguna pista)', () => {
    const { p, n } = start({ checkHints: true });

    // ── Iri: formulari, segell, clau de la cambra ──
    expect(texts(p.do('open', 'porta_cambra'))).toContain('Tancada');
    p.do('pickUp', 'tauler');
    p.goTo('fabrica_magatzem');
    expect(texts(p.talk('cargol', 'clau'))).toContain('no està segellat');
    p.do('pickUp', 'plomall');
    p.goTo('fabrica_calderes');
    expect(texts(p.do('pull', 'capatas'))).toContain('més fort');
    expect(n.isHotspotVisible('fabrica_calderes', 'segell')).toBe(false);
    expect(n.appearanceOf('capatas')).toBeNull(); // dorm amb el segell a les mans
    p.use('plomall', 'capatas');
    expect(n.isHotspotVisible('fabrica_calderes', 'segell')).toBe(true);
    expect(n.appearanceOf('capatas')).toBe('DormSenseSegell');
    p.do('pickUp', 'segell');
    p.use('segell', { kind: 'item', id: 'formulari_27b' });
    expect(p.inventory()).toContain('formulari_segellat');
    p.goTo('fabrica_magatzem');
    p.talk('cargol', 'clau', 'dia');
    expect(p.inventory()).toContain('clau_cambra');
    expect(n.remembers('cargol', 'formulari_acceptat')).toBe(1);
    expect(n.relation('cargol')).toBe(2);

    // ── Iri: la cambra i l'accident ──
    p.goTo('fabrica_calderes');
    p.use('clau_cambra', 'porta_cambra');
    expect(p.room).toBe('fabrica_cambra');
    expect(texts(p.do('pull', 'palanca'))).toContain('encallada');
    const accident = p.use('clau_anglesa', 'palanca');
    expect(texts(accident)).toContain('cau dins la cambra');
    expect(estatFinestra(n).armada).toBe('iri');

    // ── Canvi automàtic a la Vet ──
    expect(p.active).toBe('vet');
    expect(p.room).toBe('gavina_cella');
    expect(texts(accident)).toContain('tres dies');

    // ── Vet: el cop de puny (sincronia per accident) ──
    const cop = p.do('push', 'panell');
    expect(keys(cop)).toContain('finestra.rebut');
    expect(p.inventory()).toEqual(['clau_anglesa']);
    expect(n.state.quests.acte1!.objectives.primera_transferencia).toBe(true);

    // ── Vet: arreglar el panell ──
    p.use('clau_anglesa', 'panell');
    p.use('clau_anglesa', 'panell');
    expect(n.flag('panell_vet_reparat')).toBe(true);

    // ── Vet: la finestra rebutja el que no pot passar ──
    p.do('pickUp', 'escarabat');
    p.do('pickUp', 'safata');
    expect(keys(p.use('escarabat', 'panell'))).toEqual(['finestra.rebuig.viu']);
    expect(keys(p.use('sopa', 'panell'))).toEqual(['finestra.rebuig.liquid']);

    // ── Vet: en Mos i el llapis d'ulls ──
    p.do('pickUp', 'avis');
    p.talk('mos', 'familia', 'llapis_demanar', 'elogiar');
    expect(p.inventory()).toContain('llapis_ulls');
    expect(n.state.quests.carta_mos!.status).toBe('active');
    p.use('llapis_ulls', { kind: 'item', id: 'avis_reciclatge' });
    p.use('nota_vet', 'panell');
    p.do('push', 'panell');
    expect(estatFinestra(n).armada).toBe('vet');
    expect(n.requestHint()!.level).toBe(1);
    expect(n.requestHint()!.text).toContain("l'Iri"); // el segon nivell és explícit

    // ── Iri: rep la nota, la llegeix i respon ──
    const tornada = p.switchTo('iri');
    expect(texts(tornada)).toContain('parpelleja');
    const rebuda = p.do('push', 'boto');
    expect(p.inventory()).toContain('nota_vet');
    // Primer enviament fet a mà: l'Iri deixa la cambra sincronitzada.
    expect(keys(rebuda)).toContain('finestra.automatica');
    expect(n.flag('sincronia_automatica')).toBe(true);
    expect(texts(p.do('look', { kind: 'item', id: 'nota_vet' }))).toContain('brutal-plus');
    p.use('llapis', { kind: 'item', id: 'llibreta_torn' });
    // Des d'ara, posar-ho a la cambra ho fa tot: s'envia i canviem a l'altra banda.
    expect(keys(p.use('nota_iri', 'cambra'))).toEqual(['finestra.enviat']);

    // ── Vet: entén que són en temps diferents ──
    expect(p.active).toBe('vet');
    expect(p.inventory()).toContain('nota_iri');
    const lectura = texts(p.do('look', { kind: 'item', id: 'nota_iri' }));
    expect(lectura).toContain('cent vint anys');
    // El muntatge de correspondència: quatre notes més, sense ritual.
    expect(lectura).toContain('Un full en blanc');
    expect(n.flag('sap_que_es_temps')).toBe(true);
    expect(texts(p.do('look', { kind: 'item', id: 'nota_iri' }))).not.toContain('Un full en blanc');

    // ── Vet: dibuixa el pany ──
    p.do('look', 'porta');
    p.do('pickUp', 'llitera');
    p.use('llapis_ulls', { kind: 'item', id: 'fullet_reeducacio' });
    p.use('nota_pany', 'panell');

    // ── Iri: l'imant, amb el formulari per triplicat ──
    expect(p.active).toBe('iri');
    p.do('look', { kind: 'item', id: 'nota_pany' });
    expect(n.flag('iri_sap_pany')).toBe(true);
    p.goTo('fabrica_calderes');
    p.do('pickUp', 'tauler');
    p.goTo('fabrica_magatzem');
    expect(texts(p.talk('cargol', 'imant'))).toContain('per triplicat');
    p.use('segell', { kind: 'item', id: 'formulari_27b' });
    p.use('segell', { kind: 'item', id: 'formulari_segellat' });
    const imant = p.talk('cargol', 'imant');
    expect(keys(imant)[0]).toBe('dlg.cargol.hola_amiga'); // el Cargol la recorda
    expect(p.inventory()).toContain('imant_ferro9');
    p.goTo('fabrica_calderes');
    p.goTo('fabrica_cambra');
    p.use('imant_ferro9', 'cambra');

    // ── Vet: surt de la cel·la ──
    expect(p.active).toBe('vet');
    const sortida = p.use('imant_ferro9', 'porta');
    expect(p.room).toBe('gavina_passadis');
    expect(texts(sortida)).toContain("FI DE L'ACTE 1");
    // La porta queda oberta: es pot tornar a la cel·la i sortir sense imant.
    p.do('open', 'porta_cella');
    expect(p.room).toBe('gavina_cella');
    expect(texts(p.do('open', 'porta'))).not.toContain("FI DE L'ACTE 1");
    expect(p.room).toBe('gavina_passadis');
    expect(n.state.quests.acte1!.status).toBe('completed');
    expect(n.getVar('sospita_brau')).toBe(1);
    // Cinc enviaments a mà i les quatre notes del muntatge.
    expect(estatFinestra(n).enceses).toBe(24 - 5 - 4);
    expect(n.flag('sincronia_automatica')).toBe(true);
  });

  it('amb la sincronia automàtica, posar un objecte a la cambra ja l\'envia', () => {
    const { p, n } = finsPanellReparat();
    n.apply({ setFlag: 'sincronia_automatica' });
    const abans = estatFinestra(n).enceses;
    p.do('pickUp', 'avis');
    expect(keys(p.use('avis_reciclatge', 'panell'))).toEqual(['finestra.enviat']);
    expect(estatFinestra(n).armada).toBe('');
    expect(estatFinestra(n).enceses).toBe(abans - 1);
    // Canvi automàtic a l'altra banda, amb l'objecte a l'inventari.
    expect(p.active).toBe('iri');
    expect(p.inventory()).toContain('avis_reciclatge');
    // Les regles de la finestra continuen valent.
    p.switchTo('vet');
    p.do('pickUp', 'escarabat');
    expect(keys(p.use('escarabat', 'panell'))).toEqual(['finestra.rebuig.viu']);
  });

  it('si insultes en Mos, no et deixa el llapis fins que li demanis perdó', () => {
    const { p, n } = finsPanellReparat();
    p.talk('mos', 'llapis_demanar', 'insultar');
    expect(p.inventory()).not.toContain('llapis_ulls');
    expect(keys(p.talk('mos'))).toEqual(['dlg.mos.ofes']);
    p.talk('mos', 'perdo');
    expect(n.remembers('mos', 'perdonat')).toBe(1);
    // Ja ha perdonat, però encara cal convèncer-lo.
    p.talk('mos', 'llapis_demanar', 'elogiar');
    expect(p.inventory()).toContain('llapis_ulls');
  });

  it('a l\'Iri no se li deixa enviar la caixa d\'eines: pesa massa', () => {
    const { p, world } = finsPanellReparat();
    p.switchTo('iri');
    p.goTo('fabrica_calderes');
    p.goTo('fabrica_magatzem');
    p.do('pickUp', 'caixa_eines');
    p.goTo('fabrica_calderes');
    p.goTo('fabrica_cambra');
    expect(keys(p.use('caixa_eines', 'cambra'))).toEqual(['finestra.rebuig.massa_pesat']);
    expect(world.hasItem('caixa_eines')).toBe(true);
  });

  it('el panell de la Vet es veu diferent a cada pas (decorats)', () => {
    const s = start();
    const decor = () => Object.fromEntries(s.n.hotspotsIn('gavina_cella').filter((h) => h.id.startsWith('panell_')).map((h) => [h.id, h.visible]));
    expect(decor()).toEqual({ panell_afluixat: false, panell_obert: false, panell_reparat: false });
    s.n.apply({ setFlag: 'panell_vet_trencat' });
    expect(decor()).toEqual({ panell_afluixat: true, panell_obert: false, panell_reparat: false });
    s.n.apply({ setFlag: 'panell_vet_obert' });
    expect(decor()).toEqual({ panell_afluixat: false, panell_obert: true, panell_reparat: false });
    s.n.apply({ setFlag: 'panell_vet_reparat' });
    expect(decor()).toEqual({ panell_afluixat: false, panell_obert: false, panell_reparat: true });
  });

  it('mirar un objecte de l\'inventari: la descripció, o el que en diu la Vet de la clau anglesa', () => {
    const { p } = start();
    const clau = { kind: 'item' as const, id: 'clau_anglesa' };
    expect(keys(p.do('look', clau))).toEqual(['obj.clau_anglesa.desc']);
    expect(keys(p.do('look', { kind: 'item', id: 'llapis' }))).toEqual(['obj.llapis.desc']);
    p.do('pickUp', 'tauler');
    p.goTo('fabrica_magatzem');
    p.do('pickUp', 'plomall');
    p.goTo('fabrica_calderes');
    p.use('plomall', 'capatas');
    p.do('pickUp', 'segell');
    p.use('segell', { kind: 'item', id: 'formulari_27b' });
    p.goTo('fabrica_magatzem');
    p.talk('cargol', 'clau');
    p.goTo('fabrica_calderes');
    p.use('clau_cambra', 'porta_cambra');
    p.use('clau_anglesa', 'palanca');
    p.do('push', 'panell');
    expect(texts(p.do('look', clau))).toContain('Aldaia · Ferro-9 · Lot 1');
  });

  it('cada protagonista té la seva veu a les frases per defecte', () => {
    const { p } = finsPanellReparat();
    expect(texts(p.do('pickUp', 'finestreta'))).toContain('butxaques');
    p.switchTo('iri');
    expect(texts(p.do('pickUp', 'palanca'))).toContain('corporació');
  });
});
