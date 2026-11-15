#!/usr/bin/env python3
"""
`npm run sons`: genera els efectes de so d'Aigua Verne a `game/audio/sfx/` (.ogg).

Tot és sintetitzat (ones i soroll), sense mostres de fora: es pot tornar a generar sempre igual.
Per canviar un so per un de fet a mà, n'hi ha prou de posar el fitxer amb el mateix nom a
`game/audio/sfx/` i treure'l de la llista `SONS` d'aquí baix (si no, el sobreescriuria).

Hi ha dues menes de sons:
- els efectes (`SONS`): curts, normalitzats pel pic;
- els sons de fons (`AMBIENTS`, prefix `amb_`): bucles sense costura, normalitzats per la intensitat
  mitjana, que sonen sota la música (vegeu `ambient` a adapters/benne/mapping.json).

`python3 tools/sons.py porta amb_pluja` en fa només uns quants.

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


def lin(a, b, d, corba=1.0):
    """Una rampa de `a` a `b` en `d` segons (amb `corba` > 1, comença a poc a poc)."""
    return a + (b - a) * np.linspace(0, 1, int(SR * d)) ** corba


def osc(freq, d, shape='sine', phase=0.0):
    """`freq` pot ser un número o un vector (glissando)."""
    n = int(SR * d)
    f = np.asarray(freq, dtype=float)
    if not f.ndim:
        f = np.broadcast_to(f, (n,))
    elif len(f) != n:
        # (un vector fet a trossos pot fer una mostra de més o de menys: s'ajusta allargant l'última)
        f = np.concatenate([f[:n], np.full(max(0, n - len(f)), f[-1])])
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


def eco(x, cua=0.6, humit=0.3, fosc=4000):
    """Una mica de sala: soroll que s'apaga, convolucionat (allarga el so amb la cua)."""
    m = int(SR * cua)
    ir = rng.uniform(-1, 1, m) * np.exp(-np.arange(m) / (SR * cua / 5))
    ir = band(ir, 150, fosc)
    ir /= np.sqrt(np.sum(ir ** 2))
    y = np.concatenate([x, np.zeros(m)])
    mullat = np.fft.irfft(np.fft.rfft(y) * np.fft.rfft(np.concatenate([ir, np.zeros(len(y) - m)])), len(y))
    out = y + humit * mullat
    out[-int(SR * 0.05):] *= np.linspace(1, 0, int(SR * 0.05))
    return out


def _ressonador(x, fc, bw):
    """Ressonador de 2 pols (un formant) amb la freqüència `fc` variable (vector) i l'amplada `bw` fixa."""
    r = np.exp(-np.pi * bw / SR)
    a1 = 2 * r * np.cos(2 * np.pi * fc / SR)
    a2, g = -r * r, 1 - r
    y = np.zeros_like(x)
    y1 = y2 = 0.0
    for n in range(len(x)):
        v = g * x[n] + a1[n] * y1 + a2 * y2
        y2, y1 = y1, v
        y[n] = v
    return y


def _veu(d, f0_keys, formants, ale=0.09, seed=1):
    """Una veu d'animal: un to (amb vibrato) passat per formants que es mouen. Les claus són (0-1, valor)."""
    n = int(SR * d)
    u = np.arange(n) / n
    k = lambda keys: np.interp(u, [a for a, _ in keys], [b for _, b in keys])
    vibrato = 1 + 0.03 * np.sin(2 * np.pi * 5 * t(d)) * np.minimum(1, u * 4)
    ph = np.cumsum(k(f0_keys) * vibrato) / SR
    veu = sum(np.sin(2 * np.pi * h * ph) / h ** 0.8 for h in range(1, 18))
    veu = veu + ale * np.random.default_rng(seed).uniform(-1, 1, n)  # (no toca el `rng` dels altres sons)
    x = sum(g * _ressonador(veu, k(keys), bw) for keys, bw, g in formants)
    return np.append(x[0], x[1:] - 0.92 * x[:-1]), k


# ─── Peces que es fan servir a molts sons ───────────────────────────────────


def clic(f=2400, d=0.03):
    return band(noise(d), f * 0.5, f * 2) * env(d, 0.001, 0.008)


def metall(f, d, decay=0.25, harm=(1, 2.76, 5.4), amp=(1, 0.5, 0.25)):
    """Un cop de metall: parcials inharmònics que s'apaguen."""
    return sum(a * osc(f * h, d) for h, a in zip(harm, amp)) * env(d, 0.002, decay)


def cop_sord(d=0.3, lo=50, hi=400, decay=0.08):
    """Un cop greu i apagat (fusta gruixuda, terra, una cosa pesant que cau)."""
    return band(noise(d), lo, hi) * env(d, 0.002, decay)


def gemec(f0, f1, d, lo=80, hi=1500):
    """Un metall o un motor que gira a pleret: serra que llisca, filtrada."""
    return band(osc(lin(f0, f1, d), d, 'saw'), lo, hi) * env(d, d * 0.2, None, d * 0.3)


def xiuxiueig(d, lo, hi, attack=0.05, release=0.2):
    """Soroll de banda (aire, vapor, aigua) amb entrada i sortida suaus."""
    return band(noise(d), lo, hi) * env(d, attack, None, release)


def gota(f=1700, d=0.08):
    return osc(np.linspace(f, f * 0.53, int(SR * d)), d) * env(d, 0.001, 0.02)


