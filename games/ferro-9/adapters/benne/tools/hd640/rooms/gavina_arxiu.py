"""
Arxiu (La Gavina, Vet): cent vint anys de paperassa sota el moll de l'hangar. EN 3D (hd640/tres_d.py), a 1×.

Una càmera alta que mira de biaix la cantonada del fons a l'esquerra (com el despatx de la referència de l'habitació
404, docs/referencies/sala-habitacio-404.png):
  - a la paret de l'esquerra, en escorç, l'**escala** que puja al moll de l'hangar (la sortida), amb la claror freda
    que baixa per la trapa i s'escampa pel terra;
  - a la paret del fons, els quatre **arxivadors** amb volum (el calaix de les cartes, obert, en surt), les caixes al
    damunt, la **canonada de coure** del despatx del director amb el manòmetre, els prestatges de caixes, el rètol
    i el termòstat;
  - la **taula dels expedients**, separada de la paret i girada, amb les carpetes, la tassa i el flexo (s'hi passa
    per darrere); la **taula de llum** amb els plànols, també girada, amb el vidre inclinat que fa la llum cian;
  - primer pla: una pila de caixes d'arxiu en silueta a baix a l'esquerra i un pilar a la dreta.

Tot el detall ve del dibuix pla de sempre (gavina_arxiu_pla_comu.py, partit en peces), projectat; l'animació (la
pols al flexo, la bombeta que fa figa, la línia d'escaneig, el pilot del termòstat) també, per les mateixes
superfícies. La carpeta caiguda és el seu dibuix pla, dret, a terra (en surt la diferència amb el fons).

El món: x a la dreta (0 = la paret de l'escala), y amunt (0 = el terra), z cap al fons (300 = la paret del fons);
1 unitat = 1 píxel de sala a la distància on un personatge fa ≈110 px (escala 1).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from PIL import Image

from hd.pix import Canvas, Light, W, H, STEEL, PANEL, MANILA, COPPER, PAPER, IRON
from hd.rooms.gavina_arxiu import OLIVE
from hd640.rooms import gavina_arxiu_pla_comu as PL
from hd640.rooms.gavina_passadis_pla_comu import HULL, DECK, diff
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
ZW = 300                                           # la paret del fons
HW = PL.FLOOR_Y                                    # l'alçada de les parets (el dibuix pla fa 205 fins al terra)
XL = 100                                           # al dibuix pla, la cantonada: a l'esquerra, la paret de l'escala
XR = 820                                           # on s'acaba la paret del fons (fora de la pantalla)
CABS = [(107, 147), (149, 189), (192, 232), (235, 271)]   # els arxivadors (x del dibuix pla)
CT = 67                                            # la tapa dels arxivadors (y del dibuix pla)
CAB_D = 44                                         # el fons dels arxivadors
TOPS = ((109, 139, 13), (141, 168, 11), (200, 237, 15), (243, 267, 9))   # les caixes de damunt: x0, x1, alt
SHELVES = (93, 128)                                # els prestatges (y del dibuix pla)
DESK = (262, 214, 136, 50, 48, 0.26)               # la taula dels expedients: x, z del centre, ample, fons, alt, gir
LTAB = (452, 226, 150, 54, 0.32)                   # la taula de llum: x, z del centre, ample, fons, gir
LTAB_H = (44, 60)                                  # l'alçada del vidre: davant i darrere
PIPE_X = 186.5                                     # la canonada de coure (x del món)
CARPETA = (148, 238)                               # on cau la carpeta (x, z)
BOXES = (34, -46)                                  # la pila de caixes del primer pla (x, z)
PILLAR = (508, -14)                                # el pilar del primer pla


def _w(fx):
    """Una x del dibuix pla de la paret del fons → la x del món."""
    return fx - XL


def _wz(fx):
    """Una x del dibuix pla de la paret de l'escala → la z del món."""
    return ZW - XL + fx


def _y(fy):
    """Una y del dibuix pla (el terra, a 205) → l'alçada del món."""
    return HW - fy


CAM = Camera(pos=(440, 175, -320), yaw=-0.36, pitch=0.10, f=450, centre=(320, 84))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)  # (la llum és la del món: la de l'Escena)


