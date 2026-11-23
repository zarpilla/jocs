#!/usr/bin/env python3
"""
`npm run sons`: genera els efectes de so de L'Última Arrel a `game/audio/sfx/` (.ogg).

Tot és sintetitzat (ones i soroll), sense mostres de fora: es pot tornar a generar sempre igual.
Per canviar un so per un de fet a mà, n'hi ha prou de posar el fitxer amb el mateix nom a
`game/audio/sfx/` i treure'l de la llista `SONS` d'aquí baix (si no, el sobreescriuria).

Dues paletes (guió, «Regles del món» §4 i «So»):
- el bosc: fusta, vent, ocells de debò (cada un diferent) i el brunzit turquesa de la xarxa de fongs;
- NaturaPlus: bips nets, fluorescents, música d'ascensor i els ocells sintètics «versió prèmium»
  (sempre el mateix refilet, cada quatre segons).
El crit dels arbres (`crit`) és el tema: un acord greu d'orgue de fusta i una veu que puja. A l'epíleg
torna en major, molt fluix (`resposta`).

Hi ha dues menes de sons:
- els efectes (`SONS`): curts, normalitzats pel pic;
- els sons de fons (`AMBIENTS`, prefix `amb_`): bucles sense costura, normalitzats per la intensitat
  mitjana, que sonen sota la música (vegeu `ambient` a adapters/benne/mapping.json).

`python3 tools/sons.py crit amb_centraleta` en fa només uns quants.

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
rng = np.random.default_rng(23)  # sempre els mateixos sons

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


def corba(d, claus):
    """Una corba feta de claus `(0-1, valor)` al llarg de `d` segons."""
    u = np.linspace(0, 1, int(SR * d))
    return np.interp(u, [a for a, _ in claus], [b for _, b in claus])


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


def formants(x, picos):
    """Passa `x` per uns quants formants fixos `(centre, amplada, guany)` (amb la FFT)."""
    spec = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    mask = sum(g * np.exp(-((f - c) / w) ** 2) for c, w, g in picos)
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


def _veu(d, f0_keys, formants_keys, ale=0.09, seed=1, vibrato=0.03):
    """Una veu: un to (amb vibrato) passat per formants que es mouen. Les claus són (0-1, valor)."""
    n = int(SR * d)
    u = np.arange(n) / n
    k = lambda keys: np.interp(u, [a for a, _ in keys], [b for _, b in keys])
    vib = 1 + vibrato * np.sin(2 * np.pi * 5 * t(d)[:n]) * np.minimum(1, u * 4)
    ph = np.cumsum(k(f0_keys) * vib) / SR
    so = sum(np.sin(2 * np.pi * h * ph) / h ** 0.8 for h in range(1, 18))
    so = so + ale * np.random.default_rng(seed).uniform(-1, 1, n)  # (no toca el `rng` dels altres sons)
    x = sum(g * _ressonador(so, k(keys), bw) for keys, bw, g in formants_keys)
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


def fusta(f, d=0.2, decay=0.04):
    """Un cop de fusta: to curt, amb un parcial de fusta (×2,7) i el clic."""
    return mix((osc(f, d) + 0.5 * osc(f * 2.7, d) + 0.2 * osc(f * 5.2, d)) * env(d, 0.001, decay), clic(f * 3, 0.02) * 0.3)


def xiuxiueig(d, lo, hi, attack=0.05, release=0.2):
    """Soroll de banda (aire, aigua) amb entrada i sortida suaus."""
    return band(noise(d), lo, hi) * env(d, attack, None, release)


def gota(f=1700, d=0.08):
    return osc(np.linspace(f, f * 0.53, int(SR * d)), d) * env(d, 0.001, 0.02)


def bombolles(d, quantes, fmin=300, fmax=1200):
    """Bombolles que petiten (aigua que corre, fang): gotetes que pugen de to."""
    out = silence(d + 0.1)
    for _ in range(quantes):
        f = rng.uniform(fmin, fmax)
        dd = rng.uniform(0.02, 0.06)
        b = osc(np.linspace(f, f * 1.6, int(SR * dd)), dd) * env(dd, 0.002, dd / 3, 0.005)
        i = int(SR * rng.uniform(0, d))
        out[i:i + len(b)] += b * rng.uniform(0.3, 1)
    return out


def raig(d, lo=400, hi=4000):
    """Aigua que corre: soroll de banda que tremola (no és mai igual)."""
    x = band(noise(d), lo, hi)
    lent = band(rng.uniform(-1, 1, len(x)), None, 12)
    tremola = 0.75 + 0.25 * lent / max(1e-9, np.std(lent))
    return x * np.clip(tremola, 0.3, 1.3)


def grinyol(d, ritme, ressonancies, aspre=0.4):
    """Un grinyol (fusta o metall que frega): cops petits, un per cicle (`ritme`, en Hz, pot ser una corba),
    passats per les ressonàncies del material `(centre, guany)`."""
    n = int(SR * d)
    f = np.broadcast_to(np.asarray(ritme, dtype=float), (n,)) if np.ndim(ritme) == 0 else np.asarray(ritme)[:n]
    ph = np.cumsum(f) / SR
    cops = (np.diff(np.floor(ph), prepend=0) > 0).astype(float)
    cops *= 1 - aspre + aspre * rng.uniform(0, 1, n)  # el frec no és mai regular
    return sum(g * band(cops, c * 0.88, c * 1.12) for c, g in ressonancies)


def ocell(tipus=None, f0=None):
    """Un ocell de debò: cada cop una mica diferent (to, ritme, nombre de notes)."""
    tipus = tipus or rng.choice(['pit', 'merla', 'refila'])
    if tipus == 'pit':
        # «Pit-pit-pit»: notes curtes que cauen.
        f0 = f0 or rng.uniform(3600, 5200)
        parts = []
        s = 0.0
        for _ in range(int(rng.integers(2, 6))):
            dd = rng.uniform(0.035, 0.07)
            parts.append((osc(lin(f0 * 1.18, f0 * 0.82, dd), dd) * env(dd, 0.004, None, 0.012), s))
            s += rng.uniform(0.08, 0.15)
        return mix(*parts)
    if tipus == 'merla':
        # Una frase lenta i flautada, més greu: notes que llisquen.
        f0 = f0 or rng.uniform(1700, 2500)
        parts = []
        s = 0.0
        for _ in range(int(rng.integers(3, 6))):
            dd = rng.uniform(0.09, 0.22)
            fa = f0 * rng.uniform(0.85, 1.35)
            fb = fa * rng.uniform(0.85, 1.2)
            so = osc(lin(fa, fb, dd), dd) + 0.12 * osc(lin(2 * fa, 2 * fb, dd), dd)
            parts.append((so * np.sin(np.linspace(0, np.pi, int(SR * dd))) ** 1.5, s))
            s += dd + rng.uniform(0.02, 0.08)
        return mix(*parts)
    # Refilet: un trinat ràpid que s'apaga.
    f0 = f0 or rng.uniform(3000, 4500)
    dd = rng.uniform(0.4, 0.8)
    x = t(dd)
    f = f0 * (1 + 0.12 * np.sin(2 * np.pi * rng.uniform(18, 28) * x)) * lin(1.05, 0.9, dd)
    return osc(f, dd) * env(dd, 0.01, dd / 2, 0.03)


def rauc(f=170, d=0.5, pols=18):
    """Un gripau: un rauc greu a polsos (el «krrrrr»)."""
    x = t(d)
    portadora = band(osc(f * lin(1.05, 0.95, d), d, 'saw'), f * 0.8, f * 7)
    pulsos = (0.5 + 0.5 * np.sin(2 * np.pi * pols * x - np.pi / 2)) ** 3
    return portadora * pulsos * env(d, 0.02, None, 0.08)


def brunzit_turquesa(d, f=110, brillo=1.0, seed=5):
    """El brunzit de la xarxa de fongs: un acord de quintes que batega (cordes de terra), càlid."""
    r = np.random.default_rng(seed)
    out = np.zeros(int(SR * d))
    for mult, a in ((0.5, 0.7), (1, 1), (1.5, 0.55), (2, 0.4), (3, 0.18)):
        for des in (-0.25, 0.25):  # dues veus una mica desafinades: el batec lent
            out += a * osc(f * mult + des, d, phase=r.uniform(0, 6.28))
    # La lluïssor: harmònics aguts que s'encenen i s'apaguen.
    for mult in (12, 16, 20):
        out += 0.04 * brillo * osc(f * mult, d) * (0.5 + 0.5 * osc(0.25 * mult / 4, d, phase=r.uniform(0, 6.28)))
    return out / 8


def espurnes(d, quantes, fmin=1800, fmax=4200):
    """Puntets de llum que sonen: tocs de vidre suaus i aguts (els fils turquesa que s'encenen)."""
    out = silence(d + 0.6)
    for _ in range(quantes):
        f = rng.uniform(fmin, fmax)
        p = (osc(f, 0.6) + 0.3 * osc(f * 2.01, 0.6)) * env(0.6, 0.003, 0.15)
        i = int(SR * rng.uniform(0, d))
        out[i:i + len(p)] += p * rng.uniform(0.3, 1)
    return out


def bip_net(f, d=0.08, forma='sine'):
    """Un bip de tauleta: net, sense cap calidesa."""
    return osc(f, d, forma) * env(d, 0.002, None, 0.01)


def radio(x, lo=350, hi=3200, soroll=0.04):
    """Com si sortís per una ràdio petita: banda estreta, una mica saturat i amb estàtica."""
    y = band(x, lo, hi)
    y = y / max(1e-9, np.max(np.abs(y)))
    y = np.tanh(2.0 * y) + band(noise(len(y) / SR), 1500, 7000) * soroll
    return y


def orgue_fusta(f, d, rng_local):
    """Un tub d'orgue de fusta: gairebé una sinusoide, amb els harmònics senars fluixos i l'aire."""
    so = osc(f, d, phase=rng_local.uniform(0, 6.28)) + 0.25 * osc(2 * f, d) + 0.12 * osc(3 * f, d) + 0.04 * osc(5 * f, d)
    respira = 1 + 0.05 * osc(rng_local.uniform(0.2, 0.5), d, phase=rng_local.uniform(0, 6.28))
    return so * respira


# ─── El crit dels arbres ────────────────────────────────────────────────────


def _crit(d, acord, f0_keys, veu_vol, fosc):
    """L'acord greu i llarg (orgue de fusta i el buf de l'aire als tubs) i una veu que puja."""
    r = np.random.default_rng(11)
    greu = sum(a * orgue_fusta(f, d, r) for f, a in acord) * env(d, 1.0, None, 1.6)
    buf = band(noise(d), 200, 1500) * env(d, 0.5, None, 1.8) * 0.04
    dv = d - 1.2
    # La veu: entra fosca («o») i s'obre («a») a mesura que puja.
    veu, k = _veu(dv, f0_keys, [
        ([(0, 450), (0.5, 650), (1, 750)], 90, 1.0),
        ([(0, 850), (0.5, 1050), (1, 1200)], 120, 0.55),
        ([(0, 2500), (1, 2700)], 200, 0.2),
    ], ale=0.04, seed=7, vibrato=0.012)
    veu = band(veu, 150, fosc) * k([(0, 0), (0.12, 0.6), (0.4, 0.8), (0.75, 1), (0.92, 0.8), (1, 0)])
    veu /= max(1e-9, np.max(np.abs(veu)))
    greu /= max(1e-9, np.max(np.abs(greu)))
    return mix(greu + buf, (veu * veu_vol, 0.8))


def crit():
    """El crit dels arbres: Re menor greu, i una veu que puja de Re a La i a Re, i s'hi queda."""
    acord = ((36.7, 0.6), (73.4, 1.0), (110.0, 0.7), (146.8, 0.55), (174.6, 0.4), (220.0, 0.3))
    x = _crit(6.6, acord, [(0, 280), (0.08, 294), (0.3, 294), (0.45, 440), (0.6, 440), (0.75, 587), (1, 587)], 0.55, 3000)
    x = x + brunzit_turquesa(len(x) / SR, 110, 0.4) * env(len(x) / SR, 2.0, None, 1.5) * 0.25
    return eco(x, cua=1.4, humit=0.45, fosc=3000)


def resposta():
    """La resposta del bosc, a l'epíleg: el crit en Re major, molt fluix, i el brunzit turquesa sota terra."""
    acord = ((73.4, 1.0), (110.0, 0.6), (146.8, 0.5), (185.0, 0.45), (220.0, 0.3))
    x = _crit(4.4, acord, [(0, 294), (0.35, 294), (0.55, 370), (0.7, 440), (1, 440)], 0.35, 2200)
    d = len(x) / SR
    terra = band(noise(d), 30, 160) * 0.25 + osc(55, d) * 0.35 + osc(55.4, d) * 0.25
    x = x + (brunzit_turquesa(d, 110, 1.0) * 0.6 + terra) * env(d, 1.5, None, 1.2) * 0.6
    x = mix(x, (espurnes(d - 1.5, 10, 2200, 4400) * 0.06, 0.8))
    return eco(x, cua=1.0, humit=0.4, fosc=2500)


# ─── El walkie i els aparells ──────────────────────────────────────────────


def walkie():
    """El «xxxt» del walkie: el clic del botó i un esclat d'estàtica que es talla."""
    d = 0.2
    estatica = band(noise(d), 900, 5000) * (0.75 + 0.25 * osc(60, d, 'square')) * env(d, 0.004, None, 0.04)
    return mix(clic(2200, 0.02) * 0.8, (estatica, 0.012))


def walkie_grava():
    """Gravar amb el walkie: el clic, «bip» curt i el to llarg que diu que grava."""
    return mix(clic(2000, 0.02), (bip_net(1000, 0.08) * 0.6, 0.03), (bip_net(1000, 0.35) * 0.6, 0.18),
               (band(noise(0.5), 1000, 4000) * env(0.5, 0.02, None, 0.2) * 0.05, 0.18))


def ruleta():
    """La ruleta de la ràdio de l'altaveu: clics de rodeta i, entre clic i clic, emissores que xiulen."""
    parts = []
    s = 0.0
    for i in range(12):
        parts.append((clic(rng.uniform(2800, 3400), 0.02) * 0.7, s))
        dd = rng.uniform(0.05, 0.09)
        f = rng.uniform(600, 2400)
        sintonia = osc(lin(f, f * rng.uniform(0.6, 1.4), dd), dd) * env(dd, 0.005, None, 0.02) * 0.12
        parts.append((sintonia + band(noise(dd), 800, 5000) * env(dd, 0.005, None, 0.02) * 0.15, s + 0.01))
        s += dd + rng.uniform(0.0, 0.02)
    return mix(*parts)


def radar():
    """El radar que s'encén: un «uiuuu» que puja i un bip que tremola fins que s'aguanta."""
    d = 1.4
    puja = osc(lin(200, 1200, 0.3, 0.7), 0.3) * env(0.3, 0.01, None, 0.03) * 0.5
    x = t(d)
    tremola = np.exp(-x / 0.5)
    f = 1200 * (1 + 0.04 * tremola * np.sin(2 * np.pi * 9 * x))
    bip = osc(f, d) * (1 - 0.6 * tremola * (0.5 + 0.5 * np.sin(2 * np.pi * 14 * x))) * env(d, 0.01, None, 0.3)
    ping = (osc(2400, 0.5) + 0.3 * osc(4800, 0.5)) * env(0.5, 0.002, 0.12)
    return mix(puja, (bip * 0.5, 0.28), (ping * 0.4, 1.3))


def pip():
    """Un aparell que s'apaga, trist: «pi... piuuu»."""
    return mix(bip_net(1000, 0.1, 'square') * 0.5,
               (osc(lin(900, 220, 0.7, 0.8), 0.7, 'square') * env(0.7, 0.01, 0.35, 0.05) * 0.5, 0.25))


def altaveu_iri():
    """La veu de l'Iri per l'altaveu gros: el xiulet d'acoblament, un «bloop» i la veu saturadíssima, amb rebot."""
    acoble = osc(lin(2600, 3100, 0.45), 0.45) * lin(0, 1, 0.45, 2) * env(0.45, 0.01, None, 0.02) * 0.4
    bloop = osc(lin(480, 110, 0.22), 0.22) * env(0.22, 0.004, 0.08) * 0.8
    veu, k = _veu(1.3, [(0, 250), (0.25, 310), (0.5, 290), (0.75, 330), (1, 220)], [
        ([(0, 450), (0.25, 650), (0.5, 400), (0.75, 750), (1, 600)], 100, 1.0),
        ([(0, 1900), (0.25, 1100), (0.5, 900), (0.75, 1300), (1, 1000)], 150, 0.7),
        ([(0, 2700), (1, 2600)], 250, 0.3),
    ], ale=0.12, seed=3)
    # Síl·labes: «què-vols-que-di-gui».
    sil = k([(0, 0), (0.05, 1), (0.18, 1), (0.22, 0.2), (0.27, 1), (0.42, 1), (0.47, 0.2), (0.52, 1), (0.62, 0.3),
             (0.66, 1), (0.78, 0.3), (0.82, 1), (0.97, 1), (1, 0)])
    veu = veu * sil
    veu = band(np.tanh(8 * veu / max(1e-9, np.max(np.abs(veu)))), 400, 3500)
    rebot = mix(veu, (veu * 0.35, 0.17), (veu * 0.15, 0.34))
    return mix(acoble, (bloop, 0.42), (rebot, 0.55))


def sensors_esternut():
    """Els sensors d'aire que esternuden: l'alarma, tres «a... a... ATXIM!» de màquina i un bip que es queixa."""
    alarma = mix(*[(bip_net(f, 0.09, 'square') * 0.35, s) for s, f in ((0, 1500), (0.14, 1500), (0.28, 1900))])
    def esternut(k):
        # L'aire que entra: un to de màquina que puja a batzegades.
        d = 0.7
        x = t(d)
        a = osc(lin(380 * k, 900 * k, d, 1.4), d, 'square') * (0.6 + 0.4 * (np.sin(2 * np.pi * 5 * x) > 0))
        a = band(a, 300, 4000) * env(d, 0.05, None, 0.05) * lin(0.3, 1, d) * 0.25
        txim = band(noise(0.3), 1500 * k, 9000) * env(0.3, 0.002, 0.07)
        cop = cop_sord(0.2, 60, 400, 0.05) * 0.8
        molla = osc(320 * k * (1 + 0.1 * osc(9, 0.6)), 0.6) * env(0.6, 0.003, 0.15) * 0.2  # la columna que trontolla
        return mix(a, (txim, d), (cop, d), (molla, d + 0.02))
    queixa = osc(lin(1400, 700, 0.3), 0.3, 'square') * env(0.3, 0.005, None, 0.05) * 0.2
    return mix(alarma, (esternut(1.0), 0.45), (esternut(1.25) * 0.85, 0.9), (esternut(0.8) * 0.9, 1.3), (queixa, 2.4))


def xarxa_encesa():
    """La xarxa de fongs que s'encén: un brunzit greu que puja fins a l'acord turquesa, i espurnes que s'hi encenen."""
    d = 4.0
    f = np.concatenate([lin(40, 110, 1.6, 0.6), np.full(int(SR * (d - 1.6)), 110.0)])
    puja = sum(a * osc(f * m, d) for m, a in ((1, 1), (1.5, 0.5), (2, 0.4), (3, 0.15))) * env(d, 0.3, None, 1.2)
    brunz = brunzit_turquesa(d, 110, 1.2) * lin(0, 1, d, 0.7) * env(d, 0.5, None, 1.2)
    whoom = band(noise(d), 80, 900) * corba(d, [(0, 0), (0.35, 1), (0.6, 0.2), (1, 0)]) * 0.3
    return mix(puja * 0.5 + brunz * 2 + whoom, (espurnes(2.0, 22) * 0.12, 1.4))


# ─── Fusta, portes i coses que grinyolen ────────────────────────────────────


def porta_roure():
    """Una porteta de roure dins d'un arbre: el grinyol de la frontissa i un toc suau en acabar d'obrir-se."""
    d = 1.0
    ritme = corba(d, [(0, 45), (0.3, 120), (0.6, 160), (1, 80)])
    g = grinyol(d, ritme, ((520, 1.0), (1150, 0.7), (2300, 0.3))) * env(d, 0.1, None, 0.2)
    return mix(clic(1200, 0.04) * 0.4, (g * 3.0, 0.05), (fusta(180, 0.3, 0.05) * 0.25, 1.05))


def porta_topa():
    """Un cop sord de fusta: una porta (o un cap) que topa."""
    return mix(cop_sord(0.4, 50, 500, 0.07), fusta(140, 0.4, 0.06) * 0.6, (clic(800, 0.03) * 0.3, 0.005))


def gronxador():
    """El gronxador de branca: la corda que grinyola amunt i avall (dues anades) i el vent entre les fulles."""
    d = 3.0
    vent = band(noise(d), 300, 3000) * corba(d, [(0, 0), (0.3, 0.6), (0.6, 0.4), (1, 0)]) * 0.12
    def anada(alt):
        dd = 0.6
        r = corba(dd, [(0, 220), (0.5, 380), (1, 300)]) * alt
        return grinyol(dd, r, ((900, 1.0), (1900, 0.6), (3200, 0.2))) * np.sin(np.linspace(0, np.pi, int(SR * dd))) * 3
    return mix(vent, (anada(1.0), 0.2), (anada(0.8), 0.95), (anada(1.0) * 0.8, 1.7), (anada(0.8) * 0.6, 2.4))


def roda():
    """Una roda de metall que grinyola en girar: tres grinyols, i la grava que cruix."""
    d = 2.2
    grava = band(noise(d), 300, 2500) * (rng.uniform(0, 1, int(SR * d)) > 0.85) * env(d, 0.1, None, 0.3) * 0.25
    def volta():
        dd = 0.45
        r = corba(dd, [(0, 700), (0.5, 900), (1, 650)])
        return grinyol(dd, r, ((1800, 1.0), (3600, 0.5), (5100, 0.2)), 0.2) * np.sin(np.linspace(0, np.pi, int(SR * dd))) * 3
    return mix(band(grava, 300, 3000), (volta(), 0.1), (volta() * 0.8, 0.8), (volta() * 0.9, 1.5))


def segell():
    """El segell de goma: «pof» al tamponet i «CLAC» damunt del paper (amb la taula que ressona)."""
    pof = band(noise(0.12), 100, 900) * env(0.12, 0.003, 0.03) * 0.4
    clac = mix(fusta(320, 0.3, 0.035), clic(2500, 0.03) * 0.8, cop_sord(0.25, 70, 600, 0.05) * 0.8)
    return mix(pof, (clac, 0.3))


def campaneta():
    """Una campaneta petita de bronze: «dring-dring»."""
    toc = lambda: mix(metall(2350, 1.6, 0.5, (1, 1.98, 2.66, 4.1, 6.3), (1, 0.4, 0.5, 0.25, 0.1)), clic(5000, 0.01) * 0.3)
    return mix(toc(), (toc() * 0.8, 0.28), (toc() * 0.35, 0.6))


def ampolles():
    """Ampolles de plàstic buides que cauen i rodolen: tocs buits i el plàstic que cruix."""
    def ampolla(f):
        d = 0.25
        tok = (osc(f, d) + 0.5 * osc(f * 2.3, d)) * env(d, 0.001, 0.045)
        buit = band(noise(d), f * 0.8, f * 1.6) * env(d, 0.001, 0.03) * 0.7
        return tok + buit
    cops = [(ampolla(rng.uniform(350, 750)) * rng.uniform(0.5, 1), s)
            for s in (0, 0.12, 0.2, 0.37, 0.45, 0.62, 0.8, 0.95, 1.2)]
    cruix = [(clic(rng.uniform(2500, 6000), 0.02) * rng.uniform(0.2, 0.5), rng.uniform(0, 1.4)) for _ in range(25)]
    return mix(*cops, *cruix)


# ─── Fades, gripaus i aigua ─────────────────────────────────────────────────


def xiulet():
    """El xiulet d'ortiga: una fulla entre els dits que xiula agut, aspre, i s'escapa amunt."""
    d = 1.3
    x = t(d)
    f = corba(d, [(0, 1800), (0.12, 2600), (0.6, 2650), (0.75, 3100), (1, 2600)])
    f = f * (1 + 0.02 * np.sin(2 * np.pi * 7 * x) * np.minimum(1, x / 0.3))
    so = osc(f, d) + 0.35 * osc(2 * f, d) + 0.1 * osc(3 * f, d)
    aspre = 1 + 0.25 * osc(f / 20, d, 'square')  # la fulla que vibra
    ale = band(noise(d), 2000, 7000) * 0.08
    return (so * aspre + ale) * env(d, 0.03, None, 0.12)


def fades_vol():
    """Les fades que baixen en picat: aleteig ràpid i una xiulada que cau (tres fades, una darrere l'altra)."""
    def fada(k):
        d = 1.1
        ales = (0.5 + 0.5 * np.sin(2 * np.pi * np.cumsum(lin(22, 34, d)) / SR)) ** 2
        aire = band(noise(d), 600 * k, 4000 * k) * ales * 0.6
        whoosh = band(noise(d), 300, 2500) * corba(d, [(0, 0), (0.6, 1), (1, 0)]) * 0.4
        xiu = osc(lin(2600 * k, 1100 * k, d, 0.8), d) * corba(d, [(0, 0), (0.2, 1), (1, 0)]) * 0.08
        return (aire + whoosh + xiu) * env(d, 0.05, None, 0.2)
    return mix(fada(1.0), (fada(1.15) * 0.8, 0.13), (fada(0.9) * 0.7, 0.27))


def fades_mengen():
    """Les fades que mengen melmelada: «nyam-nyam» llefiscós i un glop al final."""
    parts = []
    s = 0.0
    for i in range(9):
        d = rng.uniform(0.09, 0.14)
        nyam = band(noise(d), 300, 2500) * env(d, 0.004, d / 3) * 0.6
        boca = osc(lin(rng.uniform(500, 700), 350, d), d, 'square') * env(d, 0.004, d / 3) * 0.12
        llefisc = bombolles(d, 3, 400, 900) * 0.25
        parts.append((nyam + boca + llefisc[:len(nyam)], s))
        s += rng.uniform(0.13, 0.19)
    glop = osc(lin(520, 160, 0.14), 0.14) * env(0.14, 0.004, 0.05) * 0.8
    return mix(*parts, (glop, s + 0.15))


def esternut_fada():
    """Una fada que esternuda: «i-i-txi!», agut i petitíssim."""
    veu, k = _veu(0.38, [(0, 900), (0.45, 1050), (0.55, 950), (1, 1350)], [
        ([(0, 350), (1, 400)], 90, 1.0), ([(0, 2600), (1, 2900)], 200, 0.8),
    ], ale=0.2, seed=9)
    veu = veu * k([(0, 0), (0.1, 1), (0.4, 0.3), (0.5, 1), (0.9, 1), (1, 0)])
    txi = band(noise(0.15), 3500, 11000) * env(0.15, 0.002, 0.04)
    return mix(veu / max(1e-9, np.max(np.abs(veu))) * 0.5, (txi, 0.38))


def rierol():
    """L'aigua que torna a córrer: borbolleig que creix, el rierol, i dos gripaus que se n'alegren."""
    d = 4.5
    corre = raig(d, 400, 4000) * corba(d, [(0, 0), (0.3, 0.4), (0.6, 1), (1, 1)]) * env(d, 0.05, None, 0.6) * 0.5
    glops = bombolles(d - 0.5, 50, 250, 900) * 0.35
    return mix(corre, glops, (rauc(160, 0.55) * 0.5, 2.6), (rauc(140, 0.6, 15) * 0.45, 3.4))


def passos_gripau():
    """Un gripau que camina amb solemnitat: passes lentes i molles."""
    def passa(k):
        cop = band(noise(0.15), 150, 2000) * env(0.15, 0.002, 0.03)
        moll = bombolles(0.15, 5, 200, 600) * 0.4
        greu = cop_sord(0.15, 50, 250, 0.04) * 0.8
        return mix(cop * k, (moll, 0.03), greu)
    return mix(*[(passa(rng.uniform(0.8, 1.0)), 0.7 * i) for i in range(4)])


def bastida():
    """La Vet que s'enfila per la bastida de la pantalla: els tubs d'acer que dringuen sota les botes d'aigua (cinc
    passes, cada cop més amunt i més fluixes) i, a dalt de tot, el paper de la caseta que es posa."""
    passes = []
    for i in range(5):
        f = 620 + i * 70 + rng.uniform(-20, 20)
        cop = metall(f, 0.35, decay=0.12, harm=(1, 2.6, 4.9), amp=(1, 0.45, 0.2)) * (1 - i * 0.12)
        bota = cop_sord(0.12, 60, 300, 0.03) * 0.6
        passes.append((mix(cop, bota), 0.32 * i))
    paper = band(noise(0.25), 1500, 6000) * env(0.25, 0.02, None, 0.15) * 0.25
    return mix(*passes, (paper, 1.75))


# ─── La ràdio de l'altaveu (canals que no són el 7) ─────────────────────────


def futbol():
    """Un partit per la ràdio: la multitud lluny, que s'aixeca, i el xiulet de l'àrbitre."""
    d = 3.0
    multitud = band(noise(d), 300, 2500) * corba(d, [(0, 0.5), (0.4, 0.6), (0.7, 1), (1, 0.7)])
    veus = _murmuri(d, 10) * 1.5
    xiulet_arbitre = osc(3000 * (1 + 0.03 * osc(30, 0.5)), 0.5) * env(0.5, 0.01, None, 0.05) * 0.15
    x = mix(multitud * 0.6 + veus, (xiulet_arbitre, 1.6))
    return radio(x, 350, 3000) * env(len(x) / SR, 0.05, None, 0.2)


def ascensor():
    """Música d'ascensor per la ràdio: piano elèctric en Fa major, el baix, una melodia de flauta massa contenta."""
    ppm = 100
    temps = 60 / ppm
    d = 8 * temps + 0.6
    out = silence(d)
    acords = ((41, (57, 60, 64, 67)), (40, (55, 59, 62, 67)), (38, (57, 60, 65, 69)), (43, (53, 59, 62, 65)))
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)
    def rhodes(f, dd):
        return (osc(f, dd) + 0.3 * osc(2 * f, dd) * env(dd, 0.002, 0.08) + 0.1 * osc(7 * f, dd) * env(dd, 0.001, 0.02)) * env(dd, 0.004, 0.8, 0.1)
    for i, (b, veus) in enumerate(acords):
        s = 2 * i * temps
        for e in (0, 1.5):
            for v in veus:
                x = rhodes(hz(v), 1.0) * 0.15
                j = int(SR * (s + e * temps))
                out[j:j + len(x)] += x[: len(out) - j]
        x = osc(hz(b - 12), 1.1) * env(1.1, 0.01, 0.3, 0.1) * 0.5
        j = int(SR * s)
        out[j:j + len(x)] += x[: len(out) - j]
    tema = ((0, 76, 1), (1, 79, 1), (2, 81, 2), (4, 79, 1), (5, 76, 1), (6, 74, 2), (8, 72, 1), (9, 74, 1), (10, 76, 3), (13, 74, 2))
    for e, nota, dur in tema:
        dd = dur * temps / 2 + 0.1
        x = (osc(hz(nota), dd) + 0.05 * osc(2 * hz(nota), dd)) * env(dd, 0.03, None, 0.08) * 0.35
        j = int(SR * e * temps / 2)
        out[j:j + len(x)] += x[: len(out) - j]
    return radio(out, 300, 3500, 0.03) * env(d, 0.15, None, 0.4)


