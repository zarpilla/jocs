"""
Aigua Verne — el fons dels crèdits (pantalla sencera de 640×360, sense barra de verbs).

El sistema de Vesper de nit: l'estrella petita i taronja al cantó de baix a l'esquerra, i els quatre planetes al
voltant de la pantalla, petits, il·luminats per aquell cantó. Damunt de tres (Terra-2, Aqua i Ferrum) hi ha
núvols de pluja, gruixuts i grisos. Verdant, no: Verdant brilla net, amb el palau orbital, un punt daurat.
Entre Terra-2 i el centre, petita, la Cantimplora que hi torna. El mig de la pantalla queda fosc i net per al
text.

ANIMS: `pluja` (els fils de pluja damunt dels núvols dels tres planetes) i `estrelles` (algunes estrelles que fan
pampallugues).
"""
import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)

import functools
import math

from hd.pix import Canvas, Light, W, H, hr, mix
from hd.rooms.comu import _diff
from hd.rooms.exterior import fbm, smooth
from hd640.rooms.nau_comu import OLIVE, SAFETY, INK

STAR = (-40, 400)                        # Vesper, fora de la pantalla per baix a l'esquerra
LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)

_ANIM = {'pluja': None, 'estrelles': None}

SPACE = [(2, 2, 8), (5, 4, 14), (9, 7, 22), (14, 10, 30), (22, 14, 38), (34, 20, 44), (52, 28, 48),
         (76, 38, 48)]
T2 = [(20, 12, 10), (46, 30, 20), (82, 56, 36), (122, 88, 56), (160, 120, 78), (196, 154, 104), (226, 190, 140),
      (244, 220, 176)]
AQ = [(10, 18, 30), (24, 42, 64), (48, 78, 104), (86, 120, 146), (132, 164, 184), (180, 204, 218), (220, 234, 240),
      (246, 250, 252)]
FE = [(12, 8, 8), (30, 18, 16), (56, 32, 26), (86, 50, 36), (116, 70, 48), (148, 94, 64), (176, 122, 86),
      (204, 154, 116)]
VE = [(4, 30, 10), (8, 60, 18), (14, 100, 28), (24, 144, 40), (50, 190, 56), (110, 230, 90), (190, 255, 160),
      (240, 255, 230)]
CLOUD = [(30, 32, 40), (54, 58, 68), (84, 88, 98), (118, 122, 130), (156, 160, 166), (196, 198, 202),
         (228, 230, 232)]

# nom, centre, radi, rampa, pluja?
PLANETS = (
    ('verdant', (96, 58), 15, VE, False),
    ('terra2', (78, 196), 30, T2, True),
    ('aqua', (576, 92), 26, AQ, True),
    ('ferrum', (566, 286), 34, FE, True),
)


def space(cv, tw=None, star=None, planets=None):
    star = star or STAR
    planets = planets or PLANETS
    for y in range(H):
        for x in range(W):
            d = math.hypot(x - star[0], y - star[1])
            lvl = 0.6 + 3.4 * max(0.0, 1 - d / 420) ** 2.4
            neb = fbm(x / 110, y / 70, 91)
            lvl += smooth(0.5, 0.8, neb) * 1.6 * (0.4 + 0.6 * max(0.0, 1 - d / 600))
            cv.put(x, y, SPACE, lvl, lit=0)
            if hr(x, y, 92) > 0.9972:
                b = hr(x, y, 93)
                col = (220, 224, 240) if b > 0.7 else (140, 140, 170) if b > 0.3 else (90, 86, 120)
                if tw is not None and hr(x, y, 94 + tw) > 0.85:
                    col = (60, 56, 80)
                cv.flat(x, y, col)
                if b > 0.93:
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        cv.flat(x + dx, y + dy, mix(cv.get(x + dx, y + dy), (130, 130, 170), 0.5))
    # Vesper: la claror de l'estrella que treu el cap pel cantó
    cv.glow(star[0] + 40, star[1] - 40, 190, (255, 150, 70), 0.4)
    cv.glow(star[0] + 30, star[1] - 30, 120, (255, 210, 140), 0.5)
    sr = 96
    for y in range(star[1] - sr, H):
        for x in range(0, star[0] + sr + 1):
            d = math.hypot(x - star[0], y - star[1])
            if d <= sr:
                cv.put(x, y, [(200, 80, 20), (240, 130, 40), (255, 180, 80), (255, 220, 150), (255, 246, 220)],
                       4.2 - (d / sr) ** 3 * 3.0 + (fbm(x / 8, y / 8, 95) - 0.5) * 0.8, lit=0)
    # les òrbites: punts molt febles
    for _, (px, py), _, _, _ in planets:
        R = math.hypot(px - star[0], py - star[1])
        for a in range(0, 900):
            ang = a / 900 * math.pi / 2 * 1.02 - 0.01
            x, y = star[0] + math.cos(ang) * R, star[1] - math.sin(ang) * R
            if 0 <= x < W and 0 <= y < H and int(ang * R) % 7 == 0:
                cv.flat(x, y, mix(cv.get(x, y), (90, 70, 110), 0.5))


