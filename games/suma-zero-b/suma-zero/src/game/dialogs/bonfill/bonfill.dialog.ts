// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './bonfill.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('bonfill', dialog)
})

options.q_maleti__secrets.onChoose(() => {
  chooseNarrativeOption('bonfill', dialog, 'q_maleti', 'secrets')
})

options.q_maleti__avio.onChoose(() => {
  chooseNarrativeOption('bonfill', dialog, 'q_maleti', 'avio')
})

options.q_maleti__nuvols.onChoose(() => {
  chooseNarrativeOption('bonfill', dialog, 'q_maleti', 'nuvols')
})

options.q_jove__directives.onChoose(() => {
  chooseNarrativeOption('bonfill', dialog, 'q_jove', 'directives')
})

options.q_jove__acreditacio.onChoose(() => {
  chooseNarrativeOption('bonfill', dialog, 'q_jove', 'acreditacio')
})

options.q_jove__crema.onChoose(() => {
  chooseNarrativeOption('bonfill', dialog, 'q_jove', 'crema')
})

options.q_banca__cordons.onChoose(() => {
  chooseNarrativeOption('bonfill', dialog, 'q_banca', 'cordons')
})

options.q_banca__cor.onChoose(() => {
  chooseNarrativeOption('bonfill', dialog, 'q_banca', 'cor')
})

options.q_banca__dacord.onChoose(() => {
  chooseNarrativeOption('bonfill', dialog, 'q_banca', 'dacord')
})

options.q_gos__rockefeller.onChoose(() => {
  chooseNarrativeOption('bonfill', dialog, 'q_gos', 'rockefeller')
})

options.q_gos__gats.onChoose(() => {
  chooseNarrativeOption('bonfill', dialog, 'q_gos', 'gats')
})

options.q_veure__seguretat.onChoose(() => {
  chooseNarrativeOption('bonfill', dialog, 'q_veure', 'seguretat')
})

options.q_veure__caixes.onChoose(() => {
  chooseNarrativeOption('bonfill', dialog, 'q_veure', 'caixes')
})

options.q_veure__comptes.onChoose(() => {
  chooseNarrativeOption('bonfill', dialog, 'q_veure', 'comptes')
})

options.q_veure__tecnics.onChoose(() => {
  chooseNarrativeOption('bonfill', dialog, 'q_veure', 'tecnics')
})

options.q_veure2__seguretat.onChoose(() => {
  chooseNarrativeOption('bonfill', dialog, 'q_veure2', 'seguretat')
})

options.q_veure2__caixes.onChoose(() => {
  chooseNarrativeOption('bonfill', dialog, 'q_veure2', 'caixes')
})

options.q_veure2__comptes.onChoose(() => {
  chooseNarrativeOption('bonfill', dialog, 'q_veure2', 'comptes')
})

options.q_veure2__tecnics.onChoose(() => {
  chooseNarrativeOption('bonfill', dialog, 'q_veure2', 'tecnics')
})
