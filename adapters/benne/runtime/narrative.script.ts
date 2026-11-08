/**
 * Pont amb Benne, part seqüenciada (BenneScript): parlar, conduir diàlegs,
 * fer les interaccions del JSON, canviar de protagonista, pistes i finals.
 * Les funcions exportades d'un `*.script.ts` són "step functions": cada línia
 * espera l'anterior, com als scripts de sala.
 *
 * Es copia a `src/game/narrative/` amb `npm run benne:sync`. No l'editis allà.
 */
import { display, fadeOut, player } from '@benne/script';
import type { DialogHandle, FallbackTarget } from '@benne/script';
import type { InteractionResult, ResolvedChoice, ResolvedLine } from '@aventura/narrative-core';
import {
  applyAppearances, applyHotspotVisibility, benneCharacter, benneDialog, benneRoom, ensureStarted, fromBenne, narrative, optionName, protagonistRoom,
  rememberProtagonistRoom, roomProtagonist, takePendingSwitch, targetFromBenne,
} from './narrative';

/** Diu les línies una darrere l'altra. */
export function playLines(lines: ResolvedLine[]) {
  for (const line of lines) {
    if (line.who === 'narrator') {
      display(line.text)
    } else if (line.who === 'player') {
      player.say(line.text)
    } else {
      const speaker = benneCharacter(line.who)
      if (speaker) speaker.say(line.text)
      else display(line.text)
    }
  }
}

/** Fa el que diu el resultat d'una interacció: línies, diàleg, canvi de protagonista o de sala. */
export function playResult(result: InteractionResult) {
  playLines(result.lines)
  if (result.dialogue) {
    const dialog = benneDialog(result.dialogue)
    if (dialog) dialog.start()
  }
  const who = takePendingSwitch()
  if (who) {
    goToProtagonist(who)
    return
  }
  if (result.goTo) {
    const room = benneRoom(result.goTo)
    if (room) room.goTo()
  }
}

/**
 * Totes les interaccions que cap script de Benne no gestiona arriben aquí
 * (des de `globalScript.ts`) i les resol el JSON del joc.
 */
export function routeInteraction(verb: string, target: FallbackTarget, item?: string) {
  const request = { verb, target: targetFromBenne(target.kind, target.id), item: item ? fromBenne('items', item) : undefined }
  const result = narrative.interact(request)
  if (result) playResult(result)
  else playLines([narrative.defaultLine(verb)])
}

/**
 * En entrar a una sala, abans del fos (des de `game.onEnterAnyRoom`): prepara la partida si és
 * nova, pren el control de la protagonista de la sala i mostra o amaga les coses condicionals.
 */
export function onRoomEntered() {
  ensureStarted()
  const room = narrative.world.currentRoom()
  if (!room) return
  const who = roomProtagonist(room)
  if (who) {
    if (narrative.world.activeProtagonist() !== who) {
      const character = benneCharacter(who)
      if (character) player.switchTo(character)
    }
    rememberProtagonistRoom(who, room)
  }
  applyHotspotVisibility()
  applyAppearances()
}

/** Va a la sala on és una protagonista (i, en entrar-hi, se'n pren el control). */
export function goToProtagonist(who: string) {
  const roomId = protagonistRoom(who)
  const room = roomId ? benneRoom(roomId) : undefined
  if (room) room.goTo()
}

/** En entrar a una sala (després del fos): l'`onEnter` del JSON. */
export function enterNarrativeRoom() {
  const room = narrative.world.currentRoom()
  if (!room) return
  narrative.worldChanged()
  const result = narrative.enterRoom(room)
  if (result) playResult(result)
}

function refreshOptions(dialog: DialogHandle, choices: ResolvedChoice[]) {
  const available = new Set(choices.map((c) => optionName(c.node, c.id)));
  for (const [name, option] of Object.entries(dialog.options)) {
    if (available.has(name)) option.on();
    else option.off();
  }
}

/** Des de `dialog.onStart` (generat). */
export function startNarrativeDialog(id: string, dialog: DialogHandle) {
  const step = narrative.startDialogue(id)
  refreshOptions(dialog, step.choices)
  playLines(step.lines)
  if (step.ended) dialog.end()
}

/** Des de cada `options.x.onChoose` (generat). */
export function chooseNarrativeOption(id: string, dialog: DialogHandle, node: string, choice: string) {
  const step = narrative.choose(id, choice, { node })
  refreshOptions(dialog, step.choices)
  playLines(step.lines)
  if (step.ended) dialog.end()
}

/** Botó o verb de "pista": cada vegada una mica més explícita. */
export function sayHint() {
  const hint = narrative.requestHint()
  const text = hint ? hint.text : narrative.t('ui.pista.cap')
  player.say(text)
}

/** Canvia a l'altra protagonista (per a un botó de la GUI): va a la sala on és. */
export function switchProtagonist() {
  const all = narrative.content.manifest.protagonists
  const next = all[(all.indexOf(narrative.world.activeProtagonist()) + 1) % all.length]!
  goToProtagonist(next)
}

/** Mostra el final que toca (o el que li diguis). */
export function playEnding(id?: string) {
  const endingId = id ?? narrative.resolveEnding()
  if (!endingId) return
  const ending = narrative.ending(endingId)
  fadeOut(1.5)
  display(ending.title)
  display(ending.text)
  display(narrative.t('ui.fi'))
}
