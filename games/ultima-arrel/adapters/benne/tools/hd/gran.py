"""
La mida gran de les persones de L'Última Arrel (prefix `Gran` als fulls): la mateixa figura redibuixada a ×1,5, no
ampliada.

La caseta d'obra i el campament de les Fades es van pintar per a personatges de 97 px, i els fulls en fan 68: escalats
a 1,75, cada píxel del personatge era el doble que els del decorat. Amb la mida gran, el motor (`sizeVariants` al
.character.json) la mostra a l'escala de la sala ÷ 1,5 (≈0,7–1,2) i els píxels tornen a ser com els de la sala.

Com FigK d'Aigua Verne (adapters/benne/tools/hd/personatges.py), però damunt de FigY (les proporcions de cada
persona): **FigYK** rep les mateixes ordres en coordenades de disseny, les passa a les files de FigY i les rasteritza a
×1,5, amb volum i contorn d'un píxel real. Els píxels solts dels ganxos ocupen la seva zona (1 o 2 píxels reals), les
línies són d'un píxel real, i **la cara es refà píxel a píxel a la mida nova** (`front_face_k`, `side_face_k`): la
mateixa cara (la de Suma Zero, per a la Iri i la Vet), amb els ulls de 3 px en lloc de 2.

El fotograma gran és el d'1× escalat (mateixa cantonada de dalt a l'esquerra, peus × 1,5): el motor hi compta. Per
això la figura es desplaça mig píxel real si cal (`sub`), perquè la retallada d'1× caigui en un píxel enter.
"""
import math
from contextlib import contextmanager

import hd.characters as C
from hd import arrel as A
from hd.characters import Fig
from hd.pix import mix

K = 1.5


