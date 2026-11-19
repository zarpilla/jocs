"""
Pròleg · la cambra (Iri), pantalla sencera, cinemàtica. EN 3D (hd640/tres_d.py), a 1×.

La cambra de ressonància de nit, quan salta l'alarma. Un pla contrapicat, des de terra, arran de la cambra: la cambra
de vidre amb les bobines és a prop, a la dreta, gran i en 3/4 (el davant, el costat de vidre i el sòcol de franges),
amb els cables que pugen al sostre; la consola amb el llum giratori i la palanca alçada fa el pla mitjà; al fons, la
porta de les calderes, amb el foc a l'espiell. Les bigues del sostre, la canonada de coure i les juntes de les lloses
fugen cap a la porta: per allà entra l'Iri. En primer pla, a contrallum, un rotlle de cable a terra (a l'esquerra) i
un pilar de ferro (a la dreta), tallats per les vores.

Les làmpades són apagades: el llum giratori escombra la sala amb dos feixos vermells (un cap a la cambra, l'altre cap
a la porta), que es veuen a l'aire per la pols, i tot el que no toquen queda en penombra vermellosa (la passada de
color en pantalla de sempre). La cambra conserva una mica del seu violeta.

El dibuix pla de sempre (la paret, la porta, la consola, la cambra: fabrica_cambra_pla_comu.bg) en fa les textures.
L'antic dibuix pla del pròleg és a proleg_cambra_pla_comu.py (el fa servir la intro en vídeo, intro_animada.py).

Capes: `ambient` (el llum fa mitja volta per bucle, la pols corre pels feixos, la campana vibra, el foc es mou a
l'espiell), `iri_cambra` / `iri_entra` (l'Iri entra per l'esquerra, des de la porta, i s'atura davant de la cambra,
cada cop més gran), `iri_camp` (quieta, cada cop més il·luminada pel violeta, i el flaix blanc) i `camp` /
`camp_desperta` (arcs violeta entre les bobines, cada cop més sovint).

El món: x a la dreta, y amunt, z cap a la paret del fons (la paret és a z = 0); un píxel del dibuix pla fa U unitats.
"""
import functools
import json
import math
from pathlib import Path

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from PIL import Image

from hd.pix import Canvas, Light, B4, W, H, hr, mix, ramp, IRON, BRICK, COPPER, RUST, WALNUT
from hd640.tres_d import Camera, Escena, Llum
from hd640.rooms import fabrica_cambra_pla_comu as fc
from hd640.rooms.fabrica_cambra_pla_comu import frame_diff, palanca_alcada

STONE = fc.STONE
DARK = ramp((4, 3, 6), (8, 6, 10), (14, 10, 14), (22, 16, 20), (32, 24, 26), (46, 34, 34), n=7)
VIOLET = ramp((18, 8, 34), (40, 18, 70), (70, 34, 120), (110, 64, 180), (160, 110, 240), (210, 170, 255), n=8)

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)

U = 1.25                                   # unitats del món per píxel del dibuix pla
FLOOR_FY = 204                             # la y del dibuix pla on la paret toca a terra


def X(fx):
    return fx * U


def Y(fy):
    return (FLOOR_FY - fy) * U


ROOM_X0, ROOM_X1 = X(0), X(640)
CEIL = Y(0)
CONSOLE = (119, 60, 243, 204)              # el retall del dibuix pla: la consola, la palanca, el llum i la campana
CONSOLE_D = 86.0
CAMBRA = (265, 17, 425, 213)               # la cambra de ressonància
CAMBRA_D = 170.0
CAMBRA_Z = -40.0                           # separada de la paret

# ─── La càmera: contrapicada, des de terra ─────────────────────────────────
CAM = Camera(pos=(110.0, 38.0, -430.0), yaw=0.58, pitch=-0.12, f=290.0, centre=(320, 190))


def _proj(P):
    u, v, _ = CAM.projecta(P)
    return u, v


def cambra_p(fx, fy):
    """Un punt del dibuix pla de la cambra (fx, fy) al davant de la cambra al món."""
    return (X(fx), (CAMBRA[3] - fy) * U, CAMBRA_Z - CAMBRA_D)


def consola_p(fx, fy):
    return (X(fx), Y(fy) if fy <= FLOOR_FY else 0.0, -CONSOLE_D - 0.5)


