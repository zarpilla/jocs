/** Contingut mínim per provar el nucli sense dependre del joc. */
import type { GameContent, LocaleTable } from '../src/index.js';

export const content: GameContent = {
  manifest: {
    id: 'prova', title: 'joc.titol', defaultLocale: 'ca', locales: ['ca'], protagonists: ['ana', 'bo'],
    start: { ana: { room: 'moll', items: ['moneda'] }, bo: { room: 'far' } },
  },
  state: { flags: { far_ences: false }, vars: { monedes: 0 } },
  characters: {
    ana: { name: 'pj.ana' },
    bo: { name: 'pj.bo' },
    pescador: {
      name: 'pj.pescador', facts: ['insultat', 'ajudat'], relation: { initial: 0, min: -3, max: 3 },
      interactions: [{ verb: 'look', lines: [{ who: 'player', text: 'pescador.look' }] }],
    },
  },
  items: {
    moneda: { name: 'obj.moneda', props: { pes: 0.01 } },
    esquer: {
      name: 'obj.esquer',
      interactions: [{ verb: 'use', item: 'moneda', lines: [{ who: 'player', text: 'esquer.moneda' }], effects: [{ addVar: 'monedes', amount: 1 }] }],
    },
  },
  rooms: {
    moll: {
      name: 'sala.moll',
      onEnter: [{ id: 'intro', verb: '*', once: true, lines: [{ who: 'narrator', text: 'moll.intro' }] }],
      hotspots: {
        pescador: { interactions: [{ verb: 'talkTo', dialogue: 'pescador' }] },
        cucs: {
          visibleIf: { all: [{ quest: 'esquer', status: 'active' }, { hasItem: 'esquer', is: false }] },
          interactions: [{ verb: 'pickUp', lines: [{ who: 'player', text: 'cucs.agafar' }], effects: [{ giveItem: 'esquer' }] }],
        },
        caixa: {
          interactions: [
            { id: 'obrir', verb: 'open', once: true, lines: [{ who: 'player', text: 'caixa.obrir' }], action: { name: 'comptar', args: { que: '$item' } } },
            { verb: 'open', lines: [{ who: 'player', text: 'caixa.buida' }] },
          ],
        },
        barca: { interactions: [{ verb: ['use', 'walkTo'], goTo: 'far' }] },
      },
    },
    far: {
      name: 'sala.far', protagonist: 'bo',
      hotspots: { llum: { interactions: [{ verb: 'use', if: { protagonist: 'bo' }, effects: [{ setFlag: 'far_ences' }], lines: [{ who: 'player', text: 'llum.encendre' }] }] } },
    },
  },
  dialogues: {
    pescador: {
      id: 'pescador', with: 'pescador',
      start: [
        { if: { remembers: { who: 'pescador', fact: 'insultat' } }, node: 'rancunios' },
        { node: 'hola' },
      ],
      nodes: {
        hola: {
          lines: [
            { who: 'pescador', text: 'p.hola.primer', if: { seen: { dialogue: 'pescador', node: 'hola' }, is: false } },
            { who: 'pescador', text: 'p.hola' },
          ],
          goto: 'menu',
        },
        rancunios: { lines: [{ who: 'pescador', text: 'p.rancunios' }], goto: 'menu' },
        menu: {
          choices: [
            { id: 'far', text: 'p.opt.far', once: true, next: 'far' },
            { id: 'insultar', text: 'p.opt.insultar', if: { remembers: { who: 'pescador', fact: 'insultat' }, is: false },
              effects: [{ remember: { who: 'pescador', fact: 'insultat' } }, { relation: { who: 'pescador', change: -2 } }] },
            { id: 'esquer', text: 'p.opt.esquer', if: { hasItem: 'esquer' }, effects: [{ takeItem: 'esquer' }, { completeObjective: { quest: 'esquer', objective: 'donar' } }] },
            { id: 'adeu', text: 'p.opt.adeu', next: 'adeu', end: true },
          ],
        },
        far: { lines: [{ who: 'pescador', text: 'p.far' }], effects: [{ startQuest: 'esquer' }], goto: 'menu' },
        adeu: { lines: [{ who: 'pescador', text: 'p.adeu' }] },
      },
    },
  },
  quests: {
    esquer: {
      kind: 'side', title: 'q.esquer',
      objectives: [
        { id: 'trobar', text: 'q.esquer.trobar', completeWhen: { hasItem: 'esquer' } },
        { id: 'donar', text: 'q.esquer.donar' },
      ],
      failWhen: { relation: { who: 'pescador', op: '<=', value: -3 } },
      onComplete: [{ relation: { who: 'pescador', change: 2 } }, { remember: { who: 'pescador', fact: 'ajudat' } }],
    },
  },
  hints: {
    esquer: {
      priority: 5, when: { quest: 'esquer', status: 'active' }, doneWhen: { hasItem: 'esquer' },
      levels: ['h.esquer.1', 'h.esquer.2'],
    },
  },
  endings: {
    amic: { title: 'f.amic', text: 'f.amic.text', priority: 10, when: { all: [{ flag: 'far_ences' }, { relation: { who: 'pescador', op: '>=', value: 2 } }] } },
    sol: { title: 'f.sol', text: 'f.sol.text', priority: 5, when: { flag: 'far_ences' } },
    fugida: { title: 'f.fugida', text: 'f.fugida.text' },
  },
};

const keys = [
  'joc.titol', 'pj.ana', 'pj.bo', 'pj.pescador', 'obj.moneda', 'obj.esquer', 'sala.moll', 'sala.far', 'moll.intro',
  'pescador.look', 'esquer.moneda', 'cucs.agafar', 'caixa.obrir', 'caixa.buida', 'llum.encendre', 'p.hola.primer',
  'p.hola', 'p.rancunios', 'p.opt.far', 'p.opt.insultar', 'p.opt.esquer', 'p.opt.adeu', 'p.far', 'p.adeu', 'q.esquer',
  'q.esquer.trobar', 'q.esquer.donar', 'h.esquer.1', 'h.esquer.2', 'f.amic', 'f.amic.text', 'f.sol', 'f.sol.text',
  'f.fugida', 'f.fugida.text', 'ui.defecte', 'ui.defecte.look.bo', 'comptat',
];

export const locales: Record<string, LocaleTable> = {
  ca: { ...Object.fromEntries(keys.map((k) => [k, `[${k}]`])), 'pj.pescador': 'Pescador', comptat: 'Comptat: {que}' },
};
