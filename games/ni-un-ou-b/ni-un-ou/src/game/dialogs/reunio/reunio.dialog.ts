// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './reunio.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('reunio', dialog)
})

options.qui__bastida.onChoose(() => {
  chooseNarrativeOption('reunio', dialog, 'qui', 'bastida')
})

options.qui__marcel.onChoose(() => {
  chooseNarrativeOption('reunio', dialog, 'qui', 'marcel')
})

options.qui__nadia.onChoose(() => {
  chooseNarrativeOption('reunio', dialog, 'qui', 'nadia')
})

options.qui__tomas.onChoose(() => {
  chooseNarrativeOption('reunio', dialog, 'qui', 'tomas')
})

options.qui__capitana.onChoose(() => {
  chooseNarrativeOption('reunio', dialog, 'qui', 'capitana')
})

options.qui__pensar.onChoose(() => {
  chooseNarrativeOption('reunio', dialog, 'qui', 'pensar')
})

options.proves__cisalla.onChoose(() => {
  chooseNarrativeOption('reunio', dialog, 'proves', 'cisalla')
})

options.proves__ma.onChoose(() => {
  chooseNarrativeOption('reunio', dialog, 'proves', 'ma')
})

options.proves__pipa.onChoose(() => {
  chooseNarrativeOption('reunio', dialog, 'proves', 'pipa')
})

options.proves__nus.onChoose(() => {
  chooseNarrativeOption('reunio', dialog, 'proves', 'nus')
})

options.proves__correu.onChoose(() => {
  chooseNarrativeOption('reunio', dialog, 'proves', 'correu')
})

options.proves__cambra.onChoose(() => {
  chooseNarrativeOption('reunio', dialog, 'proves', 'cambra')
})

options.proves__gat.onChoose(() => {
  chooseNarrativeOption('reunio', dialog, 'proves', 'gat')
})

options.proves__croissant.onChoose(() => {
  chooseNarrativeOption('reunio', dialog, 'proves', 'croissant')
})

options.proves__escaner.onChoose(() => {
  chooseNarrativeOption('reunio', dialog, 'proves', 'escaner')
})

options.proves__clau.onChoose(() => {
  chooseNarrativeOption('reunio', dialog, 'proves', 'clau')
})

options.proves__blaunet.onChoose(() => {
  chooseNarrativeOption('reunio', dialog, 'proves', 'blaunet')
})

options.proves__enrere.onChoose(() => {
  chooseNarrativeOption('reunio', dialog, 'proves', 'enrere')
})

options.compta__iri.onChoose(() => {
  chooseNarrativeOption('reunio', dialog, 'compta', 'iri')
})
