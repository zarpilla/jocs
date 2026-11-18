#!/usr/bin/env python3
"""
Personatges per a la prova de 640×360: els mateixos de hd/personatges.py, redibuixats a ×4/3
(una persona fa ≈110 px; fotograma de 65×116, peus a (34, 111)).

No canvia res de la sortida de 480: en aquest procés se substitueix la figura de hd/characters.py (Fig) per
FigK, que rep les mateixes ordres en coordenades de disseny (les de 49×87) i les rasteritza a la mida gran:
  - el·lipsoides, extremitats, troncs i polígons es tornen a dibuixar a la resolució nova (amb volum i
    contorn d'un píxel real), no s'amplien;
  - els píxels solts (`px`, `shade`) ocupen la seva zona (1 o 2 píxels reals);
  - les línies són d'un píxel real.
La cara (ulls, celles, nas, boca) i la diadema de l'Iri es dibuixen a part, píxel a píxel a la mida nova.

Els fulls (main) es dibuixen a ART_SCALE = 1, com les sales en 3D (vegeu docs/guia-art-profunditat.md). Amb
ART_SCALE = 2 es dibuixarien amb FigK2 (els detalls píxel a píxel, en blocs de 2×2) i portarien `artScale: 2`.

Ús (des de tools/): python3 hd640/draw_characters.py [carpeta]   (per defecte, hd640/characters/)
"""
import json
import math
import sys
from contextlib import contextmanager
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))

from PIL import Image  # noqa: E402

import hd.characters as C  # noqa: E402
from hd.pix import mix  # noqa: E402

K = 4 / 3
K640 = K
ART_SCALE = 1     # els fulls (main): a 1×, com les sales en 3D (fins al 18-11-2026, a 2× amb FigK2)
S = 1             # l'escala d'aquest procés: 1, o ART_SCALE en fer els fulls (vegeu install)


def f(u):
    """Coordenada de disseny (centre de píxel) → coordenada real."""
    return (u + 0.5) * K - 0.5


def g(X):
    """Coordenada real → de disseny."""
    return (X + 0.5) / K - 0.5


def span(i):
    """Els píxels reals que ocupa el píxel de disseny i."""
    return range(math.ceil(i * K - 0.5), math.ceil((i + 1) * K - 0.5))


