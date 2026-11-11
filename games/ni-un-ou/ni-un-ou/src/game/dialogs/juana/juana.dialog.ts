// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './juana.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('juana', dialog)
})

options.menu__valvula.onChoose(() => {
  chooseNarrativeOption('juana', dialog, 'menu', 'valvula')
})

options.menu__revisio.onChoose(() => {
  chooseNarrativeOption('juana', dialog, 'menu', 'revisio')
})

options.menu__adeu.onChoose(() => {
  chooseNarrativeOption('juana', dialog, 'menu', 'adeu')
})
