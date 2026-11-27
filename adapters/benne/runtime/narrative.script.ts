/**
 * Pont amb Benne, part seqüenciada (BenneScript): parlar, conduir diàlegs,
 * fer les interaccions del JSON, canviar de protagonista, pistes i finals.
 * Les funcions exportades d'un `*.script.ts` són "step functions": cada línia
 * espera l'anterior, com als scripts de sala.
 *
 * Es copia a `src/game/narrative/` amb `npm run benne:sync`. No l'editis allà.
 */
import { MusicHandle, SfxHandle, ambient, background, cutscene, display, fadeIn, fadeOut, game, player, pointer, saves, stayBlackOnEnter, wait } from '@benne/script';
import type { DialogHandle, FallbackTarget } from '@benne/script';
import { guis, music } from '@game';
import type { Effect, InteractionResult, ResolvedChoice, ResolvedLine, StageCue } from '@aventura/narrative-core';
import {
  AMPLADA, AUTOSAVE, applyStageNow, primeStage, toBenne, roomProp, stageActor, stagePoint, adoptLoadedState, prepareSituation, type Situacio, applyAppearances, prepareEndingPreview, applyPlaces, facingToward, npcFacingPlayer, applySwitchButton, applyHotspotVisibility, resetStageAnims, showSpeaker, showDueCharacters, benneCharacter, benneDialog, benneRoom, ensureStarted, fromBenne, narrative, optionName, protagonistRoom, doorPoint,
  musicSync, touchRouter, roomMusic, recordLine, setDoorSound, takeDoorSound, rememberProtagonistRoom, roomProtagonist, isSharedRoom, isClickableCutscene, setClickablePrompt, setEnteringProtagonist, takeEnteringProtagonist, takePendingEnding, takePendingSwitch, takePendingGoTo, leavesRoom, targetFromBenne, voiced, preloadLineVoices,
} from './narrative';
import { statsEnding, statsLoadedGame, statsNewGame } from './estadistiques';

/**
 * Què hi ha just abans i just després d'aquestes línies, quan es diuen a trossos (les cinemàtiques en diuen
 * una cada vegada): `before`/`after` són el `who` de la línia del costat; `after: 'negre'` vol dir que tot
 * seguit es canvia de sala o ve un final, i la pantalla s'ha de quedar a negre.
 */
type Around = {
  before?: string; after?: string
  /**
   * Encara vénen més línies de la mateixa cinemàtica (a trossos): l'estat de la sala (qui es veu, on és) no s'aplica
   * fins a l'última. Si no, qui ha sortit amb `stage` i no és a `hotspots` de la sala s'amagaria entre línia i línia.
   */
  more?: boolean
}

/**
 * Diu les línies una darrere l'altra (i fa sonar el so de cada una en començar-la). Si n'hi ha amb moviment
 * (`stage`, `stageAfter`), és una petita cinemàtica: els clics al món no la tallen, i la tecla de saltar l'acaba de cop.
 */
export function playLines(lines: ResolvedLine[], around: Around = {}) {
  preloadLineVoices(lines)
  if (lines.some((l) => l.stage || l.stageAfter)) {
    cutscene(() => {
      sayLines(lines, around)
      // I en acabar, cadascú torna a l'animació que diu l'estat (p. ex. en Bastida, assegut).
      applyAppearances()
    })
  } else sayLines(lines, around)
}

/** Les indicacions d'escena d'una línia, per ordre: el que és de cop, caminar (esperant-hi o no) i esperar (`hold`). */
function playStage(cues: StageCue[]) {
  for (const cue of cues) {
    applyStageNow(cue)
    if (cue.hold) wait(cue.hold)
    if (cue.walk === undefined || cue.who === undefined) continue
    const to = stagePoint(cue.walk)
    const actor = stageActor(cue.who) as unknown as { walkTo: ((p: { x: number; y: number }) => void) & { now(p: { x: number; y: number }): unknown } } | undefined
    if (!to || !actor) continue
    if (cue.wait === false) actor.walkTo.now(to)
    else actor.walkTo(to)
  }
}