BEACON_P = consola_p(fc.BEACON[0], fc.BEACON[1] + 4)
BELL_P = consola_p(155, 91)
CORE_P = (X(fc.CORE[0]), (CAMBRA[3] - fc.CORE[1]) * U, CAMBRA_Z - CAMBRA_D / 2)
BX, BY = (round(c) for c in _proj(BEACON_P))
BELL = tuple(round(c) for c in _proj(BELL_P))
# feixos: (angle en graus a la pantalla, mig angle d'obertura, força)
BEAMS = ((-12, 9, 3.2), (172, 11, 2.4))


# ─── Les textures: el dibuix pla, per trossos ───────────────────────────────

WALL_PARTS = ('sostre', 'paret', 'porta', 'pilars', 'avis', 'reixa', 'canonada', 'perill', 'pissarra')


@functools.lru_cache(maxsize=None)
def tex(kind, t=0.0):
    """El dibuix pla (de nit, amb l'alarma) d'un tros: 'paret', 'consola' o 'cambra', en un llenç transparent."""
    lt = fc.Baked(fc.make_light(alarm=True))
    lt.light.ambient = 0.6                                      # (la passada vermella ja enfosqueix)
    lt.light.vig = None
    lt.light.floor_fade = None
    cv = Canvas(light=lt, transparent=kind != 'paret')
    if kind == 'paret':
        fc.bg(cv, alarm=True, t=t, parts=WALL_PARTS)
    elif kind == 'consola':
        fc.bg(cv, alarm=True, t=t, parts=('consola', 'alarma', 'campana'))
        palanca_alcada(cv)
    else:
        fc.bg(cv, alarm=True, t=t, parts=('cambra',))
    return cv.img


# ─── Les textures procedurals ───────────────────────────────────────────────

