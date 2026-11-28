"""
L'avantdespatx del Director (Acte 3, la Vet), la planta noble del BCMU a les onze i quart. EN 3D (hd640/tres_d.py),
a 1×.

Una càmera alta que mira de biaix la cantonada del fons a la dreta (el revés de l'estudi; la porta del Director
queda a la paret que fuig, com al despatx queda la de tornar):
  - a la paret del fons, el marbre crema i l'arrimador de caoba, l'**ascensor** daurat amb l'agulla clavada a dalt,
    l'estació del **tub** pneumàtic, el pura sang, els dos cavalls al galop i el diploma «EMPLEAT DEL MES · 2004»;
  - a la paret de la dreta, en escorç, la **porta** doble del Director amb la placa de llautó i el cap de cavall;
  - la **taula de la senyora Pons**, separada de la paret i girada, amb tres cares: el llum de banquer verd,
    l'interfon i el telèfon, el portaplomes, el cartapàs i, ben a la vista, la **factura** de «Le Caniche d'Or» i
    la seva **nòmina**; la Pons hi és al darrere (i s'hi pot passar per darrere);
  - la cadira d'espera de fusta, girada (s'hi passa per darrere) i els dos ficus;
  - la catifa vermella de paret a paret, amb la sanefa d'or que ressegueix les dues parets;
  - primer pla: una columna de marbre i els pals de llautó amb el cordó de vellut de les cues del banc, a
    l'esquerra, i una butaca d'orelles d'esquena a la dreta, en silueta.

Tot el detall ve del dibuix pla de sempre (bcmu_avantdespatx_pla_comu.py), projectat; la taula, la cadira, la
catifa i el primer pla són volums. Damunt de tot, la llum de Suma Zero (hd640/llum.py): els apliques, el llum de
banquer, el bloom i la corba de to.

El món: x a la dreta (0 = la x 0 del dibuix pla de la paret del fons), y amunt (0 = el terra), z cap al fons
(300 = la paret del fons); la paret de la dreta és a x = 486. 1 unitat = 1 píxel de sala a la distància on un
personatge fa ≈111 px (escala 1).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from hd640 import llum
from hd.pix import Canvas, Light, W, H, hr, WALNUT
from hd.rooms.comu import _diff
from hd.rooms.exterior import fbm
from hd640.rooms import bcmu_avantdespatx_pla_comu as PL
from hd640.rooms.bcmu import BRASS, MAHOG, CARPET, tub_station
from hd640.rooms.bcmu_avantdespatx_pla_comu import BANKG, PAPERW, PAYB, INK
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
ZW = 300                                           # la paret del fons
HW = 200                                           # l'alçada de les parets (el dibuix pla fa 200 fins al terra)
XC = 486                                           # la cantonada: la x del dibuix pla (i del món) on gira la paret
XL = -220                                          # fins on arriba la paret del fons per l'esquerra
DESK = (318, 222, 190, 62, -0.18)                  # la taula de la Pons: x, z del centre, ample, fons, gir
DESK_H = 43                                        # l'alçada del tauler (al dibuix pla, 157)
CHAIR = (160, 262, -0.5)                           # la cadira d'espera: x, z, gir
FICUS = ((206, 284), (452, 284))                   # els dos ficus (x, z)
PONS = (372, 270)                                  # on és la Pons, darrere la taula
ROPE = ((14, 128), (96, 88))            # els pals del cordó, en primer pla
COLUMN = (-24, 140)                                 # la columna de marbre, en primer pla
ARMCHAIR = (384, -14, 2.6)                         # la butaca d'orelles, en primer pla: x, z, gir


def _y(fy):
    """Una y del dibuix pla (el terra, a 200) → l'alçada del món."""
    return HW - fy


def _rz(fx):
    """Una x del dibuix pla de la paret de la dreta → la z del món."""
    return ZW - (fx - XC)


CAM = Camera(pos=(76, 200, -236), yaw=0.36, pitch=0.2, f=470, centre=(320, 66))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)  # (la llum és la del món: la de l'Escena)
SCONCES = [(sx, _y(81), ZW - 6) for sx in PL.SCONCES if sx < XC] + \
          [(XC - 6, _y(81), _rz(sx)) for sx in PL.SCONCES if sx > XC]

# La llum de les textures: només la claror dels apliques (la resta la fa el món).
TEX_LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)
for _sx in PL.SCONCES:
    TEX_LIGHT.point(_sx, 83, r=70, k=0.6, squash=1.1, power=1.8)


