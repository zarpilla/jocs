#!/usr/bin/env python3
"""
`npm run musica`: genera la música d'Aigua Verne a `game/audio/music/` (.ogg, estèreo).

Totes les peces són el mateix tema (Mi menor, 4/4, 100 negres per minut, 32 compassos, 76,8 s) amb
instruments diferents, per lloc. Un western de secada, però a l'espai:

- `tema`: portada i pròleg. Guitarra amb tremolo, sintetitzador, el tema xiulat amb eco, cascos de
  cavall, un theremin que passa, i la musiqueta d'anunci de Verne S.A. (massa contenta, en Do major).
- `terra2`: la granja i la secada. Vent amb pols, guitarra lenta rasguejada i el tema a l'harmònica.
- `nau`: la Cantimplora. Càlida: el motor de fons, contrabaix que camina, escombretes amb swing,
  piano elèctric i el tema al vibràfon.
- `aqua`: el fons de l'antic mar. Buit i salat: vent, onades llunyanes, campanes de boia i el tema a
  trossos, lluny, amb molt d'eco.
- `ferrum`: les mines de vaga. Percussió de ferro (enclusa, martells, bombo), baix obstinat i el tema
  al metall, decidit.
- `verdant`: la residència dels rics. Muzak d'ascensor massa alegre: bossa nova en Mi major, piano
  elèctric, vibràfon i flauta, i una cinta que desafina una mica (és tot de plàstic).
- `palau`: el palau orbital. Vals fred i elegant (3/4, quatre compassos per acord): piano i cordes.
- `tensio`: les sincronies. Un rellotge, un baix que batega, cordes en tremolo i el tema greu.
- `final`: plou. El tema en Mi major: guitarra, cordes, xiulet, harmònica i la pluja.

Com que tenen la mateixa durada, el joc les encadena al mateix punt (`sync`) en canviar de lloc.
Les peces són bucles perfectes: cada so que passa del final torna a sonar al principi, les
oscil·lacions lentes fan voltes senceres i la reverberació és circular. Tot sintetitzat, i sempre igual.

`python3 tools/musica.py tema nau` en fa només unes quantes.

Cal python3 amb numpy, i ffmpeg.
"""
import functools
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np

SR = 44100
OUT = Path(__file__).resolve().parent.parent / 'game' / 'audio' / 'music'


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def t(d):
    return np.arange(int(SR * d)) / SR


def env(d, attack, release, decay=None):
    """Atac i alliberament lineals; `decay` (s) afegeix una caiguda exponencial."""
    x = t(d)
    e = np.minimum(1, x / max(attack, 1e-4))
    if decay:
        e = e * np.exp(-x / decay)
    n = min(int(SR * release), len(e))
    if n:
        e[-n:] *= np.linspace(1, 0, n)
    return e


def osc(freq, d, shape='sine', phase=0.0):
    f = np.broadcast_to(np.asarray(freq, dtype=float), (int(SR * d),))
    ph = 2 * np.pi * np.cumsum(f) / SR + phase
    if shape == 'sine':
        return np.sin(ph)
    if shape == 'saw':
        # Serra suavitzada: els harmònics aguts, sense aliàsing.
        return sum(np.sin(k * ph) / k for k in range(1, 12)) * (2 / np.pi)
    if shape == 'square':
        return sum(np.sin(k * ph) / k for k in range(1, 12, 2)) * (4 / np.pi)
    raise ValueError(shape)


def band(x, lo=None, hi=None):
    """Filtre amb la FFT (circular: el que surt pel final entra pel principi)."""
    spec = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    mask = np.ones_like(f)
    if lo:
        mask *= 1 / (1 + (lo / np.maximum(f, 1)) ** 4)
    if hi:
        mask *= 1 / (1 + (f / hi) ** 4)
    return np.fft.irfft(spec * mask, len(x))


def ressonancia(x, centre, amplada):
    """Banda estreta al voltant de `centre` (Hz): el xiulet del vent."""
    spec = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    return np.fft.irfft(spec * np.exp(-((f - centre) / amplada) ** 2), len(x))


class Pista:
    """Un bucle estèreo de `durada` segons. Tot el que s'hi posa dona la volta pel final."""

    def __init__(self, durada):
        self.n = int(round(SR * durada))
        self.durada = self.n / SR
        self.lr = np.zeros((2, self.n))

    def posa(self, x, inici, pan=0.0, vol=1.0):
        """`pan` de -1 (esquerra) a 1 (dreta)."""
        a = (pan + 1) * np.pi / 4
        x = x[: self.n] * vol
        i = int(round(SR * inici)) % self.n
        for ch, g in enumerate((np.cos(a), np.sin(a))):
            primer = min(len(x), self.n - i)
            self.lr[ch, i:i + primer] += g * x[:primer]
            if primer < len(x):
                self.lr[ch, : len(x) - primer] += g * x[primer:]

    def continu(self, x, pan=0.0, vol=1.0):
        """Un so que dura tot el bucle (ha de tancar bé: voltes senceres o filtrat amb la FFT)."""
        self.posa(x, 0, pan=pan, vol=vol)

    def lfo(self, voltes, fase=0.0):
        """Oscil·lació de 0 a 1 que fa exactament `voltes` voltes en tot el bucle."""
        return 0.5 + 0.5 * np.sin(2 * np.pi * voltes * np.arange(self.n) / self.n + fase)

    def sinus(self, freq, fase=0.0):
        """Sinusoide contínua, amb la freqüència arrodonida perquè faci voltes senceres."""
        voltes = max(1, round(freq * self.durada))
        return np.sin(2 * np.pi * voltes * np.arange(self.n) / self.n + fase)

    def soroll(self, rng):
        return rng.uniform(-1, 1, self.n)


