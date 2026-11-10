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

def wall_vent(c, x0, y0, x1, y1, frame, bar, bolt):
    """Reixa de ventilació a la paret, arran de terra, amb un cargol a cada cantonada."""
    c.rect(x0, y0, x1, y1, (14, 14, 18))
    outline_rect(c, x0, y0, x1, y1, frame)
    for x in range(x0 + 4, x1 - 2, 5):
        c.rect(x, y0 + 2, x + 1, y1 - 2, bar)
    for x, y in ((x0 + 1, y0 + 1), (x1 - 2, y0 + 1), (x0 + 1, y1 - 2), (x1 - 2, y1 - 2)):
        c.rect(x, y, x + 1, y + 1, bolt)


def carved_mark(c, x, y, col):
    """La marca de l'Iri: una I. i una clau anglesa, gravades."""
    c.rect(x, y, x + 1, y + 7, col)
    c.px(x + 3, y + 7, col)
    c.line([(x + 6, y + 8), (x + 11, y + 1)], col)
    c.ellipse(x + 9, y - 2, x + 14, y + 3, None, outline=col)


# ─── Les notes perdudes: amagatalls petits (només es veuen si hi mires bé) ───

def amb(bg, *extres):
    """El fons `bg` amb uns quants detalls més dibuixats al damunt."""
    def draw(c):
        bg(c)
        for e in extres:
            e(c)
    return draw


def esquerda(c):
    col = (22, 26, 34)
    c.line([(152, 68), (156, 72), (154, 75), (159, 79), (157, 82)], col)
    c.line([(156, 72), (161, 70)], col)


def rajola_solta(c):
    c.rect(122, 131, 144, 139, (52, 60, 74))
    c.line([(122, 131), (144, 131)], (90, 100, 116))
    c.line([(122, 139), (144, 139)], (20, 24, 32))


def caixa_recanvis(c):
    c.rect(302, 113, 328, 125, (96, 70, 48))
    c.rect(302, 113, 328, 115, (122, 90, 60))
    c.rect(306, 117, 324, 118, (70, 50, 34))
    c.px(318, 120, (150, 74, 40)); c.px(309, 122, (150, 74, 40))   # rovell


def socol_holograma(c):
    c.rect(214, 106, 236, 112, (120, 132, 148))
    c.rect(229, 107, 235, 111, (80, 90, 104))                        # la placa descargolada


# Els papers de les notes: props que desapareixen quan la Vet les agafa.
PAPER_VELL = (220, 210, 184)


def nota_esquerda(c):
    c.rect(154, 75, 156, 77, PAPER_VELL)


def nota_rajola(c):
    c.rect(140, 132, 143, 134, PAPER_VELL)


def nota_caixa(c):
    c.rect(320, 111, 324, 113, PAPER_VELL)


def nota_carpeta(c):
    c.d.polygon([(150, 114), (168, 112), (170, 119), (152, 121)], fill=(196, 170, 96))
    c.line([(151, 117), (169, 115)], (150, 124, 70))


def nota_socol(c):
    c.rect(230, 109, 233, 110, PAPER_VELL)

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
    'spawns': {'iri': (160, 138), 'capatas': (262, 132), 'sic': (300, 136)},
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
    factory_door(c, 50, 54, 78, 112)                                # porta del despatx del director
    c.rect(54, 46, 74, 50, (210, 200, 170))
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
        'porta_despatx': {'rect': (48, 44, 80, 114), 'walk': (64, 132)},
    },
    'spawns': {'iri': (70, 138), 'cargol': (210, 132), 'mira': (300, 140)},
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
    wall_vent(c, 248, 86, 286, 108, IRON[2], IRON[1], (200, 204, 212))   # reixa del conducte de servei
    vignette(c)


def cambra_reixa_llimada(c):
    """Els cargols de la reixa, llimats (llueixen) i una ratlla de llima."""
    for x, y in ((249, 87), (284, 87), (249, 106), (284, 106)):
        c.rect(x, y, x + 1, y + 1, (255, 250, 220))
    c.line([(252, 110), (282, 110)], (170, 170, 176))


def cambra_boto(c):
    c.rect(86, 70, 100, 74, (60, 60, 66))
    c.ellipse(88, 64, 98, 72, (220, 40, 40))
    c.ellipse(90, 65, 94, 68, (255, 150, 150))


