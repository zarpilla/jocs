"""
Aigua Verne — `aqua_port` (L), Escena 3: el port d'Aqua, un planeta que era mar.

Som dalt del moll de pedra, blanc de sal. Davant, on hi havia l'aigua del port, ara hi ha un forat de quaranta
metres: a l'altra banda de la dàrsena, l'escullera (la paret alta, amb les marques de l'aigua de cada any, més
avall cada vegada) i l'**escala del port**, que baixa i s'acaba a l'aire. Al fons de la dàrsena, una barca de
pesca encallada i inclinada. Per la bocana es veu el mar sec fins a l'horitzó: una plana de sal amb vaixells
encallats, una illa que ara és una muntanya, i la **Canonada d'Aqua**, una columna blanca fins al cel.
Al moll: la **grua** vella amb la **cistella** de peix penjada sobre el buit, norais, caixes de peix buides, un
rètol que diu PROHIBIT BANYAR-SE, i el **panell del preu**. A l'esquerra, la Cantimplora aparcada (la rampa).

Llum freda de migdia: el sol gairebé a plom, ombres curtes a sota de les coses.
Decorat: `grua_arreglada` (llum verd a la cabina). ANIMS: `calitja` (l'horitzó tremola), `pols` (pols de sal),
`llum_canonada` (el llum vermell del cim).
"""
import math

import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

from hd.pix import Canvas, Light, W, H, hr, mix
from hd.rooms.comu import text
from hd.rooms.exterior import fbm, smooth
from hd640.rooms.aqua_comu import (RH, SKYA, SALT, SAND, STONEA, ALGA, WOODG, TEALH, REDF, PAINTW, RUSTA, OCHRE,
                                   OLIVEN, ORANGEN, STEELA, BLACKT, GLASSD, ROPEA, WICKER, BLUEV, COL, BONE,
                                   cel, plana, canonada, canonada_llum, panell, gota, shade, to_screen,
                                   calitja_frames, pols_frames, diff)

# Art a 2× (1280×720 per a una sala de 640×360): el mateix dibuix, amb les formes, el dither i la llum a la
# resolució real (hd1280/canvas2x.py); el motor el mostra a 1/2 (artScale al .room.json).
ART_SCALE = 2
from hd1280.canvas2x import Canvas2x as Canvas  # noqa: E402,F811
from hd.pix import Canvas as Canvas1x  # noqa: E402,F401  (llenços auxiliars en píxels de sala: figures, textos)

HOR = 110                 # l'horitzó
EDGE = 196                # la vora del moll (la pedra de coronament, de 196 a 202)
FLOOR = 202               # el terra del moll
CAN_X, CAN_LY = 430, 20   # la Canonada i el seu llum
WALL_X0 = 334             # on comença l'escullera (el far)
CRANE_TIP = (330, 12)     # la punta de la ploma de la grua
BASKET = (316, 162, 350, 192)

WETST = [mix(a, b, 0.45) for a, b in zip([(36, 40, 48), (56, 60, 68), (80, 84, 90), (106, 108, 112), (132, 134, 136),
                                          (158, 158, 158), (182, 182, 178), (204, 204, 198)],
                                         [(26, 32, 30), (36, 44, 40), (50, 60, 52), (66, 76, 62), (82, 92, 74),
                                          (100, 108, 88), (120, 126, 104), (140, 144, 120)])]
QUAY = [(46, 46, 50), (70, 70, 72), (96, 94, 92), (122, 120, 114), (148, 144, 136), (172, 168, 158),
        (194, 190, 178), (214, 210, 198), (230, 228, 218), (244, 243, 236)]

LIGHT = Light(ambient=0.5, vignette=(56, 14), floor_fade=None)
LIGHT.point(360, -140, r=760, k=1.1, power=1.0)            # el sol de migdia, gairebé a plom


# ─── Fons: cel, plana, illa, vaixells llunyans ─────────────────────────────

def illa(cv):
    """Una illa que ara és una muntanya: una mesa blavosa a l'horitzó, amb els penya-segats marcats de sal."""
    for x in range(88, 196):
        u = (x - 88) / 108
        top = HOR - 1 - 9 * smooth(0, 0.18, u) * (1 - smooth(0.78, 1, u)) - 2 * fbm(x / 9, 0.3, 4)
        for y in range(int(top), HOR + 1):
            band = (y - top)
            lvl = 4.4 + (0.6 if band < 1.2 else 0) - (0.5 if int(y - top) % 3 == 2 else 0)
            lvl += (fbm(x / 6, y / 2, 5) - 0.5) * 0.6
            cv.put(x, y, SKYA, lvl, lit=0)


