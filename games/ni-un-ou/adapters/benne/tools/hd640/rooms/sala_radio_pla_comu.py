"""
**El dibuix pla de sempre** (font de les textures de la sala en 3D, sala_radio.py).

Prova de resolució: la sala de ràdio a 640×360 (×4/3 de hd/rooms/sala_radio.py, amb més detall).

Mateixa forma que la de 480: LIGHT, LIGHT_DIA, bg, PROPS (`dia`, `panell_obert`, `cable`), ANIMS (`mar`, de nit, i
`dia_mar`, de dia: el mar pel vidre del pont que es veu per la porta i els pilots de la consola) i GEOMETRIA.
La ràdio no es mou: és morta fins que l'Iri l'arregla.
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from hd640 import W, H
from hd.pix import Canvas, Light, hr, mix
from hd.rooms.arenga import CAB, ENG, DARK, WHITEP, REDP, YELL, BRASS, WARM, box, rrect, bolt, glow
from hd.rooms.comu import _diff, text
from hd.rooms.exterior import day_sky, day_sea
from hd.rooms.pont import BRI, AMB, SCRG, WOOD, FLOORB, NSKY, NSEA

from hd.pix import Canvas  # noqa: E402,F811  (a 1×: és la font de les textures de la sala en 3D)
Canvas1x = Canvas

FLOOR_Y = 203                  # 152 × 4/3
LAMP = (302, 40)
DESK_TOP = 144                 # 108 × 4/3

CABLE = [(6, 6, 8), (16, 16, 20), (30, 30, 36), (48, 48, 56), (72, 72, 80)]
PAPERY = [(60, 56, 46), (120, 114, 96), (176, 168, 140), (214, 206, 176), (236, 230, 204)]
CORK = [(40, 24, 14), (70, 44, 24), (104, 70, 40), (138, 98, 58), (170, 128, 80)]

LIGHT = Light(ambient=0.5, vignette=(80, 34), floor_fade=None)
LIGHT.point(302, 44, r=226, k=2.4, squash=1.1, down=True, power=1.5)
LIGHT.point(38, 133, r=80, k=0.5, power=1.8)
LIGHT.point(296, 100, r=66, k=0.5, power=1.8)

# `dia` (Escenes 2 i 3): claror grisa del matí per l'ull de bou i la porta del pont; el llum de taula, encès
LIGHT_DIA = Light(ambient=1.5, vignette=(80, 34), floor_fade=None)
LIGHT_DIA.point(302, 44, r=200, k=1.4, squash=1.1, down=True, power=1.5)
LIGHT_DIA.point(38, 133, r=120, k=1.0, power=1.6)                       # la claror del pont, de dia
LIGHT_DIA.point(588, 66, r=146, k=1.0, power=1.6)                       # l'ull de bou

_MODE = {'dia': False}
ANIM_N = 12
_ANIM = {'f': 0}                 # fotograma actual de l'animació (0 = el fons quiet)
SEA_FADE, SEA_STEP = 4, 0.32
MESH = [(40, 40, 44), (90, 92, 96), (150, 152, 156), (210, 212, 214)]


# ─── Exterior de nit (per la porta i l'ull de bou) ────────────────────────────

def _cloud(x, y):
    v = math.sin(x * 0.024 + math.sin(y * 0.16) * 2.2 + y * 0.09) * 0.5 + 0.5
    v *= math.sin(x * 0.010 - y * 0.04 + 1.3) * 0.5 + 0.5
    return v + (hr(x // 8, y // 4) - 0.5) * 0.25


def _night(cv, x0, y0, x1, y1, horizon, moon, t=0.0):
    mx, my = moon
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if y < horizon:
                d = math.hypot(x - mx, (y - my) * 1.4)
                lvl = 2.6 + (y - y0) * 0.02 + max(0, 1 - d / 60) * 2.8
                c = _cloud(x, y)
                if c > 0.55:
                    lvl += (c - 0.55) * 4.0 * (0.6 + max(0, 1 - d / 80) * 1.6)
                if d < 5 and c < 0.75:
                    lvl = 7.4 - d * 0.3
                if horizon - y < 5:
                    lvl += 0.6
                cv.put(x, y, NSKY, lvl, lit=0)
            else:
                dd = y - horizon
                lvl = 2.8 - dd * 0.03
                ph = math.sin(x * (0.16 - dd * 0.002) + dd * 0.8 + math.sin(x * 0.05 + dd * 0.3) * 1.6 + t)
                if ph > 0.7:
                    lvl += 0.9
                elif ph < -0.6:
                    lvl -= 0.5
                g = math.exp(-((x - mx) / (8 + dd * 1.5)) ** 2)
                if g > 0.15 and ph > 0.4 and hr(x // 2, y, int(t * 3) % 5) < g * 0.9:
                    lvl += 2.6 * g
                cv.put(x, y, NSEA, lvl, lit=0)


@functools.lru_cache(maxsize=None)
def _day_view(x0, y0, x1, y1, horizon, f):
    """El cel i el mar de dia d'una obertura, al fotograma f. Els darrers SEA_FADE fotogrames es fonen (a quadres)
    amb el principi perquè el bucle no salti."""
    def view(phase):
        cv = Canvas()
        day_sky(cv, y0, horizon - 1, seed=13, x0=x0, x1=x1)
        day_sea(cv, horizon, y1, seed=6, x0=x0, x1=x1, phase=phase)
        return cv.img
    if f == 0:
        return view(0.0)
    a, b = view(f * SEA_STEP), view((f - ANIM_N) * SEA_STEP)
    w = max(0, f - (ANIM_N - SEA_FADE)) / SEA_FADE
    o, bp = a.load(), b.load()
    k = a.width // W                                                 # píxels reals per píxel de sala (art a 2×)
    for Y in range(horizon * k, (y1 + 1) * k):
        for X in range(x0 * k, (x1 + 1) * k):
            if hr(X // k, Y // k, 90) < w:
                o[X, Y] = bp[X, Y]
    return a


def outside(cv, x0, y0, x1, y1, horizon, moon, f=0):
    """El que es veu per una obertura: de nit, cel, núvols i mar amb el camí de la lluna; de dia, cel gris de
    febrer i mar gris. `f`: fotograma de l'animació (0 = quiet)."""
    if _MODE['dia']:
        src, dst = _day_view(x0, y0, x1, y1, horizon, f).load(), cv.P
        for X, Y, x, y in cv.pixels(x0, y0, x1, y1):
            dst[X, Y] = src[X, Y]
        return
    _night(cv, x0, y0, x1, y1, horizon, moon, t=f * 2 * math.pi / ANIM_N)


