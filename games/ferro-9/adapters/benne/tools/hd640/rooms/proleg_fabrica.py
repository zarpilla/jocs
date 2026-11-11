"""
Pròleg 3 · «Cent vint anys abans...», a 640×360 (vegeu hd/rooms/proleg_fabrica.py, la de 480×270): la fàbrica de
ferro-9 de nit, vista des de l'altra riba del canal. Dues naus de maó (la llarga, amb el rètol d'ALDAIA · FERRO-9 al
teulat, i la de la façana amb l'ull de bou en forma de roda dentada), tres xemeneies treient fum, la lluna,
finestres enceses pel foc dels forns i el canal amb els reflexos. Llums: la lluna (freda, de dalt a la dreta), les
finestres i el portal dels forns, un fanal.
  - la mateixa composició ×4/3; maons de 4 píxels d'alçada (3 + el morter) i 10 de llargada, pissarres de 4;
  - el rètol del teulat, en lletres de 5×7 bombetes (a 480 eren de 3×5): es llegeix; el de la porta, també;
  - més detall: dentells sota la cornisa, capitells a les pilastres, dovelles al portal, el vidre de les
    finestres amb la silueta de les màquines, finestretes a la ciutat, els reblons de la gavarra, cargols al
    rètol de la porta;
  - el fum, el cel i el canal es calculen a 640 amb la mida de soroll i d'ones de 480 (no s'amplien).
Pantalla sencera (sense barra de verbs). `bg` es reutilitza a la portada.
"""
import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

import math
import random

from PIL import Image

from hd.pix import (Light, B4, W, H, hr, mix, ramp, BRICK, IRON, SMOKE, GLASS, FIRE, GOLD,
                    NAVY, SIL, PAPER, WALNUT, RUST, COPPER)
from hd640.rooms.proleg_gavina import Noise, vinyeta, ambient_frames

K = 4 / 3                                  # 480 → 640

# Rampes pròpies
SLATE = ramp((8, 8, 16), (16, 16, 28), (26, 26, 42), (40, 40, 58), (58, 58, 78), (84, 84, 104), (120, 118, 136), n=9)
STONE = ramp((20, 16, 22), (40, 32, 36), (64, 54, 54), (92, 80, 74), (124, 110, 98), (160, 146, 128), (200, 188, 166), n=9)
WATER = ramp((2, 4, 10), (6, 10, 22), (10, 16, 34), (16, 24, 48), (24, 34, 62), (36, 48, 80), n=8)
NIGHT = ramp((4, 4, 12), (8, 8, 22), (14, 14, 34), (24, 20, 48), (40, 28, 60), (64, 38, 66), (100, 52, 66),
             (146, 72, 62), (196, 104, 64), (236, 150, 84), n=12)

QY = 248           # vora del moll (on comença el canal)
MOON = (531, 53)

PITCH = 88 / 3     # la crugia de la nau llarga (22 a 480)
# Finestres: (x0, y0, amplada, alçada, encesa?)
WIN_A = [(round(35 + i * PITCH), 155, 16, 40, i not in (2, 6, 9)) for i in range(10)]
WIN_A_LOW = [(round(40 + i * PITCH), 211, 8, 11, i in (0, 1, 3, 4, 7, 8)) for i in range(10)]
WIN_B = [(x, y, 16, 35, lit) for (x, y, lit) in
         ((373, 139, True), (408, 139, False), (528, 139, True), (563, 139, True),
          (373, 192, True), (408, 192, True), (528, 192, False), (563, 192, True))]
PORTAL = (451, 176, 501, QY - 1)       # el portal dels forns, mig obert


def _light():
    L = Light(ambient=0.0, vignette=None, floor_fade=None)
    for x, y, w, h, lit in WIN_A + WIN_B:
        if lit:
            L.point(x + w / 2, y + h * 0.7, r=29, k=1.3, squash=1.3)
    for x, y, w, h, lit in WIN_A_LOW:
        if lit:
            L.point(x + w / 2, y + h / 2, r=13, k=0.8)
    L.point(476, 227, r=93, k=2.8, squash=0.9)             # el foc del portal
    L.point(315, 211, r=61, k=2.0, squash=1.0)             # el fanal del moll
    return L


LIGHT = _light()
N_SMOKE, N_CLOUD = Noise(31), Noise(32)

# Lletres de 5×7 per als rètols (el del teulat, de bombetes; el de la porta, pintat)
FONT = {
    'A': ['01110', '10001', '10001', '11111', '10001', '10001', '10001'],
    'L': ['10000', '10000', '10000', '10000', '10000', '10000', '11111'],
    'D': ['11110', '10001', '10001', '10001', '10001', '10001', '11110'],
    'I': ['01110', '00100', '00100', '00100', '00100', '00100', '01110'],
    'F': ['11111', '10000', '10000', '11110', '10000', '10000', '10000'],
    'E': ['11111', '10000', '10000', '11110', '10000', '10000', '11111'],
    'R': ['11110', '10001', '10001', '11110', '10100', '10010', '10001'],
    'O': ['01110', '10001', '10001', '10001', '10001', '10001', '01110'],
    '-': ['00000', '00000', '00000', '01110', '00000', '00000', '00000'],
    '9': ['01110', '10001', '10001', '01111', '00001', '00010', '01100'],
    '·': ['00000', '00000', '00000', '00100', '00000', '00000', '00000'],
    ' ': ['00000', '00000', '00000', '00000', '00000', '00000', '00000'],
}


def text_px(text, x0, y0, k=1, adv=6):
    """Píxels (x, y) d'un text en la lletra de 5×7, a escala k (cada lletra avança `adv` mòduls)."""
    out = []
    x = x0
    for ch in text:
        for j, row in enumerate(FONT[ch]):
            for i, b in enumerate(row):
                if b == '1':
                    for a in range(k):
                        for c in range(k):
                            out.append((x + i * k + a, y0 + j * k + c))
        x += adv * k
    return out


def bulbs(text, x0, y0, pitch=2, adv=11):
    """Bombetes d'un rètol: (x, y, lletra, columna, fila), una per cada bit de la lletra de 5×7."""
    out = []
    for n, ch in enumerate(text):
        for j, row in enumerate(FONT[ch]):
            for i, b in enumerate(row):
                if b == '1':
                    out.append((x0 + n * adv + i * pitch, y0 + j * pitch, n, i, j))
    return out


# ─── Peces ──────────────────────────────────────────────────────────────────

