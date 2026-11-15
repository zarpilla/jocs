"""
La terminal de l'aeroport (hd/rooms/aeroport_terminal.py) a 640×360, la composició ×4/3 dibuixada de nou.
Escena 3, la Vet, dimarts de matinada:
  - gris i blau fred: plafons de formigó, terra de rajola polida que reflecteix els fluorescents;
  - la vidriera gran: fora, l'alba sobre la pista i la cua d'un avió; a la zona de fumadors, la supervisora
    Ortega fuma i mira el mòbil (la cigarreta és el rellotge de la sincronia: es va escurçant amb els decorats
    `cigarreta_mitja` i `cigarreta_curta`);
  - el taulell de facturació (amb el pòsit de «8426» a sota), la porta de personal que vigila en Soler;
  - el panell de sortides amb el vol BCMU-07 a Ginebra;
  - objectes perduts: una garita amb un taulell (l'empleat hi és darrere) i prestatges plens (el maletí);
  - la cafeteria: una màquina de cafè que fa llum i una taula alta (les ulleres).
Animacions: `terminal` (el fum de la cigarreta i el llum anticol·lisió de l'avió), `panell` (la fletxeta
d'embarcament del BCMU-07) i `cafe` (els botons de la màquina s'encenen d'un en un).
"""
import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)

import math

from PIL import Image

from hd.pix import Light, Canvas, W, H, hr
from hd.rooms.comu import obox, outline, text, text_width, _diff, PLASTIC, SHEET, CARD, RED
from hd.rooms.bar_sala import STEELB, SLATE
from hd.rooms.pis_cuina import outline_poly
from hd.characters import M
from hd.personatges import hair_cap
from hd.rooms.aeroport_terminal import (CONC, TILE, DAWN, TARMAC, GLASS, DESK, BLUE, AMBER, BOARD, YELS,  # noqa: F401
                                        WOODC, PLANT, CHROME, VEND)
from hd640.draw_characters import person

FLOOR_Y = 200

LIGHT = Light(ambient=-0.1, vignette=(93, 40), floor_fade=(259, 40))
LIGHT.point(320, -40, r=400, k=2.2, squash=0.7, power=1.2)           # els fluorescents del sostre
LIGHT.point(607, 133, r=80, k=1.0, squash=1.0, power=2.0)            # la màquina de cafè
LIGHT.point(320, 149, r=120, k=0.7, squash=1.6, power=2.0)           # la claror de l'alba per la vidriera

# L'Ortega és a fora, lluny: petita (K) i amb els peus al paviment de la zona de fumadors (FEET_Y).
# Els detalls (monyo, gafet, mòbil, cigarreta) es van dibuixar a 480 sobre la figura a escala 0.78 amb l'origen
# a (259, 28); `_o` els porta a l'escala i el lloc d'ara (i a 640).
K = 0.6
FEET_Y = 140
_OX, _OY = 352, FEET_Y - round(116 * K)


def _o(x, y):
    return round((264 + (x - 259) * K / 0.78) * 4 / 3), round((53 + (y - 28) * K / 0.78) * 4 / 3)


# la cigarreta: de la mà de l'Ortega cap a la dreta; llargada segons l'estat
CIG = _o(287, 67)
CIG_LEN = {'sencera': 11, 'mitja': 7, 'curta': 3}

TAIL_LED = (248, 76)          # el llum anticol·lisió de la cua de l'avió
BOARD_BOX = (48, 15, 195, 53)
CAFE = (592, 69, 635, FLOOR_Y)


# ─── Paret, sostre i terra ─────────────────────────────────────────────────

