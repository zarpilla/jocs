"""
Aigua Verne — `fosa_colada` (L): la mateixa nau de la fosa, l'altra banda: on es cola.

A l'esquerra, el **pas** cap al forn (per on arriba la claror del foc, si n'hi ha). A dalt, travessant la nau, el
**pont grua**: la biga gran amb el carro i el polispast, del qual penja el **gresol** (una galleda de ferro folrada de
refractari, amb el volant i el sinfí per inclinar-la i el broc). La botonera dels comandaments penja d'un cable
(`grua_pont`). A terra, el **llit de colada**: una fossa de sorra amb un marc de ferro, on va el motlle de tres claus.
A la dreta, els sacs i la pila de **sorra** d'aquí, que és pedra picada (`sorra_pedra`), amb una pala.

Decorats (PROPS): `motlle_posat` (la caixa del motlle, buida, al llit), `motlle_preparat` (plena de sorra fina, amb
les tres claus marcades i el bebedor), `gresol_ple` (el metall fos lluu taronja i il·lumina la nau), `claus_fetes`
(les tres claus, encara roents, al motlle). ANIMS: `fum_gresol` (el vapor i les guspires del metall fos: només amb
el gresol ple).
"""
import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

import math

from PIL import Image

from hd.pix import Canvas, Light, W, H, hr, mix, B4
from hd.rooms.comu import _diff, text, text_width
from hd.rooms.exterior import fbm
from hd640.rooms.ferrum_comu import (
    RH, SMOG, HAZE, SLAGF, SOOT, MORTAR, COB, COAL, IRONF, RUSTF, TIN, PLANKF, WHITEV, BLACKT, FIREF, GLOWF,
    CLOTH, REDP, HELM, NAVE_FLOOR,
    brick_wall, nave_wall, light_shafts, trusses, crane_rail, foundry_floor)

# Art a 2× (1280×720 per a una sala de 640×360): el mateix dibuix, amb les formes, el dither i la llum a la
# resolució real (hd1280/canvas2x.py); el motor el mostra a 1/2 (artScale al .room.json).
ART_SCALE = 2
from hd1280.canvas2x import Canvas2x as Canvas  # noqa: E402,F811
from hd.pix import Canvas as Canvas1x  # noqa: E402,F401  (llenços auxiliars en píxels de sala: figures, textos)

GIRDER = (40, 58)                # el pont grua: y de dalt i de baix de la biga
TROLLEY = 372                    # el carro (x del centre)
LADLE = (372, 122, 164)          # el gresol: centre x, dalt, baix
BED = (316, 480, 206, 236)       # el llit de colada: x0, x1 (davant), y de darrere i de davant
MOLD = (354, 442, 211, 230)      # la caixa del motlle (x0, x1, y0, y1)
PENDANT = (226, 150)             # la botonera (centre x, dalt)
YELLOW = [(50, 36, 6), (110, 80, 10), (170, 128, 18), (220, 176, 40), (246, 214, 90), (255, 240, 170)]
SAND = [(70, 56, 40), (104, 86, 62), (136, 116, 86), (166, 146, 112), (194, 176, 140), (220, 204, 170),
        (240, 228, 200)]
SACK = [(40, 32, 22), (66, 54, 36), (94, 80, 56), (124, 108, 78), (152, 136, 102), (178, 164, 128)]
GRAVEL = [(30, 28, 28), (52, 48, 46), (78, 72, 66), (104, 98, 88), (132, 124, 112), (160, 152, 138)]
MOLTEN = [(120, 20, 6), (190, 52, 10), (236, 110, 24), (255, 170, 60), (255, 220, 130), (255, 250, 220)]
KEYC = [(40, 26, 20), (80, 50, 34), (130, 84, 52), (180, 126, 76), (220, 172, 112), (246, 214, 160)]


