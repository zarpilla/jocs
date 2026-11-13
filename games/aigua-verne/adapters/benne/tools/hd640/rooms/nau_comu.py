"""
Peces comunes de la Cantimplora (cantimplora_pont, cantimplora_bodega) i de les cinemàtiques (portada, crèdits).

La Cantimplora és una nau cisterna vella: planxa verd oliva, franges taronja de seguretat, reblons, rovell que
regalima, llums càlids de filament. Aquí hi ha:
  - les rampes de color (fosc → clar) de la nau i de fora;
  - la paret de planxa, el terra de xapa d'escates, les bombetes de filament amb reixa, les franges de perill,
    el rètol d'estergit;
  - el que es veu per les finestres a cada planeta (`vista`): Terra-2, Aqua, Ferrum i Verdant, amb la Canonada;
  - la cara del Magnat a la pantalla (`cara_verne`);
  - la gota blava de Verne i un dipòsit orbital (per a la portada).
"""
import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)

import math

from hd.pix import Canvas, hr, mix, RUST, B4
from hd.rooms.comu import text, text_width
from hd.rooms.exterior import fbm, smooth

# ─── Rampes (fosc → clar) ───────────────────────────────────────────────────
OLIVE = [(12, 14, 8), (22, 25, 13), (33, 37, 19), (46, 51, 26), (61, 66, 34), (78, 83, 43), (97, 101, 54),
         (118, 120, 68), (142, 142, 86), (168, 166, 110)]
SAFETY = [(44, 14, 6), (86, 30, 10), (134, 50, 14), (182, 76, 22), (222, 106, 32), (244, 146, 58), (255, 196, 120)]
DECKP = [(10, 10, 9), (18, 18, 15), (28, 27, 22), (40, 38, 31), (54, 51, 41), (70, 66, 53), (90, 84, 67),
         (114, 106, 84), (142, 132, 104)]
STEELN = [(12, 13, 15), (22, 24, 27), (34, 37, 41), (48, 52, 57), (64, 69, 74), (84, 89, 94), (108, 113, 117),
          (138, 142, 144), (172, 175, 174), (208, 210, 206)]
LEATHER = [(22, 12, 8), (38, 21, 13), (58, 33, 19), (80, 47, 27), (104, 64, 37), (130, 84, 50), (156, 108, 66),
           (182, 134, 86)]
TAPE = [(48, 48, 50), (78, 78, 80), (112, 112, 112), (146, 146, 144), (182, 182, 178)]
AMBER = [(30, 14, 4), (64, 32, 8), (112, 62, 12), (170, 100, 22), (220, 148, 40), (250, 200, 90), (255, 240, 180)]
GLASSD = [(4, 8, 14), (8, 14, 24), (14, 22, 36), (22, 32, 50), (34, 46, 66), (50, 64, 86), (72, 88, 110)]
BULB = [(120, 70, 30), (200, 130, 50), (250, 200, 110), (255, 238, 190), (255, 252, 236)]
REDK = [(30, 6, 6), (70, 12, 10), (120, 22, 16), (176, 38, 24), (220, 70, 44), (250, 130, 96)]
GREENK = [(6, 24, 10), (12, 50, 20), (24, 90, 36), (50, 150, 64), (120, 220, 120), (200, 255, 190)]
WOODB = [(26, 15, 9), (44, 27, 15), (66, 42, 23), (90, 59, 32), (116, 78, 43), (142, 99, 56), (168, 122, 72),
         (194, 150, 96)]
CORK = [(52, 32, 16), (86, 56, 28), (122, 84, 44), (156, 112, 62), (186, 140, 84), (212, 170, 110)]
PAPERN = [(70, 64, 54), (120, 112, 96), (168, 160, 138), (204, 196, 172), (228, 222, 200), (246, 242, 226)]
CLOTH = [(40, 32, 20), (70, 58, 38), (104, 88, 60), (138, 120, 84), (168, 150, 108), (196, 180, 136),
         (220, 208, 166)]
WBLUE = [(8, 20, 48), (14, 38, 86), (24, 62, 132), (40, 96, 180), (78, 140, 220), (140, 192, 244), (210, 234, 255)]
WHITEV = [(92, 100, 112), (132, 140, 150), (172, 178, 186), (204, 208, 214), (228, 230, 234), (244, 245, 247),
          (254, 254, 255)]
COL = [(120, 120, 122), (150, 150, 150), (176, 176, 174), (198, 196, 192), (216, 214, 208), (232, 230, 224),
       (244, 242, 236)]
BLACKT = [(6, 6, 8), (14, 14, 16), (24, 24, 26), (36, 36, 38), (52, 52, 54), (72, 72, 74)]
LED = [(30, 6, 4), (90, 20, 10), (180, 50, 20), (250, 120, 40), (255, 200, 120)]

WARM = (255, 196, 110)
INK = (16, 12, 10)


# ─── Ajudes de dibuix ──────────────────────────────────────────────────────

def box(cv, x0, y0, x1, y1, ramp, lvl, edge=True, grad=0.0, lit=1.0):
    """Capsa plana: llum a dalt i a l'esquerra, ombra a baix i a la dreta, i un contorn fosc d'1 px."""
    cv.rect(x0, y0, x1, y1, ramp, lambda x, y: lvl - grad * (y - y0) / max(1, y1 - y0), lit)
    if edge:
        cv.hline(x0, x1, y0, ramp, lvl + 1.3, lit)
        cv.vline(x0, y0, y1, ramp, lvl + 0.7, lit)
        cv.hline(x0, x1, y1, ramp, lvl - 1.5, lit)
        cv.vline(x1, y0, y1, ramp, lvl - 1.1, lit)


def outline(cv, x0, y0, x1, y1, col=INK):
    for x in range(x0, x1 + 1):
        cv.flat(x, y0, col)
        cv.flat(x, y1, col)
    for y in range(y0, y1 + 1):
        cv.flat(x0, y, col)
        cv.flat(x1, y, col)


def rivet(cv, x, y, ramp=OLIVE, lvl=4.0):
    cv.put(x, y, ramp, lvl + 1.6)
    cv.put(x + 1, y + 1, ramp, lvl - 1.8)
    cv.put(x + 1, y, ramp, lvl)


