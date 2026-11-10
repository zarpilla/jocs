// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './mos.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('mos', dialog)
})

options.menu__reciclatge.onChoose(() => {
  chooseNarrativeOption('mos', dialog, 'menu', 'reciclatge')
})

options.menu__llapis.onChoose(() => {
  chooseNarrativeOption('mos', dialog, 'menu', 'llapis')
})

options.menu__llapis_demanar.onChoose(() => {
  chooseNarrativeOption('mos', dialog, 'menu', 'llapis_demanar')
})

options.menu__maquillatge.onChoose(() => {
  chooseNarrativeOption('mos', dialog, 'menu', 'maquillatge')
})

options.menu__galeria.onChoose(() => {
  chooseNarrativeOption('mos', dialog, 'menu', 'galeria')
})

options.menu__familia.onChoose(() => {
  chooseNarrativeOption('mos', dialog, 'menu', 'familia')
})

options.menu__perdo.onChoose(() => {
  chooseNarrativeOption('mos', dialog, 'menu', 'perdo')
})

options.menu__distreure.onChoose(() => {
  chooseNarrativeOption('mos', dialog, 'menu', 'distreure')
})

options.menu__adeu.onChoose(() => {
  chooseNarrativeOption('mos', dialog, 'menu', 'adeu')
})

options.convencer__elogiar.onChoose(() => {
  chooseNarrativeOption('mos', dialog, 'convencer', 'elogiar')
})

options.convencer__insultar.onChoose(() => {
  chooseNarrativeOption('mos', dialog, 'convencer', 'insultar')
})

options.convencer__res.onChoose(() => {
  chooseNarrativeOption('mos', dialog, 'convencer', 'res')
})