def bombolles(d, quantes, fmin=300, fmax=1200):
    """Bombolles que petiten (aigua que bull, que s'aboca): gotetes que pugen de to."""
    out = silence(d + 0.1)
    for _ in range(quantes):
        f = rng.uniform(fmin, fmax)
        dd = rng.uniform(0.02, 0.06)
        b = osc(np.linspace(f, f * 1.6, int(SR * dd)), dd) * env(dd, 0.002, dd / 3, 0.005)
        i = int(SR * rng.uniform(0, d))
        out[i:i + len(b)] += b * rng.uniform(0.3, 1)
    return out


def raig(d, lo=400, hi=4000):
    """Un raig d'aigua: soroll de banda que tremola (el raig no és mai igual)."""
    x = band(noise(d), lo, hi)
    lent = band(rng.uniform(-1, 1, len(x)), None, 12)
    tremola = 0.75 + 0.25 * lent / max(1e-9, np.std(lent))
    return x * np.clip(tremola, 0.3, 1.3)


# ─── Portes, panys i màquines ───────────────────────────────────────────────


def porta():
    """Una porta de fusta (la granja): el pom, la frontissa i el cop en tancar."""
    grinyol = band(osc(lin(520, 610, 0.35), 0.35, 'saw'), 400, 2500) * env(0.35, 0.08, None, 0.1) * 0.15
    return mix(clic(1800, 0.04), (clic(1200, 0.05) * 0.7, 0.07), (grinyol, 0.15), (cop_sord(0.25, 70, 600, 0.05), 0.6),
               (clic(900, 0.04) * 0.6, 0.62))


def porta_metall():
    """Una porta de nau que llisca: el clac del pestell, l'aire comprimit i el cop de ferro en obrir-se del tot."""
    aire = xiuxiueig(0.7, 1500, 7000, 0.02, 0.4) * lin(1, 0.3, 0.7) * 0.5
    llisca = band(noise(0.5), 200, 900) * env(0.5, 0.05, None, 0.1) * 0.3
    return mix(clic(1400, 0.05), (metall(400, 0.2, 0.04) * 0.4, 0.02), (aire, 0.06), (llisca, 0.1),
               (metall(180, 0.6, 0.15, (1, 2.4, 4.1)) * 0.6, 0.6), (cop_sord(0.2, 60, 400, 0.04) * 0.6, 0.6))


def rampa():
    """La rampa de la Cantimplora que baixa: l'hidràulica que gemega, l'aire que s'escapa i el cop a terra."""
    d = 2.2
    hidraulica = gemec(160, 120, d, 80, 1200) * 0.4 + osc(lin(320, 240, d), d) * env(d, 0.3, None, 0.4) * 0.08
    aire = xiuxiueig(1.2, 2000, 8000, 0.05, 0.6) * 0.3
    return mix((clic(900, 0.06), 0), (hidraulica, 0.05), (aire, 0.1), (cop_sord(0.5, 40, 300, 0.12), 2.25),
               (metall(110, 1.0, 0.3) * 0.5, 2.25))


def caixa_forta():
    """Una caixa forta: la roda que fa clics, el pestell gros i la porta pesant que s'obre."""
    clics = [(clic(3000, 0.02) * 0.5, 0.1 * i + rng.uniform(0, 0.02)) for i in range(6)]
    return mix(*clics, (clic(1200, 0.05), 0.75), (metall(300, 0.4, 0.08) * 0.5, 0.77),
               (gemec(220, 180, 0.9, 150, 2000) * 0.25, 1.0), (cop_sord(0.4, 60, 400, 0.1) * 0.6, 1.85))


def teclat():
    """Un teclat numèric: quatre tecles i el bip que diu que sí."""
    tecla = lambda f: mix(osc(f, 0.07, 'square') * env(0.07, 0.002, None, 0.015) * 0.3, clic(3500, 0.015) * 0.3)
    tecles = [(tecla(f), 0.16 * i) for i, f in enumerate((1209, 1336, 1477, 1336))]
    ok = mix(osc(1760, 0.1) * env(0.1, 0.003, None, 0.02) * 0.4, (osc(2349, 0.15) * env(0.15, 0.003, None, 0.04) * 0.4, 0.1))
    return mix(*tecles, (ok, 0.75))


def bomba():
    """La bomba de Verne que xucla aigua: el motor que arrenca, i els glops que puja del pou."""
    d = 3.0
    f = np.concatenate([np.linspace(30, 90, int(SR * 0.7)), np.full(int(SR * (d - 0.7)), 90)])
    motor = (osc(f, d, 'saw') * 0.25 + band(noise(d), 60, 500) * 0.35) * env(d, 0.3, None, 0.5)
    pistó = 0.7 + 0.3 * (osc(2.5, d) > 0)
    xuclet = band(noise(d), 150, 900) * np.clip(osc(2.5, d, phase=-1.0), 0, 1) ** 2 * env(d, 0.6, None, 0.5) * 0.6
    glops = bombolles(d - 0.8, 25, 150, 500) * 0.4
    return mix(motor * pistó, xuclet, (glops, 0.7))


def cargols():
    """Un tornavís de carraca que afluixa cargols i un cargol que cau a terra de ferro."""
    carraca = [(clic(2600, 0.02) * 0.6, 0.06 * i) for i in range(8)]
    carraca2 = [(clic(2500, 0.02) * 0.5, 0.65 + 0.06 * i) for i in range(6)]
    caure = mix(metall(2400, 0.15, 0.04, (1, 2.3)), (metall(2600, 0.12, 0.03, (1, 2.3)) * 0.6, 0.11),
                (metall(2500, 0.1, 0.02, (1, 2.3)) * 0.4, 0.19))
    return mix(*carraca, *carraca2, (caure * 0.6, 1.15))


