// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './pla.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('pla', dialog)
})

options.menu__bosc.onChoose(() => {
  chooseNarrativeOption('pla', dialog, 'menu', 'bosc')
})

options.menu__vells.onChoose(() => {
  chooseNarrativeOption('pla', dialog, 'menu', 'vells')
})

options.menu__ocells.onChoose(() => {
  chooseNarrativeOption('pla', dialog, 'menu', 'ocells')
})

options.menu__aire.onChoose(() => {
  chooseNarrativeOption('pla', dialog, 'menu', 'aire')
})

options.menu__altaveu.onChoose(() => {
  chooseNarrativeOption('pla', dialog, 'menu', 'altaveu')
})

options.menu__adeu.onChoose(() => {
  chooseNarrativeOption('pla', dialog, 'menu', 'adeu')
})
