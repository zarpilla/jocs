"""
Aigua Verne — peces comunes de les sales de Verdant (verdant_jardi, verdant_cobert, verdant_residencia).

Verdant és el planeta dels rics: tot és de plàstic, massa net i massa saturat. Les rampes d'aquí són les del
«món d'anunci» (gespa artificial, flors de colors impossibles, blancs que brillen, cel blau de catàleg) i les del
món humà que hi ha amagat (la fusta vella del cobert, el zinc de la galleda, la tomaquera de debò).
"""
import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)

import math

from hd.pix import hr, GOLD
from hd.rooms.comu import text, text_width
from hd.rooms.exterior import fbm, smooth  # noqa: F401

# ─── Rampes (fosc → clar) ───────────────────────────────────────────────────
# El món d'anunci
SKYV = [(18, 58, 168), (24, 80, 200), (34, 104, 226), (52, 130, 242), (82, 160, 250), (124, 192, 255),
        (172, 220, 255), (214, 240, 255)]
CLOUDV = [(120, 156, 214), (160, 192, 236), (198, 222, 250), (230, 242, 255), (250, 253, 255), (255, 255, 255)]
TURF = [(0, 44, 22), (0, 72, 30), (4, 104, 36), (18, 138, 42), (40, 172, 48), (84, 204, 58), (140, 230, 84),
        (196, 248, 132)]
HILLV = [(30, 110, 90), (50, 140, 100), (76, 168, 108), (110, 196, 120), (150, 220, 140), (190, 236, 170)]
WHITEV = [(70, 86, 120), (118, 134, 166), (164, 178, 204), (204, 214, 232), (230, 236, 248), (246, 249, 255),
          (255, 255, 255)]
MARBLE = [(120, 120, 132), (170, 170, 180), (206, 204, 210), (230, 228, 232), (244, 242, 244), (252, 251, 250),
          (255, 255, 255)]
GOLDV = GOLD
GLASSV = [(16, 40, 80), (28, 66, 120), (46, 100, 160), (80, 140, 200), (140, 190, 236), (210, 236, 255)]
# Flors de plàstic: colors que no hi ha a la natura
MAGENTA = [(90, 0, 60), (170, 0, 110), (236, 20, 160), (255, 90, 200), (255, 180, 236)]
CYANF = [(0, 60, 110), (0, 130, 190), (0, 200, 240), (90, 240, 255), (200, 255, 255)]
YELLOWF = [(110, 70, 0), (200, 150, 0), (255, 220, 0), (255, 246, 90), (255, 255, 200)]
ORANGEF = [(110, 20, 0), (200, 50, 0), (255, 96, 10), (255, 160, 60), (255, 220, 150)]
VIOLETF = [(50, 0, 100), (100, 20, 180), (160, 60, 255), (200, 130, 255), (236, 200, 255)]
FLOWERS = (MAGENTA, CYANF, YELLOWF, ORANGEF, VIOLETF)
# El món de debò
WOODG = [(40, 36, 32), (66, 60, 52), (96, 88, 76), (126, 118, 102), (156, 148, 130), (186, 178, 160)]
PLANK = [(28, 18, 14), (46, 30, 20), (68, 46, 30), (92, 64, 40), (118, 84, 52), (144, 106, 66), (170, 130, 84),
         (196, 158, 108)]
SHEDG = [(16, 34, 24), (28, 54, 36), (42, 76, 50), (60, 98, 64), (82, 122, 80), (108, 146, 100), (140, 170, 126)]
ZINC = [(40, 44, 50), (66, 72, 78), (96, 102, 106), (128, 134, 136), (162, 166, 166), (196, 198, 196),
        (226, 228, 224)]
TERRACOTA = [(50, 20, 12), (86, 36, 20), (124, 56, 30), (160, 80, 44), (192, 108, 64), (220, 140, 90)]
LEAF = [(18, 34, 10), (30, 56, 16), (46, 82, 22), (66, 110, 30), (92, 140, 40), (126, 170, 60)]
DRYLEAF = [(40, 28, 12), (72, 52, 22), (106, 80, 36), (140, 110, 54), (172, 142, 78), (200, 174, 108)]
TOMATO = [(70, 8, 6), (130, 18, 10), (190, 36, 18), (230, 70, 36), (255, 130, 90), (255, 200, 170)]
BLACKT = [(10, 10, 12), (22, 22, 24), (36, 36, 38), (54, 54, 56), (76, 76, 78)]
HOSE = [(8, 10, 8), (18, 22, 18), (32, 38, 32), (52, 60, 52), (80, 90, 80)]
LED = [(30, 6, 4), (90, 20, 10), (180, 50, 20), (250, 120, 40), (255, 200, 120)]
BLUEG = [(10, 30, 70), (20, 60, 130), (40, 100, 190), (90, 160, 230), (170, 210, 250), (230, 244, 255)]
# La Cantimplora (nau cisterna vella)
OLIVE = [(20, 24, 12), (34, 40, 20), (50, 58, 28), (68, 78, 38), (88, 98, 50), (110, 120, 66), (136, 144, 88)]
SAFETY = [(70, 20, 4), (130, 46, 8), (196, 84, 14), (236, 124, 26), (255, 170, 70)]
RUSTV = [(40, 16, 10), (74, 32, 16), (110, 52, 24), (146, 76, 34), (178, 104, 52)]


