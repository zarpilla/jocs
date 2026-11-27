import { saves } from '@benne/script';
import { guis } from '@game';
import { gui, backBtn, loadBtn, loadList } from './load-menu.ids';
import { narrative } from '../../narrative/narrative';

/** Five fixed slots (0–4). */
const SLOTS = 5
let selected = 0

/** La partida desada més recent (o la posició 0 si no n'hi ha cap): la que es tria en obrir el menú (tasca 251). */
function latestSlot(): number {
  let best = 0
  let when = -Infinity
  for (let i = 0; i < SLOTS; i++) {
    const t = saves.get(i)?.timestamp
    if (t !== undefined && t > when) {
      best = i
      when = t
    }
  }
  return best
}

/** Repaints the rows. `autoSelect` picks the most recent save (or 0 if none). */
function refresh(autoSelect: boolean) {
  for (let i = 0; i < SLOTS; i++) {
    loadList.setRowText(i, saves.get(i)?.name ?? `(Posició ${i + 1}: buida)`)
  }
  if (autoSelect) selected = latestSlot()
  loadList.selectedIndex = selected
  loadBtn.enabled = saves.get(selected) != null
}

// Built once per room; the saves can change in between, so re-read them whenever it opens (and pick the latest).
gui.onBuilt(() => refresh(true))
gui.onShow(() => refresh(true))

loadList.onSelect((i) => {
  selected = i
  loadBtn.enabled = saves.get(i) != null
})

loadBtn.onClick(() => {
  if (!saves.get(selected)) return
  gui.hide()
  guis.gameMenu.hide()
  saves.load(selected)
})

// «Torna»: al menú de la partida si s'hi ha vingut d'allà; a la portada (sense partida), només es tanca.
backBtn.onClick(() => {
  gui.hide()
  if (narrative.world.currentRoom() !== narrative.content.manifest.cover) guis.gameMenu.show()
})
