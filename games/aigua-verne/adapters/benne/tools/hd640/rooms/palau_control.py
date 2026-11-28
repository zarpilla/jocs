"""
Aigua Verne — `palau_control` (P): la sala de control, sota la piscina central del palau. EN 3D (hd640/tres_d.py), a 1×.

Una càmera alta, girada cap a la cantonada de l'esquerra, mirant una mica avall:
  - el sostre és el fons de vidre de la piscina central (buida), inclinat com un finestral que baixa cap al fons: les
    bigues d'acer fugen, i a través del vidre es veu la rajola turquesa i la claror de la galeria de dalt;
  - el **tauler** de les vàlvules d'emergència és una consola separada de la paret, amb tres cares: el pupitre (la
    tapa amb els botons), el panell inclinat amb els tres **panys** (rètols T2, AQUA, FERRUM, cadascun amb el seu
    rellotge i el seu llum; decorats `obert_t2`, `obert_aqua`, `obert_ferrum`) i, a dalt, les pantalletes amb els
    tres dipòsits;
  - a la paret de l'esquerra, en escorç, l'**ascensor** de servei, obert: la cabina il·luminada fa una claror que
    s'escampa en diagonal pel terra; al costat, l'**interfon**;
  - a la dreta, el tub gruixut de la reserva del Magnat, que puja fins al vidre (s'hi passa per darrere), amb la
    **càmera** penjada (decorat `flors_camera`; ANIMS `camera_llum`, el llum vermell que fa pampallugues), i l'armari de
    la **palanca** vermella «RESERVA» (decorat `reserva_oberta`);
  - primer pla: una barana i una canonada gruixuda, fosques, tallades per la vora de baix.

Tot el detall ve de la sala plana de sempre (palau_control_pla_comu.py), dibuixada de cara i projectada.

El món: x a la dreta (0 = la paret de l'ascensor), y amunt (0 = el terra), z cap al fons (300 = la paret del fons);
1 unitat = 1 píxel de sala a la distància on un personatge fa 100 px (escala 1).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from PIL import Image

from hd.pix import Canvas, Light, W, H, hr
from hd.rooms.comu import _diff
from hd.rooms.exterior import fbm
from hd640.rooms import palau_control_pla_comu as PL
from hd640.rooms.palau_comu import (CROM, BLANC, BLAU, TURQ, VERMELL, NEGRE, MARB, ORP, lletres_c,
                                    lletres_grans, text_width, gota)
from hd640.tres_d import Camera, Escena, Llum, llum_personatges

ACER = PL.ACER
BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
ZW = 300                                           # la paret del fons
HB = 112                                           # l'alçada de la paret del fons (a dalt comença el vidre)
VID = ((HB, ZW), (300, 120))                       # el vidre del sostre: de (y, z) a (y, z) (inclinat)
CON = (56, 336, 212, 250)                         # la consola: x0, x1, z del davant, z del darrere
CON_ANG = -0.22                                     # el gir de la consola (no va a 90° de la paret)
FX = (146, 474)                                    # al pla, el tauler va de x 150 a 470 (amb el marge)


def _rc(x, y, z):
    """Un punt de la consola (en coordenades sense girar) al món: gira CON_ANG al voltant del seu centre."""
    x0, x1, zc, zb = CON
    cx, cz = (x0 + x1) / 2, (zc + zb) / 2
    c, s = math.cos(CON_ANG), math.sin(CON_ANG)
    return (cx + (x - cx) * c - (z - cz) * s, y, cz + (x - cx) * s + (z - cz) * c)


def _fx(x):
    """Una x del tauler pla → la x de la consola (sense girar)."""
    x0, x1, _, _ = CON
    return x0 + (x - FX[0]) * (x1 - x0) / (FX[1] - FX[0])
DESK_H = 46                                        # l'alçada del pupitre
PAN = ((DESK_H + 4, 230), (DESK_H + 96, 242))     # el panell dels panys: de (y, z) a baix a (y, z) a dalt
HOOD = ((DESK_H + 96, 242), (DESK_H + 118, 250))  # les pantalletes, a sobre
LIFT = (160, 246, 132)                             # l'ascensor (a la paret x = 0): z0, z1 i l'alçada
LIFT_D = 86                                        # la fondària de la cabina
INTER_Z = (264, 286)                               # l'interfon, a la paret de l'esquerra
TUB = (420, 166, 16)                               # el tub de la reserva: x, z, radi
ARM = (470, 516, 254, 280)                         # l'armari de la palanca: x0, x1, z0, z1
ARM_H = 124

CAM = Camera(pos=(440, 190, -170), yaw=-0.40, pitch=0.16, f=380, centre=(330, 72))   # (de biaix: el fons fuig)

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)  # (la llum és la del món: la de l'Escena)
LLUMS = [Llum((300, 230, 230), 330, 1.5, power=1.2),        # la claror que baixa per la piscina
         Llum((140, 220, 160), 240, 0.8, power=1.3),
         Llum((-40, 120, 203), 230, 2.2, power=1.2),        # la cabina de l'ascensor
         Llum((270, 120, 200), 140, 0.7, power=1.6),        # els llums del tauler
         Llum((494, 120, 200), 90, 0.6, power=1.6)]         # la palanca


# ─── Les textures: la sala plana de sempre ───────────────────────────────────

def _pany(cv, key, obert=False):
    """Un pany com el de sempre, però amb el rètol gros (a 1× i en escorç, el petit no es llegia)."""
    PL.pany(cv, key, obert)
    x, lab = PL.LOCKS[key]
    w = text_width(lab) * 2 + 8
    cv.rect(x - w // 2, 100, x + w // 2, 114, ORP, lambda xx, yy: 5.0 - (yy - 100) * 0.14)
    PL.marc_or_simple(cv, x - w // 2, 100, x + w // 2, 114)
    lletres_grans(cv, lab, x - w // 2 + 5, 103, (50, 30, 10))


@functools.lru_cache(maxsize=None)
def _consola():
    """El tauler pla (x 150..470): a dalt les pantalletes (y 64..98), el panell dels panys (98..200) i el pupitre."""
    cv = Canvas(light=PL.LIGHT)
    cv.rect(140, 56, 480, 230, ACER, lambda x, y: 3.4 + (fbm(x / 50, y / 40, 6) - 0.5) * 0.4)
    PL.pantalletes(cv)
    cv.rect(146, 62, 474, 63, ORP, 4.4)
    PL.tauler(cv)
    x0, y0, x1, _ = PL.DESK
    cv.rect(x0 + 2, y0 - 3, x1 - 2, y0 + 9, ACER, 4.0)                 # (el títol, a la tapa: aquí, els rètols)
    cv.hline(x0, x1, y0, ACER, 5.2)
    for key in PL.LOCKS:
        _pany(cv, key)
    return cv.img


@functools.lru_cache(maxsize=None)
def _pla():
    """La resta de peces planes, a les seves coordenades de sempre (transparent on no hi ha res)."""
    cv = Canvas(light=PL.LIGHT, transparent=True)
    PL.interfon(cv)
    PL.palanca(cv)
    PL.camera(cv)
    PL.ascensor(cv)
    return cv.img


# ─── Les superfícies ────────────────────────────────────────────────────────

def _planxa(lvl0, pw=52, ph=54, seed=6):
    """Paret de planxa d'acer: plaques, juntes i cargols, en coordenades del món (s, t des del cantó de dalt)."""
    def L(s, t, P):
        px_, py_ = int(s // pw), int(t // ph)
        v = lvl0 + (hr(px_, py_, seed) - 0.5) * 0.5 + (fbm(s / 40, t / 30, seed) - 0.5) * 0.5
        u, w = s % pw, t % ph
        if u < 1.0 or w < 1.0:
            v -= 1.6
        elif u < 2.0 or w < 2.0:
            v += 0.6
        if (u > pw - 5 and u < pw - 3 or 3 < u < 5) and int(w) % 18 == 9:
            v += 1.4                                               # els cargols
        return v
    return L


def _socol(lvl0, h=10, seed=6):
    """La planxa amb un sòcol fosc a baix i la tira de llum turquesa (t des de dalt; `alt` = l'alçada del quad)."""
    pl = _planxa(lvl0, seed=seed)

    def L(s, t, P):
        y = P[1]
        if y < h:
            return 2.0 - (h - y) * 0.04
        if y < h + 1.4:
            return 6.0
        return pl(s, t, P)
    return L


def _terra(s, t, P):
    """La reixa d'acer del terra: una graella de passadís (quadres foscos) amb plaques llises, vista des de dalt."""
    x, z = P[0], P[2]
    v = 2.8 + (fbm(x / 80, z / 50, 9) - 0.5) * 0.8
    plate_x, plate_z = int(x // 96), int(z // 64)
    if x % 96 < 1.4 or z % 64 < 1.4:
        return v - 1.8                                             # les juntes entre plaques
    if (plate_x + plate_z) % 3 == 0:                               # una placa llisa, gastada
        return v + 0.6 + (hr(int(x) // 3, int(z) // 3, 4) - 0.5) * 0.4
    gx, gz = x % 6, z % 6
    if gx < 1.6 or gz < 1.6:
        return v + 1.0 - (0.4 if gz < 1.6 else 0)                  # la reixa
    return v - 1.6                                                 # els forats (fosc)


def _vidre(x, w):
    """El fons de la piscina vist de sota, a través del vidre (x; w = la distància des de dalt, pel vidre): rajola
    turquesa, les bigues d'acer i la claror de la galeria de dalt. → ('acer' | 'turq', nivell)."""
    beam_x = (x + 6) % 130 < 12
    beam_t = (w + 4) % 46 < 7
    if beam_x or beam_t:
        edge = (x + 6) % 130 < 3 or (w + 4) % 46 < 2
        return 'acer', 3.4 + (1.6 if edge else 0) + (fbm(x / 30, w / 20, 2) - 0.5) * 0.5
    tile = (int(x // 18) + int(w // 12)) % 2
    joint = x % 18 < 1.4 or w % 12 < 1.2
    glow = max(0.0, 1 - abs(x - 300) / 360) * max(0.0, 1 - abs(w - 150) / 200)
    v = 2.6 + glow * 2.6 + tile * 0.3 + (1.1 if joint else 0)
    if 30 < (x - w * 1.6) % 190 < 48:
        v += 0.9                                                   # reflexos del vidre, en diagonal
    return 'turq', v


def escena(cv, tex):
    """Tota la sala, de lluny a prop. → l'Escena (qui ha pintat què)."""
    e = Escena(cv, CAM, LLUMS, ambient=0.0)
    zn = CAM.pos[2] + 40
    (yv0, zv0), (yv1, zv1) = VID
    XR = W + 260
    # la paret de l'esquerra (x = 0), alta (el vidre en tapa la part de dalt), amb el forat de l'ascensor
    lz0, lz1, lh = LIFT
    # primer, la cabina de l'ascensor (es veu pel forat): il·luminada, blanca i or (és l'ascensor del Magnat)
    cab = -LIFT_D

    def marbre(s, t, P):
        v = 4.6 + (fbm(P[2] / 30 + P[0] / 30, P[1] / 22, 5) - 0.5) * 0.9 - (1.4 if P[1] < 10 else 0)
        return v
    e.quad('cabina', (cab, lh, lz0), (cab, lh, lz1), (cab, 0, lz1), (cab, 0, lz0), ramp=MARB, lvl=marbre)
    for zz in (lz0, lz1):
        e.quad('cabina', (cab, lh, zz), (0, lh, zz), (0, 0, zz), (cab, 0, zz), ramp=MARB,
               lvl=lambda s, t, P: marbre(s, t, P) - 1.4, dues_cares=True)
    e.quad('cabina', (cab + 0.5, 46, lz0), (cab + 0.5, 46, lz1), (cab + 0.5, 42, lz1), (cab + 0.5, 42, lz0), ramp=ORP,
           lvl=lambda s, t, P: 5.4 - t * 0.6)
    e.quad('cabina', (cab, lh, lz0), (cab, lh, lz1), (0, lh, lz1), (0, lh, lz0), ramp=MARB,
           lvl=lambda s, t, P: 9.0 if 12 < s < lz1 - lz0 - 12 and 14 < t < LIFT_D - 14 else 4.0, dues_cares=True)
    e.quad('cabina', (cab, 0, lz1), (0, 0, lz1), (0, 0, lz0), (cab, 0, lz0), ramp=MARB,
           lvl=lambda s, t, P: 4.2 - (1.2 if (int(P[0]) // 20 + int(P[2]) // 20) % 2 else 0), dues_cares=True)
    # les dues fulles de la porta, gairebé amagades dins la paret (l'ascensor és obert)
    for a, b in ((lz0, lz0 + 10), (lz1 - 10, lz1)):
        e.quad('cabina', (-1, lh, a), (-1, lh, b), (-1, 0, b), (-1, 0, a), ramp=CROM,
               lvl=lambda s, t, P: 4.0 - (2.4 if s > 8.5 or s < 1.5 else 0), dues_cares=True)
    e.quad('paret_esq', (0, 300, zn), (0, 300, ZW), (0, 0, ZW), (0, 0, zn), ramp=ACER, lvl=_socol(3.0),
           forma=lambda s, t: not (lz0 - zn < s < lz1 - zn and t > 300 - lh))
    # el marc de l'ascensor (sobresurt de la paret) i el rètol de l'indicador
    for a, b in ((lz0 - 8, lz0), (lz1, lz1 + 8)):
        e.caixa('ascensor', 0, 5, 0, lh + 10, a, b, ACER, 4.6)
    e.caixa('ascensor', 0, 5, lh, lh + 18, lz0 - 8, lz1 + 8, ACER, 4.8)
    e.quad('ascensor', (5.2, lh + 16, lz0 + 22), (5.2, lh + 16, lz1 - 22), (5.2, lh + 2, lz1 - 22),
           (5.2, lh + 2, lz0 + 22), tex=(tex['pla'], (44, 84, 82, 97)))
    # les canonades que corren per la paret de l'esquerra, i les abraçadores
    for y, r, lv in ((176, 7, 3.4), (160, 5, 2.8)):
        e.tub('paret_esq', (r + 1, y, zn + 120), (r + 1, y, ZW - r - 1), r, ACER, lv, brides=48)
    # l'interfon, a la paret de l'esquerra (prop de la cantonada)
    iz0, iz1 = INTER_Z
    e.quad('interfon', (0.6, 112, iz0), (0.6, 112, iz1), (0.6, 56, iz1), (0.6, 56, iz0),
           tex=(tex['pla'], (114, 122, 142, 177)))
    # el sostre: el vidre inclinat, el fons de la piscina vist de sota
    for ramp, nom in ((ACER, 'acer'), (TURQ, 'turq')):
        e.quad('vidre', (-20, yv1, zv1), (XR, yv1, zv1), (XR, yv0, zv0), (-20, yv0, zv0), ramp=ramp,
               lvl=lambda s, t, P: _vidre(P[0], t)[1], dues_cares=True,
               forma=lambda s, t, nom=nom: _vidre(s - 20, t)[0] == nom)
    # la paret del fons (z = 300), baixa
    e.quad('paret_fons', (0, HB, ZW), (XR, HB, ZW), (XR, 0, ZW), (0, 0, ZW), ramp=ACER, lvl=_socol(3.2, seed=7))
    e.caixa('biga', -10, XR, HB - 6, HB + 2, ZW - 8, ZW, ACER, 4.4)          # la biga on s'aguanta el vidre
    # el terra
    e.quad('terra', (0, 0, ZW), (XR, 0, ZW), (XR, 0, zn), (0, 0, zn), ramp=ACER, lvl=_terra)
    # el llindar de l'ascensor: franges grogues i negres
    e.quad('terra', (0, 0.2, lz1), (14, 0.2, lz1), (14, 0.2, lz0), (0, 0.2, lz0), ramp=PL.YELLOW,
           lvl=lambda s, t, P: 3.6 if (s + t) % 12 < 6 else -2, dues_cares=True)
    # la foscor dels racons
    e.foscor('racons', (0, 0.5, ZW), (XR, 0.5, ZW), (XR, 0.5, zn), (0, 0.5, zn),
             lambda s, t: max(0.55 * max(0.0, 1 - t / 30), 0.5 * max(0.0, 1 - s / 24)))
    e.foscor('cantonada', (0, HB, ZW - 0.5), (50, HB, ZW - 0.5), (50, 0, ZW - 0.5), (0, 0, ZW - 0.5),
             lambda s, t: 0.5 * max(0.0, 1 - s / 50))
    # la claror de l'ascensor, que surt en diagonal pel terra
    e.claror((0, 0.4, lz1 + 10), (190, 0.4, lz1 - 30), (190, 0.4, lz0 - 110), (0, 0.4, lz0 - 4), (246, 248, 236),
             lambda s, t: 0.62 * max(0.0, 1 - s / 190) ** 1.3
             * max(0.0, math.sin(math.pi * min(1.0, t / max(1.0, 96 + 0.42 * s)))))
    # la claror turquesa que baixa pel vidre: franges en diagonal (les bigues fan ombra)
    e.claror((60, 0.3, 296), (520, 0.3, 296), (520, 0.3, 90), (60, 0.3, 90), (110, 220, 210),
             lambda s, t: 0.16 * max(0.0, 1 - abs(s - 230) / 260) * (0.4 if (s + t * 0.7) % 130 < 22 else 1.0)
             * max(0.0, 1 - t / 210))
    # cables pel terra, de la consola a l'armari i cap a la paret
    for ramp, lv, pts in ((NEGRE, 2.0, [(150, 0.8, 246), (130, 0.8, 226), (90, 0.8, 214), (40, 0.8, 270),
                                         (4, 0.8, 288)]),
                          (VERMELL, 2.4, [(420, 0.8, 246), (440, 0.8, 228), (470, 0.8, 212)]),
                          (NEGRE, 1.8, [(300, 0.8, 248), (318, 0.8, 254), (340, 0.8, 268), (360, 0.8, 296)])):
        e.cable('cables', pts, ramp, lv, gruix=2.2)
    # la consola (girada): l'ombra, el pupitre, el panell inclinat dels panys i les pantalletes
    x0, x1, zc, zb = CON
    R = _rc
    e.foscor('ombra_consola', R(x0 - 30, 0.6, zb + 4), R(x1 + 10, 0.6, zb + 4), R(x1 + 10, 0.6, zc - 30),
             R(x0 - 30, 0.6, zc - 30), lambda s, t: 0.55 * min(1.0, min(s, t, x1 - x0 + 40 - s) / 22))
    con = tex['consola']
    fx0, fx1 = FX
    e.caixa_girada('consola', (x0 + x1) / 2, (zc + zb) / 2, x1 - x0, zb - zc, DESK_H, CON_ANG, ACER, 3.0,
                   cares={'davant': {'ramp': ACER, 'lvl': lambda s, t, P: 2.8 - (1.6 if s % 80 < 1.2 else 0)
                                     + (0.8 if s % 80 < 2.4 else 0) - (1.4 if t > DESK_H - 8 else 0)
                                     + (0.6 if t < 2 else 0)},
                          'esquerra': {'ramp': ACER, 'lvl': lambda s, t, P: 3.4 - (1.2 if t > DESK_H - 8 else 0)},
                          'dreta': {'ramp': ACER, 'lvl': lambda s, t, P: 2.4 - (1.0 if t > DESK_H - 8 else 0)
                                    + (0.8 if 8 < s < 30 and 10 < t < 30 and int(t) % 4 < 2 else 0)},
                          'dalt': {'tex': (con, (fx0, 210, fx1, 222))}})
    (pa_y, pa_z), (pb_y, pb_z) = PAN
    e.quad('consola_costat', R(x0, pb_y, pb_z + 8), R(x0, pb_y, pb_z), R(x0, pa_y, pa_z), R(x0, pa_y, pa_z + 8),
           ramp=ACER, lvl=3.6)
    e.quad('consola_costat', R(x1, pb_y, pb_z), R(x1, pb_y, pb_z + 8), R(x1, pa_y, pa_z + 8), R(x1, pa_y, pa_z),
           ramp=ACER, lvl=2.6)
    e.quad('consola', R(x0, pb_y + 0.1, pb_z + 8), R(x1, pb_y + 0.1, pb_z + 8), R(x1, pb_y + 0.1, pb_z),
           R(x0, pb_y + 0.1, pb_z), ramp=ACER, lvl=4.6)
    e.quad('consola_panell', R(x0, pb_y, pb_z), R(x1, pb_y, pb_z), R(x1, pa_y, pa_z), R(x0, pa_y, pa_z),
           tex=(con, (fx0, 98, fx1, 204)))
    (ha_y, ha_z), (hb_y, hb_z) = HOOD
    e.quad('consola_costat', R(x0, hb_y, hb_z + 6), R(x0, hb_y, hb_z), R(x0, ha_y, ha_z), R(x0, ha_y, ha_z + 6),
           ramp=ACER, lvl=3.8)
    e.quad('consola_costat', R(x1, hb_y, hb_z), R(x1, hb_y, hb_z + 6), R(x1, ha_y, ha_z + 6), R(x1, ha_y, ha_z),
           ramp=ACER, lvl=2.8)
    e.quad('consola', R(x0, hb_y + 0.1, hb_z + 6), R(x1, hb_y + 0.1, hb_z + 6), R(x1, hb_y + 0.1, hb_z),
           R(x0, hb_y + 0.1, hb_z), ramp=ACER, lvl=5.0)
    e.quad('consola_pantalles', R(x0, hb_y, hb_z), R(x1, hb_y, hb_z), R(x1, ha_y, ha_z), R(x0, ha_y, ha_z),
           tex=(con, (fx0, 62, fx1, 98)))
    # l'armari de la palanca, amb la placa de franges al davant
    ax0, ax1, az0, az1 = ARM
    e.foscor('ombra_armari', (ax0 - 24, 0.6, az1), (ax1 + 4, 0.6, az1), (ax1 + 4, 0.6, az0 - 20),
             (ax0 - 24, 0.6, az0 - 20), lambda s, t: 0.5 * min(1.0, min(s, t) / 14))
    e.caixa('armari', ax0, ax1, 0, ARM_H, az0, az1, ACER, 3.2,
            cares={'esquerra': {'ramp': ACER, 'lvl': lambda s, t, P: 3.0 - (1.4 if P[1] < 8 else 0)},
                   'dalt': {'ramp': ACER, 'lvl': 4.6}})
    lx, ly = PL.LEVER
    cx = (ax0 + ax1) / 2
    e.quad('palanca', (cx - 22, 126, az0 - 0.5), (cx + 22, 126, az0 - 0.5), (cx + 22, 10, az0 - 0.5),
           (cx - 22, 10, az0 - 0.5), tex=(tex['pla'], (lx - 22, ly - 70, lx + 22, ly + 46)))
    # el tub de la reserva: puja del terra fins al vidre, blanc amb franges blaves; i la vàlvula fins a l'armari
    tx, tz, tr = TUB
    e.foscor('ombra_tub', (tx - 46, 0.6, tz + 26), (tx + 10, 0.6, tz + 26), (tx + 10, 0.6, tz - 26),
             (tx - 46, 0.6, tz - 26), lambda s, t: 0.6 * max(0.0, 1 - ((s - 34) / 30) ** 2 - ((t - 26) / 24) ** 2) * 1.6)
    e.tub('cables', (ax0, 60, (az0 + az1) / 2), (tx + tr - 3, 60, tz + 6), 4, CROM, 3.6)
    _tub_vertical(e, 'tub', tx, tz, tr)
    # la càmera de seguretat, penjada del tub i mirant la consola
    e.sprite('camera', tex['camera'], (24, 12), (tx - tr - 1, 172, tz - 4))
    # primer pla: la barana (a l'esquerra) i la canonada gruixuda (a baix), fosques
    for x in (-10, 62, 134):
        e.caixa('primer_pla', x - 2.5, x + 2.5, 0, 74, 6 - x * 0.12, 11 - x * 0.12, ACER, 2.0)
    e.tub('primer_pla', (-60, 74, 14), (230, 74, -20), 3.4, ACER, 2.4)
    e.tub('primer_pla', (-60, 40, 14), (230, 40, -20), 2.2, ACER, 1.8)
    e.tub('primer_pla', (250, 26, 34), (700, 26, 120), 13, ACER, 1.6, brides=60)
    return e


def _cilindre(e, sid, tx, tz, r, y0, y1, ramp, lvl, n=24):
    """Un cilindre vertical de facetes, amb la llum de l'esquerra i de davant."""
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        p0 = (tx + r * math.cos(a0), tz + r * math.sin(a0))
        p1 = (tx + r * math.cos(a1), tz + r * math.sin(a1))
        shade = 2.2 * math.cos((a0 + a1) / 2 - 3.6)
        e.quad(sid, (p0[0], y1, p0[1]), (p1[0], y1, p1[1]), (p1[0], y0, p1[1]), (p0[0], y0, p0[1]), ramp=ramp,
               lvl=lambda s, t, P, shade=shade: lvl + shade)


def _tub_vertical(e, sid, tx, tz, r):
    """El tub de la reserva: blanc, amb franges blaves i brides de crom, del terra fins al vidre."""
    _cilindre(e, sid, tx, tz, r, 0, 320, BLANC, 2.8)
    for b in (60, 150):
        _cilindre(e, sid, tx, tz, r + 0.3, b, b + 5, BLAU, 2.8)
    for b in (4, 110, 204):
        _cilindre(e, sid, tx, tz, r + 2, b, b + 5, CROM, 4.0)
    # la gota i el rètol, de cara
    e.sprite(sid, _rotul_tub(), (14, 30), (tx, 92, tz - r - 0.5))


@functools.lru_cache(maxsize=None)
def _rotul_tub():
    cv = Canvas(28, 34, transparent=True)
    gota(cv, 14, 8, 14, lit=0)
    lletres_c(cv, 'RESERVA', 14, 18, (30, 50, 110))
    lletres_c(cv, 'PRIVADA', 14, 25, (30, 50, 110))
    return cv.img


# ─── Composició ────────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _textures():
    pla = _pla()
    lx, ly = PL.CAM
    return {'consola': _consola(), 'pla': pla, 'camera': pla.crop((lx - 18, ly - 14, lx + 26, ly + 8))}


@functools.lru_cache(maxsize=None)
def _base():
    cv = Canvas(light=LIGHT)
    e = escena(cv, _textures())
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)    # la barra de verbs: negre
    return cv.img, e


def bg(cv):
    img, _ = _base()
    cv.img.paste(img)
    cv.P = cv.img.load()


def _flat(fn, base=None):
    cv = Canvas(light=PL.LIGHT, transparent=base is None, img=base.copy() if base is not None else None)
    fn(cv)
    return cv.img


def _obert(key):
    def fn(cv):
        _, e = _base()
        con = _consola()
        cv.img.alpha_composite(e.capa(_diff(_flat(lambda c: _pany(c, key, True), con), con), {'consola_panell'}))
    return fn


def reserva_oberta(cv):
    _, e = _base()
    pla = _pla()
    cv.img.alpha_composite(e.capa(_diff(_flat(lambda c: PL.palanca(c, oberta=True), pla), pla), {'palanca'}))


def flors_camera(cv):
    """Les flors de plàstic d'en Nil davant la càmera: el mateix sprite, amb les flors."""
    _, e = _base()
    lx, ly = PL.CAM
    fl = _flat(lambda c: (PL.camera(c), PL.flors_camera(c)))
    im = fl.crop((lx - 30, ly - 14, lx + 26, ly + 22))
    tmp = Canvas(light=LIGHT, transparent=True)
    tx, tz, tr = TUB
    Escena(tmp, CAM).sprite('flors', im, (36, 12), (tx - tr - 1, 172, tz - 4))
    cv.img.alpha_composite(_diff(tmp.img, Image.new('RGBA', tmp.img.size, (0, 0, 0, 0))))


PROPS = {'obert_t2': _obert('t2'), 'obert_aqua': _obert('aqua'), 'obert_ferrum': _obert('ferrum'),
         'reserva_oberta': reserva_oberta, 'flors_camera': flors_camera}

# ─── Animació: el llum de la càmera ──────────────────────────────────────────

LLUM_N = 12                                        # 12 × 110 ms: encès mig segon, apagat mig segon


def _frames_llum():
    """El llum vermell de la càmera fa pampallugues (grava): encès, amb claror al voltant, i apagat, amb el gris de la
    carcassa. Les flors (`flors_camera`), quan hi són, el tapen."""
    img, _ = _base()
    P = img.load()
    lx, ly = max(((x, y) for x in range(425, 460) for y in range(20, 45)),
                 key=lambda q: P[q][0] - P[q][1])     # el píxel més vermell, a la càmera
    vermells = [(lx + dx, ly + dy) for dx in range(-4, 5) for dy in range(-4, 5)
                if P[lx + dx, ly + dy][0] - P[lx + dx, ly + dy][1] > 12]

    def gris(x, y):                                    # la carcassa de la mateixa fila, fora del llum
        for d in (5, -5, 6, -6, 7):
            c = P[x + d, y]
            if c[0] - c[1] <= 12:
                return c
        return (150, 156, 168, 255)
    out = []
    for f in range(LLUM_N):
        im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        Q = im.load()
        if f < LLUM_N // 2:                            # encès: la creu més viva i una claror
            for dx in range(-4, 5):
                for dy in range(-4, 5):
                    d = math.hypot(dx, dy)
                    if d <= 1.0:
                        Q[lx + dx, ly + dy] = (255, 150, 120, 255) if d == 0 else (255, 72, 52, 255)
                    elif d <= 4.2:
                        Q[lx + dx, ly + dy] = (255, 60, 40, round(150 * (1 - (d - 1) / 3.2) ** 1.3))
        else:                                          # apagat
            for x, y in vermells:
                Q[x, y] = (*gris(x, y)[:3], 255)
            Q[lx, ly] = (120, 60, 64, 255)             # (el vidre del llum, fosc)
        out.append(im)
    return out


ANIMS = {'camera_llum': {'frames': _frames_llum, 'frameDuration': 110}}


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
    """L'escala d'un personatge amb els peus a la y de pantalla `v` (al terra, la profunditat només depèn de v)."""
    lo, hi = 1.0, 2000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.projecta((260, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((260, 0, (lo + hi) / 2))


def _cercle(cx, cz, r, n=10):
    return [_p(cx + r * math.cos(2 * math.pi * i / n), cz + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


TX, TZ, TR = TUB
V_DAVANT = 244                                     # la vora de davant del terra on es camina (escala ≈1,2)


def _zf(x, v=V_DAVANT):
    """El z del terra que cau a la y de pantalla `v` a l'x del món `x` (la càmera girada inclina les files)."""
    lo, hi = -100.0, 2000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.projecta((x, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return round((lo + hi) / 2)


# El terra on es camina (al món): davant la consola, pel racó de l'esquerra fins a l'ascensor i l'interfon, i a la
# dreta al voltant del tub fins a l'armari de la palanca (s'hi passa per darrere del tub).
WALK_MON = [(14, _zf(14)), (14, 254), (48, 264), _rc(CON[0] - 6, 0, CON[2] - 9)[::2],
            _rc(CON[1] + 8, 0, CON[2] - 9)[::2], _rc(CON[1] + 8, 0, CON[3])[::2], (640, 246), (640, _zf(640)),
            (300, _zf(300))]
_WALK = [_p(x, z) for x, z in WALK_MON]
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)


def _vpeu(z):
    return CAM.projecta((300, 0, z))[1]


FRONT = [
    {'id': 'davant_tub', 'mask': _amo({'tub', 'camera'}), 'baseline': round(_vpeu(TZ - TR)), 'zIndex': 20,
     'props': ('camera_llum', 'flors_camera')},    # (el llum i les flors són a la càmera: per sobre de la capa;
                                                   # amb el mateix zIndex va per nom, i les flors tapen el llum)
    {'id': 'davant_armari', 'mask': _amo({'armari', 'palanca'}), 'baseline': round(_vpeu(ARM[2])), 'zIndex': 20},
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20},
]


def _pany_rect(key):
    wx = _fx(PL.LOCKS[key][0])
    (pa_y, pa_z), (pb_y, pb_z) = PAN
    return _rect_mon(_rc(wx - 38, pb_y - 4, pb_z), _rc(wx + 38, pb_y - 4, pb_z), _rc(wx - 38, DESK_H, CON[2]),
                     _rc(wx + 38, DESK_H, CON[2]))


def _pany_walk(key):
    x, _, z = _rc(_fx(PL.LOCKS[key][0]), 0, CON[2] - 28)
    return _p(x, z)


_LX = (ARM[0] + ARM[1]) / 2

GEOMETRIA = {
    'things': {
        'ascensor': {'rect': _rect_mon((0, LIFT[2] + 18, LIFT[0] - 8), (0, 0, LIFT[1] + 8)),
                     'walk': _p(30, (LIFT[0] + LIFT[1]) / 2)},
        'interfon': {'rect': _rect_mon((0, 116, INTER_Z[0] - 2), (0, 52, INTER_Z[1] + 2)),
                     'walk': _p(34, 256)},
        'pany_t2': {'rect': _pany_rect('t2'), 'walk': _pany_walk('t2')},
        'pany_aqua': {'rect': _pany_rect('aqua'), 'walk': _pany_walk('aqua')},
        'pany_ferrum': {'rect': _pany_rect('ferrum'), 'walk': _pany_walk('ferrum')},
        'palanca': {'rect': _rect_mon((_LX - 24, 132, ARM[2]), (_LX + 24, 6, ARM[2])),
                    'walk': _p(_LX + 48, ARM[2] - 32)},   # al costat: davant la tapava (tasca 304)
        'camera': {'rect': _rect_mon((TX - TR - 50, 188, TZ - 4), (TX - TR + 6, 158, TZ - 4)),
                   'walk': _p(TX - 60, TZ - 30)},
    },
    'spawns': {'vet': _p(250, 140)},
    'walkable': _WALK,
    'forats': [_cercle(TX, TZ, TR + 8)],
    'floorSquash': 0.45,
    'characterShadow': {'enabled': True, 'color': '#06121a', 'alpha': 0.4, 'squash': 0.45, 'core': 0.6,
                        'light': {'x': _p(300, 230)[0], 'y': _p(300, 230)[1], 'stretch': 0.6, 'reach': 140}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    # La llum de la sala sobre els personatges (characterLights del motor): la sala de control, blava i en penombra:
    # la claror de la piscina, l'ascensor i el tauler.
    'characterLights': {
        'ambient': '#8a94a2',
        'lights': [
            llum_personatges(CAM, LLUMS[0].pos, LLUMS[0].r, '#c8f4f0', 0.35),  # la piscina
            llum_personatges(CAM, LLUMS[1].pos, LLUMS[1].r, '#c8f4f0', 0.2),  # la piscina
            llum_personatges(CAM, LLUMS[2].pos, LLUMS[2].r, '#f0f4ff', 0.45),  # la cabina de l'ascensor
            llum_personatges(CAM, LLUMS[3].pos, LLUMS[3].r, '#a8e0ff', 0.25),  # el tauler
            llum_personatges(CAM, LLUMS[4].pos, LLUMS[4].r, '#ff8070', 0.2),  # la palanca
        ],
    },
}
