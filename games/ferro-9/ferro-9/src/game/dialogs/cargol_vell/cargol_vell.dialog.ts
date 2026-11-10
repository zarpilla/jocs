// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './cargol_vell.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('cargol_vell', dialog)
})

options.menu__qui.onChoose(() => {
  chooseNarrativeOption('cargol_vell', dialog, 'menu', 'qui')
})

options.menu__adeu.onChoose(() => {
  chooseNarrativeOption('cargol_vell', dialog, 'menu', 'adeu')
})
