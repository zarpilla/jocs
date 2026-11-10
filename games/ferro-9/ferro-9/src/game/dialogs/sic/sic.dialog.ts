// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './sic.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('sic', dialog)
})

options.menu__que_passa.onChoose(() => {
  chooseNarrativeOption('sic', dialog, 'menu', 'que_passa')
})

options.menu__passar.onChoose(() => {
  chooseNarrativeOption('sic', dialog, 'menu', 'passar')
})

options.menu__director.onChoose(() => {
  chooseNarrativeOption('sic', dialog, 'menu', 'director')
})

options.menu__enganyar.onChoose(() => {
  chooseNarrativeOption('sic', dialog, 'menu', 'enganyar')
})

options.menu__adeu.onChoose(() => {
  chooseNarrativeOption('sic', dialog, 'menu', 'adeu')
})
