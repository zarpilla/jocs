#!/usr/bin/env python3
"""
Personatges de Ferro-9 a 640×360: els mateixos de hd/characters.py, redibuixats a ×4/3
(una persona fa ≈110 px; fotograma de 65×116, peus a (34, 111); en Cargol, 73×84; el capatàs, 87×109; MARE, 29×29).

No canvia res de la sortida de 480: en aquest procés se substitueix la figura de hd/characters.py (Fig) per
FigK, que rep les mateixes ordres en coordenades de 480 (les de 49×87) i les rasteritza a la mida gran:
  - el·lipsoides, extremitats, troncs i polígons es tornen a dibuixar a la resolució nova (amb volum i
    contorn d'un píxel real), no s'amplien;
  - els píxels solts (`px`, `shade`) ocupen la seva zona (1 o 2 píxels reals);
  - les línies són d'un píxel real.
El que és de píxel solt es redibuixa a part, píxel a píxel a la mida nova: la cara (ulls, celles, nas, boca) i la
boca que es torna a pintar sobre les barbes i els bigotis; els vidres de les ulleres de l'Iri, el llapis, el
bolígraf i la clau de la bata; el número de les plaques de les granotes; el pin i els botons de la directora; la
clau anglesa de la Mira; la placa i l'escut de la guàrdia; la reixa, els ulls, els reblons i la lluentor d'en Cargol;
la cara, els botons i les zetes del capatàs; els forats i el halo de MARE.

Ús (des de tools/): python3 hd640/draw_characters.py [carpeta]   (per defecte, hd640/characters/)

Per a les sales de 640 que dibuixen gent (hd640/rooms), aquest mòdul exporta:
  person(spec, facing='D', walk=None, talk=False)       hd.characters.person a ×4/3 (els ganxos de l'espec es
                                                        canvien pels de 640, també els d'especs fetes a les sales)
  cargol(facing, blink=False, talk=False, old=False)    73×84, erugues a terra a (36, 80)
  capatas(breath=0, with_seal=True, talk=False, zz=0)   87×109, peus a (44, 106)
  mare(glow=False)                                      29×29
  FigK(w, h)        la figura (mateixes ordres que hd.characters.Fig, en coordenades de 480) que dibuixa a ×4/3;
                    amb `with escala(k):` dibuixa a una altra escala (p. ex. K * s per a una figura de mida s).
  rpx, rshade, rline, rrow, rget   (mètodes de FigK) per als detalls en píxels reals; fg.F(u) / fg.G(X) passen
                    de coordenades de 480 a reals i al revés.
  redo_mouth(fg, p, spec)          la boca de 640 (la de la cara nova), per sobre d'una barba o un bigoti
  front_face, side_face            la cara de 640
  K, f, g           4/3 i les conversions de coordenada (centre de píxel) 480 → 640 i 640 → 480
  i, tal qual, tot el que no depèn de la mida: M, Mat, materials (SKIN_*, ORANGE, HAIR_*, CHROME...), Pose,
  hair_lvl, spiral_lvl, curl_lvl, front_normal, fold, waist_band, patch, torso_edges, side_torso_edges, les especs
  (IRI, VET, MOS...) i els ganxos (ja canviats pels de 640).
"""
import math
import sys
import types
from contextlib import contextmanager
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))

from PIL import Image  # noqa: E402

import hd640  # noqa: E402,F401  (abans que cap hd.*: posa la llibreria de dibuix a 640×360)
import hd.characters as C  # noqa: E402
from hd.characters import *  # noqa: E402,F401,F403  (materials, especs, ajudes: no depenen de la mida)
from hd.characters import (Mat, M, Pose, hair_lvl, spiral_lvl, curl_lvl, front_normal, fold,  # noqa: E402,F401
                           torso_edges, side_torso_edges, waist_band, patch as _patch480, B4, mix)

K = 4 / 3
Fig480 = C.Fig


def f(u):
    """Coordenada de 480 (centre de píxel) → coordenada real de 640."""
    return (u + 0.5) * K - 0.5


def g(X):
    """Coordenada real de 640 → de 480."""
    return (X + 0.5) / K - 0.5


class FigK(Fig480):
    """Fig que dibuixa a ×k (k = 4/3, o la de `escala`). `w`, `h` i `buf` són a la mida real; les ordres
    (ell, limb, lathe, poly, px, shade, line, get, erase) són en coordenades de 480, com a hd.characters."""
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
        """Els contorns de 480 (una parella per fila) s'interpolen entre files."""
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
        # lvlfn rep coordenades de 480 (com a hd/), però es crida per a cada píxel real
        if lvlfn:
            fn, G = lvlfn, self.G
            lvlfn = lambda x, y: fn(G(x), G(y))  # noqa: E731
        super()._paint(pix, mat, base, amp, cont, lvlfn)

    # píxels de 480: ocupen la seva zona
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
        self.rline(F(x0 + self.ox), F(y0 + self.oy), F(x1 + self.ox), F(y1 + self.oy), mat, lvl)

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


@contextmanager
def escala(k):
    """Dibuixa les figures a ×k mentre dura (k = K * s per a una figura s vegades la de 480)."""
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
    return fg.F(hx + fg.ox), round(fg.F(int(hy + 0.5) + fg.oy))


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