CAMBRA = {
    'era': 'iri',
    'things': {
        'porta': {'rect': (6, 48, 42, 114), 'walk': (30, 134)},
        'palanca': {'rect': (106, 40, 132, 68), 'walk': (122, 126)},
        'cambra': {'rect': (148, 10, 232, 118), 'walk': (190, 128)},
        'boto': {'rect': (84, 62, 102, 76), 'walk': (94, 126)},
        'reixa': {'rect': (246, 84, 288, 110), 'walk': (266, 128)},
    },
    'spawns': {'iri': (276, 138)},
    'walkable': [(14, 120), (338, 120), (346, 148), (6, 148)],
    'bg': cambra_bg,
    'props': {'boto': cambra_boto, 'reixa_llimada': cambra_reixa_llimada},
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

    cell_door(c, 8, 38, 46, 112)
    wall_vent(c, 62, 84, 100, 108, (120, 74, 52), (110, 64, 44), (90, 52, 36))   # reixa del conducte, rovellada
    rnd = random.Random(42)
    for _ in range(26):
        c.px(63 + rnd.randint(0, 36), 85 + rnd.randint(0, 22), rnd.choice([(150, 90, 56), (130, 74, 44)]))
    vignette(c, 110)


def cella_avis(c):
    c.d.polygon([(56, 130), (72, 128), (74, 136), (58, 138)], fill=(236, 232, 220))
    c.line([(60, 132), (70, 131)], (160, 150, 150))
    c.line([(61, 134), (69, 133)], (160, 150, 150))
    c.ellipse(64, 133, 67, 136, (240, 120, 170))


def cella_fullet(c):
    """El fullet de reeducació, que treu el nas per sota el coixí de la llitera de baix."""
    c.rect(316, 93, 331, 97, (236, 226, 196))
    c.rect(318, 94, 322, 96, (240, 120, 170))                         # el cor de la MARE a la portada
    c.line([(324, 95), (330, 95)], (150, 140, 130))


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


def cella_reixa_oberta(c):
    """La reixa, treta i recolzada a la paret; a dins, la marca de l'Iri i una fletxa."""
    c.rect(62, 84, 100, 108, (6, 6, 8))
    carved_mark(c, 70, 92, (150, 140, 120))
    c.line([(86, 98), (96, 98)], (150, 140, 120))
    c.line([(93, 95), (96, 98), (93, 101)], (150, 140, 120))
    c.d.polygon([(102, 112), (124, 112), (120, 90), (104, 90)], fill=(120, 74, 52))
    for x in range(107, 120, 4):
        c.line([(x, 92), (x, 110)], (90, 52, 36))


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
        'fullet': {'rect': (312, 88, 334, 102), 'walk': (296, 138)},
        'finestreta': {'rect': (226, 16, 268, 58), 'walk': (240, 126)},
        'avis': {'rect': (54, 126, 76, 140), 'walk': (82, 140)},
        'escarabat': {'rect': (88, 114, 104, 128), 'walk': (110, 134)},
        'safata': {'rect': (232, 120, 264, 138), 'walk': (226, 142)},
        'reixa': {'rect': (60, 82, 102, 110), 'walk': (80, 128)},
        'esquerda': {'rect': (148, 64, 164, 86), 'walk': (156, 128)},
    },
    'spawns': {'vet': (150, 138), 'mos': (306, 140), 'mare': (130, 30), 'directora': (214, 138)},
    'walkable': [(14, 118), (266, 118), (268, 128), (338, 130), (346, 148), (6, 148)],
    'bg': amb(cella_bg, esquerda),
    'props': {'avis': cella_avis, 'fullet': cella_fullet, 'escarabat': cella_escarabat, 'safata': cella_safata,
              'panell_afluixat': cella_panell_afluixat, 'panell_obert': cella_panell_obert,
              'panell_reparat': cella_panell_reparat, 'reixa_oberta': cella_reixa_oberta, 'esquerda': nota_esquerda},
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
    # Porta de la Sala de la Memòria, a la paret de la dreta
    c.d.polygon([(262, 62), (294, 58), (294, 112), (262, 110)], fill=(26, 32, 42))
    c.d.polygon([(265, 65), (291, 62), (291, 110), (265, 108)], fill=(120, 150, 170))
    c.rect(270, 50, 288, 55, (236, 236, 226))                          # rètol, amb el somriure
    c.ellipse(276, 51, 280, 54, (250, 220, 70))
    vignette(c, 110)


PASSADIS = {
    'era': 'vet',
    'things': {
        'porta_cella': {'rect': (6, 34, 48, 114), 'walk': (34, 134)},
        'cartell': {'rect': (238, 28, 312, 56), 'walk': (270, 128)},
        'camera_vigilancia': {'rect': (300, 8, 328, 26), 'walk': (310, 128)},
        'porta_hangar': {'rect': (186, 46, 214, 90), 'walk': (200, 120)},
        'porta_memoria': {'rect': (260, 56, 296, 112), 'walk': (276, 128)},
        'rajola': {'rect': (120, 129, 146, 141), 'walk': (133, 138)},
    },
    'spawns': {'vet': (90, 138), 'guardia': (236, 138)},
    'walkable': [(14, 118), (338, 118), (346, 148), (6, 148)],
    'bg': amb(passadis_bg, rajola_solta),
    'props': {'rajola': nota_rajola},
}


# ─── Reixes de desguàs (moll de càrrega i moll de l'hangar: el mateix lloc) ──

# Punt de fuga del terra: les línies de planks() i grating() hi convergeixen (vx=176, y≈76).
FLOOR_VP = (176, 76)
GRATE_Y = (127, 137)
GRATE_NOVA = ((70, 64, 58), (14, 12, 10), (150, 140, 128), (190, 178, 160))      # al passat: ferro nou
GRATE_VELLA = ((58, 66, 78), (10, 12, 16), (96, 106, 120), (110, 122, 138))      # al present


