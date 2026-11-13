// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './nil.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('nil', dialog)
})

options.menu__flors.onChoose(() => {
  chooseNarrativeOption('nil', dialog, 'menu', 'flors')
})

options.menu__palau.onChoose(() => {
  chooseNarrativeOption('nil', dialog, 'menu', 'palau')
})

options.menu__magnat.onChoose(() => {
  chooseNarrativeOption('nil', dialog, 'menu', 'magnat')
})

options.menu__tomaquera.onChoose(() => {
  chooseNarrativeOption('nil', dialog, 'menu', 'tomaquera')
})

options.menu__regada.onChoose(() => {
  chooseNarrativeOption('nil', dialog, 'menu', 'regada')
})

options.menu__quan.onChoose(() => {
  chooseNarrativeOption('nil', dialog, 'menu', 'quan')
})

options.menu__adeu.onChoose(() => {
  chooseNarrativeOption('nil', dialog, 'menu', 'adeu')
})
