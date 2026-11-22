// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './gueraula.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('gueraula', dialog)
})

options.m1__canta.onChoose(() => {
  chooseNarrativeOption('gueraula', dialog, 'm1', 'canta')
})

options.m1__sencera.onChoose(() => {
  chooseNarrativeOption('gueraula', dialog, 'm1', 'sencera')
})

options.m1__adeu.onChoose(() => {
  chooseNarrativeOption('gueraula', dialog, 'm1', 'adeu')
})

options.m2__tint.onChoose(() => {
  chooseNarrativeOption('gueraula', dialog, 'm2', 'tint')
})

options.m2__dormir.onChoose(() => {
  chooseNarrativeOption('gueraula', dialog, 'm2', 'dormir')
})

options.m2__veu.onChoose(() => {
  chooseNarrativeOption('gueraula', dialog, 'm2', 'veu')
})

options.m2__barbes.onChoose(() => {
  chooseNarrativeOption('gueraula', dialog, 'm2', 'barbes')
})

options.m2__llest.onChoose(() => {
  chooseNarrativeOption('gueraula', dialog, 'm2', 'llest')
})

options.m2__falta.onChoose(() => {
  chooseNarrativeOption('gueraula', dialog, 'm2', 'falta')
})

options.m2__adeu2.onChoose(() => {
  chooseNarrativeOption('gueraula', dialog, 'm2', 'adeu2')
})