def anunci():
    """L'anunci de NaturaPlus: «Na-tu-ra-Plus!» en campanetes de sintetitzador, l'acord brillant i el «ding»."""
    def fm(f, d):
        x = t(d)
        index = 3 * np.exp(-x / 0.15)
        return np.sin(2 * np.pi * f * x + index * np.sin(2 * np.pi * 3.5 * f * x)) * env(d, 0.002, 0.3)
    notes = ((0.0, 1047), (0.18, 1319), (0.36, 1568), (0.54, 2093))
    jingle = mix(*[(fm(f, 0.6) * 0.5, s) for s, f in notes])
    acord = sum(osc(f, 1.2, 'square') * 0.06 + osc(f, 1.2) * 0.1 for f in (523, 659, 784, 1047)) * env(1.2, 0.01, 0.4)
    ding = (osc(2637, 1.0) + 0.3 * osc(5274, 1.0)) * env(1.0, 0.002, 0.25) * 0.4
    x = mix(jingle, (acord, 0.54), (ding, 1.3))
    x = mix(x, (x * 0.25, 0.12))  # eco digital, net
    return radio(x, 250, 5000, 0.02)


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


def _fulles(d, vol=0.3, lo=500, hi=6000, rafegues=0.2):
    """El vent entre les fulles: un xiuxiueig ample que puja i baixa, amb fulles que fan fru-fru."""
    vent = band(noise(d), lo, hi) * _lfo(d, rafegues, 0.15, 1.0) ** 1.5
    fregs = band(noise(d), 2000, 8000) * (rng.uniform(0, 1, int(SR * d)) > 0.97) * _lfo(d, 0.3, 0, 1) ** 2 * 0.6
    return (vent + band(fregs, 2000, 8000)) * vol


