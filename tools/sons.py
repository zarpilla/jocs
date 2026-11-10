#!/usr/bin/env python3
"""
`npm run sons`: genera els efectes de so del joc a `game/audio/sfx/` (.ogg).

Tot és sintetitzat (ones i soroll), sense mostres de fora: es pot tornar a generar sempre igual.
Per canviar un so per un de fet a mà, n'hi ha prou de posar el fitxer amb el mateix nom a
`game/audio/sfx/` i treure'l de la llista `SONS` d'aquí baix (si no, el sobreescriuria).

Les notes del trencaclosques del pany sònic (pany, molla, diapasó) segueixen una mateixa escala:
la molla a tensió 3 i el diapasó a to 2 fan exactament la nota del pany.

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
    f = np.broadcast_to(np.asarray(freq, dtype=float), (int(SR * d),))
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


# ─── Les notes del pany sònic ───────────────────────────────────────────────

NOTA_PANY = 392.0  # sol
PAS = 3  # semitons per cada estirada de la molla o passada de llima: prou per sentir-ho


def pany(d=1.8):
    """Un ressonador rodó: fonamental clara i parcials de campana que s'apaguen aviat."""
    f = NOTA_PANY
    return (
        osc(f, d) * env(d, 0.01, 0.9)
        + 0.25 * osc(f * 2.0, d) * env(d, 0.01, 0.4)
        + 0.12 * osc(f * 2.76, d) * env(d, 0.002, 0.15)
        + 0.06 * osc(f * 5.4, d) * env(d, 0.001, 0.05)
    )


def molla(tensio, d=1.4):
    """Una molla que vibra: «boing» (una mica de glissando a l'inici), harmònics de corda i trèmol."""
    f = semis(NOTA_PANY, (tensio - 3) * PAS)
    x = t(d)
    glide = f * (1 + 0.05 * np.exp(-x / 0.04)) * (1 + 0.004 * np.sin(2 * np.pi * 6 * x))
    cos = (
        osc(glide, d) * env(d, 0.003, 0.6)
        + 0.4 * osc(glide * 2, d) * env(d, 0.003, 0.25)
        + 0.2 * osc(glide * 3, d) * env(d, 0.003, 0.12)
    )
    clic = band(noise(0.02), 2000, 8000) * env(0.02, 0.001, 0.004) * 0.5
    return mix(cos, clic)


def diapaso(to, d=2.0):
    """Diapasó: sinusoide gairebé pura i un «cling» agut al cop."""
    f = semis(NOTA_PANY, (to - 2) * PAS)
    return osc(f, d) * env(d, 0.004, 1.1) + 0.3 * osc(f * 6.27, d) * env(d, 0.001, 0.06)


def xiulet(d=1.6):
    """El diapasó llimat de més: xiula com una tetera."""
    x = t(d)
    f = 2300 * (1 + 0.01 * np.sin(2 * np.pi * 7 * x)) * (1 + 0.03 * np.minimum(1, x / 0.3))
    alè = band(noise(d), 1800, 3200) * 0.25
    return (osc(f, d) + alè) * env(d, 0.25, None, 0.3)


def compara(a, b):
    return seq(a[: int(SR * 1.0)] * env(1.0, 0.001, None, 0.15), b, gap=0.25)


# ─── Efectes ────────────────────────────────────────────────────────────────


def clac():
    """Un pany que s'obre: dos clics metàl·lics."""
    def clic(g):
        return g * mix(band(noise(0.03), 1500) * env(0.03, 0.0005, 0.006), osc(140, 0.06) * env(0.06, 0.001, 0.015))
    return mix(clic(1.0), (clic(0.6), 0.07))


def consola():
    """Clac, i la consola s'encén: dos pips."""
    pip = lambda f: osc(f, 0.11, 'square') * env(0.11, 0.004, None, 0.02) * 0.35
    return mix(clac(), (pip(880), 0.2), (pip(1320), 0.33))


