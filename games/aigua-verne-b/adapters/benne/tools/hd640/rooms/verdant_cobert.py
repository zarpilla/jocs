"""
Aigua Verne — `verdant_cobert` (P, de prop: persones de ≈100 px). Escena 5.

El cobert d'en Nil, el jardiner: l'únic lloc de Verdant que és vell i humà. Taulons de fusta amb escletxes per on
entra el sol de catàleg, bigues, una bombeta que penja. A l'esquerra, la **porta** oberta al jardí de plàstic (tot
massa verd, massa blau). Les **eines** penjades a la paret (rascle, pala, aixada, tisores, serra, la mànega dels
aspersors), un prestatge amb testos i pots de llavors, el banc de treball amb una ràdio vella i el calendari; el
tamboret. Els **sacs d'adob de plàstic** (lluents, de colors de llaminadura: ningú sap per a què serveixen) i, al
racó, darrere, amagada sota el raig de llum de la finestra, **la tomaquera**: de debò, en un test, mig seca.

Props: `galleda` (la galleda de zinc d'en Nil, a terra: fins que s'agafa). Decorats: `reg_muntat` (la galleda penjada
a la paret, i el reg gota a gota del pare fins al test) i `tomaquera_viva` (verda i amb tomàquets).
ANIMS: `pols` (la pols que balla al raig de llum).
"""
import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

import math

from hd.pix import Canvas, Light, W, H, hr, mix
from hd.rooms.arenga import box
from hd.rooms.comu import _diff, text
from hd.rooms.exterior import fbm
from hd640.rooms.verdant_comu import (SKYV, TURF, WHITEV, GOLDV, GLASSV, MAGENTA, CYANF, YELLOWF, ORANGEF,
                                      PLANK, WOODG, ZINC, TERRACOTA, LEAF, DRYLEAF, TOMATO, BLACKT, HOSE, RUSTV,
                                      flor, ombra, galleda)

RH = 260
FLOOR_Y = 214                 # on la paret del fons es troba amb el terra
BEAM_Y = 26                   # el tirant de la teulada
BULB = (300, 52)
DOOR = (24, 88, 94, FLOOR_Y)
WIN = (414, 54, 474, 108)
POT = (560, 222)              # el test de la tomaquera: centre de la base
GALLEDA = (262, 244)
EARTH = [(26, 18, 14), (44, 32, 22), (64, 48, 32), (86, 66, 44), (110, 86, 58), (136, 110, 76), (164, 138, 100)]

LIGHT = Light(ambient=0.2, vignette=(70, 26), floor_fade=None)
LIGHT.point(BULB[0], BULB[1] + 6, r=250, k=1.7, squash=1.1, power=1.5)        # la bombeta
LIGHT.point(70, 190, r=170, k=1.9, squash=0.8, power=1.4)                     # la porta oberta al jardí
LIGHT.point(560, 170, r=120, k=1.3, squash=0.9, power=1.6)                    # el raig de la finestra al racó


def _in_beam(x, y):
    """El raig de llum de la finestra: de la finestra cap avall i a la dreta, fins al racó de la tomaquera."""
    t = (y - WIN[3]) / (226 - WIN[3])
    if t < 0 or t > 1:
        return 0.0
    a = WIN[0] + 4 + (516 - WIN[0]) * t
    b = WIN[2] + (606 - WIN[2]) * t
    if a <= x <= b:
        return 1.0 - abs((x - a) / (b - a) - 0.5) * 1.2
    return 0.0


# ─── Parets, bigues i terra ────────────────────────────────────────────────