def videotelefon():
    """El videotelèfon de la nau que truca: dos tons que trinen, dues vegades."""
    def to():
        d = 0.9
        trino = (osc(15, d) > 0)
        return (osc(880, d, 'square') * trino + osc(1175, d, 'square') * (1 - trino)) * env(d, 0.01, None, 0.05) * 0.25
    return mix(to(), (to(), 1.4))


def radio():
    """La ràdio: estàtica a batzegades que s'aclareix, i el to de la portadora."""
    d = 1.6
    soroll = band(noise(d), 300, 6000) * (0.6 + 0.4 * (osc(9, d) > 0)) * lin(1, 0.15, d)
    portadora = osc(1000, d) * lin(0, 0.35, d, 2)
    return (soroll + portadora) * env(d, 0.02, None, 0.15)


def motor_nau():
    """La Cantimplora que arrenca i s'enlaira: tos del motor, el brunzit que puja i el rugit que se'n va."""
    d = 4.5
    tos = mix(*[(cop_sord(0.15, 40, 300, 0.04) * a, s) for s, a in ((0, 0.8), (0.3, 0.6), (0.5, 0.9))])
    f = lin(40, 110, d, 0.7)
    brunzit = (osc(f, d, 'saw') * 0.3 + osc(f * 4, d) * 0.06) * env(d, 0.4, None, 1.2)
    rugit = band(noise(d), 50, 1500) * lin(0.1, 1, d, 1.5) * env(d, 0.5, None, 1.5) * 0.9
    xiulet = osc(lin(600, 1800, d, 1.5), d) * lin(0, 0.08, d) * env(d, 0.5, None, 1.2)
    return mix(tos, (brunzit + rugit + xiulet, 0.6))


def motor_apaga():
    """La Cantimplora que s'apaga (el pròleg): el brunzit que cau, tres estossecs del motor (com a l'animació
    `nau_apaga`: a 0,2, 1,0 i 1,8 s), i els relés dels llums de la cabina i de la rampa."""
    d = 3.2
    f = lin(70, 25, d, 0.6)
    brunzit = (osc(f, d, 'saw') * 0.25 + band(noise(d), 40, 400) * 0.2) * env(d, 0.05, None, 1.4) * lin(1, 0, d, 0.8)
    tos = [(cop_sord(0.2 if i < 2 else 0.35, 40, 300, 0.05 if i < 2 else 0.1) * a, s)
           for i, (s, a) in enumerate(((0.2, 0.7), (1.0, 0.6), (1.8, 1.0)))]
    relés = [(clic(1800, 0.02) * 0.5, s) for s in (0.9, 1.1, 1.3, 2.5, 2.6, 2.7)]
    return mix(brunzit, *tos, *relés)


def mosca():
    """La Mosca, el dron de la Vet (fet d'un aspirador): un brunzit que puja, canvia de to i se'n va."""
    d = 1.8
    f = 180 + 30 * osc(1.3, d) + lin(0, 40, d)
    hèlix = osc(f, d, 'saw') * 0.25 + osc(f * 2.02, d, 'saw') * 0.12 + band(noise(d), 1500, 5000) * 0.15
    return band(hèlix, 120, 6000) * env(d, 0.25, None, 0.5) * (0.85 + 0.15 * osc(23, d))


def grua():
    """Una grua: el motor que gemega, la cadena que corre i el cop de la càrrega."""
    d = 2.0
    motor = gemec(90, 120, d, 60, 1000) * 0.4
    baules = [(metall(rng.uniform(1800, 2600), 0.08, 0.02, (1, 2.4)) * 0.35, 0.15 + 0.07 * i) for i in range(22)]
    return mix(motor, *baules, (cop_sord(0.4, 40, 300, 0.1), 2.0), (metall(140, 0.6, 0.15) * 0.4, 2.0))


def cistella():
    """Una cistella de vímet que es mou i es deixa a terra: cruixits."""
    cruix = lambda: band(noise(0.06), 1500, 6000) * env(0.06, 0.003, 0.015)
    return mix(*[(cruix() * rng.uniform(0.3, 0.8), rng.uniform(0, 0.5)) for _ in range(10)],
               (cop_sord(0.15, 150, 900, 0.03) * 0.6, 0.55), *[(cruix() * 0.4, 0.58 + 0.05 * i) for i in range(3)])


def trampa():
    """Xof! Una trampa humida: fang que cau, un esquitx i unes gotes."""
    d = 0.5
    xof = band(noise(d), 80, 1500) * env(d, 0.004, 0.08) + osc(lin(220, 70, d), d) * env(d, 0.002, 0.06) * 0.5
    esquitx = band(noise(0.3), 1500, 6000) * env(0.3, 0.005, 0.06) * 0.4
    return mix(xof, (esquitx, 0.02), (gota(1400) * 0.2, 0.45), (gota(1800) * 0.15, 0.7), (gota(1200) * 0.12, 0.95))


def sorra():
    """Sorra fina que cau dins un sac: un xiuxiueig granulat."""
    d = 1.5
    grans = band(noise(d), 2000, 9000) * (rng.uniform(0, 1, int(SR * d)) > 0.7)
    flux = band(noise(d), 500, 3000) * 0.4
    return (band(grans, 1500, 9000) * 1.5 + flux) * env(d, 0.15, None, 0.5) * (0.8 + 0.2 * osc(3, d))