def _light(ple):
    L = Light(ambient=-0.5, vignette=(80, 40), floor_fade=(250, 30))
    L.point(30, 150, r=150, k=0.9, power=1.6)                 # la claror que ve del forn, pel pas
    for wx in (196, 528):
        L.point(wx + 14, 70, r=130, k=1.0, power=1.6)          # els finestrals
    L.point(452, 130, r=240, k=0.8, power=1.8)                 # un llum de taller penjat sobre el llit
    if ple:
        L.point(LADLE[0], LADLE[1] + 4, r=300, k=2.4, power=1.6)
    return L


LIGHT = _light(False)
LIGHT_PLE = _light(True)


# ─── La nau ────────────────────────────────────────────────────────────────

def nau(cv):
    trusses(cv, 0, 30, seed=7)
    nave_wall(cv, 0, W - 1, top=31, seed=9, windows=((196, 28), (528, 28)), pilasters=(120, 470, 600))
    crane_rail(cv, 86)
    light_shafts(cv, ((196, 28, 70), (528, 28, 70)), k=0.16)
    # un llum de taller (pantalla de llauna) penjat sobre el llit
    lx = 452
    cv.line(lx, 58, lx, 116, IRONF, 1.4)
    cv.poly([(lx - 8, 116), (lx + 8, 116), (lx + 14, 124), (lx - 14, 124)], TIN, lambda x, y: 3.4 - (y - 116) * 0.1)
    cv.rect(lx - 3, 124, lx + 3, 125, GLOWF, 5.2, lit=0)
    cv.glow(lx, 126, 14, (255, 220, 160), 0.4)


def pas(cv):
    """El pas cap al forn: una obertura a l'esquerra; a l'altra banda, el forn que s'endevina."""
    x0, x1, top = 0, 70, 64
    cv.rect(x0, top - 6, x1 + 6, top - 1, MORTAR, lambda x, y: 3.0 - (y - top + 6) * 0.2)
    for y in range(top, NAVE_FLOOR + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, COAL, 0.9 + (y - top) * 0.006 + (fbm(x / 10, y / 10, 35) - 0.5) * 0.6, lit=0)
    cv.rect(x1 + 1, top, x1 + 6, NAVE_FLOOR, MORTAR, lambda x, y: 2.6 - (x - x1) * 0.3)
    # el forn de l'altra banda: la campana i la boca (fosca) en silueta
    cv.poly([(0, 100), (30, 100), (52, 134), (0, 134)], IRONF, 1.2, lit=0)
    cv.rect(0, 134, 50, NAVE_FLOOR, SOOT, lambda x, y: 1.0 + (0.6 if y % 4 == 0 else 0), lit=0)
    cv.disc(22, 170, 11, 12, COAL, 0.2, lit=0)
    cv.rect(11, 170, 33, 192, COAL, 0.2, lit=0)
    cv.rect(0, 192, 50, 196, IRONF, 1.2, lit=0)
    cv.darken(0, 96, 58, NAVE_FLOOR, 0.5, dither=False)                                  # és lluny i fosc


# ─── El pont grua i el gresol ──────────────────────────────────────────────

