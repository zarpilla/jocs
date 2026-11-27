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

/** El `maxLength` del camp del nom (save-menu.gui.json). */
const NAME_MAX = 34

/**
 * El nom per defecte (si no se n'escriu cap): la sala, i la data i l'hora de l'ordinador, «Pati de la granja · 27/11 18:40».
 * La data hi és perquè l'hora no es confongui amb la de la història («Nou del vespre.»).
 */
function defaultName(): string {
  const room = narrative.world.currentRoom()
  const key = room ? narrative.content.rooms[room]?.name : undefined
  const sala = key ? narrative.t(key) : ''
  const ara = new Date()
  const quan = `${ara.getDate()}/${ara.getMonth() + 1} ${ara.getHours()}:${String(ara.getMinutes()).padStart(2, '0')}`
  if (!sala) return quan
  // El camp del nom té `maxLength`: si no hi cap, es retalla la sala, mai la data.
  const lloc = NAME_MAX - ` · ${quan}`.length
  const curt = sala.length > lloc ? `${sala.slice(0, lloc - 1).trimEnd()}…` : sala
  return `${curt} · ${quan}`
}

/** Si la jugadora ha escrit un nom, triar una altra posició no l'esborra. */
let nomEscrit = false
let proposat = ''

// Saving is refused while a scene or a conversation is running (`saves.canSaveNow`). No cal escriure cap nom.
function syncSaveButton() {
  saveBtn.enabled = saves.canSaveNow
}

/**
 * Proposa el nom de la sala i el moment d'ara, també en una posició ocupada: el nom vell ja es veu a la
 * llista, i si es desés amb aquell nom no se sabria què hi ha.
 */
function showSlot(_slot: number) {
  if (!nomEscrit) saveName.text = proposat = defaultName()
  syncSaveButton()
}

/** Repaints the rows, numbered (1–5), so it is clear how many there are. `autoSelect` picks the first empty slot, or the last one when all are used. */
function refresh(autoSelect: boolean) {
  nomEscrit = false
  for (let i = 0; i < SLOTS; i++) {
    const nom = saves.get(i)?.name
    savedList.setRowText(i, nom ? `${i + 1}. ${nom}` : `${i + 1}. (buida)`)
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

saveName.onChange(() => {
  // (també salta quan el text el posa el guió: només compta si és diferent del proposat)
  nomEscrit = saveName.text !== proposat
  syncSaveButton()
})

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
