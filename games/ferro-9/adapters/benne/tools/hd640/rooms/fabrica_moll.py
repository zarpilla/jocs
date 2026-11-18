"""
Moll de càrrega de la fàbrica (hd/rooms/fabrica_moll.py) a 640×360: la mateixa composició ×4/3, dibuixada de nou.
Acte 2, Iri: maó, bigues de ferro, taulons; la llançadora nova a la badia, amb la comporta tancada al fons (per
sota s'escola la lluna). És el mateix lloc que l'hangar de La Gavina (gavina_hangar), cent vint anys abans: el
pilar 7, el conducte, les reixes del terra i la llançadora es dibuixen amb les mateixes funcions a totes dues
sales (aquí, nous; allà, envellits). Les fan servir també final_estacio i final_llancadora.
Llums: làmpada penjada sobre les bigues, la porta entreoberta de les calderes (foc), un aplic sobre el tauler
d'eines, el llum de servei de la badia i la lluna que s'escola per sota la comporta.
Animació: `ambient` (el foc de les calderes, la pols a la llum i l'escletxa de lluna que tremola). Els fotogrames
es fan redibuixant només dins les zones que es mouen (ClipCanvas), damunt del fons quiet.
"""
import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)

import math
import random
from functools import lru_cache

from hd.pix import (Canvas, Light, B4, W, H, hr, mix, ramp, WALNUT, FLOOR, GOLD, COPPER, RUST, BRICK, IRON, FIRE,  # noqa: F401
                    GREEN, RED, PAPER, MANILA, SKY, SIL, SMOKE, CYAN, STEEL, GRAY)
from hd.rooms.fabrica_moll import F9, ACER, OLDHULL, HULL, PAINT, MORTAR, NIGHT  # noqa: F401

try:                                     # la pols i els fotogrames, els de la sala del costat (són els mateixos)
    from hd640.rooms.fabrica_despatx_pla_comu import dust, ambient_frames
except Exception:                        # (encara no hi és, o no carrega)
    from hd.rooms.fabrica_despatx import dust, ambient_frames

hr = lru_cache(maxsize=1 << 19)(hr)      # (el soroll es calcula moltes vegades igual: a cada fotograma)

FLOOR_Y = 204
VP = (320, 139)            # punt de fuga del terra (el mateix que fan servir les reixes)

LIGHT = Light(vignette=(93, 53), floor_fade=(267, 59))
LIGHT.point(200, 40, r=233, k=2.5, squash=0.95, down=True)       # làmpada penjada
LIGHT.point(59, 200, r=127, k=2.0, squash=1.25)                  # calderes: la porta entreoberta
LIGHT.point(405, 53, r=104, k=1.5, squash=1.0, down=True)        # aplic sobre el tauler d'eines


def _moon(x, y):
    """Llum freda que s'escola per sota la comporta tancada (terra de la badia i del davant)."""
    v = 0.0
    if x > 453 and y > 160:
        v += max(0.0, 1 - math.hypot((x - 543) / 93, (y - 195) / 21)) ** 1.4 * 1.0
    if y > FLOOR_Y and x > 400:                                   # taca al terra davant la badia
        t = (y - FLOOR_Y) / 67
        xl = 445 - t * 53
        if xl < x and t < 1:
            v += (1 - t) * 0.9 * min(1, (x - xl) / 27)
    return v


LIGHT.add(_moon)
LIGHT.point(539, 21, r=160, k=1.7, squash=0.9, down=True)        # llum de servei de la badia


# ─── Retall: redibuixar només dins d'unes caixes (per als fotogrames) ───────

def _bb(cv):
    return getattr(cv, 'bb', None) or (0, 0, cv.w - 1, cv.h - 1)


def _ys(cv, a, b):
    """range(a, b + 1) retallat a la zona que es dibuixa."""
    bb = _bb(cv)
    return range(max(int(a), bb[1]), min(int(b), bb[3]) + 1)


def _xs(cv, a, b):
    bb = _bb(cv)
    return range(max(int(a), bb[0]), min(int(b), bb[2]) + 1)


class _ClipP:
    def __init__(self, P, inside):
        self.P, self.inside = P, inside

    def __getitem__(self, k):
        return self.P[k]

    def __setitem__(self, k, v):
        if self.inside(*k):
            self.P[k] = v


class ClipCanvas(Canvas):
    """Llenç que només pinta dins de `boxes` (x0, y0, x1, y1, inclusius): per refer un fotograma damunt del fons
    quiet sense recalcular la resta de la sala. Les escriptures directes a P també queden retallades."""

    def __init__(self, img, boxes, light=None):
        super().__init__(img.width, img.height, light=light, img=img)
        self.boxes = [tuple(int(v) for v in b) for b in boxes]
        self.bb = (min(b[0] for b in self.boxes), min(b[1] for b in self.boxes),
                   max(b[2] for b in self.boxes), max(b[3] for b in self.boxes))
        self.P = _ClipP(self.P, self.inside)

    def inside(self, x, y):
        x, y = int(x), int(y)
        for x0, y0, x1, y1 in self.boxes:
            if x0 <= x <= x1 and y0 <= y <= y1:
                return True
        return False

    def put(self, x, y, ramp, lvl, lit=1.0):
        if self.inside(x, y):
            Canvas.put(self, x, y, ramp, lvl, lit)

    def rect(self, x0, y0, x1, y1, ramp, lvl, lit=1.0):
        bx0, by0, bx1, by1 = self.bb
        x0, y0, x1, y1 = max(int(x0), bx0), max(int(y0), by0), min(int(x1), bx1), min(int(y1), by1)
        if x0 <= x1 and y0 <= y1:
            Canvas.rect(self, x0, y0, x1, y1, ramp, lvl, lit)

    def _cut(self, x0, y0, x1, y1):
        bx0, by0, bx1, by1 = self.bb
        return max(x0, bx0), max(y0, by0), min(x1, bx1), min(y1, by1)

    def tint(self, x0, y0, x1, y1, col, k, mask=None):
        Canvas.tint(self, *self._cut(x0, y0, x1, y1), col, k, mask)

    def darken(self, x0, y0, x1, y1, amount, dither=True):
        Canvas.darken(self, *self._cut(x0, y0, x1, y1), amount, dither)


def clip_frames(bg, light, n, boxes, base=None, kw=None):
    """Fotogrames de l'animació (només els píxels que canvien): bg(cv, t=i/n) redibuixat només dins de `boxes`
    (que no s'han de trepitjar), damunt del fons quiet (`base`, la imatge de bg amb t = 0)."""
    if base is None:
        cv = Canvas(light=light)
        bg(cv)
        base = cv.img
    base_rgb = base.convert('RGB')

    def draw(t):
        if t == 0.0:
            return base_rgb
        img = base.copy()
        for b in boxes:                       # caixa per caixa: els bucles només recorren la caixa
            bg(ClipCanvas(img, [b], light=light), t=t, **(kw or {}))
        return img.convert('RGB')
    bx = (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes) + 1, max(b[3] for b in boxes) + 1)
    return ambient_frames(bg, light, n, box=bx, draw=draw)


# ─── Lletra de plantilla (4×6) ──────────────────────────────────────────────

FONT = {
    'A': ['.##.', '#..#', '#..#', '####', '#..#', '#..#'], 'B': ['###.', '#..#', '###.', '#..#', '#..#', '###.'],
    'C': ['.###', '#...', '#...', '#...', '#...', '.###'], 'D': ['###.', '#..#', '#..#', '#..#', '#..#', '###.'],
    'E': ['####', '#...', '###.', '#...', '#...', '####'], 'F': ['####', '#...', '###.', '#...', '#...', '#...'],
    'G': ['.###', '#...', '#...', '#.##', '#..#', '.###'], 'H': ['#..#', '#..#', '####', '#..#', '#..#', '#..#'],
    'I': ['###', '.#.', '.#.', '.#.', '.#.', '###'], 'J': ['...#', '...#', '...#', '...#', '#..#', '.##.'],
    'K': ['#..#', '#.#.', '##..', '#.#.', '#..#', '#..#'], 'L': ['#...', '#...', '#...', '#...', '#...', '####'],
    'M': ['#...#', '##.##', '#.#.#', '#...#', '#...#', '#...#'], 'N': ['#..#', '##.#', '#.##', '#..#', '#..#', '#..#'],
    'O': ['.##.', '#..#', '#..#', '#..#', '#..#', '.##.'], 'P': ['###.', '#..#', '#..#', '###.', '#...', '#...'],
    'Q': ['.##.', '#..#', '#..#', '#..#', '#.#.', '.#.#'], 'R': ['###.', '#..#', '#..#', '###.', '#.#.', '#..#'],
    'S': ['.###', '#...', '.##.', '...#', '...#', '###.'], 'T': ['#####', '..#..', '..#..', '..#..', '..#..', '..#..'],
    'U': ['#..#', '#..#', '#..#', '#..#', '#..#', '.##.'], 'V': ['#...#', '#...#', '#...#', '.#.#.', '.#.#.', '..#..'],
    'W': ['#...#', '#...#', '#.#.#', '#.#.#', '##.##', '#...#'], 'X': ['#..#', '#..#', '.##.', '.##.', '#..#', '#..#'],
    'Y': ['#...#', '.#.#.', '..#..', '..#..', '..#..', '..#..'], 'Z': ['####', '...#', '..#.', '.#..', '#...', '####'],
    '0': ['.##.', '#..#', '#.##', '##.#', '#..#', '.##.'], '1': ['.#.', '##.', '.#.', '.#.', '.#.', '###'],
    '2': ['.##.', '#..#', '..#.', '.#..', '#...', '####'], '3': ['###.', '...#', '.##.', '...#', '...#', '###.'],
    '4': ['#..#', '#..#', '####', '...#', '...#', '...#'], '5': ['####', '#...', '###.', '...#', '...#', '###.'],
    '6': ['.##.', '#...', '###.', '#..#', '#..#', '.##.'], '7': ['####', '...#', '..#.', '.#..', '.#..', '.#..'],
    '8': ['.##.', '#..#', '.##.', '#..#', '#..#', '.##.'], '9': ['.##.', '#..#', '#..#', '.###', '...#', '.##.'],
    '-': ['...', '...', '###', '...', '...', '...'], '.': ['.', '.', '.', '.', '.', '#'],
    "'": ['#', '#', '.', '.', '.', '.'], ' ': ['..', '..', '..', '..', '..', '..'],
}


