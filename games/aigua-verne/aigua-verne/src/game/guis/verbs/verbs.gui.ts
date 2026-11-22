// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
// La interfície tàctil: el HUD, sense barra de verbs (la GUI es diu `verbs` perquè el pont compartit la mostra, l'amaga i
// hi busca el botó «Canvia»). Els dos modes (mòbil i tauler) i on va cada cosa: hud.ts.
import { game, onUpdate, pointer } from '@benne/script';
import { guis } from '@game';
import { gui, bossaBtn, canviaBtn, menuBtn, puntsBtn, puntsPetitBtn } from './verbs.ids';
import { isTrayOpen, layoutHud, modeTauler, refreshLine, showTray } from './hud';
import { sayHint, switchProtagonist } from '../../narrative/narrative.script';
import { botoEsPista } from '../../narrative/narrative';

bossaBtn.onClick(() => showTray(!isTrayOpen()))
puntsBtn.onClick(() => game.showClickables())
puntsPetitBtn.onClick(() => game.showClickables())
menuBtn.onClick(() => guis.gameMenu.show())
// Als jocs sense canvi de protagonista (`botoPista`), és la lupa: demana una pista. Amb `botoPista: 'mixt'`, només
// quan ara no es pot canviar.
canviaBtn.onClick(() => (botoEsPista() ? sayHint() : switchProtagonist()))

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
