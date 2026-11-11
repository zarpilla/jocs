"""
La caixa de cadenes, a proa (Escena 6, onze de la nit): fosca, estreta i rovellada. El buc es tanca cap a baix,
la cadena de l'àncora baixa pel tub de l'escobén i s'apila a l'esquerra; l'escotilla, oberta a dalt, deixa
entrar la llum groga de coberta. Prop: la manta i el paper de l'entrepà de la Juana (que és un sprite), i el rotllo de cap on seu.
"""
import math

from hd.pix import Canvas, Light, W, H, hr, mix, B4, RUST, PAPER
from hd.rooms.arenga import (WALL, ENG, DECK, CAB, DARK, WHITEP, YELL, REDP, BRASS, WARM, FLOOR_Y, BOTTOM,
                             box, rrect, bolt, hpipe, vpipe, glow)
from hd.rooms import sota

HX0, HX1 = 212, 268          # l'escotilla

LIGHT = Light(ambient=-0.9, vignette=(70, 20), floor_fade=None)
LIGHT.point(240, 24, r=200, k=2.9, squash=0.75, power=1.6)        # la llum de coberta, per l'escotilla
LIGHT.add(lambda x, y: 0.9 * max(0.0, 1 - abs(x - 240 - (y - 30) * 0.25) / (24 + y * 0.45))
          if 24 < y < 200 else 0.0)                                # el con de llum que baixa

# planxa nua: imprimació d'òxid vermell, rovellada
HULL = [(6, 4, 4), (12, 8, 7), (20, 12, 10), (30, 18, 14), (42, 26, 18), (56, 34, 22), (72, 44, 28),
        (92, 58, 36), (116, 76, 48), (142, 98, 64)]
CHAIN = [(8, 7, 7), (16, 13, 12), (28, 22, 18), (42, 32, 24), (60, 44, 30), (82, 58, 38), (108, 76, 50),
         (140, 104, 72)]
MUD = [(6, 6, 5), (12, 11, 9), (20, 18, 14), (30, 27, 20), (42, 38, 28), (56, 50, 36)]
WOOL = [(14, 14, 16), (26, 26, 30), (42, 42, 46), (62, 60, 62), (84, 82, 80), (108, 104, 98), (136, 130, 120)]
WOOD = [(10, 8, 6), (20, 15, 11), (34, 26, 18), (50, 38, 26), (68, 52, 34), (88, 68, 46), (110, 86, 58)]
NIGHT = [(2, 3, 8), (4, 6, 14), (8, 10, 22), (12, 16, 32), (20, 24, 44)]


def side(x, y):
    """Els costats del buc: es tanquen cap a baix (la proa). → 0 dins el mamparo del fons, >0 al costat."""
    lx = 40 + (y / FLOOR_Y) * 28
    rx = W - 44 - (y / FLOOR_Y) * 30
    return x < lx, x > rx, lx, rx


# ─── Parets ─────────────────────────────────────────────────────────────────

