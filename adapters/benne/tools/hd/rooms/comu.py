"""
Eines i rampes comunes de les sales de Suma Zero (vénen de la sala de mostra): contorns, capses,
cables, el pòster del gat i el 404, i el càlcul dels fotogrames d'animació.
"""
import math

from hd.pix import W, H, hr

PLASTIC = [(8, 8, 14), (16, 16, 24), (26, 26, 36), (40, 40, 52), (58, 58, 72), (82, 82, 98)]
SCREEN = [(6, 20, 26), (10, 40, 44), (16, 70, 66), (30, 110, 96), (60, 160, 130), (120, 220, 180), (200, 255, 230)]
SKY = [(6, 6, 20), (10, 12, 32), (16, 20, 48), (24, 30, 66), (36, 42, 86), (52, 56, 104)]
CITY = [(4, 4, 12), (10, 10, 24), (18, 16, 36), (28, 24, 50)]
NEON = [(60, 10, 40), (140, 20, 90), (220, 50, 150), (255, 120, 200), (255, 200, 240)]
SHEET = [(40, 36, 52), (70, 66, 84), (110, 106, 120), (150, 146, 156), (190, 186, 190), (222, 220, 218)]
CARD = [(40, 24, 14), (70, 44, 24), (106, 70, 38), (146, 102, 58), (184, 136, 80), (216, 172, 108), (240, 206, 146)]
RED = [(40, 6, 12), (80, 14, 20), (130, 26, 30), (180, 44, 40), (220, 80, 60), (246, 130, 100)]
GRAYC = [(12, 12, 18), (26, 26, 34), (44, 44, 54), (66, 66, 78), (94, 94, 106), (130, 130, 140)]
YEL = [(50, 36, 6), (110, 80, 10), (180, 136, 20), (230, 190, 50), (250, 230, 120)]


def outline(cv, x0, y0, x1, y1, ramp):
    """Contorn fosc d'un rectangle (l'estil de dibuix animat de tot el joc)."""
    for x in range(x0, x1 + 1):
        cv.flat(x, y0, ramp[0])
        cv.flat(x, y1, ramp[0])
    for y in range(y0, y1 + 1):
        cv.flat(x0, y, ramp[0])
        cv.flat(x1, y, ramp[0])


def obox(cv, x0, y0, x1, y1, ramp, lvl, top=1.0, side=-0.8, lit=1.0):
    """Capsa plena amb llum a dalt, ombra a la dreta i contorn."""
    cv.rect(x0, y0, x1, y1, ramp, lambda x, y: lvl + (top if y == y0 + 1 else 0) + (side if x >= x1 - 1 else 0), lit)
    outline(cv, x0, y0, x1, y1, ramp)


def cable(cv, pts, ramp, lvl=2.0, thick=1):
    """Cable que penja: una corba de Bézier per punts de control."""
    n = 80
    for i in range(n + 1):
        t = i / n
        p = list(pts)
        while len(p) > 1:
            p = [((a[0] * (1 - t) + b[0] * t), (a[1] * (1 - t) + b[1] * t)) for a, b in zip(p, p[1:])]
        x, y = p[0]
        for d in range(thick):
            cv.put(round(x), round(y) + d, ramp, lvl + (0.6 if d == 0 else 0))
        cv.flat(round(x), round(y) + thick, ramp[0])


def poster(cv):
    x0, y0, x1, y1 = 150, 36, 190, 92
    obox(cv, x0, y0, x1, y1, SHEET, 3.4)
    # un gat amb ulleres de sol i el text «HANG IN THERE»... en versió hacker: un gat i «404»
    cv.rect(x0 + 3, y0 + 3, x1 - 3, y1 - 16, SKY, 2.6)
    cv.disc(170, 58, 9, 8, GRAYC, lambda nx, ny: 3.0 - ny)
    cv.poly([(162, 52), (163, 44), (168, 50)], GRAYC, 3.2)
    cv.poly([(178, 52), (177, 44), (172, 50)], GRAYC, 3.2)
    cv.rect(163, 56, 168, 58, PLASTIC, 0.5)
    cv.rect(172, 56, 177, 58, PLASTIC, 0.5)
    cv.hline(168, 172, 57, PLASTIC, 0.5)
    digits = {'4': ['101', '101', '111', '001', '001'], '0': ['111', '101', '101', '101', '111']}
    x = 159
    for ch in '404':
        for j, row in enumerate(digits[ch]):
            for i, b in enumerate(row):
                if b == '1':
                    cv.rect(x + i * 2, 78 + j * 2, x + i * 2 + 1, 78 + j * 2 + 1, RED, 3.2)
        x += 8
    # cinta adhesiva als cantons
    for cx, cy in ((x0, y0), (x1, y0)):
        cv.rect(cx - 3, cy - 1, cx + 3, cy + 2, YEL, 3.0)


