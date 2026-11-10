// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './aturada.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('aturada', dialog)
})

options.tria__tornar.onChoose(() => {
  chooseNarrativeOption('aturada', dialog, 'tria', 'tornar')
})

options.tria__pagar.onChoose(() => {
  chooseNarrativeOption('aturada', dialog, 'tria', 'pagar')
})
