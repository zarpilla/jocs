// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './radio_juana.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('radio_juana', dialog)
})

options.menu__feina.onChoose(() => {
  chooseNarrativeOption('radio_juana', dialog, 'menu', 'feina')
})

options.menu__albara.onChoose(() => {
  chooseNarrativeOption('radio_juana', dialog, 'menu', 'albara')
})

options.menu__llavors.onChoose(() => {
  chooseNarrativeOption('radio_juana', dialog, 'menu', 'llavors')
})

options.menu__adeu.onChoose(() => {
  chooseNarrativeOption('radio_juana', dialog, 'menu', 'adeu')
})
