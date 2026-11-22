// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './ponc.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('ponc', dialog)
})

options.m0__culpa.onChoose(() => {
  chooseNarrativeOption('ponc', dialog, 'm0', 'culpa')
})

options.m0__adeu0.onChoose(() => {
  chooseNarrativeOption('ponc', dialog, 'm0', 'adeu0')
})

options.mo__insistir.onChoose(() => {
  chooseNarrativeOption('ponc', dialog, 'mo', 'insistir')
})

options.mo__ell.onChoose(() => {
  chooseNarrativeOption('ponc', dialog, 'mo', 'ell')
})

options.mo__privat.onChoose(() => {
  chooseNarrativeOption('ponc', dialog, 'mo', 'privat')
})

options.mo__adeu_o.onChoose(() => {
  chooseNarrativeOption('ponc', dialog, 'mo', 'adeu_o')
})

options.m1v__signe.onChoose(() => {
  chooseNarrativeOption('ponc', dialog, 'm1v', 'signe')
})

options.m1v__pare.onChoose(() => {
  chooseNarrativeOption('ponc', dialog, 'm1v', 'pare')
})

options.m1v__adeu1.onChoose(() => {
  chooseNarrativeOption('ponc', dialog, 'm1v', 'adeu1')
})

options.m1i__pare_i.onChoose(() => {
  chooseNarrativeOption('ponc', dialog, 'm1i', 'pare_i')
})

options.m1i__adeu1i.onChoose(() => {
  chooseNarrativeOption('ponc', dialog, 'm1i', 'adeu1i')
})

options.mati__adeu7.onChoose(() => {
  chooseNarrativeOption('ponc', dialog, 'mati', 'adeu7')
})
