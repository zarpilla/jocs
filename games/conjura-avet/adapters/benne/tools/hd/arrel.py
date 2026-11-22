"""
Personatges de L'Última Arrel (guio/guio.md, «Protagonistes» i «Secundaris»; guio/pla.md, «Direcció d'art»).

Totes les figures es dibuixen a la seva mida, a 1× (com les sales en 3D), i no s'escalen:

  - **Les persones** (la Iri, la Vet, l'àvia, la Senyora Pla i la Txell) fan servir el sistema de figures de
    hd/characters.py (`person`, 49×87, peus a (25, 83)), però amb **FigY**: la mateixa figura amb unes altres
    proporcions. FigY rep les ordres en coordenades de disseny (les de la persona gran) i les rasteritza amb el tronc
    i les cames més curts (o més llargs), i el cos una mica més estret, amb volum i contorn d'un píxel real. El cap i
    la cara no canvien: la cara de la Iri i la Vet és la de sempre (la de Suma Zero), píxel a píxel. Així la Iri fa
    ≈68 px, la Vet ≈60 (amb les orelles de la gorra), l'àvia ≈80 i les dues senyores ≈84.
  - **Les criatures** (l'Espora, les fades i els gripaus) es dibuixen a mà amb les primitives de Fig, cadascuna al
    seu fotograma: l'Espora ≈35 px, les fades ≈32 (amb les ales, més amples), els gripaus ≈34-36.

Ho fa servir draw_characters.py (els fulls de Benne). Vegeu també guio/art/personatges.py (la làmina de revisió).
"""
import math

from PIL import Image

import hd.characters as C
from hd.characters import (M, Fig, person, SKIN_IRI, SKIN_VET, SKIN_OLD, BOOT, BRASS, LENS, HAIR_WHITE, WHITE,
                           STEELB, EYE_W, LIP, MOUTH, front_face, shoe_front, shoe_side)
from hd.pix import mix

# ═══════════════════════════════════════════════════════════════════════════
#  FigY: la figura de sempre amb unes altres proporcions
# ═══════════════════════════════════════════════════════════════════════════

NECK_Y = 27.0          # a partir d'aquí (les espatlles) comença el tronc
HIP_Y = 51.0           # i aquí, les cames
FEET_Y = 83.0          # els peus no es mouen
CX = 24.5              # l'eix de la figura
PAD = 8                # files de més a dalt del fotograma (les persones altes, amb monyo, no hi cabrien): 49×95


class Prop:
    """Proporcions: `tronc` i `cames` (factors d'alçada del tram), `ample` (factor d'amplada del cos, del coll avall)."""

    def __init__(self, tronc=1.0, cames=1.0, ample=1.0):
        self.a, self.b, self.sx = tronc, cames, ample
        self.yh = FEET_Y - (FEET_Y - HIP_Y) * self.b          # on va el maluc
        self.yn = self.yh - (HIP_Y - NECK_Y) * self.a          # on va el coll
        self.shift = self.yn - NECK_Y                          # quant baixa el cap

    def y(self, y):
        """Fila de disseny → fila real (amb les PAD files de dalt)."""
        if y >= HIP_Y:
            return FEET_Y - (FEET_Y - y) * self.b + PAD
        if y >= NECK_Y:
            return self.yh - (HIP_Y - y) * self.a + PAD
        return y + self.shift + PAD

    def inv(self, Y):
        """Fila real → fila de disseny."""
        Y -= PAD
        if Y >= self.yh:
            return FEET_Y - (FEET_Y - Y) / self.b
        if Y >= self.yn:
            return HIP_Y - (self.yh - Y) / self.a
        return Y - self.shift

    def ky(self, y):
        """Factor vertical local."""
        return self.b if y >= HIP_Y else self.a if y >= NECK_Y else 1.0

    def kx(self, y):
        """Factor horitzontal local: el cap no canvia; del coll avall, `ample` (amb una transició curta)."""
        t = max(0.0, min(1.0, (y - (NECK_Y - 4)) / 4))
        return 1.0 + (self.sx - 1.0) * t

    def x(self, x, y):
        return CX + (x - CX) * self.kx(y)

    def ix(self, X, y):
        return CX + (X - CX) / self.kx(y)


ADULT = Prop()


class FigY(Fig):
    """Fig amb proporcions (`Prop`): les primitives amb volum es tornen a rasteritzar a la mida real; els píxels solts
    van a la seva fila real. El buffer és de 49×95: la mida de sempre i PAD files més a dalt."""

    prop = ADULT

    def __init__(self, w, h):
        super().__init__(w, h + PAD)

    def _m(self, x, y):
        P_ = self.prop
        y += self.oy
        x += self.ox
        return P_.x(x, y), P_.y(y)

    def _d(self, X, Y):
        """Real → disseny (sense ox/oy)."""
        P_ = self.prop
        y = P_.inv(Y)
        return P_.ix(X, y) - self.ox, y - self.oy

    def ell(self, cx, cy, rx, ry, mat, base, amp=1.6, cont=None, lvlfn=None, clip=None):
        P_ = self.prop
        yy = cy + self.oy
        CX_, CY_ = self._m(cx, cy)
        RX, RY = rx * P_.kx(yy), ry * P_.ky(yy)
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
        k = P_.kx((a[1] + b[1]) / 2 + self.oy)
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
        Y0 = math.floor(P_.y(y0 - 0.5 + self.oy))
        Y1 = math.ceil(P_.y(y1 + 0.5 + self.oy))
        for Y in range(Y0, Y1 + 1):
            yd = P_.inv(Y + 0.0) - self.oy
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
            xl = CX + (e[0] + self.ox - CX) * k
            xr = CX + (e[1] + self.ox - CX) * k
            mid, half = (xl + xr) / 2, max(0.5, (xr - xl) / 2)
            for x in range(math.ceil(xl - 0.01), math.floor(xr + 0.01) + 1):
                u = max(-1.0, min(1.0, (x - mid) / (half + 0.5)))
                nz = math.sqrt(max(0.0, 1 - u * u - tilt * tilt))
                pix[(x, Y)] = (u, tilt, nz)
        self._paint(pix, mat, base, amp, cont, lvlfn)
        return pix

    def poly(self, pts, mat, base, amp=0.0, cont=None, lvlfn=None, normal=None):
        pts = [self._m(px, py) for px, py in pts]
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
                    pix[(x, y)] = normal(*self._d(x, y)) if normal else (0.0, 0.0, 1.0)
        self._paint(pix, mat, base, amp, cont, lvlfn)
        return pix

    def _paint(self, pix, mat, base, amp, cont, lvlfn):
        if lvlfn:
            fn = lvlfn
            lvlfn = lambda x, y: fn(*self._d(x, y))  # noqa: E731
        super()._paint(pix, mat, base, amp, cont, lvlfn)

    def _at(self, x, y):
        X, Y = self._m(x, y)
        return int(round(X)), int(round(Y))

    def px(self, x, y, mat, lvl):
        X, Y = self._at(x, y)
        if 0 <= X < self.w and 0 <= Y < self.h:
            self.buf[Y][X] = (mat, lvl)

    def line(self, x0, y0, x1, y1, mat, lvl):
        X0, Y0 = self._m(x0, y0)
        X1, Y1 = self._m(x1, y1)
        n = max(1, int(math.ceil(max(abs(X1 - X0), abs(Y1 - Y0)))))
        for i in range(n + 1):
            t = i / n
            X, Y = int(round(X0 + (X1 - X0) * t)), int(round(Y0 + (Y1 - Y0) * t))
            if 0 <= X < self.w and 0 <= Y < self.h:
                self.buf[Y][X] = (mat, lvl)

    def shade(self, x, y, d, only=None):
        X, Y = self._at(x, y)
        if 0 <= X < self.w and 0 <= Y < self.h and self.buf[Y][X]:
            m, l = self.buf[Y][X]
            if only is None or m is only or (isinstance(only, (list, tuple)) and m in only):
                self.buf[Y][X] = (m, l + d)

    def get(self, x, y):
        X, Y = self._at(x, y)
        if 0 <= X < self.w and 0 <= Y < self.h:
            return self.buf[Y][X]
        return None

    def erase(self, x, y):
        X, Y = self._at(x, y)
        if 0 <= X < self.w and 0 <= Y < self.h:
            self.buf[Y][X] = None

    # píxels reals (per als detalls que han de ser d'un sol píxel)
    def rpx(self, X, Y, mat, lvl):
        X, Y = int(round(X)), int(round(Y))
        if 0 <= X < self.w and 0 <= Y < self.h:
            self.buf[Y][X] = (mat, lvl)


def _gira_y(fg, p, spec, S):
    """El 3/4 (DL, UL) de hd/characters.py (`_gira`), però amb les files de FigY: la figura de cara (o d'esquena),
    estreta i desplaçada cap on mira, el costat dret a l'ombra, la cara desplaçada dins el cap i el nas a la silueta."""
    P_ = fg.prop
    cx = CX
    old = [row[:] for row in fg.buf]
    b = p.bob
    for Y in range(fg.h):
        yd = P_.inv(Y) - b
        _, dx = C._q_dx(yd, p.q)
        row = old[Y]
        for X in range(fg.w):
            v = X - cx - dx
            xs = cx + v / C._q_dx(yd, p.q, v)[0]
            i = int(round(xs))
            fg.buf[Y][X] = row[i] if 0 <= i < fg.w else None
    for Y in range(fg.h):
        yd = P_.inv(Y) - b
        if yd < 27:
            continue
        row = fg.buf[Y]
        xr = next((X for X in range(fg.w - 1, -1, -1) if row[X]), None)
        if xr is None:
            continue
        for X in range(xr, max(-1, xr - 2), -1):
            if row[X]:
                m, l = row[X]
                row[X] = (m, l - 0.7)
    if p.q != 'DL':
        return
    for Y in range(fg.h):                               # el costat de darrere, més fosc (C._q_fosc_darrere)
        if P_.inv(Y) - b >= 28:
            C._q_fosc_darrere(fg.buf[Y], 2)
    hx, hy = p.head
    k, dx = C._q_dx(hy, p.q)
    p.head = (CX + (hx - CX) * k + dx + C.Q_DX_CARA, hy)
    front_face(fg, p, spec)
    for yd in (hy + 2.0, hy + 3.0):
        Y = int(round(P_.y(yd + b)))
        if not 0 <= Y < fg.h:
            continue
        row = fg.buf[Y]
        xl = next((X for X in range(fg.w) if row[X] and row[X][0] is S), None)
        if xl is not None and xl - 1 >= 0:
            row[xl - 1] = (S, row[xl][1] + 0.4)
    p.head = (hx, hy)
    if 'face_q' in spec.get('hooks', {}):               # el que va damunt la cara (ulleres, somriure), en 3/4
        spec['hooks']['face_q'](fg, p, spec)


def figura(spec, facing, walk=None, talk=False):
    """Una persona amb les proporcions de `spec['prop']`: imatge RGBA de 49×95 (peus a (25, 91))."""
    prop = spec.get('prop', ADULT)
    cls = type('FigP', (FigY,), {'prop': prop})
    saved = C.Fig, C._gira
    C.Fig = cls
    C._gira = _gira_y
    try:
        return person(spec, facing, walk=walk, talk=talk)
    finally:
        C.Fig, C._gira = saved


def respira(img, spec, k):
    """L'`Idle` de quatre fotogrames: la clariana del pit puja i baixa (+5 %, +10 %, +5 %) sense moure cap píxel
    de la silueta (draw_characters.py, «La respiració»). Les files del pit, a la mida de cada figura."""
    if not k:
        return img
    prop = spec.get('prop', ADULT)
    y0, y1 = round(prop.y(30)), round(prop.y(41))
    x0, x1 = round(prop.x(13, 35)), round(prop.x(36, 35))
    out = img.copy()
    P_ = out.load()
    for y in range(y0, y1):
        f = 1 + k * (1 - (y - y0) / max(1, y1 - y0))
        for x in range(x0, x1):
            r, g, b, a = P_[x, y]
            if a:
                P_[x, y] = (min(255, int(r * f)), min(255, int(g * f)), min(255, int(b * f)), a)
    return out


def hooks(*fns):
    """Diversos ganxos en un."""
    def run(fg, p, *a):
        for fn in fns:
            if fn:
                fn(fg, p, *a)
    return run


# ═══════════════════════════════════════════════════════════════════════════
#  Materials
# ═══════════════════════════════════════════════════════════════════════════

OCHRE = M((40, 22, 10), (78, 46, 16), (122, 76, 24), (166, 110, 36), (204, 146, 52), (232, 184, 90), dith=0.0)
MOSS = M((12, 20, 12), (24, 38, 22), (38, 58, 32), (56, 80, 44), (78, 104, 58), (104, 130, 78), dith=0.0)
BAG = M((8, 18, 38), (16, 34, 70), (28, 56, 108), (44, 84, 146), (70, 118, 180), (120, 164, 214))
HAIR_DARK = M((10, 6, 8), (24, 14, 14), (40, 24, 22), (60, 38, 30), (84, 56, 42), (114, 80, 60))
BLACKM = M((6, 6, 8), (14, 14, 16), (26, 26, 28), (42, 42, 44), (64, 64, 66))
PATCHG = M((10, 34, 20), (20, 70, 40), (46, 120, 66), (110, 180, 120))
TURQ = M((4, 30, 34), (8, 70, 74), (20, 130, 130), (50, 196, 184), (130, 240, 222), (220, 255, 246))

