// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './juana.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('juana', dialog)
})

options.menu__llavors.onChoose(() => {
  chooseNarrativeOption('juana', dialog, 'menu', 'llavors')
})

options.menu__peixos.onChoose(() => {
  chooseNarrativeOption('juana', dialog, 'menu', 'peixos')
})

options.menu__mar.onChoose(() => {
  chooseNarrativeOption('juana', dialog, 'menu', 'mar')
})

options.menu__on.onChoose(() => {
  chooseNarrativeOption('juana', dialog, 'menu', 'on')
})

options.menu__tornar.onChoose(() => {
  chooseNarrativeOption('juana', dialog, 'menu', 'tornar')
})

options.menu__bru.onChoose(() => {
  chooseNarrativeOption('juana', dialog, 'menu', 'bru')
})

options.menu__preguntes.onChoose(() => {
  chooseNarrativeOption('juana', dialog, 'menu', 'preguntes')
})

options.menu__recorda.onChoose(() => {
  chooseNarrativeOption('juana', dialog, 'menu', 'recorda')
})

options.menu__adeu.onChoose(() => {
  chooseNarrativeOption('juana', dialog, 'menu', 'adeu')
})

options.q1__vendre.onChoose(() => {
  chooseNarrativeOption('juana', dialog, 'q1', 'vendre')
})

options.q1__regalar.onChoose(() => {
  chooseNarrativeOption('juana', dialog, 'q1', 'regalar')
})

options.q1__beure.onChoose(() => {
  chooseNarrativeOption('juana', dialog, 'q1', 'beure')
})

options.q2__agafar.onChoose(() => {
  chooseNarrativeOption('juana', dialog, 'q2', 'agafar')
})

options.q2__res.onChoose(() => {
  chooseNarrativeOption('juana', dialog, 'q2', 'res')
})

options.q3__pou.onChoose(() => {
  chooseNarrativeOption('juana', dialog, 'q3', 'pou')
})

options.q3__mon.onChoose(() => {
  chooseNarrativeOption('juana', dialog, 'q3', 'mon')
})
