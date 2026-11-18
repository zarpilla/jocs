// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './fidel.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('fidel', dialog)
})

options.menu__inversora.onChoose(() => {
  chooseNarrativeOption('fidel', dialog, 'menu', 'inversora')
})

options.menu__servei.onChoose(() => {
  chooseNarrativeOption('fidel', dialog, 'menu', 'servei')
})

options.menu__qui.onChoose(() => {
  chooseNarrativeOption('fidel', dialog, 'menu', 'qui')
})

options.menu__adeu.onChoose(() => {
  chooseNarrativeOption('fidel', dialog, 'menu', 'adeu')
})

options.aval__escriptura.onChoose(() => {
  chooseNarrativeOption('fidel', dialog, 'aval', 'escriptura')
})

options.aval__contracte.onChoose(() => {
  chooseNarrativeOption('fidel', dialog, 'aval', 'contracte')
})

options.aval__sac.onChoose(() => {
  chooseNarrativeOption('fidel', dialog, 'aval', 'sac')
})

options.aval__res.onChoose(() => {
  chooseNarrativeOption('fidel', dialog, 'aval', 'res')
})
