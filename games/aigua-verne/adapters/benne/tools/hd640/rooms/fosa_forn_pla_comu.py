"""
Aigua Verne — `fosa_forn` dibuixada de cara (pla), com era abans de passar-la a 3D: les peces d'on `fosa_forn.py`
(la sala en 3D, a 1×) treu les textures, les capes i les animacions.

La sala d'abans:
Aigua Verne — `fosa_forn` (L): la fosa de Ferrum per dins, la banda del forn.

Una nau alta i fosca de maó negre, amb les encavallades de ferro a dalt i finestrals bruts per on entra una llum de
fum. A l'esquerra, la **porta** del carrer (oberta: la claror de fora); la pila de **comptadors** d'aigua per fondre
(el **metall**); al mig, el **forn** gran de maó amb la campana de ferro i la boca de foc (freda: la fosa està
aturada des de la vaga); al costat, la **manxa** (el fol de cuir i la palanca gran); el **termòmetre** de rellotge,
a la pilastra; el **rascle** de l'escòria, recolzat a la paret; i a la dreta, el **pas** cap a la colada.

Decorats (PROPS): `forn_ences` (el forn encès: brases, llum càlida a tota la nau, l'agulla del termòmetre a mitja
esfera) i `forn_fort` (a tota manxa: llum blanca-groga, agulla a la zona vermella). ANIMS: `foc` (les flames de la
boca, amb el forn encès), `foc_fort` (les flames a tota manxa) i `guspires`.
"""
import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

import functools
import math

from PIL import Image

from hd.pix import Canvas, Light, W, H, hr, mix, B4
from hd.rooms.comu import _diff, text, text_width
from hd.rooms.exterior import fbm
from hd640.rooms.ferrum_comu import (
    RH, SMOG, HAZE, SLAGF, SOOT, MORTAR, COB, COAL, IRONF, RUSTF, TIN, PLANKF, WHITEV, BLACKT, FIREF, GLOWF,
    CLOTH, REDP, HELM, NAVE_FLOOR,
    brick_wall, brick_lvl, cobbles, pila_comptadors, nave_wall, light_shafts, trusses, crane_rail, foundry_floor)

# (a 1×: les textures de la sala en 3D, vegeu docs/guia-art-profunditat.md)

BOCA = (255, 176)               # el centre de la boca del forn
FORN = (172, 338, 92, 206)      # x0, x1, dalt del cos, base
DIAL = (150, 126, 15)           # el termòmetre: centre i radi
LEATHER = [(18, 10, 8), (34, 18, 12), (54, 30, 18), (76, 44, 26), (100, 60, 34), (126, 80, 46), (150, 102, 62)]

LIGHTS = {}
for lvl, (k, r) in {0: (0, 0), 1: (2.2, 300), 2: (2.9, 380)}.items():
    L = Light(ambient=-0.5, vignette=(80, 40), floor_fade=(250, 30))
    L.point(36, 160, r=150, k=1.6, power=1.6)                    # la claror del carrer, per la porta
    for wx in (96, 404, 498):
        L.point(wx + 14, 70, r=120, k=0.9, power=1.6)            # els finestrals
    if k:
        L.point(BOCA[0], BOCA[1], r=r, k=k, power=1.6)           # el foc
    LIGHTS[lvl] = L
LIGHT = LIGHTS[0]
WARM = {1: ((255, 120, 40), 0.3, 340), 2: ((255, 160, 70), 0.38, 420)}


# ─── La nau ────────────────────────────────────────────────────────────────

def nau(cv):
    trusses(cv, 0, 30, seed=3)
    nave_wall(cv, 0, W - 1, top=31, seed=5, windows=((96, 28), (404, 28), (498, 28)), pilasters=(150, 556))
    crane_rail(cv, 86)
    light_shafts(cv, ((96, 28, 60), (404, 28, 60), (498, 28, 60)), k=0.16)


