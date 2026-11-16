#!/usr/bin/env python3
"""
Prova de densitat: l'estudi de l'Iri (hd640/rooms/pis_estudi) a 1280×720.

Tres versions, per comparar-les:
  a) l'actual, a 640×360, ampliada ×2;
  b) «auto»: el mateix codi de la sala, pintat amb Canvas2x (formes, dither, llum i efectes a 1280);
  c) «detall»: b) + la paret, el terra, la finestra, els monitors i els cables del terra dibuixats de nou a
     1280, amb el detall que a 640 no hi cap (juntes i bisells d'1 px, veta de la fusta, codi llegible, pluja
     fina, persianes amb volum).
Els personatges (Iri i Diu) són els de 640 ampliats ×2, amb la llum de la sala (characterLights).

  python3 hd1280/pis_estudi.py <directori de sortida>
"""
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import hd640  # noqa: E402
from hd.pix import Canvas, W, H, hr, mix  # noqa: E402
from hd.rooms.comu import obox, outline, text  # noqa: E402
from hd640 import llum  # noqa: E402
from hd640.rooms import pis_estudi as m  # noqa: E402
from hd1280.canvas2x import Canvas2x, S, lc  # noqa: E402

FLOOR_Y = m.FLOOR_Y
NOISE = np.random.default_rng(7).random((H * S, W * S))


def _brick(bx, row, _c={}):
    k = (bx, row)
    if k not in _c:
        _c[k] = (hr(bx, row), hr(bx, row, 5), hr(bx, row, 9), hr(bx, row, 13))
    return _c[k]


# ─── Paret: maons de 48×18 px reals, juntes d'1 px, bisell a dalt i a l'esquerra, esquerdes, escantonats ───

def wall_hd(cv):
    for Y in range(0, FLOOR_Y * S):
        row, by = Y // 18, Y % 18
        off = 24 if row % 2 else 0
        for X in range(W * S):
            u = X + off
            bx, bxx = u // 48, u % 48
            n = NOISE[Y, X]
            if by == 17 or bxx == 0:
                cv.px(X, Y, m.MORTAR, 2.0 + (n - 0.5) * 0.8)
                continue
            shade, chip, crack, wear = _brick(bx, row)
            lvl = 2.6 + (shade - 0.5) * 0.8 + (n - 0.5) * 0.5
            if by == 0:
                lvl += 0.55                                   # el cantell de dalt agafa llum
            elif by == 1:
                lvl += 0.2
            elif by == 16:
                lvl -= 0.45                                   # i el de baix fa ombra
            if bxx == 1:
                lvl += 0.25
            elif bxx == 47:
                lvl -= 0.35
            if chip > 0.9 and bxx + by < 9:
                lvl -= 1.3                                    # escantonat
            if crack > 0.93 and 8 < bxx < 38 and abs(by - (6 + (bxx - 20) * 0.25 + 1.6 * math.sin(bxx * 0.6))) < 0.6:
                lvl -= 1.1                                    # esquerda
            if wear > 0.86 and (bxx - 24) ** 2 / 140 + (by - 8) ** 2 / 30 < 1 + (n - 0.5):
                lvl -= 0.5                                    # la pintura, gastada
            cv.px(X, Y, m.BRICK, lvl)
    # sòcol, amb el cantell d'1 px
    cv.rect(0, FLOOR_Y - 7, W - 1, FLOOR_Y - 1, m.DESKB, 2.4)
    for X in range(W * S):
        cv.px(X, (FLOOR_Y - 7) * S, m.DESKB, 3.8)
        cv.px(X, (FLOOR_Y - 7) * S + 1, m.DESKB, 3.0)
        cv.px(X, FLOOR_Y * S - 1, m.DESKB, 1.2)
        cv.px(X, FLOOR_Y * S, m.DESKB, 0)
        cv.px(X, FLOOR_Y * S + 1, m.DESKB, 0)


# ─── Terra: el laminat, amb la veta de la fusta i juntes primes ─────────────

