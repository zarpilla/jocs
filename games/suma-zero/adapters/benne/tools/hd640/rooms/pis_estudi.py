"""
L'estudi de l'Iri (Escena 1), de nit, a 640×360: la composició de hd/rooms/pis_estudi.py ×4/3, dibuixada de nou.
**Sala de mostra de l'art definitiu de Suma Zero** (proposta B, la triada):
  - **escala real** dels mobles, per a personatges de ≈111 px (escriptori a l'altura del maluc);
  - **maó pintat de lila**, negres, i la llum ve de les pantalles (cian) i del neó del carrer (magenta),
    que entra per les **persianes** i pinta franges a la paret; el pòster del gat i el 404;
  - pluja al vidre, i contorns només on cal (com a Ferro-9).
Animacions: `pantalles` (pluja al vidre i el codi que corre), `neo` (la meitat del rètol de la pizzeria que es fon)
i `disc_dur` (el llumet de la torre).
"""
import math

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from hd640 import llum
from hd.pix import Light, Canvas, W, H, hr
from hd.rooms.comu import obox, outline, cable, text, _diff, PLASTIC, SCREEN, SKY, CITY, NEON, SHEET, GRAYC, YEL, CARD, RED
from hd.rooms.pis_estudi import BRICK, MORTAR, FLOORB, DESKB, STEELB, MAGENTA, CYANL, FABRICB, WARMB

# Art a 2× (1280×720 per a una sala de 640×360): el mateix dibuix, amb les formes, el dither i la llum a la
# resolució real (hd1280/canvas2x.py); el motor el mostra a 1/2 (artScale al .room.json).
ART_SCALE = 2
from hd1280.canvas2x import Canvas2x as Canvas  # noqa: E402,F811
from hd.pix import Canvas as Canvas1x  # noqa: E402,F401  (llenços auxiliars en píxels de sala: figures, textos)

FLOOR_Y = 200
DESK_Y = 155   # escala real: el taulell a l'altura del maluc d'una persona de ≈111 px

LIGHT = Light(ambient=-0.6, vignette=(93, 53), floor_fade=(253, 35))
LIGHT.point(377, 123, r=227, k=3.0, squash=1.2, power=1.6)       # monitors
LIGHT.point(607, 107, r=93, k=1.4, squash=1.0, power=2.0)        # passaplats (cuina): poca llum
LIGHT.point(105, 96, r=93, k=0.8, squash=0.9, power=2.0)         # finestra

WINDOW = (45, 40, 165, 149)
HATCH = (581, 77, 632, 133)
MONITORS = ((275, 99, 328, 147), (336, 80, 419, 147), (427, 99, 480, 147))
PORTS = (513, 521, 529)       # els ports del router (x de l'esquerra); els leds, a sobre, a y=156

YELC = [(10, 10, 20), (180, 140, 20), (232, 196, 50), (252, 236, 130)]
BLUEC = [(4, 4, 8), (20, 40, 70), (50, 100, 170), (110, 170, 230)]


def frame(cv, x0, y0, x1, y1, ramp, lvl, t=3):
    """Marc de gruix t."""
    for (a, b, c, d) in ((x0, y0, x1, y0 + t - 1), (x0, y1 - t + 1, x1, y1), (x0, y0, x0 + t - 1, y1), (x1 - t + 1, y0, x1, y1)):
        cv.rect(a, b, c, d, ramp, lvl)


def stripes(x, y):
    """Les franges de neó que la persiana projecta a la paret (en diagonal, cap a la dreta)."""
    if y > FLOOR_Y + 19 or y < 13:
        return 0.0
    u = x - 173 - (y - 40) * 0.9
    if not 0 <= u < 200:
        return 0.0
    edge = min(1.0, u / 40, (200 - u) / 40)          # s'esvaeix als extrems del raig
    fade = 1.0 if y <= FLOOR_Y else 1 - (y - FLOOR_Y) / 19
    return (1.0 if int(u) % 16 < 8 else 0.0) * edge * fade


# ─── Paret i terra ──────────────────────────────────────────────────────────