def porta(cv, fulla=True):
    """La porta del carrer, oberta: la claror grisa i taronja de fora, i un tros de carrer. `fulla`: la fulla de
    fusta, oberta cap a dins (a la sala en 3D és una superfície a part)."""
    x0, x1, top = 14, 64, 108
    cv.rect(x0 - 5, top - 6, x1 + 5, NAVE_FLOOR, MORTAR, lambda x, y: 2.4 - (0.8 if (y - top) % 8 == 7 else 0))
    for y in range(top, NAVE_FLOOR + 1):
        for x in range(x0, x1 + 1):
            if y < 168:
                cv.put(x, y, SMOG, 6.4 - (y - top) * 0.02 + (fbm(x / 9, y / 4, 13) - 0.5) * 1.6, lit=0)   # el cel
            else:
                cv.put(x, y, COB, 5.0 + (y - 168) * 0.05 + (fbm(x / 4, y / 2, 14) - 0.5) * 1.2, lit=0)    # el carrer
    # una casa de fora i el pal del panell, en silueta
    cv.rect(x0, 134, x0 + 22, 168, SOOT, lambda x, y: 2.6 + (0.8 if (y % 4 == 0) else 0), lit=0)
    cv.rect(x0 + 6, 144, x0 + 12, 154, GLOWF, 2.6, lit=0)
    cv.rect(x1 - 10, 120, x1 - 9, 168, IRONF, 2.0, lit=0)
    # la fulla de la porta, de fusta, oberta cap a dins
    if fulla:
        cv.poly([(x1, top), (x1 + 16, top + 6), (x1 + 16, NAVE_FLOOR + 8), (x1, NAVE_FLOOR)], PLANKF,
                lambda x, y: 2.2 - (1.2 if (x - x1) % 5 == 0 else 0))
    cv.rect(x0 - 1, NAVE_FLOOR - 1, x1 + 1, NAVE_FLOOR + 1, MORTAR, 3.6)


# ─── El forn ───────────────────────────────────────────────────────────────

