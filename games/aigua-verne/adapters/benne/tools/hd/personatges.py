"""
Personatges d'Aigua Verne, amb el sistema de figures amb volum de Suma Zero / Ni un ou (hd/characters.py).

Dues mides (guió, «Art: dues mides de càmera»):
  - **de lluny**: la figura a la seva mida de disseny (una persona fa ≈83 px; fotograma de 49×87, peus a (25, 83));
  - **de prop**: la mateixa figura redibuixada a ×1,2 (≈100 px; fotograma de 59×104), no ampliada: FigK rep les
    mateixes ordres en coordenades de disseny i les rasteritza a la mida gran (amb volum i contorn d'un píxel real),
    i la cara (ulls, celles, nas, boca) es refà píxel a píxel a la mida nova. Com hd640/draw_characters.py de
    Ni un ou (que ho fa a ×4/3).

Cada personatge es descriu una sola vegada (un dict per a `person`, amb ganxos) i es dibuixa a les dues mides:

    with de_prop():
        img = iri('D')          # 59×104
    img = iri('D')              # 49×87

L'aspecte és el de guio/fitxes-sales.md («Personatges»). La cara de l'Iri i de la Vet és la de sempre (la de
Suma Zero); el cabell i la roba, els d'aquest joc (guio/art/mostra/personatges.py).
"""
import math
from contextlib import contextmanager

from PIL import Image

import hd.characters as C
from hd.characters import (M, person, SKIN_IRI, SKIN_VET, SKIN_PALE, SKIN_OLD, SKIN_RUDDY, BOOT, STEELB, BRASS, LENS,
                           HAIR_WHITE, WHITE, TROUSER, SUIT_D, CREAM, ORANGE, GRAY_SHOE, BELT, GOLDPIN,
                           shoe_front, shoe_side, hair_lvl)
from hd.pix import mix

# ═══════════════════════════════════════════════════════════════════════════
#  La mida de prop: ×1,2
# ═══════════════════════════════════════════════════════════════════════════

K = 1.2
K1 = K
ART_SCALE = 1            # 2 en fer els fulls (draw_characters.py): la mida de prop es dibuixa a 2× (FigK2)
_Fig1 = C.Fig            # la figura de sempre (×1)


def f(u):
    """Coordenada de disseny (centre de píxel) → coordenada real a ×K."""
    return (u + 0.5) * K - 0.5


def g(X):
    """Coordenada real → de disseny."""
    return (X + 0.5) / K - 0.5


def span(i):
    """Els píxels reals que ocupa el píxel de disseny i."""
    return range(math.ceil(i * K - 0.5), math.ceil((i + 1) * K - 0.5))


class FigK(_Fig1):
    """Fig que dibuixa a ×K. `w`, `h` i `buf` són a la mida real."""

    big = True

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
        # lvlfn rep coordenades de disseny, però es crida per a cada píxel real
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


    def rset(self, X, Y, v):
        """Posa `v` (o None, per esborrar) en un píxel real."""
        X, Y = int(round(X)), int(round(Y))
        if 0 <= X < self.w and 0 <= Y < self.h:
            self.buf[Y][X] = v


class FigK2(FigK):
    """FigK a S× (S = ART_SCALE): la mateixa figura de prop, amb l'API en píxels de ×1,2 i el buffer a S×.
      - el que té volum (`ell`, `limb`, `lathe`, `poly`) i els píxels de disseny (`px`, `shade`, `erase`, `get`) es
        rasteritzen a la resolució real (`f`, `g` i `span` hi treballen amb K = 1,2 × S);
      - els detalls píxel a píxel (`rpx`, `rshade`, `rset`, i `line`, que hi passa), en píxels de ×1,2: cada un, un
        bloc S×S. La cara, les ulleres... queden igual que a ×1,2.
    Els ganxos que recorren el buffer fan servir `px_scale(fg)` i `design(fg, X)`."""

    kbase = K1               # l'escala de l'API (la de prop); FigL2, 1

    def __init__(self, w, h):
        super().__init__(w, h)
        self.S = ART_SCALE
        self.w, self.h = self.w * self.S, self.h * self.S
        self.buf = [[None] * self.w for _ in range(self.h)]
        self._fine = 0

    @contextmanager
    def _fi(self):
        global K
        self._fine += 1
        if self._fine == 1:
            self._k_out, K = K, self.kbase * self.S
        try:
            yield
        finally:
            self._fine -= 1
            if not self._fine:
                K = self._k_out

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
        X, Y, S = int(round(X)), int(round(Y)), self.S
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

    def rset(self, X, Y, v):
        if self._fine:
            return super().rset(X, Y, v)
        for x, y in self._blk(X, Y):
            super().rset(x, y, v)


class FigL2(FigK2):
    """La figura de lluny (×1) a S×: l'API és la de la figura de sempre (coordenades de disseny = píxels de ×1) i el
    buffer, a S×. Els volums i els píxels de disseny es rasteritzen a la resolució real (com FigK2 amb K = 1 × S); les
    línies i els píxels que els ganxos posen un a un (`rset`), en blocs S×S. `big` és fals: els ganxos hi fan el camí
    de ×1."""

    big = False
    kbase = 1.0

    def __init__(self, w, h):
        _Fig1.__init__(self, w * ART_SCALE, h * ART_SCALE)
        self.S = ART_SCALE
        self._fine = 0

    def line(self, x0, y0, x1, y1, mat, lvl):
        """Com la de ×1: un píxel de disseny de gruix (un bloc S×S)."""
        n = int(math.ceil(max(abs(x1 - x0), abs(y1 - y0), 1)))
        for i in range(n + 1):
            t = i / n
            self.rpx(x0 + (x1 - x0) * t + self.ox, y0 + (y1 - y0) * t + self.oy, mat, lvl)


def big(fg):
    return getattr(fg, 'big', False)


def px_scale(fg):
    """Quants píxels del buffer fa cada píxel real de la figura (S a FigK2, 1 si no)."""
    return getattr(fg, 'S', 1)


def design(fg, X):
    """La coordenada de disseny del píxel X del buffer d'una figura (de prop o de lluny, a qualsevol S)."""
    kb = getattr(fg, 'kbase', K1 if big(fg) else 1.0)
    return (X + 0.5) / (kb * px_scale(fg)) - 0.5


# ─── La cara, a la mida de prop ─────────────────────────────────────────────
# A ×1 l'ull és de 2×1 amb la parpella a sobre; a ×1,2, de 3 px d'ample (blanc, iris i pupil·la), amb la parpella
# i una segona fila curta d'iris: ni massa gran ni massa petit en un cap de 16 px.

def _eye(fg, x0, ey, inner_right, spec, closed):
    eye = spec.get('eye', (34, 22, 30))
    iris = spec.get('iris', (70, 50, 40))
    S = spec['skin']
    if closed:
        for i in range(3):
            fg.rpx(x0 + i, ey, eye, 0)
        return
    for i in range(3):
        fg.rpx(x0 + i, ey - 1, eye, 0)
    dark = mix(iris, eye, 0.55)
    row = [C.EYE_W, iris, dark]
    for i, c in enumerate(row if inner_right else row[::-1]):
        fg.rpx(x0 + i, ey, c, 0)
    for i in range(3):                                   # la parpella de sota, una mica d'ombra
        fg.rshade(x0 + i, ey + 1, -0.45, S)


def front_face_k(fg, p, spec):
    hx, hy = p.head
    S = spec['skin']
    brow = spec.get('brow', (40, 24, 28))
    eye = spec.get('eye', (34, 22, 30))
    yd = int(hy + 0.5)                                    # la fila dels ulls a ×1
    ey = round(f(yd))
    lx, rx = round(f(hx - 3.0)) - 1, round(f(hx + 3.0)) - 1   # 3 px cada ull, simètrics
    closed = spec.get('closed')
    _eye(fg, lx, ey, True, spec, closed)
    _eye(fg, rx, ey, False, spec, closed)
    if spec.get('lashes') and not closed:
        fg.rpx(lx - 1, ey - 1, eye, 0); fg.rpx(rx + 3, ey - 1, eye, 0)
        fg.rpx(lx - 1, ey - 2, eye, 0); fg.rpx(rx + 3, ey - 2, eye, 0)
    if spec.get('liner'):
        fg.rpx(lx - 1, ey, spec['liner'], 0); fg.rpx(rx + 3, ey, spec['liner'], 0)
    # celles
    by = ey - 3 + round(spec.get('brow_dy', 0) * K)
    for dx, dy in ((-1, 1), (0, 0), (1, 0), (2, 0)):
        fg.rpx(lx + dx, by + dy, brow, 0)
    for dx, dy in ((0, 0), (1, 0), (2, 0), (3, 1)):
        fg.rpx(rx + dx, by + dy, brow, 0)
    # nas: llum a l'esquerra del pont, ombra a la dreta i a sota
    nx = round(f(hx) - 0.5)
    for y in range(ey, ey + 3):
        fg.rshade(nx - 1, y, +0.5, S)
    fg.rshade(nx + 1, ey + 2, -0.7, S); fg.rshade(nx + 1, ey + 3, -0.9, S)
    fg.rshade(nx, ey + 3, -1.1, S); fg.rshade(nx - 1, ey + 3, -0.5, S)
    if spec.get('blush'):
        fg.rshade(lx, ey + 2, -0.4, S); fg.rshade(lx - 1, ey + 2, -0.4, S)
        fg.rshade(rx + 2, ey + 2, -0.6, S); fg.rshade(rx + 3, ey + 2, -0.6, S)
    # boca: quatre píxels; parlant, oberta
    my = ey + 6
    lip = spec.get('lip', C.LIP)
    m0 = nx - 1
    if p.talk:
        for i in range(4):
            fg.rpx(m0 + i, my, C.MOUTH if 0 < i < 3 else lip, 0)
        fg.rpx(m0 + 1, my + 1, C.MOUTH, 0); fg.rpx(m0 + 2, my + 1, C.MOUTH, 0)
        fg.rpx(m0 + 1, my + 2, lip, 0); fg.rpx(m0 + 2, my + 2, lip, 0)
    elif spec.get('smile'):
        fg.rpx(m0 - 1, my - 1, lip, 0); fg.rpx(m0 + 4, my - 1, lip, 0)
        for i in range(4):
            fg.rpx(m0 + i, my, mix(lip, C.MOUTH, 0.5) if 0 < i < 3 else lip, 0)
        fg.rshade(m0 + 1, my + 1, +0.4, S); fg.rshade(m0 + 2, my + 1, +0.4, S)
    else:
        for i in range(4):
            fg.rpx(m0 + i, my, mix(lip, C.MOUTH, 0.5) if 0 < i < 3 else lip, 0)
        fg.rshade(m0 + 1, my + 1, +0.4, S); fg.rshade(m0 + 2, my + 1, +0.4, S)


def side_face_k(fg, p, spec):
    hx, hy = p.head
    S = spec['skin']
    eye = spec.get('eye', (34, 22, 30))
    iris = spec.get('iris', (70, 50, 40))
    brow = spec.get('brow', (40, 24, 28))
    yd = int(hy + 0.5)
    ey = round(f(yd))
    ex = round(f(int(hx - 3.5)))                         # l'ull, de perfil: 2 px d'ample
    if spec.get('closed'):
        fg.rpx(ex, ey, eye, 0); fg.rpx(ex + 1, ey, eye, 0)
    else:
        for i in range(3):
            fg.rpx(ex - 1 + i, ey - 1, eye, 0)
        fg.rpx(ex - 1, ey, C.EYE_W, 0); fg.rpx(ex, ey, iris, 0); fg.rpx(ex + 1, ey, mix(iris, eye, 0.55), 0)
        fg.rshade(ex - 1, ey + 1, -0.45, S); fg.rshade(ex, ey + 1, -0.45, S)
        if spec.get('lashes'):
            fg.rpx(ex + 2, ey - 1, eye, 0)
        if spec.get('liner'):
            fg.rpx(ex + 2, ey, spec['liner'], 0)
    by = ey - 3 + round(spec.get('brow_dy', 0) * K)
    for dx, dy in ((-2, 0), (-1, 0), (0, 0), (1, 1)):
        fg.rpx(ex + dx, by + dy, brow, 0)
    # orella (amb el forat)
    oxd = int(hx + 2.5) + 0.5
    fg.ell(oxd, yd + 2, 1.6, 2.2, S, 2.6, amp=1.2)
    fg.rshade(f(oxd), f(yd + 2) - 0.5, -1.2, S); fg.rshade(f(oxd), f(yd + 2) + 0.5, -0.9, S)
    if spec.get('blush'):
        fg.rshade(ex + 1, ey + 2, -0.4, S); fg.rshade(ex + 2, ey + 2, -0.4, S)
    # boca
    my = ey + 6
    lip = spec.get('lip', C.LIP)
    mx = round(f(int(hx - 5.5)))
    if p.talk:
        fg.rpx(mx, my, C.MOUTH, 0); fg.rpx(mx + 1, my, C.MOUTH, 0); fg.rpx(mx + 2, my, lip, 0)
        fg.rpx(mx + 1, my + 1, C.MOUTH, 0)
        fg.rset(mx - 1, my, None)                         # el llavi de baix cau: la boca oberta es veu de perfil
    else:
        if spec.get('smile'):
            fg.rpx(mx + 3, my - 1, lip, 0)
        fg.rpx(mx, my, lip, 0); fg.rpx(mx + 1, my, mix(lip, C.MOUTH, 0.5), 0); fg.rpx(mx + 2, my, mix(lip, C.MOUTH, 0.3), 0)


# A ×1, la cara de sempre (amb el somriure, si cal).
_front1, _side1 = C.front_face, C.side_face


def front_face_1(fg, p, spec):
    _front1(fg, p, spec)
    if spec.get('smile') and not p.talk and not spec.get('closed'):
        hx, hy = p.head
        nx, my = int(hx), int(hy + 0.5) + 5
        fg.px(nx - 2, my - 1, spec.get('lip', C.LIP), 0); fg.px(nx + 2, my - 1, spec.get('lip', C.LIP), 0)


def side_face_1(fg, p, spec):
    _side1(fg, p, spec)
    if spec.get('smile') and not p.talk:
        hx, hy = p.head
        fg.px(int(hx - 5.5) + 2, int(hy + 0.5) + 4, spec.get('lip', C.LIP), 0)


C.front_face, C.side_face = front_face_1, side_face_1


@contextmanager
def de_prop():
    """Dins d'aquest bloc, tot el que es dibuixa amb hd.characters (i aquí) surt a ×1,2."""
    saved = C.Fig, C.front_face, C.side_face
    C.Fig, C.front_face, C.side_face = (FigK2 if ART_SCALE > 1 else FigK), front_face_k, side_face_k
    try:
        yield
    finally:
        C.Fig, C.front_face, C.side_face = saved


@contextmanager
def de_lluny():
    """Dins d'aquest bloc, la mida de lluny es dibuixa a ART_SCALE× (FigL2), si cal."""
    saved = C.Fig
    if ART_SCALE > 1:
        C.Fig = FigL2
    try:
        yield
    finally:
        C.Fig = saved


def Fig(w, h):
    """Una figura buida de w×h (de disseny), a la mida que toqui."""
    return C.Fig(w, h)


# Petites ajudes que funcionen a les dues mides

def dot(fg, x, y, mat, lvl):
    """Un punt d'un sol píxel real (a ×1, un píxel de disseny)."""
    if big(fg):
        fg.rpx(f(x + fg.ox), f(y + fg.oy), mat, lvl)
    else:
        fg.px(x, y, mat, lvl)


def hooks(*fns):
    def run(fg, p, *a):
        for fn in fns:
            fn(fg, p, *a)
    return run


# ═══════════════════════════════════════════════════════════════════════════
#  Materials
# ═══════════════════════════════════════════════════════════════════════════

LEATHER = M((22, 12, 10), (44, 24, 16), (70, 40, 24), (98, 60, 34), (128, 84, 48), (160, 112, 70), dith=0.0)
SHEEP = M((92, 80, 66), (140, 126, 104), (184, 170, 144), (216, 204, 178), (238, 230, 208))
TEE = M((70, 66, 60), (120, 114, 104), (170, 164, 150), (208, 202, 186))
OLIVE = M((14, 16, 10), (28, 32, 18), (46, 52, 30), (66, 74, 44), (90, 98, 62), (118, 126, 86), dith=0.0)
GLOVE = M((8, 8, 8), (18, 18, 18), (32, 30, 30), (50, 48, 46))
PATCH_B = M((10, 20, 50), (24, 50, 110), (60, 110, 190), (130, 180, 240))
PATCH_R = M((50, 10, 10), (120, 26, 22), (190, 56, 40), (240, 120, 90))
PATCH_Y = M((60, 44, 6), (140, 104, 16), (214, 170, 40), (250, 224, 120))
PATCH_G = M((8, 36, 18), (20, 80, 40), (50, 140, 70), (120, 200, 130))

