"""
El pallol de l'Arenga. EN 3D (hd640/tres_d.py), a 1×.

Una càmera a l'altura del sostre baix que mira de biaix la cantonada del fons a l'esquerra:
  - a la paret de l'esquerra, en escorç, la **porta** estanca del passadís amb l'**inventari** clavat damunt;
  - a la paret del fons, el moble dels **prestatges** (separat de la paret, amb la tapa i el costat), el tauler dels
    **cadenats**, les **defenses** i el **salvavides** penjats d'un cap, el pal de fregar i el bidó;
  - a terra, el **rotllo de cap d'amarrar** (en volum, volta sobre volta) i la **caixa de peix** girada on seu el
    Marcel; a la dreta, la paret de la dreta que fuig, amb una quaderna i reblons;
  - primer pla: una quaderna fosca tallada a la dreta, dues galledes a baix a l'esquerra i cables que pengen.
La llum: dues llums de gàbia penjades dels baos, càlides, amb la foscor als racons i sota els mobles.

Tot el detall ve del dibuix pla de sempre (pallol_pla_comu.py), projectat. El prop (`cadenat_sise`) i les animacions
(`defenses`, `pols`) es dibuixen plans i es projecten per la paret del fons.

El món: x a la dreta (0 = la paret de la porta), y amunt (0 = el terra), z cap al fons (300 = la paret del fons);
1 unitat = 1 píxel de sala a la distància on un personatge fa ≈110 px (escala 1).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from PIL import Image

from hd.pix import Canvas, Light, W, H, hr, mix, WALNUT, ORANGE
from hd.rooms.arenga import WALL, DECK, CAB, DARK, WHITEP, YELL, SEAG, WARM
from hd.rooms.comu import _diff
from hd.rooms.exterior import fbm
from hd640.rooms import pallol_pla_comu as PL
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
ZW = 300                                           # la paret del fons
FY = PL.FLOOR_Y                                    # al dibuix pla, el terra (203)
TOP = 25                                           # al dibuix pla, on comença la paret (a sobre, el sostre pla)
HT = FY - TOP                                      # l'alçada del dibuix pla de la paret (178)
HW = 215                                           # l'alçada de les parets (a sobre del dibuix pla, més planxa)
XL = 92                                            # al dibuix pla, la cantonada: a l'esquerra, la paret de la porta
DZ = 128                                           # a la paret de l'esquerra, on comença el tros del dibuix pla
XR = 560                                           # la paret de la dreta
SHELF = (PL.SHELF[0] - XL - 2, PL.SHELF[2] - XL + 4, ZW - 40)    # el moble: x0, x1, z del davant
SHELF_H = FY - PL.SHELF[1] + 3                     # (amb la tapa)
COIL = (304, 206)                                  # el rotllo de cap d'amarrar (x, z)
CRATE = (428, 226, -0.42)                          # la caixa de peix: x, z, gir
LAMPS = ((230, 236), (400, 190))                   # les llums de gàbia (x, z), penjades dels baos


def _w(fx):
    """Una x del dibuix pla de la paret del fons → la x del món."""
    return fx - XL


def _wz(fx):
    """Una x del dibuix pla de la paret de la porta → la z del món."""
    return DZ + fx


def _y(fy):
    """Una y del dibuix pla (el terra, a 203) → l'alçada del món."""
    return FY - fy


DOOR = (_wz(PL.DOOR[0]), _wz(PL.DOOR[2]), 0, _y(PL.DOOR[1]))              # z0, z1, y0, y1
INV = (_wz(19), _wz(67), _y(83), _y(45))                                   # l'inventari: z0, z1, y0, y1
PADS = (_w(358), _w(418), _y(139), _y(79))                                 # el tauler dels cadenats: x0, x1, y0, y1

CAM = Camera(pos=(390, 180, -190), yaw=-0.26, pitch=0.1, f=420, centre=(330, 70))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)  # (la llum és la del món: la de l'Escena)
TL = Light(ambient=-0.15, vignette=None, floor_fade=None)    # la llum de les textures (la de l'escena va a sobre)
LLUMS = [Llum((x, HW - 20, z), 330, 2.2, power=1.3) for x, z in LAMPS]


