/**
 * Pont amb Benne, part seqüenciada (BenneScript): parlar, mostrar pistes, finals.
 * Les funcions exportades d'un `*.script.ts` són "step functions": cada línia
 * espera l'anterior, com als scripts de sala.
 *
 * Es copia a `src/game/narrative/` amb `npm run benne:sync`. No l'editis allà.
 */
import { display, fadeOut, player } from '@benne/script';
import type { DialogHandle } from '@benne/script';
import type { ResolvedChoice, ResolvedLine } from '@aventura/narrative-core';
import { benneCharacter, narrative } from './narrative';

/** Nom de l'opció de Benne per a una opció d'un node (el genera el sync). */
export const optionName = (node: string, choice: string) => `${node}__${choice}`;

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
