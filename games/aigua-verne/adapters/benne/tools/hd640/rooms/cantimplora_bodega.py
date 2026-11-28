"""
Aigua Verne — la bodega de la Cantimplora (sala de prop, P: persones de ≈100 px). EN 3D.

La panxa de la nau cisterna, vista de biaix i una mica des de dalt amb la mateixa càmera que el pont (hd640/tres_d.py):
es veu la cantonada del fons a l'esquerra. A la paret de l'esquerra, que fuig, l'escala de mà que puja al pont per la
boca del sostre i, a la cantonada, un dels dipòsits rodons ajagut (el cilindre, amb la tapa del davant i la portella
oberta on dorm en Diu). A terra, davant del dipòsit, l'espai de càrrega pintat de groc, sota la politja del carril de
la grua. A la paret del fons: la rampa oberta (amb els brancals gruixuts), les argolles de l'últim barril, el panell
del motor, el quadre elèctric, el moble de calaixos de la Vet, el fogó amb la cafetera, la nevera i el tauler de
suro; i la granota d'en Tomàs penjada. El banc d'en Tomàs, amb la carmanyola, és separat de la paret i girat: s'hi
passa per darrere. Tres bombetes de filament fan bassals de llum càlida (la que puja per l'escala i es veu al pont).
Primer pla: una quaderna amb dues canonades a la dreta i un parell de caixes a baix a l'esquerra, tallades per la vora.

Tot el detall ve de la bodega plana de sempre (cantimplora_bodega_pla_comu.py): la paret, la tapa del dipòsit i els
davants dels mobles es dibuixen de cara com abans i es projecten com a textures. Els decorats i les animacions també.

PROPS: `barril` (dret contra la paret, fermat a les argolles) · decorats `llum_terra2`, `llum_aqua`, `llum_ferrum`,
`llum_verdant` (el planeta per la rampa i la claror de color que entra pel terra), `motor_obert`, `sacs_carregats`
(els tres sacs a l'espai de càrrega) i `diu_carmanyola` (en Diu damunt la carmanyola, al banc).
ANIMS: `vapor` (la cafetera), `bombeta` (la bombeta del mig, que fa pampallugues de tant en tant).

El món: x a la dreta (0 = la paret de l'escala), y amunt (0 = el terra), z cap al fons (300 = la paret de la rampa);
1 unitat = 1 píxel de sala a la distància on un personatge fa 100 px (escala 1). Al dibuix pla, x_pla = x + OFF.
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from PIL import Image

from hd.pix import Light, W, H, hr
from hd.rooms.comu import _diff
from hd.rooms.exterior import fbm
from hd.personatges import diu
from hd640.rooms import cantimplora_bodega_pla_comu as PL
from hd640.rooms.nau_comu import OLIVE, SAFETY, STEELN, DECKP, BLACKT, REDK, WOODB
from hd640.tres_d import Camera, Escena, Llum, llum_personatges

# Art a 1× (640×360), com el pont: les textures (la bodega plana) també són a 1×.
from hd.pix import Canvas  # noqa: E402,F811

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
ZW = 300                                           # la paret del fons (la de la rampa)
HW = 200                                           # l'alçada de les parets (el dibuix pla fa 200 fins al terra)
FY = PL.FLOOR_Y                                    # (200: al pla, on la paret toca el terra)
OFF = 40                                           # x del dibuix pla = x del món + OFF
TANK = (66, 76, 50, 196)                           # el dipòsit ajagut: x i y de l'eix, radi, z de la tapa
LADDER_Z = (112, 156)                              # els dos muntants de l'escala (contra la paret de l'esquerra)
RAMP_X = (PL.RAMP[0] - OFF, PL.RAMP[2] - OFF)      # l'obertura de la rampa (x del món) …
RAMP_H = FY - PL.RAMP[1]                           # … i l'alçada
BARREL = (PL.BARREL[0] - OFF, 288)                 # el barril: x, z (dret contra la paret)
CON = (PL.COUNTER[0] - OFF - 2, PL.COUNTER[2] - OFF + 2, FY - PL.COUNTER[1], 272)    # el fogó: x0, x1, alçada, z
CAL = (PL.DRAWERS[0] - OFF - 4, PL.DRAWERS[2] - OFF + 4, FY - PL.DRAWERS[1], 274)    # el calaix de la Vet
FRI = (PL.FRIDGE[0] - OFF - 1, PL.FRIDGE[2] - OFF + 1, FY - PL.FRIDGE[1], 270)       # la nevera
BENCH = (470, 206, 0.42)                           # el banc d'en Tomàs: centre (x, z) i gir
CARGO = (54, 150, 134, 186)                        # l'espai de càrrega: x0, x1, z0, z1
LAMPS = tuple((x - OFF, 214) for x, _ in PL.LAMPS)  # les bombetes (x, z): a sobre de les del pla
POLITJA = (96, 166)                                # la politja, al carril de la grua (x, z)

CAM = Camera(pos=(320, 190, -190), yaw=-0.17, pitch=0.17, f=360, centre=(320, 66))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)  # (la llum és la del món: la de l'Escena)


def _llums(apagada=None):
    return [Llum((x, 180, z), 240, 1.7, power=1.4) for i, (x, z) in enumerate(LAMPS) if i != apagada] + [
        Llum(((RAMP_X[0] + RAMP_X[1]) / 2, 50, ZW + 10), 170, 0.8, power=1.5),   # la claror de fora, per la rampa
        Llum((14, 196, 134), 90, 0.6, power=1.6),                                # la boca del sostre (el pont)
        Llum((CON[0] + 20, 50, CON[3] - 4), 50, 0.5, power=1.8),                 # el foc del fogó
    ]


# ─── Les textures: la bodega plana de sempre ────────────────────────────────

def _paret_pla(cv, steam=None):
    PL.walls(cv)
    PL.rampa(cv)
    PL.argolles(cv)
    PL.motor(cv)
    PL.fusibles(cv)
    PL.calaix(cv)
    PL.tauler(cv)
    PL.cuina(cv, steam)
    PL.nevera(cv)
    PL.granota(cv)


@functools.lru_cache(maxsize=None)
def _paret(steam=None):
    cv = Canvas(light=PL.LIGHT)
    _paret_pla(cv, steam)
    return cv.img


@functools.lru_cache(maxsize=None)
def _tapa():
    cv = Canvas(light=PL.LIGHT)
    PL.walls(cv)
    PL.diposit(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _bombeta(on=True):
    cv = Canvas(light=PL.LIGHT, transparent=True)
    PL.bulb(cv, 40, 40, cable=0, on=on)
    return cv.img.crop((0, 0, 80, 60)), (40, 40)


# ─── Les superfícies ────────────────────────────────────────────────────────

def _planxa(lvl0, pw=60, ph=44, seed=21):
    """Paret de planxa procedural (on el dibuix pla no arriba): plaques, juntes, reblons i rovell."""
    def L(s, t, P):
        px, py = int(s // pw), int(t // ph)
        val = lvl0 + (hr(px, py, seed) - 0.5) * 0.7 + (fbm(s / 26, t / 18, seed) - 0.5) * 0.9
        if s % pw < 1.2 or t % ph < 1.2:
            val -= 1.6
        elif s % pw < 2.4 or t % ph < 2.4:
            val += 0.7
        if (t % ph) > ph - 5 and (s % 8) < 1.5:
            val += 1.6
        if fbm(s / 14, t / 30, seed + 5) > 0.68:
            val -= 0.9                                             # regalims de rovell
        return val
    return L


def _terra(s, t, P):
    """Xapa estriada vista des de dalt (com al pont), més bruta: juntes, taques de greix i l'espai de càrrega."""
    x, z = P[0], P[2]
    gx, gz = int(x // 7), int(z // 7)
    lx, lz = x - (gx + 0.5) * 7, z - (gz + 0.5) * 7
    d = (lx + lz) if (gx + gz) % 2 else (lx - lz)
    stud = abs(d) < 1.0 and abs(lx - lz if (gx + gz) % 2 else lx + lz) < 5.0
    v = 2.8 + (fbm(x / 70, z / 40, 24) - 0.5) * 1.3 + (hr(int(x) // 3, int(z) // 3, 24) - 0.5) * 0.4
    if stud:
        v += 1.1
    if x % 128 < 1.2 or z % 96 < 1.2:
        v -= 1.8
    for cx, cz, r in ((380, 236, 22), (170, 200, 16), (470, 150, 14), (250, 128, 12)):     # taques de greix
        if ((x - cx) / r) ** 2 + ((z - cz) / (r * 0.7)) ** 2 < 1 + (fbm(x / 6, z / 6, 3) - 0.5):
            v -= 0.9
    return v


def _calcomania(e, sid, x0, x1, z0, z1, ramp, fn):
    """Una calcomania pintada a terra: només els punts (x, z) on `fn` torna un nivell (None: no es pinta)."""
    def forma(s, t):
        return fn(x0 + s, z1 - t) is not None

    def L(s, t, P):
        v = fn(P[0], P[2])
        return 0 if v is None else v
    e.quad(sid, (x0, 0.3, z1), (x1, 0.3, z1), (x1, 0.3, z0), (x0, 0.3, z0), ramp=ramp, lvl=L, forma=forma)


def _diposit(e, tex):
    """El dipòsit ajagut a la cantonada: el cilindre (facetes al llarg de z), la tapa del davant amb el dibuix pla
    (la portella, el 5, «BUIT») i el bressol."""
    cx, cy, r, z0 = TANK
    # el bressol (primer: el cilindre el tapa per dalt): dues potes de planxa sota el cilindre
    for zc in (ZW - 22, z0 + 16):
        e.caixa('diposit', cx - 34, cx + 34, 0, cy - r + 10, zc - 5, zc + 5, OLIVE, 2.6,
                cares={'davant': {'ramp': OLIVE, 'lvl': lambda s, t, P: 2.8 - (1.4 if t > 22 else 0)},
                       'dalt': {'ramp': OLIVE, 'lvl': 3.8}})
    n = 28
    for k in range(n):
        a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        P = lambda a, z: (cx + r * math.cos(a), cy + r * math.sin(a), z)  # noqa: E731
        am = (a0 + a1) / 2
        base = 2.6 + math.sin(am) * 1.2 + math.cos(am) * 0.4           # (la llum ve de dalt i de la dreta)
        if abs(am - 1.15) < 0.12:
            base += 1.4                                               # la lluentor de la bombeta, al llom

        def L(s, t, Pw, base=base):
            v = base + (fbm(Pw[2] / 20, Pw[1] / 12, 25) - 0.5) * 0.8
            if abs(Pw[2] - (z0 + 6)) < 1.5 or abs(Pw[2] - 262) < 1.5:
                v += 1.2                                              # els cèrcols
            elif abs(Pw[2] - (z0 + 8)) < 1.2 or abs(Pw[2] - 264) < 1.2:
                v -= 1.0
            if (Pw[2] - z0) % 9 < 1.4 and abs(Pw[2] - 262) < 4:
                v += 1.0                                              # reblons
            return v
        e.quad('diposit', P(a1, ZW), P(a0, ZW), P(a0, z0), P(a1, z0), ramp=OLIVE, lvl=L)
    # la tapa: el dibuix pla, retallat en disc
    fx, fy, fr = PL.TANK
    R = fr + 2

    def disc(s, t):
        return (s - R) ** 2 + (t - R) ** 2 <= R * R
    e.quad('diposit', (cx - R, cy + R, z0), (cx + R, cy + R, z0), (cx + R, cy - R, z0), (cx - R, cy - R, z0),
           tex=(tex['tapa'], (fx - R, fy - R, fx + R, fy + R)), forma=disc)


def _escala(e):
    """L'escala de mà contra la paret de l'esquerra: dos muntants taronja i graons, fins a la boca del sostre."""
    za, zb = LADDER_Z
    for z in (za, zb):
        e.caixa('escala', 3, 9, 0, HW, z - 2.5, z + 2.5, SAFETY, 3.2,
                cares={'dreta': {'ramp': SAFETY, 'lvl': 2.6}, 'davant': {'ramp': SAFETY, 'lvl': 3.8}})
    for y in range(14, HW - 4, 15):
        e.caixa('escala', 3.5, 8.5, y, y + 2.4, za + 2.5, zb - 2.5, STEELN, 4.2,
                cares={'dalt': {'ramp': STEELN, 'lvl': 5.0}, 'dreta': {'ramp': STEELN, 'lvl': 3.6}})
    for y in (40, 130):                                            # les grapes a la paret
        for z in (za, zb):
            e.caixa('escala', 0, 3, y, y + 4, z - 1.5, z + 1.5, STEELN, 2.2)


def escena(cv, tex, apagada=None):
    """Tota la sala, de lluny a prop. `tex`: les textures planes. `apagada`: la bombeta que no fa llum (la del mig, a
    l'animació). → l'Escena (qui ha pintat què)."""
    e = Escena(cv, CAM, _llums(apagada), ambient=0.0)
    zn = CAM.pos[2] - 100
    paret = tex['paret']
    XR = 820                                                       # (fins on arriben les parets i el terra)
    # el sostre, fosc, amb les costelles, i la boca de l'escala (la llum del pont)
    e.quad('sostre', (0, HW, zn), (XR, HW, zn), (XR, HW, ZW), (0, HW, ZW), ramp=OLIVE,
           lvl=lambda s, t, P: 1.0 - (1.4 if P[0] % 64 < 5 else 0), dues_cares=True)
    za, zb = LADDER_Z
    e.quad('boca', (0, HW - 0.5, za - 10), (24, HW - 0.5, za - 10), (24, HW - 0.5, zb + 10), (0, HW - 0.5, zb + 10),
           ramp=[(40, 30, 18), (90, 74, 50), (150, 132, 100), (210, 196, 160)],
           lvl=lambda s, t, P: 2.6 - min(s, t, 24 - s, 64 - t) * 0.0 + (0.6 if 3 < s < 21 and 4 < t < 60 else -1.4),
           dues_cares=True)
    # la paret de l'esquerra (x = 0): planxa, amb el sòcol de franges
    e.quad('paret_esq', (0, HW, zn), (0, HW, ZW), (0, 0, ZW), (0, 0, zn), ramp=OLIVE, lvl=_planxa(2.9, seed=22))
    # la paret del fons (z = 300): el dibuix pla (x del pla OFF..640) i, a la dreta, més planxa
    e.quad('paret_fons', (0, HW, ZW), (W - OFF, HW, ZW), (W - OFF, 0, ZW), (0, 0, ZW), tex=(paret, (OFF, 0, W, HW)))
    e.quad('paret_fons_dreta', (W - OFF, HW, ZW), (XR, HW, ZW), (XR, 0, ZW), (W - OFF, 0, ZW), ramp=OLIVE,
           lvl=_planxa(3.0, seed=23))
    # el terra, la pintura de l'espai de càrrega i les argolles del barril
    e.quad('terra', (0, 0, ZW), (XR, 0, ZW), (XR, 0, zn), (0, 0, zn), ramp=DECKP, lvl=_terra)
    x0, x1, z0, z1 = CARGO
    groc = [(60, 46, 10), (130, 100, 20), (190, 150, 30), (230, 196, 60)]

    def ratlla(x, z):
        vora = min(x - x0, x1 - x, z - z0, z1 - z) < 2.6
        if vora and int((x + z) // 9) % 2 == 0 and hr(int(x), int(z), 31) > 0.1:
            return 2.0 + (fbm(x / 9, z / 9, 4) - 0.5)
        if abs(z - (z0 + z1) / 2) < 4 and x0 + 26 < x < x1 - 26 and (int(x) // 3) % 3 != 2 and hr(int(x), int(z), 5) > 0.3:
            return 1.6                                              # el rètol «CARREGA», gastat
        return None
    _calcomania(e, 'carrega', x0, x1, z0, z1, groc, ratlla)
    bx, bz = BARREL
    for ax in (bx - 34, bx + 34):
        e.caixa('argolla', ax - 3, ax + 3, 0, 1.6, bz - 2, bz + 2, STEELN, 3.6, cares={'dalt': {'ramp': STEELN, 'lvl': 4.6}})
    # la foscor dels racons: on les parets es troben amb el terra i entre elles
    e.foscor('racons', (0, 0.5, ZW), (XR, 0.5, ZW), (XR, 0.5, zn), (0, 0.5, zn),
             lambda s, t: max(0.6 * max(0.0, 1 - t / 28), 0.6 * max(0.0, 1 - s / 26)))
    e.foscor('cantonada', (0.5, HW, ZW - 60), (0.5, HW, ZW), (0.5, 0, ZW), (0.5, 0, ZW - 60),
             lambda s, t: 0.55 * max(0.0, 1 - (60 - s) / 60))
    e.foscor('cantonada2', (0, HW, ZW - 0.5), (60, HW, ZW - 0.5), (60, 0, ZW - 0.5), (0, 0, ZW - 0.5),
             lambda s, t: 0.55 * max(0.0, 1 - s / 60))
    # un cable gruixut que surt de sota el panell del motor i va fent corbes pel terra fins al dipòsit
    e.cable('cables', [(PL.MOTOR[0] - OFF + 10, 0.8, ZW - 2), (330, 0.8, 268), (270, 0.8, 252), (210, 0.8, 262),
                       (150, 0.8, 244), (TANK[0] + TANK[2] - 2, 0.8, 232)], BLACKT, 2.2, gruix=2.6)
    # la rampa: els brancals i la llinda gruixuts, que surten de la paret (el davant, del dibuix pla)
    ra, rb = RAMP_X
    for xa, xb in ((ra - 8, ra), (rb, rb + 8)):
        e.caixa('rampa_marc', xa, xb, 0, RAMP_H + 10, ZW - 12, ZW, OLIVE, 3.0,
                cares={'davant': {'tex': (paret, (xa + OFF, FY - RAMP_H - 10, xb + OFF, FY))},
                       'esquerra': {'ramp': OLIVE, 'lvl': lambda s, t, P: 2.4 + (1.6 if (s + t) % 10 < 5 else 0)},
                       'dreta': {'ramp': OLIVE, 'lvl': lambda s, t, P: 1.8 + (1.6 if (s + t) % 10 < 5 else 0)},
                       'dalt': {'ramp': OLIVE, 'lvl': 3.6}})
    e.caixa('rampa_marc', ra, rb, RAMP_H, RAMP_H + 10, ZW - 12, ZW, OLIVE, 3.0,
            cares={'davant': {'tex': (paret, (ra + OFF, FY - RAMP_H - 10, rb + OFF, FY - RAMP_H))},
                   'sota': {'ramp': OLIVE, 'lvl': 1.4}, 'dalt': {'ramp': OLIVE, 'lvl': 3.6}})
    e.quad('rampa_llindar', (ra, 0.6, ZW), (rb, 0.6, ZW), (rb, 0.6, ZW - 12), (ra, 0.6, ZW - 12), ramp=STEELN,
           lvl=lambda s, t, P: 3.4 + (1.2 if (s + t) % 8 < 2 else 0) - (1.6 if t < 1.2 else 0))
    # el quadre elèctric i el panell del motor, una mica sortits de la paret
    fx0, fy0, fx1, fy1 = PL.FUSE
    e.caixa('fusibles', fx0 - OFF, fx1 - OFF, FY - fy1, FY - fy0, ZW - 6, ZW, STEELN, 2.6,
            cares={'davant': {'tex': (paret, (fx0, fy0, fx1, fy1))}, 'dalt': {'ramp': STEELN, 'lvl': 4.0}})
    mx0, my0, mx1, my1 = PL.MOTOR
    e.caixa('motor', mx0 - 3 - OFF, mx1 + 3 - OFF, FY - my1 - 1, FY - my0 + 3, ZW - 4, ZW, OLIVE, 2.4,
            cares={'davant': {'tex': (paret, (mx0 - 3, my0 - 3, mx1 + 3, my1 + 1))}, 'dalt': {'ramp': OLIVE, 'lvl': 4.0}})
    # els mobles de la cuina, contra la paret: el calaix de la Vet, el fogó i la nevera (el davant, del dibuix pla)
    for sid, (a, b, h, z), crema in (('calaix', CAL, False), ('cafetera', CON, False), ('nevera', FRI, True)):
        ramp = [(60, 54, 44), (110, 102, 84), (160, 152, 128), (196, 188, 162), (222, 216, 192), (240, 236, 216)] \
            if crema else OLIVE
        e.foscor(f'ombra_{sid}', (a - 4, 0.5, z), (b + 4, 0.5, z), (b + 4, 0.5, z - 14), (a - 4, 0.5, z - 14),
                 lambda s, t: 0.6 * max(0.0, 1 - t / 14))
        e.caixa(sid, a, b, 0, h, z, ZW, ramp, 2.6,
                cares={'davant': {'tex': (paret, (a + OFF, FY - h, b + OFF, FY))},
                       'esquerra': {'ramp': ramp, 'lvl': lambda s, t, P: 2.2 - (1.0 if P[1] < 6 else 0)},
                       'dalt': {'ramp': STEELN if sid == 'cafetera' else ramp,
                                'lvl': lambda s, t, P: 4.4 - (1.2 if s < 1.2 or t < 1.2 else 0)}})
    # el dipòsit i l'escala
    e.foscor('ombra_diposit', (TANK[0] - 60, 0.5, ZW), (TANK[0] + 70, 0.5, ZW), (TANK[0] + 70, 0.5, TANK[3] - 26),
             (TANK[0] - 60, 0.5, TANK[3] - 26), lambda s, t: 0.7 * max(0.0, min(1.0, (130 - s) / 30, (t - 0) / 26 + 0.2)))
    _diposit(e, tex)
    _escala(e)
    # el banc d'en Tomàs, separat de la paret i girat, amb la carmanyola, i l'ombra
    _banc(e)
    # el carril de la grua, la politja amb la cadena i el ganxo, i els cables del sostre
    zr = POLITJA[1]
    e.caixa('grua', 0, XR, HW - 14, HW - 2, zr - 4, zr + 4, STEELN, 2.4,
            cares={'davant': {'ramp': STEELN, 'lvl': lambda s, t, P: 2.6 + (1.4 if t < 2 or t > 10 else 0)
                              + (1.6 if t % 12 > 5 and abs((s % 24) - 12) < 1.2 else 0)},
                   'sota': {'ramp': STEELN, 'lvl': 3.4}})
    px, pz = POLITJA
    e.caixa('grua', px - 7, px + 7, HW - 30, HW - 14, pz - 6, pz + 6, SAFETY, 3.0,
            cares={'davant': {'ramp': SAFETY, 'lvl': 3.6}, 'esquerra': {'ramp': SAFETY, 'lvl': 2.2}})
    e.cable('grua', [(px, HW - 30, pz), (px + 1, 112, pz), (px, 96, pz)], STEELN, 3.6, gruix=1.6)
    e.cable('grua', [(px - 4, HW - 30, pz), (px - 4, 120, pz)], STEELN, 2.6, gruix=1.2)
    e.cable('grua', [(px, 96, pz), (px + 5, 90, pz), (px + 4, 84, pz), (px - 1, 86, pz)], STEELN, 4.4, gruix=1.6)
    e.cable('cables_sostre', [(170, HW, 260), (230, HW - 12, 250), (300, HW - 4, 256), (380, HW - 10, 246),
                              (440, HW, 252)], BLACKT, 2.0, gruix=2.0)
    # les bombetes, penjades del sostre
    for i, (lx, lz) in enumerate(LAMPS):
        img, peu = _bombeta(apagada != i)
        e.linia((lx, HW, lz), (lx, 190, lz), BLACKT, 2.0)
        e.sprite('bombeta', img, peu, (lx, 184, lz))
    # els bassals de llum càlida sota les bombetes, i la claror de la boca del sostre a la paret
    for i, (lx, lz) in enumerate(LAMPS):
        if i == apagada:
            continue
        e.claror((lx - 130, 0.4, lz + 90), (lx + 130, 0.4, lz + 90), (lx + 130, 0.4, lz - 110), (lx - 130, 0.4, lz - 110),
                 (255, 190, 110), lambda s, t: 0.16 * max(0.0, 1 - math.hypot((s - 130) / 130, (t - 90) / 100)) ** 1.3)
    # primer pla: la quaderna i dues canonades a la dreta, i dues caixes a baix a l'esquerra (es veuen tallades)
    _primer_pla(e)
    e.silueta({'primer_pla'}, 0.5)
    return e


def _banc(e):
    bx, bz, ang = BENCH
    c, s_ = math.cos(ang), math.sin(ang)
    e.foscor('ombra_banc', (bx - 46, 0.6, bz + 26), (bx + 54, 0.6, bz + 26), (bx + 54, 0.6, bz - 30),
             (bx - 46, 0.6, bz - 30),
             lambda s, t: 0.6 * max(0.0, 1 - ((s - 52) / 48) ** 2 - ((t - 30) / 26) ** 2) * 1.5)
    for lx in (-24, 24):                                           # les potes
        e.caixa_girada('banc', bx + lx * c, bz + lx * s_, 4, 16, 22, ang, WOODB, 2.6)
    fusta = {'ramp': WOODB, 'lvl': lambda s, t, P: 4.4 + (hr(int(s) // 8, 37) - 0.5) * 0.6 - (1.0 if t < 1 else 0)}
    e.caixa_girada('banc', bx, bz, 62, 20, 4, ang, WOODB, 3.0, y0=22,
                   cares={'dalt': fusta, 'davant': {'ramp': WOODB, 'lvl': 2.8}, 'esquerra': {'ramp': WOODB, 'lvl': 2.2}})
    # la carmanyola: una capsa de llauna vermella, amb la tapa i la nansa
    lx, lz = bx - 14 * c, bz - 14 * s_
    e.caixa_girada('carmanyola', lx, lz, 20, 11, 9, ang, REDK, 3.0, y0=26,
                   cares={'dalt': {'ramp': REDK, 'lvl': lambda s, t, P: 4.4 - (1.6 if abs(t - 5.5) < 0.8 else 0)},
                          'davant': {'ramp': REDK, 'lvl': lambda s, t, P: 3.4 - (1.6 if abs(t - 3) < 0.7 else 0)
                                     + (2.2 if abs(s - 10) < 1.5 and 3.5 < t < 6 else 0)},
                          'esquerra': {'ramp': REDK, 'lvl': 2.0}})
    e.caixa_girada('carmanyola', lx, lz, 8, 1.5, 3, ang, STEELN, 4.6, y0=35)
    # la clau anglesa, al costat
    kx, kz = bx + 16 * c, bz + 16 * s_
    e.caixa_girada('banc', kx, kz, 16, 2.4, 1, ang + 0.3, STEELN, 4.8, y0=26)


def _primer_pla(e):
    # la quaderna (una biga de planxa, amb franges a baix) i dues canonades verticals, a la dreta
    e.caixa('primer_pla', 476, 502, 0, HW + 40, 40, 62, OLIVE, 1.6,
            cares={'esquerra': {'ramp': OLIVE, 'lvl': lambda s, t, P: 1.4 - (1.0 if s < 2 or s > 20 else 0)
                                + (1.2 if (t % 14) < 2 and 6 < s < 16 else 0)},
                   'davant': {'ramp': SAFETY, 'lvl': lambda s, t, P: (2.4 if (s + t) % 16 < 8 else 0.4)
                              if t > 170 else 1.2 - (1.0 if s < 2 else 0)}})
    for x0, z0, r in ((500, 104, 4), (486, 94, 6)):
        e.tub('primer_pla', (x0, -10, z0), (x0, HW + 10, z0), r, STEELN, 1.0, brides=46)
    # les caixes, a baix a l'esquerra (fosques, tallades per la vora)
    tapa = {'ramp': WOODB, 'lvl': lambda s, t, P: 2.4 - (1.4 if s % 12 < 1.4 else 0)}
    e.caixa_girada('primer_pla', 22, 30, 56, 40, 34, 0.35, WOODB, 1.6,
                   cares={'dalt': tapa, 'davant': {'ramp': WOODB, 'lvl': lambda s, t, P: 1.2 - (1.0 if t % 12 < 1.4
                                                                                          else 0)},
                          'dreta': {'ramp': WOODB, 'lvl': lambda s, t, P: 0.8 - (0.6 if t % 12 < 1.4 else 0)}})
    e.caixa_girada('primer_pla', 18, 32, 36, 28, 20, 0.15, WOODB, 1.8, y0=34,
                   cares={'dalt': tapa, 'davant': {'ramp': WOODB, 'lvl': 1.4}, 'dreta': {'ramp': WOODB, 'lvl': 1.0}})
    # la canonada gruixuda de l'aigua de la bodega, molt a prop, travessant la cantonada de dalt a l'esquerra: ve de
    # fora de quadre, fa colze i s'enfila al sostre, amb les brides i dos penjadors (en silueta)
    e.tub('primer_pla', (-140, 183, -38), (240, 183, -38), 10, STEELN, 1.4, brides=60, llum_dir=(0.3, 1.0))
    e.roca('primer_pla', (240, 183, -38), 11, STEELN, 1.4, llum_dir=(0.6, -0.5), aplana=1.0, seed=3)
    e.tub('primer_pla', (240, 183, -38), (240, 320, -38), 10, STEELN, 1.4, brides=40, llum_dir=(0.8, 0.3))
    for hx in (0, 110):
        e.caixa('primer_pla', hx - 1.5, hx + 1.5, 192, 320, -39.5, -36.5, STEELN, 1.2)


# ─── Composició ────────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _textures():
    return {'paret': _paret(), 'tapa': _tapa()}


@functools.lru_cache(maxsize=None)
def _base(apagada=None):
    cv = Canvas(light=LIGHT)
    e = escena(cv, _textures(), apagada)
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)    # la barra de verbs: negre
    return cv.img, e


def bg(cv):
    img, _ = _base()
    cv.img.paste(img)
    cv.P = cv.img.load()


def _damunt(dibuixa):
    """Un decorat dibuixat damunt el fons amb la mateixa càmera (sprites, ombres): → la diferència amb el fons."""
    base, e0 = _base()
    cv = Canvas(light=LIGHT, img=base.copy())
    e = Escena(cv, CAM, e0.llums)
    dibuixa(e)
    return _diff(cv.img, base)


@functools.lru_cache(maxsize=None)
def _pla_transparent(fn):
    cv = Canvas(light=PL.LIGHT, transparent=True)
    fn(cv)
    return cv.img


def barril(cv):
    """L'últim barril, dret contra la paret entre la rampa i el motor, fermat a les argolles, amb l'ombra."""
    img = _pla_transparent(PL.barril)
    cx, top, base = PL.BARREL
    crop = img.crop((cx - 40, top - 12, cx + 40, base + 8))
    bx, bz = BARREL

    def d(e):
        e.foscor('ombra_barril', (bx - 30, 0.6, bz + 10), (bx + 40, 0.6, bz + 10), (bx + 40, 0.6, bz - 24),
                 (bx - 30, 0.6, bz - 24), lambda s, t: 0.7 * max(0.0, 1 - ((s - 34) / 32) ** 2 - ((t - 16) / 15) ** 2) * 1.6)
        e.sprite('barril', crop, (40, base - top + 12), (bx, 0, bz))
    cv.img.alpha_composite(_damunt(d))


def _claror_terra(e, col, k):
    """La claror de color que entra per la rampa i s'escampa en diagonal pel terra, cap a davant i a la dreta."""
    ra, rb = RAMP_X
    e.claror((ra - 60, 0.4, ZW - 1), (rb + 140, 0.4, ZW - 1), (rb + 140, 0.4, 120), (ra - 60, 0.4, 120), col,
             lambda s, t: k * max(0.0, 1 - t / 180) ** 1.1 * max(0.0, min(1.0, (s - 60 + t * 0.25) / 14,
                                                                         (rb - ra + 60 + t * 0.55 - s) / 14)))


def llum(planeta, col):
    """Decorat: la rampa oberta al planeta i la claror de color que entra pel terra i tenyeix els brancals."""
    def fn(cv):
        base, e = _base()
        pla = Canvas(light=PL.LIGHT, img=_paret().copy())
        PL.rampa_fora(pla, planeta)
        out = e.capa(_diff(pla.img, _paret()), {'paret_fons'})
        on = Canvas(light=LIGHT, img=base.copy())
        e2 = Escena(on, CAM)
        _claror_terra(e2, col, 0.42)
        ra, rb = RAMP_X
        e2.claror((ra - 8, RAMP_H + 10, ZW - 12), (rb + 8, RAMP_H + 10, ZW - 12), (rb + 8, 0, ZW - 12),
                  (ra - 8, 0, ZW - 12), col, lambda s, t: 0.25 if s < 9 or s > rb - ra + 7 else 0.0)
        # (només al terra i als brancals: el que hi ha dret al davant no es tenyeix)
        keep = {e.ids.index(s) for s in ('terra', 'rampa_marc', 'rampa_llindar', 'carrega', 'argolla') if s in e.ids}
        d = _diff(on.img, base).copy()
        P, W_ = d.load(), d.width
        for y in range(d.height):
            for x in range(W_):
                if P[x, y][3] and e.amo[y * W_ + x] not in keep:
                    P[x, y] = (0, 0, 0, 0)
        out.alpha_composite(d)
        cv.img.alpha_composite(out)
    return fn


def motor_obert(cv):
    """Decorat: el panell obert (la tapa girada a la dreta) i, a dins, el motor amb l'injector, que fa calor."""
    _, e = _base()
    pla = Canvas(light=PL.LIGHT, transparent=True)
    PL.motor_obert(pla)
    cv.img.alpha_composite(e.capa(pla.img, {'paret_fons', 'motor'}))


def sacs_carregats(cv):
    """Decorat: els tres sacs de llavors del pare, drets a l'espai de càrrega, amb l'ombra."""
    img = _pla_transparent(PL.sacs_carregats)
    x0, x1, z0, z1 = CARGO
    sacs = (((76, 217), (x0 + 22, z0 + 30)), ((108, 219), (x0 + 48, z0 + 16)), ((142, 216), (x0 + 72, z0 + 32)))
    # (de lluny a prop)
    sacs = sorted(sacs, key=lambda s: -s[1][1])

    def d(e):
        for (sx, base), (wx, wz) in sacs:
            e.foscor('ombra_sac', (wx - 12, 0.6, wz + 8), (wx + 22, 0.6, wz + 8), (wx + 22, 0.6, wz - 10),
                     (wx - 12, 0.6, wz - 10), lambda s, t: 0.7 * max(0.0, 1 - ((s - 15) / 16) ** 2 - ((t - 9) / 9) ** 2) * 1.6)
        for (sx, base), (wx, wz) in sacs:
            crop = img.crop((sx - 18, base - 40, sx + 18, base + 2))
            e.sprite('sac', crop, (18, 40), (wx, 0, wz))
    cv.img.alpha_composite(_damunt(d))


def diu_carmanyola(cv):
    """Decorat: en Diu, assegut damunt la carmanyola d'en Tomàs."""
    gat = diu()
    bx, bz, ang = BENCH
    lx, lz = bx - 14 * math.cos(ang), bz - 14 * math.sin(ang)

    def d(e):
        e.sprite('diu', gat, (13, gat.height - 1), (lx, 34, lz))
    cv.img.alpha_composite(_damunt(d))


# La llauna d'oli (tasca 084): damunt del barril, al costat del motor, de cara a la càmera (tasca 298: a terra era una
# taqueta que tapava qui anava al motor). Vermella, amb el broc i una etiqueta groga: es distingeix de l'oliva de la
# paret i del blau del barril. Desapareix quan s'agafa (`oli_agafat`).
LLAUNA_Y = 67                                        # l'alçada de la tapa del barril
LLAUNA_ESCALA = 2.0


def _llauna_img():
    from PIL import Image as _I
    im = _I.new('RGBA', (14, 18), (0, 0, 0, 0))
    P = im.load()
    RED = [(70, 14, 10), (120, 26, 18), (170, 40, 26), (205, 64, 40), (230, 100, 70)]
    for y in range(5, 18):
        for x in range(1, 12):
            k = 3 if x < 4 else (2 if x < 8 else 1)
            if x == 1 or y == 17:
                k = 0
            P[x, y] = RED[k] + (255,)
    for y in range(9, 13):                                          # l'etiqueta groga
        for x in range(2, 11):
            P[x, y] = ((236, 196, 70) if x < 7 else (196, 150, 50)) + (255,)
    for x in range(3, 9):                                           # la gota negra de l'etiqueta
        P[x, 10] = (40, 30, 24, 255) if x in (5, 6) else P[x, 10]
    for x in range(2, 11):                                          # la tapa
        P[x, 4] = (90, 92, 96, 255)
        P[x, 5] = (150, 152, 156, 255)
    for y in range(0, 5):                                           # el broc, inclinat
        P[8 + y // 2, y] = (170, 172, 176, 255)
        P[9 + y // 2, y] = (110, 112, 116, 255)
    P[3, 7] = (250, 190, 160, 255)                                  # una lluentor
    P[3, 8] = (240, 160, 130, 255)
    return im


def llauna(cv):
    """La llauna d'oli de motor, damunt del barril del costat del motor."""
    img = _llauna_img()
    x, z = LLAUNA

    def d(e):
        e.sprite('llauna', img, (7, 17), (x, LLAUNA_Y, z), escala_img=LLAUNA_ESCALA)
    cv.img.alpha_composite(_damunt(d))


PROPS = {
    'llauna': llauna,
    'barril': barril,
    'llum_terra2': llum('terra2', (236, 200, 140)),
    'llum_aqua': llum('aqua', (220, 236, 250)),
    'llum_ferrum': llum('ferrum', (240, 140, 70)),
    'llum_verdant': llum('verdant', (190, 250, 170)),
    'motor_obert': motor_obert,
    'sacs_carregats': sacs_carregats,
    'diu_carmanyola': diu_carmanyola,
}


def _frames_vapor():
    _, e = _base()
    p0 = _paret()
    return [e.capa(_diff(_paret(f), p0), {'paret_fons'}) for f in range(12)]


def _frames_bombeta():
    base, _ = _base()
    off = _diff(_base(1)[0], base)
    buit = Image.new('RGBA', base.size, (0, 0, 0, 0))
    return [off if f in (5, 7) else buit for f in range(24)]


ANIMS = {
    'vapor': {'frames': _frames_vapor, 'frameDuration': 140},
    'bombeta': {'frames': _frames_bombeta, 'frameDuration': 160},
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


def _caixa_mon(x0, x1, y0, y1, z0, z1):
    return _rect_mon(*[(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)])


def _banc_peus():
    """Els cantons del banc a terra (al món), amb un marge."""
    bx, bz, ang = BENCH
    c, s_ = math.cos(ang), math.sin(ang)
    return [(bx + lx * c - lz * s_, bz + lx * s_ + lz * c) for lx, lz in ((-36, -14), (36, -14), (36, 14), (-36, 14))]


_BANC_BASE = max(_p(x, z)[1] for x, z in _banc_peus())

FRONT = [
    {'id': 'davant_banc', 'mask': _amo({'banc', 'carmanyola'}), 'baseline': _BANC_BASE, 'zIndex': 20,
     'props': ('diu_carmanyola',)},
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20},
]

# El terra on es camina (al món): de la paret de l'escala fins a la quaderna, fins a tocar els mobles del fons; el
# dipòsit fa un clot a la cantonada, i les caixes del primer pla, un altre a baix a l'esquerra.
ZF = 128                                           # el davant del terra on es camina (escala ≈1,2)
WALK_MON = [(22, ZF), (22, 186), (TANK[0] + TANK[2] + 8, 186), (TANK[0] + TANK[2] + 8, 262), (590, 262),
            (550, 180), (512, ZF)]                 # (a la dreta, fins a la quaderna del primer pla)
_WALK = [_p(x, z) for x, z in WALK_MON]
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)


def _escala_a(v):
    """L'escala d'un personatge amb els peus a la y de pantalla `v` (al terra, la profunditat només depèn de v)."""
    lo, hi = 1.0, 2000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.projecta((300, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((300, 0, (lo + hi) / 2))


_DIU = (TANK[0], TANK[1] - (PL.HATCH[1] - PL.TANK[1]) - PL.HATCH[2] + 3, TANK[3])   # en Diu, a la portella
_DIU_UV = CAM.projecta(_DIU)
_LX, _LZ = LADDER_Z
_CX = (CAL[0], FRI[1])
bx_, bz_ = BARREL
LLAUNA = (bx_ + 4, bz_ - 10)                         # x, z del món: damunt del barril

GEOMETRIA = {
    'things': {
        'escala': {'rect': _caixa_mon(0, 10, 0, HW, _LX - 4, _LZ + 4), 'walk': _p(30, (_LX + _LZ) / 2)},
        'diposit': {'rect': _rect_mon((TANK[0] - TANK[2], TANK[1] + TANK[2], TANK[3]),
                                      (TANK[0] + TANK[2], 0, TANK[3]), (TANK[0] + TANK[2], TANK[1] + TANK[2], ZW)),
                    'walk': _p(TANK[0] + 30, TANK[3] - 26)},
        'carrega': {'rect': _rect_mon((CARGO[0], 0, CARGO[3]), (CARGO[1], 0, CARGO[3]), (CARGO[1], 0, CARGO[2]),
                                      (CARGO[0], 0, CARGO[2])),
                    'walk': _p((CARGO[0] + CARGO[1]) / 2, CARGO[2] - 8)},
        'rampa': {'rect': _rect_mon((RAMP_X[0], RAMP_H, ZW), (RAMP_X[1], 0, ZW)),
                  'walk': _p((RAMP_X[0] + RAMP_X[1]) / 2, 260)},
        'llauna': {'rect': _caixa_mon(LLAUNA[0] - 16, LLAUNA[0] + 16, LLAUNA_Y - 2, LLAUNA_Y + 38,
                                      LLAUNA[1] - 4, LLAUNA[1] + 4),
                   'walk': _p(bx_, 246)},
        'barril': {'rect': _caixa_mon(bx_ - 24, bx_ + 24, 0, 74, bz_, bz_),
                   'walk': _p(bx_, 246)},
        'motor': {'rect': _rect_mon((PL.MOTOR[0] - OFF - 4, FY - PL.MOTOR[1] + 14, ZW),
                                    (PL.MOTOR[2] - OFF + 4, FY - PL.MOTOR[3] - 2, ZW)),
                  'walk': _p((PL.MOTOR[0] + PL.MOTOR[2]) / 2 - OFF, 250)},
        'fusibles': {'rect': _caixa_mon(PL.FUSE[0] - OFF - 10, PL.FUSE[2] - OFF + 1, FY - PL.FUSE[3] - 1,
                                        FY - PL.FUSE[1] + 1, ZW - 6, ZW),
                     'walk': _p((PL.FUSE[0] + PL.FUSE[2]) / 2 - OFF, 254)},
        'calaix': {'rect': _caixa_mon(CAL[0], CAL[1], 0, CAL[2] + 10, CAL[3], CAL[3]),
                   'walk': _p((CAL[0] + CAL[1]) / 2, 256)},
        'tauler': {'rect': _rect_mon((PL.BOARD[0] - OFF - 4, FY - PL.BOARD[1] + 4, ZW),
                                     (PL.BOARD[2] - OFF + 4, FY - PL.BOARD[3] - 4, ZW)),
                   'walk': _p((PL.BOARD[0] + PL.BOARD[2]) / 2 - OFF, 256)},
        'cafetera': {'rect': _rect_mon((PL.POT[0] - OFF - 10, FY - PL.POT[1] + 6, ZW - 4),
                                       (PL.POT[0] - OFF + 12, CON[2], CON[3])),
                     'walk': _p(PL.POT[0] - OFF, 256)},
        'nevera': {'rect': _caixa_mon(FRI[0], FRI[1], 0, FRI[2], FRI[3], FRI[3]),
                   'walk': _p((FRI[0] + FRI[1]) / 2, 256)},
        # (fins a dalt d'en Diu, que hi dorm al damunt: clicar el gat és clicar la carmanyola)
        'carmanyola': {'rect': _rect_mon((BENCH[0] - 14 * math.cos(BENCH[2]) - 12, 58, BENCH[1] - 14 * math.sin(BENCH[2])),
                                         (BENCH[0] - 14 * math.cos(BENCH[2]) + 12, 24,
                                          BENCH[1] - 14 * math.sin(BENCH[2]))),
                       'walk': _p(BENCH[0] - 40, BENCH[1] - 34)},
    },
    # En Tomàs, a l'esquerra del banc: ni davant de la nevera ni de la carmanyola (es quedaria els clics).
    'spawns': {'tomas': _p(BENCH[0] - 70, BENCH[1] - 16), 'diu': (round(_DIU_UV[0]), round(_DIU_UV[1])),
               'iri': _p(250, 170), 'vet': _p(380, 150)},
    'walkable': _WALK,
    'forats': [[_p(x, z) for x, z in _banc_peus()]],
    'floorSquash': 0.45,                           # (la mateixa càmera que el pont, picada, a ≈1,9 m)
    # L'ombra de contacte: la llum dominant és la bombeta del mig; l'ombra s'allarga en sentit contrari.
    'characterShadow': {'enabled': True, 'color': '#1c140a', 'alpha': 0.4, 'squash': 0.42, 'core': 0.6,
                        'light': {'x': _p(*LAMPS[1])[0], 'y': _p(*LAMPS[1])[1], 'stretch': 0.6, 'reach': 130}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]},
                # en Diu, a la portella del dipòsit: la mida de la tapa, a aquella distància
                {'id': 'portella', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': False,
                 'scaleTop': round(CAM.escala(_DIU), 3), 'scaleBottom': round(CAM.escala(_DIU), 3),
                 'points': [(round(_DIU_UV[0]) - 24, round(_DIU_UV[1]) - 30), (round(_DIU_UV[0]) + 24, round(_DIU_UV[1]) - 30),
                            (round(_DIU_UV[0]) + 24, round(_DIU_UV[1]) + 4), (round(_DIU_UV[0]) - 24, round(_DIU_UV[1]) + 4)]}],
    # La llum de la sala sobre els personatges (characterLights del motor): la bodega verd oliva, fosca: les bombetes
    # del sostre i la claror de fora, per la rampa.
    'characterLights': {
        'ambient': '#8c8a78',
        'lights': [
            *[llum_personatges(CAM, l.pos, l.r, '#ffdc9a', 0.45) for l in _llums()[:len(LAMPS)]],  # les bombetes
            llum_personatges(CAM, _llums()[len(LAMPS)].pos, _llums()[len(LAMPS)].r, '#fff0d0', 0.5),  # la claror del desert, per la rampa
        ],
    },
}

