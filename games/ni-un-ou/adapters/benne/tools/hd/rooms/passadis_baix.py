"""
El passadís de la coberta de sota: estret, verd i de ferro. D'esquerra a dreta, la porta del camarot de l'Iri,
la porta estanca de la sala de màquines, la del pallol, l'escotilla de la sala de bombes (a terra) i l'escala de
mà que puja a la coberta principal.
"""
import math

from hd.pix import Canvas, Light, W, H, hr, mix, B4, WALNUT
from hd.rooms.arenga import (WALL, ENG, DECK, CAB, DARK, WHITEP, YELL, REDP, SEAG, FUEL, BRASS, WARM, FLOOR_Y,
                             BOTTOM, box, rrect, bolt, hpipe, vpipe, glow)
from hd.rooms.comu import _diff, text, text_width
from hd.rooms import sota
from hd.rooms.camarot_iri import PAINT

LAMPS = (150, 330)

LIGHT = Light(ambient=-0.45, vignette=(48, 28), floor_fade=None)
LIGHT.point(150, 26, r=150, k=2.5, squash=1.05, down=True, power=1.5)
LIGHT.point(330, 26, r=150, k=2.4, squash=1.05, down=True, power=1.5)
LIGHT.point(446, 24, r=110, k=1.6, squash=0.9, power=1.6)        # la llum de la coberta principal, per l'escala

CAMAROT = (22, 64, 68, FLOOR_Y)
MAQUINES = (112, 62, 168, FLOOR_Y)
PALLOL = (212, 64, 258, FLOOR_Y)
HATCH = [(300, 168), (360, 168), (366, 186), (294, 186)]


# ─── Paret, sostre, tubs ────────────────────────────────────────────────────

def walls(cv):
    sota.plate_wall(cv, 0, W - 1, frames=64, frame0=-30, seams=(56, 112), rust=30, seed=11)
    sota.ceiling(cv, beam0=-30)
    # aigua de mar i gasoil, com a la sala de màquines (hi van a parar)
    hpipe(cv, 0, W - 1, 36, 3, SEAG, 3.0, bands=range(40, W, 52), band_ramp=WHITEP)
    hpipe(cv, 0, 404, 46, 2, FUEL, 3.0, bands=range(66, W, 52), band_ramp=YELL)
    for x in range(20, 404, 48):
        cv.vline(x, 31, 49, CAB, 2.0)
        cv.vline(x + 1, 31, 49, CAB, 3.4)
    # un tub que baixa fins a terra entre el pallol i l'escotilla
    vpipe(cv, 280, 36, FLOOR_Y + 2, 2, SEAG, 2.8, bands=(80, 128), band_ramp=WHITEP)
    cv.disc(280, 36, 3, 3, SEAG, lambda nx, ny: 3.4 - nx - ny)


def cabin_door(cv):
    """La porta del camarot: una porta de planxa pintada, amb reixeta a baix i número de llautó."""
    x0, y0, x1, y1 = CAMAROT
    sota.door_frame(cv, x0, y0, x1, y1, ramp=WALL, lvl=4.2, r=6)
    rrect(cv, x0, y0, x1, y1 - 1, 5, PAINT, lambda x, y: 3.6 - (y - y0) * 0.004)
    rrect(cv, x0 + 5, y0 + 6, x1 - 5, y0 + 44, 3, PAINT, 4.0)
    cv.hline(x0 + 7, x1 - 7, y0 + 6, PAINT, 5.0)
    rrect(cv, x0 + 5, y1 - 28, x1 - 5, y1 - 5, 3, PAINT, 3.8)
    for i in range(6):
        cv.hline(x0 + 9, x1 - 9, y1 - 24 + i * 3, PAINT, 1.6)
    box(cv, x1 - 9, 104, x1 - 6, 112, BRASS, 3.6)
    cv.hline(x1 - 14, x1 - 7, 106, BRASS, 4.6)
    box(cv, x0 + 18, y0 + 14, x0 + 28, y0 + 20, BRASS, 3.6)             # placa amb el número
    cv.hline(x0 + 20, x0 + 26, y0 + 17, BRASS, 1.4)
    # un adhesiu d'un gat, posat torçat (de l'Iri)
    cv.disc(x0 + 23, y0 + 32, 4, 3, [(20, 20, 22), (50, 50, 54), (90, 90, 96)], 1.6)
    cv.poly([(x0 + 20, y0 + 30), (x0 + 20, y0 + 26), (x0 + 22, y0 + 29)], [(20, 20, 22), (50, 50, 54)], 1.4)
    cv.poly([(x0 + 26, y0 + 30), (x0 + 26, y0 + 26), (x0 + 24, y0 + 29)], [(20, 20, 22), (50, 50, 54)], 1.4)
    cv.put(x0 + 22, y0 + 32, YELL, 4.6, lit=0)
    cv.put(x0 + 25, y0 + 32, YELL, 4.6, lit=0)


