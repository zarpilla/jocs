"""
Pròleg · la cambra (Iri), a 640×360: la composició de hd/rooms/proleg_cambra.py ×4/3, dibuixada de nou sobre la
cambra de hd640/rooms/fabrica_cambra.py.
La mateixa cambra de ressonància, de nit, quan salta l'alarma. Les làmpades són apagades; el llum giratori de
la consola escombra la sala amb dos feixos vermells (un cap a la cambra, l'altre cap a la porta) i tot el que
no toquen queda en penombra vermellosa.
"""
import math
from functools import lru_cache

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from hd.pix import Canvas, B4, W, H, mix
from hd640.rooms.fabrica_cambra import (bg as cambra_bg, make_light, Baked, BEACON, GLASS, palanca_alcada,
                                        frame_diff)

BX, BY = BEACON[0], BEACON[1] + 4          # centre del vidre del llum giratori
BELL = (155, 91)                           # la campana
# feixos: (angle en graus, mig angle d'obertura, força)
BEAMS = ((-16, 9, 3.2), (164, 11, 2.4))


def beams_at(t=0.0):
    """Els feixos en el moment t (0..1) de l'animació: el llum fa mitja volta (en sentit horari) i, mentre
    gira, cada feix pren a poc a poc la forma de l'altre; així a t = 1 tot torna a ser com a t = 0."""
    if not t:
        return BEAMS
    s = (1 - math.cos(math.pi * t)) / 2
    (a0, h0, k0), (a1, h1, k1) = BEAMS
    return ((a0 + 180 * t, h0 + (h1 - h0) * s, k0 + (k1 - k0) * s),
            (a1 + 180 * t, h1 + (h0 - h1) * s, k1 + (k0 - k1) * s))


def beam(x, y, soft=1.0, beams=BEAMS):
    """0..1: com de dins d'un feix és (x, y), amb caiguda per distància."""
    dx, dy = x - BX, y - BY
    d = math.hypot(dx, dy)
    if d < 5:
        return 1.0
    a = math.degrees(math.atan2(dy, dx))
    v = 0.0
    for ang, half, k in beams:
        da = abs((a - ang + 180) % 360 - 180)
        h = half * soft
        if da < h:
            f = (1 - da / h) ** 0.6
            v = max(v, f * k / 3.2 * max(0.25, 1 - d / 693))
    return v


def _light(t=0.0):
    bm = beams_at(t)
    lt = make_light(alarm=True)
    lt.add(lambda x, y: beam(x, y, beams=bm) * 3.0)
    return Baked(lt)


LIGHT = _light()


