"""
Personatges de Ferro-9 en pixel art HD: es dibuixen a la mida real del fotograma (49×87 una persona),
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
# la Vet: més clara que la fosca d'abans, a mig camí de la de l'Iri (2026-11-20)
SKIN_VET = M((52, 25, 36), (95, 50, 51), (139, 84, 68), (177, 119, 90), (205, 153, 116), (227, 187, 148))
# la fosca d'abans de la Vet, que continuen fent servir els secundaris
SKIN_FOSCA = M((40, 20, 30), (72, 38, 40), (108, 64, 50), (142, 92, 66), (174, 124, 86), (204, 160, 116))
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

    def __init__(self, facing, walk=None, talk=False, thin=0, stoop=0):
        self.f, self.walk, self.talk, self.thin = facing, walk, talk, thin
        self.q = None                                   # el 3/4: 'DL' (de cara, girat a l'esquerra) o 'UL' (d'esquena)
        self.bob = 0
        if facing == 'L':
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
        amunt (UL, cap al fons); els braços, al revés. Coordenades d'abans de girar la figura. Quiet en DL, el peu de
        darrere (l'esquerre) queda una mica més amunt (més lluny, amb la càmera picada) i el braç de darrere, una mica
        darrere el cos."""
        if walk is None:
            if self.q == 'DL':
                ax, ay = self.ankle[0]
                kx, ky = self.knee[0]
                wx, wy = self.wrist[0]
                self.ankle[0] = (ax + 0.3, ay - Q_PEU_DARRERE)
                self.knee[0] = (kx + 0.15, ky - Q_PEU_DARRERE * 0.5)
                self.wrist[0] = (wx + 0.8, wy)
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
        for x0, inner in ((xl, xl + 1), (xr, xr)):
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
    p = Pose(facing, walk, talk, thin=spec.get('thin', 0), stoop=spec.get('stoop', 0))
    p.spec = spec
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
# De cara (DL), el gir és asimètric: el costat de darrere (l'esquerra de la pantalla) s'encongeix molt més que el del
# davant, i així el mig del pit (la cremallera, l'estampat) es desplaça cap on mira; el braç i la cama de darrere, més
# foscos, i el peu de darrere una mica més amunt. Amb un sol factor, el DL semblava la figura de cara feta més prima.
Q_COS, Q_CAP = 0.78, 0.90                       # amplada que queda del cos i del cap (UL, d'esquena)
QL_COS, QR_COS, QL_CAP, QR_CAP = 0.60, 0.95, 0.86, 0.97   # DL: el costat de darrere (L) i el del davant (R)
Q_DX_COS, Q_DX_CAP, Q_DX_CARA = -1.0, -1.6, -2.0  # desplaçaments (px de disseny) de la superfície que es veu
Q_FOSC_DARRERE = 0.6                            # quant s'enfosqueix el costat de darrere (DL), en nivells de llum
Q_PEU_DARRERE = 1.0                             # quant puja el peu de darrere (DL, quiet), en px de disseny
# (DL: la cara i el pit miren a l'esquerra, i s'hi desplacen; UL: d'esquena, el centre de l'esquena —la trena, el
# pegat— es desplaça cap a la dreta, perquè l'esquena gira cap a l'altre costat)


def _q_dx(yd, q='DL', u=0.0):
    """(factor, desplaçament) a la fila de disseny yd: el cap fins al coll, el cos a partir de les espatlles. `u`: a
    quin costat del centre és el píxel (només el signe, que és el mateix abans i després de girar): en DL, el de
    l'esquerra s'encongeix més (QL_COS). Un píxel x de la figura de cara va, en 3/4, a cx + (x - cx)·k + dx."""
    t = max(0.0, min(1.0, (yd - 22) / 6))
    sign = 1.0 if q == 'DL' else -0.8
    if q == 'DL':
        k = QL_CAP + (QL_COS - QL_CAP) * t if u < 0 else QR_CAP + (QR_COS - QR_CAP) * t
    else:
        k = Q_CAP + (Q_COS - Q_CAP) * t
    return k, sign * (Q_DX_CAP + (Q_DX_COS - Q_DX_CAP) * t)


def _q_fosc_darrere(row, gruix):
    """DL: el costat de darrere (els primers `gruix` píxels per l'esquerra d'una fila del cos), un to més fosc."""
    xl = next((X for X in range(len(row)) if row[X]), None)
    if xl is None:
        return
    for X in range(xl, min(len(row), xl + gruix)):
        if row[X]:
            m, l = row[X]
            row[X] = (m, l - Q_FOSC_DARRERE)


def _gira(fg, p, spec, S):
    sc = fg.w / 49                                  # píxels del buffer per píxel de disseny (×1, ×1,2, 2×...)
    cx = 24.5 * sc + (sc - 1) / 2
    old = [row[:] for row in fg.buf]
    b = p.bob
    for Y in range(fg.h):
        yd = (Y - (sc - 1) / 2) / sc - b
        _, dx = _q_dx(yd, p.q)
        row = old[Y]
        for X in range(fg.w):
            v = X - cx - dx * sc
            xs = cx + v / _q_dx(yd, p.q, v)[0]
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
    # el costat de darrere (l'esquerra), més fosc: el braç i la cama que queden més lluny
    for Y in range(fg.h):
        if (Y - (sc - 1) / 2) / sc - b >= 28:
            _q_fosc_darrere(fg.buf[Y], max(1, round(2.2 * sc)))
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


# ─── Iri ────────────────────────────────────────────────────────────────────

def iri_braid(fg, p, pts, mat=HAIR_IRI):
    """Trena: segments alternats al llarg d'una corba, amb un llaç vermell."""
    n = len(pts)
    for i, (x, y) in enumerate(pts[:-1]):
        side = -0.6 if i % 2 else 0.6
        fg.ell(x + side, y, 2.0, 1.7, mat, 2.4, amp=1.8, cont=(0.2, 1.4))
    x, y = pts[-1]
    fg.ell(x, y - 0.5, 1.7, 1.0, RED, 2.6, amp=1.2)
    fg.poly([(x - 1.2, y + 0.5), (x + 1.4, y + 0.5), (x + 1.8, y + 3.6), (x - 1.6, y + 3.2)], mat, 2.0, amp=0.0,
            lvlfn=lambda xx, yy: 0.6 * math.sin(xx * 2.1))


def iri_hair(fg, p, spec):
    hx, hy = p.head
    H = HAIR_IRI
    if p.f == 'D':
        line = lambda x, y: y <= hy - 3.6 + ((x - hx) / 6.4) ** 2 * 6.5
        fg.ell(hx, hy - 1.0, 7.3, 7.6, H, 2.6, amp=1.6, clip=line, lvlfn=hair_lvl(hx - 0.5, hy - 1.5, 5.6))
        fg.line(hx - 0.5, hy - 8, hx - 0.5, hy - 4.5, H, 0.6)                   # ratlla al mig
        # ulleres al front
        fg.limb((hx - 7.2, hy - 4.6), (hx + 7.2, hy - 4.6), 0.8, 0.8, BRASS, 2.2, amp=1.0)
        for gx in (hx - 3.0, hx + 3.0):
            fg.ell(gx, hy - 5.4, 2.4, 2.2, BRASS, 2.6, amp=1.6)
            fg.ell(gx, hy - 5.4, 1.5, 1.3, LENS, 2.4, amp=1.8)
            fg.px(gx - 0.6, hy - 6.2, LENS, 4.5)
    elif p.f == 'L':
        line = lambda x, y: (x >= hx - 4.5 + max(0, y - (hy - 6)) * 0.2 or y <= hy - 5.5) and not (x < hx + 2 and y > hy - 2.5)
        fg.ell(hx + 1.2, hy - 0.8, 7.2, 7.8, H, 2.6, amp=1.6, clip=line, lvlfn=hair_lvl(hx, hy - 1.5, 5.8))
        fg.limb((hx - 5.5, hy - 5.2), (hx + 7.6, hy - 3.4), 0.8, 0.8, BRASS, 2.2, amp=1.0)
        fg.ell(hx - 4.4, hy - 5.8, 1.6, 2.4, BRASS, 2.6, amp=1.6)
        fg.ell(hx - 4.8, hy - 5.8, 0.9, 1.5, LENS, 2.6, amp=1.8)
        fg.ell(hx + 6.4, hy + 3.4, 2.4, 2.4, H, 2.2, amp=1.6)                       # nus de la trena
    else:
        fg.ell(hx, hy - 0.4, 7.3, 8.0, H, 2.6, amp=1.6, lvlfn=hair_lvl(hx - 0.5, hy - 1.5, 5.6))
        fg.limb((hx - 7.3, hy - 4.2), (hx + 7.3, hy - 4.2), 0.9, 0.9, BRASS, 2.0, amp=1.0)
        for x in range(int(hx - 4), int(hx + 5), 2):                              # el pentinat tirat enrere
            fg.shade(x, hy + 2, -0.7, H); fg.shade(x + 1, hy + 4, -0.7, H)
        iri_braid(fg, p, [(hx + 0.2, hy + 5.5 + i * 2.6) for i in range(10)])


