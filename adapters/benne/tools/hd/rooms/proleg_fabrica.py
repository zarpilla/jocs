"""
Pròleg 3 · «Cent vint anys abans...»: la fàbrica de ferro-9 de nit, vista des de l'altra riba del canal.
Dues naus de maó (la llarga, amb el rètol d'ALDAIA · FERRO-9 al teulat, i la de la façana amb l'ull de bou en
forma de roda dentada), tres xemeneies treient fum, la lluna, finestres enceses pel foc dels forns i el canal
amb els reflexos. Llums: la lluna (freda, de dalt a la dreta), les finestres i el portal dels forns, un fanal.
Pantalla sencera (sense barra de verbs). `bg` es reutilitza a la portada.
"""
import math
import random

from hd.pix import (Light, B4, W, H, hr, mix, ramp, BRICK, IRON, SMOKE, GLASS, FIRE, GOLD,
                    NAVY, SIL, PAPER, WALNUT, RUST, COPPER)
from hd.rooms.proleg_gavina import Noise, vinyeta, ambient_frames

# Rampes pròpies
SLATE = ramp((8, 8, 16), (16, 16, 28), (26, 26, 42), (40, 40, 58), (58, 58, 78), (84, 84, 104), (120, 118, 136), n=9)
STONE = ramp((20, 16, 22), (40, 32, 36), (64, 54, 54), (92, 80, 74), (124, 110, 98), (160, 146, 128), (200, 188, 166), n=9)
WATER = ramp((2, 4, 10), (6, 10, 22), (10, 16, 34), (16, 24, 48), (24, 34, 62), (36, 48, 80), n=8)
NIGHT = ramp((4, 4, 12), (8, 8, 22), (14, 14, 34), (24, 20, 48), (40, 28, 60), (64, 38, 66), (100, 52, 66),
             (146, 72, 62), (196, 104, 64), (236, 150, 84), n=12)

QY = 186           # vora del moll (on comença el canal)
MOON = (398, 40)

# Finestres: (x0, y0, amplada, alçada, encesa?)
WIN_A = [(26 + i * 22, 116, 12, 30, i not in (2, 6, 9)) for i in range(10)]
WIN_A_LOW = [(30 + i * 22, 158, 6, 8, i in (0, 1, 3, 4, 7, 8)) for i in range(10)]
WIN_B = [(x, y, 12, 26, lit) for (x, y, lit) in
         ((280, 104, True), (306, 104, False), (396, 104, True), (422, 104, True),
          (280, 144, True), (306, 144, True), (396, 144, False), (422, 144, True))]
PORTAL = (338, 132, 376, QY - 1)       # el portal dels forns, mig obert


def _light():
    L = Light(ambient=0.0, vignette=None, floor_fade=None)
    for x, y, w, h, lit in WIN_A + WIN_B:
        if lit:
            L.point(x + w / 2, y + h * 0.7, r=22, k=1.3, squash=1.3)
    for x, y, w, h, lit in WIN_A_LOW:
        if lit:
            L.point(x + w / 2, y + h / 2, r=10, k=0.8)
    L.point(357, 170, r=70, k=2.8, squash=0.9)             # el foc del portal
    L.point(236, 158, r=46, k=2.0, squash=1.0)             # el fanal del moll
    return L


LIGHT = _light()
N_SMOKE, N_CLOUD = Noise(31), Noise(32)

# Lletres de 3×5 per al rètol
FONT = {
    'A': ['010', '101', '111', '101', '101'], 'L': ['100', '100', '100', '100', '111'],
    'D': ['110', '101', '101', '101', '110'], 'I': ['111', '010', '010', '010', '111'],
    'F': ['111', '100', '110', '100', '100'], 'E': ['111', '100', '110', '100', '111'],
    'R': ['110', '101', '110', '101', '101'], 'O': ['010', '101', '101', '101', '010'],
    '-': ['000', '000', '111', '000', '000'], '9': ['010', '101', '011', '001', '110'],
    '·': ['000', '000', '010', '000', '000'], ' ': ['000', '000', '000', '000', '000'],
}