# ─── Utilitats del món ──────────────────────────────────────────────────────

def _local(cx, cz, ang):
    """→ una funció que porta (lx, y, lz) d'un moble girat `ang` i centrat a (cx, cz) al món."""
    c, s = math.cos(ang), math.sin(ang)

    def P(lx, y, lz):
        return (cx + lx * c - lz * s, y, cz + lx * s + lz * c)
    return P


_DP = _local(DESK[0], DESK[1], DESK[4])
LAMP = _DP(-70, DESK_H + 18, 10)                   # el llum de banquer


def _llums():
    out = [Llum(p, 130, 1.1, power=1.6) for p in SCONCES]
    out.append(Llum(LAMP, 80, 1.4, power=1.8))                     # el llum de banquer
    out.append(Llum((230, 420, 150), 600, 0.5, power=1.2))         # el llum de sostre (fora de quadre)
    return out


# ─── Les textures: el dibuix pla de sempre ───────────────────────────────────

def _paret(capsule=None, needle=0):
    """Les parets planes, de cara: marbre, arrimador, apliques, l'ascensor, el tub, els quadres, el diploma i la
    porta del Director (sense els mobles: són volums)."""
    cv = Canvas(light=TEX_LIGHT)
    PL.wall(cv)
    for sx in PL.SCONCES:
        PL.sconce(cv, sx)
    PL.elevator(cv, needle)
    tub_station(cv, *PL.TUB, capsule=capsule)
    PL.paintings(cv)
    PL.employee(cv)
    PL.door(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _paret_base():
    return _paret()


@functools.lru_cache(maxsize=None)
def _paret_llisa():
    """La paret sense res: per allargar-la on el dibuix pla no arriba."""
    cv = Canvas(light=TEX_LIGHT)
    PL.wall(cv)
    return cv.img


def _peca(fn, *a, **kw):
    """Una peça del dibuix pla, sola sobre transparent."""
    cv = Canvas(light=TEX_LIGHT, transparent=True)
    fn(cv, *a, **kw)
    return cv.img


DESK_BOX = (PL.DESK[0], PL.DESK_TOP + 5, PL.DESK[1] + 1, PL.FLOOR_Y + 1)   # el frontal de la taula
LAMP_BOX = (244, 124, 275, 151)                     # el llum de banquer (el peu, a y 150)
PHONE_BOX = (371, 138, 426, 154)                    # l'interfon i el telèfon (la base, a y 153)
PEN_BOX = (311, 124, 323, 148)                      # el portaplomes (la base, a y 147)
FILES_BOX = (355, 136, 371, 147)                    # les carpetes
FICUS_BOX = (198, 120, 236, 206)                    # un ficus (el peu del test, a x 216 y 201)


@functools.lru_cache(maxsize=None)
def _textures():
    return {
        'paret': _paret_base(),
        'llisa': _paret_llisa(),
        'taula': _peca(PL.desk),
        'llum': _peca(PL.bankers_lamp),
        'interfon': _peca(PL.intercom),
        'plomes': _peca(PL.pen_holder),
        'ficus': _peca(PL.ficus, 216),
        'factura': _paper('factura'),
        'nomina': _paper('nomina'),
    }


PAPER = (22, 28)                                   # els dos papers damunt la taula (més grossos que de debò)


def _paper(quin):
    """La factura i la nòmina vistes de dalt, per estirar-les damunt la taula: el capçal, les ratlles i el total."""
    w, h = PAPER
    cv = Canvas(w=w, h=h, light=None, transparent=True)
    ramp = PAPERW if quin == 'factura' else PAYB
    cv.rect(0, 0, w - 1, h - 1, ramp, lambda x, y: 4.4 - y * 0.02)
    for x in range(w):
        cv.put(x, 0, ramp, 3.0)
        cv.put(x, h - 1, ramp, 2.4)
    for y in range(h):
        cv.put(0, y, ramp, 3.2)
        cv.put(w - 1, y, ramp, 2.6)
    if quin == 'factura':
        cv.sprite(['.aa.', 'aaa.', 'aaaa', 'a..a'], 2, 2, {'a': (BRASS, 4.6)})   # el caniche
        cv.rect(8, 2, 19, 3, [INK], 0)
        cv.rect(8, 5, 15, 5, [(150, 120, 60)], 0)
        for k, ww in enumerate((15, 12, 14, 10)):
            cv.rect(3, 9 + k * 3, 3 + ww, 9 + k * 3, [(130, 124, 120)], 0)
        cv.rect(10, 22, 19, 24, [(200, 30, 30)], 0)                   # 4.200 €
    else:
        cv.sprite(['aa.', 'abb', 'ab.'], 2, 2, {'a': (BRASS, 4.4), 'b': (BRASS, 5.6)})
        cv.rect(7, 2, 19, 3, [(40, 60, 80)], 0)
        for k in range(4):
            cv.rect(3, 8 + k * 3, 10, 8 + k * 3, [(110, 126, 134)], 0)
            cv.rect(13, 8 + k * 3, 19, 8 + k * 3, [(110, 126, 134)], 0)
        cv.rect(11, 22, 19, 24, [(30, 40, 70)], 0)                    # 2.900 €
    return cv.img


# ─── Les superfícies ────────────────────────────────────────────────────────

def _catifa(s, t, P):
    """La catifa vermella gruixuda, en coordenades del món: el pèl, les aigües i un enreixat de rombes que
    s'empetiteix cap al fons."""
    x, z = P[0], P[2]
    v = 3.0 + (fbm(x / 70, z / 40, 21) - 0.5) * 0.9 + (hr(int(x), int(z), 22) - 0.5) * 0.5
    v += math.sin(x * 0.05 + z * 0.17) * 0.15
    if abs(((x + z) % 46) - 23) < 0.9 or abs(((x - z) % 46) - 23) < 0.9:
        v -= 0.7
    return v


def _sanefa(d, u):
    """La sanefa d'or de la catifa (d: la distància a la paret; u: al llarg de la paret): dues línies i rombes."""
    if 3.5 < d < 5.5 or 13.5 < d < 15.5:
        return True
    m = abs((u % 18) - 9)
    return abs(d - 9.5) + m * 0.9 < 3.0


FOSC = [(5, 3, 3), (10, 6, 6), (17, 11, 10), (26, 17, 15), (37, 25, 21), (50, 35, 28), (66, 47, 36)]


def escena(cv, tex, estat=frozenset()):
    """Tota la sala, de lluny a prop. `estat`: 'sense_ficus' (per a l'animació). → l'Escena (qui ha pintat què)."""
    e = Escena(cv, CAM, _llums(), ambient=-0.7)
    zn = CAM.pos[2] + 60
    paret, llisa = tex['paret'], tex['llisa']
    # el sostre, fosc (gairebé no es veu)
    e.quad('sostre', (XL, HW, ZW), (XC, HW, ZW), (XC, HW, zn), (XL, HW, zn), ramp=MAHOG, lvl=1.4, dues_cares=True)
    # la paret del fons (z = 300): el dibuix pla (x 0..486) i, a l'esquerra, la paret llisa
    e.quad('paret_fons', (0, HW, ZW), (XC, HW, ZW), (XC, 0, ZW), (0, 0, ZW), tex=(paret, (0, 0, XC, HW)))
    e.quad('paret_fons_esq', (XL, HW, ZW), (0, HW, ZW), (0, 0, ZW), (XL, 0, ZW), tex=(llisa, (W + XL, 0, W, HW)))
    # la paret de la dreta (x = 486): de la cantonada cap a la càmera, el dibuix pla (x 486..640) i la llisa
    zr = _rz(W)
    e.quad('paret_dreta', (XC, HW, ZW), (XC, HW, zr), (XC, 0, zr), (XC, 0, ZW), tex=(paret, (XC, 0, W, HW)))
    e.quad('paret_dreta_prop', (XC, HW, zr), (XC, HW, zn), (XC, 0, zn), (XC, 0, zr),
           tex=(llisa, (60, 0, 60 + zr - zn, HW)))
    # la claror dels apliques a la paret, en ventall
    for (sx, sy, sz) in SCONCES:
        if sz > ZW - 10:
            e.claror((sx - 50, HW, ZW - 0.5), (sx + 50, HW, ZW - 0.5), (sx + 50, 0, ZW - 0.5), (sx - 50, 0, ZW - 0.5),
                     (255, 214, 150), lambda s, t, ty=HW - sy: 0.16 * max(0.0, 1 - math.hypot(s - 50, (t - ty) * 0.8) / 50))
        else:
            e.claror((XC - 0.5, HW, sz + 50), (XC - 0.5, HW, sz - 50), (XC - 0.5, 0, sz - 50), (XC - 0.5, 0, sz + 50),
                     (255, 214, 150), lambda s, t, ty=HW - sy: 0.16 * max(0.0, 1 - math.hypot(s - 50, (t - ty) * 0.8) / 50))
    # el terra: la catifa i la sanefa d'or que ressegueix les dues parets
    e.quad('terra', (XL, 0, ZW), (XC, 0, ZW), (XC, 0, zn), (XL, 0, zn), ramp=CARPET, lvl=_catifa)
    e.quad('sanefa', (XL, 0.2, ZW), (XC, 0.2, ZW), (XC, 0.2, ZW - 20), (XL, 0.2, ZW - 20), ramp=BRASS,
           lvl=lambda s, t, P: 2.6 + (hr(int(s), 4) - 0.5) * 0.6,
           forma=lambda s, t: t <= XC - (XL + s) and _sanefa(t, s))
    e.quad('sanefa', (XC - 20, 0.2, ZW), (XC, 0.2, ZW), (XC, 0.2, zn), (XC - 20, 0.2, zn), ramp=BRASS,
           lvl=lambda s, t, P: 2.6 + (hr(int(t), 5) - 0.5) * 0.6,
           forma=lambda s, t: (20 - s) < t and _sanefa(20 - s, t))
    # la foscor dels racons, i el bassal de llum del llum de sostre
    e.claror((0, 0.3, ZW), (XC, 0.3, ZW), (XC, 0.3, 40), (0, 0.3, 40), (255, 190, 140),
             lambda s, t: 0.14 * max(0.0, 1 - math.hypot(s - 250, (t - 130) * 1.3) / 230))
    e.foscor('racons', (XL, 0.5, ZW), (XC, 0.5, ZW), (XC, 0.5, zn), (XL, 0.5, zn),
             lambda s, t: max(0.55 * max(0.0, 1 - t / 26), 0.5 * max(0.0, 1 - (XC - XL - s) / 24)))
    e.foscor('cantonada', (XC - 70, HW, ZW - 0.5), (XC, HW, ZW - 0.5), (XC, 0, ZW - 0.5), (XC - 70, 0, ZW - 0.5),
             lambda s, t: 0.4 * max(0.0, 1 - (70 - s) / 70))
    e.foscor('cantonada2', (XC - 0.5, HW, ZW), (XC - 0.5, HW, ZW - 50), (XC - 0.5, 0, ZW - 50), (XC - 0.5, 0, ZW),
             lambda s, t: 0.4 * max(0.0, 1 - s / 50))
    e.foscor('sostre_fosc', (XL, HW - 0.5, ZW - 0.6), (XC, HW - 0.5, ZW - 0.6), (XC, 0, ZW - 0.6), (XL, 0, ZW - 0.6),
             lambda s, t: 0.4 * max(0.0, 1 - t / 50))
    # els ficus: al costat de la cadira i a la cantonada (el dibuix pla, dret), amb l'ombra
    if 'sense_ficus' not in estat:
        for k, (fx, fz) in enumerate(FICUS):
            e.foscor('ombra_ficus', (fx - 16, 0.6, fz + 12), (fx + 20, 0.6, fz + 12), (fx + 20, 0.6, fz - 14),
                     (fx - 16, 0.6, fz - 14),
                     lambda s, t: 0.55 * max(0.0, 1 - ((s - 18) / 18) ** 2 - ((t - 13) / 13) ** 2) * 1.5)
            e.sprite('ficus%d' % k, tex['ficus'].crop(FICUS_BOX), (216 - FICUS_BOX[0], 201 - FICUS_BOX[1]),
                     (fx, 0, fz))
    # la cadira d'espera, de fusta, girada: les potes, el seient i el respatller de tres travessers
    cx_, cz_, ca = CHAIR
    CP = _local(cx_, cz_, ca)
    e.foscor('ombra_cadira', (cx_ - 26, 0.6, cz_ + 22), (cx_ + 26, 0.6, cz_ + 22), (cx_ + 26, 0.6, cz_ - 22),
             (cx_ - 26, 0.6, cz_ - 22), lambda s, t: 0.5 * max(0.0, 1 - ((s - 26) / 22) ** 2 - ((t - 22) / 20) ** 2) * 1.5)

    def peca(lx, lz, w, d, h, y0, lvl, cares=None):
        px, _, pz = CP(lx, 0, lz)
        e.caixa_girada('cadira', px, pz, w, d, h, ca, WALNUT, lvl, y0=y0, cares=cares)
    for lx in (-13, 13):                                        # les potes de darrere i els muntants del respatller
        peca(lx, 12, 3, 3, 69, 0, 4.4)
    for lx in (-13, 13):
        peca(lx, -12, 3, 3, 25, 0, 4.8)
    for lz in (-12, 12):                                        # els travessers de sota
        peca(0, lz, 26, 2, 2, 9, 4.0)
    for k in range(3):                                          # (el respatller, abans que el seient: és al darrere)
        peca(0, 12, 24, 2, 4, 44 + k * 8, 5.6 - k * 0.2)
    peca(0, 0, 32, 30, 4, 25, 5.2, cares={'dalt': {'ramp': WALNUT, 'lvl': lambda s, t, P: 6.0 + (hr(int(s / 3), 1) - 0.5) * 0.4},
                                         'davant': {'ramp': WALNUT, 'lvl': 4.6}})
    # la taula de la Pons: el cos (el frontal del dibuix pla), el tauler i les coses de damunt
    dx, dz, dw, dd, da = DESK
    e.foscor('ombra_taula', *[_DP(lx, 0.6, lz) for lx, lz in ((-dw / 2 - 8, dd / 2 + 6), (dw / 2 + 8, dd / 2 + 6),
                                                             (dw / 2 + 8, -dd / 2 - 14), (-dw / 2 - 8, -dd / 2 - 14))],
             lambda s, t: 0.55 * min(1.0, max(0.0, (dd + 20 - t) / 14)) * min(1.0, s / 10, (dw + 16 - s) / 10))

    def costat(s, t, P):
        v = 2.6 + (hr(int(t / 5), int(s), 33) - 0.5) * 0.3
        if 4 < s < dd - 4 and 4 < t < 34:
            v += 0.4 if (s < 6 or t < 6) else (-0.5 if (s > dd - 6 or t > 32) else 0)
        return v
    e.caixa_girada('taula', dx, dz, dw, dd, DESK_H - 5, da, MAHOG, 2.4,
                   cares={'davant': {'tex': (tex['taula'], DESK_BOX)},
                          'esquerra': {'ramp': MAHOG, 'lvl': costat}, 'dreta': {'ramp': MAHOG, 'lvl': costat},
                          'dalt': {'ramp': MAHOG, 'lvl': 2.0}})

    def tauler(s, t, P):
        v = 4.4 + (hr(int(s / 8), int(t), 31) - 0.5) * 0.3 + math.sin(s * 0.05 + t * 0.6) * 0.08
        if s < 1.5 or t > dd + 6 - 1.5:
            v += 0.8
        return v
    e.caixa_girada('taula', dx, dz, dw + 6, dd + 6, 5, da, MAHOG, 3.6, y0=DESK_H - 5,
                   cares={'dalt': {'ramp': MAHOG, 'lvl': tauler},
                          'davant': {'ramp': MAHOG, 'lvl': lambda s, t, P: 5.4 if t < 1.5 else 3.6},
                          'esquerra': {'ramp': MAHOG, 'lvl': 3.0}, 'dreta': {'ramp': MAHOG, 'lvl': 2.8}})
    # el cartapàs de pell verda amb el filet d'or
    cart = [_DP(lx, DESK_H + 0.3, lz) for lx, lz in ((-40, 26), (52, 26), (52, -14), (-40, -14))]
    e.quad('cartapas', *cart, ramp=BANKG,
           lvl=lambda s, t, P: 2.4 + (hr(int(s), int(t), 2) - 0.5) * 0.4 + (1.6 if (2 < s < 3.5 or 88.5 < s < 90 or 2 < t < 3.5 or 36.5 < t < 38) else 0))
    # la factura i la nòmina, ben a la vista (de cara a qui ve)
    for quin, lx in (('factura', -26), ('nomina', 6)):
        pw, ph = PAPER
        e.quad(quin, _DP(lx, DESK_H + 0.6, 2 + ph / 2 * 0), _DP(lx + pw, DESK_H + 0.6, 2), _DP(lx + pw, DESK_H + 0.6, 2 - ph),
               _DP(lx, DESK_H + 0.6, 2 - ph), tex=(tex[quin], (0, 0, pw, ph)))
    # el llum de banquer, l'interfon, el portaplomes i les carpetes (el dibuix pla, dret)
    for sid, img, box, foot, lxz in (
            ('llum', tex['llum'], LAMP_BOX, (259, 150), (-70, 12)),
            ('plomes', tex['plomes'], PEN_BOX, (317, 147), (-50, 2)),
            ('interfon', tex['interfon'], PHONE_BOX, (398, 153), (64, 4)),
            ('plomes', tex['plomes'], FILES_BOX, (363, 146), (40, 16))):
        e.sprite(sid, img.crop(box), (foot[0] - box[0], foot[1] - box[1]), _DP(lxz[0], DESK_H, lxz[1]))
    # primer pla: la columna de marbre a l'esquerra i els pals de llautó amb el cordó de vellut
    e.tub('primer_pla', (COLUMN[0], 0, COLUMN[1]), (COLUMN[0], HW + 40, COLUMN[1]), 22, FOSC, 2.4, brides=0,
          llum_dir=(0.9, -0.2))
    e.tub('primer_pla', (COLUMN[0], 0, COLUMN[1]), (COLUMN[0], 10, COLUMN[1]), 27, FOSC, 2.0, llum_dir=(0.9, -0.2))
    for (px, pz) in ROPE:
        e.tub('primer_pla', (px, 0, pz), (px, 94, pz), 2.6, FOSC, 3.4, llum_dir=(0.9, -0.4))
        e.tub('primer_pla', (px, 92, pz), (px, 98, pz), 4.2, FOSC, 4.2, llum_dir=(0.9, -0.4))
        e.tub('primer_pla', (px, 0, pz), (px, 4, pz), 12, FOSC, 2.0, llum_dir=(0.9, -0.4))
    VELL = [(10, 2, 4), (24, 5, 9), (40, 8, 14), (58, 12, 20)]
    for (ax, az), (bx, bz) in zip(((COLUMN[0] + 24, COLUMN[1] - 4),) + ROPE, ROPE):
        mid = ((ax + bx) / 2, 66, (az + bz) / 2)
        e.cable('primer_pla', [(ax, 90, az), mid, (bx, 90, bz)], VELL, 2.4, gruix=3.4)
    # i, a la dreta, una butaca d'orelles de pell, d'esquena, en silueta
    ax, az, aa = ARMCHAIR
    AP = _local(ax, az, aa)
    for lx, lz, w, d, h, y0, lv in ((0, 22, 64, 16, 84, 4, 1.6), (-26, 0, 14, 56, 50, 4, 2.0),
                                    (0, 0, 64, 56, 30, 4, 1.4), (26, 0, 14, 56, 50, 4, 2.0)):
        p = AP(lx, 0, lz)
        e.caixa_girada('primer_pla', p[0], p[2], w, d, h, aa, FOSC, lv, y0=y0,
                       cares={'dalt': {'ramp': FOSC, 'lvl': lv + 1.4}, 'esquerra': {'ramp': FOSC, 'lvl': lv + 0.8}})
    return e


# ─── Composició i llum ──────────────────────────────────────────────────────

def _proj(P):
    u, v, _ = CAM.projecta(P)
    return u, v


def _fx():
    light = [llum.wash(*_proj(p), 60, (255, 214, 150), k=0.4, air=0.02, squash=1.1) for p in SCONCES]
    lx, ly = _proj(LAMP)
    light.append(llum.wash(lx, ly + 10, 60, (255, 230, 160), k=0.7, air=0.05, squash=1.4))
    tone = [llum.grade(contrast=1.12, pivot=70, sat=1.12, lift=(4, 1, 0))]
    fonts = [_proj(p) for p in SCONCES] + [_proj(LAMP)]
    bloom = [llum.bloom(thr=215, radii=((2, 0.35), (6, 0.2)), mask=lambda x, y: sum(((x - fx) ** 2 + (y - fy) ** 2) < 120 for fx, fy in fonts) > 0)]
    return light, bloom, tone


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


PROPS = {}


# ─── Animacions ─────────────────────────────────────────────────────────────

def _fotograma(capes):
    """El fons amb unes capes damunt, amb la llum, menys el fons amb la llum."""
    img, _ = _base()
    img = img.copy()
    for c in capes:
        img.alpha_composite(c)
    return _diff(_amb_llum(img), _base_llum())


@functools.lru_cache(maxsize=None)
def _buit():
    return _diff(_base_llum(), _base_llum())


# Una càpsula que puja pel tub (el banc no para): la y de la càpsula als primers fotogrames; la resta, buit.
ANIM_N = 60
CAPSULE = PL.CAPSULE


def _frames():
    _, e = _base()
    out = [_fotograma([e.capa(_diff(_paret(capsule=c), _paret_base()), {'paret_fons'})]) for c in CAPSULE]
    return out + [_buit()] * (ANIM_N - len(out))


# L'agulla de l'ascensor: clavada a dalt de tot, però de tant en tant fa un tremolor.
NEEDLE = PL.NEEDLE


def _needle_frames():
    _, e = _base()
    cache = {}
    out = []
    for d in NEEDLE:
        if not d:
            out.append(_buit())
            continue
        if d not in cache:
            cache[d] = _fotograma([e.capa(_diff(_paret(needle=d), _paret_base()), {'paret_fons'})])
        out.append(cache[d])
    return out


# Els ficus, a l'aire condicionat: les fulles es gronxen, cadascun al seu ritme.
_DARRERE = {'paret_fons', 'paret_fons_esq', 'paret_dreta', 'terra', 'sanefa', ''}


def _ficus_frames():
    from PIL import Image
    from pixels import nearest
    img0, e = _base()
    nofi, _ = _render(frozenset({'sense_ficus'}))
    src0, srcn = img0.load(), nofi.load()
    out = []
    for i in range(12):
        img = img0.copy()
        P = img.load()
        for k, (fx, fz) in enumerate(FICUS):
            sway = i * math.tau / 12 + (2.2 if k else 0)
            spr = _peca(PL.ficus, 216, sway=sway).crop(FICUS_BOX)
            idx = e.ids.index('ficus%d' % k)
            peu = (fx, 0, fz)
            sk = CAM.escala(peu)
            u, v, _ = CAM.projecta(peu)
            w, h = max(1, round(spr.width * sk)), max(1, round(spr.height * sk))
            im = nearest(spr, (w, h)) if sk >= 1 else spr.resize((w, h), Image.Resampling.BOX)
            ox, oy = round(u - (216 - FICUS_BOX[0]) * sk), round(v - (201 - FICUS_BOX[1]) * sk)
            sp = im.load()
            for Y in range(max(0, oy - 2), min(BOTTOM + 1, oy + h + 2)):
                for X in range(max(0, ox - 2), min(W, ox + w + 2)):
                    a = e.amo[Y * W + X]
                    if a != idx and e.ids[a] not in _DARRERE:
                        continue
                    x, y = X - ox, Y - oy
                    c = sp[x, y] if 0 <= x < w and 0 <= y < h else (0, 0, 0, 0)
                    if c[3] >= 128:
                        P[X, Y] = c
                    elif a == idx:
                        P[X, Y] = srcn[X, Y]
        out.append(_diff(_amb_llum(img), _base_llum()))
    return out


ANIMS = {
    'tub': {'frames': _frames, 'frameDuration': 75},
    'agulla': {'frames': _needle_frames, 'frameDuration': 60},
    'ficus': {'frames': _ficus_frames, 'frameDuration': 153},
}


def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


def _desk_baseline():
    """La línia base de la taula: entre la vora del darrere més propera i la del davant més llunyana."""
    dw, dd = DESK[2], DESK[3]
    back = max(_p(*_DP(lx, 0, dd / 2 + 3)[::2])[1] for lx in (-dw / 2, dw / 2))
    front = min(_p(*_DP(lx, 0, -dd / 2 - 3)[::2])[1] for lx in (-dw / 2, dw / 2))
    return (back + front) // 2


# Capes del davant: el primer pla (sempre davant), la taula de la Pons (amb el que hi ha damunt), la cadira
# d'espera i els ficus (qui hi passa per darrere, hi queda darrere).
FRONT = [
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20},
    {'id': 'davant_taula', 'mask': _amo({'taula', 'cartapas', 'factura', 'nomina', 'llum', 'plomes', 'interfon'}),
     'baseline': _desk_baseline(), 'zIndex': 20},
    {'id': 'davant_cadira', 'mask': _amo({'cadira'}), 'baseline': _p(CHAIR[0], CHAIR[1] - 14)[1], 'zIndex': 20},
    {'id': 'davant_ficus', 'mask': _amo({'ficus0', 'ficus1'}), 'baseline': _p(FICUS[0][0], FICUS[0][1] - 8)[1],
     'zIndex': 20, 'props': ['ficus']},                # (l'animació dels ficus, amb la capa: si no, la taparia)
]


