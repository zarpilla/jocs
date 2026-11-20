// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './subhasta.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('subhasta', dialog)
})

options.inici__c7788.onChoose(() => {
  chooseNarrativeOption('subhasta', dialog, 'inici', 'c7788')
})

options.inici__anima.onChoose(() => {
  chooseNarrativeOption('subhasta', dialog, 'inici', 'anima')
})

options.inici__peixos.onChoose(() => {
  chooseNarrativeOption('subhasta', dialog, 'inici', 'peixos')
})

options.inici__adeu.onChoose(() => {
  chooseNarrativeOption('subhasta', dialog, 'inici', 'adeu')
})
