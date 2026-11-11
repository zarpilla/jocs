"""
Cambra de ressonància (Iri), a 640×360: la composició de hd/rooms/fabrica_cambra.py ×4/3, dibuixada de nou.
Un racó de maó i ferro al fons de la sala de calderes. La cambra de vidre gruixut amb les bobines de ferro-9,
la consola (palanca, rellotges, el llum d'alarma) i la reixa del conducte de servei.
Llums: làmpada industrial sobre la consola, una altra sobre la pissarra, la lluïssor violeta de la cambra i el
foc de les calderes que entra per l'espiell de la porta.
A 640 hi ha més detall: maons amb gra i cantells picats, lloses amb esquerdes, cargols de dos píxels, les
escales dels rellotges, la placa del fabricant («ALDAIA · FERRO-9»), el rètol de la porta («CALDERES»),
l'avís de reglament amb títol i la pissarra amb la fórmula.

`bg(cv, alarm=True)` el fa servir el pròleg: làmpades apagades i el llum d'alarma encès (vegeu proleg_cambra).
"""
import math
from functools import lru_cache

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from hd.pix import (Canvas, Light, B4, W, H, hr as _hr, WALNUT, GOLD, COPPER, RUST, BRICK, IRON, FIRE, RED, PAPER,
                    MANILA, GRAY, WARN, SIL)
from hd.rooms.fabrica_cambra import STONE, FE9, FIELD, SLATE, CHALK, BULB, REDGL, GLASSD   # noqa: F401
from hd640.rooms.gavina_passadis import text, text_w

hr = lru_cache(maxsize=None)(_hr)     # (el soroll es repeteix a cada fotograma de l'animació: es desa)

FLOOR_Y = 205
LAMP1 = (179, 44)          # làmpada sobre la consola
LAMP2 = (573, 41)          # làmpada sobre la pissarra
CORE = (345, 112)          # centre de la cambra
BEACON = (136, 101)        # llum d'alarma de la consola
PIVOT = (222, 123)         # eix de la palanca
GRILLE = (447, 152, 524, 200)                 # reixa del conducte de servei
GLASS = (288, 403, 45, 184)                   # vidre de la cambra: x0, x1, y0, y1


class Baked:
    """Una llum calculada un sol cop per píxel i desada (les animacions redibuixen la sala moltes vegades)."""

    def __init__(self, light):
        self.light = light
        self.t = [None] * (W * H)

    def __call__(self, x, y):
        i = y * W + x
        v = self.t[i]
        if v is None:
            v = self.t[i] = self.light(x, y)
        return v


def make_light(alarm=False):
    lt = Light(vignette=(93, 53), floor_fade=(264, 45))
    if not alarm:
        lt.point(*LAMP1, r=200, k=2.5, squash=1.1, down=True)
        lt.point(*LAMP2, r=147, k=1.6, squash=1.1, down=True)
        lt.point(*CORE, r=147, k=1.3, squash=0.9)
        lt.point(43, 117, r=61, k=0.9)                                  # espiell de la porta
        lt.add(floor_pools)
    else:
        lt.ambient = -0.7
        lt.point(*BEACON, r=227, k=2.0, squash=1.0, power=1.5)
        lt.point(*CORE, r=107, k=0.6, squash=0.9)
    return lt


def floor_pools(x, y):
    """Taques de llum al terra sota les làmpades."""
    if y < 200:
        return 0.0
    v = 0.0
    for (lx, k, rx) in ((LAMP1[0], 1.8, 107), (LAMP2[0], 1.1, 75)):
        d = math.hypot((x - lx) / rx, (y - 224) / 29)
        if d < 1:
            v += (1 - d) ** 1.5 * k
    return v


LIGHT = Baked(make_light())


# ─── Ajudes ────────────────────────────────────────────────────────────────

def rivet(cv, x, y, base=2.6):
    """Rebló de 2×2: punt de llum a dalt a l'esquerra, ombra a baix a la dreta."""
    cv.put(x, y, IRON, base + 1.8)
    cv.put(x + 1, y, IRON, base + 0.6)
    cv.put(x, y + 1, IRON, base + 0.4)
    cv.put(x + 1, y + 1, IRON, base - 0.8)
    cv.put(x + 2, y + 2, IRON, base - 1.6)


def thick(cv, x0, y0, x1, y1, w, rp, lvl):
    """Barra gruixuda: lvl(s) amb s = -1..1 a través del gruix."""
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    dx, dy = (x1 - x0) / n, (y1 - y0) / n
    nx, ny = -dy, dx
    for i in range(int(n * 2) + 1):
        t = i / 2
        cx, cy = x0 + dx * t, y0 + dy * t
        for k in range(-w * 2, w * 2 + 1):
            s = k / (w * 2) if w else 0
            cv.put(round(cx + nx * k / 2), round(cy + ny * k / 2), rp, lvl(s))


def contact_shadow(cv, x0, x1, y0, depth, fall=11):
    for y in range(y0, y0 + depth):
        for x in range(x0 - fall, x1 + fall):
            a = (1 - (y - y0) / depth) * (1 - max(0, max(x0 - x, x - x1)) / fall)
            if a > B4[y & 3][x & 3] and 0 <= x < W and 0 <= y < H:
                o = cv.P[x, y]
                cv.P[x, y] = tuple(int(c * 0.55) for c in o[:3]) + (255,)


# ─── Fons ──────────────────────────────────────────────────────────────────

