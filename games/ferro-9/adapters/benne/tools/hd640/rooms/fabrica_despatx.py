"""
Despatx del director (Acte 2, Iri). EN 3D (hd640/tres_d.py), a 1×.

Una càmera alta que mira de biaix la cantonada del fons a l'esquerra:
  - a la paret de l'esquerra, en escorç, la **porta del magatzem** (amb el vidre glaçat), la canonada de coure amb el
    manòmetre i la **finestra** amb les cortines de vellut i el radiador: la nit de la ciutat-fàbrica, i la lluna que
    entra en diagonal i pinta al terra la taca freda amb l'ombra dels travessers;
  - a la paret del fons, el **retrat** del director Aldaia amb el llum de llautó i el plànol emmarcat;
  - l'**escriptori** amb volum (el tauler de pell verda amb l'**expedient** del Sic, el tinter, la làmpada de
    banquer; el **calaix** del pany M-3 al davant), separat de la paret i una mica girat;
  - el **faristol** amb el **llibre d'inventari**, dret al mig (s'hi passa per darrere), i la prestatgeria de llibres
    a la dreta, amb volum;
  - la catifa, girada; primer pla: una butaca de cuir en silueta a baix a la dreta i un penja-robes a l'esquerra.

Tot el detall ve del dibuix pla de sempre (fabrica_despatx_pla_comu.py), projectat.

El món: x a la dreta (0 = la paret de la finestra), y amunt (0 = el terra), z cap al fons (300 = la paret del fons);
1 unitat = 1 píxel de sala a la distància on un personatge fa ≈110 px (escala 1).
"""
import functools
import math
import random

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from PIL import Image

from hd.pix import Canvas, Light, W, H, hr, mix, WALNUT, GREEN, FLOOR, GOLD, RED, NAVY, PAPER, IRON, LAMPG
from hd640.rooms import fabrica_despatx_pla_comu as PL
from hd640.rooms.fabrica_calderes_pla_comu import frame_diff
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
ZW = 300                                           # la paret del fons
HW = PL.FLOOR_Y                                    # l'alçada de les parets (el dibuix pla fa 205 fins al terra)
XL = 240                                           # al dibuix pla, la cantonada: a l'esquerra, la paret de la finestra
XR = 760                                           # on s'acaba la paret del fons (fora de la pantalla)
DESK = (190, 238, 136, 34, 46, -0.1)               # l'escriptori: x, z del centre, ample, fons, alt, gir
SHELF = (352, 400, 268, 298)                       # la prestatgeria: x0, x1, z0, z1
LECT = (330, 170)                                  # el faristol (x, z)
RUG = (190, 140, 250, 116, -0.12)                  # la catifa: x, z del centre, ample, fons, gir


def _w(fx):
    """Una x del dibuix pla de la paret del fons → la x del món."""
    return fx - XL


def _wz(fx):
    """Una x del dibuix pla de la paret de la finestra → la z del món."""
    return ZW - XL + fx


def _y(fy):
    """Una y del dibuix pla (el terra, a 205) → l'alçada del món."""
    return HW - fy


WIN = (_wz(PL.GX0), _wz(PL.GX1), _y(PL.GY1), _y(PL.GY0))     # el vidre: z0, z1, y0, y1
MOON_D = (1.0, -0.62, -0.42)                                 # cap on va la llum de la lluna (per unitat de x)

CAM = Camera(pos=(400, 190, -260), yaw=-0.34, pitch=0.2, f=440, centre=(320, 88))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)  # (la llum és la del món: la de l'Escena)


def _desk_pt(lx, y, lz):
    cx, cz, w, d, h, a = DESK
    c, s = math.cos(a), math.sin(a)
    return (cx + lx * c - lz * s, y, cz + lx * s + lz * c)


def _desk_fx(fx):
    """Una x del dibuix pla de l'escriptori (355..491) → la x local del moble."""
    return (fx - 423) * DESK[2] / 136


LAMP_P = _desk_pt(_desk_fx(465), DESK[4] + 22, 6)
PORT_P = (_w(309), _y(30), ZW - 8)                          # el llum de llautó del retrat
LLUMS = [Llum(LAMP_P, 210, 2.2, power=1.5),                 # la làmpada de banquer
         Llum(PORT_P, 90, 1.4, power=1.6),                  # el llum del retrat
         Llum((40, 120, (WIN[0] + WIN[1]) / 2), 200, 0.8)]  # la lluna, per la finestra


