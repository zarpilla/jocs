"""
El rebost de l'Arenga (coberta de sota, porta amb porta amb la sala de màquines). Art definitiu:
  - un magatzem estret de planxa verda, amb un llum de gàbia càlid;
  - a l'esquerra, la porta estanca oberta cap a la sala de màquines, i el tamboret on el cuiner d'abans hi
    baixava a fumar (una llauna de sardines fa de cendrer);
  - el muntacàrregues de la cuina: la boca a la paret amb la portella de guillotina pujada, el replà de la safata
    i tres botons (cuina, rebost, pont); `safata` (prop): una safata d'acer amb alguna cosa;
  - les prestatgeries de queviures: llaunes de sardines de Portugal (en falten unes quantes), arròs, pots;
  - a terra, el registre del dipòsit 2 (tapa blava amb «AIGUA NO POTABLE», frontisses i un pany); `rascades` (prop, Escenes 4 i
    després): el pany forçat; `registre_obert` (prop): la tapa aixecada i el forat amb l'escala.
"""
import math

from hd.pix import Canvas, Light, W, H, hr, mix
from hd.rooms.arenga import (WALL, ENG_LIGHT as ENG, DECK, CAB, REDP, YELL, SEAG, DARK, WHITEP, BRASS, WARM,
                             FLOOR_Y, box, rrect, bolt, hpipe, vpipe, glow)
from hd.rooms.sota import (plate_wall, ceiling, checker_floor, door_frame, in_door, hinge_leaf, sill, sign,
                           cage_lamp, lamp_glow, floor_shadow)
from hd.rooms.comu import _diff, text, text_width

LAMP_X = (150, 372)
SHELF = [(18, 20, 22), (34, 38, 42), (54, 60, 64), (78, 84, 88), (104, 110, 112), (134, 140, 140), (170, 174, 172)]
TIN = [(30, 34, 40), (60, 68, 78), (100, 110, 120), (148, 158, 166), (196, 204, 208), (236, 240, 242)]
SARD = [(20, 30, 60), (30, 52, 100), (46, 80, 140), (80, 118, 176), (140, 170, 210)]       # paper blau de les llaunes
SARDY = [(60, 36, 6), (130, 90, 16), (200, 150, 30), (240, 200, 80)]                       # i les de groc
RICE = [(70, 62, 46), (130, 118, 90), (184, 172, 138), (220, 210, 180), (240, 234, 210)]
JUTE = [(30, 22, 10), (60, 44, 22), (96, 72, 38), (130, 102, 58), (164, 134, 82), (196, 170, 114)]
ONION = [(50, 20, 10), (110, 50, 20), (170, 96, 40), (210, 146, 80)]
BLUEP = [(10, 18, 34), (18, 32, 58), (28, 50, 86), (42, 72, 116), (62, 98, 146), (96, 132, 176)]
WOOD = [(24, 14, 8), (44, 26, 14), (68, 42, 22), (96, 62, 32), (126, 84, 44), (156, 110, 60), (186, 140, 82)]

LIGHT = Light(ambient=-0.4, vignette=(60, 28), floor_fade=(188, 36))
LIGHT.point(LAMP_X[0], 26, r=150, k=2.5, squash=1.05, down=True, power=1.5)
LIGHT.point(LAMP_X[1], 26, r=150, k=2.3, squash=1.05, down=True, power=1.5)
LIGHT.point(34, 110, r=40, k=0.4, power=2.0)

MUNTA = (196, 56, 246, 106)


# ─── Paret i sostre ───────────────────────────────────────────────────────