class FigYK(A.FigY):
    """FigY a ×K. `w`, `h` i `buf` són a la mida real; `sub` = (sx, sy), el desplaçament (en píxels reals) que fa caure
    la retallada d'1× en un píxel enter."""

    big = True
    sub = (0.0, 0.0)

    def __init__(self, w, h):
        Fig.__init__(self, math.ceil(w * K) + 1, math.ceil((h + A.PAD) * K) + 1)

    # coordenada d'1× (centre de píxel, la de FigY) ↔ real a ×K
    def fx(self, X):
        return (X + 0.5) * K - 0.5 + self.sub[0]

    def fy(self, Y):
        return (Y + 0.5) * K - 0.5 + self.sub[1]

    def gx(self, X):
        return (X + 0.5 - self.sub[0]) / K - 0.5

    def gy(self, Y):
        return (Y + 0.5 - self.sub[1]) / K - 0.5

    def span_x(self, i):
        """Els píxels reals que ocupa el píxel d'1× i."""
        return range(math.ceil(self.fx(i - 0.5)), math.ceil(self.fx(i + 0.5)))

    def span_y(self, j):
        return range(math.ceil(self.fy(j - 0.5)), math.ceil(self.fy(j + 0.5)))

    def _m1(self, x, y):
        """Disseny → 1× (FigY)."""
        return A.FigY._m(self, x, y)

    def _m(self, x, y):
        X, Y = self._m1(x, y)
        return self.fx(X), self.fy(Y)

    def _d(self, X, Y):
        return A.FigY._d(self, self.gx(X), self.gy(Y))

    def m(self, x, y):
        """Disseny → real (per als ganxos que dibuixen a la mida nova)."""
        return self._m(x, y)

    # ─── primitives amb volum: es rasteritzen a la mida real ───
    def ell(self, cx, cy, rx, ry, mat, base, amp=1.6, cont=None, lvlfn=None, clip=None):
        P_ = self.prop
        yy = cy + self.oy
        CX_, CY_ = self._m(cx, cy)
        RX, RY = rx * P_.kx(yy) * K, ry * P_.ky(yy) * K
        pix = {}
        for y in range(math.floor(CY_ - RY), math.ceil(CY_ + RY) + 1):
            for x in range(math.floor(CX_ - RX), math.ceil(CX_ + RX) + 1):
                nx, ny = (x - CX_) / RX, (y - CY_) / RY
                r2 = nx * nx + ny * ny
                if r2 <= 1 and (clip is None or clip(*self._d(x, y))):
                    pix[(x, y)] = (nx, ny, math.sqrt(1 - r2))
        self._paint(pix, mat, base, amp, cont, lvlfn)
        return pix

    def limb(self, a, b, r0, r1, mat, base, amp=1.6, cont=None, lvlfn=None, clip=None):
        P_ = self.prop
        ax, ay = self._m(*a)
        bx, by = self._m(*b)
        k = P_.kx((a[1] + b[1]) / 2 + self.oy) * K
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
                if d2 <= 1 and (clip is None or clip(*self._d(x, y))):
                    pix[(x, y)] = (ex / r, ey / r, math.sqrt(1 - d2))
        self._paint(pix, mat, base, amp, cont, lvlfn)
        return pix

    def lathe(self, y0, y1, edges, mat, base, amp=1.6, cont=None, lvlfn=None, tilt=0.0):
        P_ = self.prop
        y0, y1 = math.floor(y0), math.floor(y1)
        pix = {}
        Y0 = math.floor(self.fy(P_.y(y0 - 0.5 + self.oy)))
        Y1 = math.ceil(self.fy(P_.y(y1 + 0.5 + self.oy)))
        for Y in range(Y0, Y1 + 1):
            yd = P_.inv(self.gy(Y)) - self.oy
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
                if not e:
                    continue
            k = P_.kx(yd + self.oy)
            xl = self.fx(A.CX + (e[0] + self.ox - A.CX) * k) - K / 2 + 0.5
            xr = self.fx(A.CX + (e[1] + self.ox - A.CX) * k) + K / 2 - 0.5
            mid, half = (xl + xr) / 2, max(0.5, (xr - xl) / 2)
            for x in range(math.ceil(xl - 0.01), math.floor(xr + 0.01) + 1):
                u = max(-1.0, min(1.0, (x - mid) / (half + 0.5)))
                nz = math.sqrt(max(0.0, 1 - u * u - tilt * tilt))
                pix[(x, Y)] = (u, tilt, nz)
        self._paint(pix, mat, base, amp, cont, lvlfn)
        return pix

    # (poly: la de FigY, amb `_m` i `_d` d'aquí, ja rasteritza a la mida real)

    # ─── píxels de disseny: ocupen la seva zona ───
    def _zone(self, x, y):
        X1, Y1 = self._m1(x, y)
        i, j = int(round(X1)), int(round(Y1))
        return [(X, Y) for Y in self.span_y(j) for X in self.span_x(i) if 0 <= X < self.w and 0 <= Y < self.h]

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
        X, Y = self._m(x, y)
        X, Y = int(round(X)), int(round(Y))
        if 0 <= X < self.w and 0 <= Y < self.h:
            return self.buf[Y][X]
        return None

    def line(self, x0, y0, x1, y1, mat, lvl):
        """Línia d'un píxel real."""
        X0, Y0 = self._m(x0, y0)
        X1, Y1 = self._m(x1, y1)
        n = max(1, int(math.ceil(max(abs(X1 - X0), abs(Y1 - Y0)))))
        for i in range(n + 1):
            t = i / n
            self.rpx(X0 + (X1 - X0) * t, Y0 + (Y1 - Y0) * t, mat, lvl)

    # ─── píxels reals (els detalls dibuixats a la mida nova) ───
    def rshade(self, X, Y, d, only=None):
        X, Y = int(round(X)), int(round(Y))
        if 0 <= X < self.w and 0 <= Y < self.h and self.buf[Y][X]:
            m, l = self.buf[Y][X]
            if only is None or m is only or (isinstance(only, (list, tuple)) and m in only):
                self.buf[Y][X] = (m, l + d)

    def rset(self, X, Y, v):
        X, Y = int(round(X)), int(round(Y))
        if 0 <= X < self.w and 0 <= Y < self.h:
            self.buf[Y][X] = v

    def rget(self, X, Y):
        X, Y = int(round(X)), int(round(Y))
        if 0 <= X < self.w and 0 <= Y < self.h:
            return self.buf[Y][X]
        return None


def big(fg):
    return getattr(fg, 'big', False)


