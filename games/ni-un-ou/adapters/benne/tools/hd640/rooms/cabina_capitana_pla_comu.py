"""
**El dibuix pla de sempre** (font de les textures de la sala en 3D, cabina_capitana.py).

Prova de resolució: la cabina de la Capitana a 640×360 (la composició de hd/rooms/cabina_capitana.py ×4/3,
dibuixada de nou amb el detall que hi cap). Mateixes rampes, props i animacions.

  - la porta estanca del passadís a l'esquerra (oberta, fulla de teca), amb la gorra i l'anorac penjats al costat;
  - l'ull de bou, el rellotge i el baròmetre de llautó;
  - l'escriptori de teca amb el contracte de Blau Net (`contracte`), la novel·la romàntica (`novella`), el flexo,
    una tassa i una foto; a sobre, el prestatge amb barana amb els llibres de navegació i el model de l'Arenga;
  - la carta nàutica (`carta`), amb Galway i Port Hallen encerclats (Port Hallen, en vermell i més fort);
  - la llitera de teca amb la manta blava, sota la carta; una catifa al linòleum.
ANIMS: `mar` (l'ull de bou de nit), `ulls_dia_mar` (el mateix de dia, damunt del decorat `ulls_dia`) i `rellotge`.
"""
import math

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from hd.pix import Canvas, Light, W, H, hr, mix  # noqa: F401
from hd.rooms.arenga import box, rrect, bolt, hpipe, glow, CAB, DARK, WHITEP, REDP, YELL, BRASS
from hd.rooms.comu import _diff, text, text_width
from hd.rooms.principal import (CREAM, TEAK, LINO, DOORP, NIGHT, DAYSKY, DAYSEA, sill, porthole as _porthole,
                                day_porthole, second_hand, foot_shadow, floor_shadow)
from hd.rooms.laboratori import PAPERC, BLUEB
from hd640.rooms.laboratori_pla_comu import wall, ceiling, lamp, lamp_glow, lino, shine, door_frame

from hd.pix import Canvas  # noqa: E402,F811  (a 1×: és la font de les textures de la sala en 3D)
Canvas1x = Canvas

CEIL_H = 24
FLOOR_Y = 203
BOTTOM = 260                      # per sota hi ha la barra de verbs
LAMPS = ((171, 27), (496, 27))
WAINSCOT_Y = 147
FLEXO = (389, 149)                # el peu del flexo

LIGHT = Light(ambient=0.3, vignette=(80, 35), floor_fade=None)
LIGHT.point(171, 35, r=200, k=2.0, squash=1.05, down=True, power=1.5)
LIGHT.point(496, 35, r=200, k=2.0, squash=1.05, down=True, power=1.5)
LIGHT.point(376, 128, r=120, k=1.6, power=1.6)                   # el flexo de l'escriptori

NAVY = [(6, 8, 16), (10, 14, 28), (16, 22, 44), (24, 32, 62), (36, 46, 84), (52, 64, 108), (76, 90, 136)]
SHADE = [(8, 24, 14), (14, 44, 26), (22, 70, 40), (36, 100, 58), (56, 132, 80)]
PINK = [(60, 10, 30), (120, 30, 60), (180, 60, 100), (220, 110, 140), (246, 170, 190)]
GREENB = [(20, 40, 30), (40, 80, 56), (70, 120, 84), (110, 160, 120)]
YELLOWJ = YELL
INK = (34, 30, 26)


# ─── Paret, folre i porta ───────────────────────────────────────────────────

