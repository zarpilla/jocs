// Creat per adapters/benne/tactil/index.ts (dialegTauler). No l'editis aquí.
// El fons del panell d'una conversa, al tauler: mentre algú parla, el motor amaga les opcions i el HUD, i la franja de
// sota l'escena quedaria negra. Es veu quan el HUD no hi és en una sala jugable (una conversa); a sobre, el panell.
import { onUpdate } from '@benne/script'
import { guis } from '@game'
import { gui } from './fons-dialeg.ids'
import { modeTauler } from '../verbs/hud'
import { narrative } from '../../narrative/narrative'

onUpdate(() => {
  const sala = narrative.world.currentRoom()
  const jugable = !!sala && sala !== narrative.content.manifest.cover && !narrative.content.rooms[sala]?.cutscene
  const on = jugable && modeTauler() && !guis.verbs.visible
  if (gui.visible !== on) {
    if (on) gui.show()
    else gui.hide()
  }
})