COVERALL = M((8, 14, 30), (14, 28, 56), (24, 46, 86), (38, 68, 116), (58, 94, 146), (88, 126, 176), dith=0.0)
HAIR_BLACK = M((4, 4, 6), (10, 8, 12), (20, 16, 22), (34, 28, 36), (54, 46, 56), (80, 72, 82))
STRAP = M((6, 6, 6), (16, 14, 14), (30, 26, 24), (46, 40, 36))
YELLOWH = M((70, 50, 6), (150, 110, 16), (220, 176, 40), (250, 226, 120))

VELVET = M((24, 4, 12), (48, 8, 20), (78, 14, 30), (110, 22, 40), (146, 34, 52), (184, 58, 70), (214, 102, 104), dith=0.0)
SEQUIN = M((84, 54, 22), (190, 144, 54), (252, 234, 160), (255, 252, 230))


# ═══════════════════════════════════════════════════════════════════════════
#  L'Iri, la pilot
# ═══════════════════════════════════════════════════════════════════════════

HAIR_IRI_AV = M((10, 6, 6), (22, 14, 12), (36, 24, 18), (52, 36, 26), (72, 52, 38), (98, 74, 54))


def _sleek_iri(x, y):
    return 0.5 * math.sin(x * 0.6 + y * 1.7)


def _braid(fg, x0, y0, x1, y1, H, base):
    """Una trena: nusos alternats que s'aprimen, el lligam de cuir i el floc de la punta."""
    n = int(abs(y1 - y0) / 1.8)
    for k in range(n + 1):
        t = k / n
        x = x0 + (x1 - x0) * t + (0.5 if k % 2 else -0.5)
        y = y0 + (y1 - y0) * t
        fg.ell(x, y, 1.9 - 0.5 * t, 1.3, H, base + (0.3 if k % 2 else 0), amp=1.2, cont=(0.2, 0.8))
    fg.ell(x1, y1 + 0.8, 1.2, 0.7, LEATHER, 2.6, amp=0.6)
    fg.ell(x1, y1 + 2.2, 1.1, 1.3, H, base, amp=1.0)


def iri_hair(fg, p, spec):
    """Marró fosc, estirat enrere en una trena llarga (de cara, sobre l'espatlla), amb un floc solt al front."""
    hx, hy = p.head
    H = HAIR_IRI_AV
    if p.f == 'D':
        fg.ell(hx, hy - 1.4, 7.2, 7.2, H, 2.6, amp=1.6, cont=(0.2, 0.8), lvlfn=_sleek_iri,
               clip=lambda x, y: y <= hy - 4.2 + ((x - hx) / 7.0) ** 2 * 4.4 or abs(x - hx) > 6.2)
        fg.line(hx - 5.6, hy - 3, hx - 6.0, hy + 3, H, 2.0)                           # el floc solt
        _braid(fg, hx + 5.4, hy + 6.0, hx + 7.0, hy + 19.0, H, 2.6)
    elif p.f == 'L':
        fg.ell(hx + 1.0, hy - 1.4, 7.2, 7.2, H, 2.6, amp=1.6, cont=(0.2, 0.8), lvlfn=_sleek_iri,
               clip=lambda x, y: (x >= hx - 1.0 or y <= hy - 4.6) and not (x < hx + 2.6 and y > hy - 1.0))
        _braid(fg, hx + 6.0, hy + 3.0, hx + 6.6, hy + 18.0, H, 2.4)
    else:
        fg.ell(hx, hy - 0.8, 7.4, 7.8, H, 2.6, amp=1.6, cont=(0.2, 0.8), lvlfn=_sleek_iri)
        _braid(fg, hx, hy + 5.0, hx + 0.4, hy + 20.0, H, 2.6)


def iri_collar(fg, p, spec):
    """El coll de xai de la jaqueta de vol."""
    b = p.bob
    if p.f == 'D':
        for sx in (-1, 1):
            fg.ell(24.5 + sx * 4.6, 29.0 + b, 3.6, 2.4, SHEEP, 3.0 if sx < 0 else 2.4, amp=1.2, cont=(0.2, 0.8))
    elif p.f == 'L':
        fg.ell(26.5, 28.6 + b, 4.4, 2.4, SHEEP, 2.8, amp=1.2, cont=(0.2, 0.8))
    else:
        fg.ell(24.5, 28.4 + b, 6.6, 2.4, SHEEP, 2.6, amp=1.2, cont=(0.2, 0.8))


def iri_over(fg, p, spec):
    """Jaqueta oberta: la samarreta al mig, la cintura de punt i els pegats."""
    b = p.bob
    if p.f == 'D':
        for y in range(31 + b, 47 + b):
            for x in range(23, 27):
                fg.px(x, y, TEE, 2.6 - (0.8 if x == 26 else 0))
            fg.px(22, y, LEATHER, 1.4)
            fg.px(27, y, LEATHER, 1.0)
        for y in (47 + b, 48 + b, 49 + b):                                          # cintura de punt
            for x in range(16, 33):
                fg.px(x, y, LEATHER, 1.2 + (0.6 if x % 2 else 0))
        for (x0, y0), mat in (((17, 34), PATCH_B), ((29, 33), PATCH_R)):          # pegats al pit
            for y in range(y0 + b, y0 + b + 3):
                for x in range(x0, x0 + 3):
                    fg.px(x, y, mat, 2.4 if (x, y - b) != (x0, y0) else 3.0)
    elif p.f == 'L':
        for y in range(31 + b, 47 + b):
            fg.px(19.6, y, TEE, 2.2)
        for y in (47 + b, 48 + b):
            for x in range(20, 32):
                fg.px(x, y, LEATHER, 1.2 + (0.6 if x % 2 else 0))
        for y in range(34 + b, 37 + b):
            for x in (22, 23, 24):
                fg.px(x, y, PATCH_R, 2.6)
    else:
        for y in (47 + b, 48 + b, 49 + b):
            for x in range(16, 33):
                fg.px(x, y, LEATHER, 1.2 + (0.6 if x % 2 else 0))
        for y in range(34 + b, 41 + b):                                             # el pegat gran de l'esquena
            for x in range(21, 28):
                fg.px(x, y, PATCH_Y if 35 + b <= y <= 39 + b and 22 <= x <= 26 else PATCH_B, 2.4)


def iri_arm(fg, p, spec, i):
    """Un pegat a la màniga i els guants sense dits."""
    if p.f == 'L':
        s, e, w = p.arms[i]
    else:
        s, e, w = p.sh[i], p.elbow[i], p.wrist[i]
    if i == 0 and p.f != 'U':
        mx, my = (s[0] + e[0]) / 2, (s[1] + e[1]) / 2
        fg.ell(mx, my, 1.4, 1.4, PATCH_G, 2.6, amp=0.8)
    fg.ell(w[0] - (0.4 if p.f == 'L' else 0), w[1] + 1.6, 2.2, 1.6, GLOVE, 2.4, amp=1.2)


IRI = {
    'skin': SKIN_IRI, 'legs': OLIVE, 'top': LEATHER, 'shoes': BOOT, 'lashes': True,
    'iris': (52, 38, 30), 'brow': (24, 16, 22),   # la cara de l'Iri, la mateixa a tots els jocs
    'hooks': {'hair': iri_hair, 'collar': iri_collar, 'over': iri_over, 'arm': iri_arm},
}


# ─── La roba de gala: vestit de vellut granat fins als peus i corona d'engranatge ───

def _skirt_hem(p):
    """Les vores de la faldilla a cada fila (de la cintura als peus), segons la direcció i el pas."""
    b = p.bob
    if p.f == 'L':
        xs = [leg[2][0] for leg in p.legs]
        back, front = max(xs) + 6.0, min(xs) - 7.0
        top = 46 + b

        def e(y):
            t = max(0.0, min(1.0, (y - top) / (82 - top)))
            l = 20.6 + (front - 20.6) * t ** 1.3
            r = 30.6 + (back - 30.6) * t ** 1.2
            return (min(l, 20.6), max(r, 30.6))
        return top, 82, e
    lift = getattr(p, 'lift', [0, 0])
    top = 46 + b

    def e(y):
        t = max(0.0, min(1.0, (y - top) / (82 - top)))
        w = 7.6 + 6.6 * t ** 1.2
        sway = (lift[1] - lift[0]) * 0.35 * t
        return (24.5 - w + sway, 24.5 + w + sway)
    return top, 82, e


def _sequins(fg, mat):
    """Lluentons de llautó escampats pel vellut (un píxel real cadascun)."""
    for y in range(fg.h):
        for x in range(fg.w):
            v = fg.buf[y][x]
            if v and v[0] is mat:
                X, Y = x // px_scale(fg), y // px_scale(fg)                      # en píxels de ×1,2
                h = (X * 7349 + Y * 1931 + (X * Y) % 13) % 41
                if h == 0:
                    fg.buf[y][x] = (SEQUIN, 1.0 + max(0.0, v[1] - 2.2) * 0.8)
                elif h == 20 and v[1] > 2.6:
                    fg.buf[y][x] = (SEQUIN, 2.2)


def gala_torso(fg, p, spec):
    """La faldilla de vellut fins a terra (tapa les cames), amb les puntes de les sabates que en surten."""
    top, bot, e = _skirt_hem(p)
    if p.f == 'L':
        fg.lathe(top, bot, e, VELVET, 2.6, amp=1.6,
                 lvlfn=lambda x, y: (-0.7 if int(x) in (24, 28) and y > 56 else 0))
        for leg in p.legs:
            a = leg[2]
            if a[0] < 22:
                fg.ell(a[0] - 3.6, 82.4, 2.4, 1.2, GOLDPIN, 1.8, amp=1.0)
    else:
        fg.lathe(top, bot, e, VELVET, 2.6, amp=1.6,
                 lvlfn=lambda x, y: (-0.8 if int(x) in (20, 29) and y > 58 else 0.4 if int(x) == 24 and y > 58 else 0))
        if p.f == 'D':
            for i in (0, 1):
                ax = p.ankle[i][0]
                if p.lift[i] < 1.0:
                    fg.ell(ax, 82.6, 2.4, 1.0, GOLDPIN, 1.8, amp=1.0)
    # vora de llautó a baix
    l, r = e(bot)
    for x in range(math.ceil(l), math.floor(r) + 1):
        fg.px(x, bot, BRASS, 2.2 + (0.6 if x % 2 else 0))


def gala_over(fg, p, spec):
    """El cos del vestit: escot de llautó i el cinturó; i els lluentons."""
    b = p.bob
    if p.f == 'D':
        for x in range(19, 31):
            fg.px(x, 46 + b, BRASS, 2.4 + (0.6 if x % 3 == 0 else 0))
        fg.ell(24.5, 46 + b, 1.4, 1.2, BRASS, 3.0, amp=1.0)
        for k, x in enumerate(range(20, 30)):
            yy = 29 + b + abs(x - 24.5) * -0.4 + 2.6
            fg.px(x, yy, BRASS, 2.6)
    elif p.f == 'L':
        for x in range(20, 31):
            fg.px(x, 46 + b, BRASS, 2.4 + (0.6 if x % 3 == 0 else 0))
    else:
        for x in range(19, 31):
            fg.px(x, 46 + b, BRASS, 2.0)
    _sequins(fg, VELVET)


def gala_crown(fg, p, spec):
    """La corona: un engranatge de llautó posat damunt el cabell (un aro amb dents quadrades i separades)."""
    hx, hy = p.head
    cx = hx + (0.8 if p.f == 'L' else -0.2)
    cy = hy - 7.6
    half = 5.0 if p.f == 'L' else 5.6
    fg.poly([(cx - half, cy + 1.4), (cx - half, cy - 1.4), (cx + half, cy - 1.4), (cx + half, cy + 1.4)], BRASS, 2.4,
            amp=1.0, normal=lambda x, y: (max(-1, min(1, (x - cx) / (half + 1))), -0.2, 0.8))
    xs = [cx - half + 0.5 + k * 2 for k in range(int(half) + 1)]
    for k, x in enumerate(xs):
        lvl = 3.0 - 0.9 * (x - cx) / half
        fg.px(x, cy - 2.4, BRASS, lvl)
        fg.px(x, cy - 3.2, BRASS, lvl + 0.4)
    for x in range(int(cx - half), int(cx + half) + 1):                             # la vora de sota, a l'ombra
        fg.shade(x, cy + 1.2, -0.9, BRASS)
    if p.f != 'U':
        fx = cx - (2.0 if p.f == 'L' else 0)
        fg.ell(fx, cy, 1.3, 1.1, PATCH_R, 2.6, amp=1.0)                             # una pedra vermella al mig
        dot(fg, fx - 0.4, cy - 0.5, CREAM, 4.0)


def gala_arm(fg, p, spec, i):
    """Punys de llautó."""
    w = p.arms[i][2] if p.f == 'L' else p.wrist[i]
    fg.ell(w[0] - (0.4 if p.f == 'L' else 0), w[1] + 0.2, 2.6, 1.0, BRASS, 2.6, amp=1.0)


IRI_ROBA = {
    '': IRI,
    'Gala': {
        'skin': SKIN_IRI, 'legs': VELVET, 'top': VELVET, 'shoes': BOOT, 'lashes': True,
        'iris': (52, 38, 30), 'brow': (24, 16, 22),
        'hooks': {'hair': hooks(iri_hair, gala_crown), 'torso': gala_torso, 'over': gala_over, 'arm': gala_arm},
    },
}


# ═══════════════════════════════════════════════════════════════════════════
#  La Vet, l'enginyera
# ═══════════════════════════════════════════════════════════════════════════

def _sleek(x, y):
    return 0.6 * math.sin(x * 0.5 + y * 1.8)


def _bun(x, y):
    """El cabell enrotllat del monyo: espirals."""
    return 0.55 * math.sin(x * 1.6 + y * 1.6) + 0.25 * math.sin(x * 3.1 - y * 0.7)


def _buns(fg, pts, H):
    for bx, by in pts:
        fg.ell(bx, by, 3.3, 3.1, H, 2.8, amp=1.6, cont=(0.2, 0.8), lvlfn=_bun)


def vet_hair(fg, p, spec):
    """Negre, amb ratlla al mig i dos monyos, un a cada costat del cap; les ulleres de soldar al front."""
    hx, hy = p.head
    H = HAIR_BLACK
    if p.f == 'D':
        fg.ell(hx, hy - 1.4, 7.0, 7.2, H, 2.6, amp=1.6, cont=(0.2, 0.8), lvlfn=_sleek,
               clip=lambda x, y: y <= hy - 3.4 + ((x - hx) / 7.0) ** 2 * 4.6 or abs(x - hx) > 6.2)
        for y in range(int(hy - 8), int(hy - 4)):                                  # la ratlla
            fg.shade(hx, y, -1.0, H)
        _buns(fg, ((hx - 6.6, hy - 6.4), (hx + 6.6, hy - 6.4)), H)
        fg.line(hx - 7, hy - 4, hx + 7, hy - 4, STRAP, 1.6)                         # ulleres
        for gx in (hx - 2.6, hx + 2.6):
            fg.ell(gx, hy - 4.6, 2.2, 1.8, BRASS, 2.6, amp=0.8)
            fg.ell(gx, hy - 4.6, 1.2, 1.0, LENS, 2.6, amp=0.6)
    elif p.f == 'L':
        fg.ell(hx + 1.0, hy - 1.4, 7.2, 7.2, H, 2.6, amp=1.6, cont=(0.2, 0.8), lvlfn=_sleek,
               clip=lambda x, y: (x >= hx - 1.0 or y <= hy - 4.6) and not (x < hx + 2.6 and y > hy - 1.0))
        fg.ell(hx + 0.4, hy - 8.4, 2.8, 2.6, H, 1.6, amp=1.2, cont=(0.2, 0.8), lvlfn=_bun)  # l'altre, darrere
        _buns(fg, ((hx + 3.0, hy - 7.2),), H)
        fg.line(hx - 4, hy - 4, hx + 7, hy - 3, STRAP, 1.6)
        fg.ell(hx - 5.0, hy - 4.6, 1.6, 1.9, BRASS, 2.6, amp=0.8)
        fg.px(hx - 5.4, hy - 4.6, LENS, 2.8)
    else:
        fg.ell(hx, hy - 0.8, 7.4, 7.8, H, 2.6, amp=1.6, cont=(0.2, 0.8), lvlfn=_sleek)
        for y in range(int(hy - 8), int(hy + 4)):                                  # la ratlla, fins al clatell
            fg.shade(hx, y, -1.0, H)
        _buns(fg, ((hx - 6.6, hy - 6.0), (hx + 6.6, hy - 6.0)), H)
        fg.line(hx - 7, hy - 4, hx + 7, hy - 4, STRAP, 1.6)