def reverb(lr, durada, cua, humit, rng, fosc=4000):
    """Reverberació circular (convolució amb la FFT): la cua del final cau al principi del bucle."""
    n = lr.shape[1]
    out = np.empty_like(lr)
    for ch in range(2):
        m = int(SR * cua)
        ir = rng.uniform(-1, 1, m) * np.exp(-np.arange(m) / (SR * durada))
        ir[: int(SR * 0.02)] = 0  # predelay
        ir = band(ir, 120, fosc)
        ir /= np.sqrt(np.sum(ir ** 2))
        k = np.zeros(n)
        k[:m] = ir
        mullat = np.fft.irfft(np.fft.rfft(lr[ch]) * np.fft.rfft(k), n)
        out[ch] = lr[ch] + humit * mullat
    return out


def molla(lr, temps, cops, caiguda):
    """Eco de molla de guitarra de western: el so repetit cada `temps` segons, cada cop més fluix i fosc
    (circular, com la reverberació)."""
    n = lr.shape[1]
    k = np.zeros(n)
    for i in range(1, cops + 1):
        k[int(SR * temps * i) % n] += caiguda ** i
    out = np.empty_like(lr)
    for ch in range(2):
        eco = np.fft.irfft(np.fft.rfft(lr[ch]) * np.fft.rfft(k), n)
        out[ch] = lr[ch] + band(eco, 200, 3000)
    return out


# ─── El tema d'Aigua Verne ───────────────────────────────────────────────────
#
# 4/4, 100 negres per minut. Un acord cada dos compassos; les posicions van en corxeres (0-7).

PPM = 100
TEMPS = 60 / PPM          # una negra
CORXERA = TEMPS / 2
COMPAS = 4 * TEMPS

# Mi menor: baix + veus (notes MIDI). 16 acords, 32 compassos, 76,8 s.
ACORDS = [
    (40, [55, 59, 64, 67]),  # Mi m
    (36, [55, 60, 64, 67]),  # Do
    (38, [54, 57, 62, 66]),  # Re
    (35, [54, 59, 63, 69]),  # Si 7
    (40, [55, 59, 64, 67]),  # Mi m
    (43, [55, 59, 62, 67]),  # Sol
    (45, [57, 60, 64, 69]),  # La m
    (35, [54, 59, 63, 69]),  # Si 7
    (36, [55, 60, 64, 67]),  # Do
    (43, [55, 59, 62, 67]),  # Sol
    (38, [54, 57, 62, 66]),  # Re
    (40, [55, 59, 64, 67]),  # Mi m
    (45, [57, 60, 64, 69]),  # La m
    (40, [55, 59, 64, 67]),  # Mi m
    (36, [55, 59, 64, 67]),  # Do maj7 (la musiqueta del Magnat, al tema)
    (35, [54, 57, 63, 66]),  # Si 7: torna a començar
]

# El mateix, en Mi major (Verdant, que fa veure que tot va bé, i el final, quan plou de debò).
ACORDS_MAJOR = [
    (40, [56, 59, 64, 68]),  # Mi
    (37, [56, 61, 64, 68]),  # Do♯ m
    (35, [54, 57, 61, 66]),  # Si 9 sus
    (35, [54, 59, 63, 69]),  # Si 7
    (40, [56, 59, 64, 68]),  # Mi
    (44, [56, 59, 63, 68]),  # Sol♯ m
    (45, [57, 61, 64, 69]),  # La
    (35, [54, 59, 63, 69]),  # Si 7
    (33, [56, 61, 64, 69]),  # La maj7
    (44, [56, 59, 64, 68]),  # Mi/Sol♯
    (35, [54, 57, 63, 66]),  # Si 7
    (40, [56, 59, 64, 68]),  # Mi
    (45, [57, 61, 64, 69]),  # La
    (40, [56, 59, 64, 68]),  # Mi
    (37, [56, 59, 64, 68]),  # Do♯ m7
    (35, [54, 57, 63, 66]),  # Si 7
]
COMPASSOS = 2 * len(ACORDS)
DURADA = COMPASSOS * COMPAS

# (compàs, corxera, nota, durada en corxeres). Tres frases; els darrers 8 compassos, sense melodia.
MELODIA = [
    # Primera: el salt de western (Mi, Si, Mi amunt) i la resposta que cau.
    (0, 0, 64, 1), (0, 1, 71, 1), (0, 2, 76, 4), (0, 6, 74, 1), (0, 7, 71, 1), (1, 0, 76, 6),
    (2, 0, 72, 1), (2, 1, 71, 1), (2, 2, 67, 4), (2, 6, 72, 1), (2, 7, 71, 1), (3, 0, 67, 2), (3, 2, 64, 5),
    (4, 0, 66, 1), (4, 1, 69, 1), (4, 2, 74, 4), (4, 6, 72, 1), (4, 7, 71, 1), (5, 0, 69, 6),
    (6, 0, 71, 2), (6, 2, 75, 2), (6, 4, 78, 4), (7, 0, 75, 2), (7, 2, 71, 5),
    # Segona: el mateix salt, i se'n va amunt.
    (8, 0, 64, 1), (8, 1, 71, 1), (8, 2, 76, 4), (8, 6, 74, 1), (8, 7, 71, 1), (9, 0, 76, 6),
    (10, 0, 74, 1), (10, 1, 76, 1), (10, 2, 79, 4), (10, 6, 78, 1), (10, 7, 74, 1), (11, 0, 71, 6),
    (12, 0, 72, 2), (12, 2, 76, 2), (12, 4, 81, 4), (13, 0, 79, 2), (13, 2, 76, 5),
    (14, 0, 78, 2), (14, 2, 75, 2), (14, 4, 71, 4), (15, 0, 69, 2), (15, 2, 71, 5),
    # Tercera: llarga, amb set, i torna a casa.
    (16, 0, 79, 4), (16, 4, 76, 2), (16, 6, 72, 2), (17, 0, 76, 7),
    (18, 0, 74, 4), (18, 4, 71, 2), (18, 6, 67, 2), (19, 0, 71, 7),
    (20, 0, 69, 2), (20, 2, 74, 2), (20, 4, 78, 2), (20, 6, 81, 2), (21, 0, 78, 4), (21, 4, 74, 3),
    (22, 0, 76, 6), (22, 6, 71, 1), (22, 7, 74, 1), (23, 0, 76, 7),
]

