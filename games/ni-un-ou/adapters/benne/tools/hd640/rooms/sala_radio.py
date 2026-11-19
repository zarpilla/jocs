"""
Ni un ou — la sala de ràdio de l'Arenga, de nit. EN 3D (hd640/tres_d.py), a 1×.

Una càmera alta, girada cap a la dreta, que mira la cantonada del fons a la dreta (la sala és a babord del pont: la
porta del pont és a la paret de la dreta):
  - a la paret del fons, el **suro** amb els avisos i el **rellotge** de ràdio, la **ràdio** (la SAILOR) damunt la
    taula, el **panell de l'antena** (el que s'obre), el prestatge dels llibres, l'**ull de bou** i l'extintor;
  - a la paret de la dreta, en escorç, la **porta estanca del pont**, amb el vidre i la consola del pont al darrere;
  - la **taula** separada de la paret, amb volum (la tapa, la calaixera, el costat), i la ràdio damunt amb tres cares;
    el tamboret al davant (s'hi passa per darrere); el llum de sostre de pantalla verda, penjat damunt la taula;
  - primer pla: l'arxivador i les canonades del sostre a l'esquerra, i una canonada que baixa a la dreta.

Tot el detall ve del dibuix pla de sempre (sala_radio_pla_comu.py), projectat; els decorats (`cable`,
`panell_obert`, `panell_reparat`) i l'animació `mar` també, per les mateixes superfícies (la xapa del panell, a
terra, és un volum). `dia` és l'escena sencera de dia, i `dia_mar`, el mar de dia per la porta.

El món: x a la dreta (0 = on comença el suro), y amunt (0 = el terra), z cap al fons (300 = la paret del fons);
1 unitat = 1 píxel de sala a la distància on un personatge fa ≈110 px (escala 1).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from PIL import Image

from hd.pix import Canvas, Light, W, H, hr
from hd.rooms.arenga import CAB, DARK, WHITEP, REDP, BRASS, box
from hd.rooms.comu import _diff
from hd.rooms.exterior import fbm
from hd.rooms.pont import BRI, FLOORB
from hd640.rooms import sala_radio_pla_comu as PL
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
ZW = 300                                           # la paret del fons
HW = PL.FLOOR_Y                                    # l'alçada de les parets (el dibuix pla fa 203 fins al terra)
XB = 90                                            # al dibuix pla, on comença la paret del fons (abans, la porta)
XR = W - XB                                        # la paret de la dreta (x del món)
ZD = 230                                           # a la paret de la dreta, on cau la x 0 del dibuix pla (la porta)
XL = -260                                          # on s'acaba la paret del fons per l'esquerra (fora de la pantalla)
DESK = (94, 326, 250, 290, 59)                     # la taula: x0, x1, z del davant, z del darrere, alçada
RADIO = (112, 310, 262, 292, 66, 124)              # la ràdio: x0, x1, z0, z1, y de baix (del frontal), y de dalt
STOOL = (206, 222)                                 # el tamboret (x, z)
LAMP = (212, 160, 266)                             # el llum (x, y de la pantalla, z)
CRATE = (452, 160, 46, 32, 30, -0.45)              # la caixa de recanvis: x, z, ample, fons, alt, gir
PAPER = [(60, 56, 46), (120, 114, 96), (176, 168, 140), (214, 206, 176)]


def _w(fx):
    """Una x del dibuix pla de la paret del fons → la x del món."""
    return fx - XB


def _wz(fx):
    """Una x del dibuix pla de la paret de la dreta (la porta) → la z del món."""
    return ZD - fx


def _y(fy):
    """Una y del dibuix pla (el terra, a 203) → l'alçada del món."""
    return HW - fy


CAM = Camera(pos=(250, 196, -190), yaw=0.17, pitch=0.17, f=380, centre=(314, 68))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)  # (la llum és la del món: la de l'Escena)
PORT_C = (_w(588), _y(66), ZW)
DOOR_C = (XR, 70, _wz(43))


def _llums(dia=False):
    if dia:
        return [Llum(PORT_C, 300, 1.2, power=1.3),                                # l'ull de bou
                Llum((XR - 4, 90, _wz(43)), 320, 1.6, power=1.2),                 # la claror del pont, per la porta
                Llum((LAMP[0], LAMP[1] - 6, LAMP[2]), 200, 1.0, power=1.5)]       # el llum (encès)
    return [Llum((LAMP[0], LAMP[1] - 6, LAMP[2]), 250, 2.0, power=1.5),           # el llum de pantalla verda
            Llum((XR - 4, 80, _wz(43)), 150, 0.8, power=1.6),                     # el pont, per la porta
            Llum(PORT_C, 140, 0.5, power=1.5),                                    # la lluna, per l'ull de bou
            Llum((_w(311), 100, RADIO[2] - 4), 60, 0.5, power=1.8)]               # el visor de la ràdio