def _pocket(fg, x0, y0, x1, y1, lvl=2.6, mat=COVERALL):
    for y in range(int(y0), int(y1) + 1):
        for x in range(int(x0), int(x1) + 1):
            edge = x in (int(x0), int(x1)) or y == int(y1)
            fg.px(x, y, mat, lvl - (0.9 if edge else 0) + (0.5 if y == int(y0) else 0))


def vet_over(fg, p, spec):
    """Granota: cremallera, dues butxaques al pit (en una, un tornavís), el cinturó."""
    b = p.bob
    if p.f == 'D':
        for y in range(29 + b, 49 + b):
            fg.shade(24.5, y, -0.9, COVERALL)
        _pocket(fg, 17, 33 + b, 21, 38 + b)
        _pocket(fg, 27, 33 + b, 31, 38 + b)
        fg.px(28, 31 + b, YELLOWH, 2.6); fg.px(28, 32 + b, YELLOWH, 2.0)            # el tornavís
        for x in range(16, 33):
            fg.px(x, 47 + b, STRAP, 2.0)
        fg.px(24, 47 + b, BRASS, 3.0); fg.px(25, 47 + b, BRASS, 2.4)
    elif p.f == 'L':
        _pocket(fg, 20, 33 + b, 23, 38 + b)
        fg.px(21, 31 + b, YELLOWH, 2.6); fg.px(21, 32 + b, YELLOWH, 2.0)
        for x in range(20, 32):
            fg.px(x, 47 + b, STRAP, 2.0)
    else:
        for x in range(16, 33):
            fg.px(x, 47 + b, STRAP, 2.0)


def vet_arm(fg, p, spec, i):
    """Mànigues arremangades: el puny gruixut al colze."""
    e = p.arms[i][1] if p.f == 'L' else p.elbow[i]
    fg.ell(e[0], e[1] - 0.5, 3.2, 2.0, COVERALL, 3.2, amp=1.4, cont=(0.2, 0.8))


def vet_leg(fg, p, spec, i):
    """Butxaca de cama, a cada cuixa."""
    h, k = p.hip[i], p.knee[i]
    x = (h[0] + k[0]) / 2 + (-1.5 if i == 0 else 1.5)
    y = (h[1] + k[1]) / 2
    _pocket(fg, x - 1.5, y - 2, x + 1.5, y + 2, 2.4)


def vet_leg_side(fg, p, spec, leg, dl):
    h, k, a, pitch = leg
    if dl == 0:
        x, y = (h[0] + k[0]) / 2, (h[1] + k[1]) / 2
        _pocket(fg, x - 1.5, y - 2, x + 1.5, y + 2, 2.4)


VET = {
    'skin': SKIN_VET, 'legs': COVERALL, 'top': COVERALL, 'forearm': SKIN_VET, 'shoes': BOOT, 'lashes': True,
    'iris': (60, 36, 26), 'brow': (26, 14, 14), 'lip': (150, 40, 52), 'thin': 0.5,   # la cara de la Vet, la de sempre
    'hooks': {'hair': vet_hair, 'over': vet_over, 'arm': vet_arm, 'leg_deco': vet_leg,
              'leg_deco_side': vet_leg_side},
}


# ═══════════════════════════════════════════════════════════════════════════
#  Secundaris: ajudes
# ═══════════════════════════════════════════════════════════════════════════

def _curls(x, y):
    return -0.9 if (int(x * 0.9) + int(y * 0.9)) % 3 == 0 else 0.35 * math.sin(x * 2.3 + y * 1.7)


def hair_cap(mat, top=-8.0, fringe=0.0, curls=False, big_=0.0, lvl=2.4, lvlfn=None):
    """Cabell curt: un casc. Amb `curls`, rínxols; `big_` el fa més voluminós."""
    lv = _curls if curls else lvlfn

    def hook(fg, p, spec):
        hx, hy = p.head
        kw = {'lvlfn': lv} if lv else {}
        r = 7.4 + big_
        if p.f == 'D':
            line = lambda x, y: y <= hy - 3.2 + fringe + ((x - hx) / 7) ** 2 * 4.0  # noqa: E731
            fg.ell(hx, hy - 1.0 - big_ * 0.5, r, r, mat, lvl, amp=1.6, clip=line, cont=(0.2, 0.8), **kw)
        elif p.f == 'L':
            line = lambda x, y: (x >= hx - 2.5 or y <= hy - 4.6 + fringe * 0.6) and not (x < hx + 2.5 and y > hy - 1.0)  # noqa: E731
            fg.ell(hx + 1.2, hy - 1.0 - big_ * 0.5, r - 0.2, r + 0.2, mat, lvl, amp=1.6, clip=line, cont=(0.2, 0.8), **kw)
        else:
            fg.ell(hx, hy - 0.6 - big_ * 0.5, r, r + 0.6, mat, lvl, amp=1.6, cont=(0.2, 0.8), **kw)
    return hook


def _eye_box(fg, p):
    """On són els ulls, en píxels reals de la figura: (x esquerre del primer ull, x del segon, fila, ample)."""
    hx, hy = p.head
    if big(fg):
        ey = round(f(int(hy + 0.5)))
        if p.f == 'L':
            return round(f(int(hx - 3.5))) - 1, None, ey, 3
        return round(f(hx - 3.0)) - 1, round(f(hx + 3.0)) - 1, ey, 3
    ey = int(hy + 0.5)
    if p.f == 'L':
        return int(hx - 3.5) - 1, None, ey, 2
    return int(hx - 3.5), int(hx + 2.5), ey, 2


def _rp(fg, X, Y, mat, lvl):
    """Píxel real a les dues mides."""
    if big(fg):
        fg.rpx(X, Y, mat, lvl)
    elif hasattr(fg, 'rset'):                            # FigL2: un píxel de ×1, un bloc
        fg.rset(X, Y, (mat, lvl))
    else:
        X, Y = int(round(X)), int(round(Y))
        if 0 <= X < fg.w and 0 <= Y < fg.h:
            fg.buf[Y][X] = (mat, lvl)


def glasses(frame=STEELB, rnd=True, lvl=1.6):
    """Ulleres: la muntura d'un píxel al voltant de cada ull (els ulls es veuen a dins) i el pont."""
    def hook(fg, p, spec):
        if p.f == 'U':
            return
        x0, x1, ey, w = _eye_box(fg, p)
        for xa in [x for x in (x0, x1) if x is not None]:
            if p.f == 'L':
                xa -= 0
            for X in range(xa, xa + w):
                _rp(fg, X, ey - 2, frame, lvl + 0.6)
                _rp(fg, X, ey + 1, frame, lvl)
            for Y in range(ey - (1 if rnd else 2), ey + (1 if not rnd else 1)):
                _rp(fg, xa - 1, Y, frame, lvl)
                _rp(fg, xa + w, Y, frame, lvl - 0.3)
            if not rnd:
                _rp(fg, xa - 1, ey - 2, frame, lvl); _rp(fg, xa + w, ey - 2, frame, lvl)
                _rp(fg, xa - 1, ey + 1, frame, lvl); _rp(fg, xa + w, ey + 1, frame, lvl)
        if p.f == 'D':
            for X in range(x0 + w + 1, x1 - 1):
                _rp(fg, X, ey - 1, frame, lvl)
        else:
            hx, hy = p.head
            X1 = (f(hx + 2.0) if big(fg) else hx + 2.0)
            n = int(X1 - (x0 + w + 1)) + 1
            for k in range(max(0, n)):
                _rp(fg, x0 + w + 1 + k, ey - 1, frame, lvl - 0.2)
    return hook


def _coat_skirt(p, bot, flare, top=46):
    """Les vores d'una faldilla o d'un abric (de la cintura a `bot`), que segueixen les cames."""
    b = p.bob
    top = top + b
    if p.f == 'L':
        xs = [leg[1][0] for leg in p.legs]                                          # els genolls
        front = min(min(xs) - 4.0, 20.6)
        back = max(max(xs) + 4.0, 30.6)

        def e(y):
            t = max(0.0, min(1.0, (y - top) / max(1, bot - top)))
            return (20.6 + (front - 20.6 - flare * 0.4) * t, 30.6 + (back - 30.6 + flare * 0.6) * t)
        return top, bot, e
    lift = getattr(p, 'lift', [0, 0])

    def e(y):
        t = max(0.0, min(1.0, (y - top) / max(1, bot - top)))
        w = 8.4 + flare * t
        sway = (lift[1] - lift[0]) * 0.3 * t
        return (24.5 - w + sway, 24.5 + w + sway)
    return top, bot, e


def coat(mat, bot, flare, lvl=2.6, lvlfn=None, split=True):
    """Un abric llarg (ganxo `torso`): tapa les cames fins a `bot`."""
    def hook(fg, p, spec):
        top, b, e = _coat_skirt(p, bot, flare)
        fg.lathe(top, b, e, mat, lvl, amp=1.6, lvlfn=lvlfn, cont=(0.0, 0.6))
        if split and p.f == 'D':
            l, r = e(b)
            mid = (l + r) / 2
            for y in range(int(top) + 1, int(b) + 1):
                fg.shade(mid + 0.5, y, -1.0, mat)
                fg.shade(mid - 0.5, y, +0.4, mat)
        if p.f == 'L':
            l, r = e(b)
            for y in range(int(top) + 4, int(b) + 1):                               # un plec
                fg.shade(l + (r - l) * 0.55, y, -0.8, mat)
    return hook


def _chair(wood):
    """Una cadira de fusta (de perfil, el respatller darrere), sota una figura asseguda de perfil."""
    def hook(fg, p, spec):
        if not hasattr(p, 'hip_y') or 'seated' not in spec:
            return
        sy = p.hip_y + 3.6
        fg.poly([(15.0, sy), (34.0, sy), (34.0, sy + 2.0), (15.0, sy + 2.0)], wood, 2.8, amp=0.6, cont=(0.0, 0.8))
        for x, d in ((16.5, 0.0), (32.5, -0.5), (19.0, -1.2)):
            fg.limb((x, sy + 2), (x, 82.5), 0.9, 0.9, wood, 2.2 + d, cont=(0.0, 0.6))
        fg.limb((33.0, sy + 1), (34.5, sy - 22), 1.0, 1.0, wood, 2.4, cont=(0.0, 0.6))   # el respatller
        for yy in (sy - 20, sy - 14):
            fg.limb((31.0, yy), (34.6, yy - 0.3), 1.0, 1.0, wood, 2.8, cont=(0.0, 0.6))
        fg.limb((15.5, sy + 9), (32.5, sy + 9), 0.6, 0.6, wood, 1.8)
    return hook


WOOD = M((22, 12, 10), (46, 26, 18), (78, 46, 28), (112, 70, 40), (146, 98, 58), (178, 130, 82), dith=0.0)
WOOD_PALE = M((34, 26, 22), (70, 54, 40), (110, 88, 62), (150, 124, 88), (188, 162, 118), (218, 198, 156), dith=0.0)


def seated(spec, hipy=61, wood=WOOD):
    """La mateixa persona, asseguda de perfil en una cadira (la cadira forma part del sprite)."""
    hk = dict(spec.get('hooks', {}))
    hk['hair_back'] = hooks(_chair(wood), *([hk['hair_back']] if 'hair_back' in hk else []))
    return dict(spec, seated=hipy, hooks=hk)


# ═══════════════════════════════════════════════════════════════════════════
#  Materials dels secundaris
# ═══════════════════════════════════════════════════════════════════════════

SKIN_TAN = M((50, 24, 28), (92, 50, 44), (138, 86, 62), (178, 124, 86), (208, 160, 114), (232, 196, 152))
SKIN_OLIVE = M((46, 26, 26), (84, 52, 42), (126, 86, 60), (164, 120, 82), (196, 154, 108), (222, 188, 140))
SKIN_SALLOW = M((60, 40, 46), (110, 82, 76), (160, 128, 108), (198, 168, 140), (222, 198, 170), (240, 222, 198))

NAVY_COAT = M((6, 8, 20), (12, 16, 36), (22, 28, 56), (34, 44, 80), (50, 62, 104), (72, 86, 130), dith=0.0)
CAP_NAVY = M((6, 6, 16), (12, 14, 30), (22, 26, 48), (36, 42, 70), (54, 62, 94))
VISOR = M((4, 4, 6), (10, 10, 14), (22, 22, 28), (46, 46, 54), (90, 90, 100))
PATCH_BLACK = M((4, 2, 4), (10, 6, 8), (20, 14, 16), (34, 26, 28))

ORANGE_SUIT = M((50, 16, 10), (100, 34, 14), (156, 62, 18), (206, 98, 28), (236, 138, 52), (250, 184, 106), dith=0.0)
BANDANA = M((60, 6, 10), (120, 16, 20), (184, 32, 32), (226, 66, 54), (248, 120, 100))

VEST = M((26, 24, 14), (50, 46, 26), (80, 74, 42), (112, 104, 62), (144, 136, 86), (176, 168, 116), dith=0.0)
SHIRT_LB = M((40, 50, 66), (78, 94, 114), (118, 136, 156), (160, 176, 192), (196, 208, 218), (226, 234, 238))
CORD = M((18, 12, 10), (34, 24, 20), (54, 40, 32), (76, 58, 44), (100, 80, 60), (128, 104, 80), dith=0.0)
RUBBER_G = M((6, 18, 12), (12, 36, 22), (22, 60, 36), (38, 88, 52), (62, 120, 74), (110, 166, 116))
HAIR_GREY = M((40, 40, 46), (74, 74, 80), (110, 110, 114), (146, 146, 148), (182, 182, 182), (214, 214, 212))
PENCIL = M((90, 60, 6), (170, 120, 14), (236, 184, 40), (255, 228, 120))
ERASER = M((90, 30, 40), (170, 70, 80), (230, 130, 140))

APRON = M((24, 12, 8), (48, 24, 14), (78, 42, 22), (110, 64, 34), (142, 90, 50), (172, 120, 72), dith=0.0)
SHIRT_DARK = M((14, 14, 18), (26, 26, 32), (42, 42, 50), (62, 62, 70), (86, 86, 94), dith=0.0)
WORK_BROWN = M((16, 12, 12), (30, 22, 20), (48, 36, 30), (68, 52, 42), (92, 72, 58), dith=0.0)
MOUSTACHE = M((50, 50, 56), (96, 96, 102), (146, 146, 150), (190, 190, 192), (224, 224, 224))

TEAL = M((4, 30, 32), (10, 66, 70), (22, 112, 116), (48, 160, 160), (110, 206, 200))
MOP_STICK = M((40, 44, 56), (90, 98, 110), (150, 158, 168), (210, 216, 222))
MOP_HEAD = M((60, 60, 70), (120, 120, 126), (176, 174, 170), (220, 216, 206), (244, 240, 230))

HELMET = M((70, 44, 4), (140, 96, 10), (206, 152, 22), (240, 196, 46), (254, 230, 110), (255, 248, 190), dith=0.0)
LAMP = M((120, 110, 70), (220, 210, 150), (255, 248, 200), (255, 255, 240))
WORN = M((22, 20, 16), (44, 38, 30), (70, 62, 48), (98, 88, 68), (126, 116, 92), (156, 146, 120), dith=0.0)
HIVIS_D = M((70, 70, 70), (120, 120, 116), (170, 168, 158), (206, 204, 192))
HAIR_RED = M((40, 8, 8), (90, 20, 14), (144, 40, 22), (190, 66, 34), (222, 102, 56), (244, 150, 98))
TROUSER_G = M((14, 16, 18), (26, 28, 32), (40, 44, 48), (58, 62, 66), (80, 84, 86), dith=0.0)

