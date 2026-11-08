#!/usr/bin/env python3
"""
Dibuixa els sprites provisionals dels personatges de Ferro-9, en pixel art, amb el format
que espera Benne (full d'Aseprite PNG + JSON amb etiquetes, i el .character.json):

  iri      enginyera del torn de nit (passat): bata blanca oberta, trena fosca, ulleres al front
  vet      presonera de la cel·la 9 (present): granota de presó taronja, bob platí
  cargol   robot de manteniment amb closca de cargol, ulls a les antenes, erugues
  capatas  el capatàs Pruna, adormit a la cadira, amb el segell a les mans (i sense)
  mos     presoner vell i prim, maquillat
  mare     l'altaveu en forma de cor de la IA (normalment invisible)

Les protagonistes tenen Idle/Walk/Talk en tres direccions (L, D, U; Benne fa el mirall per a R).
Surt a adapters/benne/placeholder-art/<id>/. Ús: python3 draw_characters.py
"""
import json
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from escala import SCALE, box, pt  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / 'placeholder-art'
OUTLINE = (34, 24, 30, 255)
CLEAR = (0, 0, 0, 0)


def rgba(c):
    return c if len(c) == 4 else (*c, 255)


class Canvas:
    """Llenç amb coordenades de disseny (les de sempre, p. ex. 36×64) que es rasteritza a l'escala
    del joc: rectangles i el·lipses es tornen a rasteritzar a la mida real, i el contorn és d'un píxel real."""

    def __init__(self, w, h, k=SCALE):
        self.k = k
        self.w, self.h = round(w * k), round(h * k)
        self.img = Image.new('RGBA', (self.w, self.h), CLEAR)

    def rpx(self, x, y, c):
        """Un píxel real (per als detalls que només caben a la resolució gran)."""
        if 0 <= x < self.w and 0 <= y < self.h:
            self.img.putpixel((x, y), rgba(c))

    def rrect(self, x0, y0, x1, y1, c):
        for y in range(max(0, y0), min(self.h - 1, y1) + 1):
            for x in range(max(0, x0), min(self.w - 1, x1) + 1):
                self.img.putpixel((x, y), rgba(c))

    def px(self, x, y, c):
        self.rect(x, y, x, y, c)

    def rect(self, x0, y0, x1, y1, c):
        self.rrect(*box(x0, y0, x1, y1, self.k), c)

    def ellipse(self, cx, cy, rx, ry, c):
        k = self.k
        for y in range(max(0, int((cy - ry - 1) * k)), min(self.h, int((cy + ry + 2) * k))):
            for x in range(max(0, int((cx - rx - 1) * k)), min(self.w, int((cx + rx + 2) * k))):
                lx, ly = (x + 0.5) / k - 0.5, (y + 0.5) / k - 0.5
                if ((lx - cx) / (rx + 0.3)) ** 2 + ((ly - cy) / (ry + 0.3)) ** 2 <= 1:
                    self.img.putpixel((x, y), rgba(c))

    def outline(self):
        """Contorn fosc d'un píxel al voltant de tot el que s'ha dibuixat (llegibilitat sobre qualsevol fons)."""
        src = self.img.copy()
        for y in range(self.h):
            for x in range(self.w):
                if src.getpixel((x, y))[3] == 0:
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.w and 0 <= ny < self.h and src.getpixel((nx, ny))[3] > 0 and src.getpixel((nx, ny)) != rgba(OUTLINE):
                            self.img.putpixel((x, y), OUTLINE)
                            break


# ─── Persones ───────────────────────────────────────────────────────────────

class Shift:
    """Dibuixa sobre un Canvas desplaçat (el balanceig vertical del cicle de caminar)."""

    def __init__(self, c, dy):
        self.c, self.dy = c, dy

    def px(self, x, y, col):
        self.c.px(x, y + self.dy, col)

    def rect(self, x0, y0, x1, y1, col):
        self.c.rect(x0, y0 + self.dy, x1, y1 + self.dy, col)

    def ellipse(self, cx, cy, rx, ry, col):
        self.c.ellipse(cx, cy + self.dy, rx, ry, col)