def engine_door(cv):
    """La porta estanca de la sala de màquines, tancada, amb el rètol i el senyal d'orelleres."""
    x0, y0, x1, y1 = MAQUINES
    sota.door_frame(cv, x0, y0, x1, y1, ramp=WALL, lvl=4.4, r=9)
    sota.wt_leaf(cv, x0 + 1, y0 + 1, x1 - 1, y1 - 7, ramp=ENG, lvl=3.0, r=8)
    sota.sill(cv, x0, x1, y1)
    # palanques del marc
    for dx, dy in ((x0 - 5, 84), (x0 - 5, 124), (x1 + 3, 84), (x1 + 3, 124)):
        box(cv, dx, dy, dx + 2, dy + 6, CAB, 3.4)
    # rètol
    w = text_width('MÀQUINES')
    sx = (x0 + x1) // 2 - (w + 6) // 2
    sota.sign(cv, sx, 50, 'MÀQUINES', ramp=YELL, lvl=4.2)
    # senyal blau d'orelleres, a la fulla
    cx, cy = (x0 + x1) // 2, 84
    cv.disc(cx, cy, 6, 6, [(10, 20, 60), (20, 50, 120), (40, 80, 170), (90, 130, 210)], 2.6)
    cv.ring(cx, cy, 6, WHITEP, 4.6, step=10)
    cv.hline(cx - 3, cx + 3, cy - 3, WHITEP, 4.6)
    cv.rect(cx - 4, cy - 2, cx - 3, cy + 2, WHITEP, 4.6)
    cv.rect(cx + 3, cy - 2, cx + 4, cy + 2, WHITEP, 4.6)
    # una mica de llum per sota de la porta (a dins sempre hi ha llum)
    cv.hline(x0 + 6, x1 - 6, y1 - 7, YELL, 2.2, lit=0)