def front_face(fg, p, spec):
    S = spec['skin']
    HX, ey = face_xy(fg, p)
    brow = spec.get('brow', (40, 24, 28))
    eye = spec.get('eye', (34, 22, 30))
    lx, rx, _, nx = front_eyes(fg, p)                   # els ulls: 3 px, separats 5 px
    closed = spec.get('closed')
    _eye(fg, lx, ey, True, spec, closed)
    _eye(fg, rx, ey, False, spec, closed)
    if spec.get('lashes') and not closed:
        fg.rpx(lx - 1, ey - 2, eye, 0); fg.rpx(lx - 1, ey - 1, eye, 0)
        fg.rpx(rx + 3, ey - 2, eye, 0); fg.rpx(rx + 3, ey - 1, eye, 0)
    if spec.get('liner'):                               # el maquillatge (en Mos): ratlla als cantons i a sota
        liner = spec['liner']
        fg.rpx(lx - 1, ey, liner, 0); fg.rpx(rx + 3, ey, liner, 0)
        fg.rpx(lx, ey + 2, liner, 0); fg.rpx(lx + 1, ey + 2, liner, 0)
        fg.rpx(rx + 1, ey + 2, liner, 0); fg.rpx(rx + 2, ey + 2, liner, 0)
    # celles: quatre píxels en arc
    by = ey - 4 + round(spec.get('brow_dy', 0) * K)
    for dx, dy in ((-1, 1), (0, 0), (1, 0), (2, 0)):
        fg.rpx(lx + dx, by + dy, brow, 0)
    for dx, dy in ((0, 0), (1, 0), (2, 0), (3, 1)):
        fg.rpx(rx + dx, by + dy, brow, 0)
    # nas: llum a l'esquerra del pont, ombra a la dreta i a sota
    for y in range(ey, ey + 3):
        fg.rshade(nx - 1, y, +0.5, S)
    fg.rshade(nx + 1, ey + 2, -0.7, S); fg.rshade(nx + 1, ey + 3, -0.9, S)
    fg.rshade(nx, ey + 4, -1.1, S); fg.rshade(nx - 1, ey + 4, -0.6, S); fg.rshade(nx + 1, ey + 4, -0.8, S)
    fg.rshade(nx - 2, ey + 4, -0.3, S)
    if spec.get('blush'):
        fg.rshade(lx - 1, ey + 3, -0.4, S); fg.rshade(lx, ey + 3, -0.4, S)
        fg.rshade(rx + 2, ey + 3, -0.6, S); fg.rshade(rx + 3, ey + 3, -0.6, S)
    _front_mouth(fg, p, spec, nx - 2, ey + 7)


def _front_mouth(fg, p, spec, m0, my, skin_shade=True):
    """La boca de cara: quatre píxels; parlant, oberta."""
    S = spec['skin']
    lip = spec.get('lip', C.LIP)
    if p.talk:
        for i in range(4):
            fg.rpx(m0 + i, my, C.MOUTH if 0 < i < 3 else lip, 0)
        fg.rpx(m0 + 1, my + 1, C.MOUTH, 0); fg.rpx(m0 + 2, my + 1, C.MOUTH, 0)
        fg.rpx(m0, my + 1, lip, 0); fg.rpx(m0 + 3, my + 1, lip, 0)
        fg.rpx(m0 + 1, my + 2, lip, 0); fg.rpx(m0 + 2, my + 2, lip, 0)
    else:
        for i in range(4):
            fg.rpx(m0 + i, my, mix(lip, C.MOUTH, 0.5) if 0 < i < 3 else lip, 0)
        if skin_shade:
            fg.rshade(m0 + 1, my + 1, +0.4, S); fg.rshade(m0 + 2, my + 1, +0.4, S)
            fg.rshade(m0 + 1, my + 2, -0.3, S); fg.rshade(m0 + 2, my + 2, -0.3, S)


def side_face(fg, p, spec):
    hx, hy = p.head
    S = spec['skin']
    HX, ey = face_xy(fg, p)
    eye = spec.get('eye', (34, 22, 30))
    iris = spec.get('iris', (70, 50, 40))
    brow = spec.get('brow', (40, 24, 28))
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
            fg.rpx(ex + 2, ey - 2, eye, 0); fg.rpx(ex + 2, ey - 1, eye, 0)
        if spec.get('liner'):
            fg.rpx(ex + 2, ey, spec['liner'], 0)
            fg.rpx(ex, ey + 2, spec['liner'], 0); fg.rpx(ex + 1, ey + 2, spec['liner'], 0)
    by = ey - 4 + round(spec.get('brow_dy', 0) * K)
    for dx, dy in ((-2, 0), (-1, 0), (0, 0), (1, 1)):
        fg.rpx(ex + dx, by + dy, brow, 0)
    # orella (amb el forat)
    oxd, eyd = int(hx + 2.5) + 0.5, int(hy + 0.5)
    fg.ell(oxd, eyd + 2, 1.6, 2.2, S, 2.6, amp=1.2)
    fg.rshade(fg.F(oxd + fg.ox), fg.F(eyd + 2 + fg.oy) - 0.5, -1.2, S)
    fg.rshade(fg.F(oxd + fg.ox), fg.F(eyd + 2 + fg.oy) + 0.5, -0.9, S)
    if spec.get('blush'):
        fg.rshade(ex + 2, ey + 3, -0.4, S); fg.rshade(ex + 3, ey + 3, -0.4, S)
    _side_mouth(fg, p, spec, round(HX - 8.0), ey + 7)


def _side_mouth(fg, p, spec, mx, my, erase=True):
    lip = spec.get('lip', C.LIP)
    if p.talk:
        fg.rpx(mx, my, C.MOUTH, 0); fg.rpx(mx + 1, my, C.MOUTH, 0); fg.rpx(mx + 2, my, lip, 0)
        fg.rpx(mx + 1, my + 1, C.MOUTH, 0); fg.rpx(mx + 2, my + 1, lip, 0)
        if erase and fg.rget(mx - 1, my) and fg.rget(mx - 1, my)[0] is spec['skin']:
            fg.buf[my][mx - 1] = None
    else:
        fg.rpx(mx, my, lip, 0); fg.rpx(mx + 1, my, mix(lip, C.MOUTH, 0.5), 0); fg.rpx(mx + 2, my, mix(lip, C.MOUTH, 0.3), 0)


