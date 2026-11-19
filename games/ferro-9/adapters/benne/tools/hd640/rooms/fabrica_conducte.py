"""
El conducte de servei de la fàbrica (Iri): un revolt. EN 3D (hd640/tres_d.py), a 1×.

Sempre el mateix revolt, ara una cambra de planxa reblonada on es creuen els passadissos, vista des de la boca per
on s'hi entra (des de la reixa de la cambra de ressonància), amb la càmera alta i una mica girada cap a l'esquerra:
  - les dues parets fugen cap al fons, amb la canonada de coure (en 3D, amb abraçadores) que les recorre i es talla
    a cada passadís;
  - a la paret de l'esquerra i a la de la dreta, els **passadissos** que giren, en escorç, que s'enfonsen a les
    fosques; al fons, l'**arc** del passadís de dret, amb una llumeta molt lluny;
  - el terra de reixeta, amb les barres que s'empetiteixen cap al fons, i el sostre de planxa amb la **làmpada de
    gàbia** al mig (es gronxa amb el corrent d'aire i parpelleja);
  - primer pla: el marc de la boca del conducte (els muntants i la llinda reblonats, foscos, tallats per les vores) i
    la llum càlida de la reixa de la cambra que entra per darrere, a baix a l'esquerra (el camí de tornada).

A cada revolt hi canvia un detall (un prop): el cartell, el guant, l'aixeta que degota, la tassa o el formulari
27-B; els dibuixos plans de sempre (fabrica_conducte_pla_comu.py), posats al seu lloc del món.

El món: x a la dreta (0 = la paret de l'esquerra), y amunt (0 = el terra), z cap al fons (460 = la paret del fons);
1 unitat = 1 píxel de sala a la distància on un personatge fa ≈110 px (escala 1).
"""
import functools
import math
import random

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from PIL import Image, ImageChops

from hd.pix import Canvas, Light, W, H, hr, mix, B4, IRON, COPPER, WARN, CYAN, WALNUT
from hd.rooms.exterior import fbm
from hd640.rooms import fabrica_conducte_pla_comu as PL
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
CW, CD, HW = 480, 330, 190                         # la cambra: ample, la paret del fons, alçada
ZN = -40                                           # la paret del davant (la boca per on s'entra)
OBERT = (110, 200, 128)                            # el passadís de l'esquerra: z0, z1, alçada de la llinda
OBERT_D = (214, 296, 128)                          # el de la dreta
ARC = (204, 276, 104, 136)                         # el passadís de dret: x0, x1, alçada dels muntants, del cim de l'arc
TUB_Y = 132                                        # la canonada de coure, a les parets
LAMP = (250, 170, 140)                             # la bombeta de la làmpada de gàbia
LLUNY = 1100                                       # el fons del passadís de dret

CAM = Camera(pos=(330, 165, -300), yaw=-0.32, pitch=0.12, f=420, centre=(320, 105))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)  # (la llum és la del món: la de l'Escena)

LLUMS = [Llum(LAMP, 360, 2.6, power=1.4),                                   # la làmpada de gàbia
         Llum((40, 30, ZN - 30), 280, 1.6, power=1.6),                          # la reixa de la cambra, per darrere
         Llum(((ARC[0] + ARC[1]) / 2, 50, LLUNY - 40), 200, 1.2, power=2.0)]  # la llumeta del fons


class _Cv(Canvas):
    """El llenç de l'escena (tres_d vol saber quants píxels reals fa un de sala)."""
    S = 1


# ─── Les superfícies ────────────────────────────────────────────────────────

FOSC = [(4, 4, 7), (8, 8, 12), (13, 13, 18), (19, 19, 25), (27, 27, 34), (38, 37, 45), (52, 50, 58)]
WARM = (255, 170, 96)