def vpipe(cv, xc, y0, y1, r, ramp, lvl, bands=(), band_ramp=None, lit=1.0):
    for y in range(int(y0), int(y1) + 1):
        band = any(b <= y < b + 3 for b in bands)
        for x in range(xc - r, xc + r + 1):
            u = (x - xc) / (r + 0.5)
            cv.put(x, y, band_ramp if band else ramp, lvl + 1.5 * (-0.2 - u) - 0.7 * u * u, lit)


def hpipe(cv, x0, x1, yc, r, ramp, lvl, bands=(), band_ramp=None, lit=1.0):
    for x in range(int(x0), int(x1) + 1):
        band = any(b <= x < b + 3 for b in bands)
        for y in range(yc - r, yc + r + 1):
            u = (y - yc) / (r + 0.5)
            cv.put(x, y, band_ramp if band else ramp, lvl + 1.5 * (0.3 - u) - 0.7 * u * u, lit)


def hazard(cv, x0, y0, x1, y1, lvl=3.6, step=6, lit=1.0):
    """Franja de perill: diagonals taronja i negres."""
    for y in range(int(y0), int(y1) + 1):
        for x in range(int(x0), int(x1) + 1):
            if ((x + y) // step) % 2:
                cv.put(x, y, SAFETY, lvl + (hr(x // 3, y // 2, 77) - 0.5) * 0.8, lit)
            else:
                cv.put(x, y, BLACKT, 2.2, lit)
    # la pintura gastada: rascades
    for x in range(int(x0), int(x1) + 1):
        for y in range(int(y0), int(y1) + 1):
            if hr(x, y, 78) > 0.93:
                cv.put(x, y, RUST, 2.6, lit)


def stencil(cv, s, x, y, ramp=OLIVE, lvl=7.4, lit=1.0, worn=0.18, seed=5):
    """Rètol d'estergit (la font petita) amb la pintura gastada: alguns píxels hi falten."""
    tmp = []

    class _Cap:
        def put(self, px, py, ramp_, lvl_, lit_=1.0):
            tmp.append((px, py))

        def flat(self, px, py, col):
            tmp.append((px, py))
    w = text(_Cap(), s, x, y, ramp, lvl)
    for px, py in tmp:
        if hr(px, py, seed) > worn:
            cv.put(px, py, ramp, lvl, lit)
    return w


def plate_wall(cv, x0, y0, x1, y1, lvl=3.4, pw=72, ph=46, seed=3, rust=1.0, ramp=OLIVE):
    """Paret de planxa: plaques amb juntes, fileres de reblons, taques i regalims de rovell."""
    def L(x, y):
        px, py = (x - x0) // pw, (y - y0) // ph
        v = lvl + (hr(px, py, seed) - 0.5) * 0.7 + (fbm(x / 26, y / 18, seed) - 0.5) * 1.0
        # ondulació de la planxa vella
        v += 0.35 * math.sin((x - x0) / pw * math.pi * 2 + py) * 0.5
        return v
    cv.rect(x0, y0, x1, y1, ramp, L)
    for y in range(y0, y1 + 1):
        if (y - y0) % ph == 0 and y > y0:
            cv.hline(x0, x1, y, ramp, lvl - 1.8)
            cv.hline(x0, x1, y + 1, ramp, lvl + 0.9)
    for x in range(x0, x1 + 1):
        if (x - x0) % pw == 0 and x > x0:
            cv.vline(x, y0, y1, ramp, lvl - 1.6)
            cv.vline(x + 1, y0, y1, ramp, lvl + 0.7)
    # reblons al llarg de les juntes
    for y in range(y0 + ph, y1, ph):
        for x in range(x0 + 4, x1 - 2, 8):
            rivet(cv, x, y - 3, ramp, lvl)
    for x in range(x0 + pw, x1, pw):
        for y in range(y0 + 5, y1 - 2, 8):
            rivet(cv, x - 3, y, ramp, lvl)
    # rovell: taques i regalims que baixen dels reblons
    if rust:
        for k in range(int((x1 - x0) * (y1 - y0) / 1400 * rust)):
            rx = x0 + int(hr(k, seed, 1) * (x1 - x0))
            ry = y0 + int(hr(k, seed, 2) * (y1 - y0))
            n = 4 + int(hr(k, seed, 3) * 22)
            for j in range(n):
                xx = rx + (1 if hr(k, j, 4) > 0.85 else 0)
                a = 1 - j / n
                if hr(k, j, 5) < 0.15 + 0.6 * a:
                    cv.put(xx, ry + j, RUST, 1.0 + a * 1.4)
            if hr(k, 7) > 0.4:
                cv.disc(rx, ry, 1.5 + hr(k, 6) * 2.5, 1.0 + hr(k, 8), RUST,
                        lambda nx, ny: 1.6 + nx * 0.4 + (hr(int(nx * 9), int(ny * 9), k) - 0.5))


def deck(cv, x0, y0, x1, y1, lvl=3.2, seed=9):
    """Terra de xapa d'escates (xapa estriada), gastada pel mig, amb perspectiva cap al fons."""
    for y in range(y0, y1 + 1):
        t = (y - y0) / max(1, y1 - y0)
        sy = 3 + int(t * 3)                                      # les escates es fan grans cap a davant
        for x in range(x0, x1 + 1):
            u = (x - 320) * (0.7 + 0.3 * (1 - t)) + 320
            gx, gy = int(u // (sy * 2)), (y - y0) // sy
            cx = u - (gx + 0.5) * sy * 2
            cy = (y - y0) - (gy + 0.5) * sy
            stud = (cx + cy * (1 if (gx + gy) % 2 else -1)) ** 2 < 2.0 and abs(cy) < sy * 0.45
            v = lvl + (fbm(x / 60, y / 14, seed) - 0.5) * 1.2
            v += (hr(x // 4, y // 3, seed) - 0.5) * 0.4
            if stud:
                v += 1.2
            # les juntes de les planxes de terra
            if (y - y0) in (int((y1 - y0) * 0.22), int((y1 - y0) * 0.55)) or int(u) % 128 == 0:
                v -= 1.8
            cv.put(x, y, DECKP, v)
    for y in (y0, y0 + 1):
        cv.hline(x0, x1, y, DECKP, lvl - 1.6 if y == y0 else lvl + 1.0)


def bulb(cv, x, y, cable=8, on=True):
    """Bombeta de filament dins d'una reixa, penjada d'un cable. (x, y): el centre del vidre."""
    for yy in range(y - cable - 4, y - 4):
        cv.put(x, yy, BLACKT, 2.0, lit=0)
    cv.rect(x - 3, y - 6, x + 3, y - 4, STEELN, 3.0, lit=0)        # el portalàmpades
    cv.hline(x - 3, x + 3, y - 6, STEELN, 5.0, lit=0)
    if on:
        cv.glow(x, y + 2, 34, WARM, 0.5)
        cv.glow(x, y + 2, 12, (255, 236, 190), 0.7)
        cv.disc(x, y + 1, 3.5, 4.2, BULB, lambda nx, ny: 3.6 - ny * 0.8 - abs(nx) * 0.8, lit=0)
        cv.flat(x, y, (255, 255, 244))
        cv.flat(x, y + 1, (255, 255, 244))
    else:
        cv.disc(x, y + 1, 3.5, 4.2, GLASSD, 3.0, lit=0)
    for dx in (-5, -2, 2, 5):                                      # la reixa
        for yy in range(y - 3, y + 7):
            if abs(dx) < 5 or y - 1 <= yy <= y + 4:
                cv.put(x + dx, yy, BLACKT, 3.0 if dx < 0 else 2.0, lit=0)
    cv.hline(x - 5, x + 5, y + 7, BLACKT, 2.4, lit=0)


def label(cv, s, x, y, ramp=PAPERN, lvl=4.4, ink=INK):
    """Plaqueta de paper o llautó amb text de 5 px."""
    w = text_width(s)
    box(cv, x - 2, y - 2, x + w + 1, y + 6, ramp, lvl)
    text(cv, s, x, y, None, 0, flat=ink)
    return w


def drop(cv, cx, cy, r, ramp=WBLUE, lvl=3.6, lit=0):
    """La gota blava de Verne: un cercle amb la punta a dalt."""
    cv.disc(cx, cy, r, r, ramp, lambda nx, ny: lvl - nx * 0.8 - ny * 0.6, lit)
    h = int(r * 1.5)
    for j in range(h):
        w = r * (j / h) ** 1.25
        for x in range(int(cx - w), int(cx + w) + 1):
            cv.put(x, cy - h + j, ramp, lvl - (x - cx) / max(1, r) * 0.8 + 0.4, lit)
    if r >= 3:
        cv.put(cx - r // 2, cy - 1, ramp, lvl + 2.6, lit)


# ─── La Canonada ───────────────────────────────────────────────────────────

def canonada(cv, x, y0, y1, w0=1.5, w1=4.0, ring=11, haze=(230, 214, 180), haze_k=0.35, light_y=None, lit=0,
             clip=None):
    """La columna de Verne: blanca, amb anelles, des de l'horitzó (y1) fins al cel (y0). `clip`: (x0, y0, x1, y1)."""
    for y in range(int(y0), int(y1) + 1):
        t = (y - y0) / max(1, y1 - y0)
        w = w0 + (w1 - w0) * t
        for xx in range(int(x - w), int(x + w) + 1):
            if clip and not (clip[0] <= xx <= clip[2] and clip[1] <= y <= clip[3]):
                continue
            u = (xx - x) / max(1.0, w)
            lvl = 3.4 - u * 1.6 + (0.9 if y % ring == 0 else 0) - (0.7 if y % ring == 1 else 0)
            cv.put(xx, y, COL, lvl, lit)
    if haze:
        cx0, cy0, cx1, cy1 = clip or (0, 0, cv.w - 1, cv.h - 1)
        cv.tint(max(cx0, x - w1 - 2), max(cy0, y0), min(cx1, x + w1 + 2), min(cy1, y1), haze,
                lambda xx, yy: haze_k * (1 - (yy - y0) / max(1, y1 - y0)) * 0.6 + haze_k * 0.25)
    if light_y is not None:
        cv.flat(x, light_y, (230, 40, 30))


# ─── Les vistes de fora (una per planeta) ──────────────────────────────────
# `vista(cv, planeta, rect, hor, s)`: dibuixa el que es veu per una obertura dins `rect` (x0, y0, x1, y1), amb
# l'horitzó a `hor` i les coses del fons a escala `s` (1 = la vista del finestral del pont). Sense llum de sala.

SKY_T2 = [(150, 128, 98), (174, 152, 118), (194, 174, 138), (212, 194, 156), (226, 210, 172), (238, 224, 188),
          (246, 236, 204), (252, 246, 222)]
HILL_T2 = [(110, 88, 70), (130, 106, 84), (150, 126, 100), (170, 146, 118), (190, 168, 138), (204, 184, 154)]
EARTH_T2 = [(64, 44, 30), (90, 64, 42), (118, 88, 58), (146, 112, 74), (172, 136, 92), (196, 160, 114),
            (216, 184, 138), (232, 206, 162)]
SKY_AQ = [(120, 150, 172), (146, 174, 194), (170, 196, 212), (192, 214, 226), (210, 228, 236), (226, 238, 244),
          (240, 246, 250)]
SALT = [(120, 124, 126), (150, 154, 154), (178, 182, 180), (202, 206, 202), (222, 224, 220), (238, 240, 236),
        (250, 250, 248)]
STONE_AQ = [(70, 72, 74), (96, 98, 98), (124, 126, 124), (152, 152, 148), (180, 178, 172), (204, 202, 196)]
HULL_AQ = [(20, 24, 30), (34, 40, 48), (52, 58, 66), (74, 80, 86), (98, 104, 108)]
REDH = [(50, 14, 12), (86, 26, 20), (124, 40, 28), (160, 58, 40), (188, 84, 60)]
SKY_FE = [(56, 44, 42), (78, 60, 52), (102, 76, 60), (130, 92, 66), (160, 108, 70), (190, 128, 76), (214, 150, 88),
          (234, 178, 110)]
BRICK_FE = [(16, 12, 12), (26, 18, 16), (38, 26, 22), (52, 34, 28), (68, 44, 34), (86, 56, 40)]
SKY_VE = [(30, 90, 190), (44, 112, 214), (62, 136, 232), (88, 162, 244), (120, 188, 250), (162, 214, 255),
          (206, 236, 255)]
GRASS_VE = [(10, 70, 20), (16, 104, 26), (26, 140, 34), (44, 176, 44), (80, 210, 60), (140, 240, 90),
            (200, 255, 150)]
CLOUD_VE = [(176, 198, 230), (210, 226, 246), (234, 242, 252), (250, 252, 255)]


class _Clip:
    """Un llenç que només pinta dins `rect`: s'hi poden fer servir els mètodes de Canvas (poly, disc, rect...)."""

    def __init__(self, cv, rect):
        self.cv, self.r = cv, rect
        self.w, self.h = cv.w, cv.h
        self.P = cv.P

    def put(self, x, y, ramp, lvl, lit=1.0):
        if _in(self.r, int(x), int(y)):
            self.cv.put(x, y, ramp, lvl, lit)

    def flat(self, x, y, col):
        if _in(self.r, int(x), int(y)):
            self.cv.flat(x, y, col)

    def get(self, x, y):
        return self.cv.get(x, y)

    def glow(self, cx, cy, r, col, strength):
        x0, y0, x1, y1 = self.r
        for y in range(max(y0, int(cy - r)), min(y1, int(cy + r)) + 1):
            for x in range(max(x0, int(cx - r)), min(x1, int(cx + r)) + 1):
                d = math.hypot(x - cx, y - cy) / r
                if d < 1:
                    a = strength * (1 - d) ** 2
                    o = self.P[x, y]
                    if o[3] and a > B4[y & 3][x & 3] * 0.35:
                        self.P[x, y] = mix(o, col, min(1, a)) + (o[3],)


def _in(rect, x, y):
    return rect[0] <= x <= rect[2] and rect[1] <= y <= rect[3]


def _fill(cv, rect, fn):
    x0, y0, x1, y1 = rect
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            fn(x, y)


def _crane(cv, rect, x, base, s, ramp, lvl):
    """Una grua de port parada, en silueta (torre de gelosia i braç)."""
    top = base - int(70 * s)
    for y in range(top, base + 1):
        for dx in (0, int(6 * s)):
            if _in(rect, x + dx, y):
                cv.put(x + dx, y, ramp, lvl, lit=0)
        if (y - top) % max(3, int(6 * s)) == 0:
            for k in range(int(6 * s) + 1):
                if _in(rect, x + k, y):
                    cv.put(x + k, y, ramp, lvl, lit=0)
            for k in range(int(6 * s) + 1):
                yy = y + int(k * 0.8)
                if _in(rect, x + k, yy) and yy <= base:
                    cv.put(x + k, yy, ramp, lvl, lit=0)
    arm = int(70 * s)
    for k in range(-int(20 * s), arm):
        for j in (0, 1):
            if _in(rect, x + k, top + j):
                cv.put(x + k, top + j, ramp, lvl, lit=0)
        if k % 5 == 0 and _in(rect, x + k, top + 2):
            cv.put(x + k, top + 2, ramp, lvl, lit=0)
    for j in range(int(26 * s)):                                   # el cable i el ganxo
        if _in(rect, x + arm - 8, top + 2 + j):
            cv.put(x + arm - 8, top + 2 + j, ramp, lvl, lit=0)
    cab = (x - int(2 * s), top + 3, x + int(8 * s), top + int(10 * s))
    for yy in range(cab[1], cab[3]):
        for xx in range(cab[0], cab[2]):
            if _in(rect, xx, yy):
                cv.put(xx, yy, ramp, lvl, lit=0)


def _containers(cv, rect, x, base, s, cols, seed):
    """Contenidors apilats: (x, base) cantó de baix a l'esquerra."""
    cw, ch = int(26 * s), int(10 * s)
    for i, (ramp, n) in enumerate(cols):
        for j in range(n):
            x0 = x + i * (cw + 1) - (j * int(5 * s))
            y1 = base - j * ch
            for yy in range(y1 - ch + 1, y1 + 1):
                for xx in range(x0, x0 + cw):
                    if _in(rect, xx, yy):
                        rib = (xx - x0) % 3 == 0
                        cv.put(xx, yy, ramp, 2.6 - (0.8 if rib else 0) - (1.2 if yy == y1 else 0) +
                               (1.0 if yy == y1 - ch + 1 else 0), lit=0)
            if ramp is WHITEV and s >= 0.8:                         # el contenidor de Verne, amb la gota
                cx, cy = x0 + cw // 2, y1 - ch // 2
                if _in(rect, cx, cy):
                    cv.flat(cx, cy, WBLUE[3])
                    cv.flat(cx, cy - 1, WBLUE[3])
                    cv.flat(cx + 1, cy, WBLUE[2])


def vista(cv, planeta, rect, hor, s=1.0, seed=0, refl=True, canonada_x=None):
    x0, y0, x1, y1 = rect
    W_ = x1 - x0
    fx = lambda f: int(x0 + W_ * f)                                # noqa: E731
    if planeta == 'terra2':
        sun = (fx(0.86), y0 + int((hor - y0) * 0.2))

        def sky(x, y):
            t = (y - y0) / max(1, hor - y0)
            d = math.hypot(x - sun[0], (y - sun[1]) * 1.3)
            lvl = 1.8 + 3.8 * t ** 0.8 + 2.6 * max(0.0, 1 - d / (130 * s)) ** 2
            lvl += (fbm(x / 90, y / 14, 31 + seed) - 0.5) * 0.8
            cv.put(x, y, SKY_T2, lvl, lit=0)
        _fill(cv, (x0, y0, x1, hor), sky)
        c = _Clip(cv, rect)
        c.glow(sun[0], sun[1], 22 * s, (255, 250, 228), 0.9)
        Canvas.disc(c, sun[0], sun[1], 5 * s, 5 * s, SKY_T2, 7.6, lit=0)
        for x in range(x0, x1 + 1):                                # turons
            h1 = hor - 4 * s - 10 * s * fbm(x / 70, 0.3, 7 + seed)
            for y in range(int(h1), hor + 1):
                cv.put(x, y, HILL_T2, 4.2 - (y - h1) * 0.05, lit=0)
        canonada(cv, canonada_x or fx(0.34), y0, hor - 2, 1.0, 1.8 + 1.6 * s, light_y=y0 + int(10 * s),
                 clip=rect)
        _fill(cv, (x0, hor + 1, x1, y1), lambda x, y: cv.put(
            x, y, EARTH_T2, 4.6 - (y - hor) * 0.02 + (fbm(x / 22, y / 5, 11 + seed) - 0.5) * 1.2 +
            (0.8 if hr(x // 3, y // 2, 4) > 0.9 else 0), lit=0))
        _crane(cv, rect, fx(0.58), hor + int(3 * s), s, RUST, 1.6)
        _containers(cv, rect, fx(0.06), hor + int(5 * s), s, ((WHITEV, 2), (RUST, 1), (WHITEV, 1)), seed)
        cv.tint(x0, y0, x1, y1, (226, 206, 160), lambda x, y: 0.12 + 0.18 * max(0, 1 - abs(y - hor) / 30))
    elif planeta == 'aqua':
        def sky(x, y):
            t = (y - y0) / max(1, hor - y0)
            lvl = 1.4 + 5.0 * t ** 0.9 + (fbm(x / 120, y / 10, 41 + seed) - 0.5) * 0.6
            cv.put(x, y, SKY_AQ, lvl, lit=0)
        _fill(cv, (x0, y0, x1, hor), sky)
        canonada(cv, canonada_x or fx(0.72), y0, hor - 1, 1.0, 1.6 + 1.4 * s, haze=(230, 238, 244),
                 light_y=y0 + int(12 * s), clip=rect)
        # el fons del mar, sec: sal blanca fins a l'horitzó, amb ratlles d'antigues onades
        _fill(cv, (x0, hor, x1, y1), lambda x, y: cv.put(
            x, y, SALT, 5.2 - (y - hor) * 0.012 + (0.7 if int((y - hor) * 1.7 + 2 * math.sin(x / 13)) % 9 == 0
                                                    else 0) + (fbm(x / 30, y / 4, 43) - 0.5) * 0.8, lit=0))
        # un vaixell de càrrega encallat i ajagut sobre la sal, i una barca petita
        c = _Clip(cv, rect)
        bx, by = fx(0.12), hor + int(5 * s)
        ang = math.radians(-7)

        def R(px, py):
            return (bx + px * s * math.cos(ang) - py * s * math.sin(ang), by + px * s * math.sin(ang) + py * s *
                    math.cos(ang))
        hull = [R(0, -14), R(70, -14), R(78, -20), R(80, -14), R(74, 0), R(6, 0)]
        Canvas.poly(c, hull, HULL_AQ, lambda x, y: 2.6 + (0.6 if (x - bx) % 9 == 0 else 0), lit=0)
        Canvas.poly(c, [R(4, -5), R(76, -5), R(74, 0), R(6, 0)], REDH, 2.2, lit=0)          # l'obra viva, rovellada
        Canvas.poly(c, [R(2, -14), R(74, -14), R(74, -13), R(2, -13)], HULL_AQ, 4.2, lit=0)
        Canvas.poly(c, [R(6, -14), R(20, -14), R(20, -27), R(8, -27)], SALT, 3.8, lit=0)    # el pont, a popa
        for i in range(3):
            Canvas.poly(c, [R(9 + i * 4, -24), R(11 + i * 4, -24), R(11 + i * 4, -22), R(9 + i * 4, -22)],
                        HULL_AQ, 1.2, lit=0)
        Canvas.line(c, *R(14, -27), *R(14, -38), HULL_AQ, 2.2, lit=0)                         # el pal
        for i in range(4):                                                                   # les escotilles
            Canvas.poly(c, [R(28 + i * 11, -14), R(36 + i * 11, -14), R(36 + i * 11, -17), R(28 + i * 11, -17)],
                        REDH, 3.4, lit=0)
        Canvas.disc(c, bx + 40 * s, by + 2 * s, 46 * s, 3 * s, SALT, 6.0, lit=0)             # la sal amuntegada
        sbx, sby = fx(0.66), hor + int(9 * s)                                                  # la barca
        Canvas.poly(c, [(sbx, sby - 4 * s), (sbx + 22 * s, sby - 7 * s), (sbx + 19 * s, sby), (sbx + 2 * s, sby)],
                    [(40, 70, 96), (60, 100, 130), (90, 130, 156), (130, 170, 190)], 1.8, lit=0)
        Canvas.line(c, sbx, sby - 4 * s, sbx + 22 * s, sby - 7 * s, SALT, 5.0, lit=0)
        # el moll de pedra blanca, a primer terme
        mh = int(8 * s)
        for x in range(x0, x1 + 1):
            for y in range(max(y0, y1 - mh), y1 + 1):
                joint = (x // int(14 * s + 1)) % 1 == 0 and x % int(14 * s + 1) == 0
                cv.put(x, y, STONE_AQ, 4.4 - (y - (y1 - mh)) * 0.25 - (1.6 if joint else 0), lit=0)
        cv.tint(x0, y0, x1, y1, (236, 244, 250), lambda x, y: 0.14)
    elif planeta == 'ferrum':
        fire = (fx(0.5), hor)

        def sky(x, y):
            t = (y - y0) / max(1, hor - y0)
            d = math.hypot(x - fire[0], (y - fire[1]) * 1.6)
            lvl = 1.4 + 3.0 * t + 2.4 * max(0.0, 1 - d / (120 * s)) ** 1.5
            lvl += (fbm(x / 50, y / 9, 51 + seed) - 0.5) * 2.2                    # fum
            cv.put(x, y, SKY_FE, lvl, lit=0)
        _fill(cv, (x0, y0, x1, hor), sky)
        canonada(cv, canonada_x or fx(0.18), y0, hor - 1, 1.0, 1.6 + 1.4 * s, haze=(150, 110, 84), haze_k=0.4,
                 light_y=y0 + int(14 * s), clip=rect)
        # xemeneies de la fosa i cases de maó, en silueta, amb finestres enceses
        for i, (fxx, hh, ww) in enumerate(((0.36, 54, 6), (0.44, 70, 7), (0.62, 48, 5), (0.9, 40, 5))):
            cx = fx(fxx)
            for y in range(hor - int(hh * s), hor + 1):
                for x in range(cx - int(ww * s / 2), cx + int(ww * s / 2) + 1):
                    if _in(rect, x, y):
                        cv.put(x, y, BRICK_FE, 1.4 + (0.8 if (y // 3) % 4 == 0 else 0), lit=0)
            top = hor - int(hh * s)
            for k in range(int(30 * s)):                           # el fum que en surt
                xx = cx + int(k * 0.9 + math.sin(k / 3) * 2)
                yy = top - k
                for d in range(-int(1 + k / 6), int(2 + k / 6)):
                    if _in(rect, xx + d, yy) and hr(xx + d, yy, 52) > 0.3:
                        cv.flat(xx + d, yy, mix(cv.get(xx + d, yy), (70, 58, 56), 0.5))
            if _in(rect, cx, top):
                cv.glow(cx, top, 6 * s, (255, 140, 60), 0.6)
        for x in range(x0, x1 + 1):                                # la filera de cases
            hh = hor - int((8 + 10 * (hr(int((x - x0) // (16 * s + 1)), 61) > 0.5)) * s)
            roof = hh - (2 if int((x - x0) % (16 * s + 1)) < 2 else 0)
            for y in range(roof, y1 + 1):
                if _in(rect, x, y):
                    win = y < hor + 2 and (int((x - x0) % (8 * s + 1)) in (3, 4)) and (y - hh) % 6 in (3, 4) \
                        and hr(int(x // 8), y // 6, 63) > 0.55
                    if win:
                        cv.flat(x, y, (250, 170, 70))
                    else:
                        cv.put(x, y, BRICK_FE, 2.0 + (y - roof) * 0.02 - (y - hor) * 0.05, lit=0)
        _fill(cv, (x0, hor + 4, x1, y1), lambda x, y: cv.put(
            x, y, BRICK_FE, 2.2 + (fbm(x / 14, y / 4, 64) - 0.5) * 1.4, lit=0))
        cv.tint(x0, y0, x1, y1, (200, 120, 60), lambda x, y: 0.1)
    elif planeta == 'verdant':
        def sky(x, y):
            t = (y - y0) / max(1, hor - y0)
            lvl = 1.4 + 4.6 * t ** 1.2
            cv.put(x, y, SKY_VE, lvl, lit=0)
        _fill(cv, (x0, y0, x1, hor), sky)
        # núvols d'anunci: perfectes, rodons, blancs
        for k, (cxf, cyf, r) in enumerate(((0.2, 0.25, 9), (0.28, 0.22, 12), (0.36, 0.27, 8), (0.74, 0.4, 10),
                                           (0.82, 0.36, 13), (0.9, 0.42, 8))):
            cx, cy = fx(cxf), y0 + int((hor - y0) * cyf)
            rr = r * s
            for y in range(int(cy - rr), int(cy + rr * 0.6) + 1):
                for x in range(int(cx - rr), int(cx + rr) + 1):
                    if _in(rect, x, y) and (x - cx) ** 2 + (y - cy) ** 2 <= rr * rr:
                        cv.put(x, y, CLOUD_VE, 3.4 - (y - cy) / rr * 1.2 - (x - cx) / rr * 0.4, lit=0)
            for x in range(int(cx - rr * 1.6), int(cx + rr * 1.6) + 1):                 # la base plana
                for y in range(int(cy + rr * 0.3), int(cy + rr * 0.6) + 1):
                    if _in(rect, x, y):
                        cv.put(x, y, CLOUD_VE, 1.8, lit=0)
        canonada(cv, canonada_x or fx(0.56), y0, hor - 1, 1.0, 1.4 + 1.2 * s, haze=(170, 210, 250), haze_k=0.3,
                 light_y=y0 + int(12 * s), clip=rect)
        # la residència blanca, amb columnes
        rx0, rx1, rtop = fx(0.08), fx(0.42), hor - int(26 * s)
        for y in range(rtop, hor + 1):
            for x in range(rx0, rx1 + 1):
                if _in(rect, x, y):
                    col_ = (x - rx0) % int(7 * s + 1) < 2 and y > rtop + 4 * s
                    win = (x - rx0) % int(7 * s + 1) in (3, 4) and rtop + 8 * s < y < hor - 3
                    cv.put(x, y, WHITEV, (5.6 if col_ else 4.4) - (1.8 if win else 0) - (1.0 if y < rtop + 4 * s
                                                                                          else 0), lit=0)
        for x in range(rx0 - 2, rx1 + 3):
            if _in(rect, x, rtop - 1):
                cv.put(x, rtop - 1, WHITEV, 6.0, lit=0)
        # gespa perfecta a ratlles de tallar i flors de plàstic
        _fill(cv, (x0, hor + 1, x1, y1), lambda x, y: cv.put(
            x, y, GRASS_VE, 3.6 + (0.9 if ((x + (y - hor) * 2) // int(10 * s + 1)) % 2 else -0.2) +
            (y - hor) * 0.02, lit=0))
        for k in range(int(W_ * (y1 - hor) / 30)):
            px = x0 + int(hr(k, 71) * W_)
            py = hor + 2 + int(hr(k, 72) * (y1 - hor - 2))
            if _in(rect, px, py):
                cv.flat(px, py, ((255, 40, 120), (255, 220, 0), (255, 90, 30), (160, 60, 255))[k % 4])
        # una brillantor excessiva
        cv.tint(x0, y0, x1, y1, (255, 255, 255), lambda x, y: 0.06)
    else:                                                          # nit, a l'hangar: només fosc i estrelles
        _fill(cv, (x0, y0, x1, y1), lambda x, y: cv.put(x, y, GLASSD, 1.6 + (y - y0) / max(1, y1 - y0) * 1.2,
                                                         lit=0))
        for k in range(int(W_ * (y1 - y0) / 140)):
            px, py = x0 + int(hr(k, 81) * W_), y0 + int(hr(k, 82) * (y1 - y0) * 0.7)
            cv.flat(px, py, (120, 130, 150) if hr(k, 83) > 0.4 else (200, 210, 230))
    if refl:
        glass_reflex(cv, rect)


def glass_reflex(cv, rect, k=0.16):
    """Reflexos del vidre: dues bandes diagonals més clares."""
    x0, y0, x1, y1 = rect

    def m(x, y):
        d = (x - x0) + (y - y0) * 0.9
        W_ = x1 - x0
        a = 1.0 if 0.18 * W_ < d % (W_ * 0.9) < 0.18 * W_ + 9 else 0.0
        b = 1.0 if 0.18 * W_ + 13 < d % (W_ * 0.9) < 0.18 * W_ + 16 else 0.0
        return max(a, b)
    cv.tint(x0, y0, x1, y1, (240, 244, 250), lambda x, y: k * m(x, y))


# ─── La cara del Magnat ────────────────────────────────────────────────────
SKINV = [(70, 38, 32), (112, 66, 52), (156, 102, 80), (196, 140, 112), (224, 176, 146), (242, 206, 178),
         (252, 228, 206)]
HAIRW = [(120, 124, 132), (164, 168, 176), (200, 204, 210), (226, 228, 232), (246, 246, 248)]
SUITW = [(132, 136, 146), (170, 174, 182), (206, 208, 214), (230, 232, 236), (246, 247, 249), (255, 255, 255)]
OFFICE = [(176, 186, 198), (202, 210, 220), (222, 228, 236), (236, 240, 245), (246, 248, 251), (252, 253, 255)]


def cara_verne(cv, rect):
    """L'Aurelià Verne a la pantalla, de pit en amunt: 67 anys, cabell blanc pentinat enrere, vestit blanc,
    somriure perfecte. Darrere, el blanc de l'oficina i la gota blava a la paret. Colors plans a la cara (sense
    trama: és una imatge de vídeo neta, d'anunci)."""
    x0, y0, x1, y1 = rect
    W_, H_ = x1 - x0, y1 - y0
    k = H_ / 84                                                     # tot es dibuixa per a 84 px d'alt
    cx = x0 + W_ // 2 - 6
    Y = lambda v: y0 + int(round(v * k))                            # noqa: E731
    S = SKINV
    # el fons: oficina blanca, una finestra de lamel·les a l'esquerra, la gota i el nom a la paret
    cv.rect(x0, y0, x1, y1, OFFICE, lambda x, y: 2.6 + (x - x0) / W_ * 1.0 - abs(y - y0 - H_ * 0.4) / H_ * 1.2,
            lit=0)
    for y in range(Y(8), Y(56)):
        for x in range(x0 + 6, x0 + 28):
            cv.flat(x, y, OFFICE[5] if (y - y0) % 3 else OFFICE[2])
    cv.vline(x0 + 5, Y(8), Y(56), OFFICE, 1.0, lit=0)
    cv.vline(x0 + 28, Y(8), Y(56), OFFICE, 1.0, lit=0)
    drop(cv, x1 - 20, Y(20), 6, WBLUE, 3.4)
    text(cv, 'VERNE', x1 - 31, Y(30), None, 0, flat=WBLUE[2])
    # el cos: el vestit blanc (més blanc que la paret), espatlles caigudes
    sh = Y(51)
    for y in range(sh, y1 + 1):
        t = (y - sh) / max(1, y1 - sh)
        half = 12 + 30 * min(1.0, t * 1.8) ** 0.6
        for x in range(int(cx - half), int(cx + half) + 1):
            u = (x - cx) / half
            c = SUITW[5] if u < -0.15 else SUITW[4] if u < 0.55 else SUITW[3]
            if abs(u) > 0.94:
                c = SUITW[2]
            cv.flat(x, y, c)
    # la camisa i la corbata (blau Verne), dins la V de les solapes
    for j in range(y1 - sh + 1):
        w = 3 + j * 0.42
        for x in range(int(cx - w), int(cx + w) + 1):
            cv.flat(x, sh + j, SUITW[5])
        cv.flat(int(cx - w) - 1, sh + j, SUITW[1])                  # la vora de les solapes
        cv.flat(int(cx + w) + 1, sh + j, SUITW[1])
        cv.flat(int(cx + w) + 2, sh + j, SUITW[2])
    for j in range(y1 - sh - 2):
        tw = 1 + j * 0.12
        for x in range(int(round(cx - tw)), int(round(cx + tw)) + 1):
            cv.flat(x, sh + 3 + j, WBLUE[3] if x <= cx else WBLUE[2])
    cv.rect(cx - 2, sh, cx + 2, sh + 2, [WBLUE[2]], 0, lit=0)       # el nus
    cv.flat(cx - 1, sh, WBLUE[4])
    for side in (-1, 1):                                            # les puntes del coll
        for j in range(4):
            cv.flat(cx + side * (3 + j), sh - 1 + j, SUITW[5])
            cv.flat(cx + side * (4 + j), sh - 1 + j, SUITW[2] if side > 0 else SUITW[4])
    cv.flat(cx + 15, sh + 9, (196, 156, 50))                        # la insígnia d'or
    cv.flat(cx + 15, sh + 8, (240, 210, 110))
    cv.flat(cx - 16, sh + 8, SUITW[5])                              # el mocador de la butxaca
    # el coll de la pell, prim
    for y in range(Y(48), sh):
        for x in range(cx - 5, cx + 6):
            cv.flat(x, y, S[3] if x > cx + 1 else S[4])
    cv.hline(cx - 5, cx + 5, sh - 1, [S[2]], 0, lit=0)
    # el cap: oval, mentó una mica quadrat
    hc, rx, ry = Y(32), 11.5, 16.0
    for y in range(int(hc - ry), int(hc + ry) + 1):
        for x in range(int(cx - rx - 1), int(cx + rx + 2)):
            nx, ny = (x - cx) / rx, (y - hc) / ry
            sq = nx * nx * (1 if ny < 0.4 else 1.35) + ny * ny
            if sq <= 1:
                i = 5 if nx < -0.25 else 4 if nx < 0.45 else 3
                if ny > 0.8:
                    i -= 1
                cv.flat(x, y, S[i])
    for side in (-1, 1):                                            # les orelles
        ex = cx + side * 12
        for j in range(7):
            cv.flat(ex + side, hc - 2 + j, S[3] if side > 0 else S[4])
            if 1 <= j <= 5:
                cv.flat(ex + side * 2, hc - 2 + j, S[2] if side > 0 else S[3])
        cv.flat(ex + side, hc, S[2])
    # el cabell blanc, pentinat enrere: volum a dalt, entrades, pentinades cap enrere
    top = hc - ry - 4
    line = lambda x: hc - 9 + (2 if abs(x - cx) > 7 else 0) - (1 if abs(x - cx) < 3 else 0)   # noqa: E731
    for y in range(int(top), hc + 1):
        for x in range(int(cx - rx - 2), int(cx + rx + 3)):
            nx, ny = (x - cx) / (rx + 2), (y - (hc - 6)) / (ry - 5 + 4)
            inside = nx * nx + ny * ny <= 1
            side = abs(x - cx) >= rx - 1 and y <= hc - 1
            if inside and (y < line(x) or side):
                if side and y > hc - 4:
                    c = HAIRW[1]
                else:
                    stroke = int((x - cx) * 0.8 + (y - top) * (0.9 if x < cx else -0.9)) % 4 == 0
                    c = HAIRW[4] if nx < -0.2 and ny < -0.3 else HAIRW[3] if nx < 0.4 else HAIRW[2]
                    if stroke:
                        c = HAIRW[2] if c != HAIRW[2] else HAIRW[1]
                cv.flat(x, y, c)
    for x in range(int(cx - rx), int(cx + rx) + 1):                # l'ombra del cabell al front
        y = line(x)
        if cv.get(x, y)[:3] in (S[3], S[4], S[5]):
            cv.flat(x, y, S[3] if x < cx + 5 else S[2])
    # celles blanques, fines i arquejades
    for side in (-1, 1):
        for i, dy in enumerate((1, 0, 0, 0, 1)):
            cv.flat(cx + side * (2 + i), hc - 4 + dy, HAIRW[2])
    # els ulls: mig closos de tant somriure, iris blau gel, potes de gall
    for side in (-1, 1):
        ex = cx + side * 5 - (1 if side < 0 else 0)
        for i in range(4):
            cv.flat(ex + i - 1, hc - 1 + (1 if i in (0, 3) else 0), (40, 26, 22))
        cv.flat(ex, hc, (70, 110, 150))
        cv.flat(ex + 1, hc, (30, 40, 56))
        cv.flat(ex - 1, hc + 1, S[3])
        cv.flat(ex + 1, hc + 1, S[3])
        ox = ex + (3 if side > 0 else -2)
        cv.flat(ox + side, hc - 1, S[2])
        cv.flat(ox + side, hc + 1, S[2])
    # el nas, llarg i recte, amb l'ombra a la dreta
    for j in range(7):
        cv.flat(cx + 1, hc + j, S[3])
    cv.flat(cx - 1, hc + 6, S[2])
    cv.flat(cx + 2, hc + 6, S[2])
    cv.flat(cx, hc + 7, S[3])
    cv.flat(cx - 1, hc + 3, S[6])                                    # la llum de la punta del nas
    # el somriure perfecte: llavis prims i una filera de dents blanquíssimes, les comissures amunt
    my = hc + 10
    cv.hline(cx - 5, cx + 5, my - 1, [(120, 58, 50)], 0, lit=0)
    cv.flat(cx - 6, my - 2, (120, 58, 50))
    cv.flat(cx + 6, my - 2, (120, 58, 50))
    cv.hline(cx - 5, cx + 5, my, [(255, 255, 255)], 0, lit=0)
    cv.hline(cx - 4, cx + 4, my + 1, [(236, 238, 242)], 0, lit=0)
    cv.hline(cx - 3, cx + 3, my + 2, [(150, 74, 64)], 0, lit=0)
    cv.flat(cx + 4, my + 1, (150, 74, 64))
    cv.flat(cx - 4, my + 1, (150, 74, 64))
    for j in range(4):                                              # els plecs del somriure
        cv.flat(cx - 7 - (1 if j > 1 else 0), my - 4 + j, S[3])
        cv.flat(cx + 7 + (1 if j > 1 else 0), my - 4 + j, S[2])
    cv.hline(cx - 2, cx + 2, my + 5, [S[3]], 0, lit=0)              # el mentó
    # la lluïssor del front, de focus d'estudi
    cv.flat(cx - 4, hc - 6, S[6])
    cv.flat(cx - 3, hc - 6, S[6])
    cv.flat(cx - 5, hc - 5, S[6])


# ─── El dipòsit orbital (portada) ──────────────────────────────────────────

def diposit_orbital(cv, cx, cy, L, r, lit=0):
    """Un cilindre blanc, horitzontal, amb la gota blava i les panells solars; (cx, cy) el centre."""
    for x in range(int(cx - L / 2), int(cx + L / 2) + 1):
        for y in range(int(cy - r), int(cy + r) + 1):
            u = (y - cy) / r
            lvl = 4.4 - u * 1.8 - u * u * 1.4
            if (x - cx) % 14 == 0:
                lvl -= 1.0
            cv.put(x, y, WHITEV, lvl, lit)
    for side in (-1, 1):                                            # els tapes, rodons
        ex = cx + side * L / 2
        cv.disc(ex, cy, r * 0.4, r, WHITEV, lambda nx, ny: 3.6 - ny * 1.6 + side * nx * 0.6, lit)
    drop(cv, int(cx - L * 0.18), int(cy + r * 0.15), max(2, int(r * 0.35)), WBLUE, 3.4, lit)
    for k in range(int(L * 0.4)):                                   # «VERNE» en ratlletes
        if k % 3 != 2:
            cv.put(int(cx - L * 0.05) + k, cy + 1, WBLUE, 2.6, lit)
