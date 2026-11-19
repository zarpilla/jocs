// Creat per adapters/benne (benne-content.ts): els botons de la portada.
import { game, saves } from '@benne/script';
import { guis } from '@game';
import { gui, continua, comenca, carrega, version } from './portada.ids';
import { AUTOSAVE } from '../../narrative/narrative';
import { startFromCover } from '../../narrative/narrative.script';

// «Continua» carrega la partida que es desa sola a cada sala; només surt si n'hi ha una.
function syncContinua() {
  continua.visible = saves.get(AUTOSAVE) != null
}

continua.onClick(() => saves.load(AUTOSAVE))
comenca.onClick(() => startFromCover())
carrega.onClick(() => guis.loadMenu.show())

gui.onBuilt(() => {
  version.text = `v${game.version}`
  syncContinua()
})
gui.onShow(() => syncContinua())
