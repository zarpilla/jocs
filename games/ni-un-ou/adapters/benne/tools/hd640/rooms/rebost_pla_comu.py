"""
**El dibuix pla de sempre** (font de les textures de la sala en 3D, rebost.py).

Prova de resolució: el rebost de l'Arenga a 640×360 (la composició de hd/rooms/rebost.py ×4/3, dibuixada de nou
amb el detall que hi cap). Mateixes rampes, mateixos props i mateixes animacions.

  - un magatzem estret de planxa verda, amb dos llums de gàbia càlids;
  - a l'esquerra, la porta estanca oberta cap a la sala de màquines (el motor, de l'altra banda), i el tamboret
    on el cuiner d'abans hi baixava a fumar (una llauna de sardines fa de cendrer);
  - el muntacàrregues de la cuina: la portella de guillotina pujada, el replà de la safata, la placa «250 KG» i
    els tres botons (cuina, rebost, pont); `safata` (prop): una safata d'acer amb alguna cosa;
  - les prestatgeries de queviures: pots de llegums, llaunes de sardines (en falten), tomàquet, sacs d'«ARRÒS»;
  - el congelador d'arcó i el calendari del cuiner, encara del 2019;
  - a terra, el registre del dipòsit 2 (tapa blava, «AIGUA NO POTABLE»); `rascades` (Escenes 4 i després): el
    pany forçat; `registre_obert`: la tapa aixecada i el forat amb l'escala.
Animacions: `pols` (a la llum dels llums) i `ratoli` (treu el cap d'entre els sacs).

Aquí hi ha també les peces de la coberta de sota a 640 (paret de planxa, terra estriat, llum de gàbia, rètols)
que fa servir hd640/rooms/taller.py.
"""
import math
from functools import lru_cache

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from PIL import Image

from hd.pix import Canvas, Light, W, H, hr, mix, B4, RUST
from hd.rooms.arenga import (WALL, ENG_LIGHT as ENG, DECK, CAB, REDP, YELL, SEAG, DARK, WHITEP, BRASS, WARM,
                             box, rrect, bolt, hpipe, vpipe, glow)
from hd.rooms.comu import text, text_width
from hd640.rooms.sala_maquines_pla_comu import ceiling, _frame, _inside, _sill, _label

from hd.pix import Canvas  # noqa: E402,F811  (a 1×: és la font de les textures de la sala en 3D)
Canvas1x = Canvas

FLOOR_Y = 203
BOTTOM = 260
LAMP = [(120, 90, 40), (200, 160, 80), (250, 220, 150), (255, 246, 220)]

LAMP_X = (200, 496)
SHELF = [(18, 20, 22), (34, 38, 42), (54, 60, 64), (78, 84, 88), (104, 110, 112), (134, 140, 140), (170, 174, 172)]
TIN = [(30, 34, 40), (60, 68, 78), (100, 110, 120), (148, 158, 166), (196, 204, 208), (236, 240, 242)]
SARD = [(20, 30, 60), (30, 52, 100), (46, 80, 140), (80, 118, 176), (140, 170, 210)]
SARDY = [(60, 36, 6), (130, 90, 16), (200, 150, 30), (240, 200, 80)]
RICE = [(70, 62, 46), (130, 118, 90), (184, 172, 138), (220, 210, 180), (240, 234, 210)]
JUTE = [(30, 22, 10), (60, 44, 22), (96, 72, 38), (130, 102, 58), (164, 134, 82), (196, 170, 114)]
ONION = [(50, 20, 10), (110, 50, 20), (170, 96, 40), (210, 146, 80)]
LENTIL = [(40, 26, 14), (80, 54, 30), (120, 84, 46), (156, 116, 66)]
BLUEP = [(10, 18, 34), (18, 32, 58), (28, 50, 86), (42, 72, 116), (62, 98, 146), (96, 132, 176)]
WOOD = [(24, 14, 8), (44, 26, 14), (68, 42, 22), (96, 62, 32), (126, 84, 44), (156, 110, 60), (186, 140, 82)]

LIGHT = Light(ambient=-0.4, vignette=(80, 37), floor_fade=(251, 48))
LIGHT.point(LAMP_X[0], 35, r=200, k=2.5, squash=1.05, down=True, power=1.5)
LIGHT.point(LAMP_X[1], 35, r=200, k=2.3, squash=1.05, down=True, power=1.5)
LIGHT.point(45, 147, r=53, k=0.4, power=2.0)

MUNTA = (261, 75, 328, 141)


# ─── Peces de la coberta de sota a 640 (també les fa servir el taller) ──────

