import { describe, expect, it } from 'vitest';
import { HeadlessPlayer, MemoryWorld, Narrative, validateContent, type GameContent, type NarrativeEvent } from '../src/index.js';
import { content, locales } from './fixture.js';

function setup(c: GameContent = content) {
  const world = new MemoryWorld();
  const n = new Narrative({ content: c, locales, world });
  n.registerAction('comptar', ({ args }) => ({ lines: [{ who: 'narrator', text: 'comptat', params: { que: String(args.que) } }] }));
  const p = new HeadlessPlayer(n, world);
  const events: NarrativeEvent[] = [];
  n.on((e) => e.type !== 'stateChanged' && events.push(e));
  p.newGame();
  return { world, n, p, events };
}

const keys = (lines: { key: string }[]) => lines.map((l) => l.key);

describe('validació', () => {
  it('el contingut de prova és vàlid', () => {
    expect(validateContent(content, locales, { actions: ['comptar'] }).filter((i) => i.level === 'error')).toEqual([]);
  });

  it('detecta referències trencades, accions desconegudes i textos que falten', () => {
    const broken: GameContent = structuredClone(content);
    broken.quests.esquer!.startWhen = { flag: 'no_existeix' };
    broken.dialogues.pescador!.nodes.menu!.choices![0]!.next = 'node_fantasma';
    broken.rooms.moll!.hotspots.barca!.interactions![0]!.goTo = 'sala_fantasma';
    broken.rooms.moll!.hotspots.caixa!.interactions![0]!.action = { name: 'accio_fantasma' };
    const { 'p.adeu': _, ...ca } = locales.ca!;
    const messages = validateContent(broken, { ca }, { actions: ['comptar'] }).map((i) => i.message).join('\n');
    for (const bad of ['no_existeix', 'node_fantasma', 'sala_fantasma', 'accio_fantasma', 'p.adeu']) expect(messages).toContain(bad);
  });
});

describe('partida nova i sales', () => {
  it('reparteix inventaris inicials i executa l\'entrada a la sala una sola vegada', () => {
    const { p } = setup();
    expect(p.inventory('ana')).toEqual(['moneda']);
    expect(p.room).toBe('moll');
    expect(p.transcript[0]).toBe('narrator: [moll.intro]');
    expect(p.goTo('moll')).toEqual([]);
  });

  it('les interaccions "once" passen una vegada i després en toca una altra', () => {
    const { p } = setup();
    expect(keys(p.do('open', 'caixa'))).toEqual(['caixa.obrir', 'comptat']);
    expect(keys(p.do('open', 'caixa'))).toEqual(['caixa.buida']);
  });

  it('les accions de joc reben els arguments i tornen línies', () => {
    const { p } = setup();
    expect(p.do('open', 'caixa').at(-1)!.text).toBe('Comptat: ');
  });

  it('sense interacció, frase per defecte segons la protagonista', () => {
    const { p } = setup();
    expect(p.do('push', 'barca')[0]!.key).toBe('ui.defecte');
    p.switchTo('bo');
    expect(p.do('look', 'llum')[0]!.key).toBe('ui.defecte.look.bo');
  });

  it('interaccions de personatge valen a qualsevol sala; combinar objectes funciona en tots dos sentits', () => {
    const { p, n, world } = setup();
    expect(keys(p.do('look', 'pescador'))).toEqual(['pescador.look']);
    world.give('esquer');
    p.use('moneda', { kind: 'item', id: 'esquer' });
    p.use('esquer', { kind: 'item', id: 'moneda' });
    expect(n.getVar('monedes')).toBe(2);
  });

  it('dues protagonistes amb inventaris i sales separats', () => {
    const { p, n } = setup();
    p.do('use', 'barca');
    expect(p.room).toBe('far');
    expect(p.do('use', 'llum')[0]!.key).toBe('ui.defecte'); // l'Ana no pot: condició `protagonist`
    p.switchTo('bo');
    expect(p.inventory()).toEqual([]);
    p.do('use', 'llum');
    expect(n.flag('far_ences')).toBe(true);
  });
});

describe('diàlegs i memòria', () => {
  it('la primera conversa saluda diferent que les següents', () => {
    const { p } = setup();
    expect(keys(p.talk('pescador', 'adeu')).slice(0, 2)).toEqual(['p.hola.primer', 'p.hola']);
    expect(keys(p.talk('pescador'))).toEqual(['p.hola']);
  });

  it('el pescador recorda l\'insult', () => {
    const { p, n } = setup();
    p.talk('pescador', 'insultar');
    expect(n.relation('pescador')).toBe(-2);
    expect(keys(p.talk('pescador'))).toEqual(['p.rancunios']);
    expect(n.currentChoices('pescador')).toEqual([]);
  });

  it('opcions "once" desapareixen; "end" acaba; opció sense next torna al node', () => {
    const { n } = setup();
    n.startDialogue('pescador');
    expect(n.choose('pescador', 'far').choices.map((c) => c.id)).not.toContain('far');
    const bye = n.choose('pescador', 'adeu');
    expect(bye.ended).toBe(true);
    expect(() => n.choose('pescador', 'adeu')).toThrow(/no està en curs/);
  });
});

