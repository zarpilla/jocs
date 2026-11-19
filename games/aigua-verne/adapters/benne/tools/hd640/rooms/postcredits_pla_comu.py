"""
Aigua Verne — la plaça de Ferrum dels postcrèdits, plana (de cara, a 1×): les textures de `postcredits` (en 3D).

Les cases de maó ennegrit de la plaça (sense teulada: la teulada es fa en 3D), amb les finestres, les portes, el rètol
pintat a mà AIGUA PER A TOTES i el panell nou «AIGUA VESPER · 4 ▲»; la font de Verne (blanca, amb el lector de
targetes tapat amb un cartró i cinta) amb la pica plena; i els fotogrames plans del raig de la font.

Cada peça es dibuixa sola en un llenç transparent per fer-ne una textura o un sprite.
"""
import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

import math

from hd.pix import Canvas, Light, hr
from hd.rooms.comu import text, text_width
from hd.rooms.exterior import fbm
from hd640.rooms.ferrum_comu import (
    MORTAR, IRONF, TIN, CLOTH, WATER, brick_wall, soot_top, window, font_verne, panell)

BASE = 186                      # on toquen a terra les façanes
FONT = (186, 228)               # la font: centre x, base
SLATE = [(14, 14, 18), (24, 24, 30), (36, 36, 42), (50, 50, 56), (66, 64, 70), (86, 82, 86)]
DOOR = [(14, 22, 22), (22, 36, 34), (32, 52, 48), (44, 70, 62), (60, 90, 78), (80, 112, 96)]
TEXL = Light(ambient=0.8, vignette=None, floor_fade=None)        # la llum de les textures planes (neutra)

# les cases: (x0, x1, dalt, llavor, porta, finestres, enceses)
CASES = (
    (-4, 132, 70, 31, (60, 116), ((14, 86, 16, 22), (96, 86, 16, 22), (14, 134, 18, 24), (100, 134, 18, 24)), (2,)),
    (132, 252, 92, 33, (214, 124), ((146, 104, 14, 18), (186, 104, 14, 18), (226, 104, 14, 18)), (1,)),
    (252, 420, 80, 35, (330, 118), ((266, 96, 16, 20), (300, 96, 16, 20), (370, 96, 16, 20), (266, 136, 18, 24),
                                    (380, 136, 18, 24)), (0, 4)),
    (500, 640, 74, 37, (588, 130), ((520, 134, 18, 24), (612, 134, 16, 22)), (0,)),
)


