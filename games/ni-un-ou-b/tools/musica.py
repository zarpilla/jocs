#!/usr/bin/env python3
"""
`npm run musica`: genera la música d'ambient de Ni un ou a `game/audio/music/` (.ogg, estèreo).

Totes les peces són el mateix tema (Re menor, 6/8, 50 ppm a la negra amb punt, 32 compassos) amb
instruments diferents, per zona del vaixell:

- `tema`: portada i pròleg. Nit a l'Atlàntic: acords freds, un bordó greu, la mar i el tema al
  xiulet amb eco.
- `maquines`: la coberta de sota. El motor que ronca, cops de metall a les canonades i el tema a
  l'acordió, greu.
- `coberta`: la coberta principal, la casa. Acordió que acompanya a l'estil de cançó de mar, baix
  i pandero, i el tema al violí.
- `pont`: pont, ràdio i pal. Obert: vent, un sonar, puntets electrònics de satèl·lit i estàtica.
- `fora`: les cobertes de fora. Onades, vent que xiula, una boia amb campana i el tema lluny.
- `tensio`: per a les sincronies. Cor que batega, baix obstinat, cordes en tremolo.
- `galway`: el final i els crèdits. El tema en Re major, a trenc d'alba: guitarra, cordes i gavines.

Com que tenen la mateixa durada, el joc les encadena al mateix punt (`sync`) en canviar de lloc.
Les peces són bucles perfectes: cada so que passa del final torna a sonar al principi, les
oscil·lacions lentes fan voltes senceres i la reverberació és circular. Tot sintetitzat, i sempre igual.

Cal python3 amb numpy, i ffmpeg.
"""
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
        self.n = int(SR * durada)
        self.durada = self.n / SR
        self.lr = np.zeros((2, self.n))

    def posa(self, x, inici, pan=0.0, vol=1.0):
        """`pan` de -1 (esquerra) a 1 (dreta)."""
        a = (pan + 1) * np.pi / 4
        x = x[: self.n] * vol
        i = int(SR * inici) % self.n
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


# ─── El tema de Ni un ou ──────────────────────────────────────────────────
#
# 6/8 de cançó de mar, lent. Un acord cada dos compassos; les posicions van en corxeres (0-5).

PPM = 50                 # negres amb punt per minut
TEMPS = 60 / PPM         # una negra amb punt
CORXERA = TEMPS / 3
COMPAS = 2 * TEMPS

# Re menor: baix + veus (notes MIDI). 16 acords, 32 compassos, 76,8 s.
ACORDS = [
    (38, [57, 62, 65, 69]),  # Re m
    (36, [55, 60, 64, 67]),  # Do
    (34, [57, 62, 65, 70]),  # Si♭ maj7
    (33, [55, 61, 64, 69]),  # La 7
    (38, [57, 62, 65, 69]),  # Re m
    (41, [57, 60, 65, 69]),  # Fa
    (36, [55, 60, 64, 67]),  # Do
    (33, [55, 61, 64, 69]),  # La 7
    (43, [58, 62, 67, 70]),  # Sol m
    (38, [57, 62, 65, 69]),  # Re m
    (34, [58, 62, 65, 70]),  # Si♭
    (41, [57, 60, 65, 69]),  # Fa
    (43, [58, 62, 67, 70]),  # Sol m
    (34, [58, 62, 65, 72]),  # Si♭ add9
    (33, [57, 62, 64, 69]),  # La sus4
    (33, [58, 61, 64, 67]),  # La 7(♭9): torna a començar
]