def grate_quad(xa, xb, y0=GRATE_Y[0], y1=GRATE_Y[1]):
    """Cantonades d'una reixa al terra: xa..xb és la vora de davant (a y1); la del fons es projecta
    cap al punt de fuga. Retorna (davant-esquerra, davant-dreta, fons-dreta, fons-esquerra)."""
    vx, vy = FLOOR_VP
    k = (y0 - vy) / (y1 - vy)
    far = lambda x: vx + (x - vx) * k
    return (xa, y1), (xb, y1), (far(xb), y0), (far(xa), y0)


def grate_rect(xa, xb, pad=2):
    """Rectangle clicable que cobreix una reixa (per als `things` dels dissenys)."""
    pts = grate_quad(xa, xb)
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return (int(min(xs)) - pad, int(min(ys)) - pad, int(max(xs)) + pad, int(max(ys)) + pad)


def floor_grate(c, xa, xb, palette):
    """Reixa de desguàs encastada al terra, en perspectiva: marc, forat fosc i barrots que fugen."""
    frame, hole, bar, edge = palette
    (x0, y1), (x1, _), (x2, y0), (x3, _) = grate_quad(xa, xb)
    c.d.polygon([(x0, y1), (x1, y1), (x2, y0), (x3, y0)], fill=frame)
    inset = lambda p, q, t: (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
    a, b2, cc, d = (x0 + 2, y1 - 1), (x1 - 2, y1 - 1), (x2 - 1.5, y0 + 1), (x3 + 1.5, y0 + 1)
    c.d.polygon([a, b2, cc, d], fill=hole)
    n = 9
    for i in range(1, n):
        t = i / n
        c.line([inset(a, b2, t), inset(d, cc, t)], bar)
    c.line([(x3, y0), (x2, y0)], edge)
    for p in ((x0 + 1, y1 - 1), (x1 - 1, y1 - 1), (x2 - 1, y0 + 1), (x3 + 1, y0 + 1)):
        c.px(int(p[0]), int(p[1]), edge)


HANGAR_GRATES = ((16, 54), (118, 156), (214, 252), (296, 334))
MOLL_GRATES = ((24, 62), (100, 138), (170, 208))


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
    # Conducte de pressió amb la vàlvula
    pipe_v(c, 168, 6, 112, 4, COPPER)
    c.ellipse(160, 72, 176, 88, None, outline=(170, 40, 40))
    c.line([(168, 72), (168, 88)], (170, 40, 40))
    c.line([(160, 80), (176, 80)], (170, 40, 40))
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
    # Reixes de desguàs, noves. La del costat del pilar 7 s'aixeca: a sota, els fonaments.
    for xa, xb in MOLL_GRATES:
        floor_grate(c, xa, xb, GRATE_NOVA)
    vignette(c)


def moll_marca_pilar(c):
    carved_mark(c, 185, 60, (70, 40, 28))


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
        'trapa': {'rect': grate_rect(*MOLL_GRATES[2]), 'walk': (189, 143)},
        'conducte': {'rect': (158, 20, 180, 112), 'walk': (168, 130)},
        'comporta': {'rect': (244, 8, 350, 40), 'walk': (296, 132)},
        'llancadora': {'rect': (236, 42, 346, 110), 'walk': (264, 136)},
        'pilar': {'rect': (182, 8, 196, 108), 'walk': (189, 128)},
    },
    'spawns': {'iri': (40, 138)},
    'walkable': [(14, 118), (338, 118), (346, 148), (6, 148)],
    'bg': moll_bg,
    'props': {'biga_acer': moll_biga_acer, 'biga_ferro9': moll_biga_ferro9, 'serra': moll_serra, 'llima': moll_llima,
              'marca_pilar': moll_marca_pilar},
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
    # Reixes de desguàs al terra, les mateixes que al moll de la fàbrica (la del pilar 7 és la de la nota)
    for xa, xb in HANGAR_GRATES:
        floor_grate(c, xa, xb, GRATE_VELLA)
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
    # Conducte vell, amb el manòmetre a zero
    pipe_v(c, 141, 6, 112, 4, STEEL)
    c.ellipse(134, 54, 148, 68, (220, 220, 210), outline=(40, 44, 54))
    c.line([(141, 61), (137, 64)], (180, 30, 30))
    # Escala cap al nivell de sota (l'arxiu)
    c.rect(56, 76, 100, 112, (12, 14, 20))
    for i, y in enumerate(range(80, 112, 6)):
        c.rect(58 + i * 3, y, 98, y + 2, (40, 46, 56))
    c.rect(56, 92, 100, 93, STEEL[1])
    for x in (56, 70, 85, 100):
        c.rect(x, 92, x + 1, 112, STEEL[1])
    c.rect(70, 78, 86, 82, (200, 190, 150))                         # rètol «ARXIU»
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


