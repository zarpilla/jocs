#!/usr/bin/env python3
"""
Prova d'intro animada de Ni un ou (vídeo de pixel art, 1280×720: art a 2×, com les sales): els primers ~30 segons.

  Pla A, la portada: fosa des del negre, el mar que es mou, el títol que apareix i regalima; s'esvaeix.
  Pla B, el pròleg: la grua baixa la zòdiac amb la Juana, toca l'aigua, la deslliguen, va a poc a poc cap a la
  plataforma, s'atura; la Juana encén la llanterna, treu la mostra de l'aigua i l'aixeca a contrallum. A la
  plataforma s'encén el focus de la silueta, i en Bastida treu la pantalleta. Fosa a negre.

Tot es dibuixa fotograma a fotograma amb les mateixes funcions que les sales (hd640/rooms/portada.py i
hd/rooms/exterior.py), en coordenades de 640×360 sobre un Canvas2x (hd1280/canvas2x.py), i ffmpeg ho munta amb el
tema. El pla B és el del pròleg antic (abans que el pròleg passés a fer-se al mateix pla que la portada): en
Bastida i les constants del pla en són una còpia, aquí mateix.

Ús: python3 intro_animada.py <carpeta de sortida> [--fps 12] [--only 120,240]
"""
import argparse
import functools
import math
import os
import subprocess
import sys
from multiprocessing import Pool
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import hd.pix as pix  # noqa: E402

# hr() crea un Random a cada crida: amb memòria, el mar d'un fotograma surt molt més de pressa (mateix resultat).
pix.hr = functools.lru_cache(maxsize=1 << 22)(pix.hr)

import hd640  # noqa: E402,F401  (posa la llibreria a 640×360)
import room_designs  # noqa: E402,F401  (carrega les sales en l'ordre bo)
from hd.pix import Light, W, H, mix, hr  # noqa: E402
from hd1280.canvas2x import Canvas2x as Canvas, S as ART  # noqa: E402  (art a 2×: 1280×720)
from hd.rooms.exterior import arenga, platform, reflection, sheer, STEELX, ROPE, GLOW_WARM  # noqa: E402
from hd640.rooms import portada as po  # noqa: E402

GAME = HERE.parent.parent.parent
MUSIC = GAME / 'game' / 'audio' / 'music' / 'tema.ogg'
SEA = GAME / 'ni-un-ou' / 'src' / 'game' / 'assets' / 'audio' / 'sfx' / 'amb_mar.ogg'

# ─── Temps (segons) ─────────────────────────────────────────────────────────
FADE_IN = (0.0, 1.6)
TITLE_IN = (1.2, 2.6)
DRIPS = (2.2, 4.6)
TITLE_OUT = (5.8, 6.8)
B0 = 6.8                     # comença el pla B (fosa tramada de A a B)
XFADE = (6.8, 8.0)
# dins del pla B (tb = t - B0)
LOWER = (2.0, 7.0)
TOUCH = 7.0
UNHOOK = (7.6, 8.8)
SHUFFLE1 = (8.4, 9.2)        # la Juana va cap al motor
MOTOR = 9.2
MOVE = (9.6, 15.6)
SHUFFLE2 = (15.8, 16.5)      # torna al mig
LANTERN = 16.7
REACH = (17.1, 18.0)
SCOOP = (18.0, 18.7)
RAISE = (18.7, 19.9)
WATCHER = 20.6
DEVICE = 21.6
FADE_OUT = (23.4, 25.2)
B_LEN = 25.4
TOTAL = B0 + B_LEN


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def seg(t, ab):
    return ease((t - ab[0]) / (ab[1] - ab[0]))


def lerp(a, b, k):
    return a + (b - a) * k


