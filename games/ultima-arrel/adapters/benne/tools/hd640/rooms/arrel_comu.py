"""
L'Última Arrel — peces comunes de l'art definitiu de la centraleta i del campament de les fades (i de qui les
vulgui): les rampes del bosc i de NaturaPlus, el soroll ràpid, les lletres grosses (la font del joc, amb escorç),
arrels, branques, bolets, filaments del Miceli, falgueres i fulles.

Ve de les mostres d'estil (guio/art/mostra/bosc.py), passat a la llibreria de la casa (hd.pix a 640×360).
"""
import math
import random

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)

from hd.pix import B4, mix  # noqa: F401
from hd.rooms.comu import _diff  # noqa: F401
from hd640.font import GLYPHS as GLYPHS_GROS, SPACE

_BLANC = ['.' * SPACE]

BOTTOM = 259                   # la sala acaba aquí (a sota, el HUD)

# ─── Rampes (fosc → clar) ───────────────────────────────────────────────────
# El bosc viu: càlid.
BARK = [(14, 10, 10), (26, 18, 14), (42, 28, 20), (60, 40, 28), (82, 56, 36), (106, 74, 46), (132, 94, 58),
        (160, 118, 74), (188, 146, 96)]
MOSS = [(10, 18, 10), (20, 32, 16), (32, 48, 22), (48, 68, 30), (68, 90, 38), (92, 114, 50), (122, 142, 66),
        (156, 170, 88)]
EARTH = [(16, 12, 10), (30, 22, 16), (48, 34, 24), (68, 48, 32), (90, 64, 40), (114, 82, 50), (140, 102, 62),
         (166, 124, 78), (192, 150, 98)]
CLAY = [(14, 8, 8), (26, 16, 12), (42, 26, 18), (62, 40, 26), (86, 56, 34), (112, 76, 44), (140, 98, 58),
        (170, 124, 76), (204, 158, 104), (236, 200, 146)]
LEAF = [(70, 26, 12), (116, 44, 18), (164, 72, 24), (206, 108, 38), (236, 150, 62), (250, 194, 110)]
PLANK = [(22, 12, 8), (40, 24, 14), (62, 38, 20), (88, 56, 28), (116, 76, 38), (144, 98, 50), (172, 124, 66),
         (200, 152, 88), (226, 184, 120)]
IRONK = [(8, 8, 10), (18, 18, 22), (32, 30, 34), (50, 48, 52), (74, 70, 72)]
STONE = [(22, 20, 22), (38, 36, 36), (58, 54, 52), (80, 76, 70), (104, 98, 90), (130, 124, 112), (158, 152, 138)]
FERN = [(4, 6, 4), (8, 12, 8), (14, 20, 12), (22, 30, 16), (34, 42, 22), (52, 58, 30), (80, 76, 40)]
CREAM = [(70, 58, 50), (120, 104, 86), (170, 154, 128), (210, 196, 166), (236, 226, 198), (250, 244, 224)]
COPPER = [(40, 16, 10), (80, 34, 18), (124, 58, 30), (168, 88, 46), (210, 126, 70), (240, 172, 110)]
LAMPW = [(80, 50, 20), (150, 100, 40), (210, 160, 80), (245, 210, 140), (255, 240, 200), (255, 252, 236)]
# El bosc de dia: el verd de les fulles al sol del matí.
GREEN = [(10, 22, 12), (18, 38, 18), (28, 58, 24), (42, 82, 30), (62, 108, 36), (90, 136, 44), (124, 164, 56),
         (164, 192, 78), (204, 218, 120), (236, 240, 176)]
OAK = [(20, 14, 10), (36, 26, 18), (56, 40, 28), (78, 58, 40), (102, 78, 54), (128, 100, 70), (154, 124, 88),
       (180, 150, 110), (206, 180, 138), (228, 208, 168)]
# La xarxa: blau i turquesa bioluminescent.
TURQ = [(4, 20, 26), (6, 40, 48), (10, 70, 78), (20, 108, 112), (40, 150, 150), (80, 200, 192), (150, 240, 226),
        (220, 255, 248)]
GLOW_T = (110, 236, 220)
# NaturaPlus: fred, pla, artificial.
PLASTIC = [(60, 66, 80), (96, 104, 118), (136, 142, 156), (176, 182, 192), (210, 214, 222), (234, 236, 242),
           (250, 251, 253)]
NEON = [(8, 34, 10), (20, 80, 20), (50, 150, 40), (110, 220, 70), (180, 252, 130), (230, 255, 200)]
REDL = [(40, 6, 4), (100, 16, 8), (180, 34, 14), (240, 70, 30), (255, 140, 90), (255, 210, 180)]
PINKF = [(70, 10, 40), (130, 20, 80), (200, 40, 130), (246, 80, 172), (255, 140, 210), (255, 200, 236)]
BERRY = [(26, 6, 22), (48, 10, 40), (74, 18, 60), (102, 28, 82), (132, 44, 104)]
YELLOWP = [(60, 40, 6), (120, 84, 10), (190, 140, 20), (236, 190, 40), (252, 226, 110), (255, 246, 190)]

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
    return _h(int(a[0]) if a else 0, int(a[1]) if len(a) > 1 else 0, int(a[2]) if len(a) > 2 else 0)


