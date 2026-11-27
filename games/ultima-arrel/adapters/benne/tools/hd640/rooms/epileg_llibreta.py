"""
L'Última Arrel — epíleg, quarta vinyeta (pantalla sencera de 640×360, sense HUD): «La llibreta de camp de l'Iri: N de
12 observacions…» (val per a les dues línies, la de la llibreta plena i la de les pàgines en blanc).

La llibreta de camp de l'Iri, oberta damunt la taula del berenar de nit (fusta, la llum turquesa dels bolets que entra
per la dreta): la pàgina de l'esquerra plena de dibuixos a llapis amb el seu nom (el bolet, la fada, el gripau, els
filaments, una fulla de roure), la de la dreta amb un parell de dibuixos més i la meitat de baix encara en blanc. Al
costat, el llapis mossegat i una tassa.
"""
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)

from hd.pix import Light, W, H
from hd640.rooms.arrel_comu import PLANK, CREAM, TURQ, GLOW_T, YELLOWP, fbm, hr, lletres

LIGHT = Light(ambient=0.15, vignette=(90, 40), floor_fade=None)
LIGHT.width = W
LIGHT.point(330, 170, r=420, k=1.4, squash=0.8, power=1.2)

PAPER = [(70, 64, 54), (120, 112, 96), (170, 162, 140), (210, 202, 178), (234, 228, 206), (248, 244, 228)]
LLAPIS = [(40, 40, 46), (66, 66, 74), (96, 96, 104)]
TAPA = [(16, 30, 22), (28, 50, 36), (42, 72, 50), (60, 96, 66), (84, 122, 86)]

PAG_E = (130, 60, 316, 312)
PAG_D = (324, 60, 510, 312)


def taula(cv):
    for y in range(H):
        for x in range(W):
            cv.put(x, y, PLANK, 1.6 + (fbm(x / 70, y / 4, 13) - 0.5) * 2.0, lit=1.0)
    cv.glow(W + 20, 120, 260, GLOW_T, 0.45)                          # la llum dels bolets, de la dreta


def llibreta(cv):
    """Les tapes verdes, les pàgines amb ratlles i la ratlla del mig."""
    cv.darken(PAG_E[0] + 4, PAG_E[1] + 8, PAG_D[2] + 10, PAG_D[3] + 12, 0.6)
    cv.rect(PAG_E[0] - 8, PAG_E[1] - 6, PAG_D[2] + 8, PAG_D[3] + 6, TAPA, 2.6, lit=0.7)
    for x0, y0, x1, y1 in (PAG_E, PAG_D):
        for y in range(y0, y1):
            for x in range(x0, x1):
                ratlla = 0.5 if (y - y0) % 14 == 13 else 0
                cv.put(x, y, PAPER, 4.2 - ratlla + (fbm(x / 20, y / 20, 3) - 0.5) * 0.6, lit=0.6)
    for y in range(PAG_E[1], PAG_E[3]):                                 # la costura del mig
        cv.put(320, y, PAPER, 2.0, lit=0.4)
        cv.put(321, y, PAPER, 2.6, lit=0.4)
        if y % 12 < 3:
            cv.put(320, y, LLAPIS, 1.0, lit=0)


def traç(cv, pts, lvl=1.6):
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        n = max(abs(xb - xa), abs(yb - ya), 1)
        for i in range(int(n) + 1):
            t = i / n
            x, y = xa + (xb - xa) * t, ya + (yb - ya) * t
            if hr(int(x), int(y), 5) < 0.9:
                cv.put(x, y, LLAPIS, lvl, lit=0)


def cercle(cv, cx, cy, rx, ry, a0=0, a1=360, lvl=1.6):
    traç(cv, [(cx + math.cos(math.radians(a)) * rx, cy + math.sin(math.radians(a)) * ry)
              for a in range(a0, a1 + 1, 8)], lvl)


def bolet(cv, x, y):
    cercle(cv, x, y, 16, 10, 180, 360)
    traç(cv, [(x - 16, y), (x + 16, y)])
    traç(cv, [(x - 4, y), (x - 5, y + 22), (x + 5, y + 22), (x + 4, y)])
    for k in range(5):
        traç(cv, [(x - 10 + k * 5, y - 2), (x - 10 + k * 5 + 1, y - 6)], 2.0)
    cv.glow(x, y - 4, 14, GLOW_T, 0.35)                                 # pintat amb retolador turquesa


def fada(cv, x, y):
    cercle(cv, x, y, 4, 4)
    traç(cv, [(x, y + 4), (x, y + 16), (x - 4, y + 24)])
    traç(cv, [(x, y + 16), (x + 4, y + 24)])
    traç(cv, [(x, y + 8), (x - 6, y + 12)])
    traç(cv, [(x, y + 8), (x + 6, y + 12)])
    cercle(cv, x - 8, y + 6, 7, 4, lvl=1.2)                              # les ales
    cercle(cv, x + 8, y + 6, 7, 4, lvl=1.2)