class FigK(C.Fig):
    """Fig que dibuixa a ×K. `w`, `h` i `buf` són a la mida real (com els fa servir bastida_over)."""

    def __init__(self, w, h):
        super().__init__(round(w * K), round(h * K))

    # primitives amb volum: es rasteritzen a la mida real
    def ell(self, cx, cy, rx, ry, mat, base, amp=1.6, cont=None, lvlfn=None, clip=None):
        cx, cy, rx, ry = f(cx + self.ox), f(cy + self.oy), rx * K, ry * K
        pix = {}
        for y in range(math.floor(cy - ry), math.ceil(cy + ry) + 1):
            for x in range(math.floor(cx - rx), math.ceil(cx + rx) + 1):
                nx, ny = (x - cx) / rx, (y - cy) / ry
                r2 = nx * nx + ny * ny
                if r2 <= 1 and (clip is None or clip(g(x), g(y) - self.oy)):
                    pix[(x, y)] = (nx, ny, math.sqrt(1 - r2))
        self._paint(pix, mat, base, amp, cont, lvlfn)
        return pix

    def limb(self, a, b, r0, r1, mat, base, amp=1.6, cont=None, lvlfn=None, clip=None):
        ax, ay = f(a[0] + self.ox), f(a[1] + self.oy)
        bx, by = f(b[0] + self.ox), f(b[1] + self.oy)
        r0, r1 = r0 * K, r1 * K
        dx, dy = bx - ax, by - ay
        L2 = dx * dx + dy * dy or 1e-6
        R = max(r0, r1)
        pix = {}
        for y in range(math.floor(min(ay, by) - R), math.ceil(max(ay, by) + R) + 1):
            for x in range(math.floor(min(ax, bx) - R), math.ceil(max(ax, bx) + R) + 1):
                t = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / L2))
                cx, cy = ax + dx * t, ay + dy * t
                r = r0 + (r1 - r0) * t
                ex, ey = x - cx, y - cy
                d2 = (ex * ex + ey * ey) / (r * r)
                if d2 <= 1 and (clip is None or clip(g(x), g(y) - self.oy)):
                    pix[(x, y)] = (ex / r, ey / r, math.sqrt(1 - d2))
        self._paint(pix, mat, base, amp, cont, lvlfn)
        return pix

    def lathe(self, y0, y1, edges, mat, base, amp=1.6, cont=None, lvlfn=None, tilt=0.0):
        """Els contorns de disseny (una parella per fila) s'interpolen entre files."""
        y0, y1 = math.floor(y0), math.floor(y1)
        pix = {}
        for Y in range(math.floor(f(y0 - 0.5 + self.oy)), math.ceil(f(y1 + 0.5 + self.oy)) + 1):
            yd = g(Y) - self.oy
            if not (y0 - 0.5 <= yd < y1 + 0.5):
                continue
            lo = math.floor(yd)
            t = yd - lo
            e0 = edges(lo) if y0 <= lo <= y1 else None
            e1 = edges(lo + 1) if y0 <= lo + 1 <= y1 else None
            if e0 and e1:
                e = (e0[0] + (e1[0] - e0[0]) * t, e0[1] + (e1[1] - e0[1]) * t)
            else:
                e = e0 or e1
                if not e or (e is e0 and t > 0.5) or (e is e1 and t < 0.5):
                    continue
            xl, xr = f(e[0] + self.ox) - K / 2 + 0.5, f(e[1] + self.ox) + K / 2 - 0.5
            mid, half = (xl + xr) / 2, max(0.5, (xr - xl) / 2)
            for x in range(math.ceil(xl - 0.01), math.floor(xr + 0.01) + 1):
                u = max(-1.0, min(1.0, (x - mid) / (half + 0.5)))
                nz = math.sqrt(max(0.0, 1 - u * u - tilt * tilt))
                pix[(x, Y)] = (u, tilt, nz)
        self._paint(pix, mat, base, amp, cont, lvlfn)
        return pix

    def poly(self, pts, mat, base, amp=0.0, cont=None, lvlfn=None, normal=None):
        pts = [(f(px + self.ox), f(py + self.oy)) for px, py in pts]
        ys = [p[1] for p in pts]
        pix = {}
        for y in range(math.floor(min(ys)), math.ceil(max(ys)) + 1):
            xs = []
            for (xa, ya), (xb, yb) in zip(pts, pts[1:] + pts[:1]):
                if (ya <= y < yb) or (yb <= y < ya):
                    xs.append(xa + (y - ya) * (xb - xa) / (yb - ya))
            xs.sort()
            for a, b in zip(xs[::2], xs[1::2]):
                for x in range(math.ceil(a - 0.5), math.floor(b - 0.5) + 1):
                    pix[(x, y)] = normal(g(x), g(y) - self.oy) if normal else (0.0, 0.0, 1.0)
        self._paint(pix, mat, base, amp, cont, lvlfn)
        return pix

    def _paint(self, pix, mat, base, amp, cont, lvlfn):
        # lvlfn rep coordenades de disseny (com a 480), però es crida per a cada píxel real
        if lvlfn:
            fn = lvlfn
            lvlfn = lambda x, y: fn(g(x), g(y))  # noqa: E731
        super()._paint(pix, mat, base, amp, cont, lvlfn)

    # píxels de disseny: ocupen la seva zona
    def _zone(self, x, y):
        i, j = int(round(x + self.ox)), int(round(y + self.oy))
        return [(X, Y) for Y in span(j) for X in span(i) if 0 <= X < self.w and 0 <= Y < self.h]

    def px(self, x, y, mat, lvl):
        for X, Y in self._zone(x, y):
            self.buf[Y][X] = (mat, lvl)

    def shade(self, x, y, d, only=None):
        for X, Y in self._zone(x, y):
            self.rshade(X, Y, d, only)

    def erase(self, x, y):
        for X, Y in self._zone(x, y):
            self.buf[Y][X] = None

    def get(self, x, y):
        X, Y = round(f(x + self.ox)), round(f(y + self.oy))
        if 0 <= X < self.w and 0 <= Y < self.h:
            return self.buf[Y][X]
        return None

    def line(self, x0, y0, x1, y1, mat, lvl):
        """Línia d'un píxel real."""
        X0, Y0, X1, Y1 = f(x0 + self.ox), f(y0 + self.oy), f(x1 + self.ox), f(y1 + self.oy)
        n = max(1, int(math.ceil(max(abs(X1 - X0), abs(Y1 - Y0)))))
        for i in range(n + 1):
            t = i / n
            self.rpx(X0 + (X1 - X0) * t, Y0 + (Y1 - Y0) * t, mat, lvl)

    # píxels reals (per als detalls dibuixats a la mida nova)
    def rpx(self, X, Y, mat, lvl):
        X, Y = int(round(X)), int(round(Y))
        if 0 <= X < self.w and 0 <= Y < self.h:
            self.buf[Y][X] = (mat, lvl)

    def rshade(self, X, Y, d, only=None):
        X, Y = int(round(X)), int(round(Y))
        if 0 <= X < self.w and 0 <= Y < self.h and self.buf[Y][X]:
            m, l = self.buf[Y][X]
            if only is None or m is only or (isinstance(only, (list, tuple)) and m in only):
                self.buf[Y][X] = (m, l + d)


