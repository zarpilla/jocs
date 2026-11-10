// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './mira.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('mira', dialog)
})

options.menu__que_dius.onChoose(() => {
  chooseNarrativeOption('mira', dialog, 'menu', 'que_dius')
})

options.menu__planols.onChoose(() => {
  chooseNarrativeOption('mira', dialog, 'menu', 'planols')
})

options.menu__adeu.onChoose(() => {
  chooseNarrativeOption('mira', dialog, 'menu', 'adeu')
})
