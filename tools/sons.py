#!/usr/bin/env python3
"""
`npm run sons`: genera els efectes de so del joc a `game/audio/sfx/` (.ogg).

Tot és sintetitzat (ones i soroll), sense mostres de fora: es pot tornar a generar sempre igual.
Per canviar un so per un de fet a mà, n'hi ha prou de posar el fitxer amb el mateix nom a
`game/audio/sfx/` i treure'l de la llista `SONS` d'aquí baix (si no, el sobreescriuria).

Són provisionals: es refaran a la fase de so (un per a cada marca [SO: nom] del guió, que dura el que
dura l'acció).

Cal python3 amb numpy, i ffmpeg.
"""
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np

SR = 44100
OUT = Path(__file__).resolve().parent.parent / 'game' / 'audio' / 'sfx'
rng = np.random.default_rng(9)  # sempre els mateixos sons

# ─── Eines ──────────────────────────────────────────────────────────────────


def t(d):
    return np.arange(int(SR * d)) / SR


def silence(d):
    return np.zeros(int(SR * d))


def noise(d):
    return rng.uniform(-1, 1, int(SR * d))


def env(d, attack=0.005, decay=None, release=0.02):
    """Atac lineal, caiguda exponencial (temps fins a 1/e) i un final suau sense clics."""
    x = t(d)
    e = np.minimum(1, x / max(attack, 1e-4))
    if decay:
        e = e * np.exp(-x / decay)
    n = int(SR * release)
    if n and len(e) > n:
        e[-n:] *= np.linspace(1, 0, n)
    return e


def osc(freq, d, shape='sine', phase=0.0):
    """`freq` pot ser un número o un vector (glissando)."""
    f = np.asarray(freq, dtype=float)
    f = f if f.ndim else np.broadcast_to(f, (int(SR * d),))
    ph = 2 * np.pi * np.cumsum(f) / SR + phase
    if shape == 'sine':
        return np.sin(ph)
    if shape == 'square':
        return np.tanh(4 * np.sin(ph))  # quadrada arrodonida, menys aspra
    if shape == 'saw':
        return 2 * ((ph / (2 * np.pi)) % 1) - 1
    raise ValueError(shape)


def band(x, lo=None, hi=None):
    """Filtre pas-banda (o pas-baix / pas-alt) amb la FFT, amb vores suaus."""
    spec = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    mask = np.ones_like(f)
    if lo:
        mask *= 1 / (1 + (lo / np.maximum(f, 1)) ** 4)
    if hi:
        mask *= 1 / (1 + (f / hi) ** 4)
    return np.fft.irfft(spec * mask, len(x))


def mix(*parts):
    """Suma sons de llargades diferents; cada part és `(so, inici_en_segons)` o un so."""
    parts = [p if isinstance(p, tuple) else (p, 0.0) for p in parts]
    n = max(int(SR * s) + len(x) for x, s in parts)
    out = np.zeros(n)
    for x, s in parts:
        i = int(SR * s)
        out[i:i + len(x)] += x
    return out


def seq(*parts, gap=0.0):
    out = []
    for p in parts:
        out += [p, silence(gap)]
    return np.concatenate(out[:-1])


def semis(f, n):
    return f * 2 ** (n / 12)


# ─── Sons de Suma Zero ──────────────────────────────────────────────────────


def clic(f=2400, d=0.03):
    return band(noise(d), f * 0.5, f * 2) * env(d, 0.001, 0.008)


def teclat():
    """Algú que tecleja de pressa: una ràfega de tecles."""
    parts = [(clic(1800 + rng.uniform(-400, 400)) * rng.uniform(0.5, 1.0), i * 0.07 + rng.uniform(0, 0.03)) for i in range(14)]
    return mix(*parts)


def miol():
    """Un gat: miau (glissando amb formants)."""
    d = 0.7
    n = int(SR * d)
    f = np.concatenate([np.linspace(500, 820, int(SR * 0.25)), np.linspace(820, 420, n - int(SR * 0.25))])
    v = osc(f, d, 'saw') * 0.6 + osc(f * 2, d) * 0.3
    return band(v, 400, 3000) * env(d, 0.05, None, 0.15)


def mossegada():
    """Unes dents petites contra un cable: dos cruixits."""
    c = lambda: band(noise(0.06), 1500, 6000) * env(0.06, 0.001, 0.015)
    return mix(c(), (c() * 0.8, 0.12), (osc(220, 0.05) * env(0.05, 0.001, 0.02) * 0.3, 0.12))


def passaplats():
    """La porteta del passaplats: fusta que llisca i un toc."""
    llisca = band(noise(0.35), 200, 1500) * env(0.35, 0.05, None, 0.1) * 0.5
    toc = osc(np.linspace(180, 120, int(SR * 0.12)), 0.12) * env(0.12, 0.001, 0.03)
    return mix(llisca, (toc, 0.33))


def router():
    """El router s'encén: tres notes que pugen."""
    nota = lambda f: osc(f, 0.12, 'square') * env(0.12, 0.002, 0.06) * 0.5
    return seq(nota(660), nota(880), nota(1320), gap=0.05)


def nevera():
    """La porta de la nevera: la junta que desenganxa i el brunzit."""
    junta = band(noise(0.12), 300, 2000) * env(0.12, 0.002, 0.03)
    brunzit = osc(100, 0.8) * 0.15 * env(0.8, 0.1, None, 0.3)
    return mix(junta, (brunzit, 0.05))


