"""
Eines i rampes comunes de les sales de l'Arenga (vénen de la sala de mostra, guio/art/mostra/sala_maquines.py):
les rampes de color (fosc → clar), capses amb vora, tubs amb volum, reblons, cantonades rodones i llums.

Cada sala és un mòdul hd/rooms/<sala>.py amb `LIGHT`, `bg(cv)`, `PROPS` (i, si cal, `ANIMS`, `FRONT`) i la seva
`GEOMETRIA` (`things`, `spawns`, `walkable`), que substitueix la de room_designs.py.
Línies de referència: el terra comença a FLOOR_Y; per sota de y=195 hi ha la frase i la barra de verbs.
"""
import math

from hd.pix import Canvas, Light, W, H, hr, mix, GOLD, RUST, B4  # noqa: F401

# ─── Rampes (fosc → clar) ───────────────────────────────────────────────────
WALL = [(5, 10, 11), (9, 18, 18), (14, 27, 26), (21, 38, 35), (30, 51, 46), (41, 66, 58), (55, 84, 72),
        (73, 104, 88), (96, 128, 108), (126, 154, 132)]
ENG = [(6, 10, 15), (11, 17, 25), (18, 26, 36), (27, 37, 49), (38, 51, 65), (52, 68, 84), (70, 89, 106),
       (93, 114, 130), (122, 142, 156), (160, 176, 186)]
ENG_LIGHT = [(10, 15, 22), (18, 26, 36), (27, 37, 50), (38, 51, 66), (52, 68, 86), (68, 88, 108),
             (88, 110, 130), (112, 134, 152), (142, 162, 176), (180, 194, 202)]
DECK = [(5, 7, 9), (10, 12, 16), (17, 20, 25), (26, 30, 36), (37, 42, 49), (51, 56, 64), (69, 74, 82),
        (92, 97, 104)]
CAB = [(8, 10, 12), (15, 17, 21), (24, 27, 32), (35, 39, 45), (49, 54, 60), (66, 71, 77), (88, 93, 98),
       (116, 120, 124), (150, 154, 156)]
LAG = [(36, 32, 30), (62, 56, 50), (94, 86, 74), (128, 118, 100), (162, 150, 126), (194, 182, 154),
       (222, 212, 186), (240, 234, 214)]
REDP = [(28, 6, 8), (56, 12, 14), (90, 20, 20), (130, 30, 28), (170, 48, 38), (206, 78, 56), (236, 122, 90)]
YELL = [(36, 28, 6), (78, 58, 10), (128, 96, 16), (178, 136, 24), (218, 174, 42), (244, 210, 88)]
SEAG = [(6, 22, 16), (10, 38, 28), (16, 58, 42), (26, 82, 58), (40, 108, 76), (62, 138, 98)]
FUEL = [(26, 14, 8), (48, 26, 12), (76, 42, 18), (106, 62, 26), (138, 86, 38), (170, 114, 56)]
SEP = [(30, 28, 18), (56, 52, 34), (88, 82, 54), (122, 114, 78), (156, 148, 104), (188, 180, 134),
       (216, 210, 168), (236, 232, 200)]
DARK = [(2, 3, 5), (5, 7, 10), (9, 12, 16), (14, 18, 23), (20, 25, 31), (28, 34, 41)]
WHITEP = [(40, 42, 46), (80, 84, 88), (130, 134, 136), (180, 182, 180), (214, 214, 208), (236, 236, 228)]
BRASS = GOLD
WARM = (255, 214, 140)
RED_GLOW = (255, 60, 40)

FLOOR_Y = 152          # on la paret es troba amb el terra
BOTTOM = 195           # per sota hi ha la franja de la frase i la barra de verbs
LAMPS = ((160, 22), (372, 22))

# ─── Ajudes ─────────────────────────────────────────────────────────────────

def box(cv, x0, y0, x1, y1, ramp, lvl, edge=True, grad=0.0):
    """Capsa plana amb vora: llum a dalt i a l'esquerra, ombra a baix i a la dreta."""
    cv.rect(x0, y0, x1, y1, ramp, lambda x, y: lvl - grad * (y - y0) / max(1, y1 - y0))
    if edge:
        cv.hline(x0, x1, y0, ramp, lvl + 1.2)
        cv.vline(x0, y0, y1, ramp, lvl + 0.7)
        cv.hline(x0, x1, y1, ramp, lvl - 1.4)
        cv.vline(x1, y0, y1, ramp, lvl - 1.0)


def rrect(cv, x0, y0, x1, y1, r, ramp, lvl):
    """Rectangle de cantons rodons."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            dx = max(x0 + r - x, 0, x - (x1 - r))
            dy = max(y0 + r - y, 0, y - (y1 - r))
            if dx * dx + dy * dy <= r * r:
                cv.put(x, y, ramp, lvl(x, y) if callable(lvl) else lvl)


def bolt(cv, x, y, ramp, lvl):
    cv.put(x, y, ramp, lvl + 1.4)
    cv.put(x + 1, y + 1, ramp, lvl - 1.2)


def hpipe(cv, x0, x1, yc, r, ramp, lvl, bands=(), band_ramp=None):
    """Tub horitzontal amb volum (cilindre) i anelles de color."""
    for x in range(x0, x1 + 1):
        band = any(b <= x < b + 3 for b in bands)
        for y in range(yc - r, yc + r + 1):
            u = (y - yc) / (r + 0.5)
            shade = 1.4 * (0.35 - u) - 0.6 * u * u
            cv.put(x, y, band_ramp if band else ramp, lvl + shade)


def vpipe(cv, xc, y0, y1, r, ramp, lvl, bands=(), band_ramp=None):
    for y in range(y0, y1 + 1):
        band = any(b <= y < b + 3 for b in bands)
        for x in range(xc - r, xc + r + 1):
            u = (x - xc) / (r + 0.5)
            shade = 1.4 * (-0.2 - u) - 0.6 * u * u
            cv.put(x, y, band_ramp if band else ramp, lvl + shade)


def glow(cv, x, y, r, col, k):
    cv.glow(x, y, r, col, k)


