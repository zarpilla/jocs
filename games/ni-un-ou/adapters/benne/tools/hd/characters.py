"""
Personatges en pixel art HD: es dibuixen a la mida real del fotograma (49×87 una persona),
amb volum (llum de dalt a l'esquerra), rampes per material i contorn fosc selectiu.

Cada figura es munta amb primitives amb volum (el·lipsoides, extremitats en càpsula, troncs "de torn")
que guarden, per a cada píxel, el material i un nivell de llum; al final es quantitza amb la rampa del
material i s'hi afegeix el contorn exterior (fosc, tenyit del color del costat).

Ho fa servir draw_characters.py, que escriu els fulls i els .character.json.
"""
import math

from PIL import Image

from hd.pix import B4, mix

# Llum de dalt a l'esquerra (i una mica de cara)
LX, LY, LZ = -0.45, -0.6, 0.66
INK = (18, 10, 22)


class Mat:
    """Material: rampa (fosc → clar) i quant dithering admet."""

    def __init__(self, cols, dith=0.0):
        self.c = [tuple(c) for c in cols]
        self.d = dith

    def col(self, lvl, x, y):
        i = math.floor(lvl + (B4[y & 3][x & 3] - 0.5) * self.d + 0.5)
        return self.c[max(0, min(len(self.c) - 1, i))]