def manxa():
    """La manxa de la fosa: dues bufades amb el cuir que cruix."""
    buf = lambda: xiuxiueig(0.55, 150, 1200, 0.15, 0.3) * np.sin(np.linspace(0, np.pi, int(SR * 0.55)))
    cruix = lambda: band(noise(0.12), 600, 2500) * env(0.12, 0.01, 0.04) * 0.3
    return mix(cruix(), (buf(), 0.05), (cruix(), 0.75), (buf(), 0.8))


def forn():
    """El foc del forn que puja: un ronc que creix i espurnes que peten."""
    d = 3.0
    ronc = band(noise(d), 40, 600) * lin(0.1, 1, d, 0.6) * env(d, 0.3, None, 0.8)
    flama = band(noise(d), 600, 3000) * lin(0, 0.4, d) * env(d, 0.5, None, 0.8) * (0.7 + 0.3 * osc(5, d))
    petar = [(clic(rng.uniform(1500, 4000), 0.02) * rng.uniform(0.3, 0.8), rng.uniform(0.5, d - 0.3)) for _ in range(30)]
    return mix(ronc + flama, *petar)


def colada():
    """El metall fos que s'aboca al motlle: el raig espès que xiuxiueja i el bull que esclata."""
    d = 3.0
    raig_fos = band(noise(d), 200, 2500) * env(d, 0.2, None, 1.0) * (0.75 + 0.25 * osc(7, d)) * 0.6
    sizzle = xiuxiueig(2.5, 3000, 9000, 0.3, 0.8) * 0.5
    bull = bombolles(2.4, 60, 120, 450) * 0.6
    return mix(raig_fos, (sizzle, 0.4), (bull, 0.6))


def vapor():
    """Un raig de vapor que s'escapa."""
    d = 1.4
    return xiuxiueig(d, 2500, 10000, 0.01, 0.8) * lin(1, 0.4, d) + xiuxiueig(d, 600, 2000, 0.01, 0.8) * 0.3


def cops_ferro():
    """Un martell contra una enclusa, tres cops."""
    cop = lambda f, a: mix(metall(f, 0.9, 0.3, (1, 2.76, 5.4, 8.9), (1, 0.6, 0.35, 0.2)), clic(3000, 0.02)) * a
    return mix(cop(1050, 1), (cop(1040, 0.85), 0.45), (cop(1060, 0.95), 0.9))


def condensador():
    """Una màquina vella que arrenca de mala gana (el condensador d'aire) i comença a gotejar."""
    d = 3.0
    tos = mix(*[(cop_sord(0.12, 60, 500, 0.03) * a, s) for s, a in ((0, 0.7), (0.25, 0.5), (0.45, 0.8), (0.6, 0.6))])
    f = np.concatenate([lin(20, 70, 0.6), np.full(int(SR * (d - 0.6)), 70)])
    motor = (osc(f, d, 'saw') * 0.25 + band(noise(d), 80, 900) * 0.25) * env(d, 0.2, None, 0.4)
    traqueteig = band(noise(d), 1000, 4000) * (osc(11, d) > 0.9) * 0.2
    gotes = [(gota(rng.uniform(1300, 1900)) * 0.4, 1.6 + 0.35 * i + rng.uniform(0, 0.1)) for i in range(5)]
    return mix(tos, (motor + traqueteig, 0.7), *gotes)


def aixeta():
    """Una aixeta que grinyola i un raig d'aigua que cau."""
    d = 1.8
    grinyol = band(osc(lin(900, 1300, 0.3), 0.3, 'saw'), 700, 4000) * env(0.3, 0.03, None, 0.1) * 0.15
    aigua = raig(d, 400, 5000) * env(d, 0.05, None, 0.4) * 0.6
    return mix(grinyol, (aigua, 0.25))


def robot():
    """En Fidel, el majordom robot: «bi-bup» educat i un servo."""
    b = lambda f0, f1, d: osc(lin(f0, f1, d), d) * env(d, 0.005, None, 0.02) * 0.4
    servo = osc(lin(400, 600, 0.25), 0.25, 'square') * env(0.25, 0.02, None, 0.05) * 0.08
    return mix(b(880, 900, 0.1), (b(1320, 1100, 0.18), 0.13), (servo, 0.38))


def degoteig():
    """Gotes que cauen en un bassal."""
    return mix(*[(gota(f) * a, s) for s, f, a in ((0, 1600, 0.6), (0.55, 1400, 0.5), (0.9, 1750, 0.4), (1.5, 1500, 0.5))])


def regar():
    """Una regadora: el raig que es parteix en gotes sobre les fulles."""
    d = 2.0
    pluja_fina = band(noise(d), 2000, 8000) * (rng.uniform(0, 1, int(SR * d)) > 0.93) * 2
    fulles = [(band(noise(0.04), 1500, 5000) * env(0.04, 0.002, 0.01) * rng.uniform(0.2, 0.5), rng.uniform(0.1, d - 0.2)) for _ in range(30)]
    return mix(band(pluja_fina, 2000, 8000) * env(d, 0.2, None, 0.5) + raig(d, 800, 4000) * env(d, 0.2, None, 0.5) * 0.3, *fulles)


def bip():
    """La carmanyola d'en Tomàs (el comunicador amagat): dos bips curts, una mica sospitosos."""
    b = lambda: osc(2093, 0.06, 'square') * env(0.06, 0.002, None, 0.01) * 0.3
    return mix(b(), (b(), 0.12))