def sky(cv):
    rnd = random.Random(12)
    stars = {(rnd.randint(0, W - 1), rnd.randint(0, 147)) for _ in range(260)}
    for y in range(0, QY):
        v = y / K
        for x in range(W):
            u = x / K
            t = v / 150
            lvl = 0.6 + t ** 2.2 * 7.4                              # el resplendor dels forns i de la ciutat
            lvl += max(0.0, 1 - abs(u - 300) / 260) * t ** 3 * 1.2
            dm = math.hypot(u - MOON[0] / K, v - MOON[1] / K)
            if dm < 70:
                lvl += (1 - dm / 70) ** 2 * 2.2
            ds = math.hypot((u - 128) / 90, (v - 50) / 22)          # el rètol encès escalfa el cel
            if ds < 1:
                lvl += (1 - ds) ** 2 * 1.4
            # núvols prims, amb la vora encesa per la lluna (una octava més que a 480)
            c = N_CLOUD.fbm(u / 70, v / 14, 5)
            band = max(0.0, 1 - abs(v - 58) / 30)
            if c * band > 0.42:
                lvl += 0.8 + (1.2 if dm < 90 else 0) * (1 - dm / 90)
                if N_CLOUD.fbm(u / 70, (v - 2) / 14, 5) * band <= 0.42:
                    lvl += 0.6 * max(0.0, 1 - dm / 140)            # el cantell de dalt del núvol
            cv.put(x, y, NIGHT, lvl, 0)
            if (x, y) in stars and dm > 16 and c * band < 0.4:
                b = hr(x, y, 2)
                cv.flat(x, y, mix((120, 110, 160), (240, 236, 255), b) if y < 120 else (150, 120, 140))
                if b > 0.85 and y < 120 and 0 < x < W - 1 and y > 0:                            # les més brillants, amb creueta
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        cv.flat(x + dx, y + dy, mix(cv.get(x + dx, y + dy), (180, 176, 220), 0.45))
    # la lluna
    mx, my = MOON
    cv.glow(mx, my, 40, (200, 200, 230), 0.35)
    cv.disc(mx, my, 13, 13, PAPER, lambda nx, ny: 5.5 if nx * nx + ny * ny < 0.7 or nx > 0 else 4.6, 0)
    for dx, dy, r in ((-4, -3, 3.2), (4, 4, 2.4), (-1, 7, 1.9), (5, -5, 1.6), (-7, 3, 1.3), (1, -8, 1.0)):
        cv.disc(mx + dx, my + dy, r, r, PAPER, 4.5, 0)
        cv.put(mx + dx + round(r * 0.6), my + dy + round(r * 0.6), PAPER, 5.8, 0)   # la vora clara del cràter


