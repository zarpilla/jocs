// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './capitana.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('capitana', dialog)
})

options.menu__aigua.onChoose(() => {
  chooseNarrativeOption('capitana', dialog, 'menu', 'aigua')
})

options.menu__portar.onChoose(() => {
  chooseNarrativeOption('capitana', dialog, 'menu', 'portar')
})

options.menu__recorda.onChoose(() => {
  chooseNarrativeOption('capitana', dialog, 'menu', 'recorda')
})

options.menu__entrego.onChoose(() => {
  chooseNarrativeOption('capitana', dialog, 'menu', 'entrego')
})

options.menu__por.onChoose(() => {
  chooseNarrativeOption('capitana', dialog, 'menu', 'por')
})

options.menu__contracte.onChoose(() => {
  chooseNarrativeOption('capitana', dialog, 'menu', 'contracte')
})

options.menu__contracte_vet.onChoose(() => {
  chooseNarrativeOption('capitana', dialog, 'menu', 'contracte_vet')
})

options.menu__pla.onChoose(() => {
  chooseNarrativeOption('capitana', dialog, 'menu', 'pla')
})

options.menu__magnat.onChoose(() => {
  chooseNarrativeOption('capitana', dialog, 'menu', 'magnat')
})

options.menu__pare.onChoose(() => {
  chooseNarrativeOption('capitana', dialog, 'menu', 'pare')
})

options.menu__gat.onChoose(() => {
  chooseNarrativeOption('capitana', dialog, 'menu', 'gat')
})

options.menu__adeu.onChoose(() => {
  chooseNarrativeOption('capitana', dialog, 'menu', 'adeu')
})