# ─── Les textures: la sala pla de sempre ─────────────────────────────────────

def _llum_pla(dia=False):
    """La llum del dibuix pla, sense la vinyeta (les vores del pla ara són al mig de la sala)."""
    src = PL.LIGHT_DIA if dia else PL.LIGHT
    l = Light(ambient=src.ambient, vignette=None, floor_fade=None)
    l.points = list(src.points)
    return l


def _canvas(dia=False, transparent=False):
    return Canvas(light=_llum_pla(dia), transparent=transparent)


def _sostre(cv):
    """El sostre del dibuix pla (els baos, la safata de cables) sense el llum (ara penja en 3D)."""
    cv.rect(0, 0, W - 1, 23, DARK, 2.2)
    for bx in range(-26, W, 74):
        box(cv, bx - 3, 0, bx + 8, 25, BRI, 2.0, grad=0.8)
        cv.hline(bx - 2, bx + 7, 25, BRI, 1.0)
    cv.hline(0, W - 1, 24, BRI, 1.2)
    cv.hline(0, W - 1, 25, BRI, 3.0)
    box(cv, 0, 29, W - 1, 35, CAB, 2.4)
    cv.hline(0, W - 1, 30, CAB, 3.2)
    for x in range(6, W, 52):
        box(cv, x, 28, x + 3, 36, CAB, 3.4)
    for x in range(20, W, 140):
        for i in range(10):
            cv.put(x + i * 3, 36 + round(math.sin(i * 0.5) * 1.5 + i * 0.2), PL.CABLE, 2.4)


def _paret(dia=False, f=0):
    """Les parets planes, de cara: la porta del pont, el suro, el rellotge, el panell, el prestatge, l'ull de bou
    i l'extintor (sense la taula, la ràdio ni el terra)."""
    PL._MODE['dia'], PL._ANIM['f'] = dia, f
    try:
        cv = _canvas(dia)
        PL.wall(cv)
        _sostre(cv)
        PL.door(cv)
        PL.notices(cv)
        PL.panel(cv)
        PL.radio_clock(cv)
        PL.shelf(cv)
        PL.porthole(cv)
        PL.extinguisher(cv)
    finally:
        PL._MODE['dia'], PL._ANIM['f'] = False, 0
    return cv.img


def _planxa(dia=False):
    """La paret nua (planxes, el tub de terra, el sostre): per als trossos on el dibuix pla no arriba."""
    PL._MODE['dia'] = dia
    try:
        cv = _canvas(dia)
        PL.wall(cv)
        _sostre(cv)
    finally:
        PL._MODE['dia'] = False
    return cv.img


RADIO_BOX = (202, 78, 400, 135)                    # el frontal de la ràdio, al dibuix pla
MIC_BOX = (402, 86, 424, 144)                      # el micròfon penjat
DRAW_BOX = (336, PL.DESK_TOP + 6, 414, PL.FLOOR_Y + 3)   # la calaixera
PHONES_BOX = (220, PL.DESK_TOP - 15, 246, PL.DESK_TOP)


def _ras(dia=False):
    """La ràdio, el micròfon, la calaixera i els auriculars, plans sobre transparent (en surten els retalls)."""
    PL._MODE['dia'] = dia
    try:
        cv = _canvas(dia, transparent=True)
        PL.radio(cv)
        # la calaixera (al pla, dins la taula)
        x1 = 416
        box(cv, 336, PL.DESK_TOP + 6, x1 - 2, PL.FLOOR_Y + 3, CAB, 2.6, grad=0.6)
        for y in (156, 172, 188):
            box(cv, 342, y, x1 - 8, y + 12, CAB, 3.2)
            cv.hline(343, x1 - 9, y + 11, CAB, 2.0)
            box(cv, 366, y + 4, 388, y + 7, BRASS, 3.0)
            box(cv, 346, y + 3, 356, y + 7, WHITEP, 3.2, edge=False)
        # els auriculars, sols (al pla, damunt el frontal de la ràdio)
        ph = Canvas(light=_llum_pla(dia), transparent=True)
        ph.ring(232, PL.DESK_TOP - 6, 8, DARK, 2.4, step=8)
        ph.disc(224, PL.DESK_TOP - 3, 4, 3, DARK, 1.6)
        ph.disc(240, PL.DESK_TOP - 3, 4, 3, DARK, 1.6)
        cv.img.paste(ph.img.crop(PHONES_BOX), PHONES_BOX[:2])
    finally:
        PL._MODE['dia'] = False
    return cv.img