def cop():
    """Cop de puny contra un panell de metall."""
    d = 0.7
    return mix(
        osc(np.linspace(110, 60, int(SR * 0.25)), 0.25) * env(0.25, 0.001, 0.06),
        band(noise(0.08), 200, 3000) * env(0.08, 0.001, 0.02) * 0.6,
        (osc(340, d) * env(d, 0.002, 0.18) + 0.5 * osc(913, d) * env(d, 0.002, 0.1)) * 0.35,
    )


def eina():
    """Una clau anglesa: carrac-carrac."""
    clic = lambda: mix(band(noise(0.025), 2500) * env(0.025, 0.0005, 0.004), 0.3 * osc(2600, 0.04) * env(0.04, 0.001, 0.01))
    return mix(*[(clic() * (0.7 + 0.3 * (i % 2)), i * 0.075 + (0.25 if i >= 4 else 0)) for i in range(8)])


def comporta():
    """Una comporta de cent vint anys que puja: gemec greu, grinyols i un cop al final."""
    d = 2.4
    x = t(d)
    f = 48 + 10 * x / d + 2 * np.sin(2 * np.pi * 0.7 * x)
    gemec = band(osc(f, d, 'saw'), None, 400) * 0.8
    # Grinyol: fricció que s'enganxa i rellisca (polsos irregulars).
    polsos = (np.sin(2 * np.pi * np.cumsum(28 + 8 * np.sin(2 * np.pi * 1.3 * x)) / SR) > 0.6).astype(float)
    grinyol = band(noise(d), 600, 1800) * polsos * 0.5 + osc(700 + 120 * np.sin(2 * np.pi * 0.9 * x), d) * 0.08
    cos = (gemec + grinyol) * env(d, 0.3, None, 0.2)
    final = mix(osc(np.linspace(90, 50, int(SR * 0.4)), 0.4) * env(0.4, 0.001, 0.1), band(noise(0.1), 100, 2000) * env(0.1, 0.001, 0.03) * 0.5)
    return mix(cos, (final, d - 0.1))


def palanca():
    """Una palanca que baixa de cop i una clau anglesa que cau."""
    d = 0.8
    clonc = mix(osc(np.linspace(150, 70, int(SR * 0.3)), 0.3) * env(0.3, 0.001, 0.08),
                (osc(220, d) * env(d, 0.001, 0.2) + 0.6 * osc(587, d) * env(d, 0.001, 0.12)) * 0.4)
    caiguda = lambda g: g * mix(osc(1800, 0.25) * env(0.25, 0.001, 0.06) + 0.6 * osc(2950, 0.25) * env(0.25, 0.001, 0.04),
                                band(noise(0.02), 3000) * env(0.02, 0.0005, 0.004))
    return mix(clonc, (caiguda(0.5), 0.35), (caiguda(0.3), 0.47), (caiguda(0.15), 0.55))


def valvula():
    """Una roda de vàlvula que gira: grinyol metàl·lic i un buf."""
    d = 0.9
    x = t(d)
    f = 900 + 400 * x / d + 40 * np.sin(2 * np.pi * 11 * x)
    grinyol = (osc(f, d) + 0.3 * osc(f * 2.01, d)) * env(d, 0.05, None, 0.15) * 0.35
    buf = band(noise(0.8), 2000, 7000) * env(0.8, 0.2, 0.3) * 0.25
    return mix(grinyol, (buf, 0.5))


def boto():
    """Un botó que es prem: clic i un pip curt."""
    return mix(band(noise(0.02), 1500) * env(0.02, 0.0005, 0.004), (osc(600, 0.06, 'square') * env(0.06, 0.002, None, 0.02) * 0.25, 0.04))