def pantalla():
    """Una pantalla que s'encén: el xiulet que puja, el clic i el brunzit."""
    d = 1.0
    xiulet = osc(lin(4000, 15000, 0.4, 0.5), 0.4) * env(0.4, 0.02, None, 0.1) * 0.08
    brunzit = (osc(120, d) * 0.2 + band(noise(d), 3000, 8000) * 0.05) * env(d, 0.05, None, 0.3)
    return mix(xiulet, (clic(1500, 0.04), 0.3), (brunzit, 0.32))


def ascensor():
    """L'ascensor del palau: el motor llis que puja i el «ding» d'arribada."""
    d = 2.0
    motor = (osc(lin(80, 95, d), d) * 0.3 + band(noise(d), 100, 600) * 0.2) * env(d, 0.4, None, 0.5)
    ding = sum(osc(f, 1.5) * a for f, a in ((1319, 1), (2638, 0.2), (3956, 0.1))) * env(1.5, 0.002, 0.5) * 0.4
    return mix(motor, (ding, 2.0))


def pany():
    """Una clau grossa que entra i gira dins d'un pany antic."""
    entra = band(noise(0.25), 2000, 7000) * env(0.25, 0.01, 0.1) * 0.4
    gir = band(noise(0.35), 400, 2500) * env(0.35, 0.05, None, 0.1) * 0.5
    return mix(entra, (gir, 0.3), (clic(600, 0.08), 0.7), (clic(1200, 0.04) * 0.6, 0.72), (metall(500, 0.3, 0.06) * 0.3, 0.7))


def valvula():
    """La vàlvula d'un dipòsit orbital que s'obre: el cop profund, el gel que cruix i l'aigua que se n'allibera."""
    d = 4.0
    cop = mix(osc(lin(60, 30, 1.5), 1.5) * env(1.5, 0.003, 0.4), cop_sord(0.8, 30, 200, 0.2))
    gel = mix(*[(band(noise(0.05), 2000, 8000) * env(0.05, 0.001, 0.01) * rng.uniform(0.2, 0.6), rng.uniform(0.2, 1.8)) for _ in range(35)])
    allau = band(noise(d), 40, 1200) * lin(0, 1, d, 0.4) * env(d, 0.5, None, 1.5)
    brollador = raig(d, 300, 3000) * lin(0, 0.6, d) * env(d, 1.0, None, 1.5)
    return mix(cop, (gel * 0.5, 0.1), (allau + brollador * 0.5, 0.3))


def palanca():
    """Una palanca grossa: la carraca que puja i el clonc quan arriba."""
    carraca = [(clic(1500, 0.03) * 0.5, 0.07 * i) for i in range(5)]
    return mix(*carraca, (metall(260, 0.6, 0.12, (1, 2.4, 4.1)) * 0.8, 0.4), (cop_sord(0.25, 60, 400, 0.05) * 0.6, 0.4))


def martell():
    """El martell de la subhasta: un cop sec de fusta, i la sala que fa eco."""
    d = 0.4
    fusta = mix((osc(420, d) + 0.5 * osc(1150, d) + 0.25 * osc(2200, d)) * env(d, 0.001, 0.04), clic(3000, 0.02))
    return eco(fusta, cua=1.0, humit=0.25)


def cava():
    """Una ampolla de cava: el tap que salta i l'escuma."""
    pop = mix(osc(lin(900, 300, 0.05), 0.05) * env(0.05, 0.001, 0.015), band(noise(0.05), 500, 4000) * env(0.05, 0.001, 0.01))
    escuma = xiuxiueig(1.5, 3000, 10000, 0.02, 0.8) * lin(1, 0.2, 1.5) * 0.35
    return mix(pop, (escuma, 0.05), (bombolles(1.2, 40, 1500, 4000) * 0.15, 0.1))


def piscina():
    """Una piscina que s'omple: una cascada que cau i l'aigua que puja (el to de l'aigua, cada cop més greu)."""
    d = 4.0
    cascada = raig(d, 200, 4000) * env(d, 0.4, None, 1.2)
    fons = band(noise(d), 50, 400) * lin(0.3, 1, d) * env(d, 0.6, None, 1.2)
    glop = bombolles(d - 1, 40, 200, 700) * 0.3
    return cascada * 0.7 + fons * 0.6 + np.pad(glop, (0, len(cascada) - len(glop)))[: len(cascada)]


def gos():
    """En Dividend: un gos petit i pentinat, «uf! uf!»."""
    def uf(seed):
        x, k = _veu(0.16, [(0, 650), (0.2, 900), (1, 500)],
                    [([(0, 700), (0.3, 1300), (1, 900)], 200, 1.0), ([(0, 1800), (0.4, 2400), (1, 2000)], 300, 0.6)],
                    ale=0.5, seed=seed)
        return x * env(0.16, 0.005, 0.06)
    return mix(uf(2), (uf(3) * 0.85, 0.24))