def _planxa(lvl0, seed=7):
    """Planxa reblonada en coordenades del món (s, t des del cantó de dalt): plaques de 44×36 amb les juntes i els
    reblons, més fosca a dalt."""
    def L(s, t, P):
        v = lvl0 + (hr(int(s // 44), int(t // 36), seed) - 0.5) * 0.5 + (fbm(s / 30, t / 20, seed) - 0.5) * 0.4
        js, jt = s % 44, t % 36
        if js < 1.2 or jt < 1.2:
            return v - 1.3
        if js < 2.2 or jt < 2.2:
            v += 0.4
        if (js < 5 or js > 40) and int(t) % 7 == 3 or (jt < 5 or jt > 32) and int(s) % 7 == 3:
            return v + 1.4                                              # els reblons
        if hr(int(s // 6), int(t // 9), seed + 9) > 0.96:
            v -= 0.6                                                    # taques de rovell
        return v - 0.5 * max(0.0, 1 - t / 60)
    return L


def _reixeta(s, t, P):
    """El terra de reixeta, en coordenades del món: travessers al llarg de z cada 6, barres de través cada 24, i el
    buit fosc entre mig (amb el que hi ha a sota)."""
    x, z = P[0], P[2]
    if z % 24 < 2.2:
        return 2.6 + (0.6 if z % 24 < 1 else 0)                         # les barres de través
    if x % 6 < 1.6:
        return 2.2 + (0.5 if x % 6 < 0.6 else 0) + (hr(int(x // 6), int(z // 24), 13) - 0.5) * 0.4
    return -0.6 + (fbm(x / 40, z / 40, 3) - 0.5) * 0.8                    # el buit


def _arc(s, t):
    """La forma de l'arc del passadís de dret (s, t des del cantó de dalt a l'esquerra)."""
    x0, x1, hm, ht = ARC
    rx = (x1 - x0) / 2
    y = ht - t
    if y <= hm:
        return True
    return ((s - rx) / rx) ** 2 + ((y - hm) / (ht - hm)) ** 2 <= 1


def _passadis(e, costat):
    """Un passadís lateral que gira: el terra de reixeta que s'hi endinsa, la paret de la girada (que rep una mica de
    llum a la vora de prop) i el sostre, que es perden a les fosques."""
    z0, z1, h = OBERT if costat < 0 else OBERT_D
    x = 0 if costat < 0 else CW
    xf = x + costat * 160                                               # fins on es veu
    sid = 'passadis_esq' if costat < 0 else 'passadis_dre'
    llum = lambda s, t, P: 2.8 * max(0.0, 1 - abs(P[0] - x) / 150) ** 1.6 - 0.6  # noqa: E731
    a, b = (xf, x) if costat < 0 else (x, xf)
    e.quad(sid, (a, h, z1), (b, h, z1), (b, 0, z1), (a, 0, z1), ramp=IRON,
           lvl=lambda s, t, P: _planxa(0.4, 11)(s, t, P) * 0.6 + llum(s, t, P))         # la paret de la girada
    e.quad(sid, (a, 0, z1), (b, 0, z1), (b, 0, z0), (a, 0, z0), ramp=IRON,
           lvl=lambda s, t, P: _reixeta(s, t, P) * 0.6 + llum(s, t, P) - 0.4)
    e.quad(sid, (a, h, z0), (b, h, z0), (b, h, z1), (a, h, z1), ramp=IRON, lvl=lambda s, t, P: llum(s, t, P) - 1.2)
    e.foscor(sid, (a, 0.5, z1), (b, 0.5, z1), (b, 0.5, z0), (a, 0.5, z0),
             lambda s, t: 0.5 * max(0.0, 1 - t / 14))
    # el marc de planxa: els brancals i la llinda, amb la vora clara i els reblons
    for zz in (z0, z1):
        e.caixa(sid, x - 4, x + 4, 0, h + 7, zz - 4, zz + 4, IRON, 3.0,
                cares={'dalt': {'ramp': IRON, 'lvl': 3.6},
                       'davant': {'ramp': IRON, 'lvl': lambda s, t, P: 3.6 + (1.6 if int(t) % 11 == 3 else 0)},
                       'esquerra' if costat > 0 else 'dreta': {'ramp': IRON, 'lvl': lambda s, t, P: 2.6
                                                              + (1.6 if int(t) % 11 == 3 else 0)}})
    e.caixa(sid, x - 4, x + 4, h, h + 7, z0, z1, IRON, 2.6,
            cares={'sota': {'ramp': IRON, 'lvl': 1.6}, 'esquerra' if costat > 0 else 'dreta': {'ramp': IRON, 'lvl': 3.0}})


@functools.lru_cache(maxsize=None)
def _pla(nom, f=None):
    """El dibuix pla d'un detall (sobre transparent, a la mida de la sala de sempre)."""
    cv = Canvas(light=PL.LIGHT, transparent=True)
    if nom == 'aixeta':
        PL._aixeta_fixa(cv)
    else:
        getattr(PL, nom)(cv)
    return cv.img


# On va cada detall: el retall del dibuix pla i el rectangle del món on es posa (P0 a dalt a l'esquerra, P1 a dalt a
# la dreta, P2 a baix a la dreta, P3 a baix a l'esquerra, mirant-lo de cara).
CARTELL = (238, 92, 280, 122)
FORMULARI = (361, 88, 403, 137)
AIXETA = (370, 100, 396, 148)                      # el tub, el volant i el broc (el bassal és al terra)
_ZP = CD - 0.6                                     # (just davant la paret del fons)


def _paret_rect(crop, x0, y1, k=1.7):
    """Un retall del pla, posat a la paret del fons a partir del cantó de dalt a l'esquerra (x0, y1), a `k` unitats per
    píxel."""
    w, h = (crop[2] - crop[0]) * k, (crop[3] - crop[1]) * k
    return (x0, y1, _ZP), (x0 + w, y1, _ZP), (x0 + w, y1 - h, _ZP), (x0, y1 - h, _ZP)


CARTELL_W = _paret_rect(CARTELL, 112, 124)
FORMULARI_W = _paret_rect(FORMULARI, 300, 128)
AIXETA_W = _paret_rect(AIXETA, 312, HW - 4, k=2.2)
_spx = AIXETA_W[0][0] + (PL.DRIP_X - AIXETA[0]) * 2.2
GOTA = (_spx, AIXETA_W[0][1] - (PL.DRIP_Y0 - AIXETA[1]) * 2.2, CD - 9)   # on surt la gota (el broc, una mica enfora)
BASSAL = (_spx, CD - 16, 24, 10)                    # el bassal: x, z del centre, radis
GUANT = (318, 178)                                  # el guant, a terra (x, z)
TASSA = (176, 196)
RISER = (26, 56)                                    # la columna de la vàlvula (x, z)
CAIXES = ((432, 286, 46, 34, 30, -0.25, 0), (440, 290, 30, 26, 22, 0.1, 30), (392, 304, 30, 24, 18, 0.4, 0))
TUBS_SOSTRE = ((120, 176, 7), (142, 178, 5))     # x, y, radi: les canonades del sostre (al llarg de z)


def escena(cv, estat=frozenset(), lampada=True):
    """Tota la sala, de lluny a prop. `estat`: el detall del revolt que hi és. → l'Escena."""
    e = Escena(cv, CAM, LLUMS, ambient=-0.8)
    x0, x1, hm, ht = ARC
    cx = (x0 + x1) / 2
    # ── el passadís de dret, darrere l'arc: s'allarga a les fosques fins a una llumeta ──
    fons = lambda s, t, P: 2.4 * max(0.0, 1 - (P[2] - CD) / 380) ** 2 - 0.6 + 1.6 * max(0.0, 1 - (LLUNY - P[2]) / 120) ** 2  # noqa: E731
    e.quad('recte', (x0, ht, LLUNY), (x1, ht, LLUNY), (x1, 0, LLUNY), (x0, 0, LLUNY), ramp=IRON, lvl=lambda s, t, P: -0.2)
    e.quad('recte', (x0, ht, CD), (x0, ht, LLUNY), (x0, 0, LLUNY), (x0, 0, CD), ramp=IRON, lvl=fons)
    e.quad('recte', (x1, ht, LLUNY), (x1, ht, CD), (x1, 0, CD), (x1, 0, LLUNY), ramp=IRON, lvl=fons)
    e.quad('recte', (x0, 0, LLUNY), (x1, 0, LLUNY), (x1, 0, CD), (x0, 0, CD), ramp=IRON,
           lvl=lambda s, t, P: _reixeta(s, t, P) * 0.4 + fons(s, t, P) - 0.4)
    e.quad('recte', (x0, ht, CD), (x1, ht, CD), (x1, ht, LLUNY), (x0, ht, LLUNY), ramp=IRON, lvl=fons, dues_cares=True)
    # ── la paret del fons, amb l'arc ──
    e.quad('paret_fons', (0, HW, CD), (CW, HW, CD), (CW, 0, CD), (0, 0, CD), ramp=IRON, lvl=_planxa(2.0, 5),
           forma=lambda s, t: not (x0 - 0.5 <= s <= x1 + 0.5 and _arc(s - x0, t - (HW - ht))))
    # el marc de l'arc
    for k in range(0, 41):
        a = math.pi * k / 40
        rx, ry = (x1 - x0) / 2 + 3, ht - hm + 3
        P = (cx + math.cos(a) * rx, hm + math.sin(a) * ry, CD - 1)
        e.caixa('marc_arc', P[0] - 2.6, P[0] + 2.6, P[1] - 2.6, P[1] + 2.6, CD - 4, CD - 0.5, IRON, 3.4 + math.sin(a) * 0.6)
    for xx in (x0 - 3, x1 + 3):
        e.caixa('marc_arc', xx - 2.6, xx + 2.6, 0, hm, CD - 4, CD - 0.5, IRON, 3.6 if xx < cx else 2.4,
                cares={'davant': {'ramp': IRON, 'lvl': lambda s, t, P: (3.4 if P[0] < cx else 2.4)
                                  + (1.6 if int(t) % 11 == 4 else 0)}})
    # ── els passadissos de l'esquerra i la dreta ──
    _passadis(e, -1)
    _passadis(e, 1)
    # ── les parets (amb el forat del passadís), el sostre i el terra ──
    z0, z1, h = OBERT
    zd0, zd1, hd = OBERT_D
    e.quad('paret_esq', (0, HW, ZN), (0, HW, CD), (0, 0, CD), (0, 0, ZN), ramp=IRON, lvl=_planxa(2.2, 3),
           forma=lambda s, t: not (z0 <= ZN + s <= z1 and t > HW - h))
    e.quad('paret_dre', (CW, HW, CD), (CW, HW, ZN), (CW, 0, ZN), (CW, 0, CD), ramp=IRON, lvl=_planxa(2.0, 4),
           forma=lambda s, t: not (zd0 <= CD - s <= zd1 and t > HW - hd))
    e.quad('sostre', (0, HW, ZN), (CW, HW, ZN), (CW, HW, CD), (0, HW, CD), ramp=IRON, dues_cares=True,
           lvl=lambda s, t, P: 1.4 + (hr(int(s // 53), int(t // 40), 3) - 0.5) * 0.3 - (0.9 if s % 53 < 1.4 or t % 40 < 1.2 else 0))
    e.quad('terra', (0, 0, CD), (CW, 0, CD), (CW, 0, ZN), (0, 0, ZN), ramp=IRON, lvl=_reixeta)
    # la canonada de coure a les dues parets, tallada pels passadissos, amb les abraçadores; s'acaba a la paret del fons
    for xx, ld, (za0, za1) in ((5.5, (0.6, 1.0), (z0, z1)), (CW - 5.5, (-0.6, 1.0), (zd0, zd1))):
        for za, zb in ((ZN, za0 - 6), (za1 + 6, CD)):
            e.tub('canonada', (xx, TUB_Y, zb), (xx, TUB_Y, za), 5, COPPER, 2.6, brides=58, llum_dir=ld)
    # les canonades del sostre, de ferro, i les abraçadores que les pengen
    for tx, ty, tr in TUBS_SOSTRE:
        e.tub('canonada', (tx, ty, CD), (tx, ty, ZN), tr, IRON, 2.8, brides=80, llum_dir=(-0.3, 1.0))
    # la llum: el bassal de la làmpada, la de la reixa de la cambra (per darrere, a l'esquerra) i la del fons
    e.claror((LAMP[0] - 190, 0.5, LAMP[2] + 190), (LAMP[0] + 190, 0.5, LAMP[2] + 190), (LAMP[0] + 190, 0.5, LAMP[2] - 190),
             (LAMP[0] - 190, 0.5, LAMP[2] - 190), (255, 214, 140),
             lambda s, t: 0.26 * max(0.0, 1 - math.hypot(s - 190, t - 190) / 190) ** 1.3)
    e.claror((0, 0.5, 160), (260, 0.5, 160), (260, 0.5, ZN), (0, 0.5, ZN), WARM,
             lambda s, t: 0.5 * max(0.0, 1 - math.hypot(s / 240, (t - (160 - ZN)) / 200)) ** 1.2)
    e.claror((0.5, HW, ZN), (0.5, HW, 140), (0.5, 0, 140), (0.5, 0, ZN), WARM,
             lambda s, t: 0.34 * max(0.0, 1 - math.hypot(s / 200, (HW - t) / 140)) ** 1.3)
    # la foscor dels racons, del sostre i del fons
    e.foscor('racons', (0, 0.5, CD), (CW, 0.5, CD), (CW, 0.5, ZN), (0, 0.5, ZN),
             lambda s, t: max(0.6 * max(0.0, 1 - t / 30), 0.4 * max(0.0, 1 - s / 16), 0.4 * max(0.0, 1 - (CW - s) / 16)))
    for P0, P1, P2, P3 in (((0.5, HW, ZN), (0.5, HW, CD), (0.5, 0, CD), (0.5, 0, ZN)),
                           ((CW - 0.5, HW, CD), (CW - 0.5, HW, ZN), (CW - 0.5, 0, ZN), (CW - 0.5, 0, CD)),
                           ((0, HW, CD - 0.5), (CW, HW, CD - 0.5), (CW, 0, CD - 0.5), (0, 0, CD - 0.5))):
        e.foscor('racons', P0, P1, P2, P3, lambda s, t: 0.35 * max(0.0, 1 - t / 50) + 0.3 * max(0.0, 1 - (HW - t) / 20))
    # la claror de l'arc del fons, que llisca per les parets dels costats i pel terra (més com més a prop de l'arc)
    for P0, P1, P2, P3 in (((0.6, HW, CD - 150), (0.6, HW, CD), (0.6, 0, CD), (0.6, 0, CD - 150)),
                           ((CW - 0.6, HW, CD), (CW - 0.6, HW, CD - 150), (CW - 0.6, 0, CD - 150), (CW - 0.6, 0, CD))):
        izq = P0[0] < 1
        e.claror(P0, P1, P2, P3, (255, 196, 128),
                 lambda s, t, izq=izq: 0.26 * (s / 150 if izq else 1 - s / 150) ** 2 * max(0.0, 1 - abs(t - 120) / 90))
    e.claror((x0 - 90, 0.6, CD), (x1 + 90, 0.6, CD), (x1 + 90, 0.6, CD - 120), (x0 - 90, 0.6, CD - 120), (255, 196, 128),
             lambda s, t: 0.22 * max(0.0, 1 - t / 120) ** 1.5 * max(0.0, 1 - abs(s - (x1 - x0 + 180) / 2) / 130))
    # una costella de la galeria, entre els dos passadissos: els muntants arran de les parets i la biga del sostre
    costella(e, 'costella', 205, 2.4)
    # les caixes de recanvis, apilades al racó del fons a la dreta (la paret es trenca)
    for bx, bz, w, d, hh, ang, y0 in CAIXES:
        if y0 == 0:
            e.foscor('caixes', (bx - 34, 0.6, bz + 26), (bx + 34, 0.6, bz + 26), (bx + 34, 0.6, bz - 30), (bx - 34, 0.6, bz - 30),
                     lambda s, t: 0.6 * max(0.0, 1 - ((s - 34) / 34) ** 2 - ((t - 28) / 28) ** 2) * 1.5)
        e.caixa_girada('caixes', bx, bz, w, d, hh, ang, IRON, 2.0, y0=y0,
                       cares={'dalt': {'ramp': WALNUT, 'lvl': lambda s, t, P: 4.4 - (1.2 if int(s) % 10 == 0 else 0)},
                              'davant': {'ramp': WALNUT, 'lvl': lambda s, t, P: 3.6 + (1.0 if t < 2 else 0)
                                         - (1.2 if int(t) % 8 == 7 else 0) + (1.0 if abs(s - t * w / hh) < 1.5 else 0)},
                              'esquerra': {'ramp': WALNUT, 'lvl': 4.0}, 'dreta': {'ramp': WALNUT, 'lvl': 2.4}})
    # l'escala de gat a la paret del fons, a l'esquerra, que puja a una trapa del sostre
    for xx in (34, 62):
        e.caixa('escala', xx - 2, xx + 2, 0, HW, CD - 12, CD - 8, IRON, 3.0, cares={'davant': {'ramp': IRON, 'lvl': 3.4}})
    for yy in range(16, HW, 18):
        e.caixa('escala', 34, 62, yy - 1.5, yy + 1.5, CD - 12, CD - 9, IRON, 3.6,
                cares={'dalt': {'ramp': IRON, 'lvl': 4.4}, 'davant': {'ramp': IRON, 'lvl': 2.8}})
    for xx in (34, 62):
        e.caixa('escala', xx - 2, xx + 2, 6, 10, CD - 8, CD - 0.5, IRON, 2.6)
        e.caixa('escala', xx - 2, xx + 2, HW - 30, HW - 26, CD - 8, CD - 0.5, IRON, 2.6)
    # ── el detall del revolt ──
    if 'cartell' in estat:
        e.quad('cartell', *CARTELL_W, tex=(_pla('cartell'), CARTELL))
    if 'formulari' in estat:
        e.quad('formulari', *FORMULARI_W, tex=(_pla('formulari'), FORMULARI))
    if 'aixeta' in estat:
        bx, bz, rx, rz = BASSAL
        e.quad('aixeta', (bx - rx, 0.6, bz + rz), (bx + rx, 0.6, bz + rz), (bx + rx, 0.6, bz - rz), (bx - rx, 0.6, bz - rz),
               ramp=CYAN, lvl=lambda s, t, P: 1.0 - (t - rz) / rz * 0.4 + (1.2 if abs(t - rz * 0.7) < 1 and abs(s - rx * 0.8) < 6 else 0),
               forma=lambda s, t: ((s - rx) / rx) ** 2 + ((t - rz) / rz) ** 2 <= 1)
        e.quad('aixeta', *AIXETA_W, tex=(_pla('aixeta'), AIXETA))
    if 'guant' in estat:
        gx, gz = GUANT
        e.foscor('guant', (gx - 16, 0.7, gz + 8), (gx + 16, 0.7, gz + 8), (gx + 16, 0.7, gz - 8), (gx - 16, 0.7, gz - 8),
                 lambda s, t: 0.6 * max(0.0, 1 - ((s - 16) / 16) ** 2 - ((t - 8) / 8) ** 2) * 1.5)
        e.sprite('guant', _pla('guant').crop((378, 227, 410, 243)), (16, 15), (gx, 0, gz), escala_img=1.15)
    if 'tassa' in estat:
        tx, tz = TASSA
        e.foscor('tassa', (tx - 12, 0.7, tz + 6), (tx + 12, 0.7, tz + 6), (tx + 12, 0.7, tz - 6), (tx - 12, 0.7, tz - 6),
                 lambda s, t: 0.6 * max(0.0, 1 - ((s - 12) / 12) ** 2 - ((t - 6) / 6) ** 2) * 1.5)
        e.sprite('tassa', _pla('tassa').crop((218, 222, 245, 241)), (14, 18), (tx, 0, tz), escala_img=1.25)
    # ── la columna de la vàlvula: un tub gruixut que baixa del sostre i es fica a la reixeta, amb el volant ──
    rx_, rz_ = RISER
    e.foscor('ombra_columna', (rx_ - 20, 0.6, rz_ + 14), (rx_ + 26, 0.6, rz_ + 14), (rx_ + 26, 0.6, rz_ - 18),
             (rx_ - 20, 0.6, rz_ - 18), lambda s, t: 0.6 * max(0.0, 1 - ((s - 23) / 23) ** 2 - ((t - 16) / 16) ** 2) * 1.5)
    e.tub('columna', (rx_, HW, rz_), (rx_, 0, rz_), 9, IRON, 2.8, brides=44, llum_dir=(-0.8, 0.2))
    e.caixa('columna', rx_ - 9, rx_ + 9, 82, 100, rz_ - 9, rz_ + 9, IRON, 2.6,
            cares={'davant': {'ramp': IRON, 'lvl': 3.0}, 'dalt': {'ramp': IRON, 'lvl': 3.8}})
    wheel = [(rx_ + math.cos(a) * 13, 91 + math.sin(a) * 13, rz_ - 14) for a in [2 * math.pi * k / 16 for k in range(17)]]
    e.cable('columna', wheel, PL.RED, 3.4, gruix=2.4)
    for a in (0.4, 0.4 + math.pi / 2):
        e.cable('columna', [(rx_ + math.cos(a) * 13, 91 + math.sin(a) * 13, rz_ - 14),
                            (rx_ - math.cos(a) * 13, 91 - math.sin(a) * 13, rz_ - 14)], PL.RED, 3.0, gruix=1.6)
    e.cable('columna', [(rx_, 91, rz_ - 9), (rx_, 91, rz_ - 14)], IRON, 3.0, gruix=2.4)
    # ── la làmpada de gàbia, penjada del sostre ──
    if lampada:
        _lampada(e)
    # ── primer pla: la paret de la boca del conducte, reblonada i fosca, tallada per les vores ──
    def boca(s, t, P):
        v = 1.4 + (hr(int(s // 44), int(t // 36), 21) - 0.5) * 0.4
        if s % 44 < 1.5 or t % 36 < 1.5:
            return v - 1.0
        if (s % 44 < 5 or s % 44 > 39) and int(t) % 8 == 4:
            return v + 1.8
        return v
    zf = ZN
    for xa, xb in ((-60, 46), (CW - 70, CW + 80)):
        e.caixa('primer_pla', xa, xb, 0, HW + 40, zf - 10, zf, FOSC, 2.0,
                cares={'davant': {'ramp': FOSC, 'lvl': boca},
                       'dreta': {'ramp': FOSC, 'lvl': lambda s, t, P: 3.6 - (1.2 if int(t) % 9 == 0 else 0)},
                       'esquerra': {'ramp': FOSC, 'lvl': lambda s, t, P: 3.2 - (1.2 if int(t) % 9 == 0 else 0)}})
    # una costella molt a prop (només se'n veuen el muntant de l'esquerra i la biga del sostre), en silueta
    costella(e, 'primer_pla', 18, 1.6)
    for k, xx in enumerate((CW - 96, CW - 80)):
        e.cable('primer_pla', [(xx, HW - 8, zf - 14), (xx - 10 - k * 8, HW - 50 - k * 14, zf - 16), (xx + 4, HW - 84 + k * 20, zf - 18)],
                FOSC, 2.4, gruix=2.2)
    e.caixa('primer_pla', -60, CW + 80, HW - 8, HW + 40, zf - 10, zf, FOSC, 1.6,
            cares={'davant': {'ramp': FOSC, 'lvl': boca}, 'sota': {'ramp': FOSC, 'lvl': 3.6}})
    e.silueta({'primer_pla'}, 0.25, col=(3, 3, 6))
    return e


def costella(e, sid, z, lvl):
    """Una costella de la galeria a la profunditat `z`: dos muntants en I arran de les parets, la biga del sostre i
    les cartel·les dels cantons, de ferro fosc, amb els reblons."""
    w, d = 14, 10
    vora = {'ramp': FOSC, 'lvl': lambda s, t, P: lvl + (1.6 if s < 1.4 else 0) + (1.0 if int(t) % 14 == 7 else 0)}
    for xa, xb in ((0, w), (CW - w, CW)):
        e.caixa(sid, xa, xb, 0, HW, z, z + d, FOSC, lvl, cares={'davant': vora, 'esquerra': vora, 'dreta': vora})
    e.caixa(sid, 0, CW, HW - 12, HW, z, z + d, FOSC, lvl, cares={'davant': vora, 'sota': {'ramp': FOSC, 'lvl': lvl + 0.8}})
    for xa, sg in ((w, 1), (CW - w, -1)):                          # les cartel·les (triangles als cantons de dalt)
        for k in range(8):
            e.caixa(sid, min(xa, xa + sg * (24 - k * 3)), max(xa, xa + sg * (24 - k * 3)), HW - 12 - (k + 1) * 3,
                    HW - 12 - k * 3, z + 2, z + d - 2, FOSC, lvl)


def _lampada(e, swing=0.0):
    """La làmpada de gàbia: el cable des del sostre i el dibuix pla de sempre (la gàbia i la bombeta)."""
    lx, ly, lz = LAMP
    e.cable('lampada', [(lx, HW, lz), (lx + swing, ly + 10, lz)], IRON, 1.4, gruix=1.0)
    e.sprite('lampada', _lamp_img(), (12, 13), (lx + swing, ly - 4, lz), escala_img=1.4)


@functools.lru_cache(maxsize=None)
def _lamp_img(power=1.0):
    cv = Canvas(light=PL.LIGHT, transparent=True)
    PL._lamp(cv, 0.0, power)
    cx, cy = PL.LAMP
    return cv.img.crop((cx - 12, cy - 13, cx + 13, cy + 12))


# ─── Composició i llum ──────────────────────────────────────────────────────

def _proj(P):
    u, v, _ = CAM.projecta(P)
    return u, v


def _post(img, power=1.0, swing=0.0):
    """La llum que no és de cap superfície: el halo de la bombeta, la llumeta del fons i la claror de la reixa de la
    cambra, que entra per darrere a baix a l'esquerra."""
    cv = Canvas(img=img)
    lx, ly = _proj((LAMP[0] + swing, LAMP[1] - 2, LAMP[2]))
    cv.glow(lx, ly, 46, (255, 210, 130), 0.5 * power)
    fx, fy = _proj(((ARC[0] + ARC[1]) / 2, 40, LLUNY - 10))
    cv.glow(fx, fy, 9, (150, 110, 70), 0.4)
    P = img.load()
    for y in range(150, BOTTOM + 1):
        for x in range(0, 200):
            a = max(0.0, 1 - (x / 190) ** 2 - ((y - 262) / 80) ** 2) * 0.55
            if a > 0 and a > B4[y & 3][x & 3] * 0.5:
                o = P[x, y]
                P[x, y] = (min(255, int(o[0] + 70 * a)), min(255, int(o[1] + 50 * a)), min(255, int(o[2] + 30 * a)), 255)
    return img


def _render(estat=frozenset(), lampada=True):
    cv = _Cv(light=LIGHT)
    e = escena(cv, estat, lampada)
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


@functools.lru_cache(maxsize=None)
def _amb(nom):
    """La sala amb un detall del revolt, amb la llum."""
    return _post(_render(frozenset({nom}))[0])


def _decorat(nom):
    def draw(cv):
        cv.img.alpha_composite(_diff(_amb(nom), _base_llum()))
        cv.P = cv.img.load()
    return draw


PROPS = {nom: _decorat(nom) for nom in ('cartell', 'guant', 'aixeta', 'tassa', 'formulari')}


# ─── Animacions ─────────────────────────────────────────────────────────────
# De fons: la làmpada es gronxa amb el corrent d'aire del conducte i parpelleja (sobretot una caiguda de tensió a
# mig cicle), la llum que fa a les parets la segueix, la pols sura dins el con de llum i la llumeta del fons del
# passadís de dret batega. La gota de l'aixeta és l'animació del prop `aixeta` (3r revolt): el detall sencer, amb la
# gota que s'infla al broc, cau i fa onades al bassal.

N_AMBIENT = 32


@functools.lru_cache(maxsize=None)
def _sense_lampada():
    return _render(lampada=False)[0]


def _ambient_frames():
    rnd = [(hr(i, 1, 41), hr(i, 2, 41), hr(i, 3, 41)) for i in range(18)]   # la pols: x, z, fase
    base = _base_llum()
    out = []
    for i in range(N_AMBIENT):
        t = i / N_AMBIENT
        swing = 3.0 * math.sin(2 * math.pi * t)
        power = PL._flicker(t)
        img = _sense_lampada().copy()
        cv = _Cv(img=img, light=LIGHT)
        e = Escena(cv, CAM, LLUMS)
        _lampada(e, swing)
        # la llum a les parets i al sostre segueix la làmpada
        lx, ly = _proj((LAMP[0] + swing, LAMP[1], LAMP[2]))
        k = power - 1.0
        P = img.load()
        if abs(k) > 0.01 or abs(swing) > 0.4:
            for y in range(0, BOTTOM):
                for x in range(max(0, round(lx) - 170), min(W, round(lx) + 171)):
                    d = math.hypot(x - lx, (y - ly) * 1.2) / 170
                    a = max(0.0, 1 - d) ** 2 * (k + swing * (x - lx) / 600)
                    if a < -0.02 and -a > B4[y & 3][x & 3] * 0.6:
                        o = P[x, y]
                        P[x, y] = tuple(int(c * 0.8) for c in o[:3]) + (255,)
                    elif a > 0.02 and a > B4[y & 3][x & 3] * 0.6:
                        o = P[x, y]
                        P[x, y] = tuple(min(255, int(c * 1.12) + 2) for c in o[:3]) + (255,)
        # la pols que sura dins el con de llum (motes del món)
        for px, pz, ph in rnd:
            yy = 20 + ((ph + t * (0.25 + ph * 0.2)) % 1) * 120
            xx = LAMP[0] - 60 + px * 120 + 5 * math.sin(2 * math.pi * (t + ph))
            zz = LAMP[2] - 50 + pz * 100
            if math.hypot(xx - LAMP[0] - swing, zz - LAMP[2]) < (LAMP[1] - yy) * 0.6 + 6:
                u, v = _proj((xx, yy, zz))
                if 0 <= u < W and 0 <= v < BOTTOM:
                    o = P[int(u), int(v)]
                    P[int(u), int(v)] = mix(o, (255, 220, 140), 0.55 * power) + (255,)
        img = _post(img, power, swing)
        # la llumeta del fons del passadís de dret
        fx, fy = _proj(((ARC[0] + ARC[1]) / 2, 40, LLUNY - 10))
        Canvas(img=img).glow(fx, fy, 9, (150, 110, 70), 0.2 * (1 + math.sin(2 * math.pi * t * 2)))
        out.append(_diff(img, base))
    return out


def _gota_frames(n=18):
    """Una gota cada 1,8 s: s'infla al broc, cau, esquitxa i fa onades al bassal; després, quieta."""
    amb = _amb('aixeta')
    base = _base_llum()
    gx, gy, gz = GOTA
    bx, bz, rx, rz = BASSAL
    out = []
    for f in range(n):
        img = amb.copy()
        cv = Canvas(img=img)

        def put(P, lvl):
            u, v = _proj(P)
            cv.put(round(u), round(v), CYAN, lvl, lit=0)
        if f < 4:                                                   # la gota s'infla al broc
            put((gx, gy, gz), 3.0 + f * 0.3)
            if f >= 2:
                put((gx, gy - 1.6, gz), 2.4)
        elif f < 9:                                                 # cau, cada cop més de pressa
            y = gy - gy * ((f - 3) / 5) ** 2
            put((gx, y, gz), 3.8)
            put((gx, y + 1.8, gz), 2.6)
            if f > 5:
                put((gx, y + 3.6, gz), 1.8)
        elif f < 14:                                                # toca el bassal: esquitx i onades
            k = f - 9
            if k < 2:
                for dx, dy in ((-3, 3 + k * 2), (3, 3 + k * 2), (0, 5 + k * 2)):
                    put((gx + dx, dy, gz), 3.6 - k)
            for a in range(0, 360, 10):
                put((gx + math.cos(math.radians(a)) * (3 + k * 3.4), 0.8, gz + math.sin(math.radians(a)) * (1.5 + k * 1.6)),
                    3.2 - k * 0.5)
        out.append(_diff(img, base))
    return out


ANIMS = {
    'ambient': {'frames': _ambient_frames, 'frameDuration': 110},
    'aixeta': {'frames': _gota_frames, 'frameDuration': 100},
}


# ─── Capes del davant ───────────────────────────────────────────────────────

def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


# El marc de la boca del conducte (sempre davant) i la columna de la vàlvula (qui hi passa per darrere, hi queda
# darrere).
FRONT = [{'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20},
         {'id': 'davant_columna', 'mask': _amo({'columna'}), 'baseline': _p(RISER[0], RISER[1])[1], 'zIndex': 20}]


# ─── Geometria (coordenades de sala, projectades) ────────────────────────────

def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


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


_Z0, _Z1, _HO = OBERT
_ZD0, _ZD1, _HD = OBERT_D
# El terra on es camina (al món): la cambra, de la boca fins a l'arc, i l'entrada dels dos passadissos; sense la
# columna de la vàlvula ni les caixes del racó.
WALK_MON = [(8, ZN), (8, _Z0 + 4), (-24, _Z0 + 10), (-24, _Z1 - 10), (8, _Z1 - 4), (8, CD - 14), (370, CD - 14),
            (370, 262), (CW - 8, 250), (CW - 8, _ZD1 - 4), (CW + 24, _ZD1 - 10), (CW + 24, _ZD0 + 10), (CW - 8, _ZD0 + 4),
            (CW - 8, ZN)]
V_PROP = 251                                       # (més avall, el personatge passaria d'1,2: és el primer pla)
_WALK = _retalla([CAM.projecta((x, 0, z))[:2] for x, z in WALK_MON], 2, 0, W - 3, V_PROP)
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)


def _escala_a(v):
    """L'escala d'un personatge amb els peus a la y de pantalla `v` (al terra, la profunditat només depèn de v)."""
    lo, hi = -200.0, 3000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.projecta((CW / 2, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((CW / 2, 0, (lo + hi) / 2))


def _rect_quad(Ps, pad=2):
    r = _rect_mon(*Ps)
    return (r[0] - pad, r[1] - pad, r[2] + pad, r[3] + pad)


_LAMP_P = _p(LAMP[0], LAMP[2])

GEOMETRIA = {
    'things': {
        'esquerra': {'rect': _rect_mon((0, _HO, _Z0), (0, 0, _Z1), (-30, 0, _Z1)), 'walk': _p(-12, (_Z0 + _Z1) / 2)},
        'recte': {'rect': _rect_mon((ARC[0], ARC[3], CD), (ARC[1], 0, CD)), 'walk': _p((ARC[0] + ARC[1]) / 2, CD - 22)},
        'dreta': {'rect': _rect_mon((CW, _HD, _ZD0), (CW, 0, _ZD1), (CW + 30, 0, _ZD1)), 'walk': _p(CW + 12, (_ZD0 + _ZD1) / 2)},
        'enrere': {'rect': (0, 196, 120, BOTTOM), 'walk': _p(40, 6)},
        'cartell': {'rect': _rect_quad(CARTELL_W), 'walk': _p(80, CD - 40)},
        'guant': {'rect': _rect_quad([(GUANT[0] + dx, y, GUANT[1]) for dx in (-18, 18) for y in (0, 16)], 3),
                  'walk': _p(GUANT[0] - 30, GUANT[1] - 20)},
        'aixeta': {'rect': _rect_quad(list(AIXETA_W) + [(BASSAL[0] + BASSAL[2], 0, BASSAL[1] - BASSAL[3])]),
                   'walk': _p(GOTA[0] - 30, CD - 40)},
        'tassa': {'rect': _rect_quad([(TASSA[0] + dx, y, TASSA[1]) for dx in (-14, 14) for y in (0, 22)], 3),
                  'walk': _p(TASSA[0] + 30, TASSA[1] - 20)},
        'formulari': {'rect': _rect_quad(FORMULARI_W), 'walk': _p(236, CD - 40)},
    },
    'spawns': {'iri': _p(150, 20)},
    'walkable': _WALK,
    'forats': [[_p(RISER[0] + 16 * math.cos(2 * math.pi * k / 8), RISER[1] + 14 * math.sin(2 * math.pi * k / 8))
                for k in range(8)]],
    'floorSquash': 0.35,                           # (la càmera, alta: el terra es veu aixafat)
    # L'ombra de contacte: la llum dominant és la làmpada de gàbia (el punt del terra just a sota).
    'characterShadow': {'enabled': True, 'color': '#0a0a10', 'alpha': 0.45, 'squash': 0.36, 'core': 0.6,
                        'light': {'x': _LAMP_P[0], 'y': _LAMP_P[1], 'stretch': 0.7, 'reach': 170}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    # la llum de la sala sobre els personatges, en temps d'execució
    'characterLights': {
        'ambient': '#5c5a68',                                                   # el conducte, fosc
        'lights': [
            {'x': _LAMP_P[0], 'y': _LAMP_P[1] - 70, 'radius': 240, 'color': '#ffd282', 'intensity': 1.0},  # la làmpada
            {'x': 40, 'y': 250, 'radius': 200, 'color': '#ffaa60', 'intensity': 0.8},                      # la reixa
        ],
    },
}
