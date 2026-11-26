#!/usr/bin/env python3
"""
Personatges de Suma Zero a 640×360: els mateixos de hd/personatges.py, redibuixats a ×4/3
(una persona fa ≈110 px; fotograma de 65×116, peus a (34, 111)).

No canvia res de la sortida de 480: en aquest procés se substitueix la figura de hd/characters.py (Fig) per
FigK, que rep les mateixes ordres en coordenades de disseny (les de 49×87) i les rasteritza a la mida gran:
  - el·lipsoides, extremitats, troncs i polígons es tornen a dibuixar a la resolució nova (amb volum i
    contorn d'un píxel real), no s'amplien;
  - els píxels solts (`px`, `shade`) ocupen la seva zona (1 o 2 píxels reals);
  - les línies són d'un píxel real.
El que és de píxel solt es redibuixa a part, píxel a píxel a la mida nova: la cara (ulls, celles, nas, boca) i
les seves variants (la cella del Director, el somriure ample, les celles arrufades, el somriure, els plecs de la
Pons), les ulleres (les de pasta de la Vet, les d'en Marcel, les de lectura de la Pons i la cadeneta), els
auriculars de l'Iri i els de la recepcionista, els cordons i la butxaca de la dessuadora, el collaret de la clau,
els estampats («</>», l'alien, el grup, els pegats, la calavera), els quadres de la franel·la, en Diu (ulls,
zzz, l'auricular), la pantalla i el llum de la NETA-3. En Ballester (gros) i el nen (petit) es dibuixen a la seva
escala, no s'amplien ni s'encongeixen.

Els fulls (main) es dibuixen a ART_SCALE = 1, com les sales en 3D (vegeu docs/guia-art-profunditat.md). Amb
ART_SCALE = 2 es dibuixarien amb FigK2: el que té volum, a la resolució real; els detalls píxel a píxel, en blocs de
2×2 (la cara és la mateixa), i el .character.json portaria `artScale: 2`.

Ús (des de tools/): python3 hd640/draw_characters.py [carpeta]   (per defecte, hd640/characters/)
Les sales de 640 que dibuixen gent fan servir `person` (hd.characters.person a ×4/3).
"""
import math
import sys
import types
from contextlib import contextmanager
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))

from PIL import Image  # noqa: E402

import hd.characters as C  # noqa: E402
from hd.pix import mix  # noqa: E402

K = 4 / 3
ART_SCALE = 1     # els fulls dels personatges (main): a 1×, com les sales en 3D (fins al 18-11-2026, a 2× amb FigK2)
S = 1             # l'escala d'aquest procés: 1, o ART_SCALE en fer els fulls (vegeu install)


def f(u):
    """Coordenada de disseny (centre de píxel) → coordenada real (a ×4/3)."""
    return (u + 0.5) * K - 0.5


def g(X):
    """Coordenada real → de disseny (a ×4/3)."""
    return (X + 0.5) / K - 0.5


class FigK(C.Fig):
    """Fig que dibuixa a ×k (k = 4/3; en Ballester i el nen, una altra: vegeu `escala`).
    `w`, `h` i `buf` són a la mida real. L'escala es llegeix en crear la figura: la de `escala` si n'hi ha, si no
    la K del mòdul (que una sala pot canviar una estona per dibuixar gent més petita)."""
    k_escala = None

    def __init__(self, w, h):
        k = type(self).k_escala or K
        super().__init__(round(w * k), round(h * k))
        self.k = k

    def F(self, u):
        return (u + 0.5) * self.k - 0.5

    def G(self, X):
        return (X + 0.5) / self.k - 0.5

    def span(self, i):
        """Els píxels reals que ocupa el píxel de disseny i."""
        k = self.k
        return range(math.ceil(i * k - 0.5), math.ceil((i + 1) * k - 0.5))

    # primitives amb volum: es rasteritzen a la mida real
    def ell(self, cx, cy, rx, ry, mat, base, amp=1.6, cont=None, lvlfn=None, clip=None):
        F, G, k = self.F, self.G, self.k
        cx, cy, rx, ry = F(cx + self.ox), F(cy + self.oy), rx * k, ry * k
        pix = {}
        for y in range(math.floor(cy - ry), math.ceil(cy + ry) + 1):
            for x in range(math.floor(cx - rx), math.ceil(cx + rx) + 1):
                nx, ny = (x - cx) / rx, (y - cy) / ry
                r2 = nx * nx + ny * ny
                if r2 <= 1 and (clip is None or clip(G(x), G(y) - self.oy)):
                    pix[(x, y)] = (nx, ny, math.sqrt(1 - r2))
        self._paint(pix, mat, base, amp, cont, lvlfn)
        return pix

    def limb(self, a, b, r0, r1, mat, base, amp=1.6, cont=None, lvlfn=None, clip=None):
        F, G, k = self.F, self.G, self.k
        ax, ay = F(a[0] + self.ox), F(a[1] + self.oy)
        bx, by = F(b[0] + self.ox), F(b[1] + self.oy)
        r0, r1 = r0 * k, r1 * k
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
                if d2 <= 1 and (clip is None or clip(G(x), G(y) - self.oy)):
                    pix[(x, y)] = (ex / r, ey / r, math.sqrt(1 - d2))
        self._paint(pix, mat, base, amp, cont, lvlfn)
        return pix

    def lathe(self, y0, y1, edges, mat, base, amp=1.6, cont=None, lvlfn=None, tilt=0.0):
        """Els contorns de disseny (una parella per fila) s'interpolen entre files."""
        F, G, k = self.F, self.G, self.k
        y0, y1 = math.floor(y0), math.floor(y1)
        pix = {}
        for Y in range(math.floor(F(y0 - 0.5 + self.oy)), math.ceil(F(y1 + 0.5 + self.oy)) + 1):
            yd = G(Y) - self.oy
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
            xl, xr = F(e[0] + self.ox) - k / 2 + 0.5, F(e[1] + self.ox) + k / 2 - 0.5
            mid, half = (xl + xr) / 2, max(0.5, (xr - xl) / 2)
            for x in range(math.ceil(xl - 0.01), math.floor(xr + 0.01) + 1):
                u = max(-1.0, min(1.0, (x - mid) / (half + 0.5)))
                nz = math.sqrt(max(0.0, 1 - u * u - tilt * tilt))
                pix[(x, Y)] = (u, tilt, nz)
        self._paint(pix, mat, base, amp, cont, lvlfn)
        return pix

    def poly(self, pts, mat, base, amp=0.0, cont=None, lvlfn=None, normal=None):
        F, G = self.F, self.G
        pts = [(F(px + self.ox), F(py + self.oy)) for px, py in pts]
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
                    pix[(x, y)] = normal(G(x), G(y) - self.oy) if normal else (0.0, 0.0, 1.0)
        self._paint(pix, mat, base, amp, cont, lvlfn)
        return pix

    def _paint(self, pix, mat, base, amp, cont, lvlfn):
        # lvlfn rep coordenades de disseny (com a 480), però es crida per a cada píxel real
        if lvlfn:
            fn, G = lvlfn, self.G
            lvlfn = lambda x, y: fn(G(x), G(y))  # noqa: E731
        super()._paint(pix, mat, base, amp, cont, lvlfn)

    # píxels de disseny: ocupen la seva zona
    def _zone(self, x, y):
        i, j = int(round(x + self.ox)), int(round(y + self.oy))
        return [(X, Y) for Y in self.span(j) for X in self.span(i) if 0 <= X < self.w and 0 <= Y < self.h]

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
        X, Y = round(self.F(x + self.ox)), round(self.F(y + self.oy))
        if 0 <= X < self.w and 0 <= Y < self.h:
            return self.buf[Y][X]
        return None

    def line(self, x0, y0, x1, y1, mat, lvl):
        """Línia d'un píxel real."""
        F = self.F
        X0, Y0, X1, Y1 = F(x0 + self.ox), F(y0 + self.oy), F(x1 + self.ox), F(y1 + self.oy)
        self.rline(X0, Y0, X1, Y1, mat, lvl)

    # píxels reals (per als detalls dibuixats a la mida nova)
    def rpx(self, X, Y, mat, lvl):
        X, Y = int(round(X)), int(round(Y))
        if 0 <= X < self.w and 0 <= Y < self.h:
            self.buf[Y][X] = (mat, lvl)

    def rget(self, X, Y):
        X, Y = int(round(X)), int(round(Y))
        if 0 <= X < self.w and 0 <= Y < self.h:
            return self.buf[Y][X]
        return None

    def rshade(self, X, Y, d, only=None):
        X, Y = int(round(X)), int(round(Y))
        if 0 <= X < self.w and 0 <= Y < self.h and self.buf[Y][X]:
            m, l = self.buf[Y][X]
            if only is None or m is only or (isinstance(only, (list, tuple)) and m in only):
                self.buf[Y][X] = (m, l + d)

    def rline(self, X0, Y0, X1, Y1, mat, lvl):
        n = max(1, int(math.ceil(max(abs(X1 - X0), abs(Y1 - Y0)))))
        for i in range(n + 1):
            t = i / n
            self.rpx(X0 + (X1 - X0) * t, Y0 + (Y1 - Y0) * t, mat, lvl)

    def rrow(self, X0, X1, Y, d, only=None):
        """Una fila de píxels reals enfosquida o aclarida (plecs, vores)."""
        for X in range(int(round(X0)), int(round(X1)) + 1):
            self.rshade(X, Y, d, only)


