#!/usr/bin/env python3
"""
`npm run sons`: genera els efectes de so de La Conjura de l'Avet a `game/audio/sfx/` (.ogg).

Tot és sintetitzat (ones i soroll), sense mostres de fora: es pot tornar a generar sempre igual. Les eines de
síntesi són les de L'Última Arrel. Per canviar un so per un de fet a mà, n'hi ha prou de posar el fitxer amb el
mateix nom a `game/audio/sfx/` i treure'l de la llista `SONS` d'aquí baix.

La paleta (guió, «So»): fora, vent, pluja, campanes, el riu i el molí; dins el monestir de nit, espelmes, foc i
pedra; la burocràcia, el segell que pica damunt el pergamí.

Dues menes de sons: els efectes (`SONS`), curts i normalitzats pel pic, i els de fons (`AMBIENTS`, prefix `amb_`),
bucles sense costura que sonen sota la música (vegeu `ambient` a adapters/benne/mapping.json).

`python3 tools/sons.py campana amb_pont` en fa només uns quants. Cal python3 amb numpy, i ffmpeg.
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



# ─── Efectes ──────────────────────────────────────────────────────────────────


def campana():
    """La campana de Sant Pol: tres tocs de bronze, greus i llargs."""
    toc = lambda: mix(metall(392, 3.2, 1.1, (1, 2.0, 2.4, 3.0, 4.2, 5.4), (1, 0.6, 0.45, 0.3, 0.2, 0.1)), cop_sord(0.2, 60, 500, 0.05) * 0.5)
    return mix(toc(), (toc() * 0.9, 1.1), (toc() * 0.85, 2.2))


def alarma():
    """La campana del monestir tocant a rebato: tocs ràpids, més aguts."""
    toc = lambda: metall(523, 1.2, 0.5, (1, 2.0, 2.4, 3.0, 4.2), (1, 0.5, 0.4, 0.25, 0.1))
    return mix(*[(toc() * (0.9 if i % 2 else 1), i * 0.32) for i in range(8)])


def avet_cau():
    """L'avet que cau: la fusta que cruix, el xiulet de les branques i el cop contra el mur."""
    cruix = grinyol(1.4, 9, ((180, 1), (420, 0.6), (900, 0.3)), 0.6) * lin(0.3, 1, 1.4)
    aire = band(noise(1.0), 300, 3000) * lin(0, 1, 1.0, 2) * 0.6
    cop = mix(cop_sord(1.2, 30, 300, 0.35) * 1.5, band(noise(0.8), 800, 6000) * env(0.8, 0.002, 0.15) * 0.7)
    pedres = mix(*[(fusta(rng.uniform(200, 500), 0.15, 0.03) * rng.uniform(0.3, 0.7), 0.1 + rng.uniform(0, 0.8)) for _ in range(9)])
    return mix(cruix, (aire, 0.9), (cop, 1.8), (pedres, 1.9))


def post():
    """La post del sobreeixidor que cedeix: la fusta que grinyola i l'aigua que s'escola."""
    return mix(grinyol(0.6, 7, ((240, 1), (600, 0.5)), 0.5), (raig(1.6, 300, 3500) * lin(1, 0.3, 1.6), 0.4))


def aigua():
    """L'aigua que torna a entrar al rec: un raig que creix, amb bombolles."""
    return mix(raig(2.2, 200, 4000) * lin(0.2, 1, 2.2), bombolles(2.2, 25) * 0.4)


def olles():
    """La pila d'olles de ferro que cau: cops metàl·lics que rebotin."""
    return mix(*[(metall(rng.uniform(180, 420), 0.9, 0.25, (1, 2.3, 3.9), (1, 0.5, 0.3)) * rng.uniform(0.5, 1), i * rng.uniform(0.08, 0.16)) for i in range(7)])


def cullerot():
    """Un cullerot de ferro que cau a terra: clinc, clinc."""
    c = lambda: metall(1250, 0.5, 0.12, (1, 2.7, 5.2), (1, 0.4, 0.2))
    return mix(c(), (c() * 0.5, 0.18), (c() * 0.25, 0.29))


def pedra():
    """El contrapès que cau: el clic del bagul i el cop sord de la pedra a terra."""
    return mix(clic(1800, 0.03) * 0.6, (cop_sord(0.6, 40, 400, 0.12) * 1.4, 0.25))


def destral():
    """Dues destralades a una falca d'alzina."""
    cop = lambda: mix(fusta(260, 0.25, 0.04), clic(3200, 0.02) * 0.5, cop_sord(0.25, 80, 700, 0.04) * 0.6)
    return mix(cop(), (cop(), 0.45), (fusta(180, 0.35, 0.08) * 0.8, 0.8))


def truca():
    """Algú que truca a la porta de la porteria: tres cops de fusta."""
    return mix(*[(fusta(140, 0.2, 0.05) * 1.2, i * 0.28) for i in range(3)])