# ═══════════════════════════════════════════════════════════════════════════
#  La cara, a la mida gran
# ═══════════════════════════════════════════════════════════════════════════
# A 1× l'ull és de 2×1 amb la parpella a sobre, els dos ulls a 4 px l'un de l'altre, la cella de 3 px, el nas d'ombres
# i la boca de 3 px. A ×1,5: l'ull de 3 px (blanc, iris i nineta) amb la parpella i una fila d'ombra a sota, els ulls a
# 6 px, la cella de 4, el nas d'ombres en tres files i la boca de 4. Mateixos colors (els del spec) i mateixa posició
# relativa dins el cap: la cara de sempre, no una de nova.

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
    row = [C.EYE_W, iris, dark] if inner_right else [dark, iris, C.EYE_W]
    if spec.get('mira'):                                 # mira a un costat: l'iris i la nineta, a aquella banda
        row = [dark, iris, C.EYE_W] if spec['mira'] < 0 else [C.EYE_W, iris, dark]
    for i, c in enumerate(row):
        fg.rpx(x0 + i, ey, c, 0)
    for i in range(3):                                   # la parpella de sota, una mica d'ombra
        fg.rshade(x0 + i, ey + 1, -0.45, S)


def _face_rows(fg, p):
    """(fila real dels ulls, x real del centre del cap): la fila dels ulls és la primera de la zona de la d'1×."""
    hx, hy = p.head
    yd = int(hy + 0.5)                                    # la fila dels ulls a 1× (front_face)
    ey = fg._zone(int(hx), yd)[0][1]
    X, _ = fg.m(hx, hy)
    return ey, X


