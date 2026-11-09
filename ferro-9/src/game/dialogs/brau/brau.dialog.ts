// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './brau.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('brau', dialog)
})

options.menu__que_passa.onChoose(() => {
  chooseNarrativeOption('brau', dialog, 'menu', 'que_passa')
})

options.menu__passar.onChoose(() => {
  chooseNarrativeOption('brau', dialog, 'menu', 'passar')
})

options.menu__director.onChoose(() => {
  chooseNarrativeOption('brau', dialog, 'menu', 'director')
})

options.menu__enganyar.onChoose(() => {
  chooseNarrativeOption('brau', dialog, 'menu', 'enganyar')
})

options.menu__adeu.onChoose(() => {
  chooseNarrativeOption('brau', dialog, 'menu', 'adeu')
})