def pont_grua(cv):
    y0, y1 = GIRDER
    # la biga de gelosia que travessa la nau
    cv.rect(0, y0, W - 1, y0 + 3, YELLOW, lambda x, y: 3.4 - (y - y0) * 0.5)
    cv.rect(0, y1 - 3, W - 1, y1, YELLOW, lambda x, y: 2.8 - (y - y1 + 3) * 0.5)
    for x in range(-10, W + 10, 14):
        cv.line(x, y0 + 4, x + 7, y1 - 4, YELLOW, 2.0)
        cv.line(x + 7, y1 - 4, x + 14, y0 + 4, YELLOW, 1.4)
    cv.tint(0, y0, W - 1, y1, (60, 40, 30), lambda x, y: 0.3 * fbm(x / 8, y / 4, 41) ** 2)   # brutícia
    cv.rect(0, y1 + 1, W - 1, y1 + 1, COAL, 0.6, lit=0)
    # PONT 5 T, pintat a la biga
    cv.rect(120, y0 + 5, 120 + text_width('5 T') + 6, y1 - 5, COAL, 1.0)
    text(cv, '5 T', 123, y0 + 7, YELLOW, 4.4)
    # el carro, amb les rodes i el tambor del cable
    tx = TROLLEY
    cv.rect(tx - 22, y0 - 8, tx + 22, y1 + 6, IRONF, lambda x, y: 3.0 - (x - tx) * 0.02 + (0.8 if y == y0 - 8 else 0))
    for wx in (tx - 16, tx + 16):
        cv.disc(wx, y0 - 2, 4, 4, IRONF, lambda nx, ny: 4.4 - nx - ny)
    cv.disc(tx, y1 + 2, 9, 5, IRONF, lambda nx, ny: 3.6 - ny * 1.4)                       # el tambor
    for k in range(-6, 7, 2):
        cv.put(tx + k, y1 + 2, IRONF, 1.6)
    cv.rect(tx + 12, y0 + 2, tx + 20, y1 + 2, YELLOW, 2.6)                                 # el motor
    # els cables (dos ramals) fins al ganxo
    hy = LADLE[1] - 24
    for dx in (-5, 5):
        cv.line(tx + dx, y1 + 6, tx + dx * 0.4, hy, IRONF, 3.4)
    cv.rect(tx - 6, hy, tx + 6, hy + 8, IRONF, lambda x, y: 3.8 - (x - tx) * 0.1)          # el bossell
    cv.rect(tx - 6, hy + 3, tx + 6, hy + 4, YELLOW, 3.0)
    for k in range(5):                                                                    # el ganxo
        a = math.pi * (0.1 + k / 5)
        cv.put(tx + math.cos(a) * 3, hy + 11 + math.sin(a) * 3, IRONF, 4.0)
    cv.rect(tx - 1, hy + 8, tx + 1, hy + 10, IRONF, 4.0)


def gresol(cv, ple=False):
    """El gresol: galleda cònica de ferro, folrada, penjada per l'ansa, amb el volant del sinfí i el broc."""
    cx, top, bot = LADLE
    hw_top, hw_bot = 26, 19
    # l'ansa, del ganxo als dos muntons
    for k in range(2):
        cv.line(cx - 1, top - 12 + k, cx - hw_top - 3, top + 8, IRONF, 3.6 - k * 1.4)
        cv.line(cx + 1, top - 12 + k, cx + hw_top + 3, top + 8, IRONF, 3.6 - k * 1.4)
    # el cos
    for y in range(top, bot + 1):
        t = (y - top) / (bot - top)
        hw = hw_top + (hw_bot - hw_top) * t
        for x in range(int(cx - hw), int(cx + hw) + 1):
            u = (x - cx) / hw
            v = 3.2 - u * 1.4 - abs(u) ** 5 * 1.4 + (fbm(x / 4, y / 5, 51) - 0.5) * 1.2
            if (y - top) in (4, 5, bot - top - 6, bot - top - 5):
                v += 1.0                                                                  # els cèrcols
            cv.put(x, y, IRONF, v)
    cv.tint(cx - hw_top, top, cx + hw_top, bot, (140, 60, 26), lambda x, y: 0.45 * fbm(x / 5, y / 6, 52) ** 2)
    cv.disc(cx, bot, hw_bot, 3, IRONF, lambda nx, ny: 2.4 - nx)
    # la vora de dalt i el broc (a la dreta, cap al llit)
    cv.disc(cx, top, hw_top, 4, IRONF, lambda nx, ny: 4.4 - nx * 0.8)
    if ple:
        cv.disc(cx, top, hw_top - 3, 2.4, MOLTEN, lambda nx, ny: 4.6 - abs(nx) * 1.2 + (hr(int(nx * 8), 3) - 0.5) * 0.8,
                lit=0)
    else:
        cv.disc(cx, top, hw_top - 3, 2.4, SLAGF, lambda nx, ny: 1.2 + ny * 0.6, lit=0)   # buit: el refractari
    cv.poly([(cx + hw_top - 2, top - 3), (cx + hw_top + 9, top - 6), (cx + hw_top + 9, top - 3),
             (cx + hw_top, top + 4)], IRONF, 4.0)
    if ple:
        cv.line(cx + hw_top + 1, top - 3, cx + hw_top + 7, top - 5, MOLTEN, 5.0, lit=0)
    # el munyó i el volant del sinfí (per inclinar-lo), a l'esquerra
    cv.disc(cx - hw_top - 3, top + 8, 3, 3, IRONF, 4.6)
    wx, wy = cx - hw_top - 10, top + 14
    cv.ring(wx, wy, 7, IRONF, 4.0, step=4)
    cv.ring(wx, wy, 6, IRONF, 2.4, step=6)
    for a in range(0, 360, 60):
        cv.line(wx, wy, wx + math.cos(math.radians(a)) * 6, wy + math.sin(math.radians(a)) * 6, IRONF, 3.0)
    cv.disc(wx, wy, 1.5, 1.5, YELLOW, 3.4)
    if ple:
        cv.glow(cx, top, 40, (255, 150, 60), 0.55)


