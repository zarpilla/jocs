// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './barril.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('barril', dialog)
})

options.inici__cas.onChoose(() => {
  chooseNarrativeOption('barril', dialog, 'inici', 'cas')
})

options.inici__mirar.onChoose(() => {
  chooseNarrativeOption('barril', dialog, 'inici', 'mirar')
})

options.inici__no.onChoose(() => {
  chooseNarrativeOption('barril', dialog, 'inici', 'no')
})
