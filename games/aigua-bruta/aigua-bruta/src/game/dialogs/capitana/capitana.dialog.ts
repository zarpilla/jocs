// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './capitana.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('capitana', dialog)
})

options.revisio__juana.onChoose(() => {
  chooseNarrativeOption('capitana', dialog, 'revisio', 'juana')
})

options.revisio__gasoil.onChoose(() => {
  chooseNarrativeOption('capitana', dialog, 'revisio', 'gasoil')
})

options.revisio__nadia.onChoose(() => {
  chooseNarrativeOption('capitana', dialog, 'revisio', 'nadia')
})

options.revisio__valvula.onChoose(() => {
  chooseNarrativeOption('capitana', dialog, 'revisio', 'valvula')
})

options.revisio__fi.onChoose(() => {
  chooseNarrativeOption('capitana', dialog, 'revisio', 'fi')
})
