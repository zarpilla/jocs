"""
**El dibuix pla de sempre** (font de les textures de la sala en 3D, final_estacio.py).

Finals 2 i 3 · L'Estació d'Orís (hd/rooms/final_estacio.py) a 640×360: la mateixa composició ×4/3, dibuixada de nou.
El moll de l'hangar de La Gavina (gavina_hangar) en el món on no hi ha hagut mai cap presó. Panells blancs i nets,
plantes, el pilar 7 repintat, el rètol gran «ESTACIÓ D'ORÍS» (amb lletres de bombetes, com el d'ALDAIA · FERRO-9 al
pròleg) i un finestral a l'espai amb la Terra i la Lluna. Al moll, la llançadora vella (ara amb els tres
components); la directora jove (cabell coure, uniforme clar) espera la Vet, i en Mos, sense granota de pres,
descarrega caixes.
Llums: les franges del sostre (càlides), la Terra pel finestral (blava), les bombetes del rètol.
Pantalla sencera (sense barra de verbs). Les peces (rètol, plantes, terra) i els personatges es reutilitzen a
final_cargol.
Animació: `ambient` (l'onada de llum del rètol, les estrelles i les llums de ciutat, la pols als raigs de sol, les
plantes i l'heura que es gronxen, la llumeta de la llançadora). Els fotogrames es fan redibuixant només dins les
zones que es mouen (ClipCanvas), damunt del fons quiet.
"""
import hd640  # noqa: F401  (abans que cap hd.*: posa la llibreria de dibuix a 640×360)

import math
import random
from functools import lru_cache

from PIL import Image, ImageOps

from hd.pix import (Canvas, Light, B4, W, H, hr, mix, ramp, PAPER, WALNUT, GOLD, STEEL)  # noqa: F401
from hd640.rooms.proleg_gavina_pla_comu import espai, terra, lluna
from hd640.rooms.fabrica_moll_pla_comu import shuttle, pillar, F9, clip_frames, _bb, _xs, _ys
from hd640.draw_characters import (M, person, hair_lvl, waist_band, HAIR_COPPER, GOLDPIN, BELT, BOOT,  # noqa: F401
                                   VET, MOS, GUARDIA)
import hd.characters as ch

hr = lru_cache(maxsize=1 << 19)(hr)      # (el soroll es calcula moltes vegades igual: a cada fotograma)

K = 4 / 3                                # 480 → 640

# ─── Rampes pròpies (fosc → clar) ───────────────────────────────────────────
WALLW = ramp((26, 30, 44), (58, 64, 82), (102, 110, 124), (150, 156, 164), (196, 198, 196), (226, 224, 214),
             (244, 240, 228), (255, 252, 242), n=10)                                   # panells blancs, càlids
DECK = ramp((22, 26, 38), (48, 54, 70), (84, 92, 106), (124, 130, 138), (164, 166, 166), (200, 198, 190),
            (228, 224, 212), (248, 244, 232), n=10)                                    # terra polit
MINT = ramp((8, 32, 34), (14, 62, 62), (26, 100, 96), (48, 142, 130), (92, 186, 166), (160, 226, 204), (220, 250, 236), n=8)
LEAF = ramp((8, 22, 20), (16, 44, 32), (30, 74, 44), (52, 108, 54), (88, 146, 66), (138, 186, 88), (196, 222, 132), n=8)
POT = ramp((40, 20, 18), (78, 38, 28), (124, 64, 40), (168, 96, 60), (206, 136, 90), (234, 184, 136), n=7)
BULB = [(110, 70, 40), (200, 140, 70), (250, 206, 120), (255, 236, 176), (255, 250, 226)]

FLOOR_Y = 249                      # on comença el terra (187 a 480)
VP = (320, 160)                    # punt de fuga
WIN = (200, 77, 627, 235)          # el finestral
PILAR_CX = 160
SIGN_Y = 32                        # dalt de les lletres del rètol
EARTH = (621, 285, 203)            # la Terra (centre i radi, en coordenades de pantalla)
SHUTTLE = (355, 248)               # morro i eix de la llançadora

LIGHT = Light(ambient=0.9, vignette=(80, 35), floor_fade=(309, 80))
LIGHT.point(160, 11, r=267, k=1.2, squash=1.2)
LIGHT.point(493, 11, r=267, k=1.0, squash=1.2)
LIGHT.point(547, 200, r=227, k=0.8)                                # la Terra pel finestral
LIGHT.point(320, 45, r=173, k=0.9, squash=1.8)                     # el rètol


# ─── Retall ─────────────────────────────────────────────────────────────────

def _clip(cv, x0, y0, x1, y1):
    """El rectangle (x0, y0, x1, y1) retallat a la zona que es dibuixa (o None si no s'hi toca)."""
    bx0, by0, bx1, by1 = _bb(cv)
    x0, y0, x1, y1 = max(int(x0), bx0, 0), max(int(y0), by0, 0), min(int(x1), bx1, W - 1), min(int(y1), by1, H - 1)
    return (x0, y0, x1, y1) if x0 <= x1 and y0 <= y1 else None


def tint(cv, x0, y0, x1, y1, col, k):
    r = _clip(cv, x0, y0, x1, y1)
    if r:
        cv.tint(*r, col, k)


def darken(cv, x0, y0, x1, y1, amount, dither=True):
    r = _clip(cv, x0, y0, x1, y1)
    if r:
        cv.darken(*r, amount, dither)


def glow(cv, cx, cy, r, col, strength):
    if _clip(cv, cx - r, cy - r, cx + r, cy + r):
        cv.glow(cx, cy, r, col, strength)


_glow = glow                             # (bulb_sign té un paràmetre que es diu glow)


def paste(cv, img, x, y):
    """Enganxa una imatge RGBA a (x, y), també en un ClipCanvas (només dins la zona que es dibuixa)."""
    x, y = int(x), int(y)
    if getattr(cv, 'bb', None) is None:
        cv.img.alpha_composite(img, (x, y))
        return
    r = _clip(cv, x, y, x + img.width - 1, y + img.height - 1)
    if not r:
        return
    Pi = img.load()
    for yy in range(r[1], r[3] + 1):
        for xx in range(r[0], r[2] + 1):
            c = Pi[xx - x, yy - y]
            if c[3] == 255:
                cv.P[xx, yy] = c
            elif c[3]:
                cv.P[xx, yy] = mix(cv.P[xx, yy], c, c[3] / 255) + (255,)


@lru_cache(maxsize=None)
def _vig(k):
    import numpy as np
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    a = k * np.maximum(0.0, (np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2)) - 0.8) * 1.4)
    return (1 - a * 0.6)[..., None]


def vinyeta(cv, k=0.55):
    """Enfosqueix les cantonades (com la de 480), d'un cop amb numpy i només dins la zona que es dibuixa."""
    import numpy as np
    x0, y0, x1, y1 = _bb(cv)
    box = (x0, y0, x1 + 1, y1 + 1)
    A = np.array(cv.img.crop(box))
    A[..., :3] = (A[..., :3] * _vig(k)[y0:y1 + 1, x0:x1 + 1]).astype(np.uint8)
    cv.img.paste(Image.fromarray(A, 'RGBA'), box[:2])


