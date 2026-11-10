#!/usr/bin/env python3
"""
`npm run musica`: genera la música d'ambient de cada espai a `game/audio/music/` (.ogg, estèreo).

- `fabrica`: la fàbrica de ferro-9 (l'Iri). Re menor, 72 ppm: un pols de màquina llunyà, un baix
  que no para, acords de metall calent i, a la segona meitat, una melodia de campanes de tub.
- `gavina`: La Gavina, la presó en òrbita (la Vet). La menor, sense ritme: acords freds que
  s'obren a poc a poc, gotes de vidre a l'atzar, el brunzit del suport vital i l'aire dels conductes.

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
        # Serra suavitzada: els harmònics més aguts sense soroll d'aliàsing.
        return sum(np.sin(k * ph) / k for k in range(1, 12)) * (2 / np.pi)
    raise ValueError(shape)


def band(x, lo=None, hi=None):
    spec = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    mask = np.ones_like(f)
    if lo:
        mask *= 1 / (1 + (lo / np.maximum(f, 1)) ** 4)
    if hi:
        mask *= 1 / (1 + (f / hi) ** 4)
    return np.fft.irfft(spec * mask, len(x))


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


# ─── La fàbrica ─────────────────────────────────────────────────────────────

FAB_PPM = 72
FAB_TEMPS = 60 / FAB_PPM
FAB_COMPAS = 4 * FAB_TEMPS

# Un acord cada dos compassos (24 compassos, 80 s). Notes MIDI: baix + veus.
FAB_ACORDS = [
    (38, [62, 65, 69]),      # Re m
    (34, [62, 65, 70]),      # Si♭
    (41, [60, 65, 69]),      # Fa
    (36, [60, 64, 67]),      # Do
    (38, [62, 65, 69]),      # Re m
    (34, [62, 65, 70]),      # Si♭
    (43, [62, 67, 70]),      # Sol m
    (45, [61, 64, 69]),      # La
    (38, [62, 65, 69]),      # Re m
    (41, [60, 65, 69]),      # Fa
    (43, [62, 67, 70]),      # Sol m
    (45, [61, 64, 69]),      # La
]

# (compàs, temps, nota, durada en temps). Silenci els primers 8 compassos: la sala respira.
FAB_MELODIA = [
    (8, 0, 81, 2), (8, 2, 79, 1), (8, 3, 77, 1),
    (9, 0, 74, 4),
    (10, 0, 77, 2), (10, 2, 74, 2),
    (11, 0, 70, 1.5), (11, 1.5, 72, 0.5), (11, 2, 74, 2),
    (12, 0, 79, 3), (12, 3, 77, 1),
    (13, 0, 74, 2), (13, 2, 70, 2),
    (14, 0, 69, 1), (14, 1, 73, 1), (14, 2, 76, 2),
    (15, 0, 79, 2), (15, 2, 76, 2),
    (16, 0, 77, 3), (16, 3, 76, 1),
    (17, 0, 74, 4),
    (18, 0, 72, 2), (18, 2, 69, 2),
    (19, 0, 72, 1), (19, 1, 74, 1), (19, 2, 77, 2),
    (20, 0, 79, 2), (20, 2, 82, 1), (20, 3, 81, 1),
    (21, 0, 79, 2), (21, 2, 74, 2),
    (22, 0, 76, 2), (22, 2, 73, 2),
    (23, 0, 69, 4),
]


def campana_tub(f, d=3.0):
    """Campana de tub: parcials gairebé harmònics que s'apaguen de pressa els aguts."""
    parts = [(1, 1.0, 1.8), (2.0, 0.5, 0.9), (3.01, 0.3, 0.5), (4.07, 0.2, 0.25), (5.2, 0.1, 0.12)]
    return sum(a * osc(f * r, d) * env(d, 0.004, 0.3, dec) for r, a, dec in parts)


def cop_maquina(fort):
    """El pols de la fàbrica: un cop sord, de lluny, amb una mica de ferro."""
    d = 0.5
    x = t(d)
    cos = osc(60 * (1 - 0.25 * np.minimum(1, x / 0.12)), d) * env(d, 0.003, 0.05, 0.14)
    rng = np.random.default_rng(int(fort * 100))
    aire = band(rng.uniform(-1, 1, len(x)), 60, 300) * env(d, 0.002, 0.05, 0.05)
    return fort * (cos + 0.6 * aire)


