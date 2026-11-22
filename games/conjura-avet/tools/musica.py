#!/usr/bin/env python3
"""
`npm run musica`: genera la música de La Conjura de l'Avet a `game/audio/music/` (.ogg, estèreo).

Totes les peces són la mateixa cançó, la corranda de l'avet («L'avet que plantà l'Emma / té les arrels de paper; /
qui el tombi, que s'ho pensi, / que l'Emma ja ho va saber»): Re dòric, 6/8, 60 negres amb punt per minut, 48
compassos, 96 s. Quatre versos de dos compassos, amb una anacrusi de corxera; sota, el bordó de la viola de roda
(Re i La), que no s'atura mai. La forma, de vuit en vuit compassos: entrada, estrofa, estrofa, tornada, estrofa, coda.

- `tema`: la portada i el pròleg. Misteriosa: el bordó, la flauta amb eco, el murmuri dels monjos, la campana.
- `tempesta`: l'avet el dia de la pluja. Inquieta: la gossa de la viola a corxeres, tabals que insisteixen, ràfegues.
- `poble`: la plaça i el pont. De mercat: tabal i pandereta en giga, llaüt rasguejat, i el sacabutx dels
  buròcrates a la tornada, amb el segell que pica.
- `claustre`: el claustre i l'apotecaria. Tranquil·la: flauta, llaüt, gotes de les teulades, i la Gueraula que
  canta la corranda.
- `preparacio`: la bugaderia. Enjogassada: llaüt «um-pa», flauta amb mordents, i un cor de monjos de mentida.
- `nit`: la porteria i la cuina. Sigil·losa i còmica: pizzicato de puntetes, passes, el sacabutx que rellisca.
- `arxiu`: l'scriptorium i l'arxiu. Tensió baixa: bordó greu, un cor que murmura, campana llunyana, el cor que
  batega.
- `fugida`: el molí. Ràpida: tabals a corxeres, llaüt a semicorxeres, la roda del molí.
- `mati`: el matí de l'acte 4 i el judici. Solemne i esperançada: campanes, el cor, la flauta i els ocells.
- `final`: l'epíleg i els crèdits. La corranda en Re major, lluminosa.

Com que tenen la mateixa durada i la mateixa harmonia compàs a compàs, el joc les encadena al mateix punt
(`musicaSincronitzada`) en canviar de lloc. Les peces són bucles perfectes: cada so que passa del final torna a sonar
al principi, els bordons i les oscil·lacions lentes fan voltes senceres i la reverberació és circular. Tot
sintetitzat, i sempre igual. Les eines de síntesi són les de L'Última Arrel.

`python3 tools/musica.py tema nit` en fa només unes quantes.

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


# ─── La corranda ─────────────────────────────────────────────────────────────
#
# 6/8, 60 negres amb punt per minut: una corxera fa 1/3 s i un compàs, 2 s. Les posicions van en corxeres (0-5).

CORXERA = 1 / 3
TEMPS = 3 * CORXERA       # una negra amb punt
COMPAS = 6 * CORXERA

# Els acords (baix, veus en MIDI). Damunt del bordó de Re i La, que no canvia mai.
A = {
    'Rem': (38, [57, 62, 65, 69]),
    'Do': (36, [55, 60, 64, 67]),
    'Lam': (45, [57, 60, 64, 69]),
    'Sol': (43, [55, 59, 62, 67]),  # el Si natural: dòric
    'Fa': (41, [57, 60, 65, 69]),
    # En major (el final).
    'Re': (38, [57, 62, 66, 69]),
    'La': (45, [57, 61, 64, 69]),
    'Mim': (40, [55, 59, 64, 67]),
    'Sim': (47, [54, 59, 62, 66]),
}

# La forma: sis seccions de vuit compassos, i l'harmonia de cadascuna (en Re dòric i en Re major).
SECCIONS = ['entrada', 'estrofa', 'estrofa', 'tornada', 'estrofa', 'coda']
HARMONIA = {
    'entrada': (['Rem', 'Do', 'Rem', 'Lam', 'Rem', 'Lam', 'Do', 'Lam'], ['Re', 'La', 'Re', 'La', 'Re', 'La', 'Sol', 'La']),
    'estrofa': (['Rem', 'Lam', 'Do', 'Lam', 'Sol', 'Rem', 'Fa', 'Rem'], ['Re', 'La', 'Sol', 'La', 'La', 'Re', 'Sol', 'Re']),
    'tornada': (['Fa', 'Fa', 'Do', 'Do', 'Lam', 'Sol', 'Rem', 'Rem'], ['Re', 'La', 'La', 'Mim', 'Re', 'La', 'Mim', 'Re']),
    'coda': (['Rem', 'Lam', 'Do', 'Lam', 'Sol', 'Rem', 'Do', 'Lam'], ['Re', 'La', 'Sol', 'La', 'La', 'Re', 'Sol', 'La']),
}
COMPASSOS = 8 * len(SECCIONS)
DURADA = COMPASSOS * COMPAS

# (compàs, corxera, nota, durada en corxeres). Set síl·labes per vers: l'anacrusi (al compàs d'abans), quatre
# notes i dues de llargues. «L'avet que plantà l'Emma» puja; «té les arrels de paper» cau al La greu; «qui el
# tombi, que s'ho pensi» puja fins al Re (amb el Si natural); «que l'Emma ja ho va saber» torna a casa.
ESTROFA = [
    (-1, 5, 57, 1), (0, 0, 62, 2), (0, 2, 64, 1), (0, 3, 65, 2), (0, 5, 67, 1), (1, 0, 69, 3), (1, 3, 67, 2),
    (1, 5, 65, 1), (2, 0, 64, 2), (2, 2, 62, 1), (2, 3, 64, 2), (2, 5, 65, 1), (3, 0, 64, 3), (3, 3, 57, 2),
    (3, 5, 69, 1), (4, 0, 72, 2), (4, 2, 71, 1), (4, 3, 69, 2), (4, 5, 67, 1), (5, 0, 69, 3), (5, 3, 74, 2),
    (5, 5, 72, 1), (6, 0, 69, 2), (6, 2, 67, 1), (6, 3, 65, 2), (6, 5, 64, 1), (7, 0, 62, 3), (7, 3, 62, 2),
]
# La tornada: la mateixa tonada, mirant cap a Fa (més amunt, més oberta).
TORNADA = [
    (-1, 5, 65, 1), (0, 0, 69, 2), (0, 2, 72, 1), (0, 3, 74, 2), (0, 5, 72, 1), (1, 0, 69, 3), (1, 3, 72, 2),
    (1, 5, 74, 1), (2, 0, 72, 2), (2, 2, 69, 1), (2, 3, 67, 2), (2, 5, 69, 1), (3, 0, 67, 3), (3, 3, 64, 2),
    (3, 5, 65, 1), (4, 0, 69, 2), (4, 2, 72, 1), (4, 3, 74, 2), (4, 5, 76, 1), (5, 0, 74, 3), (5, 3, 72, 2),
    (5, 5, 71, 1), (6, 0, 69, 2), (6, 2, 67, 1), (6, 3, 65, 2), (6, 5, 64, 1), (7, 0, 62, 3), (7, 3, 57, 2),
]
FRASES = {'estrofa': ESTROFA, 'tornada': TORNADA}
ESTROFES = (1, 2, 4)      # les seccions amb la corranda
TOTES = (1, 2, 3, 4)      # i amb la tornada

# En major: Fa → Fa♯, Do → Do♯.
A_MAJOR = {5: 1, 0: 1}
ESCALA = [0, 2, 3, 5, 7, 9, 10]  # Re dòric, des de Re


def acord(c, major=False):
    """L'acord del compàs `c` (baix, veus)."""
    seccio = SECCIONS[(c // 8) % len(SECCIONS)]
    return A[HARMONIA[seccio][1 if major else 0][c % 8]]


def quan(c, e):
    """Segons del compàs `c`, corxera `e`."""
    return (c * 6 + e) * CORXERA


def notes(seccions=TOTES, major=False, versos=(0, 1, 2, 3)):
    """La melodia de les seccions que es demanen (compàs absolut), en major si cal, només dels `versos` triats."""
    for s in seccions:
        for c, e, nota, dur in FRASES[SECCIONS[s]]:
            if (c * 6 + e + 1) // 12 in versos:
                if major:
                    nota += A_MAJOR.get(nota % 12, 0)
                yield 8 * s + c, e, nota, dur


def grau(nota, passos, major=False):
    """La nota `passos` graus amunt (o avall) dins l'escala."""
    rel = (nota - 62) % 12
    if major:
        rel -= {6: 1, 1: 1}.get(nota % 12, 0)  # Fa♯ i Do♯ tornen a Fa i Do
    octava = (nota - 62 - rel) // 12
    i = ESCALA.index(rel) + passos
    n = 62 + 12 * (octava + i // 7) + ESCALA[i % 7]
    return n + (A_MAJOR.get(n % 12, 0) if major else 0)


def melodia(p, instrument, seccions=TOTES, pan=0.0, vol=0.2, octava=0, eco=0.0, major=False, legato=0.3,
            staccato=None, mordents=0.0, versos=(0, 1, 2, 3), rng=None):
    """La corranda a un instrument. `staccato` (s) escurça les notes; `mordents` és la probabilitat que una nota
    llarga dugui una nota de pas a sobre, de flauta de festa."""
    rng = rng or np.random.default_rng(99)
    for c, e, nota, dur in notes(seccions, major, versos):
        d = staccato if staccato else dur * CORXERA + legato
        inici = quan(c, e)
        f = midi(nota + 12 * octava)
        p.posa(instrument(f, d), inici, pan=pan, vol=vol)
        if mordents and dur >= 2 and rng.random() < mordents:
            p.posa(instrument(midi(grau(nota, 1, major) + 12 * octava), 0.09), inici - 0.08, pan=pan, vol=vol * 0.7)
        if eco:
            # Eco a negra amb punt, a l'altre costat.
            p.posa(instrument(f, d), inici + TEMPS, pan=-pan, vol=vol * eco)


# ─── Instruments ─────────────────────────────────────────────────────────────

NASAL = ((650, 220, 1.0), (1300, 320, 0.8), (2700, 500, 0.45))


def bordo_roda(p, vol, notes=(38, 50, 57), rng=None, roda=1.0):
    """El bordó de la viola de roda: cordes fregades per la roda, nasals i que no s'aturen mai. Cada corda fa voltes
    senceres al bucle (tanca bé), i la roda hi fa un vaivé lent, també de voltes senceres."""
    rng = rng or np.random.default_rng(0)
    fr = np.arange(p.n) / p.n
    so = np.zeros(p.n)
    for k, nota in enumerate(notes):
        voltes = round(midi(nota) * p.durada)
        ph = 2 * np.pi * voltes * fr + rng.uniform(0, 6.28)
        hmax = int(7000 / midi(nota))
        so += sum(np.sin(h * ph) / h for h in range(1, min(hmax, 24))) / (1 + 0.3 * k)
    so = formants(so, NASAL) + 0.5 * band(so, None, 500)
    vaive = 1 + roda * (0.06 * np.sin(2 * np.pi * round(0.7 * p.durada) * fr) + 0.03 * np.sin(2 * np.pi * round(5.3 * p.durada) * fr + 1))
    p.continu(so * vaive, pan=-0.15, vol=vol)


def viola_roda(f, d):
    """La viola de roda que fa la melodia: una serra nasal, amb el tremolor de la roda i el cop de l'atac."""
    x = t(d)
    so = osc(f * (1 + 0.002 * np.sin(2 * np.pi * 5.5 * x)), d, 'saw') * (1 + 0.06 * np.sin(2 * np.pi * 6.7 * x))
    return 1.6 * formants(so, NASAL) * env(d, 0.02, 0.07)


def gossa(f=midi(62), d=0.22):
    """La gossa (el pont que brunz de la viola de roda): un cop de serra que vibra a 45 cops per segon."""
    x = t(d)
    rasp = 0.4 + 0.6 * (np.sin(2 * np.pi * 45 * x) > 0)
    return band(osc(f, d, 'saw') * rasp, 300, 4500) * env(d, 0.003, 0.05, 0.08)


def flauta(f, d):
    """Flauta de bec: gairebé una sinusoide, amb alè i un vibrato tou."""
    x = t(d)
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.0 * x) * np.minimum(1, x / 0.4)
    so = osc(f * vib, d) + 0.18 * osc(2 * f * vib, d) + 0.06 * osc(3 * f * vib, d)
    ale = band(np.random.default_rng(int(f)).uniform(-1, 1, len(x)), f * 0.9, f * 3) * 0.08
    xuf = band(np.random.default_rng(int(f) + 1).uniform(-1, 1, len(x)), 1500, 6000) * 0.12 * np.exp(-x / 0.03)
    return (so + ale + xuf) * env(d, 0.03, min(0.25, d / 3))


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


def llaut(f, d, brillo=0.6):
    """Llaüt (o saltiri, si és brillant): corda puntejada de fusta."""
    nota = int(round(69 + 12 * np.log2(f / 440)))
    d = round(d, 2)
    return 3.5 * _corda(nota, d, brillo)[: int(SR * d)] * env(d, 0.002, 0.08)


def pizzicato(f, d=0.4):
    return llaut(f, d, 0.4) * env(d, 0.001, 0.05, 0.12)


def rasgueig(p, c, e, major, vol, pan=0.3, amunt=False, brillo=0.55):
    """El llaüt rasguejat: les notes de l'acord una darrere l'altra, molt de pressa."""
    b, veus = acord(c, major)
    cordes = [b + 12] + veus
    if amunt:
        cordes = cordes[::-1][:3]
    for j, nota in enumerate(cordes):
        p.posa(llaut(midi(nota), 0.9, brillo), quan(c, e) + 0.012 * j, pan=pan, vol=vol * (0.7 if amunt else 1))


VOCALS = {
    'a': ((750, 110, 1.0), (1180, 130, 0.55), (2600, 220, 0.2)),
    'o': ((480, 90, 1.0), (850, 110, 0.5), (2500, 220, 0.12)),
    'u': ((330, 80, 1.0), (750, 110, 0.3), (2400, 220, 0.08)),
    'e': ((480, 90, 1.0), (1900, 160, 0.4), (2600, 220, 0.25)),
    'af': ((900, 130, 1.0), (1450, 160, 0.6), (2950, 250, 0.3)),  # una veu de dona, a la «a»
}


def veu(f, d, vocal='o', puja=False, vib=0.008):
    """Una veu: vibrato lent que arriba tard, una mica d'alè, passada per una vocal (`puja`: entra per sota)."""
    x = t(d)
    scoop = 2 ** (-(1.5 / 12) * np.exp(-x / 0.07)) if puja else 1.0
    v = 1 + vib * np.sin(2 * np.pi * 5.0 * x) * np.minimum(1, x / 0.6)
    ph = 2 * np.pi * np.cumsum(f * scoop * v) / SR
    so = sum(np.sin(h * ph) / h for h in range(1, 30) if f * h < 7000)
    ale = np.random.default_rng(int(f * 10)).uniform(-1, 1, len(x)) * 0.04
    return 3 * formants(so + ale, VOCALS[vocal]) * env(d, 0.12, 0.35)


def cor(f, d, vocal='o'):
    """Uns quants monjos a l'uníson, desafinats el just."""
    return sum(veu(f * 2 ** (c / 1200), d, vocal, vib=0.006) for c in (-9, 0, 8)) / 2


def sacabutx(f, d, cau=0.0):
    """Sacabutx (el trombó d'abans): serra rodona que s'infla, amb un toc de llavis. `cau`: semitons que rellisca."""
    x = t(d)
    fr = f * (1 - 0.012 * np.exp(-x / 0.04)) * 2 ** (-cau * np.clip((x - 0.1) / max(d - 0.1, 0.01), 0, 1) ** 1.5 / 12)
    obre = 0.45 + 0.55 * np.minimum(1, x / 0.1)
    return band(osc(fr, d, 'saw'), 40, min(1800, f * 7)) * obre * env(d, 0.025, 0.1)


def campana(f, d=7.0):
    """Campana de bronze: els parcials de campana (l'«hum» a sota, la tercera menor) que s'apaguen a ritmes diferents."""
    x = t(d)
    llarg = (220 / f) ** 0.3
    parcials = ((0.5, 0.6, 3.5), (1, 1.0, 2.2), (1.19, 0.5, 1.6), (1.5, 0.35, 1.2), (2, 0.4, 1.0), (2.51, 0.2, 0.6),
                (3.01, 0.15, 0.4), (4.17, 0.08, 0.25))
    so = sum(a * np.sin(2 * np.pi * f * r * x + r) * np.exp(-x / (dec * llarg * 1.5)) for r, a, dec in parcials)
    cop = band(np.random.default_rng(int(f)).uniform(-1, 1, len(x)), 500, 4000) * np.exp(-x / 0.01) * 0.3
    return (so + cop) * env(d, 0.002, 0.3)


def gota(f, d=1.8):
    """Una gota de les teulades que ressona a la pica."""
    return (osc(f, d) + 0.3 * osc(f * 2.76, d) * env(d, 0.001, 0.1, 0.2)) * env(d, 0.002, 0.2, 0.5)


# Percussió de pell, suau.

def pell(rng, f=95, fort=1.0, d=0.5):
    """El tabal (o el pandero de pell): cop rodó que cau de to, i la mà."""
    x = t(d)
    fr = f * (1 + 0.5 * np.exp(-x / 0.012))
    cos = osc(fr, d) * env(d, 0.002, 0.05, 0.2) + 0.25 * osc(fr * 1.58, d) * env(d, 0.002, 0.05, 0.05)
    ma = band(rng.uniform(-1, 1, len(x)), 150, 1800) * env(d, 0.001, 0.02, 0.012) * 0.5
    return (cos + ma) * fort


def tec(rng, d=0.1):
    """El cop de dits a la vora del pandero."""
    return (band(rng.uniform(-1, 1, int(SR * d)), 1000, 6000) + 0.4 * osc(640, d)) * env(d, 0.001, 0.02, 0.018)


def pandereta(rng, d=0.3):
    """Les sonalles de la pandereta: uns quants platerets de llauna que xoquen."""
    x = t(d)
    so = sum(np.sin(2 * np.pi * f * x + rng.uniform(0, 6)) for f in (5300, 6900, 8150, 9700)) / 4
    xocs = band(rng.uniform(-1, 1, len(x)), 4500, 12000)
    return (0.5 * so + xocs) * env(d, 0.002, 0.05, 0.06)


def bloc(f, d=0.12):
    """Bloc de fusta: to curt i sec."""
    return (osc(f, d) + 0.4 * osc(f * 2.7, d)) * env(d, 0.001, 0.02, 0.025)


def segell(rng):
    """El segell del comte que pica damunt el pergamí: «pam!», sec, com un tambor petit."""
    d = 0.35
    x = t(d)
    cop = osc(150 * (1 + 0.3 * np.exp(-x / 0.01)), d) * env(d, 0.001, 0.05, 0.06)
    fusta = band(rng.uniform(-1, 1, len(x)), 300, 3000) * env(d, 0.001, 0.02, 0.015)
    return cop + 0.6 * fusta


def passa(rng, d=0.15):
    """Una passa de puntetes sobre la pedra, amb sabata de roba."""
    return band(rng.uniform(-1, 1, int(SR * d)), 120, 900) * env(d, 0.004, 0.03, 0.03)


def grinyol(d=0.9):
    """La roda del molí que grinyola: fusta que frega."""
    x = t(d)
    f = 180 + 60 * np.sin(2 * np.pi * 1.3 * x) + 40 * x
    so = osc(f, d, 'saw') * (0.6 + 0.4 * np.sin(2 * np.pi * 23 * x))
    return band(so, 200, 2000) * env(d, 0.1, 0.3)


# ─── Ambients que duren tot el bucle ─────────────────────────────────────────

def vent(p, rng, vol, fosc=2500, rafegues=4):
    """El vent: un fregament ample que puja i baixa, a cada costat."""
    for ch, pan in ((0, -0.7), (1, 0.7)):
        p.continu(band(p.soroll(rng), 200, fosc) * (0.15 + 0.85 * p.lfo(rafegues + ch, ch * 1.3) ** 3), pan=pan, vol=vol)


def aigua(p, rng, vol):
    """L'aigua del rec que corre (amb la FFT, tanca bé)."""
    for pan in (-0.5, 0.5):
        p.continu(band(p.soroll(rng), 300, 2500) * (0.7 + 0.3 * p.lfo(11, pan)), pan=pan, vol=vol)


def ocells(p, rng, vol, quants):
    """Ocells: cada un diferent (frases flautades o refilets), escampats."""
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


# ─── Peces que comparteixen ──────────────────────────────────────────────────

def acords(p, so, vol, compassos=range(COMPASSOS), major=False, pan=0.5, octava=0, atac=0.4, veus=(0, 1, 2, 3)):
    """Els acords llargs, un per compàs (lligats si el següent és igual)."""
    for c in compassos:
        if c > 0 and c - 1 in compassos and acord(c - 1, major) == acord(c, major):
            continue
        llarg = 1
        while c + llarg in compassos and acord(c + llarg, major) == acord(c, major) and llarg < 4:
            llarg += 1
        d = llarg * COMPAS + 0.8
        _, vs = acord(c, major)
        for j in veus:
            p.posa(so(midi(vs[j] + 12 * octava), d) * env(d, atac, 0.8), quan(c, 0), pan=-pan + 2 * pan * j / 3, vol=vol)


def arpegis(p, vol, compassos=range(COMPASSOS), major=False, pan=-0.35, brillo=0.5, cada=1, semicorxeres=False):
    """El llaüt: arpegi a corxeres que puja i baixa (`cada` = 3: només als temps)."""
    for c in compassos:
        b, veus = acord(c, major)
        arpegi = [b + 12, veus[0], veus[1], veus[2], veus[1], veus[0]]
        if semicorxeres:
            arpegi = [b + 12, veus[1], veus[0], veus[2], veus[1], veus[3], veus[2], veus[1], veus[0], veus[2], veus[1], veus[0]]
        pas = 0.5 if semicorxeres else 1
        for k, nota in enumerate(arpegi):
            if k % cada == 0:
                p.posa(llaut(midi(nota), 1.4 if not semicorxeres else 0.5, brillo), quan(c, k * pas), pan=pan,
                       vol=vol * (1.3 if k == 0 else 1))


def baixos(p, so, vol, compassos=range(COMPASSOS), major=False, temps=(0,), d=TEMPS, octava=0, pan=0.0):
    """El baix de l'acord als temps triats (en corxeres)."""
    for c in compassos:
        b, _ = acord(c, major)
        for e in temps:
            p.posa(so(midi(b + 12 * octava), d), quan(c, e), pan=pan, vol=vol)


def seccio(*s):
    """Els compassos de les seccions `s`."""
    return [8 * k + c for k in s for c in range(8)]


# ─── Les peces ───────────────────────────────────────────────────────────────

def tema():
    """La portada i el pròleg: el bordó de la viola de roda a la nit, la flauta amb eco, un cor que murmura i la
    campana del monestir, lluny. El pandero batega fluix."""
    rng = np.random.default_rng(1)
    p = Pista(DURADA)
    bordo_roda(p, 0.045, rng=rng)
    acords(p, lambda f, d: cor(f, d, 'u'), 0.05, compassos=seccio(1, 2, 3, 4), octava=-1, atac=1.5, veus=(0, 1, 2))
    for c in range(COMPASSOS):
        if 8 <= c < 40:
            p.posa(pell(rng, 80), quan(c, 0), pan=-0.1, vol=0.16)
            p.posa(pell(rng, 80, 0.5), quan(c, 3), pan=-0.1, vol=0.1)
        elif c % 2 == 0:
            p.posa(pell(rng, 75), quan(c, 0), pan=-0.1, vol=0.1)
    # Entrada: la campana, i la flauta que només gosa dir el primer vers.
    for c in (0, 4):
        p.posa(campana(midi(50), 8.0), quan(c, 0), pan=0.5, vol=0.05)
    for c, e, nota, dur in notes((1,), versos=(0,)):
        p.posa(flauta(midi(nota), dur * CORXERA + 0.4), quan(c - 4, e), pan=0.3, vol=0.08)
    melodia(p, flauta, (1, 3), pan=0.2, vol=0.09, eco=0.3, legato=0.4)
    melodia(p, viola_roda, (2,), pan=-0.1, vol=0.06, legato=0.15)
    arpegis(p, 0.04, compassos=seccio(2, 3), cada=3, brillo=0.4)
    melodia(p, flauta, (4,), pan=0.2, vol=0.1, eco=0.25, legato=0.4)
    melodia(p, viola_roda, (4,), pan=-0.2, vol=0.04, octava=-1, legato=0.15)
    # Coda: la campana, i el llaüt que recorda els tres primers versos, a poc a poc.
    p.posa(campana(midi(50), 8.0), quan(40, 0), pan=0.5, vol=0.05)
    for c, e, nota, dur in notes((1,), versos=(0, 1, 2)):
        if e in (0, 3) or c < 8:
            p.posa(llaut(midi(nota), 2.0, 0.45), quan(c + 32, e), pan=-0.3, vol=0.1)
    vent(p, rng, 0.012)
    return reverb(p.lr, durada=2.2, cua=6.0, humit=0.55, rng=rng, fosc=3500)


def tempesta():
    """L'avet el dia de la pluja: inquieta. La gossa de la viola a corxeres, el tabal que insisteix, ràfegues de vent,
    la viola de roda i la flauta aguda que no troben repòs."""
    rng = np.random.default_rng(2)
    p = Pista(DURADA)
    bordo_roda(p, 0.05, notes=(38, 45, 50), rng=rng, roda=2.0)
    for c in range(COMPASSOS):
        for e in range(6):
            if c >= 8 or e in (0, 3):
                p.posa(gossa(), quan(c, e), pan=-0.2, vol=0.05 if e in (0, 3) else 0.025)
        # Tabal: «tum . ta tum . ta», i un redoble en acabar cada vers.
        for e, f in ((0, 1.0), (2, 0.4), (3, 0.8), (5, 0.4)):
            p.posa(pell(rng, 75 if e == 0 else 100, f), quan(c, e), vol=0.14)
        if c % 2 == 1:
            for k in range(6):
                p.posa(pell(rng, 110, 0.2 + 0.08 * k, 0.25), quan(c, 3 + k / 2), pan=0.3, vol=0.12)
    baixos(p, lambda f, d: sacabutx(f, d), 0.06, compassos=range(8, 40), temps=(0,), d=TEMPS * 1.5, pan=0.1)
    # Entrada i coda: una ràfega de flauta que puja i baixa, com el vent.
    for c in (1, 3, 5, 41, 43, 45):
        b, veus = acord(c)
        for k, nota in enumerate([62, 64, 65, 67, 69, 72, 74, 72, 69, 67, 65, 64]):
            p.posa(flauta(midi(nota + 12), 0.2), quan(c, k / 2), pan=0.4, vol=0.03 + 0.003 * min(k, 12 - k))
    melodia(p, viola_roda, (1, 4), pan=-0.1, vol=0.09, legato=0.1)
    melodia(p, lambda f, d: flauta(f, d) * (0.75 + 0.25 * np.sin(2 * np.pi * 7 * t(d))), (2,), pan=0.25, vol=0.07, octava=1, legato=0.2)
    melodia(p, viola_roda, (3,), pan=-0.1, vol=0.07, legato=0.1)
    melodia(p, flauta, (3, 4), pan=0.3, vol=0.04, octava=1, legato=0.1, staccato=0.18)
    vent(p, rng, 0.02, fosc=3000, rafegues=6)
    return reverb(p.lr, durada=1.6, cua=4.5, humit=0.4, rng=rng, fosc=4000)


def poble():
    """La plaça i el pont: dia de mercat. Tabal i pandereta en giga, el llaüt rasguejat, la viola de roda i la flauta
    de festa. A la tornada arriben els buròcrates: el sacabutx, massa solemne, i el segell que pica."""
    rng = np.random.default_rng(3)
    p = Pista(DURADA)
    bordo_roda(p, 0.03, notes=(50, 57), rng=rng)
    for c in range(COMPASSOS):
        burocrates = 24 <= c < 32
        for e, f in ((0, 1.0), (3, 0.7)):
            p.posa(pell(rng, 90, f), quan(c, e), vol=0.2)
        for e in (2, 5):
            p.posa(tec(rng), quan(c, e), pan=0.2, vol=0.06)
        if not burocrates:
            for e in (1, 2, 4, 5):
                p.posa(pandereta(rng, 0.15), quan(c, e), pan=0.5, vol=0.03 if e in (1, 4) else 0.02)
            p.posa(pandereta(rng, 0.4), quan(c, 0), pan=0.5, vol=0.05)
            rasgueig(p, c, 0, False, 0.05)
            rasgueig(p, c, 3, False, 0.04)
            rasgueig(p, c, 5, False, 0.04, amunt=True)
        else:
            # Els buròcrates: «um-pa» quadrat i el segell al final de cada vers.
            b, _ = acord(c)
            p.posa(sacabutx(midi(b), TEMPS * 0.8), quan(c, 0), pan=-0.1, vol=0.14)
            p.posa(sacabutx(midi(b + 7), TEMPS * 0.8), quan(c, 3), pan=-0.1, vol=0.11)
            rasgueig(p, c, 1.5, False, 0.03)
            rasgueig(p, c, 4.5, False, 0.03)
            if c % 2 == 1:
                p.posa(segell(rng), quan(c, 3), pan=0.35, vol=0.16)
                p.posa(segell(rng), quan(c, 4), pan=0.35, vol=0.16)
        for e in (0, 3):
            p.posa(gossa(), quan(c, e), pan=-0.2, vol=0.035)
    # Entrada: la flauta saluda amb el primer vers; coda: la viola, els tres primers.
    for c, e, nota, dur in notes((1,), versos=(0,)):
        p.posa(flauta(midi(nota + 12), dur * CORXERA + 0.1), quan(c - 4, e), pan=0.3, vol=0.06)
    melodia(p, viola_roda, (1, 2, 4), pan=-0.15, vol=0.09, legato=0.05)
    melodia(p, flauta, (2, 4), pan=0.3, vol=0.07, octava=1, legato=0.05, mordents=0.5, rng=rng)
    # La tornada, al sacabutx: lenta, pomposa, i la darrera nota que rellisca avall.
    for c, e, nota, dur in notes((3,)):
        cau = 3 if (c, e) == (31, 3) else 0
        p.posa(sacabutx(midi(nota - 12), dur * CORXERA * 0.9 + (0.5 if cau else 0), cau=cau), quan(c, e), pan=0.15, vol=0.12)
    melodia(p, flauta, (3,), pan=0.4, vol=0.025, octava=1, staccato=0.1)
    return reverb(p.lr, durada=0.7, cua=2.0, humit=0.2, rng=rng, fosc=6000)


def claustre():
    """El claustre i l'apotecaria: tranquil·la, amb una mica de misteri. Flauta, llaüt a poc a poc, gotes de les
    teulades, i la Gueraula que canta la corranda sense saber què vol dir."""
    rng = np.random.default_rng(4)
    p = Pista(DURADA)
    bordo_roda(p, 0.02, notes=(50, 57), rng=rng, roda=0.5)
    arpegis(p, 0.065, cada=1, brillo=0.4, pan=-0.3)
    acords(p, lambda f, d: cor(f, d, 'u'), 0.03, octava=-1, atac=2.0, veus=(0, 2))
    for c in (0, 24):
        p.posa(campana(midi(45), 8.0), quan(c, 0), pan=0.6, vol=0.035)
    for c in range(COMPASSOS):
        _, veus = acord(c)
        for _ in range(2):
            p.posa(gota(midi(veus[int(rng.integers(0, 4))] + 24)), quan(c, int(rng.integers(0, 6))), pan=rng.uniform(-0.8, 0.8), vol=0.018)
    melodia(p, flauta, (1,), pan=0.2, vol=0.085, eco=0.25, legato=0.5)
    melodia(p, lambda f, d: veu(f, d, 'af', puja=True), (2,), pan=0.1, vol=0.075, legato=0.3)
    melodia(p, lambda f, d: llaut(f, d + 1.0, 0.85), (3,), pan=0.25, vol=0.08)
    melodia(p, flauta, (4,), pan=0.2, vol=0.09, eco=0.2, legato=0.5)
    melodia(p, lambda f, d: veu(f, d, 'af'), (4,), pan=0.1, vol=0.035, versos=(2, 3), legato=0.3)
    return reverb(p.lr, durada=2.0, cua=5.5, humit=0.5, rng=rng, fosc=4000)


def preparacio():
    """La bugaderia: enjogassada, fer de monjos. Llaüt «um-pa», flauta amb mordents, i un cor de monjos de mentida
    que canta la corranda, massa solemne i arrossegant les notes."""
    rng = np.random.default_rng(5)
    p = Pista(DURADA)
    bordo_roda(p, 0.02, notes=(50, 57), rng=rng)
    for c in range(COMPASSOS):
        b, veus = acord(c)
        # «Um-pa-pa um-pa-pa», a pizzicato.
        p.posa(pizzicato(midi(b + 12)), quan(c, 0), pan=-0.2, vol=0.16)
        p.posa(pizzicato(midi(b + 19)), quan(c, 3), pan=-0.2, vol=0.12)
        for e in (1, 2, 4, 5):
            for j, v in enumerate(veus[1:]):
                p.posa(pizzicato(midi(v), 0.25), quan(c, e) + 0.006 * j, pan=0.25, vol=0.035 if e in (2, 5) else 0.025)
        p.posa(pell(rng, 100, 0.8), quan(c, 0), vol=0.14)
        p.posa(tec(rng), quan(c, 5), pan=0.3, vol=0.05)
        if c % 4 == 3:
            p.posa(bloc(1200), quan(c, 4), pan=0.5, vol=0.05)
            p.posa(bloc(900), quan(c, 5), pan=0.5, vol=0.05)
    melodia(p, flauta, (1, 3, 4), pan=0.25, vol=0.09, legato=0.0, staccato=None, mordents=0.6, rng=rng)
    # Els monjos de mentida: la corranda una octava avall, solemne, entrant per sota de cada nota.
    melodia(p, lambda f, d: cor(f, d, 'o') * 0.5 + veu(f, d, 'o', puja=True), (2,), pan=-0.1, vol=0.07, octava=-1, legato=0.15)
    melodia(p, flauta, (2,), pan=0.4, vol=0.04, octava=1, staccato=0.1)
    # A la darrera estrofa, el cor s'hi torna a ficar al darrer vers.
    melodia(p, lambda f, d: veu(f, d, 'o', puja=True), (4,), pan=-0.1, vol=0.05, octava=-1, versos=(3,), legato=0.15)
    # La tornada, en terceres: el llaüt brillant per sota de la flauta.
    for c, e, nota, dur in notes((3,)):
        p.posa(llaut(midi(grau(nota, -2)), dur * CORXERA + 0.6, 0.8), quan(c, e), pan=-0.3, vol=0.06)
    return reverb(p.lr, durada=0.9, cua=2.5, humit=0.25, rng=rng, fosc=5000)


def nit():
    """La porteria i la cuina: sigil·losa i còmica. Pizzicato de puntetes, passes, el sacabutx que fa «pom», la
    corranda a pessics, i en acabar cada estrofa el sacabutx rellisca («ui!»)."""
    rng = np.random.default_rng(6)
    p = Pista(DURADA)
    bordo_roda(p, 0.012, notes=(38, 45), rng=rng, roda=0.5)
    for c in range(COMPASSOS):
        b, veus = acord(c)
        p.posa(sacabutx(midi(b), 0.22), quan(c, 0), vol=0.13)
        p.posa(pizzicato(midi(b + 19), 0.3), quan(c, 3), pan=-0.3, vol=0.1)
        p.posa(pizzicato(midi(veus[1]), 0.3), quan(c, 2), pan=0.3, vol=0.05)
        p.posa(pizzicato(midi(veus[2]), 0.3), quan(c, 5), pan=0.3, vol=0.05)
        # Les passes de puntetes, a cada temps, d'un costat a l'altre.
        for k, e in enumerate((0, 3)):
            p.posa(passa(rng), quan(c, e) + 0.02, pan=-0.5 if (2 * c + k) % 2 else 0.5, vol=0.12)
        if c % 8 == 7 and 8 <= c < 40:
            p.posa(sacabutx(midi(b + 12), 0.9, cau=5), quan(c, 3), pan=0.2, vol=0.09)
            p.posa(bloc(700), quan(c, 5), pan=0.5, vol=0.06)
    melodia(p, lambda f, d: pizzicato(f, 0.4), (1, 4), pan=0.15, vol=0.13, staccato=0.4)
    melodia(p, lambda f, d: flauta(f, d) * env(d, 0.01, 0.05, 0.25), (2, 4), pan=0.25, vol=0.07, staccato=0.3)
    # La tornada, al sacabutx (de puntetes, si pot), amb la flauta que hi fa l'eco.
    for c, e, nota, dur in notes((3,)):
        p.posa(sacabutx(midi(nota - 12), min(dur * CORXERA * 0.6, 0.5)), quan(c, e), pan=-0.1, vol=0.11)
    melodia(p, lambda f, d: flauta(f, 0.15), (3,), pan=0.45, vol=0.03, octava=1, staccato=0.15, versos=(1, 3))
    # Entrada i coda: la cuina, el foc i algú que ronca (dues notes de sacabutx, lentes).
    for c in (2, 6, 42, 46):
        p.posa(sacabutx(midi(38), 1.2) * env(1.2, 0.4, 0.4), quan(c, 0), pan=0.5, vol=0.05)
        p.posa(sacabutx(midi(45), 0.9, cau=2) * env(0.9, 0.3, 0.4), quan(c, 4), pan=0.5, vol=0.04)
    return reverb(p.lr, durada=1.2, cua=3.0, humit=0.35, rng=rng, fosc=3500)


def arxiu():
    """L'scriptorium i l'arxiu: tensió baixa. Bordó greu, un cor que murmura, campana llunyana, el pandero que batega
    com un cor, i la corranda a trossos."""
    rng = np.random.default_rng(7)
    p = Pista(DURADA)
    bordo_roda(p, 0.045, notes=(26, 38, 45), rng=rng, roda=1.5)
    acords(p, lambda f, d: cor(f, d, 'u'), 0.05, octava=-1, atac=3.0, veus=(0, 1))
    for c in range(0, COMPASSOS, 4):
        p.posa(campana(midi(43), 9.0), quan(c, 0) + 0.5, pan=0.6, vol=0.03)
    for c in range(COMPASSOS):
        if 8 <= c < 40:
            p.posa(pell(rng, 60), quan(c, 0), pan=-0.1, vol=0.14)
            p.posa(pell(rng, 60, 0.6), quan(c, 1), pan=-0.1, vol=0.1)
        elif c % 2 == 0:
            p.posa(pell(rng, 55), quan(c, 0), pan=-0.1, vol=0.1)
    # La flauta: només el primer i el tercer vers, greus i amb eco.
    melodia(p, flauta, (1, 4), pan=0.2, vol=0.08, eco=0.35, legato=0.4, versos=(0, 2), octava=-1)
    melodia(p, viola_roda, (2,), pan=-0.2, vol=0.035, versos=(1, 3), octava=-1, legato=0.2)
    # La tornada: el llaüt, només les notes del temps fort.
    for c, e, nota, dur in notes((3,)):
        if e in (0, 3):
            p.posa(llaut(midi(nota - 12), 2.0, 0.35), quan(c, e), pan=-0.3, vol=0.08)
    vent(p, rng, 0.006, fosc=1200, rafegues=3)
    return reverb(p.lr, durada=2.6, cua=7.0, humit=0.6, rng=rng, fosc=2800)


def fugida():
    """El molí: ràpida. Tabals a corxeres, la gossa que brunz a cada corxera, el llaüt a semicorxeres, la corranda a
    la viola de roda i a la flauta alhora, i la roda del molí que grinyola."""
    rng = np.random.default_rng(8)
    p = Pista(DURADA)
    bordo_roda(p, 0.04, notes=(38, 50, 57), rng=rng, roda=1.5)
    arpegis(p, 0.035, semicorxeres=True, brillo=0.65, pan=0.35)
    for c in range(COMPASSOS):
        b, _ = acord(c)
        for e in range(6):
            p.posa(pell(rng, 85 if e in (0, 3) else 130, 1.0 if e in (0, 3) else 0.35), quan(c, e), vol=0.14)
            p.posa(gossa(), quan(c, e), pan=-0.25, vol=0.04 if e in (0, 3) else 0.025)
            if e not in (0, 3):
                p.posa(pandereta(rng, 0.12), quan(c, e), pan=0.5, vol=0.02)
        p.posa(sacabutx(midi(b), TEMPS * 0.7), quan(c, 0), vol=0.09)
        p.posa(sacabutx(midi(b), TEMPS * 0.7), quan(c, 3), vol=0.07)
        if c % 2 == 0:
            p.posa(grinyol(), quan(c, 2), pan=0.6, vol=0.03)
        if c % 8 == 7:
            for k in range(6):
                p.posa(pell(rng, 140, 0.3 + 0.1 * k, 0.2), quan(c, 3 + k / 2), pan=0.2, vol=0.12)
    for c, e, nota, dur in notes((1,), versos=(0, 1)):
        p.posa(viola_roda(midi(nota), dur * CORXERA), quan(c - 4, e), pan=-0.1, vol=0.07)
    melodia(p, viola_roda, (1, 2, 3, 4), pan=-0.1, vol=0.08, legato=0.0)
    melodia(p, flauta, (2, 3, 4), pan=0.25, vol=0.06, octava=1, legato=0.0, mordents=0.4, rng=rng)
    aigua(p, rng, 0.01)
    return reverb(p.lr, durada=0.8, cua=2.0, humit=0.2, rng=rng, fosc=5500)


def mati():
    """El matí de l'acte 4 i el judici: solemne i esperançada. Campanes, el cor sostingut, el pandero lent, la flauta
    i la viola de roda, i els ocells, que han tornat després de la tempesta."""
    rng = np.random.default_rng(9)
    p = Pista(DURADA)
    bordo_roda(p, 0.03, notes=(38, 50, 57), rng=rng, roda=0.6)
    acords(p, lambda f, d: cor(f, d, 'a'), 0.04, atac=1.2, veus=(0, 1, 2, 3), octava=-1)
    for c, (nota, retard) in [(0, (62, 0.0)), (0, (57, 1.2)), (0, (50, 2.0)), (24, (62, 0.0)), (24, (57, 1.0))]:
        p.posa(campana(midi(nota), 9.0), quan(c, 0) + retard, pan=0.5 - 0.3 * (nota % 3), vol=0.045)
    for c in range(COMPASSOS):
        b, _ = acord(c)
        p.posa(pell(rng, 70), quan(c, 0), vol=0.15)
        if c % 2 == 1:
            p.posa(pell(rng, 85, 0.5), quan(c, 3), vol=0.1)
    arpegis(p, 0.035, compassos=seccio(0, 3, 5), cada=3, brillo=0.6)
    melodia(p, flauta, (1,), pan=0.2, vol=0.085, legato=0.45, eco=0.2)
    melodia(p, viola_roda, (2,), pan=-0.15, vol=0.08, legato=0.15)
    melodia(p, flauta, (3,), pan=0.25, vol=0.09, legato=0.45)
    for c, e, nota, dur in notes((3,)):
        p.posa(viola_roda(midi(grau(nota, -2)), dur * CORXERA + 0.15), quan(c, e), pan=-0.25, vol=0.05)
    melodia(p, lambda f, d: cor(f, d, 'a'), (4,), pan=0.0, vol=0.08, octava=-1, legato=0.3)
    melodia(p, flauta, (4,), pan=0.3, vol=0.06, legato=0.45, octava=1)
    ocells(p, rng, 0.012, 14)
    return reverb(p.lr, durada=2.0, cua=5.5, humit=0.45, rng=rng, fosc=5000)


def final():
    """L'epíleg i els crèdits: la corranda en Re major, lluminosa. Campanes, la giga de tabal i pandereta, el llaüt,
    la flauta de festa i la viola de roda, i el cor a la darrera estrofa."""
    rng = np.random.default_rng(10)
    p = Pista(DURADA)
    bordo_roda(p, 0.03, notes=(38, 50, 57), rng=rng)
    for nota, retard in ((74, 0.0), (69, 0.6), (66, 1.2), (62, 1.8)):
        p.posa(campana(midi(nota), 6.0), quan(0, 0) + retard, pan=0.4, vol=0.03)
    arpegis(p, 0.045, major=True, brillo=0.65, pan=-0.3)
    for c in range(COMPASSOS):
        p.posa(pell(rng, 90), quan(c, 0), vol=0.16)
        p.posa(pell(rng, 90, 0.6), quan(c, 3), vol=0.12)
        if c >= 8:
            for e in (2, 5):
                p.posa(pandereta(rng, 0.15), quan(c, e), pan=0.5, vol=0.025)
            p.posa(pandereta(rng, 0.4), quan(c, 0), pan=0.5, vol=0.035)
        for e in (0, 3):
            p.posa(gossa(), quan(c, e), pan=-0.2, vol=0.025)
    acords(p, lambda f, d: cor(f, d, 'a'), 0.03, compassos=seccio(3, 4, 5), major=True, octava=-1, atac=1.0)
    for c, e, nota, dur in notes((1,), major=True, versos=(0, 1)):
        p.posa(flauta(midi(nota + 12), dur * CORXERA + 0.3), quan(c - 4, e), pan=0.3, vol=0.06)
    melodia(p, flauta, (1, 2, 4), pan=0.25, vol=0.09, major=True, legato=0.2, mordents=0.4, rng=rng)
    melodia(p, viola_roda, (2, 3), pan=-0.15, vol=0.07, major=True, legato=0.1)
    melodia(p, flauta, (3,), pan=0.25, vol=0.08, major=True, legato=0.2, octava=1)
    melodia(p, lambda f, d: cor(f, d, 'a'), (4,), pan=0.0, vol=0.06, major=True, octava=-1, legato=0.3)
    # Coda: el llaüt brillant recorda els primers versos.
    for c, e, nota, dur in notes((1,), major=True, versos=(0, 1, 2)):
        p.posa(llaut(midi(nota + 12), 1.5, 0.85), quan(c + 32, e), pan=0.3, vol=0.06)
    ocells(p, rng, 0.014, 16)
    return reverb(p.lr, durada=1.6, cua=4.5, humit=0.4, rng=rng, fosc=6000)


# ─── Sortida ────────────────────────────────────────────────────────────────

MUSICA = {
    'tema': tema, 'tempesta': tempesta, 'poble': poble, 'claustre': claustre, 'preparacio': preparacio,
    'nit': nit, 'arxiu': arxiu, 'fugida': fugida, 'mati': mati, 'final': final,
}

# Volum eficaç (RMS) de cada peça: fluix, que és ambient sota els diàlegs (més fluix que els efectes).
RMS = 0.06
# Les peces amb ritme (tabals, pizzicato) s'hi senten més amb el mateix RMS: una mica més avall.
RMS_PECA = {'poble': 0.052, 'fugida': 0.05, 'preparacio': 0.054, 'nit': 0.054, 'tempesta': 0.055, 'final': 0.055}
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
