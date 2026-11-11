import { guis } from '@game';
import { gui, load, resume, save, settingsBtn, historial, pista } from './game-menu.ids';
import { sayHint } from '../../narrative/narrative.script';
import { showHistory } from '../../narrative/narrative';

resume.onClick(() => gui.hide())

settingsBtn.onClick(() => {
  guis.settingsMenu.show()
  gui.hide()
})

save.onClick(() => {
  guis.saveMenu.show()
  gui.hide()
})

load.onClick(() => {
  guis.loadMenu.show()
  gui.hide()
})

// Afegit per adapters/benne (benne-content.ts): l'historial de línies i demanar una pista.
historial.onClick(() => {
  gui.hide()
  showHistory()
})

pista.onClick(() => {
  gui.hide()
  sayHint()
})