function sayLines(lines: ResolvedLine[], around: Around) {
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]!
    if (line.stage) playStage(line.stage)
    recordLine(line.who, line.text)
    if (line.sound) new SfxHandle(line.sound).play()
    if (line.who === 'title') {
      // Pantalla de títol: les línies `title` seguides es mostren juntes sobre negre. Si després es canvia
      // de sala (o ve un final), no es torna a la sala d'ara: la següent ja entrarà des del negre.
      const before = i === 0 ? around.before : lines[i - 1]!.who
      const after = i === lines.length - 1 ? around.after : lines[i + 1]!.who
      if (before !== 'title') fadeOut(1)
      display(line.text)
      if (after !== 'title' && after !== 'negre') {
        showDueCharacters()
        fadeIn(1)
      }
    } else if (line.who === 'narrator') {
      // El narrador també pot tenir veu: `narrator<número>` (el motor la fa sonar des de `display`).
      const text = voiced('narrator', line.key, line.text)
      if (isClickableCutscene(narrative.world.currentRoom())) narrate(text)
      else display(text)
    } else if (line.who === 'player') {
      player.say(voiced(player.id, line.key, line.text))
    } else {
      const speaker = benneCharacter(line.who)
      if (speaker) {
        showSpeaker(line.who)
        speaker.say(voiced(speaker.id, line.key, line.text))
      } else display(line.text)
    }
    if (line.stageAfter) playStage(line.stageAfter)
  }
  // Qui s'ha de moure (`place`) hi camina ara, quan ja s'ha dit tot: els efectes s'apliquen abans de les
  // línies, i si caminés abans, marxaria mentre parla. El mateix amb qui desapareix i amb qui apareix.
  // Si tot seguit es marxa de la sala (`after: 'negre'`), no: la sala nova aplicarà el seu estat en entrar, i aquí
  // tornaria a sortir qui una indicació d'escena ha amagat (l'Iri, que ja és a la cistella, just abans del fos).
  if (around.more || around.after === 'negre') return
  applyHotspotVisibility()
  applyPlaces(true)
}

/**
 * A una cinemàtica amb coses per tocar (el viatge de la carta de navegació), la narració passa sola, quan s'ha pogut
 * llegir: el que s'ha triat ja s'ha triat, i no s'ha de clicar per veure com hi arriba. Un clic l'avança igualment.
 */
function narrate(text: string) {
  const shown = display.now(text)
  const fins = Date.now() + Math.max(1.8, 1 + text.length * 0.06) * 1000
  while (!shown.done && Date.now() < fins) wait(0.1)
  shown.finishNow()
}

/** Fa el que diu el resultat d'una interacció: línies, diàleg, canvi de protagonista o de sala. */
export function playResult(result: InteractionResult) {
  playLines(result.lines, { after: !result.dialogue && leavesRoom(result.goTo) ? 'negre' : undefined })
  if (result.dialogue && senseOpcions(result.dialogue)) {
    // Un «diàleg» que només diu línies (el quadern): es diu com una interacció, sense obrir la caixa del diàleg
    // (taparia el HUD, i en tornar el refaria amb el botó «Canvia» a la vista).
    playerActed()
    const step = primeStage(narrative.startDialogue(result.dialogue))
    playLines(step.lines, { after: step.ended && leavesRoom() ? 'negre' : undefined })
    if (step.ended) {
      followUp(result.goTo)
      return
    }
    // (si no s'ha acabat, que no hauria de passar sense opcions, continua com un diàleg)
  }
  if (result.dialogue) {
    // El que demanen els efectes (canvi de protagonista, de sala, final) es fa en acabar el diàleg.
    const dialog = benneDialog(result.dialogue)
    if (dialog) {
      dialog.start()
      return
    }
  }
  followUp(result.goTo)
}

/** Si cap node d'un diàleg té opcions: només diu línies. */
function senseOpcions(id: string): boolean {
  const def = narrative.content.dialogues[id]
  return !!def && Object.values(def.nodes).every((n) => !n.choices?.length)
}

/** Després d'una interacció o d'un diàleg: el final, el canvi de protagonista o la sala nova que s'hagin demanat. */
function followUp(goTo?: string) {
  if (takePendingEnding()) {
    takePendingSwitch()
    takePendingGoTo()
    playEnding()
    return
  }
  autosaveHere()
  const who = takePendingSwitch()
  const anar = takePendingGoTo() ?? goTo
  if (who) {
    goToProtagonist(who)
    return
  }
  if (anar && anar === narrative.world.currentRoom()) {
    reenterRoom(anar)
    return
  }
  if (anar) {
    const room = benneRoom(anar)
    if (room) room.goTo()
  }
}

/**
 * `anar` a la sala on ja s'és (p. ex. l'Escena 3 de Ni un ou, que comença a la infermeria, si la darrera revisió s'hi
 * acaba): Benne no hi torna a entrar (`goTo` a la mateixa sala no fa res), i el títol que hi havia just abans s'ha
 * quedat a negre esperant la sala nova. Es fa l'entrada a mà: la sala al dia sota el negre, el fos i l'`onEnter`.
 */
