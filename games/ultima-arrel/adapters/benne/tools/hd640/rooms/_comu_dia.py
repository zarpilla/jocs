"""
L'Última Arrel — peces comunes de les sales de dia: `toll_gripaus`, `caseta_obra` i `zona_zero`.

Ve de les mostres d'art aprovades (guio/art/mostra/bosc.py): les mateixes rampes (fosc → clar) del bosc càlid i de
NaturaPlus, freda i plana, amb unes quantes de més per a la llum de dia (el fang sec, els joncs, l'aigua, el cel), el
soroll ràpid, la lletra petita, les arrels, les falgueres i els filaments del Miceli.

I, a més, el terra en perspectiva dels exteriors (`Terra`): una càmera a l'alçada dels ulls d'un adult (sense picat:
les verticals, verticals), amb l'horitzó a `hor`. Un punt del terra a la fila v de pantalla és a la profunditat
z = f·h / (v − hor), i un personatge que hi té els peus fa (v − hor) / h: l'escala és exacta i lineal en v.

1 unitat del món = 1 píxel de sala a l'escala 1 dels personatges (la Iri hi fa ≈72 px).
"""
import math
import random

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from PIL import Image

from hd.pix import Canvas, Light, B4, mix  # noqa: F401
from hd.rooms.comu import GLYPHS, _glyph

W, H = 640, 360
RH = 260                       # la sala es pinta fins aquí (a sota, el HUD)

# ─── Rampes (fosc → clar) ───────────────────────────────────────────────────
# El bosc viu: càlid (les de la mostra).
HAZE = [(40, 24, 30), (62, 36, 34), (88, 50, 38), (118, 66, 42), (152, 88, 48), (188, 116, 58), (218, 148, 74),
        (240, 186, 106), (252, 220, 150)]
LEAVES = [(18, 14, 12), (34, 24, 16), (56, 36, 20), (84, 52, 24), (116, 72, 28), (150, 96, 34), (186, 124, 44),
          (218, 158, 62), (240, 194, 96)]
BARK = [(14, 10, 10), (26, 18, 14), (42, 28, 20), (60, 40, 28), (82, 56, 36), (106, 74, 46), (132, 94, 58),
        (160, 118, 74), (188, 146, 96)]
MOSS = [(10, 18, 10), (20, 32, 16), (32, 48, 22), (48, 68, 30), (68, 90, 38), (92, 114, 50), (122, 142, 66),
        (156, 170, 88)]
EARTH = [(16, 12, 10), (30, 22, 16), (48, 34, 24), (68, 48, 32), (90, 64, 40), (114, 82, 50), (140, 102, 62),
         (166, 124, 78), (192, 150, 98)]
LEAF = [(70, 26, 12), (116, 44, 18), (164, 72, 24), (206, 108, 38), (236, 150, 62), (250, 194, 110)]
PLANK = [(22, 12, 8), (40, 24, 14), (62, 38, 20), (88, 56, 28), (116, 76, 38), (144, 98, 50), (172, 124, 66),
         (200, 152, 88)]
IRONK = [(8, 8, 10), (18, 18, 22), (32, 30, 34), (50, 48, 52), (74, 70, 72)]
STONE = [(22, 20, 22), (38, 36, 36), (58, 54, 52), (80, 76, 70), (104, 98, 90), (130, 124, 112), (158, 152, 138),
         (186, 180, 164), (214, 208, 190)]
FERN = [(4, 6, 4), (8, 12, 8), (14, 20, 12), (22, 30, 16), (34, 42, 22), (52, 58, 30), (80, 76, 40)]
CREAM = [(70, 58, 50), (120, 104, 86), (170, 154, 128), (210, 196, 166), (236, 226, 198), (250, 244, 224)]
BRASS = [(40, 26, 8), (84, 58, 16), (134, 98, 30), (186, 144, 52), (226, 192, 96), (250, 230, 160)]
# La xarxa: blau i turquesa bioluminescent.
TURQ = [(4, 20, 26), (6, 40, 48), (10, 70, 78), (20, 108, 112), (40, 150, 150), (80, 200, 192), (150, 240, 226),
        (220, 255, 248)]