def botonera(cv):
    """Els comandaments del pont grua: una botonera groga penjada d'un cable."""
    cx, top = PENDANT
    cv.line(cx, GIRDER[1] + 1, cx, top, COAL, 1.0)
    cv.line(cx + 1, GIRDER[1] + 1, cx + 1, top, IRONF, 2.4)
    cv.rect(cx - 6, top, cx + 7, top + 26, YELLOW, lambda x, y: 3.6 - (x - cx) * 0.12 + (0.8 if y == top else 0))
    cv.rect(cx + 7, top + 1, cx + 7, top + 26, YELLOW, 1.4)
    for i, (col, lvl) in enumerate(((BLACKT, 2.0), (BLACKT, 2.0), (BLACKT, 2.0), (BLACKT, 2.0))):
        by = top + 4 + i * 5
        cv.rect(cx - 3, by, cx + 3, by + 2, col, lvl, lit=0)
        # fletxetes: amunt, avall, esquerra, dreta
        pts = (((0, 0), (-1, 1), (1, 1)), ((0, 2), (-1, 1), (1, 1)), ((-2, 1), (-1, 0), (-1, 2)),
               ((2, 1), (1, 0), (1, 2)))[i]
        for px, py in pts:
            cv.flat(cx + px, by + py, (230, 220, 200))
    cv.disc(cx, top + 24, 2.4, 1.6, [(80, 10, 10), (170, 30, 24), (240, 70, 50)], 1.6, lit=0)   # l'aturada


# ─── El llit de colada ─────────────────────────────────────────────────────

def _bed_x(y):
    """Les vores esquerra i dreta del llit (trapezi en perspectiva) a l'alçada y."""
    x0, x1, yb, yf = BED
    t = (y - yb) / (yf - yb)
    return x0 + 10 * (1 - t), x1 - 10 * (1 - t)


def llit(cv):
    x0, x1, yb, yf = BED
    for y in range(yb, yf + 1):
        a, b = _bed_x(y)
        for x in range(int(a), int(b) + 1):
            edge = x - a < 3 or b - x < 3 or y - yb < 2 or yf - y < 2
            if edge:
                cv.put(x, y, IRONF, 3.6 - (0.0 if y - yb < 2 else 1.0) + (0.8 if yf - y < 1 else 0))
            else:
                v = 2.0 + (fbm(x / 5, y / 2, 61) - 0.5) * 1.6 + (hr(x, y, 62) - 0.5) * 0.6       # sorra negra
                cv.put(x, y, COB, v)
    for y in range(yf + 1, yf + 4):                                                       # el cantell de davant
        a, b = _bed_x(yf)
        cv.rect(a, y, b, y, IRONF, 2.2 - (y - yf) * 0.4)
    # restes de colades velles: rajolins de metall, escòria
    for i in range(8):
        x = x0 + 20 + hr(i, 63) * (x1 - x0 - 40)
        y = yb + 5 + hr(i, 64) * (yf - yb - 10)
        cv.disc(x, y, 2 + hr(i, 65) * 3, 1.2, SLAGF, lambda nx, ny: 3.2 - ny)