RAIN = M((40, 6, 10), (80, 14, 18), (130, 26, 26), (180, 44, 36), (218, 76, 56), (244, 124, 96), dith=0.0)
TIGHTS = M((10, 10, 20), (20, 20, 36), (32, 32, 54), (48, 48, 74), (68, 68, 96))
WELLY = M((70, 46, 6), (140, 100, 14), (204, 156, 30), (236, 198, 60), (252, 230, 130))
CAP = M((22, 12, 8), (44, 26, 16), (70, 44, 26), (98, 66, 40), (130, 92, 58), (162, 124, 84))
HAIR_VET = M((6, 4, 6), (14, 10, 12), (26, 18, 20), (40, 30, 30), (60, 46, 44), (84, 66, 60))
TOGGLE = M((60, 44, 30), (120, 96, 66), (190, 164, 120), (236, 220, 180))

# l'àvia
KNIT = M((18, 30, 22), (34, 54, 38), (52, 80, 54), (74, 106, 70), (100, 134, 88), (132, 162, 112), dith=0.0)  # rebeca
PLUM = M((22, 8, 18), (44, 16, 34), (70, 28, 52), (100, 44, 72), (130, 64, 92), (162, 92, 116), dith=0.0)    # faldilla
WICKER = M((40, 24, 10), (80, 52, 22), (124, 86, 40), (166, 122, 62), (204, 160, 90), (232, 196, 128))
SHROOM = M((50, 18, 10), (100, 40, 20), (150, 70, 34), (196, 106, 54), (226, 146, 86))
SHOE_OLD = M((10, 8, 10), (24, 18, 20), (40, 30, 30), (60, 46, 42), (84, 66, 58))

# la Senyora Pla (NaturaPlus: blanc de plàstic, gris acer, verd fluor)
SUIT_W = M((70, 76, 96), (122, 128, 146), (168, 174, 188), (206, 210, 220), (230, 233, 238), (246, 248, 250),
           (255, 255, 255), dith=0.0)
NEON = M((10, 50, 10), (30, 110, 20), (70, 190, 40), (140, 250, 80), (220, 255, 170))
HAIR_BLOND = M((60, 44, 20), (110, 84, 40), (160, 128, 70), (204, 172, 108), (232, 208, 150), (250, 236, 196))
SKIN_PLA = M((70, 36, 48), (124, 74, 72), (178, 122, 104), (216, 166, 138), (238, 200, 172), (252, 228, 204))
TABLET = M((10, 12, 16), (24, 26, 32), (44, 48, 56), (70, 76, 86), (110, 118, 128))
SHOE_W = M((80, 84, 96), (140, 144, 154), (190, 194, 200), (226, 228, 232), (248, 248, 250))

# la Txell (TV Comarca)
CORAL = M((50, 12, 14), (100, 28, 26), (156, 50, 38), (206, 82, 56), (236, 120, 82), (252, 168, 128), dith=0.0)
JEANS = M((14, 22, 38), (26, 42, 64), (42, 66, 94), (62, 96, 126), (90, 130, 158))
SKIN_TXELL = M((50, 24, 28), (92, 50, 44), (138, 86, 62), (178, 124, 86), (208, 160, 114), (232, 196, 152))
HAIR_CURL = M((8, 4, 6), (20, 10, 10), (36, 20, 16), (56, 32, 24), (80, 50, 36), (108, 72, 52))
MICB = M((8, 24, 70), (16, 46, 130), (30, 80, 190), (70, 130, 236), (150, 196, 255))

# ═══════════════════════════════════════════════════════════════════════════
#  La Iri (11 anys)
# ═══════════════════════════════════════════════════════════════════════════

IRI_PROP = Prop(tronc=0.82, cames=0.80, ample=0.92)


def _strands(x, y):
    return 0.4 * math.sin(x * 1.6 + y * 0.3)


def iri_back(fg, p, spec):
    """La motxilla (de perfil, sobresurt per darrere) i la cua (de cara, es veu per sota de les orelles)."""
    b = p.bob
    if p.f == 'L':
        fg.ell(31.4, 39.0 + b, 5.4, 9.0, BAG, 2.4, amp=1.6, cont=(0.2, 0.8))
        fg.ell(32.0, 33.0 + b, 4.2, 2.4, BAG, 3.0, amp=1.2)
        fg.ell(33.6, 42.0 + b, 2.6, 4.0, BAG, 1.8, amp=1.0)                      # la butxaca del costat
    elif p.f == 'D':
        for sx in (-1, 1):
            fg.ell(24.5 + sx * 9.8, 40.0 + b, 2.4, 7.0, BAG, 1.8, amp=1.2)            # la motxilla, pels costats
        hx, hy = p.head
        fg.ell(hx, hy + 5.0, 7.6, 5.0, HAIR_DARK, 1.8, amp=1.0, lvlfn=_strands)


def iri_hair(fg, p, spec):
    """Castany fosc, ratlla al mig, recollit en una cua baixa."""
    hx, hy = p.head
    H = HAIR_DARK
    if p.f == 'D':
        fg.ell(hx, hy - 1.6, 7.4, 7.2, H, 2.6, amp=1.6, cont=(0.2, 0.8), lvlfn=_strands,
               clip=lambda x, y: y <= hy - 3.0 + ((x - hx) / 7.0) ** 2 * 3.6 or abs(x - hx) > 5.6)
        for y in range(int(hy - 8), int(hy - 3)):                                   # la ratlla al mig
            fg.shade(hx, y, -1.0, H)
        for sx in (-1, 1):                                                          # els cabells que cauen pels costats
            fg.ell(hx + sx * 6.4, hy + 2.4, 1.8, 5.0, H, 2.0 if sx < 0 else 1.6, amp=0.8, lvlfn=_strands)
    elif p.f == 'L':
        fg.ell(hx + 0.8, hy - 1.6, 7.4, 7.0, H, 2.6, amp=1.6, cont=(0.2, 0.8), lvlfn=_strands,
               clip=lambda x, y: (x >= hx - 1.5 or y <= hy - 4.4) and not (x < hx + 2.4 and y > hy - 1.0))
        sw = 0.0 if p.walk is None else 0.8 * math.sin(2 * math.pi * p.walk / 6)    # la cua es gronxa en caminar
        fg.ell(hx + 7.0 + sw, hy + 4.0, 2.2, 6.4, H, 2.2, amp=1.0, lvlfn=_strands)  # la cua
        fg.ell(hx + 6.4, hy + 0.2, 1.4, 1.2, OCHRE, 3.4, amp=0.6)                   # la goma
    else:
        fg.ell(hx, hy - 0.8, 7.4, 7.8, H, 2.6, amp=1.6, cont=(0.2, 0.8), lvlfn=_strands)
        sw = 0.0 if p.walk is None else 0.7 * math.sin(2 * math.pi * p.walk / 6)
        fg.ell(hx + sw, hy + 8.0, 2.4, 6.0, H, 2.4, amp=1.0, lvlfn=_strands)
        fg.ell(hx, hy + 3.4, 1.6, 1.0, OCHRE, 3.4, amp=0.6)


def iri_over(fg, p, spec):
    """La jaqueta oberta (la samarreta crema a dins), les corretges de la motxilla, el walkie, la lupa i el pegat."""
    b = p.bob
    if p.f == 'D':
        for y in range(30 + b, 50 + b):                                             # la jaqueta, oberta
            fg.shade(24.5, y, -1.1, OCHRE)
        for y in range(30 + b, 34 + b):                                             # la samarreta, al coll
            fg.px(24, y, TOGGLE, 3.0)
            if y < 33 + b:
                fg.px(25, y, TOGGLE, 2.6)
        for sx in (-1, 1):                                                          # corretges
            for y in range(30 + b, 44 + b):
                fg.px(24.5 + sx * 6.0, y, BAG, 2.2)
        for y in range(34 + b, 39 + b):                                             # el walkie, a la corretja
            for x in (17, 18):
                fg.px(x, y, BLACKM, 2.0 + (1.0 if y == 34 + b else 0))
        fg.px(17, 32 + b, BLACKM, 2.6)                                              # l'antena
        fg.px(17, 33 + b, BLACKM, 2.6)
        fg.px(18, 35 + b, TURQ, 3.4)                                                # el pilot
        fg.line(22, 30 + b, 24, 37 + b, BLACKM, 1.4)                                # el cordó de la lupa
        fg.line(27, 30 + b, 25, 37 + b, BLACKM, 1.4)
        fg.ell(24.5, 39.0 + b, 2.2, 2.2, BRASS, 3.0, amp=0.8)
        fg.ell(24.5, 39.0 + b, 1.2, 1.2, LENS, 3.0, amp=0.6)
        for y in range(42 + b, 45 + b):                                             # el pegat verd
            for x in (29, 30, 31):
                fg.px(x, y, PATCHG, 2.6)
    elif p.f == 'L':
        fg.line(25, 30 + b, 25, 44 + b, BAG, 2.0)                                   # la corretja
        fg.ell(20.6, 38.0 + b, 1.6, 1.6, BRASS, 3.0, amp=0.6)                       # la lupa, penjada
        fg.px(20.2, 37.6 + b, LENS, 4.0)
        for y in range(33 + b, 37 + b):                                             # el walkie
            fg.px(24, y, BLACKM, 2.2)
            fg.px(25, y, BLACKM, 1.8)
        fg.px(24, 32 + b, BLACKM, 2.6)
    else:
        fg.ell(24.5, 39.0 + b, 7.4, 9.0, BAG, 2.6, amp=1.6, cont=(0.2, 0.8))        # la motxilla
        fg.ell(24.5, 43.0 + b, 5.0, 3.6, BAG, 2.0, amp=1.0)                         # la butxaca
        fg.ell(24.5, 31.2 + b, 4.6, 1.6, BAG, 3.2, amp=0.8)
        fg.px(24, 41 + b, TURQ, 3.6)                                                # el reflectant de la butxaca
        fg.px(25, 41 + b, TURQ, 3.2)


def iri_collar(fg, p, spec):
    """El coll de la jaqueta, girat."""
    b = p.bob
    if p.f == 'L':
        fg.ell(27.0, 28.6 + b, 3.0, 1.8, OCHRE, 3.2, amp=1.0, cont=(0.2, 0.8))
    elif p.f == 'D':
        for sx in (-1, 1):
            fg.ell(24.5 + sx * 3.6, 28.4 + b, 2.6, 1.6, OCHRE, 3.4 if sx < 0 else 2.8, amp=1.0, cont=(0.2, 0.8))
    else:
        fg.ell(24.5, 28.4 + b, 5.6, 1.8, OCHRE, 3.0, amp=1.0, cont=(0.2, 0.8))


IRI = {
    'skin': SKIN_IRI, 'legs': MOSS, 'top': OCHRE, 'shoes': BOOT, 'lashes': True, 'thin': 0.4,
    'iris': (52, 38, 30), 'brow': (24, 16, 22),   # la cara de la Iri, la de sempre
    'prop': IRI_PROP,
    'hooks': {'hair_back': iri_back, 'hair': iri_hair, 'over': iri_over, 'collar': iri_collar},
}


# ═══════════════════════════════════════════════════════════════════════════
#  La Vet (9 anys)
# ═══════════════════════════════════════════════════════════════════════════

VET_PROP = Prop(tronc=0.72, cames=0.58, ample=0.88)