def _lp(lx, y, lz, box):
    """Un punt d'un moble girat (lx al llarg, lz cap al fons) → el món. `box` = (x, z, ..., gir)."""
    cx, cz, a = box[0], box[1], box[-1]
    c, s_ = math.cos(a), math.sin(a)
    return (cx + lx * c - lz * s_, y, cz + lx * s_ + lz * c)


FLEXO = _lp(30, DESK[4] + 26, 2, DESK)             # la bombeta del flexo
LTAB_C = _lp(0, LTAB_H[1], 0, LTAB)                # el centre del vidre de la taula de llum
LLUMS = [Llum(FLEXO, 190, 2.0, power=1.5),                                   # el flexo
         Llum(LTAB_C, 170, 1.4, power=1.5),                                  # la taula de llum
         Llum((10, 170, _wz(50)), 200, 1.6, power=1.4),                      # la claror de l'escala de l'hangar
         Llum((_w(330), HW - 10, ZW - 40), 520, 0.9, power=1.3)]             # el llum del sostre, fluix


def _h(*a):
    """Soroll determinista (0..1) ràpid, per als píxels de les superfícies procedurals."""
    n = 0x345678
    for v in a:
        n = ((n ^ (int(v) & 0xFFFFFFFF)) * 1000003) & 0xFFFFFFFF
    n ^= n >> 13
    n = (n * 0x5BD1E995) & 0xFFFFFFFF
    n ^= n >> 15
    return (n & 0xFFFF) / 65535


# ─── Les textures: el dibuix pla de sempre, en peces ─────────────────────────

TEX_LIGHT = Light(ambient=0.8, vignette=None, floor_fade=None)        # (la paret llisa: la llum, la del món)


@functools.lru_cache(maxsize=None)
def _llisa():
    """La paret sense res (planxes, sostre, conducte), per a les parets que el dibuix pla no cobreix."""
    cv = Canvas(light=TEX_LIGHT)
    PL.wall(cv, 0, W - 1, seed=5, base=2.6)
    cv.rect(0, 0, W - 1, 9, HULL, lambda x, y: 0.7 + (0.5 if y in (7, 8) else 0))
    cv.hline(0, W - 1, 10, HULL, 3.0)
    cv.hline(0, W - 1, 11, HULL, 1.6)
    return cv.img


@functools.lru_cache(maxsize=None)
def _paret(t=0.0):
    """Les parets planes, sense els mobles: l'escala, el conducte, el rètol, el termòstat (al moment `t`)."""
    cv = Canvas(light=PL.LIGHT)
    PL._walls(cv, t, mobles=False)
    return cv.img


