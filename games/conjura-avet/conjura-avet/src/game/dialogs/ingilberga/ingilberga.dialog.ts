// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './ingilberga.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('ingilberga', dialog)
})

options.m1__signe.onChoose(() => {
  chooseNarrativeOption('ingilberga', dialog, 'm1', 'signe')
})

options.m1__ordre.onChoose(() => {
  chooseNarrativeOption('ingilberga', dialog, 'm1', 'ordre')
})

options.m1__arxiu.onChoose(() => {
  chooseNarrativeOption('ingilberga', dialog, 'm1', 'arxiu')
})

options.m1__entrar_no.onChoose(() => {
  chooseNarrativeOption('ingilberga', dialog, 'm1', 'entrar_no')
})

options.m1__entrar.onChoose(() => {
  chooseNarrativeOption('ingilberga', dialog, 'm1', 'entrar')
})

options.m1__adeu.onChoose(() => {
  chooseNarrativeOption('ingilberga', dialog, 'm1', 'adeu')
})

options.ma__pare.onChoose(() => {
  chooseNarrativeOption('ingilberga', dialog, 'ma', 'pare')
})

options.ma__emma.onChoose(() => {
  chooseNarrativeOption('ingilberga', dialog, 'ma', 'emma')
})

options.ma__monges.onChoose(() => {
  chooseNarrativeOption('ingilberga', dialog, 'ma', 'monges')
})

options.h2__adeu2.onChoose(() => {
  chooseNarrativeOption('ingilberga', dialog, 'h2', 'adeu2')
})

options.h7__adeu7.onChoose(() => {
  chooseNarrativeOption('ingilberga', dialog, 'h7', 'adeu7')
})
