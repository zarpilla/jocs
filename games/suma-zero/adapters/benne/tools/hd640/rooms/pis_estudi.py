"""
L'estudi de l'Iri (Escena 1), de nit. EN 3D (hd640/tres_d.py), a 1×.

Una càmera alta que mira de biaix la cantonada del fons a l'esquerra (com la referència de l'habitació 404,
docs/referencies/sala-habitacio-404.png):
  - a la paret de l'esquerra, en escorç, la **finestra** amb la persiana mig abaixada: el neó magenta del carrer
    hi entra i pinta franges en diagonal pel terra;
  - a la paret del fons, el **pòster** del gat 404, el **passaplats** de la cuina i la **presa de fibra**;
  - el **matalàs** a terra, separat de la paret i girat, amb l'edredó i el coixí; les **pizzes** apilades al costat;
  - l'**escriptori** amb volum (la tapa, les potes, la torre a sota), els tres **monitors** que fan la llum cian, i
    la cadira de malla al davant (s'hi passa per darrere); el **moble del router**, una mica girat;
  - primer pla: caixes de mudança en silueta a baix a l'esquerra i cables que pengen del sostre.

Tot el detall ve del dibuix pla de sempre (pis_estudi_pla_comu.py), projectat; els decorats (la caixa, els cables
que es connecten, el passaplats obert) es dibuixen en 3D i en surt la diferència. Damunt de tot, la llum de Suma
Zero (hd640/llum.py): les pantalles, el neó, el bloom i la corba de to.

El món: x a la dreta (0 = la paret de la finestra), y amunt (0 = el terra), z cap al fons (300 = la paret del fons);
1 unitat = 1 píxel de sala a la distància on un personatge fa ≈111 px (escala 1).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from hd640 import llum
from hd.pix import Canvas, Light, W, H, hr
from hd.rooms.comu import _diff, obox, PLASTIC, SCREEN, SHEET, GRAYC, YEL, CARD, RED
from hd.rooms.exterior import fbm
from hd640.rooms import pis_estudi_pla_comu as PL
from hd640.rooms.pis_estudi_pla_comu import (BRICK, MORTAR, FLOORB, DESKB, STEELB, CYANL, FABRICB, WARMB, MAGENTA,
                                             YELC, BLUEC)
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
ZW = 300                                           # la paret del fons
HW = 200                                           # l'alçada de les parets (el dibuix pla fa 200 fins al terra)
XL = 180                                           # al dibuix pla, la cantonada: a l'esquerra, la paret de la finestra
XR = 760                                           # on s'acaba la paret del fons (fora de la pantalla)
DESK = (96, 316, 236, 292, 48)                     # l'escriptori: x0, x1, z del davant, z del darrere, alçada
TOWER = (112, 132, 246, 284, 44)                    # la torre, sota la taula: x0, x1, z0, z1, alçada
CHAIR = (214, 214)                                 # els peus de la cadira (x, z)
CAB = (352, 0.22, 46, 34, 44)                      # el moble del router: x del centre, gir, ample, fons, alçada
CAB_Z = ZW - 2 - CAB[3] / 2
MAT = (78, 196, 66, 126, 12, 0.32)                 # el matalàs: x, z del centre, ample, llarg, alt, gir
PIZZA = (58, 116)                                  # la pila de capses de pizza (x, z)
BOX = (346, 152, 40, 30, 26, -0.32)                # la caixa del router (decorat): x, z, ample, fons, alt, gir
SHELF = (486, 546, 268, 298, 138)                  # la prestatgeria, a la dreta del passaplats: x0, x1, z0, z1, alt
BIN = (530, 236)                                   # la paperera
JAMB = (303, 309, -160, -152)                      # el brancal de la porta, en primer pla: x0, x1, z0, z1
NIGHT = (430, 514, -80, -40, 96)                   # la calaixera, en primer pla: x0, x1, z0, z1, alçada
CLOCK = (16, 8, 8)                                 # el despertador, damunt: ample, alt, fons

_FONT3 = {'0': ('111', '101', '101', '101', '111'), '1': ('010', '110', '010', '010', '111'),
          '2': ('111', '001', '111', '100', '111'), '3': ('111', '001', '111', '001', '111')}


def _digits(txt, w, h):
    """La cara del despertador: dígits de 3×5 encesos (els dos punts al mig) sobre negre; (s, t) des de dalt a
    l'esquerra, en unitats del món."""
    cols = 4 * len(txt) + 1                        # 3 per dígit + 1 d'espai, i els dos punts
    def lvl(s, t, P):
        c, r = int(s / w * (cols + 2)) - 1, int(t / h * 7) - 1
        if not (0 <= r < 5 and 0 <= c < cols):
            return 0.2
        if c == 8 and r in (1, 3):                # els dos punts, entre el segon i el tercer dígit
            return 4.6
        k = c - (1 if c >= 8 else 0)
        d, x = divmod(k, 4)
        if d >= len(txt) or x == 3:
            return 0.2
        return 4.6 if _FONT3[txt[d]][r][x] == '1' else 0.6
    return lvl


def _w(fx):
    """Una x del dibuix pla de la paret del fons → la x del món."""
    return fx - XL


def _wz(fx):
    """Una x del dibuix pla de la paret de la finestra → la z del món."""
    return ZW - XL + fx


def _y(fy):
    """Una y del dibuix pla (el terra, a 200) → l'alçada del món."""
    return HW - fy


HATCH = (_w(PL.HATCH[0]), _w(PL.HATCH[2]), _y(PL.HATCH[3]), _y(PL.HATCH[1]))     # x0, x1, y0, y1
WIN = (_wz(PL.WINDOW[0]), _wz(PL.WINDOW[2]), _y(PL.WINDOW[3]), _y(PL.WINDOW[1]))  # z0, z1, y0, y1
SOCKET = (_w(560), _w(573), _y(168), _y(149))                                     # la presa de fibra
PLUG = (_w(614), _w(624), _y(200), _y(186))                                       # l'endoll de terra

CAM = Camera(pos=(420, 200, -240), yaw=-0.36, pitch=0.2, f=470, centre=(320, 66))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)  # (la llum és la del món: la de l'Escena)
MON_C = ((DESK[0] + DESK[1]) / 2, DESK[4] + 34, ZW - 14)    # el centre dels monitors
LLUMS = [Llum(MON_C, 300, 2.0, power=1.4),                 # les pantalles
         Llum((10, 110, (WIN[0] + WIN[1]) / 2), 250, 1.2, power=1.5),   # la finestra (el carrer)
         Llum((96, 20, 230), 40, 0.8, power=2.0)]           # la torre


def _llums(obert=False):
    if not obert:
        return LLUMS
    return LLUMS + [Llum(((HATCH[0] + HATCH[1]) / 2, (HATCH[2] + HATCH[3]) / 2, ZW + 30), 220, 2.4, power=1.2)]


# ─── Les textures: el dibuix pla de sempre ───────────────────────────────────

def _presa(cv):
    """La presa de fibra i l'endoll de terra (al pla, eren dins el moble del router i els cables)."""
    obox(cv, 560, 149, 573, 168, SHEET, 2.4)
    cv.rect(564, 156, 569, 161, PLASTIC, 1.0)
    cv.flat(566, 152, (60, 160, 80))
    obox(cv, 614, 186, 624, 200, SHEET, 2.4)
    cv.flat(617, 192, (20, 16, 14))
    cv.flat(621, 192, (20, 16, 14))