# ─── Les textures: el dibuix pla de sempre ───────────────────────────────────

@functools.lru_cache(maxsize=None)
def _paret_nua():
    """La paret de planxa, la porta, l'inventari i els cadenats (sense els prestatges ni les defenses)."""
    cv = Canvas(light=TL)
    PL.walls(cv)
    PL.door(cv)
    PL.inventory(cv)
    PL.padlocks(cv)
    return cv.img


def _paret(swing=0.0):
    """La paret amb les defenses i el salvavides (gronxats `swing` graus)."""
    cv = Canvas(light=TL, img=_paret_nua().copy())
    PL._SWING['a'] = swing
    try:
        PL.fenders(cv)
    finally:
        PL._SWING['a'] = 0.0
    return cv.img


@functools.lru_cache(maxsize=None)
def _paret_base():
    return _paret()


@functools.lru_cache(maxsize=None)
def _prestatges():
    """Els prestatges, de cara (amb la paret de darrere, enfosquida: el fons del moble)."""
    cv = Canvas(light=TL)
    PL.plate_wall(cv, 0, W - 1, frames=0, seams=(), rust=0, socle=0, seed=21)
    PL.shelves(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _objectes():
    """El pal de fregar i el bidó, i una llum de gàbia, sobre transparent (en surten els sprites)."""
    cv = Canvas(light=TL, transparent=True)
    PL.buckets(cv)
    PL.cage_lamp(cv, 60, ly=29, top=21)
    return cv.img


BIDO_BOX = (584, 90, 637, FY + 4)
LAMP_BOX = (51, 20, 70, 40)


# ─── Les superfícies ────────────────────────────────────────────────────────

def _planxa(lvl0, seed=21, quaderna=85):
    """Planxa pintada en coordenades del món (s, t des del cantó de dalt): quadernes amb reblons, soldadures, el
    sòcol gastat i el rovell que regalima."""
    def L(s, t, P):
        v = lvl0 + (hr(int(s) // 3, int(t) // 5, seed) - 0.5) * 0.35 + (fbm(s / 40, t / 30, seed) - 0.5) * 0.6
        d = s % quaderna
        if d < 7:
            v += 0.4 + (0.9 if d < 1 else 0.5 if d < 2 else -0.3 if d >= 6 else 0.1)
            if 3 <= d < 4 and int(t) % 16 == 0:
                v += 1.4                                                # els reblons
        if abs(t - 52) < 1 or abs(t - 124) < 1:
            v -= 1.3                                                    # soldadures
        elif abs(t - 53.5) < 0.6 or abs(t - 125.5) < 0.6:
            v += 0.7
        if t > HW - 24:
            v -= 0.9                                                    # el sòcol
        if hr(int(s) // 2, 3, seed) > 0.93 and (t - 54) % 70 < 20 * hr(int(s) // 2, 4, seed):
            v -= 0.5                                                    # regalims de rovell
        return v
    return L


def _terra(s, t, P):
    """Planxa estriada vista des de dalt: les estries en espiga, les juntes de les planxes, gastada pel mig."""
    x, z = P[0], P[2]
    gx, gz = int(x // 7), int(z // 7)
    lx, lz = x - (gx + 0.5) * 7, z - (gz + 0.5) * 7
    d = (lx + lz) if (gx + gz) % 2 else (lx - lz)
    stud = abs(d) < 1.0 and abs(lx - lz if (gx + gz) % 2 else lx + lz) < 5.0
    v = 2.6 + (fbm(x / 70, z / 40, 9) - 0.5) * 1.2 + (hr(int(x) // 3, int(z) // 3, 9) - 0.5) * 0.4
    if stud:
        v += 1.0
    if x % 101 < 1.2 or z % 90 < 1.2:
        v -= 1.6
    worn = max(0.0, 1 - abs(z - 150) / 90) * max(0.0, 1 - abs(x - 280) / 240)
    return v + worn * 0.5 - (0.6 if stud else 0) * worn


FOSC = [(2, 3, 4), (5, 8, 9), (9, 14, 14), (14, 21, 20), (20, 30, 28), (28, 40, 37)]


def anella(e, sid, cx, cz, rx, rz, y, ramp, lvl, gruix, meitat=None, a0=0.0, n=28):
    """Una volta de cap (una el·lipse al pla del terra, a l'alçada y). `meitat`: 'darrere' o 'davant' (la meitat de
    la volta que queda més lluny o més a prop de la càmera)."""
    pts = []
    for k in range(n + 1):
        a = a0 + 2 * math.pi * k / n
        P = (cx + math.cos(a) * rx, y, cz + math.sin(a) * rz)
        pts.append((P, math.sin(a)))
    seg = []
    for P, sa in pts:
        dins = meitat is None or (sa > 0) == (meitat == 'darrere')
        if dins:
            seg.append(P)
        elif len(seg) > 1:
            e.cable(sid, seg, ramp, lvl, gruix=gruix)
            seg = []
        else:
            seg = []
    if len(seg) > 1:
        e.cable(sid, seg, ramp, lvl, gruix=gruix)


def rotllo(e, sid, cx, cz, r, voltes, ramp, lvl=3.0, gruix=4.2, pas=3.6):
    """Un rotllo de cap a terra, volta sobre volta, cada cop una mica més estret: primer les meitats de darrere,
    després les del davant (de baix a dalt)."""
    for meitat in ('darrere', 'davant'):
        for k in range(voltes):
            rr = r - k * 1.6
            anella(e, sid, cx, cz, rr, rr * 0.92, gruix / 2 + k * pas, ramp,
                   lvl + (0.4 if meitat == 'davant' else -0.5) + k * 0.12, gruix, meitat, a0=k * 0.7)


def escena(cv, tex, estat=frozenset()):
    """Tota la sala, de lluny a prop. → l'Escena (qui ha pintat què)."""
    e = Escena(cv, CAM, LLUMS, ambient=-0.2)
    zn = CAM.pos[2] + 40
    paret = tex['paret']
    # el sostre, baix i fosc, amb els baos
    e.quad('sostre', (-60, HW, zn), (XR, HW, zn), (XR, HW, ZW), (-60, HW, ZW), ramp=DARK, lvl=2.4, dues_cares=True)
    # la paret de la porta (x = 0): de prop, planxa; el tros de la porta, el dibuix pla; fins a la cantonada, planxa
    e.quad('paret_esq_prop', (0, HW, zn), (0, HW, DZ), (0, 0, DZ), (0, 0, zn), ramp=WALL, lvl=_planxa(3.0, seed=3))
    e.quad('paret_esq_dalt', (0, HW, DZ), (0, HW, DZ + XL), (0, HT, DZ + XL), (0, HT, DZ), ramp=WALL,
           lvl=_planxa(3.0, seed=5, quaderna=200))
    e.quad('paret_esq', (0, HT, DZ), (0, HT, DZ + XL), (0, 0, DZ + XL), (0, 0, DZ), tex=(paret, (0, TOP, XL, FY)))
    e.quad('paret_esq_fons', (0, HW, DZ + XL), (0, HW, ZW), (0, 0, ZW), (0, 0, DZ + XL), ramp=WALL,
           lvl=_planxa(3.0, seed=4, quaderna=40))
    # la paret del fons (z = 300): el dibuix pla (x 92..640)
    e.quad('paret_fons_dalt', (0, HW, ZW), (XR, HW, ZW), (XR, HT, ZW), (0, HT, ZW), ramp=WALL,
           lvl=_planxa(3.0, seed=6, quaderna=85))
    e.quad('paret_fons', (0, HT, ZW), (W - XL, HT, ZW), (W - XL, 0, ZW), (0, 0, ZW), tex=(paret, (XL, TOP, W, FY)))
    if XR > W - XL:
        e.quad('paret_fons_dreta', (W - XL, HT, ZW), (XR, HT, ZW), (XR, 0, ZW), (W - XL, 0, ZW), ramp=WALL,
               lvl=_planxa(3.0, seed=8, quaderna=85))
    # la paret de la dreta (x = 590), que fuig
    e.quad('paret_dreta', (XR, HW, ZW), (XR, HW, zn), (XR, 0, zn), (XR, 0, ZW), ramp=WALL, lvl=_planxa(2.6, seed=7))
    # el terra
    e.quad('terra', (0, 0, ZW), (XR, 0, ZW), (XR, 0, zn), (0, 0, zn), ramp=DECK, lvl=_terra)
    # els bassals de llum de les llums de gàbia, a terra i a la paret del fons
    for lx, lz in LAMPS:
        e.claror((lx - 150, 0.3, lz + 150), (lx + 150, 0.3, lz + 150), (lx + 150, 0.3, lz - 150), (lx - 150, 0.3, lz - 150),
                 WARM, lambda s, t: 0.3 * max(0.0, 1 - math.hypot(s - 150, (t - 150) * 1.1) / 150) ** 1.5)
        e.claror((lx - 160, HT, ZW - 0.4), (lx + 160, HT, ZW - 0.4), (lx + 160, 0, ZW - 0.4), (lx - 160, 0, ZW - 0.4),
                 WARM, lambda s, t, lz=lz: 0.16 * max(0.0, 1 - math.hypot(s - 160, t * 0.8) / 160)
                 * max(0.0, 1 - (ZW - lz) / 160))
    # una mànega i un cable pel terra, que trenquen la línia de la paret
    e.cable('cables', [(XR - 2, 6, 120), (XR - 20, 0.8, 150), (520, 0.8, 236), (470, 0.8, 262), (360, 0.8, 286),
                       (300, 0.8, 292), (272, 0.8, 270)], PL.BLACKC, 2.4, gruix=3.0)
    e.cable('cables', [(4, 0.8, 238), (40, 0.8, 250), (70, 0.8, 236), (110, 0.8, 252), (150, 0.8, 256)],
            YELL, 2.4, gruix=2.0)
    # els baos del sostre, que fugen cap al fons, i la safata de cables
    for bx in (60, 230, 400, 560):
        e.caixa('baos', bx - 6, bx + 6, HW - 12, HW, zn, ZW, CAB, 1.8,
                cares={'sota': {'ramp': CAB, 'lvl': 1.6}, 'esquerra': {'ramp': CAB, 'lvl': 2.2},
                       'dreta': {'ramp': CAB, 'lvl': 1.2}})
    # la foscor dels racons: on les parets es troben amb el terra i entre elles
    e.foscor('racons', (0, 0.5, ZW), (XR, 0.5, ZW), (XR, 0.5, zn), (0, 0.5, zn),
             lambda s, t: max(0.6 * max(0.0, 1 - t / 30), 0.55 * max(0.0, 1 - s / 24), 0.5 * max(0.0, 1 - (XR - s) / 30)))
    # la cantonada de les dues parets: una ombra ampla i, arran de la junta, ben fosca (el relleu del racó)
    e.foscor('cantonada', (0, HW, ZW - 0.5), (110, HW, ZW - 0.5), (110, 0, ZW - 0.5), (0, 0, ZW - 0.5),
             lambda s, t: max(0.72 * max(0.0, 1 - s / 110) ** 1.3, 0.85 if s < 3 else 0.0))
    e.foscor('cantonada2', (0.5, HW, ZW - 110), (0.5, HW, ZW), (0.5, 0, ZW), (0.5, 0, ZW - 110),
             lambda s, t: max(0.72 * max(0.0, 1 - (110 - s) / 110) ** 1.3, 0.85 if s > 107 else 0.0))
    e.foscor('sostre_fosc', (-60, HW - 0.5, ZW - 0.6), (XR, HW - 0.5, ZW - 0.6), (XR, 0, ZW - 0.6), (-60, 0, ZW - 0.6),
             lambda s, t: 0.5 * max(0.0, 1 - t / 40))
    e.foscor('sostre_fosc2', (XR - 0.5, HW, ZW), (XR - 0.5, HW, zn), (XR - 0.5, 0, zn), (XR - 0.5, 0, ZW),
             lambda s, t: 0.4 * max(0.0, 1 - t / 40) + 0.25)
    # el tub vertical de la cantonada, i el que corre arran de la paret de la dreta
    e.tub('tubs', (4, 0, ZW - 6), (4, HW, ZW - 6), 4, SEAG, 2.6, brides=50)
    e.tub('tubs', (XR - 8, 26, ZW), (XR - 8, 26, zn + 40), 5, CAB, 2.4, brides=60)
    # el moble dels prestatges: el davant, el dibuix pla; el costat i la tapa, planxa
    x0, x1, zf = SHELF
    e.foscor('ombra_prestatges', (x0 - 6, 0.6, ZW), (x1 + 10, 0.6, ZW), (x1 + 10, 0.6, zf - 18), (x0 - 6, 0.6, zf - 18),
             lambda s, t: 0.55 * min(1.0, max(0.0, (ZW - zf + 18 - t) / 18)))
    e.caixa('prestatges', x0, x1, 0, SHELF_H, zf, ZW - 2, CAB, 2.6,
            cares={'davant': {'tex': (tex['prestatges'], (PL.SHELF[0] - 3, PL.SHELF[1] - 3, PL.SHELF[2] + 4, FY + 4))},
                   'dalt': {'ramp': CAB, 'lvl': lambda s, t, P: 3.4 - (1.2 if s % 120 < 3 else 0)
                            + (fbm(s / 20, t / 8, 5) - 0.5) * 0.6},
                   'dreta': {'ramp': CAB, 'lvl': lambda s, t, P: 2.0 - (1.4 if int(t) % 41 < 4 else 0)
                             + (0.8 if int(s) % 8 < 2 and int(t) % 8 < 2 else 0)}})
    # les galledes i la caixa de cartró, damunt la tapa del moble
    e.caixa_girada('prestatges', x0 + 40, zf + 18, 30, 24, 16, 0.2, PL.CARD, 2.6, y0=SHELF_H)
    # el pal de fregar i el bidó, drets a la cantonada de la dreta
    obj = tex['objectes']
    e.foscor('ombra_bido', (_w(600), 0.6, ZW), (_w(640), 0.6, ZW), (_w(640), 0.6, ZW - 30), (_w(600), 0.6, ZW - 30),
             lambda s, t: 0.5 * max(0.0, 1 - t / 30))
    e.sprite('bido', obj.crop(BIDO_BOX), (621 - BIDO_BOX[0], FY + 3 - BIDO_BOX[1]), (_w(621), 0, ZW - 14))
    # el rotllo de cap d'amarrar, a terra, amb l'ombra
    cx, cz = COIL
    e.foscor('ombra_rotllo', (cx - 46, 0.6, cz + 44), (cx + 50, 0.6, cz + 44), (cx + 50, 0.6, cz - 46), (cx - 46, 0.6, cz - 46),
             lambda s, t: 0.6 * max(0.0, 1 - ((s - 48) / 48) ** 2 - ((t - 45) / 45) ** 2) * 1.5)
    e.quad('rotllo', (cx - 24, 0.4, cz + 22), (cx + 24, 0.4, cz + 22), (cx + 24, 0.4, cz - 22), (cx - 24, 0.4, cz - 22),
           ramp=DARK, lvl=0.8, forma=lambda s, t: (s - 24) ** 2 + (t - 22) ** 2 < 22 ** 2)
    rotllo(e, 'rotllo', cx, cz, 38, 5, PL.ROPE, 3.0)
    anella(e, 'rotllo', cx - 14, cz - 6, 10, 6, 22, PL.ROPE, 4.0, 3.0, a0=0.8)          # la gassa, per sobre
    # la caixa de peix, del revés, girada: les posts i els travessers
    bx, bz, ba = CRATE
    e.foscor('ombra_caixa', (bx - 40, 0.6, bz + 36), (bx + 44, 0.6, bz + 36), (bx + 44, 0.6, bz - 38), (bx - 40, 0.6, bz - 38),
             lambda s, t: 0.65 * max(0.0, 1 - ((s - 42) / 40) ** 2 - ((t - 37) / 34) ** 2) * 1.5)

    def posts(s, t, P):
        v = 3.4 - (1.6 if t % 10 < 1.2 else 0) + (hr(int(t // 10), 3) - 0.5) * 0.6
        if s < 3 or s > 37:
            v += 0.4                                                     # els travessers dels cantons
        if abs(t - 13) < 1 and 8 < s < 28:
            return 1.4                                                   # la marca de pintura
        return v
    e.caixa_girada('caixa', bx, bz, 40, 34, 36, ba, WALNUT, 3.0,
                   cares={'davant': {'ramp': WALNUT, 'lvl': posts},
                          'esquerra': {'ramp': WALNUT, 'lvl': lambda s, t, P: posts(s, t, P) - 1.0},
                          'dreta': {'ramp': WALNUT, 'lvl': lambda s, t, P: posts(s, t, P) - 1.2},
                          'dalt': {'ramp': WALNUT, 'lvl': lambda s, t, P: 4.4 - (1.8 if s % 11 < 1.2 else 0)
                                   + (hr(int(s // 11), 5) - 0.5) * 0.6}})
    # les llums de gàbia, penjades dels baos
    for lx, lz in LAMPS:
        e.sprite('llums', obj.crop(LAMP_BOX), (60 - LAMP_BOX[0], 21 - LAMP_BOX[1]), (lx, HW - 12, lz))
    # primer pla: una quaderna fosca tallada a la dreta, dues galledes a baix a l'esquerra i cables que pengen
    e.caixa('primer_pla', 466, 492, 0, HW, 46, 70, FOSC, 1.8,
            cares={'esquerra': {'ramp': FOSC, 'lvl': lambda s, t, P: 2.4 + (1.4 if int(t) % 18 == 0 else 0)
                                + (1.6 if s < 2 else 0)},
                   'davant': {'ramp': FOSC, 'lvl': lambda s, t, P: 1.4 + (1.0 if s < 2 else 0)
                              + (1.4 if 8 < s < 13 and int(t) % 16 < 2 else 0)}})
    for cx_, cz_, rr, a in ((22, 86, 16, 0.3), (58, 70, 14, -0.2)):
        e.caixa_girada('primer_pla', cx_, cz_, rr * 2, rr * 2, rr * 2.2, a, FOSC, 2.0,
                       cares={'dalt': {'ramp': FOSC, 'lvl': lambda s, t, P, rr=rr: 0.6 if 3 < s < 2 * rr - 3 and 3 < t < 2 * rr - 3
                                       else 3.6},
                              'davant': {'ramp': FOSC, 'lvl': lambda s, t, P: 2.6 - (1.0 if abs(t - 8) < 1 else 0)},
                              'dreta': {'ramp': FOSC, 'lvl': 1.4}, 'esquerra': {'ramp': FOSC, 'lvl': 1.8}})
    for k, xx in enumerate((110, 128)):
        e.cable('primer_pla', [(xx, HW, 50 + k * 8), (xx + 12 + k * 6, 160 - k * 16, 54 + k * 8),
                               (xx + 4, 118 - k * 20, 58 + k * 8)], FOSC, 2.0, gruix=2.4)
    return e


# ─── Composició ────────────────────────────────────────────────────────────

def _proj(P):
    u, v, _ = CAM.projecta(P)
    return u, v


@functools.lru_cache(maxsize=None)
def _textures():
    return {'paret': _paret_base(), 'prestatges': _prestatges(), 'objectes': _objectes()}


def _glow(cv):
    """La claror de les llums de gàbia (a sobre de tot, com feia el pla)."""
    for lx, lz in LAMPS:
        u, v = _proj((lx, HW - 22, lz))
        k = CAM.escala((lx, HW - 22, lz))
        cv.glow(u, v, 52 * k, WARM, 0.5)
        cv.glow(u, v, 16 * k, (255, 240, 200), 0.6)


def _render(estat=frozenset(), tex=None):
    cv = Canvas(light=LIGHT)
    e = escena(cv, tex or _textures(), estat)
    _glow(cv)
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)    # la barra de verbs: negre
    return cv.img, e


@functools.lru_cache(maxsize=None)
def _base():
    return _render()


def bg(cv):
    cv.img.paste(_base()[0])
    cv.P = cv.img.load()


def cadenat_sise(cv):
    """El sisè cadenat, al seu ganxo del tauler (projectat per la paret del fons)."""
    _, e = _base()
    flat = Canvas(light=TL, transparent=True)
    PL.cadenat_sise(flat)
    cv.img.alpha_composite(e.capa(flat.img, {'paret_fons'}))
    cv.P = cv.img.load()


PROPS = {'cadenat_sise': cadenat_sise}


# ─── Animacions ────────────────────────────────────────────────────────────

def _frames_defenses():
    """El balanceig: les defenses i el salvavides fan un vaivé lent, projectats per la paret del fons."""
    img, e = _base()
    n = 32
    frames = []
    for i in range(n):
        a = 3.5 * math.sin(2 * math.pi * i / n)
        out = img.copy()
        out.alpha_composite(e.capa(_paret(a), {'paret_fons'}))
        frames.append(_diff(out, img))
    return frames


def _frames_pols():
    """Pols que sura a la llum de la primera llum de gàbia (cada mota fa un llaç tancat: el bucle no salta)."""
    img, _ = _base()
    lx, lz = LAMPS[0]
    motes = []
    for k in range(24):
        P = (lx + (hr(k, 7) - 0.5) * 120, HW - 30 - hr(k, 8) * 120, lz + (hr(k, 13) - 0.5) * 90)
        u, v = _proj(P)
        s = CAM.escala(P)
        motes.append((u, v, (8 + hr(k, 9) * 13) * s, (5 + hr(k, 10) * 11) * s, hr(k, 11), 1 + int(hr(k, 12) * 2)))
    cu, cv_ = _proj((lx, HW - 22, lz))
    R = 150 * CAM.escala((lx, HW - 22, lz))
    n = 48
    frames = []
    for i in range(n):
        cv = Canvas(light=LIGHT, img=img.copy())
        t = i / n
        for (cx, cy, ax, ay, ph, fx) in motes:
            a = 2 * math.pi * (t + ph)
            x = round(cx + ax * math.sin(fx * a))
            y = round(cy + ay * math.sin(a + ph * 3))
            near = max(0.0, 1 - math.hypot(x - cu, (y - cv_) * 0.9) / R)
            alpha = near * (0.5 + 0.25 * (1 + math.sin(a * 2 + ph * 7)))
            if alpha > 0.08 and 0 <= x < W and 0 <= y < BOTTOM:
                cv.flat(x, y, mix(cv.get(x, y), (255, 236, 196), alpha))
        frames.append(_diff(cv.img, img))
    return frames


ANIMS = {'defenses': {'frames': _frames_defenses, 'frameDuration': 200},
         'pols': {'frames': _frames_pols, 'frameDuration': 130}}


# ─── Capes del davant ─────────────────────────────────────────────────────

def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


# El primer pla (sempre davant), la caixa de peix i el rotllo (qui hi passa per darrere, hi queda darrere).
FRONT = [
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20},
    {'id': 'davant_caixa', 'mask': _amo({'caixa'}), 'baseline': _p(CRATE[0], CRATE[1] - 6)[1], 'zIndex': 20},
    {'id': 'davant_rotllo', 'mask': _amo({'rotllo'}), 'baseline': _p(COIL[0], COIL[1] - 4)[1], 'zIndex': 20},
]


# ─── Geometria (coordenades de sala, projectades) ────────────────────────────

def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


def _escala_a(v):
    """L'escala d'un personatge amb els peus a la y de pantalla `v` (al terra, la profunditat només depèn de v)."""
    lo, hi = 1.0, 3000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.projecta((300, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((300, 0, (lo + hi) / 2))


# El terra on es camina (al món): davant del moble i de la porta, i per darrere del rotllo; el rotllo i la caixa de
# peix hi fan forats (s'hi pot fer la volta).
def _z_v(x, v):
    """La z del terra que cau a la y de pantalla `v`, a la x del món `x`."""
    lo, hi = -100.0, 2000.0
    for _ in range(50):
        z = (lo + hi) / 2
        if CAM.projecta((x, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return round((lo + hi) / 2)


V_PROP = 245                                       # on es camina més a prop (escala ≈1,2)
WALK_MON = ([(14, 252), (270, 252), (270, 284), (486, 284), (486, 266), (528, 266)]
            + [(x, _z_v(x, V_PROP)) for x in (528, 440, 330, 220, 110)] + [(14, max(104, _z_v(14, V_PROP)))])
_WALK = [_p(x, z) for x, z in WALK_MON]
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)


def _forat_caixa(m=8):
    bx, bz, ba = CRATE
    c, s_ = math.cos(ba), math.sin(ba)
    a, b = 20 + m, 17 + m
    return [_p(bx + lx * c - lz * s_, bz + lx * s_ + lz * c) for lx, lz in ((-a, -b), (a, -b), (a, b), (-a, b))]


_FORATS = [[_p(COIL[0] + math.cos(a) * 44, COIL[1] + math.sin(a) * 42) for a in [k * math.pi / 5 for k in range(10)]],
           _forat_caixa()]

GEOMETRIA = {
    'things': {
        'porta': {'rect': _rect_mon((0, DOOR[3], DOOR[0]), (0, 0, DOOR[1])), 'walk': _p(22, (DOOR[0] + DOOR[1]) / 2)},
        'prestatges': {'rect': _rect_mon(*[(x, y, z) for x in SHELF[:2] for y in (0, SHELF_H) for z in (SHELF[2], ZW)]),
                       'walk': _p((SHELF[0] + SHELF[1]) / 2, SHELF[2] - 22)},
        'inventari': {'rect': _rect_mon((0, INV[3], INV[0]), (0, INV[2], INV[1])), 'walk': _p(24, (INV[0] + INV[1]) / 2 + 6)},
    },
    'spawns': {'iri': _p(250, 160), 'vet': _p(170, 176), 'marcel': _p(CRATE[0] + 4, CRATE[1] - 36),
               'diu': _p(CRATE[0] - 80, CRATE[1] - 44)},
    'walkable': _WALK,
    'forats': _FORATS,
    'floorSquash': 0.4,                            # (la càmera, poc picada i baixa: el terra força aixafat)
    # L'ombra de contacte: la llum dominant és la llum de gàbia de l'esquerra; curta i cap avall.
    'characterShadow': {'enabled': True, 'color': '#050a0a', 'alpha': 0.45, 'squash': 0.38, 'core': 0.6,
                        'light': {'x': _p(*LAMPS[0])[0], 'y': _p(*LAMPS[0])[1], 'stretch': 0.6, 'reach': 160}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    # la llum de la sala sobre els personatges, en temps d'execució
    'characterLights': {
        'ambient': '#7c8a86',                                                           # planxa verda, penombra
        'lights': [{'x': _p(lx, lz, HW - 22)[0], 'y': _p(lx, lz, HW - 22)[1], 'radius': 220, 'color': '#ffd28c',
                    'intensity': 0.9} for lx, lz in LAMPS],
    },
}

# Coses per mirar (tasca 061), en píxels de pantalla.
GEOMETRIA['things'].update({
    'cadenats': {'rect': (337, 75, 383, 125), 'walk': (300, 194)},
    'defenses_penjades': {'rect': (395, 55, 442, 142), 'walk': (416, 190)},
    'salvavides': {'rect': (475, 85, 528, 145), 'walk': (500, 198)},
    'corda': {'rect': (310, 182, 388, 226), 'walk': (348, 238)},
    'caixa': {'rect': (450, 168, 506, 226), 'walk': (478, 238)},
    'escombra': {'rect': (540, 92, 562, 202), 'walk': (550, 214)},
    'bombona': {'rect': (562, 145, 578, 202), 'walk': (570, 214)},
})
