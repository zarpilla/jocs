// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './joanet.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('joanet', dialog)
})

options.m__barca.onChoose(() => {
  chooseNarrativeOption('joanet', dialog, 'm', 'barca')
})

options.m__comporta.onChoose(() => {
  chooseNarrativeOption('joanet', dialog, 'm', 'comporta')
})

options.m__adeu.onChoose(() => {
  chooseNarrativeOption('joanet', dialog, 'm', 'adeu')
})
