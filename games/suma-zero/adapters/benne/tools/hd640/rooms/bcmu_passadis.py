"""
El passadís del tercer pis del BCMU (Escena 5, l'Iri). EN 3D (hd640/tres_d.py), a 1×.

Una càmera alta, a la dreta, que mira de biaix la cantonada del fons a l'esquerra, on s'acaba el passadís:
  - a la paret del fons de l'esquerra, en escorç, la **porta vella de l'escala** (fusta de 1958, el pany de la clau
    grossa i el rètol ESCALA);
  - a la paret llarga, que fuig cap a l'esquerra: la **càmera 1** amb l'adhesiu «ZONA NETEJA · NO ES GRAVA», la
    **porta de neteja**, el **quadre** «EFICIÈNCIA», el ganxo de l'**extintor**, l'**estació del tub**, la
    **porta VIP** de caoba amb la catifa vermella i els poms de llautó, l'**ascensor de servei** i la **càmera 2**;
  - el passadís continua a la dreta, fora del quadre; la catifa blau marí amb el rombe d'or fuig cap a la cantonada;
  - un **banc d'espera** de cuir, separat de la paret i girat (s'hi passa per darrere), el **cartell** de terra i la
    **galleda** de la neteja, al costat de la porta;
  - primer pla: una jardinera amb un ficus en silueta a baix a l'esquerra i una columna fosca a la vora dreta.

Tot el detall de les parets ve del dibuix pla de sempre (bcmu_passadis_pla_comu.py), projectat; el cartell i la
galleda són el dibuix pla dret (sprites), i les càmeres i els decorats de la paret es projecten amb `capa`.
Damunt de tot, la llum de Suma Zero (hd640/llum.py): els fluorescents, el llum càlid de la porta VIP i la corba de to.

El món: x a la dreta (0 = la paret de l'escala), y amunt (0 = el terra), z cap al fons (300 = la paret llarga);
1 unitat = 1 píxel de sala a la distància on un personatge fa ≈111 px (escala 1).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from hd640 import llum
from hd.pix import Canvas, Light, W, H, hr
from hd.rooms.comu import _diff
from hd.rooms.exterior import fbm
from hd640.rooms import bcmu_passadis_pla_comu as PL
from hd640.rooms.bcmu_passadis_pla_comu import PAINT, BRASS, NAVYB, CARPET, CHROME
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
ZW = 300                                           # la paret llarga (la del fons)
FY0 = 20                                           # al dibuix pla, on comença la paret (a dalt, el sostre)
HW = PL.FLOOR_Y - FY0                              # l'alçada de les parets: 180
XC = 100                                           # al dibuix pla, la cantonada: a l'esquerra, la paret de l'escala
LL = 636                                           # l'amplada de la paret llisa (12 plafons de l'arrimador)
XR = W - XC + 2 * LL                               # on s'acaba la paret llarga, a la dreta (fora de la pantalla)
BENCH = (236, 176, 92, 32, 0.38)                   # el banc: x, z del centre, llarg, fons, gir
PLANT = (44, 30)                                   # la jardinera del primer pla (x, z)
COLUMN = (506, 144)                                # la columna del primer pla (x, z)
CARTELL = (52, 268)                                # el cartell de terra (x, z dels peus)
GALLEDA = (184, 276)                               # la galleda (x, z)


def _w(fx):
    """Una x del dibuix pla de la paret llarga → la x del món."""
    return fx - XC


def _wz(fx):
    """Una x del dibuix pla de la paret de l'escala → la z del món."""
    return ZW - XC + fx


def _y(fy):
    """Una y del dibuix pla (el terra, a 200) → l'alçada del món."""
    return PL.FLOOR_Y - fy


def _fw(fx, fy):
    """Un punt del dibuix pla de les parets → el punt del món (a la paret de l'escala o a la llarga)."""
    if fx < XC:
        return (0, _y(fy), _wz(fx))
    return (_w(fx), _y(fy), ZW)


