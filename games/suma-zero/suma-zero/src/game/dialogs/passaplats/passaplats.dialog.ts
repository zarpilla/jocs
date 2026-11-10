// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './passaplats.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('passaplats', dialog)
})

options.menu__cable.onChoose(() => {
  chooseNarrativeOption('passaplats', dialog, 'menu', 'cable')
})

options.menu__pizza.onChoose(() => {
  chooseNarrativeOption('passaplats', dialog, 'menu', 'pizza')
})

options.menu__marcel.onChoose(() => {
  chooseNarrativeOption('passaplats', dialog, 'menu', 'marcel')
})

options.menu__adeu.onChoose(() => {
  chooseNarrativeOption('passaplats', dialog, 'menu', 'adeu')
})