class FigK2(FigK):
    """FigK a S× (S = 2): la mateixa figura, amb l'API en píxels de 640 i el buffer a S×.
      - el que té volum (`ell`, `limb`, `lathe`, `poly`) i els píxels de disseny (`px`, `shade`, `erase`, `get`) es
        rasteritzen a la resolució real: vores, ombrejat i contorn d'un píxel real;
      - els detalls píxel a píxel (`rpx`, `rshade`, `rget`, `rline`, `rrow`, i `line`), en coordenades de 640: cada
        un, un bloc S×S. La cara, les ulleres, els auriculars... queden igual que a 640, ara més nets al voltant.
    `F`, `G` i `k` són els de 640 (els ganxos hi compten), menys dins de `_fi`."""

    def __init__(self, w, h):
        super().__init__(w, h)
        self.k640 = self.k
        self.w, self.h = self.w * S, self.h * S
        self.buf = [[None] * self.w for _ in range(self.h)]
        self._fine = 0

    @contextmanager
    def _fi(self):
        self._fine += 1
        self.k = self.k640 * S
        try:
            yield
        finally:
            self._fine -= 1
            if not self._fine:
                self.k = self.k640

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

    def line(self, x0, y0, x1, y1, mat, lvl):
        """Línia d'un píxel de 640 (un bloc S×S de gruix)."""
        F = self.F
        self.rline(F(x0 + self.ox), F(y0 + self.oy), F(x1 + self.ox), F(y1 + self.oy), mat, lvl)

    def _blk(self, X, Y):
        X, Y = int(round(X)), int(round(Y))
        return [(X * S + i, Y * S + j) for j in range(S) for i in range(S)]

    def rpx(self, X, Y, mat, lvl):
        if self._fine:
            return super().rpx(X, Y, mat, lvl)
        for x, y in self._blk(X, Y):
            super().rpx(x, y, mat, lvl)

    def rget(self, X, Y):
        if self._fine:
            return super().rget(X, Y)
        return super().rget(round(X) * S, round(Y) * S)

    def rshade(self, X, Y, d, only=None):
        if self._fine:
            return super().rshade(X, Y, d, only)
        for x, y in self._blk(X, Y):
            super().rshade(x, y, d, only)


def _poke(img, x, y, col, q=None):
    """Un píxel de 640 en una figura ja dibuixada (a S×: un bloc S×S). `q` ('DL'): la figura és en 3/4, i el píxel va
    on l'ha portat el gir (hd.characters._gira: estreta i desplaçada cap on mira)."""
    if q:
        sc = img.width / S / 49
        cx = 24.5 * sc + (sc - 1) / 2
        k, dx = C._q_dx((y - (sc - 1) / 2) / sc, q, x - cx)
        x = round(cx + (x - cx) * k + dx * sc)
        if not (0 <= x * S < img.width and img.getpixel((x * S, y * S))[3]):
            return
    P_ = img.load()
    for j in range(S):
        for i in range(S):
            P_[x * S + i, y * S + j] = col


@contextmanager
def escala(k):
    """Dibuixa les figures a ×k mentre dura (en Ballester, ×4/3×1,14; el nen, ×4/3×0,62)."""
    old = FigK.k_escala
    FigK.k_escala = k
    try:
        yield
    finally:
        FigK.k_escala = old


# ─── La cara, a la mida nova ─────────────────────────────────────────────────

def face_xy(fg, p):
    """(HX, ey): el centre del cap en x i la fila dels ulls, en píxels reals."""
    hx, hy = p.head
    return fg.F(hx + fg.ox), round(fg.F(int(hy + 0.5)))


def front_eyes(fg, p):
    """(lx, rx, ey, nx): el píxel de l'esquerra de cada ull (3 px), la fila dels ulls i la columna del nas."""
    HX, ey = face_xy(fg, p)
    return round(HX - 5.5), round(HX + 2.5), ey, round(HX - 0.5)


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


def _small_front_face(fg, p, spec):
    """Una cara petita (el nen, a ×0,83; les figures de lluny): ulls de 2 píxels, com els de 480. Tancats (`closed`):
    només la parpella, a la fila de l'iris; mirant a un costat (`mira`): l'iris dels dos ulls, a aquella banda."""
    S = spec['skin']
    HX, ey = face_xy(fg, p)
    eye, iris, brow = spec.get('eye', (34, 22, 30)), spec.get('iris', (70, 50, 40)), spec.get('brow', (40, 24, 28))
    lx, rx, nx = round(HX - 3.5), round(HX + 1.5), round(HX - 0.5)
    for x0, inner in ((lx, lx + 1), (rx, rx)):
        if spec.get('closed'):
            fg.rpx(x0, ey, eye, 0); fg.rpx(x0 + 1, ey, eye, 0)
            continue
        if spec.get('mira'):
            inner = x0 if spec['mira'] < 0 else x0 + 1
        fg.rpx(x0, ey - 1, eye, 0); fg.rpx(x0 + 1, ey - 1, eye, 0)
        fg.rpx(inner, ey, iris, 0)
        fg.rpx(x0 + 1 if inner == x0 else x0, ey, C.EYE_W, 0)
    fg.rpx(lx, ey - 3, brow, 0); fg.rpx(lx + 1, ey - 3, brow, 0)
    fg.rpx(rx, ey - 3, brow, 0); fg.rpx(rx + 1, ey - 3, brow, 0)
    fg.rshade(nx, ey + 2, -0.9, S); fg.rshade(nx - 1, ey + 1, +0.5, S)
    my, lip = ey + 4, spec.get('lip', C.LIP)
    if p.talk:
        for x in (nx - 1, nx, nx + 1):
            fg.rpx(x, my, C.MOUTH, 0)
        fg.rpx(nx, my + 1, C.MOUTH, 0)
    else:
        fg.rpx(nx - 1, my, lip, 0); fg.rpx(nx, my, mix(lip, C.MOUTH, 0.5), 0); fg.rpx(nx + 1, my, lip, 0)


def front_face(fg, p, spec):
    if fg.k < 1:
        return _small_front_face(fg, p, spec)
    S = spec['skin']
    HX, ey = face_xy(fg, p)
    brow = spec.get('brow', (40, 24, 28))
    eye = spec.get('eye', (34, 22, 30))
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
    HX, ey = face_xy(fg, p)
    eye = spec.get('eye', (34, 22, 30))
    iris = spec.get('iris', (70, 50, 40))
    brow = spec.get('brow', (40, 24, 28))
    small = fg.k < 1
    ex = round(HX - (3.5 if small else 5.5))             # l'ull, de perfil: 2 px d'ample
    if spec.get('closed'):
        fg.rpx(ex, ey, eye, 0); fg.rpx(ex + 1, ey, eye, 0)
    elif small:
        fg.rpx(ex, ey - 1, eye, 0); fg.rpx(ex + 1, ey - 1, eye, 0)
        fg.rpx(ex, ey, iris, 0); fg.rpx(ex - 1, ey, C.EYE_W, 0)
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
    if small:
        fg.rpx(ex - 1, ey - 3, brow, 0); fg.rpx(ex, ey - 3, brow, 0)
    else:
        by = ey - 4 + round(spec.get('brow_dy', 0) * K)
        for dx, dy in ((-2, 0), (-1, 0), (0, 0), (1, 1)):
            fg.rpx(ex + dx, by + dy, brow, 0)
    # orella (amb el forat)
    oxd, eyd = int(hx + 2.5) + 0.5, int(hy + 0.5)
    fg.ell(oxd, eyd + 2, 1.6, 2.2, S, 2.6, amp=1.2)
    fg.rshade(fg.F(oxd), fg.F(eyd + 2) - 0.5, -1.2, S); fg.rshade(fg.F(oxd), fg.F(eyd + 2) + 0.5, -0.9, S)
    if spec.get('blush'):
        fg.rshade(ex + 2, ey + 3, -0.4, S); fg.rshade(ex + 3, ey + 3, -0.4, S)
    # boca
    lip = spec.get('lip', C.LIP)
    if small:
        my, mx = ey + 4, round(HX - 5.0)
        fg.rpx(mx, my, C.MOUTH if p.talk else lip, 0); fg.rpx(mx + 1, my, C.MOUTH if p.talk else mix(lip, C.MOUTH, 0.5), 0)
        if p.talk:
            fg.rpx(mx + 1, my + 1, C.MOUTH, 0)
        return
    my = ey + 7
    mx = round(HX - 8.0)
    if p.talk:
        fg.rpx(mx, my, C.MOUTH, 0); fg.rpx(mx + 1, my, C.MOUTH, 0); fg.rpx(mx + 2, my, lip, 0)
        fg.rpx(mx + 1, my + 1, C.MOUTH, 0); fg.rpx(mx + 2, my + 1, lip, 0)
        fg.erase(fg.G(mx - 1), fg.G(my))
    else:
        fg.rpx(mx, my, lip, 0); fg.rpx(mx + 1, my, mix(lip, C.MOUTH, 0.5), 0); fg.rpx(mx + 2, my, mix(lip, C.MOUTH, 0.3), 0)