def forn(cv, fire=0):
    x0, x1, top, base = FORN
    cx = (x0 + x1) // 2
    # la xemeneia, que surt pel sostre, i la campana de ferro
    for y in range(0, 52):
        for x in range(cx - 18, cx + 19):
            u = (x - cx) / 18
            cv.put(x, y, IRONF, 2.6 - u * 1.4 + (0.8 if y % 18 == 0 else 0) - abs(u) ** 6 * 1.4)
    cv.rect(cx - 20, 18, cx + 20, 20, IRONF, lambda x, y: 3.6 - (y - 18) * 0.8)
    def hood_lvl(x, y):
        t = (y - 50) / (top - 50)
        hw = 20 + (x1 - x0) / 2 * t
        u = (x - cx) / max(1, hw)
        v = 2.8 - u * 1.2 + (fbm(x / 6, y / 8, 21) - 0.5) * 1.0
        if (x - cx) % 14 == 0:
            v -= 1.0                                                                  # juntes de les planxes
        return v
    cv.poly([(cx - 20, 50), (cx + 20, 50), (x1 + 4, top), (x0 - 4, top)], IRONF, hood_lvl)
    for i in range(-5, 6):                                                            # reblons de la campana
        t = 0.9
        cv.put(cx + i * 14 * t, top - 3, IRONF, 4.6)
    cv.rect(x0 - 6, top - 1, x1 + 6, top + 3, IRONF, lambda x, y: 3.8 - (y - top + 1) * 0.5)
    cv.tint(x0, 50, x1, top, (110, 50, 26), lambda x, y: 0.35 * fbm(x / 5, y / 9, 22) ** 2)
    # el cos de maó refractari, amb tirants i cèrcols de ferro
    brick_wall(cv, x0, top + 4, x1, base, base=3.0, seed=23, bw=10, bh=4,
               soot=lambda x, y: 0.9 * max(0.0, 1 - abs(x - cx) / 40) * max(0.0, 1 - abs(y - 132) / 30))
    for bx in (x0 + 4, x1 - 6):                                                       # els muntants
        cv.rect(bx, top + 4, bx + 2, base, IRONF, lambda x, y: 3.8 - (x - bx) * 0.8)
    for by in (top + 16, base - 10):                                                  # els tirants
        cv.rect(x0, by, x1, by + 2, IRONF, lambda x, y: 3.6 - (y - by) * 0.8)
        for bx in (x0 + 5, x1 - 5):
            cv.disc(bx, by + 1, 2.4, 2.4, IRONF, 4.6)
    # la boca, d'arc, amb el marc de ferro colat
    bcx, btop, bbot, bw = BOCA[0], 142, 198, 28
    spring = 156
    for y in range(btop - 6, bbot + 1):
        for x in range(bcx - bw - 6, bcx + bw + 7):
            dx = x - bcx
            if y < spring:
                r = math.hypot(dx, (y - spring) * (bw / (spring - btop)))
                inner, outer = r <= bw, r <= bw + 6
            else:
                inner, outer = abs(dx) <= bw, abs(dx) <= bw + 6
            if inner:
                d = (y - btop) / (bbot - btop)
                if fire == 0:
                    v = 0.6 + max(0.0, d - 0.7) * 3 + (fbm(x / 3, y / 3, 25) - 0.5) * 0.8      # cendra freda
                    cv.put(x, y, COAL, v, lit=0)
                else:
                    hot = 0.8 + d ** 1.5 * 4.6 + (fbm(x / 4, y / 3, 26) - 0.5) * 1.6 + fire * 0.5
                    cv.put(x, y, FIREF, hot - abs(dx) / bw * 1.6, lit=0)
            elif outer:
                ang = math.atan2(y - spring, dx)
                cv.put(x, y, IRONF, 3.4 - math.cos(ang) * 0.8 - (1.4 if hr(int(ang * 10), 3) > 0.85 else 0))
    if fire == 0:
        for i in range(10):                                                           # carbó i cendra a la solera
            cv.disc(bcx - 20 + hr(i, 1) * 40, bbot - 4 - hr(i, 2) * 6, 2 + hr(i, 3) * 2, 1.4, SLAGF,
                    lambda nx, ny: 2.6 - ny, lit=0)
    else:
        for i in range(26):                                                           # les brases
            bx = bcx - 24 + hr(i, 4) * 48
            by = bbot - 3 - hr(i, 5) * 8
            cv.disc(bx, by, 2 + hr(i, 6) * 2, 1.6, FIREF, lambda nx, ny: 6.4 - ny * 2 - (1.6 if fire == 1 else 0) +
                    hr(i, 7) * 0.8, lit=0)
            cv.flat(bx, by + 2, FIREF[1])
    # la porta de ferro de la boca, aixecada (penja d'una cadena)
    cv.rect(bcx - bw - 2, btop - 18, bcx + bw + 2, btop - 8, IRONF, lambda x, y: 3.2 - (y - btop + 18) * 0.1 +
            (fbm(x / 4, y / 3, 27) - 0.5) * 0.8)
    cv.rect(bcx - bw - 2, btop - 8, bcx + bw + 2, btop - 8, COAL, 1.0)
    cv.line(bcx, btop - 18, bcx + 4, top + 6, IRONF, 2.6)
    # la solera de ferro i el canal de colada, cap a la dreta
    cv.rect(bcx - bw - 8, bbot, bcx + bw + 8, bbot + 6, IRONF, lambda x, y: 4.2 - (y - bbot) * 0.5)
    # la tovera: el tub de la manxa que entra pel costat
    cv.rect(x1 - 2, 182, x1 + 14, 188, IRONF, lambda x, y: 4.0 - abs(y - 184) * 0.6)
    # una placa de fosa amb l'any
    cv.rect(cx + 40, top + 24, cx + 66, top + 34, IRONF, 3.2)
    text(cv, '1907', cx + 45, top + 27, IRONF, 5.4)


# ─── La manxa ──────────────────────────────────────────────────────────────