def motor():
    """Un motor que tus, s'ofega... i arrenca."""
    def tos(d):
        x = t(d)
        cos = osc(55, d, 'saw') * (0.5 + 0.5 * np.sin(2 * np.pi * 18 * x))
        return band(cos + noise(d) * 0.4, 30, 900) * env(d, 0.02, d / 2)
    d = 2.2
    x = t(d)
    pols = 0.6 + 0.4 * np.sin(2 * np.pi * 22 * x)
    marxa = band(osc(48 + 6 * np.minimum(1, x / 0.6), d, 'saw') * pols + noise(d) * 0.25, 30, 1200) * env(d, 0.15, None, 0.6)
    return mix(tos(0.22), (tos(0.18), 0.4), (tos(0.15) * 0.6, 0.75), (marxa, 1.05))


def porta_llancadora():
    """Una porta pneumàtica que s'obre: clonc i un buf llarg."""
    buf = band(noise(1.3), 300, 5000) * env(1.3, 0.05, 0.5) * 0.5
    clonc = osc(np.linspace(120, 70, int(SR * 0.25)), 0.25) * env(0.25, 0.001, 0.06)
    return mix(clonc, (buf, 0.05))


def ronc():
    """En Mos ronca: aspiració amb vibració de gola, pausa, i buf."""
    def aspira(d):
        x = t(d)
        fry = 0.5 + 0.5 * np.sign(np.sin(2 * np.pi * (28 + 6 * x / d) * x))
        return band(noise(d) * fry + 0.4 * osc(85, d, 'saw') * fry, 80, 1200) * env(d, 0.35, None, 0.15)
    buf = band(noise(0.7), 200, 2500) * env(0.7, 0.1, 0.25) * 0.4
    return mix(aspira(1.0), (buf, 1.3))


def alarma():
    """L'alarma de vibració: brunzit que puja i baixa, tres vegades."""
    d = 0.42
    x = t(d)
    b = osc(220 + 60 * np.sin(np.pi * x / d), d, 'square') * (0.6 + 0.4 * np.sin(2 * np.pi * 14 * x)) * env(d, 0.02, None, 0.05)
    b = band(b, None, 3000) * 0.5
    return mix(b, (b, 0.5), (b, 1.0))


def vibracio():
    """La paret vibra: un brunzit greu que tremola."""
    d = 1.6
    x = t(d)
    trem = 0.5 + 0.5 * np.sin(2 * np.pi * 17 * x)
    return band(osc(70, d, 'saw') * trem + noise(d) * 0.2 * trem, 30, 600) * env(d, 0.4, None, 0.5)


def altaveu():
    """El «ding-dong-dong» alegre de la megafonia de la presó."""
    nota = lambda f, d=0.6: (osc(f, d) + 0.3 * osc(f * 2, d) + 0.1 * osc(f * 3.01, d)) * env(d, 0.005, 0.25) * 0.5
    return mix(nota(1047), (nota(1319), 0.18), (nota(1568, 0.9), 0.36))


def aigua():
    """Aigua que corre i bombolles."""
    d = 2.0
    corrent = band(noise(d), 150, 1200) * env(d, 0.3, None, 0.6) * 0.5
    bombolles = []
    for _ in range(14):
        bd = rng.uniform(0.04, 0.09)
        f0 = rng.uniform(300, 700)
        bombolles.append((osc(np.linspace(f0, f0 * 2.2, int(SR * bd)), bd) * env(bd, 0.003, bd / 3) * 0.3, rng.uniform(0, d - 0.2)))
    return mix(corrent, *bombolles)


def cambra_posa():
    """Deixar una cosa dins la cambra: un toc metàl·lic suau."""
    d = 0.5
    return osc(np.linspace(180, 140, int(SR * d)), d) * env(d, 0.001, 0.07) + 0.3 * osc(760, d) * env(d, 0.001, 0.08)


def cambra_arma():
    """El camp s'arma: un brunzit greu que puja i es queda."""
    d = 1.4
    x = t(d)
    f = 60 + 50 * np.minimum(1, x / 0.8)
    b = osc(f, d, 'saw') * 0.6 + osc(f * 2, d) * 0.3 + osc(f * 3, d) * 0.15
    return band(b, None, 1500) * env(d, 0.3, None, 0.4)


