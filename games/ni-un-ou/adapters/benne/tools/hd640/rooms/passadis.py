"""
Prova de resolució: el passadís de la coberta principal de l'Arenga a 640×360 (la composició de
hd/rooms/passadis.py ×4/3, dibuixada de nou amb el detall que hi cap). Mateixes rampes, props i animacions.

D'esquerra (popa) a dreta (proa):
  - la porta del menjador, oberta, amb la llum càlida de dins (la taula, les tasses i el llum);
  - la porta de la infermeria (blanca, amb la creu), la del laboratori (adhesius de risc biològic i un peix) i la de
    la Capitana (de fusta, amb el paperet «TRUQUEU ABANS»), cadascuna amb la placa del nom;
  - el rellotge de vaixell entre el laboratori i la Capitana;
  - l'escala del pont, que puja pel forat del sostre (llum blavosa de dalt), el plànol d'emergència i el forat de
    l'escala de baix, amb la barana groga i la llum verda de la sala de màquines;
  - la porta estanca de coberta, cap a proa, amb l'ull de bou i la nit a fora.
"""
import math

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from hd.pix import Canvas, Light, W, H, hr, mix  # noqa: F401
from hd.rooms.arenga import CAB, DARK, WHITEP, REDP, YELL, BRASS, SEAG, box, rrect, bolt, hpipe, vpipe, glow
from hd.rooms.comu import _diff, text, text_width
from hd.rooms.principal import (CREAM, TEAK, DOORP, in_door, sill, plaque, porthole, day_porthole, unmask,
                                foot_shadow, wear, second_hand)
from hd640.rooms.laboratori import wall, ceiling, lamp, lamp_glow, lino, shine, door_frame
from hd640.rooms.menjador import leaf, sign_box

# Art a 2× (1280×720 per a una sala de 640×360): el mateix dibuix, amb les formes, el dither i la llum a la
# resolució real (hd1280/canvas2x.py); el motor el mostra a 1/2 (artScale al .room.json).
ART_SCALE = 2
from hd1280.canvas2x import Canvas2x as Canvas  # noqa: E402,F811
from hd.pix import Canvas as Canvas1x  # noqa: E402,F401  (llenços auxiliars en píxels de sala: figures, textos)

CEIL_H = 24
FLOOR_Y = 203
BOTTOM = 260                      # per sota hi ha la barra de verbs
LAMP_Y = 27
LAMPS = (147, 328, 533)
BLUEL = [(6, 10, 18), (12, 20, 34), (20, 32, 52), (32, 48, 72), (48, 68, 96), (70, 92, 122), (100, 122, 150)]
INWARM = [(20, 12, 8), (40, 26, 16), (66, 44, 28), (96, 68, 42), (130, 96, 62), (168, 128, 86), (204, 164, 116),
          (232, 200, 150)]
ENGG = [(4, 10, 8), (8, 18, 14), (12, 28, 22), (18, 42, 32), (28, 60, 46), (42, 84, 64)]
INK = (34, 30, 26)
_ENG_GLOW = {'k': 0.35}           # la llum verda de la sala de màquines (l'anima `maquines`)

LIGHT = Light(ambient=-0.35, vignette=(64, 32), floor_fade=(251, 53))
for _x in LAMPS:
    LIGHT.point(_x, CEIL_H + 5, r=168, k=2.3, squash=1.1, down=True, power=1.5)
LIGHT.point(40, 160, r=61, k=0.7, power=2.0)                 # la llum del menjador, per la porta
LIGHT.point(424, 13, r=67, k=0.5, power=2.0)                 # el forat del pont