def gat():
    """En Diu: «miaaau» llarg que vol menjar. Una veu passada per formants que van de la «m» a la «i», l'«a» i la «u»."""
    d = 1.0
    x, k = _veu(d, [(0, 480), (0.25, 720), (0.6, 690), (1, 400)], [
        ([(0, 300), (0.1, 420), (0.3, 980), (0.75, 920), (0.92, 480), (1, 420)], 140, 1.0),
        ([(0, 1100), (0.1, 2600), (0.25, 2000), (0.6, 1650), (0.88, 1050), (1, 900)], 180, 0.7),
        ([(0, 2600), (0.12, 3400), (0.5, 3000), (1, 2600)], 260, 0.35),
    ])
    e = k([(0, 0), (0.08, 0.3), (0.2, 1), (0.75, 0.85), (1, 0)])
    e[-int(SR * 0.03):] *= np.linspace(1, 0, int(SR * 0.03))
    return x * e


def paper():
    """Un paper que es desplega: fregaments i cruixits."""
    fregs = [(band(noise(d), 1500, 8000) * env(d, 0.01, d / 3) * rng.uniform(0.3, 0.8), s)
             for s, d in ((0, 0.12), (0.15, 0.2), (0.4, 0.1), (0.55, 0.25))]
    cruix = [(clic(rng.uniform(2000, 5000), 0.015) * 0.5, rng.uniform(0, 0.8)) for _ in range(12)]
    return mix(*fregs, *cruix)


def motlle():
    """El motlle de sorra: s'obre amb un cop sord, la sorra s'escola i el metall encara xiuxiueja."""
    return mix(cop_sord(0.4, 60, 500, 0.1), (metall(320, 0.5, 0.1) * 0.3, 0.0),
               (band(noise(0.8), 1500, 7000) * env(0.8, 0.05, None, 0.4) * (rng.uniform(0, 1, int(SR * 0.8)) > 0.6) * 0.5, 0.15),
               (xiuxiueig(1.5, 3000, 9000, 0.3, 0.7) * 0.25, 0.4))


def titol():
    """El cop de títol de capítol: timbal greu, un acord de guitarra de western (Mi menor) i la cua."""
    d = 3.0
    timbal = mix(osc(lin(80, 45, 0.8), 0.8) * env(0.8, 0.002, 0.3), cop_sord(0.5, 30, 200, 0.12))
    corda = lambda f: sum(osc(f * h, d) * np.exp(-t(d) * h / 1.2) / h for h in range(1, 7)) * env(d, 0.003, None, 0.3)
    acord = sum(corda(f) * 0.25 for f in (82.4, 123.5, 164.8, 196.0, 246.9, 329.6))
    trem = 0.7 + 0.3 * osc(6.7, d)
    return eco(mix(timbal, (acord * trem, 0.02)), cua=1.5, humit=0.4)


# ─── Sons de fons (en bucle) ─────────────────────────────────────────────────
# Cada so és periòdic (filtres circulars, freqüències amb un nombre sencer de cicles i esdeveniments que
# donen la volta), així que el bucle no té costura. Vegeu `ambient` a adapters/benne/mapping.json.


def _lfo(d, rate, lo, hi):
    """Una corba lenta i aleatòria entre `lo` i `hi`, que acaba on comença."""
    n = max(2, int(d * rate))
    v = rng.uniform(lo, hi, n)
    v = np.append(v, v[0])
    x = np.linspace(0, n, int(SR * d), endpoint=False)
    i = np.floor(x).astype(int)
    f = x - i
    f = (1 - np.cos(np.pi * f)) / 2
    return v[i] * (1 - f) + v[i + 1] * f


def _posa(out, x, t):
    """Suma `x` a `out` a partir de `t` segons, donant la volta pel final."""
    idx = (int(SR * t) + np.arange(len(x))) % len(out)
    np.add.at(out, idx, x)


def _murmuri(d, veus, lo=250, hi=2800):
    """Gent que parla lluny: cada veu és un to que puja i baixa, que obre i tanca bandes a ritme de síl·laba."""
    out = np.zeros(int(SR * d))
    for _ in range(veus):
        # Freqüència de cada veu: entera en tot el bucle perquè la fase tanqui.
        f0 = _lfo(d, 0.8, 100, 240)
        ph = np.cumsum(f0) / SR
        ph *= np.round(ph[-1]) / ph[-1]
        so = sum(np.sin(2 * np.pi * h * ph) / h for h in range(1, 20))
        parla = _lfo(d, 0.3, 0, 1) > 0.45  # ara parla, ara escolta
        parla = band(parla.astype(float), None, 3)
        for blo, bhi in ((300, 700), (700, 1300), (1300, 2500)):
            sil = _lfo(d, rng.uniform(3.5, 5.5), 0, 1) ** 2
            out += band(so, blo, bhi) * sil * np.clip(parla, 0, 1) * rng.uniform(0.5, 1)
    return band(out, lo, hi)


def amb_vent():
    """Terra-2: vent sec que bufa a ràfegues i arrossega pols i grava."""
    d = 24
    vent = band(noise(d), 200, 2500) * _lfo(d, 0.25, 0.25, 1.0) ** 1.5 * 0.6
    xiulet = band(noise(d), 700, 850) * _lfo(d, 0.2, 0, 1) ** 3 * 0.8
    pols = band(noise(d), 3000, 9000) * (rng.uniform(0, 1, int(SR * d)) > 0.8) * _lfo(d, 0.3, 0, 1) ** 2 * 0.25
    out = vent + xiulet + band(pols, 3000, 9000)
    # Una porta de fusta que pica, lluny.
    for t in (7.0, 18.5):
        _posa(out, band(noise(0.2), 80, 600) * env(0.2, 0.002, 0.04) * 0.25, t)
    return out


