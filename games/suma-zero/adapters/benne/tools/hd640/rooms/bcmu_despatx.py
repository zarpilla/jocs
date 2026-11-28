"""
El despatx del Director (Acte 3, la Vet), la planta noble del BCMU a les onze i quart. EN 3D (hd640/tres_d.py), a 1×.

Una càmera alta que mira de biaix la cantonada del fons a l'esquerra (com l'estudi de l'Iri):
  - a la paret de l'esquerra, en escorç, la **porta** doble de caoba (tornar a l'avantdespatx), l'aplic i els
    tres diplomes; davant, el **sofà** Chesterfield, separat de la paret i una mica girat;
  - a la paret del fons, el **finestral** amb el llac de Ginebra, el Jet d'Eau i els Alps, entre les cortines de
    vellut; el sol de mig matí hi entra en diagonal i dibuixa els vidres i els travessers al parquet i a la catifa;
  - la **llibreria** de llibres de finances, amb volum (un moble arran de paret, amb el sòcol de portes);
  - la **taula** del Director, separada de la llibreria i girada, amb tres cares: la **foto** d'en Rockefeller,
    el **mòbil** cap per avall, el portaplomes, el llum i el cartapàs; la cadira de respatller alt al darrere
    (s'hi pot passar per darrere de la taula);
  - el llit d'en Rockefeller i el globus bar, davant el finestral; el retrat a l'oli i, a terra, el **bol**;
  - el parquet de llistons que fuig cap al fons i la catifa blau marí amb la sanefa d'or, una mica girada;
  - primer pla: una butaca d'orelles en silueta a baix a l'esquerra i una pilastra de marbre a la dreta.

Tot el detall ve del dibuix pla de sempre (bcmu_despatx_pla_comu.py), projectat. Damunt de tot, la llum de Suma
Zero (hd640/llum.py): el finestral, el raig de sol, el bloom i la corba de to.

El món: x a la dreta (0 = la paret de la porta), y amunt (0 = el terra), z cap al fons (300 = la paret del fons);
1 unitat = 1 píxel de sala a la distància on un personatge fa ≈111 px (escala 1).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from hd640 import llum
from hd.pix import Canvas, Light, W, H, hr, WALNUT
from hd.rooms.comu import _diff
from hd.rooms.exterior import fbm
from hd640.rooms import bcmu_despatx_pla_comu as PL
from hd640.rooms.bcmu_despatx_pla_comu import LEATHER, VELVET, PHONE, SILVER, BANKG, PAPERW
from hd640.rooms.bcmu import BRASS, MAHOG
from hd640.rooms.bcmu_avantdespatx_pla_comu import wall, sconce
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
ZW = 300                                           # la paret del fons
HW = 200                                           # l'alçada de les parets (el dibuix pla fa 200 fins al terra)
XL = 196                                           # al dibuix pla, la cantonada de la paret de l'esquerra (la porta)
XB = 186                                           # al dibuix pla de la paret del fons, la x que cau a la cantonada
XR = 760                                           # on s'acaba la paret del fons (fora de la pantalla)
DESK = (316, 220, 160, 66, 0.2)                    # la taula del Director: x, z del centre, ample, fons, gir
DESK_H = 43                                        # l'alçada del tauler (al dibuix pla, 157)
SHELF = (236, 392, 278)                            # la llibreria: x0, x1, z del davant (el darrere, a la paret)
SOFA = (46, 236, 108, 42, -0.32)                   # el sofà: x, z del centre, llarg, fons, gir (de cara a +x)
BED = (100, 270)                                   # el llit d'en Rockefeller
GLOBE = (204, 262)                                 # el globus bar
BOWL = (426, 276)                                  # el bol, sota el retrat
CHAIR = (0, 34)                                    # la cadira del Director (al sistema de la taula: lx, lz)


def _w(fx):
    """Una x del dibuix pla de la paret del fons → la x del món."""
    return fx - XB


def _wz(fx):
    """Una x del dibuix pla de la paret de l'esquerra → la z del món."""
    return ZW - XL + fx


def _y(fy):
    """Una y del dibuix pla (el terra, a 200) → l'alçada del món."""
    return HW - fy


WIN = (_w(PL.WIN[0]), _w(PL.WIN[2]), _y(PL.WIN[3]), _y(PL.WIN[1]))   # x0, x1, y0, y1
WIN_C = ((WIN[0] + WIN[1]) / 2, (WIN[2] + WIN[3]) / 2, ZW)
SUN = (0.42, -0.62, -1.0)                          # cap on va el sol (per cada unitat de z cap a la càmera)

