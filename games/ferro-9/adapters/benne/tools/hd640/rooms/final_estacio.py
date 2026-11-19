"""
Finals 2 i 3 · L'Estació d'Orís. EN 3D (hd640/tres_d.py), a 1×; el dibuix pla de sempre és a
final_estacio_pla_comu.py (d'allà surten les textures: la paret del finestral amb el rètol, la porta del moll, el
pilar 7, les plantes, les caixes i els personatges). final_cargol en continua important peces (del _pla_comu).

El moll de La Gavina en el món on no hi ha hagut mai cap presó, vist des de dalt i de biaix:
  - la càmera, alta a la dreta, mira la cantonada de l'esquerra: la paret del finestral (l'espai, la Terra i la
    Lluna, i a sobre el rètol de bombetes «ESTACIÓ D'ORÍS») fuig cap a la dreta, i la paret de la porta del moll
    (MOLL L-1, amb l'heura penjada) fuig cap a nosaltres per l'esquerra;
  - la llançadora vella, grossa i a prop, a la dreta, en 3/4 damunt les potes: el morro de coure ve cap a nosaltres
    i cap a l'esquerra, cap a on passa l'escena (és la mateixa nau de final_llancadora, `nau`, vista de l'altre
    costat). En Mos descarrega caixes a la cua; les caixes, apilades i girades;
  - el punt d'interès, petit i al fons a l'esquerra: la directora jove a la porta, i la Vet que hi va. La línia
    menta del terra (i les planxes) surt del primer pla i hi porta l'ull;
  - primer pla fosc: la kentia en test a baix a l'esquerra i una pila de caixes a baix a la dreta, tallades per
    la vora;
  - la llum: el sol entra pels vidres i fa clapes en diagonal pel terra polit; la Terra hi posa un to blau; les
    franges del sostre, càlides; racons foscos.
El quadre del text del narrador va al mig (≈145..495 × 140..240): el rètol, la directora i la Vet en queden fora.
Pantalla sencera (sense barra de verbs). Animació: `ambient` (l'onada de llum del rètol, les estrelles i les llums
de ciutat del finestral, la llumeta de la llançadora).
"""
import hd640  # noqa: F401  (abans que cap hd.*: posa la llibreria de dibuix a 640×360)

import math
from functools import lru_cache

import numpy as np
from PIL import Image

from hd.pix import Canvas, Light, B4, W, H, hr, mix, WALNUT, STEEL
import hd640.rooms.final_estacio_pla_comu as pla
from hd640.rooms.final_estacio_pla_comu import (WALLW, DECK, MINT, LEAF, WIN, FLOOR_Y, PANES)
from hd640.rooms.fabrica_moll_pla_comu import pillar
from hd640.rooms import final_llancadora as fl
from hd640.tres_d import Camera, Escena, Llum

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)

# ─── El món ─────────────────────────────────────────────────────────────────
# x a la dreta, y amunt, z cap al fons; 1 unitat = 1 píxel del dibuix pla (un personatge fa ≈110).
ZB = 620.0                      # la paret del finestral
XL = -160.0                     # la paret de la porta
WX0 = XL                        # la paret del finestral, des de la cantonada: hi va el dibuix pla des de x = TX0
TX0 = 150                       # (on comença, al dibuix pla, el tros de paret que es fa servir)
HW = FLOOR_Y                    # alçada de les parets (del terra fins a dalt del dibuix pla, amb el sostre)
CAM = Camera(pos=(260.0, 215.0, 0.0), yaw=-0.48, pitch=0.25, f=420, centre=(320, 140))

LLUMS = [Llum((330.0, 160.0, ZB - 20), 700, 1.6),                 # el finestral (la Terra i el sol)
         Llum((-60.0, 230.0, 300.0), 520, 1.4),                   # les franges del sostre, càlides
         Llum((300.0, 230.0, 120.0), 520, 1.2)]
AMBIENT = -0.4


def _pw(x_flat):
    """La x del món d'un punt de la paret del finestral (x del dibuix pla)."""
    return WX0 + (x_flat - TX0)


# ─── Textures planes ────────────────────────────────────────────────────────

