// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './trucada.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('trucada', dialog)
})

options.inici__si.onChoose(() => {
  chooseNarrativeOption('trucada', dialog, 'inici', 'si')
})

options.inici__no.onChoose(() => {
  chooseNarrativeOption('trucada', dialog, 'inici', 'no')
})

options.inici__pou.onChoose(() => {
  chooseNarrativeOption('trucada', dialog, 'inici', 'pou')
})
