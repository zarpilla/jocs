// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
import { dialog, options } from './espora.ids';
import { chooseNarrativeOption, startNarrativeDialog } from '../../narrative/narrative.script';

dialog.onStart(() => {
  startNarrativeDialog('espora', dialog)
})

options.menu__qui.onChoose(() => {
  chooseNarrativeOption('espora', dialog, 'menu', 'qui')
})

options.menu__miceli.onChoose(() => {
  chooseNarrativeOption('espora', dialog, 'menu', 'miceli')
})

options.menu__node.onChoose(() => {
  chooseNarrativeOption('espora', dialog, 'menu', 'node')
})

options.menu__melmelada.onChoose(() => {
  chooseNarrativeOption('espora', dialog, 'menu', 'melmelada')
})

options.menu__que.onChoose(() => {
  chooseNarrativeOption('espora', dialog, 'menu', 'que')
})

options.menu__adeu.onChoose(() => {
  chooseNarrativeOption('espora', dialog, 'menu', 'adeu')
})
