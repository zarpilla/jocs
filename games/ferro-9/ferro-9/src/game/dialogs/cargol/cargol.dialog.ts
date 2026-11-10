// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './cargol.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('cargol', dialog)
})

options.menu__clau.onChoose(() => {
  chooseNarrativeOption('cargol', dialog, 'menu', 'clau')
})

options.menu__imant.onChoose(() => {
  chooseNarrativeOption('cargol', dialog, 'menu', 'imant')
})

options.menu__diapaso.onChoose(() => {
  chooseNarrativeOption('cargol', dialog, 'menu', 'diapaso')
})

options.menu__imant2.onChoose(() => {
  chooseNarrativeOption('cargol', dialog, 'menu', 'imant2')
})

options.menu__tub.onChoose(() => {
  chooseNarrativeOption('cargol', dialog, 'menu', 'tub')
})

options.menu__carnet.onChoose(() => {
  chooseNarrativeOption('cargol', dialog, 'menu', 'carnet')
})

options.menu__carnet_lliurar.onChoose(() => {
  chooseNarrativeOption('cargol', dialog, 'menu', 'carnet_lliurar')
})

options.menu__dia.onChoose(() => {
  chooseNarrativeOption('cargol', dialog, 'menu', 'dia')
})

options.menu__memoria.onChoose(() => {
  chooseNarrativeOption('cargol', dialog, 'menu', 'memoria')
})

options.menu__alarma.onChoose(() => {
  chooseNarrativeOption('cargol', dialog, 'menu', 'alarma')
})

options.menu__adeu.onChoose(() => {
  chooseNarrativeOption('cargol', dialog, 'menu', 'adeu')
})
