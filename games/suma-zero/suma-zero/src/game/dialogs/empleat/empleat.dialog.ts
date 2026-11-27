// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './empleat.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('empleat', dialog)
})

options.menu__maleti.onChoose(() => {
  chooseNarrativeOption('empleat', dialog, 'menu', 'maleti')
})

options.menu__adeu.onChoose(() => {
  chooseNarrativeOption('empleat', dialog, 'menu', 'adeu')
})

options.maleti__papers.onChoose(() => {
  chooseNarrativeOption('empleat', dialog, 'maleti', 'papers')
})

options.maleti__agenda.onChoose(() => {
  chooseNarrativeOption('empleat', dialog, 'maleti', 'agenda')
})

options.maleti__llimona.onChoose(() => {
  chooseNarrativeOption('empleat', dialog, 'maleti', 'llimona')
})

options.maleti__oblit.onChoose(() => {
  chooseNarrativeOption('empleat', dialog, 'maleti', 'oblit')
})
