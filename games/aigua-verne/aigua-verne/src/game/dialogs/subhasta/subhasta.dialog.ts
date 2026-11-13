// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './subhasta.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('subhasta', dialog)
})

options.inici__oferta.onChoose(() => {
  chooseNarrativeOption('subhasta', dialog, 'inici', 'oferta')
})

options.inici__contracte.onChoose(() => {
  chooseNarrativeOption('subhasta', dialog, 'inici', 'contracte')
})

options.inici__cava.onChoose(() => {
  chooseNarrativeOption('subhasta', dialog, 'inici', 'cava')
})

options.inici__peixos.onChoose(() => {
  chooseNarrativeOption('subhasta', dialog, 'inici', 'peixos')
})

options.inici__adeu.onChoose(() => {
  chooseNarrativeOption('subhasta', dialog, 'inici', 'adeu')
})