def iri_coat(fg, p, spec):
    """Bata blanca oberta (a sota hi ha la camisa blava, que fa de tronc)."""
    W_ = WHITE
    b = p.bob
    hx = 24.5
    HEM = 70
    if p.f == 'D':
        n = front_normal(hx, 12.5)
        fl = lambda x, y: fold(x, y, (17, 32), 55 + b, HEM + b) + fold(x, y, (20,), 59 + b, HEM + b, -0.6)
        fg.poly([(hx - 8.8, 27 + b), (hx - 3.5, 27 + b), (hx - 2.2, 38 + b), (hx - 2.0, HEM + b), (hx - 12.0, HEM + b), (hx - 10.0, 45 + b)],
                W_, 3.2, amp=1.6, normal=n, cont=(0.2, 0.8), lvlfn=fl)
        fg.poly([(hx + 3.5, 27 + b), (hx + 8.8, 27 + b), (hx + 10.0, 45 + b), (hx + 12.0, HEM + b), (hx + 2.0, HEM + b), (hx + 2.2, 38 + b)],
                W_, 3.0, amp=1.6, normal=n, cont=(0.2, 0.8), lvlfn=fl)
        # solapes
        fg.poly([(hx - 5.5, 27 + b), (hx - 3.2, 27 + b), (hx - 2.2, 38 + b), (hx - 4.8, 32 + b)], W_, 4.4)
        fg.poly([(hx + 3.2, 27 + b), (hx + 5.5, 27 + b), (hx + 4.8, 32 + b), (hx + 2.2, 38 + b)], W_, 2.6)
        fg.line(hx - 4.8, 32 + b, hx - 2.4, 38 + b, W_, 2.0)
        fg.line(hx + 4.8, 32 + b, hx + 2.4, 38 + b, W_, 1.6)
        # ombra de l'obertura (sobre la camisa i els pantalons)
        for y in range(28 + b, HEM + 1 + b):
            fg.shade(hx - 1, y, -0.8, (SHIRT_BLUE, TROUSER))
            fg.shade(hx + 1, y, -1.0, (SHIRT_BLUE, TROUSER))
        # butxaca del pit amb llapis, butxaques de baix i la clau
        for x in range(int(hx + 4), int(hx + 9)):
            fg.shade(x, 35 + b, -1.1, W_)
        fg.px(hx + 5, 32 + b, RED, 3); fg.px(hx + 5, 33 + b, RED, 2); fg.px(hx + 5, 34 + b, RED, 1)
        fg.px(hx + 7, 33 + b, SHIRT_BLUE, 3); fg.px(hx + 7, 34 + b, SHIRT_BLUE, 2)
        for x in list(range(int(hx - 10), int(hx - 4))) + list(range(int(hx + 5), int(hx + 11))):
            fg.shade(x, 53 + b, -1.2, W_)
        fg.px(hx - 8, 52 + b, STEELB, 4); fg.px(hx - 8, 51 + b, STEELB, 3); fg.px(hx - 7, 51 + b, STEELB, 2)
        # cinturó dels pantalons a l'obertura
        for x in range(int(hx - 1), int(hx + 2)):
            fg.px(x, 46 + b, BELT, 1); fg.px(x, 47 + b, BELT, 2)
    elif p.f == 'U':
        n = front_normal(hx, 12.5)
        fl = lambda x, y: fold(x, y, (16, 20, 29, 33), 50 + b, HEM + b) + (-1.4 if x == 24 and y > 54 + b else 0)
        fg.poly([(hx - 8.8, 27 + b), (hx + 8.8, 27 + b), (hx + 10.0, 45 + b), (hx + 12.0, HEM + b), (hx - 12.0, HEM + b), (hx - 10.0, 45 + b)],
                W_, 3.0, amp=1.6, normal=n, cont=(0.2, 0.8), lvlfn=fl)
        fg.ell(hx, 28.5 + b, 5.0, 2.0, W_, 3.4, amp=1.0)                            # coll
        for x in range(int(hx - 6), int(hx + 7)):                                   # trabeta
            fg.shade(x, 44 + b, -1.0, W_)
            fg.shade(x, 45 + b, 0.5, W_)
    else:
        (_, kA, _, _), (_, kB, _, _) = p.legs
        front = min(19.8, min(kA[0], kB[0]) - 1.5)
        back = max(31.5, max(kA[0], kB[0]) + 4.5)
        hy = HEM + b
        n = front_normal(25.5, 7.5)
        fl = lambda x, y: fold(x, y, (int(front + 3), int(back - 3)), 55 + b, hy)
        fg.poly([(21.0, 27 + b), (30.0, 27 + b), (31.8, 42 + b), (back, hy), (front, hy), (19.4, 44 + b), (19.4, 33 + b)],
                W_, 3.1, amp=1.6, normal=n, cont=(0.3, 0.9), lvlfn=fl)
        fg.poly([(20.4, 27 + b), (22.6, 27 + b), (21.0, 37 + b), (19.4, 35 + b)], W_, 4.2)     # solapa
        for y in range(int(44 + b), int(hy)):                                         # vora de davant
            fg.shade(int(front + (19.4 - front) * (hy - y) / (hy - 44 - b)) + 1, y, -0.8, W_)
        for x in range(23, 29):
            fg.shade(x, 52 + b, -1.2, W_)


def iri_braid_hook(fg, p, spec):
    hx, hy = p.head
    if p.f == 'D':
        pts = [(hx + 5.6, hy + 4.5 + i * 2.6) for i in range(10)]
        pts = [(x + min(2.5, i * 0.5), y) for i, (x, y) in enumerate(pts)]
        iri_braid(fg, p, pts)
    elif p.f == 'L':
        sway = 0.0 if p.walk is None else math.sin(2 * math.pi * p.walk / 6) * 0.8
        pts = [(hx + 7.2 + i * 0.25 + sway * i / 8, hy + 5 + i * 2.6) for i in range(9)]
        iri_braid(fg, p, pts)
    # d'esquena, la trena es dibuixa amb el cabell (per sobre del clatell)


def iri_sleeve_cuff(fg, p, spec, i):
    if p.f == 'L':
        s, e, w = p.arms[0]
    else:
        e, w = p.elbow[i], p.wrist[i]
    fg.limb((w[0] + (e[0] - w[0]) * 0.18, w[1] + (e[1] - w[1]) * 0.18), w, 2.9, 2.9, WHITE, 2.4, amp=1.2, cont=(0.3, 1.2))


IRI = {
    'skin': SKIN_IRI, 'legs': TROUSER, 'top': SHIRT_BLUE, 'sleeve': WHITE, 'shoes': BOOT, 'lashes': True,
    'iris': (52, 38, 30), 'brow': (24, 16, 22),   # la cara de l'Iri, la mateixa a tots els jocs
    'hooks': {'hair': iri_hair, 'torso': iri_coat, 'over': iri_braid_hook, 'arm': iri_sleeve_cuff},
}


# ─── Vet ────────────────────────────────────────────────────────────────────

def vet_hair_back(fg, p, spec):
    hx, hy = p.head
    if p.f == 'D':
        fg.poly([(hx - 7.6, hy + 1), (hx + 7.6, hy + 1), (hx + 7.8, hy + 7.6), (hx - 7.8, hy + 7.6)], HAIR_PLAT, 1.2,
                lvlfn=lambda x, y: 0.5 * math.sin(x * 2.2))


def bob_lvl(hx, hy):
    """Brins verticals, lluentor en arc i puntes més fosques."""
    sh = hair_lvl(hx - 1.5, hy - 2.5, 5.2, k=1.3, strands=0.0)

    def f(x, y):
        v = sh(x, y)
        if y > hy - 2:
            v += 0.45 * math.sin(x * 2.3 + (y > hy + 4) * 1.5)
        if y >= hy + 6.5:
            v -= 0.6
        return v
    return f


