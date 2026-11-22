// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './ermessenda.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('ermessenda', dialog)
})

options.m__comporta.onChoose(() => {
  chooseNarrativeOption('ermessenda', dialog, 'm', 'comporta')
})

options.m__adeu.onChoose(() => {
  chooseNarrativeOption('ermessenda', dialog, 'm', 'adeu')
})
