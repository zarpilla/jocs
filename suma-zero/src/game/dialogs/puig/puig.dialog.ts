// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './puig.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('puig', dialog)
})

options.menu__cafe.onChoose(() => {
  chooseNarrativeOption('puig', dialog, 'menu', 'cafe')
})

options.menu__cafe2.onChoose(() => {
  chooseNarrativeOption('puig', dialog, 'menu', 'cafe2')
})

options.menu__comandament.onChoose(() => {
  chooseNarrativeOption('puig', dialog, 'menu', 'comandament')
})

options.menu__wifi.onChoose(() => {
  chooseNarrativeOption('puig', dialog, 'menu', 'wifi')
})

options.menu__adeu.onChoose(() => {
  chooseNarrativeOption('puig', dialog, 'menu', 'adeu')
})