def redo_mouth(fg, p, spec):
    """Torna a pintar la boca de 640 (quan una barba o un bigoti l'han tapada)."""
    HX, ey = face_xy(fg, p)
    if p.f == 'D':
        _front_mouth(fg, p, spec, round(HX - 0.5) - 2, ey + 7, skin_shade=False)
    elif p.f == 'L':
        _side_mouth(fg, p, spec, round(HX - 8.0), ey + 7, erase=False)


def patch(fg, x, y, w=6, h=5, digits=((2, 1), (3, 1), (2, 2), (4, 2), (3, 3), (4, 3))):
    """La placa amb el número de presó: el rectangle, i les xifres (les de 480) en traços d'un píxel real
    (els píxels de xifra que es toquen, units)."""
    fg.poly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], SNEAKER, 3.4)
    ink = (36, 36, 48)
    F = fg.F

    def at(dx, dy):
        return round(F(x + dx - 0.5 + fg.ox)), round(F(y + dy + fg.oy))
    for dx, dy in digits:
        fg.rpx(*at(dx, dy), ink, 0)
        for ddx, ddy in ((1, 0), (0, 1), (1, 1), (-1, 1)):
            if (dx + ddx, dy + ddy) in digits:
                fg.rline(*at(dx, dy), *at(dx + ddx, dy + ddy), ink, 0)


def _digit9(fg, X, Y, ink=(36, 36, 48)):
    """Un 9 de 3×5 píxels reals amb la cantonada de dalt a (X, Y)."""
    for dx, dy in ((0, 0), (1, 0), (2, 0), (0, 1), (2, 1), (0, 2), (1, 2), (2, 2), (2, 3), (1, 4), (0, 4)):
        fg.rpx(X + dx, Y + dy, ink, 0)


# ─── Els ganxos de hd/characters.py redibuixats a la mida nova ──────────────

