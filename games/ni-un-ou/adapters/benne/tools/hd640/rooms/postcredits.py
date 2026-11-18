"""
Els postcrèdits: el mòbil de la Vet, de nit, a l'habitació de Galway. EN 3D (hd640/tres_d.py), a 1×. El dibuix pla
de sempre (el mòbil amb el xat de la Juana i la foto dels tubs «GALWAY - PUNT 7», la mà, la finestra amb els llums
del port desenfocats i la pluja) és a postcredits_pla_comu.py, i se'n treuen les textures.

Pla subjectiu: la Vet, asseguda al llit a les fosques, aguanta el mòbil a prop. El mòbil, gran i girat de biaix (la
vora de la dreta fuig i el capçal s'inclina enrere), deixa veure el cantell, i la pantalla el mateix es llegeix.
Darrere, la paret de l'esquerra fuig amb la finestra en escorç (els llums del port, la pluja al vidre) i la seva
claror blava cau en diagonal pel llit; la paret del fons, fosca, amb la porta i la ratlla de llum del passadís per
sota. Primer pla fosc: la cortina, a l'esquerra, tallada per la vora; el nòrdic, a baix. A sota queda lloc per al text.
ANIMS: `escrivint` (els tres puntets de la Juana).
"""
import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

import functools
import math

from hd.pix import Light, Canvas, W, H, hr
from hd.rooms.comu import _diff
from hd.rooms.exterior import fbm
from hd640.rooms import postcredits_pla_comu as PL
from hd640.rooms.postcredits_pla_comu import ROOM, BODY
from hd640.tres_d import Camera, Escena, Llum

CAM = Camera(pos=(0.0, 0.0, 0.0), yaw=-0.12, pitch=0.06, f=420, centre=(320, 150))
LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)

# El mòbil: el centre del dibuix pla (320, 123) va a MOB_C; girat MOB_YAW (la vora de la dreta, enrere) i inclinat
# MOB_TILT (el capçal, enrere). 1 px del dibuix pla = 1 unitat.
MOB_C = (-4.0, 4.0, 400.0)
MOB_YAW, MOB_TILT = 0.46, 0.22
GRUIX = 9.0
CROP = (226, 0, 432, 304)                      # el mòbil i la mà, al dibuix pla

# L'habitació
XL, ZB, YF = -300.0, 1150.0, -230.0            # la paret de l'esquerra, la del fons i el terra
WIN = (380.0, 860.0, -60.0, 240.0)             # la finestra a la paret de l'esquerra: z0, z1, y0, y1
WIN_CROP = (23, 23, 217, 205)        # la finestra (amb el marc) al dibuix pla
DOOR = (260.0, 460.0, 280.0)                   # la porta a la paret del fons: x0, x1, alçada

SKY = [(6, 8, 18), (10, 14, 28), (14, 20, 40), (20, 28, 54), (30, 40, 70)]
WALL = [(3, 3, 6), (6, 6, 10), (9, 9, 15), (13, 13, 21), (18, 18, 28), (24, 24, 36), (32, 32, 46)]
DUVET = [(2, 2, 4), (5, 5, 9), (8, 9, 14), (12, 13, 20), (17, 19, 28), (24, 27, 38), (34, 38, 52), (48, 54, 72)]
CURT = [(1, 1, 3), (4, 4, 8), (7, 8, 13), (11, 12, 19), (16, 18, 27), (22, 25, 36)]
DOORL = [(40, 30, 18), (90, 66, 36), (160, 120, 70), (220, 180, 120)]

LLUMS = [Llum((MOB_C[0], MOB_C[1], MOB_C[2] - 40), 420.0, 2.2, power=1.4),        # la pantalla
         Llum((XL + 30, 120.0, (WIN[0] + WIN[1]) / 2), 1000.0, 2.2, power=1.2)]       # la finestra (els llums del port)
AMBIENT = 0.0


