#!/usr/bin/env python3
"""
`npm run musica`: genera la música de L'Última Arrel a `game/audio/music/` (.ogg, estèreo).

Totes les peces són el mateix tema, el crit dels arbres (Re menor dòric, 4/4, 80 negres per minut,
32 compassos, 96 s), amb instruments diferents per lloc. El crit és una veu que puja damunt d'un acord
greu d'orgue de fusta; cada frase comença amb un salt amunt, com qui crida.

- `tema`: la portada. Orgue de fusta, violoncel, la veu que crida, i el bosc al voltant.
- `bosc`: la vora del bosc, al capvespre. Corda puntejada, flauta de fusta, ocells i vent.
- `bosc_viu`: el bosc obert de l'epíleg: el mateix, en Re major i amb més llum.
- `centraleta`: la cova d'arrels. Misteri: tambor de tronc, marimba greu, gotes de vidre i el corn de fusta.
- `fades`: el campament de les Fades d'Ortiga. Punk de joguina, però amable: bateria de capses, baix
  puntejat, piano de joguina i kazoo.
- `gripaus`: el toll dels gripaus buròcrates. Lenta i quadrada: tuba, marimba i el tic-tac de l'oficina.
- `naturaplus`: la caseta d'obra. Música d'ascensor en major, freda: piano elèctric de vidre, baix
  de sintetitzador, i els ocells «prèmium» (sempre el mateix refilet, cada quatre segons).
- `presentacio`: la Zona Zero. Tensió alegre: pizzicato, caixa de banda, timbales i la trompa.
- `final`: els crèdits. El tema en Re major, càlid: cordes, corda puntejada, la veu i la flauta que respon.

Com que tenen la mateixa durada, el joc les encadena al mateix punt (`musicaSincronitzada`) en canviar de lloc.
Les peces són bucles perfectes: cada so que passa del final torna a sonar al principi, les
oscil·lacions lentes fan voltes senceres i la reverberació és circular. Tot sintetitzat, i sempre igual.

`python3 tools/musica.py tema fades` en fa només unes quantes.

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
    n = int(SR * d)
    f = np.asarray(freq, dtype=float)
    f = np.broadcast_to(f, (n,)) if not f.ndim else f[:n]
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


def formants(x, picos):
    """Passa `x` per uns quants formants `(centre, amplada, guany)` (amb la FFT): una vocal, un tub."""
    spec = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    mask = 0.03 + sum(g * np.exp(-((f - c) / w) ** 2) for c, w, g in picos)
    return np.fft.irfft(spec * mask, len(x))


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


# ─── El tema: el crit dels arbres ────────────────────────────────────────────
#
# 4/4, 80 negres per minut. Un acord cada dos compassos; les posicions van en corxeres (0-7).

PPM = 80
TEMPS = 60 / PPM          # una negra
CORXERA = TEMPS / 2
COMPAS = 4 * TEMPS

# Re menor, amb el Si natural del mode dòric (el bosc no està trist: està cansat). Baix + veus (MIDI).
ACORDS = [
    (38, [57, 62, 65, 69]),  # Re m
    (34, [58, 62, 65, 70]),  # Si♭
    (41, [57, 60, 65, 69]),  # Fa
    (36, [55, 60, 64, 67]),  # Do
    (38, [57, 62, 65, 69]),  # Re m
    (43, [55, 59, 62, 67]),  # Sol (el Si natural: dòric)
    (34, [58, 62, 65, 70]),  # Si♭
    (33, [57, 61, 64, 69]),  # La
    (43, [55, 58, 62, 67]),  # Sol m
    (41, [57, 62, 65, 69]),  # Re m/Fa
    (34, [58, 62, 65, 70]),  # Si♭
    (41, [57, 60, 65, 69]),  # Fa
    (43, [55, 58, 62, 67]),  # Sol m
    (38, [57, 62, 65, 69]),  # Re m
    (34, [57, 62, 65, 69]),  # Si♭ maj7
    (33, [55, 61, 64, 69]),  # La 7: torna a començar
]

# El mateix, en Re major: la resposta del bosc (l'epíleg i els crèdits).
ACORDS_MAJOR = [
    (38, [57, 62, 66, 69]),  # Re
    (35, [59, 62, 66, 71]),  # Si m
    (37, [57, 61, 64, 69]),  # La/Do♯ (el Re de la melodia hi fa de quarta que es resol)
    (40, [55, 59, 62, 67]),  # Mi m7
    (38, [57, 62, 66, 69]),  # Re
    (43, [59, 62, 67, 71]),  # Sol
    (35, [59, 62, 66, 71]),  # Si m
    (33, [57, 61, 64, 69]),  # La
    (40, [59, 64, 67, 71]),  # Mi m
    (42, [57, 62, 66, 69]),  # Re/Fa♯
    (35, [59, 62, 66, 71]),  # Si m
    (45, [57, 62, 66, 69]),  # Re/La
    (40, [59, 64, 67, 71]),  # Mi m
    (38, [57, 62, 66, 69]),  # Re
    (43, [59, 62, 66, 71]),  # Sol maj7
    (33, [55, 61, 64, 69]),  # La 7
]
COMPASSOS = 2 * len(ACORDS)
DURADA = COMPASSOS * COMPAS

# (compàs, corxera, nota, durada en corxeres). Tres frases; els darrers 8 compassos, sense melodia.
MELODIA = [
    # Primera: el crit. Una nota llarga i un salt que puja.
    (0, 0, 62, 6), (0, 6, 64, 2), (1, 0, 65, 4), (1, 4, 69, 4),
    (2, 0, 70, 6), (2, 6, 69, 2), (3, 0, 65, 7),
    (4, 0, 69, 4), (4, 4, 72, 4), (5, 0, 74, 6), (5, 6, 72, 2),
    (6, 0, 67, 4), (6, 4, 64, 4), (7, 0, 67, 7),
    # Segona: el mateix crit, més amunt (el Si natural, i el Do♯ de La que vol tornar a casa).
    (8, 0, 62, 2), (8, 2, 65, 2), (8, 4, 69, 8), (9, 4, 74, 4),
    (10, 0, 71, 6), (10, 6, 74, 2), (11, 0, 74, 7),
    (12, 0, 77, 4), (12, 4, 74, 4), (13, 0, 70, 4), (13, 4, 69, 4),
    (14, 0, 69, 4), (14, 4, 73, 4), (15, 0, 76, 7),
    # Tercera: llarga, al punt més alt, i torna a baixar a poc a poc.
    (16, 0, 67, 4), (16, 4, 70, 4), (17, 0, 74, 8),
    (18, 0, 77, 12), (19, 4, 76, 2), (19, 6, 74, 2),
    (20, 0, 74, 4), (20, 4, 72, 2), (20, 6, 70, 2), (21, 0, 65, 7),
    (22, 0, 69, 4), (22, 4, 67, 4), (23, 0, 69, 7),
]

# En major: Fa → Fa♯, Do → Do♯, Si♭ → Si.
A_MAJOR = {5: 1, 0: 1, 10: 1}


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


# ─── Instruments del bosc ────────────────────────────────────────────────────

VOCALS = {
    'a': ((750, 110, 1.0), (1180, 130, 0.55), (2600, 220, 0.2)),
    'o': ((480, 90, 1.0), (850, 110, 0.5), (2500, 220, 0.12)),
    'u': ((330, 80, 1.0), (750, 110, 0.3), (2400, 220, 0.08)),
}


def veu(f, d, vocal='o', puja=True):
    """La veu del crit: entra un to per sota i hi puja (`puja`), amb un vibrato lent, passada per una vocal."""
    x = t(d)
    scoop = 2 ** (-(2 / 12) * np.exp(-x / 0.09)) if puja else 1.0
    vib = 1 + 0.008 * np.sin(2 * np.pi * 5.0 * x) * np.minimum(1, x / 0.6)
    ph = 2 * np.pi * np.cumsum(f * scoop * vib) / SR
    so = sum(np.sin(h * ph) / h for h in range(1, 25) if f * h < 7000)
    ale = np.random.default_rng(int(f * 10)).uniform(-1, 1, len(x)) * 0.04
    return 3 * formants(so + ale, VOCALS[vocal]) * env(d, 0.08, 0.35)


def orgue(f, d, rng):
    """Orgue de fusta: un tub tapat (fonamental, harmònics senars fluixos) que respira, i el buf de l'aire."""
    so = osc(f, d, phase=rng.uniform(0, 6.28)) + 0.2 * osc(2 * f, d) + 0.12 * osc(3 * f, d) + 0.04 * osc(5 * f, d)
    so *= 1 + 0.04 * np.sin(2 * np.pi * rng.uniform(0.2, 0.5) * t(d))
    buf = band(rng.uniform(-1, 1, int(SR * d)), f * 2, f * 6) * 0.04 * env(d, 0.05, 0.3, 0.4)  # «xuf» de l'atac
    return so + buf


