// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './guardia.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('guardia', dialog)
})

options.menu__qui.onChoose(() => {
  chooseNarrativeOption('guardia', dialog, 'menu', 'qui')
})

options.menu__vitrina.onChoose(() => {
  chooseNarrativeOption('guardia', dialog, 'menu', 'vitrina')
})

options.menu__adeu.onChoose(() => {
  chooseNarrativeOption('guardia', dialog, 'menu', 'adeu')
})
