// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './despatx.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('despatx', dialog)
})

options.menu__gos.onChoose(() => {
  chooseNarrativeOption('despatx', dialog, 'menu', 'gos')
})

options.menu__adeu.onChoose(() => {
  chooseNarrativeOption('despatx', dialog, 'menu', 'adeu')
})

options.eines__reunio.onChoose(() => {
  chooseNarrativeOption('despatx', dialog, 'eines', 'reunio')
})

options.eines__reunio2.onChoose(() => {
  chooseNarrativeOption('despatx', dialog, 'eines', 'reunio2')
})

options.eines__gos.onChoose(() => {
  chooseNarrativeOption('despatx', dialog, 'eines', 'gos')
})

options.eines__gos_nom.onChoose(() => {
  chooseNarrativeOption('despatx', dialog, 'eines', 'gos_nom')
})

options.eines__pons.onChoose(() => {
  chooseNarrativeOption('despatx', dialog, 'eines', 'pons')
})

options.eines__ballester.onChoose(() => {
  chooseNarrativeOption('despatx', dialog, 'eines', 'ballester')
})

options.eines__adeu.onChoose(() => {
  chooseNarrativeOption('despatx', dialog, 'eines', 'adeu')
})
