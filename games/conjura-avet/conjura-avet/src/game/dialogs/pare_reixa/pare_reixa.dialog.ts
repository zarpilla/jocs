// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './pare_reixa.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('pare_reixa', dialog)
})

options.m__serra.onChoose(() => {
  chooseNarrativeOption('pare_reixa', dialog, 'm', 'serra')
})

options.m__be.onChoose(() => {
  chooseNarrativeOption('pare_reixa', dialog, 'm', 'be')
})

options.m__adeu.onChoose(() => {
  chooseNarrativeOption('pare_reixa', dialog, 'm', 'adeu')
})