def _ocells(out, d, quants, tipus=None, vol=0.1):
    for _ in range(quants):
        _posa(out, ocell(tipus) * vol * rng.uniform(0.4, 1.0), rng.uniform(0, d))


def _grills(out, d, periode=0.8, vol=0.03, f=4600):
    """Grills: tres polsos curts, cada `periode` segons (ha de dividir `d`), que van i venen."""
    pols = osc(f, 0.018) * np.sin(np.linspace(0, np.pi, int(SR * 0.018)))
    cant = mix(pols, (pols, 0.03), (pols, 0.06))
    forca = _lfo(d, 0.15, 0.2, 1.0)
    for i in range(int(round(d / periode))):
        s = i * periode
        _posa(out, cant * vol * forca[int(SR * s) % len(forca)], s)


def _ocells_premium(out, d, vol):
    """Els «Sons del Bosc — versió prèmium»: el mateix refilet sintètic exacte, cada quatre segons."""
    dd = 0.5
    x = t(dd)
    f = 2800 + 600 * np.sign(np.sin(2 * np.pi * 8 * x)) + lin(0, 500, dd)  # dos tons que salten, de joguina
    refilet = np.round(osc(f, dd) * 6) / 6 * env(dd, 0.01, None, 0.05)  # pocs bits: es nota que és de mentida
    refilet = band(refilet, 800, 6000)
    for i in range(int(d // 4)):
        _posa(out, refilet * vol, 1.0 + 4 * i)
        _posa(out, refilet * vol * 0.7, 1.6 + 4 * i)


def amb_vora_bosc():
    """La vora del bosc al capvespre: vent fluix entre les fulles, els últims ocells que s'adormen i els grills."""
    d = 24
    out = _fulles(d, 0.35, 300, 4000, 0.15) + band(noise(d), 60, 300) * 0.12 * _lfo(d, 0.1, 0.5, 1)
    _ocells(out, d, 7, 'merla', 0.09)
    _ocells(out, d, 3, 'pit', 0.05)
    _grills(out, d, 0.8, 0.03)
    return out


def amb_centraleta(encesa=False):
    """La centraleta, una cova d'arrels: l'aire quiet, gotes amb ressò, la fusta que cruix i el brunzit dels
    fongs (gairebé apagat; amb `encesa`, la xarxa turquesa que canta)."""
    d = 20
    out = band(noise(d), 50, 300) * 0.18 + band(noise(d), 300, 1200) * 0.03
    for _ in range(9):
        s = rng.uniform(0, d)
        g = gota(rng.uniform(1100, 1900), 0.1) * rng.uniform(0.07, 0.14)
        _posa(out, g, s)
        _posa(out, g * 0.3, s + 0.13)
        _posa(out, g * 0.12, s + 0.27)
    for s in (6.0, 15.5):
        dd = 1.2
        g = grinyol(dd, corba(dd, [(0, 30), (0.5, 55), (1, 35)]), ((300, 1.0), (700, 0.5))) * env(dd, 0.3, None, 0.4)
        _posa(out, g * 0.25, s)
    if encesa:
        out += brunzit_turquesa(d, 110, 1.3) * _lfo(d, 0.1, 0.8, 1.0) * 0.5
        for _ in range(30):
            _posa(out, (osc(rng.uniform(2000, 4000), 0.6) * env(0.6, 0.003, 0.15)) * rng.uniform(0.01, 0.03), rng.uniform(0, d))
    else:
        out += brunzit_turquesa(d, 110, 0.0) * _lfo(d, 0.15, 0.0, 0.5) * 0.12
    return out


def amb_campament_fades():
    """El campament de les fades, a les branques altes, al matí: vent viu, fulles, molts ocells i un picot."""
    d = 24
    out = _fulles(d, 0.4, 400, 6000, 0.3)
    _ocells(out, d, 16, None, 0.1)
    for s in (9.0, 20.0):
        for i in range(int(rng.integers(10, 16))):
            _posa(out, fusta(rng.uniform(1100, 1300), 0.06, 0.012) * 0.05, s + i / 17)
    return out


def amb_toll_gripaus(aigua=False):
    """El toll dels gripaus: aiguamoll sec al migdia, cigales, una mosca que passa i algun rauc cansat.
    Amb `aigua`, el rierol hi torna a córrer i els gripaus en parlen més."""
    d = 20
    out = np.zeros(int(SR * d))
    for f_am, lo, hi, vol in ((180, 4000, 7500, 0.35), (230, 5000, 9000, 0.2)):
        cigala = band(noise(d), lo, hi) * (0.5 + 0.5 * osc(f_am, d)) * _lfo(d, 0.12, 0.1, 1.0) ** 2
        out += cigala * vol * (0.5 if aigua else 1.0)
    for s in (4.0, 13.0):
        dd = 1.6
        mosca = band(osc(190 + 15 * osc(1.7, dd), dd, 'saw'), 150, 3000) * np.sin(np.linspace(0, np.pi, int(SR * dd))) ** 2
        _posa(out, mosca * 0.08, s)
    rraucs = ((3.0, 150), (11.5, 140)) if not aigua else ((2.0, 160), (5.5, 140), (9.0, 175), (13.0, 150), (16.5, 165))
    for s, f in rraucs:
        _posa(out, rauc(f, 0.5) * 0.15, s)
    if aigua:
        out += band(noise(d), 400, 4000) * (0.8 + 0.4 * _lfo(d, 6, 0, 1)) * 0.25
        for _ in range(int(d * 6)):
            dd = rng.uniform(0.02, 0.06)
            f = rng.uniform(300, 1100)
            _posa(out, osc(np.linspace(f, f * 1.6, int(SR * dd)), dd) * env(dd, 0.002, dd / 3, 0.005) * rng.uniform(0.05, 0.15),
                  rng.uniform(0, d))
    return out


def amb_caseta_obra(wifi=True):
    """La caseta d'obra de NaturaPlus: el fluorescent que brunz, l'aire condicionat i, cada tres segons, el «pip»
    de l'arbre Wi-Fi (fins que la Vet el desendolla)."""
    d = 24
    fluorescent = osc(100, d) * 0.2 + osc(200, d) * 0.1 + osc(300, d) * 0.04 + band(osc(100, d, 'saw'), 1500, 5000) * 0.05
    aire = band(noise(d), 150, 2500) * 0.25 + band(noise(d), 40, 150) * 0.2
    out = fluorescent * (0.9 + 0.1 * _lfo(d, 0.5, 0, 1)) + aire
    if wifi:
        for i in range(8):
            _posa(out, bip_net(2000, 0.07) * 0.15, 3 * i + 0.5)
    return out


def amb_zona_zero(fi=False):
    """La Zona Zero, la presentació: el públic del poble que parla i, al fons, la formigonera i l'altaveu fent
    proves amb els ocells «prèmium». Amb `fi` (el bosc ja ha parlat): calla el motor i tornen els ocells de debò."""
    d = 24
    out = _murmuri(d, 16) * (0.25 if not fi else 0.18) + band(noise(d), 100, 600) * 0.03
    if not fi:
        motor = band(osc(37, d, 'saw'), 40, 500) * 0.25 + band(noise(d), 40, 250) * 0.2
        tambor = 0.75 + 0.25 * osc(0.5, d)  # la cuba que gira, cada dos segons
        grava = band(noise(d), 400, 2500) * (0.5 + 0.5 * osc(0.5, d, phase=1.0)) ** 3 * 0.06
        out += motor * tambor + grava
        _ocells_premium(out, d, 0.05)
    else:
        _ocells(out, d, 8, None, 0.07)
        out += _fulles(d, 0.15, 400, 5000)
    return out


def amb_bosc_obert():
    """El bosc obert, l'epíleg: un bosc viu de dia, ocells, vent amable i el brunzit turquesa, suau, sota terra."""
    d = 24
    out = _fulles(d, 0.35, 300, 5000, 0.2)
    _ocells(out, d, 14, None, 0.09)
    out += brunzit_turquesa(d, 110, 0.8) * 0.15
    return out


AMBIENTS = {
    'amb_vora_bosc': amb_vora_bosc,
    'amb_centraleta': amb_centraleta,
    'amb_centraleta_encesa': lambda: amb_centraleta(encesa=True),
    'amb_campament_fades': amb_campament_fades,
    'amb_toll_gripaus': amb_toll_gripaus,
    'amb_toll_gripaus_aigua': lambda: amb_toll_gripaus(aigua=True),
    'amb_caseta_obra': amb_caseta_obra,
    'amb_caseta_obra_sense_wifi': lambda: amb_caseta_obra(wifi=False),
    'amb_zona_zero': amb_zona_zero,
    'amb_zona_zero_fi': lambda: amb_zona_zero(fi=True),
    'amb_bosc_obert': amb_bosc_obert,
}


SONS = {
    'walkie': walkie, 'crit': crit, 'resposta': resposta, 'ampolles': ampolles, 'altaveu_iri': altaveu_iri,
    'xiulet': xiulet, 'sensors_esternut': sensors_esternut, 'rierol': rierol, 'fades_vol': fades_vol,
    'fades_mengen': fades_mengen, 'campaneta': campaneta, 'walkie_grava': walkie_grava, 'ruleta': ruleta,
    'porta_roure': porta_roure, 'gronxador': gronxador, 'esternut_fada': esternut_fada,
    'xarxa_encesa': xarxa_encesa, 'segell': segell, 'roda': roda, 'radar': radar, 'porta_topa': porta_topa,
    'pip': pip, 'passos_gripau': passos_gripau, 'futbol': futbol, 'ascensor': ascensor, 'anunci': anunci,
    'bastida': bastida,
}

# Volum de cada so respecte del màxim (els que són tons purs, aguts o molt sostinguts sonen més del que fan).
VOLUM = {
    'walkie': 0.55, 'walkie_grava': 0.45, 'radar': 0.45, 'pip': 0.5, 'xiulet': 0.55, 'ruleta': 0.6,
    'resposta': 0.4, 'crit': 0.95, 'xarxa_encesa': 0.75, 'campaneta': 0.6, 'anunci': 0.6, 'ascensor': 0.6,
    'futbol': 0.6, 'esternut_fada': 0.6, 'roda': 0.6, 'gronxador': 0.7, 'fades_vol': 0.8,
}

# Els sons que són tot cop i poca cua se senten fluixos: se'ls comprimeix una mica (com més, més cos).
COMPRIMEIX = {
    'segell': 3, 'porta_topa': 3, 'passos_gripau': 2.5, 'ampolles': 2, 'fades_mengen': 2, 'altaveu_iri': 2,
    'gronxador': 2, 'roda': 2, 'porta_roure': 2, 'bastida': 2,
}

# Els sons de fons greus (un brunzit, un motor) se senten menys amb la mateixa intensitat: se'ls apuja perquè
# tots sonin semblant.
VOLUM_FONS = {
    'amb_centraleta': 1.4, 'amb_centraleta_encesa': 1.3, 'amb_caseta_obra': 1.2, 'amb_caseta_obra_sense_wifi': 1.2,
    'amb_zona_zero': 1.1, 'amb_toll_gripaus': 0.75, 'amb_toll_gripaus_aigua': 0.85, 'amb_vora_bosc': 0.85,
}

# Pic màxim d'un so: per sota de -1 dBFS, amb marge per al còdec.
PIC = 0.8


def write(name, x, rms=None):
    """Normalitza pel pic (o, als sons de fons, per la intensitat mitjana `rms`) i desa l'.ogg."""
    if rms:
        x = x - np.mean(x)
        x = x / max(1e-9, np.sqrt(np.mean(x ** 2))) * rms
        x = np.tanh(x / PIC) * PIC  # cap pic no satura
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
        x = x * PIC * VOLUM.get(name, 1.0)
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
