"""
Aigua Verne — `fosa_colada` (L: persones de ≈83 px): la mateixa nau de la fosa, l'altra banda: on es cola. EN 3D
(hd640/tres_d.py), a 1×.

La càmera mira la cantonada de la dreta (la del forn mira la de l'esquerra: és la mateixa nau, vista des de l'altra
punta): la paret de la dreta fuig cap al fons, amb un finestral en escorç i el carril de la grua a les mènsules; la
paret del fons, de maó negre, té a l'esquerra el **pas** cap al forn (una obertura fosca per on arriba una claror
càlida). Travessant la nau per dalt, en diagonal, el **pont grua**: la biga groga de gelosia, amb el carro penjat i el
polispast, del qual penja el **gresol** (un tronc de con de ferro, amb l'ansa, els munyons, el volant del sinfí en
escorç i el broc), vist una mica des de dalt: se'n veu la boca. Del pont penja la **botonera** groga (`grua_pont`). A
terra, sota el gresol, el **llit de colada**: una fossa de sorra negra amb el marc de ferro, girada, on va el motlle.
A la dreta, la pila de grava i els sacs de la **sorra** d'aquí (`sorra_pedra`), amb la pala. Una columna de ferro
colat aguanta la biga del carril de l'esquerra. Pel terra (es passa per darrere de tot): una pila de lingots, una
pila de caixes de motlle buides, una filera de lingoteres davant del llit, una carretilla de ferralla i unes tenalles.
En primer pla, fosc i tallat per la vora: un pilar de maó a l'esquerra, un gresol vell a terra a la dreta, les
cadenes d'un altre polispast i un munt de sorra negra amb la pala.

La llum: la claror freda dels finestrals, el llum de taller penjat sobre el llit (el bassal de llum i l'ombra de
contacte dels personatges en surten) i la claror càlida del pas. Amb el gresol ple (`gresol_ple`), el metall fos
il·lumina la nau des de la boca del gresol: la mateixa escena il·luminada amb aquesta llum, i la diferència tenyida de
taronja (cada cara segons com la mira), amb les ombres llargues pel terra. El motlle preparat (sempre al llit quan el
gresol és ple) també s'encén: `gresol_ple` el porta pintat a dins, i al `.room.json` va per sobre de
`motlle_preparat` (zIndex 5; `claus_fetes`, 5; `fum_gresol`, 6). Les capes del davant tenen la versió amb el metall
fos (`variants`); la de davant del gresol no porta la boca, on bull el metall (`fum_gresol`).

Decorats (PROPS): `motlle_posat` (la caixa del motlle, buida, al llit: hi queda quan ja s'han tret les claus,
`claus_fetes`), `motlle_preparat` (plena de sorra fina, amb les
tres claus marcades i el bebedor), `gresol_ple`, `claus_fetes` (les tres claus, roents, al motlle): tots al món, damunt
el llit. ANIMS: `fum_gresol` (el metall fos que bull a la boca del gresol, el vapor i les guspires).

El detall pla (fosa_colada_pla_comu.py, la sala d'abans): la paret amb els finestrals i el pas, la biga amb el rètol,
la botonera i els sacs es projecten com a textures.

El món: x a la dreta, y amunt, z cap al fons (860 = la paret del fons, 1100 = la de la dreta); 1 unitat = 1 píxel de
sala a la distància on un personatge fa la seva mida de lluny (83 px).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
import numpy as np
from PIL import Image

from hd.pix import Canvas, Light, W, H, hr, B4
from hd.rooms.comu import _diff
from hd.rooms.exterior import fbm
from hd640.rooms import fosa_colada_pla_comu as PL
from hd640.rooms.ferrum_comu import (RH, SLAGF, SOOT, MORTAR, COB, COAL, IRONF, PLANKF, RUSTF, nave_wall, crane_rail)
from hd640.rooms.fosa_forn import (_brick, _terra, _local, _peu, cilindre, columna, tronc, lingots, lingoteres,
                                   carretilla, tenalles, escoria)
from hd640.tres_d import Camera, Escena, Llum, llum_personatges

BOTTOM = RH - 1
ZB = 860                                           # la paret del fons
XW = 1100                                          # la paret de la dreta
KW = 1.8                                           # unitats del món per píxel del dibuix pla de la paret del fons
HW = (198 - 31) * KW                               # l'alçada de les parets
PAS = (250.0, 250.0 + 77 * KW, (198 - 58) * KW)    # el pas al forn, a la paret del fons: x0, x1, alçada
ZG = 580                                           # el pont grua: la z de la biga
GIRDER = (232.0, 270.0)                            # la biga: y de baix i de dalt
GX0 = -300.0                                       # (la biga ve de l'altra banda de la nau)
LADLE = (722.0, 580.0, 96.0, 154.0, 27.0, 36.0)    # el gresol: x, z, y de baix i de dalt, radi de baix i de dalt
BED = (724.0, 570.0, 250.0, 104.0, 0.14)           # el llit de colada: centre (x, z), llarg, ample, angle
MOLD = (744.0, 568.0, 92.0, 50.0, 16.0)            # la caixa del motlle: centre (x, z), llarg, ample, alt
PENDANT = (880.0, 580.0, 104.0)                    # la botonera: x, z i l'altura de baix (fora del camí del gresol)
GX = {'llit': LADLE[0], 'canal': 500.0}            # on para el carro (la x del gresol): damunt el llit i sota el canal
GY = {'dalt': LADLE[2], 'baix': 40.0}              # on queda el cul del gresol: penjat i avall
GH = LADLE[3] - LADLE[2]                           # l'alçada del gresol
CANAL = ((PAS[0] + 70, 138.0, ZB + 110), (GX['canal'], 112.0, 604.0))    # el canal de colada: del pas al broc
COL = (440.0, 560.0)                               # la columna de ferro colat (x, z)
SORRA = (990.0, 690.0)                             # la pila de grava (x, z)
LAMP = (856.0, 176.0, 520.0)
OLD_LADLE = (912.0, 396.0)
BANC = (512.0, 752.0, -0.5, 116.0, 46.0)           # el banc dels motlles: centre (x, z), angle, llarg, ample
LINGOTS = (372.0, 524.0, 0.3)                      # la pila de lingots al palet, a l'esquerra de la columna
LINGOTERES = (804.0, 470.0, 0.14)                  # la filera de lingoteres, davant del llit
CARRETO = (910.0, 512.0, -0.65)                    # la carretilla amb ferralla i bebedors tallats
TENALLES = (610.0, 470.0, -0.35)                   # unes tenalles a terra
CAIXES = (530.0, 650.0, 0.25)                      # una pila de caixes de motlle buides (x, z, angle)
MUNT = (600.0, 418.0, 54.0)                        # un munt de sorra negra, en primer pla (x, z, radi)

CAM = Camera(pos=(560, 185, 60), yaw=0.17, pitch=0.11, f=430, centre=(310, 108))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)
PLA = Light(ambient=0.2, vignette=None, floor_fade=None)
AMBIENT = -1.15
WINDOWS = (300, 470)                               # els finestrals de la paret del fons (x del dibuix pla)
WIN_DRETA = (540.0, 540.0 + 34 * KW)               # el finestral de la paret de la dreta (z0, z1)
LLUMS = [Llum(((wx + 14) * KW, 220, ZB - 70), 400, 0.9, power=1.4) for wx in WINDOWS] + [
    Llum((XW - 60, 220, sum(WIN_DRETA) / 2), 380, 1.0, power=1.4),
    Llum((LAMP[0], LAMP[1] - 14, LAMP[2]), 300, 2.2, power=1.4),             # el llum de taller
    Llum(((PAS[0] + PAS[1]) / 2, 60, ZB - 30), 300, 1.0, power=1.6),         # la claror del forn, pel pas
]
FOS = Llum((LADLE[0], LADLE[3] + 16, LADLE[1]), 820, 3.6, power=1.15)     # el metall fos, a la boca del gresol


def _fos(x, gy=LADLE[2]):
    """La llum del metall fos amb el gresol a `x` (i el cul a `gy`)."""
    return Llum((x, gy + GH + 16, LADLE[1]), 820, 3.6, power=1.15)
TARONJA = (1.6, 0.66, 0.22)
SAND = PL.SAND
MOLTEN = PL.MOLTEN
YELLOW = PL.YELLOW
GRAVEL = PL.GRAVEL


# ─── Les textures: la colada plana ───────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _paret():
    """La paret del fons, de cara: maó negre, pilastres, els finestrals, el carril de la grua i el pas al forn."""
    cv = Canvas(light=PLA)
    nave_wall(cv, 0, W - 1, top=31, seed=9, windows=tuple((wx, 28) for wx in WINDOWS), pilasters=(250, 400, 560))
    crane_rail(cv, 86)
    tmp = Canvas(light=PLA)
    PL.pas(tmp)
    cv.img.paste(tmp.img.crop((0, 58, 77, 199)), (round(PAS[0] / KW), 58))
    return cv.img


@functools.lru_cache(maxsize=None)
def _biga():
    cv = Canvas(light=PLA)
    PL.biga(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _botonera():
    cv = Canvas(light=PLA)
    PL.botonera(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _sacs():
    cv = Canvas(light=PLA, transparent=True)
    PL.sacs(cv)
    return cv.img


# ─── Peces ──────────────────────────────────────────────────────────────────

def con(e, sid, cx, cz, r0, r1, y0, y1, ramp, lvl, n=20):
    """Un tronc de con vertical (radi r0 a y0, r1 a y1): les facetes que es veuen. `lvl(angle, y, P)`."""
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        c0, s0, c1, s1 = math.cos(a0), math.sin(a0), math.cos(a1), math.sin(a1)
        e.quad(sid, (cx + r1 * c0, y1, cz + r1 * s0), (cx + r1 * c1, y1, cz + r1 * s1),
               (cx + r0 * c1, y0, cz + r0 * s1), (cx + r0 * c0, y0, cz + r0 * s0), ramp=ramp,
               lvl=lambda s, t, P: lvl(math.atan2(P[2] - cz, P[0] - cx), P[1], P))


def disc(e, sid, cx, y, cz, r, ramp, lvl, ri=0.0):
    """Un disc horitzontal (o un anell, si ri > 0) a l'altura y."""
    sq = ((cx - r, y, cz + r), (cx + r, y, cz + r), (cx + r, y, cz - r), (cx - r, y, cz - r))
    e.quad(sid, *sq, ramp=ramp, lvl=lvl, dues_cares=True,
           forma=lambda s, t: ri * ri <= (s - r) ** 2 + (t - r) ** 2 <= r * r)


