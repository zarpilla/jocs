// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './marcel.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('marcel', dialog)
})

options.revisio__valvula.onChoose(() => {
  chooseNarrativeOption('marcel', dialog, 'revisio', 'valvula')
})

options.revisio__nit.onChoose(() => {
  chooseNarrativeOption('marcel', dialog, 'revisio', 'nit')
})

options.revisio__fi.onChoose(() => {
  chooseNarrativeOption('marcel', dialog, 'revisio', 'fi')
})

options.esc6__gat.onChoose(() => {
  chooseNarrativeOption('marcel', dialog, 'esc6', 'gat')
})

options.esc6__gat_vet.onChoose(() => {
  chooseNarrativeOption('marcel', dialog, 'esc6', 'gat_vet')
})

options.esc6__adeu.onChoose(() => {
  chooseNarrativeOption('marcel', dialog, 'esc6', 'adeu')
})

options.secret__guardar.onChoose(() => {
  chooseNarrativeOption('marcel', dialog, 'secret', 'guardar')
})

options.secret__veritat.onChoose(() => {
  chooseNarrativeOption('marcel', dialog, 'secret', 'veritat')
})

options.secret__capitana.onChoose(() => {
  chooseNarrativeOption('marcel', dialog, 'secret', 'capitana')
})