def planet(cv, name, c, r, ramp, rain, drops=None, star=None):
    star = star or STAR
    cx, cy = c
    lx, ly = star[0] - cx, star[1] - cy
    ln = math.hypot(lx, ly)
    lx, ly = lx / ln * 0.98, ly / ln * 0.98
    lz = 0.2
    seed = sum(map(ord, name))
    for y in range(int(cy - r - 3), int(cy + r + 4)):
        for x in range(int(cx - r - 3), int(cx + r + 4)):
            nx, ny = (x - cx) / r, (y - cy) / r
            d2 = nx * nx + ny * ny
            if d2 > 1:
                # l'atmosfera: una vora fina del costat de la llum
                if d2 < 1.18 and (nx * lx + ny * ly) > 0.2:
                    cv.flat(x, y, mix(cv.get(x, y), ramp[5], 0.35 * (1.18 - d2) / 0.18))
                continue
            nz = math.sqrt(1 - d2)
            lam = max(0.0, nx * lx + ny * ly + nz * lz)
            # la superfície: continents o taques segons el planeta
            u, v = nx / (nz + 0.6), ny / (nz + 0.6)
            n = fbm(u * 2.4 + 5, v * 2.4, seed)
            lvl = 0.7 + lam * 5.6 + (n - 0.5) * (2.2 if name != 'verdant' else 1.2) * (0.3 + lam)
            if name == 'verdant':
                lvl += 0.6 if (int((u + 3) * 6) % 2) else 0                     # els camps, en ratlles perfectes
            cv.put(x, y, ramp, lvl, lit=0)
            # els núvols de pluja: espirals gruixudes i grises
            if rain:
                # un front de tempesta: una banda espessa de núvols grisos que gira, i cúmuls arrodonits
                band = math.exp(-((v - 0.15 * math.sin(u * 3)) * 1.6) ** 2)
                cl = fbm(u * 2.0, v * 3.0, seed + 1) * 0.7 + band * 0.45
                k = smooth(0.5, 0.62, cl)
                if k > hr(x, y, seed) * 0.9 + 0.05:
                    bump = fbm(u * 7, v * 7, seed + 2)
                    cvl = 0.6 + lam * 4.4 + (bump - 0.5) * 2.0 - (1 - k) * 0.8
                    cv.put(x, y, CLOUD, cvl, lit=0)
                    # la pluja: fils inclinats, de color blau pàl·lid, que baixen sota els núvols
                    if drops is not None and k > 0.7 and lam > 0.05:
                        ph = (y - drops * 2 + int(x * 0.5)) % 7
                        if ph == 0 and hr(x, (y - drops * 2) // 7, seed + 3) > 0.45:
                            cv.flat(x, y, (176, 204, 236))
                            cv.flat(x + 1, y + 1, (110, 140, 190))
    # el brillantor de Verdant (massa)
    if name == 'verdant':
        hx, hy = cx + lx * r * 0.45, cy + ly * r * 0.45
        cv.flat(hx, hy, (255, 255, 255))
        cv.flat(hx + 1, hy, (220, 255, 220))
        cv.flat(hx, hy - 1, (220, 255, 220))
        # el palau orbital: un punt daurat amb una creu de llum
        px, py = cx + r + 9, cy - r + 2
        cv.flat(px, py, (255, 230, 140))
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            cv.flat(px + dx, py + dy, (170, 140, 70))


def nau(cv):
    """La Cantimplora, petita, amb l'estela dels motors, que torna cap a Terra-2."""
    x, y = 150, 262
    for i in range(46):                                            # l'estela
        a = 1 - i / 46
        xx, yy = x + 10 + i, y - 2 - int(i * 0.35)
        if hr(i, 96) < a + 0.2:
            cv.flat(xx, yy, mix(cv.get(xx, yy), (255, 170, 90), 0.6 * a))
    # el buc (mira a l'esquerra), la franja i els dipòsits
    for i in range(14):
        h = 2 if 2 <= i <= 11 else 1
        for j in range(-h, h + 1):
            cv.put(x - 4 + i, y + j, OLIVE if j else SAFETY, 4.2 - j * 0.6, lit=0)
    for k in range(5):
        cv.put(x - 1 + k * 2, y - 3, OLIVE, 5.0, lit=0)
    cv.flat(x - 5, y, (255, 220, 150))
    cv.flat(x + 10, y, (255, 150, 70))


def bg(cv):
    space(cv, _ANIM['estrelles'])
    for name, c, r, ramp, rain in PLANETS:
        planet(cv, name, c, r, ramp, rain, _ANIM['pluja'])
    nau(cv)


@functools.lru_cache(maxsize=None)
def _base_img():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv.img.copy()


def _frames(key, n):
    out = []
    for f in range(n):
        _ANIM[key] = f
        try:
            cv = Canvas(light=LIGHT)
            bg(cv)
        finally:
            _ANIM[key] = None
        out.append(_diff(cv.img, _base_img()))
    return out


PROPS = {}

ANIMS = {
    'pluja': {'frames': lambda: _frames('pluja', 7), 'frameDuration': 110},
    'estrelles': {'frames': lambda: _frames('estrelles', 6), 'frameDuration': 400},
}

GEOMETRIA = {'things': {}, 'spawns': {}}
