// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './trucada.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('trucada', dialog)
})

options.menu__pany.onChoose(() => {
  chooseNarrativeOption('trucada', dialog, 'menu', 'pany')
})

options.menu__contrasenya.onChoose(() => {
  chooseNarrativeOption('trucada', dialog, 'menu', 'contrasenya')
})

options.menu__trucada.onChoose(() => {
  chooseNarrativeOption('trucada', dialog, 'menu', 'trucada')
})

options.menu__resum.onChoose(() => {
  chooseNarrativeOption('trucada', dialog, 'menu', 'resum')
})

options.menu__robot.onChoose(() => {
  chooseNarrativeOption('trucada', dialog, 'menu', 'robot')
})

options.menu__adeu.onChoose(() => {
  chooseNarrativeOption('trucada', dialog, 'menu', 'adeu')
})