STRAW = M((70, 50, 16), (130, 96, 34), (184, 146, 64), (218, 186, 100), (240, 216, 140), (252, 240, 190))
GARDEN = M((8, 22, 12), (16, 42, 22), (28, 66, 34), (44, 94, 48), (66, 124, 64), (98, 156, 88), dith=0.0)
SHEARS_R = M((60, 6, 8), (130, 20, 20), (196, 46, 36), (236, 96, 76))

WHITE_SUIT = M((60, 58, 72), (108, 108, 120), (156, 156, 164), (200, 198, 198), (228, 226, 220), (246, 244, 236), (255, 254, 248), dith=0.0)
DIRTY = M((52, 46, 44), (96, 88, 78), (140, 132, 116), (176, 168, 150), (202, 196, 178), (222, 216, 200), (236, 232, 218), dith=0.0)
TIE_GOLD = M((70, 44, 10), (140, 98, 22), (204, 158, 44), (244, 210, 100), (255, 242, 180))
TAN_SHOE = M((24, 14, 10), (54, 32, 20), (92, 58, 34), (132, 90, 52), (170, 126, 80))

SUIT_GREY = M((18, 18, 22), (34, 34, 40), (52, 52, 58), (72, 72, 78), (96, 96, 102), (124, 124, 130), dith=0.0)
TIE_DARK = M((8, 12, 24), (16, 24, 46), (30, 42, 74), (52, 66, 104))
SHIRT_W = M((80, 84, 96), (140, 144, 154), (196, 198, 204), (230, 232, 234), (250, 250, 250))
HAIR_GEL = M((6, 4, 4), (14, 10, 10), (26, 20, 18), (42, 34, 30), (66, 56, 50), (120, 112, 106))
BLACK_SHOE = M((6, 6, 8), (14, 14, 18), (26, 26, 32), (44, 44, 52), (80, 80, 90))

FUR_BLUE = M((8, 14, 44), (16, 30, 84), (30, 54, 130), (48, 86, 172), (80, 124, 206), (130, 170, 232), (186, 210, 248), dith=0.15)
HAIR_LILAC = M((60, 54, 80), (104, 96, 126), (150, 142, 170), (192, 184, 206), (222, 216, 232), (244, 240, 250))
PEARL = M((120, 116, 120), (190, 186, 186), (236, 232, 226), (255, 255, 250))
STOCKING = M((12, 10, 16), (24, 20, 30), (40, 34, 48), (58, 52, 68), (80, 74, 92), dith=0.0)
MASK_GOLD = M((60, 36, 8), (126, 86, 20), (196, 150, 40), (240, 206, 90), (255, 244, 170))

KNIT = M((40, 26, 12), (76, 52, 24), (116, 84, 40), (152, 116, 58), (184, 150, 82), (210, 182, 116), dith=0.0)
TWEED = M((20, 18, 16), (40, 36, 32), (64, 58, 50), (90, 82, 70), (118, 108, 92))
UMBRELLA = M((4, 4, 8), (12, 12, 18), (24, 24, 34), (40, 40, 54), (64, 64, 80))


# ═══════════════════════════════════════════════════════════════════════════
#  Capitana Or: abric de capità, gorra vella, pegat a l'ull
# ═══════════════════════════════════════════════════════════════════════════

def captain_cap(fg, p, spec):
    """Gorra de plat blau marí, gastada, amb la visera negra i l'àncora de llautó."""
    hx, hy = p.head
    if p.f == 'L':
        fg.ell(hx + 1.2, hy - 6.6, 8.0, 3.6, CAP_NAVY, 2.6, amp=1.4, cont=(0.2, 0.9),
               lvlfn=lambda x, y: -0.4 if (int(x) + int(y)) % 5 == 0 else 0)
        fg.poly([(hx - 5.0, hy - 5.2), (hx + 7.4, hy - 5.2), (hx + 7.2, hy - 3.6), (hx - 5.0, hy - 3.6)], CAP_NAVY, 1.8)
        fg.poly([(hx - 5.2, hy - 4.6), (hx - 9.4, hy - 3.4), (hx - 9.0, hy - 2.4), (hx - 4.6, hy - 3.2)], VISOR, 2.2,
                cont=(0.0, 0.6))
        fg.ell(hx - 3.0, hy - 6.6, 1.0, 1.0, BRASS, 3.0, amp=0.8)
    elif p.f == 'D':
        fg.ell(hx, hy - 7.2, 8.6, 3.4, CAP_NAVY, 2.6, amp=1.4, cont=(0.2, 0.9),
               lvlfn=lambda x, y: -0.4 if (int(x) + int(y)) % 5 == 0 else 0)
        fg.poly([(hx - 6.6, hy - 6.0), (hx + 6.6, hy - 6.0), (hx + 6.4, hy - 4.0), (hx - 6.4, hy - 4.0)], CAP_NAVY, 1.8)
        fg.ell(hx, hy - 3.4, 6.2, 1.3, VISOR, 2.0, amp=1.0)
        fg.ell(hx, hy - 7.0, 1.2, 1.2, BRASS, 3.0, amp=0.8)
        dot(fg, hx - 0.4, hy - 7.4, CREAM, 4.0)
    else:
        fg.ell(hx, hy - 7.0, 8.6, 3.6, CAP_NAVY, 2.4, amp=1.4, cont=(0.2, 0.9))
        fg.poly([(hx - 6.8, hy - 5.8), (hx + 6.8, hy - 5.8), (hx + 6.6, hy - 3.8), (hx - 6.6, hy - 3.8)], CAP_NAVY, 1.6)


def capitana_hair(fg, p, spec):
    """Cabell blanc curt; d'esquena, només el clatell (la resta, sota la gorra)."""
    if p.f == 'U':
        hx, hy = p.head
        fg.ell(hx, hy + 1.0, 7.0, 6.6, HAIR_WHITE, 1.9, amp=1.2, cont=(0.2, 0.8),
               lvlfn=lambda x, y: -0.6 if int(x) % 2 == 0 else 0, clip=lambda x, y: y >= hy - 2.5)
    else:
        hair_cap(HAIR_WHITE, fringe=-0.4, lvl=1.9)(fg, p, spec)


def eye_patch(fg, p, spec):
    """El pegat a l'ull (el de la dreta de la Capitana, el de l'esquerra de la imatge) i la cinta."""
    if p.f == 'U':
        hx, hy = p.head
        fg.line(hx - 7, hy - 1, hx + 7, hy - 2.6, PATCH_BLACK, 2.0)
        return
    hx, hy = p.head
    ey = int(hy + 0.5)
    if p.f == 'D':
        cx = int(hx - 3.5) + 0.5
        fg.ell(cx, ey - 0.2, 2.0, 1.8, PATCH_BLACK, 2.2, amp=1.0)
        fg.line(cx - 1.5, ey - 1.4, hx - 7.0, ey - 3.0, PATCH_BLACK, 1.6)
        fg.line(cx + 1.5, ey - 1.6, hx + 6.5, ey - 5.0, PATCH_BLACK, 1.6)
    else:
        cx = int(hx - 3.5) + 0.3
        fg.ell(cx, ey - 0.2, 1.6, 1.8, PATCH_BLACK, 2.2, amp=1.0)
        fg.line(cx + 1.2, ey - 1.4, hx + 6.0, ey - 3.2, PATCH_BLACK, 1.6)


def capitana_over(fg, p, spec):
    """Abric de capità: dues fileres de botons de llautó, solapes i galons a les mànigues."""
    b = p.bob
    if p.f == 'D':
        for y in range(29 + b, 46 + b):
            fg.shade(24.5, y, -0.9, NAVY_COAT)
        fg.poly([(19.5, 29 + b), (24.5, 38 + b), (23.0, 29 + b)], NAVY_COAT, 3.6)            # solapes
        fg.poly([(29.5, 29 + b), (24.5, 38 + b), (26.0, 29 + b)], NAVY_COAT, 3.0)
        for y in (37, 42, 47, 52):
            for x in (21, 28):
                fg.px(x, y + b, BRASS, 3.0)
    elif p.f == 'L':
        fg.poly([(20.0, 29 + b), (24.0, 30 + b), (21.0, 38 + b)], NAVY_COAT, 3.6)
        for y in (37, 42, 47, 52):
            fg.px(21, y + b, BRASS, 3.0)
    else:
        fg.ell(24.5, 29 + b, 6.6, 2.6, NAVY_COAT, 2.6, amp=1.2, cont=(0.2, 0.8))
        for y in range(48 + b, 70 + b):
            fg.shade(24.5, y, -1.0, NAVY_COAT)
        fg.px(22, 47 + b, BRASS, 2.6); fg.px(27, 47 + b, BRASS, 2.6)


def capitana_arm(fg, p, spec, i):
    w = p.arms[i][2] if p.f == 'L' else p.wrist[i]
    e = p.arms[i][1] if p.f == 'L' else p.elbow[i]
    t = 0.8
    x, y = e[0] + (w[0] - e[0]) * t, e[1] + (w[1] - e[1]) * t
    fg.ell(x, y, 2.6, 0.8, BRASS, 2.4, amp=0.8)


CAPITANA = {
    'skin': SKIN_OLD, 'legs': TROUSER, 'top': NAVY_COAT, 'shoes': BOOT, 'brow': (190, 190, 196), 'thin': -0.3,
    'iris': (70, 90, 110), 'lip': (150, 84, 84),
    'hooks': {'hair': hooks(capitana_hair, captain_cap, eye_patch),
              'torso': coat(NAVY_COAT, 70, 3.4), 'over': capitana_over, 'arm': capitana_arm},
}


# ═══════════════════════════════════════════════════════════════════════════
#  Tomàs: granota taronja massa gran, mocador vermell, cabell negre arrissat
# ═══════════════════════════════════════════════════════════════════════════

def tomas_collar(fg, p, spec):
    """El mocador vermell al coll, amb el nus."""
    b = p.bob
    if p.f == 'D':
        fg.poly([(19.0, 27.8 + b), (30.0, 27.8 + b), (24.5, 34.0 + b)], BANDANA, 2.8, amp=0.8, cont=(0.0, 0.7))
        fg.ell(24.5, 28.6 + b, 5.6, 1.8, BANDANA, 2.4, amp=1.0)
        fg.px(22, 30 + b, BANDANA, 4.0); fg.px(26, 29 + b, BANDANA, 4.0)
    elif p.f == 'L':
        fg.ell(25.5, 28.6 + b, 4.6, 1.8, BANDANA, 2.6, amp=1.0)
        fg.poly([(21.0, 28.0 + b), (19.4, 32.8 + b), (23.0, 30.0 + b)], BANDANA, 2.8)
    else:
        fg.ell(24.5, 28.4 + b, 6.0, 1.9, BANDANA, 2.4, amp=1.0)
        fg.poly([(23.5, 29 + b), (25.5, 29 + b), (26.4, 32.6 + b), (22.6, 32.6 + b)], BANDANA, 2.2)


def tomas_over(fg, p, spec):
    """La granota: cremallera, butxaca al pit, el nom brodat i plecs (li va gran)."""
    b = p.bob
    if p.f == 'D':
        for y in range(33 + b, 52 + b):
            fg.shade(24.5, y, -0.8, ORANGE_SUIT)
        _pocket(fg, 27, 35 + b, 30, 39 + b, 3.0, ORANGE_SUIT)
        for x in (18, 19, 20):
            fg.px(x, 36 + b, CREAM, 2.0)
        for y in range(44 + b, 50 + b):
            fg.shade(19, y, -0.7, ORANGE_SUIT); fg.shade(30, y, -0.7, ORANGE_SUIT)
    elif p.f == 'L':
        _pocket(fg, 20, 35 + b, 22, 39 + b, 3.0, ORANGE_SUIT)
        for y in range(42 + b, 50 + b):
            fg.shade(26, y, -0.7, ORANGE_SUIT)


def tomas_leg(fg, p, spec, i):
    """Els camals doblegats als turmells."""
    a = p.ankle[i]
    fg.ell(a[0], a[1] - 1.4, 3.3, 1.4, ORANGE_SUIT, 3.0, amp=1.0, cont=(0.1, 0.6))


def tomas_leg_side(fg, p, spec, leg, dl):
    a = leg[2]
    fg.ell(a[0] + 0.2, a[1] - 1.4, 3.0, 1.4, ORANGE_SUIT, 3.0 + dl, amp=1.0, cont=(0.1, 0.6))


def tomas_arm(fg, p, spec, i):
    """Les mànigues, llargues: li tapen mitja mà."""
    w = p.arms[i][2] if p.f == 'L' else p.wrist[i]
    fg.ell(w[0] - (0.4 if p.f == 'L' else 0), w[1] + 0.6, 2.9, 1.6, ORANGE_SUIT, 2.4 if i == 0 else 2.0, amp=1.0,
           cont=(0.1, 0.6))


TOMAS = {
    'skin': SKIN_TAN, 'legs': ORANGE_SUIT, 'top': ORANGE_SUIT, 'shoes': GRAY_SHOE, 'thin': 1.0,
    'iris': (40, 26, 20), 'brow': (14, 10, 12), 'lip': (140, 70, 66),
    'hooks': {'hair': hair_cap(HAIR_BLACK, curls=True, big_=0.8, lvl=2.6), 'collar': tomas_collar,
              'over': tomas_over, 'arm': tomas_arm, 'leg_deco': tomas_leg, 'leg_deco_side': tomas_leg_side},
}


# ═══════════════════════════════════════════════════════════════════════════
#  Juana: cabell gris recollit amb un llapis, ulleres rodones, armilla de pescador, botes d'aigua
# ═══════════════════════════════════════════════════════════════════════════

def juana_hair(fg, p, spec):
    hx, hy = p.head
    H = HAIR_GREY
    wave = lambda x, y: 0.4 * math.sin(x * 1.4 + y * 0.6)  # noqa: E731
    if p.f == 'D':
        fg.ell(hx + 1.0, hy - 9.4, 3.4, 2.8, H, 2.6, amp=1.4, cont=(0.2, 0.8), lvlfn=wave)          # el monyo, darrere
        fg.line(hx - 3.0, hy - 13.0, hx + 5.0, hy - 8.0, PENCIL, 2.6)
        fg.px(hx - 3.0, hy - 13.0, ERASER, 2.4)
        hair_cap(H, fringe=-0.6, lvl=2.6, lvlfn=wave)(fg, p, spec)
        fg.ell(hx - 5.2, hy - 2.6, 1.6, 2.6, H, 2.4, amp=1.0)                       # un floc escapat
    elif p.f == 'L':
        hair_cap(H, fringe=-0.6, lvl=2.6, lvlfn=wave)(fg, p, spec)
        fg.ell(hx + 6.6, hy - 5.0, 3.4, 3.4, H, 2.6, amp=1.4, cont=(0.2, 0.8), lvlfn=wave)
        fg.line(hx + 2.6, hy - 9.8, hx + 10.4, hy - 1.8, PENCIL, 2.6)
        fg.px(hx + 2.6, hy - 9.8, ERASER, 2.4)
    else:
        hair_cap(H, lvl=2.6, lvlfn=wave)(fg, p, spec)
        fg.ell(hx, hy - 4.0, 3.8, 3.4, H, 2.8, amp=1.4, cont=(0.2, 0.8),
               lvlfn=lambda x, y: 0.6 * math.sin(math.atan2(y - hy + 4, x - hx) * 3))
        fg.line(hx - 5.0, hy - 7.6, hx + 4.4, hy - 1.6, PENCIL, 2.6)
        fg.px(hx - 5.0, hy - 7.6, ERASER, 2.4)