@lru_cache(maxsize=None)
def _paret_fons(t=0.0):
    """La paret del finestral (amb el rètol i les jardineres), tal com es veu de cara: el dibuix pla."""
    cv = Canvas(light=pla.LIGHT)
    pla.ceiling(cv)
    pla.wall(cv, 0, W - 1, 22, FLOOR_Y - 1)
    pla.window(cv, t)
    pla.sign(cv, t)
    pla.planter(cv, 211, 357, 233, seed=1, tall=29, time=t)
    pla.planter(cv, 539, 621, 233, seed=2, tall=32, time=(t * 2) % 1)
    pla.grade(cv)
    return cv.img


@lru_cache(maxsize=None)
def _paret_porta():
    """La paret de la porta del moll (l'heura penjada al costat)."""
    cv = Canvas(light=pla.LIGHT)
    pla.ceiling(cv)
    pla.wall(cv, 0, W - 1, 22, FLOOR_Y - 1)
    pla.door(cv)
    pla.hang_ivy(cv, 300, 29)
    pla.grade(cv)
    return cv.img


def _retall(fn, *a, **k):
    """Un dibuix pla sobre fons transparent, retallat: → (imatge, origen x, origen y)."""
    cv = Canvas(transparent=True)
    fn(cv, *a, **k)
    box = cv.img.getbbox()
    return cv.img.crop(box), box[0], box[1]


@lru_cache(maxsize=None)
def _pilar():
    def d(cv):
        pillar(cv, 60, 22, FLOOR_Y - 1, aged=False)
        cv.rect(48, 171, 72, 179, pla.GOLD, lambda x, y: 4.2 - (y - 171) * 0.3)
        cv.hline(48, 72, 171, pla.GOLD, 5.4)
        cv.hline(48, 72, 179, pla.GOLD, 2.0)
        for x in range(51, 70, 2):
            cv.put(x, 174, pla.GOLD, 1.6)
            if x < 65:
                cv.put(x, 176, pla.GOLD, 1.8)
    return _retall(d)


@lru_cache(maxsize=None)
def _kentia():
    return _retall(pla.big_plant, 120, 200, seed=5, h=80)


@lru_cache(maxsize=None)
def _persona(name, f, talk=False, flip=False):
    from PIL import ImageOps
    img = pla._person(name, f, talk)
    return ImageOps.mirror(img) if flip else img


@lru_cache(maxsize=None)
def _mos():
    """En Mos amb la caixa als braços (els peus, a (100, 150))."""
    cv = Canvas(W, H, transparent=True)
    pla.stamp(cv, pla._person('MOS_FEINA', 'L'), 100, 150)
    pla.held_crate(cv, 81, 98, 24, 17)
    return cv.img.crop((40, 20, 160, 160))


@lru_cache(maxsize=None)
def _caixa_cara(w, h, seed, label=True):
    cv = Canvas(w + 6, h + 4, transparent=True)
    pla.crate(cv, 0, 0, w, h, label=label, seed=seed)
    return cv.img


# ─── El terra ───────────────────────────────────────────────────────────────

def _guia(x, z):
    """La línia menta del terra: de baix a la dreta fins a la porta del moll (distància a la línia)."""
    ax, az, bx, bz = 260.0, -120.0, XL + 10, 250.0
    dx, dz = bx - ax, bz - az
    k = max(0.0, min(1.0, ((x - ax) * dx + (z - az) * dz) / (dx * dx + dz * dz)))
    return math.hypot(x - ax - dx * k, z - az - dz * k), k