def fase():
    """La sincronia: buf que creix, espetec i una lluïssor aguda."""
    d = 0.9
    x = t(d)
    buf = band(noise(d), 300, 3000) * (x / d) ** 2 * 0.6
    espetec = np.zeros(int(SR * 0.25))
    for i in rng.integers(0, len(espetec), 40):
        espetec[i] = rng.uniform(-1, 1)
    espetec = band(espetec, 1000) * 6 * env(0.25, 0.001, 0.08)
    ld = 1.4
    llum = sum(osc(f, ld) for f in (1568, 1976, 2349, 3136)) * env(ld, 0.01, 0.4) * 0.12
    return mix(buf, (espetec, d), (llum, d))


def llima():
    """Tres passades de llima."""
    def passada():
        d = 0.28
        x = t(d)
        rasca = band(noise(d), 2500, 9000) * (0.6 + 0.4 * np.sin(2 * np.pi * 90 * x))
        return rasca * np.sin(np.pi * x / d) ** 0.7 * 0.6
    return mix(passada(), (passada(), 0.38), (passada(), 0.76))


# ─── Més sons (Acte 3, missions secundàries i detalls de tots els actes) ────


def segell():
    """Pam!: un segell de goma contra el paper i la taula."""
    pam = osc(np.linspace(140, 70, int(SR * 0.18)), 0.18) * env(0.18, 0.001, 0.05)
    paper = band(noise(0.06), 800, 5000) * env(0.06, 0.001, 0.015) * 0.5
    return mix(pam, paper)


def paper():
    """Paper que es desplega o s'arrenca: un frec irregular."""
    d = 0.5
    x = t(d)
    tremolor = (np.sin(2 * np.pi * np.cumsum(30 + 25 * np.sin(2 * np.pi * 3 * x)) / SR) > 0.2).astype(float)
    frec = band(noise(d), 1500, 9000) * (0.4 + 0.6 * tremolor)
    return frec * np.sin(np.pi * x / d) ** 0.5 * 0.6


def escriure():
    """Un llapis que escriu: ratllades curtes."""
    def ratlla(d):
        x = t(d)
        return band(noise(d), 2000, 7000) * np.sin(np.pi * x / d) * 0.45
    inicis = [0, 0.16, 0.27, 0.45, 0.58, 0.8]
    durs = [0.12, 0.08, 0.15, 0.1, 0.18, 0.09]
    return mix(*[(ratlla(dd), ii) for ii, dd in zip(inicis, durs)])


def serra():
    """Una serra de metall: anar i tornar, quatre vegades."""
    def passada(f0, f1):
        d = 0.32
        x = t(d)
        f = np.linspace(f0, f1, len(x))
        dents = (np.sin(2 * np.pi * np.cumsum(f) / SR) > 0.3).astype(float)
        return band(noise(d) * (0.3 + 0.7 * dents), 1800, 8000) * np.sin(np.pi * x / d) ** 0.8 * 0.6
    return mix(*[(passada(60, 110) if i % 2 == 0 else passada(110, 60), i * 0.34) for i in range(4)])


def reixa():
    """Una reixa de metall que s'aixeca: grinyol curt i un clonc."""
    d = 0.6
    x = t(d)
    grinyol = (osc(1100 + 300 * x / d, d) + 0.4 * osc(2300 + 500 * x / d, d)) * env(d, 0.05, None, 0.1) * 0.2
    rasca = band(noise(d), 1500, 6000) * env(d, 0.02, 0.25) * 0.4
    clonc = mix(osc(np.linspace(180, 90, int(SR * 0.2)), 0.2) * env(0.2, 0.001, 0.05),
                (osc(520, 0.5) * env(0.5, 0.001, 0.12) + 0.5 * osc(1370, 0.5) * env(0.5, 0.001, 0.08)) * 0.3)
    return mix(grinyol, rasca, (clonc, d - 0.05))


