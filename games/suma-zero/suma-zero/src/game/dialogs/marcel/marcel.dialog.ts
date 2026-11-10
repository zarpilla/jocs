// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './marcel.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('marcel', dialog)
})

options.menu__falten.onChoose(() => {
  chooseNarrativeOption('marcel', dialog, 'menu', 'falten')
})

options.menu__servidor.onChoose(() => {
  chooseNarrativeOption('marcel', dialog, 'menu', 'servidor')
})

options.menu__clau.onChoose(() => {
  chooseNarrativeOption('marcel', dialog, 'menu', 'clau')
})

options.menu__tub.onChoose(() => {
  chooseNarrativeOption('marcel', dialog, 'menu', 'tub')
})

options.menu__vol.onChoose(() => {
  chooseNarrativeOption('marcel', dialog, 'menu', 'vol')
})

options.menu__ballester.onChoose(() => {
  chooseNarrativeOption('marcel', dialog, 'menu', 'ballester')
})

options.menu__neta.onChoose(() => {
  chooseNarrativeOption('marcel', dialog, 'menu', 'neta')
})

options.menu__gracies.onChoose(() => {
  chooseNarrativeOption('marcel', dialog, 'menu', 'gracies')
})

options.menu__adeu.onChoose(() => {
  chooseNarrativeOption('marcel', dialog, 'menu', 'adeu')
})
