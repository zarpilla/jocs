"""
Dissenys provisionals de les sales: el dibuix del fons en pixel art i, alhora, la
geometria per a Benne (on és cada cosa, on es camina, on hi ha cada personatge), perquè el que
es veu i el que es pot clicar coincideixin.

Cada disseny:
  era       protagonista de la sala (tria la paleta de draw_placeholders.py)
  things    id → {'rect': (x0, y0, x1, y1), 'walk': (x, y)}  (hotspots, props i sortides)
  spawns    personatge → (x, y)  (peus)
  walkable  polígon del terra
  bg(c)     dibuixa el fons
  props     id → funció que dibuixa el prop condicional (fotograma a part)

Coordenades de disseny = píxels del joc, 480×270 (escala.py); per sota de y≈205
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
    """Llenç amb utilitats de pixel art. Les coordenades són de disseny (480×270); `k` és l'escala
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


# ─── Títols ─────────────────────────────────────────────────────────────────

LLETRES = {
    'F': ['11111', '10000', '10000', '11110', '10000', '10000', '10000'],
    'E': ['11111', '10000', '10000', '11110', '10000', '10000', '11111'],
    'R': ['11110', '10001', '10001', '11110', '10100', '10010', '10001'],
    'O': ['01110', '10001', '10001', '10001', '10001', '10001', '01110'],
    '-': ['00000', '00000', '00000', '11111', '00000', '00000', '00000'],
    '9': ['01110', '10001', '10001', '01111', '00001', '00010', '01100'],
    'S': ['01111', '10000', '10000', '01110', '00001', '00001', '11110'],
    'U': ['10001', '10001', '10001', '10001', '10001', '10001', '01110'],
    'M': ['10001', '11011', '10101', '10101', '10001', '10001', '10001'],
    'A': ['01110', '10001', '10001', '11111', '10001', '10001', '10001'],
    'Z': ['11111', '00001', '00010', '00100', '01000', '10000', '11111'],
    ' ': ['00000', '00000', '00000', '00000', '00000', '00000', '00000'],
    'L': ['10000', '10000', '10000', '10000', '10000', '10000', '11111'],
    'P': ['11110', '10001', '10001', '11110', '10000', '10000', '10000'],
    'I': ['01110', '00100', '00100', '00100', '00100', '00100', '01110'],
    'N': ['10001', '11001', '10101', '10011', '10001', '10001', '10001'],
}


def titol(c, text, cx, y, mida):
    """Un títol en lletres de píxel grosses, amb ombra."""
    amplada = len(text) * 6 * mida - mida
    x0 = cx - amplada / 2
    for passada, desplaçament in (('ombra', 2), ('vora', 1), ('cos', 0)):
        for i, lletra in enumerate(text):
            for fila, bits in enumerate(LLETRES[lletra]):
                for col, bit in enumerate(bits):
                    if bit != '1':
                        continue
                    x = x0 + (i * 6 + col) * mida + desplaçament
                    yy = y + fila * mida + desplaçament
                    if passada == 'ombra':
                        c.rect(x, yy, x + mida - 1, yy + mida - 1, (6, 8, 16))
                    elif passada == 'vora':
                        c.rect(x - 1, yy - 1, x + mida, yy + mida, (20, 30, 50))
                    else:
                        t = fila / 6
                        c.rect(x, yy, x + mida - 1, yy + mida - 1, lerp((236, 244, 255), (120, 170, 220), t))
                        c.px(x, yy, (255, 255, 255))


# ─── Sales de Suma Zero ─────────────────────────────────────────────────────
# Les que tenen art definitiu (hd/rooms/<sala>.py) només fan servir d'aquí la geometria; `bg` és
# el dibuix provisional per si mai no hi hagués art HD.

PIS_ESTUDI = {
    'era': 'iri',
    'things': {
        'finestra': {'rect': (34, 30, 124, 112), 'walk': (80, 184)},
        'poster': {'rect': (150, 36, 190, 92), 'walk': (170, 184)},
        'matalas': {'rect': (12, 140, 146, 176), 'walk': (90, 186)},
        'pizzes': {'rect': (148, 146, 192, 172), 'walk': (176, 186)},
        'ordinadors': {'rect': (206, 60, 360, 116), 'walk': (270, 184)},
        'router': {'rect': (372, 100, 410, 126), 'walk': (392, 184)},
        'fibra': {'rect': (414, 108, 438, 160), 'walk': (428, 184)},
        'passaplats': {'rect': (430, 56, 476, 102), 'walk': (454, 184)},
        'caixa': {'rect': (300, 163, 342, 190), 'walk': (322, 197)},
    },
    'spawns': {'iri': (150, 192), 'diu': (262, 192)},
    'walkable': [(14, 177), (466, 177), (474, 203), (6, 203)],
    'bg': lambda c: c.rect(0, 0, W, H, (40, 30, 56)),
    'props': {},
}