def violoncel(f, d, rng=None):
    """Violoncel: serra suau i fosca, l'arc que entra a poc a poc i un vibrato que arriba tard."""
    x = t(d)
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.2 * x) * np.minimum(1, x / 0.8)
    return band(osc(f * vib, d, 'saw'), 60, 1400) * env(d, 0.25, 0.5)


def cordes(f, d, rng):
    """Cordes: tres serres gairebé a l'uníson, fosques."""
    x = sum(osc(f * 2 ** (c / 1200), d, 'saw', phase=rng.uniform(0, 6.28)) for c in (-7, 0, 7)) / 3
    return band(x, 120, 2200)


def flauta(f, d):
    """Flauta de fusta: gairebé una sinusoide, amb alè i un vibrato tou."""
    x = t(d)
    vib = 1 + 0.005 * np.sin(2 * np.pi * 5.0 * x) * np.minimum(1, x / 0.4)
    so = osc(f * vib, d) + 0.12 * osc(2 * f * vib, d) + 0.04 * osc(3 * f * vib, d)
    ale = band(np.random.default_rng(int(f)).uniform(-1, 1, len(x)), f * 0.9, f * 3) * 0.06
    return (so + ale) * env(d, 0.06, 0.3)


@functools.lru_cache(maxsize=None)
def _corda(nota, d, brillo):
    """Corda puntejada (Karplus-Strong): un pols de soroll que es repeteix i s'apaga."""
    f = midi(nota)
    N = max(2, int(round(SR / f - 0.5)))
    total = int(SR * d)
    rng = np.random.default_rng(nota * 13 + int(brillo * 10))
    pols = rng.uniform(-1, 1, N + 1)
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
    return out - np.mean(out)