class FigK2(FigK):
    """FigK a S× (S = 2): la mateixa figura, amb l'API en píxels de 640 i el buffer a S×.
      - el que té volum (`ell`, `limb`, `lathe`, `poly`) i els píxels de disseny (`px`, `shade`, `erase`, `get`) es
        rasteritzen a la resolució real (`f`, `g` i `span` hi treballen amb K = 4/3 × S);
      - els detalls píxel a píxel (`rpx`, `rshade`, i `line`, que hi passa), en coordenades de 640: cada un, un bloc
        S×S. La cara, la diadema i les ulleres queden igual que a 640."""

    def __init__(self, w, h):
        super().__init__(w, h)
        self.S = S
        self.w, self.h = self.w * S, self.h * S
        self.buf = [[None] * self.w for _ in range(self.h)]
        self._fine = 0

    @contextmanager
    def _fi(self):
        global K
        self._fine += 1
        K = K640 * S
        try:
            yield
        finally:
            self._fine -= 1
            if not self._fine:
                K = K640

    def ell(self, *a, **kw):
        with self._fi():
            return super().ell(*a, **kw)

    def limb(self, *a, **kw):
        with self._fi():
            return super().limb(*a, **kw)

    def lathe(self, *a, **kw):
        with self._fi():
            return super().lathe(*a, **kw)

    def poly(self, *a, **kw):
        with self._fi():
            return super().poly(*a, **kw)

    def px(self, *a, **kw):
        with self._fi():
            return super().px(*a, **kw)

    def shade(self, *a, **kw):
        with self._fi():
            return super().shade(*a, **kw)

    def erase(self, *a, **kw):
        with self._fi():
            return super().erase(*a, **kw)

    def get(self, *a, **kw):
        with self._fi():
            return super().get(*a, **kw)

    def _blk(self, X, Y):
        X, Y = int(round(X)), int(round(Y))
        return [(X * S + i, Y * S + j) for j in range(S) for i in range(S)]

    def rpx(self, X, Y, mat, lvl):
        if self._fine:
            return super().rpx(X, Y, mat, lvl)
        for x, y in self._blk(X, Y):
            super().rpx(x, y, mat, lvl)

    def rshade(self, X, Y, d, only=None):
        if self._fine:
            return super().rshade(X, Y, d, only)
        for x, y in self._blk(X, Y):
            super().rshade(x, y, d, only)