def walls(cv):
    # el mamparo de col·lisió (al fons): planxa amb reforços verticals
    for y in range(0, FLOOR_Y):
        for x in range(W):
            lv = 3.2 + (hr(x // 3, y // 4, 41) - 0.5) * 0.5
            if hr(x // 7, y // 9, 42) > 0.82:
                lv += 0.5                                               # taques de rovell més clares
            cv.put(x, y, HULL, lv)
    for sx in range(96, 400, 52):                                       # reforços
        for x in range(sx, sx + 5):
            d = x - sx
            for y in range(0, FLOOR_Y):
                cv.put(x, y, HULL, 3.6 + (1.0 if d == 0 else 0.4 if d == 1 else -0.6 if d >= 3 else 0))
    for sy in (48, 104):
        cv.hline(0, W - 1, sy, HULL, 1.8)
        cv.hline(0, W - 1, sy + 1, HULL, 4.0)
    sota.rust_streaks(cv, 0, 10, W - 1, FLOOR_Y, 26, k=0.35, seed=43, ramp=RUST)
    # els costats del buc, amb quadernes corbes, més foscos
    for y in range(0, BOTTOM + 12):
        lx = 40 + (min(y, BOTTOM) / FLOOR_Y) * 28
        rx = W - 44 - (min(y, BOTTOM) / FLOOR_Y) * 30
        for x in range(W):
            if x < lx:
                t = x / lx
                cv.put(x, y, HULL, 1.6 + t * 1.4 + (0.9 if int(y / 22) != int((y + 1) / 22) else 0))
            elif x > rx:
                t = (W - 1 - x) / (W - 1 - rx)
                cv.put(x, y, HULL, 1.3 + t * 1.2 + (0.9 if int(y / 22) != int((y + 1) / 22) else 0))
    for y in range(0, BOTTOM + 12):
        lx = 40 + (min(y, BOTTOM) / FLOOR_Y) * 28
        rx = W - 44 - (min(y, BOTTOM) / FLOOR_Y) * 30
        cv.put(lx, y, HULL, 4.4)
        cv.put(lx + 1, y, HULL, 1.4)
        cv.put(rx, y, HULL, 3.8)
        cv.put(rx - 1, y, HULL, 1.4)
    # el sostre (la coberta per sota), baix, amb baos
    cv.rect(0, 0, W - 1, 12, DARK, 2.2)
    for bx in range(10, W, 52):
        box(cv, bx, 0, bx + 8, 14, HULL, 2.6, grad=0.6)


def hatch(cv):
    """L'escotilla, oberta: la nit, el pal de proa amb un llum groc i la brazola."""
    x0, x1 = HX0, HX1
    for y in range(0, 20):
        for x in range(x0, x1 + 1):
            cv.put(x, y, NIGHT, 2.2 + y * 0.06 + (hr(x // 5, y // 3) - 0.5) * 0.4, lit=0)
    # un núvol clar i el llum de coberta
    for x in range(x0, x1 + 1):
        yy = 6 + math.sin(x * 0.12) * 2
        cv.put(x, int(yy), NIGHT, 4.0, lit=0)
    cv.disc(252, 8, 3, 2, [(160, 120, 40), (255, 210, 110), (255, 246, 200)], 2.0, lit=0)
    glow(cv, 252, 8, 16, (255, 200, 90), 0.8)
    # la brazola i la tapa, oberta enlaire (de cantó)
    box(cv, x0 - 6, 16, x1 + 6, 24, CAB, 3.4)
    for bx in range(x0 - 4, x1 + 5, 6):
        bolt(cv, bx, 20, CAB, 3.6)
    cv.poly([(x0 - 6, 16), (x0 - 2, 0), (x0 + 2, 0), (x0 - 2, 16)], CAB, 3.0)
    # graons soldats al mamparo, de l'escotilla a terra
    for y in range(32, FLOOR_Y - 4, 11):
        box(cv, 230, y, 250, y + 2, CAB, 3.8)
        cv.vline(230, y + 3, y + 5, CAB, 2.0)
        cv.vline(250, y + 3, y + 5, CAB, 2.0)
        sota.rust_streaks(cv, 232, y + 3, 248, y + 10, 3, k=0.5, seed=y)


def haze(cv):
    """El con de llum de l'escotilla (pols a l'aire)."""
    for y in range(24, BOTTOM + 8):
        for x in range(W):
            c = 1 - abs(x - 240 - (y - 30) * 0.25) / (24 + y * 0.45)
            if c > 0:
                k = 0.16 * c * (1 - y / 260)
                if k > B4[y & 3][x & 3] * 0.35:
                    cv.flat(x, y, mix(cv.get(x, y), (255, 214, 130), k))
    # motes de pols
    for i in range(40):
        y = 30 + hr(i, 1) * 150
        x = 240 + (y - 30) * 0.25 + (hr(i, 2) - 0.5) * (24 + y * 0.45) * 1.6
        if 0 <= x < W:
            cv.flat(int(x), int(y), mix(cv.get(int(x), int(y)), (255, 230, 170), 0.5))


# ─── La cadena ──────────────────────────────────────────────────────────────

def link(cv, x, y, flat, lvl=3.2):
    """Una baula de cadena amb travesser: de cara (anella oval, gruixuda, amb el pal) o de cantó (barra)."""
    if flat:
        for a in range(0, 360, 8):
            ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
            for r in (0, 1):
                px = x + round(ca * (6 - r))
                py = y + round(sa * (4 - r))
                cv.put(px, py, CHAIN, lvl + 0.8 - sa * 1.2 - ca * 0.5 - r * 0.8)
        cv.vline(x, y - 2, y + 2, CHAIN, lvl + 0.2)
        cv.put(x, y - 2, CHAIN, lvl + 1.4)
    else:
        cv.rect(x - 6, y - 1, x + 6, y + 1, CHAIN, lvl)
        cv.hline(x - 5, x + 5, y - 1, CHAIN, lvl + 1.5)
        cv.hline(x - 5, x + 5, y + 1, CHAIN, lvl - 1.2)
        cv.put(x - 6, y, CHAIN, lvl - 0.6)
        cv.put(x + 6, y, CHAIN, lvl - 0.6)


def chain(cv):
    # el tub de l'escobén, que baixa del sostre
    vpipe(cv, 118, 0, 30, 9, HULL, 3.4)
    cv.disc(118, 31, 10, 3, HULL, lambda nx, ny: 3.8 - ny)
    cv.disc(118, 31, 7, 2, DARK, 0.6)
    # la cadena que en penja (baules alternes, de cara i de cantó)
    for i, y in enumerate(range(36, 100, 7)):
        if i % 2 == 0:
            for a in range(0, 360, 10):
                ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
                for r in (0, 1):
                    cv.put(118 + round(ca * (4 - r)), y + round(sa * (5 - r)), CHAIN, 4.2 - ca * 1.0 - r * 0.8)
        else:
            cv.rect(117, y - 5, 119, y + 5, CHAIN, 3.4)
            cv.vline(117, y - 5, y + 5, CHAIN, 4.8)
            cv.vline(119, y - 5, y + 5, CHAIN, 2.2)
    # la pila: primer l'ombra del munt, després les baules, de les de sota (fosques) a les de dalt
    mound = [(52, 182)] + [(118 + u * 66, 180 - (1 - abs(u) ** 1.6) * 88) for u in [i / 20 - 1 for i in range(41)]] + [(186, 182)]
    cv.poly(mound, CHAIN, 0.8)
    pts = []
    for i in range(300):
        u = hr(i, 1) * 2 - 1
        h = (1 - abs(u) ** 1.6) * 86
        x = 118 + u * 62
        y = 180 - hr(i, 2) ** 0.8 * h
        pts.append((y, x, i))
    pts.sort()
    for y, x, i in pts:
        depth = (180 - y) / 90
        link(cv, int(x), int(y), hr(i, 3) > 0.45, lvl=2.6 + depth * 1.6 + (hr(i, 4) - 0.5) * 0.8)
    # baules soltes que baixen per davant de la pila
    for k, (x, y) in enumerate(((172, 178), (182, 182), (166, 185))):
        link(cv, x, y, k % 2 == 0, lvl=3.4)


# ─── Terra ──────────────────────────────────────────────────────────────────

def floor(cv):
    """El fons de la caixa: una reixa de fusta damunt del fang i l'aigua que s'hi escola."""
    for y in range(FLOOR_Y, BOTTOM + 12):
        lx = 40 + (min(y, BOTTOM) / FLOOR_Y) * 28
        rx = W - 44 - (min(y, BOTTOM) / FLOOR_Y) * 30
        for x in range(int(lx) + 1, int(rx)):
            cv.put(x, y, MUD, 2.4 + (hr(x // 3, y // 2, 51) - 0.5) * 0.8)
    # llistons de la reixa (en perspectiva)
    vp = (240, 40)
    for y in range(FLOOR_Y + 2, BOTTOM + 12):
        d = y - vp[1]
        lx = 40 + (min(y, BOTTOM) / FLOOR_Y) * 28
        rx = W - 44 - (min(y, BOTTOM) / FLOOR_Y) * 30
        for x in range(int(lx) + 2, int(rx) - 1):
            u = vp[0] + (x - vp[0]) * 150 / d
            if (u % 22) < 15:
                cv.put(x, y, WOOD, 2.6 + (hr(int(u // 22), y // 4) - 0.5) * 0.6 - (0.7 if (u % 22) > 13 else 0))
    # un bassal amb el reflex de l'escotilla
    for y in range(184, 196):
        for x in range(150, 214):
            if ((x - 182) / 32) ** 2 + ((y - 190) / 6) ** 2 <= 1:
                cv.flat(x, y, mix(cv.get(x, y), (12, 14, 18), 0.6))
                if hr(x // 3, y) > 0.9:
                    cv.flat(x, y, mix(cv.get(x, y), (180, 150, 90), 0.35))


# ─── La manta (prop) ────────────────────────────────────────────────────────
# Hi va també el seient de la Juana: un rotllo de cap d'amarrar vell, gruixut, amb la manta als peus.

ROPE = [(10, 8, 6), (22, 17, 11), (38, 30, 19), (58, 46, 29), (80, 64, 40), (104, 86, 56), (130, 110, 74)]


def hawser(cv):
    """Un rotllo de cap d'amarrar, gruixut i vell, en perspectiva: el seient de la Juana (Escena 6)."""
    cx, base, top = 300, 178, 152
    sota.floor_shadow(cv, cx, base + 1, 24, 4, 0.8)
    n = (base - top) // 3
    for k in range(n + 1):
        cy = base - k * 3
        rx, ry = 19 - k * 0.15, 5.0
        for a in range(0, 360, 2):
            sa = math.sin(math.radians(a))
            x = cx + math.cos(math.radians(a)) * rx
            y = cy + sa * ry
            if sa < -0.2 and k < n:                                     # la part de darrere la tapa la volta de dalt
                continue
            for t in range(3):
                cv.put(x, y - t, ROPE, (3.6 if sa > -0.2 else 2.4) + (0.8 if t == 2 else 0) - (0.6 if (a // 8 + k) % 2 else 0))
    cv.disc(cx, top, 10, 2.5, DARK, 1.0)                                # el forat del mig, a dalt


def blanket(cv):
    """La manta, plegada de qualsevol manera a terra, i el paper d'alumini de l'entrepà, rebregat."""
    sota.floor_shadow(cv, 300, 184, 42, 4, 0.8)
    hawser(cv)
    body = [(262, 182), (274, 172), (300, 170), (330, 172), (342, 180), (336, 187), (300, 188), (268, 188)]
    cv.poly(body, WOOL, lambda x, y: 3.4 - (y - 170) * 0.04 + math.sin(x * 0.25 + y * 0.6) * 0.5)
    cv.line(274, 172, 330, 172, WOOL, 4.6)
    for x in range(266, 340):                                           # les ratlles de la manta
        for yy in (176, 177):
            cv.put(x, yy + int(math.sin(x * 0.15) * 1.5), REDP, 2.8)
    for x in range(268, 336, 3):                                        # serrell
        cv.put(x, 189, WOOL, 3.0)
    # el paper de l'entrepà, una bola rebregada a terra
    FOIL = [(40, 40, 44), (90, 90, 96), (150, 150, 156), (200, 200, 206), (236, 236, 240)]
    cv.disc(346, 186, 5, 3, FOIL, lambda nx, ny: 2.8 - nx - ny + (hr(int(nx * 4), int(ny * 4)) - 0.5) * 1.6)
    cv.put(344, 184, FOIL, 4.8)
    cv.put(347, 185, FOIL, 4.6)
    # una molla de pa
    cv.put(352, 189, PAPER, 4.0)


# ─── Muntatge ───────────────────────────────────────────────────────────────

def bg(cv):
    walls(cv)
    hatch(cv)
    floor(cv)
    chain(cv)
    haze(cv)
    glow(cv, 240, 22, 40, (255, 200, 110), 0.35)


PROPS = {'manta': blanket}

GEOMETRIA = {
    'things': {
        'escotilla': {'rect': (204, 0, 276, 150), 'walk': (240, 168)},
        'cadenes': {'rect': (48, 0, 186, 182), 'walk': (196, 186)},
        'manta': {'rect': (260, 168, 356, 190), 'walk': (250, 192)},
    },
    'spawns': {'iri': (232, 190), 'vet': (196, 194), 'juana': (302, 182)},
    'walkable': [(188, 164), (402, 164), (418, 197), (164, 197), (182, 184)],
}
