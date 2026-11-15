// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './paperets.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('paperets', dialog)
})

options.proposta__flam.onChoose(() => {
  chooseNarrativeOption('paperets', dialog, 'proposta', 'flam')
})

options.proposta__ernest.onChoose(() => {
  chooseNarrativeOption('paperets', dialog, 'proposta', 'ernest')
})

options.proposta__postres.onChoose(() => {
  chooseNarrativeOption('paperets', dialog, 'proposta', 'postres')
})

options.proposta__adeu.onChoose(() => {
  chooseNarrativeOption('paperets', dialog, 'proposta', 'adeu')
})
