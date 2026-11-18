// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './lia.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('lia', dialog)
})

options.menu__feina.onChoose(() => {
  chooseNarrativeOption('lia', dialog, 'menu', 'feina')
})

options.menu__pare.onChoose(() => {
  chooseNarrativeOption('lia', dialog, 'menu', 'pare')
})

options.menu__nota.onChoose(() => {
  chooseNarrativeOption('lia', dialog, 'menu', 'nota')
})

options.menu__adeu.onChoose(() => {
  chooseNarrativeOption('lia', dialog, 'menu', 'adeu')
})

options.aliada__control.onChoose(() => {
  chooseNarrativeOption('lia', dialog, 'aliada', 'control')
})

options.aliada__adeu2.onChoose(() => {
  chooseNarrativeOption('lia', dialog, 'aliada', 'adeu2')
})