def bg(cv, t=0.0):
    """`t` (0..1): moment de l'animació (el llum gira); amb t = 0 surt el fons quiet. El Canvas ha de
    portar la llum del mateix moment (`_light(t)`)."""
    tt = t
    ph = 2 * math.pi * tt
    bm = beams_at(tt)
    cambra_bg(cv, alarm=True, t=tt)
    palanca_alcada(cv)                       # l'alarma sona: la palanca encara és alçada

    # ─── Tot vermell: la llum que queda és la de l'alarma ────────────────────
    # (i alhora els feixos visibles a l'aire: la pols de la fàbrica, que hi corre)
    GX0, GX1, GY0, GY1 = GLASS
    P = cv.P
    for y in range(H):
        for x in range(W):
            r, g, b, a = P[x, y]
            L = 0.34 * r + 0.5 * g + 0.16 * b
            hot = beam(x, y, beams=bm)
            red = (min(255, L * 1.35 + 8), L * 0.36 + 2, L * 0.38 + 6)
            if hot > 0.05:                                       # dins el feix, cap al taronja-rosat
                red = mix(red, (min(255, L * 1.5 + 60), L * 0.72 + 20, L * 0.5 + 12), min(1.0, hot))
            # la cambra conserva una mica del seu violeta
            keep = 0.3 if GX0 - 3 <= x <= GX1 + 2 and GY0 <= y <= GY1 else 0.08
            o = mix(red, (r, g, b), keep)
            if y < 275:
                v = beam(x, y, soft=0.85, beams=bm)
                if v > 0:
                    d = math.hypot(x - BX, y - BY)
                    a = v * 0.42 * min(1.0, d / 40) * (0.8 + 0.2 * math.sin(d / 9.3 - ph * 3))
                    if a > B4[y & 3][x & 3] * 0.6:
                        o = mix(o, (255, 120, 90), min(0.55, a))
            P[x, y] = o + (255,)

    # ─── El llum giratori: nucli encès, reflector i halo ─────────────────────
    cv.glow(BX, BY, 93, (255, 40, 30), 0.55 + 0.08 * (math.cos(ph * 2) - 1))   # el reflector mira i no mira
    cv.glow(BX, BY, 35, (255, 140, 100), 0.9)
    for y in range(BY - 10, BY + 11):
        for x in range(BX - 7, BX + 8):
            d = math.hypot((x - BX) / 6.9, (y - BY) / 9.6)
            if d < 1:
                cv.flat(x, y, mix((255, 240, 220), (255, 90, 60), d))
    # destells en creu (giren amb el llum)
    rot = math.radians(180 * tt)
    for i in range(1, 19):
        a = (1 - i / 19) ** 1.5
        pts = []
        for k in range(4):
            ca, sa = math.cos(rot + k * math.pi / 2), math.sin(rot + k * math.pi / 2)
            r = i + (5 if k % 2 == 0 else 8) + (2.7 * abs(ca * sa) if tt else 0)
            pts.append((round(BX + ca * r), round(BY + sa * r)))
        for px, py in pts:
            if 0 <= px < W and 0 <= py < H and a > B4[py & 3][px & 3] * 0.8:
                cv.flat(px, py, mix(cv.P[px, py], (255, 210, 180), a))
    # la gàbia del llum, retallada contra el vidre encès
    CAGE, CAGE_D = (150, 40, 32), (110, 30, 26)
    for k in (-5, 0, 5):
        for y in range(BY - 8 + abs(k) // 2, BY + 9 - abs(k) // 2):
            cv.flat(BX + k, y, CAGE)
    for x in range(BX - 7, BX + 8):
        cv.flat(x, BY, CAGE)
    for x in range(BX - 3, BX + 4):
        cv.flat(x, BY - 9, CAGE_D)
        cv.flat(x, BY - 10, CAGE_D)
    # la campana vibra: arcs de so a banda i banda, que s'eixamplen i tornen
    ring_ = 0 if math.cos(ph * 12) > 0 else 1                  # (12 cops per bucle: a 24 fotogrames, un sí i un no)
    cx, cy = BELL
    for r, col in ((13 + ring_, (255, 160, 130)), (17 + ring_ * 3, (200, 80, 60))):
        for dy in range(-4, 5):
            dx = round(math.sqrt(max(0, r * r - (dy * 2.2) ** 2)))
            cv.flat(cx + dx, cy + dy, col)
            cv.flat(cx - dx, cy + dy, col)

    # ─── Vinyeta forta: la nit es menja les vores ────────────────────────────
    for y in range(H):
        for x in range(W):
            d = math.hypot((x - 267) / 400, (y - 133) / 227)
            k = max(0.0, d - 0.55) * 1.3
            if k > 0:
                o = P[x, y]
                f = max(0.0, 1 - k)
                P[x, y] = (int(o[0] * f), int(o[1] * f), int(o[2] * f), 255)


PROPS = {}


# Animació de fons: el llum giratori fa mitja volta per bucle (els feixos escombren la sala, la pols hi
# corre i els destells giren) i la campana vibra. Cada fotograma: només el que canvia respecte de t = 0.
@lru_cache(maxsize=None)
def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv.img


def _ambient_frames(n=24):
    base = _base()
    frames = []
    for i in range(n):
        cv = Canvas(light=_light(i / n))
        bg(cv, t=i / n)
        frames.append(frame_diff(base, cv.img))
    return frames


ANIMS = {'ambient': {'frames': _ambient_frames, 'frameDuration': 70}}
