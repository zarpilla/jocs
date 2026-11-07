import { beforeEach, describe, expect, it } from 'vitest';
import { content, locales } from '@aventura/game';
import { MemoryWorld, Narrative, validateContent, type GameContent, type NarrativeEvent } from '../src/index.js';

function setup() {
  const world = new MemoryWorld();
  const narrative = new Narrative({ content, locales, world });
  const events: NarrativeEvent[] = [];
  narrative.on(world.listener);
  narrative.on((e) => e.type !== 'stateChanged' && events.push(e));
  return { world, narrative, events };
}

/** Tria opcions en ordre i retorna l'últim pas. */
function talk(n: Narrative, dialogue: string, ...choices: string[]) {
  let step = n.startDialogue(dialogue);
  for (const c of choices) {
    expect(step.choices.map((x) => x.id), `l'opció "${c}" hauria d'estar disponible`).toContain(c);
    step = n.choose(dialogue, c);
  }
  return step;
}

describe('contingut del joc', () => {
  it('és vàlid', () => {
    const errors = validateContent(content, locales).filter((i) => i.level === 'error');
    expect(errors).toEqual([]);
  });

  it('el validador detecta referències trencades i textos que falten', () => {
    const broken: GameContent = structuredClone(content);
    broken.quests.encendre_far!.startWhen = { flag: 'no_existeix' };
    broken.dialogues.pescador!.nodes.menu!.choices![0]!.next = 'node_fantasma';
    const issues = validateContent(broken, { ca: { ...locales.ca, 'dlg.pescador.adeu': undefined as never } });
    const messages = issues.map((i) => i.message).join('\n');
    expect(messages).toContain('no_existeix');
    expect(messages).toContain('node_fantasma');
    expect(messages).toContain('dlg.pescador.adeu');
  });
});

describe('diàlegs i memòria dels personatges', () => {
  let s: ReturnType<typeof setup>;
  beforeEach(() => (s = setup()));

  it('la primera conversa saluda diferent que les següents', () => {
    const first = s.narrative.startDialogue('pescador');
    expect(first.lines.map((l) => l.key)).toEqual(['dlg.pescador.hola.1', 'dlg.pescador.hola.2']);
    expect(first.lines[0]!.text).toMatch(/cara nova/);
    s.narrative.choose('pescador', 'adeu');

    const second = s.narrative.startDialogue('pescador');
    expect(second.lines.map((l) => l.key)).toEqual(['dlg.pescador.hola.2']);
  });

  it('el pescador recorda que l\'has insultat (i canvia la salutació i les opcions)', () => {
    const step = talk(s.narrative, 'pescador', 'insultar');
    expect(step.lines.map((l) => l.who)).toEqual(['player', 'pescador']);
    expect(s.narrative.remembers('pescador', 'insultat')).toBe(1);
    expect(s.narrative.relation('pescador')).toBe(-2);
    expect(step.choices.map((c) => c.id)).toContain('demanar_perdo');
    expect(step.choices.map((c) => c.id)).not.toContain('insultar');
    s.narrative.choose('pescador', 'adeu');

    const again = s.narrative.startDialogue('pescador');
    expect(again.node).toBe('menu');
    expect(again.lines[0]!.key).toBe('dlg.pescador.rancunios');
  });

  it('les opcions "once" desapareixen i "end" tanca la conversa', () => {
    const step = talk(s.narrative, 'pescador', 'far');
    expect(step.choices.map((c) => c.id)).not.toContain('far');
    const bye = s.narrative.choose('pescador', 'adeu');
    expect(bye.ended).toBe(true);
    expect(bye.lines.at(-1)!.key).toBe('dlg.pescador.adeu');
    expect(() => s.narrative.choose('pescador', 'adeu')).toThrow(/no està en curs/);
  });

  it('opcions que només surten en certes circumstàncies', () => {
    expect(talk(s.narrative, 'pescador').choices.map((c) => c.id)).not.toContain('clau');
    s.narrative.choose('pescador', 'far');
    expect(s.narrative.currentChoices('pescador').map((c) => c.id)).toContain('clau');
  });
});

