"""
La cabina de la Capitana. EN 3D (hd640/tres_d.py), a 1×.

Una càmera alta que mira de biaix la cantonada del fons a l'esquerra, amb el sostre baix:
  - a la paret de l'esquerra, en escorç, la **porta** estanca oberta al passadís (el camí cap al fons), la gorra i
    l'anorac penjats i l'ull de bou;
  - a la paret del fons, el rellotge i el baròmetre, el prestatge dels llibres amb el model de l'Arenga i la **carta
    nàutica**; a sota de la carta, la llitera de teca encastada, amb volum (la manta, el coixí, els calaixos);
  - l'**escriptori** de teca, separat de la paret i girat, amb el **contracte**, la **novel·la**, el flexo, la tassa i
    la foto a sobre; la cadira al davant i la catifa, girades amb ell; s'hi passa per darrere (la Capitana hi espera);
  - primer pla: la canonada i els cables del sostre, una columna a la dreta i un bagul en silueta a l'esquerra.

Tot el detall ve del dibuix pla de sempre (cabina_capitana_pla_comu.py), projectat; l'ull de bou de dia és un
decorat 3D (en surt la diferència) i el rellotge, una capa per la paret.

El món: x a la dreta (0 = la paret de la porta), y amunt (0 = el terra), z cap al fons (300 = la paret del fons);
1 unitat = 1 píxel de sala a la distància on un personatge fa ≈110 px (escala 1).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from PIL import Image

from hd.pix import Canvas, Light, W, H, hr, mix
from hd.rooms.arenga import CAB, WHITEP, REDP, YELL, BRASS, box
from hd.rooms.comu import _diff
from hd.rooms.exterior import fbm
from hd.rooms.principal import CREAM, TEAK, LINO, NIGHT, DAYSKY, DAYSEA, day_porthole, second_hand
from hd.rooms.laboratori import PAPERC
from hd640.rooms import cabina_capitana_pla_comu as PL
from hd640.rooms.laboratori_pla_comu import wall, lamp
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
ZW = 300                                           # la paret del fons
FY = PL.FLOOR_Y                                    # al dibuix pla, el terra (203)
HW = FY - PL.CEIL_H                                # l'alçada de les parets (179)
XL = 160                                           # al dibuix pla, la cantonada: a l'esquerra, la paret de la porta
XR = 640                                           # la paret de la dreta
ZN = -260
DESK = (150, 222, 187, 50, FY - PL.DESK[1] - 6, 0.16)   # l'escriptori: x, z del centre, ample, fons, alçada, gir
BUNK = (PL.DESK[2] - XL + 30, 637 - XL, 66, FY - 160)   # la llitera: x0, x1, fons, alçada del matalàs
LAMPS = ((PL.LAMPS[0][0] - XL + 40, 200), (PL.LAMPS[1][0] - XL, 150))


def _w(fx):
    return fx - XL


def _wz(fx):
    return ZW - XL + fx


def _y(fy):
    return FY - fy


DOOR = (_wz(19), _wz(75), _y(88))
PORT = (_wz(PL.PORT[0]), _y(PL.PORT[1]), PL.PORT[2])

CAM = Camera(pos=(320, 160, -230), yaw=-0.22, pitch=0.2, f=400, centre=(330, 108))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)
FLEXO_W = None                                     # (es calcula més avall: on és el flexo, al món)


def _desk_P(fx, y, lz):
    """Un punt de l'escriptori: `fx` és la x del dibuix pla (229..416), `lz` des del davant."""
    cx, cz, w, d, h, a = DESK
    c, s_ = math.cos(a), math.sin(a)
    X, Z = (fx - PL.DESK[0]) * w / (PL.DESK[2] - PL.DESK[0]) - w / 2, lz - d / 2
    return (cx + X * c - Z * s_, y, cz + X * s_ + Z * c)