def plate_wall(cv, seed=0, ramp=WALL, lvl=3.1):
    """Paret de planxa pintada: quadernes amb dues fileres de reblons, soldadures amb cordó, sòcol gastat i rovell."""
    for y in range(0, FLOOR_Y):
        for x in range(W):
            v = lvl + (hr(x // 3, y // 5, seed) - 0.5) * 0.35
            if y >= 179:
                v -= 0.9 + (0.3 if hr(x // 6, y // 3, seed) > 0.8 else 0)
            cv.put(x, y, ramp, v)
    for fx in range(-11, W, 85):                                     # quadernes
        for x in range(max(0, fx), min(W - 1, fx + 7) + 1):
            d = x - fx
            for y in range(27, FLOOR_Y):
                cv.put(x, y, ramp, lvl + 0.4 + (0.9 if d == 0 else 0.5 if d == 1 else -0.3 if d >= 6 else 0.1)
                       - (0.8 if y >= 179 else 0))
        for y in range(37, 176, 16):
            if 0 <= fx + 3 < W:
                bolt(cv, fx + 3, y, ramp, lvl + 0.5)
                bolt(cv, fx + 5, y + 8, ramp, lvl + 0.3)
    for sy in (85, 149):                                             # soldadures, amb el cordó
        for x in range(W):
            cv.put(x, sy, ramp, lvl - 1.3)
            cv.put(x, sy + 1, ramp, lvl + 0.8 if (x // 2) % 2 else lvl + 0.3)
    cv.hline(0, W - 1, 179, ramp, lvl + 0.9)
    cv.hline(0, W - 1, 180, ramp, lvl - 0.9)
    cv.hline(0, W - 1, FLOOR_Y - 1, ramp, lvl - 2.1)
    for i in range(34):                                              # rovell que baixa de les soldadures
        x = int(hr(i, 7, seed) * W)
        sy = (85, 149)[int(hr(i, 8, seed) * 2)] + 2
        n = 7 + int(hr(i, 9, seed) * 21)
        for y in range(sy, min(FLOOR_Y - 2, sy + n)):
            k = 0.5 * (1 - (y - sy) / n)
            if k > B4[y & 3][x & 3] * 0.6:
                cv.flat(x, y, mix(cv.get(x, y), RUST[3], k))
            if k > 0.3 and hr(x, y, seed) > 0.7:
                cv.flat(x + 1, y, mix(cv.get(x + 1, y), RUST[2], k * 0.6))


def cage_lamp(cv, lx, ly=29, top=21, on=True):
    """Llum de gàbia al sostre: la base, el globus i la gàbia de fil."""
    box(cv, lx - 8, top, lx + 8, top + 5, CAB, 3.0)
    bolt(cv, lx - 6, top + 2, CAB, 4.0)
    bolt(cv, lx + 5, top + 2, CAB, 4.0)
    cv.disc(lx, ly + 4, 8, 5, LAMP if on else CAB, 2.6 if on else 2.0, lit=0)
    for gx in (-5, 0, 5):
        cv.vline(lx + gx, ly, ly + 9, CAB, 2.2, lit=0)
    cv.hline(lx - 8, lx + 8, ly + 5, CAB, 2.0, lit=0)
    cv.hline(lx - 6, lx + 6, ly + 9, CAB, 2.4, lit=0)


def lamp_glow(cv, lx, ly=29):
    glow(cv, lx, ly + 5, 45, WARM, 0.55)
    glow(cv, lx, ly + 5, 16, (255, 240, 200), 0.6)


VP = (320, 53)


def checker_floor(cv):
    """Terra de planxa estriada en perspectiva, amb les juntes de les planxes."""
    for y in range(FLOOR_Y, BOTTOM + 16):
        d = y - VP[1]
        for x in range(W):
            u = VP[0] + (x - VP[0]) * 200 / d
            u2 = VP[0] + (x + 1 - VP[0]) * 200 / d
            v = 4267 / d
            lvl = 2.5
            if int(u // 101) != int(u2 // 101):
                lvl = 1.0
            elif y in (211, 227, 249):
                lvl = 1.1
            elif y in (212, 228, 250):
                lvl = 3.3
            else:
                a, b = int(u * 0.5) % 4, int(v * 1.6) % 4
                if (a == 0 and b in (0, 1)) or (a == 2 and b in (2, 3)):
                    lvl += 0.9
                elif (a == 1 and b == 1) or (a == 3 and b == 3):
                    lvl -= 0.3
            cv.put(x, y, DECK, lvl)
    cv.hline(0, W - 1, FLOOR_Y, DECK, 1.0)


def floor_shadow(cv, cx, cy, rx, ry, k=0.6):
    cv.darken(cx - rx, cy - ry, cx + rx, cy + ry,
              lambda x, y: k * max(0.0, 1 - ((x - cx) / rx) ** 2 - ((y - cy) / ry) ** 2) * 1.6)


def engine_door(cv, far):
    """La porta estanca oberta cap a la sala de màquines (a l'esquerra), amb el rètol. `far(cv)` pinta el que
    es veu de l'altra banda."""
    x0, y0, x1, y1 = 19, 88, 72, FLOOR_Y
    for y in range(y0, y1):
        for x in range(x0, x1 + 1):
            if _inside(x, y, x0, y0, x1):
                cv.put(x, y, WALL, 2.0 - abs(x - 45) / 53 + (-1.0 if y > 181 else 0) - (y - y0) / 213, lit=0.3)
    far(cv)
    cv.rect(x0, y1 - 19, x1, y1 - 1, DECK, 1.6, lit=0.2)
    for x in range(x0 + 2, x1, 5):                                   # el terra estriat de l'altra banda
        cv.put(x, y1 - 14, DECK, 2.4, lit=0.2)
        cv.put(x + 2, y1 - 8, DECK, 2.4, lit=0.2)
    _frame(cv, x0, y0, x1, y1)
    _sill(cv, x0, x1, y1)
    # la fulla, oberta contra la paret
    cv.poly([(5, y0 + 5), (16, y0 - 1), (16, y1 - 3), (5, y1 - 5)], ENG, lambda x, y: 2.8 - (x - 5) * 0.05)
    cv.vline(16, y0, y1 - 3, ENG, 4.2)
    for y in range(y0 + 13, y1 - 10, 29):
        box(cv, 7, y, 13, y + 4, ENG, 3.6)
        cv.put(8, y + 1, ENG, 5.2)
    for dx, dy in ((x1 + 3, 112), (x1 + 3, 165)):                    # palanques del marc
        box(cv, dx, dy, dx + 3, dy + 8, CAB, 3.4)
        cv.put(dx + 1, dy + 1, CAB, 5.0)
    _label(cv, 'MÀQUINES', 45, 66)


# ─── Paret i sostre ───────────────────────────────────────────────────────

def room(cv):
    plate_wall(cv, seed=11)
    ceiling(cv)
    hpipe(cv, 80, W - 1, 40, 3, SEAG, 3.0, bands=range(107, W, 93), band_ramp=WHITEP)       # aigua dolça
    for x in range(107, W, 93):                                     # fletxes del sentit
        for i in range(3):
            cv.vline(x + 4 + i, 40 - 2 + i, 40 + 2 - i, SEAG, 1.2)
    for x in range(120, W, 93):                                     # abraçadores
        cv.vline(x, 34, 46, CAB, 2.0)
        cv.vline(x + 1, 34, 46, CAB, 3.4)
    # el tub del dipòsit 2, que baixa a terra (al costat del registre), amb una vàlvula
    vpipe(cv, 88, 40, FLOOR_Y + 3, 3, SEAG, 2.8, bands=(80, 160), band_ramp=WHITEP)
    hpipe(cv, 80, 88, 40, 3, SEAG, 3.0)
    cv.disc(88, 40, 4, 4, SEAG, lambda nx, ny: 3.2 - nx - ny)
    box(cv, 84, 120, 92, 127, SEAG, 3.4)
    # el volant de la vàlvula: llanta amb volum, tres radis i la boixa
    for a in range(0, 360, 6):
        for rr, lv in ((6, 4.2), (5, 2.8)):
            cv.put(88 + round(math.cos(math.radians(a)) * rr), 116 + round(math.sin(math.radians(a)) * rr),
                   REDP, lv + (0.8 if 180 < a < 300 else -0.4 if a < 90 else 0))
    for a in (90, 210, 330):
        for t in range(2, 5):
            cv.put(88 + round(math.cos(math.radians(a)) * t), 116 + round(math.sin(math.radians(a)) * t), REDP, 3.0)
    cv.disc(88, 116, 1.5, 1.5, CAB, 4.4)
    for lx in LAMP_X:
        cage_lamp(cv, lx)


# ─── La porta i el racó del cuiner ────────────────────────────────────────

def _engine_far(cv):
    """El motor, de l'altra banda de la porta: un cantó de bloc verd amb les culates i una mica de llum."""
    x0 = 19
    for y in range(107, 184):
        for x in range(x0, x0 + 25):
            cv.put(x, y, ENG, 2.4 - (y - 107) * 0.008 + (0.6 if (y - 107) % 13 == 0 else 0)
                   - (x - x0) * 0.02, lit=0.2)
    for y in range(115, 176, 13):                                   # cargols de les culates
        cv.put(x0 + 20, y + 3, ENG, 3.6, lit=0.2)
    vpipe(cv, x0 + 30, 100, 150, 1, ENG, 2.0)                       # un tub d'injecció, al fons


def door(cv):
    engine_door(cv, _engine_far)


def stool(cv):
    """El tamboret del cuiner d'abans, amb la llauna de sardines que fa de cendrer (i les burilles)."""
    x0, x1, top = 101, 133, 168
    cx = (x0 + x1) / 2
    for lx, d in ((x0 + 4, -3), (x1 - 4, 3), (round(cx), 0)):
        cv.line(lx, top + 2, lx + d, FLOOR_Y + 8, WOOD, 3.0)
        cv.line(lx + 1, top + 2, lx + d + 1, FLOOR_Y + 8, WOOD, 1.8)
    cv.hline(x0 + 3, x1 - 3, 192, WOOD, 2.6)
    cv.hline(x0 + 3, x1 - 3, 193, WOOD, 1.4)
    cv.disc(cx, top + 1, (x1 - x0) / 2, 4, WOOD, lambda nx, ny: 4.4 - ny * 1.2 - nx * 0.4)
    cv.disc(cx, top, (x1 - x0) / 2 - 1, 3, WOOD, lambda nx, ny: 5.0 - ny * 0.8 - nx * 0.6)
    for k in range(3):                                              # la veta del seient
        cv.hline(round(cx) - 10 + k * 4, round(cx) - 4 + k * 4, top - 1 + k, WOOD, 3.6)
    # la llauna-cendrer, oberta (la tapa enrotllada), amb burilles i cendra
    lx, ly = round(cx), top - 3
    cv.disc(lx, ly, 8, 3, TIN, 4.4)
    cv.disc(lx, ly, 6, 1.8, TIN, 1.4)
    cv.rect(lx - 7, ly + 1, lx + 7, ly + 3, SARD, 3.0)
    for k in range(4):                                              # la tapa enrotllada
        cv.put(lx + 8 + (k % 2), ly - 2 - k, TIN, 5.0 - k * 0.4)
    cv.rect(lx - 5, ly - 2, lx - 3, ly - 1, WHITEP, 4.6)
    cv.put(lx - 2, ly - 2, YELL, 3.6)
    cv.rect(lx + 1, ly - 1, lx + 4, ly - 1, WHITEP, 4.4)
    cv.put(lx + 5, ly - 1, YELL, 3.4)
    cv.flat(lx - 1, ly, (90, 88, 84))                                # cendra
    cv.flat(lx + 1, ly + 1, (110, 108, 102))


# ─── El muntacàrregues ────────────────────────────────────────────────────

def dumbwaiter(cv):
    x0, y0, x1, y1 = MUNTA
    box(cv, x0 - 5, y0 - 5, x1 + 5, y1 + 5, CAB, 3.2, grad=0.6)        # el marc d'acer inoxidable
    for bx, by in ((x0 - 3, y0 - 3), (x1 + 2, y0 - 3), (x0 - 3, y1 + 2), (x1 + 2, y1 + 2)):
        bolt(cv, bx, by, CAB, 4.4)
    for gx in (x0 - 2, x1 + 2):                                     # els carrils de la guillotina
        cv.vline(gx, y0 - 5, y1 + 5, CAB, 4.4)
        cv.vline(gx + (1 if gx > x0 else -1), y0 - 5, y1 + 5, CAB, 2.2)
    # l'obertura, amb la portella de guillotina pujada
    box(cv, x0, y0 + 19, x1, y1, DARK, 1.0)
    for y in range(y0 + 21, y1 - 1):
        cv.hline(x0 + 1, x1 - 1, y, DARK, 1.6 + (y - y0 - 21) * 0.03, lit=0.3)
    cv.vline(x0 + 1, y0 + 21, y1 - 1, CAB, 1.8)
    for y in range(y0 + 24, y1 - 8, 8):                             # les guies de dins del pou
        cv.put(x0 + 4, y, CAB, 2.6, lit=0.3)
        cv.put(x1 - 4, y, CAB, 2.6, lit=0.3)
    for k in range(2):                                              # els cables del muntacàrregues, que pugen
        cv.vline(x0 + 22 + k * 22, y0 + 20, y1 - 10, CAB, 2.2 - k * 0.3, lit=0.3)
    cv.hline(x0 - 3, x1 + 3, y1, CAB, 4.0)                          # el replà de la safata
    cv.hline(x0 - 3, x1 + 3, y1 + 1, CAB, 2.0)
    cv.hline(x0 - 3, x1 + 3, y1 + 2, CAB, 1.0)
    box(cv, x0, y0, x1, y0 + 16, CAB, 3.6)                          # la portella, a dalt
    for y in range(y0 + 4, y0 + 15, 4):
        cv.hline(x0 + 4, x1 - 4, y, CAB, 2.6)
        cv.hline(x0 + 4, x1 - 4, y + 1, CAB, 4.4)
    box(cv, (x0 + x1) // 2 - 7, y0 + 13, (x0 + x1) // 2 + 7, y0 + 16, BRASS, 3.4)
    cv.hline((x0 + x1) // 2 - 6, (x0 + x1) // 2 + 6, y0 + 13, BRASS, 5.0)
    # la placa de llautó del fabricant, amb la càrrega màxima
    box(cv, x0 + 13, y0 - 16, x1 - 13, y0 - 8, BRASS, 3.2)
    for bx in (x0 + 15, x1 - 15):
        cv.put(bx, y0 - 12, BRASS, 5.4)
    s = '250 KG'
    text(cv, s, (x0 + x1) // 2 - text_width(s) // 2, y0 - 14, None, 0, flat=(70, 44, 18))
    # els tres botons (cuina, rebost, pont) i el del rebost encès
    bx = x1 + 11
    box(cv, bx, 88, bx + 16, 133, CAB, 2.8)
    for by in (90, 131):
        bolt(cv, bx + 8, by, CAB, 4.0)
    for i, (lt, lit) in enumerate((('C', False), ('R', True), ('P', False))):
        y = 95 + i * 12
        cv.disc(bx + 5, y + 2, 3, 3, REDP if lit else WHITEP, 4.6 if lit else 3.4, lit=0.5)
        cv.put(bx + 4, y + 1, WHITEP, 5.6, lit=0)
        text(cv, lt, bx + 10, y, None, 0, flat=(200, 204, 200))
        if lit:
            glow(cv, bx + 5, y + 2, 7, (255, 80, 60), 0.5)
    # el timbre
    cv.disc(bx + 8, 144, 4, 3, BRASS, lambda nx, ny: 3.8 - nx - ny)
    cv.put(bx + 7, 143, BRASS, 6.0)


# ─── Les prestatgeries ────────────────────────────────────────────────────

def _tin(cv, x, y, ramp):
    """Una llauna de sardines de cantó: planxa, paper de color, una franja blanca i el peixet."""
    box(cv, x, y, x + 18, y + 6, TIN, 3.8)
    cv.rect(x + 1, y + 1, x + 17, y + 5, ramp, 2.8)
    cv.hline(x + 1, x + 17, y + 1, ramp, 3.8)
    cv.hline(x + 3, x + 9, y + 3, WHITEP, 3.8)
    cv.hline(x + 11, x + 14, y + 3, TIN, 4.6)                        # el peixet
    cv.put(x + 15, y + 2, TIN, 4.4)
    cv.put(x + 15, y + 4, TIN, 4.4)
    cv.put(x + 16, y + 3, REDP, 3.6)


def _tins_row(cv, x0, x1, base, seed, gaps=()):
    """Una filera de piles de llaunes de sardines (en falten unes quantes)."""
    x, i = x0, 0
    while x + 19 <= x1:
        stack = 2 + int(hr(i, seed) * 3)
        if i in gaps:
            stack = int(hr(i, seed, 2) * 2)
        for k in range(stack):
            _tin(cv, x, base - (k + 1) * 7, SARDY if hr(i, k, seed) > 0.7 else SARD)
        x += 20
        i += 1


def _jar(cv, x, top, bottom, w, fill, lid):
    """Un pot de vidre amb el que hi ha a dins, el reflex del vidre, la tapa i l'etiqueta."""
    for y in range(top, bottom):
        for xx in range(x, x + w):
            u = (xx - x - (w - 1) / 2) / ((w + 1) / 2)
            inside = y > top + 6
            cv.put(xx, y, fill if inside else WHITEP, (2.8 if inside else 3.2) - u * 1.0 - u * u)
            if inside and fill is LENTIL and hr(xx, y, 3) > 0.6:
                cv.put(xx, y, fill, 3.6 - u)
    cv.vline(x + 2, top + 2, bottom - 3, WHITEP, 5.0)                 # el reflex
    cv.rect(x + 1, top - 3, x + w - 2, top, lid, 3.6)
    cv.hline(x + 1, x + w - 2, top - 3, lid, 4.8)
    cv.rect(x + 2, top + 10, x + w - 3, top + 15, WHITEP, 4.2)        # l'etiqueta
    cv.hline(x + 3, x + w - 4, top + 12, CAB, 2.0)


def shelves(cv):
    x0, x1 = 381, 627
    xm = (x0 + x1) // 2
    for ux in (x0, xm, x1 - 4):                                      # els muntants (angulars perforats)
        box(cv, ux, 53, ux + 4, FLOOR_Y + 4, SHELF, 3.4)
        for y in range(58, FLOOR_Y, 8):
            cv.put(ux + 2, y, SHELF, 0.8)
            cv.put(ux + 2, y + 1, SHELF, 0.4)
    levels = (85, 125, 165, FLOOR_Y - 3)
    for y in levels:
        box(cv, x0, y, x1, y + 4, SHELF, 3.8)
        cv.hline(x0, x1, y, SHELF, 5.0)
        cv.darken(x0 + 5, y + 5, x1 - 5, y + 10, lambda xx, yy, y=y: 0.6 - (yy - y - 5) * 0.1)
    # prestatge de dalt: pots de vidre (cigrons, arròs, tomàquet sec, llenties) i un forat
    fills = [ONION, RICE, REDP, LENTIL, RICE, ONION, LENTIL, REDP, RICE, ONION, LENTIL]
    for i, x in enumerate(range(x0 + 10, x1 - 14, 21)):
        if hr(i, 3) > 0.85:
            continue
        _jar(cv, x, 61, 85, 15, fills[i % len(fills)], REDP if i % 2 else CAB)
    # segon: llaunes de sardines (en falten unes quantes)
    _tins_row(cv, x0 + 8, xm - 3, 125, 1, gaps=(3, 4))
    _tins_row(cv, xm + 7, x1 - 5, 125, 2, gaps=(2,))
    # tercer: més sardines i llaunes grosses de tomàquet
    _tins_row(cv, x0 + 8, x0 + 107, 165, 3, gaps=(1,))
    for i, x in enumerate(range(x0 + 128, x1 - 18, 20)):
        for y in range(139, 165):
            for xx in range(x, x + 17):
                u = (xx - x - 8) / 9
                band = y < 143 or y > 161
                cv.put(xx, y, TIN if band else REDP, 3.4 - u * 1.2 - u * u)
        for yy in (141, 162):                                       # els cèrcols de la llauna
            cv.hline(x + 1, x + 15, yy, TIN, 2.0)
        cv.hline(x + 3, x + 13, 150, YELL, 3.8)
        cv.disc(x + 8, 154, 3, 2, [(30, 80, 30), (60, 140, 50), (120, 190, 90)], 2.2)   # el tomàquet de l'etiqueta
    # a baix: sacs d'arròs (amb l'etiqueta) i una caixa de cebes
    for i, x in enumerate((x0 + 8, x0 + 51, x0 + 93)):
        cv.poly([(x, FLOOR_Y - 4), (x + 3, 176), (x + 11, 171), (x + 29, 171), (x + 37, 176), (x + 40, FLOOR_Y - 4)],
                JUTE, lambda xx, yy, x=x: 3.6 - (yy - 171) * 0.03 - abs(xx - x - 20) * 0.04)
        for yy in range(174, FLOOR_Y - 5, 3):                        # la trama del sac
            for xx in range(x + 4, x + 37, 4):
                if hr(xx, yy, i) > 0.4:
                    cv.put(xx, yy, JUTE, 2.6)
        cv.line(x + 14, 171, x + 20, 167, JUTE, 3.0)                 # el lligam de dalt
        cv.line(x + 20, 167, x + 26, 171, JUTE, 3.0)
        cv.rect(x + 8, 181, x + 32, 191, WHITEP, 3.6)
        cv.hline(x + 9, x + 31, 181, WHITEP, 4.8)
        s = 'ARRÒS'
        text(cv, s, x + 20 - text_width(s) // 2, 183, None, 0, flat=(150, 40, 34))
    cb0, cb1 = x0 + 147, x0 + 200
    box(cv, cb0, 176, cb1, FLOOR_Y - 4, WOOD, 3.4)
    for y in range(181, FLOOR_Y - 4, 7):
        cv.hline(cb0 + 1, cb1 - 1, y, WOOD, 2.2)
        cv.hline(cb0 + 1, cb1 - 1, y + 1, WOOD, 4.0)
    for i in range(12):
        cv.disc(cb0 + 6 + i * 4, 173 + int(hr(i, 7) * 3), 4, 3.5, ONION, lambda nx, ny: 3.4 - nx - ny)
        cv.put(cb0 + 6 + i * 4, 169 + int(hr(i, 7) * 3), ONION, 3.6)


def freezer_and_calendar(cv):
    """Un congelador d'arcó (blanc, vell) i el calendari del cuiner d'abans, encara del 2019."""
    x0, x1, top = 144, 237, 160
    box(cv, x0, top, x1, FLOOR_Y + 4, WHITEP, 3.6, grad=0.8)
    cv.rect(x0 - 1, top - 5, x1 + 1, top, WHITEP, 4.4)                # la tapa
    cv.hline(x0 - 1, x1 + 1, top - 5, WHITEP, 5.4)
    cv.hline(x0 - 1, x1 + 1, top + 1, WHITEP, 1.6)
    box(cv, (x0 + x1) // 2 - 11, top + 4, (x0 + x1) // 2 + 11, top + 8, CAB, 3.4)    # nansa
    cv.hline((x0 + x1) // 2 - 10, (x0 + x1) // 2 + 10, top + 4, CAB, 5.0)
    cv.flat(x1 - 11, top + 16, (90, 240, 120))                        # el pilot verd
    cv.flat(x1 - 10, top + 16, (60, 200, 90))
    glow(cv, x1 - 10, top + 16, 5, (90, 240, 120), 0.5)
    box(cv, x0 + 6, top + 22, x0 + 30, top + 30, WHITEP, 4.2)         # la placa de característiques
    for y in (top + 24, top + 27):
        cv.hline(x0 + 8, x0 + 28, y, CAB, 2.6)
    cv.rect(x0 + 5, FLOOR_Y - 5, x1 - 5, FLOOR_Y + 1, CAB, 1.6)      # reixeta
    for x in range(x0 + 6, x1 - 5, 2):
        cv.put(x, FLOOR_Y - 3, CAB, 3.0)
    for y in range(FLOOR_Y - 11, FLOOR_Y + 4):                       # un rovellet a la cantonada
        for x in range(x0, x0 + 5):
            if hr(x, y, 4) > 0.5:
                cv.put(x, y, [(60, 30, 16), (110, 60, 30), (150, 90, 50)], 1.6)
    # el calendari: un peix, l'any i una graella de dies
    cx0, cy0, cx1, cy1 = 165, 83, 211, 141
    box(cv, cx0, cy0, cx1, cy1, WHITEP, 4.2)
    cv.rect(cx0 + 2, cy0 + 2, cx1 - 2, cy0 + 26, [(10, 30, 50), (20, 60, 90), (40, 100, 130), (90, 150, 170)], 2.2)
    for x in range(cx0 + 2, cx1 - 1):                                 # onades al peu de la foto
        cv.put(x, cy0 + 22 + round(math.sin(x * 0.6)), [(40, 100, 130), (140, 190, 200)], 1.2)
    cv.disc(188, cy0 + 14, 12, 5, TIN, lambda nx, ny: 4.0 - ny * 1.4)            # el peix
    cv.poly([(199, cy0 + 14), (207, cy0 + 8), (207, cy0 + 20)], TIN, 3.6)
    cv.put(180, cy0 + 13, DARK, 0)
    for k in range(3):
        cv.vline(185 + k * 3, cy0 + 11, cy0 + 17, TIN, 3.0)                       # les escates
    text(cv, '2019', cx0 + 4, cy0 + 29, None, 0, flat=(150, 40, 34))
    for j in range(5):
        for i in range(7):
            cv.rect(cx0 + 5 + i * 6, cy0 + 37 + j * 4, cx0 + 6 + i * 6, cy0 + 37 + j * 4, CAB, 2.0)
    for dx, dy in ((2, 1), (4, 3)):                                   # dies encerclats en vermell
        cv.ring(cx0 + 5 + dx * 6, cy0 + 37 + dy * 4, 3, REDP, 4.0, step=30)
    cv.put((cx0 + cx1) // 2, cy0 - 3, CAB, 4.0)                       # el clau
    cv.put((cx0 + cx1) // 2, cy0 - 2, CAB, 2.4)


# ─── El registre del dipòsit 2 ────────────────────────────────────────────

REG = (112, 219, 216, 251)


def registre(cv):
    """La tapa del registre, a terra: planxa pintada de blau, frontisses a dalt, pany a baix."""
    x0, y0, x1, y1 = REG
    cv.poly([(x0 + 5, y0), (x1 - 5, y0), (x1, y1), (x0, y1)], DECK, lambda x, y: 1.8)
    cv.poly([(x0 + 9, y0 + 3), (x1 - 9, y0 + 3), (x1 - 4, y1 - 3), (x0 + 4, y1 - 3)], BLUEP,
            lambda x, y: 3.6 - (y - y0) * 0.025 + (hr(x // 3, y // 2, 8) - 0.5) * 0.4)
    cv.hline(x0 + 9, x1 - 9, y0 + 3, BLUEP, 5.0)
    cv.hline(x0 + 4, x1 - 4, y1 - 3, BLUEP, 2.2)
    cv.hline(x0, x1, y1, DECK, 4.2)
    for i in range(11):                                              # cargols de la vora
        t = i / 10
        bolt(cv, round(x0 + 7 + (x1 - x0 - 14) * t), y0 + 1, DECK, 4.0)
    for i in range(2):
        bolt(cv, x0 + 3 + i * (x1 - x0 - 7), y1 - 2, DECK, 4.0)
    for hx in (x0 + 24, x1 - 35):                                    # frontisses, a dalt
        box(cv, hx, y0 - 1, hx + 11, y0 + 5, CAB, 4.0)
        cv.hline(hx, hx + 11, y0 + 2, CAB, 5.4)
        bolt(cv, hx + 3, y0 + 3, CAB, 5.0)
        bolt(cv, hx + 8, y0 + 3, CAB, 5.0)
    s = 'AIGUA NO POTABLE'                                           # estergit en blanc
    text(cv, s, (x0 + x1) // 2 - text_width(s) // 2, y0 + 11, None, 0, flat=(200, 206, 210))
    cx = (x0 + x1) // 2
    lock(cv, cx, y1)
    cv.rect(cx - 21, y1 - 8, cx - 12, y1 - 5, DARK, 0.6)             # la nansa encastada
    cv.hline(cx - 21, cx - 12, y1 - 4, BLUEP, 5.0)


def lock(cv, cx, y1):
    """El pany de la tapa: una placa de llautó amb dos cargols i el forat de la clau."""
    box(cv, cx - 5, y1 - 12, cx + 5, y1 - 3, BRASS, 3.6)
    cv.hline(cx - 4, cx + 4, y1 - 12, BRASS, 5.0)
    cv.put(cx - 3, y1 - 10, BRASS, 5.4)
    cv.put(cx + 3, y1 - 10, BRASS, 5.4)
    cv.disc(cx, y1 - 8, 1.2, 1.2, DARK, 0.2)
    cv.vline(cx, y1 - 8, y1 - 5, DARK, 0.4)


def rascades(cv):
    """Escenes 4 i després: algú ha forçat el pany. La pintura saltada al voltant i rascades fresques."""
    x0, y0, x1, y1 = REG
    cx = (x0 + x1) // 2
    for y in range(y1 - 11, y1 - 3):
        for x in range(cx - 13, cx + 14):
            if hr(x, y, 21) > 0.35 and abs(x - cx) + abs(y - (y1 - 7)) * 2 < 17:
                cv.put(x, y, DECK, 4.6 + hr(x, y, 3))
    lock(cv, cx, y1)
    for i in range(9):
        sx = cx - 12 + int(hr(i, 1, 2) * 24)
        sy = y1 - 12 + int(hr(i, 2, 2) * 8)
        for k in range(4 + int(hr(i, 3) * 4)):
            cv.flat(sx + k, sy + (k // 2) * (1 if i % 2 else -1), (206, 214, 220))
    cv.flat(cx + 1, y1 - 7, (230, 236, 240))                         # el pany, torçat
    cv.flat(cx + 1, y1 - 6, (150, 156, 160))


def registre_obert(cv):
    """El registre obert: la tapa aixecada sobre les frontisses i el forat fosc, amb l'escala que baixa."""
    x0, y0, x1, y1 = REG
    hole = [(x0 + 9, y0 + 3), (x1 - 9, y0 + 3), (x1 - 4, y1 - 3), (x0 + 4, y1 - 3)]
    cv.poly(hole, DARK, lambda x, y: 2.4 - (y - y0) * 0.1, lit=0)
    cv.hline(x0 + 9, x1 - 9, y0 + 3, DECK, 3.4)
    cv.hline(x0 + 4, x1 - 4, y1 - 3, DECK, 3.6)
    cv.hline(x0 + 4, x1 - 4, y1 - 2, DECK, 2.0)
    for y in range(y0 + 4, y1 - 3):                                  # aigua tèrbola al fons, que brilla
        if hr(y, 5) > 0.6:
            cv.put(x0 + 40 + int(hr(y, 6) * 26), y, WHITEP, 0.6, lit=0)
    lx0, lx1 = (x0 + x1) // 2 - 9, (x0 + x1) // 2 + 9                # l'escala, que baixa i es perd
    for lx in (lx0, lx1):
        cv.vline(lx, y0 - 4, y1 - 5, CAB, lambda x, y: 5.8 - (y - y0) * 0.15)
        cv.vline(lx + 1, y0 - 4, y1 - 5, CAB, lambda x, y: 4.0 - (y - y0) * 0.15)
    for ry in range(y0 + 1, y1 - 5, 6):
        cv.hline(lx0 + 2, lx1 - 1, ry, CAB, 5.4 - (ry - y0) * 0.15)
        cv.hline(lx0 + 2, lx1 - 1, ry + 1, CAB, 3.0 - (ry - y0) * 0.15)
    for lx in (lx0, lx1):
        cv.put(lx, y0 - 5, CAB, 5.0)
        cv.put(lx + 1, y0 - 5, CAB, 3.6)
    # la tapa, aixecada i dreta: la cara de sota (planxa sense pintar, rovell i la junta de goma)
    ty = y0 - 40
    lid = [(x0 + 12, ty), (x1 - 12, ty), (x1 - 9, y0 + 1), (x0 + 9, y0 + 1)]
    cv.poly(lid, CAB, lambda x, y: 4.6 + (y - ty) * 0.015 - (x - x0) * 0.008 + (hr(x // 2, y // 2, 4) - 0.5) * 0.5)
    cv.poly([(x0 + 16, ty + 4), (x1 - 16, ty + 4), (x1 - 13, y0 - 3), (x0 + 13, y0 - 3)], DARK, 2.4)
    cv.poly([(x0 + 19, ty + 7), (x1 - 19, ty + 7), (x1 - 16, y0 - 5), (x0 + 16, y0 - 5)], CAB,
            lambda x, y: 4.0 + (y - ty) * 0.015 - (x - x0) * 0.008 + (hr(x // 3, y // 2, 9) - 0.5) * 0.6)
    for i in range(22):                                              # rovell
        rx = x0 + 21 + int(hr(i, 11) * (x1 - x0 - 42))
        ry = ty + 8 + int(hr(i, 12) * 29)
        cv.put(rx, ry, [(40, 18, 10), (80, 36, 18), (120, 60, 28), (150, 86, 44)], 1.6 + hr(i, 13) * 1.4)
        cv.put(rx + 1, ry, [(40, 18, 10), (80, 36, 18), (120, 60, 28), (150, 86, 44)], 1.2)
        if hr(i, 14) > 0.5:
            cv.put(rx, ry + 1, [(40, 18, 10), (80, 36, 18), (120, 60, 28)], 1.0)
    cv.hline(x0 + 12, x1 - 12, ty, BLUEP, 5.0)                        # el cantell de dalt (pintat)
    cv.hline(x0 + 12, x1 - 12, ty + 1, BLUEP, 3.6)
    cv.line(x0 + 12, ty, x0 + 9, y0 + 1, BLUEP, 4.4)
    cv.line(x1 - 12, ty, x1 - 9, y0 + 1, BLUEP, 2.6)
    cv.hline(x0 + 26, x1 - 26, (ty + y0) // 2, CAB, 5.2)             # el reforç
    cv.hline(x0 + 26, x1 - 26, (ty + y0) // 2 + 1, CAB, 3.0)
    for hx in (x0 + 24, x1 - 35):                                    # les frontisses, ara tombades
        box(cv, hx, y0 - 3, hx + 11, y0 + 3, CAB, 4.4)
        bolt(cv, hx + 3, y0, CAB, 5.0)
        bolt(cv, hx + 8, y0, CAB, 5.0)
    floor_shadow(cv, (x0 + x1) // 2, y0 - 5, 40, 3, 0.4)


# ─── Muntatge ─────────────────────────────────────────────────────────────

def bg(cv):
    room(cv)
    door(cv)
    dumbwaiter(cv)
    shelves(cv)
    stool(cv)
    freezer_and_calendar(cv)
    checker_floor(cv)
    floor_shadow(cv, 117, FLOOR_Y + 7, 21, 4, 0.6)
    floor_shadow(cv, 191, FLOOR_Y + 5, 53, 5, 0.6)
    floor_shadow(cv, 504, FLOOR_Y + 4, 128, 7, 0.5)
    registre(cv)
    for lx in LAMP_X:
        lamp_glow(cv, lx)


def safata(cv):
    """Una safata d'acer al replà del muntacàrregues (el que hi ha a sobre, a `objecte`)."""
    x0, y0, x1, y1 = MUNTA
    cv.poly([(x0 + 3, y1 - 4), (x1 - 3, y1 - 4), (x1 + 1, y1), (x0 - 1, y1)], CAB, 4.4)
    cv.hline(x0 - 1, x1 + 1, y1, CAB, 2.2)
    cv.hline(x0 + 3, x1 - 3, y1 - 4, CAB, 5.4)
    for hx in (x0 + 1, x1 - 4):                                      # les nanses de la safata
        cv.hline(hx, hx + 3, y1 - 2, CAB, 1.6)


def porta_tancada(cv):
    """La portella de guillotina baixada (el muntacàrregues en marxa): tapa l'obertura, amb la nansa a baix."""
    x0, y0, x1, y1 = MUNTA
    box(cv, x0, y0 + 19, x1, y1, CAB, 3.6)
    for y in range(y0 + 23, y1 - 6, 4):
        cv.hline(x0 + 4, x1 - 4, y, CAB, 2.6)
        cv.hline(x0 + 4, x1 - 4, y + 1, CAB, 4.4)
    box(cv, (x0 + x1) // 2 - 7, y1 - 4, (x0 + x1) // 2 + 7, y1 - 1, BRASS, 3.4)
    cv.hline((x0 + x1) // 2 - 6, (x0 + x1) // 2 + 6, y1 - 4, BRASS, 5.0)
    # a dalt, on era la portella, el pou buit
    box(cv, x0, y0, x1, y0 + 16, DARK, 1.2)


def objecte(cv, item):
    """L'objecte que ha arribat, damunt la safata."""
    from hd640.safata import posa
    x0, y0, x1, y1 = MUNTA
    posa(cv, item, (x0 + x1) / 2, y1 - 2, 44)


PROPS = {'safata': safata, 'rascades': rascades, 'registre_obert': registre_obert}


# ─── Animacions ─────────────────────────────────────────────────────────────
# Els fotogrames es pinten directament en un llenç transparent amb el color barrejat amb el fons (el mateix que
# _diff, però sense comparar la sala sencera a cada fotograma).

@lru_cache(maxsize=1)
def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv.img


def _frames_pols():
    """Pols que sura a la llum dels dos llums de gàbia (cada mota fa un llaç tancat: el bucle no salta)."""
    src = _base().load()
    S = _base().width // W                                           # (fotogrames a la mida de l'art)
    motes = []
    for lx in LAMP_X:
        for k in range(19):
            motes.append((lx + (hr(k, lx, 1) - 0.5) * 93, 59 + hr(k, lx, 2) * 107,
                          8 + hr(k, lx, 3) * 13, 5 + hr(k, lx, 4) * 11, hr(k, lx, 5), 1 + int(hr(k, lx, 6) * 2), lx))
    n = 48
    frames = []
    for i in range(n):
        img = Image.new('RGBA', _base().size, (0, 0, 0, 0))
        p = img.load()
        t = i / n
        for (cx, cy, ax, ay, ph, fx, lx) in motes:
            a = 2 * math.pi * (t + ph)
            x = round(cx + ax * math.sin(fx * a))
            y = round(cy + ay * math.sin(a + ph * 3))
            near = max(0.0, 1 - math.hypot(x - lx, (y - 35) * 0.9) / 187)
            tw = 0.5 + 0.5 * math.sin(a * 2 + ph * 7)
            alpha = near * (0.5 + 0.5 * tw)
            if alpha > 0.08 and 0 <= x < W and 0 <= y < FLOOR_Y:
                for dy in range(S):
                    for dx in range(S):
                        p[x * S + dx, y * S + dy] = mix(src[x * S + dx, y * S + dy][:3], (255, 236, 196), alpha) + (255,)
        frames.append(img)
    return frames


MOUSE = [(70, 62, 60), (104, 94, 90), (138, 128, 120)]


def _mouse(p, src, x, y, out, sniff):
    """El cap del ratolí que treu el morro d'entre dos sacs (x, y: l'espatlla, a terra; out: quant surt)."""
    S = _base().width // W                                           # un píxel de sala = un bloc S×S

    def put(px, py, col):
        for dy in range(S):
            for dx in range(S):
                p[px * S + dx, py * S + dy] = col + (255,)
    for dx in range(out):
        top = y - 4 + (1 if dx >= out - 2 else 0)
        for yy in range(top, y + 1):
            put(x + dx, yy, MOUSE[0] if yy == y else MOUSE[1] if yy > top else MOUSE[2])
    if out >= 4:
        put(x + 1, y - 5, (150, 104, 104))                           # l'orella
        put(x + 2, y - 5, (110, 80, 80))
        put(x + 1, y - 6, (150, 104, 104))
        put(x + out - 3, y - 3, (12, 10, 12))                        # l'ull, amb la lluentor
        if out > 5:
            put(x + out - 3, y - 4, (200, 200, 200))
        put(x + out, y - 1 - sniff, (190, 120, 120))                 # el nas, que olora
        for k in (1, 2):                                             # bigotis
            px, py = x + out + k, y - 2 - sniff + (k - 1)
            put(px, py, mix(src[px * S, py * S][:3], (200, 200, 190), 0.5))


def _frames_ratoli():
    """Un ratolí treu el cap d'entre els sacs d'arròs, olora i s'hi torna a amagar."""
    src = _base().load()
    mx, my = 471, FLOOR_Y - 6
    seq = [(0, 0)] * 20 + [(1, 0), (3, 0), (4, 0), (5, 0)] + [(7, i % 2) for i in range(10)] + \
          [(7, 0)] * 6 + [(7, i % 2) for i in range(6)] + [(4, 0), (1, 0)] + [(0, 0)] * 10
    frames = []
    for out, sniff in seq:
        img = Image.new('RGBA', _base().size, (0, 0, 0, 0))
        if out:
            _mouse(img.load(), src, mx, my, out, sniff)
        frames.append(img)
    return frames


ANIMS = {'pols': {'frames': _frames_pols, 'frameDuration': 130},
         'ratoli': {'frames': _frames_ratoli, 'frameDuration': 110}}


# ─── Geometria (coordenades de 640×360) ─────────────────────────────────────
