// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './holm.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('holm', dialog)
})

options.q__llavors.onChoose(() => {
  chooseNarrativeOption('holm', dialog, 'q', 'llavors')
})

options.q__vestit.onChoose(() => {
  chooseNarrativeOption('holm', dialog, 'q', 'vestit')
})

options.q__magnat.onChoose(() => {
  chooseNarrativeOption('holm', dialog, 'q', 'magnat')
})
