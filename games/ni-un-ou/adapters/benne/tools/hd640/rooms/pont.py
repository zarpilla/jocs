"""
Ni un ou — el pont de l'Arenga, de nit. EN 3D (hd640/tres_d.py), a 1×.

Una càmera alta, girada cap a l'esquerra, que mira la cantonada del fons (com el pont de la Cantimplora d'Aigua Verne
i la referència docs/referencies/sala-pont-control.png):
  - a la paret de l'esquerra, en escorç, la **boca de l'escala** que baixa al passadís (la llum càlida de baix s'escampa
    en diagonal pel terra) i la **porta estanca de la ràdio**, amb el baròmetre i el rellotge;
  - a la paret del fons, els **vidres** del pont (el mar de nit, la lluna), els repetidors penjats, el
    **muntacàrregues**, el **tub de veu** i la **porta del pal**, oberta a la nit;
  - la **consola**, separada dels vidres, amb tres cares (el frontal amb les portes de servei i el SAI, la tapa
    inclinada amb els commutadors, el costat): damunt, el **radar**, el **terminal** i la **impressora**;
  - el **timó** i la **cadira** alta, drets davant la consola (s'hi passa per darrere); la taula de cartes, girada;
  - primer pla: la quaderna i les canonades de l'esquerra, cables que pengen del sostre, i a baix a la dreta una
    canonada grossa i l'armari de les armilles, tallats per la vora.

Tot el detall ve del dibuix pla de sempre (pont_pla_comu.py), projectat; els decorats (`safata`, `guardacostes`) i
les animacions (`mar`, `radar`, `terminal`) també, per les mateixes superfícies. `dia` és l'escena sencera de dia
(amb forats a les pantalles), i `fosc`, el generador parat (els llums d'emergència, on són ara).

El món: x a la dreta (0 = la paret de l'escala), y amunt (0 = el terra), z cap al fons (300 = la paret dels vidres);
1 unitat = 1 píxel de sala a la distància on un personatge fa ≈110 px (escala 1).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from PIL import Image

from hd.pix import Canvas, Light, W, H, hr
from hd.rooms.arenga import CAB, ENG, DARK, WHITEP, REDP, YELL, BRASS, box
from hd.rooms.comu import _diff
from hd.rooms.exterior import fbm
from hd.rooms.pont import BRI, FLOORB
from hd640.rooms import pont_pla_comu as PL
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
ZW = 300                                           # la paret dels vidres
HW = PL.FLOOR_Y                                    # l'alçada de les parets (el dibuix pla fa 203 fins al terra)
XL = 146                                           # al dibuix pla, la cantonada: a l'esquerra, la paret de l'escala
ZL = 100                                           # on comença (z) el tros del dibuix pla a la paret de l'esquerra
XR = 760                                           # on s'acaba la paret del fons (fora de la pantalla)
CON = (26, 346, 262, 292, 59, 67)                  # la consola: x0, x1, z del davant, z del darrere, alçada davant/darrere
WHEEL = (150, 240)                                 # el peu del timó (x, z)
CHAIR = (322, 236)                                 # el peu de la cadira
TAULA = (468, 168, 64, 40, 50, 0.42)               # la taula de cartes: x, z, ample, fons, alçada, gir
LAMP = (230, 210)                                  # el llum de sostre (x, z)


def _w(fx):
    """Una x del dibuix pla de la paret del fons → la x del món."""
    return fx - XL


def _wz(fx):
    """Una x del dibuix pla de la paret de l'esquerra → la z del món."""
    return ZL + fx


def _y(fy):
    """Una y del dibuix pla (el terra, a 203) → l'alçada del món."""
    return HW - fy


def _cx(fx):
    """Una x del dibuix pla de la consola (149..488) → la x del món."""
    return CON[0] + (fx - 149) * (CON[1] - CON[0]) / (488 - 149)


def _con_y(z):
    """L'alçada de la tapa inclinada de la consola a la profunditat z."""
    x0, x1, zf, zb, hf, hb = CON
    return hf + (hb - hf) * (z - zf) / (zb - zf)


CAM = Camera(pos=(300, 196, -190), yaw=-0.17, pitch=0.17, f=380, centre=(326, 68))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)  # (la llum és la del món: la de l'Escena)
WIN_C = ((_w(PL.WIN[0]) + _w(PL.WIN[2])) / 2, _y((PL.WIN[1] + PL.WIN[3]) / 2), ZW)
TERM_C = (_cx(368), _con_y(286) + 22, 284)
RADAR_C = (_cx(200), _con_y(286) + 18, 284)
STAIRS_C = (4, 30, _wz(40))


def _llums(dia=False):
    if dia:
        return [Llum((WIN_C[0], 120, ZW + 40), 560, 2.2, power=1.1),                # la claror grisa dels vidres
                Llum((_w(610), 120, ZW + 10), 200, 0.8, power=1.4),                 # la porta del pal
                Llum(STAIRS_C, 110, 0.6, power=1.6)]
    return [Llum((LAMP[0], 196, LAMP[1]), 250, 1.4, power=1.4),                     # el llum de sostre, vermellós
            Llum(TERM_C, 120, 1.1, power=1.6),                                      # el terminal
            Llum(RADAR_C, 100, 0.9, power=1.7),                                     # el radar
            Llum(STAIRS_C, 130, 1.3, power=1.5),                                    # la llum càlida de l'escala
            Llum((WIN_C[0] - 60, 140, ZW + 20), 330, 0.7, power=1.2),               # la lluna, pels vidres
            Llum((_w(610), 110, ZW + 10), 110, 0.5, power=1.6)]                     # el llum de coberta del pal


