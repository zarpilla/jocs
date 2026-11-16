#!/usr/bin/env python3
"""
Aigua Verne — prova d'art d'una sala «de lluny»: el pati de la granja (Escena 1), a Terra-2, un matí de secada.

La càmera és lluny: l'Iri i la Vet fan ≈83 px (personatges.py), no els ≈110 px de Ni un ou a 640×360. Es
dibuixa a la resolució del joc (640×360: la sala, 640×260, i la barra de verbs a sota), amb les eines de pixel
art de Ni un ou (hd/pix.py: rampes, llum, dithering).

Què hi ha: el cel de pols, sense ni un núvol; els camps secs i la carretera; la **Canonada de Terra-2** a
l'horitzó, una columna fins al cel; el panell del preu a la carretera (48 ▲); la masia (la casa del pare) amb
els finestrons tancats; l'arbre mort; el **pou** amb la politja i la galleda; la **bomba de Verne**, blanca i
neta, amb el tub ficat al pou i un altre que se'n va sota terra cap a la Canonada; el **graner** obert, amb el
morro del tractor vermell de l'avi; el terra del pati, clivellat. En Diu, assegut a la vora del pou.

Ús: python3 granja_pati.py
Surt, al costat d'aquest fitxer:
  granja-pati.png         la sala sola (640×260)
  granja-pati-joc.png     la pantalla de joc (640×360) ×2, amb la barra de verbs de Ni un ou com a provisional
  comparativa.png         la mateixa sala amb les dues a 83 px (de lluny) i a 110 px (la mida de prop de Ni un ou)
"""
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
GAMES = HERE.parents[3]
TOOLS = GAMES / 'ni-un-ou/adapters/benne/tools'
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(HERE))
from pixels import nearest  # noqa: E402

import hd640  # noqa: E402,F401  (posa la llibreria a 640×360)
from hd.pix import Canvas, Light, hr, mix, WALNUT, RUST, RED  # noqa: E402
from hd.rooms.exterior import fbm, smooth  # noqa: E402
from hd.personatges import diu  # noqa: E402
import personatges as P  # noqa: E402

W, RH = 640, 260                 # la sala (la barra va de 260 a 360)
HOR = 118

# ─── Rampes (fosc → clar) ───────────────────────────────────────────────────
SKY = [(150, 128, 98), (174, 152, 118), (194, 174, 138), (212, 194, 156), (226, 210, 172), (238, 224, 188),
       (246, 236, 204), (252, 246, 222)]
HILL = [(122, 98, 78), (140, 116, 92), (158, 134, 108), (174, 150, 122), (190, 168, 138), (204, 184, 154)]
FIELD = [(70, 48, 30), (96, 68, 42), (122, 90, 56), (148, 112, 72), (170, 134, 90), (192, 156, 110),
         (210, 178, 132), (226, 198, 154)]
EARTH = [(52, 34, 24), (78, 54, 36), (104, 74, 48), (130, 96, 62), (156, 118, 78), (180, 142, 96),
         (202, 166, 118), (220, 190, 142), (234, 210, 166)]
ADOBE = [(58, 40, 30), (90, 64, 44), (124, 92, 62), (156, 120, 82), (184, 148, 106), (206, 174, 132),
         (224, 198, 158), (238, 218, 182)]
STONE = [(40, 36, 34), (62, 56, 50), (88, 80, 70), (114, 104, 90), (140, 128, 110), (164, 152, 132),
         (188, 178, 156), (210, 202, 182)]
TILE = [(46, 18, 14), (74, 30, 20), (104, 44, 28), (134, 62, 38), (162, 82, 50), (188, 106, 66), (210, 134, 88)]
SHUT = [(20, 34, 26), (30, 52, 38), (44, 72, 52), (62, 94, 68), (84, 116, 86), (110, 138, 106)]
PLANK = [(36, 24, 18), (56, 38, 26), (78, 54, 36), (102, 72, 46), (126, 92, 58), (150, 114, 74), (172, 138, 94)]
WHITEP = [(84, 92, 104), (126, 134, 146), (166, 172, 182), (200, 204, 212), (226, 228, 234), (244, 245, 248),
          (254, 254, 255)]
