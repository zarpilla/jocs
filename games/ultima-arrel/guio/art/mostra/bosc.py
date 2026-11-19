"""
L'Última Arrel — peces comunes de les mostres d'art: rampes, soroll ràpid, lletres petites, arrels, falgueres,
bolets i filaments del Miceli.

Les sales es dibuixen a 640×288 (el que es veu en un mòbil; en un monitor, a sota hi ha la franja del HUD), amb la
llibreria de pixel art de Ni un ou (hd/pix.py: rampes fosc → clar, llum, dithering).
"""
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
GAMES = HERE.parents[3]
sys.path.insert(0, str(GAMES / 'ni-un-ou/adapters/benne/tools'))
sys.path.insert(0, str(HERE))

from pixels import nearest  # noqa: E402,F401
from hd.pix import Canvas, Light, mix  # noqa: E402,F401

W, H = 640, 288

# ─── Rampes (fosc → clar) ───────────────────────────────────────────────────
# El bosc viu: càlid.
DUSK = [(30, 24, 56), (46, 34, 74), (68, 44, 90), (98, 56, 98), (134, 72, 96), (172, 92, 88), (206, 120, 86),
        (232, 156, 98), (246, 194, 130), (252, 226, 172)]
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
STONE = [(22, 20, 22), (38, 36, 36), (58, 54, 52), (80, 76, 70), (104, 98, 90), (130, 124, 112), (158, 152, 138)]
FERN = [(4, 6, 4), (8, 12, 8), (14, 20, 12), (22, 30, 16), (34, 42, 22), (52, 58, 30), (80, 76, 40)]
CREAM = [(70, 58, 50), (120, 104, 86), (170, 154, 128), (210, 196, 166), (236, 226, 198), (250, 244, 224)]
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

# ─── Soroll de valors ràpid (taula precalculada) ────────────────────────────
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


# ─── Lletres de 3×5 ─────────────────────────────────────────────────────────
GLYPH = {
    'A': '010101111101101', 'B': '110101110101110', 'C': '011100100100011', 'D': '110101101101110',
    'E': '111100110100111', 'G': '011100101101011', 'I': '111010010010111', 'L': '100100100100111',
    'M': '101111111101101', 'N': '110101101101101', 'O': '010101101101010', 'P': '110101110100100',
    'R': '110101110101101', 'S': '011100010001110', 'T': '111010010010010', 'U': '101101101101111',
    '0': '010101101101010', '2': '110001010100111', '.': '000000000000010', ':': '000010000010000',
    ' ': '000000000000000', '+': '000010111010000',
}


def text(cv, s, x, y, col, k=1, shear=0.0):
    """Escriu `s` a (x, y) amb lletres de 3×5 a escala k; `shear`: px de y per px de x (rètols en escorç)."""
    x0 = x
    for ch in s:
        g = GLYPH[ch]
        for j in range(5):
            for i in range(3):
                if g[j * 3 + i] == '1':
                    for dy in range(k):
                        for dx in range(k):
                            px = x + i * k + dx
                            cv.flat(px, y + j * k + dy + round((px - x0) * shear), col)
        x += 4 * k
    return x


def text_width(s, k=1):
    return len(s) * 4 * k - k


# ─── Peces del bosc ─────────────────────────────────────────────────────────

def bezier(p0, p1, p2, t):
    a = (1 - t) ** 2
    b = 2 * (1 - t) * t
    c = t * t
    return a * p0[0] + b * p1[0] + c * p2[0], a * p0[1] + b * p1[1] + c * p2[1]


def arrel(cv, p0, p1, p2, r0, r1, ramp=BARK, base=3.6, seed=0, moss=True, owner=None):
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
                        cv.put(xx, yy, MOSS, lvl + 0.4)
                    else:
                        cv.put(xx, yy, ramp, lvl)
    return n


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
                lvl = 2.6 + glow * 2.6 - nx * 0.6 - ny * 1.2
                cv.put(xx, yy, cap, lvl, lit=0 if glow else 1)
    if glow:
        cv.glow(x, y - h - r * 0.2, r * 4.0, GLOW_T, 0.55 * glow)


def filament(cv, x, y, ang, length, seed, glow=1.0, branch=2, k=3.4, dim=False):
    """Un filament del Miceli: una línia que serpenteja i es ramifica, de llum turquesa (apagat: blau fosc)."""
    rnd = random.Random(seed)
    for i in range(int(length)):
        ang += (rnd.random() - 0.5) * 0.55
        x += math.cos(ang)
        y += math.sin(ang) * 0.6
        lvl = (k if not dim else 1.6) - i / length * 1.2
        cv.put(x, y, TURQ, lvl, lit=0)
        if glow and not dim and i % 9 == 0 and rnd.random() < 0.5:
            cv.glow(x, y, 5, GLOW_T, 0.35 * glow)
        if branch and rnd.random() < 0.035:
            filament(cv, x, y, ang + rnd.choice((-1, 1)) * 0.8, length * 0.4, seed * 7 + i, glow, branch - 1, k, dim)


def falguera(cv, x, y, ang, length, side=1, ramp=FERN, lvl=2.2, rim=None, seed=0):
    """Una fulla de falguera: un raquis corbat amb pínnules a banda i banda (per als primers plans foscos)."""
    rnd = random.Random(seed)
    px, py = x, y
    for i in range(int(length)):
        t = i / length
        a = ang + side * t * 0.9
        px += math.cos(a)
        py -= math.sin(a)
        cv.put(px, py, ramp, lvl)
        if i % 3 == 0:
            pl = (1 - t) * length * 0.22 + 2
            for s in (-1, 1):
                pa = a + s * 1.1
                for k in range(int(pl)):
                    qx = px + math.cos(pa) * k
                    qy = py - math.sin(pa) * k + k * k * 0.03
                    cv.put(qx, qy, ramp, lvl + (1.8 if rim and s == rim and k > pl * 0.4 else 0) - k * 0.05)
                    cv.put(qx, qy + 1, ramp, lvl - 0.4)
        if rnd.random() < 0.02:
            ang += (rnd.random() - 0.5) * 0.2


def ombra(cv, cx, cy, rx, ry, k=0.85):
    cv.darken(cx - rx - 2, cy - ry - 2, cx + rx + 2, cy + ry + 2,
              lambda x, y: k if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1 else 0)
