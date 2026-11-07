// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './bruc.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('bruc', dialog)
})

options.menu__reciclatge.onChoose(() => {
  chooseNarrativeOption('bruc', dialog, 'menu', 'reciclatge')
})

options.menu__llapis.onChoose(() => {
  chooseNarrativeOption('bruc', dialog, 'menu', 'llapis')
})

options.menu__llapis_demanar.onChoose(() => {
  chooseNarrativeOption('bruc', dialog, 'menu', 'llapis_demanar')
})

options.menu__maquillatge.onChoose(() => {
  chooseNarrativeOption('bruc', dialog, 'menu', 'maquillatge')
})

options.menu__familia.onChoose(() => {
  chooseNarrativeOption('bruc', dialog, 'menu', 'familia')
})

options.menu__perdo.onChoose(() => {
  chooseNarrativeOption('bruc', dialog, 'menu', 'perdo')
})

options.menu__adeu.onChoose(() => {
  chooseNarrativeOption('bruc', dialog, 'menu', 'adeu')
})

options.convencer__elogiar.onChoose(() => {
  chooseNarrativeOption('bruc', dialog, 'convencer', 'elogiar')
})

options.convencer__insultar.onChoose(() => {
  chooseNarrativeOption('bruc', dialog, 'convencer', 'insultar')
})

options.convencer__res.onChoose(() => {
  chooseNarrativeOption('bruc', dialog, 'convencer', 'res')
})
