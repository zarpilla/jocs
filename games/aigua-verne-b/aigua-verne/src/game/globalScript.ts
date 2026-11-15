// ── GENERAT per adapters/benne/sync.ts: inici. No l'editis. ──
import { game } from '@benne/script';
import { fallbacks } from '@game';
import { enterNarrativeRoom, onRoomEntered, onRoomLoaded, routeInteraction } from './narrative/narrative.script';

// Totes les interaccions que cap script de sala, personatge o objecte no gestiona
// les resol el JSON del joc (game/data/rooms, characters.json, items.json).
// No registris aquí `fallbacks.on<Verb>` ni `fallbacks.onAnyVerb`: taparien aquest encaminament.
fallbacks.onUnhandled((verb, target) => {
  routeInteraction(verb.id, target)
})

// Objecte de l'inventari fet servir sobre alguna cosa.
fallbacks.onUseItem((item, target) => {
  routeInteraction('use', target, item.id)
})
fallbacks.onGiveItem((item, target) => {
  routeInteraction('give', target, item.id)
})
fallbacks.onItemUnhandled((item, target) => {
  routeInteraction('use', target, item.id)
})

// Abans del fos: partida nova, protagonista de la sala, coses condicionals.
game.onEnterAnyRoom(() => {
  onRoomEntered()
})

// Després del fos: l'onEnter de cada sala (game/data/rooms/<sala>.json).
game.onEnterAnyRoomAfterFade(() => {
  enterNarrativeRoom()
})

// En carregar una partida no hi ha entrada a la sala: es tornen a mirar les coses condicionals.
game.onLoadedAnyRoom(() => {
  onRoomLoaded()
})
// ── GENERAT per adapters/benne/sync.ts: fi. Pots afegir codi a sota. ──
import { setTouchRouter } from './narrative/narrative';
import { touchRouter } from './narrative/tactil';

// Aigua Verne B: la interfície sense barra de verbs (narrative/tactil.script.ts) es queda els clics de tocar i del
// menú d'accions, i tria entre donar i fer servir quan hi ha un objecte a la mà.
setTouchRouter(touchRouter)