function reenterRoom(room: string) {
  resetStageAnims(room)
  applyHotspotVisibility()
  applyAppearances()
  applyPlaces(false)
  narrative.worldChanged()
  const result = primeStage(narrative.enterRoom(room))
  // Si l'onEnter comença amb un títol, es queda a negre: el títol ja farà el seu fos.
  if (result?.lines[0]?.who !== 'title') {
    for (const cue of result?.lines[0]?.stage ?? []) applyStageNow(cue)
    showDueCharacters()
    fadeIn(1)
  }
  if (!untouchedNewGame) saves.autosave(AUTOSAVE)
  if (result) playResult(result)
}

/**
 * Totes les interaccions que cap script de Benne no gestiona arriben aquí
 * (des de `globalScript.ts`) i les resol el JSON del joc.
 */
export function routeInteraction(verb: string, target: FallbackTarget, item?: string) {
  const router = touchRouter()
  if (router?.takes(verb, target, item)) {
    router.route(verb, target, item)
    return
  }
  performInteraction(verb, target, item)
}

/** Fa la interacció del JSON: hi va caminant, s'hi gira, i el nucli la resol. */
export function performInteraction(verb: string, target: FallbackTarget, item?: string) {
  // Primer hi va caminant (al `walkToPoint` de la cosa o del personatge) i s'hi gira, com a les
  // aventures clàssiques. Ha de ser el primer pas: així, si el jugador clica una altra cosa pel camí,
  // el motor atura aquesta acció i fa la nova. (`walkToClicked` no serveix: als fallbacks no hi ha clic.)
  // A una cinemàtica amb coses per tocar (la carta de navegació) no hi ha ningú que hi vagi.
  if (target.kind !== 'item' && !isClickableCutscene(narrative.world.currentRoom())) {
    player.walkTo(target.id)
    const facing = facingToward(target.kind, target.id)
    if (facing) player.face(facing)
    // Si li parla o li dona alguna cosa, el personatge també es gira cap a ella.
    if (target.kind === 'character' && (verb === 'talkTo' || verb === 'give' || item)) {
      const npcFacing = npcFacingPlayer(target.id)
      const npc = benneCharacter(fromBenne('characters', target.id)) as unknown as { face: { now(d: 'L' | 'R' | 'DL' | 'DR'): unknown } } | undefined
      if (npcFacing && npc) npc.face.now(npcFacing)
    }
  }
  adoptLoadedState()
  playerActed()
  // A la carta, un cop triat on anar, la frase ja no diu «On anem?».
  if (isClickableCutscene(narrative.world.currentRoom())) setClickablePrompt('')
  const request = { verb, target: targetFromBenne(target.kind, target.id), item: item ? fromBenne('items', item) : undefined }
  const room = narrative.world.currentRoom()
  const result = primeStage(narrative.interact(request))
  touchRouter()?.acted?.(verb, target, room)
  // Una porta (o escotilla, o escala) que porta a una altra sala: el seu so sonarà en arribar-hi.
  setDoorSound(result?.goTo && !result.dialogue && target.kind !== 'item' ? narrative.world.currentRoom() : null, fromBenne('hotspots', target.id))
  if (result) playResult(result)
  else playLines([narrative.defaultLine(verb)])
}

/**
 * En carregar una partida (des de `game.onLoadedAnyRoom`): Benne no crida els ganxos d'entrada, i la
 * partida porta desat qui es veia. Una veu desada visible (partides d'abans) sortiria a la sala.
 */
export function onRoomLoaded() {
  adoptLoadedState()
  untouchedNewGame = false
  statsLoadedGame()
  applySwitchButton()
  const room = narrative.world.currentRoom()
  if (room) resetStageAnims(room)
  applyHotspotVisibility()
  applyAppearances()
  applyPlaces(false)
  startPatrols()
}

/**
 * En entrar a una sala, abans del fos (des de `game.onEnterAnyRoom`): prepara la partida si és
 * nova, pren el control de la protagonista de la sala i mostra o amaga les coses condicionals.
 */