def hangar_aigua(c):
    """El nivell de sota inundat (massa pressió al conducte): aigua al terra i un raig del conducte."""
    c.shade(0, 116, W, H, (40, 90, 140), 120)
    c.shade(56, 84, 100, 116, (40, 90, 140), 200)
    rnd = random.Random(64)
    for _ in range(30):
        x, y = rnd.randint(0, W - 8), rnd.randint(118, H - 2)
        c.line([(x, y), (x + rnd.randint(3, 8), y)], (140, 190, 230))
    for i in range(6):                                              # el raig del conducte rebentat
        c.line([(144, 96 + i * 2), (152 + i * 3, 104 + i * 4)], (170, 210, 240))


def hangar_marca_pilar(c):
    carved_mark(c, 113, 60, (40, 28, 24))


def hangar_caixa(c):
    c.rect(60, 110, 86, 120, WOOD[1])
    c.rect(60, 110, 86, 111, WOOD[2])
    c.line([(60, 115), (86, 115)], WOOD[0])
    c.rect(66, 112, 80, 114, (200, 190, 150))
    c.line([(56, 121), (90, 121)], (140, 190, 230))


HANGAR = {
    'era': 'vet',
    'things': {
        'porta_passadis': {'rect': (6, 34, 48, 114), 'walk': (34, 134)},
        'comporta': {'rect': (156, 6, 350, 112), 'walk': (220, 132)},
        'pilar': {'rect': (128, 8, 146, 112), 'walk': (137, 128)},
        'placa_terra': {'rect': grate_rect(*HANGAR_GRATES[1]), 'walk': (137, 143)},
        'llancadora': {'rect': (178, 40, 334, 104), 'walk': (260, 132)},
        'pany': {'rect': (224, 65, 238, 81), 'walk': (231, 132)},
        'conducte': {'rect': (104, 10, 124, 112), 'walk': (114, 128)},
        'escala': {'rect': (56, 74, 100, 114), 'walk': (78, 130)},
        'caixa_flotant': {'rect': (58, 106, 90, 124), 'walk': (74, 136)},
        'sortida_conducte': {'rect': grate_rect(*HANGAR_GRATES[0]), 'walk': (35, 143)},
        'caixa_recanvis': {'rect': (300, 111, 330, 127), 'walk': (296, 136)},
    },
    'spawns': {'vet': (70, 138)},
    'walkable': [(14, 118), (338, 118), (346, 148), (6, 148)],
    'bg': amb(hangar_bg, caixa_recanvis),
    'props': {'caixa_recanvis': nota_caixa, 'llancadora': hangar_llancadora, 'porta_llancadora': hangar_porta_llancadora,
              'aigua': hangar_aigua, 'caixa_flotant': hangar_caixa, 'marca_pilar': hangar_marca_pilar},
}


# ─── Fàbrica: despatx del director (Acte 2) ─────────────────────────────────

def despatx_bg(c):
    c.vgrad(0, 0, W, 112, (92, 58, 40), (70, 44, 30))
    for x in range(0, W, 22):                                       # plafons de fusta
        c.rect(x + 2, 40, x + 20, 104, (104, 66, 44))
        c.rect(x + 2, 40, x + 20, 41, (130, 86, 58))
    c.rect(0, 36, W, 39, (60, 38, 26))
    planks(c, 112, H, (110, 74, 48), (70, 46, 30))
    c.rect(0, 110, W, 113, (52, 34, 24))
    factory_door(c, 8, 50, 40, 112)
    # Finestra: la nit i les xemeneies
    c.rect(58, 14, 122, 78, (60, 38, 26))
    c.vgrad(62, 18, 118, 74, (16, 18, 36), (50, 40, 54))
    for x, h_ in ((70, 30), (86, 22), (100, 36)):
        c.rect(x, 74 - h_, x + 6, 74, (30, 26, 30))
    c.line([(90, 18), (90, 74)], (60, 38, 26)); c.line([(62, 46), (118, 46)], (60, 38, 26))
    # Retrat del Director Aldaia
    c.rect(150, 20, 190, 66, (170, 130, 60))
    c.rect(154, 24, 186, 62, (60, 50, 46))
    c.ellipse(162, 30, 178, 48, (200, 170, 140))
    c.rect(160, 48, 180, 62, (40, 40, 50))
    c.rect(164, 36, 166, 37, (30, 30, 30)); c.rect(174, 36, 176, 37, (30, 30, 30))
    c.line([(166, 43), (174, 43)], (120, 60, 60))
    # Escriptori
    c.rect(196, 88, 268, 94, WOOD[2])
    c.rect(198, 94, 266, 112, WOOD[1])
    c.rect(210, 98, 250, 106, WOOD[0])                              # calaix
    c.ellipse(226, 99, 234, 105, (90, 200, 255))                    # pany M-3
    c.glow(230, 102, 8, (90, 200, 255), 0.4)
    c.rect(214, 82, 246, 88, (230, 224, 204))                       # l'expedient del Sic
    c.rect(216, 83, 226, 84, (150, 40, 40))
    c.line([(254, 88), (254, 74)], IRON[1]); c.ellipse(248, 70, 260, 76, (60, 90, 60))
    c.glow(254, 84, 26, (255, 220, 140), 0.6)
    # Faristol amb el llibre d'inventari
    c.rect(302, 96, 306, 124, WOOD[0])
    c.d.polygon([(288, 96), (320, 96), (316, 84), (292, 84)], fill=WOOD[1])
    c.rect(292, 80, 316, 92, (120, 40, 40)); c.rect(294, 81, 314, 90, (236, 230, 210))
    c.line([(304, 81), (304, 90)], (120, 40, 40))
    vignette(c)


