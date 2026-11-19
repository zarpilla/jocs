"""
Ni un ou — el passadís de la coberta principal de l'Arenga, de nit. EN 3D (hd640/tres_d.py), a 1×.

Una càmera alta, girada cap a proa, que mira el passadís de biaix: la paret de les portes fuig cap a la dreta, fins a
la cantonada del fons, on la paret de proa (la porta estanca de coberta) queda en escorç. D'esquerra (a prop) a dreta
(al fons):
  - la porta del **menjador**, oberta, amb la llum càlida de dins que s'escampa en diagonal pel terra; l'extintor;
  - les portes de la **infermeria**, del **laboratori** i de la **Capitana** (amb el rellotge entre totes dues);
  - l'**escala del pont**, que puja pel forat del sostre, i el **plànol d'emergència**;
  - el **forat de l'escala de baix**: el pou de debò, amb els graons que baixen i la llum verda de les màquines, i la
    barana groga al voltant;
  - al fons, la **porta de proa** (coberta), amb l'ull de bou.
Les canonades i la safata de cables del sostre fugen cap al fons; el carretó de la cuina, aparcat i girat, fa que es
passi per darrere d'alguna cosa; primer pla: la quaderna i les canonades de l'esquerra, i la safata de cables i els
cables que pengen, a dalt.

Tot el detall ve del dibuix pla de sempre (passadis_pla_comu.py), projectat: el decorat `ulls_dia` i l'animació del
`rellotge`, per les mateixes superfícies; la de `maquines`, la llum verda del pou que respira.

El món: x al llarg del passadís, cap a proa (0 = on comença el dibuix pla), y amunt (0 = el terra), z cap al fons
(300 = la paret de les portes); 1 unitat = 1 píxel de sala a la distància on un personatge fa ≈110 px (escala 1).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from PIL import Image

from hd.pix import Canvas, Light, W, H, hr
from hd.rooms.arenga import CAB, DARK, WHITEP, REDP, YELL, BRASS
from hd.rooms.comu import _diff
from hd.rooms.exterior import fbm
from hd.rooms.principal import CREAM, TEAK, LINO, wear, day_porthole, second_hand
from hd640.rooms import passadis_pla_comu as PL
from hd640.rooms.laboratori_pla_comu import wall, ceiling, lamp, lamp_glow
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
ZW = 300                                           # la paret de les portes
HW = PL.FLOOR_Y                                    # l'alçada de les parets (el dibuix pla fa 203 fins al terra)
XP = 570                                           # al dibuix pla, on comença la paret de proa (i x del món d'aquesta)
ZP = 262                                           # a la paret de proa, la z on cau la x 570 del dibuix pla
XL = -300                                          # on s'acaba el passadís per popa (fora de la pantalla)
HOLE = (472, 552, 254, 292)                        # el pou de l'escala de baix: x0, x1, z0, z1
TROLLEY = (232, 214, 50, 30, 0.32)                 # el carretó de la cuina: x, z, llarg, ample, gir
BUCKET = (92, 262)                                 # la galleda de la fregona (x, z)


def _w(fx):
    """Una x del dibuix pla de la paret de les portes → la x del món."""
    return fx


def _wz(fx):
    """Una x del dibuix pla de la paret de proa → la z del món."""
    return ZP - (fx - XP)


def _y(fy):
    """Una y del dibuix pla (el terra, a 203) → l'alçada del món."""
    return HW - fy


CAM = Camera(pos=(120, 170, -220), yaw=0.40, pitch=0.10, f=390, centre=(320, 90))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)  # (la llum és la del món: la de l'Escena)
MENJ_C = ((PL.D_MENJ[0] + PL.D_MENJ[2]) / 2, 60, ZW + 20)
HOLE_C = ((HOLE[0] + HOLE[1]) / 2, -20, (HOLE[2] + HOLE[3]) / 2)


def _llums(eng=0.35):
    return ([Llum((x, 176, ZW - 16), 210, 1.6, power=1.4) for x in PL.LAMPS]                  # els llums de sostre
            + [Llum(MENJ_C, 170, 1.3, power=1.5),                                            # el menjador
               Llum((HOLE_C[0], 10, HOLE_C[2]), 110, eng * 2.6, power=1.6),                  # les màquines, pel pou
               Llum(((PL.HOLE[0] + PL.HOLE[1]) / 2, HW, ZW - 30), 120, 0.6, power=1.6)]) # el pont, pel forat