class Fig:
    """Figura: buffer de (material, nivell) amb primitives amb volum. `oy` desplaça (balanceig)."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.buf = [[None] * w for _ in range(h)]
        self.ox = self.oy = 0

    # ─── nucli ───
    def _paint(self, pix, mat, base, amp, cont, lvlfn):
        for (x, y), (nx, ny, nz) in pix.items():
            if not (0 <= x < self.w and 0 <= y < self.h):
                continue
            l = base + amp * (nx * LX + ny * LY + nz * LZ - 0.35)
            if cont:
                if (x + 1, y) not in pix or (x, y + 1) not in pix:
                    l -= cont[1]
                elif (x - 1, y) not in pix or (x, y - 1) not in pix:
                    l -= cont[0]
            if lvlfn:
                l += lvlfn(x, y)
            self.buf[y][x] = (mat, l)

    def ell(self, cx, cy, rx, ry, mat, base, amp=1.6, cont=None, lvlfn=None, clip=None):
        """El·lipsoide."""
        cx += self.ox
        cy += self.oy
        pix = {}
        for y in range(math.floor(cy - ry), math.ceil(cy + ry) + 1):
            for x in range(math.floor(cx - rx), math.ceil(cx + rx) + 1):
                nx, ny = (x - cx) / rx, (y - cy) / ry
                r2 = nx * nx + ny * ny
                if r2 <= 1 and (clip is None or clip(x, y - self.oy)):
                    pix[(x, y)] = (nx, ny, math.sqrt(1 - r2))
        self._paint(pix, mat, base, amp, cont, lvlfn)
        return pix

    def limb(self, a, b, r0, r1, mat, base, amp=1.6, cont=None, lvlfn=None, clip=None):
        """Càpsula de a a b (radis r0 → r1), ombrejada com un cilindre amb puntes esfèriques."""
        ax, ay = a[0] + self.ox, a[1] + self.oy
        bx, by = b[0] + self.ox, b[1] + self.oy
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
                if d2 <= 1 and (clip is None or clip(x, y - self.oy)):
                    pix[(x, y)] = (ex / r, ey / r, math.sqrt(1 - d2))
        self._paint(pix, mat, base, amp, cont, lvlfn)
        return pix

    def lathe(self, y0, y1, edges, mat, base, amp=1.6, cont=None, lvlfn=None, tilt=0.0):
        """Tronc: per a cada fila y, edges(y) → (xl, xr); ombreig cilíndric horitzontal."""
        pix = {}
        for y in range(math.floor(y0), math.floor(y1) + 1):
            e = edges(y)
            if not e:
                continue
            xl, xr = e[0] + self.ox, e[1] + self.ox
            mid, half = (xl + xr) / 2, max(0.5, (xr - xl) / 2)
            for x in range(math.ceil(xl - 0.01), math.floor(xr + 0.01) + 1):
                u = max(-1.0, min(1.0, (x - mid) / (half + 0.5)))
                nz = math.sqrt(max(0.0, 1 - u * u - tilt * tilt))
                pix[(x, y + self.oy)] = (u, tilt, nz)
        self._paint(pix, mat, base, amp, cont, lvlfn)
        return pix

    def poly(self, pts, mat, base, amp=0.0, cont=None, lvlfn=None, normal=None):
        """Polígon ple; `normal(x, y)` → (nx, ny, nz) opcional (si no, de cara)."""
        pts = [(px + self.ox, py + self.oy) for px, py in pts]
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
                    pix[(x, y)] = normal(x, y - self.oy) if normal else (0.0, 0.0, 1.0)
        self._paint(pix, mat, base, amp, cont, lvlfn)
        return pix

    def px(self, x, y, mat, lvl):
        x, y = int(round(x + self.ox)), int(round(y + self.oy))
        if 0 <= x < self.w and 0 <= y < self.h:
            self.buf[y][x] = (mat, lvl)

    def line(self, x0, y0, x1, y1, mat, lvl):
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        n = int(math.ceil(n))
        for i in range(n + 1):
            t = i / n
            self.px(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, mat, lvl)

    def shade(self, x, y, d, only=None):
        """Suma d al nivell d'un píxel ja pintat (opcionalment només si és del material `only`)."""
        x, y = int(round(x + self.ox)), int(round(y + self.oy))
        if 0 <= x < self.w and 0 <= y < self.h and self.buf[y][x]:
            m, l = self.buf[y][x]
            if only is None or m is only or (isinstance(only, (list, tuple)) and m in only):
                self.buf[y][x] = (m, l + d)

    def get(self, x, y):
        x, y = int(round(x + self.ox)), int(round(y + self.oy))
        if 0 <= x < self.w and 0 <= y < self.h:
            return self.buf[y][x]
        return None

    def erase(self, x, y):
        x, y = int(round(x + self.ox)), int(round(y + self.oy))
        if 0 <= x < self.w and 0 <= y < self.h:
            self.buf[y][x] = None

    # ─── sortida ───
    def render(self, outline=True):
        img = Image.new('RGBA', (self.w, self.h), (0, 0, 0, 0))
        P = img.load()
        for y in range(self.h):
            for x in range(self.w):
                v = self.buf[y][x]
                if v:
                    m, l = v
                    P[x, y] = (m.col(l, x, y) if isinstance(m, Mat) else m) + (255,)
        if outline:
            src = [[self.buf[y][x] for x in range(self.w)] for y in range(self.h)]
            for y in range(self.h):
                for x in range(self.w):
                    if src[y][x]:
                        continue
                    nb = []
                    for dx, dy in ((1, 0), (0, 1), (-1, 0), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.w and 0 <= ny < self.h and src[ny][nx]:
                            nb.append((dx, dy, src[ny][nx][0]))
                    if not nb:
                        continue
                    dx, dy, m = nb[0]
                    dark = m.c[0] if isinstance(m, Mat) else m
                    # costat il·luminat (la figura és a la dreta/sota del contorn): contorn una mica més clar
                    lit = all(d[0] >= 0 and d[1] >= 0 for d in nb)
                    P[x, y] = mix(dark, INK, 0.35 if lit else 0.6) + (255,)
        return img


# ─── Materials ──────────────────────────────────────────────────────────────

def M(*cols, dith=0.0):
    return Mat(cols, dith)


# pells (ombra cap al vermell-violeta, llum cap al groc)
SKIN_IRI = M((64, 30, 42), (118, 62, 62), (170, 104, 86), (212, 146, 114), (236, 182, 146), (250, 214, 180))
SKIN_VET = M((40, 20, 30), (72, 38, 40), (108, 64, 50), (142, 92, 66), (174, 124, 86), (204, 160, 116))
SKIN_PALE = M((70, 36, 48), (124, 74, 72), (178, 122, 104), (216, 166, 138), (238, 200, 172), (252, 228, 204))
SKIN_OLD = M((62, 34, 44), (112, 70, 68), (162, 114, 96), (202, 156, 128), (226, 190, 160), (244, 220, 196))
SKIN_RUDDY = M((66, 26, 34), (120, 56, 52), (174, 96, 78), (214, 138, 108), (236, 174, 140), (250, 206, 176))

# roba
WHITE = M((46, 44, 66), (88, 90, 116), (138, 140, 162), (184, 186, 198), (220, 220, 220), (244, 242, 232), (255, 254, 246), dith=0.0)
SHIRT_BLUE = M((22, 28, 54), (38, 54, 92), (62, 88, 132), (94, 128, 170), (140, 172, 204))
TROUSER = M((14, 12, 20), (28, 24, 34), (46, 40, 50), (68, 60, 66), (94, 84, 84))
BOOT = M((12, 8, 12), (30, 18, 20), (54, 34, 30), (84, 56, 42), (124, 90, 64))
ORANGE = M((56, 16, 18), (104, 34, 22), (156, 60, 26), (206, 94, 36), (236, 134, 56), (252, 180, 104), dith=0.0)
ORANGE_FADED = M((58, 24, 26), (110, 44, 30), (164, 76, 40), (206, 110, 56), (228, 146, 86), (242, 184, 134), dith=0.0)
SNEAKER = M((40, 40, 58), (90, 92, 112), (150, 152, 166), (206, 206, 212), (240, 240, 240), (255, 255, 255))
GRAY_SHOE = M((20, 20, 28), (40, 40, 50), (64, 64, 74), (92, 92, 100), (124, 124, 128))
SUIT_D = M((14, 14, 24), (28, 30, 44), (44, 48, 66), (62, 68, 88), (84, 92, 114), (112, 120, 142), dith=0.0)
TRENCH = M((34, 30, 34), (62, 56, 56), (96, 88, 80), (130, 122, 108), (164, 156, 138), (196, 190, 170), dith=0.0)
FELT = M((16, 14, 18), (32, 30, 34), (52, 50, 54), (76, 74, 76), (104, 102, 100))
DENIM = M((14, 22, 38), (26, 42, 64), (42, 66, 94), (62, 96, 126), (90, 130, 158), (130, 170, 190), dith=0.0)
CREAM = M((70, 58, 62), (122, 110, 104), (172, 162, 146), (212, 204, 184), (236, 230, 210), (252, 248, 232))
NAVY_U = M((8, 10, 22), (16, 22, 42), (28, 38, 66), (42, 56, 92), (60, 78, 120), (88, 108, 150), dith=0.0)
BELT = M((10, 8, 12), (24, 20, 24), (40, 34, 36), (60, 52, 50))

# cabells
HAIR_IRI = M((10, 6, 12), (26, 14, 22), (44, 26, 32), (66, 40, 42), (96, 62, 56), (134, 98, 84))
HAIR_PLAT = M((64, 60, 84), (112, 108, 128), (162, 158, 166), (204, 198, 192), (232, 226, 210), (250, 248, 234))
HAIR_WHITE = M((60, 60, 80), (106, 106, 124), (156, 156, 170), (198, 198, 206), (228, 228, 232), (248, 248, 250))
HAIR_COPPER = M((40, 14, 14), (84, 32, 20), (134, 58, 30), (180, 90, 44), (212, 126, 64), (240, 172, 104))
HAIR_BROWN = M((20, 12, 14), (40, 26, 26), (62, 42, 38), (88, 62, 52), (118, 88, 72))

# detalls
BRASS = M((40, 24, 16), (84, 54, 22), (138, 96, 34), (190, 144, 54), (230, 192, 90), (252, 234, 160))
LENS = M((16, 40, 58), (34, 90, 120), (70, 160, 196), (150, 222, 240), (230, 252, 255))
RED = M((40, 8, 16), (86, 18, 24), (144, 34, 34), (196, 60, 48), (232, 104, 80))
GOLDPIN = M((70, 44, 14), (150, 108, 30), (226, 184, 70), (255, 238, 150))
STEELB = M((30, 34, 46), (70, 78, 92), (120, 130, 144), (176, 186, 196), (230, 236, 240))

EYE_W = (240, 236, 228)
LIP = (150, 66, 70)
MOUTH = (70, 18, 30)


# ─── Persones ───────────────────────────────────────────────────────────────
#
# Fotograma 49×87, peus a (25, 83). Cap a ~(24.5, 15); espatlles a y≈30; malucs a y≈56.

GROUND = 83
HIPY = 51
LEG = 14.5


def leg_pose(phase, amp=26):
    """Cama de perfil en el cicle: (angle de la cuixa, angle de la canyella) en graus (+ = endavant)."""
    a = amp * math.sin(phase)
    c = math.cos(phase)
    knee = 44 * max(0.0, c) ** 1.3 + 3
    return a, a - knee, c > 0


def leg_points(hip, a, s, th=LEG, sh=LEG):
    """Maluc → genoll → turmell, de perfil mirant a l'esquerra (endavant = −x)."""
    ra, rs = math.radians(a), math.radians(s)
    knee = (hip[0] - math.sin(ra) * th, hip[1] + math.cos(ra) * th)
    ankle = (knee[0] - math.sin(rs) * sh, knee[1] + math.cos(rs) * sh)
    return knee, ankle


class Pose:
    """Geometria d'un fotograma: articulacions segons la direcció i el pas."""

    def __init__(self, facing, walk=None, talk=False, thin=0, stoop=0, seated=None):
        self.f, self.walk, self.talk, self.thin = facing, walk, talk, thin
        self.q = None                                   # el 3/4: 'DL' (de cara, girat a l'esquerra) o 'UL' (d'esquena)
        self.bob = 0
        if seated is not None:
            self._seated(seated, stoop)
        elif facing == 'L':
            self._side(walk, stoop)
        elif facing in ('DL', 'UL'):
            self.q = facing
            self.f = 'D' if facing == 'DL' else 'U'     # es dibuixa amb la de cara (o d'esquena) i després es gira
            self._front(walk, stoop)
            self._diagonal(walk)
        else:
            self._front(walk, stoop)

    def _diagonal(self, walk):
        """La passa en diagonal: el peu que va endavant va cap a l'esquerra i cap avall (DL, cap a la càmera) o cap
        amunt (UL, cap al fons); els braços, al revés. Coordenades d'abans de girar la figura."""
        if walk is None:
            return
        ph = 2 * math.pi * walk / 6
        for i, sign in ((0, 1.0), (1, -1.0)):          # (les cames, ja les fa _front amb la passa en diagonal)
            fw = sign * math.sin(ph)                    # +1: aquesta cama, endavant del tot
            wx, wy = self.wrist[i]
            self.wrist[i] = (wx + fw * 2.4, wy)

    # Cap on va «endavant» a la pantalla, per píxel de passa: de cara, cap avall (cap a la càmera); d'esquena, cap
    # amunt; en 3/4, cap a l'esquerra i una mica avall o amunt. (La càmera és una mica picada: la profunditat es veu.)
    FWD = {'D': (0.0, 0.16), 'U': (0.0, -0.3), 'DL': (-0.5, 0.1), 'UL': (-0.5, -0.2)}   # (D: el peu no surt del fotograma)

    def _front(self, walk, stoop):
        t = self.thin
        lift = [0.0, 0.0]
        arm = [0.0, 0.0]
        legs = None
        if walk is not None:
            # la mateixa passa que de perfil (cuixa, genoll, canyella), vista de cara: la cama que avança s'acosta a
            # la càmera (baixa a la pantalla) i la que es recull s'aixeca; el maluc baixa quan les cames s'obren
            ph = 2 * math.pi * walk / 6
            legs = [leg_pose(ph), leg_pose(ph + math.pi)]
            ext = [LEG * math.cos(math.radians(a)) + LEG * math.cos(math.radians(sh)) for a, sh, _ in legs]
            hipy = GROUND - 3 - max(ext)
            self.bob = round(hipy - HIPY)
            s = math.sin(ph)
            arm = [-s * 2.4, s * 2.4]
        b = self.bob
        self.head = (24.5, 15.5 + b + stoop)
        self.sh = [(15.2 + t, 30 + b), (33.8 - t, 30 + b)]
        self.elbow = [(14.0 + t, 41 + b - arm[0] * 0.4), (35.0 - t, 41 + b - arm[1] * 0.4)]
        self.wrist = [(13.8 + t + abs(arm[0]) * 0.2, 50.5 + b - arm[0]), (35.2 - t - abs(arm[1]) * 0.2, 50.5 + b - arm[1])]
        self.hip = [(21 + t * 0.5, HIPY + b), (28 - t * 0.5, HIPY + b)]
        self.knee = [(21 + t * 0.5, 66 + b), (28 - t * 0.5, 66 + b)]
        self.ankle = [(21.5 + t * 0.5, 80), (27.5 - t * 0.5, 80)]
        if legs:
            fx, fy = self.FWD.get(self.q or self.f, (0.0, 0.16))
            for i, (a, sh, _) in enumerate(legs):
                ra, rs = math.radians(a), math.radians(sh)
                hx, hy = self.hip[i]
                fk = LEG * math.sin(ra)                    # quant avança el genoll (+: endavant)
                fa = fk + LEG * math.sin(rs)               # i el turmell
                ky = hy + LEG * math.cos(ra)
                ay = ky + LEG * math.cos(rs)
                kx0, ax0 = self.knee[i][0], self.ankle[i][0]
                self.knee[i] = (kx0 + fk * fx, ky + fk * fy)
                self.ankle[i] = (ax0 + fa * fx, min(ay + fa * fy, GROUND - 1.5))   # (que la sabata no surti del fotograma)
                lift[i] = max(0.0, (GROUND - 3) - ay)       # el peu, enlaire (per a la faldilla, p. ex.)
        self.lift = lift

    def _seated(self, hipy, stoop):
        """De perfil (mirant a l'esquerra), assegut en un tamboret alt: el maluc a `hipy`, les cuixes una mica
        cap avall, els peus al reposapeus i la mà del davant damunt el genoll."""
        hipx = 26.0
        self.f = 'L'
        self.bob = round(hipy - HIPY)
        b = self.bob
        self.hip_y = hipy
        self.legs = []
        for a, sh, dx in ((72, -6, 0.0), (68, -10, 1.5)):          # la cama del davant i la del darrere
            hip = (hipx + dx, hipy)
            k, an = leg_points(hip, a, sh)
            self.legs.append((hip, k, an, 0.0))
        self.head = (24.5, 15 + b + stoop)
        self.shoulder = (25.5, 30 + b)
        self.arms = []
        for a, bend in ((6, 60), (-4, 66)):                          # les mans, damunt les cuixes
            ra, rb = math.radians(a), math.radians(a + bend)
            sx, sy = self.shoulder
            el = (sx - math.sin(ra) * 10.5, sy + math.cos(ra) * 10.5)
            wr = (el[0] - math.sin(rb) * 9.5, el[1] + math.cos(rb) * 9.5)
            self.arms.append(((sx, sy), el, wr))

    def _side(self, walk, stoop):
        hipx = 25.5
        if walk is None:
            legs = [(2, -1, False), (-2, -3, False)]   # (cuixa, canyella): cama del davant i la del darrere
            ph = None
        else:
            ph = 2 * math.pi * walk / 6
            legs = [leg_pose(ph), leg_pose(ph + math.pi)]
        th = sh = LEG
        ext = [th * math.cos(math.radians(a)) + sh * math.cos(math.radians(s)) for a, s, _ in legs]
        hipy = GROUND - 3 - max(ext)
        self.bob = round(hipy - HIPY) if walk is not None else 0
        b = self.bob
        self.hip_y = hipy
        self.legs = []
        for a, s, swing in legs:
            k, an = leg_points((hipx, hipy), a, s, th, sh)
            # el peu: pla quan recolza; la punta cau quan la cama passa endavant
            pitch = 0.0
            if swing:
                pitch = -18 * max(0.0, math.cos(ph if ph is not None else 0))
            self.legs.append(((hipx, hipy), k, an, pitch))
        self.head = (24.5, 15 + b + stoop)
        self.shoulder = (25.5, 30 + b)
        # braços: oposats a les cames
        if walk is None:
            arms = [(3, 8), (-4, 6)]
        else:
            s = math.sin(ph)
            arms = [(-22 * s, 10 + 14 * max(0.0, -s)), (22 * s, 10 + 14 * max(0.0, s))]
        self.arms = []
        for a, bend in arms:
            ra, rb = math.radians(a), math.radians(a + bend)
            sx, sy = self.shoulder
            el = (sx - math.sin(ra) * 10.5, sy + math.cos(ra) * 10.5)
            wr = (el[0] - math.sin(rb) * 9.5, el[1] + math.cos(rb) * 9.5)
            self.arms.append(((sx, sy), el, wr))


# ─── Peces comunes ──────────────────────────────────────────────────────────

def shoe_front(fg, ank, mat, lvl=2.6):
    x, y = ank
    fg.ell(x, y + 1.6, 3.3, 2.3, mat, lvl, amp=1.8)
    fg.ell(x, y + 2.2, 3.6, 1.8, mat, lvl - 0.2, amp=1.6)


def shoe_side(fg, ank, pitch, mat, lvl=2.6, far=False):
    x, y = ank
    r = math.radians(pitch)
    c, s = math.cos(r), math.sin(r)

    def rot(dx, dy):
        return (x + dx * c - dy * s, y + dx * s + dy * c)

    pts = [rot(2.2, -1.2), rot(2.6, 2.6), rot(-5.6, 2.6), rot(-5.8, 1.2), rot(-3.5, -0.4), rot(-1.5, -1.6)]
    d = -0.9 if far else 0
    fg.poly(pts, mat, lvl + d, amp=1.2, cont=(0.3, 1.0),
            normal=lambda px, py: (0.0, -0.6 if py < y + 0.5 else 0.3, 0.8))


def front_face(fg, p, spec):
    """Ulls, celles, nas i boca de cara (cap centrat a p.head)."""
    hx, hy = p.head
    S = spec['skin']
    eye = spec.get('eye', (34, 22, 30))
    iris = spec.get('iris', (70, 50, 40))
    brow = spec.get('brow', (40, 24, 28))
    xl, xr = int(hx - 3.5), int(hx + 2.5)   # 21, 27
    ey = int(hy + 0.5)                      # 15
    if spec.get('closed'):
        for x0 in (xl, xr):
            fg.px(x0, ey, eye, 0); fg.px(x0 + 1, ey, eye, 0)
    else:
        # parpella (fosca) a dalt, a sota iris i blanc
        mira = spec.get('mira')                         # mira a un costat: l'iris, a aquella banda dels dos ulls
        for x0, inner in ((xl, xl + 1), (xr, xr)):
            if mira:
                inner = x0 if mira < 0 else x0 + 1
            fg.px(x0, ey - 1, eye, 0); fg.px(x0 + 1, ey - 1, eye, 0)
            fg.px(inner, ey, iris, 0)
            fg.px(x0 + (x0 + 1 - inner) if inner == x0 + 1 else x0 + 1, ey, EYE_W, 0)
        if spec.get('lashes'):
            fg.px(xl - 1, ey - 1, eye, 0); fg.px(xr + 2, ey - 1, eye, 0)
        if spec.get('liner'):
            liner = spec['liner']
            fg.px(xl - 1, ey, liner, 0); fg.px(xr + 2, ey, liner, 0)
            fg.px(xl, ey + 1, liner, 0); fg.px(xr + 1, ey + 1, liner, 0)
    # celles
    by = ey - 3 + spec.get('brow_dy', 0)
    fg.px(xl - 1, by + 1, brow, 0); fg.px(xl, by, brow, 0); fg.px(xl + 1, by, brow, 0)
    fg.px(xr, by, brow, 0); fg.px(xr + 1, by, brow, 0); fg.px(xr + 2, by + 1, brow, 0)
    # nas: llum a l'esquerra, ombra a la dreta i a sota
    nx = int(hx)
    fg.shade(nx, ey + 2, -0.9, S); fg.shade(nx, ey + 3, -1.1, S); fg.shade(nx - 1, ey + 3, -0.5, S)
    fg.shade(nx - 1, ey + 1, +0.5, S); fg.shade(nx - 1, ey + 2, +0.6, S)
    # galtes
    if spec.get('blush'):
        fg.shade(xl - 1, ey + 2, -0.4, S); fg.shade(xr + 2, ey + 2, -0.6, S)
    # boca
    my = ey + 5
    lip = spec.get('lip', LIP)
    if p.talk:
        fg.px(nx - 1, my, MOUTH, 0); fg.px(nx, my, MOUTH, 0); fg.px(nx + 1, my, MOUTH, 0)
        fg.px(nx, my + 1, MOUTH, 0); fg.px(nx - 1, my + 1, lip, 0); fg.px(nx + 1, my + 1, lip, 0)
    else:
        fg.px(nx - 1, my, lip, 0); fg.px(nx, my, mix(lip, MOUTH, 0.5), 0); fg.px(nx + 1, my, lip, 0)
        fg.shade(nx, my + 1, +0.4, S)


def side_face(fg, p, spec):
    """Perfil mirant a l'esquerra: ull, cella, nas que surt, boca."""
    hx, hy = p.head
    S = spec['skin']
    eye = spec.get('eye', (34, 22, 30))
    iris = spec.get('iris', (70, 50, 40))
    brow = spec.get('brow', (40, 24, 28))
    ex, ey = int(hx - 3.5), int(hy + 0.5)   # 21, 15
    if spec.get('closed'):
        fg.px(ex, ey, eye, 0); fg.px(ex + 1, ey, eye, 0)
    else:
        fg.px(ex, ey - 1, eye, 0); fg.px(ex + 1, ey - 1, eye, 0)
        fg.px(ex, ey, iris, 0); fg.px(ex - 1, ey, EYE_W, 0)
        if spec.get('lashes'):
            fg.px(ex + 2, ey - 1, eye, 0)
        if spec.get('liner'):
            fg.px(ex + 2, ey, spec['liner'], 0); fg.px(ex, ey + 1, spec['liner'], 0)
    by = ey - 3 + spec.get('brow_dy', 0)
    fg.px(ex - 1, by, brow, 0); fg.px(ex, by, brow, 0); fg.px(ex + 1, by + 1, brow, 0)
    # orella
    ox_ = int(hx + 2.5)
    fg.ell(ox_ + 0.5, ey + 2, 1.6, 2.2, S, 2.6, amp=1.2)
    fg.shade(ox_ + 0.5, ey + 2, -1.2, S)
    if spec.get('blush'):
        fg.shade(ex + 1, ey + 2, -0.4, S)
    # boca
    my = ey + 5
    lip = spec.get('lip', LIP)
    mx = int(hx - 5.5)
    if p.talk:
        fg.px(mx, my, MOUTH, 0); fg.px(mx + 1, my, MOUTH, 0); fg.px(mx + 1, my + 1, MOUTH, 0)
        fg.erase(mx - 1, my)
    else:
        fg.px(mx, my, lip, 0); fg.px(mx + 1, my, mix(lip, MOUTH, 0.5), 0)


def head_front(fg, p, S, lvl=3.1):
    hx, hy = p.head
    # orelles (en 3/4, la de l'esquerra queda amagada: el cap es gira cap a aquell costat)
    if not getattr(p, 'q', None):
        fg.ell(hx - 6.6, hy + 2, 1.4, 2.0, S, lvl - 0.2, amp=1.2)
    fg.ell(hx + 6.6, hy + 2, 1.4, 2.0, S, lvl - 0.6, amp=1.2)
    fg.ell(hx, hy, 6.5, 7.6, S, lvl, amp=1.5)
    fg.ell(hx, hy + 3.6, 5.6, 5.0, S, lvl, amp=1.5)


def head_side(fg, p, S, lvl=3.1):
    hx, hy = p.head
    fg.ell(hx + 0.8, hy, 6.8, 7.6, S, lvl, amp=1.5)
    fg.ell(hx - 1.6, hy + 3.4, 4.8, 4.8, S, lvl, amp=1.4)
    # nas
    fg.poly([(hx - 6.2, hy + 1), (hx - 8.0, hy + 3.6), (hx - 6.0, hy + 4.2)], S, lvl + 0.3)
    fg.px(hx - 6.5, hy + 4, S, lvl - 1.2)
    # barbeta
    fg.ell(hx - 4.6, hy + 6.4, 1.6, 1.4, S, lvl, amp=1.2)


def head_back(fg, p, S, lvl=3.1):
    hx, hy = p.head
    if not getattr(p, 'q', None):
        fg.ell(hx - 6.6, hy + 2, 1.4, 2.0, S, lvl - 0.2, amp=1.2)
    fg.ell(hx + 6.6, hy + 2, 1.4, 2.0, S, lvl - 0.6, amp=1.2)
    fg.ell(hx, hy, 6.5, 7.6, S, lvl, amp=1.5)
    fg.ell(hx, hy + 3.6, 5.6, 5.0, S, lvl, amp=1.5)


def neck(fg, p, S):
    hx, hy = p.head
    if p.f == 'L':
        fg.limb((hx + 0.4, hy + 5), (hx + 1.4, hy + 12), 2.6, 2.9, S, 2.0, amp=1.2)
    else:
        fg.limb((hx, hy + 5), (hx, hy + 12), 2.6, 3.0, S, 2.0 if p.f == 'D' else 2.4, amp=1.2)


def torso_edges(p, top=27, chest=9.6, waist=7.2, hip=8.8):
    """Silueta del tronc de cara: mitja amplada per fila (espatlles arrodonides, cintura, malucs)."""
    b = p.bob
    cx = 24.5
    sh = [3.4, 1.5, 0.5]

    def e(y):
        yy = y - b
        if yy < top:
            return None
        k = yy - top
        if k < 3:
            w = chest - sh[k]
        elif yy < 36:
            w = chest
        elif yy < 43:
            w = chest + (waist - chest) * (yy - 36) / 7
        elif yy < 46:
            w = waist
        else:
            w = waist + (hip - waist) * min(1, (yy - 46) / 4)
        w -= p.thin
        return (cx - w, cx + w)
    return e


def side_torso_edges(p, top=27):
    """De perfil: pit endavant, l'esquena una mica corbada, malucs."""
    b = p.bob
    t = p.thin * 0.5
    rows = {0: (22.5, 29.5), 1: (21.0, 30.6), 2: (20.2, 31.0)}

    def e(y):
        yy = y - b
        k = yy - top
        if k < 0:
            return None
        if k in rows:
            l, r = rows[k]
        elif yy < 38:
            l, r = 19.6, 31.2
        elif yy < 45:
            f = (yy - 38) / 7
            l, r = 19.6 + f * 1.2, 31.2 - f * 0.8
        else:
            f = min(1, (yy - 45) / 5)
            l, r = 20.8 - f * 0.4, 30.4 + f * 1.4
        return (l + t, r - t)
    return e


# ─── Una persona ────────────────────────────────────────────────────────────

def person(spec, facing, walk=None, talk=False):
    """Persona de 49×87 (peus a (25, 83)). `spec`: materials i ganxos de cada personatge."""
    fg = Fig(49, 87)
    p = Pose(facing, walk, talk, thin=spec.get('thin', 0), stoop=spec.get('stoop', 0), seated=spec.get('seated'))
    p.spec = spec
    if 'pose' in spec:
        spec['pose'](p)          # una postura pròpia (p. ex. el mòbil a la mà): canvia les articulacions
    S = spec['skin']
    if p.f == 'L':
        _person_side(fg, p, spec, S)
    elif p.q:
        _person_front(fg, p, spec, S, cara=False)
        _gira(fg, p, spec, S)
    else:
        _person_front(fg, p, spec, S)
    return fg.render()


# El 3/4: la figura de cara (o d'esquena), estreta i desplaçada cap on mira (el cap, menys que el cos: és rodó), amb
# el costat dret a l'ombra (és el que es gira cap a la càmera), el nas a la silueta i la cara desplaçada dins el cap.
Q_COS, Q_CAP = 0.78, 0.90                       # amplada que queda del cos i del cap
Q_DX_COS, Q_DX_CAP, Q_DX_CARA = -1.0, -1.6, -1.8  # desplaçaments (px de disseny) de la superfície que es veu
# (DL: la cara i el pit miren a l'esquerra, i s'hi desplacen; UL: d'esquena, el centre de l'esquena —la trena, el
# pegat— es desplaça cap a la dreta, perquè l'esquena gira cap a l'altre costat)


def _q_dx(yd, q='DL'):
    """(factor, desplaçament) a la fila de disseny yd: el cap fins al coll, el cos a partir de les espatlles."""
    t = max(0.0, min(1.0, (yd - 22) / 6))
    sign = 1.0 if q == 'DL' else -0.8
    return Q_CAP + (Q_COS - Q_CAP) * t, sign * (Q_DX_CAP + (Q_DX_COS - Q_DX_CAP) * t)


def _gira(fg, p, spec, S):
    sc = fg.w / 49                                  # píxels del buffer per píxel de disseny (×1, ×1,2, 2×...)
    cx = 24.5 * sc + (sc - 1) / 2
    old = [row[:] for row in fg.buf]
    b = p.bob
    for Y in range(fg.h):
        yd = (Y - (sc - 1) / 2) / sc - b
        k, dx = _q_dx(yd, p.q)
        row = old[Y]
        for X in range(fg.w):
            xs = cx + (X - cx - dx * sc) / k
            i = int(round(xs))
            fg.buf[Y][X] = row[i] if 0 <= i < fg.w else None
    # el costat que es gira cap a la càmera (la dreta de la pantalla), a l'ombra: tronc, braç i cames
    side = max(1, round(1.6 * sc))
    for Y in range(fg.h):
        yd = (Y - (sc - 1) / 2) / sc - b
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
    # la cara, desplaçada dins el cap (es dibuixa després de girar: així no perd cap píxel)
    hx, hy = p.head
    k, dx = _q_dx(hy, p.q)
    p.head = (24.5 + (hx - 24.5) * k + dx + Q_DX_CARA, hy)
    front_face(fg, p, spec)
    # el nas a la silueta: un píxel de pell a l'esquerra de la galta, a l'alçada del nas
    for yd in (hy + 2.0, hy + 3.0):
        Y = int(round((yd + b) * sc + (sc - 1) / 2))
        if not 0 <= Y < fg.h:
            continue
        row = fg.buf[Y]
        xl = next((X for X in range(fg.w) if row[X] and row[X][0] is S), None)
        if xl is not None:
            for d in range(1, max(1, round(sc)) + 1):
                if xl - d >= 0:
                    row[xl - d] = (S, row[xl][1] + 0.4)
    p.head = (hx, hy)


def _person_front(fg, p, spec, S, cara=True):
    back = p.f == 'U'
    legs, top, shoes = spec['legs'], spec['top'], spec['shoes']
    sleeve = spec.get('sleeve', top)
    hk = spec.get('hooks', {})
    if 'hair_back' in hk:
        hk['hair_back'](fg, p, spec)
    # cames
    for i in (0, 1):
        dl = -0.2 if i == 0 else -0.5
        fg.limb(p.hip[i], p.knee[i], 3.6 - p.thin * 0.4, 3.1 - p.thin * 0.3, legs, 2.6 + dl, cont=(0, 0.4))
        fg.limb(p.knee[i], p.ankle[i], 3.1 - p.thin * 0.3, 2.6 - p.thin * 0.2, legs, 2.5 + dl, cont=(0, 0.4))
        if 'leg_deco' in hk:
            hk['leg_deco'](fg, p, spec, i)
        shoe_front(fg, p.ankle[i], shoes, spec.get('shoe_lvl', 2.6) + dl)
    # tronc
    fg.lathe(27 + p.bob, HIPY + 3 + p.bob, torso_edges(p), top, 2.8, amp=1.6)
    for y in range(HIPY + 1, HIPY + 4):
        fg.shade(24.5 - 0.5, y + p.bob, -1.2, legs)
        fg.shade(24.5 + 0.5, y + p.bob, -0.8, legs)
    if 'torso' in hk:
        hk['torso'](fg, p, spec)
    # braços (amb la mà)
    for i in (0, 1):
        dl = 0.0 if i == 0 else -0.5
        fg.limb(p.sh[i], p.elbow[i], 3.0, 2.7, sleeve, 2.7 + dl, cont=(0.3, 1.0))
        fg.limb(p.elbow[i], p.wrist[i], 2.7, 2.4, spec.get('forearm', sleeve), 2.6 + dl, cont=(0.3, 1.0))
        wx, wy = p.wrist[i]
        fg.ell(wx, wy + 2.2, 2.1, 2.5, S, 2.6 + dl, amp=1.4)
        if 'arm' in hk:
            hk['arm'](fg, p, spec, i)
    if 'over' in hk:
        hk['over'](fg, p, spec)
    # cap
    neck(fg, p, S)
    if 'collar' in hk:
        hk['collar'](fg, p, spec)
    if back:
        head_back(fg, p, S)
    else:
        head_front(fg, p, S)
        if cara:
            hx, hy = p.head
            if spec.get('mira'):                         # mira a un costat: la cara també hi gira una mica
                p.head = (hx + spec['mira'] * 1.0, hy)
            front_face(fg, p, spec)
            p.head = (hx, hy)
    if 'hair' in hk:
        hk['hair'](fg, p, spec)


def _person_side(fg, p, spec, S):
    legs, top, shoes = spec['legs'], spec['top'], spec['shoes']
    sleeve = spec.get('sleeve', top)
    hk = spec.get('hooks', {})
    (hipA, kA, aA, pA), (hipB, kB, aB, pB) = p.legs
    # ordre: la cama "del darrere" (B) primer, més fosca
    near, far = p.legs[0], p.legs[1]
    if 'hair_back' in hk:
        hk['hair_back'](fg, p, spec)
    # braç del fons
    s, e, w = p.arms[1]
    fg.limb(s, e, 2.9, 2.6, sleeve, 1.8, cont=(0.3, 1.0))
    fg.limb(e, w, 2.6, 2.3, spec.get('forearm', sleeve), 1.7, cont=(0.3, 1.0))
    fg.ell(w[0] - 0.4, w[1] + 2.2, 2.0, 2.4, S, 1.8, amp=1.3)
    for leg, dl in ((far, -0.9), (near, 0.0)):
        h, k, a, pitch = leg
        fg.limb(h, k, 3.7 - p.thin * 0.4, 3.1 - p.thin * 0.3, legs, 2.6 + dl, cont=(0.2, 0.7))
        fg.limb(k, a, 3.1 - p.thin * 0.3, 2.5 - p.thin * 0.2, legs, 2.5 + dl, cont=(0.2, 0.7))
        if 'leg_deco_side' in hk:
            hk['leg_deco_side'](fg, p, spec, leg, dl)
        shoe_side(fg, a, pitch, shoes, spec.get('shoe_lvl', 2.6), far=dl < 0)
    # tronc
    fg.lathe(27 + p.bob, round(p.hip_y) + 3, side_torso_edges(p), top, 2.8, amp=1.6)
    if 'torso' in hk:
        hk['torso'](fg, p, spec)
    neck(fg, p, S)
    if 'collar' in hk:
        hk['collar'](fg, p, spec)
    # braç del davant
    s, e, w = p.arms[0]
    fg.limb(s, e, 3.0, 2.7, sleeve, 2.8, cont=(0.4, 1.2))
    fg.limb(e, w, 2.7, 2.4, spec.get('forearm', sleeve), 2.7, cont=(0.4, 1.2))
    fg.ell(w[0] - 0.4, w[1] + 2.2, 2.1, 2.5, S, 2.7, amp=1.4)
    if 'arm' in hk:
        hk['arm'](fg, p, spec, 0)
    if 'over' in hk:
        hk['over'](fg, p, spec)
    head_side(fg, p, S)
    side_face(fg, p, spec)
    if 'hair' in hk:
        hk['hair'](fg, p, spec)


# ─── Cabells i roba: ajudes ─────────────────────────────────────────────────

def hair_lvl(cx, cy, r_shine=5.5, k=1.3, strands=0.35, freq=1.7):
    """Textura de cabell: brins (ones suaus) i una banda de lluentor a dalt a l'esquerra."""
    def f(x, y):
        v = strands * math.sin(x * freq + y * 0.45)
        d = math.hypot(x - cx, (y - cy) * 1.1)
        ang = math.atan2(y - cy, x - cx)
        if abs(d - r_shine) < 1.0 and -2.6 < ang < -0.9:
            v += k
        return v
    return f


def front_normal(cx, half):
    def n(x, y):
        u = max(-1.0, min(1.0, (x - cx) / half))
        return (u, 0.0, math.sqrt(1 - u * u))
    return n


def fold(x, y, xs, lo, hi, d=-0.9):
    """Plecs verticals: línies fosques a les x de `xs` (amb llum al costat esquerre)."""
    if not lo <= y <= hi:
        return 0.0
    for fx in xs:
        if x == fx:
            return d
        if x == fx - 1:
            return 0.5
    return 0.0


# Els personatges de Suma Zero (especificacions com a dict per a `person`) van a partir d'aquí.