def segell():
    """El segell del jutge: el «pof» a la cera i el «clac» damunt el faristol."""
    pof = band(noise(0.12), 100, 900) * env(0.12, 0.003, 0.03) * 0.4
    clac = mix(fusta(320, 0.3, 0.035), clic(2500, 0.03) * 0.8, cop_sord(0.25, 70, 600, 0.05) * 0.8)
    return mix(pof, (clac, 0.3))


# ─── Sons de fons ─────────────────────────────────────────────────────────────

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



def _pluja(d, vol=0.25):
    """Pluja: soroll ample i gotes."""
    out = band(noise(d), 800, 8000) * vol * _lfo(d, 0.2, 0.6, 1)
    for _ in range(int(d * 18)):
        _posa(out, gota(rng.uniform(1200, 2600), 0.05) * rng.uniform(0.02, 0.08), rng.uniform(0, d))
    return out


def _riu(d, vol=0.4, lo=150, hi=3500):
    return band(noise(d), lo, hi) * vol * _lfo(d, 0.3, 0.75, 1)


def _foc(d, vol=0.25):
    """Foc de llar: un ronc greu i espurnes."""
    out = band(noise(d), 60, 500) * vol * _lfo(d, 0.5, 0.6, 1)
    for _ in range(int(d * 4)):
        _posa(out, clic(rng.uniform(1500, 4000), 0.02) * rng.uniform(0.05, 0.2), rng.uniform(0, d))
    return out


def amb_tempesta():
    """L'avet el dia de la tempesta: pluja, vent que xiula a les branques i gotes que cauen de l'absis."""
    d = 24
    return _pluja(d, 0.3) + _fulles(d, 0.3, 200, 3000, 0.3)


def amb_mati():
    """El poble al matí del judici: ocells, gent que xerra lluny, un gall."""
    d = 24
    out = _fulles(d, 0.15, 400, 5000, 0.15) + _murmuri(d, 4) * 0.12
    _ocells(out, d, 10, None, 0.08)
    return out


def amb_placa():
    """La plaça de Sant Pol: el poble que xerra, dones que filen a la nau, ocells."""
    d = 24
    out = _murmuri(d, 6) * 0.2 + _fulles(d, 0.12, 400, 5000, 0.2)
    _ocells(out, d, 6, None, 0.06)
    return out


def amb_pont():
    """El Pont Vell amb el riu crescut."""
    d = 24
    return _riu(d, 0.5) + _fulles(d, 0.15, 300, 3000, 0.3)


def amb_pont_manso():
    """El Pont Vell el matí del judici: riu tranquil i ocells."""
    d = 24
    out = _riu(d, 0.22, 300, 5000)
    _ocells(out, d, 8, None, 0.08)
    return out


def amb_claustre():
    """El claustre: gotes que cauen de les teulades, i un ocell."""
    d = 24
    out = band(noise(d), 200, 2000) * 0.05
    for _ in range(int(d * 3)):
        _posa(out, gota(rng.uniform(900, 1900), 0.08) * rng.uniform(0.05, 0.15), rng.uniform(0, d))
    _ocells(out, d, 3, None, 0.05)
    return out


def amb_nit():
    """Dins el monestir, de nit: pedra, silenci, una torxa que crepita i grills de fora."""
    d = 24
    out = _foc(d, 0.08) + band(noise(d), 60, 300) * 0.05
    _grills(out, d, 0.8, 0.02)
    return out


def amb_cuina():
    """La cuina: una llar de foc gegant i una olla que bull."""
    d = 24
    out = _foc(d, 0.35)
    out += bombolles(d, int(d * 6))[:len(out)] * 0.08
    return out


def amb_moli():
    """El molí per dins: el rec que corre per sota, la fusta que cruix."""
    d = 24
    out = _riu(d, 0.35, 100, 2000)
    for _ in range(6):
        _posa(out, grinyol(0.5, 6, ((200, 1), (500, 0.5)), 0.5) * 0.05, rng.uniform(0, d))
    return out


AMBIENTS = {
    'amb_tempesta': amb_tempesta, 'amb_mati': amb_mati, 'amb_placa': amb_placa, 'amb_pont': amb_pont,
    'amb_pont_manso': amb_pont_manso, 'amb_claustre': amb_claustre, 'amb_nit': amb_nit, 'amb_cuina': amb_cuina,
    'amb_moli': amb_moli,
}

SONS = {
    'campana': campana, 'alarma': alarma, 'avet_cau': avet_cau, 'post': post, 'aigua': aigua, 'olles': olles,
    'cullerot': cullerot, 'pedra': pedra, 'destral': destral, 'truca': truca, 'segell': segell,
}
VOLUM = {'campana': 0.8, 'alarma': 0.7, 'cullerot': 0.6, 'aigua': 0.8}
COMPRIMEIX = {'segell': 3, 'destral': 2.5, 'truca': 2.5, 'pedra': 2.5, 'olles': 2}
VOLUM_FONS = {'amb_nit': 0.8, 'amb_cuina': 1.1, 'amb_moli': 1.1}

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