def vet_hair(fg, p, spec):
    hx, hy = p.head
    H = HAIR_PLAT
    tex = bob_lvl(hx, hy)
    bot = hy + 7.5
    if p.f == 'D':
        def clip(x, y):
            if y > bot or (y > bot - 1 and int(x) % 3 == 0):
                return False
            face = abs(x - hx) < 5.4 - max(0, y - (hy + 3)) * 0.3 and y >= hy - 3.5
            return not face
        fg.ell(hx, hy + 2.2, 8.2, 10.6, H, 2.8, amp=1.5, clip=clip, lvlfn=tex, cont=(0, 0.7))
        for x in range(int(hx - 4), int(hx + 5)):                                 # serrell recte (ombra a sota)
            fg.shade(x, hy - 3.5, -0.9, H)
            fg.shade(x, hy - 3.0, -0.6, spec['skin'])
    elif p.f == 'L':
        def clip(x, y):
            if y > bot or (y > bot - 1 and int(x) % 3 == 0):
                return False
            if y >= hy - 3.5 and x < hx + 0.5 - max(0, y - (hy + 3)) * 0.3:
                return False
            return x >= hx - 7.0
        fg.ell(hx + 1.6, hy + 2.2, 8.0, 10.6, H, 2.8, amp=1.5, clip=clip, lvlfn=tex, cont=(0, 0.7))
        for x in range(int(hx - 6), int(hx + 1)):
            fg.shade(x, hy - 3.5, -0.9, H)
    else:
        fg.ell(hx, hy + 2.2, 8.2, 10.6, H, 2.8, amp=1.5, clip=lambda x, y: y <= bot and not (y > bot - 1 and int(x) % 3 == 0),
               lvlfn=tex, cont=(0, 0.7))


def vet_suit(fg, p, spec):
    O = ORANGE
    b = p.bob
    hx = 24.5
    if p.f == 'D':
        for y in range(28 + b, 45 + b):                                          # cremallera
            fg.shade(hx, y, -0.9, O)
            fg.shade(hx + 1, y, +0.3, O)
        fg.poly([(hx - 2.6, 26.5 + b), (hx + 2.6, 26.5 + b), (hx + 0.5, 31.5 + b)], spec['skin'], 2.0)  # coll en V
        for x in range(int(hx - 5), int(hx + 6)):                                # coll de la granota
            fg.shade(x, 27 + b, +0.7, O)
        # placa amb el número
        fg.poly([(hx + 3, 33 + b), (hx + 9, 33 + b), (hx + 9, 38 + b), (hx + 3, 38 + b)], SNEAKER, 3.6)
        for (dx, dy) in ((5, 34), (6, 34), (5, 35), (7, 35), (6, 36), (7, 36), (7, 37)):
            fg.px(hx + dx - 0.5, dy + b, (36, 36, 48), 0)
        # cinturó elàstic
        for x in range(int(hx - 9), int(hx + 10)):
            fg.shade(x, 45 + b, -1.0, O); fg.shade(x, 46 + b, +0.4, O)
        fg.shade(hx - 6, 41 + b, -0.6, O); fg.shade(hx - 5, 42 + b, -0.6, O)       # plecs
    elif p.f == 'U':
        fg.poly([(hx - 5, 34 + b), (hx + 5, 34 + b), (hx + 5, 39 + b), (hx - 5, 39 + b)], SNEAKER, 3.6)
        for x in range(int(hx - 3), int(hx + 4)):
            fg.px(x, 36.5 + b, (36, 36, 48), 0)
        for x in range(int(hx - 9), int(hx + 10)):
            fg.shade(x, 45 + b, -1.0, O); fg.shade(x, 46 + b, +0.4, O)
    else:
        for x in range(19, 33):
            fg.shade(x, 45 + b, -1.0, O); fg.shade(x, 46 + b, +0.4, O)
        fg.poly([(20.0, 26.5 + b), (22.6, 26.5 + b), (20.6, 30 + b)], spec['skin'], 2.0)


def vet_leg_front(fg, p, spec, i):
    h, k, a = p.hip[i], p.knee[i], p.ankle[i]
    side = -1 if i == 0 else 1
    off = 2.6 * side
    fg.line(h[0] + off, h[1] + 2, k[0] + off * 0.9, k[1], SNEAKER, 3.6 if i == 0 else 2.8)
    fg.line(k[0] + off * 0.9, k[1], a[0] + off * 0.8, a[1] - 1, SNEAKER, 3.6 if i == 0 else 2.8)


def vet_leg_side(fg, p, spec, leg, dl):
    h, k, a, _ = leg
    fg.line(h[0], h[1] + 2, k[0], k[1], SNEAKER, 3.4 + dl)
    fg.line(k[0], k[1], a[0], a[1] - 1, SNEAKER, 3.4 + dl)


def vet_cuff(fg, p, spec, i):
    if p.f == 'L':
        s, e, w = p.arms[0]
    else:
        s, e, w = p.sh[i], p.elbow[i], p.wrist[i]
    fg.limb((e[0] + (s[0] - e[0]) * 0.1, e[1] + (s[1] - e[1]) * 0.1), (e[0] + (w[0] - e[0]) * 0.15, e[1] + (w[1] - e[1]) * 0.15),
            3.0, 3.0, ORANGE, 3.0, amp=1.4, cont=(0.3, 1.0))


VET = {
    'skin': SKIN_VET, 'legs': ORANGE, 'top': ORANGE, 'forearm': SKIN_VET, 'shoes': SNEAKER, 'shoe_lvl': 3.4, 'lashes': True,
    'iris': (60, 36, 26), 'brow': (190, 180, 168), 'lip': (150, 40, 52),   # la cara de la Vet (les celles, decolorades)
    'hooks': {'hair_back': vet_hair_back, 'hair': vet_hair, 'torso': vet_suit, 'leg_deco': vet_leg_front,
              'leg_deco_side': vet_leg_side, 'arm': vet_cuff},
}


# ─── Secundaris de peu ──────────────────────────────────────────────────────

def redo_mouth(fg, p, spec):
    """Torna a pintar la boca (quan una barba o un bigoti l'han tapada)."""
    hx, hy = p.head
    ey = int(hy + 0.5)
    my = ey + 5
    lip = spec.get('lip', LIP)
    if p.f == 'D':
        nx = int(hx)
        if p.talk:
            for x in (nx - 1, nx, nx + 1):
                fg.px(x, my, MOUTH, 0)
            fg.px(nx, my + 1, MOUTH, 0)
        else:
            fg.px(nx - 1, my, lip, 0); fg.px(nx, my, mix(lip, MOUTH, 0.5), 0); fg.px(nx + 1, my, lip, 0)
    elif p.f == 'L':
        mx = int(hx - 5.5)
        fg.px(mx, my, MOUTH if p.talk else lip, 0); fg.px(mx + 1, my, MOUTH if p.talk else lip, 0)
        if p.talk:
            fg.px(mx + 1, my + 1, MOUTH, 0)


def patch(fg, x, y, w=6, h=5, digits=((2, 1), (3, 1), (2, 2), (4, 2), (3, 3), (4, 3))):
    fg.poly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], SNEAKER, 3.4)
    for dx, dy in digits:
        fg.px(x + dx - 0.5, y + dy, (36, 36, 48), 0)


def waist_band(fg, p, mat, y, d=-1.0, col=None):
    b = p.bob
    for x in range(12, 38):
        if col:
            if fg.get(x, y + b) and fg.get(x, y + b)[0] in (p.spec['top'], p.spec['legs']):
                fg.px(x, y + b, col, 1.6 + (0.8 if x < 24 else 0)); fg.px(x, y + 1 + b, col, 0.8)
        else:
            fg.shade(x, y + b, d, mat); fg.shade(x, y + 1 + b, 0.4, mat)


# Mos: vell, prim i maquillat; granota taronja descolorida, calb amb cabells blancs als costats i barba blanca.
def mos_hair(fg, p, spec):
    hx, hy = p.head
    H = HAIR_WHITE
    if p.f == 'D':
        for sx in (-1, 1):
            fg.ell(hx + sx * 6.3, hy + 0.5, 1.9, 3.4, H, 2.6, amp=1.5)
        # barba (deixa veure la boca)
        clip = lambda x, y: y >= hy + 3.6 + abs(x - hx) * -0.25 and not (abs(x - hx) < 2.2 and hy + 4.5 < y < hy + 7)
        fg.ell(hx, hy + 5.6, 5.8, 4.8, H, 2.8, amp=1.4, clip=clip, lvlfn=lambda x, y: 0.4 * math.sin(x * 2.0 + y))
        redo_mouth(fg, p, spec)
    elif p.f == 'L':
        fg.ell(hx + 4.0, hy + 0.8, 3.2, 3.6, H, 2.6, amp=1.5, clip=lambda x, y: x > hx + 2.6 or y < hy - 1)
        clip = lambda x, y: y >= hy + 3.4 and x <= hx + 1 and not (x < hx - 3.5 and hy + 4.5 < y < hy + 7)
        fg.ell(hx - 2.4, hy + 5.4, 4.6, 4.6, H, 2.8, amp=1.4, clip=clip, lvlfn=lambda x, y: 0.4 * math.sin(x * 2.0 + y))
        redo_mouth(fg, p, spec)
    else:
        fg.ell(hx, hy + 2.6, 6.8, 3.4, H, 2.6, amp=1.5, clip=lambda x, y: y >= hy + 0.5,
               lvlfn=lambda x, y: 0.4 * math.sin(x * 2.0 + y))
    if p.f != 'U':
        fg.shade(hx - 1.5, hy - 5.5, 1.2, spec['skin'])        # lluentor a la calba
        fg.shade(hx - 0.5, hy - 6, 1.0, spec['skin'])