def _ganxos():
    """Les versions de 640 dels ganxos de hd/characters.py: {nom: funció}. Criden els de 480 (sense els
    detalls de píxel solt) i hi pinten els detalls a la mida nova."""
    O480 = {n: getattr(C, n) for n in ('iri_hair', 'iri_coat', 'vet_suit', 'directora_suit', 'mira_overalls',
                                       'guardia_hair', 'guardia_uniform', 'sic_coat')}

    def iri_hair(fg, p, spec):
        """El cabell de l'Iri, amb les ulleres al front: el vidre amb el reflex d'un píxel real."""
        O480["iri_hair"](fg, p, spec)
        hx, hy = p.head
        if p.f == 'D':
            for gx in (hx - 3.0, hx + 3.0):
                fg.ell(gx, hy - 5.4, 1.5, 1.3, C.LENS, 2.4, amp=1.8)
                X, Y = fg.F(gx + fg.ox), fg.F(hy - 5.4 + fg.oy)
                fg.rpx(X - 1, Y - 1, C.LENS, 4.5); fg.rpx(X, Y - 1, C.LENS, 3.6)
        elif p.f == 'L':
            X, Y = fg.F(hx - 4.8 + fg.ox), fg.F(hy - 5.8 + fg.oy)
            fg.rpx(X - 0.4, Y - 1, C.LENS, 4.5)

    def iri_coat(fg, p, spec):
        """La bata: el llapis i el bolígraf a la butxaca del pit i la clau a la de baix, en píxels reals."""
        if p.f != 'D':
            return O480["iri_coat"](fg, p, spec)
        # la bata de 480, sense els detalls de píxel solt (es tornen a pintar a sobre)
        saved = fg.px
        fg.px = lambda x, y, mat, lvl: None if mat in (C.RED, C.SHIRT_BLUE, C.STEELB) else saved(x, y, mat, lvl)
        try:
            O480["iri_coat"](fg, p, spec)
        finally:
            fg.px = saved
        b, hx, F = p.bob, 24.5, fg.F
        top = round(F(35 + b + fg.oy))                                    # la vora de la butxaca
        X = round(F(hx + 5 + fg.ox))
        for i, lvl in enumerate((3.4, 3.0, 2.4, 1.6, 1.0)):              # el llapis vermell, amb la punta
            fg.rpx(X, top - 5 + i, C.RED, lvl)
        fg.rpx(X, top - 6, (230, 200, 150), 0)
        X = round(F(hx + 7 + fg.ox))
        for i, lvl in enumerate((3.4, 2.6, 2.0)):                         # el bolígraf blau, amb el clip
            fg.rpx(X, top - 3 + i, C.SHIRT_BLUE, lvl)
        fg.rpx(X + 1, top - 3, C.STEELB, 3.4)
        X, Y = round(F(hx - 8 + fg.ox)), round(F(52 + b + fg.oy))       # la clau, que penja de la butxaca
        for dx, dy, lvl in ((0, -2, 3.0), (1, -2, 2.4), (-1, -1, 3.4), (2, -1, 2.0), (0, 0, 2.6), (1, 0, 1.6),
                            (0, 1, 4.0), (0, 2, 3.4), (1, 2, 3.0)):
            fg.rpx(X + dx, Y + dy, C.STEELB, lvl)

    def vet_suit(fg, p, spec):
        """La granota: el 9 de la placa, de 3×5 píxels reals."""
        if p.f != 'D':
            return O480["vet_suit"](fg, p, spec)
        ink = (36, 36, 48)
        saved = fg.px
        fg.px = lambda x, y, mat, lvl: None if mat == ink else saved(x, y, mat, lvl)
        try:
            O480["vet_suit"](fg, p, spec)
        finally:
            fg.px = saved
        b, hx, F = p.bob, 24.5, fg.F
        x0, x1 = F(hx + 3 + fg.ox), F(hx + 9 + fg.ox)
        y0, y1 = F(33 + b + fg.oy), F(38 + b + fg.oy)
        _digit9(fg, round((x0 + x1) / 2) - 1, round((y0 + y1) / 2) - 2, ink)

    def directora_suit(fg, p, spec):
        """El vestit: els botons d'or i el pin de la solapa, en píxels reals."""
        saved = fg.px
        fg.px = lambda x, y, mat, lvl: None if mat is C.GOLDPIN else saved(x, y, mat, lvl)
        try:
            O480["directora_suit"](fg, p, spec)
        finally:
            fg.px = saved
        b, hx, F = p.bob, 24.5, fg.F
        if p.f == 'D':
            for y in (40, 45):                                          # botons: 2×2, amb la llum a dalt
                X, Y = round(F(hx - 0.5 + fg.ox)), round(F(y + b + fg.oy))
                fg.rpx(X, Y, C.GOLDPIN, 2.6); fg.rpx(X + 1, Y, C.GOLDPIN, 1.6)
                fg.rpx(X, Y + 1, C.GOLDPIN, 1.2); fg.rpx(X + 1, Y + 1, C.GOLDPIN, 0.4)
            X, Y = round(F(hx + 5 + fg.ox)), round(F(31 + b + fg.oy))   # el pin: un rombe petit
            for dx, dy, lvl in ((1, 0, 3.4), (0, 1, 3.0), (1, 1, 2.2), (2, 1, 1.6), (1, 2, 1.0)):
                fg.rpx(X + dx, Y + dy, C.GOLDPIN, lvl)
        elif p.f == 'L':
            X, Y = round(F(21 + fg.ox)), round(F(31 + b + fg.oy))
            fg.rpx(X, Y, C.GOLDPIN, 3.4); fg.rpx(X + 1, Y, C.GOLDPIN, 2.2); fg.rpx(X, Y + 1, C.GOLDPIN, 1.6)

    def mira_overalls(fg, p, spec):
        """El pitet: els botons dels tirants i la clau anglesa a la butxaca, en píxels reals."""
        saved = fg.px
        fg.px = lambda x, y, mat, lvl: None if mat is C.STEELB else saved(x, y, mat, lvl)
        try:
            O480["mira_overalls"](fg, p, spec)
        finally:
            fg.px = saved
        b, hx, F = p.bob, 24.5, fg.F
        ST = C.STEELB

        def button(x, y, lvl):
            X, Y = round(F(x + fg.ox) - 0.5), round(F(y + b + fg.oy) - 0.5)
            fg.rpx(X, Y, ST, lvl + 0.6); fg.rpx(X + 1, Y, ST, lvl - 0.4)
            fg.rpx(X, Y + 1, ST, lvl - 0.6); fg.rpx(X + 1, Y + 1, ST, lvl - 1.4)
        if p.f == 'D':
            button(hx - 5, 34, 3.6); button(hx + 5, 34, 2.8)
            X, Y = round(F(hx + 1 + fg.ox)), round(F(36 + b + fg.oy))   # la clau anglesa: el cap obert i el mànec
            for dx, dy, lvl in ((0, -1, 3.4), (2, -1, 2.6), (0, 0, 2.8), (1, 0, 2.4), (2, 0, 2.0),
                                (1, 1, 2.2), (1, 2, 1.6)):
                fg.rpx(X + dx, Y + dy, ST, lvl)
        elif p.f == 'L':
            button(21, 36, 3.0)

    def guardia_hair(fg, p, spec):
        """La gorra: l'escut d'or, en píxels reals."""
        saved = fg.px
        fg.px = lambda x, y, mat, lvl: None if mat is C.GOLDPIN else saved(x, y, mat, lvl)
        try:
            O480["guardia_hair"](fg, p, spec)
        finally:
            fg.px = saved
        hx, hy = p.head
        F = fg.F
        if p.f == 'D':
            X, Y = round(F(hx + fg.ox)), round(F(hy - 7.5 + fg.oy))
            for dx, dy, lvl in ((0, 0, 3.4), (-1, 1, 3.0), (0, 1, 2.6), (1, 1, 2.0), (-1, 2, 2.2), (0, 2, 1.8),
                                (1, 2, 1.4), (0, 3, 1.0)):
                fg.rpx(X + dx, Y + dy, C.GOLDPIN, lvl)
        elif p.f == 'L':
            X, Y = round(F(hx - 4.0 + fg.ox)), round(F(hy - 6.5 + fg.oy))
            fg.rpx(X, Y, C.GOLDPIN, 3.4); fg.rpx(X, Y + 1, C.GOLDPIN, 2.2); fg.rpx(X + 1, Y + 1, C.GOLDPIN, 1.4)

    def guardia_uniform(fg, p, spec):
        """L'uniforme: la placa (amb la seva vora i el relleu), els botons i la sivella, en píxels reals."""
        saved = fg.px
        fg.px = lambda x, y, mat, lvl: None if mat is C.STEELB or (mat is C.GOLDPIN and lvl == 3.4) else saved(x, y, mat, lvl)
        try:
            O480["guardia_uniform"](fg, p, spec)
        finally:
            fg.px = saved
        b, hx, F = p.bob, 24.5, fg.F
        ST = C.STEELB
        if p.f == 'D':
            for y in (32, 36, 40):                                       # botons
                X, Y = round(F(hx - 1 + fg.ox)), round(F(y + b + fg.oy))
                fg.rpx(X, Y, ST, 3.4); fg.rpx(X, Y + 1, ST, 1.8)
            X, Y = round(F(hx + 4.5 + fg.ox)), round(F(32.5 + b + fg.oy))   # la placa: la lluentor del cantell
            fg.rpx(X, Y, C.GOLDPIN, 3.4); fg.rpx(X + 1, Y, C.GOLDPIN, 3.0); fg.rpx(X, Y + 1, C.GOLDPIN, 2.8)
            X, Y = round(F(hx + fg.ox)), round(F(45 + b + fg.oy))      # la sivella
            for dx in (-1, 0, 1):
                fg.rpx(X + dx, Y, ST, 4 - dx * 0.5); fg.rpx(X + dx, Y + 1, ST, 2.6)
            fg.rpx(X - 1, Y + 1, ST, 3.0); fg.rpx(X + 1, Y + 1, ST, 2.0)
        elif p.f == 'L':
            X, Y = round(F(23 + fg.ox)), round(F(45 + b + fg.oy))
            fg.rpx(X, Y, ST, 3.4); fg.rpx(X + 1, Y, ST, 2.6); fg.rpx(X, Y + 1, ST, 2.2); fg.rpx(X + 1, Y + 1, ST, 1.6)

    def sic_coat(fg, p, spec):
        """La gavardina: la corbata, els botons i la sivella en píxels reals."""
        saved = fg.px

        def px(x, y, mat, lvl):
            if mat is C.RED or mat is C.BRASS or (mat is C.BELT and lvl == 2):
                return
            saved(x, y, mat, lvl)
        fg.px = px
        try:
            O480["sic_coat"](fg, p, spec)
        finally:
            fg.px = saved
        if p.f != 'D':
            return
        b, hx, F = p.bob, 24.5, fg.F
        X, Y = round(F(hx + fg.ox)), round(F(29 + b + fg.oy))              # la corbata: el nus i la pala
        fg.rpx(X, Y, C.RED, 2.4); fg.rpx(X + 1, Y, C.RED, 1.8)
        for i in range(1, 4):
            fg.rpx(X, Y + i, C.RED, 2.0 - i * 0.3); fg.rpx(X + 1, Y + i, C.RED, 1.4 - i * 0.3)
        for y in (38, 42, 50, 56):                                         # botons, de dos en dos
            for x in (hx - 3, hx + 5):
                XX, YY = round(F(x + fg.ox)), round(F(y + b + fg.oy))
                fg.rpx(XX, YY, C.BELT, 2.6); fg.rpx(XX + 1, YY, C.BELT, 1.8)
                fg.rpx(XX, YY + 1, C.BELT, 1.4); fg.rpx(XX + 1, YY + 1, C.BELT, 0.8)
        X, Y = round(F(hx - 1 + fg.ox)), round(F(45 + b + fg.oy))          # la sivella de llautó
        for dx, dy, lvl in ((0, -1, 3.4), (1, -1, 3.0), (2, -1, 2.6), (0, 0, 2.8), (2, 0, 1.8),
                            (0, 1, 2.0), (1, 1, 1.6), (2, 1, 1.2)):
            fg.rpx(X + dx, Y + dy, C.BRASS, lvl)

    return {'iri_hair': iri_hair, 'iri_coat': iri_coat, 'vet_suit': vet_suit, 'directora_suit': directora_suit,
            'mira_overalls': mira_overalls, 'guardia_hair': guardia_hair, 'guardia_uniform': guardia_uniform,
            'sic_coat': sic_coat}