def vaixell_lluny(cv, x0, y0, s, ang, seed):
    """Un mercant encallat a la plana, petit de tan lluny: el costat del casc (vermell fosc d'òxid), la regala
    clara, el castell blanc a popa amb la xemeneia, dos pals de càrrega. La sal se l'ha menjat fins a mig casc."""
    L = 70 * s
    D = 9 * s

    def fn(u, v):
        if 0 <= u <= L:
            t = u / L
            top = -3.5 * s * (1 - smooth(0, 0.14, t)) - 1.0 * s * smooth(0.9, 1, t)
            bow = smooth(0, 0.08, t)
            if top <= v <= D and (u > (1 - bow) * (v - top) * 0.8):
                if v < top + 1.1:
                    return (PAINTW, 4.6)
                k = (v - top) / (D - top)
                lvl = 2.6 - k * 0.8 + (0.7 if int(u) % 9 == 0 else 0) - (0.6 if hr(int(u) // 2, seed) > 0.8 else 0)
                return (REDF, lvl)
            if 0.70 <= t <= 0.92 and -10 * s <= v < top:                     # el castell
                if int(v - top) % 3 == 1 and int(u) % 3 != 0 and v > -9 * s:
                    return (GLASSD, 1.8)
                return (PAINTW, 4.4 - (t - 0.70) * 4 + (1.0 if v < -9 * s else 0))
            if 0.78 <= t <= 0.84 and -15 * s <= v < -10 * s:                 # la xemeneia
                return (RUSTA, 2.6 if v > -14 * s else 1.6)
            for pt in (0.30, 0.52):                                            # els pals de càrrega
                if abs(t - pt) * L < 0.7 and -13 * s <= v < top:
                    return (STEELA, 3.2)
        return None
    shade(cv, (x0 - 6, y0 - 20 * s, x0 + L + 6, y0 + 14 * s), x0, y0, ang, fn, lit=0.6)
    # la sal que se l'ha menjat per baix, amb una duna petita de vent
    for x in range(int(x0 - 8), int(x0 + L + 10)):
        yy = y0 + D * 0.62 + (x - x0) * math.tan(ang) + math.sin(x * 0.3 + seed) * 0.6
        if x < x0 or x > x0 + L:
            yy += min(abs(x - x0), abs(x - x0 - L)) * 0.35
        for y in range(int(yy), int(y0 + D + 3)):
            cv.put(x, y, SALT, 6.4 - (y - yy) * 0.25)
        cv.put(x, int(yy) + 1, SALT, 4.4) if x0 < x < x0 + L else None
    cv.tint(x0 - 8, y0 - 20 * s, x0 + L + 10, y0 + 14 * s, (226, 234, 240), 0.18)    # la calitja de la distància


def velero(cv, x0, y0):
    """Una barca de vela petita encallada, tombada sobre un costat: el casc blau fosc, la regala blanca, el pal de
    biaix amb un tros de vela esquinçada que encara hi penja."""
    ang = -0.30

    def fn(u, v):
        if 0 <= u <= 38:
            t = u / 38
            top = -2.5 * (1 - smooth(0, 0.3, t))
            bot = 8 * math.sin(math.pi * min(1.0, 0.12 + t * 0.88)) ** 0.6
            if top <= v <= bot and u > (v - top) * 0.5 * (1 - smooth(0, 0.25, t)) * 4:
                if v < top + 1.2:
                    return (PAINTW, 4.8)
                return (TEALH, 2.6 - (v - top) * 0.15 + (0.8 if int(u) % 9 == 0 else 0))
        return None
    shade(cv, (x0 - 6, y0 - 16, x0 + 42, y0 + 14), x0, y0, ang, fn)
    mx, my = to_screen(16, -1, x0, y0, ang)
    tx, ty = to_screen(16, -34, x0, y0, ang)
    cv.line(mx, my, tx, ty, WOODG, 2.8)
    # la vela esquinçada: un triangle gris amb la vora estripada
    for i in range(22):
        t = i / 21
        px, py = to_screen(16, -32 + t * 26, x0, y0, ang)
        w = int((1 - abs(t - 0.45) * 1.6) * 8 * (0.6 + 0.4 * hr(i, 3)))
        for k in range(1, max(1, w)):
            cv.put(px + k, py + k * 0.3, PAINTW, 3.2 + (1 if k == 1 else 0) - k * 0.08)
    # la sal amuntegada contra el casc, i la seva ombra curta
    for x in range(int(x0 - 8), int(x0 + 44)):
        yy = y0 + 4 + (x - x0) * math.tan(ang) * 0.4 + math.sin(x * 0.4) * 0.8
        if x > x0 + 30:
            yy = max(yy, y0 + 4 + (x - x0 - 30) * 0.1)
        for y in range(int(yy), int(yy) + 4):
            cv.put(x, y, SALT, 6.8 - (y - yy) * 0.4)
        if x0 - 4 < x < x0 + 40:
            cv.darken(x, int(yy) + 4, x, int(yy) + 5, 0.5)


def fons_lluny(cv):
    cel(cv, HOR)
    plana(cv, HOR, EDGE + 2)
    illa(cv)
    canonada(cv, CAN_X, HOR, w0=2.2, w1=4.6, light_y=CAN_LY)
    vaixell_lluny(cv, 252, 106, 0.95, 0.07, 1)
    vaixell_lluny(cv, 98, 112, 0.5, -0.03, 2)
    velero(cv, 118, 150)


# ─── L'escullera de l'altra banda de la dàrsena ───────────────────────────

def wtop(x):
    return 101 - (x - WALL_X0) / (W - WALL_X0) * 6


def wbase(x):
    return 176 + (x - WALL_X0) / (W - WALL_X0) * 10


def escullera(cv):
    """La paret de l'escullera, a l'altra banda de la dàrsena: carreus a l'ombra (la cara vertical, amb el sol a
    plom, és més fosca que el damunt), la franja d'algues seques a baix, i les ratlles de sal de l'aigua de cada
    any, cada vegada més avall. Dalt, el parapet al sol."""
    marks = (0.24, 0.40, 0.53, 0.63, 0.71)
    for x in range(WALL_X0, W):
        yt, yb = wtop(x), wbase(x)
        h = yb - yt
        s = (x - WALL_X0) / (W - WALL_X0)
        bw = 10 + s * 7                                                      # amplada dels carreus
        algtop = 0.40 + (fbm(x / 18, 0.5, 13) - 0.5) * 0.12
        for y in range(int(yt), int(yb) + 1):
            f = (y - yt) / h
            row = int(f * 13)
            fr = f * 13 - row
            off = bw / 2 if row % 2 else 0
            col = int((x - WALL_X0 + off) / bw)
            fc = ((x - WALL_X0 + off) / bw) % 1
            lvl = 4.9 + (hr(row, col, 7) - 0.5) * 0.8 + (fbm(x / 14, y / 9, 8) - 0.5) * 0.7 + 0.4 * s
            lvl -= f * 0.6
            joint = fr < 0.13 or fc < 0.07
            if joint:
                lvl -= 1.3
            elif fr < 0.28:
                lvl += 0.5                                                   # el cantell de dalt de cada carreu
            if f > algtop:
                a = (f - algtop) / (1 - algtop)
                spot = fbm(x / 7, y / 5, 12)
                if spot > 0.58 + a * 0.1:
                    cv.put(x, y, ALGA, 2.6 + (spot - 0.58) * 4 - (1.0 if joint else 0))   # taques d'algues seques
                else:
                    cv.put(x, y, WETST, lvl - 0.9 - a * 0.6)
            else:
                cv.put(x, y, STONEA, lvl)
            for m in marks:                                                  # les marques de l'aigua
                d = (f - m) * h
                d += (fbm(x / 10, m * 10, 14) - 0.5) * 2.0
                if -0.5 <= d < 0.5 and fbm(x / 5, m * 7, 15) > 0.38:
                    cv.put(x, y, SALT, 7.2 if f < algtop else 6.0)
                elif 0.5 <= d < 1.5 and hr(x // 2, int(m * 100), 1) < 0.35:
                    cv.put(x, y, SALT, 5.0)
        # el parapet, al sol
        for y in range(int(yt) - 4, int(yt)):
            k = y - (yt - 4)
            notch = int((x - WALL_X0) / (bw * 1.7)) % 5 == 4 and k > 0
            cv.put(x, y, STONEA, (7.6 - k * 0.5) - (1.2 if notch else 0))
        cv.put(x, yt - 5, STONEA, 8.6)
        cv.put(x, yt, STONEA, 2.6)                                            # l'ombra del ràfec del parapet
    # anelles d'amarrar, amb regalims d'òxid
    for ax in (372, 430, 618):
        ay = wtop(ax) + (wbase(ax) - wtop(ax)) * 0.36
        cv.ring(ax, ay, 2, RUSTA, 3.2, step=30)
        for y in range(int(ay + 3), int(ay + 3 + 16)):
            if hr(ax, y) > 0.25:
                cv.put(ax + (1 if hr(y, ax) > 0.7 else 0), y, RUSTA, 3.6 - (y - ay) * 0.08)


def escala(cv):
    """L'escala del port, de pedra, arrapada a la paret: baixa des de dalt i s'acaba a l'aire, a mitja paret. Amb
    la barana de ferro rovellat i l'últim graó trencat."""
    steps = []
    for i in range(12):
        sx = 594 - i * 7
        sy = wtop(sx) + 1 + i * 3.9
        steps.append((int(sx), int(sy)))
    for i, (sx, sy) in enumerate(steps):
        w = 8 if i < 11 else 4
        cv.darken(sx, sy + 4, sx + w + 1, sy + 9, lambda x, y: 0.95 - (y - sy - 4) * 0.16)  # ombra a sota
        cv.rect(sx, sy, sx + w, sy, STONEA, 8.8)                                      # trepitjada, al sol
        cv.rect(sx, sy + 1, sx + w, sy + 3, STONEA, lambda x, y: 5.6 - (1.4 if x == sx else 0) + (y == sy + 1) * 0.6)
    # l'últim graó, trencat: un tros de pedra i la vareta de ferro que en sobresurt
    lx, ly = steps[-1]
    cv.put(lx - 1, ly + 1, STONEA, 4.6)
    cv.line(lx - 1, ly + 2, lx - 4, ly + 5, RUSTA, 3.4)
    # la barana: muntants i passamà
    for i in range(0, 12, 2):
        sx, sy = steps[i]
        cv.vline(sx + 6, sy - 7, sy - 1, RUSTA, 3.0)
    for i in range(10):
        (ax, ay), (bx, by) = steps[i], steps[i + 1]
        cv.line(ax + 6, ay - 7, bx + 6, by - 7, RUSTA, 3.8)
    # l'últim tros de barana, doblegat cap avall
    (ax, ay) = steps[10]
    cv.line(ax + 6, ay - 7, ax - 2, ay + 2, RUSTA, 3.2)


def far(cv):
    """El far vell de l'escullera: blanc de sal, amb el capçal vermell esvaït i el vidre trencat."""
    x0, x1, top, base = 336, 352, 60, 98
    for y in range(top, base):
        t = (y - top) / (base - top)
        hw = 5 + 3 * t
        cx = (x0 + x1) / 2
        for x in range(int(cx - hw), int(cx + hw) + 1):
            u = (x - cx) / hw
            band = (y - top) // 8 % 2 == 1 and y < base - 10
            ramp = REDF if band else PAINTW
            cv.put(x, y, ramp, (4.6 if not band else 4.0) - u * 1.4 - u * u * 0.6)
    cx = 344
    cv.rect(cx - 7, top - 2, cx + 7, top - 1, STEELA, 3.0)                        # el balcó
    cv.rect(cx - 4, top - 10, cx + 4, top - 3, GLASSD, lambda x, y: 2.0 + (1.6 if (x + y) % 5 == 0 else 0))
    cv.vline(cx, top - 10, top - 3, STEELA, 2.0)
    cv.poly([(cx - 5, top - 10), (cx, top - 15), (cx + 5, top - 10)], REDF, 2.8)
    cv.put(cx, top - 16, STEELA, 3.0)
    cv.rect(cx - 1, base - 9, cx + 1, base - 2, STEELA, 1.4)                      # la porta


def darsena(cv):
    """El fons de la dàrsena, al peu de l'escullera: sorra blanca amb ondulacions i l'ombra al peu de la paret."""
    for x in range(WALL_X0, W):
        yb = wbase(x)
        for y in range(int(yb) + 1, EDGE + 1):
            lvl = 5.6 + (y - yb) * 0.05 + (fbm(x / 12, y / 3, 30) - 0.5) * 0.9
            if math.sin(x * 0.3 + y * 1.8 + fbm(x / 20, y / 4, 31) * 5) > 0.75:
                lvl += 0.9
            cv.put(x, y, SAND, lvl)
        cv.darken(x, yb + 1, x, yb + 2, 0.7)


def barca(cv):
    """La barca de pesca encallada al fons de la dàrsena, tombada de proa: casc verd esvaït amb òxid i l'obra
    viva vermella, la timoneria blanca, el pal i el pòrtic de popa. Petita: és quaranta metres més avall."""
    cx, cy, ang, S = 424, 180, -0.22, 0.64
    L = 112

    def fn(u, v):
        u, v = u / S, v / S
        if -L / 2 <= u <= L / 2:
            t = (u + L / 2) / L
            deck = -9 * (1 - smooth(0, 0.3, t)) - 2 * smooth(0.85, 1, t)
            keel = 30 * (1 - abs(2 * t - 1.04) ** 3.0) - 2
            if deck <= v <= keel:
                d = v - deck
                if d < 2.5:
                    return (PAINTW, 4.8 - d * 0.6)
                if 13 < d < 15.5:
                    return (PAINTW, 4.0)
                if d >= 15.5:
                    if hr(int(u) // 5, 3) > 0.7 and d < 22:
                        return (RUSTA, 3.0)
                    return (REDF, 3.2 - (d - 15) * 0.07)
                lvl = 3.4 - d * 0.04 - (0.9 if int(u + 60) % 18 == 0 else 0)
                if hr(int(u) // 3, 5) > 0.8 and d < 4 + 12 * hr(int(u) // 3, 6):
                    return (RUSTA, 3.0)
                return (TEALH, lvl + (0.9 if d < 4.5 else 0))
            if 4 <= u <= 28 and -24 <= v < deck:                             # la timoneria
                if -20 <= v <= -14 and int(u) % 6 not in (0,):
                    return (GLASSD, 1.6)
                return (PAINTW, 4.4 - (u - 4) * 0.04 + (0.8 if v < -21 else 0))
            if 2 <= u <= 30 and -27 <= v < -24:
                return (PAINTW, 5.6)
            if (47 <= u <= 50 or 38 <= u <= 41) and -32 <= v < deck:          # el pòrtic de popa
                return (RUSTA, 3.4)
            if 38 <= u <= 50 and -35 <= v < -32:
                return (RUSTA, 3.0)
        return None
    shade(cv, (cx - 52, cy - 50, cx + 50, EDGE), cx, cy, ang, fn)
    P = lambda u, v: to_screen(u * S, v * S, cx, cy, ang)
    mb, mt = P(-18, -6), P(-18, -64)
    cv.line(*mb, *mt, WOODG, 4.0)
    cv.line(*P(-18, -40), *P(16, -27), WOODG, 3.4)
    for a, b in (((-18, -64), (-54, -10)), ((-18, -64), (44, -35))):
        cv.line(*P(*a), *P(*b), STEELA, 3.0)
    px, py = P(44, -33)                                                      # la xarxa, penjant del pòrtic
    for k in range(6):
        cv.line(px - 1 + k * 0.4, py + 1, px - 3 + k, py + 8 + hr(k, 1) * 4, ROPEA, 2.6 + (k % 2) * 0.8)
    # l'ombra i la sorra que s'hi ha acumulat al voltant
    for x in range(cx - 48, cx + 44):
        yy = P((x - cx) / S, 26)[1] + 1 + math.sin(x * 0.25) * 1.0
        for y in range(int(yy), EDGE + 1):
            cv.put(x, y, SAND, 5.6 + (y - yy) * 0.06 + (fbm(x / 8, y / 3, 33) - 0.5))
        cv.darken(x, yy, x, yy + 1, 0.6 if x < cx + 30 else 0)


# ─── La Cantimplora (la rampa) ─────────────────────────────────────────────

def cantimplora(cv):
    """La Cantimplora aparcada a l'esquerra: el ventre panxut oliva, un dipòsit rodó, la franja taronja de
    seguretat, i la bodega oberta amb la rampa estesa fins al moll. Dins, llum càlida de filament."""
    def xr(y):
        return 66 + 18 * math.sin(math.pi * (y + 40) / 250) - 22 * smooth(150, 196, y)

    for y in range(0, 197):
        r = xr(y)
        for x in range(0, int(r) + 1):
            u = x / r
            lvl = 3.8 - u ** 3 * 1.6 - smooth(120, 196, y) * 1.4 + (fbm(x / 10, y / 14, 61) - 0.5) * 0.8
            if y % 22 == 0:
                lvl -= 1.2
            elif y % 22 == 1:
                lvl += 0.6
            if x % 26 == 13 and y % 22 > 2:
                lvl -= 0.7
            if (y % 22 == 3) and x % 4 == 0:
                lvl += 1.0                                                   # reblons
            ramp = OLIVEN
            if 40 <= y <= 47:
                ramp = ORANGEN
                lvl = 3.4 - u ** 3 * 1.6 + (0.8 if y == 40 else 0) - (1.0 if y == 47 else 0)
                if (x + y) // 5 % 2 == 0 and y > 41:
                    ramp, lvl = BLACKT, 2.0
            if hr(x, y // 22, 77) > 0.95 and 2 < (y % 22) < 3 + 16 * hr(x, y // 22, 78):
                ramp, lvl = RUSTA, 2.8 - (y % 22) * 0.06                     # regalims d'òxid, sota les juntes
            cv.put(x, y, ramp, lvl)
        cv.put(int(r), y, OLIVEN, 0.6)
    # el nom, de plantilla, i un ull de bou
    text(cv, 'CANTIMPLORA', 8, 62, PAINTW, 4.2)
    cv.disc(52, 22, 6, 6, OLIVEN, lambda nx, ny: 5.0 - ny * 1.6)
    cv.disc(52, 22, 4, 4, GLASSD, lambda nx, ny: 2.0 - nx - ny * 0.6)
    cv.put(50, 20, GLASSD, 5.0)
    # la bodega oberta
    ox0, ox1, oy0, oy1 = 6, 56, 92, 168
    cv.rect(ox0 - 3, oy0 - 3, ox1 + 3, oy1, ORANGEN, lambda x, y: 3.0 - (1.4 if x > ox1 else 0))
    cv.rect(ox0, oy0, ox1, oy1, BLACKT, lambda x, y: 1.0 + 1.8 * max(0.0, 1 - math.hypot(x - 32, y - 120) / 44), lit=0)
    cv.glow(32, 118, 30, (250, 196, 120), 0.55)
    cv.disc(32, 99, 3, 2, [(140, 100, 40), (250, 210, 130), (255, 244, 210)], 2.0, lit=0)   # la bombeta
    for bx, by, bw, bh in ((10, 140, 14, 14), (24, 146, 12, 10), (44, 142, 10, 12)):      # caixes a dins
        cv.rect(bx, by, bx + bw, by + bh, WICKER, lambda x, y: 2.0 + (0.8 if y == by else 0) - (0.6 if x == bx + bw else 0), lit=0.3)
    # la rampa estesa: de la frontissa (168) fins al moll
    tl, tr, br, bl = (ox0, oy1), (ox1, oy1), (112, 226), (40, 232)
    def ramp_lvl(x, y):
        t = (y - oy1) / (232 - oy1)
        lvl = 3.8 - t * 0.4
        if (x + y * 2) % 6 == 0 or (x - y * 2) % 6 == 0:
            lvl += 0.8                                                       # la xapa de llàgrima
        return lvl
    cv.poly([tl, tr, br, bl], STEELA, ramp_lvl)
    for k in range(3):                                                       # les vores ratllades
        for (ax, ay), (bx, by) in (((tl[0] + k, tl[1]), (bl[0] + k, bl[1])), ((tr[0] - k, tr[1]), (br[0] - k, br[1]))):
            n = int(max(abs(bx - ax), abs(by - ay)))
            for i in range(n + 1):
                x, y = ax + (bx - ax) * i / n, ay + (by - ay) * i / n
                if int(y / 4) % 2:
                    cv.put(x, y, ORANGEN, 3.8)
                else:
                    cv.put(x, y, BLACKT, 2.0)
    cv.line(bl[0], bl[1], br[0], br[1], STEELA, 1.6)
    cv.line(bl[0], bl[1] + 1, br[0], br[1] + 1, STEELA, 0.4)
    # els pistons hidràulics
    cv.line(ox1 + 4, 132, 84, 200, STEELA, 5.0)
    cv.line(ox1 + 5, 132, 85, 200, STEELA, 3.0)
    # la pota d'aterratge
    cv.line(70, 150, 92, 204, STEELA, 3.4)
    cv.line(71, 150, 93, 204, STEELA, 1.8)
    cv.disc(93, 206, 8, 2.4, STEELA, lambda nx, ny: 3.6 - ny * 1.2)
    cv.darken(84, 207, 104, 210, 0.7)


# ─── La grua i la cistella ─────────────────────────────────────────────────

def _lattice(cv, a, b, w, ramp, lvl, n):
    """Una ploma de gelosia: dos cordons paral·lels i diagonals en ziga-zaga."""
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    L = math.hypot(dx, dy)
    nx, ny = -dy / L * w, dx / L * w
    cv.line(ax + nx, ay + ny, bx + nx * 0.5, by + ny * 0.5, ramp, lvl - 1.0)
    cv.line(ax - nx, ay - ny, bx - nx * 0.5, by - ny * 0.5, ramp, lvl + 0.6)
    for i in range(n):
        t0, t1 = i / n, (i + 1) / n
        s0, s1 = 1 - 0.5 * t0, 1 - 0.5 * t1
        p0 = (ax + dx * t0 + nx * s0 * (1 if i % 2 else -1), ay + dy * t0 + ny * s0 * (1 if i % 2 else -1))
        p1 = (ax + dx * t1 + nx * s1 * (-1 if i % 2 else 1), ay + dy * t1 + ny * s1 * (-1 if i % 2 else 1))
        cv.line(*p0, *p1, ramp, lvl - 0.4)


GX = 212                    # l'eix de la grua
CAB = (176, 40, 252, 86)    # la caseta (sala de màquines + cabina)
WIN = (222, 48, 247, 68)    # la finestra de la cabina


def grua(cv):
    """La grua vella del port: un pedestal de reblons, la caseta giratòria (la sala de màquines amb persianes i la
    cabina amb finestral), el contrapès de formigó, la ploma de gelosia i els tirants. Pintura groc ocre esvaïda,
    amb òxid a les juntes."""
    # el pedestal
    for y in range(92, FLOOR + 1):
        t = (y - 92) / (FLOOR + 1 - 92)
        hw = 12 + 8 * t
        for x in range(int(GX - hw), int(GX + hw) + 1):
            u = (x - GX) / hw
            lvl = 4.0 - u * 1.3 - u * u * 0.9 + (fbm(x / 6, y / 10, 70) - 0.5) * 0.6
            seg = (y - 92) % 18
            if seg == 0:
                lvl -= 1.2
            elif seg == 1:
                lvl += 0.6
            if seg == 3 and int(x - GX + 40) % 4 == 0:
                lvl += 1.2                                                     # reblons
            ramp = OCHRE
            if hr(x // 2, 80) > 0.72 and 1 < seg < 2 + 14 * hr(x // 2, y // 18, 81):
                ramp, lvl = RUSTA, lvl - 0.4
            cv.put(x, y, ramp, lvl)
    # la porteta del pedestal i la placa
    cv.rect(GX - 4, 150, GX + 4, 172, OCHRE, lambda x, y: 3.0 - (0.8 if x == GX + 4 else 0) + (0.6 if y == 150 else 0))
    cv.put(GX + 2, 161, STEELA, 5.0)
    cv.rect(GX - 5, 124, GX + 5, 129, PAINTW, 4.4)
    text(cv, 'P3', GX - 3, 124, STEELA, 1.0)
    cv.rect(GX - 24, FLOOR - 2, GX + 24, FLOOR + 2, STEELA, lambda x, y: 4.4 - (y - FLOOR + 2) * 0.7)   # la base
    for bx in range(GX - 21, GX + 22, 6):
        cv.put(bx, FLOOR - 1, STEELA, 6.2)
    # la corona de gir
    cv.rect(GX - 17, 86, GX + 17, 92, STEELA, lambda x, y: 4.2 - (y - 86) * 0.4 + (1.2 if x % 3 == 0 and y == 89 else 0))
    # el contrapès de formigó, a la cua
    cv.rect(150, 62, 180, 92, STONEA, lambda x, y: 5.6 - (y - 62) * 0.04 + (1.2 if y == 62 else 0)
            - (1.4 if (x - 150) % 10 == 0 and y > 63 else 0) + (fbm(x / 5, y / 5, 72) - 0.5) * 0.8)
    cv.rect(150, 90, 180, 92, STONEA, 3.0)
    # la caseta
    x0, y0, x1, y1 = CAB
    cv.rect(x0, y0, x1, y1, OCHRE, lambda x, y: 4.1 - (x - x0) * 0.008 - (1.4 if x >= x1 - 1 else 0)
            + (fbm(x / 8, y / 8, 71) - 0.5) * 0.6 - (y - y0) * 0.012)
    for xx in range(x0 + 1, x1):                                                # juntes de les planxes i reblons
        if (xx - x0) % 15 == 0:
            cv.vline(xx, y0 + 1, y1 - 1, OCHRE, 2.8)
    for yy in (y0 + 2, y1 - 2):
        for xx in range(x0 + 2, x1 - 1, 4):
            cv.put(xx, yy, OCHRE, 5.4)
    cv.rect(x0 - 3, y0 - 5, x1 + 3, y0 - 1, OCHRE, lambda x, y: 5.4 - (y - y0 + 5) * 0.6)     # la teulada
    cv.hline(x0 - 3, x1 + 3, y0 - 5, OCHRE, 6.4)
    cv.darken(x0, y0, x1, y0 + 1, 0.8)
    # persianes de la sala de màquines
    for k in range(5):
        cv.hline(x0 + 6, x0 + 22, y0 + 10 + k * 3, OCHRE, 2.0)
        cv.hline(x0 + 6, x0 + 22, y0 + 11 + k * 3, OCHRE, 4.8)
    # la porta de la cabina, amb la finestreta
    cv.rect(198, 50, 213, y1 - 1, OCHRE, lambda x, y: 3.4 - (0.9 if x == 213 else 0) + (0.6 if y == 50 else 0))
    cv.rect(201, 54, 210, 63, GLASSD, lambda x, y: 1.8 + (1.4 if (x - y) % 7 == 0 else 0))
    cv.put(211, 70, STEELA, 5.4)
    # el finestral de la cabina
    wx0, wy0, wx1, wy1 = WIN
    cv.rect(wx0 - 1, wy0 - 1, wx1 + 1, wy1 + 1, STEELA, 2.0)
    cv.rect(wx0, wy0, wx1, wy1, GLASSD, lambda x, y: 1.4 + (0.9 if y < wy0 + 6 else 0)
            + (1.8 if (x - y) % 11 in (0, 1) else 0))
    cv.vline((wx0 + wx1) // 2, wy0, wy1, STEELA, 2.2)
    cv.hline(wx0 - 2, wx1 + 2, wy1 + 2, OCHRE, 5.2)                             # l'ampit
    # òxid de la vora de baix
    for x in range(x0 + 1, x1):
        if hr(x, 90) > 0.45:
            cv.vline(x, y1 - 3, y1 - 1 - int(hr(x, 91) * 2), RUSTA, 2.8)
    # la ploma, el peu articulat i la politja
    _lattice(cv, (248, 78), CRANE_TIP, 4.0, OCHRE, 3.8, 16)
    cv.disc(248, 78, 4, 4, STEELA, lambda nx, ny: 4.2 - nx - ny)
    cv.disc(CRANE_TIP[0], CRANE_TIP[1] + 1, 4, 4, STEELA, lambda nx, ny: 4.4 - nx - ny)
    cv.put(CRANE_TIP[0], CRANE_TIP[1] + 1, STEELA, 1.0)
    # l'A del damunt de la caseta i els tirants
    cv.line(200, y0 - 5, 214, 16, STEELA, 3.8)
    cv.line(228, y0 - 5, 214, 16, STEELA, 2.8)
    cv.line(214, 16, CRANE_TIP[0] - 2, CRANE_TIP[1] - 1, STEELA, 3.0)
    cv.line(214, 16, 154, 62, STEELA, 3.0)
    cv.disc(214, 16, 2, 2, STEELA, 4.4)
    # el cable de la cistella
    cv.vline(CRANE_TIP[0] + 3, CRANE_TIP[1] + 4, BASKET[1] - 18, STEELA, 3.4)
    # l'ombra curta del pedestal (és migdia)
    cv.darken(GX - 30, FLOOR + 3, GX + 30, FLOOR + 8, lambda x, y: 0.95 if abs(x - GX) < 28 - (y - FLOOR - 3) * 4 else 0)


def cistella(cv):
    """La cistella de descarregar peix: un cistell gran de vímet amb cèrcols de ferro, quatre cadenes fins al
    ganxo. Penja sobre el buit, més enllà de la vora."""
    x0, y0, x1, y1 = BASKET
    cx = (x0 + x1) / 2
    hx, hy = CRANE_TIP[0] + 3, y0 - 18
    cv.disc(hx, hy, 2.5, 3, STEELA, lambda nx, ny: 4.2 - nx)                     # el ganxo
    cv.put(hx + 1, hy + 2, STEELA, 1.0)
    for ax in (x0 + 1, x0 + 10, x1 - 10, x1 - 1):
        cv.line(hx, hy + 3, ax, y0 + 1, STEELA, 3.0 + (0.8 if ax < hx else 0))
    for y in range(y0, y1 + 1):
        t = (y - y0) / (y1 - y0)
        inset = int(t * 4)
        for x in range(x0 + inset, x1 - inset + 1):
            u = (x - cx) / ((x1 - x0) / 2)
            weave = ((x // 2) + (y // 2)) % 2
            lvl = 3.8 - u * 1.2 - u * u * 0.8 + (0.6 if weave else -0.4) - t * 0.6
            cv.put(x, y, WICKER, lvl)
    cv.disc(cx, y0 + 1, (x1 - x0) / 2 + 1, 3.2, STEELA, lambda nx, ny: 3.6 + ny * 1.0 if ny > 0 else 2.2)
    cv.disc(cx, y0 + 1, (x1 - x0) / 2 - 1, 1.8, WICKER, 0.8)
    for yy in (y0 + 12, y1 - 4):
        ins = int((yy - y0) / (y1 - y0) * 4)
        cv.hline(x0 + ins, x1 - ins, yy, STEELA, 3.2)
    cv.line(x1 - 5, y1, x1 - 3, y1 + 9, ROPEA, 3.2)                             # una corda que penja


# ─── El moll ───────────────────────────────────────────────────────────────

def moll(cv):
    """El terra del moll: lloses grans en perspectiva, de calcària clara, amb sal a les juntes i taques de sal
    seca. La pedra de coronament (una vorada) a la vora, amb el cantell contra el buit."""
    for y in range(FLOOR, RH):
        dz = y - HOR
        rc = 961 / dz
        row = math.floor(rc)
        rowf = rc - row
        t = (y - FLOOR) / (RH - FLOOR)
        for x in range(W):
            gx = (x - 320) / dz * 2.0 + (0.5 if row % 2 else 0)
            col = math.floor(gx)
            colf = gx - col
            lvl = 6.0 + (hr(row, col, 40) - 0.5) * 0.9 + (fbm(x / 40, y / 10, 41) - 0.5) * 0.6 - t * 0.3
            if (1 - rowf) < 961 / dz ** 2 * 1.0:
                lvl = 3.0                                                      # junta: la vora de la llosa següent
                if fbm(x / 6, row, 42) > 0.62:
                    cv.put(x, y, SALT, 7.4)
                    continue
            elif colf < 2.0 / dz * 1.1:
                lvl = 3.4
                if hr(row, y // 3, col) > 0.75:
                    cv.put(x, y, SALT, 7.2)
                    continue
            elif rowf < 961 / dz ** 2 * 1.2:
                lvl += 0.8                                                     # el cantell de cada llosa, al sol
            salt = fbm(x / 26, y / 7, 43)
            if salt > 0.64:
                lvl += 1.0
                if hr(x, y, 44) > 0.93:
                    cv.put(x, y, SALT, 7.6)
                    continue
            cv.put(x, y, QUAY, lvl)
    # esquerdes en unes quantes lloses
    for sx, sy, n, seed in ((262, 226, 22, 1), (470, 244, 30, 2), (120, 250, 18, 3), (560, 222, 16, 4)):
        x, y = sx, sy
        for i in range(n):
            cv.put(x, y, QUAY, 2.4)
            x += 1
            y += (1 if hr(i, seed) > 0.66 else (-1 if hr(i, seed) < 0.2 else 0))
    # la vorada de coronament
    for x in range(W):
        bi = x // 40
        for y in range(EDGE, FLOOR):
            k = y - EDGE
            lvl = (8.4, 8.0, 7.4, 5.2, 4.8, 4.4)[k] + (hr(bi, 50) - 0.5) * 0.7 + (fbm(x / 9, y / 3, 51) - 0.5) * 0.5
            if x % 40 == 0:
                lvl -= 2.2
            cv.put(x, y, QUAY, lvl)
        cv.put(x, EDGE - 1, STONEA, 1.6)                                       # el cantell: a l'altra banda, el buit
    cv.darken(0, FLOOR, W - 1, FLOOR, 0.7)


def norai(cv, x, y, corda=None):
    """Un norai de ferro colat, damunt la vorada. `corda`: el punt on una corda vella se'n va per la vora."""
    cv.darken(x - 8, y + 1, x + 8, y + 3, lambda xx, yy: 0.9 if ((xx - x) / 8) ** 2 + ((yy - y - 1) / 2) ** 2 < 1 else 0)
    cv.rect(x - 4, y - 9, x + 4, y, STEELA, lambda xx, yy: 4.0 - (xx - x) * 0.4)
    cv.disc(x, y - 10, 7, 3, STEELA, lambda nx, ny: 4.6 - ny * 1.2 - nx * 0.6)
    cv.disc(x, y - 11, 5, 1.6, STEELA, 5.6)
    for k in range(2):
        cv.disc(x, y - 3 - k * 2, 5.5, 1.5, ROPEA, lambda nx, ny: 3.6 - ny - nx * 0.6)
    if corda:
        cv.line(x + 4, y - 4, corda[0], corda[1], ROPEA, 3.4)
        cv.line(x + 4, y - 3, corda[0], corda[1] + 1, ROPEA, 1.8)


def caixes(cv):
    """Caixes de peix buides, de plàstic blau esvaït, plenes de sal."""
    BOX = [(30, 50, 70), (46, 74, 98), (66, 100, 126), (92, 128, 152), (124, 158, 178), (166, 192, 206)]
    for bx, by, n in ((112, FLOOR + 6, 3), (136, FLOOR + 10, 2)):
        for k in range(n):
            y0 = by - (k + 1) * 9
            cv.rect(bx, y0, bx + 20, y0 + 8, BOX, lambda x, y: 3.4 - (1.0 if x == bx + 20 else 0) + (0.8 if y == y0 else 0)
                    - (1.4 if (x - bx) % 5 == 0 and y0 + 2 < y < y0 + 7 else 0))
            cv.rect(bx + 2, y0, bx + 18, y0 + 1, SALT, 6.8)
        cv.darken(bx - 1, by, bx + 22, by + 2, 0.8)
    cv.rect(160, FLOOR + 4, 172, FLOOR + 9, WICKER, 2.8)                      # un cistell petit, tombat
    cv.disc(160, FLOOR + 6, 2, 3, WICKER, 1.2)


def retol(cv, x, y):
    """Un rètol vell del port, al costat de la vora: PROHIBIT BANYAR-SE."""
    cv.rect(x + 17, y + 15, x + 18, FLOOR + 10, STEELA, 3.0)
    cv.rect(x, y, x + 37, y + 15, PAINTW, lambda xx, yy: 5.0 - (0.6 if xx > x + 34 else 0) - (fbm(xx / 4, yy / 4, 60) > 0.66) * 1.8)
    cv.rect(x, y, x + 37, y, PAINTW, 6.0)
    REDT = [(80, 20, 20), (150, 40, 34), (196, 70, 52)]
    text(cv, 'PROHIBIT', x + 3, y + 2, REDT, 1.4)
    text(cv, 'BANYAR-SE', x + 2, y + 8, REDT, 1.4)
    for xx in range(x, x + 38, 5):
        if hr(xx, 61) > 0.5:
            cv.vline(xx, y + 14, y + 15, RUSTA, 2.4)
    cv.darken(x + 12, FLOOR + 10, x + 26, FLOOR + 12, 0.8)


def detalls_moll(cv):
    norai(cv, 276, EDGE + 2)
    norai(cv, 548, EDGE + 2, corda=(566, EDGE - 1))
    # sorra de sal acumulada contra la vorada
    for x in range(W):
        h = 1 + 3 * fbm(x / 14, 0.5, 52)
        for y in range(FLOOR, int(FLOOR + h)):
            cv.put(x, y, SALT, 7.0 - (y - FLOOR) * 0.4 + (hr(x, y, 53) - 0.5))
    # una estrella de mar seca i un parell de closques
    for k in range(5):
        a = k / 5 * 2 * math.pi - math.pi / 2
        cv.line(352, 236, 352 + math.cos(a) * 5, 236 + math.sin(a) * 3, REDF, 4.0)
    cv.put(352, 236, REDF, 5.4)
    for sx, sy in ((300, 247), (512, 228), (78, 246)):
        cv.disc(sx, sy, 2, 1.4, BONE, 4.0)
        cv.put(sx - 1, sy + 1, BONE, 1.0)
    retol(cv, 456, 152)


def ombres(cv):
    """Ombres curtes (sol a plom) a sota del rètol, del panell i de la rampa."""
    cv.darken(36, 228, 116, 236, lambda x, y: 0.9 if y > 230 - (x - 40) * 0.07 else 0)


# ─── Composició ────────────────────────────────────────────────────────────

PANEL = (588, 112)


def bg(cv):
    fons_lluny(cv)
    darsena(cv)
    escullera(cv)
    far(cv)
    escala(cv)
    barca(cv)
    # la calitja del forat: com més avall, més blavosa (són quaranta metres)
    cv.tint(WALL_X0, 120, W - 1, EDGE, (214, 226, 238), lambda x, y: 0.28 * smooth(130, 196, y))
    moll(cv)
    detalls_moll(cv)
    caixes(cv)
    grua(cv)
    cistella(cv)
    cantimplora(cv)
    ombres(cv)
    panell(cv, *PANEL, post_to=FLOOR + 12)
    for X, Y, _, _ in cv.pixels(0, RH, W - 1, H - 1):                          # la barra de verbs: negre
        cv.P[X, Y] = (0, 0, 0, 255)


def grua_arreglada(cv):
    """La grua arreglada: el quadre de comandament encès (llum verd al finestral de la cabina) i el pilot verd
    del pedestal."""
    GREENL = [(16, 50, 30), (30, 110, 56), (70, 200, 100), (170, 250, 190)]
    wx0, wy0, wx1, wy1 = WIN
    for y in range(wy0, wy1 + 1):
        for x in range(wx0, wx1 + 1):
            if x == (wx0 + wx1) // 2:
                continue
            d = math.hypot(x - (wx0 + wx1) / 2, (y - wy1) * 1.3) / 20
            if d < 1:
                cv.put(x, y, GREENL, 2.6 - d * 2.4 + ((x - y) % 11 in (0, 1)) * 0.8, lit=0)
    cv.rect(wx0 + 3, wy1 - 3, wx1 - 3, wy1 - 1, GREENL, lambda x, y: 1.2 + (1.8 if x % 3 == 0 else 0), lit=0)
    cv.flat(GX + 5, 100, GREENL[3])                                             # el pilot del pedestal
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        for X, Y, _, _ in cv.pixels(GX + 5 + dx, 100 + dy, GX + 5 + dx, 100 + dy):
            cv.P[X, Y] = GREENL[2] + (170,)


PROPS = {'grua_arreglada': grua_arreglada}


# ─── Animacions ────────────────────────────────────────────────────────────

def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv.img


def _frames_calitja():
    return calitja_frames(_base(), 0, WALL_X0 - 1, HOR - 3, HOR + 9, n=8, amp=1.0)


def _frames_pols():
    return pols_frames(24, 26, (0, FLOOR - 6, W - 1, RH - 6), seed=5, C=Canvas)


def _frames_llum():
    on = canonada_llum(CAN_X, CAN_LY, True, Canvas)
    off = Canvas(transparent=True).img
    return [on, on, off, off, off, off, off, off]


ANIMS = {'calitja': {'frames': _frames_calitja, 'frameDuration': 160},
         'pols': {'frames': _frames_pols, 'frameDuration': 110},
         'llum_canonada': {'frames': _frames_llum, 'frameDuration': 250}}


GEOMETRIA = {
    'things': {
        'rampa': {'rect': (4, 92, 116, 232), 'walk': (104, 232)},
        'escala_port': {'rect': (500, 96, 604, 162), 'walk': (560, 212)},
        'grua': {'rect': (146, 8, 312, 204), 'walk': (240, 214)},
        'cistella': {'rect': (312, 140, 354, 196), 'walk': (332, 210)},
        'vaixells': {'rect': (364, 112, 468, 195), 'walk': (414, 210)},
        'panell_preu': {'rect': (586, 110, 636, 136), 'walk': (596, 218)},
        'canonada': {'rect': (422, 0, 440, 104), 'walk': (432, 210)},
    },
    'spawns': {'iri': (132, 238), 'vet': (172, 246)},
    'walkable': [(96, 222), (120, 208), (250, 206), (560, 206), (639, 212), (639, 256), (60, 256), (40, 238)],
}
