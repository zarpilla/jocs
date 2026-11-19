// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './urtica.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('urtica', dialog)
})

options.menu__avia.onChoose(() => {
  chooseNarrativeOption('urtica', dialog, 'menu', 'avia')
})

options.menu__espora.onChoose(() => {
  chooseNarrativeOption('urtica', dialog, 'menu', 'espora')
})

options.menu__naturaplus.onChoose(() => {
  chooseNarrativeOption('urtica', dialog, 'menu', 'naturaplus')
})

options.menu__apunteu.onChoose(() => {
  chooseNarrativeOption('urtica', dialog, 'menu', 'apunteu')
})

options.menu__adeu.onChoose(() => {
  chooseNarrativeOption('urtica', dialog, 'menu', 'adeu')
})

options.menu2__pla.onChoose(() => {
  chooseNarrativeOption('urtica', dialog, 'menu2', 'pla')
})

options.menu2__flor.onChoose(() => {
  chooseNarrativeOption('urtica', dialog, 'menu2', 'flor')
})

options.menu2__empeny.onChoose(() => {
  chooseNarrativeOption('urtica', dialog, 'menu2', 'empeny')
})

options.menu2__adeu2.onChoose(() => {
  chooseNarrativeOption('urtica', dialog, 'menu2', 'adeu2')
})