CAM = Camera(pos=(420, 180, -260), yaw=-0.36, pitch=0.12, f=470, centre=(320, 64))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)  # (la llum és la del món: la de l'Escena)
SCONCE = (0, _y(81), _wz(141))
LLUMS = [Llum((WIN_C[0], WIN_C[1], ZW - 70), 420, 1.5, power=1.2),   # el finestral
         Llum((WIN_C[0] + 60, 0, 150), 200, 0.8, power=1.5),         # el sol a terra, que rebota
         Llum((6, SCONCE[1], SCONCE[2]), 90, 0.8, power=1.8)]         # l'aplic

TEX_LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)
TEX_LIGHT.point(141, 83, r=60, k=0.5, squash=1.1, power=1.8)


# ─── Utilitats del món ──────────────────────────────────────────────────────

def _local(cx, cz, ang):
    """→ una funció que porta (lx, y, lz) d'un moble girat `ang` i centrat a (cx, cz) al món."""
    c, s = math.cos(ang), math.sin(ang)

    def P(lx, y, lz):
        return (cx + lx * c - lz * s, y, cz + lx * s + lz * c)
    return P


_DP = _local(DESK[0], DESK[1], DESK[4])


# ─── Les textures: el dibuix pla de sempre ───────────────────────────────────

def _paret_esq():
    """La paret de la porta, de cara: el marbre, l'aplic, la porta i els diplomes."""
    cv = Canvas(light=TEX_LIGHT)
    wall(cv)
    sconce(cv, 141)
    PL.door(cv)
    PL.diplomas(cv)
    return cv.img


