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


# ─── Sons de Ni un ou ──────────────────────────────────────────────────────


def clic(f=2400, d=0.03):
    return band(noise(d), f * 0.5, f * 2) * env(d, 0.001, 0.008)




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


def miol():
    """En Diu, queixós: «miaaaau» llarg que vol menjar. Una veu (to que puja i cau, vibrato) passada per
    tres formants que van de la «m» a la «i», l'«a» i la «u»."""
    d = 1.0
    n = int(SR * d)
    u = np.arange(n) / n
    k = lambda keys: np.interp(u, [a for a, _ in keys], [b for _, b in keys])
    vibrato = 1 + 0.04 * np.sin(2 * np.pi * 5 * t(d)) * np.minimum(1, u * 4)
    f0 = k([(0, 480), (0.25, 720), (0.6, 690), (1, 400)]) * vibrato
    ph = np.cumsum(f0) / SR
    veu = sum(np.sin(2 * np.pi * h * ph) / h ** 0.8 for h in range(1, 18))
    veu = veu + 0.09 * np.random.default_rng(1).uniform(-1, 1, n)  # alè (no toca el `rng` dels altres sons)
    formants = [
        ([(0, 300), (0.1, 420), (0.3, 980), (0.75, 920), (0.92, 480), (1, 420)], 140, 1.0),
        ([(0, 1100), (0.1, 2600), (0.25, 2000), (0.6, 1650), (0.88, 1050), (1, 900)], 180, 0.7),
        ([(0, 2600), (0.12, 3400), (0.5, 3000), (1, 2600)], 260, 0.35),
    ]
    x = sum(g * _ressonador(veu, k(keys), bw) for keys, bw, g in formants)
    x = np.append(x[0], x[1:] - 0.92 * x[:-1])  # més brillant, menys xiulet
    e = k([(0, 0), (0.08, 0.3), (0.2, 1), (0.75, 0.85), (1, 0)])
    e[-int(SR * 0.03):] *= np.linspace(1, 0, int(SR * 0.03))
    return x * e


def mossegada():
    """Unes dents petites contra un cable: dos cruixits."""
    c = lambda: band(noise(0.06), 1500, 6000) * env(0.06, 0.001, 0.015)
    return mix(c(), (c() * 0.8, 0.12), (osc(220, 0.05) * env(0.05, 0.001, 0.02) * 0.3, 0.12))



def metall(f, d, decay=0.25, harm=(1, 2.76, 5.4), amp=(1, 0.5, 0.25)):
    """Un cop de metall: parcials inharmònics que s'apaguen."""
    return sum(a * osc(f * h, d) for h, a in zip(harm, amp)) * env(d, 0.002, decay)


def estatica():
    """Una ràdio morta: soroll de banda ampla, a batzegades."""
    d = 1.0
    return band(noise(d), 300, 6000) * env(d, 0.02, None, 0.2) * (0.6 + 0.4 * (osc(7, d) > 0))


def estatica_neta():
    """La ràdio torna: estàtica que s'aclareix i un xiulet de portadora."""
    d = 1.4
    soroll = band(noise(d), 300, 6000) * np.linspace(1, 0.2, int(SR * d))
    portadora = osc(1200, d) * np.linspace(0, 0.3, int(SR * d))
    return (soroll + portadora) * env(d, 0.02, None, 0.2)


def panell():
    """Una xapa que grinyola: cargols i un xerric metàl·lic."""
    d = 0.9
    xerric = band(osc(np.linspace(900, 1400, int(SR * d)), d, 'saw'), 600, 4000) * env(d, 0.05, None, 0.2) * 0.4
    return mix((clic(3000, 0.05), 0), (clic(2600, 0.05), 0.12), (xerric, 0.25), (metall(420, 0.4), 0.95))


def valvula():
    """Una vàlvula grossa que gira dura: un gemec de metall i el cop final."""
    d = 1.2
    gemec = band(osc(np.linspace(140, 110, int(SR * d)), d, 'saw'), 80, 1200) * env(d, 0.1, None, 0.3) * 0.6
    return mix(gemec, (metall(180, 0.6, 0.2), 1.1))


