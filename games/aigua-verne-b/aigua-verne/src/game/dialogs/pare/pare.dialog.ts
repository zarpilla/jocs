// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './pare.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('pare', dialog)
})

options.menu__escriptura.onChoose(() => {
  chooseNarrativeOption('pare', dialog, 'menu', 'escriptura')
})

options.menu__contrasenya.onChoose(() => {
  chooseNarrativeOption('pare', dialog, 'menu', 'contrasenya')
})

options.menu__verne.onChoose(() => {
  chooseNarrativeOption('pare', dialog, 'menu', 'verne')
})

options.menu__llavors.onChoose(() => {
  chooseNarrativeOption('pare', dialog, 'menu', 'llavors')
})

options.menu__reg.onChoose(() => {
  chooseNarrativeOption('pare', dialog, 'menu', 'reg')
})

options.menu__com.onChoose(() => {
  chooseNarrativeOption('pare', dialog, 'menu', 'com')
})

options.menu__temporal.onChoose(() => {
  chooseNarrativeOption('pare', dialog, 'menu', 'temporal')
})

options.menu__adeu.onChoose(() => {
  chooseNarrativeOption('pare', dialog, 'menu', 'adeu')
})
