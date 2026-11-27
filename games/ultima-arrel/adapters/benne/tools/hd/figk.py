"""
Una figura redibuixada a una mida més gran (×K), no ampliada: FigK rep les mateixes ordres que Fig (hd/characters.py)
en coordenades de disseny i les rasteritza a la mida real, amb volum i contorn d'un píxel real. Els píxels de disseny
(`px`, `shade`, `erase`) ocupen la seva zona; `line` fa una línia d'un píxel real.

La fa servir l'Espora (hd/arrel.py), que a la mida de disseny feia ≈25 px a la centraleta. És la FigK d'Aigua Verne
(adapters/benne/tools/hd/personatges.py), amb la K com a paràmetre del mòdul.
"""
import math

import hd.characters as C

K = 1.2


def f(u):
    """Coordenada de disseny (centre de píxel) → coordenada real a ×K."""
    return (u + 0.5) * K - 0.5


def g(X):
    """Coordenada real → de disseny."""
    return (X + 0.5) / K - 0.5


def span(i):
    """Els píxels reals que ocupa el píxel de disseny i."""
    return range(math.ceil(i * K - 0.5), math.ceil((i + 1) * K - 0.5))


class FigK(C.Fig):
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