def nau(e, taller=True):
    zn = CAM.pos[2] - 60
    e.quad('sostre', (-400, HW, zn), (XW, HW, zn), (XW, HW, ZB), (-400, HW, ZB), ramp=COAL,
           lvl=lambda s, t, P: 0.6 + (fbm(P[0] / 80, P[2] / 60, 3) - 0.5) * 0.6, dues_cares=True)
    for z in (420, ZB - 20):
        e.cable('sostre', [(-400, HW - 8, z), (XW, HW - 8, z)], IRONF, 1.6, gruix=6)
    # la paret del fons (el dibuix pla; a l'esquerra del dibuix, més maó)
    e.quad('paret_fons', (-600, HW, ZB), (0, HW, ZB), (0, 0, ZB), (-600, 0, ZB), ramp=SOOT,
           lvl=lambda s, t, P: _brick(21)(P[0], P[1]))
    e.quad('paret_fons', (0, HW, ZB), (W * KW, HW, ZB), (W * KW, 0, ZB), (0, 0, ZB), tex=(_paret(), (0, 31, W, 198)))
    # la paret de la dreta: maó, amb el finestral en escorç (un finestral del dibuix pla)
    e.quad('paret_dreta', (XW, HW, ZB), (XW, HW, zn), (XW, 0, zn), (XW, 0, ZB), ramp=SOOT,
           lvl=lambda s, t, P: _brick(25)(P[2], P[1]) - 0.9 * max(0.0, 1 - (HW - P[1]) / 120))
    z0, z1 = WIN_DRETA
    wx = WINDOWS[0]
    e.quad('paret_dreta', (XW - 0.5, (198 - 30) * KW, z1), (XW - 0.5, (198 - 30) * KW, z0),
           (XW - 0.5, (198 - 107) * KW, z0), (XW - 0.5, (198 - 107) * KW, z1),
           tex=(_paret(), (wx - 3, 30, wx + 31, 107)))
    for z in (430, 700):                                                                  # les pilastres
        e.caixa('paret_dreta', XW - 16, XW, 0, HW, z - 18, z + 18, SOOT, 2.4,
                cares={'esquerra': {'ramp': SOOT, 'lvl': lambda s, t, P: _brick(27, 2.8)(P[2], P[1])},
                       'davant': {'ramp': SOOT, 'lvl': lambda s, t, P: _brick(28, 2.2)(P[0], P[1])}})
        e.caixa('paret_dreta', XW - 30, XW - 16, 226, 238, z - 20, z + 20, MORTAR, 3.2)    # la mènsula
    # el carril de la grua de la dreta, a les mènsules
    e.caixa('paret_dreta', XW - 34, XW - 14, 238, 252, zn, ZB, IRONF, 2.4,
            cares={'esquerra': {'ramp': IRONF, 'lvl': lambda s, t, P: 2.8 - (1.2 if P[2] % 80 < 3 else 0)},
                   'sota': {'ramp': IRONF, 'lvl': 0.8}})
    # el terra
    e.quad('terra', (-600, 0, ZB), (XW, 0, ZB), (XW, 0, zn), (-600, 0, zn), ramp=COB, lvl=_terra)
    # el pas: els brancals que fan gruix i el terra de l'altra banda
    x0, x1, ph = PAS
    e.quad('pas_terra', (x0, 0.3, ZB + 120), (x1, 0.3, ZB + 120), (x1, 0.3, ZB), (x0, 0.3, ZB), ramp=COB,
           lvl=lambda s, t, P: 1.4 - t / 120)
    for bx in (x0 - 14, x1):
        e.caixa('pas', bx, bx + 14, 0, ph + 10, ZB - 16, ZB, MORTAR, 2.4,
                cares={'davant': {'ramp': MORTAR, 'lvl': lambda s, t, P: _brick(23, 2.8)(P[0], P[1])},
                       'esquerra': {'ramp': MORTAR, 'lvl': 1.8}, 'dreta': {'ramp': MORTAR, 'lvl': 1.6}})
    e.caixa('pas', x0 - 14, x1 + 14, ph, ph + 14, ZB - 16, ZB, MORTAR, 3.0)
    # la claror càlida del forn, que entra pel pas i s'estira pel terra cap a la càmera
    e.claror((x0, 0.5, ZB), (x1, 0.5, ZB), (x1 + 40, 0.5, ZB - 260), (x0 - 40, 0.5, ZB - 260), (220, 120, 60),
             lambda s, t: 0.38 * (1 - t / 263) ** 1.4 * min(1.0, (s + 4) / 30, (x1 - x0 + 4 - s) / 30))
    # el bassal de llum sota el llum de taller
    lx, _, lz = LAMP
    if taller:
        e.claror((lx - 160, 0.5, lz + 160), (lx + 160, 0.5, lz + 160), (lx + 160, 0.5, lz - 160), (lx - 160, 0.5, lz - 160),
                 (200, 170, 120), lambda s, t: 0.22 * max(0.0, 1 - math.hypot(s - 160, t - 160) / 160) ** 1.5)
    # els racons, foscos
    e.foscor('racons', (-600, 0.5, ZB), (XW, 0.5, ZB), (XW, 0.5, zn), (-600, 0.5, zn),
             lambda s, t: max(0.6 * max(0.0, 1 - t / 60), 0.5 * max(0.0, 1 - (XW + 600 - s) / 50)))
    e.foscor('cantonada', (XW - 120, HW, ZB - 0.5), (XW, HW, ZB - 0.5), (XW, 0, ZB - 0.5), (XW - 120, 0, ZB - 0.5),
             lambda s, t: 0.6 * max(0.0, s / 120) ** 1.5)
    e.foscor('dalt', (-600, HW, ZB - 0.6), (W * KW, HW, ZB - 0.6), (W * KW, HW - 140, ZB - 0.6),
             (-600, HW - 140, ZB - 0.6), lambda s, t: 0.55 * max(0.0, 1 - t / 140))
    e.foscor('dalt_dreta', (XW - 0.6, HW, ZB), (XW - 0.6, HW, zn), (XW - 0.6, HW - 140, zn), (XW - 0.6, HW - 140, ZB),
             lambda s, t: 0.55 * max(0.0, 1 - t / 140))
    # els feixos de llum dels finestrals
    for wx in WINDOWS:
        a0, a1 = wx * KW, (wx + 28) * KW
        e.claror((a0, 262, ZB - 2), (a1, 262, ZB - 2), (a1 - 70, 0, ZB - 330), (a0 - 70, 0, ZB - 330), (190, 150, 116),
                 lambda s, t, wx=wx: 0.22 * (1 - t / 420) * (0.5 + fbm(s / 12, t / 40, wx)))
    e.claror((XW - 2, 262, z1), (XW - 2, 262, z0), (XW - 300, 0, z0 - 60), (XW - 300, 0, z1 - 60), (190, 150, 116),
             lambda s, t: 0.22 * (1 - t / 420) * (0.5 + fbm(s / 12, t / 40, 77)))


