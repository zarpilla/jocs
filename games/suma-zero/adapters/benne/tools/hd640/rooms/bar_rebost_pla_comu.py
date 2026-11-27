"""
**El dibuix pla de sempre** (font de les textures de bar_rebost.py, que és en 3D).

El rebost i despatx d'en Tomàs (hd/rooms/bar_rebost.py) a 640×360: la mateixa composició ×4/3, dibuixada de nou.
Darrere el bar La Propina:
  - un magatzem petit i brut: paret de maó emblanquinat amb humitats, terra de ciment amb una reixa;
  - la llum: una bombeta nua que penja del sostre (càlida, amb una arna que hi dona voltes) i la ratlla
    de llum del bar per sota la porta;
  - l'escriptori d'en Tomàs, vell i ple de factures, amb el calaix tancat per un **pany intel·ligent** de plàstic
    blanc que no hi lliga gens (Trencaclosques 2.2: llum vermell tancat, verd obert);
  - caixes de cervesa apilades sota un cartell de «PROHIBIT FUMAR» ple de cremades; una prestatgeria amb
    llaunes i una caixa de llimones (la llimonada!), un barril i la fregona.
Animacions: `arna` (l'arna dona voltes a la bombeta), `gota` (la canonada goteja arran de paret) i `passos`
(algú passa pel bar i l'ombra dels peus talla la ratlla de llum de sota la porta).
"""
import math
from functools import lru_cache

from PIL import Image

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from hd.pix import Light, Canvas, W, H, hr
from hd.rooms.comu import obox, outline, cable, text, text_width, PLASTIC, SHEET, CARD, RED, YEL, GRAYC
from hd.rooms.pis_cuina import outline_poly
from hd.rooms.bar_sala import WOOD, STEELB, BRASS, ENAMEL, PORC, BOTTLES, SLATE
from hd.rooms.bar_rebost import (BRICK, MORTAR, CEMENT, DAMP, CRATE_Y, CRATE_R, LEMON, WHITEP, GREEN, KEG,  # noqa: F401
                                 INK, WATER)
from hd640.rooms.bar_sala_pla_comu import fast_diff

Canvas1x = Canvas                                   # (a 1×, com la sala en 3D)

FLOOR_Y = 200
BULB = (317, 35)
DESK_TOP = 155
DOOR = (40, 67, 101, FLOOR_Y)

LIGHT = Light(ambient=-0.9, vignette=(93, 53), floor_fade=(253, 40))
LIGHT.point(BULB[0], BULB[1] + 5, r=280, k=3.6, squash=1.2, power=1.6)    # la bombeta
LIGHT.point(71, FLOOR_Y + 3, r=53, k=0.7, squash=2.0, power=2.0)          # la llum del bar per sota la porta


# ─── Paret i terra ──────────────────────────────────────────────────────────