describe('missió secundària, objectes condicionals, pistes i finals', () => {
  it('partida completa: esquer → clau → far → final', () => {
    const { world, narrative: n, events } = setup();

    // Arribar al moll activa la missió principal.
    world.enter('moll');
    n.worldChanged();
    expect(n.state.quests.encendre_far!.status).toBe('active');
    expect(n.requestHint()!.text).toBe('Algú del port deu saber on és la clau.');
    expect(n.requestHint()!.level).toBe(2);

    // L'esquer encara no apareix al moll: cal la missió secundària.
    expect(n.isObjectVisible('esquer_al_moll')).toBe(false);
    talk(n, 'pescador', 'far', 'clau');
    expect(n.state.quests.esquer_pescador!.status).toBe('active');
    expect(n.objectsIn('moll')).toContainEqual({ id: 'esquer_al_moll', visible: true });
    n.endDialogue('pescador');

    // Agafar l'esquer (ho fa l'script de la sala).
    n.apply({ giveItem: 'esquer' });
    expect(n.state.quests.esquer_pescador!.objectives.trobar_esquer).toBe(true);
    expect(n.isObjectVisible('esquer_al_moll')).toBe(false);

    // Donar-lo completa la missió, i el premi canvia la relació i la memòria.
    talk(n, 'pescador', 'donar_esquer');
    expect(n.state.quests.esquer_pescador!.status).toBe('completed');
    expect(n.getVar('monedes')).toBe(3);
    expect(n.relation('pescador')).toBe(2);
    expect(world.hasItem('esquer')).toBe(false);

    // Ara sí que dona la clau.
    const step = n.choose('pescador', 'clau');
    expect(step.lines.map((l) => l.key)).toEqual(['dlg.pescador.opt.clau', 'dlg.pescador.clau.si']);
    expect(world.hasItem('clau_far')).toBe(true);
    expect(step.choices.map((c) => c.id)).not.toContain('clau');
    n.endDialogue('pescador');

    // Encendre el far tanca la missió principal i dona el millor final.
    expect(n.resolveEnding()).toBeNull();
    n.apply({ setFlag: 'far_ences' });
    expect(n.state.quests.encendre_far!.status).toBe('completed');
    expect(n.isObjectVisible('llum_del_far')).toBe(true);
    expect(n.resolveEnding()).toBe('heroi_del_port');
    expect(n.ending('heroi_del_port').title).toBe("L'heroi del port");

    expect(events.map((e) => e.type)).toEqual(
      expect.arrayContaining(['questStarted', 'objectiveCompleted', 'questCompleted', 'giveItem', 'takeItem']),
    );
  });

  it('si et barallas amb el pescador, el final és un altre i la missió falla', () => {
    const { world, narrative: n } = setup();
    world.enter('moll');
    talk(n, 'pescador', 'far', 'clau');
    n.choose('pescador', 'insultar');
    n.apply({ relation: { who: 'pescador', change: -5 } });
    expect(n.relation('pescador')).toBe(-3); // límit de characters.json
    expect(n.state.quests.esquer_pescador!.status).toBe('failed');
    n.apply({ setFlag: 'far_ences' });
    expect(n.resolveEnding()).toBe('far_ences_sol');
  });

  it('un final forçat per efecte té prioritat', () => {
    const { narrative: n, events } = setup();
    n.apply({ ending: 'fugida' });
    expect(n.resolveEnding()).toBe('fugida');
    expect(events).toContainEqual({ type: 'ending', ending: 'fugida' });
  });
});

describe('desar i carregar', () => {
  it('l\'estat sobreviu a una partida desada i suporta contingut nou', () => {
    const a = setup();
    talk(a.narrative, 'pescador', 'insultar');
    const saved = JSON.parse(JSON.stringify(a.narrative.snapshot()));

    // Simulem una versió nova del joc amb un flag que abans no existia.
    const newer: GameContent = structuredClone(content);
    newer.state.flags.flag_nou = true;
    const b = new Narrative({ content: newer, locales, world: new MemoryWorld() });
    b.load(saved);
    expect(b.remembers('pescador', 'insultat')).toBe(1);
    expect(b.relation('pescador')).toBe(-2);
    expect(b.flag('flag_nou')).toBe(true);
    expect(b.startDialogue('pescador').lines[0]!.key).toBe('dlg.pescador.rancunios');
  });
});

describe('traduccions', () => {
  it('fa servir l\'idioma per defecte si falta una clau i interpola variables', () => {
    const world = new MemoryWorld();
    const n = new Narrative({
      content,
      locales: { ...locales, en: { 'pj.pescador.nom': 'Fisherman', 'ui.monedes': 'You have {monedes} coins' } },
      world,
    });
    n.setLocale('en');
    expect(n.characterName('pescador')).toBe('Fisherman');
    expect(n.itemName('esquer')).toBe('esquer'); // ve del català
    n.apply({ addVar: 'monedes', amount: 2 });
    expect(n.t('ui.monedes')).toBe('You have 2 coins');
    expect(n.t('no.existeix')).toBe('⟦no.existeix⟧');
  });
});