DESPATX = {
    'era': 'iri',
    'things': {
        'porta_magatzem': {'rect': (6, 48, 42, 114), 'walk': (30, 134)},
        'retrat': {'rect': (150, 20, 190, 66), 'walk': (170, 128)},
        'calaix': {'rect': (208, 96, 252, 108), 'walk': (230, 134)},
        'expedient_sic': {'rect': (212, 78, 248, 89), 'walk': (230, 130)},
        'llibre_inventari': {'rect': (288, 78, 320, 98), 'walk': (300, 130)},
    },
    'spawns': {'iri': (40, 138)},
    'walkable': [(14, 118), (338, 118), (346, 148), (6, 148)],
    'bg': despatx_bg,
    'props': {},
}


# ─── La Gavina: l'arxiu (Acte 2) ────────────────────────────────────────────

def arxiu_bg(c):
    metal_panels(c, 0, 0, W, 112, (64, 66, 70), (36, 38, 42), (96, 98, 104), seed=71)
    c.rect(0, 0, W, 6, (30, 32, 36))
    grating(c, 112, H, (44, 46, 52), (30, 32, 36))
    c.rect(0, 110, W, 113, (30, 32, 36))
    # Escala amunt, cap al moll de l'hangar
    c.rect(6, 30, 50, 112, (18, 20, 24))
    for i, y in enumerate(range(34, 112, 8)):
        c.rect(8, y, 48 - i * 3, y + 3, (60, 64, 72))
    c.rect(48, 30, 50, 112, STEEL[1])
    # Arxivadors
    for x in range(60, 150, 30):
        c.rect(x, 30, x + 28, 112, (110, 116, 110))
        c.rect(x, 30, x + 28, 31, (150, 156, 150))
        for y in range(36, 108, 18):
            c.rect(x + 3, y, x + 25, y + 14, (96, 102, 96))
            c.rect(x + 11, y + 5, x + 17, y + 7, (180, 184, 180))
    c.rect(118, 74, 138, 80, (230, 220, 190))                       # un sobre que sobresurt
    # Taula amb els expedients i un llum
    c.rect(164, 92, 242, 96, (90, 90, 96))
    c.rect(168, 96, 172, 124, (60, 60, 66)); c.rect(234, 96, 238, 124, (60, 60, 66))
    for i, (x, col) in enumerate(((172, (200, 180, 120)), (194, (220, 200, 150)), (214, (190, 170, 110)))):
        c.rect(x, 84 - i, x + 18, 92 - i, col)
    c.line([(232, 92), (232, 70)], STEEL[1]); c.ellipse(224, 64, 240, 72, (200, 190, 120))
    c.glow(232, 84, 30, (255, 230, 160), 0.6)
    # Taula de dibuix amb les còpies dels plànols
    c.d.polygon([(258, 98), (342, 98), (334, 62), (266, 62)], fill=(70, 74, 82))
    c.d.polygon([(262, 96), (338, 96), (331, 65), (269, 65)], fill=(60, 110, 170))
    for y in range(70, 94, 5):
        c.line([(272, y), (328, y)], (170, 210, 240))
    c.ellipse(286, 72, 314, 90, None, outline=(220, 240, 255))      # la cambra, dibuixada
    c.rect(270, 98, 274, 124, (50, 52, 58)); c.rect(326, 98, 330, 124, (50, 52, 58))
    vignette(c, 110)


ARXIU = {
    'era': 'vet',
    'things': {
        'escala_hangar': {'rect': (6, 28, 50, 114), 'walk': (34, 134)},
        'arxivador': {'rect': (58, 28, 150, 112), 'walk': (104, 128)},
        'expedient_iri': {'rect': (168, 78, 236, 96), 'walk': (200, 130)},
        'planols': {'rect': (258, 60, 342, 100), 'walk': (296, 130)},
        'carpeta': {'rect': (148, 110, 172, 123), 'walk': (160, 132)},
    },
    'spawns': {'vet': (40, 138)},
    'walkable': [(14, 118), (338, 118), (346, 148), (6, 148)],
    'bg': arxiu_bg,
    'props': {'carpeta': nota_carpeta},
}


# ─── La Gavina: la Sala de la Memòria (Acte 3) ──────────────────────────────