def front_face_k(fg, p, spec):
    hx, hy = p.head
    S = spec['skin']
    brow = spec.get('brow', (40, 24, 28))
    eye = spec.get('eye', (34, 22, 30))
    ey, X = _face_rows(fg, p)
    # 1×: ulls a int(hx − 3,5) i int(hx + 2,5), de 2 px; aquí, la seva zona (3 px)
    lx = fg._zone(int(hx - 3.5), int(hy + 0.5))[0][0]
    rx = fg._zone(int(hx + 2.5), int(hy + 0.5))[0][0]
    closed = spec.get('closed')
    _eye(fg, lx, ey, True, spec, closed)                 # (1×: l'iris a la banda del nas, el blanc a fora)
    _eye(fg, rx, ey, False, spec, closed)
    if spec.get('lashes') and not closed:
        fg.rpx(lx - 1, ey - 1, eye, 0); fg.rpx(rx + 3, ey - 1, eye, 0)
        fg.rpx(lx - 1, ey - 2, eye, 0); fg.rpx(rx + 3, ey - 2, eye, 0)
    if spec.get('liner') and not closed:
        fg.rpx(lx - 1, ey, spec['liner'], 0); fg.rpx(rx + 3, ey, spec['liner'], 0)
        for i in range(2):
            fg.rpx(lx + i, ey + 1, spec['liner'], 0); fg.rpx(rx + 1 + i, ey + 1, spec['liner'], 0)
    # celles (1×: 3 px, la punta de fora un píxel més avall)
    by = ey - 4 + round(spec.get('brow_dy', 0) * K)
    for dx, dy in ((-1, 1), (0, 0), (1, 0), (2, 0)):
        fg.rpx(lx + dx, by + dy, brow, 0)
    for dx, dy in ((0, 0), (1, 0), (2, 0), (3, 1)):
        fg.rpx(rx + dx, by + dy, brow, 0)
    # nas: llum a l'esquerra del pont, ombra a la dreta i a sota (1×: la columna int(hx))
    nx = fg._zone(int(hx), int(hy + 0.5))[0][0]
    for y in range(ey + 1, ey + 4):
        fg.rshade(nx - 1, y, +0.5, S)
    fg.rshade(nx, ey + 3, -0.9, S); fg.rshade(nx + 1, ey + 3, -0.7, S)
    fg.rshade(nx, ey + 4, -1.1, S); fg.rshade(nx + 1, ey + 4, -0.9, S); fg.rshade(nx - 1, ey + 4, -0.5, S)
    if spec.get('blush'):
        fg.rshade(lx - 1, ey + 3, -0.4, S); fg.rshade(lx, ey + 3, -0.4, S)
        fg.rshade(rx + 2, ey + 3, -0.6, S); fg.rshade(rx + 3, ey + 3, -0.6, S)
    # boca (1×: 3 px a la fila ey + 5): 4 px
    my = ey + round(5 * K)
    lip = spec.get('lip', C.LIP)
    m0 = nx - 1
    if p.talk:
        for i in range(4):
            fg.rpx(m0 + i, my, C.MOUTH if 0 < i < 3 else lip, 0)
        fg.rpx(m0 + 1, my + 1, C.MOUTH, 0); fg.rpx(m0 + 2, my + 1, C.MOUTH, 0)
        fg.rpx(m0, my + 1, lip, 0); fg.rpx(m0 + 3, my + 1, lip, 0)
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
    ey, _ = _face_rows(fg, p)
    ex = fg._zone(int(hx - 3.5), yd)[0][0]               # 1×: l'ull a ex (iris) i ex − 1 (blanc)
    if spec.get('closed'):
        for i in range(3):
            fg.rpx(ex - 1 + i, ey, eye, 0)
    else:
        for i in range(3):
            fg.rpx(ex - 1 + i, ey - 1, eye, 0)
        fg.rpx(ex - 1, ey, C.EYE_W, 0); fg.rpx(ex, ey, iris, 0); fg.rpx(ex + 1, ey, mix(iris, eye, 0.55), 0)
        fg.rshade(ex - 1, ey + 1, -0.45, S); fg.rshade(ex, ey + 1, -0.45, S)
        if spec.get('lashes'):
            fg.rpx(ex + 2, ey - 1, eye, 0); fg.rpx(ex + 2, ey - 2, eye, 0)
        if spec.get('liner'):
            fg.rpx(ex + 2, ey, spec['liner'], 0); fg.rpx(ex, ey + 1, spec['liner'], 0)
    by = ey - 4 + round(spec.get('brow_dy', 0) * K)
    for dx, dy in ((-2, 0), (-1, 0), (0, 0), (1, 0), (2, 1)):
        fg.rpx(ex + dx, by + dy, brow, 0)
    # orella (amb el forat)
    ox_ = int(hx + 2.5)
    fg.ell(ox_ + 0.5, yd + 2, 1.6, 2.2, S, 2.6, amp=1.2)
    OX, OY = fg.m(ox_ + 0.5, yd + 2)
    fg.rshade(OX, OY - 0.5, -1.2, S); fg.rshade(OX, OY + 0.5, -0.9, S)
    if spec.get('blush'):
        fg.rshade(ex + 1, ey + 3, -0.4, S); fg.rshade(ex + 2, ey + 3, -0.4, S)
    # boca (1×: 2 px a int(hx − 5,5)): 3 px
    my = ey + round(5 * K)
    lip = spec.get('lip', C.LIP)
    mx = fg._zone(int(hx - 5.5), yd)[0][0]
    if p.talk:
        fg.rpx(mx, my, C.MOUTH, 0); fg.rpx(mx + 1, my, C.MOUTH, 0); fg.rpx(mx + 2, my, lip, 0)
        fg.rpx(mx + 1, my + 1, C.MOUTH, 0); fg.rpx(mx, my + 1, C.MOUTH, 0)
        fg.rset(mx - 1, my, None)                         # el llavi de baix cau: la boca oberta es veu de perfil
    else:
        fg.rpx(mx, my, lip, 0); fg.rpx(mx + 1, my, mix(lip, C.MOUTH, 0.5), 0)
        fg.rpx(mx + 2, my, mix(lip, C.MOUTH, 0.3), 0)


def head_side_k(fg, p, S, lvl=3.1):
    """`head_side` a ×K amb el nas més curt i rodó. El triangle del nas d'1×, rasteritzat petit, queda d'un píxel i
    arrodonit; dibuixat sencer a ×K sortia punxegut i massa llarg."""
    hx, hy = p.head
    fg.ell(hx + 0.8, hy, 6.8, 7.6, S, lvl, amp=1.5)
    fg.ell(hx - 1.6, hy + 3.4, 4.8, 4.8, S, lvl, amp=1.4)
    fg.ell(hx - 6.2, hy + 3.0, NAS_RX, NAS_RY, S, lvl + 0.3, amp=1.2)                # el nas: surt poc i és rodó
    fg.ell(hx - 4.6, hy + 6.4, 1.6, 1.4, S, lvl, amp=1.2)                         # barbeta


NAS_RX, NAS_RY = 1.1, 1.3


# ═══════════════════════════════════════════════════════════════════════════
#  El 3/4 a la mida gran
# ═══════════════════════════════════════════════════════════════════════════

