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

Coordenades de disseny = píxels del joc, 640×360 (escala.py); les sales es pinten fins a y = 260
(a sota, la franja del HUD: hd640/pantalla.py).
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
    'G': ['01110', '10001', '10000', '10111', '10001', '10001', '01111'],
    'B': ['11110', '10001', '10001', '11110', '10001', '10001', '11110'],
    'T': ['11111', '00100', '00100', '00100', '00100', '00100', '00100'],
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



# ─── Sales de L'Última Arrel (provisionals, Fase 0) ────────────────────────
from hd.pix import hr  # noqa: E402,F401


def dark(col, k=0.55):
    return tuple(int(v * k) for v in col)


def obj(c, x0, y0, x1, y1, col, edge=None):
    """Capsa plena amb contorn fosc i una mica de llum a dalt."""
    c.rect(x0, y0, x1, y1, col)
    c.rect(x0 + 1, y0 + 1, x1 - 1, y0 + 2, tuple(min(255, int(v * 1.25)) for v in col))
    outline_rect(c, x0, y0, x1, y1, edge or dark(col, 0.4))


def door(c, x0, y0, x1, y1, col, knob=(200, 180, 120)):
    obj(c, x0, y0, x1, y1, col)
    c.rect(x0 + 4, y0 + 4, x1 - 4, (y0 + y1) // 2 - 2, dark(col, 0.85))
    c.rect(x0 + 4, (y0 + y1) // 2 + 2, x1 - 4, y1 - 4, dark(col, 0.85))
    c.ellipse(x1 - 9, (y0 + y1) // 2 - 2, x1 - 5, (y0 + y1) // 2 + 2, knob)


# Coordenades de 640×360. Les sales són pintades fins a y = 260 (pantalla.py: a sota, la franja del HUD).
TERRA_Y = 196                                     # on comença el terra
WALK = [(16, 212), (624, 212), (632, 252), (8, 252)]

# Paletes (paret de dalt, paret de baix, terra) de cada mena de sala.
BOSC = ((48, 40, 74), (150, 92, 70), (52, 70, 40))          # capvespre a la vora del bosc
COVA = ((20, 26, 24), (46, 52, 44), (58, 46, 34))           # entre arrels
BRANCA = ((150, 190, 210), (200, 210, 190), (96, 70, 44))   # a trenc d'alba, dalt del roure
FANG = ((170, 180, 170), (190, 180, 140), (120, 100, 70))   # aiguamoll sec
CASETA = ((214, 218, 220), (190, 196, 198), (150, 152, 150))
CLAR = ((150, 196, 220), (196, 214, 200), (96, 110, 70))    # clar del bosc, de dia
OBERT = ((120, 176, 210), (170, 196, 170), (60, 90, 48))

COL = {'porta': (120, 84, 50), 'escala': (130, 100, 60), 'fusta': (140, 100, 62), 'metall': (150, 156, 160),
       'blanc': (226, 226, 220), 'vermell': (190, 50, 40), 'turquesa': (60, 200, 190), 'verd': (70, 130, 70),
       'groc': (220, 180, 60), 'rosa': (240, 90, 170), 'paper': (236, 228, 200), 'pantalla': (60, 160, 130)}


def T(x0, y0, x1, y1, wx=None, wy=232):
    """Una cosa clicable: el rectangle i on s'hi atura la protagonista."""
    return {'rect': (x0, y0, x1, y1), 'walk': (wx if wx is not None else (x0 + x1) // 2, wy)}


def design(zona, things, spawns, colors=None, walkable=None):
    """Un disseny provisional: paret i terra de la zona, i cada cosa com una capsa del seu color (les portes i les
    escales, com a portes). `colors`: id → color (si no, segons el nom)."""
    colors = colors or {}

    def col(tid):
        if tid in colors:
            return COL.get(colors[tid], colors[tid]) if isinstance(colors[tid], str) else colors[tid]
        for k in ('porta', 'escala'):
            if tid.startswith(k):
                return COL[k]
        return (130, 120, 104)

    def bg(c):
        top, bot, floor = zona
        c.vgrad(0, 0, W, TERRA_Y, top, bot)
        c.rect(0, TERRA_Y - 4, W, TERRA_Y, dark(bot, 0.6))
        c.vgrad(0, TERRA_Y + 1, W, 260, floor, dark(floor, 0.6))
        c.rect(0, 261, W, H, (0, 0, 0))
        for tid, t in things.items():
            x0, y0, x1, y1 = t['rect']
            (door if tid.startswith(('porta', 'escala')) else obj)(c, x0, y0, x1, y1, col(tid))

    return {'era': '', 'things': things, 'spawns': spawns, 'walkable': walkable or WALK, 'bg': bg, 'props': {}}


DESIGNS = {
    'vora_bosc': design(BOSC, {
        'porta_roure': T(96, 150, 128, 206, wy=226),
        'cartell': T(380, 70, 500, 130),
        'tanca': T(360, 140, 510, 200),
        'excavadora': T(520, 100, 620, 200, wx=570),
    }, {'iri': (200, 236)}, colors={'cartell': 'blanc', 'tanca': 'metall', 'excavadora': 'groc'}),
    'centraleta': design(COVA, {
        'escala': T(40, 40, 76, 206, wy=226),
        'tauler': T(400, 90, 560, 180, wx=480),
        'radar': T(440, 40, 520, 86, wx=480),
        'corn': T(280, 110, 320, 170),
    }, {'iri': (200, 236), 'espora': (360, 230)}, colors={'tauler': 'fusta', 'radar': 'pantalla', 'corn': 'fusta'}),
    'campament_fades': design(BRANCA, {
        'gronxador': T(330, 60, 380, 170),
        'flor_pebre': T(560, 40, 610, 90, wx=520),
        'diana': T(80, 70, 150, 140),
    }, {'vet': (220, 238), 'urtica': (420, 230), 'pica': (470, 232), 'card': (520, 228)},
        colors={'gronxador': 'rosa', 'flor_pebre': 'vermell', 'diana': 'blanc'}),
    'toll_gripaus': design(FANG, {
        'arxiu': T(240, 90, 340, 200),
        'rierol': T(480, 60, 600, 150, wx=540),
        'comporta': T(560, 150, 620, 200, wx=580),
    }, {'iri': (140, 236), 'bufo': (300, 228), 'gripau': (400, 232)},
        colors={'arxiu': 'fusta', 'rierol': (90, 140, 180), 'comporta': 'metall'}),
    'caseta_obra': design(CASETA, {
        'altaveu': T(470, 120, 540, 200),
        'arbre_wifi': T(580, 90, 620, 200, wx=590),
        'maqueta': T(60, 140, 200, 196),
    }, {'vet': (300, 236), 'pla': (390, 230)}, colors={'altaveu': (40, 40, 46), 'arbre_wifi': 'verd', 'maqueta': 'paper'}),
    'zona_zero': design(CLAR, {
        'sensors': T(460, 110, 540, 200),
        'pantalla': T(250, 30, 410, 110, wx=330),
        'formigonera': T(40, 100, 160, 196),
    }, {'iri': (300, 238), 'txell': (580, 232)}, colors={'sensors': 'blanc', 'pantalla': 'pantalla', 'formigonera': 'groc'}),
    'bosc_obert': design(OBERT, {
        'taula': T(300, 170, 400, 206, wy=232),
        'porta_oberta': T(96, 150, 128, 206, wy=226),
        'bolets': T(150, 186, 220, 206),
    }, {'vet': (480, 238), 'avia': (420, 230)}, colors={'taula': 'fusta', 'porta_oberta': 'turquesa', 'bolets': 'turquesa'}),
}


# Una sala amb art definitiu (hd/rooms/<sala>.py) pot portar la seva geometria (`GEOMETRIA`: `things`, `spawns`,
# `walkable`): així el dibuix i el que es clica són al mateix fitxer, i substitueix la d'aquí.

def _escala_disseny(d, k):
    """Passa la geometria d'un disseny fet a 480×270 a k vegades (×4/3 a 640×360)."""
    r = lambda v: round(v * k)  # noqa: E731
    for t in d.get('things', {}).values():
        if 'rect' in t:
            x0, y0, x1, y1 = t['rect']
            t['rect'] = (r(x0), r(y0), r(x1 + 1) - 1, r(y1 + 1) - 1)
        if 'walk' in t:
            t['walk'] = tuple(r(v) for v in t['walk'])
    if 'spawns' in d:
        d['spawns'] = {c: tuple(r(v) for v in xy) for c, xy in d['spawns'].items()}
    if 'walkable' in d:
        d['walkable'] = [tuple(r(v) for v in xy) for xy in d['walkable']]


def _amb_geometria():
    """Les sales amb art definitiu a hd640/rooms/<sala>.py, amb la seva GEOMETRIA (a 640×360)."""
    import importlib
    from pathlib import Path as _P
    rooms = _P(__file__).resolve().parent / 'hd640' / 'rooms'
    for f in sorted(rooms.glob('*.py')):
        if f.stem.startswith('_') or f.stem.endswith('_comu'):
            continue
        geo = getattr(importlib.import_module(f'hd640.rooms.{f.stem}'), 'GEOMETRIA', None)
        if geo is None:
            continue
        DESIGNS[f.stem] = {'things': dict(geo.get('things', {})), 'spawns': dict(geo.get('spawns', {})),
                           'walkable': list(geo.get('walkable') or [(0, 250), (639, 250), (639, 258), (0, 258)]),
                           'regions': list(geo.get('regions', [])),
                           'forats': list(geo.get('forats', [])),
                           'characterShadow': geo.get('characterShadow'),
                           'characterOutline': geo.get('characterOutline'),
                           'characterLights': geo.get('characterLights'),
                           'floorSquash': geo.get('floorSquash'),
                           'bg': lambda c: None, 'props': {}, 'etiquetes': False}


_amb_geometria()