GLOW_T = (110, 236, 220)
# NaturaPlus: fred, pla, artificial.
PLASTIC = [(60, 66, 80), (96, 104, 118), (136, 142, 156), (176, 182, 192), (210, 214, 222), (234, 236, 242),
           (250, 251, 253)]
STEEL = [(16, 18, 24), (30, 34, 42), (48, 54, 64), (70, 78, 90), (98, 106, 118), (130, 138, 148), (168, 174, 182),
         (206, 210, 216)]
NEON = [(8, 34, 10), (20, 80, 20), (50, 150, 40), (110, 220, 70), (180, 252, 130), (230, 255, 200)]
SIGNK = [(6, 8, 10), (12, 16, 18), (20, 26, 28), (30, 38, 40)]
CONE = [(60, 16, 6), (120, 36, 10), (190, 70, 20), (236, 116, 40), (252, 170, 90)]
YELLOWM = [(50, 36, 6), (100, 74, 10), (160, 120, 20), (214, 170, 36), (244, 210, 80), (255, 236, 150)]
REDL = [(40, 6, 4), (100, 16, 8), (180, 34, 14), (240, 70, 30), (255, 140, 90), (255, 210, 180)]
SCREENB = [(8, 14, 30), (14, 30, 60), (24, 54, 100), (44, 90, 150), (90, 150, 210), (170, 214, 245),
           (230, 245, 255)]

# De dia (noves).
SKYD = [(96, 140, 186), (120, 162, 204), (146, 184, 218), (172, 202, 228), (196, 218, 236), (216, 230, 240),
        (234, 240, 244), (246, 248, 246)]
DRYG = [(40, 30, 14), (70, 54, 22), (104, 82, 32), (140, 112, 44), (176, 144, 60), (206, 176, 84), (228, 204, 118),
        (244, 228, 160)]                                            # herba seca, joncs grocs
CLAY = [(36, 24, 16), (62, 42, 26), (92, 64, 38), (124, 90, 54), (156, 120, 74), (186, 152, 100), (210, 182, 132),
        (230, 210, 168), (244, 232, 202)]                           # el fang sec, clar de sol
GREENL = [(14, 26, 12), (24, 44, 18), (38, 66, 24), (56, 90, 32), (80, 118, 40), (110, 146, 52), (146, 176, 70),
          (186, 206, 104)]                                          # verd de fulla viva, de dia
WATER = [(10, 30, 40), (16, 48, 60), (26, 70, 84), (40, 96, 110), (62, 126, 138), (98, 162, 170), (150, 202, 206),
         (214, 238, 236)]
CLOTH = {                                                          # roba de la gent del poble (de lluny)
    'vermell': [(40, 10, 10), (90, 24, 20), (140, 40, 30), (186, 64, 44), (222, 100, 70)],
    'blau': [(10, 18, 40), (20, 36, 76), (36, 60, 114), (60, 90, 150), (100, 130, 186)],
    'verd': [(14, 28, 16), (26, 50, 28), (42, 76, 40), (64, 104, 56), (96, 136, 80)],
    'ocre': [(40, 24, 8), (84, 54, 18), (130, 88, 30), (176, 124, 46), (214, 166, 76)],
    'gris': [(24, 24, 28), (48, 48, 54), (78, 78, 86), (112, 112, 120), (152, 152, 158)],
    'lila': [(30, 16, 40), (60, 34, 78), (94, 58, 116), (132, 92, 154), (172, 136, 190)],
    'groc': [(50, 40, 8), (110, 86, 16), (170, 136, 30), (214, 180, 54), (240, 214, 110)],
    'blanc': [(110, 112, 118), (156, 158, 164), (196, 198, 204), (226, 228, 232), (246, 246, 248)],
}
SKINS = [[(60, 34, 26), (110, 68, 50), (160, 108, 80), (206, 152, 118), (236, 192, 160)],
         [(44, 24, 18), (82, 48, 34), (124, 80, 56), (164, 114, 80), (198, 148, 110)],
         [(64, 38, 30), (120, 78, 60), (176, 124, 96), (222, 172, 138), (244, 210, 182)]]