def _terra(s, t, P):
    x, z = P[0], P[2]
    pl = math.floor(x / 34)
    fr = x - pl * 34
    seg = math.floor((z + hr(pl, 3) * 90) / 110)
    fz = (z + hr(pl, 3) * 90) - seg * 110
    lvl = 3.4 + (hr(pl, seg, 2) - 0.5) * 0.35 + (hr(int(x) // 6, int(z) // 9, 7) - 0.5) * 0.12
    if fr < 1.1:
        lvl -= 1.3
    elif fr < 2.2:
        lvl += 0.35                                        # el cantell de la planxa, polit
    elif fz < 1.2:
        lvl -= 1.1
    return lvl


def terra(e):
    e.quad('terra', (XL, 0, ZB), (900, 0, ZB), (900, 0, -500), (XL, 0, -500), ramp=DECK, lvl=_terra)
    # la línia menta, damunt (una franja de rajoles en diagonal)
    ax, az, bx, bz = 260.0, -120.0, XL + 10, 250.0
    L = math.hypot(bx - ax, bz - az)
    ux, uz = (bx - ax) / L, (bz - az) / L
    nx, nz = -uz, ux
    for side in (-1, 1):
        o = side * 11
        P0 = (ax + nx * (o - 4), 0.3, az + nz * (o - 4))
        P1 = (ax + nx * (o + 4), 0.3, az + nz * (o + 4))
        P2 = (bx + nx * (o + 4), 0.3, bz + nz * (o + 4))
        P3 = (bx + nx * (o - 4), 0.3, bz + nz * (o - 4))
        e.quad('terra', P3, P2, P1, P0, ramp=MINT, dues_cares=True,
               lvl=lambda s, t, P: 4.4 if ((t * 1.0) // 16) % 2 == 0 else -9,
               forma=lambda s, t: (t // 16) % 2 == 0)


def clapes(e):
    """Les clapes de sol dels vidres, estirades en diagonal pel terra (cap a nosaltres i cap a la dreta)."""
    warm = (255, 228, 170)
    for xa, xb in PANES:
        a, b = _pw(xa + 6), _pw(xb - 6)
        dx, dz = 150.0, -330.0                             # cap on s'estira la clapa
        P0, P1 = (a, 0.4, ZB - 4), (b, 0.4, ZB - 4)
        P2, P3 = (b + dx, 0.4, ZB - 4 + dz), (a + dx, 0.4, ZB - 4 + dz)
        e.claror(P3, P2, P1, P0, warm,
                 lambda s, t, w=b - a: 0.5 * min(1.0, s / 8, (w - s) / 8) * min(1.0, t / 40) * (0.35 + 0.65 * t / 360))
    # el blau de la Terra, arran de la paret del finestral
    e.claror((_pw(400), 0.5, ZB - 140), (_pw(640), 0.5, ZB - 140), (_pw(640), 0.5, ZB - 2), (_pw(400), 0.5, ZB - 2),
             (110, 160, 255), lambda s, t: 0.18 * t / 138)


def ombra_peu(e, x, z, rx, rz=None, k=0.55, dx=-14.0, dz=10.0):
    """L'ombra de contacte (una el·lipse al terra), una mica desplaçada lluny del finestral."""
    rz = rz or rx * 0.6
    cx, cz = x + dx * 0.3, z - dz * 0.3
    e.foscor('ombra', (cx - rx, 0.2, cz + rz), (cx + rx, 0.2, cz + rz), (cx + rx, 0.2, cz - rz), (cx - rx, 0.2, cz - rz),
             lambda s, t: k * max(0.0, 1 - math.hypot(s / rx - 1, t / rz - 1)) * 1.6)


# ─── La llançadora i les caixes ─────────────────────────────────────────────

NAU_NOSE = (200.0, 62.0, 240.0)
NAU_K = 1.6
_d = (-0.48, 0.0, -0.88)
_l = math.sqrt(sum(c * c for c in _d))
NAU_AXIS = tuple(c / _l for c in _d)


def _nau():
    return fl.Nau(NAU_NOSE, NAU_AXIS, roll=0.0, espill=True, k=NAU_K)


def llancadora(e):
    nv = _nau()
    # l'ombra de sota, allargada
    A, B = nv.eix(10), nv.eix(fl.LEN)
    e.foscor('ombra', (A[0] - 30, 0.3, A[2] + 40), (B[0] - 10, 0.3, B[2] + 50), (B[0] + 30, 0.3, B[2] - 40),
             (A[0] + 20, 0.3, A[2] - 50), lambda s, t: 0.55 * min(1.0, s / 30, t / 25))
    # les potes: tres parells, del ventre al terra (amb un peu)
    for u in (40, 110, 175):
        for side in (-1, 1):
            top = nv.p(u, math.pi / 2 + side * 0.7, fl.radi(u) - 2)
            foot = (top[0] - side * 10, 0.0, top[2] - side * 14)
            e.cable('nau', [top, foot], STEEL, 3.0, gruix=4)
            e.caixa('nau', foot[0] - 7, foot[0] + 7, 0, 3, foot[2] - 6, foot[2] + 6, STEEL, 3.2)
    fl.nau(e, nv, vet=False)
    return nv


def caixa(e, sid, cx, cz, w, d, h, ang, seed, y0=0.0, label=True):
    img = _caixa_cara(int(w), int(h), seed, label)
    e.caixa_girada(sid, cx, cz, w, d, h, ang, WALNUT, 4.0, y0=y0, cares={
        'davant': {'tex': (img, (0, 0, w, h))},
        'dreta': {'ramp': WALNUT, 'lvl': lambda s, t, P: 3.2 - (0.9 if int(t) % 9 == 8 else 0)},
        'esquerra': {'ramp': WALNUT, 'lvl': lambda s, t, P: 4.0 - (0.9 if int(t) % 9 == 8 else 0)},
        'dalt': {'ramp': WALNUT, 'lvl': lambda s, t, P: 5.2 - (0.8 if int(s) % 7 == 0 else 0)},
    })


# ─── Composició ────────────────────────────────────────────────────────────

def scene(cv, t=0.0, gent=True):
    cv.S = 1
    e = Escena(cv, CAM, LLUMS, ambient=AMBIENT)
    # parets (la del finestral i la de la porta) i terra
    pf = _paret_fons(t)
    e.quad('paret_fons', (WX0, HW, ZB), (WX0 + (W - TX0), HW, ZB), (WX0 + (W - TX0), 0, ZB), (WX0, 0, ZB),
           tex=(pf, (TX0, 0, W, FLOOR_Y)))
    for k in range(6):                                     # (la paret continua, sense finestral)
        x0 = WX0 + (W - TX0) + k * 100
        e.quad('paret_fons', (x0, HW, ZB), (x0 + 100, HW, ZB), (x0 + 100, 0, ZB), (x0, 0, ZB),
               tex=(pf, (8, 0, 108, FLOOR_Y)))
    pp = _paret_porta()                                    # (de cara a la paret, la cantonada és a la dreta)
    e.quad('paret_porta', (XL, HW, ZB - 400), (XL, HW, ZB), (XL, 0, ZB), (XL, 0, ZB - 400),
           tex=(pp, (11, 0, 411, FLOOR_Y)))               # (la porta, a z ≈ 270; l'heura, entre la porta i la cantonada)
    e.quad('paret_porta', (XL, HW, ZB - 640), (XL, HW, ZB - 400), (XL, 0, ZB - 400), (XL, 0, ZB - 640),
           tex=(pp, (400, 0, 640, FLOOR_Y)))
    e.quad('sostre', (XL, HW, -400), (1400, HW, -400), (1400, HW, ZB), (XL, HW, ZB), ramp=WALLW,
           lvl=lambda s, t, P: 3.4 - (1.4 if (P[0] % 59 < 1.2 or P[2] % 59 < 1.2) else 0) - t * 0.0015)
    terra(e)
    clapes(e)
    # racons foscos: la cantonada i la línia de les parets amb el terra
    e.foscor('ombra', (XL, 0.2, ZB), (XL + 140, 0.2, ZB), (XL + 140, 0.2, ZB - 140), (XL, 0.2, ZB - 140),
             lambda s, t: 0.45 * max(0.0, 1 - math.hypot(s, 140 - t) / 140))
    e.foscor('ombra', (XL, HW, ZB), (XL, HW, ZB - 300), (XL, 0, ZB - 300), (XL, 0, ZB),
             lambda s, t: 0.35 * max(0.0, 1 - s / 300) * (0.5 + t / HW))
    e.foscor('ombra', (XL, 0.3, ZB), (900, 0.3, ZB), (900, 0.3, ZB - 12), (XL, 0.3, ZB - 12), lambda s, t: 0.4 * t / 12)
    # el pilar 7, separat de la paret, i la seva ombra
    img, ox, oy = _pilar()
    px_, pz_ = XL + 45, 470.0
    ombra_peu(e, px_, pz_, 30, 18, 0.5)
    e.sprite('pilar', img, (60 - ox, FLOOR_Y - 1 - oy), (px_, 0, pz_))
    # la directora a la porta, i la Vet que hi va
    if gent:
        for name, f, x, z, flip, talk in (('DIRECTORA_JOVE', 'L', XL + 48, 272.0, False, True),
                                          ('VET', 'L', XL + 40, 186.0, True, False)):
            ombra_peu(e, x, z, 20, 9, 0.6)
            e.sprite(name, _persona(name, f, talk, flip), pla.FEET, (x, 0, z))
    # en Mos, a la cua de la nau, i les caixes descarregades
    caixa(e, 'caixes', 330, 585, 40, 34, 29, 0.35, 1)
    caixa(e, 'caixes', 332, 587, 32, 28, 27, 0.20, 2, y0=29)
    caixa(e, 'caixes', 190, 590, 36, 30, 24, -0.30, 3)
    if gent:
        ombra_peu(e, 255, 600, 20, 9, 0.6)
        e.sprite('mos', _mos(), (60, 130), (255, 0, 600))
    llancadora(e)
    # primer pla: la kentia (a baix a l'esquerra) i una pila de caixes (a baix a la dreta), a contrallum
    img, ox, oy = _kentia()
    e.sprite('primer_pla', img, (120 - ox, 200 - oy), (110, 0, 150), escala_img=1.1)
    caixa(e, 'primer_pla', 330, 285, 44, 38, 32, 0.5, 4)
    caixa(e, 'primer_pla', 334, 289, 36, 30, 28, 0.25, 5, y0=32)
    return e


def _primer_pla_fosc(cv, e):
    """El primer pla, a contrallum: gairebé negre i fred."""
    idx = {i for i, s in enumerate(e.ids) if s == 'primer_pla'}
    P = cv.P
    amo = e.amo
    for Y in range(H):
        for X in range(W):
            if amo[Y * W + X] in idx:
                c = P[X, Y]
                P[X, Y] = (int(c[0] * 0.28 + 4), int(c[1] * 0.30 + 6), int(c[2] * 0.36 + 12), 255)


def _fx(cv):
    """Llum de conjunt: càlida de dalt (el rètol, el sostre) i blavosa cap al finestral; vinyeta."""
    cv.tint(0, 0, W - 1, H - 1, (255, 214, 160), lambda x, y: 0.10 * max(0.0, 1 - y / 220))
    wx, wy, _ = CAM.projecta((_pw(560), 120, ZB))
    cv.tint(0, 0, W - 1, H - 1, (90, 150, 255), lambda x, y: 0.12 * max(0.0, 1 - math.hypot(x - wx, y - wy) / 300))
    pla.vinyeta(cv, 0.5)


def _nau_llums(cv, t=0.0):
    """La llumeta verda de l'aleta (dos cops per bucle) i la claror de la finestreta de la nau."""
    nv = _nau()
    fx, fy, _ = CAM.projecta(nv.p(33, 0.28))
    cv.glow(int(fx), int(fy), 18, (255, 170, 90), 0.3)
    if 0.25 <= t % 0.5 < 0.30:
        x, y, _ = CAM.projecta(nv.p(fl.LEN - 2, -math.pi / 2, fl.radi(fl.LEN - 43) + 22))
        x, y = int(x), int(y)
        cv.flat(x, y, (200, 255, 210))
        cv.flat(x + 1, y, (170, 255, 190))
        cv.glow(x, y, 9, (130, 255, 170), 0.6)


@lru_cache(maxsize=None)
def _render(t=0.0):
    cv = Canvas(light=LIGHT)
    e = scene(cv, t)
    _primer_pla_fosc(cv, e)
    _nau_llums(cv, t)
    _fx(cv)
    return cv.img


def bg(cv, t=0.0):
    cv.img.paste(_render(t))
    cv.P = cv.img.load()


PROPS = {}


def _ambient_frames(n=16):
    B = np.asarray(_render(0.0))
    frames = []
    for i in range(n):
        A = np.array(_render(i / n))
        A[~(A != B).any(axis=2)] = 0
        frames.append(Image.fromarray(A, 'RGBA'))
    return frames


ANIMS = {'ambient': {'frames': _ambient_frames, 'frameDuration': 110}}
