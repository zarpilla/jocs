"""
La infermeria de l'Arenga. EN 3D (hd640/tres_d.py), a 1×.

Una càmera alta que mira de biaix la cantonada del fons a l'esquerra:
  - a la paret de l'esquerra, en escorç, la **porta** del passadís (el camí cap al fons) i la **boca del tub de veu**;
  - a la paret del fons, l'**armari** de medicaments (amb volum) a la cantonada, l'ull de bou, l'**escriptori** amb
    l'arxivador de **fitxes**, el flexo i el walkie, el llum d'examen, la làmina del rentat de mans i el **marbre** amb
    la pica, el mirall, la **cafetera** i la bombona d'oxigen;
  - la **llitera de rescat** al mig, separada de la paret i girada cap a la càmera: qui hi seu (la Juana, en Bastida)
    hi queda darrere, i s'hi passa per darrere;
  - primer pla: la cortina de la llitera (el carril i la tela, en silueta) a l'esquerra, una canonada a la dreta i la
    galleda de les gases a baix.

Tot el detall ve del dibuix pla de sempre (infermeria_pla_comu.py), projectat; els decorats (el travesser que falta,
les mantes, l'ull de bou de dia) es dibuixen en 3D i en surt la diferència.

El món: x a la dreta (0 = la paret de la porta), y amunt (0 = el terra), z cap al fons (300 = la paret del fons);
1 unitat = 1 píxel de sala a la distància on un personatge fa ≈110 px (escala 1).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from PIL import Image

from hd.pix import Canvas, Light, W, H, hr, mix
from hd.rooms.arenga import CAB, DARK, WHITEP, REDP, YELL, BRASS, glow
from hd.rooms.comu import _diff
from hd.rooms.exterior import fbm
from hd.rooms.principal import CREAM, porthole, day_porthole, wear
from hd.rooms.infermeria import STEEL, MEDLINO, FILEG, PAD, OXY
from hd640.rooms import infermeria_pla_comu as PL
from hd640.rooms.laboratori_pla_comu import ceiling, lamp
from hd640.rooms.menjador_pla_comu import wall
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
ZW = 300                                           # la paret del fons
FY = PL.FLOOR_Y                                    # al dibuix pla, el terra (203)
HW = FY                                            # l'alçada de les parets: tot el dibuix pla (a dalt, les canonades)
XL = 100                                           # al dibuix pla, la cantonada: a l'esquerra, la paret de la porta
XR = 660                                           # la paret de la dreta
ZN = -280                                          # on s'acaben, cap a la càmera, el terra i les parets
ARMARI = (PL.ARMARI[0] - XL + 20, PL.ARMARI[2] - XL + 20, 36)   # l'armari: x0, x1, fons (no tapa el tub de veu)
DSH = 33                                           # l'escriptori, desplaçat a la dreta respecte del pla
DESK = (PL.DESK[0] - XL + DSH, PL.DESK[2] - XL + DSH, 44, FY - PL.DESK[1], 0.07)   # l'escriptori: x0, x1, fons, alçada, gir
COUNTER = (PL.COUNTER[0] - XL - 3, PL.COUNTER[1] - XL + 3, 40, FY - PL.COUNTER_Y)  # el marbre: x0, x1, fons, alçada
LL = (200, 54, 0.22)                               # la llitera: llarg, ample, gir (de cara a la càmera)
LL_H = (FY - PL.LL_BOT, FY - PL.LL_RAIL, FY - PL.LL_TOP)  # la llitera: sota la cistella, la barana, el matalasset
LAMPS = ((PL.LAMPS[0] - XL, 230), (PL.LAMPS[1] - XL, 170), (PL.LAMPS[2] - XL, 230))   # els llums (x, z)


def _w(fx):
    """Una x del dibuix pla de la paret del fons → la x del món."""
    return fx - XL


def _wz(fx):
    """Una x del dibuix pla de la paret de la porta → la z del món."""
    return ZW - XL + fx


def _y(fy):
    """Una y del dibuix pla (el terra, a 203) → l'alçada del món."""
    return FY - fy


DOOR = (_wz(PL.D_PORTA[0]), _wz(PL.D_PORTA[2]), _y(PL.D_PORTA[1]))   # la porta: z0, z1, alçada
VOICE = (_wz(PL.VOICE[0]), _y(PL.VOICE[1]))                          # la boca del tub de veu: z, y
PORT = (_w(PL.PORT[0]), _y(PL.PORT[1]), PL.PORT[2])                  # l'ull de bou: x, y del centre i radi

CAM = Camera(pos=(320, 180, -260), yaw=-0.22, pitch=0.2, f=480, centre=(330, 110))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)  # (la llum és la del món: la de l'Escena)
LLUMS = [Llum((x, HW - 30, z), 230, 1.6, power=1.4) for x, z in LAMPS] + [
    Llum((PORT[0], PORT[1], ZW - 10), 110, 0.4, power=1.6)]