# ─── Logotip i rètols ──────────────────────────────────────────────────────

# xifres quadrades de 3×5, de pantalla (les del panell del preu, com a la mostra de la granja)
DIGITS = {d: [g[i:i + 3] for i in range(0, 15, 3)] for d, g in {
    '0': '111101101101111', '1': '010110010010111', '2': '111001111100111', '3': '111001111001111',
    '4': '101101111001001', '5': '111100111001111', '6': '111100111101111', '7': '111001010010010',
    '8': '111101111101111', '9': '111101111001111'}.items()}

def gota(cv, cx, cy, s=1.0, lit=0):
    """La gota blava de Verne (el logotip): una gota de cap per amunt, amb un reflex."""
    if s < 1:                                                         # en petit, dibuixada a mà
        cv.sprite(['..a..', '.aaa.', 'abaaa', 'aaaac', '.acc.'], cx - 2, cy - 3,
                  {'a': BLUEG[2], 'b': BLUEG[5], 'c': BLUEG[1]}, lit=lit)
        return
    r = 3.0 * s
    cv.disc(cx, cy, r, r * 1.05, BLUEG, lambda nx, ny: 2.6 - nx * 0.8 - ny * 0.6, lit=lit)
    for k in range(1, int(4 * s) + 1):
        w = r * (1 - k / (4 * s + 1))
        cv.rect(cx - w + 0.5, cy - r - k + 0.5, cx + w - 0.5, cy - r - k + 0.5, BLUEG, 2.4 + k * 0.1, lit=lit)
    cv.flat(cx - max(1, round(r * 0.4)), cy - max(0, round(r * 0.2)), BLUEG[5])