export function onRoomEntered() {
  // En desenvolupament, `window.__aventura.provar(situació)` porta la partida a una situació (vegeu `prepareSituation`).
  // `goTo` acaba el handler llançant un símbol; des de la consola no hi ha handler que el reculli: s'ignora.
  if (import.meta.env.DEV) (window as unknown as { __aventura?: unknown }).__aventura = { provar: provarDesDeLaConsola, narrative, ambient }
  adoptLoadedState()
  ensureStarted()
  const room = narrative.world.currentRoom()
  if (!room) return
  // A la portada i a les cinemàtiques (el pròleg) no hi ha res per clicar: fora la barra de verbs. Una cinemàtica
  // amb coses per tocar (la carta de navegació), amb la interfície tàctil, deixa la frase (el HUD només hi posa això).
  const portada = room === narrative.content.manifest.cover
  const ambFrase = isClickableCutscene(room) && touchRouter() !== null
  if (portada || (narrative.content.rooms[room]?.cutscene && !ambFrase)) guis.verbs.hide()
  else guis.verbs.show()
  if (portada) {
    guis.portada.show()
    // «Comença» esvaeix el títol (vegeu `startFromCover`), i l'alfa queda desada: en tornar-hi, torna a ser-hi.
    const titol = roomProp(room, 'titol')
    if (titol) titol.alpha = 1
  } else guis.portada.hide()
  applySwitchButton()
  // A una sala compartida hi entra qui juga, o l'altra si s'hi va per canviar de protagonista.
  const entering = takeEnteringProtagonist()
  const who = isSharedRoom(room) ? (entering ?? narrative.world.activeProtagonist()) : roomProtagonist(room)
  applyAmbientMusic(room, portada)
  const porta = takeDoorSound()
  if (porta) new SfxHandle(porta).play()
  if (who) {
    if (narrative.world.activeProtagonist() !== who) {
      const character = benneCharacter(who)
      if (character) player.switchTo(character)
    }
    // Qui entra per una porta apareix davant de la porta (vegeu `doorPoint`).
    const from = protagonistRoom(who)
    const porta = from && from !== room ? doorPoint(room, from) : null
    if (porta) player.moveTo(porta)
    rememberProtagonistRoom(who, room)
  }
  resetStageAnims(room)
  applyHotspotVisibility()
  applyAppearances()
  applyPlaces(false)
  // L'onEnter es resol ara, abans del fos, i es reprodueix després (`enterNarrativeRoom`). Si comença
  // amb un títol, la pantalla es posa a negre ja: si no, es veuria la sala, s'enfosquiria i tornaria.
  narrative.worldChanged()
  const result = primeStage(narrative.enterRoom(room))
  entrada = { room, result }
  if (result?.lines[0]?.who === 'title') stayBlackOnEnter()
  // Com comença l'escena (qui hi ha, on, assegut o dret) ja es veu en sortir del fos: el moviment, després.
  for (const cue of result?.lines[0]?.stage ?? []) applyStageNow(cue)
  // Entrada caminant: abans del fos, la protagonista es posa fora de la pantalla, a la mateixa alçada.
  if (result?.walkIn) {
    const lloc = player.position
    entrada.walkTo = lloc
    player.moveTo({ x: result.walkIn === 'left' ? -FORA : AMPLADA + FORA, y: lloc.y })
  } else if (who && isSharedRoom(room)) {
    const aparta = apartaDeLAltra(room, who)
    if (aparta) entrada.walkTo = aparta
  }
}

/** Quants píxels fora de la pantalla comença una entrada caminant (`walkIn`). */
const FORA = 24
/** Quant s'aparta la protagonista que entra si l'altra és al mateix lloc (vegeu `apartaDeLAltra`). */
const APARTA = { x: 30, y: 8 }

/**
 * Les protagonistes surten per la mateixa porta (s'hi acosten fins al `walkToPoint`) i Benne desa la posició de
 * cadascuna a cada sala: en tornar-hi, la segona apareixeria just damunt de la primera. Si és així, torna on ha
 * de caminar la que entra perquè no es tapin: cap al mig de la sala i una mica endavant. Si el punt no és de
 * la zona on es camina, Benne s'hi acosta tant com pot.
 */
function apartaDeLAltra(room: string, who: string): { x: number; y: number } | null {
  const lloc = (benneCharacter(who) as { position?: { x: number; y: number } } | undefined)?.position
  if (!lloc) return null
  for (const id of narrative.content.rooms[room]?.protagonists ?? []) {
    if (id === who || protagonistRoom(id) !== room) continue
    const at = (benneCharacter(id) as { position?: { x: number; y: number } } | undefined)?.position
    if (!at || Math.hypot(at.x - lloc.x, at.y - lloc.y) >= APARTA.x / 2) continue
    return { x: lloc.x + (lloc.x < AMPLADA / 2 ? APARTA.x : -APARTA.x), y: lloc.y + APARTA.y }
  }
  return null
}

/**
 * Música d'ambient (`music` al mapping.json del joc): cada sala, o cada protagonista, té la seva peça, i
 * en canviar d'una a l'altra s'encadenen (amb `musicSync`, al mateix punt del tema). Les sales sense
 * peça (les cinemàtiques) continuen amb la que sonava; la portada sense peça és en silenci.
 */