def puntejat(f, d, brillo=0.5):
    """Corda puntejada de fusta (una guitarra vella, una cítara)."""
    nota = int(round(69 + 12 * np.log2(f / 440)))
    d = round(d, 2)
    return 3.5 * _corda(nota, d, brillo)[: int(SR * d)] * env(d, 0.002, 0.08)


def pizzicato(f, d=0.5):
    return puntejat(f, d, 0.4) * env(d, 0.001, 0.05, 0.18)


def marimba(f, d=1.0):
    """Marimba: la làmina de fusta (fonamental i el parcial de ×3,9) que s'apaga de pressa."""
    caiguda = 0.5 * (261 / f) ** 0.5
    so = osc(f, d) + 0.25 * osc(3.93 * f, d) * env(d, 0.001, 0.05, caiguda / 4) + 0.08 * osc(9.2 * f, d) * env(d, 0.001, 0.02, 0.02)
    return so * env(d, 0.002, 0.1, caiguda)


def tambor_tronc(f=110, d=0.6):
    """Tambor de tronc buit: un cop de fusta greu i rodó."""
    x = t(d)
    so = osc(f * (1 + 0.15 * np.exp(-x / 0.02)), d) + 0.3 * osc(f * 2.3, d) * np.exp(-x / 0.05)
    return so * env(d, 0.002, 0.05, 0.18)


def vidre(f, d=2.5):
    """Un toc de vidre o de gota que ressona (els fils turquesa)."""
    return (osc(f, d) + 0.3 * osc(f * 2.76, d) * env(d, 0.001, 0.1, 0.3)) * env(d, 0.002, 0.2, 0.7)


# ─── Instruments de les fades (joguina) ─────────────────────────────────────

def piano_joguina(f, d=0.8):
    """Piano de joguina: varetes de metall, brillants i curtes."""
    x = t(d)
    so = osc(f, d) + 0.5 * osc(f * 3.0, d) * np.exp(-x / 0.08) + 0.3 * osc(f * 5.4, d) * np.exp(-x / 0.04)
    return so * env(d, 0.001, 0.08, 0.35)


def kazoo(f, d):
    """Un kazoo: una serra que brunz, passada per una vocal nasal."""
    x = t(d)
    vib = 1 + 0.01 * np.sin(2 * np.pi * 6 * x)
    so = osc(f * vib, d, 'saw') * (0.85 + 0.15 * np.sin(2 * np.pi * 31 * x))
    return 1.5 * formants(so, ((600, 160, 1.0), (1400, 220, 0.9), (2900, 320, 0.5))) * env(d, 0.02, 0.08)


def baix_puntejat(f, d):
    """El baix del grup de les fades: puntejat i rodó."""
    return band(osc(f, d, 'saw'), 40, 700) * env(d, 0.004, 0.05, 0.25)


def capsa(rng, d=0.18):
    """La caixa de la bateria: una capsa de cartró."""
    return (band(rng.uniform(-1, 1, int(SR * d)), 300, 2500) + 0.6 * osc(330, d)) * env(d, 0.001, 0.03, 0.045)


def bombo(rng, fort=True):
    """Pell greu que cau de to i un fregament."""
    d = 0.4
    x = t(d)
    f = 55 + 60 * np.exp(-x / 0.025)
    pell = osc(f, d) * env(d, 0.002, 0.05, 0.16 if fort else 0.07)
    return pell + 0.12 * band(rng.uniform(-1, 1, len(x)), 400, 3000) * env(d, 0.001, 0.05, 0.02)


def picarol(rng, d=0.07):
    """Un picarol de llavors (el charles de les fades)."""
    return band(rng.uniform(-1, 1, int(SR * d)), 4000, 11000) * env(d, 0.002, 0.02, 0.02)


# ─── Instruments dels gripaus ────────────────────────────────────────────────

def tuba(f, d):
    """Tuba: serra fosca que s'infla en entrar, amb un toc de llavis."""
    x = t(d)
    obre = 0.5 + 0.5 * np.minimum(1, x / 0.08)
    return band(osc(f * (1 - 0.01 * np.exp(-x / 0.04)), d, 'saw'), 30, min(900, f * 5)) * obre * env(d, 0.03, 0.12)


