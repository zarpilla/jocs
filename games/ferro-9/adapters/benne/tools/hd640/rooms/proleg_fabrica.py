"""
Pròleg 3 · «Cent vint anys abans...» (pantalla sencera, cinemàtica). EN 3D (hd640/tres_d.py), a 1×.

La fàbrica de ferro-9 de nit, vista des d'un pont, mirant canal amunt. El canal fuig en diagonal fins a la dàrsena
del fons, i porta l'ull fins al portal dels forns, que crema:
  - a l'esquerra, a prop i tallada per la vora, la nau llarga de maó (en 3/4: la façana del canal amb els finestrals
    encesos, el capçal i la teulada de pissarra amb el llanternó), el rètol de bombetes «ALDAIA · FERRO-9» dalt de
    la teulada, girat cap al pont, i dues xemeneies treient fum;
  - al fons, petita i girada, la nau de la façana (el dibuix pla de sempre, projectat): el frontó amb l'ull de bou
    en forma de roda dentada, el rètol FERRO-9 i el portal dels forns mig obert, amb els carrils fins al moll;
  - el moll de l'esquerra, amb el fanal de gas, els noràis i la gavarra de mineral amarrada; a la dreta, l'altra
    riba amb els magatzems foscos i una filera de fanals que també fuig cap a la dàrsena;
  - el canal reflecteix tot el que hi ha a dalt (una segona càmera, de mirall) trencat per les ones, i la columna
    de la lluna;
  - primer pla fosc: la barana de ferro del pont i un fanal del pont, a contrallum, tallats per les vores.
Llums: la lluna (freda, de dalt a la dreta), els finestrals, el portal dels forns, els fanals.

El dibuix pla de sempre és a proleg_fabrica_pla_comu.py (en surten la façana del fons, el rètol, el fum i el cel);
la intro en vídeo (intro_animada.py) el continua fent servir.

Capes: `ambient` (el fum, les ones, l'onada de llum del rètol, el foc del portal, finestres que tremolen i el gas del
fanal), `iri_moll` / `iri_torn` (l'Iri passa pel moll sota el fanal, s'atura davant del portal, es gira i entra a la
llum; el sprite de l'Iri a l'escala que toca a cada distància, a contrallum).

El món: x a la dreta, y amunt, z canal amunt; 1 unitat ≈ 1 px allà on un personatge (≈110 px) fa la mida normal.
L'aigua és a y = -60 i els molls a y = 0.
"""
import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

import functools
import json
import math
from pathlib import Path

from PIL import Image

from hd.pix import (Canvas, Light, B4, W, H, hr, mix, ramp, BRICK, IRON, SMOKE, GLASS, FIRE,
                    NAVY, SIL, RUST)
from hd640.tres_d import Camera, Escena, Llum
from hd640.rooms import proleg_fabrica_pla_comu as fab
from hd640.rooms.proleg_gavina_pla_comu import Noise, vinyeta

SLATE, STONE, WATER, NIGHT = fab.SLATE, fab.STONE, fab.WATER, fab.NIGHT
DARK = ramp((4, 4, 8), (8, 7, 12), (12, 10, 16), (18, 14, 20), (26, 20, 26), (40, 30, 34), (64, 46, 44), n=8)
FARBRICK = ramp((10, 8, 16), (16, 12, 22), (24, 16, 26), (34, 22, 30), (48, 30, 34), (64, 40, 40), n=7)

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)

# ─── La càmera ─────────────────────────────────────────────────────────────
CPOS = (520.0, 400.0, -1500.0)
YAW, PITCH, F, CENTRE = -0.26, 0.0, 700.0, (320, 194)
CAM = Camera(pos=CPOS, yaw=YAW, pitch=PITCH, f=F, centre=CENTRE)
WY = -60.0                                   # el nivell de l'aigua
# la càmera de mirall: reflectida pel pla de l'aigua; la imatge surt girada de dalt a baix (v' = H - v)
CAM_M = Camera(pos=(CPOS[0], 2 * WY - CPOS[1], CPOS[2]), yaw=YAW, pitch=-PITCH, f=F, centre=(CENTRE[0], H - CENTRE[1]))