HAIRS = [[(10, 8, 8), (30, 20, 16), (54, 36, 26)], [(40, 26, 14), (80, 54, 28), (120, 84, 44)],
         [(120, 116, 112), (170, 166, 160), (214, 210, 204)], [(70, 30, 14), (120, 56, 24), (170, 90, 40)]]

# ─── Soroll de valors ràpid (taula precalculada, el de la mostra) ───────────
_T = [random.Random(s).random() for s in range(256 * 256)]


def _h(i, j, seed):
    return _T[((i * 73 + seed * 151) & 255) * 256 + ((j * 37 + seed * 59) & 255)]


def vn(u, v, seed=0):
    x0, y0 = math.floor(u), math.floor(v)
    fx, fy = u - x0, v - y0
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a, b = _h(x0, y0, seed), _h(x0 + 1, y0, seed)
    c, d = _h(x0, y0 + 1, seed), _h(x0 + 1, y0 + 1, seed)
    return a + (b - a) * fx + (c - a) * fy + (a - b - c + d) * fx * fy


def fbm(u, v, seed=0, octaves=3):
    s, amp, tot = 0.0, 1.0, 0.0
    for o in range(octaves):
        s += vn(u * (1 << o), v * (1 << o), seed + o * 17) * amp
        tot += amp
        amp *= 0.5
    return s / tot


def hr(*a):
    """Soroll determinista (0..1) a partir d'enters."""
    return _h(a[0] if a else 0, a[1] if len(a) > 1 else 0, a[2] if len(a) > 2 else 0)


def esquerda(u, v, seed=0):
    """Esquerdes del fang (soroll de cel·les): → distància a la vora de la cel·la més propera (0 = a l'esquerda)."""
    iu, iv = math.floor(u), math.floor(v)
    d1 = d2 = 9.0
    for j in (-1, 0, 1):
        for i in (-1, 0, 1):
            cu, cv = iu + i, iv + j
            px = cu + 0.15 + 0.7 * _h(cu, cv, seed)
            py = cv + 0.15 + 0.7 * _h(cu, cv, seed + 7)
            d = (px - u) ** 2 + (py - v) ** 2
            if d < d1:
                d1, d2 = d, d1
            elif d < d2:
                d2 = d
    return math.sqrt(d2) - math.sqrt(d1)


def boira_px(cv, x, y, col, k):
    """La calitja: barreja el píxel (x, y) ja pintat cap a `col` (k = 0..1)."""
    if 0 <= x < cv.w and 0 <= y < cv.h and k > 0:
        o = cv.P[int(x), int(y)]
        cv.P[int(x), int(y)] = mix(o, col, min(1.0, k)) + (o[3],)


def smooth(a, b, t):
    """0 fins a `a`, 1 des de `b`, suau entremig (amb a > b, al revés)."""
    if a > b:
        return 1.0 - smooth(b, a, t)
    if t <= a:
        return 0.0
    if t >= b:
        return 1.0
    t = (t - a) / (b - a)
    return t * t * (3 - 2 * t)


# ─── El terra en perspectiva ────────────────────────────────────────────────

class Terra:
    """Càmera d'exterior sense picat: horitzó a `hor`, ulls a `h` unitats del terra, focal `f`, centre a x = 320."""

    def __init__(self, hor, h, f=500.0, cx=320.0):
        self.hor, self.h, self.f, self.cx = hor, h, f, cx

    def z(self, v):
        return self.f * self.h / max(0.01, v - self.hor)

    def mon(self, u, v):
        """Un píxel del terra → (x, z) del món."""
        z = self.z(v)
        return (u - self.cx) * z / self.f, z

    def pant(self, x, z, y=0.0):
        """Un punt del món → (u, v) de pantalla."""
        return self.cx + self.f * x / z, self.hor + self.f * (self.h - y) / z

    def escala(self, v):
        return (v - self.hor) / self.h

    def k(self, z):
        """Píxels per unitat a la profunditat z."""
        return self.f / z


