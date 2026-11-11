// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './tomas.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('tomas', dialog)
})

options.revisio__juana.onChoose(() => {
  chooseNarrativeOption('tomas', dialog, 'revisio', 'juana')
})

options.revisio__clau.onChoose(() => {
  chooseNarrativeOption('tomas', dialog, 'revisio', 'clau')
})

options.revisio__nit.onChoose(() => {
  chooseNarrativeOption('tomas', dialog, 'revisio', 'nit')
})

options.revisio__fi.onChoose(() => {
  chooseNarrativeOption('tomas', dialog, 'revisio', 'fi')
})

options.esc7__clau7.onChoose(() => {
  chooseNarrativeOption('tomas', dialog, 'esc7', 'clau7')
})

options.esc7__entrepa7.onChoose(() => {
  chooseNarrativeOption('tomas', dialog, 'esc7', 'entrepa7')
})

options.esc7__adeu.onChoose(() => {
  chooseNarrativeOption('tomas', dialog, 'esc7', 'adeu')
})