def casa(cv, x0, x1, top, seed, door=None, wins=(), lit=()):
    """Una casa de miners: maó ennegrit, porta i finestres (la teulada, en 3D)."""
    brick_wall(cv, x0, top, x1, BASE, base=3.3, seed=seed, soot=soot_top(top, 46, 1.8, seed + 1))
    cv.rect(x0 - 3, top - 1, x1 + 2, top + 1, MORTAR, 3.4)
    cv.rect(x0, BASE - 7, x1, BASE, MORTAR, lambda x, y: 2.6 + (0.6 if (x // 8 + y // 3) % 2 else 0) -
            (1.4 if x % 8 == 0 else 0))
    for i, (wx, wy, ww, wh) in enumerate(wins):
        window(cv, wx, wy, ww, wh, lit=(i in lit), seed=seed + i)
    if door:
        dx0, dtop = door
        dx1 = dx0 + 26
        cv.rect(dx0 - 3, dtop - 4, dx1 + 3, dtop - 1, MORTAR, 3.6)
        cv.rect(dx0, dtop, dx1, BASE - 1, DOOR, lambda x, y: 2.6 - (1.2 if (x - dx0) % 7 == 0 else 0) +
                (fbm(x / 3, y / 14, dx0) - 0.5) * 0.8)
        cv.disc(dx1 - 4, (dtop + BASE) // 2, 1.2, 1.2, TIN, 4.0)


def retol(cv):
    """AIGUA PER A TOTES, pintat a mà a la paret, en blanc de calç, gros (en escorç s'ha de llegir): la lletra a 2×
    d'alt i d'ample, amb els regalims de la pintura."""
    s = 'AIGUA PER A TOTES'
    tmp = Canvas(260, 12, light=TEXL, transparent=True)
    text(tmp, s, 1, 1, CLOTH, 4.4)
    tw = text_width(s) + 2
    x0, y0 = 336 - tw, 82
    P = tmp.img.load()
    for y in range(12):
        for x in range(tw):
            c = P[x, y]
            if c[3]:
                for dx in (0, 1):
                    for dy in (0, 1):
                        cv.flat(x0 + 2 * x + dx, y0 + 2 * y + dy, c)
    for dx in (6, 42, 80):               # (cap al final: en escorç, un regalim sota TOTES fa una Ę o una Ş)
        for k in range(1 + int(hr(dx, 4) * 2)):
            cv.put(x0 + dx, y0 + 14 + k, CLOTH, 3.6)


def panell_vesper(cv):
    """El panell nou: el mateix de Verne, amb el rètol canviat: AIGUA VESPER / 4 ▲. Dibuixat a 2× (en escorç, a la
    paret del fons, s'ha de llegir)."""
    tmp = Canvas(80, 24, light=TEXL, transparent=True)
    w = panell(tmp, 1, 1, 'AIGUA VESPER', '4 ▲')
    x0, y0 = 568 - w, 80
    P = tmp.img.load()
    for y in range(24):
        for x in range(w + 3):
            c = P[x, y]
            if c[3]:
                for dx in (0, 1):
                    for dy in (0, 1):
                        cv.flat(x0 + 2 * x + dx, y0 + 2 * y + dy, c)
    for bx in (x0 + 10, x0 + 2 * w - 12):                                                   # els suports
        cv.rect(bx, y0 + 42, bx + 2, y0 + 46, IRONF, 3.0)


def cases(cv):
    for x0, x1, top, seed, door, wins, lit in CASES:
        casa(cv, x0, x1, top, seed, door=door, wins=wins, lit=lit)
    retol(cv)
    panell_vesper(cv)


def font(cv):
    """La font de Verne, amb la pica plena i el desguàs que vessa per un costat."""
    x, base = FONT
    font_verne(cv, x, base, lector=True, tapat=True)
    cv.disc(x, base - 14, 18, 3.2, WATER, lambda nx, ny: 2.8 + nx * 0.6 - ny * 0.8, lit=0)
    cv.put(x + 6, base - 15, WATER, 5.0, lit=0)
    cv.put(x - 9, base - 14, WATER, 4.4, lit=0)
    for y in range(base - 12, base):
        cv.put(x + 21 + (y - base + 12) * 0.2, y, WATER, 3.0, lit=0)


def frames_aigua(n=8):
    """El raig de la font: un fil d'aigua que tremola, i les esquitxades i els cercles a la pica (plans)."""
    x, base = FONT
    y0, y1 = base - 30, base - 15
    frames = []
    for f in range(n):
        cv = Canvas(light=TEXL, transparent=True)
        for y in range(y0, y1 + 1):
            t = (y - y0) / (y1 - y0)
            wob = math.sin(f * 0.8 + y * 0.9) * 0.4 * t
            for dx in (0, 1):
                xx = int(round(x - 0.5 + dx + wob))
                lvl = 2 + (1 if (y + f) % 4 == dx else 0) + (1 if dx == 0 else 0)
                cv.flat(xx, y, WATER[min(5, lvl + (1 if (y - f * 2) % 7 == 0 else 0))])
        for k in range(5):
            s = ((f / n) + k / 5) % 1
            a = (k - 2) * 0.7
            sx = x + math.sin(a) * s * 8
            sy = y1 - math.sin(s * math.pi) * 4
            if s < 0.9:
                cv.flat(sx, sy, WATER[5 if s < 0.4 else 4])
        r = 2 + (f % 4) * 3
        for a in range(0, 360, 24):
            px = x + math.cos(math.radians(a)) * r
            py = y1 + math.sin(math.radians(a)) * r * 0.2
            if ((px - x) / 18) ** 2 + ((py - base + 14) / 3.2) ** 2 < 1:
                cv.flat(px, py, WATER[4])
        frames.append(cv.img)
    return frames
