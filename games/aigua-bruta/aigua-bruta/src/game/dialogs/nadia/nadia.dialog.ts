// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './nadia.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('nadia', dialog)
})

options.revisio__juana.onChoose(() => {
  chooseNarrativeOption('nadia', dialog, 'revisio', 'juana')
})

options.revisio__mareig.onChoose(() => {
  chooseNarrativeOption('nadia', dialog, 'revisio', 'mareig')
})

options.revisio__feina.onChoose(() => {
  chooseNarrativeOption('nadia', dialog, 'revisio', 'feina')
})

options.revisio__fi.onChoose(() => {
  chooseNarrativeOption('nadia', dialog, 'revisio', 'fi')
})

options.esc4__contrasenya.onChoose(() => {
  chooseNarrativeOption('nadia', dialog, 'esc4', 'contrasenya')
})

options.esc4__adeu.onChoose(() => {
  chooseNarrativeOption('nadia', dialog, 'esc4', 'adeu')
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