# ─── Lletres de 5×7 (i accents) ─────────────────────────────────────────────

FONT5 = {
    'E': ['#####', '#....', '#....', '####.', '#....', '#....', '#####'],
    'S': ['.####', '#....', '#....', '.###.', '....#', '....#', '####.'],
    'T': ['#####', '..#..', '..#..', '..#..', '..#..', '..#..', '..#..'],
    'A': ['.###.', '#...#', '#...#', '#####', '#...#', '#...#', '#...#'],
    'C': ['.####', '#....', '#....', '#....', '#....', '#....', '.####'],
    'I': ['###', '.#.', '.#.', '.#.', '.#.', '.#.', '###'],
    'O': ['.###.', '#...#', '#...#', '#...#', '#...#', '#...#', '.###.'],
    'D': ['####.', '#...#', '#...#', '#...#', '#...#', '#...#', '####.'],
    'R': ['####.', '#...#', '#...#', '####.', '#.#..', '#..#.', '#...#'],
    'G': ['.####', '#....', '#....', '#.###', '#...#', '#...#', '.###.'],
    'L': ['#....', '#....', '#....', '#....', '#....', '#....', '#####'],
    'M': ['#...#', '##.##', '#.#.#', '#.#.#', '#...#', '#...#', '#...#'],
    'N': ['#...#', '##..#', '#.#.#', '#..##', '#...#', '#...#', '#...#'],
    'B': ['####.', '#...#', '#...#', '####.', '#...#', '#...#', '####.'],
    'V': ['#...#', '#...#', '#...#', '#...#', '.#.#.', '.#.#.', '..#..'],
    'U': ['#...#', '#...#', '#...#', '#...#', '#...#', '#...#', '.###.'],
    '-': ['...', '...', '...', '###', '...', '...', '...'],
    '1': ['.#', '##', '.#', '.#', '.#', '.#', '.#'],
    "'": ['#', '#', '.', '.', '.', '.', '.'],
    ' ': ['..', '..', '..', '..', '..', '..', '..'],
}
ACUTE = {'Ó': 'O', 'Í': 'I'}