FLEXO_W = _desk_P(PL.FLEXO[0] + 12, DESK[4] + 30, 30)
LLUMS = [Llum((x, HW - 10, z), 250, 1.6, power=1.4) for x, z in LAMPS] + [
    Llum(FLEXO_W, 140, 1.6, power=1.6),
    Llum((10, PORT[1], PORT[0]), 110, 0.4, power=1.6)]


# ─── Les textures: el dibuix pla de sempre ───────────────────────────────────

def _glass(cv, t, day):
    """El vidre de l'ull de bou, amb `t` (0..1 del bucle): l'horitzó puja i baixa amb el balanceig i les ratlles
    d'onada corren (el de la sala plana d'abans)."""
    cx, cy, r = PL.PORT
    ph = t * 2 * math.pi
    hz = cy + r * 0.15 + math.sin(ph) * 2.2
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if math.hypot(x - cx, y - cy) > r:
                continue
            crest = math.sin(x * 0.55 + y * 1.8 - ph * 2)
            if day:
                if y < hz:
                    cl = hr(int(x // 6), int(y // 3), 0)
                    cv.put(x, y, DAYSKY, 4.2 + (y - (cy - r)) / (r * 2.2) * 1.4 - (0.7 if cl > 0.75 else 0), lit=0.08)
                else:
                    cv.put(x, y, DAYSEA, 4.4 - (y - hz) / (r * 0.9) + (1.2 if crest > 0.8 else 0), lit=0.08)
            else:
                if y < hz:
                    cl = hr(int(x // 5), int(y // 3), 0)
                    cv.put(x, y, NIGHT, 2.0 + (hz - y) / (r * 2) + (0.8 if cl > 0.72 else 0), lit=0.1)
                else:
                    cv.put(x, y, NIGHT, 1.6 - (y - hz) / (r * 1.6) + (1.6 if crest > 0.85 else 0), lit=0.1)
    shine_c = (236, 240, 244) if day else (200, 210, 230)
    for i in range(-r // 2, r // 3):
        x, y = cx - r // 3 + i, cy - r // 2 - i // 2
        cv.flat(x, y, mix(cv.get(x, y), shine_c, 0.35))


def _paret(dia=False, vidre=None, segon=None):
    """Les dues parets planes, de cara: la porta, la gorra, l'ull de bou, el rellotge, els llibres i la carta."""
    cv = Canvas(light=PL.LIGHT)
    wall(cv, dado=FY, rail=FY + 20, seed=3)
    PL.wainscot(cv)
    PL.watertight_door(cv)
    PL.cap_hook(cv)
    PL._porthole(cv, PL.PORT[0], PL.PORT[1], PL.PORT[2], None, rim=4)
    box(cv, PL.PORT[0] - 2, PL.PORT[1] + PL.PORT[2] + 5, PL.PORT[0] + 2, PL.PORT[1] + PL.PORT[2] + 9, BRASS, 3.2)
    PL.clock_barometer(cv)
    PL.bookshelf(cv)
    PL.sea_chart(cv)
    if dia:
        day_porthole(cv, *PL.PORT)
    if vidre is not None:
        _glass(cv, vidre, dia)
    if segon is not None:
        second_hand(cv, 191, 68, segon, r=7)
    return cv.img


@functools.lru_cache(maxsize=None)
def _paret_base(dia=False):
    return _paret(dia)


@functools.lru_cache(maxsize=None)
def _paret_nua():
    cv = Canvas(light=PL.LIGHT)
    wall(cv, dado=FY, rail=FY + 20, seed=3)
    PL.wainscot(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _mobles():
    """L'escriptori, la cadira, les coses de damunt, la llitera i la catifa, plans sobre transparent."""
    cv = Canvas(light=PL.LIGHT, transparent=True)
    PL.desk(cv)
    PL.desk_things(cv)
    PL.contract(cv)
    PL.novel(cv)
    PL.bunk(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _cadira():
    cv = Canvas(light=PL.LIGHT, transparent=True)
    PL.chair(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _llum_pla():
    cv = Canvas(80, 40, light=PL.LIGHT, transparent=True)
    lamp(cv, 40, 10)
    return cv.img


DESK_BOX = (PL.DESK[0], PL.DESK[1] + 14, PL.DESK[2] + 1, PL.DESK[3] + 1)   # el davant de l'escriptori
CHAIR_BOX = (293, 140, 338, 217)
FLEXO_BOX = (378, 110, 412, 153)
CUP_BOX = (235, 133, 255, 151)
PHOTO_BOX = (366, 126, 386, 151)
CONTRACT_BOX = (258, 137, 311, 153)
NOVEL_BOX = (330, 132, 362, 153)
BUNK_BOX = (PL.DESK[2] + 16, 179, 638, FY + 6)                             # el davant de la llitera (post i calaixos)
LAMP_BOX = (612, 132, 630, 152)                                            # el llum de lectura


# ─── Les superfícies ────────────────────────────────────────────────────────

def _terra(s, t, P):
    """Linòleum vermell fosc en tires de 40 que fugen, juntes de testa."""
    x, z = P[0], P[2]
    tira = math.floor(x / 40)
    v = 3.4 + (hr(tira, 5) - 0.5) * 0.5 + (fbm(x / 70, z / 40, 7) - 0.5) * 0.7
    v += (hr(int(x) // 4, int(z) // 4, 3) - 0.5) * 0.35
    if x % 40 < 1.0:
        return 1.8
    if int(z + hr(tira, 9) * 160) % 160 < 1.0:
        return 2.2
    return v


def _sostre(s, t, P):
    x = P[0]
    if (x + 13) % 96 < 10:
        return 2.6 + (0.6 if (x + 13) % 96 < 2 else 0)
    return 1.8 + (fbm(x / 50, P[2] / 50, 3) - 0.5) * 0.6


FOSC = [(4, 3, 2), (9, 6, 4), (15, 10, 7), (22, 15, 10), (31, 22, 15), (42, 30, 20)]
NAVY = PL.NAVY


def escena(cv, tex, estat=frozenset()):
    """Tota la sala, de lluny a prop. `estat`: els decorats ('dia'). → l'Escena (qui ha pintat què)."""
    e = Escena(cv, CAM, LLUMS, ambient=-0.3)
    paret, nua, mob = tex['paret'], tex['nua'], tex['mobles']
    e.quad('sostre', (0, HW, ZN), (XR, HW, ZN), (XR, HW, ZW), (0, HW, ZW), ramp=CREAM, lvl=_sostre, dues_cares=True)
    e.quad('paret_esq_prop', (0, HW, ZN), (0, HW, ZW - XL), (0, 0, ZW - XL), (0, 0, ZN),
           tex=(nua, (W - (ZW - XL - ZN), PL.CEIL_H, W, FY)))
    e.quad('paret_esq', (0, HW, ZW - XL), (0, HW, ZW), (0, 0, ZW), (0, 0, ZW - XL), tex=(paret, (0, PL.CEIL_H, XL, FY)))
    e.quad('paret_fons', (0, HW, ZW), (W - XL, HW, ZW), (W - XL, 0, ZW), (0, 0, ZW), tex=(paret, (XL, PL.CEIL_H, W, FY)))
    e.quad('paret_fons_dreta', (W - XL, HW, ZW), (XR, HW, ZW), (XR, 0, ZW), (W - XL, 0, ZW),
           tex=(nua, (0, PL.CEIL_H, XR - (W - XL), FY)))
    e.quad('paret_dreta', (XR, HW, ZW), (XR, HW, ZN), (XR, 0, ZN), (XR, 0, ZW), tex=(nua, (60, PL.CEIL_H, 60 + ZW - ZN, FY)))
    e.quad('terra', (0, 0, ZW), (XR, 0, ZW), (XR, 0, ZN), (0, 0, ZN), ramp=LINO, lvl=_terra)
    for lx, lz in LAMPS:
        e.claror((lx - 120, 0.3, lz + 120), (lx + 120, 0.3, lz + 120), (lx + 120, 0.3, lz - 120), (lx - 120, 0.3, lz - 120),
                 (255, 214, 140), lambda s, t: 0.26 * max(0.0, 1 - math.hypot(s - 120, t - 120) / 120) ** 1.3)
    dz0, dz1, dh = DOOR
    e.claror((0, 0.4, dz1 + 10), (90, 0.4, dz1 + 50), (90, 0.4, dz0 - 40), (0, 0.4, dz0 - 4), (230, 200, 140),
             lambda s, t: 0.3 * max(0.0, 1 - s / 90) * max(0.0, math.sin(math.pi * min(1.0, t / max(1.0, 60 + 0.9 * s)))))
    if 'dia' in estat:
        pz = PORT[0]
        e.claror((0, 0.5, pz + 30), (240, 0.5, pz - 50), (240, 0.5, pz - 150), (0, 0.5, pz - 60), (210, 226, 236),
                 lambda s, t: 0.34 * max(0.0, 1 - s / 240) * max(0.0, 1 - abs(t - 50) / 45))
    # la catifa, girada amb l'escriptori, davant seu
    cx, cz, dw, dd, dh_, da = DESK
    c, s_ = math.cos(da), math.sin(da)

    def Pr(lx, lz):
        return (cx + lx * c - lz * s_, 0.4, cz + lx * s_ + lz * c)
    RW, RD = 200, 74

    def catifa(s, t, P):
        vora = min(s, t, RW - s, RD - t)
        if vora < 2:
            return 2.2 + (1.0 if int(s) % 3 == 0 else 0)                  # el serrell
        if vora < 7:
            return -9 if False else 2.6
        d = abs(s - RW / 2) / 34 + abs(t - RD / 2) / 16
        base = 2.8 + (0.4 if (int(s) // 3 + int(t)) % 6 == 0 else 0) + (hr(int(s) // 5, int(t), 2) - 0.5) * 0.3
        if 0.7 < d < 1.0:
            return 1.8
        return base
    e.quad('catifa', Pr(-RW / 2, -dd / 2 - 8), Pr(RW / 2, -dd / 2 - 8), Pr(RW / 2, -dd / 2 - 8 - RD), Pr(-RW / 2, -dd / 2 - 8 - RD),
           ramp=NAVY, lvl=catifa,
           tint=None)
    # (la vora vermella i el rombe: una segona passada)
    e.claror(Pr(-RW / 2 + 2, -dd / 2 - 10), Pr(RW / 2 - 2, -dd / 2 - 10), Pr(RW / 2 - 2, -dd / 2 - 6 - RD),
             Pr(-RW / 2 + 2, -dd / 2 - 6 - RD), (150, 40, 34),
             lambda s, t: 0.75 if (min(s, t, RW - 4 - s, RD - 4 - t) < 5 or
                                   0.7 < abs(s - RW / 2 + 2) / 34 + abs(t - RD / 2 + 2) / 16 < 1.0) else 0.0)
    # la foscor dels racons
    e.foscor('racons', (0, 0.5, ZW), (XR, 0.5, ZW), (XR, 0.5, ZN), (0, 0.5, ZN),
             lambda s, t: max(0.6 * max(0.0, 1 - t / 26), 0.5 * max(0.0, 1 - s / 22), 0.5 * max(0.0, 1 - (XR - s) / 30)))
    e.foscor('cantonada', (0, HW, ZW - 0.5), (60, HW, ZW - 0.5), (60, 0, ZW - 0.5), (0, 0, ZW - 0.5),
             lambda s, t: 0.5 * max(0.0, 1 - s / 60))
    e.foscor('cantonada2', (0.5, HW, ZW - 60), (0.5, HW, ZW), (0.5, 0, ZW), (0.5, 0, ZW - 60),
             lambda s, t: 0.5 * max(0.0, 1 - (60 - s) / 60))
    e.foscor('sostre_fosc', (0, HW - 0.5, ZW - 0.6), (XR, HW - 0.5, ZW - 0.6), (XR, 0, ZW - 0.6), (0, 0, ZW - 0.6),
             lambda s, t: 0.4 * max(0.0, 1 - t / 40))
    for z in (ZW - XL - 108 + 96 * k for k in range(-3, 1)):
        if z < ZN + 10:
            continue
        e.caixa('quadernes', 0, 7, 0, HW, z, z + 6, CREAM, 3.6,
                cares={'dreta': {'ramp': CREAM, 'lvl': lambda s, t, P: 4.2 - (1.2 if int(t) % 14 == 0 else 0)},
                       'davant': {'ramp': CREAM, 'lvl': 2.6}})
    e.tub('canonades', (16, HW - 8, ZW), (16, HW - 8, ZN + 40), 4, REDP, 3.4, brides=70)
    e.tub('canonades', (30, HW - 6, ZW), (30, HW - 6, ZN + 40), 2.5, WHITEP, 3.2, brides=90)
    e.tub('canonades', (0, HW - 7, ZW - 6), (XR, HW - 7, ZW - 6), 4, REDP, 3.0, brides=120)
    # la llitera encastada, sota la carta: el davant (la post i els calaixos), la manta i el coixí
    bx0, bx1, bd, bh = BUNK
    e.foscor('ombra_llitera', (bx0 - 8, 0.6, ZW), (bx1 + 8, 0.6, ZW), (bx1 + 8, 0.6, ZW - bd - 16), (bx0 - 8, 0.6, ZW - bd - 16),
             lambda s, t: 0.55 * min(1.0, max(0.0, (bd + 16 - t) / 16)))
    e.caixa('llitera', bx0, bx1, 0, bh - 16, ZW - bd, ZW, TEAK, 3.0,
            cares={'davant': {'tex': (mob, (BUNK_BOX[0], BUNK_BOX[1] + 1, BUNK_BOX[2], BUNK_BOX[3]))},
                   'esquerra': {'ramp': TEAK, 'lvl': lambda s, t, P: 3.4 + math.sin(t * 0.5 + s * 0.05) * 0.2}})

    def manta(s, t, P):
        v = 3.4 + math.sin(s * 0.09 + t * 0.22) * 0.3 - t * 0.008
        return v
    e.caixa('llitera', bx0 + 4, bx1, bh - 16, bh - 2, ZW - bd + 6, ZW, NAVY, 3.0,
            cares={'dalt': {'ramp': NAVY, 'lvl': manta},
                   'davant': {'ramp': NAVY, 'lvl': lambda s, t, P: 3.2 + (1.4 if abs(t - 7) < 1.2 else 0)},
                   'esquerra': {'ramp': NAVY, 'lvl': 2.6}})
    e.quad('llitera', (bx0 + 4, bh - 1.5, ZW - bd + 6 + 18), (bx1, bh - 1.5, ZW - bd + 6 + 18), (bx1, bh - 1.5, ZW - bd + 6 + 14),
           (bx0 + 4, bh - 1.5, ZW - bd + 6 + 14), ramp=REDP, lvl=3.4)
    e.caixa('llitera', bx0, bx0 + 6, 0, bh + 6, ZW - bd, ZW, TEAK, 3.8, cares={'dalt': {'ramp': TEAK, 'lvl': 5.0}})
    e.caixa('llitera', bx0, bx1, bh - 18, bh - 10, ZW - bd - 2, ZW - bd + 4, TEAK, 4.4,
            cares={'dalt': {'ramp': TEAK, 'lvl': 5.4}})                      # la post alta del davant
    e.caixa('llitera', bx1 - 42, bx1 - 4, bh - 2, bh + 9, ZW - 40, ZW - 4, PAPERC, 4.2,
            cares={'dalt': {'ramp': PAPERC, 'lvl': lambda s, t, P: 4.6 - (1.0 if abs(s - 14 - t * 0.3) < 0.8 else 0)}})
    e.sprite('llitera', mob.crop(LAMP_BOX), (621 - LAMP_BOX[0], LAMP_BOX[3] - LAMP_BOX[1]), (_w(621), bh + 20, ZW - 2))
    # l'escriptori, separat de la paret i girat: el davant (el dibuix pla), el sobre i el costat
    e.foscor('ombra_escriptori', *[_desk_P(fx, 0.6, lz) for fx, lz in ((PL.DESK[0] - 12, dd + 16), (PL.DESK[2] + 12, dd + 16),
                                                                         (PL.DESK[2] + 12, -14), (PL.DESK[0] - 12, -14))],
             lambda s, t: 0.6 * min(1.0, min(s, t, dw + 24 - s, dd + 30 - t) / 14))
    e.caixa_girada('escriptori', cx, cz, dw - 4, dd - 4, dh_ - 5, da, TEAK, 2.6,
                   cares={'davant': {'tex': (mob, DESK_BOX)},
                          'esquerra': {'ramp': TEAK, 'lvl': lambda s, t, P: 3.4 + math.sin(t * 0.6 + s * 0.04) * 0.25},
                          'dreta': {'ramp': TEAK, 'lvl': 2.6}})

    def sobre(s, t, P):
        return 4.0 + math.sin(s * 0.3 + t * 0.9) * 0.15 + (fbm(s / 30, t / 6, 2) - 0.5) * 0.5
    e.caixa_girada('escriptori', cx, cz, dw, dd, 5, da, TEAK, 4.4, y0=dh_ - 5,
                   cares={'dalt': {'ramp': TEAK, 'lvl': sobre}, 'davant': {'ramp': TEAK, 'lvl': 4.6},
                          'esquerra': {'ramp': TEAK, 'lvl': 3.8}})
    # damunt: el contracte i la novel·la (estesos), la tassa, la foto i el flexo (drets)
    for sid, bx, l0, l1 in (('contracte', CONTRACT_BOX, 6, 28), ('novella', NOVEL_BOX, 8, 26)):
        e.quad(sid, _desk_P(bx[0], dh_ + 0.6, l1), _desk_P(bx[2], dh_ + 0.6, l1), _desk_P(bx[2], dh_ + 0.6, l0),
               _desk_P(bx[0], dh_ + 0.6, l0), tex=(mob, bx))
    e.sprite('tassa', mob.crop(CUP_BOX), (242 - CUP_BOX[0], 149 - CUP_BOX[1]), _desk_P(242, dh_, 22))
    e.sprite('foto', mob.crop(PHOTO_BOX), (375 - PHOTO_BOX[0], 149 - PHOTO_BOX[1]), _desk_P(375, dh_, 38))
    e.sprite('flexo', mob.crop(FLEXO_BOX), (PL.FLEXO[0] - FLEXO_BOX[0], PL.FLEXO[1] - FLEXO_BOX[1] + 2),
             _desk_P(PL.FLEXO[0], dh_, 34))
    # la llum del flexo, damunt del sobre
    fP = _desk_P(PL.FLEXO[0] + 14, dh_ + 0.8, 20)
    e.claror(_desk_P(PL.FLEXO[0] - 50, dh_ + 0.8, dd), _desk_P(PL.DESK[2], dh_ + 0.8, dd), _desk_P(PL.DESK[2], dh_ + 0.8, 0),
             _desk_P(PL.FLEXO[0] - 50, dh_ + 0.8, 0), (255, 220, 150),
             lambda s, t: 0.35 * max(0.0, 1 - math.hypot(s - 60, t - 26) / 60))
    del fP
    # la cadira, davant l'escriptori (el dibuix pla, dret), amb la seva ombra
    chP = _desk_P(315, 0, -26)
    e.foscor('ombra_cadira', (chP[0] - 22, 0.7, chP[2] + 14), (chP[0] + 22, 0.7, chP[2] + 14), (chP[0] + 22, 0.7, chP[2] - 14),
             (chP[0] - 22, 0.7, chP[2] - 14), lambda s, t: 0.6 * max(0.0, 1 - ((s - 22) / 22) ** 2 - ((t - 14) / 14) ** 2) * 1.6)
    e.sprite('cadira', tex['cadira'].crop(CHAIR_BOX), (315 - CHAIR_BOX[0], 215 - CHAIR_BOX[1]), chP)
    # els llums del sostre
    lp = _llum_pla()
    for lx, lz in LAMPS:
        e.sprite('llums', lp, (40, 6), (lx, HW - 2, lz))
    # primer pla: una canonada que travessa el sostre, cables que pengen, una columna a la dreta i un bagul
    e.tub('primer_pla', (-40, HW - 6, -70), (XR + 40, HW - 6, -70), 7, FOSC, 2.4, brides=90)
    for k, (xa, xb, cai) in enumerate(((40, 130, 16), (400, 490, 14))):
        pts = [(xa + (xb - xa) * i / 8, HW - 10 - cai * math.sin(math.pi * i / 8), -64 + k * 6) for i in range(9)]
        e.cable('primer_pla', pts, FOSC, 2.0, gruix=2.6)
    e.tub('primer_pla', (445, 0, 12), (445, HW, 12), 8, FOSC, 2.2, brides=56)
    e.caixa_girada('primer_pla', 26, 18, 40, 26, 24, 0.5, FOSC, 2.0,
                   cares={'dalt': {'ramp': FOSC, 'lvl': lambda s, t, P: 2.8 - (1.2 if abs(t - 16) < 1 else 0)},
                          'davant': {'ramp': FOSC, 'lvl': lambda s, t, P: 1.4 + (1.2 if abs(s - 25) < 3 and 18 < t < 24 else 0)
                                     + (0.8 if t < 3 else 0)},
                          'dreta': {'ramp': FOSC, 'lvl': 2.2}})
    return e


# ─── Composició ─────────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _textures(dia=False):
    return {'paret': _paret_base(dia), 'nua': _paret_nua(), 'mobles': _mobles(), 'cadira': _cadira()}


def _render(estat=frozenset(), tex=None):
    cv = Canvas(light=LIGHT)
    e = escena(cv, tex or _textures('dia' in estat), estat)
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)
    return cv.img, e


@functools.lru_cache(maxsize=None)
def _base(estat=frozenset()):
    return _render(estat)


def bg(cv):
    cv.img.paste(_base()[0])
    cv.P = cv.img.load()


def _decorat(*estat):
    def draw(cv):
        img, _ = _base(frozenset(estat))
        cv.img.alpha_composite(_diff(img, _base()[0]))
        cv.P = cv.img.load()
    return draw


# Escenes 2 i 3: de dia, el vidre de l'ull de bou clar i la claror pel terra
PROPS = {'ulls_dia': _decorat('dia')}


# ─── Animacions ─────────────────────────────────────────────────────────────

def _fotograma(capes, estat=frozenset()):
    img = _base(estat)[0]
    out = img.copy()
    for c in capes:
        out.alpha_composite(c)
    return _diff(out, img)


def _frames_port(dia):
    estat = frozenset({'dia'}) if dia else frozenset()
    _, e = _base(estat)
    return [_fotograma([e.capa(_paret(dia, vidre=i / 12), {'paret_esq'})], estat) for i in range(12)]


def _frames_rellotge():
    _, e = _base()
    return [_fotograma([e.capa(_paret(segon=s), {'paret_fons'})]) for s in range(60)]


ANIMS = {'mar': {'frames': lambda: _frames_port(False), 'frameDuration': 220},
         'ulls_dia_mar': {'frames': lambda: _frames_port(True), 'frameDuration': 220},
         'rellotge': {'frames': _frames_rellotge, 'frameDuration': 1000}}


# ─── Capes del davant i geometria (coordenades de sala, projectades) ─────────

def _amo(ids, estat=frozenset()):
    def mask(x, y):
        _, e = _base(estat)
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


def _pd(fx, lz, y=0.0):
    P = _desk_P(fx, y, lz)
    return _p(P[0], P[2], y)


_CHAIR = _desk_P(315, 0, -26)

FRONT = [
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 30},
    {'id': 'davant_escriptori', 'mask': _amo({'escriptori', 'contracte', 'novella', 'tassa', 'foto', 'flexo'}),
     'baseline': _pd((PL.DESK[0] + PL.DESK[2]) / 2, -2)[1], 'zIndex': 20},
    {'id': 'davant_cadira', 'mask': _amo({'cadira'}), 'baseline': _p(_CHAIR[0], _CHAIR[2])[1], 'zIndex': 20},
]


def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


def _v_escala(k):
    lo, hi = -2000.0, 3000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.escala((260, 0, z)) > k:
            lo = z
        else:
            hi = z
    return CAM.projecta((260, 0, lo))[1]


def _talla(poly, vmax):
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


# El terra on es camina: de la porta fins davant la llitera encastada; l'escriptori és un forat (s'hi passa per
# darrere).
WALK_MON = [(12, ZW - 10), (BUNK[0] - 8, ZW - 10), (BUNK[0] - 8, ZW - BUNK[2] - 12), (XR - 40, ZW - BUNK[2] - 12),
            (XR - 40, -200), (12, -200)]
_WALK = _talla([_p(x, z) for x, z in WALK_MON], _v_escala(1.2))
_FORAT = [_pd(fx, lz) for fx, lz in ((PL.DESK[0] - 6, DESK[3] + 6), (PL.DESK[2] + 6, DESK[3] + 6),
                                      (PL.DESK[2] + 6, -6), (PL.DESK[0] - 6, -6))]
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)
# Darrere l'escriptori no s'hi camina (tasca 316): si no, per parlar amb la Capitana, la Vet s'hi posava al costat,
# com si hagués travessat l'escriptori. El contorn s'atura al davant de l'escriptori. (La
# perspectiva, amb el contorn sencer, de dalt.)
_WALK = [(175, 152), (190, 166), (358, 170), (379, 165), (639, 188), (639, 223), (34, 223)]
_DH = DESK[4]

GEOMETRIA = {
    'things': {
        'porta': {'rect': _rect_mon((0, DOOR[2] + 8, DOOR[0] - 8), (0, 0, DOOR[1] + 2)), 'walk': _p(40, (DOOR[0] + DOOR[1]) / 2)},
        'contracte': {'rect': _rect_mon(*[_desk_P(fx, y, lz) for fx in (CONTRACT_BOX[0], CONTRACT_BOX[2])
                                          for lz in (4, 30) for y in (_DH, _DH + 4)]),
                      'walk': _pd((CONTRACT_BOX[0] + CONTRACT_BOX[2]) / 2, -34)},
        'novella': {'rect': _rect_mon(*[_desk_P(fx, y, lz) for fx in (NOVEL_BOX[0], NOVEL_BOX[2])
                                        for lz in (6, 28) for y in (_DH, _DH + 6)]),
                    'walk': _pd((NOVEL_BOX[0] + NOVEL_BOX[2]) / 2, -34)},
        'carta': {'rect': _rect_mon((_w(437), _y(45), ZW), (_w(606), _y(136), ZW)),
                  'walk': _p(_w(521), ZW - BUNK[2] - 26)},
    },
    'spawns': {'iri': _p(120, 120), 'vet': _p(200, 100), 'capitana': _pd(330, DESK[3] + 26)},
    'walkable': _WALK,
    'forats': [],
    'floorSquash': 0.42,
    'characterShadow': {'enabled': True, 'color': '#120806', 'alpha': 0.45, 'squash': 0.4, 'core': 0.6,
                        'light': {'x': _p(*LAMPS[1])[0], 'y': _p(*LAMPS[1])[1], 'stretch': 0.6, 'reach': 160}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    'characterLights': {
        'ambient': '#a89880',
        'lights': [{'x': _p(lx, lz, HW - 10)[0], 'y': _p(lx, lz, HW - 10)[1], 'radius': 220, 'color': '#ffd68c',
                    'intensity': 0.7} for lx, lz in LAMPS] + [
            {'x': _p(FLEXO_W[0], FLEXO_W[2], FLEXO_W[1])[0], 'y': _p(FLEXO_W[0], FLEXO_W[2], FLEXO_W[1])[1],
             'radius': 120, 'color': '#ffdc96', 'intensity': 0.6}],
    },
}
