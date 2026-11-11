// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './bastida.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('bastida', dialog)
})

options.esc2__revisio.onChoose(() => {
  chooseNarrativeOption('bastida', dialog, 'esc2', 'revisio')
})

options.esc2__mar.onChoose(() => {
  chooseNarrativeOption('bastida', dialog, 'esc2', 'mar')
})

options.esc2__pipa.onChoose(() => {
  chooseNarrativeOption('bastida', dialog, 'esc2', 'pipa')
})

options.esc2__plataforma.onChoose(() => {
  chooseNarrativeOption('bastida', dialog, 'esc2', 'plataforma')
})

options.esc2__adeu.onChoose(() => {
  chooseNarrativeOption('bastida', dialog, 'esc2', 'adeu')
})

options.esc3__temporal.onChoose(() => {
  chooseNarrativeOption('bastida', dialog, 'esc3', 'temporal')
})

options.esc3__tensio.onChoose(() => {
  chooseNarrativeOption('bastida', dialog, 'esc3', 'tensio')
})

options.esc3__mans.onChoose(() => {
  chooseNarrativeOption('bastida', dialog, 'esc3', 'mans')
})

options.esc3__adeu.onChoose(() => {
  chooseNarrativeOption('bastida', dialog, 'esc3', 'adeu')
})

options.esc6__nus.onChoose(() => {
  chooseNarrativeOption('bastida', dialog, 'esc6', 'nus')
})

options.esc6__adeu.onChoose(() => {
  chooseNarrativeOption('bastida', dialog, 'esc6', 'adeu')
})

options.dubte__veritat.onChoose(() => {
  chooseNarrativeOption('bastida', dialog, 'dubte', 'veritat')
})

options.dubte__iri.onChoose(() => {
  chooseNarrativeOption('bastida', dialog, 'dubte', 'iri')
})

options.dubte__cafe.onChoose(() => {
  chooseNarrativeOption('bastida', dialog, 'dubte', 'cafe')
})

options.dubte__arengades.onChoose(() => {
  chooseNarrativeOption('bastida', dialog, 'dubte', 'arengades')
})

options.dubte__mentida.onChoose(() => {
  chooseNarrativeOption('bastida', dialog, 'dubte', 'mentida')
})

options.dubte__diners.onChoose(() => {
  chooseNarrativeOption('bastida', dialog, 'dubte', 'diners')
})

options.dubte__adeu.onChoose(() => {
  chooseNarrativeOption('bastida', dialog, 'dubte', 'adeu')
})