def _terra_de(u, v):
    """El punt del terra (x, z) que es veu a (u, v) de la pantalla."""
    C = CAM
    x2, y2 = (u - C.centre[0]) / C.f, -(v - C.centre[1]) / C.f
    z2 = 1.0
    dy = y2 * C._cp - z2 * C._sp
    z1 = y2 * C._sp + z2 * C._cp
    dx = x2 * C._cy + z1 * C._sy
    dz = -x2 * C._sy + z1 * C._cy
    t = -C.pos[1] / dy
    return C.pos[0] + dx * t, C.pos[2] + dz * t


# On seuen a la llitera (els peus, en coordenades de sala: les del guió) i la llitera, a partir d'aquí.
SEU_JUANA = PL.JUANA
SEU_BASTIDA = (457, 208)   # al cantell de davant, amb les cames penjant (a 451,200 quedava sota el matalàs)
_JX, _JZ = _terra_de(*SEU_JUANA)
_LJ = PL.JUANA[0] - PL.LL_X0                        # al pla, la Juana seu a aquesta distància del cap de la llitera
_C, _S = math.cos(LL[2]), math.sin(LL[2])
LL_C = (_JX + (LL[0] / 2 - _LJ) * _C - (LL[1] / 2 - 12) * _S, _JZ + (LL[0] / 2 - _LJ) * _S + (LL[1] / 2 - 12) * _C)


def _ll_P(lx, y, lz):
    """Un punt de la llitera: `lx` des del cap de l'esquerra (x del pla menys LL_X0), `lz` des del davant."""
    X, Z = lx - LL[0] / 2, lz - LL[1] / 2
    return (LL_C[0] + X * _C - Z * _S, y, LL_C[1] + X * _S + Z * _C)


# ─── Les textures: el dibuix pla de sempre ───────────────────────────────────

def _paret(dia=False, vidre=None, cadeneta=0.0):
    """Les dues parets planes, de cara (amb les canonades del sostre a dalt). `vidre` = t: el mar de l'ull de bou;
    `cadeneta`: l'angle de la tapa del tub de veu (None: sense)."""
    cv = Canvas(light=PL.LIGHT)
    ceiling(cv)
    wall(cv, lvl=5.2, seed=4)
    wear(cv, 0, 40, W - 1, 168, 22, seed=4, k=0.2)
    PL.door(cv)
    PL._VT['chain'] = False
    try:
        PL.voice_tube(cv, *PL.VOICE)
    finally:
        PL._VT['chain'] = True
    if cadeneta is not None:
        PL._chain(cv, *PL.VOICE, cadeneta)
    porthole(cv, *PL.PORT, rim=4, seed=4)
    PL.exam_lamp(cv)
    PL.handwash(cv)
    PL.counter(cv)
    if dia:
        day_porthole(cv, *PL.PORT, seed=4)
    if vidre is not None:
        PL._glass(cv, vidre, dia)
    return cv.img


@functools.lru_cache(maxsize=None)
def _paret_base(dia=False):
    return _paret(dia)


@functools.lru_cache(maxsize=None)
def _paret_nua():
    cv = Canvas(light=PL.LIGHT)
    ceiling(cv)
    wall(cv, lvl=5.2, seed=4)
    wear(cv, 0, 40, W - 1, 168, 22, seed=4, k=0.2)
    return cv.img


def _mobles(sense=False, walkie=None):
    """L'armari, l'escriptori, les fitxes, el marbre i la llitera, plans sobre transparent (en surten els retalls).
    `sense`: la llitera sense el travesser; `walkie`: el llum del walkie (0..1)."""
    cv = Canvas(light=PL.LIGHT, transparent=True)
    PL.cabinet(cv)
    PL.desk(cv)
    PL.files(cv)
    PL.counter(cv)
    PL.stretcher(cv)
    if sense:
        PL.sense_travesser(cv)
    if walkie is not None:
        x, y = PL.FITXES[2] + 10, PL.DESK[1] - 9
        cv.flat(x, y, mix((30, 80, 44), (170, 255, 180), walkie))
        if walkie > 0.15:
            cv.glow(x, y, 4, (90, 255, 120), 0.55 * walkie)
    return cv.img


@functools.lru_cache(maxsize=None)
def _mobles_base(sense=False):
    return _mobles(sense)