# ─── El món ────────────────────────────────────────────────────────────────
QX, OX = 0.0, 820.0                          # les vores del canal: el moll de la fàbrica i l'altra riba
ZE = 2500.0                                  # la dàrsena: el canal s'acaba aquí
AX = -200.0                                  # la façana de la nau llarga
ZA0, ZA1 = -300.0, 2150.0
HA = 430.0                                   # alçada de la paret (la cornisa)
AD = 900.0                                   # fondària de la nau
RIDGE = (AX - AD / 2, HA + 250.0)            # el carener: x, y
BAY = 115.0                                  # crugia: pilastres i finestrals
N_BAY = int((ZA1 - ZA0 - 40) // BAY)
# la nau de la façana (al fons), girada
BC, BANG = (40.0, 3550.0), -0.40
BTEX = (344, 60, 608, 248)                   # el retall del dibuix pla (la façana, amb el frontó)
BU = 3.05                                    # unitats del món per píxel del dibuix pla
BW, BD = (BTEX[2] - BTEX[0]) * BU, 1600.0
BH = (fab.QY - fab.B_TOP) * BU               # alçada de la paret
BPEAK = (fab.QY - fab.B_PEAK[1] + 9) * BU    # el cim del frontó (amb l'acroteri)
LAMP = (-40.0, 0.0, 1150.0)                  # el fanal del moll (el peu)
LAMP_H = 235.0
MOON = (588, 50)
SIGN_Z = 1250.0                              # el rètol de bombetes, de través damunt la teulada
SIGN_U = 4.4                                 # unitats per píxel del dibuix del rètol


def _bp(lx, y, lz):
    """Un punt de la nau del fons (coordenades locals: lx cap a la dreta de la façana, lz cap endins) al món."""
    c, s = math.cos(BANG), math.sin(BANG)
    return (BC[0] + lx * c - lz * s, y, BC[1] + lx * s + lz * c)


def _bfront(px, py, y0=0.0):
    """Un punt del dibuix pla de la façana del fons (px, py, en píxels de 640) al món, damunt la façana."""
    return _bp(-BW / 2 + (px - BTEX[0]) * BU, (fab.QY - py) * BU + y0, -BD / 2 - 1)


PORTAL = _bfront((fab.PORTAL[0] + fab.PORTAL[2]) / 2, fab.QY)          # el peu del portal dels forns
PORTAL_IN = _bp(-BW / 2 + ((fab.PORTAL[0] + fab.PORTAL[2]) / 2 - BTEX[0]) * BU, 0, -BD / 2 + 60)
PORTAL_LIT = _bfront((fab.PORTAL[0] + fab.PORTAL[2]) / 2, fab.QY - 30)


def _proj(P, cam=CAM):
    u, v, _ = cam.projecta(P)
    return u, v


# finestrals de la nau llarga: (z0, lit?) i les finestretes de baix
WIN_W, WIN_TOP, WIN_BOT = 62.0, 356.0, 200.0
LOW_W, LOW_TOP, LOW_BOT = 34.0, 140.0, 96.0
WINS = [(ZA0 + 40 + i * BAY + (BAY - WIN_W) / 2, i % 10 not in (2, 6, 9)) for i in range(N_BAY)]
LOWS = [(ZA0 + 40 + i * BAY + (BAY - LOW_W) / 2, i % 10 in (0, 1, 3, 4, 7, 8)) for i in range(N_BAY)]
FLICK = {4: 'a', 7: 'b', 13: 'c'}             # finestrals que tremolen (índex → nom de la superfície)


def _llums():
    L = [Llum((60000.0, 50000.0, 70000.0), 1e7, 1.1, power=1.0)]       # la lluna
    for z0, lit in WINS:
        if lit:
            L.append(Llum((AX + 40, 260.0, z0 + WIN_W / 2), 170, 1.5))
    L.append(Llum((LAMP[0], LAMP_H - 10, LAMP[2]), 330, 2.4))          # el fanal del moll
    L.append(Llum((PORTAL_LIT[0] + 40, 120.0, PORTAL_LIT[2] - 120), 620, 3.4))   # el portal dels forns
    for z in _right_lamps():
        L.append(Llum((OX + 40, LAMP_H - 10, z), 260, 1.6))
    return L


def _right_lamps():
    return [-200.0 + i * 460 for i in range(7)]


# ─── Les textures procedurals (en coordenades del món) ─────────────────────

def _px_k(P, cam):
    return cam.escala(P)


def _brick(base=2.2, course=13.0, length=34.0, cam=CAM, seed=0, soot=None):
    """Maó: filades de `course` unitats, maons de `length` a trencajunts. El morter és d'un píxel de pantalla (no
    s'esvaeix ni fa moaré de lluny); de lluny, el maó s'aplana."""
    def f(s, t, P):
        k = cam.escala(P)
        row = int(t // course)
        fy = (t % course) * k
        xx = s + (row % 2) * length / 2
        fx = (xx % length) * k
        lvl = base + (hr(int(xx // length), row, seed) - 0.5) * 0.7 * min(1.0, k * 3)
        if fy < 1.0:
            lvl -= 1.0 if k > 0.22 else 0.45
        elif fx < 1.0 and k > 0.18:
            lvl -= 0.8
        elif fy < 2.0 and k > 0.35:
            lvl += 0.25
        if hr(int(xx // length), row, seed + 9) > 0.95:
            lvl -= 0.5                                               # un maó recremat
        if soot:
            lvl -= soot(s, t)
        return lvl
    return f


def _setts(base=2.0, cam=CAM, seed=3):
    """Llambordes del moll (en x, z del món): files al llarg del moll."""
    def f(s, t, P):
        k = cam.escala(P)
        x, z = P[0], P[2]
        row = int(z // 22)
        xx = x + (row % 2) * 14
        lvl = base + (hr(int(xx // 28), row, seed) - 0.5) * 0.6 * min(1.0, k * 3)
        if k > 0.15 and ((z % 22) * k < 0.8 or (xx % 28) * k < 0.8):
            lvl -= 0.7
        return lvl
    return f


def _ashlar(base=2.4, cam=CAM, seed=7):
    """Carreus del mur del moll (s al llarg, t avall)."""
    def f(s, t, P):
        k = cam.escala(P)
        row = int(t // 20)
        xx = s + (row % 2) * 30
        lvl = base - t * 0.012 + (hr(int(xx // 60), row, seed) - 0.5) * 0.5
        if (t % 20) * k < 1.0 or (xx % 60) * k < 0.9:
            lvl -= 1.1
        if t > 40:
            lvl -= 0.6                                               # la humitat de prop de l'aigua
        return lvl
    return f


def _slate(cam=CAM):
    def f(s, t, P):
        k = cam.escala(P)
        row = int(t // 11)
        xx = s + (row % 2) * 9
        lvl = 2.4 - t * 0.003 + (hr(int(xx // 18), row, 2) - 0.5) * 0.5
        if (t % 11) * k < 1.0:
            lvl -= 0.9
        elif (t % 11) * k > 11 * k - 1.0 and k > 0.3:
            lvl += 0.3
        if (xx % 18) * k < 0.8 and k > 0.25:
            lvl -= 0.4
        return lvl
    return f


# ─── Els finestrals ─────────────────────────────────────────────────────────

def _arch(w, extra=0.0):
    r = w / 2

    def forma(s, t):
        if t >= r:
            return True
        return math.hypot(s - r, t - r) <= r + extra
    return forma


def _glass(w, h, lit, seed, flick=0.0):
    """El vidre d'un finestral (s, t en unitats des de dalt a l'esquerra): encès pel foc dels forns, amb la silueta
    d'una màquina a contrallum; o fosc, amb la lluna que hi rebota."""
    machine = hr(seed, 1) < 0.5

    def f(s, t, P):
        mull = abs(s - w / 3) < 2.5 or abs(s - 2 * w / 3) < 2.5 or (t > w / 2 and (t - w / 2) % 34 < 3)
        if mull:
            return 0.6 if lit else 0.3
        if lit:
            lvl = 2.2 + (t / h) * 2.8 + (hr(seed, int(s // 8), int(t // 16)) - 0.5) * 0.6 + flick
            if machine and ((t > h * 0.6 and abs(s - w / 2) < w * 0.3) or math.hypot(s - w / 2, t - h * 0.6) < w * 0.22):
                lvl -= 2.0
            return lvl
        return 1.4 - t / h * 0.6 + (1.3 if (int(s // 4) + int(t // 4)) % 9 == 0 and t < h / 2 else 0)
    return f


def finestrals(e, x, side, cam, flick=None):
    """Els finestrals d'una façana al pla x (de cara a +x), amb el brancal de pedra, l'ampit i la reixa."""
    flick = flick or {}
    out = x + 0.6
    for i, (z0, lit) in enumerate(WINS):
        z1 = z0 + WIN_W
        r = WIN_W / 2
        # brancal i dovelles de pedra (una mica més gran, arran de la paret)
        e.quad('pedra', (out, WIN_TOP + 9, z0 - 9), (out, WIN_TOP + 9, z1 + 9), (out, WIN_BOT, z1 + 9),
               (out, WIN_BOT, z0 - 9), ramp=STONE, lvl=lambda s, t, P: 3.0 - (0.9 if (t < r + 9 and int(math.degrees(
                   math.atan2(t - r - 9, s - r - 9)) // 14) % 2) else 0), forma=_arch(WIN_W + 18))
        sid = 'vidre_' + FLICK[i] if i in FLICK else 'vidre'
        e.quad(sid, (out + 0.4, WIN_TOP, z0), (out + 0.4, WIN_TOP, z1), (out + 0.4, WIN_BOT, z1),
               (out + 0.4, WIN_BOT, z0), ramp=GLASS if lit else NAVY,
               lvl=_glass(WIN_W, WIN_TOP - WIN_BOT, lit, i, flick.get(i, 0.0)), forma=_arch(WIN_W))
        # l'ampit, que sobresurt
        e.caixa('pedra', out - 1, out + 9, WIN_BOT - 9, WIN_BOT, z0 - 12, z1 + 12, STONE, 3.6,
                cares={'dalt': {'ramp': STONE, 'lvl': 4.6}, 'davant': {'ramp': STONE, 'lvl': 3.2}})
        # la clau de l'arc
        e.caixa('pedra', out, out + 4, WIN_TOP + 4, WIN_TOP + 16, z0 + r - 6, z0 + r + 6, STONE, 4.2)
    for i, (z0, lit) in enumerate(LOWS):
        z1 = z0 + LOW_W
        e.quad('pedra', (out, LOW_TOP + 7, z0 - 7), (out, LOW_TOP + 7, z1 + 7), (out, LOW_BOT - 7, z1 + 7),
               (out, LOW_BOT - 7, z0 - 7), ramp=STONE, lvl=3.0)
        e.quad('vidre', (out + 0.4, LOW_TOP, z0), (out + 0.4, LOW_TOP, z1), (out + 0.4, LOW_BOT, z1),
               (out + 0.4, LOW_BOT, z0), ramp=GLASS if lit else NAVY,
               lvl=(lambda s, t, P: 0.6 if abs(s - LOW_W / 2) < 2.5 or abs(t - 22) < 2.5 else 3.0 + t * 0.03)
               if lit else 1.2)


# ─── La nau llarga ──────────────────────────────────────────────────────────

def xemeneia(e, cx, cz, y0, top, r=46.0, flick=0.0):
    """Una xemeneia de maó quadrada, una mica cònica (en dos trams), amb anelles de ferro i el capçal."""
    mid = (y0 + top) / 2
    e.caixa('xemeneia', cx - r, cx + r, y0, mid, cz - r, cz + r, BRICK, 2.0,
            cares={'dreta': {'ramp': BRICK, 'lvl': _brick(2.7, 14, 30, seed=11)},
                   'davant': {'ramp': BRICK, 'lvl': _brick(1.7, 14, 30, seed=12)}})
    r2 = r * 0.82
    e.caixa('xemeneia', cx - r2, cx + r2, mid, top, cz - r2, cz + r2, BRICK, 2.0,
            cares={'dreta': {'ramp': BRICK, 'lvl': _brick(2.9, 14, 30, seed=13)},
                   'davant': {'ramp': BRICK, 'lvl': _brick(1.8, 14, 30, seed=14)}})
    for yy, rr in ((mid - 4, r + 5), (top - 70, r2 + 5)):                  # anelles de ferro
        e.caixa('xemeneia', cx - rr, cx + rr, yy, yy + 9, cz - rr, cz + rr, IRON, 2.6,
                cares={'dreta': {'ramp': IRON, 'lvl': 3.8}, 'dalt': {'ramp': IRON, 'lvl': 2.2}})
    e.caixa('xemeneia', cx - r2 - 12, cx + r2 + 12, top, top + 22, cz - r2 - 12, cz + r2 + 12, BRICK, 2.6,
            cares={'dreta': {'ramp': BRICK, 'lvl': 3.6}, 'dalt': {'ramp': FIRE, 'lvl': lambda s, t, P: 3.4 + flick
                   - 1.8 * (abs(s - r2 - 12) < r2 - 4 and abs(t - r2 - 12) < r2 - 4)}})
    # la boca, encesa del foc de dins
    e.quad('xemeneia', (cx - r2 + 4, top + 22.2, cz + r2 - 4), (cx + r2 - 4, top + 22.2, cz + r2 - 4),
           (cx + r2 - 4, top + 22.2, cz - r2 + 4), (cx - r2 + 4, top + 22.2, cz - r2 + 4), ramp=FIRE, lvl=3.6 + flick)


A_CHIMNEYS = ((AX - 640, 480.0, 880.0), (AX - 600, 1900.0, 1060.0))   # (x, z, cim)
B_CHIMNEY = (260.0, 700.0, 1340.0)                                      # local lx, lz, cim


def nau_llarga(e, cam, flick=None):
    rx, ry = RIDGE
    # la teulada de pissarra (el vessant del canal) i el llanternó del carener
    e.quad('teulada', (rx, ry, ZA0 - 30), (rx, ry, ZA1 + 30), (AX + 26, HA + 6, ZA1 + 30), (AX + 26, HA + 6, ZA0 - 30),
           ramp=SLATE, lvl=_slate(cam))
    e.caixa('llanterno', rx - 50, rx + 50, ry - 30, ry + 46, ZA0 + 160, ZA1 - 160, SLATE, 2.0,
            cares={'dreta': {'ramp': SLATE, 'lvl': lambda s, t, P: 1.8 + (2.2 if (s % 40 > 8 and t > 12 and t < 58
                   and hr(int(s // 40), 6) > 0.3) else 0)},
                   'dalt': {'ramp': SLATE, 'lvl': 3.4}, 'davant': {'ramp': SLATE, 'lvl': 1.4}})
    e.quad('llanterno', (rx, ry + 76, ZA0 + 150), (rx, ry + 76, ZA1 - 150), (rx + 66, ry + 44, ZA1 - 150),
           (rx + 66, ry + 44, ZA0 + 150), ramp=SLATE, lvl=3.0)
    # el capçal (de cara al pont): la paret i el frontó, amb un òcul
    def capcal(s, t, P):
        return _brick(1.5, seed=4)(s, t, P) - 0.8 * max(0.0, 1 - s / 160)
    e.quad('capcal', (AX - AD, HA, ZA0), (AX, HA, ZA0), (AX, 0, ZA0), (AX - AD, 0, ZA0), ramp=BRICK, lvl=capcal)
    e.quad('capcal', (AX - AD, ry, ZA0), (AX, ry, ZA0), (AX, HA, ZA0), (AX - AD, HA, ZA0), ramp=BRICK,
           lvl=_brick(1.4, seed=5), forma=lambda s, t: t >= abs(s - AD / 2) * (ry - HA) / (AD / 2) - 0.5)
    e.quad('capcal', (AX - AD / 2 - 46, ry - 60, ZA0 - 1), (AX - AD / 2 + 46, ry - 60, ZA0 - 1),
           (AX - AD / 2 + 46, ry - 152, ZA0 - 1), (AX - AD / 2 - 46, ry - 152, ZA0 - 1), ramp=GLASS,
           lvl=lambda s, t, P: 2.6 + t * 0.02 - (1.6 if abs(s - 46) < 3 or abs(t - 46) < 3 else 0),
           forma=lambda s, t: math.hypot(s - 46, t - 46) <= 44)
    # la façana del canal
    e.quad('facana', (AX, HA, ZA0), (AX, HA, ZA1), (AX, 0, ZA1), (AX, 0, ZA0), ramp=BRICK, lvl=_brick(2.0, seed=1))
    # el sòcol de pedra i la cornisa, que sobresurten
    e.caixa('socol', AX - 2, AX + 7, 0, 36, ZA0 - 7, ZA1, STONE, 2.4,
            cares={'dreta': {'ramp': STONE, 'lvl': _ashlar(2.4, cam)}, 'dalt': {'ramp': STONE, 'lvl': 3.6},
                   'davant': {'ramp': STONE, 'lvl': 1.8}})
    # les pilastres, amb el capitell
    for i in range(N_BAY + 1):
        z = ZA0 + 40 + i * BAY - 9
        e.caixa('pilastra', AX, AX + 10, 36, HA - 20, z, z + 18, BRICK, 2.4,
                cares={'dreta': {'ramp': BRICK, 'lvl': _brick(2.7, 13, 18, seed=20 + i)},
                       'davant': {'ramp': BRICK, 'lvl': 1.4}})
        e.caixa('pilastra', AX, AX + 14, HA - 26, HA - 18, z - 3, z + 21, STONE, 3.4,
                cares={'dalt': {'ramp': STONE, 'lvl': 4.2}})
    finestrals(e, AX, 1, cam, flick)
    e.caixa('cornisa', AX - 4, AX + 18, HA - 10, HA + 8, ZA0 - 18, ZA1 + 4, STONE, 3.0,
            cares={'dreta': {'ramp': STONE, 'lvl': lambda s, t, P: 3.8 - t * 0.12 - (0.7 if (s % 14) < 6 and t > 11 else 0)},
                   'dalt': {'ramp': STONE, 'lvl': 4.4}, 'sota': {'ramp': STONE, 'lvl': 0.8},
                   'davant': {'ramp': STONE, 'lvl': 2.6}})
    # baixant de coure a la cantonada del capçal
    e.caixa('baixant', AX + 2, AX + 10, 0, HA - 10, ZA0 + 8, ZA0 + 16, fab.COPPER, 2.6, cares={'dreta': {'ramp': fab.COPPER, 'lvl': 3.2}})


def retol_img(t=0.0):
    """El rètol de bombetes (la bastida de ferro i les lletres), en un dibuix transparent: com el de la teulada del
    dibuix pla. Amb `t`, l'onada de llum que el recorre i la bombeta fluixa."""
    sw = len(fab.SIGN) * 11 - 2
    x0, y0 = 6, 6
    cv = Canvas(sw + 14, 32, transparent=True)
    cv.hline(x0 - 4, x0 + sw + 3, y0 + 17, IRON, 2.4, 0)
    cv.hline(x0 - 4, x0 + sw + 3, y0 + 18, IRON, 1.2, 0)
    cv.hline(x0 - 4, x0 + sw + 3, y0 - 4, IRON, 2.0, 0)
    for x in range(x0 - 4, x0 + sw + 4, 8):
        cv.line(x, y0 - 4, x + 8, y0 + 17, IRON, 1.2, 0)
    for x in range(x0 - 4, x0 + sw + 4, 16):
        cv.vline(x, y0 - 4, y0 + 17, IRON, 1.4, 0)
    wave = -18 + t * (sw + 36)
    for x, y, n, i, j in fab.bulbs(fab.SIGN, x0, y0):
        cols = [(255, 244, 196), (250, 206, 120), (250, 206, 120), (196, 134, 70)]
        if t:
            k = max(0.0, 1 - abs(x - x0 - wave) / 12)
            if k:
                cols = [mix(c, (255, 252, 236), k * 0.85) for c in cols]
            if (n, i, j) == (9, 0, 0) and round(t * 24) in (4, 13, 14):
                cols = [mix(c, (120, 70, 40), 0.7) for c in cols]
        for (dx, dy), c in zip(((0, 0), (1, 0), (0, 1), (1, 1)), cols):
            cv.flat(x + dx, y + dy, c)
    return cv.img


def _sign_quad():
    w, h = retol_img().size
    W_, H_ = w * SIGN_U, h * SIGN_U
    cx = RIDGE[0] + 30
    y0 = RIDGE[1] + 70
    return ((cx - W_ / 2, y0 + H_, SIGN_Z), (cx + W_ / 2, y0 + H_, SIGN_Z), (cx + W_ / 2, y0, SIGN_Z),
            (cx - W_ / 2, y0, SIGN_Z)), (w, h)


def retol(e):
    """La bastida del rètol, dreta damunt la teulada (de través, de cara al pont), i les lletres."""
    (P0, P1, P2, P3), (w, h) = _sign_quad()
    rx, ry = RIDGE
    # les potes de la bastida, fins als vessants
    for k in (0.12, 0.5, 0.88):
        x = P3[0] + (P2[0] - P3[0]) * k
        yr = ry - abs(x - rx) * (ry - HA) / (AD / 2)
        for dz in (-30, 30):
            e.cable('bastida', [(x, P3[1] + 12, SIGN_Z), (x, yr, SIGN_Z + dz)], IRON, 1.6, gruix=4)
        e.cable('bastida', [(x, P3[1] + 12, SIGN_Z + 2), (x, yr, SIGN_Z + 2)], IRON, 2.0, gruix=5)
    e.quad('retol', P0, P1, P2, P3, tex=(retol_img(), (0, 0, w, h)))


# ─── La nau del fons (el dibuix pla, projectat) ─────────────────────────────

@functools.lru_cache(maxsize=None)
def facana_img(t=0.0):
    """El dibuix pla de la fàbrica (sense el rètol de la teulada) en un llenç transparent, reduït a la meitat (fent
    la mitjana: de lluny, la façana fa mig píxel per píxel del dibuix): la façana del fons en surt com a textura.
    Amb `t`, el foc del portal i les finestres que tremolen."""
    cv = Canvas(light=fab.LIGHT, transparent=True)
    fab.factory(cv, retol=False, t=t)
    return cv.img.resize((W // 2, H // 2), Image.Resampling.BOX)


def _gable(s, t):
    """Dins la silueta de la façana del fons (la paret i el frontó amb l'albardilla)? (s, t: unitats del món)."""
    px, py = BTEX[0] + s / BU, BTEX[1] + t / BU
    if py >= fab.B_TOP - 4:
        return fab.B_X0 - 4 <= px <= fab.B_X1 + 4
    pkx, pky = fab.B_PEAK
    if abs(px - pkx) <= 3 and py >= pky - 9:
        return True
    half = (fab.B_X1 - fab.B_X0) / 2 + 4
    return py >= pky - 5 + abs(px - pkx) / half * (fab.B_TOP - pky)


def nau_fons(e, cam):
    a, b = BW / 2, BD / 2
    P = _bp
    # la xemeneia de darrere
    lx, lz, top = B_CHIMNEY
    cx, _, cz = P(lx, 0, lz)
    xemeneia(e, cx, cz, BH, top, r=50)
    # el vessant de la dreta i la paret de la dreta (de cara a la dàrsena)
    e.quad('nau_fons', P(0, BPEAK - 30, -b), P(0, BPEAK - 30, b), P(a + 14, BH, b), P(a + 14, BH, -b), ramp=SLATE,
           lvl=lambda s, t, Pw: _slate(cam)(s, t, Pw) - 0.6)
    e.quad('nau_fons', P(a, BH, -b), P(a, BH, b), P(a, 0, b), P(a, 0, -b), ramp=BRICK,
           lvl=_brick(1.3, 13, 34, cam, seed=31))
    for k in range(4):                                                    # finestrals del costat
        z0 = -b + 160 + k * 320
        lit = k in (0, 2)
        e.quad('nau_fons', P(a + 0.5, 300, z0), P(a + 0.5, 300, z0 + 60), P(a + 0.5, 150, z0 + 60),
               P(a + 0.5, 150, z0), ramp=GLASS if lit else NAVY, lvl=_glass(60, 150, lit, 40 + k), forma=_arch(60))
    # la façana: el dibuix pla de sempre
    x0, y0, x1, y1 = BTEX
    Wt, Ht = (x1 - x0) * BU, (y1 - y0) * BU
    e.quad('B_davant', P(-a, Ht, -b - 1), P(a, Ht, -b - 1), P(a, 0, -b - 1), P(-a, 0, -b - 1),
           tex=(facana_img(), (x0 / 2, y0 / 2, x1 / 2, y1 / 2), 1), forma=_gable)


# ─── Els molls, el canal i l'altra riba ─────────────────────────────────────

def molls(e, cam, mirall=False):
    far = 9000.0
    if not mirall:
        e.quad('aigua', (QX, WY, ZE), (OX, WY, ZE), (OX, WY, CPOS[2] - 200), (QX, WY, CPOS[2] - 200), ramp=WATER, lvl=1.4)
    # els murs del moll (de cara al canal)
    e.quad('mur', (QX, 0, CPOS[2] - 200), (QX, 0, ZE), (QX, WY, ZE), (QX, WY, CPOS[2] - 200), ramp=STONE,
           lvl=_ashlar(2.2, cam))
    e.quad('mur', (OX, 0, ZE), (OX, 0, CPOS[2] - 200), (OX, WY, CPOS[2] - 200), (OX, WY, ZE), ramp=STONE,
           lvl=_ashlar(1.6, cam, seed=8))
    e.quad('mur', (QX, 0, ZE), (OX, 0, ZE), (OX, WY, ZE), (QX, WY, ZE), ramp=STONE, lvl=_ashlar(2.0, cam, seed=9))
    # els terres: el moll de la fàbrica, la dàrsena i l'altra riba
    e.quad('terra', (-3000, 0, far), (QX, 0, far), (QX, 0, CPOS[2] - 200), (-3000, 0, CPOS[2] - 200), ramp=STONE,
           lvl=_setts(1.9, cam))
    e.quad('terra', (QX, 0, far), (OX, 0, far), (OX, 0, ZE), (QX, 0, ZE), ramp=STONE, lvl=_setts(1.9, cam, seed=4))
    e.quad('terra', (OX, 0, far), (5000, 0, far), (5000, 0, CPOS[2] - 200), (OX, 0, CPOS[2] - 200), ramp=STONE,
           lvl=_setts(1.3, cam, seed=5))
    # la vora de pedra dels molls (l'albardilla), que fa la línia que porta l'ull
    e.caixa('vora', QX - 14, QX + 4, -6, 4, CPOS[2] - 200, ZE, STONE, 3.4,
            cares={'dalt': {'ramp': STONE, 'lvl': 3.8}, 'dreta': {'ramp': STONE, 'lvl': 3.0}})
    e.caixa('vora', QX - 14, OX + 14, -6, 4, ZE - 4, ZE + 14, STONE, 3.4,
            cares={'dalt': {'ramp': STONE, 'lvl': 3.6}, 'davant': {'ramp': STONE, 'lvl': 3.0}})
    e.caixa('vora', OX - 4, OX + 14, -6, 4, CPOS[2] - 200, ZE, STONE, 2.6,
            cares={'dalt': {'ramp': STONE, 'lvl': 3.0}, 'esquerra': {'ramp': STONE, 'lvl': 2.0}})
    # els carrils, del portal fins a la vora de la dàrsena
    lp = -BW / 2 + ((fab.PORTAL[0] + fab.PORTAL[2]) / 2 - BTEX[0]) * BU
    for dl in (-34, 34):
        A = _bp(lp + dl, 0.6, -BD / 2)
        d = (A[2] - ZE + 6) / math.cos(BANG)                             # fins a la vora, de través a la façana
        B = _bp(lp + dl, 0.6, -BD / 2 - d)
        e.cable('carrils', [A, B], IRON, 4.2, gruix=3)


def altra_riba(e, cam):
    """Els magatzems foscos de l'altra riba (de cara al canal), amb alguna finestra encesa."""
    x = OX + 420
    e.quad('magatzem', (x, 380, 3400), (x, 380, CPOS[2]), (x, 0, CPOS[2]), (x, 0, 3400), ramp=FARBRICK,
           lvl=lambda s, t, P: _brick(2.0, 13, 34, cam, seed=41)(s, t, P) - (0.9 if (s // 600) % 2 else 0))
    for i, z in enumerate(range(-1100, 3300, 150)):
        lit = hr(i, 44) > 0.72
        for yy in (250, 110):
            e.quad('magatzem', (x - 0.5, yy + 60, z + 46), (x - 0.5, yy + 60, z), (x - 0.5, yy, z),
                   (x - 0.5, yy, z + 46), ramp=GLASS if lit and yy == 250 else NAVY,
                   lvl=(lambda s, t, P: 3.4 + t * 0.02 - (1.2 if abs(s - 23) < 2.5 else 0)) if lit and yy == 250 else 1.0)
    # els ràfecs
    e.caixa('magatzem', x - 20, x + 400, 380, 396, CPOS[2], 3400, DARK, 3.0,
            cares={'esquerra': {'ramp': DARK, 'lvl': 2.4}, 'sota': {'ramp': DARK, 'lvl': 0.6}})


def fanal(e, sid, x, z, h=LAMP_H, lit=True):
    """Un fanal de gas: el pal, la base i la llanterna (la llum és a la passada de pantalla)."""
    e.caixa(sid, x - 9, x + 9, 0, 20, z - 9, z + 9, IRON, 1.6, cares={'dalt': {'ramp': IRON, 'lvl': 2.8}})
    e.caixa(sid, x - 3.5, x + 3.5, 20, h - 30, z - 3.5, z + 3.5, IRON, 1.6,
            cares={'dreta': {'ramp': IRON, 'lvl': 2.6}})
    e.caixa(sid, x - 6, x + 6, 150, 156, z - 6, z + 6, IRON, 2.2)
    e.caixa(sid, x - 10, x + 10, h - 30, h + 4, z - 10, z + 10, GLASS, 5.4 if lit else 1.0,
            cares={'davant': {'ramp': GLASS, 'lvl': 5.6 if lit else 1.2}, 'dreta': {'ramp': GLASS, 'lvl': 4.8 if lit else 1.0}})
    e.caixa(sid, x - 13, x + 13, h + 4, h + 9, z - 13, z + 13, IRON, 2.4)
    e.caixa(sid, x - 4, x + 4, h + 9, h + 16, z - 4, z + 4, IRON, 2.0)


def moll_fabrica(e, cam):
    """El moll de la fàbrica: noràis, el fanal de gas i la gavarra de mineral amarrada."""
    bollards = (-140.0, 420.0, 980.0, 1980.0)
    for z in bollards:
        e.caixa('norai', -34, -18, 0, 22, z - 8, z + 8, IRON, 2.0,
                cares={'dreta': {'ramp': IRON, 'lvl': 3.0}, 'dalt': {'ramp': IRON, 'lvl': 3.6}})
        e.caixa('norai', -37, -15, 22, 27, z - 11, z + 11, IRON, 3.2)
    fanal(e, 'fanal_moll', LAMP[0], LAMP[2])


GZ0, GZ1, GX0, GX1 = 140.0, 1180.0, 26.0, 236.0


def gavarra(e, cam, mirall=False):
    """La gavarra de ferro, carregada de mineral (es veu des de dalt: la coberta i el costat)."""
    top = 18.0
    e.caixa('gavarra', GX0, GX1, WY - 4, top, GZ0, GZ1, RUST, 2.0,
            cares={'dreta': {'ramp': RUST, 'lvl': lambda s, t, P: 2.3 - t * 0.02 + (0.5 if (s % 70) < 4 else 0)
                             + (1.2 if int(t) in (8, 9) or (int(t) in (30, 50) and (s % 14) < 3) else 0)},
                   'davant': {'ramp': RUST, 'lvl': lambda s, t, P: 1.6 - t * 0.015},
                   'dalt': {'ramp': RUST, 'lvl': 3.6}})
    if mirall:
        return
    e.quad('gavarra', (GX0 + 8, top + 0.4, GZ1 - 8), (GX1 - 8, top + 0.4, GZ1 - 8), (GX1 - 8, top + 0.4, GZ0 + 8),
           (GX0 + 8, top + 0.4, GZ0 + 8), ramp=RUST, lvl=0.8)
    # el mineral apilat: monticles (una superfície alçada amb soroll)
    N = Noise(77)
    step = 26.0
    zs = [GZ0 + 30 + i * step for i in range(int((GZ1 - GZ0 - 60) // step) + 1)]
    for z in zs[::-1]:
        hgt = 34 + 16 * math.sin(z / 150) + 8 * math.sin(z / 47)
        e.quad('mineral', (GX0 + 16, top, z + step), (GX1 - 16, top, z + step), (GX1 - 26, top + hgt, z + step / 2),
               (GX0 + 26, top + hgt, z + step / 2), ramp=IRON,
               lvl=lambda s, t, P: 1.4 + (N.fbm(P[0] / 9, P[2] / 9, 3) - 0.5) * 2.2
               + (1.6 if hr(int(P[0] // 3), int(P[2] // 3), 3) > 0.93 else 0), dues_cares=True)
        e.quad('mineral', (GX0 + 26, top + hgt, z + step / 2), (GX1 - 26, top + hgt, z + step / 2), (GX1 - 16, top, z),
               (GX0 + 16, top, z), ramp=IRON,
               lvl=lambda s, t, P: 2.0 + (N.fbm(P[0] / 9, P[2] / 9, 3) - 0.5) * 2.2
               + (1.6 if hr(int(P[0] // 3), int(P[2] // 3), 4) > 0.93 else 0), dues_cares=True)
    # les cordes d'amarratge fins als noràis
    for zb, zg in ((420.0, GZ0 + 40), (980.0, GZ1 - 40)):
        e.cable('corda', [(-26, 24, zb), ((-26 + GX0) / 2, 4, (zb + zg) / 2), (GX0 + 6, top + 6, zg)],
                fab.WALNUT, 3.4, gruix=3)


def pont(e):
    """El primer pla: la barana de ferro del pont i un fanal del pont, a contrallum."""
    z = CPOS[2] + 150
    yt = CPOS[1] - 30
    e.caixa('pont', -400, 1500, yt - 3.5, yt, z - 3, z + 3, SIL, 1.0, cares={'dalt': {'ramp': SIL, 'lvl': 2.8}})
    e.caixa('pont', -400, 1500, yt - 22, yt - 20.5, z - 1, z + 1, SIL, 0.6)
    for x in range(-400, 1500, 12):
        e.caixa('pont', x - 0.6, x + 0.6, yt - 140, yt - 3.5, z - 0.6, z + 0.6, SIL, 0.6)
        if (x // 12) % 2:                                                # els rínxols de ferro
            e.caixa('pont', x + 3, x + 9, yt - 12, yt - 10.5, z - 0.5, z + 0.5, SIL, 0.5)
            e.caixa('pont', x + 5.4, x + 6.6, yt - 16, yt - 6, z - 0.5, z + 0.5, SIL, 0.5)
    for x in (-60.0, 1180.0):                                            # pilars amb la bola
        e.caixa('pont', x - 8, x + 8, yt - 140, yt + 6, z - 8, z + 8, SIL, 1.0,
                cares={'dalt': {'ramp': SIL, 'lvl': 2.6}, 'dreta': {'ramp': SIL, 'lvl': 1.6}})
        e.caixa('pont', x - 4, x + 4, yt + 6, yt + 14, z - 4, z + 4, SIL, 1.8)
    # el fanal del pont, a la dreta (la llanterna, apagada, queda fora del quadre)
    x, zz = CPOS[0] + 44, CPOS[2] + 300
    e.caixa('pont', x - 5, x + 5, yt - 140, yt + 900, zz - 5, zz + 5, SIL, 0.6,
            cares={'esquerra': {'ramp': SIL, 'lvl': 1.9}, 'davant': {'ramp': SIL, 'lvl': 0.8}})
    e.caixa('pont', x - 12, x + 12, yt - 20, yt + 8, zz - 12, zz + 12, SIL, 1.2,
            cares={'esquerra': {'ramp': SIL, 'lvl': 2.2}})
    e.caixa('pont', x - 10, x + 10, yt + 140, yt + 150, zz - 10, zz + 10, SIL, 1.2,
            cares={'esquerra': {'ramp': SIL, 'lvl': 2.2}})


# ─── El cel i la ciutat (en pantalla) ───────────────────────────────────────

N_CLOUD = Noise(32)
HZ = CENTRE[1] - F * math.tan(PITCH)          # l'horitzó a la pantalla


def cel(cv):
    rnd_stars = {(int(hr(i, 1) * W), int(hr(i, 2) * 150)) for i in range(300)}
    mx, my = MOON
    for y in range(H):
        for x in range(W):
            t = max(0.0, min(1.0, y / (HZ + 30)))
            lvl = 0.6 + t ** 2.2 * 6.6
            lvl += max(0.0, 1 - abs(x - 330) / 300) * t ** 3 * 1.6           # el resplendor dels forns
            dm = math.hypot(x - mx, y - my)
            if dm < 93:
                lvl += (1 - dm / 93) ** 2 * 2.2
            c = N_CLOUD.fbm(x / 93, y / 19, 5)
            band = max(0.0, 1 - abs(y - 62) / 40)
            if c * band > 0.42:
                lvl += 0.8 + (1.2 * (1 - dm / 120) if dm < 120 else 0)
                if N_CLOUD.fbm(x / 93, (y - 3) / 19, 5) * band <= 0.42:
                    lvl += 0.6 * max(0.0, 1 - dm / 190)
            cv.put(x, y, NIGHT, lvl, 0)
            if (x, y) in rnd_stars and dm > 20 and c * band < 0.4:
                b = hr(x, y, 2)
                cv.flat(x, y, mix((120, 110, 160), (240, 236, 255), b))
    cv.glow(mx, my, 40, (200, 200, 230), 0.35)
    cv.disc(mx, my, 12, 12, fab.PAPER, lambda nx, ny: 5.5 if nx * nx + ny * ny < 0.7 or nx > 0 else 4.6, 0)
    for dx, dy, r in ((-4, -3, 3.0), (4, 4, 2.2), (-1, 7, 1.8), (5, -5, 1.5), (-7, 3, 1.2)):
        cv.disc(mx + dx, my + dy, r, r, fab.PAPER, 4.5, 0)
        cv.put(mx + dx + round(r * 0.6), my + dy + round(r * 0.6), fab.PAPER, 5.8, 0)


def ciutat(cv):
    """La ciutat de fons, a l'horitzó: una silueta baixa, amb finestretes i alguna xemeneia."""
    base = round(_proj((0, 0, 14000))[1])
    tops = [base] * W
    x = 0
    i = 0
    while x < W:
        w = 8 + int(hr(i, 51) * 18)
        top = base - 10 - int(hr(i, 52) * 16)
        for xx in range(x, min(W, x + w)):
            tops[xx] = top
        if hr(i, 53) < 0.25:
            cx = x + 2 + int(hr(i, 54) * max(1, w - 4))
            for xx in range(cx, min(W, cx + 2)):
                tops[xx] = top - 10 - int(hr(i, 55) * 12)
        x += w
        i += 1
    for x in range(W):
        for y in range(tops[x], base + 30):
            if x % 3 != 2 and y % 4 != 3 and hr(x // 3, y // 4, 8) < 0.05 and y > tops[x] + 2 and y < base:
                cv.flat(x, y, (190, 120, 60) if hr(x // 3, y // 4, 9) > 0.3 else (220, 160, 90))
            else:
                cv.put(x, y, SIL, 1.9 + (0.7 if y == tops[x] else 0), 0)


# ─── L'escena ───────────────────────────────────────────────────────────────

def escena(cv, cam, mirall=False, flick=None):
    cv.S = 1
    e = Escena(cv, cam, llums=_llums(), ambient=-0.5)
    molls(e, cam, mirall)
    altra_riba(e, cam)
    for z in _right_lamps()[::-1]:
        fanal(e, 'fanals', OX + 40, z)
    nau_fons(e, cam)
    xemeneia(e, A_CHIMNEYS[1][0], A_CHIMNEYS[1][1], HA, A_CHIMNEYS[1][2])
    nau_llarga(e, cam, flick)
    retol(e)
    xemeneia(e, A_CHIMNEYS[0][0], A_CHIMNEYS[0][1], RIDGE[1] - 80, A_CHIMNEYS[0][2])
    moll_fabrica(e, cam)
    gavarra(e, cam, mirall)
    if not mirall:
        _ombres(e)
        pont(e)
    return e


def _ombres(e):
    """La llum del portal i dels finestrals al terra del moll, i la foscor dels racons."""
    # la claror del portal dels forns, que s'escampa pel moll i la dàrsena
    px, _, pz = PORTAL
    e.claror((px - 420, 0.5, pz + 40), (px + 520, 0.5, pz + 40), (px + 620, 0.5, pz - 760), (px - 360, 0.5, pz - 760),
             (255, 150, 70), lambda s, t: 0.5 * max(0.0, 1 - math.hypot(s - 420, t) / 640) ** 1.4)
    # la llum dels finestrals de baix, a trossos pel moll
    for z0, lit in LOWS:
        if lit:
            e.claror((AX + 1, 0.5, z0 - 10), (AX + 1, 0.5, z0 + LOW_W + 10), (AX + 120, 0.5, z0 + LOW_W + 60),
                     (AX + 120, 0.5, z0 + 30), (240, 160, 80), lambda s, t: 0.28 * max(0.0, 1 - t / 120))
    # la gavarra fa ombra a l'aigua del costat del moll, i el racó de la dàrsena és fosc
    e.foscor('ombra', (OX - 120, WY + 0.5, ZE), (OX, WY + 0.5, ZE), (OX, WY + 0.5, ZE - 900), (OX - 120, WY + 0.5, ZE - 900),
             lambda s, t: 0.45 * max(0.0, 1 - s / 120))


def _glows(cv, cam, flick=None, gas=0.0, portal=0.0):
    """Els halos, en pantalla: finestrals, fanals, el portal, les boques de les xemeneies i el rètol."""
    flick = flick or {}
    for i, (z0, lit) in enumerate(WINS):
        if lit:
            u, v = _proj((AX, (WIN_TOP + WIN_BOT) / 2, z0 + WIN_W / 2), cam)
            k = cam.escala((AX, 0, z0))
            cv.glow(u, v, 34 * k + 4, (255, 170, 90), 0.22 + 0.15 * flick.get(i, 0.0))
    for x, z, s in [(LAMP[0], LAMP[2], 1.0)] + [(OX + 40, z, 0.8) for z in _right_lamps()]:
        u, v = _proj((x, LAMP_H - 12, z), cam)
        k = cam.escala((x, LAMP_H, z))
        g = gas if x == LAMP[0] else 0.0
        cv.glow(u, v, 150 * k + 6, (255, 200, 110), (0.45 + g * 0.3) * s)
        cv.glow(u, v, 40 * k + 2, (255, 240, 190), (0.8 + g * 0.3) * s)
    u, v = _proj(PORTAL_LIT, cam)
    cv.glow(u, v, 70, (255, 140, 60), 0.45 + portal)
    for x, z, top in A_CHIMNEYS:
        u, v = _proj((x, top + 30, z), cam)
        cv.glow(u, v, 14, (255, 140, 60), 0.6)
    bx, _, bz = _bp(B_CHIMNEY[0], 0, B_CHIMNEY[1])
    u, v = _proj((bx, B_CHIMNEY[2] + 30, bz), cam)
    cv.glow(u, v, 11, (255, 140, 60), 0.6)
    (P0, P1, P2, P3), _ = _sign_quad()
    u0, v0 = _proj(P0, cam)
    u1, v1 = _proj(P2, cam)
    cv.glow((u0 + u1) / 2, (v0 + v1) / 2, (u1 - u0) * 0.6, (255, 190, 110), 0.16)


# ─── El canal: el reflex ────────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _mirall():
    """El que es veu reflectit al canal: el cel (girat) i l'escena amb la càmera de mirall. → imatge de 640×360,
    ja girada de dalt a baix (el píxel (x, y) és el reflex que es veu a (x, y))."""
    sky = Canvas(light=LIGHT)
    cel(sky)
    # el cel reflectit: a la pantalla, el reflex de la fila v és la fila 2·HZ - v (simètrica respecte de l'horitzó);
    # el llenç del mirall és girat de dalt a baix, així que la fila v' hi porta la fila v' + 2·HZ - H + 1
    d = int(round(H - 1 - 2 * HZ))                               # (el llenç del mirall, desplaçat d files)
    img = Image.new('RGBA', (W, H))
    if d >= 0:
        img.paste(sky.img.crop((0, 0, W, 1)).resize((W, max(1, d))), (0, 0))
        img.paste(sky.img.crop((0, 0, W, H - d)), (0, d))
    else:
        img.paste(sky.img.crop((0, -d, W, H)), (0, 0))
        img.paste(sky.img.crop((0, H - 1, W, H)).resize((W, -d)), (0, H + d))
    cv = Canvas(light=LIGHT, img=img)
    escena(cv, CAM_M, mirall=True)
    _glows(cv, CAM_M)
    return cv.img.transpose(Image.FLIP_TOP_BOTTOM)


def canal(cv, e, t=0.0):
    """L'aigua: el reflex trencat per les ones (més fosc i més trencat de prop), i la columna de la lluna."""
    ph = 2 * math.pi * t
    M = _mirall().load()
    P = cv.P
    amo, ids = e.amo, e.ids
    water = ids.index('aigua') if 'aigua' in ids else -1
    mx = MOON[0]
    for y in range(int(HZ), H):
        dep = max(1.0, y - HZ)                                     # de lluny (dep petit) a prop
        for x in range(W):
            o = amo[y * W + x]
            if o != water:
                continue
            wob = math.sin(y * 0.55 + math.sin(x * 0.05 + ph) * 1.5 - ph * 2) * (0.6 + dep * 0.03)
            sy = y + int(math.sin(x * 0.11 + y * 0.9 - ph * 3) * dep * 0.02)
            sx = int(x + wob)
            base = P[x, y]
            if 0 <= sx < W and 0 <= sy < H:
                ripple = math.sin(y * 1.3 + math.sin(x / 17 + y * 0.6 - ph) * 2 - ph * 3) > -0.35 - 12 / dep
                if ripple:
                    c = M[sx, sy]
                    k = 0.78 - min(0.5, dep / 400)
                    lum = (c[0] + c[1] + c[2]) / 3
                    base = mix(base, c, min(1.0, k * (1.1 if lum > 70 else 0.6)))
                else:
                    base = mix(base, (6, 10, 22), 0.4)
            # la columna de la lluna
            spread = 2 + dep * 0.07
            d = abs(x - mx + math.sin(y * 0.7 - ph * 2) * 2) / spread
            if d < 1 and math.sin(y * 1.6 + x * 0.25 - ph * 3) > 0.1 + d * 0.6:
                base = mix(base, (210, 214, 240), 0.7 - d * 0.4)
            P[x, y] = tuple(base[:3]) + (255,)


# ─── Compondre ──────────────────────────────────────────────────────────────

def _flicks(t):
    """Finestrals que tremolen: {índex: quant}; un s'enfosqueix un sol fotograma (algú hi passa per davant)."""
    if not t:
        return {}
    ph = 2 * math.pi * t
    return {4: 0.45 * (math.sin(ph * 3) + 0.6 * math.sin(ph * 7 + 1) - 0.6 * math.sin(1)),
            13: 0.4 * (math.sin(ph * 4 + 2) - math.sin(2)) + 0.25 * math.sin(ph * 9),
            7: -1.6 if 17 <= t * 24 < 18 else 0.0}


@functools.lru_cache(maxsize=None)
def _escena_base():
    """L'escena quieta (sense el canal ni el fum): (imatge, escena)."""
    cv = Canvas(light=LIGHT)
    cel(cv)
    ciutat(cv)
    e = escena(cv, CAM)
    return cv.img.copy(), e


def _smoke_sources():
    out = []
    for x, z, top in A_CHIMNEYS:
        u, v = _proj((x, top + 22, z))
        out.append((u, v, 230 * CAM.escala((x, top, z)) / 0.2))
    bx, _, bz = _bp(B_CHIMNEY[0], 0, B_CHIMNEY[1])
    u, v = _proj((bx, B_CHIMNEY[2] + 22, bz))
    out.append((u, v, 80))
    return out


def frame(t=0.0):
    """La pantalla al moment `t` (0..1) del bucle de l'animació de fons. → imatge."""
    img, e = _escena_base()
    cv = Canvas(light=LIGHT, img=img.copy())
    fl = _flicks(t)
    if t:
        # el foc del portal i les finestres de la façana del fons (el dibuix pla, al seu moment)
        cv.img.alpha_composite(e.capa(facana_img(t), sids={'B_davant'}))
        cv.img.alpha_composite(e.capa(retol_img(t), sids={'retol'}))
        cv.P = cv.img.load()
        # els finestrals de la nau llarga que tremolen
        for i, k in fl.items():
            sid = 'vidre_' + FLICK[i]
            idx = [j for j, s in enumerate(e.ids) if s == sid]
            u0, v0, u1, v1 = e.caixes.get(sid, (0, 0, -1, -1))
            for y in range(max(0, int(v0)), min(H, int(v1) + 1)):
                for x in range(max(0, int(u0)), min(W, int(u1) + 1)):
                    if e.amo[y * W + x] in idx:
                        o = cv.P[x, y]
                        f = max(0.15, 1 + k * 0.35)
                        cv.P[x, y] = (min(255, int(o[0] * f)), min(255, int(o[1] * f)), min(255, int(o[2] * f)), 255)
    gas = 0.3 * (math.sin(2 * math.pi * t * 5 + 0.7) - math.sin(0.7)) + 0.2 * math.sin(2 * math.pi * t * 11) if t else 0.0
    portal = 0.08 * (math.sin(2 * math.pi * t * 3) if t else 0.0)
    canal(cv, e, t)
    _glows(cv, CAM, fl, gas, portal)
    fab.smoke(cv, _smoke_sources(), t=t)
    vinyeta(cv, 0.6)
    return cv.img


@functools.lru_cache(maxsize=None)
def base_img():
    return frame(0.0)


def bg(cv, t=0.0):
    cv.img.paste(frame(t) if t else base_img())
    cv.P = cv.img.load()


def _ambient_frames(n=24):
    from hd640.rooms.fabrica_cambra_pla_comu import frame_diff
    base = base_img()
    return [frame_diff(base, frame(i / n)) for i in range(n)]


PROPS = {}

# ─── L'Iri entra al torn de nit (capa del pròleg) ────────────────────────────
# Mentre la narració presenta la fàbrica, l'Iri passa pel moll sota el fanal, camina d'esquena (en 3/4) cap al portal
# dels forns, cada cop més petita, s'hi atura, es gira cap a la llum i hi entra («iri_torn», sense bucle: es queda
# buida). Fins llavors, la capa és buida («iri_moll»). El seu sprite, a l'escala que toca a cada distància, a
# contrallum: la vora encesa pel fanal i pel foc del portal. El fanal del moll la tapa quan hi passa per darrere.

ART = Path(__file__).resolve().parents[3] / 'placeholder-art'
IRI_WALK = (0.0, 5.4)             # del fanal al portal
IRI_ENTER = (5.4, 6.5)            # es gira i s'endinsa a la llum
ZT = 0.1
IRI_START = (-110.0, 0.0, 700.0)
IRI_STOP = (PORTAL[0] + 6, 0.0, PORTAL[2] - 110)
TAPA = {'fanal_moll', 'norai', 'pont'}


@functools.lru_cache(maxsize=None)
def _sheet(tag):
    meta = json.loads((ART / 'iri' / 'iri.json').read_text())
    feet = json.loads((ART / 'iri' / 'iri.character.json').read_text())['feet']
    sheet = Image.open(ART / 'iri' / 'iri.png').convert('RGBA')
    frames = list(meta['frames'].values())
    tg = next(x for x in meta['meta']['frameTags'] if x['name'] == tag)
    out = []
    for i in range(tg['from'], tg['to'] + 1):
        f = frames[i]['frame']
        out.append(sheet.crop((f['x'], f['y'], f['x'] + f['w'], f['y'] + f['h'])))
    return out, (feet['x'], feet['y'])


def warm_at(P):
    """Quanta llum càlida toca a un punt del món: la del fanal i la del portal (0..1)."""
    lamp = max(0.0, 1 - math.hypot(P[0] - LAMP[0], P[2] - LAMP[2]) / 360)
    port = max(0.0, 1 - math.hypot(P[0] - PORTAL[0], P[2] - PORTAL[2]) / 520)
    return min(1.0, lamp * 1.2 + port * 1.3)


def _lerp3(A, B, k):
    return tuple(a + (b - a) * k for a, b in zip(A, B))


def _iri_at(t):
    """→ (punt del món, etiqueta, fotograma, mirall?, fosa 0..1) al segon `t` del seu tros."""
    step = int(t / ZT)
    if t < IRI_WALK[1]:
        u = max(0.0, (t - IRI_WALK[0]) / (IRI_WALK[1] - IRI_WALK[0]))
        return _lerp3(IRI_START, IRI_STOP, u), 'WalkUL', step, True, 0.0
    u = min(1.0, (t - IRI_ENTER[0]) / (IRI_ENTER[1] - IRI_ENTER[0]))
    P = _lerp3(IRI_STOP, (PORTAL_IN[0], 0.0, PORTAL_IN[2]), u * 0.6)
    return P, ('WalkU' if u < 1 else 'IdleU'), step, False, max(0.0, (u - 0.3) / 0.7)


def draw_iri(cv, e, t):
    P, tag, step, flip, gone = _iri_at(t)
    frames, (fx, fy) = _sheet(tag)
    img = frames[step % len(frames)]
    if flip:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
        fx = img.width - fx
    k = CAM.escala(P)
    u, v, _ = CAM.projecta(P)
    w, h = max(1, round(img.width * k)), max(1, round(img.height * k))
    im = img.resize((w, h), Image.Resampling.BOX)
    ox, oy = round(u - fx * k), round(v - fy * k)
    warm = warm_at(P)
    # l'ombra de contacte, cap a la càmera (la llum és al davant: el portal)
    for dy in range(-1, 2):
        for dx in range(-round(9 * k * 1.6), round(9 * k * 1.6) + 1):
            X, Y = round(u + dx), round(v + dy)
            if 0 <= X < W and 0 <= Y < H and e.ids[e.amo[Y * W + X]] not in TAPA:
                if (dx / (9 * k * 1.6 + 0.5)) ** 2 + dy * dy / 2.5 < 1 and B4[Y & 3][X & 3] < 0.6:
                    o = cv.P[X, Y]
                    cv.P[X, Y] = (int(o[0] * 0.55), int(o[1] * 0.55), int(o[2] * 0.6), 255)
    src = im.load()
    for y in range(h):
        first = True
        for x in range(w):
            r, g, b, a = src[x, y]
            if a < 110:
                first = True
                continue
            X, Y = ox + x, oy + y
            if not (0 <= X < W and 0 <= Y < H):
                continue
            if e.ids[e.amo[Y * W + X]] in TAPA:
                first = False
                continue
            if gone > 0 and B4[Y & 3][X & 3] < gone:
                continue
            col = mix((r, g, b), (22, 16, 26), 0.62 - 0.3 * warm)
            col = mix(col, (255, 170, 90), 0.25 * warm)
            if first or (x + 1 < w and src[x + 1, y][3] < 110):
                col = mix(col, (255, 200, 130), 0.25 + 0.4 * warm)              # la vora encesa
            first = False
            cv.flat(X, Y, col)


def _iri_frames():
    from hd640.rooms.fabrica_cambra_pla_comu import frame_diff
    base = base_img()
    _, e = _escena_base()
    out = []
    for i in range(round(IRI_ENTER[1] / ZT) + 2):
        cv = Canvas(light=LIGHT, img=base.copy())
        draw_iri(cv, e, i * ZT)
        out.append(frame_diff(base, cv.img))
    out.append(Canvas(transparent=True).img)                                       # ja és a dins
    return out


ANIMS = {
    'ambient': {'frames': _ambient_frames, 'frameDuration': 130},
    'iri_moll': {'frames': lambda: [Image.new('RGBA', (W, H))], 'frameDuration': 1000, 'loop': False, 'zIndex': 2},
    'iri_torn': {'frames': _iri_frames, 'frameDuration': 100, 'loop': False, 'prop': 'iri_moll'},
}
