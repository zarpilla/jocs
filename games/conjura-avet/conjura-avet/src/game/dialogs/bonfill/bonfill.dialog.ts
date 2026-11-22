// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './bonfill.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('bonfill', dialog)
})

options.mp__llegir.onChoose(() => {
  chooseNarrativeOption('bonfill', dialog, 'mp', 'llegir')
})

options.mp__pare.onChoose(() => {
  chooseNarrativeOption('bonfill', dialog, 'mp', 'pare')
})

options.mp__adeu.onChoose(() => {
  chooseNarrativeOption('bonfill', dialog, 'mp', 'adeu')
})

options.ss__ora.onChoose(() => {
  chooseNarrativeOption('bonfill', dialog, 'ss', 'ora')
})

options.ss__pax.onChoose(() => {
  chooseNarrativeOption('bonfill', dialog, 'ss', 'pax')
})

options.ss__visca.onChoose(() => {
  chooseNarrativeOption('bonfill', dialog, 'ss', 'visca')
})

options.ss__tres.onChoose(() => {
  chooseNarrativeOption('bonfill', dialog, 'ss', 'tres')
})

options.ss__fuig.onChoose(() => {
  chooseNarrativeOption('bonfill', dialog, 'ss', 'fuig')
})

options.ms__dona.onChoose(() => {
  chooseNarrativeOption('bonfill', dialog, 'ms', 'dona')
})

options.ms__fuig2.onChoose(() => {
  chooseNarrativeOption('bonfill', dialog, 'ms', 'fuig2')
})

options.mn__dir.onChoose(() => {
  chooseNarrativeOption('bonfill', dialog, 'mn', 'dir')
})

options.mn__assenyala.onChoose(() => {
  chooseNarrativeOption('bonfill', dialog, 'mn', 'assenyala')
})

options.mn__tos.onChoose(() => {
  chooseNarrativeOption('bonfill', dialog, 'mn', 'tos')
})
