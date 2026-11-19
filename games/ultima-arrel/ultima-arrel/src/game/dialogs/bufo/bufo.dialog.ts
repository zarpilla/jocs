// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './bufo.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('bufo', dialog)
})

options.menu__paper.onChoose(() => {
  chooseNarrativeOption('bufo', dialog, 'menu', 'paper')
})

options.menu__paper2.onChoose(() => {
  chooseNarrativeOption('bufo', dialog, 'menu', 'paper2')
})

options.menu__rierol.onChoose(() => {
  chooseNarrativeOption('bufo', dialog, 'menu', 'rierol')
})

options.menu__tramit.onChoose(() => {
  chooseNarrativeOption('bufo', dialog, 'menu', 'tramit')
})

options.menu__adeu.onChoose(() => {
  chooseNarrativeOption('bufo', dialog, 'menu', 'adeu')
})