def clanc(f=180):
    d = 1.2
    return sum(a * osc(f * r, d) * env(d, 0.001, 0.2, dec) for r, a, dec in
               [(1, 0.5, 0.4), (2.71, 0.4, 0.25), (5.13, 0.3, 0.12), (8.27, 0.2, 0.06)])


def vapor(rng):
    d = 2.5
    return band(rng.uniform(-1, 1, int(SR * d)), 1800, 6000) * env(d, 0.6, 1.2) * np.linspace(1, 0.4, int(SR * d))


def fabrica():
    rng = np.random.default_rng(9)
    p = Pista(len(FAB_ACORDS) * 2 * FAB_COMPAS)

    # Acords: serres desafinades, filtrades amb una obertura que va i ve (dues voltes per bucle).
    pad = Pista(p.durada)
    llarg = 2 * FAB_COMPAS
    for i, (baix, veus) in enumerate(FAB_ACORDS):
        inici = i * llarg
        d = llarg + 1.5
        for j, v in enumerate(veus):
            for des, costat in ((-0.0012, -0.4), (0.0012, 0.4)):
                pan = costat + 0.25 * (j - 1)
                pad.posa(osc(midi(v) * (1 + des), d, 'saw') * env(d, 1.2, 1.5), inici, pan=pan, vol=0.16)
        # El baix: sinusoide amb una mica de serra, que entra suau.
        b = osc(midi(baix), d) + 0.25 * osc(midi(baix), d, 'saw')
        p.posa(b * env(d, 0.3, 1.5), inici, vol=0.35)
    obre = p.lfo(2, -np.pi / 2)
    for ch in range(2):
        tancat = band(pad.lr[ch], 80, 500)
        obert = band(pad.lr[ch], 80, 1500)
        p.lr[ch] += tancat * (1 - obre) + obert * obre

    # El brunzit de la fàbrica: un re greu que no s'atura mai.
    drone = osc(midi(26), p.durada) + 0.3 * osc(midi(38), p.durada) + 0.1 * osc(midi(26) * 3.003, p.durada)
    p.posa(drone * (0.7 + 0.3 * p.lfo(3)), 0, vol=0.12)

    # Les màquines: un cop a cada temps (més fort al primer), un clanc a la contra cada dos compassos
    # i una alenada de vapor cada quatre.
    compassos = len(FAB_ACORDS) * 2
    for c in range(compassos):
        for b in range(4):
            p.posa(cop_maquina(1.0 if b == 0 else 0.45), (c * 4 + b) * FAB_TEMPS, vol=0.55)
        if c % 2 == 1:
            p.posa(clanc(180 if c % 4 == 1 else 151), (c * 4 + 3.5) * FAB_TEMPS, pan=0.6 if c % 4 == 1 else -0.6, vol=0.10)
        if c % 4 == 2:
            p.posa(vapor(rng), (c * 4 + 2) * FAB_TEMPS, pan=-0.7, vol=0.06)

    # La melodia: campanes de tub, una mica a la dreta.
    for c, b, nota, dur in FAB_MELODIA:
        d = max(3.0, dur * FAB_TEMPS + 2)
        p.posa(campana_tub(midi(nota), d), (c * 4 + b) * FAB_TEMPS, pan=0.25, vol=0.20)
        # I el seu eco a l'altre costat, un temps i mig més tard i més fluix.
        p.posa(campana_tub(midi(nota), d), (c * 4 + b + 1.5) * FAB_TEMPS, pan=-0.5, vol=0.06)

    return reverb(p.lr, durada=0.6, cua=3.0, humit=0.35, rng=rng, fosc=3500)


# ─── La Gavina ──────────────────────────────────────────────────────────────