def _paret(rain=0, neon=True, obert=False):
    """Les dues parets planes, de cara: maó, la finestra, el pòster, el passaplats i la presa."""
    cv = Canvas(light=PL.LIGHT)
    PL.wall(cv)
    PL.window(cv, rain=rain, neon=neon)
    PL.poster(cv)
    PL.hatch(cv)
    if obert:
        PL.passaplats_obert(cv)
    _presa(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _paret_base():
    return _paret()


@functools.lru_cache(maxsize=None)
def _paret_oberta():
    return _paret(obert=True)


def _escriptori(frame=0, disc=False, router=False):
    """Els monitors, la torre i el router, dibuixats plans sobre transparent (en surten els retalls)."""
    cv = Canvas(light=PL.LIGHT, transparent=True)
    PL.monitors(cv, frame)
    obox(cv, 315, 131, 325, 141, YEL, 3.0)                       # el pòsit a la vora de la pantalla
    for j in range(3):
        cv.hline(317, 317 + 4 + (j * 3) % 4, 134 + j * 2, [(60, 20, 20), (120, 30, 30)], 1.4, lit=0)
    # la torre (el davant), amb el llum del disc dur
    obox(cv, 285, 171, 315, 221, PLASTIC, 2.0)
    cv.vline(309, 176, 213, CYANL, 4.0, lit=0)
    cv.vline(310, 176, 213, CYANL, 2.4, lit=0)
    for y in range(195, 214, 3):
        cv.hline(290, 303, y, PLASTIC, 0.6)
    cv.rect(289, 176, 291, 177, PLASTIC, 4.0)
    if disc:
        cv.flat(290, 180, (255, 170, 60))
        cv.flat(291, 180, (200, 110, 30))
    # el router, amb les antenes
    obox(cv, 501, 152, 541, 167, PLASTIC, 1.8, top=1.2)
    cv.line(507, 152, 503, 136, PLASTIC, 2.2)
    cv.line(536, 152, 540, 136, PLASTIC, 2.2)
    cv.flat(503, 135, PLASTIC[3])
    cv.flat(540, 135, PLASTIC[3])
    for x in PL.PORTS:
        cv.rect(x, 160, x + 4, 164, PLASTIC, 0.4)
        on = (120, 255, 150) if router else (90, 30, 30)
        cv.flat(x + 1, 156, on)
        cv.flat(x + 2, 156, on if router else (70, 24, 24))
    for x in range(533, 539, 2):
        cv.vline(x, 157, 164, PLASTIC, 0.6)
    # el moble del router (el davant): dos calaixos d'acer
    obox(cv, 496, 168, 547, 213, STEELB, 2.0)
    cv.hline(497, 546, 189, STEELB, 0.6)
    cv.hline(497, 546, 190, STEELB, 3.0)
    cv.rect(515, 177, 528, 178, STEELB, 3.4)
    cv.rect(515, 199, 528, 200, STEELB, 3.4)
    for y in (180, 202):
        cv.rect(519, y, 524, y + 3, SHEET, 3.0)
    # la cadira de malla, de cara
    cv.disc(400, 203, 27, 7, PLASTIC, lambda nx, ny: 1.8 - ny * 0.6)
    cv.rect(396, 209, 404, 227, STEELB, 2.0)
    cv.vline(397, 209, 227, STEELB, 3.0)
    for dx in (-19, -8, 8, 19):
        cv.line(400, 227, 400 + dx, 235, STEELB, 2.0)
        cv.disc(400 + dx, 236, 2, 1.5, PLASTIC, 1.4)
    back = [(379, 139), (421, 139), (425, 195), (375, 195)]
    cv.poly(back, PLASTIC, lambda x, y: 1.6 + (0.6 if (x + y) % 3 == 0 else 0) + (0.5 if y < 143 else 0))
    cv.rect(381, 193, 419, 196, PLASTIC, 2.2)
    PL.outline(cv, 375, 139, 425, 196, PLASTIC)
    for (ax, bx) in ((372, 377), (423, 428)):
        cv.rect(ax, 176, bx, 178, PLASTIC, 2.4)
    return cv.img


MON_BOX = (268, 77, 487, 156)                      # els monitors, al dibuix pla (amb els peus)
TOWER_BOX = (285, 171, 316, 222)
ROUTER_BOX = (499, 133, 545, 168)
CAB_BOX = (496, 168, 548, 214)
CHAIR_BOX = (368, 137, 432, 239)


@functools.lru_cache(maxsize=None)
def _escriptori_base():
    return _escriptori()


# ─── Les superfícies ────────────────────────────────────────────────────────

def _mao(lvl0, seed=3):
    """Maó pintat de lila en coordenades del món (s, t des del cantó de dalt): on el dibuix pla no arriba."""
    def L(s, t, P):
        row = int(t // 9)
        off = 12 if row % 2 else 0
        bx = int((s + off) // 24)
        if t % 9 > 8 or (s + off) % 24 < 1:
            return lvl0 - 0.6
        v = lvl0 + 0.4 + (hr(bx, row, seed) - 0.5) * 0.8
        if t % 9 < 1:
            v += 0.35
        if t > HW - 7:
            v = 2.4 if t > HW - 6 else 3.4                     # el sòcol
        return v
    return L


def _terra(s, t, P):
    """La tarima de laminat, en coordenades del món: llistons de 40 que fugen cap al fons, juntes de testa."""
    x, z = P[0], P[2]
    plank = math.floor(x / 26)
    v = 2.4 + (hr(plank, 3) - 0.5) * 0.6 + (fbm(x / 60, z / 30, 4) - 0.5) * 0.5
    if x % 26 < 1.0:
        return 0.8
    if int(z + hr(plank, 7) * 120) % 120 < 1.0:
        return 1.2
    return v


def _llum_neo(x, z, y=0.0):
    """Quanta llum del neó (0..1) arriba a un punt del món: la línia que va de la finestra cap avall, cap a la dreta
    i una mica cap a la càmera; la persiana (la meitat de dalt de la finestra) la talla en franges."""
    t = x / 1.0
    yw, zw = y + 0.78 * t, z + 0.32 * t
    z0, z1, y0, y1 = WIN
    if not (z0 + 5 < zw < z1 - 5 and y0 + 5 < yw < y1 - 4):
        return 0.0
    fy = HW - yw                                       # la y del dibuix pla, a la finestra
    if fy < 98 and int(fy - PL.WINDOW[1] - 3) % 5 < 3:
        return 0.0                                     # un llistó de la persiana
    if abs(zw - (z0 + z1) / 2) < 2:
        return 0.0                                     # el muntant del mig
    return max(0.0, 1 - x / 330) * 0.42


def _dins(x, z, poly):
    """Si el punt (x, z) és dins el polígon convex `poly` de punts del món (x, y, z)."""
    sg = 0
    for (ax, _, az), (bx, _, bz) in zip(poly, poly[1:] + poly[:1]):
        c = (bx - ax) * (z - az) - (bz - az) * (x - ax)
        if c and sg and (c > 0) != (sg > 0):
            return False
        sg = sg or c
    return True


def escena(cv, tex, estat=frozenset()):
    """Tota la sala, de lluny a prop. `estat`: els decorats que hi són ('caixa', 'router', 'fibra', 'xarxa',
    'alimentacio', 'obert'). → l'Escena (qui ha pintat què)."""
    e = Escena(cv, CAM, _llums('obert' in estat), ambient=-0.4)
    zn = CAM.pos[2] + 60
    paret, esc = tex['paret'], tex['escriptori']
    # el sostre, fosc
    e.quad('sostre', (0, HW, zn), (XR, HW, zn), (XR, HW, ZW), (0, HW, ZW), ramp=MORTAR, lvl=0.8, dues_cares=True)
    # la paret de la finestra (x = 0): de prop, maó; cap a la cantonada, el dibuix pla (x 0..180)
    e.quad('paret_esq_prop', (0, HW, zn), (0, HW, ZW - XL), (0, 0, ZW - XL), (0, 0, zn), ramp=BRICK, lvl=_mao(2.6))
    e.quad('paret_esq', (0, HW, ZW - XL), (0, HW, ZW), (0, 0, ZW), (0, 0, ZW - XL), tex=(paret, (0, 0, XL, HW)))
    # la paret del fons (z = 300): el dibuix pla (x 180..640) i, a la dreta, més maó
    e.quad('paret_fons', (0, HW, ZW), (W - XL, HW, ZW), (W - XL, 0, ZW), (0, 0, ZW), tex=(paret, (XL, 0, W, HW)))
    e.quad('paret_fons_dreta', (W - XL, HW, ZW), (XR, HW, ZW), (XR, 0, ZW), (W - XL, 0, ZW), ramp=BRICK,
           lvl=_mao(2.6, seed=5))
    # el passaplats obert: la llum càlida de la cuina s'escampa per la paret
    if 'obert' in estat:
        hx = (HATCH[0] + HATCH[1]) / 2
        e.claror((hx - 120, HW, ZW - 0.5), (hx + 120, HW, ZW - 0.5), (hx + 120, 0, ZW - 0.5), (hx - 120, 0, ZW - 0.5),
                 (255, 150, 70), lambda s, t: 0.32 * max(0.0, 1 - math.hypot(s - 120, (t - (HW - HATCH[3] + 28)) * 1.3) / 120))
    # el terra
    e.quad('terra', (0, 0, ZW), (XR, 0, ZW), (XR, 0, zn), (0, 0, zn), ramp=FLOORB, lvl=_terra)
    # l'estora gastada davant la taula, una mica girada (els fils, més grossos a prop)
    e.quad('estora', (176, 0.3, 214), (330, 0.3, 200), (318, 0.3, 112), (160, 0.3, 124), ramp=FABRICB,
           lvl=lambda s, t, P: 2.6 + (0.6 if int(t) % 6 < 3 else 0) - (1.2 if s < 3 or s > 152 or t < 3 or t > 86 else 0)
           + (fbm(s / 20, t / 12, 3) - 0.5) * 1.0)
    # la llum de les pantalles al terra, davant la taula, i el neó en franges que entra per la finestra
    e.claror((DESK[0] - 60, 0.3, ZW), (DESK[1] + 60, 0.3, ZW), (DESK[1] + 60, 0.3, DESK[2] - 150),
             (DESK[0] - 60, 0.3, DESK[2] - 150), (60, 190, 180),
             lambda s, t: 0.22 * max(0.0, 1 - abs(s - 175) / 175) * max(0.0, 1 - t / 210))
    e.claror((0, 0.4, ZW), (360, 0.4, ZW), (360, 0.4, 0), (0, 0.4, 0), (220, 80, 200),
             lambda s, t: _llum_neo(s, ZW - t))
    if 'obert' in estat:
        hx = (HATCH[0] + HATCH[1]) / 2
        e.claror((hx - 90, 0.5, ZW), (hx + 90, 0.5, ZW), (hx + 120, 0.5, ZW - 150), (hx - 120, 0.5, ZW - 150),
                 (255, 150, 70), lambda s, t: 0.28 * max(0.0, 1 - abs(s - 90) / 100) * max(0.0, 1 - t / 150))
    # la foscor dels racons
    e.foscor('racons', (0, 0.5, ZW), (XR, 0.5, ZW), (XR, 0.5, zn), (0, 0.5, zn),
             lambda s, t: max(0.6 * max(0.0, 1 - t / 30), 0.5 * max(0.0, 1 - s / 26)))
    e.foscor('cantonada', (0, HW, ZW - 0.5), (60, HW, ZW - 0.5), (60, 0, ZW - 0.5), (0, 0, ZW - 0.5),
             lambda s, t: 0.55 * max(0.0, 1 - s / 60))
    e.foscor('cantonada2', (0.5, HW, ZW - 60), (0.5, HW, ZW), (0.5, 0, ZW), (0.5, 0, ZW - 60),
             lambda s, t: 0.55 * max(0.0, 1 - (60 - s) / 60))
    e.foscor('sostre_fosc', (0, HW - 0.5, ZW - 0.6), (XR, HW - 0.5, ZW - 0.6), (XR, 0, ZW - 0.6), (0, 0, ZW - 0.6),
             lambda s, t: 0.45 * max(0.0, 1 - t / 60))
    # els cables pel terra: de la torre cap a la paret, i un altre que travessa
    for ramp, lv, pts in (
            ([(4, 4, 8), (20, 20, 28), (40, 40, 52), (70, 70, 84)], 2.0,
             [(100, 0.8, 250), (130, 0.8, 214), (220, 0.8, 222), (290, 0.8, 250), (318, 0.8, 286)]),
            (BLUEC, 1.8, [(90, 0.8, 246), (70, 0.8, 214), (110, 0.8, 170), (40, 0.8, 150), (8, 0.8, 140)])):
        e.cable('cables', pts, ramp, lv, gruix=2.2)
    # el matalàs, girat: el costat encoixinat, l'edredó (amb plecs i el llibre) i el coixí
    mx, mz, mw, ml, mh, ma = MAT
    e.foscor('ombra_matalas', (mx - mw, 0.6, mz + ml * 0.7), (mx + mw, 0.6, mz + ml * 0.7),
             (mx + mw, 0.6, mz - ml * 0.7), (mx - mw, 0.6, mz - ml * 0.7),
             lambda s, t: 0.55 * max(0.0, 1 - ((s - mw) / mw) ** 2 - ((t - ml * 0.7) / (ml * 0.7)) ** 2) * 1.4)

    def edredo(s, t, P):
        v = 3.2 + 0.8 * math.sin(s / 7 + t / 11) + (fbm(s / 14, t / 9, 6) - 0.5) * 0.8
        if t < 30:
            v = 3.8 + (fbm(s / 8, t / 6, 2) - 0.5) * 0.6                # el llençol, girat
        if abs(s - 40) < 7 and abs(t - 74) < 5:
            return 1.6 + (1.2 if abs(s - 40) < 0.8 else 0)              # el llibre, de bocaterrosa
        return v
    e.caixa_girada('matalas', mx, mz, mw, ml, mh, ma, SHEET, 1.4,
                   cares={'dalt': {'ramp': FABRICB, 'lvl': edredo},
                          'davant': {'ramp': SHEET, 'lvl': lambda s, t, P: 1.2 - (0.6 if int(s) % 6 == 0 else 0)},
                          'dreta': {'ramp': SHEET, 'lvl': lambda s, t, P: 0.9 - (0.5 if int(s) % 6 == 0 else 0)}})
    e.caixa_girada('matalas', mx - 2, mz + ml / 2 - 18, mw - 16, 20, 7, ma, SHEET, 2.6, y0=mh,
                   cares={'dalt': {'ramp': SHEET, 'lvl': lambda s, t, P: 3.0 - abs(t - 10) * 0.08}})
    e.quad('llibre', *[(mx - 6 + dx, mh + 0.4, mz - 4 + dz) for dx, dz in ((0, 6), (12, 6), (12, -2), (0, -2))],
           ramp=RED, lvl=lambda s, t, P: 1.8 - (1.0 if abs(s - 6) < 0.8 else 0))
    c_, s_ = math.cos(ma), math.sin(ma)
    tops = [(mx + lx * c_ - lz * s_, mh + 0.6, mz + lx * s_ + lz * c_)
            for lx, lz in ((-mw / 2, ml / 2), (mw / 2, ml / 2), (mw / 2, -ml / 2), (-mw / 2, -ml / 2))]
    e.claror((0, mh + 0.6, ZW), (200, mh + 0.6, ZW), (200, mh + 0.6, 0), (0, mh + 0.6, 0), (220, 80, 200),
             lambda s, t: _llum_neo(s, ZW - t, mh) if _dins(s, ZW - t, tops) else 0.0)
    # les capses de pizza, apilades i cadascuna una mica girada
    px_, pz_ = PIZZA
    e.foscor('ombra_pizzes', (px_ - 28, 0.6, pz_ + 26), (px_ + 30, 0.6, pz_ + 26), (px_ + 30, 0.6, pz_ - 26),
             (px_ - 28, 0.6, pz_ - 26), lambda s, t: 0.55 * max(0.0, 1 - ((s - 29) / 29) ** 2 - ((t - 26) / 26) ** 2) * 1.5)
    for i, (dx, dz, a) in enumerate(((0, 0, 0.1), (2, -2, 0.3), (-2, 1, -0.05), (1, 0, 0.42))):
        e.caixa_girada('pizzes', px_ + dx, pz_ + dz, 34, 34, 4, a, CARD, 2.0 - (i % 2) * 0.3, y0=i * 4,
                       cares={'dalt': {'ramp': CARD, 'lvl': (lambda s, t, P: 3.0 - (1.2 if abs(s - 17) < 4 and abs(t - 17) < 2
                                                                                  else 0)) if i == 3 else 3.0},
                              'davant': {'ramp': CARD, 'lvl': lambda s, t, P: 1.8 - (0.8 if t > 3 else 0)}})
    # l'escriptori: la tapa, les potes i la barra de sota; la torre, a sota; i les coses de damunt
    x0, x1, zf, zb, dh = DESK
    e.foscor('ombra_taula', (x0 - 4, 0.6, zb), (x1 + 6, 0.6, zb), (x1 + 6, 0.6, zf - 16), (x0 - 4, 0.6, zf - 16),
             lambda s, t: 0.5 * min(1.0, (zb - zf + 16 - t) / 14) if t > 0 else 0)
    for lx in (x0 + 4, x1 - 6):
        for lz in (zf + 3, zb - 3):
            e.caixa('taula', lx - 1.5, lx + 1.5, 0, dh - 3, lz - 1.5, lz + 1.5, STEELB, 3.0)
    e.caixa('taula', x0 + 4, x1 - 4, 12, 15, zb - 4, zb - 2, STEELB, 2.4)
    tx0, tx1, tz0, tz1, th = TOWER
    e.caixa('torre', tx0, tx1, 0, th, tz0, tz1, PLASTIC, 1.6,
            cares={'davant': {'tex': (esc, TOWER_BOX)}, 'dalt': {'ramp': PLASTIC, 'lvl': 2.4},
                   'dreta': {'ramp': PLASTIC, 'lvl': lambda s, t, P: 1.4 - (0.6 if int(t) % 4 == 0 and t > 20 else 0)}})
    e.caixa('taula', x0, x1, dh - 3, dh, zf, zb, DESKB, 2.4,
            cares={'dalt': {'ramp': DESKB, 'lvl': lambda s, t, P: 3.2 + (fbm(s / 40, t / 10, 8) - 0.5) * 0.5},
                   'davant': {'ramp': DESKB, 'lvl': 1.6}})
    # els monitors (el dibuix pla, dret), arran de la paret
    mid = (x0 + x1) / 2
    e.sprite('monitors', esc.crop(MON_BOX), ((MON_BOX[2] - MON_BOX[0]) / 2, MON_BOX[3] - MON_BOX[1] - 1),
             (mid, dh, zb - 12))
    # el teclat retroil·luminat, el ratolí, les llaunes, la tassa i el portàtil tancat, damunt la tapa
    kz = zf + 14
    e.caixa('teclat', mid - 26, mid + 22, dh, dh + 2, kz - 7, kz + 7, PLASTIC, 2.0,
            cares={'dalt': {'ramp': CYANL, 'lvl': lambda s, t, P: 2.6 if int(s) % 4 < 2 and int(t) % 4 < 2 else 0.8}})
    e.caixa('teclat', mid + 30, mid + 35, dh, dh + 2, kz - 3, kz + 4, PLASTIC, 2.2)
    for cx in (x0 + 22, x0 + 30):
        e.caixa('llaunes', cx - 2.5, cx + 2.5, dh, dh + 13, zb - 30, zb - 25, GRAYC, 2.6,
                cares={'davant': {'ramp': [(10, 40, 20), (30, 120, 50), (90, 220, 100)],
                                  'lvl': lambda s, t, P: 1.6 if 3 < t < 8 else 2.2}})
    e.caixa('tassa', x0 + 44, x0 + 51, dh, dh + 9, zf + 10, zf + 17, RED, 2.2, cares={'dalt': {'ramp': [(20, 10, 6), (40, 22, 12)], 'lvl': 1.0}})
    e.caixa_girada('portatil', x1 - 26, zf + 24, 30, 22, 2.5, -0.25, PLASTIC, 1.8, y0=dh,
                   cares={'dalt': {'ramp': PLASTIC, 'lvl': lambda s, t, P: 2.4 + (1.6 if abs(s - 15) < 4 and abs(t - 11) < 2 else 0)}})
    # el moble del router, una mica girat, amb el router damunt
    cx_, ang, cw, cd, ch = CAB
    e.foscor('ombra_moble', (cx_ - 34, 0.6, CAB_Z + 22), (cx_ + 34, 0.6, CAB_Z + 22), (cx_ + 34, 0.6, CAB_Z - 30),
             (cx_ - 34, 0.6, CAB_Z - 30), lambda s, t: 0.5 * max(0.0, 1 - ((s - 34) / 34) ** 2 - ((t - 30) / 26) ** 2) * 1.4)
    e.caixa_girada('moble', cx_, CAB_Z, cw, cd, ch, ang, STEELB, 2.0,
                   cares={'davant': {'tex': (esc, CAB_BOX)}, 'dalt': {'ramp': STEELB, 'lvl': 3.4},
                          'esquerra': {'ramp': STEELB, 'lvl': 1.4}, 'dreta': {'ramp': STEELB, 'lvl': 1.2}})
    e.sprite('router', esc.crop(ROUTER_BOX), ((ROUTER_BOX[2] - ROUTER_BOX[0]) / 2, ROUTER_BOX[3] - ROUTER_BOX[1] - 1),
             (cx_, ch, CAB_Z))
    # els cables que es connecten (decorats)
    rp = (cx_ - 6, ch + 6, CAB_Z - 6)                                      # els ports del router
    if 'fibra' in estat:
        e.cable('fibra', [((SOCKET[0] + SOCKET[1]) / 2, SOCKET[2] + 2, ZW - 1), (SOCKET[0] + 6, SOCKET[2] - 6, ZW - 4),
                          (cx_ + 18, ch + 6, CAB_Z - 4), (cx_ + 12, ch + 5, CAB_Z - 8)], YELC, 2.2, gruix=1.6)
    else:
        e.cable('fibra', [((SOCKET[0] + SOCKET[1]) / 2, SOCKET[2], ZW - 1), ((SOCKET[0] + SOCKET[1]) / 2 + 4, 14, ZW - 3),
                          (SOCKET[0] - 2, 0.8, ZW - 12), (SOCKET[0] - 14, 0.8, ZW - 10)], YELC, 1.6, gruix=1.6)
    if 'xarxa' in estat:
        e.cable('xarxa', [rp, (cx_ - 20, 20, CAB_Z - 18), (cx_ - 24, 0.8, CAB_Z - 30), (230, 0.8, 228),
                          (130, 0.8, 238), (tx1, 10, tz0 + 6)], BLUEC, 2.2, gruix=1.8)
    if 'alimentacio' in estat:
        e.cable('alimentacio', [(cx_ + 6, ch + 5, CAB_Z - 6), (cx_ + 22, 16, CAB_Z - 10), (cx_ + 30, 0.8, CAB_Z - 20),
                                (PLUG[0] - 30, 0.8, ZW - 24), (PLUG[0] - 6, 0.8, ZW - 14)],
                [(4, 4, 8), (24, 24, 30), (50, 50, 60), (90, 90, 100)], 2.0, gruix=1.8)
        e.caixa('alimentacio', PLUG[0] - 14, PLUG[0] - 4, 0, 6, ZW - 20, ZW - 12, PLASTIC, 2.4)
        e.cable('alimentacio', [(PLUG[0] - 4, 3, ZW - 16), ((PLUG[0] + PLUG[1]) / 2, 5, ZW - 2)],
                [(4, 4, 8), (24, 24, 30), (50, 50, 60), (90, 90, 100)], 2.0, gruix=1.4)
    # la cadira, davant la taula (el dibuix pla, dret), amb la seva ombra
    chx, chz = CHAIR
    e.foscor('ombra_cadira', (chx - 22, 0.7, chz + 14), (chx + 22, 0.7, chz + 14), (chx + 22, 0.7, chz - 14),
             (chx - 22, 0.7, chz - 14), lambda s, t: 0.6 * max(0.0, 1 - ((s - 22) / 22) ** 2 - ((t - 14) / 14) ** 2) * 1.6)
    e.sprite('cadira', esc.crop(CHAIR_BOX), (400 - CHAIR_BOX[0], 236 - CHAIR_BOX[1]), (chx, 0, chz), escala_img=0.82)
    # la caixa del router (decorat): de cartró, amb la tapa oberta, la cinta i l'etiqueta
    if 'caixa' in estat:
        bx, bz, bw, bd, bh, ba = BOX
        e.foscor('ombra_caixa', (bx - 30, 0.6, bz + 26), (bx + 34, 0.6, bz + 26), (bx + 34, 0.6, bz - 24),
                 (bx - 30, 0.6, bz - 24), lambda s, t: 0.6 * max(0.0, 1 - ((s - 32) / 30) ** 2 - ((t - 25) / 22) ** 2) * 1.5)

        def cara(s, t, P):
            v = 2.4 - (0.4 if s > bw - 6 else 0)
            if abs(s - bw / 2) < 3:
                return 1.6                                                  # la cinta d'embalar
            return v
        e.caixa_girada('caixa', bx, bz, bw, bd, bh, ba, CARD, 2.0,
                       cares={'davant': {'ramp': CARD, 'lvl': lambda s, t, P: 3.4 if 6 < s < 18 and 6 < t < 13 else cara(s, t, P)},
                              'dalt': {'ramp': CARD, 'lvl': lambda s, t, P: 0.8 if 3 < s < bw - 3 and 3 < t < bd - 3 else 2.8},
                              'dreta': {'ramp': CARD, 'lvl': 1.5}, 'esquerra': {'ramp': CARD, 'lvl': 1.5}})
        c, s_ = math.cos(ba), math.sin(ba)

        def Pc(lx, y, lz):
            return (bx + lx * c - lz * s_, y, bz + lx * s_ + lz * c)
        e.quad('caixa', Pc(-bw / 2, bh + 14, -bd / 2 - 6), Pc(bw / 2, bh + 14, -bd / 2 - 6), Pc(bw / 2, bh, -bd / 2),
               Pc(-bw / 2, bh, -bd / 2), ramp=CARD, lvl=2.8, dues_cares=True)                     # la tapa oberta
    # la prestatgeria, a la dreta del passaplats: llibres i una caixa a dalt; i la paperera de reixa
    sx0, sx1, sz0, sz1, sh = SHELF
    e.foscor('ombra_prestatgeria', (sx0 - 6, 0.6, sz1), (sx1 + 8, 0.6, sz1), (sx1 + 8, 0.6, sz0 - 16),
             (sx0 - 6, 0.6, sz0 - 16), lambda s, t: 0.5 * min(1.0, max(0.0, (sz1 - sz0 + 16 - t) / 16)))

    def llibres(s, t, P):
        if t % 34 < 3 or s < 2.5 or s > sx1 - sx0 - 2.5:
            return 3.0                                                      # els prestatges i els muntants
        b, fila = int(s // 5), int(t // 34)
        if t % 34 < 8 + hr(b, fila, 4) * 12 or hr(b, fila, 9) > 0.82:
            return 0.4                                                      # el buit de sobre els llibres
        return 1.6 + hr(b, fila, 2) * 2.0 - (0.8 if s % 5 < 1 else 0)
    LLIBRES = [(14, 8, 20), (40, 16, 30), (70, 26, 40), (90, 50, 50), (110, 80, 60), (140, 110, 80), (176, 150, 110)]
    e.caixa('prestatgeria', sx0, sx1, 0, sh, sz0, sz1, DESKB, 2.0,
            cares={'davant': {'ramp': LLIBRES, 'lvl': llibres}, 'dalt': {'ramp': DESKB, 'lvl': 3.4},
                   'esquerra': {'ramp': DESKB, 'lvl': 1.4}})
    e.caixa('prestatgeria', sx0 + 18, sx1 - 14, sh, sh + 14, sz0 + 6, sz1 - 4, CARD, 1.8,
            cares={'dalt': {'ramp': CARD, 'lvl': 2.6}})
    bx_, bz_ = BIN
    e.caixa('paperera', bx_ - 9, bx_ + 9, 0, 24, bz_ - 9, bz_ + 9, STEELB, 1.6,
            cares={'davant': {'ramp': STEELB, 'lvl': lambda s, t, P: 2.8 if int(s) % 3 == 0 or int(t) % 3 == 0 else 0.6},
                   'dreta': {'ramp': STEELB, 'lvl': lambda s, t, P: 2.2 if int(s) % 3 == 0 or int(t) % 3 == 0 else 0.4},
                   'dalt': {'ramp': SHEET, 'lvl': 2.2}})
    # primer pla: caixes de mudança en silueta a baix a l'esquerra, una canonada a la dreta i cables que pengen
    FOSC = [(4, 3, 6), (9, 6, 10), (15, 11, 15), (22, 17, 21), (31, 24, 28), (42, 33, 36)]
    for cx, cz, w, d, h, a, y0 in ((-4, 52, 70, 56, 46, 0.3, 0), (-8, 58, 52, 42, 30, 0.12, 46), (66, 8, 50, 40, 28, -0.2, 0)):
        e.caixa_girada('primer_pla', cx, cz, w, d, h, a, FOSC, 1.6, y0=y0,
                       cares={'dalt': {'ramp': FOSC, 'lvl': lambda s, t, P: 3.0 - (1.2 if abs(s - 30) < 2 else 0)},
                              'davant': {'ramp': FOSC, 'lvl': 1.2}, 'dreta': {'ramp': FOSC, 'lvl': 2.0}})
    # el brancal de la porta per on mirem, a tocar de la càmera a l'esquerra (amb un fil de claror de les pantalles)
    e.caixa('primer_pla', JAMB[0], JAMB[1], 0, HW + 40, JAMB[2], JAMB[3], FOSC, 1.0,
            cares={'dreta': {'ramp': FOSC, 'lvl': lambda s, t, P: 3.6 if s < 1.2 else 1.4},
                   'davant': {'ramp': FOSC, 'lvl': 0.8}})
    e.tub('primer_pla', (470, 0, 20), (470, HW, 20), 6, FOSC, 1.8, brides=60)
    e.roca('primer_pla', (432, 0, 96), 30, [(10, 4, 14), (20, 8, 26), (32, 14, 40), (46, 22, 56), (62, 32, 72)], lvl=2.0,
           llum_dir=(-0.7, -0.6), aplana=0.5, seed=4)                            # el puf
    e.cable('primer_pla', [(230, 0.8, 30), (300, 0.8, 70), (380, 0.8, 50), (470, 0.8, 26)],
            [(4, 4, 8), (14, 12, 20), (26, 22, 34), (40, 36, 48)], 2.2, gruix=3.0)
    for k, xx in enumerate((150, 172, 196)):
        e.cable('primer_pla', [(xx, HW, 10 + k * 10), (xx + 10 + k * 6, 150 - k * 18, 16 + k * 10),
                               (xx + 4, 112 - k * 24, 20 + k * 10)], [(4, 4, 8), (14, 12, 20), (26, 22, 34)], 1.2,
                gruix=2.0)
    # la calaixera, a baix a la dreta (l'última: és el més proper a la càmera i ho tapa tot): una silueta amb el
    # cantell tocat pel cian de les pantalles, i el despertador damunt (les 03:12, en vermell)
    RIM = [(4, 3, 6), (9, 8, 14), (14, 18, 26), (20, 40, 48), (40, 90, 100), (90, 170, 175)]
    tx0, tx1, tz0, tz1, th = NIGHT
    BRASA = [(4, 3, 6), (14, 6, 10), (30, 10, 14), (60, 16, 20), (110, 30, 30), (170, 60, 50)]

    def tapa(s, t, P):                             # la claror vermella del despertador, i el cantell
        d = math.hypot(s - 16, t - 8)
        return max(1.4, 4.2 - d / 9) + (0.8 if s < 1.2 or t > tz1 - tz0 - 1.2 else 0)

    def calaixos(s, t, P):                         # tres calaixos: les juntes, fosques, i els poms, amb el cian
        if abs(t - th / 3) < 0.9 or abs(t - 2 * th / 3) < 0.9:
            return 0.2
        if t < 1.0 or s < 1.0:
            return 3.0
        if abs(s - (tx1 - tx0) / 2) < 3 and any(abs(t - (k + 0.5) * th / 3) < 1.5 for k in range(3)):
            return 3.6
        return 1.0
    e.caixa('primer_pla', tx0, tx1, 0, th, tz0, tz1, FOSC, 1.2,
            cares={'dalt': {'ramp': BRASA, 'lvl': tapa},
                   'esquerra': {'ramp': RIM, 'lvl': lambda s, t, P: 4.0 if t < 1.0 else 1.8},
                   'davant': {'ramp': RIM, 'lvl': calaixos}})
    cx0, cz0 = tx0 + 8, tz1 - 12
    e.caixa('primer_pla', cx0, cx0 + CLOCK[0], th, th + CLOCK[1], cz0, cz0 + CLOCK[2], FOSC, 1.4,
            cares={'davant': {'ramp': RED, 'lvl': _digits('0312', CLOCK[0], CLOCK[1])},
                   'esquerra': {'ramp': RIM, 'lvl': 2.6}, 'dalt': {'ramp': RIM, 'lvl': 2.2}})
    return e


# ─── Composició i llum ──────────────────────────────────────────────────────

def _proj(P):
    u, v, _ = CAM.projecta(P)
    return u, v


def _fx():
    mx, my = _proj(MON_C)
    wx, wy = _proj((0, (WIN[2] + WIN[3]) / 2, (WIN[0] + WIN[1]) / 2))
    hx, hy = _proj(((HATCH[0] + HATCH[1]) / 2, (HATCH[2] + HATCH[3]) / 2, ZW))
    light = [llum.wash(mx, my + 10, 230, (80, 230, 210), k=1.0, air=0.05, squash=1.1),      # les pantalles, cian
             llum.wash(wx, wy, 190, (190, 110, 255), k=0.9, air=0.06, squash=0.8)]          # la finestra, lila
    tone = [llum.grade(contrast=1.12, pivot=40, sat=1.25, lift=(5, 1, 10))]
    bloom = [llum.bloom(thr=125, mask=lambda x, y: 1 - 0.8 * ((abs(x - hx) < 30) & (abs(y - hy) < 34)))]
    return light, bloom, tone


@functools.lru_cache(maxsize=None)
def _textures():
    return {'paret': _paret_base(), 'escriptori': _escriptori_base()}


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


def _decorat(*estat, tex=None, retall=None):
    """Un decorat: la sala amb aquell estat, menys la de sempre (només el que canvia), amb la llum."""
    def draw(cv):
        img, _ = _render(frozenset(estat), tex)
        out = _diff(_amb_llum(img, bloom=False), _amb_llum(_base()[0], bloom=False))
        if retall:
            from PIL import Image
            keep = Image.new('RGBA', out.size, (0, 0, 0, 0))
            keep.paste(out.crop(retall), retall[:2])
            out = keep
        cv.img.alpha_composite(out)
        cv.P = cv.img.load()
    return draw


def _amb_router(cv):
    tex = {'paret': _paret_base(), 'escriptori': _escriptori(router=True)}
    _decorat(tex=tex)(cv)


def _obert(cv):
    tex = {'paret': _paret_oberta(), 'escriptori': _escriptori_base()}
    _decorat('obert', tex=tex)(cv)


def figura(who, tag='IdleD'):
    """El primer fotograma d'una animació d'un personatge (el sprite del joc, a escala 1), per posar-lo en un decorat."""
    import json
    from pathlib import Path
    from PIL import Image
    d = Path(__file__).resolve().parents[1] / 'characters' / who
    meta = json.loads((d / f'{who}.json').read_text())
    n = next(t['from'] for t in meta['meta']['frameTags'] if t['name'] == tag)
    frames = meta['frames']
    f = (frames[n] if isinstance(frames, list) else frames[f'{who} {n}.aseprite'])['frame']
    return Image.open(d / f'{who}.png').convert('RGBA').crop((f['x'], f['y'], f['x'] + f['w'], f['y'] + f['h']))


@functools.lru_cache(maxsize=None)
def _paret_vet():
    """La paret amb el passaplats obert i, a l'altra banda, la Vet a la cuina (de mig cos en amunt: l'ampit la talla)."""
    from PIL import Image
    img = _paret_oberta().copy()
    fig = figura('vet')
    k = 0.62                                       # (és a la cuina, més lluny que la paret)
    fig = fig.resize((round(fig.width * k), round(fig.height * k)), Image.Resampling.BOX)
    x0, y0, x1, y1 = PL.HATCH
    capa = Image.new('RGBA', img.size, (0, 0, 0, 0))
    capa.paste(fig, (round((x0 + x1) / 2 - fig.width / 2 - 4), y0 + 9))
    dins = Image.new('RGBA', img.size, (0, 0, 0, 0))
    dins.paste(capa.crop((x0 + 3, y0 + 3, x1 - 2, y1 - 2)), (x0 + 3, y0 + 3))
    img.alpha_composite(dins)
    return img


def _vet_passaplats(cv):
    tex = {'paret': _paret_vet(), 'escriptori': _escriptori_base()}
    _decorat('obert', tex=tex)(cv)


PROPS = {
    'passaplats_obert': _obert,
    'vet_passaplats': _vet_passaplats,
    'pantalles_cerca': lambda cv: _pantalles_cerca(cv),
    'caixa': _decorat('caixa'),
    'router_connectat': _amb_router,
    'fibra_connectada': _decorat('fibra'),
    'xarxa_connectada': _decorat('xarxa'),
    'alimentacio_connectada': _decorat('alimentacio'),
}


# ─── Animacions ─────────────────────────────────────────────────────────────

def _sprite_capa(e, sid, img, peu_img, peu, escala_img=1.0):
    """Un fotograma d'un dibuix pla dret (un sprite de l'escena), on aquell sprite és el que es veu."""
    from PIL import Image
    from pixels import nearest
    idx = e.ids.index(sid)
    k = e.cam.escala(peu) * escala_img
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


def _fotograma(capes):
    """El fons amb unes capes damunt, amb la llum, menys el fons amb la llum."""
    img, _ = _base()
    img = img.copy()
    for c in capes:
        img.alpha_composite(c)
    return _diff(_amb_llum(img), _base_llum())


def _pantalles_cerca(cv):
    """Les pantalles quan l'Iri troba en Marcel (tasca 010): a l'esquerra, la llista d'acomiadaments del BCMU; al
    mig, la fitxa d'en Marcel ressaltada; a la dreta, les seves ressenyes de La Propina (amb estrelles)."""
    from hd.rooms.comu import text
    from PIL import Image
    _, e = _base()
    x0, x1, zf, zb, dh = DESK
    fl = Canvas(light=PL.LIGHT, transparent=True)
    PL.monitors(fl, 0)
    ink, hi = (150, 255, 190), (255, 236, 140)
    for n, (a, b, c, d) in enumerate(PL.MONITORS):
        sx0, sy0, sx1, sy1 = a + 3, b + 3, c - 3, d - 4
        fl.rect(sx0, sy0, sx1, sy1, SCREEN, 1.0, lit=0)
        if n == 0:                                              # la llista: «REESTRUC.» i dos mil noms
            text(fl, 'BCMU', sx0 + 2, sy0 + 2, [ink], 0, flat=ink)
            for k, y in enumerate(range(sy0 + 11, sy1 - 1, 4)):
                w = 10 + int(hr(k, 77) * (sx1 - sx0 - 16))
                fl.hline(sx0 + 2, sx0 + 2 + w, y, [ink if k != 5 else hi], 0, lit=0)
            fl.rect(sx0 + 1, sy0 + 30, sx1 - 1, sy0 + 32, [(40, 90, 60)], 0, lit=0)     # la línia triada
        elif n == 1:                                            # la fitxa d'en Marcel
            text(fl, 'MARCEL', (a + c) // 2 - 14, sy0 + 20, [hi], 0, flat=hi)
            fl.rect((a + c) // 2 - 8, sy0 + 30, (a + c) // 2 + 8, sy0 + 50, [(60, 120, 90), (110, 200, 150)], 1.0, lit=0)
            fl.disc((a + c) // 2, sy0 + 36, 4, 4, [(110, 200, 150), (180, 250, 210)], 1.0, lit=0)   # la foto
            for y in range(sy0 + 30, sy0 + 50, 4):
                fl.hline((a + c) // 2 + 12, sx1 - 4, y, [ink], 0, lit=0)
        else:                                                   # les ressenyes: estrelles i ratlles
            for k, y in enumerate(range(sy0 + 3, sy1 - 2, 9)):
                for st in range(5):
                    fl.flat(sx0 + 3 + st * 3, y, hi if st < 2 + k % 2 else (60, 90, 70))
                fl.hline(sx0 + 3, sx1 - 4, y + 3, [ink], 0, lit=0)
                fl.hline(sx0 + 3, sx0 + 3 + int(hr(k, 9) * (sx1 - sx0 - 8)), y + 5, [ink], 0, lit=0)
    mon = fl.img.crop(MON_BOX)
    capa = _sprite_capa(e, 'monitors', mon, ((MON_BOX[2] - MON_BOX[0]) / 2, MON_BOX[3] - MON_BOX[1] - 1),
                        ((x0 + x1) / 2, dh, zb - 12))
    cv.img.alpha_composite(_fotograma([capa]))
    cv.P = cv.img.load()


def _frames():
    """La pluja al vidre i el codi que corre a les pantalles."""
    _, e = _base()
    x0, x1, zf, zb, dh = DESK
    out = []
    for i in range(8):
        win = e.capa(_paret(rain=i), {'paret_esq'})
        mon = _escriptori(frame=i).crop(MON_BOX)
        out.append(_fotograma([win, _sprite_capa(e, 'monitors', mon, ((MON_BOX[2] - MON_BOX[0]) / 2,
                                                                   MON_BOX[3] - MON_BOX[1] - 1), ((x0 + x1) / 2, dh, zb - 12))]))
    return out


def _frames_neo():
    _, e = _base()
    off = _fotograma([e.capa(_paret(neon=False), {'paret_esq'})])
    on = _diff(_base_llum(), _base_llum())
    return [on if k else off for k in PL.NEON_SEQ]


def _frames_disc():
    _, e = _base()
    lit = _fotograma([e.capa(_escriptori(disc=True), {'torre'})])
    dark = _diff(_base_llum(), _base_llum())
    return [lit if k else dark for k in PL.DISK_SEQ]


ANIMS = {
    'pantalles': {'frames': _frames, 'frameDuration': 200},
    'neo': {'frames': _frames_neo, 'frameDuration': 110},
    'disc_dur': {'frames': _frames_disc, 'frameDuration': 90},
}


def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


# Capes del davant: el primer pla (sempre davant), la cadira, la pila de pizzes i el matalàs (qui hi passa per
# darrere, hi queda darrere).
FRONT = [
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20},
    {'id': 'davant_cadira', 'mask': _amo({'cadira'}), 'baseline': _p(CHAIR[0], CHAIR[1])[1], 'zIndex': 20},
    {'id': 'davant_pizzes', 'mask': _amo({'pizzes'}), 'baseline': _p(PIZZA[0], PIZZA[1] - 14)[1], 'zIndex': 20},
    # la caixa del router (un decorat, no és al fons): una capa buida que només li dona la línia base, perquè qui hi
    # passa per darrere hi quedi darrere i no sembli que s'hi enfila (tasca 285)
    {'id': 'davant_caixa', 'mask': lambda x, y: False, 'baseline': _p(BOX[0], BOX[1] - BOX[3] / 2)[1] - 4, 'zIndex': 20,
     'props': ('caixa',)},
]


# ─── Geometria (coordenades de sala, projectades) ────────────────────────────

def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


# El terra on es camina (al món): entre el matalàs i les pizzes, la taula, el moble i la cantonada de la dreta.
WALK_MON = [(110, 84), (300, 112), (440, 152), (520, 196), (520, 262), (390, 268), (372, 250), (300, 244),
            (300, 230), (122, 230), (122, 140), (96, 140), (96, 96)]
_WALK = [_p(x, z) for x, z in WALK_MON]
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


_MON_RECT = _rect_mon((DESK[0] + 10, DESK[4] + 74, DESK[3] - 12), (DESK[1] - 10, DESK[4], DESK[3] - 12))
_WIN_Y = (WIN[2], WIN[3])

GEOMETRIA = {
    'things': {
        'finestra': {'rect': _rect_mon((0, WIN[3], WIN[0]), (0, WIN[2], WIN[1])), 'walk': _p(118, 190)},
        'poster': {'rect': _rect_mon((_w(198), _y(46), ZW), (_w(256), _y(124), ZW)), 'walk': _p(120, 226)},
        'matalas': {'rect': _rect_mon(*[(MAT[0] + dx, y, MAT[1] + dz) for dx in (-40, 40) for dz in (-62, 62) for y in (0, 20)]),
                    'walk': _p(122, 170)},
        'pizzes': {'rect': _rect_mon(*[(PIZZA[0] + dx, y, PIZZA[1] + dz) for dx in (-20, 20) for dz in (-20, 20) for y in (0, 18)]),
                   'walk': _p(104, 108)},
        'ordinadors': {'rect': _MON_RECT, 'walk': _p((DESK[0] + DESK[1]) / 2 + 30, 226)},
        'router': {'rect': _rect_mon((CAB[0] - 24, CAB[4] + 34, CAB_Z), (CAB[0] + 24, CAB[4] - 6, CAB_Z)),
                   'walk': _p(CAB[0] - 4, 252)},
        'fibra': {'rect': _rect_mon((SOCKET[0] - 2, SOCKET[3] + 2, ZW), (SOCKET[1] + 2, SOCKET[2] - 2, ZW)),
                  'walk': _p(SOCKET[0] + 6, 266)},
        'passaplats': {'rect': _rect_mon((HATCH[0], HATCH[3], ZW), (HATCH[1], HATCH[2], ZW)),
                       'walk': _p(HATCH[0] - 30, 266)},     # (al costat: davant, la taparia)
        'caixa': {'rect': _rect_mon(*[(BOX[0] + dx, y, BOX[1] + dz) for dx in (-24, 24) for dz in (-18, 18) for y in (0, BOX[4] + 14)]),
                  'walk': (352, 203)},          # a l'esquerra de la caixa, al terra (la caixa no es trepitja: 285)
    },
    'spawns': {'iri': _p(200, 150), 'diu': _p(250, 196)},
    'walkable': _WALK,
    'floorSquash': 0.45,                           # (la càmera, picada: el terra es veu aixafat)
    # L'ombra de contacte: la llum dominant són les pantalles (el punt del terra sota els monitors); curta i cap avall.
    'characterShadow': {'enabled': True, 'color': '#0a0614', 'alpha': 0.45, 'squash': 0.42, 'core': 0.6,
                        'light': {'x': _p(MON_C[0], ZW - 20)[0], 'y': _p(MON_C[0], ZW - 20)[1], 'stretch': 0.6,
                                  'reach': 160}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    # la llum de la sala sobre els personatges, en temps d'execució
    'characterLights': {
        'ambient': '#8c84a8',                                                           # habitació fosca, lila
        'lights': [
            {'x': _p(MON_C[0], ZW - 14, MON_C[1])[0], 'y': _p(MON_C[0], ZW - 14, MON_C[1])[1], 'radius': 260,
             'color': '#50e6d2', 'intensity': 0.9},                                     # les pantalles
            {'x': _p(0, (WIN[0] + WIN[1]) / 2, 100)[0], 'y': _p(0, (WIN[0] + WIN[1]) / 2, 100)[1], 'radius': 240,
             'color': '#be6eff', 'intensity': 0.8},                                     # la finestra
            {'x': _p((HATCH[0] + HATCH[1]) / 2, ZW, 100)[0], 'y': _p((HATCH[0] + HATCH[1]) / 2, ZW, 100)[1],
             'radius': 170, 'color': '#ff8c3c', 'intensity': 1.3, 'whenPropVisible': 'passaplats_obert'},
        ],
    },
}

# El terra de sota la caixa del router (tasca 285): no es trepitja mentre la caixa hi és (el runtime activa la regió
# `sota_caixa` amb el decorat `caixa`; quan en Diu se l'endú, el terra torna a ser de tots).
def _sota_caixa(marge=2):
    bx, bz, bw, bd, _, ba = BOX
    c, s_ = math.cos(ba), math.sin(ba)
    return [_p(bx + lx * c - lz * s_, bz + lx * s_ + lz * c) for lx, lz in
            ((-bw / 2 - marge, -bd / 2 - marge), (bw / 2 + marge, -bd / 2 - marge), (bw / 2 + marge, bd / 2 + marge),
             (-bw / 2 - marge, bd / 2 + marge))]


GEOMETRIA['regions'].append({'id': 'sota_caixa', 'active': True, 'walkable': False, 'points': _sota_caixa()})

# Coses per mirar (tasca 012): rectangles de pantalla; s'hi va pel punt d'una cosa del costat.
GEOMETRIA['things'].update({
    'prestatgeria': {'rect': (560, 30, 625, 165), 'walk': GEOMETRIA['things']['passaplats']['walk']},
    'despertador': {'rect': (527, 218, 573, 247), 'walk': GEOMETRIA['things']['caixa']['walk']},
    'paperera': {'rect': (600, 160, 626, 195), 'walk': GEOMETRIA['things']['fibra']['walk']},
})
