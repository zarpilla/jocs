"""
Moll de càrrega de la fàbrica (Acte 2, Iri), de nit. EN 3D (hd640/tres_d.py), a 1×.

Una càmera alta que mira de biaix la cantonada del fons a l'esquerra:
  - a la paret de l'esquerra, en escorç, la **porta de les calderes** entreoberta: el foc s'escampa pel terra en
    diagonal;
  - a la paret del fons (maó), el rètol «MATERIAL F-9», el **bastidor** amb la biga de ferro-9, el **conducte** de
    pressió de coure (ve de les calderes per sota la biga del sostre i baixa fins a terra), el **tauler d'eines** amb
    l'aplic, i la **badia**: un entrant de debò, amb la **llançadora** nova a dins i la **comporta** tancada al fons,
    per sota de la qual s'escola la lluna (una llengua freda pel terra);
  - al mig, separat de la paret, el **pilar 7** (s'hi passa per darrere) amb la reixa del desguàs (la **trapa**) als
    peus, i els **cavallets** girats amb la biga d'acer, sota la làmpada penjada (s'hi passa per darrere);
  - el carril de la vagoneta surt de la badia i fuig cap al davant;
  - primer pla: caixes de fusta en silueta a baix a l'esquerra, un pilar de ferro fosc a la dreta i la cadena d'un
    polispast que penja.

Tot el detall de les parets ve del dibuix pla de sempre (fabrica_moll_pla_comu.py), projectat; els decorats de la
paret (la biga de ferro-9, la serra, la llima) es projecten per la mateixa paret, i la biga d'acer és en 3D.

El món: x a la dreta (0 = la paret de les calderes), y amunt (0 = el terra), z cap al fons (300 = la paret del fons);
1 unitat = 1 píxel de sala a la distància on un personatge fa ≈110 px (escala 1).
"""
import functools
import math
import random

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from PIL import Image, ImageChops

from hd.pix import (Canvas, Light, W, H, hr, mix, B4, WALNUT, FLOOR, GOLD, COPPER, BRICK, IRON, GREEN, PAPER, GRAY,
                    MANILA)
from hd.rooms.exterior import fbm
from hd640.rooms import fabrica_moll_pla_comu as PL
from hd640.rooms.fabrica_moll_pla_comu import ClipCanvas, F9, ACER, MORTAR, FLOOR_Y
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
ZW = 300                                           # la paret del fons
HW = 204                                           # l'alçada de les parets (el dibuix pla fa 204 fins al terra)
XL = 96                                            # al dibuix pla, la cantonada: a l'esquerra, la paret de les calderes
XR = 760                                           # on s'acaba la paret del fons (fora de la pantalla)
FB0, FB1 = 445, 635                                # al dibuix pla, la boca de la badia
ZB = 410                                           # el fons de la badia (la comporta)
ZS = 352                                           # el pla de la llançadora, dins la badia
PILAR = (280, 190)                                 # el pilar 7 (x, z)
CAV = (150, 170, 0.48)                             # els cavallets: x, z del centre, gir
CAV_H, CAV_L = 40, 112                             # l'alçada dels cavallets; la distància entre tots dos
BIGA = (156, 10, 9)                                # la biga d'acer: llarg, ample, alt
LAMP = (150, 110, 168)                             # la bombeta de la làmpada penjada
VIA = (430, 460)                                   # els carrils de la vagoneta (x)
PIL2 = (468, 10)                                   # el pilar de ferro del primer pla (x, z)
CADENA = (438, 60)                                 # la cadena del polispast (x, z)


class _Cv(Canvas):
    """El llenç de l'escena (tres_d vol saber quants píxels reals fa un de sala)."""
    S = 1


def _w(fx):
    """Una x del dibuix pla de la paret del fons → la x del món."""
    return fx - XL


def _wz(fx):
    """Una x del dibuix pla de la paret de les calderes → la z del món."""
    return ZW - XL + fx


def _y(fy):
    """Una y del dibuix pla (el terra, a 204) → l'alçada del món."""
    return HW - fy


BX0, BX1 = _w(FB0), _w(FB1)                         # la badia, al món
DOOR = (_wz(17), _wz(69), _y(FLOOR_Y), _y(93))      # el forat de la porta: z0, z1, y0, y1

CAM = Camera(pos=(400, 190, -300), yaw=-0.32, pitch=0.16, f=480, centre=(320, 80))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)  # (la llum és la del món: la de l'Escena)

# La llum del dibuix pla de les textures: la de sempre, sense la vinyeta (ara les vores no són les de la pantalla).
TEX_LIGHT = Light(vignette=None, floor_fade=None)
TEX_LIGHT.points = list(PL.LIGHT.points)
TEX_LIGHT.extra = list(PL.LIGHT.extra)

LLUMS = [Llum(LAMP, 270, 2.2, power=1.4),                                   # la làmpada penjada
         Llum((6, 50, (DOOR[0] + DOOR[1]) / 2), 230, 2.2, power=1.6),       # el foc de les calderes
         Llum((_w(405), _y(56), ZW - 6), 120, 1.2, power=1.6),              # l'aplic del tauler d'eines
         Llum(((BX0 + BX1) / 2, 186, ZS - 10), 170, 1.6, power=1.5),        # el llum de servei de la badia
         Llum(((BX0 + BX1) / 2, 4, ZB - 6), 230, 1.2, power=1.3)]           # la lluna, per sota la comporta


# ─── Les textures: el dibuix pla de sempre ───────────────────────────────────

_FORA = ('pillar', 'crate', 'dust', 'shuttle', 'grate', 'floor_planks')     # el que ara és en 3D (o no hi és)
_BEAM = [3.2, 3.0, 2.4, 1.8, 1.6, 1.4, 1.4, 1.4, 1.2, 1.0, 0.4]