def side_mouth(fg, p):
    """(mx, my): el primer píxel de la boca de perfil."""
    HX, ey = face_xy(fg, p)
    return round(HX - 8.0), ey + 7


def _brow_px(fg, p, spec):
    """Els píxels de les celles que hi posa la cara (per esborrar-les si una expressió les canvia)."""
    lx, rx, ey, _ = front_eyes(fg, p)
    by = ey - 4 + round(spec.get('brow_dy', 0) * K)
    if p.f == 'D':
        return by, [(lx - 1, by + 1), (lx, by), (lx + 1, by), (lx + 2, by), (rx, by), (rx + 1, by), (rx + 2, by), (rx + 3, by + 1)]
    ex = lx
    return by, [(ex - 2, by), (ex - 1, by), (ex, by), (ex + 1, by + 1)]


# ─── Els ganxos de hd/personatges.py redibuixats a la mida nova ─────────────

def _ganxos(P):
    """Les versions de 640 dels ganxos i funcions de hd/personatges.py: {nom: funció}."""
    def rx_(fg, u):
        return fg.F(u + fg.ox)

    # --- Iri ---
    def iri_hoodie(fg, p, spec):
        """La dessuadora: butxaca de cangur, cordons blancs amb les puntes, la cintura elàstica i la caputxa."""
        b = p.bob
        hx = 24.5
        O = P.HOODIE
        F = fg.F
        if p.f == 'D':
            y0, y1 = round(F(38 + b)), round(F(46 + b))
            xl, xr = round(F(hx - 6)), round(F(hx + 6))
            fg.rrow(xl, xr, y0, -1.0, O)                                         # la butxaca: la vora de dalt
            fg.rrow(xl + 1, xr - 1, y0 + 1, +0.4, O)
            for y in range(y0, y1):
                fg.rshade(xl, y, -0.9, O); fg.rshade(xr, y, -0.9, O)
                fg.rshade(xl + 1, y, +0.3, O)
            for X in (round(F(hx - 3)), round(F(hx + 3))):                       # els cordons, amb la punta
                for Y in range(round(F(28 + b)), round(F(30 + b)) + 1):
                    fg.rpx(X, Y, P.CORD, 1.4)
                fg.rpx(X, round(F(30 + b)) + 1, P.CORD, 0.4)
            fg.rrow(F(hx - 9), F(hx + 9), y1, -1.0, O)                           # la cintura elàstica
            fg.rrow(F(hx - 9), F(hx + 9), y1 + 1, +0.4, O)
            for X in range(round(F(hx - 9)), round(F(hx + 9)) + 1, 2):
                fg.rshade(X, y1 + 2, -0.3, O)
            fg.shade(hx - 7, 33 + b, -0.6, O)
            fg.shade(hx + 7, 34 + b, -0.6, O)
        elif p.f == 'U':
            fg.ell(hx, 31 + b, 6.0, 4.6, O, 2.4, amp=1.6, cont=(0.2, 1.0))      # la caputxa caiguda
            fg.rrow(F(hx - 4), F(hx + 4), round(F(33 + b)), -0.8, O)
            fg.rrow(F(hx - 3), F(hx + 3), round(F(33 + b)) + 1, +0.3, O)
            fg.rrow(F(hx - 9), F(hx + 9), round(F(46 + b)), -1.0, O)
            fg.rrow(F(hx - 9), F(hx + 9), round(F(46 + b)) + 1, +0.4, O)
        else:
            fg.ell(29.0, 30 + b, 3.6, 4.0, O, 2.4, amp=1.6, cont=(0.2, 1.0))    # la caputxa al clatell
            X = round(F(21.0))
            for Y in range(round(F(29 + b)), round(F(35 + b)) + 1):
                fg.rpx(X, Y, P.CORD, 2 if Y < F(33 + b) else 1)
            fg.rpx(X, round(F(35 + b)) + 1, P.CORD, 0.4)
            fg.rrow(F(19), F(32), round(F(46 + b)), -1.0, O)
            fg.rrow(F(19), F(32), round(F(46 + b)) + 1, +0.4, O)

    def iri_phones(fg, p, spec):
        """Els auriculars: la diadema (tres píxels reals de gruix, amb la llum a dalt) i les copes."""
        hx, hy = p.head
        PH = P.PHONES
        if p.f in ('D', 'U'):
            CX, CY = rx_(fg, hx), fg.F(hy - 0.5)
            RX, RY = 8.6 * fg.k, 9.2 * fg.k
            for i in range(121):
                a = math.pi * i / 120
                for d, lvl in ((1, 2.6), (0, 1.8), (-1, 1.0)):
                    fg.rpx(CX - math.cos(a) * (RX + d * 0.4), CY - math.sin(a) * (RY + d), PH, lvl + 0.4 * math.sin(a))
            for sx in (-8.4, 8.4):
                fg.ell(hx + sx, hy + 1.2, 2.4, 3.4, PH, 2.2, amp=1.6, cont=(0.2, 1.0))
                fg.ell(hx + sx + (0.6 if sx < 0 else -0.6), hy + 1.2, 1.2, 2.4, P.PHONES_RED, 2.6, amp=1.4)
                X = round(rx_(fg, hx + sx))                                       # la unió de la diadema amb la copa
                fg.rpx(X, round(fg.F(hy - 2.6)), PH, 3.2)
        else:
            CX, CY = rx_(fg, hx + 1.4), fg.F(hy - 0.5)
            for i in range(61):
                a = math.pi * (0.2 + 0.6 * i / 60)
                for d, lvl in ((1, 2.6), (0, 1.8), (-1, 1.0)):
                    fg.rpx(CX + math.cos(a) * 2.5 * fg.k, CY - math.sin(a) * (9.2 * fg.k + d), PH, lvl)
            fg.ell(hx + 1.6, hy + 1.2, 3.0, 3.8, PH, 2.2, amp=1.6, cont=(0.2, 1.0))
            fg.ell(hx + 1.2, hy + 1.2, 1.8, 2.8, P.PHONES_RED, 2.6, amp=1.4)
            fg.rshade(rx_(fg, hx + 0.6), fg.F(hy - 0.6), +1.2, P.PHONES_RED)

    # --- Vet ---
    def vet_glasses(fg, p, spec):
        """Les ulleres de pasta de la cafeteria de l'aeroport: una vora gruixuda al voltant de cada ull."""
        FR = P.FRAME
        if fg.k < 1:
            return _vet_glasses_small(fg, p, FR)
        lx, rx, ey, _ = front_eyes(fg, p)
        if p.f == 'D':
            for x0 in (lx, rx):
                for x in range(x0 - 1, x0 + 4):
                    fg.rpx(x, ey - 2, FR, 2.2)
                    fg.rpx(x, ey + 2, FR, 1.2)
                for y in range(ey - 1, ey + 2):
                    fg.rpx(x0 - 1, y, FR, 1.6)
                    fg.rpx(x0 + 3, y, FR, 1.4)
                fg.rpx(x0 - 2, ey - 2, FR, 1.8)                                  # la pasta, que sobresurt als cantons
                fg.rpx(x0 + 4, ey - 2, FR, 1.8)
                fg.rpx(x0, ey - 1, FR, 3.0)                                      # el reflex
            for x in range(lx + 4, rx - 1):
                fg.rpx(x, ey - 1, FR, 1.4)                                       # el pont
        elif p.f == 'L':
            ex = lx
            for x in range(ex - 2, ex + 3):
                fg.rpx(x, ey - 2, FR, 2.2)
                fg.rpx(x, ey + 2, FR, 1.2)
            for y in range(ey - 1, ey + 2):
                fg.rpx(ex - 2, y, FR, 1.6)
                fg.rpx(ex + 2, y, FR, 1.6)
            hx, hy = p.head
            fg.rline(ex + 3, ey - 1, rx_(fg, hx + 2.5), ey - 1, FR, 1.2)       # la patilla, fins a l'orella

    def _vet_glasses_small(fg, p, FR):
        """Les mateixes ulleres a la cara petita (ulls de 2 píxels, vegeu _small_front_face): la vora al voltant de
        cada ull, el pont i, de perfil, la patilla."""
        HX, ey = face_xy(fg, p)
        if p.f == 'D':
            lx, rx = round(HX - 3.5), round(HX + 1.5)
            for x0 in (lx, rx):
                for x in range(x0 - 1, x0 + 3):
                    fg.rpx(x, ey - 2, FR, 2.2)
                    fg.rpx(x, ey + 1, FR, 1.2)
                for y in (ey - 1, ey):
                    fg.rpx(x0 - 1, y, FR, 1.6)
                    fg.rpx(x0 + 2, y, FR, 1.4)
            for x in range(lx + 3, rx - 1):
                fg.rpx(x, ey - 1, FR, 1.4)                                       # el pont
        elif p.f == 'L':
            ex = round(HX - 3.5)
            for x in range(ex - 2, ex + 3):
                fg.rpx(x, ey - 2, FR, 2.2)
                fg.rpx(x, ey + 1, FR, 1.2)
            for y in (ey - 1, ey):
                fg.rpx(ex - 2, y, FR, 1.6)
                fg.rpx(ex + 2, y, FR, 1.6)
            hx, hy = p.head
            fg.rline(ex + 3, ey - 1, rx_(fg, hx + 2.5), ey - 1, FR, 1.2)       # la patilla, fins a l'orella

    def plaid(fg, p, spec):
        """Quadres: línies fosques cada 5 píxels reals a tot el que sigui de franel·la."""
        for y in range(fg.h):
            for x in range(fg.w):
                c = fg.buf[y][x]
                X, Y = x // S, y // S                                            # en píxels de 640
                if c and c[0] is P.FLANNEL and (X % 5 == 0 or Y % 5 == 1):
                    fg.buf[y][x] = (P.FLANNEL_DARK, c[1] - (0.6 if (X % 5 == 0 and Y % 5 == 1) else 0))

    # --- Secundaris ---
    def glasses(fg, p, spec):
        """Les ulleres d'en Marcel: muntura d'acer d'un píxel, vidres que fan llum i els ulls que s'hi veuen."""
        lx, rx, ey, _ = front_eyes(fg, p)
        ST, CR = C.STEELB, C.CREAM
        if p.f == 'D':
            for x0 in (lx, rx):
                for x in range(x0, x0 + 3):
                    fg.rpx(x, ey - 2, ST, 2.0)
                    fg.rpx(x, ey + 2, ST, 1.4)
                for y in range(ey - 1, ey + 2):
                    fg.rpx(x0 - 1, y, ST, 1.8)
                    fg.rpx(x0 + 3, y, ST, 1.6)
                fg.rpx(x0, ey - 1, CR, 4.6)                                      # el reflex del vidre
                fg.rpx(x0 + 2, ey + 1, CR, 3.4)
            for x in range(lx + 4, rx - 1):
                fg.rpx(x, ey - 1, ST, 2.2)                                       # el pont
        elif p.f == 'L':
            ex = lx
            for x in range(ex - 1, ex + 2):
                fg.rpx(x, ey - 2, ST, 2.0)
                fg.rpx(x, ey + 2, ST, 1.4)
            for y in range(ey - 1, ey + 2):
                fg.rpx(ex - 2, y, ST, 1.8)
                fg.rpx(ex + 2, y, ST, 1.6)
            fg.rpx(ex - 1, ey - 1, CR, 4.6)
            hx, hy = p.head
            fg.rline(ex + 3, ey - 1, rx_(fg, hx + 2.5), ey, ST, 1.6)

    def brow_raised(fg, p, spec):
        """Una cella arquejada (la de la dreta de la imatge): ben amunt, i l'ull, obert de cop."""
        lx, rx, ey, _ = front_eyes(fg, p)
        brow, S = (120, 116, 126), spec['skin']
        lid, iris = (34, 22, 30), (70, 90, 120)
        by, old = _brow_px(fg, p, spec)
        if p.f == 'D':
            for (x, y) in old[4:]:
                fg.rpx(x, y, S, 3.0)
            for x in range(rx, rx + 3):
                fg.rpx(x, ey - 2, S, 3.0)
            for dx, dy in ((-1, -5), (0, -6), (1, -7), (2, -7), (3, -6)):
                fg.rpx(rx + dx, ey + dy, brow, 0)
            for i in range(3):
                fg.rpx(rx + i, ey - 2, lid, 0)
            for j, row in enumerate(((C.EYE_W, iris, C.EYE_W), (C.EYE_W, mix(iris, lid, 0.6), C.EYE_W), (C.EYE_W, iris, C.EYE_W))):
                for i, c in enumerate(row):
                    fg.rpx(rx + i, ey - 1 + j, c, 0)
        elif p.f == 'L':
            ex = lx
            for (x, y) in old:
                fg.rpx(x, y, S, 3.0)
            for dx, dy in ((-2, -5), (-1, -6), (0, -6), (1, -5)):
                fg.rpx(ex + dx, ey + dy, brow, 0)
            for i in range(3):
                fg.rpx(ex - 1 + i, ey - 2, lid, 0)
            fg.rpx(ex - 1, ey - 1, C.EYE_W, 0); fg.rpx(ex, ey - 1, iris, 0)
            fg.rpx(ex - 1, ey, C.EYE_W, 0); fg.rpx(ex, ey, iris, 0); fg.rpx(ex + 1, ey, C.EYE_W, 0)

    def wide_smile(fg, p, spec):
        """El somriure del Director: massa ample, amb les dents de dalt i les de baix."""
        lx, rx, ey, nx = front_eyes(fg, p)
        my = ey + 7
        MO, W = C.MOUTH, C.EYE_W
        if p.f == 'D':
            for x in range(nx - 4, nx + 4):
                fg.rpx(x, my, W if nx - 4 < x < nx + 3 else MO, 0)
            fg.rpx(nx - 5, my - 1, MO, 0); fg.rpx(nx + 4, my - 1, MO, 0)           # les comissures, amunt
            for x in range(nx - 3, nx + 3):
                fg.rpx(x, my + 1, MO, 0)
            for x in range(nx - 2, nx + 2):
                fg.rpx(x, my + 1, mix(W, MO, 0.35), 0)                          # les dents de baix
                fg.rpx(x, my + 2, MO, 0)
            fg.rpx(nx - 1, my, mix(W, MO, 0.2), 0)                              # la ratlla entre les dents
            fg.rshade(nx - 6, my - 1, -0.6, spec['skin']); fg.rshade(nx + 5, my - 1, -0.6, spec['skin'])
        elif p.f == 'L':
            mx, my = side_mouth(fg, p)
            for x in range(mx, mx + 3):
                fg.rpx(x, my, W, 0)
                fg.rpx(x, my + 1, MO, 0)
            fg.rpx(mx + 3, my - 1, MO, 0); fg.rpx(mx + 3, my, MO, 0)

    def frown(fg, p, spec):
        """Celles avall cap al nas (mal humor) i la boca tensa."""
        lx, rx, ey, nx = front_eyes(fg, p)
        brow, S = spec.get('brow', (40, 24, 28)), spec['skin']
        by, old = _brow_px(fg, p, spec)
        for (x, y) in old:
            fg.rpx(x, y, S, 3.0)
        if p.f == 'D':
            for x, y in ((lx - 1, by - 1), (lx, by - 1), (lx + 1, by), (lx + 2, by + 1),
                         (rx, by + 1), (rx + 1, by), (rx + 2, by - 1), (rx + 3, by - 1)):
                fg.rpx(x, y, brow, 0)
            fg.rshade(nx - 1, by + 1, -0.5, S); fg.rshade(nx, by + 1, -0.5, S)      # l'arruga del mig
            if not p.talk:
                for x in range(nx - 2, nx + 2):
                    fg.rpx(x, ey + 7, C.MOUTH, 0)
                fg.rshade(nx - 3, ey + 8, -0.5, S); fg.rshade(nx + 2, ey + 8, -0.5, S)
        elif p.f == 'L':
            ex = lx
            for x, y in ((ex - 2, by + 1), (ex - 1, by + 1), (ex, by), (ex + 1, by - 1)):
                fg.rpx(x, y, brow, 0)

    def smile(fg, p, spec):
        lx, rx, ey, nx = front_eyes(fg, p)
        my = ey + 7
        if p.f == 'D' and not p.talk:
            fg.rpx(nx - 3, my - 1, C.MOUTH, 0); fg.rpx(nx + 2, my - 1, C.MOUTH, 0)
            for x in range(nx - 2, nx + 2):
                fg.rpx(x, my, C.MOUTH, 0)
            fg.rshade(nx - 1, my + 1, +0.4, spec['skin']); fg.rshade(nx, my + 1, +0.4, spec['skin'])
        elif p.f == 'L' and not p.talk:
            mx, my = side_mouth(fg, p)
            for x in range(mx, mx + 3):
                fg.rpx(x, my, C.MOUTH, 0)
            fg.rpx(mx + 3, my - 1, C.MOUTH, 0)

    def tired_mouth(fg, p, spec):
        """Els plecs del costat de la boca (vint anys de secretària)."""
        if p.f != 'D':
            return
        lx, rx, ey, nx = front_eyes(fg, p)
        my, S = ey + 7, spec['skin']
        for x, y, d in ((nx - 4, my - 2, -0.4), (nx - 4, my - 1, -0.6), (nx - 4, my, -0.5), (nx - 3, my + 1, -0.4),
                        (nx + 3, my - 2, -0.5), (nx + 3, my - 1, -0.7), (nx + 3, my, -0.6), (nx + 2, my + 1, -0.4)):
            fg.rshade(x, y, d, S)

    def chain(fg, pts, lvl):
        """Una cadeneta de punts reals (un sí, un no) per sobre del que ja hi ha dibuixat: no penja mai a l'aire."""
        k = 0
        pts = [(rx_(fg, x), fg.F(y)) for x, y in pts]
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            n = int(max(abs(bx - ax), abs(by - ay))) + 1
            for i in range(n):
                x, y = ax + (bx - ax) * i / n, ay + (by - ay) * i / n
                if k % 2 == 0 and fg.rget(x, y):
                    fg.rpx(x, y, P.CHAIN_FINE, lvl + (0.8 if k % 4 == 0 else 0))
                k += 1

    def reading_glasses(fg, p, spec):
        """Ulleres de lectura de mitja lluna a la punta del nas (els ulls hi miren per sobre) i la cadeneta."""
        hx, hy = p.head
        lx, rx, ey, nx = front_eyes(fg, p)
        S, SP = spec['skin'], P.SPECS
        if p.f == 'D':
            for x0 in (lx, rx):
                for x in range(x0 - 1, x0 + 4):
                    fg.rpx(x, ey + 3, SP, 2.6)                                   # la vora de dalt
                fg.rpx(x0 - 1, ey + 4, SP, 1.4); fg.rpx(x0 + 3, ey + 4, SP, 1.4)
                for x in range(x0, x0 + 3):
                    fg.rshade(x, ey + 4, 0.6, S)                                 # el vidre
                    fg.rpx(x, ey + 5, SP, 1.2)                                   # la vora de baix
                fg.rshade(x0, ey + 4, 0.6, S)
            for x in range(lx + 4, rx - 1):
                fg.rpx(x, ey + 3, SP, 1.8)                                       # el pont, al nas
            for sx in (-1, 1):
                chain(fg, [(hx + sx * 6.2, hy + 6), (hx + sx * 5.6, hy + 10), (hx + sx * 4.2, 28 + p.bob)], 1.8)
        elif p.f == 'L':
            ex = lx
            for x in range(ex - 3, ex + 1):
                fg.rpx(x, ey + 3, SP, 2.4)
            fg.rpx(ex - 3, ey + 4, SP, 2.0); fg.rpx(ex - 2, ey + 5, SP, 1.4); fg.rpx(ex - 1, ey + 5, SP, 1.4)
            X1 = rx_(fg, hx + 2)
            for x in range(ex + 1, round(X1) + 1):
                fg.rpx(x, ey + 3 - (x - ex) * 0.2, SP, 1.8)                     # la patilla
            chain(fg, [(hx + 2, int(hy + 0.5) + 1), (hx + 2.5, hy + 8), (hx + 0.5, 29 + p.bob)], 2.2)
        elif p.f == 'U':
            chain(fg, [(hx - 5.4, hy + 7.6), (hx, hy + 9.8), (hx + 5.4, hy + 7.6)], 2.2)   # pel clatell

    def headset(fg, p, spec):
        """Els auriculars de diadema de recepció: la diadema prima, un auricular i el micro davant la boca."""
        hx, hy = p.head
        PH = P.PHONES
        if p.f in ('D', 'U'):
            CX, CY = rx_(fg, hx), fg.F(hy - 0.5)
            for i in range(91):
                a = math.pi * i / 90
                fg.rpx(CX - math.cos(a) * 7.6 * fg.k, CY - math.sin(a) * 8.6 * fg.k, PH, 2.8 if i % 9 else 1.6)
                fg.rpx(CX - math.cos(a) * (7.6 * fg.k - 0.6), CY - math.sin(a) * (8.6 * fg.k - 1), PH, 1.4)
            ex = hx - 7.2 if p.f == 'D' else hx + 7.2
            fg.ell(ex, hy + 1.6, 1.6, 2.2, PH, 2.6, amp=1.2, cont=(0.2, 0.8))
            if p.f == 'D':
                lx, rx, ey, nx = front_eyes(fg, p)
                fg.rline(rx_(fg, ex + 0.6), fg.F(hy + 3.6), nx - 4, ey + 6, PH, 2.0)      # el micro
                fg.rpx(nx - 4, ey + 6, PH, 3.4); fg.rpx(nx - 3, ey + 6, PH, 3.0)
        elif p.f == 'L':
            CX, CY = rx_(fg, hx + 2.4), fg.F(hy - 0.5)
            for i in range(61):
                a = math.pi * i / 60
                fg.rpx(CX - 1.6 * fg.k * math.cos(a), CY - 8.8 * fg.k * math.sin(a), PH, 2.8 if i % 9 else 1.6)
            fg.ell(hx + 3.2, hy + 2.0, 1.8, 2.4, PH, 2.6, amp=1.2, cont=(0.2, 0.8))
            mx, my = side_mouth(fg, p)
            fg.rline(rx_(fg, hx + 1.8), fg.F(hy + 4.0), mx + 1, my - 1, PH, 2.0)
            fg.rpx(mx + 1, my - 1, PH, 3.4); fg.rpx(mx, my - 1, PH, 3.0)

    def key_collar(fg, p, spec):
        """El collaret: una cadena de baules de llautó i la clau grossa del Llibre Major al pit."""
        b = p.bob
        hx = 24.5
        CH = P.CHAIN
        if p.f == 'D':
            for t in range(0, 25):
                a = math.pi * t / 24
                fg.rpx(rx_(fg, hx - 5.5 * math.cos(a)), fg.F(28 + b + 7 * math.sin(a)), CH, 2.8 if t % 2 else 1.6)
            kx, ky = hx, 36 + b
            fg.ell(kx, ky, 1.8, 1.8, CH, 2.8, amp=1.2)
            KX, KY = round(rx_(fg, kx)), round(fg.F(ky))
            fg.rpx(KX, KY, CH, 0.4); fg.rpx(KX, KY - 1, CH, 0.8)                  # l'ull de la clau
            for Y in range(KY + 3, KY + 10):
                fg.rpx(KX, Y, CH, 2.8)                                           # la tija
                fg.rpx(KX - 1, Y, CH, 1.6)
            for Y, w in ((KY + 7, 2), (KY + 9, 2), (KY + 8, 1)):                 # les dents
                for i in range(1, w + 1):
                    fg.rpx(KX + i, Y, CH, 2.2)
        elif p.f == 'L':
            X = round(rx_(fg, 19.0))
            for Y in range(round(fg.F(29 + b)), round(fg.F(36 + b)) + 1):
                fg.rpx(X, Y, CH, 2.6 if Y % 2 else 1.4)
            fg.ell(18.5, 37 + b, 1.4, 1.6, CH, 2.8, amp=1.0)

    return {
        'iri_hoodie': iri_hoodie, 'iri_phones': iri_phones, 'vet_glasses': vet_glasses, 'plaid': plaid,
        'glasses': glasses, 'brow_raised': brow_raised, 'wide_smile': wide_smile, 'frown': frown, 'smile': smile,
        'tired_mouth': tired_mouth, 'reading_glasses': reading_glasses, 'headset': headset,
        'key_collar': key_collar,
    }