def manxa(cv, fire=0):
    """La manxa de la fosa: un fol gros de cuir (dues posts en falca i els plecs) sobre un cavallet, i la palanca:
    una biga que bascula en un pal, lligada al fol per una barra; de l'altra punta penja la cadena amb el mànec."""
    hx, hy = 350, 186                         # la frontissa del fol (a tocar del forn)
    x1 = 432                                  # la punta del fol
    open_ = 26 if fire == 0 else 18
    # el cavallet
    for lx in (hx + 8, x1 - 12):
        cv.poly([(lx - 4, 212), (lx, 192), (lx + 3, 192), (lx + 7, 212)], PLANKF, lambda x, y: 3.2 - (x - lx) * 0.1)
    cv.rect(hx + 2, 190, x1 - 4, 193, PLANKF, lambda x, y: 3.8 - (y - 190) * 0.5)
    # la post de baix
    cv.rect(hx, 186, x1, 189, PLANKF, lambda x, y: 4.0 - (y - 186) * 0.6 + (0.6 if x % 17 == 0 else 0))
    top = lambda x: hy - 2 - open_ * (x - hx) / (x1 - hx)
    # els plecs de cuir: un ventall de plecs que surten de la frontissa
    for x in range(hx + 1, x1):
        ty = top(x)
        for y in range(int(ty) + 2, 186):
            k = (186 - y) / max(1.0, 186 - ty)                                          # 0 a baix, 1 a dalt
            fold = (k * 5) % 1
            v = 2.6 + (1.4 if fold < 0.35 else -0.2) - (1.2 if 0.9 < fold else 0) - (x - hx) * 0.004
            if x > x1 - 3:
                v -= 1.0
            cv.put(x, y, LEATHER, v)
    # la post de dalt (gruixuda, amb dos cèrcols de ferro) i el pes de pedra a sobre
    for x in range(hx - 4, x1 + 4):
        y = top(min(x, x1))
        for k in range(4):
            cv.put(x, y - k + 2, PLANKF, 4.6 - k * 0.7 - (1.4 if k == 0 else 0))
    for bx in (hx + 30, hx + 62):
        for k in range(5):
            cv.put(bx, top(bx) - 2 + k, IRONF, 4.0)
            cv.put(bx + 1, top(bx) - 2 + k, IRONF, 2.6)
    # el broc: un tub de ferro que entra a la tovera del forn
    cv.rect(FORN[1] + 2, 181, hx + 2, 186, IRONF, lambda x, y: 4.2 - abs(y - 183) * 0.7)
    cv.disc(hx - 2, 186, 4, 4, IRONF, lambda nx, ny: 4.0 - nx - ny)
    # la palanca: el pal de suport, la biga i la barra que baixa fins a la punta del fol
    px, py = 448, 112
    cv.rect(px - 2, py, px + 2, 212, PLANKF, lambda x, y: 3.8 - (x - px + 2) * 0.5 - (0.6 if y % 19 == 0 else 0))
    cv.poly([(px - 7, 212), (px + 7, 212), (px + 4, 206), (px - 4, 206)], PLANKF, 2.6)
    ax, ay = x1 - 6, top(x1 - 6) - 2
    bl, br = (ax - 4, py + 6), (506, py - 8)
    for k in range(4):
        cv.line(bl[0], bl[1] + k - 2, br[0], br[1] + k - 2, PLANKF, 4.6 - k * 0.8)
    cv.disc(px, py, 3.4, 3.4, IRONF, lambda nx, ny: 4.6 - nx - ny)                       # l'eix
    cv.disc(px, py, 1, 1, COAL, 1.0)
    for k in range(2):                                                                   # la barra
        cv.line(ax + k, ay, bl[0] + 2 + k, bl[1] + 2, IRONF, 3.6 - k * 1.2)
    cv.disc(ax, ay, 2, 2, IRONF, 4.4)
    # la cadena i el mànec, a l'altra punta
    cy = br[1] + 2
    for y in range(cy, 170, 3):
        cv.disc(br[0] - 2, y, 1, 1.4, IRONF, 4.4 - (1.4 if (y // 3) % 2 else 0))
    cv.rect(br[0] - 9, 170, br[0] + 5, 173, PLANKF, lambda x, y: 4.6 - (y - 170) * 0.6)

# ─── Termòmetre, rascle, metall ────────────────────────────────────────────

def termometre(cv, fire=0):
    cx, cy, r = DIAL
    # el capil·lar que ve del forn i el suport de la pilastra
    cv.line(cx + r + 1, cy + 8, FORN[0] - 6, cy + 8, IRONF, 3.0)
    cv.line(cx + r + 1, cy + 9, FORN[0] - 6, cy + 9, COAL, 1.0)
    cv.rect(cx - 3, cy + r, cx + 3, cy + r + 10, IRONF, 3.0)
    cv.disc(cx, cy, r + 3, r + 3, TIN, lambda nx, ny: 4.6 - nx * 1.2 - ny * 1.2)          # el bisell de llautó
    cv.disc(cx, cy, r, r, WHITEV, lambda nx, ny: 3.4 - ny * 0.6 - nx * 0.3)
    # la zona vermella (de 9 a 10)
    for a in range(0, 360, 2):
        an = math.radians(a)
        frac = ((a - 135) % 360) / 270
        if frac <= 1:
            for d in (r - 1, r - 2):
                x, y = cx + math.cos(an) * d, cy + math.sin(an) * d
                if frac > 0.78:
                    cv.put(x, y, REDP, 4.4, lit=0)
            if int(frac * 270) % 27 == 0:
                for d in range(r - 4, r - 1):
                    cv.put(cx + math.cos(an) * d, cy + math.sin(an) * d, COAL, 1.0)
    text(cv, 'C', cx - 1, cy + 5, COAL, 1.4)
    frac = {0: 0.04, 1: 0.5, 2: 0.88}[fire]
    an = math.radians(135 + frac * 270)
    cv.line(cx, cy, cx + math.cos(an) * (r - 3), cy + math.sin(an) * (r - 3), REDP, 3.0, lit=0)
    cv.line(cx, cy, cx - math.cos(an) * 3, cy - math.sin(an) * 3, COAL, 1.0, lit=0)
    cv.disc(cx, cy, 1.4, 1.4, IRONF, 4.0)
    cv.put(cx - r * 0.5, cy - r * 0.55, WHITEV, 7.0, lit=0)                                # reflex del vidre
    cv.put(cx - r * 0.45, cy - r * 0.6, WHITEV, 7.0, lit=0)


def rascle(cv):
    """El rascle de l'escòria: un pal de ferro llarg amb la pala plana, recolzat a la paret."""
    for k in range(2):
        cv.line(540 + k, 104, 522 + k, 214, IRONF, 4.0 - k * 1.8)
    cv.poly([(512, 210), (532, 212), (532, 218), (512, 216)], IRONF, lambda x, y: 3.4 - (y - 210) * 0.2)
    cv.rect(538, 100, 544, 106, PLANKF, 3.4)                                               # el mànec
    cv.tint(512, 208, 532, 218, (90, 50, 30), 0.35)


def metall(cv):
    """El metall per fondre: la pila de comptadors de Verne que han portat els miners, i una carretilla."""
    pila_comptadors(cv, 70, 156, 236, 38, seed=11)
    # la carretilla, mig plena
    cv.poly([(84, 206), (124, 206), (118, 222), (90, 222)], IRONF, lambda x, y: 3.0 - (x - 84) * 0.02)
    cv.rect(84, 205, 124, 206, IRONF, 4.6)


# ─── El pas cap a la colada ────────────────────────────────────────────────

def pas(cv):
    """Una obertura gran a la paret de la dreta: l'altra banda de la nau, fosca, amb el gresol que s'hi endevina."""
    x0, x1, top = 568, 640, 64
    cv.rect(x0 - 6, top - 6, x1, top - 1, MORTAR, lambda x, y: 3.0 - (y - top + 6) * 0.2)
    for y in range(top, NAVE_FLOOR + 1):
        for x in range(x0, x1):
            cv.put(x, y, COAL, 0.8 + (y - top) * 0.004 + (fbm(x / 10, y / 10, 33) - 0.5) * 0.6, lit=0)
    cv.rect(x0 - 6, top, x0 - 1, NAVE_FLOOR, MORTAR, lambda x, y: 2.6 - (x - x0 + 6) * 0.3)
    # el pont grua de l'altra banda i el gresol, en silueta
    cv.rect(x0, 86, x1, 92, IRONF, 1.4, lit=0)
    cv.line(612, 92, 612, 128, IRONF, 1.2, lit=0)
    cv.poly([(598, 130), (626, 130), (622, 156), (602, 156)], IRONF, 1.2, lit=0)
    cv.rect(x0 + 4, 170, x0 + 40, NAVE_FLOOR, SLAGF, 1.2, lit=0)                         # sacs
    cv.tint(x0, top, x1, NAVE_FLOOR, (60, 40, 40), 0.2)


# ─── Composició ────────────────────────────────────────────────────────────

def draw(cv, fire=0):
    nau(cv)
    foundry_floor(cv, NAVE_FLOOR, RH - 1, seed=9, plates=((168, 206, 344, 226), (344, 212, 430, 230)))
    porta(cv)
    pas(cv)
    forn(cv, fire)
    termometre(cv, fire)
    rascle(cv)
    manxa(cv, fire)
    metall(cv)
    # ombres al terra
    cv.darken(160, 204, 350, 214, lambda x, y: 0.7 if fire == 0 else 0)
    cv.darken(346, 210, 440, 214, 0.6)
    cv.darken(60, 234, 166, 240, lambda x, y: 0.8 if ((x - 113) / 50) ** 2 + ((y - 236) / 3) ** 2 <= 1 else 0)
    if fire:
        col, k, rr = WARM[fire]
        bx, by = BOCA
        cv.tint(0, 0, W - 1, RH - 1, col, lambda x, y: k * max(0.0, 1 - math.hypot(x - bx, (y - by) * 1.2) / rr) ** 1.4)
        cv.glow(bx, by + 6, 46 + fire * 10, (255, 200, 120), 0.5 + fire * 0.15)
        # la llum del foc al terra, davant la boca
        cv.tint(bx - 70, 206, bx + 70, RH - 1, (255, 170, 80),
                lambda x, y: 0.2 * fire * max(0.0, 1 - math.hypot((x - bx) / 70, (y - 206) / 40)))
    for y in range(RH, H):
        for x in range(W):
            cv.flat(x, y, (0, 0, 0))


def bg(cv):
    draw(cv, 0)


# ─── Decorats ──────────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _render(fire):
    cv = Canvas(light=LIGHTS[fire])
    draw(cv, fire)
    return cv.img


def _fire_prop(fire):
    def fn(cv):
        cv.img.alpha_composite(_diff(_render(fire), _render(0)))
    return fn


forn_ences = _fire_prop(1)
forn_fort = _fire_prop(2)

PROPS = {'forn_ences': forn_ences, 'forn_fort': forn_fort}


# ─── Animacions ─────────────────────────────────────────────────────────────

def _flames(fire, n=8):
    """Les flames que surten de la boca i llepen l'arc; més altes i més blanques a tota manxa."""
    bcx, bbot, bw = BOCA[0], 196, 26
    frames = []
    hmax = 30 if fire == 1 else 44
    for f in range(n):
        img = Image.new('RGBA', (W * Canvas.S, H * Canvas.S), (0, 0, 0, 0))
        cv = Canvas(light=LIGHTS[fire], img=img)
        ph = f / n * 2 * math.pi
        for y in range(bbot - hmax, bbot - 2):
            t = (bbot - 2 - y) / hmax
            for x in range(bcx - bw, bcx + bw + 1):
                u = (x - bcx) / bw
                # que no surtin de l'arc
                spring, btop = 156, 142
                if y < spring and math.hypot(x - bcx, (y - spring) * (28 / (spring - btop))) > 27:
                    continue
                sway = math.sin(ph + t * 5 + u * 2) * 0.12 * t
                tongue = 0.5 + 0.5 * math.sin((u + sway) * 9 + ph * 2 + 1.3 * math.sin(ph + u * 3))
                hgt = (1 - abs(u) ** 2.2) * (0.45 + 0.6 * tongue)
                if t < hgt:
                    lvl = 6.8 - t / max(0.05, hgt) * 3.6 - abs(u) * 0.6 + (0.6 if fire == 2 else -0.2)
                    if lvl > 3.4:
                        cv.put(x, y, FIREF, lvl, lit=0)
        frames.append(img)
    return frames


def _frames_guspires():
    """Guspires que salten de la boca i cauen fent un arc (més com més fort)."""
    bcx, by = BOCA[0], 168
    frames = []
    n = 16
    for f in range(n):
        cv = Canvas(transparent=True)
        for k in range(9):
            s = ((f / n) + hr(k, 1)) % 1
            vx = (hr(k, 2) - 0.3) * 70
            vy = -40 - hr(k, 3) * 40
            x = bcx + (hr(k, 4) - 0.5) * 30 + vx * s
            y = by + vy * s + 90 * s * s
            if s < 0.85 and 0 <= x < W and 0 <= y < RH:
                c = FIREF[6] if s < 0.25 else FIREF[5] if s < 0.55 else FIREF[3]
                cv.flat(x, y, c)
                if s < 0.4:
                    px, py = int(x - vx * 0.02), int(y - (vy + 180 * s) * 0.02)
                    if 0 <= px < W and 0 <= py < RH:
                        cv.flat(px, py, FIREF[4])
        frames.append(cv.img)
    return frames


ANIMS = {'foc': {'frames': lambda: _flames(1), 'frameDuration': 100},
         'foc_fort': {'frames': lambda: _flames(2), 'frameDuration': 80},
         'guspires': {'frames': _frames_guspires, 'frameDuration': 70}}
