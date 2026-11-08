"""
Dissenys provisionals de les sales de Ferro-9: el dibuix del fons en pixel art i, alhora, la
geometria per a Benne (on és cada cosa, on es camina, on hi ha cada personatge), perquè el que
es veu i el que es pot clicar coincideixin.

Cada disseny:
  era       'iri' (passat, fàbrica) o 'vet' (present, presó orbital)
  things    id → {'rect': (x0, y0, x1, y1), 'walk': (x, y)}  (hotspots, props i sortides)
  spawns    personatge → (x, y)  (peus)
  walkable  polígon del terra
  bg(c)     dibuixa el fons
  props     id → funció que dibuixa el prop condicional (fotograma a part)

Coordenades de disseny 352×198 (escala.py les porta a la resolució del joc); per sota de y≈150
hi ha la barra de verbs.
"""
import math
import random

import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from escala import DESIGN_W, DESIGN_H, box, pt  # noqa: E402

W, H = DESIGN_W, DESIGN_H
K = 1.0  # escala de disseny → píxels reals; la fixa draw_placeholders.py segons la mida de la sala


# ─── Eines de dibuix ────────────────────────────────────────────────────────

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


class ScaledDraw:
    """ImageDraw amb coordenades de disseny: les converteix a píxels reals abans de dibuixar."""

    def __init__(self, img, k):
        self.d, self.k = ImageDraw.Draw(img), k

    def _box(self, b):
        x0, y0, x1, y1 = b
        return list(box(x0, y0, x1, y1, self.k))

    def _pts(self, pts):
        return [pt(x, y, self.k) for x, y in pts]

    def _w(self, width):
        return max(1, round(width * self.k))

    def rectangle(self, b, fill=None, outline=None, width=1):
        self.d.rectangle(self._box(b), fill=fill, outline=outline, width=self._w(width))

    def ellipse(self, b, fill=None, outline=None, width=1):
        self.d.ellipse(self._box(b), fill=fill, outline=outline, width=self._w(width))

    def polygon(self, pts, fill=None, outline=None):
        self.d.polygon(self._pts(pts), fill=fill, outline=outline)

    def line(self, pts, fill=None, width=1):
        self.d.line(self._pts(pts), fill=fill, width=self._w(width))

    def arc(self, b, start, end, fill=None, width=1):
        self.d.arc(self._box(b), start, end, fill=fill, width=self._w(width))


