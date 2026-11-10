"""
Proposta B: l'estudi de l'Iri **sense caricatura**, amb to urbà de hacker i d'espies.

La mateixa habitació i la mateixa disposició que la proposta A (hd/rooms/pis_estudi.py), però:
  - **escala real** dels mobles, per a personatges de ≈83 px (escriptori a l'altura del maluc);
  - **paleta freda i apagada**: maó pintat de gris blavós, negres, i la llum ve de les pantalles (cian) i
    del neó del carrer (magenta), que entra per les **persianes** i pinta franges a la paret;
  - pluja al vidre, i contorns només on cal (com a Ferro-9).
"""
import math

from hd.pix import Light, Canvas, W, H, hr
from hd.rooms.pis_estudi import (obox, outline, cable, _diff, PLASTIC, SCREEN, SKY, CITY, NEON, SHEET, GRAYC, YEL, CARD)

BRICK = [(10, 12, 18), (16, 20, 28), (24, 28, 38), (32, 38, 50), (42, 50, 64), (54, 64, 80), (70, 82, 98), (90, 104, 120)]
MORTAR = [(8, 10, 14), (14, 16, 22), (20, 24, 30), (28, 32, 40), (38, 42, 50)]
FLOORB = [(8, 8, 12), (14, 14, 20), (22, 22, 30), (32, 30, 40), (44, 42, 52), (58, 56, 66), (76, 72, 82)]
DESKB = [(6, 6, 10), (12, 12, 18), (20, 20, 28), (30, 30, 40), (42, 42, 54), (58, 58, 72), (78, 78, 92)]
STEELB = [(10, 12, 16), (20, 24, 30), (34, 38, 46), (50, 56, 66), (70, 78, 90), (96, 104, 116), (130, 138, 150)]
MAGENTA = [(30, 6, 30), (60, 12, 56), (100, 20, 90), (150, 34, 130), (200, 60, 170), (240, 110, 210)]
CYANL = [(4, 20, 26), (8, 40, 50), (14, 70, 84), (24, 110, 124), (50, 160, 170), (120, 220, 220)]
FABRICB = [(8, 10, 16), (14, 18, 26), (22, 28, 38), (32, 40, 52), (46, 56, 70), (64, 76, 92)]
WARMB = [(30, 16, 10), (70, 36, 16), (120, 66, 26), (170, 104, 40), (210, 150, 70), (240, 200, 130)]

FLOOR_Y = 150
DESK_Y = 116   # escala real: el taulell a l'altura del maluc d'una persona de ≈83 px

LIGHT = Light(ambient=-0.6, vignette=(70, 40), floor_fade=(190, 26))
LIGHT.point(283, 92, r=170, k=3.0, squash=1.2, power=1.6)        # monitors
LIGHT.point(455, 80, r=70, k=1.4, squash=1.0, power=2.0)         # passaplats (cuina): poca llum
LIGHT.point(79, 72, r=70, k=0.8, squash=0.9, power=2.0)          # finestra


def stripes(x, y):
    """Les franges de neó que la persiana projecta a la paret (en diagonal, cap a la dreta)."""
    if y > FLOOR_Y + 14 or y < 10:
        return 0.0
    u = x - 130 - (y - 30) * 0.9
    if not 0 <= u < 150:
        return 0.0
    edge = min(1.0, u / 30, (150 - u) / 30)          # s'esvaeix als extrems del raig
    fade = 1.0 if y <= FLOOR_Y else 1 - (y - FLOOR_Y) / 14
    return (1.0 if int(u) % 12 < 6 else 0.0) * edge * fade