# ─── Acte 1: sales provisionals (geometria definitiva, dibuix esquemàtic) ─────

from hd.pix import hr  # noqa: E402  (soroll determinista)
# Paletes per lloc: la cuina, càlida; el bar, fusta i neó; l'aeroport, gris i blau fred.

def dark(col, k=0.55):
    return tuple(int(v * k) for v in col)


def obj(c, x0, y0, x1, y1, col, edge=None):
    """Capsa plena amb contorn fosc (estil del joc) i una mica de llum a dalt."""
    c.rect(x0, y0, x1, y1, col)
    c.rect(x0 + 1, y0 + 1, x1 - 1, y0 + 2, tuple(min(255, int(v * 1.25)) for v in col))
    outline_rect(c, x0, y0, x1, y1, edge or dark(col, 0.4))


def room_base(c, wall_top, wall_bot, floor, floor_y=150, base=None):
    c.vgrad(0, 0, W, floor_y, wall_top, wall_bot)
    c.rect(0, floor_y - 4, W, floor_y, base or dark(wall_bot, 0.6))
    c.vgrad(0, floor_y + 1, W, H, floor, dark(floor, 0.6))


def door(c, x0, y0, x1, y1, col, knob=(200, 180, 120)):
    obj(c, x0, y0, x1, y1, col)
    c.rect(x0 + 4, y0 + 4, x1 - 4, (y0 + y1) // 2 - 2, dark(col, 0.85))
    c.rect(x0 + 4, (y0 + y1) // 2 + 2, x1 - 4, y1 - 4, dark(col, 0.85))
    c.ellipse(x1 - 9, (y0 + y1) // 2 - 2, x1 - 5, (y0 + y1) // 2 + 2, knob)


WALK_STD = [(14, 177), (466, 177), (474, 203), (6, 203)]


# La cuina (Vet)
def cuina_bg(c):
    room_base(c, (122, 96, 58), (96, 74, 46), (70, 60, 52))
    for x in range(0, W, 16):                                    # rajoles
        for y in range(70, 146, 12):
            c.rect(x, y, x + 15, y + 11, (196, 186, 160) if (x // 16 + y // 12) % 2 else (180, 170, 146))
    obj(c, 16, 124, 204, 160, (120, 80, 50))                     # taulell i armaris
    obj(c, 12, 118, 208, 124, (200, 190, 170))
    obj(c, 104, 112, 176, 122, (160, 168, 176))                  # aigüera amb els plats
    for i in range(6):
        c.ellipse(110 + i * 9, 104 - (i % 3) * 3, 124 + i * 9, 114 - (i % 3) * 3, (226, 226, 220), (120, 120, 120))
    obj(c, 56, 96, 86, 118, (60, 60, 66))                        # cafetera
    c.rect(64, 86, 78, 96, (40, 40, 44))
    c.ellipse(78, 100, 84, 106, (200, 40, 40))
    obj(c, 220, 50, 282, 160, (226, 230, 232))                   # nevera
    c.line([(274, 80), (274, 110)], (120, 120, 130), 2)
    c.rect(300, 66, 352, 110, (90, 60, 40))                      # passaplats
    c.rect(304, 70, 348, 106, (240, 200, 120))
    door(c, 418, 40, 466, 160, (110, 76, 52))
    c.rect(330, 20, 400, 52, (40, 40, 60))                       # finestra de la cuina
    c.rect(333, 23, 397, 49, (20, 24, 50))


def cuina_cable(c):
    c.line([(70, 118), (66, 130), (40, 136), (30, 128)], (30, 30, 30), 2)
    c.rect(26, 124, 32, 130, (240, 240, 240))


def cuina_nevera_oberta(c):
    c.rect(222, 52, 280, 158, (250, 246, 220))
    for y in (78, 98, 118, 138):
        c.rect(224, y, 278, y + 1, (200, 200, 200))
    c.rect(282, 50, 300, 160, (226, 230, 232))
    outline_rect(c, 282, 50, 300, 160, (90, 90, 96))
    c.ellipse(266, 120, 276, 134, (240, 240, 230), (150, 150, 150))   # el iogurt que vota


def cuina_pizza(c):
    c.rect(228, 82, 266, 90, (210, 170, 110))
    outline_rect(c, 228, 82, 266, 90, (110, 80, 40))


def cuina_tonyina(c):
    c.ellipse(232, 102, 248, 112, (220, 170, 100), (120, 80, 40))
    c.rect(252, 104, 264, 112, (90, 140, 200))


PIS_CUINA = {
    'era': 'vet',
    'things': {
        'cafetera': {'rect': (56, 86, 86, 118), 'walk': (80, 188)},
        'plats': {'rect': (104, 98, 176, 122), 'walk': (140, 188)},
        'nevera': {'rect': (220, 50, 282, 160), 'walk': (250, 188)},
        'pizza_nevera': {'rect': (228, 80, 266, 92), 'walk': (250, 188)},
        'tonyina': {'rect': (230, 100, 266, 114), 'walk': (250, 188)},
        'passaplats': {'rect': (300, 66, 352, 110), 'walk': (326, 188)},
        'porta': {'rect': (418, 40, 466, 160), 'walk': (442, 186)},
    },
    'sense_etiqueta': ('pizza_nevera', 'tonyina'),
    'spawns': {'vet': (180, 194)},
    'walkable': WALK_STD,
    'bg': cuina_bg,
    'props': {'cable_cafetera': cuina_cable, 'nevera_oberta': cuina_nevera_oberta, 'pizza_nevera': cuina_pizza, 'tonyina': cuina_tonyina},
}


# El bar (Vet)
def bar_bg(c):
    room_base(c, (70, 40, 34), (52, 30, 28), (60, 44, 34))
    for x in range(0, W, 24):                                    # arrambador de fusta
        c.rect(x, 96, x + 22, 146, (96, 60, 38))
    c.rect(150, 18, 310, 48, (24, 16, 24))                       # rètol (neó) amb el nom
    c.rect(170, 26, 290, 40, (60, 20, 40))
    titol(c, 'LA PROPINA', 230, 27, 2)
    c.glow(230, 33, 70, (255, 80, 160), 0.18)
    obj(c, 100, 120, 420, 152, (110, 70, 44))                    # barra
    obj(c, 96, 114, 424, 120, (170, 120, 80))
    for x in (130, 190, 250, 310):                               # tamborets
        c.rect(x, 152, x + 4, 176, (60, 60, 70))
        c.ellipse(x - 8, 148, x + 12, 156, (170, 40, 40))
    for i, x in enumerate(range(116, 410, 14)):                  # ampolles a la lleixa
        c.rect(x, 78, x + 6, 94, [(60, 120, 60), (140, 90, 30), (180, 180, 200), (120, 30, 30)][i % 4])
    c.rect(110, 94, 412, 96, (130, 90, 60))
    obj(c, 326, 40, 404, 86, (20, 20, 24))                       # tele
    c.rect(330, 44, 400, 80, (40, 130, 60))                      # partit de futbol
    c.rect(364, 44, 365, 80, (220, 230, 220))
    obj(c, 430, 68, 452, 100, (200, 190, 160))                   # telèfon de paret
    c.rect(436, 74, 446, 92, (60, 60, 60))
    door(c, 18, 54, 64, 150, (110, 76, 52))                      # rebost
    obj(c, 456, 48, 478, 160, (60, 80, 90))                      # sortida (vidre)
    c.rect(460, 52, 474, 156, (30, 50, 70))
    c.rect(78, 20, 140, 60, (20, 24, 44))                        # finestra: autopista de nit
    c.line([(80, 52), (138, 44)], (220, 200, 120), 1)


def bar_tap(c):
    c.ellipse(252, 112, 262, 118, (220, 200, 80), (110, 90, 30))
    c.rect(256, 110, 258, 112, (180, 180, 180))


def bar_comandament(c):
    c.rect(282, 112, 300, 117, (30, 30, 34))
    c.px(286, 114, (220, 40, 40))


def bar_bassols(c):
    c.rect(330, 44, 400, 80, (40, 40, 70))
    c.ellipse(350, 52, 368, 76, (220, 180, 150))                 # la comissària, de perfil
    c.rect(346, 48, 372, 56, (50, 30, 30))
    c.rect(374, 64, 396, 66, (240, 240, 240))


def bar_rebost_tancat(c):
    c.rect(26, 92, 56, 102, (230, 220, 180))
    outline_rect(c, 26, 92, 56, 102, (120, 40, 40))
    c.line([(30, 97), (52, 97)], (180, 40, 40), 2)


BAR_SALA = {
    'era': 'vet',
    'things': {
        'retol': {'rect': (150, 18, 310, 48), 'walk': (230, 186)},
        'tele': {'rect': (326, 40, 404, 86), 'walk': (360, 186)},
        'telefon': {'rect': (430, 68, 452, 100), 'walk': (440, 186)},
        'porta_rebost': {'rect': (18, 54, 64, 150), 'walk': (42, 184)},
        'porta': {'rect': (456, 48, 478, 160), 'walk': (462, 186)},
        'tap_barra': {'rect': (248, 108, 266, 120), 'walk': (256, 186)},
        'comandament_barra': {'rect': (280, 108, 302, 120), 'walk': (290, 186)},
    },
    'sense_etiqueta': ('tap_barra', 'comandament_barra'),
    'spawns': {'vet': (226, 196), 'marcel': (140, 190), 'puig': (340, 172)},
    'walkable': WALK_STD,
    'bg': bar_bg,
    'props': {'tap_barra': bar_tap, 'comandament_barra': bar_comandament, 'tele_bassols': bar_bassols, 'rebost_tancat': bar_rebost_tancat},
}


# El rebost (Vet)
def rebost_bg(c):
    room_base(c, (86, 76, 64), (66, 58, 48), (56, 48, 40))
    obj(c, 160, 116, 290, 160, (100, 70, 46))                    # escriptori d'en Puig
    obj(c, 196, 120, 252, 136, (130, 90, 60))                    # calaix
    c.rect(220, 124, 228, 132, (40, 40, 44))
    c.px(224, 128, (220, 40, 40))                                # el llum vermell del pany
    for i, (x, y) in enumerate(((300, 120), (340, 120), (320, 90), (380, 120), (360, 90))):
        obj(c, x, y, x + 36, y + 30, (150, 110, 60))
    c.rect(330, 30, 380, 60, (220, 210, 190))                    # cartell de prohibit fumar
    c.ellipse(345, 35, 365, 55, (200, 40, 40))
    door(c, 30, 50, 76, 160, (110, 76, 52))


def rebost_calaix_obert(c):
    c.rect(196, 136, 252, 146, (90, 60, 40))
    c.rect(210, 138, 230, 142, (240, 240, 230))
    c.px(224, 128, (60, 220, 90))


BAR_REBOST = {
    'era': 'vet',
    'things': {
        'calaix': {'rect': (196, 116, 252, 146), 'walk': (224, 188)},
        'caixes': {'rect': (300, 90, 416, 150), 'walk': (360, 188)},
        'porta': {'rect': (30, 50, 76, 160), 'walk': (54, 186)},
    },
    'spawns': {'vet': (150, 194)},
    'walkable': WALK_STD,
    'bg': rebost_bg,
    'props': {'calaix_obert': rebost_calaix_obert},
}


# L'aeroport: la terminal (Vet)
def terminal_bg(c):
    room_base(c, (176, 186, 196), (140, 150, 162), (120, 124, 130), base=(90, 96, 104))
    for x in range(0, W, 40):
        c.rect(x, 150, x + 1, H, (100, 104, 110))
    c.rect(170, 26, 310, 112, (60, 90, 120))                     # vidriera
    c.rect(174, 30, 306, 108, (110, 150, 190))
    c.line([(240, 30), (240, 108)], (60, 90, 120), 2)
    c.rect(270, 60, 286, 106, (40, 40, 50))                      # l'Ortega, a fora
    c.ellipse(270, 46, 286, 62, (220, 180, 150))
    c.rect(286, 66, 298, 68, (240, 240, 240))                    # la cigarreta sencera
    c.px(298, 67, (255, 120, 40))
    obj(c, 30, 110, 150, 150, (90, 100, 120))                    # taulell de facturació
    obj(c, 26, 104, 154, 110, (200, 204, 210))
    door(c, 8, 40, 26, 150, (120, 130, 140))                     # porta de personal (on vigila en Soler)
    obj(c, 330, 70, 426, 150, (110, 90, 70))                     # objectes perduts
    c.rect(340, 80, 416, 100, (90, 70, 56))
    c.rect(330, 58, 426, 70, (240, 200, 60))
    obj(c, 432, 136, 474, 142, (200, 200, 200))                  # taula de cafeteria
    c.rect(450, 142, 454, 170, (120, 120, 120))
    c.rect(40, 14, 140, 24, (30, 30, 40))                        # pantalla de vols
    for i in range(4):
        c.rect(44, 16 + i * 2, 44 + 20 + i * 15, 16 + i * 2, (240, 200, 60))


def terminal_cigarreta_mitja(c):
    c.rect(292, 66, 298, 68, (110, 150, 190))


def terminal_cigarreta_curta(c):
    c.rect(288, 66, 298, 68, (110, 150, 190))


def terminal_maleti(c):
    obj(c, 394, 90, 416, 104, (110, 60, 30))
    c.rect(402, 87, 408, 90, (60, 30, 20))
    c.rect(398, 94, 406, 98, (240, 220, 120))


def terminal_ulleres(c):
    c.ellipse(440, 130, 448, 136, (30, 30, 30))
    c.ellipse(450, 130, 458, 136, (30, 30, 30))
    c.line([(448, 133), (450, 133)], (30, 30, 30), 1)


AEROPORT_TERMINAL = {
    'era': 'vet',
    'things': {
        'taulell': {'rect': (30, 104, 154, 150), 'walk': (92, 186)},
        'vidriera': {'rect': (170, 26, 310, 112), 'walk': (240, 186)},
        'maleti': {'rect': (392, 84, 418, 106), 'walk': (380, 186)},
        'ulleres': {'rect': (436, 126, 462, 140), 'walk': (446, 186)},
    },
    'spawns': {'vet': (220, 196), 'soler': (44, 186), 'empleat': (376, 156), 'nen': (300, 194)},
    'walkable': WALK_STD,
    'bg': terminal_bg,
    'props': {'maleti': terminal_maleti, 'ulleres': terminal_ulleres,
              'cigarreta_mitja': terminal_cigarreta_mitja, 'cigarreta_curta': terminal_cigarreta_curta},
}


# L'aeroport: la porta de personal (Iri)
def personal_bg(c):
    room_base(c, (150, 156, 164), (120, 126, 134), (96, 100, 106), base=(80, 84, 90))
    obj(c, 250, 44, 312, 160, (130, 140, 150))                   # la porta
    c.rect(258, 56, 304, 70, (200, 60, 50))
    obj(c, 226, 86, 246, 112, (40, 44, 50))                      # teclat
    for i in range(9):
        c.rect(229 + (i % 3) * 6, 89 + (i // 3) * 6, 232 + (i % 3) * 6, 92 + (i // 3) * 6, (180, 180, 180))
    c.ellipse(232, 106, 240, 110, (200, 40, 40))                 # llum vermell
    obj(c, 20, 30, 180, 120, (90, 100, 110))                     # vidre cap a la terminal
    c.rect(24, 34, 176, 116, (170, 186, 200))


def personal_porta_oberta(c):
    c.rect(252, 46, 310, 158, (30, 34, 40))
    c.ellipse(232, 106, 240, 110, (60, 220, 90))


def personal_alarma(c):
    c.ellipse(232, 106, 240, 110, (255, 60, 40))
    c.glow(236, 108, 18, (255, 60, 40), 0.6)


AEROPORT_PERSONAL = {
    'era': 'iri',
    'things': {
        'teclat': {'rect': (224, 84, 248, 114), 'walk': (236, 188)},
        'porta': {'rect': (250, 44, 312, 160), 'walk': (280, 186)},
    },
    'spawns': {'iri': (160, 194)},
    'walkable': WALK_STD,
    'bg': personal_bg,
    'props': {'porta_oberta': personal_porta_oberta, 'alarma': personal_alarma},
}


# L'aeroport: l'oficina de facturació (Iri)
def oficina_bg(c):
    room_base(c, (130, 136, 144), (104, 110, 118), (84, 86, 92))
    obj(c, 90, 122, 330, 160, (150, 150, 156))                   # taula
    obj(c, 120, 86, 180, 122, (40, 44, 50))                      # terminal
    c.rect(124, 90, 176, 116, (20, 60, 90))
    obj(c, 258, 100, 304, 122, (220, 220, 224))                  # impressora
    c.rect(266, 98, 296, 100, (60, 60, 64))
    door(c, 400, 50, 450, 160, (120, 130, 140))
    for i in range(3):                                           # arxivadors
        obj(c, 20 + i * 22, 70, 40 + i * 22, 150, (100, 110, 120))


def oficina_llista(c):
    for i in range(4):
        c.rect(128, 94 + i * 5, 128 + 20 + (i * 7) % 24, 95 + i * 5, (200, 230, 240))
    c.rect(128, 112, 168, 113, (240, 220, 80))


def oficina_imprimint(c):
    c.rect(270, 90, 292, 100, (250, 250, 250))
    c.glow(281, 104, 14, (120, 255, 140), 0.4)


def oficina_acreditacions(c):
    c.rect(268, 92, 282, 100, (250, 250, 250))
    c.rect(284, 92, 298, 100, (250, 250, 250))
    c.rect(270, 94, 274, 98, (200, 120, 100))
    c.rect(286, 94, 290, 98, (120, 90, 80))


AEROPORT_OFICINA = {
    'era': 'iri',
    'things': {
        'terminal': {'rect': (118, 84, 182, 124), 'walk': (150, 188)},
        'impressora': {'rect': (256, 90, 306, 124), 'walk': (280, 188)},
        'porta': {'rect': (400, 50, 450, 160), 'walk': (424, 186)},
    },
    'spawns': {'iri': (200, 194)},
    'walkable': WALK_STD,
    'bg': oficina_bg,
    'props': {'llista_feta': oficina_llista, 'imprimint': oficina_imprimint, 'acreditacions_llestes': oficina_acreditacions},
}


# Cinemàtiques: el pròleg (Ginebra de nit) i l'avió
def ginebra_bg(c):
    c.vgrad(0, 0, W, 140, (8, 10, 30), (40, 30, 70))
    for i in range(40):
        c.px(int(hr(i, 1) * W), int(hr(i, 2) * 90), (220, 220, 240))
    c.vgrad(0, 140, W, H, (20, 30, 60), (6, 8, 20))              # el llac
    obj(c, 150, 40, 330, 140, (180, 176, 168))                   # la seu del BCMU
    for row in range(5):
        for col in range(8):
            c.rect(160 + col * 21, 50 + row * 18, 172 + col * 21, 60 + row * 18,
                   (250, 220, 140) if hr(row, col) > 0.6 else (60, 70, 90))
    c.rect(150, 30, 330, 40, (150, 146, 140))
    c.rect(214, 18, 266, 30, (40, 40, 60))
    for i, ch in enumerate('BCMU'):
        c.rect(220 + i * 11, 21, 228 + i * 11, 27, (240, 200, 80))
    c.line([(240, 140), (240, 150)], (240, 220, 140), 1)
    for y in range(146, 200, 6):                                 # reflex al llac
        c.line([(200 + (y % 12), y), (280 - (y % 12), y)], (120, 110, 90), 1)


def avio_bg(c):
    c.vgrad(0, 0, W, H, (60, 66, 80), (30, 32, 40))
    for x in range(30, W, 70):
        c.ellipse(x, 40, x + 34, 80, (200, 220, 240), (120, 130, 150))   # finestretes
        c.ellipse(x + 4, 44, x + 30, 76, (90, 130, 190))
    for x in range(10, W, 60):
        obj(c, x, 110, x + 46, 200, (50, 70, 120))               # seients
        obj(c, x + 4, 96, x + 42, 116, (60, 84, 140))


def portada_bg(c):
    c.vgrad(0, 0, W, H, (20, 10, 34), (60, 20, 50))
    for i in range(10):                                          # silueta de la ciutat
        x = i * 50
        h = 40 + int(hr(i, 7) * 70)
        c.rect(x, 190 - h, x + 44, 190, (14, 10, 22))
        for wy in range(190 - h + 6, 186, 8):
            for wx in range(x + 4, x + 40, 8):
                if hr(wx, wy) > 0.65:
                    c.rect(wx, wy, wx + 2, wy + 2, (250, 200, 120))
    c.rect(0, 190, W, H, (10, 8, 16))
    titol(c, 'SUMA ZERO', W / 2, 40, 5)


def cinematica(bg):
    return {'era': '', 'things': {}, 'spawns': {}, 'walkable': [(150, 190), (200, 190), (200, 196), (150, 196)],
            'bg': bg, 'props': {}, 'etiquetes': False}


# Cada sala amb disseny propi: id de la sala → disseny (vegeu el principi del fitxer).
DESIGNS = {
    'pis_estudi': PIS_ESTUDI,
    'pis_cuina': PIS_CUINA,
    'bar_sala': BAR_SALA,
    'bar_rebost': BAR_REBOST,
    'aeroport_terminal': AEROPORT_TERMINAL,
    'aeroport_personal': AEROPORT_PERSONAL,
    'aeroport_oficina': AEROPORT_OFICINA,
    'proleg_ginebra': cinematica(ginebra_bg),
    'avio': cinematica(avio_bg),
    'portada': cinematica(portada_bg),
}
