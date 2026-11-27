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
**comptadors** (el **metall**) i una carretilla girada. Pel terra, la brossa de la foneria: una pila de lingots
damunt un palet, el bidó d'aigua amb la cullera, el munt d'escòria amb les tenalles i una filera de lingoteres (es
passa per darrere dels lingots, el bidó i l'escòria). En primer pla, fosc i tallat per la vora, les caixes de motlles,
la cadena d'un polispast que penja, un munt de carbó i una enclusa damunt la soca. Les capes del davant tenen la seva
versió amb el foc (`variants`): si no, la capa, retallada del fons apagat, taparia la llum.

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

from hd.pix import Canvas, Light, W, H, hr, B4
from hd.rooms.comu import _diff
from hd.rooms.exterior import fbm
from hd640.rooms import fosa_forn_pla_comu as PL
from hd640.rooms.ferrum_comu import (RH, SMOG, SLAGF, SOOT, MORTAR, COB, COAL, IRONF, RUSTF, PLANKF, FIREF,
                                     brick_lvl, nave_wall, crane_rail, pila_comptadors)
from hd640.tres_d import Camera, Escena, Llum, llum_personatges

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
LINGOTS = (476.0, 552.0, 0.35)                     # la pila de lingots al palet (x, z, angle)
LINGOTERES = (580.0, 474.0, -0.18)                 # la filera de lingoteres, a terra, davant (x, z, angle)
ESCORIA = (628.0, 592.0, 26.0)                     # el munt d'escòria tret del forn (x, z, radi), amb les tenalles
BIDO = (292.0, 528.0)                              # el bidó d'aigua per refredar les eines (x, z)
ENCLUSA = (318.0, 388.0, 0.45)                     # l'enclusa damunt la soca, en primer pla (x, z, angle)

CAM = Camera(pos=(520, 185, 60), yaw=-0.16, pitch=0.11, f=430, centre=(330, 108))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)      # (la llum és la del món: la de l'Escena)
PLA = Light(ambient=0.2, vignette=None, floor_fade=None)        # la llum neutra de les textures planes
AMBIENT = -1.2
WINDOWS = (40, 300, 520)                           # els finestrals (x del dibuix pla de la paret del fons)
LLUMS = [Llum(((wx + 14) * KW, 220, ZB - 70), 420, 1.0, power=1.4) for wx in WINDOWS] + [
    Llum((20, 80, (DOOR[0] + DOOR[1]) / 2), 560, 2.8, power=1.3),          # la claror del carrer, per la porta
]
FOC = {1: Llum((FCX, 46, FZ0 - 24), 760, 3.0, power=1.2), 2: Llum((FCX, 50, FZ0 - 24), 900, 4.0, power=1.1)}
MOLTEN = [(120, 20, 6), (190, 52, 10), (236, 110, 24), (255, 170, 60), (255, 220, 130), (255, 250, 220)]  # el metall fos
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
def _dial(fire, tremola=0.0, temp=None):
    cv = Canvas(light=PLA, transparent=True)
    PL.termometre(cv, fire, tremola, temp)
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


def _palanca(p):
    """La palanca de la manxa amb el fol tancat `p` (0: obert del tot, com és sempre; 1: tancat): la biga gira pel cap
    del pal. → (A, el cap del pal, B, el cap del fol): A, l'extrem del fol (lligat al fol per la barra); B, el de la
    cadena."""
    hx, hz, ang, Lm, Wm = MANXA
    L = _local((hx, hz), ang)
    w2 = Wm / 2
    px, _, pz = L(Lm + 14, 0, w2 + 20)
    Pv = (px, 150.0, pz)
    A0, B0 = L(Lm - 18, 116, w2 + 20), L(Lm + 60, 164, -46)
    d = (B0[0] - A0[0], B0[2] - A0[2])
    n = math.hypot(*d)
    k = (-d[1] / n, 0.0, d[0] / n)                       # l'eix: horitzontal, de través a la biga
    rA = math.dist(A0, Pv)
    th = 30 * p / rA

    def gira(P):                                          # (Rodrigues)
        v = (P[0] - Pv[0], P[1] - Pv[1], P[2] - Pv[2])
        c, sn = math.cos(th), math.sin(th)
        kv = (k[1] * v[2] - k[2] * v[1], k[2] * v[0] - k[0] * v[2], k[0] * v[1] - k[1] * v[0])
        kd = k[0] * v[0] + k[1] * v[1] + k[2] * v[2]
        return tuple(Pv[i] + v[i] * c + kv[i] * sn + k[i] * kd * (1 - c) for i in range(3))
    A, B = gira(A0), gira(B0)
    if A[1] > A0[1]:                                      # (el sentit de gir: A ha de baixar)
        th = -th
        A, B = gira(A0), gira(B0)
    return A, Pv, B, L(Lm - 4, 78 - 30 * p, 0)


def manxa(e, p=0.0, part=None):
    """La manxa: el fol de cuir en falca sobre el cavallet, girat; la palanca, amb el pal, la biga i la cadena.
    `p`: com de tancat és el fol (0: obert). `part`: 'fix' (el cavallet, el broc i el pal), 'fol' (el que es mou: el
    cuir, la post, la biga i la cadena) o tot. El que es mou és `manxa_fol`."""
    hx, hz, ang, Lm, Wm = MANXA
    L = _local((hx, hz), ang)
    w2 = Wm / 2
    ub, uc = Lm / 2, Lm + 2
    alt = 36 - 30 * p                                     # l'alçada de la falca al fons (oberta, 36)
    if part != 'fol':
        # el cavallet: dues potes en A i el travesser
        for u in (18, Lm - 16):
            cx, _, cz = L(u, 0, 0)
            e.caixa_girada('manxa', cx, cz, 7, Wm + 14, 30, ang, PLANKF, 2.6,
                           cares={'dalt': {'ramp': PLANKF, 'lvl': 3.8}, 'davant': {'ramp': PLANKF, 'lvl': 2.4}})
        cx, _, cz = L(ub, 0, 0)
        e.caixa_girada('manxa', cx, cz, Lm + 4, Wm + 8, 5, ang, PLANKF, 3.4, y0=30,
                       cares={'dalt': {'ramp': PLANKF, 'lvl': 4.0}})
    if part != 'fix':
        # el cuir: els dos costats (falques amb els plecs) i el darrere (el fons de l'acordió)
        top = lambda u: 38 + alt * u / Lm                                                   # noqa: E731
        pleat = lambda s, t, P, hgt: (2.6 + (1.4 if ((hgt - t) / max(1.0, hgt) * 5) % 1 < 0.35 else -0.2)  # noqa: E731
                                      - (1.0 if ((hgt - t) / max(1.0, hgt) * 5) % 1 > 0.88 else 0))
        H0 = 38 + alt + 2
        for w in sorted((-w2, w2), key=lambda w: -math.dist(L(ub, 50, w), CAM.pos)):
            e.quad('manxa_fol', L(0, H0, w), L(Lm, H0, w), L(Lm, 35, w), L(0, 35, w), ramp=PPELL, dues_cares=True,
                   lvl=lambda s, t, P: pleat(s, t - (H0 - top(s)), P, top(s) - 35),
                   forma=lambda s, t: t >= H0 - top(s) - 0.5)
        e.quad('manxa_fol', L(Lm, H0 - 2, -w2), L(Lm, H0 - 2, w2), L(Lm, 35, w2), L(Lm, 35, -w2), ramp=PPELL,
               dues_cares=True,
               lvl=lambda s, t, P: 2.4 + (1.4 if (t / max(1.0, alt + 3) * 5) % 1 < 0.35 else -0.4) - abs(s - w2) / w2 * 0.6)
        # la post de dalt, inclinada, amb dos cèrcols de ferro
        e.quad('manxa_fol', L(-4, 40, -w2 - 3), L(uc, 41 + alt, -w2 - 3), L(uc, 41 + alt, w2 + 3), L(-4, 40, w2 + 3),
               ramp=PLANKF, dues_cares=True,
               lvl=lambda s, t, P: 3.8 - (1.4 if s % 18 < 1.2 else 0) + (1.4 if abs(s - 40) < 3 or abs(s - 78) < 3 else 0))
    if part != 'fol':
        # el broc, de ferro
        e.tub('manxa', L(-14, 39, 0), L(2, 39, 0), 5, IRONF, 3.2)
        # el pal de la palanca
        px, _, pz = L(Lm + 14, 0, w2 + 20)
        e.caixa('manxa', px - 3, px + 3, 0, 150, pz - 3, pz + 3, PLANKF, 3.0,
                cares={'davant': {'ramp': PLANKF, 'lvl': lambda s, t, P: 3.2 - (0.8 if t % 40 < 2 else 0)}})
        e.caixa('manxa', px - 7, px + 7, 0, 7, pz - 7, pz + 7, PLANKF, 2.6)
    if part != 'fix':
        # la biga (de l'extrem del fol cap enlaire), la barra i la cadena amb el mànec
        A, Pv, B, F = _palanca(p)
        e.cable('manxa_fol', [A, Pv, B], PLANKF, 3.8, gruix=5)
        e.cable('manxa_fol', [F, A], IRONF, 3.4, gruix=2)
        e.cable('manxa_fol', [B, (B[0], B[1] - 94, B[2])], IRONF, 4.2, gruix=1.6)
        e.caixa('manxa_fol', B[0] - 9, B[0] + 9, B[1] - 102, B[1] - 98, B[2] - 2, B[2] + 2, PLANKF, 4.2)


