// La interfície tàctil: el menú d'accions (mantenir premut o clic dret sobre una cosa). El contingut el decideix
// narrative/tactil.script.ts (`openMenu`); aquí només es pinta al costat d'on s'ha premut. Art i .gui.json: el hud.py de cada joc.
import { game, onUpdate } from '@benne/script';
import {
  gui, fons, titol, accio0, accio1, accio2, accio3, accio4, accio5, text0, text1, text2, text3, text4, text5,
} from './accions.ids';
import { chooseOption, closeMenu } from '../../narrative/tactil.script';
import { isOpeningRelease, openMenu } from '../../narrative/tactil';

const botons = [accio0, accio1, accio2, accio3, accio4, accio5]
const textos = [text0, text1, text2, text3, text4, text5]
const KEY_W = 104
const KEY_H = 22
const GAP = 2
const FONS_ALFA = 0.35
const DIT = 26 // a quina distància del dit va el menú (que no quedi a sota)

for (let i = 0; i < botons.length; i++) {
  botons[i]!.onClick(() => {
    if (isOpeningRelease()) return
    chooseOption(i)
  })
}

fons.onClick(() => {
  if (isOpeningRelease()) return
  closeMenu()
})

function layout() {
  const m = openMenu()
  if (!m) return
  fons.alpha = FONS_ALFA
  const n = Math.min(m.opcions.length, botons.length)
  const alt = n * (KEY_H + GAP) - GAP
  const { width: W, height: H } = game.screenSize
  const p = { x: m.x, y: m.y }
  // Al costat del dit (a la dreta si hi cap; si no, a l'esquerra), centrat en vertical.
  const x = p.x + DIT + KEY_W <= W - 4 ? p.x + DIT : Math.max(4, p.x - DIT - KEY_W)
  const y = Math.round(Math.min(Math.max(p.y - alt / 2, 18), H - 4 - alt))
  titol.text = m.titol
  titol.x = Math.round(x + KEY_W / 2)
  titol.y = y - 12
  for (let i = 0; i < botons.length; i++) {
    const b = botons[i]!
    const t = textos[i]!
    const opcio = m.opcions[i]
    b.visible = t.visible = i < n && opcio !== undefined
    if (!opcio) continue
    b.x = Math.round(x)
    b.y = y + i * (KEY_H + GAP)
    t.text = opcio.text
    t.x = Math.round(x + KEY_W / 2)
    t.y = b.y + 7
  }
}

gui.onShow(() => layout())
gui.onBuilt(() => layout())
// El fons, mig transparent: en construir-se la GUI surt opac (com els controls amagats, que surten visibles).
onUpdate(() => {
  if (gui.visible && fons.alpha !== FONS_ALFA) fons.alpha = FONS_ALFA
})