def _pantalla_llum():
    """La pantalla verda del llum, plana i transparent (es posa dreta en 3D)."""
    cv = Canvas(40, 16, light=_llum_pla(), transparent=True)
    lx, ly = 20, 10
    green = [(10, 24, 18), (18, 44, 30), (30, 70, 46), (50, 100, 66), (80, 130, 90), (120, 160, 120)]
    box(cv, lx - 2, ly - 10, lx + 2, ly - 7, CAB, 3.0)
    cv.poly([(lx - 4, ly - 8), (lx + 4, ly - 8), (lx + 16, ly), (lx - 16, ly)], green,
            lambda x, y: 2.8 - (x - lx) * 0.07 - (y - ly + 8) * 0.06)
    cv.hline(lx - 16, lx + 16, ly, green, 1.2)
    cv.disc(lx, ly + 1, 9, 3, [(160, 120, 60), (250, 220, 150), (255, 246, 220)], 2.0, lit=0)
    return cv.img, (20, 13)


def _xapa_tex():
    """La xapa del panell (la tapa que s'ha tret): el panell pla de sempre, retallat."""
    cv = _canvas(transparent=True)
    PL.panel(cv)
    x0, y0, x1, y1 = PL.PANEL
    return cv.img.crop((x0 - 3, y0 - 3, x1 + 4, y1 + 4))


# ─── Les superfícies ────────────────────────────────────────────────────────