def bloc(f, d=0.12):
    """Bloc de fusta: to curt i sec (el tic-tac d'oficina)."""
    return (osc(f, d) + 0.4 * osc(f * 2.7, d)) * env(d, 0.001, 0.02, 0.025)


def campaneta(f, d=1.5):
    """La campaneta de la màquina d'escriure (o d'un mostrador)."""
    return sum(a * osc(f * r, d) for r, a in ((1, 1), (2.32, 0.4), (4.25, 0.2))) * env(d, 0.001, 0.1, 0.35)


# ─── Instruments de NaturaPlus (freds) ───────────────────────────────────────

def piano_vidre(f, d):
    """Piano elèctric de FM, net i fred: la campaneta de l'atac i un cos sense cap calidesa."""
    x = t(d)
    index = 1.8 * np.exp(-x / 0.25)
    so = np.sin(2 * np.pi * f * x + index * np.sin(2 * np.pi * f * x))
    tine = 0.12 * np.sin(2 * np.pi * 14 * f * x) * np.exp(-x / 0.03)
    return (so + tine) * env(d, 0.003, 0.12, 1.2)


def sinte_fred(f, d):
    """Sintetitzador fred: quadrada filtrada, sense vibrato."""
    return band(osc(f, d, 'square'), 200, 2200) * env(d, 0.01, 0.1)


def baix_sinte(f, d):
    return (osc(f, d) + 0.15 * osc(2 * f, d)) * env(d, 0.005, 0.06, 0.4)


def tic(rng, d=0.03):
    """Un charles electrònic, petitíssim."""
    return band(rng.uniform(-1, 1, int(SR * d)), 7000, 14000) * env(d, 0.001, 0.01, 0.008)


def ocell_premium(d=0.5):
    """L'ocell de mentida dels «Sons del Bosc — versió prèmium»: dos tons que salten, amb pocs bits."""
    x = t(d)
    f = 2800 + 600 * np.sign(np.sin(2 * np.pi * 8 * x)) + 1000 * x
    return band(np.round(osc(f, d) * 6) / 6, 800, 6000) * env(d, 0.01, 0.05)


# ─── Instruments de la presentació ───────────────────────────────────────────

def trompa(f, d):
    """Trompa: serra rodona i fosca, que entra suau i s'obre una mica."""
    x = t(d)
    vib = 1 + 0.003 * np.sin(2 * np.pi * 5 * x) * np.minimum(1, x / 0.6)
    obre = 0.6 + 0.4 * np.minimum(1, x / 0.2)
    return band(osc(f * vib, d, 'saw'), 80, 1300) * obre * env(d, 0.06, 0.2)


def timbal(f, d=1.2):
    """Timbal: pell afinada que cau una mica de to, i el cop."""
    x = t(d)
    so = osc(f * (1 + 0.06 * np.exp(-x / 0.05)), d) + 0.3 * osc(f * 1.5, d) * np.exp(-x / 0.2)
    cop = band(np.random.default_rng(int(f)).uniform(-1, 1, len(x)), 80, 800) * np.exp(-x / 0.02)
    return (so + 0.5 * cop) * env(d, 0.002, 0.1, 0.45)


def caixa_banda(rng, d=0.15, fort=1.0):
    """La caixa de la banda de música: bordons (soroll brillant) i la pell."""
    return (band(rng.uniform(-1, 1, int(SR * d)), 1500, 9000) + 0.4 * osc(220, d)) * env(d, 0.001, 0.03, 0.05) * fort


def glock(f, d=1.2):
    return (osc(f, d) + 0.2 * osc(f * 2.76, d) * env(d, 0.001, 0.05, 0.1)) * env(d, 0.001, 0.1, 0.5)


# ─── Ambients que duren tot el bucle ─────────────────────────────────────────

def fulles(p, rng, vol, fosc=4000):
    """El vent entre les fulles: un fregament ample que puja i baixa, a cada costat."""
    for ch, pan in ((0, -0.7), (1, 0.7)):
        p.continu(band(p.soroll(rng), 300, fosc) * (0.2 + 0.8 * p.lfo(4 + ch, ch * 1.3) ** 2), pan=pan, vol=vol)


def ocells(p, rng, vol, quants):
    """Ocells de debò: cada un diferent (frases flautades o refilets), escampats."""
    for _ in range(quants):
        f0 = rng.uniform(1800, 3200)
        s = rng.uniform(0, p.durada)
        pan = rng.uniform(-0.9, 0.9)
        e = 0.0
        for _ in range(int(rng.integers(3, 6))):
            d = rng.uniform(0.08, 0.2)
            fa = f0 * rng.uniform(0.85, 1.35)
            so = osc(np.linspace(fa, fa * rng.uniform(0.85, 1.2), int(SR * d)), d)
            p.posa(so * np.sin(np.linspace(0, np.pi, int(SR * d))) ** 1.5, s + e, pan=pan, vol=vol * rng.uniform(0.5, 1))
            e += d + rng.uniform(0.02, 0.08)


