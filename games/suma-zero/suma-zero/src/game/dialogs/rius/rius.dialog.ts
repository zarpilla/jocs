// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './rius.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('rius', dialog)
})

options.menu__targeta.onChoose(() => {
  chooseNarrativeOption('rius', dialog, 'menu', 'targeta')
})

options.menu__mobil.onChoose(() => {
  chooseNarrativeOption('rius', dialog, 'menu', 'mobil')
})

options.menu__arreglar.onChoose(() => {
  chooseNarrativeOption('rius', dialog, 'menu', 'arreglar')
})

options.menu__cafe.onChoose(() => {
  chooseNarrativeOption('rius', dialog, 'menu', 'cafe')
})

options.menu__adeu.onChoose(() => {
  chooseNarrativeOption('rius', dialog, 'menu', 'adeu')
})