def llit(e):
    """El llit de colada: el marc de ferro arran de terra i la sorra negra, amb restes de colades velles."""
    cx, cz, L, A, ang = BED
    Lo = _local((cx, cz), ang)

    def sorra(s, t, P):
        v = 1.8 + (fbm(s / 10, t / 5, 61) - 0.5) * 1.6 + (hr(int(s) // 2, int(t) // 2, 62) - 0.5) * 0.6
        i, j = int(s // 24), int(t // 24)
        if hr(i, j, 63) > 0.7:                                                           # rajolins d'escòria
            d = math.hypot(s - i * 24 - 12, (t - j * 24 - 12) * 1.4)
            if d < 4 + hr(i, j, 64) * 4:
                v += 1.6 - d * 0.2
        return v
    e.quad('llit', Lo(-L / 2, 0.4, A / 2), Lo(L / 2, 0.4, A / 2), Lo(L / 2, 0.4, -A / 2), Lo(-L / 2, 0.4, -A / 2),
           ramp=COB, lvl=sorra)
    for (u, w, l, a) in ((0, A / 2, L + 12, 6), (0, -A / 2, L + 12, 6), (-L / 2, 0, 6, A), (L / 2, 0, 6, A)):
        x, _, z = Lo(u, 0, w)
        e.caixa_girada('llit', x, z, l, a, 7, ang, IRONF, 3.0,
                       cares={'dalt': {'ramp': IRONF, 'lvl': 4.2}, 'davant': {'ramp': IRONF, 'lvl': 2.4}})


def pont_grua(e):
    """La biga de gelosia (la cara de davant, el dibuix pla), el carro penjat, el polispast i el ganxo."""
    y0, y1 = GIRDER
    x1 = XW - 36
    # la biga: la cara de baix, la de davant (la textura) i la de darrere, fosca
    e.quad('grua', (GX0, y0, ZG - 12), (x1, y0, ZG - 12), (x1, y0, ZG + 12), (GX0, y0, ZG + 12), ramp=YELLOW,
           lvl=lambda s, t, P: 1.6 - (1.0 if s % 26 < 3 else 0), dues_cares=True)
    e.quad('grua', (GX0, y1, ZG - 12), (x1, y1, ZG - 12), (x1, y0, ZG - 12), (GX0, y0, ZG - 12),
           tex=(_biga(), (0, PL.GIRDER[0], W, PL.GIRDER[1] + 1)))
    # el capçal, que roda pel carril de la dreta
    e.caixa('grua', x1, XW - 14, y0 - 6, y1 + 4, ZG - 40, ZG + 40, YELLOW, 2.6,
            cares={'davant': {'ramp': YELLOW, 'lvl': lambda s, t, P: 3.0 - (1.4 if abs(t - 22) < 2 else 0)},
                   'sota': {'ramp': YELLOW, 'lvl': 1.4}, 'esquerra': {'ramp': YELLOW, 'lvl': 2.4}})
    # (el carro, el cable i el gresol es mouen: són els decorats `gresol_*` i la capa `gresol_mou`)


def carro(e, x, gy):
    """El carro, penjat de la biga a `x`, amb el tambor i el motor; els dos ramals del cable fins al bossell i el
    ganxo, que és on penja l'ansa del gresol (amb el cul a l'altura `gy`)."""
    y0 = GIRDER[0]
    lz = LADLE[1]
    e.caixa('grua', x - 26, x + 26, y0 - 22, y0, ZG - 18, ZG + 18, IRONF, 2.8,
            cares={'davant': {'ramp': IRONF, 'lvl': lambda s, t, P: 3.0 + (0.8 if t < 2 else 0)},
                   'sota': {'ramp': IRONF, 'lvl': 1.6}})
    e.caixa('grua', x + 26, x + 38, y0 - 18, y0 - 2, ZG - 10, ZG + 6, YELLOW, 3.0)
    e.tub('grua', (x - 18, y0 - 26, ZG), (x + 18, y0 - 26, ZG), 6, IRONF, 2.6)
    hy = _ganxo(gy)
    for dx in (-6, 6):
        e.cable('grua', [(x + dx, y0 - 30, lz), (x + dx * 0.4, hy + 10, lz)], IRONF, 2.6, gruix=1.4)
    e.caixa('grua', x - 8, x + 8, hy, hy + 12, lz - 4, lz + 4, IRONF, 3.6,
            cares={'davant': {'ramp': IRONF, 'lvl': lambda s, t, P: 3.4 + (1.4 if 5 < t < 8 else 0)}})
    e.cable('grua', [(x, hy, lz), (x, hy - 6, lz), (x - 4, hy - 11, lz), (x + 3, hy - 13, lz)], IRONF, 3.6,
            gruix=2.4)


def _ganxo(gy):
    """L'altura del bossell amb el cul del gresol a `gy`."""
    return gy + GH + 44


class _Gira:
    """Una Escena que gira el que s'hi dibuixa `ang` radians (en el pla de la pantalla, x-y) al voltant d'un eix
    paral·lel a z que passa per `pivot`: per gronxar el gresol del ganxo i per bolcar-lo pels munyons."""

    def __init__(self, e, pivot, ang):
        self.e, self.px, self.py = e, pivot[0], pivot[1]
        self.c, self.s = math.cos(ang), math.sin(ang)

    def r(self, P):
        dx, dy = P[0] - self.px, P[1] - self.py
        return (self.px + dx * self.c - dy * self.s, self.py + dx * self.s + dy * self.c, P[2])

    def quad(self, sid, P0, P1, P2, P3, **kw):
        return self.e.quad(sid, self.r(P0), self.r(P1), self.r(P2), self.r(P3), **kw)

    def tub(self, sid, A, B, *a, **kw):
        return self.e.tub(sid, self.r(A), self.r(B), *a, **kw)

    def cable(self, sid, punts, *a, **kw):
        return self.e.cable(sid, [self.r(P) for P in punts], *a, **kw)


def gresol(e, x=LADLE[0], gy=LADLE[2], ple=False, ph=0.0, bolca=0.0, gronxa=0.0, buidant=False):
    """El gresol: un tronc de con de ferro rovellat amb els cèrcols, l'ansa fins al ganxo, els munyons, el volant del
    sinfí (en escorç) i el broc; la boca, vista des de dalt (el refractari, o el metall fos, que bull: `ph`, de 0 a 1).
    A `x`, amb el cul a `gy`; `gronxa`: radians que es gronxa del ganxo; `bolca`: radians que es bolca pels munyons
    cap a la dreta (cap al broc). `buidant`: el metall de la boca, ja mig buit (a mitja bolcada)."""
    cz, r0, r1 = LADLE[1], LADLE[4], LADLE[5]
    cx, y0, y1 = x, gy, gy + GH
    hy = _ganxo(gy) - 13
    my = y1 - 16
    eg = _Gira(e, (cx, hy), gronxa)                       # tot el gresol, gronxant-se del ganxo
    g = _Gira(eg, (cx, my), -bolca)                       # el cos, bolcat pels munyons

    def ferro(a, y, P):
        v = 2.8 - math.cos(a - 2.3) * 1.4 + (fbm(a * 3, y / 6, 51) - 0.5) * 1.2
        yy = P[1]
        if abs(yy - (y1 - 7)) < 2.4 or abs(yy - (y0 + 8)) < 2.4:
            v += 1.0                                                                       # els cèrcols
        return v
    ferro_g = lambda a, y, P: ferro(a, y, _desgira(P, eg, g))   # noqa: E731  (els cèrcols, on eren abans de girar)
    con(g, 'gresol', cx, cz, r0, r1, y0, y1, IRONF, ferro_g, n=22)
    disc(g, 'gresol', cx, y0, cz, r0, IRONF, 1.4)                                         # el cul (per sota)
    # la vora de dalt i la boca
    disc(g, 'gresol', cx, y1 + 0.2, cz, r1 + 2.5, IRONF, lambda s, t, P: 4.2 - (s - r1 - 2.5) / r1 * 0.8, ri=r1 - 3)
    if ple:
        nivell = -6 if buidant else -0.5
        disc(g, 'gresol_boca', cx, y1 + nivell, cz, r1 - 3, MOLTEN,
             lambda s, t, P: 4.0 - math.hypot(s - r1 + 3, t - r1 + 3) / r1 * 1.0
             + ((fbm(s / 5 + ph * 3, t / 3, 91) * (1 - ph) + fbm(s / 5 + (ph - 1) * 3, t / 3, 91) * ph) - 0.5) * 3.2)
    else:
        disc(g, 'gresol_boca', cx, y1 - 0.5, cz, r1 - 3, SLAGF, lambda s, t, P: 1.2 + (t / (2 * r1)) * 1.2)
    # el broc, cap a la dreta
    g.quad('gresol', (cx + r1 - 3, y1 + 2, cz - 7), (cx + r1 + 14, y1 + 6, cz - 5), (cx + r1 + 14, y1 + 6, cz + 5),
           (cx + r1 - 3, y1 + 2, cz + 7), ramp=IRONF, lvl=3.6, dues_cares=True)
    # els munyons, l'ansa fins al ganxo (l'ansa no es bolca: hi penja) i el volant del sinfí
    for k in (-1, 1):
        g.tub('gresol', (cx + k * (r1 - 2), my, cz), (cx + k * (r1 + 6), my, cz), 4, IRONF, 3.6)
        eg.cable('gresol', [g.r((cx + k * (r1 + 5), my, cz)), (cx + k * (r1 + 3), y1 + 16, cz), (cx + k * 4, hy, cz)],
                 IRONF, 3.4, gruix=2.6)
    wx, wy = cx - r1 - 14, my + 4
    g.quad('gresol', (wx, wy + 11, cz + 11), (wx, wy + 11, cz - 11), (wx, wy - 11, cz - 11), (wx, wy - 11, cz + 11),
           ramp=IRONF, dues_cares=True,
           lvl=lambda s, t, P: 4.0 if math.hypot(s - 11, t - 11) > 8.5 else 3.0,
           forma=lambda s, t: (8.4 <= math.hypot(s - 11, t - 11) <= 11) or
           (math.hypot(s - 11, t - 11) < 8.4 and min(abs(s - 11), abs(t - 11)) < 1.2) or math.hypot(s - 11, t - 11) < 2.2)
    g.tub('gresol', (wx, wy, cz), (cx - r1 + 2, wy - 2, cz), 2, IRONF, 3.0)
    return g


def _desgira(P, *gs):
    """El punt `P` (del món) tornat al lloc d'abans de girar-lo amb les `_Gira` (de fora a dins)."""
    for g in gs:
        dx, dy = P[0] - g.px, P[1] - g.py
        P = (g.px + dx * g.c + dy * g.s, g.py - dx * g.s + dy * g.c, P[2])
    return P


def broc(x, gy, bolca=0.0, gronxa=0.0):
    """On és la punta del broc (al món) amb el gresol a `x`, el cul a `gy` i bolcat `bolca`."""
    cz, r1 = LADLE[1], LADLE[5]
    y1 = gy + GH
    eg = _Gira(None, (x, _ganxo(gy) - 13), gronxa)
    g = _Gira(None, (x, y1 - 16), -bolca)
    return eg.r(g.r((x + r1 + 14, y1 + 6, cz)))


def canal(e):
    """El canal de colada: una canaleta de ferro en U que surt pel pas (el metall ve del forn), baixa en diagonal
    damunt dues cavalletes i acaba en un broc just darrere el lloc del gresol."""
    (ax, ay, az), (bx, by, bz) = CANAL
    dx, dz = bx - ax, bz - az
    n = math.hypot(dx, dz)
    ux, uz = dx / n, dz / n
    px, pz = -uz, ux                                     # (perpendicular, a terra)
    w, h = 9.0, 9.0
    A = lambda t, o, y=0.0: (ax + dx * t + px * o, ay + (by - ay) * t + y, az + dz * t + pz * o)   # noqa: E731
    # les cavalletes: dues potes i el travesser, i una riosta
    for t in (0.3, 0.72):
        top = A(t, 0)[1]
        for o in (-w - 6, w + 6):
            P = A(t, o)
            e.cable('canal', [(P[0], top - 2, P[2]), (P[0] + px * o * 0.3, 0, P[2] + pz * o * 0.3)], IRONF, 2.6, gruix=3)
        e.cable('canal', [A(t, -w - 6, -3), A(t, w + 6, -3)], IRONF, 3.0, gruix=3)
        P = A(t, w + 6)
        e.cable('canal', [(P[0], top - 30, P[2]), A(t + 0.12, w + 4, -3)], IRONF, 2.2, gruix=2)
    # la canaleta: el fons i els dos costats (per fora, rovell; per dins, el refractari ennegrit)
    e.quad('canal', A(0, -w), A(1, -w), A(1, w), A(0, w), ramp=IRONF, lvl=1.8, dues_cares=True)
    for o in (-w, w):
        e.quad('canal', A(0, o, h), A(1, o, h), A(1, o), A(0, o), ramp=IRONF, dues_cares=True,
               lvl=lambda s, t, P: 2.4 + (1.2 if t < 1.5 else 0) + (fbm(s / 6, t / 3, 66) - 0.5) * 1.2)
    e.quad('canal', A(0, -w + 1, 0.4), A(1, -w + 1, 0.4), A(1, w - 1, 0.4), A(0, w - 1, 0.4), ramp=SLAGF,
           lvl=lambda s, t, P: 1.4 + (fbm(s / 8, t / 3, 67) - 0.5) * 1.4)
    # el broc: la punta, que sobresurt i fa bec
    e.quad('canal', A(1, -w * 0.6), A(1.06, -w * 0.3, -3), A(1.06, w * 0.3, -3), A(1, w * 0.6), ramp=IRONF, lvl=3.2,
           dues_cares=True)


def botonera(e):
    """La botonera dels comandaments: penja del pont grua per un cable; la cara de davant, el dibuix pla."""
    x, z, yb = PENDANT
    e.cable('botonera', [(x, GIRDER[0], z), (x + 1, yb + 38, z)], COAL, 1.6, gruix=1.2)
    cx, top = PL.PENDANT
    e.caixa('botonera', x - 9.8, x + 9.8, yb, yb + 38, z - 5, z + 5, YELLOW, 2.6,
            cares={'davant': {'tex': (_botonera(), (cx - 6, top, cx + 8, top + 27))},
                   'dalt': {'ramp': YELLOW, 'lvl': 4.4}, 'dreta': {'ramp': YELLOW, 'lvl': 2.0},
                   'esquerra': {'ramp': YELLOW, 'lvl': 3.0}})


def sorra(e):
    """La pila de grava (pedra picada), la pala clavada i els sacs, contra la paret de la dreta."""
    x, z = SORRA
    e.foscor('ombra_sorra', (x - 120, 0.6, z + 70), (x + 80, 0.6, z + 70), (x + 80, 0.6, z - 70), (x - 120, 0.6, z - 70),
             lambda s, t: 0.6 * max(0.0, 1 - ((s - 100) / 100) ** 2 - ((t - 70) / 70) ** 2) * 1.5)
    img = _sacs()
    e.sprite('sorra', img.crop((588, 186, 628, 223)), (20, 36), (x + 60, 0, z + 60), escala_img=1.5)
    e.roca('sorra', (x - 10, 0, z + 10), 62, GRAVEL, 2.6, llum_dir=(-0.7, -0.6), aplana=0.5, seed=11)
    e.roca('sorra', (x - 60, 0, z - 20), 30, GRAVEL, 2.4, llum_dir=(-0.7, -0.6), aplana=0.45, seed=12)
    # la pala, clavada a la pila
    e.cable('sorra', [(x - 30, 30, z - 10), (x - 64, 128, z - 34)], PLANKF, 4.0, gruix=2.4)
    e.quad('sorra', (x - 36, 38, z - 4), (x - 22, 38, z - 16), (x - 18, 16, z - 12), (x - 32, 16, z), ramp=IRONF,
           lvl=3.6, dues_cares=True)
    e.cable('sorra', [(x - 70, 128, z - 38), (x - 58, 130, z - 30)], PLANKF, 4.2, gruix=3)
    e.sprite('sorra', img.crop((486, 182, 554, 218)), (34, 34), (x - 110, 0, z - 40), escala_img=1.5)


def banc(e):
    """El banc dels motlles, girat i separat de la paret: el tauler, les potes, dues caixes de motlle i el sedàs."""
    cx, cz, a, L, A = BANC
    Lo = _local((cx, cz), a)
    e.foscor('ombra_banc', Lo(-L / 2 - 10, 0.6, -A / 2 - 10), Lo(L / 2 + 10, 0.6, -A / 2 - 10),
             Lo(L / 2 + 10, 0.6, A / 2 + 10), Lo(-L / 2 - 10, 0.6, A / 2 + 10),
             lambda s, t: 0.55 * min(1.0, min(s, t, L + 20 - s, A + 20 - t) / 12))
    for u, w in ((-L / 2 + 5, -A / 2 + 5), (L / 2 - 5, -A / 2 + 5), (-L / 2 + 5, A / 2 - 5), (L / 2 - 5, A / 2 - 5)):
        x, _, z = Lo(u, 0, w)
        e.caixa_girada('banc', x, z, 5, 5, 40, a, PLANKF, 2.4)
    e.caixa_girada('banc', cx, cz, L, A, 5, a, PLANKF, 3.0, y0=40,
                   cares={'dalt': {'ramp': PLANKF, 'lvl': lambda s, t, P: 4.0 - (1.2 if t % 11.5 < 1.2 else 0)
                                   + (fbm(s / 8, t / 3, 71) - 0.5) * 0.8},
                          'davant': {'ramp': PLANKF, 'lvl': 2.6}, 'dreta': {'ramp': PLANKF, 'lvl': 1.8},
                          'esquerra': {'ramp': PLANKF, 'lvl': 2.2}})
    for (u, w, h, k) in ((-30, 0, 14, 0), (-30, 0, 14, 1), (26, -4, 12, 0)):
        x, _, z = Lo(u, 0, w)
        e.caixa_girada('banc', x, z, 40, 26, h, a + 0.1 * k, IRONF, 3.0, y0=45 + k * 14,
                       cares={'dalt': {'ramp': IRONF, 'lvl': lambda s, t, P: 1.2 if 3 < s < 37 and 3 < t < 23 else 4.4}})
    x, _, z = Lo(34, 0, 10)
    disc(e, 'banc', x, 46, z, 13, PL.TIN, 3.4, ri=10.5)                                   # el sedàs
    disc(e, 'banc', x, 45.8, z, 10.5, SAND, lambda s, t, P: 3.0 + (0.8 if (int(s) + int(t)) % 2 else 0))


def llum_taller(e):
    """El llum de taller penjat sobre el llit: el cable, la pantalla de llauna i la bombeta."""
    x, y, z = LAMP
    e.cable('llum', [(x, HW, z), (x, y + 10, z)], COAL, 1.4, gruix=1.2)
    tronc(e, 'llum', x, z, 30, 30, 8, 8, z, y - 6, y + 10, PL.TIN, lambda s, t, P: 3.6 - t * 0.08)


def primer_pla(e):
    """Fosc i tallat per la vora: el pilar de maó de l'esquerra, un gresol vell a terra a la dreta, les cadenes i un
    munt de sorra negra amb la pala."""
    mx, mz, mr = MUNT
    e.roca('primer_pla', (mx, 0, mz), mr, COAL, 2.0, llum_dir=(-0.6, -0.7), aplana=0.55, seed=31)
    e.cable('primer_pla', [(mx + 8, 22, mz + 4), (mx + 34, 46, mz - 14)], PLANKF, 1.6, gruix=3)
    e.quad('primer_pla', (mx - 4, 24, mz + 10), (mx + 12, 24, mz), (mx + 14, 8, mz + 2), (mx - 2, 8, mz + 12), ramp=IRONF,
           lvl=1.8, dues_cares=True)
    e.caixa('primer_pla', 320, 392, 0, HW + 40, 400, 456, SOOT, 1.0,
            cares={'dreta': {'ramp': SOOT, 'lvl': lambda s, t, P: _brick(33, 1.2)(P[2], P[1])},
                   'davant': {'ramp': SOOT, 'lvl': lambda s, t, P: _brick(34, 0.6)(P[0], P[1])}})
    gx, gz = OLD_LADLE
    con(e, 'primer_pla', gx, gz, 40, 50, 0, 66, IRONF,
        lambda a, y, P: 1.4 - math.cos(a - 2.3) * 0.8 + (0.8 if abs(y - 58) < 2 else 0), n=18)
    disc(e, 'primer_pla', gx, 66.2, gz, 52, IRONF, 2.2, ri=46)
    disc(e, 'primer_pla', gx, 64, gz, 46, SLAGF, 0.6)
    # (les cadenes de l'altre polispast es gronxen: són la capa `cadenes`)


CADENES = ((500, 380, 4), (516, 382, -3))          # les cadenes del polispast del primer pla: x, z i la corba


def cadenes(e, ph=0.0):
    """Les dues cadenes del primer pla, que pengen del sostre i es gronxen una mica (`ph`: de 0 a 1, el cicle)."""
    for k, (x, z, dx) in enumerate(CADENES):
        a = math.sin(2 * math.pi * (ph + k * 0.3)) * (3.0 + k)
        e.cable('cadenes', [(x, HW + 30, z), (x + dx + a * 0.5, 150, z + 2), (x + dx * 2 + a, 118, z + 4)], IRONF, 1.8,
                gruix=2.4)


def escena(cv, llum=None, taller=True):
    """Tota la sala, sense el gresol ni el carro (es mouen: decorats). `llum`: on és el gresol ple que il·lumina la
    nau ('llit', 'canal' o cap); `taller`: el llum de taller encès."""
    llums = [l for k, l in enumerate(LLUMS) if taller or k != 3] + ([_fos(GX[llum])] if llum else [])
    e = Escena(cv, CAM, llums, ambient=AMBIENT)
    nau(e, taller)
    llit(e)
    # les ombres a terra: la columna, els sacs
    e.foscor('ombra', (COL[0] - 14, 0.6, COL[1] + 70), (COL[0] + 50, 0.6, COL[1] + 70),
             (COL[0] + 50, 0.6, COL[1] - 30), (COL[0] - 14, 0.6, COL[1] - 30),
             lambda s, t: 0.45 * max(0.0, 1 - abs(s - 14 - (t - 30) * 0.3) / 14) * max(0.0, 1 - abs(t - 30) / 40))
    if llum:
        ombres_fos(e, GX[llum])
    canal(e)
    sorra(e)
    llum_taller(e)
    pont_grua(e)
    e.darrere = len(e.ids)                       # (el que es pinta d'aquí endavant pot tapar el gresol)
    banc(e)
    botonera(e)
    columna(e, 'columna', *COL)
    brossa(e)
    primer_pla(e)
    return e


def _ferralla(e, L):
    """La càrrega de la carretilla: bebedors i rebaves tallats d'altres colades, i un parell de lingots."""
    for k in range(6):
        u, w = -14 + (k % 3) * 12, -7 + (k // 3) * 12
        x, _, z = L(u, 0, w)
        e.roca('carreto', (x, 26, z), 7 + hr(k, 41) * 4, RUSTF if k % 2 else IRONF, 3.4, llum_dir=(-0.6, -0.6),
               aplana=0.7, seed=40 + k)
    x, _, z = L(4, 0, -4)
    e.caixa_girada('carreto', x, z, 30, 9, 7, CARRETO[2] + 0.3, IRONF, 4.2, y0=30,
                   cares={'dalt': {'ramp': IRONF, 'lvl': 5.6}})


def brossa(e):
    """El que omple el terra de la nau: la pila de lingots, les lingoteres, la carretilla de ferralla, les tenalles i
    un rastre d'escòria."""
    lingots(e, 'lingots', *LINGOTS, files=4, capes=4)
    cx, cz, a = CAIXES
    e.foscor('ombra_caixes', *[(x, 0.6, z) for x, z in _peu(cx, cz, a, 70, 52)],
             lambda s, t: 0.55 * min(1.0, min(s, t, 70 - s, 52 - t) / 10))
    for k in range(3):                                                                    # les caixes de motlle
        e.caixa_girada('caixes', cx + k * 2, cz - k, 56, 40, 14, a + k * 0.12, IRONF, 3.2, y0=k * 14,
                       cares={'dalt': {'ramp': IRONF, 'lvl': lambda s, t, P: 1.0 if 4 < s < 52 and 4 < t < 36 else 4.8},
                              'davant': {'ramp': RUSTF, 'lvl': lambda s, t, P: 3.0 + (1.2 if t < 1.5 else 0)
                                         + (fbm(s / 4, t / 2, 44) - 0.5) * 1.4},
                              'dreta': {'ramp': IRONF, 'lvl': 2.2}, 'esquerra': {'ramp': IRONF, 'lvl': 3.4}})
    for u in (-31, 31):                                                                   # les nanses de dalt
        x, _, z = _local((cx + 4, cz - 2), a + 0.24)(u, 0, 0)
        e.caixa_girada('caixes', x, z, 5, 12, 4, a + 0.24, IRONF, 4.4, y0=36)
    lingoteres(e, 'lingoteres', *LINGOTERES, n=3, ple=1)
    carretilla(e, 'carreto', *CARRETO, carrega=_ferralla)
    tenalles(e, 'tenalles', *TENALLES, llarg=100)
    for k, (x, z) in enumerate(((560, 500), (640, 520), (470, 640))):             # trossos d'escòria pel terra
        e.roca('tenalles', (x, 0, z), 4 + hr(k, 43) * 3, SLAGF, 2.8, llum_dir=(-0.6, -0.6), aplana=0.6, seed=50 + k)


def ombres_fos(e, bx=LADLE[0]):
    """Amb el gresol ple, les ombres llargues que fa la seva llum pel terra (lluny del gresol)."""
    bz = LADLE[1]
    for (x, z, w, ll) in ((*COL, 22, 260), (SORRA[0] - 20, SORRA[1], 120, 200), (PENDANT[0], PENDANT[1], 20, 120)):
        d = math.hypot(x - bx, z - bz)
        dx, dz = (x - bx) / d, (z - bz) / d
        px, pz = -dz * w / 2, dx * w / 2
        P0, P1 = (x - px, 0.7, z - pz), (x + px, 0.7, z + pz)
        e.foscor('ombra_fos', P0, P1, (P1[0] + dx * ll, 0.7, P1[2] + dz * ll), (P0[0] + dx * ll, 0.7, P0[2] + dz * ll),
                 lambda s, t, w=w, ll=ll: 0.75 * (1 - t / ll) * min(1.0, (w / 2 - abs(s - w / 2)) / (w * 0.2) + 0.1))


# ─── Composició ────────────────────────────────────────────────────────────

def _negre(img):
    cv = Canvas(img=img)
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)


@functools.lru_cache(maxsize=None)
def _escena(llum=None, taller=True):
    """La sala dibuixada tal qual: sense el metall fos, o amb la seva llum (sense tenyir) des d'on és el gresol."""
    cv = Canvas(light=LIGHT)
    e = escena(cv, llum, taller)
    _negre(cv.img)
    return cv.img, e


def _tenyeix(a, b):
    """La llum del metall fos tenyida de taronja: b (sense) + la diferència de llum amb a (amb), en taronja."""
    a = np.asarray(a).astype(np.float32)
    b = np.asarray(b).astype(np.float32)
    dl = np.clip((a[..., :3] - b[..., :3]).mean(axis=2, keepdims=True), 0, None)
    out = b[..., :3] + dl * np.array(TARONJA, np.float32) * 1.6
    return np.concatenate([np.clip(out, 0, 255), b[..., 3:]], axis=2).astype(np.uint8)


@functools.lru_cache(maxsize=None)
def _base(llum=None):
    """La sala (sense el gresol); amb el gresol ple a `llum`, la llum del metall fos tenyida de taronja."""
    img, e = _escena()
    if not llum:
        return img, e
    lit, _ = _escena(llum)
    return Image.fromarray(_tenyeix(lit, img), 'RGBA'), e


def bg(cv):
    img, _ = _base()
    cv.img.paste(img)
    cv.P = cv.img.load()


# ─── Decorats: el motlle i les claus, al món, damunt el llit ─────────────────

def _mold_frame(e):
    """La caixa del motlle: un marc de ferro amb nanses, girada com el llit."""
    cx, cz, L, A, h = MOLD
    ang = BED[4]
    Lo = _local((cx, cz), ang)
    for (u, w, l, a) in ((0, A / 2 - 2, L, 4), (0, -A / 2 + 2, L, 4), (-L / 2 + 2, 0, 4, A - 8), (L / 2 - 2, 0, 4, A - 8)):
        x, _, z = Lo(u, 0, w)
        e.caixa_girada('motlle', x, z, l, a, h, ang, IRONF, 3.0,
                       cares={'dalt': {'ramp': IRONF, 'lvl': 4.6}, 'davant': {'ramp': IRONF, 'lvl': 2.8},
                              'esquerra': {'ramp': IRONF, 'lvl': 2.0}, 'dreta': {'ramp': IRONF, 'lvl': 3.4}})
    for u in (-L / 2 - 3, L / 2 + 3):                                                    # les nanses
        x, _, z = Lo(u, 0, 0)
        e.caixa_girada('motlle', x, z, 4, 12, 4, ang, IRONF, 4.0, y0=h - 8)
    return Lo


def _claus(s, t):
    """Les tres claus, en coordenades de la cara de dalt del motlle (s al llarg, t a l'ample): → 0 (no), 1 (sí)."""
    cx, cz, L, A, h = MOLD
    for k in range(3):
        kx, ky = 22 + k * 24, 13
        d = math.hypot(s - kx, t - ky)
        if 2.4 <= d <= 5.2:                                                               # l'ull
            return True
        if kx + 4 <= s <= kx + 18 and abs(t - ky - (s - kx) * 0.45) < 1.6:              # la tija, en diagonal
            return True
        if kx + 12 <= s <= kx + 18 and 0 < (t - ky - (s - kx) * 0.45) < 6 and int(s) % 3 != 0:   # les dents
            return True
    return False


def _sorra_motlle(e, Lo, marques=True):
    cx, cz, L, A, h = MOLD

    def lv(s, t, P):
        v = 4.2 + (hr(int(s), int(t), 81) - 0.5) * 0.8 - t * 0.012
        if marques and _claus(s, t):
            v -= 2.6
        if marques and math.hypot(s - (L - 16), t - 12) < 4:                              # el bebedor
            v -= 3.0
        if marques and abs(t - 12 - (s - (L - 16)) * 0.0) < 1 and 40 < s < L - 20:       # el canal
            v -= 1.6
        return v
    e.quad('motlle', Lo(-L / 2 + 4, h - 3, A / 2 - 4), Lo(L / 2 - 4, h - 3, A / 2 - 4), Lo(L / 2 - 4, h - 3, -A / 2 + 4),
           Lo(-L / 2 + 4, h - 3, -A / 2 + 4), ramp=SAND, lvl=lv)


def _prop(draw):
    """Un decorat dibuixat al món damunt la sala (una Escena nova sobre una còpia del fons): → només el que canvia."""
    @functools.lru_cache(maxsize=None)
    def img():
        base, _ = _base()
        cv = Canvas(light=LIGHT, img=base.copy())
        e = Escena(cv, CAM, LLUMS, ambient=AMBIENT)
        draw(e)
        _negre(cv.img)
        return _diff(cv.img, base)

    def fn(cv):
        cv.img.alpha_composite(img())
    return fn


def _motlle_buit(e):
    Lo = _mold_frame(e)
    cx, cz, L, A, h = MOLD
    e.quad('motlle', Lo(-L / 2 + 4, 1, A / 2 - 4), Lo(L / 2 - 4, 1, A / 2 - 4), Lo(L / 2 - 4, 1, -A / 2 + 4),
           Lo(-L / 2 + 4, 1, -A / 2 + 4), ramp=COAL, lvl=1.2)


def _motlle_ple(e):
    Lo = _mold_frame(e)
    _sorra_motlle(e, Lo)


def _claus_roents(e):
    cx, cz, L, A, h = MOLD
    Lo = _local((cx, cz), BED[4])
    e.quad('claus', Lo(-L / 2 + 4, h - 2.6, A / 2 - 4), Lo(L / 2 - 4, h - 2.6, A / 2 - 4),
           Lo(L / 2 - 4, h - 2.6, -A / 2 + 4), Lo(-L / 2 + 4, h - 2.6, -A / 2 + 4), ramp=MOLTEN,
           lvl=lambda s, t, P: 4.0 + (0.9 if (int(s) + int(t)) % 3 == 0 else 0), forma=_claus)


@functools.lru_cache(maxsize=None)
def _motlle_ences(llum):
    """El motlle preparat il·luminat pel metall fos del gresol (a `llum`): dibuixat damunt la sala sense i amb aquesta
    llum, i la diferència tenyida de taronja, com la resta de la nau. → (imatge RGBA de la sala, màscara del motlle)."""
    b = Canvas(light=LIGHT, img=_escena()[0].copy())
    _motlle_ple(Escena(b, CAM, LLUMS, ambient=AMBIENT))
    a = Canvas(light=LIGHT, img=_escena(llum)[0].copy())
    _motlle_ple(Escena(a, CAM, LLUMS + [_fos(GX[llum])], ambient=AMBIENT))
    m = np.any(np.asarray(b.img) != np.asarray(_escena()[0]), axis=2)
    return _tenyeix(a.img, b.img), m


def _llum_fos(llum):
    """La nau il·luminada pel gresol ple (a `llum`), i també el motlle preparat que l'espera al llit (aquest decorat va
    per sobre de `motlle_preparat` i el pinta encès)."""
    def fn(cv):
        full, _ = _base(llum)
        base, _ = _base()
        out = np.asarray(full).copy()
        lit, m = _motlle_ences(llum)
        out[m] = lit[m]
        cv.img.alpha_composite(_diff(Image.fromarray(out, 'RGBA'), base))
    return fn


# ─── El gresol: decorats (on és) i la capa `gresol_mou` (quan es mou) ───────
# Cada fotograma té el carro, el cable i el gresol sols, retallats on els tapa el que hi ha davant (la columna, el
# llum, les coses de terra del davant, el primer pla). Les capes del davant que són més a prop (la columna, els
# lingots...) van per sobre seu (zIndex), i el gresol, al seu torn, per sobre de les del fons (el banc, les caixes).

OCLU = {'botonera', 'columna', 'lingots', 'lingoteres', 'carreto', 'tenalles', 'primer_pla', 'llum'}
POSICIONS = [('llit', 'dalt'), ('llit', 'baix'), ('canal', 'dalt'), ('canal', 'baix')]


@functools.lru_cache(maxsize=None)
def _tapa():
    _, e = _base()
    amo = np.frombuffer(e.amo, np.uint16).reshape(H, W)
    return np.isin(amo, [i for i, sid in enumerate(e.ids) if sid in OCLU])


def _gresol_img(x, gy, ple=False, ph=0.0, bolca=0.0, gronxa=0.0, buidant=False, raig=0.0, rph=0.0):
    """El carro i el gresol a (`x`, `gy`), i el raig de metall fos (`raig`: el gruix, 0..1) si es bolca."""
    def pinta(llums):
        cv = Canvas(light=LIGHT, transparent=True)
        e = Escena(cv, CAM, llums, ambient=AMBIENT)
        carro(e, x, gy)
        gresol(e, x, gy, ple, ph, bolca, gronxa, buidant)
        return cv.img
    img = pinta(LLUMS)
    if ple or raig:
        img = Image.fromarray(_tenyeix(pinta(LLUMS + [Llum((x, gy + GH + 20, LADLE[1]), 90, 1.4, power=1.2)]), img),
                              'RGBA').copy()
    if raig:
        _raig(img, broc(x, gy, bolca, gronxa), raig, rph)
    a = np.asarray(img).copy()
    a[_tapa()] = 0
    return Image.fromarray(a, 'RGBA').copy()


def _raig(img, B, gruix, ph):
    """El raig de metall fos que cau del broc `B` al motlle, i les guspires on toca."""
    cv = Canvas(img=img)
    e = Escena(cv, CAM, [], 0)
    fons = (B[0] + 4, MOLD[4] + 0.5, B[2] - 4)
    punts = [(B[0] + 3 * t + 2 * t * t, B[1] + (fons[1] - B[1]) * t, B[2] - 4 * t) for t in (0, 0.25, 0.5, 0.75, 1.0)]
    e.cable('raig', punts, MOLTEN, 3.8, gruix=2.4 + 5.0 * gruix)
    e.cable('raig', punts, MOLTEN, 4.8, gruix=1.0 + 2.4 * gruix)
    for j in range(7):                                    # les guspires que salten on cau
        t = (ph + j / 7) % 1
        a = j * 2.4
        P = (fons[0] + math.cos(a) * (6 + 22 * t), fons[1] + 26 * t - 34 * t * t, fons[2] + math.sin(a) * 10 * t)
        if P[1] > 0 and gruix > 0.2:
            u, v, _ = CAM.projecta(P)
            if 0 <= u < W and 0 <= v < BOTTOM:
                cv.flat(u, v, MOLTEN[5] if t < 0.4 else MOLTEN[3])


def _vapor(img, x, y1, ph, col=(150, 110, 90), alt=54, ample=16):
    """El vapor que puja de la boca del gresol (a `x`, la vora a `y1`), a quadres, i les guspires."""
    cv = Canvas(img=img)
    cz = LADLE[1]
    u0, v0, _ = CAM.projecta((x, y1, cz))
    k = CAM.escala((x, y1, cz))
    for Y in range(max(0, int(v0 - alt * k)), int(v0 - 2)):
        t = (v0 - 2 - Y) / (alt * k)
        for X in range(int(u0 - 30 * k), int(u0 + 30 * k)):
            uu = (X - u0 - math.sin(t * 3 + ph * 6.28) * 5 * k) / ((ample + t * 12) * k)
            if abs(uu) > 1 or not (0 <= X < W):
                continue
            dd = (1 - t) * (1 - uu * uu) * (0.3 + fbm(X / 6, (Y + ph * alt * k) / 6, 92))
            if dd > 0.55 + B4[Y & 3][X & 3] * 0.6:
                cv.flat(X, Y, col)
    for j in range(5):                                                                # guspires
        s = (ph + j / 5) % 1
        Pw = (x - 18 + j * 9 + math.sin(s * 9 + j) * 5, y1 + 4 + s * 50, cz + math.cos(j * 2.1) * 10)
        if s < 0.7:
            uu, vv, _ = CAM.projecta(Pw)
            if 0 <= uu < W and 0 <= vv < BOTTOM:
                cv.flat(uu, vv, MOLTEN[5] if s < 0.3 else MOLTEN[3])


def _quiet(x, y):
    def fn(cv):
        cv.img.alpha_composite(_gresol_img(GX[x], GY[y]))
    return fn


def _frames_ple(x, y):
    """El gresol ple, quiet a (`x`, `y`): el metall bull, el vapor puja i salten guspires (en bucle)."""
    n = 12
    out = []
    for f in range(n):
        img = _gresol_img(GX[x], GY[y], True, ph=f / n)
        _vapor(img, GX[x], GY[y] + GH, f / n)
        a = np.asarray(img).copy()
        a[_tapa()] = 0
        out.append(Image.fromarray(a, 'RGBA').copy())
    return out


def _ease(t):
    return t * t * (3 - 2 * t)


GRONXA = (1.0, -0.7, 0.45, -0.25, 0.1, 0.0)       # com es gronxa en aturar-se (× l'amplada)


def _frames_mou(de, a, ple):
    """El gresol que va de la posició `de` a la posició `a` (('llit', 'dalt'), ...): el carro llisca per la biga (o
    el cable s'enrotlla), el gresol es queda una mica enrere i, en aturar-se, es gronxa."""
    (x0, y0), (x1, y1) = (GX[de[0]], GY[de[1]]), (GX[a[0]], GY[a[1]])
    n = 14 if x0 != x1 else 10
    sgn = 1 if x1 > x0 else -1
    out = []
    for f in range(1, n + 1):
        t = _ease(f / n)
        g = -sgn * 0.08 * math.sin(math.pi * f / n) if x0 != x1 else 0.0
        out.append(_gresol_img(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, ple, ph=(f / 12) % 1, gronxa=g))
    for k, gg in enumerate(GRONXA):
        if x0 != x1:
            out.append(_gresol_img(x1, y1, ple, ph=((n + k) / 12) % 1, gronxa=sgn * 0.05 * gg))
        else:
            out.append(_gresol_img(x1, y1 + (1.6 if y1 < y0 else -1.6) * gg, ple, ph=((n + k) / 12) % 1))
    return out


def _frames_bolca():
    """Damunt el motlle, avall: el gresol es bolca pels munyons, el metall raja pel broc fins al motlle, i torna a
    redreçar-se, buit."""
    x, gy = GX['llit'], GY['baix']
    out = []
    for f in range(1, 9):                                 # es bolca
        b = _ease(f / 8) * 1.15
        out.append(_gresol_img(x, gy, True, ph=f / 12, bolca=b, raig=max(0.0, (b - 0.75) / 0.4), rph=f / 7))
    for f in range(12):                                   # raja
        out.append(_gresol_img(x, gy, True, ph=f / 12, bolca=1.15 + 0.1 * f / 11, buidant=f > 6,
                               raig=1.0 - 0.5 * max(0, f - 8) / 3, rph=f / 7))
    for f in range(1, 9):                                 # es redreça, buit
        b = (1 - _ease(f / 8)) * 1.25
        out.append(_gresol_img(x, gy, False, bolca=b, raig=max(0.0, 0.4 - f * 0.15), rph=f / 7))
    out.append(_gresol_img(x, gy))
    return out


PROPS = {'motlle_posat': _prop(_motlle_buit), 'motlle_preparat': _prop(_motlle_ple),
         'gresol_ple': _llum_fos('llit'), 'gresol_ple_canal': _llum_fos('canal'), 'claus_fetes': _prop(_claus_roents),
         **{f'gresol_{x}_{y}': _quiet(x, y) for x, y in POSICIONS}}


# ─── L'ambient: la pols dels feixos, el fum del pas, les cadenes i el llum de taller ───

FONS = {'', 'sostre', 'paret_fons', 'paret_dreta', 'terra', 'pas', 'pas_terra', 'racons', 'cantonada', 'dalt',
        'dalt_dreta', 'llit'}


@functools.lru_cache(maxsize=None)
def _fons():
    """On es veu el fons de la nau (les parets, el terra, el sostre): la pols i el fum només s'hi veuen allà."""
    _, e = _base()
    amo = np.frombuffer(e.amo, np.uint16).reshape(H, W)
    return np.isin(amo, [i for i, sid in enumerate(e.ids) if sid in FONS])


def _feixos():
    """Els feixos de llum dels finestrals, com a quadrilàters del món (els de `nau`)."""
    out = []
    for wx in WINDOWS:
        a0, a1 = wx * KW, (wx + 28) * KW
        out.append(((a0, 262, ZB - 2), (a1, 262, ZB - 2), (a1 - 70, 0, ZB - 330), (a0 - 70, 0, ZB - 330)))
    z0, z1 = WIN_DRETA
    out.append(((XW - 2, 262, z1), (XW - 2, 262, z0), (XW - 300, 0, z0 - 60), (XW - 300, 0, z1 - 60)))
    return out


def _frames_pols(n=32):
    """La pols que sura dins els feixos de llum: punts que es mouen a poc a poc i parpellegen."""
    fons = _fons()
    out = []
    for f in range(n):
        cv = Canvas(transparent=True)
        ph = f / n
        for q, (P0, P1, P2, P3) in enumerate(_feixos()):
            for k in range(34):
                s0, t0 = hr(k, q, 71), hr(k, q, 72)
                s = (s0 + 0.05 * math.sin(2 * math.pi * (ph + hr(k, q, 73)))) % 1
                t = (t0 + ph * (0.3 + hr(k, q, 74) * 0.3)) % 1
                A = [P0[i] + (P1[i] - P0[i]) * s for i in range(3)]
                B = [P3[i] + (P2[i] - P3[i]) * s for i in range(3)]
                P = [A[i] + (B[i] - A[i]) * t for i in range(3)]
                u, v, _ = CAM.projecta(P)
                u, v = int(u), int(v)
                llum = math.sin(math.pi * t) * (0.5 + 0.5 * math.sin(2 * math.pi * (ph * 2 + hr(k, q, 75))))
                if 0 <= u < W and 0 <= v < BOTTOM and fons[v, u] and llum > 0.45:
                    cv.flat(u, v, (214, 186, 146) if llum > 0.75 else (168, 140, 110))
        out.append(cv.img)
    return out


def _frames_fum_pas(n=24):
    """Un fum càlid i fluix que surt per dalt del pas (ve del forn) i s'esfilagarsa cap amunt."""
    fons = _fons()
    x0, x1, ph_ = PAS
    out = []
    for f in range(n):
        cv = Canvas(transparent=True)
        ph = f / n
        u0, v0, _ = CAM.projecta(((x0 + x1) / 2, ph_ - 6, ZB))
        k = CAM.escala(((x0 + x1) / 2, ph_ - 6, ZB))
        alt = 120 * k
        for Y in range(max(0, int(v0 - alt)), int(v0 + 20 * k)):
            t = (v0 + 20 * k - Y) / (alt + 20 * k)
            for X in range(int(u0 - 70 * k), int(u0 + 70 * k)):
                if not (0 <= X < W) or not fons[Y, X]:
                    continue
                uu = (X - u0 - math.sin(t * 4 + ph * 6.28) * 8 * k) / ((34 + t * 30) * k)
                if abs(uu) > 1:
                    continue
                dd = (1 - t) * (1 - uu * uu) * (0.25 + fbm(X / 9, (Y + ph * alt) / 9, 93))
                if dd > 0.5 + B4[Y & 3][X & 3] * 0.55:
                    cv.flat(X, Y, (104, 80, 66) if dd < 0.62 else (126, 96, 76))
        out.append(cv.img)
    return out


def _frames_cadenes(n=24):
    out = []
    for f in range(n):
        cv = Canvas(light=LIGHT, transparent=True)
        cadenes(Escena(cv, CAM, LLUMS, ambient=AMBIENT), f / n)
        out.append(cv.img)
    return out


# El llum de taller: quasi sempre encès; de tant en tant, un parpelleig (s'apaga un moment i torna).
PARPELLEIG = [0] * 34 + [1, 0, 1, 1, 0] + [0] * 41 + [1, 0]


def _frames_llum():
    off, _ = _escena(None, False)
    base, _ = _base()
    fosc = _diff(off, base)
    buit = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    return [fosc if k else buit for k in PARPELLEIG]


def _frames_vapor_motlle():
    """La sorra fina cau damunt el motlle roent (l'Iri la hi tira) i en surt una gran bafarada de vapor."""
    cx, cz, L, A, h = MOLD
    n = 30
    out = []
    for f in range(n):
        cv = Canvas(transparent=True)
        if f < 10:                                        # la sorra que cau
            for k in range(40):
                t = ((f + hr(k, 1, 21) * 4) / 6) % 1
                P = (cx - 30 + hr(k, 2, 21) * 60, 70 - 54 * t, cz - 10 + hr(k, 3, 21) * 20)
                u, v, _ = CAM.projecta(P)
                if 0 <= u < W and 0 <= v < BOTTOM:
                    cv.flat(u, v, (226, 206, 160) if k % 3 else (190, 168, 124))
        img = cv.img
        if f >= 4:
            fo = min(1.0, (f - 4) / 8) * (1 - max(0.0, (f - 20) / 10))
            if fo > 0.05:
                for k in range(3):
                    _vapor(img, cx - 30 + k * 30, h + 2, (f / 10 + k * 0.33) % 1, col=(196, 190, 184),
                           alt=60 + 80 * fo, ample=10 + 16 * fo)
        out.append(img)
    return out


ANIMS = {
    'colada_accio': {'frames': lambda: [Image.new('RGBA', (W, H), (0, 0, 0, 0))], 'frameDuration': 1000, 'loop': False,
                     'zIndex': 6},
    'vapor_motlle': {'frames': _frames_vapor_motlle, 'frameDuration': 90, 'loop': False, 'prop': 'colada_accio'},
    'pols': {'frames': _frames_pols, 'frameDuration': 150},
    'fum_pas': {'frames': _frames_fum_pas, 'frameDuration': 140},
    'llum_taller': {'frames': _frames_llum, 'frameDuration': 110},
    'cadenes': {'frames': _frames_cadenes, 'frameDuration': 150, 'zIndex': 60},
    # el gresol ple, quiet (decorats que bullen)
    **{f'gresol_{x}_{y}_ple': {'frames': (lambda x=x, y=y: _frames_ple(x, y)), 'frameDuration': 110}
       for x, y in POSICIONS},
    # la capa que es mou (les indicacions d'escena del diàleg `grua`): buida quan no es mou
    'gresol_mou': {'frames': lambda: [Image.new('RGBA', (W, H), (0, 0, 0, 0))], 'frameDuration': 1000, 'loop': False},
    **{f'{nom}{p}': {'frames': (lambda de=de, a=a, ple=bool(p): _frames_mou(de, a, ple)), 'frameDuration': 80,
                     'loop': False, 'prop': 'gresol_mou'}
       for nom, de, a in (('mou_llit_canal', ('llit', 'dalt'), ('canal', 'dalt')),
                          ('mou_canal_llit', ('canal', 'dalt'), ('llit', 'dalt')),
                          ('baixa_llit', ('llit', 'dalt'), ('llit', 'baix')),
                          ('puja_llit', ('llit', 'baix'), ('llit', 'dalt')),
                          ('baixa_canal', ('canal', 'dalt'), ('canal', 'baix')),
                          ('puja_canal', ('canal', 'baix'), ('canal', 'dalt')))
       for p in ('', '_ple')},
    'bolca': {'frames': _frames_bolca, 'frameDuration': 90, 'loop': False, 'prop': 'gresol_mou'},
}


def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


# ─── Geometria (coordenades de sala, projectades) ────────────────────────────

def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


def _escala_a(v):
    lo, hi = 1.0, 4000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.projecta((760, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((760, 0, (lo + hi) / 2))


def _cercle(cx, cz, r, n=10):
    return [_p(cx + r * math.cos(2 * math.pi * i / n), cz + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def _llit_peu(m=10):
    cx, cz, L, A, ang = BED
    Lo = _local((cx, cz), ang)
    return [(Lo(u, 0, w)[0], Lo(u, 0, w)[2]) for u, w in ((-L / 2 - m, -A / 2 - m), (L / 2 + m, -A / 2 - m),
                                                         (L / 2 + m, A / 2 + m), (-L / 2 - m, A / 2 + m))]


def _banc_peu(m=0):
    cx, cz, a, L, A = BANC
    Lo = _local((cx, cz), a)
    return [(Lo(u, 0, w)[0], Lo(u, 0, w)[2]) for u, w in ((-L / 2 - m, -A / 2 - m), (L / 2 + m, -A / 2 - m),
                                                         (L / 2 + m, A / 2 + m), (-L / 2 - m, A / 2 + m))]


def _vfront(*xz):
    return round(max(_p(x, z)[1] for x, z in xz))


# El terra on es camina (al món): del pas del forn fins a la sorra, pel davant i pel darrere del llit; no arriba al
# primer pla (el pilar i el gresol vell). Forats: el llit, la columna i la pila de grava.
WALK_MON = [(PAS[0] + 6, ZB + 40), (PAS[1] - 6, ZB + 40), (PAS[1] - 6, ZB - 10), (XW - 40, ZB - 10),
            (XW - 40, 520), (880, 458), (700, 446), (500, 456), (340, 506), (296, 640), (PAS[0] - 20, ZB - 10),
            (PAS[0] + 6, ZB - 10)]
_WALK = [_p(x, z) for x, z in WALK_MON]
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)
_LP = _llit_peu(0)

def _base_girada(cx, cz, ang, L, A):
    """La línia base d'una cosa girada: la del cantó de davant que queda més al fons (el segon més avall)."""
    return round(sorted(_p(x, z)[1] for x, z in _peu(cx, cz, ang, L, A))[-2])


_FOS = ('gresol_ple', 'gresol_ple_canal')        # (amb el gresol ple, cada capa té la seva versió il·luminada)
_GRESOL = [f'gresol_{x}_{y}{p}' for x, y in POSICIONS for p in ('', '_ple')] + ['gresol_mou']


def _canal_peu(t):
    (ax, _, az), (bx, _, bz) = CANAL
    return ax + (bx - ax) * t, az + (bz - az) * t

FRONT = [
    {'id': 'davant_lingots', 'mask': _amo({'lingots'}), 'baseline': _base_girada(*LINGOTS, 58, 42), 'zIndex': 20, 'variants': _FOS},
    {'id': 'davant_lingoteres', 'mask': _amo({'lingoteres'}), 'baseline': _base_girada(*LINGOTERES, 114, 18),
     'zIndex': 20, 'variants': _FOS},
    {'id': 'davant_caixes', 'mask': _amo({'caixes'}), 'baseline': _base_girada(*CAIXES, 56, 40), 'zIndex': 20, 'variants': _FOS},
    {'id': 'davant_carreto', 'mask': _amo({'carreto'}), 'baseline': _base_girada(*CARRETO, 60, 32), 'zIndex': 20, 'variants': _FOS},
    # El gresol (els decorats de cada posició i la capa que es mou) va just per sobre d'aquesta capa, que és buida:
    # només hi és per la línia base (qui passa per davant del gresol el tapa; qui hi passa per darrere, no).
    {'id': 'davant_gresol', 'mask': lambda x, y: False, 'props': _GRESOL,
     'baseline': _vfront((LADLE[0], LADLE[1] - LADLE[5])), 'zIndex': 20},
    {'id': 'davant_canal', 'mask': _amo({'canal'}), 'baseline': _vfront(_canal_peu(0.72)), 'zIndex': 20,
     'variants': _FOS},
    {'id': 'davant_botonera', 'mask': _amo({'botonera'}), 'baseline': _vfront((PENDANT[0], PENDANT[1] - 5)),
     'zIndex': 20, 'variants': _FOS},
    {'id': 'davant_banc', 'mask': _amo({'banc'}), 'baseline': _vfront(*_banc_peu()), 'zIndex': 20, 'variants': _FOS},
    {'id': 'davant_columna', 'mask': _amo({'columna'}), 'baseline': _vfront((COL[0], COL[1] - 13)), 'zIndex': 20, 'variants': _FOS},
    {'id': 'davant_sorra', 'mask': _amo({'sorra'}),
     'baseline': _vfront((SORRA[0] - 60, SORRA[1] - 40), (SORRA[0] - 110, SORRA[1] - 40)), 'zIndex': 20, 'variants': _FOS},
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20, 'variants': _FOS},
]

GEOMETRIA = {
    'things': {
        'pas': {'rect': _rect_mon((PAS[0], PAS[2], ZB), (PAS[1], 0, ZB)), 'walk': _p((PAS[0] + PAS[1]) / 2, ZB + 20)},
        'gresol': {'rect': _rect_mon((GX['llit'] - LADLE[5] - 26, GY['dalt'] + GH + 30, LADLE[1] - LADLE[5]),
                                     (GX['llit'] + LADLE[5] + 16, GY['baix'], LADLE[1] - LADLE[5])),
                   'walk': _p(LADLE[0] - 40, BED[1] - BED[3] / 2 - 46)},
        'gresol_c': {'rect': _rect_mon((GX['canal'] - LADLE[5] - 26, GY['dalt'] + GH + 30, LADLE[1] - LADLE[5]),
                                       (GX['canal'] + LADLE[5] + 16, GY['baix'], LADLE[1] - LADLE[5])),
                     'walk': _p(GX['canal'] + 10, LADLE[1] - 90)},
        'canal': {'rect': _rect_mon((CANAL[0][0], CANAL[0][1] + 12, CANAL[0][2]), (CANAL[1][0] + 6, CANAL[1][1] - 6, CANAL[1][2])),
                  'walk': _p(*_canal_peu(0.5)[:1], _canal_peu(0.5)[1] - 70)},
        'grua_pont': {'rect': _rect_mon((PENDANT[0] - 12, PENDANT[2] + 60, PENDANT[1] - 5),
                                        (PENDANT[0] + 12, PENDANT[2] - 2, PENDANT[1] - 5)),
                      'walk': _p(PENDANT[0] - 6, PENDANT[1] - 92)},
        'llit': {'rect': _rect_mon(*[(x, 0, z) for x, z in _LP], *[(x, 16, z) for x, z in _LP]),
                 'walk': _p(BED[0] - 30, BED[1] - BED[3] / 2 - 40)},
        'sorra_pedra': {'rect': _rect_mon((SORRA[0] - 140, 110, SORRA[1] - 50), (XW, 0, SORRA[1] - 50)),
                        'walk': _p(SORRA[0] - 120, SORRA[1] - 110)},
    },
    'spawns': {'iri': _p(600, 505), 'vet': _p(480, 610)},
    'walkable': _WALK,
    'forats': [[_p(x, z) for x, z in _llit_peu(12)], _cercle(*COL, 22, 8), [_p(x, z) for x, z in _banc_peu(10)],
               [_p(x, z) for x, z in ((860, 630), (1000, 600), (1050, 650), (1050, 790), (880, 720))],
               [_p(x, z) for x, z in _peu(*LINGOTS, 58, 42, 8)], [_p(x, z) for x, z in _peu(*LINGOTERES, 114, 18, 6)],
               [_p(x, z) for x, z in _peu(*CARRETO, 60, 34, 8)], [_p(x, z) for x, z in _peu(*CAIXES, 56, 40, 8)],
               *[_cercle(*_canal_peu(t), 22, 6) for t in (0.3, 0.72)]],
    'floorSquash': 0.4,
    # L'ombra de contacte: la llum dominant és el llum de taller penjat sobre el llit.
    'characterShadow': {'enabled': True, 'color': '#120a08', 'alpha': 0.42, 'squash': 0.4, 'core': 0.6,
                        'light': {'x': _p(LAMP[0], LAMP[2])[0], 'y': _p(LAMP[0], LAMP[2])[1],
                                  'stretch': 0.8, 'reach': 140}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    # La llum de la sala sobre els personatges (characterLights del motor): la fosa, fosca i de sutge: els finestrals,
    # el llum de taller, la claror del forn i el metall fos.
    'characterLights': {
        'ambient': '#645a54',
        'lights': [
            *[llum_personatges(CAM, l.pos, l.r, '#c8d0dc', 0.3) for l in LLUMS[:3]],  # els finestrals
            llum_personatges(CAM, LLUMS[3].pos, LLUMS[3].r, '#ffd8a0', 0.55),  # el llum de taller
            llum_personatges(CAM, LLUMS[4].pos, LLUMS[4].r, '#ff9a50', 0.3),  # el forn, pel pas
            llum_personatges(CAM, FOS.pos, FOS.r, '#ff7a28', 0.7, whenPropVisible='gresol_ple'),  # el metall fos, amb el gresol ple
            llum_personatges(CAM, _fos(GX['canal']).pos, FOS.r, '#ff7a28', 0.7, whenPropVisible='gresol_ple_canal'),
        ],
    },
}