# ─── Lletres grosses (la font del joc: 9 px d'alt les majúscules) ────────────

def ample(s, k=1, kx=None):
    kx = kx or k
    return sum((len(GLYPHS_GROS.get(ch, _BLANC)[0]) + 1) * kx for ch in s) - kx


def lletres(cv, s, x, y, col, k=1, kx=None, shear=0.0, wobble=0.0, seed=0, ramp=None, lvl=None, esp=0):
    """Escriu `s` a (x, y) (cantó de dalt a l'esquerra) amb la font del joc, a escala `k` (`kx` d'ample).
    `shear`: px de y per px de x (rètols en escorç o pintats de biaix); `wobble`: tremolor de pintada a mà.
    `col`: un color pla, o bé `ramp` + `lvl` (amb la llum de la sala). `esp`: espai de més entre lletres (per al
    traç gruixut)."""
    kx = kx or k
    cx = x
    for n, ch in enumerate(s):
        g = GLYPHS_GROS.get(ch, _BLANC)
        dy0 = (hr(n, 3, seed) - 0.5) * 2 * wobble
        for j, row in enumerate(g):
            for i, bit in enumerate(row):
                if bit != '#':
                    continue
                for yy in range(k):
                    for xx in range(kx):
                        px = cx + i * kx + xx
                        py = y + j * k + yy + round((px - x) * shear + dy0)
                        if ramp is not None:
                            cv.put(px, py, ramp, lvl, lit=1.0)
                        else:
                            cv.flat(px, py, col)
        cx += (len(g[0]) + 1) * kx + esp
    return cx


# ─── Peces del bosc ─────────────────────────────────────────────────────────

def bezier(p0, p1, p2, t):
    a, b, c = (1 - t) ** 2, 2 * (1 - t) * t, t * t
    return a * p0[0] + b * p1[0] + c * p2[0], a * p0[1] + b * p1[1] + c * p2[1]


def arrel(cv, p0, p1, p2, r0, r1, ramp=BARK, base=3.6, seed=0, moss=True, lit=1.0, llum=(0.5, 1.6)):
    """Una arrel (o una branca): un tub que s'aprima de r0 a r1 seguint una corba, amb el llom il·luminat.
    `llum` = (pes de x, pes de y) de la llum: (0.5, 1.6), de dalt i una mica de l'esquerra."""
    n = int(math.hypot(p2[0] - p0[0], p2[1] - p0[1]) * 1.2) + 4
    lx, ly = llum
    for i in range(n + 1):
        t = i / n
        x, y = bezier(p0, p1, p2, t)
        r = r0 + (r1 - r0) * t
        for yy in range(int(y - r - 1), int(y + r + 2)):
            for xx in range(int(x - r - 1), int(x + r + 2)):
                nx, ny = (xx - x) / max(r, 0.6), (yy - y) / max(r, 0.6)
                if nx * nx + ny * ny <= 1:
                    lvl = base - ny * ly - nx * lx + (fbm(xx / 3, yy / 7, seed) - 0.5) * 1.4
                    if moss and ny < -0.2 and fbm(xx / 9, yy / 9, seed + 5) > 0.56:
                        cv.put(xx, yy, MOSS, lvl + 0.4, lit)
                    else:
                        cv.put(xx, yy, ramp, lvl, lit)
    return n


def bolet(cv, x, y, h, r, glow=1.0, cap=TURQ, stem=CREAM, lit=1.0):
    """Un bolet: el peu i el barret; amb `glow` > 0, bioluminescent (el barret és llum, no s'il·lumina)."""
    for yy in range(int(y - h), int(y) + 1):
        w = max(0.6, r * 0.28 * (1 + (y - yy) / max(h, 1) * 0.2))
        for xx in range(int(x - w), int(x + w) + 1):
            cv.put(xx, yy, stem, 2.6 - (xx - x) / max(w, 1) * 0.8 + glow * 1.2, lit=0.4 * lit)
    for yy in range(int(y - h - r * 0.7), int(y - h + 1) + 1):
        for xx in range(int(x - r), int(x + r) + 1):
            nx, ny = (xx - x) / r, (yy - (y - h)) / (r * 0.7)
            if nx * nx + ny * ny <= 1 and ny <= 0.25:
                lvl = 2.6 + glow * 2.6 - nx * 0.6 - ny * 1.2
                cv.put(xx, yy, cap, lvl, lit=0 if glow else lit)
    if glow:
        cv.glow(x, y - h - r * 0.2, r * 4.0, GLOW_T, 0.55 * glow)