def bomba():
    """Una bomba elèctrica que arrenca: un brunzit que puja i es queda."""
    d = 2.0
    n1 = int(SR * 0.6)
    f = np.concatenate([np.linspace(30, 100, n1), np.full(int(SR * d) - n1, 100)])
    motor = osc(f, d, 'saw') * 0.3 + band(noise(d), 60, 600) * 0.4
    return motor * env(d, 0.3, None, 0.4)


def frontissa():
    """Un cargol que surt i una frontissa que cau."""
    return mix(band(noise(0.4), 800, 3000) * env(0.4, 0.05, 0.15) * 0.5, (metall(600, 0.5, 0.12), 0.45))


def clau_vella():
    """Una clau grossa que entra i gira dins d'un pany antic."""
    entra = band(noise(0.25), 2000, 7000) * env(0.25, 0.01, 0.1) * 0.4
    gir = band(noise(0.35), 400, 2500) * env(0.35, 0.05, None, 0.1) * 0.5
    return mix(entra, (gir, 0.3), (clic(600, 0.08), 0.7), (clic(1200, 0.04) * 0.6, 0.72))


def muntacarregues():
    """El muntacàrregues: un timbre, un motor que s'allunya i un cop sord."""
    d = 1.6
    timbre = osc(1320, 0.15) * env(0.15, 0.002, 0.05) * 0.4
    motor = (osc(70, d, 'saw') * 0.3 + band(noise(d), 100, 800) * 0.3) * env(d, 0.15, None, 0.3) * np.linspace(1, 0.4, int(SR * d))
    return mix(timbre, (motor, 0.1), (metall(110, 0.3, 0.08) * 0.6, 1.7))


def terminal():
    """El terminal del satèl·lit: tres bips que pugen."""
    b = lambda f: osc(f, 0.09, 'square') * env(0.09, 0.002, None, 0.02) * 0.4
    return mix(b(880), (b(1100), 0.12), (b(1320), 0.24))


def enviat():
    """Enviat: un arpegi que acaba bé."""
    b = lambda f, d=0.14: osc(f, d) * env(d, 0.002, 0.1) * 0.5
    return mix(b(660), (b(880), 0.12), (b(1100), 0.24), (b(1320, 0.5), 0.36))


def impressora():
    """Una impressora que arrenca, rumia i treu un full."""
    d = 1.4
    motor = band(noise(d), 150, 900) * 0.4 + osc(120, d, 'saw') * 0.1
    return motor * env(d, 0.1, None, 0.2) * (0.8 + 0.2 * osc(3, d))


def antena():
    """L'antena que gira: un servo que xiula i fa clic."""
    d = 0.8
    servo = osc(np.linspace(500, 900, int(SR * d)), d, 'square') * 0.15 * env(d, 0.02, None, 0.1)
    return mix(servo, (clic(1800, 0.05), 0.8))


def clau_tubs():
    """Una clau de tubs contra un cargol rovellat."""
    return mix(metall(300, 0.4, 0.1), (band(noise(0.3), 500, 2000) * env(0.3, 0.02, 0.1) * 0.5, 0.2), (metall(260, 0.4, 0.1), 0.5))


def travesser():
    """Un travesser d'acer que surt de la llitera."""
    return mix(clic(1500, 0.06), (band(noise(0.4), 600, 3000) * env(0.4, 0.05, 0.15) * 0.5, 0.1), (metall(520, 0.6, 0.2), 0.5))


def pot():
    """Una bossa de plàstic amb un pot de vidre a dins."""
    return mix(band(noise(0.3), 1500, 6000) * env(0.3, 0.02, 0.08) * 0.4, (metall(1800, 0.3, 0.06, (1, 2.4)), 0.25))


def cisalla():
    """Una cisalla que talla un cadenat: esforç, el clac i el metall a terra."""
    return mix(band(noise(0.3), 300, 2000) * env(0.3, 0.1, None, 0.05) * 0.4, (clic(800, 0.08), 0.3),
               (metall(900, 0.5, 0.12) * 0.6, 0.6), (metall(700, 0.4, 0.1) * 0.4, 0.8))