# ─── En Cargol (robot), a la mida nova ──────────────────────────────────────

def cargol(facing, blink=False, talk=False, old=False):
    """En Cargol a ×4/3 (73×84, erugues a terra a (36, 80)): els volums com a 480; la reixa de la boca, els
    reblons, els ulls, la lluentor de la closca i els forats de les rodes, en píxels reals."""
    install()
    fg = FigK(55, 63)
    ST = C.RUSTY if old else C.CHROME
    BR = C.RUST_BRASS if old else C.BRASS
    LP = C.LAMP_OLD if old else C.LAMP
    RUBBER, SCREEN = C.RUBBER, C.SCREEN
    F = fg.F
    lamp_lvl = 1.0 if blink else (4.0 if talk else 3.0)
    if old:
        lamp_lvl -= 0.6
    up = -1 if talk else 0

    def tracks(x0, x1, side):
        Y0, Y1 = round(F(50)), round(F(60))
        fg.poly([(x0 + 2, 50), (x1 - 2, 50), (x1, 53), (x1, 58), (x1 - 2, 60), (x0 + 2, 60), (x0, 58), (x0, 53)], RUBBER, 2.4,
                amp=1.4, normal=lambda x, y: (0, (y - 55) / 6, 0.8), cont=(0.3, 0.8))
        # les dents de l'eruga: un píxel clar de cada quatre, a dalt i a baix (desfasades)
        for X in range(round(F(x0)), round(F(x1)) + 1):
            for Y, ph in ((Y0, 0), (Y0 + 1, 0), (Y1 - 1, 2), (Y1, 2)):
                if (X + ph) % 4 == 0:
                    fg.rshade(X, Y, 0.9, RUBBER)
        if side:
            for wx in range(x0 + 4, x1 - 2, 6):
                fg.ell(wx, 55, 2.4, 2.4, ST, 2.6, amp=1.6)
                X, Y = round(F(wx)), round(F(55))                    # el boixó, amb el cargol al mig
                fg.rpx(X, Y, ST, 0.6); fg.rpx(X + 1, Y, ST, 1.0); fg.rpx(X, Y + 1, ST, 1.0)
                fg.rpx(X - 1, Y - 1, ST, 4.0)

    def antenna(bx, by, tx, ty):
        X0, Y0, X1, Y1 = round(F(bx)), F(by), round(F(tx)), F(ty + 2)        # la tija: dos píxels reals
        fg.rline(X0, Y0, X1, Y1, ST, 2.2)
        fg.rline(X0 + 1, Y0, X1 + 1, Y1, ST, 3.6)
        fg.ell(tx + 0.5, ty, 3.0, 3.0, ST, 2.8, amp=1.6)
        fg.ell(tx + 0.5, ty, 2.0, 2.0, LP, lamp_lvl, amp=1.2)
        if not blink:
            X, Y = F(tx + 0.5), F(ty)
            fg.rpx(X - 1, Y - 1, LP, 4.6); fg.rpx(X - 1, Y - 2, LP, 4.0); fg.rpx(X - 2, Y - 1, LP, 4.0)

    def shine(x, y):
        if old:
            return
        X, Y = round(F(x)), round(F(y))                                # una estrelleta: creu de 5 i el centre ple
        for dx, dy, lvl in ((0, 0, 7), (-1, 0, 6), (1, 0, 6), (0, -1, 6), (0, 1, 6), (-2, 0, 5), (2, 0, 5),
                            (0, -2, 5), (0, 2, 5)):
            fg.rpx(X + dx, Y + dy, C.CHROME, lvl)

    def rivet(x, y):
        X, Y = round(F(x)), round(F(y))
        fg.rpx(X, Y, ST, 1.0); fg.rpx(X - 1, Y - 1, ST, 4.2)

    def grille(x0, x1, y):
        """La reixa de la boca: barretes de dos píxels, cada tres; parlant, s'encenen."""
        Y = round(F(y))
        for X in range(round(F(x0)), round(F(x1)) + 1, 3):
            for dx in (0, 1):
                if talk:
                    fg.rpx(X + dx, Y, LP, 2.4 - dx * 0.4); fg.rpx(X + dx, Y + 1, LP, 1.6 - dx * 0.4)
                else:
                    fg.rpx(X + dx, Y, ST, 3.4 - dx * 0.6); fg.rpx(X + dx, Y + 1, ST, 1.6)

    def eye(ex, ey, rx):
        fg.ell(ex, ey, rx, 2.0 if not blink else 0.6, LP, lamp_lvl, amp=1.0)
        if not blink:
            X, Y = F(ex), F(ey)
            fg.rpx(X - 1, Y - 1, LP, lamp_lvl + 1.4)

    if facing == 'D':
        tracks(9, 21, False)
        tracks(33, 45, False)
        fg.ell(27, 28, 17, 15, BR, 2.8, amp=1.6, lvlfn=spiral_lvl(27, 28, 5.0), cont=(0, 0.8))   # closca, darrere
        fg.lathe(22, 52, lambda y: (17 - max(0, 25 - y) * 1.2, 37 + max(0, 25 - y) * 1.2) if y <= 50 else (19, 35), ST, 3.0, amp=1.8,
                 cont=(0.2, 1.0))
        fg.poly([(19, 28), (35, 28), (35, 40), (19, 40)], SCREEN, 1.6, cont=(1.0, -0.8))             # pantalla
        for ex in (23, 31):
            eye(ex, 32.5, 2.2)
        grille(22, 32, 37 + up)
        for X in range(round(F(18)), round(F(36)) + 1):                                          # junta
            fg.rshade(X, round(F(44)), -1.2, ST); fg.rshade(X, round(F(44)) + 1, -0.4, ST)
            fg.rshade(X, round(F(45)) + 1, 0.8, ST)
        for (x, y) in ((19, 47), (35, 47), (19, 25), (35, 25)):
            rivet(x, y)
        # braços
        fg.limb((15.5, 31), (11.5, 41), 1.8, 1.6, ST, 2.6, amp=1.6, cont=(0.2, 0.8))
        fg.ell(11.5, 42, 2.2, 1.8, ST, 2.2, amp=1.4)
        fg.limb((38.5, 31), (43, 40), 1.8, 1.6, ST, 2.4, amp=1.6, cont=(0.2, 0.8))
        fg.limb((43.5, 38), (44.5, 48), 1.3, 1.3, ST, 3.4, amp=1.6)                               # clau anglesa
        fg.ell(44.5, 49.5, 2.4, 2.0, ST, 3.0, amp=1.4)
        X = round(F(44.5))                                                                         # la boca de la clau
        for Y in range(round(F(49.8)), round(F(51.5)) + 1):
            for dx in (-1, 0, 1):
                fg.buf[Y][X + dx] = None
        antenna(21, 22, 19, 9 + up)
        antenna(33, 22, 35, 9 + up)
        shine(19, 26)
    elif facing == 'L':
        tracks(8, 42, True)
        fg.lathe(22, 51, lambda y: (12 + max(0, 25 - y) * 1.0, 30), ST, 3.0, amp=1.8, cont=(0.2, 1.0))
        fg.poly([(12, 28), (19, 28), (19, 40), (12, 40)], SCREEN, 1.6, cont=(1.0, -0.8))
        eye(15, 32.5, 1.8)
        grille(13, 18, 37 + up)
        fg.ell(36, 30, 15, 16, BR, 2.8, amp=1.6, lvlfn=spiral_lvl(37, 29, 4.4), cont=(0.2, 1.0))     # closca
        fg.ell(37, 29, 2.4, 2.4, BR, 1.2, amp=0.8)
        for X in range(round(F(12)), round(F(30)) + 1):
            fg.rshade(X, round(F(44)), -1.2, ST); fg.rshade(X, round(F(44)) + 1, -0.4, ST)
            fg.rshade(X, round(F(45)) + 1, 0.8, ST)
        fg.limb((22, 32), (13, 39), 1.8, 1.6, ST, 2.8, amp=1.6, cont=(0.3, 1.0))
        fg.limb((12, 39), (8, 46), 1.3, 1.3, ST, 3.4, amp=1.6)
        fg.ell(7.5, 47.5, 2.2, 1.8, ST, 3.0, amp=1.4)
        antenna(16, 22, 12, 9 + up)
        antenna(21, 22, 21, 7 + up)
        rivet(13, 47)
        shine(19, 26)
    else:
        tracks(9, 21, False)
        tracks(33, 45, False)
        fg.lathe(30, 52, lambda y: (17, 37), ST, 2.6, amp=1.8, cont=(0.2, 1.0))
        fg.limb((15.5, 33), (11.5, 42), 1.8, 1.6, ST, 2.2, amp=1.6)
        fg.limb((38.5, 33), (43, 42), 1.8, 1.6, ST, 2.0, amp=1.6)
        fg.ell(27, 30, 17, 17, BR, 2.8, amp=1.6, lvlfn=spiral_lvl(27, 30, 4.6), cont=(0, 0.8))
        fg.ell(27, 30, 2.6, 2.6, BR, 1.2, amp=0.8)
        antenna(21, 14, 19, 8 + up)
        antenna(33, 14, 35, 8 + up)
    if old:
        # taques de rovell (d'uns quants píxels), una abonyegadura i un cargol que hi falta
        for (x, y) in ((24, 47), (25, 48), (31, 46), (20, 49), (30, 26), (14, 50)):
            X, Y = round(F(x)), round(F(y))
            for dx, dy, d in ((0, 0, -1.4), (1, 0, -1.0), (0, 1, -0.8), (-1, 1, -0.5), (1, 1, -1.2)):
                fg.rshade(X + dx, Y + dy, d, ST)
        for X, Y in ((F(36), F(34)), (F(37), F(35))):
            fg.rshade(X, Y, -1.0); fg.rshade(X + 1, Y, -0.7)
        fg.rshade(F(36) - 1, F(34) - 1, +0.8)
    else:
        for (x, y) in ((22, 24), (23, 23), (27, 18), (40, 22)):                       # lluentors a la closca
            X, Y = round(F(x)), round(F(y))
            fg.rshade(X, Y, 1.6, BR); fg.rshade(X + 1, Y, 1.0, BR); fg.rshade(X, Y + 1, 0.6, BR)
    return fg.render()


