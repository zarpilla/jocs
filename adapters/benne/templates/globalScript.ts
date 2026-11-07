import { game } from '@benne/script';
import { fallbacks } from '@game';
import { enterNarrativeRoom, routeInteraction } from './narrative/narrative.script';

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

// L'onEnter de cada sala (game/data/rooms/<sala>.json).
game.onEnterAnyRoomAfterFade(() => {
  enterNarrativeRoom()
})