# ─── La cara, a la mida nova ─────────────────────────────────────────────────

def _eye(fg, x0, ey, inner_right, spec, closed):
    """Un ull de 3×2 (parpella + blanc, iris i pupil·la cap al nas); x0 = píxel de l'esquerra."""
    eye = spec.get('eye', (34, 22, 30))
    iris = spec.get('iris', (70, 50, 40))
    if closed:
        for i in range(3):
            fg.rpx(x0 + i, ey, eye, 0)
        return
    for i in range(3):
        fg.rpx(x0 + i, ey - 1, eye, 0)
    dark = mix(iris, eye, 0.6)
    rows = ([C.EYE_W, iris, dark], [C.EYE_W, iris, iris])            # dues files: blanc, iris i pupil·la
    rows = [row if inner_right else row[::-1] for row in rows]
    if spec.get('mira'):                                 # mira a un costat: l'iris i la nineta, a aquella banda
        rows = ([iris, dark, C.EYE_W], [iris, iris, C.EYE_W]) if spec['mira'] < 0 else \
            ([C.EYE_W, dark, iris], [C.EYE_W, iris, iris])
    for j, row in enumerate(rows):
        for i, c in enumerate(row):
            fg.rpx(x0 + i, ey + j, c, 0)
    S = spec['skin']
    for i in range(3):                                   # la parpella de sota, una mica d'ombra
        fg.rshade(x0 + i, ey + 2, -0.35, S)


def front_face(fg, p, spec):
    hx, hy = p.head
    S = spec['skin']
    HX, HY = f(hx + fg.ox), f(hy + fg.oy)
    brow = spec.get('brow', (40, 24, 28))
    eye = spec.get('eye', (34, 22, 30))
    ey = round(f(int(hy + 0.5)))
    lx, rx = round(HX - 5.5), round(HX + 2.5)           # els ulls: 3 px, separats 5 px
    closed = spec.get('closed')
    _eye(fg, lx, ey, True, spec, closed)
    _eye(fg, rx, ey, False, spec, closed)
    if spec.get('lashes') and not closed:
        fg.rpx(lx - 1, ey - 2, eye, 0); fg.rpx(lx - 1, ey - 1, eye, 0)
        fg.rpx(rx + 3, ey - 2, eye, 0); fg.rpx(rx + 3, ey - 1, eye, 0)
    if spec.get('liner'):
        liner = spec['liner']
        fg.rpx(lx - 1, ey, liner, 0); fg.rpx(rx + 3, ey, liner, 0)
    # celles: quatre píxels en arc
    by = ey - 4 + round(spec.get('brow_dy', 0) * K)
    for dx, dy in ((-1, 1), (0, 0), (1, 0), (2, 0)):
        fg.rpx(lx + dx, by + dy, brow, 0)
    for dx, dy in ((0, 0), (1, 0), (2, 0), (3, 1)):
        fg.rpx(rx + dx, by + dy, brow, 0)
    # nas: llum a l'esquerra del pont, ombra a la dreta i a sota
    nx = round(HX - 0.5)
    for y in range(ey, ey + 3):
        fg.rshade(nx - 1, y, +0.5, S)
    fg.rshade(nx + 1, ey + 2, -0.7, S); fg.rshade(nx + 1, ey + 3, -0.9, S)
    fg.rshade(nx, ey + 4, -1.1, S); fg.rshade(nx - 1, ey + 4, -0.6, S); fg.rshade(nx + 1, ey + 4, -0.8, S)
    fg.rshade(nx - 2, ey + 4, -0.3, S)
    if spec.get('blush'):
        fg.rshade(lx - 1, ey + 3, -0.4, S); fg.rshade(lx, ey + 3, -0.4, S)
        fg.rshade(rx + 2, ey + 3, -0.6, S); fg.rshade(rx + 3, ey + 3, -0.6, S)
    # boca: quatre píxels; parlant, oberta
    my = ey + 7
    lip = spec.get('lip', C.LIP)
    m0 = nx - 2
    if p.talk:
        for i in range(4):
            fg.rpx(m0 + i, my, C.MOUTH if 0 < i < 3 else lip, 0)
        fg.rpx(m0 + 1, my + 1, C.MOUTH, 0); fg.rpx(m0 + 2, my + 1, C.MOUTH, 0)
        fg.rpx(m0, my + 1, lip, 0); fg.rpx(m0 + 3, my + 1, lip, 0)
        fg.rpx(m0 + 1, my + 2, lip, 0); fg.rpx(m0 + 2, my + 2, lip, 0)
    else:
        for i in range(4):
            fg.rpx(m0 + i, my, mix(lip, C.MOUTH, 0.5) if 0 < i < 3 else lip, 0)
        fg.rshade(m0 + 1, my + 1, +0.4, S); fg.rshade(m0 + 2, my + 1, +0.4, S)
        fg.rshade(m0 + 1, my + 2, -0.3, S); fg.rshade(m0 + 2, my + 2, -0.3, S)