# El mateix, en Re major (el final a Galway).
ACORDS_MAJOR = [
    (38, [57, 62, 66, 69]),  # Re
    (37, [57, 61, 64, 69]),  # La/Do♯
    (43, [55, 59, 62, 66]),  # Sol maj7
    (33, [55, 61, 64, 69]),  # La 7
    (38, [57, 62, 66, 69]),  # Re
    (42, [57, 61, 66, 69]),  # Fa♯ m
    (40, [55, 59, 62, 67]),  # Mi m7
    (33, [57, 61, 64, 69]),  # La
    (43, [59, 62, 67, 71]),  # Sol
    (38, [57, 62, 66, 69]),  # Re
    (35, [59, 62, 66, 71]),  # Si m
    (38, [57, 62, 66, 69]),  # Re
    (43, [59, 62, 67, 71]),  # Sol
    (40, [55, 59, 62, 67]),  # Mi m7
    (33, [57, 62, 64, 69]),  # La sus4
    (33, [57, 61, 64, 67]),  # La 7
]
COMPASSOS = 2 * len(ACORDS)
DURADA = COMPASSOS * COMPAS

# (compàs, corxera, nota, durada en corxeres). Tres frases; els darrers 8 compassos, sense melodia.
MELODIA = [
    # Primera: una pregunta que baixa i torna a pujar.
    (0, 0, 69, 2), (0, 2, 74, 1), (0, 3, 72, 2), (0, 5, 69, 1), (1, 0, 65, 3), (1, 3, 67, 1), (1, 4, 69, 2),
    (2, 0, 67, 2), (2, 2, 72, 1), (2, 3, 76, 2), (2, 5, 74, 1), (3, 0, 72, 4), (3, 4, 67, 2),
    (4, 0, 65, 2), (4, 2, 70, 1), (4, 3, 74, 2), (4, 5, 72, 1), (5, 0, 70, 3), (5, 3, 69, 1), (5, 4, 67, 2),
    (6, 0, 64, 2), (6, 2, 69, 1), (6, 3, 73, 3), (7, 0, 76, 2), (7, 2, 73, 1), (7, 3, 69, 3),
    # Segona: el mateix començament, i se'n va cap amunt.
    (8, 0, 69, 2), (8, 2, 74, 1), (8, 3, 72, 2), (8, 5, 69, 1), (9, 0, 65, 3), (9, 3, 67, 1), (9, 4, 69, 2),
    (10, 0, 72, 2), (10, 2, 77, 1), (10, 3, 76, 2), (10, 5, 72, 1), (11, 0, 69, 4), (11, 4, 72, 2),
    (12, 0, 76, 2), (12, 2, 79, 1), (12, 3, 76, 2), (12, 5, 74, 1), (13, 0, 72, 3), (13, 3, 67, 1), (13, 4, 64, 2),
    (14, 0, 69, 2), (14, 2, 73, 1), (14, 3, 76, 3), (15, 0, 74, 2), (15, 2, 73, 1), (15, 3, 69, 3),
    # Tercera: més amunt, amb enyor, i torna a casa.
    (16, 0, 74, 2), (16, 2, 70, 1), (16, 3, 67, 2), (16, 5, 70, 1), (17, 0, 74, 3), (17, 3, 77, 1), (17, 4, 74, 2),
    (18, 0, 77, 2), (18, 2, 76, 1), (18, 3, 74, 2), (18, 5, 69, 1), (19, 0, 74, 5),
    (20, 0, 70, 2), (20, 2, 74, 1), (20, 3, 77, 2), (20, 5, 76, 1), (21, 0, 74, 3), (21, 3, 72, 1), (21, 4, 70, 2),
    (22, 0, 69, 2), (22, 2, 72, 1), (22, 3, 65, 2), (22, 5, 67, 1), (23, 0, 69, 5),
]

# En major: Fa → Fa♯, Si♭ → Si, Do → Do♯.
A_MAJOR = {5: 1, 10: 1, 0: 1}


