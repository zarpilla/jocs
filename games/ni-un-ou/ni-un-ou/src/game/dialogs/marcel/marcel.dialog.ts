// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './marcel.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('marcel', dialog)
})

options.revisio_menu__valvula.onChoose(() => {
  chooseNarrativeOption('marcel', dialog, 'revisio_menu', 'valvula')
})

options.revisio_menu__nit.onChoose(() => {
  chooseNarrativeOption('marcel', dialog, 'revisio_menu', 'nit')
})

options.revisio_menu__fi.onChoose(() => {
  chooseNarrativeOption('marcel', dialog, 'revisio_menu', 'fi')
})

options.esc6_menu__gat.onChoose(() => {
  chooseNarrativeOption('marcel', dialog, 'esc6_menu', 'gat')
})

options.esc6_menu__gat_vet.onChoose(() => {
  chooseNarrativeOption('marcel', dialog, 'esc6_menu', 'gat_vet')
})

options.esc6_menu__adeu.onChoose(() => {
  chooseNarrativeOption('marcel', dialog, 'esc6_menu', 'adeu')
})

options.secret__veritat.onChoose(() => {
  chooseNarrativeOption('marcel', dialog, 'secret', 'veritat')
})

options.secret__guardar.onChoose(() => {
  chooseNarrativeOption('marcel', dialog, 'secret', 'guardar')
})

options.secret__capitana.onChoose(() => {
  chooseNarrativeOption('marcel', dialog, 'secret', 'capitana')
})