def juana_over(fg, p, spec):
    """L'armilla de pescador (oberta, amb quatre butxaques) damunt la camisa."""
    b = p.bob
    if p.f == 'D':
        fg.poly([(22.0, 28 + b), (27.0, 28 + b), (26.2, 52 + b), (22.8, 52 + b)], SHIRT_LB, 2.8, amp=0.6)
        for y in range(31 + b, 51 + b, 4):
            fg.px(24.5, y, SHIRT_LB, 1.6)
        for x0, y0 in ((17, 33), (27, 33), (17, 41), (27, 41)):
            _pocket(fg, x0, y0 + b, x0 + 4, y0 + 5 + b, 2.6, VEST)
        fg.shade(22, 40 + b, -0.6)
    elif p.f == 'L':
        fg.poly([(19.6, 30 + b), (21.6, 30 + b), (21.2, 50 + b), (19.8, 50 + b)], SHIRT_LB, 2.6)
        for y0 in (33, 41):
            _pocket(fg, 21, y0 + b, 25, y0 + 5 + b, 2.6, VEST)
    else:
        for y in range(33 + b, 50 + b, 3):
            for x in range(17, 32, 3):
                fg.shade(x + (y // 3) % 2, y, -0.5, VEST)


def _boot(fg, k, a, mat, lvl):
    t = 0.35
    top = (k[0] + (a[0] - k[0]) * t, k[1] + (a[1] - k[1]) * t)
    fg.limb(top, a, 3.4, 3.0, mat, lvl, cont=(0.2, 0.8))
    fg.ell(top[0], top[1], 3.6, 1.2, mat, lvl + 0.6, amp=1.0)


def juana_leg(fg, p, spec, i):
    _boot(fg, p.knee[i], p.ankle[i], RUBBER_G, 2.4 - (0.4 if i else 0))


def juana_leg_side(fg, p, spec, leg, dl):
    _boot(fg, leg[1], leg[2], RUBBER_G, 2.4 + dl)


JUANA = {
    'skin': SKIN_PALE, 'legs': CORD, 'top': VEST, 'sleeve': SHIRT_LB, 'shoes': RUBBER_G, 'thin': 0.6,
    'brow': (110, 104, 104), 'iris': (60, 90, 70), 'lip': (166, 96, 96),
    'hooks': {'hair': hooks(juana_hair, glasses(STEELB, True, 1.4)), 'over': juana_over,
              'leg_deco': juana_leg, 'leg_deco_side': juana_leg_side},
}


# ═══════════════════════════════════════════════════════════════════════════
#  Bru: corpulent, calb, bigoti gris, davantal de cuir de fonedor
# ═══════════════════════════════════════════════════════════════════════════

def bru_hair(fg, p, spec):
    """Calb: una corona de cabell gris curt al voltant del clatell, i el bigoti."""
    hx, hy = p.head
    S = spec['skin']
    H = MOUSTACHE
    if p.f == 'D':
        for sx in (-1, 1):
            fg.ell(hx + sx * 6.4, hy - 0.4, 1.4, 3.0, H, 2.0, amp=1.0)
        fg.shade(hx - 2.5, hy - 5.5, +0.8, S); fg.shade(hx - 1.5, hy - 6.0, +0.8, S)   # la lluentor de la closca
        ey = int(hy + 0.5)
        fg.poly([(hx - 3.6, ey + 3.4), (hx + 3.6, ey + 3.4), (hx + 4.2, ey + 5.6), (hx + 1.0, ey + 4.6),
                 (hx - 1.0, ey + 4.6), (hx - 4.2, ey + 5.6)], H, 2.6, amp=0.6, cont=(0.0, 0.6))
    elif p.f == 'L':
        fg.ell(hx + 4.8, hy + 0.4, 3.0, 3.4, H, 2.0, amp=1.0, clip=lambda x, y: x > hx + 3.4)
        fg.shade(hx - 1.5, hy - 6.0, +0.8, S); fg.shade(hx - 0.5, hy - 6.5, +0.8, S)
        ey = int(hy + 0.5)
        fg.poly([(hx - 6.6, ey + 3.4), (hx - 3.0, ey + 3.4), (hx - 3.0, ey + 5.0), (hx - 7.0, ey + 5.6)], H, 2.6)
    else:
        fg.ell(hx, hy + 2.0, 6.8, 5.6, H, 1.8, amp=1.2, cont=(0.2, 0.8), clip=lambda x, y: y >= hy + 0.5,
               lvlfn=lambda x, y: -0.5 if int(x) % 2 == 0 else 0)
        fg.shade(hx - 1.5, hy - 5.5, +0.8, S)


def bru_over(fg, p, spec):
    """El davantal de cuir, gruixut, del pit als genolls, penjat del coll."""
    b = p.bob
    lift = getattr(p, 'lift', [0, 0])
    if p.f == 'D':
        sway = (lift[1] - lift[0]) * 0.3
        fg.poly([(18.0, 33 + b), (31.0, 33 + b), (32.6, 46 + b), (33.0 + sway, 69 + b), (16.0 + sway, 69 + b),
                 (16.4, 46 + b)], APRON, 2.6, amp=0.8, cont=(0.2, 0.9),
                normal=lambda x, y: (max(-1, min(1, (x - 24.5) / 10)), 0.0, 0.8))
        fg.line(19, 33 + b, 21, 27 + b, APRON, 1.8); fg.line(30, 33 + b, 28, 27 + b, APRON, 1.8)
        for y in range(48 + b, 69 + b):                                             # rascades i cremades
            fg.shade(21, y, -0.5, APRON)
        for x, y in ((27, 52), (20, 60), (29, 63)):
            fg.px(x, y + b, APRON, 1.0)
        for x in range(17, 33):
            fg.px(x, 47 + b, BELT, 1.8)
    elif p.f == 'L':
        k = min(leg[1][0] for leg in p.legs)
        fg.poly([(19.4, 33 + b), (22.0, 33 + b), (22.0, 69 + b), (min(18.0, k - 1.0), 69 + b), (18.6, 46 + b)],
                APRON, 2.6, amp=0.8, cont=(0.2, 0.9))
        fg.line(20, 33 + b, 27, 27 + b, APRON, 1.8)
        for x in range(19, 32):
            fg.px(x, 47 + b, BELT, 1.8)
    else:
        fg.line(18, 47 + b, 31, 47 + b, BELT, 1.6)
        fg.line(19, 28 + b, 30, 47 + b, APRON, 1.6); fg.line(30, 28 + b, 19, 47 + b, APRON, 1.6)
        fg.ell(24.5, 47 + b, 1.8, 1.4, APRON, 2.4, amp=1.0)


def bru_arm(fg, p, spec, i):
    """Avantbraços gruixuts de fonedor."""
    if p.f == 'L':
        s, e, w = p.arms[i]
    else:
        e, w = p.elbow[i], p.wrist[i]
    fg.limb(e, w, 3.2, 2.8, spec['skin'], 2.6 if i == 0 else 2.1, cont=(0.3, 1.0))
    fg.ell(e[0], e[1] - 0.6, 3.4, 1.8, SHIRT_DARK, 2.6, amp=1.2, cont=(0.2, 0.8))
    fg.ell(w[0] - (0.4 if p.f == 'L' else 0), w[1] + 2.2, 2.5, 2.7, spec['skin'], 2.6 if i == 0 else 2.1, amp=1.4)


BRU = {
    'skin': SKIN_RUDDY, 'legs': WORK_BROWN, 'top': SHIRT_DARK, 'forearm': SKIN_RUDDY, 'shoes': BOOT, 'thin': -2.0,
    'brow': (120, 120, 124), 'iris': (60, 50, 40), 'lip': (150, 70, 66),
    'hooks': {'hair': bru_hair, 'over': bru_over, 'arm': bru_arm},
}


# ═══════════════════════════════════════════════════════════════════════════
#  Lia: uniforme blanc de servei, cabell negre curt, pal de fregar
# ═══════════════════════════════════════════════════════════════════════════

def lia_hair(fg, p, spec):
    hx, hy = p.head
    hair_cap(HAIR_BLACK, fringe=1.2, lvl=2.6, lvlfn=_sleek)(fg, p, spec)
    if p.f == 'D':
        fg.poly([(hx - 6.6, hy - 5.0), (hx + 1.0, hy - 6.6), (hx - 2.0, hy - 2.4), (hx - 6.8, hy - 1.2)], HAIR_BLACK, 3.0)
        for sx in (-1, 1):
            fg.ell(hx + sx * 6.6, hy + 1.0, 1.4, 3.4, HAIR_BLACK, 2.2, amp=1.0)
    elif p.f == 'L':
        fg.ell(hx + 3.4, hy + 0.8, 3.0, 3.6, HAIR_BLACK, 2.4, amp=1.2, clip=lambda x, y: x > hx + 1.6)


def lia_over(fg, p, spec):
    """La túnica blanca de servei amb el coll i els botons turquesa (els colors del palau)."""
    b = p.bob
    if p.f == 'D':
        fg.ell(24.5, 28.4 + b, 5.0, 1.8, TEAL, 2.6, amp=1.0)
        for y in range(30 + b, 52 + b):
            fg.px(26.5, y, WHITE, 3.0 if y % 4 else 1.6)
        for y in (33, 38, 43):
            fg.px(27, y + b, TEAL, 2.6)
        for x in range(16, 33):
            fg.px(x, 52 + b, TEAL, 2.0)
    elif p.f == 'L':
        fg.ell(25.5, 28.4 + b, 4.2, 1.8, TEAL, 2.6, amp=1.0)
        for y in (33, 38, 43):
            fg.px(20, y + b, TEAL, 2.6)
        for x in range(20, 32):
            fg.px(x, 52 + b, TEAL, 2.0)
    else:
        fg.ell(24.5, 28.2 + b, 6.0, 1.8, TEAL, 2.4, amp=1.0)
        for x in range(16, 33):
            fg.px(x, 52 + b, TEAL, 1.8)
    _mop(fg, p)


def _mop(fg, p):
    """El pal de fregar, a la mà: el pal cromat i el cap de fils."""
    if p.f == 'L':
        w = p.arms[0][2]
        top = (w[0] + 3.0, w[1] - 20.0)
        bot = (w[0] - 5.0, 79.0)
    else:
        w = p.wrist[1]
        top = (w[0] + 0.6, w[1] - 22.0)
        bot = (w[0] + 1.6, 79.0)
    fg.limb(top, bot, 0.7, 0.7, MOP_STICK, 2.6, amp=1.0)
    hx, hy = bot
    fg.ell(hx, hy + 1.2, 4.0, 2.6, MOP_HEAD, 2.6, amp=1.4, cont=(0.2, 0.8),
           lvlfn=lambda x, y: -0.8 if int(x) % 2 == 0 and y > hy + 0.5 else 0)
    if p.f == 'L':
        fg.ell(w[0] - 0.4, w[1] + 2.0, 2.1, 2.3, p.spec['skin'], 2.7, amp=1.4)    # la mà, davant del pal
    else:
        fg.ell(w[0], w[1] + 2.0, 2.1, 2.3, p.spec['skin'], 2.1, amp=1.4)


LIA = {
    'skin': SKIN_OLIVE, 'legs': WHITE, 'top': WHITE, 'shoes': GRAY_SHOE, 'thin': 0.8, 'lashes': True,
    'iris': (40, 28, 22), 'brow': (14, 10, 12), 'lip': (150, 74, 76),
    'hooks': {'hair': lia_hair, 'over': lia_over},
}


# ═══════════════════════════════════════════════════════════════════════════
#  Rosa: minera, casc amb llum, jaqueta de treball gastada, cabell vermellós
# ═══════════════════════════════════════════════════════════════════════════

def rosa_hair_back(fg, p, spec):
    """La mitja melena vermellosa, que surt per sota el casc."""
    hx, hy = p.head
    wave = lambda x, y: 0.5 * math.sin(x * 1.1 + y * 0.9)  # noqa: E731
    if p.f == 'D':
        for sx in (-1, 1):
            fg.ell(hx + sx * 6.4, hy + 2.8, 2.6, 5.6, HAIR_RED, 2.4, amp=1.4, cont=(0.2, 0.8), lvlfn=wave)
    elif p.f == 'L':
        fg.ell(hx + 3.8, hy + 2.6, 4.4, 6.0, HAIR_RED, 2.4, amp=1.4, cont=(0.2, 0.8), lvlfn=wave)
    else:
        fg.ell(hx, hy + 2.6, 7.6, 7.0, HAIR_RED, 2.4, amp=1.4, cont=(0.2, 0.8), lvlfn=wave)


def miner_helmet(fg, p, spec):
    """Casc groc de mina amb el llum al front."""
    hx, hy = p.head
    cx = hx + (0.8 if p.f == 'L' else 0)
    if p.f == 'U':
        fg.ell(hx, hy + 1.0, 7.8, 7.6, HAIR_RED, 2.4, amp=1.4, cont=(0.2, 0.8),
               lvlfn=lambda x, y: 0.5 * math.sin(x * 1.1 + y * 0.9) + (-0.7 if int(x) % 3 == 0 else 0))
    if p.f == 'D':
        fg.ell(hx - 5.6, hy - 1.6, 1.8, 2.4, HAIR_RED, 2.6, amp=1.0)
        fg.ell(hx + 5.6, hy - 1.6, 1.8, 2.4, HAIR_RED, 2.2, amp=1.0)
    elif p.f == 'L':
        fg.ell(hx + 3.0, hy - 1.4, 3.0, 2.0, HAIR_RED, 2.4, amp=1.0)
    fg.ell(cx, hy - 5.0, 8.0, 6.0, HELMET, 2.8, amp=1.6, cont=(0.2, 0.9), clip=lambda x, y: y <= hy - 2.6)
    fg.ell(cx, hy - 2.8, 9.0, 1.3, HELMET, 2.2, amp=1.0, cont=(0.0, 0.8))
    for y in range(int(hy - 10), int(hy - 2)):                                      # el nervi del mig
        fg.shade(cx + (0.5 if p.f != 'L' else 0), y, -0.5, HELMET)
    if p.f == 'D':
        fg.ell(hx, hy - 6.0, 2.0, 1.8, STEELB, 2.0, amp=0.8)
        fg.ell(hx, hy - 6.0, 1.3, 1.2, LAMP, 2.8, amp=0.6)
        dot(fg, hx - 0.4, hy - 6.4, LAMP, 4.0)
    elif p.f == 'L':
        fg.ell(cx - 7.4, hy - 5.6, 1.2, 1.8, STEELB, 2.0, amp=0.8)
        fg.px(cx - 8.2, hy - 5.6, LAMP, 3.6)
    else:
        fg.ell(hx, hy - 5.0, 1.6, 1.2, STRAP, 2.0, amp=0.6)                         # la bateria del llum


def rosa_over(fg, p, spec):
    """Jaqueta de treball gastada: colzes i vores pelades, banda reflectant bruta, butxaques."""
    b = p.bob
    if p.f == 'D':
        for x in range(16, 33):
            for dy in (0, 1):
                fg.px(x, 41 + b + dy, HIVIS_D, 2.0 + (0.6 if (x + dy) % 3 else -0.4))
        for y in range(29 + b, 52 + b):
            fg.shade(24.5, y, -0.9, WORN)
        _pocket(fg, 18, 45 + b, 22, 50 + b, 2.4, WORN)
        _pocket(fg, 27, 45 + b, 31, 50 + b, 2.4, WORN)
        fg.ell(24.5, 28.6 + b, 5.4, 2.0, WORN, 2.8, amp=1.0, cont=(0.2, 0.8))
    elif p.f == 'L':
        for x in range(20, 32):
            for dy in (0, 1):
                fg.px(x, 41 + b + dy, HIVIS_D, 2.0 + (0.6 if (x + dy) % 3 else -0.4))
        _pocket(fg, 21, 45 + b, 25, 50 + b, 2.4, WORN)
        fg.ell(25.5, 28.6 + b, 4.4, 2.0, WORN, 2.8, amp=1.0, cont=(0.2, 0.8))
    else:
        for x in range(16, 33):
            for dy in (0, 1):
                fg.px(x, 41 + b + dy, HIVIS_D, 1.8 + (0.6 if (x + dy) % 3 else -0.4))


def _worn(x, y):
    return 0.7 if (int(x * 3) * 7 + int(y * 3) * 13) % 29 == 0 else -0.5 if (int(x) * 5 + int(y) * 3) % 17 == 0 else 0


ROSA = {
    'skin': SKIN_PALE, 'legs': TROUSER_G, 'top': WORN, 'shoes': BOOT, 'thin': 0.0, 'blush': True,
    'brow': (130, 50, 30), 'iris': (70, 90, 60), 'lip': (160, 84, 80),
    'hooks': {'hair_back': rosa_hair_back, 'hair': miner_helmet, 'over': rosa_over},
}


# ═══════════════════════════════════════════════════════════════════════════
#  Nil: jardiner, barret de palla, granota verda, barba blanca, tisores de podar
# ═══════════════════════════════════════════════════════════════════════════

def _straw(x, y):
    return 0.5 if (int(x) + int(y)) % 2 == 0 else -0.3


def nil_hair(fg, p, spec):
    """La barba blanca i el barret de palla d'ala ampla."""
    hx, hy = p.head
    ey = int(hy + 0.5)
    beard = lambda x, y: 0.5 * math.sin(x * 2.1 + y * 1.3)  # noqa: E731
    if p.f == 'D':
        fg.ell(hx, hy + 6.0, 5.8, 4.4, HAIR_WHITE, 2.4, amp=1.2, clip=lambda x, y: y >= hy + 3.8, lvlfn=beard)
        fg.ell(hx - 2.0, ey + 3.4, 2.4, 1.0, HAIR_WHITE, 2.8, amp=1.0)
        fg.ell(hx + 2.0, ey + 3.4, 2.4, 1.0, HAIR_WHITE, 2.4, amp=1.0)
        if p.talk:
            for x in (-1, 0, 1):
                fg.px(int(hx) + x, ey + 5, C.MOUTH, 0)
        for sx in (-1, 1):
            fg.ell(hx + sx * 6.4, hy - 0.6, 1.4, 2.6, HAIR_WHITE, 2.2, amp=1.0)
        fg.ell(hx, hy - 5.6, 6.8, 4.0, STRAW, 2.6, amp=1.4, cont=(0.2, 0.9), lvlfn=_straw)
        fg.ell(hx, hy - 4.4, 7.0, 1.2, GARDEN, 2.4, amp=1.0)
        fg.ell(hx, hy - 3.4, 12.4, 2.4, STRAW, 2.6, amp=1.0, cont=(0.2, 0.9), lvlfn=_straw,
               clip=lambda x, y: y >= hy - 4.0 or abs(x - hx) > 6.0)
    elif p.f == 'L':
        fg.poly([(hx + 2.4, hy + 1.0), (hx + 2.2, hy + 6.0), (hx - 1.0, hy + 9.2), (hx - 5.4, hy + 8.4),
                 (hx - 6.4, hy + 5.8), (hx - 3.0, hy + 4.8), (hx - 0.4, hy + 2.4)], HAIR_WHITE, 2.2, lvlfn=beard)
        fg.px(hx - 5.5, ey + 3.4, HAIR_WHITE, 3.0); fg.px(hx - 4.5, ey + 3.4, HAIR_WHITE, 2.6)
        fg.ell(hx + 4.4, hy - 0.4, 2.6, 2.6, HAIR_WHITE, 2.2, amp=1.0)
        fg.ell(hx + 0.8, hy - 6.0, 6.4, 3.8, STRAW, 2.6, amp=1.4, cont=(0.2, 0.9), lvlfn=_straw)
        fg.ell(hx + 0.8, hy - 4.6, 6.6, 1.2, GARDEN, 2.4, amp=1.0)
        fg.ell(hx + 0.6, hy - 3.6, 12.0, 1.8, STRAW, 2.6, amp=1.0, cont=(0.2, 0.9), lvlfn=_straw)
    else:
        fg.ell(hx, hy + 0.4, 7.0, 4.0, HAIR_WHITE, 2.2, amp=1.0, clip=lambda x, y: y >= hy - 1.0)
        fg.ell(hx, hy - 5.6, 6.8, 4.0, STRAW, 2.4, amp=1.4, cont=(0.2, 0.9), lvlfn=_straw)
        fg.ell(hx, hy - 4.4, 7.0, 1.2, GARDEN, 2.2, amp=1.0)
        fg.ell(hx, hy - 3.2, 12.4, 2.6, STRAW, 2.4, amp=1.0, cont=(0.2, 0.9), lvlfn=_straw)


def nil_over(fg, p, spec):
    """La granota verda de jardiner: pitet amb butxaca, tirants i uns guants a la butxaca del darrere."""
    b = p.bob
    if p.f == 'D':
        _pocket(fg, 21, 35 + b, 28, 41 + b, 2.8, GARDEN)
        for sx in (19, 30):
            fg.px(sx, 33 + b, BRASS, 3.0)
        for y in range(42 + b, 52 + b):
            fg.shade(24.5, y, -0.7, GARDEN)
    elif p.f == 'L':
        _pocket(fg, 20, 35 + b, 23, 41 + b, 2.8, GARDEN)
        fg.px(22, 33 + b, BRASS, 3.0)
    else:
        _pocket(fg, 26, 50 + b, 30, 55 + b, 2.4, GARDEN)
        fg.ell(28, 50 + b, 1.8, 1.4, HELMET, 2.4, amp=0.8)                           # els guants a la butxaca


def nil_arm(fg, p, spec, i):
    """Les tisores de podar, a la mà."""
    if i != 0 or p.f == 'U':
        return
    w = p.arms[0][2] if p.f == 'L' else p.wrist[0]
    x, y = w[0] - (0.4 if p.f == 'L' else 0), w[1] + 2.2
    fg.limb((x + 0.6, y - 1.0), (x - 0.6, y + 1.8), 0.7, 0.6, SHEARS_R, 2.8)
    fg.limb((x + 1.6, y - 0.8), (x + 1.2, y + 1.8), 0.7, 0.6, SHEARS_R, 2.4)
    fg.limb((x + 0.4, y + 2.4), (x + 0.2, y + 6.8), 0.8, 0.4, STEELB, 3.0)
    fg.ell(x + 0.4, y + 0.6, 2.0, 2.0, spec['skin'], 2.6, amp=1.2)


NIL = {
    'skin': SKIN_RUDDY, 'legs': GARDEN, 'top': GARDEN, 'shoes': BOOT, 'stoop': 2, 'thin': 0.4,
    'brow': (220, 220, 220), 'iris': (60, 80, 100), 'lip': (150, 80, 76),
    'hooks': {'hair': nil_hair, 'over': nil_over, 'arm': nil_arm},
}


# ═══════════════════════════════════════════════════════════════════════════
#  Aurelià Verne: alt i prim, vestit blanc impecable, cabell blanc enrere, somriure
# ═══════════════════════════════════════════════════════════════════════════

def _comb(x, y):
    return -0.7 if int(x * 1.0 + y * 0.35) % 3 == 0 else 0.2


def verne_hair(fg, p, spec):
    """Blanc, pentinat enrere amb el pinte (les ratlles), el front alt."""
    hx, hy = p.head
    H = HAIR_WHITE
    if p.f == 'D':
        fg.ell(hx, hy - 2.2, 7.2, 6.8, H, 2.6, amp=1.6, cont=(0.2, 0.8), lvlfn=lambda x, y: -0.6 if int(x) % 2 == 0 else 0,
               clip=lambda x, y: y <= hy - 4.6 + ((x - hx) / 7) ** 2 * 5.0)
        for sx in (-1, 1):
            fg.ell(hx + sx * 6.6, hy - 1.0, 1.2, 2.6, H, 2.2, amp=1.0)
    elif p.f == 'L':
        fg.ell(hx + 1.6, hy - 1.8, 7.0, 7.0, H, 2.6, amp=1.6, cont=(0.2, 0.8), lvlfn=_comb,
               clip=lambda x, y: (x >= hx - 0.8 or y <= hy - 5.4) and not (x < hx + 2.6 and y > hy - 1.2))
        fg.ell(hx + 6.4, hy + 1.6, 1.8, 3.0, H, 2.2, amp=1.0)
    else:
        fg.ell(hx, hy - 0.8, 7.4, 7.6, H, 2.6, amp=1.6, cont=(0.2, 0.8), lvlfn=lambda x, y: -0.6 if int(x) % 2 == 0 else 0)
    if spec.get('messy'):
        for dx, dy in ((-3, -8.6), (-2, -9.4), (2, -8.8), (3, -9.6), (4, -8.4)):
            fg.px(hx + dx + (1 if p.f == 'L' else 0), hy + dy, H, 3.2 if dy < -9 else 2.4)


def verne_over(fg, p, spec):
    """Les solapes, la camisa, la corbata daurada, el mocador a la butxaca i els botons."""
    b = p.bob
    suit = spec['top']
    tie = spec.get('tie', TIE_GOLD)
    if p.f == 'D':
        fg.poly([(21.6, 28 + b), (27.4, 28 + b), (24.5, 40 + b)], SHIRT_W, 3.0)
        dx = 1.6 if spec.get('messy') else 0
        fg.poly([(24.0 + dx, 30 + b), (25.0 + dx, 30 + b), (26.0 + dx, 38 + b), (24.5 + dx, 40 + b), (23.0 + dx, 38 + b)],
                tie, 2.8, cont=(0.0, 0.6))
        fg.ell(24.5 + dx, 29.6 + b, 1.0, 0.9, tie, 3.0, amp=0.6)
        fg.poly([(19.4, 28 + b), (21.4, 28 + b), (24.0, 41 + b), (22.6, 41 + b)], suit, 3.8)
        fg.poly([(29.6, 28 + b), (27.6, 28 + b), (25.0, 41 + b), (26.4, 41 + b)], suit, 3.0)
        for y in range(41 + b, 54 + b):
            fg.shade(24.5, y, -1.0, suit)
        fg.px(24, 44 + b, suit, 1.4); fg.px(24, 49 + b, suit, 1.4)
        fg.poly([(18.0, 35 + b), (20.6, 35 + b), (20.6, 36.4 + b), (18.0, 36.4 + b)], tie, 3.0)   # el mocador
    elif p.f == 'L':
        fg.poly([(19.8, 29 + b), (21.6, 29 + b), (21.0, 39 + b), (19.8, 37 + b)], SHIRT_W, 2.8)
        fg.poly([(19.6, 30 + b), (20.8, 30 + b), (20.4, 38 + b), (19.4, 38 + b)], tie, 2.6)
        fg.poly([(21.6, 29 + b), (25.0, 29 + b), (22.0, 40 + b)], suit, 3.6)
        fg.px(21, 44 + b, suit, 1.4)
    else:
        fg.ell(24.5, 28.2 + b, 4.0, 1.6, SHIRT_W, 2.4, amp=1.0)
        for y in range(44 + b, 56 + b):
            fg.shade(24.5, y, -1.0, suit)
    if spec.get('messy'):
        _stains(fg, suit)


def _stains(fg, mat):
    """Taques i arrugues al vestit (roba `Brut`)."""
    for y in range(fg.h):
        for x in range(fg.w):
            v = fg.buf[y][x]
            if v and v[0] is mat:
                gx, gy = design(fg, x), design(fg, y)
                n = math.sin(gx * 0.9 + gy * 0.37) + math.sin(gx * 0.31 - gy * 0.83 + 1.7) + math.sin(gy * 0.5 + 2.2)
                d = 0.0
                if n > 2.1:
                    d -= 1.0
                elif n > 1.8:
                    d -= 0.5
                if (int(gx * 1.3 + gy * 0.6) % 9 == 0) and gy > 40:
                    d -= 0.7                                                         # arrugues
                fg.buf[y][x] = (mat, v[1] + d)


VERNE = {
    'skin': SKIN_PALE, 'legs': WHITE_SUIT, 'top': WHITE_SUIT, 'shoes': TAN_SHOE, 'thin': 1.2, 'smile': True,
    'brow': (200, 200, 206), 'iris': (90, 120, 150), 'lip': (160, 90, 90),
    'hooks': {'hair': verne_hair, 'over': verne_over},
}
VERNE_ROBA = {
    '': VERNE,
    'Brut': dict(VERNE, legs=DIRTY, top=DIRTY, messy=True, smile=False, shoes=BOOT),
}


# ═══════════════════════════════════════════════════════════════════════════
#  Holm, director del Banc: vestit gris fosc, ulleres primes, cabell engominat
# ═══════════════════════════════════════════════════════════════════════════

def _gel(x, y):
    return 1.2 if (int(x + y * 0.4) % 6 == 0) else 0.0


def holm_hair(fg, p, spec):
    hx, hy = p.head
    H = HAIR_GEL
    if p.f == 'D':
        fg.ell(hx, hy - 2.0, 7.2, 6.8, H, 2.4, amp=1.8, cont=(0.2, 0.8), lvlfn=_gel,
               clip=lambda x, y: y <= hy - 4.4 + ((x - hx) / 7) ** 2 * 5.0)
        for y in range(int(hy - 8), int(hy - 4)):                                  # la clenxa, al costat
            fg.shade(hx - 2.5, y, -1.2, H)
        for sx in (-1, 1):
            fg.ell(hx + sx * 6.6, hy - 0.4, 1.0, 2.0, H, 2.0, amp=1.0)
    elif p.f == 'L':
        fg.ell(hx + 1.2, hy - 1.6, 7.0, 7.2, H, 2.4, amp=1.8, cont=(0.2, 0.8), lvlfn=_gel,
               clip=lambda x, y: (x >= hx - 2.0 or y <= hy - 5.0) and not (x < hx + 2.6 and y > hy - 1.2))
    else:
        fg.ell(hx, hy - 0.8, 7.2, 7.6, H, 2.4, amp=1.8, cont=(0.2, 0.8), lvlfn=_gel)


HOLM = {
    'skin': SKIN_SALLOW, 'legs': SUIT_GREY, 'top': SUIT_GREY, 'shoes': BLACK_SHOE, 'thin': 0.6,
    'brow': (30, 24, 22), 'iris': (60, 70, 80), 'lip': (140, 96, 96), 'tie': TIE_DARK,
    'hooks': {'hair': hooks(holm_hair, glasses(STEELB, False, 2.2)), 'over': verne_over},
}


# ═══════════════════════════════════════════════════════════════════════════
#  Kessel, magnat de l'aire: abric de pells blau, perles, mascareta d'oxigen daurada
# ═══════════════════════════════════════════════════════════════════════════

def _fur(x, y):
    return 0.6 * math.sin(x * 2.3 + y * 0.9) * math.sin(y * 1.7 - x * 0.5) - (0.5 if (int(x) * 3 + int(y) * 5) % 11 == 0 else 0)


def kessel_hair(fg, p, spec):
    """Un cardat alt i lila-platejat."""
    hx, hy = p.head
    H = HAIR_LILAC
    curl = lambda x, y: 0.6 * math.sin(x * 1.6) * math.sin(y * 1.6)  # noqa: E731
    if p.f == 'D':
        fg.ell(hx, hy - 4.0, 8.8, 7.2, H, 2.6, amp=1.6, cont=(0.2, 0.9), lvlfn=curl,
               clip=lambda x, y: y <= hy - 3.0 + ((x - hx) / 8) ** 2 * 5.0)
        for sx in (-1, 1):
            fg.ell(hx + sx * 7.0, hy + 0.6, 2.4, 3.4, H, 2.4, amp=1.2, lvlfn=curl)
    elif p.f == 'L':
        fg.ell(hx + 1.6, hy - 3.6, 8.6, 7.4, H, 2.6, amp=1.6, cont=(0.2, 0.9), lvlfn=curl,
               clip=lambda x, y: (x >= hx - 1.0 or y <= hy - 5.0) and not (x < hx + 2.6 and y > hy - 1.0))
        fg.ell(hx + 5.0, hy + 1.6, 3.0, 3.6, H, 2.4, amp=1.2, lvlfn=curl)
    else:
        fg.ell(hx, hy - 2.6, 8.8, 8.6, H, 2.6, amp=1.6, cont=(0.2, 0.9), lvlfn=curl)


def kessel_collar(fg, p, spec):
    """El coll de pells, gros."""
    b = p.bob
    if p.f == 'L':
        fg.ell(26.0, 29.0 + b, 5.6, 3.4, FUR_BLUE, 3.0, amp=1.4, cont=(0.2, 0.9), lvlfn=_fur)
    elif p.f == 'D':
        for sx in (-1, 1):
            fg.ell(24.5 + sx * 5.6, 30.0 + b, 4.4, 3.4, FUR_BLUE, 3.2 if sx < 0 else 2.6, amp=1.4, cont=(0.2, 0.9),
                   lvlfn=_fur)
    else:
        fg.ell(24.5, 29.0 + b, 8.4, 3.6, FUR_BLUE, 2.8, amp=1.4, cont=(0.2, 0.9), lvlfn=_fur)
    if p.f == 'D':                                                                 # perles i la mascareta
        for k in range(9):
            a = math.pi * (0.15 + 0.7 * k / 8)
            x, y = 24.5 + math.cos(a) * 3.6, 28.6 + b + math.sin(a) * 2.6
            dot(fg, x, y, PEARL, 2.8 if k % 2 else 2.2)
        fg.ell(26.0, 35.6 + b, 1.8, 1.5, MASK_GOLD, 2.8, amp=1.2, cont=(0.1, 0.7))
        fg.line(27.0, 36.2 + b, 30.0, 40.0 + b, MASK_GOLD, 1.8)
        fg.line(25.0, 34.0 + b, 22.4, 30.0 + b, MASK_GOLD, 1.4)
    elif p.f == 'L':
        for k in range(4):
            dot(fg, 21.4 + k * 0.9, 30.0 + b + k * 0.5, PEARL, 2.6)
        fg.ell(21.6, 35.0 + b, 1.3, 1.5, MASK_GOLD, 2.8, amp=1.2, cont=(0.1, 0.7))
        fg.line(22.4, 36.0 + b, 25.0, 40.0 + b, MASK_GOLD, 1.8)


def kessel_over(fg, p, spec):
    b = p.bob
    if p.f == 'D':
        for y in range(34 + b, 46 + b):
            fg.shade(24.5, y, -0.9, FUR_BLUE)


def kessel_arm(fg, p, spec, i):
    """Punys de pell grossos."""
    w = p.arms[i][2] if p.f == 'L' else p.wrist[i]
    fg.ell(w[0] - (0.4 if p.f == 'L' else 0), w[1] - 0.2, 3.2, 1.8, FUR_BLUE, 2.8 if i == 0 else 2.2, amp=1.2,
           cont=(0.2, 0.8), lvlfn=_fur)


KESSEL = {
    'skin': SKIN_OLD, 'legs': STOCKING, 'top': FUR_BLUE, 'shoes': BLACK_SHOE, 'thin': -0.6, 'lashes': True,
    'brow': (120, 110, 130), 'iris': (60, 50, 90), 'lip': (170, 40, 70),
    'hooks': {'hair': kessel_hair, 'torso': coat(FUR_BLUE, 74, 3.6, 2.8, _fur, False), 'collar': kessel_collar,
              'over': kessel_over, 'arm': kessel_arm},
}


# ═══════════════════════════════════════════════════════════════════════════
#  Quim, el pare (82): jersei de llana, gorra, molt prim
# ═══════════════════════════════════════════════════════════════════════════

def quim_hair(fg, p, spec):
    """Quatre cabells blancs a sota la gorra de visera, de tweed."""
    hx, hy = p.head
    if p.f == 'D':
        for sx in (-1, 1):
            fg.ell(hx + sx * 6.4, hy - 1.4, 0.9, 1.4, HAIR_WHITE, 2.0, amp=1.0)
        fg.ell(hx, hy - 5.4, 7.8, 3.8, TWEED, 2.6, amp=1.4, cont=(0.2, 0.9), clip=lambda x, y: y <= hy - 3.4,
               lvlfn=lambda x, y: -0.5 if (int(x) + int(y)) % 3 == 0 else 0)
        fg.ell(hx, hy - 3.4, 6.4, 1.4, TWEED, 1.8, amp=1.0, cont=(0.0, 0.8))
    elif p.f == 'L':
        fg.ell(hx + 4.6, hy + 0.4, 2.2, 2.4, HAIR_WHITE, 2.4, amp=1.0)
        fg.ell(hx + 1.4, hy - 5.0, 7.6, 3.8, TWEED, 2.6, amp=1.4, cont=(0.2, 0.9), clip=lambda x, y: y <= hy - 3.0,
               lvlfn=lambda x, y: -0.5 if (int(x) + int(y)) % 3 == 0 else 0)
        fg.poly([(hx - 5.4, hy - 4.6), (hx - 9.0, hy - 3.2), (hx - 8.8, hy - 2.4), (hx - 4.8, hy - 3.0)], TWEED, 2.0,
                cont=(0.0, 0.6))
    else:
        fg.ell(hx, hy - 5.0, 7.8, 4.0, TWEED, 2.4, amp=1.4, cont=(0.2, 0.9), clip=lambda x, y: y <= hy - 2.6,
               lvlfn=lambda x, y: -0.5 if (int(x) + int(y)) % 3 == 0 else 0)


def quim_over(fg, p, spec):
    """El jersei de llana: punt d'arròs i un coll alt doblegat."""
    for y in range(fg.h):
        for x in range(fg.w):
            v = fg.buf[y][x]
            if v and v[0] is KNIT:
                gx, gy = int(design(fg, x)), int(design(fg, y))
                if gx % 3 == 0:
                    fg.buf[y][x] = (KNIT, v[1] - 0.6)
                elif gy % 2 == 0 and gx % 3 == 1:
                    fg.buf[y][x] = (KNIT, v[1] + 0.5)
    b = p.bob
    if p.f == 'L':
        fg.ell(26.0, 28.4 + b, 4.0, 2.4, KNIT, 2.8, amp=1.2, cont=(0.2, 0.8))
    elif p.f == 'D':
        fg.ell(24.5, 28.2 + b, 4.6, 2.4, KNIT, 2.8, amp=1.2, cont=(0.2, 0.8))
    if 'seated' in spec:
        _umbrella(fg, p)


def _umbrella(fg, p):
    """El paraigua tancat, de pal, a la mà del davant i amb la punta a terra."""
    w = p.arms[0][2]
    top = (w[0] - 1.0, w[1] - 1.0)
    bot = (w[0] - 3.4, 82.8)
    fg.poly([(top[0] - 0.8, top[1] + 4), (top[0] + 0.9, top[1] + 4), (bot[0] + 1.6, bot[1] - 6),
             (bot[0] + 0.3, bot[1] - 1), (bot[0] - 0.6, bot[1] - 6)], UMBRELLA, 2.4, amp=0.6, cont=(0.0, 0.8))
    fg.line(top[0], top[1] + 4, top[0], top[1] - 1, WOOD, 2.4)
    fg.ell(top[0] + 1.2, top[1] - 1.6, 1.4, 1.2, WOOD, 2.8, amp=1.0, clip=lambda x, y: y <= top[1] - 1.2)
    fg.ell(w[0] - 0.4, w[1] + 1.8, 2.1, 2.3, p.spec['skin'], 2.7, amp=1.4)


QUIM = {
    'skin': SKIN_OLD, 'legs': CORD, 'top': KNIT, 'shoes': BOOT, 'thin': 1.8, 'stoop': 3,
    'brow': (226, 226, 226), 'iris': (70, 80, 90), 'lip': (140, 90, 90),
    'hooks': {'hair': quim_hair, 'over': quim_over},
}


NPCS = {
    'capitana': CAPITANA, 'tomas': TOMAS, 'juana': JUANA, 'bru': BRU, 'lia': LIA, 'rosa': ROSA, 'nil': NIL,
    'verne': VERNE, 'holm': HOLM, 'kessel': KESSEL, 'quim': QUIM,
}
ROBES = {'verne': VERNE_ROBA}
SEUEN = {'juana': WOOD_PALE, 'quim': WOOD}


def npc(cid, facing, talk=False, walk=None, roba=''):
    spec = ROBES[cid][roba] if roba else NPCS[cid]
    return person(spec, facing, walk=walk, talk=talk)


def npc_seu(cid, talk=False):
    """Assegut de perfil (mirant a l'esquerra) en una cadira; la boca es mou."""
    return person(seated(NPCS[cid], 61, SEUEN[cid]), 'L', talk=talk)


# ═══════════════════════════════════════════════════════════════════════════
#  En Diu, el gat (el de Ni un ou)
# ═══════════════════════════════════════════════════════════════════════════

CAT = M((14, 12, 16), (34, 30, 34), (58, 52, 54), (86, 78, 76), (116, 106, 100), (150, 140, 128))
CAT_WHITE = M((70, 66, 74), (130, 126, 128), (182, 178, 172), (220, 216, 206), (244, 240, 230))
CAT_EYE = M((20, 40, 10), (90, 130, 30), (160, 200, 60), (220, 240, 130))
GW, GH = 30, 26          # fotograma del gat a ×1 (peus a (13, 25))


def diu(cua=0, parpelleja=False):
    """Assegut de tres quarts, tigrat i amb el pitet blanc."""
    fg = Fig(GW, GH)
    tx = [24, 26, 27, 26][cua % 4]
    fg.limb((19, 22), (tx, 14), 1.4, 1.2, CAT, 2.2, cont=(0.2, 0.8))
    fg.limb((tx, 14), (tx - 1, 10), 1.2, 1.1, CAT, 2.4, cont=(0.2, 0.8))
    fg.ell(14, 18, 7.5, 6.5, CAT, 2.6, amp=1.6, cont=(0.2, 1.0),
           lvlfn=lambda x, y: -0.8 if (int(x) + int(y) // 2) % 4 == 0 else 0)
    fg.ell(12, 19, 3.2, 4.4, CAT_WHITE, 2.8, amp=1.4)
    fg.ell(10, 24, 2.4, 1.4, CAT_WHITE, 2.8, amp=1.2)
    fg.ell(15, 24, 2.4, 1.4, CAT_WHITE, 2.4, amp=1.2)
    fg.ell(12, 9, 5.6, 5.0, CAT, 2.8, amp=1.6, cont=(0.2, 1.0),
           lvlfn=lambda x, y: -0.8 if int(y) in (5, 6) and int(x) % 3 == 0 else 0)
    fg.poly([(7, 6), (8, 1), (11, 4)], CAT, 2.6)
    fg.poly([(17, 6), (16, 1), (13, 4)], CAT, 2.2)
    fg.ell(12, 11.5, 2.4, 1.6, CAT_WHITE, 3.0, amp=1.0)
    for ex in (9.5, 14.5):
        if parpelleja:
            fg.px(ex - 1, 9, CAT, 0); fg.px(ex, 9, CAT, 0); fg.px(ex + 1, 9, CAT, 0)
        else:
            fg.ell(ex, 9, 1.4, 1.3, CAT_EYE, 2.6, amp=1.0)
            dot(fg, ex, 9, CAT, 0)
            if big(fg):
                dot(fg, ex, 8.4, CAT, 0)
    fg.px(12, 11, (190, 110, 120), 0)
    return fg.render()


def diu_camina(k=0):
    """Caminant de perfil, cap a l'esquerra (el motor el gira per anar a la dreta). Sis fotogrames."""
    fg = Fig(GW, GH)
    fase = k * math.pi / 3
    bob = 0.5 if k % 3 == 0 else 0
    for x0, ph, near in ((10, 0, False), (21, math.pi, False), (12, math.pi, True), (23, 0, True)):
        sw = math.sin(fase + ph)
        lift = max(0.0, math.cos(fase + ph)) * 1.2
        fg.limb((x0, 18 + bob), (x0 - 2.2 * sw, 24.5 - lift), 1.4, 1.1, CAT, 2.6 if near else 1.6, cont=(0.2, 0.8))
        fg.ell(x0 - 2.2 * sw - 0.4, 25 - lift, 1.3, 0.8, CAT_WHITE if near else CAT, 2.4 if near else 1.4, amp=1.0)
    tx = 29 + 0.8 * math.sin(fase)
    fg.limb((25, 15 + bob), (28, 10 + bob), 1.4, 1.2, CAT, 2.2, cont=(0.2, 0.8))
    fg.limb((28, 10 + bob), (tx, 5 + bob), 1.2, 1.0, CAT, 2.4, cont=(0.2, 0.8))
    fg.ell(17, 16 + bob, 9.0, 4.6, CAT, 2.6, amp=1.6, cont=(0.2, 1.0),
           lvlfn=lambda x, y: -0.8 if (int(x) + int(y) // 2) % 4 == 0 else 0)
    fg.ell(16, 19 + bob, 6.0, 1.6, CAT_WHITE, 2.6, amp=1.2)
    fg.ell(9, 17 + bob, 2.6, 3.0, CAT_WHITE, 2.8, amp=1.4)
    hy = 11 + bob
    fg.ell(7, hy, 4.6, 4.2, CAT, 2.8, amp=1.6, cont=(0.2, 1.0),
           lvlfn=lambda x, y: -0.8 if int(y) == int(hy) - 3 and int(x) % 3 == 0 else 0)
    fg.poly([(5, hy - 3), (5, hy - 8), (8, hy - 4)], CAT, 2.6)
    fg.poly([(8, hy - 3), (10, hy - 7), (11, hy - 2)], CAT, 2.2)
    fg.ell(3.6, hy + 1.6, 2.0, 1.4, CAT_WHITE, 3.0, amp=1.0)
    fg.ell(5.5, hy - 0.5, 1.2, 1.2, CAT_EYE, 2.6, amp=1.0)
    dot(fg, 5, hy - 0.5, CAT, 0)
    fg.px(2.5, hy + 1, (190, 110, 120), 0)
    return fg.render()


# ═══════════════════════════════════════════════════════════════════════════
#  En Dividend, el gos del Magnat: petit, blanc, pentinat, amb un banyador de ratlles
# ═══════════════════════════════════════════════════════════════════════════

DW, DH = 34, 26          # fotograma del gos a ×1 (peus a (17, 25))
DOG = M((70, 66, 84), (128, 124, 136), (180, 176, 180), (218, 214, 210), (240, 236, 228), (252, 250, 244), dith=0.0)
DOG_WET = M((40, 46, 62), (78, 88, 106), (118, 128, 142), (156, 166, 176), (190, 198, 204), (218, 224, 228), dith=0.0)
STRIPE_N = M((6, 10, 30), (14, 24, 64), (26, 44, 108), (44, 70, 150), (76, 104, 186))
STRIPE_W = M((120, 110, 100), (190, 182, 166), (232, 226, 210), (250, 248, 238))
BOW = M((70, 6, 20), (150, 16, 40), (214, 40, 64), (246, 100, 120))
NOSE = (20, 14, 18)
TONGUE = (220, 110, 130)
DROP = M((40, 90, 130), (90, 160, 210), (170, 220, 250), (240, 252, 255))


def _fluff(x, y):
    return 0.45 * math.sin(x * 2.2 + y * 1.3) * math.sin(y * 2.0 - x * 0.7)


def _stripes(fg, pix, vertical=True, w=2):
    """Pinta de ratlles blaves i blanques els píxels `pix` (els d'una primitiva)."""
    for (X, Y), _ in pix.items():
        if not (0 <= X < fg.w and 0 <= Y < fg.h) or not fg.buf[Y][X]:
            continue
        u = design(fg, X) if vertical else design(fg, Y)
        m, l = fg.buf[Y][X]
        fg.buf[Y][X] = (STRIPE_W if int(math.floor(u / w)) % 2 else STRIPE_N, l)


def dividend(facing='L', walk=None, talk=False, moll=False):
    """En Dividend. `facing` D, L o U; `walk` 0..5; `talk` = borda; `moll` = xop (acaba de nedar)."""
    fg = Fig(DW, DH)
    F = DOG_WET if moll else DOG
    fl = (lambda x, y: -0.6 if int(x) % 2 == 0 else 0) if moll else _fluff     # xop: el pèl, en flocs enganxats
    sh = 0.7 if moll else 1.0                                                   # el pèl xop fa el gos més prim
    bob = 0
    if walk is not None:
        bob = -0.6 if walk % 3 == 1 else 0
    if facing == 'L':
        fase = (walk or 0) * math.pi / 3
        # cua: un pompó amunt (xop: avall)
        if moll:
            fg.limb((25, 15 + bob), (29, 19 + bob), 1.0, 0.8, F, 2.2, cont=(0.2, 0.8))
        else:
            fg.limb((25, 14 + bob), (27.5, 9 + bob), 0.9, 0.8, F, 2.4, cont=(0.2, 0.8))
            fg.ell(28, 7.6 + bob + (0.4 * math.sin(fase * 2) if walk is not None else 0), 2.2, 2.0, F, 3.0, amp=1.4,
                   cont=(0.2, 0.9), lvlfn=fl)
        for x0, ph, near in ((11, 0, False), (22, math.pi, False), (13, math.pi, True), (24, 0, True)):
            sw = math.sin(fase + ph) if walk is not None else 0
            lift = max(0.0, math.cos(fase + ph)) * 1.2 if walk is not None else 0
            fx = x0 - 2.0 * sw
            fg.limb((x0, 17 + bob), (fx, 24.0 - lift), 1.4 * sh + 0.2, 1.0, F, 2.6 if near else 1.6, cont=(0.2, 0.8), lvlfn=fl)
            fg.ell(fx - 0.5, 24.6 - lift, 1.4, 0.8, F, 2.6 if near else 1.6, amp=1.0)
        body = fg.ell(18, 14.6 + bob, 8.0, 4.0 * sh + 0.8, F, 2.8, amp=1.6, cont=(0.2, 1.0), lvlfn=fl)
        suit = fg.ell(19.4, 14.8 + bob, 6.4, 3.4 * sh + 0.8, STRIPE_N, 2.6, amp=1.6, cont=(0.1, 0.8),
                      clip=lambda x, y: x >= 13.6)
        _stripes(fg, suit, True, 2)
        if moll:
            for x, y in ((14, 20.4), (19, 20.8), (23, 20.2)):
                fg.px(x, y + bob, DROP, 2.6)
        hy = 9.6 + bob + (-0.8 if talk else 0)
        fg.ell(9.0, hy, 4.4 * sh + 0.6, 4.0 * sh + 0.6, F, 3.0, amp=1.6, cont=(0.2, 1.0), lvlfn=fl)       # cap
        fg.ell(4.6, hy + 1.6, 2.6, 1.7, F, 3.2, amp=1.2, cont=(0.2, 0.8))                       # morro
        dot(fg, 2.2, hy + 1.0, NOSE, 0)
        if big(fg):
            dot(fg, 2.2, hy + 1.6, NOSE, 0)
        if talk:                                                                   # borda: la boca oberta
            fg.poly([(2.6, hy + 2.4), (7.0, hy + 2.0), (3.2, hy + 4.4)], (60, 14, 26), 0)
            dot(fg, 3.8, hy + 3.2, TONGUE, 0)
        else:
            fg.line(3.0, hy + 2.6, 5.6, hy + 2.6, (120, 100, 110), 0)
        dot(fg, 7.2, hy - 0.6, NOSE, 0)                                            # ull
        if big(fg):
            dot(fg, 7.2, hy - 1.4, NOSE, 0)
        fg.ell(11.2, hy + 1.6, 1.7, 3.4 if not moll else 4.0, F, 2.0, amp=1.2, cont=(0.2, 0.8), lvlfn=fl)  # orella
        if moll:
            fg.px(11.2, hy + 6.0, DROP, 2.6)
            fg.ell(9.0, hy - 3.6, 3.2, 1.2, F, 3.0, amp=1.0)                       # el tupè, aixafat
            fg.ell(9.8, hy - 3.8, 1.2, 0.9, BOW, 1.8, amp=0.8)
        else:
            fg.ell(9.4, hy - 4.2, 3.6, 2.6, F, 3.4, amp=1.4, cont=(0.2, 0.9), lvlfn=_fluff)    # el tupè, pentinat
            fg.ell(10.4, hy - 6.4, 1.4, 1.1, BOW, 2.6, amp=0.8)
            fg.ell(12.0, hy - 6.6, 1.2, 1.0, BOW, 2.2, amp=0.8)
    else:
        # de cara o d'esquena: dret, el pit, les potes del davant i les anques als costats
        lift = [0, 0]
        if walk is not None:
            sn = math.sin(2 * math.pi * walk / 6)
            lift = [max(0.0, sn) * 1.4, max(0.0, -sn) * 1.4]
        back = facing == 'U'
        for i, x in enumerate((12.8, 21.2)):                                        # potes del darrere
            fg.limb((x, 19 + bob), (x - 0.2 * (1 if i else -1), 24.0 - lift[1 - i]), 1.3 * sh + 0.3, 1.1, F, 1.8,
                    cont=(0.2, 0.8), lvlfn=fl)
            fg.ell(x, 24.4 - lift[1 - i], 1.5, 0.8, F, 1.8, amp=1.0)
        suit = fg.ell(17, 17.6 + bob, 5.4 * sh + 1.4, 4.0, STRIPE_N, 2.6, amp=1.6, cont=(0.1, 0.8))
        _stripes(fg, suit, False, 1.5)
        if back:
            if moll:
                fg.limb((17, 18 + bob), (17.6, 22 + bob), 1.0, 0.8, F, 2.2, cont=(0.2, 0.8))
            else:
                fg.limb((17, 16 + bob), (17, 12.4 + bob), 0.9, 0.8, F, 2.4, cont=(0.2, 0.8))
                fg.ell(17, 11.2 + bob, 2.4, 2.2, F, 3.0, amp=1.4, cont=(0.2, 0.9), lvlfn=fl)    # el pompó de la cua
        else:
            fg.ell(17, 14.4 + bob, 3.6 * sh + 0.8, 3.0, F, 3.0, amp=1.4, cont=(0.2, 0.9), lvlfn=fl)  # el pit
            for i, x in enumerate((15.0, 19.0)):                                    # potes del davant
                fg.limb((x, 16 + bob), (x, 24.0 - lift[i]), 1.3 * sh + 0.3, 1.1, F, 2.8 - i * 0.4, cont=(0.2, 0.8),
                        lvlfn=fl)
                fg.ell(x, 24.4 - lift[i], 1.6, 0.9, F, 2.8 - i * 0.4, amp=1.0)
        hy = 8.6 + bob + (-0.6 if talk else 0)
        for sx in (-1, 1):                                                          # orelles
            fg.ell(17 + sx * 4.8 * (0.9 if moll else 1), hy + 2.0, 1.7, 3.4 if not moll else 4.0,
                   F, 2.0 if sx > 0 else 2.4, amp=1.2, cont=(0.2, 0.8), lvlfn=fl)
        fg.ell(17, hy, 4.2 * sh + 1.0, 4.0 * sh + 0.6, F, 3.0, amp=1.6, cont=(0.2, 1.0), lvlfn=fl)
        if moll:
            fg.ell(17, hy - 3.4, 3.0, 1.2, F, 3.0, amp=1.0)
            fg.ell(18.2, hy - 4.0, 1.0, 0.8, BOW, 1.8, amp=0.8)
            for x, y in ((12.4, hy + 6.2), (21.8, hy + 6.6), (14, 23.4), (20, 23.6)):
                fg.px(x, y, DROP, 2.6)
        else:
            fg.ell(17, hy - 3.8, 3.4, 2.4, F, 3.4, amp=1.4, cont=(0.2, 0.9), lvlfn=_fluff)
            fg.ell(16.0, hy - 6.0, 1.1, 0.9, BOW, 2.6, amp=0.8)
            fg.ell(18.0, hy - 6.0, 1.1, 0.9, BOW, 2.2, amp=0.8)
        if not back:
            fg.ell(17, hy + 2.2, 2.4, 1.7, F, 3.4, amp=1.0)                         # morro
            dot(fg, 17, hy + 1.4, NOSE, 0)
            if big(fg):
                dot(fg, 16.2, hy + 1.4, NOSE, 0)
            for ex in (15.0, 19.0):
                dot(fg, ex, hy - 0.4, NOSE, 0)
                if big(fg):
                    dot(fg, ex, hy - 1.2, NOSE, 0)
            if talk:
                fg.ell(17, hy + 3.6, 1.3, 1.1, (60, 14, 26), 0)
                dot(fg, 17, hy + 4.0, TONGUE, 0)
            else:
                dot(fg, 16.2, hy + 3.0, (120, 100, 110), 0); dot(fg, 17.8, hy + 3.0, (120, 100, 110), 0)
    return fg.render()


# ═══════════════════════════════════════════════════════════════════════════
#  En Fidel, el majordom robot: cilindre blanc amb llacet, cap-pantalla amb dos ulls, braços prims
# ═══════════════════════════════════════════════════════════════════════════

ENAMEL = M((50, 54, 72), (98, 104, 120), (150, 156, 168), (196, 200, 206), (228, 230, 230), (246, 246, 242), (255, 255, 252), dith=0.0)
SCREEN = M((4, 8, 14), (8, 16, 26), (14, 28, 40), (24, 44, 60), (40, 70, 90))
EYE_CYAN = M((10, 70, 90), (40, 160, 190), (120, 230, 250), (220, 255, 255))
JOINT = M((14, 16, 22), (34, 38, 48), (64, 70, 82), (104, 112, 124), (156, 164, 174), (210, 216, 222))
BOWTIE = M((4, 4, 6), (10, 10, 14), (22, 22, 28), (40, 40, 50), (70, 70, 84))


def fidel(facing='D', walk=None, talk=False):
    """En Fidel. Fotograma de persona (49×87, peus a (25, 83)): llisca damunt un disc, no camina."""
    fg = Fig(49, 87)
    k = walk if walk is not None else 0
    bob = (-1 if k in (1, 2, 4, 5) else 0) if walk is not None else 0
    sw = math.sin(2 * math.pi * k / 6) if walk is not None else 0
    # el disc i la llum de sota
    fg.ell(24.5, 82.4, 6.4 if k % 2 == 0 else 5.6, 1.0, EYE_CYAN, 2.0 + (0.6 if k % 2 else 0), amp=0.6)
    fg.ell(24.5, 79.6 + bob * 0.5, 7.4, 2.4, JOINT, 2.2, amp=1.4, cont=(0.2, 0.8))
    side = facing == 'L'

    def body_edges(y):
        yy = y - bob
        if yy < 42:
            return None
        if yy < 45:
            w = [5.6, 7.6, 8.6][yy - 42]
        elif yy < 60:
            w = 8.6 + (yy - 45) * 0.07
        else:
            w = 9.6 - (yy - 60) * 0.11
        if side:
            w -= 1.0
        return (24.5 - w, 24.5 + w)
    # braç del fons (de perfil)
    sh_y = 46 + bob

    def arm(sx, el, wr, lvl):
        fg.limb((sx, sh_y), el, 1.0, 0.9, JOINT, lvl, cont=(0.2, 0.8))
        fg.limb(el, wr, 0.9, 0.8, JOINT, lvl, cont=(0.2, 0.8))
        fg.ell(el[0], el[1], 1.4, 1.4, ENAMEL, lvl + 0.4, amp=1.0)
        fg.ell(wr[0], wr[1] + 1.6, 2.0, 2.2, ENAMEL, lvl + 0.6, amp=1.4, cont=(0.2, 0.8))   # el guant blanc
    if side:
        arm(26.5, (28.0 + 3 * sw, 55 + bob), (27.0 + 5 * sw, 63 + bob), 1.6)
    fg.lathe(42 + bob, 78 + bob, body_edges, ENAMEL, 3.0, amp=1.8, cont=(0.0, 0.6))
    for y in (50, 70):                                                              # junts del xapat
        e = body_edges(y + bob)
        for x in range(int(e[0]) + 1, int(e[1]) + 1):
            fg.shade(x, y + bob, -1.0, ENAMEL)
    if facing == 'D':
        for y in (56, 61, 66):
            fg.ell(24.5, y + bob, 0.9, 0.9, BOWTIE, 2.4, amp=0.8)                   # els botons de majordom
    elif side:
        for y in (56, 61, 66):
            fg.ell(17.4, y + bob, 0.7, 0.9, BOWTIE, 2.4, amp=0.8)
    else:
        fg.poly([(21.0, 46 + bob), (28.0, 46 + bob), (27.0, 58 + bob), (22.0, 58 + bob)], ENAMEL, 2.4, cont=(0.0, 0.8))
        for y in (49, 52, 55):
            fg.line(23, y + bob, 26, y + bob, JOINT, 1.4)                           # la reixeta de ventilació
    # coll i cap-pantalla
    fg.limb((24.5, 35 + bob), (24.5, 42 + bob), 1.4, 1.6, JOINT, 2.2, cont=(0.2, 0.8))
    hx = 24.5
    if side:
        x0, x1 = 19.5, 30.5
    else:
        x0, x1 = 16.0, 33.0
    y0, y1 = 16 + bob, 35 + bob

    def head_edges(y):
        r = 2.4
        t = min(y - y0, y1 - y)
        if t < 0:
            return None
        cut = r - math.sqrt(max(0.0, r * r - (r - t) ** 2)) if t < r else 0
        return (x0 + cut, x1 - cut)
    fg.lathe(y0, y1, head_edges, ENAMEL, 3.0, amp=1.6, cont=(0.0, 0.7))
    # l'antena
    ax = hx + (2.0 if side else 0)
    fg.limb((ax, y0), (ax + 1.0, y0 - 4.5), 0.5, 0.5, JOINT, 2.6)
    fg.ell(ax + 1.0, y0 - 5.4, 1.2, 1.2, BOW if talk else EYE_CYAN, 2.6, amp=1.0)
    if facing == 'D':
        fg.lathe(y0 + 2, y1 - 2, lambda y: (x0 + 2.0, x1 - 2.0) if y0 + 2 <= y <= y1 - 2 else None, SCREEN, 2.0,
                 amp=1.2)
        for y in range(int(y0 + 3), int(y0 + 7)):                                   # reflex al vidre
            fg.shade(x0 + 3.0 + (y - y0 - 3), y, +1.6, SCREEN)
        ey = y0 + 7
        if talk:
            # parlant: els ulls, arquejats (contents); i una ona per boca
            for ex in (20.5, 28.5):
                for dx, dy in ((-1, 1), (0, 0), (1, 0), (2, 1)):
                    fg.px(ex + dx - 0.5, ey + dy, EYE_CYAN, 2.6)
            for i, x in enumerate(range(21, 29)):
                fg.px(x, y0 + 13 + (1 if i % 4 in (1, 2) else 0), EYE_CYAN, 2.2)
        else:
            for ex in (20.5, 28.5):
                for dx in (-1, 0):
                    for dy in (0, 1, 2):
                        fg.px(ex + dx, ey + dy, EYE_CYAN, 2.4 + (0.8 if dy == 0 else 0))
    elif side:
        fg.lathe(y0 + 2, y1 - 2, lambda y: (x0 - 0.2, x0 + 1.6) if y0 + 2 <= y <= y1 - 2 else None, SCREEN, 2.0, amp=0.8)
        ey = y0 + 7
        for dy in (0, 1, 2):
            fg.px(x0 + 0.5, ey + dy, EYE_CYAN, 2.6 + (0.8 if dy == 0 else 0))
        if talk:
            fg.px(x0 + 0.5, y0 + 13, EYE_CYAN, 2.2); fg.px(x0 + 0.5, y0 + 14, EYE_CYAN, 2.2)
        fg.ell(x0 + 7.0, (y0 + y1) / 2, 2.0, 2.0, JOINT, 2.0, amp=1.0)                 # el cargol de l'orella
    else:
        for y in range(int(y0 + 4), int(y1 - 3), 3):
            fg.line(x0 + 4, y, x1 - 4, y, ENAMEL, 2.0)
    # el llacet negre
    by = 39.5 + bob
    if side:
        fg.ell(17.6, by, 1.4, 1.8, BOWTIE, 2.6, amp=1.0, cont=(0.0, 0.6))
    elif facing == 'D':
        fg.poly([(20.0, by - 2.2), (24.5, by), (20.0, by + 2.2)], BOWTIE, 2.6, cont=(0.0, 0.6))
        fg.poly([(29.0, by - 2.2), (24.5, by), (29.0, by + 2.2)], BOWTIE, 2.2, cont=(0.0, 0.6))
        fg.ell(24.5, by, 1.2, 1.2, BOWTIE, 3.2, amp=0.8)
    # braços del davant
    if side:
        arm(23.5, (22.5 - 3 * sw, 55 + bob), (21.5 - 5 * sw, 63 + bob), 2.6)
    else:
        for i, sx in enumerate((14.2, 34.8)):
            d = -1 if i == 0 else 1
            s2 = sw * (1 if i == 0 else -1)
            fg.ell(sx - d * 0.4, sh_y, 1.8, 1.8, JOINT, 2.4 - i * 0.5, amp=1.2, cont=(0.2, 0.8))   # l'espatlla
            el = (sx + d * 1.2, 55 + bob - s2 * 0.6)
            wr = (sx + d * 0.8, 63 + bob - s2 * 1.4)
            arm(sx, el, wr, 2.6 - i * 0.6)
    return fg.render()


# ═══════════════════════════════════════════════════════════════════════════
#  Per a la GUI (hd/gui.py): les protagonistes a la mida de disseny i la cara
# ═══════════════════════════════════════════════════════════════════════════

def iri(facing='L', walk=None, talk=False, roba=''):
    return person(IRI_ROBA[roba], facing, walk=walk, talk=talk)


def vet(facing='D', walk=None, talk=False, roba=''):
    return person(VET, facing, walk=walk, talk=talk)


def cara(fn):
    """La cara d'una protagonista (25×30), per al botó «Canvia»."""
    return fn('D').crop((12, 2, 37, 32))
