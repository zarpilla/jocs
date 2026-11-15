// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './teclat.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('teclat', dialog)
})

options.inici__maria.onChoose(() => {
  chooseNarrativeOption('teclat', dialog, 'inici', 'maria')
})

options.inici__verne.onChoose(() => {
  chooseNarrativeOption('teclat', dialog, 'inici', 'verne')
})

options.inici__titus.onChoose(() => {
  chooseNarrativeOption('teclat', dialog, 'inici', 'titus')
})

options.inici__deixa.onChoose(() => {
  chooseNarrativeOption('teclat', dialog, 'inici', 'deixa')
})
