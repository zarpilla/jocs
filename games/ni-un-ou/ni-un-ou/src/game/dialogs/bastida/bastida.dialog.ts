// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './bastida.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('bastida', dialog)
})

options.esc2_menu__pipa.onChoose(() => {
  chooseNarrativeOption('bastida', dialog, 'esc2_menu', 'pipa')
})

options.esc2_menu__revisio.onChoose(() => {
  chooseNarrativeOption('bastida', dialog, 'esc2_menu', 'revisio')
})

options.esc2_menu__plataforma.onChoose(() => {
  chooseNarrativeOption('bastida', dialog, 'esc2_menu', 'plataforma')
})

options.esc2_menu__mar.onChoose(() => {
  chooseNarrativeOption('bastida', dialog, 'esc2_menu', 'mar')
})

options.esc2_menu__adeu.onChoose(() => {
  chooseNarrativeOption('bastida', dialog, 'esc2_menu', 'adeu')
})

options.esc3_menu__temporal.onChoose(() => {
  chooseNarrativeOption('bastida', dialog, 'esc3_menu', 'temporal')
})

options.esc3_menu__tensio.onChoose(() => {
  chooseNarrativeOption('bastida', dialog, 'esc3_menu', 'tensio')
})

options.esc3_menu__mans.onChoose(() => {
  chooseNarrativeOption('bastida', dialog, 'esc3_menu', 'mans')
})

options.esc3_menu__adeu.onChoose(() => {
  chooseNarrativeOption('bastida', dialog, 'esc3_menu', 'adeu')
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
