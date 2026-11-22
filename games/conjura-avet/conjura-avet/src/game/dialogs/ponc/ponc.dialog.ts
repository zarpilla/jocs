// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './ponc.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('ponc', dialog)
})

options.menu__tall.onChoose(() => {
  chooseNarrativeOption('ponc', dialog, 'menu', 'tall')
})

options.menu__adeu.onChoose(() => {
  chooseNarrativeOption('ponc', dialog, 'menu', 'adeu')
})
