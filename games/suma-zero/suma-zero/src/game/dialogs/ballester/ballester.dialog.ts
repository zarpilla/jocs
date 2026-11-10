// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './ballester.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('ballester', dialog)
})

options.menu__seguretat.onChoose(() => {
  chooseNarrativeOption('ballester', dialog, 'menu', 'seguretat')
})

options.menu__collaret.onChoose(() => {
  chooseNarrativeOption('ballester', dialog, 'menu', 'collaret')
})

options.menu__serie.onChoose(() => {
  chooseNarrativeOption('ballester', dialog, 'menu', 'serie')
})

options.menu__adeu.onChoose(() => {
  chooseNarrativeOption('ballester', dialog, 'menu', 'adeu')
})

options.eines__cantar.onChoose(() => {
  chooseNarrativeOption('ballester', dialog, 'eines', 'cantar')
})

options.eines__banquers.onChoose(() => {
  chooseNarrativeOption('ballester', dialog, 'eines', 'banquers')
})

options.eines__euros.onChoose(() => {
  chooseNarrativeOption('ballester', dialog, 'eines', 'euros')
})

options.eines__auditor.onChoose(() => {
  chooseNarrativeOption('ballester', dialog, 'eines', 'auditor')
})

options.eines__violi.onChoose(() => {
  chooseNarrativeOption('ballester', dialog, 'eines', 'violi')
})

options.eines__vidua.onChoose(() => {
  chooseNarrativeOption('ballester', dialog, 'eines', 'vidua')
})

options.eines__serie_sync.onChoose(() => {
  chooseNarrativeOption('ballester', dialog, 'eines', 'serie_sync')
})

options.eines__adeu.onChoose(() => {
  chooseNarrativeOption('ballester', dialog, 'eines', 'adeu')
})

options.clau_relaxat__veritat.onChoose(() => {
  chooseNarrativeOption('ballester', dialog, 'clau_relaxat', 'veritat')
})

options.clau_relaxat__mentida.onChoose(() => {
  chooseNarrativeOption('ballester', dialog, 'clau_relaxat', 'mentida')
})

options.clau_tens__or.onChoose(() => {
  chooseNarrativeOption('ballester', dialog, 'clau_tens', 'or')
})

options.clau_tens__adeu.onChoose(() => {
  chooseNarrativeOption('ballester', dialog, 'clau_tens', 'adeu')
})