describe('missions, objectes condicionals, pistes i finals', () => {
  it('missió secundària completa amb premi', () => {
    const { p, n, world, events } = setup();
    expect(n.isHotspotVisible('moll', 'cucs')).toBe(false);
    p.talk('pescador', 'far');
    expect(n.hotspotsIn('moll')).toContainEqual({ id: 'cucs', visible: true });
    expect(n.requestHint()!.level).toBe(1);
    expect(n.requestHint()!.hasMore).toBe(false);
    p.do('pickUp', 'cucs');
    expect(n.isHotspotVisible('moll', 'cucs')).toBe(false);
    expect(n.requestHint()).toBeNull();
    p.talk('pescador', 'esquer');
    expect(world.hasItem('esquer')).toBe(false);
    expect(n.state.quests.esquer!.status).toBe('completed');
    expect(n.relation('pescador')).toBe(2);
    expect(events.map((e) => e.type)).toEqual(expect.arrayContaining(['questStarted', 'objectiveCompleted', 'questCompleted']));

    n.apply({ setFlag: 'far_ences' });
    expect(n.resolveEnding()).toBe('amic');
  });

  it('la relació té límits i pot fer fallar la missió', () => {
    const { p, n } = setup();
    p.talk('pescador', 'far', 'insultar');
    n.apply({ relation: { who: 'pescador', change: -9 } });
    expect(n.relation('pescador')).toBe(-3);
    expect(n.state.quests.esquer!.status).toBe('failed');
    n.apply({ setFlag: 'far_ences' });
    expect(n.resolveEnding()).toBe('sol');
  });

  it('un objectiu amb showWhen no surt fins que es compleix (o fins que és fet)', () => {
    const c = structuredClone(content);
    c.quests.esquer!.objectives[1]!.showWhen = { flag: 'sap_donar' };
    const { p, n } = setup(c);
    p.talk('pescador', 'far');
    const ids = () => n.quests()[0]!.objectives.map((o) => o.id);
    expect(ids()).toEqual(['trobar']);
    n.apply({ setFlag: 'sap_donar' });
    expect(ids()).toEqual(['trobar', 'donar']);
  });

  it('un final forçat per efecte té prioritat', () => {
    const { n } = setup();
    n.apply({ ending: 'fugida' });
    expect(n.resolveEnding()).toBe('fugida');
  });
});

describe('desar i carregar', () => {
  it('l\'estat sobreviu i accepta contingut nou', () => {
    const { p, n } = setup();
    p.talk('pescador', 'insultar');
    p.do('open', 'caixa');
    const saved = JSON.parse(JSON.stringify(n.snapshot()));

    const newer: GameContent = structuredClone(content);
    newer.state.flags.flag_nou = true;
    const b = new Narrative({ content: newer, locales, world: new MemoryWorld() });
    b.registerAction('comptar', () => {});
    b.load(saved);
    expect(b.remembers('pescador', 'insultat')).toBe(1);
    expect(b.flag('flag_nou')).toBe(true);
    expect(b.interact({ verb: 'open', target: { kind: 'hotspot', id: 'caixa' }, room: 'moll' })!.lines[0]!.key).toBe('caixa.buida');
  });
});

describe('traduccions', () => {
  it('torna a l\'idioma per defecte i interpola variables', () => {
    const n = new Narrative({ content, locales: { ...locales, en: { 'pj.pescador': 'Fisherman', x: 'You have {monedes} coins' } }, world: new MemoryWorld() });
    n.setLocale('en');
    expect(n.characterName('pescador')).toBe('Fisherman');
    expect(n.itemName('esquer')).toBe('[obj.esquer]');
    n.apply({ addVar: 'monedes', amount: 2 });
    expect(n.t('x')).toBe('You have 2 coins');
    expect(n.t('no.existeix')).toBe('⟦no.existeix⟧');
  });
});

describe('regles després de cada acció i situar', () => {
  it("onAfterAction s'executa després de cada interacció i opció que encaixa, però no amb les frases per defecte", () => {
    const { n, p } = setup();
    const vistes: string[] = [];
    n.onAfterAction((a) => {
      vistes.push(a.kind === 'interaction' ? `${a.verb}:${a.target.id}` : `${a.dialogue}.${a.choice}`);
      return a.kind === 'interaction' && a.verb === 'open' ? { lines: [{ who: 'narrator', text: 'comptat', params: { que: 'torn' } }] } : undefined;
    });
    const lines = p.do('open', 'caixa');
    expect(keys(lines)).toContain('comptat');
    p.do('push', 'caixa'); // cap interacció: frase per defecte, no compta
    p.talk('pescador', 'far');
    expect(vistes).toEqual(['open:caixa', 'pescador.far']);
  });

  it("l'esdeveniment situar mou l'altra protagonista: hi entra quan s'hi canvia", () => {
    const { n, p } = setup();
    n.apply({ event: 'situar', args: { who: 'bo', room: 'moll' } });
    p.switchTo('bo');
    expect(p.room).toBe('moll');
  });

  it('outfitOf tria la primera roba que es compleix, o la normal', () => {
    const c: GameContent = structuredClone(content);
    c.characters.ana!.outfit = [
      { if: { all: [{ flag: 'far_ences' }, { var: 'monedes', op: '>', value: 0 }] }, name: 'FestaRica' },
      { if: { flag: 'far_ences' }, name: 'Festa' },
    ];
    const { n } = setup(c);
    expect(n.outfitOf('ana')).toBe('');
    n.apply({ setFlag: 'far_ences' });
    expect(n.outfitOf('ana')).toBe('Festa');
    n.apply({ addVar: 'monedes', amount: 1 });
    expect(n.outfitOf('ana')).toBe('FestaRica');
    expect(n.outfitOf('bo')).toBe('');
  });
});