def porta_pis():
    """Les claus i la porta del pis que es tanca."""
    claus = mix(*[(band(noise(0.04), 4000, 9000) * env(0.04, 0.001, 0.01) * 0.6, i * 0.06) for i in range(5)])
    cop = osc(np.linspace(90, 60, int(SR * 0.25)), 0.25) * env(0.25, 0.001, 0.07)
    return mix(claus, (cop, 0.4), (clic(1200) * 0.6, 0.45))


def vaporitzador():
    """El vaporitzador de la cafetera escumant la llet."""
    d = 1.2
    return band(noise(d), 2000, 9000) * env(d, 0.08, None, 0.3) * (0.7 + 0.3 * osc(7, d))


def pany_clic():
    """Un pany intel·ligent: un bip de l'aplicació i el pestell que salta."""
    bip = osc(1760, 0.09) * env(0.09, 0.002, 0.04) * 0.5
    return mix(bip, (bip * 0.8, 0.12), (clic(900, 0.05), 0.3))


def telefon_bar():
    """Un telèfon de paret antic que sona."""
    d = 0.9
    ring = (osc(440, d) + osc(480, d)) * (osc(18, d, 'square') * 0.5 + 0.5)
    return ring * env(d, 0.01, None, 0.1) * 0.5


def porta_bar():
    """La porta del bar, amb la campaneta."""
    campana = (osc(2100, 1.0) + 0.5 * osc(3150, 1.0)) * env(1.0, 0.001, 0.25) * 0.4
    return mix(campana, (osc(np.linspace(100, 70, int(SR * 0.2)), 0.2) * env(0.2, 0.001, 0.06), 0.15))


def megafonia():
    """El ding-dong de la megafonia de l'aeroport."""
    nota = lambda f: (osc(f, 0.7) + 0.3 * osc(f * 2, 0.7)) * env(0.7, 0.005, 0.3)
    return mix(nota(784), (nota(622), 0.45))


def teclat_porta():
    """Quatre tecles d'un teclat numèric i el pestell elèctric."""
    tecla = lambda f: osc(f, 0.08) * env(0.08, 0.002, 0.03) * 0.5
    return mix(*[(tecla(f), i * 0.18) for i, f in enumerate((1209, 1336, 1477, 1209))], (clic(700, 0.06), 0.85))


def alarma_porta():
    """La porta de personal que xiula: un codi incorrecte."""
    bip = osc(2600, 0.12, 'square') * env(0.12, 0.002, None, 0.02) * 0.5
    return seq(bip, bip, bip, gap=0.06)


def plor():
    """La Vet plorant de mentida: un «buaaa» exagerat."""
    d = 1.1
    f = 330 + 60 * osc(5, d) + np.linspace(40, -60, int(SR * d))
    v = osc(f, d, 'saw')
    return band(v, 300, 2500) * env(d, 0.08, None, 0.3)


def impressora():
    """Una impressora làser que arrenca, rumia i treu fulls."""
    d = 1.4
    motor = band(noise(d), 150, 900) * 0.4 + osc(120, d, 'saw') * 0.1
    return motor * env(d, 0.1, None, 0.2) * (0.8 + 0.2 * osc(3, d))


def auricular():
    """Un auricular que es treu i es posa: frec i clic de plàstic."""
    frec = band(noise(0.15), 1000, 5000) * env(0.15, 0.02, 0.05) * 0.4
    return mix(frec, (clic(3000, 0.03), 0.15))


# ─── Llista ─────────────────────────────────────────────────────────────────

SONS = {
    'teclat': teclat, 'miol': miol, 'mossegada': mossegada, 'passaplats': passaplats, 'router': router,
    'nevera': nevera, 'porta_pis': porta_pis, 'vaporitzador': vaporitzador, 'pany_clic': pany_clic,
    'telefon_bar': telefon_bar, 'porta_bar': porta_bar, 'megafonia': megafonia, 'teclat_porta': teclat_porta,
    'alarma_porta': alarma_porta, 'plor': plor, 'impressora': impressora, 'auricular': auricular,
}

# Volum de cada so respecte del màxim.
VOLUM = {'alarma_porta': 0.5, 'telefon_bar': 0.6, 'vaporitzador': 0.5, 'impressora': 0.6, 'teclat': 0.6}


def write(name, x):
    x = x / max(1e-9, np.max(np.abs(x))) * 0.8 * VOLUM.get(name, 1.0)
    pcm = (np.clip(x, -1, 1) * 32767).astype('<i2')
    with tempfile.NamedTemporaryFile(suffix='.wav') as tmp:
        with wave.open(tmp.name, 'wb') as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(pcm.tobytes())
        subprocess.run(
            ['ffmpeg', '-loglevel', 'error', '-y', '-i', tmp.name, '-c:a', 'libvorbis', '-q:a', '5', str(OUT / f'{name}.ogg')],
            check=True,
        )


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    only = set(sys.argv[1:])
    for name, make in SONS.items():
        if only and name not in only:
            continue
        write(name, make())
    print(f'✔ {len(only) or len(SONS)} sons a {OUT}')


if __name__ == '__main__':
    main()
