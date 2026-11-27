"""
**El dibuix pla de sempre** (font de les textures de la sala en 3D, pont.py).

Prova de resolució: el pont de l'Arenga a 640×360 (×4/3 de hd/rooms/pont.py, amb més detall).

Mateixa forma que la de 480: LIGHT, LIGHT_DIA, bg, PROPS (`dia`, `safata`, `guardacostes`, `fosc`), ANIMS (`radar`,
`terminal`, `mar`) i GEOMETRIA. Com a 480, de dia (`dia`) el mar no es mou: el decorat deixa forats a les pantalles
del radar i del terminal, i s'hi veuen les animacions de sota.
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from hd640 import W, H
from hd.pix import Canvas, Light, hr, mix
from hd.rooms.arenga import CAB, ENG, DARK, WHITEP, REDP, YELL, BRASS, WARM, box, rrect, bolt, vpipe, glow
from hd.rooms.comu import _diff, text
from hd.rooms.exterior import day_sky, day_sea
from hd.rooms.pont import BRI, AMB, SCRG, WOOD, FLOORB, NSKY, NSEA
from hd640.rooms.sala_radio_pla_comu import door_frame

from hd.pix import Canvas  # noqa: E402,F811  (a 1×: és la font de les textures de la sala en 3D)
Canvas1x = Canvas

GREENL = (90, 240, 140)
PAPERY = [(60, 56, 46), (120, 114, 96), (176, 168, 140), (214, 206, 176), (236, 230, 204)]
CABLE = [(6, 6, 8), (16, 16, 20), (30, 30, 36), (48, 48, 56), (72, 72, 80)]

FLOOR_Y = 203                         # 152 × 4/3
CON_TOP = 144                         # 108 × 4/3
WIN = (157, 32, 483, 128)             # els vidres (rectangle exterior dels marcs)
PANES = ((163, 237), (245, 320), (328, 403), (411, 477))
HORIZON = 93
MOON = (200, 53)
LAMP = (400, 13)                      # el llum de sostre (vermellós, de nit)
RADAR = (200, 123)
SCREEN = (341, 107, 395, 133)         # la pantalla del terminal

_MODE = {'dia': False}
_ANIM = {'mar': 0, 'radar': 0, 'terminal': 0}     # fotograma de cada animació (0 = el fons quiet)
MAR_N, RADAR_N = 12, 12

LIGHT = Light(ambient=0.35, vignette=(80, 34), floor_fade=None)
LIGHT.point(400, 16, r=226, k=2.0, squash=1.1, down=True, power=1.5)     # llum de sostre, esmorteït
LIGHT.point(368, 149, r=80, k=0.9, power=1.8)                            # pantalla del terminal
LIGHT.point(200, 149, r=67, k=0.7, power=1.8)                            # el radar
LIGHT.point(40, 200, r=80, k=0.7, power=1.8)                             # la llum que puja de l'escala
LIGHT.point(320, 80, r=266, k=0.5, squash=1.4, power=1.2)                # la claror de fora (lluna)

LIGHT_DIA = Light(ambient=1.2, vignette=(80, 34), floor_fade=None)
LIGHT_DIA.point(320, 75, r=373, k=1.9, squash=1.3, power=1.2)            # la claror grisa dels vidres
LIGHT_DIA.point(40, 200, r=80, k=0.4, power=1.8)                         # la llum que puja de l'escala


# ─── Fora: cel i mar ─────────────────────────────────────────────────────────

def _cloud(x, y):
    """Densitat de núvols (0..1): bandes horitzontals deformades (a l'escala de 640)."""
    v = math.sin(x * 0.023 + math.sin(y * 0.16) * 2.2 + y * 0.09) * 0.5 + 0.5
    v *= math.sin(x * 0.010 - y * 0.037 + 1.3) * 0.5 + 0.5
    return v + (hr(x // 8, y // 4) - 0.5) * 0.25


def _night(cv, x0, y0, x1, y1, t=0.0):
    mx, my = MOON
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if y < HORIZON:
                d = math.hypot(x - mx, (y - my) * 1.4)
                lvl = 3.4 + (y - 13) * 0.022 + max(0, 1 - d / 120) * 3.2     # (la claror de la lluna)
                c = _cloud(x, y)
                if c > 0.55:
                    lvl += (c - 0.55) * 4.0 * (0.6 + max(0, 1 - d / 120) * 1.6)
                if d < 7 and c < 0.75:
                    lvl = 7.4 - d * 0.22                       # la lluna, entre núvols
                    if d < 6 and hr(x // 2, y // 2, 7) > 0.8:
                        lvl -= 0.8                             # taques de la lluna
                if HORIZON - y < 6:
                    lvl += 0.6                                 # boirina a l'horitzó
                cv.put(x, y, NSKY, lvl, lit=0)
            else:
                dd = y - HORIZON
                lvl = 3.4 - dd * 0.02 + max(0.0, 1 - abs(x - mx) / 150) * 0.8
                ph = math.sin(x * (0.135 - dd * 0.0011) + dd * 0.68 + math.sin(x * 0.038 + dd * 0.22) * 1.6 + t)
                if ph > 0.7:
                    lvl += 0.9
                elif ph < -0.6:
                    lvl -= 0.5
                w = 13 + dd * 1.5                              # el camí de la lluna
                g = math.exp(-((x - mx) / w) ** 2)
                if g > 0.15 and ph > 0.4 and hr(x // 2, y, int(t * 2) % 7) < g * 0.9:
                    lvl += 3.0 * g
                cv.put(x, y, NSEA, lvl, lit=0)
    if y0 <= HORIZON <= y1:
        for x in range(x0, x1 + 1):
            cv.put(x, HORIZON, NSEA, 3.0 + (0.8 if abs(x - mx) < 24 else 0), lit=0)
    if x0 <= mx <= x1 and y0 <= my <= y1:
        glow(cv, mx, my, 30, (170, 184, 214), 0.5)


@functools.lru_cache(maxsize=None)
def _day():
    """El cel i el mar de dia, de tota l'amplada."""
    cv = Canvas()
    day_sky(cv, 5, HORIZON - 1, seed=13)
    day_sea(cv, HORIZON, H - 1, seed=6)
    return cv.img


def outside(cv, x0, y0, x1, y1):
    if _MODE['dia']:
        src, dst = _day().load(), cv.P
        for X, Y, x, y in cv.pixels(x0, y0, x1, y1):
            dst[X, Y] = src[X, Y]
        return
    _night(cv, x0, y0, x1, y1, t=_ANIM['mar'] * 2 * math.pi / MAR_N)


# ─── Parets i sostre ─────────────────────────────────────────────────────────

def wall(cv):
    for y in range(0, FLOOR_Y):
        for x in range(W):
            lvl = 3.4 + (hr(x // 3, y // 5) - 0.5) * 0.3
            if y >= 181:
                lvl -= 0.8
            cv.put(x, y, BRI, lvl)
    for fx in range(-26, W, 74):                       # costures de les planxes i reblons
        cv.vline(fx, 24, FLOOR_Y - 1, BRI, 2.2)
        cv.vline(fx + 1, 24, FLOOR_Y - 1, BRI, 4.2)
        for y in range(34, 178, 18):
            bolt(cv, fx + 4, y, BRI, 3.8)
            bolt(cv, fx - 4, y + 9, BRI, 3.6)
    for fx in range(-26, W, 74):                       # rovell a les costures de baix
        for y in range(160, 180):
            if hr(fx, y, 3) > 0.84:
                cv.put(fx + 2, y, [(40, 22, 16), (80, 44, 26), (120, 70, 36)], 1.2)
    cv.hline(0, W - 1, 180, BRI, 4.4)
    cv.hline(0, W - 1, 181, BRI, 2.0)
    cv.hline(0, W - 1, FLOOR_Y - 1, BRI, 1.0)


def ceiling(cv):
    cv.rect(0, 0, W - 1, 23, DARK, 2.2)
    for bx in range(-13, W, 74):                       # baos
        box(cv, bx - 3, 0, bx + 8, 25, BRI, 2.0, grad=0.8)
        cv.hline(bx - 2, bx + 7, 25, BRI, 1.0)
    cv.hline(0, W - 1, 24, BRI, 1.2)
    cv.hline(0, W - 1, 25, BRI, 3.0)
    lx = LAMP[0]                                       # el llum de sostre, amb filtre vermell
    box(cv, lx - 13, 11, lx + 13, 17, CAB, 2.6)
    if _MODE['dia']:
        cv.rect(lx - 11, 17, lx + 11, 20, [(60, 14, 12), (90, 50, 46), (120, 96, 92)], 1.6)
    else:
        cv.rect(lx - 11, 17, lx + 11, 20, [(60, 14, 12), (130, 30, 24), (200, 70, 50), (250, 140, 110)], 2.4, lit=0)


def repeaters(cv):
    """La fila d'instruments penjats sobre els vidres: giroscòpica, vent, angle del timó, rellotge, ecosonda."""
    box(cv, 200, 3, 453, 21, ENG, 2.0, grad=0.5)
    cv.hline(203, 450, 4, ENG, 3.4)
    for bx in (206, 447):
        cv.vline(bx, 0, 3, CAB, 2.4)
    for i, cx in enumerate((224, 275, 325, 376, 427)):
        cy = 12
        cv.disc(cx, cy, 8, 8, CAB, lambda nx, ny: 1.6 - ny * 0.4)
        cv.ring(cx, cy, 8, CAB, 3.2, step=10)
        if i == 0:                                     # giroscòpica: rosa ambre amb les marques
            cv.disc(cx, cy, 6.5, 6.5, AMB, lambda nx, ny: 2.6 - ny * 0.6, lit=0)
            for a in range(0, 360, 45):
                cv.put(cx + round(math.cos(math.radians(a)) * 5), cy + round(math.sin(math.radians(a)) * 5), AMB, 4.4, lit=0)
            cv.vline(cx, cy - 6, cy, DARK, 0, lit=0)
            cv.put(cx, cy - 7, REDP, 4.4, lit=0)
        elif i == 3:                                   # rellotge
            cv.disc(cx, cy, 6.5, 6.5, WHITEP, 3.4)
            for a in range(0, 360, 30):
                cv.put(cx + round(math.cos(math.radians(a)) * 5.5), cy + round(math.sin(math.radians(a)) * 5.5), DARK, 1.0)
            cv.line(cx, cy, cx, cy - 4, DARK, 0)
            cv.line(cx, cy, cx + 3, cy + 1, DARK, 0)
        else:                                          # vent, timó, ecosonda: digitals
            cv.disc(cx, cy, 6.5, 6.5, SCRG, 0.8, lit=0)
            num = {1: '24', 2: '03', 4: '86'}[i]
            text(cv, num, cx - 3, cy - 2, SCRG, 4.0, lit=0)
        glow(cv, cx, cy, 12, (120, 200, 160) if i in (1, 2, 4) else (230, 170, 80), 0.25)


# ─── Els vidres ──────────────────────────────────────────────────────────────

def windows(cv):
    x0, y0, x1, y1 = WIN
    box(cv, x0, y0, x1, y1, BRI, 4.0)
    for a, b in PANES:
        rrect(cv, a, y0 + 5, b, y1 - 5, 5, DARK, 1.0)
        outside(cv, a + 1, y0 + 6, b - 1, y1 - 6)
        for y in range(y0 + 5, y1 - 4):                # la goma del vidre (cantons rodons)
            for x in range(a, b + 1):
                dx = max(a + 5 - x, 0, x - (b - 5))
                dy = max(y0 + 10 - y, 0, y - (y1 - 10))
                d = math.hypot(dx, dy)
                if 4 <= d <= 5.8 or (dx == 0 and dy == 0 and (x in (a, b) or y in (y0 + 5, y1 - 5))):
                    cv.put(x, y, DARK, 0.6, lit=0)
        for k in (0, 9, 13):                           # reflex del vidre: ratlles en diagonal
            for i in range(36 if k != 13 else 18):
                x, y = a + 10 + k + i, y1 - 13 - i
                if a < x < b and y0 + 8 < y < y1 - 8 and hr(i, k, a) > 0.35:
                    cv.flat(x, y, mix(cv.get(x, y)[:3], (230, 234, 236) if _MODE['dia'] else (150, 176, 220),
                                      0.18 if _MODE['dia'] else 0.32))
        for i in range(10):                            # gotes de sal seques
            sx, sy = a + 4 + int(hr(i, a, 1) * (b - a - 8)), y0 + 10 + int(hr(i, a, 2) * (y1 - y0 - 20))
            cv.flat(sx, sy, mix(cv.get(sx, sy)[:3], (200, 206, 212), 0.25 if _MODE['dia'] else 0.15))
    # el «clear view», un disc giratori al segon vidre, amb el motor al mig
    cv.ring(283, 61, 15, BRI, 3.0, lit=0.5, step=3)
    cv.ring(283, 61, 14, BRI, 1.6, lit=0.3, step=4)
    cv.disc(283, 61, 3, 3, CAB, lambda nx, ny: 4.0 - nx - ny)
    # eixugaparabrises al tercer i quart
    for a, b in PANES[2:]:
        cv.line(a + 11, y1 - 8, (a + b) // 2 + 13, y0 + 19, DARK, 1.4, lit=0)
        cv.line(a + 12, y1 - 8, (a + b) // 2 + 14, y0 + 19, DARK, 0.6, lit=0)
        cv.disc(a + 11, y1 - 8, 2, 2, CAB, 3.4)
    # el marc de dalt, més gruixut, i l'ampit
    cv.hline(x0, x1, y0 + 1, BRI, 5.2)
    box(cv, x0 - 5, y1 + 1, x1 + 5, y1 + 7, BRI, 4.6)
    cv.hline(x0 - 5, x1 + 5, y1 + 8, BRI, 1.0)


# ─── La consola ──────────────────────────────────────────────────────────────

def console(cv):
    x0, x1 = 149, 488
    box(cv, x0, CON_TOP, x1, FLOOR_Y + 3, ENG, 2.6, grad=1.0)
    cv.poly([(x0, CON_TOP - 8), (x1, CON_TOP - 8), (x1 + 3, CON_TOP), (x0 - 3, CON_TOP)], ENG,
            lambda x, y: 3.8 + (y - CON_TOP) * 0.06)
    cv.hline(x0 - 3, x1 + 3, CON_TOP - 8, ENG, 4.8)
    cv.hline(x0 - 3, x1 + 3, CON_TOP + 1, ENG, 1.2)
    for dx in range(157, 470, 53):                     # portes de servei del frontal
        rrect(cv, dx, 157, dx + 45, 195, 3, ENG, lambda x, y: 2.2 - (y - 157) * 0.015)
        cv.hline(dx + 3, dx + 42, 157, ENG, 3.4)
        for y in range(165, 189, 3):
            cv.hline(dx + 8, dx + 37, y, ENG, 1.2)
        box(cv, dx + 40, 170, dx + 42, 179, CAB, 3.2)
        for bx, by in ((dx + 3, 160), (dx + 42, 160), (dx + 3, 192), (dx + 42, 192)):
            cv.put(bx, by, ENG, 4.0)
    cv.rect(x0, FLOOR_Y - 3, x1, FLOOR_Y + 3, DARK, 1.4)                # sòcol
    for i, x in enumerate(range(157, 480, 8)):         # commutadors i pilots damunt del frontal inclinat
        if 164 <= x <= 238 or 330 <= x <= 404:
            continue
        cv.rect(x, CON_TOP - 6, x + 4, CON_TOP - 3, CAB, 1.6)
        cv.hline(x + 1, x + 3, CON_TOP - 6, CAB, 4.4)
        if hr(i, 3) > 0.6:
            col = GREENL if hr(i, 4) > 0.4 else (255, 180, 60)
            cv.flat(x + 2, CON_TOP - 2, col)
            cv.flat(x + 1, CON_TOP - 2, mix(col, (0, 0, 0), 0.5))


def _sweep(cv, cx, cy, ang, r0=16):
    for r in range(1, r0):
        for k, lv in ((0, 4.6), (1, 3.6), (2, 2.8), (3, 2.2)):
            a = math.radians(ang - k * 9)
            cv.put(cx + round(math.cos(a) * r), cy + round(math.sin(a) * r), SCRG, lv, lit=0)


def radar(cv):
    """El radar: la caixa, la pantalla rodona amb la costa a l'est, els ecos i el feix que gira."""
    cx, cy = RADAR
    ang = 30 + _ANIM['radar'] * 360 / RADAR_N
    box(cv, 166, 98, 234, CON_TOP - 7, CAB, 2.4, grad=0.6)
    cv.hline(167, 233, 99, CAB, 3.8)
    rrect(cv, 179, 102, 221, 106, 1, DARK, 1.2)                   # la visera
    cv.disc(cx, cy, 17, 17, DARK, 1.0)
    cv.disc(cx, cy, 16, 16, SCRG, lambda nx, ny: 1.1 - math.hypot(nx, ny) * 0.3, lit=0)
    for r in (5, 10, 15):
        cv.ring(cx, cy, r, SCRG, 2.0, lit=0, step=9)
    for a in range(0, 360, 30):                         # la rosa de rumbs, a la vora
        cv.put(cx + round(math.cos(math.radians(a)) * 16), cy + round(math.sin(math.radians(a)) * 16), SCRG, 3.0, lit=0)
    cv.vline(cx, cy - 15, cy - 1, SCRG, 2.4, lit=0)              # la línia de proa
    for i in range(12):                                 # la costa, a l'est
        x = cx + 11 + round(math.sin(i * 0.7) * 1.5) + (i // 6)
        y = cy - 9 + i * 2
        if (x - cx) ** 2 + (y - cy) ** 2 < 15.5 ** 2:
            cv.put(x, y, SCRG, 3.4, lit=0)
            cv.put(x + 1, y, SCRG, 2.6, lit=0)
    for ex, ey in ((cx + 8, cy - 5), (cx - 7, cy + 9), (cx + 3, cy + 12), (cx - 10, cy - 6)):   # ecos
        a = (math.degrees(math.atan2(ey - cy, ex - cx)) - ang) % 360
        cv.put(ex, ey, SCRG, 4.8 if a > 300 else 3.0, lit=0)
        cv.put(ex + 1, ey, SCRG, 3.6 if a > 300 else 2.2, lit=0)
    _sweep(cv, cx, cy, ang)
    text(cv, '6NM', 223, 133, SCRG, 4.0, lit=0)
    for bx in (173, 182):
        cv.disc(bx, 133, 2, 2, CAB, lambda nx, ny: 3.8 - nx - ny)
    glow(cv, cx, cy, 27, (90, 220, 140), 0.25)


def wheel(cv):
    """El timó: pedestal davant la consola i una roda petita de fusta amb puny de llautó."""
    cx, cy = 269, 160
    box(cv, 259, 176, 280, FLOOR_Y + 5, ENG, 2.8, grad=0.8)
    cv.hline(259, 280, 176, ENG, 4.2)
    box(cv, 263, 182, 276, 188, BRASS, 2.8)                       # la placa de llautó
    box(cv, 253, FLOOR_Y + 3, 285, FLOOR_Y + 8, ENG, 2.0)
    for a in range(0, 360, 1):
        for rr in (16, 17):
            x = cx + round(math.cos(math.radians(a)) * rr)
            y = cy + round(math.sin(math.radians(a)) * rr * 0.92)
            cv.put(x, y, WOOD, 4.0 - math.sin(math.radians(a)) * 1.2 - (rr - 16) * 0.8)
    for a in range(0, 360, 45):
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        cv.line(cx, cy, cx + round(ca * 16), cy + round(sa * 15), WOOD, 3.2)
        cv.line(cx + round(ca * 17), cy + round(sa * 16), cx + round(ca * 21), cy + round(sa * 20), WOOD, 4.4)
        cv.put(cx + round(ca * 21), cy + round(sa * 20), WOOD, 5.4)
    cv.disc(cx, cy, 4, 4, BRASS, lambda nx, ny: 4.0 - nx - ny)
    cv.put(cx, cy - 18, BRASS, 5.0)                              # la marca de timó al mig


def screen(cv):
    x0, y0, x1, y1 = SCREEN
    cv.rect(x0, y0, x1, y1, SCRG, lambda x, y: 1.0 + (0.3 if y % 2 else 0), lit=0)
    text(cv, 'SAT-C', x0 + 3, y0 + 3, SCRG, 4.6, lit=0)
    cv.hline(x0 + 25, x0 + 36, y0 + 5, SCRG, 3.0, lit=0)
    for j, w in enumerate((30, 22, 26)):                         # línies de text
        cv.hline(x0 + 3, x0 + 3 + w, y0 + 10 + j * 3, SCRG, 2.6, lit=0)
    for i in range(10):                                         # la barra de senyal: 10 graons que pugen
        bx = x0 + 3 + i * 4
        h = 2 + i * 2 // 3
        cv.rect(bx, y1 - 3 - h, bx + 2, y1 - 3, SCRG, 4.4 if i < 7 else 2.0, lit=0)
    if _ANIM['terminal'] == 0:                                   # el cursor que parpelleja
        cv.rect(x1 - 7, y1 - 8, x1 - 4, y1 - 3, SCRG, 5.0, lit=0)
    glow(cv, (x0 + x1) / 2, (y0 + y1) / 2, 35, (90, 220, 140), 0.22)


def terminal(cv):
    """El terminal de satèl·lit: pantalla verda, amb el text i la barra de senyal; el SAI a sota."""
    x0, y0, x1, y1 = 336, 101, 400, 139
    box(cv, x0, y0, x1, y1, CAB, 2.2, grad=0.6)
    cv.hline(x0 + 1, x1 - 1, y0 + 1, CAB, 3.8)
    screen(cv)
    cv.disc(x1 - 3, y1 - 3, 1, 1, CAB, 4.2)
    box(cv, 363, y1 + 1, 373, CON_TOP - 7, CAB, 1.8)             # el peu
    cv.poly([(339, CON_TOP - 7), (397, CON_TOP - 7), (400, CON_TOP - 1), (336, CON_TOP - 1)], CAB, 2.8)
    for row in (CON_TOP - 5, CON_TOP - 3):                       # el teclat
        for x in range(340, 397, 3):
            cv.put(x + (1 if row == CON_TOP - 3 else 0), row, CAB, 4.4)
    # el SAI, al frontal, amb el pilot verd i la marca de bateria
    box(cv, 336, 149, 395, 168, CAB, 2.0)
    for i in range(5):
        cv.rect(341 + i * 7, 155, 345 + i * 7, 161, SCRG, 3.4 if i < 4 else 1.4, lit=0)
    cv.rect(377, 154, 390, 161, WHITEP, 3.0)
    text(cv, 'SAI', 378, 155, DARK, 0.6)
    cv.flat(382, 165, GREENL)
    cv.flat(383, 165, GREENL)
    glow(cv, 382, 165, 5, GREENL, 0.5)
    # el cable de l'antena, que baixa del sostre
    vpipe(cv, 407, 26, 123, 1, CAB, 2.4)
    for y in (40, 80, 110):
        box(cv, 404, y, 410, y + 2, CAB, 3.2)
    cv.line(407, 123, 400, 128, CAB, 2.4)


def printer(cv):
    """La impressora: capsa beix amb la safata de paper i un full a mig sortir, amb la ruta impresa."""
    x0, y0, x1, y1 = 411, 120, 461, CON_TOP - 5
    box(cv, x0, y0, x1, y1, WHITEP, 2.8, grad=0.8)
    cv.hline(x0 + 1, x1 - 1, y0 + 1, WHITEP, 3.8)
    cv.rect(x0 + 5, y0 + 5, x1 - 5, y0 + 8, DARK, 1.0)          # la boca
    cv.poly([(x0 + 8, y0 + 7), (x1 - 8, y0 + 7), (x1 - 12, y0 - 8), (x0 + 12, y0 - 8)], WHITEP, 4.2)
    for y in range(y0 - 6, y0 + 5, 2):
        cv.hline(x0 + 15, x1 - 18 - (y % 4), y, WHITEP, 3.0)
    for x in range(x0 + 14, x1 - 14, 2):                         # el marge perforat
        cv.put(x, y0 - 7, WHITEP, 2.6)
    cv.flat(x1 - 8, y1 - 5, GREENL)
    cv.rect(x0 + 5, y1 - 7, x0 + 19, y1 - 4, CAB, 2.0)
    for i, bx in enumerate((x0 + 23, x0 + 28)):
        cv.rect(bx, y1 - 6, bx + 3, y1 - 4, CAB, 3.0)


# ─── A l'esquerra: l'escala avall i la porta de la ràdio ─────────────────────

def stairs_down(cv):
    """La boca de l'escala que baixa al passadís: sense porta, amb passamans i la llum càlida de baix."""
    x0, y0, x1, y1 = 11, 88, 69, FLOOR_Y
    for y in range(y0, y1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, DARK, 1.0 + (y - y0) * 0.008, lit=0.2)
    for i in range(7):                                  # els graons, cada cop més avall i amb llum càlida
        sy = 144 + i * 9
        cv.rect(x0 + 3, sy, x1 - 3, sy + 1, BRI, 3.2 + i * 0.25, lit=0.5)
        cv.rect(x0 + 3, sy + 2, x1 - 3, sy + 8, BRI, 1.4 + i * 0.2, lit=0.3)
        cv.hline(x0 + 3, x1 - 3, sy, YELL, 2.4, lit=0.2)          # cantell antilliscant
        for x in range(x0 + 4, x1 - 3, 4):
            cv.put(x, sy + 1, YELL, 1.6, lit=0.2)
    for y in range(133, y1):
        k = (y - 133) / (y1 - 133) * 0.5
        cv.tint(x0 + 1, y, x1 - 1, y, WARM, k * 0.5)
    for t in range(4):                                  # el marc
        cv.vline(x0 - t, y0 - t, y1, BRI, 4.4 - t * 0.8)
        cv.vline(x1 + t, y0 - t, y1, BRI, 3.8 - t * 0.8)
        cv.hline(x0 - t, x1 + t, y0 - t, BRI, 4.6 - t * 0.8)
    for hx in (x0 + 5, x1 - 5):                         # els passamans, de tub
        cv.line(hx, 133, hx, 197, CAB, 3.4)
        cv.line(hx + 1, 133, hx + 1, 197, CAB, 1.8)
        cv.line(hx, 133, hx + (8 if hx < 40 else -8), 123, CAB, 3.6)
        for by in (150, 180):
            box(cv, hx - 1, by, hx + 2, by + 2, CAB, 3.0)
    box(cv, 29, 71, 51, 81, WHITEP, 3.6)                # el rètol: fletxa avall
    for i in range(4):
        cv.hline(40 - i, 40 + i, 79 - i, DARK, 0.5)
    cv.vline(40, 73, 76, DARK, 0.5)
    glow(cv, 40, 187, 29, WARM, 0.25)


def ws_door(cv, x0, y0, x1, y1, ramp, lvl=3.0):
    """Fulla de porta estanca tancada: cantons rodons, nervis, palanques i volant."""
    rrect(cv, x0, y0, x1, y1, 11, ramp, lambda x, y: lvl - (y - y0) * 0.005 - (x - x0) * 0.006)
    for yy in (y0 + 4, y1 - 4):
        cv.hline(x0 + 8, x1 - 8, yy, ramp, lvl + 1.0)
    cv.hline(x0 + 4, x1 - 4, (y0 + y1) // 2, ramp, lvl + 0.8)
    cv.hline(x0 + 4, x1 - 4, (y0 + y1) // 2 + 1, ramp, lvl - 1.0)
    for dy in (y0 + 19, (y0 + y1) // 2 + 14, y1 - 19):           # palanques («dogs»)
        box(cv, x1 - 5, dy, x1 + 3, dy + 3, CAB, 3.6)
        box(cv, x0 - 3, dy, x0 + 5, dy + 3, CAB, 3.6)
        cv.put(x1 - 3, dy + 1, CAB, 1.4)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2 - 13
    cv.ring(cx, cy, 8, CAB, 3.6, step=4)
    cv.ring(cx, cy, 7, CAB, 2.2, step=4)
    cv.disc(cx, cy, 2, 2, CAB, 4.0)
    cv.line(cx - 7, cy, cx + 7, cy, CAB, 3.0)
    cv.line(cx, cy - 7, cx, cy + 7, CAB, 2.6)


def radio_door(cv):
    x0, y0, x1, y1 = 88, 88, 141, FLOOR_Y
    door_frame(cv, x0, y0, x1, y1, BRI)
    ws_door(cv, x0 + 1, y0 + 1, x1 - 1, y1 - 3, BRI, 3.2)
    cv.rect(x0 + 1, y1 - 3, x1 - 1, y1, BRI, 2.0)
    box(cv, 96, 71, 133, 81, WHITEP, 3.8)               # plaqueta «RÀDIO»
    cv.hline(97, 132, 80, WHITEP, 2.6)
    text(cv, 'RÀDIO', 105, 74, BRI, 1.0)
    cv.hline(x0 + 5, x1 - 5, y1 - 1, [(60, 50, 30), (140, 120, 80)], 1.2, lit=0)   # un fil de llum per sota


def barometer(cv):
    """El baròmetre i el rellotge de llautó, sobre la porta de la ràdio."""
    for cx, kind in ((101, 'b'), (131, 'r')):
        cy = 46
        cv.disc(cx, cy, 12, 12, BRASS, lambda nx, ny: 3.6 - nx - ny * 1.2)
        cv.disc(cx, cy, 9.5, 9.5, WHITEP, lambda nx, ny: 3.8 - ny * 0.6)
        if kind == 'b':
            for a in range(200, 341, 14):
                cv.put(cx + round(math.cos(math.radians(a)) * 7), cy + round(math.sin(math.radians(a)) * 7), DARK, 0.4)
            cv.line(cx, cy, cx + 4, cy - 5, DARK, 0.2)
            cv.line(cx, cy, cx - 3, cy - 5, BRASS, 3.0)
            text(cv, 'MB', cx - 3, cy + 3, DARK, 1.6)
        else:
            for a in range(0, 360, 30):
                cv.put(cx + round(math.cos(math.radians(a)) * 7.5), cy + round(math.sin(math.radians(a)) * 7.5),
                       DARK, 0.4 if a % 90 == 0 else 1.6)
            cv.line(cx, cy, cx, cy - 6, DARK, 0.2)
            cv.line(cx, cy, cx + 4, cy + 1, DARK, 0.2)
        cv.ring(cx, cy, 12, BRASS, 1.8, step=5)
        for a in (45, 135, 225, 315):
            cv.put(cx + round(math.cos(math.radians(a)) * 11), cy + round(math.sin(math.radians(a)) * 11), BRASS, 5.0)
    box(cv, 109, 61, 123, 65, BRASS, 3.0)


# ─── A la dreta: muntacàrregues, tub de veu i la porta del pal ──────────────

def dumbwaiter(cv):
    x0, y0, x1, y1 = 496, 80, 552, 147
    box(cv, x0, y0, x1, y1, CAB, 3.0, grad=0.6)
    box(cv, x0 + 5, y0 + 19, x1 - 5, y1 - 5, DARK, 1.0)          # l'obertura
    for y in range(y0 + 21, y1 - 6):
        cv.hline(x0 + 6, x1 - 6, y, DARK, 1.4 + (y - y0 - 21) * 0.025, lit=0.3)
    cv.vline(x0 + 6, y0 + 21, y1 - 6, CAB, 1.8)
    for y in range(y0 + 24, y1 - 8, 8):                           # les guies del pou, al fons
        cv.put(x1 - 8, y, CAB, 2.0, lit=0.3)
    cv.hline(x0 + 5, x1 - 5, y1 - 8, CAB, 3.6)                    # el replà de la safata
    box(cv, x0 + 5, y0 + 5, x1 - 5, y0 + 16, CAB, 3.6)            # la porteta, pujada
    for y in (y0 + 8, y0 + 12):
        cv.hline(x0 + 7, x1 - 7, y, CAB, 2.4)
    box(cv, (x0 + x1) // 2 - 5, y0 + 13, (x0 + x1) // 2 + 5, y0 + 16, BRASS, 3.4)
    box(cv, x0 + 14, y0 - 11, x1 - 14, y0 - 3, WHITEP, 3.6)       # rètol
    text(cv, 'CUINA', x0 + 18, y0 - 9, BRI, 1.0)
    box(cv, x1 + 3, 99, x1 + 9, 119, CAB, 2.6)                    # botons i timbre
    cv.disc(x1 + 6, 104, 2, 2, REDP, 4.4, lit=0.5)
    cv.disc(x1 + 6, 112, 2, 2, SCRG, 3.6, lit=0.5)
    cv.put(x1 + 6, 117, CAB, 4.4)


def voice_tube(cv):
    """La boca del tub de veu: el tub de llautó que baixa del sostre i la campana amb tapa."""
    cx = 568
    vpipe(cv, cx, 26, 107, 3, BRASS, 2.6)
    for y in (43, 80):
        box(cv, cx - 4, y, cx + 4, y + 3, CAB, 3.2)
    cv.disc(cx, 112, 5, 5, BRASS, lambda nx, ny: 3.2 - nx * 1.2 - ny)
    cv.disc(cx, 117, 8, 7, BRASS, lambda nx, ny: 3.5 - nx * 1.3 - ny * 1.2)
    cv.disc(cx, 117, 5.5, 4.5, BRASS, lambda nx, ny: 1.2 + nx * 0.6 + ny * 0.8)
    cv.disc(cx, 117, 3, 2, DARK, 0.6)
    for i, y in enumerate(range(125, 133)):                       # la cadeneta de la tapa
        cv.put(cx + 4 + (i % 2), y, BRASS, 3.0 + (i % 2))
    cv.disc(cx + 5, 135, 3.5, 2, BRASS, lambda nx, ny: 3.8 - ny)
    box(cv, cx - 9, 141, cx + 9, 145, BRASS, 2.8)
    box(cv, cx - 10, 150, cx + 10, 157, WHITEP, 3.4)              # «MÀQ.»
    text(cv, 'MÀQ', cx - 6, 152, BRI, 1.0)


MAST_DOOR = (592, 80, 637, FLOOR_Y)


def mast_door(cv):
    """La porta de l'escala exterior del pal, oberta: fora, la nit, la barana i els esglaons del pal."""
    x0, y0, x1, y1 = MAST_DOOR
    outside(cv, x0, y0, x1, y1)
    for y in range(168, y1):                             # l'ala del pont: coberta, barana blanca i franja vermella
        cv.hline(x0, x1, y, DARK, 1.6 + (y - 168) * 0.025, lit=0)
    cv.hline(x0, x1, 149, WHITEP, 2.0, lit=0)
    cv.hline(x0, x1, 160, WHITEP, 1.6, lit=0)
    cv.rect(x0, 165, x1, 169, REDP, 2.2, lit=0)
    for x in range(x0 + 3, x1, 16):
        cv.vline(x, 149, 168, WHITEP, 1.4, lit=0)
    for sx in (611, 627):                                # l'escala del pal: muntants i esglaons
        cv.vline(sx, y0, 187, CAB, 2.6, lit=0)
        cv.vline(sx + 1, y0, 187, CAB, 1.6, lit=0)
    for y in range(y0 + 5, 187, 8):
        cv.hline(611, 627, y, CAB, 2.2, lit=0)
    glow(cv, 621, 93, 16, (255, 200, 110), 0.4)          # una mica de llum groga de coberta
    cv.disc(621, 88, 2.5, 2.5, YELL, 5, lit=0)
    door_frame(cv, x0, y0, x1 + 5, y1, BRI)
    cv.rect(x0 + 1, y1 - 7, x1, y1 - 1, BRI, 2.6)                 # el llindar alt
    cv.hline(x0 + 1, x1, y1 - 7, BRI, 4.0)
    cv.poly([(576, y0 + 5), (587, y0 - 1), (587, y1 - 3), (576, y1 - 5)], BRI, lambda x, y: 3.2 - (x - 576) * 0.06)
    for dy in (y0 + 19, y1 - 19):
        box(cv, 578, dy, 584, dy + 4, CAB, 3.6)
    box(cv, 596, 66, 630, 75, WHITEP, 3.6)                        # rètol
    text(cv, 'PAL', 607, 68, BRI, 1.0)


# ─── El terra ────────────────────────────────────────────────────────────────

def floor(cv):
    """Linòleum gris blavós de rajoles, gastat pel camí del timó."""
    vp = (320, 53)
    for y in range(FLOOR_Y, H):
        d = y - vp[1]
        for x in range(W):
            u = vp[0] + (x - vp[0]) * 200 / d
            u2 = vp[0] + (x + 1 - vp[0]) * 200 / d
            v = 4267 / d
            lvl = 3.6 + (hr(int(u // 40), int(v // 3.33)) - 0.5) * 0.5
            if int(u // 40) != int(u2 // 40) or int(v // 3.33) != int(4267 / (d + 1) // 3.33):
                lvl = 2.4
            if abs(x - 280) < 53 - (y - FLOOR_Y) * 0.2 and hr(x // 2, y) > 0.5:
                lvl += 0.4                                       # gastat davant del timó
            cv.put(x, y, FLOORB, lvl)
    cv.hline(0, W - 1, FLOOR_Y, FLOORB, 1.0)
    for y in range(FLOOR_Y + 8, FLOOR_Y + 21):                   # estora de goma davant la consola
        for x in range(200 - (y - FLOOR_Y), 440 + (y - FLOOR_Y)):
            cv.put(x, y, FLOORB, 1.6 + (0.6 if (x + y) % 4 == 0 else 0))


def chair(cv):
    """La cadira alta del pont, girada, a la dreta del timó (fixada a terra)."""
    cx = 461
    box(cv, cx - 3, 182, cx + 3, FLOOR_Y + 16, CAB, 2.6)
    cv.disc(cx, FLOOR_Y + 16, 13, 3.5, CAB, 1.8)
    box(cv, cx - 16, 171, cx + 16, 181, ENG, 3.4, grad=0.6)       # seient
    cv.hline(cx - 14, cx + 14, 176, ENG, 2.4)                     # el cosit
    box(cv, cx + 11, 133, cx + 17, 173, ENG, 3.2)                 # respatller
    box(cv, cx - 16, 165, cx - 11, 171, CAB, 3.0)                 # braç
    box(cv, cx - 10, 195, cx + 10, 197, CAB, 2.4)                 # el reposapeus


# ─── Muntatge ────────────────────────────────────────────────────────────────

def bg(cv):
    wall(cv)
    ceiling(cv)
    windows(cv)
    repeaters(cv)
    console(cv)
    radar(cv)
    terminal(cv)
    printer(cv)
    stairs_down(cv)
    radio_door(cv)
    barometer(cv)
    dumbwaiter(cv)
    voice_tube(cv)
    mast_door(cv)
    floor(cv)
    wheel(cv)
    chair(cv)
    if not _MODE['dia']:
        glow(cv, LAMP[0], 21, 32, (255, 120, 90), 0.35)


# ─── Props ───────────────────────────────────────────────────────────────────

def safata(cv):
    """Una safata d'acer al replà del muntacàrregues (el que hi ha a sobre, a `objecte`)."""
    cv.poly([(504, 137), (544, 137), (547, 141), (501, 141)], CAB, 4.0)
    cv.hline(501, 547, 141, CAB, 2.0)


def porta_tancada(cv):
    """La porteta baixada (el muntacàrregues en marxa): tapa l'obertura, amb la nansa de llautó a baix."""
    x0, y0, x1, y1 = 496, 80, 552, 147
    box(cv, x0 + 5, y0 + 19, x1 - 5, y1 - 5, CAB, 3.6)
    for y in range(y0 + 23, y1 - 9, 4):
        cv.hline(x0 + 7, x1 - 7, y, CAB, 2.4)
    box(cv, (x0 + x1) // 2 - 5, y1 - 9, (x0 + x1) // 2 + 5, y1 - 6, BRASS, 3.4)
    box(cv, x0 + 5, y0 + 5, x1 - 5, y0 + 16, DARK, 1.2)           # on era la porteta, el pou


def objecte(cv, item):
    """L'objecte que ha arribat, damunt la safata."""
    from hd640.safata import posa
    posa(cv, item, 524, 139, 34)


def guardacostes(cv):
    """Els llums del guardacostes de Valmark, a l'horitzó del tercer vidre: la silueta, el llum blanc de pal,
    el vermell de babord i el blau del pont."""
    cx, hy = 368, HORIZON
    cv.poly([(cx - 19, hy), (cx + 16, hy), (cx + 13, hy + 3), (cx - 16, hy + 3)], NSKY, 0.4, lit=0)
    cv.rect(cx - 5, hy - 5, cx + 5, hy - 1, NSKY, 0.6, lit=0)
    cv.rect(cx - 3, hy - 7, cx + 3, hy - 5, NSKY, 0.6, lit=0)
    cv.vline(cx, hy - 11, hy - 5, NSKY, 0.6, lit=0)
    for x, y, col in ((cx, hy - 12, (255, 250, 230)), (cx - 8, hy - 2, (255, 60, 50)),
                      (cx + 4, hy - 5, (230, 240, 255)), (cx + 11, hy - 1, (255, 230, 200)),
                      (cx - 2, hy - 4, (255, 230, 200))):
        cv.flat(x, y, col)
    for i in range(1, 12, 2):                            # els reflexos a l'aigua
        cv.flat(cx - 8, hy + 3 + i, (150, 40, 40))
        cv.flat(cx, hy + 4 + i, (140, 140, 130))
    cv.flat(cx - 3, hy - 8, (90, 150, 255))
    cv.flat(cx - 2, hy - 8, (90, 150, 255))


def fosc(cv):
    """El generador parat: tot fosc, només els llums d'emergència vermells i les pantalles amb el SAI."""
    P = cv.P
    lamps = ((53, 35), (531, 35))
    for X, Y, x, y in cv.pixels():                               # (X, Y: píxel real; x, y: de sala)
        a = 165
        r = 0
        for lx, ly in lamps:
            d = math.hypot(x - lx, (y - ly) * 1.1)
            if d < 147:
                f = (1 - d / 147) ** 1.6
                a -= int(70 * f)
                r += int(150 * f)
        d = math.hypot(x - 368, y - 123)                         # el terminal (SAI) encara fa claror
        if d < 61:
            a -= int(80 * (1 - d / 61) ** 1.5)
        a = max(0, min(255, a))
        if a > 0:
            P[X, Y] = (min(255, 4 + r // 3), 2, 8, a)
    for lx, ly in lamps:                                         # els llums d'emergència
        for X, Y, x, y in cv.pixels(lx - 9, ly - 4, lx + 9, ly + 3):
            P[X, Y] = (40, 40, 46, 255) if Y // cv.S > ly - 4 else (62, 62, 70, 255)
        for X, Y, x, y in cv.pixels(lx - 7, ly - 1, lx + 7, ly + 3):
            if ((x - lx) / 7.5) ** 2 + ((y - ly - 1) / 3) ** 2 <= 1:
                P[X, Y] = (255, 110 if Y // cv.S == ly else 40, 30, 255)


def dia(cv):
    """Decorat `dia` (sota, Escenes 2 i 3): el pont sencer de dia, amb el cel i el mar grisos pels vidres i la
    claror freda que entra. Deixa forats a les pantalles del radar i del terminal (s'hi veuen les animacions)."""
    _MODE['dia'] = True
    try:
        day = Canvas(light=LIGHT_DIA)
        bg(day)
    finally:
        _MODE['dia'] = False
    day.tint(0, 0, W - 1, H - 1, (150, 160, 172), 0.1)
    src, o = day.img.load(), cv.P
    x0, y0, x1, y1 = SCREEN
    for X, Y, x, y in cv.pixels():
        if math.hypot(x - RADAR[0], y - RADAR[1]) <= 16.5 or (x0 <= X // cv.S <= x1 and y0 <= Y // cv.S <= y1):
            continue
        o[X, Y] = src[X, Y]


PROPS = {'dia': dia, 'safata': safata, 'guardacostes': guardacostes, 'fosc': fosc}


# ─── Animacions ──────────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv.img


def _frames(key, n):
    """Fotogrames d'una animació: la sala sencera a cada fotograma, menys el fons quiet (només el que canvia)."""
    out = []
    for f in range(n):
        _ANIM[key] = f
        try:
            cv = Canvas(light=LIGHT)
            bg(cv)
        finally:
            _ANIM[key] = 0
        out.append(_diff(cv.img, _base()))
    return out


ANIMS = {'radar': {'frames': lambda: _frames('radar', RADAR_N), 'frameDuration': 220},
         'terminal': {'frames': lambda: _frames('terminal', 2), 'frameDuration': 530},
         'mar': {'frames': lambda: _frames('mar', MAR_N), 'frameDuration': 260}}


# ─── Geometria (×4/3 de la de 480) ───────────────────────────────────────────

def _t(x0, y0, x1, y1, wx=None, wy=240):
    return {'rect': (x0, y0, x1, y1), 'walk': (wx if wx is not None else (x0 + x1) // 2, wy)}
