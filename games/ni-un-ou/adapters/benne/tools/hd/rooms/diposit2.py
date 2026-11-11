"""
El dipòsit d'aigua 2 de l'Arenga (Escena 7), fora de servei des de fa anys. Art definitiu:
  - l'interior d'un dipòsit d'acer pintat de blanc epoxi, ara esquerdat i rovellat, amb la marca de l'aigua
    antiga a les parets, reforços verticals i una mica d'aigua al fons; fosc i ressonant;
  - l'única llum baixa pel registre del sostre (obert, des del rebost): un feix càlid amb pols;
  - l'escala de mà que baixa del registre;
  - la carcassa del filtre (un cilindre amb la tapa cargolada, entre dos tubs);
  - el cartell de 1984: «AIGUA NO POTABLE», amb una gota que somriu.
Animacions: `gota` (cau del sostre al bassal), `bassal` (el reflex del registre tremola a l'aigua) i `pols`
(motes que suren dins el feix de llum).
"""
import math

from hd.pix import Canvas, Light, W, H, hr, mix, B4, RUST
from hd.rooms.arenga import (CAB, REDP, YELL, DARK, WHITEP, BRASS, WARM, FLOOR_Y, box, rrect, bolt, hpipe, vpipe,
                             glow)
from hd.rooms.sota import vladder, rust_streaks
from hd.rooms.comu import _diff, text, text_width

HATCH = (222, 18)                       # el centre del registre, al sostre
_PH = {'t': 0.0}                        # fase de l'aigua del bassal (animació `bassal`)
EPOXY = [(10, 12, 14), (20, 24, 26), (34, 38, 40), (52, 58, 58), (74, 80, 78), (100, 106, 102), (130, 134, 128),
         (164, 166, 158), (198, 198, 188)]
BOTTOMR = [(6, 7, 8), (12, 14, 15), (20, 23, 24), (30, 34, 34), (42, 47, 46), (58, 63, 60), (78, 82, 78)]
STAIN = (96, 70, 40)
WATER = [(4, 10, 12), (8, 18, 22), (14, 30, 34), (24, 46, 50), (40, 68, 70), (80, 110, 108)]
STEELF = [(14, 16, 20), (28, 32, 38), (44, 50, 58), (64, 72, 80), (90, 98, 106), (122, 130, 136), (160, 166, 170),
          (206, 210, 212)]
ENAMEL = [(70, 70, 64), (140, 138, 128), (200, 198, 184), (232, 230, 216), (248, 246, 236)]
DROPB = [(14, 40, 90), (30, 80, 160), (70, 140, 220), (150, 200, 250), (220, 240, 255)]

LIGHT = Light(ambient=-1.1, vignette=(110, 20), floor_fade=(184, 30))
LIGHT.point(HATCH[0], HATCH[1] + 30, r=150, k=2.9, squash=0.8, power=1.4)
LIGHT.point(HATCH[0], FLOOR_Y + 14, r=110, k=1.6, squash=2.4, power=1.6)          # la taca de llum a terra


def _beam(x, y):
    """El feix de llum que baixa del registre: un con que s'eixampla cap a terra."""
    t = (y - 24) / (FLOOR_Y + 20 - 24)
    if t < 0 or t > 1.1:
        return 0.0
    half = 20 + t * 46
    d = abs(x - HATCH[0]) / half
    return max(0.0, 1 - d) ** 1.4 * (1 - t * 0.4)


# ─── Parets, sostre i fons ────────────────────────────────────────────────