def amb_nau():
    """L'interior de la Cantimplora: el brunzit del motor, la ventilació i el casc que grinyola."""
    d = 16
    brunzit = osc(41, d) * 0.3 + osc(82, d) * 0.4 + osc(123, d) * 0.15 + band(osc(41, d, 'saw'), 40, 300) * 0.2
    ventilacio = band(noise(d), 150, 1500) * _lfo(d, 0.2, 0.7, 1.0) * 0.25
    out = brunzit * (0.85 + 0.15 * osc(0.5, d)) + ventilacio
    for t, f in ((3.0, 190), (11.0, 240)):
        g = band(osc(lin(f, f * 0.9, 0.9), 0.9, 'saw'), f * 1.5, f * 8) * env(0.9, 0.35, None, 0.35) * 0.06
        _posa(out, g, t)
    return out


def amb_aqua():
    """El fons de l'antic mar d'Aqua: vent salat i buit, un mar que ja no hi és, i una boia lluny."""
    d = 24
    vent = band(noise(d), 300, 3000) * _lfo(d, 0.25, 0.2, 0.9) * 0.5
    buit = band(noise(d), 450, 520) * _lfo(d, 0.15, 0, 1) ** 2 * 1.2
    mar = band(noise(d), 60, 400) * _lfo(d, 0.12, 0.1, 1) ** 2 * 0.5
    out = vent + buit + mar
    campana = sum(a * osc(659 * r, 3.0) * env(3.0, 0.002, dec) for r, a, dec in ((1, 1, 1.2), (2.0, 0.3, 0.7), (2.51, 0.2, 0.4))) * 0.05
    for t in (5.0, 15.5):
        _posa(out, campana, t)
    return out


def amb_ferrum():
    """Ferrum de vaga: una foguera que crema i gent que parla, lluny."""
    d = 20
    foc = band(noise(d), 60, 800) * _lfo(d, 0.5, 0.5, 1.0) * 0.35
    out = foc + _murmuri(d, 6) * 0.15
    for _ in range(80):
        _posa(out, clic(rng.uniform(1200, 4000), 0.02) * rng.uniform(0.1, 0.4), rng.uniform(0, d))
    # Un martell lluny, de tant en tant.
    for t in (6.0, 6.6, 14.0):
        _posa(out, metall(900, 0.6, 0.15) * 0.04, t)
    return out


def amb_fosa():
    """La fosa: el forn que ronca, l'aire que xiula a les toveres."""
    d = 16
    ronc = band(noise(d), 30, 300) * _lfo(d, 0.4, 0.6, 1.0) * 0.9
    flama = band(noise(d), 300, 2000) * _lfo(d, 0.8, 0.3, 0.8) * 0.3
    tovera = band(noise(d), 1100, 1300) * 0.2
    out = ronc + flama + tovera + osc(31, d) * 0.15
    for _ in range(25):
        _posa(out, clic(rng.uniform(1500, 4000), 0.02) * rng.uniform(0.1, 0.3), rng.uniform(0, d))
    return out


def amb_verdant():
    """El jardí de Verne: els aspersors que fan «txic-txic-txic» i ocells de mentida (sempre el mateix refilet)."""
    d = 16
    out = band(noise(d), 2000, 9000) * 0.03
    txic = band(noise(0.05), 3000, 9000) * env(0.05, 0.002, 0.015) * 0.4
    for i in range(int(d / 0.25)):
        if (i % 32) < 24:  # l'aspersor gira, i torna enrere
            _posa(out, txic * (0.6 + 0.4 * ((i % 32) / 24)), i * 0.25)

    def refilet():
        dd = 0.6
        x = t(dd)
        f = 3000 + 800 * np.sin(2 * np.pi * 9 * x) + lin(0, 600, dd)
        return osc(f, dd) * env(dd, 0.02, None, 0.1) * 0.12
    # El mateix ocell, exactament, cada quatre segons: és un altaveu.
    for t0 in (1.0, 5.0, 9.0, 13.0):
        _posa(out, refilet(), t0)
        _posa(out, refilet() * 0.7, t0 + 0.8)
    return out


def amb_palau():
    """El palau orbital: brunzit net d'estació, l'aire condicionat i, molt lluny, un aquari que bombolleja."""
    d = 16
    brunzit = osc(60, d) * 0.15 + osc(120, d) * 0.1 + osc(1000, d) * 0.005
    aire = band(noise(d), 200, 3000) * 0.2 * _lfo(d, 0.1, 0.85, 1.0)
    out = brunzit + aire
    for _ in range(14):
        _posa(out, gota(rng.uniform(600, 900), 0.05) * 0.04, rng.uniform(0, d))
    return out


def amb_subhasta():
    """La sala de la subhasta: el murmuri de la gent bona, una tos i el dringar d'una copa."""
    d = 20
    out = _murmuri(d, 14) * 0.25 + band(noise(d), 100, 600) * 0.03
    _posa(out, band(noise(0.25), 200, 1500) * env(0.25, 0.005, 0.07) * 0.15, 8.0)
    _posa(out, metall(2637, 1.0, 0.4, (1, 2.4, 3.9), (1, 0.3, 0.15)) * 0.03, 14.2)
    return out


def amb_pluja():
    """La pluja: un xiuxiueig ample, gotes que piquen al pati i el canaló que raja."""
    d = 20
    out = band(noise(d), 600, 7000) * 0.4 * _lfo(d, 0.2, 0.8, 1.0) + band(noise(d), 80, 500) * 0.2
    for _ in range(int(d * 40)):
        g = band(noise(0.03), 2000, 9000) * env(0.03, 0.001, 0.006) * rng.uniform(0.05, 0.3)
        _posa(out, g, rng.uniform(0, d))
    canalo = band(noise(d), 300, 2000) * (0.7 + 0.3 * _lfo(d, 2, 0, 1)) * 0.15
    return out + canalo