def gripau(cv, x, y):
    cercle(cv, x, y, 18, 11)
    cercle(cv, x - 8, y - 10, 5, 5)
    cercle(cv, x + 8, y - 10, 5, 5)
    traç(cv, [(x - 10, y + 2), (x, y + 5), (x + 10, y + 2)])
    for ex in (-8, 8):
        traç(cv, [(x + ex - 2, y - 10), (x + ex + 2, y - 10)], 1.0)


def fulla(cv, x, y):
    pts = []
    for i in range(0, 41):
        t = i / 40
        w = math.sin(t * math.pi) * (8 + 3 * math.sin(t * math.pi * 5))
        pts.append((x + w, y + t * 36))
    traç(cv, pts)
    traç(cv, [(2 * x - p[0], p[1]) for p in pts])
    traç(cv, [(x, y), (x, y + 40)])


def miceli(cv, x, y):
    for k in range(4):
        pts = [(x + i * 3, y + k * 5 + math.sin(i / 2 + k) * 3) for i in range(22)]
        traç(cv, pts, 1.2)


def pagines(cv):
    x0, y0 = PAG_E[0], PAG_E[1]
    lletres(cv, 'OBSERVACIONS', x0 + 14, y0 + 10, None, ramp=LLAPIS, lvl=1.4, wobble=0.6, seed=2)
    bolet(cv, x0 + 40, y0 + 60)
    lletres(cv, 'BOLET', x0 + 18, y0 + 92, None, ramp=LLAPIS, lvl=1.6, wobble=0.6, seed=3)
    fada(cv, x0 + 130, y0 + 44)
    lletres(cv, 'FADA', x0 + 112, y0 + 76, None, ramp=LLAPIS, lvl=1.6, wobble=0.6, seed=4)
    gripau(cv, x0 + 46, y0 + 150)
    lletres(cv, 'GRIPAU', x0 + 18, y0 + 174, None, ramp=LLAPIS, lvl=1.6, wobble=0.6, seed=5)
    miceli(cv, x0 + 100, y0 + 134)
    lletres(cv, 'MICELI', x0 + 104, y0 + 164, None, ramp=LLAPIS, lvl=1.6, wobble=0.6, seed=6)
    fulla(cv, x0 + 70, y0 + 196)
    for k in range(7):                                                  # les marques de comptar
        traç(cv, [(x0 + 120 + k * 6, y0 + 204), (x0 + 122 + k * 6, y0 + 220)], 1.4)
    traç(cv, [(x0 + 116, y0 + 218), (x0 + 160, y0 + 206)], 1.4)
    x0 = PAG_D[0]
    fada(cv, x0 + 40, y0 + 22)
    cercle(cv, x0 + 120, y0 + 40, 20, 20, 200, 520)                     # un roure (la capçada)
    traç(cv, [(x0 + 120, y0 + 60), (x0 + 120, y0 + 84)])
    lletres(cv, 'ROURE', x0 + 102, y0 + 92, None, ramp=LLAPIS, lvl=1.6, wobble=0.6, seed=8)


def llapis(cv):
    """El llapis groc, mossegat, de biaix damunt la pàgina de la dreta."""
    x0, y0, x1, y1 = 400, 290, 560, 230
    n = int(math.hypot(x1 - x0, y1 - y0))
    ux, uy = (x1 - x0) / n, (y1 - y0) / n
    vx, vy = -uy, ux
    cv.darken(x0 + 4, y1 + 6, x1 + 6, y0 + 10, lambda x, y: 0.5 if abs((x - x0 - 5) * vx + (y - y0 - 8) * vy) < 4
              and 14 <= (x - x0 - 5) * ux + (y - y0 - 8) * uy <= n else 0)
    for i in range(n):
        for j in range(-3, 4):
            x, y = x0 + ux * i + vx * j, y0 + uy * i + vy * j
            if i < 14:                                                  # la punta, de fusta i grafit
                if abs(j) <= i / 4 - 0.5:
                    cv.put(x, y, LLAPIS if i < 5 else CREAM, 2.0 if i < 5 else 3.4, lit=0.4)
            else:
                mos = i > n - 10 and hr(i, j) < 0.35                    # el cap, mossegat
                if not mos:
                    cv.put(x, y, YELLOWP, 3.6 - j * 0.3 + (0.6 if j == 1 else 0), lit=0.5)


def tassa(cv):
    cx, cy = 590, 90
    cv.darken(cx - 30, cy - 24, cx + 38, cy + 34, lambda x, y: 0.55 if (x - cx - 6) ** 2 / 34 ** 2 +
              (y - cy - 6) ** 2 / 28 ** 2 <= 1 else 0)
    cv.disc(cx, cy, 30, 24, CREAM, lambda nx, ny: 3.6 - ny * 0.6 + nx * 0.6, lit=0.6)
    cv.disc(cx, cy, 24, 18, PLANK, lambda nx, ny: 1.6 + ny * 0.8, lit=0.3)          # el te, fosc
    cv.disc(cx - 6, cy - 5, 6, 3, TURQ, 3.6, lit=0)                                    # el reflex turquesa


def bg(cv):
    taula(cv)
    llibreta(cv)
    pagines(cv)
    llapis(cv)
    tassa(cv)
    cv.P = cv.img.load()


PROPS = {}
ANIMS = {}
GEOMETRIA = {'things': {}, 'spawns': {}}
