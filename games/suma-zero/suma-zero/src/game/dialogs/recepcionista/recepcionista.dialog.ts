// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './recepcionista.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('recepcionista', dialog)
})

options.menu__dessuadora.onChoose(() => {
  chooseNarrativeOption('recepcionista', dialog, 'menu', 'dessuadora')
})

options.menu__altra.onChoose(() => {
  chooseNarrativeOption('recepcionista', dialog, 'menu', 'altra')
})

options.menu__font.onChoose(() => {
  chooseNarrativeOption('recepcionista', dialog, 'menu', 'font')
})

options.menu__adeu.onChoose(() => {
  chooseNarrativeOption('recepcionista', dialog, 'menu', 'adeu')
})
