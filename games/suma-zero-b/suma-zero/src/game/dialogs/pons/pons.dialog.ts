// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './pons.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('pons', dialog)
})

options.menu__escoltar.onChoose(() => {
  chooseNarrativeOption('pons', dialog, 'menu', 'escoltar')
})

options.menu__ue.onChoose(() => {
  chooseNarrativeOption('pons', dialog, 'menu', 'ue')
})

options.menu__per_que.onChoose(() => {
  chooseNarrativeOption('pons', dialog, 'menu', 'per_que')
})

options.menu__adeu.onChoose(() => {
  chooseNarrativeOption('pons', dialog, 'menu', 'adeu')
})
