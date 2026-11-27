"""
La sala de seguretat del BCMU (Escena 6, la Vet amb en Ballester). EN 3D (hd640/tres_d.py), a 1×.

Una càmera alta, a la dreta, que mira de biaix la cantonada del fons a l'esquerra:
  - a la paret de l'esquerra, en escorç, l'**ascensor** amb el marc de llautó i l'indicador «-1», i l'**estació del
    tub**;
  - a la paret del fons, la **paret de monitors** (5×3), que fa tota la llum de la sala (cian), el **calendari** de
    1994 i la **ràdio** d'en Ballester al seu suport;
  - la **taula de control** amb volum, separada de la paret i una mica girada: el tauler amb els teclats, el
    micròfon i els llums; damunt, el **got** d'aigua (a la vora, massa a la vora), la tassa «MILLOR AVI», la foto
    girada i la planta morta; i on van l'**entrepà**, el **clauer** i el **collaret**;
  - la **cadira** giratòria d'en Ballester davant la taula (s'hi passa per darrere);
  - primer pla: les taquilles fosques contra la paret de l'esquerra, un arxivador metàl·lic en silueta a la dreta
    i un feix de cables pel terra; la paperera de reixa al costat de la taula.

Tot el detall ve del dibuix pla de sempre (bcmu_seguretat_pla_comu.py), projectat; les coses de damunt la taula i la
cadira són el dibuix pla dret (sprites). Damunt de tot, la llum de Suma Zero (hd640/llum.py): els monitors, el bloom
i la corba de to.

El món: x a la dreta (0 = la paret de l'ascensor), y amunt (0 = el terra), z cap al fons (300 = la paret dels
monitors); 1 unitat = 1 píxel de sala a la distància on un personatge fa ≈111 px (escala 1).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from hd640 import llum
from hd.pix import Canvas, Light, W, H, hr
from hd.rooms.comu import _diff
from hd.rooms.exterior import fbm
from hd640.rooms import bcmu_seguretat_pla_comu as PL
from hd640.rooms.bcmu_seguretat_pla_comu import TILEF, CONSOLE, WATER, PLASTICR, CHROME, STEELB, CONCB
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
ZW = 300                                           # la paret dels monitors
FY0 = 4                                            # al dibuix pla, on comença la paret
HW = PL.FLOOR_Y - FY0                              # l'alçada de les parets: 196
XC = 165                                           # al dibuix pla, la cantonada: a l'esquerra, la paret de l'ascensor
LL = 520                                           # l'amplada de la paret llisa (fora del dibuix pla)
XR = W - XC + LL                                   # on s'acaba la paret del fons, a la dreta (fora de la pantalla)
DESK = (30, 320, 232, 264, 46, -0.1)              # la taula: x0, x1, z del davant, z del darrere, alçada, gir
CHAIR = (240, 196)                                 # la cadira (x, z dels peus)
CAB = (400, 160)                                   # l'arxivador del primer pla (x, z)


def _w(fx):
    """Una x del dibuix pla de la paret del fons → la x del món."""
    return fx - XC


def _wz(fx):
    """Una x del dibuix pla de la paret de l'ascensor → la z del món."""
    return ZW - XC + fx


def _y(fy):
    """Una y del dibuix pla (el terra, a 200) → l'alçada del món."""
    return PL.FLOOR_Y - fy


def _fw(fx, fy):
    if fx < XC:
        return (0, _y(fy), _wz(fx))
    return (_w(fx), _y(fy), ZW)


CAM = Camera(pos=(260, 175, -240), yaw=-0.24, pitch=0.16, f=500, centre=(320, 112))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)  # (la llum és la del món: la de l'Escena)
MON_C = (_w((PL.MON[0] + PL.MON[2]) / 2), _y((PL.MON[1] + PL.MON[3]) / 2), ZW - 16)   # el centre dels monitors
LIFT_C = (4, _y(40), _wz(110))                     # l'indicador de l'ascensor
RADIO_C = (_w(532), _y(136), ZW - 6)
LLUMS = [Llum(MON_C, 360, 3.0, power=1.3),                       # la paret de monitors
         Llum(LIFT_C, 90, 0.8, power=2.0),                       # l'indicador de l'ascensor
         Llum(RADIO_C, 40, 0.6, power=2.0)]                      # el llum de la ràdio


# ─── Les textures: el dibuix pla de sempre ───────────────────────────────────

