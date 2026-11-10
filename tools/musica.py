#!/usr/bin/env python3
"""
`npm run musica`: genera la música d'ambient de Suma Zero a `game/audio/music/` (.ogg, estèreo).

Totes les peces són el mateix tema (La menor, 84 ppm, 24 compassos) amb instruments diferents, per lloc:

- `tema`: portada i pròleg. De nit: acords llargs, piano elèctric amb eco i un rellotge.
- `pis`: el pis. Lo-fi de hacker: ritme mandrós, piano apagat i vinil.
- `bar`: La Propina. Jazz de tarda: contrabaix caminant, escombretes i vibràfon.
- `aeroport`: l'aeroport. Espies: baix obstinat, cops d'aro, cordes en tremolo i guitarra seca.

Com que tenen la mateixa durada, el joc les encadena al mateix punt (`sync`) en canviar de lloc.
Les peces són bucles perfectes: cada so que passa del final torna a sonar al principi i la
reverberació és circular. Tot sintetitzat, i sempre igual.

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


# ─── El tema de Suma Zero ───────────────────────────────────────────────────
#
# Totes les peces comparteixen tempo, acords, melodia i durada: només canvien els instruments.
# Així, en passar d'un lloc a un altre, la música s'encadena al mateix punt (`sync`) i sona com
# un sol tema que canvia de roba.

PPM = 84
TEMPS = 60 / PPM
COMPAS = 4 * TEMPS

# Un acord cada dos compassos (24 compassos, uns 69 s). La menor: baix + veus (notes MIDI).
ACORDS = [
    (45, [60, 64, 67, 71]),  # La m9
    (41, [57, 60, 64, 67]),  # Fa maj7
    (38, [60, 64, 65, 69]),  # Re m9
    (40, [59, 62, 65, 68]),  # Mi 7(♭9)
    (45, [60, 64, 67, 71]),  # La m9
    (41, [57, 60, 64, 67]),  # Fa maj7
    (47, [57, 59, 62, 65]),  # Si m7(♭5)
    (40, [56, 59, 62, 64]),  # Mi 7
    (41, [57, 60, 64, 67]),  # Fa maj7
    (40, [59, 62, 64, 67]),  # Mi m7
    (38, [60, 64, 65, 69]),  # Re m9
    (40, [59, 62, 65, 68]),  # Mi 7(♭9)
]
COMPASSOS = 2 * len(ACORDS)

# (compàs, temps, nota, durada en temps). Els darrers 8 compassos, sense melodia: la sala respira.
MELODIA = [
    (0, 0, 76, 1), (0, 1, 72, 1), (0, 2, 69, 2), (1, 0, 71, 1), (1, 1, 72, 1), (1, 2, 76, 2),
    (2, 0, 77, 1.5), (2, 1.5, 76, 0.5), (2, 2, 72, 2), (3, 0, 69, 4),
    (4, 0, 74, 1), (4, 1, 72, 1), (4, 2, 69, 1), (4, 3, 65, 1), (5, 0, 64, 1), (5, 1, 65, 1), (5, 2, 69, 2),
    (6, 0, 68, 2), (6, 2, 71, 1), (6, 3, 74, 1), (7, 0, 77, 3), (7, 3, 76, 1),
    (8, 0, 76, 1), (8, 1, 72, 1), (8, 2, 69, 2), (9, 0, 71, 1), (9, 1, 72, 1), (9, 2, 79, 2),
    (10, 0, 81, 1.5), (10, 1.5, 79, 0.5), (10, 2, 76, 2), (11, 0, 72, 4),
    (12, 0, 74, 1), (12, 1, 77, 1), (12, 2, 81, 2), (13, 0, 77, 1), (13, 1, 74, 1), (13, 2, 71, 2),
    (14, 0, 68, 1), (14, 1, 71, 1), (14, 2, 74, 1), (14, 3, 76, 1), (15, 0, 80, 3), (15, 3, 76, 1),
]


def acord(c):
    """L'acord que sona al compàs `c`."""
    return ACORDS[(c // 2) % len(ACORDS)]


def quan(c, b, swing=0.5):
    """Segons del compàs `c`, temps `b`. Amb `swing` > 0.5, les corxeres a contratemps arriben tard."""
    sencer = int(b)
    frac = b - sencer
    if abs(frac - 0.5) < 1e-6:
        frac = swing
    return (c * 4 + sencer + frac) * TEMPS


def mix(p, x, inici, pan=0.0, vol=1.0):
    p.posa(x, inici, pan=pan, vol=vol)


# ─── Instruments ─────────────────────────────────────────────────────────────

def epiano(f, d):
    """Piano elèctric (FM): l'atac brilla i s'apaga de seguida; queda el cos rodó."""
    x = t(d)
    idx = 1.8 * np.exp(-x / 0.25)
    cos = np.sin(2 * np.pi * f * x + idx * np.sin(2 * np.pi * f * x))
    campaneta = 0.15 * osc(f * 7.1, d) * env(d, 0.001, 0.05, 0.04)
    return (cos + campaneta) * env(d, 0.004, 0.3, 1.6)


def vibrafon(f, d):
    x = t(d)
    tremolo = 0.8 + 0.2 * np.sin(2 * np.pi * 5.2 * x)
    so = osc(f, d) + 0.25 * osc(f * 4, d) * env(d, 0.001, 0.1, 0.4)
    return so * tremolo * env(d, 0.002, 0.4, 2.2)


def punteig(f, d, fosc=2500):
    """Corda puntejada i esmorteïda (la guitarra d'espies)."""
    so = osc(f, d, 'saw') * env(d, 0.002, 0.05, 0.18)
    return band(so, 80, fosc)


def baix_suau(f, d):
    return (osc(f, d) + 0.15 * osc(f * 2, d)) * env(d, 0.01, 0.15)


def contrabaix(f, d):
    x = t(d)
    so = osc(f * (1 + 0.01 * np.exp(-x / 0.03)), d) + 0.3 * osc(f * 2, d) * env(d, 0.002, 0.1, 0.15)
    return so * env(d, 0.004, 0.1, 0.5)


def pad(f, d, rng):
    """Tres sinusoides gairebé a l'uníson i l'octava fluixa."""
    x = sum(osc(f * 2 ** (c / 1200), d, phase=rng.uniform(0, 6.28)) for c in (-6, 0, 6)) / 3
    return x + 0.08 * osc(f * 2, d)


def bombo():
    d = 0.4
    x = t(d)
    f = 45 + 70 * np.exp(-x / 0.03)
    return osc(f, d) * env(d, 0.002, 0.05, 0.18)


def caixa(rng):
    d = 0.3
    return 0.7 * band(rng.uniform(-1, 1, int(SR * d)), 900, 5000) * env(d, 0.001, 0.05, 0.08) \
        + 0.5 * osc(185, d) * env(d, 0.001, 0.05, 0.05)


def charles(rng, obert=False):
    d = 0.4 if obert else 0.1
    return band(rng.uniform(-1, 1, int(SR * d)), 7000) * env(d, 0.001, 0.02, 0.12 if obert else 0.025)


def escombreta(rng):
    """Escombretes de jazz: un fregament curt."""
    d = 0.35
    return band(rng.uniform(-1, 1, int(SR * d)), 2000, 8000) * env(d, 0.06, 0.15, 0.15)


def plat_ride(rng):
    d = 1.2
    metall = sum(a * osc(f, d) for f, a in ((3150, 0.4), (4270, 0.3), (5530, 0.25), (6980, 0.2)))
    return (0.5 * metall + band(rng.uniform(-1, 1, int(SR * d)), 5000)) * env(d, 0.001, 0.2, 0.35)


def aro(rng):
    """Cop d'aro (rimshot): un clic sec i de fusta."""
    d = 0.08
    return (osc(1750, d) + 0.6 * band(rng.uniform(-1, 1, int(SR * d)), 1500, 6000)) * env(d, 0.0005, 0.02, 0.012)


def espetecs(p, rng, quants):
    """El vinil: espetecs a l'atzar i un fregament molt fluix."""
    for _ in range(quants):
        d = 0.01
        clic = band(rng.uniform(-1, 1, int(SR * d)), 1500) * env(d, 0.0002, 0.002, 0.002)
        p.posa(clic, rng.uniform(0, p.durada), pan=rng.uniform(-0.6, 0.6), vol=rng.uniform(0.1, 0.4))
    for ch in range(2):
        p.lr[ch] += 0.012 * band(p.soroll(rng), 300, 4000)


def melodia(p, instrument, pan=0.0, vol=0.2, octava=0, eco=0.0, staccato=None):
    for c, b, nota, dur in MELODIA:
        d = (min(dur, staccato) if staccato else dur) * TEMPS + 1.5
        x = instrument(midi(nota + 12 * octava), d)
        p.posa(x, quan(c, b), pan=pan, vol=vol)
        if eco:
            # Eco a corxera amb punt, a l'altre costat.
            p.posa(x, quan(c, b) + 0.75 * TEMPS, pan=-pan, vol=vol * eco)


def baix_a_terra(p, so, vol, ritme=(0,)):
    """Fonamental de cada acord, als temps de `ritme` de cada compàs."""
    for c in range(COMPASSOS):
        baix = acord(c)[0]
        for b in ritme:
            p.posa(so(midi(baix), TEMPS * 1.2), quan(c, b), vol=vol)


# ─── Les peces ───────────────────────────────────────────────────────────────

def tema():
    """Portada i pròleg: de nit, a la seu del banc. Acords llargs, el piano elèctric i un rellotge."""
    rng = np.random.default_rng(1)
    p = Pista(COMPASSOS * COMPAS)
    for i, (baix, veus) in enumerate(ACORDS):
        inici = 2 * i * COMPAS
        d = 2 * COMPAS + 3
        for j, v in enumerate(veus):
            p.posa(pad(midi(v), d, rng) * env(d, 2.0, 3.0), inici, pan=-0.5 + j / 3, vol=0.09)
        p.posa(osc(midi(baix - 12), d) * env(d, 1.0, 3.0), inici, vol=0.25)
    melodia(p, epiano, pan=0.2, vol=0.16, eco=0.35)
    # El rellotge: un tic fluix a cada temps.
    for c in range(COMPASSOS):
        for b in range(4):
            p.posa(aro(rng), quan(c, b), pan=0.5, vol=0.05 if b else 0.08)
    return reverb(p.lr, durada=1.6, cua=5.0, humit=0.6, rng=rng, fosc=5000)


def pis():
    """El pis de l'Iri: lo-fi de hacker a casa. Ritme mandrós, piano elèctric apagat i vinil."""
    rng = np.random.default_rng(2)
    p = Pista(COMPASSOS * COMPAS)
    sw = 0.62
    for c in range(COMPASSOS):
        baix, veus = acord(c)
        # Piano: l'acord al primer temps i un cop curt a l'«i» del segon.
        for b, d, vol in ((0, 2.2 * TEMPS, 0.07), (1.5, 0.8 * TEMPS, 0.05)):
            for j, v in enumerate(veus):
                p.posa(epiano(midi(v), d + 0.8), quan(c, b, sw) + 0.012 * j, pan=-0.3 + 0.2 * j, vol=vol)
        p.posa(baix_suau(midi(baix), 1.6 * TEMPS), quan(c, 0, sw), vol=0.3)
        p.posa(baix_suau(midi(baix), 0.8 * TEMPS), quan(c, 2.5, sw), vol=0.22)
        # Bateria: bombo a l'1 i a l'«i» del 2, caixa al 2 i al 4, charles a corxeres amb swing.
        for b in (0, 1.5):
            p.posa(bombo(), quan(c, b, sw), vol=0.4)
        for b in (1, 3):
            p.posa(caixa(rng), quan(c, b, sw), vol=0.18)
        for k in range(8):
            p.posa(charles(rng), quan(c, k / 2, sw), pan=0.3, vol=0.06 if k % 2 else 0.09)
    melodia(p, epiano, pan=-0.15, vol=0.09, octava=-1)
    espetecs(p, rng, 160)
    lr = reverb(p.lr, durada=0.5, cua=2.0, humit=0.25, rng=rng, fosc=3000)
    # Tot plegat, fosc: com si sonés per un altaveu de portàtil.
    return np.stack([band(ch, 50, 3200) for ch in lr])


def walking():
    """Línia de contrabaix a negres: notes de l'acord i, abans del canvi, un semitò per sota del següent."""
    notes = []
    for i, (baix, veus) in enumerate(ACORDS):
        rel = {(v - baix) % 12 for v in veus}
        tercera = 3 if 3 in rel else 4
        quinta = 7 if 7 in rel else 6
        setena = 10 if 10 in rel else 11
        seguent = ACORDS[(i + 1) % len(ACORDS)][0]
        aprop = seguent - 1 if seguent - 1 > baix - 4 else seguent + 1
        for r in (0, tercera, quinta, tercera, 12, setena, quinta):
            notes.append(baix + r)
        notes.append(aprop)
    return notes


def bar():
    """El bar La Propina: jazz de tarda. Contrabaix caminant, escombretes, plat i vibràfon."""
    rng = np.random.default_rng(3)
    p = Pista(COMPASSOS * COMPAS)
    sw = 0.66
    for k, nota in enumerate(walking()):
        p.posa(contrabaix(midi(nota), TEMPS * 1.1), k * TEMPS, pan=-0.1, vol=0.42)
    for c in range(COMPASSOS):
        baix, veus = acord(c)
        # Piano: acords curts a contratemps, com un pianista que acompanya sense molestar.
        cops = ((1.5, 0.6), (3, 1.0)) if c % 2 == 0 else ((0.5, 0.6), (2.5, 1.2))
        for b, dur in cops:
            for j, v in enumerate(veus):
                p.posa(epiano(midi(v), dur * TEMPS + 0.6), quan(c, b, sw) + 0.01 * j, pan=0.35, vol=0.045)
        # Bateria: ride «ding, ding-a ding», charles amb el peu al 2 i al 4, escombreta a cada temps.
        for b in (0, 1, 1.5, 2, 3, 3.5):
            p.posa(plat_ride(rng), quan(c, b, sw), pan=0.45, vol=0.05 if b in (0, 2) else 0.035)
        for b in (1, 3):
            p.posa(charles(rng), quan(c, b, sw), pan=-0.3, vol=0.08)
        for b in range(4):
            p.posa(escombreta(rng), quan(c, b, sw), pan=-0.2, vol=0.05)
    melodia(p, vibrafon, pan=-0.25, vol=0.13)
    return reverb(p.lr, durada=0.8, cua=3.0, humit=0.35, rng=rng, fosc=4500)


def aeroport():
    """L'aeroport: espies. Baix obstinat a corxeres, cops d'aro, cordes en tremolo i guitarra seca."""
    rng = np.random.default_rng(4)
    p = Pista(COMPASSOS * COMPAS)
    figura = (0, 0, 12, 0, 7, 0, 12, 10)
    for c in range(COMPASSOS):
        baix, veus = acord(c)
        for k, r in enumerate(figura):
            p.posa(punteig(midi(baix + r), 0.4, fosc=900) * 1.4, quan(c, k / 2), vol=0.22 if k % 4 == 0 else 0.15)
        for b in (0, 1.5, 2.5):
            p.posa(bombo(), quan(c, b), vol=0.25)
        for b in (1, 3, 3.75):
            p.posa(aro(rng), quan(c, b), pan=0.3, vol=0.1 if b != 3.75 else 0.05)
        for k in range(16):
            p.posa(charles(rng), quan(c, k / 4), pan=0.5, vol=0.035 if k % 2 else 0.05)
        # Cordes: l'acord en tremolo, cada dos compassos.
        if c % 2 == 0:
            d = 2 * COMPAS + 1
            tremolo = 0.6 + 0.4 * np.sin(2 * np.pi * (4 / TEMPS) * t(d))
            for j, v in enumerate(veus):
                p.posa(pad(midi(v), d, rng) * tremolo * env(d, 0.8, 1.0), quan(c, 0), pan=-0.6 + 0.4 * j, vol=0.05)
    melodia(p, lambda f, d: punteig(f, d, 3500), pan=0.2, vol=0.2, eco=0.4, staccato=0.6)
    return reverb(p.lr, durada=0.7, cua=2.5, humit=0.3, rng=rng, fosc=5000)

# ─── Sortida ────────────────────────────────────────────────────────────────

MUSICA = {'tema': tema, 'pis': pis, 'bar': bar, 'aeroport': aeroport}

# Volum eficaç (RMS) de cada peça: fluix, que és ambient i no ha de tapar les veus ni els sons.
RMS = {'tema': 0.08, 'pis': 0.08, 'bar': 0.08, 'aeroport': 0.08}


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