# ─── Lletra petita (la de la casa, a escala k i amb biaix) ──────────────────

EXTRA = {'%': ['101', '001', '010', '100', '101'], '?': ['110', '001', '010', '000', '010'],
         '—': ['0000', '0000', '1111', '0000', '0000']}


def _g(ch):
    return (EXTRA[ch], 0) if ch in EXTRA else _glyph(ch)


def lletres(cv, s, x, y, col, k=1, shear=0.0, kx=None):
    """Escriu `s` amb la font de 3×5 de la casa (accents i ce trencada inclosos), a escala k (kx: l'ample), amb el
    color pla `col`, o (rampa, nivell). `shear`: píxels de y per píxel de x (rètols en escorç). → l'amplada."""
    kx = kx or k
    cx = x
    for ch in s:
        g, top = _g(ch)
        for j, row in enumerate(g, start=top):
            for i, bit in enumerate(row):
                if bit != '1':
                    continue
                for dy in range(k):
                    for dx in range(kx):
                        px = cx + i * kx + dx
                        py = y + j * k + dy + round((px - x) * shear)
                        if isinstance(col[0], list):
                            cv.put(px, py, col[0], col[1], lit=0)
                        else:
                            cv.flat(px, py, col)
        cx += (len(g[0]) + 1) * kx
    return cx - x - kx


def ample(s, k=1):
    return sum((len(_g(ch)[0][0]) + 1) * k for ch in s) - k


# ─── Peces del bosc ─────────────────────────────────────────────────────────

def bezier(p0, p1, p2, t):
    a, b, c = (1 - t) ** 2, 2 * (1 - t) * t, t * t
    return a * p0[0] + b * p1[0] + c * p2[0], a * p0[1] + b * p1[1] + c * p2[1]


def arrel(cv, p0, p1, p2, r0, r1, ramp=BARK, base=3.6, seed=0, moss=True, lit=1.0):
    """Una arrel (o una branca): un tub que s'aprima de r0 a r1 seguint una corba, amb el llom il·luminat."""
    n = int(math.hypot(p2[0] - p0[0], p2[1] - p0[1]) * 1.2) + 4
    for i in range(n + 1):
        t = i / n
        x, y = bezier(p0, p1, p2, t)
        r = r0 + (r1 - r0) * t
        for yy in range(int(y - r - 1), int(y + r + 2)):
            for xx in range(int(x - r - 1), int(x + r + 2)):
                nx, ny = (xx - x) / max(r, 0.6), (yy - y) / max(r, 0.6)
                if nx * nx + ny * ny <= 1:
                    lvl = base - ny * 1.6 - nx * 0.5 + (fbm(xx / 3, yy / 7, seed) - 0.5) * 1.4
                    if moss and ny < -0.2 and fbm(xx / 9, yy / 9, seed + 5) > 0.56:
                        cv.put(xx, yy, MOSS, lvl + 0.4, lit)
                    else:
                        cv.put(xx, yy, ramp, lvl, lit)


def falguera(cv, x, y, ang, length, side=1, ramp=FERN, lvl=2.2, rim=None, seed=0):
    """Una fulla de falguera: un raquis corbat amb pínnules a banda i banda (per als primers plans foscos)."""
    rnd = random.Random(seed)
    px, py = x, y
    for i in range(int(length)):
        t = i / length
        a = ang + side * t * 0.9
        px += math.cos(a)
        py -= math.sin(a)
        cv.put(px, py, ramp, lvl, lit=0)
        if i % 3 == 0:
            pl = (1 - t) * length * 0.22 + 2
            for s in (-1, 1):
                pa = a + s * 1.1
                for k in range(int(pl)):
                    qx = px + math.cos(pa) * k
                    qy = py - math.sin(pa) * k + k * k * 0.03
                    cv.put(qx, qy, ramp, lvl + (1.8 if rim and s == rim and k > pl * 0.4 else 0) - k * 0.05, lit=0)
                    cv.put(qx, qy + 1, ramp, lvl - 0.4, lit=0)
        if rnd.random() < 0.02:
            ang += (rnd.random() - 0.5) * 0.2