def side_face(fg, p, spec):
    hx, hy = p.head
    S = spec['skin']
    HX = f(hx + fg.ox)
    eye = spec.get('eye', (34, 22, 30))
    iris = spec.get('iris', (70, 50, 40))
    brow = spec.get('brow', (40, 24, 28))
    ey = round(f(int(hy + 0.5)))
    ex = round(HX - 5.5)                                 # l'ull, de perfil: 2 px d'ample
    if spec.get('closed'):
        fg.rpx(ex, ey, eye, 0); fg.rpx(ex + 1, ey, eye, 0)
    else:
        for i in range(3):
            fg.rpx(ex - 1 + i, ey - 1, eye, 0)
        fg.rpx(ex - 1, ey, C.EYE_W, 0); fg.rpx(ex, ey, iris, 0); fg.rpx(ex + 1, ey, mix(iris, eye, 0.6), 0)
        fg.rpx(ex - 1, ey + 1, C.EYE_W, 0); fg.rpx(ex, ey + 1, iris, 0)
        fg.rshade(ex, ey + 2, -0.35, S); fg.rshade(ex + 1, ey + 2, -0.35, S)
        if spec.get('lashes'):
            fg.rpx(ex - 2, ey - 2, eye, 0); fg.rpx(ex - 2, ey - 1, eye, 0)
        if spec.get('liner'):
            fg.rpx(ex + 2, ey, spec['liner'], 0)
    by = ey - 4 + round(spec.get('brow_dy', 0) * K)
    for dx, dy in ((-2, 0), (-1, 0), (0, 0), (1, 1)):
        fg.rpx(ex + dx, by + dy, brow, 0)
    # orella (amb el forat)
    oxd, eyd = int(hx + 2.5) + 0.5, int(hy + 0.5)
    fg.ell(oxd, eyd + 2, 1.6, 2.2, S, 2.6, amp=1.2)
    fg.rshade(f(oxd), f(eyd + 2) - 0.5, -1.2, S); fg.rshade(f(oxd), f(eyd + 2) + 0.5, -0.9, S)
    if spec.get('blush'):
        fg.rshade(ex + 2, ey + 3, -0.4, S); fg.rshade(ex + 3, ey + 3, -0.4, S)
    # boca
    my = ey + 7
    lip = spec.get('lip', C.LIP)
    mx = round(HX - 8.0)
    if p.talk:
        fg.rpx(mx, my, C.MOUTH, 0); fg.rpx(mx + 1, my, C.MOUTH, 0); fg.rpx(mx + 2, my, lip, 0)
        fg.rpx(mx + 1, my + 1, C.MOUTH, 0); fg.rpx(mx + 2, my + 1, lip, 0)
        fg.erase(g(mx - 1), g(my))
    else:
        fg.rpx(mx, my, lip, 0); fg.rpx(mx + 1, my, mix(lip, C.MOUTH, 0.5), 0); fg.rpx(mx + 2, my, mix(lip, C.MOUTH, 0.3), 0)