@functools.lru_cache(maxsize=None)
def _mobles():
    """Els mobles plans sobre transparent: d'aquí surten els fronts dels arxivadors, les caixes, el manòmetre."""
    cv = Canvas(light=PL.LIGHT, transparent=True)
    PL._canonada(cv)
    PL._arxivadors(cv)
    PL._prestatge(cv)
    PL._taula_moble(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _objectes(t=0.0):
    """El que hi ha damunt la taula (els expedients, la tassa, el flexo, la pols), al moment `t`."""
    cv = Canvas(light=PL.LIGHT, transparent=True)
    PL._taula_objectes(cv, t)
    return cv.img


@functools.lru_cache(maxsize=None)
def _vidre(t=0.0):
    """La taula de llum plana (el vidre amb el plànol i la línia d'escaneig), al moment `t`."""
    cv = Canvas(light=PL.LIGHT, transparent=True)
    PL._taula_llum(cv, t)
    return cv.img


@functools.lru_cache(maxsize=None)
def _carpeta():
    cv = Canvas(light=PL.LIGHT, transparent=True)
    PL.carpeta(cv)
    box = cv.img.getbbox()
    return cv.img.crop(box)


OBJ_BOX = (305, 118, 433, 164)                     # els objectes de damunt la taula, al dibuix pla
OBJ_PEU = (368 - OBJ_BOX[0], 160 - OBJ_BOX[1])     # el punt del dibuix que toca al mig del tauler
GLASS = (484, 118, 606, 158)                       # el vidre de la taula de llum, al dibuix pla
MANO_BOX = (277, 82, 296, 101)                     # el manòmetre


# ─── Les superfícies ────────────────────────────────────────────────────────

def _terra(s, t, P):
    """Planxes d'acer de 72×52 amb la junta, el cantell il·luminat, reblons i pols; en coordenades del món."""
    x, z = P[0], P[2]
    cx, cz = math.floor(x / 72), math.floor(z / 52)
    fx, fz = x - cx * 72, z - cz * 52
    if fx < 1.0 or fz < 1.0:
        return 0.8
    v = 2.2 + (_h(cx, cz, 4) - 0.5) * 0.4
    if fx < 2.2 or fz < 2.2:
        v += 0.6
    elif fx > 70.6 or fz > 50.6:
        v -= 0.4
    for rx in (4.5, 67.5):
        for rz in (4.5, 47.5):
            if (fx - rx) ** 2 + (fz - rz) ** 2 < 2.2:
                return 4.2 if fx - rx + fz - rz < 0 else 1.5
    if _h(int(x) // 7, int(z) // 4, 44) > 0.92:
        v -= 0.3                                                          # pols
    if _h(int(x) // 5, int(z) // 2, 45) > 0.985:
        v += 1.0                                                          # papers trepitjats, rascades
    return v


def _arxivadors(e, mob):
    z0 = ZW - CAB_D
    e.foscor('ombra_arxivadors', (_w(100), 0.6, ZW), (_w(282), 0.6, ZW), (_w(282), 0.6, z0 - 26), (_w(100), 0.6, z0 - 26),
             lambda s, t: 0.6 * min(1.0, max(0.0, (CAB_D + 26 - t) / 26)))
    for ci, (x0, x1) in enumerate(CABS):
        e.caixa('arxivador', _w(x0), _w(x1 + 1), 0, _y(CT), z0, ZW - 1, OLIVE, 2.4,
                cares={'davant': {'tex': (mob, (x0, CT, x1 + 1, HW))},
                       'dalt': {'ramp': OLIVE, 'lvl': lambda s, t, P: 3.8 - t * 0.02 + (0.8 if t < 1.2 else 0)},
                       'dreta': {'ramp': OLIVE, 'lvl': lambda s, t, P: 1.8 - (0.6 if s % 33 < 1 else 0)},
                       'esquerra': {'ramp': OLIVE, 'lvl': 2.2}})
    # les caixes d'arxiu de damunt
    for i, (bx0, bx1, bh) in enumerate(TOPS):
        zc = ZW - 22 + (i % 2) * 4
        e.caixa('arxivador', _w(bx0), _w(bx1 + 1), _y(CT), _y(CT) + bh, zc - 15, zc + 15, MANILA, 2.4,
                cares={'davant': {'tex': (mob, (bx0, CT - bh, bx1 + 1, CT))},
                       'dalt': {'ramp': MANILA, 'lvl': lambda s, t, P: 3.4 - (0.8 if abs(t - 15) < 0.7 else 0)},
                       'dreta': {'ramp': MANILA, 'lvl': 1.8}})
    # el calaix obert, amb les cartes confiscades
    x0, x1 = CABS[2]
    y0 = CT + 5 + 33
    e.foscor('ombra_calaix', (_w(x0), _y(y0 + 36), z0 - 0.4), (_w(x1), _y(y0 + 36), z0 - 0.4),
             (_w(x1), _y(y0 + 50), z0 - 0.4), (_w(x0), _y(y0 + 50), z0 - 0.4), lambda s, t: 0.6 * (1 - t / 14))

    def cartes(s, t, P):
        k = int(s // 4.5)
        if t > 20:
            return 1.2
        return 3.4 + _h(k, 3) * 0.8 - (0.9 if s % 4.5 < 0.8 else 0) - t * 0.03
    e.caixa('arxivador', _w(x0 + 1), _w(x1), _y(y0 + 36), _y(y0 + 4), z0 - 22, z0, OLIVE, 2.6,
            cares={'davant': {'tex': (mob, (x0 + 1, y0 + 4, x1, y0 + 37))},
                   'dalt': {'ramp': PAPER, 'lvl': cartes}, 'dreta': {'ramp': OLIVE, 'lvl': 1.8}})


def _prestatges(e, mob):
    for sy in SHELVES:
        e.foscor('ombra_prestatge', (_w(306), _y(sy + 3), ZW - 0.5), (_w(442), _y(sy + 3), ZW - 0.5),
                 (_w(442), _y(sy + 20), ZW - 0.5), (_w(306), _y(sy + 20), ZW - 0.5),
                 lambda s, t: 0.55 * (1 - t / 17))
        for sx in (_w(316), _w(430)):                                     # les escaires
            e.caixa('prestatge', sx, sx + 2, _y(sy + 10), _y(sy + 3), ZW - 16, ZW, HULL, 2.4)
        e.caixa('prestatge', _w(309), _w(438), _y(sy + 3), _y(sy), ZW - 24, ZW, HULL, 2.6,
                cares={'davant': {'ramp': HULL, 'lvl': lambda s, t, P: 4.2 - t * 0.6},
                       'dalt': {'ramp': HULL, 'lvl': 3.4}, 'dreta': {'ramp': HULL, 'lvl': 2.0}})
        crop = mob.crop((309, sy - 28, 438, sy))
        e.sprite('prestatge', crop, (crop.width / 2, crop.height), (_w(373.5), _y(sy), ZW - 12))


def _taula(e, mob, obj):
    x, z, w, d, h, a = DESK
    e.foscor('ombra_taula', _lp(-w / 2 - 6, 0.6, d / 2 + 10, DESK), _lp(w / 2 + 40, 0.6, d / 2 + 10, DESK),
             _lp(w / 2 + 40, 0.6, -d / 2 - 8, DESK), _lp(-w / 2 - 6, 0.6, -d / 2 - 8, DESK),
             lambda s, t: 0.55 * max(0.0, 1 - ((s - (w + 46) / 2 + 14) / ((w + 46) / 2)) ** 4
                                     - ((t - (d + 18) / 2) / ((d + 18) / 2)) ** 4))

    def caixa(lx, lz, cw, cd, ch, ramp, lvl=2.6, y0=0.0, cares=None):
        P = _lp(lx, 0, lz, DESK)
        e.caixa_girada('taula', P[0], P[2], cw, cd, ch, a, ramp, lvl, y0=y0, cares=cares)
    for lx in (-w / 2 + 6, w / 2 - 6):                                    # les potes i el travesser
        for lz in (-d / 2 + 5, d / 2 - 5):
            caixa(lx, lz, 4, 4, h - 4, STEEL, 3.0)
    caixa(0, d / 2 - 5, w - 14, 2, 2, STEEL, 2.4, y0=12)
    caixa(w / 2 - 28, 0, 34, d - 10, 30, PANEL, 2.4, y0=h - 34,          # la calaixera
          cares={'davant': {'tex': (mob, (390, 170, 426, 201))}})
    caixa(0, 0, w, d, 5, PANEL, 2.8, y0=h - 5,
          cares={'dalt': {'ramp': PANEL, 'lvl': lambda s, t, P: 3.8 + (0.6 if t < 1.2 else 0) - (0.4 if int(s * 0.7 + t) % 23 == 0 else 0)},
                 'davant': {'ramp': PANEL, 'lvl': lambda s, t, P: 4.4 - t * 0.6},
                 'dreta': {'ramp': PANEL, 'lvl': lambda s, t, P: 3.2 - t * 0.5},
                 'esquerra': {'ramp': PANEL, 'lvl': lambda s, t, P: 3.4 - t * 0.5}})
    # la claror del flexo damunt el tauler
    corners = [_lp(lx, h + 0.4, lz, DESK) for lx, lz in ((-w / 2, d / 2), (w / 2, d / 2), (w / 2, -d / 2), (-w / 2, -d / 2))]
    e.claror(*corners, (255, 214, 140), lambda s, t: 0.32 * max(0.0, 1 - math.hypot(s - w / 2 - 30, t - d / 2) / 70))
    # els objectes de damunt (el dibuix pla, dret, al mig del tauler)
    e.sprite('objectes', obj.crop(OBJ_BOX), OBJ_PEU, _lp(0, h, 0, DESK))


def _taula_llum(e, vidre):
    x, z, w, d, a = LTAB
    hf, hb = LTAB_H
    e.foscor('ombra_taula_llum', _lp(-w / 2 - 6, 0.6, d / 2 + 8, LTAB), _lp(w / 2 + 30, 0.6, d / 2 + 8, LTAB),
             _lp(w / 2 + 30, 0.6, -d / 2 - 8, LTAB), _lp(-w / 2 - 6, 0.6, -d / 2 - 8, LTAB),
             lambda s, t: 0.45 * max(0.0, 1 - ((s - (w + 36) / 2 + 10) / ((w + 36) / 2)) ** 4
                                     - ((t - (d + 16) / 2) / ((d + 16) / 2)) ** 4))

    def caixa(lx, lz, cw, cd, ch, ramp, lvl=2.6, y0=0.0, cares=None):
        P = _lp(lx, 0, lz, LTAB)
        e.caixa_girada('taula_llum', P[0], P[2], cw, cd, ch, a, ramp, lvl, y0=y0, cares=cares)
    for lx in (-w / 2 + 8, w / 2 - 8):
        for lz in (-d / 2 + 6, d / 2 - 6):
            caixa(lx, lz, 4, 4, hf if lz < 0 else hb, STEEL, 3.0)
    caixa(0, -d / 2 + 6, w - 20, 2, 2, STEEL, 2.4, y0=20)
    caixa(0, 0, w, d, 6, PANEL, 2.4, y0=hf - 6,
          cares={'davant': {'ramp': PANEL, 'lvl': lambda s, t, P: 3.6 - t * 0.4},
                 'dreta': {'ramp': PANEL, 'lvl': 2.2}, 'esquerra': {'ramp': PANEL, 'lvl': 2.6}})

    def P(lx, lz):
        return _lp(lx, hf + (hb - hf) * (lz + d / 2) / d, lz, LTAB)
    # el marc, inclinat, i el vidre de llum (el plànol cian)
    e.quad('taula_llum', P(-w / 2, d / 2), P(w / 2, d / 2), P(w / 2, -d / 2), P(-w / 2, -d / 2), ramp=PANEL,
           lvl=lambda s, t, P_: 3.0 + (1.6 if t > d - 1.5 else 0))
    i = 7
    q = [P(-w / 2 + i, d / 2 - i), P(w / 2 - i, d / 2 - i), P(w / 2 - i, -d / 2 + i), P(-w / 2 + i, -d / 2 + i)]
    q = [(p[0], p[1] + 0.4, p[2]) for p in q]
    e.quad('vidre', *q, tex=(vidre, GLASS))


def _primer_pla(e):
    """La pila de caixes d'arxiu en silueta, a baix a l'esquerra, i el pilar de la dreta."""
    FOSC = [(4, 4, 6), (10, 9, 10), (17, 15, 15), (25, 22, 20), (35, 30, 26), (46, 40, 34)]
    bx, bz = BOXES
    for cx, cz, w, d, h, a, y0 in ((bx, bz, 56, 40, 34, 0.18, 0), (bx - 4, bz + 4, 50, 36, 30, -0.1, 34),
                                   (bx + 50, bz - 26, 46, 36, 32, 0.4, 0)):
        e.caixa_girada('primer_pla', cx, cz, w, d, h, a, FOSC, 1.6, y0=y0,
                       cares={'dalt': {'ramp': FOSC, 'lvl': lambda s, t, P: 3.0 - (1.0 if abs(t - 18) < 1 else 0)},
                              'davant': {'ramp': FOSC, 'lvl': lambda s, t, P: 1.4 + (1.0 if 8 < s < 20 and 6 < t < 12 else 0)},
                              'dreta': {'ramp': FOSC, 'lvl': 2.2}})
    px, pz = PILLAR
    e.caixa('primer_pla', px - 12, px + 12, 0, HW + 40, pz - 12, pz + 12, FOSC, 1.6,
            cares={'esquerra': {'ramp': FOSC, 'lvl': lambda s, t, P: 2.4 - (0.8 if int(t) % 46 < 2 else 0)},
                   'davant': {'ramp': FOSC, 'lvl': lambda s, t, P: 1.4 + (0.6 if s < 2 else 0)}})


def escena(cv, estat=frozenset(), t=0.0):
    """Tota la sala, de lluny a prop. `estat`: els decorats que hi són ('carpeta'). → l'Escena."""
    cv.S = 1                                               # (el Canvas d'1× de Ferro-9 no ho diu)
    e = Escena(cv, CAM, LLUMS, ambient=-0.4)
    zn = CAM.pos[2] + 60
    paret, llisa, mob = _paret(t), _llisa(), _mobles()
    # el sostre, fosc
    e.quad('sostre', (0, HW, zn), (XR, HW, zn), (XR, HW, ZW), (0, HW, ZW), ramp=HULL, dues_cares=True,
           lvl=lambda s, t_, P: 0.8 + (1.4 if P[2] % 80 < 6 else 0))
    # la paret de l'escala (x = 0): de prop, la paret llisa; cap a la cantonada, el dibuix pla (x 0..100)
    e.quad('paret_esq_prop', (0, HW, zn), (0, HW, ZW - XL), (0, 0, ZW - XL), (0, 0, zn),
           tex=(llisa, (150, 0, 150 + ZW - XL - zn, HW)))
    e.quad('paret_esq', (0, HW, ZW - XL), (0, HW, ZW), (0, 0, ZW), (0, 0, ZW - XL), tex=(paret, (0, 0, XL, HW)))
    # la paret del fons (z = 300): el dibuix pla (x 100..640) i, a la dreta, la paret llisa
    e.quad('paret_fons', (0, HW, ZW), (W - XL, HW, ZW), (W - XL, 0, ZW), (0, 0, ZW), tex=(paret, (XL, 0, W, HW)))
    e.quad('paret_fons_dreta', (W - XL, HW, ZW), (XR, HW, ZW), (XR, 0, ZW), (W - XL, 0, ZW),
           tex=(llisa, (100, 0, 100 + XR - W + XL, HW)))
    # el terra, amb la claror freda de l'escala, la del flexo i la de la taula de llum
    e.quad('terra', (0, 0, ZW), (XR, 0, ZW), (XR, 0, zn), (0, 0, zn), ramp=DECK, lvl=_terra)
    e.claror((0, 0.3, ZW), (XR, 0.3, ZW), (XR, 0.3, 0), (0, 0.3, 0), (150, 190, 230),
             lambda s, t_: 0.3 * max(0.0, 1 - math.hypot((s - 10) / 110, (t_ - 50) / 70)) ** 1.3)
    e.claror((0, 0.3, ZW), (XR, 0.3, ZW), (XR, 0.3, 0), (0, 0.3, 0), (255, 214, 140),
             lambda s, t_: 0.18 * max(0.0, 1 - math.hypot((s - FLEXO[0]) / 120, (t_ - ZW + FLEXO[2]) / 70)) ** 1.3)
    e.claror((0, 0.3, ZW), (XR, 0.3, ZW), (XR, 0.3, 0), (0, 0.3, 0), (110, 200, 240),
             lambda s, t_: 0.2 * max(0.0, 1 - math.hypot((s - LTAB_C[0]) / 120, (t_ - ZW + LTAB_C[2]) / 70)) ** 1.3)
    # la foscor dels racons
    e.foscor('racons', (0, 0.5, ZW), (XR, 0.5, ZW), (XR, 0.5, zn), (0, 0.5, zn),
             lambda s, t_: max(0.6 * max(0.0, 1 - t_ / 26), 0.5 * max(0.0, 1 - s / 22)))
    e.foscor('cantonada', (0, HW, ZW - 0.5), (70, HW, ZW - 0.5), (70, 0, ZW - 0.5), (0, 0, ZW - 0.5),
             lambda s, t_: 0.45 * max(0.0, 1 - s / 70))
    e.foscor('paret_prop', (0.5, HW, zn), (0.5, HW, ZW - 100), (0.5, 0, ZW - 100), (0.5, 0, zn),
             lambda s, t_: 0.35 * max(0.0, 1 - s / 300))
    # la canonada de coure, amb el manòmetre
    e.tub('canonada', (PIPE_X, 0, ZW - 6), (PIPE_X, HW, ZW - 6), 3.6, COPPER, 1.6, brides=45)
    mano = mob.crop(MANO_BOX)
    e.sprite('canonada', mano, (286 - MANO_BOX[0], 98 - MANO_BOX[1]), (PIPE_X, _y(98), ZW - 10))
    _arxivadors(e, mob)
    # la carpeta caiguda (decorat), al costat de l'arxivador
    if 'carpeta' in estat:
        img = _carpeta()
        e.foscor('ombra_carpeta', (CARPETA[0] - 22, 0.6, CARPETA[1] + 8), (CARPETA[0] + 22, 0.6, CARPETA[1] + 8),
                 (CARPETA[0] + 22, 0.6, CARPETA[1] - 8), (CARPETA[0] - 22, 0.6, CARPETA[1] - 8),
                 lambda s, t_: 0.5 * max(0.0, 1 - ((s - 22) / 22) ** 2 - ((t_ - 8) / 8) ** 2))
        e.sprite('carpeta', img, (img.width / 2, img.height - 1), (CARPETA[0], 0, CARPETA[1]))
    _prestatges(e, mob)
    _taula_llum(e, _vidre(t))
    _taula(e, mob, _objectes(t))
    _primer_pla(e)
    return e


# ─── Composició ─────────────────────────────────────────────────────────────

def _render(estat=frozenset()):
    cv = Canvas(light=LIGHT)
    e = escena(cv, estat)
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)    # la barra de verbs: negre
    return cv.img, e


@functools.lru_cache(maxsize=None)
def _base():
    return _render()


def bg(cv):
    cv.img.paste(_base()[0])
    cv.P = cv.img.load()


def _decorat(nom):
    """Un decorat en 3D: la sala amb ell, menys la de sempre (només el que canvia)."""
    def fn(cv):
        img, _ = _render(frozenset({nom}))
        cv.img.alpha_composite(diff(img, _base()[0]))
        cv.P = cv.img.load()
    return fn


PROPS = {'carpeta': _decorat('carpeta')}


# ─── Animació: la pols al flexo, la bombeta que fa figa, la línia d'escaneig i el pilot del termòstat ──

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


def _frames(capa, n=24):
    """Els fotogrames d'una part de l'animació: el fons amb la capa del moment `t`, menys el fons."""
    img0, e = _base()
    out = []
    for i in range(n):
        img = img0.copy()
        img.alpha_composite(capa(e, i / n))
        out.append(diff(img, img0))
    return out


def _capa_paret(e, t):
    return e.capa(diff(_paret(t), _paret()), {'paret_fons', 'paret_esq'})


def _capa_vidre(e, t):
    return e.capa(diff(_vidre(t), _vidre()), {'vidre'})


def _capa_flexo(e, t):
    return _sprite_capa(e, 'objectes', _objectes(t).crop(OBJ_BOX), OBJ_PEU, _lp(0, DESK[4], 0, DESK))


# El pilot del termòstat (a la paret); la pols i la bombeta del flexo i la línia d'escaneig, damunt de les seves
# capes del davant (la taula i la taula de llum), perquè no les tapin.
ANIMS = {'ambient': {'frames': lambda: _frames(_capa_paret), 'frameDuration': 120},
         'flexo': {'frames': lambda: _frames(_capa_flexo), 'frameDuration': 120},
         'escaneig': {'frames': lambda: _frames(_capa_vidre), 'frameDuration': 120}}


def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


def _base_davant(box):
    """La línia base d'un moble girat: la del cantó de davant que queda més al fons (qui és davant de qualsevol tros
    del moble, hi passa per davant)."""
    return min(_p(*_lp(lx, 0, -box[3] / 2, box)[::2])[1] for lx in (-box[2] / 2, box[2] / 2))


# Capes del davant: el primer pla (sempre davant), la taula dels expedients i la taula de llum (qui hi passa per
# darrere, hi queda darrere).
FRONT = [
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20},
    {'id': 'davant_taula', 'mask': _amo({'taula', 'objectes'}), 'baseline': _base_davant(DESK), 'zIndex': 20,
     'props': ('flexo',)},
    {'id': 'davant_taula_llum', 'mask': _amo({'taula_llum', 'vidre'}), 'baseline': _base_davant(LTAB), 'zIndex': 20,
     'props': ('escaneig',)},
]


# ─── Geometria (coordenades de sala, projectades) ────────────────────────────

def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


V_MAX = 250                                        # més a prop, el personatge passaria d'1,2: és per al primer pla


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


def _forat(box, w, d, m=4):
    return [_p(*_lp(lx, 0, lz, box)[::2]) for lx, lz in ((-w / 2 - m, -d / 2 - m), (w / 2 + m, -d / 2 - m),
                                                          (w / 2 + m, d / 2 + m), (-w / 2 - m, d / 2 + m))]


# El terra on es camina (al món): de l'escala fins a la taula de llum, per davant dels arxivadors i per darrere i
# per davant de les dues taules (que són forats). Les caixes i el pilar del primer pla hi passen per davant.
WALK_MON = [(16, ZW - CAB_D - 8), (_w(278), ZW - CAB_D - 8), (_w(278), 286), (600, 286), (600, 170), (PILLAR[0] - 18, -40), (16, -40)]
_WALK = _talla([_p(x, z) for x, z in WALK_MON], V_MAX)
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)


def _escala_a(v):
    """L'escala d'un personatge amb els peus a la y de pantalla `v` (al terra, la profunditat només depèn de v)."""
    lo, hi = -400.0, 2000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.projecta((260, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((260, 0, (lo + hi) / 2))


def _sprite_rect(img, peu_img, peu):
    k = CAM.escala(peu)
    u, v, _ = CAM.projecta(peu)
    return (round(u - peu_img[0] * k) - 2, round(v - peu_img[1] * k) - 2, round(u + (img.width - peu_img[0]) * k) + 2,
            round(v + (img.height - peu_img[1]) * k) + 2)


def _moble_rect(box, w, d, h):
    return _rect_mon(*[_lp(lx, y, lz, box) for lx in (-w / 2, w / 2) for lz in (-d / 2, d / 2) for y in (0, h)])


_CARP = _carpeta()

GEOMETRIA = {
    'things': {
        'escala_hangar': {'rect': _rect_mon((0, _y(48), _wz(10)), (0, 0, _wz(92))), 'walk': _p(26, _wz(52))},
        'arxivador': {'rect': _rect_mon((_w(107), _y(CT) + 15, ZW - CAB_D), (_w(272), 0, ZW - CAB_D), (_w(107), 0, ZW)),
                      'walk': _p(_w(190), ZW - CAB_D - 30)},
        'expedient_iri': {'rect': _sprite_rect(Image.new('RGBA', (OBJ_BOX[2] - OBJ_BOX[0], OBJ_BOX[3] - OBJ_BOX[1])),
                                               OBJ_PEU, _lp(0, DESK[4], 0, DESK)),
                          'walk': _p(*_lp(0, 0, -DESK[3] / 2 - 26, DESK)[::2])},
        'planols': {'rect': _moble_rect(LTAB, LTAB[2], LTAB[3], LTAB_H[1]),
                    'walk': _p(*_lp(-10, 0, -LTAB[3] / 2 - 26, LTAB)[::2])},
        'carpeta': {'rect': _sprite_rect(_CARP, (_CARP.width / 2, _CARP.height - 1), (CARPETA[0], 0, CARPETA[1])),
                    'walk': _p(CARPETA[0] + 4, CARPETA[1] - 30)},
    },
    'spawns': {'vet': _p(44, 210)},
    'walkable': _WALK,
    'forats': [_forat(DESK, DESK[2], DESK[3]), _forat(LTAB, LTAB[2], LTAB[3])],
    'floorSquash': 0.4,                            # (la càmera, picada: el terra es veu aixafat)
    # L'ombra de contacte: el flexo (el punt del terra just a sota); la llum de l'arxiu és baixa i càlida.
    'characterShadow': {'enabled': True, 'color': '#08080c', 'alpha': 0.45, 'squash': 0.4, 'core': 0.6,
                        'light': {'x': _p(FLEXO[0], FLEXO[2])[0], 'y': _p(FLEXO[0], FLEXO[2])[1], 'stretch': 0.7,
                                  'reach': 170}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    # la llum de la sala sobre els personatges, en temps d'execució
    'characterLights': {
        'ambient': '#7c8494',                                                           # penombra freda
        'lights': [
            {'x': _p(FLEXO[0], FLEXO[2], FLEXO[1])[0], 'y': _p(FLEXO[0], FLEXO[2], FLEXO[1])[1], 'radius': 170,
             'color': '#ffd890', 'intensity': 0.9},                                     # el flexo
            {'x': _p(LTAB_C[0], LTAB_C[2], LTAB_C[1])[0], 'y': _p(LTAB_C[0], LTAB_C[2], LTAB_C[1])[1], 'radius': 150,
             'color': '#78d2ff', 'intensity': 0.7},                                     # la taula de llum
            {'x': _p(10, _wz(50), 150)[0], 'y': _p(10, _wz(50), 150)[1], 'radius': 160,
             'color': '#aad2f0', 'intensity': 0.6},                                     # l'escala de l'hangar
        ],
    },
}