def store_door(cv):
    """La porta del pallol: de planxa, amb un pany de cadenat i el rètol."""
    x0, y0, x1, y1 = PALLOL
    sota.door_frame(cv, x0, y0, x1, y1, ramp=WALL, lvl=4.2, r=6)
    rrect(cv, x0, y0, x1, y1 - 7, 5, CAB, lambda x, y: 3.4 - (y - y0) * 0.006)
    for y in range(y0 + 8, y1 - 10, 6):                                 # nervis horitzontals
        cv.hline(x0 + 4, x1 - 4, y, CAB, 4.2)
        cv.hline(x0 + 4, x1 - 4, y + 1, CAB, 2.4)
    sota.sill(cv, x0, x1, y1)
    # frontisses
    for hy in (y0 + 12, y1 - 22):
        box(cv, x0 - 2, hy, x0 + 2, hy + 8, CAB, 4.0)
    # la balda, oberta, i el cadenat obert, penjat de la grapa: l'arc fora del cos (s'hi entra sense res)
    box(cv, x1 - 14, 98, x1 - 8, 104, CAB, 4.4)                         # la placa de la grapa
    cv.ring(x1 - 6, 101, 2, CAB, 4.6, step=30)                          # la grapa
    box(cv, x1 - 3, 96, x1 - 1, 112, CAB, 3.8)                          # la balda, girada avall
    cv.vline(x1 - 9, 103, 111, BRASS, 3.8)                              # l'arc: la pota llarga, dins el cos
    cv.hline(x1 - 9, x1 - 6, 102, BRASS, 4.6)
    cv.vline(x1 - 5, 103, 106, BRASS, 4.2)                              # la pota curta, fora
    cv.put(x1 - 5, 107, BRASS, 2.6)
    rrect(cv, x1 - 11, 111, x1 - 4, 118, 1, BRASS, lambda x, y: 4.2 - (x - x1 + 11) * 0.12)
    cv.put(x1 - 6, 111, DARK, 1.0)                                      # el forat de l'arc, buit
    cv.put(x1 - 8, 115, DARK, 1.0)                                      # el pany
    cv.put(x1 - 8, 116, DARK, 1.6)
    w = text_width('PALLOL')
    sota.sign(cv, (x0 + x1) // 2 - (w + 6) // 2, 52, 'PALLOL')


# ─── Detalls de paret ───────────────────────────────────────────────────────

def extinguisher(cv):
    x0 = 184
    box(cv, x0 - 2, 76, x0 + 14, 82, WHITEP, 4.0)                       # rètol de l'extintor
    cv.rect(x0, 78, x0 + 12, 80, REDP, 3.6)
    for y in range(92, 132):
        for x in range(x0, x0 + 13):
            u = (x - x0 - 6) / 6.5
            cv.put(x, y, REDP, 3.6 + 1.5 * (-0.3 - u) - 0.9 * u * u)
    cv.disc(x0 + 6, 92, 6, 3, REDP, lambda nx, ny: 4.2 - nx - ny)
    box(cv, x0 + 3, 84, x0 + 9, 90, CAB, 3.6)
    cv.line(x0 + 9, 86, x0 + 15, 84, CAB, 3.8)                          # la maneta
    cv.line(x0 + 3, 90, x0 - 2, 110, DARK, 2.6)                         # la mànega
    cv.rect(x0 + 1, 104, x0 + 11, 112, WHITEP, 3.8)                     # etiqueta
    cv.hline(x0 + 3, x0 + 9, 107, DARK, 1.6)
    box(cv, x0 - 1, 128, x0 + 13, 132, CAB, 3.0)                        # suport


def notice(cv):
    """Un tauler amb el torn de guàrdies i el plànol d'evacuació, entre la sala de màquines i el camarot."""
    x0, y0, x1, y1 = 76, 70, 104, 108
    box(cv, x0, y0, x1, y1, WALNUT, 3.2)
    box(cv, x0 + 2, y0 + 2, x1 - 2, y1 - 2, [(40, 34, 20), (80, 64, 40), (120, 98, 64), (150, 128, 90)], 2.6, edge=False)
    from hd.pix import PAPER
    box(cv, x0 + 4, y0 + 4, x0 + 15, y0 + 20, PAPER, 4.0)              # guàrdies
    for y in range(y0 + 7, y0 + 19, 2):
        cv.hline(x0 + 6, x0 + 13, y, PAPER, 1.6)
    box(cv, x0 + 16, y0 + 6, x1 - 4, y0 + 24, [(14, 40, 20), (30, 80, 40), (60, 130, 70), (150, 200, 150)], 2.6)
    cv.rect(x0 + 18, y0 + 10, x1 - 6, y0 + 14, WHITEP, 3.6)             # plànol (verd, sortides)
    cv.line(x0 + 19, y0 + 20, x1 - 7, y0 + 20, WHITEP, 3.6)
    box(cv, x0 + 6, y0 + 23, x0 + 20, y1 - 5, PAPER, 3.8)
    for y in range(y0 + 26, y1 - 6, 2):
        cv.hline(x0 + 8, x0 + 18, y, PAPER, 1.6)
    for px, py in ((x0 + 9, y0 + 5), (x0 + 22, y0 + 7), (x0 + 13, y0 + 24)):
        cv.put(px, py, REDP, 4.4)


def ladder_sign(cv):
    """Rètol de sortida (verd) cap a l'escala."""
    box(cv, 368, 60, 392, 66, SEAG, 3.6, edge=False)
    for i in range(4):
        cv.hline(384 - i, 384 - i, 63 - i, WHITEP, 4.6, lit=0)
        cv.hline(384 - i, 384 - i, 63 + i, WHITEP, 4.6, lit=0)
    cv.hline(372, 386, 63, WHITEP, 4.6, lit=0)
    glow(cv, 380, 63, 10, (90, 255, 140), 0.3)


# ─── L'escala cap a la coberta principal ───────────────────────────────────

def stair(cv):
    """Escala de vaixell (inclinada, de graons plans i passamans) que puja per un forat del sostre."""
    # el forat del sostre i la llum de la coberta principal (crema, càlida)
    CREAM = [(40, 36, 28), (80, 72, 56), (126, 114, 90), (170, 156, 124), (206, 192, 156), (232, 222, 190)]
    cv.rect(400, 0, 479, 20, CREAM, lambda x, y: 2.6 + (20 - y) * 0.05, lit=0.6)
    for x in range(400, W):
        if x % 22 == 0:
            cv.vline(x, 0, 20, CREAM, 1.6, lit=0.4)
    cv.hline(400, 479, 20, CAB, 1.0)
    cv.hline(400, 479, 21, CAB, 3.4)
    box(cv, 396, 0, 402, 23, ENG, 2.6)                                  # la brazola del forat
    # la paret de darrere l'escala, una mica més fosca (és un buc)
    cv.darken(404, 22, 479, FLOOR_Y - 1, lambda x, y: 0.18)
    # zancs (dues bigues inclinades) i graons
    bx0, by0, bx1, by1 = 404, FLOOR_Y + 2, 470, 10     # de baix a l'esquerra a dalt a la dreta
    n = 13
    for i in range(1, n):
        t = i / n
        x = bx0 + (bx1 - bx0) * t
        y = by0 + (by1 - by0) * t
        box(cv, int(x) - 10, int(y) - 1, int(x) + 12, int(y) + 2, CAB, 3.4)
        for k in range(-8, 12, 3):                                     # antilliscant
            cv.put(int(x) + k, int(y), CAB, 4.6)
    for off, lvl in ((-13, 3.6), (13, 4.2)):
        for w in range(3):
            cv.line(bx0 + off + w, by0, bx1 + off + w, by1, ENG, lvl + (1.0 if w == 0 else -0.6 if w == 2 else 0))
    # passamans, de tub
    for off in (-14, 15):
        cv.line(bx0 + off, by0 - 30, bx1 + off, by1 - 30, BRASS, 3.6)
        cv.line(bx0 + off, by0 - 29, bx1 + off, by1 - 29, BRASS, 2.0)
    for t in (0.12, 0.55):
        x = bx0 + (bx1 - bx0) * t
        y = by0 + (by1 - by0) * t
        for off in (-14, 15):
            cv.vline(int(x) + off, int(y) - 30, int(y), BRASS, 2.8)


# ─── L'escotilla de la sala de bombes ──────────────────────────────────────

def hatch(cv):
    # vora ratllada groc i negre
    cv.poly([(296, 166), (364, 166), (371, 189), (289, 189)], DARK, 1.2)
    for y in range(166, 190):
        t = (y - 166) / 23
        xa, xb = 296 - 7 * t, 364 + 7 * t
        for x in range(int(xa), int(xb) + 1):
            if ((x + y) // 4) % 2 == 0:
                cv.put(x, y, YELL, 3.2)
    # la tapa (planxa estriada, una mica més clara)
    cv.poly(HATCH, DECK, lambda x, y: 3.6 + (0.9 if ((x // 2 + y) % 4 == 0) else 0))
    cv.line(300, 168, 360, 168, DECK, 5.2)
    cv.line(294, 186, 366, 186, DECK, 1.0)
    # frontisses (a baix) i la nansa encastada
    for hx in (308, 348):
        box(cv, hx, 185, hx + 6, 188, CAB, 3.8)
    rrect(cv, 324, 174, 336, 179, 2, CAB, 1.6)
    cv.hline(326, 334, 176, CAB, 4.4)
    # el rètol a la paret
    w = text_width('BOMBES')
    sota.sign(cv, 330 - (w + 6) // 2, 120, 'BOMBES', ramp=WHITEP, lvl=4.0)
    cv.line(330, 131, 330, 140, WHITEP, 3.6)
    cv.poly([(327, 138), (333, 138), (330, 142)], WHITEP, 3.6)


# ─── Muntatge ───────────────────────────────────────────────────────────────

def bg(cv):
    walls(cv)
    notice(cv)
    cabin_door(cv)
    engine_door(cv)
    store_door(cv)
    extinguisher(cv)
    ladder_sign(cv)
    sota.checker_floor(cv)
    hatch(cv)
    stair(cv)
    for lx in LAMPS:
        sota.cage_lamp(cv, lx)
    for lx in LAMPS:
        sota.lamp_glow(cv, lx)
    glow(cv, 440, 12, 40, (255, 236, 190), 0.35)


PROPS = {}


# ─── Animacions ─────────────────────────────────────────────────────────────

def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv


def _frames_llum():
    """El llum de gàbia de la dreta fa mal contacte: de tant en tant baixa dues vegades i torna."""
    base = _base()
    lx, ly = LAMPS[1], 26
    dims = {38: 0.55, 39: 0.25, 41: 0.6, 42: 0.35}              # fotograma → quant s'apaga
    frames = []
    for i in range(48):
        cv = Canvas(light=LIGHT, img=base.img.copy())
        k = dims.get(i, 0)
        if k:
            cv.darken(lx - 120, 0, lx + 120, FLOOR_Y + 30,
                      lambda x, y: k * max(0.0, 1 - math.hypot(x - lx, (y - ly) * 1.1) / 130), dither=False)
            cv.darken(lx - 8, ly - 4, lx + 8, ly + 12, min(0.85, k * 1.4), dither=False)
        frames.append(_diff(cv.img, base.img))
    return frames


def _frames_gota():
    """Una gota de condensació que es forma sota el tub de gasoil, cau a terra i hi fa una rodoneta."""
    base = _base()
    gx, top, ground = 292, 50, 158
    seq = [('f', 0)] * 3 + [('f', 1)] * 3 + [('f', 2)] * 2
    y, v = top + 3, 1.0
    while y < ground:
        seq.append(('c', int(y)))
        y, v = y + v, v + 1.6
    seq += [('r', 1), ('r', 2), ('r', 3), ('r', 4)] + [('n', 0)] * 40
    frames = []
    for kind, v in seq:
        cv = Canvas(light=LIGHT, img=base.img.copy())
        if kind == 'f':
            for k in range(v + 1):
                cv.flat(gx, top + k, mix(cv.get(gx, top + k), (150, 190, 185), 0.7))
        elif kind == 'c':
            cv.flat(gx, v, (170, 205, 200))
            cv.flat(gx, v + 1, mix(cv.get(gx, v + 1), (130, 170, 165), 0.6))
        elif kind == 'r':
            for a in range(0, 360, 24):
                x = gx + round(math.cos(math.radians(a)) * v * 1.8)
                yy = ground + round(math.sin(math.radians(a)) * v * 0.45)
                cv.flat(x, yy, mix(cv.get(x, yy), (150, 190, 185), 0.55 - v * 0.08))
        frames.append(_diff(cv.img, base.img))
    return frames


ANIMS = {'llum': {'frames': _frames_llum, 'frameDuration': 110},
         'gota': {'frames': _frames_gota, 'frameDuration': 80}}

GEOMETRIA = {
    'things': {
        'porta_camarot': {'rect': (18, 58, 72, 152), 'walk': (45, 168)},
        'porta_maquines': {'rect': (106, 46, 174, 152), 'walk': (140, 168)},
        'porta_pallol': {'rect': (208, 48, 262, 152), 'walk': (235, 168)},
        'escotilla': {'rect': (290, 164, 370, 189), 'walk': (330, 194)},
        'escala': {'rect': (392, 0, 479, 152), 'walk': (410, 168)},
    },
    'spawns': {'iri': (240, 190), 'vet': (400, 194)},
    'walkable': [(6, 164), (474, 164), (478, 197), (2, 197)],
}
