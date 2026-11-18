"""
Aigua Verne — `fosa_forn` (L: persones de ≈83 px): la fosa de Ferrum per dins, la banda del forn. EN 3D
(hd640/tres_d.py), a 1×.

La nau, vista de biaix i des de dalt, mirant la cantonada de l'esquerra: la paret del carrer fuig cap al fons amb la
**porta** oberta en escorç (la claror grisa de fora entra en diagonal pel terra i la fulla de fusta es veu oberta cap
a dins); la paret del fons, de maó negre amb els finestrals bruts (feixos de llum de fum en diagonal), i a la dreta el
**pas** cap a la colada, una obertura alta i fosca al fons. Al mig, el **forn**: un volum de maó amb la boca, la
campana de ferro (un tronc de piràmide) i la xemeneia que travessa el sostre. Al costat, la **manxa**, girada: el fol
de cuir en falca sobre el cavallet, el broc a la tovera del forn i la palanca amb la cadena. Les columnes de ferro
colat aguanten les bigues del carril de la grua, que fugen cap al fons: a la de l'esquerra hi ha el **termòmetre**
(el capil·lar va pel terra fins al forn); a la de la dreta, recolzat, el **rascle**. Al costat de la porta, la pila de
**comptadors** (el **metall**) i una carretilla girada. En primer pla, fosc i tallat per la vora, un pilar de maó, la
cadena d'un polispast que penja i un munt de carbó.

La llum: sense foc, la nau és fosca, amb la claror freda de la porta i dels finestrals (les cares que miren la porta,
més clares; els racons i el sostre, negres). Amb el forn encès (`forn_ences`, `forn_fort`) la llum del foc ve de la
boca i pinta de taronja cada cara segons com la mira (la mateixa escena, il·luminada amb el foc, i la diferència de
llum tenyida de taronja), amb les ombres llargues cap a la càmera.

El detall ve de la fosa plana de sempre (fosa_forn_pla_comu.py): la paret amb els finestrals i el pas, la façana del
forn amb la boca, el termòmetre, la porta i la pila de comptadors es dibuixen de cara i es projecten. Les flames
(`foc`, `foc_fort`) es dibuixen planes i es projecten per la façana del forn; les guspires (`guspires`) salten de la
boca en el món.

El món: x a la dreta (0 = la paret de la porta), y amunt (0 = el terra), z cap al fons (860 = la paret del fons);
1 unitat = 1 píxel de sala a la distància on un personatge fa la seva mida de lluny (83 px).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
import numpy as np
from PIL import Image

from hd.pix import Canvas, Light, W, H, hr
from hd.rooms.comu import _diff
from hd.rooms.exterior import fbm
from hd640.rooms import fosa_forn_pla_comu as PL
from hd640.rooms.ferrum_comu import (RH, SMOG, SLAGF, SOOT, MORTAR, COB, COAL, IRONF, RUSTF, PLANKF, FIREF,
                                     brick_lvl, nave_wall, crane_rail, pila_comptadors)
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = RH - 1                                    # la sala acaba aquí (a sota, la barra de verbs)
ZB = 860                                           # la paret del fons
KW = 1.8                                           # unitats del món per píxel del dibuix pla de la paret del fons
HW = (198 - 31) * KW                               # l'alçada de les parets (fins a les encavallades)
XR = 640 * KW                                      # on s'acaba la paret del fons (a la dreta, fora de pantalla)
PAS = (372 * KW, 450 * KW, (198 - 64) * KW)        # el pas a la colada, a la paret del fons: x0, x1, alçada
DOOR = (600.0, 600 + 61 * 1.6, 96 * 1.6)           # la porta del carrer, a la paret de l'esquerra: z0, z1, alçada
FORN = (258.0, 502.0, 150.0, 154.0)                # el forn: x0, x1, fondària, alçada del cos
FCX = (FORN[0] + FORN[1]) / 2
FZ0 = ZB - FORN[2]                                 # la façana del forn
HOOD = 290.0                                       # dalt de la campana
COL1, COL2 = (196.0, 600.0), (742.0, 540.0)        # les columnes de ferro colat (x, z)
MANXA = (536.0, 772.0, -0.62, 112.0, 40.0)         # el fol: la frontissa (x, z), l'angle, la llargada, l'amplada
METALL = (118.0, 520.0)                            # la pila de comptadors (x, z)
CARRET = (214.0, 494.0, 0.55)                      # la carretilla (x, z, angle)
DIAL_Y = 128.0                                     # l'altura del termòmetre a la columna

CAM = Camera(pos=(520, 185, 60), yaw=-0.16, pitch=0.11, f=430, centre=(330, 108))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)      # (la llum és la del món: la de l'Escena)
PLA = Light(ambient=0.2, vignette=None, floor_fade=None)        # la llum neutra de les textures planes
AMBIENT = -1.2
WINDOWS = (40, 300, 520)                           # els finestrals (x del dibuix pla de la paret del fons)
LLUMS = [Llum(((wx + 14) * KW, 220, ZB - 70), 420, 1.0, power=1.4) for wx in WINDOWS] + [
    Llum((20, 80, (DOOR[0] + DOOR[1]) / 2), 560, 2.8, power=1.3),          # la claror del carrer, per la porta
]
FOC = {1: Llum((FCX, 46, FZ0 - 24), 760, 3.0, power=1.2), 2: Llum((FCX, 50, FZ0 - 24), 900, 4.0, power=1.1)}
PPELL = PL.LEATHER                                 # el cuir de la manxa
TARONJA = {1: (1.6, 0.62, 0.2), 2: (1.5, 0.95, 0.42)}          # com tenyeix la llum del foc (r, g, b)


# ─── Les textures: la fosa plana ─────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _paret():
    """La paret del fons, de cara: maó negre, pilastres, els finestrals, el carril de la grua i el pas."""
    cv = Canvas(light=PLA)
    nave_wall(cv, 0, W - 1, top=31, seed=5, windows=tuple((wx, 28) for wx in WINDOWS), pilasters=(132, 252, 600))
    crane_rail(cv, 86)
    tmp = Canvas(light=PLA)
    PL.pas(tmp)                                                    # (el pas pla és a x 562..640: es trasllada)
    cv.img.paste(tmp.img.crop((562, 58, 640, 199)), (int(PAS[0] / KW) - 6, 58))
    return cv.img


@functools.lru_cache(maxsize=None)
def _porta():
    cv = Canvas(light=PLA)
    PL.porta(cv, fulla=False)
    return cv.img


@functools.lru_cache(maxsize=None)
def _forn(fire):
    cv = Canvas(light=PL.LIGHTS[fire] if fire else PLA)
    PL.forn(cv, fire)
    return cv.img


@functools.lru_cache(maxsize=None)
def _dial(fire):
    cv = Canvas(light=PLA, transparent=True)
    PL.termometre(cv, fire)
    cx, cy, r = PL.DIAL
    return cv.img.crop((cx - r - 4, cy - r - 4, cx + r + 5, cy + r + 11)), (r + 4, r + 4)


@functools.lru_cache(maxsize=None)
def _pila():
    cv = Canvas(light=PLA, transparent=True)
    pila_comptadors(cv, 70, 156, 236, 38, seed=11)
    return cv.img.crop((62, 192, 164, 242)), (113 - 62, 236 - 192)


# ─── Peces ──────────────────────────────────────────────────────────────────

def _brick(seed, base=2.4, soot=None):
    """Maó en coordenades del món (`a` al llarg de la paret, `y` amunt), del mateix gra que la paret plana."""
    def L(a, y):
        return brick_lvl(int(a / KW), int((HW - y) / KW), 0, 0, bw=12, bh=4, base=base, seed=seed,
                         soot=soot)
    return L


def _terra(s, t, P):
    """Sorra negra trepitjada: grans, taques d'oli i escòria, en coordenades del món (més menuda cap al fons)."""
    x, z = P[0], P[2]
    v = 2.6 + (fbm(x / 90, z / 60, 9) - 0.5) * 1.4 + (hr(int(x) // 3, int(z) // 3, 9) - 0.5) * 0.7
    cx, cz = int(x // 26), int(z // 26)
    if hr(cx, cz, 31) > 0.82:                                      # trossos d'escòria
        ox, oz = hr(cx, cz, 32) * 26, hr(cx, cz, 33) * 26
        d = math.hypot(x - cx * 26 - ox, (z - cz * 26 - oz) * 1.3)
        r = 2 + hr(cx, cz, 34) * 3
        if d < r:
            v += 1.4 - d / r * 1.2
        elif d < r + 1.6:
            v -= 0.9
    if fbm(x / 60, z / 45, 21) > 0.66:                             # taques d'oli
        v -= 0.9
    worn = max(0.0, 1 - abs(z - 560) / 160) * max(0.0, 1 - abs(x - 420) / 360)
    return v + worn * 0.6


def _planxes(s, t, P):
    """Les planxes de ferro davant la boca del forn (on es treballa amb el rascle)."""
    x, z = P[0], P[2]
    v = 2.8 + (fbm(x / 20, z / 14, 2) - 0.5) * 1.4 + (0.6 if (int(x) + int(z) * 2) % 17 == 0 else 0)
    if s % 62 < 1.6 or t % 46 < 1.6:
        v -= 1.8
    return v


def cilindre(e, sid, cx, cz, r, y0, y1, ramp, lvl, n=24):
    """Un cilindre vertical: les facetes que es veuen. `lvl(angle, y, P)`."""
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        p0 = (cx + r * math.cos(a0), cz + r * math.sin(a0))
        p1 = (cx + r * math.cos(a1), cz + r * math.sin(a1))
        e.quad(sid, (p0[0], y1, p0[1]), (p1[0], y1, p1[1]), (p1[0], y0, p1[1]), (p0[0], y0, p0[1]), ramp=ramp,
               lvl=lambda s, t, P: lvl(math.atan2(P[2] - cz, P[0] - cx), P[1], P))


def tronc(e, sid, cx, cz, wb, db, wt, dt, zt, y0, y1, ramp, lvl):
    """Un tronc de piràmide (una campana): la base wb × db centrada a (cx, cz), el cim wt × dt centrat a (cx, zt),
    de y0 a y1. Les cares inclinades que es veuen (trapezis: el polígon és el dels quatre cantons); `lvl(s, t, P)`."""
    zb0, zb1, zt0, zt1 = cz - db / 2, cz + db / 2, zt - dt / 2, zt + dt / 2
    xb0, xb1, xt0, xt1 = cx - wb / 2, cx + wb / 2, cx - wt / 2, cx + wt / 2
    e.quad(sid, (xt1, y1, zt0), (xt1, y1, zt1), (xb1, y0, zb1), (xb1, y0, zb0), ramp=ramp, lvl=lvl)
    e.quad(sid, (xt0, y1, zt1), (xt0, y1, zt0), (xb0, y0, zb0), (xb0, y0, zb1), ramp=ramp, lvl=lvl)
    e.quad(sid, (xt0, y1, zt0), (xt1, y1, zt0), (xb1, y0, zb0), (xb0, y0, zb0), ramp=ramp, lvl=lvl)


def _local(o, a):
    """Un sistema de coordenades girat `a` al voltant de la vertical, amb l'origen a o = (x, z): (u, y, w) → món."""
    c, s_ = math.cos(a), math.sin(a)
    return lambda u, y, w: (o[0] + u * c - w * s_, y, o[1] + u * s_ + w * c)


# ─── La sala ────────────────────────────────────────────────────────────────

def nau(e):
    zn = CAM.pos[2] - 60
    # el sostre, negre, amb les encavallades de ferro (fugen cap al fons)
    e.quad('sostre', (0, HW, zn), (XR + 400, HW, zn), (XR + 400, HW, ZB), (0, HW, ZB), ramp=COAL,
           lvl=lambda s, t, P: 0.6 + (fbm(P[0] / 80, P[2] / 60, 3) - 0.5) * 0.6, dues_cares=True)
    for z in (380, 620, ZB - 20):
        e.cable('sostre', [(0, HW - 8, z), (XR + 200, HW - 8, z)], IRONF, 1.6, gruix=6)
        for x in range(0, int(XR) + 200, 70):
            e.cable('sostre', [(x, HW - 8, z), (x + 35, HW + 40, z), (x + 70, HW - 8, z)], IRONF, 1.2, gruix=2.4)
    # la paret de l'esquerra (la del carrer): maó, amb pilastres; de prop, més sutge
    e.quad('paret_esq', (0, HW, zn), (0, HW, ZB), (0, 0, ZB), (0, 0, zn), ramp=SOOT,
           lvl=lambda s, t, P: _brick(17)(P[2], P[1]) - 0.9 * max(0.0, 1 - (HW - P[1]) / 120))
    # la paret del fons (el dibuix pla) i la de la dreta del pas (planxa de maó més enllà del dibuix)
    e.quad('paret_fons', (0, HW, ZB), (XR, HW, ZB), (XR, 0, ZB), (0, 0, ZB), tex=(_paret(), (0, 31, W, 198)))
    e.quad('paret_fons', (XR, HW, ZB), (XR + 600, HW, ZB), (XR + 600, 0, ZB), (XR, 0, ZB), ramp=SOOT,
           lvl=lambda s, t, P: _brick(19)(P[0], P[1]))
    # el terra, i les planxes davant la boca
    e.quad('terra', (0, 0, ZB), (XR + 600, 0, ZB), (XR + 600, 0, zn), (0, 0, zn), ramp=COB, lvl=_terra)
    e.quad('terra', (FORN[0] - 20, 0.2, FZ0), (FORN[1] + 30, 0.2, FZ0), (FORN[1] + 30, 0.2, FZ0 - 92),
           (FORN[0] - 20, 0.2, FZ0 - 92), ramp=IRONF, lvl=_planxes)
    # el pas a la colada: els brancals de maó, que fan gruix, i el terra de l'altra banda, fosc
    x0, x1, ph = PAS
    e.quad('pas_terra', (x0, 0.3, ZB + 120), (x1, 0.3, ZB + 120), (x1, 0.3, ZB), (x0, 0.3, ZB), ramp=COB,
           lvl=lambda s, t, P: 1.0 - t / 120)
    for bx in (x0 - 14, x1):
        e.caixa('pas', bx, bx + 14, 0, ph + 10, ZB - 16, ZB, MORTAR, 2.4,
                cares={'davant': {'ramp': MORTAR, 'lvl': lambda s, t, P: _brick(23, 2.8)(P[0], P[1])},
                       'esquerra': {'ramp': MORTAR, 'lvl': 1.8}, 'dreta': {'ramp': MORTAR, 'lvl': 1.6}})
    e.caixa('pas', x0 - 14, x1 + 14, ph, ph + 14, ZB - 16, ZB, MORTAR, 3.0)
    # la porta del carrer: l'obertura (el dibuix pla), i la fulla de fusta oberta cap a dins
    z0, z1, dh = DOOR
    e.quad('porta', (0.5, dh, z0), (0.5, dh, z1), (0.5, 0, z1), (0.5, 0, z0), tex=(_porta(), (9, 102, 70, 198)))
    a = math.radians(64)                                           # (oberta 64°, amb la frontissa al brancal del fons)
    fx = 80 * math.sin(a)
    e.quad('porta_fulla', (0.5, dh - 6, z1 + 2), (fx, dh - 6, z1 + 2 - 80 * math.cos(a)),
           (fx, 2, z1 + 2 - 80 * math.cos(a)), (0.5, 2, z1 + 2), ramp=PLANKF, dues_cares=True,
           lvl=lambda s, t, P: 2.6 - (1.4 if s % 12 < 1.4 else 0) + (fbm(s / 5, t / 30, 4) - 0.5) * 0.8
           - (1.0 if abs(t - 30) < 3 or abs(t - 120) < 3 else 0))
    # la claror del carrer: entra per la porta i s'escampa en ventall pel terra, cap a la dreta i endavant
    zc = (z0 + z1) / 2

    def ventall(s, t):
        x, dz = s, (z1 + 60 - t) - zc
        return 0.8 * max(0.0, 1 - x / 440) ** 1.2 * max(0.0, 1 - abs(dz + 0.38 * x) / (52 + 0.5 * x)) ** 0.8
    e.claror((0, 0.5, z1 + 60), (440, 0.5, z1 + 60), (440, 0.5, 380), (0, 0.5, 380), (206, 182, 156), ventall)
    # la foscor dels racons: on les parets toquen a terra, la cantonada, i el sostre
    e.foscor('racons', (0, 0.5, ZB), (XR + 600, 0.5, ZB), (XR + 600, 0.5, zn), (0, 0.5, zn),
             lambda s, t: max(0.6 * max(0.0, 1 - t / 60), 0.5 * max(0.0, 1 - s / 50)))
    e.foscor('cantonada', (0, HW, ZB - 0.5), (120, HW, ZB - 0.5), (120, 0, ZB - 0.5), (0, 0, ZB - 0.5),
             lambda s, t: 0.6 * max(0.0, 1 - s / 120))
    e.foscor('dalt', (0, HW, ZB - 0.6), (XR, HW, ZB - 0.6), (XR, HW - 140, ZB - 0.6), (0, HW - 140, ZB - 0.6),
             lambda s, t: 0.55 * max(0.0, 1 - t / 140))
    e.foscor('dalt_esq', (0.6, HW, zn), (0.6, HW, ZB), (0.6, HW - 140, ZB), (0.6, HW - 140, zn),
             lambda s, t: 0.55 * max(0.0, 1 - t / 140))
    # els feixos de llum dels finestrals, en diagonal fins a terra
    for wx in WINDOWS:
        a0, a1 = wx * KW, (wx + 28) * KW
        e.claror((a0, 262, ZB - 2), (a1, 262, ZB - 2), (a1 + 70, 0, ZB - 330), (a0 + 70, 0, ZB - 330), (190, 150, 116),
                 lambda s, t: 0.24 * (1 - t / 420) * (0.5 + fbm(s / 12, t / 40, wx)))


def columna(e, sid, x, z, fins=None):
    """Una columna de ferro colat: el fust, el capitell que aguanta la biga del carril de la grua, i la base."""
    lv = lambda a, y, P: 2.6 - math.cos(a - 2.0) * 1.2 + (1.2 if y % 60 < 3 else 0)       # noqa: E731
    cilindre(e, sid, x, z, 8, 0, 236, IRONF, lv, n=14)
    e.caixa(sid, x - 13, x + 13, 0, 10, z - 13, z + 13, IRONF, 2.8,
            cares={'dalt': {'ramp': IRONF, 'lvl': 3.8}, 'davant': {'ramp': IRONF, 'lvl': 2.6}})
    e.caixa(sid, x - 14, x + 14, 232, 244, z - 14, z + 14, IRONF, 3.0, cares={'davant': {'ramp': IRONF, 'lvl': 2.4}})


def bigues(e):
    """Les bigues del carril de la grua, damunt les columnes: fugen cap al fons."""
    zn = CAM.pos[2] - 40
    for x, _ in (COL1, COL2):
        e.caixa('bigues', x - 10, x + 10, 244, 270, zn, ZB, IRONF, 2.4,
                cares={'davant': {'ramp': IRONF, 'lvl': 1.4},
                       'esquerra': {'ramp': IRONF, 'lvl': lambda s, t, P: 1.8 + (1.2 if t < 3 else 0)
                                    - (1.4 if P[2] % 90 < 3 else 0)},
                       'dreta': {'ramp': IRONF, 'lvl': lambda s, t, P: 1.8 - (1.2 if P[2] % 90 < 3 else 0)},
                       'sota': {'ramp': IRONF, 'lvl': 0.6}})
        e.caixa('bigues', x - 3, x + 3, 270, 276, zn, ZB, IRONF, 3.6)                     # el carril


def forn(e, fire):
    x0, x1, fd, fh = FORN
    tex = _forn(fire)
    side = _brick(23, 2.8, soot=lambda a, y: 0.8 * max(0.0, 1 - y / 40))
    # el cos de maó refractari: la façana és el dibuix pla (x 168..342, de y 96 a la base, 206)
    e.caixa('forn', x0, x1, 0, fh, FZ0, ZB, SOOT, 2.6,
            cares={'davant': {'tex': (tex, (168, 96, 342, 206))},
                   'dreta': {'ramp': SOOT, 'lvl': lambda s, t, P: side(P[2], P[1])},
                   'esquerra': {'ramp': SOOT, 'lvl': lambda s, t, P: side(P[2], P[1])},
                   'dalt': {'ramp': IRONF, 'lvl': 1.6}})
    # els cèrcols i els tirants de ferro que l'abracen pels costats
    for y in (22, fh - 26):
        e.caixa('forn', x0 - 3, x0, y, y + 5, FZ0 - 3, ZB, IRONF, 3.2)
        e.caixa('forn', x1, x1 + 3, y, y + 5, FZ0 - 3, ZB, IRONF, 3.2)
    # la vora de la campana i la campana (un tronc de piràmide de planxa), i la xemeneia
    e.caixa('forn', x0 - 8, x1 + 8, fh, fh + 7, FZ0 - 8, ZB, IRONF, 3.4,
            cares={'davant': {'ramp': IRONF, 'lvl': lambda s, t, P: 3.4 + (1.4 if s % 24 < 2 and 2 < t < 5 else 0)}})
    hood = lambda s, t, P: (2.8 + (fbm(P[0] / 12, P[1] / 16, 21) - 0.5) * 1.2           # noqa: E731
                            - (1.2 if (P[0] - FCX) % 30 < 1.6 else 0) - (0.9 if P[1] % 44 < 1.4 else 0))
    tronc(e, 'forn', FCX, (FZ0 - 8 + ZB) / 2, x1 - x0 + 16, ZB - FZ0 + 8, 60, 52, ZB - 34, fh + 7, HOOD, IRONF,
          hood)
    cilindre(e, 'forn', FCX, ZB - 34, 26, HOOD, HW + 60, IRONF,
             lambda a, y, P: 2.4 - math.cos(a - 2.0) * 1.2 + (1.4 if y % 70 < 4 else 0), n=18)
    # la tovera (el tub de la manxa entra pel costat de la dreta)
    e.tub('forn', (x1 + 2, 38, FZ0 + 46), _local(MANXA[:2], MANXA[2])(-6, 39, 0), 4.4, IRONF, 2.8, brides=40)


def manxa(e):
    """La manxa: el fol de cuir en falca sobre el cavallet, girat; la palanca, amb el pal, la biga i la cadena."""
    hx, hz, ang, Lm, Wm = MANXA
    L = _local((hx, hz), ang)
    w2 = Wm / 2
    ub, uc = Lm / 2, Lm + 2
    # el cavallet: dues potes en A i el travesser
    for u in (18, Lm - 16):
        cx, _, cz = L(u, 0, 0)
        e.caixa_girada('manxa', cx, cz, 7, Wm + 14, 30, ang, PLANKF, 2.6,
                       cares={'dalt': {'ramp': PLANKF, 'lvl': 3.8}, 'davant': {'ramp': PLANKF, 'lvl': 2.4}})
    cx, _, cz = L(ub, 0, 0)
    e.caixa_girada('manxa', cx, cz, Lm + 4, Wm + 8, 5, ang, PLANKF, 3.4, y0=30,
                   cares={'dalt': {'ramp': PLANKF, 'lvl': 4.0}})
    # el cuir: els dos costats (falques amb els plecs) i el darrere (el fons de l'acordió)
    top = lambda u: 38 + 36 * u / Lm                                                      # noqa: E731
    pleat = lambda s, t, P, hgt: (2.6 + (1.4 if ((hgt - t) / max(1.0, hgt) * 5) % 1 < 0.35 else -0.2)  # noqa: E731
                                  - (1.0 if ((hgt - t) / max(1.0, hgt) * 5) % 1 > 0.88 else 0))
    for w in sorted((-w2, w2), key=lambda w: -math.dist(L(ub, 50, w), CAM.pos)):
        e.quad('manxa', L(0, 76, w), L(Lm, 76, w), L(Lm, 35, w), L(0, 35, w), ramp=PPELL, dues_cares=True,
               lvl=lambda s, t, P: pleat(s, t - (76 - top(s)), P, top(s) - 35),
               forma=lambda s, t: t >= 76 - top(s) - 0.5)
    e.quad('manxa', L(Lm, 74, -w2), L(Lm, 74, w2), L(Lm, 35, w2), L(Lm, 35, -w2), ramp=PPELL, dues_cares=True,
           lvl=lambda s, t, P: 2.4 + (1.4 if (t / 39 * 5) % 1 < 0.35 else -0.4) - abs(s - w2) / w2 * 0.6)
    # la post de dalt, inclinada, amb dos cèrcols de ferro, i el pes de pedra
    e.quad('manxa', L(-4, 40, -w2 - 3), L(uc, 77, -w2 - 3), L(uc, 77, w2 + 3), L(-4, 40, w2 + 3), ramp=PLANKF,
           dues_cares=True,
           lvl=lambda s, t, P: 3.8 - (1.4 if s % 18 < 1.2 else 0) + (1.4 if abs(s - 40) < 3 or abs(s - 78) < 3 else 0))
    # el broc, de ferro
    e.tub('manxa', L(-14, 39, 0), L(2, 39, 0), 5, IRONF, 3.2)
    # la palanca: el pal, la biga (de l'extrem del fol cap enlaire), la barra i la cadena amb el mànec
    px, _, pz = L(Lm + 14, 0, w2 + 20)
    e.caixa('manxa', px - 3, px + 3, 0, 150, pz - 3, pz + 3, PLANKF, 3.0,
            cares={'davant': {'ramp': PLANKF, 'lvl': lambda s, t, P: 3.2 - (0.8 if t % 40 < 2 else 0)}})
    e.caixa('manxa', px - 7, px + 7, 0, 7, pz - 7, pz + 7, PLANKF, 2.6)
    A = L(Lm - 18, 116, w2 + 20)
    B = L(Lm + 60, 164, -46)
    e.cable('manxa', [A, (px, 150, pz), B], PLANKF, 3.8, gruix=5)
    e.cable('manxa', [L(Lm - 4, 78, 0), A], IRONF, 3.4, gruix=2)
    e.cable('manxa', [B, (B[0], 70, B[2])], IRONF, 4.2, gruix=1.6)
    e.caixa('manxa', B[0] - 9, B[0] + 9, 62, 66, B[2] - 2, B[2] + 2, PLANKF, 4.2)



def termometre(e, fire):
    x, z = COL1
    # el capil·lar: de l'esfera, columna avall i pel terra fins al costat del forn
    e.cable('capil', [(x - 2, DIAL_Y - 12, z - 10), (x - 2, 4, z - 10), (x + 30, 1.2, z + 10),
                      (FORN[0] - 30, 1.2, FZ0 + 30), (FORN[0], 30, FZ0 + 30)], IRONF, 2.6, gruix=1.4)
    img, peu = _dial(fire)
    e.sprite('termometre', img, peu, (x, DIAL_Y, z - 12), escala_img=1.4)


def rascle(e):
    x, z = COL2
    foot, top = (x - 34, 2, z - 24), (x - 6, 168, z - 10)
    e.cable('rascle', [foot, top], IRONF, 3.8, gruix=2.4)
    e.cable('rascle', [(top[0], top[1] - 2, top[2]), (top[0] + 1, top[1] + 12, top[2] + 1)], PLANKF, 4.0, gruix=3.4)
    a = 0.5
    e.quad('rascle', (foot[0] - 15 * math.cos(a), 12, foot[2] + 15 * math.sin(a)),
           (foot[0] + 15 * math.cos(a), 12, foot[2] - 15 * math.sin(a)),
           (foot[0] + 15 * math.cos(a), 0.6, foot[2] - 15 * math.sin(a)),
           (foot[0] - 15 * math.cos(a), 0.6, foot[2] + 15 * math.sin(a)), ramp=IRONF, dues_cares=True,
           lvl=lambda s, t, P: 3.0 - t * 0.08 + (fbm(s / 4, t / 4, 5) - 0.5))


def metall(e):
    """La pila de comptadors (el dibuix pla, dret) i la carretilla, girada, amb la seva ombra."""
    mx, mz = METALL
    e.foscor('ombra_metall', (mx - 64, 0.6, mz + 26), (mx + 64, 0.6, mz + 26), (mx + 64, 0.6, mz - 34),
             (mx - 64, 0.6, mz - 34), lambda s, t: 0.6 * max(0.0, 1 - ((s - 64) / 64) ** 2 - ((t - 30) / 30) ** 2) * 1.6)
    img, peu = _pila()
    e.sprite('metall', img, peu, (mx, 0, mz), escala_img=1.5)
    cx, cz, a = CARRET
    L = _local((cx, cz), a)
    e.foscor('ombra_metall', L(-36, 0.6, -24), L(36, 0.6, -24), L(36, 0.6, 24), L(-36, 0.6, 24),
             lambda s, t: 0.55 * max(0.0, 1 - ((s - 36) / 36) ** 2 - ((t - 24) / 24) ** 2) * 1.5)
    e.caixa_girada('metall', cx, cz, 50, 32, 16, a, IRONF, 2.8, y0=14,
                   cares={'dalt': {'ramp': COB, 'lvl': lambda s, t, P: 1.0 if 3 < s < 47 and 3 < t < 29 else 4.4},
                          'davant': {'ramp': IRONF, 'lvl': lambda s, t, P: 3.2 - t * 0.08},
                          'dreta': {'ramp': IRONF, 'lvl': 2.2}, 'esquerra': {'ramp': IRONF, 'lvl': 3.6}})
    e.quad('metall', L(-34, 16, 0), L(-18, 16, 0), L(-18, 0, 0), L(-34, 0, 0), ramp=RUSTF, dues_cares=True,
           lvl=lambda s, t, P: 2.4 + (1.4 if math.hypot(s - 8, t - 8) > 5.6 else -0.6),
           forma=lambda s, t: math.hypot(s - 8, t - 8) <= 8)                               # la roda
    for w in (-12, 12):                                                                   # els mànecs
        e.cable('metall', [L(22, 28, w), L(56, 22, w * 1.1), L(58, 0, w * 1.1)], PLANKF, 3.6, gruix=2.2)


def primer_pla(e):
    """Fosc i tallat per la vora: les caixes de motlles de la dreta, la cadena del polispast i el munt de carbó."""
    for (cx, cz, w, d, h, ang, y0) in ((640, 420, 96, 60, 44, 0.32, 0), (700, 470, 80, 56, 40, -0.2, 0),
                                       (650, 424, 70, 46, 30, 0.5, 44)):
        e.caixa_girada('primer_pla', cx, cz, w, d, h, ang, PLANKF, 1.4, y0=y0,
                       cares={'dalt': {'ramp': PLANKF, 'lvl': lambda s, t, P: 2.2 - (1.2 if s % 16 < 1.4 else 0)},
                              'davant': {'ramp': PLANKF, 'lvl': lambda s, t, P: 1.2 - (0.8 if t % 11 < 1.2 else 0)
                                         + (1.0 if s < 3 else 0)},
                              'esquerra': {'ramp': PLANKF, 'lvl': 0.8}, 'dreta': {'ramp': PLANKF, 'lvl': 0.6}})
    hx, hz = 430, 330                                                                     # el polispast
    for dx in (-6, 6):
        e.cable('primer_pla', [(hx + dx, HW + 30, hz), (hx + dx * 0.5, 156, hz)], IRONF, 2.0, gruix=2.4)
    e.caixa('primer_pla', hx - 5, hx + 5, 146, 158, hz - 3, hz + 3, IRONF, 3.4,
            cares={'davant': {'ramp': IRONF, 'lvl': lambda s, t, P: 3.2 + (1.6 if 4 < t < 7 else 0)}})  # el bossell
    e.cable('primer_pla', [(hx, 144, hz), (hx, 130, hz), (hx - 6, 122, hz), (hx, 116, hz), (hx + 5, 120, hz)],
            IRONF, 2.8, gruix=2.6)                                                         # el ganxo
    for (x, z, r, seed) in ((150, 384, 52, 3), (70, 420, 38, 5), (236, 380, 22, 7)):
        e.roca('primer_pla', (x, 0, z), r, COAL, 1.6, llum_dir=(-0.6, -0.6), seed=seed)


def ombres_foc(e):
    """Amb el forn encès, les ombres llargues que el foc de la boca fa pel terra, lluny de la boca."""
    bx, bz = FCX, FZ0 - 24
    L = _local(MANXA[:2], MANXA[2])
    for (x, z, w, ll) in ((*COL1, 22, 260), (*COL2, 22, 300), (METALL[0], METALL[1], 110, 220),
                          (CARRET[0], CARRET[1], 60, 200), (L(MANXA[3] / 2, 0, 0)[0], L(MANXA[3] / 2, 0, 0)[2], 70, 160)):
        d = math.hypot(x - bx, z - bz)
        dx, dz = (x - bx) / d, (z - bz) / d
        px, pz = -dz * w / 2, dx * w / 2
        P0, P1 = (x - px, 0.7, z - pz), (x + px, 0.7, z + pz)
        e.foscor('ombra_foc', P0, P1, (P1[0] + dx * ll, 0.7, P1[2] + dz * ll), (P0[0] + dx * ll, 0.7, P0[2] + dz * ll),
                 lambda s, t, w=w, ll=ll: 0.75 * (1 - t / ll) * min(1.0, (w / 2 - abs(s - w / 2)) / (w * 0.2) + 0.1))


def escena(cv, fire=0, foc=False):
    """Tota la sala, de lluny a prop; `fire`: el dibuix del forn (0, 1, 2); `foc`: la llum del foc al món."""
    e = Escena(cv, CAM, LLUMS + ([FOC[fire]] if foc and fire else []), ambient=AMBIENT)
    nau(e)
    forn(e, fire)
    bigues(e)
    # les ombres a terra: el forn, la manxa, les columnes
    e.foscor('ombra', (FORN[0] - 30, 0.6, FZ0), (FORN[1] + 30, 0.6, FZ0), (FORN[1] + 30, 0.6, FZ0 - 40),
             (FORN[0] - 30, 0.6, FZ0 - 40), lambda s, t: 0.5 * max(0.0, 1 - t / 40))
    L = _local(MANXA[:2], MANXA[2])
    e.foscor('ombra', L(-10, 0.6, -40), L(MANXA[3] + 20, 0.6, -40), L(MANXA[3] + 20, 0.6, 40), L(-10, 0.6, 40),
             lambda s, t: 0.55 * max(0.0, 1 - ((s - 70) / 70) ** 2 - ((t - 40) / 40) ** 2) * 1.6)
    for x, z in (COL1, COL2):
        e.foscor('ombra', (x - 14, 0.6, z + 70), (x + 40, 0.6, z + 70), (x + 40, 0.6, z - 30), (x - 14, 0.6, z - 30),
                 lambda s, t: 0.45 * max(0.0, 1 - abs(s - 14 - (t - 30) * 0.25) / 14) * max(0.0, 1 - abs(t - 30) / 40))
    if foc and fire:
        ombres_foc(e)
    manxa(e)
    columna(e, 'columna_dreta', *COL2)
    rascle(e)
    columna(e, 'columna_esq', *COL1)
    termometre(e, fire)
    metall(e)
    primer_pla(e)
    return e


# ─── Composició ────────────────────────────────────────────────────────────

def _negre(cv):
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)      # la barra de verbs: negre


@functools.lru_cache(maxsize=None)
def _escena(fire, foc):
    cv = Canvas(light=LIGHT)
    e = escena(cv, fire, foc)
    _negre(cv)
    return cv.img, e


@functools.lru_cache(maxsize=None)
def _base(fire=0):
    """La sala amb el forn en l'estat `fire`: sense foc, tal qual; amb foc, la llum del foc tenyida de taronja."""
    img, e = _escena(fire, False)
    if not fire:
        return img, e
    lit, _ = _escena(fire, True)
    a = np.asarray(lit).astype(np.float32)
    b = np.asarray(img).astype(np.float32)
    dl = np.clip((a[..., :3] - b[..., :3]).mean(axis=2, keepdims=True), 0, None)
    out = b[..., :3] + dl * np.array(TARONJA[fire], np.float32) * 1.6
    out = np.concatenate([np.clip(out, 0, 255), b[..., 3:]], axis=2).astype(np.uint8)
    return Image.fromarray(out, 'RGBA'), e


def bg(cv):
    img, _ = _base(0)
    cv.img.paste(img)
    cv.P = cv.img.load()


def _fire_prop(fire):
    def fn(cv):
        cv.img.alpha_composite(_diff(_base(fire)[0], _base(0)[0]))
    return fn


PROPS = {'forn_ences': _fire_prop(1), 'forn_fort': _fire_prop(2)}


def _flames(fire):
    _, e = _base(fire)
    return [e.capa(f, {'forn'}) for f in PL._flames(fire)]


def _frames_guspires():
    """Guspires que salten de la boca cap a la càmera i cauen fent un arc, al món (a la mida de cada distància)."""
    out = []
    n = 16
    for f in range(n):
        cv = Canvas(transparent=True)
        for k in range(12):
            s = ((f / n) + hr(k, 1)) % 1
            P0 = (FCX + (hr(k, 4) - 0.5) * 50, 40 + hr(k, 6) * 20, FZ0 - 4)
            v = ((hr(k, 2) - 0.5) * 120, 70 + hr(k, 3) * 70, -90 - hr(k, 5) * 120)
            P = (P0[0] + v[0] * s, P0[1] + v[1] * s - 220 * s * s, P0[2] + v[2] * s)
            if s > 0.85 or P[1] < 0:
                continue
            u, vv, _ = CAM.projecta(P)
            c = FIREF[6] if s < 0.25 else FIREF[5] if s < 0.55 else FIREF[3]
            if 0 <= u < W and 0 <= vv < BOTTOM:
                cv.flat(u, vv, c)
                if s < 0.45:
                    Q = (P[0] - v[0] * 0.03, P[1] - (v[1] - 440 * s) * 0.03, P[2] - v[2] * 0.03)
                    uq, vq, _ = CAM.projecta(Q)
                    if 0 <= uq < W and 0 <= vq < BOTTOM:
                        cv.flat(uq, vq, FIREF[4])
        out.append(cv.img)
    return out


ANIMS = {'foc': {'frames': lambda: _flames(1), 'frameDuration': 100},
         'foc_fort': {'frames': lambda: _flames(2), 'frameDuration': 80},
         'guspires': {'frames': _frames_guspires, 'frameDuration': 70}}


def _amo(ids):
    def mask(x, y):
        _, e = _base(0)
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
    """L'escala d'un personatge amb els peus a la y de pantalla `v` (al terra, la profunditat només depèn de v)."""
    lo, hi = 1.0, 4000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.projecta((420, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((420, 0, (lo + hi) / 2))


def _cercle(cx, cz, r, n=10):
    return [_p(cx + r * math.cos(2 * math.pi * i / n), cz + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def _manxa_peu():
    hx, hz, ang, Lm, Wm = MANXA
    L = _local((hx, hz), ang)
    return [(L(u, 0, w)[0], L(u, 0, w)[2]) for u, w in ((-6, -Wm / 2 - 10), (Lm + 34, -Wm / 2 - 10),
                                                       (Lm + 34, Wm / 2 + 30), (-6, Wm / 2 + 10))]


# El terra on es camina (al món): de la porta del carrer fins al pas de la colada, davant el forn; no arriba al
# primer pla (el pilar i el carbó). Forats: la manxa, les columnes, la pila i la carretilla.
WALK_MON = [(14, 450), (14, DOOR[1] - 6), (90, DOOR[1] - 6), (FORN[0] - 24, FZ0 - 14), (FORN[1] + 4, FZ0 - 14),
            (FORN[1] + 4, ZB - 12), (PAS[0] + 6, ZB - 10), (PAS[0] + 6, ZB + 40), (PAS[1] - 6, ZB + 40),
            (PAS[1] - 6, ZB - 12), (900, 680), (900, 610), (790, 572), (560, 512), (300, 432), (190, 440), (110, 470)]
_WALK = [_p(x, z) for x, z in WALK_MON]
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)
_MP = _manxa_peu()


def _vfront(*xz):
    """La línia base d'una cosa: la y de pantalla del seu punt de terra més proper."""
    return round(max(_p(x, z)[1] for x, z in xz))


FRONT = [
    {'id': 'davant_manxa', 'mask': _amo({'manxa'}), 'baseline': _vfront(*_MP), 'zIndex': 20},
    {'id': 'davant_columna_esq', 'mask': _amo({'columna_esq', 'termometre'}),
     'baseline': _vfront((COL1[0], COL1[1] - 13)), 'zIndex': 20},
    {'id': 'davant_columna_dreta', 'mask': _amo({'columna_dreta', 'rascle'}),
     'baseline': _vfront((COL2[0], COL2[1] - 13), (COL2[0] - 34, COL2[1] - 24)), 'zIndex': 20},
    {'id': 'davant_metall', 'mask': _amo({'metall'}),
     'baseline': _vfront((METALL[0], METALL[1] - 10), (CARRET[0] + 30, CARRET[1] - 30)), 'zIndex': 20},
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20},
]

_DIAL = CAM.projecta((COL1[0], DIAL_Y, COL1[1] - 12))
_DR = 15 * 1.4 * CAM.escala((COL1[0], DIAL_Y, COL1[1] - 12))

GEOMETRIA = {
    'things': {
        'porta': {'rect': _rect_mon((0, DOOR[2], DOOR[0]), (0, 0, DOOR[1])), 'walk': _p(30, (DOOR[0] + DOOR[1]) / 2)},
        'pas': {'rect': _rect_mon((PAS[0], PAS[2], ZB), (PAS[1], 0, ZB)), 'walk': _p((PAS[0] + PAS[1]) / 2, ZB + 20)},
        'forn': {'rect': _rect_mon((FORN[0], HOOD, ZB - 40), (FORN[1], 0, FZ0)), 'walk': _p(FCX, FZ0 - 40)},
        'manxa': {'rect': _rect_mon(*[(x, 0, z) for x, z in _MP], *[(x, 80, z) for x, z in _MP[:2]],
                                    _local(MANXA[:2], MANXA[2])(MANXA[3] + 60, 168, -46),
                                    _local(MANXA[:2], MANXA[2])(MANXA[3] + 60, 60, -46)),
                  'walk': _p(*_local(MANXA[:2], MANXA[2])(MANXA[3] + 40, 0, -40)[::2])},
        'metall': {'rect': _rect_mon((METALL[0] - 70, 60, METALL[1]), (CARRET[0] + 40, 0, CARRET[1] - 40)),
                   'walk': _p(METALL[0] + 60, METALL[1] - 70)},
        'rascle': {'rect': _rect_mon((COL2[0] - 50, 180, COL2[1] - 24), (COL2[0] + 2, 0, COL2[1] - 24)),
                   'walk': _p(COL2[0] - 40, COL2[1] - 70)},
        'termometre': {'rect': (round(_DIAL[0] - _DR - 2), round(_DIAL[1] - _DR - 2), round(_DIAL[0] + _DR + 2),
                                round(_DIAL[1] + _DR + 2)),
                       'walk': _p(COL1[0] + 50, COL1[1] - 60)},
    },
    'spawns': {'iri': _p(380, 500), 'vet': _p(500, 540)},
    'walkable': _WALK,
    'forats': [[_p(x, z) for x, z in _MP], _cercle(*COL1, 22, 8), _cercle(*COL2, 22, 8),
               _cercle(METALL[0], METALL[1], 56, 10), _cercle(CARRET[0], CARRET[1], 40, 8)],
    # La càmera, a 1,85 m i mirant avall, aixafa el terra: 185 d'alçada a ≈500 de fons (on es camina).
    'floorSquash': 0.4,
    # L'ombra de contacte: la llum dominant és la claror del carrer, per la porta (l'ombra cau cap a la dreta).
    'characterShadow': {'enabled': True, 'color': '#120a08', 'alpha': 0.42, 'squash': 0.4, 'core': 0.6,
                        'light': {'x': _p(10, (DOOR[0] + DOOR[1]) / 2)[0], 'y': _p(10, (DOOR[0] + DOOR[1]) / 2)[1],
                                  'stretch': 0.8, 'reach': 160}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
}
