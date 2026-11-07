import { guis } from '@game';
import { gui, load, resume, save, settingsBtn, canviar, pista } from './game-menu.ids';
import { sayHint, switchProtagonist } from '../../narrative/narrative.script';

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

// Afegit per adapters/benne (benne-content.ts): canviar de protagonista i demanar una pista.
canviar.onClick(() => {
  gui.hide()
  switchProtagonist()
})

pista.onClick(() => {
  gui.hide()
  sayHint()
})