def vet_hair(fg, p, spec):
    """La gorra amb orelles d'os i dues trenes curtes que en surten per sota."""
    hx, hy = p.head
    if p.f == 'D':
        for sx in (-1, 1):                                                          # trenes
            for k in range(4):
                fg.ell(hx + sx * 7.2, hy + 1.0 + k * 2.2, 1.6, 1.3, HAIR_VET, 2.6 - k * 0.2, amp=0.8)
            fg.px(hx + sx * 7.2, hy + 9.6, RAIN, 3.4)                               # les gomes, vermelles
        fg.ell(hx, hy - 3.0, 7.8, 5.6, CAP, 2.8, amp=1.6, cont=(0.2, 0.8),
               clip=lambda x, y: y <= hy - 3.2 + ((x - hx) / 7.6) ** 2 * 2.6)
        for x in range(int(hx - 7), int(hx + 8)):                                   # la vora de la gorra
            fg.px(x, hy - 3 + ((x - hx) / 7.6) ** 2 * 2.6, CAP, 1.6)
        for sx in (-1, 1):                                                          # orelles
            fg.ell(hx + sx * 5.6, hy - 8.4, 2.4, 2.2, CAP, 2.8, amp=1.0, cont=(0.2, 0.8))
            fg.ell(hx + sx * 5.6, hy - 8.2, 1.0, 1.0, CAP, 1.4, amp=0.4)
    elif p.f == 'L':
        sw = 0.0 if p.walk is None else 0.7 * math.sin(2 * math.pi * p.walk / 6)
        for k in range(4):
            fg.ell(hx + 5.4 + sw * k / 3, hy + 1.4 + k * 2.2, 1.6, 1.3, HAIR_VET, 2.4 - k * 0.2, amp=0.8)
        fg.px(hx + 5.4 + sw, hy + 9.8, RAIN, 3.2)
        fg.ell(hx + 0.6, hy - 3.0, 7.8, 5.6, CAP, 2.8, amp=1.6, cont=(0.2, 0.8),
               clip=lambda x, y: y <= hy - 2.6)
        fg.ell(hx - 5.6, hy - 2.8, 3.0, 1.0, CAP, 2.2, amp=0.6)                     # la visera
        fg.ell(hx + 2.0, hy - 9.0, 2.4, 2.2, CAP, 2.8, amp=1.0, cont=(0.2, 0.8))
        fg.ell(hx + 2.0, hy - 8.8, 1.0, 1.0, CAP, 1.4, amp=0.4)
    else:
        for sx in (-1, 1):
            for k in range(4):
                fg.ell(hx + sx * 5.0, hy + 3.0 + k * 2.2, 1.6, 1.3, HAIR_VET, 2.4 - k * 0.2, amp=0.8)
            fg.px(hx + sx * 5.0, hy + 11.4, RAIN, 3.2)
        fg.ell(hx, hy - 1.6, 7.8, 6.6, CAP, 2.6, amp=1.6, cont=(0.2, 0.8))
        for sx in (-1, 1):
            fg.ell(hx + sx * 5.6, hy - 8.4, 2.4, 2.2, CAP, 2.6, amp=1.0, cont=(0.2, 0.8))


def vet_collar(fg, p, spec):
    """La caputxa de l'impermeable, plegada darrere el coll."""
    b = p.bob
    if p.f == 'L':
        fg.ell(29.0, 29.0 + b, 3.6, 2.6, RAIN, 2.2, amp=1.0, cont=(0.2, 0.8))
    else:
        fg.ell(24.5, 28.6 + b, 6.4, 2.2, RAIN, 2.0 if p.f == 'D' else 2.8, amp=1.0, cont=(0.2, 0.8))


def vet_over(fg, p, spec):
    """L'impermeable: botons de fusta, i més llarg (tapa el maluc)."""
    b = p.bob
    if p.f == 'D':
        for y in range(31 + b, 54 + b):
            fg.shade(24.5, y, -0.8, RAIN)
        for y in (35, 41, 47):
            fg.px(23, y + b, TOGGLE, 2.6)
            fg.px(26, y + b, TOGGLE, 2.6)
        for x in range(17, 33):                                                     # la vora de baix
            fg.px(x, 54 + b, RAIN, 1.4)
            fg.px(x, 53 + b, RAIN, 2.4)
    elif p.f == 'L':
        for x in range(19, 31):
            fg.px(x, 53 + b, RAIN, 2.2)
            fg.px(x, 54 + b, RAIN, 1.2)
        for y in (35, 41, 47):
            fg.px(19, y + b, TOGGLE, 2.6)
    else:
        for x in range(17, 33):
            fg.px(x, 53 + b, RAIN, 2.2)
            fg.px(x, 54 + b, RAIN, 1.2)


def vet_arm(fg, p, spec, i):
    """El walkie a la mà dreta (la de la pantalla, l'esquerra de la Vet)."""
    if i != 1 or p.f == 'U':
        return
    w = p.arms[0][2] if p.f == 'L' else p.wrist[1]
    for y in range(int(w[1]) + 1, int(w[1]) + 6):
        fg.px(w[0], y, BLACKM, 2.2)
        fg.px(w[0] + 1, y, BLACKM, 1.6)
    fg.px(w[0], w[1] - 1, BLACKM, 2.6)
    fg.px(w[0], w[1] - 2, BLACKM, 2.6)
    fg.px(w[0] + 1, w[1] + 2, TURQ, 3.4)


def _vet_arm_side(fg, p, spec, i):
    """De perfil, el walkie a la mà del davant."""
    if p.f != 'L':
        return
    w = p.arms[0][2]
    for y in range(int(w[1]) + 2, int(w[1]) + 7):
        fg.px(w[0] - 1, y, BLACKM, 2.2)
        fg.px(w[0], y, BLACKM, 1.6)
    fg.px(w[0] - 1, w[1] + 1, BLACKM, 2.6)
    fg.px(w[0] - 1, w[1], BLACKM, 2.6)


def vet_boot(fg, p, spec, i):
    """Les botes d'aigua: la canya, groga, fins a mitja cama."""
    k, a = p.knee[i], p.ankle[i]
    for t in (0.45, 0.6, 0.75, 0.9, 1.0):
        x, y = k[0] + (a[0] - k[0]) * t, k[1] + (a[1] - k[1]) * t
        fg.ell(x, y, 3.0, 1.2, WELLY, 2.8 - (0.3 if i else 0), amp=1.0)


def vet_boot_side(fg, p, spec, leg, dl):
    h, k, a, pitch = leg
    for t in (0.45, 0.6, 0.75, 0.9, 1.0):
        x, y = k[0] + (a[0] - k[0]) * t, k[1] + (a[1] - k[1]) * t
        fg.ell(x, y, 2.8, 1.2, WELLY, 2.8 + dl, amp=1.0)


def _vet_arm(fg, p, spec, i):
    if p.f == 'L':
        _vet_arm_side(fg, p, spec, i)
    else:
        vet_arm(fg, p, spec, i)


VET = {
    'skin': SKIN_VET, 'legs': TIGHTS, 'top': RAIN, 'shoes': WELLY, 'lashes': True, 'thin': 0.6,
    'iris': (60, 36, 26), 'brow': (26, 14, 14), 'lip': (150, 40, 52),   # la cara de la Vet, la de sempre
    'prop': VET_PROP,
    'hooks': {'hair': vet_hair, 'collar': vet_collar, 'over': vet_over, 'arm': _vet_arm,
              'leg_deco': vet_boot, 'leg_deco_side': vet_boot_side},
}


# ═══════════════════════════════════════════════════════════════════════════
#  Ajudes per a les persones grans
# ═══════════════════════════════════════════════════════════════════════════

def skirt(mat, bot, flare, lvl=2.6, top=45, lvlfn=None):
    """Una faldilla (o un abric llarg) que segueix les cames (ganxo `torso`), de la cintura a `bot`."""
    def hook(fg, p, spec):
        b = p.bob
        t0 = top + b
        if p.f == 'L':
            xs = [leg[1][0] for leg in p.legs]
            front = min(min(xs) - 4.0, 20.6)
            back = max(max(xs) + 4.0, 30.6)

            def e(y):
                t = max(0.0, min(1.0, (y - t0) / max(1, bot - t0)))
                return (20.6 + (front - 20.6 - flare * 0.4) * t, 30.6 + (back - 30.6 + flare * 0.6) * t)
        else:
            lift = getattr(p, 'lift', [0, 0])

            def e(y):
                t = max(0.0, min(1.0, (y - t0) / max(1, bot - t0)))
                w = 8.4 - p.thin + flare * t
                sway = (lift[1] - lift[0]) * 0.3 * t
                return (24.5 - w + sway, 24.5 + w + sway)
        fg.lathe(t0, bot, e, mat, lvl, amp=1.6, lvlfn=lvlfn, cont=(0.0, 0.6))
        l, r = e(bot)
        for x in range(math.ceil(l), math.floor(r) + 1):                            # la vora, una mica més fosca
            fg.shade(x, bot, -0.7, mat)
        if p.f == 'L':
            for y in range(int(t0) + 4, int(bot) + 1):                              # un plec
                fg.shade(l + (r - l) * 0.55, y, -0.8, mat)
        else:
            for fx in (0.33, 0.66):
                for y in range(int(t0) + 6, int(bot) + 1):
                    fg.shade(l + (r - l) * fx, y, -0.6, mat)
    return hook


def eyes_at(p):
    """On són els ulls (de cara: x esquerre de cada ull; de perfil: x de l'ull) i la fila."""
    hx, hy = p.head
    ey = int(hy + 0.5)
    if p.f == 'L':
        return [int(hx - 3.5)], ey
    return [int(hx - 3.5), int(hx + 2.5)], ey


def glasses(fg, p, spec, frame=STEELB, lvl=2.0):
    """Unes ulleres petites: la muntura d'un píxel al voltant de cada ull (de 2 px) i el pont."""
    if p.f == 'U':
        return
    xs, ey = eyes_at(p)
    if p.f == 'L':
        x0 = xs[0] - 1
        for x in range(x0, x0 + 3):
            fg.px(x, ey - 2 + 0 * x, frame, lvl + 0.6)
            fg.px(x, ey + 1, frame, lvl)
        fg.px(x0 - 1, ey - 1, frame, lvl); fg.px(x0 - 1, ey, frame, lvl)
        fg.line(x0 + 3, ey - 1, p.head[0] + 2.5, ey, frame, lvl - 0.3)              # la patilla
        return
    for x0 in xs:
        for x in range(x0 - 1, x0 + 3):
            fg.px(x, ey + 1, frame, lvl)
        for x in range(x0, x0 + 2):
            fg.px(x, ey - 2, frame, lvl + 0.6)
        fg.px(x0 - 1, ey - 1, frame, lvl); fg.px(x0 - 1, ey, frame, lvl)
        fg.px(x0 + 2, ey - 1, frame, lvl - 0.3); fg.px(x0 + 2, ey, frame, lvl - 0.3)
    for x in range(xs[0] + 3, xs[1] - 1):
        fg.px(x, ey - 1, frame, lvl)


def glasses_q(fg, p, spec):
    """Les ulleres en 3/4 (DL): la cara ja és desplaçada (p.head)."""
    hx, hy = p.head
    k, dx = C._q_dx(hy, p.q)
    saved = p.head
    p.head = (CX + (hx - CX) * k + dx + C.Q_DX_CARA, hy)
    p.f = 'D'
    glasses(fg, p, spec)
    p.head = saved


# ═══════════════════════════════════════════════════════════════════════════
#  L'àvia Montse (78 anys)
# ═══════════════════════════════════════════════════════════════════════════

AVIA_PROP = Prop(tronc=0.96, cames=0.94, ample=0.98)


def avia_hair(fg, p, spec):
    """Cabell blanc, recollit en un monyo a dalt, i les ulleres."""
    hx, hy = p.head
    H = HAIR_WHITE
    wave = lambda x, y: 0.35 * math.sin(x * 1.2 - y * 0.8)  # noqa: E731
    if p.f == 'D':
        fg.ell(hx, hy - 1.4, 7.2, 7.0, H, 2.6, amp=1.6, cont=(0.2, 0.8), lvlfn=wave,
               clip=lambda x, y: y <= hy - 2.6 + ((x - hx) / 7.0) ** 2 * 4.0)
        fg.ell(hx + 0.4, hy - 8.6, 3.6, 2.8, H, 2.8, amp=1.4, cont=(0.2, 0.8), lvlfn=wave)   # el monyo
        for sx in (-1, 1):
            fg.ell(hx + sx * 6.4, hy + 0.6, 1.4, 3.0, H, 2.2 if sx < 0 else 1.8, amp=0.8)
        glasses(fg, p, spec)
    elif p.f == 'L':
        fg.ell(hx + 0.8, hy - 1.4, 7.2, 7.0, H, 2.6, amp=1.6, cont=(0.2, 0.8), lvlfn=wave,
               clip=lambda x, y: (x >= hx - 1.0 or y <= hy - 4.6) and not (x < hx + 2.6 and y > hy - 1.0))
        fg.ell(hx + 4.6, hy - 6.6, 3.4, 3.0, H, 2.6, amp=1.4, cont=(0.2, 0.8), lvlfn=wave)
        fg.px(hx + 6.6, hy - 8.0, BRASS, 3.4)                                       # la forquilla del monyo
        fg.px(hx + 7.4, hy - 8.6, BRASS, 3.0)
        glasses(fg, p, spec)
    else:
        fg.ell(hx, hy - 0.8, 7.2, 7.6, H, 2.6, amp=1.6, cont=(0.2, 0.8), lvlfn=wave)
        fg.ell(hx, hy - 6.8, 3.8, 3.2, H, 2.6, amp=1.4, cont=(0.2, 0.8), lvlfn=wave)
        fg.px(hx - 1, hy - 7.6, BRASS, 3.4)
        fg.px(hx + 1, hy - 8.0, BRASS, 3.2)


def avia_over(fg, p, spec):
    """La rebeca de punt: oberta, amb botons i butxaques; el coll de la brusa."""
    b = p.bob
    if p.f == 'D':
        for y in range(30 + b, 50 + b):
            fg.shade(24.5, y, -1.0, KNIT)
            if (y - b) % 4 == 0:
                fg.px(23, y, TOGGLE, 3.0)
        for sx in (-1, 1):                                                          # les butxaques
            for x in range(int(24.5 + sx * 3.5), int(24.5 + sx * 7.5), sx):
                fg.shade(x, 44 + b, -0.9, KNIT)
        for x in range(21, 29):                                                     # la brusa
            fg.px(x, 30 + b, CREAM_B, 3.6 - abs(x - 24.5) * 0.2)
    elif p.f == 'L':
        for y in range(31 + b, 49 + b):
            if (y - b) % 4 == 0:
                fg.px(20, y, TOGGLE, 3.0)
        fg.px(21, 29 + b, CREAM_B, 3.6)
        fg.px(22, 29 + b, CREAM_B, 3.2)
    # el punt: una textura de canalé
    # (es fa a `knit_lvl`, el lvlfn de la rebeca)


