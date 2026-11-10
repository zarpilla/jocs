"""
Biblioteca de pixel art "HD": es dibuixa directament a la resolució del joc (480×270),
píxel a píxel, amb rampes de color (fosc → clar, amb canvi de to), dithering ordenat (Bayer 4×4) i
llums de sala.

Idea bàsica: cada píxel es pinta amb una rampa i un nivell (un nombre real). El nivell final és
`nivell + lit × llum(x, y)`, i el dithering decideix entre els dos tons veïns de la rampa. Així una
mateixa superfície s'il·lumina sola a prop d'una làmpada i s'enfosqueix a les vores.

    from hd.pix import Canvas, Light, WALNUT, GOLD
    light = Light(ambient=0, vignette=(80, 46))
    light.point(349, 104, r=160, k=2.7, squash=1.15, down=True)
    cv = Canvas(light=light)
    cv.rect(0, 0, 479, 106, GREEN, 2.0)

Els props (fotogrames que es mostren i s'amaguen) es dibuixen en un Canvas transparent amb la mateixa
llum que el fons, perquè encaixin.
"""
import math
import random

from PIL import Image

W, H = 480, 270

_B = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
B4 = [[(v + 0.5) / 16 for v in row] for row in _B]


def hr(*a):
    """Soroll determinista (0..1) a partir d'enters."""
    return random.Random(hash(a) & 0xFFFFFFFF).random()


def mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def ramp(*keys, n=None):
    """Rampa interpolada entre colors clau (n tons en total)."""
    if n is None:
        return list(keys)
    out = []
    for i in range(n):
        t = i / (n - 1) * (len(keys) - 1)
        j = min(int(t), len(keys) - 2)
        out.append(mix(keys[j], keys[j + 1], t - j))
    return out