def mos_suit(fg, p, spec):
    b = p.bob
    hx = 24.5
    O = spec['top']
    if p.f == 'D':
        fg.poly([(hx - 2.4, 26.5 + b), (hx + 2.6, 26.5 + b), (hx + 0.5, 31 + b)], spec['skin'], 1.8)
        patch(fg, hx + 2.5, 33 + b, 5, 4, ((1, 1), (2, 1), (3, 2), (2, 3)))
        for y in range(29 + b, 45 + b):
            fg.shade(hx, y, -0.7, O)
        waist_band(fg, p, O, 45)
        for (x, y) in ((hx - 5, 36), (hx - 4, 37), (hx + 4, 40), (hx - 6, 48), (hx + 5, 49)):   # plecs
            fg.shade(x, y + b, -0.8, O)
    elif p.f == 'U':
        patch(fg, hx - 4, 33 + b, 8, 4, ((2, 2), (3, 2), (4, 2), (5, 2), (6, 2)))
        waist_band(fg, p, O, 45)
    else:
        waist_band(fg, p, O, 45)


MOS = {
    'skin': SKIN_OLD, 'legs': ORANGE_FADED, 'top': ORANGE_FADED, 'shoes': GRAY_SHOE, 'thin': 1, 'stoop': 1,
    'iris': (40, 34, 40), 'brow': (226, 226, 232), 'liner': (96, 40, 110), 'lip': (176, 70, 110), 'lashes': True, 'blush': True,
    'hooks': {'hair': mos_hair, 'torso': mos_suit, 'leg_deco': vet_leg_front, 'leg_deco_side': vet_leg_side},
}


# Directora Aldaia: vestit fosc, camisa blanca, pin d'or; cabell blanc recollit en un monyo estirat.
def directora_hair(fg, p, spec):
    hx, hy = p.head
    H = HAIR_WHITE
    tex = hair_lvl(hx - 1, hy - 2, 5.4, k=1.0, strands=0.25, freq=2.4)
    if p.f == 'D':
        line = lambda x, y: y <= hy - 4.2 + ((x - hx) / 6.5) ** 2 * 6.0
        fg.ell(hx, hy - 0.6, 7.0, 7.6, H, 2.8, amp=1.6, clip=line, lvlfn=tex)
        fg.ell(hx, hy - 8.4, 3.2, 2.4, H, 3.0, amp=1.6, cont=(0, 0.8))
        fg.line(hx - 2, hy - 8.2, hx + 2, hy - 8.8, H, 1.6)
    elif p.f == 'L':
        line = lambda x, y: (x >= hx - 4.6 + max(0, y - (hy - 6)) * 0.3 or y <= hy - 5.8) and not (x < hx + 2.5 and y > hy - 2.5)
        fg.ell(hx + 1.2, hy - 0.8, 7.0, 7.6, H, 2.8, amp=1.6, clip=line, lvlfn=tex)
        fg.ell(hx + 5.6, hy - 6.6, 2.8, 2.8, H, 3.0, amp=1.6, cont=(0, 0.8))
    else:
        fg.ell(hx, hy - 0.4, 7.0, 7.8, H, 2.8, amp=1.6, lvlfn=tex)
        fg.ell(hx, hy - 6.0, 3.4, 3.0, H, 3.0, amp=1.6, cont=(0, 0.8))
        fg.ell(hx, hy - 6.0, 1.0, 1.0, H, 1.4, amp=0.5)


def directora_suit(fg, p, spec):
    b = p.bob
    hx = 24.5
    T = spec['top']
    if p.f == 'D':
        fg.poly([(hx - 3.6, 26.5 + b), (hx + 3.6, 26.5 + b), (hx + 0.5, 37 + b)], CREAM, 4.0)            # camisa
        fg.poly([(hx - 6, 27 + b), (hx - 3.4, 27 + b), (hx + 0.2, 37.5 + b), (hx - 4.6, 33 + b)], T, 3.8)  # solapes
        fg.poly([(hx + 3.4, 27 + b), (hx + 6, 27 + b), (hx + 4.6, 33 + b), (hx + 0.8, 37.5 + b)], T, 2.4)
        fg.line(hx + 0.5, 38 + b, hx + 0.5, 53 + b, T, 1.0)
        for y in (40, 45):
            fg.px(hx - 0.5, y + b, GOLDPIN, 1)
        fg.px(hx + 5, 31 + b, GOLDPIN, 3); fg.px(hx + 6, 31 + b, GOLDPIN, 2); fg.px(hx + 5, 32 + b, GOLDPIN, 1)
        for x in list(range(int(hx - 8), int(hx - 3))) + list(range(int(hx + 4), int(hx + 9))):
            fg.shade(x, 47 + b, -1.0, T)
    elif p.f == 'U':
        for y in range(29 + b, 54 + b):
            fg.shade(hx, y, -0.8, T)
        fg.ell(hx, 28 + b, 4.6, 1.8, T, 3.4, amp=1.0)
    else:
        fg.poly([(20.0, 26.5 + b), (22.8, 26.5 + b), (20.4, 33 + b)], CREAM, 3.6)
        fg.poly([(20.6, 27 + b), (23.0, 27 + b), (21.4, 36 + b), (19.8, 34 + b)], T, 3.6)
        fg.px(21, 31 + b, GOLDPIN, 3)


DIRECTORA = {
    'skin': SKIN_PALE, 'legs': SUIT_D, 'top': SUIT_D, 'shoes': BELT, 'shoe_lvl': 2.2,
    'iris': (60, 70, 90), 'brow': (120, 116, 130), 'lip': (140, 40, 56), 'lashes': True, 'brow_dy': 0,
    'hooks': {'hair': directora_hair, 'torso': directora_suit},
}


# Inspector Sic: gavardina llarga cordada amb cinturó, barret de feltre, bigoti espès.
def sic_hat(fg, p, spec):
    hx, hy = p.head
    F = FELT
    hair = HAIR_BROWN
    if p.f == 'D':
        fg.ell(hx - 6.2, hy + 0.5, 1.4, 2.6, hair, 2.0, amp=1.2)
        fg.ell(hx + 6.2, hy + 0.5, 1.4, 2.6, hair, 1.6, amp=1.2)
        # bigoti
        fg.poly([(hx - 3.6, hy + 3.6), (hx + 3.6, hy + 3.6), (hx + 4.4, hy + 5.6), (hx + 1.0, hy + 4.8), (hx - 1.0, hy + 4.8), (hx - 4.4, hy + 5.6)],
                hair, 2.6, lvlfn=lambda x, y: 0.5 * math.sin(x * 2.4))
        redo_mouth(fg, p, spec)
        fg.ell(hx, hy - 4.6, 10.0, 2.0, F, 2.4, amp=1.4)                                         # ala
        fg.ell(hx, hy - 8.0, 6.4, 4.4, F, 2.8, amp=1.6, clip=lambda x, y: y <= hy - 4.8)          # copa
        for x in range(int(hx - 6), int(hx + 7)):
            fg.px(x, hy - 5.4, BELT, 1.4)
        fg.shade(hx - 0.5, hy - 11.5, -0.9, F)                                                    # plec de la copa
    elif p.f == 'L':
        fg.ell(hx + 4.0, hy + 0.6, 2.6, 3.0, hair, 2.0, amp=1.2, clip=lambda x, y: x > hx + 2.4)
        fg.poly([(hx - 7.4, hy + 3.4), (hx - 3.4, hy + 3.4), (hx - 3.0, hy + 5.4), (hx - 5.0, hy + 4.8), (hx - 7.6, hy + 5.4)],
                hair, 2.6)
        redo_mouth(fg, p, spec)
        fg.ell(hx + 0.6, hy - 4.6, 10.0, 1.8, F, 2.4, amp=1.4)
        fg.ell(hx + 1.0, hy - 8.0, 6.4, 4.4, F, 2.8, amp=1.6, clip=lambda x, y: y <= hy - 4.8)
        for x in range(int(hx - 5), int(hx + 8)):
            fg.px(x, hy - 5.4, BELT, 1.4)
    else:
        fg.ell(hx, hy + 1, 6.6, 5.0, hair, 2.2, amp=1.4, clip=lambda x, y: y >= hy - 3)
        fg.ell(hx, hy - 4.6, 10.0, 2.0, F, 2.2, amp=1.4)
        fg.ell(hx, hy - 8.0, 6.4, 4.4, F, 2.8, amp=1.6, clip=lambda x, y: y <= hy - 4.8)
        for x in range(int(hx - 6), int(hx + 7)):
            fg.px(x, hy - 5.4, BELT, 1.4)