# La piquera (el forat del forn per on surt el metall fos, amb el seu broc) i la regata del terra que el porta fins al
# pas, cap a la colada.
PIQUERA = (FORN[1] - 26, 30.0, FZ0)                # on surt el broc, a la façana del forn
REGATA = [(FORN[1] - 26, FZ0 - 18), (660, FZ0 - 22), (744, ZB + 20)]


def _regata_punt(t):
    """Un punt de la regata (x, z), de 0 (sota la piquera) a 1 (al pas), per trams iguals de llargada."""
    seg = list(zip(REGATA, REGATA[1:]))
    ll = [math.dist(a, b) for a, b in seg]
    d = t * sum(ll)
    for (a, b), l in zip(seg, ll):
        if d <= l:
            return a[0] + (b[0] - a[0]) * d / l, a[1] + (b[1] - a[1]) * d / l
        d -= l
    return REGATA[-1]


def piquera(e):
    """El broc de la piquera, el tap de fang i la regata del terra (una canal estreta amb les vores de ferro)."""
    x, y, z = PIQUERA
    e.caixa('piquera', x - 9, x + 9, y - 6, y + 8, z - 4, z, IRONF, 2.6)
    e.quad('piquera', (x - 5, y + 1, z - 4), (x + 5, y + 1, z - 4), (x + 4, y - 3, z - 20), (x - 4, y - 3, z - 20),
           ramp=IRONF, lvl=3.4, dues_cares=True)
    e.tub('piquera', (x, y + 2, z - 1), (x, y + 2, z - 5), 3, COAL, 1.4)                   # el tap
    for (ax, az), (bx, bz) in zip(REGATA, REGATA[1:]):
        dx, dz = bx - ax, bz - az
        n = math.hypot(dx, dz)
        px, pz = -dz / n * 6, dx / n * 6
        e.quad('regata', (ax - px, 0.3, az - pz), (bx - px, 0.3, bz - pz), (bx + px, 0.3, bz + pz),
               (ax + px, 0.3, az + pz), ramp=SLAGF, lvl=lambda s, t, P: 0.6 + (1.6 if t < 1.6 or t > 10.4 else 0))
    e.foscor('regata', (x - 12, 0.4, z - 22), (x + 12, 0.4, z - 22), (x + 12, 0.4, z - 10), (x - 12, 0.4, z - 10),
             lambda s, t: 0.5)


def termometre(e, fire):
    x, z = COL1
    # el capil·lar: de l'esfera, columna avall i pel terra fins al costat del forn
    e.cable('capil', [(x - 2, DIAL_Y - 12, z - 10), (x - 2, 4, z - 10), (x + 30, 1.2, z + 10),
                      (FORN[0] - 30, 1.2, FZ0 + 30), (FORN[0], 30, FZ0 + 30)], IRONF, 2.6, gruix=1.4)
    img, peu = _dial(fire)
    e.sprite('termometre', img, peu, (x, DIAL_Y, z - 12), escala_img=1.4)


def rascle(e):
    x, z = COL2
    foot, top = (x - 56, 2, z - 30), (x - 6, 168, z - 10)
    # (més clar que la columna: de fosc sobre fosc no es veia, i les tenalles de terra hi robaven l'ull)
    e.cable('rascle', [foot, top], IRONF, 6.0, gruix=3.6)
    e.cable('rascle', [(top[0], top[1] - 2, top[2]), (top[0] + 1, top[1] + 24, top[2] + 1)], PLANKF, 6.4, gruix=4.4)
    a = 0.5
    e.quad('rascle', (foot[0] - 15 * math.cos(a), 12, foot[2] + 15 * math.sin(a)),
           (foot[0] + 15 * math.cos(a), 12, foot[2] - 15 * math.sin(a)),
           (foot[0] + 15 * math.cos(a), 0.6, foot[2] - 15 * math.sin(a)),
           (foot[0] - 15 * math.cos(a), 0.6, foot[2] + 15 * math.sin(a)), ramp=IRONF, dues_cares=True,
           lvl=lambda s, t, P: 5.4 - t * 0.08 + (fbm(s / 4, t / 4, 5) - 0.5))


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


# ─── La brossa de la foneria (també la fa servir la colada) ───────────────────

def lingots(e, sid, cx, cz, ang, files=4, capes=3, ombra=True):
    """Una pila de lingots de ferro colat damunt un palet, en capes creuades (cada capa girada 90°), amb la seva
    ombra. Cada lingot: 30 × 9 × 7, amb els cantons de dalt bisellats (la cara de dalt, més clara)."""
    L = _local((cx, cz), ang)
    if ombra:
        e.foscor(f'ombra_{sid}', L(-38, 0.6, -34), L(38, 0.6, -34), L(38, 0.6, 34), L(-38, 0.6, 34),
                 lambda s, t: 0.6 * max(0.0, 1 - ((s - 38) / 40) ** 2 - ((t - 34) / 36) ** 2) * 1.5)
    for u in (-24, 0, 24):                                                                # el palet
        x, _, z = L(u, 0, 0)
        e.caixa_girada(sid, x, z, 8, 40, 5, ang, PLANKF, 2.2)
    e.caixa_girada(sid, cx, cz, 58, 42, 3, ang, PLANKF, 4.2, y0=5,
                   cares={'dalt': {'ramp': PLANKF, 'lvl': lambda s, t, P: 4.6 - (1.6 if s % 11 < 1.4 else 0)}})
    lv = {'dalt': {'ramp': IRONF, 'lvl': lambda s, t, P: 6.0 + (fbm(s / 3, t / 3, 13) - 0.5) * 1.4
                   - (1.6 if s < 1.2 or t < 1.2 else 0)},
          'davant': {'ramp': RUSTF, 'lvl': lambda s, t, P: 3.6 - t * 0.12 + (fbm(s / 3, t / 2, 14) - 0.5) * 1.2},
          'dreta': {'ramp': IRONF, 'lvl': 3.0}, 'esquerra': {'ramp': IRONF, 'lvl': 4.4}, 'darrere': {'ramp': IRONF, 'lvl': 3.0}}
    for k in range(capes):
        y = 8 + k * 7
        n = files - (1 if k == capes - 1 and capes > 2 else 0)
        for i in range(n):
            off = (i - (n - 1) / 2) * 11
            if k % 2 == 0:                                                                # al llarg
                x, _, z = L(0, 0, off)
                e.caixa_girada(sid, x, z, 44, 9, 7, ang, IRONF, 3.0, y0=y, cares=lv)
            else:                                                                         # creuats
                x, _, z = L(off * 1.3, 0, 0)
                e.caixa_girada(sid, x, z, 9, 36, 7, ang, IRONF, 3.0, y0=y, cares=lv)