# ─── Rampes comunes (fosc → clar) ───────────────────────────────────────────
# Passat (fàbrica, Iri): fustes, llautó, coure, rovell, foc.
WALNUT = [(18, 10, 16), (34, 18, 22), (52, 28, 26), (72, 40, 30), (96, 56, 36), (122, 74, 44), (150, 96, 56), (182, 126, 76), (214, 164, 108)]
FLOOR = [(20, 12, 16), (36, 22, 22), (56, 34, 28), (80, 50, 34), (106, 68, 42), (134, 90, 54), (164, 116, 70), (196, 148, 92), (226, 184, 124)]
GOLD = [(36, 22, 18), (70, 44, 22), (110, 74, 30), (154, 110, 40), (198, 152, 60), (232, 194, 96), (250, 230, 160)]
COPPER = [(40, 18, 14), (76, 34, 20), (118, 56, 30), (160, 84, 44), (200, 120, 66), (232, 162, 104), (250, 210, 160)]
RUST = [(30, 14, 12), (58, 26, 18), (92, 42, 24), (128, 62, 32), (164, 88, 44), (196, 122, 64)]
BRICK = [(26, 12, 14), (48, 20, 20), (76, 32, 26), (104, 46, 32), (134, 62, 40), (164, 84, 54), (192, 112, 74)]
IRON = [(14, 14, 20), (26, 26, 34), (40, 40, 50), (58, 58, 68), (82, 80, 90), (110, 108, 116), (146, 142, 146), (186, 182, 182)]
FIRE = [(60, 10, 10), (120, 24, 10), (180, 52, 14), (226, 96, 24), (250, 150, 50), (255, 206, 110), (255, 244, 200)]
GREEN = [(10, 16, 20), (16, 26, 26), (24, 38, 32), (34, 52, 40), (46, 66, 48), (62, 82, 56), (82, 100, 66), (108, 122, 80), (140, 146, 98)]
RED = [(22, 8, 14), (42, 12, 20), (68, 16, 26), (98, 24, 32), (132, 38, 38), (164, 58, 46), (196, 90, 62), (224, 132, 90)]
NAVY = [(10, 10, 22), (16, 18, 36), (26, 28, 54), (38, 42, 72), (54, 60, 92)]
PAPER = [(64, 56, 54), (112, 100, 90), (162, 150, 130), (200, 190, 164), (228, 220, 196), (246, 242, 224), (255, 252, 240)]
MANILA = [(64, 44, 28), (110, 82, 48), (158, 126, 74), (198, 166, 102), (226, 198, 136), (244, 224, 170)]
GLASS = [(40, 30, 26), (80, 58, 40), (130, 96, 58), (176, 136, 80), (214, 178, 112), (240, 214, 150)]
SMOKE = [(30, 24, 36), (48, 38, 52), (70, 56, 66), (96, 74, 78), (126, 104, 104)]
LAMPG = [(8, 26, 18), (14, 44, 28), (22, 70, 40), (36, 102, 54), (60, 140, 72), (110, 190, 104), (184, 234, 156)]
# Present (La Gavina, Vet): acer fred, plàstic, llum blanca, pantalles.
STEEL = [(10, 14, 22), (18, 24, 34), (28, 36, 48), (40, 50, 64), (56, 68, 84), (76, 90, 108), (102, 118, 136), (136, 152, 168), (178, 192, 204), (222, 232, 238)]
PANEL = [(16, 18, 24), (28, 32, 40), (44, 48, 58), (62, 68, 80), (84, 92, 104), (110, 118, 130), (140, 148, 158), (176, 182, 190), (214, 218, 222)]
ORANGE = [(48, 16, 10), (92, 32, 14), (140, 54, 18), (190, 84, 26), (230, 122, 40), (250, 168, 80), (255, 214, 150)]
CYAN = [(14, 30, 56), (30, 70, 120), (60, 140, 210), (110, 200, 250), (190, 236, 255), (240, 252, 255)]
TEAL = [(6, 22, 26), (10, 40, 46), (16, 66, 72), (28, 100, 104), (50, 140, 140), (96, 190, 180), (170, 236, 220)]
SPACE = [(2, 2, 8), (6, 6, 16), (10, 12, 28), (16, 20, 42), (26, 28, 58), (42, 36, 72), (70, 44, 76)]
WARN = [(40, 28, 6), (90, 64, 10), (150, 110, 16), (210, 160, 30), (246, 206, 70), (255, 240, 160)]
PINK = [(50, 10, 30), (100, 24, 60), (160, 50, 100), (220, 100, 160), (255, 160, 210), (255, 220, 240)]
# Comunes
SKIN = [(56, 30, 30), (92, 52, 44), (132, 82, 62), (172, 118, 86), (206, 154, 116), (232, 192, 156)]
GRAY = [(36, 34, 42), (64, 62, 70), (98, 96, 104), (136, 134, 138), (176, 174, 170), (214, 212, 204)]
SUIT = [(8, 8, 14), (14, 14, 24), (22, 22, 36), (34, 34, 50), (50, 50, 68), (70, 70, 88)]
SIL = [(8, 6, 12), (14, 10, 18), (22, 16, 24), (32, 22, 28), (60, 34, 30), (120, 60, 36)]
SKY = [(6, 6, 16), (10, 12, 28), (16, 20, 42), (26, 28, 58), (42, 36, 72), (70, 44, 76), (112, 56, 68), (160, 80, 56), (206, 120, 60), (242, 172, 92)]
BLUEP = [(8, 18, 40), (14, 32, 68), (22, 50, 98), (34, 70, 126), (54, 96, 154), (120, 160, 200), (200, 224, 240)]


# ─── Llum ──────────────────────────────────────────────────────────────────