COL = [(150, 150, 150), (176, 176, 174), (198, 196, 192), (216, 214, 208), (232, 230, 224), (244, 242, 236)]
BLUE = [(10, 30, 70), (20, 60, 130), (40, 100, 190), (90, 160, 230), (170, 210, 250)]
BLACKT = [(10, 10, 12), (22, 22, 24), (36, 36, 38), (54, 54, 56), (76, 76, 78)]
LED = [(30, 6, 4), (90, 20, 10), (180, 50, 20), (250, 120, 40), (255, 200, 120)]
GRASS = [(70, 58, 30), (100, 86, 44), (132, 116, 62), (164, 146, 84), (194, 176, 110)]

LIGHT = Light(ambient=0.6, vignette=(70, 18), floor_fade=None)
LIGHT.point(560, -40, r=700, k=1.2, power=1.1)            # el sol, a dalt a la dreta


# ─── Lletres de 3×5 per als rètols petits ──────────────────────────────────
GLYPH = {
    '0': '111101101101111', '1': '010110010010111', '2': '111001111100111', '3': '111001111001111',
    '4': '101101111001001', '5': '111100111001111', '6': '111100111101111', '7': '111001010010010',
    '8': '111101111101111', '9': '111101111001111', 'A': '010101111101101', 'E': '111100110100111',
    'G': '011100101101011', 'I': '111010010010111', 'N': '101111111111101', 'R': '110101110101101',
    'U': '101101101101111', 'V': '101101101101010', ' ': '000000000000000',
}


def tiny(cv, s, x, y, col):
    for ch in s:
        g = GLYPH[ch]
        for j in range(5):
            for i in range(3):
                if g[j * 3 + i] == '1':
                    cv.flat(x + i, y + j, col)
        x += 4
    return x


# ─── Cel, turons, Canonada ─────────────────────────────────────────────────

def sky(cv):
    for y in range(0, HOR + 1):
        t = y / HOR
        for x in range(W):
            d = math.hypot(x - 540, (y - 26) * 1.3)
            lvl = 2.0 + 3.6 * t ** 0.8 + 2.4 * max(0.0, 1 - d / 160) ** 2
            lvl += (fbm(x / 140, y / 18, 31) - 0.5) * 0.7                            # pols en suspensió
            cv.put(x, y, SKY, lvl, lit=0)
    cv.glow(540, 26, 30, (255, 250, 228), 0.9)
    cv.disc(540, 26, 7, 7, SKY, 7.6, lit=0)


def hills(cv):
    for x in range(W):
        h1 = HOR - 6 - 12 * fbm(x / 90, 0.3, 7)
        h2 = HOR - 2 - 7 * fbm(x / 50, 1.7, 9)
        for y in range(int(h1), HOR + 1):
            cv.put(x, y, HILL, 4.4 - (y - h1) * 0.03, lit=0)
        for y in range(int(h2), HOR + 1):
            cv.put(x, y, HILL, 3.4 + (fbm(x / 8, y / 4, 3) - 0.5), lit=0)


def canonada(cv, x=402):
    """La columna de Verne: de l'horitzó fins més amunt del cel. Blanca, amb anelles, i un llum vermell."""
    for y in range(0, HOR):
        w = 2.2 + 2.2 * (y / HOR)
        for xx in range(int(x - w), int(x + w) + 1):
            u = (xx - x) / max(1.0, w)
            lvl = 3.2 - u * 1.4 + (0.9 if y % 13 == 0 else 0) - (0.6 if y % 13 == 1 else 0)
            cv.put(xx, y, COL, lvl, lit=0)
    cv.tint(x - 6, 0, x + 6, HOR, (230, 214, 180), lambda xx, yy: 0.35 - 0.2 * yy / HOR)   # la boira de pols
    cv.rect(x - 11, HOR - 7, x + 11, HOR, COL, 2.4, lit=0)                          # l'estació
    cv.rect(x - 11, HOR - 8, x + 11, HOR - 8, COL, 4.4, lit=0)
    cv.flat(x - 1, 22, (230, 40, 30))
    cv.glow(x, 22, 4, (255, 90, 60), 0.5)