SILVER = (200, 200, 210)
GOGGLE_STRAP, GOGGLE_GLASS = (200, 160, 60), (130, 206, 224)
HAIR_TIE = (190, 50, 44)


def braid(c, x, y0, y1, h, h2, w=2):
    """Trena vertical amb textura alterna i un llaç vermell al final."""
    for y in range(y0, y1 + 1):
        k = (y - y0) % 3
        c.rect(x, y, x + w - 1, y, h if k else h2)
        if k == 0:
            c.px(x + (w - 1 if (y // 3) % 2 else 0), y, (90, 66, 70))
    c.rect(x, y1 + 1, x + w - 1, y1 + 1, HAIR_TIE)
    c.px(x + w // 2, y1 + 2, h)


def hair_iri(c, p, f, layer):
    """Cabell fosc tirat enrere amb ratlla al mig, ulleres al front i una trena gruixuda sobre l'espatlla."""
    if layer != 'front':
        return
    h, h2 = p['hair'], p['hair2']
    if f == 'U':
        c.ellipse(17.5, 11, 5.5, 6.5, h)
        c.rect(17, 5, 18, 16, h2)
        c.rect(12, 9, 23, 9, GOGGLE_STRAP)
        braid(c, 16, 16, 35, h, h2, w=3)
    elif f == 'D':
        c.rect(12, 5, 23, 8, h)
        c.px(17, 5, h2); c.px(18, 6, h2)
        c.rect(12, 9, 12, 13, h); c.rect(23, 9, 23, 13, h)
        c.rect(13, 8, 22, 8, GOGGLE_STRAP)
        c.rect(14, 7, 16, 8, GOGGLE_GLASS); c.rect(19, 7, 21, 8, GOGGLE_GLASS)
        c.rect(22, 12, 23, 14, h)
        braid(c, 22, 15, 33, h, h2, w=3)
    else:
        c.rect(12, 5, 22, 8, h)
        c.rect(18, 9, 22, 14, h)
        c.px(18, 13, p['skin'])  # orella
        c.rect(12, 8, 18, 8, GOGGLE_STRAP)
        c.rect(12, 7, 14, 8, GOGGLE_GLASS)
        braid(c, 20, 14, 33, h, h2, w=3)


def hair_vet(c, p, f, layer):
    """Bob platí a l'altura de la barbeta amb serrell recte."""
    h, h2 = p['hair'], p['hair2']
    if layer == 'back':
        if f == 'D':
            c.rect(11, 9, 24, 18, h2)
        return
    if f == 'U':
        c.ellipse(17.5, 10, 6, 6, h); c.rect(11, 10, 24, 18, h); c.rect(11, 18, 24, 18, h2)
    elif f == 'D':
        c.ellipse(17.5, 7, 6.2, 3.5, h)
        c.rect(11, 8, 13, 17, h); c.rect(22, 8, 24, 17, h)
        c.rect(14, 8, 21, 9, h)
        c.rect(11, 17, 13, 17, h2); c.rect(22, 17, 24, 17, h2)
    else:
        c.ellipse(17.5, 7, 6, 3.5, h)
        c.rect(16, 8, 23, 17, h); c.rect(20, 14, 23, 17, h2)
        c.rect(11, 8, 15, 9, h)


def hair_mos(c, p, f, layer):
    """Calb, amb cabells blancs als costats."""
    if layer != 'front':
        return
    h, h2 = p['hair'], p['hair2']
    if f == 'U':
        c.ellipse(17.5, 12, 5.5, 6, h2)
        c.ellipse(17.5, 9, 4, 3.5, p['skin'])
    else:
        c.rect(12, 9, 13, 14, h)
        if f == 'D':
            c.rect(22, 9, 23, 14, h)
        else:
            c.rect(18, 8, 23, 15, h)


def deco_bata(c, p, f):
    """Bata blanca llarga i oberta sobre una camisa blava, amb llapis i una clau a les butxaques."""
    C, C2 = p['coat'], p['coat2']
    shirt = (120, 150, 180)
    if f == 'D':
        c.rect(12, 22, 23, 52, C); c.rect(22, 22, 23, 52, C2); c.rect(12, 22, 12, 52, C2)
        c.rect(16, 22, 19, 37, shirt); c.rect(16, 38, 19, 52, p['legs'])
        c.rect(15, 22, 15, 52, C2); c.rect(20, 22, 20, 52, C2)
        c.rect(14, 22, 15, 24, C2); c.rect(20, 22, 21, 24, C2)
        c.rect(21, 27, 22, 29, C2); c.px(21, 26, (190, 50, 44)); c.px(22, 26, (60, 90, 160))
        c.rect(13, 40, 14, 43, C2); c.rect(21, 40, 22, 43, C2)
        c.px(13, 39, SILVER)
    elif f == 'L':
        c.rect(13, 22, 22, 52, C); c.rect(20, 22, 22, 52, C2)
        c.rect(13, 22, 13, 52, C2); c.rect(14, 40, 16, 43, C2)
    else:
        c.rect(12, 22, 23, 52, C); c.rect(17, 42, 18, 52, C2); c.rect(14, 33, 21, 33, C2)


def deco_taronja(c, p, f):
    """Granota de presó taronja: número estampat al pit i a l'esquena (les franges van a les cames)."""
    ink, white = (40, 40, 48), (240, 240, 240)
    if f == 'D':
        c.rect(17, 22, 18, 23, p['skin'])  # coll en V
        c.rect(14, 25, 17, 28, ink)
        c.px(15, 26, white); c.px(16, 27, white); c.px(15, 27, white)
        c.rect(12, 37, 23, 37, white)
    elif f == 'U':
        c.rect(14, 26, 21, 31, ink); c.rect(15, 28, 20, 29, white)


def deco_mos(c, p, f):
    if f == 'D':
        c.rect(19, 25, 22, 28, (236, 236, 236))  # pegat amb el número
        c.px(20, 26, (40, 40, 60)); c.px(21, 27, (40, 40, 60))
        c.rect(17, 22, 18, 23, p['skin'])


IRI = {
    'skin': (226, 176, 134), 'skin2': (196, 142, 106), 'hair': (50, 34, 38), 'hair2': (30, 20, 24),
    'top': (238, 236, 228), 'top2': (200, 198, 190), 'coat': (238, 236, 228), 'coat2': (200, 198, 190),
    'sleeve': (238, 236, 228), 'sleeve_len': 'long', 'legs': (66, 56, 52), 'legs2': (50, 42, 38),
    'shoes': (40, 30, 26), 'eyes': (40, 30, 30), 'lashes': True, 'hair_fn': hair_iri, 'deco': deco_bata, 'shine': 0.3,
}
VET = {
    'skin': (156, 104, 76), 'skin2': (124, 80, 58), 'hair': (232, 226, 210), 'hair2': (190, 182, 168),
    'top': (226, 116, 44), 'top2': (186, 88, 30), 'sleeve_len': 'long', 'legs': (226, 116, 44), 'legs2': (186, 88, 30),
    'shoes': (232, 232, 232), 'sole': (90, 90, 96), 'leg_stripe': (240, 240, 240), 'eyes': (30, 24, 30), 'lashes': True,
    'hair_fn': hair_vet, 'deco': deco_taronja, 'shine': 0.6,
}
MOS = {
    'skin': (214, 170, 140), 'skin2': (184, 138, 110), 'hair': (206, 206, 214), 'hair2': (160, 160, 170),
    'top': (150, 172, 194), 'top2': (110, 132, 154), 'sleeve_len': 'long', 'legs': (150, 172, 194), 'legs2': (110, 132, 154),
    'shoes': (90, 90, 96), 'eyes': (20, 16, 24), 'makeup': True, 'hair_fn': hair_mos, 'deco': deco_mos,
}

SLEEVE_END = {'long': 37, 'rolled': 29}


def person(p, facing, walk=None, talk=False, thin=False):
    """Una persona de peu, 36×64, peus a (18, 61). `walk`: fotograma 0-5 del cicle."""
    c = Canvas(36, 64)
    bob = [0, -1, 0, 0, -1, 0][walk] if walk is not None else 0
    narrow = 1 if thin else 0
    s = Shift(c, bob)
    p['hair_fn'](s, p, facing, 'back')

    # Cames i peus
    stripe, sole = p.get('leg_stripe'), p.get('sole')
    if facing == 'L':
        swing = [-3, -1, 1, 3, 1, -1][walk] if walk is not None else 0
        for off, shade in ((-swing, p['legs2']), (swing, p['legs'])):
            x = 16 + off
            c.rect(x, 42, x + 3, 57, shade)
            if stripe:
                c.rect(x, 42, x, 57, stripe)
            c.rect(x - 2, 58, x + 3, 61, p['shoes'])
            if sole:
                c.rect(x - 2, 61, x + 3, 61, sole)
    else:
        lift_l = [0, 2, 1, 0, 0, 0][walk] if walk is not None else 0
        lift_r = [0, 0, 0, 0, 2, 1][walk] if walk is not None else 0
        for x0, x1, lift, sx in ((13 + narrow, 16, lift_l, 13 + narrow), (19, 22 - narrow, lift_r, 22 - narrow)):
            c.rect(x0, 42, x1, 57 - lift, p['legs'])
            if stripe:
                c.rect(sx, 42, sx, 57 - lift, stripe)
            c.rect(x0, 58 - lift, x1, 61 - lift, p['shoes'])
            if sole:
                c.rect(x0, 61 - lift, x1, 61 - lift, sole)

    # Malucs i tors
    if facing == 'L':
        s.rect(14, 22, 21, 41, p['top'])
        s.rect(19, 22, 21, 41, p['top2'])
    else:
        s.rect(13 + narrow, 22, 22 - narrow, 37, p['top'])
        s.rect(12 + narrow, 37, 23 - narrow, 41, p['legs'])
        s.rect(21 - narrow, 22, 22 - narrow, 41, p['top2'])
    p['deco'](s, p, facing)

    # Braços
    sleeve = p.get('sleeve', p['top2'])
    end = SLEEVE_END[p['sleeve_len']]
    if facing == 'L':
        sw = [-2, -1, 0, 2, 1, 0][walk] if walk is not None else 0
        arms = [(17 + sw, 0)]
    else:
        sw = [0, 1, 0, 0, -1, 0][walk] if walk is not None else 0
        arms = [(10 + narrow, sw), (23 - narrow, -sw)]
    for ax, dy in arms:
        s.rect(ax, 23 + dy, ax + 2, min(end, 37) + dy, sleeve)
        if end < 37:
            s.rect(ax, end + 1 + dy, ax + 2, 37 + dy, p['skin'])
        s.rect(ax, 38 + dy, ax + 2, 39 + dy, p['skin2'])

    # Coll i cap
    s.rect(16, 19, 19, 21, p['skin2'])
    s.ellipse(17.5 if facing != 'L' else 17, 12, 5, 6.5, p['skin'])
    if facing == 'L':
        s.px(11, 13, p['skin'])  # nas
        s.px(12, 13, p['skin'])

    # Cara
    eye = p['eyes']
    if facing == 'D':
        s.px(15, 12, eye); s.px(20, 12, eye)
        if p.get('lashes'):
            s.px(14, 11, eye); s.px(21, 11, eye)
        if p.get('makeup'):  # llapis d'ulls i barba blanca
            for x in (14, 16, 19, 21):
                s.px(x, 12, (60, 30, 70))
            s.rect(14, 16, 21, 18, p['hair'])
        if talk:
            s.rect(17, 15, 18, 16, (90, 30, 30))
        else:
            s.rect(17, 16, 18, 16, (120, 50, 50))
    elif facing == 'L':
        s.px(14, 12, eye)
        if p.get('lashes'):
            s.px(13, 11, eye)
        if p.get('makeup'):
            s.px(13, 12, (60, 30, 70))
            s.rect(13, 16, 17, 18, p['hair'])
        s.rect(13, 16, 14, 16 + (1 if talk else 0), (90, 30, 30) if talk else (120, 50, 50))

    p['hair_fn'](s, p, facing, 'front')
    face_detail(c, p, facing, bob)
    c.outline()
    return c.img


def mix(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def face_detail(c, p, facing, bob):
    """Detalls a píxel real, que només caben a la resolució gran: celles, nas, galtes i lluentors al cabell."""
    if c.k < 1.2 or facing == 'U':
        if facing == 'U' and c.k >= 1.2 and p.get('shine'):
            hx, hy = pt(15, 7 + bob)
            for i in range(3):
                c.rpx(hx + i, hy - (1 if i == 1 else 0), mix(p['hair'], (255, 255, 255), p['shine']))
        return
    brow = mix(p['hair2'], (30, 20, 24), 0.4) if not p.get('makeup') else p['hair2']
    blush = mix(p['skin'], (230, 90, 90), 0.35)
    shade = p['skin2']
    if facing == 'D':
        for ex in (15, 20):
            x, y = pt(ex, 12 + bob)
            c.rpx(x, y - 1, p['eyes'])                     # ulls d'1×2
            c.rpx(x - 1 if ex == 15 else x, y - 3, brow)   # celles
            c.rpx(x if ex == 15 else x + 1, y - 3, brow)
            c.rpx(x + (-1 if ex == 15 else 1), y + 2, blush)  # galtes
        nx, ny = pt(17.5, 14 + bob)
        c.rpx(nx, ny, shade)                               # nas
    else:
        x, y = pt(14, 12 + bob)
        c.rpx(x, y - 1, p['eyes'])
        c.rpx(x, y - 3, brow); c.rpx(x - 1, y - 3, brow)
        c.rpx(x + 1, y + 2, blush)
        nx, ny = pt(12, 14 + bob)
        c.rpx(nx, ny, shade)
    if p.get('shine'):                                      # lluentor al cabell
        hx, hy = pt(15 if facing == 'D' else 16, 6 + bob)
        for i in range(3):
            c.rpx(hx + i, hy - (1 if i == 1 else 0), mix(p['hair'], (255, 255, 255), p['shine']))


# ─── Cargol (robot) ─────────────────────────────────────────────────────────

BRASS, BRASS2, BRASS3 = (206, 160, 70), (164, 120, 48), (120, 84, 34)
STEEL, STEEL2 = (186, 196, 206), (140, 150, 162)


def cargol(facing, blink=False, talk=False):
    c = Canvas(40, 46)
    lamp = (120, 240, 170) if not blink else (60, 120, 90)
    if talk:
        lamp = (190, 255, 210)
    # Erugues
    c.rect(7, 37, 32, 44, (70, 70, 78))
    for x in range(9, 32, 4):
        c.ellipse(x, 41, 1.5, 1.5, (40, 40, 46))
    # Closca de cargol (a l'esquena): espiral de llautó
    sx = {'D': 20, 'L': 25, 'U': 20}[facing]
    r = 12 if facing != 'D' else 11
    c.ellipse(sx, 22, r, r, BRASS)
    c.ellipse(sx, 22, r - 3, r - 3, BRASS2)
    c.ellipse(sx + 1, 21, r - 6, r - 6, BRASS)
    c.ellipse(sx + 1, 21, 2, 2, BRASS3)
    if facing != 'U':
        # Cos de metall al davant
        bx0 = 11 if facing == 'D' else 8
        c.rect(bx0, 18, bx0 + 17 - (3 if facing == 'L' else 0), 37, STEEL)
        c.rect(bx0, 33, bx0 + 17 - (3 if facing == 'L' else 0), 37, STEEL2)
        # Pantalla-cara
        fx = 14 if facing == 'D' else 9
        c.rect(fx, 22, fx + 11 - (4 if facing == 'L' else 0), 29, (36, 44, 56))
        c.rect(fx + 2, 25, fx + 3, 26, lamp)
        if facing == 'D':
            c.rect(fx + 8, 25, fx + 9, 26, lamp)
        # Reixeta de la boca
        gy = 28 if not talk else 27
        for x in range(fx + 2, fx + (10 if facing == 'D' else 6), 2):
            c.px(x, gy, (150, 160, 170))
        # Braç amb clau anglesa
        ax = 30 if facing == 'D' else 6
        c.rect(ax, 25, ax + 1, 32, STEEL2)
        c.rect(ax - 1, 33, ax + 2, 34, (200, 200, 210))
    # Antenes amb ulls (com un cargol)
    stalks = [(15, 24)] if facing == 'L' else [(14, 25)]
    if facing == 'L':
        stalks = [(10, 14)]
    for x0, x1 in [stalks[0]] if facing == 'L' else [(14, 14), (25, 25)]:
        top = 6 if not talk else 5
        for y in range(top + 2, 19):
            c.px(x0, y, STEEL2)
        c.ellipse(x0, top, 2, 2, lamp)
        c.px(x0, top, (255, 255, 255))
    c.outline()
    return c.img


# ─── El capatàs Pruna, adormit ──────────────────────────────────────────────

def capatas(breath=0, with_seal=True, talk=False, zz=0):
    c = Canvas(48, 60)
    wood, wood2 = (122, 82, 50), (92, 60, 36)
    shirt, shirt2 = (222, 214, 196), (190, 180, 160)
    trousers = (84, 74, 70)
    skin, skin2 = (230, 170, 140), (200, 140, 112)
    # Cadira (respatller darrere, seient, potes)
    c.rect(9, 14, 36, 40, wood2)
    c.rect(11, 16, 34, 38, wood)
    c.rect(7, 40, 38, 43, wood)
    for x in (8, 36):
        c.rect(x, 44, x + 2, 58, wood2)
    # Cames (assegut: cuixes endavant, canyelles avall)
    c.rect(12, 40, 21, 45, trousers)
    c.rect(24, 40, 33, 45, trousers)
    c.rect(13, 46, 19, 54, trousers)
    c.rect(26, 46, 32, 54, trousers)
    c.rect(12, 55, 20, 58, (50, 36, 28))
    c.rect(25, 55, 33, 58, (50, 36, 28))
    # Panxa i tors (respira)
    c.ellipse(22.5, 32, 11 + breath, 9 + breath * 0.5, shirt)
    c.rect(13, 20, 32, 30, shirt)
    c.rect(28, 20, 32, 38, shirt2)
    c.rect(16, 20, 17, 40, (120, 40, 40))   # tirants
    c.rect(28, 20, 29, 40, (120, 40, 40))
    c.rect(17, 41, 28, 42, (60, 46, 36))    # cinturó
    # Braços creuats sobre la panxa
    c.rect(12, 30, 33, 34, shirt2)
    c.rect(18, 31, 27, 34, skin)
    if with_seal:
        c.rect(20, 25, 22, 31, (180, 44, 44))      # mànec vermell del segell
        c.ellipse(21, 24, 2, 1.5, (180, 44, 44))
        c.rect(18, 32, 25, 34, (110, 74, 40))      # base de fusta
    # Cap, decantat i amb la gorra sobre els ulls
    c.rect(20, 17, 25, 19, skin2)
    c.ellipse(23, 12, 6, 6.5, skin)
    c.rect(16, 4, 30, 9, (96, 96, 104))            # gorra
    c.rect(14, 9, 29, 10, (70, 70, 78))            # visera
    c.rect(19, 12, 21, 12, (60, 40, 40))           # ulls tancats
    c.rect(25, 12, 27, 12, (60, 40, 40))
    c.rect(19, 15, 28, 16, (70, 48, 40))           # bigoti
    if talk:
        c.rect(22, 17, 24, 18, (90, 30, 30))
    else:
        c.px(23, 17, (90, 30, 30))                 # roncant
    # Zetes
    if zz:
        for i in range(zz):
            x, y = 33 + i * 4, 8 - i * 4
            for (dx, dy) in ((0, 0), (1, 0), (2, 0), (1, 1), (0, 2), (1, 2), (2, 2)):
                c.px(x + dx, y + dy, (255, 255, 255))
    c.outline()
    return c.img


def mare(glow=False):
    c = Canvas(16, 16)
    pink = (255, 120, 180) if not glow else (255, 170, 210)
    c.ellipse(5, 6, 3.5, 3.5, pink)
    c.ellipse(10, 6, 3.5, 3.5, pink)
    for y in range(7, 14):
        w = 13 - y
        c.rect(7.5 - w if False else int(7.5 - w), y, int(7.5 + w), y, pink)
    for x in (5, 7, 9):
        c.px(x, 7, (120, 40, 80))
    c.outline()
    return c.img


# ─── Fulls i definicions ────────────────────────────────────────────────────

def scaled_extra(extra):
    """Punts i velocitats del .character.json, de coordenades de disseny a píxels reals."""
    out = dict(extra)
    out['walkSpeed'] = round(extra['walkSpeed'] * SCALE)
    for key in ('walkToPoint', 'talkPoint', 'feet'):
        x, y = pt(extra[key]['x'], extra[key]['y'])
        out[key] = {'x': x, 'y': y}
    out['collider'] = {'points': [dict(zip('xy', pt(p['x'], p['y']))) for p in extra['collider']['points']]}
    return out


def write(cid, tags, size, extra):
    """tags: [(nom, [imatges])]. Escriu <id>.png, <id>.json (Aseprite) i <id>.character.json."""
    frames = [img for _, imgs in tags for img in imgs]
    w, h = frames[0].size
    extra = scaled_extra(extra)
    sheet = Image.new('RGBA', (w * len(frames), h), CLEAR)
    for i, img in enumerate(frames):
        sheet.paste(img, (i * w, 0))
    d = OUT / cid
    d.mkdir(parents=True, exist_ok=True)
    sheet.save(d / f'{cid}.png')
    frame_tags, i = [], 0
    for name, imgs in tags:
        frame_tags.append({'name': name, 'from': i, 'to': i + len(imgs) - 1, 'direction': 'forward', 'color': '#000000ff'})
        i += len(imgs)
    meta = {
        'frames': {f'{cid} {n}.aseprite': {
            'frame': {'x': n * w, 'y': 0, 'w': w, 'h': h}, 'rotated': False, 'trimmed': False,
            'spriteSourceSize': {'x': 0, 'y': 0, 'w': w, 'h': h}, 'sourceSize': {'w': w, 'h': h}, 'duration': 100,
        } for n in range(len(frames))},
        'meta': {'app': 'https://www.aseprite.org/', 'version': 'provisional (draw_characters.py)', 'image': f'{cid}.png',
                 'format': 'RGBA8888', 'size': {'w': sheet.width, 'h': h}, 'scale': '1',
                 'frameTags': frame_tags, 'layers': [], 'slices': []},
    }
    (d / f'{cid}.json').write_text(json.dumps(meta, indent=2) + '\n')
    character = {
        'id': cid, 'name': cid, 'description': '', 'clickable': True, 'display': {'aseprite': True},
        **extra,
    }
    (d / f'{cid}.character.json').write_text(json.dumps(character, indent=2) + '\n')
    print(f'✔ {cid}: {len(frames)} fotogrames, {", ".join(t for t, _ in tags)}')


def walker(cid, p):
    tags = []
    for f in 'LDU':
        tags.append((f'Idle{f}', [person(p, f)]))
    for f in 'LDU':
        tags.append((f'Walk{f}', [person(p, f, walk=k) for k in range(6)]))
    for f in 'LDU':
        tags.append((f'Talk{f}', [person(p, f, talk=False), person(p, f, talk=True)]))
    anims = {t: {'loop': True} for t, _ in tags}
    for f in 'LDU':
        anims[f'Walk{f}']['frameDuration'] = 90 if f == 'L' else 80
        anims[f'Talk{f}']['frameDuration'] = 140
    write(cid, tags, (36, 64), {
        'walkSpeed': 84, 'walkToPoint': {'x': 40, 'y': 61}, 'talkPoint': {'x': 18, 'y': -2}, 'feet': {'x': 18, 'y': 61},
        'collider': {'points': [{'x': 11, 'y': 2}, {'x': 25, 'y': 2}, {'x': 27, 'y': 40}, {'x': 24, 'y': 63}, {'x': 11, 'y': 63}, {'x': 8, 'y': 40}]},
        'animations': anims, 'defaultVerb': 'look',
    })


def standing(cid, p, thin=False):
    tags = []
    for f in 'DLU':
        tags.append((f'Idle{f}', [person(p, f, thin=thin)]))
        tags.append((f'Talk{f}', [person(p, f, thin=thin), person(p, f, talk=True, thin=thin)]))
    anims = {t: {'loop': True, **({'frameDuration': 140} if t.startswith('Talk') else {})} for t, _ in tags}
    write(cid, tags, (36, 64), {
        'walkSpeed': 60, 'walkToPoint': {'x': 44, 'y': 61}, 'talkPoint': {'x': 18, 'y': -2}, 'feet': {'x': 18, 'y': 61},
        'collider': {'points': [{'x': 11, 'y': 2}, {'x': 25, 'y': 2}, {'x': 27, 'y': 40}, {'x': 24, 'y': 63}, {'x': 11, 'y': 63}, {'x': 8, 'y': 40}]},
        'animations': anims, 'defaultVerb': 'talkTo',
    })


def main():
    walker('iri', IRI)
    walker('vet', VET)
    standing('mos', MOS, thin=True)

    tags = []
    for f in 'DLU':
        tags.append((f'Idle{f}', [cargol(f), cargol(f), cargol(f), cargol(f, blink=True)]))
        tags.append((f'Talk{f}', [cargol(f, talk=False), cargol(f, talk=True)]))
    write('cargol', tags, (40, 46), {
        'walkSpeed': 50, 'walkToPoint': {'x': 46, 'y': 44}, 'talkPoint': {'x': 20, 'y': 0}, 'feet': {'x': 20, 'y': 44},
        'collider': {'points': [{'x': 6, 'y': 4}, {'x': 34, 'y': 4}, {'x': 34, 'y': 45}, {'x': 6, 'y': 45}]},
        'animations': {t: {'loop': True, 'frameDuration': 250 if t.startswith('Idle') else 140} for t, _ in tags},
        'defaultVerb': 'talkTo',
    })

    snore = [capatas(0, zz=0), capatas(1, zz=1), capatas(1, zz=2), capatas(0, zz=3)]
    snore_empty = [capatas(0, False, zz=0), capatas(1, False, zz=1), capatas(1, False, zz=2), capatas(0, False, zz=3)]
    talk = [capatas(0, talk=True), capatas(0)]
    tags = [('IdleD', snore), ('TalkD', talk), ('IdleL', snore), ('TalkL', talk), ('IdleU', snore), ('TalkU', talk),
            ('DormSenseSegell', snore_empty)]
    write('capatas', tags, (48, 60), {
        'walkSpeed': 40, 'walkToPoint': {'x': 52, 'y': 58}, 'talkPoint': {'x': 24, 'y': 0}, 'feet': {'x': 24, 'y': 58},
        'collider': {'points': [{'x': 8, 'y': 4}, {'x': 38, 'y': 4}, {'x': 38, 'y': 59}, {'x': 8, 'y': 59}]},
        'animations': {t: {'loop': True, 'frameDuration': 600 if t != 'TalkD' and not t.startswith('Talk') else 160} for t, _ in tags},
        'defaultVerb': 'look',
    })

    tags = [(t, [mare(), mare(glow=True)]) for t in ('IdleD', 'TalkD', 'IdleL', 'TalkL', 'IdleU', 'TalkU')]
    write('mare', tags, (16, 16), {
        'walkSpeed': 1, 'walkToPoint': {'x': 0, 'y': 30}, 'talkPoint': {'x': 8, 'y': -2}, 'feet': {'x': 8, 'y': 15},
        'clickable': False, 'collider': {'points': [{'x': 0, 'y': 0}, {'x': 15, 'y': 0}, {'x': 15, 'y': 15}, {'x': 0, 'y': 15}]},
        'animations': {t: {'loop': True, 'frameDuration': 300} for t, _ in tags}, 'defaultVerb': 'talkTo',
    })


if __name__ == '__main__':
    main()