def brunzit(p, vol, f=73.42):
    """El brunzit turquesa de la xarxa: quintes que bateguen a poc a poc."""
    for mult, a in ((1, 1), (1.5, 0.5), (2, 0.4), (3, 0.12)):
        for k, des in enumerate((-0.2, 0.2)):
            p.continu(p.sinus(f * mult + des, k * 1.7) * a, pan=-0.4 + 0.8 * k, vol=vol)


# ─── Peces que comparteixen ──────────────────────────────────────────────────

def acords_llargs(p, rng, so, vol, pan=0.5, major=False, atac=2.0, octava=0):
    acords = ACORDS_MAJOR if major else ACORDS
    for i, (b, veus) in enumerate(acords):
        d = 2 * COMPAS + 3
        for j, v in enumerate(veus):
            p.posa(so(midi(v + 12 * octava), d, rng) * env(d, atac, 3.0), 2 * i * COMPAS, pan=-pan + 2 * pan * j / 3, vol=vol)


def bordo(p, vol, major=False, octava=0, so=None, rng=None):
    """El baix de cada acord, llarg."""
    acords = ACORDS_MAJOR if major else ACORDS
    for i, (b, _) in enumerate(acords):
        d = 2 * COMPAS + 2
        x = so(midi(b + 12 * octava), d, rng) if so else osc(midi(b + 12 * octava), d)
        p.posa(x * env(d, 1.0, 2.5), 2 * i * COMPAS, vol=vol)


def arpegis(p, vol, major=False, pan=-0.35, brillo=0.5, cada=1):
    """Corda puntejada: arpegi a corxeres que puja i baixa (`cada` = 2: només a les negres)."""
    for c in range(COMPASSOS):
        b, veus = acord(c, major)
        arpegi = [b + 12, veus[0], veus[1], veus[2], veus[3], veus[2], veus[1], veus[0]]
        for e, nota in enumerate(arpegi):
            if e % cada == 0:
                p.posa(puntejat(midi(nota), 1.6, brillo), quan(c, e), pan=pan, vol=vol * (1.3 if e == 0 else 1))


# ─── Les peces ───────────────────────────────────────────────────────────────

def tema():
    """La portada: l'orgue de fusta greu, el violoncel, la veu que crida, i el bosc al voltant."""
    rng = np.random.default_rng(1)
    p = Pista(DURADA)
    acords_llargs(p, rng, orgue, 0.06, pan=0.5, atac=2.5, octava=-1)
    bordo(p, 0.12, so=violoncel, rng=rng)
    bordo(p, 0.12, octava=-1)
    # La corda puntejada, a negres: el bosc que respira.
    arpegis(p, 0.05, cada=2, brillo=0.4)
    melodia(p, lambda f, d: veu(f, d, 'o'), pan=0.15, vol=0.16, eco=0.25, frases=(0, 2))
    melodia(p, lambda f, d: veu(f, d, 'a'), pan=0.15, vol=0.15, eco=0.25, frases=(1,))
    # Compassos 24-31: el violoncel respon amb el crit, greu.
    for c, e, nota, dur in notes(frases=(0,)):
        d = dur * CORXERA + 0.6
        p.posa(violoncel(midi(nota - 12), d), quan(c + 24, e), pan=-0.3, vol=0.12)
    brunzit(p, 0.012)
    fulles(p, rng, 0.012)
    ocells(p, rng, 0.012, 10)
    return reverb(p.lr, durada=2.0, cua=6.0, humit=0.55, rng=rng, fosc=4000)


def bosc(major=False):
    """El bosc: corda puntejada, la flauta de fusta, i el bosc que hi és (vent i ocells).
    En menor és el capvespre de la vora; en major, el bosc obert de l'epíleg."""
    rng = np.random.default_rng(2 if not major else 12)
    p = Pista(DURADA)
    acords_llargs(p, rng, lambda f, d, r: orgue(f, d, r) * 0.6 + 0.4 * cordes(f, d, r), 0.025, pan=0.7, major=major, atac=3.0)
    bordo(p, 0.13, major=major)
    arpegis(p, 0.06, major=major, brillo=0.45 if not major else 0.6)
    melodia(p, flauta, pan=0.2, vol=0.11, eco=0.2, major=major, frases=(0, 2))
    # La segona frase, a la corda puntejada (la flauta respira).
    for c, e, nota, dur in notes(major, frases=(1,)):
        p.posa(puntejat(midi(nota), dur * CORXERA + 1.0, 0.7), quan(c, e), pan=0.3, vol=0.1)
    # Compassos 24-31: la flauta sola, només el començament del crit, dues vegades i més fluix.
    for k in (0, 4):
        for c, e, nota, dur in notes(major, frases=(0,)):
            if c < 2:
                p.posa(flauta(midi(nota), dur * CORXERA + 0.4), quan(c + 24 + k, e), pan=-0.2, vol=0.06 if k == 0 else 0.04)
    fulles(p, rng, 0.02 if not major else 0.015)
    ocells(p, rng, 0.012 if not major else 0.018, 6 if not major else 16)
    if major:
        brunzit(p, 0.008)
    return reverb(p.lr, durada=1.4, cua=4.5, humit=0.4, rng=rng, fosc=4500)