def install(art_scale=1):
    """Substitueix Fig i la cara a hd.characters (només en aquest procés). Cal fer-ho abans d'importar hd.personatges.
    `art_scale`: 1 per a figures de 640, ART_SCALE per als fulls."""
    global S
    S = art_scale
    fig = FigK2 if S > 1 else FigK
    C.Fig = fig
    C.front_face = front_face
    C.side_face = side_face
    import hd.personatges as P
    P.Fig = fig

    def headband3(fg, cx, cy, rx, ry, a0, a1, n=None):
        """La diadema de tres ratlles, d'un píxel real cadascuna."""
        CX, CY, RX, RY = f(cx), f(cy), rx * K, ry * K
        n = n or int(abs(a1 - a0) / 180 * math.pi * RX * 3)
        for k, (mat, lvl) in enumerate(((P.BAND_R, 2.8), (P.BAND_Y, 2.8), (P.BAND_G, 2.6))):
            for i in range(n + 1):
                a = math.radians(a0 + (a1 - a0) * i / n)
                fg.rpx(CX + math.cos(a) * (RX - k * 0.3), CY - math.sin(a) * (RY - k), mat,
                       lvl + 0.8 * math.sin(a) - 0.4 * math.cos(a))

    def band_on_head(fg, p, hx, hy):
        if p.f == 'D':
            headband3(fg, hx, hy - 1.4, 7.6, 5.6, 12, 168)
        elif p.f == 'L':
            for k, (mat, lvl) in enumerate(((P.BAND_R, 3.0), (P.BAND_Y, 3.0), (P.BAND_G, 2.6))):
                for i in range(49):
                    t = i / 48
                    fg.rpx(f(hx - 3.4 + 9.0 * t) + k, f(hy - 7.6 + 7.0 * t ** 1.4), mat, lvl - t * 0.8)
        else:
            headband3(fg, hx, hy - 1.2, 8.0, 5.8, 10, 170)

    def glasses(fg, p, spec):
        """Ulleres: la muntura d'un píxel, amb els ulls que es veuen a dins i un reflex."""
        hx, hy = p.head
        ey = round(f(int(hy + 0.5)))
        HX = f(hx)
        frame_lvl = 1.8

        def ring(cx, cy, rx, ry):
            for a in range(0, 360, 8):
                fg.rpx(cx + math.cos(math.radians(a)) * rx, cy + math.sin(math.radians(a)) * ry, C.STEELB, frame_lvl)
            fg.rpx(cx - rx * 0.5, cy - ry * 0.4, C.CREAM, 5.0)                 # el reflex
        if p.f == 'D':
            for cx in (round(HX - 5.5) + 1, round(HX + 2.5) + 1):
                ring(cx, ey + 0.5, 2.9, 2.4)
            for x in range(round(HX - 1.5), round(HX + 0.5) + 1):              # el pont
                fg.rpx(x, ey - 1, C.STEELB, frame_lvl)
        elif p.f == 'L':
            ex = round(HX - 5.5)
            ring(ex, ey + 0.5, 2.0, 2.4)
            fg.line(g(ex + 2), g(ey - 1), hx + 2.5, hy + 0.6, C.STEELB, frame_lvl)   # la patilla, fins a l'orella

    P._headband3 = headband3
    P._band_on_head = band_on_head
    P.glasses = glasses
    return P


# ─── Fulls ───────────────────────────────────────────────────────────────────

def main():
    P = install(ART_SCALE)
    import draw_characters as D
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / 'characters'
    D.OUT = out

    def scaled_extra(extra):
        o = dict(extra)
        o['walkSpeed'] = round(extra['walkSpeed'] * K)
        if S > 1:
            o['artScale'] = S

        def pt(q):
            return {'x': round(f(q['x'])), 'y': round(f(q['y']))}
        for key in ('walkToPoint', 'talkPoint', 'feet'):
            o[key] = pt(extra[key])
        o['collider'] = {'points': [pt(q) for q in extra['collider']['points']]}
        return o

    D.scaled_extra = scaled_extra
    D.main()


if __name__ == '__main__':
    main()