def lingoteres(e, sid, cx, cz, ang, n=3, ple=0):
    """Una filera de lingoteres (els motlles oberts dels lingots, de ferro) a terra, una al costat de l'altra; les
    `ple` primeres, amb un lingot refredat a dins."""
    L = _local((cx, cz), ang)
    e.foscor(f'ombra_{sid}', L(-n * 19 - 6, 0.6, -18), L(n * 19 + 6, 0.6, -18), L(n * 19 + 6, 0.6, 18),
             L(-n * 19 - 6, 0.6, 18), lambda s, t: 0.5 * min(1.0, min(s, t, 2 * n * 19 + 12 - s, 36 - t) / 8))
    for i in range(n):
        x, _, z = L((i - (n - 1) / 2) * 38, 0, 0)
        dins = (lambda s, t: 3 < s < 31 and 3 < t < 15)
        e.caixa_girada(sid, x, z, 34, 18, 8, ang, IRONF, 2.8,
                       cares={'dalt': {'ramp': IRONF, 'lvl': lambda s, t, P, d=dins: (0.8 + t * 0.06) if d(s, t)
                                       else 3.8 + (fbm(s / 3, t / 3, 17 + i) - 0.5)},
                              'davant': {'ramp': RUSTF, 'lvl': lambda s, t, P: 2.6 + (fbm(s / 4, t / 2, 19) - 0.5) * 1.6},
                              'dreta': {'ramp': IRONF, 'lvl': 2.0}, 'esquerra': {'ramp': IRONF, 'lvl': 3.0}})
        if i < ple:
            e.caixa_girada(sid, x, z, 26, 10, 3, ang, IRONF, 4.0, y0=5.5,
                           cares={'dalt': {'ramp': IRONF, 'lvl': lambda s, t, P: 4.6 - (1.2 if s < 1 or t < 1 else 0)}})


def escoria(e, sid, x, z, r, seed=1, llum_dir=(-0.6, -0.6)):
    """Un munt d'escòria (la crosta que es treu del metall fos): un bony negre i vidriat amb trossos al voltant."""
    e.foscor(f'ombra_{sid}', (x - r * 1.6, 0.6, z + r), (x + r * 1.6, 0.6, z + r), (x + r * 1.6, 0.6, z - r * 1.3),
             (x - r * 1.6, 0.6, z - r * 1.3),
             lambda s, t: 0.55 * max(0.0, 1 - ((s - r * 1.6) / (r * 1.6)) ** 2 - ((t - r) / (r * 1.15)) ** 2) * 1.5)
    e.roca(sid, (x, 0, z), r, SLAGF, 2.9, llum_dir=llum_dir, aplana=0.55, seed=seed)
    for k in range(5):
        a = hr(k, seed, 7) * 6.28
        d = r * (0.95 + hr(k, seed, 8) * 0.6)
        e.roca(sid, (x + math.cos(a) * d * 1.3, 0, z + math.sin(a) * d * 0.8), r * (0.16 + hr(k, seed, 9) * 0.14),
               SLAGF if k % 2 else RUSTF, 3.2, llum_dir=llum_dir, aplana=0.6, seed=seed * 10 + k)


def tenalles(e, sid, x, z, ang, llarg=90):
    """Unes tenalles de foneria (o una espumadora), llargues, estirades a terra."""
    L = _local((x, z), ang)
    for w in (-2.5, 2.5):
        e.cable(sid, [L(-llarg / 2, 1.2, w), L(llarg / 2 - 16, 1.6, w * 0.6), L(llarg / 2, 2.2, w * 3.2)], IRONF, 5.0,
                gruix=1.8)


def carretilla(e, sid, cx, cz, a, carrega=None):
    """Una carretilla de foneria de ferro, girada, amb la roda i els mànecs; `carrega`: fn(e, Lo) que hi posa coses."""
    L = _local((cx, cz), a)
    e.foscor(f'ombra_{sid}', L(-36, 0.6, -24), L(36, 0.6, -24), L(36, 0.6, 24), L(-36, 0.6, 24),
             lambda s, t: 0.55 * max(0.0, 1 - ((s - 36) / 36) ** 2 - ((t - 24) / 24) ** 2) * 1.5)
    e.caixa_girada(sid, cx, cz, 50, 32, 16, a, IRONF, 2.8, y0=14,
                   cares={'dalt': {'ramp': COB, 'lvl': lambda s, t, P: 1.0 if 3 < s < 47 and 3 < t < 29 else 4.4},
                          'davant': {'ramp': IRONF, 'lvl': lambda s, t, P: 3.2 - t * 0.08},
                          'dreta': {'ramp': IRONF, 'lvl': 2.2}, 'esquerra': {'ramp': IRONF, 'lvl': 3.6}})
    e.quad(sid, L(-34, 16, 0), L(-18, 16, 0), L(-18, 0, 0), L(-34, 0, 0), ramp=RUSTF, dues_cares=True,
           lvl=lambda s, t, P: 2.4 + (1.4 if math.hypot(s - 8, t - 8) > 5.6 else -0.6),
           forma=lambda s, t: math.hypot(s - 8, t - 8) <= 8)                               # la roda
    for w in (-12, 12):                                                                   # els mànecs
        e.cable(sid, [L(22, 28, w), L(56, 22, w * 1.1), L(58, 0, w * 1.1)], PLANKF, 3.6, gruix=2.2)
    if carrega:
        carrega(e, L)


def bido(e, sid, x, z, r=17, h=44):
    """Un bidó d'aigua per refredar les eines: el cos amb els cèrcols, l'aigua negra a dins (amb el reflex) i una
    cullera de colada recolzada a la vora."""
    e.foscor(f'ombra_{sid}', (x - r * 2, 0.6, z + r * 1.4), (x + r * 2, 0.6, z + r * 1.4), (x + r * 2, 0.6, z - r * 2),
             (x - r * 2, 0.6, z - r * 2),
             lambda s, t: 0.6 * max(0.0, 1 - ((s - r * 2) / (r * 2)) ** 2 - ((t - r * 1.7) / (r * 1.7)) ** 2) * 1.5)
    cilindre(e, sid, x, z, r, 0, h, RUSTF, lambda a, y, P: 3.4 - math.cos(a - 2.2) * 1.4
             + (1.2 if abs(y - 8) < 2 or abs(y - h + 6) < 2 else 0) + (fbm(a * 4, y / 6, 23) - 0.5) * 1.2, n=16)
    e.quad(sid, (x - r, h, z + r), (x + r, h, z + r), (x + r, h, z - r), (x - r, h, z - r), ramp=IRONF,
           lvl=lambda s, t, P: 4.6 if math.hypot(s - r, t - r) > r - 1.6 else
           (1.2 + (2.6 if abs(s - r * 0.7 - (t - r) * 0.4) < 2 else 0)),
           forma=lambda s, t: math.hypot(s - r, t - r) <= r)
    e.cable(sid, [(x + 4, h - 6, z + 2), (x + r + 6, h + 26, z - 10), (x + r + 30, 0.5, z - 30)], PLANKF, 4.0,
            gruix=2.2)                                                                    # el mànec de la cullera