def wainscot(cv):
    """Folre de teca a la part de baix de la paret, de plafons (la cabina del capità sempre en té)."""
    for y in range(WAINSCOT_Y, FLOOR_Y):
        for x in range(W):
            grain = math.sin(x * 0.7 + math.sin(y * 0.11 + x * 0.04) * 3) * 0.25
            lv = 3.6 + grain + (hr(x // 40, 3) - 0.5) * 0.4
            if x % 40 == 0:
                lv = 2.0
            elif x % 40 == 1:
                lv = 4.6
            cv.put(x, y, TEAK, lv)
    # els plafons: una motllura a cada tauló
    for px in range(0, W, 40):
        for y in range(WAINSCOT_Y + 8, FLOOR_Y - 13):
            cv.put(px + 6, y, TEAK, 2.4)
            cv.put(px + 34, y, TEAK, 4.4)
        cv.hline(px + 6, px + 34, WAINSCOT_Y + 8, TEAK, 2.4)
        cv.hline(px + 6, px + 34, FLOOR_Y - 13, TEAK, 4.4)
    box(cv, 0, WAINSCOT_Y - 4, W - 1, WAINSCOT_Y, TEAK, 4.8)
    cv.hline(0, W - 1, WAINSCOT_Y - 3, TEAK, 5.8)
    cv.hline(0, W - 1, WAINSCOT_Y + 1, TEAK, 1.6)
    box(cv, 0, FLOOR_Y - 8, W - 1, FLOOR_Y - 1, TEAK, 3.0)
    cv.hline(0, W - 1, FLOOR_Y - 8, TEAK, 4.2)


def watertight_door(cv, x0=19, y0=88, x1=75, y1=FLOOR_Y, leaf_ramp=TEAK, leaf_lvl=4.0):
    """La porta del passadís, oberta: el passadís de crema i linòleum vermell al fons, i la fulla de teca."""
    cx = (x0 + x1) // 2
    for y in range(y0, y1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, CREAM, 3.4 - abs(x - cx) / 32 - (y - y0) / 120, lit=0.25)
    # l'altra banda del passadís: una porta tancada (la del laboratori) i el passamans
    rrect(cv, cx - 9, y0 + 30, cx + 9, y1 - 22, 4, DOORP, 2.0)
    cv.vline(cx + 5, y0 + 60, y0 + 66, BRASS, 2.6, lit=0.25)
    hpipe(cv, x0, x1, y1 - 46, 1, TEAK, 2.6)
    cv.rect(x0, y1 - 24, x1, y1 - 16, TEAK, 2.6, lit=0.25)
    cv.rect(x0, y1 - 15, x1, y1 - 1, LINO, lambda x, y: 2.6 + (y - y1 + 15) * 0.09, lit=0.2)
    for x in range(x0, x1 + 1, 6):
        cv.line(x, y1 - 1, cx + (x - cx) * 0.4, y1 - 14, LINO, 2.0, lit=0.2)
    cv.disc(cx, y0 + 13, 5, 2, [(120, 100, 60), (220, 190, 130), (250, 230, 190)], 1.6, lit=0)
    glow(cv, cx, y0 + 15, 18, (230, 200, 140), 0.35)
    door_frame(cv, x0, y0, x1, y1)
    sill(cv, x0, x1, y1, h=7)
    for x in range(x0 + 4, x1 - 2, 9):
        cv.put(x, y1 - 4, DOORP, 4.6)
    # la fulla, oberta contra la paret (de cantó), de teca
    lx = x0 - 15
    cv.poly([(lx, y0 + 5), (x0 - 4, y0 - 1), (x0 - 4, y1 - 3), (lx, y1 - 5)], leaf_ramp,
            lambda x, y: leaf_lvl - (x - lx) * 0.05)
    cv.vline(lx, y0 + 5, y1 - 5, leaf_ramp, leaf_lvl - 1.6)
    cv.vline(x0 - 4, y0, y1 - 3, leaf_ramp, leaf_lvl + 1.0)
    for y in range(y0 + 8, y1 - 8, 5):                                 # la veta, de cantó
        cv.put(lx + 4 + (y // 5) % 4, y, leaf_ramp, leaf_lvl - 0.8)
    box(cv, lx + 3, (y0 + y1) // 2, lx + 7, (y0 + y1) // 2 + 8, BRASS, 3.2)   # la maneta
    for dy in (y0 + 18, y1 - 24):
        box(cv, lx + 2, dy, lx + 6, dy + 3, BRASS, 3.0)                  # les frontisses
    # el rètol verd de SORTIDA
    teal = [(6, 22, 16), (10, 38, 28), (16, 58, 42), (26, 82, 58), (40, 108, 76), (62, 138, 98)]
    w = text_width('SORTIDA') + 8
    box(cv, cx - w // 2, y0 - 22, cx + w // 2, y0 - 13, teal, 3.4)
    text(cv, 'SORTIDA', cx - w // 2 + 4, y0 - 20, None, 0, flat=(230, 250, 236))
    glow(cv, cx, y0 - 17, 22, (80, 220, 140), 0.15)


def cap_hook(cv):
    """La gorra de capitana (blanca, visera negra i ancoreta daurada) i l'anorac groc de mar, penjats."""
    for hy in (93, 123):
        box(cv, 91, hy, 96, hy + 4, BRASS, 3.6)
        cv.put(95, hy + 5, BRASS, 4.8)
    # la gorra: copa blanca, cinta blau marí, visera negra i l'àncora
    cv.disc(93, 104, 11, 5, WHITEP, lambda nx, ny: 4.6 - nx * 0.6 - ny * 0.8)
    cv.hline(84, 102, 100, WHITEP, 5.4)
    cv.rect(83, 105, 104, 109, NAVY, 1.4)
    cv.hline(83, 104, 105, NAVY, 2.6)
    cv.poly([(84, 110), (103, 110), (107, 114), (80, 114)], DARK, lambda x, y: 2.4 + (y - 110) * 0.2)
    cv.hline(81, 106, 114, DARK, 0.6)
    ax, ay = 93, 106                                                     # l'ancoreta daurada
    cv.vline(ax, ay - 1, ay + 2, YELL, 5.0)
    cv.hline(ax - 1, ax + 1, ay - 1, YELL, 5.0)
    cv.put(ax - 1, ay + 2, YELL, 4.0)
    cv.put(ax + 1, ay + 2, YELL, 4.0)
    for x in range(86, 101, 3):                                          # el cordó daurat
        cv.put(x, 108, YELL, 4.2)
    # l'anorac groc, amb la cremallera, la caputxa i les bandes reflectants
    cv.poly([(88, 128), (99, 128), (107, 139), (107, 184), (83, 184), (83, 139)], YELL,
            lambda x, y: 3.6 - (x - 83) * 0.04 + (0.5 if (x * 3 + y) % 13 == 0 else 0))
    cv.poly([(89, 128), (98, 128), (96, 134), (91, 134)], YELL, 2.4)     # la caputxa plegada
    cv.vline(95, 131, 184, CAB, 2.4)
    for y in range(133, 184, 3):
        cv.put(96, y, CAB, 4.0)
    cv.line(85, 139, 81, 176, YELL, 2.4)
    cv.line(105, 141, 108, 172, YELL, 2.8)
    for y in (165, 174):
        cv.hline(83, 107, y, [(120, 120, 110), (220, 220, 200), (250, 250, 240)], 1.8)
        cv.hline(83, 107, y + 1, [(120, 120, 110), (220, 220, 200), (250, 250, 240)], 1.0)
    box(cv, 99, 147, 105, 153, YELL, 3.0)                                # la butxaca
    floor_shadow(cv, 95, FLOOR_Y + 4, 14, 2, 0.3)


def clock_barometer(cv):
    """Rellotge i baròmetre de llautó, aparellats en una post de teca."""
    box(cv, 173, 53, 237, 83, TEAK, 4.0)
    cv.hline(174, 236, 54, TEAK, 5.2)
    for bx in (176, 234):
        cv.put(bx, 56, BRASS, 5.0)
        cv.put(bx, 80, BRASS, 5.0)
    for cx in (191, 220):
        cv.disc(cx, 68, 12, 12, BRASS, lambda nx, ny: 3.8 - nx * 1.2 - ny * 1.2)
        cv.disc(cx, 68, 9, 9, WHITEP, lambda nx, ny: 4.8 - ny * 0.3)
        for a in range(0, 360, 30):
            d = 8 if a % 90 else 7
            cv.put(cx + round(math.cos(math.radians(a)) * d), 68 + round(math.sin(math.radians(a)) * d), CAB, 1.4)
    cv.line(191, 68, 191, 62, CAB, 0.6)                              # les quatre menys deu
    cv.line(191, 68, 196, 68, CAB, 0.6)
    # el baròmetre: escala vermella de mal temps a l'esquerra, l'agulla baixant
    for a in range(150, 211, 6):
        cv.put(220 + round(math.cos(math.radians(a)) * 7), 68 + round(math.sin(math.radians(a)) * 7), REDP, 4.0)
    text(cv, 'MB', 216, 71, None, 0, flat=(60, 50, 40))
    cv.line(220, 68, 215, 62, REDP, 3.0)
    cv.line(220, 68, 224, 71, CAB, 1.0)
    cv.put(220, 68, BRASS, 5.0)


def bookshelf(cv):
    """Prestatge amb barana sobre l'escriptori: derroters, l'almanac, carpetes i un model de l'Arenga."""
    x0, x1, y = 248, 400, 93
    box(cv, x0, y, x1, y + 4, TEAK, 4.6)
    cv.hline(x0, x1, y, TEAK, 5.6)
    for bx in (x0 + 8, x1 - 8):
        cv.poly([(bx - 1, y + 5), (bx + 2, y + 5), (bx + 2, y + 16), (bx - 1, y + 8)], CAB, 3.2)
    cols = [NAVY, REDP, TEAK, GREENB, NAVY, PAPERC]
    x = x0 + 4
    i = 0
    while x < 338:
        w = 4 + int(hr(i, 81) * 4)
        h = 16 + int(hr(i, 82) * 8)
        c = cols[int(hr(i, 83) * len(cols))]
        lean = i == 9
        for xx in range(x, x + w):
            for yy in range(y - h, y):
                cv.put(xx + (1 if lean and yy < y - h // 2 else 0), yy, c, 3.0 - (xx - x) * 0.25 + (0.8 if xx == x else 0))
        if h > 19:
            cv.hline(x, x + w - 1, y - h + 5, BRASS, 4.0)                   # les lletres daurades del llom
            cv.hline(x + 1, x + w - 2, y - h + 8, BRASS, 3.2)
        cv.hline(x, x + w - 1, y - h, c, 4.2)
        x += w + 1
        i += 1
    # el model de l'Arenga: casc blanc, línia vermella, el pont amb finestres i el pal, en una base de fusta
    box(cv, 346, 88, 394, 92, TEAK, 3.6)
    cv.poly([(349, 80), (395, 80), (390, 87), (355, 87)], WHITEP, lambda x, y: 4.6 - (y - 80) * 0.12)
    cv.hline(352, 392, 83, REDP, 4.2)
    cv.hline(352, 391, 84, REDP, 3.0)
    box(cv, 365, 70, 381, 79, WHITEP, 4.6)
    for wx in range(367, 380, 3):
        cv.put(wx, 73, NAVY, 2.4)
    cv.vline(376, 57, 69, CAB, 3.0)
    cv.hline(373, 379, 61, CAB, 3.0)
    cv.rect(356, 76, 362, 79, (YELL), 4.0)                                # la grua
    cv.hline(x0, x1, y - 9, BRASS, 3.6)                                   # la barana
    cv.hline(x0, x1, y - 8, BRASS, 2.2)
    for bx in range(x0 + 2, x1, 25):
        cv.vline(bx, y - 9, y - 1, BRASS, 3.0)


DESK = (229, 144, 416, 211)     # x0, y del sobre (darrere), x1, y dels peus


def desk(cv):
    x0, ytop, x1, ybot = DESK
    # el sobre, una mica en perspectiva, amb la veta
    cv.poly([(x0 + 4, ytop), (x1 - 4, ytop), (x1, ytop + 8), (x0, ytop + 8)], TEAK,
            lambda x, y: 4.0 + (y - ytop) * 0.12 + math.sin(x * 0.3 + y) * 0.15)
    cv.rect(x0, ytop + 9, x1, ytop + 13, TEAK, 4.4)
    cv.hline(x0, x1, ytop + 9, TEAK, 5.6)
    cv.hline(x0, x1, ytop + 14, TEAK, 1.0)
    # el caixó dels calaixos (a la dreta) i la pota de l'esquerra
    box(cv, x1 - 61, ytop + 14, x1 - 3, ybot, TEAK, 3.6, grad=0.8)
    for cy in (ytop + 18, ytop + 34, ytop + 50):
        box(cv, x1 - 57, cy, x1 - 7, cy + 13, TEAK, 4.0)
        cv.hline(x1 - 56, x1 - 8, cy + 13, TEAK, 2.0)
        box(cv, x1 - 37, cy + 5, x1 - 27, cy + 7, BRASS, 4.0)
        cv.put(x1 - 32, cy + 8, BRASS, 2.4)
    box(cv, x0 + 3, ytop + 14, x0 + 10, ybot, TEAK, 3.2)
    # el buit de sota, fosc, i el calaix del mig
    cv.rect(x0 + 11, ytop + 14, x1 - 62, ybot, TEAK, lambda x, y: 1.0 + (y - ytop) * 0.008)
    cv.rect(x0 + 11, ytop + 14, x1 - 62, ytop + 24, TEAK, 3.2)
    cv.hline(x0 + 11, x1 - 62, ytop + 24, TEAK, 1.8)
    mx = (x0 + x1 - 51) // 2
    box(cv, mx - 5, ytop + 18, mx + 5, ytop + 20, BRASS, 4.0)
    # la paperera, de reixeta, amb un paper arrugat
    for y in range(ybot - 18, ybot + 1):
        for x in range(261, 280):
            u = (x - 270.5) / 9.5
            if (x + y) % 3:
                cv.put(x, y, CAB, 3.0 - u * 1.2)
    cv.disc(270, ybot - 18, 9, 2, CAB, 1.0)
    cv.hline(261, 280, ybot - 18, CAB, 3.8)
    cv.disc(267, ybot - 20, 4, 3, PAPERC, lambda nx, ny: 4.0 - nx - ny)
    cv.put(266, ybot - 21, PAPERC, 2.4)


def chair(cv):
    """La cadira de l'escriptori, de teca amb el coixí blau, separada de la taula."""
    cx, y0 = 315, 141
    rrect(cv, cx - 17, y0, cx + 17, y0 + 8, 4, TEAK, lambda x, y: 4.6 - (y - y0) * 0.1)
    cv.hline(cx - 14, cx + 14, y0, TEAK, 5.6)
    for x in range(cx - 13, cx + 15, 6):
        cv.vline(x, y0 + 8, y0 + 29, TEAK, 3.4)
        cv.vline(x + 1, y0 + 8, y0 + 29, TEAK, 2.2)
    cv.vline(cx - 17, y0 + 4, y0 + 35, TEAK, 3.8)
    cv.vline(cx - 16, y0 + 4, y0 + 35, TEAK, 3.2)
    cv.vline(cx + 17, y0 + 4, y0 + 35, TEAK, 2.6)
    cv.vline(cx + 16, y0 + 4, y0 + 35, TEAK, 2.0)
    cv.disc(cx, y0 + 39, 21, 5, TEAK, lambda nx, ny: 3.8 - ny * 1.4)
    cv.disc(cx, y0 + 36, 17, 4, NAVY, lambda nx, ny: 4.0 - ny * 1.2)
    cv.put(cx, y0 + 36, NAVY, 2.0)                                       # el botó del coixí
    cv.vline(cx, y0 + 44, y0 + 67, CAB, 3.6)
    cv.vline(cx + 1, y0 + 44, y0 + 67, CAB, 2.2)
    for dx in (-20, -8, 8, 20):
        cv.line(cx, y0 + 67, cx + dx, y0 + 73, CAB, 3.0)
        cv.disc(cx + dx, y0 + 74, 1.5, 1.5, DARK, 0.8)
    cv.darken(cx - 21, y0 + 75, cx + 21, y0 + 77, 0.6)


def contract(cv):
    """El contracte de Blau Net: un plec grapat, amb la capçalera blava i el logotip (una gota)."""
    x0, y0 = 259, 139
    cv.poly([(x0 + 3, y0), (x0 + 32, y0 - 1), (x0 + 35, y0 + 11), (x0, y0 + 12)], PAPERC,
            lambda x, y: 4.4 - (y - y0) * 0.04)
    cv.poly([(x0 + 11, y0 + 1), (x0 + 48, y0 + 1), (x0 + 51, y0 + 12), (x0 + 8, y0 + 12)], PAPERC,
            lambda x, y: 4.8 - (y - y0) * 0.04)
    cv.rect(x0 + 12, y0 + 2, x0 + 48, y0 + 4, [(10, 40, 90), (20, 80, 160), (60, 140, 220)], 1.6)
    cv.put(x0 + 14, y0 + 2, [(240, 250, 255)], 0, lit=0)                   # la gota del logotip
    cv.put(x0 + 14, y0 + 3, [(240, 250, 255)], 0, lit=0)
    cv.put(x0 + 13, y0 + 3, [(200, 220, 240)], 0, lit=0)
    for y in (y0 + 6, y0 + 8, y0 + 10):
        for x in range(x0 + 13, x0 + 48):
            if hr(x // 2, y) > 0.3:
                cv.put(x, y, PAPERC, 2.4)
    cv.line(x0 + 36, y0 + 10, x0 + 46, y0 + 9, BLUEB, 2.4)                # la signatura (no hi és: només la ratlla)
    cv.rect(x0 + 12, y0 + 1, x0 + 14, y0 + 1, CAB, 4.6)                   # la grapa
    # el bolígraf al damunt
    cv.line(x0 + 27, y0 + 13, x0 + 45, y0 + 8, NAVY, 3.0)
    cv.line(x0 + 27, y0 + 14, x0 + 45, y0 + 9, NAVY, 1.6)
    cv.put(x0 + 45, y0 + 8, BRASS, 4.6)


def novel(cv):
    """«Amor a alta mar», volum tres: butxaca de tapa rosa, amb un cor i un punt de llibre amb una àncora."""
    x0, y0 = 331, 141
    cv.poly([(x0 + 3, y0), (x0 + 27, y0), (x0 + 29, y0 + 7), (x0, y0 + 7)], PINK,
            lambda x, y: 3.0 + (y - y0) * 0.08)
    cv.rect(x0, y0 + 8, x0 + 29, y0 + 10, PAPERC, 4.0)
    for x in range(x0 + 1, x0 + 29, 2):
        cv.put(x, y0 + 9, PAPERC, 3.0)                                   # les pàgines
    cv.hline(x0, x0 + 29, y0 + 11, PINK, 1.4)
    for dx, dy in ((12, 2), (14, 2), (16, 2), (18, 2), (11, 3), (12, 3), (13, 3), (14, 3), (15, 3), (16, 3),
                   (17, 3), (18, 3), (19, 3), (12, 4), (13, 4), (14, 4), (15, 4), (16, 4), (17, 4), (18, 4),
                   (14, 5), (15, 5), (16, 5)):
        cv.flat(x0 + dx, y0 + dy, (250, 220, 230))
    cv.flat(x0 + 15, y0 + 2, (220, 140, 170))                            # el cor partit en dos
    cv.rect(x0 + 21, y0 - 7, x0 + 22, y0, BRASS, 4.4)                    # el punt de llibre
    cv.put(x0 + 21, y0 - 8, BRASS, 5.4)
    cv.put(x0 + 22, y0 - 8, BRASS, 5.4)
    cv.put(x0 + 20, y0 - 7, BRASS, 3.4)


def desk_things(cv):
    """El flexo, una tassa i la foto."""
    bx, by = FLEXO
    cv.disc(bx, by, 9, 3, BRASS, lambda nx, ny: 3.6 - nx - ny * 0.4)
    cv.line(bx, by - 1, bx - 5, 128, BRASS, 4.0)
    cv.line(bx + 1, by - 1, bx - 4, 128, BRASS, 2.6)
    cv.disc(bx - 5, 128, 1.5, 1.5, BRASS, 4.6)                           # la ròtula
    cv.line(bx - 5, 128, bx + 8, 117, BRASS, 4.0)
    cv.line(bx - 5, 129, bx + 8, 118, BRASS, 2.6)
    cv.poly([(bx + 3, 115), (bx + 13, 112), (bx + 21, 125), (bx + 3, 128)], SHADE, lambda x, y: 3.4 - (y - 112) * 0.08)
    cv.hline(bx + 4, bx + 20, 127, [(200, 170, 100), (255, 240, 190)], 1.4, lit=0)
    cv.hline(bx + 6, bx + 12, 114, SHADE, 4.6)
    # la tassa (blanca, amb el logotip de Mar Obert: un cercle vermell) i el cafè
    for y in range(136, 150):
        for x in range(237, 248):
            cv.put(x, y, WHITEP, 4.4 - (x - 237) * 0.12)
    cv.disc(241, 142, 2, 2, REDP, 4.4)
    cv.put(241, 142, WHITEP, 5.0)
    cv.ring(250, 142, 3, WHITEP, 3.6, step=20)
    cv.disc(242, 136, 5, 1.5, [(30, 18, 10), (60, 36, 20)], 1.0)
    # la foto: un marc de llautó amb un vaixell petit i el mar
    box(cv, 368, 128, 381, 147, BRASS, 3.2)
    cv.rect(370, 130, 379, 145, [(60, 90, 120), (120, 150, 170), (180, 200, 210)], 1.8)
    cv.rect(370, 140, 379, 145, [(20, 40, 70), (40, 70, 100)], 1.0)
    cv.hline(371, 378, 138, WHITEP, 4.0)
    cv.rect(373, 136, 376, 137, WHITEP, 4.2)
    cv.vline(375, 132, 135, CAB, 2.0)
    cv.line(381, 147, 384, 150, BRASS, 2.0)                               # el peu del marc


def sea_chart(cv):
    """La carta nàutica de la campanya: mar blau pàl·lid, terra groguenca, batimètriques, la ruta, Galway i
    Port Hallen encerclats. Irlanda, a l'est (dreta), amb la badia de Galway; la costa de Valmark, al nord-est."""
    x0, y0, x1, y1 = 440, 48, 603, 133
    box(cv, x0 - 3, y0 - 3, x1 + 3, y1 + 3, TEAK, 4.2)
    cv.hline(x0 - 2, x1 + 2, y0 - 2, TEAK, 5.4)

    def irlanda(x, y):
        u, v = (x - x0) * 0.75, (y - y0) * 0.75
        if not 24 <= v <= 62:
            return False
        costa = 82 + 4 * math.sin(v * 0.45) + 1.5 * math.sin(v * 1.3) + abs(v - 42) ** 2 * 0.04
        if 33 <= v <= 37:                                                # la badia de Galway
            costa += 5 - abs(v - 35) * 1.5
        return u > costa

    def valmark(x, y):
        u, v = (x - x0) * 0.75, (y - y0) * 0.75
        return u > 64 and v < 3 + (u - 64) * 0.12 + 1.5 * math.sin(u * 0.3)

    land = [(150, 134, 90), (196, 180, 128), (226, 212, 160)]
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if irlanda(x, y) or valmark(x, y):
                edge = not (irlanda(x - 1, y) or valmark(x - 1, y)) or not (irlanda(x, y - 1) or valmark(x, y - 1))
                cv.put(x, y, land, 0.6 if edge else 1.6 + (0.4 if (x * 7 + y) % 13 == 0 else 0))
            else:
                deep = math.sin((x - x0) * 0.06 + (y - y0) * 0.038)
                lv = 1.8 if deep > 0.6 else 2.2
                cv.put(x, y, [(120, 150, 170), (160, 190, 206), (200, 222, 232), (226, 238, 242)], lv)
                if abs(deep - 0.6) < 0.03:
                    cv.put(x, y, [(90, 120, 150), (120, 150, 170)], 1.0)           # les batimètriques
    # la quadrícula de longitud i latitud
    for x in range(x0 + 27, x1, 40):
        for y in range(y0, y1, 2):
            cv.put(x, y, [(90, 110, 130), (130, 150, 170)], 1.0)
    for y in range(y0 + 21, y1, 29):
        for x in range(x0, x1, 2):
            cv.put(x, y, [(90, 110, 130), (130, 150, 170)], 1.0)
    # la rosa dels vents, a baix a l'esquerra (mar obert)
    rx, ry = x0 + 19, y0 + 66
    rose = [(90, 60, 80), (150, 100, 120)]
    cv.ring(rx, ry, 8, rose, 1.4, step=15)
    cv.line(rx, ry - 10, rx, ry + 10, rose, 1.4)
    cv.line(rx - 10, ry, rx + 10, ry, rose, 1.4)
    cv.line(rx - 5, ry - 5, rx + 5, ry + 5, rose, 1.0)
    cv.line(rx - 5, ry + 5, rx + 5, ry - 5, rose, 1.0)
    cv.poly([(rx - 2, ry - 2), (rx, ry - 10), (rx + 2, ry - 2)], rose, 0.4)
    text(cv, 'N', rx - 1, ry - 17, None, 0, flat=(90, 60, 80))
    # la ruta, a llapis, del Punt 7 cap a Galway (a l'est)
    gal = (x0 + 115, y0 + 47)
    hal = (x0 + 131, y0 + 12)
    p7 = (x0 + 56, y0 + 53)
    for i in range(0, 60):
        t = i / 60
        x = round(p7[0] + (gal[0] - p7[0]) * t)
        y = round(p7[1] + (gal[1] - p7[1]) * t)
        if i % 4 != 3:
            cv.flat(x, y, (70, 70, 80))
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if abs(dx) + abs(dy) < 2:
                cv.flat(p7[0] + dx, p7[1] + dy, (30, 30, 40))
    text(cv, '7', p7[0] - 2, p7[1] + 3, None, 0, flat=(40, 40, 50))
    # Galway: un cercle fi, a llapis blau, i el nom
    cv.ring(gal[0], gal[1], 6, BLUEB, 2.4, step=10)
    # Port Hallen: en vermell, repassat dues vegades, i un signe d'interrogació
    cv.ring(hal[0], hal[1], 8, REDP, 4.0, step=6)
    cv.ring(hal[0] + 1, hal[1], 9, REDP, 3.4, step=6)
    cv.flat(hal[0], hal[1], (40, 20, 20))
    text(cv, '?', hal[0] - 16, hal[1] - 2, None, 0, flat=(170, 40, 34))
    # el títol de la carta i les xinxetes
    text(cv, 'ATLÀNTIC N', x0 + 4, y0 + 4, None, 0, flat=(80, 96, 116))
    for x, y in ((x0 + 1, y0 + 1), (x1 - 1, y0 + 1), (x0 + 1, y1 - 1), (x1 - 1, y1 - 1)):
        cv.flat(x, y, (220, 50, 46))
        cv.flat(x + 1, y + 1, (120, 20, 20))


def bunk(cv):
    """La llitera de teca amb calaixos, la manta blava de ratlla vermella i el coixí; un llum de lectura."""
    x0, x1, top = 432, 637, 160
    # el llum de lectura de llautó
    box(cv, 616, 139, 627, 144, BRASS, 3.4)
    cv.vline(621, 133, 139, BRASS, 3.0)
    cv.disc(621, 146, 5, 3, [(120, 96, 50), (210, 176, 110), (250, 228, 170)], 1.6, lit=0)
    glow(cv, 621, 148, 14, (255, 220, 150), 0.25)
    # el matalàs i la manta, amb els plecs
    cv.rect(x0 + 5, top, x1, top + 5, PAPERC, lambda x, y: 3.6 + (0.4 if y == top else 0))
    for y in range(top + 4, top + 21):
        for x in range(x0 + 5, x1 + 1):
            fold = math.sin(x * 0.09 + y * 0.22) * 0.3
            cv.put(x, y, NAVY, 3.6 - (y - top) * 0.045 + fold)
    cv.hline(x0 + 5, x1, top + 4, NAVY, 5.0)
    for x in range(x0 + 5, x1 + 1):
        cv.put(x, top + 12, REDP, 3.6)
        cv.put(x, top + 13, REDP, 2.8)
    # el coixí, a la dreta, amb el plec
    rrect(cv, 595, top - 8, 632, top + 4, 4, PAPERC, lambda x, y: 4.6 - (y - top + 8) * 0.07)
    cv.line(604, top - 6, 610, top + 2, PAPERC, 3.4)
    # la post de davant (la vora alta perquè no et tiri la mar) i els calaixos
    box(cv, x0, top + 19, x1, top + 27, TEAK, 4.6)
    cv.hline(x0, x1, top + 19, TEAK, 5.6)
    box(cv, x0, top + 28, x1, FLOOR_Y + 5, TEAK, 3.4, grad=0.6)
    for dx in range(x0 + 8, x1 - 40, 67):
        box(cv, dx, top + 32, dx + 56, FLOOR_Y, TEAK, 3.8)
        cv.hline(dx + 1, dx + 55, FLOOR_Y, TEAK, 2.0)
        box(cv, dx + 23, top + 37, dx + 33, top + 39, BRASS, 4.0)
        cv.put(dx + 28, top + 40, BRASS, 2.4)
    box(cv, x0, top - 5, x0 + 5, FLOOR_Y + 5, TEAK, 4.2)                    # el capçal dels peus
    cv.hline(x0, x0 + 5, top - 5, TEAK, 5.6)


def rug(cv):
    """Una catifa gastada, blau marí amb vora vermella i serrell, a terra davant l'escriptori."""
    pts = [(235, 219), (424, 219), (445, 251), (213, 251)]
    cv.poly(pts, NAVY, lambda x, y: 2.6 + (0.4 if (x // 3 + y) % 6 == 0 else 0) + (hr(x // 5, y) - 0.5) * 0.3)
    cv.poly([(243, 223), (416, 223), (435, 247), (224, 247)], REDP, 2.2)
    cv.poly([(248, 225), (411, 225), (428, 244), (232, 244)], NAVY, lambda x, y: 2.8 + (hr(x // 4, y // 2) - 0.5) * 0.3)
    # el motiu del mig: un rombe vermell
    cv.poly([(330, 228), (348, 234), (330, 241), (312, 234)], REDP, 2.0)
    cv.poly([(330, 231), (340, 234), (330, 238), (320, 234)], NAVY, 3.2)
    for x in range(213, 446, 3):                                         # el serrell
        cv.put(x, 252, PAPERC, 2.0)
        cv.put(x, 253, PAPERC, 1.4)
    for x in range(236, 424, 3):
        cv.put(x, 218, PAPERC, 1.8)


# ─── Muntatge ───────────────────────────────────────────────────────────────

PORT = (141, 101, 15)              # l'ull de bou: centre i radi del vidre


def bg(cv):
    wall(cv, dado=FLOOR_Y, rail=FLOOR_Y + 20, seed=3)                  # sense sòcol ni passamans: hi ha el folre
    wainscot(cv)
    ceiling(cv)
    mask = lino(cv, lvl=3.8)
    foot_shadow(cv, 0, W - 1, FLOOR_Y + 1, 5, 0.35)
    shine(cv, mask, [lx for lx, _ in LAMPS])
    rug(cv)
    watertight_door(cv)
    cap_hook(cv)
    _porthole(cv, PORT[0], PORT[1], PORT[2], None, rim=4)
    box(cv, PORT[0] - 2, PORT[1] + PORT[2] + 5, PORT[0] + 2, PORT[1] + PORT[2] + 9, BRASS, 3.2)   # la palanca
    clock_barometer(cv)
    bookshelf(cv)
    desk(cv)
    chair(cv)
    desk_things(cv)
    contract(cv)
    novel(cv)
    sea_chart(cv)
    bunk(cv)
    for lx, ly in LAMPS:
        lamp(cv, lx, ly)
    cv.darken(DESK[0], DESK[3] + 1, DESK[2], DESK[3] + 5, lambda x, y: 0.8 - (y - DESK[3]) * 0.16)
    cv.darken(432, FLOOR_Y + 6, 639, FLOOR_Y + 10, lambda x, y: 0.7 - (y - FLOOR_Y - 6) * 0.16)
    for lx, ly in LAMPS:
        lamp_glow(cv, lx, ly)
    glow(cv, 401, 131, 35, (255, 220, 150), 0.35)                     # el flexo


# Escenes 2 i 3: de dia, el vidre de l'ull de bou clar
PROPS = {'ulls_dia': lambda cv: day_porthole(cv, *PORT)}