def wall(cv):
    # maó pintat de gris blavós, gastat
    for y in range(0, FLOOR_Y):
        row = y // 7
        for x in range(W):
            off = 9 if row % 2 else 0
            if y % 7 == 6 or (x + off) % 18 == 0:
                cv.put(x, y, MORTAR, 2.2)
            else:
                cv.put(x, y, BRICK, 2.6 + (hr((x + off) // 18, row) - 0.5) * 0.8 + (hr(x // 2, y // 2) - 0.5) * 0.3)
    cv.rect(0, FLOOR_Y - 5, W - 1, FLOOR_Y - 1, DESKB, 2.4)
    cv.hline(0, W - 1, FLOOR_Y, DESKB, 0)


def neon_stripes(cv, k=1.0):
    """Franges magenta damunt de tot el que hi ha a la paret."""
    cv.tint(0, 0, W - 1, FLOOR_Y + 14, (210, 60, 170), lambda x, y: 0.13 * k * stripes(x, y))


def floor(cv):
    # tarima fosca de laminat, amb la llum de les pantalles reflectida
    for y in range(FLOOR_Y + 1, H):
        dep = (y - FLOOR_Y) / (H - FLOOR_Y)
        for x in range(W):
            u = (x - W / 2) / (1 + dep * 0.5) + W / 2
            plank = math.floor(u / 30)
            lvl = 2.4 + (hr(plank, 3) - 0.5) * 0.6
            if (u % 30) < 1:
                lvl = 0.8
            cv.put(x, y, FLOORB, lvl)
    # reflex de les pantalles al terra
    cv.tint(200, FLOOR_Y + 12, 370, 200, (60, 180, 170), lambda x, y: 0.18 * max(0, 1 - abs(x - 283) / 90) * max(0, 1 - (y - 162) / 40))


def window(cv, rain=0):
    x0, y0, x1, y1 = 34, 30, 124, 112
    for y in range(y0 + 3, y1 - 2):
        for x in range(x0 + 3, x1 - 2):
            cv.put(x, y, SKY, 0.6 + (y - y0) / 40, lit=0)
    for i, (bx, bw, bh) in enumerate(((37, 14, 56), (52, 10, 66), (63, 18, 46), (82, 12, 62), (95, 16, 40), (110, 12, 56))):
        top = y1 - 3 - bh
        cv.rect(bx, top, bx + bw, y1 - 3, CITY, 1.0, lit=0)
        for wy in range(top + 3, y1 - 6, 5):
            for wx in range(bx + 2, bx + bw - 1, 4):
                if hr(wx, wy, i) > 0.7:
                    cv.flat(wx, wy, (120, 190, 220) if hr(wy, wx) > 0.5 else (200, 150, 90))
    # el neó del carrer (letres de la pizzeria, en magenta)
    for j in range(5):
        for x in (68, 70, 72, 76, 80, 82, 84, 88, 90, 92):
            if hr(x, j) > 0.35:
                cv.put(x, 84 + j, NEON, 3.6, lit=0)
    cv.glow(80, 86, 18, (255, 90, 200), 0.4)
    # pluja: regalims al vidre
    for i in range(26):
        rx = x0 + 4 + int(hr(i, 9) * (x1 - x0 - 8))
        ry = y0 + 4 + int((hr(i, 3) * (y1 - y0) + rain * 7 + i * 3) % (y1 - y0 - 10))
        for d in range(3 + int(hr(i, 5) * 4)):
            cv.tint(rx, ry + d, rx, ry + d, (170, 200, 230), 0.45)
    # persiana mig abaixada: llistons horitzontals
    for y in range(y0 + 2, 72, 4):
        cv.hline(x0 + 2, x1 - 2, y, STEELB, 3.4)
        cv.hline(x0 + 2, x1 - 2, y + 1, STEELB, 2.2)
    cv.line(x0 + 18, y0 + 2, x0 + 18, 76, STEELB, 1.6)
    # marc d'alumini
    for (a, b, c, d) in ((x0, y0, x1, y0 + 2), (x0, y1 - 2, x1, y1), (x0, y0, x0 + 2, y1), (x1 - 2, y0, x1, y1)):
        cv.rect(a, b, c, d, STEELB, 3.0)
    cv.rect((x0 + x1) // 2 - 1, y0, (x0 + x1) // 2 + 1, y1, STEELB, 2.6)
    cv.rect(x0 - 4, y1, x1 + 4, y1 + 3, STEELB, 3.2)


def mattress(cv):
    cv.poly([(18, 152), (146, 152), (152, 170), (12, 170)], SHEET, lambda x, y: 1.6 + (0.6 if y < 155 else 0))
    cv.rect(12, 170, 152, 175, SHEET, 0.8)
    cv.poly([(16, 146), (80, 140), (148, 150), (152, 166), (60, 168), (14, 166)], FABRICB,
            lambda x, y: 2.2 + 0.9 * math.sin(x / 7 + y / 4) + (0.8 if y < 147 else 0))
    cv.disc(32, 147, 16, 6, SHEET, lambda nx, ny: 2.4 - ny * 1.2)


def wall_map(cv):
    """Un mapa del centre de Ginebra clavat a la paret amb xinxetes i fils vermells: estil espia."""
    x0, y0, x1, y1 = 146, 30, 196, 92
    cv.rect(x0, y0, x1, y1, SHEET, 2.2)
    for i in range(14):
        a, b = hr(i, 1), hr(i, 2)
        cv.line(x0 + 2 + a * 46, y0 + 2, x0 + 2 + b * 46, y1 - 2, GRAYC, 2.4)
    cv.line(x0 + 2, y0 + 30, x1 - 2, y0 + 26, [(40, 40, 60), (70, 90, 140), (100, 130, 190)], 2.0)  # el llac
    pins = ((156, 44), (184, 52), (170, 74), (162, 62))
    for (ax, ay), (bx, by) in zip(pins, pins[1:]):
        cv.line(ax, ay, bx, by, [(60, 6, 10), (150, 20, 26), (220, 40, 40)], 2.0, lit=0)
    for px, py in pins:
        cv.disc(px, py, 1.6, 1.6, [(60, 6, 10), (150, 20, 26), (230, 60, 50)], 2.0, lit=0)
    cv.rect(178, 40, 192, 48, SHEET, 3.2)                                          # foto de la seu del BCMU
    cv.rect(180, 42, 190, 47, GRAYC, 2.2)
    outline(cv, x0, y0, x1, y1, SHEET)


def desk(cv):
    # escriptori d'acer i fusta fosca, a escala real
    obox(cv, 196, DESK_Y, 368, DESK_Y + 4, DESKB, 3.0, top=1.2)
    for x in (200, 362):
        cv.rect(x, DESK_Y + 4, x + 3, 166, STEELB, 2.4)
    cv.line(203, 150, 360, 150, STEELB, 1.8)
    # torre del PC sota la taula, amb llums
    obox(cv, 214, 128, 236, 166, PLASTIC, 2.0)
    cv.vline(232, 132, 160, CYANL, 4.0, lit=0)
    cv.glow(232, 146, 10, (60, 200, 210), 0.25)
    # cadira de malla
    cv.disc(300, 152, 20, 5, PLASTIC, lambda nx, ny: 1.8 - ny * 0.6)
    cv.rect(297, 157, 303, 170, STEELB, 2.0)
    for dx in (-14, -6, 6, 14):
        cv.line(300, 170, 300 + dx, 176, STEELB, 2.0)
    cv.poly([(284, 104), (316, 104), (319, 146), (281, 146)], PLASTIC, lambda x, y: 1.6 + (0.6 if (x + y) % 3 == 0 else 0))
    outline(cv, 281, 104, 319, 146, PLASTIC)


def monitors(cv, frame=0):
    specs = ((206, 74, 246, 110), (252, 60, 314, 110), (320, 74, 360, 110))
    for n, (x0, y0, x1, y1) in enumerate(specs):
        obox(cv, x0, y0, x1, y1, PLASTIC, 1.6)
        sx0, sy0, sx1, sy1 = x0 + 2, y0 + 2, x1 - 2, y1 - 3
        for y in range(sy0, sy1 + 1):
            for x in range(sx0, sx1 + 1):
                cv.put(x, y, SCREEN, 1.2 + (0.25 if (y + frame) % 2 == 0 else 0), lit=0)
        for row in range(sy0 + 1, sy1, 3):
            seed = (row - sy0) // 3 + frame + n * 7
            indent = int(hr(seed, 1) * 3) * 3
            length = int(4 + hr(seed, 2) * (sx1 - sx0 - 10))
            for x in range(sx0 + 2 + indent, min(sx1 - 1, sx0 + 2 + indent + length)):
                if hr(x // 3, seed) > 0.25:
                    cv.put(x, row, SCREEN, 4.2 if n != 1 or row % 9 else 5.2, lit=0)
        mx = (x0 + x1) // 2
        cv.rect(mx - 1, y1, mx + 1, DESK_Y, STEELB, 2.4)
        cv.rect(mx - 7, DESK_Y - 1, mx + 7, DESK_Y, STEELB, 3.0)
    # el mapa de xarxa del BCMU a la del mig: nodes i línies
    nodes = ((262, 70), (284, 66), (302, 74), (272, 88), (296, 92), (284, 100))
    for (ax, ay), (bx, by) in ((nodes[0], nodes[1]), (nodes[1], nodes[2]), (nodes[0], nodes[3]), (nodes[3], nodes[4]),
                               (nodes[2], nodes[4]), (nodes[4], nodes[5]), (nodes[3], nodes[5])):
        cv.line(ax, ay, bx, by, SCREEN, 3.4, lit=0)
    for i, (x, y) in enumerate(nodes):
        cv.disc(x, y, 2, 2, [(60, 6, 10), (150, 20, 26), (240, 70, 60), (255, 160, 140)] if i == 5 else SCREEN, 3.0 if i == 5 else 5.0, lit=0)
    cv.glow(283, 88, 70, (60, 200, 190), 0.14)


def desk_clutter(cv):
    obox(cv, 258, DESK_Y - 3, 300, DESK_Y, PLASTIC, 2.0)
    for x in range(260, 299, 3):
        cv.hline(x, x + 1, DESK_Y - 2, CYANL, 2.6, lit=0)                       # teclat retroil·luminat
    cv.disc(310, DESK_Y - 1, 3, 1.4, PLASTIC, 2.0)
    for x in (222, 228):
        obox(cv, x, DESK_Y - 11, x + 4, DESK_Y, GRAYC, 2.6)
    obox(cv, 340, DESK_Y - 12, 352, DESK_Y, PLASTIC, 1.8)                        # un portàtil vell, tancat, de cantell
    cv.rect(342, DESK_Y - 8, 350, DESK_Y - 7, MAGENTA, 3.0, lit=0)               # adhesiu


def router_shelf(cv):
    obox(cv, 372, 126, 410, 160, STEELB, 2.0)                                     # moble d'acer d'oficina
    cv.hline(373, 409, 142, STEELB, 0.6)
    cv.rect(386, 133, 396, 134, STEELB, 3.4)
    cv.rect(386, 149, 396, 150, STEELB, 3.4)
    obox(cv, 376, 114, 406, 125, PLASTIC, 1.8, top=1.2)
    cv.line(380, 114, 377, 102, PLASTIC, 2.2)
    cv.line(402, 114, 405, 102, PLASTIC, 2.2)
    for x in (385, 391, 397):
        cv.rect(x, 120, x + 3, 123, PLASTIC, 0.4)
        cv.flat(x + 1, 117, (90, 30, 30))
    obox(cv, 420, 112, 430, 126, SHEET, 2.4)
    cv.rect(423, 117, 427, 121, PLASTIC, 1.0)
    cable(cv, [(425, 126), (432, 150), (418, 158), (414, 140)], [(10, 10, 20), (180, 140, 20), (232, 196, 50), (252, 236, 130)], 1.4, thick=2)


def hatch(cv):
    x0, y0, x1, y1 = 436, 58, 474, 100
    for y in range(y0 + 3, y1 - 2):
        for x in range(x0 + 3, x1 - 2):
            cv.put(x, y, WARMB, 2.0 + (y - y0) / 40, lit=0)
    cv.rect(x0 + 3, 80, x1 - 3, 82, WARMB, 1.0, lit=0)
    for (a, b, c, d) in ((x0, y0, x1, y0 + 2), (x0, y1 - 2, x1, y1), (x0, y0, x0 + 2, y1), (x1 - 2, y0, x1, y1)):
        cv.rect(a, b, c, d, DESKB, 2.6)
    cv.glow(456, 90, 30, (240, 170, 100), 0.12)


def pizza_stack(cv):
    for i, (x0, y0, dx) in enumerate(((150, 166, 0), (152, 160, 3), (148, 154, -2), (151, 148, 2))):
        cv.poly([(x0 + dx, y0), (x0 + dx + 38, y0), (x0 + 38, y0 + 6), (x0, y0 + 6)], CARD, 2.0 - (i % 2) * 0.4)
        cv.hline(x0, x0 + 38, y0 + 6, CARD, 0)


def floor_cables(cv):
    cable(cv, [(240, 162), (250, 190), (330, 176), (380, 196), (420, 168), (400, 160)], [(4, 4, 8), (20, 20, 28), (40, 40, 52), (70, 70, 84)], 1.6, thick=2)
    cable(cv, [(232, 160), (200, 200), (120, 180), (60, 194)], [(4, 4, 8), (20, 40, 70), (40, 80, 130), (80, 130, 180)], 1.6, thick=2)
    cable(cv, [(366, 160), (380, 182), (440, 186), (466, 160)], [(4, 4, 8), (80, 20, 24), (130, 36, 40), (180, 80, 80)], 1.6, thick=1)


def bg(cv):
    wall(cv)
    floor(cv)
    window(cv)
    wall_map(cv)
    neon_stripes(cv)
    mattress(cv)
    pizza_stack(cv)
    desk(cv)
    monitors(cv, 0)
    desk_clutter(cv)
    router_shelf(cv)
    hatch(cv)
    floor_cables(cv)
    cv.darken(196, 160, 368, 166, 0.5)
    cv.darken(372, 158, 412, 164, 0.4)


def caixa(cv):
    x0, y0, x1, y1 = 300, 172, 338, 190
    cv.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], CARD, lambda x, y: 2.2 - (0.8 if x > x1 - 8 else 0))
    cv.poly([(x0, y0), (x0 + 6, y0 - 9), (x0 + 16, y0 - 7), (x0 + 12, y0)], CARD, 2.8)
    cv.rect(x0 + 2, y0 + 1, x1 - 2, y0 + 3, CARD, 0.6)
    cv.rect(x0 + 8, y0 + 8, x0 + 22, y0 + 12, SHEET, 2.6)
    cv.darken(x0 - 2, y1, x1 + 3, y1 + 2, 0.5)


def router_connectat(cv):
    for x in (385, 391, 397):
        cv.flat(x + 1, 117, (120, 255, 150))
    cv.glow(392, 117, 10, (120, 255, 160), 0.4)


PROPS = {'caixa': caixa, 'router_connectat': router_connectat}


def _frames():
    base = Canvas(light=LIGHT)
    bg(base)
    frames = []
    for i in range(8):
        cv = Canvas(light=LIGHT, img=base.img.copy())
        window(cv, rain=i)
        monitors(cv, i)
        desk_clutter(cv)
        frames.append(_diff(cv.img, base.img))
    return frames


ANIMS = {'pantalles': {'frames': _frames, 'frameDuration': 200}}
