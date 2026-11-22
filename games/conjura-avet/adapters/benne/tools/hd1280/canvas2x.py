"""
Canvas2x: un Canvas de hd.pix a S× (1280×720), que rep coordenades de sala (640×360).

  - `put`, `flat`, `sprite`, `text` (font petita) i `outline`: un píxel de sala = un bloc S×S;
  - `rect`, `poly`: es recorren a la resolució real (el dither i la llum, per píxel real); `lvl(x, y)` rep la
    coordenada de sala entera (els patrons fets amb `%` continuen igual);
  - `disc`, `line`, `glow`, `tint`, `darken`: a la resolució real, amb coordenades de sala fraccionàries
    (vores rodones, línies primes, degradats llisos);
  - `px(X, Y, ...)`: un sol píxel real, per al detall que no existeix a 640.

Una sala hi passa amb `ART_SCALE = 2` i `from hd1280.canvas2x import Canvas2x as Canvas` (vegeu hd/render.py).
"""
import math

from PIL import Image

import hd640  # noqa: F401
from hd.pix import B4, Canvas, W, H, mix

S = 2


def lc(X):
    """Coordenada de sala del centre del píxel real X."""
    return (X + 0.5) / S - 0.5


def _in(v, a, b):
    """`v` dins de [a, b]: els píxels reals de la vora d'un rectangle de sala tenen el centre fins a 0.25 a fora, i
    les funcions de les sales (fetes per a enters de sala) no n'esperen res de fora (p. ex. una base negativa ** 1.5)."""
    return a if v < a else b if v > b else v


