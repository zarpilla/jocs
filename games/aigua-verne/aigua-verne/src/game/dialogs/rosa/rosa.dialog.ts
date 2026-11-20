// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './rosa.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('rosa', dialog)
})

options.menu__vaga.onChoose(() => {
  chooseNarrativeOption('rosa', dialog, 'menu', 'vaga')
})

options.menu__vestit.onChoose(() => {
  chooseNarrativeOption('rosa', dialog, 'menu', 'vestit')
})

options.menu__vestit_cas.onChoose(() => {
  chooseNarrativeOption('rosa', dialog, 'menu', 'vestit_cas')
})

options.menu__vestit_tomas.onChoose(() => {
  chooseNarrativeOption('rosa', dialog, 'menu', 'vestit_tomas')
})

options.menu__tomas.onChoose(() => {
  chooseNarrativeOption('rosa', dialog, 'menu', 'tomas')
})

options.menu__adeu.onChoose(() => {
  chooseNarrativeOption('rosa', dialog, 'menu', 'adeu')
})