def room(cv):
    plate_wall(cv, 0, W - 1, seed=11)
    ceiling(cv)
    hpipe(cv, 60, W - 1, 30, 2, SEAG, 3.0, bands=range(80, W, 70), band_ramp=WHITEP)       # aigua dolça
    for x in range(90, W, 70):
        cv.vline(x, 26, 34, CAB, 3.0)
    # el tub del dipòsit 2, que baixa a terra (al costat del registre)
    vpipe(cv, 66, 30, FLOOR_Y + 2, 2, SEAG, 2.8, bands=(60, 120), band_ramp=WHITEP)
    hpipe(cv, 60, 66, 30, 2, SEAG, 3.0)
    for lx in LAMP_X:
        cage_lamp(cv, lx)


# ─── La porta i el racó del cuiner ────────────────────────────────────────

def door(cv):
    x0, y0, x1, y1 = 14, 66, 54, FLOOR_Y
    for y in range(y0, y1):
        for x in range(x0, x1 + 1):
            if in_door(x, y, x0, y0, x1, y1):
                cv.put(x, y, WALL, 2.0 - abs(x - 34) / 40 + (-1.0 if y > 136 else 0) - (y - y0) / 160, lit=0.3)
    for y in range(y0 + 14, y1 - 14):                               # el motor, de l'altra banda
        for x in range(x0, x0 + 18):
            cv.put(x, y, ENG, 2.4 - (y - y0) * 0.01 + (0.6 if (y - y0) % 10 == 0 else 0), lit=0.2)
    cv.rect(x0, y1 - 14, x1, y1 - 1, DECK, 1.6, lit=0.2)
    door_frame(cv, x0, y0, x1, y1)
    sill(cv, x0, x1, y1)
    hinge_leaf(cv, 4, y0, 12, y1)
    for dx, dy in ((x1 + 2, 84), (x1 + 2, 124)):
        box(cv, dx, dy, dx + 2, dy + 6, CAB, 3.4)
    sign(cv, 12, 52, 'MÀQUINES')