def memoria_bg(c):
    c.vgrad(0, 0, W, 112, (196, 206, 214), (160, 172, 184))
    for x in range(0, W, 44):                                       # plafons nets, de museu
        c.rect(x, 8, x + 1, 108, (176, 186, 196))
    c.rect(0, 0, W, 6, (120, 130, 144))
    c.vgrad(0, 112, W, H, (130, 140, 154), (70, 78, 90))            # terra polit
    for y in range(116, H, 9):
        c.line([(0, y), (W, y)], (150, 160, 172))
    c.rect(0, 110, W, 113, (96, 104, 118))
    # Porta
    c.rect(5, 35, 49, 112, (90, 100, 114))
    c.hgrad(8, 38, 46, 112, [(0, STEEL[0]), (0.3, STEEL[2]), (1, STEEL[0])])
    # Foto del torn de nit
    c.rect(68, 28, 122, 72, (120, 90, 50))
    c.rect(71, 31, 119, 69, (210, 200, 176))
    for i, x in enumerate(range(76, 116, 9)):                       # el torn de nit, en fila
        c.ellipse(x, 42, x + 6, 48, (150, 130, 110)); c.rect(x, 48, x + 6, 62, (110, 100, 90))
    c.rect(94, 42, 100, 48, (60, 50, 50)); c.line([(93, 41), (101, 49)], (40, 30, 30)); c.line([(101, 41), (93, 49)], (40, 30, 30))  # la cara ratllada
    c.rect(104, 52, 112, 64, (176, 180, 186))                       # el Cargol, nou
    # Mapa de La Gavina
    c.rect(130, 24, 192, 72, (30, 40, 60))
    c.ellipse(140, 32, 182, 64, None, outline=(150, 200, 230))
    c.rect(156, 44, 166, 52, (150, 200, 230))
    for x in range(140, 184, 4):                                    # el conducte, en discontínua
        c.line([(x, 60), (x + 2, 60)], (240, 200, 80))
    c.px(160, 46, (250, 80, 80))                                    # «vostè és aquí»
    # Pedestal de l'holograma (la figura és un prop a part, però sempre hi és)
    c.ellipse(204, 104, 246, 116, (90, 100, 116))
    c.ellipse(208, 102, 242, 110, (130, 200, 240))
    c.glow(225, 80, 40, (120, 200, 255), 0.5)
    c.d.polygon([(214, 104), (236, 104), (232, 40), (218, 40)], fill=(150, 210, 240, 90))
    c.ellipse(218, 30, 232, 44, (170, 220, 245))
    c.rect(216, 46, 234, 84, (150, 210, 240))
    for y in range(32, 100, 3):                                     # línies d'escaneig
        c.line([(214, y), (236, y)], (200, 235, 255))
    # Vitrina buida
    c.rect(262, 92, 298, 112, (90, 96, 110))
    c.rect(264, 66, 296, 92, (200, 225, 240))
    c.d.rectangle([264, 66, 296, 92], outline=(240, 250, 255))
    c.rect(270, 94, 290, 98, (236, 230, 210))
    # Expositor de fullets
    c.rect(314, 76, 340, 112, (110, 116, 128))
    for y in (80, 90, 100):
        c.rect(317, y, 337, y + 7, (240, 220, 120)); c.ellipse(324, y + 1, 330, y + 6, (250, 220, 70))
    vignette(c, 70)


MEMORIA = {
    'era': 'vet',
    'things': {
        'porta_passadis': {'rect': (6, 34, 48, 114), 'walk': (34, 134)},
        'foto': {'rect': (66, 26, 124, 74), 'walk': (95, 128)},
        'mapa': {'rect': (128, 22, 194, 74), 'walk': (161, 128)},
        'holograma': {'rect': (204, 26, 246, 104), 'walk': (225, 136)},
        'socol': {'rect': (204, 104, 246, 116), 'walk': (225, 136)},
        'vitrina': {'rect': (260, 64, 300, 112), 'walk': (280, 132)},
        'fullets': {'rect': (312, 74, 342, 112), 'walk': (322, 132)},
    },
    'spawns': {'vet': (40, 138), 'cargol_vell': (180, 136)},
    'walkable': [(14, 118), (338, 118), (346, 148), (6, 148)],
    'bg': amb(memoria_bg, socol_holograma),
    'props': {'socol': nota_socol},
}



# ─── El pròleg: quatre pantalles sense res per clicar ───────────────────────
# Ocupen tota la imatge (sense barra de verbs). Les sales són `cutscene` al contingut.

def _estels(c, n, seed, y1=H):
    rnd = random.Random(seed)
    for _ in range(n):
        x, y = rnd.randint(0, W), rnd.randint(0, y1)
        b = rnd.randint(150, 255)
        c.px(x, y, (b, b, min(255, b + 20)))