def centraleta():
    """La cova d'arrels: tambor de tronc, marimba greu, gotes de vidre, el brunzit i el corn de fusta."""
    rng = np.random.default_rng(3)
    p = Pista(DURADA)
    acords_llargs(p, rng, orgue, 0.035, pan=0.6, atac=4.0, octava=-1)
    bordo(p, 0.14, octava=-1)
    brunzit(p, 0.02)
    for c in range(COMPASSOS):
        b, veus = acord(c)
        # El cor de la cova: tambor de tronc, «tum... tum-tum».
        p.posa(tambor_tronc(midi(b + 12) * 1.0), quan(c, 0), pan=-0.2, vol=0.2)
        if c % 2 == 1:
            p.posa(tambor_tronc(midi(b + 12)), quan(c, 5), pan=-0.2, vol=0.1)
            p.posa(tambor_tronc(midi(b + 19)), quan(c, 6), pan=0.2, vol=0.12)
        # Marimba greu: notes de l'acord, poques i a deshora.
        for e in ((3,) if c % 2 == 0 else (2, 7)):
            p.posa(marimba(midi(veus[int(rng.integers(0, 4))] - 12), 1.2), quan(c, e), pan=rng.uniform(-0.5, 0.5), vol=0.1)
        # Gotes de vidre que ressonen: dues per compàs, aleatòries però de l'acord.
        for _ in range(2):
            p.posa(vidre(midi(veus[int(rng.integers(0, 4))] + 24)), quan(c, int(rng.integers(0, 8))), pan=rng.uniform(-0.8, 0.8), vol=0.02)
    # El corn de fusta (la veu que fa sentir els arbres): la primera i la tercera frase, una octava avall, fosc.
    corn = lambda f, d: band(veu(f, d, 'u'), 80, 1500)
    melodia(p, corn, pan=0.1, vol=0.18, octava=-1, eco=0.35, frases=(0, 2))
    return reverb(p.lr, durada=2.6, cua=7.0, humit=0.6, rng=rng, fosc=3000)


def fades():
    """Punk de joguina, amable: bateria de capses, baix puntejat a corxeres, piano de joguina i el kazoo."""
    rng = np.random.default_rng(4)
    p = Pista(DURADA)
    for c in range(COMPASSOS):
        b, veus = acord(c)
        # Baix a corxeres, decidit; l'octava a la darrera.
        for e in range(8):
            nota = b + 12 + (12 if e == 7 else 0)
            p.posa(baix_puntejat(midi(nota), CORXERA * 0.9), quan(c, e), vol=0.16 if e % 2 == 0 else 0.11)
        # Bateria: bombo a l'1 i al 3 (i un cop de més), capsa al 2 i al 4, el picarol a corxeres.
        for e in (0, 3, 4):
            p.posa(bombo(rng), quan(c, e), vol=0.22 if e != 3 else 0.12)
        for e in (2, 6):
            p.posa(capsa(rng), quan(c, e), pan=0.15, vol=0.16)
        for e in range(8):
            p.posa(picarol(rng), quan(c, e), pan=-0.4, vol=0.035 if e % 2 == 0 else 0.022)
        if c % 4 == 3:  # un redoble de capses en acabar la frase
            for k in range(4):
                p.posa(capsa(rng, 0.1), quan(c, 6 + k / 2), pan=0.2, vol=0.06 + 0.02 * k)
        # Piano de joguina: «acords de força» (fonamental i quinta) a contratemps.
        for e in (1, 3, 5, 7):
            for nota in (veus[0], veus[0] + 7):
                p.posa(piano_joguina(midi(nota + 12), 0.4), quan(c, e), pan=0.4, vol=0.025)
    # El tema al kazoo i al piano de joguina, alhora (un d'ells desafina una mica, és clar).
    melodia(p, kazoo, pan=-0.15, vol=0.05, legato=0.1)
    melodia(p, lambda f, d: piano_joguina(f * 2 ** (8 / 1200), min(d, 1.0)), pan=0.25, vol=0.08, octava=1, legato=0.1)
    # Compassos 24-31: la primera frase a l'octava, només piano de joguina i picarols; cridòria de fades.
    for c, e, nota, dur in notes(frases=(0,)):
        p.posa(piano_joguina(midi(nota + 24), 0.8), quan(c + 24, e), pan=0.0, vol=0.06)
    return reverb(p.lr, durada=0.5, cua=1.5, humit=0.2, rng=rng, fosc=6000)


