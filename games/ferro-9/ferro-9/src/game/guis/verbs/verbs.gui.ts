import { pointer } from '@benne/script';
import { guis, verbs } from '@game';
import {
  gui, closeBtn, giveBtn, lookAtBtn, menuBtn, openBtn, pickUpBtn, pullBtn, pushBtn, talkToBtn, useBtn, verbLineText, canviaBtn,
} from './verbs.ids';
import { switchProtagonist } from '../../narrative/narrative.script';
import { fromBenne, narrative } from '../../narrative/narrative';
import config from '../../game-config.json';

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
// The names carry their article («la porta», «el passadís»), so the line contracts the prepositions:
// «Ves a el passadís» → «Ves al passadís», «Ves a cap a la reixa» → «Ves cap a la reixa» (tasca 164).
const CONTRETS: Record<string, string> = {
  'a el': 'al', 'a els': 'als', 'de el': 'del', 'de els': 'dels', 'per el': 'pel', 'per els': 'pels',
}
function contreu(frase: string): string {
  return frase
    .replace(/(^|\s)(a|de|per) (els?) /g, (_, s: string, p: string, el: string) => `${s}${CONTRETS[`${p} ${el}`]} `)
    .replace(/(^|\s)a (cap a )/g, '$1$2')
}

// Sense verb triat, damunt d'un objecte de l'inventari no es camina cap enlloc: la frase diu el verb del clic dret
// («Mira el formulari 27-B»), el mateix que queda en groc a la graella (tasca 325).
const ETIQUETES = new Map(config.verbs.map((v) => [v.id, v.label]))
function frase(): string {
  const hover = pointer.hover
  const etiqueta = hover?.defaultVerb && ETIQUETES.get(hover.defaultVerb.id)
  if (!pointer.verb && !pointer.item && hover?.kind === 'item' && hover.description && etiqueta) {
    return `${etiqueta} ${hover.description}`
  }
  const sentence = pointer.sentence
  return ambArticle(sentence)
}

// Els personatges, amb l'article i en minúscula («Parla amb el Cargol», «Mira el capatàs Tul»): el seu nom és també
// el de qui parla, i per a la frase n'hi ha un altre (`ui.amb_article.<personatge>`; tasca 324).
function ambArticle(frase: string): string {
  const hover = pointer.hover
  if (hover?.kind !== 'character' || !hover.id || !hover.description || !frase.endsWith(hover.description)) return frase
  const clau = `ui.amb_article.${fromBenne('characters', hover.id)}`
  if (!narrative.i18n.has(clau)) return frase
  return frase.slice(0, -hover.description.length) + narrative.t(clau)
}

function refresh() {
  const text = frase()
  verbLineText.text = contreu(text)
  const armed = pointer.verb
  const highlighted = pointer.hover?.defaultVerb
  for (const [verb, button] of buttons) {
    button.visualState = verb === armed ? 'pressed' : verb === highlighted ? 'hover' : 'normal'
  }
}

gui.onBuilt(refresh)
pointer.onContextChange(refresh)

// Esc desfà el verb i l'objecte triats: «Usa el llapis amb» torna a «Camina cap a» (tasca 326).
if (typeof window !== 'undefined') {
  window.addEventListener('keydown', (ev) => {
    if (ev.key !== 'Escape' || (!pointer.verb && !pointer.item)) return
    pointer.item = null
    pointer.verb = null
  })
}

// Afegit per adapters/benne (benne-content.ts): canviar de protagonista.
canviaBtn.onClick(() => switchProtagonist())
