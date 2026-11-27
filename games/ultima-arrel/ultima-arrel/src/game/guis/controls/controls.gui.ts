// GENERAT per adapters/benne/sync.ts. No l'editis aquí.
// La interfície tàctil: la targeta «Com es juga» (el dit o el ratolí), que surt sola després de «Comença» i s'obre des
// de les opcions. Què diu i quan surt:
// narrative/controls.ts. L'art i el .gui.json: tactil/controls.py (des del hud.py de cada joc). Els textos fixos (títol,
// «D'acord», girar els botons) els posa el sync dels locales (`ui.controls.*`); els de les files, el script.
import { onUpdate } from '@benne/script';
import {
  gui, fons, dit0, dit1, dit2, dit3, dit4, ratoli0, ratoli1, ratoli2, ratoli3, ratoli4, text0, text1, text2, text3, text4,
  dacord, intercanvia, intercanviaText,
} from './controls.ids';
import { ambElDit, filaCanvia, filesControls, tancaControls, vigilaControls } from '../../narrative/controls';
import { preferencies, setPreferencia } from '../../narrative/preferencies';

const FONS_ALFA = 0.6

// La sisena fila (el canvi de protagonista) només hi és als jocs que passen la cara a controls.py: es busca per nom.
type Ctrl = { visible: boolean; text?: string }
const fila5 = (id: string) => (gui.controls as unknown as Record<string, Ctrl | undefined>)[id]

function omple() {
  const files = filesControls()
  const textos = [text0, text1, text2, text3, text4, fila5('text5')]
  for (let i = 0; i < textos.length; i++) {
    const t = textos[i]
    if (t && t.text !== (files[i] ?? '')) t.text = files[i] ?? ''
  }
  intercanvia.checked = preferencies().esquerreFa
}

// (els controls amagats al .gui.json surten visibles en construir-se la GUI: per això es diu sempre què es veu)
function icones() {
  const dit = ambElDit()
  for (const c of [dit0, dit1, dit2, dit3, dit4]) if (c.visible !== dit) c.visible = dit
  for (const c of [ratoli0, ratoli1, ratoli2, ratoli3, ratoli4, intercanvia, intercanviaText]) if (c.visible === dit) c.visible = !dit
  // la sisena fila, si el joc en té i diu alguna cosa
  const canvia = !!filaCanvia()
  const d5 = fila5('dit5'), r5 = fila5('ratoli5'), t5 = fila5('text5')
  if (d5 && d5.visible !== (canvia && dit)) d5.visible = canvia && dit
  if (r5 && r5.visible !== (canvia && !dit)) r5.visible = canvia && !dit
  if (t5 && t5.visible !== canvia) t5.visible = canvia
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
  vigilaControls()
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