# ─── Geometria (coordenades de sala, projectades) ────────────────────────────

def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


# El terra on es camina (al món): davant l'ascensor i el tub, entre la cadira i la taula, per davant de la taula i
# fins a la porta del Director. Per darrere de la taula, no (tasca 286): per parlar amb la Pons, la Vet hi entrava
# per la dreta i s'hi quedava, com si fos una altra secretària (la Pons, que no es mou, hi és fora del terra).
def _z_a(x, v):
    """La z del terra que es veu a la y de pantalla `v`, a la x del món `x`."""
    lo, hi = -400.0, 400.0
    for _ in range(50):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if CAM.projecta((x, 0, m))[1] > v else (lo, m)
    return lo


V_PROP = 214                                       # el terra on es camina s'acaba aquí (escala ≈1,2)
WALK_MON = [(20, 272), (122, 272), (130, 244), (194, 236), (204, 204), (400, 166), (428, 178), (432, 236),
            (414, 250), (440, 266), (474, 260)]
_WALK = [_p(x, z) for x, z in WALK_MON]
_A, _B = _WALK[-1], _p(WALK_MON[-1][0], _z_a(WALK_MON[-1][0], V_PROP))   # la vora de la paret de la dreta, fins a baix
if _B[0] > 628:                                    # (tallada per la vora de la pantalla)
    _WALK += [(628, round(_A[1] + (_B[1] - _A[1]) * (628 - _A[0]) / (_B[0] - _A[0]))), (628, V_PROP)]