def city(cv):
    """La ciutat de fons, una silueta baixa amb finestretes i xemeneies llunyanes."""
    rnd = random.Random(4)
    sky_ = [QY] * W
    x = 0
    while x < W:
        w = rnd.randint(13, 35)
        top = rnd.randint(187, 213)
        for xx in range(x, min(W, x + w)):
            sky_[xx] = top
        if rnd.random() < 0.3:
            cx = x + rnd.randint(3, max(4, w - 4))
            for xx in range(cx, min(W, cx + 3)):
                sky_[xx] = top - rnd.randint(19, 35)
        elif rnd.random() < 0.3:                                    # un terrat a dues aigües
            for xx in range(x, min(W, x + w)):
                sky_[xx] = top - min(xx - x, x + w - 1 - xx) // 2
        x += w
    for x in range(W):
        for y in range(sky_[x], QY):
            if x % 3 != 2 and y % 4 != 3 and hr(x // 3, y // 4, 8) < 0.04 and y > sky_[x] + 3:
                cv.flat(x, y, (200, 130, 60) if hr(x // 3, y // 4, 9) > 0.3 else (230, 170, 90))
            else:
                cv.put(x, y, SIL, 1.6 + (0.8 if y == sky_[x] else 0), 0)


def chimney(cv, x0, x1, top, base, lit_side=1, flick=0.0):
    """Xemeneia de maó, una mica cònica, amb anelles i un capçal; la boca brilla del foc."""
    for y in range(top, base + 1):
        t = (y - top) / max(1, base - top)
        inset = (1 - t) * 2
        a, b = x0 + inset, x1 - inset
        for x in range(math.floor(a), math.ceil(b) + 1):
            u = (x - a) / (b - a)
            row = y // 4
            mortar = y % 4 == 3 or (x + (row % 2) * 4) % 8 == 7
            lvl = 2.2 + u * 1.4 * lit_side - (1 - u) * 0.4 + (hr(x // 8, row, 3) - 0.5) * 0.6
            if mortar:
                lvl -= 0.9
            if (y - top) in (13, 14, 40, 41):
                cv.put(x, y, IRON, 2.4 + u * 2.2 + (0.8 if (y - top) in (13, 40) else 0), 0)   # anelles de ferro
                continue
            if (y - top) in (15, 42) and (x - x0) % 5 == 2:
                cv.put(x, y, RUST, 2.4, 0)                          # el rovell que regalima de l'anella
                continue
            cv.put(x, y, BRICK, lvl, 0)
    # capçal
    cv.rect(x0 - 3, top - 4, x1 + 3, top, BRICK, lambda x, y: 3.2 + (x - x0) / (x1 - x0) * 1.4 - (y - top + 4) * 0.25, 0)
    cv.hline(x0 - 3, x1 + 3, top, BRICK, 1.2, 0)
    cv.hline(x0 - 2, x1 + 2, top - 5, FIRE, 3.6, 0)
    cv.hline(x0, x1, top - 6, FIRE, 2.6, 0)
    cv.glow((x0 + x1) / 2, top - 5, 11, (255, 140, 60), 0.6 + flick)


def smoke(cv, sources, t=0.0):
    """Plomalls de fum que el vent s'emporta cap a la dreta: encesos de taronja a la boca, grisos de lluna a dalt.
    `sources`: (x, y, llargada) en píxels de 640; la forma i el soroll es calculen amb les mides de 480.
    `t` (0..1): moment del bucle d'animació. El fum flueix plomall amunt (el soroll es desplaça i es fon amb una
    còpia desplaçada un bucle enrere, perquè enllaci) i el vent el fa onejar. Amb t = 0, el fons quiet."""
    ph = 2 * math.pi * t
    VX, VY = 16.0, -3.0                                     # el que avança el fum en un bucle (unitats de 480)
    wa, wb = 1 - t, t
    wn = math.sqrt(wa * wa + wb * wb)
    src = [(sx / K, sy / K, ln / K) for sx, sy, ln in sources]

    def noise(x, y):
        if not t:
            return N_SMOKE.fbm((x - y * 0.3) / 11, y / 8, 4)
        xa, ya = x - VX * t, y - VY * t
        xb, yb = xa + VX, ya + VY
        na = N_SMOKE.fbm((xa - ya * 0.3) / 11, ya / 8, 4)
        nb = N_SMOKE.fbm((xb - yb * 0.3) / 11, yb / 8, 4)
        return 0.5 + (wa * (na - 0.5) + wb * (nb - 0.5)) / wn
    Y1 = 200
    D = [[0.0] * W for _ in range(Y1)]
    WM = [[0.0] * W for _ in range(Y1)]
    for y in range(Y1):
        v = y / K
        for x in range(W):
            u = x / K
            best, warm = 0.0, 0.0
            n = None
            for i, (sx, sy, length) in enumerate(src):
                dx = u - sx
                if dx < -6 or dx > length or v > sy:
                    continue
                e = max(0.0, dx)
                yc = sy - 6 - 26 * (1 - math.exp(-e / 22)) - e * 0.08          # puja i s'ajeu amb el vent
                if ph:                                                          # el vent l'oneja, cua avall
                    q = -e / 26 + i * 2.1
                    yc += 3.0 * (e / length) * (math.sin(ph + q) - math.sin(q))
                te = e / length                                                 # (no `t`: és el moment del bucle)
                wid = 4 + e * 0.2 + 4 * (1 - math.exp(-e / 10))
                if dx < 0:
                    wid = 3 + dx * 0.4
                    if wid <= 0:
                        continue
                d = abs(v - yc) / wid
                if d > 1.8:
                    continue
                if n is None:
                    n = noise(u, v)
                dens = (1 - d * 0.55) * (1 - te) ** 0.9 * (0.25 + n * 1.3)
                if dens > best:
                    best, warm = dens, max(0.0, 1 - e / 12) * max(0.0, 1 - (sy - v) / 14)
            D[y][x], WM[y][x] = best, warm
    TH = 0.42
    for y in range(Y1):
        for x in range(W):
            v = D[y][x]
            if v <= TH:
                # vora esfilagarsada: un vel puntejat
                if v > TH - 0.1 and B4[y & 3][x & 3] < (v - TH + 0.1) * 5:
                    cv.put(x, y, SMOKE, 1.0, 0)
                continue
            up = D[y - 3][x] if y >= 3 else 0
            up1 = D[y - 1][x] if y >= 1 else 0
            dn = D[y + 3][x] if y + 3 < Y1 else 0
            lvl = 1.5 + min(1.0, (v - TH) * 2.5) * 0.8
            if up1 <= TH:
                lvl += 1.9                                          # la vora de dalt, tocada per la lluna
            elif up <= TH:
                lvl += 1.0
            elif dn <= TH:
                lvl -= 0.8
            if WM[y][x] > 0.15:
                cv.put(x, y, NIGHT, 6.5 + WM[y][x] * 3, 0)
            else:
                cv.put(x, y, SMOKE, lvl, 0)


def bricks(cv, x0, y0, x1, y1, base=2.1, seed=0):
    """Paret de maó: filades de 4 píxels (3 + el morter), maons de 10 a trencajunts; algun de més cremat."""
    def f(x, y):
        row = y // 4
        if y % 4 == 3:
            return base - 1.1
        xx = x + (row % 2) * 5
        if xx % 10 == 9:
            return base - 0.9
        h = hr(xx // 10, row, seed)
        lvl = base + (h - 0.5) * 0.7 - (y - y0) / 270
        if h > 0.94:
            lvl -= 0.6                                              # un maó recremat
        if y % 4 == 0:
            lvl += 0.25                                             # el cantell de dalt del maó
        return lvl
    cv.rect(x0, y0, x1, y1, BRICK, f)


def window(cv, x, y, w, h, lit, seed=0, flick=0.0):
    """Finestral de mig punt amb brancals de pedra (amb dovelles a l'arc) i reixa de ferro."""
    r = w / 2
    cx = x + r - 0.5

    def inside(px, py, grow=0.0):
        if py >= y + r:
            return x - grow <= px <= x + w - 1 + grow and py <= y + h - 1 + grow
        return math.hypot(px - cx, py - (y + r)) <= r + grow - 0.3

    machine = hr(seed, 1) < 0.5
    for py in range(int(y - 4), int(y + h + 4)):
        for px in range(int(x - 4), int(x + w + 4)):
            if inside(px, py):
                ix, iy = px - x, py - y
                mull = ix in (w // 3, 2 * w // 3) or (iy > r and (iy - int(r)) % 9 == 0)
                if mull:
                    cv.put(px, py, IRON, 1.0 if lit else 0.6, 0)
                elif lit:
                    # vidre encès: més calent a baix, on hi ha el foc; alguna silueta de màquina a dins
                    lvl = 2.2 + (iy / h) * 2.8 + (hr(seed, ix // 2, iy // 4) - 0.5) * 0.6 + flick
                    if machine and ((iy > h * 0.6 and abs(ix - w / 2) < w * 0.3)
                                    or math.hypot(ix - w / 2 + 0.5, iy - h * 0.6) < w * 0.22):
                        lvl -= 2.0                                  # una màquina a contrallum (amb el volant)
                    if (ix + iy) % 11 == 0 and iy < h * 0.4:
                        lvl += 0.6                                  # un vidre que fa aigües
                    cv.put(px, py, GLASS, lvl, 0)
                else:
                    lvl = 1.6 - iy / h * 0.6 + (1.4 if (ix + iy) % 12 == 0 and iy < h / 2 else 0)
                    cv.put(px, py, NAVY, lvl, 0)                    # fosc: hi rebota la lluna
            elif inside(px, py, 2.2):
                lvl = 3.2 + (0.8 if px >= x + w - 1 else 0)
                if py < y + r:                                      # dovelles: juntes radials a l'arc
                    a = math.atan2(py - (y + r), px - cx)
                    if (a / (math.pi / 7)) % 1 < 0.14:
                        lvl -= 1.2
                elif (py - y) % 8 == 0:
                    lvl -= 1.0                                      # juntes dels carreus del brancal
                cv.put(px, py, STONE, lvl)                          # brancal de pedra
    cv.rect(x - 3, y + h, x + w + 2, y + h + 2, STONE, lambda a, b: 4.4 - (b - y - h) * 1.3)    # ampit
    cv.darken(x - 2, y + h + 3, x + w + 1, y + h + 3, 0.6)                                   # la seva ombra
    cv.rect(cx - 1.5, y - 4, cx + 1.5, y, STONE, lambda a, b: 4.6 + (0.6 if a < cx else 0))   # clau


# ─── La pantalla ────────────────────────────────────────────────────────────

A_X0, A_X1, A_TOP = 16, 341, 136          # nau llarga
B_X0, B_X1, B_TOP, B_PEAK = 349, 603, 123, (476, 67)   # nau de la façana
SIGN = 'ALDAIA · FERRO-9'
SX0, SY0 = 85, 56                         # on comença el rètol de bombetes (66, 42 a 480)


def _flicks(t):
    """Finestres que tremolen: {(nau, índex): quant}. Dues amb el foc de dins i una que s'enfosqueix un sol
    fotograma (algú hi passa per davant)."""
    if not t:
        return {}
    ph = 2 * math.pi * t
    return {('A', 4): 0.45 * (math.sin(ph * 3) + 0.6 * math.sin(ph * 7 + 1) - 0.6 * math.sin(1)),
            ('B', 7): 0.4 * (math.sin(ph * 4 + 2) - math.sin(2)) + 0.25 * math.sin(ph * 9),
            ('A', 7): -1.6 if 17 <= t * 24 < 18 else 0.0}


def factory(cv, retol=True, t=0.0):
    tt = t
    ph = 2 * math.pi * tt
    fl = _flicks(tt)
    # xemeneies (darrere les naus)
    chimney(cv, 53, 69, 53, A_TOP, flick=0.18 * (math.sin(ph * 2) - 0))
    chimney(cv, 285, 299, 69, A_TOP, flick=0.18 * (math.sin(ph * 3 + 1) - math.sin(1)))
    chimney(cv, 571, 587, 45, B_TOP, flick=0.18 * (math.sin(ph * 5 + 2) - math.sin(2)))

    # ── Nau A: teulada de pissarra amb un llanternó de finestretes ──
    RY = 104
    roof = [(A_X0 - 5, A_TOP), (A_X0 + 35, RY), (A_X1 - 35, RY), (A_X1 + 5, A_TOP)]

    def slate(x, y):
        row = (y - RY) // 4
        lvl = 2.0 + (y - RY) / 32 * 1.2 + (hr((x + row * 4) // 8, row, 2) - 0.5) * 0.5
        if (y - RY) % 4 == 0:
            lvl -= 0.9                                              # fileres de pissarra
        elif (y - RY) % 4 == 3:
            lvl += 0.3                                              # el cantell de baix de cada pissarra
        if (x + row * 4) % 8 == 0:
            lvl -= 0.5
        return lvl + max(0.0, 1 - abs(x - 307) / 213) * 1.2         # reflex de la lluna
    cv.poly(roof, SLATE, slate, 0.5)
    cv.line(A_X0 - 5, A_TOP, A_X0 + 35, RY, SLATE, 3.4, 0.5)        # els carenals dels angles
    cv.line(A_X1 + 5, A_TOP, A_X1 - 35, RY, SLATE, 4.4, 0.5)
    cv.rect(61, 91, 296, 103, SLATE, lambda x, y: 2.6 if y < 94 else 1.6, 0.5)    # llanternó
    cv.hline(59, 298, 90, SLATE, 4.2, 0.5)
    cv.hline(59, 298, 89, SLATE, 3.0, 0.5)
    for x in range(69, 291, 9):
        lit = hr(x, 6) > 0.3
        cv.rect(x, 95, x + 4, 101, GLASS if lit else NAVY, (lambda a, b: 3.9 - (b - 95) * 0.1) if lit else 1.2, 0)
        cv.vline(x + 2, 95, 101, IRON, 1.0, 0)                      # el muntant del mig
        cv.hline(x - 1, x + 5, 102, SLATE, 3.6, 0.5)                # l'ampit
    # el rètol: bastida de ferro i lletres de bombetes
    if retol:
        bl = bulbs(SIGN, SX0, SY0)
        sw = len(SIGN) * 11 - 2
        for lx in (SX0 + 11, SX0 + sw // 2, SX0 + sw - 11):         # potes de la bastida
            cv.line(lx, SY0 + 17, lx - 7, 89, IRON, 1.6, 0)
            cv.line(lx, SY0 + 17, lx + 7, 89, IRON, 1.6, 0)
            cv.line(lx, SY0 + 17, lx, 89, IRON, 1.2, 0)
        cv.hline(SX0 - 4, SX0 + sw + 3, SY0 + 17, IRON, 2.4, 0)
        cv.hline(SX0 - 4, SX0 + sw + 3, SY0 + 18, IRON, 1.2, 0)
        cv.hline(SX0 - 4, SX0 + sw + 3, SY0 - 4, IRON, 2.0, 0)
        for x in range(SX0 - 4, SX0 + sw + 4, 8):
            cv.line(x, SY0 - 4, x + 8, SY0 + 17, IRON, 1.2, 0)
        for x in range(SX0 - 4, SX0 + sw + 4, 16):
            cv.vline(x, SY0 - 4, SY0 + 17, IRON, 1.4, 0)
        # una onada de llum recorre les bombetes, un cop per bucle (amb t = 0 encara no ha entrat)
        wave = -18 + tt * (sw + 36)
        for x, y, n, i, j in bl:
            cols = [(255, 244, 196), (250, 206, 120), (250, 206, 120), (196, 134, 70)]
            if tt:
                k = max(0.0, 1 - abs(x - SX0 - wave) / 12)
                if k:
                    cols = [mix(c, (255, 252, 236), k * 0.85) for c in cols]
                if (n, i, j) == (9, 0, 0) and round(tt * 24) in (4, 13, 14):
                    cols = [mix(c, (120, 70, 40), 0.7) for c in cols]   # una bombeta fluixa
            for (dx, dy), c in zip(((0, 0), (1, 0), (0, 1), (1, 1)), cols):
                cv.flat(x + dx, y + dy, c)

    # ── Nau A: paret de maó amb pilastres i finestrals ──
    bricks(cv, A_X0, A_TOP, A_X1, QY - 1, seed=1)
    cv.rect(A_X0 - 3, A_TOP - 1, A_X1 + 3, A_TOP + 3, STONE, lambda x, y: [4.8, 4.0, 3.2, 2.2, 1.0][y - A_TOP + 1])  # cornisa
    for x in range(A_X0, A_X1 + 1, 4):                              # dentells
        cv.rect(x, A_TOP + 4, x + 1, A_TOP + 5, STONE, 2.6)
    for i in range(11):                                             # pilastres
        px = round(27 + i * PITCH)
        if px > A_X1 - 3:
            break
        cv.rect(px, A_TOP + 6, px + 4, QY - 1, BRICK, lambda x, y, p=px: 2.8 + (x - p) * 0.3 + (-0.8 if y % 4 == 3 else 0))
        cv.vline(px + 5, A_TOP + 6, QY - 1, BRICK, 0.6)
        cv.rect(px - 1, A_TOP + 6, px + 5, A_TOP + 7, STONE, lambda x, y: 3.8 - (y - A_TOP - 6))   # capitell
    for i, (x, y, w, h, lit) in enumerate(WIN_A):
        window(cv, x, y, w, h, lit, seed=i, flick=fl.get(('A', i), 0.0))
    for i, (x, y, w, h, lit) in enumerate(WIN_A_LOW):
        cv.rect(x - 2, y - 2, x + w + 1, y + h + 1, STONE, lambda a, b: 3.0 + (0.8 if b == y - 2 else 0))
        cv.rect(x, y, x + w - 1, y + h - 1, GLASS if lit else NAVY, (lambda a, b: 3.0 + (b - y) * 0.15) if lit else 1.2, 0)
        cv.vline(x + w // 2, y, y + h - 1, IRON, 1.0, 0)
        cv.hline(x, x + w - 1, y + h // 2, IRON, 1.0, 0)
    cv.rect(A_X0, QY - 8, A_X1, QY - 1, STONE, lambda x, y: 2.2 - (y - QY + 8) * 0.15 - (0.8 if (x // 14 + y) % 7 == 0 and y > QY - 7 else 0))   # sòcol
    cv.hline(A_X0, A_X1, QY - 8, STONE, 3.4)

    # ── Nau B: façana de capçal amb frontó ──
    bricks(cv, B_X0, B_TOP, B_X1, QY - 1, base=2.3, seed=2)
    px_, py_ = B_PEAK
    gable = [(B_X0, B_TOP), (px_, py_), (B_X1, B_TOP)]
    cv.poly(gable, BRICK, lambda x, y: 2.2 + (hr((x + (y // 4 % 2) * 5) // 10, y // 4, 5) - 0.5) * 0.6
            - (1.0 if y % 4 == 3 else 0) - (0.8 if (x + (y // 4 % 2) * 5) % 10 == 9 else 0))
    for k in range(5):                                              # albardilla del frontó
        cv.line(B_X0 - 4, B_TOP + 1 - k, px_, py_ - k, STONE, 4.8 - k * 0.7)
        cv.line(px_, py_ - k, B_X1 + 4, B_TOP + 1 - k, STONE, 4.0 - k * 0.7)
    cv.rect(px_ - 2, py_ - 8, px_ + 2, py_ - 4, STONE, lambda x, y: 4.6 - (x - px_) * 0.4)   # l'acroteri del cim
    cv.rect(B_X0 - 3, B_TOP, B_X1 + 3, B_TOP + 4, STONE, lambda x, y: [4.6, 3.8, 3.0, 2.2, 1.0][y - B_TOP])
    for x in range(B_X0, B_X1 + 1, 4):                              # dentells
        cv.rect(x, B_TOP + 5, x + 1, B_TOP + 6, STONE, 2.6)
    for px in (B_X0, B_X0 + 72, B_X1 - 77, B_X1 - 5):              # pilastres de cantonada i del mig
        cv.rect(px, B_TOP + 7, px + 5, QY - 1, BRICK, lambda x, y, p=px: 3.0 + (x - p) * 0.3 + (-0.8 if y % 4 == 3 else 0))
        cv.rect(px - 1, B_TOP + 7, px + 6, B_TOP + 8, STONE, lambda x, y: 3.8 - (y - B_TOP - 7))
    # l'ull de bou: una roda dentada de ferro
    ox, oy, orr = px_, 96, 13
    for y in range(oy - orr - 6, oy + orr + 7):
        for x in range(ox - orr - 6, ox + orr + 7):
            d = math.hypot(x - ox, y - oy)
            a = math.atan2(y - oy, x - ox)
            tooth = orr + 2.1 + (1.9 if math.cos(a * 10) > 0.2 else 0)
            if d <= orr - 2.5:
                spoke = min(abs(math.sin(a * 3 - 0.3)) * d, 99) < 1.3 or d < 3.2
                if spoke:
                    cv.put(x, y, IRON, 1.2 + (0.8 if d < 2 else 0), 0)
                else:
                    cv.put(x, y, GLASS, 3.4 + (1 - d / orr) * 1.6 + (0.5 if (x + y) % 7 == 0 else 0), 0)
            elif d <= tooth:
                lvl = 2.2 + (x - ox) / orr * 0.8 - (y - oy) / orr * 0.4
                if abs(d - (orr - 0.5)) < 0.6 and math.cos(a * 5) > 0.95:
                    lvl += 1.6                                      # els cargols de la llanta
                if d > tooth - 0.8:
                    lvl += 0.6
                cv.put(x, y, IRON, lvl)
            elif d <= tooth + 1.6 and d > orr + 1.9:
                cv.put(x, y, STONE, 3.4)
    for i, (x, y, w, h, lit) in enumerate(WIN_B):
        window(cv, x, y, w, h, lit, seed=20 + i, flick=fl.get(('B', i), 0.0))
    # el portal dels forns, mig obert: a dins, foc
    x0, y0, x1, y1 = PORTAL
    r = (x1 - x0) / 2
    cxp = (x0 + x1) / 2
    for y in range(y0 - 5, y1 + 1):
        for x in range(x0 - 5, x1 + 6):
            dy = max(0.0, (y0 + r) - y)
            d_in = math.hypot(x - cxp, dy) if y < y0 + r else abs(x - cxp)
            if y >= y0 and d_in <= r:
                ix = x - x0
                if ix < 9 or ix > x1 - x0 - 11:                    # les dues fulles de fusta, obertes a mitges
                    plank = (x - x0) % 5 == 0
                    lvl = 2.0 + (0.0 if plank else 0.8) + (1.0 if ix > 27 else 0)
                    if (y - y0) % 30 in (24, 25):
                        lvl = 1.4 if ix > 27 else 1.0               # les frontisses de ferro
                        cv.put(x, y, IRON, lvl + 1.0)
                        continue
                    cv.put(x, y, WALNUT, lvl)
                else:
                    depth = (y - y0) / (y1 - y0)
                    lvl = 2.6 + depth * 3.4 - abs(x - cxp) / r * 1.0 + (hr(x // 5, y // 8, 9) - 0.5) * 0.3
                    if y > y1 - 19 and abs(x - cxp - 3) < 9 and y > y1 - 19 + abs(x - cxp - 3):
                        lvl += 1.6                                  # la boca d'un forn
                    if 8 < y - y0 < 13:
                        lvl -= 2.2                                  # una biga a contrallum
                    if tt:                                          # el foc respira i les flames pugen
                        u, v = x / K, y / K
                        q = v * 0.45 + math.sin(u * 0.35) * 0.9
                        lvl += 0.28 * (math.sin(ph * 3 + q) - math.sin(q)) + 0.25 * depth * (math.sin(ph * 5 + v * 0.6) - math.sin(v * 0.6))
                    cv.put(x, y, FIRE, lvl, 0)
            elif d_in <= r + 4 and y >= y0 - 4:
                lvl = 3.6 + (0.8 if x > cxp else 0)
                if y < y0 + r:                                      # dovelles de l'arc
                    a = math.atan2(y - (y0 + r), x - cxp)
                    if (a / (math.pi / 9)) % 1 < 0.12:
                        lvl -= 1.3
                elif (y - y0) % 10 == 0:
                    lvl -= 1.1
                cv.put(x, y, STONE, lvl)
    # carrils que surten del portal fins al moll
    for rx in (461, 491):
        cv.vline(rx, QY - 7, QY - 1, IRON, 4.4)
        cv.vline(rx + 1, QY - 7, QY - 1, IRON, 2.4)
    cv.rect(B_X0, QY - 8, x0 - 6, QY - 1, STONE, 2.2)
    cv.rect(x1 + 6, QY - 8, B_X1, QY - 1, STONE, 2.2)
    cv.hline(B_X0, x0 - 6, QY - 8, STONE, 3.4)
    cv.hline(x1 + 6, B_X1, QY - 8, STONE, 3.4)
    # rètol de la porta
    cv.rect(440, 160, 512, 170, IRON, lambda x, y: 1.2 + (1.4 if y == 160 else 0) - (0.6 if y == 170 else 0))
    for bx, by in ((442, 162), (510, 162), (442, 168), (510, 168)):
        cv.put(bx, by, IRON, 4.6)                                   # els cargols
    for x, y in text_px('FERRO-9', 440 + (73 - 41) // 2, 162):
        cv.put(x, y, GOLD, 4.6 + (0.8 if y == 162 else 0))

    # baixants de coure entre les naus
    for x in (343, 344, 345):
        cv.vline(x, A_TOP, QY - 1, COPPER, (1.4, 2.8, 1.8)[x - 343])
    cv.rect(341, A_TOP, 347, A_TOP + 3, COPPER, 3.2)
    for y in range(A_TOP + 22, QY - 4, 26):                         # les abraçadores
        cv.hline(342, 346, y, COPPER, 3.8)


def quay(cv, t=0.0):
    """El moll: un mur de carreus, noràis, un fanal i una gavarra de carbó amarrada. Amb `t`, el gas del fanal
    tremola."""
    ph = 2 * math.pi * t
    gas = 0.3 * (math.sin(ph * 5 + 0.7) - math.sin(0.7)) + 0.2 * math.sin(ph * 11) if t else 0.0
    for y in range(QY, QY + 12):
        for x in range(W):
            row = (y - QY) // 5
            joint = (y - QY) % 5 == 4 or (x + row * 9) % 19 == 18
            lvl = 2.6 - (y - QY) * 0.11 + (hr((x + row * 9) // 19, row, 7) - 0.5) * 0.5
            if (y - QY) % 5 == 0 and not joint:
                lvl += 0.3
            cv.put(x, y, STONE, lvl - (1.2 if joint else 0))
    cv.hline(0, W - 1, QY, STONE, 4.4)
    cv.hline(0, W - 1, QY + 1, STONE, 3.4)
    for bx in (80, 224, 389, 560):                                  # noràis
        cv.rect(bx, QY - 7, bx + 4, QY - 1, IRON, lambda x, y, b=bx: 2.0 + (x - b) * 0.5)
        cv.rect(bx - 1, QY - 8, bx + 5, QY - 8, IRON, 3.6)
        cv.hline(bx, bx + 4, QY - 9, IRON, 2.8)
    # fanal de gas
    lx = 315
    cv.vline(lx, 203, QY - 1, IRON, 1.6)
    cv.vline(lx + 1, 203, QY - 1, IRON, 2.6)
    cv.rect(lx - 3, QY - 5, lx + 4, QY - 1, IRON, 2.0)
    cv.hline(lx - 2, lx + 3, QY - 6, IRON, 2.6)
    cv.hline(lx - 2, lx + 3, 220, IRON, 2.2)                        # l'anella del pal
    cv.poly([(lx - 4, 203), (lx + 6, 203), (lx + 4, 192), (lx - 2, 192)], GLASS, 5.4 + gas, 0)
    for xx in (lx - 2, lx + 3):                                     # el marc de la llanterna
        cv.line(xx + (-1 if xx < lx else 1), 203, xx, 192, IRON, 1.8, 0)
    cv.hline(lx - 4, lx + 5, 204, IRON, 2.2)
    cv.hline(lx - 4, lx + 5, 191, IRON, 2.0)
    cv.hline(lx - 2, lx + 3, 190, IRON, 2.4)
    cv.put(lx, 189, IRON, 2.0)
    cv.put(lx + 1, 189, IRON, 2.6)
    cv.put(lx, 188, IRON, 2.0)
    cv.glow(lx + 0.5, 197, 40, (255, 200, 110), 0.5)
    cv.glow(lx + 0.5, 197, 12, (255, 240, 190), 0.8 + gas * 0.3)


def barge(cv):
    """Gavarra de ferro carregada de mineral, amarrada davant de la nau gran."""
    x0, x1, yt = 93, 261, QY + 9
    hh = 13
    for y in range(yt, yt + hh):
        t = (y - yt) / (hh - 1)
        a, b = x0 + t * 4, x1 - t * 13
        for x in range(math.floor(a), math.ceil(b) + 1):
            if y == yt:
                lvl = 3.5                                           # regala
            elif y == yt + 1:
                lvl = 2.6
            elif y == yt + 2:
                lvl = 1.5
            else:
                lvl = 2.5 - t * 1.6 + (0.5 if (x - x0) % 21 in (0, 1) else 0)      # planxes reblades
                if (x - x0) % 21 == 2:
                    lvl -= 0.8
                if y in (yt + 4, yt + 10) and (x - x0) % 4 == 1:
                    lvl += 1.2                                      # reblons
            cv.put(x, y, RUST, lvl)
    # mineral apilat
    for x in range(x0 + 5, x1 - 8):
        hgt = 8 + math.sin((x - x0) / 14.7) * 4 + math.sin((x - x0) / 5.7) * 1.6
        for y in range(int(yt - hgt), yt):
            lvl = 1.5 + (yt - y) / hgt * 1.0 + (1.0 if y == int(yt - hgt) else 0)
            if hr(x, y, 3) > 0.9:
                lvl += 1.5                                          # un brill de lluna
            if hr(x // 2, y // 2, 4) > 0.85:
                lvl -= 0.7                                          # un tros més gros, amb ombra
            cv.put(x, y, IRON, lvl)
    # corda d'amarratge fins al norai
    for i in range(22):
        t = i / 21
        cv.put(80 + 2 + (x0 + 4 - 82) * t, QY - 5 + (yt - QY + 5) * t + math.sin(t * math.pi) * 3, WALNUT, 3.5)
    # el reflex fosc de la gavarra
    cv.darken(x0, yt + hh, x1 - 13, yt + hh + 8, lambda x, y: 0.9 - (y - yt - hh) * 0.1)


def canal(cv, t=0.0):
    """L'aigua: el reflex de tot el que hi ha a dalt, trencat per les ones, i la columna de la lluna.
    Amb `t` (0..1, bucle d'animació), les ones s'acosten i els reflexos tremolen. Les ones tenen la mida de 480."""
    ph = 2 * math.pi * t
    src = cv.img.copy()
    S = src.load()
    WY = QY + 12                                                    # línia de l'aigua
    for y in range(WY, H):
        depth = (y - WY) / K
        v = y / K
        for x in range(W):
            u = x / K
            wob = math.sin(v * 0.9 + math.sin(u * 0.07 + ph) * 1.5 - ph * 2) * (1 + depth * 0.05) * K
            sy = WY - 1 - int((y - WY) * 1.15)
            sx = int(x + wob)
            base = 1.4 + depth / 90
            lvl = base + (0.6 if hr(x // 12, y, 4) > 0.8 else 0)
            cv.put(x, y, WATER, lvl, 0)
            if 0 <= sy < H and 0 <= sx < W and sy > 0:
                # bandes d'ona: el reflex surt a franges
                ripple = math.sin(v * 1.7 + math.sin(u / 13 + v - ph) * 2 - ph * 3) > -0.2 - depth / 120
                if ripple:
                    c = S[sx, sy]
                    k = 0.55 - depth / 220
                    o = cv.get(x, y)
                    lum = sum(c[:3]) / 3
                    if lum > 70 and k > 0:
                        cv.flat(x, y, mix(o, c, min(1, k * 1.1)))
                    elif k > 0:
                        cv.flat(x, y, mix(o, c, k * 0.5))
    # la columna de la lluna a l'aigua
    mx = MOON[0]
    for y in range(WY, H):
        depth = (y - WY) / K
        v = y / K
        spread = (4 + depth * 0.18) * K
        for x in range(int(mx - spread * 2), int(mx + spread * 2) + 1):
            u = x / K
            d = abs(x - mx + math.sin(v * 1.3 - ph * 2) * 2 * K) / spread
            if d < 1 and math.sin(v * 2.1 + u * 0.3 - ph * 3) > 0.1 + d * 0.6:
                cv.flat(x, y, mix(cv.get(x, y), (210, 214, 240), 0.7 - d * 0.4))
    # vora fosca sota el mur
    cv.darken(0, WY, W - 1, WY + 3, 0.8)


def railing(cv):
    """La barana de ferro de l'altra riba, des d'on mirem: a contrallum, a baix de tot."""
    for y in range(341, H):
        for x in range(W):
            cv.put(x, y, SIL, 1.5 + (1.0 if y == 341 else 0) - (y - 341) * 0.06, 0)
    for x in range(0, W):
        cv.put(x, 317, SIL, 1.5 + (0.6 if hr(x // 53) > 0.5 else 0.0), 0)
        cv.put(x, 318, SIL, 0.5, 0)
        cv.put(x, 319, SIL, 0.5, 0)
        cv.put(x, 333, SIL, 0.5, 0)
        cv.put(x, 334, SIL, 0.5, 0)
    for x in range(5, W, 12):
        cv.vline(x, 320, 340, SIL, 0.5, 0)
        if (x // 12) % 2:                                              # els rínxols de ferro
            for dx, dy in ((0, 325), (-1, 326), (1, 326), (-2, 327), (2, 327), (-1, 328), (1, 328), (0, 329)):
                cv.put(x + dx, dy, SIL, 0.5, 0)
    for x in range(0, W, 96):                                          # pilars
        cv.rect(x + 40, 309, x + 48, 341, SIL, lambda a, b: 0.5 + (0.6 if a == x + 48 else 0), 0)
        cv.rect(x + 39, 306, x + 49, 309, SIL, lambda a, b: 1.5 + (0.8 if b == 306 else 0), 0)
        cv.rect(x + 42, 303, x + 46, 305, SIL, 1.0, 0)                 # la bola del pilar
    # el reflex de la lluna i dels forns a la barana
    cv.hline(0, W - 1, 316, SIL, 2.5, 0)


def bg(cv, retol=True, t=0.0):
    """`t` (0..1): moment del bucle de l'animació de fons (amb 0, el fons quiet)."""
    sky(cv)
    city(cv)
    factory(cv, retol, t=t)
    smoke(cv, [(61, 48, 253), (292, 64, 227), (579, 40, 120)], t=t)
    quay(cv, t=t)
    canal(cv, t=t)
    barge(cv)
    railing(cv)
    vinyeta(cv, 0.6)


PROPS = {}

# ─── L'Iri entra al torn de nit (capa del pròleg) ────────────────────────────
# Mentre la narració presenta la fàbrica, l'Iri (petita, 28 píxels) passa pel moll sota el fanal, s'atura davant del
# portal dels forns, es gira i entra a la llum («iri_torn», sense bucle: es queda buida). Fins llavors, la capa és
# buida («iri_moll»). Sense el reflex al canal: el faria quiet damunt de l'aigua que es mou.
# La intro en vídeo (intro_animada.py) fa servir el mateix dibuix.

LAMP, PORTAL_C = (315, 197), (476, 214)
FEET_Y = 246
IRI_WALK = (0.0, 5.4)             # del fanal al portal
IRI_ENTER = (5.4, 6.5)            # es gira i s'endinsa a la llum
IRI_X0 = 282


def warm_at(x, y):
    """Quanta llum càlida hi ha a (x, y): la del fanal i la del portal (0..1)."""
    lamp = max(0.0, 1 - math.hypot(x - LAMP[0], (y - LAMP[1]) * 1.3) / 46)
    port = max(0.0, 1 - math.hypot(x - PORTAL_C[0], (y - PORTAL_C[1]) * 0.8) / 60)
    return min(1.0, lamp * 1.2 + port * 1.1)


def iri_petita(cv, fx, fy, t, facing, walking):
    """L'Iri petita (28 píxels), de nit: la bata blanca, la trena fosca. `facing`: 1 cap a la dreta, 0 d'esquena (a
    contrallum: silueta amb la vora encesa). `t`, en segons, mou les cames si `walking`."""
    HAIR, BRAID, SKN, LEG, SHOE = (46, 28, 22), (36, 22, 18), (196, 150, 120), (72, 68, 84), (26, 20, 22)
    COAT_N, COAT_W = (78, 80, 98), (250, 214, 160)
    ph = int(t * 10) % 4 if walking else 0                        # 4 passos per cicle
    bob = 1 if ph in (1, 3) else 0
    y0 = fy - 27 + bob

    def coat(x, y, edge=0.0):
        w = warm_at(x, y)
        if not facing:
            return (255, 196, 120) if edge else mix((34, 24, 28), (90, 50, 34), w * 0.5)
        c = mix(COAT_N, COAT_W, w * 0.85)
        return mix(c, (20, 18, 26), edge)

    def leg(x, y):
        return mix(LEG, (120, 80, 60), warm_at(x, y) * 0.5) if facing else (22, 16, 18)

    # les cames: obertes (0, 2) o juntes (1, 3)
    spread = (3, -3) if ph == 0 else ((-3, 3) if ph == 2 else (0, 0))
    for i, s in enumerate(spread):
        lx = fx - 1 + i * 2
        for y in range(fy - 8, fy):
            xx = lx + (round(s * (y - (fy - 8)) / 7) if facing else 0)
            cv.flat(xx, y, leg(xx, y))
        if facing:
            cv.flat(lx + s + 1, fy - 1, SHOE)
            cv.flat(lx + s, fy - 1, SHOE)
    # la bata: de les espatlles als genolls, s'eixampla una mica
    for y in range(y0 + 7, fy - 7 + bob):
        half = 3 if y < y0 + 15 else 4
        for x in range(fx - half, fx + half):
            if facing:
                edge = 0.45 if x == fx - half else (0.2 if x == fx + half - 1 else 0.0)
            else:
                edge = 1 if x in (fx - half, fx + half - 1) and hr(x, y, 8) > 0.3 else 0
            cv.flat(x, y, coat(x, y, edge))
    # el braç, que es balanceja
    if facing:
        sw = (1 if ph == 0 else -1 if ph == 2 else 0)
        for k in range(8):
            cv.flat(fx + round(sw * k / 7), y0 + 8 + k, coat(fx, y0 + 8 + k, 0.3))
        cv.flat(fx + sw, y0 + 16, SKN)
    # el cap i els cabells
    for y in range(y0, y0 + 6):
        for x in range(fx - 2, fx + 3):
            face = facing and x >= fx + 1 and y >= y0 + 2
            hair = HAIR if facing else ((150, 90, 60) if x in (fx - 2, fx + 2) else (24, 16, 14))
            cv.flat(x, y, mix(SKN, (40, 30, 40), 0.35 * (1 - warm_at(x, y))) if face else hair)
    if facing:
        cv.flat(fx + 3, y0 + 3, mix(SKN, (40, 30, 40), 0.3))                     # el nas
        cv.flat(fx, y0, (110, 180, 180))                                          # les ulleres a la diadema
        cv.flat(fx + 1, y0, (70, 120, 120))
    # la trena, a l'esquena
    bx = fx - 3 if facing else fx
    for y in range(y0 + 4, y0 + 15):
        cv.flat(bx, y, BRAID)
    cv.flat(bx, y0 + 15, (150, 30, 30))                                           # la goma vermella


def iri_torn(cv, t):
    """L'Iri al moll al segon `t` del seu tros: → quant s'ha fos ja amb la llum (0..1), per a la fosa tramada."""
    if t < IRI_WALK[1]:
        u = max(0.0, (t - IRI_WALK[0]) / (IRI_WALK[1] - IRI_WALK[0]))
        iri_petita(cv, round(IRI_X0 + (PORTAL_C[0] - IRI_X0) * u), FEET_Y, t, 1, True)
        return 0.0
    u = min(1.0, (t - IRI_ENTER[0]) / (IRI_ENTER[1] - IRI_ENTER[0]))
    iri_petita(cv, PORTAL_C[0], FEET_Y - round(u * 2), t, 0, u < 1)
    return max(0.0, (u - 0.35) / 0.65)


def _base():
    from hd.pix import Canvas
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv.img


def _iri_frames():
    import numpy as np
    from hd.pix import Canvas
    from hd640.rooms.fabrica_cambra import frame_diff
    base = _base()
    bayer = np.array([[(B4[y & 3][x & 3]) for x in range(W)] for y in range(H)])
    out = []
    for i in range(round(IRI_ENTER[1] / 0.1) + 2):
        cv = Canvas(light=LIGHT, img=base.copy())
        cv.P = cv.img.load()
        gone = iri_torn(cv, i * 0.1)
        d = np.array(frame_diff(base, cv.img))
        if gone > 0:
            d[bayer < gone, 3] = 0
        out.append(Image.fromarray(d, 'RGBA'))
    out.append(Canvas(transparent=True).img)                                       # ja és a dins
    return out


ANIMS = {
    'ambient': {'frames': lambda: ambient_frames(bg, LIGHT), 'frameDuration': 130},
    'iri_moll': {'frames': lambda: [Image.new('RGBA', (W, H))], 'frameDuration': 1000, 'loop': False, 'zIndex': 2},
    'iri_torn': {'frames': _iri_frames, 'frameDuration': 100, 'loop': False, 'prop': 'iri_moll'},
}
