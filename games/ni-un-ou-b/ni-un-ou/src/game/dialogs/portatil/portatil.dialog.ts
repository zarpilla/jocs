// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './portatil.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('portatil', dialog)
})

options.contrasenya__esperanca.onChoose(() => {
  chooseNarrativeOption('portatil', dialog, 'contrasenya', 'esperanca')
})

options.contrasenya__pili.onChoose(() => {
  chooseNarrativeOption('portatil', dialog, 'contrasenya', 'pili')
})

options.contrasenya__pilar.onChoose(() => {
  chooseNarrativeOption('portatil', dialog, 'contrasenya', 'pilar')
})

options.contrasenya__juana.onChoose(() => {
  chooseNarrativeOption('portatil', dialog, 'contrasenya', 'juana')
})

options.contrasenya__adeu.onChoose(() => {
  chooseNarrativeOption('portatil', dialog, 'contrasenya', 'adeu')
})