class Light:
    """Camp de llum d'una sala: suma de llums puntuals + llum ambient − vinyeta."""

    def __init__(self, ambient=0.0, vignette=(80, 46), floor_fade=(196, 36)):
        self.ambient = ambient
        self.vig = vignette            # (amplada lateral, alçada del sostre) de la vinyeta, o None
        self.floor_fade = floor_fade   # (y on comença, longitud) de l'enfosquiment de baix, o None
        self.points = []
        self.extra = []

    def point(self, x, y, r, k, squash=1.0, down=False, power=1.7):
        """Llum puntual a (x, y) de radi r i força k (nivells). `down`: la tapa una pantalla per dalt."""
        self.points.append((x, y, r, k, squash, down, power))
        return self

    def add(self, fn):
        """Una contribució qualsevol: fn(x, y) → nivells."""
        self.extra.append(fn)
        return self

    def __call__(self, x, y):
        v = self.ambient
        for lx, ly, r, k, sq, down, pw in self.points:
            dy = y - ly
            d = math.hypot(x - lx, dy * sq)
            if d < r:
                f = (1 - d / r) ** pw * k
                if down and dy < -2:
                    f *= max(0.3, 1 + (dy + 2) / 26)
                v += f
        for fn in self.extra:
            v += fn(x, y)
        if self.vig:
            side, top = self.vig
            ex = min(x, W - 1 - x)
            v -= 1.4 * max(0.0, 1 - ex / side) ** 2
            v -= 1.1 * max(0.0, 1 - y / top) ** 2
        if self.floor_fade and y > self.floor_fade[0]:
            v -= (y - self.floor_fade[0]) / self.floor_fade[1]
        return v


# ─── Llenç ─────────────────────────────────────────────────────────────────

