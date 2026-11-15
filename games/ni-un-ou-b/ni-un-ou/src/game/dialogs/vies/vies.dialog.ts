// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './vies.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('vies', dialog)
})

options.tria__borda.onChoose(() => {
  chooseNarrativeOption('vies', dialog, 'tria', 'borda')
})

options.tria__separador.onChoose(() => {
  chooseNarrativeOption('vies', dialog, 'tria', 'separador')
})
