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



# ─── Sales d'Aigua bruta ────────────────────────────────────────────────────
from hd.pix import hr  # noqa: E402

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


# Paletes per zona: a baix, verd de sala de màquines; la coberta principal, crema i fusta; el pont, blau;
# a fora, el mar (de nit, per defecte; de dia, el decorat `dia`).
BAIX = ((70, 92, 80), (46, 62, 56), (52, 56, 60))
PRINCIPAL = ((196, 186, 160), (164, 152, 128), (110, 84, 60))
PONT = ((120, 138, 160), (92, 108, 128), (64, 66, 74))
NIT = ((14, 22, 46), (22, 34, 62), (58, 62, 70))
DIPOSIT = ((60, 66, 70), (40, 44, 48), (34, 38, 42))

COL = {'porta': (120, 104, 80), 'metall': (110, 120, 130), 'vermell': (170, 50, 40), 'groc': (210, 170, 60),
       'blanc': (220, 220, 214), 'fusta': (140, 100, 62), 'paper': (236, 228, 200), 'pantalla': (60, 160, 130),
       'llauto': (196, 150, 60), 'taronja': (220, 120, 40), 'fosc': (30, 30, 36), 'verd': (60, 120, 70)}


def exterior_bg(c):
    c.vgrad(0, 0, W, 112, (8, 12, 30), (24, 36, 66))
    c.vgrad(0, 112, W, 150, (16, 30, 54), (10, 20, 40))
    for x in range(0, W, 23):
        c.px(x + hr(x) % 11, 60 + hr(x * 3) % 40, (200, 210, 230))
    c.rect(0, 150, W, H, (70, 70, 74))
    c.vgrad(0, 150, W, H, (82, 80, 78), (46, 46, 50))
    c.rect(0, 146, W, 150, (150, 40, 34))


def dia(c):
    """De dia (Escena 2): cel pàl·lid de febrer i mar gris."""
    c.vgrad(0, 0, W, 112, (150, 176, 196), (210, 220, 224))
    c.vgrad(0, 112, W, 146, (90, 110, 120), (70, 88, 98))
    c.rect(0, 146, W, 150, (180, 50, 40))
    c.vgrad(0, 150, W, H, (150, 146, 136), (96, 94, 90))


def design(zona, things, spawns, colors=None, props=None, decor=None, walkable=None, bg_extra=None, exterior=False, cond=None):
    """Un disseny provisional: la paret i el terra de la zona, cada cosa dibuixada com una capsa del seu color,
    les portes com a portes. `colors`: id → color (si no, segons el nom)."""
    colors = colors or {}

    def col(tid):
        if tid in colors:
            return colors[tid]
        for k, v in (('porta', COL['porta']), ('escala', COL['metall']), ('escotilla', COL['metall']), ('boca', COL['llauto']),
                     ('munta', COL['metall']), ('safata', COL['paper'])):
            if tid.startswith(k):
                return v
        return (130, 120, 104)

    pr = {}
    for tid in (cond or PROPS_COND):
        if tid in things:
            x0, y0, x1, y1 = things[tid]['rect']
            pr[tid] = (lambda c, r=(x0, y0, x1, y1), cc=col(tid): obj(c, *r, cc))
    pr.update(props or {})
    pr.update(decor or {})
    def bg(c, de_dia=False):
        if de_dia:
            dia(c)
        elif exterior:
            exterior_bg(c)
        else:
            top, bot, floor = zona
            room_base(c, top, bot, floor)
        if bg_extra:
            bg_extra(c)
        for tid, t in things.items():
            if tid in pr:
                continue
            x0, y0, x1, y1 = t['rect']
            if tid.startswith('porta') or tid.startswith('escala'):
                door(c, x0, y0, x1, y1, col(tid))
            else:
                obj(c, x0, y0, x1, y1, col(tid))

    if (decor or {}).get('dia') is dia:
        pr['dia'] = lambda c: bg(c, de_dia=True)
    return {'era': '', 'things': things, 'spawns': spawns, 'walkable': walkable or WALK_STD, 'bg': bg, 'props': pr}