def gripaus():
    """Els gripaus buròcrates: lenta i quadrada. Tuba, marimba, el tic-tac de l'oficina i el segell."""
    rng = np.random.default_rng(5)
    p = Pista(DURADA)
    for c in range(COMPASSOS):
        b, veus = acord(c)
        # «Um... pa»: la tuba a l'1 i al 3 (fonamental i quinta), la marimba als contratemps.
        p.posa(tuba(midi(b), TEMPS * 1.6), quan(c, 0), vol=0.3)
        p.posa(tuba(midi(b + 7 if c % 2 == 0 else b - 5), TEMPS * 1.6), quan(c, 4), vol=0.24)
        for e in (2, 6):
            for j, v in enumerate(veus[1:]):
                p.posa(marimba(midi(v), 0.6), quan(c, e) + 0.01 * j, pan=0.35, vol=0.06)
        # El rellotge de l'oficina: tic... tac...
        for k in range(4):
            p.posa(bloc(1500 if k % 2 == 0 else 1150), quan(c, 2 * k), pan=-0.5, vol=0.04)
        # Cada quatre compassos: el segell («pam!») i la campaneta del mostrador.
        if c % 4 == 3:
            p.posa(tambor_tronc(90, 0.4), quan(c, 7), vol=0.18)
        if c % 8 == 7:
            p.posa(campaneta(2093), quan(c, 7.5), pan=0.5, vol=0.03)
    # El tema a la tuba, solemne i una mica massa lent per a ell (només les notes del temps fort).
    for c, e, nota, dur in notes(frases=(0, 2)):
        if e in (0, 4):
            d = dur * CORXERA + 0.2
            p.posa(tuba(midi(nota - 12), d) * env(d, 0.05, 0.25), quan(c, e), pan=0.15, vol=0.16)
    # La segona frase, a la marimba amb tremolo.
    for c, e, nota, dur in notes(frases=(1,)):
        for k in range(dur * 2):
            p.posa(marimba(midi(nota), 0.4), quan(c, e + k / 2), pan=-0.1, vol=0.07 * (1 if k == 0 else 0.6))
    return reverb(p.lr, durada=0.8, cua=2.5, humit=0.25, rng=rng, fosc=4000)


def naturaplus():
    """NaturaPlus: música d'ascensor en major, freda. Piano elèctric de vidre, baix de sintetitzador, charles
    electrònic, la melodia al sintetitzador i els ocells «prèmium», cada quatre segons, sempre iguals."""
    rng = np.random.default_rng(6)
    p = Pista(DURADA)
    for c in range(COMPASSOS):
        b, veus = acord(c, major=True)
        # Baix: fonamental a l'1, quinta a la corxera abans del 3. Recte, sense swing.
        for e, nota in ((0, b), (3, b + 7), (4, b), (6, b + 12)):
            p.posa(baix_sinte(midi(nota), CORXERA * 1.6), quan(c, e), vol=0.18 if e in (0, 4) else 0.11)
        # Piano de vidre: l'acord amb la sèptima, als temps 1 i «i» del 2.
        setena = [v for v in veus] + [b + 23]
        for e in (0, 3):
            for j, v in enumerate(setena):
                p.posa(piano_vidre(midi(v + 12), 1.2), quan(c, e) + 0.004 * j, pan=-0.3, vol=0.022)
        # Charles a semicorxeres, petitíssim, i un «bip» de tauleta cada quatre compassos.
        for k in range(16):
            p.posa(tic(rng), quan(c, k / 2), pan=0.5, vol=0.03 if k % 2 == 0 else 0.015)
        if c % 4 == 1:
            p.posa(osc(2093, 0.08) * env(0.08, 0.002, 0.01), quan(c, 7), pan=0.6, vol=0.04)
    acords_llargs(p, rng, lambda f, d, r: band(osc(f, d, 'square'), 300, 1500), 0.012, pan=0.6, major=True, atac=0.5)
    # El tema al sintetitzador, en major i somrient (i, a sota, el piano de vidre que el dobla).
    melodia(p, sinte_fred, pan=0.15, vol=0.05, octava=1, major=True, legato=0.15)
    melodia(p, piano_vidre, pan=-0.1, vol=0.05, octava=1, major=True, legato=0.4)
    # Els «Sons del Bosc — versió prèmium»: el mateix ocell exacte, cada quatre segons.
    for k in range(int(DURADA / 4)):
        p.posa(ocell_premium(), 4 * k + 1.0, pan=0.7, vol=0.025)
        p.posa(ocell_premium(), 4 * k + 1.6, pan=0.7, vol=0.018)
    # Fred: una sala petita i neta, sense calidesa ni greus de més.
    lr = reverb(p.lr, durada=0.4, cua=1.5, humit=0.2, rng=rng, fosc=8000)
    return np.stack([band(ch, 60, None) for ch in lr])