def sic_coat(fg, p, spec):
    b = p.bob
    hx = 24.5
    T = TRENCH
    HEM = 71
    if p.f in 'DU':
        n = front_normal(hx, 12.5)
        fl = lambda x, y: fold(x, y, (17, 21, 29, 32), 52 + b, HEM + b)
        fg.poly([(hx - 9.2, 27 + b), (hx + 9.2, 27 + b), (hx + 10.0, 45 + b), (hx + 11.6, HEM + b), (hx - 11.6, HEM + b), (hx - 10.0, 45 + b)],
                T, 2.9, amp=1.6, normal=n, cont=(0.2, 0.8), lvlfn=fl)
        if p.f == 'D':
            fg.poly([(hx - 6.5, 27 + b), (hx - 1.0, 27 + b), (hx + 2.0, 36 + b), (hx - 4.0, 33 + b)], T, 4.0)   # solapes
            fg.poly([(hx + 1.0, 27 + b), (hx + 6.5, 27 + b), (hx + 4.0, 33 + b), (hx + 2.0, 36 + b)], T, 2.4)
            fg.poly([(hx - 1.6, 26.5 + b), (hx + 1.6, 26.5 + b), (hx, 29 + b)], CREAM, 3.4)
            fg.px(hx, 29 + b, RED, 2); fg.px(hx, 30 + b, RED, 1.4)                                         # corbata
            for y in range(37 + b, HEM + b):
                fg.shade(hx + 2.5, y, -1.0, T)
            for y in (38, 42, 50, 56):
                fg.px(hx - 3, y + b, BELT, 2); fg.px(hx + 5, y + b, BELT, 2)
        else:
            for y in range(48 + b, HEM + b):
                fg.shade(hx, y, -1.2, T)
            fg.ell(hx, 28 + b, 5.4, 2.2, T, 3.6, amp=1.0)
        for x in range(12, 38):                                                       # cinturó
            if fg.get(x, 44 + b) and fg.get(x, 44 + b)[0] is T:
                fg.px(x, 44 + b, T, 1.4); fg.px(x, 45 + b, T, 2.4); fg.px(x, 46 + b, T, 1.2)
        if p.f == 'D':
            fg.px(hx - 1, 45 + b, BRASS, 3); fg.px(hx, 45 + b, BRASS, 2)
    else:
        n = front_normal(25.5, 7.5)
        fg.poly([(20.6, 27 + b), (30.4, 27 + b), (32.0, 42 + b), (33.4, HEM + b), (18.8, HEM + b), (19.4, 44 + b), (19.2, 33 + b)],
                T, 2.9, amp=1.6, normal=n, cont=(0.3, 0.9), lvlfn=lambda x, y: fold(x, y, (22, 29), 52 + b, HEM + b))
        fg.poly([(20.4, 27 + b), (23.0, 27 + b), (21.0, 37 + b), (19.2, 35 + b)], T, 4.0)
        for x in range(18, 34):
            if fg.get(x, 44 + b) and fg.get(x, 44 + b)[0] is T:
                fg.px(x, 44 + b, T, 1.4); fg.px(x, 45 + b, T, 2.4); fg.px(x, 46 + b, T, 1.2)


SIC = {
    'skin': SKIN_RUDDY, 'legs': TROUSER, 'top': TRENCH, 'shoes': BOOT, 'shoe_lvl': 2.2,
    'iris': (40, 30, 30), 'brow': (52, 36, 32), 'brow_dy': 1, 'lip': (130, 60, 56),
    'hooks': {'hair': sic_hat, 'torso': sic_coat},
}


# Mira d'Orís: cabell coure arrissat i curt amb mocador groc, granota de feina amb pitet i tirants,
# camisa crema arromangada i una clau anglesa a la butxaca.
def curls(fg, cx, cy, rx, ry, mat, clip=None, base=2.8):
    """Massa de rínxols: un el·lipsoide amb petits cercles de llum i ombra."""
    fg.ell(cx, cy, rx, ry, mat, base, amp=1.6, clip=clip, cont=(0, 0.6),
           lvlfn=curl_lvl)