# ─── El capatàs Tul, a la mida nova ─────────────────────────────────────────

ZETA = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (3, 1), (2, 2), (1, 3), (0, 4), (1, 4), (2, 4), (3, 4), (4, 4)]


class _CapatasFig(FigK):
    """La figura del capatàs: deixa de banda els detalls de píxel solt de 480 (els ulls, la boca i els botons)
    i, en acabar, els pinta en píxels reals."""
    talk = False

    def px(self, x, y, mat, lvl):
        if not isinstance(mat, Mat) or (mat is C.CREAM and lvl == 4):
            return
        super().px(x, y, mat, lvl)

    def line(self, x0, y0, x1, y1, mat, lvl):
        if mat == C.MOUTH:
            return
        super().line(x0, y0, x1, y1, mat, lvl)

    def render(self, outline=True):
        F = self.F
        S = C.SKIN_RUDDY
        hx, hy = 36, 19
        ey = hy + 3.6
        my = ey + 5.6
        for y in range(36, 52, 4):                                        # botons de la camisa: 2×2
            X, Y = round(F(33) - 0.5), round(F(y) - 0.5)
            if self.rget(X, Y) and self.rget(X, Y)[0] is C.SHIRT_C:
                self.rpx(X, Y, C.CREAM, 4.4); self.rpx(X + 1, Y, C.CREAM, 3.4)
                self.rpx(X, Y + 1, C.CREAM, 3.0); self.rpx(X + 1, Y + 1, C.CREAM, 2.0)
        # els ulls tancats: una corba d'un píxel de 4 d'ample, cap avall (les puntes un píxel més amunt)
        Y = round(F(ey + 0.4))
        for x0 in (hx - 5, hx + 1):
            X0 = round(F(x0)) - 1
            for dx, dy in ((0, 0), (1, 1), (2, 1), (3, 0)):
                self.rpx(X0 + dx, Y + dy, C.MOUTH, 0)
        # la boca, sota el bigoti
        X, Y = round(F(hx - 1)), round(F(my))
        lip = mix(C.MOUTH, (150, 70, 70), 0.5)
        if self.talk:
            for dx in (-2, -1, 0, 1):
                self.rpx(X + dx, Y, C.MOUTH if -2 < dx < 1 else lip, 0)
            self.rpx(X - 1, Y + 1, C.MOUTH, 0); self.rpx(X, Y + 1, C.MOUTH, 0)
            self.rpx(X - 1, Y + 2, lip, 0); self.rpx(X, Y + 2, lip, 0)
        else:
            self.rpx(X - 2, Y, lip, 0); self.rpx(X - 1, Y, C.MOUTH, 0); self.rpx(X, Y, C.MOUTH, 0)
            self.rpx(X + 1, Y, lip, 0)
        return super().render(outline)