def _lloses(s, t, P):
    """Lloses de pedra de 64 unitats, a trencajunts, amb esquerdes; la junta és d'un píxel de pantalla."""
    x, z = P[0], P[2]
    k = CAM.escala(P)
    row = math.floor(z / 64)
    xx = x + (32 if row % 2 else 0)
    col = math.floor(xx / 64)
    lvl = 2.0 + (hr(col, row, 1) - 0.5) * 0.6 + (hr(int(x // 3), int(z // 3), 5) - 0.5) * 0.25 * min(1, k)
    if (z % 64) * k < 1.0 or (xx % 64) * k < 1.0:
        lvl = 1.0
    elif hr(col, row, 4) > 0.75 and abs((xx % 64) - (z % 64) * 0.8 - 6) < 0.8 / max(k, 0.3):
        lvl -= 0.8                                                     # una esquerda en diagonal
    if z > -40:
        lvl -= (z + 40) / 40 * 1.0                                     # el racó de la paret
    return lvl


def _sostre(s, t, P):
    return 0.8 + (hr(int(P[0] // 40), int(P[2] // 60), 7) - 0.5) * 0.3


def _maons(s, t, P):
    k = CAM.escala(P)
    row = int(t // 10)
    xx = s + (row % 2) * 12
    lvl = 1.5 + (hr(int(xx // 24), row, 3) - 0.5) * 0.7
    if (t % 10) * k < 1.0 or (xx % 24) * k < 0.9:
        lvl = 0.7
    return lvl


def _ferro(base=2.0, rivets=22.0):
    def f(s, t, P):
        lvl = base + (hr(int(s // 3), int(t // 2), 31) - 0.5) * 0.2
        if rivets and (s % rivets) < 3 and (t % rivets) < 3:
            lvl += 1.8
        return lvl
    return f


def _vidre_costat(s, t, P):
    """El costat de vidre de la cambra: el violeta de dins, les bobines de coure a contrallum i un reflex."""
    h = (CAMBRA[3] - CAMBRA[1]) * U
    if t < 34 or t > h - 40 or s < 8 or s > CAMBRA_D - 8:
        return None
    lvl = 2.6 + (1 - abs(t - h * 0.5) / (h * 0.5)) * 1.6
    for cz in (CAMBRA_D * 0.3, CAMBRA_D * 0.5, CAMBRA_D * 0.7):
        if abs(s - cz) < 9 and 46 < t < h - 56:
            return ('coure', 2.2 + (1.0 if (t // 12) % 2 else 0) - abs(s - cz) / 9)
    if abs(s - t * 0.35 - 20) < 3:
        lvl += 1.6                                                     # el reflex del vidre
    return ('vidre', lvl)


# ─── L'escena ───────────────────────────────────────────────────────────────

def escena(cv):
    cv.S = 1
    llums = [Llum(BEACON_P, 760, 2.0), Llum(CORE_P, 340, 1.4), Llum((X(44), Y(114), -10), 220, 1.2)]
    e = Escena(cv, CAM, llums=llums, ambient=-0.6)
    z0, z1 = -1400.0, 0.0
    # el sostre, amb les bigues de ferro que fugen cap a la porta
    e.quad('sostre', (ROOM_X0 - 400, CEIL, z1), (ROOM_X1 + 400, CEIL, z1), (ROOM_X1 + 400, CEIL, z0),
           (ROOM_X0 - 400, CEIL, z0), ramp=IRON, lvl=_sostre, dues_cares=True)
    for x in range(-300, 1200, 170):
        e.caixa('bigues', x - 9, x + 9, CEIL - 24, CEIL, z0, z1, IRON, 1.6,
                cares={'sota': {'ramp': IRON, 'lvl': lambda s, t, P: 1.4 + (1.6 if (t % 30) < 3 and (s % 18) < 3 else 0)},
                       'esquerra': {'ramp': IRON, 'lvl': 2.4}, 'dreta': {'ramp': IRON, 'lvl': 1.0}})
    # les parets: la del fons (el dibuix pla) i les dels costats (maó)
    e.quad('paret', (ROOM_X0, CEIL, 0), (ROOM_X1, CEIL, 0), (ROOM_X1, 0, 0), (ROOM_X0, 0, 0),
           tex=(tex('paret'), (0, 0, 640, FLOOR_FY), 1))
    e.quad('paret_dre', (ROOM_X1 + 30, CEIL, 0), (ROOM_X1 + 30, CEIL, z0), (ROOM_X1 + 30, 0, z0), (ROOM_X1 + 30, 0, 0),
           ramp=BRICK, lvl=_maons)
    e.quad('paret_esq', (ROOM_X0 - 6, CEIL, z0), (ROOM_X0 - 6, CEIL, 0), (ROOM_X0 - 6, 0, 0), (ROOM_X0 - 6, 0, z0),
           ramp=BRICK, lvl=_maons)
    # el terra
    e.quad('terra', (ROOM_X0 - 400, 0, z1), (ROOM_X1 + 400, 0, z1), (ROOM_X1 + 400, 0, z0), (ROOM_X0 - 400, 0, z0),
           ramp=STONE, lvl=_lloses)
    e.foscor('ombra', (ROOM_X0 - 400, 0.5, 0), (ROOM_X1 + 400, 0.5, 0), (ROOM_X1 + 400, 0.5, -60),
             (ROOM_X0 - 400, 0.5, -60), lambda s, t: 0.5 * (1 - t / 60))
    # els pilars de ferro arran de paret
    for fx0, fx1 in ((84, 98), (597, 610)):
        e.caixa('pilars', X(fx0), X(fx1), 0, CEIL, -16, 0, IRON, 2.0,
                cares={'davant': {'ramp': IRON, 'lvl': _ferro(2.2, 18)}, 'dreta': {'ramp': IRON, 'lvl': 1.2},
                       'esquerra': {'ramp': IRON, 'lvl': 2.8}})
    # la canonada de coure, que baixa del sostre
    e.tub('canonada', (X(542), CEIL, -14), (X(542), 0, -14), 6.5, COPPER, 2.4, brides=70)
    # la galleda de sorra
    e.tub('galleda', (X(624), 0, -40), (X(624), 30 * U, -40), 13, RUST, 2.4, llum_dir=(-0.6, 0.4))
    # la consola: el davant és el dibuix pla (amb el llum giratori, la campana i la palanca, a sobre)
    cx0, cy0, cx1, cy1 = CONSOLE
    e.caixa('consola', X(cx0), X(cx1), 0, Y(112), -CONSOLE_D, 0, WALNUT, 2.2,
            cares={'dalt': {'ramp': IRON, 'lvl': _ferro(1.8, 0)}, 'dreta': {'ramp': WALNUT, 'lvl': 1.6},
                   'esquerra': {'ramp': WALNUT, 'lvl': 2.6},
                   'davant': {'ramp': WALNUT, 'lvl': 0.5}})
    e.quad('consola_davant', (X(cx0), Y(cy0), -CONSOLE_D - 0.5), (X(cx1), Y(cy0), -CONSOLE_D - 0.5),
           (X(cx1), 0, -CONSOLE_D - 0.5), (X(cx0), 0, -CONSOLE_D - 0.5), tex=(tex('consola'), CONSOLE, 1))
    # els cables, de la consola a la cambra, per terra
    for k in range(3):
        e.cable('cables', [(X(243) - 4, 20 + k * 6, -30 - k * 8), (X(255), 1.5, -70 - k * 10),
                           (X(265) - 10, 1.5, CAMBRA_Z - CAMBRA_D + 40 + k * 14), (X(268), 12, CAMBRA_Z - 60 + k * 14)],
                IRON, 1.4, gruix=3.2)
    # la cambra de ressonància, separada de la paret
    fx0, fy0, fx1, fy1 = CAMBRA
    hh = (fy1 - fy0) * U
    zf = CAMBRA_Z - CAMBRA_D
    e.caixa('cambra', X(fx0), X(fx1), 0, hh, zf, CAMBRA_Z, IRON, 2.0,
            cares={'dreta': {'ramp': IRON, 'lvl': 1.2}, 'esquerra': {'ramp': IRON, 'lvl': 2.2},
                   'dalt': {'ramp': IRON, 'lvl': 1.6}, 'sota': {'ramp': IRON, 'lvl': 0.4}})
    # el costat de l'esquerra (el de la càmera): el marc de ferro, el sòcol de franges i el vidre, amb les bobines de
    # coure a dins, a contrallum
    xl = X(fx0) - 0.5
    e.quad('cambra_costat', (xl, hh, CAMBRA_Z), (xl, hh, zf), (xl, 0, zf), (xl, 0, CAMBRA_Z), ramp=IRON,
           lvl=lambda s, t, P: _ferro(2.0, 20)(s, t, P) - (0.6 if t > hh - 24 else 0))
    e.quad('cambra_costat', (xl - 0.3, 30, CAMBRA_Z), (xl - 0.3, 30, zf), (xl - 0.3, 0, zf), (xl - 0.3, 0, CAMBRA_Z),
           ramp=fc.WARN, lvl=lambda s, t, P: 3.4 if ((s + t) // 12) % 2 else -2.0)
    g0, g1 = 36.0, hh - 42
    e.quad('cambra_vidre', (xl - 0.4, hh - g0, CAMBRA_Z - 12), (xl - 0.4, hh - g0, zf + 12), (xl - 0.4, hh - g1, zf + 12),
           (xl - 0.4, hh - g1, CAMBRA_Z - 12), ramp=VIOLET,
           lvl=lambda s, t, P: 1.8 + (1 - abs(t - (g1 - g0) / 2) / ((g1 - g0) / 2)) * 1.8
           + (1.8 if abs(s - t * 0.35 - 14) < 3 else 0))
    for cz in (0.3, 0.52, 0.74):
        z = CAMBRA_Z - CAMBRA_D * cz
        e.quad('cambra_vidre', (xl - 0.6, hh - 50, z + 9), (xl - 0.6, hh - 50, z - 9), (xl - 0.6, 58, z - 9),
               (xl - 0.6, 58, z + 9), ramp=COPPER,
               lvl=lambda s, t, P: 1.4 + (1.0 if (t // 13) % 2 else 0) - abs(s - 9) / 9 * 1.2)
    e.quad('cambra_davant', (X(fx0), hh, zf - 0.5), (X(fx1), hh, zf - 0.5), (X(fx1), 0, zf - 0.5),
           (X(fx0), 0, zf - 0.5), tex=(tex('cambra'), CAMBRA, 1))
    # els cables i les canonades que pugen de la cambra al sostre
    for fx, dz in ((282, -30), (297, -90), (397, -40), (412, -120)):
        e.cable('cambra_cables', [(X(fx), hh, zf + 20 - dz * 0.2), (X(fx) + 6, hh + 30, zf - dz * 0.3),
                                  (X(fx) + 2, CEIL - 20, zf - dz)], IRON, 1.6, gruix=4)
    # el primer pla, a contrallum: un cable gruixut per terra
    # un pilar de ferro, a prop, a l'esquerra (tallat per dalt i per baix)
    e.caixa('primer_pla', 60, 76, 0, CEIL, -322, -306, DARK, 1.2,
            cares={'dreta': {'ramp': DARK, 'lvl': lambda s, t, P: 2.2 + (1.8 if (t % 24) < 3 and abs(s - 8) < 2 else 0)
                             + (1.4 if s > 13 else 0)},
                   'davant': {'ramp': DARK, 'lvl': lambda s, t, P: 1.0 + (1.2 if s > 13 else 0)}})
    e.cable('primer_pla', [(70, 2, -380), (110, 1.5, -330), (150, 1.5, -270), (170, 1.5, -200),
                           (X(119) + 30, 1.5, -CONSOLE_D - 10)], DARK, 2.0, gruix=4)
    return e


# ─── La passada de pantalla: tot vermell d'alarma ───────────────────────────

def beams_at(t=0.0):
    """Els feixos en el moment t (0..1) de l'animació: el llum fa mitja volta (en sentit horari) i, mentre gira, cada
    feix pren a poc a poc la forma de l'altre; així a t = 1 tot torna a ser com a t = 0."""
    if not t:
        return BEAMS
    s = (1 - math.cos(math.pi * t)) / 2
    (a0, h0, k0), (a1, h1, k1) = BEAMS
    return ((a0 + 180 * t, h0 + (h1 - h0) * s, k0 + (k1 - k0) * s),
            (a1 + 180 * t, h1 + (h0 - h1) * s, k1 + (k0 - k1) * s))


def beam(x, y, soft=1.0, beams=BEAMS):
    """0..1: com de dins d'un feix és (x, y) de la pantalla, amb caiguda per distància."""
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
            v = max(v, f * k / 3.2 * max(0.25, 1 - d / 700))
    return v


def vermell(cv, e, t=0.0):
    ph = 2 * math.pi * t
    bm = beams_at(t)
    P = cv.P
    keep_ids = {i for i, s in enumerate(e.ids) if s in ('cambra_davant', 'cambra_vidre')}
    amo = e.amo
    for y in range(H):
        for x in range(W):
            r, g, b, a = P[x, y]
            L = 0.34 * r + 0.5 * g + 0.16 * b
            hot = beam(x, y, beams=bm)
            red = (min(255, L * 1.35 + 8), L * 0.36 + 2, L * 0.38 + 6)
            if hot > 0.05:                                       # dins el feix, cap al taronja-rosat
                red = mix(red, (min(255, L * 1.5 + 60), L * 0.72 + 20, L * 0.5 + 12), min(1.0, hot))
            keep = 0.3 if amo[y * W + x] in keep_ids else 0.08   # la cambra conserva una mica del seu violeta
            o = mix(red, (r, g, b), keep)
            v = beam(x, y, soft=0.85, beams=bm)                 # els feixos, a l'aire
            if v > 0:
                d = math.hypot(x - BX, y - BY)
                a_ = v * 0.42 * min(1.0, d / 40) * (0.8 + 0.2 * math.sin(d / 9.3 - ph * 3))
                if a_ > B4[y & 3][x & 3] * 0.6:
                    o = mix(o, (255, 120, 90), min(0.55, a_))
            P[x, y] = o + (255,)


def llum_giratori(cv, t=0.0):
    """El llum giratori: el nucli encès, el reflector, els destells en creu (giren) i la gàbia; la campana vibra."""
    ph = 2 * math.pi * t
    k = CAM.escala(BEACON_P)
    cv.glow(BX, BY, 110, (255, 40, 30), 0.55 + 0.08 * (math.cos(ph * 2) - 1))
    cv.glow(BX, BY, 40, (255, 140, 100), 0.9)
    rx, ry = 6.9 * k / U * 1.0, 9.6 * k / U * 1.0
    for y in range(int(BY - ry - 1), int(BY + ry + 2)):
        for x in range(int(BX - rx - 1), int(BX + rx + 2)):
            d = math.hypot((x - BX) / rx, (y - BY) / ry)
            if d < 1:
                cv.flat(x, y, mix((255, 240, 220), (255, 90, 60), d))
    rot = math.radians(180 * t)
    for i in range(1, 22):
        a = (1 - i / 22) ** 1.5
        for kk in range(4):
            ca, sa = math.cos(rot + kk * math.pi / 2), math.sin(rot + kk * math.pi / 2)
            r = i + (5 if kk % 2 == 0 else 8) + (2.7 * abs(ca * sa) if t else 0)
            px, py = round(BX + ca * r), round(BY + sa * r)
            if 0 <= px < W and 0 <= py < H and a > B4[py & 3][px & 3] * 0.8:
                cv.flat(px, py, mix(cv.P[px, py], (255, 210, 180), a))
    CAGE, CAGE_D = (150, 40, 32), (110, 30, 26)
    for dx in (-round(rx * 0.72), 0, round(rx * 0.72)):
        for y in range(round(BY - ry * 0.85 + abs(dx) / 2), round(BY + ry * 0.9 - abs(dx) / 2)):
            cv.flat(BX + dx, y, CAGE)
    for x in range(round(BX - rx), round(BX + rx) + 1):
        cv.flat(x, BY, CAGE)
    for x in range(round(BX - rx * 0.45), round(BX + rx * 0.45) + 1):
        cv.flat(x, round(BY - ry * 0.95), CAGE_D)
        cv.flat(x, round(BY - ry * 1.05), CAGE_D)
    ring_ = 0 if math.cos(ph * 12) > 0 else 1
    cx, cy = BELL
    kb = CAM.escala(BELL_P) / U
    for r, col in ((13 * kb + ring_, (255, 160, 130)), (17 * kb + ring_ * 3, (200, 80, 60))):
        for dy in range(-round(4 * kb), round(4 * kb) + 1):
            dx = round(math.sqrt(max(0, r * r - (dy * 2.2) ** 2)))
            cv.flat(cx + dx, cy + dy, col)
            cv.flat(cx - dx, cy + dy, col)


def vinyeta(cv):
    P = cv.P
    for y in range(H):
        for x in range(W):
            d = math.hypot((x - 330) / 400, (y - 170) / 227)
            k = max(0.0, d - 0.55) * 1.3
            if k > 0:
                o = P[x, y]
                f = max(0.0, 1 - k)
                P[x, y] = (int(o[0] * f), int(o[1] * f), int(o[2] * f), 255)


@functools.lru_cache(maxsize=None)
def _escena_base():
    cv = Canvas(light=LIGHT)
    e = escena(cv)
    return cv.img.copy(), e


def frame(t=0.0):
    img, e = _escena_base()
    cv = Canvas(light=LIGHT, img=img.copy())
    if t:
        # el foc de l'espiell, les agulles i el camp que ondula (el dibuix pla al seu moment), per les mateixes
        # superfícies
        cv.img.alpha_composite(e.capa(tex('paret', t), sids={'paret'}))
        cv.img.alpha_composite(e.capa(tex('consola', t), sids={'consola_davant'}))
        cv.img.alpha_composite(e.capa(tex('cambra', t), sids={'cambra_davant'}))
        cv.P = cv.img.load()
    vermell(cv, e, t)
    llum_giratori(cv, t)
    vinyeta(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def base_img():
    return frame(0.0)


def bg(cv, t=0.0):
    cv.img.paste(frame(t) if t else base_img())
    cv.P = cv.img.load()


def _ambient_frames(n=24):
    base = base_img()
    return [frame_diff(base, frame(i / n)) for i in range(n)]


PROPS = {}


# ─── L'Iri i el camp (capes del pròleg) ──────────────────────────────────────
# «iri_entra»: l'Iri (el seu sprite, a l'escala que toca a cada distància, tenyit amb el vermell de la sala) entra per
# l'esquerra, des de la porta del fons, i camina en diagonal fins davant de la cambra, cada cop més gran; s'hi atura
# de cara al vidre. «camp_desperta»: el camp es desperta, amb arcs violeta entre les bobines cada cop més sovint (el
# dibuix pla dels arcs, projectat pel davant de la cambra). Alhora, «iri_camp»: l'Iri, quieta, cada cop més
# il·luminada pel violeta pel costat de la cambra, i al final un flaix blanc ho tapa tot (es queda blanc: la sala
# següent hi entra amb la fosa). Sense bucle; fins que la narració les engega, les capes són buides.

ART = Path(__file__).resolve().parents[3] / 'placeholder-art'
WALK_LEN = 4.2                   # de fora de la pantalla fins davant de la cambra
FIELD_LEN = 4.2                  # el camp, fins al flaix
FIELD_DT = 1 / 12
ZT = 0.1
IRI_FROM = (X(44), 0.0, -24.0)
IRI_STOP = (310.0, 0.0, -292.0)        # davant del vidre, tal com la veu la càmera


@functools.lru_cache(maxsize=None)
def _sheet(tag):
    meta = json.loads((ART / 'iri' / 'iri.json').read_text())
    feet = json.loads((ART / 'iri' / 'iri.character.json').read_text())['feet']
    sheet = Image.open(ART / 'iri' / 'iri.png').convert('RGBA')
    frames = list(meta['frames'].values())
    tg = next(x for x in meta['meta']['frameTags'] if x['name'] == tag)
    out = []
    for i in range(tg['from'], tg['to'] + 1):
        f = frames[i]['frame']
        out.append(sheet.crop((f['x'], f['y'], f['x'] + f['w'], f['y'] + f['h'])))
    return out, (feet['x'], feet['y'])


def _ease(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


def iri_at(t):
    """→ (punt del món, etiqueta, fotograma, mirall?) al segon `t`: surt de la porta i camina en diagonal cap a la
    càmera i a la dreta (WalkDL de mirall) fins davant del vidre, i s'hi gira (IdleUL de mirall: d'esquena, en 3/4)."""
    turn = WALK_LEN - 0.3
    if t < turn:
        u = t / turn
        P = tuple(a + (b - a) * (u * 0.85 + 0.15 * _ease(u)) for a, b in zip(IRI_FROM, IRI_STOP))
        return P, 'WalkDL', int(t / ZT), True
    if t < WALK_LEN:
        return IRI_STOP, 'IdleDL', 0, True
    return IRI_STOP, 'IdleUL', int((t - WALK_LEN) / 0.8), True


def redden(rgb, x, y, k_field=0.0):
    """El color d'un píxel de l'Iri amb la llum de la sala (el vermell de la passada de pantalla) i, amb `k_field`,
    el violeta del camp."""
    r, g, b = rgb
    L = (0.34 * r + 0.5 * g + 0.16 * b) * 0.62
    red = (min(255, L * 1.35 + 8), L * 0.36 + 2, L * 0.38 + 6)
    hot = beam(x, y)
    if hot > 0.05:
        red = mix(red, (min(255, L * 1.5 + 60), L * 0.72 + 20, L * 0.5 + 12), min(1.0, hot))
    o = mix(red, (r, g, b), 0.08)
    if k_field > 0:
        o = mix(o, (min(255, L * 1.1 + 70), L * 0.8 + 40, min(255, L * 1.4 + 90)), 0.55 * k_field)
    d = math.hypot((x - 330) / 400, (y - 170) / 227)
    f = max(0.0, 1 - max(0.0, d - 0.55) * 1.3)
    return (int(o[0] * f), int(o[1] * f), int(o[2] * f))


TAPA = {'primer_pla'}            # (davant de l'Iri només hi ha el primer pla)


def draw_iri(cv, t, k_field=0.0):
    P, tag, step, flip = iri_at(t)
    frames, (fx, fy) = _sheet(tag)
    img = frames[step % len(frames)]
    if flip:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
        fx = img.width - fx
    k = CAM.escala(P)
    u, v, _ = CAM.projecta(P)
    w, h = max(1, round(img.width * k)), max(1, round(img.height * k))
    im = img.resize((w, h), Image.Resampling.BOX)
    ox, oy = round(u - fx * k), round(v - fy * k)
    _, e = _escena_base()
    # l'ombra de contacte
    rw = 15 * k
    for dy in range(-round(3 * k), round(3 * k) + 1):
        for dx in range(-round(rw), round(rw) + 1):
            X_, Y_ = round(u + dx), round(v + dy)
            if 0 <= X_ < W and 0 <= Y_ < H and (dx / (rw + 0.5)) ** 2 + (dy / (3 * k + 0.5)) ** 2 < 1:
                if e.ids[e.amo[Y_ * W + X_]] not in TAPA and B4[Y_ & 3][X_ & 3] < 0.7:
                    o = cv.P[X_, Y_]
                    cv.P[X_, Y_] = (int(o[0] * 0.5), int(o[1] * 0.5), int(o[2] * 0.5), 255)
    src = im.load()
    for y in range(h):
        for x in range(w):
            p = src[x, y]
            if p[3] < 110:
                continue
            X_, Y_ = ox + x, oy + y
            if not (0 <= X_ < W and 0 <= Y_ < H) or e.ids[e.amo[Y_ * W + X_]] in TAPA:
                continue
            if t < 0.5 and B4[Y_ & 3][X_ & 3] > t / 0.5:
                continue                                                   # surt de la foscor de la porta
            # d'esquena al vidre: el violeta la retalla (la vora) i li tenyeix una mica tot el cos
            edge = x == 0 or y == 0 or src[x - 1, y][3] < 110 or (x + 1 < w and src[x + 1, y][3] < 110) \
                or src[x, y - 1][3] < 110
            side = k_field * (1.0 if edge else 0.35)
            cv.flat(X_, Y_, redden(p[:3], X_, Y_, side))


def field_level(u):
    """Com de despert és el camp (0..1) a la fracció `u` del seu tros."""
    u = max(0.0, min(1.0, u))
    return (u * u * (3 - 2 * u)) ** 1.4


def arc(cv, x0, y0, x1, y1, seed, k):
    """Un arc elèctric en ziga-zaga de (x0, y0) a (x1, y1), al dibuix pla."""
    n = max(3, round(abs(x1 - x0) / 5))
    pts = [(x0, y0)]
    for i in range(1, n):
        u = i / n
        pts.append((x0 + (x1 - x0) * u + (hr(i, seed, 1) - 0.5) * 3, y0 + (y1 - y0) * u + (hr(i, seed, 2) - 0.5) * 9))
    pts.append((x1, y1))
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        steps = max(1, round(max(abs(bx - ax), abs(by - ay))))
        for s_ in range(steps + 1):
            px, py = round(ax + (bx - ax) * s_ / steps), round(ay + (by - ay) * s_ / steps)
            if 0 <= px < W and 0 <= py < H:
                cv.flat(px, py, (250, 236, 255))
                for dx, dy in ((0, -1), (0, 1)):
                    if cv.P[px + dx, py + dy][3] == 0:
                        cv.P[px + dx, py + dy] = (190, 120, 255, int(255 * min(1.0, 0.7 * k)))


def field_flat(k, f):
    """El camp despert `k` (0..1), al fotograma `f`, al dibuix pla de la cambra: el vidre tenyit de violeta i els
    arcs entre les bobines (transparent on no hi ha res)."""
    cv = Canvas(transparent=True)
    if k <= 0:
        return cv.img
    gx0, gx1, gy0, gy1 = fc.GLASS
    for y in range(gy0, gy1 + 1):
        for x in range(gx0, gx1 + 1):
            a = 0.42 * k * (1 - abs(x - 345) / 70)
            if a > 0:
                cv.P[x, y] = (170, 110, 255, int(255 * min(1.0, a)))
    n = int(k * 7 + hr(f, 3) * 2 * k)                     # de tant en tant al principi, a dojo al final
    for i in range(n):
        side = hr(f, i, 4)
        y = round(60 + hr(f, i, 5) * 110)
        dy = round((hr(f, i, 6) - 0.5) * 10)
        if side < 0.45:
            arc(cv, 323, y, 337, y + dy, f * 13 + i, k)
        elif side < 0.9:
            arc(cv, 353, y, 368, y + dy, f * 13 + i, k)
        elif k > 0.5:                                      # i, al final, fins al vidre
            if hr(f, i, 7) < 0.5:
                arc(cv, gx0 + 2, y, 308, y + 6, f * 13 + i, k)
            else:
                arc(cv, 383, y, gx1 - 2, y - 6, f * 13 + i, k)
    return cv.img


def field(cv, k, f):
    """El camp, damunt la pantalla: el dibuix pla projectat pel davant de la cambra i la claror violeta, que
    s'escampa pel terra i pel costat de vidre."""
    if k <= 0:
        return
    _, e = _escena_base()
    cv.img.alpha_composite(e.capa(field_flat(k, f), sids={'cambra_davant'}))
    cv.P = cv.img.load()
    u, v = _proj(CORE_P)
    cv.glow(u, v, 90 + 70 * k, (190, 130, 255), 0.22 * k)
    u2, v2 = _proj((X(345), 0, CAMBRA_Z - CAMBRA_D - 60))
    cv.glow(u2, v2, 80 + 60 * k, (170, 110, 255), 0.2 * k)


def _layer(draw):
    base = base_img()
    cv = Canvas(light=LIGHT, img=base.copy())
    draw(cv)
    return frame_diff(base, cv.img)


def _empty():
    return [Canvas(transparent=True).img]


def _iri_entra():
    return [_layer(lambda cv: draw_iri(cv, i * ZT)) for i in range(round(WALK_LEN / ZT) + 2)]


def _flash():
    """El flaix: blanc tramat (B4) cada cop més ple, i blanc del tot."""
    out = []
    for k in (0.25, 0.5, 0.75):
        img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        P = img.load()
        for y in range(H):
            for x in range(W):
                if B4[y & 3][x & 3] < k:
                    P[x, y] = (255, 255, 255, 255)
        out.append(img)
    out.append(Image.new('RGBA', (W, H), (255, 255, 255, 255)))
    return out


def _iri_camp():
    # (la capa de l'Iri és la de dalt: el flaix hi va al final, perquè ho tapi tot)
    n = round(FIELD_LEN / FIELD_DT) + 1
    return [_layer(lambda cv: draw_iri(cv, WALK_LEN + 1 + i * FIELD_DT, k_field=field_level(i / (n - 1))))
            for i in range(n)] + _flash()


def _camp():
    n = round(FIELD_LEN / FIELD_DT) + 1
    return [_layer(lambda cv: field(cv, field_level(i / (n - 1)), i)) for i in range(n)]


ANIMS = {
    'ambient': {'frames': _ambient_frames, 'frameDuration': 70},
    'iri_cambra': {'frames': _empty, 'frameDuration': 1000, 'loop': False, 'zIndex': 3},
    'iri_entra': {'frames': _iri_entra, 'frameDuration': 100, 'loop': False, 'prop': 'iri_cambra'},
    'iri_camp': {'frames': _iri_camp, 'frameDuration': round(FIELD_DT * 1000), 'loop': False, 'prop': 'iri_cambra'},
    'camp': {'frames': _empty, 'frameDuration': 1000, 'loop': False, 'zIndex': 2},
    'camp_desperta': {'frames': _camp, 'frameDuration': round(FIELD_DT * 1000), 'loop': False, 'prop': 'camp'},
}