def curl_lvl(x, y):
    u, v = (x + (y // 3) * 1.5) % 3, y % 3
    if u < 1 and v < 1:
        return 0.8
    if u >= 2 and v >= 1:
        return -0.7
    return 0.0


def mira_hair(fg, p, spec):
    hx, hy = p.head
    H = HAIR_COPPER
    scarf = M((70, 50, 10), (150, 110, 20), (214, 170, 40), (240, 208, 80), (255, 236, 150))
    if p.f == 'D':
        curls(fg, hx, hy - 1.2, 8.0, 7.8, H, clip=lambda x, y: y <= hy - 3.4 + ((x - hx) / 6.2) ** 2 * 7)
        fg.limb((hx - 7.4, hy - 4.8), (hx + 7.4, hy - 4.8), 1.3, 1.3, scarf, 2.6, amp=1.2)
        fg.ell(hx + 6.8, hy - 6.6, 1.8, 1.4, scarf, 3.0, amp=1.2)                                  # nus
        for (dx, dy) in ((-3, 3), (-2, 4), (3, 3), (2, 4), (-4, 4), (4, 4)):                      # pigues
            fg.shade(hx + dx - 0.5, hy + dy - 0.5, -0.7, spec['skin'])
    elif p.f == 'L':
        curls(fg, hx + 1.4, hy - 0.8, 7.8, 7.8, H,
              clip=lambda x, y: (x >= hx - 4.4 or y <= hy - 5.6) and not (x < hx + 2.2 and y > hy - 2.8))
        fg.limb((hx - 6.0, hy - 5.0), (hx + 8.6, hy - 3.6), 1.3, 1.3, scarf, 2.6, amp=1.2)
        fg.ell(hx + 9.0, hy - 2.0, 1.4, 2.2, scarf, 2.2, amp=1.2)
        for (dx, dy) in ((-2, 3), (-1, 4), (-3, 4)):
            fg.shade(hx + dx - 0.5, hy + dy - 0.5, -0.7, spec['skin'])
    else:
        curls(fg, hx, hy + 0.2, 8.0, 8.2, H)
        fg.limb((hx - 7.6, hy - 4.6), (hx + 7.6, hy - 4.6), 1.3, 1.3, scarf, 2.6, amp=1.2)
        fg.ell(hx, hy - 4.0, 1.8, 1.6, scarf, 3.0, amp=1.2)


def mira_overalls(fg, p, spec):
    b = p.bob
    hx = 24.5
    D = DENIM
    if p.f == 'L':
        fg.lathe(44 + b, round(p.hip_y) + 3, side_torso_edges(p), D, 2.8, amp=1.6)
    else:
        fg.lathe(44 + b, HIPY + 3 + b, torso_edges(p), D, 2.8, amp=1.6)
    if p.f == 'D':
        fg.poly([(hx - 5.5, 34 + b), (hx + 5.5, 34 + b), (hx + 7.4, 46 + b), (hx - 7.4, 46 + b)], D, 3.0, amp=1.4,
                normal=front_normal(hx, 10), cont=(0.2, 0.8))                                       # pitet
        fg.line(hx - 5.5, 34 + b, hx - 7.2, 27 + b, D, 2.6); fg.line(hx - 4.5, 34 + b, hx - 6.2, 27 + b, D, 2.2)  # tirants
        fg.line(hx + 5.5, 34 + b, hx + 7.2, 27 + b, D, 2.0); fg.line(hx + 4.5, 34 + b, hx + 6.2, 27 + b, D, 1.6)
        fg.px(hx - 5, 34 + b, STEELB, 4); fg.px(hx + 5, 34 + b, STEELB, 3)
        for x in range(int(hx - 3), int(hx + 3)):                                                    # butxaca
            fg.shade(x, 38 + b, -1.0, D)
        fg.px(hx + 2, 36 + b, STEELB, 3); fg.px(hx + 2, 37 + b, STEELB, 2); fg.px(hx + 1, 36 + b, STEELB, 2)  # clau anglesa
        fg.poly([(hx - 2.2, 26.5 + b), (hx + 2.2, 26.5 + b), (hx, 29 + b)], spec['skin'], 2.0)
        for x in range(int(hx - 9), int(hx + 10)):
            if fg.get(x, 46 + b) and fg.get(x, 46 + b)[0] is D:
                fg.shade(x, 46 + b, -0.9, D)
    elif p.f == 'U':
        fg.line(hx - 6.5, 27 + b, hx, 38 + b, D, 2.4); fg.line(hx + 6.5, 27 + b, hx, 38 + b, D, 1.8)
        fg.line(hx - 5.5, 27 + b, hx, 37 + b, D, 2.0); fg.line(hx + 5.5, 27 + b, hx, 37 + b, D, 1.6)
        for x in range(int(hx - 4), int(hx + 5)):
            fg.shade(x, 44 + b, -0.8, D)
    else:
        fg.poly([(19.6, 35 + b), (22.6, 35 + b), (22.6, 46 + b), (20.4, 46 + b)], D, 3.0, amp=1.0)
        fg.line(21.5, 35 + b, 26.0, 27 + b, D, 2.4)
        fg.px(21, 36 + b, STEELB, 3)


MIRA = {
    'skin': SKIN_PALE, 'legs': DENIM, 'top': CREAM, 'forearm': SKIN_PALE, 'shoes': BOOT,
    'iris': (60, 90, 60), 'brow': (150, 70, 36), 'lashes': True, 'blush': True,
    'hooks': {'hair': mira_hair, 'torso': mira_overalls},
}


def cuff_hook(mat):
    def h(fg, p, spec, i):
        if p.f == 'L':
            s, e, w = p.arms[0]
        else:
            s, e, w = p.sh[i], p.elbow[i], p.wrist[i]
        fg.limb((e[0] + (s[0] - e[0]) * 0.1, e[1] + (s[1] - e[1]) * 0.1), (e[0] + (w[0] - e[0]) * 0.15, e[1] + (w[1] - e[1]) * 0.15),
                3.0, 3.0, mat, 3.0, amp=1.4, cont=(0.3, 1.0))
    return h


MIRA['hooks']['arm'] = cuff_hook(CREAM)


# Guàrdia d'Orís: el cabell coure de la família recollit en una cua, gorra i uniforme blau marí amb placa.
def guardia_hair_back(fg, p, spec):
    hx, hy = p.head
    if p.f == 'U':
        fg.limb((hx, hy + 2), (hx + 0.4, hy + 13), 2.0, 1.4, HAIR_COPPER, 2.6, amp=1.6, cont=(0, 0.8),
                lvlfn=lambda x, y: 0.6 * math.sin(y * 1.3))


def guardia_hair(fg, p, spec):
    hx, hy = p.head
    H = HAIR_COPPER
    C = NAVY_U
    tex = hair_lvl(hx - 1, hy - 2, 5.0, k=1.0, strands=0.3, freq=2.0)
    if p.f == 'D':
        fg.ell(hx, hy - 0.6, 7.0, 7.4, H, 2.6, amp=1.6, lvlfn=tex, clip=lambda x, y: y <= hy - 3 + ((x - hx) / 6.4) ** 2 * 7)
        fg.ell(hx, hy - 5.4, 7.6, 3.6, C, 2.8, amp=1.6, clip=lambda x, y: y <= hy - 4.0)            # gorra
        fg.ell(hx, hy - 3.8, 7.8, 1.4, C, 1.4, amp=1.0)                                              # visera
        fg.px(hx - 0.5, hy - 6.5, GOLDPIN, 3); fg.px(hx + 0.5, hy - 6.5, GOLDPIN, 2); fg.px(hx, hy - 7.5, GOLDPIN, 2)
    elif p.f == 'L':
        fg.ell(hx + 1.2, hy - 0.6, 7.0, 7.4, H, 2.6, amp=1.6, lvlfn=tex,
               clip=lambda x, y: (x >= hx - 4.0 or y <= hy - 5) and not (x < hx + 2.4 and y > hy - 2.6))
        fg.limb((hx + 6.4, hy - 0.5), (hx + 8.6, hy + 9), 2.0, 1.3, H, 2.6, amp=1.6, cont=(0, 0.8),
                lvlfn=lambda x, y: 0.6 * math.sin(y * 1.3))                                          # cua
        fg.ell(hx + 1.6, hy - 5.4, 7.4, 3.6, C, 2.8, amp=1.6, clip=lambda x, y: y <= hy - 4.0)
        fg.poly([(hx - 9.0, hy - 4.6), (hx - 3.0, hy - 4.8), (hx - 3.0, hy - 3.2), (hx - 8.0, hy - 3.4)], C, 1.4)
        fg.px(hx - 4.0, hy - 6.5, GOLDPIN, 3)
    else:
        fg.ell(hx, hy - 0.2, 7.0, 7.8, H, 2.6, amp=1.6, lvlfn=tex)
        fg.ell(hx, hy - 5.4, 7.6, 3.6, C, 2.8, amp=1.6, clip=lambda x, y: y <= hy - 4.0)
        fg.ell(hx, hy + 1.2, 1.8, 1.2, C, 2.2, amp=1.0)                                              # goma de la cua


def guardia_uniform(fg, p, spec):
    b = p.bob
    hx = 24.5
    U = NAVY_U
    if p.f == 'D':
        for y in range(29 + b, 45 + b):
            fg.shade(hx, y, -0.9, U)
        for y in (32, 36, 40):
            fg.px(hx - 1, y + b, STEELB, 3)
        fg.poly([(hx - 2.6, 26.5 + b), (hx + 2.6, 26.5 + b), (hx, 28.5 + b)], CREAM, 3.4)
        fg.poly([(hx + 3.5, 32 + b), (hx + 6.5, 32 + b), (hx + 6.5, 34.5 + b), (hx + 5, 36 + b), (hx + 3.5, 34.5 + b)], GOLDPIN, 2.2, amp=1.0)
        fg.px(hx + 4.5, 32.5 + b, GOLDPIN, 3.4)
        for x in range(int(hx - 8), int(hx - 3)):                                                    # butxaca
            fg.shade(x, 33 + b, -1.0, U)
    elif p.f == 'U':
        for y in range(29 + b, 45 + b):
            fg.shade(hx, y, -0.6, U)
    for x in range(12, 38):
        g = fg.get(x, 45 + b)
        if g and g[0] in (U, spec['legs']):
            fg.px(x, 45 + b, BELT, 2.2 if x < 24 else 1.6); fg.px(x, 46 + b, BELT, 1.0)
    if p.f == 'D':
        fg.px(hx - 0.5, 45 + b, STEELB, 4); fg.px(hx + 0.5, 45 + b, STEELB, 3)
    elif p.f == 'L':
        fg.px(23, 45 + b, STEELB, 3)


GUARDIA = {
    'skin': SKIN_PALE, 'legs': NAVY_U, 'top': NAVY_U, 'shoes': BELT, 'shoe_lvl': 2.4,
    'iris': (60, 90, 60), 'brow': (150, 70, 36), 'lashes': True, 'blush': True,
    'hooks': {'hair_back': guardia_hair_back, 'hair': guardia_hair, 'torso': guardia_uniform},
}


# ─── Cargol (robot) ─────────────────────────────────────────────────────────
#
# 55×63, erugues a terra a (27, 60). Closca de cargol de llautó a l'esquena, cos d'acer amb pantalla-cara,
# ulls a dalt de dues antenes, un braç amb una clau anglesa. De vell (conserge): rovellat i amb els llums gastats.

CHROME = M((14, 18, 30), (34, 42, 60), (64, 76, 96), (104, 118, 138), (150, 166, 184), (198, 212, 224), (240, 248, 252), (255, 255, 255))
RUBBER = M((10, 10, 14), (22, 22, 28), (36, 36, 44), (54, 54, 62), (76, 76, 84))
SCREEN = M((6, 10, 14), (12, 22, 26), (18, 34, 38), (28, 50, 52))
LAMP = M((20, 70, 50), (50, 150, 100), (110, 230, 160), (190, 255, 214), (240, 255, 246))
RUSTY = M((24, 12, 12), (48, 22, 18), (78, 38, 26), (110, 58, 36), (142, 86, 52), (170, 116, 76), (196, 150, 108))
RUST_BRASS = M((30, 18, 14), (60, 34, 20), (96, 58, 30), (130, 86, 44), (160, 118, 64), (188, 150, 92))
LAMP_OLD = M((50, 34, 10), (110, 80, 24), (180, 140, 50), (226, 196, 100), (250, 230, 170))


def spiral_lvl(cx, cy, pitch=4.2, turn=1.0):
    def f(x, y):
        r = math.hypot(x - cx, y - cy)
        th = math.atan2(y - cy, x - cx) * turn
        s = (r / pitch - th / (2 * math.pi)) % 1
        if s < 0.2:
            return -1.6
        if s < 0.4:
            return 0.7
        return 0.0
    return f


def cargol(facing, blink=False, talk=False, old=False):
    fg = Fig(55, 63)
    ST = RUSTY if old else CHROME
    BR = RUST_BRASS if old else BRASS
    LP = LAMP_OLD if old else LAMP
    lamp_lvl = 1.0 if blink else (4.0 if talk else 3.0)
    if old:
        lamp_lvl -= 0.6
    up = -1 if talk else 0

    def tracks(x0, x1, side):
        fg.poly([(x0 + 2, 50), (x1 - 2, 50), (x1, 53), (x1, 58), (x1 - 2, 60), (x0 + 2, 60), (x0, 58), (x0, 53)], RUBBER, 2.4, amp=1.4,
                normal=lambda x, y: (0, (y - 55) / 6, 0.8), cont=(0.3, 0.8),
                lvlfn=lambda x, y: (0.9 if (x + (0 if y < 55 else 1)) % 3 == 0 else 0) if y in (50, 51, 59, 60) else 0)
        if side:
            for wx in range(x0 + 4, x1 - 2, 6):
                fg.ell(wx, 55, 2.4, 2.4, ST, 2.6, amp=1.6)
                fg.px(wx, 55, ST, 0.6)

    def antenna(bx, by, tx, ty):
        fg.line(bx, by, tx, ty + 2, ST, 2.2)
        fg.line(bx + 1, by, tx + 1, ty + 2, ST, 3.6)
        fg.ell(tx + 0.5, ty, 3.0, 3.0, ST, 2.8, amp=1.6)
        fg.ell(tx + 0.5, ty, 2.0, 2.0, LP, lamp_lvl, amp=1.2)
        if not blink:
            fg.px(tx, ty - 0.5, LP, 4.6)

    def shine():
        if old:
            return
        for (x, y) in ((18, 26), (19, 25), (19, 27), (20, 26)):
            fg.px(x, y, CHROME, 7)

    if facing == 'D':
        tracks(9, 21, False)
        tracks(33, 45, False)
        fg.ell(27, 28, 17, 15, BR, 2.8, amp=1.6, lvlfn=spiral_lvl(27, 28, 5.0), cont=(0, 0.8))   # closca, darrere
        fg.lathe(22, 52, lambda y: (17 - max(0, 25 - y) * 1.2, 37 + max(0, 25 - y) * 1.2) if y <= 50 else (19, 35), ST, 3.0, amp=1.8, cont=(0.2, 1.0))
        fg.poly([(19, 28), (35, 28), (35, 40), (19, 40)], SCREEN, 1.6, cont=(1.0, -0.8))             # pantalla
        for ex in (23, 31):
            fg.ell(ex, 32.5, 2.2, 2.0 if not blink else 0.6, LP, lamp_lvl, amp=1.0)
        gy = 37 + up
        for x in range(22, 33, 2):
            fg.px(x, gy, LP if talk else ST, 2.4 if talk else 3.4)
            if talk:
                fg.px(x, gy + 1, LP, 1.6)
        for x in range(18, 37):                                                                   # junta
            fg.shade(x, 44, -1.2, ST); fg.shade(x, 45, 0.8, ST)
        for (x, y) in ((19, 47), (35, 47), (19, 25), (35, 25)):
            fg.px(x, y, ST, 1.0)
        # braços
        fg.limb((15.5, 31), (11.5, 41), 1.8, 1.6, ST, 2.6, amp=1.6, cont=(0.2, 0.8))
        fg.ell(11.5, 42, 2.2, 1.8, ST, 2.2, amp=1.4)
        fg.limb((38.5, 31), (43, 40), 1.8, 1.6, ST, 2.4, amp=1.6, cont=(0.2, 0.8))
        fg.limb((43.5, 38), (44.5, 48), 1.3, 1.3, ST, 3.4, amp=1.6)                               # clau anglesa
        fg.ell(44.5, 49.5, 2.4, 2.0, ST, 3.0, amp=1.4)
        fg.erase(44.5, 51); fg.erase(44.5, 50)
        antenna(21, 22, 19, 9 + up)
        antenna(33, 22, 35, 9 + up)
        shine()
    elif facing == 'L':
        tracks(8, 42, True)
        fg.lathe(22, 51, lambda y: (12 + max(0, 25 - y) * 1.0, 30), ST, 3.0, amp=1.8, cont=(0.2, 1.0))
        fg.poly([(12, 28), (19, 28), (19, 40), (12, 40)], SCREEN, 1.6, cont=(1.0, -0.8))
        fg.ell(15, 32.5, 1.8, 2.0 if not blink else 0.6, LP, lamp_lvl, amp=1.0)
        for x in range(13, 19, 2):
            fg.px(x, 37 + up, LP if talk else ST, 2.4 if talk else 3.4)
        fg.ell(36, 30, 15, 16, BR, 2.8, amp=1.6, lvlfn=spiral_lvl(37, 29, 4.4), cont=(0.2, 1.0))     # closca
        fg.ell(37, 29, 2.4, 2.4, BR, 1.2, amp=0.8)
        for x in range(12, 31):
            fg.shade(x, 44, -1.2, ST); fg.shade(x, 45, 0.8, ST)
        fg.limb((22, 32), (13, 39), 1.8, 1.6, ST, 2.8, amp=1.6, cont=(0.3, 1.0))
        fg.limb((12, 39), (8, 46), 1.3, 1.3, ST, 3.4, amp=1.6)
        fg.ell(7.5, 47.5, 2.2, 1.8, ST, 3.0, amp=1.4)
        antenna(16, 22, 12, 9 + up)
        antenna(21, 22, 21, 7 + up)
        shine()
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
        # taques de rovell, una abonyegadura i un cargol que hi falta
        for (x, y) in ((24, 47), (25, 48), (31, 46), (20, 49), (30, 26), (14, 50)):
            fg.shade(x, y, -1.4, ST)
        fg.shade(36, 34, -1.0)
        fg.shade(37, 35, -1.0)
    else:
        for (x, y) in ((22, 24), (23, 23), (27, 18), (40, 22)):
            fg.shade(x, y, 1.6, BR)
    return fg.render()


# ─── El capatàs Tul, adormit a la cadira ─────────────────────────────────────
#
# 65×82, peus a (33, 79). Panxa que respira, gorra sobre els ulls, bigoti, braços creuats amb el segell.

WOOD = M((20, 10, 12), (42, 22, 20), (68, 38, 28), (98, 58, 36), (130, 84, 50), (164, 112, 68), (196, 146, 96))
CAP = M((14, 14, 20), (30, 30, 38), (50, 50, 60), (74, 74, 82), (102, 100, 106))
SHIRT_C = M((60, 50, 54), (110, 98, 92), (160, 148, 130), (204, 194, 172), (232, 224, 204), (248, 244, 228))
BRACES = M((40, 8, 14), (80, 18, 24), (122, 32, 32), (164, 52, 42))


def capatas(breath=0, with_seal=True, talk=False, zz=0):
    fg = Fig(65, 82)
    S = SKIN_RUDDY
    # cadira: respatller, seient, potes
    fg.poly([(13, 22), (51, 22), (50, 58), (14, 58)], WOOD, 2.0, amp=0.0, cont=(0.3, 1.2),
            lvlfn=lambda x, y: (0.6 if y in (22, 23) else 0) + (-0.8 if (x - 13) % 9 == 0 else 0) + 0.25 * math.sin(y * 0.9 + x * 0.1))
    fg.limb((12, 20), (52, 20), 2.2, 2.2, WOOD, 3.0, amp=1.4)
    for x in (13, 49):
        fg.limb((x + 1, 58), (x + 1, 79), 1.6, 1.4, WOOD, 2.4, amp=1.4, cont=(0.2, 0.8))
    fg.poly([(9, 56), (56, 56), (58, 61), (7, 61)], WOOD, 3.0, amp=0.0, cont=(0.2, 1.0),
            lvlfn=lambda x, y: 1.0 if y == 56 else (-0.6 if y == 61 else 0))
    # cames: cuixes cap a nosaltres (escurçades), canyelles avall
    for kx in (25, 41):
        fg.ell(kx, 58, 6.4, 4.4, TROUSER, 2.8, amp=1.6)
        fg.limb((kx, 61), (kx + (1 if kx > 33 else -1), 74), 3.8, 3.4, TROUSER, 2.6, amp=1.6, cont=(0.2, 0.6))
        fg.ell(kx + (1.5 if kx > 33 else -1.5), 76.5, 4.6, 3.0, BOOT, 2.6, amp=1.8)
    # panxa (respira) i tronc
    fg.lathe(30, 54, lambda y: (19 - breath * 0.5 - max(0, (y - 32)) * 0.15, 47 + breath * 0.5 + max(0, (y - 32)) * 0.15) if y < 50 else (19.5, 46.5),
             SHIRT_C, 2.8, amp=1.4)
    fg.ell(33, 44, 13.5 + breath, 11 + breath * 0.6, SHIRT_C, 2.9, amp=2.2,
           lvlfn=lambda x, y: (-0.8 if x == 33 and y < 50 else 0))
    for y in range(36, 52, 4):
        fg.px(33, y, CREAM, 4)
    for bx in (25, 41):                                                       # tirants
        fg.line(bx, 30, bx + (-1.5 if bx < 33 else 1.5), 52, BRACES, 2.4)
        fg.line(bx + 1, 30, bx + 1 + (-1.5 if bx < 33 else 1.5), 52, BRACES, 1.6)
    fg.lathe(52, 55, lambda y: (19.5, 46.5), BELT, 2.0, amp=1.2)
    fg.px(33, 53, BRASS, 3); fg.px(34, 53, BRASS, 2)
    # braços creuats
    fg.limb((20, 33), (22, 46), 3.6, 3.4, SHIRT_C, 2.4, amp=1.6, cont=(0.2, 0.9))
    fg.limb((46, 33), (44, 46), 3.6, 3.4, SHIRT_C, 2.0, amp=1.6, cont=(0.2, 0.9))
    fg.limb((22, 46), (40, 44), 3.2, 3.0, SHIRT_C, 2.8, amp=1.6, cont=(0.3, 1.0))
    fg.limb((44, 46), (27, 47), 3.2, 3.0, SHIRT_C, 3.0, amp=1.6, cont=(0.3, 1.0))
    if with_seal:
        fg.limb((33, 38), (33, 42), 1.5, 1.8, RED, 2.6, amp=1.6, cont=(0.2, 0.8))   # mànec vermell
        fg.ell(33, 36.5, 2.8, 2.4, RED, 2.8, amp=1.8, cont=(0.2, 0.8))
        fg.poly([(27.5, 42), (38.5, 42), (38.5, 45), (27.5, 45)], WOOD, 3.0, amp=0.0, cont=(0.3, 1.0),
                lvlfn=lambda x, y: 0.8 if y == 42 else 0)                     # base de fusta
        fg.line(28, 46, 38, 46, BRASS, 2.0)
    fg.ell(40.5, 44.5, 2.6, 2.3, S, 2.8, amp=1.4)                             # mans
    fg.ell(26.5, 46.5, 2.6, 2.3, S, 2.8, amp=1.4)
    # cap decantat, gorra sobre els ulls
    hx, hy = 36, 19
    fg.limb((hx - 1, hy + 4), (hx - 2.5, hy + 10), 4.0, 4.4, S, 2.0, amp=1.2)
    fg.poly([(hx - 9, hy + 10), (hx + 4, hy + 10), (hx - 1, hy + 14), (hx - 3.5, hy + 13)], SHIRT_C, 3.6, cont=(0.2, 0.8))  # coll
    fg.ell(hx, hy, 7.2, 7.8, S, 3.0, amp=1.5)
    fg.ell(hx - 0.6, hy + 4.6, 6.6, 5.6, S, 3.0, amp=1.5)
    fg.ell(hx - 7.0, hy + 2.6, 1.4, 2.0, S, 2.6, amp=1.2)
    fg.ell(hx + 7.0, hy + 2.6, 1.4, 2.0, S, 2.2, amp=1.2)
    fg.ell(hx + 0.5, hy - 3.6, 8.6, 5.2, CAP, 2.8, amp=1.6, clip=lambda x, y: y <= hy + 0.6 + (x - hx) * 0.1)
    fg.poly([(hx - 9.6, hy - 0.2), (hx + 6, hy + 0.8), (hx + 5.8, hy + 2.6), (hx - 8.8, hy + 2.0)], CAP, 1.6, cont=(0, 0.8))
    for x in range(int(hx - 4), int(hx + 3)):
        fg.px(x, hy - 4.5 + (x - hx) * 0.12, CAP, 3.6)
    fg.px(hx + 3, hy - 7, CAP, 4.2)                                                                   # botó
    ey = hy + 3.6
    fg.line(hx - 5, ey, hx - 3, ey + 0.4, MOUTH, 0); fg.line(hx + 1, ey + 0.4, hx + 3, ey + 0.6, MOUTH, 0)   # ulls tancats
    fg.ell(hx - 1, ey + 1.8, 2.0, 1.6, S, 3.6, amp=1.2)                                                   # nas
    fg.shade(hx, ey + 2.6, -1.0, S)
    fg.shade(hx - 5, ey + 2, -0.5, S); fg.shade(hx + 3, ey + 2, -0.5, S)                                  # galtes
    fg.poly([(hx - 6, ey + 3), (hx + 4, ey + 3.4), (hx + 5, ey + 5.4), (hx + 1, ey + 4.6), (hx - 3, ey + 4.6), (hx - 7, ey + 5.2)],
            HAIR_BROWN, 2.6, lvlfn=lambda x, y: 0.5 * math.sin(x * 2.4))                                  # bigoti
    my = ey + 5.6
    if talk:
        fg.px(hx - 2, my, MOUTH, 0); fg.px(hx - 1, my, MOUTH, 0); fg.px(hx, my, MOUTH, 0); fg.px(hx - 1, my + 1, MOUTH, 0)
    else:
        fg.px(hx - 1, my, MOUTH, 0); fg.px(hx - 2, my, mix(MOUTH, (150, 70, 70), 0.5), 0)
    img = fg.render()
    # zetes (sense contorn de la figura, però amb una ombra)
    if zz:
        Z = [(0, 0), (1, 0), (2, 0), (3, 0), (2, 1), (1, 2), (0, 3), (1, 3), (2, 3), (3, 3)]
        P = img.load()
        for i in range(zz):
            x0, y0 = 46 + i * 5, 12 - i * 5
            for dx, dy in Z:
                for ox, oy, c in ((1, 1, (40, 30, 50, 255)), (0, 0, (240, 240, 250, 255))):
                    x, y = x0 + dx + ox, y0 + dy + oy
                    if 0 <= x < 65 and 0 <= y < 82:
                        P[x, y] = c
    return img


# ─── MARE: l'altaveu en forma de cor ─────────────────────────────────────────

HEART = M((50, 10, 30), (100, 24, 60), (160, 50, 100), (220, 100, 160), (255, 160, 210), (255, 220, 240))


def mare(glow=False):
    fg = Fig(22, 22)
    base = 3.0 if glow else 2.4
    fg.ell(7.5, 8, 4.8, 4.8, HEART, base, amp=1.6)
    fg.ell(14.5, 8, 4.8, 4.8, HEART, base - 0.2, amp=1.6)
    fg.poly([(3.0, 9.5), (19.0, 9.5), (11.0, 19.0)], HEART, base - 0.3, amp=1.2,
            normal=lambda x, y: ((x - 11) / 9, 0.2, 0.9), cont=(0, 0.8))
    for (x, y) in ((8, 9), (10, 9), (12, 9), (14, 9), (9, 11), (11, 11), (13, 11), (10, 13), (12, 13), (11, 15)):
        fg.px(x, y, HEART, 1.0 if not glow else 1.6)
    fg.px(6, 6, HEART, 5); fg.px(7, 5, HEART, 5)
    img = fg.render()
    if glow:
        halo = Image.new('RGBA', img.size, (0, 0, 0, 0))
        P, Q = img.load(), halo.load()
        for y in range(22):
            for x in range(22):
                d = math.hypot(x - 11, (y - 11) * 1.1) / 11
                if d < 1 and not P[x, y][3] and (1 - d) ** 1.5 * 0.9 > B4[y & 3][x & 3]:
                    Q[x, y] = (255, 120, 190, 110)
        halo.alpha_composite(img)
        img = halo
    return img