def wall(cv):
    """Maó emblanquinat fa molts anys: el blanc s'ha anat menjant, i a baix hi ha humitats i salnitre."""
    for y in range(0, FLOOR_Y):
        row = y // 9
        for x in range(W):
            off = 12 if row % 2 else 0
            bx = (x + off) // 24
            jy, jx = y % 9, (x + off) % 24
            joint = jy == 8 or jx == 23
            n = (hr(bx, row) - 0.5) * 0.7 + (hr(x // 2, y // 2, 4) - 0.5) * 0.3 + (hr(x, y, 5) - 0.5) * 0.15
            lime = hr(x // 12, y // 8, 7)                    # on encara queda calç
            if joint:
                cv.put(x, y, MORTAR, 2.0 + n * 0.4)
            else:
                edge = 0.5 if jy == 0 else (-0.4 if jy == 7 or jx == 22 else 0)   # el cantell del maó
                cv.put(x, y, BRICK, 2.8 + n * 0.6 + edge + (1.2 if lime > 0.55 else 0))
            # humitat a la part de baix de la paret, i el salnitre a la vora
            dh = 24 + 13 * math.sin(x / 31) + 8 * hr(x // 9, 1)
            if (FLOOR_Y - y) < dh:
                cv.tint(x, y, x, y, DAMP[1], 0.35)
            elif (FLOOR_Y - y) < dh + 1.5 and hr(x, 3) > 0.4:
                cv.tint(x, y, x, y, (190, 186, 170), 0.3)
    cv.rect(0, FLOOR_Y - 4, W - 1, FLOOR_Y - 1, CEMENT, 2.0)    # sòcol de ciment
    cv.hline(0, W - 1, FLOOR_Y - 4, CEMENT, 3.2)
    cv.hline(0, W - 1, FLOOR_Y, CEMENT, 0)
    # una canonada que travessa la paret, a dalt, amb abraçadores i una mica de rovell
    cv.rect(0, 11, W - 1, 15, STEELB, lambda x, y: 3.0 + (1.2 if y == 12 else 0) - (0.8 if y == 15 else 0))
    for bx in range(40, W, 120):
        cv.rect(bx, 9, bx + 3, 16, STEELB, lambda x, y: 2.0 + (1.0 if x == bx else 0))
        cv.put(bx + 1, 10, STEELB, 4.6)
    for rx in (210, 470, 560):
        cv.rect(rx, 14, rx + 5, 15, [(40, 20, 8), (90, 50, 20), (130, 80, 30)], 1.6)


def floor(cv):
    """Ciment amb taques, juntes de dilatació, una reixa de desguàs i serradures."""
    for y in range(FLOOR_Y + 1, H):
        dep = (y - FLOOR_Y) / (H - FLOOR_Y)
        for x in range(W):
            u = (x - W / 2) / (1 + dep * 0.6) + W / 2
            n = (hr(x // 4, y // 3, 2) - 0.5) * 0.5 + (hr(int(u) // 40, (y - FLOOR_Y) // 12, 9) - 0.5) * 0.6 \
                + (hr(x, y, 8) - 0.5) * 0.2
            joint = abs(u % 160) < 0.9
            cv.put(x, y, CEMENT, (1.6 if joint else 3.0 + n))
    # taques d'oli i de cervesa
    for (cx, cy, rx, ry) in ((160, 235, 24, 5), (440, 248, 35, 7), (560, 224, 16, 4)):
        cv.disc(cx, cy, rx, ry, CEMENT, lambda nx, ny: 1.8 + (nx * nx + ny * ny) * 0.8)
    # serradures escampades
    for i in range(40):
        x, y = 30 + int(hr(i, 71) * 580), 206 + int(hr(i, 72) * 50)
        cv.put(x, y, CARD, 2.6 + hr(i, 73))
    # la reixa del desguàs
    gx0, gy0 = 315, 243
    cv.rect(gx0, gy0, gx0 + 24, gy0 + 7, SLATE, 0.6)
    for i in range(0, 25, 3):
        cv.vline(gx0 + i, gy0, gy0 + 7, STEELB, 3.0)
        cv.put(gx0 + i, gy0, STEELB, 4.2)
    outline(cv, gx0 - 1, gy0 - 1, gx0 + 25, gy0 + 8, CEMENT)
    # la claror de la bombeta al terra
    cv.tint(187, 208, 453, 272, (255, 210, 140),
            lambda x, y: 0.10 * max(0, 1 - abs(x - BULB[0]) / 147) * max(0, 1 - (y - 208) / 67))


# ─── La porta, el penjador ─────────────────────────────────────────────────

def door(cv):
    """La porta del bar, vista des de dins: fusta pelada, una balda i la llum del bar per sota."""
    x0, y0, x1, y1 = DOOR
    obox(cv, x0 - 5, y0 - 5, x1 + 5, y1, WOOD, 3.2)
    obox(cv, x0, y0, x1, y1, WOOD, 2.4, top=0.4)
    for i in range(x0 + 8, x1, 11):                                 # taulons, amb la veta
        cv.vline(i, y0 + 1, y1 - 1, WOOD, 1.4)
        cv.vline(i + 1, y0 + 1, y1 - 1, WOOD, 3.0)
    for x in range(x0 + 2, x1 - 1):
        for y in range(y0 + 2, y1 - 1, 1):
            if hr(x, y // 6, 13) > 0.93:
                cv.put(x, y, WOOD, 1.8)
    for (a, b) in ((y0 + 27, y0 + 31), (y1 - 35, y1 - 31)):        # travessers, amb claus
        cv.rect(x0 + 2, a, x1 - 2, b, WOOD, lambda x, y: 3.2 + (0.8 if y == a else 0))
        cv.hline(x0 + 2, x1 - 2, b + 1, WOOD, 1.0)
        for nx in range(x0 + 6, x1 - 2, 11):
            cv.put(nx, a + 2, STEELB, 4.0)
    cv.disc(x1 - 9, 136, 3, 3, BRASS, lambda nx, ny: 3.6 - nx - ny)   # el pom
    obox(cv, x1 - 13, 123, x1 - 4, 127, STEELB, 3.8)                 # la balda
    cv.rect(x1 - 1, 122, x1 + 3, 128, STEELB, 2.8)
    cv.hline(x0, x1, y1, [(255, 224, 150)], 0, lit=0)                # la llum del bar
    cv.hline(x0 + 2, x1 - 2, y1 + 1, [(200, 160, 100)], 0, lit=0)
    cv.glow((x0 + x1) // 2, y1 + 3, 29, (255, 210, 130), 0.35)
    cv.darken(x1 + 6, y0, x1 + 10, y1, 0.4)


def hooks(cv):
    """El penjador al costat de la porta: la jaqueta de pana d'en Tomàs i un davantal de recanvi."""
    cv.rect(115, 77, 171, 81, WOOD, lambda x, y: 3.0 + (0.8 if y == 78 else 0))
    outline(cv, 115, 77, 171, 81, WOOD)
    for sx in (118, 168):
        cv.put(sx, 79, STEELB, 4.4)
    for hx in (125, 157):
        cv.rect(hx, 81, hx + 1, 87, BRASS, 3.6)
        cv.put(hx + 2, 86, BRASS, 3.0)
    # la jaqueta de pana marró
    jack = [(115, 88), (136, 85), (141, 93), (139, 144), (112, 144), (112, 96)]
    cv.poly(jack, CARD, lambda x, y: 2.2 + (0.6 if (x % 3) == 0 else 0) - (y - 85) * 0.008)
    outline_poly(cv, jack, CARD)
    cv.line(127, 88, 127, 142, CARD, 1.0)
    cv.line(119, 89, 126, 100, CARD, 3.2)                            # el coll
    cv.line(135, 88, 128, 100, CARD, 3.2)
    cv.hline(116, 124, 124, CARD, 1.2)                               # la butxaca
    for by in (106, 118, 130):
        cv.disc(130, by, 1.2, 1.2, [(20, 12, 6), (60, 40, 20)], 1.4)
    # el davantal negre, penjat pel coll, amb una taca
    ap = [(149, 88), (165, 88), (168, 131), (147, 131)]
    cv.poly(ap, SLATE, lambda x, y: 2.6 + (0.6 if x == 149 else 0))
    outline_poly(cv, ap, SLATE)
    cv.line(149, 88, 157, 83, SLATE, 3.4)
    cv.line(165, 88, 157, 83, SLATE, 3.4)
    cv.rect(151, 108, 163, 116, SLATE, 3.2)                           # la butxaca del davantal
    cv.disc(158, 98, 3, 2, [(30, 30, 34), (50, 50, 56)], 1.4)


def fusebox(cv):
    """El quadre elèctric, amb un cable pelat que fa por de mirar."""
    obox(cv, 187, 53, 211, 85, GRAYC, 3.0)
    cv.rect(191, 61, 207, 69, SLATE, 1.0)
    for i in range(5):
        cv.rect(192 + i * 3, 62, 193 + i * 3, 68, WHITEP, 3.6 if i != 2 else 2.0)
        cv.put(192 + i * 3, 63 if i != 2 else 67, WHITEP, 5.0)
    cv.rect(191, 74, 200, 80, YEL, 3.4)                              # el llamp groc
    cv.line(197, 75, 194, 78, SLATE, 1.0)
    cv.line(194, 78, 197, 78, SLATE, 1.0)
    cv.line(197, 78, 194, 80, SLATE, 1.0)
    cable(cv, [(200, 85), (203, 101), (195, 115), (200, 128)], SLATE, 1.6)
    cv.put(200, 129, [(200, 120, 60)], 0)                            # el coure pelat
    cv.put(201, 130, [(200, 120, 60)], 0)
    cv.rect(197, 16, 201, 52, GRAYC, lambda x, y: 2.6 + (0.8 if x == 197 else 0) - (0.8 if x == 201 else 0))


# ─── L'escriptori ──────────────────────────────────────────────────────────

def calendar(cv):
    """Un calendari d'una marca de cervesa, a la paret de damunt l'escriptori, encara al mes de fa dos anys."""
    x0, y0, x1, y1 = 235, 59, 272, 115
    obox(cv, x0, y0, x1, y1, SHEET, 4.4)
    cv.rect(x0 + 2, y0 + 2, x1 - 2, y0 + 24, CRATE_Y, lambda x, y: 2.8 - (y - y0) * 0.03)   # la foto
    cv.rect(248, y0 + 8, 259, y0 + 23, CRATE_Y, lambda x, y: 3.8 + (0.8 if x == 249 else 0))
    cv.rect(248, y0 + 5, 259, y0 + 8, WHITEP, 4.6)                     # l'espuma
    cv.put(251, y0 + 4, WHITEP, 4.6)
    cv.put(255, y0 + 4, WHITEP, 4.6)
    text(cv, '1985', x0 + 3, y0 + 27, INK, 2.0)
    for j in range(4):
        for i in range(7):
            cv.rect(x0 + 3 + i * 5, y0 + 34 + j * 5, x0 + 4 + i * 5, y0 + 34 + j * 5, [(110, 106, 120)], 0)
    cv.disc(x0 + 9, y0 + 34, 3, 2.4, RED, 2.6)                        # un dia encerclat
    cv.disc(x0 + 9, y0 + 34, 2, 1.4, SHEET, 4.2)
    cv.disc(253, y0 - 1, 1.6, 1.6, STEELB, 4.0)


def corkboard(cv):
    """Un suro amb factures clavades, un número de telèfon i una foto de l'equip de futbol."""
    x0, y0, x1, y1 = 283, 53, 373, 112
    obox(cv, x0 - 3, y0 - 3, x1 + 3, y1 + 3, WOOD, 3.4)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, CARD, 2.6 + (hr(x, y, 8) - 0.5) * 0.8)
    papers = ((288, 59, 309, 85, SHEET, 4.4, -1), (315, 61, 336, 80, YEL, 3.6, 1), (341, 59, 368, 93, SHEET, 4.0, 0),
              (293, 88, 320, 109, SHEET, 3.8, 1), (325, 85, 349, 107, PORC, 4.0, -1))
    for (a, b, c, d, ramp, lvl, tilt) in papers:
        pts = [(a, b + max(0, tilt)), (c, b + max(0, -tilt)), (c, d + max(0, -tilt)), (a, d + max(0, tilt))]
        cv.poly(pts, ramp, lvl)
        outline_poly(cv, pts, ramp)
        for ly in range(b + 5, d - 2, 3):
            cv.hline(a + 3, c - 4 - (ly * 7) % 6, ly, SLATE, 2.6)
        cv.disc((a + c) // 2, b + 1, 1.4, 1.4, RED, 3.4)
    # la foto de l'equip (verd i blau), dues files de jugadors
    cv.rect(328, 88, 347, 101, GREEN, 2.4)
    for i in range(6):
        cv.rect(330 + i * 3, 95, 331 + i * 3, 99, [(30, 30, 90), (60, 60, 160)], 1.0)
        cv.put(330 + i * 3, 94, [(200, 150, 120)], 0)
    for i in range(5):
        cv.rect(331 + i * 3, 91, 332 + i * 3, 93, [(30, 30, 90), (60, 60, 160)], 1.4)


def desk(cv):
    """L'escriptori d'en Tomàs: fusta fosca rascada, el calaix del mig amb el pany intel·ligent."""
    x0, x1 = 213, 387
    # el taulell, una mica des de dalt, amb rascades i la rodona d'un got
    cv.poly([(x0 + 3, DESK_TOP - 8), (x1 - 3, DESK_TOP - 8), (x1 + 3, DESK_TOP), (x0 - 3, DESK_TOP)], WOOD,
            lambda x, y: 4.2 + (y - DESK_TOP) * 0.06 + (0.5 if hr(x // 8, y, 2) > 0.8 else 0)
            - (0.6 if hr(x, y, 3) > 0.97 else 0))
    cv.ring(300, DESK_TOP - 3, 4, WOOD, 3.0, step=15)
    cv.rect(x0 - 3, DESK_TOP, x1 + 3, DESK_TOP + 4, WOOD, lambda x, y: 3.0 + (0.6 if y == DESK_TOP else 0))
    cv.hline(x0 - 3, x1 + 3, DESK_TOP + 4, WOOD, 0)
    # el frontal: dos calaixeres i el calaix del mig
    for (a, b) in ((x0, 261), (336, x1)):
        obox(cv, a, DESK_TOP + 5, b, FLOOR_Y + 11, WOOD, 2.2, top=0.2)
        for k in range(3):
            yy = DESK_TOP + 11 + k * 16
            obox(cv, a + 4, yy, b - 4, yy + 12, WOOD, 2.8, top=0.6)
            cv.rect((a + b) // 2 - 4, yy + 5, (a + b) // 2 + 4, yy + 7, BRASS, lambda x, y: 3.4 + (0.8 if y == yy + 5 else 0))
            cv.put((a + b) // 2, yy + 3, SLATE, 0.6)                      # el forat del pany (antic)
    # el forat de sota, fosc
    cv.rect(262, 183, 335, FLOOR_Y + 11, SLATE, 0.8)
    cv.darken(262, 183, 335, 189, 0.5)
    # la paperera al forat, plena de papers arrugats
    obox(cv, 307, 187, 328, FLOOR_Y + 11, GRAYC, 1.8)
    for k in range(4):
        cv.vline(311 + k * 5, 189, FLOOR_Y + 9, GRAYC, 1.0)
    for i in range(4):
        cv.disc(311 + i * 5, 187, 3, 1.8, SHEET, 3.0 + i * 0.4)
    drawer(cv, open_=False)
    cv.darken(x0 - 4, FLOOR_Y + 12, x1 + 5, FLOOR_Y + 17, lambda x, y: 0.7 - (y - FLOOR_Y - 12) * 0.1)


def drawer(cv, open_=False):
    """El calaix del mig: fusta vella i, clavat amb quatre cargols, el pany intel·ligent de 19,99 €."""
    y0, y1 = (160, 181) if not open_ else (168, 195)
    if open_:
        # el calaix tret: es veu per dins (fons clar)
        cv.poly([(261, 160), (336, 160), (339, 168), (259, 168)], WOOD, 1.2)
        cv.rect(264, 161, 333, 167, CARD, lambda x, y: 2.0 + (0.4 if y == 166 else 0))
        cv.vline(262, 161, 167, WOOD, 2.6)
        cv.vline(335, 161, 167, WOOD, 0.8)
    obox(cv, 261, y0, 336, y1, WOOD, 3.0, top=0.8)
    cv.hline(264, 333, y0 + 3, WOOD, 3.8)
    for x in range(263, 335):
        if hr(x, y0, 21) > 0.9:
            cv.put(x, y0 + 8 + int(hr(x, 22) * 8), WOOD, 2.2)               # rascades
    # el pany: plàstic blanc lluent, molt més nou que tot el que l'envolta (però no tan blanc com un paper: amb el
    # calaix obert semblava la servilleta de la recepta, tasca 235), amb el pom fosc al mig, que es vegi que és un pany
    lx0, ly0 = 291, y0 + 3
    obox(cv, lx0, ly0, lx0 + 16, ly0 + 15, WHITEP, 3.0, top=1.2)
    cv.disc(lx0 + 8, ly0 + 8, 3.6, 3.6, SLATE, lambda nx, ny: 3.4 - ny)
    cv.disc(lx0 + 8, ly0 + 8, 1.6, 1.6, WHITEP, 2.0)                     # el bombí, de pega
    led = (60, 230, 100) if open_ else (240, 40, 40)
    cv.flat(lx0 + 13, ly0 + 3, led)
    cv.flat(lx0 + 14, ly0 + 3, led)
    cv.glow(lx0 + 13, ly0 + 3, 7, led, 0.5)
    for (sx, sy) in ((lx0 + 2, ly0 + 2), (lx0 + 14, ly0 + 13), (lx0 + 2, ly0 + 13)):
        cv.flat(sx, sy, (120, 120, 126))
    for k in range(3):                                                     # el logo, en gris
        cv.flat(lx0 + 5 + k * 3, ly0 + 13, (170, 170, 176))


def desk_things(cv):
    """Damunt l'escriptori: el cendrer ple, el punxó de factures, la calculadora, el marc i el flexo."""
    t = DESK_TOP - 4
    # el flexo, encorbat cap a les factures
    cv.disc(229, t, 8, 2, SLATE, lambda nx, ny: 2.6 - ny)
    cv.line(229, t, 235, t - 24, STEELB, 3.0)
    cv.line(230, t, 236, t - 24, STEELB, 4.2)
    cv.disc(235, t - 24, 1.4, 1.4, STEELB, 4.0)
    cv.line(235, t - 24, 248, t - 32, STEELB, 3.0)
    cv.line(235, t - 25, 248, t - 33, STEELB, 4.2)
    shade = [(245, t - 35), (259, t - 32), (256, t - 24), (243, t - 28)]
    cv.poly(shade, GREEN, lambda x, y: 2.4 + (0.8 if y < t - 31 else 0))
    outline_poly(cv, shade, GREEN)
    # el punxó amb factures
    cv.vline(272, t - 24, t, STEELB, 4.2)
    for i in range(8):
        y = t - 2 - i * 2
        cv.hline(264 + (i % 2), 280 - (i % 3), y, SHEET, 4.2 - i * 0.15)
        cv.hline(264 + (i % 2), 280 - (i % 3), y + 1, SHEET, 2.4)
    cv.put(272, t - 25, STEELB, 5.4)
    # la calculadora, amb el rotlle de paper
    obox(cv, 285, t - 4, 307, t, PLASTIC, 2.4)
    cv.rect(288, t - 3, 296, t - 3, [(60, 80, 50), (120, 150, 90)], 1.0)
    for i in range(4):
        cv.put(299 + i * 2, t - 2, PLASTIC, 4.6)
    cv.rect(289, t - 9, 295, t - 5, SHEET, 4.4)
    # el cendrer ple de burilles (aquí dins sí que es fuma)
    cv.disc(320, t - 1, 8, 2.8, [(30, 40, 50), (70, 90, 110), (130, 160, 180), (190, 210, 220)], lambda nx, ny: 2.4 - ny)
    cv.disc(320, t - 2, 5, 1.4, [(40, 40, 40), (70, 70, 70), (110, 110, 110)], 1.6)    # la cendra
    for i in range(5):
        cv.line(314 + i * 3, t - 2, 317 + i * 3, t - 5 - (i % 2), SHEET, 4.0)
        cv.flat(317 + i * 3, t - 5 - (i % 2), (200, 140, 90))
    cv.put(323, t - 7, [(120, 120, 120)], 0)                              # el fum d'una que encara crema
    cv.put(324, t - 9, [(90, 90, 96)], 0)
    # el marc: la foto de mostra que venia amb el marc («la seva dona»)
    obox(cv, 341, t - 24, 363, t, BRASS, 3.4)
    cv.rect(344, t - 21, 360, t - 3, [(60, 90, 120), (120, 160, 190), (190, 210, 230)], 1.4)
    cv.disc(352, t - 13, 3.4, 4, [(140, 90, 70), (210, 160, 130), (240, 200, 170)], 1.8)
    cv.rect(348, t - 8, 356, t - 3, RED, 2.6)
    cv.disc(352, t - 17, 4, 2.2, YEL, 2.8)                                  # rossa, somrient, genèrica
    cv.hline(351, 353, t - 11, [(160, 60, 60)], 0)
    cv.rect(355, t - 6, 360, t - 3, [(250, 250, 250)], 0)                  # l'etiqueta del preu, encara
    cv.hline(356, 359, t - 5, [(200, 40, 40)], 0)
    cv.line(361, t, 365, t + 1, BRASS, 2.0)                                 # el peu
    # una tassa amb bolígrafs
    obox(cv, 371, t - 11, 380, t, PORC, 4.0)
    for i, c in enumerate((RED, PLASTIC, YEL)):
        cv.line(372 + i * 3, t - 11, 371 + i * 4, t - 19 + i, c, 3.0)


def chair(cv):
    """La cadira de despatx, de skai rebentat, apartada a l'esquerra de l'escriptori."""
    cx = 192
    cv.rect(cx - 1, 184, cx + 1, 213, STEELB, lambda x, y: 3.0 + (1.0 if x == cx - 1 else 0))
    for dx in (-13, -5, 5, 13):
        cv.line(cx, 213, cx + dx, 219, STEELB, 2.6)
        cv.disc(cx + dx, 220, 2, 1.4, SLATE, 2.0)
    back = [(176, 131), (203, 128), (205, 173), (176, 176)]
    cv.poly(back, SLATE, lambda x, y: 2.0 + (0.8 if x < 181 else 0) + (0.4 if hr(x // 3, y // 3) > 0.85 else 0))
    outline_poly(cv, back, SLATE)
    for (sx, sy) in ((184, 140), (196, 140), (184, 160), (196, 160)):       # els botons del capitonat
        cv.put(sx, sy, SLATE, 0.6)
        cv.put(sx + 1, sy + 1, SLATE, 3.4)
    cv.disc(189, 147, 4, 3, CARD, lambda nx, ny: 4.0 - ny)                  # l'escuma que surt pel forat
    seat = [(171, 173), (211, 171), (213, 184), (168, 187)]
    cv.poly(seat, SLATE, lambda x, y: 2.4 + (1.0 if y < 176 else 0))
    outline_poly(cv, seat, SLATE)
    cv.darken(176, 221, 211, 224, 0.6)


# ─── El magatzem ───────────────────────────────────────────────────────────

def no_smoking(cv):
    """«PROHIBIT FUMAR», ple de cremades de cigarreta."""
    x0, y0, x1, y1 = 440, 40, 507, 80
    obox(cv, x0, y0, x1, y1, ENAMEL, 4.6)
    cx, cy = 473, 51
    for r in (11, 10, 9):
        cv.ring(cx, cy, r, RED, 3.4, step=1)
    cv.rect(cx - 8, cy - 1, cx + 6, cy + 1, SHEET, 4.4)                     # la cigarreta
    cv.rect(cx + 4, cy - 1, cx + 6, cy + 1, [(200, 120, 60), (240, 160, 80)], 1.0)
    cv.put(cx + 7, cy - 3, SHEET, 2.6)
    cv.put(cx + 8, cy - 5, SHEET, 2.0)
    for k in range(3):
        cv.line(cx - 7 + k, cy + 7, cx + 6 + k, cy - 7, RED, 3.4)
    for k, word in enumerate(('PROHIBIT', 'FUMAR')):
        text(cv, word, (x0 + x1 - text_width(word)) // 2 + 1, y1 - 15 + k * 7, INK, 2.0)
    for (bx, by) in ((449, 48), (496, 64), (461, 69), (488, 45), (455, 60), (501, 51), (468, 76)):   # les cremades
        cv.disc(bx, by, 2.2, 1.8, [(20, 12, 6), (60, 40, 20), (110, 80, 40)], lambda nx, ny: 0.4 + (nx * nx + ny * ny) * 1.6)
    cv.disc(x0 + 3, y0 + 3, 1.2, 1.2, STEELB, 4.0)
    cv.disc(x1 - 3, y0 + 3, 1.2, 1.2, STEELB, 4.0)


def crate(cv, x0, y0, ramp, label=None):
    """Una caixa de cervesa de plàstic (48×27) amb els colls de les ampolles a dalt."""
    x1, y1 = x0 + 48, y0 + 27
    for i in range(8):                                                      # els colls, amb la xapa
        bx = x0 + 4 + i * 5 + (1 if i > 3 else 0)
        cv.rect(bx, y0 - 7, bx + 2, y0, BOTTLES[1], lambda x, y: 2.4 + (1.2 if x == bx else 0))
        cv.rect(bx, y0 - 8, bx + 2, y0 - 8, [(140, 120, 40), (200, 170, 60)], 1.4)
    obox(cv, x0, y0, x1, y1, ramp, 3.0, top=0.8)
    cv.rect(x0 + 6, y0 + 5, x1 - 6, y0 + 9, ramp, 1.2)                      # l'agafador
    cv.hline(x0 + 6, x1 - 6, y0 + 10, ramp, 4.0)
    for i in range(6):
        cv.vline(x0 + 6 + i * 7, y0 + 13, y1 - 3, ramp, 1.8)
        cv.vline(x0 + 7 + i * 7, y0 + 13, y1 - 3, ramp, 3.6)
    if label:
        text(cv, label, x0 + (48 - text_width(label)) // 2, y0 + 16, [(30, 6, 4), (240, 230, 200)], 1.0,
             flat=(250, 244, 220))


def crates(cv):
    """Les caixes de cervesa, apilades de qualsevol manera, i una capsa de tovallons."""
    crate(cv, 400, 173, CRATE_Y)
    crate(cv, 451, 173, CRATE_R)
    crate(cv, 501, 173, CRATE_Y)
    crate(cv, 424, 140, CRATE_R)
    crate(cv, 477, 139, CRATE_Y)
    crate(cv, 453, 105, CRATE_Y)
    # una capsa de cartró de tovallons, damunt de tot a la dreta
    w = text_width('TOVALLONS')
    obox(cv, 530 - w // 2 - 4, 123, 530 + w // 2 + 4, 165, CARD, 3.2, top=0.8)
    text(cv, 'TOVALLONS', 530 - w // 2, 136, [(30, 16, 8), (70, 40, 20)], 1.0)
    cv.hline(530 - w // 2 - 3, 530 + w // 2 + 3, 146, CARD, 4.4)              # la cinta d'embalar
    cv.vline(530, 124, 146, CARD, 4.4)
    for i in range(3):                                                         # les fletxes «amunt»
        cv.put(530 - w // 2 + 2 + i, 154 - i, [(30, 16, 8)], 0)
        cv.put(530 - w // 2 + 6 - i, 154 - i, [(30, 16, 8)], 0)
    cv.darken(397, FLOOR_Y + 1, 555, FLOOR_Y + 5, 0.5)


def shelves(cv):
    """Prestatgeria metàl·lica: llaunes, la caixa de llimones, un sac de sucre, garrafes i paquets de cafè."""
    x0, x1 = 565, 632
    for x in (x0, x1):
        cv.rect(x, 32, x + 1, FLOOR_Y + 5, STEELB, lambda xx, y: 3.2 + (0.8 if xx == x else 0))
        for hy in range(36, FLOOR_Y, 6):                                     # els forats del perfil
            cv.put(x, hy, STEELB, 1.0)
    for y in (59, 101, 144, 187):
        cv.rect(x0, y, x1 + 1, y + 2, STEELB, lambda x, yy: 3.8 + (0.8 if yy == y else 0))
        cv.hline(x0, x1 + 1, y + 3, STEELB, 0.8)
    # prestatge 1: llaunes de tomàquet i d'olives
    for i in range(8):
        lx = x0 + 3 + i * 8
        r = [(30, 6, 6), (110, 20, 20), (180, 40, 30), (230, 220, 200)] if i % 2 else STEELB
        obox(cv, lx, 46, lx + 6, 59, r, 2.6)
        cv.hline(lx + 1, lx + 5, 47, STEELB, 4.6)
        if i % 2:
            cv.rect(lx + 1, 51, lx + 5, 54, r, 3.6)
    # prestatge 2: la caixa de llimones (la llimonada!) i un sac de sucre
    w = text_width('LLIMONES')
    obox(cv, x0 + 2, 83, x0 + w + 8, 101, CARD, 2.6)
    for i in range(8):
        cv.disc(x0 + 7 + i * 5, 81 - (i % 2), 3, 2.6, LEMON, lambda nx, ny: 3.2 - ny - nx * 0.6)
    text(cv, 'LLIMONES', x0 + 5, 91, [(30, 16, 8), (90, 60, 20)], 1.0)
    obox(cv, x0 + w + 10, 82, x1 - 1, 101, SHEET, 3.6)
    text(cv, 'SUCRE', x0 + w + 11, 89, INK, 1.4)
    # prestatge 3: garrafes d'aigua
    for i in range(2):
        gx = x0 + 16 + i * 29
        cv.disc(gx, 128, 12, 15, [(30, 50, 70), (60, 100, 130), (120, 170, 200), (200, 230, 240)],
                lambda nx, ny: 1.6 + (1.6 if nx < -0.3 and ny < 0 else 0) + (0.6 if abs(ny - 0.2) < 0.08 else 0))
        cv.rect(gx - 3, 109, gx + 2, 114, [(10, 40, 110), (30, 80, 180)], 1.4)
        cv.put(gx - 5, 120, [(240, 250, 255)], 0)
    # prestatge 4: paquets de cafè
    for i in range(6):
        px = x0 + 3 + i * 10
        obox(cv, px, 165, px + 8, 187, [(14, 8, 6), (40, 24, 16), (90, 30, 20), (200, 160, 80)], 1.6)
        cv.rect(px + 2, 172, px + 6, 176, [(200, 160, 80)], 0)
        cv.hline(px + 1, px + 7, 167, [(40, 24, 16)], 0)


def keg_and_mop(cv):
    """Un barril de cervesa a terra i la fregona dins la galleda."""
    # el barril
    cx, top, bot = 597, 205, 245
    for y in range(top, bot + 1):
        for x in range(cx - 17, cx + 18):
            nx = (x - cx) / 17
            cv.put(x, y, KEG, 3.4 - nx * 1.6 + (1.6 if -0.5 < nx < -0.25 else 0) + (0.8 if (y - top) in (5, 35) else 0)
                   - (0.6 if (y - top) in (6, 36) else 0))
    cv.disc(cx, top, 17, 4, KEG, lambda nx, ny: 3.0 - ny)
    cv.disc(cx, top, 5, 1.8, SLATE, 1.6)
    cv.disc(cx, top - 1, 3, 1, STEELB, 4.0)                                  # el cap de tirar
    for x in (cx - 17, cx + 17):
        cv.vline(x, top, bot, KEG, 0)
    cv.darken(cx - 19, bot + 1, cx + 21, bot + 5, 0.55)
    # la galleda i la fregona
    gx = 131
    pts = [(gx - 13, 213), (gx + 13, 213), (gx + 11, 235), (gx - 11, 235)]
    cv.poly(pts, [(30, 10, 30), (80, 30, 90), (130, 60, 150), (180, 110, 200)], lambda x, y: 2.4 - (x - gx) * 0.05)
    outline_poly(cv, pts, [(20, 6, 20)])
    cv.hline(gx - 12, gx + 12, 218, [(30, 10, 30), (80, 30, 90), (130, 60, 150)], 2.8)   # el reforç
    cv.disc(gx, 213, 13, 3, [(20, 20, 26), (50, 50, 60), (90, 90, 100)], 1.4)
    cv.line(gx + 3, 213, gx + 19, 128, CARD, 3.4)
    cv.line(gx + 4, 213, gx + 20, 128, CARD, 2.2)
    cv.disc(gx + 1, 211, 8, 2.6, SHEET, lambda nx, ny: 2.6 - ny)
    for k in range(5):                                                       # les tires de la fregona
        cv.vline(gx - 6 + k * 3, 211, 214, SHEET, 3.0 - k * 0.2)
    cv.darken(gx - 12, 236, gx + 13, 239, 0.6)


def bulb(cv):
    """La bombeta nua, penjada del fil."""
    bx, by = BULB
    cv.vline(bx, 0, by - 7, SLATE, 1.4)
    cv.vline(bx + 1, 0, by - 7, SLATE, 0.6)
    obox(cv, bx - 3, by - 8, bx + 3, by - 4, BRASS, 3.0)
    cv.disc(bx, by, 5.4, 6.2, [(255, 220, 140)], 0, lit=0)
    cv.disc(bx - 1, by - 1, 2.6, 2.6, [(255, 250, 220)], 0, lit=0)
    cv.glow(bx, by, 53, (255, 200, 120), 0.45)


def bg(cv):
    wall(cv)
    floor(cv)
    fusebox(cv)
    hooks(cv)
    door(cv)
    calendar(cv)
    corkboard(cv)
    no_smoking(cv)
    shelves(cv)
    crates(cv)
    chair(cv)
    desk(cv)
    desk_things(cv)
    keg_and_mop(cv)
    bulb(cv)


# ─── Props ──────────────────────────────────────────────────────────────────

def calaix_obert(cv):
    """El calaix obert: el pany en verd i, a dins, el fons del calaix."""
    cv.rect(259, 157, 339, 196, SLATE, 0.6)
    drawer(cv, open_=True)


def recepta_calaix(cv):
    """La servilleta amb la recepta, dins el calaix obert (fins que la Vet l'agafa)."""
    pts = [(277, 163), (301, 161), (304, 166), (275, 167)]
    cv.poly(pts, SHEET, 5.0)
    outline_poly(cv, pts, SHEET)
    cv.line(280, 163, 296, 162, INK, 1.4)
    cv.line(281, 165, 299, 164, INK, 1.4)


PROPS = {'calaix_obert': calaix_obert, 'recepta_calaix': recepta_calaix}


# ─── Animacions ─────────────────────────────────────────────────────────────

@lru_cache(maxsize=None)
def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv.img


def _frames():
    """L'arna dona voltes a la bombeta (un vuit), amb les ales que baten i l'ombra a la paret."""
    base = _base()
    box = (BULB[0] - 30, 0, BULB[0] + 31, BULB[1] + 30)
    frames = []
    for i in range(16):
        cv = Canvas(light=LIGHT, img=base.copy())
        a = i / 16 * 2 * math.pi
        mx = BULB[0] + round(math.cos(a) * 15)
        my = BULB[1] + round(math.sin(a * 2) * 5) + 3
        up = i % 2
        wing = (90, 80, 70) if up else (150, 140, 120)
        cv.flat(mx, my, (40, 34, 30))
        cv.flat(mx, my + 1, (60, 50, 44))
        cv.flat(mx - 1, my - up, wing)
        cv.flat(mx + 1, my - up, wing)
        if not up:
            cv.flat(mx - 2, my, wing)
            cv.flat(mx + 2, my, wing)
        frames.append(fast_diff(cv.img, base, box))
    return frames


ANIMS = {'arna': {'frames': _frames, 'frameDuration': 70}}


DRIP_X = 560                   # entre la pila de caixes i la prestatgeria


def _frames_gota():
    """La canonada del sostre goteja: la gota s'infla, cau arran de paret i esquitxa el terra."""
    base = _base()
    box = (DRIP_X - 8, 10, DRIP_X + 9, FLOOR_Y + 6)
    empty = Image.new('RGBA', base.size, (0, 0, 0, 0))
    seq = [('n', 0)] * 3 + [('f', 1)] * 4 + [('f', 2)] * 3 + [('f', 3)] * 2
    y, v = 18.0, 2.0
    while y < FLOOR_Y - 2:
        seq.append(('c', int(y)))
        y, v = y + v, v + 4.0
    seq += [('s', 0), ('s', 1), ('s', 2)] + [('n', 0)] * 4
    frames = []
    for kind, k in seq:
        if kind == 'n':
            frames.append(empty)
            continue
        cv = Canvas(light=LIGHT, img=base.copy())
        if kind == 'f':                                            # la gota es forma sota la canonada
            for j in range(k):
                cv.put(DRIP_X, 16 + j, WATER, 3.0 - j * 0.3, lit=0)
            if k == 3:
                cv.flat(DRIP_X, 17, (190, 204, 210))
        elif kind == 'c':                                          # cau, amb una cua
            cv.put(DRIP_X, k, WATER, 3.4, lit=0)
            cv.put(DRIP_X, k + 1, WATER, 2.8, lit=0)
            cv.put(DRIP_X, k - 1, WATER, 2.0, lit=0)
            cv.put(DRIP_X, k - 2, WATER, 1.2, lit=0)
        else:                                                      # esquitx, i la taca que s'eixampla
            cv.put(DRIP_X, FLOOR_Y + 1, WATER, 3.0, lit=0)
            r = 1 + k * 2
            for d in (-1, 1):
                cv.put(DRIP_X + d * (r + 1), FLOOR_Y + 1 - (2 - k), WATER, 2.6, lit=0)
                cv.put(DRIP_X + d * r, FLOOR_Y + 2 - (2 - k), WATER, 2.0, lit=0)
        frames.append(fast_diff(cv.img, base, box))
    return frames


def _frames_passos():
    """Algú passa pel bar, a l'altra banda de la porta: l'ombra dels peus talla la ratlla de llum de sota."""
    base = _base()
    x0, y0, x1, y1 = DOOR
    box = (x0 - 2, y1 - 3, x1 + 3, y1 + 6)
    empty = Image.new('RGBA', base.size, (0, 0, 0, 0))
    frames = []
    for i in range(28):
        if i >= 14:
            frames.append(empty)
            continue
        cv = Canvas(light=LIGHT, img=base.copy())
        x = 28 + i * 6                                              # d'esquerra a dreta, dos peus
        for fx in (x, x + 12 - (5 if i % 2 else 0)):
            cv.darken(max(x0, fx), y1 - 1, min(x1, fx + 5), y1 + 1, 0.9, dither=False)
            cv.darken(max(x0, fx - 1), y1 + 2, min(x1, fx + 6), y1 + 4, 0.5)
        frames.append(fast_diff(cv.img, base, box))
    return frames


ANIMS['gota'] = {'frames': _frames_gota, 'frameDuration': 90}
ANIMS['passos'] = {'frames': _frames_passos, 'frameDuration': 120}


# ─── Geometria (coordenades de 640×360) ─────────────────────────────────────

GEOMETRIA = {
    'things': {
        'porta': {'rect': (35, 62, 106, 213), 'walk': (72, 248)},
        'calaix': {'rect': (261, 155, 336, 195), 'walk': (299, 251)},
        'caixes': {'rect': (400, 97, 555, 200), 'walk': (480, 251)},
    },
    'spawns': {'vet': (200, 259)},
    'walkable': [(19, 236), (621, 236), (632, 271), (8, 271)],
}
