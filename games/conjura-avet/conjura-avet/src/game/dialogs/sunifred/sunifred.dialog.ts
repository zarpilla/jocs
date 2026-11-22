// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './sunifred.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('sunifred', dialog)
})

options.m1__signe.onChoose(() => {
  chooseNarrativeOption('sunifred', dialog, 'm1', 'signe')
})

options.m1__nit.onChoose(() => {
  chooseNarrativeOption('sunifred', dialog, 'm1', 'nit')
})

options.m1__adeu.onChoose(() => {
  chooseNarrativeOption('sunifred', dialog, 'm1', 'adeu')
})

options.mc__ofici.onChoose(() => {
  chooseNarrativeOption('sunifred', dialog, 'mc', 'ofici')
})

options.mc__vi.onChoose(() => {
  chooseNarrativeOption('sunifred', dialog, 'mc', 'vi')
})

options.mc__adeu_c.onChoose(() => {
  chooseNarrativeOption('sunifred', dialog, 'mc', 'adeu_c')
})

options.s7__adeu7.onChoose(() => {
  chooseNarrativeOption('sunifred', dialog, 's7', 'adeu7')
})