def filament(cv, x, y, ang, length, seed, glow=1.0, branch=2, k=3.4, dim=False, sostre=None, evita=None, cap=None):
    """Un filament del Miceli: una línia que serpenteja i es ramifica, de llum turquesa (apagat: blau fosc).
    Torna els punts per on passa. `sostre`: la y on s'atura (no puja més). (Apagat o encès, el camí és el mateix.)"""
    rnd = random.Random(seed)
    pts = []
    for i in range(int(length)):
        ang += (rnd.random() - 0.5) * 0.55
        if cap is not None:                                 # (la direcció cap on tiba: puja cap al sostre)
            ang += (cap - ang) * 0.06
        x += math.cos(ang)
        y += math.sin(ang) * 0.6
        if sostre is not None and y < sostre:
            break
        pts.append((x, y))
        lvl = (k if not dim else 1.7) - i / length * (1.2 if not dim else 0.4)
        amagat = evita is not None and evita(x, y)
        if cv is not None and not amagat:
            cv.put(x, y, TURQ, lvl, lit=0)
        g = rnd.random() if i % 9 == 0 else 1.0
        if cv is not None and glow and not dim and g < 0.5 and not amagat:
            cv.glow(x, y, 5, GLOW_T, 0.35 * glow)
        if branch and rnd.random() < 0.035:
            pts += filament(cv, x, y, ang + rnd.choice((-1, 1)) * 0.8, length * 0.4, seed * 7 + i, glow, branch - 1,
                            k, dim, sostre, evita, cap)
    return pts


def falguera(cv, x, y, ang, length, side=1, ramp=FERN, lvl=2.2, rim=None, seed=0, lit=0.0):
    """Una fulla de falguera: un raquis corbat amb pínnules a banda i banda (per als primers plans foscos)."""
    rnd = random.Random(seed)
    px, py = x, y
    for i in range(int(length)):
        t = i / length
        a = ang + side * t * 0.9
        px += math.cos(a)
        py -= math.sin(a)
        cv.put(px, py, ramp, lvl, lit)
        if i % 3 == 0:
            pl = (1 - t) * length * 0.22 + 2
            for s in (-1, 1):
                pa = a + s * 1.1
                for k in range(int(pl)):
                    qx = px + math.cos(pa) * k
                    qy = py - math.sin(pa) * k + k * k * 0.03
                    cv.put(qx, qy, ramp, lvl + (1.8 if rim and s == rim and k > pl * 0.4 else 0) - k * 0.05, lit)
                    cv.put(qx, qy + 1, ramp, lvl - 0.4, lit)
        if rnd.random() < 0.02:
            ang += (rnd.random() - 0.5) * 0.2


def fulla_roure(cv, cx, cy, ang, mida, ramp=GREEN, lvl=4.0, lit=1.0, seed=0, vores=True, llum=None):
    """Una fulla de roure (lobulada), centrada a (cx, cy), girada `ang` (radiants; 0 = la punta a la dreta), de
    llargada `mida`. `llum(nx, ny)` → nivells que s'hi sumen (si no, de dalt a l'esquerra)."""
    ca, sa = math.cos(ang), math.sin(ang)
    L, Wd = mida / 2, mida * 0.32
    R = int(L + 2)
    for yy in range(int(cy - R), int(cy + R) + 1):
        for xx in range(int(cx - R), int(cx + R) + 1):
            dx, dy = xx - cx, yy - cy
            u = (dx * ca + dy * sa) / L                     # al llarg (-1 = el pecíol, 1 = la punta)
            v = (-dx * sa + dy * ca) / Wd                   # de través
            if abs(u) > 1:
                continue
            perfil = math.sqrt(max(0.0, 1 - u * u)) * (0.78 + 0.22 * math.cos(u * math.pi * 3.5 + 0.6))
            if abs(v) > perfil:
                continue
            nerv = abs(v) < 0.09 and u < 0.85
            k = lvl + (llum(dx / R, dy / R) if llum else (-dx * 0.4 - dy * 0.6) / R)
            k += (0.5 if v < 0 else -0.3)                   # una meitat més clara: la fulla no és plana
            if vores and abs(v) > perfil - 0.18:
                k -= 0.9
            if nerv:
                k += 0.8
            k += (hr(xx, yy, seed) - 0.5) * 0.5
            cv.put(xx, yy, ramp, k, lit)


def ombra(cv, cx, cy, rx, ry, k=0.85):
    cv.darken(cx - rx - 2, cy - ry - 2, cx + rx + 2, cy + ry + 2,
              lambda x, y: k if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1 else 0)


def hud_negre(cv):
    """A sota de la sala, el HUD: negre."""
    cv.rect(0, BOTTOM + 1, cv.w - 1, cv.h - 1, [(0, 0, 0)], 0, lit=0)


def sense(img, mask_img):
    """`img` sense els píxels que `mask_img` (RGBA) té pintats: el que canvia un decorat no ha de tapar el primer pla."""
    import numpy as np
    from PIL import Image
    a = np.asarray(img.convert('RGBA')).copy()
    m = np.asarray(mask_img.convert('RGBA'))[..., 3] > 0
    a[m] = 0
    return Image.fromarray(a, 'RGBA')
