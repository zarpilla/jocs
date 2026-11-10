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

# Cada sala amb disseny propi: id de la sala → disseny (vegeu el principi del fitxer).
DESIGNS = {
    'pis_estudi': PIS_ESTUDI,
}
