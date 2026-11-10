"""
Pròleg · la cambra (Iri): la mateixa cambra de ressonància, de nit, quan salta l'alarma.
Les làmpades són apagades; el llum giratori de la consola escombra la sala amb dos feixos vermells
(un cap a la cambra, l'altre cap a la porta) i tot el que no toquen queda en penombra vermellosa.
"""
import math

from hd.pix import Light, B4, W, H, mix
from hd.rooms.fabrica_cambra import bg as cambra_bg, make_light, BEACON, palanca_alcada, frame_diff

BX, BY = BEACON[0], BEACON[1] + 3          # centre del vidre del llum giratori
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
    if d < 4:
        return 1.0
    a = math.degrees(math.atan2(dy, dx))
    v = 0.0
    for ang, half, k in beams:
        da = abs((a - ang + 180) % 360 - 180)
        h = half * soft
        if da < h:
            f = (1 - da / h) ** 0.6
            v = max(v, f * k / 3.2 * max(0.25, 1 - d / 520))
    return v


def _light(t=0.0):
    bm = beams_at(t)
    lt = make_light(alarm=True)
    lt.add(lambda x, y: beam(x, y, beams=bm) * 3.0)
    return lt


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
    for y in range(H):
        for x in range(W):
            r, g, b, a = cv.P[x, y]
            L = 0.34 * r + 0.5 * g + 0.16 * b
            hot = beam(x, y, beams=bm)
            red = (min(255, L * 1.35 + 8), L * 0.36 + 2, L * 0.38 + 6)
            if hot > 0.05:                                       # dins el feix, cap al taronja-rosat
                red = mix(red, (min(255, L * 1.5 + 60), L * 0.72 + 20, L * 0.5 + 12), min(1.0, hot))
            # la cambra conserva una mica del seu violeta
            keep = 0.3 if 214 <= x <= 304 and 34 <= y <= 138 else 0.08
            cv.P[x, y] = mix(red, (r, g, b), keep) + (255,)

    # ─── Feixos visibles a l'aire (pols de la fàbrica) ───────────────────────
    for y in range(0, 206):
        for x in range(W):
            v = beam(x, y, soft=0.85, beams=bm)
            if v <= 0:
                continue
            d = math.hypot(x - BX, y - BY)
            a = v * 0.42 * min(1.0, d / 30) * (0.8 + 0.2 * math.sin(d / 7.0 - ph * 3))   # la pols corre pel feix
            if a > B4[y & 3][x & 3] * 0.6:
                o = cv.P[x, y]
                cv.P[x, y] = mix(o, (255, 120, 90), min(0.55, a)) + (255,)

    # ─── El llum giratori: nucli encès, reflector i halo ─────────────────────
    cv.glow(BX, BY, 70, (255, 40, 30), 0.55 + 0.08 * (math.cos(ph * 2) - 1))   # el reflector mira i no mira
    cv.glow(BX, BY, 26, (255, 140, 100), 0.9)
    for y in range(BY - 7, BY + 8):
        for x in range(BX - 5, BX + 6):
            d = math.hypot((x - BX) / 5.2, (y - BY) / 7.2)
            if d < 1:
                cv.flat(x, y, mix((255, 240, 220), (255, 90, 60), d))
    # destells en creu (giren amb el llum)
    rot = math.radians(180 * tt)
    for i in range(1, 15):
        a = (1 - i / 15) ** 1.5
        pts = []
        for k in range(4):
            ca, sa = math.cos(rot + k * math.pi / 2), math.sin(rot + k * math.pi / 2)
            r = i + (4 if k % 2 == 0 else 6) + (2 * abs(ca * sa) if tt else 0)
            pts.append((round(BX + ca * r), round(BY + sa * r)))
        for px, py in pts:
            if 0 <= px < W and 0 <= py < H and a > B4[py & 3][px & 3] * 0.8:
                cv.flat(px, py, mix(cv.P[px, py], (255, 210, 180), a))
    # la gàbia del llum, retallada contra el vidre encès
    CAGE = (150, 40, 32)
    for k in (-4, 0, 4):
        for y in range(BY - 6 + abs(k) // 2, BY + 7 - abs(k) // 2):
            cv.flat(BX + k, y, CAGE)
    for x in range(BX - 5, BX + 6):
        cv.flat(x, BY, CAGE)
    for x in range(BX - 2, BX + 3):
        cv.flat(x, BY - 7, (110, 30, 26))
    # la campana vibra: arcs de so a banda i banda, que s'eixamplen i tornen
    ring_ = 0 if math.cos(ph * 12) > 0 else 1                  # (12 cops per bucle: a 24 fotogrames, un sí i un no)
    for r, col in ((10 + ring_, (255, 160, 130)), (13 + ring_ * 2, (200, 80, 60))):
        for dy in range(-3, 4):
            dx = round(math.sqrt(max(0, r * r - (dy * 2.2) ** 2)))
            cv.flat(116 + dx, 68 + dy, col)
            cv.flat(116 - dx, 68 + dy, col)

    # ─── Vinyeta forta: la nit es menja les vores ────────────────────────────
    for y in range(H):
        for x in range(W):
            d = math.hypot((x - 200) / 300, (y - 100) / 170)
            k = max(0.0, d - 0.55) * 1.3
            if k > 0:
                o = cv.P[x, y]
                f = max(0.0, 1 - k)
                cv.P[x, y] = (int(o[0] * f), int(o[1] * f), int(o[2] * f), 255)


PROPS = {}


# Animació de fons: el llum giratori fa mitja volta per bucle (els feixos escombren la sala, la pols hi
# corre i els destells giren) i la campana vibra. Cada fotograma: només el que canvia respecte de t = 0.
def _ambient_frames(n=24):
    from hd.pix import Canvas
    base = Canvas(light=LIGHT)
    bg(base)
    frames = []
    for i in range(n):
        cv = Canvas(light=_light(i / n))
        bg(cv, t=i / n)
        frames.append(frame_diff(base.img, cv.img))
    return frames


ANIMS = {'ambient': {'frames': _ambient_frames, 'frameDuration': 70}}