def stool(cv):
    """El tamboret del cuiner d'abans, amb la llauna de sardines que fa de cendrer."""
    x0, x1, top = 76, 100, 126
    cv.disc((x0 + x1) / 2, top, (x1 - x0) / 2, 3, WOOD, lambda nx, ny: 4.4 - ny * 1.2)
    for lx, d in ((x0 + 3, -2), (x1 - 3, 2), ((x0 + x1) // 2, 0)):
        cv.line(lx, top + 2, lx + d, FLOOR_Y + 6, WOOD, 3.0)
    cv.hline(x0 + 3, x1 - 3, 144, WOOD, 2.6)
    # la llauna-cendrer, oberta, amb dues burilles
    cv.disc(88, top - 2, 6, 2, TIN, 4.4)
    cv.disc(88, top - 2, 4, 1.2, TIN, 1.6)
    cv.rect(84, top - 4, 85, top - 3, WHITEP, 4.6)
    cv.put(86, top - 4, YELL, 3.6)
    cv.rect(91, top - 3, 93, top - 3, WHITEP, 4.4)


# ─── El muntacàrregues ────────────────────────────────────────────────────

def dumbwaiter(cv):
    x0, y0, x1, y1 = MUNTA
    box(cv, x0 - 4, y0 - 4, x1 + 4, y1 + 4, CAB, 3.2, grad=0.6)      # el marc d'acer inoxidable
    # els carrils de la guillotina
    for gx in (x0 - 2, x1 + 2):
        cv.vline(gx, y0 - 4, y1 + 4, CAB, 4.4)
    # l'obertura, amb la portella de guillotina pujada
    box(cv, x0, y0 + 14, x1, y1, DARK, 1.0)
    for y in range(y0 + 16, y1 - 1):
        cv.hline(x0 + 1, x1 - 1, y, DARK, 1.6 + (y - y0 - 16) * 0.03, lit=0.3)
    cv.vline(x0 + 1, y0 + 16, y1 - 1, CAB, 1.8)
    for y in range(y0 + 18, y1 - 6, 8):                              # les guies de dins del pou
        cv.put(x0 + 3, y, CAB, 2.6, lit=0.3)
        cv.put(x1 - 3, y, CAB, 2.6, lit=0.3)
    cv.hline(x0 - 2, x1 + 2, y1, CAB, 4.0)                          # el replà de la safata
    cv.hline(x0 - 2, x1 + 2, y1 + 1, CAB, 2.0)
    box(cv, x0, y0, x1, y0 + 12, CAB, 3.6)                          # la portella, a dalt
    for y in range(y0 + 3, y0 + 11, 3):
        cv.hline(x0 + 3, x1 - 3, y, CAB, 2.6)
    box(cv, (x0 + x1) // 2 - 5, y0 + 10, (x0 + x1) // 2 + 5, y0 + 12, BRASS, 3.4)
    # la placa de llautó del fabricant
    box(cv, x0 + 12, y0 - 12, x1 - 12, y0 - 7, BRASS, 3.2)
    for x in range(x0 + 14, x1 - 13, 2):
        cv.put(x, y0 - 10, BRASS, 1.6)
    # els tres botons (cuina, rebost, pont): plaques amb lletres i el del rebost encès
    bx = x1 + 8
    box(cv, bx, 66, bx + 12, 100, CAB, 2.8)
    for i, (lt, lit) in enumerate((('C', False), ('R', True), ('P', False))):
        y = 70 + i * 10
        cv.disc(bx + 4, y + 2, 2, 2, REDP if lit else WHITEP, 4.6 if lit else 3.4, lit=0.5)
        text(cv, lt, bx + 8, y, None, 0, flat=(200, 204, 200))
        if lit:
            glow(cv, bx + 4, y + 2, 5, (255, 80, 60), 0.5)
    # el timbre
    cv.disc(bx + 6, 108, 3, 2, BRASS, lambda nx, ny: 3.8 - nx - ny)


# ─── Les prestatgeries ────────────────────────────────────────────────────

def _tins_row(cv, x0, x1, base, seed, gaps=()):
    """Una filera de llaunes de sardines, apilades de costat (rectangles plans amb el paper blau o groc)."""
    x = x0
    i = 0
    while x + 14 <= x1:
        h = 4
        stack = 2 + int(hr(i, seed) * 3)
        if i in gaps:
            stack = int(hr(i, seed, 2) * 2)                         # en falten
        for k in range(stack):
            y = base - (k + 1) * (h + 1)
            ramp = SARDY if hr(i, k, seed) > 0.7 else SARD
            box(cv, x, y, x + 13, y + h, TIN, 3.8)
            cv.rect(x + 1, y + 1, x + 12, y + h - 1, ramp, 2.8)
            cv.hline(x + 3, x + 7, y + 2, WHITEP, 3.8)
            cv.put(x + 10, y + 2, REDP, 3.6)
        x += 15
        i += 1


def shelves(cv):
    x0, x1 = 286, 470
    # els muntants (angulars perforats)
    for ux in (x0, (x0 + x1) // 2, x1 - 3):
        box(cv, ux, 40, ux + 3, FLOOR_Y + 3, SHELF, 3.4)
        for y in range(44, FLOOR_Y, 6):
            cv.put(ux + 1, y, SHELF, 0.8)
    levels = (64, 94, 124, FLOOR_Y - 2)
    for y in levels:
        box(cv, x0, y, x1, y + 3, SHELF, 3.8)
        cv.darken(x0 + 4, y + 4, x1 - 4, y + 8, lambda xx, yy: 0.6 - (yy - y - 4) * 0.12)
    # prestatge de dalt: pots de vidre (llegums) i garrafes
    for i, x in enumerate(range(x0 + 8, x1 - 10, 16)):
        if hr(i, 3) > 0.85:
            continue
        col = [ONION, RICE, REDP, ONION, RICE][i % 5]
        for y in range(46, 64):
            for xx in range(x, x + 11):
                u = (xx - x - 5) / 6
                cv.put(xx, y, col if y > 50 else WHITEP, (2.8 if y > 50 else 3.4) - u * 1.0 - u * u)
        cv.rect(x + 1, 44, x + 9, 46, REDP if i % 2 else CAB, 3.6)
    # segon: llaunes de sardines (en falten unes quantes)
    _tins_row(cv, x0 + 6, (x0 + x1) // 2 - 2, 94, 1, gaps=(3, 4))
    _tins_row(cv, (x0 + x1) // 2 + 5, x1 - 4, 94, 2, gaps=(2,))
    # tercer: més sardines i llaunes grosses de tomàquet
    _tins_row(cv, x0 + 6, x0 + 80, 124, 3, gaps=(1,))
    for i, x in enumerate(range(x0 + 96, x1 - 8, 15)):
        for y in range(104, 124):
            for xx in range(x, x + 13):
                u = (xx - x - 6) / 7
                cv.put(xx, y, TIN if (y < 107 or y > 121) else REDP, 3.4 - u * 1.2 - u * u)
        cv.hline(x + 2, x + 10, 112, YELL, 3.8)
    # a baix: sacs d'arròs i una caixa de cebes
    for i, x in enumerate((x0 + 6, x0 + 38, x0 + 70)):
        cv.poly([(x, FLOOR_Y - 3), (x + 2, 132), (x + 8, 128), (x + 22, 128), (x + 28, 132), (x + 30, FLOOR_Y - 3)],
                JUTE, lambda xx, yy: 3.6 - (yy - 128) * 0.03 - abs(xx - x - 15) * 0.05)
        cv.rect(x + 8, 136, x + 22, 142, WHITEP, 3.4)
        cv.hline(x + 10, x + 20, 139, REDP, 3.6)
    box(cv, x0 + 110, 132, x0 + 150, FLOOR_Y - 3, WOOD, 3.4)
    for y in range(136, FLOOR_Y - 3, 5):
        cv.hline(x0 + 111, x0 + 149, y, WOOD, 2.2)
    for i in range(9):
        cv.disc(x0 + 116 + i * 4, 130 + int(hr(i, 7) * 2), 3, 2.5, ONION, lambda nx, ny: 3.4 - nx - ny)


def freezer_and_calendar(cv):
    """Un congelador d'arcó (blanc, vell) i el calendari del cuiner d'abans, encara del 2019."""
    x0, x1, top = 108, 178, 120
    box(cv, x0, top, x1, FLOOR_Y + 3, WHITEP, 3.6, grad=0.8)
    cv.rect(x0 - 1, top - 4, x1 + 1, top, WHITEP, 4.4)                # la tapa
    cv.hline(x0 - 1, x1 + 1, top - 4, WHITEP, 5.4)
    cv.hline(x0 - 1, x1 + 1, top + 1, WHITEP, 1.6)
    box(cv, (x0 + x1) // 2 - 8, top + 3, (x0 + x1) // 2 + 8, top + 6, CAB, 3.4)    # nansa
    cv.flat(x1 - 8, top + 12, (90, 240, 120))                         # el pilot verd
    glow(cv, x1 - 8, top + 12, 4, (90, 240, 120), 0.5)
    cv.rect(x0 + 4, FLOOR_Y - 4, x1 - 4, FLOOR_Y + 1, CAB, 1.6)      # reixeta
    for x in range(x0 + 5, x1 - 4, 2):
        cv.put(x, FLOOR_Y - 2, CAB, 3.0)
    # un rovellet a la cantonada
    for y in range(FLOOR_Y - 8, FLOOR_Y + 3):
        for x in range(x0, x0 + 4):
            if hr(x, y, 4) > 0.5:
                cv.put(x, y, [(60, 30, 16), (110, 60, 30), (150, 90, 50)], 1.6)
    # el calendari: un peix i una graella de dies
    cx0, cy0, cx1, cy1 = 124, 62, 158, 106
    box(cv, cx0, cy0, cx1, cy1, WHITEP, 4.2)
    cv.rect(cx0 + 2, cy0 + 2, cx1 - 2, cy0 + 20, [(10, 30, 50), (20, 60, 90), (40, 100, 130), (90, 150, 170)], 2.2)
    cv.disc(141, cy0 + 11, 9, 4, TIN, lambda nx, ny: 4.0 - ny * 1.4)          # el peix
    cv.poly([(149, cy0 + 11), (155, cy0 + 6), (155, cy0 + 16)], TIN, 3.6)
    cv.put(135, cy0 + 10, DARK, 0)
    for j in range(5):
        for i in range(7):
            cv.put(cx0 + 4 + i * 4, cy0 + 25 + j * 4, CAB, 2.0)
    for i, (dx, dy) in enumerate(((2, 1), (4, 3))):                    # dies encerclats en vermell
        cv.ring(cx0 + 4 + dx * 4, cy0 + 25 + dy * 4, 2, REDP, 4.0, step=40)
    cv.put((cx0 + cx1) // 2, cy0 - 2, CAB, 4.0)                       # el clau


# ─── El registre del dipòsit 2 ────────────────────────────────────────────

REG = (84, 164, 162, 188)


def registre(cv):
    """La tapa del registre, a terra: planxa pintada de blau, frontisses a dalt, pany a baix amb rascades."""
    x0, y0, x1, y1 = REG
    # la vora (brida), més ample a baix per la perspectiva
    cv.poly([(x0 + 4, y0), (x1 - 4, y0), (x1, y1), (x0, y1)], DECK, lambda x, y: 1.8)
    cv.poly([(x0 + 7, y0 + 2), (x1 - 7, y0 + 2), (x1 - 3, y1 - 2), (x0 + 3, y1 - 2)], BLUEP,
            lambda x, y: 3.6 - (y - y0) * 0.03 + (hr(x // 3, y // 2, 8) - 0.5) * 0.4)
    cv.hline(x0 + 7, x1 - 7, y0 + 2, BLUEP, 5.0)
    cv.hline(x0, x1, y1, DECK, 4.2)
    # cargols de la vora
    for i in range(9):
        t = i / 8
        bolt(cv, round(x0 + 5 + (x1 - x0 - 10) * t), y0 + 1, DECK, 4.0)
    # frontisses (les que la Juana va treure i tornar a posar), a dalt
    for hx in (x0 + 18, x1 - 26):
        box(cv, hx, y0 - 1, hx + 8, y0 + 4, CAB, 4.0)
        cv.hline(hx, hx + 8, y0 + 1, CAB, 5.4)
        bolt(cv, hx + 2, y0 + 2, CAB, 5.0)
        bolt(cv, hx + 6, y0 + 2, CAB, 5.0)
    # «AIGUA NO POTABLE», estergit en blanc
    s = 'AIGUA NO POTABLE'
    tx = (x0 + x1) // 2 - text_width(s) // 2
    text(cv, s, tx, y0 + 8, None, 0, flat=(200, 206, 210))
    # el pany, a baix al mig (les rascades i la pintura saltada són el prop `rascades`)
    cx = (x0 + x1) // 2
    lock(cv, cx, y1)
    # la nansa encastada
    cv.rect(cx - 16, y1 - 6, cx - 9, y1 - 4, DARK, 0.6)
    cv.hline(cx - 16, cx - 9, y1 - 3, BLUEP, 5.0)


def lock(cv, cx, y1):
    """El pany de la tapa: una placa de llautó amb el forat de la clau."""
    box(cv, cx - 4, y1 - 9, cx + 4, y1 - 2, BRASS, 3.6)
    cv.vline(cx, y1 - 7, y1 - 4, DARK, 0.4)
    cv.put(cx, y1 - 7, DARK, 0.2)


def rascades(cv):
    """Escenes 4 i després: algú ha forçat el pany. La pintura saltada al voltant i rascades fresques."""
    x0, y0, x1, y1 = REG
    cx = (x0 + x1) // 2
    for y in range(y1 - 8, y1 - 2):                                # la pintura saltada (planxa nua)
        for x in range(cx - 10, cx + 11):
            if hr(x, y, 21) > 0.35 and abs(x - cx) + abs(y - (y1 - 5)) * 2 < 13:
                cv.put(x, y, DECK, 4.6 + hr(x, y, 3))
    lock(cv, cx, y1)
    for i in range(7):                                             # rascades fresques (ratlles brillants)
        sx = cx - 9 + int(hr(i, 1, 2) * 18)
        sy = y1 - 9 + int(hr(i, 2, 2) * 6)
        for k in range(3 + int(hr(i, 3) * 3)):
            cv.flat(sx + k, sy + (k // 2) * (1 if i % 2 else -1), (206, 214, 220))


def registre_obert(cv):
    """El registre obert: la tapa aixecada sobre les frontisses i el forat fosc, amb l'escala que baixa."""
    x0, y0, x1, y1 = REG
    # el forat: a dalt s'hi veu la paret del fons del pou (una mica de llum), a baix negre
    hole = [(x0 + 7, y0 + 2), (x1 - 7, y0 + 2), (x1 - 3, y1 - 2), (x0 + 3, y1 - 2)]
    cv.poly(hole, DARK, lambda x, y: 2.4 - (y - y0) * 0.14, lit=0)
    cv.hline(x0 + 7, x1 - 7, y0 + 2, DECK, 3.4)                    # el cantell de la brida, de dins
    cv.hline(x0 + 3, x1 - 3, y1 - 2, DECK, 3.6)                    # el cantell del davant
    cv.hline(x0 + 3, x1 - 3, y1 - 1, DECK, 2.0)
    for y in range(y0 + 3, y1 - 2):                                # una mica d'aigua tèrbola, al fons, que brilla
        if hr(y, 5) > 0.6:
            cv.put(x0 + 30 + int(hr(y, 6) * 20), y, WHITEP, 0.6, lit=0)
    # l'escala, clavada a la paret del fons, que baixa i es perd
    lx0, lx1 = (x0 + x1) // 2 - 7, (x0 + x1) // 2 + 7
    for lx in (lx0, lx1):
        cv.vline(lx, y0 - 3, y1 - 4, CAB, lambda x, y: 5.8 - (y - y0) * 0.2)
        cv.vline(lx + 1, y0 - 3, y1 - 4, CAB, lambda x, y: 4.0 - (y - y0) * 0.2)
    for ry in range(y0 + 1, y1 - 4, 5):
        cv.hline(lx0 + 2, lx1 - 1, ry, CAB, 5.4 - (ry - y0) * 0.2)
    cv.put(lx0, y0 - 4, CAB, 5.0)                                  # els caps de l'escala, per agafar-s'hi
    cv.put(lx1, y0 - 4, CAB, 5.0)
    # la tapa, aixecada i dreta: en veiem la cara de sota (planxa sense pintar, rovell i la junta de goma)
    ty = y0 - 30
    lid = [(x0 + 9, ty), (x1 - 9, ty), (x1 - 7, y0 + 1), (x0 + 7, y0 + 1)]
    cv.poly(lid, CAB, lambda x, y: 4.6 + (y - ty) * 0.02 - (x - x0) * 0.01 + (hr(x // 2, y // 2, 4) - 0.5) * 0.5)
    cv.poly([(x0 + 12, ty + 3), (x1 - 12, ty + 3), (x1 - 10, y0 - 2), (x0 + 10, y0 - 2)], DARK, 2.4)  # la junta
    cv.poly([(x0 + 14, ty + 5), (x1 - 14, ty + 5), (x1 - 12, y0 - 4), (x0 + 12, y0 - 4)], CAB,
            lambda x, y: 4.0 + (y - ty) * 0.02 - (x - x0) * 0.01 + (hr(x // 3, y // 2, 9) - 0.5) * 0.6)
    for i in range(14):                                            # rovell
        rx = x0 + 16 + int(hr(i, 11) * (x1 - x0 - 32))
        ry = ty + 6 + int(hr(i, 12) * 22)
        cv.put(rx, ry, [(40, 18, 10), (80, 36, 18), (120, 60, 28), (150, 86, 44)], 1.6 + hr(i, 13) * 1.4)
        cv.put(rx + 1, ry, [(40, 18, 10), (80, 36, 18), (120, 60, 28), (150, 86, 44)], 1.2)
    cv.hline(x0 + 9, x1 - 9, ty, BLUEP, 5.0)                         # el cantell de dalt
    cv.line(x0 + 9, ty, x0 + 7, y0 + 1, BLUEP, 4.4)
    cv.line(x1 - 9, ty, x1 - 7, y0 + 1, BLUEP, 2.6)
    cv.hline(x0 + 20, x1 - 20, (ty + y0) // 2, CAB, 5.2)          # el reforç
    cv.hline(x0 + 20, x1 - 20, (ty + y0) // 2 + 1, CAB, 3.0)
    for hx in (x0 + 18, x1 - 26):                                  # les frontisses, ara tombades
        box(cv, hx, y0 - 2, hx + 8, y0 + 2, CAB, 4.4)
        bolt(cv, hx + 2, y0, CAB, 5.0)
        bolt(cv, hx + 6, y0, CAB, 5.0)
    floor_shadow(cv, (x0 + x1) // 2, y0 - 4, 30, 2, 0.4)


# ─── Muntatge ─────────────────────────────────────────────────────────────

def bg(cv):
    room(cv)
    door(cv)
    dumbwaiter(cv)
    shelves(cv)
    stool(cv)
    freezer_and_calendar(cv)
    checker_floor(cv)
    floor_shadow(cv, 88, FLOOR_Y + 5, 16, 3, 0.6)
    floor_shadow(cv, 143, FLOOR_Y + 4, 40, 4, 0.6)
    floor_shadow(cv, 378, FLOOR_Y + 3, 96, 5, 0.5)
    registre(cv)
    for lx in LAMP_X:
        lamp_glow(cv, lx)


def safata(cv):
    """Una safata d'acer al replà del muntacàrregues, amb alguna cosa embolicada amb un drap de cuina."""
    x0, y0, x1, y1 = MUNTA
    cv.poly([(x0 + 2, y1 - 3), (x1 - 2, y1 - 3), (x1 + 1, y1), (x0 - 1, y1)], CAB, 4.4)
    cv.hline(x0 - 1, x1 + 1, y1, CAB, 2.2)
    cv.hline(x0 + 2, x1 - 2, y1 - 3, CAB, 5.4)
    # el drap (quadres vermells i blancs), amb un bony a dins
    cx = (x0 + x1) // 2
    for y in range(y1 - 12, y1 - 2):
        for x in range(cx - 13, cx + 14):
            nx, ny = (x - cx) / 13.5, (y - (y1 - 2)) / 10
            if nx * nx + ny * ny <= 1:
                chk = ((x // 3) + (y // 3)) % 2
                cv.put(x, y, REDP if chk else WHITEP, (3.8 if chk else 4.2) - ny * 0.6 - nx * 0.8)
    cv.poly([(cx + 8, y1 - 9), (cx + 16, y1 - 12), (cx + 14, y1 - 6)], WHITEP, 3.6)    # una punta del drap
    # un paperet doblegat al costat
    cv.poly([(x1 - 10, y1 - 4), (x1 - 3, y1 - 6), (x1 - 2, y1 - 3), (x1 - 9, y1 - 2)], WHITEP, 4.6)


PROPS = {'safata': safata, 'rascades': rascades, 'registre_obert': registre_obert}


# ─── Animacions ─────────────────────────────────────────────────────────────

def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv


def _frames_pols():
    """Pols que sura a la llum dels dos llums de gàbia (cada mota fa un llaç tancat: el bucle no salta)."""
    base = _base()
    motes = []
    for lx in LAMP_X:
        for k in range(14):
            motes.append((lx + (hr(k, lx, 1) - 0.5) * 70, 44 + hr(k, lx, 2) * 80,
                          6 + hr(k, lx, 3) * 10, 4 + hr(k, lx, 4) * 8, hr(k, lx, 5), 1 + int(hr(k, lx, 6) * 2), lx))
    n = 48
    frames = []
    for i in range(n):
        cv = Canvas(light=LIGHT, img=base.img.copy())
        t = i / n
        for (cx, cy, ax, ay, ph, fx, lx) in motes:
            a = 2 * math.pi * (t + ph)
            x = round(cx + ax * math.sin(fx * a))
            y = round(cy + ay * math.sin(a + ph * 3))
            near = max(0.0, 1 - math.hypot(x - lx, (y - 26) * 0.9) / 140)       # només es veu a prop del llum
            tw = 0.5 + 0.5 * math.sin(a * 2 + ph * 7)                              # i fa pampallugues
            alpha = near * (0.5 + 0.5 * tw)
            if alpha > 0.08 and 0 <= x < W and 0 <= y < FLOOR_Y:
                cv.flat(x, y, mix(cv.get(x, y), (255, 236, 196), alpha))
        frames.append(_diff(cv.img, base.img))
    return frames


MOUSE = [(70, 62, 60), (104, 94, 90), (138, 128, 120)]


def _mouse(cv, x, y, out, sniff):
    """El cap del ratolí que treu el morro d'entre dos sacs (x, y: l'espatlla, a terra; out: quant surt)."""
    for dx in range(out):
        top = y - 3 + (1 if dx == out - 1 else 0)
        for yy in range(top, y + 1):
            cv.flat(x + dx, yy, MOUSE[1] if yy > top else MOUSE[2])
    if out >= 3:
        cv.flat(x + 1, y - 4, (150, 104, 104))                     # l'orella
        cv.flat(x + out - 2, y - 2, (12, 10, 12))                  # l'ull
        cv.flat(x + out, y - 1 - sniff, (190, 120, 120))           # el nas, que olora
        cv.flat(x + out + 1, y - 2 - sniff, mix(cv.get(x + out + 1, y - 2 - sniff), (200, 200, 190), 0.5))  # bigotis


def _frames_ratoli():
    """Un ratolí treu el cap d'entre els sacs d'arròs, olora i s'hi torna a amagar."""
    base = _base()
    mx, my = 352, FLOOR_Y - 4                                       # entre el segon sac i el tercer
    seq = [(0, 0)] * 20 + [(1, 0), (2, 0), (3, 0), (4, 0)] + [(5, i % 2) for i in range(10)] + \
          [(5, 0)] * 6 + [(5, i % 2) for i in range(6)] + [(3, 0), (1, 0)] + [(0, 0)] * 10
    frames = []
    for out, sniff in seq:
        cv = Canvas(light=LIGHT, img=base.img.copy())
        if out:
            _mouse(cv, mx, my, out, sniff)
        frames.append(_diff(cv.img, base.img))
    return frames


ANIMS = {'pols': {'frames': _frames_pols, 'frameDuration': 130},
         'ratoli': {'frames': _frames_ratoli, 'frameDuration': 110}}


GEOMETRIA = {
    'things': {
        'porta': {'rect': (2, 46, 60, 152), 'walk': (34, 174)},
        'munta': {'rect': (190, 42, 268, 94), 'walk': (222, 176)},
        'safata': {'rect': (192, 95, 250, 110), 'walk': (222, 176)},
        'prestatges': {'rect': (284, 38, 472, 152), 'walk': (378, 176)},
        'registre': {'rect': (82, 160, 164, 190), 'walk': (176, 186)},
    },
    'spawns': {'iri': (250, 188), 'vet': (320, 190)},
    'walkable': [(6, 170), (474, 170), (478, 196), (2, 196)],
}