def _paret_fons(f=None):
    """La paret del fons, de cara: el marbre, les cortines, el finestral (amb el llac) i el retrat."""
    cv = Canvas(light=TEX_LIGHT)
    wall(cv)
    PL.curtain(cv, 187, 203, True)
    PL.curtain(cv, 397, 413, False)
    PL.window(cv, f)
    PL.portrait(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _paret_llisa():
    cv = Canvas(light=TEX_LIGHT)
    wall(cv)
    return cv.img


def _peca(fn, *a, **kw):
    """Una peça del dibuix pla, sola sobre transparent."""
    cv = Canvas(light=TEX_LIGHT, transparent=True)
    fn(cv, *a, **kw)
    return cv.img


DESK_BOX = (PL.DESK[0], PL.DESK_TOP + 6, PL.DESK[1] + 1, PL.FLOOR_Y + 1)   # el frontal de la taula
SHELF_BOX = (425, 24, 576, 158)                    # la llibreria (amb la cornisa)
CHAIR_BOX = (510, 110, 547, 146)                   # el respatller de la cadira
PHOTO_BOX = (437, 136, 461, 157)                   # la foto (la base, a y 155)
PENS_BOX = (536, 134, 560, 155)                    # el portaplomes (la base, a y 154)
LAMP_BOX = (555, 120, 576, 154)                    # el llum de taula (la base, a y 153)
BED_BOX = (204, 178, 263, 208)                     # el llit d'en Rockefeller (a terra, a y 204)
GLOBE_BOX = (298, 144, 342, 204)                   # el globus bar (a terra, a y 201)
BOWL_BOX = (585, 188, 621, 208)                    # el bol (a terra, a y 204)


@functools.lru_cache(maxsize=None)
def _textures():
    return {
        'esq': _paret_esq(),
        'fons': _paret_fons(),
        'llisa': _paret_llisa(),
        'taula': _peca(PL.desk),
        'llibreria': _peca(PL.bookcase),
        'cadira': _peca(PL.chair),
        'foto': _peca(PL.photo),
        'coses': _peca(PL.desk_things),
        'llit': _peca(PL.dog_bed),
        'globus': _peca(PL.globe_bar),
        'bol': _peca(PL.bowl),
    }


# ─── Les superfícies ────────────────────────────────────────────────────────

def _parquet(s, t, P):
    """El parquet de llistons encerat, en coordenades del món: llistons de 14 que fugen cap al fons, a trencajunts."""
    x, z = P[0], P[2]
    col = math.floor(x / 14)
    fz = z + hr(col, 3) * 60
    if x % 14 < 1.0 or fz % 60 < 0.9:
        return 3.0
    return (4.4 + (hr(col, int(fz // 60), 4) - 0.5) * 0.7 + math.sin(x * 0.9 + hr(col, 7) * 6) * 0.12
            + (fbm(x / 50, z / 30, 5) - 0.5) * 0.4)


RUG = (60, 330, 70, 250, 0.08)                     # la catifa: x0, x1, z0, z1 (abans de girar), gir


def _rug_pts(y=0.3):
    x0, x1, z0, z1, a = RUG
    P = _local((x0 + x1) / 2, (z0 + z1) / 2, a)
    hw, hd = (x1 - x0) / 2, (z1 - z0) / 2
    return [P(-hw, y, hd), P(hw, y, hd), P(hw, y, -hd), P(-hw, y, -hd)]


def _rug(s, t, P):
    """La catifa blau marí: la sanefa d'or i un motiu de rombes."""
    w, d = RUG[1] - RUG[0], RUG[3] - RUG[2]
    edge = min(s, t, w - s, d - t)
    n = (hr(int(s), int(t), 6) - 0.5) * 0.6
    if edge < 5:
        return 2.6 + n
    if edge < 9:
        return 2.2 + n
    mot = abs(((s - 11) % 32) - 16) + abs(((t - 8) % 24) - 12) * 1.4 < 4
    dot = abs(((s + 5) % 32) - 16) + abs(((t + 4) % 24) - 12) * 1.4 < 1.5
    return (3.4 if mot else (3.0 if dot else 2.4)) + n


def _rug_or(s, t):
    w, d = RUG[1] - RUG[0], RUG[3] - RUG[2]
    edge = min(s, t, w - s, d - t)
    return edge < 3 or 5 <= edge < 8


def _sol(x, z, y=0.0):
    """Quant sol (0..1) arriba a un punt del món: el raig que entra pel finestral (i se'n veuen els travessers)."""
    t = ZW - z                                       # (la z que ha recorregut des del vidre)
    xw, yw = x - SUN[0] * t, y - SUN[1] * t
    fx, fy = xw + XB, HW - yw                        # el punt del finestral, al dibuix pla
    x0, y0, x1, y1 = PL.WIN
    if not (x0 + 4 < fx < x1 - 4 and y0 + 4 < fy < y1 - 4):
        return 0.0
    for mx in (x0 + 67, x0 + 133):
        if mx - 0.5 <= fx <= mx + 4.5:
            return 0.0                                # un muntant
    if 62.5 <= fy <= 65.5:
        return 0.0                                    # el travesser
    return max(0.0, 1 - t / 340) * 0.36


FOSC = [(4, 4, 8), (9, 8, 14), (15, 13, 20), (23, 20, 28), (33, 28, 37), (45, 38, 48), (60, 50, 60)]


def escena(cv, tex, f=None):
    """Tota la sala, de lluny a prop (`f`: el fotograma del llac, per a l'animació). → l'Escena."""
    e = Escena(cv, CAM, LLUMS, ambient=-0.5)
    zn = CAM.pos[2] + 60
    esq, fons, llisa = tex['esq'], tex['fons'], tex['llisa']
    # el sostre, fosc
    e.quad('sostre', (0, HW, zn), (XR, HW, zn), (XR, HW, ZW), (0, HW, ZW), ramp=MAHOG, lvl=1.4, dues_cares=True)
    # la paret de la porta (x = 0): de prop, la llisa; cap a la cantonada, el dibuix pla (x 0..196)
    e.quad('paret_esq_prop', (0, HW, zn), (0, HW, ZW - XL), (0, 0, ZW - XL), (0, 0, zn),
           tex=(llisa, (W - (ZW - XL - zn), 0, W, HW)))
    e.quad('paret_esq', (0, HW, ZW - XL), (0, HW, ZW), (0, 0, ZW), (0, 0, ZW - XL), tex=(esq, (0, 0, XL, HW)))
    # la paret del fons (z = 300): el dibuix pla (x 186..640) i, a la dreta, la llisa
    e.quad('paret_fons', (0, HW, ZW), (W - XB, HW, ZW), (W - XB, 0, ZW), (0, 0, ZW), tex=(fons, (XB, 0, W, HW)))
    e.quad('paret_fons_dreta', (W - XB, HW, ZW), (XR, HW, ZW), (XR, 0, ZW), (W - XB, 0, ZW),
           tex=(llisa, (0, 0, XR - W + XB, HW)))
    # el terra: el parquet, el sol que entra pel finestral i la catifa
    e.quad('terra', (0, 0, ZW), (XR, 0, ZW), (XR, 0, zn), (0, 0, zn), ramp=WALNUT, lvl=_parquet)
    rp = _rug_pts()
    e.quad('catifa', *rp, ramp=VELVET, lvl=_rug)
    e.quad('catifa', *_rug_pts(0.35), ramp=BRASS, lvl=lambda s, t, P: 2.8 + (hr(int(s), int(t), 7) - 0.5) * 0.6,
           forma=_rug_or)
    e.claror((0, 0.5, ZW), (XR, 0.5, ZW), (XR, 0.5, 0), (0, 0.5, 0), (255, 240, 200),
             lambda s, t: _sol(s, ZW - t))
    # la foscor dels racons
    e.foscor('racons', (0, 0.6, ZW), (XR, 0.6, ZW), (XR, 0.6, zn), (0, 0.6, zn),
             lambda s, t: max(0.55 * max(0.0, 1 - t / 28), 0.5 * max(0.0, 1 - s / 24)))
    e.foscor('cantonada', (0, HW, ZW - 0.5), (60, HW, ZW - 0.5), (60, 0, ZW - 0.5), (0, 0, ZW - 0.5),
             lambda s, t: 0.45 * max(0.0, 1 - s / 60))
    e.foscor('cantonada2', (0.5, HW, ZW - 60), (0.5, HW, ZW), (0.5, 0, ZW), (0.5, 0, ZW - 60),
             lambda s, t: 0.45 * max(0.0, 1 - (60 - s) / 60))
    e.foscor('sostre_fosc', (0, HW - 0.5, ZW - 0.6), (XR, HW - 0.5, ZW - 0.6), (XR, 0, ZW - 0.6), (0, 0, ZW - 0.6),
             lambda s, t: 0.4 * max(0.0, 1 - t / 40))
    e.foscor('sostre_fosc2', (0.6, HW - 0.5, zn), (0.6, HW - 0.5, ZW), (0.6, 0, ZW), (0.6, 0, zn),
             lambda s, t: 0.4 * max(0.0, 1 - t / 40))
    # la llibreria, amb volum: el sòcol de portes i, a sobre, els prestatges del dibuix pla
    sx0, sx1, sz = SHELF
    e.foscor('ombra_llibreria', (sx0 - 6, 0.7, ZW), (sx1 + 8, 0.7, ZW), (sx1 + 8, 0.7, sz - 14), (sx0 - 6, 0.7, sz - 14),
             lambda s, t: 0.5 * min(1.0, max(0.0, (ZW - sz + 14 - t) / 14)))

    def portes(s, t, P):
        w = sx1 - sx0
        v = 3.0 + (hr(int(s), int(t / 5), 63) - 0.5) * 0.3
        if t < 3:
            return 5.0 if t < 1 else 4.0                                  # el cantell
        k = int(s // (w / 4))
        a = s - k * w / 4
        if a < 2 or a > w / 4 - 2 or t < 5 or t > 40:
            return v + (0.8 if a < 2 else -0.6)
        if abs(a - (w / 8 + (6 if k % 2 == 0 else -6))) < 1 and 18 < t < 26:
            return 1.2                                                    # el pany
        return v + 0.4
    e.caixa('llibreria', sx0, sx1, 0, 43, sz - 6, ZW, MAHOG, 2.4,
            cares={'davant': {'ramp': MAHOG, 'lvl': portes}, 'dalt': {'ramp': MAHOG, 'lvl': 4.6},
                   'dreta': {'ramp': MAHOG, 'lvl': 2.0}, 'esquerra': {'ramp': MAHOG, 'lvl': 3.0}})
    e.caixa('llibreria', sx0 + 4, sx1 - 4, 43, _y(SHELF_BOX[1]), sz, ZW, MAHOG, 2.4,
            cares={'davant': {'tex': (tex['llibreria'], SHELF_BOX)}, 'dalt': {'ramp': MAHOG, 'lvl': 3.6},
                   'dreta': {'ramp': MAHOG, 'lvl': 1.8}, 'esquerra': {'ramp': MAHOG, 'lvl': 3.0}})
    # el retrat i el bol (a terra, el dibuix pla dret), amb l'ombra
    bx, bz = BOWL
    e.foscor('ombra_bol', (bx - 18, 0.7, bz + 10), (bx + 18, 0.7, bz + 10), (bx + 18, 0.7, bz - 10), (bx - 18, 0.7, bz - 10),
             lambda s, t: 0.5 * max(0.0, 1 - ((s - 18) / 18) ** 2 - ((t - 10) / 10) ** 2) * 1.5)
    e.sprite('bol', tex['bol'].crop(BOWL_BOX), (602 - BOWL_BOX[0], 204 - BOWL_BOX[1]), (bx, 0, bz), escala_img=0.8)
    # el llit d'en Rockefeller i el globus bar, davant el finestral
    for sid, img, box, foot, (px, pz), k in (('llit', tex['llit'], BED_BOX, (233, 204), BED, 1.0),
                                            ('globus', tex['globus'], GLOBE_BOX, (320, 201), GLOBE, 1.0)):
        e.foscor('ombra_' + sid, (px - 32, 0.7, pz + 16), (px + 32, 0.7, pz + 16), (px + 32, 0.7, pz - 16),
                 (px - 32, 0.7, pz - 16), lambda s, t: 0.5 * max(0.0, 1 - ((s - 32) / 30) ** 2 - ((t - 16) / 15) ** 2) * 1.4)
        e.sprite(sid, img.crop(box), (foot[0] - box[0], foot[1] - box[1]), (px, 0, pz), escala_img=k)
    # la cadira del Director, darrere la taula: el respatller capitonat (el dibuix pla), el seient i el peu
    cx_, cz_ = _DP(CHAIR[0], 0, CHAIR[1])[::2]
    da = DESK[4]
    CP = _local(cx_, cz_, da)
    e.foscor('ombra_cadira', (cx_ - 24, 0.7, cz_ + 16), (cx_ + 24, 0.7, cz_ + 16), (cx_ + 24, 0.7, cz_ - 16),
             (cx_ - 24, 0.7, cz_ - 16), lambda s, t: 0.5 * max(0.0, 1 - ((s - 24) / 22) ** 2 - ((t - 16) / 15) ** 2) * 1.4)
    bk = CP(0, 0, 14)
    e.caixa_girada('cadira', bk[0], bk[2], 36, 7, 38, da, LEATHER, 2.4, y0=32,
                   cares={'davant': {'tex': (tex['cadira'], CHAIR_BOX)}, 'dalt': {'ramp': LEATHER, 'lvl': 4.0}})
    e.tub('cadira', (cx_, 2, cz_), (cx_, 26, cz_), 3, PHONE, 2.4)
    e.caixa_girada('cadira', cx_, cz_, 34, 30, 6, da, LEATHER, 3.2, y0=26,
                   cares={'dalt': {'ramp': LEATHER, 'lvl': 4.0}})
    # la taula: el cos (el frontal del dibuix pla), el tauler i el que hi ha damunt
    dx, dz, dw, dd, _ = DESK
    e.foscor('ombra_taula', *[_DP(lx, 0.7, lz) for lx, lz in ((-dw / 2 - 8, dd / 2 + 6), (dw / 2 + 8, dd / 2 + 6),
                                                             (dw / 2 + 8, -dd / 2 - 14), (-dw / 2 - 8, -dd / 2 - 14))],
             lambda s, t: 0.55 * min(1.0, max(0.0, (dd + 20 - t) / 14)) * min(1.0, s / 10, (dw + 16 - s) / 10))

    def costat(s, t, P):
        v = 2.6 + (hr(int(t / 5), int(s), 63) - 0.5) * 0.3
        if 6 < s < dd - 6 and 6 < t < 32:
            v += 0.4 if (s < 8 or t < 8) else (-0.5 if (s > dd - 8 or t > 30) else 0)
        return v
    e.caixa_girada('taula', dx, dz, dw, dd, DESK_H - 6, da, MAHOG, 2.4,
                   cares={'davant': {'tex': (tex['taula'], DESK_BOX)},
                          'esquerra': {'ramp': MAHOG, 'lvl': costat}, 'dreta': {'ramp': MAHOG, 'lvl': costat},
                          'dalt': {'ramp': MAHOG, 'lvl': 2.0}})

    def tauler(s, t, P):
        v = 4.4 + (hr(int(s / 8), int(t), 61) - 0.5) * 0.3 + math.sin(s * 0.05 + t * 0.6) * 0.08
        if s < 1.5 or t > dd + 8 - 1.5:
            v += 0.8
        return v
    e.caixa_girada('taula', dx, dz, dw + 8, dd + 8, 6, da, MAHOG, 3.6, y0=DESK_H - 6,
                   cares={'dalt': {'ramp': MAHOG, 'lvl': tauler},
                          'davant': {'ramp': MAHOG, 'lvl': lambda s, t, P: 5.4 if t < 1.5 else 3.6},
                          'esquerra': {'ramp': MAHOG, 'lvl': 3.0}, 'dreta': {'ramp': MAHOG, 'lvl': 2.6}})
    # el cartapàs de pell verda, amb uns papers per signar i la ploma
    e.quad('cartapas', *[_DP(lx, DESK_H + 0.3, lz) for lx, lz in ((4, 22), (60, 22), (60, -10), (4, -10))], ramp=BANKG,
           lvl=lambda s, t, P: 2.4 + (hr(int(s), int(t), 2) - 0.5) * 0.4 + (1.6 if (s < 1.5 or s > 54.5 or t < 1.5 or t > 30.5) else 0))
    e.quad('papers', *[_DP(lx, DESK_H + 0.6, lz) for lx, lz in ((12, 16), (38, 18), (38, -6), (12, -8))], ramp=PAPERW,
           lvl=lambda s, t, P: 4.4 - (1.6 if int(t) % 4 == 0 and 3 < s < 22 and t > 4 else 0))
    e.cable('papers', [_DP(42, DESK_H + 1, 4), _DP(52, DESK_H + 1, -4)], PHONE, 2.0, gruix=1.4)
    # el mòbil cap per avall: la carcassa negra, el cantell d'alumini i el mòdul de càmeres
    mp = _DP(-30, 0, -10)
    e.caixa_girada('mobil', mp[0], mp[2], 13, 22, 1.8, da + 0.25, SILVER, 3.4, y0=DESK_H,
                   cares={'dalt': {'ramp': PHONE, 'lvl': lambda s, t, P: (4.6 if 2 < s < 6 and 2 < t < 7 else 2.0)
                                   - (1.8 if (s - 3.2) ** 2 + (t - 3.4) ** 2 < 1.2 or (s - 3.2) ** 2 + (t - 5.8) ** 2 < 1.2 else 0)
                                   + (0.8 if s < 1 or t < 1 else 0)}})
    # la foto amb el llacet, el portaplomes i el llum (el dibuix pla, dret)
    for sid, img, box, foot, lxz in (
            ('foto', tex['foto'], PHOTO_BOX, (449, 155), (-58, 6)),
            ('coses', tex['coses'], PENS_BOX, (548, 154), (34, 18)),
            ('coses', tex['coses'], LAMP_BOX, (565, 152), (66, 22))):
        e.sprite(sid, img.crop(box), (foot[0] - box[0], foot[1] - box[1]), _DP(lxz[0], DESK_H, lxz[1]))
    # el sofà Chesterfield, separat de la paret i girat: la faldilla, el seient, els coixins, el respatller i els braços
    sx, sz, sl, sd, sa = SOFA
    ang = math.pi / 2 + sa                            # (el davant, cap a +x)
    SP = _local(sx, sz, ang)
    e.foscor('ombra_sofa', (sx - 30, 0.7, sz + sl / 2 + 8), (sx + 36, 0.7, sz + sl / 2 + 8),
             (sx + 36, 0.7, sz - sl / 2 - 8), (sx - 30, 0.7, sz - sl / 2 - 8),
             lambda s, t: 0.55 * max(0.0, 1 - ((s - 33) / 33) ** 2 - ((t - sl / 2 - 8) / (sl / 2 + 8)) ** 2) * 1.6)

    def capitone(s, t, P):
        row = int(t // 8)
        dx_ = ((s + (4 if row % 2 else 0)) % 8) - 4
        dy_ = (t % 8) - 4
        d = abs(dx_) + abs(dy_)
        return 3.2 - d * 0.22 - (1.6 if d < 0.8 else 0)

    def part(lx, lz, w, d, h, y0, lvl, cares=None):
        p = SP(lx, 0, lz)
        e.caixa_girada('sofa', p[0], p[2], w, d, h, ang, LEATHER, lvl, y0=y0, cares=cares)
    # (de lluny a prop: les potes, el respatller, el braç del fons, el seient i els coixins, i el braç de prop)
    for lx in (sl / 2 - 4, -sl / 2 + 4):
        for lz in (sd / 2 - 4, -sd / 2 + 4):
            part(lx, lz, 4, 4, 4, 0, 1.4)
    part(0, sd / 2 - 6, sl - 4, 12, 30, 24, 2.2,
         cares={'davant': {'ramp': LEATHER, 'lvl': capitone}, 'dalt': {'ramp': LEATHER, 'lvl': 4.4}})

    def brac(lx):
        part(lx, 0, 14, sd, 46, 4, 2.0,
             cares={'dalt': {'ramp': LEATHER, 'lvl': lambda s, t, P: 4.6 - abs(s - 7) * 0.25},
                    'davant': {'ramp': LEATHER, 'lvl': lambda s, t, P: (3.8 - math.hypot(s - 7, t - 7) * 0.15) if t < 14 else 2.0},
                    'esquerra': {'ramp': LEATHER, 'lvl': capitone}, 'dreta': {'ramp': LEATHER, 'lvl': capitone}})
    brac(sl / 2 - 7)
    part(0, 0, sl - 4, sd - 4, 20, 4, 1.6, cares={
        'davant': {'ramp': LEATHER, 'lvl': lambda s, t, P: 1.8 + (3.0 if t < 2 and int(s) % 4 == 0 else 0)
                   - (0.6 if t > 17 else 0)},
        'dalt': {'ramp': LEATHER, 'lvl': 2.6}})
    for k in range(3):                                                # els coixins
        part(-sl / 2 + 14 + (sl - 28) * (k + 0.5) / 3, -2, (sl - 28) / 3 - 1, sd - 14, 6, 24, 2.6,
             cares={'dalt': {'ramp': LEATHER, 'lvl': lambda s, t, P: 4.2 - abs(t - 13) * 0.06 - (1.6 if s < 1 else 0)},
                    'davant': {'ramp': LEATHER, 'lvl': lambda s, t, P: 2.8 - (1.2 if s < 1 else 0)}})
    brac(-sl / 2 + 7)
    # primer pla: una butaca d'orelles a baix a l'esquerra i una pilastra de marbre a la dreta, en silueta
    for cx, cz, w, d, h, a, y0, lv in ((30, 30, 60, 54, 30, 0.5, 4, 1.6), (12, 46, 60, 16, 76, 0.5, 4, 1.4),
                                       (50, 2, 14, 54, 52, 0.5, 4, 2.0)):
        e.caixa_girada('primer_pla', cx, cz, w, d, h, a, FOSC, lv, y0=y0,
                       cares={'dalt': {'ramp': FOSC, 'lvl': lv + 1.2}, 'dreta': {'ramp': FOSC, 'lvl': lv + 0.8}})
    e.tub('primer_pla', (486, 0, 46), (486, HW + 40, 46), 14, FOSC, 2.0, llum_dir=(-0.9, -0.2))
    return e


# ─── Composició i llum ──────────────────────────────────────────────────────

def _proj(P):
    u, v, _ = CAM.projecta(P)
    return u, v


def _raig():
    """El raig de sol que entra pel finestral: del vidre fins al terra (en coordenades de sala)."""
    x0, x1, y0, y1 = WIN
    a = [(x0 + 6, y1 - 6, ZW), (x1 - 6, y1 - 6, ZW), (x1 - 6, y0 + 6, ZW), (x0 + 6, y0 + 6, ZW)]

    def terra(P):
        t = P[1] / -SUN[1]
        return (P[0] + SUN[0] * t, 0, P[2] + SUN[2] * t)
    b = [terra(P) for P in a]
    return [_proj(P) for P in (a[0], a[1], b[1], b[2], b[3], b[0])]


def _fx():
    wx, wy = _proj(WIN_C)
    light = [llum.wash(wx, wy + 30, 300, (255, 236, 196), k=0.45, air=0.05, squash=0.9),
             llum.haze(_raig(), (255, 236, 190), k=0.12, blur=8)]
    tone = [llum.grade(contrast=1.1, pivot=70, sat=1.12, lift=(2, 2, 6))]
    x0, y0 = _proj((WIN[0], WIN[3], ZW))
    x1, y1 = _proj((WIN[1], WIN[2], ZW))
    bloom = [llum.bloom(thr=200, radii=((3, 0.35), (10, 0.25)),
                        mask=lambda x, y: (x > x0) & (x < x1) & (y > y0) & (y < y1))]
    return light, bloom, tone


def _render(f=None, tex=None):
    cv = Canvas(light=LIGHT)
    e = escena(cv, tex or _textures(), f)
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


# ─── Animació: el llac i el Jet d'Eau ──────────────────────────────────────

ANIM_N = PL.ANIM_N


def _frames():
    """L'aigua es mou, el Jet d'Eau bufa i el vaixell es gronxa: el finestral, projectat a la paret."""
    img0, e = _base()
    out = []
    for i in range(ANIM_N):
        img = img0.copy()
        img.alpha_composite(e.capa(_diff(_paret_fons(f=i), _textures()['fons']), {'paret_fons'}))   # (només el que canvia)
        out.append(_diff(_amb_llum(img), _base_llum()))
    return out


ANIMS = {'llac': {'frames': _frames, 'frameDuration': 70}}


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
    back = max(_p(*_DP(lx, 0, dd / 2 + 4)[::2])[1] for lx in (-dw / 2, dw / 2))
    front = min(_p(*_DP(lx, 0, -dd / 2 - 4)[::2])[1] for lx in (-dw / 2, dw / 2))
    return (back + front) // 2


# Capes del davant: el primer pla (sempre davant), la taula (amb el que hi ha damunt) i el sofà, el globus i el llit
# (qui hi passa per darrere, hi queda darrere).
FRONT = [
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20},
    {'id': 'davant_taula', 'mask': _amo({'taula', 'cartapas', 'papers', 'mobil', 'foto', 'coses'}),
     'baseline': _desk_baseline(), 'zIndex': 20},
    {'id': 'davant_globus', 'mask': _amo({'globus'}), 'baseline': _p(GLOBE[0], GLOBE[1] - 10)[1], 'zIndex': 20},
]


# ─── Geometria (coordenades de sala, projectades) ────────────────────────────

def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


def _z_a(x, v):
    """La z del terra que es veu a la y de pantalla `v`, a la x del món `x`."""
    lo, hi = -400.0, 400.0
    for _ in range(50):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if CAM.projecta((x, 0, m))[1] > v else (lo, m)
    return lo


V_PROP = 222                                       # el terra on es camina s'acaba aquí (escala ≈1,2)
# El terra on es camina (al món): de la porta fins a la taula, davant el finestral (entre el llit i el globus) i
# per darrere la taula (s'hi entra per la dreta), fins al bol.
WALK_MON = [(12, 110), (12, 186), (66, 184), (78, 250), (130, 252), (130, 290), (180, 290), (182, 246),
            (222, 244), (232, 196), (380, 166), (402, 210), (300, 258), (306, 272), (452, 272), (470, 120)]
_WALK = [_p(x, z) for x, z in WALK_MON]
_WALK += [(_p(WALK_MON[-1][0], _z_a(WALK_MON[-1][0], V_PROP))[0], V_PROP),
          (_p(WALK_MON[0][0], _z_a(WALK_MON[0][0], V_PROP))[0], V_PROP)]
_V_FONS = min(v for _, v in _WALK)


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


_DOOR = (_wz(19), _wz(82), _y(200), _y(53))        # la porta: z0, z1, y0, y1 (a la paret de l'esquerra)
_MP = _DP(-30, 0, -10)

GEOMETRIA = {
    'things': {
        'porta': {'rect': _rect_mon((0, _DOOR[3], _DOOR[0]), (0, _DOOR[2], _DOOR[1])), 'walk': _p(30, 156)},
        'finestra': {'rect': _rect_mon((WIN[0], WIN[3], ZW), (WIN[1], WIN[2], ZW)), 'walk': _p(156, 262)},
        'foto': {'rect': _rect_mon(*[_DP(lx, y, lz) for lx in (-66, -50) for lz in (2, 10) for y in (DESK_H, DESK_H + 22)]),
                 'walk': _p(*_DP(-56, 0, -DESK[3] / 2 - 26)[::2])},
        'mobil': {'rect': _rect_mon(*[(_MP[0] + dx, DESK_H + y, _MP[2] + dz) for dx in (-12, 12) for dz in (-12, 12)
                                      for y in (0, 4)]),
                  'walk': _p(*_DP(-26, 0, -DESK[3] / 2 - 26)[::2])},
        'bol': {'rect': _rect_mon(*[(BOWL[0] + dx, y, BOWL[1] + dz) for dx in (-16, 16) for dz in (-8, 8) for y in (0, 12)]),
                'walk': _p(BOWL[0] - 10, BOWL[1] - 18)},
        # el retrat a l'oli d'en Rockefeller, a la paret de la dreta, sobre el bol (tasca 290): és el primer que es
        # clica buscant el gos (rectangle de pantalla)
        'retrat': {'rect': (478, 24, 524, 92), 'walk': _p(BOWL[0] - 10, BOWL[1] - 18)},
    },
    'spawns': {'vet': _p(150, 170), 'bonfill': _p(156, 262), 'ballester': _p(40, 150)},
    'walkable': _WALK,
    'floorSquash': 0.4,                            # (la càmera, picada: el terra es veu aixafat)
    # L'ombra de contacte: la llum dominant és el finestral (el punt del terra sota el vidre); llarga, cap endavant.
    'characterShadow': {'enabled': True, 'color': '#0a0a18', 'alpha': 0.4, 'squash': 0.38, 'core': 0.6,
                        'light': {'x': _p(WIN_C[0], ZW - 10)[0], 'y': _p(WIN_C[0], ZW - 10)[1], 'stretch': 0.8,
                                  'reach': 200}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, V_PROP + 2), (0, V_PROP + 2)]}],
    # la llum de la sala sobre els personatges, en temps d'execució
    'characterLights': {
        'ambient': '#9a98a8',                                                           # llum de dia, freda
        'lights': [
            {'x': round(_proj(WIN_C)[0]), 'y': round(_proj(WIN_C)[1]) + 40, 'radius': 300,
             'color': '#fff0c8', 'intensity': 0.9},                                     # el finestral
            {'x': round(_proj(SCONCE)[0]), 'y': round(_proj(SCONCE)[1]), 'radius': 90,
             'color': '#ffd696', 'intensity': 0.4},                                     # l'aplic
        ],
    },
}