def paret(cv):
    """Taulons verticals vells, amb nusos, taques i escletxes per on entra la llum de fora."""
    for y in range(0, FLOOR_Y):
        for x in range(W):
            col = x // 13
            u = (x % 13) / 12
            lvl = 2.6 + (hr(col, 1) - 0.5) * 0.8 + (fbm(x / 3, y / 40, 101 + col) - 0.5) * 1.0 - u * 0.4
            if x % 13 == 0:
                if hr(col, y // 26, 5) > 0.94 and y % 26 < 5 and y > BEAM_Y + 12:
                    cv.flat(x, y, (236, 230, 200) if y % 26 in (1, 2, 3) else (150, 130, 96))   # l'escletxa: el sol de fora
                    continue
                lvl = 0.6
            elif x % 13 == 1:
                lvl += 0.8
            # un nus
            nx, ny = (x % 13) - 6, (y + col * 37) % 71 - 35
            if nx * nx + ny * ny * 0.3 < 5 and hr(col, (y + col * 37) // 71, 7) > 0.6:
                lvl -= 1.0
            cv.put(x, y, PLANK, lvl)
    # el sòcol, podrit i fosc
    cv.rect(0, FLOOR_Y - 8, W - 1, FLOOR_Y - 1, PLANK, lambda x, y: 1.6 + (hr(x // 13, 2) - 0.5) * 0.6 +
            (0.8 if y == FLOOR_Y - 8 else 0))
    # el racó de la dreta, en perspectiva (la paret del costat, més fosca)
    cv.poly([(612, 0), (W, 0), (W, RH), (626, FLOOR_Y + 4), (612, FLOOR_Y)], PLANK,
            lambda x, y: 1.6 + (0.6 if (x - 612) % 9 == 0 else 0) + (fbm(x / 4, y / 30, 113) - 0.5) * 0.8)
    cv.vline(612, 0, FLOOR_Y, PLANK, 0.4)


def sostre(cv):
    """La teulada per sota: taulons inclinats, dues bigues i el tirant; teranyines."""
    for y in range(0, BEAM_Y):
        for x in range(W):
            lvl = 1.2 + (y / BEAM_Y) * 0.8 + (fbm(x / 30, y / 2, 121) - 0.5) * 0.6 - (0.8 if (x + y * 3) % 22 == 0 else 0)
            cv.put(x, y, PLANK, lvl)
    for bx in (150, 470):                                             # les bigues inclinades
        for k in range(8):
            cv.line(bx - 60 + k, 0, bx + k, BEAM_Y, PLANK, 3.0 - k * 0.15 + (0.8 if k == 0 else 0))
    cv.rect(0, BEAM_Y, W - 1, BEAM_Y + 9, PLANK, lambda x, y: 3.6 - (y - BEAM_Y) * 0.25 +
            (fbm(x / 20, y / 3, 123) - 0.5) * 0.8)
    cv.hline(0, W - 1, BEAM_Y, PLANK, 4.8)
    cv.hline(0, W - 1, BEAM_Y + 10, PLANK, 0.6)
    # una teranyina al racó
    for k in range(6):
        a = math.pi / 2 * k / 5
        cv.line(612, BEAM_Y + 10, 612 - math.cos(a) * 22, BEAM_Y + 10 + math.sin(a) * 22, WOODG, 4.4)
    for r in (8, 14, 20):
        for k in range(10):
            a = math.pi / 2 * k / 9
            cv.put(612 - math.cos(a) * r, BEAM_Y + 10 + math.sin(a) * r, WOODG, 4.0)


def terra(cv):
    """Terra de terra piconada, serradures, fulles seques; la llum de la porta hi fa una catifa."""
    for y in range(FLOOR_Y, RH):
        t = (y - FLOOR_Y) / (RH - FLOOR_Y)
        for x in range(W):
            if x > 612 + (y - FLOOR_Y) * 0.95 and y < FLOOR_Y + 4:
                continue
            lvl = 3.0 - t * 0.3 + (fbm(x / 18, y / 5, 131) - 0.5) * 1.2
            if hr(x, y, 133) > 0.93:
                lvl += 1.0                                             # serradures
            cv.put(x, y, EARTH, lvl)
    for i in range(26):                                                # fulles seques
        x, y = 40 + hr(i, 1) * 560, FLOOR_Y + 4 + hr(i, 2) * 40
        cv.disc(x, y, 2.4, 1.2, [(60, 40, 18), (110, 76, 30), (160, 116, 52), (196, 156, 84)],
                lambda nx, ny: 2.0 - nx * 0.6)
    # la catifa de llum de la porta (fora fa un sol d'anunci)
    cv.tint(DOOR[0], FLOOR_Y, 200, RH - 1, (255, 250, 214),
            lambda x, y: 0.42 if DOOR[0] - (y - FLOOR_Y) * 0.4 <= x <= DOOR[2] + (y - FLOOR_Y) * 1.7 and
            (x + y) % 2 == 0 else 0)


# ─── La porta ──────────────────────────────────────────────────────────────

def porta(cv):
    """La porta oberta: a fora, el jardí de plàstic (gespa a franges, cel blau, la façana blanca)."""
    x0, y0, x1, y1 = DOOR
    hz = 168
    for y in range(y0, y1):
        for x in range(x0, x1 + 1):
            if y < hz - 14:
                cv.put(x, y, SKYV, 4.4 + (y - y0) / 40, lit=0)
            elif y < hz:
                cv.put(x, y, TURF, 3.6 + (hr(x // 2, y // 2, 5) - 0.5) * 0.6, lit=0)   # la bardissa
            else:
                band = int(math.floor(math.atan2(x - 70, y - 120) * 9 + 50)) % 2
                cv.put(x, y, TURF, 4.6 + (0.8 if band else 0), lit=0)
    # un tros de la residència, blanca, i una flor magenta que es veu des d'aquí
    cv.rect(x0, y0 + 10, x0 + 22, hz - 1, WHITEV, lambda x, y: 5.2 - (0.8 if (y - y0) % 10 == 0 else 0), lit=0)
    cv.rect(x0 + 6, y0 + 28, x0 + 16, y0 + 50, GLASSV, 4.0, lit=0)
    cv.hline(x0, x0 + 22, y0 + 10, GOLDV, 5.0, lit=0)
    for fx, fy, ramp in ((60, 186, MAGENTA), (74, 192, CYANF), (48, 196, YELLOWF), (84, 182, MAGENTA)):
        cv.vline(fx, fy, fy + 5, TURF, 3.0, lit=0)
        flor(cv, fx, fy, ramp, size=2, lit=0)
    cv.glow(60, 150, 50, (255, 255, 240), 0.25)
    # el marc de fusta
    for x in (x0 - 5, x0 - 4, x0 - 3, x0 - 2, x0 - 1):
        cv.vline(x, y0 - 5, y1, PLANK, 3.6 - (x0 - x) * 0.3)
    for x in range(x1 + 1, x1 + 6):
        cv.vline(x, y0 - 5, y1, PLANK, 3.0 - (x - x1) * 0.2)
    cv.rect(x0 - 5, y0 - 6, x1 + 5, y0 - 1, PLANK, lambda x, y: 4.2 - (y - y0 + 6) * 0.2)
    cv.rect(x0 - 2, y1, x1 + 2, y1 + 3, PLANK, 3.4)                   # el llindar
    # la fulla, oberta cap endins (de cantó, contra les eines)
    lx = x1 + 30
    cv.poly([(x1 + 5, y0 - 2), (lx, y0 + 6), (lx, y1 + 10), (x1 + 5, y1 + 1)], PLANK,
            lambda x, y: 2.6 + (x - x1) * 0.02 - (1.2 if (y - y0) % 14 == 0 else 0) + (fbm(x / 4, y / 20, 141) - 0.5))
    cv.vline(lx, y0 + 6, y1 + 10, PLANK, 1.4)
    for yy in (y0 + 22, y1 - 22):
        cv.line(x1 + 6, yy, lx - 1, yy + 6, PLANK, 3.8)
    for yy in (y0 + 12, y1 - 14):
        cv.rect(x1 + 2, yy, x1 + 8, yy + 3, RUSTV, 2.8)               # les frontisses
    cv.disc(lx - 6, 160, 2, 2, RUSTV, 3.2)                             # el baldó


# ─── Les eines, el prestatge, el banc ──────────────────────────────────────

def eines(cv):
    """El tauler de les eines: cada una al seu clau, amb la silueta dibuixada (en Nil és endreçat)."""
    x0, y0, x1, y1 = 132, 58, 258, 196
    box(cv, x0, y0, x1, y1, PLANK, 1.9, grad=0.4)
    for y in range(y0 + 2, y1, 14):
        cv.hline(x0 + 1, x1 - 1, y, PLANK, 0.8)
    # el rascle
    cv.rect(144, 66, 145, 190, PLANK, lambda x, y: 4.6 - (x - 144) * 1.2)
    cv.rect(137, 64, 152, 66, ZINC, 3.4)
    for x in range(137, 153, 3):
        cv.vline(x, 60, 64, ZINC, 3.8)
    # la pala
    cv.rect(166, 64, 167, 160, PLANK, lambda x, y: 4.4 - (x - 166) * 1.2)
    cv.rect(162, 60, 171, 63, PLANK, 3.6)
    cv.poly([(159, 160), (174, 160), (174, 182), (166, 190), (159, 182)], ZINC,
            lambda x, y: 4.4 - (x - 159) * 0.1 + (0.6 if (x + y) % 11 == 0 else 0))
    cv.disc(163, 176, 3, 4, RUSTV, 2.6)
    # l'aixada
    cv.rect(188, 70, 189, 188, PLANK, lambda x, y: 4.2 - (x - 188) * 1.2)
    cv.poly([(180, 70), (198, 70), (196, 80), (182, 80)], ZINC, lambda x, y: 3.8 - (y - 70) * 0.1)
    # les tisores de podar, la serra i una paleta
    for k, ang in ((0, 0.45), (1, -0.45)):
        cv.line(214, 76, 214 + math.sin(ang) * 18, 96, [(70, 10, 10), (130, 30, 20), (180, 60, 40), (220, 100, 70)], 2.6)
    cv.poly([(211, 66), (217, 66), (215, 77), (213, 77)], ZINC, 4.4)
    cv.poly([(226, 108), (250, 108), (250, 120), (226, 114)], ZINC, lambda x, y: 4.2 - (y - 108) * 0.08)
    for x in range(227, 250, 2):
        cv.put(x, 115 + (x - 226) * 0.2, ZINC, 1.6)
    cv.rect(248, 104, 255, 122, PLANK, 3.4)
    cv.rect(212, 136, 214, 152, PLANK, 3.6)
    cv.poly([(208, 152), (218, 152), (216, 166), (210, 166)], ZINC, 4.0)
    # la mànega dels aspersors, enrotllada: verd de plàstic (la que només fa boira)
    for r in range(11, 5, -1):
        for a in range(0, 360, 4):
            ra = math.radians(a)
            cv.put(234 + math.cos(ra) * r * 1.1, 160 + math.sin(ra) * r, TURF, 2.6 + (11 - r) * 0.1 +
                   (1.4 if -0.8 < math.sin(ra) < -0.3 else 0))
    cv.line(240, 171, 246, 194, TURF, 3.0)
    for x, y in ((144, 62), (166, 60), (188, 68), (214, 64), (238, 104), (213, 134), (234, 148)):
        cv.flat(x, y, ZINC[5])                                           # els claus


def prestatge(cv):
    """Prestatge damunt les eines: testos de terrissa, pots de llavors amb etiqueta a mà, una ampolla d'aigua."""
    y = 48
    box(cv, 120, y, 270, y + 4, PLANK, 4.0)
    cv.hline(120, 270, y, PLANK, 5.2)
    for bx in (130, 260):
        cv.poly([(bx - 1, y + 5), (bx + 2, y + 5), (bx + 2, y + 14), (bx - 1, y + 8)], ZINC, 2.4)
    for i, x in enumerate((126, 140, 154)):                            # testos apilats
        for k in range(3 - (i % 2)):
            cv.poly([(x, y - 3 - k * 4), (x + 11, y - 3 - k * 4), (x + 9, y - k * 4), (x + 2, y - k * 4)], TERRACOTA,
                    lambda xx, yy: 3.4 - (xx - x) * 0.1)
    for i, x in enumerate((176, 190, 204, 218)):                       # pots de vidre amb llavors
        cv.rect(x, y - 14, x + 9, y - 1, GLASSV, lambda xx, yy: 3.2 - (xx - x) * 0.18)
        cv.rect(x + 1, y - 8, x + 8, y - 1, [(60, 40, 20), (100, 72, 36), (140, 108, 60), (180, 150, 96)],
                lambda xx, yy: 1.8 + hr(xx, yy, i) * 1.2)
        cv.rect(x, y - 16, x + 9, y - 15, ZINC, 3.6)
        cv.rect(x + 2, y - 12, x + 7, y - 10, [(200, 190, 160), (240, 232, 210)], 1.0)
    # l'ampolla d'aigua d'en Nil (la que fa servir per regar d'amagat), mig buida
    cv.rect(236, y - 20, 245, y - 1, GLASSV, lambda xx, yy: 3.8 - (xx - 236) * 0.2)
    cv.rect(237, y - 9, 244, y - 2, [(30, 80, 140), (60, 130, 200), (120, 190, 240)], 1.4)
    cv.rect(239, y - 24, 242, y - 21, CYANF, 2.0)
    cv.rect(237, y - 16, 244, y - 13, WHITEV, 4.0)
    cv.flat(240, y - 15, (60, 120, 220))
    cv.flat(241, y - 15, (60, 120, 220))


def banc(cv):
    """El banc de treball: la ràdio vella, una tassa, sobres de llavors; el calendari a sobre."""
    x0, x1, top = 282, 384, 158
    # el calendari: una foto de tomàquets de debò (de Terra, d'abans) i la graella del mes
    box(cv, 302, 70, 344, 124, [(160, 150, 130), (200, 192, 170), (228, 222, 204), (244, 240, 228)], 2.4)
    cv.rect(305, 73, 341, 96, [(30, 50, 20), (60, 100, 30), (90, 140, 50)], lambda x, y: 1.0 + hr(x // 3, y // 3) * 1.4)
    for tx, ty in ((314, 85), (324, 82), (333, 88), (319, 92)):
        cv.disc(tx, ty, 4, 4, TOMATO, lambda nx, ny: 3.6 - nx * 0.8 - ny * 0.8)
    for gy in range(100, 122, 4):
        for gx in range(306, 341, 5):
            cv.rect(gx, gy, gx + 3, gy + 2, [(200, 192, 170), (228, 222, 204)], 1.0)
    for gx, gy in ((311, 100), (316, 100), (321, 104), (326, 104), (331, 108)):
        cv.line(gx, gy, gx + 3, gy + 2, [(120, 20, 20), (180, 40, 30)], 1.0)   # dies ratllats
    cv.flat(323, 68, ZINC[5])
    # el sobre i les potes
    cv.rect(x0, top, x1, top + 6, PLANK, lambda x, y: 4.4 - (y - top) * 0.3)
    cv.hline(x0, x1, top, PLANK, 5.4)
    cv.hline(x0, x1, top + 7, PLANK, 0.8)
    for lx in (x0 + 4, x1 - 8):
        cv.rect(lx, top + 7, lx + 4, FLOOR_Y + 2, PLANK, lambda x, y, lx=lx: 3.2 - (x - lx) * 0.4)
    cv.rect(x0 + 8, top + 34, x1 - 8, top + 37, PLANK, 2.4)           # la lleixa de baix
    for i, x in enumerate((x0 + 14, x0 + 30, x0 + 48)):                 # testos buits a la lleixa
        cv.poly([(x, top + 22), (x + 13, top + 22), (x + 11, top + 33), (x + 2, top + 33)], TERRACOTA,
                lambda xx, yy: 3.0 - (xx - x) * 0.1)
    # la ràdio vella
    box(cv, 292, 136, 326, 157, [(40, 20, 14), (70, 36, 22), (110, 60, 36), (150, 90, 52), (190, 130, 80)], 2.6)
    for yy in range(140, 154, 2):
        cv.hline(296, 309, yy, PLANK, 4.4)
    cv.disc(318, 146, 4, 4, ZINC, lambda nx, ny: 4.0 - nx - ny)
    cv.line(322, 136, 334, 112, ZINC, 4.0)
    # la tassa i els sobres de llavors
    cv.rect(340, 148, 347, 157, WHITEV, lambda x, y: 3.6 - (x - 340) * 0.2)
    cv.ring(349, 152, 2, WHITEV, 3.0, step=30)
    for i, (sx, c) in enumerate(((354, YELLOWF), (366, ORANGEF))):
        cv.poly([(sx, 151), (sx + 10, 149), (sx + 12, 157), (sx + 1, 158)], [(140, 120, 90), (200, 180, 140), (236, 222, 190)], 1.6)
        cv.disc(sx + 6, 153, 2, 2, c, 2.6)


def tamboret(cv):
    """El tamboret d'en Nil, de tres potes, amb el seient gastat."""
    cx, sy = 334, 196
    ombra(cv, cx + 4, FLOOR_Y + 12, 16, 3, 0.7)
    for dx, x1 in ((-10, -14), (10, 14), (2, 3)):
        cv.line(cx + dx, sy + 3, cx + x1, FLOOR_Y + 12 if dx != 2 else FLOOR_Y + 6, PLANK, 3.0 if dx < 0 else 2.2)
        cv.line(cx + dx + 1, sy + 3, cx + x1 + 1, FLOOR_Y + 12 if dx != 2 else FLOOR_Y + 6, PLANK, 2.2)
    cv.hline(cx - 11, cx + 11, sy + 14, PLANK, 2.6)
    cv.disc(cx, sy + 2, 14, 3, PLANK, 2.2)
    cv.disc(cx, sy, 14, 3, PLANK, lambda nx, ny: 4.4 - ny * 0.4 + (fbm(nx * 4, ny * 2, 151) - 0.5))


# ─── La finestra, els sacs i la tomaquera ──────────────────────────────────

def finestra(cv):
    x0, y0, x1, y1 = WIN
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if y < y0 + 34:
                c = (SKYV, 5.0 + (y - y0) / 18)
            else:
                c = (TURF, 4.4 + (0.8 if ((x // 5) + (y // 3)) % 2 else 0))
            cv.put(x, y, c[0], c[1], lit=0)
    cv.rect(x0 + 34, y0 + 18, x1, y0 + 33, WHITEV, 5.4, lit=0)        # la residència, de lluny
    cv.hline(x0 + 34, x1, y0 + 18, GOLDV, 5.0, lit=0)
    # el vidre brut: taques i pols
    cv.tint(x0, y0, x1, y1, (180, 170, 140), lambda x, y: 0.15 + fbm(x / 6, y / 6, 161) * 0.35)
    for x0_, y0_, x1_, y1_ in ((x0 - 4, y0 - 4, x1 + 4, y0 - 1), (x0 - 4, y1 + 1, x1 + 6, y1 + 5),
                               (x0 - 4, y0, x0 - 1, y1), (x1 + 1, y0, x1 + 4, y1)):
        cv.rect(x0_, y0_, x1_, y1_, PLANK, 3.6)
    cv.hline(x0 - 4, x1 + 6, y1 + 1, PLANK, 4.8)
    cv.vline((x0 + x1) // 2, y0, y1, PLANK, 3.2)
    cv.hline(x0, x1, (y0 + y1) // 2, PLANK, 3.2)
    # un vidre trencat, apedaçat amb cinta
    cv.line(x0 + 4, y0 + 6, x0 + 14, y0 + 16, [(200, 196, 170), (240, 236, 210)], 1.0, lit=0)
    cv.line(x0 + 14, y0 + 4, x0 + 4, y0 + 18, [(200, 196, 170), (240, 236, 210)], 1.0, lit=0)


def raig(cv):
    """El raig de llum de la finestra, a quadres, fins al racó de la tomaquera."""
    cv.tint(WIN[0], WIN[3] + 6, 612, RH - 1, (255, 246, 210),
            lambda x, y: 0.22 * _in_beam(x, y) if (x + y) % 2 == 0 else 0.1 * _in_beam(x, y))


SACK = [MAGENTA, CYANF, YELLOWF, MAGENTA]


def sac(cv, x0, y0, w, h, ramp, label, tilt=0):
    """Un sac d'adob de plàstic lluent: cantons arrodonits, la boca cosida, l'etiqueta i la flor de plàstic."""
    for y in range(y0, y0 + h + 1):
        for x in range(x0, x0 + w + 1):
            u, v = (x - x0) / w, (y - y0) / h
            if (u < 0.06 or u > 0.94) and (v < 0.12 or v > 0.9):
                continue
            xx = x + int(tilt * (1 - v))
            lvl = 3.0 - abs(u - 0.4) * 1.6 - v * 0.4
            if 0.15 < u < 0.3 and v < 0.8:
                lvl += 1.4                                              # la brillantor del plàstic
            cv.put(xx, y, ramp, lvl)
    cv.hline(x0 + 2 + tilt, x0 + w - 2 + tilt, y0 + 2, ramp, 1.2)        # la costura de dalt
    for x in range(x0 + 3, x0 + w - 2, 3):
        cv.put(x + tilt, y0 + 3, ramp, 4.2)
    lx0, ly0 = x0 + w // 2 - 16, y0 + h // 2 - 8
    cv.rect(lx0 + tilt // 2, ly0, lx0 + 32 + tilt // 2, ly0 + 15, WHITEV, 4.8)
    text(cv, label, lx0 + 3 + tilt // 2, ly0 + 2, None, 0, flat=(40, 40, 60))
    flor(cv, lx0 + 26 + tilt // 2, ly0 + 4, ramp, size=2)
    text(cv, 'PLÀSTIC', lx0 + 3 + tilt // 2, ly0 + 9, None, 0, flat=(200, 40, 120))


def sacs(cv):
    ombra(cv, 450, 223, 62, 5, 0.75)
    sac(cv, 394, 186, 54, 36, CYANF, 'ADOB')
    sac(cv, 446, 184, 56, 38, MAGENTA, 'ADOB')
    sac(cv, 410, 152, 54, 34, YELLOWF, 'ADOB', tilt=3)
    sac(cv, 470, 150, 40, 36, MAGENTA, 'ADOB', tilt=-2)


def test(cv):
    """El test de terrissa, esquerdat, amb terra seca i les canyes."""
    cx, by = POT
    for y in range(by - 26, by + 1):
        t = (y - by + 26) / 26
        hw = 18 - t * 4
        for x in range(int(cx - hw), int(cx + hw) + 1):
            u = (x - cx) / hw
            lvl = 3.6 - u * 1.4 - u * u * 0.6 + (0.8 if y < by - 21 else 0) - (1.2 if y == by - 21 else 0)
            cv.put(x, y, TERRACOTA, lvl)
    cv.disc(cx, by - 26, 18, 3.4, TERRACOTA, lambda nx, ny: 4.6 if ny < 0 else 2.0)
    cv.disc(cx, by - 25.5, 15.5, 2.4, EARTH, lambda nx, ny: 1.4 + (hr(int(nx * 9), int(ny * 3)) - 0.5) * 1.4)
    cv.line(cx + 6, by - 20, cx + 9, by - 8, TERRACOTA, 1.2)            # l'esquerda
    cv.line(cx + 9, by - 8, cx + 7, by - 2, TERRACOTA, 1.2)
    ombra(cv, cx + 8, by + 2, 22, 3, 0.7)
    # les canyes, lligades amb cordill
    for x0, x1 in ((cx - 7, cx - 3), (cx + 7, cx + 4)):
        cv.line(x0, by - 26, x1, 98, [(70, 60, 26), (120, 104, 50), (160, 146, 84), (190, 178, 120)], 1.6)
        cv.line(x0 + 1, by - 26, x1 + 1, 98, [(70, 60, 26), (120, 104, 50), (160, 146, 84)], 0.8)


def mata_seca(cv):
    """La tomaquera mig seca: tiges que s'arrosseguen per les canyes, fulles marrons arrugades que pengen,
    unes quantes de groguenques, dues de verdes a baix i un sol tomàquet verd. Encara viu."""
    cx, by = POT
    stem = [(cx, by - 26), (cx + 1, by - 50), (cx - 3, by - 76), (cx + 1, by - 100), (cx - 2, by - 114)]
    for (xa, ya), (xb, yb) in zip(stem, stem[1:]):
        cv.line(xa, ya, xb, yb, DRYLEAF, 2.4)
        cv.line(xa + 1, ya, xb + 1, yb, DRYLEAF, 1.4)
    for k in range(13):
        sy = by - 34 - k * 6.4
        side = -1 if k % 2 else 1
        ln = 12 + hr(k, 3) * 8 - k * 0.3
        sx = cx + (hr(k, 4) - 0.5) * 2
        ex, ey = sx + side * ln, sy + 5 + ln * 0.5                       # les branquetes pengen
        cv.line(sx, sy, ex, ey, DRYLEAF, 2.0)
        if k < 3:
            ramp, lv = LEAF, 2.6                                         # les verdes, a baix
        elif k < 6:
            ramp, lv = [(60, 54, 14), (100, 92, 24), (146, 134, 40), (186, 170, 66), (214, 200, 100)], 2.2
        else:
            ramp, lv = DRYLEAF, 2.0
        for j in range(3):
            t = 0.35 + j * 0.3
            lx, ly = sx + (ex - sx) * t, sy + (ey - sy) * t
            for q in range(4):                                           # cada fulla, una tira arrugada que penja
                cv.put(lx + side * (q % 2), ly + 1 + q, ramp, lv + 0.8 - q * 0.4 + (hr(k, j, q) - 0.5))
                cv.put(lx + side * (q % 2) + 1, ly + 1 + q, ramp, lv - q * 0.4)
            cv.put(lx - side, ly + 2, ramp, lv - 0.6)
    # fulles seques caigudes a terra i al test
    for i in range(9):
        cv.disc(cx - 24 + hr(i, 9) * 48, by + 1 + hr(i, 8) * 5, 2.4, 1.2, DRYLEAF, 2.6 + hr(i, 7))
    cv.disc(cx + 5, by - 58, 2.6, 3, LEAF, lambda nx, ny: 3.4 - nx - ny)  # un tomàquet verd, petit, l'únic
    cv.flat(cx + 4, by - 61, LEAF[5])


# ─── Muntatge ───────────────────────────────────────────────────────────────

def bombeta(cv):
    x, y = BULB
    cv.vline(x, BEAM_Y + 10, y - 5, BLACKT, 2.0)
    cv.rect(x - 2, y - 5, x + 2, y - 2, ZINC, 2.6)
    cv.disc(x, y + 1, 3.5, 4, [(200, 160, 80), (250, 220, 140), (255, 246, 210), (255, 255, 240)],
            lambda nx, ny: 2.6 - ny * 0.6, lit=0)


def bg(cv):
    paret(cv)
    sostre(cv)
    terra(cv)
    porta(cv)
    prestatge(cv)
    eines(cv)
    banc(cv)
    finestra(cv)
    tamboret(cv)
    test(cv)
    mata_seca(cv)
    sacs(cv)
    raig(cv)
    bombeta(cv)
    cv.glow(BULB[0], BULB[1] + 1, 40, (255, 220, 150), 0.45)
    cv.darken(0, FLOOR_Y, W - 1, FLOOR_Y + 3, lambda x, y: 0.6 - (y - FLOOR_Y) * 0.18)
    for y in range(RH, H):
        for x in range(W):
            cv.flat(x, y, (0, 0, 0))


# ─── Props i decorats ──────────────────────────────────────────────────────

def p_galleda(cv):
    x, y = GALLEDA
    ombra(cv, x + 8, y + 1, 16, 3, 0.7)
    galleda(cv, x, y, s=1.0)


def reg_muntat(cv):
    """El reg gota a gota del pare, muntat: la galleda penjada d'un clau a la paret del racó, i el tub negre que
    baixa fins al test i hi fa la volta, amb els goters foradats amb l'agulla; les gotes."""
    gx, gy = 596, 96                                                     # la base de la galleda penjada
    cv.flat(596, 64, ZINC[5])
    cv.line(596, 64, 585, 76, ZINC, 3.0)
    cv.line(596, 64, 607, 76, ZINC, 3.0)
    galleda(cv, gx, gy, s=0.95, plena=True)
    # l'aixeta i el tub que baixa resseguint la paret
    cv.rect(gx - 2, gy + 1, gx + 2, gy + 4, ZINC, 3.0)
    pts = [(gx, gy + 4), (gx + 2, 130), (gx + 3, 170), (gx - 4, 190), (POT[0] + 16, POT[1] - 28)]
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        cv.line(xa, ya, xb, yb, HOSE, 2.6)
        cv.line(xa + 1, ya, xb + 1, yb, HOSE, 1.2)
    # la volta damunt la terra del test, amb tres goters verds
    cx, by = POT
    for a in range(0, 360, 6):
        ra = math.radians(a)
        cv.put(cx + math.cos(ra) * 12, by - 26 + math.sin(ra) * 2.2, HOSE, 3.0 if math.sin(ra) > 0 else 1.6)
    for a in (40, 150, 270):
        ra = math.radians(a)
        x, y = cx + math.cos(ra) * 12, by - 26 + math.sin(ra) * 2.2
        cv.rect(x - 1, y - 1, x + 1, y, [(10, 60, 20), (30, 120, 40), (80, 190, 80)], 1.6)
        cv.flat(x, y + 1, (170, 220, 250))
    # una etiqueta del pare, a mà, lligada al tub
    cv.rect(gx + 4, 140, gx + 12, 146, [(180, 170, 140), (220, 210, 180), (244, 236, 210)], 1.4)
    cv.line(gx + 3, 140, gx + 4, 142, ZINC, 2.0)


def tomaquera_viva(cv):
    """La tomaquera salvada: tiges gruixudes, fulles verdes de debò (no brillen), flors grogues i tomàquets."""
    cx, by = POT
    stem = [(cx, by - 26), (cx + 1, by - 50), (cx - 2, by - 76), (cx + 1, by - 100), (cx - 1, by - 116)]
    for (xa, ya), (xb, yb) in zip(stem, stem[1:]):
        for k in range(3):
            cv.line(xa - 1 + k, ya, xb - 1 + k, yb, LEAF, 2.0 + k * 0.4)

    def fulla(x, y, side, s=1.0):
        cv.disc(x, y, 5 * s, 3 * s, LEAF, lambda nx, ny: 3.0 - ny * 1.0 - nx * side * 0.4 + (hr(int(x), int(y)) - 0.5))
        cv.line(x - side * 3 * s, y, x + side * 4 * s, y + 1, LEAF, 1.4)
        for d in (-1, 1):
            cv.disc(x + side * 4 * s, y + d * 3 * s, 3 * s, 2 * s, LEAF, lambda nx, ny: 2.6 - ny * 0.8)
    # les branques i el fullatge, de darrere cap endavant
    for k in range(16):
        sy = by - 34 - k * 5.4
        side = -1 if k % 2 else 1
        ln = 14 + hr(k, 3) * 12 - k * 0.4
        sx = cx + (hr(k, 4) - 0.5) * 2
        ex, ey = sx + side * ln, sy + 3 - hr(k, 5) * 6
        cv.line(sx, sy, ex, ey, LEAF, 2.4)
        fulla(ex, ey, side, 1.0 + hr(k, 6) * 0.3)
        fulla(sx + side * ln * 0.5, sy + 2 + (sy - ey) * 0.0, side, 0.8)
    for k in range(5):                                                   # el cim
        fulla(cx + (k - 2) * 4, by - 118 + abs(k - 2) * 3, 1 if k > 2 else -1, 0.7)
    # flors grogues petites
    for i in range(7):
        x, y = cx - 22 + hr(i, 11) * 44, by - 110 + hr(i, 12) * 70
        for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1)):
            cv.flat(x + dx, y + dy, (250, 220, 40))
        cv.flat(x, y, (180, 120, 10))
    # els tomàquets: penjant en rams, vermells i algun encara taronja o verd
    for i, (x, y, r, ramp) in enumerate(((cx - 15, by - 50, 4.4, TOMATO), (cx - 9, by - 44, 4.0, TOMATO),
                                         (cx + 14, by - 64, 4.6, TOMATO), (cx + 19, by - 57, 3.6, TOMATO),
                                         (cx - 17, by - 84, 4.0, TOMATO), (cx + 9, by - 92, 3.4, ORANGE_T),
                                         (cx - 6, by - 100, 3.2, LEAF), (cx + 16, by - 38, 3.8, TOMATO))):
        cv.disc(x, y, r, r * 0.92, ramp, lambda nx, ny: 2.6 - nx * 0.9 - ny * 1.0)
        cv.flat(x - r * 0.4, y - r * 0.4, ramp[5] if len(ramp) > 5 else ramp[-1])
        cv.flat(x, y - r, LEAF[1])                                         # el capoll
        cv.flat(x - 1, y - r, LEAF[2])
        cv.flat(x + 1, y - r, LEAF[2])


ORANGE_T = [(90, 30, 6), (160, 70, 14), (220, 120, 30), (250, 166, 60), (255, 206, 120), (255, 236, 190)]

PROPS = {'galleda': p_galleda, 'reg_muntat': reg_muntat, 'tomaquera_viva': tomaquera_viva}

GEOMETRIA = {
    'things': {
        'porta': {'rect': (18, 82, 100, 216), 'walk': (66, 240)},
        'tomaquera': {'rect': (512, 90, 608, 226), 'walk': (530, 244)},
        'galleda': {'rect': (246, 218, 280, 248), 'walk': (236, 252)},
        'sacs': {'rect': (390, 146, 512, 224), 'walk': (446, 240)},
        'eines': {'rect': (128, 40, 262, 200), 'walk': (196, 238)},
    },
    'spawns': {'iri': (150, 248), 'vet': (380, 246)},
    'walkable': [(14, 228), (608, 228), (632, 256), (6, 256)],
}


# ─── Animacions ────────────────────────────────────────────────────────────

def _frames_pols():
    """La pols que balla al raig de llum de la finestra."""
    cv0 = Canvas(light=LIGHT)
    bg(cv0)
    base = cv0.img
    frames = []
    n = 16
    for i in range(n):
        cv = Canvas(light=LIGHT, img=base.copy())
        for j in range(40):
            t = (hr(j, 1) + i / n * (0.3 + hr(j, 2) * 0.3)) % 1.0
            y = WIN[3] + 6 + t * 100
            a = WIN[0] + 4 + (516 - WIN[0]) * ((y - WIN[3]) / (226 - WIN[3]))
            b = WIN[2] + (606 - WIN[2]) * ((y - WIN[3]) / (226 - WIN[3]))
            x = a + (b - a) * hr(j, 3) + math.sin(i * 0.4 + j) * 2
            if hr(j, i // 4, 9) > 0.3:
                cv.flat(x, y, mix(cv.get(x, y), (255, 250, 220), 0.7))
        frames.append(_diff(cv.img, base))
    return frames


ANIMS = {'pols': {'frames': _frames_pols, 'frameDuration': 180}}
