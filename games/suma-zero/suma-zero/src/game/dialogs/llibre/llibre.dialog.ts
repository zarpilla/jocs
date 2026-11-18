// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './llibre.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('llibre', dialog)
})

options.menu__bonfill.onChoose(() => {
  chooseNarrativeOption('llibre', dialog, 'menu', 'bonfill')
})

options.menu__diners.onChoose(() => {
  chooseNarrativeOption('llibre', dialog, 'menu', 'diners')
})

options.menu__rockefeller.onChoose(() => {
  chooseNarrativeOption('llibre', dialog, 'menu', 'rockefeller')
})

options.menu__sostenibilitat.onChoose(() => {
  chooseNarrativeOption('llibre', dialog, 'menu', 'sostenibilitat')
})

options.menu__adeu.onChoose(() => {
  chooseNarrativeOption('llibre', dialog, 'menu', 'adeu')
})
