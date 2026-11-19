// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
// La interfície tàctil: la targeta «Com es juga» (el dit o el ratolí), que s'obre des de les opcions. Què diu:
// narrative/controls.ts. L'art i el .gui.json: tactil/controls.py (des del hud.py de cada joc). Els textos fixos (títol,
// «D'acord», girar els botons) els posa el sync dels locales (`ui.controls.*`); els de les files, el script.
import { onUpdate } from '@benne/script';
import {
  gui, fons, dit0, dit1, dit2, ratoli0, ratoli1, ratoli2, text0, text1, text2, dacord, intercanvia, intercanviaText,
} from './controls.ids';
import { ambElDit, filesControls, tancaControls } from '../../narrative/controls';
import { preferencies, setPreferencia } from '../../narrative/preferencies';

const FONS_ALFA = 0.6

function omple() {
  const files = filesControls()
  const textos = [text0, text1, text2]
  for (let i = 0; i < textos.length; i++) textos[i]!.text = files[i] ?? ''
  intercanvia.checked = preferencies().esquerreFa
}

// (els controls amagats al .gui.json surten visibles en construir-se la GUI: per això es diu sempre què es veu)
function icones() {
  const dit = ambElDit()
  for (const c of [dit0, dit1, dit2]) if (c.visible !== dit) c.visible = dit
  for (const c of [ratoli0, ratoli1, ratoli2, intercanvia, intercanviaText]) if (c.visible === dit) c.visible = !dit
}

gui.onShow(() => {
  omple()
  icones()
})
gui.onBuilt(() => {
  omple()
  icones()
})
onUpdate(() => {
  if (!gui.visible) return
  if (fons.alpha !== FONS_ALFA) fons.alpha = FONS_ALFA
  icones()
})

// què fa cada botó del ratolí, aquí mateix: els textos ho diuen a l'acte
intercanvia.onChange((on: boolean) => {
  setPreferencia('esquerreFa', on)
  omple()
})
dacord.onClick(() => tancaControls())
