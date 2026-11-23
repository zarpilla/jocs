"""
L'Última Arrel — peces comunes de les sales de dia: `toll_gripaus`, `caseta_obra` i `zona_zero`.

Ve de les mostres d'art aprovades (guio/art/mostra/bosc.py): les mateixes rampes (fosc → clar) del bosc càlid i de
NaturaPlus, freda i plana, amb unes quantes de més per a la llum de dia (el fang sec, els joncs, l'aigua, el cel), el
soroll ràpid, la lletra petita, les arrels, les falgueres i els filaments del Miceli.

I, a més, el terra en perspectiva dels exteriors (`Terra`): una càmera a l'alçada dels ulls d'un adult (sense picat:
les verticals, verticals), amb l'horitzó a `hor`. Un punt del terra a la fila v de pantalla és a la profunditat
z = f·h / (v − hor), i un personatge que hi té els peus fa (v − hor) / h: l'escala és exacta i lineal en v.

1 unitat del món = 1 píxel de sala a l'escala 1 dels personatges (l'Iri hi fa ≈72 px).
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

def persona(cv, x, y, alt, seed, cara=1, polsera=True, gorra=False, sol=(-0.8, -0.35), ombra_llarga=(0.7, 0.1)):
    """Una figura de fons de `alt` px amb els peus a (x, y), de cara (`cara` 1) o d'esquena (-1), amb volum: la llum
    rasant de `sol` (de l'esquerra: la vora encesa, l'ombra pròpia a la dreta), plecs, braços i cames com a tubs,
    sabates, un contorn fosc al cantó de l'ombra i l'ombra llarga a terra (`ombra_llarga`: cap on va, per alçada).
    D'esquena, el cap es gira cap a la dreta (cap a l'escenari): se'n veu l'orella i un tros de galta. Cada figura
    (segons `seed`) té la seva complexió, roba i complements: faldilla, motxilla, bufanda, gorro, boina, caputxa, o el
    mòbil enlaire (gravant: d'esquena, se'n veu la pantalla encesa). `gorra`: la gorra vermella. `polsera`: la
    polsera de punts verd fluor."""
    rnd = random.Random(seed)
    roba = CLOTH[rnd.choice(('vermell', 'blau', 'verd', 'ocre', 'gris', 'lila', 'groc'))]
    cames = CLOTH[rnd.choice(('blau', 'gris', 'ocre', 'verd'))]
    pell = rnd.choice(SKINS)
    cabell = rnd.choice(HAIRS)
    s = alt / 70.0
    build = 0.85 + rnd.random() * 0.4
    esp = 8.4 * s * build                                    # mitja amplada d'espatlles
    cap_r = 5.6 * s
    hy = y - alt + cap_r * 1.1
    coll = hy + cap_r * 1.05
    cintura = y - alt * 0.47
    faldilla = rnd.random() < 0.22
    abric = cintura + alt * (0.04 + rnd.random() * 0.16) + (alt * 0.12 if faldilla else 0)
    extra = rnd.choice(('res', 'res', 'motxilla', 'bufanda', 'gorro', 'boina', 'caputxa', 'mobil'))
    tmp = Canvas(cv.w, cv.h, transparent=True)
    # a tons plans, com els fulls dels personatges (sense el tramat de la llum): cada nivell, a la seva banda
    tmp.put = lambda xx, yy, ramp, lvl, lit=0: Canvas.put(tmp, xx, yy, ramp, math.floor(lvl + 0.6) + 0.5, 0)
    lx, ly = sol

    def ll(nx, ny=0.0):
        """La llum d'una superfície amb normal (nx, ny) de pantalla (el volum: 0 a l'ombra … 1 de cara al sol)."""
        nz = math.sqrt(max(0.0, 1 - nx * nx - ny * ny))
        return max(0.0, nx * lx + ny * ly + nz * 0.35)

    def tub(x0, y0, x1, y1, r0, r1, ramp, base, fosc=0.0, sep=0):
        """Un tub (un braç, una cama) de (x0, y0) a (x1, y1), amb el volum de la llum; `sep` (±1): el cantó que
        toca el cos, fosc (separa el braç del tronc)."""
        n = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 2
        for i in range(n + 1):
            t = i / n
            cx, cy = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            r = max(0.7, r0 + (r1 - r0) * t)
            for xx in range(int(cx - r - 1), int(cx + r + 2)):
                u = (xx + 0.5 - cx) / r
                if abs(u) <= 1:
                    lvl = base + 2.6 * ll(u) - fosc + (0.7 if u < -0.75 else 0)
                    if sep and u * sep > 0.6:
                        lvl = 0
                    tmp.put(xx, cy, ramp, lvl, lit=0.3)

    # ─ les cames (o la faldilla, fins més avall) i les sabates, de tres quarts cap a la dreta
    for k in (-1, 1):
        cx = x + k * esp * 0.34
        tub(cx, cintura, cx + k * 0.3 * s, y - 2 * s, esp * 0.3, esp * 0.22, cames, 0.6, fosc=0.5 if k > 0 else 0)
        for xx in range(int(cx - 2.4 * s), int(cx + 3.4 * s) + 1):
            for yy in range(int(y - 2.2 * s), int(y) + 1):
                nx, ny = (xx - cx - 0.5 * s) / (2.9 * s), (yy - y + 1 * s) / (1.4 * s)
                if nx * nx + ny * ny <= 1.15:
                    tmp.put(xx, yy, IRON_SHOE, 1.0 + 2.2 * ll(nx * 0.8, ny * 0.6), lit=0.3)
    # ─ el braç del costat de l'ombra (darrere el cos)
    mobil = extra == 'mobil'
    sx_d = x + esp * 0.92
    if mobil:                                                 # el braç dret enlaire, amb el mòbil
        hx, hyy = x + esp * 0.7, hy - cap_r * 1.6
        tub(sx_d, coll + 3 * s, hx, hyy + 2 * s, 2.0 * s, 1.5 * s, roba, 0.4, fosc=0.6)
    else:
        tub(sx_d, coll + 3 * s, sx_d + 0.6 * s, cintura + 2 * s, 2.1 * s, 1.7 * s, roba, 0.4, fosc=0.7)
    # ─ el tronc (l'abric o la jaqueta): espatlles arrodonides, una mica de cintura, i s'eixampla cap avall
    for yy in range(int(coll), int(abric) + 1):
        t = (yy - coll) / max(1.0, abric - coll)
        e = min(1.0, (yy - coll + 0.5) / (4.0 * s))
        sh = math.sqrt(max(0.0, 1 - (1 - e) ** 2))
        cint = 1.0 - 0.1 * math.sin(math.pi * min(1.0, t * 1.4)) * (1 if not faldilla else 1.4)
        vora = 1.0 - 0.2 * smooth(0.88, 1.0, t)
        w = esp * (0.45 + 0.55 * sh) * cint * vora * (1.0 + (0.1 if not faldilla else 0.3) * t)
        for xx in range(int(round(x - w)), int(round(x + w)) + 1):
            u = (xx + 0.5 - x) / max(w, 1)
            if abs(u) > 1.05:
                continue
            ny = -0.5 * (1 - sh) if e < 1 else 0.0                # les espatlles miren amunt
            lvl = 0.5 + 3.0 * ll(max(-1.0, min(1.0, u)), ny) + (0.6 if u < -0.82 else 0)
            # els plecs: dues ratlles fosques que baixen, i a l'abric obert, la tapeta
            for fu in (-0.35, 0.3):
                if abs(u - fu - math.sin(t * 3 + seed) * 0.05) < 0.07 and t > 0.45:
                    lvl -= 0.7
            if cara > 0 and abs(u - 0.05) < 0.06 and not faldilla:
                lvl -= 0.9
            if yy >= abric - 0.5:
                lvl -= 0.8                                       # la vora de baix
            tmp.put(xx, yy, roba, lvl, lit=0.4)
    # ─ la motxilla (d'esquena: damunt; de cara: les tires)
    if extra == 'motxilla':
        mc = CLOTH[rnd.choice(('vermell', 'verd', 'gris', 'groc'))]
        if cara < 0:
            for yy in range(int(coll + 3 * s), int(cintura + 1 * s)):
                for xx in range(int(x - esp * 0.6), int(x + esp * 0.6) + 1):
                    u = (xx + 0.5 - x) / (esp * 0.6)
                    v = (yy - coll - 3 * s) / max(1.0, cintura - coll - 2 * s)
                    if u * u + (2 * v - 1) ** 6 < 1:
                        tmp.put(xx, yy, mc, 0.8 + 2.8 * ll(u, 2 * v - 1) - (0.8 if abs(v - 0.55) < 0.05 else 0), lit=0.3)
        else:
            for k in (-1, 1):
                for yy in range(int(coll + 1), int(coll + 9 * s)):
                    tmp.put(x + k * esp * 0.5, yy, mc, 1.2, lit=0.3)
    # ─ el braç del costat del sol (davant)
    sx_e = x - esp * 0.92
    tub(sx_e, coll + 3 * s, sx_e - 0.5 * s, cintura + 2 * s, 2.2 * s, 1.8 * s, roba, 0.8, sep=1)
    for k, (hx_, hy_) in enumerate(((sx_e - 0.5 * s, cintura + 3.2 * s),
                                    (None, None) if mobil else (sx_d + 0.6 * s, cintura + 3.2 * s))):
        if hx_ is None:
            continue
        tmp.disc(hx_, hy_, 1.4 * s, 1.5 * s, pell, lambda nx, ny, k=k: 1.4 + 2.2 * ll(nx, ny) - k * 0.6, lit=0.3)
        if polsera and k == 1:
            tmp.flat(hx_, hy_ - 1.6 * s, (150, 255, 110))
            tmp.flat(hx_ - 1, hy_ - 1.6 * s, (90, 220, 70))
    if mobil:                                                 # el mòbil, i (d'esquena) la pantalla encesa
        px, py = x + esp * 0.7, hy - cap_r * 1.6
        tmp.rect(px - 2 * s, py - 4 * s, px + 2 * s, py + 1 * s, IRON_SHOE, 1.0, lit=0)
        if cara < 0:
            tmp.rect(px - 1.4 * s, py - 3.4 * s, px + 1.4 * s, py + 0.4 * s, [(170, 220, 240), (220, 245, 255)], 0.6,
                     lit=0)
        tmp.disc(px, py + 1.6 * s, 1.3 * s, 1.3 * s, pell, 2.6, lit=0.3)
    # ─ el coll: una ombra sota el cap, i la bufanda
    tmp.rect(x - cap_r * 0.45, coll - 1.4 * s, x + cap_r * 0.45, coll + 0.4 * s, pell, 0.6, lit=0.2)
    if extra == 'bufanda':
        bc = CLOTH[rnd.choice(('vermell', 'groc', 'lila', 'verd'))]
        for yy in range(int(coll - 1.5 * s), int(coll + 2.5 * s)):
            for xx in range(int(x - cap_r * 1.1), int(x + cap_r * 1.1) + 1):
                u = (xx + 0.5 - x) / (cap_r * 1.1)
                tmp.put(xx, yy, bc, 0.8 + 2.8 * ll(u) - (0.6 if (yy + xx) % 3 == 0 else 0), lit=0.3)
        for yy in range(int(coll + 2 * s), int(coll + 9 * s)):    # la punta que penja
            tmp.put(x - cap_r * 0.6 * cara, yy, bc, 2.4, lit=0.3)
            tmp.put(x - cap_r * 0.6 * cara + 1, yy, bc, 1.6, lit=0.3)
    # ─ el cap: una esfera, amb el cabell (d'esquena, girat cap a la dreta: l'orella i un tros de galta)
    tmp.disc(x, hy, cap_r, cap_r * 1.1, pell, lambda nx, ny: 0.8 + 3.0 * ll(nx, ny), lit=0.3)
    if cara < 0:
        def cab(nx, ny):
            if nx > 0.55 and ny > -0.25:                          # la galta i l'orella, cap a l'escenari
                return -9
            return 0.3 + 2.4 * ll(nx, ny) + (0.6 if fbm(nx * 3, ny * 5, seed) > 0.6 else 0)
        tmp.disc(x - 0.3 * s, hy - 0.3 * s, cap_r + 0.5, cap_r * 1.12, cabell, cab, lit=0.3)
        tmp.disc(x + cap_r * 0.62, hy + 0.4 * s, 0.9 * s, 1.4 * s, pell, lambda nx, ny: 1.6 - nx * 0.4, lit=0.3)
        if rnd.random() < 0.35 and extra not in ('caputxa', 'gorro'):          # una cua
            tub(x - 0.4 * s, hy + cap_r * 0.6, x - 0.6 * s, hy + cap_r * 1.9, 1.1 * s, 0.7 * s, cabell, 0.4)
    else:
        tmp.disc(x, hy - cap_r * 0.4, cap_r + 0.5, cap_r * 0.8, cabell,
                 lambda nx, ny: (0.4 + 2.2 * ll(nx, ny)) if ny < 0.2 else -9, lit=0.3)
        for ex in (0.05, 0.55):                                    # els ulls, mirant cap a l'escenari
            tmp.flat(x + cap_r * ex, hy + 0.6 * s, (30, 20, 20))
    # ─ els barrets
    if gorra:
        g = CLOTH['vermell']
        tmp.disc(x, hy - cap_r * 0.5, cap_r + 0.6, cap_r * 0.6, g, lambda nx, ny: 1.0 + 2.6 * ll(nx, ny) if ny < 0.3 else -9,
                 lit=0.3)
        tmp.rect(x + cap_r * 0.3, hy - cap_r * 0.25, x + cap_r * 1.5, hy - cap_r * 0.05, g, 1.4, lit=0.3)   # la visera
    elif extra == 'gorro':
        g = CLOTH[rnd.choice(('vermell', 'groc', 'blau', 'lila'))]
        tmp.disc(x, hy - cap_r * 0.35, cap_r + 0.7, cap_r * 0.85, g,
                 lambda nx, ny: (0.6 + 3.0 * ll(nx, ny) - (0.7 if int((nx + 1) * 4) % 2 else 0)) if ny < 0.25 else -9, lit=0.3)
        tmp.disc(x, hy - cap_r * 1.25, 1.5 * s, 1.4 * s, g, lambda nx, ny: 1.4 + 2.6 * ll(nx, ny), lit=0.3)     # la borla
    elif extra == 'boina':
        tmp.disc(x - 0.4 * s, hy - cap_r * 0.75, cap_r * 1.15, cap_r * 0.42, IRON_SHOE,
                 lambda nx, ny: 0.6 + 2.6 * ll(nx, ny), lit=0.3)
    elif extra == 'caputxa':
        for yy in range(int(hy - cap_r * 1.2), int(coll + 2 * s)):
            for xx in range(int(x - cap_r * 1.3), int(x + cap_r * 1.3) + 1):
                nx, ny = (xx + 0.5 - x) / (cap_r * 1.3), (yy - hy + 0.2 * s) / (cap_r * 1.25)
                if nx * nx + ny * ny <= 1 and (cara < 0 or nx * nx + (ny - 0.1) ** 2 > 0.5):
                    tmp.put(xx, yy, roba, 0.4 + 2.8 * ll(nx, ny) - (0.6 if nx * nx + ny * ny > 0.8 and cara > 0 else 0),
                            lit=0.3)
    # ─ el contorn, al cantó de l'ombra (a la dreta i a baix): separa la figura del fons
    T = tmp.img.load()
    x0b, x1b = int(x - esp * 2.2), int(x + esp * 2.2)
    y0b = int(y - alt - cap_r * 2)
    vores = []
    for yy in range(max(0, y0b), min(cv.h - 1, int(y) + 2)):
        for xx in range(max(1, x0b), min(cv.w - 1, x1b)):
            if T[xx, yy][3]:
                continue
            for dx, dy in ((-1, 0), (0, -1), (1, 0)):
                c = T[xx + dx, yy + dy] if 0 <= yy + dy < cv.h else (0, 0, 0, 0)
                if c[3] and (dx < 0 or dy < 0):
                    vores.append((xx, yy, c))
                    break
    for xx, yy, c in vores:
        T[xx, yy] = (int(c[0] * 0.35), int(c[1] * 0.3), int(c[2] * 0.3), 255)
    # ─ l'ombra llarga a terra, abans de la figura: una llengua que surt dels peus i s'aprima i s'esvaeix
    ox, oy = ombra_llarga
    L = alt * ox

    def om(xx, yy):
        t = (xx - x + esp * 0.5) / (L + esp * 0.5)
        if not 0 <= t <= 1:
            return 0
        yc = y + (xx - x) * oy / ox
        return 0.6 * (1 - t) ** 0.7 if abs(yy - yc) <= 2.2 * s * (1 - 0.6 * t) + 0.3 else 0
    cv.darken(x - esp, y - 4, x + L + 2, y + L * oy / ox + 4, om)
    cv.img.alpha_composite(tmp.img)
    cv.P = cv.img.load()


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