def conducte():
    """Arrossegar-se per un conducte de metall: cops buits que ressonen."""
    def pas(g):
        d = 0.5
        cos = osc(np.linspace(170, 140, int(SR * d)), d) * env(d, 0.002, 0.12) + 0.4 * osc(410, d) * env(d, 0.002, 0.2)
        return g * mix(cos, band(noise(0.04), 300, 2000) * env(0.04, 0.001, 0.01) * 0.6)
    return mix(*[(pas(0.8 if i % 2 == 0 else 0.55), i * 0.33 + (0.05 if i % 2 else 0)) for i in range(5)])


def holograma():
    """Un holograma que s'encén: brunzit que puja i una mica de soroll de transmissió."""
    d = 1.4
    x = t(d)
    brunzit = (osc(120, d, 'saw') * 0.3 + osc(240 + 60 * np.minimum(1, x / 0.4), d) * 0.4) * env(d, 0.3, None, 0.4)
    brunzit = band(brunzit, 80, 2500)
    talls = (np.sin(2 * np.pi * 7 * x) > 0.85).astype(float)
    estatica = band(noise(d), 2000, 8000) * talls * 0.25
    return mix(brunzit, estatica, (osc(1760, 0.15) * env(0.15, 0.005, 0.05) * 0.15, 0.35))


def tos():
    """Tus, tus: dues tossides discretes."""
    def una(g):
        d = 0.18
        x = t(d)
        return g * band(noise(d) + 0.4 * osc(160, d, 'saw'), 200, 2500) * env(d, 0.005, 0.05)
    return mix(una(1.0), (una(0.8), 0.28))


def porta_preso():
    """La porta de la cel·la que es tanca: buf pneumàtic, cop i forrellat."""
    buf = band(noise(0.5), 400, 5000) * env(0.5, 0.05, 0.2) * 0.4
    cop_ = osc(np.linspace(110, 60, int(SR * 0.3)), 0.3) * env(0.3, 0.001, 0.08)
    return mix(buf, (cop_, 0.45), (clac() * 0.7, 0.75))


# ─── Llista ─────────────────────────────────────────────────────────────────

SONS = {
    'pany': pany,
    **{f'molla_{i}': (lambda i=i: molla(i)) for i in range(6)},
    **{f'diapaso_{i}': (lambda i=i: diapaso(i)) for i in range(3)},
    # Comparacions: primer el que fa de model, després el que s'afina.
    **{f'pany_molla_{i}': (lambda i=i: compara(pany(), molla(i))) for i in range(6)},
    **{f'pany_diapaso_{i}': (lambda i=i: compara(pany(), diapaso(i))) for i in range(3)},
    **{f'molla_diapaso_{i}': (lambda i=i: compara(molla(3), diapaso(i))) for i in range(3)},
    'diapaso_xiulet': xiulet,
    'llima': llima,
    'clac': clac,
    'consola': consola,
    'cop': cop,
    'eina': eina,
    'comporta': comporta,
    'palanca': palanca,
    'valvula': valvula,
    'boto': boto,
    'motor': motor,
    'porta_llancadora': porta_llancadora,
    'ronc': ronc,
    'alarma': alarma,
    'vibracio': vibracio,
    'altaveu': altaveu,
    'aigua': aigua,
    'cambra_posa': cambra_posa,
    'cambra_arma': cambra_arma,
    'fase': fase,
    'segell': segell,
    'paper': paper,
    'escriure': escriure,
    'serra': serra,
    'reixa': reixa,
    'conducte': conducte,
    'holograma': holograma,
    'tos': tos,
    'porta_preso': porta_preso,
}

# Volum de cada so respecte del màxim (els cops forts no han de tapar les notes).
VOLUM = {'alarma': 0.5, 'vibracio': 0.6, 'motor': 0.7, 'comporta': 0.7, 'aigua': 0.6, 'ronc': 0.6, 'diapaso_xiulet': 0.5, 'boto': 0.6, 'holograma': 0.6, 'conducte': 0.7, 'paper': 0.6, 'escriure': 0.5, 'tos': 0.6}


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