def floor_hd(cv):
    for Y in range((FLOOR_Y + 1) * S, H * S):
        y = lc(Y)
        dep = (y - FLOOR_Y) / (H - FLOOR_Y)
        v = (y - FLOOR_Y) * 2.4 / (1 + dep * 0.5)
        for X in range(W * S):
            x = lc(X)
            u = (x - W / 2) / (1 + dep * 0.5) + W / 2
            plank = math.floor(u / 40)
            f = u % 40
            ph = hr(plank, 3)
            lvl = 2.4 + (ph - 0.5) * 0.6 + (NOISE[Y, X] - 0.5) * 0.3
            lvl += 0.28 * math.sin(f * 0.55 + ph * 9 + 2.2 * math.sin(v * 0.05 + plank * 1.7))   # la veta
            if f < 0.45:
                lvl = 0.6
            elif f < 0.9:
                lvl -= 0.45
            elif f > 39.3:
                lvl += 0.35
            elif int(v * 2 + hr(plank, 7) * 180) % 180 == 0:
                lvl = 1.0                                     # junta de testa
            cv.px(X, Y, m.FLOORB, lvl)
    cv.tint(267, FLOOR_Y + 16, 493, 267, (60, 180, 170),
            lambda x, y: 0.18 * max(0, 1 - abs(x - 377) / 120) * max(0, 1 - (y - 216) / 53))


# ─── La finestra: ciutat amb més finestres, pluja fina, persianes amb volum ──

def _pxtint(cv, X, Y, col, k):
    if 0 <= X < cv.w and 0 <= Y < cv.h:
        o = cv.P[X, Y]
        cv.P[X, Y] = mix(o, col, min(1, k)) + (o[3],)