def bg(cv, alarm=False, t=0.0):
    """`t` (0..1): moment del cicle de l'animació de fons; amb t = 0 surt el fons quiet."""
    tt = t                                   # (dins la funció, `t` es fa servir per a altres coses)
    ph = 2 * math.pi * tt
    # ─── Sostre: biga de ferro reblonada i canonada de coure ─────────────────
    cv.rect(0, 0, W - 1, 4, IRON, lambda x, y: 0.4 + (0.3 if (x // 37) % 2 and y == 4 else 0))
    cv.rect(0, 5, W - 1, 12, IRON, lambda x, y: 2.0 + (0.7 if y == 5 else 0) - (y - 5) * 0.11
            + (hr(x // 3, y // 2, 31) - 0.5) * 0.2)
    cv.hline(0, W - 1, 13, IRON, 3.0)
    cv.hline(0, W - 1, 14, IRON, 1.6)
    cv.hline(0, W - 1, 15, IRON, 0.6)
    for x in range(8, W, 21):
        rivet(cv, x, 7, 2.2)
    # canonada de coure horitzontal
    for y in range(17, 24):
        cv.hline(0, W - 1, y, COPPER, [1.6, 2.8, 3.6, 3.2, 2.7, 2.0, 0.8][y - 17])
    for x in range(0, W):                                          # verdet i taques de la canonada
        if hr(x // 2, 17) > 0.93:
            cv.put(x, 21 + (x % 2), COPPER, 1.4)
    for x in range(40, W, 93):                                     # brides i abraçadores
        cv.rect(x, 16, x + 4, 24, COPPER, lambda xx, yy: 3.8 - (xx - x) * 0.55 - (0.6 if yy in (16, 24) else 0))
        cv.vline(x + 2, 13, 15, IRON, 1.6)
        cv.put(x + 1, 18, COPPER, 5.0); cv.put(x + 1, 22, COPPER, 4.4)          # cargols de la brida

    # ─── Paret de maó (24..193) ───────────────────────────────────────────────
    def brick(x, y):
        row = (y - 25) // 8
        v = (y - 25) % 8
        off = 9 if row % 2 else 0
        bx = (x + off) // 19
        u = (x + off) % 19
        if v == 7 or u == 18:
            return 0.7 + (0.3 if hr(x, y, 12) > 0.85 else 0)       # morter, amb grumolls
        lvl = 1.5 + (hr(bx, row, 3) - 0.5) * 0.7
        if v == 0:
            lvl += 0.4
        if v == 6 or u == 17:
            lvl -= 0.3
        if hr(bx, row, 7) > 0.85:                                  # maó socarrimat
            lvl -= 0.6
        if (u in (0, 17) and v in (0, 6)) and hr(bx, row, 9) > 0.6:  # cantells picats
            lvl = 0.9
        lvl += (hr(x, y, 13) - 0.5) * 0.35                          # gra del maó
        lvl -= max(0, 1 - (y - 25) / 29) * 1.3                       # sutge de sota la canonada
        return lvl

    cv.rect(0, 24, W - 1, 193, BRICK, brick)
    cv.hline(0, W - 1, 24, BRICK, 0.2)
    # sòcol de pedra
    cv.hline(0, W - 1, 194, STONE, 4.0)
    cv.hline(0, W - 1, 195, STONE, 3.3)
    cv.rect(0, 196, W - 1, 202, STONE, lambda x, y: 2.6 - (y - 196) * 0.15 + (hr(x // 29, 5) - 0.5) * 0.4
            + (hr(x // 2, y, 51) - 0.5) * 0.3 - (0.8 if x % 29 == 0 else 0))
    cv.hline(0, W - 1, 203, STONE, 1.2)
    cv.hline(0, W - 1, 204, STONE, 0.4)

    # ─── Terra de lloses de pedra en perspectiva ─────────────────────────────
    VPX, VPY = 320, -213
    for y in range(FLOOR_Y, H):
        dep = y - VPY
        t = 5067 / dep
        row = math.floor(t / 0.95)
        row_up = math.floor(5067 / (dep - 1) / 0.95)
        for x in range(W):
            u = (x - VPX) / dep * 10 + (0.5 if row % 2 else 0)
            col = math.floor(u)
            fr = (u - col) * dep / 10
            lvl = 2.0 + (hr(col, row, 1) - 0.5) * 0.6 + (hr(x // 3, y // 2, col) - 0.5) * 0.25
            if fr < 1 or row != row_up:
                lvl = 1.0
            elif fr < 2:
                lvl += 0.3
            elif hr(col, row, 4) > 0.75:                            # una esquerda en diagonal per la llosa
                frac = (t / 0.95) - row
                if abs((u - col) - (0.2 + frac * 0.6)) * dep / 10 < 0.6:
                    lvl = 1.2
            if y < 216:
                lvl -= (216 - y) / 11 * 1.2                         # ombra de contacte amb la paret
            cv.put(x, y, STONE, lvl)

    # ─── Porta cap a la sala de calderes (8..79 × 81..204) ───────────────────
    cv.rect(8, 81, 79, 204, IRON, lambda x, y: 2.4 + (0.9 if x in (8, 9) or y in (81, 82) else 0)
            - (1.2 if x in (78, 79) else 0))
    cv.rect(15, 88, 72, 204, IRON, 0.3)
    for x in range(11, 77, 8):
        rivet(cv, x, 84, 2.4)
    for y in range(91, 203, 9):
        rivet(cv, 11, y, 2.4)
        rivet(cv, 74, y, 2.0)

    def door(x, y):
        lvl = 2.0 + (0.9 if x == 16 else 0) - (1.0 if x == 71 else 0)
        if y in (133, 165):
            lvl += 0.9
        if y in (134, 166):
            lvl -= 1.0
        if (x - 16) % 55 in (4, 51) and (y - 92) % 11 == 0:
            lvl += 1.6
        if (x - 16) % 55 in (5, 52) and (y - 92) % 11 == 1:
            lvl -= 0.6
        return lvl + (hr(x // 3, y // 5, 61) - 0.5) * 0.3 + (hr(x, y, 63) - 0.5) * 0.15

    cv.rect(16, 89, 71, 204, IRON, door)
    # rovell a la part baixa
    for y in range(181, 205):
        for x in range(16, 72):
            if hr(x // 2, y // 2, 62) < (y - 181) / 32 - 0.1:
                cv.put(x, y, RUST, 1.6 + hr(x // 2, y // 2) * 0.6 + (hr(x, y, 64) - 0.5) * 0.5)
    # espiell amb barrots: el foc de les calderes
    cv.rect(28, 101, 59, 127, IRON, 0.6)
    for y in range(104, 125):
        for x in range(31, 57):
            f = 1 - abs(x - 44) / 19 + (y - 104) / 21 * 0.6 + (hr(x // 3, y // 4, 5) - 0.5) * 0.6
            if tt:                                                 # les flames es mouen darrere els barrots
                u = x * 0.34 + y * 0.26
                f += 0.28 * (math.sin(u - ph * 3 + y * 0.15) - math.sin(u + y * 0.15)) \
                    + 0.18 * (math.sin(x * 0.68 - ph * 4) - math.sin(x * 0.68))
            cv.put(x, y, FIRE, 1.4 + f * 2.2, 0)
    for x in (37, 44, 51):
        cv.vline(x - 1, 104, 124, IRON, 2.2, 0)
        cv.vline(x, 104, 124, IRON, 1.2, 0)
        cv.vline(x + 1, 104, 124, IRON, 0.4, 0)
    cv.hline(28, 59, 101, IRON, 3.6)
    cv.hline(29, 58, 102, IRON, 2.6)
    cv.hline(28, 59, 127, IRON, 0.8)
    cv.vline(28, 101, 127, IRON, 3.0)
    cv.glow(44, 117, 35, (255, 150, 70), 0.0 if alarm else 0.35 + 0.05 * math.sin(ph * 3) + 0.03 * math.sin(ph * 4 + 1) - 0.03 * math.sin(1))
    # maneta de palanca i pany
    cv.rect(59, 144, 63, 160, IRON, lambda x, y: 3.2 - (x - 59) * 0.4)
    cv.rect(51, 148, 65, 151, IRON, lambda x, y: 4.0 - (y - 148) * 0.9)
    cv.disc(49, 149.5, 2.7, 2.7, IRON, lambda nx, ny: 4.2 - nx - ny)
    cv.rect(60, 165, 62, 169, IRON, 0.2)                           # forat del pany
    cv.put(61, 170, IRON, 0.2)
    # frontisses
    for y in (99, 187):
        cv.rect(13, y, 20, y + 7, IRON, lambda x, yy: 3.4 - (yy - y) * 0.3)
        cv.hline(13, 20, y, IRON, 4.2)
        cv.put(16, y + 3, IRON, 1.0)
    # rètol esmaltat sobre la porta
    cv.rect(18, 66, 69, 78, PAPER, lambda x, y: 3.6 - (y - 66) * 0.1 + (hr(x, y, 65) - 0.5) * 0.2)
    cv.hline(18, 69, 66, IRON, 1.2); cv.hline(18, 69, 78, IRON, 0.8)
    cv.vline(18, 66, 78, IRON, 1.2); cv.vline(69, 66, 78, IRON, 0.8)
    s = 'CALDERES'
    text(cv, 44 - text_w(s) // 2, 69, s, IRON, 1.0, 0.6)
    for x, y in ((20, 68), (67, 68), (20, 76), (67, 76)):
        cv.put(x, y, IRON, 2.0)
    for x in range(19, 69):                                         # l'esmalt saltat a la vora de baix
        if hr(x, 66) > 0.82:
            cv.put(x, 77, IRON, 1.6)
    cv.darken(70, 67, 70, 79, 0.6)
    cv.darken(19, 79, 70, 79, 0.6)

    # ─── Pilars de ferro ─────────────────────────────────────────────────────
    PIL = [1.2, 3.6, 3.4, 3.0, 2.7, 2.5, 2.3, 2.1, 1.9, 1.7, 1.4, 0.9, 0.4]
    for px in (85, 597):
        cv.rect(px, 16, px + 12, 204, IRON, lambda x, y: PIL[x - px] + (hr(x, y // 3, 66) - 0.5) * 0.2)
        cv.rect(px - 3, 187, px + 15, 204, IRON, lambda x, y: 2.6 - (y - 187) * 0.08 - (x - px) * 0.06)
        cv.hline(px - 3, px + 15, 187, IRON, 3.8)
        cv.hline(px - 3, px + 15, 188, IRON, 3.0)
        cv.rect(px - 2, 24, px + 14, 27, IRON, lambda x, y: 3.2 - (y - 24) * 0.6)     # capitell
        for y in range(31, 184, 12):
            rivet(cv, px + 3, y, 2.6)
            rivet(cv, px + 8, y, 2.2)

    # ─── Avís de reglament, clavat al maó (103..121 × 83..109) ───────────────
    cv.rect(103, 83, 121, 109, PAPER, lambda x, y: 3.2 - (y - 83) * 0.03 + (hr(x, y, 3) - 0.5) * 0.3)
    cv.rect(103, 83, 121, 86, PAPER, 4.0)
    text(cv, 106, 88, 'AVIS', SIL, 1.4, 0.6, small=True)
    for y in range(95, 107, 2):
        for x in range(105, 120):
            if hr(x // 2, y, 4) > 0.3:
                cv.put(x, y, SIL, 2.2)
    cv.put(112, 82, GOLD, 4.0); cv.put(112, 83, GOLD, 2.4)                       # xinxeta
    for x, y in ((120, 108), (121, 107), (121, 108)):                            # cantonada doblegada
        cv.put(x, y, PAPER, 2.0)
    cv.darken(122, 84, 123, 110, 0.6)
    cv.darken(104, 110, 123, 111, 0.6)

    # ─── Consola (119..243 × 112..204) ───────────────────────────────────────
    CX0, CX1 = 119, 243
    contact_shadow(cv, CX0, CX1, FLOOR_Y, 12)
    # cos de fusta amb sòcol de ferro
    cv.rect(CX0, 139, CX1, 200, WALNUT, lambda x, y: 2.2 + (hr(x // 2, 7) - 0.5) * 0.3
            + (0.25 if (x + round(math.sin(y / 9 + x / 31) * 2)) % 7 == 0 else 0))   # veta de la fusta
    cv.vline(CX0, 139, 200, WALNUT, 3.6)
    cv.vline(CX0 + 1, 139, 200, WALNUT, 3.0)
    cv.vline(CX1, 139, 200, WALNUT, 0.8)
    cv.rect(CX0, 196, CX1, 204, IRON, lambda x, y: 1.8 - (y - 196) * 0.12)
    cv.hline(CX0, CX1, 196, IRON, 3.0)
    # tauler frontal de llautó negre amb rellotges
    cv.rect(CX0 + 5, 143, CX1 - 5, 187, IRON, lambda x, y: 1.4 + (hr(x // 4, y // 4, 8) - 0.5) * 0.15)
    cv.hline(CX0 + 5, CX1 - 5, 143, IRON, 0.4)
    cv.vline(CX0 + 5, 143, 187, IRON, 0.6)
    cv.hline(CX0 + 5, CX1 - 5, 187, IRON, 2.6)
    for x, y in ((CX0 + 8, 146), (CX1 - 9, 146), (CX0 + 8, 184), (CX1 - 9, 184)):
        cv.put(x, y, GOLD, 4.2); cv.put(x + 1, y, GOLD, 2.6); cv.put(x, y + 1, GOLD, 2.0)

    def gauge(cx, cy, r, ang):
        cv.disc(cx, cy, r + 2.1, r + 2.1, GOLD, lambda nx, ny: 3.4 - nx * 1.2 - ny * 1.2)
        cv.disc(cx, cy, r, r, PAPER, lambda nx, ny: 3.8 - ny * 0.8 - nx * 0.3)
        for a in range(200, 341, 14):                               # escala: marques grosses i fines
            big = (a - 200) % 28 == 0
            rr = r - 1
            cv.put(round(cx + math.cos(math.radians(a)) * rr), round(cy + math.sin(math.radians(a)) * rr), SIL, 1.0 if big else 2.0)
            if big:
                cv.put(round(cx + math.cos(math.radians(a)) * (rr - 1)), round(cy + math.sin(math.radians(a)) * (rr - 1)), SIL, 1.6)
        for a in range(312, 341, 4):                                # zona vermella
            cv.flat(round(cx + math.cos(math.radians(a)) * (r - 2)), round(cy + math.sin(math.radians(a)) * (r - 2)), (170, 40, 34))
        for i in range(int(r)):
            cv.flat(round(cx + math.cos(ang) * i), round(cy + math.sin(ang) * i), (150, 26, 24))
        cv.flat(round(cx), round(cy), (30, 24, 24))
        cv.flat(round(cx) + 1, round(cy), (60, 48, 44))
        cv.put(round(cx - r * 0.45), round(cy - r * 0.5), PAPER, 6, 0)
        cv.put(round(cx - r * 0.45) + 1, round(cy - r * 0.55), PAPER, 5.4, 0)

    # les agulles tremolen una mica (la cambra brunzeix)
    gauge(141, 160, 9.3, math.radians(-30 + 7 * math.sin(ph * 7) + 4 * math.sin(ph * 11)))
    gauge(168, 160, 9.3, math.radians(-120 + 6 * math.sin(ph * 5 + 1) - 6 * math.sin(1) + 4 * math.sin(ph * 13)))
    # fila de llums de senyal (vidres apagats; de tant en tant se n'encén algun)
    BLINK = ((0.10, 0.30), (0.40, 0.46), (0.58, 0.63), (0.70, 0.75), (0.84, 0.96))
    WHO = (0, 1, 2, 2, 3)
    for i, (rp, lv) in enumerate(((FE9, 2.0), (WARN, 1.4), (FE9, 2.0), (WARN, 1.4))):
        x = 189 + i * 11
        on = any(a <= tt < b and WHO[k] == i for k, (a, b) in enumerate(BLINK))
        cv.disc(x, 153, 2.9, 2.9, GOLD, lambda nx, ny: 3.4 - nx * 0.8 - ny * 0.8)
        if on:
            cv.glow(x, 153, 9, rp[-3], 0.55)
            cv.disc(x, 153, 1.9, 1.9, rp, lambda nx, ny: len(rp) - 2.4 - (nx * nx + ny * ny) * 1.2, 0)
            cv.flat(x - 1, 152, rp[-1])
        else:
            cv.disc(x, 153, 1.9, 1.9, rp, lambda nx, ny: lv + 1 - nx - ny)
    # interruptors de ganivet
    for i in range(3):
        x = 192 + i * 12
        cv.rect(x, 165, x + 5, 180, SIL, lambda xx, yy: 1.2 + (0.6 if xx == x else 0))
        cv.rect(x + 1, 168, x + 4, 169, COPPER, lambda xx, yy: 3.6 - (yy - 168) * 0.6)
        cv.rect(x + 1, 176, x + 4, 177, COPPER, lambda xx, yy: 3.2 - (yy - 176) * 0.6)
        tip = x + 3 + (3 if i != 1 else -1)
        cv.line(x + 2, 177, tip - 1, 165, COPPER, 4.0)
        cv.line(x + 3, 177, tip, 165, COPPER, 2.8)
        cv.put(tip - 1, 164, SIL, 3.4); cv.put(tip, 164, SIL, 2.6)
        cv.put(tip - 1, 163, SIL, 3.0)
    # reixeta de ventilació de la consola
    for x in range(129, 181, 4):
        cv.vline(x, 175, 183, IRON, 0.2)
        cv.vline(x + 1, 175, 183, IRON, 2.4)
        cv.vline(x + 2, 175, 183, IRON, 1.6)
    # placa de llautó del fabricant
    cv.rect(146, 188, 214, 195, GOLD, lambda x, y: 3.6 - (y - 188) * 0.25)
    cv.hline(146, 214, 188, GOLD, 4.6)
    cv.hline(146, 214, 195, GOLD, 1.4)
    s = 'ALDAIA · FERRO-9'
    text(cv, 180 - text_w(s, small=True) // 2, 189, s, GOLD, 0.6, 0, small=True)
    # sobre inclinat (112..139): on hi ha el botó i la palanca
    for y in range(117, 139):
        t = (y - 117) / 21
        xl, xr = CX0 + 4 - t * 4, CX1 - 4 + t * 4
        for x in range(round(xl), round(xr) + 1):
            edge = x <= xl + 1 or x >= xr - 1
            cv.put(x, y, WALNUT, (3.6 if edge else 2.6) + t * 0.5 - (1.2 if x >= xr - 1 else 0)
                   + (0.2 if (x + y // 5) % 9 == 0 else 0))
    cv.rect(CX0 + 11, 120, CX1 - 29, 135, IRON, lambda x, y: 1.8 + (y - 120) * 0.05 + (hr(x // 3, y // 2, 22) - 0.5) * 0.15)
    cv.hline(CX0 + 11, CX1 - 29, 120, IRON, 0.6)
    cv.hline(CX0 + 11, CX1 - 29, 135, IRON, 3.0)
    for x, y in ((CX0 + 13, 122), (CX1 - 32, 122), (CX0 + 13, 132), (CX1 - 32, 132)):
        rivet(cv, x, y, 2.0)
    cv.rect(CX0, 136, CX1, 139, WALNUT, lambda x, y: [4.4, 3.8, 2.6, 1.0][y - 136])
    # cables que surten de la consola cap a la cambra
    for i, (y0, lv) in enumerate(((171, 1.4), (179, 1.0), (187, 1.2))):
        pts = []
        for k in range(40):
            t = k / 39
            x = CX1 + t * (275 - CX1)
            y = y0 + t * (200 - y0) + math.sin(t * math.pi) * (21 - i * 4)
            pts.append((x, y))
        for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
            cv.line(round(xa), round(ya), round(xb), round(yb), GRAY, lv + 0.6)
            cv.line(round(xa), round(ya) + 1, round(xb), round(yb) + 1, SIL, lv + 0.8)
            cv.line(round(xa), round(ya) + 2, round(xb), round(yb) + 2, SIL, lv)
            cv.line(round(xa), round(ya) + 3, round(xb), round(yb) + 3, SIL, 0.2)

    # ─── Base de la palanca (203..241 × 72..125): quadrant dentat i ranura ───
    # (el braç és un prop: palanca_alcada / palanca_baixada)
    qx, qy = PIVOT
    cv.disc(qx, qy, 14.7, 6.7, IRON, lambda nx, ny: 2.6 - ny * 1.2 - nx * 0.4)       # quadrant
    for a in range(200, 341, 10):
        big = (a - 200) % 20 == 0
        cv.put(round(qx + math.cos(math.radians(a)) * 13.3), round(qy + math.sin(math.radians(a)) * 6), GOLD, 3.8 if big else 2.6)
    cv.rect(qx - 5, 121, qx + 6, 129, IRON, lambda x, y: 2.8 - (x - qx + 5) * 0.2)
    cv.hline(qx - 5, qx + 6, 121, IRON, 4.0)
    cv.hline(qx - 2, qx + 5, 124, IRON, 0.2)                                       # ranura per on corre el braç
    cv.hline(qx - 2, qx + 5, 125, IRON, 1.0)
    cv.disc(qx, qy, 2.7, 2.7, GOLD, lambda nx, ny: 4.4 - nx - ny)                  # eix

    # ─── Llum d'alarma de la consola (gàbia amb vidre vermell) ───────────────
    bx, by = BEACON
    cv.rect(bx - 8, by + 12, bx + 8, by + 16, IRON, lambda x, y: 3.0 - (y - by - 12) * 0.5)
    cv.rect(bx - 3, by + 16, bx + 3, by + 17, IRON, 1.2)
    if alarm:
        cv.disc(bx, by + 4, 6.7, 9.3, REDGL, lambda nx, ny: 5.6 - (nx * nx + ny * ny) * 2.4 - ny * 0.6, 0)
    else:
        cv.disc(bx, by + 4, 6.7, 9.3, REDGL, lambda nx, ny: 2.6 - nx * 1.2 - ny * 0.8)
        cv.put(bx - 3, by - 1, REDGL, 5.0)
        cv.put(bx - 3, by, REDGL, 4.4)
    for k in (-5, 0, 5):                                                         # gàbia
        cv.line(bx + k, by - 4 + abs(k) // 2, bx + k, by + 12, IRON, 3.4 if k < 0 else 2.0)
    cv.hline(bx - 7, bx + 7, by + 4, IRON, 2.4)
    cv.disc(bx, by - 5, 2.7, 1.9, IRON, lambda nx, ny: 3.4 - ny)
    # campana de l'alarma (a la paret, sobre la consola)
    cv.disc(155, 91, 8.7, 8.7, GOLD, lambda nx, ny: 3.2 - nx * 1.2 - ny * 1.2)      # gong de la campana
    cv.ring(155, 91, 6, GOLD, 4.6, step=4)
    cv.ring(155, 91, 8.7, GOLD, 1.2, step=3)
    cv.put(151, 86, GOLD, 6.0); cv.put(152, 85, GOLD, 5.4)
    cv.disc(155, 91, 2, 2, IRON, 3.0)
    cv.rect(149, 101, 160, 108, IRON, lambda x, y: 3.0 - (x - 149) * 0.15 - (y - 101) * 0.15)   # caixa del timbre
    cv.hline(149, 160, 101, IRON, 4.0)
    cv.line(159, 101, 163, 93, IRON, 3.0)                                         # martell
    cv.line(160, 101, 164, 93, IRON, 1.6)
    cv.disc(163.3, 92.7, 1.7, 1.7, IRON, 3.6)
    cv.line(155, 108, 155, 117, SIL, 1.2)                                         # cable de la campana

    # ─── Cables que pugen de la cambra al sostre ─────────────────────────────
    for x, lv in ((296, 1.4), (301, 1.0), (389, 1.4), (395, 1.0)):
        cv.vline(x, 25, 29, SIL, lv)
        cv.vline(x + 1, 25, 29, SIL, lv + 0.8)

    # ─── Cambra de ressonància (265..425 × 17..215) ──────────────────────────
    PX0, PX1 = 265, 425
    contact_shadow(cv, PX0, PX1, FLOOR_Y + 8, 9)
    # plataforma de ferro amb franges de perill
    cv.rect(PX0, 188, PX1, 213, IRON, lambda x, y: 2.0 - (y - 188) * 0.04)
    cv.hline(PX0, PX1, 188, IRON, 4.2)
    cv.hline(PX0, PX1, 189, IRON, 3.2)
    cv.vline(PX0, 188, 213, IRON, 3.0)
    cv.vline(PX1, 188, 213, IRON, 0.8)
    for y in range(195, 201):
        for x in range(PX0 + 4, PX1 - 3):
            yel = ((x + y) // 7) % 2 == 0
            cv.put(x, y, WARN if yel else SIL, (2.6 if yel else 1.0) - (hr(x, y, 4) > 0.9) * 1.0
                   - (0.5 if yel and hr(x // 3, y // 2, 8) > 0.85 else 0))
    cv.hline(PX0 + 4, PX1 - 4, 194, IRON, 0.6)
    cv.hline(PX0 + 4, PX1 - 4, 201, IRON, 3.0)
    for x in range(PX0 + 5, PX1 - 2, 16):
        rivet(cv, x, 206, 2.0)
    cv.hline(PX0, PX1, 213, IRON, 0.3)
    # graó davant
    cv.rect(301, 208, 389, 215, IRON, lambda x, y: 3.2 - (y - 208) * 0.3)
    cv.hline(301, 389, 208, IRON, 4.4)
    for x in range(304, 389, 4):
        cv.put(x, 211, IRON, 1.4)
        cv.put(x + 1, 212, IRON, 1.4)

    # interior: fons fosc de la cambra, il·luminat pel camp
    GX0, GX1, GY0, GY1 = GLASS
    dim = 1 if alarm else 0                                      # el camp, de nit, és més apagat
    for y in range(GY0, GY1 + 1):
        for x in range(GX0, GX1 + 1):
            d = math.hypot(x - CORE[0], (y - CORE[1]) * 0.7) / 93
            lvl = 4.2 - d * 3.2 - dim
            for k, gx in enumerate((330, 360.7)):                    # fils d'energia entre bobines (ondulen)
                w = gx + math.sin(y / 6.67 + gx - ph * (2 + k)) * (2.9 + 0.67 * math.sin(ph * (1 + 2 * k) + gx)
                                                                     - 0.67 * math.sin(gx))
                if abs(x - w) < 1.0 and 69 < y < 165:
                    lvl += 1.8
                elif abs(x - w) < 4:
                    lvl += 0.75 * (1 - abs(x - w) / 4) + 0.15
            cv.put(x, y, FIELD, lvl, 0)
    # anells de llautó que aguanten les bobines
    for yy in (61, 168):
        cv.rect(GX0 + 3, yy, GX1 - 3, yy + 4, GOLD, lambda x, y: 3.4 - (y - yy) * 0.5 - abs(x - CORE[0]) / 80, 0.4)
        for x in range(GX0 + 8, GX1 - 4, 12):
            cv.put(x, yy + 2, GOLD, 5.2, 0.3)
    # tres bobines: nucli de ferro-9 enrotllat amb fil de coure
    for cx in (315, 345, 376):
        for y in range(67, 168):
            for x in range(cx - 8, cx + 9):
                s = (x - cx) / 8.7
                band = (y - 67) % 17
                if band in (14, 15, 16):                             # espai entre enrotllaments: el ferro-9 nu
                    if abs(s) < 0.6:
                        cv.put(x, y, FE9, 5.0 - s * 2.4 - (1.2 if band == 16 else 0), 0.3)
                    continue
                if abs(s) > 0.9 and (x - cx) * (CORE[0] - cx) > 0 and band not in (0, 13):            # vora encesa pel camp
                    cv.put(x, y, FIELD, 5.5 - dim, 0)
                    continue
                lv = 3.2 - s * 1.4 - s * s * 1.4 + (y % 2) * 0.5 - (1.0 if band in (0, 13) else 0)
                cv.put(x, y, COPPER, round(lv - dim) + 0.5, 0)
        # caps de ferro-9 polit
        for yy in (65, 167):
            cv.rect(cx - 9, yy, cx + 9, yy + 2, FE9, lambda x, y: 5.4 - (x - cx) / 5.3 - (y - yy) * 0.3, 0.3)
        for x, lv in ((cx - 1, 5.6), (cx, 4.6), (cx + 1, 3.6)):
            cv.vline(x, 56, 64, FE9, lv, 0.3)
            cv.vline(x, 170, 181, FE9, lv - 1.0, 0.3)
    # el camp: lluïssor entre les bobines
    for k, cx in enumerate((329, 361)):
        breath = 0.07 * (math.sin(ph * (1 + k) + k * 2) - math.sin(k * 2))       # el camp respira
        cv.glow(cx, 117, 24, (190, 160, 255), 0.0 if alarm else 0.45 + breath)
    cv.glow(CORE[0], CORE[1], 80, (150, 110, 240), 0.22 if alarm else 0.4)
    # petits arcs entre les bobines, de tant en tant (un parell de fotogrames cadascun)
    for (a, b, x0, y0, x1, seed) in ARCS:
        if a <= tt < b:
            n = abs(x1 - x0)
            pts = [(x0 + (x1 - x0) * i / n, y0 + (hr(i // 2, seed, int(tt * 97)) - 0.5) * 9 * math.sin(math.pi * i / n))
                   for i in range(n + 1)]
            for (xa, ya) in pts:
                cv.glow(xa, ya, 4, (200, 180, 255), 0.5)
            for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
                cv.line(round(xa), round(ya), round(xb), round(yb), FIELD, 7.0, 0)
    # el vidre: lleuger tint fred i reflexos en diagonal
    cv.tint(GX0, GY0, GX1, GY1, (170, 200, 230), 0.06)

    def streak(x, y):
        u = x - GX0 + (y - GY0) * 0.55
        return 0.32 if 11 <= u <= 19 else (0.2 if 24 <= u <= 25 else (0.16 if 93 <= u <= 101 else 0.0))

    cv.tint(GX0, GY0, GX1, GY1, (230, 244, 255), streak)
    cv.vline(GX0 + 1, GY0 + 2, GY1 - 2, PAPER, 4.4, 0)                          # cantell gruixut del vidre
    cv.vline(GX0 + 2, GY0 + 2, GY1 - 2, FE9, 4.0, 0)
    cv.vline(GX0 + 3, GY0 + 2, GY1 - 2, FE9, 3.0, 0)
    cv.hline(GX0 + 1, GX1 - 1, GY1 - 1, FE9, 3.4, 0)
    # muntants laterals (guies del vidre que baixa)
    MUN = [1.0, 3.8, 3.5, 3.2, 3.0, 2.8, 2.6, 2.5, 2.4, 2.2, 2.0, 1.9, 1.8, 1.6, 1.4, 1.0, 0.4]
    for x0, lit in ((271, True), (404, False)):
        cv.rect(x0, 35, x0 + 16, 187, IRON, lambda x, y: MUN[x - x0] - (0 if lit else 0.5)
                + (hr(x // 2, y // 3, 67) - 0.5) * 0.2)
        gx_ = x0 + 15 if lit else x0 + 1
        cv.vline(gx_, 45, 184, GOLD, 3.4)                                         # ranura de llautó
        cv.vline(gx_ + (-1 if lit else 1), 45, 184, GOLD, 1.8)
        for y in range(43, 184, 13):
            rivet(cv, x0 + 4, y, 2.4)
            rivet(cv, x0 + 10, y, 2.0)
    # caixa superior on s'amaga el vidre, amb aïlladors
    cv.rect(265, 27, 425, 44, IRON, lambda x, y: 2.6 - (y - 27) * 0.06 + (hr(x // 4, y // 3, 68) - 0.5) * 0.15)
    cv.hline(265, 425, 27, IRON, 4.2)
    cv.hline(265, 425, 28, IRON, 3.4)
    cv.hline(265, 425, 44, IRON, 0.4)
    cv.rect(312, 31, 379, 40, GOLD, lambda x, y: 3.2 - (y - 31) * 0.2)          # placa
    cv.hline(312, 379, 31, GOLD, 4.6)
    cv.hline(312, 379, 40, GOLD, 1.6)
    s = 'RESSONÀNCIA'
    text(cv, 346 - text_w(s) // 2, 33, s, GOLD, 0.6, 0)
    for x in range(271, 424, 11):
        rivet(cv, x, 41, 2.0)
    for ix in (280, 296, 395, 411):                                              # aïlladors de porcellana
        for j in range(3):
            cv.disc(ix, 23 - j * 3, 3.5 - j * 0.4, 1.3, PAPER, lambda nx, ny: 3.6 - nx * 1.2 - ny * 0.6, 0.8)
        cv.vline(ix, 15, 17, COPPER, 3.0)
    # llengua de vidre a la ranura de dalt
    cv.hline(GX0, GX1, GY0 - 1, FE9, 1.4)
    # lluïssor violeta del camp sobre el que hi ha al voltant
    if not alarm:
        cv.glow(CORE[0], 160, 120, (120, 90, 220), 0.16)
        cv.glow(CORE[0], 211, 80, (150, 120, 240), 0.12)
        cv.tint(200, 215, 493, 273, (150, 120, 240),
                lambda x, y: 0.28 * max(0.0, 1 - math.hypot((x - CORE[0]) / 133, (y - 217) / 35)) ** 1.2)

    # ─── Reixa del conducte de servei (447..524 × 152..200) ──────────────────
    RX0, RY0, RX1, RY1 = GRILLE
    cv.rect(RX0, RY0, RX1, RY1, IRON, lambda x, y: 2.8 - (y - RY0) * 0.015)
    cv.hline(RX0, RX1, RY0, IRON, 4.0)
    cv.vline(RX0, RY0, RY1, IRON, 3.6)
    cv.hline(RX0, RX1, RY1, IRON, 0.8)
    cv.vline(RX1, RY0, RY1, IRON, 1.0)
    cv.rect(RX0 + 5, RY0 + 5, RX1 - 5, RY1 - 5, SIL, lambda x, y: 0.4 + max(0, 1 - abs(x - 485) / 40) * 0.6)  # conducte fosc
    for y in range(RY0 + 7, RY1 - 5, 5):                                         # lamel·les
        cv.hline(RX0 + 5, RX1 - 5, y, IRON, 3.4)
        cv.hline(RX0 + 5, RX1 - 5, y + 1, IRON, 2.6)
        cv.hline(RX0 + 5, RX1 - 5, y + 2, IRON, 1.6)
        cv.hline(RX0 + 5, RX1 - 5, y + 3, IRON, 0.6)
    for x, lv in ((485, 2.6), (486, 1.8), (487, 1.0)):                           # travesser
        cv.vline(x, RY0 + 5, RY1 - 5, IRON, lv)
    for x, y in ((RX0 + 3, RY0 + 3), (RX1 - 3, RY0 + 3), (RX0 + 3, RY1 - 3), (RX1 - 3, RY1 - 3)):
        cv.disc(x, y, 2.4, 2.4, IRON, lambda nx, ny: 4.6 - nx * 1.2 - ny * 1.2)   # cargols d'acer nous
        cv.put(x - 1, y, IRON, 1.0); cv.put(x, y, IRON, 1.0); cv.put(x + 1, y, IRON, 1.0)   # la ranura
    contact_shadow(cv, RX0, RX1, FLOOR_Y, 5, fall=4)

    # ─── Canonada vertical amb vàlvula i manòmetre (539..547) ────────────────
    PIPE = [1.4, 2.6, 3.4, 3.9, 3.5, 3.0, 2.3, 1.5, 0.6]
    for y in range(24, 205):
        for x in range(539, 548):
            cv.put(x, y, COPPER, PIPE[x - 539] - (0.8 if hr(x // 2, y // 3, 69) > 0.94 else 0))
    cv.rect(536, 23, 550, 27, COPPER, lambda x, y: 3.0 - (y - 23) * 0.2)
    for y in (61, 160):
        cv.rect(536, y, 550, y + 3, COPPER, lambda x, yy: 3.6 - (yy - y) * 0.7)
        cv.put(537, y + 1, COPPER, 5.0); cv.put(549, y + 1, COPPER, 3.0)
    cv.rect(533, 197, 552, 204, IRON, lambda x, y: 2.4 - (y - 197) * 0.25)
    cv.hline(533, 552, 197, IRON, 3.6)
    cv.ring(543, 128, 9.3, IRON, 3.0, step=3)                                    # volant de la vàlvula
    cv.ring(543, 128, 8, IRON, 1.8, step=3)
    for a in (0, 90, 180, 270):
        ca, sa = math.cos(math.radians(a + 45)), math.sin(math.radians(a + 45))
        cv.line(543, 128, 543 + round(ca * 8), 128 + round(sa * 8), IRON, 2.6)
    cv.disc(543, 128, 2.1, 2.1, RED, lambda nx, ny: 3.6 - nx - ny)
    cv.disc(559, 96, 7.5, 7.5, GOLD, lambda nx, ny: 3.4 - nx - ny)              # manòmetre
    cv.disc(559, 96, 5.6, 5.6, PAPER, lambda nx, ny: 3.8 - ny * 0.6)
    for a in range(200, 341, 35):
        cv.put(round(559 + math.cos(math.radians(a)) * 4.6), round(96 + math.sin(math.radians(a)) * 4.6), SIL, 1.4)
    na = math.radians(-34 + 9 * math.sin(ph * 9 + 2) - 9 * math.sin(2) + 5 * math.sin(ph * 2))   # l'agulla tremola
    cv.line(559, 96, round(559 + math.cos(na) * 4.8), round(96 + math.sin(na) * 4.8), RED, 2.6)
    cv.hline(548, 552, 96, COPPER, 3.0)
    cv.hline(548, 552, 97, COPPER, 1.6)
    # rètol de perill sobre la reixa
    cv.rect(461, 96, 509, 123, WARN, lambda x, y: 3.2 - (y - 96) * 0.03 + (hr(x, y, 70) - 0.5) * 0.2)
    for x in range(461, 510):
        for y in (96, 97, 98, 121, 122, 123):
            if ((x + y) // 4) % 2 == 0:
                cv.put(x, y, SIL, 0.6)
    cv.poly([(485, 101), (479, 111), (484, 111), (481, 119), (492, 107), (487, 107), (489, 101)], SIL, 0.4)   # llamp
    for x, y in ((463, 100), (507, 100), (463, 118), (507, 118)):
        cv.put(x, y, IRON, 1.6)
    cv.darken(462, 124, 511, 125, 0.5)
    cv.darken(510, 97, 511, 125, 0.5)

    # ─── Pissarra amb càlculs de ressonància (559..596 × 57..154) ────────────
    QX0, QY0, QX1, QY1 = 563, 61, 592, 149
    cv.rect(QX0 - 4, QY0 - 4, QX1 + 4, QY1 + 4, WALNUT, lambda x, y: 3.2 - (1.6 if x > QX1 or y > QY1 else 0)
            + (0.5 if x == QX0 - 4 or y == QY0 - 4 else 0))
    cv.rect(QX0, QY0, QX1, QY1, SLATE, lambda x, y: 1.6 + (hr(x // 2, y // 3, 6) - 0.5) * 0.5
            + (0.4 if hr(x // 6, y // 4, 71) > 0.85 else 0))         # restes de guix mal esborrat
    for i in range(3):                                                           # ones
        yb = 75 + i * 21
        for x in range(QX0 + 3, QX1 - 1):
            y = yb + round(math.sin((x - QX0) / (2.9 + i * 1.33)) * (4 - i * 0.8))
            cv.put(x, y, CHALK, 2.0 - i * 0.3, 0.5)
    text(cv, QX0 + 3, 129, 'FE-9', CHALK, 2.0, 0.5)
    for y in range(139, 147, 4):
        for x in range(QX0 + 3, QX1 - 2):
            if hr(x // 2, y, 7) > 0.35:
                cv.put(x, y, CHALK, 1.4, 0.5)
    cv.rect(QX0 - 5, QY1 + 4, QX1 + 5, QY1 + 7, WALNUT, lambda x, y: 3.8 - (y - QY1 - 4))
    cv.rect(571, QY1 + 2, 575, QY1 + 3, CHALK, lambda x, y: 3.0 - (y - QY1 - 2) * 0.6)

    # ─── Galleda de sorra contra el foc (dreta) ─────────────────────────────
    contact_shadow(cv, 616, 635, 213, 5, fall=4)
    for y in range(187, 216):
        t = (y - 187) / 28
        xl, xr = 616 + t * 2, 635 - t * 2
        for x in range(round(xl), round(xr) + 1):
            s = (x - (xl + xr) / 2) / ((xr - xl) / 2)
            cv.put(x, y, RED, 3.4 - s * 1.6 - s * s - (0.6 if hr(x, y // 2, 72) > 0.92 else 0))
    cv.disc(625.5, 187, 10, 2.1, MANILA, lambda nx, ny: 2.2 + (hr(round(nx * 9), round(ny * 3), 73) - 0.5) * 0.6)
    cv.hline(615, 636, 186, RED, 4.2)
    for y in (195, 208):
        cv.hline(round(616 + (y - 187) / 28 * 2), round(635 - (y - 187) / 28 * 2), y, RED, 1.6)

    # ─── Làmpades industrials penjades ───────────────────────────────────────
    for (lx, ly) in (LAMP1, LAMP2):
        cv.vline(lx, 24, ly - 8, SIL, 1.0)
        cv.vline(lx + 1, 24, ly - 8, SIL, 0.4)
        for y in range(ly - 8, ly + 1):
            t = (y - ly + 8) / 8
            half = 2.7 + t * 12
            for x in range(round(lx - half), round(lx + half) + 1):
                u = (x - lx) / half
                cv.put(x, y, GRAY if not alarm else IRON, 3.6 - u * 1.4 - (1 - t) * 0.8)
        cv.hline(lx - 15, lx + 15, ly + 1, GRAY, 1.0)
        cv.rect(lx - 3, ly - 11, lx + 3, ly - 8, IRON, lambda x, y: 2.4 - (x - lx) * 0.2)
        if not alarm:
            cv.disc(lx, ly + 3, 4, 2.4, BULB, 0, 0)
            cv.glow(lx, ly + 4, 40, (255, 220, 150), 0.5)
        else:
            cv.disc(lx, ly + 3, 4, 2.4, GLASSD, lambda nx, ny: 1.0 - nx, 0)

    # ─── Retoc: escalfor de les làmpades i frescor del camp ──────────────────
    if not alarm:
        cv.tint(0, 0, W - 1, H - 1, (255, 200, 130),
                lambda x, y: 0.10 * max(0.0, 1 - math.hypot(x - LAMP1[0], (y - LAMP1[1]) * 1.1) / 160))


# arcs del camp: (des de t, fins a t, x d'una bobina, y, x de l'altra, llavor)
ARCS = ((0.22, 0.30, 323, 93, 337, 1), (0.52, 0.57, 353, 139, 368, 2), (0.79, 0.86, 323, 128, 337, 3),
        (0.90, 0.94, 353, 83, 368, 4))


# ─── Props ─────────────────────────────────────────────────────────────────

def boto(cv):
    """El botó vermell de sincronia, encès, amb la placa «SINCRONIA» (152..187 × 112..139)."""
    cv.rect(155, 119, 184, 135, IRON, lambda x, y: 2.2 + (y - 119) * 0.03)
    cv.hline(155, 184, 119, IRON, 3.8)
    cv.vline(155, 119, 135, IRON, 3.2)
    cv.hline(155, 184, 135, IRON, 0.6)
    cv.vline(184, 119, 135, IRON, 0.8)
    for x, y in ((157, 121), (182, 121)):
        cv.put(x, y, IRON, 4.4)
    # placa de llautó amb el rètol
    cv.rect(157, 130, 182, 133, GOLD, lambda x, y: 3.8 - (y - 130) * 0.45)
    for x in range(159, 181):
        if (x - 159) % 3 != 2 and hr(x, 3) > 0.15:
            cv.put(x, 131, GOLD, 1.0)
            cv.put(x, 132, GOLD, 1.2 if hr(x, 4) > 0.4 else 2.4)
    # bisell i bolet vermell
    cv.disc(169, 123.3, 8.3, 4.8, GOLD, lambda nx, ny: 4.2 - nx * 1.4 - ny * 1.4)
    cv.disc(169, 123.3, 6.7, 3.7, IRON, 0.6)
    cv.disc(169, 120.7, 5.9, 4.3, REDGL, lambda nx, ny: 5.2 - (nx * nx + ny * ny) * 1.6 - ny * 1.0 - nx * 0.6, 0)
    for x, y in ((166, 118), (167, 118), (166, 119)):
        cv.put(x, y, REDGL, 6.0, 0)
    cv.glow(169, 121, 21, (255, 70, 50), 0.6)


def lever(cv, ang, arm=39):
    """Braç de la palanca amb mànec de fusta; ang en graus des de la vertical (+ cap a la dreta)."""
    px, py = PIVOT[0] + 0.5, PIVOT[1]
    ux, uy = math.sin(math.radians(ang)), -math.cos(math.radians(ang))
    nx, ny = -uy, ux                                                              # normal (cap a la dreta del braç)
    tx, ty = px + ux * arm, py + uy * arm
    cv.poly([(px - nx * 3.5, py - ny * 3.5), (px + nx * 3.5, py + ny * 3.5),
             (tx + nx * 2.7, ty + ny * 2.7), (tx - nx * 2.7, ty - ny * 2.7)], IRON,
            lambda x, y: 4.6 - (((x - px) * nx + (y - py) * ny) / 3.1 + 1) * 2.1)
    # mànec de fusta, amb una virola de llautó
    hx, hy = tx + ux * 9, ty + uy * 9
    thick(cv, round(tx), round(ty), round(hx), round(hy), 3, WALNUT, lambda s: 4.4 - s * 2.2)
    thick(cv, round(tx), round(ty), round(tx + ux), round(ty + uy), 3, GOLD, lambda s: 4.2 - s * 2.0)
    cv.disc(hx + ux * 0.7, hy + uy * 0.7, 3.5, 3.2, WALNUT, lambda a, b: 4.6 - a - b)
    cv.disc(PIVOT[0], PIVOT[1], 2.7, 2.7, GOLD, lambda a, b: 4.4 - a - b)        # eix, per sobre del braç


def palanca_alcada(cv):
    """La palanca alçada: l'alarma encara funciona."""
    lever(cv, 11.7)


def palanca_baixada(cv):
    """La palanca abatuda contra el tope esquerre del quadrant."""
    lever(cv, -52, arm=28)
    # el tope de goma que l'atura
    cv.disc(208, 119, 2.1, 1.9, IRON, lambda a, b: 1.6 - a - b)


def reixa_llimada(cv):
    """Els cargols de la reixa, llimats (llueixen), i una ratlla de llima al marc."""
    RX0, RY0, RX1, RY1 = GRILLE
    for x, y in ((RX0 + 3, RY0 + 3), (RX1 - 3, RY0 + 3), (RX0 + 3, RY1 - 3), (RX1 - 3, RY1 - 3)):
        cv.disc(x, y, 2.4, 2.4, IRON, lambda nx, ny: 7.0 - nx - ny, 0.3)
        cv.flat(x, y, (255, 250, 226))
        cv.flat(x - 1, y - 1, (255, 250, 226))
        for dx, dy in ((-3, 0), (3, 0), (0, -3), (0, 3), (-2, -2), (2, 2)):
            cv.put(x + dx, y + dy, IRON, 6.0, 0.3)                       # llimadures brillants al voltant
    for x in range(RX0 + 8, RX1 - 8):                                      # ratlles de llima al marc
        if hr(x, 5) > 0.35:
            cv.put(x, RY1 - 1, IRON, 6.4, 0.3)
            if hr(x, 6) > 0.6:
                cv.put(x, RY1, IRON, 5.6, 0.3)
    for x in range(RX0 + 1, RX0 + 5):
        cv.put(x, RY1 + 4, IRON, 5.6, 0.3)
    # llimadures a terra
    for i in range(20):
        x = RX0 + 3 + int(hr(i, 8) * (RX1 - RX0 - 6))
        y = 207 + int(hr(i, 9) * 5)
        cv.put(x, y, IRON, 5.4 + hr(i, 1), 0.3)


PROPS = {'boto': boto, 'reixa_llimada': reixa_llimada,
         'palanca_alcada': palanca_alcada, 'palanca_baixada': palanca_baixada}


# Animació de fons: el camp violeta ondula i fa petits arcs, les llums de senyal parpellegen, el foc es
# mou darrere l'espiell i les agulles tremolen. Cada fotograma porta només el que canvia respecte del
# fons quiet (t = 0).
def frame_diff(base, img):
    """Imatge transparent amb només els píxels d'`img` que no són iguals a `base`."""
    from PIL import Image, ImageChops
    d = ImageChops.difference(base.convert('RGB'), img.convert('RGB')).convert('L').point(lambda v: 255 if v else 0)
    out = Image.new('RGBA', img.size, (0, 0, 0, 0))
    out.paste(img, (0, 0), d)
    return out


@lru_cache(maxsize=None)
def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv.img


def _ambient_frames(n=24):
    base = _base()
    frames = []
    for i in range(n):
        cv = Canvas(light=LIGHT)
        bg(cv, t=i / n)
        frames.append(frame_diff(base, cv.img))
    return frames


ANIMS = {'ambient': {'frames': _ambient_frames, 'frameDuration': 120}}