def acord(c, major=False):
    """L'acord que sona al compàs `c`."""
    acords = ACORDS_MAJOR if major else ACORDS
    return acords[(c // 2) % len(acords)]


def quan(c, e):
    """Segons del compàs `c`, corxera `e`."""
    return (c * 6 + e) * CORXERA


def melodia(p, instrument, pan=0.0, vol=0.2, octava=0, eco=0.0, major=False):
    for c, e, nota, dur in MELODIA:
        if major:
            nota += A_MAJOR.get(nota % 12, 0)
        d = dur * CORXERA + 0.6
        x = instrument(midi(nota + 12 * octava), d)
        p.posa(x, quan(c, e), pan=pan, vol=vol)
        if eco:
            # Eco a negra amb punt, a l'altre costat.
            p.posa(x, quan(c, e) + TEMPS, pan=-pan, vol=vol * eco)


# ─── Instruments ─────────────────────────────────────────────────────────────

def xiulet(f, d):
    """Xiulet de llauna: gairebé una sinusoide, amb alè i un vibrato que arriba tard."""
    x = t(d)
    vib = 1 + 0.005 * np.sin(2 * np.pi * 5.2 * x) * np.minimum(1, x / 0.5)
    so = osc(f * vib, d) + 0.1 * osc(2 * f * vib, d)
    ale = band(np.random.default_rng(int(f)).uniform(-1, 1, len(x)), f * 0.8, f * 3) * 0.08
    return (so + ale) * env(d, 0.05, 0.25)


def violi(f, d):
    x = t(d)
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.6 * x) * np.minimum(1, x / 0.35)
    return band(osc(f * vib, d, 'saw'), 250, 3500) * env(d, 0.09, 0.25)


def acordio(f, d, atac=0.03):
    """Llengüetes: dues serres una mica desafinades (el batec de l'acordió) i la manxa."""
    x = t(d)
    manxa = 0.9 + 0.1 * np.sin(2 * np.pi * 0.7 * x)
    so = (osc(f * 2 ** (4 / 1200), d, 'saw') + osc(f * 2 ** (-4 / 1200), d, 'saw')) / 2
    return band(so, 150, 3000) * manxa * env(d, atac, 0.12)


def pad(f, d, rng):
    """Tres sinusoides gairebé a l'uníson i l'octava fluixa."""
    x = sum(osc(f * 2 ** (c / 1200), d, phase=rng.uniform(0, 6.28)) for c in (-6, 0, 6)) / 3
    return x + 0.08 * osc(f * 2, d)


def cordes(f, d, rng):
    """Cordes fredes: el pad amb una mica de serra filtrada."""
    return 0.7 * pad(f, d, rng) + 0.3 * band(osc(f, d, 'saw'), 200, 1800)


def baix(f, d):
    return (osc(f, d) + 0.2 * osc(f * 2, d)) * env(d, 0.01, 0.15)


def punteig(f, d, fosc=3000):
    """Corda puntejada (guitarra)."""
    so = osc(f, d, 'saw') * env(d, 0.002, 0.08, 0.35)
    return band(so, 90, fosc)


def pandero(rng, fort=True):
    """Bodhran: pell greu que cau de to i un fregament."""
    d = 0.35
    x = t(d)
    f = 70 + 50 * np.exp(-x / 0.02)
    pell = osc(f, d) * env(d, 0.002, 0.05, 0.12 if fort else 0.06)
    return pell + 0.15 * band(rng.uniform(-1, 1, len(x)), 500, 3000) * env(d, 0.001, 0.05, 0.03)


def campana(f, d=4.0):
    """Campana (la boia, o un vidre): parcials inharmònics que s'apaguen a ritmes diferents."""
    parcials = ((0.5, 0.3, 2.5), (1, 1, 1.8), (1.19, 0.4, 1.2), (1.56, 0.3, 0.9), (2.0, 0.35, 1.0), (2.51, 0.2, 0.6), (3.01, 0.15, 0.4))
    return sum(a * osc(f * r, d) * env(d, 0.002, 0.2, dec) for r, a, dec in parcials) / 2


def metall(rng, f):
    """Un cop a una canonada: metall inharmònic i un clic."""
    d = 1.2
    so = sum(a * osc(f * r, d) * env(d, 0.001, 0.1, dec) for r, a, dec in ((1, 1, 0.5), (2.76, 0.5, 0.3), (5.4, 0.3, 0.15), (8.93, 0.2, 0.08)))
    clic = band(rng.uniform(-1, 1, int(SR * d)), 1500) * env(d, 0.0005, 0.05, 0.01)
    return so + 0.5 * clic


def bip(f, d=0.25):
    """Puntet electrònic: sinusoide neta i curta."""
    return (osc(f, d) + 0.2 * osc(f * 3, d)) * env(d, 0.003, 0.05, 0.08)


def sonar(f):
    d = 3.0
    return osc(f, d) * env(d, 0.004, 0.3, 0.7)


def gavina(rng):
    """Una gavina lluny: un crit que puja i cau, dos o tres cops."""
    sortida = []
    for _ in range(rng.integers(2, 4)):
        d = rng.uniform(0.25, 0.4)
        x = t(d) / d
        f = 1500 + 500 * np.sin(np.pi * np.minimum(1, x * 1.4)) - 300 * x
        so = osc(f, d) + 0.4 * osc(2 * f, d) + 0.2 * osc(3 * f, d)
        sortida.append(band(so * env(d, 0.03, 0.1), 900, 5000))
        sortida.append(np.zeros(int(SR * rng.uniform(0.05, 0.15))))
    return np.concatenate(sortida)


# ─── Ambients que duren tot el bucle ─────────────────────────────────────────

def onades(p, rng, vol, pan=0.4):
    """La mar: soroll greu que puja i baixa, dues capes amb onades de ritmes diferents."""
    for voltes, fase, costat in ((11, 0.0, -pan), (7, 2.0, pan)):
        x = band(p.soroll(rng), 80, 900)
        ona = p.lfo(voltes, fase) ** 3
        p.continu(x * (0.15 + ona), pan=costat, vol=vol)
        escuma = band(p.soroll(rng), 1500, 6000) * p.lfo(voltes, fase + 0.4) ** 6
        p.continu(escuma, pan=costat, vol=vol * 0.3)


def vent(p, rng, vol, xiula=True):
    """El vent: un fregament ample i, a sobre, bandes estretes que s'encenen i s'apaguen (el xiulet)."""
    for ch, pan in ((0, -0.7), (1, 0.7)):
        base = band(p.soroll(rng), 150, 1500) * (0.5 + 0.5 * p.lfo(5, ch * 1.3))
        p.continu(base, pan=pan, vol=vol)
    if xiula:
        for k, (centre, voltes) in enumerate(((420, 3), (610, 4), (880, 6), (1250, 5))):
            x = ressonancia(p.soroll(rng), centre, centre * 0.03)
            x /= np.sqrt(np.mean(x ** 2))
            p.continu(x * p.lfo(voltes, k * 1.7) ** 4, pan=-0.6 + 0.4 * k, vol=vol * 0.25)


def motor(p, rng, vol):
    """El motor dièsel: un brunzit greu en Re i explosions regulars, tot en voltes senceres."""
    p.continu(p.sinus(midi(26)) + 0.5 * p.sinus(2 * midi(26), 1.0) + 0.2 * p.sinus(3 * midi(26), 2.0), vol=vol * 0.5)
    cops = round(5.5 * p.durada)
    for i in range(cops):
        d = 0.12
        x = t(d)
        cop = osc(60 + 30 * np.exp(-x / 0.01), d) * env(d, 0.002, 0.02, 0.04)
        p.posa(cop, i * p.durada / cops, vol=vol * rng.uniform(0.6, 1.0))
    remor = band(p.soroll(rng), 30, 250) * (0.6 + 0.4 * p.lfo(cops))
    p.continu(remor, vol=vol * 0.6)


def estatica(p, rng, quantes, vol):
    """La ràdio: ràfegues curtes de soroll de banda estreta, amb espetecs."""
    for _ in range(quantes):
        d = rng.uniform(0.4, 1.4)
        x = band(rng.uniform(-1, 1, int(SR * d)), 800, 3500)
        x *= (rng.uniform(0, 1, len(x)) > 0.995) * 3 + 0.5
        p.posa(x * env(d, 0.1, 0.3), rng.uniform(0, p.durada), pan=rng.uniform(-0.5, 0.5), vol=vol)


# ─── Les peces ───────────────────────────────────────────────────────────────

def acords_llargs(p, rng, so, vol, pan=0.5, major=False, atac=2.0):
    acords = ACORDS_MAJOR if major else ACORDS
    for i, (b, veus) in enumerate(acords):
        d = 2 * COMPAS + 3
        for j, v in enumerate(veus):
            p.posa(so(midi(v), d, rng) * env(d, atac, 3.0), 2 * i * COMPAS, pan=-pan + 2 * pan * j / 3, vol=vol)


def bordo(p, vol, major=False):
    """El baix de cada acord, una octava avall, llarg."""
    acords = ACORDS_MAJOR if major else ACORDS
    for i, (b, _) in enumerate(acords):
        d = 2 * COMPAS + 2
        p.posa(osc(midi(b), d) * env(d, 1.0, 2.5), 2 * i * COMPAS, vol=vol)


def tema():
    """Portada i pròleg: nit a l'Atlàntic. Acords freds, bordó, la mar i el xiulet amb eco."""
    rng = np.random.default_rng(1)
    p = Pista(DURADA)
    acords_llargs(p, rng, pad, 0.08)
    bordo(p, 0.22)
    melodia(p, xiulet, pan=0.2, vol=0.17, eco=0.35)
    onades(p, rng, 0.05)
    # Una campana llunyana al començament de cada frase.
    for c in (0, 8, 16, 24):
        p.posa(campana(midi(74)), quan(c, 0), pan=-0.5, vol=0.04)
    return reverb(p.lr, durada=1.8, cua=5.0, humit=0.6, rng=rng, fosc=4500)


def maquines():
    """La coberta de sota: el motor, cops de canonada i el tema a l'acordió, greu."""
    rng = np.random.default_rng(2)
    p = Pista(DURADA)
    motor(p, rng, 0.25)
    acords_llargs(p, rng, pad, 0.05, pan=0.3)
    for c in range(COMPASSOS):
        b, veus = acord(c)
        # El baix, a negres amb punt, com les bieles.
        for e in (0, 3):
            p.posa(baix(midi(b), TEMPS * 0.9), quan(c, e), vol=0.22 if e == 0 else 0.15)
        # Canonades: un cop al primer temps de cada compàs parell, i un de més agut de tant en tant.
        if c % 2 == 0:
            p.posa(metall(rng, midi(b + 24)), quan(c, 0), pan=-0.5, vol=0.05)
        if c % 4 == 3:
            p.posa(metall(rng, midi(veus[-1] + 12)), quan(c, 4), pan=0.6, vol=0.035)
    melodia(p, lambda f, d: acordio(f, d, 0.05), pan=0.15, vol=0.15, octava=-1)
    # Un xiuxiueig de vapor de tant en tant.
    for c in (5, 13, 21, 29):
        d = 1.6
        p.posa(band(rng.uniform(-1, 1, int(SR * d)), 3000, 9000) * env(d, 0.3, 0.8), quan(c, 2), pan=0.7, vol=0.03)
    lr = reverb(p.lr, durada=0.6, cua=2.0, humit=0.35, rng=rng, fosc=3000)
    # Tot plegat, tancat: com si sonés entre parets de ferro.
    return np.stack([band(ch, 30, 5000) for ch in lr])


def coberta():
    """La coberta principal, la casa: acordió de cançó de mar, baix, pandero i el tema al violí."""
    rng = np.random.default_rng(3)
    p = Pista(DURADA)
    for c in range(COMPASSOS):
        b, veus = acord(c)
        # Baix «a-ma» (fonamental i quinta) i l'acordió a les corxeres 2 i 5.
        p.posa(baix(midi(b), TEMPS * 0.8), quan(c, 0), vol=0.22)
        p.posa(baix(midi(b + 7), TEMPS * 0.8), quan(c, 3), vol=0.15)
        for e in (1, 2, 4, 5):
            d = CORXERA * 0.9
            for j, v in enumerate(veus[1:]):
                p.posa(acordio(midi(v), d + 0.1), quan(c, e), pan=-0.3 + 0.1 * j, vol=0.03 if e in (2, 5) else 0.02)
        for e, fort in ((0, True), (3, True), (5, False)):
            p.posa(pandero(rng, fort), quan(c, e), pan=0.25, vol=0.2 if fort else 0.1)
    acords_llargs(p, rng, pad, 0.035)
    melodia(p, violi, pan=0.15, vol=0.12)
    return reverb(p.lr, durada=0.7, cua=2.5, humit=0.3, rng=rng, fosc=4000)


def pont():
    """Pont, ràdio i pal: obert. Vent, sonar, puntets de satèl·lit, estàtica i el tema al xiulet."""
    rng = np.random.default_rng(4)
    p = Pista(DURADA)
    acords_llargs(p, rng, cordes, 0.06, pan=0.7, atac=2.5)
    bordo(p, 0.15)
    vent(p, rng, 0.05)
    for c in range(COMPASSOS):
        b, veus = acord(c)
        # Satèl·lit: les notes de l'acord, dues octaves amunt, a corxeres i fluixes.
        for e in range(6):
            nota = veus[(e * 2 + c) % len(veus)] + 24
            p.posa(bip(midi(nota)), quan(c, e), pan=0.6 if e % 2 else -0.6, vol=0.025 if e else 0.04)
        # El sonar: un cop cada dos compassos, a la fonamental.
        if c % 2 == 0:
            p.posa(sonar(midi(b + 36)), quan(c, 0), pan=-0.2, vol=0.05)
    estatica(p, rng, 10, 0.03)
    melodia(p, xiulet, pan=0.1, vol=0.13, eco=0.3)
    return reverb(p.lr, durada=1.4, cua=4.0, humit=0.5, rng=rng, fosc=6000)


def fora():
    """Les cobertes de fora: onades, vent que xiula, la boia i el tema lluny."""
    rng = np.random.default_rng(5)
    p = Pista(DURADA)
    onades(p, rng, 0.09, pan=0.5)
    vent(p, rng, 0.08)
    acords_llargs(p, rng, pad, 0.04, pan=0.8, atac=3.0)
    bordo(p, 0.12)
    # La boia: la campana a l'atzar del balanceig (sempre a la mateixa nota, Re).
    for k in range(9):
        c = int(k * COMPASSOS / 9) + rng.integers(0, 2)
        p.posa(campana(midi(69), 5.0), quan(c, rng.integers(0, 6)), pan=0.6, vol=0.035)
    # El tema, lluny i esmorteït: com si arribés de dins.
    melodia(p, lambda f, d: band(xiulet(f, d), 200, 1800), pan=-0.2, vol=0.13, octava=-1, eco=0.4)
    return reverb(p.lr, durada=2.2, cua=6.0, humit=0.55, rng=rng, fosc=3500)


def tensio():
    """Les sincronies: cor que batega, baix obstinat, cordes en tremolo i el tema al violí, greu."""
    rng = np.random.default_rng(6)
    p = Pista(DURADA)
    for c in range(COMPASSOS):
        b, veus = acord(c)
        # El cor: doble cop a cada negra amb punt.
        for e in (0, 3):
            p.posa(pandero(rng), quan(c, e), vol=0.3)
            p.posa(pandero(rng, False), quan(c, e + 0.6), vol=0.15)
        # Baix a corxeres, amb la quinta a la tercera.
        for e in range(6):
            nota = b + (7 if e == 2 or e == 5 else 0)
            p.posa(baix(midi(nota), CORXERA * 0.7), quan(c, e), vol=0.2 if e % 3 == 0 else 0.12)
        # Cordes en tremolo, cada dos compassos.
        if c % 2 == 0:
            d = 2 * COMPAS + 1
            tremolo = 0.55 + 0.45 * np.sin(2 * np.pi * (2 / CORXERA) * t(d))  # dues per corxera
            for j, v in enumerate(veus):
                p.posa(cordes(midi(v), d, rng) * tremolo * env(d, 0.6, 1.0), quan(c, 0), pan=-0.6 + 0.4 * j, vol=0.05)
        # Un pic de metall agut als darrers compassos de cada frase.
        if c % 8 == 7:
            p.posa(metall(rng, midi(veus[-1] + 24)), quan(c, 3), pan=0.5, vol=0.04)
    melodia(p, violi, pan=0.2, vol=0.1, octava=-1)
    return reverb(p.lr, durada=0.8, cua=2.5, humit=0.35, rng=rng, fosc=4000)


def galway():
    """El final: el tema en major a trenc d'alba. Guitarra, cordes càlides, xiulet i gavines."""
    rng = np.random.default_rng(7)
    p = Pista(DURADA)
    acords_llargs(p, rng, cordes, 0.06, major=True)
    bordo(p, 0.18, major=True)
    for c in range(COMPASSOS):
        b, veus = acord(c, major=True)
        # Guitarra: arpegi a corxeres, avall i amunt.
        arpegi = [b + 12, veus[1], veus[2], veus[3], veus[2], veus[1]]
        for e, nota in enumerate(arpegi):
            p.posa(punteig(midi(nota), 1.2), quan(c, e), pan=-0.35, vol=0.08 if e else 0.11)
    melodia(p, xiulet, pan=0.15, vol=0.16, eco=0.25, major=True)
    # Últims compassos, sense melodia: el violí hi respon a sota, amb la primera frase.
    for c, e, nota, dur in MELODIA:
        if c < 8:
            nota += A_MAJOR.get(nota % 12, 0)
            d = dur * CORXERA + 0.6
            p.posa(violi(midi(nota - 12), d), quan(c + 24, e), pan=0.3, vol=0.07)
    onades(p, rng, 0.025)
    for c in (3, 11, 19, 28):
        p.posa(gavina(rng), quan(c, rng.integers(0, 6)), pan=rng.uniform(-0.7, 0.7), vol=0.025)
    return reverb(p.lr, durada=1.5, cua=4.5, humit=0.5, rng=rng, fosc=6000)


# ─── Sortida ────────────────────────────────────────────────────────────────

MUSICA = {'tema': tema, 'maquines': maquines, 'coberta': coberta, 'pont': pont, 'fora': fora, 'tensio': tensio, 'galway': galway}

# Volum eficaç (RMS) de cada peça: fluix, que és ambient i no ha de tapar les veus ni els sons.
RMS = {'tema': 0.08, 'maquines': 0.08, 'coberta': 0.08, 'pont': 0.08, 'fora': 0.08, 'tensio': 0.08, 'galway': 0.08}


def write(name, lr):
    lr = lr - lr.mean(axis=1, keepdims=True)
    lr *= RMS[name] / np.sqrt(np.mean(lr ** 2))
    pic = np.max(np.abs(lr))
    if pic > 0.95:
        lr *= 0.95 / pic
    pcm = (np.clip(lr.T, -1, 1) * 32767).astype('<i2')
    with tempfile.NamedTemporaryFile(suffix='.wav') as tmp:
        with wave.open(tmp.name, 'wb') as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(pcm.tobytes())
        subprocess.run(
            ['ffmpeg', '-loglevel', 'error', '-y', '-i', tmp.name, '-c:a', 'libvorbis', '-q:a', '4', str(OUT / f'{name}.ogg')],
            check=True,
        )
    print(f'  {name}: {lr.shape[1] / SR:.1f} s, pic {np.max(np.abs(lr)):.2f}')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    only = set(sys.argv[1:])
    for name, make in MUSICA.items():
        if not only or name in only:
            write(name, make())
    print(f'✔ música a {OUT}')


if __name__ == '__main__':
    main()
