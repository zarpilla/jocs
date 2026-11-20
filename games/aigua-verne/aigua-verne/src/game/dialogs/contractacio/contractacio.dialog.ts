// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './contractacio.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('contractacio', dialog)
})

options.inici__no.onChoose(() => {
  chooseNarrativeOption('contractacio', dialog, 'inici', 'no')
})

options.inici__si.onChoose(() => {
  chooseNarrativeOption('contractacio', dialog, 'inici', 'si')
})

options.inici__deixa.onChoose(() => {
  chooseNarrativeOption('contractacio', dialog, 'inici', 'deixa')
})

options.p2__h24.onChoose(() => {
  chooseNarrativeOption('contractacio', dialog, 'p2', 'h24')
})

options.p2__h9.onChoose(() => {
  chooseNarrativeOption('contractacio', dialog, 'p2', 'h9')
})

options.p3__aigua_si.onChoose(() => {
  chooseNarrativeOption('contractacio', dialog, 'p3', 'aigua_si')
})

options.p3__aigua_no.onChoose(() => {
  chooseNarrativeOption('contractacio', dialog, 'p3', 'aigua_no')
})
