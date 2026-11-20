// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './tomas.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('tomas', dialog)
})

options.revisio_menu__juana.onChoose(() => {
  chooseNarrativeOption('tomas', dialog, 'revisio_menu', 'juana')
})

options.revisio_menu__clau.onChoose(() => {
  chooseNarrativeOption('tomas', dialog, 'revisio_menu', 'clau')
})

options.revisio_menu__nit.onChoose(() => {
  chooseNarrativeOption('tomas', dialog, 'revisio_menu', 'nit')
})

options.revisio_menu__cremades.onChoose(() => {
  chooseNarrativeOption('tomas', dialog, 'revisio_menu', 'cremades')
})

options.revisio_menu__menjar.onChoose(() => {
  chooseNarrativeOption('tomas', dialog, 'revisio_menu', 'menjar')
})

options.revisio_menu__fi.onChoose(() => {
  chooseNarrativeOption('tomas', dialog, 'revisio_menu', 'fi')
})

options.esc7_menu__clau7.onChoose(() => {
  chooseNarrativeOption('tomas', dialog, 'esc7_menu', 'clau7')
})

options.esc7_menu__passa7.onChoose(() => {
  chooseNarrativeOption('tomas', dialog, 'esc7_menu', 'passa7')
})

options.esc7_menu__entrepa7.onChoose(() => {
  chooseNarrativeOption('tomas', dialog, 'esc7_menu', 'entrepa7')
})

options.esc7_menu__adeu.onChoose(() => {
  chooseNarrativeOption('tomas', dialog, 'esc7_menu', 'adeu')
})