# ─── Les textures: el passadís pla de sempre ──────────────────────────────────

def _llum_pla():
    """La llum del dibuix pla, sense la vinyeta ni l'enfosquiment de baix (ara la llum és la de l'escena)."""
    l = Light(ambient=PL.LIGHT.ambient + 0.25, vignette=None, floor_fade=None)
    l.points = list(PL.LIGHT.points)
    return l


def _canvas(transparent=False):
    return Canvas(light=_llum_pla(), transparent=transparent)


@functools.lru_cache(maxsize=None)
def _paret():
    """La paret de les portes i la de proa, de cara (sense el terra ni el forat de l'escala de baix)."""
    cv = _canvas()
    ceiling(cv)
    wall(cv, seed=1)
    wear(cv, 0, 40, W - 1, 168, 40, seed=1, k=0.25)
    PL.door_menjador(cv)
    PL.extinguisher(cv, 82, 128)
    PL.door_infermeria(cv)
    PL.door_laboratori(cv)
    PL.door_capitana(cv)
    PL.stairs_up(cv)
    PL.plan_board(cv)
    PL.door_proa(cv)
    PL.clock(cv)
    for lx in PL.LAMPS:
        lamp(cv, lx, PL.LAMP_Y)
    for lx in PL.LAMPS:
        lamp_glow(cv, lx, PL.LAMP_Y)
    return cv.img


@functools.lru_cache(maxsize=None)
def _nua():
    """La paret nua (crema, amb el sòcol i el passamà): per als trossos on el dibuix pla no arriba."""
    cv = _canvas()
    ceiling(cv)
    wall(cv, seed=3)
    wear(cv, 0, 40, W - 1, 168, 40, seed=3, k=0.25)
    return cv.img


# ─── Les superfícies ────────────────────────────────────────────────────────