def text_width(s):
    return sum(len(FONT.get(ch, FONT[' '])[0]) + 1 for ch in s) - 1 if s else 0


def text(cv, x, y, s, rmp, lvl, lit=0.5):
    """Lletres de plantilla de 4×6 (rètols i plaques). Retorna la x on acaba."""
    for ch in s:
        g = FONT.get(ch, FONT[' '])
        for j, row in enumerate(g):
            for i, c in enumerate(row):
                if c == '#':
                    cv.put(x + i, y + j, rmp, lvl, lit)
        x += len(g[0]) + 1
    return x


def cyl(u):
    """Ombrejat d'un cilindre vertical (u = -1..1, llum de l'esquerra)."""
    return -u * 1.1 - u * u * 1.3 + (0.9 if -0.62 < u < -0.4 else 0) + (0.4 if 0.7 < u < 0.82 else 0)


def _interp(vals, s):
    """Valor de la llista `vals` a la posició s = 0..1 (interpolat)."""
    f = s * (len(vals) - 1)
    i = min(len(vals) - 2, int(f))
    return vals[i] + (vals[i + 1] - vals[i]) * (f - i)


# ─── Peces compartides amb l'hangar i els finals ────────────────────────────

SEVEN = ['######', '######', '....##', '...##.', '...##.', '..##..', '..##..', '.##...', '.##...']


