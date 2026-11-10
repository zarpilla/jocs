"""
La terminal de l'aeroport (Escena 3, la Vet), dimarts de matinada. Art definitiu:
  - gris i blau fred: plafons de formigó, terra de rajola polida que reflecteix els fluorescents;
  - la vidriera gran: fora, l'alba (blau fosc que es torna rosa) sobre la pista i la cua d'un avió; a la zona
    de fumadors, la supervisora Ortega fuma i mira el mòbil (la cigarreta és el rellotge de la sincronia: es
    va escurçant amb els decorats `cigarreta_mitja` i `cigarreta_curta`);
  - el taulell de facturació (amb el pòsit de «8426» a sota), la porta de personal que vigila en Soler;
  - el panell de sortides amb el vol BCMU-07 a Ginebra;
  - objectes perduts: una garita amb un taulell (l'empleat hi és darrere) i prestatges plens (el maletí);
  - la cafeteria: una màquina de cafè que fa llum i una taula alta (les ulleres).
"""
import math

from PIL import Image

from hd.pix import Light, Canvas, W, H, hr
from hd.rooms.comu import obox, outline, cable, text, text_width, _diff, PLASTIC, SHEET, CARD, RED, YEL, GRAYC
from hd.rooms.bar_sala import STEELB, SLATE, BOTTLES
from hd.rooms.pis_cuina import outline_poly
from hd.characters import person, M
from hd.personatges import hair_cap

FLOOR_Y = 150

CONC = [(14, 18, 24), (26, 30, 38), (40, 46, 56), (56, 64, 76), (74, 84, 98), (94, 106, 122), (118, 130, 146), (144, 156, 170), (172, 182, 194)]
TILE = [(12, 16, 22), (22, 28, 36), (34, 42, 52), (48, 58, 70), (64, 76, 90), (84, 96, 112), (108, 120, 136), (136, 148, 162), (170, 180, 192)]
DAWN = [(10, 12, 34), (18, 22, 56), (34, 36, 80), (60, 54, 104), (100, 76, 120), (150, 100, 126), (200, 130, 120), (236, 170, 120), (252, 210, 150)]
TARMAC = [(8, 10, 16), (16, 18, 26), (26, 28, 38), (38, 40, 52)]
GLASS = [(10, 14, 22), (20, 28, 40), (34, 46, 62)]
DESK = [(16, 20, 28), (30, 36, 48), (48, 56, 72), (70, 80, 98), (96, 108, 126), (128, 140, 156), (166, 176, 188), (210, 216, 224)]
BLUE = [(4, 14, 40), (8, 30, 80), (16, 52, 124), (30, 80, 170), (60, 120, 210), (120, 170, 240)]
AMBER = [(40, 20, 0), (110, 60, 0), (200, 120, 10), (250, 180, 40)]
BOARD = [(4, 4, 6), (8, 8, 12), (14, 14, 20), (22, 22, 30)]
YELS = [(60, 40, 0), (130, 96, 6), (200, 156, 16), (240, 200, 40), (252, 230, 110)]
WOODC = [(30, 16, 8), (60, 34, 16), (96, 58, 28), (130, 86, 44), (164, 116, 64), (196, 150, 90)]
PLANT = [(4, 16, 8), (10, 34, 16), (20, 58, 28), (36, 86, 40), (60, 120, 60)]
CHROME = [(20, 24, 30), (50, 56, 66), (90, 98, 110), (140, 148, 160), (200, 206, 214), (240, 244, 248)]
VEND = [(30, 4, 6), (70, 10, 14), (120, 20, 22), (170, 34, 30), (210, 60, 46)]

LIGHT = Light(ambient=-0.1, vignette=(70, 30), floor_fade=(194, 30))
LIGHT.point(240, -30, r=300, k=2.2, squash=0.7, power=1.2)           # els fluorescents del sostre
LIGHT.point(455, 100, r=60, k=1.0, squash=1.0, power=2.0)            # la màquina de cafè
LIGHT.point(240, 112, r=90, k=0.7, squash=1.6, power=2.0)            # la claror de l'alba per la vidriera