def cops():
    """Cops apagats dins d'una caixa de ferro."""
    cop = lambda: band(noise(0.15), 60, 400) * env(0.15, 0.003, 0.05)
    return mix(cop(), (cop(), 0.35), (cop() * 0.8, 0.7))


def vies():
    """La maneta de la vàlvula de tres vies: un cop sec."""
    return mix(clic(1200, 0.05), (metall(340, 0.4, 0.1), 0.05))


def generador_para():
    """El generador s'atura: el brunzit baixa fins al silenci."""
    d = 2.5
    f = np.linspace(100, 15, int(SR * d))
    return (osc(f, d, 'saw') * 0.4 + band(noise(d), 40, 400) * 0.3) * np.linspace(1, 0, int(SR * d)) ** 1.5


def generador_engega():
    """El generador torna: un brunzit que puja i es queda."""
    d = 2.2
    n1 = int(SR * 1.2)
    f = np.concatenate([np.linspace(15, 100, n1), np.full(int(SR * d) - n1, 100)])
    return (osc(f, d, 'saw') * 0.4 + band(noise(d), 40, 400) * 0.3) * env(d, 0.4, None, 0.3)


def telefon_satellit():
    """Un telèfon de satèl·lit: dos tons electrònics, dues vegades."""
    to = lambda: (osc(1000, 0.4, 'square') + osc(1250, 0.4, 'square')) * env(0.4, 0.01, None, 0.05) * 0.25
    return mix(to(), (to(), 0.6))


def portatil():
    """Un portàtil que obre la sessió: un acord curt."""
    return sum(osc(f, 0.8) for f in (523, 659, 784)) * env(0.8, 0.01, 0.3) * 0.3


# ─── Portes ──────────────────────────────────────────────────────────────────
# Sonen en arribar a la sala nova (vegeu `doors` a adapters/benne/mapping.json).


def porta():
    """Una porta de cabina: el pom, la frontissa i el cop de fusta en tancar."""
    cop = band(noise(0.25), 70, 600) * env(0.25, 0.002, 0.05)
    grinyol = band(osc(np.linspace(520, 610, int(SR * 0.35)), 0.35, 'saw'), 400, 2500) * env(0.35, 0.08, None, 0.1) * 0.15
    return mix(clic(1800, 0.04), (clic(1200, 0.05) * 0.7, 0.07), (grinyol, 0.15), (cop, 0.6), (clic(900, 0.04) * 0.6, 0.62))


def porta_estanca():
    """Una porta estanca: la palanca que fa clonc, la porta pesant que gira i el tancament de ferro."""
    gemec = band(osc(np.linspace(95, 80, int(SR * 0.6)), 0.6, 'saw'), 60, 900) * env(0.6, 0.12, None, 0.15) * 0.35
    cop = band(noise(0.3), 50, 400) * env(0.3, 0.002, 0.08) * 0.8
    return mix(metall(210, 0.35, 0.07, (1, 2.4, 4.1)), (clic(700, 0.05), 0.02), (gemec, 0.3),
               (cop, 0.95), (metall(130, 0.9, 0.25, (1, 2.76, 5.4), (1, 0.35, 0.15)) * 0.8, 0.95),
               (metall(240, 0.3, 0.06) * 0.5, 1.25))


def escotilla():
    """Una escotilla de ferro: el passador, la tapa que s'aixeca i el cop en caure."""
    grinyol = band(osc(np.linspace(300, 380, int(SR * 0.4)), 0.4, 'saw'), 200, 2000) * env(0.4, 0.06, None, 0.1) * 0.25
    cop = band(noise(0.3), 40, 350) * env(0.3, 0.002, 0.1)
    return mix(clic(1500, 0.05), (metall(380, 0.25, 0.05), 0.04), (grinyol, 0.15), (cop, 0.65),
               (metall(160, 0.7, 0.2) * 0.7, 0.65))


