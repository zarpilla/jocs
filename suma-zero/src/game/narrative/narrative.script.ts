// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
/**
 * Pont amb Benne, part seqüenciada (BenneScript): parlar, conduir diàlegs,
 * fer les interaccions del JSON, canviar de protagonista, pistes i finals.
 * Les funcions exportades d'un `*.script.ts` són "step functions": cada línia
 * espera l'anterior, com als scripts de sala.
 *
 * Es copia a `src/game/narrative/` amb `npm run benne:sync`. No l'editis allà.
 */
import { MusicHandle, SfxHandle, display, fadeIn, fadeOut, player, stayBlackOnEnter, wait } from '@benne/script';
import type { DialogHandle, FallbackTarget } from '@benne/script';
import { guis, music } from '@game';
import type { InteractionResult, ResolvedChoice, ResolvedLine } from '@aventura/narrative-core';
import {
  adoptLoadedState, applyAppearances, facingToward, applySwitchButton, applyHotspotVisibility, benneCharacter, benneDialog, benneRoom, ensureStarted, fromBenne, narrative, optionName, protagonistRoom,
  protagonistMusic, recordLine, rememberProtagonistRoom, roomProtagonist, takePendingEnding, takePendingSwitch, targetFromBenne,
} from './narrative';

/** Diu les línies una darrere l'altra (i fa sonar el so de cada una en començar-la). */
export function playLines(lines: ResolvedLine[]) {
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]!
    recordLine(line.who, line.text)
    if (line.sound) new SfxHandle(line.sound).play()
    if (line.who === 'title') {
      // Pantalla de títol: les línies `title` seguides es mostren juntes sobre negre.
      const first = i === 0 || lines[i - 1]!.who !== 'title'
      const last = i === lines.length - 1 || lines[i + 1]!.who !== 'title'
      if (first) fadeOut(1)
      display(line.text)
      if (last) fadeIn(1)
    } else if (line.who === 'narrator') {
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
  if (takePendingEnding()) {
    takePendingSwitch()
    playEnding()
    return
  }
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
  // Primer hi va caminant (al `walkToPoint` de la cosa o del personatge) i s'hi gira, com a les
  // aventures clàssiques. Ha de ser el primer pas: així, si el jugador clica una altra cosa pel camí,
  // el motor atura aquesta acció i fa la nova. (`walkToClicked` no serveix: als fallbacks no hi ha clic.)
  if (target.kind !== 'item') {
    player.walkTo(target.id)
    const facing = facingToward(target.kind, target.id)
    if (facing) player.face(facing)
  }
  adoptLoadedState()
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
  adoptLoadedState()
  ensureStarted()
  const room = narrative.world.currentRoom()
  if (!room) return
  // A la portada i a les cinemàtiques (el pròleg) no hi ha res per clicar: fora la barra de verbs.
  const portada = room === narrative.content.manifest.cover
  if (portada || narrative.content.rooms[room]?.cutscene) guis.verbs.hide()
  else guis.verbs.show()
  if (portada) guis.portada.show()
  else guis.portada.hide()
  applySwitchButton()
  const who = roomProtagonist(room)
  applyAmbientMusic(portada, who)
  if (who) {
    if (narrative.world.activeProtagonist() !== who) {
      const character = benneCharacter(who)
      if (character) player.switchTo(character)
    }
    rememberProtagonistRoom(who, room)
  }
  applyHotspotVisibility()
  applyAppearances()
  // L'onEnter es resol ara, abans del fos, i es reprodueix després (`enterNarrativeRoom`). Si comença
  // amb un títol, la pantalla es posa a negre ja: si no, es veuria la sala, s'enfosquiria i tornaria.
  narrative.worldChanged()
  const result = narrative.enterRoom(room)
  entrada = { room, result }
  if (result?.lines[0]?.who === 'title') stayBlackOnEnter()
}

/**
 * Música d'ambient: cada protagonista té la del seu espai i, en canviar d'una a l'altra, s'encadenen.
 * A la portada no en sona cap; a les cinemàtiques (pròleg, finals) continua la que sonava.
 */
function applyAmbientMusic(portada: boolean, who: string | null) {
  if (portada) {
    if (music.isPlaying) music.stop()
    return
  }
  const track = who ? protagonistMusic(who) : null
  if (!track) return
  const handle = new MusicHandle(track)
  if (!handle.isPlaying) handle.play({ fadeSeconds: 2.5 })
}

/** L'onEnter de la sala on acabem d'entrar, resolt abans del fos (vegeu `onRoomEntered`). */
let entrada: { room: string; result: InteractionResult | null } | null = null

/** El botó «Comença» de la portada: el pròleg, si n'hi ha, o la sala de la primera protagonista. */
export function startFromCover() {
  // Per provar els finals (només en desenvolupament): `?final=fugida` a l'adreça.
  const provar = import.meta.env.DEV ? new URLSearchParams(location.search).get('final') : null
  if (provar && narrative.content.endings[provar]) {
    playEnding(provar)
    return
  }
  const manifest = narrative.content.manifest
  const first = manifest.protagonists[0]!
  const desti = manifest.intro ?? manifest.start?.[first]?.room
  const sala = desti ? benneRoom(desti) : undefined
  if (sala) sala.goTo()
}