def enclusa(e, sid, x, z, ang):
    """Una enclusa damunt una soca (per al primer pla, fosca)."""
    cilindre(e, sid, x, z, 20, 0, 34, PLANKF, lambda a_, y, P: 1.4 - math.cos(a_ - 2.3) * 0.6
             + (0.6 if y % 9 < 1 else 0), n=14)
    e.caixa_girada(sid, x, z, 22, 16, 10, ang, IRONF, 1.6, y0=34)
    e.caixa_girada(sid, x, z, 44, 18, 9, ang, IRONF, 1.4, y0=44,
                   cares={'dalt': {'ramp': IRONF, 'lvl': 2.6}, 'davant': {'ramp': IRONF, 'lvl': 1.0}})
    L = _local((x, z), ang)
    tx, _, tz = L(30, 0, 0)
    e.caixa_girada(sid, tx, tz, 16, 10, 6, ang, IRONF, 1.4, y0=47,
                   cares={'dalt': {'ramp': IRONF, 'lvl': 2.2}})                            # la banya


def brossa(e):
    """El que omple el terra de la nau: la pila de lingots, l'escòria amb les tenalles i les lingoteres."""
    escoria(e, 'escoria', *ESCORIA, seed=3)
    tenalles(e, 'tenalles', ESCORIA[0] - 46, ESCORIA[1] - 30, 0.5, llarg=100)
    lingots(e, 'lingots', *LINGOTS, files=4, capes=4)
    bido(e, 'bido', *BIDO)
    lingoteres(e, 'lingoteres', *LINGOTERES, n=4, ple=2)


def primer_pla(e):
    """Fosc i tallat per la vora: les caixes de motlles de la dreta, la cadena del polispast, el munt de carbó i
    l'enclusa."""
    enclusa(e, 'primer_pla', *ENCLUSA)
    for (cx, cz, w, d, h, ang, y0) in ((640, 420, 96, 60, 44, 0.32, 0), (700, 470, 80, 56, 40, -0.2, 0),
                                       (650, 424, 70, 46, 30, 0.5, 44)):
        e.caixa_girada('primer_pla', cx, cz, w, d, h, ang, PLANKF, 1.4, y0=y0,
                       cares={'dalt': {'ramp': PLANKF, 'lvl': lambda s, t, P: 2.2 - (1.2 if s % 16 < 1.4 else 0)},
                              'davant': {'ramp': PLANKF, 'lvl': lambda s, t, P: 1.2 - (0.8 if t % 11 < 1.2 else 0)
                                         + (1.0 if s < 3 else 0)},
                              'esquerra': {'ramp': PLANKF, 'lvl': 0.8}, 'dreta': {'ramp': PLANKF, 'lvl': 0.6}})
    # (el polispast es gronxa: és la capa `polispast`)
    for (x, z, r, seed) in ((150, 384, 52, 3), (70, 420, 38, 5), (236, 380, 22, 7)):
        e.roca('primer_pla', (x, 0, z), r, COAL, 1.6, llum_dir=(-0.6, -0.6), seed=seed)


def polispast(e, ph=0.0):
    """El polispast del primer pla: els dos ramals de la cadena, el bossell i el ganxo, que es gronxen (`ph`, de 0 a
    1: el cicle) del sostre."""
    hx, hz = 430, 330
    a = math.sin(2 * math.pi * ph) * 0.035               # radians
    top = HW + 30
    G = lambda x, y: (hx + (x - hx) + (top - y) * math.sin(a), y + (top - y) * (1 - math.cos(a)), hz)   # noqa: E731
    for dx in (-6, 6):
        e.cable('polispast', [(hx + dx, top, hz), G(hx + dx * 0.5, 156)], IRONF, 2.0, gruix=2.4)
    bx = G(hx, 152)[0] - hx
    e.caixa('polispast', hx - 5 + bx, hx + 5 + bx, 146, 158, hz - 3, hz + 3, IRONF, 3.4,
            cares={'davant': {'ramp': IRONF, 'lvl': lambda s, t, P: 3.2 + (1.6 if 4 < t < 7 else 0)}})
    e.cable('polispast', [G(hx, 144), G(hx, 130), G(hx - 6, 122), G(hx, 116), G(hx + 5, 120)], IRONF, 2.8, gruix=2.6)


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


def escena(cv, fire=0, foc=False, sense_fol=False, sense_rascle=False):
    """Tota la sala, de lluny a prop; `fire`: el dibuix del forn (0, 1, 2); `foc`: la llum del foc al món;
    `sense_fol`: sense el que es mou de la manxa (el fons que queda darrere quan es mou); `sense_rascle`: sense el
    rascle de la columna (el que queda darrere quan el porta la Vet)."""
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
    piquera(e)
    manxa(e, part='fix' if sense_fol else None)
    e.darrere = len(e.ids)                       # (el que es pinta d'aquí endavant pot tapar la manxa)
    columna(e, 'columna_dreta', *COL2)
    if not sense_rascle:
        rascle(e)
    columna(e, 'columna_esq', *COL1)
    termometre(e, fire)
    metall(e)
    brossa(e)
    primer_pla(e)
    return e


# ─── Composició ────────────────────────────────────────────────────────────

def _negre(cv):
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)      # la barra de verbs: negre


@functools.lru_cache(maxsize=None)
def _escena(fire, foc, sense_fol=False, sense_rascle=False):
    cv = Canvas(light=LIGHT)
    e = escena(cv, fire, foc, sense_fol, sense_rascle)
    _negre(cv)
    return cv.img, e


@functools.lru_cache(maxsize=None)
def _base(fire=0, sense_fol=False, sense_rascle=False):
    """La sala amb el forn en l'estat `fire`: sense foc, tal qual; amb foc, la llum del foc tenyida de taronja."""
    img, e = _escena(fire, False, sense_fol, sense_rascle)
    if not fire:
        return img, e
    lit, _ = _escena(fire, True, sense_fol, sense_rascle)
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


# ─── La manxa que bufa (la capa `manxa_mou`) ────────────────────────────────
# Cada fotograma: el fons que queda darrere el que es mou de la manxa (la sala dibuixada sense, amb el foc que toca),
# on hi havia el fol, i a sobre el fol, la post, la biga i la cadena a la posició del moment; retallat on el tapa el
# que hi ha davant (la columna, el rascle...). Va just per sobre de la capa del davant de la manxa.

@functools.lru_cache(maxsize=None)
def _zones():
    """→ (on es veia el que es mou de la manxa, el que hi ha davant la manxa), màscares de la sala."""
    _, e = _base(0)
    amo = np.frombuffer(e.amo, np.uint16).reshape(H, W)
    fol = np.isin(amo, [i for i, sid in enumerate(e.ids) if sid == 'manxa_fol'])
    return fol, amo >= e.darrere