function applyAmbientMusic(room: string, portada: boolean) {
  const track = roomMusic(room)
  if (!track) {
    if (portada && music.isPlaying) music.stop()
    return
  }
  const handle = new MusicHandle(track)
  if (!handle.isPlaying) handle.play({ fadeSeconds: 2.5, ...(musicSync ? { sync: true } : {}) })
}

/** L'onEnter de la sala on acabem d'entrar, resolt abans del fos (vegeu `onRoomEntered`). */
let entrada: { room: string; result: InteractionResult | null; walkTo?: { x: number; y: number } } | null = null

/**
 * Una partida nova on encara no s'ha fet res: no desa sola, perquè si s'ha clicat «Comença» per
 * error la partida d'abans (el botó «Continua») no es perdi. Deixa de ser-ho a la primera acció.
 */
let untouchedNewGame = false

/** El jugador fa alguna cosa (una acció, una conversa, canviar de protagonista). */
function playerActed() {
  if (!untouchedNewGame) return
  untouchedNewGame = false
  saves.autosave(AUTOSAVE)
}

/**
 * Desa la partida en acabar una interacció o un diàleg (`saves.autosave` espera que s'acabin), perquè «Continua» no
 * perdi el que s'ha fet dins d'una sala (les revisions de la infermeria de Ni un ou). Mai a la portada, a una
 * cinemàtica, al final ni en una partida nova on encara no s'ha fet res.
 */
function autosaveHere() {
  const room = narrative.world.currentRoom()
  if (untouchedNewGame || room === narrative.content.manifest.cover || narrative.content.rooms[room]?.cutscene || finale.length) return
  saves.autosave(AUTOSAVE)
}

/** Qui vol saber que s'ha clicat «Comença» (la targeta «Com es juga», als jocs tàctils: vegeu controls.ts). */
const enComencar: Array<() => void> = []

/** Crida `fn` cada cop que es comença una partida nova des de la portada. */
export function onNewGame(fn: () => void) {
  enComencar.push(fn)
}

/** El botó «Comença» de la portada: el pròleg, si n'hi ha, o la sala de la primera protagonista. */
export function startFromCover() {
  // Per provar els finals (només en desenvolupament): `?final=<id>` a l'adreça (vegeu `prepareEndingPreview`).
  const query = import.meta.env.DEV ? new URLSearchParams(location.search) : null
  const provar = query?.get('final')
  if (provar && narrative.content.endings[provar]) {
    prepareEndingPreview(provar, query!)
    playEnding(provar)
    return
  }
  untouchedNewGame = true
  statsNewGame()
  for (const fn of enComencar) fn()
  const manifest = narrative.content.manifest
  // Si la portada té el títol en una capa a part (`titol`), els botons se'n van i el títol s'esvaeix: el pròleg
  // comença al mateix pla (Ni un ou), i s'hi passa amb un tall net, sense fosa a negre.
  const titol = manifest.cover ? roomProp(manifest.cover, 'titol') : undefined
  if (titol) {
    guis.portada.hide()
    titol.fade(0, 1.5)
  }
  const first = manifest.protagonists[0]!
  const desti = manifest.intro ?? manifest.start?.[first]?.room
  const sala = desti ? benneRoom(desti) : undefined
  if (sala) sala.goTo({ cut: !!titol })
}

/** Provar una situació (vegeu `prepareSituation`): hi posa la partida i hi va, amb qui juga. */
export function provarSituacio(s: Situacio) {
  const sala = prepareSituation(s)
  setEnteringProtagonist(s.active)
  const room = benneRoom(sala)
  if (room) room.goTo()
}

/** `provarSituacio` des de la consola del navegador, sense l'avís de «Uncaught (in promise)» del final del handler. */
function provarDesDeLaConsola(s: Situacio) {
  Promise.resolve().then(() => provarSituacio(s)).catch((e: unknown) => {
    if (typeof e !== 'symbol') console.error(e)
  })
}

/** Va a la sala on és una protagonista (i, en entrar-hi, se'n pren el control). */
export function goToProtagonist(who: string) {
  const roomId = protagonistRoom(who)
  const room = roomId ? benneRoom(roomId) : undefined
  if (!room) return
  // Si és a la mateixa sala (una sala compartida), es canvia sense sortir-ne.
  if (roomId === narrative.world.currentRoom()) {
    const character = benneCharacter(who)
    if (character) player.switchTo(character)
    narrative.worldChanged()
    applySwitchButton()
    applyHotspotVisibility()
    applyAppearances()
    return
  }
  setEnteringProtagonist(who)
  room.goTo()
}

