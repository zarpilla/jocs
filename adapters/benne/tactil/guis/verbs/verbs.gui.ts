// La interfície tàctil: el HUD, sense barra de verbs (la GUI es diu `verbs` perquè el pont compartit la mostra, l'amaga i
// hi busca el botó «Canvia»). Els dos modes (mòbil i tauler) i on va cada cosa: hud.ts.
import { game, onUpdate, pointer } from '@benne/script';
import { guis } from '@game';
import { gui, bossaBtn, canviaBtn, menuBtn, puntsBtn } from './verbs.ids';
import { isTrayOpen, layoutHud, modeTauler, refreshLine, showTray } from './hud';
import { switchProtagonist } from '../../narrative/narrative.script';

bossaBtn.onClick(() => showTray(!isTrayOpen()))
puntsBtn.onClick(() => game.showClickables())
menuBtn.onClick(() => guis.gameMenu.show())
canviaBtn.onClick(() => switchProtagonist())

gui.onBuilt(() => {
  layoutHud()
  refreshLine()
})
pointer.onContextChange(() => {
  refreshLine()
  // Al mòbil, la safata tapa l'escena: quan prens un objecte a la mà, es plega sola.
  if (pointer.item && isTrayOpen() && !modeTauler()) showTray(false)
})

onUpdate(() => layoutHud())