def wall(cv):
    """Plafons de formigó amb juntes, un fals sostre amb fluorescents i una franja blava d'aeroport."""
    for y in range(0, FLOOR_Y):
        for x in range(W):
            seam = (x % 80 == 0) or (y % 48 == 47 and y > 13)
            n = (hr(x // 2, y // 2, 3) - 0.5) * 0.3 + (hr(x, y, 4) - 0.5) * 0.15 + (hr(x // 80, y // 48, 6) - 0.5) * 0.4
            lvl = 2.2 if seam else 4.0 + n
            if not seam and (x % 80 == 1 or y % 48 == 0):
                lvl += 0.5                                              # el cantell de llum de la junta
            cv.put(x, y, CONC, lvl)
    # els forats dels ancoratges, a les cantonades dels plafons
    for px in range(0, W, 80):
        for py in range(47, FLOOR_Y, 48):
            for dx in (6, 73):
                cv.put(px + dx, py - 5, CONC, 2.0)
                cv.put(px + dx, py - 42, CONC, 2.0)
    # el fals sostre
    for x in range(W):
        for y in range(0, 9):
            cv.put(x, y, CONC, 5.0 - y * 0.15 + (0.6 if x % 32 == 0 else 0))
    cv.hline(0, W - 1, 9, CONC, 1.4)
    for fx in range(27, W, 160):                                       # els fluorescents
        obox(cv, fx - 3, 1, fx + 83, 7, CHROME, 3.6)
        cv.rect(fx, 3, fx + 80, 5, [(230, 240, 250)], 0, lit=0)
        cv.hline(fx, fx + 80, 4, [(248, 252, 255)], 0, lit=0)
        cv.glow(fx + 40, 5, 32, (220, 236, 255), 0.25)
    # la franja blava, a mitja alçada
    cv.rect(0, 123, W - 1, 127, BLUE, 2.6)
    cv.hline(0, W - 1, 123, BLUE, 3.4)
    cv.rect(0, FLOOR_Y - 7, W - 1, FLOOR_Y - 1, CONC, 2.4)             # sòcol
    cv.hline(0, W - 1, FLOOR_Y - 7, CONC, 3.2)
    cv.hline(0, W - 1, FLOOR_Y, CONC, 0.6)


def floor(cv):
    """Rajola polida, en perspectiva; brilla amb els reflexos de la vidriera i dels fluorescents."""
    for y in range(FLOOR_Y + 1, H):
        dep = (y - FLOOR_Y) / (H - FLOOR_Y)
        v = (y - FLOOR_Y) * 1.6 / (1 + dep * 0.5)
        for x in range(W):
            u = (x - W / 2) / (0.6 + dep * 0.8) + W / 2
            if (u % 48) < 0.9 or (v % 26.67) < 0.8:
                cv.put(x, y, TILE, 2.6)
                continue
            n = (hr(int(u // 48), int(v // 26.67), 2) - 0.5) * 0.4
            cv.put(x, y, TILE, 4.0 + n + (hr(x, y, 9) - 0.5) * 0.3)
    # el reflex de l'alba de la vidriera, a terra
    cv.tint(227, 203, 413, 267, (200, 140, 150), lambda x, y: 0.22 * max(0, 1 - (y - 203) / 64) * (0.6 + 0.4 * math.sin(x / 9.3) ** 2))
    cv.tint(0, 203, W - 1, 224, (220, 236, 255), lambda x, y: 0.06 * max(0, 1 - (y - 203) / 21))
    # el resplendor vermell de la màquina de cafè
    cv.tint(585, 203, 639, 250, (230, 90, 70), lambda x, y: 0.12 * max(0, 1 - (y - 203) / 47) * max(0, 1 - abs(x - 613) / 30))


# ─── La vidriera ───────────────────────────────────────────────────────────

def outside(cv):
    """L'alba sobre la pista: cel, la línia d'arbres llunyana, un avió aparcat i la zona de fumadors."""
    x0, y0, x1, y1 = 229, 37, 411, 147
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, DAWN, 0.6 + (y - y0) / 12.0, lit=0)
    # dos núvols prims, rosats
    for x in range(x0, x1):
        yy = 61 + int(3 * math.sin(x / 15))
        if hr(x // 7, 3) > 0.3:
            cv.put(x, yy, DAWN, 6.2, lit=0)
            if hr(x // 4, 5) > 0.6:
                cv.put(x, yy + 1, DAWN, 5.4, lit=0)
        yy = 50 + int(2 * math.sin(x / 21 + 1))
        if hr(x // 9, 8) > 0.55:
            cv.put(x, yy, DAWN, 5.0, lit=0)
    # un estel que encara aguanta
    cv.flat(381, 44, (230, 230, 255))
    # l'horitzó: arbres i les llums de la pista
    for x in range(x0, x1 + 1):
        top = 104 - int(3 * hr(x // 5, 1) + 2 * math.sin(x / 17))
        for y in range(top, 112):
            cv.put(x, y, TARMAC, 1.0, lit=0)
    for y in range(112, y1 + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, TARMAC, 1.6 + (y - 112) / 19, lit=0)
    for lx in range(235, 411, 12):
        cv.flat(lx, 112, (120, 200, 255) if (lx // 12) % 2 else (250, 200, 90))
    cv.hline(x0, x1, 118, TARMAC, 2.6, lit=0)                         # la línia de la pista
    # l'avió aparcat: la cua i el fuselatge, a l'esquerra
    tail = [(245, 75), (259, 75), (275, 101), (275, 109), (237, 109)]
    cv.poly(tail, CONC, 4.6, lit=0)
    cv.poly([(248, 77), (257, 77), (267, 93), (253, 93)], BLUE, 3.0, lit=0)
    cv.line(247, 78, 251, 78, BLUE, 4.4, lit=0)
    cv.poly([(262, 100), (280, 100), (283, 103), (266, 103)], CONC, 4.0, lit=0)   # l'estabilitzador
    cv.rect(235, 101, 320, 115, CONC, lambda x, y: 5.4 - (y - 101) * 0.19, lit=0)
    cv.hline(235, 320, 109, BLUE, 2.6, lit=0)                          # la franja de la companyia
    for wx in range(277, 318, 5):
        cv.rect(wx, 104, wx + 1, 105, [(30, 40, 60)], 0, lit=0)
    cv.rect(286, 103, 288, 108, CONC, 3.2, lit=0)                      # la porta de darrere
    obox(cv, 296, 115, 316, 120, CONC, 3.0, lit=0)                     # el motor
    cv.rect(296, 116, 297, 119, TARMAC, 0.6, lit=0)
    cv.flat(*TAIL_LED, (255, 60, 60))
    # la zona de fumadors: una paperera-cendrer i el paviment
    cv.rect(x0, 128, x1, y1, CONC, lambda x, y: 2.8 + (0.6 if (x + y) % 12 == 0 else 0) + (0.4 if (x - y) % 12 == 0 else 0), lit=0)
    cv.hline(x0, x1, 128, CONC, 3.6, lit=0)
    obox(cv, 397, 109, 405, 133, STEELB, 3.0, lit=0)
    cv.rect(396, 108, 406, 109, STEELB, 4.6, lit=0)
    cv.rect(398, 107, 404, 107, SLATE, 1.6, lit=0)                     # la sorra del cendrer
    cv.flat(400, 106, (220, 216, 200))
    cv.flat(402, 106, (200, 160, 100))
    cv.vline(398, 113, 128, STEELB, 4.0, lit=0)


ORTEGA = {'skin': M((56, 30, 34), (104, 62, 56), (152, 100, 80), (194, 138, 106), (222, 172, 136), (240, 204, 172)),
          'legs': M((8, 8, 14), (18, 18, 28), (30, 30, 44), (44, 44, 60), (62, 62, 80)),
          'top': M((20, 6, 12), (44, 12, 22), (72, 20, 34), (104, 32, 46), (136, 48, 58), (168, 72, 76), dith=0.0),
          'shoes': M((6, 6, 8), (14, 14, 18), (26, 26, 32), (44, 44, 52)), 'thin': 1,
          'hooks': {'hair': hair_cap(M((10, 10, 12), (24, 22, 26), (40, 38, 42), (60, 58, 62), (86, 84, 88)), fringe=0.5)}}


def ortega(cv, cig='sencera'):
    """La supervisora Ortega, darrere el vidre: uniforme granat, gafet, el mòbil en una mà i la cigarreta a l'altra."""
    fig = person(ORTEGA, 'D')
    fig = fig.resize((round(fig.width * K), round(fig.height * K)), Image.NEAREST)
    # l'ombra als peus, perquè trepitgi el paviment i no suri
    cx0, _ = _o(268, 0)
    cx1, _ = _o(290, 0)
    cv.tint(cx0, FEET_Y - 1, cx1, FEET_Y + 2, (4, 6, 10), 0.55)
    cv.img.alpha_composite(fig, (_OX, _OY))
    # el monyo i el mocador de coll
    mx, my = _o(278, 32)
    cv.disc(mx, my, 2.7, 2.7, [(10, 10, 12), (30, 28, 32), (56, 54, 58)], lambda nx, ny: 1.8 - ny, lit=0)
    (sx0, sy), (sx1, _) = _o(275, 48), _o(282, 48)
    cv.hline(sx0, sx1, sy, YELS, 3.0, lit=0)
    cv.flat(sx1 - 1, sy + 1, YELS[2])                                   # la punta del mocador
    gx, gy = _o(281, 55)
    cv.rect(gx, gy, gx + 1, gy, [(230, 230, 240)], 0, lit=0)            # el gafet
    cv.rect(gx, gy + 1, gx + 1, gy + 1, [(90, 140, 200)], 0, lit=0)
    # el mòbil, a la mà esquerra (la pantalla li il·lumina la cara des de baix)
    px, py = _o(268, 64)
    px += 2                                                             # a la mà de la figura de 640
    cv.rect(px, py, px + 1, py + 3, [(20, 20, 26)], 0, lit=0)
    cv.rect(px, py + 1, px, py + 2, [(170, 220, 255)], 0, lit=0)
    lx, ly = _o(272, 46)
    cv.glow(lx, ly, 8, (150, 200, 255), 0.18)
    # la cigarreta
    n = CIG_LEN[cig]
    cx, cy = CIG
    cv.hline(cx, cx + n - 1, cy, [(236, 232, 222)], 0, lit=0)
    cv.hline(cx, cx + 1, cy, [(210, 150, 80)], 0, lit=0)                # el filtre
    cv.flat(cx + n, cy, (255, 110, 40))                                 # la brasa
    cv.flat(cx + n, cy - 1, (120, 110, 104))                            # una mica de cendra
    cv.glow(cx + n, cy, 3, (255, 120, 40), 0.5)


def window_frame(cv):
    """El marc d'alumini, el muntant del mig i el reflex dels fluorescents al vidre."""
    x0, y0, x1, y1 = 227, 35, 413, 149
    cv.tint(x0, y0, x1, y1, (150, 180, 220), lambda x, y: 0.10 if (x - y) % 53 < 8 else (0.06 if (x - y) % 53 < 11 else 0.04))
    for (a, b, c, d) in ((x0, y0, x1, y0 + 3), (x0, y1 - 3, x1, y1), (x0, y0, x0 + 3, y1), (x1 - 3, y0, x1, y1), (318, y0, 321, y1)):
        cv.rect(a, b, c, d, CHROME, lambda x, y, a=a, b=b: 3.0 + (0.8 if x == a or y == b else 0))
    outline(cv, x0 - 1, y0 - 1, x1 + 1, y1 + 1, CONC)
    # la goma negra de les juntes
    cv.vline(317, y0 + 4, y1 - 4, SLATE, 0.6)
    cv.vline(322, y0 + 4, y1 - 4, SLATE, 0.6)



def seats(cv):
    """Una fila de seients d'espera, sota la vidriera."""
    for i in range(5):
        sx = 243 + i * 32
        back = [(sx, 155), (sx + 27, 155), (sx + 27, 176), (sx, 176)]
        cv.poly(back, BLUE, lambda x, y: 2.4 + (0.8 if y < 159 else 0) + (0.3 if (x + y) % 5 == 0 else 0))
        outline_poly(cv, back, BLUE)
        seat = [(sx - 1, 176), (sx + 28, 176), (sx + 29, 184), (sx - 2, 184)]
        cv.poly(seat, BLUE, lambda x, y: 3.2 - (y - 176) * 0.15)
        outline_poly(cv, seat, BLUE)
        if i < 4:
            cv.rect(sx + 28, 168, sx + 31, 170, CHROME, 3.8)            # el braç
            cv.vline(sx + 29, 170, 176, CHROME, 2.6)
    cv.rect(240, 185, 400, 188, CHROME, lambda x, y: 3.0 + (1.0 if y == 185 else 0))
    for lx in (248, 320, 392):
        cv.rect(lx, 188, lx + 1, 203, CHROME, 2.6)
        cv.rect(lx - 2, 203, lx + 3, 203, CHROME, 2.0)
    cv.darken(237, 204, 403, 208, 0.5)
    # algú s'ha deixat un diari
    paper = [(309, 173), (328, 172), (329, 177), (308, 179)]
    cv.poly(paper, SHEET, 4.2)
    for k in range(2):
        cv.hline(312, 324 - k * 4, 174 + k * 2, SLATE, 2.6)


# ─── El panell de sortides i la facturació ─────────────────────────────────

ROWS = (('GINEBRA', 'BCMU-07', '06:10'), ('PARÍS', 'VY 8000', '06:45'), ('PALMA', 'IB 1234', '07:05'),
        ('ROMA', 'AZ 0077', '07:30'))


def departures(cv):
    """El panell de sortides: el BCMU-07 a Ginebra, a les 6:10."""
    x0, y0, x1, y1 = BOARD_BOX
    cv.vline(80, 9, y0, STEELB, 2.4)
    cv.vline(163, 9, y0, STEELB, 2.4)
    obox(cv, x0, y0, x1, y1, BOARD, 1.4)
    for j, (dest, fl, hh) in enumerate(ROWS):
        yy = y0 + 4 + j * 9
        col = (250, 190, 50) if j else (255, 220, 120)
        text(cv, dest, x0 + 4, yy, AMBER, 0, lit=0, flat=col)
        text(cv, fl, x0 + 58, yy, AMBER, 0, lit=0, flat=col)
        text(cv, hh, x1 - 4 - text_width(hh), yy, AMBER, 0, lit=0, flat=col)
    cv.glow((x0 + x1) // 2, y0 + 16, 53, (250, 180, 60), 0.08)


def staff_door(cv):
    """La porta de personal: metàl·lica, grisa, amb «NOMÉS PERSONAL»; l'agent Soler la vigila."""
    x0, y0, x1, y1 = 11, 53, 35, FLOOR_Y
    obox(cv, x0 - 3, y0 - 3, x1 + 3, y1, CHROME, 2.4)
    obox(cv, x0, y0, x1, y1, DESK, 3.4, top=0.6)
    cv.rect(x0 + 4, y0 + 5, x1 - 4, y0 + 24, GLASS, 1.6)                  # finestreta
    cv.line(x0 + 5, y0 + 16, x0 + 12, y0 + 6, GLASS, 2.4)
    outline(cv, x0 + 3, y0 + 4, x1 - 3, y0 + 25, CHROME)
    cv.rect(x1 - 7, 128, x1 - 4, 131, CHROME, 4.4)                       # la maneta
    cv.rect(x1 - 5, 132, x1 - 4, 134, CHROME, 2.6)
    cv.rect(x0, 171, x1, 175, CHROME, lambda x, y: 3.6 + (1.0 if y == 172 else 0))   # la barra antipànic
    cv.rect(x0 + 1, y1 - 9, x1 - 1, y1 - 1, CHROME, 2.8)                 # la xapa de cops
    for hy in (y0 + 8, y1 - 20):                                         # frontisses
        cv.rect(x0 - 1, hy, x0, hy + 6, CHROME, 3.8)
    # el senyal de prohibit el pas
    cv.disc(23, 88, 8, 8, RED, lambda nx, ny: 3.6 - ny * 0.6)
    cv.ring(23, 88, 8, RED, 2.2, step=4)
    cv.rect(17, 87, 29, 89, [(250, 244, 236)], 0)


def checkin(cv):
    """El taulell de facturació: frontal de laminat blau amb el logotip, la cinta de les maletes i els monitors."""
    x0, x1 = 40, 205
    top = 139
    # els monitors i el cartell «FACTURACIÓ», al darrere
    for mx in (67, 144):
        obox(cv, mx, 112, mx + 29, 133, PLASTIC, 1.8)
        cv.rect(mx + 3, 115, mx + 26, 129, BLUE, lambda x, y: 2.0 + (0.4 if y < 118 else 0), lit=0)
        cv.hline(mx + 5, mx + 16, 120, BLUE, 4.0, lit=0)
        cv.hline(mx + 5, mx + 21, 123, BLUE, 3.2, lit=0)
        cv.hline(mx + 5, mx + 12, 126, BLUE, 3.2, lit=0)
        cv.flat(mx + 26, 132, (60, 230, 90))
        cv.rect(mx + 13, 133, mx + 16, top, PLASTIC, 2.4)
        cv.glow(mx + 14, 122, 16, (90, 140, 230), 0.10)
    obox(cv, 88, 61, 157, 77, BLUE, 3.0)
    cv.hline(90, 155, 63, BLUE, 3.8)
    w = text_width('FACTURACIÓ')
    text(cv, 'FACTURACIÓ', 123 - w // 2, 67, [(240, 244, 250)], 0, flat=(240, 244, 250))
    cv.vline(107, 52, 61, STEELB, 2.4)
    cv.vline(139, 52, 61, STEELB, 2.4)
    # el taulell
    cv.rect(x0 - 5, top, x1 + 5, top + 5, DESK, lambda x, y: 6.0 - (y - top) * 0.4)
    cv.hline(x0 - 5, x1 + 5, top + 6, DESK, 0.6)
    for y in range(top + 7, FLOOR_Y + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, BLUE, 2.4 + (0.6 if (x - x0) % 41 == 0 else 0) - (y - top) * 0.015 + (hr(x, y, 12) - 0.5) * 0.25)
    outline(cv, x0, top + 7, x1, FLOOR_Y, BLUE)
    # els números dels mostradors
    for k, nx in enumerate((61, 143)):
        obox(cv, nx, top + 10, nx + 10, top + 18, [(240, 244, 250), (250, 252, 255)], 0)
        text(cv, str(k + 1), nx + 4, top + 12, [(20, 40, 90)], 0, flat=(20, 40, 90))
    # el logotip de la companyia: un avió estilitzat
    cv.poly([(112, 163), (133, 155), (139, 157), (123, 165), (133, 173), (128, 175), (112, 168)], [(240, 244, 250)], 0, lit=0)
    # la bàscula de les maletes, a l'esquerra
    obox(cv, 8, 176, 40, FLOOR_Y + 2, CHROME, 2.6)
    cv.rect(13, 179, 35, 181, SLATE, 1.6)
    obox(cv, 18, 186, 30, 191, [(4, 8, 4), (30, 60, 30)], 1.0, lit=0)       # el pes, en verd
    text(cv, '0.0', 19, 187, [(90, 220, 110)], 0, lit=0, flat=(90, 220, 110))
    # el pòsit groc, enganxat sota el cantell del taulell (es veu de reüll)
    cv.rect(176, top + 7, 183, top + 12, YELS, lambda x, y: 3.6 + (0.4 if y == top + 7 else 0))
    cv.darken(x0, FLOOR_Y + 1, x1 + 8, FLOOR_Y + 5, 0.5)
    # el pal de la cua amb la cinta
    px = 216
    cv.rect(px, 165, px + 1, 208, CHROME, lambda x, y: 3.6 + (0.8 if x == px else 0))
    cv.disc(px, 165, 2, 1.4, CHROME, 4.4)
    cv.disc(px, 209, 5, 2, CHROME, 2.6)
    cv.rect(px - 24, 171, px, 172, BLUE, 3.4)
    cv.darken(px - 6, 211, px + 7, 213, 0.5)


# ─── Objectes perduts ──────────────────────────────────────────────────────

def lost_found(cv):
    """La garita d'objectes perduts: el rètol groc, prestatges plens de coses i el taulell (l'empleat hi és darrere)."""
    x0, y0, x1 = 440, 77, 568
    # el rètol
    obox(cv, x0, y0, x1, 93, YELS, 3.2)
    cv.hline(x0 + 2, x1 - 2, y0 + 2, YELS, 4.0)
    w = text_width('OBJECTES PERDUTS')
    text(cv, 'OBJECTES PERDUTS', (x0 + x1 - w) // 2, 82, [(20, 14, 4)], 0, flat=(30, 22, 6))
    # l'interior: paret del fons més fosca
    cv.rect(x0 + 3, 94, x1 - 3, 149, CONC, lambda x, y: 2.6 + (hr(x // 2, y // 2, 13) - 0.5) * 0.3)
    # prestatges
    for y in (115, 141):
        cv.rect(x0 + 3, y, x1 - 3, y + 1, WOODC, 3.0)
        cv.hline(x0 + 3, x1 - 3, y + 2, CONC, 1.6)
        for bx in (x0 + 10, x1 - 10):                                   # escaires
            cv.line(bx, y + 2, bx + 3, y + 5, STEELB, 2.2)
    # prestatge de dalt: paraigües, un osset, una gorra, un casc
    for i in range(4):
        ux = 448 + i * 7
        cv.line(ux, 113, ux + 3, 96, [(10, 10, 16), (30, 30, 44), (60, 60, 90)] if i % 2 else VEND, 1.4)
        cv.line(ux - 1, 113, ux + 1, 104, [(10, 10, 16), (30, 30, 44), (60, 60, 90)] if i % 2 else VEND, 2.2)
        cv.flat(ux + 3, 96, (180, 180, 180))
        cv.flat(ux, 114, (40, 30, 20))                                  # el mànec
    cv.disc(488, 107, 7, 7, CARD, lambda nx, ny: 3.6 - nx - ny)         # l'osset
    cv.disc(484, 100, 2.7, 2.7, CARD, 3.4)
    cv.disc(492, 100, 2.7, 2.7, CARD, 3.4)
    cv.disc(488, 109, 3, 2.2, CARD, 4.4)                                # el musell
    cv.flat(486, 105, (20, 10, 6))
    cv.flat(490, 105, (20, 10, 6))
    cv.flat(488, 108, (40, 20, 10))
    cv.rect(484, 112, 492, 113, RED, 3.0)                               # una cinta al coll
    cv.disc(517, 109, 8, 5, RED, lambda nx, ny: 3.4 - ny)               # una gorra
    cv.rect(523, 112, 531, 113, RED, 2.0)
    cv.flat(517, 104, RED[4])
    cv.disc(549, 107, 9, 8, [(10, 10, 14), (30, 30, 40), (70, 70, 90), (140, 140, 170)],
            lambda nx, ny: 2.0 + (1.6 if nx < -0.3 and ny < -0.2 else 0))   # un casc de moto
    cv.disc(552, 108, 5, 3, [(20, 24, 30), (60, 80, 100), (120, 150, 170)], lambda nx, ny: 1.0 + (1.2 if nx < -0.4 else 0))
    # prestatge de baix: una maleta, un ukelele, una bossa (el maletí, quan hi és, va a la dreta)
    obox(cv, 448, 120, 477, 141, BLUE, 2.4)
    cv.rect(459, 116, 467, 118, SLATE, 2.0)
    cv.vline(462, 122, 139, BLUE, 1.6)
    cv.rect(452, 126, 458, 130, [(240, 220, 120)], 0)                   # l'etiqueta de facturació
    cv.disc(491, 133, 7, 7, WOODC, lambda nx, ny: 3.6 - nx * 0.6)
    cv.disc(491, 125, 5, 5, WOODC, 3.4)
    cv.rect(490, 115, 492, 126, WOODC, 2.4)
    cv.disc(491, 132, 2, 2, SLATE, 0.8)
    for sx in (490, 492):
        cv.vline(sx, 116, 136, [(220, 216, 200)], 0)
    bag = [(501, 141), (520, 141), (517, 125), (504, 125)]
    cv.poly(bag, [(30, 50, 30), (50, 90, 50), (80, 130, 70)], lambda x, y: 1.6 + (0.4 if x < 507 else 0))
    cv.line(506, 125, 510, 120, [(30, 50, 30), (50, 90, 50)], 1.2)
    cv.line(515, 125, 511, 120, [(30, 50, 30), (50, 90, 50)], 1.2)
    # els laterals de la garita
    for sx in (x0, x1 - 3):
        cv.rect(sx, 93, sx + 3, FLOOR_Y, CHROME, lambda x, y, sx=sx: 3.0 + (0.8 if x == sx + 1 else 0))
    lost_counter(cv)


def lost_counter(cv):
    """El taulell de la garita (per davant de l'empleat)."""
    x0, x1 = 440, 568
    top = 149
    cv.rect(x0, top, x1, top + 4, DESK, lambda x, y: 6.0 - (y - top) * 0.5)
    cv.hline(x0, x1, top + 5, DESK, 0.6)
    for y in range(top + 6, FLOOR_Y + 1):
        for x in range(x0 + 3, x1 - 1):
            cv.put(x, y, YELS, 1.8 + (0.5 if (x - x0) % 32 == 0 else 0) + (hr(x, y, 14) - 0.5) * 0.2)
    outline(cv, x0, top + 6, x1, FLOOR_Y, YELS)
    # un timbre, un formulari i un bolígraf
    cv.disc(459, top - 1, 4, 2, CHROME, lambda nx, ny: 4.4 - ny)
    cv.disc(459, top - 3, 1.4, 1, CHROME, 5.0)
    cv.flat(459, top - 4, (220, 220, 220))
    cv.poly([(533, top - 3), (552, top - 3), (555, top + 1), (531, top + 1)], SHEET, 4.6)
    for k in range(2):
        cv.hline(537, 549 - k * 5, top - 2 + k * 2, SLATE, 3.0)
    cv.line(522, top, 529, top - 2, [(30, 60, 160)], 0)
    cv.darken(x0, FLOOR_Y + 1, x1 + 3, FLOOR_Y + 5, 0.5)


# ─── La cafeteria ──────────────────────────────────────────────────────────

def cafe(cv):
    """La màquina de cafè (vermella i lluminosa), una planta de plàstic i la taula alta."""
    # la planta, al racó entre la garita i la cafeteria
    obox(cv, 571, 176, 584, FLOOR_Y + 2, CONC, 3.4)
    cv.hline(572, 583, 177, SLATE, 1.0)
    for i in range(9):
        a = -1.25 + i * 0.31
        L = 15 + (i % 3) * 3
        cv.line(577, 176, 577 + round(math.sin(a) * L * 0.65), 176 - round(math.cos(a) * L), PLANT, 2.6 + (i % 2))
    # la màquina
    x0, y0, x1, y1 = CAFE
    obox(cv, x0, y0, x1, y1, VEND, 2.6)
    cv.vline(x0 + 1, y0 + 1, y1, VEND, 3.6)
    cv.rect(x0 + 4, y0 + 5, x1 - 4, y0 + 40, [(60, 30, 20), (140, 80, 40), (220, 150, 80), (250, 210, 150)],
            lambda x, y: 1.4 + (y - y0) / 19, lit=0)
    cv.disc(613, y0 + 26, 9, 5, [(60, 30, 16), (120, 70, 36), (200, 150, 100)], lambda nx, ny: 2.0 - ny, lit=0)   # el plat
    cv.disc(613, y0 + 21, 9, 9, [(30, 14, 8), (80, 40, 20), (160, 100, 50), (240, 200, 140)], lambda nx, ny: 2.6 - ny, lit=0)   # la tassa
    cv.disc(613, y0 + 16, 7, 2.4, [(20, 10, 4), (60, 34, 14), (110, 70, 34)], lambda nx, ny: 1.2 + nx, lit=0)   # el cafè
    cv.ring(622, y0 + 21, 3, [(80, 40, 20), (160, 100, 50)], 1.2, lit=0, step=20)   # la nansa
    for k in range(3):                                                  # el fum dibuixat
        sx = 609 + k * 4
        for j in range(5):
            cv.flat(sx + round(math.sin(j * 1.2 + k) * 1), y0 + 11 - j, (250, 236, 210))
    text(cv, 'CAFÈ', x0 + 12, y0 + 48, [(250, 240, 220)], 0, lit=0, flat=(250, 240, 220))
    for j in range(3):
        for i in range(3):
            bx, by = x0 + 8 + i * 9, y0 + 61 + j * 8
            cv.rect(bx, by, bx + 5, by + 4, CHROME, lambda x, y, by=by: 3.6 + (0.8 if y == by else 0))
    obox(cv, x1 - 8, y0 + 60, x1 - 5, y0 + 70, SLATE, 1.6)              # la ranura de les monedes
    cv.vline(x1 - 7, y0 + 62, y0 + 68, [(10, 10, 12)], 0)
    cv.rect(x0 + 11, y0 + 93, x1 - 11, y0 + 109, SLATE, 0.6)            # on surt el got
    cv.hline(x0 + 11, x1 - 11, y0 + 109, CHROME, 3.0)
    cv.glow(613, 101, 40, (255, 160, 120), 0.2)
    # la taula alta (les ulleres hi van a sobre)
    cv.disc(600, 184, 29, 4.5, CHROME, lambda nx, ny: 4.6 - ny * 1.2)
    cv.rect(599, 188, 601, 227, CHROME, lambda x, y: 3.2 + (0.8 if x == 599 else 0))
    cv.disc(600, 228, 12, 2.7, CHROME, 2.4)
    cv.darken(587, 229, 616, 233, 0.55)
    # un got de cafè abandonat
    obox(cv, 621, 175, 628, 183, SHEET, 4.6)
    cv.hline(621, 628, 178, [(150, 40, 30)], 0)
    cv.hline(622, 627, 175, [(70, 40, 20)], 0)


def bg(cv, cig='sencera'):
    wall(cv)
    floor(cv)
    departures(cv)
    outside(cv)
    ortega(cv, cig)
    window_frame(cv)
    seats(cv)
    staff_door(cv)
    checkin(cv)
    lost_found(cv)
    cafe(cv)


_BASE = {}


def _base():
    if 'img' not in _BASE:
        cv = Canvas(light=LIGHT)
        bg(cv)
        _BASE['img'] = cv.img
    return _BASE['img']


# ─── Props ──────────────────────────────────────────────────────────────────

def _cig_state(cv, cig):
    """La cigarreta més curta: només el que canvia respecte del fons."""
    var = Canvas(light=LIGHT)
    bg(var, cig)
    cv.img.alpha_composite(_diff(var.img, _base()))


def cigarreta_mitja(cv):
    _cig_state(cv, 'mitja')


def cigarreta_curta(cv):
    _cig_state(cv, 'curta')


def maleti(cv):
    """El maletí de pell al prestatge d'objectes perduts, amb l'adhesiu «AGENDA 2019 — COMPTE, LLIMONA»."""
    obox(cv, 525, 120, 555, 140, WOODC, 2.6, top=0.8)
    cv.hline(526, 554, 126, WOODC, 1.8)                                 # la tapa
    cv.rect(536, 115, 544, 116, WOODC, 1.4)
    cv.vline(536, 115, 120, WOODC, 1.4)
    cv.vline(544, 115, 120, WOODC, 1.4)
    for sx in range(527, 554, 3):                                       # el pespunt
        cv.flat(sx, 138, (196, 150, 90))
    cv.rect(531, 124, 540, 129, YELS, 4.0)
    cv.hline(532, 539, 125, YELS, 4.6)
    cv.flat(533, 127, (40, 30, 6))
    cv.flat(537, 127, (40, 30, 6))
    for bx in (529, 551):
        cv.rect(bx, 121, bx + 1, 122, [(230, 200, 120)], 0)


def ulleres(cv):
    """Unes ulleres de pasta negra, damunt la taula alta de la cafeteria."""
    for gx in (591, 604):
        cv.ring(gx, 177, 4.5, [(8, 8, 10), (30, 30, 36)], 0.6, step=8)
        cv.disc(gx, 177, 3.2, 2.7, [(120, 150, 180), (190, 210, 230)], lambda nx, ny: 0.6 + (1 if nx < -0.2 and ny < 0 else 0))
    cv.hline(595, 600, 176, [(8, 8, 10)], 0)
    cv.line(586, 176, 583, 173, [(8, 8, 10)], 0)
    cv.line(609, 176, 612, 173, [(8, 8, 10)], 0)


PROPS = {'maleti': maleti, 'ulleres': ulleres, 'cigarreta_mitja': cigarreta_mitja, 'cigarreta_curta': cigarreta_curta}


# ─── L'empleat, darrere el taulell ─────────────────────────────────────────

FRONT = {'mask': lambda x, y: 440 <= x <= 571 and 144 <= y <= FLOOR_Y + 5, 'baseline': 213, 'zIndex': 20}


# ─── Animació: el fum de la cigarreta i el llum de l'avió ──────────────────

def _frames():
    base = _base()
    frames = []
    for i in range(10):
        cv = Canvas(light=LIGHT, img=base.copy())
        # el fum puja des de la mà de l'Ortega, i se'l mou el vent
        for k in range(6):
            t = (i + k * 5 / 3) % 10
            sx = CIG[0] + CIG_LEN['sencera'] - 3 + round(math.sin((t + k) * 0.9) * 2.7 + t * 0.45)
            sy = round(CIG[1] - 4 - t * 2.7)
            if sy > 40:
                w = 1 if t < 5 else 2
                cv.tint(sx, sy, sx + w, sy, (220, 220, 230), 0.45 - t * 0.04)
        # el llum anticol·lisió de la cua de l'avió
        cv.flat(*TAIL_LED, (255, 60, 60) if i % 5 == 0 else (90, 30, 40))
        if i % 5 == 0:
            cv.glow(*TAIL_LED, 5, (255, 60, 60), 0.6)
        frames.append(_diff(cv.img, base))
    return frames


def _frames_panell():
    """El llumet d'«embarcant» del BCMU-07, al panell de sortides: encès, apagat."""
    base = _base()
    x0, y0 = BOARD_BOX[:2]
    ax, ay = x0 + 58 + text_width('BCMU-07') + 4, y0 + 6
    cv = Canvas(light=LIGHT, img=base.copy())
    for k in range(4):                                                  # una fletxeta que apunta a GINEBRA
        cv.vline(ax + k, ay - k, ay + k, [(255, 220, 120)], 0, lit=0)
    cv.glow(ax + 1, ay, 7, (250, 180, 60), 0.3)
    return [_diff(cv.img, base), _diff(base, base)]


def _frames_cafe():
    """La màquina de cafè, esperant clients: els botons s'il·luminen d'un en un i després descansen."""
    base = _base()
    x0, y0 = CAFE[:2]
    frames = []
    for i in range(12):
        cv = Canvas(light=LIGHT, img=base.copy())
        if i < 9:
            bx, by = x0 + 8 + (i % 3) * 9, y0 + 61 + (i // 3) * 8
            cv.rect(bx, by, bx + 5, by + 4, [(150, 110, 80), (230, 190, 140), (255, 236, 200)], lambda x, y: 2.0 - (y - by) * 0.25, lit=0)
            cv.glow(bx + 3, by + 2, 7, (255, 190, 130), 0.25)
        frames.append(_diff(cv.img, base))
    return frames


ANIMS = {'terminal': {'frames': _frames, 'frameDuration': 160},
         'panell': {'frames': _frames_panell, 'frameDuration': 650},
         'cafe': {'frames': _frames_cafe, 'frameDuration': 260}}


# ─── Geometria a 640×360 (room_designs.AEROPORT_TERMINAL ×4/3) ─────────────

GEOMETRIA = {
    'things': {
        'taulell': {'rect': (40, 139, 206, 200), 'walk': (123, 248)},
        'vidriera': {'rect': (227, 35, 414, 150), 'walk': (320, 248)},
        'maleti': {'rect': (523, 112, 558, 142), 'walk': (507, 248)},
        'ulleres': {'rect': (581, 168, 616, 187), 'walk': (595, 248)},
    },
    'spawns': {'vet': (293, 261), 'soler': (59, 248), 'empleat': (501, 208), 'nen': (400, 259)},
    'walkable': [(19, 236), (621, 236), (632, 271), (8, 271)],
}
