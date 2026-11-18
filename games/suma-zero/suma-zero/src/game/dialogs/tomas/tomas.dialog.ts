// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './tomas.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('tomas', dialog)
})

options.menu__wifi.onChoose(() => {
  chooseNarrativeOption('tomas', dialog, 'menu', 'wifi')
})

options.menu__cafe.onChoose(() => {
  chooseNarrativeOption('tomas', dialog, 'menu', 'cafe')
})

options.menu__cafe2.onChoose(() => {
  chooseNarrativeOption('tomas', dialog, 'menu', 'cafe2')
})

options.menu__comandament.onChoose(() => {
  chooseNarrativeOption('tomas', dialog, 'menu', 'comandament')
})

options.menu__adeu.onChoose(() => {
  chooseNarrativeOption('tomas', dialog, 'menu', 'adeu')
})
