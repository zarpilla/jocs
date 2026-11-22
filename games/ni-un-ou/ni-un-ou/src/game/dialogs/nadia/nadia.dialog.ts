// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './nadia.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('nadia', dialog)
})

options.revisio_menu__juana.onChoose(() => {
  chooseNarrativeOption('nadia', dialog, 'revisio_menu', 'juana')
})

options.revisio_menu__mareig.onChoose(() => {
  chooseNarrativeOption('nadia', dialog, 'revisio_menu', 'mareig')
})

options.revisio_menu__feina.onChoose(() => {
  chooseNarrativeOption('nadia', dialog, 'revisio_menu', 'feina')
})

options.revisio_menu__esmorzar.onChoose(() => {
  chooseNarrativeOption('nadia', dialog, 'revisio_menu', 'esmorzar')
})

options.revisio_menu__capcalera.onChoose(() => {
  chooseNarrativeOption('nadia', dialog, 'revisio_menu', 'capcalera')
})

options.revisio_menu__fi.onChoose(() => {
  chooseNarrativeOption('nadia', dialog, 'revisio_menu', 'fi')
})

options.pillada__denunciar.onChoose(() => {
  chooseNarrativeOption('nadia', dialog, 'pillada', 'denunciar')
})

options.pillada__aliar.onChoose(() => {
  chooseNarrativeOption('nadia', dialog, 'pillada', 'aliar')
})

options.esc6__soroll.onChoose(() => {
  chooseNarrativeOption('nadia', dialog, 'esc6', 'soroll')
})

options.esc6__adeu.onChoose(() => {
  chooseNarrativeOption('nadia', dialog, 'esc6', 'adeu')
})
