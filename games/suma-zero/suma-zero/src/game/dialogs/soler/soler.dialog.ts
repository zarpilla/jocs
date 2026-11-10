// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './soler.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('soler', dialog)
})

options.menu__fill.onChoose(() => {
  chooseNarrativeOption('soler', dialog, 'menu', 'fill')
})

options.menu__adeu.onChoose(() => {
  chooseNarrativeOption('soler', dialog, 'menu', 'adeu')
})

options.nom__nom_curt.onChoose(() => {
  chooseNarrativeOption('soler', dialog, 'nom', 'nom_curt')
})

options.nom__nom_llarg.onChoose(() => {
  chooseNarrativeOption('soler', dialog, 'nom', 'nom_llarg')
})

options.edat__edat_curt.onChoose(() => {
  chooseNarrativeOption('soler', dialog, 'edat', 'edat_curt')
})

options.edat__edat_llarg.onChoose(() => {
  chooseNarrativeOption('soler', dialog, 'edat', 'edat_llarg')
})

options.roba__roba_curt.onChoose(() => {
  chooseNarrativeOption('soler', dialog, 'roba', 'roba_curt')
})

options.roba__roba_llarg.onChoose(() => {
  chooseNarrativeOption('soler', dialog, 'roba', 'roba_llarg')
})

options.xiulet__plorar.onChoose(() => {
  chooseNarrativeOption('soler', dialog, 'xiulet', 'plorar')
})

options.xiulet__res.onChoose(() => {
  chooseNarrativeOption('soler', dialog, 'xiulet', 'res')
})