def _fol_img(p, fire):
    def pinta(llums):
        cv = Canvas(light=LIGHT, transparent=True)
        manxa(Escena(cv, CAM, llums, ambient=AMBIENT), p, part='fol')
        return cv.img
    img = pinta(LLUMS)
    if fire:
        a = np.asarray(pinta(LLUMS + [FOC[fire]])).astype(np.float32)
        b = np.asarray(img).astype(np.float32)
        dl = np.clip((a[..., :3] - b[..., :3]).mean(axis=2, keepdims=True), 0, None)
        out = np.clip(b[..., :3] + dl * np.array(TARONJA[fire], np.float32) * 1.6, 0, 255)
        img = Image.fromarray(np.concatenate([out, b[..., 3:]], axis=2).astype(np.uint8), 'RGBA').copy()
    return img


def _guspirada(cv, k0, n, f, forca=1.0):
    """Una esbufegada de guspires que surten de la boca (el fotograma `f` d'una de `n`)."""
    for k in range(int(26 * forca)):
        s = (f / n) * (0.8 + hr(k, k0, 1) * 0.6)
        if s <= 0 or s > 0.95:
            continue
        P0 = (FCX + (hr(k, k0, 4) - 0.5) * 60, 30 + hr(k, k0, 6) * 40, FZ0 - 4)
        v = ((hr(k, k0, 2) - 0.5) * 200, 90 + hr(k, k0, 3) * 110, -120 - hr(k, k0, 5) * 160)
        P = (P0[0] + v[0] * s, P0[1] + v[1] * s - 260 * s * s, P0[2] + v[2] * s)
        if P[1] < 0:
            continue
        u, vv, _ = CAM.projecta(P)
        if 0 <= u < W and 0 <= vv < BOTTOM:
            cv.flat(u, vv, FIREF[6] if s < 0.3 else FIREF[5] if s < 0.6 else FIREF[3])


