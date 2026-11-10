// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './diu.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('diu', dialog)
})

options.menu__cables.onChoose(() => {
  chooseNarrativeOption('diu', dialog, 'menu', 'cables')
})

options.menu__adeu.onChoose(() => {
  chooseNarrativeOption('diu', dialog, 'menu', 'adeu')
})
