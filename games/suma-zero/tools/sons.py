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


# ─── Acte 2: el BCMU ────────────────────────────────────────────────────────


def ascensor():
    """Un ascensor que arrenca, puja amb un brunzit i fa «ding» en arribar."""
    d = 1.6
    motor = (band(noise(d), 60, 400) * 0.5 + osc(np.linspace(70, 95, int(SR * d)), d) * 0.3) * env(d, 0.25, None, 0.3)
    ding = (osc(1318, 0.9) + 0.4 * osc(2636, 0.9)) * env(0.9, 0.002, 0.3) * 0.5
    return mix(motor, (ding, 1.45))


def tub_envia():
    """La càpsula que entra al tub: el tap que s'obre, i l'aire que se l'endú (fuuup)."""
    d = 0.7
    xiulet = band(noise(d), 600, 4000) * env(d, 0.01, None, 0.15)
    xiulet *= np.linspace(1, 0.2, len(xiulet))
    return mix((clic(800, 0.04), 0), (xiulet, 0.05), (osc(np.linspace(500, 1500, int(SR * 0.5)), 0.5) * env(0.5, 0.01, 0.15) * 0.15, 0.05))


def tub_rep():
    """La càpsula que arriba: un xiulet que s'acosta i el cop sec contra el tope."""
    d = 0.5
    arriba = band(noise(d), 600, 4000) * np.linspace(0.1, 1, int(SR * d)) * env(d, 0.01)
    cop = osc(np.linspace(220, 110, int(SR * 0.15)), 0.15) * env(0.15, 0.001, 0.04)
    return mix(arriba, (cop, 0.5), (clic(1500, 0.04) * 0.5, 0.52))


def bip_llibre():
    """El Llibre Major (1984) confirma un codi: un bip fortíssim, quadrat i llarg."""
    d = 0.9
    return osc(1046, d, 'square') * env(d, 0.003, None, 0.05) * 0.8


def clau_gira():
    """Una clau grossa que entra i gira dins d'un pany antic: metall, ressort i el clac final."""
    entra = band(noise(0.25), 2000, 7000) * env(0.25, 0.01, 0.1) * 0.4
    gir = band(noise(0.35), 400, 2500) * env(0.35, 0.05, None, 0.1) * 0.5
    return mix(entra, (gir, 0.3), (clic(600, 0.08), 0.7), (clic(1200, 0.04) * 0.6, 0.72))


def rebobinar():
    """El Dia de la Marmota: una cinta que rebobina a tota velocitat."""
    d = 1.3
    f = np.linspace(300, 2400, int(SR * d))
    cinta = osc(f, d, 'saw') * 0.25 + band(noise(d), 1000, 8000) * 0.3
    return cinta * env(d, 0.05, None, 0.25) * (0.7 + 0.3 * osc(23, d, 'square'))


def mobil_ok():
    """Un mòbil que torna a la vida: l'arpegi d'engegada."""
    nota = lambda f: (osc(f, 0.18) + 0.3 * osc(f * 2, 0.18)) * env(0.18, 0.005, 0.08) * 0.6
    return seq(nota(784), nota(988), nota(1175), nota(1568), gap=0.02)


def maquina_cafe():
    """Una màquina expenedora que s'empassa la moneda i rep un cop de puny."""
    moneda = mix(*[(clic(3000 - i * 400, 0.02) * (0.8 - i * 0.15), i * 0.05) for i in range(4)])
    cop = osc(np.linspace(110, 60, int(SR * 0.3)), 0.3) * env(0.3, 0.001, 0.08) + band(noise(0.3), 100, 1200) * env(0.3, 0.001, 0.05)
    return mix(moneda, (cop, 0.6))


def robot_neteja():
    """NETA-3 netejant molles: un aspirador petit i uns quants xiulets de servo."""
    d = 1.4
    aspira = band(noise(d), 800, 5000) * env(d, 0.1, None, 0.3) * 0.5
    servo = mix(*[(osc(np.linspace(400, 700, int(SR * 0.12)), 0.12, 'square') * env(0.12, 0.005, 0.05) * 0.2, x) for x in (0.2, 0.6, 1.0)])
    return mix(aspira, servo)


def robot_atura():
    """NETA-3 que s'atura: un motor que baixa de to fins a callar, i un sospir electrònic."""
    d = 1.2
    f = np.linspace(500, 60, int(SR * d))
    return osc(f, d, 'saw') * env(d, 0.01, None, 0.3) * 0.4 * np.linspace(1, 0.3, int(SR * d))


def galleda():
    """Una galleda de plàstic que es posa de barret a una càmera: un cop buit."""
    cop = osc(np.linspace(260, 180, int(SR * 0.3)), 0.3) * env(0.3, 0.001, 0.07)
    return mix(cop, (band(noise(0.1), 500, 3000) * env(0.1, 0.001, 0.03) * 0.4, 0))


def porta_neteja():
    """Una porta de servei que s'obre: el pom, la frontissa que grinyola i el tancament."""
    pom = clic(900, 0.05)
    grinyol = band(osc(np.linspace(700, 900, int(SR * 0.5)), 0.5, 'saw'), 500, 3000) * env(0.5, 0.05, None, 0.1) * 0.3
    tanca = osc(np.linspace(90, 60, int(SR * 0.2)), 0.2) * env(0.2, 0.001, 0.06)
    return mix(pom, (grinyol, 0.1), (tanca, 0.7))