class Canvas2x(Canvas):
    def __init__(self, w=W, h=H, light=None, transparent=False, img=None):
        super().__init__(w * S, h * S, light, transparent, img)
        if img is not None:
            self.w, self.h = img.size

    S = S

    def blit(self, img, pos=(0, 0)):
        """Una imatge en píxels de sala (una figura, una capa de W×H), ampliada ×S, a la posició de sala `pos`."""
        big = img.transform((img.width * S, img.height * S), Image.Transform.EXTENT, (0, 0, img.width, img.height),
                            Image.Resampling.NEAREST)
        self.img.alpha_composite(big, (int(pos[0]) * S, int(pos[1]) * S))

    def pixels(self, x0=0, y0=0, x1=None, y1=None):
        x1 = self.w // S - 1 if x1 is None else x1
        y1 = self.h // S - 1 if y1 is None else y1
        for Y in range(max(0, int(y0 * S)), min(self.h, int((y1 + 1) * S))):
            for X in range(max(0, int(x0 * S)), min(self.w, int((x1 + 1) * S))):
                yield X, Y, lc(X), lc(Y)

    # ── píxel real ──
    def px(self, X, Y, ramp, lvl, lit=1.0):
        if 0 <= X < self.w and 0 <= Y < self.h:
            v = lvl + (lit * self.light(lc(X), lc(Y)) if lit else 0)
            i = math.floor(v + B4[Y & 3][X & 3] - 0.5)
            self.P[X, Y] = ramp[max(0, min(len(ramp) - 1, i))] + (255,)

    def pxflat(self, X, Y, col):
        if 0 <= X < self.w and 0 <= Y < self.h:
            self.P[X, Y] = tuple(col[:3]) + (255,)

    # ── píxel de sala ──
    def put(self, x, y, ramp, lvl, lit=1.0):
        X, Y = int(x) * S, int(y) * S
        for dy in range(S):
            for dx in range(S):
                self.px(X + dx, Y + dy, ramp, lvl, lit)

    def flat(self, x, y, col):
        X, Y = int(x) * S, int(y) * S
        for dy in range(S):
            for dx in range(S):
                self.pxflat(X + dx, Y + dy, col)

    def get(self, x, y):
        return self.P[int(x) * S, int(y) * S]

    def rect(self, x0, y0, x1, y1, ramp, lvl, lit=1.0):
        for Y in range(int(y0) * S, (int(y1) + 1) * S):
            for X in range(int(x0) * S, (int(x1) + 1) * S):
                self.px(X, Y, ramp, lvl(X // S, Y // S) if callable(lvl) else lvl, lit)

    def poly(self, pts, ramp, lvl, lit=1.0):
        P = [(x * S, y * S) for x, y in pts]
        ys = [p[1] for p in P]
        for Y in range(int(min(ys)), int(max(ys)) + 1):
            xs = []
            for (xa, ya), (xb, yb) in zip(P, P[1:] + P[:1]):
                if (ya <= Y + 0.5 < yb) or (yb <= Y + 0.5 < ya):
                    xs.append(xa + (Y + 0.5 - ya) * (xb - xa) / (yb - ya))
            xs.sort()
            for a, b in zip(xs[::2], xs[1::2]):
                for X in range(math.ceil(a - 0.5), math.floor(b - 0.5) + 1):
                    self.px(X, Y, ramp, lvl(X // S, Y // S) if callable(lvl) else lvl, lit)

    def disc(self, cx, cy, rx, ry, ramp, lvl, lit=1.0):
        for Y in range(int((cy - ry - 1) * S), int((cy + ry + 2) * S)):
            for X in range(int((cx - rx - 1) * S), int((cx + rx + 2) * S)):
                nx, ny = (lc(X) - cx) / rx, (lc(Y) - cy) / ry
                if nx * nx + ny * ny <= 1:
                    self.px(X, Y, ramp, lvl(nx, ny) if callable(lvl) else lvl, lit)

    def line(self, x0, y0, x1, y1, ramp, lvl, lit=1.0, thin=False):
        """Línia de S píxels reals de gruix (o d'1 amb `thin`), traçada a la resolució real."""
        X0, Y0, X1, Y1 = (x0 + 0.5) * S - 0.5, (y0 + 0.5) * S - 0.5, (x1 + 0.5) * S - 0.5, (y1 + 0.5) * S - 0.5
        n = max(abs(X1 - X0), abs(Y1 - Y0), 1)
        horiz = abs(X1 - X0) >= abs(Y1 - Y0)
        for i in range(int(n) + 1):
            t = i / n
            # (floor + 0.5, no round(): els punts cauen just a .5 i round() arrodoneix cap al parell; + 1e-6: l'error de
            # coma flotant en tirava alguns avall, i la línia repetia un píxel i en deixava un de buit)
            X, Y = math.floor(X0 + (X1 - X0) * t + 0.5 + 1e-6), math.floor(Y0 + (Y1 - Y0) * t + 0.5 + 1e-6)
            self.px(X, Y, ramp, lvl, lit)
            if not thin:
                self.px(X, Y + 1, ramp, lvl, lit) if horiz else self.px(X + 1, Y, ramp, lvl, lit)

    def _each(self, x0, y0, x1, y1):
        for Y in range(max(0, int(y0 * S)), min(self.h, int((y1 + 1) * S))):
            for X in range(max(0, int(x0 * S)), min(self.w, int((x1 + 1) * S))):
                yield X, Y

    def glow(self, cx, cy, r, col, strength):
        for X, Y in self._each(cx - r, cy - r, cx + r, cy + r):
            d = math.hypot(lc(X) - cx, lc(Y) - cy) / r
            if d < 1:
                a = strength * (1 - d) ** 2
                o = self.P[X, Y]
                if o[3] and a > B4[Y & 3][X & 3] * 0.35:
                    self.P[X, Y] = mix(o, col, min(1, a)) + (o[3],)

    def tint(self, x0, y0, x1, y1, col, k, mask=None):
        for X, Y in self._each(x0, y0, x1, y1):
            o = self.P[X, Y]
            if not o[3]:
                continue
            x, y = _in(lc(X), x0, x1), _in(lc(Y), y0, y1)
            kk = k(x, y) if callable(k) else k
            if mask:
                kk *= mask(x, y)
            if kk > 0:
                self.P[X, Y] = mix(o, col, min(1, kk)) + (o[3],)

    def darken(self, x0, y0, x1, y1, amount, dither=True):
        for X, Y in self._each(x0, y0, x1, y1):
            a = amount(_in(lc(X), x0, x1), _in(lc(Y), y0, y1)) if callable(amount) else amount
            if a <= 0:
                continue
            o = self.P[X, Y]
            if not o[3]:
                continue
            if dither:
                if a > B4[Y & 3][X & 3]:
                    self.P[X, Y] = tuple(int(c * 0.55) for c in o[:3]) + (o[3],)
            else:
                self.P[X, Y] = tuple(int(c * (1 - a * 0.6)) for c in o[:3]) + (o[3],)