CAM = Camera(pos=(360, 175, -230), yaw=-0.26, pitch=0.17, f=460, centre=(320, 88))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)  # (la llum és la del món: la de l'Escena)
TUBS = [(_w(x), HW - 4, ZW - 60) for x in PL.TUBES] + [(-40 + 0, HW - 4, ZW - 180), (720, HW - 4, ZW - 60)]
VIP_C = (_w(477), _y(80), ZW - 30)                 # el llum càlid de sobre la porta VIP
LLUMS = [Llum(p, 260, 2.2, power=1.6) for p in TUBS] + [Llum(VIP_C, 120, 1.0, power=1.6)]


# ─── Les textures: el dibuix pla de sempre ───────────────────────────────────

LIGHT_TEX = Light(ambient=-0.25, vignette=None, floor_fade=None)
for _x in PL.TUBES:
    LIGHT_TEX.point(_x, 5, r=200, k=0.8, squash=0.8, power=1.4)
LIGHT_TEX.point(477, 80, r=80, k=0.5, squash=1.0, power=2.0)


def _paret_sense_cameres():
    """Les parets planes, de cara, sense les càmeres: les portes, el quadre, el tub, l'ascensor."""
    cv = Canvas(light=LIGHT_TEX)
    PL.wall(cv)
    PL.porta_escala(cv)
    PL.adhesiu(cv)
    PL.porta_neteja(cv)
    PL.quadre(cv)
    PL.extintor_buit(cv)
    PL.tub_station(cv, 392, 93, 417, 150)
    PL.porta_vip(cv, catifa=False)
    PL.ascensor(cv)
    return cv


@functools.lru_cache(maxsize=None)
def _paret_buida():
    return _paret_sense_cameres().img