def sorra(cv):
    """La sorra d'aquí (pedra picada): sacs apilats, una pila de grava i la pala clavada."""
    # la pila de grava
    cx, base = 540, 232
    for y in range(base - 22, base + 1):
        hw = 40 * math.sqrt(max(0.0, (y - base + 22) / 22))
        for x in range(int(cx - hw), int(cx + hw) + 1):
            if hr(x, y, 71) < 0.85 or y > base - 18:
                g = hr(x // 2, y // 2, 72)
                cv.put(x, y, GRAVEL, 2.8 + (g - 0.5) * 2.4 - (x - cx) / max(1, hw) * 0.6 + (y - base) * 0.02)
    # la pala, clavada
    cv.poly([(552, 214), (562, 212), (564, 222), (554, 224)], IRONF, lambda x, y: 4.0 - (x - 552) * 0.1)
    for k in range(2):
        cv.line(557 + k, 213, 578 + k, 168, PLANKF, 4.2 - k * 1.6)
    cv.rect(576, 164, 584, 167, PLANKF, 4.2)
    # els sacs, al costat (de la paret cap enfora)
    for i, (sx, sy, w, h) in enumerate(((488, 198, 34, 16), (520, 200, 32, 15), (500, 184, 32, 15),
                                         (590, 204, 36, 17), (596, 188, 30, 15))):
        for y in range(sy, sy + h + 1):
            for x in range(sx, sx + w + 1):
                nx, ny = (x - sx - w / 2) / (w / 2), (y - sy - h / 2) / (h / 2)
                if nx * nx * 0.7 + ny * ny ** 2 * 1.2 > 1 or abs(nx) > 1 or abs(ny) > 1:
                    continue
                v = 3.4 - nx * 0.8 - ny * 1.0 + (fbm(x / 3, y / 3, 73 + i) - 0.5) * 0.8
                if (x - sx + y) % 4 == 0:
                    v -= 0.4                                                               # la trama de la saca
                cv.put(x, y, SACK, v)
        text(cv, 'SORRA', sx + w // 2 - 9, sy + h // 2 - 2, SACK, 1.0) if i in (0, 3) else None
        cv.put(sx + 2, sy + h // 2, SACK, 1.0)                                              # el lligat


# ─── Composició ────────────────────────────────────────────────────────────

def draw(cv, ple=False):
    nau(cv)
    foundry_floor(cv, NAVE_FLOOR, RH - 1, seed=13, plates=())
    pas(cv)
    # les ombres a terra
    cv.darken(LADLE[0] - 30, 238, LADLE[0] + 40, 244,
              lambda x, y: 0.6 if ((x - LADLE[0] - 4) / 32) ** 2 + ((y - 241) / 3) ** 2 <= 1 else 0)
    cv.darken(470, 228, 640, 236, lambda x, y: 0.7 if y < 232 + (x % 7 == 0) else 0.4)
    llit(cv)
    sorra(cv)
    pont_grua(cv)
    botonera(cv)
    gresol(cv, ple)
    if ple:
        cv.tint(0, 0, W - 1, RH - 1, (255, 130, 50),
                lambda x, y: 0.32 * max(0.0, 1 - math.hypot(x - LADLE[0], (y - LADLE[1]) * 1.1) / 300) ** 1.5)
    for y in range(RH, H):
        for x in range(W):
            cv.flat(x, y, (0, 0, 0))


def bg(cv):
    draw(cv, False)


# ─── Decorats ──────────────────────────────────────────────────────────────

def _mold_box(cv):
    """La caixa del motlle (la de tres claus): un marc de ferro amb nanses, en perspectiva."""
    x0, x1, y0, y1 = MOLD
    sk = 6                                                                                 # el biaix de darrere
    # la cara de dalt: un paral·lelogram (el forat, de moment buit: fosc)
    for y in range(y0, y1 - 4):
        t = (y - y0) / (y1 - 4 - y0)
        a, b = x0 + sk * (1 - t), x1 - sk * (1 - t) * 0.2
        for x in range(int(a), int(b) + 1):
            rim = x - a < 3 or b - x < 3 or y - y0 < 2 or (y1 - 5) - y < 2
            cv.put(x, y, IRONF if rim else COAL, (4.4 - t * 0.6) if rim else 1.0 + t * 0.4)
    # la cara de davant
    cv.rect(x0, y1 - 4, x1, y1, IRONF, lambda x, y: 3.0 - (y - y1 + 4) * 0.3 - (x - x0) * 0.01)
    cv.rect(x0, y1 - 4, x1, y1 - 4, IRONF, 4.6)
    for hx in (x0 - 3, x1 + 1):                                                          # les nanses
        cv.rect(hx, y1 - 3, hx + 2, y1 - 1, IRONF, 4.0)
    # la sombra a la sorra
    for x in range(x0, x1 + 6):
        cv.put(x, y1 + 1, COAL, 0.6, lit=0)
    text(cv, '3', x0 + 3, y1 - 3, IRONF, 1.4) if False else None


def _keys_shape():
    """Les tres claus, en coordenades del motlle: llista de (x, y) dels píxels de cada clau."""
    x0, x1, y0, y1 = MOLD
    keys = []
    for k in range(3):
        kx = x0 + 14 + k * 22
        ky = y0 + 3 + k * 0
        pts = set()
        # l'ull (anella) i la tija, en diagonal per la perspectiva, i les dents
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                if 1.2 <= math.hypot(dx, dy * 1.2) <= 2.6:
                    pts.add((kx + dx, ky + dy))
        for i in range(3, 10):
            pts.add((kx + i // 3, ky + i * 0.7 // 1 + 1))
        bx, by = kx + 3, ky + 7
        pts |= {(bx + 1, by), (bx + 2, by), (bx + 1, by - 1 + 2), (bx + 2, by + 2)}
        keys.append(sorted(pts))
    return keys


def motlle_posat(cv):
    _mold_box(cv)


def motlle_preparat(cv):
    """La caixa del motlle plena de sorra fina (la de la platja d'Aqua), amb les tres claus marcades i el bebedor."""
    _mold_box(cv)
    x0, x1, y0, y1 = MOLD
    sk = 6
    for y in range(y0 + 2, y1 - 6):
        t = (y - y0) / (y1 - 4 - y0)
        a, b = x0 + sk * (1 - t) + 3, x1 - sk * (1 - t) * 0.2 - 3
        for x in range(int(a), int(b) + 1):
            cv.put(x, y, SAND, 4.2 - t * 0.6 + (hr(x, y, 81) - 0.5) * 0.8)
    for pts in _keys_shape():
        for x, y in pts:
            cv.put(x, y, SAND, 1.4)
    # el bebedor (on s'aboca) i els canals
    bx, by = x1 - 10, y0 + 5
    cv.disc(bx, by, 2.5, 1.6, SAND, 0.6)
    cv.line(bx - 3, by, x0 + 60, y0 + 4, SAND, 2.0)


def gresol_ple(cv):
    """El gresol ple de metall fos: lluu taronja i il·lumina la nau."""
    base = Canvas(light=LIGHT)
    draw(base, False)
    lit = Canvas(light=LIGHT_PLE)
    draw(lit, True)
    d = _diff(lit.img, base.img)
    # el llit (on hi pot haver el motlle i les claus, que són altres decorats) queda com és (caixes en píxels reals)
    k = base.S
    d.paste((0, 0, 0, 0), tuple(v * k for v in (BED[0] - 2, BED[2] - 2, BED[1] + 3, BED[3] + 5)))
    d.paste((0, 0, 0, 0), tuple(v * k for v in (0, RH, W, H)))
    cv.img.alpha_composite(d)


def claus_fetes(cv):
    """Les tres claus, acabades de colar: encara roents al motlle."""
    x0, x1, y0, y1 = MOLD
    for pts in _keys_shape():
        for x, y in pts:
            cv.put(x, y, MOLTEN, 3.6 + (0.8 if (x + y) % 3 == 0 else 0), lit=0)
        x, y = pts[0]
        cv.glow(x + 2, y + 3, 8, (255, 160, 70), 0.35)


PROPS = {'motlle_posat': motlle_posat, 'motlle_preparat': motlle_preparat, 'gresol_ple': gresol_ple,
         'claus_fetes': claus_fetes}


# ─── Animacions ─────────────────────────────────────────────────────────────

def _frames_fum_gresol():
    """El metall fos del gresol: la superfície que bull (taques que es mouen), el vapor i alguna guspira."""
    cx, top = LADLE[0], LADLE[1]
    frames = []
    n = 12
    for f in range(n):
        img = Image.new('RGBA', (W * Canvas.S, H * Canvas.S), (0, 0, 0, 0))
        cv = Canvas(light=LIGHT_PLE, img=img)
        ph = f / n
        for y in range(top - 2, top + 3):
            for x in range(cx - 22, cx + 23):
                nx, ny = (x - cx) / 23, (y - top) / 2.4
                if nx * nx + ny * ny <= 1:
                    na = fbm(x / 4 + ph * 3, y / 2, 91)
                    nb = fbm(x / 4 + (ph - 1) * 3, y / 2, 91)
                    v = na * (1 - ph) + nb * ph
                    cv.put(x, y, MOLTEN, 3.4 + (v - 0.5) * 4.0 - abs(nx) * 1.0, lit=0)
        for k in range(4):                                                                # guspires
            s = (ph + k / 4) % 1
            x = cx - 14 + k * 9 + math.sin(s * 9 + k) * 4
            y = top - 4 - s * 30
            if s < 0.7:
                cv.flat(x, y, MOLTEN[5] if s < 0.3 else MOLTEN[3])
        # el vapor, a quadres, que puja
        for y in range(top - 40, top - 3):
            t = (top - 3 - y) / 37
            for x in range(cx - 20, cx + 21):
                u = (x - cx - math.sin(t * 3 + ph * 6.28) * 4) / (14 + t * 10)
                if abs(u) > 1:
                    continue
                d = (1 - t) * (1 - u * u) * (0.3 + fbm(x / 6, (y + ph * 37) / 6, 92))
                if d > 0.55 + B4[y & 3][x & 3] * 0.6:
                    cv.flat(x, y, (150, 110, 90))
        frames.append(img)
    return frames


ANIMS = {'fum_gresol': {'frames': _frames_fum_gresol, 'frameDuration': 110}}


# ─── Geometria (640×360) ───────────────────────────────────────────────────

GEOMETRIA = {
    'things': {
        'pas': {'rect': (0, 58, 78, 206), 'walk': (40, 222)},
        'gresol': {'rect': (330, 96, 406, 168), 'walk': (360, 248)},
        'grua_pont': {'rect': (214, 40, 240, 180), 'walk': (228, 228)},
        'llit': {'rect': (314, 204, 482, 240), 'walk': (300, 248)},
        'sorra_pedra': {'rect': (484, 162, 640, 236), 'walk': (500, 246)},
    },
    'spawns': {'iri': (250, 240), 'vet': (150, 236)},
    'walkable': [(0, 214), (310, 212), (300, 244), (492, 244), (488, 236), (640, 238), (640, 257), (0, 257)],
}