LIGHT_TEX = Light(ambient=-0.5, vignette=None, floor_fade=None)
LIGHT_TEX.point(313, 75, r=307, k=2.2, squash=1.25, power=1.4)
LIGHT_TEX.point(112, 40, r=80, k=0.6, squash=1.0, power=2.0)
LIGHT_TEX.point(532, 133, r=40, k=0.5, squash=1.0, power=2.0)
LIGHT_TEX.point(45, 115, r=53, k=0.5, squash=1.0, power=2.0)


def _paret(t=0, views=None):
    """Les parets planes, de cara: plafons, l'ascensor, el tub, els monitors, el calendari i la ràdio."""
    cv = Canvas(light=LIGHT_TEX)
    PL.wall(cv)
    PL.tub_station(cv, 32, 85, 59, 144)
    PL.lift(cv)
    PL.monitors(cv, t, views)
    PL.calendar(cv)
    PL.radio(cv)
    return cv


@functools.lru_cache(maxsize=None)
def _paret_base():
    return _paret().img


@functools.lru_cache(maxsize=None)
def _llisa():
    cv = Canvas(light=LIGHT_TEX)
    PL.wall(cv)
    return cv.img


def _taula():
    """La consola plana, de cara (en surt el frontal)."""
    cv = Canvas(light=LIGHT_TEX, transparent=True)
    PL.desk(cv)
    return cv.img


