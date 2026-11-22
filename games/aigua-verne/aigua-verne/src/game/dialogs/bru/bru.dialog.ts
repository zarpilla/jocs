// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './bru.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('bru', dialog)
})

options.menu__lia.onChoose(() => {
  chooseNarrativeOption('bru', dialog, 'menu', 'lia')
})

options.menu__juana.onChoose(() => {
  chooseNarrativeOption('bru', dialog, 'menu', 'juana')
})

options.menu__canalla.onChoose(() => {
  chooseNarrativeOption('bru', dialog, 'menu', 'canalla')
})

options.menu__promesa.onChoose(() => {
  chooseNarrativeOption('bru', dialog, 'menu', 'promesa')
})

options.menu__colada.onChoose(() => {
  chooseNarrativeOption('bru', dialog, 'menu', 'colada')
})

options.menu__recorda.onChoose(() => {
  chooseNarrativeOption('bru', dialog, 'menu', 'recorda')
})

options.menu__adeu.onChoose(() => {
  chooseNarrativeOption('bru', dialog, 'menu', 'adeu')
})