def presentacio():
    """La presentació a la Zona Zero: tensió alegre. Pizzicato a corxeres, caixa de banda, timbales, la trompa
    amb el tema i el glockenspiel que fa pampallugues."""
    rng = np.random.default_rng(7)
    p = Pista(DURADA)
    for c in range(COMPASSOS):
        b, veus = acord(c)
        # Pizzicato: fonamental, quinta i octava, a corxeres, saltant.
        patro = [b + 12, b + 19, b + 24, b + 19, b + 12, b + 19, veus[2], b + 19]
        for e, nota in enumerate(patro):
            p.posa(pizzicato(midi(nota)), quan(c, e), pan=-0.35 + 0.1 * (e % 2), vol=0.13 if e % 4 == 0 else 0.09)
        # Caixa de banda: «ta, ta-ta-ta», com qui s'escapa de puntetes.
        for e, f in ((2, 1.0), (6, 1.0), (6.5, 0.5), (7, 0.6), (7.5, 0.7)):
            p.posa(caixa_banda(rng, fort=f), quan(c, e), pan=0.3, vol=0.06)
        # Timbales: la fonamental a cada compàs, i la quinta a l'acabar l'acord.
        p.posa(timbal(midi(b + 12)), quan(c, 0), vol=0.2)
        if c % 2 == 1:
            p.posa(timbal(midi(b + 7)), quan(c, 4), vol=0.12)
        # El glockenspiel: una nota de l'acord, a dalt de tot, a contratemps.
        if c % 2 == 0:
            p.posa(glock(midi(veus[3] + 24)), quan(c, 5), pan=0.6, vol=0.03)
    acords_llargs(p, rng, cordes, 0.03, pan=0.5, atac=1.0)
    melodia(p, trompa, pan=0.1, vol=0.1, octava=-1, legato=0.25)
    # Compassos 24-31: el crit a les cordes, en tremolo, i la caixa que s'aguanta la respiració.
    for c, e, nota, dur in notes(frases=(0,)):
        d = dur * CORXERA + 0.3
        trem = 0.6 + 0.4 * np.sin(2 * np.pi * (4 / TEMPS) * t(d))
        p.posa(cordes(midi(nota), d, rng) * trem * env(d, 0.05, 0.2), quan(c + 24, e), pan=-0.2, vol=0.07)
    return reverb(p.lr, durada=1.0, cua=3.0, humit=0.3, rng=rng, fosc=5000)


def final():
    """Els crèdits: el tema en Re major, la resposta del bosc. Cordes, corda puntejada, la veu, i la flauta
    que respon."""
    rng = np.random.default_rng(8)
    p = Pista(DURADA)
    acords_llargs(p, rng, cordes, 0.04, pan=0.6, major=True, atac=2.0)
    acords_llargs(p, rng, orgue, 0.025, pan=0.3, major=True, atac=3.0, octava=-1)
    bordo(p, 0.12, major=True, so=violoncel, rng=rng)
    arpegis(p, 0.06, major=True, brillo=0.6)
    melodia(p, lambda f, d: veu(f, d, 'a'), pan=0.15, vol=0.14, eco=0.25, major=True)
    # Compassos 24-31: la flauta respon amb el crit, i els ocells hi tornen.
    for c, e, nota, dur in notes(major=True, frases=(0,)):
        p.posa(flauta(midi(nota + 12), dur * CORXERA + 0.4), quan(c + 24, e), pan=-0.25, vol=0.07)
    brunzit(p, 0.01)
    ocells(p, rng, 0.012, 12)
    return reverb(p.lr, durada=1.8, cua=5.0, humit=0.45, rng=rng, fosc=5500)


# ─── Sortida ────────────────────────────────────────────────────────────────

MUSICA = {
    'tema': tema, 'bosc': bosc, 'bosc_viu': lambda: bosc(major=True), 'centraleta': centraleta, 'fades': fades,
    'gripaus': gripaus, 'naturaplus': naturaplus, 'presentacio': presentacio, 'final': final,
}

# Volum eficaç (RMS) de cada peça: fluix, que és ambient sota els diàlegs (més fluix que els efectes).
RMS = 0.06
# Les peces amb ritme (bateria, pizzicato) s'hi senten més amb el mateix RMS: una mica més avall.
RMS_PECA = {'fades': 0.05, 'presentacio': 0.052, 'naturaplus': 0.05}
# Pic màxim: per sota de -1 dBFS, amb marge per al còdec.
PIC = 0.85


def limita(lr):
    """Compressor suau de pics: per sota del llindar no toca res; per sobre, arrodoneix fins a `PIC`."""
    llindar = 0.55
    a = np.abs(lr)
    sobre = a > llindar
    out = lr.copy()
    marge = PIC - llindar
    out[sobre] = np.sign(lr[sobre]) * (llindar + marge * np.tanh((a[sobre] - llindar) / marge))
    return out


def write(name, lr):
    lr = lr - lr.mean(axis=1, keepdims=True)
    lr *= RMS_PECA.get(name, RMS) / np.sqrt(np.mean(lr ** 2))
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
