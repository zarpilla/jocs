import { game, settings } from '@benne/script';
import { guis } from '@game';
import { gui, back, musicEnabled, musicVolume, sfxVolume, textSpeedSlider, version } from './settings-menu.ids';

// The text speed slider runs from slow (0.1) to fast (2), the opposite way to the speech
// duration multiplier, so it maps across the same range.
const TEXT_SPEED_MIN = 0.1
const TEXT_SPEED_MAX = 2

gui.onBuilt(() => {
  version.text = `v${game.version}`
  sfxVolume.value = settings.sfxVolume * 100
  musicVolume.value = settings.musicVolume * 100
  textSpeedSlider.value = TEXT_SPEED_MIN + TEXT_SPEED_MAX - settings.textSpeed
})

sfxVolume.onChange((v: number) => {
  settings.sfxVolume = v / 100
})

musicVolume.onChange((v: number) => {
  settings.musicVolume = v / 100
})

textSpeedSlider.onChange((v: number) => {
  settings.textSpeed = TEXT_SPEED_MIN + TEXT_SPEED_MAX - v
})

// The checkbox is called "musicEnabled" in the GUI, but it switches click-to-skip.
musicEnabled.onChange((checked: boolean) => {
  settings.clickToSkip = checked
})

back.onClick(() => {
  gui.hide()
  guis.gameMenu.show()
})

// Afegit per adapters/benne/tactil (index.ts, opcionsTactils): què fa cada botó del ratolí (una preferència
// de cada joc i de cada aparell) i la targeta «Com es juga».
import { intercanvia, controls } from './settings-menu.ids'
import { mostraControls } from '../../narrative/controls'
import { preferencies, setPreferencia } from '../../narrative/preferencies'

gui.onShow(() => {
  intercanvia.checked = preferencies().esquerreMira
})

intercanvia.onChange((on: boolean) => {
  setPreferencia('esquerreMira', on)
})

controls.onClick(() => {
  gui.hide()
  mostraControls(true)
})