def _frames_manxa(fire):
    """Dues manxades: el fol es tanca (bufa: guspires per la boca) i es torna a obrir."""
    fol, davant = _zones()
    fons = np.asarray(_base(fire, True)[0])
    ps = [0.0]
    for _ in range(2):
        ps += [_ease(t / 6) for t in range(1, 7)] + [1 - _ease(t / 5) for t in range(1, 6)]
    out = []
    for f, p in enumerate(ps):
        a = np.zeros((H, W, 4), np.uint8)
        a[fol] = fons[fol]
        img = Image.fromarray(a, 'RGBA').copy()
        img.alpha_composite(_fol_img(p, fire))
        a = np.asarray(img).copy()
        a[davant] = 0
        img = Image.fromarray(a, 'RGBA').copy()
        bufa = f - 1 if f < 12 else f - 12
        if 0 <= bufa < 9:
            _guspirada(Canvas(img=img), f // 12, 9, bufa + 1, 0.8 if fire == 1 else 1.0)
        out.append(img)
    return out


def _ease(t):
    return t * t * (3 - 2 * t)


# ─── El que passa a la boca i a la piquera (la capa `forn_accio`) ───────────

def _flat(cv, P, col):
    u, v, _ = CAM.projecta(P)
    if 0 <= u < W and 0 <= v < BOTTOM:
        cv.flat(u, v, col)


def _bola(cv, P, r, ramp, lvl):
    """Una boleta (un comptador, un tros d'escòria) al món, de radi `r`, ombrejada."""
    u, v, _ = CAM.projecta(P)
    rr = max(0.8, r * CAM.escala(P))
    for Y in range(int(v - rr), int(v + rr) + 1):
        for X in range(int(u - rr), int(u + rr) + 1):
            dx, dy = (X - u) / rr, (Y - v) / rr
            if dx * dx + dy * dy <= 1 and 0 <= X < W and 0 <= Y < BOTTOM:
                cv.put(X, Y, ramp, lvl - dx * 0.8 - dy * 1.0, lit=0)


def _frames_metall():
    """Els comptadors volen de les mans de la Vet (al costat de la boca) cap dins el forn, i el foc esbufega."""
    n = 18
    out = []
    for f in range(n):
        cv = Canvas(transparent=True)
        for k in range(7):
            t = (f - k * 1.4) / 6
            if not 0 <= t <= 1:
                continue
            A = (FORN[1] - 30 + hr(k, 1, 7) * 10, 54, FZ0 - 44)
            B = (FCX + (hr(k, 2, 7) - 0.5) * 50, 30 + hr(k, 3, 7) * 20, FZ0 + 8)
            P = (A[0] + (B[0] - A[0]) * t, A[1] + (B[1] - A[1]) * t + 40 * t * (1 - t), A[2] + (B[2] - A[2]) * t)
            _bola(cv, P, 4.6, [(60, 64, 70), (110, 116, 124), (160, 166, 172), (210, 214, 220), (240, 240, 236)],
                  3.0 + (0.6 if (f + k) % 2 else 0))
        if f >= 8:
            _guspirada(cv, 7, n - 8, f - 7, 1.0)
        out.append(cv.img)
    out.append(Image.new('RGBA', (W, H), (0, 0, 0, 0)))
    return out


# El rascle a les mans: qui treu l'escòria (la Vet o l'Iri, amb el gest `Fa` mirant a l'esquerra) és al punt de
# `forn` de la GEOMETRIA, i té les mans a (−20, −52) px dels peus del sprite; a la seva fondària, 1 px del sprite és
# 1 unitat del món (l'escala del personatge és la de la càmera). El pal hi passa per dins (les mans tapen el tros on
# l'agafen: la capa va per sota dels personatges) i la pala entra a la boca i en surt.
MANS = (FORN[1] - 14 - 20, 52.0, FZ0 - 44)
RASCLE_L = 130.0                                   # la llargada del pal, de la pala al puny
PALA_DINS, PALA_FORA = (FCX + 6, 12.0, FZ0 + 22), (FCX + 10, 1.0, FZ0 - 30)


def _rascle_ma(e, pala, davant=False):
    """El rascle amb la pala a `pala` i el pal passant per les mans. Amb `davant`, només el que és davant la façana
    del forn (el que és a dins, la boca el retalla)."""
    d = [MANS[i] - pala[i] for i in range(3)]
    n = math.sqrt(sum(c * c for c in d))
    u = [c / n for c in d]
    cul = tuple(pala[i] + u[i] * RASCLE_L for i in range(3))
    puny = tuple(pala[i] + u[i] * (RASCLE_L - 22) for i in range(3))
    A = pala
    if davant and pala[2] > FZ0:                   # el pal, des d'on travessa la façana
        t = (pala[2] - FZ0) / (pala[2] - cul[2])
        A = tuple(pala[i] + (cul[i] - pala[i]) * t for i in range(3))
    e.cable('rascle', [(A[0], A[1] + 5, A[2]), (puny[0], puny[1] + 5, puny[2])], IRONF, 4.6, gruix=3.4)
    e.cable('rascle', [(puny[0], puny[1] + 5, puny[2]), (cul[0], cul[1] + 5, cul[2])], PLANKF, 4.4, gruix=4.0)
    if davant and pala[2] > FZ0 - 4:
        return
    # la pala: una planxa dreta, de través al pal
    h = math.hypot(u[0], u[2])
    px, pz = -u[2] / h * 14, u[0] / h * 14
    x, y, z = pala
    e.quad('rascle', (x - px, y + 10, z - pz), (x + px, y + 10, z + pz), (x + px, y, z + pz), (x - px, y, z - pz),
           ramp=IRONF, dues_cares=True, lvl=lambda s, t, P: 3.0 - t * 0.08 + (fbm(s / 4, t / 4, 5) - 0.5))


@functools.lru_cache(maxsize=None)
def _boca_mask():
    """La boca del forn a la pantalla (on es veu el que hi ha a dins)."""
    from PIL import ImageDraw
    m = Image.new('L', (W, H), 0)
    pts = [CAM.projecta((FCX + dx, y, FZ0))[:2] for dx, y in ((-36, 11), (36, 11), (36, 64), (0, 86), (-36, 64))]
    ImageDraw.Draw(m).polygon(pts, fill=255)
    return m


def _amb_foc(draw, fire=2):
    """Pinta `draw(e)` amb la llum de la sala i la del foc tenyida de taronja (com el fons)."""
    def pinta(llums):
        cv = Canvas(light=LIGHT, transparent=True)
        draw(Escena(cv, CAM, llums, ambient=AMBIENT))
        return cv.img
    img = pinta(LLUMS)
    a = np.asarray(pinta(LLUMS + [FOC[fire]])).astype(np.float32)
    b = np.asarray(img).astype(np.float32)
    dl = np.clip((a[..., :3] - b[..., :3]).mean(axis=2, keepdims=True), 0, None)
    out = np.clip(b[..., :3] + dl * np.array(TARONJA[fire], np.float32) * 1.6, 0, 255)
    return Image.fromarray(np.concatenate([out, b[..., 3:]], axis=2).astype(np.uint8), 'RGBA').copy()


def _rascle_img(pala):
    """El rascle a les mans, amb la pala a `pala`: el que és dins el forn, només per la boca."""
    tot = _amb_foc(lambda e: _rascle_ma(e, pala))
    dins = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    dins.paste(tot, (0, 0), _boca_mask())
    dins.alpha_composite(_amb_foc(lambda e: _rascle_ma(e, pala, davant=True)))
    return dins


def _frames_escoria():
    """La Vet treu l'escòria amb el rascle: el fica a la boca i l'estira, i els trossos grisos surten de la boca i
    cauen davant, amb fum; després el rascle es queda a terra, davant el forn, fins que la Vet el torna a deixar."""
    n, d0 = 22, 3                                  # (els trossos surten quan el rascle comença a estirar)
    out = []
    for f in range(n):
        if f < d0:                                 # entra a la boca
            t = _ease((f + 1) / d0)
            pala = tuple(PALA_FORA[i] + (PALA_DINS[i] - PALA_FORA[i]) * (0.4 + 0.6 * t) for i in range(3))
        else:                                      # estira
            t = _ease(min(1.0, (f - d0) / 10))
            pala = tuple(PALA_DINS[i] + (PALA_FORA[i] - PALA_DINS[i]) * t for i in range(3))
        cv = Canvas(img=_rascle_img(pala), transparent=True)
        g = f - d0
        for k in range(5):
            t = min(1.0, max(0.0, (g - k * 2) / 8))
            if g < k * 2:
                continue
            A = (FCX + (hr(k, 1, 8) - 0.5) * 40, 22 + hr(k, 2, 8) * 10, FZ0 + 2)
            B = (FCX + 20 + hr(k, 3, 8) * 60, 2.5, FZ0 - 26 - hr(k, 4, 8) * 30)
            P = (A[0] + (B[0] - A[0]) * t, A[1] + (B[1] - A[1]) * t + 18 * t * (1 - t), A[2] + (B[2] - A[2]) * t)
            calor = max(0.0, 1 - (g - k * 2) / 14)
            _bola(cv, P, 7 + hr(k, 5, 8) * 3, FIREF if calor > 0.5 else SLAGF, 3.4 if calor > 0.5 else 2.6)
        # el fum que en surt
        for k in range(8):
            if g < 0:
                break
            s = (g / n + hr(k, 9, 8)) % 1
            P = (FCX + 30 + (hr(k, 10, 8) - 0.5) * 60 + math.sin(s * 5 + k) * 8, 6 + s * 110, FZ0 - 40)
            u, v, _ = CAM.projecta(P)
            r = (3 + s * 9) * CAM.escala(P)
            for Y in range(int(v - r), int(v + r) + 1):
                for X in range(int(u - r), int(u + r) + 1):
                    if (X - u) ** 2 + (Y - v) ** 2 <= r * r and 0 <= X < W and 0 <= Y < BOTTOM and \
                            B4[Y & 3][X & 3] < 0.55 * (1 - s):
                        cv.flat(X, Y, (96, 90, 86))
        out.append(cv.img)
    return out


def _frames_sense_rascle():
    """La columna sense el rascle (quan el porta la Vet): el fons que hi ha darrere, on es veia el rascle. Només amb el
    forn a tota manxa (`forn_fort`), que és quan es treu l'escòria. Va damunt la capa del davant de la columna."""
    amb, e = _base(2)
    amo = np.frombuffer(e.amo, np.uint16).reshape(H, W)
    zona = np.isin(amo, [i for i, sid in enumerate(e.ids) if sid == 'rascle'])
    sense = np.asarray(_base(2, sense_rascle=True)[0])
    a = np.zeros((H, W, 4), np.uint8)
    a[zona] = sense[zona]
    a[zona, 3] = 255
    return [Image.fromarray(a, 'RGBA')]


def _frames_piquera():
    """La piquera oberta: el raig de metall fos cau del broc a la regata i hi corre fins al pas, amb vapor."""
    x, y, z = PIQUERA
    n = 26
    out = []
    for f in range(n):
        cv = Canvas(transparent=True)
        e = Escena(cv, CAM, [], 0)
        fins = max(0.0, min(1.0, (f - 2) / 18))
        g = min(1.0, f / 3) * (1 - max(0.0, (f - 20) / 6))
        if g > 0:
            e.cable('raig', [(x, y - 3, z - 20), (x + 1, 10, z - 20), (x + 1, 0.6, z - 19)], MOLTEN, 3.6,
                    gruix=1.6 + 3 * g)
        if fins > 0:
            m = max(2, int(fins * 40))
            pts = [_regata_punt(fins * i / (m - 1)) for i in range(m)]
            e.cable('regata', [(px, 0.6, pz) for px, pz in pts], MOLTEN, 3.4, gruix=7)
            cap = _regata_punt(fins)
            for k in range(4):                         # el front, que bull
                _flat(cv, (cap[0] + (hr(f, k, 3) - 0.5) * 8, 2 + hr(f, k, 4) * 5, cap[1]), MOLTEN[5])
        for k in range(10):                            # el vapor que puja de la regata
            s = (f / 8 + hr(k, 1, 9)) % 1
            tt = hr(k, 2, 9) * fins
            px, pz = _regata_punt(tt)
            P = (px + math.sin(s * 6 + k) * 4, 4 + s * 60, pz)
            if fins > 0 and B4[k & 3][f & 3] < 0.7 * (1 - s):
                _flat(cv, P, (150, 120, 100))
        out.append(cv.img)
    return out


# ─── L'ambient: brases i fum al forn apagat, la pols, el termòmetre, el polispast ───

def _frames_brases(n=24):
    """El forn apagat: unes brases a la boca que s'avivem i s'apaguen, i un fil de fum que en surt i puja."""
    out = []
    for f in range(n):
        cv = Canvas(transparent=True)
        for k in range(9):
            P = (FCX - 26 + hr(k, 1, 11) * 52, 12 + hr(k, 2, 11) * 4, FZ0 + 14)
            b = 0.5 + 0.5 * math.sin(2 * math.pi * (f / n * (1 + k % 3) + hr(k, 3, 11)))
            if b > 0.25:
                _flat(cv, P, FIREF[5] if b > 0.85 else FIREF[4] if b > 0.55 else FIREF[3])
        for Y0 in range(0, 140, 2):                    # el fil de fum, que surt per dalt de la boca
            s = Y0 / 140
            ph = f / n
            P = (FCX + math.sin(s * 5 - ph * 2 * math.pi) * (4 + s * 14) + s * 20, 86 + Y0, FZ0 - 6)
            u, v, _ = CAM.projecta(P)
            if B4[int(v) & 3][int(u) & 3] < 0.6 * (1 - s) and 0 <= u < W and 0 <= v < BOTTOM:
                cv.flat(u, v, (92, 86, 82))
                if s < 0.5:
                    cv.flat(u + 1, v, (80, 76, 72))
        out.append(cv.img)
    return out


FONS = {'', 'sostre', 'paret_esq', 'paret_fons', 'terra', 'pas', 'pas_terra', 'racons', 'dalt', 'dalt_esq'}


def _frames_pols(n=32):
    """La pols que sura dins els feixos de llum dels finestrals."""
    _, e = _base(0)
    amo = np.frombuffer(e.amo, np.uint16).reshape(H, W)
    fons = np.isin(amo, [i for i, sid in enumerate(e.ids) if sid in FONS])
    out = []
    for f in range(n):
        cv = Canvas(transparent=True)
        ph = f / n
        for q, wx in enumerate(WINDOWS):
            a0, a1 = wx * KW, (wx + 28) * KW
            P0, P1, P2, P3 = (a0, 262, ZB - 2), (a1, 262, ZB - 2), (a1 + 70, 0, ZB - 330), (a0 + 70, 0, ZB - 330)
            for k in range(30):
                s = (hr(k, q, 71) + 0.05 * math.sin(2 * math.pi * (ph + hr(k, q, 73)))) % 1
                t = (hr(k, q, 72) + ph * (0.3 + hr(k, q, 74) * 0.3)) % 1
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


def _frames_termometre(fire, temp, n=10):
    """El termòmetre amb l'agulla a `temp` (damunt la capa del davant de la columna). Amb el forn encès (`fire`),
    l'agulla tremola; apagat, un sol fotograma."""
    x, z = COL1
    lit = np.asarray(_base(fire)[0]).astype(np.float32)
    fosc = np.asarray(_base(0)[0]).astype(np.float32)
    k = np.clip(lit[..., :3] / np.maximum(fosc[..., :3], 1), 0.5, 4)
    # Dins l'esfera, la llum d'un sol color (la mediana): els fons tenen l'agulla a llocs diferents, i el quocient
    # píxel a píxel hi deixaria el rastre de les dues agulles.
    yy, xx = np.mgrid[:k.shape[0], :k.shape[1]]
    esfera = (xx - _DIAL[0]) ** 2 + (yy - _DIAL[1]) ** 2 <= (_DR + 1) ** 2
    k[esfera] = np.median(k[esfera], axis=0)
    out = []
    for f in range(n if fire else 1):
        cv = Canvas(light=LIGHT, transparent=True)
        img, peu = _dial(fire, (0.012 * math.sin(2 * math.pi * f / n * 3) + (0.02 if f in (3, 7) else 0)) if fire else 0.0,
                         temp)
        Escena(cv, CAM, LLUMS, ambient=AMBIENT).sprite('termometre', img, peu, (x, DIAL_Y, z - 12), escala_img=1.4)
        a = np.asarray(cv.img).astype(np.float32)
        a[..., :3] = np.clip(a[..., :3] * k, 0, 255)
        out.append(Image.fromarray(a.astype(np.uint8), 'RGBA').copy())
    return out


def _frames_polispast(n=24):
    out = []
    for f in range(n):
        cv = Canvas(light=LIGHT, transparent=True)
        polispast(Escena(cv, CAM, LLUMS, ambient=AMBIENT), f / n)
        out.append(cv.img)
    return out


BUIT = lambda: [Image.new('RGBA', (W, H), (0, 0, 0, 0))]   # noqa: E731

# El termòmetre de la colada marca la temperatura (de 1 a 9: comença a 8 i la manxa la puja fins a 9; a 0 es torna a
# començar). Una capa per grau: `termo_fred_<t>`, amb el forn apagat (abans de la manxa), i `termo_<t>`, encès.
TEMPS = range(1, 10)
TERMO = [f'termo_fred_{t}' for t in TEMPS] + [f'termo_{t}' for t in TEMPS]

ANIMS = {'foc': {'frames': lambda: _flames(1), 'frameDuration': 100},
         'foc_fort': {'frames': lambda: _flames(2), 'frameDuration': 80},
         'guspires': {'frames': _frames_guspires, 'frameDuration': 70},
         'brases': {'frames': _frames_brases, 'frameDuration': 140},
         'pols': {'frames': _frames_pols, 'frameDuration': 150},
         'polispast': {'frames': _frames_polispast, 'frameDuration': 160, 'zIndex': 60},
         # la manxa que bufa (les indicacions d'escena de rooms/fosa_forn.json)
         'manxa_mou': {'frames': BUIT, 'frameDuration': 1000, 'loop': False},
         'manxa_bufa': {'frames': lambda: _frames_manxa(1), 'frameDuration': 80, 'loop': False, 'prop': 'manxa_mou'},
         'manxa_bufa_fort': {'frames': lambda: _frames_manxa(2), 'frameDuration': 80, 'loop': False,
                             'prop': 'manxa_mou'},
         # el que passa a la boca i a la piquera
         'forn_accio': {'frames': BUIT, 'frameDuration': 1000, 'loop': False, 'zIndex': 5},
         'metall_entra': {'frames': _frames_metall, 'frameDuration': 70, 'loop': False, 'prop': 'forn_accio'},
         'escoria_fora': {'frames': _frames_escoria, 'frameDuration': 80, 'loop': False, 'prop': 'forn_accio'},
         # el rascle de la columna, que desapareix quan la Vet l'agafa (va damunt la capa del davant de la columna)
         'rascle_fora': {'frames': BUIT, 'frameDuration': 1000, 'loop': False},
         'rascle_agafat': {'frames': _frames_sense_rascle, 'frameDuration': 1000, 'loop': False,
                           'prop': 'rascle_fora'},
         'piquera_raja': {'frames': _frames_piquera, 'frameDuration': 80, 'loop': False, 'prop': 'forn_accio'}}
ANIMS.update({f'termo_fred_{t}': {'frames': functools.partial(_frames_termometre, 0, t), 'frameDuration': 1000}
              for t in TEMPS})
ANIMS.update({f'termo_{t}': {'frames': functools.partial(_frames_termometre, 1, t), 'frameDuration': 120}
              for t in TEMPS})


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


def _peu(cx, cz, ang, L, A, m=0.0):
    """Els quatre cantons de terra (x, z) d'una caixa girada de L × A (amb un marge m)."""
    Lo = _local((cx, cz), ang)
    return [(Lo(u, 0, w)[0], Lo(u, 0, w)[2]) for u, w in ((-L / 2 - m, -A / 2 - m), (L / 2 + m, -A / 2 - m),
                                                         (L / 2 + m, A / 2 + m), (-L / 2 - m, A / 2 + m))]


def _base_girada(cx, cz, ang, L, A):
    """La línia base d'una cosa girada: la del cantó de davant que queda més al fons (el segon més avall)."""
    return round(sorted(_p(x, z)[1] for x, z in _peu(cx, cz, ang, L, A))[-2])


_FOC = ('forn_ences', 'forn_fort')               # (amb el forn encès, cada capa té la seva versió il·luminada)

FRONT = [
    {'id': 'davant_lingots', 'mask': _amo({'lingots'}), 'baseline': _base_girada(*LINGOTS, 58, 42), 'zIndex': 20, 'variants': _FOC},
    {'id': 'davant_bido', 'mask': _amo({'bido'}), 'baseline': _vfront((BIDO[0], BIDO[1] - 12)), 'zIndex': 20, 'variants': _FOC},
    {'id': 'davant_escoria', 'mask': _amo({'escoria'}), 'baseline': _vfront((ESCORIA[0], ESCORIA[1] - ESCORIA[2] * 0.6)),
     'zIndex': 20, 'variants': _FOC},
    {'id': 'davant_manxa', 'mask': _amo({'manxa', 'manxa_fol'}), 'baseline': _vfront(*_MP), 'zIndex': 20,
     'variants': _FOC, 'props': ['manxa_mou']},
    {'id': 'davant_columna_esq', 'mask': _amo({'columna_esq', 'termometre'}),
     'baseline': _vfront((COL1[0], COL1[1] - 13)), 'zIndex': 20, 'variants': _FOC,
     'props': [*TERMO]},
    {'id': 'davant_columna_dreta', 'mask': _amo({'columna_dreta', 'rascle'}),
     'baseline': _vfront((COL2[0], COL2[1] - 13), (COL2[0] - 56, COL2[1] - 30)), 'zIndex': 20, 'variants': _FOC,
     'props': ['rascle_fora']},
    {'id': 'davant_metall', 'mask': _amo({'metall'}),
     'baseline': _vfront((METALL[0], METALL[1] - 10), (CARRET[0] + 30, CARRET[1] - 30)), 'zIndex': 20, 'variants': _FOC},
    {'id': 'davant', 'mask': _amo({'primer_pla', 'lingoteres'}), 'baseline': 999, 'zIndex': 20, 'variants': _FOC},
]

_DIAL = CAM.projecta((COL1[0], DIAL_Y, COL1[1] - 12))
_DR = 15 * 1.4 * CAM.escala((COL1[0], DIAL_Y, COL1[1] - 12))

_TEN = _local((ESCORIA[0] - 46, ESCORIA[1] - 30), 0.5)    # les tenalles de `brossa`

GEOMETRIA = {
    'things': {
        'porta': {'rect': _rect_mon((0, DOOR[2], DOOR[0]), (0, 0, DOOR[1])), 'walk': _p(30, (DOOR[0] + DOOR[1]) / 2)},
        'pas': {'rect': _rect_mon((PAS[0], PAS[2], ZB), (PAS[1], 0, ZB)), 'walk': _p((PAS[0] + PAS[1]) / 2, ZB + 20)},
        'forn': {'rect': _rect_mon((FORN[0], HOOD, ZB - 40), (FORN[1], 0, FZ0)), 'walk': _p(FORN[1] - 14, FZ0 - 44)},
        # El broc de la piquera, a la façana del forn (a sobre de la zona del forn: es clica abans).
        'piquera': {'rect': _rect_mon((PIQUERA[0] - 16, PIQUERA[1] + 16, PIQUERA[2]),
                                      (PIQUERA[0] + 16, 0, PIQUERA[2] - 24)),
                    'walk': _p(FORN[1] - 14, FZ0 - 44)},
        'manxa': {'rect': _rect_mon(*[(x, 0, z) for x, z in _MP], *[(x, 80, z) for x, z in _MP[:2]],
                                    _local(MANXA[:2], MANXA[2])(MANXA[3] + 60, 168, -46),
                                    _local(MANXA[:2], MANXA[2])(MANXA[3] + 60, 60, -46)),
                  'walk': _p(*_local(MANXA[:2], MANXA[2])(MANXA[3] + 40, 0, -40)[::2])},
        'metall': {'rect': _rect_mon((METALL[0] - 70, 60, METALL[1]), (CARRET[0] + 40, 0, CARRET[1] - 40)),
                   'walk': _p(METALL[0] + 60, METALL[1] - 70)},
        # Les tenalles estirades a terra, al costat de l'escòria (es veuen més que el rascle: que diguin alguna cosa).
        'tenalles': {'rect': _rect_mon(_TEN(-52, 0, -6), _TEN(52, 0, 6), _TEN(-52, 10, -6), _TEN(52, 10, 6)),
                     'walk': _p(*_TEN(-10, 0, -40)[::2])},
        'rascle': {'rect': _rect_mon((COL2[0] - 72, 196, COL2[1] - 30), (COL2[0] + 2, 0, COL2[1] - 30)),
                   'walk': _p(COL2[0] - 40, COL2[1] - 70)},
        'termometre': {'rect': (round(_DIAL[0] - _DR - 2), round(_DIAL[1] - _DR - 2), round(_DIAL[0] + _DR + 2),
                                round(_DIAL[1] + _DR + 2)),
                       'walk': _p(COL1[0] + 50, COL1[1] - 60)},
    },
    'spawns': {'iri': _p(380, 500), 'vet': _p(570, 650)},
    'walkable': _WALK,
    'forats': [[_p(x, z) for x, z in _MP], _cercle(*COL1, 22, 8), _cercle(*COL2, 22, 8),
               _cercle(METALL[0], METALL[1], 56, 10), _cercle(CARRET[0], CARRET[1], 40, 8),
               [_p(x, z) for x, z in _peu(*LINGOTS, 58, 42, 8)], _cercle(*BIDO, 26, 8),
               _cercle(ESCORIA[0], ESCORIA[1], ESCORIA[2] * 1.25, 8)],
    # La càmera, a 1,85 m i mirant avall, aixafa el terra: 185 d'alçada a ≈500 de fons (on es camina).
    'floorSquash': 0.4,
    # L'ombra de contacte: la llum dominant és la claror del carrer, per la porta (l'ombra cau cap a la dreta).
    'characterShadow': {'enabled': True, 'color': '#120a08', 'alpha': 0.42, 'squash': 0.4, 'core': 0.6,
                        'light': {'x': _p(10, (DOOR[0] + DOOR[1]) / 2)[0], 'y': _p(10, (DOOR[0] + DOOR[1]) / 2)[1],
                                  'stretch': 0.8, 'reach': 160}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    # La llum de la sala sobre els personatges (characterLights del motor): la fosa, fosca i de sutge: els finestrals,
    # la claror del carrer per la porta i el forn quan crema.
    'characterLights': {
        'ambient': '#645a54',
        'lights': [
            *[llum_personatges(CAM, l.pos, l.r, '#c8d0dc', 0.3) for l in LLUMS[:len(WINDOWS)]],  # els finestrals
            llum_personatges(CAM, LLUMS[len(WINDOWS)].pos, LLUMS[len(WINDOWS)].r, '#e8dcc8', 0.55),  # el carrer, per la porta
            llum_personatges(CAM, FOC[1].pos, FOC[1].r, '#ff8a30', 0.7, whenPropVisible='forn_ences'),  # el forn encès
            llum_personatges(CAM, FOC[2].pos, FOC[2].r, '#ffa040', 1.0, whenPropVisible='forn_fort'),  # el forn a tota màquina
        ],
    },
}