def escala():
    """Unes passes per una escala de ferro."""
    pas = lambda f: mix(band(noise(0.12), 80, 700) * env(0.12, 0.002, 0.03), metall(f, 0.25, 0.05, (1, 2.3, 3.9), (0.6, 0.3, 0.1)))
    return mix(*[(pas(f) * a, i * 0.27) for i, (f, a) in enumerate([(330, 1), (300, 0.85), (345, 0.95), (310, 0.75)])])


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


def _grinyol(f=200):
    """El casc que treballa: un gemec de ferro o de fusta."""
    d = rng.uniform(0.6, 1.2)
    g = osc(np.linspace(f, f * rng.uniform(0.85, 1.15), int(SR * d)), d, 'saw')
    return band(g, f * 1.5, f * 8) * env(d, d * 0.4, None, d * 0.4) * (0.6 + 0.4 * osc(rng.uniform(9, 15), d))


def _gota():
    d = 0.08
    return osc(np.linspace(1700, 900, int(SR * d)), d) * env(d, 0.001, 0.02)


def _onades(d, lo=100, hi=2500, rate=0.18):
    """Onades contra el casc: soroll que puja i baixa sense ritme fix."""
    return band(noise(d), lo, hi) * _lfo(d, rate, 0.15, 1.0) ** 2


def amb_maquines():
    """La sala de màquines: el dièsel que ronca, el batec dels pistons, els empujadors i el xiuxiueig de l'aire."""
    d = 16
    ronc = osc(25, d) * 0.35 + osc(50, d) * 0.5 + osc(75, d) * 0.25 + osc(100, d) * 0.2 + band(osc(50, d, 'saw'), 40, 400) * 0.3
    batec = 0.75 + 0.25 * osc(6.25, d)
    tic = band(noise(d), 900, 3500) * (osc(12.5, d) > 0.85) * 0.12
    aire = band(noise(d), 150, 1800) * 0.25
    xiulet = osc(400, d) * 0.02
    return ronc * batec + tic + aire + xiulet


def amb_coberta():
    """La coberta principal per dins: la ventilació, el mar lluny i el casc que grinyola de tant en tant."""
    d = 20
    out = osc(50, d) * 0.08 + band(noise(d), 80, 450) * 0.35 * _lfo(d, 0.2, 0.7, 1.0) + _onades(d, 80, 500, 0.12) * 0.35
    for t, f in [(3.0, 180), (11.5, 240), (16.2, 150)]:
        _posa(out, _grinyol(f) * 0.12, t)
    return out


def amb_pont():
    """El pont: el brunzit dels instruments, el ping de la sonda i el vent a fora dels vidres."""
    d = 16
    out = osc(50, d) * 0.06 + osc(2000, d) * 0.006 + band(noise(d), 250, 1600) * 0.3 * _lfo(d, 0.3, 0.4, 1.0) ** 2
    ping = osc(1500, 0.6) * env(0.6, 0.003, 0.12) * 0.12
    for t in (1.0, 5.0, 9.0, 13.0):
        _posa(out, ping, t)
    return out


def amb_mar():
    """A coberta, de nit: les onades, el vent i alguna esquitxada."""
    d = 24
    vent = band(noise(d), 350, 3000) * _lfo(d, 0.25, 0.3, 1.0) * 0.45 + band(noise(d), 820, 960) * _lfo(d, 0.2, 0, 1) * 0.6
    out = _onades(d) + vent
    for t in (4.0, 13.5, 19.0):
        _posa(out, band(noise(0.9), 1500, 7000) * env(0.9, 0.08, 0.3) * 0.4, t)
    return out


def amb_pal():
    """Dalt del pal: vent fort, el mar a sota i una driça que pica contra el ferro."""
    d = 20
    vent = band(noise(d), 300, 3500) * _lfo(d, 0.35, 0.3, 1.0) * 0.8 + band(noise(d), 700, 900) * _lfo(d, 0.25, 0, 1) * 0.8
    out = vent + _onades(d, 100, 1500, 0.15) * 0.35
    for t in (2.0, 2.6, 9.3, 15.1, 15.5):
        _posa(out, metall(1250, 0.5, 0.12, (1, 2.7, 5.1)) * 0.08, t)
    return out