/** En entrar a una sala (després del fos): l'`onEnter` del JSON. */
export function enterNarrativeRoom() {
  adoptLoadedState()
  const room = narrative.world.currentRoom()
  if (!room) return
  let result: InteractionResult | null
  let walkTo: { x: number; y: number } | undefined
  if (entrada?.room === room) {
    result = entrada.result
    walkTo = entrada.walkTo
  } else {
    narrative.worldChanged()
    result = primeStage(narrative.enterRoom(room))
  }
  entrada = null
  startPatrols()
  if (finale[0]?.room === room) {
    playFinaleRoom()
    return
  }
  const cutscene = narrative.content.rooms[room]?.cutscene
  // Desa la partida a cada sala jugable, per si es recarrega la pàgina: el botó «Continua» de la
  // portada la recupera. Espera que acabi l'onEnter (no desa mai a mitja escena). En una partida
  // nova, no fins que s'hi faci alguna cosa (`playerActed`).
  if (room !== narrative.content.manifest.cover && !cutscene && !untouchedNewGame) saves.autosave(AUTOSAVE)
  // Sense onEnter (o ja dit), la protagonista també ha de fer el pas d'entrada o d'apartar-se de l'altra.
  if (!result) {
    if (walkTo && !cutscene) player.walkTo.now(walkTo)
    return
  }
  // Cinemàtica amb coses per tocar (la carta de navegació): l'onEnter no s'atura a cada línia ni espera cap clic. Es
  // fa el moviment (on és la nau) i el text queda a la frase del HUD («On anem?») fins que hi ha alguna cosa a sota.
  if (cutscene && isClickableCutscene(room)) {
    for (const line of result.lines) for (const cue of [...(line.stage ?? []), ...(line.stageAfter ?? [])]) applyStageNow(cue)
    setClickablePrompt(result.lines.map((l) => l.text).join(' '))
    return
  }
  if (!cutscene) {
    if (walkTo) player.walkTo(walkTo)
    playResult(result)
    return
  }
  // Cinemàtica que obre un diàleg: sense protagonista ni barra de verbs, però amb les opcions del diàleg. On anar
  // després ho diu el diàleg (`anar`).
  if (result.dialogue) {
    playResult(result)
    return
  }
  // Cinemàtica: Benne ja embolica aquest moment en una cutscene, i amb Esc la resta s'acaba de cop.
  // Si l'han saltada, anem directament al final (`skipTo`) en lloc de passar per les altres pantalles.
  const final = takePendingEnding()
  const negre = result.goTo || final ? 'negre' : undefined
  let saltada = false
  for (let k = 0; k < result.lines.length; k++) {
    const more = k < result.lines.length - 1
    playLines([result.lines[k]!], { before: result.lines[k - 1]?.who, after: result.lines[k + 1]?.who ?? negre, more })
    // Mentre se salta una cinemàtica, `wait` acaba a l'instant: així sabem si han premut Esc.
    const inici = Date.now()
    wait(0.1)
    if (Date.now() - inici < 50) {
      saltada = true
      break
    }
  }
  // Saltada a mitges: l'estat de la sala no s'ha aplicat (vegeu `more`).
  if (saltada) {
    applyHotspotVisibility()
    applyPlaces(false)
  }
  if (final) {
    // La cinemàtica acaba el joc (l'avió: «Continuarà»).
    takePendingSwitch()
    playEnding()
    return
  }
  const desti = saltada && cutscene.skipTo ? cutscene.skipTo : result.goTo
  const sala = desti ? benneRoom(desti) : undefined
  if (sala) sala.goTo()
}

/**
 * Tanca el diàleg i fa el que s'hagi demanat (canvi de protagonista, de sala, final). A Benne, `dialog.end()`
 * acaba el handler (llança): sense aturar-ho, el que ve després no es faria mai i, si el diàleg acabava amb
 * un títol, la pantalla es quedaria a negre.
 */
function endDialog(dialog: DialogHandle) {
  try {
    dialog.end()
  } catch (e) {
    // Les maneres d'acabar de Benne són símbols; un error de debò, no.
    if (typeof e !== 'symbol') throw e
  }
  followUp()
}

function refreshOptions(dialog: DialogHandle, choices: ResolvedChoice[]) {
  // L'opció triada es diu en veu alta: la seva veu, que ja vingui.
  preloadLineVoices(choices.map((c) => ({ who: 'player', key: c.key, text: c.text })))
  const available = new Set(choices.map((c) => optionName(c.node, c.id)));
  for (const [name, option] of Object.entries(dialog.options)) {
    if (available.has(name)) option.on();
    else option.off();
  }
}

