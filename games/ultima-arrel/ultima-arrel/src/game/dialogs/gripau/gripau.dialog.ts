// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './gripau.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('gripau', dialog)
})

options.menu__vaga.onChoose(() => {
  chooseNarrativeOption('gripau', dialog, 'menu', 'vaga')
})

options.menu__ajuda.onChoose(() => {
  chooseNarrativeOption('gripau', dialog, 'menu', 'ajuda')
})

options.menu__pancarta.onChoose(() => {
  chooseNarrativeOption('gripau', dialog, 'menu', 'pancarta')
})

options.menu__adeu.onChoose(() => {
  chooseNarrativeOption('gripau', dialog, 'menu', 'adeu')
})