def bolet(cv, x, y, h, r, glow=1.0, cap=TURQ, stem=CREAM):
    """Un bolet: el peu i el barret; amb `glow` > 0, bioluminescent (el barret és llum, no s'il·lumina)."""
    for yy in range(int(y - h), int(y) + 1):
        w = max(0.6, r * 0.28 * (1 + (y - yy) / max(h, 1) * 0.2))
        for xx in range(int(x - w), int(x + w) + 1):
            cv.put(xx, yy, stem, 2.6 - (xx - x) / max(w, 1) * 0.8 + glow * 1.2, lit=0.4)
    for yy in range(int(y - h - r * 0.7), int(y - h + 1) + 1):
        for xx in range(int(x - r), int(x + r) + 1):
            nx, ny = (xx - x) / r, (yy - (y - h)) / (r * 0.7)
            if nx * nx + ny * ny <= 1 and ny <= 0.25:
                cv.put(xx, yy, cap, 2.6 + glow * 2.6 - nx * 0.6 - ny * 1.2, lit=0 if glow else 1)
    if glow:
        cv.glow(x, y - h - r * 0.2, r * 4.0, GLOW_T, 0.55 * glow)


def ombra(cv, cx, cy, rx, ry, k=0.85):
    cv.darken(cx - rx - 2, cy - ry - 2, cx + rx + 2, cy + ry + 2,
              lambda x, y: k if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1 else 0)


def jonc(cv, x, y, h, ang, ramp=DRYG, lvl=3.6, gruix=1.0, lit=0.6, cap=True):
    """Un jonc: una tija prima que s'enfila de (x, y) amb inclinació `ang` (0 = dret; >0 cau cap a la dreta) i es
    corba; si `cap`, la panotxa fosca a dalt."""
    px, py = x, y
    n = int(h)
    for i in range(n):
        t = i / max(1, n)
        a = ang * (0.3 + 1.2 * t * t)
        px += math.sin(a)
        py -= math.cos(a)
        for g in range(int(math.ceil(gruix))):
            cv.put(px + g, py, ramp, lvl - t * 0.4 + (0.8 if g == 0 else 0), lit)
        if cap and 0.62 < t < 0.8:
            cv.put(px + 1, py, BARK, 3.0, lit)
            cv.put(px - 1, py, BARK, 2.4, lit)


def mata_joncs(cv, x, y, n, h, seed, caiguts=True, ramp=DRYG, lvl=3.4, escala=1.0, lit=0.6):
    """Una mata de joncs: `caiguts` (secs, grocs, doblegats) o drets (verds, quan torna l'aigua)."""
    rnd = random.Random(seed)
    for i in range(n):
        dx = (rnd.random() - 0.5) * 16 * escala
        hh = h * (0.6 + rnd.random() * 0.5)
        if caiguts:
            ang = (rnd.random() - 0.5) * 1.2 + (0.9 if rnd.random() < 0.5 else -0.9) * rnd.random()
        else:
            ang = (rnd.random() - 0.5) * 0.25
        jonc(cv, x + dx, y + rnd.random() * 2, hh, ang, ramp, lvl + (rnd.random() - 0.5) * 1.2,
             gruix=1 + (escala > 0.9), lit=lit, cap=rnd.random() < 0.5)


# ─── Arbres de fons i capçades ──────────────────────────────────────────────

def capcada(cv, x0, x1, y0, y1, seed, ramp=LEAVES, base=3.0, edge=0.42, lit=0.6, sx=30, sy=20, llum=(-0.4, -1.0),
            forma=None, ramp2=None, boira=None):
    """Una massa de fulles (soroll amb forats), il·luminada des de `llum` (en pantalla). `forma(x, y)` → el que se
    suma al llindar (0 al mig de la capçada, > 0 a les vores: així no queda la vora del rectangle). `ramp2`: una
    segona rampa (fulles d'un altre color) a taques. `boira`: (color, k) de la calitja."""
    for y in range(int(y0), int(y1)):
        for x in range(int(x0), int(x1)):
            e = edge + (forma(x, y) if forma else 0.0)
            f = fbm(x / sx, y / sy, seed, 4)
            if f > e:
                d = (f - e) * 9
                g = (fbm((x + 2 * llum[0]) / sx, (y + 2 * llum[1]) / sy, seed, 4) - f) * -30
                lvl = base + min(2.4, d) * 0.5 + g + (fbm(x / 3, y / 3, seed + 8) - 0.5) * 1.4
                r = ramp2 if ramp2 and fbm(x / 40, y / 30, seed + 3) > 0.55 else ramp
                cv.put(x, y, r, lvl, lit)
                if boira:
                    boira_px(cv, x, y, *boira)


