// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './directora.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('directora', dialog)
})

options.menu__que_vol.onChoose(() => {
  chooseNarrativeOption('directora', dialog, 'menu', 'que_vol')
})

options.menu__iri.onChoose(() => {
  chooseNarrativeOption('directora', dialog, 'menu', 'iri')
})

options.menu__pacte.onChoose(() => {
  chooseNarrativeOption('directora', dialog, 'menu', 'pacte')
})

options.menu__no.onChoose(() => {
  chooseNarrativeOption('directora', dialog, 'menu', 'no')
})

options.menu__adeu.onChoose(() => {
  chooseNarrativeOption('directora', dialog, 'menu', 'adeu')
})

options.menu__adeu_pacte.onChoose(() => {
  chooseNarrativeOption('directora', dialog, 'menu', 'adeu_pacte')
})
