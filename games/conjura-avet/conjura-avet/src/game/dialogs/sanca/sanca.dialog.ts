// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './sanca.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('sanca', dialog)
})

options.mi__canem_i.onChoose(() => {
  chooseNarrativeOption('sanca', dialog, 'mi', 'canem_i')
})

options.mi__adeu_i.onChoose(() => {
  chooseNarrativeOption('sanca', dialog, 'mi', 'adeu_i')
})

options.mv__queixa.onChoose(() => {
  chooseNarrativeOption('sanca', dialog, 'mv', 'queixa')
})

options.mv__canem.onChoose(() => {
  chooseNarrativeOption('sanca', dialog, 'mv', 'canem')
})

options.mv__tracte.onChoose(() => {
  chooseNarrativeOption('sanca', dialog, 'mv', 'tracte')
})

options.mv__noms.onChoose(() => {
  chooseNarrativeOption('sanca', dialog, 'mv', 'noms')
})

options.mv__adeu.onChoose(() => {
  chooseNarrativeOption('sanca', dialog, 'mv', 'adeu')
})

options.mm__creu.onChoose(() => {
  chooseNarrativeOption('sanca', dialog, 'mm', 'creu')
})

options.mm__adeu_m.onChoose(() => {
  chooseNarrativeOption('sanca', dialog, 'mm', 'adeu_m')
})
