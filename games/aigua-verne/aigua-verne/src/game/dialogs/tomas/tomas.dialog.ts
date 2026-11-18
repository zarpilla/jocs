// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './tomas.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('tomas', dialog)
})

options.menu__pilot.onChoose(() => {
  chooseNarrativeOption('tomas', dialog, 'menu', 'pilot')
})

options.menu__clau.onChoose(() => {
  chooseNarrativeOption('tomas', dialog, 'menu', 'clau')
})

options.menu__contracte.onChoose(() => {
  chooseNarrativeOption('tomas', dialog, 'menu', 'contracte')
})

options.menu__paper.onChoose(() => {
  chooseNarrativeOption('tomas', dialog, 'menu', 'paper')
})

options.menu__adeu.onChoose(() => {
  chooseNarrativeOption('tomas', dialog, 'menu', 'adeu')
})

options.enxampat__venut.onChoose(() => {
  chooseNarrativeOption('tomas', dialog, 'enxampat', 'venut')
})

options.enxampat__capitana.onChoose(() => {
  chooseNarrativeOption('tomas', dialog, 'enxampat', 'capitana')
})

options.enxampat__per_que.onChoose(() => {
  chooseNarrativeOption('tomas', dialog, 'enxampat', 'per_que')
})

options.enxampat__volar.onChoose(() => {
  chooseNarrativeOption('tomas', dialog, 'enxampat', 'volar')
})

options.enxampat__iri.onChoose(() => {
  chooseNarrativeOption('tomas', dialog, 'enxampat', 'iri')
})

options.enxampat2__venut.onChoose(() => {
  chooseNarrativeOption('tomas', dialog, 'enxampat2', 'venut')
})

options.enxampat2__capitana.onChoose(() => {
  chooseNarrativeOption('tomas', dialog, 'enxampat2', 'capitana')
})

options.enxampat2__per_que.onChoose(() => {
  chooseNarrativeOption('tomas', dialog, 'enxampat2', 'per_que')
})

options.enxampat2__volar.onChoose(() => {
  chooseNarrativeOption('tomas', dialog, 'enxampat2', 'volar')
})

options.enxampat2__iri.onChoose(() => {
  chooseNarrativeOption('tomas', dialog, 'enxampat2', 'iri')
})

options.girat__informe.onChoose(() => {
  chooseNarrativeOption('tomas', dialog, 'girat', 'informe')
})

options.girat__adeu2.onChoose(() => {
  chooseNarrativeOption('tomas', dialog, 'girat', 'adeu2')
})