# ─── Estampats a la mida nova ────────────────────────────────────────────────

# «</>» de 15×7
LOGO = tuple((x, y) for y in range(7) for x in (3 - min(y, 6 - y), 11 + min(y, 6 - y), round(9 - y * 0.5)))
SKULL = ('..XXXXX..', '.XXXXXXX.', 'XXXXXXXXX', 'X..XXX..X', 'X..X.X..X', 'XXXX.XXXX', '.XXXXXXX.', '.X.X.X.X.')
ALIEN = ('..XXXXX..', '.XXXXXXX.', 'XXXXXXXXX', 'X...X...X', 'XX..X..XX', '.XXXXXXX.', '..XXXXX..', '...XXX...',
         '....X....')
BAND = ('XX..X..X..XX', 'X...X..X...X', 'X...XXXX...X', 'X...X..X...X', 'XX..X..X..XX')
PATCH_A = ('XXXX', 'X..X', 'X..X', 'XXXX')
PATCH_B = ('..X..', '..X..', 'XXXXX', '..X..', '..X..')
STAMPS = {'SKULL': SKULL, 'ALIEN': ALIEN, 'BAND': BAND, 'PATCH_A': PATCH_A, 'PATCH_B': PATCH_B}


def _stamp_at(img, pat, pat480, x0, y0, col, q=None):
    """Posa l'estampat de 640 on hi havia el de 480 (amb el mateix centre)."""
    w, h = len(pat480[0]), len(pat480)
    X0 = round(f(x0 + (w - 1) / 2) - (len(pat[0]) - 1) / 2)
    Y0 = round(f(y0 + (h - 1) / 2) - (len(pat) - 1) / 2)
    for dy, row in enumerate(pat):
        for dx, ch in enumerate(row):
            if ch == 'X':
                _poke(img, X0 + dx, Y0 + dy, col, q)