/** Des de `dialog.onStart` (generat). */
export function startNarrativeDialog(id: string, dialog: DialogHandle) {
  adoptLoadedState()
  playerActed()
  const step = primeStage(narrative.startDialogue(id))
  refreshOptions(dialog, step.choices)
  playLines(step.lines, { after: step.ended && leavesRoom() ? 'negre' : undefined })
  if (step.ended) endDialog(dialog)
}

/** Des de cada `options.x.onChoose` (generat). */
export function chooseNarrativeOption(id: string, dialog: DialogHandle, node: string, choice: string) {
  adoptLoadedState()
  // La primera línia és l'opció dita en veu alta (si no és `silent`): el decorat de l'escena és a la següent.
  const echo = narrative.content.dialogues[id]?.nodes[node]?.choices?.find((c) => c.id === choice)?.silent ? 0 : 1
  const step = primeStage(narrative.choose(id, choice, { node }), echo)
  refreshOptions(dialog, step.choices)
  playLines(step.lines, { after: step.ended && leavesRoom() ? 'negre' : undefined })
  if (step.ended) endDialog(dialog)
}

/**
 * Botó o verb de "pista": cada vegada una mica més explícita. Si la pista apunta a coses de la sala (`targets`), hi
 * surten uns filaments que hi porten (la lupa de L'Última Arrel); si la diu una altra (`who`, p. ex. la germana pel
 * walkie), la diu ella.
 */
export function sayHint() {
  const hint = narrative.requestHint()
  const text = hint ? hint.text : narrative.noHintText()
  const key = hint ? hint.key : narrative.noHintKey()
  if (hint?.targets.length) {
    const ids = hint.targets.map((t) => (narrative.content.characters[t] ? toBenne('characters', t) : toBenne('hotspots', t)))
    game.showThreads(ids, 3.2)
  }
  const speaker = hint?.who ? benneCharacter(hint.who) : undefined
  if (hint?.who && speaker) {
    playLines([{ who: hint.who, key, text }])
    return
  }
  preloadLineVoices([{ who: 'player', key, text }])
  recordLine('player', text)
  player.say(voiced(player.id, key, text))
}

/** Canvia a l'altra protagonista (per a un botó de la GUI): va a la sala on és. */
export function switchProtagonist() {
  if (!narrative.canSwitch()) return
  playerActed()
  const all = narrative.content.manifest.protagonists
  const next = all[(all.indexOf(narrative.world.activeProtagonist()) + 1) % all.length]!
  goToProtagonist(next)
}

/** Una línia d'un final: els personatges ja no hi són, i el que diuen surt amb el nom al davant. */
type EndingLine = { who: string; key?: string; text: string; sound?: string; effects?: Effect[]; stage?: StageCue[]; stageAfter?: StageCue[] }

/**
 * Una línia d'un final. Damunt d'una sala (`enSala`), qui hi és i es veu la diu amb bafarada, com a la resta del
 * joc, i els `effects` de la línia s'apliquen abans (algú que es mou, una cosa que s'apaga). Si no, és text.
 */
function displayEndingLine(line: EndingLine, enSala = false) {
  // Damunt d'una sala, el moviment de la línia (`stage`, `stageAfter`), com a les interaccions: qui serveix, qui es gira.
  if (enSala && line.stage) playStage(line.stage)
  sayEndingLine(line, enSala)
  if (enSala && line.stageAfter) playStage(line.stageAfter)
}

function sayEndingLine(line: EndingLine, enSala: boolean) {
  recordLine(line.who, line.text)
  if (line.sound) new SfxHandle(line.sound).play()
  if (enSala && line.effects?.length) {
    narrative.apply(line.effects)
    applyHotspotVisibility()
    applyAppearances()
    applyPlaces(false)
  }
  if (line.who === 'narrator') {
    // Amb veu, com a la resta del joc (`narrator<número>`, que el motor fa sonar des de `display`).
    display(voiced('narrator', line.key, line.text))
    return
  }
  if (line.who === 'title' || line.who === 'player') {
    display(line.text)
    return
  }
  const speaker = enSala ? (benneCharacter(line.who) as { id: string; visible?: boolean; say?(text: string): void } | undefined) : undefined
  if (speaker?.visible && speaker.say) speaker.say(voiced(speaker.id, line.key, line.text))
  else display(`${narrative.characterName(line.who)}: ${line.text}`)
}

/**
 * Un final amb imatges (`room` a les línies de l'escena): les línies que van damunt de cada sala.
 * Es reprodueixen en entrar-hi (`enterNarrativeRoom`), com el pròleg, i després es passa a la següent.
 */
let finale: { room: string; lines: EndingLine[] }[] = []

