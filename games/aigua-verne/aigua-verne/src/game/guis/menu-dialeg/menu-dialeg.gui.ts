// Creat per adapters/benne/tactil/index.ts (menuDialeg). No l'editis aquí.
// El botó del menú durant una conversa: es veu només amb les opcions a la vista (el motor amaga el HUD).
import { onUpdate } from '@benne/script'
import { guis } from '@game'
import { gui, menuBtn } from './menu-dialeg.ids'

menuBtn.onClick(() => {
  gui.hide()
  guis.gameMenu.show()
})

onUpdate(() => {
  const on = guis.dialog.visible && !guis.gameMenu.visible
  if (gui.visible !== on) {
    if (on) gui.show()
    else gui.hide()
  }
})
