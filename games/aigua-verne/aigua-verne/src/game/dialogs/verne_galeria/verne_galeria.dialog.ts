// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './verne_galeria.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('verne_galeria', dialog)
})

options.menu__piscines.onChoose(() => {
  chooseNarrativeOption('verne_galeria', dialog, 'menu', 'piscines')
})

options.menu__aigua.onChoose(() => {
  chooseNarrativeOption('verne_galeria', dialog, 'menu', 'aigua')
})

options.menu__reserva.onChoose(() => {
  chooseNarrativeOption('verne_galeria', dialog, 'menu', 'reserva')
})

options.menu__gos.onChoose(() => {
  chooseNarrativeOption('verne_galeria', dialog, 'menu', 'gos')
})

options.menu__subhasta.onChoose(() => {
  chooseNarrativeOption('verne_galeria', dialog, 'menu', 'subhasta')
})

options.menu__adeu.onChoose(() => {
  chooseNarrativeOption('verne_galeria', dialog, 'menu', 'adeu')
})