# ─── Paret, sostre i terra ────────────────────────────────────────────────────

def wall(cv):
    for y in range(0, FLOOR_Y):
        for x in range(W):
            lvl = 3.4 + (hr(x // 3, y // 5) - 0.5) * 0.3
            if y >= 182:
                lvl -= 0.8
            cv.put(x, y, BRI, lvl)
    for fx in range(-26, W, 74):
        cv.vline(fx, 26, FLOOR_Y - 1, BRI, 2.2)
        cv.vline(fx + 1, 26, FLOOR_Y - 1, BRI, 4.2)
        for y in range(40, 176, 16):
            bolt(cv, fx + 4, y, BRI, 3.8)
            bolt(cv, fx - 4, y + 8, BRI, 3.6)
    for fx in range(-26, W, 74):                                         # rovell a les costures de baix
        for y in range(158, 181):
            if hr(fx, y) > 0.82:
                cv.put(fx + 2, y, [(40, 22, 16), (80, 44, 26), (120, 70, 36)], 1.2)
    cv.hline(0, W - 1, 181, BRI, 4.4)
    cv.hline(0, W - 1, 182, BRI, 2.0)
    cv.hline(0, W - 1, FLOOR_Y - 1, BRI, 1.0)
    # el tub d'aigua que corre arran de terra
    for x in range(0, W):
        for y in range(189, 196):
            u = (y - 192.5) / 4
            cv.put(x, y, CAB, 2.8 + 1.4 * (0.35 - u) - 0.6 * u * u)
    for x in range(30, W, 96):
        box(cv, x, 186, x + 3, 198, CAB, 3.0)


def ceiling(cv):
    cv.rect(0, 0, W - 1, 23, DARK, 2.2)
    for bx in range(-26, W, 74):
        box(cv, bx - 3, 0, bx + 8, 25, BRI, 2.0, grad=0.8)
        cv.hline(bx - 2, bx + 7, 25, BRI, 1.0)
    cv.hline(0, W - 1, 24, BRI, 1.2)
    cv.hline(0, W - 1, 25, BRI, 3.0)
    box(cv, 0, 29, W - 1, 35, CAB, 2.4)
    cv.hline(0, W - 1, 30, CAB, 3.2)
    for x in range(6, W, 52):
        box(cv, x, 28, x + 3, 36, CAB, 3.4)
    for x in range(20, W, 140):
        for i in range(10):
            cv.put(x + i * 3, 36 + round(math.sin(i * 0.5) * 1.5 + i * 0.2), CABLE, 2.4)
    lx, ly = LAMP
    cv.vline(lx, 36, ly - 8, CAB, 2.0)
    cv.vline(lx + 1, 36, ly - 8, CAB, 1.2)
    box(cv, lx - 2, ly - 10, lx + 2, ly - 7, CAB, 3.0)
    green = [(10, 24, 18), (18, 44, 30), (30, 70, 46), (50, 100, 66), (80, 130, 90), (120, 160, 120)]
    cv.poly([(lx - 4, ly - 8), (lx + 4, ly - 8), (lx + 16, ly), (lx - 16, ly)], green,
            lambda x, y: 2.8 - (x - lx) * 0.07 - (y - ly + 8) * 0.06)
    cv.hline(lx - 16, lx + 16, ly, green, 1.2)
    cv.disc(lx, ly + 1, 9, 3, [(160, 120, 60), (250, 220, 150), (255, 246, 220)], 2.0, lit=0)


def floor(cv):
    vp = (320, 100)
    for y in range(FLOOR_Y, H):
        d = y - vp[1]
        for x in range(W):
            u = vp[0] + (x - vp[0]) * 200 / d
            u2 = vp[0] + (x + 1 - vp[0]) * 200 / d
            v = 4200 / d
            lvl = 3.6 + (hr(int(u // 40), int(v // 3)) - 0.5) * 0.5
            if int(u // 40) != int(u2 // 40) or int(v // 3) != int(4200 / (d + 1) // 3):
                lvl = 2.4
            if abs(x - 300) < 60 - (y - FLOOR_Y) * 0.2 and hr(x // 2, y) > 0.55:
                lvl += 0.4
            cv.put(x, y, FLOORB, lvl)
    cv.hline(0, W - 1, FLOOR_Y, FLOORB, 1.0)
    for y in range(FLOOR_Y + 8, FLOOR_Y + 21):                            # estora de goma davant la ràdio
        for x in range(196 - (y - FLOOR_Y), 404 + (y - FLOOR_Y)):
            cv.put(x, y, FLOORB, 1.6 + (0.6 if (x + y) % 4 == 0 else 0))


# ─── La porta del pont ────────────────────────────────────────────────────────

def door_frame(cv, x0, y0, x1, y1, ramp, r=12):
    for t in range(4):
        for y in range(y0 - t, y1 + 1):
            for x in range(x0 - t, x1 + t + 1):
                dx = max(x0 - t + r - x, 0, x - (x1 + t - r))
                dy = max(y0 - t + r - y, 0)
                inside = dx * dx + dy * dy <= r * r
                ddx = max(x0 - t + 1 + r - x, 0, x - (x1 + t - 1 - r))
                ddy = max(y0 - t + 1 + r - y, 0)
                inner = x0 - t + 1 <= x <= x1 + t - 1 and y >= y0 - t + 1 and ddx * ddx + ddy * ddy <= r * r
                if inside and not inner:
                    cv.put(x, y, ramp, 4.6 - t * 0.8)


_BLINK = next(x for x in range(20, 70, 5) if hr(x, 1) > 0.7)     # el pilot verd que parpelleja


def door(cv):
    x0, y0, x1, y1 = 16, 88, 70, FLOOR_Y
    for y in range(y0, y1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, BRI, 1.8 - (y - y0) * 0.003, lit=0.3)
    f = _ANIM['f']
    outside(cv, x0 + 8, y0 + 10, x1 - 6, y0 + 42, horizon=y0 + 30, moon=(x0 + 18, y0 + 20), f=f)
    cv.rect(x0 + 6, y0 + 8, x1 - 4, y0 + 9, BRI, 3.0, lit=0.3)
    cv.rect(x0 + 6, y0 + 43, x1 - 4, y0 + 46, BRI, 3.0, lit=0.3)
    cv.vline(x0 + 30, y0 + 10, y0 + 42, BRI, 3.0, lit=0.3)
    # la consola del pont, al fons, amb pilots i el radar
    box(cv, x0, 147, x1, 186, ENG, 1.6, edge=False)
    cv.hline(x0, x1, 147, ENG, 3.0)
    for x in range(x0 + 4, x1, 5):
        r = hr(x, 1)
        if x == x0 + 19:                                                # l'alarma de sentina, ambre, a poc a poc
            if (f // 3) % 2:
                cv.flat(x, 150, (240, 170, 60))
                cv.flat(x, 151, (150, 90, 30))
        elif r > 0.45 and not (r > 0.7 and x == _BLINK and f in (7, 8)):   # un pilot verd fa un pampallugueig
            cv.flat(x, 150, (90, 240, 140) if r > 0.7 else (240, 170, 60))
    for x in range(x0 + 6, x1 - 4, 10):
        cv.disc(x, 158, 2, 2, ENG, 3.0, lit=0.3)
    rrect(cv, x0 + 28, 136, x1 - 4, 166, 3, ENG, 1.4)
    cv.disc(x0 + 42, 151, 9, 9, SCRG, lambda nx, ny: 1.4 + max(0, 1 - math.hypot(nx, ny)) * 0.8, lit=0)
    cv.ring(x0 + 42, 151, 5, SCRG, 2.4, step=20)
    cv.line(x0 + 42, 151, x0 + 48, 145, SCRG, 4.6, lit=0)
    glow(cv, x0 + 42, 151, 16, (90, 220, 140), 0.25)
    cv.rect(x0 + 1, y1 - 7, x1 - 1, y1, BRI, 2.6)
    cv.hline(x0 + 1, x1 - 1, y1 - 7, BRI, 4.0)
    door_frame(cv, x0, y0, x1, y1, BRI)
    cv.poly([(2, y0 + 6), (12, y0 - 1), (12, y1 - 2), (2, y1 - 6)], BRI, lambda x, y: 3.0 - (x - 2) * 0.05)
    for y in range(y0 + 14, y1 - 10, 30):
        box(cv, 4, y, 9, y + 4, CAB, 3.6)
    cv.vline(12, y0, y1 - 2, BRI, 4.6)
    box(cv, 25, 72, 61, 82, WHITEP, 3.8)
    cv.hline(26, 60, 81, WHITEP, 2.6)
    text(cv, 'PONT', 32, 75, BRI, 1.0)


# ─── El suro amb avisos ──────────────────────────────────────────────────────

def notices(cv):
    x0, y0, x1, y1 = 96, 84, 166, 140
    box(cv, x0 - 2, y0 - 2, x1 + 2, y1 + 2, WOOD, 3.0)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, CORK, 2.4 + (hr(x, y) - 0.5) * 1.2)
    box(cv, x0 + 4, y0 + 4, x0 + 34, y0 + 42, PAPERY, 3.8, edge=False)   # taula de freqüències
    text(cv, 'VHF', x0 + 8, y0 + 7, REDP, 2.0)
    for i, y in enumerate(range(y0 + 15, y0 + 40, 4)):
        cv.hline(x0 + 7, x0 + 15, y, DARK, 1.6)
        cv.hline(x0 + 19, x0 + 31, y, DARK, 1.6 if i != 2 else 0.6)
    cv.hline(x0 + 6, x0 + 32, y0 + 22, REDP, 3.0)
    cv.disc(x0 + 19, y0 + 5, 1.5, 1.5, REDP, 3.6)
    cv.poly([(x0 + 40, y0 + 8), (x0 + 64, y0 + 5), (x0 + 66, y0 + 26), (x0 + 42, y0 + 29)], WHITEP, 4.2)   # foto
    cv.poly([(x0 + 43, y0 + 10), (x0 + 62, y0 + 8), (x0 + 63, y0 + 22), (x0 + 44, y0 + 24)],
            [(20, 40, 60), (40, 70, 96), (70, 110, 130), (130, 160, 170)], lambda x, y: 3.2 - (y - y0 - 8) * 0.12)
    cv.poly([(x0 + 44, y0 + 19), (x0 + 63, y0 + 17), (x0 + 63, y0 + 22), (x0 + 44, y0 + 24)], WOOD, 2.0)
    cv.disc(x0 + 54, y0 + 7, 1.5, 1.5, YELL, 4.0)
    box(cv, x0 + 44, y0 + 34, x0 + 60, y0 + 50, YELL, 4.2, edge=False)  # post-it
    for y in (y0 + 38, y0 + 42, y0 + 46):
        cv.hline(x0 + 47, x0 + 57, y, YELL, 1.6)
    cv.disc(x0 + 52, y0 + 35, 1.5, 1.5, SCRG, 3.6)
    box(cv, x0 + 8, y0 + 45, x0 + 36, y0 + 53, PAPERY, 3.4, edge=False)  # llista de guàrdies
    for y in (y0 + 48, y0 + 51):
        cv.hline(x0 + 10, x0 + 34, y, DARK, 2.0)


# ─── La taula i la ràdio ──────────────────────────────────────────────────────

def desk(cv):
    x0, x1 = 184, 416
    box(cv, x0, DESK_TOP, x1, DESK_TOP + 5, WOOD, 4.0)
    cv.hline(x0, x1, DESK_TOP, WOOD, 5.4)
    for x in range(x0 + 4, x1 - 4, 9):
        if hr(x, 7) > 0.4:
            cv.hline(x, x + 5, DESK_TOP + 3, WOOD, 3.2)
    box(cv, 336, DESK_TOP + 6, x1 - 2, FLOOR_Y + 3, CAB, 2.6, grad=0.6)
    for y in (156, 172, 188):
        box(cv, 342, y, x1 - 8, y + 12, CAB, 3.2)
        cv.hline(343, x1 - 9, y + 11, CAB, 2.0)
        box(cv, 366, y + 4, 388, y + 7, BRASS, 3.0)
        box(cv, 346, y + 3, 356, y + 7, WHITEP, 3.2, edge=False)
    box(cv, x0 + 2, DESK_TOP + 6, x0 + 10, FLOOR_Y + 3, CAB, 2.4)
    for y in range(DESK_TOP + 6, FLOOR_Y + 1):
        cv.darken(x0 + 11, y, 335, y, 0.5 + (y - DESK_TOP) * 0.01)
    box(cv, 240, 174, 286, 178, WOOD, 3.4)                               # tamboret
    cv.hline(240, 286, 174, WOOD, 4.6)
    for lx in (245, 281):
        cv.vline(lx, 179, FLOOR_Y + 5, CAB, 2.4)
        cv.vline(lx + 1, 179, FLOOR_Y + 5, CAB, 1.4)
    cv.hline(245, 281, 194, CAB, 2.0)
    for y in range(DESK_TOP - 9, DESK_TOP):                              # la tassa
        for x in range(190, 198):
            u = (x - 193.5) / 4
            cv.put(x, y, WHITEP, 3.8 + 1.2 * (-0.3 - u) - 0.6 * u * u)
    cv.ring(199, DESK_TOP - 5, 2.5, WHITEP, 3.0, step=30)
    cv.hline(191, 196, DESK_TOP - 9, WOOD, 1.4)


def radio(cv):
    x0, y0, x1, y1 = 202, 78, 400, DESK_TOP - 1
    box(cv, x0, y0, x1, y1, CAB, 3.2, grad=0.8)
    cv.hline(x0 + 1, x1 - 1, y0 + 1, CAB, 4.4)
    for x in range(x0 + 30, x1 - 30, 4):                                 # reixeta de ventilació
        cv.vline(x, y0 + 3, y0 + 5, DARK, 1.0)
    for hx in (x0 + 4, x1 - 9):
        box(cv, hx, y0 + 12, hx + 5, y1 - 12, BRASS, 2.6)
        cv.vline(hx + 1, y0 + 13, y1 - 13, BRASS, 4.2)
        cv.vline(hx + 4, y0 + 13, y1 - 13, BRASS, 1.8)
    for bx, by in ((x0 + 3, y0 + 4), (x1 - 5, y0 + 4), (x0 + 3, y1 - 5), (x1 - 5, y1 - 5)):
        bolt(cv, bx, by, CAB, 3.6)
    box(cv, 222, 84, 258, 90, BRASS, 3.0)                                # placa del fabricant
    text(cv, 'SAILOR', 224, 85, BRASS, 0.8)
    rrect(cv, 218, 94, 262, 134, 5, CAB, 1.8)                            # altaveu
    for y in range(97, 132, 3):
        for x in range(221, 260, 3):
            dx, dy = x - 240, (y - 114) * 1.1
            if dx * dx + dy * dy < 400:
                cv.put(x, y, DARK, 0.4)
    box(cv, 272, 84, 350, 98, DARK, 1.0)                                 # visor de freqüència
    cv.rect(274, 86, 348, 96, AMB, 1.0, lit=0)
    text(cv, '2182.0', 280, 89, AMB, 4.4, lit=0)
    text(cv, 'KHZ', 330, 89, AMB, 3.2, lit=0)
    glow(cv, 311, 91, 28, (255, 170, 60), 0.3)
    box(cv, 358, 84, 390, 100, DARK, 1.0)                                # vúmetre
    cv.rect(360, 86, 388, 98, [(120, 100, 60), (200, 180, 120), (240, 226, 180)], 1.6, lit=0.5)
    for a in range(210, 331, 15):
        cv.put(374 + round(math.cos(math.radians(a)) * 10), 99 + round(math.sin(math.radians(a)) * 10), DARK, 0.4)
    cv.line(374, 98, 367, 89, DARK, 0.2)
    cv.rect(383, 88, 386, 89, REDP, 3.4)
    for cx, lab in ((290, 'TUNE'), (332, 'GAIN')):                       # dials
        cv.disc(cx, 116, 10, 10, DARK, 1.2)
        cv.disc(cx, 116, 8, 8, CAB, lambda nx, ny: 4.2 - nx * 1.2 - ny * 1.4)
        cv.disc(cx, 116, 3.5, 3.5, CAB, lambda nx, ny: 2.4 + nx + ny)
        cv.line(cx, 116, cx - 4, 110, WHITEP, 3.6)
        for a in range(0, 360, 24):
            cv.put(cx + round(math.cos(math.radians(a)) * 12), 116 + round(math.sin(math.radians(a)) * 12), WHITEP, 2.6)
        text(cv, lab, cx - 7, 132, WHITEP, 2.4)
    for i, x in enumerate(range(356, 392, 9)):
        box(cv, x, 108, x + 6, 113, CAB, 4.0 if i != 1 else 2.4)
        cv.disc(x + 3, 122, 2.5, 2.5, CAB, lambda nx, ny: 3.8 - nx - ny)
    cv.disc(272, 112, 2.5, 2.5, REDP, 1.4)                               # pilot (apagat)
    cv.disc(272, 126, 4, 4, CAB, lambda nx, ny: 3.6 - nx - ny)           # selector de banda
    cv.line(272, 126, 275, 123, DARK, 0.6)
    # el micròfon de mà, penjat, amb el cordó en espiral
    box(cv, 404, 88, 409, 93, CAB, 3.4)
    rrect(cv, 404, 93, 418, 116, 4, DARK, lambda x, y: 2.4 - (x - 404) * 0.08)
    for y in range(98, 106, 2):
        cv.hline(407, 414, y, CABLE, 3.4)
    box(cv, 418, 101, 421, 106, CAB, 3.6)
    for i in range(26):
        cv.put(410 + round(math.sin(i * 1.3) * 3), 117 + i, DARK, 2.4)
        cv.put(410 + round(math.sin(i * 1.3) * 3) + 1, 117 + i, DARK, 1.2)
    cv.ring(232, DESK_TOP - 6, 8, DARK, 2.4, step=8)                     # auriculars
    cv.disc(224, DESK_TOP - 3, 4, 3, DARK, 1.6)
    cv.disc(240, DESK_TOP - 3, 4, 3, DARK, 1.6)
    cv.poly([(300, DESK_TOP - 3), (350, DESK_TOP - 3), (353, DESK_TOP), (297, DESK_TOP)], WHITEP, 4.4)   # llibre
    cv.vline(325, DESK_TOP - 3, DESK_TOP, WHITEP, 2.4)
    for x in range(301, 350, 2):
        if hr(x, 9) > 0.3 and abs(x - 325) > 1:
            cv.put(x, DESK_TOP - 2, DARK, 1.8)
    cv.line(358, DESK_TOP - 1, 372, DESK_TOP - 4, YELL, 4.0)
    cv.put(372, DESK_TOP - 4, WOOD, 2.0)


# ─── Panell de l'antena ───────────────────────────────────────────────────────

PANEL = (440, 80, 520, 160)


def panel(cv):
    x0, y0, x1, y1 = PANEL
    box(cv, 472, 36, 488, y0, CAB, 2.6, grad=0.4)
    cv.vline(474, 37, y0 - 1, CAB, 3.6)
    for y in range(44, y0, 12):
        box(cv, 470, y, 490, y + 2, CAB, 3.2)
    box(cv, 421, 138, x0, 145, CAB, 2.4)
    cv.hline(421, x0, 139, CAB, 3.4)
    box(cv, x0 - 3, y0 - 3, x1 + 3, y1 + 3, BRI, 2.2)
    box(cv, x0, y0, x1, y1, BRI, 4.0, grad=0.8)
    cv.hline(x0 + 2, x1 - 2, y0 + 2, BRI, 5.0)
    for bx, by in ((x0 + 5, y0 + 5), (x1 - 6, y0 + 5), (x0 + 5, y1 - 6), (x1 - 6, y1 - 6)):
        cv.disc(bx, by, 2.2, 2.2, CAB, 4.4)
        cv.line(bx - 1, by + 1, bx + 1, by - 1, CAB, 1.4)
        for dx, dy in ((3, -1), (-3, 1), (1, 3), (-2, -3)):
            cv.put(bx + dx, by + dy, WHITEP, 2.6)
    cv.poly([(480, 92), (491, 111), (469, 111)], YELL, 4.2)
    cv.poly([(482, 96), (477, 104), (481, 104), (478, 109), (484, 101), (480, 101)], DARK, 0.4)
    box(cv, 452, 118, 508, 127, WHITEP, 3.8)
    text(cv, 'ANTENA', 463, 120, BRI, 1.0)
    box(cv, 456, 132, 504, 138, YELL, 3.4, edge=False)
    text(cv, 'PERILL', 466, 133, DARK, 0.6)


# ─── El racó dret ────────────────────────────────────────────────────────────

def radio_clock(cv):
    cx, cy, r = 150, 58, 16
    cv.disc(cx, cy, r + 3, r + 3, BRASS, lambda nx, ny: 3.6 - nx - ny * 1.2)
    cv.disc(cx, cy, r, r, WHITEP, 4.0)
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            d = math.hypot(x - cx, y - cy)
            if r - 5 <= d <= r - 1:
                m = ((math.degrees(math.atan2(x - cx, cy - y)) + 360) % 360) / 6
                if 15 <= m < 18 or 45 <= m < 48:
                    cv.put(x, y, REDP, 4.0)
                elif 0 <= m < 3 or 30 <= m < 33:
                    cv.put(x, y, SCRG, 3.4)
    for a in range(0, 360, 6):
        px, py = cx + round(math.sin(math.radians(a)) * (r - 1)), cy - round(math.cos(math.radians(a)) * (r - 1))
        cv.put(px, py, DARK, 0.4) if a % 30 == 0 else cv.put(px, py, WHITEP, 2.6)
    cv.line(cx, cy, cx + 7, cy - 5, DARK, 0.2)
    cv.line(cx, cy, cx - 3, cy - 11, DARK, 0.2)
    cv.line(cx, cy, cx + 2, cy + 12, REDP, 3.0)
    cv.disc(cx, cy, 1.5, 1.5, REDP, 3.0)


def shelf(cv):
    x0, x1 = 548, 630
    box(cv, x0, 122, x1, 126, WOOD, 3.6)
    for bx in (x0 + 6, x1 - 8):
        cv.poly([(bx, 127), (bx + 3, 127), (bx + 3, 136)], CAB, 2.6)
    x, i = x0 + 2, 0
    while x < x1 - 6:
        w = 5 + int(hr(i, 2) * 5)
        h = 18 + int(hr(i, 3) * 8)
        ramp = [CABLE, [(20, 30, 60), (36, 52, 96), (60, 80, 130), (100, 120, 170)],
                [(60, 20, 20), (100, 34, 30), (140, 54, 44), (180, 90, 70)], WOOD][int(hr(i, 4) * 4)]
        if i == 6:                                                       # un llibre ajagut
            box(cv, x, 116, x + 18, 121, ramp, 2.6)
            x += 20
            i += 1
            continue
        box(cv, x, 122 - h, x + w - 1, 121, ramp, 2.4, edge=False)
        cv.vline(x, 122 - h, 121, ramp, 3.4)
        cv.hline(x + 1, x + w - 2, 122 - h + 4, WHITEP, 2.6)
        cv.hline(x + 1, x + w - 2, 122 - h + 6, WHITEP, 2.2)
        x += w + 1
        i += 1
    cv.hline(x0, x1, 110, BRASS, 3.2)
    for px in (x0 + 2, (x0 + x1) // 2, x1 - 2):
        cv.vline(px, 110, 121, BRASS, 2.8)


def porthole(cv):
    cx, cy = 588, 66
    cv.disc(cx, cy, 18, 18, BRASS, lambda nx, ny: 3.6 - nx - ny * 1.2)
    cv.disc(cx, cy, 14, 14, DARK, 1.0)
    tmp = Canvas(light=LIGHT)
    outside(tmp, cx - 13, cy - 13, cx + 13, cy + 13, horizon=cy + 4, moon=(cx - 5, cy - 6))
    for X, Y, x, y in cv.pixels(cx - 13, cy - 13, cx + 13, cy + 13):
        if (x - cx) ** 2 + (y - cy) ** 2 <= 169:
            cv.P[X, Y] = tmp.P[X, Y]
    for a in range(0, 360, 45):
        bolt(cv, cx + round(math.cos(math.radians(a)) * 16), cy + round(math.sin(math.radians(a)) * 16), BRASS, 3.0)
    for i in range(8):
        cv.flat(cx - 7 + i, cy - 8 + i, mix(cv.get(cx - 7 + i, cy - 8 + i)[:3],
                                            (236, 240, 244) if _MODE['dia'] else (150, 160, 180), 0.3))


def extinguisher(cv):
    x0, x1 = 600, 614
    for y in range(155, FLOOR_Y + 3):
        for x in range(x0, x1 + 1):
            u = (x - (x0 + x1) / 2) / 7.5
            cv.put(x, y, REDP, 3.6 + 1.4 * (-0.3 - u) - 0.8 * u * u)
    cv.disc((x0 + x1) / 2, 155, 7, 4, REDP, 4.2)
    box(cv, 604, 143, 610, 151, CAB, 3.4)
    cv.line(610, 146, 618, 143, CAB, 3.4)
    for i in range(12):
        cv.put(618 + (i % 2), 143 + i * 2, DARK, 1.6)
    cv.rect(x0 + 2, 170, x1 - 2, 180, WHITEP, 3.6)
    text(cv, 'CO2', x0 + 2, 172, DARK, 0.6)
    box(cv, 598, 162, 616, 164, CAB, 2.6)


def bg(cv):
    wall(cv)
    ceiling(cv)
    door(cv)
    notices(cv)
    panel(cv)
    desk(cv)
    radio(cv)
    radio_clock(cv)
    shelf(cv)
    porthole(cv)
    floor(cv)
    extinguisher(cv)
    glow(cv, LAMP[0], LAMP[1] + 2, 40, WARM, 0.25 if _MODE['dia'] else 0.45)
    glow(cv, LAMP[0], LAMP[1] + 2, 13, (255, 240, 200), 0.6)


# ─── Props ──────────────────────────────────────────────────────────────────
# Coordenades: les de 480 (hd/rooms/sala_radio.py) passades al panell de 640, X = 440 + (x - 330)·4/3, Y = 80 + (y - 60)·4/3.

CX = 480                          # el cable de l'antena baixa pel mig del panell


def panell_obert(cv):
    """El panell sense la xapa: el forat fosc, el cable de l'antena que hi baixa i el born de connexió. La xapa,
    a terra, recolzada a la paret; una gota de sang seca a la vora."""
    x0, y0, x1, y1 = PANEL
    box(cv, x0, y0, x1, y1, DARK, 1.2)
    for y in range(y0 + 1, y1):
        cv.hline(x0 + 1, x1 - 1, y, DARK, 1.4 + (y - y0) * 0.015)
    for bx, by in ((x0 + 5, y0 + 5), (x1 - 6, y0 + 5), (x0 + 5, y1 - 6), (x1 - 6, y1 - 6)):     # forats dels cargols
        cv.disc(bx, by, 2.2, 2.2, BRI, 4.4)
        cv.put(bx, by, DARK, 0)
    cv.hline(x0, x1, y0, BRI, 5.4)                                    # la vora tallant
    cv.vline(x0, y0, y1, BRI, 4.8)
    cv.hline(x0 + 1, x1 - 1, y0 + 1, BRI, 3.0)
    cv.flat(x1, y0 + 40, (110, 20, 18))                               # la gota de sang
    cv.flat(x1, y0 + 41, (80, 14, 14))
    cv.flat(x1 - 1, y0 + 41, (90, 16, 16))
    # els cables secundaris, al fons, en una safata (amb les brides)
    for yy, col in ((91, CABLE), (96, [(60, 20, 20), (120, 40, 34), (180, 70, 50)]), (155, CABLE)):
        cv.hline(x0 + 4, x1 - 4, yy, col, 2.2)
        cv.hline(x0 + 4, x1 - 4, yy + 1, col, 1.2)
    for bx in range(x0 + 10, x1 - 6, 16):
        cv.vline(bx, 90, 97, WHITEP, 2.0)
    # el cable de l'antena: baixa del sostre fins al tall (a dalt) i del tall al born (a baix)
    _cable(cv, CX, y0 + 1, 101)
    _end(cv, CX, 101, up=True)
    _cable(cv, CX, 140, 144)
    _end(cv, CX, 140, up=False)
    # el born de connexió i la sortida cap a la ràdio
    box(cv, 467, 144, 493, 152, CAB, 3.2)
    for bx in (472, 480, 488):
        cv.disc(bx, 148, 2, 2, BRASS, 4.2)
        cv.put(bx, 148, DARK, 1.0)
    cv.hline(x0 + 1, 467, 143, CABLE, 2.4)
    cv.hline(x0 + 1, 467, 142, CABLE, 3.2)
    # la xapa, a terra, recolzada a la paret
    cv.poly([(525, FLOOR_Y + 5), (581, FLOOR_Y + 5), (589, 136), (536, 136)], BRI, lambda x, y: 3.8 - (y - 136) * 0.022)
    cv.line(536, 136, 589, 136, BRI, 5.0)
    cv.line(525, FLOOR_Y + 5, 536, 136, BRI, 4.6)
    cv.line(581, FLOOR_Y + 5, 589, 136, BRI, 1.6)
    for bx, by in ((540, 141), (583, 141), (532, 200), (576, 200)):
        cv.disc(bx, by, 1.6, 1.6, DARK, 0.6)
    cv.poly([(559, 147), (567, 161), (551, 161)], YELL, 3.8)
    box(cv, 539, 168, 576, 174, WHITEP, 3.4)


def _cable(cv, cx, y0, y1):
    """Cable gruixut de funda negra (7 px)."""
    for y in range(y0, y1 + 1):
        for x in range(cx - 3, cx + 4):
            u = (x - cx) / 3.5
            cv.put(x, y, CABLE, 3.9 + 1.6 * (-0.3 - u) - 0.8 * u * u, lit=0.5)


def _end(cv, cx, y, up):
    """El cap tallat: la funda s'acaba i en surt la malla d'acer, esfilagarsada."""
    d = 1 if up else -1
    for i in range(5):
        yy = y + d * (i + 1)
        for x in range(cx - 3, cx + 4):
            if hr(x, yy) > 0.25 + i * 0.12:
                cv.put(x + (1 if i >= 3 and x > cx else -1 if i >= 3 and x < cx else 0), yy, MESH, 2.6 - i * 0.3)
    cv.put(cx, y + d * 6, MESH, 3.4)                                  # el fil de coure del mig
    cv.put(cx, y + d * 7, [(80, 40, 20), (200, 120, 60)], 1.4)
    cv.put(cx, y + d * 8, [(80, 40, 20), (200, 120, 60)], 1.0)


def cable(cv):
    """El tram tallat: el tros del mig, encara al seu lloc, amb el tall net (i l'osca de la cisalla mellada)."""
    _cable(cv, CX, 102, 117)
    _cable(cv, CX + 1, 122, 139)                                      # el tros de sota, una mica de biaix
    for x in range(CX - 3, CX + 4):                                   # la malla d'acer, a cada costat del tall
        cv.put(x, 118, MESH, 3.0 if x % 2 else 2.0)
        cv.put(x + 1, 121, MESH, 3.0 if x % 2 else 2.0)
    cv.put(CX, 119, [(80, 40, 20), (200, 120, 60)], 1.4)              # el fil de coure del mig
    cv.put(CX, 120, [(80, 40, 20), (200, 120, 60)], 1.0)
    cv.put(CX - 3, 118, DARK, 0)                                      # l'osca
    cv.put(CX - 2, 118, DARK, 0)
    cv.put(CX - 2, 121, DARK, 0)


def panell_reparat(cv):
    """Decorat `panell_reparat` (connector crimpat, panell encara obert): el tram nou al forat del tallat, amb la
    funda més lluent, i una virolla crimpada a cada empalmament, tapant la malla esfilagarsada."""
    _cable(cv, CX, 102, 139)
    for y in range(105, 137):                                         # funda nova: una lluentor que la deixa veure
        cv.put(CX - 1, y, CABLE, 4.4, lit=0.5)
    _virolla(cv, CX, 102, 110)
    _virolla(cv, CX, 131, 139)


def _virolla(cv, cx, y0, y1):
    """Virolla de metall (9 px d'ample) crimpada: un cilindre lluent amb les marques de la crimpadora."""
    for y in range(y0, y1 + 1):
        for x in range(cx - 4, cx + 5):
            u = (x - cx) / 4.5
            lvl = 2.4 + 1.2 * (-0.3 - u) - 0.7 * u * u
            if y in (y0 + 2, y0 + 3, y1 - 3, y1 - 2):                 # les dues marques del crimpat
                lvl -= 1.1
            cv.put(x, y, MESH, lvl, lit=0.5)
    cv.hline(cx - 3, cx + 3, y0, MESH, 1.2, lit=0.3)                  # les vores
    cv.hline(cx - 3, cx + 3, y1, MESH, 1.0, lit=0.3)


def dia(cv):
    """Decorat `dia` (sota, Escenes 2 i 3): la sala sencera de dia, amb el cel gris a l'ull de bou i al vidre
    del pont, que es veu per la porta."""
    _MODE['dia'] = True
    try:
        day = Canvas(light=LIGHT_DIA)
        bg(day)
    finally:
        _MODE['dia'] = False
    day.tint(0, 0, W - 1, H - 1, (150, 160, 172), 0.08)
    cv.img.paste(day.img)


PROPS = {'dia': dia, 'panell_obert': panell_obert, 'cable': cable, 'panell_reparat': panell_reparat}


# ─── Animacions ────────────────────────────────────────────────────────────

def _frames(draw):
    """Fotogrames: la sala sencera a cada fotograma, menys el fons quiet (només el que canvia)."""
    def render(f):
        _ANIM['f'] = f
        try:
            cv = Canvas(light=LIGHT)
            draw(cv)
            return cv.img
        finally:
            _ANIM['f'] = 0
    base = render(0)
    return [_diff(render(f), base) for f in range(ANIM_N)]


ANIMS = {'mar': {'frames': lambda: _frames(bg), 'frameDuration': 260},
         'dia_mar': {'frames': lambda: _frames(dia), 'frameDuration': 260}}


# ─── Geometria (×4/3 de la de 480) ─────────────────────────────────────────

def _t(x0, y0, x1, y1, wx=None, wy=240):
    return {'rect': (x0, y0, x1, y1), 'walk': (wx if wx is not None else (x0 + x1) // 2, wy)}