@functools.lru_cache(maxsize=None)
def _mantes_pla():
    cv = Canvas(light=PL.LIGHT, transparent=True)
    PL.mantes(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _llum_pla():
    cv = Canvas(80, 40, light=PL.LIGHT, transparent=True)
    lamp(cv, 40, 10)
    return cv.img


ARMARI_BOX = (PL.ARMARI[0], PL.ARMARI[1], PL.ARMARI[2] + 1, FY)
DESK_BOX = (PL.DESK[0], PL.DESK[1] + 4, PL.DESK[2] + 1, FY)
FILES_BOX = (PL.FITXES[0], PL.FITXES[1], PL.FITXES[2] + 1, PL.FITXES[3] + 1)
FLEXO_BOX = (256, 96, 284, 149)                    # el flexo, dret
WALKIE_BOX = (PL.FITXES[2] + 1, 128, PL.FITXES[2] + 13, 149)
COUNTER_BOX = (PL.COUNTER[0], PL.COUNTER_Y + 1, PL.COUNTER[1] + 1, FY)
CAFE_BOX = (527, 58, 604, 150)                     # la cafetera, la tassa i el sucre (i el vapor, a dalt)
OXY_BOX = (618, 92, 637, FY + 2)                   # la bombona d'oxigen
LL_BOX = (PL.LL_X0 - 2, PL.LL_RAIL - 2, PL.LL_X1 + 3, PL.LL_BOT + 4)   # el davant de la cistella


# ─── Les superfícies ────────────────────────────────────────────────────────

def _terra(s, t, P):
    """Linòleum gris verdós de rajoles de 35, a escacs suaus, en coordenades del món."""
    x, z = P[0], P[2]
    gx, gz = math.floor(x / 35), math.floor(z / 35)
    v = 4.0 + (0.35 if (gx + gz) % 2 else 0) + (hr(int(x) // 4, int(z) // 4, 4) - 0.5) * 0.4
    v += (fbm(x / 80, z / 50, 6) - 0.5) * 0.6
    if x % 35 < 1.0 or z % 35 < 1.0:
        return v - 0.9
    return v


FOSC = [(2, 4, 5), (5, 8, 9), (9, 13, 14), (14, 19, 20), (20, 27, 28), (28, 36, 37)]
TELA = [(6, 12, 14), (12, 22, 26), (20, 34, 40), (30, 50, 58), (44, 68, 76)]


def escena(cv, tex, estat=frozenset()):
    """Tota la sala, de lluny a prop. `estat`: els decorats ('sense_travesser', 'mantes', 'dia').
    → l'Escena (qui ha pintat què)."""
    e = Escena(cv, CAM, LLUMS, ambient=-0.3)
    paret, nua, mob = tex['paret'], tex['nua'], tex['mobles']
    e.quad('sostre', (0, HW, ZN), (XR, HW, ZN), (XR, HW, ZW), (0, HW, ZW), ramp=CREAM, lvl=1.8, dues_cares=True)
    # la paret de la porta (x = 0): de prop, la paret nua; cap a la cantonada, el dibuix pla (x 0..100)
    e.quad('paret_esq_prop', (0, HW, ZN), (0, HW, ZW - XL), (0, 0, ZW - XL), (0, 0, ZN),
           tex=(nua, (300 - (ZW - XL - ZN), 0, 300, FY)) if ZW - XL - ZN <= 300 else
           (nua, (W - (ZW - XL - ZN), 0, W, FY)))
    e.quad('paret_esq', (0, HW, ZW - XL), (0, HW, ZW), (0, 0, ZW), (0, 0, ZW - XL), tex=(paret, (0, 0, XL, FY)))
    # la paret del fons (z = 300): el dibuix pla (x 100..640) i, a la dreta, la paret nua
    e.quad('paret_fons', (0, HW, ZW), (W - XL, HW, ZW), (W - XL, 0, ZW), (0, 0, ZW), tex=(paret, (XL, 0, W, FY)))
    e.quad('paret_fons_dreta', (W - XL, HW, ZW), (XR, HW, ZW), (XR, 0, ZW), (W - XL, 0, ZW),
           tex=(nua, (200, 0, 200 + XR - (W - XL), FY)))
    e.quad('paret_dreta', (XR, HW, ZW), (XR, HW, ZN), (XR, 0, ZN), (XR, 0, ZW), tex=(nua, (40, 0, 40 + ZW - ZN, FY)))
    # el terra
    e.quad('terra', (0, 0, ZW), (XR, 0, ZW), (XR, 0, ZN), (0, 0, ZN), ramp=MEDLINO, lvl=_terra)
    for lx, lz in LAMPS:
        e.claror((lx - 110, 0.3, lz + 110), (lx + 110, 0.3, lz + 110), (lx + 110, 0.3, lz - 110), (lx - 110, 0.3, lz - 110),
                 (255, 220, 150), lambda s, t: 0.24 * max(0.0, 1 - math.hypot(s - 110, t - 110) / 110) ** 1.3)
    if 'dia' in estat:
        # la claror del mar per l'ull de bou: una taca allargada en diagonal pel terra, cap endavant i a la dreta
        px_ = PORT[0]
        e.claror((px_ - 30, 0.5, ZW - 2), (px_ + 30, 0.5, ZW - 2), (px_ + 150, 0.5, ZW - 190), (px_ + 60, 0.5, ZW - 190),
                 (210, 226, 236), lambda s, t: 0.32 * max(0.0, 1 - t / 190) * max(0.0, 1 - abs(s / 60 - 0.5) * 2) ** 0.7)
    # la foscor dels racons
    e.foscor('racons', (0, 0.5, ZW), (XR, 0.5, ZW), (XR, 0.5, ZN), (0, 0.5, ZN),
             lambda s, t: max(0.6 * max(0.0, 1 - t / 26), 0.5 * max(0.0, 1 - s / 22)))
    e.foscor('cantonada', (0, HW, ZW - 0.5), (60, HW, ZW - 0.5), (60, 0, ZW - 0.5), (0, 0, ZW - 0.5),
             lambda s, t: 0.5 * max(0.0, 1 - s / 60))
    e.foscor('cantonada2', (0.5, HW, ZW - 60), (0.5, HW, ZW), (0.5, 0, ZW), (0.5, 0, ZW - 60),
             lambda s, t: 0.5 * max(0.0, 1 - (60 - s) / 60))
    # les quadernes de la paret de l'esquerra, de prop
    for z in (ZW - XL - 108 + 96 * k for k in range(-4, 1)):
        if z < ZN + 10:
            continue
        e.caixa('quadernes', 0, 7, 0, HW, z, z + 6, CREAM, 4.0,
                cares={'dreta': {'ramp': CREAM, 'lvl': lambda s, t, P: 4.6 - (1.2 if int(t) % 14 == 0 else 0)},
                       'davant': {'ramp': CREAM, 'lvl': 3.0}})
    # les canonades del sostre que vénen del fons cap a la càmera (a l'esquerra)
    e.tub('canonades', (18, HW - 10, ZW), (18, HW - 10, ZN + 40), 4, REDP, 3.4, brides=70)
    e.tub('canonades', (34, HW - 7, ZW), (34, HW - 7, ZN + 40), 2.5, WHITEP, 3.2, brides=90)
    # l'armari de medicaments, a la cantonada, contra la paret del fons
    ax0, ax1, ad = ARMARI
    e.foscor('ombra_armari', (ax0 - 6, 0.6, ZW), (ax1 + 10, 0.6, ZW), (ax1 + 10, 0.6, ZW - ad - 16),
             (ax0 - 6, 0.6, ZW - ad - 16), lambda s, t: 0.55 * min(1.0, max(0.0, (ad + 16 - t) / 16)))
    e.caixa('armari', ax0, ax1, 0, _y(PL.ARMARI[1]), ZW - ad, ZW, WHITEP, 3.6,
            cares={'davant': {'tex': (mob, ARMARI_BOX)}, 'dalt': {'ramp': WHITEP, 'lvl': 4.6},
                   'dreta': {'ramp': WHITEP, 'lvl': lambda s, t, P: 2.8 - (0.8 if t > 140 else 0)}})
    # l'escriptori, una mica girat: el davant (amb la cadira) és el dibuix pla
    dx0, dx1, dd, dh, da = DESK
    dcx, dcz = (dx0 + dx1) / 2, ZW - dd / 2 - 8
    e.foscor('ombra_escriptori', (dx0 - 6, 0.6, ZW), (dx1 + 16, 0.6, ZW), (dx1 + 16, 0.6, ZW - dd - 30),
             (dx0 - 6, 0.6, ZW - dd - 30), lambda s, t: 0.5 * min(1.0, max(0.0, (dd + 30 - t) / 22)))
    e.caixa_girada('escriptori', dcx, dcz, dx1 - dx0, dd, dh, da, STEEL, 2.4,
                   cares={'davant': {'tex': (mob, DESK_BOX)},
                          'dalt': {'ramp': [(16, 8, 6), (30, 15, 9), (48, 26, 14), (70, 40, 20), (94, 56, 28),
                                            (120, 74, 38), (148, 96, 50)],
                                   'lvl': lambda s, t, P: 4.4 + (fbm(s / 30, t / 6, 2) - 0.5) * 0.8},
                          'dreta': {'ramp': STEEL, 'lvl': 2.6}, 'esquerra': {'ramp': STEEL, 'lvl': 3.0}})

    def Pd(fx, y, lz):
        c, s_ = math.cos(da), math.sin(da)
        X, Z = (fx - XL + DSH) - dcx, lz - dd / 2
        return (dcx + X * c - Z * s_, y, dcz + X * s_ + Z * c)
    fx0, fy0, fx1, fy1 = FILES_BOX
    fcx = (fx0 + fx1) / 2
    P = Pd(fcx, 0, 24)
    e.caixa_girada('fitxes', P[0], P[2], fx1 - fx0, 30, fy1 - fy0, da, FILEG, 2.6, y0=dh,
                   cares={'davant': {'tex': (mob, FILES_BOX)}, 'dalt': {'ramp': FILEG, 'lvl': lambda s, t, P:
                                                                         4.8 if 8 < s < 30 and 6 < t < 18 else 3.6},
                          'esquerra': {'ramp': FILEG, 'lvl': 3.4}, 'dreta': {'ramp': FILEG, 'lvl': 2.4}})
    e.quad('fitxes', Pd(fx0 + 8, fy1 - fy0 + dh + 0.6, 22), Pd(fx0 + 28, fy1 - fy0 + dh + 0.6, 22),
           Pd(fx0 + 28, fy1 - fy0 + dh + 0.6, 10), Pd(fx0 + 8, fy1 - fy0 + dh + 0.6, 10), ramp=WHITEP, lvl=4.8)
    e.sprite('flexo', mob.crop(FLEXO_BOX), (277 - FLEXO_BOX[0], FLEXO_BOX[3] - FLEXO_BOX[1] - 1), Pd(277, dh, 30))
    e.sprite('walkie', mob.crop(WALKIE_BOX), (5, WALKIE_BOX[3] - WALKIE_BOX[1] - 1), Pd(PL.FITXES[2] + 7, dh, 18))
    # el marbre de la dreta, contra la paret: el davant i el sobre d'acer; la cafetera a sobre
    cx0, cx1, cd, ch = COUNTER
    e.foscor('ombra_marbre', (cx0 - 8, 0.6, ZW), (cx1 + 8, 0.6, ZW), (cx1 + 8, 0.6, ZW - cd - 16),
             (cx0 - 8, 0.6, ZW - cd - 16), lambda s, t: 0.55 * min(1.0, max(0.0, (cd + 16 - t) / 16)))
    e.caixa('marbre', cx0 + 3, cx1 - 3, 0, ch - 4, ZW - cd + 4, ZW, WHITEP, 3.6,
            cares={'davant': {'tex': (mob, (COUNTER_BOX[0], COUNTER_BOX[1] + 4, COUNTER_BOX[2], COUNTER_BOX[3]))},
                   'esquerra': {'ramp': WHITEP, 'lvl': 3.0}})
    e.caixa('marbre', cx0, cx1, ch - 4, ch, ZW - cd, ZW, STEEL, 4.4,
            cares={'dalt': {'ramp': STEEL, 'lvl': lambda s, t, P: 1.8 if 10 < s < 42 and 6 < t < 26 else
                            4.8 + (fbm(s / 20, t / 10, 3) - 0.5) * 0.6},
                   'davant': {'ramp': STEEL, 'lvl': 5.2}, 'esquerra': {'ramp': STEEL, 'lvl': 4.0}})
    e.sprite('cafetera', mob.crop(CAFE_BOX), ((PL.CAFE[0] + PL.CAFE[2]) / 2 - CAFE_BOX[0], PL.CAFE[3] - CAFE_BOX[1]),
             (_w((PL.CAFE[0] + PL.CAFE[2]) / 2), ch, ZW - 12))
    # la bombona d'oxigen, lligada a la paret
    e.sprite('bombona', tex['oxigen'], (9, OXY_BOX[3] - OXY_BOX[1] - 1), (_w(627), 0, ZW - 9))
    # els cables pel terra
    for ramp, lv, pts in (
            (CAB, 2.4, [(cx0 - 4, 0.8, ZW - 4), (cx0 - 20, 0.8, ZW - 30), (cx0 - 60, 0.8, ZW - 34), (dx1 + 30, 0.8, ZW - 50)]),
            (YELL, 2.4, [(dx0 + 10, 0.8, ZW - 50), (dx0 - 10, 0.8, ZW - 70), (ax1 + 6, 0.8, ZW - 80), (ax0 + 10, 0.8, ZW - 44)])):
        e.cable('cables', pts, ramp, lv, gruix=2.0)
    # la llitera de rescat, girada: les potes, la cistella (el dibuix pla) i el matalasset amb el coixí
    lw, ld, la = LL
    hb, hr_, ht = LL_H
    e.foscor('ombra_llitera', *[_ll_P(lx, 0.6, lz) for lx, lz in ((-16, ld + 26), (lw + 16, ld + 26), (lw + 16, -16), (-16, -16))],
             lambda s, t: 0.6 * min(1.0, min(s, t, lw + 32 - s, ld + 42 - t) / 18))
    for lx in (13, lw - 13):
        for lz in (8, ld - 8):
            e.tub('llitera', _ll_P(lx, 0, lz), _ll_P(lx, hb, lz), 1.6, STEEL, 3.6)
        e.tub('llitera', _ll_P(lx, hb - 10, 8), _ll_P(lx, hb - 10, ld - 8), 1.2, STEEL, 3.2)
        e.caixa_girada('llitera', *[_ll_P(lx, 0, ld / 2)[i] for i in (0, 2)], 18, ld - 4, 3, la, STEEL, 2.6)
    e.tub('llitera', _ll_P(13, 5, ld / 2), _ll_P(lw - 13, 5, ld / 2), 1.2, STEEL, 3.0)
    mx, mz = [_ll_P(lw / 2, 0, ld / 2)[i] for i in (0, 2)]
    lb = tex['llitera']
    e.caixa_girada('llitera', mx, mz, lw, ld, hr_ - hb + 2, la, PAD, 2.2, y0=hb,
                   cares={'davant': {'tex': (lb, LL_BOX)},
                          'esquerra': {'ramp': STEEL, 'lvl': lambda s, t, P: 3.6 if (int(s) + int(t)) % 4 == 0 else 1.8},
                          'dreta': {'ramp': STEEL, 'lvl': lambda s, t, P: 3.2 if (int(s) + int(t)) % 4 == 0 else 1.6},
                          'dalt': {'ramp': PAD, 'lvl': 2.6}})

    def matalas(s, t, P):
        v = 3.8 + (fbm(s / 20, t / 8, 5) - 0.5) * 0.5 - t * 0.012
        if abs(t - 4) < 0.6 or abs(t - (ld - 10) + 4) < 0.6:
            v -= 0.8                                                     # el cosit
        return v
    e.caixa_girada('llitera', mx, mz, lw - 8, ld - 8, ht - hr_ - 2, la, PAD, 3.0, y0=hr_ + 2,
                   cares={'dalt': {'ramp': PAD, 'lvl': matalas}, 'davant': {'ramp': PAD, 'lvl': 3.8},
                          'esquerra': {'ramp': PAD, 'lvl': 3.4}})
    pc = _ll_P(30, 0, ld / 2)
    e.caixa_girada('llitera', pc[0], pc[2], 30, ld - 18, 7, la + 0.08, WHITEP, 4.0, y0=ht,
                   cares={'dalt': {'ramp': WHITEP, 'lvl': lambda s, t, P: 4.6 - abs(t - (ld - 18) / 2) * 0.05
                                   - (1.0 if abs(s - 12 - t * 0.2) < 0.7 else 0)}})
    # les mantes (decorat): damunt la falda i les espatlles de qui seu, a la seva escala
    if 'mantes' in estat:
        mt = _mantes_pla()
        bb = mt.getbbox()
        jx, jz = _JX, _JZ
        e.sprite('mantes', mt.crop(bb), (SEU_JUANA[0] - bb[0], SEU_JUANA[1] - bb[1]), (jx, 0, jz))
    # els llums
    lp = _llum_pla()
    for lx, lz in LAMPS:
        e.sprite('llums', lp, (40, 6), (lx, HW - 24, lz))
        e.cable('llums', [(lx, HW, lz), (lx, HW - 24, lz)], CAB, 2.4, gruix=1.0)
    # primer pla: la cortina de la llitera (el carril i la tela) a l'esquerra, una canonada a la dreta i la galleda
    e.tub('primer_pla', (-10, HW - 30, 40), (90, HW - 30, 40), 2.2, FOSC, 2.6)

    def plecs(s, t, P):
        return 1.6 + 0.9 * math.sin(s / 5.5) + (0.5 if t < 6 else 0) - t * 0.004
    for k in range(6):
        a0, a1 = -10 + k * 8, -10 + (k + 1) * 8
        dz = 5 * math.sin(k * 1.3)
        e.quad('primer_pla', (a0, HW - 32, 40 + dz), (a1, HW - 32, 40 - dz), (a1 + 3, 20, 40 - dz), (a0 + 3, 20, 40 + dz),
               ramp=TELA, lvl=lambda s, t, P, k=k: plecs(s + k * 8, t, P), dues_cares=True)
    e.tub('primer_pla', (452, 0, 92), (452, HW, 92), 7, FOSC, 2.2, brides=60)
    e.tub('primer_pla', (452, HW - 50, 92), (XR, HW - 50, 92), 4, FOSC, 2.0)
    e.caixa_girada('primer_pla', 70, 16, 26, 26, 24, 0.5, FOSC, 1.8,
                   cares={'dalt': {'ramp': FOSC, 'lvl': lambda s, t, P: 0.6 if 3 < s < 23 and 3 < t < 23 else 3.0},
                          'davant': {'ramp': FOSC, 'lvl': lambda s, t, P: 1.4 + (0.9 if abs(t - 16) < 1.5 else 0)},
                          'dreta': {'ramp': FOSC, 'lvl': 2.4}})
    return e


# ─── Composició ─────────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _oxigen():
    cv = Canvas(light=PL.LIGHT, transparent=True)
    PL.counter(cv)
    return cv.img.crop(OXY_BOX)


@functools.lru_cache(maxsize=None)
def _textures(dia=False, sense=False):
    return {'paret': _paret_base(dia), 'nua': _paret_nua(), 'mobles': _mobles_base(), 'llitera': _mobles_base(sense),
            'oxigen': _oxigen()}


def _render(estat=frozenset(), tex=None):
    cv = Canvas(light=LIGHT)
    e = escena(cv, tex or _textures('dia' in estat, 'sense_travesser' in estat), estat)
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)    # la barra de verbs: negre
    return cv.img, e


@functools.lru_cache(maxsize=None)
def _base(estat=frozenset()):
    return _render(estat)


def bg(cv):
    cv.img.paste(_base()[0])
    cv.P = cv.img.load()


def _decorat(*estat):
    """Un decorat: la sala amb aquell estat, menys la de sempre (només el que canvia)."""
    def draw(cv):
        img, _ = _base(frozenset(estat))
        cv.img.alpha_composite(_diff(img, _base()[0]))
        cv.P = cv.img.load()
    return draw


PROPS = {'sense_travesser': _decorat('sense_travesser'), 'mantes': _decorat('mantes'),
         'ulls_dia': _decorat('dia')}                                   # Escenes 2 i 3: de dia


# ─── Animacions ─────────────────────────────────────────────────────────────

def _sprite_capa(e, sid, img, peu_img, peu, lliure=False):
    """Un fotograma d'un dibuix pla dret (un sprite de l'escena), on aquell sprite és el que es veu (`lliure`: també
    fora del sprite, on no hi ha res al davant: el vapor que puja)."""
    from pixels import nearest
    idx = e.ids.index(sid)
    davant = {i for i, s in enumerate(e.ids) if s in ('primer_pla', 'llums')}
    k = e.cam.escala(peu)
    u, v, _ = e.cam.projecta(peu)
    w, h = max(1, round(img.width * k)), max(1, round(img.height * k))
    im = nearest(img, (w, h)) if k >= 1 else img.resize((w, h), Image.Resampling.BOX)
    ox, oy = round(u - peu_img[0] * k), round(v - peu_img[1] * k)
    out = Image.new('RGBA', (e.cv.w, e.cv.h), (0, 0, 0, 0))
    src, dst, W_ = im.load(), out.load(), e.cv.w
    for y in range(h):
        Y = oy + y
        if not 0 <= Y < e.cv.h:
            continue
        for x in range(w):
            X = ox + x
            if not 0 <= X < W_ or src[x, y][3] < (1 if lliure else 128):
                continue
            a = e.amo[Y * W_ + X]
            if a == idx or (lliure and a not in davant):
                dst[X, Y] = src[x, y]
    return out


def _fotograma(capes, estat=frozenset()):
    img = _base(estat)[0]
    out = img.copy()
    for c in capes:
        out.alpha_composite(c)
    return _diff(out, img)


def _frames_port(dia):
    estat = frozenset({'dia'}) if dia else frozenset()
    _, e = _base(estat)
    return [_fotograma([e.capa(_paret(dia, vidre=i / 12), {'paret_fons'})], estat) for i in range(12)]


def _frames_cadeneta():
    """La tapa del tub de veu es gronxa amb el balanceig."""
    _, e = _base()
    return [_fotograma([e.capa(_paret(cadeneta=9 * math.sin(i / 32 * 2 * math.pi)), {'paret_esq'})]) for i in range(32)]


def _frames_walkie():
    """El walkie es carrega: el llum verd respira."""
    _, e = _base()
    dx0, dx1, dd, dh, da = DESK
    dcx, dcz = (dx0 + dx1) / 2, ZW - dd / 2 - 8
    c, s_ = math.cos(da), math.sin(da)
    X, Z = (PL.FITXES[2] + 7 - XL + DSH) - dcx, 18 - dd / 2
    peu = (dcx + X * c - Z * s_, dh, dcz + X * s_ + Z * c)
    out = []
    for i in range(12):
        k = 0.5 - 0.5 * math.cos(i / 12 * 2 * math.pi)
        im = _mobles(walkie=k).crop(WALKIE_BOX)
        out.append(_fotograma([_sprite_capa(e, 'walkie', im, (5, WALKIE_BOX[3] - WALKIE_BOX[1] - 1), peu)]))
    return out


def _frames_cafe():
    """La cafetera dolenta, sempre encesa: el vapor puja i cau una gota a la gerra."""
    _, e = _base()
    base = _mobles_base()
    cx0, cy0, cx1, cy1 = PL.CAFE
    gx, top, surf = (cx0 + cx1 - 8) // 2, cy0 + 12, cy0 + 24
    n, wisps = 64, 14
    peu = (_w((cx0 + cx1) / 2), COUNTER[3], ZW - 12)
    pi = ((cx0 + cx1) / 2 - CAFE_BOX[0], cy1 - CAFE_BOX[1])
    out = []
    for i in range(n):
        cv = Canvas(light=PL.LIGHT, img=base.copy())
        vap = Canvas(light=PL.LIGHT, transparent=True)
        t = i / n
        for p in range(wisps):
            age = (t * 2 + p / wisps) % 1
            y = cy0 + 13 - age * 53
            x = cx0 + 1 - age * 21 + 3 * math.sin(age * 9 + p * 1.7)
            a = 0.75 * (1 - age) * min(1.0, age * 5)
            for dx, k in ((0, 1.0), (1, 0.6), (-1, 0.3)):
                xx, yy = round(x) + dx, round(y)
                if 0 <= xx < W and 0 <= yy < H:
                    vap.P[xx, yy] = (236, 240, 240, int(255 * min(1.0, a * k)))
        k = i % 32
        if k < 5:
            cv.flat(gx, top, mix(cv.get(gx, top), (90, 50, 26), 0.4 + k * 0.12))
        elif k < 11:
            y = top + (k - 4) * 2
            if y < surf:
                cv.flat(gx, y, (70, 38, 18))
        elif k < 15:
            r = k - 10
            for dx in (-r - 1, r + 1):
                cv.flat(gx + dx, surf, mix(cv.get(gx + dx, surf), (120, 76, 44), 0.6))
        capa = _sprite_capa(e, 'cafetera', cv.img.crop(CAFE_BOX), pi, peu)
        vp = _sprite_capa(e, 'cafetera', vap.img.crop(CAFE_BOX), pi, peu, lliure=True)
        img = _base()[0].copy()
        img.alpha_composite(capa)
        img.alpha_composite(vp)
        out.append(_diff(img, _base()[0]))
    return out


ANIMS = {'cafe': {'frames': _frames_cafe, 'frameDuration': 90},
         'walkie': {'frames': _frames_walkie, 'frameDuration': 150},
         'cadeneta': {'frames': _frames_cadeneta, 'frameDuration': 140},
         'mar': {'frames': lambda: _frames_port(False), 'frameDuration': 220},
         'ulls_dia_mar': {'frames': lambda: _frames_port(True), 'frameDuration': 220}}


# ─── Capes del davant i geometria (coordenades de sala, projectades) ─────────

def _amo(ids, estat=frozenset()):
    def mask(x, y):
        _, e = _base(estat)
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


def _pl(lx, lz, y=0.0):
    P = _ll_P(lx, y, lz)
    return _p(P[0], P[2], y)


# El primer pla tapa sempre; qui seu a la llitera o hi passa per darrere hi queda darrere (el travesser que falta i
# les mantes van amb la llitera).
FRONT = [
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 30},
    {'id': 'davant_llitera', 'mask': _amo({'llitera'}), 'baseline': _pl(LL[0] / 2, -2)[1], 'zIndex': 20,
     'props': ('sense_travesser', 'mantes')},
]


def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


def _v_escala(k):
    """La y de pantalla on un personatge fa escala `k` (al terra)."""
    lo, hi = -2000.0, 3000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.escala((260, 0, z)) > k:
            lo = z
        else:
            hi = z
    return CAM.projecta((260, 0, lo))[1]


def _talla(poly, vmax):
    """El polígon de pantalla `poly` tallat per sota de la y `vmax` (on els personatges passarien d'escala 1,2)."""
    out = []
    for (ax, ay), (bx, by) in zip(poly, poly[1:] + poly[:1]):
        if ay <= vmax:
            out.append((ax, ay))
        if (ay <= vmax) != (by <= vmax):
            k = (vmax - ay) / (by - ay)
            out.append((round(ax + (bx - ax) * k), round(vmax)))
    return [(max(0, min(W - 1, x)), y) for x, y in out]


def _escala_a(v):
    lo, hi = -2000.0, 3000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.projecta((260, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((260, 0, (lo + hi) / 2))


# El terra on es camina (al món): davant dels mobles de la paret del fons, fins a la paret de la porta; la llitera és
# un forat (s'hi fa la volta).
WALK_MON = [(12, ZW - 14), (ARMARI[1] + 4, ZW - 14), (ARMARI[1] + 4, ZW - DESK[2] - 24), (DESK[1] + 6, ZW - DESK[2] - 24),
            (DESK[1] + 16, ZW - 14), (COUNTER[0] - 8, ZW - 14), (COUNTER[0] - 8, ZW - COUNTER[2] - 14),
            (XR - 70, ZW - COUNTER[2] - 14), (XR - 70, -200), (12, -200)]
_WALK = _talla([_p(x, z) for x, z in WALK_MON], _v_escala(1.2))
_FORAT = [_pl(lx, lz) for lx, lz in ((-8, LL[1] + 6), (LL[0] + 8, LL[1] + 6), (LL[0] + 8, -2), (-8, -2))]
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)

_DX = DESK
_FT = FILES_BOX

GEOMETRIA = {
    'things': {
        'porta': {'rect': _rect_mon((0, DOOR[2] + 14, DOOR[0] - 4), (0, 0, DOOR[1] + 4)), 'walk': _p(36, (DOOR[0] + DOOR[1]) / 2)},
        'boca': {'rect': _rect_mon((0, VOICE[1] + 10, VOICE[0] - 12), (0, VOICE[1] - 40, VOICE[0] + 14)),
                 'walk': _p(40, VOICE[0] - 10)},
        'armari': {'rect': _rect_mon((ARMARI[0], _y(PL.ARMARI[1]), ZW - ARMARI[2]), (ARMARI[1], 0, ZW - ARMARI[2]),
                                     (ARMARI[1], 0, ZW)),
                   'walk': _p((ARMARI[0] + ARMARI[1]) / 2 + 10, ZW - ARMARI[2] - 34)},
        'fitxes': {'rect': _rect_mon((_w(_FT[0]) + DSH, _DX[3] + 48, ZW - 40), (_w(_FT[2]) + DSH, _DX[3], ZW - 10)),
                   'walk': _p(_w((_FT[0] + _FT[2]) / 2) + DSH, ZW - _DX[2] - 40)},
        'llitera': {'rect': _rect_mon(*[_ll_P(lx, y, lz) for lx in (0, LL[0]) for lz in (0, LL[1]) for y in (0, LL_H[2] + 6)]),
                    'walk': _pl(LL[0] / 2, -34)},
        'cafetera': {'rect': _rect_mon((_w(PL.CAFE[0]) - 4, COUNTER[3] + 40, ZW - 12), (_w(PL.CAFE[2]) + 4, COUNTER[3], ZW - 12)),
                     'walk': _p(_w((PL.CAFE[0] + PL.CAFE[2]) / 2), ZW - COUNTER[2] - 34)},
    },
    'spawns': {'iri': _p(430, 140), 'vet': _p(150, 170),
               'capitana': _pl(LL[0] / 2, -30), 'tomas': _pl(LL[0] / 2, -30), 'nadia': _pl(LL[0] / 2, -30),
               'marcel': _pl(LL[0] / 2, -30),
               'bastida': SEU_BASTIDA, 'juana': SEU_JUANA},
    'walkable': _WALK,
    'forats': [_FORAT],
    'floorSquash': 0.42,
    # L'ombra de contacte: la llum dominant és el llum del mig (sobre la llitera).
    'characterShadow': {'enabled': True, 'color': '#06100e', 'alpha': 0.45, 'squash': 0.4, 'core': 0.6,
                        'light': {'x': _p(*LAMPS[1])[0], 'y': _p(*LAMPS[1])[1], 'stretch': 0.6, 'reach': 160}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    'characterLights': {
        'ambient': '#a0a498',
        'lights': [{'x': _p(lx, lz, HW - 30)[0], 'y': _p(lx, lz, HW - 30)[1], 'radius': 200, 'color': '#ffdc96',
                    'intensity': 0.6} for lx, lz in LAMPS],
    },
}