/** Va a la sala on és una protagonista (i, en entrar-hi, se'n pren el control). */
export function goToProtagonist(who: string) {
  const roomId = protagonistRoom(who)
  const room = roomId ? benneRoom(roomId) : undefined
  if (room) room.goTo()
}

/** En entrar a una sala (després del fos): l'`onEnter` del JSON. */
export function enterNarrativeRoom() {
  adoptLoadedState()
  const room = narrative.world.currentRoom()
  if (!room) return
  let result: InteractionResult | null
  if (entrada?.room === room) {
    result = entrada.result
  } else {
    narrative.worldChanged()
    result = narrative.enterRoom(room)
  }
  entrada = null
  if (finale[0]?.room === room) {
    playFinaleRoom()
    return
  }
  if (!result) return
  const cutscene = narrative.content.rooms[room]?.cutscene
  if (!cutscene) {
    playResult(result)
    return
  }
  // Cinemàtica: Benne ja embolica aquest moment en una cutscene, i amb Esc la resta s'acaba de cop.
  // Si l'han saltada, anem directament al final (`skipTo`) en lloc de passar per les altres pantalles.
  let saltada = false
  for (const line of result.lines) {
    playLines([line])
    // Mentre se salta una cinemàtica, `wait` acaba a l'instant: així sabem si han premut Esc.
    const inici = Date.now()
    wait(0.1)
    if (Date.now() - inici < 50) {
      saltada = true
      break
    }
  }
  const desti = saltada && cutscene.skipTo ? cutscene.skipTo : result.goTo
  const sala = desti ? benneRoom(desti) : undefined
  if (sala) sala.goTo()
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
  adoptLoadedState()
  const step = narrative.startDialogue(id)
  refreshOptions(dialog, step.choices)
  playLines(step.lines)
  if (step.ended) dialog.end()
}

/** Des de cada `options.x.onChoose` (generat). */
export function chooseNarrativeOption(id: string, dialog: DialogHandle, node: string, choice: string) {
  adoptLoadedState()
  const step = narrative.choose(id, choice, { node })
  refreshOptions(dialog, step.choices)
  playLines(step.lines)
  if (step.ended) dialog.end()
}

/** Botó o verb de "pista": cada vegada una mica més explícita. */
export function sayHint() {
  const hint = narrative.requestHint()
  const text = hint ? hint.text : narrative.t('ui.pista.cap')
  recordLine('player', text)
  player.say(text)
}

/** Canvia a l'altra protagonista (per a un botó de la GUI): va a la sala on és. */
export function switchProtagonist() {
  if (!narrative.canSwitch()) return
  const all = narrative.content.manifest.protagonists
  const next = all[(all.indexOf(narrative.world.activeProtagonist()) + 1) % all.length]!
  goToProtagonist(next)
}

/** Una línia d'un final: els personatges ja no hi són, i el que diuen surt amb el nom al davant. */
function displayEndingLine(line: { who: string; text: string }) {
  if (line.who === 'narrator' || line.who === 'title' || line.who === 'player') display(line.text)
  else display(`${narrative.characterName(line.who)}: ${line.text}`)
}

/**
 * Un final amb imatges (`room` a les línies de l'escena): les línies que van damunt de cada sala.
 * Es reprodueixen en entrar-hi (`enterNarrativeRoom`), com el pròleg, i després es passa a la següent.
 */
let finale: { room: string; lines: { who: string; text: string }[] }[] = []

/** Mostra el final que toca (o el que li diguis). */
export function playEnding(id?: string) {
  const endingId = id ?? narrative.resolveEnding()
  if (!endingId) return
  const ending = narrative.ending(endingId)
  // Trossos de l'escena: el que va sobre negre (abans de la primera sala) i el que va damunt de cada sala.
  const negre: { who: string; text: string }[] = []
  const trossos: typeof finale = []
  for (const line of ending.scene) {
    const actual = trossos[trossos.length - 1]
    if (line.room && line.room !== actual?.room) trossos.push({ room: line.room, lines: [line] })
    else (actual ? actual.lines : negre).push(line)
  }
  const tancament = { who: 'narrator', text: ending.text }
  const ultim = trossos[trossos.length - 1]
  if (ending.textRoom && ending.textRoom !== ultim?.room) trossos.push({ room: ending.textRoom, lines: [tancament] })
  else (ultim ? ultim.lines : negre).push(tancament)

  fadeOut(1.5)
  display(ending.title)
  for (const line of negre) displayEndingLine(line)
  const primer = trossos[0]
  const sala = primer ? benneRoom(primer.room) : undefined
  if (!sala) {
    display(narrative.t('ui.fi'))
    return
  }
  finale = trossos
  sala.goTo()
}

/** En entrar a una sala d'un final: les seves línies, i després la sala següent o el «Fi». */
function playFinaleRoom() {
  const tros = finale.shift()!
  let saltat = false
  for (const line of tros.lines) {
    displayEndingLine(line)
    // Amb Esc, `wait` acaba a l'instant: llavors anem directament al «Fi».
    const inici = Date.now()
    wait(0.1)
    if (Date.now() - inici < 50) {
      saltat = true
      break
    }
  }
  const seguent = saltat ? undefined : finale[0]
  const sala = seguent ? benneRoom(seguent.room) : undefined
  if (sala) {
    sala.goTo()
    return
  }
  finale = []
  fadeOut(1.5)
  display(narrative.t('ui.fi'))
}
