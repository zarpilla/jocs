// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './mapa.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('mapa', dialog)
})

options.inici__terra2.onChoose(() => {
  chooseNarrativeOption('mapa', dialog, 'inici', 'terra2')
})

options.inici__aqua.onChoose(() => {
  chooseNarrativeOption('mapa', dialog, 'inici', 'aqua')
})

options.inici__ferrum.onChoose(() => {
  chooseNarrativeOption('mapa', dialog, 'inici', 'ferrum')
})

options.inici__verdant.onChoose(() => {
  chooseNarrativeOption('mapa', dialog, 'inici', 'verdant')
})

options.inici__palau.onChoose(() => {
  chooseNarrativeOption('mapa', dialog, 'inici', 'palau')
})

options.inici__res.onChoose(() => {
  chooseNarrativeOption('mapa', dialog, 'inici', 'res')
})