def espai_gavina(c, cx=120, cy=70, tx=290, ty=250, vinyeta=True):
    """L'espai amb la Terra (centre tx, ty) i La Gavina (centre cx, cy)."""
    c.vgrad(0, 0, W, H, (4, 6, 16), (10, 16, 40))
    _estels(c, 90, 7)
    # La Terra, enorme, a baix a la dreta
    ox, oy = tx - 290, ty - 250
    T = lambda x0, y0, x1, y1: (x0 + ox, y0 + oy, x1 + ox, y1 + oy)
    c.glow(tx, ty, 150, (90, 150, 255), 0.6)
    c.ellipse(*T(170, 130, 410, 370), (36, 90, 190))
    c.ellipse(*T(200, 150, 260, 185), (70, 140, 80)); c.ellipse(*T(240, 170, 300, 200), (80, 150, 86))
    c.ellipse(*T(300, 145, 345, 165), (90, 156, 92)); c.ellipse(*T(320, 175, 352, 198), (70, 140, 80))
    c.ellipse(*T(215, 140, 250, 150), (232, 240, 255)); c.ellipse(*T(275, 160, 320, 170), (232, 240, 255))
    c.d.arc(list(T(170, 130, 410, 370)), 180, 360, fill=(160, 210, 255), width=2)
    # La Gavina: un cos central i dues ales de panells solars doblegades, com una gavina planant
    for sign in (-1, 1):
        colze = (cx + sign * 46, cy - 26)
        punta = (cx + sign * 96, cy - 8)
        interior = [(cx + sign * 10, cy - 4), colze, (colze[0] + sign * 4, colze[1] + 9), (cx + sign * 12, cy + 6)]
        exterior = [colze, punta, (punta[0] - sign * 2, punta[1] + 7), (colze[0] + sign * 4, colze[1] + 9)]
        for ala in (interior, exterior):
            c.d.polygon(ala, fill=(48, 66, 110), outline=(130, 160, 210))
        for k in range(1, 4):
            t = k / 4
            c.line([(cx + sign * (10 + 36 * t), cy - 4 - 22 * t), (cx + sign * (12 + 38 * t), cy + 6 - 19 * t)], (90, 120, 170))
            c.line([(colze[0] + sign * 50 * t, colze[1] + 18 * t), (colze[0] + sign * (4 + 44 * t), colze[1] + 9 + 4 * t)], (90, 120, 170))
    c.ellipse(cx - 14, cy - 9, cx + 14, cy + 9, (150, 160, 172))
    c.ellipse(cx - 14, cy - 9, cx + 14, cy + 1, (190, 198, 208))
    c.rect(cx - 2, cy + 8, cx + 2, cy + 18, (120, 128, 140))                  # el moll de càrrega
    for x in range(cx - 10, cx + 11, 4):
        c.px(x, cy + 2, (60, 66, 80))
    c.px(cx + 6, cy + 3, (255, 210, 120))                                      # una sola finestra encesa
    c.glow(cx + 6, cy + 3, 6, (255, 200, 120), 0.8)
    if vinyeta:
        vignette(c, 110)


def proleg_gavina_bg(c):
    espai_gavina(c)


def proleg_cella_bg(c):
    cella_bg(c)
    c.shade(0, 0, W, H, (6, 10, 30), 170)                                      # és de nit
    # La Vet dorm a la llitera
    c.ellipse(282, 92, 338, 108, (60, 40, 30))                                 # la manta
    c.ellipse(276, 88, 292, 100, (200, 196, 184))                              # el cabell platí
    # El panell vibra i fa llum
    c.glow(192, 75, 40, (110, 200, 255), 0.9)
    c.d.rectangle([176, 58, 208, 92], outline=(150, 220, 255))
    for i, x in enumerate((168, 214)):
        sx = -1 if i == 0 else 1
        for k in range(3):
            c.line([(x + sx * k * 4, 66 + k * 2), (x + sx * k * 4 + sx * 2, 70 + k * 2), (x + sx * k * 4, 74 + k * 2)], (150, 220, 255))
    vignette(c, 140)