def wall(cv):
    # maó pintat de lila, gastat: maons de 24×9, juntes d'1 px, i alguna escantonada
    for y in range(0, FLOOR_Y):
        row = y // 9
        off = 12 if row % 2 else 0
        for x in range(W):
            bx = (x + off) // 24
            if y % 9 == 8 or (x + off) % 24 == 0:
                cv.put(x, y, MORTAR, 2.2)
            else:
                lvl = 2.6 + (hr(bx, row) - 0.5) * 0.8 + (hr(x // 2, y // 2) - 0.5) * 0.3
                if y % 9 == 0:
                    lvl += 0.35                                  # el cantell de dalt del maó agafa llum
                if hr(bx, row, 5) > 0.93 and (x + off) % 24 < 4 and y % 9 < 3:
                    lvl -= 1.2                                   # escantonat
                cv.put(x, y, BRICK, lvl)
    cv.rect(0, FLOOR_Y - 7, W - 1, FLOOR_Y - 1, DESKB, 2.4)
    cv.hline(0, W - 1, FLOOR_Y - 7, DESKB, 3.4)
    cv.hline(0, W - 1, FLOOR_Y, DESKB, 0)


def neon_stripes(cv, k=1.0):
    """Franges magenta damunt de tot el que hi ha a la paret."""
    cv.tint(0, 0, W - 1, FLOOR_Y + 19, (210, 60, 170), lambda x, y: 0.13 * k * stripes(x, y))


def floor(cv):
    # tarima fosca de laminat (llistons de 40 amb les juntes de testa alternades), amb la llum de les pantalles
    for y in range(FLOOR_Y + 1, H):
        dep = (y - FLOOR_Y) / (H - FLOOR_Y)
        v = (y - FLOOR_Y) * 2.4 / (1 + dep * 0.5)
        for x in range(W):
            u = (x - W / 2) / (1 + dep * 0.5) + W / 2
            plank = math.floor(u / 40)
            lvl = 2.4 + (hr(plank, 3) - 0.5) * 0.6 + (hr(int(u) // 3, y, plank) - 0.5) * 0.25
            if (u % 40) < 1:
                lvl = 0.8
            elif int(v + hr(plank, 7) * 90) % 90 == 0:
                lvl = 1.2                                        # junta de testa
            cv.put(x, y, FLOORB, lvl)
    # reflex de les pantalles al terra
    cv.tint(267, FLOOR_Y + 16, 493, 267, (60, 180, 170), lambda x, y: 0.18 * max(0, 1 - abs(x - 377) / 120) * max(0, 1 - (y - 216) / 53))


# ─── La finestra ────────────────────────────────────────────────────────────

def window(cv, rain=0, neon=True):
    x0, y0, x1, y1 = WINDOW
    for y in range(y0 + 4, y1 - 3):
        for x in range(x0 + 4, x1 - 3):
            cv.put(x, y, SKY, 0.6 + (y - y0) / 53, lit=0)
    # la ciutat: blocs amb terrats (dipòsits, antenes) i finestres enceses
    blocks = ((49, 19, 75), (69, 13, 88), (84, 24, 61), (109, 16, 83), (127, 21, 53), (147, 16, 75))
    for i, (bx, bw, bh) in enumerate(blocks):
        top = y1 - 4 - bh
        cv.rect(bx, top, bx + bw, y1 - 4, CITY, 1.0 + (0.4 if i % 2 else 0), lit=0)
        cv.vline(bx + bw, top, y1 - 4, CITY, 0.3, lit=0)
        if i in (1, 4):                                                   # antena amb el llum vermell
            cv.vline(bx + bw // 2, top - 9, top - 1, CITY, 2.0, lit=0)
            cv.flat(bx + bw // 2, top - 10, (200, 40, 40))
        elif i in (0, 3):                                                 # dipòsit d'aigua
            cv.rect(bx + 3, top - 5, bx + 9, top - 1, CITY, 1.6, lit=0)
            cv.hline(bx + 2, bx + 10, top - 6, CITY, 2.2, lit=0)
        for wy in range(top + 4, y1 - 8, 6):
            for wx in range(bx + 2, bx + bw - 1, 4):
                if hr(wx, wy, i) > 0.7:
                    col = (120, 190, 220) if hr(wy, wx) > 0.5 else (200, 150, 90)
                    cv.flat(wx, wy, col)
                    cv.flat(wx + 1, wy, tuple(int(c * 0.7) for c in col))
    # el neó del carrer: el rètol de la pizzeria, en magenta, amb el tub de la vora (al vidre de l'esquerra)
    for x in range(61, 93):
        for y in (107, 117):
            cv.put(x, y, NEON, 2.6 if neon or x < 74 else 0.6, lit=0)
    text(cv, 'PI', 67, 110, NEON, 3.8, lit=0)
    text(cv, 'ZZA', 75, 110, NEON, 3.8 if neon else 0.7, lit=0)        # neon=False: la meitat dreta, fosa
    cv.glow(77, 112, 24, (255, 90, 200), 0.4 if neon else 0.22)
    # pluja: regalims al vidre
    for i in range(36):
        rx = x0 + 5 + int(hr(i, 9) * (x1 - x0 - 10))
        ry = y0 + 5 + int((hr(i, 3) * (y1 - y0) + rain * 9 + i * 4) % (y1 - y0 - 13))
        n = 4 + int(hr(i, 5) * 6)
        for d in range(n):
            cv.tint(rx, ry + d, rx, ry + d, (170, 200, 230), 0.45 if d < n - 1 else 0.7)
    # persiana mig abaixada: llistons horitzontals, amb la corda i la maneta
    for y in range(y0 + 3, 96, 5):
        cv.hline(x0 + 3, x1 - 3, y, STEELB, 3.6)
        cv.hline(x0 + 3, x1 - 3, y + 1, STEELB, 2.6)
        cv.hline(x0 + 3, x1 - 3, y + 2, STEELB, 1.4)
    cv.hline(x0 + 3, x1 - 3, 97, STEELB, 4.0)                            # el llistó de baix, més gruixut
    cv.hline(x0 + 3, x1 - 3, 98, STEELB, 2.0)
    for cx in (x0 + 24, x1 - 24):
        cv.vline(cx, y0 + 3, 96, STEELB, 1.6)
    cv.vline(x0 + 8, y0 + 3, 116, GRAYC, 2.4)                             # la corda
    cv.rect(x0 + 7, 117, x0 + 9, 121, GRAYC, 3.2)
    # marc d'alumini
    frame(cv, x0, y0, x1, y1, STEELB, 3.0)
    cv.hline(x0, x1, y0, STEELB, 4.0)
    cv.rect((x0 + x1) // 2 - 1, y0, (x0 + x1) // 2 + 1, y1, STEELB, 2.6)
    cv.vline((x0 + x1) // 2 - 1, y0, y1, STEELB, 3.4)
    cv.rect(x0 - 5, y1, x1 + 5, y1 + 4, STEELB, 3.2)
    cv.hline(x0 - 5, x1 + 5, y1, STEELB, 4.2)
    cv.hline(x0 - 5, x1 + 5, y1 + 4, STEELB, 0)


def poster(cv):
    """El pòster del gat amb ulleres de sol i el «404» (el «HANG IN THERE», en versió hacker)."""
    x0, y0, x1, y1 = 200, 48, 253, 123
    obox(cv, x0, y0, x1, y1, SHEET, 3.4)
    cv.rect(x0 + 4, y0 + 4, x1 - 4, y1 - 21, SKY, lambda x, y: 2.2 + (y - y0) * 0.02)
    for i in range(9):                                                     # estrelles
        cv.flat(x0 + 6 + int(hr(i, 41) * 40), y0 + 6 + int(hr(i, 42) * 46), (110, 120, 170))
    cv.disc(227, 79, 12, 11, GRAYC, lambda nx, ny: 3.0 - ny - nx * 0.3)
    cv.poly([(216, 72), (217, 61), (224, 69)], GRAYC, 3.2)
    cv.poly([(238, 72), (237, 61), (230, 69)], GRAYC, 3.2)
    cv.poly([(218, 70), (218, 65), (222, 69)], RED, 1.6)                   # l'interior de les orelles
    cv.poly([(236, 70), (236, 65), (232, 69)], RED, 1.6)
    cv.disc(227, 92, 9, 4, GRAYC, 1.4)                                     # el coll
    cv.rect(217, 76, 224, 80, PLASTIC, 0.5)
    cv.rect(230, 76, 237, 80, PLASTIC, 0.5)
    cv.hline(224, 230, 77, PLASTIC, 0.5)
    cv.flat(218, 77, (200, 200, 230))                                      # la lluïssor de les ulleres
    cv.flat(231, 77, (200, 200, 230))
    cv.rect(226, 83, 228, 84, RED, 2.0)                                    # el nas
    cv.flat(225, 86, GRAYC[0])
    cv.flat(229, 86, GRAYC[0])
    for dy in (-1, 1):                                                     # bigotis
        cv.line(213, 84 + dy * 2, 221, 85 + dy, GRAYC, 5.0)
        cv.line(233, 85 + dy, 241, 84 + dy * 2, GRAYC, 5.0)
    digits = {'4': ['101', '101', '111', '001', '001'], '0': ['111', '101', '101', '101', '111']}
    x = 211
    for ch in '404':
        for j, row in enumerate(digits[ch]):
            for i, b in enumerate(row):
                if b == '1':
                    cv.rect(x + i * 3, 105 + j * 3, x + i * 3 + 2, 105 + j * 3 + 2, RED, 3.2)
        x += 12
    # cinta adhesiva als cantons, i un cantó que s'aixeca
    for cx, cy in ((x0, y0), (x1, y0)):
        cv.rect(cx - 4, cy - 1, cx + 4, cy + 3, YEL, 3.0)
        cv.hline(cx - 4, cx + 4, cy - 1, YEL, 4.0)
    cv.poly([(x1, y1 - 6), (x1, y1), (x1 - 6, y1)], SHEET, 1.6)
    cv.darken(x1 + 1, y0 + 3, x1 + 2, y1, 0.5)


def mattress(cv):
    cv.poly([(24, 203), (195, 203), (203, 227), (16, 227)], SHEET, lambda x, y: 1.6 + (0.6 if y < 207 else 0))
    cv.rect(16, 227, 203, 233, SHEET, 0.8)
    cv.hline(16, 203, 228, SHEET, 1.4)
    for x in range(22, 200, 6):                                            # el costat del matalàs, encoixinat
        cv.vline(x, 229, 232, SHEET, 0.3)
    duvet = [(21, 195), (107, 187), (197, 200), (203, 221), (80, 224), (19, 221)]
    cv.poly(duvet, FABRICB, lambda x, y: 2.2 + 0.9 * math.sin(x / 9 + y / 5) + (0.8 if y < 196 else 0))
    for k in range(3):                                                     # plecs
        cv.line(60 + k * 34, 194 + k, 74 + k * 36, 220 - k, FABRICB, 1.0)
    cv.disc(43, 196, 21, 8, SHEET, lambda nx, ny: 2.4 - ny * 1.2)
    cv.line(28, 197, 56, 195, SHEET, 1.2)                                  # el clot del coixí
    # un llibre obert, de bocaterrosa damunt de l'edredó
    cv.poly([(130, 200), (140, 197), (150, 200), (140, 203)], RED, 1.8)
    cv.line(131, 201, 139, 204, SHEET, 2.4)                                # el cantell de les pàgines
    cv.line(141, 204, 149, 201, SHEET, 2.0)
    cv.line(140, 197, 140, 203, RED, 0.6)


# ─── L'escriptori ───────────────────────────────────────────────────────────

def desk(cv):
    # escriptori d'acer i fusta fosca, a escala real
    obox(cv, 261, DESK_Y, 491, DESK_Y + 5, DESKB, 3.0, top=1.2)
    for x in (267, 483):
        cv.rect(x, DESK_Y + 6, x + 4, 221, STEELB, 2.4)
        cv.vline(x, DESK_Y + 6, 221, STEELB, 3.4)
        cv.rect(x - 2, 220, x + 6, 221, STEELB, 1.6)                       # els peus
    cv.line(271, 200, 482, 200, STEELB, 1.8)
    cv.line(271, 201, 482, 201, STEELB, 0.8)
    # torre del PC sota la taula, amb llums i la reixeta
    obox(cv, 285, 171, 315, 221, PLASTIC, 2.0)
    cv.vline(309, 176, 213, CYANL, 4.0, lit=0)
    cv.vline(310, 176, 213, CYANL, 2.4, lit=0)
    for y in range(195, 214, 3):
        cv.hline(290, 303, y, PLASTIC, 0.6)
    cv.rect(289, 176, 291, 177, PLASTIC, 4.0)                                # el botó
    cv.glow(309, 195, 13, (60, 200, 210), 0.25)
    # cadira de malla
    cv.disc(400, 203, 27, 7, PLASTIC, lambda nx, ny: 1.8 - ny * 0.6)
    cv.rect(396, 209, 404, 227, STEELB, 2.0)
    cv.vline(397, 209, 227, STEELB, 3.0)
    for dx in (-19, -8, 8, 19):
        cv.line(400, 227, 400 + dx, 235, STEELB, 2.0)
        cv.disc(400 + dx, 236, 2, 1.5, PLASTIC, 1.4)                       # rodetes
    back = [(379, 139), (421, 139), (425, 195), (375, 195)]
    cv.poly(back, PLASTIC, lambda x, y: 1.6 + (0.6 if (x + y) % 3 == 0 else 0) + (0.5 if y < 143 else 0))
    cv.rect(381, 193, 419, 196, PLASTIC, 2.2)
    outline(cv, 375, 139, 425, 196, PLASTIC)
    for (ax, bx) in ((372, 377), (423, 428)):                              # braços
        cv.rect(ax, 176, bx, 178, PLASTIC, 2.4)


def monitors(cv, frame=0):
    for n, (x0, y0, x1, y1) in enumerate(MONITORS):
        obox(cv, x0, y0, x1, y1, PLASTIC, 1.6)
        sx0, sy0, sx1, sy1 = x0 + 3, y0 + 3, x1 - 3, y1 - 4
        for y in range(sy0, sy1 + 1):
            for x in range(sx0, sx1 + 1):
                cv.put(x, y, SCREEN, 1.2 + (0.25 if (y + frame) % 2 == 0 else 0), lit=0)
        for row in range(sy0 + 2, sy1, 4):
            seed = (row - sy0) // 4 + frame + n * 7
            indent = int(hr(seed, 1) * 3) * 4
            length = int(5 + hr(seed, 2) * (sx1 - sx0 - 13))
            for x in range(sx0 + 3 + indent, min(sx1 - 1, sx0 + 3 + indent + length)):
                if hr(x // 4, seed) > 0.25 and (x + 1) % 4:
                    cv.put(x, row, SCREEN, 4.2 if n != 1 or row % 12 else 5.2, lit=0)
        cv.flat((x0 + x1) // 2, y1 - 1, (60, 200, 120))                    # el llum d'engegada
        mx = (x0 + x1) // 2
        cv.rect(mx - 2, y1 + 1, mx + 1, DESK_Y - 1, STEELB, 2.4)
        cv.vline(mx - 2, y1 + 1, DESK_Y - 1, STEELB, 3.4)
        cv.rect(mx - 9, DESK_Y - 2, mx + 9, DESK_Y - 1, STEELB, 3.0)
    # a la del mig, el rètol «BCMU» i, a sota, el mapa de xarxa del banc
    cv.rect(356, 85, 400, 99, SCREEN, 2.4, lit=0)
    outline(cv, 356, 85, 400, 99, SCREEN)
    font = {'B': ['11110', '10001', '10001', '11110', '10001', '10001', '11110'],
            'C': ['01111', '10000', '10000', '10000', '10000', '10000', '01111'],
            'M': ['1000001', '1100011', '1010101', '1001001', '1000001', '1000001', '1000001'],
            'U': ['10001', '10001', '10001', '10001', '10001', '10001', '01110']}
    x = 362
    for ch in 'BCMU':
        for j, row in enumerate(font[ch]):
            for i, bit in enumerate(row):
                if bit == '1':
                    cv.put(x + i, 89 + j, SCREEN, 5.4, lit=0)
        x += len(font[ch][0]) + 2
    nodes = ((349, 109), (379, 105), (403, 112), (363, 125), (395, 129), (379, 137))
    for (ax, ay), (bx, by) in ((nodes[0], nodes[1]), (nodes[1], nodes[2]), (nodes[0], nodes[3]), (nodes[3], nodes[4]),
                               (nodes[2], nodes[4]), (nodes[4], nodes[5]), (nodes[3], nodes[5])):
        cv.line(ax, ay, bx, by, SCREEN, 3.4, lit=0)
    for i, (x, y) in enumerate(nodes):
        if i == 5:                                                          # el node de la seu: vermell, amb anella
            cv.disc(x, y, 3, 3, [(60, 6, 10), (150, 20, 26), (240, 70, 60), (255, 160, 140)], 3.0, lit=0)
            cv.ring(x, y, 5, [(150, 20, 26), (240, 70, 60)], 1.0, lit=0, step=20)
        else:
            cv.disc(x, y, 2.5, 2.5, SCREEN, 5.0, lit=0)
    cv.glow(377, 117, 93, (60, 200, 190), 0.14)


def desk_clutter(cv):
    # teclat retroil·luminat, dues fileres de tecles
    obox(cv, 344, DESK_Y - 4, 400, DESK_Y, PLASTIC, 2.0)
    for x in range(347, 397, 4):
        cv.hline(x, x + 2, DESK_Y - 3, CYANL, 2.6, lit=0)
        cv.hline(x + 2, x + 4, DESK_Y - 1, CYANL, 2.2, lit=0)
    cv.disc(413, DESK_Y - 1, 4, 2, PLASTIC, 2.0)                             # el ratolí
    cv.flat(413, DESK_Y - 2, (60, 200, 210))
    for x in (296, 304):                                                    # llaunes de beguda energètica
        obox(cv, x, DESK_Y - 15, x + 5, DESK_Y, GRAYC, 2.6)
        cv.rect(x + 1, DESK_Y - 10, x + 4, DESK_Y - 6, [(10, 40, 20), (30, 120, 50), (90, 220, 100)], 1.6, lit=0.6)
        cv.hline(x + 1, x + 4, DESK_Y - 14, GRAYC, 4.6)
    obox(cv, 453, DESK_Y - 16, 469, DESK_Y, PLASTIC, 1.8)                    # un portàtil vell, tancat, de cantell
    cv.rect(456, DESK_Y - 11, 466, DESK_Y - 9, MAGENTA, 3.0, lit=0)          # adhesiu
    obox(cv, 321, DESK_Y - 9, 329, DESK_Y, RED, 2.2)                        # la tassa de cafè
    cv.line(330, DESK_Y - 7, 331, DESK_Y - 3, RED, 2.0)
    cv.hline(322, 328, DESK_Y - 8, [(20, 10, 6), (40, 22, 12)], 1.0)
    obox(cv, 315, 131, 325, 141, YEL, 3.0)                                  # un pòsit a la vora de la pantalla
    for j in range(3):
        cv.hline(317, 317 + 4 + (j * 3) % 4, 134 + j * 2, [(60, 20, 20), (120, 30, 30)], 1.4, lit=0)


def router_shelf(cv):
    obox(cv, 496, 168, 547, 213, STEELB, 2.0)                                # moble d'acer d'oficina
    cv.hline(497, 546, 189, STEELB, 0.6)
    cv.hline(497, 546, 190, STEELB, 3.0)
    cv.rect(515, 177, 528, 178, STEELB, 3.4)
    cv.rect(515, 199, 528, 200, STEELB, 3.4)
    for y in (180, 202):
        cv.rect(519, y, 524, y + 3, SHEET, 3.0)                               # etiquetes dels calaixos
    obox(cv, 501, 152, 541, 167, PLASTIC, 1.8, top=1.2)                       # el router
    cv.line(507, 152, 503, 136, PLASTIC, 2.2)
    cv.line(536, 152, 540, 136, PLASTIC, 2.2)
    cv.flat(503, 135, PLASTIC[3])
    cv.flat(540, 135, PLASTIC[3])
    for x in PORTS:
        cv.rect(x, 160, x + 4, 164, PLASTIC, 0.4)
        cv.flat(x + 1, 156, (90, 30, 30))
        cv.flat(x + 2, 156, (70, 24, 24))
    for x in range(533, 539, 2):                                              # reixeta
        cv.vline(x, 157, 164, PLASTIC, 0.6)
    obox(cv, 560, 149, 573, 168, SHEET, 2.4)                                  # la presa de fibra
    cv.rect(564, 156, 569, 161, PLASTIC, 1.0)
    cv.flat(566, 152, (60, 160, 80))
    cable(cv, [(567, 168), (576, 200), (557, 211), (552, 187)], YELC, 1.4, thick=3)


def hatch(cv):
    x0, y0, x1, y1 = HATCH
    for y in range(y0 + 3, y1 - 2):
        for x in range(x0 + 3, x1 - 2):
            cv.put(x, y, WARMB, 0.9 + (y - y0) / 70 + (0.4 if (x - y) % 13 == 0 else 0), lit=0)   # vidre glaçat (la cuina, fosca)
    cv.rect(x0 + 3, 106, x1 - 3, 108, WARMB, 0.4, lit=0)
    cv.rect(603, 101, 610, 103, STEELB, 3.0)                                  # nanses
    cv.rect(603, 111, 610, 113, STEELB, 3.0)
    frame(cv, x0, y0, x1, y1, DESKB, 2.6)
    outline(cv, x0, y0, x1, y1, DESKB)
    cv.glow(608, 120, 30, (240, 170, 100), 0.05)


def pizza_stack(cv):
    for i, (x0, y0, dx) in enumerate(((200, 221, 0), (203, 213, 4), (197, 205, -3), (201, 197, 3))):
        cv.poly([(x0 + dx, y0), (x0 + dx + 51, y0), (x0 + 51, y0 + 8), (x0, y0 + 8)], CARD,
                lambda x, y, i=i, x0=x0: 2.0 - (i % 2) * 0.4 - (0.6 if x > x0 + 45 else 0))
        cv.hline(x0 + dx + 1, x0 + dx + 50, y0, CARD, 3.0)
        cv.hline(x0, x0 + 51, y0 + 8, CARD, 0)
        cv.hline(x0 + 4, x0 + 12, y0 + 4, CARD, 0.8)                          # la nansa de la capsa
    cv.disc(229, 199, 6, 2, RED, 2.2)                                         # el logo de la de dalt
    cv.hline(225, 233, 199, [(240, 220, 180)], 0)


def floor_cables(cv):
    cable(cv, [(320, 216), (333, 253), (440, 235), (507, 261), (560, 224), (533, 213)], [(4, 4, 8), (20, 20, 28), (40, 40, 52), (70, 70, 84)], 1.6, thick=3)
    cable(cv, [(309, 213), (267, 267), (160, 240), (80, 259)], [(4, 4, 8), (20, 40, 70), (40, 80, 130), (80, 130, 180)], 1.6, thick=3)
    cable(cv, [(488, 213), (507, 243), (587, 248), (621, 213)], [(4, 4, 8), (80, 20, 24), (130, 36, 40), (180, 80, 80)], 1.6, thick=2)
    obox(cv, 614, 186, 624, 200, SHEET, 2.4)                                  # l'endoll de terra
    cv.flat(617, 192, (20, 16, 14))
    cv.flat(621, 192, (20, 16, 14))


def _draw(cv):
    wall(cv)
    floor(cv)
    window(cv)
    poster(cv)
    neon_stripes(cv)
    mattress(cv)
    pizza_stack(cv)
    desk(cv)
    monitors(cv, 0)
    desk_clutter(cv)
    router_shelf(cv)
    hatch(cv)
    floor_cables(cv)
    cv.darken(261, 213, 491, 221, 0.5)
    cv.darken(496, 211, 549, 219, 0.4)


# ─── Llum (prototip: hd640/llum.py) ─────────────────────────────────────────

def _stripe_fade(x, y):
    import numpy as np
    return np.clip(1 - (y - 40) / 220, 0, 1) * 0.8 + 0.2


FX_LIGHT = [
    llum.wash(377, 118, 210, (80, 230, 210), k=1.0, air=0.05, squash=1.1),            # les pantalles, cian
    llum.wash(105, 105, 170, (190, 110, 255), k=0.9, air=0.06, squash=0.9),           # la finestra, lila
    llum.haze([(50, 100), (160, 100), (232, 236), (8, 236)], (170, 90, 230), k=0.16, blur=10,
              fade=lambda x, y: 1.25 - (y - 100) / 180),                                 # el con de la finestra
    llum.haze([(173, 13), (373, 13), (373 + 0.9 * 206, 219), (173 + 0.9 * 206, 219)], (210, 70, 190), k=0.07,
              blur=14, fade=_stripe_fade),                                               # el raig de les persianes
]
FX_TONE = [llum.grade(contrast=1.12, pivot=40, sat=1.25, lift=(5, 1, 10))]
FX = FX_LIGHT + [llum.bloom(thr=125, mask=lambda x, y: 1 - 0.75 * ((x > 578) & (y < 138)) - 0.8 * ((x > 196) & (x < 258) & (y < 126)))] + FX_TONE
FX_PROPS = FX_LIGHT + FX_TONE                       # els props no fan bloom (el halo cauria fora del seu alfa)


def bg(cv):
    _draw(cv)
    llum.apply_cv(cv, FX)


# ─── Props ──────────────────────────────────────────────────────────────────

def caixa(cv):
    x0, y0, x1, y1 = 400, 229, 451, 253
    cv.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], CARD, lambda x, y: 2.2 - (0.8 if x > x1 - 11 else 0))
    cv.poly([(x0, y0), (x0 + 8, y0 - 12), (x0 + 21, y0 - 9), (x0 + 16, y0)], CARD, 2.8)
    cv.line(x0 + 8, y0 - 12, x0 + 21, y0 - 9, CARD, 4.0)
    cv.rect(x0 + 3, y0 + 1, x1 - 3, y0 + 4, CARD, 0.6)
    cv.rect(x0 + 24, y0 + 5, x0 + 29, y1, [(60, 50, 30), (110, 96, 60), (150, 134, 90)], 1.8)   # cinta d'embalar
    cv.rect(x0 + 6, y0 + 10, x0 + 21, y0 + 17, SHEET, 2.6)                    # l'etiqueta
    for j in range(2):
        cv.hline(x0 + 8, x0 + 15 + j * 3, y0 + 12 + j * 3, GRAYC, 1.0)
    cv.vline(x1, y0, y1, CARD, 0)
    cv.hline(x0, x1, y1, CARD, 0)
    cv.darken(x0 - 3, y1 + 1, x1 + 4, y1 + 3, 0.5)


def router_connectat(cv):
    for x in PORTS:
        cv.flat(x + 1, 156, (120, 255, 150))
        cv.flat(x + 2, 156, (80, 200, 110))
    cv.glow(523, 156, 13, (120, 255, 160), 0.4)


def fibra_connectada(cv):
    """La fibra, de la presa al router (groc)."""
    cable(cv, [(567, 168), (560, 171), (549, 165), (539, 163)], YELC, 2.2, thick=2)
    cv.rect(537, 161, 540, 164, PLASTIC, 3.0)


def xarxa_connectada(cv):
    """El cable de xarxa, del router a la torre de sota la taula (blau)."""
    cable(cv, [(515, 165), (507, 200), (400, 224), (315, 200)], BLUEC, 2.2, thick=2)
    cv.rect(513, 163, 517, 166, BLUEC, 2.6)


def alimentacio_connectada(cv):
    """El cable d'alimentació, del router a l'endoll de terra (negre amb el transformador)."""
    cable(cv, [(531, 165), (539, 200), (560, 221), (590, 227)], [(4, 4, 8), (24, 24, 30), (50, 50, 60), (90, 90, 100)], 2.0, thick=2)
    obox(cv, 589, 221, 601, 230, PLASTIC, 2.4)
    cv.flat(593, 224, (60, 200, 90))
    cable(cv, [(601, 225), (610, 222), (616, 210), (619, 196)], [(4, 4, 8), (24, 24, 30), (50, 50, 60), (90, 90, 100)], 2.0, thick=1)


def passaplats_obert(cv):
    """El passaplats obert (les portetes s'obren cap a la cuina): es veu la cuina, càlida, amb les rajoles
    verdes, la cantonada d'un armari i el llum penjant."""
    x0, y0, x1, y1 = HATCH
    plaster = [(30, 18, 18), (44, 28, 24), (60, 40, 30), (78, 54, 38), (98, 70, 46), (120, 88, 56), (144, 108, 68), (170, 132, 86)]
    tiles = [(18, 30, 28), (30, 46, 40), (46, 64, 54), (64, 84, 70), (86, 106, 86), (112, 130, 104)]
    for y in range(y0 + 3, y1 - 2):
        for x in range(x0 + 3, x1 - 2):
            glow = max(0, 1 - math.hypot(x - 595, y - 85) / 53) * 2.4
            if y >= 112:
                grout = (y - 112) % 8 == 7 or (x - x0) % 8 == 7
                gloss = 0.6 if (x - x0) % 8 == 1 and (y - 112) % 8 < 3 else 0
                cv.put(x, y, tiles, (1.2 if grout else 2.4 + gloss) + glow * 0.6, lit=0)
            else:
                cv.put(x, y, plaster, 2.4 + glow + (hr(x // 3, y // 3) - 0.5) * 0.4, lit=0)
    cv.rect(608, y0 + 3, x1 - 3, 99, plaster, 4.0, lit=0)                  # la cantonada d'un armari crema
    cv.vline(608, y0 + 3, 99, plaster, 1.0, lit=0)
    cv.hline(608, x1 - 3, 99, plaster, 1.0, lit=0)
    cv.rect(612, 90, 613, 96, [(40, 44, 50), (130, 138, 150)], 1.0, lit=0)   # la nansa
    cv.vline(592, y0 + 3, 83, [(10, 6, 6), (30, 20, 16)], 1.0, lit=0)      # el fil del llum
    shade = [(588, 84), (596, 84), (600, 91), (584, 91)]
    cv.poly(shade, [(120, 60, 14), (214, 140, 40), (255, 230, 150)], 1.6, lit=0)
    cv.hline(585, 598, 91, [(255, 230, 150), (255, 246, 200)], 1.0, lit=0)
    cv.disc(592, 93, 2, 1.5, [(255, 246, 200)], 0, lit=0)
    obox(cv, 618, 116, 624, 123, [(40, 30, 40), (90, 70, 80), (150, 130, 130), (200, 180, 170)], 2.6, lit=0)   # una tassa a la lleixa
    frame(cv, x0, y0, x1, y1, DESKB, 2.6)
    outline(cv, x0, y0, x1, y1, DESKB)
    cv.glow(608, 123, 45, (240, 170, 100), 0.2)


_PROPS = {'passaplats_obert': passaplats_obert, 'caixa': caixa, 'router_connectat': router_connectat, 'fibra_connectada': fibra_connectada,
         'xarxa_connectada': xarxa_connectada, 'alimentacio_connectada': alimentacio_connectada}


def _lit_prop(fn):
    def draw(cv):
        fn(cv)
        llum.apply_cv(cv, FX_PROPS)
    return draw


PROPS = {pid: _lit_prop(fn) for pid, fn in _PROPS.items()}

# el passaplats obert deixa entrar la llum càlida de la cuina: el prop inclou la paret del voltant, tornada
# a il·luminar (fins a y=147, per sobre de la presa de fibra; el raig s'acaba abans de les vores de la caixa)
WARM_BOX = (545, 25, 639, 147)
FX_OBERT = FX_LIGHT + [llum.wash(607, 105, 60, (255, 140, 60), k=1.4, air=0.18, squash=1.4, power=1.1)] + FX[len(FX_LIGHT):]


def _passaplats_obert_llum(cv):
    raw = _raw()
    base = llum.apply(raw, FX)
    lit = Canvas(light=LIGHT, img=raw.copy())
    passaplats_obert(lit)
    out = _diff(llum.apply(lit.img, FX_OBERT), base)
    s = out.width // W
    x0, y0, x1, y1 = (v * s for v in WARM_BOX)
    cv.img.paste(out.crop((x0, y0, x1 + s, y1 + s)), (x0, y0))
    cv.P = cv.img.load()


PROPS['passaplats_obert'] = _passaplats_obert_llum


# ─── Animacions ─────────────────────────────────────────────────────────────

def _raw():
    cv = Canvas(light=LIGHT)
    _draw(cv)
    return cv.img


def _fx_diff(img, base):
    """El fotograma (dibuixat sobre el fons cru) amb la llum, menys el fons amb la llum."""
    return _diff(llum.apply(img, FX), base)


def _base():
    return llum.apply(_raw(), FX)


def _frames():
    raw = _raw()
    base = llum.apply(raw, FX)
    frames = []
    for i in range(8):
        cv = Canvas(light=LIGHT, img=raw.copy())
        window(cv, rain=i)
        monitors(cv, i)
        desk_clutter(cv)
        frames.append(_fx_diff(cv.img, base))
    return frames


ANIMS = {'pantalles': {'frames': _frames, 'frameDuration': 200}}

# la meitat dreta del rètol de la pizzeria: encès (1) o fos (0), un fotograma per pas
NEON_SEQ = [1] * 14 + [0, 1, 0, 0, 1, 1, 0, 0, 0, 1]


def _frames_neo():
    """El rètol de neó del carrer, a la finestra: de tant en tant la meitat dreta parpelleja i es fon."""
    raw = _raw()
    base = llum.apply(raw, FX)
    cv = Canvas(light=LIGHT, img=raw.copy())
    window(cv, neon=False)
    off = _fx_diff(cv.img, base)
    on = _diff(base, base)
    return [on if k else off for k in NEON_SEQ]


# el llum del disc dur de la torre: activitat irregular (1 encès, 0 apagat)
DISK_SEQ = [1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0]


def _frames_disc():
    """El llumet ambre del disc dur de la torre, sota la taula, que parpelleja mentre l'script de l'Iri treballa."""
    raw = _raw()
    base = llum.apply(raw, FX)
    cv = Canvas(light=LIGHT, img=raw.copy())
    cv.flat(290, 180, (255, 170, 60))
    cv.flat(291, 180, (200, 110, 30))
    cv.glow(290, 180, 4, (255, 160, 60), 0.35)
    lit = _fx_diff(cv.img, base)
    dark = _diff(base, base)
    return [lit if k else dark for k in DISK_SEQ]


ANIMS['neo'] = {'frames': _frames_neo, 'frameDuration': 110}
ANIMS['disc_dur'] = {'frames': _frames_disc, 'frameDuration': 90}


GEOMETRIA = {
    'things': {
        'finestra': {'rect': (45, 40, 166, 153), 'walk': (107, 245)},
        'poster': {'rect': (196, 47, 257, 123), 'walk': (227, 245)},
        'matalas': {'rect': (16, 187, 203, 234), 'walk': (120, 248)},
        'pizzes': {'rect': (197, 195, 256, 230), 'walk': (235, 248)},
        'ordinadors': {'rect': (275, 80, 481, 155), 'walk': (360, 245)},
        'router': {'rect': (496, 133, 547, 168), 'walk': (523, 245)},
        'fibra': {'rect': (552, 144, 584, 213), 'walk': (571, 245)},
        'passaplats': {'rect': (573, 75, 635, 136), 'walk': (605, 245)},
        'caixa': {'rect': (400, 217, 456, 254), 'walk': (429, 263)},
    },
    'spawns': {'iri': (200, 256), 'diu': (349, 256)},
    # la llum de la sala sobre els personatges, en temps d'execució (la mateixa que FX_LIGHT, en més suau)
    'characterLights': {
        'ambient': '#8c84a8',                                                           # habitació fosca, lila
        'lights': [
            {'x': 377, 'y': 118, 'radius': 260, 'color': '#50e6d2', 'intensity': 0.9},  # les pantalles
            {'x': 105, 'y': 110, 'radius': 220, 'color': '#be6eff', 'intensity': 0.8},  # la finestra
            {'x': 607, 'y': 105, 'radius': 170, 'color': '#ff8c3c', 'intensity': 1.3,
             'whenPropVisible': 'passaplats_obert'},                                     # la cuina, si és obert
        ],
    },
    'walkable': [(19, 236), (621, 236), (632, 271), (8, 271)],
}
