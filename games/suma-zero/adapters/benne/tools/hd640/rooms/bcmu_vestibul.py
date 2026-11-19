"""
El vestíbul del BCMU (Escena 4, la Vet), Ginebra, les nou del matí. EN 3D (hd640/tres_d.py), a 1×.

Una càmera alta que mira de biaix la cantonada del fons a l'esquerra:
  - a la paret de l'esquerra, en escorç, la **porta gran** de vidre i llautó (la sortida), amb el matí gris de
    Ginebra a fora; la claror hi entra i s'estira pel terra; les dues **plantes** de plàstic als costats
    (`planta_retallada`: en falta una);
  - a la paret del fons, de marbre crema amb **pilastres** que en sobresurten (amb els apliques), la cornisa de caoba:
    el banquer gran, el **retrat** del Director amb en Rockefeller, la **pancarta**, el logotip, l'**estació del
    tub**, el banquer petit i l'**ascensor** daurat amb l'agulla;
  - la **font** seca, enmig de la sala, amb volum (la pica, la columna i els caps de lleó, el rètol): s'hi passa per
    darrere;
  - la **recepció**, separada de la paret i una mica girada, amb el cartellet i la cadira buida al darrere (la
    recepcionista hi és, quan hi és, darrere el taulell); la **màquina d'entrepans**, amb volum;
  - el terra de marbre en escacs, que fuig, i tan polit que hi surt tot reflectit (la sala tornada a pintar amb la
    càmera sota el terra);
  - primer pla: els pals de llautó amb el cordó vermell de les cues, a baix, i una columna de marbre a la dreta.
  - la barra de sospita (`sospita`, `sospita_5` … `sospita_95`): un HUD a dalt de tot, pla, sense llum de sala.

Tot el detall ve del dibuix pla de sempre (bcmu_vestibul_pla_comu.py), projectat. Els decorats (la planta que
falta, l'entrepà que falta) tornen a pintar la sala i en surt la diferència.

El món: x a la dreta (0 = la paret de la porta), y amunt (0 = el terra), z cap al fons (300 = la paret del fons);
1 unitat = 1 píxel de sala a la distància on un personatge fa ≈111 px (escala 1).
"""
import functools
import math

import numpy as np
from PIL import Image

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from hd.pix import Canvas, Light, W, H, hr
from hd.rooms.comu import _diff, text, text_width
from hd640.rooms import bcmu_vestibul_pla_comu as PL
from hd640.rooms.bcmu_vestibul_pla_comu import CREAM, DARKM, MARBLE, BRASS, MAHOG, NAVYB, CARPET, logo
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
ZW = 300                                           # la paret del fons
HW = 200                                           # l'alçada de les parets (el dibuix pla fa 200 fins al terra)
XL = 125                                           # al dibuix pla, la cantonada: a l'esquerra, la paret de la porta
XR = 760                                           # on s'acaba la paret del fons (fora de la pantalla)
FONT = (124, 196, 122, 74, 40, 0.45)               # la font: x, z del centre, ample, fons, alçada, gir
RECEP = (290, 238, 128, 44, 0.12)                  # la recepció: x, z del centre, ample, fons, gir
PILAR = 8                                          # el que sobresurten les pilastres
PLANTES = ((14, 150, 0), (14, 272, 1))             # les plantes: x, z, varietat (els costats de la porta)
MACH_D = 40                                        # el fons de la màquina d'entrepans


def _w(fx):
    """Una x del dibuix pla de la paret del fons → la x del món."""
    return fx - XL


def _wz(fx):
    """Una x del dibuix pla de la paret de la porta → la z del món."""
    return ZW - XL + fx


def _y(fy):
    """Una y del dibuix pla (el terra, a 200) → l'alçada del món."""
    return HW - fy


DOOR = (_wz(3), _wz(80), 0, _y(34))                # la porta (amb el marc i el travesser): z0, z1, y0, y1
MACH = (_w(PL.MACHINE[0]), _w(PL.MACHINE[2]) + 1)  # x0, x1
ASC = (_w(PL.ASC[0] - 4), _w(PL.ASC[2] + 9), 0, _y(PL.DIAL[1] - 13))   # l'ascensor amb l'indicador i el botó

CAM = Camera(pos=(420, 190, -260), yaw=-0.36, pitch=0.16, f=440, centre=(320, 90))
CAM_REFLEX = Camera(pos=(420, -190, -260), yaw=-0.36, pitch=-0.16, f=440, centre=(320, H - 90))   # (sota el terra)

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)  # (la llum és la del món: la de l'Escena)
TEX_LIGHT = Light(ambient=0.3, vignette=None, floor_fade=None)   # el dibuix pla de les textures, sense vinyeta