def pillar(cv, cx, y0, y1, aged=False):
    """Pilar de ferro colat amb un 7 pintat: el mateix a les dues èpoques. cx = centre; y0 = sota la biga."""
    # capitell: àbac, coll i motllura que s'estreny cap al fust
    for y in _ys(cv, y0, y0 + 10):
        k = y - y0
        hw = 15 if k < 5 else 15 - (k - 4) * 0.9
        for x in _xs(cv, cx - hw, cx + hw):
            lvl = 3.2 + cyl((x - cx) / (hw + 0.5)) - k * 0.1 + (1.3 if k == 0 else 0) - (1.0 if k == 4 else 0) \
                + (0.5 if k == 5 else 0)
            cv.put(x, y, IRON, lvl)
    for x in range(cx - 13, cx + 14, 6):                            # cargols de l'àbac
        cv.put(x, y0 + 2, IRON, 4.8)
        cv.put(x + 1, y0 + 3, IRON, 1.4)
    # fust (al present, la pintura vermella esvaïda i clapes de rovell)
    for y in _ys(cv, y0 + 11, y1 - 14):
        for x in _xs(cv, cx - 9, cx + 9):
            u = (x - cx) / 10
            lvl = 2.6 + cyl(u) + (hr(x, y // 5, 12) - 0.5) * 0.2
            if aged:
                n = hr(x // 3, y // 5, 7) * 0.6 + hr(x // 2, y // 2, 8) * 0.4
                if n > 0.62:
                    cv.put(x, y, RUST, 2.2 + cyl(u) * 0.8 - (0.6 if n > 0.8 else 0) + (0.5 if hr(x, y, 9) > 0.8 else 0))
                    continue
                lvl -= 0.5
            cv.put(x, y, PAINT, lvl)
    # anelles de reforç, amb un fil de reblons
    for yy in (y0 + 40, y1 - 45):
        for y in _ys(cv, yy, yy + 5):
            for x in _xs(cv, cx - 11, cx + 11):
                lvl = 3.0 + cyl((x - cx) / 11.5) + (0.9 if y == yy else 0) - (1.3 if y == yy + 5 else 0)
                if y == yy + 2 and (x - cx) % 4 == 0:
                    lvl += 1.6
                cv.put(x, y, IRON, lvl)
    # base: sòcol esglaonat
    for y in _ys(cv, y1 - 13, y1):
        k = y - (y1 - 13)
        hw = 11 + min(4, k // 2)
        for x in _xs(cv, cx - hw, cx + hw):
            cv.put(x, y, IRON, 2.6 + cyl((x - cx) / (hw + 0.5)) - (1.0 if y == y1 else 0) + (0.9 if k in (0, 6) else 0)
                   - (0.5 if k == 5 else 0))
    if aged:
        # rovell que regalima i pintura que salta
        rnd = random.Random(cx * 3)
        for _ in range(12):
            x = rnd.randint(cx - 8, cx + 8)
            ya = rnd.randint(y0 + 16, y1 - 40)
            for y in range(ya, ya + rnd.randint(8, 29)):
                if hr(x, y, 3) > 0.25:
                    cv.put(x, y, RUST, 1.6 + cyl((x - cx) / 10) * 0.6 + (0.5 if y == ya else 0))
        for _ in range(40):
            x, y = rnd.randint(cx - 8, cx + 8), rnd.randint(y0 + 13, y1 - 16)
            cv.put(x, y, RUST, 3.6)
            cv.put(x + 1, y, RUST, 2.6)
            cv.put(x, y + 1, RUST, 0.8)
    # el 7, en blanc de plantilla, damunt d'una franja
    sy = y0 + 56
    for y in _ys(cv, sy - 3, sy + 12):
        for x in _xs(cv, cx - 8, cx + 8):
            lvl = 1.6 + cyl((x - cx) / 10) * 0.8 + (0.6 if aged else 0)
            if aged and hr(x // 2, y // 2, 40) > 0.88:
                lvl -= 1.2                                            # la franja, bruta
            cv.put(x, y, PAPER if not aged else MANILA, lvl)
    for j, row in enumerate(SEVEN):
        for i, ch in enumerate(row):
            if ch == '#':
                x, y = cx - 3 + i, sy + j
                if aged and hr(x, y, 41) < 0.15:
                    continue                                          # pintura esquerdada
                cv.put(x, y, PAINT, (1.4 if not aged else 1.0) + (0.5 if j == 0 else 0))


def carved_mark(cv, x, y, aged=False):
    """La marca de l'Iri: una I. i una clau anglesa, gravades. Nova: metall viu; vella: solc ple de rovell."""
    cut = (F9, 5.6) if not aged else (SIL, 0.6)
    lip = (F9, 3.2) if not aged else (RUST, 5.4)
    pts = [(x, y + i) for i in range(9)] + [(x + 3, y + 8)]                         # I.
    pts += [(x + 5 + i, y + 9 - i) for i in range(7)]                               # mànec de la clau
    cx, cy = x + 13, y + 1                                                          # boca de la clau, oberta amunt
    for a in range(0, 360, 20):
        if 255 < a < 335:
            continue
        pts.append((round(cx + math.cos(math.radians(a)) * 2.6), round(cy + math.sin(math.radians(a)) * 2.6)))
    seen = set()
    for px, py in pts:
        if (px, py) in seen:
            continue
        seen.add((px, py))
        cv.put(px, py, cut[0], cut[1], 0.4)
    for px, py in seen:
        if (px + 1, py + 1) not in seen:
            cv.put(px + 1, py + 1, lip[0], lip[1] - 1.8, 0.4)                         # ombra del solc


def grate(cv, xa, xb, aged=False, y0=231, y1=249):
    """Reixa de desguàs encastada al terra (en perspectiva cap a VP)."""
    vx, vy = VP
    k = (y0 - vy) / (y1 - vy)
    far = lambda x: vx + (x - vx) * k  # noqa: E731
    fr = IRON if not aged else STEEL
    for y in _ys(cv, y0, y1):
        t = (y - y0) / (y1 - y0)
        xl = far(xa) + (xa - far(xa)) * t
        xr = far(xb) + (xb - far(xb)) * t
        for x in _xs(cv, round(xl), round(xr)):
            inner = y0 + 1 < y < y1 - 1 and xl + 3.2 < x < xr - 3.2
            if inner:
                # forat amb barrots que fugen; al fons del forat, la foscor (i un reflex d'aigua a baix)
                s = (x - xl) / (xr - xl)
                ph = (s * 12) % 1
                if ph < 0.26:
                    cv.put(x, y, fr, 3.2 + (0.7 if y < y0 + 4 else 0) - t * 0.4 + (0.8 if ph < 0.08 else 0))
                elif ph < 0.34:
                    cv.put(x, y, fr, 0.9 - t * 0.3, 0.4)                       # ombra del barrot
                else:
                    cv.put(x, y, fr, 0.0 - t * 0.5 + (0.6 if y > y1 - 5 and hr(x // 3, 70) > 0.6 else 0), 0.3)
            else:
                edge = 4.2 if y == y0 else (1.4 if y == y1 else (3.2 if y == y0 + 1 else 2.6))
                if not (y0 < y < y1) or x <= xl + 1 or x >= xr - 1:
                    edge += (0.8 if x <= xl + 1 else 0) - (0.8 if x >= xr - 1 else 0)
                cv.put(x, y, fr, edge)
    # travesser del mig
    ym = (y0 + y1) // 2
    t = (ym - y0) / (y1 - y0)
    xl = far(xa) + (xa - far(xa)) * t
    xr = far(xb) + (xb - far(xb)) * t
    cv.hline(round(xl) + 3, round(xr) - 3, ym, fr, 2.8)
    cv.hline(round(xl) + 3, round(xr) - 3, ym + 1, fr, 0.8)
    # cargols als quatre cantons
    for bx, by in ((far(xa) + 2, y0 + 1), (far(xb) - 2, y0 + 1), (xa + 2, y1 - 1), (xb - 2, y1 - 1)):
        cv.put(round(bx), by, fr, 4.6)
    if aged:
        rnd = random.Random(xa)
        for _ in range(24):
            x = rnd.randint(xa, xb)
            y = rnd.randint(y0, y1)
            if _bb(cv)[0] <= x <= _bb(cv)[2] and _bb(cv)[1] <= y <= _bb(cv)[3] and cv.get(x, y)[3]:
                cv.put(x, y, RUST, 2.4)


def shuttle(cv, x0, cy, aged=False, L=173, R=32):
    """La llançadora de càrrega, de perfil (morro a l'esquerra). Nova al moll; vella i sense peces a l'hangar.
    Retorna (porta, pany): les caixes on van la porta i el pany sònic."""
    body = HULL if not aged else OLDHULL
    trim = GOLD if not aged else COPPER
    rnd = random.Random(7)

    def half(s):
        if s < 0.26:
            return R * math.sqrt(max(0.0, 1 - ((0.26 - s) / 0.26) ** 2)) ** 0.9
        if s > 0.86:
            return R * (1 - (s - 0.86) / 0.14 * 0.28)
        return R

    # aletes (darrere el cos)
    tail = x0 + L
    cv.poly([(tail - 40, cy - R + 3), (tail - 5, cy - R - 21), (tail + 4, cy - R - 21), (tail - 3, cy - R + 8)], body,
            lambda x, y: 3.4 - (y - cy) * 0.015 + (0.8 if (x - tail) % 9 == 0 else 0))
    cv.poly([(tail - 40, cy + R - 3), (tail - 5, cy + R + 19), (tail + 4, cy + R + 19), (tail - 3, cy + R - 8)], body, 1.8)
    cv.line(tail - 5, cy - R - 21, tail + 4, cy - R - 21, trim, 4.0)
    cv.line(tail - 5, cy - R - 20, tail + 4, cy - R - 20, trim, 2.8)
    cv.line(tail - 5, cy + R + 19, tail + 4, cy + R + 19, trim, 2.6)
    cv.line(tail - 40, cy - R + 3, tail - 5, cy - R - 21, body, 4.6)            # cantell de l'aleta, a la llum
    # cos
    for x in _xs(cv, x0, tail):
        s = (x - x0) / L
        h = half(s)
        for y in _ys(cv, round(cy - h), round(cy + h)):
            ny = (y - cy) / max(h, 1)
            lvl = 4.0 - ny * 1.6 - ny * ny * 1.6 + (1.3 if -0.72 < ny < -0.5 else 0) - (0.6 if s < 0.1 else 0) \
                + (0.6 if -0.5 <= ny < -0.44 else 0)
            seam = (x - x0) % 23 == 0 and s > 0.2
            if seam:
                lvl -= 1.4
            if abs(ny - 0.42) < 0.04 and s > 0.24:
                lvl -= 1.2
            if aged:
                lvl -= 0.6 + (hr(x // 3, y // 2, 11) - 0.5) * 0.6
            cv.put(x, y, body, lvl)
            if seam and (y - cy) % 5 == 0:
                cv.put(x + 1, y, body, lvl + 2.4)                 # reblons
                cv.put(x + 1, y + 1, body, lvl - 0.6)
    # cap del morro, de llautó
    for x in _xs(cv, x0, x0 + 11):
        h = half((x - x0) / L)
        for y in _ys(cv, round(cy - h), round(cy + h)):
            ny = (y - cy) / max(h, 1)
            cv.put(x, y, trim, 3.4 - ny * 1.4 - ny * ny + (1.0 if -0.6 < ny < -0.3 else 0) - (1.0 if x == x0 + 11 else 0))
    # cèrcol de popa
    for y in range(round(cy - half(0.9)), round(cy + half(0.9)) + 1):
        ny = (y - cy) / R
        for x in range(tail - 19, tail - 15):
            cv.put(x, y, trim, 3.2 - ny * 1.4 + (0.8 if x == tail - 19 else 0) - (0.8 if x == tail - 16 else 0))
    # finestreta: cèrcol de llautó cargolat i vidre
    px_, py_ = x0 + 29, cy - 9
    cv.disc(px_, py_, 8.7, 8.7, trim, lambda nx, ny: 3.6 - nx - ny)
    for a in range(0, 360, 45):
        cv.put(round(px_ + math.cos(math.radians(a)) * 7.4), round(py_ + math.sin(math.radians(a)) * 7.4), trim, 5.0)
    glass = CYAN if not aged else STEEL
    cv.disc(px_, py_, 5.9, 5.9, glass, lambda nx, ny: (1.2 if not aged else 2.2) + ny * 0.6 - nx * 0.3, 0.3)
    cv.put(px_ - 3, py_ - 2, PAPER, 5.0, 0)
    cv.put(px_ - 2, py_ - 3, PAPER, 4.6, 0)
    cv.put(px_ - 1, py_ - 4, PAPER, 4.0, 0)
    # porta
    dx0, dx1, dy0, dy1 = x0 + 53, x0 + 77, cy - 23, cy + 25
    for y in range(dy0, dy1 + 1):
        for x in range(dx0, dx1 + 1):
            if x in (dx0, dx1) or y in (dy0, dy1):
                cv.put(x, y, body, 0.8 if x == dx1 or y == dy1 else 1.2)
    cv.vline(dx0 + 1, dy0 + 1, dy1 - 1, body, 5.0 if not aged else 4.0)
    cv.hline(dx0 + 1, dx1 - 1, dy0 + 1, body, 5.2 if not aged else 4.0)
    cv.vline(dx1 - 1, dy0 + 1, dy1 - 1, body, 2.2)
    for hy in (dy0 + 8, dy1 - 10):                                   # frontisses
        cv.rect(dx0 - 3, hy, dx0, hy + 3, trim, lambda x, y: 3.6 - (y - hy) * 0.4)
    cv.rect(dx1 - 5, cy + 2, dx1 - 3, cy + 6, trim, 3.4)              # agafador
    # pany sònic: un ressonador rodó, sense forat per a cap clau
    lx, ly = dx1 + 8, cy - 1
    cv.disc(lx, ly, 8, 8, trim, lambda nx, ny: 2.8 - nx * 0.8 - ny * 1.0)
    cv.ring(lx, ly, 5.3, trim, 1.2, step=5)
    cv.ring(lx, ly, 3.4, trim, 3.4, step=8)
    cv.ring(lx, ly, 2, trim, 4.6, step=12)
    cv.put(lx, ly, trim, 1.0)
    cv.put(lx - 5, ly - 5, PAPER, 4.6, 0)
    cv.put(lx - 4, ly - 6, PAPER, 3.8, 0)
    # els tres components de ferro-9 (al moll hi són; a l'hangar, tres forats)
    for ox in (96, 116, 136):
        hx, hy = x0 + ox, cy + 13
        if not aged:
            cv.rect(hx, hy, hx + 12, hy + 7, F9, lambda x, y: 4.6 - (y - hy) * 0.5)
            cv.hline(hx, hx + 12, hy, F9, 6.0)
            cv.vline(hx + 12, hy, hy + 7, F9, 2.6)
            cv.put(hx + 1, hy + 2, F9, 7, 0)
            cv.put(hx + 2, hy + 2, F9, 6.4, 0)
        else:
            cv.rect(hx - 1, hy - 1, hx + 13, hy + 8, body, 4.0)
            cv.rect(hx, hy, hx + 12, hy + 7, SIL, 0.4, 0)
            cv.hline(hx, hx + 12, hy, SIL, 1.6, 0)
            for k in range(2):                                    # cables arrencats
                cv.put(hx + 3 + k * 5, hy + 8, COPPER, 3.2)
                cv.put(hx + 4 + k * 5, hy + 9, COPPER, 2.4)
                cv.put(hx + 4 + k * 5, hy + 10, COPPER, 1.6)
    # inscripció pintada a la popa: «L-1»
    text(cv, x0 + 120, cy - 16, 'L-1', RED if not aged else RUST, 3.0 if not aged else 1.8, 1.0)
    if aged:
        # pols, regalims de rovell i taques de verdet
        for _ in range(107):
            x = rnd.randint(x0 + 8, tail - 3)
            h = half((x - x0) / L)
            y = rnd.randint(round(cy - h) + 1, round(cy - h * 0.2))
            cv.put(x, y, GRAY, 4.6)
        for _ in range(14):
            x = rnd.randint(x0 + 27, tail - 13)
            ya = cy + rnd.randint(-8, 16)
            for y in range(ya, min(ya + rnd.randint(8, 19), round(cy + half((x - x0) / L)))):
                cv.put(x, y, RUST, 2.4 - (y - ya) * 0.03)
    # bressol (suports)
    for sx in (x0 + 40, x0 + 133):
        cv.rect(sx - 4, cy + R - 3, sx + 4, cy + R + 29, IRON, lambda x, y: 2.4 - (x - sx) * 0.3 + (0.8 if x == sx - 3 else 0))
        cv.rect(sx - 11, cy + R + 27, sx + 11, cy + R + 31, IRON, lambda x, y: 3.0 - (y - cy - R - 27) * 0.5)
        cv.poly([(sx - 13, cy + R - 5), (sx + 13, cy + R - 5), (sx + 8, cy + R + 1), (sx - 8, cy + R + 1)], IRON, 2.6)
        cv.hline(sx - 12, sx + 12, cy + R - 5, IRON, 4.0)
        for bx in (sx - 8, sx + 8):
            cv.put(bx, cy + R + 28, IRON, 4.6)
    return (dx0, dy0, dx1, dy1), (lx, ly)


# ─── Fons ───────────────────────────────────────────────────────────────────

def bricks(cv, x0, y0, x1, y1, base=2.0, rmp=BRICK, seed=0):
    """Maó de 16×7 (amb el morter), a trencajunts: cantell de dalt més clar, algun maó cremat o escantonat."""
    for y in _ys(cv, y0, y1):
        row = (y - y0) // 7
        off = 8 if row % 2 else 0
        v = (y - y0) % 7
        for x in _xs(cv, x0, x1):
            u = (x + off) % 16
            if v == 6 or u == 15:
                cv.put(x, y, MORTAR, base + 0.4 - (0.5 if v == 6 and u == 15 else 0))
            else:
                b = hr((x + off) // 16, row, seed)
                lvl = base + (b - 0.5) * 1.0 + (0.5 if v == 0 else 0) - (0.3 if v == 5 else 0) + (0.2 if u == 0 else 0)
                lvl += (hr(x // 2, y, seed + 1) - 0.5) * 0.3
                if b > 0.93:
                    lvl -= 0.9                                    # maó cremat
                if b < 0.05 and u > 11 and v < 2:
                    cv.put(x, y, MORTAR, base + 0.2)               # cantonada escantonada
                    continue
                cv.put(x, y, rmp, lvl)


def floor_planks(cv):
    vx, vy = VP
    for y in _ys(cv, FLOOR_Y, H - 1):
        dep = y - vy
        sh = (213 - y) / 9 * 1.2 if y < 213 else 0                 # ombra de contacte amb la paret
        for x in _xs(cv, 0, W - 1):
            u = (x - vx) / dep * 4.2
            pl = math.floor(u)
            fr = (u - pl) * dep / 4.2
            t = 1200 / dep
            r = hr(pl, 5)
            seg = math.floor(t / 3.2 + r * 4)
            seg_up = math.floor(1200 / (dep - 1) / 3.2 + r * 4)
            lvl = 1.9 + (hr(pl, seg) - 0.5) * 0.7 + (0.25 if hr(pl, seg, x // 4) > 0.85 else 0)
            lvl += (0.2 if hr(pl, seg, round(fr * 3)) > 0.8 else 0)  # veta
            if fr < 1:
                lvl = 0.5
            elif fr < 2:
                lvl += 0.3
            elif seg != seg_up:
                lvl = 0.7
            elif fr < 4 and abs((t / 3.2 + r * 4) % 1 - 0.06) < 0.02:
                lvl += 1.4                                       # claus a la punta del tauló
            cv.put(x, y, FLOOR, lvl - sh)


def lamp_cone(x, y):
    """El con de llum sota la làmpada penjada (0..1)."""
    if not 53 <= y <= 160:
        return 0.0
    half = 11 + (y - 53) * 0.55
    return max(0.0, min(1.0, (1 - abs(x - 200) / half) * 2.0)) * (1 - (y - 53) / 107) ** 0.7


def bg(cv, t=0.0):
    tt = t
    ph = 2 * math.pi * tt
    # ─── Sostre: taulons foscos i una biga d'acer ──────────────────────────
    cv.rect(0, 0, W - 1, 16, WALNUT, lambda x, y: 0.4 + (0.5 if x % 32 in (0, 1) else 0) + (hr(x // 32, 3) - 0.5) * 0.4
            - (0.3 if x % 32 == 2 else 0), 0.4)
    for x in range(0, W, 64):                                    # tirants de la cavallada
        cv.line(x, 16, x + 32, 0, IRON, 1.2, 0.4)
        cv.line(x + 32, 0, x + 64, 16, IRON, 1.0, 0.4)
        cv.line(x + 1, 16, x + 33, 0, IRON, 0.6, 0.4)
    beam = [3.2, 3.0, 2.4, 1.8, 1.6, 1.4, 1.4, 1.4, 1.2, 1.0, 0.4]
    cv.rect(0, 17, W - 1, 27, IRON, lambda x, y: beam[y - 17] + (hr(x // 5, y, 4) - 0.5) * 0.2)
    for x in range(5, W, 13):
        cv.put(x, 19, IRON, 4.2)
        cv.put(x + 1, 20, IRON, 1.6)
        cv.put(x, 25, IRON, 2.8)

    # ─── Paret de maó ─────────────────────────────────────────────────────
    bricks(cv, 0, 28, W - 1, FLOOR_Y - 1, base=2.0, seed=51)
    cv.darken(0, 28, W - 1, 36, lambda x, y: (37 - y) / 9)            # ombra de la biga
    # sòcol de pedra
    cv.rect(0, FLOOR_Y - 7, W - 1, FLOOR_Y - 1, GRAY, lambda x, y: 1.4 + (0.8 if y == FLOOR_Y - 7 else 0)
            + (0.3 if y == FLOOR_Y - 6 else 0) + (hr(x // 19, 2) - 0.5) * 0.4 - (0.8 if x % 19 == 0 else 0))

    # ─── Terra de taulons ────────────────────────────────────────────────
    floor_planks(cv)
    # carrils de la vagoneta: surten de la badia i fugen cap al davant
    vx, vy = VP
    for rx in (496, 581):
        for y in _ys(cv, FLOOR_Y + 3, H - 1):                    # travesses
            dep = y - vy
            if (2400 / dep) % 3 < 0.25:
                xa = vx + (rx - 13 - vx) * (y - vy) / (FLOOR_Y - vy)
                xb = vx + (rx + 16 - vx) * (y - vy) / (FLOOR_Y - vy)
                cv.hline(round(xa), round(xb), y, WALNUT, 1.0)
                cv.hline(round(xa), round(xb), y - 1, WALNUT, 2.0)
        for y in _ys(cv, FLOOR_Y, H - 1):
            x = vx + (rx - vx) * (y - vy) / (FLOOR_Y - vy)
            cv.put(x - 1, y, IRON, 1.6)
            cv.put(x, y, IRON, 4.4)
            cv.put(x + 1, y, IRON, 3.0)
            cv.put(x + 2, y, IRON, 2.2)
            cv.put(x + 3, y, IRON, 0.6)

    # ─── Porta de les calderes, entreoberta (11..76 × 83..204) ────────────
    # arc de maó
    for y in _ys(cv, 83, FLOOR_Y - 1):
        for x in _xs(cv, 11, 76):
            if x < 17 or x > 69 or y < 93:
                d = min(x - 11, 76 - x, y - 83)
                lvl = 3.2 - (0.8 if (x + y) % 8 == 0 else 0) - (d == 0) * 1.4 + (0.4 if d == 1 else 0)
                if x < 17 and (y - 83) % 7 == 6 or x > 69 and (y - 83) % 7 == 6:
                    lvl -= 1.0                                    # filades del brancal
                cv.put(x, y, BRICK, lvl)
    cv.rect(11, 83, 76, 86, GRAY, lambda x, y: 3.4 - (y - 83) * 0.7 + (hr(x // 3, 6) - 0.5) * 0.4)  # llinda de pedra
    # interior: el foc de les calderes
    for y in _ys(cv, 93, FLOOR_Y - 1):
        for x in _xs(cv, 17, 69):
            fl = 0.0
            if x > 53:                                            # (la part que es veu) les flames que es mouen a la paret
                fl = 0.35 * math.sin(y * 0.22 + x * 0.16 + ph * 3) + 0.25 * math.sin(y * 0.1 - x * 0.28 + ph * 2 + 1.0) \
                    + 0.15 * math.sin(y * 0.375 + ph * 5 + 2.0)
            cv.put(x, y, FIRE, 1.4 + (y - 93) / 107 * 2.4 - abs(x - 61) / 27 + (hr(x // 2, y // 4) - 0.5) * 0.4 + fl, 0.2)
    # silueta d'una caldera al fons
    for y in _ys(cv, 112, FLOOR_Y - 1):                          # caldera: cos cilíndric reblonat
        for x in _xs(cv, 35, 68):
            u = (x - 51) / 16.7
            top = 112 + (1 - math.sqrt(max(0, 1 - u * u))) * 11
            if y >= top:
                lvl = 1.4 + u * 1.2 - u * u + (0.8 if (y - 112) % 19 == 0 else 0)
                cv.put(x, y, SIL, lvl + (1.6 if (y - 112) % 19 == 1 and x % 5 == 0 else 0), 0)
    cv.rect(47, 93, 53, 115, SIL, lambda x, y: 1.2 + (x - 47) * 0.15, 0)        # xemeneia
    cv.hline(46, 54, 104, SIL, 2.4, 0)
    for y in _ys(cv, 165, 175):
        for x in _xs(cv, 40, 56):
            cv.put(x, y, FIRE, 5.4 - abs(x - 48) / 4 - abs(y - 170) / 6 + (hr(x, y) - 0.5), 0)  # boca del forn
    cv.hline(39, 57, 164, SIL, 2.0, 0)
    # fulla de la porta (ferro reblonat), oberta cap a dins
    for y in _ys(cv, 93, FLOOR_Y - 1):
        for x in _xs(cv, 17, 55):
            u = (x - 17) / 38
            lvl = 2.2 - u * 0.6 + (hr(x // 2, 31) - 0.5) * 0.2 + (hr(x // 3, y // 3, 32) - 0.5) * 0.15
            if (x - 17) % 19 in (0, 18) or (y - 93) % 27 in (0, 26):
                lvl -= 0.6
            elif (x - 17) % 19 == 1 or (y - 93) % 27 == 1:
                lvl += 0.3
            cv.put(x, y, IRON, lvl)
            if ((x - 17) % 19 in (3, 15)) and (y - 93) % 27 in (4, 22):
                cv.put(x, y, IRON, lvl + 2.0)
                cv.put(x + 1, y + 1, IRON, lvl - 0.8)
    cv.vline(55, 93, FLOOR_Y - 1, IRON, 4.4)                     # cantell il·luminat pel foc
    cv.vline(54, 93, FLOOR_Y - 1, IRON, 3.0)
    cv.tint(53, 93, 56, FLOOR_Y - 1, (255, 150, 60), 0.4)
    cv.rect(48, 144, 52, 149, GOLD, lambda x, y: 3.4 - (y - 144) * 0.3)          # maneta
    cv.put(49, 145, GOLD, 5.6)
    # placa esmaltada «CALDERES»
    cv.rect(19, 67, 68, 78, PAPER, lambda x, y: 3.8 - (y - 67) * 0.12)
    cv.hline(19, 68, 67, PAPER, 5.0)
    cv.hline(20, 67, 68, PAPER, 2.6)
    cv.hline(19, 68, 78, PAPER, 1.6)
    text(cv, 24, 70, 'CALDERES', [(30, 34, 70), (40, 46, 96)], 0.5, 0)
    cv.put(21, 76, IRON, 1.0); cv.put(66, 76, IRON, 1.0)
    cv.put(21, 69, IRON, 1.0); cv.put(66, 69, IRON, 1.0)
    cv.darken(62, 72, 68, 78, lambda x, y: 0.35 if hr(x, y, 77) > 0.5 else 0)   # esmalt saltat
    # llum del foc: halo i taca al terra
    cv.glow(61, 160, 61, (255, 140, 60), 0.32 + 0.03 * math.sin(ph * 3) + 0.025 * (math.sin(ph * 5 + 1) - math.sin(1)))
    for y in _ys(cv, FLOOR_Y, 266):
        tf = (y - FLOOR_Y) / 63
        for x in _xs(cv, int(19 - tf * 27), int(77 + tf * 35) - 1):
            cv.tint(x, y, x, y, (255, 130, 50), 0.28 * (1 - tf) * (1 - abs(x - 53) / (53 + tf * 40)))

    # ─── Conducte de pressió: de les calderes cap al moll ─────────────────
    pipe(cv, aged=False)

    # ─── Bastidor de la paret (la biga de ferro-9 hi va al damunt) ────────
    for bx in (123, 259):
        cv.rect(bx - 3, 112, bx + 3, 133, IRON, lambda x, y: 3.0 - (x - bx) * 0.4)
        cv.rect(bx - 3, 112, bx + 16, 116, IRON, lambda x, y: 3.6 - (y - 112) * 0.5)
        cv.line(bx + 3, 132, bx + 15, 117, IRON, 2.2)
        cv.line(bx + 3, 131, bx + 14, 117, IRON, 3.2)
        for by in (119, 125, 130):
            cv.put(bx, by, IRON, 4.8)
            cv.put(bx + 1, by + 1, IRON, 1.0)
        cv.darken(bx + 4, 117, bx + 7, 135, lambda x, y: 0.5)
    # lletres pintades directament al maó
    cv.rect(157, 63, 229, 76, PAPER, lambda x, y: 1.6 + (hr(x // 3, y // 2) - 0.5) * 0.5)
    xe = text(cv, 161, 67, 'MATERIAL', PAINT, 1.8, 0.8)
    text(cv, xe + 4, 67, 'F-9', [(20, 40, 70), (30, 60, 100), (50, 90, 140)], 1.4, 0.4)
    cv.darken(157, 63, 229, 76, lambda x, y: 0.4 if hr(x // 2, y, 5) > 0.82 else 0)
    for y in range(63, 77):                                       # la pintura segueix les juntes del maó
        if (y - 28) % 7 == 6:
            cv.darken(157, y, 229, y, 0.3)

    # ─── Cavallets (la biga d'acer hi va al damunt) ───────────────────────
    for tx in (133, 251):
        cv.darken(tx - 24, 209, tx + 24, 216, lambda x, y: 0.7 - abs(x - tx) / 40)
        for s in (-1, 1):
            cv.line(tx + s * 4, 181, tx + s * 17, 213, WALNUT, 4.6 if s < 0 else 3.4)
            cv.line(tx + s * 5, 181, tx + s * 18, 213, WALNUT, 3.2 if s < 0 else 2.2)
            cv.line(tx + s * 6, 181, tx + s * 19, 213, WALNUT, 2.0 if s < 0 else 1.2)
        cv.rect(tx - 16, 179, tx + 16, 183, WALNUT, lambda x, y: 4.6 - (y - 179) * 0.7 + (hr(x // 4, 8) - 0.5) * 0.3)
        cv.line(tx - 12, 200, tx + 12, 200, WALNUT, 2.4)
        cv.line(tx - 12, 201, tx + 12, 201, WALNUT, 1.2)
        cv.put(tx - 10, 181, IRON, 4.0); cv.put(tx + 10, 181, IRON, 4.0)

    # ─── Pilar 7 ─────────────────────────────────────────────────────────
    pillar(cv, 343, 28, FLOOR_Y - 1)
    cv.darken(325, FLOOR_Y, 361, FLOOR_Y + 5, lambda x, y: 0.8 - abs(x - 343) / 26)

    # ─── Reixes de desguàs, noves (la del pilar 7 és la trapa) ────────────
    for xa, xb in ((24, 62), (100, 138), (170, 208)):
        grate(cv, round(xa * 640 / 352), round(xb * 640 / 352))

    # ─── Tauler d'eines (365..443 × 57..156) ──────────────────────────────
    cv.rect(365, 57, 443, 156, WALNUT, 1.0)
    for y in _ys(cv, 60, 154):
        for x in _xs(cv, 368, 441):
            lvl = 2.6 + (hr(x // 11, 13) - 0.5) * 0.4 - (0.7 if (x - 368) % 11 == 0 else 0) + (0.2 if (x - 368) % 11 == 1 else 0)
            lvl += (hr(x // 11, y // 2, 14) - 0.5) * 0.15
            if (x % 8 == 4) and (y % 8 == 4):
                lvl = 0.6                                         # forats
            cv.put(x, y, WALNUT, lvl)
    cv.hline(365, 443, 57, WALNUT, 3.8)
    cv.hline(366, 442, 58, WALNUT, 2.8)
    cv.darken(368, 60, 441, 63, lambda x, y: (64 - y) / 5)

    # siluetes pintades de les eines (on va cada cosa): serra, llima i la clau anglesa
    def outline(pts):
        for x, y in pts:
            cv.put(x, y, PAPER, 2.2, 0.6)
    outline([(x, 83) for x in range(389, 435)] + [(389, y) for y in range(77, 89)] + [(434, y) for y in range(77, 89)])
    outline([(429, y) for y in range(107, 142)] + [(424, y) for y in range(107, 142)])
    outline([(376 + i // 2, 107 + i) for i in range(32)] + [(374, 104), (378, 104), (373, 101), (379, 101), (375, 106), (377, 106)])
    # martell i unes tenalles, de debò
    cv.vline(399, 110, 139, WALNUT, 4.0); cv.vline(400, 110, 139, WALNUT, 2.6); cv.vline(401, 110, 139, WALNUT, 1.4)
    cv.rect(392, 107, 407, 112, IRON, lambda x, y: 3.6 - (y - 107) * 0.45 + (0.6 if x == 392 else 0))
    cv.hline(392, 407, 107, IRON, 4.6)
    for i in range(21):
        cv.put(409 + (i // 7), 112 + i, IRON, 3.4)
        cv.put(410 + (i // 7), 112 + i, IRON, 2.6)
        cv.put(415 - (i // 7), 112 + i, IRON, 2.4)
    cv.disc(412, 115, 2.6, 2.6, IRON, 4.0)
    cv.put(412, 115, IRON, 1.2)
    for hx, hy in ((399, 105), (412, 109), (405, 73), (429, 100)):  # ganxos
        cv.put(hx, hy, IRON, 4.0)
        cv.put(hx, hy + 1, IRON, 2.4)
    # aplic de llum de paret
    cv.rect(401, 40, 409, 44, GOLD, lambda x, y: 3.4 - (y - 40) * 0.3)
    cv.vline(405, 36, 39, GOLD, 2.4)
    for y in range(45, 53):
        hw = 3 + (y - 45) * 1.2
        for x in range(round(405 - hw), round(405 + hw) + 1):
            cv.put(x, y, GREEN, 3.4 - (x - 405) / hw - (y - 45) * 0.08 + (0.8 if x == round(405 - hw) + 1 else 0), 0.4)
    cv.hline(396, 414, 53, [(255, 236, 170)], 0, 0)
    cv.disc(405, 54, 2, 1.2, PAPER, 6, 0)
    cv.glow(405, 56, 29, (255, 220, 150), 0.35)

    # ─── La badia: la llançadora i, al fons, la comporta tancada ──────────
    BX0, BX1, BY0 = 445, 635, 12
    # marc d'acer de la badia
    cv.rect(BX0 - 4, 11, BX0, FLOOR_Y - 1, IRON, lambda x, y: [1.4, 3.8, 3.0, 2.2, 1.4][x - BX0 + 4])
    cv.rect(BX1, 11, W - 1, FLOOR_Y - 1, IRON, lambda x, y: 1.6 + (0.8 if x == BX1 else 0))
    cv.rect(BX0 - 4, 8, W - 1, 11, IRON, lambda x, y: [3.8, 3.0, 2.2, 1.0][y - 8])
    for y in range(20, FLOOR_Y - 4, 21):                          # reblons del marc
        cv.put(BX0 - 2, y, IRON, 5.0)
    # interior de la badia: sostre, parets de maó i terra en perspectiva cap a la comporta
    FX0, FX1, FY0, FY1 = 469, 616, 29, 187
    for y in _ys(cv, BY0, FLOOR_Y - 1):
        for x in _xs(cv, BX0 + 1, BX1 - 1):
            if FX0 <= x <= FX1 and FY0 <= y <= FY1:
                continue
            if y > FY1:                                           # terra de la badia
                cv.put(x, y, FLOOR, 1.2 + (y - FY1) / 12 - (0.6 if x % 12 == 0 else 0))
            elif y < FY0:                                         # sostre de la badia, amb una biga
                cv.put(x, y, IRON, 0.5 + (FY0 - y) / 16 + (1.2 if y == 19 else 0) - (0.6 if y == 20 else 0))
            else:                                                 # parets laterals
                v = (y - FY0) % 8 == 7 or (x + ((y - FY0) // 8) * 7) % 14 == 0
                cv.put(x, y, BRICK, 1.2 - (0.6 if v else 0) - (0.4 if x < FX0 else 0.1) + (hr(x // 3, y // 8, 90) - 0.5) * 0.3)
    # la comporta: planxes de ferro reblades sobre taulons, corredisses a banda i banda
    GX0, GX1 = FX0 + 7, FX1 - 7
    for y in _ys(cv, FY0, FY1):
        for x in _xs(cv, FX0, FX1):
            if x < GX0 or x > GX1:                                # guies de ferro (canal en U)
                u = x - FX0 if x < GX0 else FX1 - x
                cv.put(x, y, IRON, [0.6, 2.8, 2.2, 1.6, 1.0, 0.6, 0.3][u])
                continue
            band = (y - FY0) % 27
            if band < 5:                                          # fleixos de ferro horitzontals
                lvl = [3.2, 2.6, 2.2, 1.6, 0.6][band]
                cv.put(x, y, IRON, lvl + (hr(x // 5, y, 81) - 0.5) * 0.3)
                if band == 1 and (x - GX0) % 12 == 5:
                    cv.put(x, y, IRON, 4.6)                       # reblons
                    cv.put(x, y + 1, IRON, 3.6)
                continue
            k = (x - GX0) % 15                                    # taulons verticals
            lvl = 1.8 + (hr((x - GX0) // 15, 81) - 0.5) * 0.6 + (hr(x, y // 3, 82) - 0.5) * 0.3
            if k == 0:
                lvl = 0.4
            elif k == 1:
                lvl += 0.7
            elif k == 14:
                lvl -= 0.3
            if band == 5:
                lvl -= 0.8                                        # ombra del fleix
            cv.put(x, y, WALNUT, lvl)
    # rovell que regalima dels fleixos
    for x in range(GX0, GX1, 3):
        if hr(x, 83) > 0.7:
            y0 = FY0 + 5 + int(hr(x, 84) * 5) * 27
            for y in _ys(cv, y0, min(FY1 - 11, y0 + 4 + int(hr(x, 85) * 8)) - 1):
                cv.put(x, y, RUST, 1.8 - (y - y0) * 0.05)
    # franges de perill a la vora de baix i l'escletxa de lluna per sota
    for x in _xs(cv, GX0, GX1):
        for y in range(FY1 - 9, FY1 - 1):
            yel = ((x + y) // 7) % 2 == 0
            cv.put(x, y, GOLD if yel else IRON, (3.4 if yel else 0.8) - (y - FY1 + 9) * 0.12)
        cv.put(x, FY1 - 1, IRON, 0.2)
        if hr(x // 4, 86) > 0.15:                             # (la claror de l'escletxa tremola una mica)
            fi = hr(x // 5, 88) * 6.283
            cv.flat(x, FY1, mix((150, 170, 230), (230, 236, 255), min(1, max(0, hr(x, 87) + 0.3 * math.sin(ph * (1 + x // 5 % 3) + fi)))))
    # la lluna que s'escola per sota, tirada pel terra de la badia
    for y in _ys(cv, FY1 + 1, FLOOR_Y - 1):
        for x in _xs(cv, GX0 - 5, GX1 + 5):
            a = (1 - (y - FY1) / (FLOOR_Y - FY1)) * 0.5
            if a > B4[y & 3][x & 3]:
                cv.P[x, y] = mix(cv.P[x, y], (150, 170, 230), 0.4) + (255,)
    # cadenes que pugen del cap de la comporta fins al tambor del sostre
    for cx_ in (GX0 + 13, GX1 - 13):
        cv.rect(cx_ - 3, FY0, cx_ + 3, FY0 + 3, IRON, lambda x, y: 3.8 - (y - FY0) * 0.3)      # orella
        cv.put(cx_, FY0 + 1, IRON, 0.6)
        for y in range(BY0 + 7, FY0):
            k = (y - BY0) % 4
            cv.put(cx_, y, IRON, [3.4, 3.8, 1.0, 2.6][k])
            cv.put(cx_ + 1, y, IRON, [2.0, 1.2, 3.2, 2.0][k])
            if k == 2:
                cv.put(cx_ - 1, y, IRON, 2.2)
    cv.rect(GX0 + 5, BY0 + 3, GX1 - 5, BY0 + 9, IRON, lambda x, y: [1.2, 3.6, 3.0, 2.4, 1.8, 1.2, 0.6][y - BY0 - 3])  # tambor
    for x in range(GX0 + 8, GX1 - 5, 9):
        cv.vline(x, BY0 + 4, BY0 + 8, IRON, 0.8)
    # encaix de la palanca de dos metres, a la guia esquerra, amb la roda dentada i el retén
    cv.rect(FX0 - 1, 69, FX0 + 16, 93, IRON, lambda x, y: 3.0 - (x - FX0) * 0.1 - (y - 69) * 0.025)
    cv.hline(FX0 - 1, FX0 + 16, 69, IRON, 4.4)
    cv.vline(FX0 + 16, 70, 93, IRON, 1.2)
    for a_ in range(0, 360, 24):
        ca, sa = math.cos(math.radians(a_)), math.sin(math.radians(a_))
        cv.put(round(FX0 + 8 + ca * 7.4), round(77 + sa * 7.4), IRON, 3.0 - sa)
        cv.put(round(FX0 + 8 + ca * 6.6), round(77 + sa * 6.6), IRON, 3.0 - sa)
    cv.disc(FX0 + 8, 77, 6, 6, IRON, lambda nx, ny: 4.0 - nx - ny)
    cv.disc(FX0 + 8, 77, 1.6, 1.6, IRON, 1.2)
    cv.rect(FX0 + 5, 84, FX0 + 11, 92, SIL, 0.4, 0)                       # l'encaix (buit)
    cv.hline(FX0 + 5, FX0 + 11, 84, SIL, 1.6, 0)
    cv.line(FX0 + 13, 70, FX0 + 17, 76, IRON, 4.0)                        # retén
    cv.line(FX0 + 14, 70, FX0 + 18, 76, IRON, 2.0)
    # carrils dins la badia
    for ry in (200, 195):
        cv.hline(BX0 + 1, BX1 - 1, ry, IRON, 3.6)
        cv.hline(BX0 + 1, BX1 - 1, ry + 1, IRON, 1.6)
    # la llançadora, nova de trinca
    shuttle(cv, 451, 144)
    cv.darken(BX0 + 1, 196, BX1 - 1, 203, lambda x, y: 0.5)
    # llum de servei de la badia, engabiat al sostre
    cv.vline(539, BY0 + 8, 16, IRON, 1.4)
    cv.disc(539, 19, 4, 2.6, IRON, 2.6)
    cv.disc(539, 21, 3, 1.9, [(255, 236, 180)], 0, 0)
    for gx in (536, 539, 542):                                    # la gàbia
        cv.vline(gx, 20, 23, IRON, 1.6)
    cv.glow(539, 23, 35, (255, 220, 160), 0.35)
    # tint fred de la lluna que entra per sota la comporta
    cv.tint(BX0, FY1 - 27, BX1, FLOOR_Y + 40, (150, 170, 230), lambda x, y: 0.2 * min(1, _moon(x, y)))

    # ─── Làmpada penjada ──────────────────────────────────────────────────
    cv.vline(200, 27, 37, IRON, 1.4)
    cv.rect(198, 35, 202, 37, GOLD, 2.6)
    for y in range(37, 46):
        hw = 3 + (y - 37) * 1.6
        for x in range(round(200 - hw), round(200 + hw) + 1):
            cv.put(x, y, GREEN, 3.0 - (x - 200) / hw * 1.2 - (y - 37) * 0.1 + (0.9 if y == 45 else 0), 0.3)
    cv.hline(185, 215, 46, [(255, 240, 190)], 0, 0)
    cv.disc(200, 48, 3.2, 2.1, PAPER, 6, 0)
    cv.glow(200, 51, 53, (255, 222, 150), 0.4)

    # pols que sura sota la làmpada i a la llum de la lluna que entra per sota la comporta
    dust(cv, tt, 30, 61, (168, 59, 232, 139), (255, 236, 190), 0.6, lamp_cone, fall=(-4, 8), wander=2.7)
    dust(cv, tt, 28, 62, (448, 165, 632, 248), (206, 216, 248), 0.85, lambda x, y: min(1.0, _moon(x, y) * 1.4),
         fall=(-3, -7), wander=2.7)

    # ─── Detalls: caixes a la vora de la porta ────────────────────────────
    crate(cv, 80, 177, 27, 25)
    crate(cv, 85, 155, 19, 23, small=True)
    cv.darken(75, FLOOR_Y - 1, 112, FLOOR_Y + 7, lambda x, y: 0.7)


def crate(cv, x0, y0, w, h, small=False):
    """Caixa de fusta amb tires de ferro i «F-9» de plantilla."""
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            lvl = 2.6 + (hr(x // 5, y0) - 0.5) * 0.3 - (0.7 if (y - y0) % 7 == 6 else 0) + (0.2 if (y - y0) % 7 == 0 else 0)
            if x in (x0, x0 + w - 1) or y in (y0, y0 + h - 1):
                lvl = 3.4 if (x == x0 or y == y0) else 1.2
            elif x in (x0 + 1, x0 + w - 2) or y in (y0 + 1, y0 + h - 2):
                lvl = 2.0 + (0.6 if (x == x0 + 1 or y == y0 + 1) else 0)
            cv.put(x, y, WALNUT, lvl)
    cv.line(x0 + 2, y0 + h - 3, x0 + w - 3, y0 + 2, WALNUT, 3.4)
    cv.line(x0 + 2, y0 + h - 2, x0 + w - 3, y0 + 3, WALNUT, 1.4)
    for cx, cy in ((x0 + 1, y0 + 1), (x0 + w - 2, y0 + 1), (x0 + 1, y0 + h - 2), (x0 + w - 2, y0 + h - 2)):
        cv.put(cx, cy, IRON, 4.0)                                 # claus
    if not small:
        cv.rect(x0 + 4, y0 + 8, x0 + w - 5, y0 + 14, MANILA, 2.6)
        text(cv, x0 + 7, y0 + 9, 'F-9', [(20, 18, 16), (40, 30, 24)], 0.4, 0)


def pipe(cv, aged=False, x=300, w=15, run_y=35, y_end=FLOOR_Y - 1, from_left=True):
    """El conducte de pressió: tram horitzontal sota la biga, colze i baixada fins a terra, amb vàlvula
    i manòmetre. Al passat, de coure lluent; al present, el mateix tub, rovellat."""
    rmp = COPPER if not aged else RUST
    LV = [1.6, 3.0, 4.2, 3.8, 3.2, 2.8, 2.4, 2.0, 1.6, 1.2, 0.6]
    lv = [_interp(LV, i / (w - 1)) for i in range(w)]
    # tram horitzontal
    if from_left:
        for xx in _xs(cv, 0, x + w - 1):
            for i in range(w - 2):
                yy = run_y + i
                if xx < x + i:
                    cv.put(xx, yy, rmp, lv[i] + (0.3 if not aged else (hr(xx // 3, yy) - 0.5) * 0.6))
        for xx in range(40, x, 61):                              # brides i abraçadores
            cv.rect(xx, run_y - 2, xx + 3, run_y + w - 2, rmp, lambda a, b: 3.6 - (b - run_y) * 0.2 + (0.6 if a == xx else 0))
            cv.vline(xx + 1, run_y - 9, run_y - 3, IRON, 2.0)       # penjador de la biga
    # baixada
    for yy in _ys(cv, run_y, y_end):
        for i in range(w):
            cv.put(x + i, yy, rmp, lv[i] + ((hr((x + i) // 2, yy // 3) - 0.5) * 0.6 if aged else 0))
    # colze
    cv.disc(x + 5, run_y + 5, 8, 8, rmp, lambda nx, ny: 3.0 - nx - ny * 0.8)
    for yy in range(run_y + 21, y_end, 45):                       # brides, amb cargols
        cv.rect(x - 2, yy, x + w + 1, yy + 3, rmp, lambda a, b: 3.8 - (b - yy) * 0.6)
        cv.put(x - 1, yy + 1, rmp, 5.0); cv.put(x + w, yy + 1, rmp, 2.6)
    cv.rect(x - 4, y_end - 4, x + w + 3, y_end, IRON, lambda a, b: 2.8 - (b - y_end + 4) * 0.35)
    cv.hline(x - 4, x + w + 3, y_end - 4, IRON, 3.8)
    # manòmetre
    mx, my = x + w + 7, 93
    cv.rect(x + w, my - 1, mx - 4, my + 1, rmp, lambda a, b: 3.4 - (b - my + 1) * 0.6)
    cv.disc(mx, my, 8, 8, GOLD if not aged else RUST, lambda nx, ny: 3.6 - nx - ny)
    cv.disc(mx, my, 6, 6, PAPER if not aged else GRAY, lambda nx, ny: (4.4 if not aged else 3.2) - ny * 0.4, 0.4)
    for a in range(200, 341, 20):
        rr = 4.6 if a % 40 == 0 else 5.0
        cv.put(round(mx + math.cos(math.radians(a)) * rr), round(my + math.sin(math.radians(a)) * rr), IRON, 1.0, 0)
    cv.put(round(mx + math.cos(math.radians(330)) * 4.6), round(my + math.sin(math.radians(330)) * 4.6), RED, 3.6, 0)
    ang = math.radians(300 if not aged else 205)                  # al present, l'agulla a zero
    for r in range(5):
        cv.flat(round(mx + math.cos(ang) * r), round(my + math.sin(ang) * r), (170, 30, 30))
    cv.flat(mx, my, (40, 30, 30))
    if not aged:
        cv.put(mx - 3, my - 4, PAPER, 6.0, 0)                     # reflex del vidre
    # vàlvula de volant
    vx, vy = x + w // 2, 144
    cv.rect(x - 3, vy - 8, x + w + 2, vy + 8, IRON if not aged else RUST, lambda a, b: 3.0 - (a - x) * 0.12 + (0.8 if b == vy - 8 else 0))
    cv.rect(vx - 2, vy - 3, vx + 2, vy + 3, IRON, 4.0)
    wheel = RED if not aged else RUST
    for a in range(0, 360, 2):
        for rr in (10.5, 11.5, 12.3):
            px = round(vx + math.cos(math.radians(a)) * rr)
            py = round(vy + math.sin(math.radians(a)) * rr * 0.9)
            cv.put(px, py, wheel, {10.5: 4.4, 11.5: 3.6, 12.3: 2.6}[rr] - math.sin(math.radians(a)) * 0.8)
    for a in (45, 135, 225, 315):
        for rr in range(3, 11):
            cv.put(round(vx + math.cos(math.radians(a)) * rr), round(vy + math.sin(math.radians(a)) * rr * 0.9), wheel, 3.6)
    cv.disc(vx, vy, 2.4, 2.2, wheel, lambda nx, ny: 4.0 - nx - ny)


# ─── Props ──────────────────────────────────────────────────────────────────

def p_biga_acer(cv):
    """Biga d'acer de dos metres, damunt dels cavallets."""
    x0, x1, y0 = 107, 280, 165
    for x in range(x0, x1 + 1):
        g = (hr(x // 4, 61) - 0.5) * 0.4
        cv.put(x, y0, ACER, 5.2 + g)
        cv.put(x, y0 + 1, ACER, 4.6 + g)
        cv.put(x, y0 + 2, ACER, 3.8 + g)
        for y in range(y0 + 3, y0 + 11):
            cv.put(x, y, ACER, 2.0 + g - (y - y0 - 3) * 0.12 + (0.8 if y == y0 + 3 else 0) + (hr(x // 2, y, 62) - 0.5) * 0.2)
        cv.put(x, y0 + 11, ACER, 3.4 + g)
        cv.put(x, y0 + 12, ACER, 1.4 + g)
    for xe in (x0, x1):                                          # testes tallades
        cv.vline(xe, y0, y0 + 12, ACER, 4.4 if xe == x0 else 1.0)
    cv.vline(x0 + 1, y0, y0 + 12, ACER, 3.2)
    for x in range(x0 + 8, x1, 31):                               # marques de guix
        cv.vline(x, y0 + 4, y0 + 8, PAPER, 3.0, 0.5)
        cv.put(x + 1, y0 + 4, PAPER, 2.4, 0.5)
    cv.darken(x0, y0 + 13, x1, y0 + 16, lambda x, y: 0.6)


def p_biga_ferro9(cv):
    """Biga de ferro-9 al bastidor, amb l'etiqueta de la caldera 4."""
    x0, x1, y0 = 107, 280, 97
    for x in range(x0, x1 + 1):
        sh = math.sin(x / 12.0) * 0.25
        cv.put(x, y0, F9, 6.4 + sh)
        cv.put(x, y0 + 1, F9, 5.6 + sh)
        cv.put(x, y0 + 2, F9, 4.6 + sh)
        for y in range(y0 + 3, y0 + 12):
            cv.put(x, y, F9, 3.0 + sh - (y - y0 - 3) * 0.14 + (1.0 if y == y0 + 3 else 0))
        cv.put(x, y0 + 12, F9, 4.6 + sh)
        cv.put(x, y0 + 13, F9, 2.4)
    cv.vline(x0, y0, y0 + 13, F9, 6.0)
    cv.vline(x0 + 1, y0, y0 + 13, F9, 4.8)
    cv.vline(x1, y0, y0 + 13, F9, 2.0)
    for i in range(6):                                           # reflex llarg
        cv.hline(147 + i * 19, 155 + i * 19, y0 + 5, F9, 5.4)
        cv.hline(149 + i * 19, 153 + i * 19, y0 + 6, F9, 4.6)
    cv.glow(193, y0 + 7, 61, (150, 210, 255), 0.18)
    # etiqueta de cartró penjada amb un cordill
    cv.line(200, y0 + 13, 203, y0 + 17, PAPER, 2.4)
    cv.rect(195, y0 + 17, 216, y0 + 23, MANILA, lambda x, y: 4.2 - (y - y0 - 17) * 0.15)
    cv.put(197, y0 + 19, IRON, 1.0)
    text(cv, 200, y0 + 18, '4', RED, 2.6, 0.6)
    cv.hline(205, 214, y0 + 20, RED, 2.6)
    cv.hline(205, 211, y0 + 22, RED, 2.0)


def p_serra(cv):
    """Serra de metall penjada al tauler (arc, fulla dentada i mànec)."""
    y = 83
    cv.hline(391, 432, y - 5, IRON, 3.8)
    cv.hline(391, 432, y - 4, IRON, 2.4)
    cv.rect(389, y - 5, 392, y + 5, IRON, 3.0)
    cv.rect(429, y - 5, 432, y + 5, IRON, 2.2)
    cv.vline(389, y - 5, y + 5, IRON, 4.2)
    for x in range(392, 430):
        cv.put(x, y + 3, ACER, 5.4)
        cv.put(x, y + 4, ACER, 4.0)
        cv.put(x, y + 5, ACER, 3.6 if x % 2 else 1.4)
    cv.put(390, y + 4, IRON, 4.6); cv.put(430, y + 4, IRON, 4.0)    # palometes
    cv.put(405, y - 9, IRON, 3.6); cv.put(405, y - 8, IRON, 3.0); cv.put(405, y - 7, IRON, 2.4); cv.put(405, y - 6, IRON, 2.0)
    for yy in range(y - 3, y + 10):                              # mànec de fusta
        for xx in range(433, 440):
            cv.put(xx, yy, WALNUT, 4.0 - (xx - 433) * 0.4 + (0.4 if yy < y else 0) - (0.6 if yy == y + 9 else 0))
    cv.rect(435, y + 1, 437, y + 5, WALNUT, 0.8)


def p_llima(cv):
    """Llima fina penjada, amb el mànec de fusta a dalt."""
    for y in range(104, 118):
        cv.put(425, y, WALNUT, 4.2 - (0.4 if y > 115 else 0))
        cv.put(426, y, WALNUT, 3.6)
        cv.put(427, y, WALNUT, 2.8)
        cv.put(428, y, WALNUT, 1.8)
    cv.hline(425, 428, 104, WALNUT, 4.6)
    cv.hline(424, 429, 118, GOLD, 4.0)
    cv.hline(424, 429, 119, GOLD, 2.6)
    for y in range(120, 145):
        w_ = 2 if y > 138 else 3
        for x in range(426 - w_ // 2, 427 + (w_ + 1) // 2):
            cv.put(x, y, ACER, (5.0 if x == 426 - w_ // 2 else 3.0) - (0.6 if y % 2 else 0))
    cv.put(426, 103, IRON, 3.0)
    cv.put(426, 102, IRON, 2.4)


def p_marca(cv):
    carved_mark(cv, 336, 107)


# Animació de fons: el foc de les calderes es mou darrere la porta, la pols sura a la llum de la làmpada i de
# la lluna, i l'escletxa de sota la comporta tremola.
_ANIM_BOXES = [
    (0, 92, 125, 228),          # el foc, darrere la porta, i la seva claror
    (155, 46, 245, 155),        # la pols al con de la làmpada
    (435, 150, 639, 265),       # l'escletxa de la comporta i la pols a la lluna
]


@lru_cache(maxsize=None)
def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv.img


def _ambient_frames():
    return clip_frames(bg, LIGHT, 24, _ANIM_BOXES, base=_base())


ANIMS = {'ambient': {'frames': _ambient_frames, 'frameDuration': 130}}

PROPS = {
    'biga_acer': p_biga_acer,
    'biga_ferro9': p_biga_ferro9,
    'serra': p_serra,
    'llima': p_llima,
    'marca_pilar': p_marca,
}
