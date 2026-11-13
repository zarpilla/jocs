// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './comunicador.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('comunicador', dialog)
})

options.inici__fem.onChoose(() => {
  chooseNarrativeOption('comunicador', dialog, 'inici', 'fem')
})

options.inici__preu.onChoose(() => {
  chooseNarrativeOption('comunicador', dialog, 'inici', 'preu')
})

options.inici__adeu.onChoose(() => {
  chooseNarrativeOption('comunicador', dialog, 'inici', 'adeu')
})
