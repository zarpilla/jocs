// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './fitxes.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('fitxes', dialog)
})

options.tria__capitana.onChoose(() => {
  chooseNarrativeOption('fitxes', dialog, 'tria', 'capitana')
})

options.tria__tomas.onChoose(() => {
  chooseNarrativeOption('fitxes', dialog, 'tria', 'tomas')
})

options.tria__nadia.onChoose(() => {
  chooseNarrativeOption('fitxes', dialog, 'tria', 'nadia')
})

options.tria__marcel.onChoose(() => {
  chooseNarrativeOption('fitxes', dialog, 'tria', 'marcel')
})

options.tria__bastida.onChoose(() => {
  chooseNarrativeOption('fitxes', dialog, 'tria', 'bastida')
})

options.tria__juana.onChoose(() => {
  chooseNarrativeOption('fitxes', dialog, 'tria', 'juana')
})

options.tria__cap.onChoose(() => {
  chooseNarrativeOption('fitxes', dialog, 'tria', 'cap')
})