def _paret(a1=0, a2=0, led=True, extra=()):
    """Les parets amb les càmeres (amb un angle) i, si cal, decorats plans damunt (`extra`: funcions de dibuix)."""
    cv = Canvas(light=LIGHT_TEX, img=_paret_buida().copy())
    PL.cameres(cv, a1, a2, led)
    for fn in extra:
        fn(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _paret_base():
    return _paret()


@functools.lru_cache(maxsize=None)
def _llisa():
    """La paret llisa (pintura i arrimador, sense pilastres): per allargar les parets fora del dibuix pla."""
    cv = Canvas(light=LIGHT_TEX)
    PL.wall(cv, pilastres=False)
    return cv.img


@functools.lru_cache(maxsize=None)
def _textures():
    return {'paret': _paret_base(), 'llisa': _llisa()}


@functools.lru_cache(maxsize=None)
def _ficus_img():
    """Un ficus en silueta (el primer pla): tiges fosques i una copa espessa de fulles allargades, amb el cantell de
    la dreta que agafa la llum del passadís. A escala 1 (fa 130 d'alt), sobre transparent; el peu, a (60, 129)."""
    from PIL import Image
    img = Image.new('RGBA', (120, 130), (0, 0, 0, 0))
    P = img.load()
    FULLA = [(3, 8, 5), (6, 14, 9), (10, 22, 14), (16, 32, 20), (26, 46, 30), (40, 64, 42)]

    def put(x, y, lvl):
        if 0 <= x < 120 and 0 <= y < 130:
            P[x, y] = FULLA[max(0, min(len(FULLA) - 1, int(lvl)))] + (255,)
    for tx, ty in ((40, 40), (80, 30), (60, 14), (28, 70), (94, 64)):                # les tiges
        for i in range(80):
            t = i / 79
            for d in (0, 1):
                put(round(60 + d + (tx - 60) * t), round(129 - (129 - ty) * t), 0.4)
    for i in range(260):                                                             # les fulles
        a = hr(i, 1) * 2 * math.pi
        r = hr(i, 2) ** 0.5 * 50
        cx, cy = 60 + math.cos(a) * r, 58 + math.sin(a) * r * 0.95
        ang = hr(i, 3) * math.pi
        L, Wd = 6 + hr(i, 4) * 4, 2.4
        ca, sa = math.cos(ang), math.sin(ang)
        for yy in range(-9, 10):
            for xx in range(-9, 10):
                lu, lv = (xx * ca + yy * sa) / L, (-xx * sa + yy * ca) / Wd
                if lu * lu + lv * lv <= 1:
                    lvl = 1.4 + (cx - 60) / 34 + lu * 0.7 - (0.6 if abs(lv) < 0.3 else 0) - (cy - 30) / 90
                    put(round(cx + xx), round(cy + yy), lvl)
    return img


# ─── Les superfícies ────────────────────────────────────────────────────────

def _or(x, z):
    """Si el punt (x, z) del terra és a la línia d'or dels rombes (o al punt del mig)."""
    u, v = (x % 48) - 24, (z % 36) - 18
    d = abs(u) / 24 + abs(v) / 18
    return 0.95 < d < 1.05 or d < 0.08


def _moqueta(s, t, P):
    """La moqueta blau marí, en coordenades del món: gastada pel mig del passadís, amb el pèl que fa aigües."""
    x, z = P[0], P[2]
    n = (fbm(x / 30, z / 20, 4) - 0.5) * 0.6 + (hr(int(x // 2), int(z // 2), 6) - 0.5) * 0.3
    worn = max(0.0, 1 - abs(z - (ZW - 100)) / 70) * 0.5
    return 3.0 + n + worn


def _terra(e, zn):
    """La moqueta i, damunt, el rombe d'or del banc (els rombes s'empetiteixen cap al fons)."""
    e.quad('terra', (-400, 0, ZW), (XR, 0, ZW), (XR, 0, zn), (-400, 0, zn), ramp=NAVYB, lvl=_moqueta)
    e.quad('terra', (-400, 0.05, ZW), (XR, 0.05, ZW), (XR, 0.05, zn), (-400, 0.05, zn), ramp=BRASS,
           lvl=lambda s, t, P: 1.6 + (hr(int(P[0]), int(P[2]), 7) - 0.5) * 0.6,
           forma=lambda s, t: _or(s - 400, ZW - t))


def escena(cv, tex, estat=frozenset()):
    """Tota la sala, de lluny a prop. `estat`: res de moment (els decorats es fan amb capes). → l'Escena."""
    e = Escena(cv, CAM, LLUMS, ambient=-0.9)
    zn = CAM.pos[2] + 60
    paret, llisa = tex['paret'], tex['llisa']
    # el sostre, fosc (gairebé no es veu)
    e.quad('sostre', (0, HW, zn), (XR, HW, zn), (XR, HW, ZW), (0, HW, ZW), ramp=PAINT, lvl=1.4, dues_cares=True)
    # la paret de l'escala (x = 0): el dibuix pla (x 0..100) a tocar de la cantonada; cap a la càmera, paret llisa
    e.quad('paret_esq', (0, HW, ZW - XC), (0, HW, ZW), (0, 0, ZW), (0, 0, ZW - XC), tex=(paret, (0, FY0, XC, PL.FLOOR_Y)))
    for k in range(2):
        z1 = ZW - XC - k * LL
        e.quad('paret_esq_prop', (0, HW, z1 - LL), (0, HW, z1), (0, 0, z1), (0, 0, z1 - LL),
               tex=(llisa, (0, FY0, LL, PL.FLOOR_Y)))
    # la paret llarga (z = 300): el dibuix pla (x 100..640) i, a la dreta, més paret llisa
    e.quad('paret_fons', (0, HW, ZW), (W - XC, HW, ZW), (W - XC, 0, ZW), (0, 0, ZW), tex=(paret, (XC, FY0, W, PL.FLOOR_Y)))
    for k in range(2):
        x0 = W - XC + k * LL
        e.quad('paret_fons_dreta', (x0, HW, ZW), (x0 + LL, HW, ZW), (x0 + LL, 0, ZW), (x0, 0, ZW),
               tex=(llisa, (0, FY0, LL, PL.FLOOR_Y)))
    # el terra
    _terra(e, zn)
    # la catifa vermella de la porta VIP, amb el galó d'or, i els poms de llautó
    vx0, vx1 = _w(428) - 14, _w(527) + 14
    cz0 = ZW - 52
    e.quad('catifa', (vx0, 0.3, ZW), (vx1, 0.3, ZW), (vx1, 0.3, cz0), (vx0, 0.3, cz0), ramp=CARPET,
           lvl=lambda s, t, P: 3.2 + (hr(int(s // 2), int(t), 5) - 0.5) * 0.5 - t * 0.01)
    e.quad('catifa', (vx0, 0.4, ZW), (vx1, 0.4, ZW), (vx1, 0.4, cz0), (vx0, 0.4, cz0), ramp=BRASS,
           lvl=lambda s, t, P: 3.6 if (s < 1.5 or s > vx1 - vx0 - 1.5 or t > ZW - cz0 - 1.5) else 2.4,
           forma=lambda s, t: s < 4 or s > vx1 - vx0 - 4 or t > ZW - cz0 - 4)
    # la foscor: al llarg de la paret, a la cantonada i sota el sostre
    e.foscor('racons', (-400, 0.5, ZW), (XR, 0.5, ZW), (XR, 0.5, zn), (-400, 0.5, zn),
             lambda s, t: max(0.5 * max(0.0, 1 - t / 26), 0.45 * max(0.0, 1 - (s - 400) / 30) if s >= 400 else 0.45))
    e.foscor('cantonada', (0, HW, ZW - 0.5), (70, HW, ZW - 0.5), (70, 0, ZW - 0.5), (0, 0, ZW - 0.5),
             lambda s, t: 0.5 * max(0.0, 1 - s / 70))
    e.foscor('cantonada2', (0.5, HW, ZW - 70), (0.5, HW, ZW), (0.5, 0, ZW), (0.5, 0, ZW - 70),
             lambda s, t: 0.5 * max(0.0, 1 - (70 - s) / 70))
    e.foscor('sostre_fosc', (-400, HW - 0.5, ZW - 0.6), (XR, HW - 0.5, ZW - 0.6), (XR, 0, ZW - 0.6), (-400, 0, ZW - 0.6),
             lambda s, t: 0.35 * max(0.0, 1 - t / 40))
    e.foscor('sostre_fosc2', (0.6, HW - 0.5, -400), (0.6, HW - 0.5, ZW), (0.6, 0, ZW), (0.6, 0, -400),
             lambda s, t: 0.35 * max(0.0, 1 - t / 40))
    # els bassals de llum dels fluorescents al terra
    for tx, _, tz in TUBS:
        e.claror((tx - 90, 0.6, tz + 90), (tx + 90, 0.6, tz + 90), (tx + 90, 0.6, tz - 90), (tx - 90, 0.6, tz - 90),
                 (190, 200, 230), lambda s, t: 0.16 * max(0.0, 1 - math.hypot(s - 90, (t - 90) * 1.2) / 90))
    e.claror((vx0 - 20, 0.7, ZW), (vx1 + 20, 0.7, ZW), (vx1 + 20, 0.7, ZW - 90), (vx0 - 20, 0.7, ZW - 90),
             (255, 200, 130), lambda s, t: 0.18 * max(0.0, 1 - abs(s - 80) / 80) * max(0.0, 1 - t / 90))
    # els poms de llautó de la catifa
    for px in (vx0 - 6, vx1 + 6):
        pz = cz0 + 4
        e.foscor('ombra_pom', (px - 10, 0.8, pz + 6), (px + 10, 0.8, pz + 6), (px + 10, 0.8, pz - 6), (px - 10, 0.8, pz - 6),
                 lambda s, t: 0.5 * max(0.0, 1 - ((s - 10) / 10) ** 2 - ((t - 6) / 6) ** 2))
        e.caixa('poms', px - 5, px + 5, 0, 2, pz - 5, pz + 5, BRASS, 3.0)
        e.tub('poms', (px, 2, pz), (px, 38, pz), 1.6, BRASS, 3.2)
        e.tub('poms', (px, 38, pz), (px, 43, pz), 3.0, BRASS, 3.8)
    # el banc d'espera, de cuir, separat de la paret i girat: el seient, el respatller i les potes de crom
    bx, bz, bl, bd, ba = BENCH
    e.foscor('ombra_banc', (bx - 56, 0.8, bz + 34), (bx + 56, 0.8, bz + 34), (bx + 56, 0.8, bz - 34), (bx - 56, 0.8, bz - 34),
             lambda s, t: 0.55 * max(0.0, 1 - ((s - 56) / 54) ** 2 - ((t - 34) / 30) ** 2) * 1.4)
    c, s_ = math.cos(ba), math.sin(ba)

    def Pb(lx, lz):
        return bx + lx * c - lz * s_, bz + lx * s_ + lz * c
    for lx in (-bl / 2 + 6, bl / 2 - 6):
        for lz in (-bd / 2 + 4, bd / 2 - 4):
            px, pz = Pb(lx, lz)
            e.caixa('banc', px - 1.5, px + 1.5, 0, 20, pz - 1.5, pz + 1.5, CHROME, 3.4)
    cuir = [(16, 8, 6), (36, 18, 12), (62, 32, 20), (92, 50, 32), (130, 76, 50)]

    def capitons(s, t, P):
        v = 2.4 + (fbm(s / 10, t / 6, 2) - 0.5) * 0.6
        if int(s) % 14 == 0 or int(t) % 14 == 0:
            v -= 0.8                                                    # les costures del capitonat
        return v
    e.caixa_girada('banc', bx, bz, bl, bd, 7, ba, cuir, 1.6, y0=20,
                   cares={'dalt': {'ramp': cuir, 'lvl': capitons}, 'davant': {'ramp': cuir, 'lvl': 1.4},
                          'esquerra': {'ramp': cuir, 'lvl': 1.0}, 'dreta': {'ramp': cuir, 'lvl': 1.8}})
    # una revista oblidada damunt el seient
    rx, rz = Pb(-18, -2)
    e.caixa_girada('banc', rx, rz, 16, 12, 0.8, ba + 0.3, [(20, 20, 30), (50, 60, 90), (110, 120, 150), (160, 160, 170)],
                   2.6, y0=27, cares={'dalt': {'ramp': [(20, 20, 30), (50, 60, 90), (110, 120, 150), (160, 160, 170)],
                                               'lvl': lambda s, t, P: 3.0 if t < 4 else (1.4 if int(t) % 3 == 0 else 2.2)}})
    # primer pla: la jardinera amb el ficus (en silueta), a baix a l'esquerra, i una columna fosca a la dreta
    FOSC = [(4, 4, 8), (9, 9, 15), (15, 15, 23), (22, 22, 32), (31, 31, 42), (42, 42, 54)]
    FULLA = [(2, 6, 4), (6, 13, 9), (10, 21, 14), (15, 30, 20), (22, 42, 28), (32, 56, 36)]
    jx, jz = PLANT
    e.caixa_girada('primer_pla', jx, jz, 50, 50, 44, 0.3, FOSC, 1.6,
                   cares={'dalt': {'ramp': FOSC, 'lvl': 0.6},
                          'davant': {'ramp': FOSC, 'lvl': lambda s, t, P: 1.4 + (1.0 if t < 3 else 0)},
                          'dreta': {'ramp': FOSC, 'lvl': lambda s, t, P: 2.2 + (1.0 if t < 3 else 0)}})
    e.sprite('primer_pla', _ficus_img(), (60, 129), (jx, 40, jz))
    cx_, cz_ = COLUMN
    e.caixa('primer_pla', cx_ - 18, cx_ + 18, 0, HW, cz_ - 18, cz_ + 18, FOSC, 1.4,
            cares={'davant': {'ramp': FOSC, 'lvl': lambda s, t, P: 1.6 + (0.8 if s < 3 else 0)},
                   'esquerra': {'ramp': FOSC, 'lvl': lambda s, t, P: 2.4 + (0.6 if t > HW - 8 else 0)}})
    return e


# ─── Composició i llum ──────────────────────────────────────────────────────

def _proj(P):
    u, v, _ = CAM.projecta(P)
    return u, v


def _fx():
    light = []
    for P in TUBS[:3]:
        x, y = _proj(P)
        light.append(llum.wash(x, y + 30, 200, (200, 215, 255), k=0.25, air=0.02, squash=0.9))
    vx, vy = _proj(VIP_C)
    light.append(llum.wash(vx, vy, 90, (255, 200, 130), k=0.5, air=0.05, squash=1.0))
    tone = [llum.grade(contrast=1.08, pivot=50, sat=1.12, lift=(2, 2, 8))]
    bloom = [llum.bloom(thr=215, radii=((2, 0.4), (8, 0.25)))]
    return light, bloom, tone


def _render(tex=None, estat=frozenset()):
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


def _fotograma(capes):
    """El fons amb unes capes damunt, amb la llum, menys el fons amb la llum."""
    img, _ = _base()
    img = img.copy()
    for c in capes:
        img.alpha_composite(c)
    return _diff(_amb_llum(img), _base_llum())


def _capa_paret(*fns):
    """Un decorat dibuixat pla damunt la paret (amb les càmeres de sempre), projectat."""
    _, e = _base()
    return e.capa(_paret(extra=fns), {'paret_fons', 'paret_esq'})


def _drets(img, peu_img, peu, escala_img=1.0):
    """Un dibuix pla dret damunt el terra (el cartell, la galleda), amb una ombra de contacte, en una capa: on res de
    l'escena no hi és més a prop (només el primer pla, que és una capa del davant)."""
    from PIL import Image
    from pixels import nearest
    k = CAM.escala(peu) * escala_img
    u, v, _ = CAM.projecta(peu)
    w, h = max(1, round(img.width * k)), max(1, round(img.height * k))
    im = nearest(img, (w, h)) if k >= 1 else img.resize((w, h), Image.Resampling.BOX)
    ox, oy = round(u - peu_img[0] * k), round(v - peu_img[1] * k)
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    dst = out.load()
    rx, ry = w * 0.62, max(2.0, w * 0.16)
    for Y in range(int(v - ry), int(v + ry) + 1):
        for X in range(int(u - rx), int(u + rx) + 1):
            d = ((X - u) / rx) ** 2 + ((Y - v) / ry) ** 2
            if d < 1 and 0 <= X < W and 0 <= Y < H:
                dst[X, Y] = (6, 6, 14, int(150 * (1 - d) ** 0.7))
    out.alpha_composite(im, (ox, oy))
    return out


def _cartell_img():
    cv = Canvas(light=LIGHT_TEX, transparent=True)
    PL._cartell(cv, 40, 60)
    return cv.img.crop((24, 16, 57, 61))                       # (el peu, a (16, 44) del retall)


def _galleda_img():
    cv = Canvas(light=LIGHT_TEX, transparent=True)
    PL.galleda(cv, at=(40, 60))
    return cv.img.crop((27, 30, 54, 61))                       # (el peu, a (13, 30))


def _prop_cartell(cv):
    cv.img.alpha_composite(_fotograma([_drets(_cartell_img(), (16, 44), (CARTELL[0], 0, CARTELL[1]))]))
    cv.P = cv.img.load()


def _prop_galleda(cv):
    cv.img.alpha_composite(_fotograma([_drets(_galleda_img(), (13, 30), (GALLEDA[0], 0, GALLEDA[1]))]))
    cv.P = cv.img.load()


def _prop_paret(fn):
    def draw(cv):
        cv.img.alpha_composite(_fotograma([_capa_paret(fn)]))
        cv.P = cv.img.load()
    return draw


PROPS = {'cartell': _prop_cartell, 'galleda': _prop_galleda, 'extintor': _prop_paret(PL.extintor),
         'camera1_tapada': _prop_paret(PL.camera1_tapada), 'camera2_tapada': _prop_paret(PL.camera2_tapada)}


# ─── Les càmeres que escombren ─────────────────────────────────────────────

def _frames():
    _, e = _base()
    n = len(PL.CAM_ANGLES)
    out = []
    for i in range(n):
        a1, a2 = PL.CAM_ANGLES[i], PL.CAM_ANGLES[(i + n // 2) % n]
        capa = e.capa(_paret(a1, a2, led=(i % 4 < 2)), {'paret_fons', 'paret_esq'})
        out.append(_fotograma([capa]))
    return out


ANIMS = {'cameres': {'frames': _frames, 'frameDuration': 230}}


# ─── Capes del davant ───────────────────────────────────────────────────────

def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


def _baseline_banc():
    bx, bz, bl, bd, ba = BENCH
    c, s_ = math.cos(ba), math.sin(ba)
    return max(_p(bx + lx * c - lz * s_, bz + lx * s_ + lz * c)[1] for lx in (-bl / 2, bl / 2) for lz in (-bd / 2, bd / 2)) - 6


# El primer pla (sempre davant) i el banc (qui hi passa per darrere, hi queda darrere).
FRONT = [
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20},
    {'id': 'davant_banc', 'mask': _amo({'banc'}), 'baseline': _baseline_banc(), 'zIndex': 20},
]


# ─── Geometria (coordenades de sala, projectades) ────────────────────────────

def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


def _rect_pla(x0, y0, x1, y1):
    """Un rectangle del dibuix pla de les parets → el rectangle de pantalla que ocupa (amb tots els cantons)."""
    return _rect_mon(*[_fw(x, y) for x in (x0, x1) for y in (y0, y1)] + ([_fw(XC, y0), _fw(XC, y1)] if x0 < XC < x1 else []))


def _rect_dret(img, peu_img, peu):
    k = CAM.escala(peu)
    u, v, _ = CAM.projecta(peu)
    return (round(u - peu_img[0] * k), round(v - peu_img[1] * k), round(u + (img.width - peu_img[0]) * k),
            round(v + (img.height - peu_img[1]) * k))


def _talla(poly, a, b, c):
    """Retalla el polígon (de pantalla) pel semiplà a·u + b·v + c ≥ 0."""
    out = []
    for P, Q in zip(poly, poly[1:] + poly[:1]):
        fp, fq = a * P[0] + b * P[1] + c, a * Q[0] + b * Q[1] + c
        if fp >= 0:
            out.append(P)
        if (fp >= 0) != (fq >= 0):
            k = fp / (fp - fq)
            out.append((P[0] + (Q[0] - P[0]) * k, P[1] + (Q[1] - P[1]) * k))
    return out


def _escala_a(v):
    """L'escala d'un personatge amb els peus a la y de pantalla `v` (al terra, la profunditat només depèn de v)."""
    lo, hi = -200.0, 2000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.projecta((260, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((260, 0, (lo + hi) / 2))


def _v_escala(k):
    """La y de pantalla on un personatge fa escala `k`."""
    lo, hi = 0.0, float(BOTTOM)
    for _ in range(40):
        m = (lo + hi) / 2
        if _escala_a(m) < k:
            lo = m
        else:
            hi = m
    return lo


# El terra on es camina: al món, de la paret de l'escala fins a la dreta, arran de la paret llarga; retallat per la
# pantalla i per on un personatge passaria d'escala 1,2 (més a prop, el primer pla).
WALK_MON = [(14, 284), (700, 284), (700, -100), (14, -100)]
V_MAX = _v_escala(1.2)
_WALK = [_p(x, z) for x, z in WALK_MON]
for _a, _b, _c in ((1, 0, -4), (-1, 0, W - 5), (0, -1, V_MAX)):
    _WALK = _talla(_WALK, _a, _b, _c)
_WALK = [(round(u), round(v)) for u, v in _WALK]
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)


def _forat_banc():
    bx, bz, bl, bd, ba = BENCH
    c, s_ = math.cos(ba), math.sin(ba)
    return [_p(bx + lx * c - lz * s_, bz + lx * s_ + lz * c) for lx, lz in
            ((-bl / 2 - 4, -bd / 2 - 4), (bl / 2 + 4, -bd / 2 - 4), (bl / 2 + 4, bd / 2 + 4), (-bl / 2 - 4, bd / 2 + 4))]


GEOMETRIA = {
    'things': {
        'porta_escala': {'rect': _rect_pla(14, 62, 85, 200), 'walk': _p(14, _wz(50))},
        'camera1': {'rect': _rect_pla(140, 22, 184, 51), 'walk': _p(_w(165), ZW - 40)},
        'porta_neteja': {'rect': _rect_pla(196, 71, 271, 200), 'walk': _p(_w(235), ZW - 30)},
        'cartell': {'rect': _rect_dret(_cartell_img(), (16, 44), (CARTELL[0], 0, CARTELL[1])),
                    'walk': _p(CARTELL[0] + 6, CARTELL[1] - 34)},
        'galleda': {'rect': _rect_dret(_galleda_img(), (13, 30), (GALLEDA[0], 0, GALLEDA[1])),
                    'walk': _p(GALLEDA[0] + 4, GALLEDA[1] - 34)},
        'extintor': {'rect': _rect_pla(351, 125, 377, 176), 'walk': _p(_w(364), ZW - 34)},
        'tub': {'rect': _rect_pla(390, 93, 422, 150), 'walk': _p(_w(405), ZW - 34)},
        'porta_vip': {'rect': _rect_pla(428, 54, 527, 200), 'walk': _p(_w(477), ZW - 70)},
        'ascensor': {'rect': _rect_pla(531, 62, 601, 200), 'walk': _p(_w(560), ZW - 34)},
        'camera2': {'rect': _rect_pla(590, 22, 628, 51), 'walk': _p(_w(600), ZW - 40)},
    },
    'spawns': {'iri': _p(60, 190), 'neta': _p(_w(240), ZW - 46)},
    'walkable': _WALK,
    'forats': [_forat_banc()],
    'floorSquash': 0.42,
    # L'ombra de contacte: la llum dominant són els fluorescents del sostre, al llarg del passadís; curta i cap avall.
    'characterShadow': {'enabled': True, 'color': '#06060e', 'alpha': 0.42, 'squash': 0.4, 'core': 0.6,
                        'light': {'x': _p(_w(333), ZW - 60)[0], 'y': _p(_w(333), ZW - 60)[1], 'stretch': 0.4,
                                  'reach': 200}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    # la llum de la sala sobre els personatges, en temps d'execució
    'characterLights': {
        'ambient': '#b4b8c8',                                                           # oficina, llum freda
        'lights': [
            {'x': _p(P[0], P[2], P[1])[0], 'y': _p(P[0], P[2], P[1])[1], 'radius': 220, 'color': '#e6ecff',
             'intensity': 0.5} for P in TUBS[:3]] + [
            {'x': _p(VIP_C[0], VIP_C[2], VIP_C[1])[0], 'y': _p(VIP_C[0], VIP_C[2], VIP_C[1])[1], 'radius': 120,
             'color': '#ffc882', 'intensity': 0.6}],
    },
}