def _m(px, py, dz=0.0):
    """Un punt del dibuix pla del mòbil (px, py) al món; `dz`: cap enrere (el gruix)."""
    ca, sa = math.cos(MOB_YAW), math.sin(MOB_YAW)
    cb, sb = math.cos(MOB_TILT), math.sin(MOB_TILT)
    pa, pb = px - 320, py - 123
    # R: la dreta del mòbil (enrere amb el gir); D: avall pel mòbil (cap a nosaltres amb la inclinació); N: enrere
    R = (ca, 0.0, sa)
    D = (sb * sa, -cb, -sb * ca)
    N = (-cb * sa, -sb, cb * ca)
    return tuple(MOB_C[k] + pa * R[k] + pb * D[k] + dz * N[k] for k in range(3))


# ─── Textures ─────────────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _mobil(dots=0):
    cv = Canvas(light=PL.LIGHT, transparent=True)
    PL.phone(cv)
    PL.screen(cv, dots)
    PL.hand(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _finestra():
    cv = Canvas(light=PL.LIGHT)
    PL.room(cv)
    return cv.img


# ─── L'escena ────────────────────────────────────────────────────────────────

def _parets(e):
    def paret(s, t, P):
        return 1.6 + (fbm(P[0] / 90 + P[2] / 90, P[1] / 70, 3) - 0.5) * 0.8
    # el terra (gairebé no es veu: el tapa el llit) i el sostre
    e.quad('terra', (XL, YF, ZB), (900.0, YF, ZB), (900.0, YF, 0.0), (XL, YF, 0.0), ramp=WALL, lvl=1.0)
    e.quad('sostre', (XL, 330.0, 0.0), (900.0, 330.0, 0.0), (900.0, 330.0, ZB), (XL, 330.0, ZB), ramp=WALL,
           lvl=lambda s, t, P: 1.2 - t / 900)
    # la paret del fons, amb la porta i la ratlla de llum del passadís per sota
    e.quad('fons', (XL, 330.0, ZB), (900.0, 330.0, ZB), (900.0, YF, ZB), (XL, YF, ZB), ramp=WALL, lvl=paret)
    x0, x1, h = DOOR
    e.quad('porta', (x0, YF + h, ZB - 1), (x1, YF + h, ZB - 1), (x1, YF, ZB - 1), (x0, YF, ZB - 1), ramp=WALL,
           lvl=lambda s, t, P: 1.0 + (0.8 if s < 8 or s > x1 - x0 - 8 or t < 8 else 0) + (0.5 if abs(s - 160) < 4 and 130 < t < 150 else 0))
    e.quad('porta', (x0 + 6, YF + 3, ZB - 2), (x1 - 6, YF + 3, ZB - 2), (x1 - 6, YF, ZB - 2), (x0 + 6, YF, ZB - 2),
           ramp=DOORL, lvl=2.6)
    e.claror((x0 - 60, YF + 0.5, ZB - 2), (x1 + 60, YF + 0.5, ZB - 2), (x1 + 160, YF + 0.5, ZB - 260),
             (x0 + 40, YF + 0.5, ZB - 260), (220, 180, 120), lambda s, t: 0.25 * max(0.0, 1 - t / 260))
    # la paret de l'esquerra, amb la finestra en escorç (el dibuix pla: els llums del port i la pluja al vidre)
    z0, z1, y0, y1 = WIN
    e.quad('esquerra', (XL, 330.0, 0.0), (XL, 330.0, ZB), (XL, YF, ZB), (XL, YF, 0.0), ramp=WALL, lvl=paret)
    e.quad('finestra', (XL + 0.5, y1, z0), (XL + 0.5, y1, z1), (XL + 0.5, y0, z1), (XL + 0.5, y0, z0),
           tex=(_finestra(), WIN_CROP))
    # l'ampit, que fa una mica de cornisa
    e.caixa('ampit', XL, XL + 22, y0 - 8, y0, z0 - 14, z1 + 14, WALL, 2.0,
            cares={'dalt': {'ramp': WALL, 'lvl': 3.2}})
    # la claror de la finestra: cau en diagonal per la paret del fons i pel terra
    e.claror((XL, YF + 0.5, z1 + 40), (500.0, YF + 0.5, z1 + 320), (500.0, YF + 0.5, z0 + 60), (XL, YF + 0.5, z0 - 40),
             (60, 80, 140), lambda s, t: 0.3 * max(0.0, 1 - s / 800))


def _llit(e):
    """El nòrdic, a baix: plecs grossos, fosc, amb la claror blava de la finestra i la del mòbil."""
    def plecs(s, t, P):
        x, z = P[0], P[2]
        lv = 2.0 + math.sin(x / 38 + math.sin(z / 60) * 1.4) * 0.9 + (fbm(x / 80, z / 60, 7) - 0.5) * 1.4
        return lv
    e.quad('llit', (XL, -150.0, 900.0), (900.0, -150.0, 900.0), (900.0, -150.0, 120.0), (XL, -150.0, 120.0),
           ramp=DUVET, lvl=plecs)
    # el capçal del llit d'en davant, i el coixí: a la paret de la dreta no hi arribem; el llit acaba al fons
    e.caixa('llit', XL, 900.0, YF, -150.0, 880.0, 920.0, DUVET, 1.0, cares={'dalt': {'ramp': DUVET, 'lvl': 2.4}})
    # la claror de la finestra pel nòrdic, en diagonal, amb l'ombra del muntant del mig
    z0, z1 = WIN[0], WIN[1]
    zm = (z0 + z1) / 2
    e.claror((XL, -149.5, z1 + 40), (XL + 420, -149.5, z1 + 300), (XL + 420, -149.5, z0 + 120), (XL, -149.5, z0 - 20),
             (70, 96, 170), lambda s, t: (0.0 if abs(t - (z1 - zm + 30)) < 12 else 0.42) * max(0.0, 1 - s / 520)
             * min(1.0, t / 30, (z1 - z0 + 60 - t) / 30))


def _mobil_mon(e, img):
    """El mòbil (i la mà que l'aguanta), pla i girat; el cantell de l'esquerra i el de sota, amb el gruix."""
    x0, y0, x1, y1 = PL.PHONE
    # el cantell de l'esquerra (es veu perquè la vora de la dreta fuig) i el de dalt (el capçal s'inclina enrere)
    e.quad('mobil_cantell', _m(x0 + 2, y0 + 12, GRUIX), _m(x0 + 2, y0 + 12), _m(x0 + 2, y1 - 12), _m(x0 + 2, y1 - 12, GRUIX),
           ramp=BODY, lvl=lambda s, t, P: 3.0 - (1.4 if s > GRUIX - 3 else 0) + (0.8 if abs(t - 46) < 10 or abs(t - 72) < 6 else 0),
           dues_cares=True)
    a, b, c, d = CROP
    e.quad('mobil', _m(a, b), _m(c, b), _m(c, d), _m(a, d), tex=(img, CROP))


def _cortina(e):
    """La cortina, a l'esquerra, a tocar: plecs verticals, gairebé negra, tallada per la vora."""
    def plecs(s, t, P):
        return 1.0 + math.sin(s / 9) * 1.1 + math.sin(s / 23 + 1) * 0.5 - t / 500
    e.quad('cortina', (-250.0, 330.0, 170.0), (-185.0, 330.0, 250.0), (-185.0, -200.0, 250.0), (-250.0, -200.0, 170.0),
           ramp=CURT, lvl=plecs, dues_cares=True)


def escena(cv, dots=0):
    e = Escena(cv, CAM, LLUMS, ambient=AMBIENT)
    _parets(e)
    _llit(e)
    _cortina(e)
    _mobil_mon(e, _mobil(dots))
    # la claror de la pantalla, en pantalla: un halo fred al voltant del mòbil
    u, v, _ = CAM.projecta(_m(320, 123))
    cv.glow(round(u), round(v), 190, (150, 180, 230), 0.06)
    return e


@functools.lru_cache(maxsize=None)
def _base():
    cv = Canvas(light=LIGHT)
    e = escena(cv)
    return cv.img.copy(), e


def bg(cv):
    cv.img.paste(_base()[0])
    cv.P = cv.img.load()


PROPS = {}


def _frames():
    base, e = _base()
    out = []
    for i in range(3):
        img = base.copy()
        img.alpha_composite(e.capa(_mobil(i), {'mobil'}))
        out.append(_diff(img, base))
    return out


ANIMS = {'escrivint': {'frames': _frames, 'frameDuration': 380}}

GEOMETRIA = {'things': {}, 'spawns': {}}