def proleg_fabrica_bg(c):
    c.vgrad(0, 0, W, 120, (12, 10, 30), (54, 36, 54))
    _estels(c, 40, 12, 70)
    c.ellipse(286, 18, 300, 32, (236, 228, 200))                               # la lluna
    # Xemeneies i fum
    for x, top in ((70, 16), (104, 28), (250, 22)):
        c.rect(x, top, x + 12, 110, (70, 36, 30))
        c.rect(x - 2, top - 3, x + 14, top, (52, 28, 24))
        fum = Image.new('RGBA', c.img.size, (0, 0, 0, 0))
        fd = ScaledDraw(fum, c.k)
        for k in range(6):
            r, fx, fy = 5 + k * 3, x + 6 + k * 9, top - 8 - k * 8
            fd.ellipse([fx - r, fy - r * 0.7, fx + r, fy + r * 0.7], fill=(150, 140, 150, 120 - k * 16))
        c.img.alpha_composite(fum)
    # Les naus de la fàbrica
    bricks(c, 20, 60, 200, 120, (98, 46, 34), (60, 30, 24), seed=21)
    bricks(c, 200, 50, 340, 120, (90, 42, 32), (56, 28, 22), seed=22)
    c.d.polygon([(20, 60), (110, 36), (200, 60)], fill=(40, 30, 34))
    c.d.polygon([(200, 50), (270, 30), (340, 50)], fill=(40, 30, 34))
    for row, y in enumerate((72, 92)):
        for x in range(30, 196, 18):
            lit = (x // 18 + row) % 3 != 0
            c.rect(x, y, x + 9, y + 10, (250, 200, 110) if lit else (40, 30, 34))
        for x in range(210, 336, 18):
            lit = (x // 18 + row) % 4 != 1
            c.rect(x, y - 6, x + 9, y + 4, (250, 200, 110) if lit else (40, 30, 34))
    c.glow(176, 100, 40, (255, 190, 100), 0.35)
    c.rect(150, 26, 230, 34, (30, 22, 24))                                     # el rètol
    c.rect(152, 28, 228, 32, (200, 150, 70))
    # El canal, amb el reflex de les finestres
    c.vgrad(0, 120, W, H, (18, 22, 40), (6, 8, 18))
    rnd = random.Random(5)
    for _ in range(60):
        x, y = rnd.randint(20, 340), rnd.randint(124, 190)
        c.line([(x, y), (x + rnd.randint(3, 10), y)], (120, 100, 70) if x < 340 else (60, 70, 90))
    vignette(c, 120)


def proleg_cambra_bg(c):
    cambra_bg(c)
    c.shade(0, 0, W, H, (10, 4, 6), 150)
    c.shade(0, 0, W, H, (255, 20, 20), 40)                                     # tot vermell d'alarma
    c.glow(190, 60, 110, (255, 30, 30), 1.0)                                   # l'alarma
    c.glow(190, 60, 50, (255, 120, 80), 0.8)
    c.ellipse(184, 2, 196, 10, (255, 60, 50))                                  # el llum giratori
    c.glow(190, 6, 24, (255, 80, 60), 0.9)
    vignette(c, 150)


def _proleg(bg, era):
    return {'era': era, 'things': {}, 'spawns': {}, 'walkable': [(150, 190), (200, 190), (200, 196), (150, 196)],
            'bg': bg, 'props': {}}


PROLEG_GAVINA = _proleg(proleg_gavina_bg, 'vet')
PROLEG_CELLA = _proleg(proleg_cella_bg, 'vet')
PROLEG_FABRICA = _proleg(proleg_fabrica_bg, 'iri')
PROLEG_CAMBRA = _proleg(proleg_cambra_bg, 'iri')



# ─── Finals: pantalles de cinemàtica (l'art és a hd/rooms/final_*.py) ───────

def final_bg(c):
    c.rect(0, 0, W, H, (0, 0, 0))


FINALS = {f'final_{nom}': _proleg(final_bg, 'vet') for nom in ('llancadora', 'museu', 'anell', 'estacio', 'cargol', 'nota')}
FINALS['credits'] = _proleg(final_bg, 'vet')                     # els crèdits (art: hd/rooms/credits.py)


# ─── Portada: la fàbrica i La Gavina, partides en diagonal, i el títol ──────

# Lletres de 5×7 per al títol (1 = píxel ple).
LLETRES = {
    'F': ['11111', '10000', '10000', '11110', '10000', '10000', '10000'],
    'E': ['11111', '10000', '10000', '11110', '10000', '10000', '11111'],
    'R': ['11110', '10001', '10001', '11110', '10100', '10010', '10001'],
    'O': ['01110', '10001', '10001', '10001', '10001', '10001', '01110'],
    '-': ['00000', '00000', '00000', '11111', '00000', '00000', '00000'],
    '9': ['01110', '10001', '10001', '01111', '00001', '00010', '01100'],
}


def titol(c, text, cx, y, mida):
    """Un títol en lletres de píxel grosses, de metall (ferro-9 que no s'oxida), amb ombra."""
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


def portada_bg(c):
    w, h = c.img.size
    fabrica = Image.new('RGBA', (w, h), (0, 0, 0, 255))
    proleg_fabrica_bg(C(fabrica, c.k))
    espai_gavina(c, cx=262, cy=104, tx=360, ty=260, vinyeta=False)
    tall = Image.new('L', (w, h), 0)
    ImageDraw.Draw(tall).polygon([(0, 0), (round(200 * c.k), 0), (round(150 * c.k), h), (0, h)], fill=255)
    c.img.paste(fabrica, (0, 0), tall)
    c.line([(200, 0), (150, H)], (235, 235, 245), 1)
    c.shade(0, 0, W, H, (0, 0, 0), 60)
    titol(c, 'FERRO-9', W / 2, 16, 5)
    vignette(c, 120)


PORTADA = {'era': 'vet', 'things': {}, 'spawns': {}, 'walkable': [(150, 190), (200, 190), (200, 196), (150, 196)],
           'bg': portada_bg, 'props': {}}


DESIGNS = {
    'fabrica_calderes': CALDERES,
    'fabrica_magatzem': MAGATZEM,
    'fabrica_cambra': CAMBRA,
    'gavina_cella': CELLA,
    'gavina_passadis': PASSADIS,
    'fabrica_moll': MOLL,
    'gavina_hangar': HANGAR,
    'fabrica_despatx': DESPATX,
    'gavina_arxiu': ARXIU,
    'gavina_memoria': MEMORIA,
    'proleg_gavina': PROLEG_GAVINA,
    'proleg_cella': PROLEG_CELLA,
    'proleg_fabrica': PROLEG_FABRICA,
    'proleg_cambra': PROLEG_CAMBRA,
    'portada': PORTADA,
    **FINALS,
}
