// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './grua.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('grua', dialog)
})

options.menu__esquerra.onChoose(() => {
  chooseNarrativeOption('grua', dialog, 'menu', 'esquerra')
})

options.menu__dreta.onChoose(() => {
  chooseNarrativeOption('grua', dialog, 'menu', 'dreta')
})

options.menu__amunt.onChoose(() => {
  chooseNarrativeOption('grua', dialog, 'menu', 'amunt')
})

options.menu__amunt_c.onChoose(() => {
  chooseNarrativeOption('grua', dialog, 'menu', 'amunt_c')
})

options.menu__avall.onChoose(() => {
  chooseNarrativeOption('grua', dialog, 'menu', 'avall')
})

options.menu__avall_c.onChoose(() => {
  chooseNarrativeOption('grua', dialog, 'menu', 'avall_c')
})

options.menu__bolca_buit.onChoose(() => {
  chooseNarrativeOption('grua', dialog, 'menu', 'bolca_buit')
})

options.menu__bolca_canal.onChoose(() => {
  chooseNarrativeOption('grua', dialog, 'menu', 'bolca_canal')
})

options.menu__bolca_brut.onChoose(() => {
  chooseNarrativeOption('grua', dialog, 'menu', 'bolca_brut')
})

options.menu__bolca.onChoose(() => {
  chooseNarrativeOption('grua', dialog, 'menu', 'bolca')
})

options.menu__adeu.onChoose(() => {
  chooseNarrativeOption('grua', dialog, 'menu', 'adeu')
})