# ─── Les textures: el pont pla de sempre ─────────────────────────────────────

def _llum_pla(dia=False):
    """La llum del dibuix pla, sense la vinyeta (les vores del pla ara són al mig de la sala)."""
    src = PL.LIGHT_DIA if dia else PL.LIGHT
    l = Light(ambient=src.ambient + (0.0 if dia else 0.2), vignette=None, floor_fade=None)
    l.points = list(src.points)
    return l


def _canvas(dia=False, transparent=False):
    return Canvas(light=_llum_pla(dia), transparent=transparent)


def _paret(dia=False, mar=0):
    """Les parets planes, de cara: les planxes, els vidres amb el mar, els repetidors, l'escala, la porta de la ràdio,
    el baròmetre, el muntacàrregues, el tub de veu i la porta del pal (sense la consola ni el terra)."""
    PL._MODE['dia'], PL._ANIM['mar'] = dia, mar
    try:
        cv = _canvas(dia)
        PL.wall(cv)
        PL.ceiling(cv)
        PL.windows(cv)
        PL.repeaters(cv)
        PL.stairs_down(cv)
        PL.radio_door(cv)
        PL.barometer(cv)
        PL.dumbwaiter(cv)
        PL.voice_tube(cv)
        PL.mast_door(cv)
    finally:
        PL._MODE['dia'], PL._ANIM['mar'] = False, 0
    return cv.img


def _planxa(dia=False):
    """La paret nua (planxes i reblons, el sostre amb els baos): per als trossos on el dibuix pla no arriba."""
    PL._MODE['dia'] = dia
    try:
        cv = _canvas(dia)
        PL.wall(cv)
        cv.rect(0, 0, W - 1, 23, DARK, 2.2)
        for bx in range(-13, W, 74):
            box(cv, bx - 3, 0, bx + 8, 25, BRI, 2.0, grad=0.8)
        cv.hline(0, W - 1, 24, BRI, 1.2)
        cv.hline(0, W - 1, 25, BRI, 3.0)
    finally:
        PL._MODE['dia'] = False
    return cv.img


def _sai(cv):
    """El SAI, al frontal de la consola (al pla, el dibuixava el terminal)."""
    from hd.rooms.comu import text
    box(cv, 336, 149, 395, 168, CAB, 2.0)
    for i in range(5):
        cv.rect(341 + i * 7, 155, 345 + i * 7, 161, PL.SCRG, 3.4 if i < 4 else 1.4, lit=0)
    cv.rect(377, 154, 390, 161, WHITEP, 3.0)
    text(cv, 'SAI', 378, 155, DARK, 0.6)
    cv.flat(382, 165, PL.GREENL)
    cv.flat(383, 165, PL.GREENL)
    cv.glow(382, 165, 5, PL.GREENL, 0.5)


def _consola(dia=False):
    """La consola plana (el frontal i la tapa inclinada amb els commutadors), amb el SAI."""
    PL._MODE['dia'] = dia
    try:
        cv = _canvas(dia)
        PL.wall(cv)                                                # (sota la tapa: no surt de la superfície)
        PL.console(cv)
        _sai(cv)
    finally:
        PL._MODE['dia'] = False
    return cv.img


RADAR_BOX = (164, 96, 240, 138)                    # els instruments damunt la consola, al dibuix pla
TERM_BOX = (334, 99, 401, 144)
PRINT_BOX = (409, 110, 464, 140)
WHEEL_BOX = (246, 138, 293, 212)
CHAIR_BOX = (443, 130, 480, 220)


def _instruments(dia=False, radar=0, terminal=0):
    """El radar, el terminal i la impressora, el timó i la cadira, plans sobre transparent (en surten els retalls)."""
    PL._MODE['dia'] = dia
    PL._ANIM['radar'], PL._ANIM['terminal'] = radar, terminal
    try:
        cv = _canvas(dia, transparent=True)
        PL.radar(cv)
        # el terminal sense el cable de l'antena (el cable baixa del sostre en 3D)
        x0, y0, x1, y1 = 336, 101, 400, 139
        box(cv, x0, y0, x1, y1, CAB, 2.2, grad=0.6)
        cv.hline(x0 + 1, x1 - 1, y0 + 1, CAB, 3.8)
        PL.screen(cv)
        cv.disc(x1 - 3, y1 - 3, 1, 1, CAB, 4.2)
        box(cv, 363, y1 + 1, 373, PL.CON_TOP - 7, CAB, 1.8)
        cv.poly([(339, PL.CON_TOP - 7), (397, PL.CON_TOP - 7), (400, PL.CON_TOP - 1), (336, PL.CON_TOP - 1)], CAB, 2.8)
        for row in (PL.CON_TOP - 5, PL.CON_TOP - 3):
            for x in range(340, 397, 3):
                cv.put(x + (1 if row == PL.CON_TOP - 3 else 0), row, CAB, 4.4)
        PL.printer(cv)
        PL.wheel(cv)
        PL.chair(cv)
    finally:
        PL._MODE['dia'] = False
        PL._ANIM['radar'], PL._ANIM['terminal'] = 0, 0
    return cv.img