def text_px(text, x0, y0, k=1):
    """Píxels (x, y) d'un text en la lletra de 3×5, a escala k."""
    out = []
    x = x0
    for ch in text:
        for j, row in enumerate(FONT[ch]):
            for i, b in enumerate(row):
                if b == '1':
                    for a in range(k):
                        for c in range(k):
                            out.append((x + i * k + a, y0 + j * k + c))
        x += 4 * k
    return out


# ─── Peces ──────────────────────────────────────────────────────────────────

def sky(cv):
    rnd = random.Random(12)
    stars = {(rnd.randint(0, W - 1), rnd.randint(0, 110)) for _ in range(150)}
    for y in range(0, QY):
        for x in range(W):
            t = y / 150
            lvl = 0.6 + t ** 2.2 * 7.4                              # el resplendor dels forns i de la ciutat
            lvl += max(0.0, 1 - abs(x - 300) / 260) * t ** 3 * 1.2
            dm = math.hypot(x - MOON[0], y - MOON[1])
            if dm < 70:
                lvl += (1 - dm / 70) ** 2 * 2.2
            ds = math.hypot((x - 128) / 90, (y - 50) / 22)          # el rètol encès escalfa el cel
            if ds < 1:
                lvl += (1 - ds) ** 2 * 1.4
            # núvols prims, amb la vora encesa per la lluna
            c = N_CLOUD.fbm(x / 70, y / 14, 4)
            band = max(0.0, 1 - abs(y - 58) / 30)
            if c * band > 0.42:
                lvl += 0.8 + (1.2 if dm < 90 else 0) * (1 - dm / 90)
            cv.put(x, y, NIGHT, lvl, 0)
            if (x, y) in stars and dm > 16 and c * band < 0.4:
                b = hr(x, y, 2)
                cv.flat(x, y, mix((120, 110, 160), (240, 236, 255), b) if y < 90 else (150, 120, 140))
    # la lluna
    mx, my = MOON
    cv.glow(mx, my, 30, (200, 200, 230), 0.35)
    cv.disc(mx, my, 10, 10, PAPER, lambda nx, ny: 5.5 if nx * nx + ny * ny < 0.7 or nx > 0 else 4.6, 0)
    for dx, dy, r in ((-3, -2, 2.4), (3, 3, 1.8), (-1, 5, 1.4), (4, -4, 1.2)):
        cv.disc(mx + dx, my + dy, r, r, PAPER, 4.5, 0)