GAV_ACORD = 16.0  # segons per acord: quatre acords, 64 s
GAV_ACORDS = [
    [45, 52, 57, 59, 60, 64],  # La m (add9)
    [41, 53, 57, 60, 64, 71],  # Fa maj7 (#11)
    [36, 55, 59, 62, 64, 67],  # Do maj9
    [40, 55, 59, 62, 66, 67],  # Mi m9
]


def veu_pad(f, d, rng):
    """Tres sinusoides gairebé a l'uníson (un cor fred) i l'octava, molt fluixa."""
    x = sum(osc(f * 2 ** (c / 1200), d, phase=rng.uniform(0, 6.28)) for c in (-5, 0, 5)) / 3
    return x + 0.08 * osc(f * 2, d) + 0.03 * osc(f * 3, d)


def vidre(f, d=4.0):
    return (osc(f, d) * env(d, 0.003, 0.5, 1.6)
            + 0.25 * osc(f * 2.76, d) * env(d, 0.002, 0.3, 0.3)
            + 0.08 * osc(f * 5.4, d) * env(d, 0.001, 0.2, 0.08))


def gavina():
    rng = np.random.default_rng(1609)
    p = Pista(len(GAV_ACORDS) * GAV_ACORD)

    # Acords: entren a poc a poc (6 s) i se'n van encara més a poc a poc, damunt del següent.
    for i, veus in enumerate(GAV_ACORDS):
        inici = i * GAV_ACORD
        d = GAV_ACORD + 7
        for j, v in enumerate(veus):
            pan = -0.6 + 1.2 * j / (len(veus) - 1)
            vol = 0.22 if j == 0 else 0.13
            p.posa(veu_pad(midi(v), d, rng) * env(d, 6.0, 7.0), inici + 0.4 * j, pan=pan, vol=vol)

    # Les veus pugen i baixen de brillantor amb una ona lenta per a cada canal.
    for ch, fase in ((0, 0.0), (1, 2.0)):
        brill = band(p.lr[ch], 900, None)
        p.lr[ch] += 0.6 * brill * p.lfo(3, fase)

    # Gotes de vidre: notes de l'acord que sona, a l'atzar però sempre les mateixes.
    temps = 1.5
    while temps < p.durada:
        acord = GAV_ACORDS[int(temps // GAV_ACORD) % len(GAV_ACORDS)]
        nota = rng.choice([v for v in acord[1:]]) + rng.choice([12, 24])
        p.posa(vidre(midi(nota)), temps, pan=rng.uniform(-0.8, 0.8), vol=rng.uniform(0.05, 0.11))
        temps += rng.uniform(2.5, 6.5)

    # El suport vital: un brunzit a 50 Hz que respira, i l'aire dels conductes.
    hum = osc(50, p.durada) + 0.5 * osc(100, p.durada) + 0.2 * osc(150.3, p.durada)
    p.posa(hum * (0.6 + 0.4 * p.lfo(4)), 0, vol=0.06)
    for ch, fase in ((0, 0.0), (1, 1.3)):
        aire = band(p.soroll(rng), 150, 900)
        p.lr[ch] += 0.05 * aire * (0.3 + 0.7 * p.lfo(8, fase))

    # Un sonar, de molt lluny, cada 32 s.
    for s in (8.0, 40.0):
        d = 2.0
        ping = osc(1318.5, d) * env(d, 0.002, 0.5, 0.35) + 0.3 * osc(1318.5 * 2.01, d) * env(d, 0.002, 0.3, 0.1)
        p.posa(ping, s, pan=0.7 if s < 20 else -0.7, vol=0.05)

    return reverb(p.lr, durada=2.2, cua=7.0, humit=0.8, rng=rng, fosc=6000)


# ─── Sortida ────────────────────────────────────────────────────────────────

MUSICA = {'fabrica': fabrica, 'gavina': gavina}

# Volum eficaç (RMS) de cada peça: fluix, que és ambient i no ha de tapar les veus ni els sons.
RMS = {'fabrica': 0.09, 'gavina': 0.08}


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
    print(f'  {name}: {lr.shape[1] / SR:.0f} s')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    only = set(sys.argv[1:])
    for name, make in MUSICA.items():
        if not only or name in only:
            write(name, make())
    print(f'✔ música a {OUT}')


if __name__ == '__main__':
    main()