def text5_px(s, x0, y0, k=1):
    """Píxels (x, y, és_accent) d'un text en lletra de 5×7 a escala k (pot ser fraccionària: cada punt és la
    cel·la de round(x)..round(x + k) - 1); els accents van per sobre de y0. Retorna també la x on acaba."""
    out = []
    x = x0
    for c in s:
        base = ACUTE.get(c, c)
        g = FONT5[base]
        w = len(g[0])
        for j, row in enumerate(g):
            for i, b in enumerate(row):
                if b == '#':
                    out.append((x + i * k, y0 + j * k, False))
        if c in ACUTE:
            mx = x + (w // 2) * k
            out.append((mx + k, y0 - 3 * k, True))
            out.append((mx, y0 - 2 * k, True))
        x += (w + 1) * k
    return out, x - k


def text5_width(s, k=1):
    return round(text5_px(s, 0, 0, k)[1]) + 1


def _cell(x, y, k):
    """Els píxels (x0, y0, x1, y1) de la cel·la d'un punt de lletra a escala k."""
    x0, y0 = round(x), round(y)
    return x0, y0, max(x0, round(x + k) - 1), max(y0, round(y + k) - 1)


def bulb_sign(cv, s, x0, y0, k=4, glow=True, chase=None, band=None):
    """Lletres de bombetes (com el rètol del pròleg): cada punt de la lletra és una bombeta rodona de k×k, amb el
    portalàmpades fosc a la vora i un reflex a dalt a l'esquerra. `chase`: x on passa una onada de llum (les
    bombetes de prop s'encenen més), d'amplada `band`."""
    pts, xe = text5_px(s, x0, y0, k)
    band = band or 4 * k
    for x, y, acc in pts:
        cx0, cy0, cx1, cy1 = _cell(x, y, k)
        if not _clip(cv, cx0, cy0, cx1, cy1):
            continue
        boost = max(0.0, 1 - abs(x - chase) / band) if chase is not None else 0.0
        warm = (round(x / k) + round(y / k)) % 2
        n = cx1 - cx0 + 1
        r = (n - 1) / 2
        for yy in range(cy0, cy1 + 1):
            for xx in range(cx0, cx1 + 1):
                dx, dy = xx - cx0 - r + 0.15, yy - cy0 - r + 0.15
                d = math.hypot(dx, dy) / (r + 0.35)
                if d > 0.95 or xx == cx1 or yy == cy1:
                    c = BULB[2] if d < 1.25 else BULB[1]          # el portalàmpades, a la vora
                elif dx + dy < -r * 0.9:
                    c = BULB[4]                                     # el reflex
                else:
                    c = BULB[3]
                    if warm:
                        c = mix(c, (255, 214, 140), 0.35)
                if boost > 0:
                    edge = c in (BULB[1], BULB[2])
                    c = mix(c, (255, 255, 250) if not edge else BULB[4], min(1.0, boost * 1.3))
                cv.flat(xx, yy, c)
    if chase is not None and x0 - band < chase < xe + band:
        _glow(cv, chase, y0 + 7 * k / 2, band * 2.4, (255, 236, 180), 0.5)
    if glow:
        for x, y, acc in pts[::3]:
            _glow(cv, x + k / 3, y + k / 3, 9, (255, 220, 150), 0.22)


GULL = [(-5, 0), (-4, -1), (-3, -2), (-2, -2), (-1, -1), (0, 0), (1, -1), (2, -2), (3, -2), (4, -1), (5, 0)]


def gull(cv, cx, cy, flip=False, k=1):
    """Una gavina estilitzada, en menta (l'emblema de l'estació: el nom de La Gavina hi és, però és una altra).
    `k` és l'escala de la de 480 (k=1: la petita de les caixes; k=2: la del rètol); aquí es dibuixa a ×4/3, com
    una corba contínua (dues ales en arc) amb el gruix i l'ombra a sota."""
    s = k * K
    if k > 1:
        span = 5.4 * s
        th = s                                                    # gruix del traç
        for i in range(int(-span * 2), int(span * 2) + 1):
            u = i / 2
            yc = -2 * s * math.sin(math.pi * min(1.0, abs(u) / span))
            for b in range(int(th + 1.5)):
                y = cy + yc + b
                cv.put(cx + u, y, MINT, (3.6 + (0.5 if b == 0 else 0)) if b < th else 1.8, 0)
        return
    # la petita: ales en arc, més fina, amb la cua
    span = 6.2 * K
    for i in range(int(-span * 2), int(span * 2) + 1):
        u = i / 2
        a = abs(u) / span
        yc = -2.0 * K * math.sin(math.pi * min(1.0, a * 1.1)) + (1.0 if a < 0.12 else 0)
        cv.put(cx + u, cy + yc, MINT, 3.4, 0)
        cv.put(cx + u, cy + yc + 1, MINT, 2.0, 0)
    cv.put(cx, cy + 2, MINT, 2.4, 0)
    cv.put(cx, cy + 3, MINT, 1.8, 0)


# ─── Peces ──────────────────────────────────────────────────────────────────

def ceiling(cv):
    """Sostre de panells blancs amb dues franges de llum càlida."""
    for y in _ys(cv, 0, 20):
        for x in _xs(cv, 0, W - 1):
            lvl = 4.4 + y * 0.09 + (hr(x // 53, 1) - 0.5) * 0.3
            if x % 53 == 0:
                lvl -= 1.4
            elif x % 53 == 1:
                lvl += 0.6
            cv.put(x, y, WALLW, lvl, 0.4)
    for x0, x1 in ((16, 304), (336, 624)):
        if not _clip(cv, x0 - 22, 0, x1 + 22, 32):
            continue
        cv.hline(x0 - 1, x1 + 1, 6, WALLW, 2.0, 0)
        cv.hline(x0, x1, 7, WALLW, 2.6, 0)
        for x in range(x0, x1 + 1, 13):
            glow(cv, x, 11, 21, (255, 236, 200), 0.4)
        cv.hline(x0, x1, 8, [(255, 252, 244)], 0, 0)
        cv.hline(x0, x1, 9, [(255, 248, 228)], 0, 0)
        cv.hline(x0, x1, 10, [(255, 240, 206)], 0, 0)
        cv.hline(x0, x1, 11, WALLW, 3.0, 0)
        cv.vline(x0 - 1, 6, 11, WALLW, 2.2, 0)
        cv.vline(x1 + 1, 6, 11, WALLW, 2.2, 0)
    cv.hline(0, W - 1, 20, WALLW, 2.0, 0.4)
    cv.hline(0, W - 1, 21, WALLW, 6.4, 0.3)


def wall(cv, x0, x1, y0, y1):
    """Panells blancs arrodonits, amb juntes suaus (ombra i llum) i un sòcol de color menta."""
    for y in _ys(cv, y0, y1):
        for x in _xs(cv, x0, x1):
            u, v = x % 59, (y - y0) % 56
            lvl = 4.6 + (hr(x // 59, (y - y0) // 56, 6) - 0.5) * 0.3 - v * 0.009
            if u == 0 or v == 0:
                lvl -= 1.6
            elif u == 1 or v == 1:
                lvl += 0.9
            elif u == 58 or v == 55:
                lvl -= 0.5
            if u in (3, 55) and v in (3, 52):
                lvl += 1.2                                         # cargols de les cantonades
            cv.put(x, y, WALLW, lvl)
    # sòcol menta amb una línia de llum
    for y in _ys(cv, y1 - 8, y1):
        for x in _xs(cv, x0, x1):
            cv.put(x, y, MINT, [5.6, 4.6, 4.0, 3.6, 3.4, 3.3, 3.1, 2.8, 1.8][y - y1 + 8])


def sign(cv, t=0.0):
    """El rètol: «ESTACIÓ D'ORÍS» en bombetes sobre una biga blanca, i una gavina a cada banda."""
    k = 4
    txt = "ESTACIÓ D'ORÍS"
    w = text5_width(txt, k)
    x0 = (W - w) // 2
    if not _clip(cv, x0 - 80, 0, x0 + w + 80, 110):
        return
    # biga que fa de suport
    by0, by1 = SIGN_Y - 12, SIGN_Y + 7 * k + 7
    for y in _ys(cv, by0, by1):
        for x in _xs(cv, x0 - 35, x0 + w + 34):
            lvl = 5.4 - (y - by0) * 0.022
            if y == by0:
                lvl = 7.2
            elif y == by0 + 1:
                lvl = 6.4
            elif y == by1:
                lvl = 2.2
            elif y == by1 - 1:
                lvl = 3.6
            cv.put(x, y, WALLW, lvl, 0.3)
    for x in (x0 - 35, x0 + w + 34):
        cv.vline(x, by0, by1, WALLW, 2.6, 0.3)
    cv.vline(x0 - 34, by0 + 1, by1 - 1, WALLW, 6.4, 0.3)
    darken(cv, x0 - 35, by1 + 1, x0 + w + 34, by1 + 5, lambda x, y: 0.7 - (y - by1) * 0.14)
    # cargols de la biga
    for bx in (x0 - 29, x0 + w + 28):
        for by in (by0 + 5, by1 - 6):
            cv.put(bx, by, WALLW, 7.6, 0.3)
            cv.put(bx + 1, by + 1, WALLW, 3.0, 0.3)
    # franja menta a sota
    cv.hline(x0 - 29, x0 + w + 28, by1 - 4, MINT, 4.8, 0)
    cv.hline(x0 - 29, x0 + w + 28, by1 - 3, MINT, 3.6, 0)
    # les lletres, amb una ombra suau al panell
    pts, _ = text5_px(txt, x0, SIGN_Y, k)
    for x, y, _a in pts:
        darken(cv, x + 1, y + 2, x + k, y + k + 1, 0.35)
    # una onada de llum recorre les bombetes d'esquerra a dreta (a t=0 és fora del rètol)
    bulb_sign(cv, txt, x0, SIGN_Y, k, chase=x0 - 40 + (t % 1) * (w + 80), band=19)
    # gavines (l'emblema de l'estació) a cada banda
    for gx, flip in ((x0 - 21, False), (x0 + w + 20, True)):
        gull(cv, gx - 1, SIGN_Y + 15, flip, k=2)


def window(cv, t=0.0):
    """El finestral: l'espai, la Terra i la Lluna, amb marc blanc arrodonit i muntants."""
    X0, Y0, X1, Y1 = WIN
    r = _clip(cv, X0, Y0, X1, Y1)
    if r:
        S = _sky(t).load()
        for y in range(r[1], r[3] + 1):
            for x in range(r[0], r[2] + 1):
                cv.P[x, y] = S[x, y]
        # reflexos al vidre: unes ratlles en diagonal, molt fluixes
        tint(cv, X0, Y0, X1, Y1, (200, 230, 255),
             lambda x, y: 0.10 if (x + y * 0.6) % 120 < 13 else (0.05 if (x + y * 0.6) % 120 < 21 else 0))
    # muntants (amb la cantonada arrodonida)
    MUL = [X0, 309, 419, 528, X1]
    for mx in MUL:
        a, b = (mx - 5, mx + 5)
        for y in _ys(cv, Y0 - 5, Y1 + 6):
            for x in _xs(cv, a, b):
                u = (x - a) / (b - a)
                cv.put(x, y, WALLW, 6.4 - u * 3.0 + (0.6 if x == a + 1 else 0) - (0.8 if x == b else 0))
    for y0_, y1_, top in ((Y0 - 8, Y0 - 1, True), (Y1 + 1, Y1 + 11, False)):
        for y in _ys(cv, y0_, y1_):
            for x in _xs(cv, X0 - 5, X1 + 5):
                tt = (y - y0_) / (y1_ - y0_)
                lvl = (6.6 - tt * 3.4) if top else (7.0 - tt * 4.2)
                if not top and y == y0_ + 1:
                    lvl += 0.5
                cv.put(x, y, WALLW, lvl)
    # cantonades arrodonides dins de cada vidre
    for i in range(len(MUL) - 1):
        xa, xb = MUL[i] + 6, MUL[i + 1] - 6
        for (cx, cy, sx, sy) in ((xa, Y0, 1, 1), (xb, Y0, -1, 1), (xa, Y1, 1, -1), (xb, Y1, -1, -1)):
            for dy in range(5):
                for dx in range(5):
                    d = math.hypot(4.5 - dx, 4.5 - dy)
                    if d > 4.6:
                        cv.put(cx + dx * sx, cy + dy * sy, WALLW, 5.6)
                    elif d > 3.9:
                        cv.put(cx + dx * sx, cy + dy * sy, WALLW, 3.0)
    darken(cv, X0, Y0, X1, Y0 + 3, lambda x, y: 0.5 - (y - Y0) * 0.1)
    # cargols del marc
    for mx in MUL:
        for y in (Y0 + 13, Y1 - 13):
            cv.put(mx, y, WALLW, 7.6)
            cv.put(mx + 1, y + 1, WALLW, 3.4)


@lru_cache(maxsize=32)
def _sky(t=0.0):
    """L'espai del finestral (amb la Lluna i la Terra): les estrelles titil·len i les ciutats fan pampallugues."""
    X0, Y0, X1, Y1 = WIN
    sky = Canvas()
    espai(sky, X0, X1, seed=11, t=t)
    lluna(sky, 275, 112, 9)
    terra(sky, EARTH[0], EARTH[1], EARTH[2], X0, X1, t=t)
    return sky.img


def planter(cv, x0, x1, ytop, seed=0, tall=35, time=0.0):
    """Jardinera llarga amb plantes de fulla (sota el finestral)."""
    if not _clip(cv, x0 - 12, ytop - tall - 14, x1 + 12, ytop + 16):
        return
    rnd = random.Random(seed)
    # mates de fulla rodona
    for _ in range((x1 - x0) // 21):
        bx, r = rnd.uniform(x0 + 11, x1 - 11), rnd.uniform(8, 12)
        by = ytop - r * 0.6
        for y in _ys(cv, by - r, ytop):
            for x in _xs(cv, bx - r - 1, bx + r + 2):
                nx, ny = (x - bx) / r, (y - by) / r
                d = nx * nx + ny * ny
                if d <= 1 + (hr(x // 3, y // 3, seed) - 0.5) * 0.5:
                    lvl = 3.2 - nx * 1.0 - ny * 1.2 + (hr(x // 3, y // 3, 9) - 0.5) * 1.2 + (hr(x, y, 10) - 0.5) * 0.6
                    if (x + y * 2) % 7 == 0 and hr(x // 2, y, 11) > 0.6:
                        lvl -= 0.9                                    # les vores de les fulletes
                    cv.put(x, y, LEAF, lvl)
    # fulles, darrere la jardinera
    for _ in range((x1 - x0) // 4):
        bx = rnd.uniform(x0 + 3, x1 - 3)
        hgt = rnd.uniform(tall * 0.5, tall)
        lean = rnd.uniform(-0.5, 0.5)
        for i in range(int(hgt)):
            tt = i / hgt
            x = bx + lean * i + math.sin(tt * 3 + bx / K) * 1.6
            x += 1.5 * tt * tt * (math.sin(2 * math.pi * time + bx * 0.3) - math.sin(bx * 0.3))   # es gronxen
            y = ytop - i
            wdt = 2.1 * math.sin(tt * math.pi) + 0.5
            for dx in range(-int(wdt), int(wdt) + 1):
                lvl = 2.6 + tt * 2.6 - (0.9 if dx > 0 else 0) + (0.5 if dx == -int(wdt) else 0) \
                    + (hr(int(x) + dx, y, 4) - 0.5) * 0.6
                if dx == 0 and tt > 0.15:
                    lvl += 0.4                                        # el nervi
                cv.put(x + dx, y, LEAF, lvl)
    # flors petites
    for _ in range((x1 - x0) // 19):
        fx, fy = rnd.randint(x0 + 5, x1 - 5), ytop - rnd.randint(int(tall * 0.4), tall)
        col = rnd.choice(((255, 210, 120), (255, 160, 170), (250, 250, 240)))
        dk = mix(col, (120, 60, 60), 0.3)
        if _clip(cv, fx - 1, fy - 1, fx + 2, fy + 2):
            for dx, dy, c in ((0, -1, col), (-1, 0, col), (0, 0, (255, 236, 150)), (1, 0, dk), (0, 1, dk), (1, 1, dk)):
                cv.flat(fx + dx, fy + dy, c)
    # jardinera
    for y in _ys(cv, ytop, ytop + 15):
        for x in _xs(cv, x0, x1):
            lvl = 4.4 - (y - ytop) * 0.11 - (x - x0) / (x1 - x0) * 0.4
            if y == ytop:
                lvl = 6.6
            elif y == ytop + 1:
                lvl = 5.4
            elif y == ytop + 2:
                lvl = 3.4
            elif y == ytop + 15:
                lvl = 2.6
            if x == x0:
                lvl += 1.0
            cv.put(x, y, WALLW, lvl)
    cv.hline(x0 + 4, x1 - 4, ytop + 8, MINT, 4.2)
    cv.hline(x0 + 4, x1 - 4, ytop + 9, MINT, 3.0)
    for y in _ys(cv, ytop + 2, ytop + 5):                               # la terra
        for x in _xs(cv, x0 + 3, x1 - 2):
            if hr(x, y, 2) > 0.5:
                cv.put(x, y, POT, 1.0 + (0.6 if hr(x, y, 3) > 0.8 else 0))


def big_plant(cv, cx, base, seed=3, h=80):
    """Una planta gran en test de terrissa: fulles llargues que cauen (com una kentia)."""
    rnd = random.Random(seed)
    # test
    for y in range(base - 29, base + 1):
        tt = (y - base + 29) / 29
        hw = 15 - tt * 4
        for x in range(math.floor(cx - hw), math.ceil(cx + hw) + 1):
            u = (x - cx) / hw
            lvl = 3.6 - u * 1.4 - u * u * 1.0 - tt * 0.6
            if y < base - 25:
                lvl += 1.4 - (0.8 if y == base - 25 else 0)
            if abs(u) <= 1 and (y - base) % 9 == 0 and y > base - 24:
                lvl -= 0.5                                            # les marques del torn
            cv.put(x, y, POT, lvl)
    cv.hline(cx - 16, cx + 16, base - 29, POT, 5.0)
    cv.hline(cx - 15, cx + 15, base - 28, POT, 4.4)
    # tiges i fulles en arc
    fronds = []
    for i in range(9):
        ang = -math.pi / 2 + (i - 4) * 0.34 + rnd.uniform(-0.12, 0.12)
        ln = h * rnd.uniform(0.6, 1.0)
        fronds.append((ang, ln, i))
    fronds.sort(key=lambda f: -abs(f[0] + math.pi / 2))
    for ang, ln, i in fronds:
        x, y = cx, base - 29
        dx, dy = math.cos(ang), math.sin(ang)
        n = int(ln)
        for s in range(n):
            tt = s / n
            x += dx
            y += dy
            dy += 0.021                                              # cau pel pes
            cv.put(x, y, LEAF, 2.4 + tt * 1.2)
            cv.put(x, y + 1, LEAF, 1.8 + tt * 1.0)
            if tt > 0.12:
                for side in (-1, 1):                                 # folíols
                    lf = (1 - tt) * 9.3 + 2.7
                    for k in range(1, int(lf)):
                        px = x - dy * side * k * 0.7 + dx * k * 0.5
                        py = y + dx * side * k * 0.7 + dy * k * 0.5 + k * 0.25
                        if (s + (1 if side > 0 else 0)) % 3 != 2:
                            lvl = 3.0 + tt * 1.8 + (0.9 if side < 0 else -0.6) - k * 0.08
                            if (s + (1 if side > 0 else 0)) % 3 == 1:
                                lvl -= 0.7                            # l'altra cara del folíol
                            cv.put(px, py, LEAF, lvl)


def door(cv):
    """Porta corredissa cap a l'estació, amb un vidre que deixa veure un passadís lluminós."""
    x0, x1, y0, y1 = 21, 101, 131, FLOOR_Y - 1
    for y in range(y0 - 5, y1 + 1):
        for x in range(x0 - 5, x1 + 6):
            inside = x0 <= x <= x1 and y >= y0
            if not inside:
                cv.put(x, y, WALLW, 3.0 + (2.4 if x < x0 or y < y0 - 3 else 0) - (1.2 if x > x1 else 0)
                       + (0.8 if x == x0 - 5 or y == y0 - 5 else 0))
    mid = (x0 + x1) // 2
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            lvl = 5.4 - (x - x0) * 0.009 - (y - y0) * 0.003
            if x in (mid, mid + 1):
                lvl = 2.2 if x == mid else 6.2
            elif x in (x0, mid + 2):
                lvl += 0.8
            cv.put(x, y, WALLW, lvl)
    # vidres amb el passadís de darrere (llum càlida): llums al sostre i portes al fons
    for gx in (x0 + 9, mid + 9):
        for y in range(y0 + 13, y0 + 61):
            for x in range(gx, gx + 21):
                d = (y - y0 - 13) / 48
                lvl = 4.6 - d * 1.2 + (1.2 if (x - gx) < 4 else 0)
                if 29 < y - y0 < 45 and (x - gx) % 9 == 4:
                    lvl -= 1.6
                if y - y0 == 17 and (x - gx) % 7 < 4:
                    lvl += 1.4                                         # els llums del passadís
                cv.put(x, y, GOLD, lvl - 0.4, 0)
        cv.hline(gx, gx + 20, y0 + 13, WALLW, 2.0)
        cv.vline(gx + 20, y0 + 13, y0 + 60, WALLW, 6.0)
        cv.hline(gx, gx + 20, y0 + 61, WALLW, 6.4)
        for k in range(6):                                             # reflex del vidre, en diagonal
            cv.put(gx + 13 + k // 2, y0 + 20 + k, PAPER, 5.6, 0)
    # franja menta i nansa
    cv.hline(x0, x1, y0 + 75, MINT, 4.4)
    cv.hline(x0, x1, y0 + 76, MINT, 3.4)
    cv.hline(x0, x1, y0 + 77, MINT, 2.4)
    for hx in (mid - 5, mid + 7):
        cv.vline(hx, y0 + 80, y0 + 93, STEEL, 6.4)
        cv.vline(hx + 1, y0 + 80, y0 + 93, STEEL, 3.6)
    # rètol del moll damunt la porta
    cv.rect(x0 + 5, y0 - 20, x1 - 5, y0 - 7, MINT, 2.6, 0.3)
    cv.hline(x0 + 5, x1 - 5, y0 - 20, MINT, 4.4, 0.3)
    cv.hline(x0 + 5, x1 - 5, y0 - 7, MINT, 1.6, 0.3)
    tw = text5_width('MOLL L-1')
    tx = (x0 + x1) // 2 - tw // 2
    for x, y, _a in text5_px('MOLL L-1', tx, y0 - 17)[0]:
        cv.flat(x + 1, y + 1, (16, 66, 64))
        cv.flat(x, y, (232, 252, 242))
    # pilot verd
    cv.flat(x1 + 11, y0 + 53, (150, 255, 190))
    cv.flat(x1 + 12, y0 + 53, (110, 230, 160))
    cv.glow(x1 + 11, y0 + 53, 8, (120, 255, 170), 0.5)


def floor_deck(cv):
    """Terra de planxes clares i polides, en perspectiva: hi brilla el que hi ha a sobre (la paret, el finestral)
    i hi cauen les clapes de sol que entren pels vidres."""
    vx, vy = VP
    r = _clip(cv, 0, FLOOR_Y, W - 1, H - 1)
    above = _pre_floor().load() if r else None
    for y in (range(r[1], r[3] + 1) if r else ()):
        dep = y - vy
        for x in range(r[0], r[2] + 1):
            u = (x - vx) / dep * 3.0
            pl = math.floor(u)
            fr = (u - pl) * dep / 3.0
            tt = 1467 / dep
            seg = math.floor(tt / 2.4)
            seg_up = math.floor(1467 / (dep - 1) / 2.4)
            lvl = 3.5 + (hr(pl, seg, 2) - 0.5) * 0.35 - (y - FLOOR_Y) * 0.0045
            if fr < 1:
                lvl -= 1.4
            elif fr < 2:
                lvl += 0.35                                          # el cantell de la planxa, polit
            elif seg != seg_up:
                lvl -= 1.2
            cv.put(x, y, DECK, lvl)
            # reflex de la paret: es fon a mesura que s'allunya de la vora
            d = y - FLOOR_Y
            sy = FLOOR_Y - 1 - int(d * 1.1)
            k = 0.42 * max(0.0, 1 - d / 69) ** 1.4
            if sy > 22 and k > 0.02 and fr >= 1:
                cv.flat(x, y, mix(cv.get(x, y), above[x, sy], k))
    sun_patches(cv)
    # línia menta de guia, cap a la porta
    for y in _ys(cv, FLOOR_Y + 11, FLOOR_Y + 14):
        for x in _xs(cv, 0, W - 1):
            if ((x - y * 2) // 11) % 2 == 0:
                cv.put(x, y, MINT, 4.6 - (y - FLOOR_Y - 11) * 0.5)
    cv.hline(0, W - 1, FLOOR_Y, WALLW, 2.0, 0.3)


@lru_cache(maxsize=None)
def _pre_floor():
    """El que hi ha damunt del terra abans de dibuixar-lo (el que s'hi reflecteix), amb el fons quiet: així el
    reflex no depèn del fotograma (les estrelles que titil·len no hi arriben a fer-se veure)."""
    cv = Canvas(light=LIGHT)
    _upper(cv)
    return cv.img


PANES = [(205, 304), (315, 413), (424, 523), (533, 621)]
SUN_DX = 1.05                      # el sol entra de l'esquerra: les clapes es desplacen a la dreta


def sun_patches(cv, air=True):
    """Clapes de sol al terra (la forma dels vidres, estirada cap a nosaltres) i raigs suaus a l'aire."""
    X0, Y0, X1, Y1 = WIN
    warm = (255, 228, 170)
    for xa, xb in PANES:
        for y in _ys(cv, FLOOR_Y + 4, FLOOR_Y + 87):
            d = y - FLOOR_Y - 4
            off = d * SUN_DX + 8
            grow = d * 0.28
            a, b = xa + off - grow * 0.2, xb + off + grow
            fade = max(0.0, 1 - d / 84)
            for x in _xs(cv, max(0, int(a)), min(W - 1, int(b))):
                e = min(x - a, b - x)
                k = 0.55 * fade * min(1.0, e / 4)
                if k > B4[y & 3][x & 3] * 0.3:
                    cv.flat(x, y, mix(cv.get(x, y), warm, k))
        if air:
            # raig a l'aire: del vidre fins a la clapa
            for y in _ys(cv, Y0 + 8, FLOOR_Y + 3):
                tt = (y - Y0) / (FLOOR_Y + 4 - Y0)
                a = xa + 13 + tt * 11
                b = xb - 8 + tt * 13
                for x in _xs(cv, max(0, int(a)), min(W - 1, int(b))):
                    k = 0.07 * (0.3 + tt) * (0.6 + 0.4 * math.sin((x - y * 0.4) / 12))
                    if k > 0:
                        cv.flat(x, y, mix(cv.get(x, y), warm, k))


FEET = (34, 111)                   # on són els peus al fotograma de persona (65×116)


def reflect(cv, img, fx, fy, k=0.28, flip=False):
    """Reflex d'un fotograma al terra polit (de cap per avall, a sota dels peus, que es fon)."""
    if flip:
        img = ImageOps.mirror(img)
        fx -= img.width - 1 - 2 * FEET[0]
    f = ImageOps.flip(img)
    P = f.load()
    ox, oy = int(fx - FEET[0]), int(fy)
    h = f.height
    n = FEET[1] + 1
    for j in range(h - n + 1, h):
        y = oy + (j - (h - n)) - 1
        r = _clip(cv, ox, y, ox + f.width - 1, y) if FLOOR_Y < y < H else None
        if not r:
            continue
        for i in range(r[0] - ox, r[2] - ox + 1):
            c = P[i, j]
            if c[3]:
                d = y - fy
                kk = k * max(0.0, 1 - d / 53)
                if kk > B4[y & 3][(ox + i) & 3] * 0.25:
                    cv.flat(ox + i, y, mix(cv.get(ox + i, y), c, kk))


def components(cv, x0, cy):
    """Els tres components de ferro-9, al seu lloc a la llançadora vella (tapen els forats de l'envellida)."""
    for ox in (96, 116, 136):
        hx, hy = x0 + ox, cy + 13
        cv.rect(hx, hy, hx + 12, hy + 7, F9, lambda x, y: 4.6 - (y - hy) * 0.5)
        cv.hline(hx, hx + 12, hy, F9, 6.0)
        cv.vline(hx + 12, hy, hy + 7, F9, 2.6)
        cv.hline(hx, hx + 12, hy + 7, F9, 2.2)
        cv.put(hx + 1, hy + 2, F9, 7, 0)
        cv.put(hx + 2, hy + 2, F9, 6.4, 0)
        cv.put(hx + 10, hy + 5, F9, 1.6, 0)                          # el cargol de fixació
        glow(cv, hx + 6, hy + 4, 8, (160, 210, 255), 0.25)


def crate(cv, x0, y0, w, h, label=True, seed=0):
    """Caixa de càrrega de l'estació (fusta clara, amb cantoneres menta)."""
    if not _clip(cv, x0 - 1, y0, x0 + w + 4, y0 + h + 3):
        return
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            lvl = 4.6 + (hr(x // 7, seed) - 0.5) * 0.4 - (0.9 if (y - y0) % 9 == 8 else 0) \
                + (0.3 if (y - y0) % 9 == 0 else 0) - (x - x0) / w * 0.6 + (hr(x, y // 3, seed + 5) - 0.5) * 0.25
            if y < y0 + 3:
                lvl = 6.0 - (y - y0) * 0.4
            if x in (x0, x0 + w - 1):
                lvl = 5.6 if x == x0 else 3.0
            cv.put(x, y, WALNUT, lvl)
    for cx, cy in ((x0, y0), (x0 + w - 4, y0), (x0, y0 + h - 4), (x0 + w - 4, y0 + h - 4)):
        cv.rect(cx, cy, cx + 3, cy + 3, MINT, lambda x, y: 4.2 - (x - cx) * 0.15 - (y - cy) * 0.2)
        cv.put(cx + 1, cy + 1, MINT, 6.0)                            # el clau de la cantonera
    if label:
        lx0, ly0 = x0 + w // 2 - 8, y0 + h // 2 - 4
        cv.rect(lx0, ly0, lx0 + 15, ly0 + 8, PAPER, 5.0)
        cv.hline(lx0, lx0 + 15, ly0 + 8, PAPER, 3.6)
        gull(cv, x0 + w // 2, y0 + h // 2 - 1)
    darken(cv, x0 - 1, y0 + h, x0 + w + 4, y0 + h + 2, lambda x, y: 0.7)


# ─── Personatges ────────────────────────────────────────────────────────────

LIGHTUNI = M((60, 66, 84), (112, 120, 134), (168, 174, 180), (210, 212, 210), (236, 234, 226), (250, 248, 240), (255, 255, 250))
WORK = M((22, 40, 44), (36, 66, 70), (54, 96, 98), (78, 128, 124), (110, 160, 150), (150, 192, 178))


def directora_jove_hair(fg, p, spec):
    """El cabell coure de les Orís, recollit en una cua baixa (sense gorra)."""
    hx, hy = p.head
    Hm = HAIR_COPPER
    tex = hair_lvl(hx - 1, hy - 2, 5.0, k=1.1, strands=0.3, freq=2.0)
    if p.f == 'D':
        fg.ell(hx, hy - 1.0, 7.2, 7.8, Hm, 2.8, amp=1.6, lvlfn=tex, clip=lambda x, y: y <= hy - 3 + ((x - hx) / 6.4) ** 2 * 7)
        fg.line(hx - 1, hy - 8, hx - 3, hy - 3.6, Hm, 1.6)                                       # clenxa
    elif p.f == 'L':
        fg.ell(hx + 1.2, hy - 0.8, 7.2, 7.8, Hm, 2.8, amp=1.6, lvlfn=tex,
               clip=lambda x, y: (x >= hx - 4.0 or y <= hy - 4.6) and not (x < hx + 2.4 and y > hy - 2.6))
        fg.limb((hx + 6.6, hy + 0.5), (hx + 7.6, hy + 11), 2.2, 1.4, Hm, 2.6, amp=1.6, cont=(0, 0.8),
                lvlfn=lambda x, y: 0.6 * math.sin(y * 1.3))                                       # cua
        fg.ell(hx + 6.4, hy + 0.6, 1.4, 1.0, GOLDPIN, 2.4, amp=1.0)                               # agulla
        X, Y = fg.F(hx + 6.0 + fg.ox), fg.F(hy + 0.2 + fg.oy)
        fg.rpx(X, Y, GOLDPIN, 4.4)                                                              # (el reflex)
    else:
        fg.ell(hx, hy - 0.4, 7.2, 8.0, Hm, 2.8, amp=1.6, lvlfn=tex)
        fg.limb((hx, hy + 3), (hx + 0.4, hy + 13), 2.2, 1.4, Hm, 2.6, amp=1.6, cont=(0, 0.8))


def _pin(fg, X, Y):
    """El pin de la gavina d'or, en píxels reals: dues ales i el reflex."""
    for dx, dy, lv in ((-2, 0, 2), (-1, -1, 3), (0, 0, 3), (1, -1, 3), (2, 0, 2), (0, 1, 1.6)):
        fg.rpx(X + dx, Y + dy, GOLDPIN, lv)
    fg.rpx(X - 1, Y - 1, GOLDPIN, 4.2)


def directora_jove_uniform(fg, p, spec):
    """Uniforme clar de l'estació: jaqueta creuada, coll menta, el pin de la gavina d'or."""
    b = p.bob
    hx = 24.5
    U = spec['top']
    TR = M((10, 50, 50), (26, 100, 96), (60, 160, 140), (130, 220, 196))
    F, G = fg.F, fg.G
    if p.f == 'D':
        fg.poly([(hx - 3.2, 26.5 + b), (hx + 3.2, 26.5 + b), (hx, 31 + b)], TR, 2.2)
        for Y in range(round(F(29 + b)), round(F(46 + b))):                                     # la solapa creuada
            fg.rshade(F(hx + 2 - (G(Y) - 29 - b) * 0.12), Y, -1.0, U)
        for y in (33, 38, 43):                                                                  # botons
            X, Y = F(hx + 3), F(y + b)
            fg.rpx(X, Y, GOLDPIN, 2.4)
            fg.rpx(X + 1, Y, GOLDPIN, 1.6)
            fg.rpx(X, Y - 1, GOLDPIN, 3.6)
        _pin(fg, F(hx - 5), F(33 + b))
    elif p.f == 'L':
        fg.poly([(20.0, 26.5 + b), (23.4, 26.5 + b), (21.0, 30.5 + b)], TR, 2.2)
        _pin(fg, F(20.5), F(33 + b))
        for Y in range(round(F(29 + b)), round(F(46 + b))):
            fg.rshade(F(19.6), Y, -0.6, U)
    # la vora de la jaqueta, ribetejada de menta
    Y = round(F(46 + b))
    for X in range(round(F(12)), round(F(38)) + 1):
        g_ = fg.rget(X, Y)
        if g_ and g_[0] in (U, spec['legs']):
            fg.rpx(X, Y, TR, 1.6 if X < F(24) else 1.2)
            g2 = fg.rget(X, Y - 1)
            if g2 and g2[0] is U:
                fg.rpx(X, Y - 1, TR, 2.4 if X < F(24) else 2.0)


DIRECTORA_JOVE = dict(GUARDIA)
DIRECTORA_JOVE.update({
    'top': LIGHTUNI, 'legs': LIGHTUNI, 'sleeve': LIGHTUNI, 'shoes': BELT, 'shoe_lvl': 2.6,
    'hooks': {'hair': directora_jove_hair, 'torso': directora_jove_uniform},
})


def mos_feina(fg, p, spec):
    """En Mos amb granota de feina de l'estació (sense número): cremallera, cinturó i una gavina a la màniga."""
    b = p.bob
    O = spec['top']
    hx = 24.5
    F = fg.F
    if p.f == 'D':
        X = F(hx)
        for Y in range(round(F(29 + b)), round(F(45 + b))):
            fg.rshade(X, Y, -0.8, O)
            if Y % 2 == 0:
                fg.rshade(X + 1, Y, 0.5, O)                                                    # les dents de la cremallera
        fg.poly([(hx - 2.4, 26.5 + b), (hx + 2.6, 26.5 + b), (hx + 0.5, 31 + b)], spec['skin'], 1.8)
    elif p.f == 'L':
        fg.poly([(20.0, 26.5 + b), (22.6, 26.5 + b), (20.6, 30 + b)], spec['skin'], 1.8)
    waist_band(fg, p, O, 45, col=BELT)


MOS_FEINA = dict(MOS)
MOS_FEINA.update({'legs': WORK, 'top': WORK, 'shoes': BOOT, 'hooks': {'hair': ch.mos_hair, 'torso': mos_feina}})


@lru_cache(maxsize=None)
def _person(name, f, talk=False):
    spec = {'DIRECTORA_JOVE': DIRECTORA_JOVE, 'VET': VET, 'MOS_FEINA': MOS_FEINA}[name]
    return person(spec, f, talk=talk)


def stamp(cv, img, fx, fy, flip=False):
    """Enganxa un fotograma de persona amb els peus a (fx, fy) (els peus són a (34, 111) del fotograma)."""
    if flip:
        img = ImageOps.mirror(img)
        fx -= img.width - 1 - 2 * FEET[0]
    paste(cv, img, fx - FEET[0], fy - FEET[1])


def shadow(cv, cx, cy, rx, ry=4, k=0.6):
    darken(cv, cx - rx, cy - ry, cx + rx, cy + ry,
           lambda x, y: k * max(0.0, 1 - math.hypot((x - cx) / rx, (y - cy) / ry)) * 1.6, dither=True)


def held_crate(cv, x0, y0, w=24, h=17):
    """La caixa que porta en Mos, agafada per sota."""
    crate(cv, x0, y0, w, h, label=False, seed=4)
    gull(cv, x0 + w // 2, y0 + h // 2)


# ─── La pantalla ────────────────────────────────────────────────────────────

def _upper(cv, t=0.0):
    """Sostre, paret, finestral, porta, pilar i rètol (el que hi ha abans del terra)."""
    ceiling(cv)
    wall(cv, 0, W - 1, 22, FLOOR_Y - 1)
    window(cv, t)
    if _clip(cv, 10, 100, 120, FLOOR_Y):
        door(cv)
    # el pilar 7, repintat de nou: el de la fàbrica, que ara és la columna d'honor de l'estació
    if _clip(cv, PILAR_CX - 22, 22, PILAR_CX + 22, FLOOR_Y + 8):
        pillar(cv, PILAR_CX, 22, FLOOR_Y - 1, aged=False)
        cv.rect(PILAR_CX - 12, 171, PILAR_CX + 12, 179, GOLD, lambda x, y: 4.2 - (y - 171) * 0.3)    # placa de llautó
        cv.hline(PILAR_CX - 12, PILAR_CX + 12, 171, GOLD, 5.4)
        cv.hline(PILAR_CX - 12, PILAR_CX + 12, 179, GOLD, 2.0)
        for x in range(PILAR_CX - 9, PILAR_CX + 10, 2):            # unes ratlles gravades (la dedicatòria)
            cv.put(x, 174, GOLD, 1.6)
            if x < PILAR_CX + 5:
                cv.put(x, 176, GOLD, 1.8)
        for x in (PILAR_CX - 11, PILAR_CX + 11):
            cv.put(x, 175, GOLD, 5.6)
    sign(cv, t)


def estacio(cv, people=True, t=0.0):
    _upper(cv, t)
    floor_deck(cv)
    darken(cv, PILAR_CX - 21, FLOOR_Y, PILAR_CX + 21, FLOOR_Y + 7, lambda x, y: 0.7 - abs(x - PILAR_CX) / 32)
    # jardineres sota el finestral, i plantes grans
    planter(cv, 211, 357, 233, seed=1, tall=29, time=t)
    planter(cv, 539, 621, 233, seed=2, tall=32, time=(t * 2) % 1)
    if _clip(cv, 60, 160, 200, 270):
        big_plant(cv, 128, 267, seed=5, h=80)
    # cistella penjant amb una heura, a l'esquerra
    hang_ivy(cv, 61, 29, t)
    # la llançadora vella, aterrada, amb els tres components al lloc
    sx, sy = SHUTTLE
    if _clip(cv, sx - 5, sy - 60, sx + 190, sy + 70):
        shadow(cv, sx + 88, sy + 61, 107, 7, 0.45)
        shuttle(cv, sx, sy, aged=True)
        components(cv, sx, sy)
    beacon(cv, sx, sy, t)
    # caixes descarregades al costat de la cua
    crate(cv, 539, 283, 40, 29, seed=1)
    crate(cv, 547, 256, 32, 27, seed=2)
    crate(cv, 496, 301, 35, 24, seed=3)
    if people:
        # la directora espera a la porta; la Vet hi va, girada cap a ella; en Mos descarrega
        for name, f, x, y, flip, talk in (('DIRECTORA_JOVE', 'L', 88, 333, True, True), ('VET', 'L', 275, 344, False, False),
                                          ('MOS_FEINA', 'L', 603, 349, False, False)):
            if not _clip(cv, x - 40, y - 115, x + 40, H - 1):
                continue
            img = _person(name, f, talk)
            reflect(cv, img, x, y, flip=flip)
            shadow(cv, x, y, 17, 4, 0.7)
            stamp(cv, img, x, y, flip=flip)
        held_crate(cv, 584, 297, 24, 17)


def hang_ivy(cv, cx, top, t=0.0):
    """Un test penjat amb heura que cau."""
    if not _clip(cv, cx - 20, top, cx + 20, top + 105):
        return
    cv.vline(cx - 8, top, top + 32, STEEL, 5.0)
    cv.vline(cx + 8, top, top + 32, STEEL, 5.0)
    cv.put(cx - 8, top, STEEL, 6.6)
    cv.put(cx + 8, top, STEEL, 6.6)
    cv.disc(cx, top + 37, 12, 7, POT, lambda nx, ny: 3.6 - nx - ny * 0.6 + (1.2 if ny < -0.6 else 0))
    rnd = random.Random(8)
    for i in range(7):
        x = cx - 12 + i * 4 + rnd.uniform(-1, 1)
        ln = rnd.randint(19, 59)
        for s in range(ln):
            xx = x + math.sin(s / 6.7 + i) * 2.0
            xx += 1.9 * (s / 59) ** 1.5 * (math.sin(2 * math.pi * t - s / 19 + i * 0.3) - math.sin(-s / 19 + i * 0.3))
            yy = top + 37 + s
            if s % 4 == 0:                                             # fulles en forma de cor, alternades
                side = -1 if (s // 4) % 2 else 1
                cv.put(xx + side, yy, LEAF, 3.6 - s * 0.015)
                cv.put(xx + side * 2, yy, LEAF, 3.0 - s * 0.015)
                cv.put(xx + side, yy + 1, LEAF, 2.4)
                cv.put(xx + side * 2, yy + 1, LEAF, 2.0)
            cv.put(xx, yy, LEAF, 2.8 + (s % 4 == 1) * 1.0)


# ─── Animació de fons ──────────────────────────────────────────────────────
# Tot és funció de t ∈ [0, 1) i fa bucle (t=1 ≡ t=0); a t=0 cap efecte no canvia el fons quiet.
# (Les estrelles del finestral parpellegen dins _sky, amb el titil·leig de l'espai de 640.)

def dust(cv, t):
    """Pols que sura dins els raigs de sol: baixa a poc a poc i s'encén i s'apaga."""
    if not t:
        return
    X0, Y0, X1, Y1 = WIN
    rnd = random.Random(44)
    for xa, xb in PANES:
        for _ in range(9):
            u, v = rnd.random(), rnd.random()
            m = rnd.choice((1, 2, 3))
            b = math.sin(math.pi * (m * t)) ** 2 * rnd.uniform(0.5, 1.0)
            vv = (v + t) % 1                                         # baixa (una volta per bucle)
            y = Y0 + 13 + vv * (216 - Y0 - 13)
            tt = (y - Y0) / (FLOOR_Y + 4 - Y0)
            x = xa + 19 + tt * 11 + u * (xb - xa - 35) + 2.7 * math.sin(2 * math.pi * (t + u))
            if b > 0.15 and 0 <= x < W:
                cv.flat(x, y, mix(cv.get(x, y), (255, 240, 200), min(1.0, b)))
                if b > 0.7:                                          # les més brillants, amb un halo d'un píxel
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        cv.flat(x + dx, y + dy, mix(cv.get(x + dx, y + dy), (255, 240, 200), 0.3 * b))


def beacon(cv, sx, sy, t):
    """Una llumeta verda a l'aleta de la llançadora: dos cops per bucle (apagada a t=0)."""
    on = 0.25 <= t % 0.5 < 0.30
    if on:
        x, y = sx + 172, sy - 52
        cv.flat(x, y, (200, 255, 210)); cv.flat(x + 1, y, (170, 255, 190)); cv.flat(x + 2, y, (120, 230, 160))
        cv.flat(x + 1, y - 1, (150, 240, 175))
        glow(cv, x + 1, y, 9, (130, 255, 170), 0.6)


def grade(cv):
    """Color de conjunt: càlid a dalt (les franges del sostre) i blavós a prop de la Terra."""
    tint(cv, 0, 0, W - 1, 266, (255, 214, 160), lambda x, y: 0.10 * max(0.0, 1 - y / 267))
    ex, ey, er = EARTH
    tint(cv, 400, 80, W - 1, H - 1, (90, 150, 255), lambda x, y: 0.10 * max(0.0, 1 - math.hypot(x - ex, y - ey - 40) / 267))


def bg(cv, t=0.0):
    estacio(cv, t=t)
    dust(cv, t)
    grade(cv)
    vinyeta(cv, 0.45)


PROPS = {}

# Zones que es mouen (no es trepitgen): el rètol i la seva claror; el finestral, les jardineres, la pols, la
# llumeta de la llançadora (i la claror del rètol que hi baixa); l'heura.
_ANIM_BOXES = [
    (0, 0, W - 1, 95),
    (196, 96, 632, 236),
    (30, 96, 100, 140),
]


@lru_cache(maxsize=None)
def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv.img


def _ambient_frames(n=16):
    """Fotogrames de l'animació de fons: només els píxels que canvien respecte del fons quiet."""
    return clip_frames(bg, LIGHT, n, _ANIM_BOXES, base=_base())


ANIMS = {'ambient': {'frames': _ambient_frames, 'frameDuration': 110}}