# ─── Les textures: el dibuix pla de sempre ───────────────────────────────────

def _tex_light():
    lt = Light(ambient=0.2, vignette=None, floor_fade=None)
    lt.point(465, 139, r=213, k=2.2, squash=1.15, down=True)
    lt.add(lambda x, y: max(0.0, 1 - math.hypot(x - 309, (y - 45) * 0.75) / 64) ** 1.5 * 1.5 if y >= 40 else 0.0)
    return lt


@functools.lru_cache(maxsize=None)
def _paret(t=0.0):
    """Les dues parets planes, de cara: el paper pintat, la porta, la canonada, la finestra (al moment t), el radiador,
    el retrat i el plànol."""
    cv = Canvas(light=_tex_light())
    PL.walls(cv)
    PL.door(cv)
    PL.pipe(cv)
    PL.window_frame(cv)
    PL.window(cv, t)
    PL.radiator(cv)
    PL.portrait(cv)
    PL.blueprint(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _mobles(obert=False):
    """L'escriptori, el faristol i la prestatgeria, plans sobre transparent (en surten els retalls). `obert`: amb el
    calaix del pany estirat."""
    cv = Canvas(light=_tex_light(), transparent=True)
    PL.desk(cv, obert)
    PL.lectern(cv)
    PL.shelves(cv)
    img = cv.img
    for y in range(PL.FLOOR_Y, H):                                   # (l'ombra de l'escriptori al terra: la fa el món)
        for x in range(W):
            img.putpixel((x, y), (0, 0, 0, 0))
    return img


DESK_FRONT = (355, 161, 492, 205)                  # el davant de l'escriptori, amb els calaixos i el pany
DESK_TOP = (355, 140, 446, 161)                    # el damunt: l'expedient, el tinter i la ploma
LAMP_BOX = (446, 126, 486, 161)
LECT_BOX = (515, 140, 590, 228)
SHELF_BOX = (592, 29, 640, HW)


# ─── Les superfícies ────────────────────────────────────────────────────────

def _paper(s, t, P):
    """El paper pintat verd i l'arrimador, en coordenades del món: on el dibuix pla no arriba."""
    fy = t
    if fy < 20:
        return 0.6 if fy < 13 else 2.6
    if fy < 142:
        u, v = int(s) % 27, int(fy - 21) % 35
        a, b = abs(u - 13) / 13, abs(v - 17) / 17
        ring = a * 1.3 + b
        return 2.0 + (0.9 if 0.64 < ring < 0.77 else 0) - max(0, 1 - (fy - 21) / 13) * 1.2
    if fy < 148:
        return 4.0 - (fy - 142) * 0.5
    if fy < 194:
        px = int(s) % 59
        if 8 <= px <= 51 and 155 <= fy <= 188:
            return 2.7 if not (px == 8 or fy < 156) else 0.9
        return 2.3
    return 1.6


def _taulons(s, t, P):
    """El terra de taulons encerats, en coordenades del món: fugen cap al fons, juntes de testa."""
    x, z = P[0], P[2]
    pl = math.floor(x / 22)
    r = hr(pl, 3)
    seg = math.floor((z + r * 200) / 90)
    v = 2.4 + (hr(pl, seg) - 0.5) * 0.8 + 0.12 * math.sin(x * 0.4 + z * 0.05 + r * 20)
    if x % 22 < 1.0:
        return 0.7
    if (z + r * 200) % 90 < 1.0:
        return 0.9
    if x % 22 < 2.0:
        v += 0.35
    return v


def _lluna(x, z, y=0.0):
    """Quanta llum de la lluna (0..1) arriba a un punt del món: la línia cap a la finestra, amb l'ombra dels
    travessers i del muntant."""
    if x <= 0:
        return 0.0
    yw, zw = y - MOON_D[1] * x, z - MOON_D[2] * x
    z0, z1, y0, y1 = WIN
    if not (z0 + 2 < zw < z1 - 2 and y0 + 2 < yw < y1 - 2):
        return 0.0
    fy = HW - yw
    if abs(fy - 65.5) < 1.6 or abs(fy - 99.5) < 1.6 or abs(zw - _wz(163.5)) < 1.6:
        return 0.0
    if zw < _wz(117) or zw > _wz(211):
        return 0.0                                     # les cortines
    e = min(zw - z0, z1 - zw, yw - y0, y1 - yw) / 8
    return min(1.0, e) * max(0.0, 1 - x / 420) * 0.5


def _catifa(s, t, P):
    """La catifa: vora vermella, sanefa de rombes, el medalló blau del mig."""
    w, d = RUG[2], RUG[3]
    bd = min(s, w - s, t * 2.2, (d - t) * 2.2)
    if bd < 2:
        return ('R', 1.2)
    if bd < 5:
        return ('G', 2.4)
    if bd < 14:
        k = (int(s / 3) + int(t / 3)) % 4
        return ('N', 2.2) if k < 2 else ('R', 2.6)
    if bd < 17:
        return ('G', 2.0)
    md = abs(s / w - 0.5) * 2.6 + abs(t / d - 0.5) * 2.0
    if md < 0.35:
        return ('N', 2.6)
    if md < 0.45:
        return ('G', 2.8)
    if md < 0.6:
        return ('R', 3.4)
    return ('R', 3.0 if (int(s / 4) + int(t / 3)) % 5 == 0 else 2.5)


def _rug_pt(lx, y, lz):
    cx, cz, w, d, a = RUG
    c, s = math.cos(a), math.sin(a)
    return (cx + lx * c - lz * s, y, cz + lx * s + lz * c)


def escena(cv, tex=None, obert=False):
    """Tota la sala, de lluny a prop. → l'Escena (qui ha pintat què). `obert`: el calaix del pany, estirat."""
    e = Escena(cv, CAM, LLUMS, ambient=-0.45)
    zn = CAM.pos[2] + 60
    paret, mob = tex or _paret(), _mobles(obert)
    # el sostre, fosc
    e.quad('sostre', (0, HW, zn), (XR, HW, zn), (XR, HW, ZW), (0, HW, ZW), ramp=WALNUT, lvl=0.6, dues_cares=True)
    # la paret de la finestra (x = 0): de prop, paper pintat; cap a la cantonada, el dibuix pla (x 0..240)
    e.quad('paret_esq_prop', (0, HW, zn), (0, HW, ZW - XL), (0, 0, ZW - XL), (0, 0, zn), ramp=GREEN,
           lvl=lambda s, t, P: _paper(s, t, P) if 20 <= t < 142 else 0)
    e.quad('paret_esq', (0, HW, ZW - XL), (0, HW, ZW), (0, 0, ZW), (0, 0, ZW - XL), tex=(paret, (0, 0, XL, HW)))
    # la paret del fons (z = 300): el dibuix pla (x 240..640) i, a la dreta, més paper pintat
    e.quad('paret_fons', (0, HW, ZW), (W - XL, HW, ZW), (W - XL, 0, ZW), (0, 0, ZW), tex=(paret, (XL, 0, W, HW)))
    e.quad('paret_fons_dreta', (W - XL, HW, ZW), (XR, HW, ZW), (XR, 0, ZW), (W - XL, 0, ZW), ramp=GREEN,
           lvl=lambda s, t, P: _paper(s, t, P))
    # (l'arrimador de la dreta, de fusta: per sobre del paper)
    e.quad('paret_fons_dreta', (W - XL, HW - 142, ZW - 0.3), (XR, HW - 142, ZW - 0.3), (XR, 0, ZW - 0.3),
           (W - XL, 0, ZW - 0.3), ramp=WALNUT, lvl=lambda s, t, P: _paper(s, t + 142, P))
    e.quad('paret_esq_prop', (0.3, HW - 142, zn), (0.3, HW - 142, ZW - XL), (0.3, 0, ZW - XL), (0.3, 0, zn), ramp=WALNUT,
           lvl=lambda s, t, P: _paper(s, t + 142, P))
    e.quad('paret_esq_prop', (0.3, HW - 2, zn), (0.3, HW - 2, ZW - XL), (0.3, HW - 20, ZW - XL), (0.3, HW - 20, zn),
           ramp=WALNUT, lvl=lambda s, t, P: _paper(s, t + 2, P))
    # el terra
    e.quad('terra', (0, 0, ZW), (XR, 0, ZW), (XR, 0, zn), (0, 0, zn), ramp=FLOOR, lvl=_taulons)
    # la catifa, una mica girada
    RAMPS = {'R': RED, 'G': GOLD, 'N': NAVY}
    cw, cd = RUG[2], RUG[3]
    for key, rp in RAMPS.items():
        e.quad('catifa', _rug_pt(-cw / 2, 0.3, cd / 2), _rug_pt(cw / 2, 0.3, cd / 2), _rug_pt(cw / 2, 0.3, -cd / 2),
               _rug_pt(-cw / 2, 0.3, -cd / 2), ramp=rp,
               lvl=lambda s, t, P, k=key: _catifa(s, t, P)[1] - ((fbm_pel(s, t) - 0.5) * 0.4),
               forma=lambda s, t, k=key: _catifa(s, t, None)[0] == k)
    # el serrell, a davant i a darrere
    for lz in (-cd / 2, cd / 2):
        e.quad('catifa', _rug_pt(-cw / 2, 0.35, lz + 2), _rug_pt(cw / 2, 0.35, lz + 2), _rug_pt(cw / 2, 0.35, lz - 2),
               _rug_pt(-cw / 2, 0.35, lz - 2), ramp=PAPER, lvl=lambda s, t, P: 2.0 if int(s) % 2 == 0 else -9,
               forma=lambda s, t: int(s) % 2 == 0)
    # la taca de la lluna (amb l'ombra dels travessers) i la llum de la làmpada al terra
    e.claror((0, 0.5, ZW), (420, 0.5, ZW), (420, 0.5, 0), (0, 0.5, 0), (170, 186, 236),
             lambda s, t: 0.8 * _lluna(s, ZW - t))
    lx, ly, lz_ = LAMP_P
    e.claror((lx - 180, 0.6, lz_ + 40), (lx + 180, 0.6, lz_ + 40), (lx + 180, 0.6, lz_ - 200), (lx - 180, 0.6, lz_ - 200),
             (255, 220, 150), lambda s, t: 0.2 * max(0.0, 1 - math.hypot(s - 180, (t - 60) * 0.8) / 180))
    # la foscor dels racons
    e.foscor('racons', (0, 0.5, ZW), (XR, 0.5, ZW), (XR, 0.5, zn), (0, 0.5, zn),
             lambda s, t: max(0.6 * max(0.0, 1 - t / 24), 0.5 * max(0.0, 1 - s / 22)))
    e.foscor('cantonada', (0, HW, ZW - 0.5), (60, HW, ZW - 0.5), (60, 0, ZW - 0.5), (0, 0, ZW - 0.5),
             lambda s, t: 0.5 * max(0.0, 1 - s / 60))
    e.foscor('cantonada2', (0.5, HW, ZW - 60), (0.5, HW, ZW), (0.5, 0, ZW), (0.5, 0, ZW - 60),
             lambda s, t: 0.5 * max(0.0, 1 - (60 - s) / 60))
    e.foscor('dreta_fosc', (W - XL - 40, HW, ZW - 0.6), (XR, HW, ZW - 0.6), (XR, 0, ZW - 0.6), (W - XL - 40, 0, ZW - 0.6),
             lambda s, t: 0.6 * min(1.0, s / 200))
    # el radiador, amb volum, sota la finestra
    rz0, rz1 = _wz(123), _wz(209)
    e.caixa('radiador', 0, 8, 6, _y(163), rz0, rz1, IRON, 2.2,
            cares={'dreta': {'tex': (paret, (123, 163, 209, 199))},
                   'dalt': {'ramp': IRON, 'lvl': lambda s, t, P: 3.0 if int(t) % 8 < 6 else 0.8}})
    # ─ l'escriptori: el cos amb els calaixos (el dibuix pla), el tauler de pell, la làmpada ─
    cx, cz, w, d, h, a = DESK
    e.foscor('ombra_taula', _desk_pt(-w / 2 - 8, 0.6, d / 2 + 6), _desk_pt(w / 2 + 14, 0.6, d / 2 + 6),
             _desk_pt(w / 2 + 14, 0.6, -d / 2 - 14), _desk_pt(-w / 2 - 8, 0.6, -d / 2 - 14),
             lambda s, t: 0.55 * max(0.0, 1 - ((s - (w + 22) / 2) / ((w + 22) / 2)) ** 6 - ((t - (d + 20) / 2) / ((d + 20) / 2)) ** 6))
    e.caixa_girada('taula', cx, cz, w, d, h, a, WALNUT, 2.0,
                   cares={'davant': {'tex': (mob, DESK_FRONT)},
                          'esquerra': {'ramp': WALNUT, 'lvl': lambda s, t, P: 2.4 + (0.8 if t < 6 else 0) - (1.0 if t > h - 5 else 0)},
                          'dreta': {'ramp': WALNUT, 'lvl': lambda s, t, P: 1.6 + (0.8 if t < 6 else 0)},
                          'dalt': {'ramp': LAMPG, 'lvl': lambda s, t, P: 3.6 if (s < 5 or s > w - 5 or t < 4 or t > d - 4)
                                   else (2.6 if (s < 6 or s > w - 6 or t < 5 or t > d - 5) else 1.5 + (hr(int(s) // 2, int(t), 5) - 0.5) * 0.3)}})
    if obert:
        _calaix_obert(e)
    # (la vora del tauler, de noguera, i el filet daurat de la pell)
    for (s0, s1, t0, t1, rp, lv) in ((0, w, 0, 4, WALNUT, 3.6), (0, w, d - 4, d, WALNUT, 3.0), (0, 5, 0, d, WALNUT, 3.4),
                                     (w - 5, w, 0, d, WALNUT, 3.2)):
        e.quad('taula', _desk_pt(-w / 2 + s0, h + 0.2, d / 2 - t0), _desk_pt(-w / 2 + s1, h + 0.2, d / 2 - t0),
               _desk_pt(-w / 2 + s1, h + 0.2, d / 2 - t1), _desk_pt(-w / 2 + s0, h + 0.2, d / 2 - t1), ramp=rp, lvl=lv)
    # el damunt (l'expedient, el tinter, la ploma): el dibuix pla, ajagut sobre la pell
    x0_, x1_ = _desk_fx(DESK_TOP[0]), _desk_fx(DESK_TOP[2])
    e.quad('expedient', _desk_pt(x0_, h + 0.5, d / 2 - 2), _desk_pt(x1_, h + 0.5, d / 2 - 2), _desk_pt(x1_, h + 0.5, -d / 2 + 1),
           _desk_pt(x0_, h + 0.5, -d / 2 + 1), tex=(mob, DESK_TOP))
    e.sprite('lampada', mob.crop(LAMP_BOX), (465 - LAMP_BOX[0], 160 - LAMP_BOX[1]), _desk_pt(_desk_fx(465), h, 6))
    # ─ la prestatgeria, amb volum ─
    sx0, sx1, sz0, sz1 = SHELF
    e.foscor('ombra_prestatgeria', (sx0 - 10, 0.6, sz1), (sx1 + 6, 0.6, sz1), (sx1 + 6, 0.6, sz0 - 16), (sx0 - 10, 0.6, sz0 - 16),
             lambda s, t: 0.55 * min(1.0, max(0.0, (sz1 - sz0 + 16 - t) / 16)))
    e.caixa('prestatgeria', sx0, sx1, 0, HW - SHELF_BOX[1], sz0, sz1, WALNUT, 1.6,
            cares={'davant': {'tex': (mob, SHELF_BOX)}, 'dalt': {'ramp': WALNUT, 'lvl': 3.4},
                   'esquerra': {'ramp': WALNUT, 'lvl': lambda s, t, P: 2.4 + (0.6 if t < 6 else 0) + (hr(int(t) // 4, 3) - 0.5) * 0.3}})
    # ─ el faristol amb el llibre (el dibuix pla, dret), amb la seva ombra ─
    fx_, fz_ = LECT
    e.foscor('ombra_faristol', (fx_ - 24, 0.7, fz_ + 14), (fx_ + 24, 0.7, fz_ + 14), (fx_ + 24, 0.7, fz_ - 14),
             (fx_ - 24, 0.7, fz_ - 14), lambda s, t: 0.6 * max(0.0, 1 - ((s - 24) / 24) ** 2 - ((t - 14) / 14) ** 2) * 1.6)
    e.sprite('faristol', mob.crop(LECT_BOX), (552 - LECT_BOX[0], 225 - LECT_BOX[1]), (fx_, 0, fz_))
    # ─ primer pla: la butaca de cuir (a baix a la dreta) i el penja-robes (a l'esquerra), en silueta ─
    FOSC = [(4, 2, 4), (10, 5, 8), (18, 9, 12), (28, 14, 16), (40, 20, 20), (54, 28, 24)]
    bx, bz, ba = 492, 10, 0.5
    for (lx, lz, ww, dd, hh, y0, lvl) in ((0, 0, 70, 60, 24, 6, 2.2),          # el seient
                                           (0, 26, 70, 14, 64, 6, 1.8),        # el respatller
                                           (-36, 0, 10, 60, 40, 6, 2.6),       # els braços
                                           (36, 0, 10, 60, 40, 6, 1.6)):
        c_, s_ = math.cos(ba), math.sin(ba)
        e.caixa_girada('primer_pla', bx + lx * c_ - lz * s_, bz + lx * s_ + lz * c_, ww, dd, hh, ba, FOSC, lvl, y0=y0,
                       cares={'dalt': {'ramp': FOSC, 'lvl': lvl + 1.0}})
    kx, kz = 46, -34                                                           # el penja-robes
    e.tub('primer_pla', (kx, 0, kz), (kx, 170, kz), 3, FOSC, 2.4)
    e.tub('primer_pla', (kx, 4, kz), (kx, 8, kz), 12, FOSC, 1.8)
    for dx, dz in ((-12, 0), (12, 0), (0, 10)):
        e.cable('primer_pla', [(kx, 162, kz), (kx + dx, 172, kz + dz)], FOSC, 2.6, gruix=2.0)
    e.roca('primer_pla', (kx + 4, 104, kz - 2), 15, FOSC, lvl=2.4, llum_dir=(0.6, -0.4), aplana=2.6, seed=7)   # l'abric
    return e


def _calaix_obert(e):
    """El calaix del pany M-3, estirat: surt del forat (380..457 × 175..196 al dibuix pla), buit, amb el pany al
    davant. És un calaix baix (una safata): des de la càmera, alta, se'n veu el fons, de fusta clara."""
    cx, cz, w, d, h, a = DESK
    x0, x1 = _desk_fx(382), _desk_fx(455)
    yb = h - (195 - 161) * h / 44                      # (el davant de l'escriptori: 161..205 al dibuix pla)
    hc = 9                                             # l'alçada del calaix
    fons, surt = 30, 26                                # el calaix fa 30 de fons; en surten 26
    lz0 = -d / 2 - surt
    cw = x1 - x0

    def box(lx, lz, ww, dd, hh, lvl, y0, cares=None):
        X, _, Z = _desk_pt(lx, 0, lz)
        e.caixa_girada('calaix', X, Z, ww, dd, hh, a, WALNUT, lvl, y0=y0, cares=cares)

    # el fons, de fusta clara (buit: els plànols ja són a l'inventari)
    box((x0 + x1) / 2, lz0 + fons / 2, cw, fons, 1, 3.0, yb,
        cares={'dalt': {'ramp': WALNUT, 'lvl': lambda s, t, P: 3.6 + (hr(int(s) // 3, int(t) // 2, 9) - 0.5) * 0.4
                        - max(0.0, t - fons + 10) * 0.15}})
    # els costats i el darrere (prims, amb el cantell clar)
    for lx in (x0 + 1, x1 - 1):
        box(lx, lz0 + fons / 2, 2, fons, hc, 2.4, yb, cares={'dalt': {'ramp': WALNUT, 'lvl': 4.4}})
    box((x0 + x1) / 2, lz0 + fons - 1, cw, 2, hc, 1.6, yb, cares={'dalt': {'ramp': WALNUT, 'lvl': 4.0}})
    # el davant, amb el pany
    box((x0 + x1) / 2, lz0 + 1.5, cw + 2, 3, hc + 3, 2.9, yb - 1,
        cares={'dalt': {'ramp': WALNUT, 'lvl': 4.6},
               'davant': {'ramp': WALNUT, 'lvl': lambda s, t, P: 2.9 + (hr(int(s) // 2, 3) - 0.5) * 0.3}})
    pcx = _desk_fx(418.5)
    for (dx, y0_, y1_, lvl) in ((4, yb + 2, yb + 10, 3.4), (1.5, yb + 4, yb + 7, 0.4)):
        e.quad('calaix', _desk_pt(pcx - dx, y1_, lz0 - 0.3), _desk_pt(pcx + dx, y1_, lz0 - 0.3), _desk_pt(pcx + dx, y0_, lz0 - 0.3),
               _desk_pt(pcx - dx, y0_, lz0 - 0.3), ramp=IRON, lvl=lvl, dues_cares=True)
    # l'ombra del calaix al terra
    e.foscor('calaix', _desk_pt(x0 - 2, 0.7, lz0 - 5), _desk_pt(x1 + 5, 0.7, lz0 - 5), _desk_pt(x1 + 5, 0.7, -d / 2),
             _desk_pt(x0 - 2, 0.7, -d / 2), lambda s, t: 0.35)


def fbm_pel(s, t):
    return hr(int(s) // 2, int(t) // 2, 17)


# ─── Composició ─────────────────────────────────────────────────────────────

def _render(tex=None, obert=False):
    cv = Canvas(light=LIGHT)
    cv.S = 1                                                       # (tres_d: un píxel de sala per píxel real)
    e = escena(cv, tex, obert)
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)    # la barra de verbs: negre
    return cv.img, e


@functools.lru_cache(maxsize=None)
def _base():
    return _render()


def bg(cv, t=0.0):
    cv.img.paste(_base()[0])
    cv.P = cv.img.load()


def _calaix_prop(cv):
    """El calaix obert (decorat `calaix_obert`): la sala amb el calaix estirat, menys la de sempre."""
    img, _ = _render(obert=True)
    cv.img.alpha_composite(frame_diff(img, _base()[0]))
    cv.P = cv.img.load()


PROPS = {'calaix_obert': _calaix_prop}


# ─── Animació: el fum, les estrelles, els forns i la pols al raig de la lluna ─

def _pols(img, tt, n=34, seed=7):
    """Pols que sura dins el raig de la lluna: motes al món, entre la finestra i el terra, a la mida de la distància."""
    rnd = random.Random(seed)
    P = img.load()
    z0, z1, y0, y1 = WIN
    for _ in range(n):
        zw, yw, s = rnd.uniform(z0 + 6, z1 - 6), rnd.uniform(y0 + 6, y1 - 6), rnd.uniform(20, 200)
        s0, m, fi = rnd.random(), rnd.choice((1, 2, 3)), rnd.uniform(0, 6.283)
        ph = (s0 + tt) % 1
        x = s + 6 * ph
        Pw = (x, yw + MOON_D[1] * x - 8 * ph + 2 * math.sin(2 * math.pi * tt * m + fi),
              zw + MOON_D[2] * x + 2 * math.sin(2 * math.pi * tt * (4 - m) + fi * 1.7))
        if Pw[1] < 1:
            continue
        u, v, _ = CAM.projecta(Pw)
        u, v = int(u), int(v)
        a = 0.75 * math.sin(math.pi * ph)
        if 0 <= u < W and 0 <= v <= BOTTOM and a > 0.06:
            o = P[u, v]
            P[u, v] = mix(o, (206, 216, 248), min(1.0, a)) + (o[3],)


def _ambient_frames(n=24):
    base, e = _base()
    out = []
    for i in range(n):
        t = i / n
        img = base.copy()
        if t:
            img.alpha_composite(e.capa(_paret(t), {'paret_esq'}))
        _pols(img, t)
        out.append(frame_diff(img, base))
    return out


ANIMS = {'ambient': {'frames': _ambient_frames, 'frameDuration': 130}}


def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


# Capes del davant: el primer pla (sempre davant), el faristol i l'escriptori (qui hi passa per darrere, hi queda
# darrere).
FRONT = [
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20},
    {'id': 'davant_faristol', 'mask': _amo({'faristol'}), 'baseline': _p(LECT[0], LECT[1])[1], 'zIndex': 20},
    {'id': 'davant_taula', 'mask': _amo({'taula', 'expedient', 'lampada'}), 'baseline': _p(DESK[0], DESK[1] - 10)[1],
     'zIndex': 20},
]


# ─── Geometria (coordenades de sala, projectades) ────────────────────────────

def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


def _z_escala(k, x=250):
    lo, hi = -2000.0, 3000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.escala((x, 0, z)) > k:
            lo = z
        else:
            hi = z
    return z


def _escala_a(v):
    """L'escala d'un personatge amb els peus a la y de pantalla `v` (al terra, la profunditat només depèn de v)."""
    lo, hi = -500.0, 3000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.projecta((250, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((250, 0, (lo + hi) / 2))


V12 = round(CAM.projecta((250, 0, _z_escala(1.2)))[1])     # la y de pantalla on un personatge fa 1,2


def _retalla_v(poly, vmax):
    """Un polígon de pantalla retallat per la pantalla i per sota de la y `vmax`."""
    for keep, cut in ((lambda p: p[1] <= vmax, lambda a, b: (a[0] + (b[0] - a[0]) * (vmax - a[1]) / (b[1] - a[1]), vmax)),
                      (lambda p: p[0] >= 0, lambda a, b: (0, a[1] + (b[1] - a[1]) * (0 - a[0]) / (b[0] - a[0]))),
                      (lambda p: p[0] <= W - 1, lambda a, b: (W - 1, a[1] + (b[1] - a[1]) * (W - 1 - a[0]) / (b[0] - a[0])))):
        out = []
        for A, B in zip(poly, poly[1:] + poly[:1]):
            if keep(A):
                out.append(A)
            if keep(A) != keep(B):
                out.append(cut(A, B))
        poly = out
    return [(round(u), round(v)) for u, v in poly]


# El terra on es camina (al món): de la porta a la cantonada, per davant de l'escriptori i fins a la prestatgeria.
WALK_MON = [(14, 60), (14, 284), (60, 284), (64, 210), (300, 196), (340, 264), (520, 264), (620, -200), (14, -200)]
_WALK = _retalla_v([CAM.projecta((x, 0, z))[:2] for x, z in WALK_MON], V12)
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)


def _forat(cx, cz, w, d, m=10):
    return [_p(cx - w / 2 - m, cz - d / 2 - m), _p(cx + w / 2 + m, cz - d / 2 - m), _p(cx + w / 2 + m, cz + d / 2 + m),
            _p(cx - w / 2 - m, cz + d / 2 + m)]


_PORTRAIT = (_w(272), _w(347), _y(121), _y(36))
_DOOR = (_wz(11), _wz(77), _y(83))


def _calaix():
    h = DESK[4]
    pts = [_desk_pt(_desk_fx(fx), h * (HW - fy) / 44, -DESK[3] / 2) for fx in (378, 459) for fy in (174, 198)]
    return _rect_mon(*pts)


def _expedient():
    h, d = DESK[4], DESK[3]
    return _rect_mon(*[_desk_pt(_desk_fx(fx), h + y, z) for fx in (385, 452) for z in (-d / 2, d / 2) for y in (0, 3)])


def _llibre():
    fx_, fz_ = LECT
    return _rect_mon(*[(fx_ + (px - 552), 225 - py, fz_) for px in (519, 588) for py in (141, 178)])


GEOMETRIA = {
    'things': {
        'porta_magatzem': {'rect': _rect_mon((0, _DOOR[2], _DOOR[0]), (0, 0, _DOOR[1])), 'walk': _p(40, (_DOOR[0] + _DOOR[1]) / 2)},
        'retrat': {'rect': _rect_mon((_PORTRAIT[0], _PORTRAIT[3], ZW), (_PORTRAIT[1], _PORTRAIT[2], ZW)), 'walk': _p(80, 250)},
        'calaix': {'rect': _calaix(), 'walk': _p(DESK[0] + 6, DESK[1] - 48)},
        'expedient_sic': {'rect': _expedient(), 'walk': _p(DESK[0] - 6, DESK[1] - 46)},
        'llibre_inventari': {'rect': _llibre(), 'walk': _p(LECT[0] - 10, LECT[1] - 34)},
    },
    'spawns': {'iri': _p(46, 120)},
    'walkable': _WALK,
    'forats': [_forat(LECT[0], LECT[1], 30, 22, m=6)],
    'floorSquash': 0.42,                           # (la càmera, picada: el terra es veu aixafat)
    # L'ombra de contacte: la llum dominant és la làmpada de banquer (el punt del terra sota la làmpada).
    'characterShadow': {'enabled': True, 'color': '#0a0608', 'alpha': 0.42, 'squash': 0.4, 'core': 0.6,
                        'light': {'x': _p(LAMP_P[0], LAMP_P[2])[0], 'y': _p(LAMP_P[0], LAMP_P[2])[1], 'stretch': 0.7,
                                  'reach': 170}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    'characterLights': {
        'ambient': '#7c7c94',                                                           # nit, freda
        'lights': [
            {'x': _p(LAMP_P[0], LAMP_P[2], LAMP_P[1])[0], 'y': _p(LAMP_P[0], LAMP_P[2], LAMP_P[1])[1], 'radius': 220,
             'color': '#ffe29a', 'intensity': 1.0},                                     # la làmpada de banquer
            {'x': _p(0, (WIN[0] + WIN[1]) / 2, 110)[0], 'y': _p(0, (WIN[0] + WIN[1]) / 2, 110)[1], 'radius': 220,
             'color': '#aab8f0', 'intensity': 0.7},                                     # la lluna
        ],
    },
}