def _terra(s, t, P):
    """Linòleum de rajoles grises en coordenades del món: les juntes fugen cap al fons; gastat davant la ràdio."""
    x, z = P[0], P[2]
    gx, gz = int(x // 40), int(z // 40)
    v = 3.3 + (hr(gx, gz, 6) - 0.5) * 0.5 + (fbm(x / 80, z / 50, 8) - 0.5) * 0.8
    if x % 40 < 1.1 or z % 40 < 1.1:
        return 2.0
    worn = max(0.0, 1 - math.hypot((x - STOOL[0]) / 90, (z - 226) / 40))
    v += worn * 0.6 * (0.6 + 0.4 * hr(int(x) // 2, int(z) // 2, 3))
    return v


def _estora(s, t, P):
    v = 1.6 + (0.6 if int(s) % 4 == 0 else 0) + (fbm(s / 30, t / 12, 2) - 0.5) * 0.6
    if s < 2 or t < 1.5 or s > 206 or t > 32.5:
        v -= 0.6
    return v


def _llum_ull(x, z):
    """La claror de la lluna que entra per l'ull de bou i cau pel terra, cap endavant i a l'esquerra (un disc
    estirat)."""
    cx, cz = PORT_C[0] - 70, ZW - 120
    d = math.hypot((x - cx) / 34, (z - cz) / 70)
    return 0.22 * max(0.0, 1 - d) ** 1.4


def llum_penjat(e, tex, angle=0.0):
    """El llum de pantalla verda, penjat del sostre damunt la taula; `angle`: quant es decanta (el balanceig)."""
    lx, ly, lz = LAMP
    img, peu = tex['pantalla']
    dx = (HW - ly) * math.sin(angle)
    e.linia((lx, HW, lz), (lx + dx * (HW - ly - 8) / (HW - ly), ly + 8, lz), PL.CABLE, 2.0)
    e.sprite('llum', img, peu, (lx + dx, ly - 3, lz))


def escena(cv, tex, estat=frozenset()):
    """Tota la sala, de lluny a prop. `estat`: 'dia', 'xapa' (la tapa del panell, a terra). → l'Escena."""
    dia = 'dia' in estat
    e = Escena(cv, CAM, _llums(dia), ambient=0.5 if dia else -0.2)
    zn = CAM.pos[2] + 60
    paret, planxa, ras = tex['paret'], tex['planxa'], tex['ras']
    # el sostre
    e.quad('sostre', (XL, HW, zn), (XR, HW, zn), (XR, HW, ZW), (XL, HW, ZW), ramp=BRI,
           lvl=lambda s, t, P: 1.4 - (1.2 if (P[0] + 26) % 74 < 8 else 0), dues_cares=True)
    # la paret del fons (z = 300): planxa a l'esquerra, i el dibuix pla (x 90..640) fins a la cantonada
    e.quad('paret_fons_esq', (XL, HW, ZW), (0, HW, ZW), (0, 0, ZW), (XL, 0, ZW), tex=(planxa, (100, 0, 100 - XL, HW)))
    e.quad('paret_fons', (0, HW, ZW), (XR, HW, ZW), (XR, 0, ZW), (0, 0, ZW), tex=(paret, (XB, 0, W, HW)))
    # la paret de la dreta (x = 550): planxa a la cantonada, la porta del pont (el dibuix pla, x 0..90), més planxa
    e.quad('paret_dreta_fons', (XR, HW, ZW), (XR, HW, ZD), (XR, 0, ZD), (XR, 0, ZW),
           tex=(planxa, (400, 0, 400 + ZW - ZD, HW)))
    e.quad('paret_dreta', (XR, HW, ZD), (XR, HW, ZD - XB), (XR, 0, ZD - XB), (XR, 0, ZD), tex=(paret, (0, 0, XB, HW)))
    e.quad('paret_dreta_prop', (XR, HW, ZD - XB), (XR, HW, zn), (XR, 0, zn), (XR, 0, ZD - XB),
           tex=(planxa, (90, 0, 90 + ZD - XB - zn, HW)))
    # el terra i l'estora davant la ràdio
    e.quad('terra', (XL, 0, ZW), (XR, 0, ZW), (XR, 0, zn), (XL, 0, zn), ramp=FLOORB, lvl=_terra)
    x0, x1, zf, zb, dh = DESK
    e.quad('estora', (x0 + 10, 0.3, zf - 6), (x0 + 218, 0.3, zf - 6), (x0 + 218, 0.3, zf - 40), (x0 + 10, 0.3, zf - 40),
           ramp=FLOORB, lvl=_estora)
    # la llum: el bassal del llum, la claror del pont per la porta i la lluna per l'ull de bou
    lx, ly, lz = LAMP
    e.claror((lx - 150, 0.5, lz + 40), (lx + 150, 0.5, lz + 40), (lx + 150, 0.5, lz - 200), (lx - 150, 0.5, lz - 200),
             (255, 220, 150), lambda s, t: (0.12 if dia else 0.26) * max(0.0, 1 - math.hypot(s - 150, (t - 60) * 0.9) / 150))
    dz0, dz1 = _wz(70), _wz(16)
    e.claror((XR, 0.4, dz1 + 10), (XR, 0.4, dz0 - 40), (XR - 180, 0.4, dz0 - 120), (XR - 180, 0.4, dz1 - 10),
             (140, 190, 200) if not dia else (210, 220, 230),
             lambda s, t: (0.4 if dia else 0.3) * max(0.0, 1 - t / 180) ** 1.2
             * max(0.0, math.sin(math.pi * min(1.0, s / max(1.0, 70 + 0.6 * t)))))
    e.claror((0, 0.6, ZW), (XR, 0.6, ZW), (XR, 0.6, 0), (0, 0.6, 0), (120, 140, 190) if not dia else (220, 226, 232),
             lambda s, t: (2.0 if dia else 1.0) * _llum_ull(s, ZW - t))
    # la foscor dels racons
    e.foscor('racons', (XL, 0.5, ZW), (XR, 0.5, ZW), (XR, 0.5, zn), (XL, 0.5, zn),
             lambda s, t: max(0.55 * max(0.0, 1 - t / 26), 0.5 * max(0.0, 1 - (XR - XL - s) / 22)))
    e.foscor('cantonada', (XR - 50, HW, ZW - 0.5), (XR, HW, ZW - 0.5), (XR, 0, ZW - 0.5), (XR - 50, 0, ZW - 0.5),
             lambda s, t: 0.5 * max(0.0, 1 - (50 - s) / 50))
    e.foscor('cantonada2', (XR - 0.5, HW, ZW), (XR - 0.5, HW, ZW - 50), (XR - 0.5, 0, ZW - 50), (XR - 0.5, 0, ZW),
             lambda s, t: 0.5 * max(0.0, 1 - s / 50))
    e.foscor('sostre_fosc', (XL, HW - 0.5, ZW - 0.6), (XR, HW - 0.5, ZW - 0.6), (XR, 0, ZW - 0.6), (XL, 0, ZW - 0.6),
             lambda s, t: 0.35 * max(0.0, 1 - t / 50))
    # la xapa del panell (decorat), a terra recolzada a la paret, entre el panell i l'extintor
    if 'xapa' in estat:
        xa0, xa1 = _w(522), _w(602)
        e.foscor('ombra_xapa', (xa0 - 4, 0.6, ZW), (xa1 + 6, 0.6, ZW), (xa1 + 6, 0.6, ZW - 26), (xa0 - 4, 0.6, ZW - 26),
                 lambda s, t: 0.55 * max(0.0, 1 - t / 26))
        xt = tex['xapa']
        e.quad('xapa', (xa0, 84, ZW - 3), (xa1, 84, ZW - 3), (xa1, 0, ZW - 20), (xa0, 0, ZW - 20),
               tex=(xt, (0, 0, xt.width, xt.height)))
        e.caixa('xapa', xa0, xa1, 0, 2, ZW - 22, ZW - 18, BRI, 1.6)
    # els cables pel terra: de sota la taula cap a la paret
    for ramp, lv, pts in (
            (PL.CABLE, 2.2, [(110, 0.8, zb - 4), (88, 0.8, 236), (60, 0.8, 250), (30, 0.8, 296)]),
            (REDP, 1.6, [(300, 0.8, zb - 2), (330, 0.8, 240), (360, 0.8, 262), (380, 0.8, 298)])):
        e.cable('cables', pts, ramp, lv, gruix=2.0)
    # la taula: la tapa, la pota de l'esquerra i la calaixera (el dibuix pla), amb l'ombra
    e.foscor('ombra_taula', (x0 - 6, 0.6, zb + 6), (x1 + 8, 0.6, zb + 6), (x1 + 8, 0.6, zf - 22), (x0 - 6, 0.6, zf - 22),
             lambda s, t: 0.5 * min(1.0, max(0.0, (zb - zf + 28 - t) / 22)) if t > 2 else 0.25)
    e.caixa('taula', x0 + 2, x0 + 10, 0, dh - 5, zf + 2, zb - 2, CAB, 2.2,
            cares={'davant': {'ramp': CAB, 'lvl': 2.6}, 'dreta': {'ramp': CAB, 'lvl': 1.6}})
    cx0, cx1 = _w(336) + 4, x1 - 2
    e.caixa('taula', cx0, cx1, 0, dh - 5, zf + 2, zb - 2, CAB, 2.0,
            cares={'davant': {'tex': (ras, DRAW_BOX)}, 'esquerra': {'ramp': CAB, 'lvl': 1.4},
                   'dreta': {'ramp': CAB, 'lvl': 1.8}})
    e.caixa('taula', x0, x1, dh - 5, dh, zf, zb, PL.WOOD, 3.6,
            cares={'dalt': {'ramp': PL.WOOD, 'lvl': lambda s, t, P: 3.8 + (fbm(s / 40, t / 6, 5) - 0.5) * 0.8
                            - (0.6 if int(t) % 9 == 0 else 0)},
                   'davant': {'ramp': PL.WOOD, 'lvl': lambda s, t, P: 4.4 if t < 1.2 else 3.2},
                   'dreta': {'ramp': PL.WOOD, 'lvl': 2.6}})
    # la ràdio damunt la taula: el sòcol, el frontal (el dibuix pla) i la tapa i els costats
    rx0, rx1, rz0, rz1, ry0, ry1 = RADIO
    e.caixa('radio', rx0 + 4, rx1 - 4, dh, ry0, rz0 + 2, rz1, CAB, 1.6)
    e.caixa('radio', rx0, rx1, ry0, ry1, rz0, rz1, CAB, 2.6,
            cares={'davant': {'tex': (ras, RADIO_BOX)},
                   'dalt': {'ramp': CAB, 'lvl': lambda s, t, P: 3.6 - (1.6 if 30 < s < 168 and t % 4 < 1.4 and t > 18 else 0)},
                   'dreta': {'ramp': CAB, 'lvl': lambda s, t, P: 2.0 - (0.8 if abs(t - 2) < 1 else 0)},
                   'esquerra': {'ramp': CAB, 'lvl': 2.4}})
    # el cable de la ràdio al panell (per darrere) i el de l'antena, que baixa del sostre
    e.cable('cable_panell', [(rx1, ry0 + 8, rz1 - 6), (rx1 + 12, ry0 + 4, ZW - 4), (_w(421), _y(141), ZW - 1)],
            PL.CABLE, 2.4, gruix=2.4)
    # damunt la taula: el micròfon penjat al costat de la ràdio, els auriculars, el llibre de registre, la tassa i el
    # llapis
    e.sprite('radio', ras.crop(MIC_BOX), (6, MIC_BOX[3] - MIC_BOX[1] - 1), (rx1 + 10, dh, rz0 + 10))
    e.sprite('radio', ras.crop(PHONES_BOX), (12, PHONES_BOX[3] - PHONES_BOX[1] - 1), (_w(232), dh, zf + 12))
    e.quad('radio', (_w(298), dh + 0.6, zf + 22), (_w(352), dh + 0.6, zf + 22), (_w(352), dh + 0.6, zf + 6),
           (_w(298), dh + 0.6, zf + 6), ramp=WHITEP,
           lvl=lambda s, t, P: 2.6 if abs(s - 27) < 0.8 else (3.0 if int(t) % 3 == 0 and 3 < s < 51 else 4.2))
    e.caixa('radio', _w(190), _w(198), dh, dh + 9, zf + 8, zf + 16, WHITEP, 3.6,
            cares={'dalt': {'ramp': PL.WOOD, 'lvl': 1.2}})
    e.caixa_girada('radio', _w(366), zf + 12, 16, 2, 2, -0.5, PL.YELL, 4.0, y0=dh)
    # el llum, penjat del sostre damunt la taula
    if 'sense_llum' not in estat:
        llum_penjat(e, tex)
    # el tamboret, davant la taula, una mica girat
    sx, sz = STOOL
    e.foscor('ombra_tamboret', (sx - 22, 0.7, sz + 16), (sx + 22, 0.7, sz + 16), (sx + 22, 0.7, sz - 16),
             (sx - 22, 0.7, sz - 16), lambda s, t: 0.6 * max(0.0, 1 - ((s - 22) / 22) ** 2 - ((t - 16) / 16) ** 2) * 1.6)
    a = 0.3
    c_, s_ = math.cos(a), math.sin(a)
    for lx_, lz_ in ((-15, -10), (15, -10), (-15, 10), (15, 10)):
        px, pz = sx + lx_ * c_ - lz_ * s_, sz + lx_ * s_ + lz_ * c_
        e.caixa('tamboret', px - 1.2, px + 1.2, 0, 26, pz - 1.2, pz + 1.2, CAB, 2.4)
    e.caixa_girada('tamboret', sx, sz, 32, 22, 1.6, a, CAB, 2.0, y0=8)
    e.caixa_girada('tamboret', sx, sz, 46, 30, 4, a, PL.WOOD, 3.4, y0=26,
                   cares={'dalt': {'ramp': PL.WOOD, 'lvl': lambda s, t, P: 4.4 - (0.6 if int(s) % 10 == 0 else 0)},
                          'davant': {'ramp': PL.WOOD, 'lvl': 3.0}})
    # la caixa de recanvis, a terra i girada (s'hi passa per darrere), i la paperera
    bx, bz, bw, bd, bh, ba = CRATE
    e.foscor('ombra_caixa', (bx - 34, 0.6, bz + 30), (bx + 36, 0.6, bz + 30), (bx + 36, 0.6, bz - 30),
             (bx - 34, 0.6, bz - 30), lambda s, t: 0.6 * max(0.0, 1 - ((s - 35) / 33) ** 2 - ((t - 30) / 26) ** 2) * 1.5)

    def llates(s, t, P):
        v = 3.0 + (fbm(s / 12, t / 6, 3) - 0.5) * 0.8
        if t % 9 < 1.2 or s < 2 or s > bw - 2:
            v -= 1.4
        return v
    e.caixa_girada('caixa', bx, bz, bw, bd, bh, ba, PL.WOOD, 2.4,
                   cares={'davant': {'ramp': PL.WOOD, 'lvl': lambda s, t, P: 4.2 if 12 < s < 30 and 9 < t < 17 and
                                     int(s + t) % 3 else llates(s, t, P)},
                          'dalt': {'ramp': PL.WOOD, 'lvl': lambda s, t, P: 3.8 - (1.2 if t % 10 < 1.2 else 0)},
                          'esquerra': {'ramp': PL.WOOD, 'lvl': lambda s, t, P: llates(s, t, P) - 1.0},
                          'dreta': {'ramp': PL.WOOD, 'lvl': lambda s, t, P: llates(s, t, P) - 0.6}})
    e.cable('caixa', [(bx - 8, bh + 0.5, bz - 4), (bx - 2, bh + 3, bz + 6), (bx + 8, bh + 0.5, bz)], PL.CABLE, 2.4,
            gruix=2.0)
    e.caixa('paperera', 14, 32, 0, 24, 236, 254, CAB, 1.8,
            cares={'davant': {'ramp': CAB, 'lvl': lambda s, t, P: 2.8 if int(s) % 3 == 0 or int(t) % 3 == 0 else 0.8},
                   'dreta': {'ramp': CAB, 'lvl': lambda s, t, P: 2.2 if int(s) % 3 == 0 or int(t) % 3 == 0 else 0.6},
                   'dalt': {'ramp': PAPER, 'lvl': 2.6}})
    # primer pla: l'arxivador i les canonades a l'esquerra, els cables que pengen, i una canonada a la dreta
    FOSC = [(3, 4, 6), (7, 9, 12), (12, 15, 19), (18, 22, 27), (26, 31, 37), (36, 42, 49)]
    e.caixa('primer_pla', 50, 120, 0, 132, 14, 64, FOSC, 2.0,                           # l'arxivador
            cares={'dreta': {'ramp': FOSC, 'lvl': lambda s, t, P: 2.0 + (1.4 if t % 33 < 2 else 0)
                             + (1.6 if 14 < t % 33 < 18 and 18 < s < 34 else 0)},
                   'dalt': {'ramp': FOSC, 'lvl': 2.8},
                   'davant': {'ramp': FOSC, 'lvl': lambda s, t, P: 1.4 + (1.2 if t % 33 < 2 else 0)}})
    e.caixa_girada('primer_pla', 86, 40, 40, 30, 20, 0.35, FOSC, 2.2, y0=132,
                   cares={'dalt': {'ramp': [(30, 22, 12), (60, 44, 24), (96, 70, 40)], 'lvl': 1.6}})
    e.caixa('primer_pla', XL, XR, 182, HW, 18, 36, FOSC, 1.6,                          # el bao, en silueta
            cares={'davant': {'ramp': FOSC, 'lvl': lambda s, t, P: 1.8 + (1.4 if t < 2 else 0)
                              + (1.2 if (s % 60) < 2.5 and 6 < t < 16 else 0)}})
    e.tub('primer_pla', (XR - 30, 176, 300), (XR - 30, 176, 0), 5, FOSC, 2.6, brides=40)
    for k, xx in enumerate((60, 78)):
        e.cable('primer_pla', [(xx, HW, 30 + k * 8), (xx + 8 + k * 4, 140 - k * 22, 36 + k * 8),
                               (xx + 2, 100 - k * 26, 42 + k * 8)], FOSC, 1.4, gruix=2.2)
    e.tub('primer_pla', (XR - 14, 0, 60), (XR - 14, HW, 60), 9, FOSC, 2.4, brides=46)
    return e


# ─── Composició ────────────────────────────────────────────────────────────

def _textures(dia=False, f=0):
    return {'paret': _paret(dia, f), 'planxa': _planxa(dia), 'ras': _ras(dia), 'pantalla': _pantalla_llum(),
            'xapa': _xapa_tex()}


@functools.lru_cache(maxsize=None)
def _tex(dia=False):
    return _textures(dia)


def _render(estat=frozenset(), tex=None):
    cv = Canvas(light=LIGHT)
    e = escena(cv, tex or _tex('dia' in estat), estat)
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)    # la barra de verbs: negre
    return cv.img, e


@functools.lru_cache(maxsize=None)
def _base():
    return _render()


@functools.lru_cache(maxsize=None)
def _base_dia():
    return _render(frozenset({'dia'}))


def bg(cv):
    img, _ = _base()
    cv.img.paste(img)
    cv.P = cv.img.load()


def _flat(fn, retall=None):
    cv = _canvas(transparent=True)
    fn(cv)
    if retall:
        keep = Image.new('RGBA', cv.img.size, (0, 0, 0, 0))
        keep.paste(cv.img.crop(retall), retall[:2])
        return keep
    return cv.img


def _capa(fn, retall=None):
    def draw(cv):
        _, e = _base()
        cv.img.alpha_composite(e.capa(_flat(fn, retall), {'paret_fons'}))
        cv.P = cv.img.load()
    return draw


def panell_obert(cv):
    """El panell sense la xapa (el forat, el cable tallat, el born), projectat a la paret; i la xapa, a terra
    recolzada a la paret, en 3D (la diferència amb el fons)."""
    img0, e = _base()
    img, _ = _render(frozenset({'xapa'}))
    out = _diff(img, img0)
    out.alpha_composite(e.capa(_flat(PL.panell_obert, (0, 0, 522, H)), {'paret_fons'}))
    cv.img.alpha_composite(out)
    cv.P = cv.img.load()


def dia(cv):
    """Decorat `dia` (Escenes 2 i 3): la sala sencera de dia, amb el cel gris a l'ull de bou i al vidre del pont, que
    es veu per la porta."""
    img, _ = _base_dia()
    img = img.copy()
    P = img.load()
    for Y in range(BOTTOM + 1):
        for X in range(W):
            o = P[X, Y]
            P[X, Y] = (int(o[0] * 0.92 + 12), int(o[1] * 0.92 + 13), int(o[2] * 0.92 + 14), 255)
    cv.img.paste(img)
    cv.P = cv.img.load()


PROPS = {'dia': dia, 'panell_obert': panell_obert, 'cable': _capa(PL.cable), 'panell_reparat': _capa(PL.panell_reparat)}


# ─── Animacions ────────────────────────────────────────────────────────────

def _frames(dia=False):
    """El mar pel vidre del pont, que es veu per la porta, i els pilots de la consola: la paret de la dreta a cada
    fotograma, menys la de sempre."""
    img0, e = _base_dia() if dia else _base()
    if dia:
        img0 = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        img0.paste(_dia_img())
    p0 = _tex(dia)['paret']
    out = [Image.new('RGBA', (W, H), (0, 0, 0, 0))]
    for f in range(1, PL.ANIM_N):
        img = img0.copy()
        img.alpha_composite(_amb_dia(e.capa(_diff(_paret(dia, f), p0), {'paret_dreta'}), dia))
        out.append(_diff(img, img0))
    return out


def _dia_img():
    cv = Canvas(light=LIGHT)
    dia(cv)
    return cv.img


def _amb_dia(img, dia):
    if not dia:
        return img
    P = img.load()
    for Y in range(img.height):
        for X in range(img.width):
            o = P[X, Y]
            if o[3]:
                P[X, Y] = (int(o[0] * 0.92 + 12), int(o[1] * 0.92 + 13), int(o[2] * 0.92 + 14), o[3])
    return img


def _frames_llum(n=16):
    """El llum penjat que es gronxa amb el balanceig del vaixell (±4°, lent): la sala sense el llum i, a sobre, el llum
    decantat, només on no hi ha res pintat després d'ell (el tamboret, el primer pla)."""
    img0, e0 = _base()
    sense, es = _render(frozenset({'sense_llum'}))
    despres = set(e0.ids[e0.ids.index('llum') + 1:])
    W_ = es.cv.w
    out = []
    for i in range(n):
        cv = Canvas(light=LIGHT, transparent=True)
        e = Escena(cv, CAM, _llums(False), ambient=-0.2)
        llum_penjat(e, _tex(False), 0.07 * math.sin(2 * math.pi * i / n))
        img = sense.copy()
        P, L = img.load(), cv.img.load()
        for Y in range(BOTTOM + 1):
            for X in range(W_):
                c = L[X, Y]
                if c[3] and es.ids[es.amo[Y * W_ + X]] not in despres:
                    P[X, Y] = c
        out.append(_diff(img, img0))
    return out


ANIMS = {'mar': {'frames': lambda: _frames(False), 'frameDuration': 260},
         'llum': {'frames': _frames_llum, 'frameDuration': 150},
         'dia_mar': {'frames': lambda: _frames(True), 'frameDuration': 260}}


def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


# Capes del davant: el primer pla (sempre davant) i el tamboret (qui hi passa per darrere, hi queda darrere).
FRONT = [
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20, 'variants': ('dia',)},
    {'id': 'davant_tamboret', 'mask': _amo({'tamboret'}), 'baseline': _p(STOOL[0], STOOL[1] - 8)[1], 'zIndex': 20, 'variants': ('dia',)},
    {'id': 'davant_caixa', 'mask': _amo({'caixa'}), 'baseline': _p(CRATE[0], CRATE[1] - 12)[1], 'zIndex': 20, 'variants': ('dia',)},
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


# El terra on es camina (al món): davant la taula, i a la dreta fins al panell i la porta del pont.
WALK_MON = [(-30, 120), (-30, 242), (DESK[1] + 8, 242), (DESK[1] + 8, 286), (530, 286), (532, 150), (510, 96),
            (0, 96)]
V_MAX = 238                                        # més a prop, el personatge passaria d'1,2: és per al primer pla
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
    return _rect_mon((_w(fx0), _y(fy0), ZW), (_w(fx1), _y(fy1), ZW))


_RADIO = _rect_mon(*[(x, y, z) for x in (RADIO[0], RADIO[1] + 18) for y in (DESK[4], RADIO[5]) for z in (RADIO[2], RADIO[3])])

GEOMETRIA = {
    'things': {
        'porta': {'rect': _rect_mon((XR, _y(85), _wz(12)), (XR, 0, _wz(72))), 'walk': _p(516, _wz(43))},
        'radio': {'rect': _RADIO, 'walk': _p((RADIO[0] + RADIO[1]) / 2, 232)},
        'panell': {'rect': _wall(437, 77, 523, 163), 'walk': _p(_w(480), 278)},
        'cable': {'rect': _wall(459, 99, 502, 142), 'walk': _p(_w(480), 278)},
    },
    'spawns': {'iri': _p(_w(480) - 20, 250), 'vet': _p(150, 200), 'bastida': _p(500, _wz(43) + 4)},
    'walkable': _WALK,
    'forats': [[_p(STOOL[0] + dx, STOOL[1] + dz) for dx, dz in ((-20, -14), (20, -14), (20, 14), (-20, 14))],
               [_p(CRATE[0] + dx * math.cos(CRATE[5]) - dz * math.sin(CRATE[5]),
                   CRATE[1] + dx * math.sin(CRATE[5]) + dz * math.cos(CRATE[5]))
                for dx, dz in ((-27, -20), (27, -20), (27, 20), (-27, 20))]],
    'floorSquash': 0.45,
    # L'ombra de contacte: el llum de damunt la taula (el punt del terra just a sota); curta, és llum de dalt.
    'characterShadow': {'enabled': True, 'color': '#06080e', 'alpha': 0.42, 'squash': 0.42, 'core': 0.6,
                        'light': {'x': _p(LAMP[0], LAMP[2])[0], 'y': _p(LAMP[0], LAMP[2])[1], 'stretch': 0.55,
                                  'reach': 150}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
}