class C:
    """Llenç amb utilitats de pixel art. Les coordenades són de disseny (352×198); `k` és l'escala
    fins als píxels reals de la imatge (vegeu escala.py)."""

    def __init__(self, img, k=None):
        self.img = img
        self.k = K if k is None else k
        self.d = ScaledDraw(img, self.k)

    def rect(self, x0, y0, x1, y1, col):
        self.d.rectangle([x0, y0, x1, y1], fill=col)

    def line(self, pts, col, w=1):
        self.d.line(pts, fill=col, width=w)

    def px(self, x, y, col):
        self.d.rectangle([int(x), int(y), int(x), int(y)], fill=col)

    def vgrad(self, x0, y0, x1, y1, c1, c2):
        X0, Y0, X1, Y1 = box(x0, y0, x1, y1, self.k)
        dr = ImageDraw.Draw(self.img)
        for y in range(Y0, Y1 + 1):
            t = (y - Y0) / max(1, Y1 - Y0)
            dr.line([(X0, y), (X1, y)], fill=lerp(c1, c2, t))

    def hgrad(self, x0, y0, x1, y1, stops):
        """Gradient horitzontal per tons (cilindres): stops = [(t, color), ...]."""
        X0, Y0, X1, Y1 = box(x0, y0, x1, y1, self.k)
        dr = ImageDraw.Draw(self.img)
        for x in range(X0, X1 + 1):
            t = (x - X0) / max(1, X1 - X0)
            for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
                if t0 <= t <= t1:
                    dr.line([(x, Y0), (x, Y1)], fill=lerp(c0, c1, (t - t0) / max(1e-6, t1 - t0)))
                    break

    def ellipse(self, x0, y0, x1, y1, col, outline=None):
        self.d.ellipse([x0, y0, x1, y1], fill=col, outline=outline)

    def glow(self, cx, cy, r, col, strength=0.5):
        layer = Image.new('RGBA', self.img.size, (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        (X, Y), R = pt(cx, cy, self.k), round(r * self.k)
        for i in range(R, 0, -2):
            a = int(255 * strength * (1 - i / R) ** 1.6)
            ld.ellipse([X - i, Y - i, X + i, Y + i], fill=col + (max(0, min(255, a)) // 3,))
        self.img.alpha_composite(layer)

    def shade(self, x0, y0, x1, y1, col, alpha):
        layer = Image.new('RGBA', self.img.size, (0, 0, 0, 0))
        ImageDraw.Draw(layer).rectangle(list(box(x0, y0, x1, y1, self.k)), fill=col + (alpha,))
        self.img.alpha_composite(layer)


def bricks(c, x0, y0, x1, y1, base, mortar, seed=1):
    rnd = random.Random(seed)
    c.rect(x0, y0, x1, y1, mortar)
    bh, bw = 6, 14
    for row, y in enumerate(range(y0, y1, bh)):
        off = (row % 2) * (bw // 2)
        for x in range(x0 - off, x1, bw):
            v = rnd.randint(-14, 10)
            col = tuple(max(0, min(255, ch + v)) for ch in base)
            c.rect(max(x0, x + 1), y + 1, min(x1, x + bw - 1), min(y1, y + bh - 1), col)
            c.line([(max(x0, x + 1), y + 1), (min(x1, x + bw - 2), y + 1)], lerp(col, (255, 220, 180), 0.12))


def planks(c, y0, y1, base, seam, vx=176):
    """Terra de taulons en perspectiva."""
    c.vgrad(0, y0, W, y1, base, lerp(base, (0, 0, 0), 0.45))
    y, gap = y0, 3
    while y < y1:
        c.line([(0, y), (W, y)], seam)
        y += gap
        gap += 2
    for i in range(-12, 13):
        x_far = vx + i * 14
        x_near = vx + i * 48
        c.line([(x_far, y0), (x_near, y1)], lerp(seam, base, 0.4))


def grating(c, y0, y1, base, line, vx=176):
    """Terra de reixa metàl·lica en perspectiva."""
    c.vgrad(0, y0, W, y1, base, lerp(base, (0, 0, 0), 0.5))
    y, gap = y0, 2
    while y < y1:
        c.line([(0, y), (W, y)], line)
        y += gap
        gap += 1
    for i in range(-16, 17):
        c.line([(vx + i * 10, y0), (vx + i * 34, y1)], line)


def metal_panels(c, x0, y0, x1, y1, base, seam, rivet, pw=44, ph=36, seed=3):
    rnd = random.Random(seed)
    c.rect(x0, y0, x1, y1, seam)
    for y in range(y0, y1, ph):
        for x in range(x0, x1, pw):
            v = rnd.randint(-6, 6)
            col = tuple(max(0, min(255, ch + v)) for ch in base)
            c.vgrad(x + 1, y + 1, min(x1, x + pw - 1), min(y1, y + ph - 1), lerp(col, (255, 255, 255), 0.06), lerp(col, (0, 0, 0), 0.12))
            for rx, ry in ((x + 3, y + 3), (x + pw - 4, y + 3), (x + 3, y + ph - 4), (x + pw - 4, y + ph - 4)):
                if rx < x1 and ry < y1:
                    c.px(rx, ry, rivet)


def pipe_h(c, x0, x1, y, r, tones):
    dark, mid, light = tones
    c.rect(x0, y - r, x1, y + r, mid)
    c.line([(x0, y - r), (x1, y - r)], light)
    c.line([(x0, y + r), (x1, y + r)], dark)
    for fx in range(x0 + 20, x1, 46):  # brides
        c.rect(fx, y - r - 1, fx + 2, y + r + 1, dark)


def pipe_v(c, x, y0, y1, r, tones):
    dark, mid, light = tones
    c.rect(x - r, y0, x + r, y1, mid)
    c.line([(x - r, y0), (x - r, y1)], light)
    c.line([(x + r, y0), (x + r, y1)], dark)
    for fy in range(y0 + 16, y1, 40):
        c.rect(x - r - 1, fy, x + r + 1, fy + 2, dark)


def gauge(c, cx, cy, r, angle):
    c.ellipse(cx - r - 1, cy - r - 1, cx + r + 1, cy + r + 1, (60, 46, 30))
    c.ellipse(cx - r, cy - r, cx + r, cy + r, (236, 228, 204))
    c.line([(cx, cy), (cx + math.cos(angle) * (r - 1), cy + math.sin(angle) * (r - 1))], (170, 30, 30))


def vignette(c, strength=90):
    layer = Image.new('RGBA', c.img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    w, h, steps = c.img.width, c.img.height, round(24 * c.k)
    for i in range(steps):
        a = int(strength * (1 - i / steps) ** 2)
        ld.rectangle([i, i, w - 1 - i, h - 1 - i], outline=(0, 0, 0, a))
    c.img.alpha_composite(layer)


def outline_rect(c, x0, y0, x1, y1, col):
    c.d.rectangle([x0, y0, x1, y1], outline=col)


# Paletes
COPPER = ((120, 62, 34), (192, 108, 58), (238, 166, 102))
IRON = ((40, 38, 44), (74, 70, 78), (112, 108, 116))
STEEL = ((60, 72, 88), (104, 120, 138), (160, 178, 196))
WOOD = ((70, 46, 30), (112, 76, 48), (146, 104, 66))


# ─── Portes ─────────────────────────────────────────────────────────────────

def factory_door(c, x0, y0, x1, y1, iron=False, sign=False):
    frame = (52, 36, 26)
    c.rect(x0 - 2, y0 - 3, x1 + 2, y1, frame)
    if iron:
        c.hgrad(x0, y0, x1, y1, [(0, IRON[0]), (0.35, IRON[2]), (1, IRON[0])])
        for y in range(y0 + 6, y1, 14):
            for x in (x0 + 3, x1 - 3):
                c.px(x, y, (150, 146, 150))
        if sign:  # franges de perill
            for i, x in enumerate(range(x0, x1, 4)):
                c.rect(x, y0 + 8, x + 1, y0 + 12, (230, 180, 40) if i % 2 == 0 else (30, 30, 30))
    else:
        c.hgrad(x0, y0, x1, y1, [(0, WOOD[0]), (0.4, WOOD[2]), (1, WOOD[0])])
        for x in range(x0 + 6, x1, 7):
            c.line([(x, y0), (x, y1)], WOOD[0])
    c.ellipse(x1 - 7, (y0 + y1) // 2 - 2, x1 - 3, (y0 + y1) // 2 + 2, (210, 170, 80))


def cell_door(c, x0, y0, x1, y1, outside=False):
    c.rect(x0 - 3, y0 - 3, x1 + 3, y1, (26, 32, 42))
    c.hgrad(x0, y0, x1, y1, [(0, STEEL[0]), (0.3, STEEL[2]), (1, STEEL[0])])
    c.rect(x0 + 8, y0 + 10, x1 - 8, y0 + 26, (14, 18, 24))      # finestreta amb barrots
    for x in range(x0 + 11, x1 - 8, 5):
        c.line([(x, y0 + 10), (x, y0 + 26)], STEEL[1])
    lx = x1 - 10 if not outside else x0 + 4                        # pany magnètic M-3
    c.rect(lx, y0 + 40, lx + 7, y0 + 52, (40, 44, 54))
    c.rect(lx + 2, y0 + 43, lx + 5, y0 + 45, (90, 200, 255))
    c.glow(lx + 3, y0 + 44, 6, (90, 200, 255), 0.6)
    if outside:
        c.rect(x0 + 10, y0 - 3, x1 - 10, y0 + 5, (220, 220, 210))  # placa amb el 9
        nine = ['###', '#.#', '###', '..#', '###']
        nx = (x0 + x1) // 2 - 1
        for dy, row in enumerate(nine):
            for dx, ch in enumerate(row):
                if ch == '#':
                    c.px(nx + dx, y0 - 2 + dy, (40, 40, 40))


# ─── Fàbrica: sala de calderes ──────────────────────────────────────────────

def calderes_bg(c):
    bricks(c, 0, 0, W, 112, (128, 64, 42), (70, 40, 30), seed=11)
    c.vgrad(0, 0, W, 10, (40, 26, 20), (70, 40, 30))
    pipe_h(c, 0, W, 6, 3, COPPER)
    pipe_h(c, 0, 300, 16, 2, IRON)
    planks(c, 112, H, (96, 64, 42), (62, 40, 26))
    c.rect(0, 110, W, 113, (52, 34, 24))                           # sòcol

    # Caldera gran
    bx0, bx1 = 56, 128
    pipe_v(c, 92, 6, 26, 4, COPPER)
    c.ellipse(bx0, 18, bx1, 40, COPPER[1])
    c.hgrad(bx0, 30, bx1, 108, [(0, COPPER[0]), (0.3, COPPER[2]), (0.55, COPPER[1]), (1, COPPER[0])])
    c.ellipse(bx0, 100, bx1, 116, COPPER[0])
    for y in (40, 62, 84):                                          # anelles reblades
        c.rect(bx0, y, bx1, y + 2, COPPER[0])
        for x in range(bx0 + 3, bx1, 6):
            c.px(x, y + 1, COPPER[2])
    gauge(c, 92, 52, 7, -0.6)
    c.rect(78, 88, 106, 104, (40, 30, 26))                          # porta del foc
    c.rect(81, 91, 103, 101, (200, 80, 30))
    c.glow(92, 96, 26, (255, 120, 40), 0.9)
    for x in range(83, 102, 3):
        c.line([(x, 91), (x, 101)], (40, 30, 26))
    # Volant de vàlvula
    c.ellipse(124, 60, 140, 76, None, outline=(170, 40, 40))
    c.line([(132, 60), (132, 76)], (170, 40, 40))
    c.line([(124, 68), (140, 68)], (170, 40, 40))

    # Taula i llum del capatàs
    c.rect(214, 98, 244, 102, WOOD[2])
    c.rect(216, 103, 218, 128, WOOD[0])
    c.rect(240, 103, 242, 128, WOOD[0])
    c.rect(222, 92, 228, 97, (230, 230, 220))                       # tassa de cafè
    c.rect(229, 93, 230, 95, (230, 230, 220))
    c.line([(236, 97), (236, 84)], IRON[1])                         # flexo
    c.ellipse(230, 80, 242, 86, (60, 90, 60))
    c.glow(236, 92, 30, (255, 220, 140), 0.8)

    # Tauler d'anuncis
    c.rect(146, 24, 206, 64, (88, 58, 36))
    c.rect(149, 27, 203, 61, (186, 140, 88))
    rnd = random.Random(5)
    for x, y, w, h, col in ((152, 30, 14, 18, (240, 236, 220)), (169, 29, 16, 12, (244, 220, 120)),
                            (188, 31, 12, 16, (240, 236, 220)), (155, 50, 18, 9, (220, 120, 120)), (176, 44, 20, 14, (240, 236, 220))):
        c.rect(x, y, x + w, y + h, col)
        for ly in range(y + 3, y + h - 1, 3):
            c.line([(x + 2, ly), (x + w - 2 - rnd.randint(0, 4), ly)], (150, 140, 130))
        c.px(x + w // 2, y + 1, (200, 40, 40))
    for i in range(4):                                              # pila de formularis 27-B
        c.rect(196 - i, 50 - i, 202 - i, 58 - i, (232, 228, 214))

    # Llum d'alarma, damunt la porta de la cambra
    c.rect(326, 30, 330, 36, IRON[1])
    c.ellipse(321, 34, 335, 46, (200, 40, 40))
    c.ellipse(324, 36, 329, 40, (255, 140, 140))
    c.glow(328, 40, 34, (255, 60, 40), 0.7)

    factory_door(c, 8, 50, 40, 112)
    factory_door(c, 312, 50, 344, 112, iron=True, sign=True)
    factory_door(c, 154, 70, 200, 112)                              # porta del moll de càrrega
    c.rect(166, 64, 188, 68, (210, 200, 170))                        # rètol «MOLL»
    for x in (169, 174, 179, 184):
        c.rect(x, 65, x + 2, 67, (60, 46, 30))
    vignette(c)


def calderes_segell(c):
    """El segell, a terra, quan el capatàs el deixa caure."""
    c.rect(226, 134, 238, 137, (110, 74, 40))
    c.rect(229, 130, 235, 133, (180, 44, 44))
    c.ellipse(229, 127, 235, 131, (200, 60, 60))


CALDERES = {
    'era': 'iri',
    'things': {
        'porta_magatzem': {'rect': (6, 48, 42, 114), 'walk': (30, 134)},
        'porta_cambra': {'rect': (310, 48, 346, 114), 'walk': (320, 134)},
        'tauler': {'rect': (146, 24, 206, 64), 'walk': (176, 128)},
        'alarma': {'rect': (318, 28, 338, 48), 'walk': (316, 132)},
        'segell': {'rect': (222, 124, 242, 140), 'walk': (214, 140)},
        'porta_moll': {'rect': (152, 62, 202, 114), 'walk': (177, 132)},
    },
    'spawns': {'iri': (160, 138), 'capatas': (262, 132)},
    'walkable': [(14, 118), (338, 118), (346, 148), (6, 148)],
    'bg': calderes_bg,
    'props': {'segell': calderes_segell},
}


# ─── Fàbrica: magatzem d'eines ──────────────────────────────────────────────

def magatzem_bg(c):
    bricks(c, 0, 0, W, 112, (118, 62, 44), (66, 38, 30), seed=21)
    pipe_h(c, 0, W, 6, 3, IRON)
    planks(c, 112, H, (92, 62, 40), (58, 38, 26))
    c.rect(0, 110, W, 113, (52, 34, 24))

    # Prestatgeria gran
    x0, x1 = 112, 236
    c.rect(x0, 16, x1, 110, WOOD[0])
    for y in (16, 40, 64, 88, 108):
        c.rect(x0, y, x1, y + 3, WOOD[2])
    rnd = random.Random(7)
    for shelf_y in (40, 64, 88, 108):
        x = x0 + 4
        while x < x1 - 10:
            kind = rnd.choice(['box', 'wrench', 'coil', 'jar', 'box'])
            if kind == 'box':
                w, h = rnd.randint(10, 16), rnd.randint(8, 14)
                c.rect(x, shelf_y - h, x + w, shelf_y - 1, rnd.choice([(150, 110, 70), (120, 90, 60), (170, 130, 80)]))
                c.line([(x, shelf_y - h), (x + w, shelf_y - h)], (190, 150, 100))
            elif kind == 'wrench':
                w = 4
                c.rect(x + 1, shelf_y - 16, x + 2, shelf_y - 1, (150, 156, 170))
                c.rect(x, shelf_y - 18, x + 3, shelf_y - 15, (150, 156, 170))
            elif kind == 'coil':
                w = 10
                c.ellipse(x, shelf_y - 10, x + 10, shelf_y - 1, (90, 70, 140))
                c.ellipse(x + 3, shelf_y - 7, x + 7, shelf_y - 4, WOOD[0])
            else:
                w = 7
                c.rect(x, shelf_y - 11, x + 6, shelf_y - 1, (120, 170, 160))
                c.rect(x + 1, shelf_y - 13, x + 5, shelf_y - 11, (90, 70, 50))
            x += w + rnd.randint(3, 6)

    # Banc de treball
    c.rect(250, 80, 340, 86, WOOD[2])
    c.rect(252, 87, 256, 112, WOOD[0])
    c.rect(334, 87, 338, 112, WOOD[0])
    c.rect(262, 70, 280, 79, (120, 120, 130))                       # cargol de banc
    c.rect(300, 72, 320, 79, (150, 110, 70))
    c.line([(296, 40), (296, 60)], IRON[1])                          # llum penjant
    c.ellipse(288, 58, 304, 66, (60, 90, 60))
    c.glow(296, 72, 40, (255, 220, 140), 0.8)

    # Ganxo del plomall (el plomall és un prop)
    c.rect(86, 44, 96, 47, IRON[1])
    # Taulell d'eines a la paret
    c.rect(48, 30, 100, 40, (150, 120, 80))
    for x in range(52, 98, 8):
        c.rect(x, 33, x + 2, 38, (140, 146, 160))

    factory_door(c, 8, 50, 40, 112)
    vignette(c)


def magatzem_plomall(c):
    c.line([(91, 47), (91, 84)], (120, 80, 40), 2)
    for i in range(14):
        a = -1.2 + i * 0.18
        c.line([(91, 86), (91 + math.cos(a + 1.57) * 8, 86 + math.sin(a + 1.57) * 12)], (230, 200, 120))
    c.ellipse(85, 84, 97, 98, (220, 180, 90))


def magatzem_caixa(c):
    x0, y0, x1, y1 = 266, 118, 304, 136
    c.rect(x0, y0, x1, y1, (180, 40, 40))
    c.rect(x0, y0, x1, y0 + 4, (210, 70, 60))
    c.rect(x0 + 14, y0 - 5, x1 - 14, y0 - 3, (60, 60, 66))
    c.rect(x0 + 14, y0 - 5, x0 + 15, y0, (60, 60, 66))
    c.rect(x1 - 15, y0 - 5, x1 - 14, y0, (60, 60, 66))
    c.rect(x0 + 17, y0 + 7, x1 - 17, y0 + 9, (220, 200, 120))


MAGATZEM = {
    'era': 'iri',
    'things': {
        'porta_calderes': {'rect': (6, 48, 42, 114), 'walk': (30, 134)},
        'prestatges': {'rect': (112, 16, 236, 110), 'walk': (174, 126)},
        'plomall': {'rect': (82, 44, 100, 100), 'walk': (92, 128)},
        'caixa_eines': {'rect': (264, 112, 306, 138), 'walk': (256, 140)},
    },
    'spawns': {'iri': (70, 138), 'cargol': (210, 132)},
    'walkable': [(14, 118), (338, 118), (346, 148), (6, 148)],
    'bg': magatzem_bg,
    'props': {'plomall': magatzem_plomall, 'caixa_eines': magatzem_caixa},
}


# ─── Fàbrica: cambra de ressonància ─────────────────────────────────────────

def cambra_bg(c):
    metal_panels(c, 0, 0, W, 112, (70, 60, 56), (40, 34, 32), (120, 110, 100), seed=31)
    pipe_h(c, 0, W, 6, 3, COPPER)
    planks(c, 112, H, (80, 60, 46), (52, 38, 28))
    c.rect(0, 110, W, 113, (40, 30, 26))

    # Plataforma i cambra de vidre amb bobines de ferro-9
    c.rect(140, 104, 240, 118, IRON[0])
    c.rect(140, 104, 240, 106, IRON[2])
    c.rect(150, 10, 230, 16, IRON[1])
    c.glow(190, 60, 60, (150, 110, 255), 1.0)
    for x in (162, 176, 204, 218):
        c.hgrad(x - 3, 18, x + 3, 102, [(0, (40, 30, 70)), (0.4, (150, 120, 220)), (1, (40, 30, 70))])
    for y in range(26, 100, 12):
        c.rect(156, y, 224, y + 2, (90, 70, 150))
    c.shade(152, 16, 228, 104, (170, 210, 230), 50)                  # vidre
    c.line([(158, 20), (158, 98)], (220, 240, 255))
    c.line([(160, 20), (160, 60)], (220, 240, 255))
    c.d.rectangle([152, 16, 228, 104], outline=(200, 220, 230))

    # Cables cap a la consola
    for i, y in enumerate((96, 100, 104)):
        c.line([(130, y), (150, y - 4 + i)], (30, 30, 34), 2)

    # Consola
    c.rect(66, 70, 132, 112, IRON[1])
    c.rect(62, 66, 136, 72, IRON[2])
    for x, col in ((72, (90, 220, 120)), (80, (230, 200, 60)), (88, (90, 220, 120))):
        c.ellipse(x, 78, x + 4, 82, col)
    gauge(c, 112, 86, 6, -2.2)
    for x in range(72, 100, 4):
        c.rect(x, 96, x + 2, 104, (60, 60, 66))
    # Base de la palanca
    c.rect(114, 62, 124, 66, IRON[0])
    c.line([(119, 62), (124, 46)], (150, 150, 160), 2)                 # palanca (alçada)
    c.ellipse(121, 42, 128, 49, (40, 40, 44))

    # Rètols
    c.rect(268, 30, 320, 46, (230, 190, 50))
    for x in range(270, 318, 6):
        c.line([(x, 44), (x + 4, 32)], (40, 40, 40))
    factory_door(c, 8, 50, 40, 112, iron=True)
    pipe_v(c, 300, 10, 110, 3, COPPER)
    vignette(c)


def cambra_boto(c):
    c.rect(86, 70, 100, 74, (60, 60, 66))
    c.ellipse(88, 64, 98, 72, (220, 40, 40))
    c.ellipse(90, 65, 94, 68, (255, 150, 150))


CAMBRA = {
    'era': 'iri',
    'things': {
        'porta': {'rect': (6, 48, 42, 114), 'walk': (30, 134)},
        'palanca': {'rect': (112, 40, 132, 68), 'walk': (122, 126)},
        'cambra': {'rect': (148, 10, 232, 118), 'walk': (190, 128)},
        'boto': {'rect': (84, 62, 102, 76), 'walk': (94, 126)},
    },
    'spawns': {'iri': (276, 138)},
    'walkable': [(14, 120), (338, 120), (346, 148), (6, 148)],
    'bg': cambra_bg,
    'props': {'boto': cambra_boto},
}


# ─── La Gavina: cel·la 9 ────────────────────────────────────────────────────

def cella_bg(c):
    metal_panels(c, 0, 0, W, 112, (58, 70, 86), (30, 38, 50), (96, 112, 130), seed=41)
    c.rect(0, 0, W, 6, (26, 32, 42))
    c.rect(130, 2, 230, 6, (200, 240, 255))                          # llum de sostre
    c.glow(180, 6, 70, (170, 220, 255), 0.6)
    grating(c, 112, H, (40, 48, 60), (26, 30, 40))
    c.rect(0, 110, W, 113, (24, 30, 40))

    # Ull de bou amb la Terra (dibuixada a part i retallada en cercle)
    cx, cy, r = 247, 37, 19
    c.ellipse(cx - r - 4, cy - r - 4, cx + r + 4, cy + r + 4, (30, 36, 46))
    space = Image.new('RGBA', (round((2 * r + 1) * c.k),) * 2, (8, 10, 24, 255))
    sc = C(space, c.k)
    rnd = random.Random(4)
    for _ in range(22):
        sc.px(rnd.randint(0, 2 * r), rnd.randint(0, 2 * r), (230, 230, 255))
    sc.ellipse(r - 4, r + 2, r + 34, r + 40, (40, 100, 200))
    sc.ellipse(r + 2, r + 8, r + 14, r + 18, (70, 150, 80))
    sc.ellipse(r + 12, r + 4, r + 22, r + 9, (230, 240, 255))
    sc.glow(r + 14, r + 20, 22, (120, 180, 255), 0.5)
    mask = Image.new('L', space.size, 0)
    ImageDraw.Draw(mask).ellipse([0, 0, space.width - 1, space.height - 1], fill=255)
    c.img.paste(space, box(cx - r, cy - r, cx - r, cy - r, c.k)[:2], mask)
    c.d.ellipse([cx - r - 2, cy - r - 2, cx + r + 2, cy + r + 2], outline=(130, 150, 170))
    c.line([(cx - 8, cy - 12), (cx - 2, cy - 15)], (200, 220, 240))     # reflex del vidre

    # Altaveu de la MARE (cor)
    c.ellipse(118, 12, 130, 24, (240, 110, 170))
    c.ellipse(128, 12, 140, 24, (240, 110, 170))
    c.d.polygon([(118, 19), (140, 19), (129, 32)], fill=(240, 110, 170))
    for x in range(122, 138, 3):
        c.line([(x, 17), (x, 24)], (150, 50, 100))
    c.glow(129, 22, 18, (255, 120, 180), 0.5)

    # Panell rovellat
    c.rect(176, 58, 208, 92, (120, 74, 52))
    c.rect(178, 60, 206, 90, (150, 96, 64))
    rnd = random.Random(9)
    for _ in range(30):
        c.px(178 + rnd.randint(0, 28), 60 + rnd.randint(0, 30), rnd.choice([(110, 60, 40), (170, 110, 70), (90, 52, 36)]))
    for x, y in ((180, 62), (204, 62), (180, 88), (204, 88)):
        c.px(x, y, (60, 50, 50))
    for y in range(66, 84, 4):
        c.line([(184, y), (200, y)], (90, 56, 40))

    # Llitera de dos pisos
    lx0, lx1 = 272, 346
    for x in (lx0, lx1 - 3):
        c.rect(x, 50, x + 3, 126, STEEL[0])
    for y, mat in ((62, (150, 150, 160)), (100, (150, 150, 160))):
        c.rect(lx0, y, lx1, y + 3, STEEL[1])
        c.rect(lx0 + 4, y - 6, lx1 - 4, y - 1, mat)
        c.rect(lx1 - 18, y - 9, lx1 - 6, y - 5, (220, 220, 225))       # coixí
    c.rect(lx0 + 4, 96, lx0 + 20, 99, (200, 180, 120))                # fullet sota el coixí... a sota

    cell_door(c, 8, 38, 46, 112)
    vignette(c, 110)


def cella_avis(c):
    c.d.polygon([(56, 130), (72, 128), (74, 136), (58, 138)], fill=(236, 232, 220))
    c.line([(60, 132), (70, 131)], (160, 150, 150))
    c.line([(61, 134), (69, 133)], (160, 150, 150))
    c.ellipse(64, 133, 67, 136, (240, 120, 170))


def cella_escarabat(c):
    c.ellipse(92, 119, 100, 124, (40, 30, 26))
    c.px(91, 121, (40, 30, 26))
    c.px(96, 119, (90, 70, 50))
    for x in (93, 95, 97):
        c.px(x, 125, (30, 22, 20))


def cella_safata(c):
    c.rect(234, 130, 262, 136, (150, 156, 166))
    c.ellipse(242, 126, 256, 133, (210, 210, 200))
    c.ellipse(244, 127, 254, 131, (150, 190, 90))
    for x, y in ((247, 124), (251, 122)):
        c.ellipse(x, y, x + 2, y + 2, (190, 230, 140))                # bombolles


def cella_panell_afluixat(c):
    # La tapa, afluixada pel cop: una escletxa fosca i un cargol menys.
    c.rect(176, 57, 209, 60, (20, 22, 28))
    c.rect(176, 57, 179, 93, (20, 22, 28))
    c.rect(179, 60, 209, 94, (120, 74, 52))
    c.rect(181, 62, 207, 92, (150, 96, 64))
    rnd = random.Random(9)
    for _ in range(30):
        c.px(181 + rnd.randint(0, 26), 62 + rnd.randint(0, 30), rnd.choice([(110, 60, 40), (170, 110, 70), (90, 52, 36)]))
    for x, y in ((205, 64), (183, 90), (205, 90)):
        c.px(x, y, (60, 50, 50))
    for y in range(68, 86, 4):
        c.line([(187, y), (203, y)], (90, 56, 40))


def _cella_consola(c):
    """El forat del panell amb la consola vella a dins, i la tapa recolzada a terra."""
    c.rect(176, 58, 208, 92, (120, 74, 52))                           # marc rovellat
    c.rect(178, 60, 206, 90, (18, 20, 26))                            # forat
    c.rect(181, 70, 203, 88, (78, 84, 92))                            # consola
    c.rect(181, 70, 203, 72, (110, 118, 128))
    c.ellipse(184, 75, 192, 83, (210, 200, 170))                      # rellotge
    c.line([(188, 79), (190, 76)], (150, 40, 30))
    c.rect(196, 64, 199, 70, (30, 30, 34))                            # forat de la palanca
    for x in (195, 198, 201):
        c.px(x, 84, (60, 40, 40))                                     # llums apagades
    # La tapa, a terra contra la paret
    c.d.polygon([(214, 113), (238, 113), (234, 96), (218, 96)], fill=(150, 96, 64))
    c.line([(219, 101), (233, 101)], (90, 56, 40))
    c.line([(218, 106), (234, 106)], (90, 56, 40))


def cella_panell_obert(c):
    _cella_consola(c)


def cella_panell_reparat(c):
    _cella_consola(c)
    # La clau anglesa fent de palanca
    c.line([(197, 69), (203, 52)], (200, 210, 225), 2)
    c.ellipse(200, 47, 208, 55, (200, 210, 225))
    c.rect(203, 47, 206, 51, (18, 20, 26))
    c.px(201, 60, (240, 250, 255))
    c.rect(194, 83, 197, 86, (90, 240, 120))                          # llumeta verda
    c.px(195, 84, (220, 255, 230))
    c.glow(195, 84, 10, (90, 240, 120), 0.9)


CELLA = {
    'era': 'vet',
    'things': {
        'porta': {'rect': (6, 36, 48, 114), 'walk': (34, 134)},
        'panell': {'rect': (176, 58, 208, 92), 'walk': (192, 126)},
        'altaveu': {'rect': (116, 10, 142, 32), 'walk': (130, 126)},
        'llitera': {'rect': (270, 46, 346, 126), 'walk': (262, 134)},
        'finestreta': {'rect': (226, 16, 268, 58), 'walk': (240, 126)},
        'avis': {'rect': (54, 126, 76, 140), 'walk': (82, 140)},
        'escarabat': {'rect': (88, 114, 104, 128), 'walk': (110, 134)},
        'safata': {'rect': (232, 120, 264, 138), 'walk': (226, 142)},
    },
    'spawns': {'vet': (150, 138), 'mos': (306, 140), 'mare': (130, 30)},
    'walkable': [(14, 118), (266, 118), (268, 128), (338, 130), (346, 148), (6, 148)],
    'bg': cella_bg,
    'props': {'avis': cella_avis, 'escarabat': cella_escarabat, 'safata': cella_safata,
              'panell_afluixat': cella_panell_afluixat, 'panell_obert': cella_panell_obert,
              'panell_reparat': cella_panell_reparat},
}


# ─── La Gavina: passadís ────────────────────────────────────────────────────

def passadis_bg(c):
    vx, vy = 200, 64
    c.rect(0, 0, W, H, (40, 50, 64))
    # Parets en perspectiva
    c.d.polygon([(0, 0), (vx - 40, vy - 24), (vx - 40, vy + 24), (0, 112)], fill=(56, 68, 84))
    c.d.polygon([(W, 0), (vx + 40, vy - 24), (vx + 40, vy + 24), (W, 112)], fill=(50, 62, 78))
    c.d.polygon([(0, 0), (W, 0), (vx + 40, vy - 24), (vx - 40, vy - 24)], fill=(32, 40, 52))
    c.rect(vx - 40, vy - 24, vx + 40, vy + 24, (24, 30, 40))
    c.rect(vx - 10, vy - 14, vx + 10, vy + 24, (16, 20, 28))           # porta del fons
    c.glow(vx, vy, 30, (255, 80, 60), 0.6)
    c.ellipse(vx - 3, vy - 20, vx + 3, vy - 16, (255, 90, 70))
    # Terra
    c.d.polygon([(0, 112), (vx - 40, vy + 24), (vx + 40, vy + 24), (W, 112), (W, H), (0, H)], fill=(36, 44, 56))
    grating(c, 112, H, (38, 46, 58), (26, 30, 40), vx=vx)
    c.d.polygon([(vx - 2, vy + 24), (vx + 2, vy + 24), (vx + 30, H), (vx - 30, H)], fill=(200, 170, 50))
    # Llums de sostre en perspectiva
    for t in (0.15, 0.45, 0.75):
        x0 = int(W * 0.5 * (1 - t) + (vx - 30) * t)
        y0 = int(0 * (1 - t) + (vy - 24) * t)
        x1 = int(W * 0.5 * (1 - t) + (vx + 30) * t) + 40
        c.rect(min(x0, x1) + 10, y0 + 2, max(x0, x1) - 10, y0 + 4, (200, 240, 255))
        c.glow((x0 + x1) // 2, y0 + 4, 40, (170, 220, 255), 0.4)
    # Línies de paret
    for i in range(1, 6):
        t = i / 6
        x = int(0 * (1 - t) + (vx - 40) * t)
        c.line([(x, int(0 * (1 - t) + (vy - 24) * t)), (x, int(112 * (1 - t) + (vy + 24) * t))], (40, 50, 64))
        x = int(W * (1 - t) + (vx + 40) * t)
        c.line([(x, int(0 * (1 - t) + (vy - 24) * t)), (x, int(112 * (1 - t) + (vy + 24) * t))], (36, 46, 60))

    # Cartell del reciclatge (sense text: el text el diu el joc)
    c.rect(240, 30, 296, 54, (236, 236, 226))
    c.d.rectangle([240, 30, 296, 54], outline=(60, 160, 90))
    for i in range(3):                                                 # fletxes de reciclar en cercle
        a = i * 2.094
        x, y = 256 + math.cos(a) * 7, 42 + math.sin(a) * 7
        c.d.polygon([(x - 3, y - 3), (x + 3, y), (x - 3, y + 3)], fill=(60, 160, 90))
    c.ellipse(272, 34, 290, 50, (250, 220, 70))                        # el somriure
    c.px(278, 40, (40, 40, 40))
    c.px(284, 40, (40, 40, 40))
    c.d.arc([276, 38, 286, 47], 20, 160, fill=(40, 40, 40))
    c.d.polygon([(298, 38), (310, 42), (298, 46)], fill=(60, 160, 90))  # fletxa cap al fons

    # Càmera de vigilància
    c.rect(318, 10, 322, 16, (30, 30, 34))
    c.d.polygon([(304, 14), (326, 14), (326, 24), (306, 24)], fill=(170, 176, 186))
    c.rect(302, 16, 306, 22, (40, 40, 46))
    c.px(320, 18, (90, 255, 120))
    c.glow(320, 18, 6, (90, 255, 120), 0.6)

    cell_door(c, 8, 38, 46, 112, outside=True)
    vignette(c, 110)


PASSADIS = {
    'era': 'vet',
    'things': {
        'porta_cella': {'rect': (6, 34, 48, 114), 'walk': (34, 134)},
        'cartell': {'rect': (238, 28, 312, 56), 'walk': (270, 128)},
        'camera_vigilancia': {'rect': (300, 8, 328, 26), 'walk': (310, 128)},
        'porta_hangar': {'rect': (186, 46, 214, 90), 'walk': (200, 120)},
    },
    'spawns': {'vet': (90, 138)},
    'walkable': [(14, 118), (338, 118), (346, 148), (6, 148)],
    'bg': passadis_bg,
    'props': {},
}


# ─── Fàbrica: moll de càrrega (Acte 2) ──────────────────────────────────────

def pillar(c, x0, x1, base, dark, num_col, y0=0, y1=112):
    """Pilar amb un 7 pintat (és el mateix lloc a les dues èpoques)."""
    c.hgrad(x0, y0, x1, y1, [(0, dark), (0.4, base), (1, dark)])
    seven = ['####', '...#', '..#.', '..#.', '.#..', '.#..']
    for dy, row in enumerate(seven):
        for dx, ch in enumerate(row):
            if ch == '#':
                c.px(x0 + 4 + dx, 40 + dy, num_col)


def moll_bg(c):
    bricks(c, 0, 0, W, 112, (122, 62, 42), (68, 38, 30), seed=51)
    c.vgrad(0, 0, W, 10, (40, 26, 20), (70, 40, 30))
    pipe_h(c, 0, 240, 6, 3, IRON)
    planks(c, 112, H, (92, 64, 44), (58, 38, 26))
    c.rect(0, 110, W, 113, (52, 34, 24))
    # Rails de la llançadora
    for y in (126, 138):
        c.line([(240, y), (W, y + 6)], IRON[2], 2)
    factory_door(c, 8, 50, 40, 112)
    # Comporta del moll, oberta: a fora, la nit
    c.rect(244, 10, 350, 112, (40, 34, 30))
    c.vgrad(250, 16, 346, 108, (18, 20, 40), (40, 34, 50))
    rnd = random.Random(52)
    for _ in range(18):
        c.px(rnd.randint(252, 344), rnd.randint(18, 60), (220, 220, 240))
    c.rect(244, 10, 350, 18, IRON[1])
    for x in range(248, 350, 8):                                    # franges de perill
        c.rect(x, 12, x + 3, 16, (230, 180, 40))
    # La llançadora, nova
    c.ellipse(256, 44, 344, 98, (176, 186, 196))
    c.ellipse(262, 50, 338, 70, (214, 222, 230))
    c.d.polygon([(256, 71), (238, 66), (238, 76)], fill=(150, 160, 170))   # morro
    for x in range(270, 340, 10):
        c.px(x, 72, (120, 130, 140))
        c.px(x, 86, (120, 130, 140))
    c.rect(290, 60, 306, 72, (60, 120, 160))                        # finestreta
    c.rect(318, 92, 334, 104, (140, 150, 160))                      # aleta
    c.rect(270, 98, 276, 112, IRON[1])                              # suports
    c.rect(322, 98, 328, 112, IRON[1])
    # Pilar 7
    pillar(c, 182, 196, (150, 92, 64), (100, 60, 40), (240, 230, 210))
    # Cavallets (la biga és un prop a part)
    for x in (70, 136):
        c.line([(x - 6, 126), (x, 100)], WOOD[0], 2)
        c.line([(x + 6, 126), (x, 100)], WOOD[0], 2)
        c.rect(x - 8, 100, x + 8, 102, WOOD[1])
    # Bastidor de la paret (la biga de ferro-9 és un prop a part)
    for x in (66, 146):
        c.rect(x, 48, x + 3, 62, IRON[0])
        c.rect(x - 2, 60, x + 5, 62, IRON[1])
    # Tauler d'eines
    c.rect(204, 30, 244, 82, (110, 80, 52))
    c.rect(206, 32, 242, 80, (150, 112, 74))
    c.rect(210, 62, 216, 76, IRON[1]); c.rect(208, 60, 218, 63, IRON[2])      # martell
    c.rect(226, 62, 228, 78, (190, 196, 206)); c.rect(224, 60, 230, 63, (190, 196, 206))  # clau
    # Trapa als fonaments, al costat del pilar
    c.rect(198, 120, 226, 130, (70, 48, 30))
    c.rect(200, 122, 224, 128, WOOD[1])
    c.line([(212, 122), (212, 128)], WOOD[0])
    c.ellipse(216, 123, 220, 127, None, outline=IRON[2])
    vignette(c)


def moll_biga_acer(c):
    c.rect(56, 94, 156, 100, (150, 156, 164))
    c.rect(56, 94, 156, 95, (196, 202, 210))
    c.rect(56, 99, 156, 100, (100, 106, 114))


def moll_biga_ferro9(c):
    c.rect(58, 52, 154, 58, (170, 200, 230))
    c.rect(58, 52, 154, 53, (230, 245, 255))
    c.glow(106, 55, 30, (160, 210, 255), 0.35)
    c.rect(100, 58, 112, 64, (236, 230, 210))                       # etiqueta
    c.line([(102, 60), (110, 60)], (160, 40, 40))


def moll_serra(c):
    c.rect(214, 46, 234, 49, (200, 206, 216))                       # fulla
    for x in range(214, 234, 2):
        c.px(x, 50, (150, 156, 166))
    c.rect(232, 44, 240, 52, (120, 60, 40))                         # mànec


def moll_llima(c):
    c.rect(236, 58, 238, 72, (170, 176, 186))
    for y in range(59, 72, 2):
        c.px(237, y, (120, 126, 136))
    c.rect(235, 72, 239, 78, (120, 70, 40))


MOLL = {
    'era': 'iri',
    'things': {
        'porta_calderes': {'rect': (6, 48, 42, 114), 'walk': (30, 134)},
        'biga_acer': {'rect': (54, 90, 158, 104), 'walk': (106, 132)},
        'biga_ferro9': {'rect': (56, 46, 156, 66), 'walk': (106, 128)},
        'serra': {'rect': (212, 42, 242, 54), 'walk': (226, 128)},
        'llima': {'rect': (232, 56, 242, 80), 'walk': (232, 128)},
        'trapa': {'rect': (196, 118, 228, 132), 'walk': (212, 142)},
        'comporta': {'rect': (244, 8, 350, 40), 'walk': (296, 132)},
        'llancadora': {'rect': (236, 42, 346, 110), 'walk': (264, 136)},
    },
    'spawns': {'iri': (40, 138)},
    'walkable': [(14, 118), (338, 118), (346, 148), (6, 148)],
    'bg': moll_bg,
    'props': {'biga_acer': moll_biga_acer, 'biga_ferro9': moll_biga_ferro9, 'serra': moll_serra, 'llima': moll_llima},
}


# ─── La Gavina: moll de l'hangar (Acte 2) ───────────────────────────────────

def hangar_bg(c):
    metal_panels(c, 0, 0, W, 112, (56, 66, 80), (28, 34, 44), (90, 104, 120), seed=61)
    c.rect(0, 0, W, 6, (24, 30, 40))
    grating(c, 112, H, (38, 46, 58), (26, 30, 40))
    c.rect(0, 110, W, 113, (24, 30, 40))
    # Porta del passadís
    c.rect(5, 35, 49, 112, (26, 32, 42))
    c.hgrad(8, 38, 46, 112, [(0, STEEL[0]), (0.3, STEEL[2]), (1, STEEL[0])])
    c.rect(38, 70, 42, 78, (40, 44, 54))
    # Pilar 7: el de la fàbrica, cent vint anys després
    pillar(c, 110, 124, (96, 70, 60), (60, 44, 40), (170, 150, 120))
    c.shade(110, 0, 124, 112, (40, 30, 30), 70)
    # Plaques del terra (la del costat del pilar és la de la nota)
    for x in range(20, 340, 40):
        c.d.rectangle([x, 120, x + 36, 128], outline=(52, 62, 76))
    c.d.rectangle([100, 120, 136, 128], outline=(70, 82, 98))
    for x, y in ((102, 122), (134, 122), (102, 126), (134, 126)):
        c.px(x, y, (120, 130, 140))
    # La comporta, tancada i rovellada
    c.rect(156, 6, 350, 112, (30, 36, 46))
    for y in range(10, 104, 8):
        c.vgrad(176, y, 346, y + 6, (110, 116, 124), (70, 76, 86))
    rnd = random.Random(62)
    for _ in range(26):                                             # rovell
        x, y = rnd.randint(178, 340), rnd.randint(12, 100)
        c.ellipse(x, y, x + rnd.randint(2, 7), y + rnd.randint(2, 5), (130, 74, 44))
    for x in range(176, 346, 8):                                    # franges de perill
        c.rect(x, 104, x + 3, 110, (200, 160, 40))
    # L'encaix de la palanca, buit
    c.rect(158, 56, 172, 104, (20, 24, 30))
    c.rect(162, 60, 168, 100, (8, 10, 14))
    c.rect(156, 52, 174, 56, STEEL[1])
    vignette(c, 100)


def hangar_llancadora(c):
    """La comporta oberta i, a dins, la llançadora vella (quan la Vet obre amb la biga)."""
    c.rect(176, 10, 346, 104, (14, 16, 22))
    for y in range(10, 22, 3):                                      # la comporta, plegada a dalt
        c.rect(176, y, 346, y + 2, (100, 106, 114))
    c.ellipse(196, 46, 330, 100, (120, 120, 116))
    c.ellipse(204, 52, 322, 70, (146, 146, 140))
    c.d.polygon([(196, 73), (178, 68), (178, 78)], fill=(100, 100, 96))
    for x, y in ((236, 76), (268, 82), (300, 74)):                  # els tres forats
        c.rect(x, y, x + 10, y + 7, (20, 20, 24))
        c.d.rectangle([x - 1, y - 1, x + 11, y + 8], outline=(200, 160, 40))
    c.rect(250, 60, 266, 70, (50, 70, 80))
    rnd = random.Random(63)
    for _ in range(40):                                             # pols
        c.px(rnd.randint(200, 326), rnd.randint(50, 98), (160, 160, 150))
    c.line([(176, 22), (196, 50)], (190, 190, 190))                 # teranyines
    c.line([(346, 22), (326, 52)], (190, 190, 190))
    # La porta, amb el pany sònic (un ressonador rodó, sense forat per a cap clau)
    c.rect(214, 56, 234, 90, (104, 104, 100))
    c.d.rectangle([214, 56, 234, 90], outline=(70, 70, 66))
    c.ellipse(228, 70, 234, 76, (150, 140, 110))
    for r_ in (1, 2):
        c.ellipse(231 - r_, 73 - r_, 231 + r_, 73 + r_, None, outline=(90, 84, 66))


def hangar_porta_llancadora(c):
    """La porta de la llançadora, oberta (quan el diapasó obre el pany sònic)."""
    c.rect(214, 56, 234, 90, (10, 12, 16))
    c.rect(206, 56, 213, 90, (104, 104, 100))
    c.d.rectangle([206, 56, 213, 90], outline=(70, 70, 66))
    c.glow(224, 84, 10, (120, 160, 200), 0.3)


HANGAR = {
    'era': 'vet',
    'things': {
        'porta_passadis': {'rect': (6, 34, 48, 114), 'walk': (34, 134)},
        'comporta': {'rect': (156, 6, 350, 112), 'walk': (220, 132)},
        'pilar': {'rect': (108, 8, 126, 112), 'walk': (118, 128)},
        'placa_terra': {'rect': (98, 118, 138, 130), 'walk': (118, 142)},
        'llancadora': {'rect': (178, 40, 334, 104), 'walk': (260, 132)},
    },
    'spawns': {'vet': (70, 138)},
    'walkable': [(14, 118), (338, 118), (346, 148), (6, 148)],
    'bg': hangar_bg,
    'props': {'llancadora': hangar_llancadora, 'porta_llancadora': hangar_porta_llancadora},
}


DESIGNS = {
    'fabrica_calderes': CALDERES,
    'fabrica_magatzem': MAGATZEM,
    'fabrica_cambra': CAMBRA,
    'gavina_cella': CELLA,
    'gavina_passadis': PASSADIS,
    'fabrica_moll': MOLL,
    'gavina_hangar': HANGAR,
}