def avia_arm(fg, p, spec, i):
    """El cistell de vímet (amb bolets), penjat del braç."""
    if p.f == 'U':
        if i == 0:
            wx, wy = p.wrist[0]
            fg.ell(wx - 1.0, wy + 6.0, 4.0, 3.0, WICKER, 2.0, amp=1.0, cont=(0.2, 0.8))
        return
    if p.f == 'L':
        if i != 0:
            return
        wx, wy = p.arms[0][2]
    else:
        if i != 0:
            return
        wx, wy = p.wrist[0]
    bx, by = wx - 0.5, wy + 7.0
    for a in range(0, 181, 15):                                                     # la nansa
        r = math.radians(a)
        fg.px(bx + math.cos(r) * 3.6, by - 2.0 - math.sin(r) * 4.6, WICKER, 3.0)
    fg.ell(bx - 2.0, by - 2.2, 1.6, 1.0, SHROOM, 3.4, amp=1.0)                      # els bolets
    fg.ell(bx + 1.2, by - 2.6, 1.8, 1.2, SHROOM, 3.0, amp=1.0)
    fg.px(bx - 2.0, by - 2.8, CREAM_B, 4.0)
    fg.ell(bx, by + 1.0, 4.6, 3.2, WICKER, 2.8, amp=1.4, cont=(0.2, 0.8),
           lvlfn=lambda x, y: -0.6 if (int(x) + int(y)) % 2 else 0.2)
    for x in range(int(bx - 4), int(bx + 5)):
        fg.px(x, by - 1.6, WICKER, 3.8)


def knit_lvl(x, y):
    return -0.35 if int(x) % 2 else 0.15


CREAM_B = M((70, 58, 62), (122, 110, 104), (172, 162, 146), (212, 204, 184), (236, 230, 210), (252, 248, 232))
LEGS_OLD = M((24, 20, 22), (44, 38, 40), (66, 58, 58), (92, 82, 80), (120, 110, 104))

AVIA = {
    'skin': SKIN_OLD, 'legs': LEGS_OLD, 'top': KNIT, 'shoes': SHOE_OLD, 'thin': 0.2, 'stoop': 1,
    'iris': (70, 60, 50), 'brow': (170, 166, 170), 'lip': (150, 82, 84),
    'prop': AVIA_PROP,
    'hooks': {'hair': avia_hair, 'over': avia_over, 'arm': avia_arm, 'torso': skirt(PLUM, 71, 2.0),
              'face_q': glasses_q},
}


# ═══════════════════════════════════════════════════════════════════════════
#  La Senyora Pla (NaturaPlus)
# ═══════════════════════════════════════════════════════════════════════════

ALTA_PROP = Prop(tronc=1.04, cames=1.12, ample=0.96)


def smile(fg, p, spec):
    """El somriure de la Senyora Pla: les comissures amunt i les dents (no el treu mai)."""
    if p.talk:
        return
    hx, hy = p.head
    ey = int(hy + 0.5)
    my = ey + 5
    nx = int(hx)
    lip = spec.get('lip', LIP)
    fg.px(nx - 2, my - 1, lip, 0)
    fg.px(nx + 2, my - 1, lip, 0)
    for x in (nx - 1, nx, nx + 1):
        fg.px(x, my, EYE_W, 0)
        fg.px(x, my + 1, lip, 0)


def pla_hair(fg, p, spec):
    """Una melena rossa, llisa i curta (fins a la barbeta), els auriculars i el somriure."""
    hx, hy = p.head
    H = HAIR_BLOND
    sleek = lambda x, y: 0.5 if abs((x - hx) + 3.2) < 0.8 and y < hy else 0.0  # noqa: E731
    if p.f == 'D':
        fg.ell(hx + 0.6, hy - 1.6, 7.6, 7.2, H, 2.8, amp=1.6, cont=(0.2, 0.8), lvlfn=sleek,
               clip=lambda x, y: y <= hy - 3.6 + max(0.0, (x - hx + 2.0)) * 0.5 or abs(x - hx) > 5.6)
        for sx in (-1, 1):
            fg.ell(hx + sx * 6.6, hy + 2.2, 1.8, 5.4, H, 2.4 if sx < 0 else 2.0, amp=0.8)
        for sx in (-1, 1):                                                          # els auriculars
            fg.px(hx + sx * 7.4, hy + 3.0, WHITE, 6.0)
        smile(fg, p, spec)
    elif p.f == 'L':
        fg.ell(hx + 1.2, hy - 1.4, 7.6, 7.2, H, 2.8, amp=1.6, cont=(0.2, 0.8),
               clip=lambda x, y: (x >= hx - 2.0 or y <= hy - 4.6) and not (x < hx + 2.2 and y > hy - 1.4))
        fg.ell(hx + 4.6, hy + 2.6, 3.2, 4.6, H, 2.4, amp=1.0)
        fg.px(hx + 2.6, hy + 2.0, WHITE, 6.0)                                       # l'auricular
        fg.px(hx + 2.6, hy + 3.0, WHITE, 4.4)
        if not p.talk:
            fg.px(int(hx - 5.5) + 1, int(hy + 0.5) + 4, spec['lip'], 0)             # el somriure, de perfil
    else:
        fg.ell(hx, hy - 0.6, 7.6, 7.8, H, 2.8, amp=1.6, cont=(0.2, 0.8))
        fg.ell(hx, hy + 4.0, 7.0, 3.6, H, 2.4, amp=1.0)
        for sx in (-1, 1):
            fg.px(hx + sx * 7.4, hy + 3.0, WHITE, 6.0)


def pla_q(fg, p, spec):
    hx, hy = p.head
    k, dx = C._q_dx(hy, p.q)
    saved = p.head
    p.head = (CX + (hx - CX) * k + dx + C.Q_DX_CARA, hy)
    smile(fg, p, spec)
    p.head = saved


def pla_over(fg, p, spec):
    """L'americana blanca: les solapes, la brusa gris i la insígnia de NaturaPlus (verd fluor)."""
    b = p.bob
    if p.f == 'D':
        for i in range(0, 8):                                                       # la brusa, en V
            for x in range(int(24.5 - (8 - i) * 0.45), int(24.5 + (8 - i) * 0.45) + 1):
                fg.px(x, 30 + i + b, STEELB, 3.0)
        for i in range(0, 9):                                                       # les solapes
            fg.px(24.5 - (8 - i) * 0.45 - 1, 30 + i + b, SUIT_W, 2.6)
            fg.px(24.5 + (8 - i) * 0.45 + 1, 30 + i + b, SUIT_W, 2.0)
        for y in range(38 + b, 51 + b):
            fg.shade(24.5, y, -1.2, SUIT_W)
        fg.px(28, 42 + b, SUIT_W, 2.2); fg.px(28, 46 + b, SUIT_W, 2.2)             # els botons
        fg.px(19, 34 + b, NEON, 3.6); fg.px(20, 34 + b, NEON, 3.0)                 # la insígnia
        fg.px(19, 33 + b, NEON, 3.0)
    elif p.f == 'L':
        for y in range(31 + b, 39 + b):
            fg.px(20, y, STEELB, 3.0)
        fg.px(21, 34 + b, NEON, 3.4)


def pla_arm(fg, p, spec, i):
    """La tauleta, a la mà (amb la pantalla encesa, verda)."""
    if p.f == 'U':
        return
    if p.f == 'L':
        if i != 0:
            return
        wx, wy = p.arms[0][2]
        pts = [(wx - 4.6, wy + 0.6), (wx + 0.6, wy - 0.4), (wx + 1.0, wy + 1.4), (wx - 4.2, wy + 2.4)]
        fg.poly(pts, TABLET, 2.6, cont=(0.0, 0.8))
        fg.px(wx - 3.0, wy + 0.4, NEON, 3.0)
        return
    if i != 1:
        return
    wx, wy = p.wrist[1]
    fg.poly([(wx - 3.0, wy - 1.0), (wx + 1.6, wy - 1.6), (wx + 1.6, wy + 6.4), (wx - 3.0, wy + 7.0)],
            TABLET, 2.4, cont=(0.0, 0.8))
    for y in range(int(wy), int(wy + 6)):
        fg.px(wx - 1.8, y, NEON, 2.0 + (y - wy) * 0.1)
        fg.px(wx - 0.8, y, NEON, 1.6)
    fg.ell(wx + 0.6, wy + 3.0, 1.8, 2.2, spec['skin'], 2.6, amp=1.2)              # la mà, que l'agafa


PLA = {
    'skin': SKIN_PLA, 'legs': SUIT_W, 'top': SUIT_W, 'shoes': SHOE_W, 'thin': 0.8, 'lashes': True,
    'iris': (60, 110, 140), 'brow': (150, 120, 70), 'lip': (176, 62, 78), 'liner': (60, 40, 50),
    'prop': ALTA_PROP,
    'hooks': {'hair': pla_hair, 'over': pla_over, 'arm': pla_arm, 'face_q': pla_q},
}


# ═══════════════════════════════════════════════════════════════════════════
#  La Txell (TV Comarca)
# ═══════════════════════════════════════════════════════════════════════════

def _curls(x, y):
    return -0.9 if (int(x * 0.9) + int(y * 0.9)) % 3 == 0 else 0.35 * math.sin(x * 2.3 + y * 1.7)


def txell_hair(fg, p, spec):
    """Cabell negre arrissat, recollit en una cua alta, i unes arracades daurades."""
    hx, hy = p.head
    H = HAIR_CURL
    if p.f == 'D':
        fg.ell(hx, hy - 1.8, 7.8, 7.4, H, 2.6, amp=1.6, cont=(0.2, 0.8), lvlfn=_curls,
               clip=lambda x, y: y <= hy - 3.4 + ((x - hx) / 7.0) ** 2 * 4.2)
        fg.ell(hx + 1.0, hy - 9.4, 3.6, 2.6, H, 2.6, amp=1.4, cont=(0.2, 0.8), lvlfn=_curls)   # la cua, a dalt
        for sx in (-1, 1):
            fg.px(hx + sx * 6.8, hy + 4.0, BRASS, 4.6)
    elif p.f == 'L':
        fg.ell(hx + 1.0, hy - 1.6, 7.6, 7.2, H, 2.6, amp=1.6, cont=(0.2, 0.8), lvlfn=_curls,
               clip=lambda x, y: (x >= hx - 2.0 or y <= hy - 4.6) and not (x < hx + 2.4 and y > hy - 1.0))
        fg.ell(hx + 6.4, hy - 6.0, 3.6, 3.0, H, 2.6, amp=1.4, cont=(0.2, 0.8), lvlfn=_curls)
        fg.ell(hx + 8.6, hy - 1.0, 2.6, 4.4, H, 2.2, amp=1.2, cont=(0.2, 0.8), lvlfn=_curls)
        fg.px(hx + 2.6, hy + 4.6, BRASS, 4.6)
    else:
        fg.ell(hx, hy - 0.8, 7.8, 7.8, H, 2.6, amp=1.6, cont=(0.2, 0.8), lvlfn=_curls)
        fg.ell(hx, hy - 8.0, 3.8, 3.0, H, 2.6, amp=1.4, cont=(0.2, 0.8), lvlfn=_curls)
        fg.ell(hx, hy - 3.0, 3.0, 4.0, H, 2.2, amp=1.2, lvlfn=_curls)


def txell_over(fg, p, spec):
    """L'americana coral, oberta sobre una samarreta negra, i l'acreditació penjada."""
    b = p.bob
    if p.f == 'D':
        for y in range(30 + b, 50 + b):
            w = 1.5 if y < 44 + b else 0.5
            for x in range(int(24.5 - w), int(24.5 + w) + 1):
                fg.px(x, y, BLACKM, 2.2)
        fg.line(21.5, 30 + b, 23.5, 38 + b, MICB, 2.6)                              # el cordó de l'acreditació
        fg.line(27.5, 30 + b, 25.5, 38 + b, MICB, 2.6)
        for y in range(38 + b, 42 + b):
            for x in (23, 24, 25, 26):
                fg.px(x, y, CREAM_B, 4.2 if y == 38 + b else 3.4)
        fg.px(24, 40 + b, MICB, 2.6); fg.px(25, 40 + b, MICB, 2.6)
    elif p.f == 'L':
        for y in range(31 + b, 40 + b):
            fg.px(20, y, BLACKM, 2.2)
        for y in range(36 + b, 40 + b):
            fg.px(19, y, CREAM_B, 3.6)


