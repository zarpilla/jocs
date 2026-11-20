// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './txell.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('txell', dialog)
})

options.menu__forta.onChoose(() => {
  chooseNarrativeOption('txell', dialog, 'menu', 'forta')
})

options.menu__germana.onChoose(() => {
  chooseNarrativeOption('txell', dialog, 'menu', 'germana')
})

options.menu__canal7.onChoose(() => {
  chooseNarrativeOption('txell', dialog, 'menu', 'canal7')
})

options.menu__adeu.onChoose(() => {
  chooseNarrativeOption('txell', dialog, 'menu', 'adeu')
})