def window_hd(cv, rain=0):
    x0, y0, x1, y1 = m.WINDOW
    X0, Y0, X1, Y1 = (x0 + 4) * S, (y0 + 4) * S, (x1 - 3) * S, (y1 - 3) * S
    for Y in range(Y0, Y1):
        for X in range(X0, X1):
            cv.px(X, Y, m.SKY, 0.6 + (lc(Y) - y0) / 53 + (NOISE[Y, X] - 0.5) * 0.25, lit=0)
    # boira de la ciutat a l'horitzó
    cv.tint(x0 + 4, y1 - 40, x1 - 4, y1 - 4, (120, 60, 140), lambda x, y: 0.25 * max(0, 1 - abs(y - (y1 - 30)) / 18))
    blocks = ((49, 19, 75), (69, 13, 88), (84, 24, 61), (109, 16, 83), (127, 21, 53), (147, 16, 75))
    for i, (bx, bw, bh) in enumerate(blocks):
        top = y1 - 4 - bh
        cv.rect(bx, top, bx + bw, y1 - 4, m.CITY, 1.0 + (0.4 if i % 2 else 0), lit=0)
        for Y in range(top * S, (y1 - 4) * S):
            cv.px((bx + bw) * S + 1, Y, m.CITY, 0.2, lit=0)              # el cantell en ombra, d'1 px
            cv.px(bx * S, Y, m.CITY, 2.0, lit=0)                          # i el que rep el neó
        if i in (1, 4):
            cv.line(bx + bw // 2, top - 12, bx + bw // 2, top - 1, m.CITY, 2.0, lit=0, thin=True)
            cv.line(bx + bw // 2 - 2, top - 7, bx + bw // 2 + 2, top - 7, m.CITY, 1.8, lit=0, thin=True)
            cv.pxflat((bx + bw // 2) * S, (top - 12) * S, (255, 60, 60))
            cv.pxflat((bx + bw // 2) * S, (top - 12) * S + 1, (160, 30, 30))
        elif i in (0, 3):
            cv.rect(bx + 3, top - 5, bx + 9, top - 1, m.CITY, 1.6, lit=0)
            cv.hline(bx + 2, bx + 10, top - 6, m.CITY, 2.2, lit=0)
            for X in range((bx + 3) * S, (bx + 10) * S, 3):
                cv.line(X / S, top - 1, X / S - 0.5, top + 0.5, m.CITY, 0.6, lit=0, thin=True)   # les potes
        # finestres de 2×2 px reals, en files de 5
        for Y in range(top * S + 6, (y1 - 8) * S, 5):
            for X in range(bx * S + 3, (bx + bw) * S - 3, 4):
                h = hr(X, Y, i)
                if h > 0.68:
                    col = (120, 190, 220) if hr(Y, X) > 0.55 else (220, 160, 90) if hr(Y, X, 2) > 0.3 else (230, 90, 170)
                    dim = tuple(int(c * 0.6) for c in col)
                    cv.pxflat(X, Y, col)
                    cv.pxflat(X + 1, Y, dim)
                    cv.pxflat(X, Y + 1, dim)
                    cv.pxflat(X + 1, Y + 1, tuple(int(c * 0.4) for c in col))
                elif h > 0.6:
                    cv.pxflat(X, Y, (40, 34, 60))                              # una finestra a les fosques
    # el rètol de neó
    for x in range(61, 93):
        for y in (107, 117):
            cv.put(x, y, m.NEON, 2.6, lit=0)
    for X in range(61 * S, 93 * S):
        cv.px(X, 107 * S, m.NEON, 4.2, lit=0)                                 # el tub, amb el reflex d'1 px
        cv.px(X, 117 * S, m.NEON, 4.2, lit=0)
    text(cv, 'PIZZA', 67, 110, m.NEON, 3.8, lit=0)
    cv.glow(77, 112, 24, (255, 90, 200), 0.4)
    # pluja: regalims d'1 px, amb la gota al cap
    for i in range(90):
        rx = X0 + 2 + int(hr(i, 9) * (X1 - X0 - 4))
        ry = Y0 + int((hr(i, 3) * (Y1 - Y0) + rain * 18 + i * 8) % (Y1 - Y0 - 24))
        n = 6 + int(hr(i, 5) * 16)
        wob = hr(i, 6) * 6
        for d in range(n):
            _pxtint(cv, rx + int(math.sin(d / 5 + wob) * 1.2), ry + d, (170, 200, 230), 0.25 + 0.2 * d / n)
        _pxtint(cv, rx, ry + n, (220, 235, 255), 0.75)
        _pxtint(cv, rx + 1, ry + n, (220, 235, 255), 0.45)
        _pxtint(cv, rx, ry + n + 1, (120, 140, 170), 0.5)
    for i in range(60):                                                       # gotetes quietes al vidre
        _pxtint(cv, X0 + int(hr(i, 21) * (X1 - X0)), Y0 + int(hr(i, 22) * (Y1 - Y0)), (200, 220, 245), 0.5)
    # persiana: llistons de 6 px reals cada 10, amb volum (cantell clar, cos, cantell fosc) i les cintes
    for Ys in range((y0 + 3) * S, 96 * S, 10):
        for X in range((x0 + 3) * S, (x1 - 2) * S):
            curve = 0.25 * math.sin((X - x0 * S) / ((x1 - x0) * S) * math.pi)
            for d, lv in enumerate((4.2, 3.6, 3.0, 2.6, 2.0, 0.8)):
                cv.px(X, Ys + d, m.STEELB, lv + curve)
            cv.px(X, Ys + 6, m.STEELB, 0, lit=0) if NOISE[Ys, X] > 0.5 else None   # l'ombra del llistó, tramada
    for X in range((x0 + 3) * S, (x1 - 2) * S):
        for d, lv in enumerate((4.4, 4.0, 3.4, 2.8, 2.2, 1.6, 0.6)):
            cv.px(X, 97 * S + d, m.STEELB, lv)
    for cx in (x0 + 24, x1 - 24):
        for Y in range((y0 + 3) * S, 97 * S):
            cv.px(cx * S, Y, m.GRAYC, 2.6)                                    # les cintes, d'1 px
            cv.px(cx * S + 6, Y, m.GRAYC, 2.6)
    for Y in range((y0 + 3) * S, 117 * S):
        cv.px((x0 + 8) * S, Y, m.GRAYC, 3.0)                                  # la corda
        cv.px((x0 + 8) * S + 1, Y, m.GRAYC, 1.6)
    cv.disc(x0 + 8.5, 119, 1.6, 2.6, m.GRAYC, lambda nx, ny: 3.4 - nx - ny)
    # marc d'alumini, amb el bisell d'1 px
    m.frame(cv, x0, y0, x1, y1, m.STEELB, 3.0)
    cv.hline(x0, x1, y0, m.STEELB, 4.0)
    cv.rect((x0 + x1) // 2 - 1, y0, (x0 + x1) // 2 + 1, y1, m.STEELB, 2.6)
    cv.vline((x0 + x1) // 2 - 1, y0, y1, m.STEELB, 3.4)
    for (a, b) in ((x0, x1),):
        for X in range(a * S, (b + 1) * S):
            cv.px(X, y0 * S, m.STEELB, 5.0)
            cv.px(X, (y0 + 3) * S - 1, m.STEELB, 1.0)
    cv.rect(x0 - 5, y1, x1 + 5, y1 + 4, m.STEELB, 3.2)
    for X in range((x0 - 5) * S, (x1 + 6) * S):
        cv.px(X, y1 * S, m.STEELB, 5.0)
        cv.px(X, y1 * S + 1, m.STEELB, 4.2)
        cv.px(X, (y1 + 5) * S - 1, m.STEELB, 0)


# ─── Monitors: codi «llegible» de 3×3 px reals, línies d'escaneig d'1 px, reflex al vidre ───

def _glyph(seed):
    return [[hr(seed, r, c) > 0.45 for c in range(3)] for r in range(3)]


def monitors_hd(cv, frame=0):
    for n, (x0, y0, x1, y1) in enumerate(m.MONITORS):
        obox(cv, x0, y0, x1, y1, m.PLASTIC, 1.6)
        SX0, SY0, SX1, SY1 = (x0 + 3) * S, (y0 + 3) * S, (x1 - 3) * S + 1, (y1 - 4) * S + 1
        for Y in range(SY0, SY1 + 1):
            for X in range(SX0, SX1 + 1):
                e = min(X - SX0, SX1 - X, Y - SY0, SY1 - Y)
                cv.px(X, Y, m.SCREEN, 1.25 + (0.25 if (Y + frame) % 2 == 0 else 0) - max(0, 0.5 - e * 0.1), lit=0)
        bright = 3.2 if n == 1 else 4.4
        for line, Y in enumerate(range(SY0 + 4, SY1 - 4, 5)):
            seed = line + frame + n * 11
            X = SX0 + 4 + int(hr(seed, 1) * 4) * 6
            end = SX0 + 4 + int(8 + hr(seed, 2) * (SX1 - SX0 - 14))
            word = 0
            while X + 3 < min(end, SX1 - 2):
                wl = 2 + int(hr(seed, word, 3) * 5)
                hot = hr(seed, word, 4) > 0.8                                   # una paraula clau, més viva
                for c in range(wl):
                    if X + 3 >= min(end, SX1 - 2):
                        break
                    g = _glyph((seed, word, c))
                    for r in range(3):
                        for cc in range(3):
                            if g[r][cc]:
                                cv.px(X + cc, Y + r, m.SCREEN, bright + (0.9 if hot else 0), lit=0)
                    X += 4
                X += 4
                word += 1
        if n != 1:                                                              # el cursor, al final
            cv.rect((SX0 + 8) / S, (SY1 - 8) / S, (SX0 + 11) / S, (SY1 - 5) / S, m.SCREEN, 5.4, lit=0)
        # reflex al vidre: una franja diagonal suau
        cv.tint(x0 + 3, y0 + 3, x1 - 3, y1 - 4, (200, 255, 240),
                lambda x, y, x0=x0, y0=y0: 0.07 * max(0, 1 - abs((x - x0) - (y - y0) * 0.7 - 14) / 6))
        cv.flat((x0 + x1) // 2, y1 - 1, (60, 200, 120))
        mx = (x0 + x1) // 2
        cv.rect(mx - 2, y1 + 1, mx + 1, m.DESK_Y - 1, m.STEELB, 2.4)
        cv.vline(mx - 2, y1 + 1, m.DESK_Y - 1, m.STEELB, 3.4)
        cv.rect(mx - 9, m.DESK_Y - 2, mx + 9, m.DESK_Y - 1, m.STEELB, 3.0)
    # el rètol «BCMU» i el mapa de xarxa, amb línies d'1 px i rètols diminuts als nodes
    cv.rect(356, 85, 400, 99, m.SCREEN, 2.4, lit=0)
    outline(cv, 356, 85, 400, 99, m.SCREEN)
    font = {'B': ['11110', '10001', '10001', '11110', '10001', '10001', '11110'],
            'C': ['01111', '10000', '10000', '10000', '10000', '10000', '01111'],
            'M': ['1000001', '1100011', '1010101', '1001001', '1000001', '1000001', '1000001'],
            'U': ['10001', '10001', '10001', '10001', '10001', '10001', '01110']}
    x = 362
    for ch in 'BCMU':
        for j, row in enumerate(font[ch]):
            for i, bit in enumerate(row):
                if bit == '1':
                    cv.put(x + i, 89 + j, m.SCREEN, 5.4, lit=0)
        x += len(font[ch][0]) + 2
    nodes = ((349, 109), (379, 105), (403, 112), (363, 125), (395, 129), (379, 137))
    for (ax, ay), (bx, by) in ((nodes[0], nodes[1]), (nodes[1], nodes[2]), (nodes[0], nodes[3]), (nodes[3], nodes[4]),
                               (nodes[2], nodes[4]), (nodes[4], nodes[5]), (nodes[3], nodes[5])):
        cv.line(ax, ay, bx, by, m.SCREEN, 4.6, lit=0, thin=True)
    for i, (x, y) in enumerate(nodes):
        if i == 5:
            cv.disc(x, y, 3, 3, [(60, 6, 10), (150, 20, 26), (240, 70, 60), (255, 160, 140)], 3.0, lit=0)
            cv.ring(x, y, 5, [(150, 20, 26), (240, 70, 60)], 1.0, lit=0, step=20)
        else:
            cv.disc(x, y, 2.5, 2.5, m.SCREEN, lambda nx, ny: 5.4 - (nx + ny) * 0.6, lit=0)
            for k in range(4):                                                  # el rètol del node
                if hr(i, k) > 0.3:
                    cv.px((x + 4) * S + k * 2, (y - 3) * S, m.SCREEN, 3.6, lit=0)
    cv.glow(377, 117, 93, (60, 200, 190), 0.14)


# ─── Cables del terra: de 3 px reals (no 6) ─────────────────────────────────

def cable_hd(cv, pts, ramp, lvl=2.0, thick=3):
    n = 600
    for i in range(n + 1):
        t = i / n
        p = list(pts)
        while len(p) > 1:
            p = [((a[0] * (1 - t) + b[0] * t), (a[1] * (1 - t) + b[1] * t)) for a, b in zip(p, p[1:])]
        X, Y = round((p[0][0] + 0.5) * S - 0.5), round((p[0][1] + 0.5) * S - 0.5)
        for d in range(thick):
            cv.px(X, Y + d, ramp, lvl + (0.9 if d == 0 else 0.3 if d == 1 else 0))
        cv.pxflat(X, Y + thick, ramp[0])


def floor_cables_hd(cv):
    dark = [(4, 4, 8), (20, 20, 28), (40, 40, 52), (70, 70, 84)]
    cable_hd(cv, [(320, 216), (333, 253), (440, 235), (507, 261), (560, 224), (533, 213)], dark, 1.6)
    cable_hd(cv, [(309, 213), (267, 267), (160, 240), (80, 259)], [(4, 4, 8), (20, 40, 70), (40, 80, 130), (80, 130, 180)], 1.6)
    cable_hd(cv, [(488, 213), (507, 243), (587, 248), (621, 213)], [(4, 4, 8), (80, 20, 24), (130, 36, 40), (180, 80, 80)], 1.6, thick=2)
    obox(cv, 614, 186, 624, 200, m.SHEET, 2.4)
    cv.flat(617, 192, (20, 16, 14))
    cv.flat(621, 192, (20, 16, 14))


# ─── Muntatge ───────────────────────────────────────────────────────────────

def draw(cv, detail):
    (wall_hd if detail else m.wall)(cv)
    (floor_hd if detail else m.floor)(cv)
    (window_hd if detail else m.window)(cv)
    m.poster(cv)
    m.neon_stripes(cv)
    m.mattress(cv)
    m.pizza_stack(cv)
    m.desk(cv)
    (monitors_hd if detail else m.monitors)(cv)
    m.desk_clutter(cv)
    m.router_shelf(cv)
    m.hatch(cv)
    (floor_cables_hd if detail else m.floor_cables)(cv)
    cv.darken(261, 213, 491, 221, 0.5)
    cv.darken(496, 211, 549, 219, 0.4)


def characters(img, scale):
    """L'Iri i la Diu (els sprites de 640, ×scale), amb la llum de la sala."""
    from hd640.preview import sprite
    art = Path(hd640.__file__).parent / 'characters'
    cl = m.GEOMETRIA['characterLights']
    cl = {**cl, 'lights': [{**l, 'x': l['x'] * scale, 'y': l['y'] * scale, 'radius': l['radius'] * scale} for l in cl['lights']]}
    for cid, (x, y) in sorted(m.GEOMETRIA['spawns'].items(), key=lambda kv: kv[1][1]):
        spr, (fx, fy) = sprite(cid, art)
        if scale != 1:
            spr = spr.transform((spr.width * scale, spr.height * scale), Image.Transform.EXTENT,
                                (0, 0, spr.width, spr.height), Image.Resampling.NEAREST)
        pos = ((x - fx) * scale, (y - fy) * scale)
        img.alpha_composite(llum.light_character(spr, pos, cl), pos)


def bar(img, scale):
    import hd640.gui as gui
    b = gui.verb_bar()
    if scale != 1:
        b = b.transform((b.width * scale, b.height * scale), Image.Transform.EXTENT, (0, 0, b.width, b.height),
                        Image.Resampling.NEAREST)
    img.paste(b, (0, hd640.BAR_Y * scale))


def up2(img):
    return img.transform((img.width * 2, img.height * 2), Image.Transform.EXTENT, (0, 0, img.width, img.height),
                         Image.Resampling.NEAREST)


def render(kind):
    if kind == '640':
        cv = Canvas(light=m.LIGHT)
        m._draw(cv)
        img = llum.apply(cv.img, m.FX)
        pc = Canvas(light=m.LIGHT, transparent=True)
        m._PROPS['caixa'](pc)
        img.alpha_composite(llum.apply(pc.img, m.FX_PROPS))
        characters(img, 1)
        bar(img, 1)
        return up2(img)
    cv = Canvas2x(light=m.LIGHT)
    draw(cv, kind == 'detall')
    img = llum.apply(cv.img, m.FX, scale=S)
    pc = Canvas2x(light=m.LIGHT, transparent=True)
    m._PROPS['caixa'](pc)
    img.alpha_composite(llum.apply(pc.img, m.FX_PROPS, scale=S))
    characters(img, S)
    bar(img, S)
    return img


def main():
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    imgs = {}
    for kind in ('640', 'auto', 'detall'):
        imgs[kind] = render(kind)
        imgs[kind].save(out / f'estudi_{kind}.png')
        print('✔', out / f'estudi_{kind}.png')
    # retalls a 1:1 (sense reescalar) de les tres versions, l'una sota l'altra
    for name, box in (('finestra', (60, 60, 700, 330)), ('pantalles', (520, 140, 1160, 410))):
        w, h = box[2] - box[0], box[3] - box[1]
        sheet = Image.new('RGBA', (w, h * 3 + 8), (255, 255, 255, 255))
        for i, kind in enumerate(('640', 'auto', 'detall')):
            sheet.paste(imgs[kind].crop(box), (0, i * (h + 4)))
        sheet.save(out / f'retall_{name}.png')
        print('✔', out / f'retall_{name}.png')


if __name__ == '__main__':
    main()