def fields(cv):
    """Camps secs, amb solcs que fugen cap a l'horitzó; la carretera a la dreta."""
    vx, vy = 300, HOR - 60
    for y in range(HOR + 1, 200):
        t = (y - HOR) / 82
        for x in range(W):
            ang = math.atan2(y - vy, x - vx)
            furrow = math.sin(ang * 90) * 0.5
            lvl = 4.2 - t * 1.0 + furrow * t + (fbm(x / 30, y / 6, 11) - 0.5) * 1.0
            cv.put(x, y, FIELD, lvl)
    # carretera: de la dreta de baix fins a l'horitzó
    for y in range(HOR + 1, 200):
        t = (y - HOR) / 82
        cx = 430 + 90 * t
        hw = 1 + 22 * t
        for x in range(int(cx - hw), int(cx + hw) + 1):
            cv.put(x, y, EARTH, 6.0 - t * 0.4 + (hr(x // 3, y // 2) - 0.5) * 0.8)
    # el panell del preu, a la vora de la carretera
    px0, py0 = 422, 126
    cv.rect(px0 + 20, py0 + 18, px0 + 21, py0 + 40, STONE, 2.0)
    cv.rect(px0, py0, px0 + 41, py0 + 18, BLACKT, 1.4, lit=0)
    cv.rect(px0, py0, px0 + 41, py0, BLACKT, 3.4, lit=0)
    cv.disc(px0 + 5, py0 + 7, 2, 3, BLUE, 3.0, lit=0)                               # la gota de Verne
    cv.flat(px0 + 5, py0 + 3, BLUE[3])
    tiny(cv, 'VERNE', px0 + 10, py0 + 3, (210, 220, 236))
    x = tiny(cv, '48', px0 + 14, py0 + 10, LED[3])
    for j, w in enumerate((0, 1, 2)):                                               # ▲
        for i in range(-w, w + 1):
            cv.flat(x + 3 + i, py0 + 11 + j, LED[3])


# ─── La masia ──────────────────────────────────────────────────────────────

def masia(cv):
    base = 184
    apex = (104, 34)
    left, right = (-6, 80), (214, 80)

    def wall_lvl(x, y):
        return 3.6 + (fbm(x / 14, y / 10, 21) - 0.5) * 1.4 - (0.6 if hr(x // 5, y // 3) > 0.93 else 0)

    cv.poly([(0, 82), apex, (208, 82), (208, base), (0, base)], ADOBE, wall_lvl)
    # teulada: la vora de teules a dues aigües
    for k in range(10):
        f = k / 9
        lvl = 3.4 - f * 1.4
        cv.line(left[0], left[1] + k * 0.4 - 6 + k, apex[0], apex[1] - 6 + k, TILE, lvl)
        cv.line(apex[0], apex[1] - 6 + k, right[0], right[1] - 6 + k + k * 0.4, TILE, lvl - 0.6)
    for i in range(0, 108, 6):                                                      # els canals de les teules
        t = i / 107
        cv.put(left[0] + (apex[0] - left[0]) * t, left[1] - 5 + (apex[1] - left[1]) * t + 1, TILE, 4.8)
        cv.put(apex[0] + (right[0] - apex[0]) * t, apex[1] - 5 + (right[1] - apex[1]) * t + 1, TILE, 4.0)
    cv.darken(0, 82, 208, 92, lambda x, y: 0.55 if y < 82 + 6 * (1 - abs(x - 104) / 104) + 4 else 0)
    # sòcol de pedra
    cv.rect(0, base - 12, 208, base, STONE, lambda x, y: 3.2 + (0.8 if (x // 9 + y // 4) % 2 else 0) -
            (1.4 if x % 9 == 0 or y % 4 == 0 else 0))
    # la porta d'arc de mig punt
    dx0, dx1, dtop = 82, 124, 128
    for y in range(dtop - 21, base):
        for x in range(dx0 - 4, dx1 + 5):
            cx = (dx0 + dx1) / 2
            r_in, r_out = (dx1 - dx0) / 2, (dx1 - dx0) / 2 + 4
            d = math.hypot(x - cx, (y - dtop) * 1.0) if y < dtop else abs(x - cx)
            if d <= r_in:
                plank = (x - dx0) % 7 == 0
                cv.put(x, y, PLANK, 3.0 - (1.4 if plank else 0) - (0.6 if x > cx else 0))
            elif d <= r_out and (y < dtop or x < dx0 or x > dx1):
                cv.put(x, y, STONE, 4.2 - (1.2 if hr(int(math.atan2(y - dtop, x - cx) * 8), 1) > 0.7 else 0))
    cv.disc(116, 160, 1.6, 1.6, RUST, 4.0)                                          # la baula
    # finestres amb els finestrons tancats
    for x0, y0, w, h in ((34, 92, 22, 28), (152, 92, 22, 28), (150, 138, 20, 22)):
        cv.rect(x0 - 2, y0 - 2, x0 + w + 1, y0 + h + 1, STONE, 4.4)
        cv.rect(x0, y0, x0 + w - 1, y0 + h - 1, SHUT, lambda x, y: 3.0 - (1.6 if (y - y0) % 4 == 3 else 0) -
                (1.2 if x == x0 + w // 2 else 0))
        cv.rect(x0 - 3, y0 + h + 2, x0 + w + 2, y0 + h + 3, STONE, 3.4)
    # l'ull de bou de les golfes
    cv.disc(104, 62, 7, 7, STONE, 4.4)
    cv.disc(104, 62, 5, 5, BLACKT, lambda nx, ny: 0.8 + ny * 0.6)
    # el banc de pedra i el pedrís
    cv.rect(140, 174, 178, 178, STONE, 4.4)
    cv.rect(142, 179, 145, 184, STONE, 2.6)
    cv.rect(173, 179, 176, 184, STONE, 2.6)


def arbre(cv, x0=232, base=188):
    """Una olivera morta: soca torta i branques nues."""
    def branch(x, y, a, l, w, depth):
        if depth == 0 or l < 3:
            return
        x1, y1 = x + math.cos(a) * l, y - math.sin(a) * l
        for k in range(int(w) + 1):
            cv.line(x + k * 0.5, y, x1 + k * 0.3, y1, PLANK, 2.4 - k * 0.6 + depth * 0.2)
        branch(x1, y1, a + 0.5 + (hr(depth, int(x)) - 0.5) * 0.4, l * 0.7, max(0, w - 1), depth - 1)
        branch(x1, y1, a - 0.45 + (hr(int(y), depth) - 0.5) * 0.4, l * 0.65, max(0, w - 1), depth - 1)
    for y in range(base - 46, base + 1):                                            # la soca
        wob = math.sin(y * 0.15) * 3
        for x in range(int(x0 - 5 + wob), int(x0 + 5 + wob)):
            cv.put(x, y, PLANK, 3.2 - abs(x - x0 - wob) * 0.25 - (1.0 if (x + y // 3) % 5 == 0 else 0))
    branch(x0 + math.sin((base - 46) * 0.15) * 3, base - 46, 1.25, 26, 3, 5)
    branch(x0 + 2, base - 40, 0.35, 22, 2, 4)
    branch(x0 - 2, base - 30, 2.6, 18, 2, 4)


# ─── El graner i el tractor ────────────────────────────────────────────────

def graner(cv):
    x0, x1, top, base = 472, 640, 92, 190
    cv.poly([(x0 - 4, top + 2), (x0 + 60, top - 26), (x1 + 4, top - 8), (x1 + 4, top + 4)], RUST,
            lambda x, y: 3.2 + (0.8 if x % 5 < 2 else -0.4) + (fbm(x / 9, y / 9, 5) - 0.5) * 1.6)   # xapa rovellada
    cv.rect(x0, top + 2, x1, base, PLANK, lambda x, y: 3.6 - (1.6 if (x - x0) % 8 == 0 else 0) +
            (fbm(x / 6, y / 18, 41) - 0.5) * 1.2)
    # la porta gran, oberta: dins, fosc, i el morro del tractor vermell
    dx0, dx1, dtop = 516, 600, 118
    cv.rect(dx0, dtop, dx1, base, BLACKT, lambda x, y: 0.4 + max(0.0, 1 - (y - dtop) / 40) * 0.6, lit=0)
    cv.rect(dx0 + 22, 152, dx0 + 66, 176, RED, lambda x, y: 4.2 - (x - dx0 - 22) * 0.04 - (1.6 if y == 152 else 0)
            - (1.0 if (x - dx0) % 4 == 0 and 158 < y < 172 else 0))                      # el capó i la graella
    cv.rect(dx0 + 30, 158, dx0 + 50, 170, BLACKT, lambda x, y: 1.6 + (1.4 if (x - dx0) % 3 == 0 else 0))
    cv.disc(dx0 + 36, 162, 3, 3, mix_ramp(), 3.2)                                   # el far
    for wx in (dx0 + 16, dx0 + 72):                                                 # les rodes
        cv.disc(wx, 176, 11, 13, BLACKT, lambda nx, ny: 2.4 - ny * 0.8 + (0.8 if int((nx + ny) * 6) % 2 else 0))
        cv.disc(wx, 176, 4, 5, RED, 3.0)
    cv.rect(dx0 + 40, 138, dx0 + 43, 152, BLACKT, 2.0)                              # el tub d'escapament
    cv.tint(dx0, dtop, dx1, base, (20, 14, 12), 0.35)
    # la fulla de la porta, oberta cap enfora
    cv.poly([(dx0 - 2, dtop), (dx0 - 34, dtop + 8), (dx0 - 34, base + 6), (dx0 - 2, base)], PLANK,
            lambda x, y: 2.8 - (1.6 if (x - dx0) % 7 == 0 else 0))
    cv.line(dx0 - 30, dtop + 14, dx0 - 4, base - 6, PLANK, 1.2)
    cv.line(dx0 - 30, base - 4, dx0 - 4, dtop + 10, PLANK, 1.2)
    # el reg gota a gota del pare, enrotllat a la paret (Escena 1: «Això no es toca, que encara serveix»)
    for r in (6, 5, 4):
        cv.ring(492, 150, r, BLACKT, 2.2 + (6 - r) * 0.3, step=6)
    cv.rect(491, 136, 493, 144, STONE, 2.0)


def mix_ramp():
    return [(70, 60, 30), (150, 140, 80), (230, 220, 150), (255, 250, 210)]


# ─── Pou, bomba i tanca ────────────────────────────────────────────────────

def tanca(cv):
    for x in range(250, 470, 26):
        cv.rect(x, 160, x + 2, 186, PLANK, 3.0)
        cv.put(x + 1, 159, PLANK, 3.8)
    for y in (166, 176):
        for x in range(250, 470):
            if not (x % 26 in (0, 1, 2)) and hr(x // 26, y) > 0.15:
                cv.put(x, y, PLANK, 3.4 - (0.8 if (x // 3) % 7 == 0 else 0))
                cv.put(x, y + 1, PLANK, 2.2)


WX, WTOP, WBASE, WRX = 300, 174, 204, 26


def pou(cv):
    """El pou de pedra, amb la politja i la galleda (seca)."""
    for y in range(WTOP, WBASE + 1):
        for x in range(WX - WRX, WX + WRX + 1):
            u = (x - WX) / WRX
            if abs(u) <= 1:
                yy = y + 7 * math.sqrt(max(0.0, 1 - u * u))
                if yy > WTOP + 6 or y > WTOP + 3:
                    row, col = int((y - WTOP) / 6), int((math.asin(max(-1, min(1, u))) + (0.5 if int((y - WTOP) / 6) % 2 else 0)) * 5)
                    joint = (y - WTOP) % 6 == 0 or hr(row, col, 3) < 0.0 or abs((math.asin(max(-1, min(1, u))) * 5 + (0.5 if row % 2 else 0)) % 1) < 0.12
                    cv.put(x, y + 4, STONE, 4.2 - u * 1.4 - (1.6 if joint else 0) + (hr(row, col) - 0.5) * 0.8)
    cv.disc(WX, WTOP + 4, WRX, 7, STONE, lambda nx, ny: 5.0 - nx * 0.6)             # la vora de dalt
    cv.disc(WX, WTOP + 4, WRX - 4, 4.4, BLACKT, lambda nx, ny: 0.4 + ny * 0.8)      # el forat, negre i sec
    for px_ in (WX - 22, WX + 22):                                                  # els pals i la biga
        cv.rect(px_ - 2, 130, px_ + 1, WTOP + 4, PLANK, lambda x, y: 3.6 - (x - px_ + 2) * 0.6)
    cv.rect(WX - 26, 127, WX + 26, 131, PLANK, lambda x, y: 4.0 - (y - 127) * 0.6)
    cv.disc(WX, 136, 5, 5, STONE, lambda nx, ny: 3.6 - nx - ny)                     # la politja
    cv.disc(WX, 136, 1.4, 1.4, BLACKT, 1.0)
    cv.line(WX + 5, 136, WX + 5, 150, PLANK, 1.6)                                   # la corda i la galleda
    cv.poly([(WX - 1, 150), (WX + 11, 150), (WX + 10, 162), (WX, 162)], STONE,
            lambda x, y: 3.4 - (x - WX) * 0.12 - (1.4 if y in (153, 159) else 0))


def bomba(cv):
    """La bomba de Verne: una caixa blanca i neta, amb la gota blava, el tub al pou i un altre sota terra."""
    x0, x1, y0, y1 = 334, 362, 172, 206
    cv.rect(x0, y0, x1, y1, WHITEP, lambda x, y: 4.6 - (x - x0) * 0.05 + (0.8 if y == y0 else 0) -
            (1.4 if x == x1 else 0))
    cv.rect(x0, y1 - 2, x1, y1, WHITEP, 2.4)
    cv.disc(348, 184, 3, 4, BLUE, lambda nx, ny: 2.6 - nx - ny * 0.6, lit=0)        # el logotip
    cv.put(348, 179, BLUE, 2.6, lit=0)
    cv.rect(338, 194, 358, 196, BLUE, 1.6, lit=0)                                   # la franja «VERNE»
    for x in range(339, 358, 3):
        cv.flat(x, 195, (210, 225, 245))
    cv.rect(352, 199, 356, 202, [(80, 70, 10), (200, 170, 30), (250, 220, 70)], 1.6, lit=0)   # perill
    cv.rect(x0 - 2, y0 + 6, x0, y0 + 14, WHITEP, 2.0)                               # cargols de cap de flor
    # el tub que va al pou, en arc
    for i in range(40):
        t = i / 39
        x = x0 - 2 - (x0 - (WX + 12)) * t
        y = y0 + 4 - math.sin(t * math.pi) * 14
        for k in range(3):
            cv.put(x, y + k, WHITEP, 4.6 - k * 1.0)
    cv.rect(WX + 11, WTOP - 2, WX + 13, WTOP + 7, WHITEP, 3.4)
    # el tub que se'n va sota terra, cap a la Canonada (una rasa recta, tapada de pressa)
    for i in range(110):
        t = i / 109
        x = x1 + 2 + 140 * t
        y = y1 - 2 - 18 * t
        cv.put(x, y, EARTH, 2.0)
        cv.put(x, y + 1, EARTH, 6.6)
        if i % 9 == 0:
            cv.put(x, y - 1, WHITEP, 3.2)


# ─── El terra del pati ─────────────────────────────────────────────────────

def _cracks(x, y, cell=13):
    """Distància a la vora d'una cel·la de Voronoi: el fang sec, clivellat."""
    gx, gy = x // cell, y // cell
    d = []
    for j in (-1, 0, 1):
        for i in (-1, 0, 1):
            cx = (gx + i + hr(gx + i, gy + j, 1)) * cell
            cy = (gy + j + hr(gx + i, gy + j, 2)) * cell
            d.append(math.hypot(x - cx, (y - cy) * 1.8))
    d.sort()
    return d[1] - d[0]


def terra(cv):
    for y in range(184, RH):
        t = (y - 184) / (RH - 184)
        for x in range(W):
            if y < 200 and cv.get(x, y)[3] and y < 190 and not (250 <= x <= 470):
                pass
            c = _cracks(x, int((y - 184) / (0.5 + t)) + 184, cell=11 + int(t * 8))
            lvl = 4.4 + t * 0.6 + (fbm(x / 40, y / 10, 17) - 0.5) * 1.4
            if c < 1.0 + t * 0.6:
                lvl -= 2.4
            elif c < 2.0 + t:
                lvl += 0.6
            cv.put(x, y, EARTH, lvl)
    for x, y in ((40, 236), (120, 250), (470, 244), (600, 232), (210, 214)):          # pedres
        cv.disc(x, y, 3, 2, STONE, lambda nx, ny: 4.0 - nx - ny)
    for x0, y0 in ((6, 186), (196, 188), (476, 192), (246, 190), (624, 196)):       # herba seca
        for k in range(7):
            a = 1.2 + (k - 3) * 0.18
            cv.line(x0 + k, y0, x0 + k + math.cos(a) * 7, y0 - math.sin(a) * 7, GRASS, 2.0 + hr(k, x0) * 2)


def ombres(cv, peus):
    """Ombres llargues cap a l'esquerra (el sol és a dalt a la dreta)."""
    def shadow(cx, cy, rx, ry, k=0.85):
        cv.darken(cx - rx - 2, cy - ry - 2, cx + rx + 2, cy + ry + 2,
                  lambda x, y: k if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1 else 0)
    shadow(WX - 18, WBASE + 6, 32, 6)
    shadow(340, 208, 18, 4)
    shadow(222, 190, 16, 3)
    for x, y in peus:
        shadow(x - 9, y + 1, 13, 2.6)


# ─── Composició ────────────────────────────────────────────────────────────

IRI_PEUS, VET_PEUS = (442, 236), (384, 242)


def fons():
    cv = Canvas(W, RH, light=LIGHT)
    sky(cv)
    hills(cv)
    canonada(cv)
    fields(cv)
    terra(cv)
    tanca(cv)
    masia(cv)
    arbre(cv)
    graner(cv)
    ombres(cv, (IRI_PEUS, VET_PEUS))
    pou(cv)
    bomba(cv)
    img = cv.img
    gat = diu()
    img.alpha_composite(gat, (WX - 30, WTOP - 18))                                  # en Diu, a la vora del pou
    return img


def amb_personatges(img, iri, vet, feet=(25, 83)):
    out = img.copy()
    for spr, (x, y) in sorted(((vet, VET_PEUS), (iri, IRI_PEUS)), key=lambda s: s[1][1]):
        out.alpha_composite(spr, (x - feet[0], y - feet[1]))
    return out


def main():
    bg = fons()
    bg.save(HERE / 'granja-pati.png')

    petita = amb_personatges(bg, P.figura(P.IRI, 'D', talk=True), P.figura(P.VET, 'L'))

    # la mida de prop (×4/3, com Ni un ou a 640): el mateix disseny redibuixat amb les eines de hd640
    sys.path.insert(0, str(TOOLS / 'hd640'))
    import hd640.draw_characters as DC
    DC.install()
    gran_iri, gran_vet = P.figura(P.IRI, 'D', talk=True), P.figura(P.VET, 'L')
    gran = amb_personatges(bg, gran_iri, gran_vet, feet=(34, 111))

    # la pantalla de joc, amb la barra de Ni un ou (provisional) i la cara de la Vet nova a l'ull de bou
    import hd640.gui as gui
    bar = gui.verb_bar({'line': 'Mira la bomba de Verne', 'inv': (), 'face': 'vet'})
    cara = gran_vet if False else P.figura(P.VET, 'D')
    n = 2 * gui.FACE_R + 1
    disc = Image.new('RGBA', (n, n + 1), (0, 0, 0, 0))
    S, D = cara.load(), disc.load()
    x0, y0 = round(gui.FACE_C[0] - gui.FACE_R), round(gui.FACE_C[1] - gui.FACE_R) - 4
    for y in range(n + 1):
        for x in range(n):
            if (x - gui.FACE_R) ** 2 + (y - gui.FACE_R) ** 2 <= gui.FACE_R ** 2 and 0 <= y0 + y < cara.height:
                r, g, b, a = S[x0 + x, y0 + y]
                if a:
                    D[x, y] = (int(r * 0.92), int(g * 0.95), int(b), a)
    port = gui.PORT
    ImageDraw.Draw(bar).ellipse((port[0] - 13, port[1] - 14, port[0] + 13, port[1] + 12), fill=(30, 52, 70, 255))
    bar.alpha_composite(disc, (port[0] - disc.width // 2, port[1] - disc.height // 2 - 1))
    screen = Image.new('RGBA', (W, 360), (0, 0, 0, 255))
    screen.alpha_composite(petita, (0, 0))
    screen.alpha_composite(bar, (0, 260))
    nearest(screen, (W * 2, 720)).save(HERE / 'granja-pati-joc.png')

    # comparativa: de lluny (83 px) a dalt, de prop (110 px) a baix
    comp = Image.new('RGBA', (W, RH * 2 + 40), (24, 22, 26, 255))
    d = ImageDraw.Draw(comp)
    d.text((8, 4), 'De lluny: personatges de ~83 px (aquesta prova)', fill=(240, 230, 200))
    comp.alpha_composite(petita, (0, 20))
    d.text((8, RH + 24), 'De prop: ~110 px (la mida de Ni un ou a 640x360), a la mateixa sala', fill=(240, 230, 200))
    comp.alpha_composite(gran, (0, RH + 40))
    nearest(comp, (W * 2, comp.height * 2)).save(HERE / 'comparativa.png')
    print('granja-pati.png, granja-pati-joc.png, comparativa.png')


if __name__ == '__main__':
    main()