ZETA = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (3, 1), (2, 2), (1, 3), (0, 4), (1, 4), (2, 4), (3, 4), (4, 4)]


def capatas(breath=0, with_seal=True, talk=False, zz=0):
    """El capatàs adormit a ×4/3 (87×109, peus a (44, 106)): el cos amb FigK; els ulls tancats, la boca, els
    botons i les zetes (de 5×5), en píxels reals."""
    install()
    cls = type('_CapatasFigT', (_CapatasFig,), {'talk': talk})
    old = C.Fig
    C.Fig = cls
    try:
        img = C.capatas(breath, with_seal, talk, zz=0)
    finally:
        C.Fig = old
    if zz:
        P = img.load()
        for i in range(zz):
            X0, Y0 = round(f(46 + i * 5)), round(f(12 - i * 5))
            for dx, dy in ZETA:
                for ox, oy, c in ((1, 1, (40, 30, 50, 255)), (0, 0, (240, 240, 250, 255))):
                    x, y = X0 + dx + ox, Y0 + dy + oy
                    if 0 <= x < img.width and 0 <= y < img.height:
                        P[x, y] = c
    return img


# ─── MARE, a la mida nova ───────────────────────────────────────────────────

def mare(glow=False):
    """L'altaveu en forma de cor a ×4/3 (29×29): la reixa de forats i el reflex en píxels reals, el halo a la mida."""
    install()
    H = C.HEART
    fg = FigK(22, 22)
    F = fg.F
    base = 3.0 if glow else 2.4
    fg.ell(7.5, 8, 4.8, 4.8, H, base, amp=1.6)
    fg.ell(14.5, 8, 4.8, 4.8, H, base - 0.2, amp=1.6)
    fg.poly([(3.0, 9.5), (19.0, 9.5), (11.0, 19.0)], H, base - 0.3, amp=1.2,
            normal=lambda x, y: ((x - 11) / 9, 0.2, 0.9), cont=(0, 0.8))
    for (x, y) in ((8, 9), (10, 9), (12, 9), (14, 9), (9, 11), (11, 11), (13, 11), (10, 13), (12, 13), (11, 15)):
        X, Y = round(F(x)), round(F(y))
        fg.rpx(X, Y, H, 1.0 if not glow else 1.6)                     # el forat i la vora de sota, més clara
        fg.rshade(X, Y + 1, +0.5, H)
    X, Y = F(6.5), F(5.5)                                             # el reflex
    for dx, dy, lvl in ((0, 0, 5), (1, -1, 5), (-1, 1, 4.6), (1, 0, 4.4), (2, -1, 4.2)):
        fg.rpx(X + dx, Y + dy, H, lvl)
    img = fg.render()
    if glow:
        n = img.width
        c = F(11)
        halo = Image.new('RGBA', img.size, (0, 0, 0, 0))
        P, Q = img.load(), halo.load()
        for y in range(n):
            for x in range(n):
                d = math.hypot(x - c, (y - c) * 1.1) / (11 * K)
                if d < 1 and not P[x, y][3] and (1 - d) ** 1.5 * 0.9 > B4[y & 3][x & 3]:
                    Q[x, y] = (255, 120, 190, 110)
        halo.alpha_composite(img)
        img = halo
    return img