def _peu(box_, fx, fy):
    """El punt (fx, fy) del dibuix pla, dins el retall `box_`."""
    return fx - box_[0], fy - box_[1]


# ─── Les superfícies ────────────────────────────────────────────────────────

def _terra(s, t, P):
    """Linòleum de rajoles grises en coordenades del món: les juntes fugen cap al fons; gastat davant el timó."""
    x, z = P[0], P[2]
    gx, gz = int(x // 40), int(z // 40)
    v = 3.3 + (hr(gx, gz, 5) - 0.5) * 0.5 + (fbm(x / 80, z / 50, 7) - 0.5) * 0.8
    if x % 40 < 1.1 or z % 40 < 1.1:
        return 2.0
    worn = max(0.0, 1 - math.hypot((x - WHEEL[0]) / 70, (z - 214) / 40))
    v += worn * 0.6 * (0.6 + 0.4 * hr(int(x) // 2, int(z) // 2, 3))
    if hr(int(x * 0.7), int(z * 0.7), 11) > 0.985:
        v -= 0.8                                                   # rascades
    return v


def _estora(s, t, P):
    """L'estora de goma davant la consola: els nervis, que s'empetiteixen cap al fons."""
    v = 1.6 + (0.6 if int(s) % 4 == 0 else 0) + (fbm(s / 30, t / 12, 2) - 0.5) * 0.6
    if s < 2 or t < 1.5 or s > 278 or t > 24.5:
        v -= 0.6
    return v


def _llum_lluna(x, z):
    """La claror de la lluna que entra pels vidres i cau en diagonal pel terra (cap a la dreta i endavant): quatre
    franges, una per vidre, tallades pels muntants."""
    t = (ZW - z)                                                   # quant ha baixat el raig des dels vidres
    xw = x - t * 0.55                                              # d'on ve, a la paret dels vidres
    if not (_w(PL.WIN[0]) + 4 < xw < _w(PL.WIN[2]) - 4):
        return 0.0
    fx = xw + XL
    for a, b in PL.PANES:
        if a + 3 < fx < b - 3:
            break
    else:
        return 0.0
    return 0.16 * max(0.0, 1 - t / 230) * min(1.0, (t - 30) / 40) if t > 30 else 0.0


def escena(cv, tex, estat=frozenset()):
    """Tota la sala, de lluny a prop. `estat`: 'dia'. → l'Escena (qui ha pintat què)."""
    dia = 'dia' in estat
    e = Escena(cv, CAM, _llums(dia), ambient=0.4 if dia else -0.3)
    zn = CAM.pos[2] + 60
    paret, planxa, con, ins = tex['paret'], tex['planxa'], tex['consola'], tex['instruments']
    # el sostre, fosc, amb els baos
    e.quad('sostre', (0, HW, zn), (XR, HW, zn), (XR, HW, ZW), (0, HW, ZW), ramp=BRI,
           lvl=lambda s, t, P: 1.4 - (1.2 if P[0] % 74 < 6 else 0), dues_cares=True)
    # la paret de l'esquerra (x = 0): de prop, planxa; després l'escala i la porta de la ràdio; i fins a la
    # cantonada, més planxa (tot del dibuix pla)
    e.quad('paret_esq_prop', (0, HW, zn), (0, HW, ZL), (0, 0, ZL), (0, 0, zn), tex=(planxa, (260, 0, 260 + ZL - zn, HW)))
    e.quad('paret_esq', (0, HW, ZL), (0, HW, ZL + XL), (0, 0, ZL + XL), (0, 0, ZL), tex=(paret, (0, 0, XL, HW)))
    e.quad('paret_esq_fons', (0, HW, ZL + XL), (0, HW, ZW), (0, 0, ZW), (0, 0, ZL + XL),
           tex=(planxa, (196, 0, 196 + ZW - ZL - XL, HW)))
    # la paret dels vidres (z = 300): el dibuix pla (x 146..640) i, a la dreta, més planxa
    e.quad('paret_fons', (0, HW, ZW), (W - XL, HW, ZW), (W - XL, 0, ZW), (0, 0, ZW), tex=(paret, (XL, 0, W, HW)))
    e.quad('paret_fons_dreta', (W - XL, HW, ZW), (XR, HW, ZW), (XR, 0, ZW), (W - XL, 0, ZW),
           tex=(planxa, (100, 0, 100 + XR - W + XL, HW)))
    # el terra
    e.quad('terra', (0, 0, ZW), (XR, 0, ZW), (XR, 0, zn), (0, 0, zn), ramp=FLOORB, lvl=_terra)
    x0, x1, zf, zb, hf, hb = CON
    e.quad('estora', (x0 + 20, 0.3, zf - 4), (x0 + 300, 0.3, zf - 4), (x0 + 300, 0.3, zf - 30), (x0 + 20, 0.3, zf - 30),
           ramp=FLOORB, lvl=_estora)
    # la llum: la claror càlida que puja de l'escala, en diagonal pel terra, i la lluna en franges pels vidres
    sz0, sz1 = _wz(11), _wz(69)
    e.claror((0, 0.4, sz1 + 20), (150, 0.4, sz1 + 60), (150, 0.4, sz0 - 60), (0, 0.4, sz0 - 4), (255, 186, 104),
             lambda s, t: (0.25 if dia else 0.55) * max(0.0, 1 - s / 150) ** 1.2
             * max(0.0, math.sin(math.pi * min(1.0, t / max(1.0, 62 + 0.8 * s)))))
    if not dia:
        e.claror((0, 0.5, ZW), (XR, 0.5, ZW), (XR, 0.5, 0), (0, 0.5, 0), (120, 140, 190),
                 lambda s, t: _llum_lluna(s, ZW - t))
    else:
        e.claror((0, 0.5, ZW), (XR, 0.5, ZW), (XR, 0.5, 0), (0, 0.5, 0), (200, 210, 220),
                 lambda s, t: 2.2 * _llum_lluna(s, ZW - t))
    # la foscor dels racons
    e.foscor('racons', (0, 0.5, ZW), (XR, 0.5, ZW), (XR, 0.5, zn), (0, 0.5, zn),
             lambda s, t: max(0.55 * max(0.0, 1 - t / 26), 0.5 * max(0.0, 1 - s / 22)))
    e.foscor('cantonada', (0, HW, ZW - 0.5), (50, HW, ZW - 0.5), (50, 0, ZW - 0.5), (0, 0, ZW - 0.5),
             lambda s, t: 0.5 * max(0.0, 1 - s / 50))
    e.foscor('cantonada2', (0.5, HW, ZW - 50), (0.5, HW, ZW), (0.5, 0, ZW), (0.5, 0, ZW - 50),
             lambda s, t: 0.5 * max(0.0, 1 - (50 - s) / 50))
    # el llum de sostre, amb el filtre vermell (de dia, apagat)
    lx, lz = LAMP
    e.caixa('llum', lx - 13, lx + 13, HW - 6, HW, lz - 8, lz + 8, CAB, 2.6)
    lens = [(60, 14, 12), (90, 50, 46), (120, 96, 92)] if dia else [(60, 14, 12), (130, 30, 24), (200, 70, 50),
                                                                       (250, 140, 110)]
    e.quad('llum', (lx - 11, HW - 6.2, lz + 6), (lx + 11, HW - 6.2, lz + 6), (lx + 11, HW - 6.2, lz - 6),
           (lx - 11, HW - 6.2, lz - 6), ramp=lens, lvl=1.6 if dia else 3.0, dues_cares=True)
    if not dia:
        e.claror((lx - 120, 0.6, lz + 100), (lx + 120, 0.6, lz + 100), (lx + 120, 0.6, lz - 100),
                 (lx - 120, 0.6, lz - 100), (150, 40, 34),
                 lambda s, t: 0.16 * max(0.0, 1 - math.hypot(s - 120, t - 100) / 120))
    # els cables pel terra: de sota la consola cap a la paret de l'esquerra i cap a la taula de cartes
    for ramp, lv, pts in (
            (PL.CABLE, 2.4, [(60, 0.8, zf + 6), (48, 0.8, zf - 8), (58, 0.8, 226), (26, 0.8, 214), (2, 0.8, 214)]),
            (REDP, 1.8, [(300, 0.8, zf + 4), (312, 0.8, zf - 10), (360, 0.8, 236), (430, 0.8, 214),
                         (TAULA[0] - 10, 0.8, TAULA[1] + 18)])):
        e.cable('cables', pts, ramp, lv, gruix=2.2)
    # el cable de l'antena, que baixa del sostre fins al terminal
    tx = TERM_C[0] + 34
    e.cable('cable_antena', [(tx, HW, ZW - 4), (tx, 140, ZW - 6), (tx - 1, _con_y(288) + 26, 290),
                             (tx - 8, _con_y(288) + 20, 288)], PL.CABLE, 2.4, gruix=2.2)
    # la consola: el costat, la tapa inclinada i el frontal (el dibuix pla), amb l'ombra
    e.foscor('ombra_consola', (x0 - 6, 0.6, zf), (x1 + 10, 0.6, zf), (x1 + 10, 0.6, zf - 24), (x0 - 6, 0.6, zf - 24),
             lambda s, t: 0.5 * max(0.0, 1 - t / 24))
    e.quad('consola', (x0, hb, zb), (x0, hf, zf), (x0, 0, zf), (x0, 0, zb), ramp=ENG,
           lvl=lambda s, t, P: 2.2 - (1.4 if P[1] < 6 else 0))
    e.quad('consola', (x1, hf, zf), (x1, hb, zb), (x1, 0, zb), (x1, 0, zf), ramp=ENG,
           lvl=lambda s, t, P: 2.0 - (1.4 if P[1] < 6 else 0) + (0.8 if s < 1.5 else 0))
    e.quad('consola_dalt', (x0, hb, zb), (x1, hb, zb), (x1, hf, zf), (x0, hf, zf),
           tex=(con, (149, PL.CON_TOP - 8, 488, PL.CON_TOP)))
    e.quad('consola_davant', (x0, hf, zf), (x1, hf, zf), (x1, 0, zf), (x0, 0, zf),
           tex=(con, (149, PL.CON_TOP, 488, HW + 3)))
    # els instruments, drets damunt la tapa
    zi = 284
    for sid, bx, fx in (('radar', RADAR_BOX, 200), ('terminal', TERM_BOX, 368), ('impressora', PRINT_BOX, 436)):
        fy = bx[3] - 1 if sid != 'terminal' else PL.CON_TOP - 1
        e.sprite(sid, ins.crop(bx), _peu(bx, fx, fy), (_cx(fx), _con_y(zi), zi))
    # la taula de cartes, girada, amb la carta nàutica damunt (s'hi passa per darrere)
    tx_, tz_, tw, td, th, ta = TAULA
    e.foscor('ombra_taula', (tx_ - 46, 0.6, tz_ + 40), (tx_ + 50, 0.6, tz_ + 40), (tx_ + 50, 0.6, tz_ - 44),
             (tx_ - 46, 0.6, tz_ - 44), lambda s, t: 0.55 * max(0.0, 1 - ((s - 48) / 46) ** 2 - ((t - 42) / 38) ** 2) * 1.5)
    c_, s_ = math.cos(ta), math.sin(ta)
    for lx_, lz_ in ((-tw / 2 + 4, -td / 2 + 4), (tw / 2 - 4, -td / 2 + 4), (-tw / 2 + 4, td / 2 - 4), (tw / 2 - 4, td / 2 - 4)):
        e.caixa_girada('taula', tx_ + lx_ * c_ - lz_ * s_, tz_ + lx_ * s_ + lz_ * c_, 3, 3, th - 4, ta, CAB, 2.6)
    e.caixa_girada('taula', tx_, tz_, tw * 0.8, td * 0.7, 10, ta, ENG, 1.6, y0=14,
                   cares={'davant': {'ramp': ENG, 'lvl': lambda s, t, P: 2.0 + (1.4 if abs(s - tw * 0.4) < 4 and 3 < t < 7 else 0)}})

    def carta(s, t, P):
        v = 3.8 + (fbm(s / 16, t / 10, 4) - 0.5) * 0.6
        if s < 3 or t < 3 or s > tw - 3 or t > td - 3:
            return 2.2                                             # la vora de fusta
        if abs((s - 10) * 0.4 + (t - 8) - 10) < 0.6 and s > 8:
            return 1.6                                             # la ruta, a llapis
        if fbm(s / 14, t / 14, 9) > 0.62:
            return 2.8                                             # la costa
        return v
    e.caixa_girada('taula', tx_, tz_, tw, td, 4, ta, PL.WOOD, 2.6, y0=th - 4,
                   cares={'dalt': {'ramp': PL.PAPERY, 'lvl': carta}, 'davant': {'ramp': PL.WOOD, 'lvl': 2.8},
                          'esquerra': {'ramp': PL.WOOD, 'lvl': 2.0}, 'dreta': {'ramp': PL.WOOD, 'lvl': 1.6}})
    # el timó i la cadira (els dibuixos plans, drets), amb la seva ombra
    for sid, (px, pz), bx, peu in (('timo', WHEEL, WHEEL_BOX, _peu(WHEEL_BOX, 269, 210)),
                                   ('cadira', CHAIR, CHAIR_BOX, _peu(CHAIR_BOX, 461, 218))):
        e.foscor(f'ombra_{sid}', (px - 22, 0.7, pz + 14), (px + 22, 0.7, pz + 14), (px + 22, 0.7, pz - 16),
                 (px - 22, 0.7, pz - 16), lambda s, t: 0.6 * max(0.0, 1 - ((s - 22) / 22) ** 2 - ((t - 15) / 15) ** 2) * 1.6)
        e.sprite(sid, ins.crop(bx), peu, (px, 0, pz))
    # primer pla: la quaderna i les canonades de l'esquerra, els cables que pengen, i a baix a la dreta una canonada
    # grossa i l'armari de les armilles (es veuen tallats)
    FOSC = [(3, 4, 6), (7, 9, 12), (12, 15, 19), (18, 22, 27), (26, 31, 37), (36, 42, 49)]
    e.caixa('primer_pla', 0, 24, 0, HW, 46, 70, FOSC, 2.4,
            cares={'dreta': {'ramp': FOSC, 'lvl': lambda s, t, P: 2.2 - (1.6 if s < 2 else 0) + (1.0 if s > 20 else 0)
                             + (1.8 if (t % 16) < 2 and 6 < s < 18 else 0)},
                   'davant': {'ramp': FOSC, 'lvl': 1.6}})
    for yy, r, xx in ((184, 8, 16), (170, 5, 30)):                 # canonades arran del sostre, cap a la càmera
        e.tub('primer_pla', (xx, yy, 200), (xx, yy, -40), r, FOSC, 2.2, brides=40)
    for k, xx in enumerate((40, 56, 70)):
        e.cable('primer_pla', [(xx, HW, 34 + k * 6), (xx + 6 + k * 4, 150 - k * 22, 40 + k * 6),
                               (xx + 2, 112 - k * 28, 46 + k * 6)], FOSC, 1.4, gruix=2.2)
    e.tub('primer_pla', (150, 11, 58), (800, 11, 58), 11, FOSC, 3.0)      # la canonada grossa, a terra
    for xx in (240, 420):
        e.caixa('primer_pla', xx - 6, xx + 6, 0, 28, 52, 64, FOSC, 2.4)               # les abraçadores
    e.caixa('primer_pla', 456, 570, 0, 96, 84, 124, FOSC, 2.2,                          # l'armari de les armilles
            cares={'dalt': {'ramp': FOSC, 'lvl': lambda s, t, P: 3.2 - (1.2 if s % 38 < 1.5 else 0)},
                   'esquerra': {'ramp': FOSC, 'lvl': lambda s, t, P: 2.0 - (1.0 if t > 80 else 0)
                                + (1.0 if abs(s - 20) < 1 else 0)},
                   'davant': {'ramp': [(30, 8, 6), (60, 16, 12), (100, 30, 22), (140, 50, 34), (180, 80, 50)],
                              'lvl': lambda s, t, P: 1.2 + (2.0 if 14 < t < 30 and 8 < s < 60 and (s + t) % 9 < 5 else 0)
                              - (0.8 if abs(s - 57) < 1 else 0)}})
    return e


# ─── Composició ────────────────────────────────────────────────────────────

def _textures(dia=False, mar=0, radar=0, terminal=0):
    return {'paret': _paret(dia, mar), 'planxa': _planxa(dia), 'consola': _consola(dia),
            'instruments': _instruments(dia, radar, terminal)}


@functools.lru_cache(maxsize=None)
def _tex_base():
    return _textures()


def _render(estat=frozenset(), tex=None):
    cv = Canvas(light=LIGHT)
    e = escena(cv, tex or _tex_base(), estat)
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


def safata(cv):
    """La safata al replà del muntacàrregues (el dibuix pla, projectat a la paret del fons)."""
    _, e = _base()
    cv.img.alpha_composite(e.capa(_flat(PL.safata), {'paret_fons'}))
    cv.P = cv.img.load()


def guardacostes(cv):
    """Els llums del guardacostes a l'horitzó del tercer vidre (projectats)."""
    _, e = _base()
    cv.img.alpha_composite(e.capa(_flat(PL.guardacostes), {'paret_fons'}))
    cv.P = cv.img.load()


def _sprite_capa(e, sid, img, peu_img, peu):
    """Un fotograma d'un dibuix pla dret (un sprite de l'escena), on aquell sprite és el que es veu."""
    from pixels import nearest
    idx = e.ids.index(sid)
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
            if 0 <= X < W_ and e.amo[Y * W_ + X] == idx and src[x, y][3] >= 128:
                dst[X, Y] = src[x, y]
    return out


def _instrument_capa(e, ins, sid):
    zi = 284
    for s_, bx, fx in (('radar', RADAR_BOX, 200), ('terminal', TERM_BOX, 368)):
        if s_ == sid:
            fy = bx[3] - 1 if sid != 'terminal' else PL.CON_TOP - 1
            return _sprite_capa(e, sid, ins.crop(bx), _peu(bx, fx, fy), (_cx(fx), _con_y(zi), zi))


def _pantalles():
    """Màscara de les dues pantalles (la del radar i la del terminal), on es veuen: els forats del decorat `dia`."""
    _, e = _base()
    m = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    P = m.load()
    cx, cy = PL.RADAR
    for y in range(cy - 17, cy + 18):
        for x in range(cx - 17, cx + 18):
            if math.hypot(x - cx, y - cy) <= 16.5:
                P[x, y] = (255, 255, 255, 255)
    x0, y0, x1, y1 = PL.SCREEN
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            P[x, y] = (255, 255, 255, 255)
    out = _instrument_capa(e, m, 'radar')
    out.alpha_composite(_instrument_capa(e, m, 'terminal'))
    return out


def dia(cv):
    """Decorat `dia` (Escenes 2 i 3): el pont sencer de dia, amb el cel i el mar grisos pels vidres i la claror freda
    que entra. Deixa forats a les pantalles del radar i del terminal (s'hi veuen les animacions)."""
    img, _ = _render(frozenset({'dia'}), _textures(dia=True))
    img = img.copy()
    hole = _pantalles().load()
    P = img.load()
    for Y in range(H):
        for X in range(W):
            o = P[X, Y]
            if hole[X, Y][3]:
                P[X, Y] = (0, 0, 0, 0)
            else:
                P[X, Y] = (int(o[0] * 0.9 + 15), int(o[1] * 0.9 + 16), int(o[2] * 0.9 + 17), 255)
    for Y in range(BOTTOM + 1, H):
        for X in range(W):
            P[X, Y] = (0, 0, 0, 255)
    cv.img.paste(img)
    cv.P = cv.img.load()


EMERG = ((0.5, 168, _wz(53)), (_w(531), 168, ZW - 0.5))  # els llums d'emergència: dalt l'escala i dalt el muntacàrregues


def fosc(cv):
    """El generador parat: tot fosc, només els llums d'emergència vermells i les pantalles amb el SAI."""
    P = cv.P
    lamps = [CAM.projecta(p)[:2] for p in EMERG]
    rad = [147 * CAM.escala(p) for p in EMERG]
    tu, tv, _ = CAM.projecta(TERM_C)
    for Y in range(H):
        for X in range(W):
            a = 165
            r = 0
            for (lx, ly), rr in zip(lamps, rad):
                d = math.hypot(X - lx, (Y - ly) * 1.1)
                if d < rr:
                    f = (1 - d / rr) ** 1.6
                    a -= int(70 * f)
                    r += int(150 * f)
            d = math.hypot(X - tu, Y - tv)
            if d < 50:
                a -= int(80 * (1 - d / 50) ** 1.5)
            a = max(0, min(255, a))
            if a > 0:
                P[X, Y] = (min(255, 4 + r // 3), 2, 8, a)
    for (lx, ly), p in zip(lamps, EMERG):                        # els llums d'emergència
        k = CAM.escala(p)
        hw_, hh = 9 * k, 4 * k
        for Y in range(int(ly - hh), int(ly + hh * 0.8) + 1):
            for X in range(int(lx - hw_), int(lx + hw_) + 1):
                if 0 <= X < W and 0 <= Y < H:
                    P[X, Y] = (40, 40, 46, 255) if Y > ly - hh * 0.6 else (62, 62, 70, 255)
        for Y in range(int(ly - hh * 0.3), int(ly + hh * 0.8) + 1):
            for X in range(int(lx - hw_ * 0.8), int(lx + hw_ * 0.8) + 1):
                if ((X - lx) / (hw_ * 0.8)) ** 2 + ((Y - ly - hh * 0.25) / (hh * 0.6)) ** 2 <= 1:
                    P[X, Y] = (255, 110 if abs(Y - ly) < 1 else 40, 30, 255)


PROPS = {'dia': dia, 'safata': safata, 'guardacostes': guardacostes, 'fosc': fosc}


# ─── Animacions ──────────────────────────────────────────────────────────────

def _frames_mar():
    """El mar pels vidres (i per la porta del pal): les ones que es mouen, projectades a la paret del fons."""
    img0, e = _base()
    out = []
    for f in range(PL.MAR_N):
        img = img0.copy()
        img.alpha_composite(e.capa(_diff(_paret(mar=f), _tex_base()['paret']), {'paret_fons'}))
        out.append(_diff(img, img0))
    return out


def _frames_instrument(sid, n, key):
    img0, e = _base()
    ins0 = _tex_base()['instruments']
    out = []
    for f in range(n):
        ins = _instruments(**{key: f})
        img = img0.copy()
        img.alpha_composite(_instrument_capa(e, _diff(ins, ins0), sid))
        out.append(_diff(img, img0))
    return out


ANIMS = {'radar': {'frames': lambda: _frames_instrument('radar', PL.RADAR_N, 'radar'), 'frameDuration': 220},
         'terminal': {'frames': lambda: _frames_instrument('terminal', 2, 'terminal'), 'frameDuration': 530},
         'mar': {'frames': _frames_mar, 'frameDuration': 260}}


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


# Capes del davant: el primer pla (sempre davant), el timó, la cadira i la taula de cartes (qui hi passa per
# darrere, hi queda darrere).
FRONT = [
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20, 'variants': ('dia', 'fosc')},
    {'id': 'davant_timo', 'mask': _amo({'timo'}), 'baseline': _p(WHEEL[0], WHEEL[1] - 4)[1], 'zIndex': 20, 'variants': ('dia', 'fosc')},
    {'id': 'davant_cadira', 'mask': _amo({'cadira'}), 'baseline': _p(CHAIR[0], CHAIR[1] - 6)[1], 'zIndex': 20, 'variants': ('dia', 'fosc')},
    {'id': 'davant_taula', 'mask': _amo({'taula'}), 'baseline': _p(TAULA[0], TAULA[1] - 14)[1], 'zIndex': 20, 'variants': ('dia', 'fosc')},
]


# ─── Geometria (coordenades de sala, projectades) ────────────────────────────

def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


# El terra on es camina (al món): davant la consola, fins a l'escala i la porta de la ràdio a l'esquerra i, a la
# dreta, fins al muntacàrregues i la porta del pal; lluny del primer pla.
WALK_MON = [(14, 100), (14, 250), (CON[0] - 4, 252), (CON[0] - 4, 254), (CON[1] + 8, 254), (CON[1] + 8, 284),
            (505, 284), (520, 236), (500, 170), (440, 130), (440, 90), (200, 84)]
V_MAX = 240                                        # més a prop, el personatge passaria d'1,2: és per al primer pla


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


_WALK = _talla([_p(x, z) for x, z in WALK_MON], V_MAX)


def _forat(x, z, rx, rz):
    return [_p(x + dx, z + dz) for dx, dz in ((-rx, -rz), (rx, -rz), (rx, rz), (-rx, rz))]


def _forat_taula():
    tx_, tz_, tw, td, th, ta = TAULA
    c_, s_ = math.cos(ta), math.sin(ta)
    a, b = tw / 2 + 3, td / 2 + 3
    return [_p(tx_ + lx * c_ - lz * s_, tz_ + lx * s_ + lz * c_) for lx, lz in ((-a, -b), (a, -b), (a, b), (-a, b))]


_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)


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


def _sprite_rect(bx, fx, fy, peu):
    k = CAM.escala(peu)
    u, v, _ = CAM.projecta(peu)
    return (round(u - (fx - bx[0]) * k), round(v - (fy - bx[1]) * k), round(u + (bx[2] - fx) * k),
            round(v + (bx[3] - fy) * k))


_ZI = 284
_TERM = _sprite_rect(TERM_BOX, 368, PL.CON_TOP - 1, (_cx(368), _con_y(_ZI), _ZI))
_SAI = _rect_mon((_cx(336), _y(149), CON[2]), (_cx(395), _y(168), CON[2]))
_PRINT = _sprite_rect(PRINT_BOX, 436, PRINT_BOX[3] - 1, (_cx(436), _con_y(_ZI), _ZI))
_WHEEL = _sprite_rect(WHEEL_BOX, 269, 210, (WHEEL[0], 0, WHEEL[1]))


def _wall(fx0, fy0, fx1, fy1):
    return _rect_mon((_w(fx0), _y(fy0), ZW), (_w(fx1), _y(fy1), ZW))


GEOMETRIA = {
    'things': {
        'escala': {'rect': _rect_mon((0, _y(85), _wz(8)), (0, 0, _wz(72))), 'walk': _p(26, _wz(40))},
        'porta_radio': {'rect': _rect_mon((0, _y(83), _wz(85)), (0, 0, _wz(144))), 'walk': _p(26, _wz(114))},
        'vidre': {'rect': _wall(*PL.WIN), 'walk': _p(_w(320), 246)},
        'timo': {'rect': _WHEEL, 'walk': _p(WHEEL[0] + 4, WHEEL[1] - 26)},
        'terminal': {'rect': (min(_TERM[0], _SAI[0]), _TERM[1], max(_TERM[2], _SAI[2]), _SAI[3]),
                     'walk': _p(_cx(368), 246)},
        'impressora': {'rect': _PRINT, 'walk': _p(_cx(436), 246)},
        'munta': {'rect': _wall(496, 80, 552, 147), 'walk': _p(_w(524), 276)},
        'safata': {'rect': _wall(501, 128, 547, 143), 'walk': _p(_w(524), 276)},
        'boca': {'rect': _wall(557, 104, 579, 139), 'walk': _p(_w(568), 276)},
        'escala_pal': {'rect': _wall(587, 77, 637, 200), 'walk': _p(_w(614), 276)},
    },
    'spawns': {'iri': _p(300, 170), 'vet': _p(110, 176), 'capitana': _p(WHEEL[0] + 30, 222)},
    'walkable': _WALK,
    'forats': [_forat(WHEEL[0], WHEEL[1], 12, 8), _forat(CHAIR[0], CHAIR[1], 12, 8), _forat_taula()],
    'floorSquash': 0.45,                           # (la càmera, picada, a ≈2 m: el terra es veu aixafat)
    # L'ombra de contacte: el llum de sostre (el punt del terra just a sota); curta, és llum de dalt.
    'characterShadow': {'enabled': True, 'color': '#06080e', 'alpha': 0.42, 'squash': 0.42, 'core': 0.6,
                        'light': {'x': _p(LAMP[0], LAMP[1])[0], 'y': _p(LAMP[0], LAMP[1])[1], 'stretch': 0.5,
                                  'reach': 140}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    # La llum de la sala sobre els personatges (les de _llums, a la pantalla): penombra freda; el llum de sostre,
    # vermellós; el verd de les pantalles a la consola; la llum càlida que puja de l'escala, i la lluna pels vidres.
    'characterLights': {
        'ambient': '#6e7690',
        'lights': [
            _llum_pj((LAMP[0], 196, LAMP[1]), 230, '#ffb898', 0.5),                       # el llum de sostre
            _llum_pj(TERM_C, 110, '#8cf0a0', 0.45),                                       # el terminal
            _llum_pj(RADAR_C, 100, '#78e68c', 0.4),                                       # el radar
            _llum_pj(STAIRS_C, 150, '#ffc070', 0.7),                                      # l'escala
            _llum_pj((WIN_C[0] - 60, 140, ZW + 20), 300, '#a8bce0', 0.3),                 # la lluna, pels vidres
            _llum_pj((_w(610), 110, ZW + 10), 110, '#ffd8a0', 0.3),                       # el llum del pal
            # de dia (el decorat `dia`): la claror grisa dels vidres
            _llum_pj(WIN_C, 420, '#e0e8f0', 0.6, power=1.0, whenPropVisible='dia'),
            # el generador parat (`fosc`): els llums d'emergència, vermells
            *[_llum_pj(p, 200, '#ff4030', 0.5, whenPropVisible='fosc') for p in EMERG],
        ],
    },
}
