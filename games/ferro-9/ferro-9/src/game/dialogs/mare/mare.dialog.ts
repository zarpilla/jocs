// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './mare.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('mare', dialog)
})

options.menu__reciclatge.onChoose(() => {
  chooseNarrativeOption('mare', dialog, 'menu', 'reciclatge')
})

options.menu__sortir.onChoose(() => {
  chooseNarrativeOption('mare', dialog, 'menu', 'sortir')
})

options.menu__preso.onChoose(() => {
  chooseNarrativeOption('mare', dialog, 'menu', 'preso')
})

options.menu__adeu.onChoose(() => {
  chooseNarrativeOption('mare', dialog, 'menu', 'adeu')
})