# la cigarreta: de la mà de l'Ortega (x 287) cap a la dreta; llargada segons l'estat
CIG = (287, 67)
CIG_LEN = {'sencera': 10, 'mitja': 6, 'curta': 3}


# ─── Paret, sostre i terra ─────────────────────────────────────────────────

def wall(cv):
    """Plafons de formigó amb juntes, un fals sostre amb fluorescents i una franja blava d'aeroport."""
    for y in range(0, FLOOR_Y):
        for x in range(W):
            seam = (x % 60 == 0) or (y % 36 == 35 and y > 10)
            n = (hr(x // 2, y // 2, 3) - 0.5) * 0.4 + (hr(x // 60, y // 36, 6) - 0.5) * 0.4
            cv.put(x, y, CONC, (2.2 if seam else 4.0 + n))
    # el fals sostre
    for x in range(W):
        for y in range(0, 7):
            cv.put(x, y, CONC, 5.0 - y * 0.2 + (0.6 if x % 24 == 0 else 0))
    cv.hline(0, W - 1, 7, CONC, 1.4)
    for fx in range(20, W, 120):                                       # els fluorescents
        cv.rect(fx, 2, fx + 60, 4, [(230, 240, 250)], 0, lit=0)
        cv.glow(fx + 30, 4, 24, (220, 236, 255), 0.25)
    # la franja blava, a mitja alçada
    cv.rect(0, 92, W - 1, 95, BLUE, 2.6)
    cv.rect(0, FLOOR_Y - 5, W - 1, FLOOR_Y - 1, CONC, 2.4)             # sòcol
    cv.hline(0, W - 1, FLOOR_Y, CONC, 0.6)


def floor(cv):
    """Rajola polida, en perspectiva; brilla amb els reflexos de la vidriera i dels fluorescents."""
    for y in range(FLOOR_Y + 1, H):
        dep = (y - FLOOR_Y) / (H - FLOOR_Y)
        v = (y - FLOOR_Y) * 1.6 / (1 + dep * 0.5)
        for x in range(W):
            u = (x - W / 2) / (0.6 + dep * 0.8) + W / 2
            if (u % 36) < 0.9 or (v % 20) < 0.8:
                cv.put(x, y, TILE, 2.6)
                continue
            n = (hr(int(u // 36), int(v // 20), 2) - 0.5) * 0.4
            cv.put(x, y, TILE, 4.0 + n + (hr(x, y, 9) - 0.5) * 0.3)
    # el reflex de l'alba de la vidriera, a terra
    cv.tint(170, 152, 310, 200, (200, 140, 150), lambda x, y: 0.22 * max(0, 1 - (y - 152) / 48) * (0.6 + 0.4 * math.sin(x / 7) ** 2))
    cv.tint(0, 152, W - 1, 168, (220, 236, 255), lambda x, y: 0.06 * max(0, 1 - (y - 152) / 16))


# ─── La vidriera ───────────────────────────────────────────────────────────

def outside(cv):
    """L'alba sobre la pista: cel, la línia d'arbres llunyana, un avió aparcat i la zona de fumadors."""
    x0, y0, x1, y1 = 172, 28, 308, 110
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, DAWN, 0.6 + (y - y0) / 9.0, lit=0)
    # un núvol prim, rosat
    for x in range(x0, x1):
        yy = 46 + int(2 * math.sin(x / 11))
        if hr(x // 5, 3) > 0.3:
            cv.put(x, yy, DAWN, 6.2, lit=0)
    # l'horitzó: arbres i les llums de la pista
    for x in range(x0, x1 + 1):
        top = 78 - int(2 * hr(x // 4, 1) + 1.5 * math.sin(x / 13))
        for y in range(top, 84):
            cv.put(x, y, TARMAC, 1.0, lit=0)
    for y in range(84, y1 + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, TARMAC, 1.6 + (y - 84) / 14, lit=0)
    for lx in range(176, 308, 9):
        cv.flat(lx, 84, (120, 200, 255) if lx % 2 else (250, 200, 90))
    # l'avió aparcat: la cua i el fuselatge, a l'esquerra
    tail = [(184, 56), (194, 56), (206, 76), (206, 82), (178, 82)]
    cv.poly(tail, CONC, 4.6, lit=0)
    cv.poly([(186, 58), (193, 58), (200, 70), (190, 70)], BLUE, 3.0, lit=0)
    cv.rect(176, 76, 240, 86, CONC, lambda x, y: 5.4 - (y - 76) * 0.25, lit=0)
    for wx in range(208, 238, 4):
        cv.flat(wx, 79, (30, 40, 60))
    cv.flat(186, 57, (255, 60, 60))
    # la zona de fumadors: una paperera-cendrer i el paviment
    cv.rect(x0, 96, x1, y1, CONC, lambda x, y: 2.8 + (0.6 if (x + y) % 9 == 0 else 0), lit=0)
    obox(cv, 298, 82, 304, 100, STEELB, 3.0, lit=0)
    cv.rect(297, 81, 305, 82, STEELB, 4.6, lit=0)


ORTEGA = {'skin': M((56, 30, 34), (104, 62, 56), (152, 100, 80), (194, 138, 106), (222, 172, 136), (240, 204, 172)),
          'legs': M((8, 8, 14), (18, 18, 28), (30, 30, 44), (44, 44, 60), (62, 62, 80)),
          'top': M((20, 6, 12), (44, 12, 22), (72, 20, 34), (104, 32, 46), (136, 48, 58), (168, 72, 76), dith=0.0),
          'shoes': M((6, 6, 8), (14, 14, 18), (26, 26, 32), (44, 44, 52)), 'thin': 1,
          'hooks': {'hair': hair_cap(M((10, 10, 12), (24, 22, 26), (40, 38, 42), (60, 58, 62), (86, 84, 88)), fringe=0.5)}}


def ortega(cv, cig='sencera'):
    """La supervisora Ortega, darrere el vidre: uniforme granat, gafet, el mòbil en una mà i la cigarreta a l'altra."""
    fig = person(ORTEGA, 'D')
    k = 0.78
    fig = fig.resize((round(fig.width * k), round(fig.height * k)), Image.NEAREST)
    ox, oy = 259, 28
    cv.img.alpha_composite(fig, (ox, oy))
    # el monyo i el mocador de coll
    cv.disc(278, oy + 4, 3, 2.4, [(10, 10, 12), (30, 28, 32), (56, 54, 58)], lambda nx, ny: 1.8 - ny, lit=0)
    cv.rect(275, oy + 20, 282, oy + 21, YELS, 3.0, lit=0)
    cv.flat(281, oy + 27, (230, 230, 240))                              # el gafet
    cv.flat(281, oy + 28, (90, 140, 200))
    # el mòbil, a la mà esquerra (la pantalla li il·lumina la cara des de baix)
    cv.rect(268, 64, 270, 68, [(20, 20, 26)], 0, lit=0)
    cv.flat(269, 65, (170, 220, 255))
    cv.glow(272, 46, 8, (150, 200, 255), 0.18)
    # la cigarreta
    n = CIG_LEN[cig]
    cx, cy = CIG
    cv.hline(cx, cx + n - 1, cy, [(236, 232, 222)], 0, lit=0)
    cv.flat(cx, cy, (210, 150, 80))                                     # el filtre
    cv.flat(cx + n, cy, (255, 110, 40))                                 # la brasa
    cv.glow(cx + n, cy, 3, (255, 120, 40), 0.5)


def window_frame(cv):
    """El marc d'alumini, el muntant del mig i el reflex dels fluorescents al vidre."""
    x0, y0, x1, y1 = 170, 26, 310, 112
    cv.tint(x0, y0, x1, y1, (150, 180, 220), lambda x, y: 0.10 if (x - y) % 40 < 6 else 0.04)
    for (a, b, c, d) in ((x0, y0, x1, y0 + 2), (x0, y1 - 2, x1, y1), (x0, y0, x0 + 2, y1), (x1 - 2, y0, x1, y1), (239, y0, 241, y1)):
        cv.rect(a, b, c, d, CHROME, 3.0)
    outline(cv, x0 - 1, y0 - 1, x1 + 1, y1 + 1, CONC)


def seats(cv):
    """Una fila de seients d'espera, sota la vidriera."""
    for i in range(5):
        sx = 182 + i * 24
        back = [(sx, 116), (sx + 20, 116), (sx + 20, 132), (sx, 132)]
        cv.poly(back, BLUE, lambda x, y: 2.4 + (0.8 if y < 119 else 0))
        outline_poly(cv, back, BLUE)
        seat = [(sx - 1, 132), (sx + 21, 132), (sx + 22, 138), (sx - 2, 138)]
        cv.poly(seat, BLUE, lambda x, y: 3.2 - (y - 132) * 0.2)
        outline_poly(cv, seat, BLUE)
    cv.rect(180, 139, 300, 141, CHROME, 3.0)
    for lx in (186, 240, 294):
        cv.rect(lx, 141, lx + 1, 152, CHROME, 2.6)
    cv.darken(178, 152, 302, 156, 0.5)
    # algú s'ha deixat un diari
    cv.poly([(232, 130), (246, 129), (247, 133), (231, 134)], SHEET, 4.2)


# ─── El panell de sortides i la facturació ─────────────────────────────────

def departures(cv):
    """El panell de sortides: el BCMU-07 a Ginebra, a les 6:10."""
    x0, y0, x1, y1 = 36, 12, 146, 38
    cv.vline(60, 7, y0, STEELB, 2.4)
    cv.vline(122, 7, y0, STEELB, 2.4)
    obox(cv, x0, y0, x1, y1, BOARD, 1.4)
    rows = (('GINEBRA', 'BCMU-07', '06:10'), ('PARÍS', 'VY 8000', '06:45'), ('PALMA', 'IB 1234', '07:05'))
    for j, (dest, fl, hh) in enumerate(rows):
        yy = y0 + 3 + j * 9
        col = (250, 190, 50) if j else (255, 220, 120)
        text(cv, dest, x0 + 3, yy, AMBER, 0, lit=0, flat=col)
        text(cv, fl, x0 + 44, yy, AMBER, 0, lit=0, flat=col)
        text(cv, hh, x1 - 3 - text_width(hh), yy, AMBER, 0, lit=0, flat=col)
    cv.glow((x0 + x1) // 2, y0 + 12, 40, (250, 180, 60), 0.08)


def staff_door(cv):
    """La porta de personal: metàl·lica, grisa, amb «NOMÉS PERSONAL»; l'agent Soler la vigila."""
    x0, y0, x1, y1 = 8, 40, 26, FLOOR_Y
    obox(cv, x0 - 2, y0 - 2, x1 + 2, y1, CHROME, 2.4)
    obox(cv, x0, y0, x1, y1, DESK, 3.4, top=0.6)
    cv.rect(x0 + 3, y0 + 4, x1 - 3, y0 + 18, GLASS, 1.6)                  # finestreta
    cv.rect(x1 - 5, 96, x1 - 3, 98, CHROME, 4.4)                         # la maneta
    cv.rect(x0, 128, x1, 131, CHROME, 3.6)                               # la barra antipànic
    # el senyal de prohibit el pas
    cv.disc(17, 66, 6, 6, RED, lambda nx, ny: 3.6 - ny * 0.6)
    cv.rect(13, 65, 21, 67, [(250, 244, 236)], 0)


def checkin(cv):
    """El taulell de facturació: frontal de laminat blau amb el logotip, la cinta de les maletes i els monitors."""
    x0, x1 = 30, 154
    top = 104
    # els monitors i el cartell «FACTURACIÓ», al darrere
    for mx in (50, 108):
        obox(cv, mx, 84, mx + 22, 100, PLASTIC, 1.8)
        cv.rect(mx + 2, 86, mx + 20, 97, BLUE, 2.0, lit=0)
        cv.rect(mx + 10, 100, mx + 12, top, PLASTIC, 2.4)
    obox(cv, 66, 46, 118, 58, BLUE, 3.0)
    w = text_width('FACTURACIÓ')
    text(cv, 'FACTURACIÓ', 92 - w // 2, 50, [(240, 244, 250)], 0, flat=(240, 244, 250))
    cv.vline(80, 39, 46, STEELB, 2.4)
    cv.vline(104, 39, 46, STEELB, 2.4)
    # el taulell
    cv.rect(x0 - 4, top, x1 + 4, top + 4, DESK, lambda x, y: 6.0 - (y - top) * 0.5)
    cv.hline(x0 - 4, x1 + 4, top + 5, DESK, 0.6)
    for y in range(top + 6, FLOOR_Y + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, BLUE, 2.4 + (0.6 if (x - x0) % 31 == 0 else 0) - (y - top) * 0.02)
    outline(cv, x0, top + 6, x1, FLOOR_Y, BLUE)
    # el logotip de la companyia: un avió estilitzat
    cv.poly([(84, 122), (100, 116), (104, 118), (92, 124), (100, 130), (96, 131), (84, 126)], [(240, 244, 250)], 0, lit=0)
    # la báscula de les maletes, a l'esquerra
    obox(cv, 6, 132, 30, FLOOR_Y + 2, CHROME, 2.6)
    cv.rect(10, 134, 26, 136, SLATE, 1.6)
    # el pòsit groc, enganxat sota el cantell del taulell (es veu de reüll)
    cv.rect(132, top + 6, 137, top + 9, YELS, 3.6)
    cv.darken(x0, FLOOR_Y + 1, x1 + 6, FLOOR_Y + 4, 0.5)
    # el pal de la cua amb la cinta
    for px in (162,):
        cv.rect(px, 124, px + 1, 156, CHROME, 3.6)
        cv.disc(px, 157, 4, 1.4, CHROME, 2.6)
        cv.rect(px - 18, 128, px, 129, BLUE, 3.4)


# ─── Objectes perduts ──────────────────────────────────────────────────────

def lost_found(cv):
    """La garita d'objectes perduts: el rètol groc, prestatges plens de coses i el taulell (l'empleat hi és darrere)."""
    x0, y0, x1 = 330, 58, 426
    # el rètol
    obox(cv, x0, y0, x1, 70, YELS, 3.2)
    w = text_width('OBJECTES PERDUTS')
    text(cv, 'OBJECTES PERDUTS', (x0 + x1 - w) // 2, 61, [(20, 14, 4)], 0, flat=(30, 22, 6))
    # l'interior: paret del fons més fosca
    cv.rect(x0 + 2, 71, x1 - 2, 112, CONC, 2.6)
    # prestatges
    for y in (86, 106):
        cv.rect(x0 + 2, y, x1 - 2, y + 1, WOODC, 3.0)
    # prestatge de dalt: paraigües, un osset, una gorra, un casc
    for i in range(4):
        ux = 336 + i * 5
        cv.line(ux, 85, ux + 2, 72, [(10, 10, 16), (30, 30, 44), (60, 60, 90)] if i % 2 else VEND, 1.4)
        cv.flat(ux + 2, 72, (180, 180, 180))
    cv.disc(366, 80, 5, 5, CARD, lambda nx, ny: 3.6 - nx - ny)          # l'osset
    cv.disc(363, 75, 2, 2, CARD, 3.4)
    cv.disc(369, 75, 2, 2, CARD, 3.4)
    cv.flat(365, 79, (20, 10, 6))
    cv.flat(368, 79, (20, 10, 6))
    cv.disc(388, 82, 6, 4, RED, lambda nx, ny: 3.4 - ny)                 # una gorra
    cv.rect(392, 84, 398, 85, RED, 2.0)
    cv.disc(412, 80, 7, 6, [(10, 10, 14), (30, 30, 40), (70, 70, 90), (140, 140, 170)], lambda nx, ny: 2.0 + (1.6 if nx < -0.3 and ny < -0.2 else 0))  # un casc de moto
    # prestatge de baix: una maleta, un ukelele, una bossa (el maletí, quan hi és, va a la dreta)
    obox(cv, 336, 90, 358, 106, BLUE, 2.4)
    cv.rect(344, 87, 350, 89, SLATE, 2.0)
    cv.disc(368, 100, 5, 5, WOODC, 3.6)
    cv.rect(368, 88, 370, 96, WOODC, 2.4)
    cv.disc(368, 100, 1.4, 1.4, SLATE, 0.8)
    cv.poly([(376, 106), (390, 106), (388, 94), (378, 94)], [(30, 50, 30), (50, 90, 50), (80, 130, 70)], 1.6)
    # els laterals de la garita
    for sx in (x0, x1 - 2):
        cv.rect(sx, 70, sx + 2, FLOOR_Y, CHROME, 3.0)
    lost_counter(cv)


def lost_counter(cv):
    """El taulell de la garita (per davant de l'empleat)."""
    x0, x1 = 330, 426
    top = 112
    cv.rect(x0, top, x1, top + 3, DESK, lambda x, y: 6.0 - (y - top) * 0.6)
    cv.hline(x0, x1, top + 4, DESK, 0.6)
    for y in range(top + 5, FLOOR_Y + 1):
        for x in range(x0 + 2, x1 - 1):
            cv.put(x, y, YELS, 1.8 + (0.5 if (x - x0) % 24 == 0 else 0))
    outline(cv, x0, top + 5, x1, FLOOR_Y, YELS)
    # un timbre i un formulari
    cv.disc(344, top - 1, 3, 1.6, CHROME, lambda nx, ny: 4.4 - ny)
    cv.flat(344, top - 3, (220, 220, 220))
    cv.poly([(400, top - 2), (414, top - 2), (416, top + 1), (398, top + 1)], SHEET, 4.6)
    cv.darken(x0, FLOOR_Y + 1, x1 + 2, FLOOR_Y + 4, 0.5)


# ─── La cafeteria ──────────────────────────────────────────────────────────

def cafe(cv):
    """La màquina de cafè (vermella i lluminosa), una planta de plàstic i la taula alta."""
    # la planta, al racó entre la garita i la cafeteria
    obox(cv, 428, 132, 438, FLOOR_Y + 2, CONC, 3.4)
    for i in range(7):
        a = -1.2 + i * 0.4
        cv.line(433, 132, 433 + round(math.sin(a) * 9), 132 - round(math.cos(a) * 14), PLANT, 2.6 + (i % 2))
    # la màquina
    x0, y0, x1, y1 = 444, 52, 476, FLOOR_Y
    obox(cv, x0, y0, x1, y1, VEND, 2.6)
    cv.rect(x0 + 3, y0 + 4, x1 - 3, y0 + 30, [(60, 30, 20), (140, 80, 40), (220, 150, 80), (250, 210, 150)], lambda x, y: 1.4 + (y - y0) / 14, lit=0)
    cv.disc(460, y0 + 17, 7, 7, [(30, 14, 8), (80, 40, 20), (160, 100, 50), (240, 200, 140)], lambda nx, ny: 2.6 - ny, lit=0)   # la tassa
    text(cv, 'CAFÈ', x0 + 9, y0 + 36, [(250, 240, 220)], 0, lit=0, flat=(250, 240, 220))
    for j in range(3):
        for i in range(3):
            cv.rect(x0 + 6 + i * 7, y0 + 46 + j * 6, x0 + 10 + i * 7, y0 + 49 + j * 6, CHROME, 3.6)
    cv.rect(x0 + 8, y0 + 70, x1 - 8, y0 + 82, SLATE, 0.6)               # on surt el got
    cv.glow(460, 76, 30, (255, 160, 120), 0.2)
    # la taula alta (les ulleres hi van a sobre)
    cv.disc(450, 138, 22, 3.4, CHROME, lambda nx, ny: 4.6 - ny * 1.2)
    cv.rect(449, 141, 451, 170, CHROME, 3.2)
    cv.disc(450, 171, 9, 2, CHROME, 2.4)
    cv.darken(440, 172, 462, 175, 0.55)
    # un got de cafè abandonat
    obox(cv, 466, 131, 471, 137, SHEET, 4.6)


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


# ─── Props ──────────────────────────────────────────────────────────────────

def _cig_state(cv, cig):
    """La cigarreta més curta: només el que canvia respecte del fons."""
    base = Canvas(light=LIGHT)
    bg(base)
    var = Canvas(light=LIGHT)
    bg(var, cig)
    cv.img.alpha_composite(_diff(var.img, base.img))


def cigarreta_mitja(cv):
    _cig_state(cv, 'mitja')


def cigarreta_curta(cv):
    _cig_state(cv, 'curta')


def maleti(cv):
    """El maletí de pell al prestatge d'objectes perduts, amb l'adhesiu «AGENDA 2019 — COMPTE, LLIMONA»."""
    obox(cv, 394, 90, 416, 105, WOODC, 2.6, top=0.8)
    cv.rect(402, 86, 408, 87, WOODC, 1.4)
    cv.vline(402, 86, 90, WOODC, 1.4)
    cv.vline(408, 86, 90, WOODC, 1.4)
    cv.rect(398, 93, 405, 97, YELS, 4.0)
    cv.flat(400, 95, (40, 30, 6))
    cv.flat(403, 95, (40, 30, 6))
    for bx in (397, 413):
        cv.flat(bx, 91, (230, 200, 120))


def ulleres(cv):
    """Unes ulleres de pasta negra, damunt la taula alta de la cafeteria."""
    for gx in (443, 453):
        cv.ring(gx, 133, 3.4, [(8, 8, 10), (30, 30, 36)], 0.6, step=12)
        cv.disc(gx, 133, 2.4, 2, [(120, 150, 180), (190, 210, 230)], lambda nx, ny: 0.6 + (1 if nx < -0.2 and ny < 0 else 0))
    cv.hline(446, 450, 132, [(8, 8, 10)], 0)
    cv.line(439, 132, 437, 130, [(8, 8, 10)], 0)
    cv.line(457, 132, 459, 130, [(8, 8, 10)], 0)


PROPS = {'maleti': maleti, 'ulleres': ulleres, 'cigarreta_mitja': cigarreta_mitja, 'cigarreta_curta': cigarreta_curta}


# ─── L'empleat, darrere el taulell ─────────────────────────────────────────

FRONT = {'mask': lambda x, y: 330 <= x <= 428 and 108 <= y <= FLOOR_Y + 4, 'baseline': 160, 'zIndex': 20}


# ─── Animació: el fum de la cigarreta i el llum de l'avió ──────────────────

def _frames():
    base = Canvas(light=LIGHT)
    bg(base)
    frames = []
    for i in range(10):
        cv = Canvas(light=LIGHT, img=base.img.copy())
        # el fum puja des de la mà de l'Ortega, i se'l mou el vent
        for k in range(5):
            t = (i + k * 2) % 10
            sx = CIG[0] + 6 + round(math.sin((t + k) * 0.9) * 2) + t // 3
            sy = CIG[1] - 3 - t * 2
            if sy > 30:
                cv.tint(sx, sy, sx + 1, sy, (220, 220, 230), 0.45 - t * 0.04)
        # el llum anticol·lisió de la cua de l'avió
        cv.flat(186, 57, (255, 60, 60) if i % 5 == 0 else (90, 30, 40))
        if i % 5 == 0:
            cv.glow(186, 57, 4, (255, 60, 60), 0.6)
        frames.append(_diff(cv.img, base.img))
    return frames


ANIMS = {'terminal': {'frames': _frames, 'frameDuration': 160}}