def txell_arm(fg, p, spec, i):
    """El micròfon de TV Comarca: el mànec negre, el cub blau amb les lletres i la reixeta."""
    if p.f == 'U':
        return
    if p.f == 'L':
        if i != 0:
            return
        wx, wy = p.arms[0][2]
        fg.limb((wx - 0.6, wy + 2.0), (wx - 2.6, wy - 4.0), 0.8, 0.8, BLACKM, 2.4)
        fg.poly([(wx - 4.0, wy - 4.4), (wx - 0.8, wy - 4.4), (wx - 0.8, wy - 1.4), (wx - 4.0, wy - 1.4)], MICB, 3.0,
                cont=(0.0, 0.8))
        fg.ell(wx - 3.2, wy - 6.0, 1.6, 1.6, STEELB, 2.6, amp=1.2)
        return
    if i != 1:
        return
    wx, wy = p.wrist[1]
    fg.limb((wx, wy + 2.0), (wx - 0.6, wy - 4.0), 0.8, 0.8, BLACKM, 2.4)
    fg.poly([(wx - 2.4, wy - 4.6), (wx + 1.4, wy - 4.6), (wx + 1.4, wy - 1.2), (wx - 2.4, wy - 1.2)], MICB, 3.0,
            cont=(0.0, 0.8))
    fg.px(wx - 1.0, wy - 3.0, CREAM_B, 5.0)                                         # «TV»
    fg.px(wx, wy - 3.0, CREAM_B, 5.0)
    fg.ell(wx - 0.6, wy - 6.2, 1.8, 1.8, STEELB, 2.6, amp=1.2)
    fg.ell(wx, wy + 2.4, 1.9, 2.1, spec['skin'], 2.6, amp=1.2)


TXELL = {
    'skin': SKIN_TXELL, 'legs': JEANS, 'top': CORAL, 'shoes': BOOT, 'thin': 0.6, 'lashes': True,
    'iris': (50, 32, 22), 'brow': (20, 10, 10), 'lip': (140, 56, 60),
    'prop': ALTA_PROP,
    'hooks': {'hair': txell_hair, 'over': txell_over, 'arm': txell_arm},
}


# ═══════════════════════════════════════════════════════════════════════════
#  Criatures: ajudes
# ═══════════════════════════════════════════════════════════════════════════

def h01(*a):
    """Un nombre pseudoaleatori fix (0..1) per a unes coordenades."""
    v = 0
    for x in a:
        v = (v * 1103515245 + int(x) * 2654435761 + 12345) & 0xFFFFFFFF
    v ^= v >> 13
    v = (v * 0x5bd1e995) & 0xFFFFFFFF
    v ^= v >> 15
    return (v & 0xFFFF) / 65535


def flip(img):
    return img.transpose(Image.FLIP_LEFT_RIGHT)


def aclareix(img, box, k):
    """La respiració de les criatures: la zona `box` (x0, y0, x1, y1) un `k` més clara, més a dalt que a baix."""
    if not k:
        return img
    x0, y0, x1, y1 = box
    out = img.copy()
    P_ = out.load()
    for y in range(y0, y1):
        f = 1 + k * (1 - (y - y0) / max(1, y1 - y0))
        for x in range(x0, x1):
            r, g, b, a = P_[x, y]
            if a:
                P_[x, y] = (min(255, int(r * f)), min(255, int(g * f)), min(255, int(b * f)), a)
    return out


SKIN_GNOME = M((66, 26, 34), (120, 56, 52), (174, 96, 78), (214, 138, 108), (236, 174, 140), (250, 206, 176))
BEARD = M((70, 70, 84), (118, 118, 128), (166, 166, 170), (206, 204, 202), (234, 232, 226), (250, 248, 242))
MOSSB = M((14, 34, 14), (30, 64, 24), (56, 100, 36), (94, 140, 56), (140, 180, 90))
LEAF = M((34, 16, 8), (70, 36, 14), (112, 62, 22), (156, 94, 34), (196, 132, 54), (226, 170, 90), dith=0.0)
LEAF2 = M((40, 26, 8), (84, 56, 16), (130, 92, 26), (174, 128, 40), (210, 166, 64), (236, 204, 110), dith=0.0)
PORCINI = M((30, 14, 8), (62, 30, 14), (98, 52, 24), (136, 78, 38), (170, 108, 56), (200, 142, 82))
GILLS = M((90, 74, 50), (150, 132, 96), (204, 188, 146), (236, 226, 190))
GLASS_F = M((8, 6, 6), (22, 16, 14), (40, 30, 24), (62, 48, 36))
GLASS_L = M((40, 70, 80), (90, 140, 150), (160, 210, 214), (224, 248, 248))
TROUS_G = M((14, 12, 10), (28, 24, 20), (44, 38, 30), (64, 56, 44))
VIAL = M((20, 40, 44), (70, 110, 116), (150, 190, 196), (220, 240, 244))


# ═══════════════════════════════════════════════════════════════════════════
#  L'Espora, gnom micòleg (≈35 px)
# ═══════════════════════════════════════════════════════════════════════════
# Un barret de cep, ulleres gruixudes, nas rodó, barba blanca amb molsa i una bata de laboratori feta de fulles
# seques (la vora en punxes de fulla), amb un tub d'assaig turquesa a la butxaca. Fotograma de 34×42, peus a (17, 40).

ESPORA_W, ESPORA_H, ESPORA_FEET = 34, 42, (17, 40)