/** Mostra el final que toca (o el que li diguis). */
export function playEnding(id?: string) {
  const endingId = id ?? narrative.resolveEnding()
  if (!endingId) return
  const ending = narrative.ending(endingId)
  statsEnding(endingId)
  // Trossos de l'escena: el que va sobre negre (abans de la primera sala) i el que va damunt de cada sala.
  const negre: EndingLine[] = []
  const trossos: typeof finale = []
  for (const line of ending.scene) {
    const actual = trossos[trossos.length - 1]
    if (line.room && line.room !== actual?.room) trossos.push({ room: line.room, lines: [line] })
    else (actual ? actual.lines : negre).push(line)
  }
  const tancament = { who: 'narrator', key: narrative.content.endings[endingId]?.text, text: ending.text }
  const ultim = trossos[trossos.length - 1]
  if (ending.textRoom && ending.textRoom !== ultim?.room) trossos.push({ room: ending.textRoom, lines: [tancament] })
  else (ultim ? ultim.lines : negre).push(tancament)
  // Els crèdits, després del text final: amb `room`, a la seva sala; si no, damunt de la que hi hagi.
  for (const line of ending.credits) {
    const actual = trossos[trossos.length - 1]
    if (line.room && line.room !== actual?.room) trossos.push({ room: line.room, lines: [line] })
    else (actual ? actual.lines : negre).push(line)
  }

  fadeOut(1.5)
  display(ending.title)
  for (const line of negre) displayEndingLine(line)
  const primer = trossos[0]
  const sala = primer ? benneRoom(primer.room) : undefined
  if (!sala) {
    showTheEnd()
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
    displayEndingLine(line, true)
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
  showTheEnd()
}

/**
 * El «Fi»: quan el jugador hi clica (o passa l'estona), torna a la portada. Es recarrega el joc, perquè la partida
 * acabada no quedi a mitges en memòria; «Continua» hi torna des de la darrera sala desada.
 */
function showTheEnd() {
  display(narrative.t('ui.fi'))
  wait(0.5)
  location.reload()
}

// ─── Rondes (`patrol` a characters.json) ─────────────────────────────────────

type PatrolActor = {
  position: { x: number; y: number }; visible: boolean; stopWalking(): void;
  walkTo: { now(p: { x: number; y: number }): unknown }; face: (d: 'L' | 'R' | 'U' | 'D') => void;
}

/** En entrar a una sala (o carregar-hi una partida): qui hi pot fer ronda la fa en segon pla. */
function startPatrols() {
  const room = narrative.world.currentRoom()
  if (!room) return
  for (const [id, def] of Object.entries(narrative.content.characters)) {
    if (def.patrol?.some((p) => p.room === room)) background(() => { patrol(id, room) })
  }
}

/** Si el ratolí és damunt d'un personatge. */
function hovered(id: string): boolean {
  const h = pointer.hover
  if (!h?.kind || !h.id || h.kind !== 'character') return false
  return targetFromBenne(h.kind, h.id).id === id
}

/**
 * La ronda d'un personatge: mentre l'estat la demani, va de punt en punt i s'hi atura una estona. Si passa
 * alguna cosa (una línia, una conversa, una cinemàtica), s'atura on és, i després continua cap al mateix
 * punt. S'acaba en sortir de la sala (Benne atura els blocs de segon pla).
 */
function patrol(id: string, room: string) {
  const actor = benneCharacter(id) as unknown as PatrolActor | undefined
  if (!actor) return
  let next = 0
  let walking = false
  let still = 0
  let last = { x: -1, y: -1 }
  while (narrative.world.currentRoom() === room) {
    const route = narrative.patrolOf(id, room)
    // (també s'atura mentre el ratolí hi és a sobre: si no, un robot que va i ve costa d'encertar)
    if (!route || !actor.visible || game.isBusy || narrative.world.activeProtagonist() === id || hovered(id)) {
      if (walking) actor.stopWalking()
      walking = false
      wait(0.25)
      continue
    }
    const to = route.path[next % route.path.length]!
    if (!walking) {
      actor.walkTo.now({ x: to.x, y: to.y })
      walking = true
      still = 0
    }
    wait(0.2)
    const at = actor.position
    still = Math.hypot(at.x - last.x, at.y - last.y) < 0.5 ? still + 1 : 0
    last = { x: at.x, y: at.y }
    // Hi ha arribat (o no s'hi pot acostar més: el punt és fora de la zona on es camina).
    if (Math.hypot(at.x - to.x, at.y - to.y) < 3 || still >= 3) {
      walking = false
      next++
      if (to.face) actor.face(to.face)
      wait(route.pause ?? 1.5)
    }
  }
}