# Coses amb `visibleIf` (són props: es dibuixen a part, perquè es vegin o no).
PROPS_COND = ('cisalla', 'clau_tubs', 'safata', 'nota', 'llibre', 'llanterna', 'cable', 'manta', 'plataforma', 'horitzo', 'portatil')


def T(x0, y0, x1, y1, wx=None, wy=186):
    return {'rect': (x0, y0, x1, y1), 'walk': (wx if wx is not None else (x0 + x1) // 2, wy)}


def shade_all(alpha=150):
    def f(c):
        c.shade(0, 0, W, H, (0, 4, 12), alpha)
    return f


def water(c):
    """Dos dits d'aigua a terra."""
    c.shade(0, 156, W, 205, (40, 90, 110), 120)
    for x in range(0, W, 17):
        c.line([(x, 170 + hr(x) % 30), (x + 8, 170 + hr(x) % 30)], (140, 190, 210))


PROTA = {'iri': (230, 192), 'vet': (300, 196)}

DESIGNS = {
    'camarot_iri': design(BAIX, {
        'porta': T(400, 50, 460, 150), 'llitera': T(20, 118, 170, 158), 'carregador': T(176, 112, 206, 136),
        'motxilla': T(220, 128, 262, 160), 'ull_de_bou': T(290, 50, 330, 90)}, {'iri': (300, 192), 'vet': (360, 196)},
        colors={'llitera': (90, 110, 150), 'carregador': COL['fosc'], 'motxilla': (60, 90, 60), 'ull_de_bou': (20, 30, 60)}),
    'passadis_baix': design(BAIX, {
        'porta_camarot': T(20, 50, 70, 150), 'porta_maquines': T(110, 50, 170, 150), 'porta_pallol': T(210, 50, 260, 150),
        'escotilla': T(300, 168, 360, 186, wy=192), 'escala': T(400, 30, 460, 150)}, {'iri': (240, 192), 'vet': (330, 196)}),
    'sala_maquines': design(BAIX, {
        'porta_passadis': T(6, 64, 50, 150), 'boca': T(56, 90, 74, 114), 'motor': T(80, 84, 200, 148),
        'porta_rebost': T(206, 64, 250, 150), 'sensor': T(256, 96, 272, 116), 'valvula': T(256, 130, 294, 162, wy=190),
        'quadre': T(300, 70, 350, 140), 'generador': T(300, 30, 350, 66), 'vies': T(354, 118, 374, 146),
        'separador': T(378, 70, 418, 150), 'porta_taller': T(424, 64, 474, 150), 'sentina': T(130, 168, 190, 186, wy=194)},
        {'iri': (230, 192), 'vet': (330, 196), 'bastida': (110, 190), 'diu': (150, 84)},
        colors={'motor': (60, 80, 100), 'valvula': COL['vermell'], 'quadre': (70, 74, 80), 'vies': COL['groc'],
                'separador': (190, 180, 130), 'sensor': COL['vermell'], 'generador': (90, 96, 100), 'sentina': COL['fosc']},
        decor={'aigua': water, 'valvula_tancada': lambda c: obj(c, 262, 122, 290, 130, COL['metall']),
               'brida': lambda c: c.rect(318, 100, 332, 104, COL['blanc']), 'fosc': shade_all()}),
    'taller': design(BAIX, {
        'porta': T(8, 64, 52, 150), 'tauler': T(100, 30, 320, 60), 'cisalla': T(120, 66, 170, 96), 'clau_tubs': T(200, 66, 260, 96),
        'banc': T(320, 110, 460, 150)}, PROTA, colors={'tauler': (120, 100, 70), 'cisalla': COL['vermell'], 'clau_tubs': COL['metall'], 'banc': COL['fusta']}),
    'rebost': design(BAIX, {
        'porta': T(8, 64, 52, 150), 'munta': T(180, 50, 250, 104), 'safata': T(184, 108, 246, 126), 'prestatges': T(300, 40, 460, 140),
        'registre': T(80, 162, 150, 186, wy=194)}, {'iri': (260, 192), 'vet': (330, 196)},
        colors={'prestatges': COL['fusta'], 'registre': COL['metall']}),
    'diposit2': design(DIPOSIT, {
        'registre': T(190, 30, 250, 70), 'filtre': T(300, 90, 360, 150), 'cartell': T(60, 60, 140, 90)},
        {'iri': (200, 192), 'vet': (260, 194)}, colors={'filtre': COL['metall'], 'cartell': COL['paper']}),
    'pallol': design(BAIX, {
        'porta': T(8, 64, 52, 150), 'prestatges': T(80, 40, 250, 140), 'inventari': T(60, 40, 76, 60)},
        {'iri': (260, 192), 'vet': (300, 196), 'marcel': (390, 190), 'diu': (340, 186)},
        colors={'prestatges': COL['fusta'], 'inventari': COL['paper']}),
    'sala_bombes': design(DIPOSIT, {
        'escotilla': T(200, 20, 260, 60), 'llibre': T(150, 172, 186, 186, wy=194), 'llanterna': T(210, 174, 240, 186, wy=194),
        'bombes': T(280, 70, 470, 150)}, {'iri': (230, 192), 'vet': (300, 196)},
        colors={'llibre': (120, 60, 50), 'llanterna': COL['groc'], 'bombes': COL['verd']}),
    'passadis': design(PRINCIPAL, {
        'porta_menjador': T(6, 60, 50, 150), 'porta_infermeria': T(80, 60, 130, 150), 'porta_laboratori': T(150, 60, 200, 150),
        'porta_capitana': T(220, 60, 270, 150), 'escala_amunt': T(290, 40, 340, 150), 'escala_avall': T(350, 162, 410, 186, wy=194),
        'porta_proa': T(430, 60, 474, 150)}, {'iri': (240, 192), 'vet': (300, 196)}),
    'menjador': design(PRINCIPAL, {
        'porta_passadis': T(430, 60, 474, 150), 'porta_cuina': T(190, 60, 240, 140), 'passaplats': T(250, 80, 300, 110),
        'porta_popa': T(6, 60, 50, 150), 'poster': T(330, 40, 380, 100), 'taula': T(100, 150, 380, 172, wy=192)},
        {'iri': (420, 196), 'vet': (240, 198), 'capitana': (130, 152), 'bastida': (180, 152), 'marcel': (230, 152),
         'tomas': (290, 152), 'juana': (340, 152), 'nadia': (390, 152)},
        colors={'passaplats': (90, 70, 50), 'poster': (60, 140, 160), 'taula': COL['fusta']}),
    'cuina': design(PRINCIPAL, {
        'porta': T(6, 60, 50, 150), 'munta': T(100, 50, 160, 110), 'safata': T(104, 112, 156, 128), 'boca': T(170, 70, 188, 96),
        'cambra_freda': T(200, 40, 270, 150), 'armari': T(290, 70, 350, 150), 'forn': T(370, 90, 440, 150)},
        {'vet': (150, 195), 'iri': (330, 196), 'tomas': (410, 190), 'nadia': (240, 186)},
        colors={'cambra_freda': COL['blanc'], 'armari': COL['fusta'], 'forn': COL['fosc']},
        decor={'armari_obert': lambda c: obj(c, 294, 74, 346, 146, (40, 30, 24))}),
    'infermeria': design(PRINCIPAL, {
        'porta': T(6, 60, 50, 150), 'boca': T(56, 80, 72, 104), 'armari': T(90, 40, 150, 140), 'fitxes': T(160, 80, 210, 120),
        'llitera': T(220, 122, 400, 160, wy=190), 'cafetera': T(420, 90, 450, 120)},
        {'vet': (160, 195), 'iri': (420, 196), 'capitana': (300, 182), 'tomas': (300, 182), 'nadia': (300, 182),
         'marcel': (300, 182), 'bastida': (300, 182), 'juana': (300, 170)},
        colors={'armari': COL['blanc'], 'fitxes': COL['paper'], 'llitera': (120, 150, 160), 'cafetera': COL['fosc']}),
    'laboratori': design(PRINCIPAL, {
        'porta': T(6, 60, 50, 150), 'llibre': T(140, 100, 190, 124), 'portatil': T(200, 100, 250, 124), 'nota': T(256, 108, 280, 122),
        'taulell': T(120, 126, 330, 150), 'nevera': T(360, 50, 440, 150)}, PROTA,
        colors={'llibre': (60, 100, 140), 'portatil': COL['fosc'], 'nota': COL['paper'], 'taulell': COL['blanc'], 'nevera': COL['blanc']},
        decor={'remenat': lambda c: [obj(c, 130 + i * 40, 128, 150 + i * 40, 134, COL['paper']) for i in range(4)]},
        cond=('portatil', 'nota')),
    'cabina_capitana': design(PRINCIPAL, {
        'porta': T(6, 60, 50, 150), 'contracte': T(200, 112, 250, 126), 'novella': T(260, 112, 290, 126), 'carta': T(330, 40, 450, 100)},
        {'iri': (150, 194), 'vet': (190, 196), 'capitana': (300, 190)},
        colors={'contracte': COL['paper'], 'novella': (180, 60, 90), 'carta': (200, 190, 150)},
        bg_extra=lambda c: obj(c, 180, 126, 320, 150, COL['fusta'])),
    'pont': design(PONT, {
        'escala': T(6, 64, 50, 150), 'porta_radio': T(60, 56, 104, 150), 'vidre': T(110, 30, 370, 100), 'timo': T(220, 110, 260, 150),
        'terminal': T(280, 100, 330, 140), 'impressora': T(336, 116, 370, 140), 'munta': T(380, 60, 430, 110),
        'safata': T(384, 112, 426, 126), 'boca': T(436, 70, 452, 96), 'escala_pal': T(456, 40, 476, 150)},
        {'iri': (300, 192), 'vet': (200, 196), 'capitana': (240, 190)},
        colors={'vidre': (20, 30, 60), 'timo': COL['fusta'], 'terminal': COL['pantalla'], 'impressora': COL['blanc']},
        decor={'guardacostes': lambda c: [c.ellipse(300 + i * 12, 66, 304 + i * 12, 70, (255, 80, 60)) for i in range(2)],
               'fosc': shade_all()}),
    'sala_radio': design(PONT, {
        'porta': T(6, 64, 50, 150), 'radio': T(150, 60, 300, 130), 'panell': T(320, 60, 400, 140), 'cable': T(334, 90, 386, 120)},
        {'iri': (300, 192), 'vet': (200, 196), 'bastida': (30, 190)},
        colors={'radio': (60, 64, 70), 'panell': COL['metall'], 'cable': COL['taronja']},
        decor={'panell_obert': lambda c: obj(c, 324, 64, 396, 136, (30, 30, 34)),
               'panell_reparat': lambda c: obj(c, 356, 76, 364, 104, (150, 152, 156))}),
    'pal': design(NIT, {
        'escala': T(200, 172, 260, 200, wy=196), 'antena': T(190, 30, 300, 110), 'mar': T(20, 40, 150, 140)},
        {'iri': (240, 190), 'vet': (280, 194), 'marcel': (330, 190)}, exterior=True,
        colors={'antena': (200, 200, 210), 'mar': (20, 40, 70)}),
    'coberta_popa': design(NIT, {
        'porta': T(400, 60, 450, 150), 'proa': T(452, 40, 476, 190, wx=464), 'grua': T(20, 20, 140, 150), 'borda': T(150, 120, 300, 150),
        'plataforma': T(200, 60, 280, 110), 'horitzo': T(160, 70, 330, 110), 'taula': T(300, 150, 380, 176, wy=192)},
        {'iri': (230, 195), 'vet': (130, 196), 'bastida': (180, 182), 'capitana': (320, 170), 'marcel': (360, 192),
         'nadia': (280, 192), 'tomas': (392, 178)}, exterior=True,
        colors={'grua': (200, 170, 60), 'borda': (150, 40, 34), 'plataforma': (90, 90, 96), 'horitzo': (30, 40, 70), 'taula': COL['fusta']},
        decor={'dia': dia}, cond=PROPS_COND + ('taula',)),
    'coberta_proa': design(NIT, {
        'popa': T(4, 40, 28, 190, wx=16), 'porta': T(40, 60, 90, 150), 'molinet': T(140, 130, 200, 160), 'escotilla': T(220, 162, 280, 186, wy=194),
        'balsa': T(300, 60, 420, 120)}, {'iri': (240, 195), 'vet': (180, 196), 'juana': (360, 172)}, exterior=True,
        colors={'molinet': COL['metall'], 'escotilla': COL['metall'], 'balsa': COL['blanc']},
        decor={'dia': dia, 'cadenat': lambda c: obj(c, 244, 168, 256, 178, COL['groc'])}),
    'caixa_cadenes': design(DIPOSIT, {
        'escotilla': T(210, 20, 270, 60), 'cadenes': T(60, 80, 180, 180), 'manta': T(260, 172, 340, 186, wy=194)},
        {'iri': (220, 192), 'vet': (180, 196), 'juana': (300, 180)},
        colors={'cadenes': (90, 60, 40), 'manta': (140, 60, 60)}),
}


def cine(bg, spawns=None):
    d = cinematica(bg)
    if spawns:
        d['spawns'] = spawns
    return d


def cinematica(bg):
    return {'era': '', 'things': {}, 'spawns': {}, 'walkable': [(150, 190), (200, 190), (200, 196), (150, 196)],
            'bg': bg, 'props': {}, 'etiquetes': False}


def proleg_bg(c):
    exterior_bg(c)
    obj(c, 300, 70, 440, 118, (70, 70, 80))                               # la plataforma
    c.rect(330, 84, 380, 92, (200, 200, 190))                            # la cinta americana
    obj(c, 180, 150, 280, 168, (60, 60, 64))                             # la zòdiac


def galway_bg(c):
    c.vgrad(0, 0, W, 120, (240, 180, 120), (180, 200, 220))
    c.vgrad(0, 120, W, 150, (90, 120, 140), (60, 90, 110))
    obj(c, 300, 40, 420, 140, (70, 80, 90))                              # l'Arenga, amarrada
    c.rect(358, 10, 362, 40, (90, 90, 90))                               # el pal
    obj(c, 0, 150, W, 205, (120, 90, 60))                                # la terrassa
    obj(c, 400, 96, 460, 140, (40, 40, 44))                              # la tele


def portada_bg(c):
    exterior_bg(c)
    titol(c, 'AIGUA BRUTA', W // 2, 50, 4)


DESIGNS.update({
    'proleg_punt7': cine(proleg_bg, {'juana': (230, 150), 'bastida': (90, 150)}),
    'portada': cine(portada_bg),
    'final_galway': dict(cine(galway_bg, {'iri': (200, 190), 'vet': (250, 190), 'diu': (225, 160), 'nadia': (110, 190),
                                          'capitana': (150, 190), 'marcel': (300, 190), 'tomas': (340, 190)}),
                         props={'tele_apagada': lambda c: obj(c, 404, 100, 456, 136, (10, 10, 12))}),
    'credits': cine(lambda c: c.rect(0, 0, W, H, (6, 10, 20))),
    'postcredits': cine(lambda c: (c.rect(0, 0, W, H, (6, 10, 20)), obj(c, 200, 60, 280, 190, (30, 30, 34)), obj(c, 206, 70, 274, 170, (220, 210, 200)))),
})


# ─── Geometria de l'art definitiu ───────────────────────────────────────────
# Una sala amb art definitiu (hd/rooms/<sala>.py) pot portar la seva geometria (`GEOMETRIA`: `things`, `spawns`,
# `walkable`): així el dibuix i el que es clica són al mateix fitxer, i substitueix la d'aquí.

def _amb_geometria():
    import importlib
    from pathlib import Path as _P
    rooms = _P(__file__).resolve().parent / 'hd' / 'rooms'
    for name, d in DESIGNS.items():
        if not (rooms / f'{name}.py').exists():
            continue
        geo = getattr(importlib.import_module(f'hd.rooms.{name}'), 'GEOMETRIA', None)
        if not geo:
            continue
        for key in ('things', 'spawns', 'walkable'):
            if key in geo:
                d[key] = {**d[key], **geo[key]} if isinstance(d[key], dict) else geo[key]


_amb_geometria()
