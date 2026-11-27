"""
L'Última Arrel — epíleg, primera vinyeta (pantalla sencera de 640×360, sense HUD): «Al Bosc de la Coma, els bolets
brillen de turquesa. Sota terra, el nord torna a parlar amb el sud.»

Un tall del bosc de nit, com un dibuix de llibre de natura: a dalt, el terra del bosc amb molsa, falgueres i els
bolets encesos de turquesa; a sota, la terra tallada, amb arrels i pedres, i els filaments del Miceli que la creuen
d'una banda a l'altra (del nord, a l'esquerra, al sud, a la dreta), tots encesos, i que pugen fins als bolets.

ANIMS: `espores` (espores turquesa que pugen dels bolets i parpellegen).
"""
import math
import random

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)

from hd.pix import Light, W, H
from hd640.rooms.arrel_comu import EARTH, CLAY, STONE, MOSS, BARK, fbm, hr, arrel, bolet, filament
from hd640.rooms.vora_comu import espores_frames

SOL = 142                                           # el terra del bosc (on comença el tall)

LIGHT = Light(ambient=0.15, vignette=(60, 24), floor_fade=None)
LIGHT.width = W

NIT = [(2, 6, 14), (4, 12, 24), (8, 20, 36), (12, 30, 50), (18, 44, 66), (28, 60, 82)]
BOLETS = [(70, SOL + 2, 26, 15), (104, SOL + 4, 15, 9), (210, SOL + 1, 34, 19), (246, SOL + 3, 18, 10),
          (352, SOL + 2, 24, 13), (452, SOL + 1, 36, 20), (492, SOL + 4, 16, 9), (580, SOL + 2, 26, 14)]


def _sol(x):
    return SOL + math.sin(x / 37) * 2.5 + (fbm(x / 20, 0, 4) - 0.5) * 4


def cel(cv):
    """El bosc de nit, darrere: el cel fosc, els troncs en silueta i alguna estrella entre les capçades."""
    for y in range(0, SOL + 6):
        for x in range(W):
            cv.put(x, y, NIT, 3.2 - y / SOL * 2.2 + (fbm(x / 40, y / 30, 2) - 0.5) * 0.8, lit=0)
    rnd = random.Random(5)
    for _ in range(40):
        x, y = rnd.randrange(W), rnd.randrange(4, 60)
        cv.flat(x, y, (180, 220, 230) if rnd.random() < 0.3 else (90, 130, 150))
    for i, x0 in enumerate((24, 130, 300, 410, 540, 620)):
        w = 10 + hr(i, 1) * 14
        for y in range(0, SOL + 4):
            for x in range(int(x0 - w), int(x0 + w)):
                cv.put(x, y, NIT, 0.6 + (fbm(x / 3, y / 14, i) - 0.5) * 0.6, lit=0)
    for i in range(90):                                         # les capçades, a dalt
        cx, cy = hr(i, 2) * W, hr(i, 3) * 38
        cv.disc(cx, cy, 18 + hr(i, 4) * 20, 10 + hr(i, 5) * 8, NIT, 0.8, lit=0)


def terra(cv):
    """El tall de terra: capes (humus fosc a dalt, argila més avall), pedres i el terra de molsa a la vora."""
    for x in range(W):
        top = int(_sol(x))
        for y in range(top, H):
            d = (y - top) / (H - SOL)
            ramp = EARTH if d < 0.55 else CLAY
            lvl = 2.6 - d * 1.2 + (fbm(x / 14, y / 6, 9) - 0.5) * 1.6
            cv.put(x, y, ramp, lvl, lit=0.5)
        for y in range(top - 3, top + 3):                       # la molsa de la vora
            cv.put(x, y, MOSS, 3.4 + (fbm(x / 3, y, 1) - 0.5) * 2 - (y - top) * 0.3, lit=0.4)
    rnd = random.Random(8)
    for _ in range(26):                                         # pedres
        cx, cy = rnd.uniform(0, W), rnd.uniform(SOL + 30, H - 6)
        rx, ry = rnd.uniform(4, 11), rnd.uniform(3, 7)
        cv.disc(cx, cy, rx, ry, STONE, lambda nx, ny: 3.2 - ny * 1.4 - nx * 0.5, lit=0.3)


def arrels(cv):
    """Les arrels dels arbres de dalt, que baixen pel tall."""
    for i, (x, w) in enumerate(((24, 7), (130, 6), (300, 8), (410, 6), (540, 7), (620, 5))):
        for j in range(3):
            dx = (j - 1) * (18 + hr(i, j) * 26)
            arrel(cv, (x + dx * 0.2, SOL - 2), (x + dx * 0.7, SOL + 40 + hr(i, j, 1) * 30),
                  (x + dx, SOL + 90 + hr(i, j, 2) * 80), w * (0.9 - j * 0.15), 1.0, ramp=BARK, base=2.6, seed=i * 3 + j,
                  moss=False, lit=0.3)


def miceli(cv):
    """Els filaments: tres fils llargs que creuen el tall del nord (esquerra) al sud (dreta), ramificats, i fils que
    pugen fins a cada bolet."""
    def fora(x, y):
        return y < _sol(x) + 4
    for k, y in enumerate((SOL + 60, SOL + 120, SOL + 180)):
        filament(cv, -4, y, 0.0, 720, 31 + k * 5, glow=1.0, branch=1, k=3.8, evita=fora, cap=0.0)
    for i, (x, y, h, r) in enumerate(BOLETS):
        filament(cv, x + 2, SOL + 60 + (i % 3) * 60, -math.pi / 2, 160, 50 + i, glow=0.8, branch=0, k=3.4,
                 sostre=_sol(x) + 3, cap=-math.pi / 2)


def superficie(cv):
    """Damunt del terra: brins d'herba i els bolets encesos."""
    for x in range(0, W, 3):                                   # brins d'herba a la vora
        h = 2 + hr(x, 9) * 6
        cv.line(x, _sol(x), x + (hr(x, 8) - 0.5) * 3, _sol(x) - h, MOSS, 3.0, lit=0.3)
    for x, y, h, r in BOLETS:
        bolet(cv, x, _sol(x) + (y - SOL), h, r, glow=1.0)


def bg(cv):
    cel(cv)
    terra(cv)
    arrels(cv)
    miceli(cv)
    superficie(cv)
    cv.P = cv.img.load()


PROPS = {}


def _espores():
    return espores_frames(0, n=24, seed=23, count=26, area=(20, 620, 40, SOL - 4), k=1.0)


ANIMS = {'espores': {'frames': _espores, 'frameDuration': 150}}

GEOMETRIA = {'things': {}, 'spawns': {}}