def got():
    """Un got que cau i es trenca."""
    vidre = mix(*[(band(noise(0.25), 3000, 10000) * env(0.25, 0.001, 0.06) * (0.9 - 0.2 * i), i * 0.04) for i in range(4)])
    dring = mix(*[((osc(f, 0.6) * env(0.6, 0.001, 0.15)) * 0.25, 0.01 * i) for i, f in enumerate((2900, 4100, 5300))])
    return mix(vidre, dring)


# ─── Acte 3: Robin Hood 2.0 ─────────────────────────────────────────────────


def virus():
    """ROBIN HOOD 2.0 s'executa: una cascada de comptadors que cauen, cada cop més de pressa, i un bip llarg."""
    parts = []
    t0 = 0.0
    for i in range(18):
        f = 1800 - i * 70
        parts.append((osc(f, 0.05, 'square') * env(0.05, 0.002, 0.02) * 0.35, t0))
        t0 += max(0.03, 0.14 - i * 0.008)
    final = osc(523, 0.8, 'square') * env(0.8, 0.003, None, 0.2) * 0.5
    return mix(*parts, (final, t0 + 0.05))


def mobil_vibra():
    """El mòbil del Director que vibra damunt la taula: dues vibracions."""
    d = 0.35
    vib = band(osc(170, d, 'square') * (0.6 + 0.4 * osc(31, d)), 80, 1200) * env(d, 0.01, None, 0.05) * 0.6
    return seq(vib, vib, gap=0.15)


def aturada():
    """El Llibre Major atura el virus: un motor que s'apaga i tres notes que baixen, com un sospir."""
    d = 1.0
    motor = osc(np.linspace(220, 50, int(SR * d)), d, 'saw') * env(d, 0.01, None, 0.3) * 0.25
    nota = lambda f: osc(f, 0.35, 'square') * env(0.35, 0.003, None, 0.1) * 0.35
    return mix(motor, (seq(nota(784), nota(659), nota(523), gap=0.05), 0.4))


def megafonia_bcmu():
    """La megafonia del banc: tres notes elegants, de les que demanen calma mentre et busquen."""
    nota = lambda f: (osc(f, 0.8) + 0.3 * osc(f * 2, 0.8) + 0.1 * osc(f * 3, 0.8)) * env(0.8, 0.005, 0.3) * 0.5
    return mix(nota(659), (nota(880), 0.35), (nota(1319), 0.7))


def extintor():
    """Un extintor que baixa pel conducte i esclata en escuma: cops metàl·lics i un xiuxiueig llarg."""
    cops = mix(*[(osc(np.linspace(300, 200, int(SR * 0.08)), 0.08) * env(0.08, 0.001, 0.03) * (0.6 - 0.1 * i), i * 0.22) for i in range(4)])
    d = 1.6
    escuma = band(noise(d), 1500, 9000) * env(d, 0.02, None, 0.6) * 0.5
    return mix(cops, (escuma, 0.95))


def contenidor():
    """La tapa d'un contenidor que s'obre i algú que hi cau a dins, damunt d'una cosa tova."""
    tapa = mix(clic(400, 0.06), (band(osc(np.linspace(300, 260, int(SR * 0.4)), 0.4, 'saw'), 200, 2000) * env(0.4, 0.02, 0.1) * 0.3, 0.05))
    caiguda = osc(np.linspace(90, 50, int(SR * 0.35)), 0.35) * env(0.35, 0.001, 0.12) + band(noise(0.35), 100, 900) * env(0.35, 0.001, 0.1) * 0.6
    return mix(tapa, (caiguda, 0.9))


# ─── Llista ─────────────────────────────────────────────────────────────────

SONS = {
    'teclat': teclat, 'miol': miol, 'mossegada': mossegada, 'passaplats': passaplats, 'router': router,
    'nevera': nevera, 'porta_pis': porta_pis, 'vaporitzador': vaporitzador, 'pany_clic': pany_clic,
    'telefon_bar': telefon_bar, 'porta_bar': porta_bar, 'megafonia': megafonia, 'teclat_porta': teclat_porta,
    'alarma_porta': alarma_porta, 'plor': plor, 'impressora': impressora, 'auricular': auricular,
    'ascensor': ascensor, 'tub_envia': tub_envia, 'tub_rep': tub_rep, 'bip_llibre': bip_llibre, 'clau_gira': clau_gira,
    'rebobinar': rebobinar, 'mobil_ok': mobil_ok, 'maquina_cafe': maquina_cafe, 'robot_neteja': robot_neteja,
    'robot_atura': robot_atura, 'galleda': galleda, 'porta_neteja': porta_neteja, 'got': got,
    'virus': virus, 'mobil_vibra': mobil_vibra, 'aturada': aturada, 'megafonia_bcmu': megafonia_bcmu,
    'extintor': extintor, 'contenidor': contenidor,
}

# Volum de cada so respecte del màxim.
VOLUM = {'bip_llibre': 0.45, 'rebobinar': 0.6, 'alarma_porta': 0.5, 'telefon_bar': 0.6, 'vaporitzador': 0.5, 'impressora': 0.6, 'teclat': 0.6}


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