def _diff(frame, base):
    """Només els píxels que canvien respecte del fons (la resta, transparent)."""
    out = frame.copy()
    a, b, o = frame.load(), base.load(), out.load()
    for y in range(H):
        for x in range(W):
            if a[x, y] == b[x, y]:
                o[x, y] = (0, 0, 0, 0)
    return out


# ─── Text petit (rètols, cartells, pantalles) ──────────────────────────────
# Lletres de 5 píxels d'alt (la majoria de 3 d'ample). Només majúscules, xifres i quatre signes.
GLYPHS = {
    'A': ['010', '101', '111', '101', '101'], 'B': ['110', '101', '110', '101', '110'], 'C': ['011', '100', '100', '100', '011'],
    'D': ['110', '101', '101', '101', '110'], 'E': ['111', '100', '110', '100', '111'], 'F': ['111', '100', '110', '100', '100'],
    'G': ['011', '100', '101', '101', '011'], 'H': ['101', '101', '111', '101', '101'], 'I': ['111', '010', '010', '010', '111'],
    'J': ['001', '001', '001', '101', '010'], 'K': ['101', '101', '110', '101', '101'], 'L': ['100', '100', '100', '100', '111'],
    'M': ['10001', '11011', '10101', '10001', '10001'], 'N': ['1001', '1101', '1011', '1001', '1001'], 'O': ['010', '101', '101', '101', '010'],
    'P': ['110', '101', '110', '100', '100'], 'Q': ['010', '101', '101', '110', '011'], 'R': ['110', '101', '110', '101', '101'],
    'S': ['011', '100', '010', '001', '110'], 'T': ['111', '010', '010', '010', '010'], 'U': ['101', '101', '101', '101', '111'],
    'V': ['101', '101', '101', '101', '010'], 'W': ['10001', '10001', '10101', '11011', '10001'], 'X': ['101', '101', '010', '101', '101'],
    'Y': ['101', '101', '010', '010', '010'], 'Z': ['111', '001', '010', '100', '111'],
    '0': ['111', '101', '101', '101', '111'], '1': ['010', '110', '010', '010', '111'], '2': ['110', '001', '010', '100', '111'],
    '3': ['110', '001', '010', '001', '110'], '4': ['101', '101', '111', '001', '001'], '5': ['111', '100', '110', '001', '110'],
    '6': ['011', '100', '110', '101', '010'], '7': ['111', '001', '010', '010', '010'], '8': ['010', '101', '010', '101', '010'],
    '9': ['010', '101', '011', '001', '110'], '(': ['01', '10', '10', '10', '01'], ')': ['10', '01', '01', '01', '10'],
    '-': ['000', '000', '111', '000', '000'], '.': ['0', '0', '0', '0', '1'], ',': ['00', '00', '00', '01', '10'],
    ':': ['0', '1', '0', '1', '0'], '!': ['1', '1', '1', '0', '1'], '€': ['011', '100', '111', '100', '011'], "'": ['1', '1', '0', '0', '0'],
    '/': ['001', '001', '010', '100', '100'], ' ': ['00', '00', '00', '00', '00'],
}


def text_width(s):
    return sum(len(GLYPHS.get(ch, GLYPHS[' '])[0]) + 1 for ch in s) - 1


def text(cv, s, x, y, ramp, lvl, lit=1.0, mirror=False, flat=None):
    """Escriu `s` amb la font petita a (x, y) (cantó de dalt a l'esquerra). `mirror`: de darrere un vidre."""
    w = text_width(s)
    cx = x
    for ch in s:
        g = GLYPHS.get(ch, GLYPHS[' '])
        for j, row in enumerate(g):
            for i, bit in enumerate(row):
                if bit == '1':
                    px = cx + i
                    if mirror:
                        px = x + w - 1 - (px - x)
                    if flat:
                        cv.flat(px, y + j, flat)
                    else:
                        cv.put(px, y + j, ramp, lvl, lit)
        cx += len(g[0]) + 1
    return w