def walls(cv):
    for y in range(24, FLOOR_Y):
        for x in range(W):
            v = 3.2 + (hr(x // 4, y // 6, 31) - 0.5) * 0.4
            cv.put(x, y, EPOXY, v)
    # reforços verticals (perfils en T), amb ombra a la dreta
    for fx in range(18, W, 74):
        for x in range(fx, fx + 7):
            d = x - fx
            for y in range(24, FLOOR_Y):
                cv.put(x, y, EPOXY, 3.6 + (1.0 if d == 0 else 0.5 if d < 3 else -0.4 if d >= 5 else 0))
        cv.darken(fx + 7, 24, fx + 11, FLOOR_Y, lambda xx, yy, fx=fx: 0.6 - (xx - fx - 7) * 0.15)
    # soldadures horitzontals
    for sy in (70, 116):
        for x in range(W):
            cv.put(x, sy, EPOXY, 1.8)
            cv.put(x, sy + 1, EPOXY, 4.0 if hr(x // 2, sy) > 0.3 else 3.4)
    # la marca de l'aigua antiga: tot el que hi ha a sota és més brut i marronós
    tide = 62
    for y in range(tide, FLOOR_Y):
        for x in range(W):
            k = 0.16 + 0.14 * (y - tide) / (FLOOR_Y - tide)
            if hr(x // 3, y // 4, 77) > 0.85:
                k += 0.12
            cv.flat(x, y, mix(cv.get(x, y), STAIN, k))
    for x in range(W):
        wob = round(math.sin(x * 0.07) * 1.2)
        cv.flat(x, tide + wob, mix(cv.get(x, tide + wob), (70, 52, 30), 0.55))
        cv.flat(x, tide + wob + 1, mix(cv.get(x, tide + wob + 1), (70, 52, 30), 0.3))
    # l'epoxi esquerdat i saltat (taques de planxa rovellada)
    for i in range(22):
        cx = int(hr(i, 1, 5) * W)
        cy = 34 + int(hr(i, 2, 5) * (FLOOR_Y - 44))
        rx, ry = 1.5 + hr(i, 3) * 4, 1 + hr(i, 4) * 2
        for y in range(int(cy - ry), int(cy + ry) + 1):
            for x in range(int(cx - rx), int(cx + rx) + 1):
                e = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
                if e <= 1 and hr(x, y, i) > 0.35:
                    cv.flat(x, y, mix(cv.get(x, y), RUST[2 if e > 0.5 else 3], 0.55))
    rust_streaks(cv, 0, 30, W - 1, FLOOR_Y - 2, 60, k=0.45, seed=4)


def ceiling(cv):
    """El sostre del dipòsit (la coberta del rebost), vist de sota: planxa i bigues, amb el registre obert."""
    for y in range(0, 24):
        for x in range(W):
            cv.put(x, y, EPOXY, 1.6 + y * 0.05 + (hr(x // 5, y // 3, 9) - 0.5) * 0.3)
    for bx in range(18, W, 74):
        box(cv, bx - 1, 0, bx + 7, 25, EPOXY, 2.6, grad=0.4)
    cv.hline(0, W - 1, 24, EPOXY, 1.0)
    cv.hline(0, W - 1, 25, EPOXY, 0.6)
    # el registre obert: la boca (llum del rebost), la brida amb cargols i la tapa, oberta enlaire
    hx, hy = HATCH
    cv.disc(hx, hy - 4, 26, 9, EPOXY, 1.2)                              # brida
    for a in range(0, 360, 30):
        bolt(cv, hx + round(math.cos(math.radians(a)) * 24), hy - 4 + round(math.sin(math.radians(a)) * 8), EPOXY, 3.8)
    for y in range(int(hy - 13), int(hy + 5)):
        for x in range(hx - 24, hx + 25):
            nx, ny = (x - hx) / 21, (y - (hy - 4)) / 7
            if nx * nx + ny * ny <= 1:
                cv.flat(x, y, mix((255, 226, 160), (255, 246, 220), max(0.0, 1 - abs(nx))))
    cv.rect(hx - 14, 0, hx + 10, 4, [(120, 100, 70), (180, 156, 110)], 1.2, lit=0)  # el rebost, a dalt
    # la tapa, oberta (es veu de cantó, a la dreta del forat)
    cv.poly([(hx + 20, hy - 8), (hx + 34, hy - 18), (hx + 36, hy - 15), (hx + 22, hy - 4)], [(14, 22, 40), (24, 40, 70),
            (40, 64, 100), (62, 92, 130)], 2.0)


def floor(cv):
    """El fons del dipòsit: planxa amb cordons de soldadura, molla i un bassal d'aigua estancada."""
    mask = [[False] * W for _ in range(H)]
    vp = (240, 30)
    for y in range(FLOOR_Y, H):
        d = y - vp[1]
        for x in range(W):
            u = vp[0] + (x - vp[0]) * 150 / d
            u2 = vp[0] + (x + 1 - vp[0]) * 150 / d
            lv = 2.4 + (hr(x // 4, y // 2, 12) - 0.5) * 0.4
            if int(u // 90) != int(u2 // 90):
                lv = 1.0
            elif y in (166, 186):
                lv = 3.6
            cv.put(x, y, BOTTOMR, lv)
            mask[y][x] = True
    # el bassal: una el·lipse d'aigua fosca amb la llum del registre reflectida
    pcx, pcy, prx, pry = 238, 180, 92, 11
    src = cv.img.copy().load()
    for y in range(pcy - pry - 2, pcy + pry + 3):
        for x in range(pcx - prx - 4, pcx + prx + 5):
            e = ((x - pcx) / (prx + hr(y, 1) * 6)) ** 2 + ((y - pcy) / pry) ** 2
            if e <= 1:
                c = mix(src[x, y][:3], WATER[2], 0.7)
                rx_ = 9 - abs(y - pcy) * 0.5
                if abs(x - HATCH[0] - round(math.sin(y * 1.3 + _PH['t']) * 1.4)) < rx_ and (y % 2 == 0 or abs(x - HATCH[0]) < 3):
                    c = mix(c, WARM, 0.45 * (1 - abs(x - HATCH[0]) / max(rx_, 1)))   # el registre, reflectit
                if math.sin(x * 0.3 + y * 2.1 - _PH['t']) > 0.94:
                    c = mix(c, (120, 150, 140), 0.25)
                cv.flat(x, y, c)
    return mask


def beam(cv):
    """El feix de llum amb pols, per damunt de tot."""
    for y in range(24, FLOOR_Y + 24):
        for x in range(HATCH[0] - 80, HATCH[0] + 81):
            b = _beam(x, y)
            if b > 0.02:
                k = 0.26 * b
                if hr(x, y, 55) > 0.996:
                    k = 0.6                                                # pols suspesa
                cv.flat(x, y, mix(cv.get(x, y), (255, 228, 170), k))


# ─── El cartell, el filtre ─────────────────────────────────────────────────

def sign(cv):
    """Cartell esmaltat de 1984: «AIGUA NO POTABLE» i una gota que somriu."""
    x0, y0, x1, y1 = 60, 74, 146, 104
    rrect(cv, x0, y0, x1, y1, 3, ENAMEL, lambda x, y: 3.4 - (y - y0) * 0.01)
    rrect(cv, x0 + 2, y0 + 2, x1 - 2, y1 - 2, 2, [(40, 10, 10), (110, 24, 22), (170, 40, 34), (210, 70, 56)], 2.6)
    rrect(cv, x0 + 4, y0 + 4, x1 - 4, y1 - 4, 2, ENAMEL, 3.6)
    # la gota que somriu, a l'esquerra
    gx, gy = 78, 92
    cv.disc(gx, gy, 7, 7, DROPB, lambda nx, ny: 3.2 - nx * 0.8 - ny * 0.8)
    cv.poly([(gx - 5, gy - 5), (gx, gy - 14), (gx + 5, gy - 5)], DROPB, 3.2)
    cv.put(gx - 3, gy - 4, DROPB, 4.8)
    cv.put(gx - 2, gy - 5, DROPB, 4.8)
    cv.flat(gx - 3, gy - 1, (10, 16, 30))
    cv.flat(gx + 2, gy - 1, (10, 16, 30))
    for i, dx in enumerate((-3, -2, -1, 0, 1, 2)):
        cv.flat(gx + dx, gy + 3 + (1 if -2 <= dx <= 1 else 0), (10, 16, 30))
    # el text, en dues línies
    for s, y in (('AIGUA', 82), ('NO POTABLE', 92)):
        text(cv, s, 90 + (52 - text_width(s)) // 2, y, None, 0, flat=(150, 30, 28))
    # esmalt saltat i un cargol rovellat a cada cantó
    for (bx, by) in ((x0 + 2, y0 + 2), (x1 - 3, y0 + 2), (x0 + 2, y1 - 3), (x1 - 3, y1 - 3)):
        cv.put(bx, by, RUST, 3.0)
        cv.put(bx + 1, by + 1, RUST, 1.4)
    for i in range(8):
        cx, cy = x0 + int(hr(i, 61) * (x1 - x0)), y0 + int(hr(i, 62) * (y1 - y0))
        cv.put(cx, cy, DARK, 2.0)
        cv.put(cx + 1, cy, RUST, 2.4)
    for x in range(x0 + 6, x1 - 6):                                   # una regalimada de rovell
        if hr(x, 71) > 0.9:
            for y in range(y1 + 1, y1 + 4 + int(hr(x, 72) * 8)):
                cv.flat(x, y, mix(cv.get(x, y), RUST[3], 0.5))


def filter_housing(cv):
    """La carcassa del filtre: un cilindre d'acer amb la tapa de cargols, entre els dos tubs, sobre un peu."""
    cx, x0, x1 = 334, 316, 352
    # els tubs, que entren i surten per la paret
    hpipe(cv, 260, x0, 112, 3, STEELF, 3.0, bands=(274, 300), band_ramp=WHITEP)
    vpipe(cv, 262, 24, 112, 3, STEELF, 2.8)
    cv.disc(262, 112, 3, 3, STEELF, 3.2)
    hpipe(cv, x1, 420, 132, 3, STEELF, 3.0, bands=(380,), band_ramp=WHITEP)
    vpipe(cv, 420, 132, FLOOR_Y + 4, 3, STEELF, 2.8)
    cv.disc(420, 132, 3, 3, STEELF, 3.2)
    # el peu
    box(cv, 322, 140, 346, FLOOR_Y + 6, STEELF, 2.4)
    box(cv, 316, FLOOR_Y + 3, 352, FLOOR_Y + 7, STEELF, 2.0)
    # el cos (cilindre)
    for y in range(100, 142):
        for x in range(x0, x1 + 1):
            u = (x - cx) / ((x1 - x0) / 2 + 0.5)
            cv.put(x, y, STEELF, 3.6 + 1.6 * (-0.3 - u) - 0.9 * u * u)
    cv.disc(cx, 141, (x1 - x0) / 2, 3, STEELF, lambda nx, ny: 2.4 - nx)
    # la tapa (brida amb cargols), una mica desplaçada: algú l'ha oberta i tancada
    cv.disc(cx + 1, 98, (x1 - x0) / 2 + 3, 5, STEELF, lambda nx, ny: 4.4 - nx * 1.2 - ny * 1.4)
    cv.disc(cx + 1, 97, (x1 - x0) / 2 - 2, 3, STEELF, lambda nx, ny: 3.4 - nx - ny)
    for a in range(0, 360, 40):
        bolt(cv, cx + 1 + round(math.cos(math.radians(a)) * 19), 98 + round(math.sin(math.radians(a)) * 4), STEELF, 4.4)
    box(cv, cx - 3, 89, cx + 5, 93, STEELF, 4.6)                         # la maneta de la tapa
    # placa i manòmetre
    box(cv, cx - 10, 114, cx + 10, 122, BRASS, 3.0)
    for x in range(cx - 8, cx + 9, 2):
        cv.put(x, 118, BRASS, 1.4)
    cv.disc(x1 + 8, 118, 4, 4, STEELF, 2.0)
    cv.disc(x1 + 8, 118, 3, 3, WHITEP, 4.4)
    cv.line(x1 + 8, 118, x1 + 6, 120, DARK, 0)
    vpipe(cv, x1 + 8, 122, 130, 1, STEELF, 3.0)
    # rovell que regalima de la tapa
    rust_streaks(cv, x0 + 2, 100, x1 - 2, 140, 10, k=0.5, seed=8)


def ladder(cv):
    """L'escala de mà que baixa del registre fins al fons."""
    vladder(cv, HATCH[0] - 9, HATCH[0] + 9, 14, FLOOR_Y + 8, ramp=STEELF, lvl=3.4, step=10)
    cv.darken(HATCH[0] - 10, FLOOR_Y + 8, HATCH[0] + 12, FLOOR_Y + 12, 0.5)


# ─── Muntatge ─────────────────────────────────────────────────────────────

def _base(cv):
    walls(cv)
    ceiling(cv)
    sign(cv)
    floor(cv)
    filter_housing(cv)
    ladder(cv)
    beam(cv)
    glow(cv, HATCH[0], HATCH[1] - 4, 40, WARM, 0.45)


def bg(cv):
    _base(cv)


def _frames_gota():
    """Una gota que es forma al sostre, cau al bassal i hi fa una rodoneta."""
    base = Canvas(light=LIGHT)
    _base(base)
    gx, top, pool = 286, 26, 180
    seq = [('f', 0), ('f', 1), ('f', 2)] + [('c', y) for y in range(top + 6, pool, 22)] + [('r', 2), ('r', 4), ('r', 6),
                                                                                            ] + [('n', 0)] * 30
    frames = []
    for kind, v in seq:
        cv = Canvas(light=LIGHT, img=base.img.copy())
        if kind == 'f':                                     # es forma
            for k in range(v + 1):
                cv.flat(gx, top + k, (150, 180, 180))
        elif kind == 'c':                                   # cau
            cv.flat(gx, v, (190, 210, 210))
            cv.flat(gx, v + 1, (130, 160, 160))
        elif kind == 'r':                                   # rodoneta
            for a in range(0, 360, 20):
                x = gx + round(math.cos(math.radians(a)) * v * 1.6)
                y = pool + round(math.sin(math.radians(a)) * v * 0.4)
                cv.flat(x, y, mix(cv.get(x, y), (160, 190, 180), 0.5 - v * 0.05))
        frames.append(_diff(cv.img, base.img))
    return frames


def _frames_bassal():
    """L'aigua del bassal: el reflex del registre ondula i les ratlles de llum corren (bucle de 12)."""
    base = Canvas(light=LIGHT)
    _base(base)
    frames = []
    try:
        for i in range(12):
            _PH['t'] = 2 * math.pi * i / 12
            cv = Canvas(light=LIGHT)
            _base(cv)
            frames.append(_diff(cv.img, base.img))
    finally:
        _PH['t'] = 0.0
    return frames


def _frames_pols():
    """Motes de pols que suren lentament dins el feix del registre i fan pampallugues."""
    base = Canvas(light=LIGHT)
    _base(base)
    n, motes = 48, []
    for k in range(30):
        y = 34 + hr(k, 1, 88) * (FLOOR_Y - 30)
        t = (y - 24) / (FLOOR_Y + 20 - 24)
        x = HATCH[0] + (hr(k, 2, 88) - 0.5) * (30 + t * 70)
        motes.append((x, y, 2 + hr(k, 3, 88) * 5, 3 + hr(k, 4, 88) * 6, hr(k, 5, 88) * 6.283, 1 + int(hr(k, 6, 88) * 2)))
    frames = []
    for i in range(n):
        cv = Canvas(light=LIGHT, img=base.img.copy())
        a = 2 * math.pi * i / n
        for k, (x0, y0, ax, ay, ph, sp) in enumerate(motes):
            x = round(x0 + math.sin(a * sp + ph) * ax)
            y = round(y0 + math.sin(a + ph * 1.7) * ay)
            b = _beam(x, y)
            tw = 0.5 + 0.5 * math.sin(a * 3 + ph * 2)
            if b > 0.15 and tw > 0.25:
                cv.flat(x, y, mix(cv.get(x, y), (255, 236, 190), min(0.75, 0.35 + b * 0.5 * tw)))
        frames.append(_diff(cv.img, base.img))
    return frames


ANIMS = {'gota': {'frames': _frames_gota, 'frameDuration': 90},
         'bassal': {'frames': _frames_bassal, 'frameDuration': 200},
         'pols': {'frames': _frames_pols, 'frameDuration': 130}}

PROPS = {}


GEOMETRIA = {
    'things': {
        'registre': {'rect': (196, 0, 248, 158), 'walk': (222, 174)},
        'filtre': {'rect': (310, 86, 364, 160), 'walk': (336, 178)},
        'cartell': {'rect': (58, 72, 148, 106), 'walk': (104, 176)},
    },
    'spawns': {'iri': (196, 186), 'vet': (256, 188)},
    'walkable': [(10, 170), (470, 170), (476, 196), (4, 196)],
}