LLUMS = [Llum((300, 520, 150), 640, 1.4, power=1.2),                     # la claraboia (fora de quadre)
         Llum((-60, 110, (DOOR[0] + DOOR[1]) / 2), 260, 1.0, power=1.5)]   # el matí per la porta de vidre
for _px in (232, 320, 499, 555):                                         # els apliques de les pilastres
    LLUMS.append(Llum((_w(_px) + 4, _y(86), ZW - PILAR - 6), 70, 0.8, power=2.0))


# ─── Les textures: el dibuix pla de sempre ───────────────────────────────────

def _paret(needle=0.0, ding=0.0):
    """Les dues parets planes, de cara: el marbre, la cornisa, la porta, els quadres, el retrat, la pancarta, el
    logotip, el tub i l'ascensor. `needle`: l'agulla de l'ascensor (0..1); `ding`: el botó encès."""
    cv = Canvas(light=TEX_LIGHT)
    PL.wall(cv)
    PL.door(cv)
    PL.frame(cv, 133, 40, 221, 117)                                    # un banquer gran
    PL.banker(cv, 138, 45, 216, 112, 1)
    PL.frame(cv, 509, 32, 549, 72)                                     # i un de petit, damunt la màquina
    PL.banker(cv, 514, 37, 544, 67, 2)
    PL.portrait(cv)
    PL.banner(cv)
    PL.tub_station(cv, 472, 93, 497, 150)
    PL.elevator(cv, needle)
    if ding:
        cv.glow(PL.ASC[2] + 7, 131, 7, (255, 220, 140), ding)
    logo(cv, 408, 80, k=4.27, lvl=4.2)                                 # el logotip gran, damunt la recepció
    text(cv, 'B C M U', 408 - text_width('B C M U') // 2, 106, BRASS, 4.6)
    return cv.img


def _peces(plants=(0, 1), empty=(), sway=None, price=True):
    """La font, la recepció, la màquina i les plantes, planes sobre transparent (se'n treuen retalls)."""
    out = {}
    for nom, fn in (('font', PL.fountain), ('recepcio', PL.reception),
                    ('maquina', lambda cv: PL.machine(cv, empty, price))):
        cv = Canvas(light=TEX_LIGHT, transparent=True)
        fn(cv)
        out[nom] = cv.img
    for i, (cx, kind) in enumerate(PL.PLANTS):
        cv = Canvas(light=TEX_LIGHT, transparent=True)
        if i in plants:
            PL.plant(cv, cx, kind, sway=sway if kind == 0 else None)
        out[f'planta{i}'] = cv.img
    return out


BASIN_BOX = (129, 173, 226, 208)                   # el davant de la pica, amb el rètol
COLUMN_BOX = (155, 127, 200, 174)                  # la columna, la tassa i els caps de lleó
RECEP_BOX = (345, 149, 472, 201)                   # el davant de la recepció (el marbre de dalt i la caoba)
SIGN_BOX = (356, 127, 461, 150)                    # el cartellet i el timbre, damunt el taulell
CHAIR_BOX = (420, 122, 446, 150)                   # la cadira buida
MACH_BOX = (PL.MACHINE[0], PL.MACHINE[1], PL.MACHINE[2] + 1, PL.MACHINE[3] + 1)


BANNER_BOX = (332, 20, 479, 54)                    # la pancarta, amb les barres i el serrell


def _planta_box(i):
    cx = PL.PLANTS[i][0]
    return (cx - 21, 116, cx + 22, 202)


def _pilastra_box(px):
    return (px - 2, 21, px + 11, 192)


@functools.lru_cache(maxsize=None)
def _textures(plants=(0, 1), empty=()):
    return {'paret': _paret(), **_peces(plants, empty)}


# ─── Les superfícies ────────────────────────────────────────────────────────

def _marbre(lvl0=4.4, seed=3):
    """Marbre crema amb vetes en coordenades del món (s, t des del cantó de dalt): on el dibuix pla no arriba."""
    def L(s, t, P):
        if t < 21:
            return 3.0 if t < 12 else 3.4 + (1.2 if t < 13 else 0)                  # el sostre i la cornisa
        if t > HW - 9:
            return 3.0 + (1.4 if t < HW - 8 else 0)                                  # el sòcol fosc
        v = math.sin((s * 0.045 + t * 0.0825) + math.sin(t * 0.0375 + seed) * 2.2 + seed)
        vein = 1.1 if abs(v) < 0.026 else (0.45 if abs(v) < 0.07 else 0)
        return lvl0 + (hr(int(s // 4), int(t // 4), seed) - 0.5) * 0.35 - vein - (1.2 if s % 64 < 1 else 0)
    return L


def _fosca(x, z):
    """Si la llosa del terra a (x, z) és de les grises (els escacs)."""
    return (math.floor(x / 42) + math.floor(z / 42)) % 2 == 1


def _escacs(fosc):
    """El terra de marbre en escacs, en coordenades del món, amb vetes fines: les lloses cremes o les grises."""
    def L(s, t, P):
        x, z = P[0], P[2]
        cu = math.floor(x / 42)
        seam = x % 42 < 0.9 or z % 42 < 0.9
        vein = 0.6 if abs(math.sin(x * 0.05 + z * 0.11 + math.sin(z * 0.06 + cu) * 1.8)) < 0.035 else 0
        n = (hr(int(x // 4), int(z // 3), 7) - 0.5) * 0.3
        if fosc:
            return 3.0 if seam else 4.0 + n + vein * 0.6
        return 4.0 if seam else 5.0 + n - vein
    return L


def escena(cv, tex, estat=frozenset(), cam=CAM, reflex=False):
    """Tota la sala, de lluny a prop. `reflex`: la passada del reflex (sense el que és pintat damunt el terra).
    → l'Escena (qui ha pintat què)."""
    e = Escena(cv, cam, LLUMS, ambient=-0.2)
    zn = CAM.pos[2] + 60
    paret = tex['paret']
    # el sostre de cassetons
    e.quad('sostre', (0, HW, zn), (XR, HW, zn), (XR, HW, ZW), (0, HW, ZW), ramp=CREAM,
           lvl=lambda s, t, P: 3.0 if s % 43 < 3 or t % 43 < 3 else 4.4, dues_cares=True)
    # la paret de la porta (x = 0): de prop, marbre; cap a la cantonada, el dibuix pla (la porta)
    e.quad('paret_esq_prop', (0, HW, zn), (0, HW, ZW - XL), (0, 0, ZW - XL), (0, 0, zn), ramp=MARBLE, lvl=_marbre())
    # de prop, un altre banquer important i dues pilastres que sobresurten (com les del fons)
    e.quad('paret_esq_prop', (0.5, _y(40), 52), (0.5, _y(40), 52 + 88), (0.5, _y(117), 52 + 88), (0.5, _y(117), 52),
           tex=(paret, (133, 40, 222, 118)))
    for pz in (24, 160):
        b = _pilastra_box(232)
        e.caixa('pilastres', 0.5, PILAR, 0, HW - 21, pz, pz + b[2] - b[0], MARBLE, 4.0,
                cares={'dreta': {'tex': (paret, b)}, 'davant': {'ramp': MARBLE, 'lvl': 3.4}})
    e.quad('paret_esq', (0, HW, ZW - XL), (0, HW, ZW), (0, 0, ZW), (0, 0, ZW - XL), tex=(paret, (0, 0, XL, HW)))
    # la paret del fons (z = 300): el dibuix pla (x 125..640) i, a la dreta, més marbre
    e.quad('paret_fons', (0, HW, ZW), (W - XL, HW, ZW), (W - XL, 0, ZW), (0, 0, ZW), tex=(paret, (XL, 0, W, HW)))
    e.quad('paret_fons_dreta', (W - XL, HW, ZW), (XR, HW, ZW), (XR, 0, ZW), (W - XL, 0, ZW), ramp=MARBLE,
           lvl=_marbre(seed=5))
    # la pancarta, penjada de la cornisa, una mica separada de la paret i més grossa (que es llegeixi)
    bk = 1.4
    bx0, by0, bx1, by1 = BANNER_BOX
    bc = _w((bx0 + bx1) / 2)
    e.quad('pancarta', (bc - (bx1 - bx0) * bk / 2, _y(by0), ZW - 3), (bc + (bx1 - bx0) * bk / 2, _y(by0), ZW - 3),
           (bc + (bx1 - bx0) * bk / 2, _y(by0) - (by1 - by0) * bk, ZW - 6),
           (bc - (bx1 - bx0) * bk / 2, _y(by0) - (by1 - by0) * bk, ZW - 6), tex=(paret, BANNER_BOX))
    # les pilastres, que sobresurten de la paret del fons (el davant, el dibuix pla)
    for px in (232, 320, 499, 555):
        x0 = _w(px - 2)
        b = _pilastra_box(px)
        e.caixa('pilastres', x0, x0 + b[2] - b[0], 0, HW - 21, ZW - PILAR, ZW - 0.5, MARBLE, 4.0,
                cares={'davant': {'tex': (paret, b)},
                       'esquerra': {'ramp': MARBLE, 'lvl': lambda s, t, P: 3.6 - (0.8 if t < 9 else 0)},
                       'dreta': {'ramp': MARBLE, 'lvl': lambda s, t, P: 3.2 - (0.8 if t < 9 else 0)}})
    # el terra: els escacs (dues rampes: el crema i el gris)
    e.quad('terra', (0, 0, ZW), (XR, 0, ZW), (XR, 0, zn), (0, 0, zn), ramp=CREAM, lvl=_escacs(False))
    e.quad('terra', (0, 0, ZW), (XR, 0, ZW), (XR, 0, zn), (0, 0, zn), ramp=DARKM, lvl=_escacs(True),
           forma=lambda s, t: _fosca(s, ZW - t))
    if not reflex:
        # la claror del matí, que entra per la porta i s'estira pel terra en diagonal
        dz0, dz1 = DOOR[0] + 4, DOOR[1] - 4
        e.claror((0, 0.3, dz1), (230, 0.3, dz1 - 110), (230, 0.3, dz0 - 140), (0, 0.3, dz0), (232, 238, 244),
                 lambda s, t: 0.20 * max(0.0, 1 - s / 230))
        # la foscor dels racons
        e.foscor('racons', (0, 0.5, ZW), (XR, 0.5, ZW), (XR, 0.5, zn), (0, 0.5, zn),
                 lambda s, t: max(0.4 * max(0.0, 1 - t / 22), 0.35 * max(0.0, 1 - s / 18)))
    e.foscor('cantonada', (0, HW, ZW - 0.5), (50, HW, ZW - 0.5), (50, 0, ZW - 0.5), (0, 0, ZW - 0.5),
             lambda s, t: 0.35 * max(0.0, 1 - s / 50))
    # les plantes, als costats de la porta
    for i, (px_, pz_, _) in enumerate(PLANTES):
        b = _planta_box(i)
        img = tex[f'planta{i}'].crop(b)
        if img.getbbox():
            if not reflex:
                e.foscor('ombra_plantes', (px_ - 12, 0.6, pz_ + 12), (px_ + 14, 0.6, pz_ + 12), (px_ + 14, 0.6, pz_ - 12),
                         (px_ - 12, 0.6, pz_ - 12), lambda s, t: 0.5 * max(0.0, 1 - ((s - 13) / 13) ** 2 - ((t - 12) / 12) ** 2) * 1.6)
            e.sprite(f'planta{i}', img, (PL.PLANTS[i][0] - b[0], 199 - b[1]), (px_, 0, pz_), escala_img=1.25)
    # la màquina d'entrepans, contra la paret del fons
    mx0, mx1 = MACH
    mh = MACH_BOX[3] - MACH_BOX[1]
    if not reflex:
        e.foscor('ombra_maquina', (mx0 - 4, 0.6, ZW), (mx1 + 12, 0.6, ZW), (mx1 + 12, 0.6, ZW - MACH_D - 14),
                 (mx0 - 4, 0.6, ZW - MACH_D - 14), lambda s, t: 0.5 * min(1.0, max(0.0, (MACH_D + 14 - t) / 14)))
    e.caixa('maquina', mx0, mx1, 0, mh, ZW - 1 - MACH_D, ZW - 1, NAVYB, 2.6,
            cares={'davant': {'tex': (tex['maquina'], MACH_BOX)}, 'dalt': {'ramp': NAVYB, 'lvl': 3.0},
                   'esquerra': {'ramp': NAVYB, 'lvl': lambda s, t, P: 2.4 + (1.4 if t < 6 else 0)}})
    # la recepció, girada: el davant (el dibuix pla), el marbre de dalt, el cartellet i la cadira buida al darrere
    rx, rz, rw, rd, ra = RECEP
    c_, s_ = math.cos(ra), math.sin(ra)

    def R(lx, y, lz):
        return (rx + lx * c_ - lz * s_, y, rz + lx * s_ + lz * c_)
    rh = RECEP_BOX[3] - RECEP_BOX[1]
    e.sprite('recepcio', tex['recepcio'].crop(CHAIR_BOX), ((CHAIR_BOX[2] - CHAIR_BOX[0]) / 2, CHAIR_BOX[3] - CHAIR_BOX[1] - 1),
             R(30, 18, rd / 2 + 16), escala_img=1.2)
    if not reflex:
        e.foscor('ombra_recepcio', R(-rw / 2 - 6, 0.6, rd / 2 + 4), R(rw / 2 + 10, 0.6, rd / 2 + 4),
                 R(rw / 2 + 10, 0.6, -rd / 2 - 16), R(-rw / 2 - 6, 0.6, -rd / 2 - 16),
                 lambda s, t: 0.45 * min(1.0, max(0.0, (rd + 20 - t) / 14)) * min(1.0, s / 8))
    e.caixa_girada('recepcio', rx, rz, rw, rd, rh - 6, ra, MAHOG, 2.4,
                   cares={'davant': {'tex': (tex['recepcio'], (RECEP_BOX[0], RECEP_BOX[1] + 6, RECEP_BOX[2], RECEP_BOX[3]))},
                          'esquerra': {'ramp': MAHOG, 'lvl': lambda s, t, P: 2.6 + (hr(int(s), int(t // 5), 3) - 0.5) * 0.3},
                          'dalt': {'ramp': MAHOG, 'lvl': 2.0}})
    e.caixa_girada('recepcio', rx, rz, rw + 8, rd + 6, 6, ra, MARBLE, 5.0, y0=rh - 6,
                   cares={'davant': {'ramp': MARBLE, 'lvl': lambda s, t, P: 6.0 if t < 1.5 else 4.6},
                          'dalt': {'ramp': MARBLE, 'lvl': lambda s, t, P: 5.2 + (hr(int(s // 4), int(t // 4), 21) - 0.5) * 0.4},
                          'esquerra': {'ramp': MARBLE, 'lvl': 4.2}})
    e.sprite('recepcio', tex['recepcio'].crop(SIGN_BOX), (58, SIGN_BOX[3] - SIGN_BOX[1] - 1), R(0, rh, -rd / 2 + 10),
             escala_img=1.15)
    # la font seca, enmig de la sala: la pica (el davant, el dibuix pla amb el rètol), la columna i la tassa
    fx, fz, fw, fd, fh, fa = FONT
    c2, s2 = math.cos(fa), math.sin(fa)

    def F(lx, y, lz):
        return (fx + lx * c2 - lz * s2, y, fz + lx * s2 + lz * c2)
    if not reflex:
        e.foscor('ombra_font', F(-fw / 2 - 6, 0.6, fd / 2 + 6), F(fw / 2 + 12, 0.6, fd / 2 + 6), F(fw / 2 + 12, 0.6, -fd / 2 - 14),
                 F(-fw / 2 - 6, 0.6, -fd / 2 - 14),
                 lambda s, t: 0.5 * max(0.0, 1 - ((s - fw / 2 - 9) / (fw / 2 + 9)) ** 2 - ((t - fd / 2 - 10) / (fd / 2 + 10)) ** 2) * 1.8)

    def pica(s, t, P):
        if 4 < s < fw - 4 and 4 < t < fd - 4:
            v = 3.0 + (hr(int(s // 3), int(t // 3), 5) - 0.5) * 0.4               # el fons sec, a l'ombra
            for k, (ms, mt) in enumerate(((22, 20), (50, 34), (76, 24))):
                if abs(s - ms) < 1.6 and abs(t - mt) < 1.2:
                    return 7.0                                                    # una moneda (llautó: veure ramp)
            return v
        return 5.6
    e.caixa_girada('font', fx, fz, fw, fd, fh, fa, MARBLE, 4.4,
                   cares={'davant': {'tex': (tex['font'], BASIN_BOX)},
                          'dalt': {'ramp': MARBLE, 'lvl': pica},
                          'esquerra': {'ramp': MARBLE, 'lvl': 3.8}, 'dreta': {'ramp': MARBLE, 'lvl': 3.4}})
    e.sprite('font', tex['font'].crop(COLUMN_BOX), ((COLUMN_BOX[2] - COLUMN_BOX[0]) / 2, COLUMN_BOX[3] - COLUMN_BOX[1] - 1),
             F(0, fh - 4, 0), escala_img=1.35)
    # primer pla: els pals de llautó de les cues amb el cordó vermell, a baix a l'esquerra, i una columna de marbre a la
    # dreta
    FOSC_B = [(6, 4, 2), (14, 10, 4), (26, 18, 8), (44, 32, 14), (70, 52, 24), (100, 76, 36)]
    FOSC_M = [(8, 7, 6), (16, 14, 12), (26, 23, 20), (38, 34, 30), (52, 47, 41), (68, 61, 53), (88, 79, 68),
              (112, 101, 87)]
    pals = [(22, 112), (106, 54), (196, 14)]
    for i in range(len(pals) - 1):
        (ax, az), (bx, bz) = pals[i], pals[i + 1]
        mid = ((ax + bx) / 2, 66, (az + bz) / 2 - 4)
        e.cable('primer_pla', [(ax, 88, az), mid, (bx, 88, bz)], [(20, 2, 6), (50, 6, 14), (90, 14, 24), (130, 30, 40)],
                2.0, gruix=3.0)
    for ax, az in pals:
        e.caixa('primer_pla', ax - 9, ax + 9, 0, 3, az - 9, az + 9, FOSC_B, 2.0)
        e.tub('primer_pla', (ax, 3, az), (ax, 92, az), 2.4, FOSC_B, 2.4, llum_dir=(-0.6, -0.8))
        e.tub('primer_pla', (ax, 92, az), (ax, 96, az), 3.4, FOSC_B, 3.0)
    e.tub('primer_pla', (506, 0, 34), (506, HW, 34), 15, FOSC_M, 3.4, brides=0, llum_dir=(-0.9, -0.2))
    e.caixa('primer_pla', 486, 526, 0, 12, 14, 54, FOSC_M, 2.2)
    return e


# ─── Composició ─────────────────────────────────────────────────────────────

def _render(estat=frozenset(), tex=None):
    """La sala, amb el terra polit: la mateixa sala pintada des de sota el terra, girada, barrejada damunt els
    escacs."""
    tex = tex or _textures()
    cv = Canvas(light=LIGHT)
    e = escena(cv, tex, estat)
    cr = Canvas(light=LIGHT)
    escena(cr, tex, estat, cam=CAM_REFLEX, reflex=True)
    from PIL import ImageFilter
    ref = np.asarray(cr.img.transpose(Image.Transpose.FLIP_TOP_BOTTOM).filter(ImageFilter.BoxBlur(1))).astype(float)
    img = np.asarray(cv.img).astype(float)
    terra = [i for i, sid in enumerate(e.ids) if sid == 'terra']
    mask = np.isin(np.frombuffer(e.amo, dtype=np.uint16).reshape(H, W), terra)
    yy = np.mgrid[0:H, 0:W][0]
    a = np.clip(0.24 - (yy - 120) / 140 * 0.14, 0.08, 0.24)
    a = np.where(mask, a, 0.0)[..., None]
    img[..., :3] = img[..., :3] * (1 - a) + ref[..., :3] * a
    cv.img = Image.fromarray(img.astype('uint8'), 'RGBA').copy()
    cv.P = cv.img.load()
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)    # la barra de verbs: negre
    return cv.img, e


@functools.lru_cache(maxsize=None)
def _base():
    return _render()


def bg(cv):
    cv.img.paste(_base()[0])
    cv.P = cv.img.load()


def _decorat(**kw):
    """Un decorat: la sala amb el dibuix pla canviat, menys la de sempre (només el que canvia)."""
    def draw(cv):
        img, _ = _render(tex=_textures(**kw))
        cv.img.alpha_composite(_diff(img, _base()[0]))
        cv.P = cv.img.load()
    return draw


# La barra de sospita és un HUD: es pinta pla, a dalt de tot, com sempre.
PROPS = {'sospita': PL.sospita, **{f'sospita_{v}': PL._seg(v) for v in range(PL.STEP, 100, PL.STEP)},
         'planta_retallada': _decorat(plants=(0,)), 'maquina_forat': _decorat(empty=(PL.EMPTY,))}


# ─── Animacions ─────────────────────────────────────────────────────────────

def _sprite_capa(e, sid, img, peu_img, peu, escala_img=1.0):
    """Un fotograma d'un dibuix pla dret (un sprite de l'escena), on aquell sprite és el que es veu."""
    from pixels import nearest
    k = e.cam.escala(peu) * escala_img
    u, v, _ = e.cam.projecta(peu)
    w, h = max(1, round(img.width * k)), max(1, round(img.height * k))
    im = nearest(img, (w, h)) if k >= 1 else img.resize((w, h), Image.Resampling.BOX)
    ox, oy = round(u - peu_img[0] * k), round(v - peu_img[1] * k)
    out = Image.new('RGBA', (e.cv.w, e.cv.h), (0, 0, 0, 0))
    src, dst, W_ = im.load(), out.load(), e.cv.w
    ids = {i for i, s in enumerate(e.ids) if s == sid}
    for y in range(h):
        Y = oy + y
        if not 0 <= Y < e.cv.h:
            continue
        for x in range(w):
            X = ox + x
            if 0 <= X < W_ and e.amo[Y * W_ + X] in ids and src[x, y][3] >= 128:
                dst[X, Y] = src[x, y]
    return out


def _fotograma(capes):
    """El fons amb unes capes damunt, menys el fons."""
    img, _ = _base()
    img = img.copy()
    for c in capes:
        img.alpha_composite(c)
    return _diff(img, _base()[0])


def _ease(t):
    return t * t * (3 - 2 * t)


def _frames():
    """L'agulla de l'ascensor, que va pujant i baixant, amb el «ding» (el botó s'encén un moment)."""
    _, e = _base()
    base = _paret()
    seq = [0.0] * 5 + [_ease(i / 9) for i in range(1, 10)] + [1.0] * 5 + [1 - _ease(i / 9) for i in range(1, 10)]
    cache, out = {}, []
    for i, n in enumerate(seq):
        ding = 0.7 if i in (0, 14) else 0.35 if i in (1, 15) else 0.0
        if (n, ding) not in cache:
            cache[(n, ding)] = _fotograma([e.capa(_diff(_paret(needle=n, ding=ding), base), {'paret_fons'})])
        out.append(cache[(n, ding)])
    return out


def _frames_planta():
    """El corrent de l'aire condicionat gronxa les fulles de dalt del ficus."""
    _, e = _base()
    i = [k for k, (_, _, kind) in enumerate(PLANTES) if kind == 0][0]
    b = _planta_box(i)
    px_, pz_, _ = PLANTES[i]
    out = []
    for f in range(12):
        img = _peces(sway=f * math.tau / 12)[f'planta{i}'].crop(b)
        out.append(_fotograma([_sprite_capa(e, f'planta{i}', img, (PL.PLANTS[i][0] - b[0], 199 - b[1]), (px_, 0, pz_),
                                            escala_img=1.25)]))
    return out


def _frames_maquina():
    """La pantalleta del preu de la màquina parpelleja (dos cops) per cridar l'atenció."""
    _, e = _base()
    base = _peces()['maquina']
    off = _fotograma([e.capa(_diff(_peces(price=False)['maquina'], base), {'maquina'})])
    on = _diff(_base()[0], _base()[0])
    return [on] * 4 + [off, on, off, on]


ANIMS = {'ascensor': {'frames': _frames, 'frameDuration': 150},
         'planta': {'frames': _frames_planta, 'frameDuration': 147},
         'maquina': {'frames': _frames_maquina, 'frameDuration': 380}}


# ─── Capes del davant ───────────────────────────────────────────────────────

def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


def _F(lx, lz):
    fx, fz, _, _, _, fa = FONT
    return fx + lx * math.cos(fa) - lz * math.sin(fa), fz + lx * math.sin(fa) + lz * math.cos(fa)


def _R(lx, lz):
    rx, rz, _, _, ra = RECEP
    return rx + lx * math.cos(ra) - lz * math.sin(ra), rz + lx * math.sin(ra) + lz * math.cos(ra)


# El primer pla (sempre davant), la font i la recepció (qui hi passa per darrere, hi queda darrere) i les plantes.
FRONT = [
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20},
    {'id': 'davant_font', 'mask': _amo({'font'}), 'baseline': _p(*_F(0, -FONT[3] / 2))[1], 'zIndex': 20},
    {'id': 'davant_recepcio', 'mask': _amo({'recepcio'}), 'baseline': _p(*_R(0, -RECEP[3] / 2))[1], 'zIndex': 20},
    {'id': 'davant_planta', 'mask': _amo({'planta0'}), 'baseline': _p(PLANTES[0][0], PLANTES[0][1] - 6)[1],
     'zIndex': 20},
]


# ─── Geometria (coordenades de sala, projectades) ────────────────────────────

def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


def _escala_a(v):
    """L'escala d'un personatge amb els peus a la y de pantalla `v` (al terra, la profunditat només depèn de v)."""
    lo, hi = 1.0, 2000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.projecta((260, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((260, 0, (lo + hi) / 2))


def _caixa_girada(cx, cz, w, d, a, y0, y1):
    c, s = math.cos(a), math.sin(a)
    return [(cx + lx * c - lz * s, y, cz + lx * s + lz * c) for lx in (-w / 2, w / 2) for lz in (-d / 2, d / 2)
            for y in (y0, y1)]


# El terra on es camina (al món): tota la sala davant les parets, menys la recepció i la màquina (s'hi va per davant)
# i amb la font com a forat (s'hi fa la volta); no s'acosta tant a la càmera que el personatge passi d'≈1,2.
_RF = [_R(-RECEP[2] / 2 - 8, -RECEP[3] / 2 - 10), _R(RECEP[2] / 2 + 8, -RECEP[3] / 2 - 10)]
WALK_MON = [(18, 288), (196, 288), (214, 262), _RF[0], _RF[1], (376, 252), (MACH[0] - 6, 250), (MACH[1] + 8, 250),
            (MACH[1] + 10, 288), (530, 288), (530, 170), (470, 126), (300, 118), (150, 128), (40, 150), (18, 170)]
_WALK = [_p(x, z) for x, z in WALK_MON]
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)
_FORAT = [_p(*_F(lx, lz)) for lx, lz in ((-FONT[2] / 2 - 4, FONT[3] / 2 + 4), (FONT[2] / 2 + 4, FONT[3] / 2 + 4),
                                         (FONT[2] / 2 + 4, -FONT[3] / 2 - 4), (-FONT[2] / 2 - 4, -FONT[3] / 2 - 4))]

_PB = [_planta_box(i) for i in range(2)]
GEOMETRIA = {
    'things': {
        'sortida': {'rect': _rect_mon((0, 0, DOOR[0]), (0, DOOR[3], DOOR[1])), 'walk': _p(26, (DOOR[0] + DOOR[1]) / 2)},
        'plantes': {'rect': _rect_mon(*[(px_, y, pz_) for px_, pz_, _ in PLANTES for y in (0, 100)],
                                      *[(px_ + 16, 0, pz_) for px_, pz_, _ in PLANTES]),
                    'walk': _p(40, 212)},
        'font': {'rect': _rect_mon(*_caixa_girada(*FONT[:2], FONT[2], FONT[3], FONT[5], 0, FONT[4] + 55)),
                 'walk': _p(*_F(10, -FONT[3] / 2 - 22))},
        'retrat': {'rect': _rect_mon((_w(245), _y(35), ZW), (_w(315), _y(122), ZW)), 'walk': _p(_w(280), 262)},
        'cartell': {'rect': _rect_mon(*[(_w(405) + dx * 147 * 0.7, y, ZW - 4) for dx in (-1, 1) for y in (_y(20), _y(20) - 34 * 1.4)]),
                    'walk': _p(_w(405), 200)},
        'recepcio': {'rect': _rect_mon(*_caixa_girada(*RECEP[:2], RECEP[2], RECEP[3], RECEP[4], 0, 80)),
                     'walk': _p(*_R(0, -RECEP[3] / 2 - 22))},
        'tub': {'rect': _rect_mon((_w(472), _y(93), ZW), (_w(506), _y(150), ZW)), 'walk': _p(_w(484), 258)},
        'maquina': {'rect': _rect_mon(*[(x, y, z) for x in MACH for y in (0, MACH_BOX[3] - MACH_BOX[1])
                                        for z in (ZW - MACH_D, ZW)]),
                    'walk': _p((MACH[0] + MACH[1]) / 2, 232)},
        'ascensor': {'rect': _rect_mon((ASC[0], ASC[3], ZW), (ASC[1], 0, ZW)), 'walk': _p((ASC[0] + ASC[1]) / 2, 272)},
    },
    'spawns': {'vet': _p(340, 138), 'bonfill': _p(222, 192), 'recepcionista': _p(*_R(-8, RECEP[3] / 2 + 14))},
    'walkable': _WALK,
    'forats': [_FORAT],
    'floorSquash': 0.42,                           # (la càmera, picada: el terra es veu aixafat)
    # L'ombra de contacte: la llum dominant és la claraboia, a sobre de la sala; curta i rodona.
    'characterShadow': {'enabled': True, 'color': '#1a140c', 'alpha': 0.38, 'squash': 0.4, 'core': 0.6,
                        'light': {'x': _p(300, 160)[0], 'y': _p(300, 160)[1], 'stretch': 0.35, 'reach': 200}},
    # El reflex dels personatges al marbre polit (més fort que el de la sala, a _render: la roba fosca damunt els
    # escacs, a 0,2, no es veia), que s'esvaeix lluny dels peus.
    'characterReflection': {'enabled': True, 'alpha': 0.5, 'fade': 0.1, 'length': 0.9, 'maxY': BOTTOM},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    # la llum de la sala sobre els personatges, en temps d'execució
    'characterLights': {
        'ambient': '#d8d0c0',                                                           # marbre i claraboia
        'lights': [
            {'x': _p(0, (DOOR[0] + DOOR[1]) / 2, 100)[0], 'y': _p(0, (DOOR[0] + DOOR[1]) / 2, 100)[1],
             'radius': 240, 'color': '#e8eef4', 'intensity': 0.6},                      # el matí per la porta
            {'x': _p(_w(324), ZW, 110)[0], 'y': _p(_w(324), ZW, 110)[1], 'radius': 160, 'color': '#ffe6aa',
             'intensity': 0.5},                                                         # els apliques
        ],
    },
}
