// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
/**
 * Pont amb Benne, part seqüenciada (BenneScript): parlar, conduir diàlegs,
 * fer les interaccions del JSON, canviar de protagonista, pistes i finals.
 * Les funcions exportades d'un `*.script.ts` són "step functions": cada línia
 * espera l'anterior, com als scripts de sala.
 *
 * Es copia a `src/game/narrative/` amb `npm run benne:sync`. No l'editis allà.
 */
import { MusicHandle, SfxHandle, ambient, background, cutscene, display, fadeIn, fadeOut, game, player, saves, stayBlackOnEnter, wait } from '@benne/script';
import type { DialogHandle, FallbackTarget } from '@benne/script';
import { guis, music } from '@game';
import type { Effect, InteractionResult, ResolvedChoice, ResolvedLine, StageCue } from '@aventura/narrative-core';
import {
  AMPLADA, AUTOSAVE, applyStageNow, stageActor, stagePoint, adoptLoadedState, prepareSituation, type Situacio, applyAppearances, prepareEndingPreview, applyPlaces, facingToward, applySwitchButton, applyHotspotVisibility, showSpeaker, showDueCharacters, benneCharacter, benneDialog, benneRoom, ensureStarted, fromBenne, narrative, optionName, protagonistRoom,
  musicSync, roomMusic, recordLine, setDoorSound, takeDoorSound, rememberProtagonistRoom, roomProtagonist, isSharedRoom, setEnteringProtagonist, takeEnteringProtagonist, takePendingEnding, takePendingSwitch, takePendingGoTo, leavesRoom, targetFromBenne,
} from './narrative';
import { statsEnding, statsLoadedGame, statsNewGame } from './estadistiques';

/**
 * Què hi ha just abans i just després d'aquestes línies, quan es diuen a trossos (les cinemàtiques en diuen
 * una cada vegada): `before`/`after` són el `who` de la línia del costat; `after: 'negre'` vol dir que tot
 * seguit es canvia de sala o ve un final, i la pantalla s'ha de quedar a negre.
 */
type Around = { before?: string; after?: string }

/**
 * Diu les línies una darrere l'altra (i fa sonar el so de cada una en començar-la). Si n'hi ha amb moviment
 * (`stage`, `stageAfter`), és una petita cinemàtica: els clics al món no la tallen, i la tecla de saltar l'acaba de cop.
 */
export function playLines(lines: ResolvedLine[], around: Around = {}) {
  if (lines.some((l) => l.stage || l.stageAfter)) {
    cutscene(() => {
      sayLines(lines, around)
      // I en acabar, cadascú torna a l'animació que diu l'estat (p. ex. en Bastida, assegut).
      applyAppearances()
    })
  } else sayLines(lines, around)
}

/** Les indicacions d'escena d'una línia, per ordre: el que és de cop, i caminar (esperant-hi o no). */
function playStage(cues: StageCue[]) {
  for (const cue of cues) {
    applyStageNow(cue)
    if (cue.walk === undefined) continue
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
      display(line.text)
    } else if (line.who === 'player') {
      player.say(line.text)
    } else {
      const speaker = benneCharacter(line.who)
      if (speaker) {
        showSpeaker(line.who)
        speaker.say(line.text)
      } else display(line.text)
    }
    if (line.stageAfter) playStage(line.stageAfter)
  }
  // Qui s'ha de moure (`place`) hi camina ara, quan ja s'ha dit tot: els efectes s'apliquen abans de les
  // línies, i si caminés abans, marxaria mentre parla. El mateix amb qui desapareix i amb qui apareix.
  applyHotspotVisibility()
  applyPlaces(true)
}