# portes: (x0, y0, x1, y1)
D_MENJ = (16, 85, 67, FLOOR_Y)
D_INF = (112, 85, 165, FLOOR_Y)
D_LAB = (208, 85, 261, FLOOR_Y)
D_CAP = (296, 85, 349, FLOOR_Y)
D_PROA = (579, 83, 627, FLOOR_Y)
PLAQUE_Y = 66
CLOCK = (279, 107)
PORT_PROA = ((D_PROA[0] + D_PROA[2]) // 2 + 3, 115, 9)


# ─── Portes ─────────────────────────────────────────────────────────────────

def louvre(cv, x0, x1, y1, ramp, lvl):
    """La reixeta de ventilació de baix de les portes de cabina."""
    cx = (x0 + x1) // 2
    lx0, lx1 = cx - 11, cx + 11
    box(cv, lx0, y1 - 25, lx1, y1 - 11, ramp, lvl - 0.4)
    for y in range(y1 - 22, y1 - 13, 3):
        cv.hline(lx0 + 2, lx1 - 2, y, ramp, lvl - 2.0)
        cv.hline(lx0 + 2, lx1 - 2, y + 1, ramp, lvl + 0.9)
        cv.hline(lx0 + 2, lx1 - 2, y + 2, ramp, lvl - 0.6)
    for bx in (lx0 + 1, lx1 - 1):
        cv.put(bx, y1 - 24, ramp, lvl + 1.4)
        cv.put(bx, y1 - 12, ramp, lvl - 1.0)


def door_menjador(cv):
    x0, y0, x1, y1 = D_MENJ
    cx = (x0 + x1) // 2
    # a dins: la paret del menjador, càlida, el terra, la taula amb el cantell i dues tasses, i el llum
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if in_door(x, y, x0, y0, x1, y1, 11):
                v = 4.0 - abs(x - cx - 3) / 24 - (y - y0) / 107
                if y > 171:
                    v = 2.4 + (0.6 if (x + y) % 9 == 0 else 0) - (y - 171) * 0.01      # el terra de dins
                elif x % 21 == 5:
                    v -= 0.5                                                          # les quadernes
                cv.put(x, y, INWARM, v, lit=0)
    cv.rect(x0, 149, x1, 153, TEAK, 4.2, lit=0.3)                      # la taula
    cv.hline(x0, x1, 149, TEAK, 5.4, lit=0.3)
    cv.rect(x0, 154, x1, 157, TEAK, 2.2, lit=0.3)
    for lx in (27, 56):
        cv.vline(lx, 158, 170, TEAK, 1.6, lit=0.3)
        cv.vline(lx + 1, 158, 170, TEAK, 1.0, lit=0.3)
    for mx, c in ((30, [(80, 20, 20), (150, 40, 34), (200, 80, 60)]), (47, [(20, 40, 80), (40, 70, 130), (90, 120, 180)])):
        cv.rect(mx, 143, mx + 4, 148, c, 1.8, lit=0.4)                   # dues tasses
        cv.put(mx + 5, 145, c, 1.2, lit=0.4)
    cv.disc(cx, 99, 5, 2, [(160, 120, 60), (255, 230, 170), (255, 250, 230)], 1.6, lit=0)
    cv.vline(cx, y0 + 1, 96, CAB, 1.4, lit=0)
    glow(cv, cx, 101, 24, (255, 210, 140), 0.45)
    # la fulla, oberta contra la paret (de cantó)
    cv.poly([(x0 - 12, y0 + 5), (x0 - 4, y0 - 1), (x0 - 4, y1 - 3), (x0 - 12, y1 - 7)], DOORP,
            lambda x, y: 3.0 - (x0 - 4 - x) * 0.08)
    cv.vline(x0 - 12, y0 + 5, y1 - 7, DOORP, 1.6)
    cv.vline(x0 - 4, y0, y1 - 3, DOORP, 4.6)
    for dy in (y0 + 22, y1 - 30):
        box(cv, x0 - 10, dy, x0 - 6, dy + 4, BRASS, 3.0)                  # les frontisses
    door_frame(cv, x0, y0, x1, y1)
    sill(cv, x0, x1, y1, h=7)
    plaque(cv, cx, PLAQUE_Y, 'MENJADOR')


def door_closed(cv, rect, ramp, lvl, label, cross=False, seed=0, handle='right'):
    x0, y0, x1, y1 = rect
    leaf(cv, x0, y0, x1, y1 - 7, ramp, lvl, handle=handle, seed=seed)
    louvre(cv, x0, x1, y1 - 7, ramp, lvl)
    door_frame(cv, x0, y0, x1, y1)
    sill(cv, x0, x1, y1, h=7)
    for x in range(x0 + 4, x1 - 2, 9):                                   # cargols del llindar
        cv.put(x, y1 - 4, DOORP, 4.6)
    plaque(cv, (x0 + x1) // 2, PLAQUE_Y, label, cross=cross)


def door_infermeria(cv):
    x0, y0, x1, y1 = D_INF
    door_closed(cv, D_INF, WHITEP, 3.7, 'INFERMERIA', seed=1)
    # la creu vermella a la fulla, amb el cantell clar
    cx, cy = (x0 + x1) // 2 - 3, 113
    cv.rect(cx - 3, cy - 9, cx + 3, cy + 9, REDP, 4.2)
    cv.rect(cx - 9, cy - 3, cx + 9, cy + 3, REDP, 4.2)
    cv.hline(cx - 3, cx + 3, cy - 9, REDP, 5.4)
    cv.hline(cx - 9, cx + 9, cy - 3, REDP, 5.4)
    cv.vline(cx + 3, cy - 8, cy - 4, REDP, 3.0)
    cv.vline(cx + 9, cy - 2, cy + 3, REDP, 3.0)
    # un rètol petit a sota: «TRUCAR»
    w = text_width('TRUCAR') + 6
    box(cv, cx - w // 2, cy + 16, cx + w // 2, cy + 24, WHITEP, 4.8)
    text(cv, 'TRUCAR', cx - w // 2 + 3, cy + 18, None, 0, flat=(150, 40, 34))


def door_laboratori(cv):
    x0, y0, x1, y1 = D_LAB
    door_closed(cv, D_LAB, DOORP, 4.0, 'LABORATORI', seed=2)
    # l'adhesiu de risc biològic: rombe groc amb vora negra i el símbol
    cx, cy = (x0 + x1) // 2 - 3, 109
    cv.poly([(cx - 8, cy), (cx, cy - 8), (cx + 8, cy), (cx, cy + 8)], DARK, 1.2)
    cv.poly([(cx - 6, cy), (cx, cy - 6), (cx + 6, cy), (cx, cy + 6)], YELL, 4.2)
    cv.ring(cx, cy, 2, DARK, 0.8, step=30)
    for a in (90, 210, 330):
        cv.put(cx + round(math.cos(math.radians(a)) * 3.5), cy - round(math.sin(math.radians(a)) * 3.5), DARK, 0.8)
    cv.put(cx, cy, DARK, 0.8)
    # el peix (l'adhesiu de Mar Obert), amb l'ull i l'aleta
    px, py = cx - 8, cy + 19
    fish = [(20, 50, 80), (40, 90, 130), (90, 150, 190), (160, 210, 230)]
    cv.disc(px + 8, py, 8, 3, fish, lambda nx, ny: 2.6 - ny * 0.8)
    cv.poly([(px + 15, py), (px + 21, py - 4), (px + 20, py), (px + 21, py + 4)], fish, 2.2)
    cv.poly([(px + 7, py - 3), (px + 11, py - 6), (px + 12, py - 3)], fish, 1.6)
    cv.put(px + 3, py - 1, DARK, 0)
    cv.put(px + 3, py - 2, WHITEP, 5.0)
    for x in range(px + 6, px + 14, 2):                                  # les escates
        cv.put(x, py + 1, fish, 3.4)


def door_capitana(cv):
    x0, y0, x1, y1 = D_CAP
    # fulla de fusta envernissada, de dos plafons, amb la veta
    rrect(cv, x0, y0, x1, y1 - 7, 9, TEAK, lambda x, y: 4.0 - (y - y0) * 0.005)
    for y in range(y0 + 2, y1 - 8):
        for x in range(x0 + 2, x1 - 1):
            g = math.sin(x * 0.55 + math.sin(y * 0.07 + x * 0.03) * 2.6)
            if g > 0.82 and in_door(x, y, x0, y0, x1, y1, 9):
                cv.put(x, y, TEAK, 3.2)                                  # veta
    for py0, py1 in ((y0 + 8, y0 + 54), (y0 + 60, y1 - 15)):
        rrect(cv, x0 + 7, py0, x1 - 7, py1, 3, TEAK, lambda x, y: 3.6 - (y - py0) * 0.004)
        cv.hline(x0 + 8, x1 - 8, py0, TEAK, 2.2)                         # motllura: ombra a dalt i llum a baix
        cv.vline(x0 + 7, py0 + 2, py1 - 2, TEAK, 2.4)
        cv.hline(x0 + 8, x1 - 8, py1, TEAK, 5.0)
        cv.vline(x1 - 7, py0 + 2, py1 - 2, TEAK, 4.8)
    cv.vline(x1, y0 + 9, y1 - 7, TEAK, 2.0)
    cv.vline(x0, y0 + 9, y1 - 7, TEAK, 4.8)
    # el pom de llautó i l'escut
    hx, my = x1 - 10, (y0 + y1) // 2 + 6
    box(cv, hx - 1, my - 6, hx + 3, my + 8, BRASS, 2.8)
    cv.disc(hx + 1, my, 3, 3, BRASS, lambda nx, ny: 4.4 - nx - ny)
    cv.put(hx + 1, my + 5, DARK, 0.4)
    door_frame(cv, x0, y0, x1, y1)
    sill(cv, x0, x1, y1, h=7)
    plaque(cv, (x0 + x1) // 2, PLAQUE_Y, 'CAPITANA')
    # el paperet, amb cinta adhesiva: «TRUQUEU ABANS» i, a llapis, «I DESPRÉS NO ENTREU»
    px0, py0 = x0 + 11, 96
    box(cv, px0, py0, px0 + 29, py0 + 21, WHITEP, 4.6, edge=False)
    cv.vline(px0 + 29, py0 + 1, py0 + 21, WHITEP, 3.2)
    cv.darken(px0 + 1, py0 + 22, px0 + 30, py0 + 23, 0.6)
    text(cv, 'TRUQUEU', px0 + 2, py0 + 3, None, 0, flat=(40, 40, 48))
    text(cv, 'ABANS', px0 + 2, py0 + 10, None, 0, flat=(40, 40, 48))
    for x in range(px0 + 2, px0 + 27):                                    # el llapis, tort
        y = py0 + 17 + (1 if x > px0 + 14 else 0)
        if hr(x, y) > 0.3:
            cv.flat(x, y, (110, 110, 120))
    cv.rect(px0 + 10, py0 - 2, px0 + 18, py0 + 1, YELL, 4.6)             # cinta adhesiva
    cv.hline(px0 + 10, px0 + 18, py0 - 2, YELL, 5.4)


def door_proa(cv):
    x0, y0, x1, y1 = D_PROA
    pcx, pcy, pr = PORT_PROA
    leaf(cv, x0, y0, x1, y1 - 8, CREAM, 4.4, dogs=True, handle='left', seed=4, window=(pcx, pcy, pr, None))
    door_frame(cv, x0, y0, x1, y1, lvl=5.4)
    sill(cv, x0, x1, y1, CREAM, 3.6, h=8)
    for x in range(x0 + 4, x1 - 2, 9):
        cv.put(x, y1 - 5, CREAM, 5.0)
    # el rètol verd de sortida, amb la fletxa, i el cercle vermell de Mar Obert
    sign_box(cv, x0 + 1, 59, 'COBERTA', SEAG, 3.4, (220, 236, 226))
    glow(cv, x0 + 24, 66, 22, (80, 220, 140), 0.12)
    mx, my = x0 + 34, 175
    cv.disc(mx, my, 7, 7, WHITEP, 4.6)
    cv.disc(mx, my, 6, 6, REDP, 4.4)
    cv.disc(mx, my, 3, 3, WHITEP, 4.8)
    cv.put(mx - 2, my - 4, REDP, 5.6)


# ─── Les escales ────────────────────────────────────────────────────────────

ST_X0, ST_X1 = 373, 461            # el nínxol de l'escala del pont
HOLE = (387, 448)                  # el forat del sostre


def _along(y):
    """x del muntant de davant de l'escala a l'altura y (puja de dreta a esquerra)."""
    return 451 - (FLOOR_Y - y) * 0.28


def stairs_up(cv):
    """Escala de vaixell cap al pont: puja de dreta a esquerra i entra pel forat del sostre."""
    ax0, ax1 = ST_X0, ST_X1
    hx0, hx1 = HOLE
    for y in range(0, FLOOR_Y):
        for x in range(ax0, ax1 + 1):
            if y <= CEIL_H + 1 and hx0 <= x <= hx1:
                v = 3.2 + (CEIL_H - y) * 0.06
                if (x - hx0) % 19 == 0:
                    v -= 0.8                                               # els baos del sostre del pont
                cv.put(x, y, BLUEL, v, lit=0.2)
            elif y > CEIL_H + 1:
                cv.put(x, y, CREAM, 3.4 + (hr(x // 3, y // 5, 9) - 0.5) * 0.25
                       - (0.7 if x < ax0 + 4 or x > ax1 - 4 else 0))
    # el llum del pont, a dalt, que s'endevina pel forat (una claror, no un llum)
    glow(cv, 424, 4, 26, (150, 180, 220), 0.25)
    cv.vline(ax0, CEIL_H, FLOOR_Y, CREAM, 5.4)
    cv.vline(ax0 + 1, CEIL_H, FLOOR_Y, CREAM, 4.2)
    cv.vline(ax1, CEIL_H, FLOOR_Y, CREAM, 2.0)
    cv.vline(ax1 - 1, CEIL_H, FLOOR_Y, CREAM, 2.8)
    cv.hline(hx0, hx1, CEIL_H + 1, CREAM, 5.0)                            # el cantell del forat
    cv.hline(hx0, hx1, CEIL_H + 2, CREAM, 1.8)
    cv.hline(hx0, hx1, CEIL_H + 3, CREAM, 2.6)
    for y in range(CEIL_H + 4, CEIL_H + 40):                              # llum blavosa de dalt
        for x in range(hx0, hx1 + 1):
            k = 0.22 * (1 - (y - CEIL_H - 4) / 36)
            if k > 0:
                cv.flat(x, y, mix(cv.get(x, y), (150, 180, 220), k))
    # sòcol també al nínxol
    for y in range(171, FLOOR_Y):
        for x in range(ax0 + 2, ax1 - 1):
            cv.put(x, y, TEAK, 2.4 - (0.8 if (y - 171) % 8 == 0 else 0))
    # la barana de l'altra banda, contra la paret (més fosca)
    for y in range(0, FLOOR_Y - 40):
        cv.put(round(_along(y + 40)) - 20, y, CAB, 2.0)
        cv.put(round(_along(y + 40)) - 19, y, CAB, 2.6)
    # el muntant del darrere
    for y in range(0, FLOOR_Y + 1):
        for dx in range(-23, -19):
            cv.put(round(_along(y)) + dx, y, CAB, 2.0 + (0.6 if dx == -23 else 0))
    # graons: el pla de cada graó, el cantell groc antilliscant i l'ombra de sota
    for y in range(FLOOR_Y - 12, 8, -15):
        x = round(_along(y))
        cv.rect(x - 20, y, x, y + 2, CAB, 3.4)
        cv.hline(x - 20, x, y, CAB, 4.6)
        cv.rect(x - 5, y, x, y + 2, YELL, 4.2)
        for xx in range(x - 19, x - 5, 3):                                # el relleu de l'antilliscant
            cv.put(xx, y + 1, CAB, 4.2)
        cv.darken(x - 20, y + 3, x, y + 6, 0.55)
    # el muntant de davant (llisera), amb volum
    for y in range(0, FLOOR_Y + 1):
        x = round(_along(y))
        for dx in range(0, 8):
            cv.put(x + dx, y, CAB, 3.6 + (1.1 if dx == 0 else 0.5 if dx == 1 else -0.9 if dx >= 6 else 0))
        if y % 15 == 7:
            cv.put(x + 3, y, CAB, 5.0)                                     # els cargols dels graons
    # barana de davant (tub) amb els puntals
    for y in range(0, FLOOR_Y - 37):
        x = round(_along(y + 40)) + 4
        cv.put(x, y, CAB, 4.6)
        cv.put(x + 1, y, CAB, 3.6)
        cv.put(x + 2, y, CAB, 2.4)
    for y in range(FLOOR_Y - 45, 0, -53):
        for t in range(0, 40):
            cv.put(round(_along(y + t)) + 3, y + t, CAB, 4.0)
            cv.put(round(_along(y + t)) + 4, y + t, CAB, 2.6)
    box(cv, round(_along(FLOOR_Y)) - 3, FLOOR_Y - 4, round(_along(FLOOR_Y)) + 11, FLOOR_Y + 1, CAB, 2.8)
    plaque(cv, 403, 149, 'PONT')


def plan_board(cv):
    """El plànol d'emergència del vaixell, verd i blanc, emmarcat, amb el «sou aquí»."""
    x0, y0, x1, y1 = 476, 66, 552, 116
    box(cv, x0, y0, x1, y1, CAB, 3.0)
    box(cv, x0 + 2, y0 + 2, x1 - 2, y1 - 2, WHITEP, 4.6, edge=False)
    cv.rect(x0 + 2, y0 + 2, x1 - 2, y0 + 12, SEAG, 3.0)
    text(cv, 'EMERGÈNCIA', x0 + 9, y0 + 6, None, 0, flat=(226, 240, 230))
    # el casc del vaixell, de perfil, amb les cobertes
    hy = y0 + 30
    cv.poly([(x0 + 6, hy), (x1 - 5, hy - 2), (x1 - 13, hy + 11), (x0 + 12, hy + 11)], WHITEP, 3.6)
    cv.line(x0 + 6, hy, x1 - 5, hy - 2, DARK, 1.0)
    cv.line(x1 - 5, hy - 2, x1 - 13, hy + 11, DARK, 1.0)
    cv.line(x0 + 6, hy, x0 + 12, hy + 11, DARK, 1.0)
    cv.line(x0 + 12, hy + 11, x1 - 13, hy + 11, DARK, 1.0)
    cv.hline(x0 + 10, x1 - 11, hy + 5, DARK, 2.4)                         # la coberta principal
    cv.rect(x0 + 22, hy - 11, x0 + 42, hy - 1, WHITEP, 3.8)              # el pont
    cv.hline(x0 + 22, x0 + 42, hy - 11, DARK, 1.0)
    cv.vline(x0 + 22, hy - 11, hy, DARK, 1.0)
    cv.vline(x0 + 42, hy - 11, hy, DARK, 1.0)
    cv.vline(x0 + 36, hy - 17, hy - 11, DARK, 1.6)                       # el pal
    # les rutes d'evacuació, en verd, amb fletxes
    for x in range(x0 + 10, x1 - 10, 4):
        cv.put(x, hy + 3, SEAG, 4.2)
        cv.put(x + 1, hy + 3, SEAG, 4.2)
    cv.poly([(x1 - 12, hy + 1), (x1 - 8, hy + 3), (x1 - 12, hy + 5)], SEAG, 4.2)
    for ex in (x0 + 18, x1 - 22):                                         # les balses
        cv.rect(ex, hy - 4, ex + 4, hy - 2, (REDP), 4.0)
    cv.rect(x0 + 45, hy + 1, x0 + 48, hy + 4, REDP, 4.6, lit=0.3)        # «sou aquí»
    cv.put(x0 + 46, hy + 2, WHITEP, 6.0, lit=0)
    # la llegenda
    for i, y in enumerate((y1 - 8, y1 - 5)):
        cv.rect(x0 + 6, y, x0 + 8, y + 1, SEAG if i == 0 else REDP, 4.0)
        for x in range(x0 + 11, x0 + 28 + i * 6):
            if hr(x, y) > 0.3:
                cv.flat(x, y, (110, 110, 116))
    for bx, by in ((x0 + 1, y0 + 1), (x1 - 1, y0 + 1), (x0 + 1, y1 - 1), (x1 - 1, y1 - 1)):
        cv.put(bx, by, CAB, 5.2)
    copies(cv)


COPIES = (500, 119, 528, 131)


def copies(cv):
    """Sota el plànol, el portafulls de plàstic amb les còpies plastificades (des de l'Escena 6, se n'agafa una)."""
    x0, y0, x1, y1 = COPIES
    for i, dy in enumerate((0, 1, 2)):                                     # tres còpies, una mica desplaçades
        cv.rect(x0 + 2 + i, y0 + dy, x1 - 2 - (2 - i), y0 + 5 + dy, WHITEP, 4.4 - i * 0.3)
        cv.hline(x0 + 2 + i, x1 - 2 - (2 - i), y0 + dy, SEAG, 3.0)
    box(cv, x0, y0 + 4, x1, y1, CAB, 2.4)                                   # la butxaca, fosca i transparent
    cv.rect(x0 + 2, y0 + 6, x1 - 2, y1 - 2, WHITEP, 3.2)
    cv.hline(x0 + 3, x1 - 3, y0 + 7, SEAG, 2.6)
    cv.line(x0 + 4, y1 - 3, x0 + 10, y0 + 6, WHITEP, 5.6)                  # el reflex del plàstic


def stairs_down(cv):
    """El forat de l'escala de baix, arran de la paret, amb la barana groga i la llum verda de les màquines."""
    hx0, hx1, hy0, hy1 = 472, 552, 208, 229
    pts = [(hx0 + 5, hy0), (hx1 - 5, hy0), (hx1, hy1), (hx0, hy1)]
    cv.poly(pts, ENGG, lambda x, y: 1.0 + (y - hy0) * 0.045, lit=0)
    # graons que baixen (de cara), cada cop més foscos, amb el cantell groc
    for i, y in enumerate(range(hy0 + 3, hy1 - 1, 5)):
        cv.hline(hx0 + 10 + i, hx1 - 10 - i, y, CAB, 2.6 - i * 0.4, lit=0.3)
        cv.hline(hx0 + 10 + i, hx1 - 10 - i, y + 1, CAB, 1.8 - i * 0.4, lit=0.3)
        cv.hline(hx0 + 10 + i, hx1 - 10 - i, y, YELL, 2.0 - i * 0.5, lit=0.3)
    glow(cv, (hx0 + hx1) // 2, hy1 - 3, 24, (90, 200, 140), _ENG_GLOW['k'])
    # el cantell (brazola) del forat
    cv.line(hx0, hy1, hx1, hy1, CAB, 4.2)
    cv.line(hx0, hy1 + 1, hx1, hy1 + 1, CAB, 2.6)
    cv.line(hx0, hy1 + 2, hx1, hy1 + 2, CAB, 1.6)
    cv.line(hx0 + 5, hy0, hx0, hy1, CAB, 3.2)
    cv.line(hx1 - 5, hy0, hx1, hy1, CAB, 2.6)
    # barana: puntals i dos tubs grocs, el de davant amb les ratlles negres
    for px, py in ((hx0, hy1), (hx0 + 5, hy0), (hx1, hy1), (hx1 - 5, hy0)):
        vpipe(cv, px, py - 40, py, 1, YELL, 3.6 if py == hy1 else 2.6)
        box(cv, px - 2, py - 1, px + 2, py + 1, CAB, 3.0)                 # la base del puntal
    for dy in (40, 20):
        cv.line(hx0 + 5, hy0 - dy, hx0, hy1 - dy, YELL, 3.4)
        cv.line(hx1 - 5, hy0 - dy, hx1, hy1 - dy, YELL, 2.8)
        cv.line(hx0 + 5, hy0 - dy, hx1 - 5, hy0 - dy, YELL, 2.4)
    hpipe(cv, hx0, hx1, hy1 - 40, 1, YELL, 3.8)
    hpipe(cv, hx0, hx1, hy1 - 20, 1, YELL, 3.2)
    for x in range(hx0 + 3, hx1 - 2, 13):
        cv.rect(x, hy1 - 41, x + 4, hy1 - 39, DARK, 1.6)
    cv.darken(hx0 - 3, hy1 + 3, hx1 + 3, hy1 + 8, lambda x, y: 0.6 - (y - hy1 - 3) * 0.1)


# ─── Petites coses ─────────────────────────────────────────────────────────

def extinguisher(cv, x, y):
    """Extintor vermell penjat a la paret (x, y: cantó de dalt a l'esquerra), amb el suport, la mànega i l'etiqueta."""
    box(cv, x - 2, y + 9, x + 14, y + 12, CAB, 3.0)                       # la brida
    for yy in range(y + 6, y + 40):
        for xx in range(x, x + 13):
            u = (xx - x - 6) / 6.5
            cv.put(xx, yy, REDP, 3.6 + 1.3 * (-0.3 - u) - 0.7 * u * u)
    cv.disc(x + 6, y + 6, 6, 3, REDP, lambda nx, ny: 4.4 - nx - ny)
    box(cv, x + 3, y, x + 9, y + 4, CAB, 3.4)                            # la vàlvula i el gallet
    cv.line(x + 9, y + 1, x + 15, y + 3, CAB, 3.6)
    cv.put(x + 4, y - 1, YELL, 4.6)                                      # el passador
    for i, yy in enumerate(range(y + 4, y + 30)):                        # la mànega
        cv.put(x + 15 + (1 if 8 < i < 20 else 0), yy, DARK, 2.4)
    box(cv, x + 13, y + 30, x + 17, y + 34, DARK, 2.0)
    box(cv, x + 2, y + 16, x + 10, y + 26, WHITEP, 4.2)                  # l'etiqueta
    cv.hline(x + 3, x + 9, y + 18, REDP, 3.0)
    for yy in (y + 21, y + 23):
        cv.hline(x + 3, x + 9, yy, DARK, 2.0)
    cv.hline(x, x + 12, y + 39, REDP, 1.8)


def clock(cv):
    """Rellotge de vaixell de llautó, entre la porta del laboratori i la de la Capitana."""
    cx, cy = CLOCK
    cv.disc(cx, cy, 10, 10, BRASS, lambda nx, ny: 3.4 - nx - ny)
    cv.disc(cx, cy, 8, 8, WHITEP, lambda nx, ny: 4.8 - ny * 0.3)
    for a in range(0, 360, 30):
        d = 7 if a % 90 else 6
        cv.put(cx + round(math.sin(math.radians(a)) * d), cy - round(math.cos(math.radians(a)) * d), CAB, 1.2)
    for a in range(30, 360, 60):                                         # els cargols del bisell
        cv.put(cx + round(math.cos(math.radians(a)) * 9), cy + round(math.sin(math.radians(a)) * 9), BRASS, 5.0)
    cv.line(cx, cy, cx, cy - 6, DARK, 0)                                 # les dotze i quart
    cv.line(cx, cy, cx + 4, cy + 1, DARK, 0)


# ─── Muntatge ───────────────────────────────────────────────────────────────

def bg(cv):
    ceiling(cv)
    wall(cv, seed=1)
    wear(cv, 0, 40, W - 1, 168, 40, seed=1, k=0.25)
    door_menjador(cv)
    extinguisher(cv, 82, 128)
    door_infermeria(cv)
    door_laboratori(cv)
    door_capitana(cv)
    stairs_up(cv)
    plan_board(cv)
    door_proa(cv)
    clock(cv)
    for lx in LAMPS:
        lamp(cv, lx, LAMP_Y)
    mask = lino(cv, lvl=4.0)
    for x0, _, x1, _ in (D_MENJ, D_INF, D_LAB, D_CAP, D_PROA):
        foot_shadow(cv, x0 - 4, x1 + 4, FLOOR_Y + 1, 4, 0.5)
    foot_shadow(cv, 0, W - 1, FLOOR_Y + 1, 5, 0.35)
    shine(cv, mask, LAMPS)
    before = cv.img.copy()
    stairs_down(cv)
    unmask(mask, cv, 453, 160, 560, 240, before)
    for lx in LAMPS:
        lamp_glow(cv, lx, LAMP_Y)


# Escenes 2 i 3: de dia, l'ull de bou de la porta de coberta clar
PROPS = {'ulls_dia': lambda cv: day_porthole(cv, *PORT_PROA)}


# ─── Animacions ─────────────────────────────────────────────────────────────

def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv


def _frames_rellotge():
    """El rellotge del passadís: l'agulla dels segons (un fotograma per segon)."""
    base = _base()
    frames = []
    for s in range(60):
        cv = Canvas(light=LIGHT, img=base.img.copy())
        second_hand(cv, CLOCK[0], CLOCK[1], s, r=6)
        frames.append(_diff(cv.img, base.img))
    return frames


def _frames_maquines():
    """La llum verda de la sala de màquines, pel forat de l'escala, respira amb el motor."""
    base = _base()
    frames = []
    for i in range(12):
        _ENG_GLOW['k'] = 0.35 + 0.14 * math.sin(2 * math.pi * i / 12)
        frames.append(_diff(_base().img, base.img))
    _ENG_GLOW['k'] = 0.35
    return frames


ANIMS = {'rellotge': {'frames': _frames_rellotge, 'frameDuration': 1000},
         'maquines': {'frames': _frames_maquines, 'frameDuration': 200}}


# ─── Geometria (640×360) ────────────────────────────────────────────────────

GEOMETRIA = {
    'things': {
        'porta_menjador': {'rect': (11, 61, 72, FLOOR_Y), 'walk': (43, 237)},
        'porta_infermeria': {'rect': (107, 61, 171, FLOOR_Y), 'walk': (139, 237)},
        'porta_laboratori': {'rect': (203, 61, 267, FLOOR_Y), 'walk': (235, 237)},
        'porta_capitana': {'rect': (291, 61, 355, FLOOR_Y), 'walk': (323, 237)},
        'escala_amunt': {'rect': (376, 5, 459, FLOOR_Y), 'walk': (429, 237)},
        'escala_avall': {'rect': (467, 165, 557, 232), 'walk': (512, 245)},
        'porta_proa': {'rect': (573, 59, 632, FLOOR_Y), 'walk': (603, 237)},
        'planol': {'rect': (474, 64, 554, 132), 'walk': (514, 237)},
    },
    'spawns': {'iri': (309, 251), 'vet': (387, 256)},
    'walkable': [(8, 224), (461, 224), (461, 237), (560, 237), (560, 224), (635, 224), (635, 263), (8, 263)],
}
