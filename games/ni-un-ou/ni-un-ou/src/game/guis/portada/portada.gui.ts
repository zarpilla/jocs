// Creat per adapters/benne (benne-content.ts): els botons de la portada.
// Interfície tàctil: abans de jugar, la targeta «Com es juga» (adapters/benne/tactil, controls.script.ts).
import { game, saves } from '@benne/script';
import { gui, continua, comenca, carrega, version } from './portada.ids';
import { AUTOSAVE } from '../../narrative/narrative';
import { abansDeJugar } from '../../narrative/controls.script';

// «Continua» carrega la partida que es desa sola a cada sala; només surt si n'hi ha una.
function syncContinua() {
  continua.visible = saves.get(AUTOSAVE) != null
}

continua.onClick(() => abansDeJugar('continua'))
comenca.onClick(() => abansDeJugar('comenca'))
carrega.onClick(() => abansDeJugar('carrega'))

gui.onBuilt(() => {
  version.text = `v${game.version}`
  syncContinua()
})
gui.onShow(() => syncContinua())