def _tapa(img, boxes):
    """Torna a posar la biga del sostre, el maó i el sòcol dins les caixes (on el pla hi tenia els cavallets o la
    làmpada, que ara són en 3D)."""
    for b in boxes:
        c = ClipCanvas(img, [b], light=TEX_LIGHT)
        c.rect(0, 17, W - 1, 27, IRON, lambda x, y: _BEAM[y - 17] + (hr(x // 5, y, 4) - 0.5) * 0.2)
        PL.bricks(c, 0, 28, W - 1, FLOOR_Y - 1, base=2.0, seed=51)
        c.darken(0, 28, W - 1, 36, lambda x, y: (37 - y) / 9)
        c.rect(0, FLOOR_Y - 7, W - 1, FLOOR_Y - 1, GRAY, lambda x, y: 1.4 + (0.8 if y == FLOOR_Y - 7 else 0)
               + (0.3 if y == FLOOR_Y - 6 else 0) + (hr(x // 19, 2) - 0.5) * 0.4 - (0.8 if x % 19 == 0 else 0))


def _pla(cv, t=0.0):
    """El fons pla de sempre (les parets, la porta, el conducte, el bastidor, el tauler i la comporta), sense el que ara
    és en 3D: el pilar, les caixes, la pols, la llançadora, les reixes, el terra, els cavallets i la làmpada."""
    desa = {k: getattr(PL, k) for k in _FORA}
    try:
        for k in _FORA:
            setattr(PL, k, lambda *a, **kw: None)
        PL.bg(cv, t)
    finally:
        for k, v in desa.items():
            setattr(PL, k, v)
    _tapa(cv.img, [(112, 176, 274, FLOOR_Y - 1), (183, 27, 217, 54)])


@functools.lru_cache(maxsize=None)
def _paret():
    cv = Canvas(light=TEX_LIGHT)
    _pla(cv)
    return cv.img


def _paret_t(t):
    """El fons pla al moment t (0..1) de l'animació: només el foc de la porta i l'escletxa de la comporta."""
    img = _paret().copy()
    for b in ((14, 90, 72, FLOOR_Y - 1), (469, 180, 617, 188)):
        _pla(ClipCanvas(img, [b], light=TEX_LIGHT), t)
    return img


@functools.lru_cache(maxsize=None)
def _llancadora():
    cv = Canvas(light=TEX_LIGHT, transparent=True)
    PL.shuttle(cv, 451, 144)
    return cv.img


SHUT_BOX = (447, 88, 633, 208)                     # la llançadora, al dibuix pla (amb les aletes i el bressol)
PILLAR_BOX = (326, 28, 361, 204)                   # el pilar 7, al dibuix pla
LAMP_BOX = (183, 26, 218, 51)


def _pilar_img(marca=False):
    cv = Canvas(light=TEX_LIGHT, transparent=True)
    PL.pillar(cv, 343, 28, FLOOR_Y - 1)
    if marca:
        PL.carved_mark(cv, 336, 107)
    return cv.img.crop(PILLAR_BOX)


@functools.lru_cache(maxsize=None)
def _pilar_base():
    return _pilar_img()


@functools.lru_cache(maxsize=None)
def _lamp_img():
    """La làmpada penjada (la pantalla verda d'esmalt i la bombeta), com al pla."""
    cv = Canvas(light=TEX_LIGHT, transparent=True)
    cv.rect(198, 35, 202, 37, GOLD, 2.6)
    for y in range(37, 46):
        hw = 3 + (y - 37) * 1.6
        for x in range(round(200 - hw), round(200 + hw) + 1):
            cv.put(x, y, GREEN, 3.0 - (x - 200) / hw * 1.2 - (y - 37) * 0.1 + (0.9 if y == 45 else 0), 0.3)
    cv.hline(185, 215, 46, [(255, 240, 190)], 0, 0)
    cv.disc(200, 48, 3.2, 2.1, PAPER, 6, 0)
    return cv.img.crop(LAMP_BOX)


@functools.lru_cache(maxsize=None)
def _textures():
    return {'paret': _paret(), 'llancadora': _llancadora().crop(SHUT_BOX), 'pilar': _pilar_base(), 'lamp': _lamp_img()}


# ─── Les superfícies ────────────────────────────────────────────────────────

def _mao(lvl0, seed=3, beam=True):
    """Maó de 16×7 en coordenades del món (s, t des del cantó de dalt, com al pla): on el dibuix pla no arriba."""
    def L(s, t, P):
        if beam and t < 17:
            return 0.5 + (0.5 if int(s) % 32 in (0, 1) else 0)                 # els taulons del sostre
        if beam and t < 28:
            return _BEAM[min(10, int(t) - 17)] - 0.4
        r = int((t - 28) // 7)
        off = 8 if r % 2 else 0
        if (t - 28) % 7 > 6 or (s + off) % 16 < 1:
            return lvl0 - 0.2
        v = lvl0 + (hr(int((s + off) // 16), r, seed) - 0.5) * 1.0 + (0.4 if (t - 28) % 7 < 1 else 0)
        if t > HW - 7:
            v = 1.4 + (0.8 if t < HW - 6 else 0)                                # el sòcol de pedra
        if t < 37:
            v -= (37 - t) / 9 * 1.2                                           # l'ombra de la biga
        return v
    return L


def _terra(s, t, P):
    """Els taulons del terra, en coordenades del món: fugen cap al fons, amb les juntes de testa i els claus."""
    x, z = P[0], P[2]
    pl = math.floor(x / 22)
    r = hr(pl, 5)
    v = 1.9 + (hr(pl, math.floor((z + r * 130) / 130)) - 0.5) * 0.7 + (fbm(x / 50, z / 24, 4) - 0.5) * 0.5
    if x % 22 < 1.0:
        return 0.5
    if x % 22 < 2.0:
        v += 0.3
    zz = (z + r * 130) % 130
    if zz < 1.0:
        return 0.7
    if zz < 4 and abs(x % 22 - 11) > 6 and abs(x % 22 - 11) < 8:
        return 3.2                                                          # els claus de la punta
    if hr(int(x // 3), int(z // 9), 77) > 0.93:
        v -= 0.5                                                            # taques d'oli
    return v


def _reixa(w, d):
    """Una reixa de desguàs encastada al terra: el marc, els barrots (al llarg de z) i el travesser del mig."""
    def L(s, t, P):
        if s < 2.4 or s > w - 2.4 or t < 2.4 or t > d - 2.4:
            return 3.4 if (s < 1.2 or t < 1.2) else 2.4
        if abs(t - d / 2) < 0.9:
            return 2.8
        if s % 4.0 < 1.3:
            return 3.0 - (t / d) * 0.4
        return -0.4 + (0.6 if t > d - 5 and hr(int(s), 70) > 0.6 else 0)
    return L


def _dins(x, z, poly):
    sg = 0
    for (ax, az), (bx, bz) in zip(poly, poly[1:] + poly[:1]):
        c = (bx - ax) * (z - az) - (bz - az) * (x - ax)
        if c and sg and (c > 0) != (sg > 0):
            return False
        sg = sg or c
    return True


def _rot(cx, cz, ang):
    c, s_ = math.cos(ang), math.sin(ang)

    def P(lx, y, lz):
        return (cx + lx * c - lz * s_, y, cz + lx * s_ + lz * c)
    return P


GRATES = [(28, 66, 196, 216), (130, 168, 236, 256), (PILAR[0] - 20, PILAR[0] + 20, PILAR[1] - 46, PILAR[1] - 26)]
TRAPA = GRATES[2]
FOSC = [(4, 3, 6), (9, 6, 9), (15, 10, 12), (22, 15, 16), (31, 21, 20), (42, 29, 26), (58, 40, 32)]


def _cavallets(e, biga=False):
    """Els dos cavallets de fusta, girats, i (decorat) la biga d'acer al damunt."""
    cx, cz, ang = CAV
    P = _rot(cx, cz, ang)
    for lx in (-CAV_L / 2, CAV_L / 2):
        for lz in (-1, 1):                                              # les potes, obertes
            for k in (-1, 1):
                e.cable('cavallets', [P(lx + k * 7, CAV_H - 3, lz * 2), P(lx + k * 18, 0.5, lz * 9)], WALNUT,
                        3.8 if lz < 0 else 2.2, gruix=3.6)
        e.caixa_girada('cavallets', *P(lx, 0, 0)[::2], 38, 7, 5, ang, WALNUT, 3.0, y0=CAV_H - 5,
                       cares={'dalt': {'ramp': WALNUT, 'lvl': lambda s, t, P_: 4.4 + (hr(int(s // 4), 8) - 0.5) * 0.4},
                              'davant': {'ramp': WALNUT, 'lvl': 2.6}})
        e.cable('cavallets', [P(lx - 13, 14, -6), P(lx + 13, 14, -6)], WALNUT, 3.0, gruix=2.4)   # el travesser
    if biga:
        L, bw, bh = BIGA

        def costat(s, t, P_):
            v = 2.6 - t * 0.12 + (hr(int(s // 4), 61) - 0.5) * 0.4
            if 2.6 < t < 3.6:
                v -= 1.2                                                    # l'ala de la biga en I
            if int(s) % 31 == 8 and 3 < t < 7:
                return 5.6                                                  # les marques de guix
            return v
        e.caixa_girada('biga_acer', cx, cz, L, bw, bh, ang, ACER, 2.6, y0=CAV_H,
                       cares={'dalt': {'ramp': ACER, 'lvl': lambda s, t, P_: 5.0 - (1.4 if 3.5 < t < 6.5 else 0)
                                       + (hr(int(s // 4), 61) - 0.5) * 0.4},
                              'davant': {'ramp': ACER, 'lvl': costat},
                              'esquerra': {'ramp': ACER, 'lvl': 4.4}, 'dreta': {'ramp': ACER, 'lvl': 1.4}})


def escena(cv, tex, estat=frozenset()):
    """Tota la sala, de lluny a prop. `estat`: els decorats en 3D que hi són ('biga_acer'). → l'Escena."""
    e = Escena(cv, CAM, LLUMS, ambient=-0.5)
    zn = CAM.pos[2] + 60
    paret = tex['paret']
    gx0, gx1 = BX0 + 7, BX1 - 7
    # 'surt:<k>': la llançadora se'n va (la fugida de l'Iri), k de 0 (al bressol) a 1 (fora)
    surt = next((float(x.split(':')[1]) for x in estat if x.startswith('surt:')), None)
    obre, nau = _surt_moll(surt) if surt is not None else (0.0, (0.0, ZS))
    hc = _y(12)                                                         # l'alçada de la comporta
    sx0, sy0, sx1, sy1 = SHUT_BOX

    def llancadora():
        dy, zs = nau[0], nau[1]
        dx = nau[2] if len(nau) > 2 else 0.0
        if dy is None:
            return
        e.quad('llancadora', (_w(sx0) + dx, 207 - sy0 + dy, zs), (_w(sx1) + dx, 207 - sy0 + dy, zs),
               (_w(sx1) + dx, 207 - sy1 + dy, zs), (_w(sx0) + dx, 207 - sy1 + dy, zs),
               tex=(tex['llancadora'], (0, 0, sx1 - sx0, sy1 - sy0)))
        if surt is not None and dy > 0:                                 # la tobera encesa, a popa (a la dreta)
            tx, ty = _w(sx1) - 6 + dx, 207 - (sy0 + sy1) / 2 + dy - 4
            e.tub('llancadora', (tx, ty, zs - 2), (tx + 26, ty, zs - 2), 7.0, NIT, 9.0, llum_dir=(0.0, 1.0))
            e.tub('llancadora', (tx, ty, zs - 3), (tx + 16, ty, zs - 3), 4.0, NIT, 10.0, llum_dir=(0.0, 1.0))
    # ── la badia: la comporta al fons (pujant, i la nit a fora), les parets, el sostre i el terra ──
    if obre > 0:
        e.quad('comporta', (BX0 - 60, hc + 60, ZB + 60), (BX1 + 60, hc + 60, ZB + 60), (BX1 + 60, -30, ZB + 60),
               (BX0 - 60, -30, ZB + 60), tex=(_nit(), (0, 0, 400, 300)))
        if nau[1] > ZB:
            llancadora()
        r0 = 12 + (189 - 12) * obre                                     # la fulla puja: se'n veu el tros de baix
        if r0 < 188:
            e.quad('comporta', (BX0, hc, ZB), (BX1, hc, ZB), (BX1, hc * obre, ZB), (BX0, hc * obre, ZB),
                   tex=(paret, (469, r0, 617, 189)))
    else:
        e.quad('comporta', (BX0, _y(12), ZB), (BX1, _y(12), ZB), (BX1, 0, ZB), (BX0, 0, ZB),
               tex=(paret, (469, 12, 617, 189)))
    e.quad('badia', (BX0, _y(12), ZW), (BX0, _y(12), ZB), (BX0, 0, ZB), (BX0, 0, ZW), ramp=BRICK,
           lvl=_mao(1.2, seed=8, beam=False))
    e.quad('badia', (BX1, _y(12), ZB), (BX1, _y(12), ZW), (BX1, 0, ZW), (BX1, 0, ZB), ramp=BRICK,
           lvl=_mao(1.0, seed=9, beam=False))
    e.quad('badia', (BX0, _y(12), ZW), (BX1, _y(12), ZW), (BX1, _y(12), ZB), (BX0, _y(12), ZB), ramp=IRON,
           lvl=lambda s, t, P: 0.6 + (1.2 if int(s) % 40 < 3 else 0), dues_cares=True)
    e.quad('badia', (BX0, 0, ZB), (BX1, 0, ZB), (BX1, 0, ZW), (BX0, 0, ZW), ramp=FLOOR, lvl=_terra)
    for rz in (ZS - 18, ZS + 18):                                       # els carrils de la llançadora
        e.quad('badia', (BX0, 0.4, rz + 1.5), (BX1, 0.4, rz + 1.5), (BX1, 0.4, rz - 1.5), (BX0, 0.4, rz - 1.5),
               ramp=IRON, lvl=lambda s, t, P: 4.0 - t * 0.8)
    # la lluna que s'escola per sota la comporta: una llengua freda pel terra de la badia i del moll
    e.claror((gx0 - 10, 0.5, ZB), (gx1 + 10, 0.5, ZB), (gx1 + 60, 0.5, ZW - 170), (gx0 - 40, 0.5, ZW - 170),
             (130, 152, 215), lambda s, t: 0.42 * max(0.0, 1 - t / 300) ** 1.1 * min(1.0, s / 30, (gx1 - gx0 + 60 - s) / 40))
    e.foscor('badia_racons', (BX0, 0.6, ZB), (BX1, 0.6, ZB), (BX1, 0.6, ZW), (BX0, 0.6, ZW),
             lambda s, t: max(0.5 * max(0.0, 1 - s / 22), 0.5 * max(0.0, 1 - (BX1 - BX0 - s) / 22)))
    # la llançadora, nova de trinca, damunt el bressol (el dibuix pla, al seu pla)
    if nau[0] is not None and nau[1] <= ZS + 1:
        k_om = max(0.0, 1 - nau[0] / 30)
        e.foscor('badia_ombra', (_w(sx0) + 10, 0.7, ZS + 22), (_w(sx1) - 10, 0.7, ZS + 22), (_w(sx1) - 10, 0.7, ZS - 26),
                 (_w(sx0) + 10, 0.7, ZS - 26), lambda s, t: 0.55 * k_om * max(0.0, 1 - abs(t - 24) / 24))
    if nau[1] <= ZB:
        llancadora()
    # ── la paret del fons (z = 300): el dibuix pla fins a la badia, la llinda, el muntant i més maó ──
    e.quad('paret_fons', (0, HW, ZW), (_w(FB0), HW, ZW), (_w(FB0), 0, ZW), (0, 0, ZW), tex=(paret, (XL, 0, FB0, HW)))
    e.quad('paret_fons', (BX0, HW, ZW), (BX1, HW, ZW), (BX1, _y(12), ZW), (BX0, _y(12), ZW),
           tex=(paret, (FB0, 0, FB1, 12)))
    e.quad('paret_fons', (BX1, HW, ZW), (_w(W), HW, ZW), (_w(W), 0, ZW), (BX1, 0, ZW), tex=(paret, (FB1, 0, W, HW)))
    e.quad('paret_fons_dreta', (_w(W), HW, ZW), (XR, HW, ZW), (XR, 0, ZW), (_w(W), 0, ZW), ramp=BRICK,
           lvl=_mao(1.6, seed=5))
    # ── la paret de les calderes (x = 0): de prop, maó; cap a la cantonada, el dibuix pla (la porta) ──
    e.quad('paret_esq_prop', (0, HW, zn), (0, HW, ZW - XL), (0, 0, ZW - XL), (0, 0, zn), ramp=BRICK,
           lvl=_mao(1.8, seed=4))
    e.quad('paret_esq', (0, HW, ZW - XL), (0, HW, ZW), (0, 0, ZW), (0, 0, ZW - XL), tex=(paret, (0, 0, XL, HW)))
    # el conducte de coure continua per la paret de l'esquerra, cap a la paret de les calderes (on el pla no arriba)
    e.tub('conducte_esq', (1 + 7, _y(42), zn + 40), (1 + 7, _y(42), ZW - XL), 7, COPPER, 2.6, brides=61,
          llum_dir=(0.6, 1.0))
    # ── el terra ──
    e.quad('terra', (0, 0, ZW), (XR, 0, ZW), (XR, 0, zn), (0, 0, zn), ramp=FLOOR, lvl=_terra)
    for x0, x1, z0, z1 in GRATES:                                       # les reixes de desguàs (la del pilar, la trapa)
        e.quad('trapa' if (x0, x1, z0, z1) == TRAPA else 'reixes', (x0, 0.3, z1), (x1, 0.3, z1), (x1, 0.3, z0),
               (x0, 0.3, z0), ramp=IRON, lvl=_reixa(x1 - x0, z1 - z0))
    # el carril de la vagoneta: surt de la badia i fuig cap al davant
    for k in range(int(zn) + 6, ZB, 22):
        e.quad('via', (VIA[0] - 9, 0.4, k + 5), (VIA[1] + 9, 0.4, k + 5), (VIA[1] + 9, 0.4, k), (VIA[0] - 9, 0.4, k),
               ramp=WALNUT, lvl=lambda s, t, P: 2.0 + (hr(int(P[2]), 3) - 0.5) * 0.6 - (0.6 if t > 4 else 0))
    for rx in VIA:
        e.quad('via', (rx - 1.5, 1.6, ZB), (rx + 1.5, 1.6, ZB), (rx + 1.5, 1.6, zn), (rx - 1.5, 1.6, zn), ramp=IRON,
               lvl=lambda s, t, P: 4.2 - s * 0.6)
        e.quad('via', (rx - 1.5, 1.6, zn), (rx - 1.5, 0, zn), (rx - 1.5, 0, ZB), (rx - 1.5, 1.6, ZB), ramp=IRON, lvl=1.8,
               dues_cares=True)
    # la llum: el bassal de la làmpada, el foc de la porta (en diagonal) i la lluna
    e.claror((LAMP[0] - 130, 0.5, LAMP[2] + 130), (LAMP[0] + 130, 0.5, LAMP[2] + 130),
             (LAMP[0] + 130, 0.5, LAMP[2] - 130), (LAMP[0] - 130, 0.5, LAMP[2] - 130), (255, 214, 140),
             lambda s, t: 0.26 * max(0.0, 1 - math.hypot(s - 130, t - 130) / 130) ** 1.5)
    dz = (DOOR[0] + DOOR[1]) / 2

    def foc(s, t):
        x, z = s, ZW - t
        if x < 1:
            return 0.0
        a = (z - dz) / x                                                # el feix s'obre en diagonal cap al davant
        if not -1.6 < a < 0.25:
            return 0.0
        return 0.55 * max(0.0, 1 - x / 320) ** 1.2 * min(1.0, (a + 1.6) * 1.4, (0.25 - a) * 4)
    e.claror((0, 0.5, ZW), (340, 0.5, ZW), (340, 0.5, zn + 60), (0, 0.5, zn + 60), (255, 130, 50), foc)
    # la foscor dels racons i de la vora de les parets
    e.foscor('racons', (0, 0.5, ZW), (XR, 0.5, ZW), (XR, 0.5, zn), (0, 0.5, zn),
             lambda s, t: max(0.55 * max(0.0, 1 - t / 26), 0.45 * max(0.0, 1 - s / 22)))
    e.foscor('cantonada', (0, HW, ZW - 0.5), (70, HW, ZW - 0.5), (70, 0, ZW - 0.5), (0, 0, ZW - 0.5),
             lambda s, t: 0.5 * max(0.0, 1 - s / 70))
    e.foscor('sostre_fosc', (0, HW - 0.5, ZW - 0.6), (XR, HW - 0.5, ZW - 0.6), (XR, 0, ZW - 0.6), (0, 0, ZW - 0.6),
             lambda s, t: 0.4 * max(0.0, 1 - t / 40))
    # les caixes de fusta al costat de la porta, una mica girades
    for cx, cz, w, d, h, a, y0 in ((34, 178, 34, 30, 28, 0.18, 0), (30, 176, 24, 22, 22, -0.1, 28)):
        e.foscor('ombra_caixes', (cx - 30, 0.6, cz + 26), (cx + 30, 0.6, cz + 26), (cx + 30, 0.6, cz - 30),
                 (cx - 30, 0.6, cz - 30), lambda s, t: 0.5 * max(0.0, 1 - ((s - 30) / 30) ** 2 - ((t - 28) / 28) ** 2) * 1.5)
        e.caixa_girada('caixes', cx, cz, w, d, h, a, WALNUT, 2.4, y0=y0,
                       cares={'dalt': {'ramp': WALNUT, 'lvl': lambda s, t, P: 3.4 - (0.8 if int(t) % 7 == 6 else 0)},
                              'davant': {'ramp': WALNUT, 'lvl': lambda s, t, P: 2.6 - (0.8 if int(t) % 7 == 6 else 0)
                                         + (1.0 if abs(s - t * w / h) < 1.2 else 0)},
                              'dreta': {'ramp': WALNUT, 'lvl': 1.6}})
    # el pilar 7, separat de la paret, i la biga que el lliga amb la del sostre
    px_, pz_ = PILAR
    e.foscor('ombra_pilar', (px_ - 24, 0.6, pz_ + 16), (px_ + 30, 0.6, pz_ + 16), (px_ + 30, 0.6, pz_ - 22),
             (px_ - 24, 0.6, pz_ - 22), lambda s, t: 0.55 * max(0.0, 1 - ((s - 27) / 27) ** 2 - ((t - 19) / 19) ** 2) * 1.5)
    e.caixa('biga_pilar', px_ - 8, px_ + 8, _y(27), _y(17), pz_, ZW, IRON, 1.8,
            cares={'dalt': {'ramp': IRON, 'lvl': 2.6}, 'davant': {'ramp': IRON, 'lvl': lambda s, t, P: 2.2
                                                                    + (2.0 if int(s) % 5 == 2 and t < 3 else 0)}})
    pil = tex['pilar']
    e.sprite('pilar', pil, (343 - PILLAR_BOX[0], FLOOR_Y - PILLAR_BOX[1]), (px_, 0, pz_))
    # els cavallets (i la biga d'acer, si hi és), sota la làmpada
    cx, cz, ang = CAV
    Pc = _rot(cx, cz, ang)
    e.foscor('ombra_cavallets', Pc(-96, 0.6, 26), Pc(96, 0.6, 26), Pc(96, 0.6, -26), Pc(-96, 0.6, -26),
             lambda s, t: 0.55 * max(0.0, 1 - ((s - 96) / 94) ** 4 - ((t - 26) / 24) ** 2) * 1.4)
    _cavallets(e, 'biga_acer' in estat)
    # la làmpada penjada, amb el cable
    e.cable('lampada', [(LAMP[0], HW + 40, LAMP[2]), (LAMP[0], LAMP[1] + 14, LAMP[2])], IRON, 1.4, gruix=1.0)
    e.sprite('lampada', tex['lamp'], (200 - LAMP_BOX[0], 48 - LAMP_BOX[1]), LAMP)
    # ── primer pla: caixes en silueta a baix a l'esquerra, un pilar de ferro a la dreta i una cadena que penja ──
    for cx, cz, w, d, h, a, y0 in ((-6, 30, 64, 52, 50, 0.28, 0), (2, 34, 46, 40, 34, 0.1, 50), (78, -2, 50, 40, 30, -0.22, 0)):
        e.caixa_girada('primer_pla', cx, cz, w, d, h, a, FOSC, 1.6, y0=y0,
                       cares={'dalt': {'ramp': FOSC, 'lvl': lambda s, t, P: 4.0 - (1.2 if int(s) % 9 == 0 else 0)
                                       + (1.6 if t < 1.5 else 0)},
                              'davant': {'ramp': FOSC, 'lvl': lambda s, t, P: 2.2 - (1.2 if int(t) % 9 == 8 else 0)
                                         + (0.8 if t < 2 else 0) + (1.0 if abs(s - t * w / h) < 1.6 else 0)},
                              'dreta': {'ramp': FOSC, 'lvl': lambda s, t, P: 3.0 - (1.2 if int(t) % 9 == 8 else 0)}})
    e.tub('primer_pla', (PIL2[0], 0, PIL2[1]), (PIL2[0], HW + 60, PIL2[1]), 11, FOSC, 2.4, brides=70,
          llum_dir=(-1.0, 0.3))
    cx_, cz_ = CADENA
    for k in range(0, 24):                                              # la cadena del polispast, baula a baula
        yy = HW + 30 - k * 5.2
        a_, b_ = (0.7, 1.6) if k % 2 else (1.6, 0.7)
        e.caixa('primer_pla', cx_ - a_, cx_ + a_, yy - 4.6, yy, cz_ - b_, cz_ + b_, FOSC, 3.6 - (k % 2) * 0.8)
    yk = HW + 30 - 24 * 5.2
    e.cable('primer_pla', [(cx_, yk, cz_), (cx_ + 1, yk - 9, cz_), (cx_ + 7, yk - 11, cz_), (cx_ + 9, yk - 5, cz_)],
            FOSC, 3.8, gruix=2.6)                                       # el ganxo
    return e


# ─── Composició i llum ──────────────────────────────────────────────────────

def _proj(P):
    u, v, _ = CAM.projecta(P)
    return u, v


def _post(img):
    """La llum que no és de cap superfície: el halo de la bombeta, del foc a la porta i del llum de la badia."""
    cv = Canvas(img=img)
    lx, ly = _proj(LAMP)
    cv.glow(lx, ly + 2, 46, (255, 222, 150), 0.42)
    fx, fy = _proj((0, 50, (DOOR[0] + DOOR[1]) / 2))
    cv.glow(fx + 8, fy, 44, (255, 140, 60), 0.3)
    bx, by = _proj(((BX0 + BX1) / 2 + 40, 186, ZS - 30))
    cv.glow(bx, by, 30, (255, 220, 160), 0.3)
    return img


NIT = [(4, 8, 22), (10, 18, 44), (22, 36, 80), (44, 66, 120), (90, 120, 180), (160, 200, 240), (220, 240, 255),
       (255, 255, 255), (255, 255, 255), (255, 255, 255), (255, 255, 255)]   # la nit; i, de dalt, la flama blanca


@functools.lru_cache(maxsize=None)
def _nit():
    """El que es veu per la comporta oberta: el cel de nit, amb estrelles i la lluna, i la ciutat-fàbrica lluny."""
    w, h = 400, 300
    img = Image.new('RGBA', (w, h))
    P = img.load()
    for y in range(h):
        for x in range(w):
            k = y / h
            P[x, y] = (int(8 + 18 * k), int(12 + 26 * k), int(30 + 46 * k), 255)
    rnd = random.Random(4)
    for _ in range(90):
        x, y = rnd.randrange(w), rnd.randrange(int(h * 0.75))
        c = rnd.choice(((230, 236, 255), (170, 182, 230), (255, 240, 200)))
        P[x, y] = c + (255,)
    for y in range(40, 76):                                            # la lluna
        for x in range(250, 290):
            d = math.hypot(x - 270, y - 58)
            if d < 16:
                P[x, y] = (226, 232, 240, 255) if d < 15 else (160, 170, 200, 255)
    for x in range(w):                                                 # la ciutat-fàbrica, lluny, amb llums
        top = int(h * 0.8 - 18 * hr(x // 14, 3) - (30 if hr(x // 40, 4) > 0.8 and x % 40 < 6 else 0))
        for y in range(top, h):
            lit = (x % 5 == 2 and y % 6 == 3 and hr(x, y, 7) > 0.7)
            P[x, y] = (255, 196, 110, 255) if lit else (10, 12, 20, 255)
    return img


def _ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def _surt_moll(k):
    """L'animació de sortir del moll, al moment k → (obertura de la comporta, (alçada de la nau, z de la nau)): la
    comporta puja, la nau s'enlaira del bressol i se'n va per la comporta, cap a la nit, fent-se petita."""
    obre = _ease(k / 0.35)
    if k >= 1:
        return obre, (None, ZS)
    dy = _ease((k - 0.15) / 0.3) * 26
    va = _ease((k - 0.4) / 0.6)
    sx0, sy0, sx1, sy1 = SHUT_BOX
    c0 = ((_w(sx0) + _w(sx1)) / 2, 207 - (sy0 + sy1) / 2 + dy, ZS)
    D = ((BX0 + BX1) / 2, _y(12) * 0.5, ZB)                             # el mig del forat de la comporta
    C = CAM.pos
    lam = 1 + 9 * va ** 1.5
    T = tuple(C[i] + (D[i] - C[i]) * lam for i in range(3))
    b = _ease(va / 0.3)
    P = tuple(c0[i] + (T[i] - c0[i]) * b for i in range(3))
    return obre, (P[1] - (207 - (sy0 + sy1) / 2), P[2], P[0] - (_w(sx0) + _w(sx1)) / 2)


def _render(estat=frozenset(), tex=None):
    cv = _Cv(light=LIGHT)
    e = escena(cv, tex or _textures(), estat)
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)    # la barra de verbs: negre
    return cv.img, e


@functools.lru_cache(maxsize=None)
def _base():
    return _render()


@functools.lru_cache(maxsize=None)
def _base_llum():
    return _post(_base()[0].copy())


def bg(cv):
    cv.img.paste(_base_llum())
    cv.P = cv.img.load()


def _diff(img, base):
    """Només els píxels d'`img` que no són iguals a `base` (la resta, transparent)."""
    d = ImageChops.difference(base.convert('RGB'), img.convert('RGB')).convert('L').point(lambda v: 255 if v else 0)
    out = Image.new('RGBA', img.size, (0, 0, 0, 0))
    out.paste(img, (0, 0), d)
    return out


def _fotograma(capes):
    """El fons amb unes capes damunt, amb la llum, menys el fons amb la llum."""
    img = _base()[0].copy()
    for c in capes:
        img.alpha_composite(c)
    return _diff(_post(img), _base_llum())


def _capa_paret(prop):
    """Un decorat de la paret del fons (dibuixat pla, damunt del pla de sempre), projectat per la paret."""
    def draw(cv):
        flat = Canvas(light=TEX_LIGHT, transparent=True)
        prop(flat)
        _, e = _base()
        cv.img.alpha_composite(_fotograma([e.capa(flat.img, {'paret_fons'})]))
        cv.P = cv.img.load()
    return draw


def _biga_acer(cv):
    img, _ = _render(frozenset({'biga_acer'}))
    cv.img.alpha_composite(_diff(_post(img), _base_llum()))
    cv.P = cv.img.load()


def _sprite_capa(e, sid, img, peu_img, peu, escala_img=1.0):
    """Un fotograma d'un dibuix pla dret (un sprite de l'escena), on aquell sprite és el que es veu."""
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


def _marca(cv):
    _, e = _base()
    capa = _sprite_capa(e, 'pilar', _pilar_img(marca=True), (343 - PILLAR_BOX[0], FLOOR_Y - PILLAR_BOX[1]),
                        (PILAR[0], 0, PILAR[1]))
    cv.img.alpha_composite(_fotograma([capa]))
    cv.P = cv.img.load()


PROPS = {
    'biga_acer': _biga_acer,
    'biga_ferro9': _capa_paret(PL.p_biga_ferro9),
    'serra': _capa_paret(PL.p_serra),
    'llima': _capa_paret(PL.p_llima),
    'marca_pilar': _marca,
}


# ─── Animació ───────────────────────────────────────────────────────────────
# El foc de les calderes es mou darrere la porta, l'escletxa de sota la comporta tremola, i la pols sura a la llum
# de la làmpada i a la llengua de lluna (motes del món, que s'empetiteixen i s'apaguen cap al fons).

N_AMBIENT = 24


def _pols(img, t, n, seed, centre, mida, col, k, llum):
    """Motes de pols dins un volum del món (`centre` ± `mida`), que fan un tram curt al llarg del cicle."""
    rnd = random.Random(seed)
    P = img.load()
    for _ in range(n):
        b = [centre[i] + rnd.uniform(-mida[i], mida[i]) for i in range(3)]
        s0, m, fi = rnd.random(), rnd.choice((1, 2, 3)), rnd.uniform(0, 6.283)
        s = (s0 + t) % 1
        p = (b[0] + 3 * math.sin(2 * math.pi * t * m + fi), b[1] - 10 * s, b[2] + 2 * math.cos(2 * math.pi * t * m + fi))
        u, v, _ = CAM.projecta(p)
        x, y = round(u), round(v)
        a = k * math.sin(math.pi * s) * llum(p)
        if 0 <= x < W and 0 <= y < BOTTOM and a > 0.06:
            o = P[x, y]
            P[x, y] = mix(o, col, min(1.0, a)) + (255,)


def _cono(p):
    """La llum de la làmpada (0..1): un con cap avall."""
    dx, dz, dy = p[0] - LAMP[0], p[2] - LAMP[2], LAMP[1] - p[1]
    if dy < 4:
        return 0.0
    return max(0.0, 1 - math.hypot(dx, dz) / (8 + dy * 0.7)) ** 0.6


def _llengua(p):
    """La llum de la lluna, arran de terra (0..1)."""
    return max(0.0, 1 - p[1] / 60) * max(0.0, 1 - (ZB - p[2]) / 260)


def _ambient_frames():
    _, e = _base()
    out = []
    for i in range(N_AMBIENT):
        t = i / N_AMBIENT
        capa = e.capa(_paret_t(t), {'paret_esq', 'comporta'}) if i else None
        img = _base()[0].copy()
        if capa is not None:
            img.alpha_composite(capa)
        _pols(img, t, 34, 61, (LAMP[0], 80, LAMP[2]), (60, 60, 60), (255, 236, 190), 0.7, _cono)
        _pols(img, t, 30, 62, ((BX0 + BX1) / 2, 26, ZW - 30), (110, 26, 120), (206, 216, 248), 0.8, _llengua)
        out.append(_diff(_post(img), _base_llum()))
    return out


# La llançadora se'n va (la fugida de l'Iri): el decorat `nau_fora` (la badia buida, amb la comporta oberta a la nit),
# amb l'etiqueta `surt`, que una indicació d'escena hi posa; s'acaba al mateix decorat.
SURT = tuple(i / 23 for i in range(24))


def _surt_fotograma(k):
    img, _ = _render(frozenset({f'surt:{k}'}))
    return _diff(_post(img), _base_llum())


def _nau_fora(cv):
    cv.img.alpha_composite(_surt_fotograma(1.0))
    cv.P = cv.img.load()


PROPS['nau_fora'] = _nau_fora

ANIMS = {'ambient': {'frames': _ambient_frames, 'frameDuration': 130},
         'surt': {'frames': lambda: [_surt_fotograma(k) for k in SURT], 'frameDuration': 140, 'loop': False,
                  'prop': 'nau_fora'}}


# ─── Capes del davant ───────────────────────────────────────────────────────

def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


# El primer pla (sempre davant); els cavallets (amb la biga d'acer al damunt), el pilar 7 (amb la marca de l'Iri) i
# les caixes de la porta: qui hi passa per darrere, hi queda darrere.
FRONT = [
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20},
    {'id': 'davant_cavallets', 'mask': _amo({'cavallets'}), 'baseline': _p(CAV[0], CAV[1] - 4)[1], 'zIndex': 20,
     'props': ('biga_acer',)},
    {'id': 'davant_pilar', 'mask': _amo({'pilar'}), 'baseline': _p(*PILAR)[1], 'zIndex': 20, 'props': ('marca_pilar',)},
    {'id': 'davant_caixes', 'mask': _amo({'caixes'}), 'baseline': _p(34, 178 - 12)[1], 'zIndex': 20},
]


# ─── Geometria (coordenades de sala, projectades) ────────────────────────────

def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


# El terra on es camina (al món): del davant de les caixes fins a la paret del fons, i fins a la boca de la badia.
WALK_MON = [(14, 120), (14, 282), (BX0 - 6, 286), (BX0 + 10, 296), (BX1 - 10, 296), (BX1 + 30, 280), (700, 200),
            (700, 0), (60, 0)]
V_PROP = 232                                       # (més avall, el personatge passaria d'1,2: és el primer pla)


def _retalla(poly, x0, y0, x1, y1):
    """El polígon retallat al rectangle (Sutherland-Hodgman)."""
    for inside, cut in ((lambda p: p[0] >= x0, lambda a, b: (x0, a[1] + (b[1] - a[1]) * (x0 - a[0]) / (b[0] - a[0]))),
                        (lambda p: p[0] <= x1, lambda a, b: (x1, a[1] + (b[1] - a[1]) * (x1 - a[0]) / (b[0] - a[0]))),
                        (lambda p: p[1] >= y0, lambda a, b: (a[0] + (b[0] - a[0]) * (y0 - a[1]) / (b[1] - a[1]), y0)),
                        (lambda p: p[1] <= y1, lambda a, b: (a[0] + (b[0] - a[0]) * (y1 - a[1]) / (b[1] - a[1]), y1))):
        out = []
        for a, b in zip(poly, poly[1:] + poly[:1]):
            if inside(a):
                out.append(a)
            if inside(a) != inside(b):
                out.append(cut(a, b))
        poly = out
    return [(round(x), round(y)) for x, y in poly]


_WALK = _retalla([CAM.projecta((x, 0, z))[:2] for x, z in WALK_MON], 2, 0, W - 3, V_PROP)
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)


def _cercle(x, z, rx, rz, n=10):
    return [_p(x + rx * math.cos(2 * math.pi * i / n), z + rz * math.sin(2 * math.pi * i / n)) for i in range(n)]


def _forat_cavallets():
    """Els cavallets i tot el que tenen al darrere fins a la paret: amb la càmera tan picada, qui s'hi posa darrere
    queda amb els peus amagats sota la biga i sembla enfilat al banc (tasca 260). S'hi passa per davant o pel costat."""
    cx, cz, ang = CAV
    P = _rot(cx, cz, ang)
    return [_p(*P(lx, 0, lz)[::2]) for lx, lz in ((-CAV_L / 2 - 20, -10), (CAV_L / 2 + 20, -10), (CAV_L / 2 + 20, 150),
                                                  (-CAV_L / 2 - 16, 150))]


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


def _caixa_mon(x0, x1, y0, y1, z0, z1):
    return _rect_mon(*[(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)])


_SHUT = (_w(SHUT_BOX[0]), _w(SHUT_BOX[2]))
_LAMP_P = _p(LAMP[0], LAMP[2])
_FOC_P = _p(40, (DOOR[0] + DOOR[1]) / 2)
_LLUNA_P = _p((BX0 + BX1) / 2, ZW - 40)


def _things():
    cx, cz, ang = CAV
    P = _rot(cx, cz, ang)
    L, bw, bh = BIGA
    biga = _rect_mon(*[P(lx, y, lz) for lx in (-L / 2, L / 2) for lz in (-bw / 2, bw / 2) for y in (CAV_H, CAV_H + bh + 2)])
    biga = (biga[0], biga[1] - 4, biga[2], biga[3] + 4)
    return {
        # el tauler d'eines sencer, el primer: les eines (capes, zIndex més alt) hi queden al damunt (tasca 132)
        'tauler': {'rect': _caixa_mon(_w(365), _w(443), _y(156), _y(57), ZW, ZW), 'walk': _p(_w(405), 270)},
        'porta_calderes': {'rect': _caixa_mon(0, 2, 0, DOOR[3] + 8, DOOR[0] - 6, DOOR[1] + 6), 'walk': _p(22, 236)},
        'biga_acer': {'rect': biga, 'walk': _p(*P(10, 0, -46)[::2])},
        # (tasca 260) es mira i s'agafa des de davant del banc: darrere seu no s'hi pot estar
        'biga_ferro9': {'rect': _caixa_mon(_w(105), _w(282), _y(116), _y(94), ZW, ZW), 'walk': _p(*P(-30, 0, -40)[::2])},
        # (tasca 132) zones més generoses que el dibuix: la serra amb el mànec, i la llima amb el seu tros de tauler
        'serra': {'rect': _caixa_mon(_w(384), _w(443), _y(96), _y(68), ZW, ZW), 'walk': _p(_w(410), 268)},
        'llima': {'rect': _caixa_mon(_w(417), _w(437), _y(150), _y(97), ZW, ZW), 'walk': _p(_w(426), 270)},
        'trapa': {'rect': _caixa_mon(TRAPA[0] - 2, TRAPA[1] + 2, 0, 1, TRAPA[2] - 2, TRAPA[3] + 2),
                  'walk': _p((TRAPA[0] + TRAPA[1]) / 2, TRAPA[2] - 18)},
        'conducte': {'rect': _caixa_mon(_w(296), _w(332), _y(160), _y(34), ZW, ZW), 'walk': _p(_w(306), 272)},
        'comporta': {'rect': _caixa_mon(BX0, BX1, _y(14), _y(86), ZB, ZB), 'walk': _p((BX0 + BX1) / 2 - 10, 288)},
        'llancadora': {'rect': _caixa_mon(_SHUT[0] + 2, _SHUT[1] - 2, 0, 120, ZS, ZS), 'walk': _p(_SHUT[0] + 40, 288)},
        'pilar': {'rect': _caixa_mon(PILAR[0] - 12, PILAR[0] + 12, 0, 178, PILAR[1], PILAR[1]),
                  'walk': _p(PILAR[0] - 30, PILAR[1] - 24)},
    }


GEOMETRIA = {
    'things': _things(),
    # Sense porta (de la cambra, pel conducte), l'Iri surt al peu del conducte: el punt d'abans, al fons a l'esquerra,
    # queia darrere els cavallets i semblava dreta damunt del banc (tasca 176).
    'spawns': {'iri': _p(_w(306), 272)},
    'walkable': _WALK,
    'forats': [_forat_cavallets(), _cercle(PILAR[0], PILAR[1], 18, 14)],
    'floorSquash': 0.4,                            # (la càmera, picada: el terra es veu aixafat)
    # L'ombra de contacte: la llum dominant és la làmpada penjada (el punt del terra just a sota).
    'characterShadow': {'enabled': True, 'color': '#120a08', 'alpha': 0.42, 'squash': 0.4, 'core': 0.6,
                        'light': {'x': _LAMP_P[0], 'y': _LAMP_P[1], 'stretch': 0.7, 'reach': 170}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    # la llum de la sala sobre els personatges, en temps d'execució
    'characterLights': {
        'ambient': '#7a6a66',                                                   # moll fosc, de nit
        'lights': [
            {'x': _LAMP_P[0], 'y': _LAMP_P[1] - 60, 'radius': 220, 'color': '#ffd890', 'intensity': 0.9},   # la làmpada
            {'x': _FOC_P[0], 'y': _FOC_P[1] - 40, 'radius': 200, 'color': '#ff8a3c', 'intensity': 1.0},     # el foc
            {'x': _LLUNA_P[0], 'y': _LLUNA_P[1], 'radius': 180, 'color': '#96aae6', 'intensity': 0.7},      # la lluna
        ],
    },
}

# Coses per mirar (tasca 259): rectangles de pantalla i el punt on s'hi va.
GEOMETRIA['things'].update({
    'caixes': {'rect': (0, 112, 110, 245), 'walk': (100, 212)},
})
