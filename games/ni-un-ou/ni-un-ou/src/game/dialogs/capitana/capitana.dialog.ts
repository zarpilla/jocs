// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './capitana.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('capitana', dialog)
})

options.revisio_menu__juana.onChoose(() => {
  chooseNarrativeOption('capitana', dialog, 'revisio_menu', 'juana')
})

options.revisio_menu__gasoil.onChoose(() => {
  chooseNarrativeOption('capitana', dialog, 'revisio_menu', 'gasoil')
})

options.revisio_menu__nadia.onChoose(() => {
  chooseNarrativeOption('capitana', dialog, 'revisio_menu', 'nadia')
})

options.revisio_menu__valvula.onChoose(() => {
  chooseNarrativeOption('capitana', dialog, 'revisio_menu', 'valvula')
})

options.revisio_menu__fi.onChoose(() => {
  chooseNarrativeOption('capitana', dialog, 'revisio_menu', 'fi')
})

options.esc8g__reunir.onChoose(() => {
  chooseNarrativeOption('capitana', dialog, 'esc8g', 'reunir')
})

options.esc8g__encara.onChoose(() => {
  chooseNarrativeOption('capitana', dialog, 'esc8g', 'encara')
})

options.esc8__reunir.onChoose(() => {
  chooseNarrativeOption('capitana', dialog, 'esc8', 'reunir')
})

options.esc8__encara.onChoose(() => {
  chooseNarrativeOption('capitana', dialog, 'esc8', 'encara')
})