def _stamp_petit(img, pat480, x0, y0, col, k, q=None):
    """L'estampat de 480 en una figura dibuixada a ×k < 1: cada píxel de disseny, al píxel real on cau."""
    for dy, row in enumerate(pat480):
        for dx, ch in enumerate(row):
            if ch == 'X':
                _poke(img, round((x0 + dx + 0.5) * k - 0.5), round((y0 + dy + 0.5) * k - 0.5), col, q)


# ─── En Diu, a la mida nova ──────────────────────────────────────────────────

def _diu(P):
    GW, GH = round(P.GW * K), round(P.GH * K)       # 40×35
    CAT, CAT_WHITE, CAT_EYE = P.CAT, P.CAT_WHITE, P.CAT_EYE

    def diu(cua=0, parpelleja=False):
        """Assegut de tres quarts, tigrat i amb el pitet blanc. Fotograma de 40×35."""
        fg = C.Fig(P.GW, P.GH)
        tx = [24, 26, 27, 26][cua % 4]
        fg.limb((19, 22), (tx, 14), 1.4, 1.2, CAT, 2.2, cont=(0.2, 0.8),
                lvlfn=lambda x, y: -0.7 if int(y * 1.5) % 3 == 0 else 0)            # la cua, anellada
        fg.limb((tx, 14), (tx - 1, 10), 1.2, 1.1, CAT, 2.4, cont=(0.2, 0.8))
        fg.ell(14, 18, 7.5, 6.5, CAT, 2.6, amp=1.6, cont=(0.2, 1.0),
               lvlfn=lambda x, y: -0.8 if (int(x * 1.33) + int(y * 1.33) // 2) % 5 == 0 else 0)
        fg.ell(12, 19, 3.2, 4.4, CAT_WHITE, 2.8, amp=1.4)
        fg.ell(10, 24, 2.4, 1.4, CAT_WHITE, 2.8, amp=1.2)
        fg.ell(15, 24, 2.4, 1.4, CAT_WHITE, 2.4, amp=1.2)
        for X in (round(fg.F(9)), round(fg.F(10.5)), round(fg.F(14)), round(fg.F(15.5))):   # els dits
            fg.rshade(X, round(fg.F(24.6)), -1.0, CAT_WHITE)
        fg.ell(12, 9, 5.6, 5.0, CAT, 2.8, amp=1.6, cont=(0.2, 1.0),
               lvlfn=lambda x, y: -0.8 if 4.6 < y < 6.6 and int(x * 1.33) % 4 == 0 else 0)
        fg.poly([(7, 6), (8, 1), (11, 4)], CAT, 2.6)
        fg.poly([(17, 6), (16, 1), (13, 4)], CAT, 2.2)
        fg.poly([(8, 5), (8.4, 2.6), (10, 4.2)], P.M((90, 40, 50), (150, 80, 90), (200, 120, 128)), 1.4)   # l'interior de l'orella
        fg.ell(12, 11.5, 2.4, 1.6, CAT_WHITE, 3.0, amp=1.0)
        for ex in (9.5, 14.5):
            EX, EY = round(fg.F(ex)), round(fg.F(9))
            if parpelleja:
                for X in range(EX - 2, EX + 2):
                    fg.rpx(X, EY + (1 if X in (EX - 2, EX + 1) else 0) - 0, CAT, 0)
            else:
                fg.ell(ex, 9, 1.4, 1.3, CAT_EYE, 2.6, amp=1.0)
                for Y in (EY - 1, EY, EY + 1):                                 # la pupil·la, una escletxa
                    fg.rpx(EX, Y, CAT, 0)
                fg.rpx(EX - 1, EY - 1, CAT_EYE, 3.6)                            # la lluentor
        NX, NY = round(fg.F(12)), round(fg.F(11))
        fg.rpx(NX, NY, (190, 110, 120), 0); fg.rpx(NX - 1, NY, (210, 130, 140), 0)
        fg.rpx(NX - 1, NY + 2, CAT, 1.0); fg.rpx(NX - 2, NY + 1, CAT, 1.4)       # la boca
        fg.rpx(NX, NY + 2, CAT, 1.0); fg.rpx(NX + 1, NY + 1, CAT, 1.4)
        return fg.render()

    def zzz(img, k):
        """Una «z» que puja per sobre del cap d'en Diu quan dorm (k: fotograma, 0-3)."""
        x0, y0 = 25 + (k % 2), 4 - round(k * K)
        if y0 < 0:
            return img
        for dx, dy in ((0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (3, 1), (2, 2), (1, 3), (0, 4), (1, 4), (2, 4), (3, 4), (4, 4)):
            x, y = x0 + dx, y0 + dy
            if 0 <= x < img.width // S and 0 <= y < img.height // S:
                _poke(img, x, y, (226, 220, 236, 255))
        return img

    def caixa_sola():
        """La caixa de cartró, sola (al fotograma d'assegut: es posa davant del gat)."""
        fg = C.Fig(P.GW, P.GH)
        BOX = P.M((40, 24, 14), (90, 60, 30), (146, 102, 58), (184, 136, 80), (216, 172, 108))
        fg.poly([(2, 14), (26, 14), (26, 25), (2, 25)], BOX, 2.6, cont=(0.2, 0.8))
        Y0 = round(fg.F(14))
        fg.rrow(fg.F(2), fg.F(26), Y0, +0.8, BOX)                            # el cantell de dalt
        fg.rrow(fg.F(2), fg.F(26), Y0 + 1, -0.6, BOX)
        for X in range(round(fg.F(12)), round(fg.F(16)) + 1):                # la cinta d'embalar
            for Y in range(Y0, round(fg.F(25))):
                fg.rshade(X, Y, +0.6, BOX)
        return fg.render()

    def diu_estat(estat, cua=0, dorm=False):
        """En Diu dins la caixa, amb l'auricular o davant la pizza; `dorm`: dorm (ulls tancats, cua quieta, zzz)."""
        base = diu(cua=0 if dorm else cua, parpelleja=dorm)
        if dorm and estat is None:
            return zzz(base, cua)
        fg = C.Fig(P.GW, P.GH)
        if estat == 'caixa':
            out = Image.new('RGBA', (GW * S, GH * S), (0, 0, 0, 0))
            out.alpha_composite(base, (0, -5 * S))
            out.alpha_composite(caixa_sola())
            return zzz(out, cua) if dorm else out
        if estat == 'auricular':
            # els auriculars de diadema de l'Iri, entre les potes: la diadema negra i les dues copes vermelles
            for i in range(60):
                a = math.pi * i / 59
                for d, lvl in ((0, 2.6), (1, 1.4)):
                    fg.rpx(fg.F(13) - (5.5 * K - d * 0.5) * math.cos(a), fg.F(22) - (4.0 * K - d) * math.sin(a), P.PHONES, lvl)
            for cx in (7.5, 18.5):
                fg.ell(cx, 23, 1.8, 2.4, P.PHONES_RED, 2.6, amp=1.4)
        if estat == 'pizza':
            fg.ell(22, 23, 6.0, 2.2, P.M((70, 30, 14), (150, 80, 30), (210, 130, 50), (240, 190, 90)), 2.8, amp=1.0)
            for X, Y in ((25, 30), (30, 31), (34, 30), (28, 29)):                # el tomàquet i el formatge
                fg.rpx(X, Y, (170, 40, 30), 0)
            fg.rpx(32, 29, (250, 220, 140), 0)
        base.alpha_composite(fg.render())
        return zzz(base, cua) if dorm else base

    return diu, zzz, diu_estat, caixa_sola


# ─── NETA-3, a la mida nova ──────────────────────────────────────────────────

def _neta(P):
    ROBO, ROBO_D, BRUSH, HAZ, APRON = P.ROBO, P.ROBO_D, P.BRUSH, P.HAZ, P.APRON
    SCR_ON, SCR_DIM = P.SCR_ON, P.SCR_DIM

    def neta(facing='D', talk=False, estat='', k=0, davantal=False):
        """Com hd/personatges.neta, a 53×59: la pantalla, el llum, la franja de perill i les molles, a píxel real."""
        fg = C.Fig(P.NW, P.NH)
        F = fg.F
        low = 4 if estat == 'descansa' else 0
        lean = estat == 'molles'
        gy = 42
        for bx in ((12, 28) if facing != 'L' else (14, 26)):
            fg.ell(bx, gy - 1, 5, 1.6, BRUSH, 2.0, amp=1.0,
                   lvlfn=lambda x, y, k=k: 0.8 if int(x * K + k) % 3 == 0 else 0)
        top = 14 + low
        fg.lathe(gy - 8, gy - 3, lambda y: (6, 34), ROBO_D, 2.6, amp=1.4, cont=(0.2, 0.8))
        for X in range(round(F(7)), round(F(33)) + 1, 4):                      # els cargols de la faldilla
            fg.rpx(X, round(F(gy - 5)), ROBO_D, 4.0)

        def body(y):
            t = (y - top) / (gy - 8 - top)
            half = 11 + 2.5 * t
            c = 20 - 2 * (1 - t) if (lean and facing == 'L') else 20
            return (c - half, c + half)
        fg.lathe(top + 4, gy - 8, body, ROBO, 3.0, amp=1.6, cont=(0.3, 1.0))
        fg.ell(20 - (2 if lean and facing == 'L' else 0), top + 4, 11, 4, ROBO, 3.6, amp=1.6, cont=(0.2, 0.8))   # la tapa
        x0, x1 = (10, 30) if facing in ('D', 'U') else (8, 32)                  # franja de perill, en diagonal
        for Y in range(round(F(gy - 12)) - 1, round(F(gy - 11)) + 1):
            for X in range(round(F(x0)), round(F(x1)) + 1):
                fg.rpx(X, Y, HAZ, 2.4 if (X + Y) % 6 < 3 else 0.6)
        if davantal and facing in ('D', 'L'):
            ax0, ax1 = (13, 27) if facing == 'D' else (8, 17)
            fg.poly([(ax0, top + 8), (ax1, top + 8), (ax1 + 1, gy - 9), (ax0 - 1, gy - 9)], APRON, 2.2, cont=(0.2, 0.8))
            fg.line(ax0 + 1, top + 8, ax0 + 3, top + 5, APRON, 1.6)
            fg.line(ax1 - 1, top + 8, ax1 - 3, top + 5, APRON, 1.6)
            fg.line(ax0 + 3, top + 13, ax1 - 3, top + 13, APRON, 3.6)
            fg.line(ax0 + 3, top + 13, ax0 + 3, top + 16, APRON, 3.0)            # la vora de la butxaca
            fg.line(ax1 - 3, top + 13, ax1 - 3, top + 16, APRON, 3.0)
        hx = 20 - (4 if lean and facing == 'L' else 0)
        hy = top - 3 + (3 if lean else 0)
        fg.limb((20, top + 2), (hx, hy + 3), 2.0, 2.0, ROBO_D, 2.2)
        on = SCR_DIM if estat == 'descansa' else SCR_ON
        HX, HY = round(F(hx)), round(F(hy))
        if facing == 'L':
            fg.poly([(hx - 7, hy - 4), (hx + 4, hy - 4), (hx + 4, hy + 4), (hx - 7, hy + 4)], ROBO, 3.0, cont=(0.2, 0.8))
            fg.poly([(hx - 7, hy - 3), (hx - 4, hy - 3), (hx - 4, hy + 3), (hx - 7, hy + 3)], ROBO_D, 1.0)
            ex = round(F(hx - 6))
            fg.rpx(ex, HY - 2, on, 0); fg.rpx(ex + 1, HY - 2, on, 0)
            fg.rpx(ex, HY - 1, on, 0); fg.rpx(ex + 1, HY - 1, on, 0)
            if talk:
                for X in range(ex, ex + 3):
                    fg.rpx(X, HY + 2, on, 0)
        else:
            fg.poly([(hx - 7, hy - 4), (hx + 7, hy - 4), (hx + 7, hy + 4), (hx - 7, hy + 4)], ROBO, 3.0, cont=(0.2, 0.8))
            if facing == 'D':
                fg.poly([(hx - 5, hy - 3), (hx + 5, hy - 3), (hx + 5, hy + 3), (hx - 5, hy + 3)], ROBO_D, 0.6)
                for Y in range(round(F(hy - 3)), round(F(hy + 3)) + 1, 2):        # les línies de la pantalla
                    fg.rrow(F(hx - 5), F(hx + 5), Y, 0.3, ROBO_D)
                if estat == 'descansa':
                    for ex in (HX - 5, HX + 2):                                  # ulls tancats: dues ratlletes
                        for X in range(ex, ex + 3):
                            fg.rpx(X, HY, on, 0)
                else:
                    blink = k == 5
                    for ex in (HX - 5, HX + 2):
                        for X in range(ex, ex + 3):
                            fg.rpx(X, HY - 2, on, 0)
                            if not blink:
                                fg.rpx(X, HY - 1, on, 0)
                                fg.rpx(X, HY, on, 0)
                        if not blink:
                            fg.rpx(ex, HY - 2, (200, 250, 255), 0)              # la lluentor
                if talk:
                    for X in range(HX - 3, HX + 3):
                        fg.rpx(X, HY + 3, on, 0)
                    fg.rpx(HX - 2, HY + 2, on, 0); fg.rpx(HX + 1, HY + 2, on, 0)
                    fg.rpx(HX - 1, HY + 4, on, 0); fg.rpx(HX, HY + 4, on, 0)
                elif estat != 'descansa':
                    for X in range(HX - 2, HX + 2):
                        fg.rpx(X, HY + 3, on, 0)
                    fg.rpx(HX - 3, HY + 2, on, 0); fg.rpx(HX + 2, HY + 2, on, 0)
            else:                                                               # d'esquena: la reixeta de ventilació
                for y in range(int(hy - 2), int(hy + 3), 2):
                    fg.line(hx - 4, y, hx + 4, y, ROBO_D, 1.6)
                for X in (round(F(hx - 6)), round(F(hx + 6))):                   # els cargols
                    fg.rpx(X, round(F(hy - 3)), ROBO_D, 3.6)
                    fg.rpx(X, round(F(hy + 3)), ROBO_D, 3.6)
        led = (240, 80, 60) if k % 4 < 2 else (120, 30, 30)
        if estat == 'descansa':
            led = (90, 40, 40)
        fg.line(hx + 4, hy - 4, hx + 5, hy - 8, ROBO_D, 2.0)
        LX, LY = round(F(hx + 5)), round(F(hy - 9))
        for X, Y in ((LX, LY), (LX + 1, LY), (LX, LY - 1), (LX + 1, LY - 1)):
            fg.rpx(X, Y, led, 0)
        if led[0] > 200:
            fg.rpx(LX, LY - 1, (255, 190, 170), 0)                             # el reflex del llum encès
        if facing == 'U':
            return fg.render()
        sx = 9 if facing == 'D' else 13
        sy = top + 10
        if estat == 'molles':
            ex, ey = sx - 4, sy + 8
            wx, wy = sx - 6 + (k % 2), gy - 4
        elif estat == 'descansa':
            ex, ey = sx - 1, sy + 7
            wx, wy = sx, sy + 13
        else:
            ex, ey = sx - 4, sy + 4
            wx, wy = sx - 5, sy + 10 - (1 if talk else 0)
        fg.limb((sx, sy), (ex, ey), 1.4, 1.3, ROBO_D, 2.4)
        fg.limb((ex, ey), (wx, wy), 1.3, 1.2, ROBO_D, 2.4)
        fg.ell(wx, wy + 1.5, 2.6, 1.6, BRUSH, 2.4, amp=1.0)
        img = fg.render()
        if estat == 'molles':                                                   # les molles, a terra
            for i, (mx, my) in enumerate(((2, 42), (5, 43), (8, 42), (3, 41), (34, 43), (37, 42))):
                if (i + k) % 3 != 0:
                    X, Y = round(f(mx)), min(img.height // S - 1, round(f(my)))
                    _poke(img, X, Y, (214, 170, 100, 255))
                    if i % 2:
                        _poke(img, X + 1, Y, (176, 130, 70, 255))
        return img

    return neta


# ─── Instal·lació ────────────────────────────────────────────────────────────

_MAP = {}


def _port(obj, seen=None):
    """Una còpia de `obj` (espec, dict, tupla, clausura) amb els ganxos de 480 canviats pels de 640."""
    if isinstance(obj, types.FunctionType):
        if obj in _MAP:
            return _MAP[obj]
        if obj.__closure__:
            seen = seen or set()
            if id(obj) in seen:
                return obj
            seen.add(id(obj))
            vals = []
            for c in obj.__closure__:
                try:
                    vals.append(c.cell_contents)
                except ValueError:
                    return obj
            new = [_port(v, seen) for v in vals]
            if any(a is not b for a, b in zip(vals, new)):
                fn = types.FunctionType(obj.__code__, obj.__globals__, obj.__name__, obj.__defaults__,
                                        tuple(types.CellType(v) for v in new))
                fn.__kwdefaults__ = obj.__kwdefaults__
                return fn
        return obj
    if isinstance(obj, dict):
        new = {k: _port(v, seen) for k, v in obj.items()}
        return obj if all(new[k] is obj[k] for k in obj) else new
    if isinstance(obj, (list, tuple)):
        new = [_port(v, seen) for v in obj]
        if all(a is b for a, b in zip(obj, new)):
            return obj
        return type(obj)(new) if isinstance(obj, list) else tuple(new)
    return obj


def install(art_scale=1):
    """Substitueix Fig, la cara i els ganxos de detall a hd.characters i hd.personatges (només en aquest procés).
    `art_scale` (la primera vegada): 1 per a les figures de 640 (les sales), ART_SCALE per als fulls."""
    global S
    import hd.personatges as P
    if getattr(P, '_hd640', False):
        return P
    S = art_scale
    fig = FigK2 if S > 1 else FigK
    C.Fig = fig
    C.front_face = front_face
    C.side_face = side_face
    P.Fig = fig
    P.front_face = front_face
    P.side_face = side_face

    for name, fn in _ganxos(P).items():
        _MAP[getattr(P, name)] = fn
        setattr(P, name, fn)

    # els personatges que es dibuixen sencers o s'hi enganxa alguna cosa després (estampats, escala)
    old_iri, old_vet = P.iri, P.vet

    def iri(facing, walk=None, talk=False, roba=''):
        """L'Iri, amb el «</>» de 640 (15×7)."""
        spec = dict(P.IRI)
        hooks = dict(spec['hooks'])
        hair = hooks['hair']

        def hair_and_phones(fg, p, s):
            hair(fg, p, s)
            if roba != 'SenseAuriculars':
                P.iri_phones(fg, p, s)
        hooks['hair'] = hair_and_phones
        hooks.pop('over', None)
        spec['hooks'] = hooks
        img = C.person(spec, facing, walk=walk, talk=talk)
        if facing in ('D', 'DL'):
            b = C.Pose(facing, walk, talk, stoop=spec.get('stoop', 0)).bob
            x0, y0 = round(f(24) - 7), round(f(33 + b))
            for dx, dy in LOGO:
                _poke(img, x0 + dx, y0 + dy, (226, 236, 228, 255), 'DL' if facing == 'DL' else None)
        return img

    def vet(facing, walk=None, talk=False, roba='', ulleres=False):
        """La Vet, amb les ulleres i els estampats de 640."""
        spec, prints = P.VET_ROBA[roba]
        spec = dict(spec)
        if ulleres:
            hk = dict(spec['hooks'])
            hair = hk['hair']
            hk['hair'] = lambda fg, p, s: (hair(fg, p, s), P.vet_glasses(fg, p, s))
            spec['hooks'] = hk
        img = C.person(spec, facing, walk=walk, talk=talk)
        if facing in ('D', 'DL'):
            b = C.Pose(facing, walk, talk, stoop=spec.get('stoop', 0)).bob
            k = FigK.k_escala or K
            for pattern, x, y, col in prints:
                q = 'DL' if facing == 'DL' else None
                if k < 1:                                   # una figura petita (de lluny): l'estampat de 480, a ×k
                    _stamp_petit(img, pattern, x, y + b, col, k, q)
                    continue
                name = next(n for n in STAMPS if getattr(P, n) is pattern)
                _stamp_at(img, STAMPS[name], pattern, x, y + b, col, q)
        return img

    def npc(cid, facing, talk=False, walk=None):
        spec = P.NPCS[cid]
        if spec.get('seated') is not None and facing != 'L':
            side = C.person(spec, 'L', talk=talk)
            out = Image.new('RGBA', side.size, (0, 0, 0, 0))
            out.alpha_composite(side.transpose(Image.FLIP_LEFT_RIGHT), (3 * S, 0))   # els peus, a x = 34 (com de perfil)
            return out
        if cid == 'nen':
            # un nen de set anys: dibuixat directament a ×0,62 (no encongit), amb els peus al mateix lloc
            with escala(K * 0.62):
                small = C.person(spec, facing, walk=walk, talk=talk)
            out = Image.new('RGBA', (round(49 * K) * S, round(87 * K) * S), (0, 0, 0, 0))
            out.alpha_composite(small, (round(f(25) - (25.5 * K * 0.62 - 0.5)) * S, round(f(83) - (83.5 * K * 0.62 - 0.5)) * S))
            return out
        return C.person(spec, facing, walk=walk, talk=talk)

    def npc2(cid, facing, talk=False, variant='', walk=None):
        spec = P.NPCS2[cid][variant]
        k = P.BIG.get(cid)
        if not k:
            return C.person(spec, facing, walk=walk, talk=talk)
        # en Ballester: dibuixat directament a ×k (no ampliat), en un fotograma de 77×133 amb els peus a big2_feet ×4/3
        with escala(K * k):
            big = C.person(spec, facing, walk=walk, talk=talk)
        w, h = P.big2_size(cid)
        fx, fy = P.big2_feet(cid)
        out = Image.new('RGBA', (round(w * K) * S, round(h * K) * S), (0, 0, 0, 0))
        out.alpha_composite(big, ((round(f(fx)) - round(25.5 * K * k - 0.5)) * S, (round(f(fy)) - round(83.5 * K * k - 0.5)) * S))
        return out

    P.iri, P.vet, P.npc, P.npc2 = iri, vet, npc, npc2
    P._iri480, P._vet480 = old_iri, old_vet
    P.diu, P.zzz, P.diu_estat, P.caixa_sola = _diu(P)
    P.neta = _neta(P)

    # les especificacions ja muntades (diccionaris i clausures amb els ganxos de 480)
    P.IRI = _port(P.IRI)
    P.HAIR_HOOKS = _port(P.HAIR_HOOKS)
    P.VET_ROBA = {k: (_port(spec), prints) for k, (spec, prints) in P.VET_ROBA.items()}
    P.NPCS = _port(P.NPCS)
    P.NPCS2 = _port(P.NPCS2)
    P._hd640 = True
    return P


def person(spec, facing='D', walk=None, talk=False):
    """Per a les sales que dibuixen gent (hd640/rooms): hd.characters.person a ×4/3 (65×116, peus a (34, 111)).
    Els ganxos de hd/personatges.py que hi hagi a `spec` es canvien pels de 640."""
    install()
    return C.person(_port(spec), facing, walk=walk, talk=talk)


# ─── Fulls ───────────────────────────────────────────────────────────────────

def scaled_extra(extra):
    """Punts i velocitats del .character.json, de coordenades de 480 a 640."""
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


def de_lluny(fn):
    """`fn()` (una figura) dibuixada directament a la mida de lluny, ×K×LLUNY de draw_characters (vegeu-hi LLUNY)."""
    import draw_characters as D
    with escala(K * D.LLUNY):
        return fn()


def main():
    install(ART_SCALE)
    import draw_characters as D
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / 'characters'
    D.OUT = out
    D.scaled_extra = scaled_extra
    D.DE_LLUNY = de_lluny
    D.main()


if __name__ == '__main__':
    main()