# En major: Sol → Sol♯, Do → Do♯, Re → Re♯.
A_MAJOR = {7: 1, 0: 1, 2: 1}

# La musiqueta de l'anunci de Verne S.A. (compassos 28-29, sobre el Do maj7): «Ai-gua Ver-ne!» i el «ding».
JINGLE = [(28, 0, 79, 1), (28, 1, 84, 1), (28, 2, 88, 2), (28, 4, 86, 1), (28, 5, 88, 1), (28, 6, 91, 2)]


def acord(c, major=False):
    """L'acord que sona al compàs `c`."""
    acords = ACORDS_MAJOR if major else ACORDS
    return acords[(c // 2) % len(acords)]


def quan(c, e, swing=False):
    """Segons del compàs `c`, corxera `e`. Amb `swing`, les corxeres del darrere arriben tard."""
    if swing and int(e) % 2 == 1:
        e = e + 0.33
    return (c * 8 + e) * CORXERA


def notes(major=False, frases=(0, 1, 2)):
    """La melodia, en major si cal, només de les frases que es demanen."""
    for c, e, nota, dur in MELODIA:
        if c // 8 in frases:
            if major:
                nota += A_MAJOR.get(nota % 12, 0)
            yield c, e, nota, dur


def melodia(p, instrument, pan=0.0, vol=0.2, octava=0, eco=0.0, major=False, swing=False, frases=(0, 1, 2), legato=0.5):
    for c, e, nota, dur in notes(major, frases):
        d = dur * CORXERA + legato
        x = instrument(midi(nota + 12 * octava), d)
        p.posa(x, quan(c, e, swing), pan=pan, vol=vol)
        if eco:
            # Eco a negra amb punt, a l'altre costat.
            p.posa(x, quan(c, e, swing) + 3 * CORXERA, pan=-pan, vol=vol * eco)


# ─── Instruments ─────────────────────────────────────────────────────────────

def xiulet(f, d, vibrat=0.006):
    """Xiulet de western: gairebé una sinusoide, amb alè i un vibrato que arriba tard."""
    x = t(d)
    vib = 1 + vibrat * np.sin(2 * np.pi * 5.5 * x) * np.minimum(1, x / 0.4)
    so = osc(f * vib, d) + 0.08 * osc(2 * f * vib, d)
    ale = band(np.random.default_rng(int(f)).uniform(-1, 1, len(x)), f * 0.8, f * 3) * 0.07
    return (so + ale) * env(d, 0.04, 0.25)


def theremin(f, d):
    """El theremin de l'espai: entra lliscant des de sota, amb un vibrato ample."""
    x = t(d)
    llisca = 2 ** (-(7 / 12) * np.exp(-x / 0.12))
    vib = 1 + 0.015 * np.sin(2 * np.pi * 6.2 * x)
    return (osc(f * llisca * vib, d) + 0.15 * osc(2 * f * llisca * vib, d)) * env(d, 0.15, 0.6)


@functools.lru_cache(maxsize=None)
def _corda(nota, d, brillo):
    """Corda puntejada (Karplus-Strong): un pols de soroll que es repeteix i s'apaga."""
    f = midi(nota)
    N = max(2, int(round(SR / f - 0.5)))
    total = int(SR * d)
    rng = np.random.default_rng(nota * 7 + int(brillo * 10))
    pols = rng.uniform(-1, 1, N + 1)
    # Com més fosc, més suau el pols (menys harmònics aguts).
    for _ in range(int((1 - brillo) * 6)):
        pols = 0.5 * (pols + np.roll(pols, 1))
    out = np.zeros(total + N + 1)
    out[: N + 1] = pols
    i = N + 1
    perdua = 0.996 if f < 200 else 0.993
    while i < len(out):
        k = min(N, len(out) - i)
        out[i:i + k] = perdua * 0.5 * (out[i - N:i - N + k] + out[i - N - 1:i - N - 1 + k])
        i += k
    out = out[N + 1:]
    out = out - np.mean(out)
    return out


def guitarra(f, d, brillo=0.6):
    nota = int(round(69 + 12 * np.log2(f / 440)))
    # (×3,5: el pols de Karplus-Strong surt fluix al costat dels altres instruments)
    return 3.5 * _corda(nota, round(d, 2), brillo)[: int(SR * d)] * env(d, 0.002, 0.08)


def guitarra_tremolo(f, d, rapid=2 / CORXERA):
    """Guitarra amb el tremolo de l'amplificador (dues pulsacions per corxera)."""
    x = t(d)
    return guitarra(f, d, 0.7) * (0.55 + 0.45 * np.sin(2 * np.pi * rapid * x))


def rasgueig(p, veus, inici, vol, pan=0.0, avall=True, d=2.0):
    """Un acord de guitarra rasguejat: les cordes, una darrere l'altra."""
    ordre = veus if avall else veus[::-1]
    for j, v in enumerate(ordre):
        p.posa(guitarra(midi(v), d, 0.5), inici + 0.018 * j, pan=pan, vol=vol * (1 - 0.08 * j))


def harmonica(f, d):
    """Harmònica: dues llengüetes una mica desafinades, l'alè i un vibrato de mà."""
    x = t(d)
    vib = 1 + 0.004 * np.sin(2 * np.pi * 4.8 * x) * np.minimum(1, x / 0.5)
    mà = 0.85 + 0.15 * np.sin(2 * np.pi * 4.8 * x + 1)
    so = (osc(f * vib * 2 ** (6 / 1200), d, 'square') + osc(f * vib * 2 ** (-6 / 1200), d, 'saw')) / 2
    so = band(so, 400, 3200)
    ale = band(np.random.default_rng(int(f) + 3).uniform(-1, 1, len(x)), 1000, 5000) * 0.05
    return 2 * (so + ale) * mà * env(d, 0.06, 0.2)


def metall_lead(f, d):
    """Un metall de banda de mina: serra filtrada, atac decidit."""
    x = t(d)
    vib = 1 + 0.003 * np.sin(2 * np.pi * 5 * x) * np.minimum(1, x / 0.5)
    obre = 0.6 + 0.4 * np.minimum(1, x / 0.15)
    return band(osc(f * vib, d, 'saw'), 180, 2200) * obre * env(d, 0.03, 0.15)


def pad(f, d, rng):
    """Tres sinusoides gairebé a l'uníson i l'octava fluixa."""
    x = sum(osc(f * 2 ** (c / 1200), d, phase=rng.uniform(0, 6.28)) for c in (-6, 0, 6)) / 3
    return x + 0.08 * osc(f * 2, d)


def cordes(f, d, rng):
    """Cordes sintètiques: el pad amb una mica de serra filtrada."""
    return 0.7 * pad(f, d, rng) + 0.3 * band(osc(f, d, 'saw'), 200, 1800)


def sinte(f, d, rng):
    """El sintetitzador de l'espai: serres desafinades, fosques."""
    x = sum(osc(f * 2 ** (c / 1200), d, 'saw', phase=rng.uniform(0, 6.28)) for c in (-9, 0, 9)) / 3
    return band(x, 120, 1400)


def rhodes(f, d):
    """Piano elèctric: la vareta (sinusoide i l'octava) i el cop metàl·lic que s'apaga de seguida."""
    so = osc(f, d) + 0.25 * osc(2 * f, d) * env(d, 0.002, 0.05, 0.4)
    cop = 0.15 * osc(f * 7.1, d) * env(d, 0.001, 0.02, 0.05)
    return (so + cop) * env(d, 0.004, 0.15, 1.6)


def vibrafon(f, d):
    """Vibràfon: barra de metall (fonamental i 4a harmònica) amb el ventilador que fa ondular el so."""
    x = t(d)
    so = osc(f, d) + 0.2 * osc(4 * f, d) * np.exp(-x / 0.3)
    return so * (0.75 + 0.25 * np.sin(2 * np.pi * 5.5 * x)) * env(d, 0.002, 0.15, 1.4)


def piano(f, d):
    """Piano: harmònics una mica desafinats cap amunt, que s'apaguen de pressa els aguts."""
    x = t(d)
    so = np.zeros(len(x))
    caiguda = 1.6 * (261 / f) ** 0.4
    for k in range(1, 9):
        fk = f * k * np.sqrt(1 + 0.0004 * k * k)
        if fk > 12000:
            break
        so += osc(fk, d) * np.exp(-x * k ** 0.6 / caiguda) / k ** 1.3
    return so * env(d, 0.002, 0.15)


def baix(f, d):
    return (osc(f, d) + 0.25 * osc(f * 2, d)) * env(d, 0.01, 0.12)


def contrabaix(f, d):
    """Contrabaix puntejat: cop i cos, que s'apaga."""
    return band(osc(f, d) + 0.4 * osc(2 * f, d) + 0.1 * osc(3 * f, d), 30, 900) * env(d, 0.006, 0.1, 0.5)


def bombo(rng, fort=True):
    """Pell greu que cau de to i un fregament."""
    d = 0.4
    x = t(d)
    f = 55 + 60 * np.exp(-x / 0.025)
    pell = osc(f, d) * env(d, 0.002, 0.05, 0.16 if fort else 0.07)
    return pell + 0.12 * band(rng.uniform(-1, 1, len(x)), 400, 3000) * env(d, 0.001, 0.05, 0.02)


def escombreta(rng, d=0.25):
    """Escombretes sobre la caixa: un fregament."""
    return band(rng.uniform(-1, 1, int(SR * d)), 1500, 8000) * env(d, 0.01, 0.05, d / 3)


def plat(rng, d=0.5):
    """El plat de ride, molt fluix."""
    x = band(rng.uniform(-1, 1, int(SR * d)), 5000, 12000) + 0.3 * osc(3800, d)
    return x * env(d, 0.001, 0.05, 0.18)


def cascavell(rng):
    """Maraca o grava: un gra de soroll aspre i curt."""
    d = 0.08
    return band(rng.uniform(-1, 1, int(SR * d)), 3000, 10000) * env(d, 0.003, 0.02, 0.025)


def fusta(f, d=0.15):
    """Bloc de fusta (cascos de cavall, el rellotge): to curt i sec."""
    return (osc(f, d) + 0.4 * osc(f * 2.7, d)) * env(d, 0.001, 0.02, 0.03)


def campana(f, d=4.0):
    """Campana (la boia, o un vidre): parcials inharmònics que s'apaguen a ritmes diferents."""
    parcials = ((0.5, 0.3, 2.5), (1, 1, 1.8), (1.19, 0.4, 1.2), (1.56, 0.3, 0.9), (2.0, 0.35, 1.0), (2.51, 0.2, 0.6), (3.01, 0.15, 0.4))
    return sum(a * osc(f * r, d) * env(d, 0.002, 0.2, dec) for r, a, dec in parcials) / 2


def metall(rng, f, d=1.2):
    """Un cop a una enclusa o un tub: metall inharmònic i un clic."""
    so = sum(a * osc(f * r, d) * env(d, 0.001, 0.1, dec) for r, a, dec in ((1, 1, 0.5), (2.76, 0.5, 0.3), (5.4, 0.3, 0.15), (8.93, 0.2, 0.08)))
    clic = band(rng.uniform(-1, 1, int(SR * d)), 1500) * env(d, 0.0005, 0.05, 0.01)
    return so + 0.5 * clic


def bip(f, d=0.25):
    """Puntet electrònic: sinusoide neta i curta."""
    return (osc(f, d) + 0.2 * osc(f * 3, d)) * env(d, 0.003, 0.05, 0.08)


# ─── Ambients que duren tot el bucle ─────────────────────────────────────────

def onades(p, rng, vol, pan=0.4):
    """Onades llunyanes: soroll greu que puja i baixa, dues capes de ritmes diferents."""
    for voltes, fase, costat in ((11, 0.0, -pan), (7, 2.0, pan)):
        x = band(p.soroll(rng), 80, 900)
        ona = p.lfo(voltes, fase) ** 3
        p.continu(x * (0.15 + ona), pan=costat, vol=vol)


def vent(p, rng, vol, xiula=True, fosc=1500):
    """El vent: un fregament ample i, a sobre, bandes estretes que s'encenen i s'apaguen (el xiulet)."""
    for ch, pan in ((0, -0.7), (1, 0.7)):
        base = band(p.soroll(rng), 150, fosc) * (0.5 + 0.5 * p.lfo(5, ch * 1.3))
        p.continu(base, pan=pan, vol=vol)
    if xiula:
        for k, (centre, voltes) in enumerate(((420, 3), (610, 4), (880, 6), (1250, 5))):
            x = ressonancia(p.soroll(rng), centre, centre * 0.03)
            x /= np.sqrt(np.mean(x ** 2))
            p.continu(x * p.lfo(voltes, k * 1.7) ** 4, pan=-0.6 + 0.4 * k, vol=vol * 0.25)


def pluja(p, rng, vol):
    """La pluja: un xiuxiueig ample i gotes soltes que piquen a tot arreu."""
    for pan in (-0.6, 0.6):
        p.continu(band(p.soroll(rng), 600, 7000) * (0.8 + 0.2 * p.lfo(3, pan)), pan=pan, vol=vol)
    gota = lambda: band(rng.uniform(-1, 1, int(SR * 0.03)), 2000, 9000) * env(0.03, 0.001, 0.01, 0.006)
    for _ in range(int(p.durada * 25)):
        p.posa(gota(), rng.uniform(0, p.durada), pan=rng.uniform(-0.9, 0.9), vol=vol * rng.uniform(0.5, 2.0))


# ─── Peces que comparteixen ──────────────────────────────────────────────────

def acords_llargs(p, rng, so, vol, pan=0.5, major=False, atac=2.0):
    acords = ACORDS_MAJOR if major else ACORDS
    for i, (b, veus) in enumerate(acords):
        d = 2 * COMPAS + 3
        for j, v in enumerate(veus):
            p.posa(so(midi(v), d, rng) * env(d, atac, 3.0), 2 * i * COMPAS, pan=-pan + 2 * pan * j / 3, vol=vol)


def bordo(p, vol, major=False, octava=0):
    """El baix de cada acord, llarg."""
    acords = ACORDS_MAJOR if major else ACORDS
    for i, (b, _) in enumerate(acords):
        d = 2 * COMPAS + 2
        p.posa(osc(midi(b + 12 * octava), d) * env(d, 1.0, 2.5), 2 * i * COMPAS, vol=vol)


def cascos(p, rng, vol, des_de=0, fins=COMPASSOS):
    """Un cavall al trot: «ta-ca-toc» a cada temps."""
    for c in range(des_de, fins):
        for temps in range(4):
            e = 2 * temps
            p.posa(fusta(900), quan(c, e), pan=-0.3, vol=vol)
            p.posa(fusta(700), quan(c, e + 0.6), pan=-0.3, vol=vol * 0.6)
            p.posa(fusta(780), quan(c, e + 1), pan=-0.3, vol=vol * 0.8)


# ─── Les peces ───────────────────────────────────────────────────────────────

def tema():
    """Portada i pròleg: guitarra amb tremolo, sintetitzador, el tema xiulat, i l'anunci del Magnat."""
    rng = np.random.default_rng(1)
    p = Pista(DURADA)
    acords_llargs(p, rng, sinte, 0.05, pan=0.6)
    bordo(p, 0.2)
    for c in range(COMPASSOS):
        b, veus = acord(c)
        # Guitarra amb tremolo: arpegi a negres (fonamental, quinta, veus).
        arpegi = [b + 12, veus[1], veus[2], veus[3]] if c % 2 == 0 else [veus[2], veus[1], veus[3], veus[2]]
        for k, nota in enumerate(arpegi):
            p.posa(guitarra_tremolo(midi(nota), 1.4), quan(c, 2 * k), pan=-0.4, vol=0.1 if k else 0.13)
    melodia(p, xiulet, pan=0.2, vol=0.15, eco=0.3)
    # Cascos de cavall llunyans a la segona frase; el theremin que passa a la primera i a la tercera.
    cascos(p, rng, 0.03, 8, 16)
    for c in (2, 18):
        p.posa(theremin(midi(acord(c)[1][-1] + 12), 3.0), quan(c, 4), pan=0.7, vol=0.05)
    # Compassos 24-27: la guitarra sola respon amb la primera frase, greu.
    for c, e, nota, dur in MELODIA:
        if c < 4:
            p.posa(guitarra(midi(nota - 12), dur * CORXERA + 0.8, 0.8), quan(c + 24, e), pan=0.35, vol=0.13)
    # Compassos 28-29: «Aigua Verne. Perquè la set no espera.» La musiqueta d'anunci, massa contenta.
    for c, e, nota, dur in JINGLE:
        p.posa(vibrafon(midi(nota), dur * CORXERA + 0.8), quan(c, e), pan=0.1, vol=0.11)
        p.posa(xiulet(midi(nota), dur * CORXERA + 0.2, 0.002), quan(c, e), pan=0.1, vol=0.05)
    for nota in (72, 76, 79, 84):  # el «ding» del logotip
        p.posa(campana(midi(nota + 12), 3.0), quan(29, 0), pan=-0.1, vol=0.04)
    for e in (1, 3, 5):  # pizzicato de banda de jingle
        for nota in (60, 64, 67):
            p.posa(rhodes(midi(nota), 0.3), quan(28, e), pan=0.4, vol=0.03)
    lr = molla(p.lr, 3 * CORXERA, 3, 0.25)
    return reverb(lr, durada=1.6, cua=5.0, humit=0.5, rng=rng, fosc=5000)


def terra2():
    """La secada: vent amb pols, guitarra lenta rasguejada i el tema a l'harmònica."""
    rng = np.random.default_rng(2)
    p = Pista(DURADA)
    vent(p, rng, 0.06, fosc=2500)
    bordo(p, 0.16)
    acords_llargs(p, rng, pad, 0.025, pan=0.7, atac=3.0)
    for c in range(COMPASSOS):
        b, veus = acord(c)
        # La guitarra: el baix al primer temps i un rasgueig lent al tercer; amunt al quart, de tant en tant.
        p.posa(guitarra(midi(b + 12), 2.4, 0.5), quan(c, 0), pan=-0.3, vol=0.16)
        rasgueig(p, veus, quan(c, 4), 0.07, pan=-0.3)
        if c % 2 == 1:
            rasgueig(p, veus[1:], quan(c, 6), 0.04, pan=-0.3, avall=False, d=1.2)
    melodia(p, harmonica, pan=0.2, vol=0.1, frases=(0, 2), legato=0.3)
    # La segona frase, a la guitarra (que l'harmònica respira).
    for c, e, nota, dur in notes(frases=(1,)):
        p.posa(guitarra(midi(nota), dur * CORXERA + 1.0, 0.7), quan(c, e), pan=0.3, vol=0.12)
    # Compassos 24-31: l'harmònica, sola i baixeta, amb un bordó de queixa.
    for c in (24, 28):
        b, veus = acord(c)
        d = 2 * COMPAS
        p.posa(harmonica(midi(veus[-1]), d) * env(d, 1.0, 1.5), quan(c, 0), pan=0.3, vol=0.04)
    return reverb(p.lr, durada=1.2, cua=4.0, humit=0.35, rng=rng, fosc=3500)


def nau():
    """La Cantimplora: motor de fons, contrabaix que camina, escombretes amb swing i el vibràfon."""
    rng = np.random.default_rng(3)
    p = Pista(DURADA)
    # El motor de la nau: un brunzit càlid en Mi, que respira a ritme de bucle.
    p.continu((p.sinus(midi(28)) + 0.4 * p.sinus(midi(40), 1.0)) * (0.8 + 0.2 * p.lfo(8)), vol=0.06)
    p.continu(band(p.soroll(rng), 40, 300), vol=0.04)
    for c in range(COMPASSOS):
        b, veus = acord(c)
        seg = acord(c + 1)[0]
        # Contrabaix que camina: fonamental, tercera o quinta, i una nota d'aproximació al compàs que ve.
        quinta, octava = b + 7, b + 12
        if c % 2 == 0:
            passos = [b, quinta, octava, quinta]
        else:
            # Cap a la fonamental de l'acord que ve, des d'un semitò per sobre o per sota.
            aprox = seg + (1 if seg < b else -1)
            passos = [octava, quinta, b + 4 if (b + 4) % 12 in [v % 12 for v in veus] else b + 3, aprox]
        for k, nota in enumerate(passos):
            p.posa(contrabaix(midi(nota), TEMPS * 0.95), quan(c, 2 * k), vol=0.24)
        # Bateria amb escombretes: fregament al 2 i al 4, ride amb swing.
        for e in (2, 6):
            p.posa(escombreta(rng), quan(c, e), pan=0.3, vol=0.06)
        for e in (0, 2, 3, 4, 6, 7):
            p.posa(plat(rng), quan(c, e, swing=True), pan=0.5, vol=0.03 if e % 2 == 0 else 0.018)
        # Piano elèctric: l'acord, a contratemps.
        for e in ((3, 6) if c % 2 == 0 else (1, 5)):
            for j, v in enumerate(veus):
                p.posa(rhodes(midi(v), 0.8), quan(c, e, swing=True) + 0.006 * j, pan=-0.35, vol=0.035)
    melodia(p, vibrafon, pan=0.25, vol=0.12, swing=True)
    # Compassos 24-31: la Vet xiula la primera frase, sense pressa.
    for c, e, nota, dur in notes(frases=(0,)):
        p.posa(xiulet(midi(nota), dur * CORXERA + 0.4), quan(c + 24, e, swing=True), pan=0.1, vol=0.07)
    lr = reverb(p.lr, durada=0.6, cua=2.0, humit=0.3, rng=rng, fosc=3500)
    # Càlid: sense aguts.
    return np.stack([band(ch, 30, 6000) for ch in lr])


def aqua():
    """El fons de l'antic mar: vent salat, buit, campanes de boia i el tema a trossos, lluny."""
    rng = np.random.default_rng(4)
    p = Pista(DURADA)
    vent(p, rng, 0.07)
    onades(p, rng, 0.12, pan=0.6)
    acords_llargs(p, rng, pad, 0.04, pan=0.8, atac=3.5)
    bordo(p, 0.1)
    # Les boies: dues campanes, una a cada banda, que sonen quan el vent les mou.
    for k in range(12):
        c = int(k * COMPASSOS / 12) + int(rng.integers(0, 2))
        nota, pan = (64, 0.6) if k % 2 else (71, -0.6)
        p.posa(campana(midi(nota), 5.0), quan(c, int(rng.integers(0, 8))), pan=pan, vol=0.04)
    # Vidres: les notes de l'acord, molt amunt, una per compàs.
    for c in range(COMPASSOS):
        _, veus = acord(c)
        p.posa(campana(midi(veus[(c * 3) % 4] + 24), 3.0), quan(c, 5), pan=rng.uniform(-0.5, 0.5), vol=0.012)
    # El tema, només la primera i la tercera frase, lluny i esmorteït, amb un eco que no s'acaba.
    def lluny(f, d):
        return band(xiulet(f, d), 300, 2200)
    melodia(p, lluny, pan=-0.2, vol=0.12, eco=0.45, frases=(0, 2))
    lr = molla(p.lr, 4 * CORXERA, 4, 0.4)
    return reverb(lr, durada=2.6, cua=7.0, humit=0.6, rng=rng, fosc=3500)


def ferrum():
    """Les mines de vaga: enclusa, martells, bombo, baix obstinat i el tema al metall, decidit."""
    rng = np.random.default_rng(5)
    p = Pista(DURADA)
    acords_llargs(p, rng, cordes, 0.035, pan=0.4, atac=1.5)
    for c in range(COMPASSOS):
        b, veus = acord(c)
        # Baix obstinat a corxeres: 3 + 3 + 2, com qui pica pedra.
        for e in range(8):
            nota = b + (12 if e in (3, 6) else 0)
            p.posa(baix(midi(nota), CORXERA * 0.8), quan(c, e), vol=0.2 if e in (0, 3, 6) else 0.11)
        # L'enclusa als accents; un martell més greu a contratemps.
        for e in (0, 3, 6):
            p.posa(metall(rng, 1046 if e == 0 else 880, 0.9), quan(c, e), pan=-0.45, vol=0.05 if e == 0 else 0.035)
        p.posa(metall(rng, 330, 0.7), quan(c, 5), pan=0.5, vol=0.03)
        # El bombo, com un pas pesant, i grava que cau.
        for e in (0, 4):
            p.posa(bombo(rng), quan(c, e), vol=0.32)
        if c % 4 == 3:
            p.posa(bombo(rng, False), quan(c, 7), vol=0.18)
        for e in range(8):
            p.posa(cascavell(rng), quan(c, e + 0.5), pan=0.3, vol=0.02)
    melodia(p, metall_lead, pan=0.15, vol=0.11, octava=-1, legato=0.2)
    # Compassos 24-31: tothom canta la primera frase, a l'uníson, sense paraules (un cor de vaga).
    for c, e, nota, dur in notes(frases=(0,)):
        d = dur * CORXERA + 0.3
        p.posa(band(cordes(midi(nota - 12), d, rng), 150, 1500) * env(d, 0.08, 0.2), quan(c + 24, e), pan=-0.1, vol=0.12)
    lr = reverb(p.lr, durada=0.9, cua=3.0, humit=0.35, rng=rng, fosc=3000)
    return np.stack([band(ch, 30, 7000) for ch in lr])


def verdant():
    """Muzak d'ascensor de la residència de Verne: bossa nova en major, massa alegre, de plàstic."""
    rng = np.random.default_rng(6)
    p = Pista(DURADA)
    for c in range(COMPASSOS):
        b, veus = acord(c, major=True)
        # Baix de bossa: fonamental i quinta, amb punt.
        for e, nota in ((0, b), (3, b + 7), (4, b), (7, b + 7)):
            p.posa(contrabaix(midi(nota), CORXERA * 2.5), quan(c, e), vol=0.2 if e in (0, 4) else 0.13)
        # Clau de bossa al canyís, i un shaker a semicorxeres.
        clau = (0, 3, 6) if c % 2 == 0 else (2, 4)
        for e in clau:
            p.posa(fusta(1700, 0.08), quan(c, e), pan=0.4, vol=0.04)
        for k in range(16):
            p.posa(cascavell(rng), quan(c, k / 2), pan=-0.4, vol=0.02 if k % 2 else 0.03)
        # Piano elèctric sincopat.
        for e in ((0, 3, 5) if c % 2 == 0 else (2, 5)):
            for j, v in enumerate(veus):
                p.posa(rhodes(midi(v + 12), 0.5), quan(c, e) + 0.004 * j, pan=-0.3, vol=0.03)
    acords_llargs(p, rng, pad, 0.03, pan=0.6, major=True, atac=1.0)
    # El tema al vibràfon i a la flauta, una octava amunt: somriu massa.
    melodia(p, vibrafon, pan=0.2, vol=0.1, major=True)
    melodia(p, lambda f, d: xiulet(f, d, 0.003), pan=-0.1, vol=0.05, octava=1, major=True)
    # Compassos 24-31: el «ding-dong» de la residència, i un altre cop la primera frase, al vibràfon sol.
    for c, e, nota, dur in notes(major=True, frases=(0,)):
        if c < 6:
            p.posa(vibrafon(midi(nota + 12), dur * CORXERA + 0.5), quan(c + 24, e), pan=0.3, vol=0.07)
    for k, nota in enumerate((88, 84)):
        p.posa(campana(midi(nota), 2.5), quan(30, 4 * k), pan=0, vol=0.035)
    lr = reverb(p.lr, durada=0.5, cua=2.0, humit=0.25, rng=rng, fosc=6000)
    # La cinta, gastada: la peça entera desafina amunt i avall (vibrato lent, voltes senceres).
    n = lr.shape[1]
    retard = 0.003 * SR * (0.5 + 0.5 * np.sin(2 * np.pi * 24 * np.arange(n) / n))  # fins a 3 ms
    idx = (np.arange(n) - retard) % n
    i0 = np.floor(idx).astype(int)
    fr = idx - i0
    return np.stack([ch[i0] * (1 - fr) + ch[(i0 + 1) % n] * fr for ch in lr])


def palau():
    """El palau orbital: vals fred (3/4, quatre compassos per acord), piano i cordes sintètiques."""
    rng = np.random.default_rng(7)
    p = Pista(DURADA)
    vals = COMPAS / 2          # cada compàs de 4/4 són dos compassos de vals
    temps = vals / 3           # una negra del vals (150 per minut)
    acords_llargs(p, rng, cordes, 0.045, pan=0.7, atac=1.5)
    for c in range(COMPASSOS):
        b, veus = acord(c)
        for k in range(2):
            inici = c * COMPAS + k * vals
            # «Um-pa-pa»: el baix al primer temps (fonamental i quinta), l'acord al segon i al tercer.
            nota = b if k == 0 else b + 7
            p.posa(piano(midi(nota), temps * 2.5), inici, pan=-0.2, vol=0.13)
            for tt in (1, 2):
                for j, v in enumerate(veus[1:]):
                    d = temps * 0.8
                    p.posa(piano(midi(v), d), inici + tt * temps, pan=0.15 + 0.1 * j, vol=0.04 if tt == 1 else 0.03)
    # El tema, al piano, amb el ritme quadrat cap al vals: cada nota cau a la corxera de vals més propera.
    for c, e, nota, dur in notes():
        inici = round(quan(c, e) / (temps / 2)) * (temps / 2)
        d = dur * CORXERA + 0.6
        p.posa(piano(midi(nota + 12), d), inici, pan=0.1, vol=0.11)
    # Compassos 24-31: les cordes canten la tercera frase, una octava avall; un vidre a cada compàs.
    for c, e, nota, dur in notes(frases=(2,)):
        if c < 22:
            d = dur * CORXERA + 0.8
            p.posa(cordes(midi(nota - 12), d, rng) * env(d, 0.3, 0.5), quan(c + 8, e), pan=-0.3, vol=0.07)
    for c in range(24, 32):
        p.posa(campana(midi(acord(c)[1][-1] + 24), 2.0), quan(c, 0), pan=0.5, vol=0.015)
    lr = reverb(p.lr, durada=2.0, cua=5.0, humit=0.55, rng=rng, fosc=7000)
    return lr


def tensio():
    """Les sincronies: un rellotge, el baix que batega, cordes en tremolo i el tema greu."""
    rng = np.random.default_rng(8)
    p = Pista(DURADA)
    for c in range(COMPASSOS):
        b, veus = acord(c)
        # El rellotge: tic-tac a cada negra.
        for k in range(4):
            p.posa(fusta(2600 if k % 2 == 0 else 2000, 0.06), quan(c, 2 * k), pan=0.5, vol=0.06)
        # El cor: doble cop al primer temps i al tercer.
        for e in (0, 4):
            p.posa(bombo(rng), quan(c, e), vol=0.3)
            p.posa(bombo(rng, False), quan(c, e + 0.5), vol=0.14)
        # Baix pulsant a corxeres.
        for e in range(8):
            nota = b + (12 if e % 4 == 3 else 0)
            p.posa(baix(midi(nota), CORXERA * 0.6), quan(c, e), vol=0.18 if e % 2 == 0 else 0.1)
        # Puntets electrònics a semicorxeres: el sistema compta.
        for k in range(16):
            if k % 4 != 1:
                nota = veus[(k + c) % 4] + 24
                p.posa(bip(midi(nota), 0.12), quan(c, k / 2), pan=-0.5 if k % 2 else 0.5, vol=0.012)
        # Cordes en tremolo, cada dos compassos.
        if c % 2 == 0:
            d = 2 * COMPAS + 1
            tremolo = 0.55 + 0.45 * np.sin(2 * np.pi * (2 / CORXERA) * t(d))
            for j, v in enumerate(veus):
                p.posa(cordes(midi(v), d, rng) * tremolo * env(d, 0.6, 1.0), quan(c, 0), pan=-0.6 + 0.4 * j, vol=0.045)
        if c % 8 == 7:
            p.posa(metall(rng, midi(veus[-1] + 24)), quan(c, 6), pan=0.5, vol=0.04)
    melodia(p, lambda f, d: band(cordes(f, d, rng), 100, 2500) * env(d, 0.1, 0.3), pan=0.2, vol=0.09, octava=-1)
    return reverb(p.lr, durada=0.8, cua=2.5, humit=0.35, rng=rng, fosc=4000)


def final():
    """Plou: el tema en Mi major, càlid. Guitarra, cordes, xiulet, l'harmònica que respon i la pluja."""
    rng = np.random.default_rng(9)
    p = Pista(DURADA)
    acords_llargs(p, rng, cordes, 0.055, major=True)
    bordo(p, 0.16, major=True)
    for c in range(COMPASSOS):
        b, veus = acord(c, major=True)
        # Guitarra: arpegi a corxeres, amunt i avall.
        arpegi = [b + 12, veus[1], veus[2], veus[3], veus[2] + 12 if c % 2 else veus[3], veus[2], veus[1], veus[2]]
        for e, nota in enumerate(arpegi):
            p.posa(guitarra(midi(nota), 1.6, 0.55), quan(c, e), pan=-0.35, vol=0.08 if e else 0.11)
    melodia(p, xiulet, pan=0.15, vol=0.14, eco=0.25, major=True)
    # Compassos 24-31: l'harmònica respon amb la primera frase.
    for c, e, nota, dur in notes(major=True, frases=(0,)):
        d = dur * CORXERA + 0.4
        p.posa(harmonica(midi(nota), d), quan(c + 24, e), pan=0.3, vol=0.08)
    pluja(p, rng, 0.06)
    return reverb(p.lr, durada=1.5, cua=4.5, humit=0.45, rng=rng, fosc=6000)


# ─── Sortida ────────────────────────────────────────────────────────────────

MUSICA = {
    'tema': tema, 'terra2': terra2, 'nau': nau, 'aqua': aqua, 'ferrum': ferrum,
    'verdant': verdant, 'palau': palau, 'tensio': tensio, 'final': final,
}

# Volum eficaç (RMS) de cada peça: fluix, que és ambient i no ha de tapar les veus ni els sons.
RMS = 0.075
# Pic màxim (per sota de 0 dBFS, amb marge per al còdec).
PIC = 0.89


def limita(lr):
    """Compressor suau de pics: per sota del llindar no toca res; per sobre, arrodoneix fins a `PIC`."""
    llindar = 0.6
    a = np.abs(lr)
    sobre = a > llindar
    out = lr.copy()
    marge = PIC - llindar
    out[sobre] = np.sign(lr[sobre]) * (llindar + marge * np.tanh((a[sobre] - llindar) / marge))
    return out


def write(name, lr):
    lr = lr - lr.mean(axis=1, keepdims=True)
    lr *= RMS / np.sqrt(np.mean(lr ** 2))
    lr = limita(lr)
    pcm = (np.clip(lr.T, -1, 1) * 32767).astype('<i2')
    with tempfile.NamedTemporaryFile(suffix='.wav') as tmp:
        with wave.open(tmp.name, 'wb') as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(pcm.tobytes())
        subprocess.run(
            ['ffmpeg', '-loglevel', 'error', '-y', '-i', tmp.name, '-c:a', 'libvorbis', '-q:a', '3', str(OUT / f'{name}.ogg')],
            check=True,
        )
    rms = np.sqrt(np.mean(lr ** 2))
    costura = np.max(np.abs(lr[:, 0] - lr[:, -1]))
    print(f'  {name}: {lr.shape[1] / SR:.1f} s, pic {np.max(np.abs(lr)):.2f}, rms {rms:.3f}, salt a la costura {costura:.3f}')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    only = set(sys.argv[1:])
    for name, make in MUSICA.items():
        if not only or name in only:
            write(name, make())
    print(f'✔ música a {OUT}')


if __name__ == '__main__':
    main()