else:
    _WALK.append(_B)
_WALK.append((_p(WALK_MON[0][0], _z_a(WALK_MON[0][0], V_PROP))[0], V_PROP))
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)


def _escala_a(v):
    """L'escala d'un personatge amb els peus a la y de pantalla `v` (al terra, la profunditat només depèn de v)."""
    lo, hi = 1.0, 2000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.projecta((250, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((250, 0, (lo + hi) / 2))


def _davant(lx):
    """Un punt del terra davant la taula, a l'altura `lx` del tauler."""
    x, _, z = _DP(lx, 0, -DESK[3] / 2 - 26)
    return _p(x, z)


def _paper_rect(lx):
    pw, ph = PAPER
    return _rect_mon(*[_DP(x, DESK_H + 0.6, z) for x in (lx, lx + pw) for z in (2, 2 - ph)])


_ASC = (19, 95, _y(31), _y(200))                   # l'ascensor al dibuix pla: x0, x1, y de dalt, y de baix
_DOOR = (504, 595, _y(48), _y(200))                # la porta del Director, a la paret de la dreta

GEOMETRIA = {
    'things': {
        'ascensor': {'rect': _rect_mon((_ASC[0], _ASC[2], ZW), (_ASC[1], _ASC[3], ZW)), 'walk': _p(57, 262)},
        'tub': {'rect': _rect_mon((PL.TUB[0], _y(PL.TUB[1]), ZW), (PL.TUB[2] + 6, _y(PL.TUB[3]), ZW)),
                'walk': _p(118, 262)},
        'factura': {'rect': _paper_rect(-26), 'walk': _davant(-14)},
        'nomina': {'rect': _paper_rect(6), 'walk': _davant(18)},
        'porta': {'rect': _rect_mon((XC, _DOOR[2], _rz(_DOOR[0])), (XC, _DOOR[3], _rz(_DOOR[1]))),
                  'walk': _p(452, 236)},
    },
    'spawns': {'pons': _p(*PONS), 'vet': _p(190, 130), 'ballester': _p(100, 230)},   # (en Ballester, si acompanya la Vet)
    'walkable': _WALK,
    'floorSquash': 0.45,                           # (la càmera, picada: el terra es veu aixafat)
    # L'ombra de contacte: la llum dominant és la del sostre, al mig de la sala; curta i cap enfora.
    'characterShadow': {'enabled': True, 'color': '#140608', 'alpha': 0.42, 'squash': 0.42, 'core': 0.6,
                        'light': {'x': _p(230, 160)[0], 'y': _p(230, 160)[1], 'stretch': 0.5, 'reach': 170}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    # la llum de la sala sobre els personatges, en temps d'execució
    'characterLights': {
        'ambient': '#a89484',                                                           # planta noble, càlida
        'lights': [
            {'x': round(_proj(p)[0]), 'y': round(_proj(p)[1]), 'radius': 110, 'color': '#ffd696', 'intensity': 0.7}
            for p in SCONCES
        ] + [
            {'x': round(_proj(LAMP)[0]), 'y': round(_proj(LAMP)[1]), 'radius': 90, 'color': '#c8f0a0', 'intensity': 0.6},  # el llum de banquer
        ],
    },
}