def amb_caixa():
    """La caixa de cadenes: el mar que pica a la proa, aigua que es mou, gotes i la cadena."""
    d = 20
    out = band(noise(d), 40, 300) * _lfo(d, 0.22, 0.1, 1.0) ** 3 * 1.4 + band(noise(d), 300, 1200) * _lfo(d, 0.3, 0.1, 0.6) * 0.3
    for t in (1.2, 6.8, 7.9, 12.3, 17.7):
        _posa(out, _gota() * 0.25, t)
    for t in (4.5, 14.0):
        _posa(out, metall(2200, 0.4, 0.08, (1, 1.6, 2.9)) * 0.06, t)
    return out


def amb_fosc():
    """El vaixell sense generador: cap brunzit, només el casc, el mar i gotes."""
    d = 20
    out = _onades(d, 60, 400, 0.15) * 0.5
    for t, f in [(1.5, 160), (6.0, 220), (9.8, 140), (14.5, 190)]:
        _posa(out, _grinyol(f) * 0.2, t)
    for t in (3.3, 11.1, 17.4):
        _posa(out, _gota() * 0.2, t)
    return out


AMBIENTS = {
    'amb_maquines': amb_maquines, 'amb_coberta': amb_coberta, 'amb_pont': amb_pont, 'amb_mar': amb_mar,
    'amb_pal': amb_pal, 'amb_caixa': amb_caixa, 'amb_fosc': amb_fosc,
}


SONS = {
    'miol': miol, 'mossegada': mossegada, 'clic': lambda: clic(), 'estatica': estatica, 'estatica_neta': estatica_neta,
    'panell': panell, 'valvula': valvula, 'bomba': bomba, 'frontissa': frontissa, 'clau_vella': clau_vella,
    'muntacarregues': muntacarregues, 'terminal': terminal, 'enviat': enviat, 'impressora': impressora, 'antena': antena,
    'clau_tubs': clau_tubs, 'travesser': travesser, 'pot': pot, 'cisalla': cisalla, 'cops': cops, 'vies': vies,
    'generador_para': generador_para, 'generador_engega': generador_engega, 'telefon_satellit': telefon_satellit,
    'portatil': portatil, 'porta': porta, 'porta_estanca': porta_estanca, 'escotilla': escotilla, 'escala': escala,
}

# Volum de cada so respecte del màxim.
VOLUM = {'estatica': 0.5, 'estatica_neta': 0.5, 'impressora': 0.6, 'terminal': 0.5, 'telefon_satellit': 0.5, 'bomba': 0.7}


def write(name, x, rms=None):
    """Normalitza pel pic (o, als sons de fons, per la intensitat mitjana `rms`) i desa l'.ogg."""
    if rms:
        x = x - np.mean(x)
        x = x / max(1e-9, np.sqrt(np.mean(x ** 2))) * rms
        x = np.tanh(x / 0.9) * 0.9  # cap pic no satura
    else:
        x = x / max(1e-9, np.max(np.abs(x))) * 0.8 * VOLUM.get(name, 1.0)
    pcm = (np.clip(x, -1, 1) * 32767).astype('<i2')
    with tempfile.NamedTemporaryFile(suffix='.wav') as tmp:
        with wave.open(tmp.name, 'wb') as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(pcm.tobytes())
        subprocess.run(
            # Els bucles, en Opus: amb Vorbis, Chrome no retalla el farciment del final i el bucle faria un forat.
            ['ffmpeg', '-loglevel', 'error', '-y', '-i', tmp.name, *(['-c:a', 'libopus', '-b:a', '96k'] if rms else ['-c:a', 'libvorbis', '-q:a', '5']), str(OUT / f'{name}.ogg')],
            check=True,
        )


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
        write(name, make(), rms=0.07)
    print(f'✔ {len(only) or len(SONS) + len(AMBIENTS)} sons a {OUT}')


if __name__ == '__main__':
    main()