# Bayer 8×8 per a les foses tramades (64 nivells)
def _bayer(n):
    if n == 1:
        return np.zeros((1, 1))
    m = _bayer(n // 2)
    return np.block([[4 * m, 4 * m + 2], [4 * m + 3, 4 * m + 1]])


TH = np.tile((_bayer(8) + 0.5) / 64, (H * ART // 8 + 1, W * ART // 8 + 1))[:H * ART, :W * ART]   # (píxels reals)


def dmix(a, b, k):
    """Fosa tramada: k=0 → a, k=1 → b."""
    if k <= 0:
        return a
    if k >= 1:
        return b
    m = TH < k
    out = a.copy()
    out[m] = b[m]
    return out


def arr(cv):
    return np.asarray(cv.img)[:, :, :3].copy()


@functools.cache
def sky(which):
    cv = Canvas(light=po.LIGHT)
    if which == 'A':
        po.night_sky(cv, 0, po.HOR, moon=po.MOON, seed=31, clouds=0.55)
    else:
        po.night_sky(cv, 0, pr.HOR, moon=pr.MOON, seed=21, clouds=0.6)
    return cv.img


@functools.cache
def title_layer():
    cv = Canvas(light=po.LIGHT, transparent=True)
    po.title(cv)
    a = np.asarray(cv.img)
    return a[:, :, :3].copy(), a[:, :, 3] > 0


# ─── Pla A: la portada ──────────────────────────────────────────────────────

def shot_a(t):
    cv = Canvas(light=po.LIGHT, img=sky('A').copy())
    cv.P = cv.img.load()
    st = int(t * 3.3)                                       # les guspires i els reflexos canvien a ~3 per segon
    po.night_sea(cv, po.HOR, H - 1, moon_x=po.MOON[0], seed=32, phase=t * 1.5, path=(2.5, 0.27), twinkle=st)
    platform(cv, po.PLAT[0], po.PLAT[1], po.PLAT[2], 'night')
    reflection(cv, po.PLAT[0] - 67, po.PLAT[0] + 67, po.PLAT[1], 40, k=0.45, seed=33 + st)
    xs, ywl, s = po.SHIP
    if 0.9 <= t % 2.4 < 2.1:
        ywl -= 1
    arenga(cv, xs, ywl, s, 'night', facing=1)
    reflection(cv, xs - 11, xs + 224, ywl, 40, k=0.3, seed=35 + st)
    if int(t / 0.6) % 2:
        lx, ly = round(po.PLAT[0] + 10 * po.PLAT[2]), round(po.PLAT[1] - 30 * po.PLAT[2])
        cv.rect(lx, ly, lx + 1, ly + 1, [(90, 20, 20)], 0, lit=0)
    img = arr(cv)
    # el títol: les lletres apareixen tramades i els regalims creixen cap avall
    col, mask = title_layer()
    base = (po.TITLE_Y + 7 * po.S + 5) * ART                # (en píxels reals)
    k_in, k_out = seg(t, TITLE_IN), seg(t, TITLE_OUT)
    grow = seg(t, DRIPS) * 40 * ART
    ys = np.arange(H * ART)[:, None]
    show = mask & (TH < k_in) & ~(TH < k_out) & ((ys <= base) | (ys < base + grow))
    img[show] = col[show]
    return img


# ─── Pla B: el pròleg ───────────────────────────────────────────────────────
# El pla del pròleg antic (hd640/rooms/proleg_punt7.py fins al commit 4cdff5a): la popa de l'Arenga a l'esquerra,
# mirant a l'esquerra, i la plataforma al fons a la dreta.

SIL = [(4, 5, 8), (8, 9, 14), (14, 16, 22), (22, 24, 32), (34, 36, 46)]
JACKET = [(20, 8, 6), (50, 16, 10), (96, 34, 16), (150, 62, 28), (196, 104, 50)]
SKINR = [(40, 22, 18), (90, 52, 40), (150, 96, 70), (200, 140, 104)]
ZODR = [(18, 18, 22), (30, 30, 36), (46, 46, 52), (66, 66, 72), (90, 90, 94), (120, 120, 122)]
HAT = [(14, 34, 20), (20, 50, 30), (40, 90, 50), (70, 130, 80)]
BEARD = [(110, 110, 108), (160, 160, 156), (200, 200, 196), (226, 226, 222)]
JAR = [(60, 56, 46), (110, 104, 84), (170, 164, 140), (220, 216, 196)]
CRANEW = [(60, 46, 10), (130, 100, 20), (200, 160, 40), (236, 200, 80)]


def bastida(cv, x, y):
    """En Bastida a la borda de popa: gorra, barba blanca, la pipa encesa i, a la mà, la pantalleta que fa llum."""
    # el cos (de la cintura amunt; la resta queda darrere la borda): l'anorac fosc amb el coll alçat
    cv.rect(x - 4, y - 15, x + 4, y, SIL, 2.4)
    cv.vline(x + 4, y - 14, y, SIL, 3.2)                                   # la vora de la dreta, amb la lluna
    cv.vline(x - 4, y - 14, y, SIL, 1.6)
    cv.hline(x - 4, x + 4, y - 15, SIL, 3.0)                               # el coll
    cv.vline(x, y - 13, y, SIL, 1.4)                                       # la cremallera
    # la cara, mig a l'ombra, i l'ull
    cv.rect(x - 3, y - 22, x + 3, y - 16, SKINR, 1.6)
    cv.vline(x + 2, y - 21, y - 17, SKINR, 2.6)
    cv.vline(x + 3, y - 21, y - 18, SKINR, 2.2)
    cv.flat(x + 1, y - 20, (16, 10, 10))
    cv.hline(x, x + 2, y - 21, BEARD, 1.2)                                 # la cella, blanca
    # la barba blanca, que s'aprima cap avall
    cv.rect(x - 3, y - 18, x + 3, y - 16, BEARD, 2.4, lit=0)
    cv.hline(x - 2, x + 2, y - 15, BEARD, 2.0, lit=0)
    cv.put(x + 2, y - 17, BEARD, 3.0, lit=0)
    # la gorra de llana, amb la vora girada
    cv.rect(x - 4, y - 26, x + 3, y - 23, SIL, 1.2)
    cv.hline(x - 4, x + 4, y - 23, SIL, 2.2)
    cv.hline(x - 3, x + 2, y - 26, SIL, 1.8)
    # la pipa, amb la brasa i un fil de fum
    cv.hline(x + 3, x + 5, y - 17, ROPE, 2.0)
    cv.rect(x + 5, y - 19, x + 6, y - 17, ROPE, 1.6)
    cv.flat(x + 5, y - 20, (255, 140, 60))
    cv.flat(x + 6, y - 20, (200, 80, 30))
    cv.glow(x + 5, y - 20, 3, (255, 140, 60), 0.4)
    for i in range(7):
        cv.flat(x + 6 + round(math.sin(i * 0.9) * 1.2), y - 22 - i * 2,
                mix(cv.get(x + 6 + round(math.sin(i * 0.9) * 1.2), y - 22 - i * 2), (120, 126, 140), 0.35 - i * 0.04))
    # el braç i la pantalleta (el missatger de satèl·lit), que li il·lumina la mà i la barba
    cv.line(x - 3, y - 12, x - 7, y - 7, SIL, 3.0)
    cv.line(x - 3, y - 11, x - 7, y - 6, SIL, 2.0)
    cv.rect(x - 10, y - 8, x - 7, y - 4, [(30, 50, 70)], 0, lit=0)
    cv.rect(x - 9, y - 7, x - 8, y - 5, [(150, 226, 255)], 0, lit=0)
    cv.glow(x - 8, y - 6, 9, (120, 210, 255), 0.5)
    cv.flat(x - 3, y - 16, mix(cv.get(x - 3, y - 16), (140, 210, 240), 0.35))


pr = SimpleNamespace(HOR=187, SHIP=(261, 243, 7.0 * po.K), PLAT=(536, 187 + 4, 3.0 * po.K), MOON=(128, 48),
                     LIGHT=Light(ambient=0.0, vignette=None, floor_fade=None), bastida=bastida)

XS, YWL, SS = pr.SHIP


def X(m):
    return XS - m * SS


def Y(m):
    return YWL - m * SS


TIP = (round(X(-4.0)), round(Y(9.6)))         # la punta del braç de la grua, girat cap a fora
CX0, WL_HANG, WL_WATER = TIP[0] - 2, 206, 252
CX1, WL1 = 392, 266
HOOK_UP = 176


def zpos(tb):
    """→ (cx, wl, a l'aigua?)"""
    if tb < TOUCH:
        k = seg(tb, LOWER)
        sway = 2.2 * math.sin(tb * 2.3) * (1 - 0.7 * k)
        return round(CX0 + sway), round(lerp(WL_HANG, WL_WATER, k)), False
    k = seg(tb, MOVE)
    d = tb - TOUCH
    bob = 3.0 * math.exp(-d * 2.2) * math.sin(d * 9) + 0.9 * math.sin(tb * 2.6)
    return round(lerp(CX0, CX1, k)), round(lerp(WL_WATER, WL1, k) + bob), True


def crane(cv):
    post = round(X(3.2))
    cv.rect(post - 1, round(Y(5.8)), post + 1, round(Y(sheer(3))), STEELX, lambda x, y: 4.4 if x == post - 1 else 3.2, lit=0)
    cv.rect(post + 2, round(Y(4.6)), post + 5, round(Y(4.0)), STEELX, 2.6, lit=0)        # el tambor del cable
    cv.disc(post + 3.5, round(Y(4.3)), 1.5, 1.5, STEELX, 4.0, lit=0)
    tx, ty = TIP
    cv.line(post, round(Y(5.8)), tx, ty, CRANEW, 2.0, lit=0)
    cv.line(post, round(Y(5.5)), tx, ty + 1, CRANEW, 3.0, lit=0)
    cv.line(post, round(Y(5.3)), tx, ty + 2, CRANEW, 1.0, lit=0)
    cv.rect(tx - 1, ty - 1, tx + 2, ty + 3, STEELX, 3.6, lit=0)                         # la politja
    cv.glow(post, round(Y(6.2)), 14, GLOW_WARM, 0.3)
    cv.flat(post, round(Y(6.2)), (255, 240, 200))
    # el comandament, on en Bastida té la mà
    cv.rect(post - 7, round(Y(4.9)), post - 3, round(Y(4.3)), STEELX, 3.0, lit=0)
    cv.flat(post - 5, round(Y(4.9)) + 1, (255, 120, 40))


def bastida_layer(cv, tb, before):
    """En Bastida; si no fa servir la pantalleta, se li treu (es repinta la zona amb el fons d'abans)."""
    x, y = round(X(5.5)), round(Y(sheer(5.5)) - 1)
    arm = 'device' if tb >= DEVICE else ('lever' if 1.4 <= tb < 9.2 else 'down')
    pr.bastida(cv, x, y)
    if arm != 'device':
        bp = before.load()
        for X_, Y_, _, _ in cv.pixels(x - 19, y - 18, x - 5, y + 3):
            cv.P[X_, Y_] = bp[X_, Y_]
        cv.vline(x - 4, y - 14, y, SIL, 1.6)
        if arm == 'lever':
            post = round(X(3.2))
            hx, hy = post - 5, round(Y(4.9)) - 1
            if 2.0 <= tb < 7.0:
                hy += round(math.sin(tb * 3) * 0.6)
            cv.line(x + 3, y - 12, hx, hy, SIL, 3.0, lit=0)
            cv.line(x + 3, y - 11, hx, hy + 1, SIL, 2.0, lit=0)
            cv.flat(hx, hy, (120, 80, 60))
        else:
            cv.line(x - 3, y - 12, x - 5, y - 1, SIL, 2.4, lit=0)
    else:
        if int(tb * 6) % 3 == 0:
            cv.flat(x - 8, y - 6, (230, 250, 255))


def ring(cv, cx, cy, r, k, seed):
    if k <= 0.02:
        return
    for a in range(0, 360, 2):
        px = cx + round(math.cos(math.radians(a)) * r)
        py = cy + round(math.sin(math.radians(a)) * r * 0.12)
        if 0 <= px < W and 0 <= py < H and hr(a, seed) > 0.35:
            cv.flat(px, py, mix(cv.get(px, py), (130, 150, 170), k))


def droplets(cv, x0, wl, t, n, spread, seed, power=1.0):
    """Esquitxos: gotes que salten i cauen (t = segons des del cop)."""
    for i in range(n):
        vx = (hr(i, seed, 1) - 0.5) * 40 * power
        vy = -(30 + hr(i, seed, 2) * 50) * power
        xx = x0 + (hr(i, seed, 3) - 0.5) * spread + vx * t
        yy = wl + vy * t + 0.5 * 260 * t * t
        if yy <= wl and 0 <= xx < W:
            cv.flat(round(xx), round(yy), (190, 210, 220) if hr(i, seed, 4) > 0.4 else (120, 140, 160))


def wake(cv, tb):
    for k in range(1, 46):
        tp = tb - k * 0.1
        if tp < MOVE[0] - 0.4:
            break
        if tp > MOVE[1] - 0.6:              # quan s'atura, ja no en fa
            continue
        cx, wl, _ = zpos(tp)
        age = k * 0.1
        a = 0.6 * (1 - age / 4.6)
        if a <= 0:
            break
        x = cx - 40
        for side in (-1, 1):
            yy = wl + 2 + side * round(age * 0.9)
            for dx in range(-3, 4):
                if hr(k + int(tp * 10), dx, side) > 0.45:
                    px = x + dx - round(age * 2)
                    if 0 <= px < W and 0 <= yy < H:
                        cv.flat(px, yy, mix(cv.get(px, yy), (150, 170, 180), a))


def zodiac_shadow(cv, cx, wl):
    for y in range(wl + 1, wl + 5):
        for x in range(cx - 38, cx + 34):
            if 0 <= x < W and 0 <= y < H and hr(x, y, 41) > 0.3:
                cv.flat(x, y, mix(cv.get(x, y), (3, 5, 9), 0.55 * (1 - (y - wl) / 5)))


def zodiac(cv, cx, wl, motor_on, tb):
    for x in range(cx - 35, cx + 36):
        t = (x - cx + 35) / 70
        lift = int(4 * max(0.0, (t - 0.8) / 0.2) ** 1.5) if t > 0.8 else 0
        r = 5 if t < 0.95 else 4
        cyy = wl - 4 - lift
        for y in range(cyy - r, cyy + r + 1):
            u = (y - cyy) / (r + 0.5)
            cv.put(x, y, ZODR, 2.6 - u * 1.4 - u * u, lit=0)
        if t < 0.98:
            cv.put(x, cyy + 1, [(140, 50, 20), (200, 90, 40)], 0.4, lit=0)
            cv.put(x, cyy + 2, [(140, 50, 20), (200, 90, 40)], 0.0, lit=0)
        if x % 9 == 0 and t < 0.95:
            cv.put(x, cyy - r + 1, ROPE, 2.4, lit=0)
            cv.put(x + 1, cyy - r + 1, ROPE, 2.4, lit=0)
    shake = 1 if motor_on and int(tb * 12) % 2 else 0
    cv.rect(cx - 43, wl - 16 - shake, cx - 35, wl - 7, ZODR, 1.0, lit=0)
    cv.hline(cx - 43, cx - 35, wl - 16 - shake, ZODR, 2.2, lit=0)
    cv.rect(cx - 41, wl - 7, cx - 38, wl + 2, ZODR, 0.6, lit=0)
    cv.put(cx - 42, wl - 13, [(140, 50, 20), (200, 90, 40)], 1.0, lit=0)
    cv.line(cx - 35, wl - 14, cx - 27, wl - 12, ZODR, 2.0, lit=0)          # la canya del timó
    if motor_on:
        for i in range(6):                                                  # l'aigua remenada per l'hèlix
            if hr(i, int(tb * 12), 5) > 0.4:
                cv.flat(cx - 44 - round(hr(i, int(tb * 12), 6) * 6), wl + 1 + (i % 2), (170, 190, 200))


def cable(cv, hook, attached, cx, wl):
    tx, ty = TIP
    hx, hy = hook
    cv.line(tx, ty + 3, hx, hy, STEELX, 3.0, lit=0)
    cv.line(tx + 1, ty + 3, hx + 1, hy, STEELX, 1.8, lit=0)
    cv.rect(hx - 1, hy, hx + 2, hy + 3, STEELX, 3.6, lit=0)
    cv.put(hx + 2, hy + 4, STEELX, 4.2, lit=0)
    if attached:                                                            # les eslingues, fins als flotadors
        for ex_, ey in ((cx - 30, wl - 10), (cx + 30, wl - 11), (cx - 12, wl - 10), (cx + 14, wl - 10)):
            cv.line(hx + 1, hy + 4, ex_, ey, STEELX, 2.2, lit=0)


def beam(cv, lx, ly, tx, ty):
    dx, dy = tx - lx, ty - ly
    d = math.hypot(dx, dy) or 1
    ux, uy = dx / d, dy / d
    nx, ny = -uy, ux
    n = int(min(44, d + 10))
    for i in range(1, n):
        for w in range(-i // 4, i // 4 + 1):
            px = round(lx + ux * i + nx * w * 0.6)
            py = round(ly + uy * i + ny * w * 0.6)
            if 0 <= px < W and 0 <= py < H and hr(px, py, 9) > i / (n * 1.15):
                cv.flat(px, py, mix(cv.get(px, py), (255, 236, 180), 0.35 * (1 - i / (n + 2))))


def juana(cv, cx, wl, tb):
    # on seu: al mig mentre penja, a popa (al motor) mentre navega, al mig per agafar la mostra
    if tb < SHUFFLE1[0]:
        off = 5
    elif tb < SHUFFLE2[0]:
        off = round(lerp(5, -18, seg(tb, SHUFFLE1)))
    else:
        off = round(lerp(-18, 5, seg(tb, SHUFFLE2)))
    hop = 1 if (SHUFFLE1[0] < tb < SHUFFLE1[1] or SHUFFLE2[0] < tb < SHUFFLE2[1]) else 0
    f = -1 if tb < 6.0 else 1                    # mentre la baixen, mira en Bastida; després, endavant
    jx, jy = cx + off, wl - 9 - hop
    # el braç dret: repòs → a l'aigua → enlaire amb el pot
    rest, reach, up = (jx + 6, jy - 3), (jx + 17, wl + 2), (jx + 11, jy - 20)
    if tb < REACH[0]:
        h, lean = rest, 0.0
    elif tb < REACH[1]:
        k = seg(tb, REACH)
        h, lean = (lerp(rest[0], reach[0], k), lerp(rest[1], reach[1], k)), 4 * k
    elif tb < RAISE[0]:
        h, lean = (reach[0] + round(math.sin(tb * 13) * 1.2), reach[1]), 4.0
    elif tb < RAISE[1]:
        k = seg(tb, RAISE)
        h, lean = (lerp(reach[0], up[0], k), lerp(reach[1], up[1], k)), 4 * (1 - k)
    else:
        h, lean = (up[0], up[1] + round(math.sin(tb * 1.7) * 0.7)), 0.0
    hx, hy = round(h[0]), round(h[1])
    L = round(lean)
    hdx, hdy = L, L // 2
    # el cos: l'anorac (inclinat cap a la dreta si s'acosta a l'aigua)
    cv.poly([(jx - 4, jy + 1), (jx + 5, jy + 1), (jx + 5 + L, jy - 12 + hdy), (jx - 4 + L, jy - 12 + hdy)],
            JACKET, 2.0, lit=0)
    cv.line(jx - 4, jy, jx - 4 + L, jy - 12 + hdy, JACKET, 3.0, lit=0)
    cv.hline(jx - 3 + L // 2, jx + 3 + L // 2, jy - 6 + hdy // 2, JACKET, 1.2, lit=0)
    # el cap
    x0, y0 = jx + hdx, jy + hdy
    cv.rect(x0 - 3, y0 - 19, x0 + 3, y0 - 13, SKINR, 1.8, lit=0)
    lantern_on = tb >= LANTERN
    cv.vline(x0 + 3 * f, y0 - 18, y0 - 14, SKINR, 2.8 if lantern_on else 2.2, lit=0)
    cv.hline(min(x0 + f, x0 + 3 * f), max(x0 + f, x0 + 3 * f), y0 - 17, [(200, 210, 220)], 0, lit=0)
    cv.flat(x0 + 2 * f, y0 - 17, (16, 10, 10))
    for yy in range(y0 - 18, y0 - 12):
        cv.put(x0 - 3 * f, yy, [(30, 20, 14), (56, 36, 24)], 0.6, lit=0)
    cv.put(x0 - 4 * f, y0 - 14, [(30, 20, 14), (56, 36, 24)], 0.4, lit=0)
    cv.rect(x0 - 4, y0 - 22, x0 + 4, y0 - 19, HAT, 1.6, lit=0)
    cv.hline(x0 - 4, x0 + 4, y0 - 19, HAT, 2.6, lit=0)
    cv.disc(x0 - f, y0 - 23, 1.6, 1.4, HAT, 3.0, lit=0)
    # el braç esquerre: la canya del timó, la llanterna o en repòs
    sx, sy = x0 - 3, y0 - 10
    lamp = None
    if MOTOR - 0.2 <= tb < MOVE[1] + 0.1:
        cv.line(sx, sy, cx - 27, wl - 12, JACKET, 2.4, lit=0)
        cv.flat(cx - 27, wl - 12, SKINR[2])
    elif lantern_on:
        lx, ly = x0 - 5, y0 - 8
        cv.line(sx, sy, lx + 1, ly + 1, JACKET, 2.4, lit=0)
        cv.rect(lx - 3, ly - 1, lx, ly + 1, SIL, 3.0, lit=0)
        cv.flat(lx + 1, ly, (255, 246, 220))
        lamp = (lx, ly)
    else:
        cv.line(sx, sy, jx - 6, jy - 3, JACKET, 2.4, lit=0)
    # el braç dret i el pot
    cv.line(x0 + 3, y0 - 10, hx, hy, JACKET, 2.4, lit=0)
    cv.line(x0 + 3, y0 - 9, hx, hy + 1, JACKET, 1.4, lit=0)
    has_jar = tb >= SCOOP[0]
    if has_jar and hy < wl - 1:
        cv.rect(hx - 2, hy - 8, hx + 2, hy, JAR, 1.6, lit=0)
        cv.hline(hx - 2, hx + 2, hy - 9, [(120, 120, 124), (170, 170, 172)], 1.0, lit=0)
        cv.vline(hx - 1, hy - 7, hy - 1, JAR, 3.0, lit=0)
        cv.rect(hx, hy - 4, hx + 1, hy - 1, [(90, 86, 76)], 0, lit=0)
        cv.hline(hx - 1, hx + 1, hy - 4, [(130, 126, 106)], 0, lit=0)
    else:
        cv.flat(hx, hy, SKINR[2])
    # la llum
    if lamp:
        lx, ly = lamp
        if tb < REACH[0]:
            tgt = (lx + 30, wl + 6)
        elif tb < RAISE[0]:
            tgt = (hx, wl + 1)
        else:
            tgt = (round(lerp(hx, hx, 1)), hy - 4) if has_jar else (hx, hy)
        beam(cv, lx + 1, ly, *tgt)
        flick = 1.0 if tb - LANTERN > 0.25 else (0.3 if int((tb - LANTERN) * 24) % 2 else 0.9)
        cv.glow(lx, ly, 10, (255, 240, 200), 0.8 * flick)
        if has_jar and tb >= RAISE[1] - 0.3:
            cv.glow(hx, hy - 4, 14, GLOW_WARM, 0.4)
        for y in range(wl + 1, wl + 18):                      # el reflex de la llanterna a l'aigua
            for x in range(cx - 40, cx + 40):
                k = 0.24 * flick * (1 - (y - wl) / 18) * max(0.0, 1 - abs(x - (lx + 6)) / 28)
                if 0 <= x < W and 0 <= y < H and hr(x // 2, y, 31 + int(tb * 4)) > 0.62 and k > 0.05:
                    cv.flat(x, y, mix(cv.get(x, y), (255, 214, 140), k))
    return hx, hy


def shot_b(tb):
    cv = Canvas(light=pr.LIGHT, img=sky('B').copy())
    cv.P = cv.img.load()
    st = int(tb * 3.3)
    po.night_sea(cv, pr.HOR, H - 1, moon_x=pr.MOON[0], seed=22, phase=tb * 1.6)
    watcher = tb >= WATCHER and not (WATCHER + 0.15 < tb < WATCHER + 0.3)   # el focus s'encén amb un tremolor
    platform(cv, pr.PLAT[0], pr.PLAT[1], pr.PLAT[2], 'night', watcher=watcher)
    reflection(cv, pr.PLAT[0] - 80, pr.PLAT[0] + 80, pr.PLAT[1], 53, k=0.45, seed=23 + st)
    arenga(cv, XS, YWL, SS, 'night', facing=-1, crane=False, zodiac=False)
    crane(cv)
    before = cv.img.copy()
    bastida_layer(cv, tb, before)
    reflection(cv, 0, XS + 60, YWL, 45, k=0.32, seed=25 + st)

    cx, wl, floating = zpos(tb)
    if floating:
        d = tb - TOUCH
        ring(cv, cx, wl + 3, 40 + d * 26, 0.45 * (1 - d / 2.2), 1)
        ring(cv, cx, wl + 3, 36 + max(0, d - 0.4) * 22, 0.4 * (1 - (d - 0.4) / 2.2) if d > 0.4 else 0, 2)
        if tb > MOVE[0] - 0.4:
            wake(cv, tb)
        zodiac_shadow(cv, cx, wl)
        if REACH[1] - 0.1 < tb < RAISE[0] + 1.6:
            hd = tb - (REACH[1] - 0.1)
            ring(cv, cx + 22, wl + 3, 4 + hd * 12, 0.5 * (1 - hd / 1.6), 3)
    # el ganxo
    if tb < UNHOOK[0]:
        hook, attached = (cx + 2, wl - 42), True
    else:
        k = seg(tb, UNHOOK)
        hook, attached = (round(lerp(CX0 + 2, TIP[0] + round(math.sin(tb * 1.9) * 1.5), k)),
                          round(lerp(WL_WATER - 42, HOOK_UP, k))), False
    motor_on = MOTOR <= tb < MOVE[1] + 0.3
    if not attached:
        cable(cv, hook, False, cx, wl)
    zodiac(cv, cx, wl, motor_on, tb)
    if attached:
        cable(cv, hook, True, cx, wl)
    hx, hy = juana(cv, cx, wl, tb)
    # esquitxos: quan toca l'aigua, quan hi fica la mà i quan en treu el pot
    if floating and tb - TOUCH < 0.8:
        droplets(cv, cx, wl, tb - TOUCH, 26, 70, 11)
    if REACH[1] - 0.1 <= tb < REACH[1] + 0.5:
        droplets(cv, cx + 22, wl, tb - (REACH[1] - 0.1), 7, 6, 12, 0.6)
    if RAISE[0] <= tb < RAISE[0] + 0.6:
        droplets(cv, cx + 22, wl, tb - RAISE[0], 9, 6, 13, 0.7)
    # el motor en arrencar: unes bufades de fum
    if MOTOR <= tb < MOTOR + 2.2:
        for i in range(3):
            a = tb - MOTOR - i * 0.35
            if 0 <= a < 1.4:
                px, py = cx - 40 - round(a * 6), wl - 18 - round(a * 12)
                cv.disc(px, py, 1.5 + a * 2, 1.2 + a * 1.5, [(60, 64, 76), (90, 94, 104)], 0.5,  lit=0)
    if int(tb / 0.64) % 2:
        cv.glow(pr.PLAT[0] + 10 * pr.PLAT[2], pr.PLAT[1] - 30 * pr.PLAT[2], 8, (255, 40, 30), 0.3)
    return arr(cv)


# ─── Muntatge ───────────────────────────────────────────────────────────────

def frame(t):
    img = None
    if t < XFADE[1]:
        img = shot_a(t)
        img = dmix(np.zeros_like(img), img, seg(t, FADE_IN))
    if t >= B0:
        b = shot_b(t - B0)
        img = b if img is None else dmix(img, b, seg(t, XFADE))
        img = dmix(img, np.zeros_like(img), seg(t - B0, FADE_OUT))
    return img


def work(job):
    i, fps, out = job
    Image.fromarray(frame(i / fps)).save(out / f'{i:04d}.png')
    return i


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out')
    ap.add_argument('--fps', type=int, default=12)
    ap.add_argument('--only', help='índexs de fotogrames, separats per comes (per provar)')
    a = ap.parse_args()
    out = Path(a.out)
    frames = out / 'frames'
    frames.mkdir(parents=True, exist_ok=True)
    n = int(TOTAL * a.fps)
    idx = [int(x) for x in a.only.split(',')] if a.only else list(range(n))
    with Pool(os.cpu_count()) as pool:
        for k, _ in enumerate(pool.imap_unordered(work, [(i, a.fps, frames) for i in idx], chunksize=2)):
            if k % 24 == 0:
                print(f'{k}/{len(idx)}', flush=True)
    if a.only:
        return
    video = out / 'intro_ni_un_ou.mp4'
    fade = TOTAL - 2.5
    subprocess.run([
        'ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(a.fps), '-i', str(frames / '%04d.png'),
        '-i', str(MUSIC), '-stream_loop', '-1', '-i', str(SEA),
        '-filter_complex',
        f'[0:v]fps=24[v];'                                  # (els fotogrames ja són de 1280×720)
        f'[1:a]volume=0.9[m];[2:a]volume=0.35[s];[m][s]amix=inputs=2:duration=first,'
        f'afade=t=in:d=1.5,afade=t=out:st={fade:.2f}:d=2.5,atrim=0:{TOTAL:.2f}[a]',
        '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-crf', '14', '-pix_fmt', 'yuv420p',
        '-c:a', 'aac', '-b:a', '192k', '-t', f'{TOTAL:.2f}', str(video)], check=True)
    print(video)


if __name__ == '__main__':
    main()