AMBIENTS = {
    'amb_vent': amb_vent, 'amb_nau': amb_nau, 'amb_aqua': amb_aqua, 'amb_ferrum': amb_ferrum, 'amb_fosa': amb_fosa,
    'amb_verdant': amb_verdant, 'amb_palau': amb_palau, 'amb_subhasta': amb_subhasta, 'amb_pluja': amb_pluja,
}


SONS = {
    'porta': porta, 'porta_metall': porta_metall, 'rampa': rampa, 'caixa_forta': caixa_forta, 'teclat': teclat,
    'bomba': bomba, 'cargols': cargols, 'videotelefon': videotelefon, 'radio': radio, 'motor_nau': motor_nau,
    'motor_apaga': motor_apaga, 'mosca': mosca, 'grua': grua, 'cistella': cistella, 'trampa': trampa, 'sorra': sorra, 'manxa': manxa,
    'forn': forn, 'colada': colada, 'vapor': vapor, 'cops_ferro': cops_ferro, 'condensador': condensador,
    'aixeta': aixeta, 'robot': robot, 'degoteig': degoteig, 'regar': regar, 'bip': bip, 'pantalla': pantalla,
    'ascensor': ascensor, 'pany': pany, 'valvula': valvula, 'palanca': palanca, 'martell': martell, 'cava': cava,
    'piscina': piscina, 'gos': gos, 'gat': gat, 'paper': paper, 'motlle': motlle, 'titol': titol,
}

# Volum de cada so respecte del màxim (els que són tons purs o molt sostinguts sonen més del que fan).
VOLUM = {
    'radio': 0.6, 'videotelefon': 0.28, 'teclat': 0.4, 'bip': 0.5, 'robot': 0.4, 'pantalla': 0.5, 'mosca': 0.6,
    'bomba': 0.7, 'vapor': 0.6, 'piscina': 0.7, 'forn': 0.85, 'colada': 0.85, 'sorra': 0.75, 'regar': 0.6,
    'ascensor': 0.5, 'motor_nau': 0.8, 'motor_apaga': 0.8, 'gat': 0.7, 'cops_ferro': 0.8, 'grua': 0.8,
}

# Els sons que són tot cop i poca cua se senten fluixos: se'ls comprimeix una mica (com més, més cos).
COMPRIMEIX = {'trampa': 4, 'martell': 3, 'regar': 3, 'titol': 2.5, 'valvula': 2.5, 'caixa_forta': 2, 'degoteig': 2, 'cava': 2}

# Els sons de fons greus (un brunzit, un forn) se senten menys amb la mateixa intensitat: se'ls apuja perquè
# tots sonin semblant (uns -22 LUFS).
VOLUM_FONS = {'amb_fosa': 2.2, 'amb_nau': 1.6, 'amb_palau': 1.5, 'amb_verdant': 0.7, 'amb_pluja': 0.85, 'amb_ferrum': 1.1, 'amb_subhasta': 1.1}


def write(name, x, rms=None):
    """Normalitza pel pic (o, als sons de fons, per la intensitat mitjana `rms`) i desa l'.ogg."""
    if rms:
        x = x - np.mean(x)
        x = x / max(1e-9, np.sqrt(np.mean(x ** 2))) * rms
        x = np.tanh(x / 0.9) * 0.9  # cap pic no satura
    else:
        # Que comenci i acabi a zero (sense clic).
        x = x.copy()
        n = min(int(SR * 0.004), len(x) // 4)
        x[:n] *= np.linspace(0, 1, n)
        x[-n:] *= np.linspace(1, 0, n)
        x = x / max(1e-9, np.max(np.abs(x)))
        if name in COMPRIMEIX:
            k = COMPRIMEIX[name]
            x = np.tanh(k * x) / np.tanh(k)
        x = x * 0.8 * VOLUM.get(name, 1.0)
    pcm = (np.clip(x, -1, 1) * 32767).astype('<i2')
    with tempfile.NamedTemporaryFile(suffix='.wav') as tmp:
        with wave.open(tmp.name, 'wb') as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(pcm.tobytes())
        subprocess.run(
            # Els bucles, en Opus: amb Vorbis, Chrome no retalla el farciment del final i el bucle faria un forat.
            ['ffmpeg', '-loglevel', 'error', '-y', '-i', tmp.name, *(['-c:a', 'libopus', '-b:a', '64k'] if rms else ['-c:a', 'libvorbis', '-q:a', '4']), str(OUT / f'{name}.ogg')],
            check=True,
        )
    print(f'  {name}: {len(x) / SR:.1f} s, pic {np.max(np.abs(x)):.2f}' + (f', salt a la costura {abs(x[0] - x[-1]):.3f}' if rms else ''))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    only = set(sys.argv[1:])
    for name, make in SONS.items():
        if only and name not in only:
            continue
        write(name, make())
    for name, make in AMBIENTS.items():
        if only and name not in only:
            continue
        write(name, make(), rms=0.07 * VOLUM_FONS.get(name, 1.0))
    print(f'✔ {len(only) or len(SONS) + len(AMBIENTS)} sons a {OUT}')


if __name__ == '__main__':
    main()