/** Fa el que diu el resultat d'una interacció: línies, diàleg, canvi de protagonista o de sala. */
export function playResult(result: InteractionResult) {
  playLines(result.lines, { after: !result.dialogue && leavesRoom(result.goTo) ? 'negre' : undefined })
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

/** Després d'una interacció o d'un diàleg: el final, el canvi de protagonista o la sala nova que s'hagin demanat. */
function followUp(goTo?: string) {
  if (takePendingEnding()) {
    takePendingSwitch()
    takePendingGoTo()
    playEnding()
    return
  }
  const who = takePendingSwitch()
  const anar = takePendingGoTo() ?? goTo
  if (who) {
    goToProtagonist(who)
    return
  }
  if (anar) {
    const room = benneRoom(anar)
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
  playerActed()
  const request = { verb, target: targetFromBenne(target.kind, target.id), item: item ? fromBenne('items', item) : undefined }
  const result = narrative.interact(request)
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
  if (import.meta.env.DEV) (window as unknown as { __aventura?: unknown }).__aventura = { provar: provarSituacio, narrative, ambient }
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
    rememberProtagonistRoom(who, room)
  }
  applyHotspotVisibility()
  applyAppearances()
  applyPlaces(false)
  // L'onEnter es resol ara, abans del fos, i es reprodueix després (`enterNarrativeRoom`). Si comença
  // amb un títol, la pantalla es posa a negre ja: si no, es veuria la sala, s'enfosquiria i tornaria.
  narrative.worldChanged()
  const result = narrative.enterRoom(room)
  entrada = { room, result }
  if (result?.lines[0]?.who === 'title') stayBlackOnEnter()
  // Com comença l'escena (qui hi ha, on, assegut o dret) ja es veu en sortir del fos: el moviment, després.
  for (const cue of result?.lines[0]?.stage ?? []) applyStageNow(cue)
  // Entrada caminant: abans del fos, la protagonista es posa fora de la pantalla, a la mateixa alçada.
  if (result?.walkIn) {
    const lloc = player.position
    entrada.walkTo = lloc
    player.moveTo({ x: result.walkIn === 'left' ? -FORA : AMPLADA + FORA, y: lloc.y })
  }
}

/** Quants píxels fora de la pantalla comença una entrada caminant (`walkIn`). */
const FORA = 24

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
  const manifest = narrative.content.manifest
  const first = manifest.protagonists[0]!
  const desti = manifest.intro ?? manifest.start?.[first]?.room
  const sala = desti ? benneRoom(desti) : undefined
  if (sala) sala.goTo()
}

/** Provar una situació (vegeu `prepareSituation`): hi posa la partida i hi va, amb qui juga. */
export function provarSituacio(s: Situacio) {
  const sala = prepareSituation(s)
  setEnteringProtagonist(s.active)
  const room = benneRoom(sala)
  if (room) room.goTo()
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
    result = narrative.enterRoom(room)
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
  if (!result) return
  if (!cutscene) {
    if (walkTo) player.walkTo(walkTo)
    playResult(result)
    return
  }
  // Cinemàtica: Benne ja embolica aquest moment en una cutscene, i amb Esc la resta s'acaba de cop.
  // Si l'han saltada, anem directament al final (`skipTo`) en lloc de passar per les altres pantalles.
  const final = takePendingEnding()
  const negre = result.goTo || final ? 'negre' : undefined
  let saltada = false
  for (let k = 0; k < result.lines.length; k++) {
    playLines([result.lines[k]!], { before: result.lines[k - 1]?.who, after: result.lines[k + 1]?.who ?? negre })
    // Mentre se salta una cinemàtica, `wait` acaba a l'instant: així sabem si han premut Esc.
    const inici = Date.now()
    wait(0.1)
    if (Date.now() - inici < 50) {
      saltada = true
      break
    }
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
  const step = narrative.startDialogue(id)
  refreshOptions(dialog, step.choices)
  playLines(step.lines, { after: step.ended && leavesRoom() ? 'negre' : undefined })
  if (step.ended) endDialog(dialog)
}

/** Des de cada `options.x.onChoose` (generat). */
export function chooseNarrativeOption(id: string, dialog: DialogHandle, node: string, choice: string) {
  adoptLoadedState()
  const step = narrative.choose(id, choice, { node })
  refreshOptions(dialog, step.choices)
  playLines(step.lines, { after: step.ended && leavesRoom() ? 'negre' : undefined })
  if (step.ended) endDialog(dialog)
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
  playerActed()
  const all = narrative.content.manifest.protagonists
  const next = all[(all.indexOf(narrative.world.activeProtagonist()) + 1) % all.length]!
  goToProtagonist(next)
}

/** Una línia d'un final: els personatges ja no hi són, i el que diuen surt amb el nom al davant. */
type EndingLine = { who: string; text: string; sound?: string; effects?: Effect[] }

/**
 * Una línia d'un final. Damunt d'una sala (`enSala`), qui hi és i es veu la diu amb bafarada, com a la resta del
 * joc, i els `effects` de la línia s'apliquen abans (algú que es mou, una cosa que s'apaga). Si no, és text.
 */
function displayEndingLine(line: EndingLine, enSala = false) {
  recordLine(line.who, line.text)
  if (line.sound) new SfxHandle(line.sound).play()
  if (enSala && line.effects?.length) {
    narrative.apply(line.effects)
    applyHotspotVisibility()
    applyAppearances()
    applyPlaces(false)
  }
  if (line.who === 'narrator' || line.who === 'title' || line.who === 'player') {
    display(line.text)
    return
  }
  const speaker = enSala ? (benneCharacter(line.who) as { visible?: boolean; say?(text: string): void } | undefined) : undefined
  if (speaker?.visible && speaker.say) speaker.say(line.text)
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
  const tancament = { who: 'narrator', text: ending.text }
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
  display(narrative.t('ui.fi'))
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
    if (!route || !actor.visible || game.isBusy || narrative.world.activeProtagonist() === id) {
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