# ─── Instal·lació ───────────────────────────────────────────────────────────

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


_installed = False
SPECS = ('IRI', 'VET', 'MOS', 'DIRECTORA', 'SIC', 'MIRA', 'GUARDIA')


def install():
    """Posa la figura, la cara, la boca i la placa de 640 a hd.characters, i els ganxos de 640 a les especs
    (només en aquest procés). Ho fan sols person, cargol, capatas i mare; es pot cridar més d'un cop."""
    global _installed
    if _installed:
        return
    _installed = True
    if getattr(C, '_hd640_map', None) is not None:
        # ja ho ha fet una altra còpia d'aquest mòdul (importat amb un altre nom: draw_characters / hd640.draw_characters)
        _MAP.update(C._hd640_map)
        return
    C._hd640_map = _MAP
    C.Fig = FigK
    C.front_face = front_face
    C.side_face = side_face
    C.redo_mouth = redo_mouth
    C.patch = patch
    hooks = _ganxos()
    for name, fn in hooks.items():
        _MAP[getattr(C, name)] = fn
    # les especs de hd.characters es canvien al seu lloc (els ganxos en diccionaris propis, que no es comparteixen)
    for name in SPECS:
        spec = getattr(C, name)
        spec['hooks'] = {k: _MAP.get(v, v) for k, v in spec['hooks'].items()}
        globals()[name] = spec
    for name, fn in hooks.items():
        setattr(C, name, fn)
        globals()[name] = fn
    # (els ganxos de 480 originals, per si una sala els vol cridar a 480)
    globals()['hooks480'] = {fn480.__name__: fn480 for fn480 in _MAP}


def person(spec, facing='D', walk=None, talk=False):
    """Per a les sales que dibuixen gent (hd640/rooms): hd.characters.person a ×4/3 (65×116, peus a (34, 111)).
    Els ganxos de hd/characters.py que hi hagi a `spec` es canvien pels de 640."""
    install()
    return C.person(_port(spec), facing, walk=walk, talk=talk)


# ─── Fulls ───────────────────────────────────────────────────────────────────

def scaled_extra(extra):
    """Punts i velocitats del .character.json: de coordenades de disseny (352×198) a píxels de 480 (com hi eren),
    i d'aquí a 640 amb la mateixa f() que fa servir FigK, perquè quadrin amb el sprite (els peus on toquen a terra)."""
    from escala import pt as pt480
    k480 = 480 / 352
    o = dict(extra)
    o['walkSpeed'] = round(extra['walkSpeed'] * k480 * K)

    def pt(q):
        x, y = pt480(q['x'], q['y'], k480)
        return {'x': round(f(x)), 'y': round(f(y))}
    for key in ('walkToPoint', 'talkPoint', 'feet'):
        o[key] = pt(extra[key])
    o['collider'] = {'points': [pt(q) for q in extra['collider']['points']]}
    return o


def main():
    install()
    import draw_characters as D
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / 'characters'
    D.OUT = out
    D.scaled_extra = scaled_extra
    D.hd_person = C.person
    D.cargol, D.capatas, D.mare = cargol, capatas, mare
    D.main()


if __name__ == '__main__':
    main()
