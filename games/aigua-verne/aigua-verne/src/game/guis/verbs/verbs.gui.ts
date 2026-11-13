import { onUpdate, player, pointer } from '@benne/script';
import { guis, verbs } from '@game';
import {
  gui, closeBtn, giveBtn, lookAtBtn, menuBtn, openBtn, pickUpBtn, pullBtn, pushBtn, talkToBtn, useBtn, verbLineText, canviaBtn,
  caraIri, caraVet,
} from './verbs.ids';
import { switchProtagonist } from '../../narrative/narrative.script';

const buttons = new Map([
  [verbs.give, giveBtn],
  [verbs.pickUp, pickUpBtn],
  [verbs.use, useBtn],
  [verbs.open, openBtn],
  [verbs.look, lookAtBtn],
  [verbs.push, pushBtn],
  [verbs.close, closeBtn],
  [verbs.talkTo, talkToBtn],
  [verbs.pull, pullBtn],
])

// Clicking a verb button makes it the verb for the next click on the room.
for (const [verb, button] of buttons) button.onClick(() => verb.select())

menuBtn.onClick(() => guis.gameMenu.show())

// The verb line ("Use Knife with Bread"), and the hovered thing's default verb lit up.
function refresh() {
  verbLineText.text = pointer.sentence
  const highlighted = pointer.hover?.defaultVerb
  for (const [verb, button] of buttons) {
    button.visualState = verb === highlighted ? 'hover' : 'normal'
  }
}

gui.onBuilt(refresh)
pointer.onContextChange(refresh)

// Afegit per adapters/benne (benne-content.ts): canviar de protagonista.
canviaBtn.onClick(() => switchProtagonist())

// La pantalla rodona del botó «Canvia» mostra la cara de l'altra protagonista (la que no juga). Les cares són dues
// imatges (adapters/benne/tools/hd640/gui_rest.py); el botó es mostra o s'amaga des de narrative.ts, per això es mira
// a cada fotograma (només s'escriu quan canvia).
onUpdate(() => {
  const on = canviaBtn.visible
  const iri = on && player.id === 'vet'
  const vet = on && player.id !== 'vet'
  if (caraIri.visible !== iri) caraIri.visible = iri
  if (caraVet.visible !== vet) caraVet.visible = vet
})