def _gira_yk(fg, p, spec, S):
    """`_gira_y` d'arrel.py a ×K: les files i els desplaçaments, a la mida real."""
    P_ = fg.prop
    cx = fg.fx(A.CX)
    old = [row[:] for row in fg.buf]
    b = p.bob
    for Y in range(fg.h):
        yd = P_.inv(fg.gy(Y)) - b
        k, dx = C._q_dx(yd, p.q)
        row = old[Y]
        for X in range(fg.w):
            xs = cx + (X - cx - dx * K) / k
            i = int(round(xs))
            fg.buf[Y][X] = row[i] if 0 <= i < fg.w else None
    side = round(2 * K)                                  # (a 1×, les dues columnes de la dreta)
    for Y in range(fg.h):
        yd = P_.inv(fg.gy(Y)) - b
        if yd < 27:
            continue
        row = fg.buf[Y]
        xr = next((X for X in range(fg.w - 1, -1, -1) if row[X]), None)
        if xr is None:
            continue
        for X in range(xr, max(-1, xr - side), -1):
            if row[X]:
                m, l = row[X]
                row[X] = (m, l - 0.7)
    if p.q != 'DL':
        return
    hx, hy = p.head
    k, dx = C._q_dx(hy, p.q)
    p.head = (A.CX + (hx - A.CX) * k + dx + C.Q_DX_CARA, hy)
    front_face_k(fg, p, spec)
    # el nas a la silueta: un píxel de pell a l'esquerra de la galta, a les files del nas
    Ya, Yb = fg.m(hx, hy + 1.5)[1], fg.m(hx, hy + 3.5)[1]
    for Y in range(math.ceil(Ya), math.ceil(Yb)):
        if not 0 <= Y < fg.h:
            continue
        row = fg.buf[Y]
        xl = next((X for X in range(fg.w) if row[X] and row[X][0] is S), None)
        if xl is not None and xl - 1 >= 0:
            row[xl - 1] = (S, row[xl][1] + 0.4)
    p.head = (hx, hy)
    if 'face_q' in spec.get('hooks', {}):
        spec['hooks']['face_q'](fg, p, spec)


# ═══════════════════════════════════════════════════════════════════════════
#  Una persona a la mida gran
# ═══════════════════════════════════════════════════════════════════════════

@contextmanager
def _gran(spec, sub):
    prop = spec.get('prop', A.ADULT)
    cls = type('FigPK', (FigYK,), {'prop': prop, 'sub': sub})
    saved = C.Fig, C._gira, C.front_face, C.side_face, C.head_side
    C.Fig, C._gira, C.front_face, C.side_face, C.head_side = cls, _gira_yk, front_face_k, side_face_k, head_side_k
    try:
        yield
    finally:
        C.Fig, C._gira, C.front_face, C.side_face, C.head_side = saved


def figura(spec, facing, walk=None, talk=False, sub=(0.0, 0.0)):
    """`arrel.figura` a ×K: imatge RGBA de ⌈49·K⌉+1 × ⌈95·K⌉+1. Un punt d'1× (vora de píxel) X va a X·K + sub."""
    with _gran(spec, sub):
        return C.person(spec, facing, walk=walk, talk=talk)


def respira(img, spec, k, sub=(0.0, 0.0)):
    """`arrel.respira` a ×K: la clariana del pit puja i baixa, a les files del pit de la figura gran."""
    if not k:
        return img
    prop = spec.get('prop', A.ADULT)
    fx = lambda X: (X + 0.5) * K - 0.5 + sub[0]  # noqa: E731
    fy = lambda Y: (Y + 0.5) * K - 0.5 + sub[1]  # noqa: E731
    y0, y1 = round(fy(prop.y(30) - 0.5) + 0.5), round(fy(prop.y(41) - 0.5) + 0.5)
    x0, x1 = round(fx(prop.x(13, 35) - 0.5) + 0.5), round(fx(prop.x(36, 35) - 0.5) + 0.5)
    out = img.copy()
    P_ = out.load()
    for y in range(y0, y1):
        f = 1 + k * (1 - (y - y0) / max(1, y1 - y0))
        for x in range(x0, x1):
            r, g, b, a = P_[x, y]
            if a:
                P_[x, y] = (min(255, int(r * f)), min(255, int(g * f)), min(255, int(b * f)), a)
    return out