class Canvas:
    """Llenç de 480×270 (o la mida que sigui). `transparent=True` per als props."""

    def __init__(self, w=W, h=H, light=None, transparent=False, img=None):
        self.w, self.h = w, h
        self.light = light or (lambda x, y: 0.0)
        self.img = img or Image.new('RGBA', (w, h), (0, 0, 0, 0) if transparent else (0, 0, 0, 255))
        self.P = self.img.load()

    # bàsic
    def put(self, x, y, ramp, lvl, lit=1.0):
        x, y = int(x), int(y)
        if 0 <= x < self.w and 0 <= y < self.h:
            v = lvl + (lit * self.light(x, y) if lit else 0)
            i = math.floor(v + B4[y & 3][x & 3] - 0.5)
            self.P[x, y] = ramp[max(0, min(len(ramp) - 1, i))] + (255,)

    def flat(self, x, y, col):
        x, y = int(x), int(y)
        if 0 <= x < self.w and 0 <= y < self.h:
            self.P[x, y] = tuple(col[:3]) + (255,)

    def get(self, x, y):
        return self.P[int(x), int(y)]

    # formes (nivell constant o funció lvl(x, y))
    def rect(self, x0, y0, x1, y1, ramp, lvl, lit=1.0):
        for y in range(int(y0), int(y1) + 1):
            for x in range(int(x0), int(x1) + 1):
                self.put(x, y, ramp, lvl(x, y) if callable(lvl) else lvl, lit)

    def hline(self, x0, x1, y, ramp, lvl, lit=1.0):
        self.rect(x0, y, x1, y, ramp, lvl, lit)

    def vline(self, x, y0, y1, ramp, lvl, lit=1.0):
        self.rect(x, y0, x, y1, ramp, lvl, lit)

    def line(self, x0, y0, x1, y1, ramp, lvl, lit=1.0):
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(int(n) + 1):
            t = i / n
            self.put(round(x0 + (x1 - x0) * t), round(y0 + (y1 - y0) * t), ramp, lvl, lit)

    def disc(self, cx, cy, rx, ry, ramp, lvl, lit=1.0):
        """El·lipse plena. lvl pot ser funció (nx, ny) en coordenades normalitzades (-1..1)."""
        for y in range(int(cy - ry - 1), int(cy + ry + 2)):
            for x in range(int(cx - rx - 1), int(cx + rx + 2)):
                nx, ny = (x - cx) / rx, (y - cy) / ry
                if nx * nx + ny * ny <= 1:
                    self.put(x, y, ramp, lvl(nx, ny) if callable(lvl) else lvl, lit)

    def ring(self, cx, cy, r, ramp, lvl, lit=1.0, step=2):
        for a in range(0, 360, step):
            self.put(round(cx + math.cos(math.radians(a)) * r), round(cy + math.sin(math.radians(a)) * r), ramp, lvl, lit)

    def poly(self, pts, ramp, lvl, lit=1.0):
        """Polígon ple (regla parell-senar). lvl pot ser funció (x, y)."""
        ys = [p[1] for p in pts]
        for y in range(int(min(ys)), int(max(ys)) + 1):
            xs = []
            for (xa, ya), (xb, yb) in zip(pts, pts[1:] + pts[:1]):
                if (ya <= y + 0.5 < yb) or (yb <= y + 0.5 < ya):
                    xs.append(xa + (y + 0.5 - ya) * (xb - xa) / (yb - ya))
            xs.sort()
            for a, b in zip(xs[::2], xs[1::2]):
                for x in range(math.ceil(a - 0.5), math.floor(b - 0.5) + 1):
                    self.put(x, y, ramp, lvl(x, y) if callable(lvl) else lvl, lit)

    def sprite(self, rows, x0, y0, legend, lit=1.0):
        """Dibuix a mà: rows = ['..ab..', ...]; legend = {'a': (rampa, nivell) o color RGB}; '.' = res."""
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch in legend:
                    v = legend[ch]
                    if isinstance(v[0], list):
                        self.put(x0 + i, y0 + j, v[0], v[1], lit)
                    else:
                        self.flat(x0 + i, y0 + j, v)

    # efectes (sobre el que ja hi ha)
    def glow(self, cx, cy, r, col, strength):
        """Halo de color (dithered) sobre el que ja està pintat."""
        for y in range(int(cy - r), int(cy + r) + 1):
            for x in range(int(cx - r), int(cx + r) + 1):
                if 0 <= x < self.w and 0 <= y < self.h:
                    d = math.hypot(x - cx, y - cy) / r
                    if d < 1:
                        a = strength * (1 - d) ** 2
                        o = self.P[x, y]
                        if o[3] and a > B4[y & 3][x & 3] * 0.35:
                            self.P[x, y] = mix(o, col, min(1, a)) + (o[3],)

    def tint(self, x0, y0, x1, y1, col, k, mask=None):
        """Barreja cap a `col` (k = 0..1, o funció de (x, y)); `mask(x, y)` → 0..1 opcional."""
        for y in range(max(0, int(y0)), min(self.h, int(y1) + 1)):
            for x in range(max(0, int(x0)), min(self.w, int(x1) + 1)):
                o = self.P[x, y]
                if not o[3]:
                    continue
                kk = k(x, y) if callable(k) else k
                if mask:
                    kk *= mask(x, y)
                if kk > 0:
                    self.P[x, y] = mix(o, col, min(1, kk)) + (o[3],)

    def darken(self, x0, y0, x1, y1, amount, dither=True):
        """Ombra: amount = 0..1 o funció (x, y). Amb dither, l'ombra és a quadres a les vores."""
        for y in range(max(0, int(y0)), min(self.h, int(y1) + 1)):
            for x in range(max(0, int(x0)), min(self.w, int(x1) + 1)):
                a = amount(x, y) if callable(amount) else amount
                if a <= 0:
                    continue
                o = self.P[x, y]
                if not o[3]:
                    continue
                if dither:
                    if a > B4[y & 3][x & 3]:
                        self.P[x, y] = tuple(int(c * 0.55) for c in o[:3]) + (o[3],)
                else:
                    self.P[x, y] = tuple(int(c * (1 - a * 0.6)) for c in o[:3]) + (o[3],)


# ─── Coordenades de disseny (room_designs.py) → píxels reals ──────────────
# A Suma Zero el disseny ja és a 480×270 (escala.py): K = 1.

K = W / 480


def R(x0, y0, x1, y1):
    """Rectangle de disseny → rectangle real inclusiu (on cal dibuixar una cosa clicable)."""
    return (math.floor(x0 * K), math.floor(y0 * K), math.floor((x1 + 1) * K) - 1, math.floor((y1 + 1) * K) - 1)


def Pt(x, y):
    return (round((x + 0.5) * K - 0.5), round((y + 0.5) * K - 0.5))