def _leaf_lvl(x, y):
    """Les fulles de la bata: escates que s'encavalquen (la vora de dalt de cada fulla, més fosca)."""
    row = int((y - 20) // 3)
    off = (row % 2) * 2
    cx = ((x + off) // 4) * 4 + 2 - off
    v = 0.0
    if int(y - 20) % 3 == 0:
        v -= 0.7
    if abs(x - cx) < 0.6 and int(y - 20) % 3 == 2:
        v -= 0.4                                                               # el nervi
    return v + (h01(x // 4, row) - 0.5) * 0.8


def _beard_lvl(x, y):
    return 0.45 * math.sin(x * 1.9 + y * 0.6) - (0.4 if (int(x) + int(y)) % 5 == 0 else 0)


def espora(facing='D', talk=False, closed=False, k=0, walk=None):
    """L'Espora: D (de cara), L (de perfil, mirant a l'esquerra) o U (d'esquena). `talk`: la boca oberta i la mà
    amunt («Excel·lent hifa!»). `closed`: els ulls tancats (Blink). `walk` (0..5): el pas, de sis fotogrames (les
    cames curtes fan passes curtes i el braç es gronxa; el pròleg, quan torna a casa)."""
    fg = Fig(ESPORA_W, ESPORA_H)
    S = SKIN_GNOME
    cx = 17.0
    if facing == 'L':
        _espora_side(fg, S, talk, closed, walk)
    else:
        back = facing == 'U'
        # cames i botes (caminant de cara o d'esquena, cada peu s'aixeca a la seva meitat del pas)
        for sx in (-1, 1):
            lift = 0.0
            if walk is not None:
                lift = max(0.0, math.sin(2 * math.pi * walk / 6 + (0 if sx < 0 else math.pi))) * 1.6
            fg.limb((cx + sx * 2.2, 33.0), (cx + sx * 2.4, 37.0 - lift), 1.8, 1.7, TROUS_G, 2.4 - (0.4 if sx > 0 else 0))
            fg.ell(cx + sx * 2.6, 38.4 - lift, 2.4, 1.7, BOOT, 2.6 - (0.4 if sx > 0 else 0), amp=1.6)
        # la bata de fulles
        top, bot = 20, 35
        e = lambda y: (cx - (5.2 + (y - top) * 0.2), cx + (5.2 + (y - top) * 0.2))  # noqa: E731
        fg.lathe(top, bot, e, LEAF, 2.8, amp=1.6, lvlfn=_leaf_lvl, cont=(0.0, 0.6))
        for x in range(int(cx - 8), int(cx + 9)):                                 # la vora, en punxes de fulla
            if x % 3 == 0:
                fg.erase(x, bot)
            elif x % 3 == 1:
                fg.px(x, bot + 1, LEAF, 2.0)
        if not back:
            for y in range(top + 3, bot):                                         # l'obertura de la bata
                fg.shade(cx, y, -1.2, LEAF)
            for y in range(25, 29):                                               # el tub d'assaig a la butxaca
                fg.px(cx + 3, y, VIAL, 3.6 if y == 25 else 2.6)
            fg.px(cx + 3, 27, TURQ, 3.8)
            fg.px(cx + 3, 28, TURQ, 3.2)
            for x in range(int(cx + 2), int(cx + 5)):
                fg.shade(x, 29, -0.9, LEAF)
        # braços
        for sx in (-1, 1):
            up = talk and sx > 0
            sh = (cx + sx * 5.0, 22.5)
            swing = math.sin(2 * math.pi * walk / 6 + (math.pi if sx < 0 else 0)) * 1.2 if walk is not None else 0.0
            hand = (cx + sx * 8.0, 23.0) if up else (cx + sx * 6.8, 30.0 + swing)
            fg.limb(sh, hand, 1.9, 1.7, LEAF2, 2.6 - (0.5 if sx > 0 else 0), cont=(0.2, 0.8))
            fg.ell(hand[0], hand[1] + (-1.4 if up else 1.4), 1.6, 1.7, S, 2.8 - (0.4 if sx > 0 else 0), amp=1.2)
            if up:
                fg.px(hand[0], hand[1] - 3.4, S, 3.0)                             # el dit, amunt
        # el cap
        hx, hy = cx, 15.0
        fg.ell(hx, hy, 5.4, 5.2, S, 3.0, amp=1.5)
        for sx in (-1, 1):                                                        # orelles
            fg.ell(hx + sx * 5.4, hy + 0.6, 1.2, 1.8, S, 2.6 if sx < 0 else 2.0, amp=1.0)
        if back:
            fg.ell(hx, hy + 1.0, 5.6, 4.8, BEARD, 2.8, amp=1.4, lvlfn=_beard_lvl, cont=(0.2, 0.8))   # el clatell, blanc
            for sx in (-1, 1):
                fg.ell(hx + sx * 5.6, hy + 6.0, 1.6, 3.4, BEARD, 2.4, amp=1.0, lvlfn=_beard_lvl)   # la barba, pels costats
        else:
            for sx in (-1, 1):                                                    # els cabells blancs, pels costats
                fg.ell(hx + sx * 5.0, hy - 0.4, 1.4, 2.6, BEARD, 2.8 if sx < 0 else 2.2, amp=0.8, lvlfn=_beard_lvl)
            # la barba
            jaw = 1.0 if talk else 0.0
            fg.ell(hx, 21.6 + jaw * 0.5, 5.6, 6.4 + jaw * 0.4, BEARD, 2.8, amp=1.5, lvlfn=_beard_lvl, cont=(0.2, 0.8),
                   clip=lambda x, y: y >= 17.6)
            for (mx, my) in ((14, 22), (19, 24), (16, 26), (20, 21), (13, 25)):   # la molsa de la barba
                fg.px(mx, my + jaw, MOSSB, 2.6 + h01(mx, my) * 1.2)
            fg.px(18, 25 + jaw, MOSSB, 3.6)
            if talk:
                for x in (16, 17, 18):
                    fg.px(x, 20, MOUTH, 0)
                fg.px(17, 21, MOUTH, 0)
            fg.ell(hx, 19.0, 3.8, 1.3, BEARD, 3.2, amp=1.0, lvlfn=_beard_lvl)     # el bigoti
            fg.ell(hx, 17.2, 1.8, 1.6, S, 3.2, amp=1.4)                           # el nas, rodó
            fg.px(hx - 0.6, 16.6, S, 4.6)
            # les ulleres: dues anelles gruixudes, el vidre clar i l'ull a dins
            for ex in (hx - 2.6, hx + 2.6):
                for a in range(0, 360, 20):
                    r = math.radians(a)
                    fg.px(ex + math.cos(r) * 2.0, 14.2 + math.sin(r) * 2.0, GLASS_F, 1.6 if a < 180 else 2.4)
                for (dx, dy) in ((0, 0), (-1, 0), (0, -1), (-1, -1), (1, 0), (0, 1)):
                    fg.px(ex + dx * 0.9, 14.2 + dy * 0.9, GLASS_L, 2.2)
                if closed:
                    fg.px(ex - 0.6, 14.4, MOUTH, 0); fg.px(ex + 0.6, 14.4, MOUTH, 0)
                else:
                    fg.px(ex + (0.5 if ex < hx else -0.5), 14.2, (24, 16, 20), 0)  # l'ull, mirant al mig
                fg.px(ex - 1.0, 13.2, GLASS_L, 3.8)                               # el reflex
            fg.px(hx, 14.0, GLASS_F, 2.0)                                          # el pont
            for sx in (-1, 1):                                                    # les celles, blanques i espesses
                for i in range(3):
                    fg.px(hx + sx * (1.6 + i), 11.0 + (0.6 if i == 2 else 0) - (0.6 if sx * i < 0 else 0), BEARD, 4.0)
        # el barret de cep
        fg.ell(hx, 10.2, 8.6, 5.0, PORCINI, 3.0, amp=1.6, cont=(0.2, 0.8), clip=lambda x, y: y <= 11.4,
               lvlfn=lambda x, y: 0.5 if (x - hx + 4) ** 2 + (y - 7) ** 2 < 4 else 0.0)
        for x in range(int(hx - 8), int(hx + 9)):                                 # les làmines, a sota
            fg.px(x, 11.6, GILLS, 2.6 - abs(x - hx) * 0.08)
        fg.px(hx - 4, 7, PORCINI, 4.6); fg.px(hx - 3, 7, PORCINI, 4.2)           # la llum
    return fg.render()


def _espora_side(fg, S, talk, closed, walk=None):
    """De perfil, mirant a l'esquerra. `walk` (0..5): el pas."""
    cx = 17.5
    a = 2 * math.pi * walk / 6 if walk is not None else None
    for d, dl, ph in ((1.0, -0.6, math.pi), (-1.0, 0.0, 0.0)):                    # cames: la del fons primer
        foot, lift = cx + d * 0.6, 0.0
        if a is not None:
            foot = cx - 3.2 * math.sin(a + ph)                                   # endavant (a l'esquerra) i enrere
            lift = max(0.0, math.cos(a + ph)) * 1.4                               # el peu que avança, aixecat
        fg.limb((cx + d * 0.5, 33.0), (foot, 37.0 - lift), 1.8, 1.7, TROUS_G, 2.4 + dl)
        fg.ell(foot - 1.4, 38.4 - lift, 2.8, 1.6, BOOT, 2.6 + dl, amp=1.6)
    top, bot = 20, 35
    e = lambda y: (cx - (4.2 + (y - top) * 0.18), cx + (4.0 + (y - top) * 0.22))  # noqa: E731
    fg.lathe(top, bot, e, LEAF, 2.8, amp=1.6, lvlfn=_leaf_lvl, cont=(0.0, 0.6))
    for x in range(int(cx - 7), int(cx + 8)):
        if x % 3 == 0:
            fg.erase(x, bot)
        elif x % 3 == 1:
            fg.px(x, bot + 1, LEAF, 2.0)
    hx, hy = 16.0, 15.0
    fg.ell(hx + 0.6, hy, 5.2, 5.2, S, 3.0, amp=1.5)
    fg.ell(hx + 3.0, hy + 0.6, 1.2, 1.8, S, 2.4, amp=1.0)                         # l'orella
    fg.ell(hx + 4.4, hy + 0.6, 1.6, 3.4, BEARD, 2.4, amp=0.8, lvlfn=_beard_lvl)    # els cabells del clatell
    jaw = 1.0 if talk else 0.0
    fg.ell(hx - 1.6, 21.4 + jaw * 0.5, 4.6, 6.2, BEARD, 2.8, amp=1.5, lvlfn=_beard_lvl, cont=(0.2, 0.8),
           clip=lambda x, y: y >= 17.6 and x <= hx + 2.6)
    fg.px(hx - 4, 26 + jaw, MOSSB, 2.8)
    fg.px(hx - 1, 23 + jaw, MOSSB, 3.2)
    fg.px(hx - 2, 25 + jaw, MOSSB, 3.6)
    if talk:
        fg.px(hx - 4, 20, MOUTH, 0); fg.px(hx - 3, 20, MOUTH, 0)
    fg.ell(hx - 3.8, 19.0, 2.6, 1.2, BEARD, 3.2, amp=1.0, lvlfn=_beard_lvl)        # el bigoti
    fg.ell(hx - 5.0, 17.0, 1.9, 1.6, S, 3.2, amp=1.4)                              # el nas, que surt
    ex = hx - 3.0                                                                  # les ulleres, una anella
    for a in range(0, 360, 20):
        r = math.radians(a)
        fg.px(ex + math.cos(r) * 1.6, 14.2 + math.sin(r) * 2.0, GLASS_F, 1.6 if a < 180 else 2.4)
    fg.px(ex, 14.2, GLASS_L, 2.2); fg.px(ex - 0.8, 14.2, GLASS_L, 2.2)
    if closed:
        fg.px(ex, 14.4, MOUTH, 0)
    else:
        fg.px(ex - 0.6, 14.4, (24, 16, 20), 0)
    fg.px(ex - 0.8, 13.0, GLASS_L, 3.8)
    fg.line(ex + 1.8, 13.6, hx + 2.4, 14.4, GLASS_F, 1.6)                          # la patilla
    for i in range(3):
        fg.px(ex - 1 + i, 11.2 + (0.6 if i == 2 else 0), BEARD, 4.0)
    # el braç del davant
    hand = (cx - 5.4, 24.0) if talk else (cx - 1.6 + (2.2 * math.sin(a) if a is not None else 0.0), 30.0)
    fg.limb((cx - 0.6, 22.5), hand, 1.9, 1.7, LEAF2, 2.6, cont=(0.2, 0.8))
    fg.ell(hand[0], hand[1] + (-1.4 if talk else 1.4), 1.6, 1.7, S, 2.8, amp=1.2)
    if talk:
        fg.px(hand[0], hand[1] - 3.4, S, 3.0)
    fg.ell(hx + 1.0, 10.2, 8.4, 5.0, PORCINI, 3.0, amp=1.6, cont=(0.2, 0.8), clip=lambda x, y: y <= 11.4,
           lvlfn=lambda x, y: 0.5 if (x - hx + 3) ** 2 + (y - 7) ** 2 < 4 else 0.0)
    for x in range(int(hx - 7), int(hx + 10)):
        fg.px(x, 11.6, GILLS, 2.6 - abs(x - hx) * 0.08)


def espora_respira(img, k):
    return aclareix(img, (9, 21, 26, 30), k)


# ═══════════════════════════════════════════════════════════════════════════
#  Les Fades d'Ortiga (≈32 px)
# ═══════════════════════════════════════════════════════════════════════════
# Primes, amb jaqueta de cuir d'escarabat (negra amb reflexos de color, i punxes d'ortiga a les espatlles), una
# cresta de pelussa de card (blanca, amb la base de la flor) i quatre ales de libèl·lula apedaçades (translúcides,
# amb els nervis i un pegat d'esparadrap). Suren: les ales baten i el cos puja i baixa. La Urtica (la cap) porta
# un tirador. La Pica i la Card són la mateixa fada amb uns altres colors.
# Fotograma de 44×42, peus a (22, 40).

FADA_W, FADA_H, FADA_FEET = 44, 42, (22, 40)

BEETLE_G = M((4, 8, 8), (10, 20, 18), (16, 36, 30), (26, 60, 46), (44, 100, 70), (90, 170, 120), (180, 240, 200),
             dith=0.0)
BEETLE_B = M((6, 4, 14), (14, 10, 34), (26, 20, 62), (44, 34, 100), (74, 60, 156), (130, 120, 220), (210, 200, 255),
             dith=0.0)
BEETLE_C = M((14, 6, 4), (34, 14, 8), (62, 28, 12), (100, 52, 20), (150, 92, 36), (210, 150, 70), (250, 220, 150),
             dith=0.0)
FLUFF_W = M((120, 116, 128), (176, 172, 180), (216, 214, 218), (240, 238, 240), (255, 255, 255))
FLUFF_P = M((110, 40, 80), (170, 80, 130), (222, 130, 176), (246, 184, 214), (255, 228, 240))
FLUFF_Y = M((120, 100, 60), (180, 160, 100), (226, 210, 150), (246, 236, 190), (255, 252, 230))
STUBBLE = M((10, 8, 10), (22, 18, 20), (36, 30, 32), (54, 46, 46))
THISTLE = M((40, 10, 40), (80, 24, 90), (124, 48, 140), (170, 84, 190), (210, 140, 230))
LEG_G = M((8, 16, 8), (18, 32, 16), (30, 50, 26), (46, 72, 38))
LEG_P = M((16, 6, 16), (32, 14, 30), (52, 24, 48), (76, 38, 70))
LEG_B = M((14, 8, 6), (30, 18, 12), (50, 32, 22), (72, 50, 34))
SKIN_FADA_U = M((50, 40, 40), (98, 86, 72), (150, 140, 112), (194, 186, 150), (222, 216, 182), (240, 236, 206))
SKIN_FADA_P = C.SKIN_FOSCA
SKIN_FADA_C = SKIN_IRI
THORN = M((40, 70, 30), (90, 140, 60), (160, 210, 110), (220, 250, 180))
WING = (196, 236, 240)
WING_V = (70, 120, 140)
TAPE = M((90, 70, 50), (160, 136, 100), (214, 194, 150), (240, 226, 190))
SLING = M((30, 16, 8), (64, 36, 16), (104, 64, 30), (146, 98, 50), (186, 134, 74))

FADES = {
    'urtica': {'skin': SKIN_FADA_U, 'jacket': BEETLE_G, 'fluff': FLUFF_W, 'base': THISTLE, 'legs': LEG_G,
               'iris': (40, 120, 60), 'tirador': True, 'brow': (30, 30, 24), 'cella': -1},
    'pica': {'skin': SKIN_FADA_P, 'jacket': BEETLE_B, 'fluff': FLUFF_P, 'base': THISTLE, 'legs': LEG_P,
             'iris': (60, 36, 26), 'brow': (26, 14, 14), 'cella': 1},
    'card': {'skin': SKIN_FADA_C, 'jacket': BEETLE_C, 'fluff': FLUFF_Y, 'base': THISTLE, 'legs': LEG_B,
             'iris': (50, 70, 40), 'brow': (70, 40, 20), 'cella': 0},
}


def _wings(facing, beat):
    """Les quatre ales (una capa a part, translúcida): RGBA del fotograma. `beat` 0..3: on són en el batec."""
    img = Image.new('RGBA', (FADA_W, FADA_H), (0, 0, 0, 0))
    P_ = img.load()
    sway = (0.0, -9.0, -14.0, -6.0)[beat % 4]                                       # graus (amunt = negatiu)
    roots = []
    if facing == 'L':
        roots = [((24.0, 19.0), -30 + sway, 13.0, 2.6), ((24.0, 20.5), 8 + sway * 0.6, 11.0, 2.2)]
        sides = (1,)
    else:
        roots = [((22.0, 19.0), -28 + sway, 13.0, 2.6), ((22.0, 20.5), 10 + sway * 0.6, 11.0, 2.2)]
        sides = (-1, 1)
    for sx in sides:
        for (rx, ry), ang, L, Wd in roots:
            a = math.radians(ang)
            ux, uy = math.cos(a) * sx, math.sin(a)
            for y in range(FADA_H):
                for x in range(FADA_W):
                    dx, dy = x - rx, y - ry
                    t = dx * ux + dy * uy
                    s = -dx * uy + dy * ux
                    if not (0.5 < t < L):
                        continue
                    w = Wd * math.sin(math.pi * min(1.0, t / L) ** 0.8)
                    if abs(s) > w:
                        continue
                    edge = abs(s) > w - 0.9 or t > L - 1.0
                    vein = abs(s) < 0.5 or (int(t) % 4 == 0 and abs(s) < w)
                    if edge:
                        c = WING_V + (230,)
                    elif vein:
                        c = mix(WING, WING_V, 0.55) + (190,)
                    else:
                        c = mix(WING, (255, 255, 255), max(0.0, -s / Wd) * 0.4) + (120,)
                    old = P_[x, y]
                    if old[3] < c[3]:
                        P_[x, y] = c
    # el pegat d'esparadrap, a l'ala de dalt de la dreta de la pantalla (o la del fons, de perfil)
    (rx, ry), ang, L, Wd = roots[0]
    a = math.radians(ang)
    sx = sides[-1]
    px_, py_ = rx + math.cos(a) * sx * L * 0.6, ry + math.sin(a) * L * 0.6
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            X, Y = int(round(px_ + dx)), int(round(py_ + dy))
            if 0 <= X < FADA_W and 0 <= Y < FADA_H:
                P_[X, Y] = (TAPE.c[3] if dy < 1 else TAPE.c[2]) + (255,)
    X, Y = int(round(px_)), int(round(py_))
    if 0 <= X < FADA_W and 0 <= Y < FADA_H:
        P_[X, Y] = TAPE.c[1] + (255,)
    return img


def _fluff_lvl(x, y):
    return 0.6 * math.sin(x * 2.1 + y * 1.3) + (h01(x, y, 7) - 0.5) * 0.8


def fada(qui, facing='D', talk=False, closed=False, k=0):
    """Una fada (urtica, pica o card): D, L o U. `k` 0..3: el batec de les ales i el cos que sura."""
    c = FADES[qui]
    S, J, L_ = c['skin'], c['jacket'], c['legs']
    bob = (0, -1, -1, 0)[k % 4]
    fg = Fig(FADA_W, FADA_H)
    fg.oy = bob
    cx = 22.0
    back = facing == 'U'
    if facing == 'L':
        # de perfil: les cames penjant (les puntes cap avall), el cos prim i el cap
        for d, dl in ((1.2, -0.6), (-0.4, 0.0)):
            fg.limb((cx + d, 27.0), (cx + d - 0.6, 34.0), 1.3, 1.1, L_, 2.4 + dl)
            fg.limb((cx + d - 0.6, 34.0), (cx + d - 2.4, 37.6), 1.2, 0.9, BOOT, 2.4 + dl, amp=1.4)
        e = lambda y: (cx - 2.6, cx + 2.4)  # noqa: E731
        fg.lathe(17, 27, e, J, 3.0, amp=2.0, cont=(0.0, 0.6),
                 lvlfn=lambda x, y: 1.4 if (x - cx + 1) ** 2 + (y - 20) ** 2 < 2.5 else 0.0)
        for (tx, ty) in ((cx + 1, 16.6), (cx + 2, 17.4)):
            fg.px(tx, ty, THORN, 2.8)
        hand = (cx - 4.2, 20.0) if talk else (cx - 1.0, 26.0)
        fg.limb((cx - 0.4, 18.6), hand, 1.2, 1.0, J, 2.6, cont=(0.2, 0.8))
        fg.ell(hand[0], hand[1] + 1.0, 1.1, 1.1, S, 3.0, amp=1.0)
        hx, hy = cx - 0.6, 12.0
        fg.ell(hx + 0.4, hy, 4.0, 4.2, S, 3.0, amp=1.5)
        fg.ell(hx - 3.6, hy + 1.2, 1.0, 1.0, S, 3.2, amp=1.0)                       # el nas, petit i punxegut
        fg.px(hx + 2.4, hy - 0.4, S, 2.4); fg.px(hx + 3.2, hy - 1.4, S, 2.8)       # l'orella punxeguda
        ex, ey = int(hx - 2), int(hy)
        if closed:
            fg.px(ex, ey, MOUTH, 0)
        else:
            fg.px(ex, ey - 1, MOUTH, 0); fg.px(ex, ey, c['iris'], 0)
        fg.px(ex - 1 + 0, ey - 2 + (1 if c['cella'] < 0 else 0), c['brow'], 0)
        fg.px(ex, ey - 2, c['brow'], 0)
        fg.px(ex - 1, ey + 2, MOUTH if talk else mix(LIP, S.c[2], 0.3), 0)
        if talk:
            fg.px(ex - 1, ey + 3, MOUTH, 0)
        # la cresta, del front al clatell
        fg.ell(hx + 1.6, hy - 1.6, 3.0, 2.4, STUBBLE, 2.0, amp=0.8, clip=lambda x, y: x > hx - 0.6 and y < hy - 0.4)
        for i in range(5):
            t = i / 4
            bx, by = hx - 1.6 + t * 4.6, hy - 3.8 + t * 1.4
            fg.ell(bx, by, 0.9, 0.7, c['base'], 2.4, amp=0.8)
            fg.ell(bx + 0.4, by - 1.8 - math.sin(t * math.pi) * 0.8, 1.4, 1.8, c['fluff'], 2.8, amp=1.2,
                   lvlfn=_fluff_lvl)
        if c.get('tirador'):
            _tirador(fg, hand, side=True)
    else:
        for sx in (-1, 1):
            dl = -0.5 if sx > 0 else 0.0
            fg.limb((cx + sx * 1.2, 27.0), (cx + sx * 1.6, 34.0), 1.3, 1.1, L_, 2.4 + dl)
            fg.limb((cx + sx * 1.6, 34.0), (cx + sx * 1.4, 37.4), 1.2, 1.0, BOOT, 2.4 + dl, amp=1.4)
        e = lambda y: (cx - 3.0 - (0.4 if y > 23 else 0), cx + 3.0 + (0.4 if y > 23 else 0))  # noqa: E731
        fg.lathe(17, 27, e, J, 3.0, amp=2.0, cont=(0.0, 0.6),
                 lvlfn=lambda x, y: 1.4 if (x - cx + 1.6) ** 2 + (y - 20) ** 2 < 2.5 else
                 (0.8 if (x - cx - 1.6) ** 2 + (y - 24) ** 2 < 1.2 else 0.0))
        if not back:
            for y in range(19, 27):                                               # la cremallera
                fg.shade(cx, y, -1.0, J)
            fg.px(cx, 19, STEELB, 3.4)
        for sx in (-1, 1):                                                        # les espatlles amb punxes d'ortiga
            fg.ell(cx + sx * 3.2, 17.8, 1.6, 1.2, J, 3.2 if sx < 0 else 2.6, amp=1.0)
            fg.px(cx + sx * 3.6, 16.4, THORN, 2.8)
            fg.px(cx + sx * 4.6, 16.8, THORN, 2.4)
        for sx in (-1, 1):
            up = talk and sx > 0
            hand = (cx + sx * 5.6, 15.4) if up else (cx + sx * 4.6, 25.0)
            fg.limb((cx + sx * 3.4, 18.4), hand, 1.2, 1.0, J, 2.6 - (0.5 if sx > 0 else 0), cont=(0.2, 0.8))
            fg.ell(hand[0], hand[1] + (-0.6 if up else 1.0), 1.1, 1.1, S, 3.0 - (0.4 if sx > 0 else 0), amp=1.0)
            if c.get('tirador') and sx < 0 and not back:
                _tirador(fg, hand)
        hx, hy = cx, 12.0
        for sx in (-1, 1):                                                        # les orelles punxegudes
            fg.px(hx + sx * 4.4, hy + 0.4, S, 2.6 if sx < 0 else 2.0)
            fg.px(hx + sx * 5.2, hy - 0.6, S, 2.8 if sx < 0 else 2.2)
        fg.ell(hx, hy, 4.0, 4.2, S, 3.0, amp=1.5)
        fg.limb((hx, hy + 3.4), (hx, hy + 5.4), 1.2, 1.2, S, 2.4)                   # el coll
        if not back:
            for sx in (-1, 1):                                                    # els ulls: grossos, foscos
                ex = int(hx + (-2 if sx < 0 else 1))
                if closed:
                    fg.px(ex, hy, MOUTH, 0); fg.px(ex + 1, hy, MOUTH, 0)
                else:
                    fg.px(ex, hy - 1, MOUTH, 0); fg.px(ex + 1, hy - 1, MOUTH, 0)
                    fg.px(ex + (1 if sx < 0 else 0), hy, c['iris'], 0)
                    fg.px(ex + (0 if sx < 0 else 1), hy, EYE_W, 0)
                # la cella: la Urtica, arrufada; la Pica, amunt (tot és «brutal»); la Card, recta
                d = c['cella']
                fg.px(ex, hy - 2.6 + (0.8 if (d < 0) == (sx > 0) and d else 0) - (0.6 if d > 0 and sx < 0 else 0), c['brow'], 0)
                fg.px(ex + 1, hy - 2.6 + (0.8 if (d < 0) == (sx < 0) and d else 0) - (0.6 if d > 0 and sx > 0 else 0), c['brow'], 0)
            if talk:
                fg.px(hx - 1, hy + 2.4, MOUTH, 0); fg.px(hx, hy + 2.4, MOUTH, 0); fg.px(hx - 0.6, hy + 3.2, MOUTH, 0)
            else:
                fg.px(hx - 1, hy + 2.4, mix(LIP, S.c[2], 0.2), 0); fg.px(hx, hy + 2.4, mix(LIP, S.c[2], 0.4), 0)
            fg.shade(hx - 0.6, hy + 1.2, -0.7, S)                                 # el nas
        # els costats rapats (una ombra de cabell fosc: la pelussa només fa la cresta)
        fg.ell(hx, hy - 1.4, 4.0, 2.8, STUBBLE, 2.2, amp=0.8, clip=lambda x, y: y < hy - 2.2 + abs(x - hx) * 0.25)
        fg.ell(hx, hy - 4.0, 1.8, 0.9, c['base'], 2.6, amp=0.8)                   # la base de la flor
        for i, (dx, dy, r) in enumerate(((0.0, -6.2, 1.9), (-1.0, -7.8, 1.4), (1.0, -8.0, 1.4),
                                         (-1.8, -5.4, 1.2), (1.8, -5.6, 1.2))):
            fg.ell(hx + dx, hy + dy, r, r * 1.1, c['fluff'], 2.9 - (0.3 if dx > 0 else 0), amp=1.2, lvlfn=_fluff_lvl)
    body = fg.render()
    wings = _wings(facing, k)
    if facing == 'U':                                                             # d'esquena, les ales al davant
        out = body.copy()
        out.alpha_composite(wings, (0, bob))
        return out
    out = Image.new('RGBA', (FADA_W, FADA_H), (0, 0, 0, 0))
    out.alpha_composite(wings, (0, bob))
    out.alpha_composite(body)
    return out


def _tirador(fg, hand, side=False):
    """El tirador de la Urtica (una forquilla de branca amb la goma), a la mà."""
    hx, hy = hand
    fg.limb((hx, hy + 2.6), (hx, hy - 1.0), 0.7, 0.7, SLING, 2.8)
    fg.limb((hx, hy - 1.0), (hx - 1.6, hy - 3.6), 0.6, 0.6, SLING, 3.0)
    fg.limb((hx, hy - 1.0), (hx + 1.6, hy - 3.6), 0.6, 0.6, SLING, 2.4)
    fg.px(hx - 0.6, hy - 2.6, RAIN, 3.0)
    fg.px(hx + 0.6, hy - 2.6, RAIN, 3.0)


def fada_respira(img, k):
    return img                                     # (ja sura: el batec de les ales i el cos que puja fan la feina)


# ═══════════════════════════════════════════════════════════════════════════
#  Els Gripaus Buròcrates (≈34-36 px)
# ═══════════════════════════════════════════════════════════════════════════
# Un gripau assegut dret, panxut: la pell berrugosa, la panxa clara, els ulls daurats amb la nineta horitzontal i
# la boca ampla. El Registrador Bufó porta armilla granat amb la cadena del rellotge, una visera verda de comptable i
# el segell de goma a la mà; el vaguista, la mateixa base amb uns altres colors i una pancarta «VAGA».
# Fotograma de 48×48, peus a (24, 46).

GRIPAU_W, GRIPAU_H, GRIPAU_FEET = 48, 48, (24, 46)

TOAD_B = M((20, 18, 8), (40, 36, 16), (64, 56, 26), (92, 80, 40), (122, 106, 56), (152, 136, 78), (184, 170, 110))
TOAD_G = M((12, 22, 10), (24, 42, 18), (40, 64, 28), (60, 90, 40), (84, 118, 54), (112, 146, 74), (148, 178, 104))
BELLY_B = M((96, 80, 44), (150, 132, 84), (200, 184, 128), (230, 218, 166), (246, 238, 200))
BELLY_G = M((90, 96, 52), (140, 150, 92), (190, 198, 136), (222, 228, 172), (242, 246, 206))
VEST_R = M((24, 6, 10), (50, 12, 20), (84, 22, 32), (120, 36, 44), (156, 56, 60), (190, 86, 84), dith=0.0)
VEST_Y = M((44, 30, 6), (84, 60, 12), (130, 96, 22), (176, 134, 38), (214, 174, 64), (240, 210, 110), dith=0.0)
VISOR_G = M((10, 50, 30), (20, 100, 60), (40, 150, 90), (90, 200, 140), (170, 240, 200))
VISOR_N = M((30, 30, 36), (70, 70, 80), (120, 120, 130), (170, 170, 180), (220, 220, 226))
GOLD_EYE = M((70, 40, 6), (140, 90, 10), (210, 150, 30), (246, 200, 70), (255, 236, 150))
RUBBER = M((40, 6, 10), (90, 16, 20), (150, 30, 34), (200, 56, 50))
STAMPW = M((30, 16, 8), (64, 36, 16), (104, 64, 30), (146, 98, 50), (186, 134, 74), (220, 176, 110))
BOARD = M((60, 44, 26), (110, 86, 54), (160, 134, 92), (204, 180, 132), (232, 214, 172), (248, 236, 204))
PAINT_R = (170, 30, 34)
FONT_VAGA = {'V': ('#.#', '#.#', '#.#', '#.#', '.#.'), 'A': ('.#.', '#.#', '###', '#.#', '#.#'),
             'G': ('.##', '#..', '#.#', '#.#', '.##'), '!': ('#', '#', '#', '.', '#')}

GRIPAUS = {
    'bufo': {'skin': TOAD_B, 'belly': BELLY_B, 'vest': VEST_R, 'visor': VISOR_G, 'segell': True, 'cadena': True},
    'gripau': {'skin': TOAD_G, 'belly': BELLY_G, 'vest': VEST_Y, 'visor': VISOR_N, 'pancarta': True},
}


def _warts(fg, mat, cx, cy, rx, ry, seed):
    """Berrugues: punts més clars amb l'ombra a sota, escampats per la pell."""
    for i in range(int(rx * ry / 5)):
        x = cx + (h01(seed, i, 1) * 2 - 1) * rx
        y = cy + (h01(seed, i, 2) * 2 - 1) * ry
        if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 < 0.8 and fg.get(x, y) and fg.get(x, y)[0] is mat:
            fg.shade(x, y, 0.9, mat)
            fg.shade(x, y + 1, -0.6, mat)


def gripau(qui, facing='D', talk=False, closed=False, k=0):
    """Un gripau buròcrata (bufo o gripau): D, L o U. `k`: la gola, que s'infla i es desinfla (Idle)."""
    c = GRIPAUS[qui]
    T, B = c['skin'], c['belly']
    fg = Fig(GRIPAU_W, GRIPAU_H)
    gola = (0.0, 0.5, 1.0, 0.5)[k % 4]
    if facing == 'L':
        _gripau_side(fg, c, talk, closed, gola)
        return fg.render()
    back = facing == 'U'
    cx = 24.0
    if c.get('pancarta') and not back:
        _pancarta(fg, c, front=True)
    # les potes de darrere, plegades als costats, i els peus palmats al davant
    for sx in (-1, 1):
        dl = -0.5 if sx > 0 else 0.0
        fg.ell(cx + sx * 10.4, 38.0, 6.0, 5.6, T, 2.6 + dl, amp=1.6, cont=(0.2, 0.8))
        fg.ell(cx + sx * 7.6, 44.4, 4.6, 1.8, T, 2.4 + dl, amp=1.2, cont=(0.2, 0.8))
        for t in range(3):                                                        # els dits
            fg.ell(cx + sx * (4.4 + t * 2.6), 45.4, 1.1, 1.0, T, 2.8 + dl, amp=1.0)
    # el cos, en forma de pera
    fg.ell(cx, 32.0, 11.6, 12.0, T, 2.8, amp=1.6, cont=(0.2, 0.8))
    if not back:
        fg.ell(cx, 34.0, 8.0, 9.4, B, 2.8, amp=1.4)                               # la panxa
        # l'armilla: dos panells, oberta al mig, amb botons i (el Bufó) la cadena del rellotge
        for sx in (-1, 1):
            pts = [(cx + sx * 1.2, 24.0), (cx + sx * 10.6, 26.0), (cx + sx * 10.4, 36.0), (cx + sx * 3.0, 40.0),
                   (cx + sx * 2.0, 36.0)]
            fg.poly(pts, c['vest'], 2.8 - (0.5 if sx > 0 else 0), amp=0.8, cont=(0.3, 0.9),
                    normal=lambda x, y, sx=sx: (sx * min(1.0, abs(x - cx) / 10), 0.0, 0.8))
        for y in (29, 33, 37):
            fg.px(cx - 2.6 - (y - 29) * 0.1, y, GOLD_EYE, 3.4)
        if c.get('cadena'):
            for i in range(7):
                t = i / 6
                fg.px(cx - 2.4 + t * 7.0, 33.0 + math.sin(t * math.pi) * 2.2, BRASS, 4.0 - (i % 2) * 0.8)
            fg.px(cx + 5.0, 33.6, BRASS, 4.6)
            fg.px(cx + 5.6, 34.4, BRASS, 3.6)
    else:
        fg.ell(cx, 30.0, 10.6, 9.0, c['vest'], 2.6, amp=1.4, cont=(0.2, 0.8), clip=lambda x, y: y > 23)
    # el cap: ample, amb la gola a sota
    fg.ell(cx, 19.4, 12.4, 7.6, T, 3.0, amp=1.6, cont=(0.2, 0.8))
    if not back:
        fg.ell(cx, 24.4 + gola * 0.4, 6.0 + gola * 0.8, 2.0 + gola * 0.8, B, 3.0 + gola * 0.4, amp=1.2)   # la gola
    _warts(fg, T, cx, 30, 11, 11, 3)
    _warts(fg, T, cx, 18, 11, 6, 5)
    # els ulls, a dalt del cap
    for sx in (-1, 1):
        ex, ey = cx + sx * 7.6, 13.2
        fg.ell(ex, ey, 3.6, 3.4, T, 3.2 - (0.4 if sx > 0 else 0), amp=1.4, cont=(0.2, 0.8))
        if not back:
            if closed:
                for dx in (-2, -1, 0, 1, 2):
                    fg.px(ex + dx, ey + 0.4, T, 1.0)
            else:
                fg.ell(ex, ey + 0.4, 2.4, 2.0, GOLD_EYE, 3.0, amp=1.4)
                for dx in (-1, 0, 1):                                             # la nineta horitzontal
                    fg.px(ex + dx, ey + 0.4, MOUTH, 0)
                fg.px(ex - 1.2, ey - 0.6, GOLD_EYE, 5.0)                          # la llum
                for dx in (-2, -1, 0, 1, 2):                                      # la parpella, solemne
                    fg.px(ex + dx, ey - 1.4, T, 2.0)
    # la visera de comptable: la cinta i la visera, entre els ulls
    V = c['visor']
    if not back:
        fg.poly([(cx - 4.6, 10.6), (cx + 4.6, 10.6), (cx + 6.0, 14.6), (cx - 6.0, 14.6)], V, 2.6, amp=0.6,
                cont=(0.0, 1.0), normal=lambda x, y: (0.0, -0.4, 0.9))
        for x in range(int(cx - 5), int(cx + 6)):
            fg.px(x, 10.6, V, 4.0)
            fg.shade(x, 15.6, -1.0, T)                                            # l'ombra de la visera
    else:
        for x in range(int(cx - 9), int(cx + 10)):
            fg.px(x, 12.6 + abs(x - cx) * 0.05, V, 1.6)
    if not back:
        # el nas (dos foradets) i la boca: ampla, amb les comissures avall
        fg.px(cx - 1.6, 17.4, T, 0.6); fg.px(cx + 1.6, 17.4, T, 0.6)
        if talk:
            for x in range(int(cx - 7), int(cx + 8)):
                d = abs(x - cx)
                h = max(0, int(2.6 - d * 0.3))
                for y in range(20, 21 + h):
                    fg.px(x, y, MOUTH if y < 20 + h else (190, 90, 100), 0)
            fg.ell(cx, 21.6, 2.4, 0.9, M((120, 40, 50), (170, 70, 80), (210, 110, 120)), 1.6, amp=0.6)   # la llengua
        else:
            for x in range(int(cx - 9), int(cx + 10)):
                d = abs(x - cx)
                fg.px(x, 20.2 + (0.0 if d < 6 else (d - 6) * 0.35), T, 0.4)
    # els braços, prims, amb els dits; el segell de goma o la pancarta
    for sx in (-1, 1):
        dl = -0.5 if sx > 0 else 0.0
        sh = (cx + sx * 9.6, 26.0)
        if back:
            hand = (cx + sx * 11.4, 34.0)
        elif c.get('segell') and sx > 0:
            hand = (cx + 8.0, 29.0) if not talk else (cx + 10.0, 22.0)
        elif c.get('pancarta') and sx > 0:
            hand = (cx + 9.4, 26.0)
        else:
            hand = (cx + sx * 8.6, 35.0) if not (talk and sx < 0) else (cx - 11.6, 27.0)
        fg.limb(sh, hand, 1.6, 1.3, T, 2.6 + dl, cont=(0.2, 0.8))
        fg.ell(hand[0], hand[1] + 0.8, 1.6, 1.3, T, 3.0 + dl, amp=1.0)
        for t in (-1, 0, 1):
            fg.px(hand[0] + t * 1.0, hand[1] + 2.2, T, 2.4 + dl)
        if c.get('segell') and sx > 0 and not back:
            hx, hy = hand
            fg.ell(hx, hy - 3.6, 1.6, 1.4, STAMPW, 3.2, amp=1.2)                  # el pom
            fg.limb((hx, hy - 2.6), (hx, hy + 1.4), 0.8, 0.8, STAMPW, 2.8)
            fg.poly([(hx - 2.6, hy + 1.4), (hx + 2.6, hy + 1.4), (hx + 2.6, hy + 3.0), (hx - 2.6, hy + 3.0)],
                    STAMPW, 2.4, cont=(0.0, 0.8))
            for x in range(int(hx - 2), int(hx + 3)):
                fg.px(x, hy + 3.6, RUBBER, 2.6)
    if c.get('pancarta') and back:
        _pancarta(fg, c, front=False)
    return fg.render()


def _pancarta(fg, c, front=True, x0=26, y0=1):
    """La pancarta del vaguista: un pal i un cartró amb «VAGA!» pintat de vermell (de darrere, el cartró llis)."""
    fg.limb((x0 + 4.4, y0 + 11.0), (x0 + 4.4, 27.0), 0.8, 0.8, STAMPW, 2.8)
    S = [(x0, y0), (x0 + 19, y0), (x0 + 19, y0 + 11), (x0, y0 + 11)]
    fg.poly(S, BOARD, 3.2, cont=(0.4, 1.0), normal=lambda x, y: (0.0, -0.2, 0.95))
    for x in range(x0, x0 + 20):                                                  # la vora gastada
        if h01(x, 9) > 0.7:
            fg.shade(x, y0 + 11, -1.0, BOARD)
    if front:
        x = x0 + 2
        for ch in 'VAGA!':
            g = FONT_VAGA[ch]
            for j, row in enumerate(g):
                for i, cc in enumerate(row):
                    if cc == '#':
                        fg.px(x + i, y0 + 3 + j, PAINT_R, 0)
            x += len(g[0]) + 1


def _gripau_side(fg, c, talk, closed, gola):
    """De perfil, mirant a l'esquerra."""
    T, B = c['skin'], c['belly']
    cx = 25.0
    if c.get('pancarta'):
        _pancarta(fg, c, front=False, x0=14, y0=1)
    fg.ell(cx + 4.6, 37.6, 7.0, 6.2, T, 2.4, amp=1.6, cont=(0.2, 0.8))           # la pota de darrere
    fg.ell(cx - 3.0, 44.6, 7.0, 1.8, T, 2.6, amp=1.2, cont=(0.2, 0.8))           # el peu, llarg
    fg.ell(cx + 1.0, 32.0, 9.6, 11.6, T, 2.8, amp=1.6, cont=(0.2, 0.8))
    fg.ell(cx - 4.4, 34.0, 4.0, 8.4, B, 2.8, amp=1.2, clip=lambda x, y: x < cx - 3.0)   # la panxa, de costat
    fg.poly([(cx - 6.4, 24.0), (cx + 4.0, 24.0), (cx + 6.6, 36.0), (cx - 4.6, 40.0), (cx - 8.6, 34.0)],
            c['vest'], 2.8, amp=0.8, cont=(0.3, 0.9), normal=lambda x, y: (-0.4, 0.0, 0.9))
    for y in (29, 33, 37):
        fg.px(cx - 6.6 + (y - 29) * 0.1, y, GOLD_EYE, 3.4)
    fg.ell(cx - 3.0, 19.6, 10.4, 7.2, T, 3.0, amp=1.6, cont=(0.2, 0.8))           # el cap, el musell endavant
    fg.ell(cx - 7.4, 24.2 + gola * 0.4, 3.6 + gola * 0.6, 1.8 + gola * 0.8, B, 3.0, amp=1.2)
    _warts(fg, T, cx + 1, 31, 9, 11, 4)
    _warts(fg, T, cx - 2, 18, 9, 6, 6)
    ex, ey = cx - 6.0, 13.6
    fg.ell(ex, ey, 3.4, 3.2, T, 3.2, amp=1.4, cont=(0.2, 0.8))
    if closed:
        for dx in (-2, -1, 0, 1):
            fg.px(ex + dx, ey + 0.4, T, 1.0)
    else:
        fg.ell(ex - 0.6, ey + 0.4, 2.0, 1.8, GOLD_EYE, 3.0, amp=1.2)
        fg.px(ex - 1, ey + 0.4, MOUTH, 0); fg.px(ex, ey + 0.4, MOUTH, 0)
        fg.px(ex - 1.6, ey - 0.6, GOLD_EYE, 5.0)
        for dx in (-2, -1, 0, 1):
            fg.px(ex + dx, ey - 1.2, T, 2.0)
    V = c['visor']                                                                # la visera, endavant
    fg.poly([(ex - 1.0, 10.4), (ex + 7.0, 10.4), (ex + 7.0, 11.6), (ex - 5.6, 13.2)], V, 2.8, amp=0.6, cont=(0.0, 1.0))
    if talk:
        for x in range(int(cx - 13), int(cx - 3)):
            fg.px(x, 21, MOUTH, 0)
            if x < cx - 7:
                fg.px(x, 22, MOUTH, 0)
    else:
        for x in range(int(cx - 13), int(cx - 2)):
            fg.px(x, 21.0 + (0.6 if x > cx - 5 else 0), T, 0.4)
    fg.px(cx - 12.4, 17.6, T, 0.6)                                                # el narius
    hand = (cx - 8.4, 26.0) if (talk or c.get('segell')) else (cx - 6.4, 36.0)
    if c.get('pancarta'):
        hand = (cx - 6.6, 26.0)
    fg.limb((cx - 2.0, 26.0), hand, 1.6, 1.3, T, 2.8, cont=(0.2, 0.8))
    fg.ell(hand[0], hand[1] + 0.8, 1.6, 1.3, T, 3.0, amp=1.0)
    if c.get('segell'):
        hx, hy = hand
        fg.ell(hx, hy - 3.6, 1.6, 1.4, STAMPW, 3.2, amp=1.2)
        fg.limb((hx, hy - 2.6), (hx, hy + 1.4), 0.8, 0.8, STAMPW, 2.8)
        fg.poly([(hx - 2.6, hy + 1.4), (hx + 2.6, hy + 1.4), (hx + 2.6, hy + 3.0), (hx - 2.6, hy + 3.0)],
                STAMPW, 2.4, cont=(0.0, 0.8))
        for x in range(int(hx - 2), int(hx + 3)):
            fg.px(x, hy + 3.6, RUBBER, 2.6)


def gripau_respira(img, k):
    return img                                     # (la gola ja s'infla i es desinfla: és el seu respirar)
