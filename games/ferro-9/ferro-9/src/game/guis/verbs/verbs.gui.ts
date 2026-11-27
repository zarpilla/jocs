import { pointer } from '@benne/script';
import { guis, verbs } from '@game';
import {
  gui, closeBtn, giveBtn, lookAtBtn, menuBtn, openBtn, pickUpBtn, pullBtn, pushBtn, talkToBtn, useBtn, verbLineText, canviaBtn,
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

// The verb line ("Use Knife with Bread"), the chosen verb pressed (white) and the hovered thing's default verb
// lit up (gold), so the two don't look the same (tasca 068).
function refresh() {
  verbLineText.text = pointer.sentence
  const armed = pointer.verb
  const highlighted = pointer.hover?.defaultVerb
  for (const [verb, button] of buttons) {
    button.visualState = verb === armed ? 'pressed' : verb === highlighted ? 'hover' : 'normal'
  }
}

gui.onBuilt(refresh)
pointer.onContextChange(refresh)

// Afegit per adapters/benne (benne-content.ts): canviar de protagonista.
canviaBtn.onClick(() => switchProtagonist())
