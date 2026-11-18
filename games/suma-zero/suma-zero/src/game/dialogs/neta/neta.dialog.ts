// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './neta.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('neta', dialog)
})

options.menu__hores.onChoose(() => {
  chooseNarrativeOption('neta', dialog, 'menu', 'hores')
})

options.menu__descansa.onChoose(() => {
  chooseNarrativeOption('neta', dialog, 'menu', 'descansa')
})

options.menu__adeu.onChoose(() => {
  chooseNarrativeOption('neta', dialog, 'menu', 'adeu')
})