def _terra(s, t, P):
    """El linòleum, en coordenades del món: les tires de 80 al llarg del passadís, la veta fina, i gastat pel mig."""
    x, z = P[0], P[2]
    v = 3.6 + (hr(int(x // 4), int(z // 3), 2) - 0.5) * 0.45 + (fbm(x / 90, z / 40, 3) - 0.5) * 0.7
    if z % 80 < 1.1:
        v -= 1.2                                                    # les juntes de les tires
    elif x % 160 < 0.9:
        v -= 0.8                                                    # les juntes de testa
    worn = max(0.0, 1 - abs(z - 250) / 30)
    v += worn * 0.4 * (0.5 + 0.5 * hr(int(x) // 3, int(z) // 2, 5))
    return v


def escena(cv, estat=frozenset(), eng=0.35):
    """Tot el passadís, de lluny a prop. `eng`: com de forta és la llum verda de les màquines. → l'Escena."""
    e = Escena(cv, CAM, _llums(eng), ambient=-0.5)
    zn = CAM.pos[2] + 40
    paret, nua = _paret(), _nua()
    # el sostre, baix, crema
    e.quad('sostre', (XL, HW, zn), (XP, HW, zn), (XP, HW, ZW), (XL, HW, ZW), ramp=CREAM,
           lvl=lambda s, t, P: 2.6 - (1.0 if P[2] % 70 < 5 else 0), dues_cares=True)
    # la paret de les portes (z = 300): de popa, la paret nua; després el dibuix pla fins a la cantonada de proa
    e.quad('paret_popa', (XL, HW, ZW), (0, HW, ZW), (0, 0, ZW), (XL, 0, ZW), tex=(nua, (W + XL, 0, W, HW)))
    e.quad('paret_fons', (0, HW, ZW), (XP, HW, ZW), (XP, 0, ZW), (0, 0, ZW), tex=(paret, (0, 0, XP, HW)))
    # la paret de proa (x = 570): la cantonada nua, la porta de coberta i, cap a la càmera, més paret
    e.quad('paret_proa_fons', (XP, HW, ZW), (XP, HW, ZP), (XP, 0, ZP), (XP, 0, ZW), tex=(nua, (100, 0, 100 + ZW - ZP, HW)))
    e.quad('paret_proa', (XP, HW, ZP), (XP, HW, ZP - (W - XP)), (XP, 0, ZP - (W - XP)), (XP, 0, ZP),
           tex=(paret, (XP, 0, W, HW)))
    e.quad('paret_proa_prop', (XP, HW, ZP - (W - XP)), (XP, HW, zn), (XP, 0, zn), (XP, 0, ZP - (W - XP)),
           tex=(nua, (200, 0, 200 + ZP - (W - XP) - zn, HW)))
    # el pou de l'escala de baix (per sota del terra: es pinta abans, i el terra hi deixa el forat)
    x0, x1, z0, z1 = HOLE
    D = 90
    ENGG = PL.ENGG + [(60, 120, 90), (90, 160, 120)]
    e.quad('pou', (x0, 0, z1), (x1, 0, z1), (x1, -D, z1), (x0, -D, z1), ramp=ENGG,
           lvl=lambda s, t, P: 1.0 + eng * 3 * max(0.0, 1 - t / D) + (0.6 if int(s) % 26 < 2 else 0))
    e.quad('pou', (x0, 0, z0), (x0, 0, z1), (x0, -D, z1), (x0, -D, z0), ramp=ENGG, lvl=lambda s, t, P: 0.8 + eng * 2)
    e.quad('pou', (x1, 0, z1), (x1, 0, z0), (x1, -D, z0), (x1, -D, z1), ramp=ENGG, lvl=lambda s, t, P: 0.6 + eng * 2)
    for k in range(7):                                              # els graons, que baixen cap a la paret
        yk, zk = -9 * (k + 1), z0 + 4 + 5 * k
        e.caixa('pou', x0 + 10, x1 - 10, yk - 2, yk, zk, zk + 6, PL.ENGG + [(80, 90, 80)], 1.0,
                cares={'dalt': {'ramp': [(20, 22, 18), (40, 44, 36), (70, 76, 60), (120, 110, 40), (180, 150, 50)],
                                'lvl': lambda s, t, P, k=k: (3.6 if t > 4.5 else 2.0) - k * 0.35 + eng * 1.5},
                       'davant': {'ramp': CAB, 'lvl': 1.2 - k * 0.15}})
    # el terra, amb el forat del pou
    e.quad('terra', (XL, 0, ZW), (XP, 0, ZW), (XP, 0, zn), (XL, 0, zn), ramp=LINO, lvl=_terra,
           forma=lambda s, t: not (x0 < XL + s < x1 and z0 < ZW - t < z1))
    e.quad('pou', (x0, 0, z0), (x1, 0, z0), (x1, -6, z0), (x0, -6, z0), ramp=CAB, lvl=2.4)     # la brazola
    # la llum: els bassals dels llums (la reflexió al linòleum), la claror del menjador i la verda del pou
    for lx in PL.LAMPS:
        e.claror((lx - 90, 0.4, ZW), (lx + 90, 0.4, ZW), (lx + 90, 0.4, ZW - 160), (lx - 90, 0.4, ZW - 160),
                 (255, 214, 150), lambda s, t: 0.2 * max(0.0, 1 - math.hypot((s - 90) / 70, (t - 18) / 120)) ** 1.3)
    mx0, mx1 = PL.D_MENJ[0], PL.D_MENJ[2]
    e.claror((mx0, 0.5, ZW), (mx1, 0.5, ZW), (mx1 + 150, 0.5, ZW - 160), (mx0 + 70, 0.5, ZW - 170), (255, 186, 110),
             lambda s, t: 0.5 * max(0.0, 1 - t / 170) ** 1.2 * max(0.0, math.sin(math.pi * min(1.0, s / max(1.0, 51 + t * 0.4)))))
    e.claror((x0 - 70, 0.6, ZW), (x1 + 18, 0.6, ZW), (x1 + 18, 0.6, z0 - 80), (x0 - 70, 0.6, z0 - 80), (90, 200, 140),
             lambda s, t: eng * 0.9 * max(0.0, 1 - math.hypot((s - 110) / 100, (t - 30) / 70)) if not (
                 70 <= s <= 150 and t <= ZW - z0) else 0.0)
    e.claror((x0 - 40, HW, ZW - 0.4), (x1 + 18, HW, ZW - 0.4), (x1 + 18, 0, ZW - 0.4), (x0 - 40, 0, ZW - 0.4),
             (90, 200, 140), lambda s, t: eng * 0.7 * max(0.0, 1 - math.hypot((s - 80) / 80, (t - HW) / 70)))
    # la foscor dels racons i el peu de la paret
    e.foscor('racons', (XL, 0.5, ZW), (XP, 0.5, ZW), (XP, 0.5, zn), (XL, 0.5, zn),
             lambda s, t: max(0.5 * max(0.0, 1 - t / 18), 0.45 * max(0.0, 1 - (XP - XL - s) / 20)))
    e.foscor('cantonada', (XP - 40, HW, ZW - 0.5), (XP, HW, ZW - 0.5), (XP, 0, ZW - 0.5), (XP - 40, 0, ZW - 0.5),
             lambda s, t: 0.45 * max(0.0, 1 - (40 - s) / 40))
    for dx0, _, dx1, _ in (PL.D_INF, PL.D_LAB, PL.D_CAP):
        e.foscor('peu', (dx0 - 4, 0.6, ZW), (dx1 + 4, 0.6, ZW), (dx1 + 4, 0.6, ZW - 6), (dx0 - 4, 0.6, ZW - 6),
                 lambda s, t: 0.5 * (1 - t / 6))
    # les canonades i la safata de cables del sostre, que fugen cap a proa
    for yy, zz, r, ramp, lv in ((193, 290, 5, REDP, 2.6), (193, 276, 3.5, WHITEP, 2.4), (186, 288, 2.5, CAB, 3.0)):
        e.tub('canonades', (XL, yy, zz), (XP, yy, zz), r, ramp, lv, brides=74)
    e.caixa('safata', XL, XP, 196, 198, 236, 262, CAB, 2.2,
            cares={'sota': {'ramp': CAB, 'lvl': lambda s, t, P: 1.6 + (1.4 if int(P[0]) % 12 < 2 else 0)}})
    for x in range(-280, XP, 120):
        e.caixa('safata', x, x + 3, 192, HW, 236, 262, CAB, 2.8)
    # la barana groga del pou, amb les ratlles negres a la de davant
    YB = [(36, 28, 6), (78, 58, 10), (128, 96, 16), (178, 136, 24), (218, 174, 42), (244, 210, 88)]
    for px, pz in ((x0, z0), (x1, z0), (x0, z1 - 2), (x1, z1 - 2)):
        e.caixa('barana', px - 1.5, px + 1.5, 0, 42, pz - 1.5, pz + 1.5, YB, 3.2)
        e.caixa('barana', px - 3, px + 3, 0, 2, pz - 3, pz + 3, CAB, 2.6)
    for hy in (40, 21):
        e.cable('barana', [(x0, hy, z1 - 2), (x0, hy, z0), (x1, hy, z0), (x1, hy, z1 - 2)], YB, 3.6, gruix=2.4)
        for k in range(8):
            xa = x0 + 4 + k * 10
            e.cable('barana', [(xa, hy, z0), (xa + 4, hy, z0)], [(4, 4, 4), (14, 14, 14), (30, 30, 30)], 1.6, gruix=2.6)
    # el carretó de la cuina, aparcat i girat (s'hi passa per darrere)
    tx, tz, tl, ta, tg = TROLLEY
    e.foscor('ombra_carreto', (tx - 40, 0.6, tz + 30), (tx + 40, 0.6, tz + 30), (tx + 40, 0.6, tz - 30),
             (tx - 40, 0.6, tz - 30), lambda s, t: 0.55 * max(0.0, 1 - ((s - 40) / 36) ** 2 - ((t - 30) / 26) ** 2) * 1.5)
    c_, s_ = math.cos(tg), math.sin(tg)
    for lx, lz in ((-tl / 2 + 3, -ta / 2 + 3), (tl / 2 - 3, -ta / 2 + 3), (-tl / 2 + 3, ta / 2 - 3), (tl / 2 - 3, ta / 2 - 3)):
        px, pz = tx + lx * c_ - lz * s_, tz + lx * s_ + lz * c_
        e.caixa('carreto', px - 1.2, px + 1.2, 4, 46, pz - 1.2, pz + 1.2, WHITEP, 3.4)
        e.caixa('carreto', px - 2.5, px + 2.5, 0, 4, pz - 2.5, pz + 2.5, DARK, 2.0)
    for yy in (10, 44):
        e.caixa_girada('carreto', tx, tz, tl, ta, 2.5, tg, WHITEP, 3.6, y0=yy,
                       cares={'dalt': {'ramp': WHITEP, 'lvl': lambda s, t, P: 3.8 - (0.6 if s < 2 or s > tl - 2 else 0)}})
    e.caixa_girada('carreto', tx - 8, tz, 16, 12, 9, tg, [(40, 30, 20), (90, 60, 40), (140, 100, 60), (200, 160, 110)],
                   2.4, y0=46.5)                                                      # la safata de pa
    for k, (dx, col) in enumerate(((10, [(60, 14, 14), (130, 30, 28), (190, 70, 60)]),
                                   (17, [(14, 30, 60), (30, 60, 120), (80, 110, 170)]))):
        e.caixa_girada('carreto', tx + dx * c_, tz + dx * s_, 5, 5, 6, tg, col, 1.8, y0=46.5)  # les tasses
    e.caixa_girada('carreto', tx, tz, tl - 6, ta - 6, 10, tg, CREAM, 2.0, y0=12.5,
                   cares={'dalt': {'ramp': [(40, 30, 20), (90, 70, 50), (140, 110, 80)], 'lvl': 1.8}})  # la galleda
    e.cable('carreto', [(tx + (tl / 2) * c_ - (-ta / 2) * s_, 46, tz + (tl / 2) * s_ + (-ta / 2) * c_),
                        (tx + (tl / 2 + 6) * c_, 50, tz + (tl / 2 + 6) * s_),
                        (tx + (tl / 2) * c_ - (ta / 2) * s_, 46, tz + (tl / 2) * s_ + (ta / 2) * c_)], WHITEP, 3.6, gruix=2)
    # la galleda i la fregona, recolzada a la paret entre el menjador i la infermeria (s'hi passa per darrere)
    gx, gz = BUCKET
    e.foscor('ombra_galleda', (gx - 16, 0.6, gz + 14), (gx + 18, 0.6, gz + 14), (gx + 18, 0.6, gz - 16),
             (gx - 16, 0.6, gz - 16), lambda s, t: 0.6 * max(0.0, 1 - ((s - 17) / 16) ** 2 - ((t - 15) / 14) ** 2) * 1.5)
    e.caixa_girada('galleda', gx, gz, 20, 18, 22, 0.2, [(10, 20, 40), (20, 40, 80), (40, 70, 120), (80, 110, 160)], 2.2,
                   cares={'dalt': {'ramp': [(8, 12, 18), (20, 30, 40), (40, 60, 70)],
                                   'lvl': lambda s, t, P: 2.6 if s < 1.5 or t < 1.5 or s > 18.5 or t > 16.5 else 0.8}})
    e.cable('galleda', [(gx + 2, 20, gz), (gx + 8, 80, ZW - 30), (gx + 12, 130, ZW - 4)],
            [(30, 22, 12), (70, 50, 28), (120, 90, 50), (160, 130, 80)], 2.6, gruix=2.4)
    # primer pla: la quaderna i les canonades de l'esquerra, la safata de cables que passa per dalt i els cables
    FOSC = [(4, 3, 3), (9, 7, 6), (15, 12, 10), (22, 18, 15), (31, 25, 21), (42, 35, 29)]
    e.caixa('primer_pla', -16, 8, 0, HW, 148, 170, FOSC, 2.0,
            cares={'dreta': {'ramp': FOSC, 'lvl': lambda s, t, P: 2.4 - (1.4 if s < 2 else 0) + (1.0 if s > 21 else 0)
                             + (1.8 if (t % 18) < 2 and 6 < s < 20 else 0)},
                   'davant': {'ramp': FOSC, 'lvl': 1.4}})
    for xx, r in ((16, 6), (28, 4)):
        e.tub('primer_pla', (xx, 0, 158), (xx, HW, 158), r, FOSC, 2.4, brides=50)
    e.roca('primer_pla', (64, 0, 158), 22, FOSC, lvl=2.4, llum_dir=(0.6, -0.7), aplana=0.4, seed=5)   # el rotllo de corda
    for k in range(3):
        e.cable('primer_pla', [(46 + k * 4, 6 + k * 2, 152), (64, 9 + k * 2, 148 - k * 2), (82 - k * 4, 6 + k * 2, 154)],
                [(20, 16, 10), (50, 40, 26), (90, 74, 50), (130, 110, 74)], 2.0, gruix=2.4)
    e.caixa('primer_pla', -100, 700, 192, 197, 50, 68, FOSC, 1.6,
            cares={'sota': {'ramp': FOSC, 'lvl': lambda s, t, P: 1.4 + (1.6 if int(P[0]) % 16 < 3 else 0)},
                   'davant': {'ramp': FOSC, 'lvl': 2.2}})
    e.caixa_girada('primer_pla', 620, 120, 70, 50, 54, -0.3, FOSC, 2.0,                # les caixes de les armilles
                   cares={'dalt': {'ramp': FOSC, 'lvl': 3.0},
                          'davant': {'ramp': [(30, 10, 6), (70, 26, 12), (120, 50, 20), (170, 80, 30)],
                                     'lvl': lambda s, t, P: 1.6 + (1.6 if 18 < t < 34 and (s + t) % 10 < 5 else 0)}})
    return e


# ─── Composició ────────────────────────────────────────────────────────────

def _render(eng=0.35):
    cv = Canvas(light=LIGHT)
    e = escena(cv, eng=eng)
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)    # la barra de verbs: negre
    return cv.img, e


@functools.lru_cache(maxsize=None)
def _base():
    return _render()


def bg(cv):
    img, _ = _base()
    cv.img.paste(img)
    cv.P = cv.img.load()


def _flat(fn):
    cv = _canvas(transparent=True)
    fn(cv)
    return cv.img


def ulls_dia(cv):
    """Escenes 2 i 3: de dia, l'ull de bou de la porta de coberta, clar (projectat a la paret de proa)."""
    _, e = _base()
    cv.img.alpha_composite(e.capa(_flat(lambda c: day_porthole(c, *PL.PORT_PROA)), {'paret_proa'}))
    cv.P = cv.img.load()


PROPS = {'ulls_dia': ulls_dia}


# ─── Animacions ─────────────────────────────────────────────────────────────

def _frames_rellotge():
    """El rellotge del passadís: l'agulla dels segons (un fotograma per segon), projectada a la paret."""
    img0, e = _base()
    frames = []
    for s in range(60):
        cv = _canvas(transparent=True)
        second_hand(cv, PL.CLOCK[0], PL.CLOCK[1], s, r=6)
        img = img0.copy()
        img.alpha_composite(e.capa(cv.img, {'paret_fons'}))
        frames.append(_diff(img, img0))
    return frames


def _frames_maquines():
    """La llum verda de la sala de màquines, pel pou de l'escala, respira amb el motor: la diferència entre la sala
    amb la llum més forta i la de sempre, a la força de cada fotograma (només al voltant del pou)."""
    import numpy as np
    img0, e = _base()
    hi, _ = _render(eng=0.6)
    a0 = np.asarray(img0).astype(np.float32)
    d = np.asarray(hi).astype(np.float32) - a0
    frames = []
    for i in range(12):
        k = 0.35 + 0.14 * math.sin(2 * math.pi * i / 12)
        f = np.clip(a0 + d * (k - 0.35) / 0.25, 0, 255).astype(np.uint8)
        f[..., 3] = 255
        frames.append(_diff(Image.fromarray(f, 'RGBA'), img0))
    return frames


ANIMS = {'rellotge': {'frames': _frames_rellotge, 'frameDuration': 1000},
         'maquines': {'frames': _frames_maquines, 'frameDuration': 200}}


def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


def _llum_pj(P, radius, color, intensity, **kw):
    """Una llum del món (x, y, z), a la pantalla: una llum dels personatges (`characterLights`)."""
    u, v = _p(P[0], P[2], P[1])
    return {'x': u, 'y': v, 'radius': radius, 'color': color, 'intensity': intensity, **kw}


# Capes del davant: el primer pla (sempre davant), el carretó i la barana del pou (qui hi passa per darrere, hi queda
# darrere).
FRONT = [
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20},
    {'id': 'davant_galleda', 'mask': _amo({'galleda'}), 'baseline': _p(BUCKET[0], BUCKET[1] - 8)[1], 'zIndex': 20},
    {'id': 'davant_carreto', 'mask': _amo({'carreto'}), 'baseline': _p(TROLLEY[0], TROLLEY[1] - 8)[1], 'zIndex': 20},
    {'id': 'davant_barana', 'mask': _amo({'barana'}), 'baseline': _p((HOLE[0] + HOLE[1]) / 2, HOLE[2])[1],
     'zIndex': 20},
]


# ─── Geometria (coordenades de sala, projectades) ────────────────────────────

def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


def _talla(poly, vmax):
    """El polígon de pantalla retallat per sota de la y `vmax`."""
    out = []
    for (ax, ay), (bx, by) in zip(poly, poly[1:] + poly[:1]):
        if ay <= vmax:
            out.append((ax, ay))
        if (ay <= vmax) != (by <= vmax):
            k = (vmax - ay) / (by - ay)
            out.append((round(ax + (bx - ax) * k), vmax))
    return out


# El terra on es camina (al món): el passadís, arran de la paret de les portes, fins a la porta de proa; el pou de
# l'escala de baix no es trepitja.
WALK_MON = [(-40, 292), (HOLE[0] - 6, 292), (HOLE[0] - 6, HOLE[2] - 6), (HOLE[1] + 6, HOLE[2] - 6),
            (HOLE[1] + 6, 292), (XP - 6, 292), (XP - 6, 150), (300, 120), (60, 110), (-40, 110)]
V_MAX = 232                                        # més a prop, el personatge passaria d'1,2: és per al primer pla
_WALK = _talla([_p(x, z) for x, z in WALK_MON], V_MAX)
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)


def _escala_a(v):
    lo, hi = 1.0, 2000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.projecta((260, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((260, 0, (lo + hi) / 2))


def _wall(fx0, fy0, fx1, fy1):
    return _rect_mon((_w(fx0), _y(fy0), ZW), (_w(fx1), min(HW, _y(fy1)), ZW))


def _forat_carreto():
    tx, tz, tl, ta, tg = TROLLEY
    c_, s_ = math.cos(tg), math.sin(tg)
    a, b = tl / 2 + 3, ta / 2 + 3
    return [_p(tx + lx * c_ - lz * s_, tz + lx * s_ + lz * c_) for lx, lz in ((-a, -b), (a, -b), (a, b), (-a, b))]


def _door(d):
    x0, _, x1, _ = d
    return {'rect': _wall(x0 - 5, PL.PLAQUE_Y - 5, x1 + 6, PL.FLOOR_Y), 'walk': _p((x0 + x1) / 2, 274)}


GEOMETRIA = {
    'things': {
        'porta_menjador': _door(PL.D_MENJ),
        'porta_infermeria': _door(PL.D_INF),
        'porta_laboratori': _door(PL.D_LAB),
        'porta_capitana': _door(PL.D_CAP),
        'escala_amunt': {'rect': _wall(376, 5, 459, PL.FLOOR_Y), 'walk': _p(436, 278)},
        'escala_avall': {'rect': _rect_mon((HOLE[0] - 4, 44, HOLE[2] - 4), (HOLE[1] + 4, 44, HOLE[3]),
                                           (HOLE[0] - 4, 0, HOLE[2] - 4), (HOLE[1] + 4, 0, HOLE[2] - 4)),
                         'walk': _p((HOLE[0] + HOLE[1]) / 2, HOLE[2] - 14)},
        'porta_proa': {'rect': _rect_mon((XP, _y(59), _wz(573)), (XP, 0, _wz(632))),
                       'walk': _p(XP - 16, _wz((PL.D_PROA[0] + PL.D_PROA[2]) / 2))},
        'planol': {'rect': _wall(474, 64, 554, 132), 'walk': _p(514, HOLE[2] - 14)},
    },
    'spawns': {'iri': _p(300, 262), 'vet': _p(370, 240)},
    'walkable': _WALK,
    'forats': [_forat_carreto(), [_p(BUCKET[0] + dx, BUCKET[1] + dz) for dx, dz in ((-14, -13), (14, -13), (14, 13), (-14, 13))]],
    'floorSquash': 0.42,
    # L'ombra de contacte: el llum del mig (el punt del terra just a sota); curta, és llum de dalt.
    'characterShadow': {'enabled': True, 'color': '#120806', 'alpha': 0.42, 'squash': 0.4, 'core': 0.6,
                        'light': {'x': _p(PL.LAMPS[1], ZW - 16)[0], 'y': _p(PL.LAMPS[1], ZW - 16)[1], 'stretch': 0.55,
                                  'reach': 150}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    # La llum de la sala sobre els personatges (les de _llums, a la pantalla): els tres llums de sostre, càlids; la
    # porta del menjador, i el verd de les màquines que puja pel pou de l'escala.
    'characterLights': {
        'ambient': '#9c9282',
        'lights': [
            *[_llum_pj((x, 176, ZW - 16), 200, '#ffd28c', 0.6) for x in PL.LAMPS],           # els llums de sostre
            _llum_pj(MENJ_C, 140, '#ffc880', 0.5),                                        # el menjador
            _llum_pj((HOLE_C[0], 10, HOLE_C[2]), 100, '#78e6a0', 0.5),                    # les màquines, pel pou
        ],
    },
}