def _coses(got=True):
    """Les coses de damunt la taula i la cadira, planes, sobre transparent (en surten els sprites)."""
    cv = Canvas(light=LIGHT_TEX, transparent=True)
    if got:
        PL.glass(cv)
    PL.mug(cv)
    PL.photo(cv)
    PL.dead_plant(cv)
    PL.chair(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _taula_base():
    return _taula()


@functools.lru_cache(maxsize=None)
def _coses_base():
    return _coses()


@functools.lru_cache(maxsize=None)
def _textures():
    return {'paret': _paret_base(), 'llisa': _llisa(), 'taula': _taula_base(), 'coses': _coses_base()}


FRONT_BOX = (195, PL.DESK_TOP + 3, 486, PL.FLOOR_Y + 1)            # el frontal de la consola, al dibuix pla
# les coses de damunt la taula: (retall del dibuix pla, x del peu al dibuix pla, z del món)
GOT = ((231, 139, 247, PL.DESK_TOP), 238, 250)
TASSA = ((375, 130, 392, PL.DESK_TOP - 3), 382, 254)
FOTO = ((394, 134, 414, PL.DESK_TOP), 402, 258)
PLANTA = ((446, 116, 482, PL.DESK_TOP), 462, 256)
CHAIR_BOX = (372, 168, 428, 241)
ENTREPA = ((261, 146, 290, PL.DESK_TOP + 1), 275, 248)
CLAUER = ((301, 146, 320, PL.DESK_TOP + 1), 311, 250)
COLLARET = ((335, 146, 360, PL.DESK_TOP + 1), 347, 250)


def _xt(fx):
    """Una x del dibuix pla de la taula → la x del món (la taula fa el mateix ample que al pla)."""
    return DESK[0] + (fx - FRONT_BOX[0])


def _sobre(fx, z):
    """El punt de damunt el tauler (al món) que correspon a una x del dibuix pla i una z del món."""
    x0, x1, zf, zb, dh, ang = DESK
    cx, cz = (x0 + x1) / 2, (zf + zb) / 2
    lx, lz = _xt(fx) - cx, z - cz
    c, s_ = math.cos(ang), math.sin(ang)
    return (cx + lx * c - lz * s_, dh, cz + lx * s_ + lz * c)


# ─── Les superfícies ────────────────────────────────────────────────────────

def _moqueta(s, t, P):
    """Rajoles de moqueta grises de 40, amb el pèl girat a quadres i gastades davant la taula i cap a l'ascensor."""
    x, z = P[0], P[2]
    tx, tz = math.floor(x / 40), math.floor(z / 40)
    if x % 40 < 1.0 or z % 40 < 1.0:
        return 2.2
    pile = 0.3 if (tx + tz) % 2 and int(x + z) % 3 == 0 else 0
    n = (hr(tx, tz, 8) - 0.5) * 0.5 + (fbm(x / 40, z / 30, 3) - 0.5) * 0.5
    worn = max(0.0, 1 - math.hypot((x - 200) / 90, (z - 200) / 40)) * 0.7 + max(0.0, 1 - math.hypot(x / 70, (z - 245) / 50)) * 0.5
    return 3.2 + n + pile + worn


def escena(cv, tex, estat=frozenset()):
    """Tota la sala, de lluny a prop. `estat`: 'got_trencat'. → l'Escena (qui ha pintat què)."""
    e = Escena(cv, CAM, LLUMS, ambient=-1.0)
    zn = CAM.pos[2] + 60
    paret, llisa, taula, coses = tex['paret'], tex['llisa'], tex['taula'], tex['coses']
    # el sostre, baix i fosc
    e.quad('sostre', (0, HW, zn), (XR, HW, zn), (XR, HW, ZW), (0, HW, ZW), ramp=CONCB, lvl=0.8, dues_cares=True)
    # la paret de l'ascensor (x = 0): el dibuix pla (x 0..165) a tocar de la cantonada; cap a la càmera, plafons
    e.quad('paret_esq_prop', (0, HW, zn), (0, HW, ZW - XC), (0, 0, ZW - XC), (0, 0, zn),
           tex=(llisa, (0, FY0, min(W, ZW - XC - zn), PL.FLOOR_Y)))
    e.quad('paret_esq', (0, HW, ZW - XC), (0, HW, ZW), (0, 0, ZW), (0, 0, ZW - XC), tex=(paret, (0, FY0, XC, PL.FLOOR_Y)))
    # la paret del fons (z = 300): el dibuix pla (x 165..640) i, a la dreta, més plafons
    e.quad('paret_fons', (0, HW, ZW), (W - XC, HW, ZW), (W - XC, 0, ZW), (0, 0, ZW), tex=(paret, (XC, FY0, W, PL.FLOOR_Y)))
    e.quad('paret_fons_dreta', (W - XC, HW, ZW), (XR, HW, ZW), (XR, 0, ZW), (W - XC, 0, ZW),
           tex=(llisa, (100, FY0, 100 + LL, PL.FLOOR_Y)) if LL <= W - 100 else (llisa, (0, FY0, LL, PL.FLOOR_Y)))
    # el terra
    e.quad('terra', (0, 0, ZW), (XR, 0, ZW), (XR, 0, zn), (0, 0, zn), ramp=TILEF, lvl=_moqueta)
    # la claror dels monitors al terra, davant la taula, i el reflex a la paret de l'ascensor
    mx = MON_C[0]
    e.claror((mx - 200, 0.3, ZW), (mx + 200, 0.3, ZW), (mx + 200, 0.3, ZW - 260), (mx - 200, 0.3, ZW - 260),
             (60, 200, 210), lambda s, t: 0.20 * max(0.0, 1 - abs(s - 200) / 200) * max(0.0, 1 - t / 260))
    e.claror((0.5, HW, ZW - 160), (0.5, HW, ZW), (0.5, 0, ZW), (0.5, 0, ZW - 160), (80, 210, 220),
             lambda s, t: 0.10 * max(0.0, s / 160) * max(0.0, 1 - abs(t - 80) / 110))
    # la foscor dels racons i del sostre
    e.foscor('racons', (0, 0.5, ZW), (XR, 0.5, ZW), (XR, 0.5, zn), (0, 0.5, zn),
             lambda s, t: max(0.55 * max(0.0, 1 - t / 30), 0.5 * max(0.0, 1 - s / 30)))
    e.foscor('cantonada', (0, HW, ZW - 0.5), (60, HW, ZW - 0.5), (60, 0, ZW - 0.5), (0, 0, ZW - 0.5),
             lambda s, t: 0.5 * max(0.0, 1 - s / 60))
    e.foscor('cantonada2', (0.5, HW, ZW - 60), (0.5, HW, ZW), (0.5, 0, ZW), (0.5, 0, ZW - 60),
             lambda s, t: 0.5 * max(0.0, 1 - (60 - s) / 60))
    e.foscor('sostre_fosc', (0, HW - 0.5, ZW - 0.6), (XR, HW - 0.5, ZW - 0.6), (XR, 0, ZW - 0.6), (0, 0, ZW - 0.6),
             lambda s, t: 0.4 * max(0.0, 1 - t / 40))
    # els cables pel terra: de la taula a la paret, i el de la ràdio
    for ramp, lv, pts in (
            (PLASTICR, 1.6, [(_w(300), 0.8, ZW - 38), (200, 0.8, ZW - 26), (120, 0.8, ZW - 14), (80, 0.8, ZW - 3)]),
            (PLASTICR, 1.4, [(DESK[1] - 6, 0.8, ZW - 40), (DESK[1] + 16, 0.8, ZW - 22), (RADIO_C[0] - 6, 0.8, ZW - 4)])):
        e.cable('cables', pts, ramp, lv, gruix=2.0)
    # la taula de control: una mica girada, amb el frontal del dibuix pla i el tauler amb la claror dels monitors
    x0, x1, zf, zb, dh, ang = DESK
    cx, cz = (x0 + x1) / 2, (zf + zb) / 2
    e.foscor('ombra_taula', (x0 - 10, 0.6, zb + 4), (x1 + 12, 0.6, zb + 4), (x1 + 12, 0.6, zf - 22), (x0 - 10, 0.6, zf - 22),
             lambda s, t: 0.6 * min(1.0, max(0.0, (zb - zf + 26 - t) / 18)))

    def tauler(s, t, P):
        v = 3.2 + (fbm(s / 40, t / 8, 11) - 0.5) * 0.4 + 1.2 * max(0.0, 1 - abs(s - 130) / 170) * (t / (zb - zf))
        if t < 1.2:
            v += 1.6                                                      # el cantell, que agafa la llum
        return v
    e.caixa_girada('taula', cx, cz, x1 - x0, zb - zf, dh, ang, CONSOLE, 1.8,
                   cares={'davant': {'tex': (taula, FRONT_BOX)}, 'dalt': {'ramp': CONSOLE, 'lvl': tauler},
                          'esquerra': {'ramp': CONSOLE, 'lvl': lambda s, t, P: 2.4 - (0.6 if int(s) % 8 == 0 else 0)},
                          'dreta': {'ramp': CONSOLE, 'lvl': 1.4}})
    # el que hi ha damunt el tauler: els teclats, els llums, el micròfon, la tassa, la foto, la planta
    for kx in (213, 360):
        P0 = _sobre(kx + 20, zf + 12)
        e.caixa_girada('taula', P0[0], P0[2], 40, 12, 2.0, ang, CONSOLE, 3.0, y0=dh,
                       cares={'dalt': {'ramp': CONSOLE, 'lvl': lambda s, t, P: 5.0 if int(s) % 3 == 1 and int(t) % 3 == 1 else 3.0}})
    for i in range(10):
        bx = 261 + i * 8
        col = [(60, 220, 120), (240, 190, 60), (240, 70, 60)][int(hr(i, 2) * 3)]
        P0 = _sobre(bx, zf + 6)
        e.quad('taula', (P0[0] - 1.2, dh + 0.3, P0[2] + 1.2), (P0[0] + 1.2, dh + 0.3, P0[2] + 1.2),
               (P0[0] + 1.2, dh + 0.3, P0[2] - 1.2), (P0[0] - 1.2, dh + 0.3, P0[2] - 1.2), ramp=[col], lvl=0)
    mb = _sobre(430, zf + 10)                                            # el micròfon de peu
    e.caixa_girada('taula', mb[0], mb[2], 14, 8, 2.5, ang, CHROME, 2.4, y0=dh)
    e.tub('taula', (mb[0] - 2, dh + 2.5, mb[2]), (mb[0] + 2, dh + 18, mb[2] + 2), 0.9, CHROME, 3.0)
    e.tub('taula', (mb[0] + 2, dh + 18, mb[2] + 2), (mb[0] + 2.5, dh + 22, mb[2] + 2), 2.4, PLASTICR, 2.4)
    if 'got_trencat' not in estat:
        _sobre_sprite(e, coses, GOT)
    for item in (TASSA, FOTO, PLANTA):
        _sobre_sprite(e, coses, item)
    if 'got_trencat' in estat:
        _got_trencat(e)
    # la cadira d'en Ballester, davant la taula (el dibuix pla, dret), amb la seva ombra
    chx, chz = CHAIR
    e.foscor('ombra_cadira', (chx - 24, 0.7, chz + 16), (chx + 24, 0.7, chz + 16), (chx + 24, 0.7, chz - 16),
             (chx - 24, 0.7, chz - 16), lambda s, t: 0.6 * max(0.0, 1 - ((s - 24) / 24) ** 2 - ((t - 16) / 16) ** 2) * 1.6)
    e.sprite('cadira', coses.crop(CHAIR_BOX), (400 - CHAIR_BOX[0], 236 - CHAIR_BOX[1]), (chx, 0, chz))
    # primer pla: l'arxivador metàl·lic en silueta, a baix a la dreta, i un feix de cables
    FOSC = [(3, 4, 7), (7, 9, 14), (12, 14, 21), (18, 21, 30), (26, 30, 40), (36, 40, 52)]
    ax, az = CAB
    e.caixa_girada('primer_pla', ax, az, 60, 70, 110, -0.25, FOSC, 1.4,
                   cares={'dalt': {'ramp': FOSC, 'lvl': lambda s, t, P: 2.4 + (0.6 if s < 2 else 0)},
                          'esquerra': {'ramp': FOSC, 'lvl': lambda s, t, P: 1.8 + (1.2 if int(t) % 36 < 2 else 0)
                                       + (0.8 if int(t) % 36 == 16 and 20 < s < 50 else 0)},
                          'davant': {'ramp': FOSC, 'lvl': lambda s, t, P: 1.2 + (0.8 if int(t) % 36 < 2 else 0)}})
    e.cable('primer_pla', [(150, 0.8, 70), (230, 0.8, 100), (300, 0.8, 84), (380, 0.8, 120)],
            [(3, 4, 7), (10, 12, 18), (20, 24, 32), (34, 38, 48)], 2.0, gruix=3.0)
    e.cable('primer_pla', [(170, 0.8, 60), (250, 0.8, 80), (340, 0.8, 70)],
            [(3, 4, 7), (10, 12, 18), (20, 24, 32), (34, 38, 48)], 1.6, gruix=2.4)
    # les taquilles, contra la paret de l'esquerra, a prop (fosques): portes amb reixetes, tiradors i etiquetes
    def taquilla(s, t, P):
        u = s % 25
        if u < 1.2:
            return 0.6                                                  # la junta entre portes
        v = 2.2 + (0.6 if u < 3 else 0) - (0.5 if u > 23 else 0)
        if 10 < t < 30 and 6 < u < 20 and int(t) % 3 == 0:
            return 0.8                                                  # la reixeta
        if 70 < t < 80 and 18 < u < 21:
            return 3.6                                                  # el tirador
        if 40 < t < 46 and 6 < u < 16:
            return 3.8 if hr(int(s // 25), 4) > 0.4 else 1.0             # l'etiqueta
        return v
    TAQ = [(4, 6, 10), (10, 13, 20), (17, 21, 32), (26, 31, 45), (36, 42, 58), (48, 56, 74), (70, 78, 96)]
    e.caixa('primer_pla', 0, 34, 0, 150, -60, 95, TAQ, 1.4,
            cares={'dreta': {'ramp': TAQ, 'lvl': taquilla}, 'dalt': {'ramp': TAQ, 'lvl': 1.2},
                   'davant': {'ramp': TAQ, 'lvl': lambda s, t, P: 1.0 + (0.8 if s > 32 else 0)}})
    e.foscor('ombra_taquilles', (34, 0.6, 95), (60, 0.6, 95), (60, 0.6, -60), (34, 0.6, -60),
             lambda s, t: 0.55 * max(0.0, 1 - s / 26))
    # la paperera de reixa, al costat de la taula
    px_, pz_ = DESK[1] + 22, ZW - 26
    e.caixa('paperera', px_ - 8, px_ + 8, 0, 22, pz_ - 8, pz_ + 8, STEELB, 1.6,
            cares={'davant': {'ramp': STEELB, 'lvl': lambda s, t, P: 2.6 if int(s) % 3 == 0 or int(t) % 3 == 0 else 0.6},
                   'esquerra': {'ramp': STEELB, 'lvl': lambda s, t, P: 2.0 if int(s) % 3 == 0 or int(t) % 3 == 0 else 0.4},
                   'dalt': {'ramp': [(30, 30, 34), (90, 86, 70), (170, 160, 130)], 'lvl': 1.6}})
    return e


def _sobre_sprite(e, taula, item, sid='taula'):
    """Una cosa de damunt la taula: el retall del dibuix pla, dret, amb el peu al tauler."""
    box, fx, z = item
    img = taula.crop(box)
    if item is GOT:                                                     # (el vidre, sense la llum de la sala, enlluerna)
        img = img.point(lambda c: int(c * 0.72))
        img.putalpha(taula.crop(box).getchannel('A'))
    e.sprite(sid, img, (fx - box[0], box[3] - box[1]), _sobre(fx, z))


def _got_trencat(e):
    """El got, trencat: el cul del got a la taula, el toll, l'aigua que regalima pel frontal, el bassal i els vidres."""
    x0, x1, zf, zb, dh, ang = DESK
    gx, _, gz = _sobre(238, zf + 6)
    e.quad('got_trencat', (gx - 12, dh + 0.3, gz + 8), (gx + 12, dh + 0.3, gz + 8), (gx + 12, dh + 0.3, gz - 8),
           (gx - 12, dh + 0.3, gz - 8), ramp=WATER, lvl=lambda s, t, P: 1.0 + (0.8 if int(s + t) % 5 == 0 else 0),
           forma=lambda s, t: ((s - 12) / 12) ** 2 + ((t - 8) / 8) ** 2 < 1)
    e.caixa('got_trencat', gx - 3, gx + 3, dh, dh + 4, gz + 1, gz + 6, WATER, 3.4)
    # el regalim pel frontal (z del davant de la taula a aquella x) i el bassal a terra
    fz = zf + (gx - (x0 + x1) / 2) * math.sin(ang) - 0.6
    e.quad('got_trencat', (gx + 5, dh, fz), (gx + 5.8, dh, fz), (gx + 5.8, 12, fz), (gx + 5, 12, fz), ramp=WATER, lvl=1.4)
    e.quad('got_trencat', (gx - 10, 0.5, fz - 2), (gx + 22, 0.5, fz - 2), (gx + 22, 0.5, fz - 22), (gx - 10, 0.5, fz - 22),
           ramp=WATER, lvl=lambda s, t, P: 0.6 + (0.8 if int(s) % 6 == 0 else 0),
           forma=lambda s, t: ((s - 16) / 16) ** 2 + ((t - 10) / 10) ** 2 < 1)
    for i in range(16):
        vx = gx - 30 + hr(i, 6) * 60
        vz = fz - 8 - hr(i, 7) * 40
        e.quad('got_trencat', (vx, 0.6, vz + 1), (vx + 1.6, 0.6, vz + 1), (vx + 1.6, 0.6, vz), (vx, 0.6, vz),
               ramp=[(120, 170, 180), (200, 236, 240), (230, 250, 252)], lvl=i % 3)


# ─── Composició i llum ──────────────────────────────────────────────────────

def _proj(P):
    u, v, _ = CAM.projecta(P)
    return u, v


def _fx():
    mx, my = _proj(MON_C)
    lx, ly = _proj(LIFT_C)
    light = [llum.wash(mx, my + 20, 280, (80, 220, 230), k=0.9, air=0.05, squash=1.0),      # els monitors, cian
             llum.wash(lx, ly, 70, (255, 170, 80), k=0.6, air=0.04, squash=1.0)]             # l'indicador
    tone = [llum.grade(contrast=1.12, pivot=40, sat=1.2, lift=(2, 4, 10))]
    bloom = [llum.bloom(thr=120)]
    return light, bloom, tone


def _render(estat=frozenset(), tex=None):
    cv = Canvas(light=LIGHT)
    e = escena(cv, tex or _textures(), estat)
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)    # la barra de verbs: negre
    return cv.img, e


@functools.lru_cache(maxsize=None)
def _base():
    return _render()


def _amb_llum(img, bloom=True):
    light, bl, tone = _fx()
    return llum.apply(img, light + (bl if bloom else []) + tone)


@functools.lru_cache(maxsize=None)
def _base_llum():
    return _amb_llum(_base()[0])


def bg(cv):
    cv.img.paste(_base_llum())
    cv.P = cv.img.load()


def _fotograma(capes):
    """El fons amb unes capes damunt, amb la llum, menys el fons amb la llum."""
    img, _ = _base()
    img = img.copy()
    for c in capes:
        img.alpha_composite(c)
    return _diff(_amb_llum(img), _base_llum())


def _drets(img, peu_img, peu):
    """Un dibuix pla dret (una cosa de damunt la taula), en una capa, amb una ombreta de contacte."""
    from PIL import Image
    from pixels import nearest
    k = CAM.escala(peu)
    u, v, _ = CAM.projecta(peu)
    w, h = max(1, round(img.width * k)), max(1, round(img.height * k))
    im = nearest(img, (w, h)) if k >= 1 else img.resize((w, h), Image.Resampling.BOX)
    ox, oy = round(u - peu_img[0] * k), round(v - peu_img[1] * k)
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    dst = out.load()
    rx, ry = w * 0.6, max(1.5, w * 0.14)
    for Y in range(int(v - ry), int(v + ry) + 1):
        for X in range(int(u - rx), int(u + rx) + 1):
            d = ((X - u) / rx) ** 2 + ((Y - v) / ry) ** 2
            if d < 1 and 0 <= X < W and 0 <= Y < H:
                dst[X, Y] = (4, 6, 10, int(140 * (1 - d) ** 0.7))
    out.alpha_composite(im, (ox, oy))
    return out


def _prop_sobre(draw_fn, item):
    """Un objecte de damunt la taula (l'entrepà, el clauer, el collaret): el dibuix pla, dret al tauler."""
    def draw(cv):
        c = Canvas(light=LIGHT_TEX, transparent=True)
        draw_fn(c)
        box, fx, z = item
        cv.img.alpha_composite(_fotograma([_drets(c.img.crop(box), (fx - box[0], box[3] - box[1]), _sobre(fx, z))]))
        cv.P = cv.img.load()
    return draw


def _prop_got_trencat(cv):
    tex = {**_textures(), 'coses': _coses(got=False)}
    img, _ = _render(frozenset({'got_trencat'}), tex)
    cv.img.alpha_composite(_diff(_amb_llum(img), _base_llum()))
    cv.P = cv.img.load()


PROPS = {'entrepa': _prop_sobre(PL.entrepa, ENTREPA), 'clauer': _prop_sobre(PL.clauer, CLAUER),
         'collaret': _prop_sobre(PL.collaret, COLLARET), 'got_trencat': _prop_got_trencat,
         'collaret_taula': _prop_sobre(PL.collaret_taula, COLLARET)}


# ─── Animació: els monitors canvien de pla, i un fa neu ────────────────────

def _frames():
    _, e = _base()
    out = []
    for t in range(8):
        views = list(PL.VIEWS)
        views[13] = 'neu'
        if t >= 4:                                                       # canvien de càmera
            views[2], views[9] = 'escala', 'buida'
            views[11] = 'passadis'
        if t in (3, 7):
            views[6] = 'neu'
        cv = Canvas(light=LIGHT_TEX, img=_paret_base().copy())
        for i, kind in enumerate(views):
            a, b, c, d = PL._cell(i)
            PL.view(cv, i, kind, t)
            PL._glass(cv, a, b, c, d)
        out.append(_fotograma([e.capa(cv.img, {'paret_fons'})]))
    return out


ANIMS = {'monitors': {'frames': _frames, 'frameDuration': 260}}


# ─── Capes del davant ───────────────────────────────────────────────────────

def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


# El primer pla (sempre davant) i la cadira (qui hi passa per darrere, hi queda darrere).
FRONT = [
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20},
    {'id': 'davant_cadira', 'mask': _amo({'cadira'}), 'baseline': _p(CHAIR[0], CHAIR[1])[1], 'zIndex': 20},
]


# ─── Geometria (coordenades de sala, projectades) ────────────────────────────

def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


def _rect_pla(x0, y0, x1, y1):
    """Un rectangle del dibuix pla de les parets → el rectangle de pantalla que ocupa (amb tots els cantons)."""
    return _rect_mon(*[_fw(x, y) for x in (x0, x1) for y in (y0, y1)] + ([_fw(XC, y0), _fw(XC, y1)] if x0 < XC < x1 else []))


def _rect_sobre(item, marge=2):
    """El rectangle de pantalla d'una cosa de damunt la taula."""
    box, fx, z = item
    P = _sobre(fx, z)
    k = CAM.escala(P)
    u, v, _ = CAM.projecta(P)
    return (round(u - (fx - box[0]) * k) - marge, round(v - (box[3] - box[1]) * k) - marge,
            round(u + (box[2] - fx) * k) + marge, round(v) + marge)


def _talla(poly, a, b, c):
    """Retalla el polígon (de pantalla) pel semiplà a·u + b·v + c ≥ 0."""
    out = []
    for P, Q in zip(poly, poly[1:] + poly[:1]):
        fp, fq = a * P[0] + b * P[1] + c, a * Q[0] + b * Q[1] + c
        if fp >= 0:
            out.append(P)
        if (fp >= 0) != (fq >= 0):
            k = fp / (fp - fq)
            out.append((P[0] + (Q[0] - P[0]) * k, P[1] + (Q[1] - P[1]) * k))
    return out


def _escala_a(v):
    """L'escala d'un personatge amb els peus a la y de pantalla `v` (al terra, la profunditat només depèn de v)."""
    lo, hi = -300.0, 2000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.projecta((260, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((260, 0, (lo + hi) / 2))


def _v_escala(k):
    lo, hi = 0.0, float(BOTTOM)
    for _ in range(40):
        m = (lo + hi) / 2
        if _escala_a(m) < k:
            lo = m
        else:
            hi = m
    return lo


# El terra on es camina (al món): davant la taula i l'ascensor, fins a l'arxivador; retallat per la pantalla i per on
# un personatge passaria d'escala 1,2.
_ZF = DESK[2] - 10
WALK_MON = [(10, 288), (24, 288), (24, _ZF + 4), (DESK[1] + 14, _ZF - 14), (DESK[1] + 30, 290), (560, 290),
            (560, CAB[1] + 50), (CAB[0] - 50, CAB[1] + 40), (CAB[0] - 60, -100), (44, -100), (44, 110), (10, 120)]
V_MAX = _v_escala(1.2)
_WALK = [_p(x, z) for x, z in WALK_MON]
for _a, _b, _c in ((1, 0, -4), (-1, 0, W - 5), (0, -1, V_MAX)):
    _WALK = _talla(_WALK, _a, _b, _c)
_WALK = [(round(u), round(v)) for u, v in _WALK]
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)


def _sobre_walk(fx):
    """On es posa un personatge per agafar una cosa de damunt la taula: davant el tauler, a aquella x."""
    P = _sobre(fx, DESK[2] - 26)
    return _p(P[0], P[2])


GEOMETRIA = {
    'things': {
        'tub': {'rect': _rect_pla(30, 83, 66, 146), 'walk': _p(16, _wz(46))},
        'ascensor': {'rect': _rect_pla(70, 30, 150, 200), 'walk': _p(30, _wz(110))},
        'monitors': {'rect': _rect_pla(*PL.MON), 'walk': _p(_w(300), DESK[2] - 30)},
        'got': {'rect': _rect_sobre(GOT), 'walk': _sobre_walk(GOT[1])},
        'entrepa': {'rect': _rect_sobre(ENTREPA), 'walk': _sobre_walk(ENTREPA[1])},
        'clauer': {'rect': _rect_sobre(CLAUER), 'walk': _sobre_walk(CLAUER[1])},
        'collaret': {'rect': _rect_sobre(COLLARET), 'walk': _sobre_walk(COLLARET[1])},
        'radio': {'rect': _rect_pla(517, 108, 547, 160), 'walk': _p(RADIO_C[0] - 4, ZW - 40)},
    },
    # En Ballester, a la punta de la taula: qui li parla s'hi posa a la dreta, i més enllà l'arxivador la tapava.
    'spawns': {'vet': _p(120, 150), 'ballester': _p(DESK[1] - 10, DESK[2] - 32)},
    'walkable': _WALK,
    'floorSquash': 0.45,
    # L'ombra de contacte: la llum dominant és la paret de monitors (el punt del terra sota el centre); cap avall.
    'characterShadow': {'enabled': True, 'color': '#04080e', 'alpha': 0.5, 'squash': 0.42, 'core': 0.6,
                        'light': {'x': _p(MON_C[0], ZW - 10)[0], 'y': _p(MON_C[0], ZW - 10)[1], 'stretch': 0.7,
                                  'reach': 200}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    'characterLights': {
        'ambient': '#6c7890',                                                           # sala fosca, blavosa
        'lights': [
            {'x': _p(MON_C[0], MON_C[2], MON_C[1])[0], 'y': _p(MON_C[0], MON_C[2], MON_C[1])[1], 'radius': 320,
             'color': '#50dce6', 'intensity': 1.0},                                     # els monitors
            {'x': _p(LIFT_C[0], LIFT_C[2], LIFT_C[1])[0], 'y': _p(LIFT_C[0], LIFT_C[2], LIFT_C[1])[1], 'radius': 90,
             'color': '#ffaa50', 'intensity': 0.5},                                     # l'indicador de l'ascensor
        ],
    },
}
