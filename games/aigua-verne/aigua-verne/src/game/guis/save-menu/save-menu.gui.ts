import { saves } from '@benne/script';
import { guis } from '@game';
import { gui, backBtn, saveBtn, saveName, savedList } from './save-menu.ids';
import { narrative } from '../../narrative/narrative';

/** Five fixed slots (0–4). */
const SLOTS = 5
let selected = 0

function firstEmptySlot(): number {
  for (let i = 0; i < SLOTS; i++) {
    if (!saves.get(i)) return i
  }
  return SLOTS - 1
}

/** El nom per defecte (si no se n'escriu cap): la sala i l'hora, «Pati de la granja · 18:40». */
function defaultName(): string {
  const room = narrative.world.currentRoom()
  const key = room ? narrative.content.rooms[room]?.name : undefined
  const sala = key ? narrative.t(key) : ''
  const ara = new Date()
  const hora = `${ara.getHours()}:${String(ara.getMinutes()).padStart(2, '0')}`
  return sala ? `${sala} · ${hora}` : hora
}

// Saving is refused while a scene or a conversation is running (`saves.canSaveNow`). No cal escriure cap nom.
function syncSaveButton() {
  saveBtn.enabled = saves.canSaveNow
}

/** Shows the slot's save name, ready to overwrite (buida, el nom per defecte). */
function showSlot(slot: number) {
  saveName.text = saves.get(slot)?.name ?? defaultName()
  syncSaveButton()
}

/** Repaints the rows. `autoSelect` picks the first empty slot, or the last one when all are used. */
function refresh(autoSelect: boolean) {
  for (let i = 0; i < SLOTS; i++) {
    savedList.setRowText(i, saves.get(i)?.name ?? `(Posició ${i + 1}: buida)`)
  }
  if (autoSelect) selected = firstEmptySlot()
  savedList.selectedIndex = selected
  showSlot(selected)
}

gui.onBuilt(() => refresh(true))
gui.onShow(() => refresh(false))

savedList.onSelect((i) => {
  selected = i
  showSlot(i)
})

saveName.onChange(() => syncSaveButton())

/** Després de desar: el títol del menú diu «Desat.» una estona. */
function confirmSaved() {
  const title = (guis.gameMenu.controls as unknown as Record<string, { text: string } | undefined>).title
  if (!title) return
  const abans = narrative.t('ui.menu.titol')
  title.text = narrative.t('ui.desar.fet')
  setTimeout(() => { if (title.text === narrative.t('ui.desar.fet')) title.text = abans }, 2000)
}

saveBtn.onClick(() => {
  const name = saveName.text.trim() || defaultName()
  saves.save(selected, name)
  gui.hide()
  guis.gameMenu.show()
  confirmSaved()
})

backBtn.onClick(() => {
  gui.hide()
  guis.gameMenu.show()
})