def panell_preu(cv, x0, y0, num='', post=40, w=46):
    """El panell del preu: pantalla negra amb la gota, «VERNE», el preu en taronja amb la fletxa i una barra
    que s'omple. Damunt d'un pal blanc de Verdant (polit, com tot)."""
    h = 26
    cx = x0 + w // 2
    cv.rect(cx - 1, y0 + h, cx + 1, y0 + h + post, WHITEV, lambda x, y: 5.0 - (x - cx + 1) * 1.2)
    cv.rect(cx - 4, y0 + h + post - 2, cx + 4, y0 + h + post, WHITEV, 3.6)
    cv.rect(x0 - 1, y0 - 1, x0 + w + 1, y0 + h + 1, WHITEV, lambda x, y: 4.6 if y == y0 - 1 else 3.2)   # el marc
    cv.rect(x0, y0, x0 + w, y0 + h, BLACKT, 1.2, lit=0)
    cv.hline(x0, x0 + w, y0, BLACKT, 3.0, lit=0)
    gota(cv, x0 + 6, y0 + 8, 0.9)
    text(cv, 'VERNE', x0 + 12, y0 + 3, None, 0, flat=(210, 224, 240))
    x = x0 + 13 if num else x0 + 14
    for ch in num:                                                     # el preu, xifres de 3×5 a doble alçada
        g = DIGITS[ch]
        for j, row in enumerate(g):
            for i, bit in enumerate(row):
                if bit == '1':
                    cv.flat(x + i, y0 + 11 + j * 2, LED[3])
                    cv.flat(x + i, y0 + 12 + j * 2, LED[2] if j == 4 else LED[3])
        x += 4
    for j in range(4):                                                 # ▲
        for i in range(-j, j + 1):
            cv.flat(x + 4 + i, y0 + 13 + j, LED[3])
    for i in range(w - 6):                                             # la barra, plena a les dues terceres parts
        on = i < (w - 6) * 0.66
        cv.flat(x0 + 3 + i, y0 + h - 3, LED[3] if on else BLACKT[3])
        cv.flat(x0 + 3 + i, y0 + h - 2, LED[2] if on else BLACKT[2])
    cv.glow(x0 + w // 2, y0 + 16, 16, (255, 140, 60), 0.12)


# ─── Natura de plàstic ─────────────────────────────────────────────────────

def flor(cv, x, y, ramp, size=2, lit=1.0):
    """Una flor de plàstic: cinc pètals rodons perfectes i el botó del mig (sempre groc, o blanc si és groga)."""
    if size <= 1:
        cv.put(x, y, ramp, 3.4, lit)
        cv.put(x + 1, y, ramp, 2.4, lit)
        cv.put(x, y - 1, ramp, 4.0, lit)
        return
    for k in range(5):
        a = k * 2 * math.pi / 5 - math.pi / 2
        px, py = x + math.cos(a) * size * 0.9, y + math.sin(a) * size * 0.75
        cv.disc(px, py, size * 0.7, size * 0.6, ramp, lambda nx, ny: 3.2 - nx * 0.6 - ny * 0.8, lit=lit)
    mid = WHITEV if ramp is YELLOWF else YELLOWF
    cv.put(x, y, mid, 3.4, lit)
    cv.put(x + 1, y, mid, 2.6, lit)


def tija(cv, x, y0, y1, lvl=3.4, lit=1.0):
    for y in range(int(y0), int(y1) + 1):
        cv.put(x, y, TURF, lvl, lit)


def arbre_rodo(cv, x, base, r, lit=1.0, trunk=WHITEV):
    """Un arbre de piruleta: tronc blanc i una bola verda perfecta, amb el reflex de plàstic."""
    th = int(r * 1.3)
    cv.rect(x - 1, base - th, x + 1, base, trunk, lambda xx, yy: 4.4 - (xx - x + 1) * 0.9, lit=lit)
    cv.disc(x, base - th - r + 2, r, r, TURF,
            lambda nx, ny: 3.6 - nx * 1.0 - ny * 1.4 + (0.5 if (nx * nx + ny * ny) > 0.85 else 0) * -1, lit=lit)
    # el reflex: una taca blanca de plàstic, massa brillant
    cv.disc(x - r * 0.35, base - th - r * 1.4 + 2, max(1.0, r * 0.22), max(1.0, r * 0.16), TURF, 7.0, lit=0)


def bola_boix(cv, x, base, r, lit=1.0):
    """Un boix retallat en bola perfecta, en un test blanc."""
    cv.poly([(x - r * 0.7, base - r * 0.8), (x + r * 0.7, base - r * 0.8), (x + r * 0.55, base), (x - r * 0.55, base)],
            WHITEV, lambda xx, yy: 4.6 - (xx - x) / r * 1.2, lit=lit)
    cv.hline(x - r * 0.7, x + r * 0.7, base - r * 0.8, WHITEV, 5.6, lit=lit)
    cv.hline(x - r * 0.55, x + r * 0.55, base - r * 0.4, GOLDV, 4.4, lit=lit)
    cy = base - r * 0.8 - r + 1
    cv.disc(x, cy, r, r, TURF, lambda nx, ny: 3.6 - nx * 1.1 - ny * 1.3 +
            (0.6 if hr(int(nx * 9), int(ny * 9), 5) > 0.7 else 0), lit=lit)
    cv.disc(x - r * 0.4, cy - r * 0.45, max(1.0, r * 0.2), max(1.0, r * 0.14), TURF, 7.0, lit=0)


def ombra(cv, cx, cy, rx, ry, k=0.85):
    cv.darken(cx - rx - 2, cy - ry - 2, cx + rx + 2, cy + ry + 2,
              lambda x, y: k if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1 else 0)


def rotul(cv, s, cx, y, col):
    """Text centrat amb la font petita, de color pla."""
    w = text_width(s)
    text(cv, s, cx - w // 2, y, None, 0, flat=col)
    return w


def galleda(cv, x, y, s=1.0, lit=1.0, plena=False):
    """La galleda d'en Nil: zinc vell, abonyegada, amb la nansa. (x, y) és el centre de la base."""
    top_w, bot_w, h = 12 * s, 9 * s, 20 * s
    ytop = y - h
    for yy in range(int(ytop), int(y) + 1):
        t = (yy - ytop) / h
        hw = top_w + (bot_w - top_w) * t
        for xx in range(int(x - hw), int(x + hw) + 1):
            u = (xx - x) / hw
            lvl = 4.0 - u * 1.6 - u * u * 0.8
            if int((yy - ytop) / (5 * s)) in (1, 3) and (yy - ytop) % int(5 * s) == 0:
                lvl -= 1.3                                                    # els cèrcols
            if hr(int(xx), int(yy), 77) > 0.94:
                lvl -= 0.8                                                    # abonyegat, ratllat
            cv.put(xx, yy, ZINC, lvl, lit)
    cv.disc(x, ytop, top_w, 2.6 * s, ZINC, lambda nx, ny: 5.0 if ny < -0.2 else 2.2, lit=lit)
    cv.disc(x, ytop + 0.5, top_w - 1.5, 1.8 * s, (BLUEG if plena else ZINC), 2.0 if plena else 0.8, lit=lit)
    cv.hline(x - bot_w, x + bot_w, y, ZINC, 1.6, lit=lit)
    # la nansa, de filferro, caiguda cap a un costat
    for k in range(17):
        a = math.pi * k / 16
        cv.put(x - math.cos(a) * top_w, ytop - math.sin(a) * 6 * s + 1, ZINC, 2.4, lit)
    cv.put(x - top_w - 1, ytop + 1, ZINC, 1.6, lit)
    cv.put(x + top_w + 1, ytop + 1, ZINC, 1.6, lit)