def city(cv):
    """La ciutat de fons, una silueta baixa amb finestretes i xemeneies llunyanes."""
    rnd = random.Random(4)
    sky_ = [QY] * W
    x = 0
    while x < W:
        w = rnd.randint(10, 26)
        top = rnd.randint(140, 160)
        for xx in range(x, min(W, x + w)):
            sky_[xx] = top
        if rnd.random() < 0.3:
            cx = x + rnd.randint(2, max(3, w - 3))
            for xx in range(cx, min(W, cx + 2)):
                sky_[xx] = top - rnd.randint(14, 26)
        x += w
    for x in range(W):
        for y in range(sky_[x], QY):
            if hr(x // 2, y // 3, 8) < 0.04 and y > sky_[x] + 2:
                cv.flat(x, y, (200, 130, 60))
            else:
                cv.put(x, y, SIL, 1.6 + (0.8 if y == sky_[x] else 0), 0)


def chimney(cv, x0, x1, top, base, lit_side=1, flick=0.0):
    """Xemeneia de maó, una mica cònica, amb anelles i un capçal; la boca brilla del foc."""
    for y in range(top, base + 1):
        t = (y - top) / max(1, base - top)
        inset = (1 - t) * 1.5
        a, b = x0 + inset, x1 - inset
        for x in range(math.floor(a), math.ceil(b) + 1):
            u = (x - a) / (b - a)
            row = y // 3
            mortar = y % 3 == 2 or (x + (row % 2) * 3) % 6 == 5
            lvl = 2.2 + u * 1.4 * lit_side - (1 - u) * 0.4 + (hr(x // 6, row, 3) - 0.5) * 0.6
            if mortar:
                lvl -= 0.9
            if (y - top) in (10, 11, 30, 31):
                lvl += 0.8                                          # anelles de ferro
                cv.put(x, y, IRON, 2.4 + u * 2.2, 0)
                continue
            cv.put(x, y, BRICK, lvl, 0)
    # capçal
    cv.rect(x0 - 2, top - 3, x1 + 2, top, BRICK, lambda x, y: 3.2 + (x - x0) / (x1 - x0) * 1.4 - (y - top + 3) * 0.3, 0)
    cv.hline(x0 - 1, x1 + 1, top - 4, FIRE, 3.6, 0)
    cv.glow((x0 + x1) / 2, top - 4, 8, (255, 140, 60), 0.6 + flick)


def smoke(cv, sources, t=0.0):
    """Plomalls de fum que el vent s'emporta cap a la dreta: encesos de taronja a la boca, grisos de lluna a dalt.
    `t` (0..1): moment del bucle d'animació. El fum flueix plomall amunt (el soroll es desplaça i es fon amb una
    còpia desplaçada un bucle enrere, perquè enllaci) i el vent el fa onejar. Amb t = 0, el fons quiet."""
    ph = 2 * math.pi * t
    VX, VY = 16.0, -3.0                                     # el que avança el fum en un bucle (píxels)
    wa, wb = 1 - t, t
    wn = math.sqrt(wa * wa + wb * wb)

    def noise(x, y):
        if not t:
            return N_SMOKE.fbm((x - y * 0.3) / 11, y / 8, 3)
        xa, ya = x - VX * t, y - VY * t
        xb, yb = xa + VX, ya + VY
        na = N_SMOKE.fbm((xa - ya * 0.3) / 11, ya / 8, 3)
        nb = N_SMOKE.fbm((xb - yb * 0.3) / 11, yb / 8, 3)
        return 0.5 + (wa * (na - 0.5) + wb * (nb - 0.5)) / wn
    Y1 = 150
    D = [[0.0] * W for _ in range(Y1)]
    WM = [[0.0] * W for _ in range(Y1)]
    for y in range(Y1):
        for x in range(W):
            best, warm = 0.0, 0.0
            for i, (sx, sy, length) in enumerate(sources):
                dx = x - sx
                if dx < -6 or dx > length or y > sy:
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
                d = abs(y - yc) / wid
                if d > 1.8:
                    continue
                n = noise(x, y)
                dens = (1 - d * 0.55) * (1 - te) ** 0.9 * (0.25 + n * 1.3)
                if dens > best:
                    best, warm = dens, max(0.0, 1 - e / 12) * max(0.0, 1 - (sy - y) / 14)
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
            up = D[y - 2][x] if y >= 2 else 0
            dn = D[y + 2][x] if y + 2 < Y1 else 0
            lvl = 1.5 + min(1.0, (v - TH) * 2.5) * 0.8
            if up <= TH:
                lvl += 1.4                                          # la vora de dalt, tocada per la lluna
            elif dn <= TH:
                lvl -= 0.8
            if WM[y][x] > 0.15:
                cv.put(x, y, NIGHT, 6.5 + WM[y][x] * 3, 0)
            else:
                cv.put(x, y, SMOKE, lvl, 0)


def bricks(cv, x0, y0, x1, y1, base=2.1, seed=0):
    def f(x, y):
        row = y // 3
        if y % 3 == 2:
            return base - 1.1
        if (x + (row % 2) * 4) % 8 == 7:
            return base - 0.9
        return base + (hr(((x + (row % 2) * 4) // 8), row, seed) - 0.5) * 0.7 - (y - y0) / 200
    cv.rect(x0, y0, x1, y1, BRICK, f)


def window(cv, x, y, w, h, lit, seed=0, flick=0.0):
    """Finestral de mig punt amb brancals de pedra i reixa de ferro."""
    r = w / 2
    cx = x + r - 0.5

    def inside(px, py, grow=0.0):
        if py >= y + r:
            return x - grow <= px <= x + w - 1 + grow and py <= y + h - 1 + grow
        return math.hypot(px - cx, py - (y + r)) <= r + grow - 0.3

    for py in range(int(y - 3), int(y + h + 3)):
        for px in range(int(x - 3), int(x + w + 3)):
            if inside(px, py):
                ix, iy = px - x, py - y
                mull = ix in (w // 3, 2 * w // 3) or (iy > r and (iy - int(r)) % 7 == 0)
                if mull:
                    cv.put(px, py, IRON, 1.0 if lit else 0.6, 0)
                elif lit:
                    # vidre encès: més calent a baix, on hi ha el foc; alguna silueta de màquina a dins
                    lvl = 2.2 + (iy / h) * 2.8 + (hr(seed, ix // 2, iy // 3) - 0.5) * 0.6 + flick
                    if hr(seed, 1) < 0.5 and iy > h * 0.55 and abs(ix - w / 2) < w * 0.3:
                        lvl -= 2.0                                  # una màquina a contrallum
                    cv.put(px, py, GLASS, lvl, 0)
                else:
                    lvl = 1.6 - iy / h * 0.6 + (1.4 if (ix + iy) % 9 == 0 and iy < h / 2 else 0)
                    cv.put(px, py, NAVY, lvl, 0)                    # fosc: hi rebota la lluna
            elif inside(px, py, 1.6):
                cv.put(px, py, STONE, 3.2 + (0.8 if px >= x + w - 1 else 0))   # brancal de pedra
    cv.rect(x - 2, y + h, x + w + 1, y + h + 1, STONE, lambda a, b: 4.2 - (b - y - h) * 1.6)    # ampit
    cv.rect(cx - 1, y - 3, cx + 1, y, STONE, 4.4)                                              # clau


# ─── La pantalla ────────────────────────────────────────────────────────────

A_X0, A_X1, A_TOP = 12, 256, 102          # nau llarga
B_X0, B_X1, B_TOP, B_PEAK = 262, 452, 92, (357, 50)   # nau de la façana


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
    chimney(cv, 40, 52, 40, A_TOP, flick=0.18 * (math.sin(ph * 2) - 0))
    chimney(cv, 214, 224, 52, A_TOP, flick=0.18 * (math.sin(ph * 3 + 1) - math.sin(1)))
    chimney(cv, 428, 440, 34, B_TOP, flick=0.18 * (math.sin(ph * 5 + 2) - math.sin(2)))

    # ── Nau A: teulada de pissarra amb un llanternó de finestretes ──
    roof = [(A_X0 - 4, A_TOP), (A_X0 + 26, 78), (A_X1 - 26, 78), (A_X1 + 4, A_TOP)]
    def slate(x, y):
        row = (y - 78) // 3
        lvl = 2.0 + (y - 78) / 24 * 1.2 + (hr((x + row * 3) // 6, row, 2) - 0.5) * 0.5
        if (y - 78) % 3 == 0:
            lvl -= 0.9                                              # fileres de pissarra
        if (x + row * 3) % 6 == 0:
            lvl -= 0.5
        return lvl + max(0.0, 1 - abs(x - 230) / 160) * 1.2         # reflex de la lluna
    cv.poly(roof, SLATE, slate, 0.5)
    cv.rect(46, 68, 222, 77, SLATE, lambda x, y: 2.6 if y < 70 else 1.6, 0.5)    # llanternó
    cv.hline(44, 224, 67, SLATE, 4.2, 0.5)
    for x in range(52, 218, 7):
        lit = hr(x, 6) > 0.3
        cv.rect(x, 71, x + 3, 75, GLASS if lit else NAVY, 3.6 if lit else 1.2, 0)
    # el rètol: bastida de ferro i lletres de bombetes
    if retol:
        SX0, SY0, txt = 66, 42, 'ALDAIA · FERRO-9'
        sw = len(txt) * 8 - 2
        for lx in (SX0 + 8, SX0 + sw // 2, SX0 + sw - 8):              # potes de la bastida
            cv.line(lx, SY0 + 14, lx - 5, 67, IRON, 1.6, 0)
            cv.line(lx, SY0 + 14, lx + 5, 67, IRON, 1.6, 0)
        cv.hline(SX0 - 3, SX0 + sw + 2, SY0 + 13, IRON, 2.4, 0)
        cv.hline(SX0 - 3, SX0 + sw + 2, SY0 - 3, IRON, 2.0, 0)
        for x in range(SX0 - 3, SX0 + sw + 3, 6):
            cv.line(x, SY0 - 3, x + 6, SY0 + 13, IRON, 1.2, 0)
        # una onada de llum recorre les bombetes, un cop per bucle (amb t = 0 encara no ha entrat)
        wave = -14 + tt * (sw + 28)
        for x, y in text_px(txt, SX0, SY0, 2):
            col = (255, 236, 170) if (x + y) % 2 else (250, 200, 110)
            if tt:
                k = max(0.0, 1 - abs(x - SX0 - wave) / 9)
                if k:
                    col = mix(col, (255, 252, 236), k * 0.85)
                if ((x - SX0) // 2, (y - SY0) // 2) == (36, 0) and round(tt * 24) in (4, 13, 14):
                    col = mix(col, (120, 70, 40), 0.7)                  # una bombeta fluixa
            cv.flat(x, y, col)

    # ── Nau A: paret de maó amb pilastres i finestrals ──
    bricks(cv, A_X0, A_TOP, A_X1, QY - 1, seed=1)
    cv.rect(A_X0 - 2, A_TOP - 1, A_X1 + 2, A_TOP + 2, STONE, lambda x, y: [4.6, 3.6, 2.4, 1.0][y - A_TOP + 1])  # cornisa
    for i in range(11):                                             # pilastres
        px = 20 + i * 22
        if px > A_X1 - 2:
            break
        cv.rect(px, A_TOP + 3, px + 3, QY - 1, BRICK, lambda x, y: 2.8 + (x - px) * 0.4)
        cv.vline(px + 4, A_TOP + 3, QY - 1, BRICK, 0.6)
    for i, (x, y, w, h, lit) in enumerate(WIN_A):
        window(cv, x, y, w, h, lit, seed=i, flick=fl.get(('A', i), 0.0))
    for i, (x, y, w, h, lit) in enumerate(WIN_A_LOW):
        cv.rect(x - 1, y - 1, x + w, y + h, STONE, 3.0)
        cv.rect(x, y, x + w - 1, y + h - 1, GLASS if lit else NAVY, (lambda a, b: 3.0 + (b - y) * 0.2) if lit else 1.2, 0)
    cv.rect(A_X0, QY - 6, A_X1, QY - 1, STONE, lambda x, y: 2.2 - (y - QY + 6) * 0.2)   # sòcol

    # ── Nau B: façana de capçal amb frontó ──
    bricks(cv, B_X0, B_TOP, B_X1, QY - 1, base=2.3, seed=2)
    px_, py_ = B_PEAK
    gable = [(B_X0, B_TOP), (px_, py_), (B_X1, B_TOP)]
    cv.poly(gable, BRICK, lambda x, y: 2.2 + (hr(x // 8, y // 3, 5) - 0.5) * 0.6 - (1.0 if y % 3 == 2 else 0))
    for k in range(4):                                              # albardilla del frontó
        cv.line(B_X0 - 3, B_TOP + 1 - k, px_, py_ - k, STONE, 4.6 - k * 0.8)
        cv.line(px_, py_ - k, B_X1 + 3, B_TOP + 1 - k, STONE, 3.8 - k * 0.8)
    cv.rect(B_X0 - 2, B_TOP, B_X1 + 2, B_TOP + 3, STONE, lambda x, y: [4.4, 3.4, 2.4, 1.0][y - B_TOP])
    for px in (B_X0, B_X0 + 54, B_X1 - 58, B_X1 - 4):              # pilastres de cantonada i del mig
        cv.rect(px, B_TOP + 4, px + 4, QY - 1, BRICK, lambda x, y, p=px: 3.0 + (x - p) * 0.35)
    # l'ull de bou: una roda dentada de ferro
    ox, oy, orr = px_, 72, 10
    for y in range(oy - orr - 3, oy + orr + 4):
        for x in range(ox - orr - 3, ox + orr + 4):
            d = math.hypot(x - ox, y - oy)
            a = math.atan2(y - oy, x - ox)
            tooth = orr + 1.6 + (1.4 if math.cos(a * 10) > 0.2 else 0)
            if d <= orr - 2:
                spoke = min(abs(math.sin(a * 3 - 0.3)) * d, 99) < 1.0 or d < 2.4
                if spoke:
                    cv.put(x, y, IRON, 1.2, 0)
                else:
                    cv.put(x, y, GLASS, 3.4 + (1 - d / orr) * 1.6, 0)
            elif d <= tooth:
                cv.put(x, y, IRON, 2.2 + (x - ox) / orr * 0.8 - (y - oy) / orr * 0.4)
            elif d <= tooth + 1.2 and d > orr + 1.4:
                cv.put(x, y, STONE, 3.4)
    for i, (x, y, w, h, lit) in enumerate(WIN_B):
        window(cv, x, y, w, h, lit, seed=20 + i, flick=fl.get(('B', i), 0.0))
    # el portal dels forns, mig obert: a dins, foc
    x0, y0, x1, y1 = PORTAL
    r = (x1 - x0) / 2
    cxp = (x0 + x1) / 2
    for y in range(y0 - 4, y1 + 1):
        for x in range(x0 - 4, x1 + 5):
            dy = max(0.0, (y0 + r) - y)
            d_in = math.hypot(x - cxp, dy) if y < y0 + r else abs(x - cxp)
            if y >= y0 and d_in <= r:
                ix = x - x0
                if ix < 7 or ix > x1 - x0 - 9:                     # les dues fulles de fusta, obertes a mitges
                    plank = (x - x0) % 4 == 0
                    cv.put(x, y, WALNUT, 2.0 + (0.0 if plank else 0.8) + (1.0 if ix > 20 else 0))
                else:
                    depth = (y - y0) / (y1 - y0)
                    lvl = 2.6 + depth * 3.4 - abs(x - cxp) / r * 1.0 + (hr(x // 4, y // 6, 9) - 0.5) * 0.3
                    if y > y1 - 14 and abs(x - cxp - 2) < 7 and y > y1 - 14 + abs(x - cxp - 2):
                        lvl += 1.6                                  # la boca d'un forn
                    if 6 < y - y0 < 10:
                        lvl -= 2.2                                  # una biga a contrallum
                    if tt:                                          # el foc respira i les flames pugen
                        q = y * 0.45 + math.sin(x * 0.35) * 0.9
                        lvl += 0.28 * (math.sin(ph * 3 + q) - math.sin(q)) + 0.25 * depth * (math.sin(ph * 5 + y * 0.6) - math.sin(y * 0.6))
                    cv.put(x, y, FIRE, lvl, 0)
            elif d_in <= r + 3 and y >= y0 - 3:
                cv.put(x, y, STONE, 3.6 + (0.8 if x > cxp else 0))
    # carrils que surten del portal fins al moll
    for rx in (346, 368):
        cv.vline(rx, QY - 5, QY - 1, IRON, 4.4)
    cv.rect(B_X0, QY - 6, x0 - 5, QY - 1, STONE, 2.2)
    cv.rect(x1 + 5, QY - 6, B_X1, QY - 1, STONE, 2.2)
    # rètol de la porta
    cv.rect(330, 120, 384, 127, IRON, 1.2)
    for x, y in text_px('FERRO-9', 330 + (55 - 27) // 2, 121):
        cv.put(x, y, GOLD, 4.6)

    # baixants de coure entre les naus
    for x in (257, 258):
        cv.vline(x, A_TOP, QY - 1, COPPER, 1.6 if x == 257 else 2.6)
    cv.rect(256, A_TOP, 260, A_TOP + 2, COPPER, 3.2)


def quay(cv, t=0.0):
    """El moll: un mur de carreus, noràis, un fanal i una gavarra de carbó amarrada. Amb `t`, el gas del fanal
    tremola."""
    ph = 2 * math.pi * t
    gas = 0.3 * (math.sin(ph * 5 + 0.7) - math.sin(0.7)) + 0.2 * math.sin(ph * 11) if t else 0.0
    for y in range(QY, QY + 9):
        for x in range(W):
            row = (y - QY) // 4
            joint = (y - QY) % 4 == 3 or (x + row * 7) % 14 == 13
            lvl = 2.6 - (y - QY) * 0.15 + (hr((x + row * 7) // 14, row, 7) - 0.5) * 0.5
            cv.put(x, y, STONE, lvl - (1.2 if joint else 0))
    cv.hline(0, W - 1, QY, STONE, 4.4)
    for bx in (60, 168, 292, 420):                                  # noràis
        cv.rect(bx, QY - 5, bx + 3, QY - 1, IRON, lambda x, y, b=bx: 2.0 + (x - b) * 0.6)
        cv.rect(bx - 1, QY - 6, bx + 4, QY - 6, IRON, 3.6)
    # fanal de gas
    lx = 236
    cv.vline(lx, 152, QY - 1, IRON, 1.6)
    cv.vline(lx + 1, 152, QY - 1, IRON, 2.6)
    cv.rect(lx - 2, QY - 4, lx + 3, QY - 1, IRON, 2.0)
    cv.poly([(lx - 3, 152), (lx + 4, 152), (lx + 3, 144), (lx - 2, 144)], GLASS, 5.4 + gas, 0)
    cv.hline(lx - 3, lx + 4, 143, IRON, 2.0)
    cv.put(lx, 142, IRON, 2.0)
    cv.glow(lx + 0.5, 148, 30, (255, 200, 110), 0.5)
    cv.glow(lx + 0.5, 148, 9, (255, 240, 190), 0.8 + gas * 0.3)


def barge(cv):
    """Gavarra de ferro carregada de mineral, amarrada davant de la nau gran."""
    x0, x1, yt = 70, 196, QY + 7
    hh = 10
    for y in range(yt, yt + hh):
        t = (y - yt) / (hh - 1)
        a, b = x0 + t * 3, x1 - t * 10
        for x in range(math.floor(a), math.ceil(b) + 1):
            if y == yt:
                lvl = 3.5                                           # regala
            elif y == yt + 1:
                lvl = 1.5
            else:
                lvl = 2.5 - t * 1.6 + (0.5 if (x - x0) % 16 in (0, 1) else 0)      # planxes reblades
            cv.put(x, y, RUST, lvl)
    # mineral apilat
    for x in range(x0 + 4, x1 - 6):
        hgt = 6 + math.sin((x - x0) / 11) * 3 + math.sin((x - x0) / 4.3) * 1.2
        for y in range(int(yt - hgt), yt):
            lvl = 1.5 + (yt - y) / hgt * 1.0 + (1.0 if y == int(yt - hgt) else 0)
            if hr(x, y, 3) > 0.9:
                lvl += 1.5                                          # un brill de lluna
            cv.put(x, y, IRON, lvl)
    # corda d'amarratge fins al norai
    for i in range(16):
        t = i / 15
        cv.put(60 + 2 + (x0 + 3 - 62) * t, QY - 4 + (yt - QY + 4) * t + math.sin(t * math.pi) * 2, WALNUT, 3.5)
    # el reflex fosc de la gavarra
    cv.darken(x0, yt + hh, x1 - 10, yt + hh + 6, lambda x, y: 0.9 - (y - yt - hh) * 0.13)


def canal(cv, t=0.0):
    """L'aigua: el reflex de tot el que hi ha a dalt, trencat per les ones, i la columna de la lluna.
    Amb `t` (0..1, bucle d'animació), les ones s'acosten i els reflexos tremolen."""
    ph = 2 * math.pi * t
    src = cv.img.copy()
    S = src.load()
    WY = QY + 9                                                     # línia de l'aigua
    for y in range(WY, H):
        depth = y - WY
        for x in range(W):
            wob = math.sin(y * 0.9 + math.sin(x * 0.07 + ph) * 1.5 - ph * 2) * (1 + depth * 0.05)
            sy = WY - 1 - int(depth * 1.15)
            sx = int(x + wob)
            base = 1.4 + depth / 90
            lvl = base + (0.6 if hr(x // 9, y, 4) > 0.8 else 0)
            cv.put(x, y, WATER, lvl, 0)
            if 0 <= sy < H and 0 <= sx < W and sy > 0:
                # bandes d'ona: el reflex surt a franges
                ripple = math.sin(y * 1.7 + math.sin(x / 13 + y - ph) * 2 - ph * 3) > -0.2 - depth / 120
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
        spread = 4 + (y - WY) * 0.18
        for x in range(int(mx - spread * 2), int(mx + spread * 2) + 1):
            d = abs(x - mx + math.sin(y * 1.3 - ph * 2) * 2) / spread
            if d < 1 and math.sin(y * 2.1 + x * 0.3 - ph * 3) > 0.1 + d * 0.6:
                cv.flat(x, y, mix(cv.get(x, y), (210, 214, 240), 0.7 - d * 0.4))
    # vora fosca sota el mur
    cv.darken(0, WY, W - 1, WY + 2, 0.8)


def railing(cv):
    """La barana de ferro de l'altra riba, des d'on mirem: a contrallum, a baix de tot."""
    for y in range(256, H):
        for x in range(W):
            cv.put(x, y, SIL, 1.5 + (1.0 if y == 256 else 0) - (y - 256) * 0.08, 0)
    for x in range(0, W):
        cv.put(x, 238, SIL, 1.5 + (0.6 if hr(x // 40) > 0.5 else 0.0), 0)
        cv.put(x, 239, SIL, 0.5, 0)
        cv.put(x, 250, SIL, 0.5, 0)
    for x in range(4, W, 9):
        cv.vline(x, 240, 255, SIL, 0.5, 0)
        if (x // 9) % 2:
            cv.put(x, 245, SIL, 0.5, 0); cv.put(x - 1, 246, SIL, 0.5, 0); cv.put(x + 1, 246, SIL, 0.5, 0)
    for x in range(0, W, 72):                                          # pilars
        cv.rect(x + 30, 232, x + 36, 256, SIL, lambda a, b: 0.5 + (0.6 if a == x + 36 else 0), 0)
        cv.rect(x + 29, 230, x + 37, 232, SIL, 1.5, 0)
    # el reflex de la lluna i dels forns a la barana
    cv.hline(0, W - 1, 237, SIL, 2.5, 0)


def bg(cv, retol=True, t=0.0):
    """`t` (0..1): moment del bucle de l'animació de fons (amb 0, el fons quiet)."""
    sky(cv)
    city(cv)
    factory(cv, retol, t=t)
    smoke(cv, [(46, 36, 190), (219, 48, 170), (434, 30, 90)], t=t)
    quay(cv, t=t)
    canal(cv, t=t)
    barge(cv)
    railing(cv)
    vinyeta(cv, 0.6)


PROPS = {}

ANIMS = {'ambient': {'frames': lambda: ambient_frames(bg, LIGHT), 'frameDuration': 130}}
