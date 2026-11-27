import { game } from '@benne/script';
import { guis } from '@game';
import { gui, load, resume, save, settingsBtn, canviar, pista, historial, quit } from './game-menu.ids';
import { sayHint, switchProtagonist, quitAfterSaving } from '../../narrative/narrative.script';

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

// Afegit per adapters/benne (benne-content.ts): l'historial de línies.
historial.onClick(() => {
  gui.hide()
  guis.historial.show()
})

// «Surt»: a l'escriptori tanca l'aplicació; al navegador torna a l'arrel del web (els jocs viuen a malaherbasoft.cat/<joc>/).
quit.onClick(() => {
  // Abans de marxar, desa on és la partida: «Continua» hi torna (tasca 108). Amb el menú tancat, el joc no és aturat.
  gui.hide()
  quitAfterSaving(() => {
    if (game.isDesktop) game.quit()
    else window.location.href = '/'
  })
})