def tronc(cv, cx, y0, y1, w0, w1, seed, ramp=BARK, base=3.0, lit=0.6, molsa=0.62):
    """Un tronc dret de cx, de y0 (dalt, ample w0) a y1 (baix, ample w1), amb llum de l'esquerra."""
    for y in range(int(y0), int(y1) + 1):
        t = (y - y0) / max(1, y1 - y0)
        w = w0 + (w1 - w0) * t ** 2.4
        c = cx + 3 * math.sin(y / 37 + seed)
        for x in range(int(c - w), int(c + w) + 1):
            u = (x - c) / max(w, 1)
            fis = fbm(u * 6 + seed, y / 26, seed + 41, 3)
            lvl = base - u * 1.3 - abs(u) ** 6 * 1.6 + (fis - 0.5) * 2.0 - (1.2 if fis < 0.35 else 0)
            if u < -0.1 and fbm(x / 7, y / 9, seed + 4) > molsa:
                cv.put(x, y, MOSS, lvl + 0.8, lit)
            else:
                cv.put(x, y, ramp, lvl, lit)


# ─── Gent del poble, de lluny (figures de fons, sense animar) ───────────────

def persona(cv, x, y, alt, seed, cara=1, polsera=True, gorra=False):
    """Una figura de fons de `alt` px amb els peus a (x, y), de cara (`cara` 1) o d'esquena (-1): el cap, els cabells,
    l'abric, els pantalons i les sabates, amb la llum de l'esquerra; i (`polsera`) una polsera de punts verd fluor."""
    rnd = random.Random(seed)
    roba = CLOTH[rnd.choice(('vermell', 'blau', 'verd', 'ocre', 'gris', 'lila', 'groc'))]
    cames = CLOTH[rnd.choice(('blau', 'gris', 'ocre', 'verd'))]
    pell = rnd.choice(SKINS)
    cabell = rnd.choice(HAIRS)
    s = alt / 70.0
    esp = (8.2 + rnd.random() * 1.6) * s                     # mitja amplada d'espatlles
    cap_r = 5.0 * s
    cy_cap = y - alt + cap_r + 0.5
    coll = cy_cap + cap_r + 0.5
    cintura = y - alt * 0.47
    abric = cintura + alt * (0.06 + rnd.random() * 0.12)     # on acaba l'abric
    # les cames (amb un forat entre totes dues) i les sabates
    for yy in range(int(cintura), int(y) + 1):
        for k in (-1, 1):
            cx = x + k * esp * 0.36
            w = max(1.0, esp * 0.3)
            for xx in range(int(cx - w), int(cx + w) + 1):
                u = (xx - cx) / w
                if yy >= y - 1.5 * s:
                    cv.put(xx + k * 0.5, yy, IRON_SHOE, 1.6 - u * 0.4, lit=0.4)
                else:
                    cv.put(xx, yy, cames, 2.4 - u * 0.8 - (0.6 if k > 0 else 0), lit=0.5)
    # el tronc (l'abric): les espatlles arrodonides, i s'eixampla una mica cap avall
    for yy in range(int(coll), int(abric) + 1):
        t = (yy - coll) / max(1.0, abric - coll)
        e = min(1.0, (yy - coll + 0.5) / (4.0 * s))           # les espatlles, arrodonides (un quart de cercle)
        sh = math.sqrt(max(0.0, 1 - (1 - e) ** 2))
        cint = 1.0 - 0.12 * math.sin(math.pi * min(1.0, t * 1.4))   # una mica de cintura
        vora = 1.0 - 0.25 * smooth(0.85, 1.0, t)                    # la vora de baix, arrodonida
        w = esp * (0.45 + 0.55 * sh) * cint * vora * (1.0 + 0.12 * t)
        for xx in range(int(round(x - w)), int(round(x + w)) + 1):
            u = (xx - x) / max(w, 1)
            lvl = 3.0 - u * 1.3 - t * 0.3 + math.sqrt(max(0.0, 1 - u * u)) * 0.6
            if u > 0.8:
                lvl -= 0.8                                        # el cantó de l'ombra
            cv.put(xx, yy, roba, lvl, lit=0.5)
    # els braços, separats del cos per una ratlla fosca
    for k in (-1, 1):
        for yy in range(int(coll + 2.5 * s), int(cintura + 3 * s)):
            t = (yy - coll) / max(1.0, cintura - coll)
            bx = x + k * (esp * (0.95 + 0.06 * t))                # el braç, una mica separat cap avall
            cv.put(bx, yy, roba, 2.4 - k * 0.7, lit=0.5)
            cv.put(bx + k, yy, roba, 1.8 - k * 0.7, lit=0.5)
            cv.put(bx - k, yy, roba, 1.0, lit=0.4)
        bx = x + k * esp * 1.01
        mx, my = bx, cintura + 3 * s
        cv.put(mx, my, pell, 2.8 - k * 0.4, lit=0.5)
        cv.put(mx, my + 1, pell, 2.2, lit=0.5)
        if polsera and k == 1:
            cv.flat(mx, my - 1, (150, 255, 110))
            cv.flat(mx - 1, my - 1, (90, 220, 70))
    # el cap
    cv.disc(x, cy_cap, cap_r, cap_r * 1.12, pell, lambda nx, ny: 3.2 - nx * 0.9 - ny * 0.4, lit=0.5)
    if cara < 0:                                                  # d'esquena: tot cabell (i potser una cua)
        cv.disc(x, cy_cap - 0.3, cap_r + 0.5, cap_r * 1.12, cabell, lambda nx, ny: 1.8 - nx * 0.7 - ny * 0.5, lit=0.5)
        if rnd.random() < 0.4:
            cv.rect(x - 1, cy_cap + cap_r * 0.6, x, cy_cap + cap_r * 1.8, cabell, 1.2, lit=0.5)
    else:
        cv.disc(x, cy_cap - cap_r * 0.4, cap_r + 0.5, cap_r * 0.8, cabell,
                lambda nx, ny: (1.8 - nx * 0.7) if ny < 0.2 else -9, lit=0.5)
        cv.flat(x - cap_r * 0.4, cy_cap + 0.6, (30, 20, 20))
        cv.flat(x + cap_r * 0.4, cy_cap + 0.6, (30, 20, 20))
    if gorra:
        g = CLOTH['vermell']
        cv.disc(x, cy_cap - cap_r * 0.5, cap_r + 0.6, cap_r * 0.6, g, lambda nx, ny: 2.8 - nx * 0.6 if ny < 0.3 else -9,
                lit=0.5)


IRON_SHOE = [(10, 8, 8), (24, 20, 18), (40, 34, 30), (60, 52, 46)]


# ─── Capes del davant i fotogrames ──────────────────────────────────────────

def diferencia(frame, base):
    """El que canvia d'un fotograma respecte del fons (la resta, transparent)."""
    out = Image.new('RGBA', frame.size, (0, 0, 0, 0))
    f, b, o = frame.load(), base.load(), out.load()
    for y in range(frame.size[1]):
        for x in range(frame.size[0]):
            if f[x, y] != b[x, y]:
                o[x, y] = f[x, y]
    return out


def mascara(img):
    """→ fn(x, y): el píxel és pintat a la capa `img` (RGBA, transparent on no hi ha res)."""
    a = img.getchannel('A').load()

    def m(x, y):
        return a[x, y] > 0
    return m


def capa_transparent():
    return Canvas(W, H, transparent=True)
