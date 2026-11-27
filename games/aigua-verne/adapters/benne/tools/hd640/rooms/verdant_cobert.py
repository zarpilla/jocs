"""
Aigua Verne — `verdant_cobert` (P, de prop: persones de ≈100 px). Escena 5. EN 3D (hd640/tres_d.py), a 1×.

El cobert d'en Nil, el jardiner: l'únic lloc de Verdant que és vell i humà. Vist de biaix i una mica des de dalt,
com el pont de la Cantimplora: la paret de la **porta** (oberta al jardí de plàstic, tot massa verd, massa blau) fuig
cap a la cantonada, amb la fulla oberta cap endins; a la paret del fons, el tauler de les **eines**, el prestatge, el
calendari i la finestra bruta. El banc de treball, separat de la paret i una mica girat, amb la ràdio vella; el
tamboret; la pila de **sacs d'adob de plàstic** (lluents, de colors de llaminadura), i darrere els sacs, dins el raig
de llum de la finestra, **la tomaquera**: de debò, en un test, mig seca. Per arribar-hi es passa per darrere dels
sacs. La bombeta penja del tirant; la llum blanca del jardí entra per la porta i s'escampa pel terra en diagonal.
Primer pla: el pal de la quadra a la dreta, una caixa de testos a baix a l'esquerra i la mànega que penja del tirant.

El detall ve del cobert pla de sempre (verdant_cobert_pla_comu.py), dibuixat de cara i projectat: la paret, la porta,
les eines, el prestatge, el calendari, la finestra, els sacs, la ràdio, el tamboret i la tomaquera.

Props: `galleda` (la galleda de zinc d'en Nil, a terra: fins que s'agafa). Decorats: `reg_muntat` (el reg gota a gota del pare, del clau
de la paret del fons fins al test), `galleda_penjada` (la galleda plena, penjada del clau quan s'hi posa) i
`tomaquera_viva` (verda i amb tomàquets).
ANIMS: `pols` (la pols que balla al raig de llum).

El món: x a la dreta (0 = la paret de la porta), y amunt (0 = el terra), z cap al fons (300 = la paret de les eines);
1 unitat = 1 píxel de sala a la distància on un personatge fa 100 px (escala 1).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from PIL import Image

from hd.pix import Canvas, Light, W, H, hr
from hd.rooms.comu import _diff
from hd.rooms.exterior import fbm
from hd640.rooms import verdant_cobert_pla_comu as PL
from hd640.rooms.verdant_comu import (PLANK, WOODG, ZINC, TERRACOTA, BLACKT, HOSE, MAGENTA, CYANF, YELLOWF, galleda)
from hd640.tres_d import Camera, Escena, Llum, llum_personatges

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
ZW = 300                                           # la paret del fons (les eines)
TY0 = 20                                           # al dibuix pla, la paret comença aquí (a sobre, la teulada)
HW = PL.FLOOR_Y - TY0                              # l'alçada de les parets
XL = 112                                           # al dibuix pla, la cantonada: a l'esquerra, la paret de la porta
XR = 612 - XL                                      # on s'acaba el dibuix pla a la paret del fons (més enllà, taulons)
EARTH = PL.EARTH
DOOR_Z = (ZW - XL + PL.DOOR[0], ZW - XL + PL.DOOR[2])   # la porta, a la paret de l'esquerra
WIN_X = (PL.WIN[0] - XL, PL.WIN[2] - XL)                # la finestra, a la paret del fons
WIN_Y = (PL.FLOOR_Y - PL.WIN[3], PL.FLOOR_Y - PL.WIN[1])
BANC = (222, 276, 104, 30, 0.1)                    # el banc: centre (x, z), amplada, fondària, gir
TOMA = (452, 262)                                  # el test de la tomaquera (x, z)
SACS = ((310, 214, 0, 0.42), (368, 206, 0, -0.18), (334, 214, 34, 0.12))   # (x, z, y0, gir)
TAMB = (252, 234)                                  # el tamboret
GALLEDA = (124, 178)                               # la galleda d'en Nil, a terra
BULB = (214, 222)                                  # la bombeta (x, z), penjada del tirant

CAM = Camera(pos=(290, 185, -190), yaw=-0.12, pitch=0.16, f=380, centre=(330, 72))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)   # (la llum és la del món: la de l'Escena)
LLUMS = [
    Llum((BULB[0], 150, BULB[1]), 250, 1.6, power=1.4),           # la bombeta
    Llum((6, 70, (DOOR_Z[0] + DOOR_Z[1]) / 2), 190, 1.8, power=1.3),   # el sol del jardí, per la porta
    Llum(((WIN_X[0] + WIN_X[1]) / 2 + 60, 40, 240), 150, 1.2, power=1.5),   # el raig de la finestra, al racó
]
AMBIENT = -0.3
TL = Light(ambient=0.35, vignette=None, floor_fade=None)      # la llum de les textures (plana: la posa el món)
SUN = (255, 246, 210)                              # el color del raig de la finestra
GARDEN = (236, 255, 226)                           # la llum blanca i verda del jardí, per la porta


# ─── Les textures: el cobert pla de sempre ───────────────────────────────────

def _pla(fn, transparent=True):
    cv = Canvas(light=TL, transparent=transparent)
    fn(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _paret():
    def fn(cv):
        PL.paret(cv)
        PL.porta(cv, fulla=False)
        PL.prestatge(cv)
        PL.eines(cv)
        PL.calendari(cv)
        PL.finestra(cv)
    return _pla(fn, transparent=False)


@functools.lru_cache(maxsize=None)
def _retall(nom):
    """Un dibuix pla retallat: (imatge, el punt de la imatge que toca a terra)."""
    if nom == 'tamboret':
        img = _pla(PL.tamboret)
        return img.crop((314, 186, 356, 228)), (20, 40)
    if nom == 'radio':
        img = _pla(lambda cv: PL.banc(cv, amb_calendari=False))
        return img.crop((286, 110, 382, 158)), (48, 48)
    if nom in ('tomaquera', 'tomaquera_viva'):
        cx, by = PL.POT

        def fn(cv):
            PL.test(cv)
            if nom == 'tomaquera':
                PL.mata_seca(cv)
            else:
                PL.tomaquera_viva(cv)
        return _pla(fn).crop((cx - 44, by - 132, cx + 44, by + 8)), (44, 132)
    if nom == 'galleda':
        return _pla(lambda cv: galleda(cv, 40, 40, s=1.0)).crop((20, 10, 60, 42)), (20, 30)
    if nom == 'galleda_penjada':
        return _pla(lambda cv: galleda(cv, 40, 40, s=0.95, plena=True)).crop((20, 10, 60, 42)), (20, 30)
    raise KeyError(nom)


@functools.lru_cache(maxsize=None)
def _sac(i):
    """El davant d'un sac d'adob (el dibuix pla de sempre), sol."""
    ramp, label = ((CYANF, 'ADOB'), (MAGENTA, 'ADOB'), (YELLOWF, 'ADOB'))[i]
    img = _pla(lambda cv: PL.sac(cv, 10, 10, 54, 34, ramp, label))
    return img, (10, 10, 65, 45), ramp


# ─── Les superfícies ────────────────────────────────────────────────────────

def _taulons(lvl0, pw=13, seed=3, vertical=True):
    """Taulons de fusta vella procedurals (on el dibuix pla no arriba), en coordenades del món."""
    def L(s, t, P):
        u, v = (s, t) if vertical else (t, s)
        col = int(u // pw)
        val = lvl0 + (hr(col, seed) - 0.5) * 0.8 + (fbm(u / 3, v / 40, seed + col) - 0.5) * 1.0
        if u % pw < 1.0:
            val -= 1.8
        elif u % pw < 2.0:
            val += 0.6
        return val
    return L


def _terra(s, t, P):
    """Terra piconada amb serradures i fulles seques (en coordenades del món: grans a prop, petites al fons)."""
    x, z = P[0], P[2]
    v = 3.0 + (fbm(x / 40, z / 30, 131) - 0.5) * 1.3 + (fbm(x / 9, z / 7, 132) - 0.5) * 0.6
    if hr(int(x) // 2, int(z) // 2, 133) > 0.94:
        v += 1.1                                                   # serradures
    if hr(int(x) // 2, int(z) // 2, 134) > 0.985:
        v -= 1.2                                                   # pedretes
    worn = max(0.0, 1 - abs(z - 180) / 90) * max(0.0, 1 - abs(x - 200) / 220)
    return v + worn * 0.5


def _fulles(e):
    """Fulles seques per terra, aplanades (vistes des de dalt)."""
    for i in range(34):
        x, z = 20 + hr(i, 1) * 560, 70 + hr(i, 2) * 220
        r = 3.5 + hr(i, 3) * 2
        e.quad('terra', (x - r, 0.3, z + r * 0.6), (x + r, 0.3, z + r * 0.6), (x + r, 0.3, z - r * 0.6),
               (x - r, 0.3, z - r * 0.6), ramp=[(60, 40, 18), (110, 76, 30), (160, 116, 52), (196, 156, 84)],
               lvl=lambda s, t, P, i=i: 1.6 + (hr(i, 4)) * 1.2 - s * 0.1,
               forma=lambda s, t, r=r: ((s - r) / r) ** 2 + ((t - r * 0.6) / (r * 0.6)) ** 2 < 1)


def _convex(pts):
    pts = sorted(set(pts))
    if len(pts) < 3:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], p) <= 0:
            hi.pop()
        hi.append(p)
    return lo[:-1] + hi[:-1]


# El raig de llum de la finestra: entra de dalt a l'esquerra i cau cap endavant i a la dreta, fins al racó de la
# tomaquera. A terra, un paral·lelogram (els cantons del vidre traslladats al llarg del raig).
RAIG = (0.55, -1.0, -0.72)                         # la direcció del raig (x, y, z), cap avall


def _raig_terra(x, y, z):
    k = y / -RAIG[1]
    return (x + RAIG[0] * k, 0.0, z + RAIG[2] * k)


RAIG_VIDRE = [(WIN_X[0], WIN_Y[1], ZW), (WIN_X[1], WIN_Y[1], ZW), (WIN_X[1], WIN_Y[0], ZW), (WIN_X[0], WIN_Y[0], ZW)]
RAIG_TERRA = [_raig_terra(*P) for P in RAIG_VIDRE]


def _feix(cv, k=0.16):
    """El feix de llum a l'aire (de la finestra fins a terra): una claror suau, a quadres."""
    pts = [CAM.projecta(P)[:2] for P in RAIG_VIDRE + RAIG_TERRA]
    poly = _convex(pts)
    P = cv.P
    x0, x1 = int(min(p[0] for p in poly)), int(max(p[0] for p in poly)) + 1
    y0, y1 = int(min(p[1] for p in poly)), int(max(p[1] for p in poly)) + 1
    for y in range(max(0, y0), min(BOTTOM, y1)):
        for x in range(max(0, x0), min(W, x1)):
            ins = all((b[0] - a[0]) * (y - a[1]) - (b[1] - a[1]) * (x - a[0]) >= 0
                      for a, b in zip(poly, poly[1:] + poly[:1]))
            if not ins:
                continue
            f = k * (0.6 + 0.4 * fbm(x / 7 - y / 14, y / 30, 9)) * (1 if (x + y) % 2 else 0.6)
            o = P[x, y]
            P[x, y] = (int(o[0] + (SUN[0] - o[0]) * f), int(o[1] + (SUN[1] - o[1]) * f),
                       int(o[2] + (SUN[2] - o[2]) * f), o[3])


def escena(cv, tex):
    """Tota la sala, de lluny a prop. → l'Escena (qui ha pintat què)."""
    e = Escena(cv, CAM, LLUMS, ambient=AMBIENT)
    zn = CAM.pos[2] - 100
    paret = tex['paret']
    # el sostre: els taulons de la teulada, foscos, i les bigues
    e.quad('sostre', (0, HW, zn), (W + 260, HW, zn), (W + 260, HW, ZW), (0, HW, ZW), ramp=PLANK,
           lvl=lambda s, t, P: 1.0 + (fbm(P[0] / 30, P[2] / 4, 121) - 0.5) * 0.6 - (0.9 if P[2] % 26 < 2 else 0),
           dues_cares=True)
    # la paret de la porta (x = 0): de prop, taulons; de la porta a la cantonada, el dibuix pla (x 0..112)
    e.quad('paret_esq_prop', (0, HW, zn), (0, HW, ZW - XL), (0, 0, ZW - XL), (0, 0, zn), ramp=PLANK,
           lvl=_taulons(2.4, seed=5))
    e.quad('paret_esq', (0, HW, ZW - XL), (0, HW, ZW), (0, 0, ZW), (0, 0, ZW - XL), tex=(paret, (0, TY0, XL, PL.FLOOR_Y)))
    # la paret del fons (z = 300): el dibuix pla (x 112..612) i, a la dreta, més taulons
    e.quad('paret_fons', (0, HW, ZW), (XR, HW, ZW), (XR, 0, ZW), (0, 0, ZW), tex=(paret, (XL, TY0, 612, PL.FLOOR_Y)))
    e.quad('paret_fons_dreta', (XR, HW, ZW), (W + 260, HW, ZW), (W + 260, 0, ZW), (XR, 0, ZW), ramp=PLANK,
           lvl=_taulons(2.6, seed=7))
    # el terra
    e.quad('terra', (0, 0, ZW), (W + 260, 0, ZW), (W + 260, 0, zn), (0, 0, zn), ramp=EARTH, lvl=_terra)
    _fulles(e)
    # la foscor dels racons: on les parets es troben amb el terra i entre elles
    e.foscor('racons', (0, 0.5, ZW), (W + 260, 0.5, ZW), (W + 260, 0.5, zn), (0, 0.5, zn),
             lambda s, t: max(0.6 * max(0.0, 1 - t / 24), 0.5 * max(0.0, 1 - s / 20)))
    e.foscor('cantonada', (0, HW, ZW - 0.5), (40, HW, ZW - 0.5), (40, 0, ZW - 0.5), (0, 0, ZW - 0.5),
             lambda s, t: 0.5 * max(0.0, 1 - s / 40))
    e.foscor('cantonada2', (0.5, HW, ZW - 40), (0.5, HW, ZW), (0.5, 0, ZW), (0.5, 0, ZW - 40),
             lambda s, t: 0.5 * max(0.0, 1 - (40 - s) / 40))
    e.foscor('sostre_fosc', (0, HW - 0.5, ZW - 0.6), (W + 260, HW - 0.5, ZW - 0.6), (W + 260, HW - 60, ZW - 0.6),
             (0, HW - 60, ZW - 0.6), lambda s, t: 0.45 * max(0.0, 1 - t / 60))
    # el tirant (la biga travessera) i les bigues de la teulada, de lluny a prop
    for z in (ZW - 2, 150):
        e.caixa('bigues', -10, W + 260, HW - 14, HW, z - 12, z, PLANK, 2.4,
                cares={'davant': {'ramp': PLANK, 'lvl': lambda s, t, P: 2.2 + (fbm(s / 30, t / 3, 7) - 0.5) * 0.8},
                       'sota': {'ramp': PLANK, 'lvl': 1.2}})
    # la llum blanca del jardí: entra per la porta i s'escampa pel terra en diagonal, cap endavant i a la dreta
    dz0, dz1 = DOOR_Z
    e.claror((0, 0.4, dz1 + 4), (190, 0.4, dz1 - 40), (190, 0.4, dz0 - 130), (0, 0.4, dz0 - 2), GARDEN,
             lambda s, t: 0.5 * max(0.0, 1 - s / 190) ** 1.1 *
             max(0.0, math.sin(math.pi * min(1.0, t / max(1.0, 70 + 0.5 * s)))))
    # el raig de la finestra, a terra (es veu també damunt del que hi ha a sota: després dels mobles)
    # la fulla de la porta, oberta cap endins (frontisses a la vora del fons de la porta)
    hz = DOOR_Z[1] + 4
    a = math.radians(100)
    dx, dz = math.sin(a), math.cos(a)
    dw = DOOR_Z[1] - DOOR_Z[0]
    dh = PL.FLOOR_Y - PL.DOOR[1]
    e.foscor('ombra_fulla', (2, 0.5, hz), (dw * dx + 8, 0.5, hz + dw * dz), (dw * dx + 8, 0.5, hz + dw * dz - 16),
             (2, 0.5, hz - 16), lambda s, t: 0.45 * max(0.0, 1 - t / 16))
    e.caixa_girada('fulla', 2 + dw * dx / 2, hz + dw * dz / 2, dw, 4, dh, math.atan2(dz, dx), PLANK, 2.6,
                   cares={'davant': {'ramp': PLANK, 'lvl': lambda s, t, P: 2.6 + (fbm(s / 3, t / 40, 141) - 0.5)
                                     - (1.4 if s % 10 < 1 else 0) - (1.0 if abs(t - 24) < 2 or abs(t - dh + 24) < 2 else 0)
                                     + (0.6 if abs(t - (24 + (dh - 48) * s / dw)) < 1.6 else 0)},
                          'darrere': {'ramp': PLANK, 'lvl': 2.2}, 'dalt': {'ramp': PLANK, 'lvl': 3.6},
                          'dreta': {'ramp': PLANK, 'lvl': 1.6}, 'esquerra': {'ramp': PLANK, 'lvl': 3.0}})
    # la tomaquera, al racó, dins el raig de llum
    tx, tz = TOMA
    e.foscor('ombra_test', (tx - 10, 0.6, tz + 16), (tx + 40, 0.6, tz + 16), (tx + 40, 0.6, tz - 16),
             (tx - 10, 0.6, tz - 16), lambda s, t: 0.6 * max(0.0, 1 - ((s - 26) / 24) ** 2 - ((t - 16) / 14) ** 2) * 1.6)
    img, peu = _retall('tomaquera')
    e.sprite('tomaquera', img, peu, (tx, 0, tz))
    # el banc de treball, separat de la paret i una mica girat
    bx, bz, bw, bd, ba = BANC
    c, s_ = math.cos(ba), math.sin(ba)

    def bp(lx, lz):
        return bx + lx * c - lz * s_, bz + lx * s_ + lz * c
    e.foscor('ombra_banc', (bx - bw / 2 - 6, 0.6, bz + 18), (bx + bw / 2 + 14, 0.6, bz + 18),
             (bx + bw / 2 + 14, 0.6, bz - 24), (bx - bw / 2 - 6, 0.6, bz - 24),
             lambda s, t: 0.5 * min(1.0, min(s, t, bw + 20 - s, 42 - t) / 10))
    for lx in (-bw / 2 + 5, bw / 2 - 5):
        for lz in (-bd / 2 + 4, bd / 2 - 4):
            px, pz = bp(lx, lz)
            e.caixa_girada('banc', px, pz, 5, 5, 50, ba, PLANK, 2.6)
    e.caixa_girada('banc', bx, bz, bw - 12, bd - 6, 3, ba, PLANK, 2.4, y0=14,
                   cares={'dalt': {'ramp': PLANK, 'lvl': 3.0}})
    for k, lx in enumerate((-30, -14, 2)):                         # testos buits a la lleixa de baix
        px, pz = bp(lx, 2)
        e.caixa_girada('banc', px, pz, 11, 11, 10, ba + 0.3 * k, TERRACOTA, 3.0, y0=17,
                       cares={'dalt': {'ramp': TERRACOTA, 'lvl': 1.2}})
    e.caixa_girada('banc', bx, bz, bw, bd, 6, ba, PLANK, 3.2, y0=50,
                   cares={'dalt': {'ramp': PLANK, 'lvl': lambda s, t, P: 4.2 - (1.4 if t % 10 < 0.8 else 0)
                                   + (fbm(s / 20, t / 3, 17) - 0.5) * 0.8},
                          'davant': {'ramp': PLANK, 'lvl': 3.0}, 'esquerra': {'ramp': PLANK, 'lvl': 2.2}})
    img, peu = _retall('radio')
    px, pz = bp(0, 6)
    e.sprite('banc', img, peu, (px, 56, pz))
    # els sacs d'adob, apilats i girats, amb l'ombra
    e.foscor('ombra_sacs', (270, 0.6, 250), (420, 0.6, 250), (420, 0.6, 176), (270, 0.6, 176),
             lambda s, t: 0.6 * max(0.0, 1 - ((s - 70) / 80) ** 2 - ((t - 36) / 40) ** 2) * 1.5)
    for i, (sx, sz, sy, sa) in enumerate(SACS):
        img, crop, ramp = _sac(i)
        e.caixa_girada('sacs', sx, sz, 54, 30, 34, sa, ramp, 2.2, y0=sy,
                       cares={'davant': {'tex': (img, crop)},
                              'dalt': {'ramp': ramp, 'lvl': lambda s, t, P: 3.4 - (1.2 if abs(t - 4) < 1 else 0)
                                       + (0.9 if 8 < s < 18 else 0)},
                              'esquerra': {'ramp': ramp, 'lvl': lambda s, t, P: 2.6 - t * 0.02},
                              'dreta': {'ramp': ramp, 'lvl': lambda s, t, P: 1.6 - t * 0.02},
                              'darrere': {'ramp': ramp, 'lvl': 1.4}})
    # el tamboret
    tx, tz = TAMB
    e.foscor('ombra_tamb', (tx - 20, 0.6, tz + 12), (tx + 26, 0.6, tz + 12), (tx + 26, 0.6, tz - 14),
             (tx - 20, 0.6, tz - 14), lambda s, t: 0.55 * max(0.0, 1 - ((s - 23) / 23) ** 2 - ((t - 13) / 13) ** 2) * 1.6)
    img, peu = _retall('tamboret')
    e.sprite('tamboret', img, peu, (tx, 0, tz))
    # trastos arran de la paret del fons, a la dreta: una caixa de fusta i dos taulons recolzats
    e.caixa_girada('trastos', 528, 278, 40, 28, 28, -0.3, PLANK, 2.6,
                   cares={'dalt': {'ramp': PLANK, 'lvl': lambda s, t, P: 3.6 - (1.4 if s % 11 < 1 else 0)},
                          'davant': {'ramp': PLANK, 'lvl': lambda s, t, P: 2.8 - (1.4 if t % 10 < 1 else 0)}})
    for k, x0 in enumerate((556, 570)):
        e.quad('trastos', (x0, 120 - k * 14, ZW - 1), (x0 + 11, 120 - k * 14, ZW - 1), (x0 + 11 + k * 6, 0, ZW - 22),
               (x0 + k * 6, 0, ZW - 22), ramp=WOODG, lvl=lambda s, t, P, k=k: 3.0 - k * 0.6 - (1.2 if s < 1 else 0)
               + (fbm(s / 2, t / 30, 31 + k) - 0.5))
    # el raig de la finestra: la taca a terra i el feix a l'aire
    g = RAIG_TERRA
    e.claror((g[3][0], 0.5, g[3][2]), (g[2][0], 0.5, g[2][2]), (g[1][0], 0.5, g[1][2]), (g[0][0], 0.5, g[0][2]),
             SUN, lambda s, t: 0.42 * (1 if (int(s) + int(t)) % 2 else 0.8))
    _feix(cv)
    # la bombeta, penjada del tirant
    lx, lz = BULB
    e.linia((lx, HW - 14, lz), (lx, 160, lz), BLACKT, 2.0)
    e.caixa('bombeta', lx - 2, lx + 2, 154, 160, lz - 2, lz + 2, ZINC, 2.8)
    _bombeta(cv, *CAM.projecta((lx, 150, lz))[:2], CAM.escala((lx, 150, lz)))
    # primer pla: el pal de la quadra (dreta), la caixa de testos (baix a l'esquerra), la mànega que penja
    e.caixa('primer_pla', 448, 474, 0, HW + 40, 62, 86, PLANK, 1.6,
            cares={'esquerra': {'ramp': PLANK, 'lvl': lambda s, t, P: 1.8 + (fbm(s / 3, t / 30, 5) - 0.5) * 0.8
                                - (1.2 if s < 2 else 0)},
                   'davant': {'ramp': PLANK, 'lvl': lambda s, t, P: 0.9 + (fbm(s / 3, t / 30, 6) - 0.5) * 0.6}})
    e.caixa('primer_pla', 448, 474, HW - 14, HW, 62, ZW, PLANK, 1.4,
            cares={'esquerra': {'ramp': PLANK, 'lvl': 1.4}, 'sota': {'ramp': PLANK, 'lvl': 0.8}})
    e.caixa_girada('primer_pla', 34, 30, 70, 46, 30, 0.35, PLANK, 1.0,
                   cares={'dalt': {'ramp': PLANK, 'lvl': lambda s, t, P: 1.6 - (1.2 if s % 14 < 1.2 else 0)},
                          'davant': {'ramp': PLANK, 'lvl': lambda s, t, P: 0.6 - (0.6 if t % 10 < 1 else 0)},
                          'dreta': {'ramp': PLANK, 'lvl': 0.3}})
    for k, (px, pz) in enumerate(((22, 34), (46, 22), (60, 42))):          # testos de terrissa, de boca
        cilindre(e, 'primer_pla', px, pz, 8, 30, 44, TERRACOTA, lambda a, y, P: 0.5 + math.cos(a + 0.6) * 0.6
                 + (0.8 if y > 41 else 0))
        e.quad('primer_pla', (px - 8, 44.2, pz + 8), (px + 8, 44.2, pz + 8), (px + 8, 44.2, pz - 8), (px - 8, 44.2, pz - 8),
               ramp=TERRACOTA, lvl=0.2, forma=lambda s, t: (s - 8) ** 2 + (t - 8) ** 2 < 49)
    e.cable('primer_pla', [(392, HW, 58), (404, 150, 56), (388, 110, 54), (402, 84, 52)], HOSE, 1.2, gruix=3.0)
    prestatgeria(e)
    e.silueta({'primer_pla'}, 0.5)
    return e


def prestatgeria(e):
    """Primer pla, molt a prop, a baix a l'esquerra: una prestatgeria tallada per la vora (el muntant, dos prestatges
    amb un test i una regadora), en silueta: com si espiéssim el cobert des de darrere."""
    x1, z0, z1 = 168, -62, -26
    e.caixa('primer_pla', x1 - 10, x1, 0, HW + 60, z0, z0 + 10, PLANK, 1.2,
            cares={'dreta': {'ramp': PLANK, 'lvl': lambda s, t, P: 1.8 + (fbm(s / 3, t / 30, 15) - 0.5) * 0.8}})
    e.caixa('primer_pla', x1 - 10, x1, 0, HW + 60, z1 - 10, z1, PLANK, 1.2,
            cares={'dreta': {'ramp': PLANK, 'lvl': 1.8}})
    for y in (58, 124):
        e.caixa('primer_pla', -20, x1, y, y + 6, z0, z1, PLANK, 1.4,
                cares={'dalt': {'ramp': PLANK, 'lvl': lambda s, t, P: 2.2 - (1.0 if s % 16 < 1.2 else 0)},
                       'davant': {'ramp': PLANK, 'lvl': 1.2}})
    cilindre(e, 'primer_pla', 130, -44, 13, 64, 88, TERRACOTA, lambda a, y, P: 0.8 + math.cos(a + 0.6) * 0.6
             + (0.8 if y > 85 else 0))
    for k in range(5):                                             # (una planta seca, que penja)
        a = -0.9 + k * 0.45
        e.cable('primer_pla', [(130, 88, -44), (130 + math.cos(a) * 16, 100 + k % 2 * 6, -44 + math.sin(a) * 6),
                               (130 + math.cos(a) * 26, 92 - k * 2, -44 + math.sin(a) * 8)], WOODG, 1.4, gruix=1.6)
    e.caixa('primer_pla', 80, 112, 130, 152, -52, -34, ZINC, 1.6,                     # la regadora
            cares={'dreta': {'ramp': ZINC, 'lvl': 2.4}})
    e.cable('primer_pla', [(112, 136, -43), (126, 150, -43), (132, 156, -43)], ZINC, 1.8, gruix=2.4)



def cilindre(e, sid, cx, cz, r, y0, y1, ramp, lvl, n=24):
    """Un cilindre vertical: les facetes que es veuen. `lvl(angle, y, P)`."""
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        p0 = (cx + r * math.cos(a0), cz + r * math.sin(a0))
        p1 = (cx + r * math.cos(a1), cz + r * math.sin(a1))
        e.quad(sid, (p0[0], y1, p0[1]), (p1[0], y1, p1[1]), (p1[0], y0, p1[1]), (p0[0], y0, p0[1]), ramp=ramp,
               lvl=lambda s, t, P: lvl(math.atan2(P[2] - cz, P[0] - cx), P[1], P))


def _bombeta(cv, u, v, k):
    r = max(1.5, 3.5 * k)
    cv.disc(u, v, r, r * 1.1, [(200, 160, 80), (250, 220, 140), (255, 246, 210), (255, 255, 240)],
            lambda nx, ny: 2.6 - ny * 0.6, lit=0)
    cv.glow(u, v, 56, (255, 220, 150), 0.45)


# ─── Composició ────────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _textures():
    return {'paret': _paret()}


@functools.lru_cache(maxsize=None)
def _base():
    cv = Canvas(light=LIGHT)
    e = escena(cv, _textures())
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)    # la barra de verbs: negre
    return cv.img, e


def bg(cv):
    img, _ = _base()
    cv.img.paste(img)
    cv.P = cv.img.load()


def _davant_de(e2, ids):
    """Esborra de la capa `e2` el que, al fons, queda tapat per les superfícies `ids` (el primer pla, els sacs)."""
    _, e = _base()
    P, W_ = e2.cv.P, e.cv.w
    for y in range(e.cv.h):
        for x in range(W_):
            if e.ids[e.amo[y * W_ + x]] in ids:
                P[x, y] = (0, 0, 0, 0)


def _sprite_sol(nom, peu, ids_davant=('primer_pla',)):
    def fn(cv):
        c2 = Canvas(light=LIGHT, transparent=True)
        e2 = Escena(c2, CAM, LLUMS, ambient=AMBIENT)
        img, pi = _retall(nom)
        e2.sprite(nom, img, pi, peu)
        _davant_de(e2, set(ids_davant))
        cv.img.alpha_composite(c2.img)
    return fn


def p_galleda(cv):
    x, z = GALLEDA
    c2 = Canvas(light=LIGHT, transparent=True)
    e2 = Escena(c2, CAM, LLUMS, ambient=AMBIENT)
    _, e = _base()
    # l'ombra: s'enfosqueix el fons (copiat) on toca, només a la capa
    base = _base()[0]
    c2.img.paste(base)
    c2.P = c2.img.load()
    e2.foscor('ombra', (x - 14, 0.6, z + 10), (x + 22, 0.6, z + 10), (x + 22, 0.6, z - 10), (x - 14, 0.6, z - 10),
              lambda s, t: 0.6 * max(0.0, 1 - ((s - 18) / 18) ** 2 - ((t - 10) / 10) ** 2) * 1.6)
    img, pi = _retall('galleda')
    e2.sprite('galleda', img, pi, (x, 0, z))
    out = _diff(c2.img, base)
    cv.img.alpha_composite(out)


def _galleda_penjada_pos():
    tx, _ = TOMA
    return tx + 14, 120


def reg_muntat(cv):
    """El reg gota a gota del pare, muntat: el tub negre que puja per la paret del fons, damunt la tomaquera, fins al
    clau on es penjarà la galleda (el cap del tub, a punt per a l'aigua), i que baixa fins al test, on hi fa la volta
    amb tres goters verds. La galleda penjada és un altre decorat (`galleda_penjada`): no hi és fins que s'hi posa."""
    tx, tz = TOMA
    c2 = Canvas(light=LIGHT, transparent=True)
    e2 = Escena(c2, CAM, LLUMS, ambient=AMBIENT)
    gx, gy = _galleda_penjada_pos()
    e2.linia((gx - 1, gy + 34, ZW - 1), (gx + 1, gy + 34, ZW - 1), ZINC, 3.0)          # el clau
    e2.cable('reg', [(gx + 1, gy + 32, ZW - 2), (gx, gy + 14, ZW - 3), (gx, gy - 2, ZW - 3), (gx + 2, 70, ZW - 2), (gx + 3, 2, ZW - 2),
                     (gx - 2, 1.5, ZW - 14), (tx + 14, 1.5, tz + 14), (tx + 8, 26, tz + 4)], HOSE, 2.6, gruix=1.8)
    for a in range(0, 360, 8):                                     # la volta damunt la terra del test
        ra = math.radians(a)
        e2.cable('reg', [(tx + math.cos(ra) * 12, 26, tz + math.sin(ra) * 12),
                         (tx + math.cos(ra + 0.15) * 12, 26, tz + math.sin(ra + 0.15) * 12)], HOSE,
                 3.0 if math.sin(ra) < 0 else 1.6, gruix=1.4)
    for a in (40, 150, 270):
        ra = math.radians(a)
        u, v, _ = CAM.projecta((tx + math.cos(ra) * 12, 26, tz + math.sin(ra) * 12))
        c2.rect(u - 1, v - 1, u + 1, v, [(10, 60, 20), (30, 120, 40), (80, 190, 80)], 1.6, lit=0)
        c2.flat(u, v + 1, (170, 220, 250))
    _davant_de(e2, {'primer_pla'})
    cv.img.alpha_composite(c2.img)


def galleda_penjada(cv):
    """La galleda plena, penjada del clau per la nansa, amb el tub del reg que en surt per sota."""
    c2 = Canvas(light=LIGHT, transparent=True)
    e2 = Escena(c2, CAM, LLUMS, ambient=AMBIENT)
    gx, gy = _galleda_penjada_pos()
    e2.linia((gx, gy + 34, ZW - 1), (gx - 11, gy + 22, ZW - 1), ZINC, 3.0)
    e2.linia((gx, gy + 34, ZW - 1), (gx + 11, gy + 22, ZW - 1), ZINC, 3.0)
    img, pi = _retall('galleda_penjada')
    e2.sprite('reg', img, pi, (gx, gy, ZW - 4))
    _davant_de(e2, {'primer_pla'})
    cv.img.alpha_composite(c2.img)


PROPS = {
    'galleda': p_galleda,
    'reg_muntat': reg_muntat,
    'galleda_penjada': galleda_penjada,
    'tomaquera_viva': _sprite_sol('tomaquera_viva', (TOMA[0], 0, TOMA[1])),
}


def _frames_pols():
    """La pols que balla al raig de llum de la finestra (punts del món, dins el feix)."""
    base, e = _base()
    frames = []
    n = 16
    for i in range(n):
        im = Image.new('RGBA', base.size, (0, 0, 0, 0))
        P, B = im.load(), base.load()
        for j in range(46):
            a, b = hr(j, 3), hr(j, 4)
            t = (hr(j, 1) + i / n * (0.25 + hr(j, 2) * 0.25)) % 1.0
            top = (WIN_X[0] + (WIN_X[1] - WIN_X[0]) * a, WIN_Y[0] + (WIN_Y[1] - WIN_Y[0]) * b, ZW - 1)
            k = top[1] * t
            Pw = (top[0] + RAIG[0] * k + math.sin(i * 0.4 + j) * 2, top[1] - k, top[2] + RAIG[2] * k)
            u, v, _ = CAM.projecta(Pw)
            x, y = int(u), int(v)
            if 0 <= x < W and 0 <= y < BOTTOM and hr(j, i // 4, 9) > 0.3:
                ow = e.ids[e.amo[y * W + x]]
                if ow in ('primer_pla', 'sacs', 'banc'):
                    continue
                o = B[x, y]
                P[x, y] = (int(o[0] + (255 - o[0]) * 0.7), int(o[1] + (250 - o[1]) * 0.7), int(o[2] + (220 - o[2]) * 0.7), 255)
        frames.append(im)
    return frames


ANIMS = {'pols': {'frames': _frames_pols, 'frameDuration': 180}}


def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _v(x, z):
    return round(CAM.projecta((x, 0, z))[1])


# Capes del davant: es passa per darrere dels sacs (per arribar a la tomaquera) i del tamboret.
FRONT = [
    {'id': 'davant_sacs', 'mask': _amo({'sacs'}), 'baseline': _v(340, 214), 'zIndex': 20},
    {'id': 'davant_tamboret', 'mask': _amo({'tamboret'}), 'baseline': _v(*TAMB), 'zIndex': 20},
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20},
]


# ─── Geometria (coordenades de sala, projectades) ────────────────────────────

def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


def _fons(fx, fy):
    """Un punt del dibuix pla de la paret del fons, al món."""
    return (fx - XL, PL.FLOOR_Y - fy, ZW)


def _caixa_terra(cx, cz, w, d, ang, m=6):
    """Els quatre cantons (a terra, projectats) d'un moble girat, amb un marge: un forat al terra on es camina."""
    c, s = math.cos(ang), math.sin(ang)
    a, b = w / 2 + m, d / 2 + m
    return [_p(cx + lx * c - lz * s, cz + lx * s + lz * c) for lx, lz in ((-a, -b), (a, -b), (a, b), (-a, b))]


# El terra on es camina (al món): de la porta fins al pal de la dreta, del banc i la tomaquera fins a la caixa de
# testos del primer pla. Forats: els sacs, el banc i el tamboret (s'hi pot fer la volta).
def _z_a(x, v):
    """La z del terra que cau a la y de pantalla `v` a la x del món `x`."""
    lo, hi = 1.0, 2000.0
    for _ in range(50):
        z = (lo + hi) / 2
        if CAM.projecta((x, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return round((lo + hi) / 2)


V_PROP = 236                                       # el terra on es camina no baixa d'aquí (escala ≈1,2)
WALK_MON = [(14, _z_a(14, V_PROP)), (430, _z_a(430, V_PROP)), (430, 244), (424, 254), (150, 256), (40, 254),
            (14, 236)]
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


GEOMETRIA = {
    'things': {
        'porta': {'rect': _rect_mon((0, PL.FLOOR_Y - PL.DOOR[1] + 6, DOOR_Z[0] - 6), (0, 0, DOOR_Z[1] + 6)),
                  'walk': _p(30, 240)},
        'tomaquera': {'rect': _rect_mon((TOMA[0] - 26, 134, TOMA[1]), (TOMA[0] + 30, 0, TOMA[1])),
                      'walk': _p(TOMA[0] - 30, TOMA[1] - 26)},
        'galleda': {'rect': _rect_mon((GALLEDA[0] - 18, 30, GALLEDA[1]), (GALLEDA[0] + 18, 0, GALLEDA[1])),
                    'walk': _p(GALLEDA[0] - 20, GALLEDA[1] - 30)},
        'sacs': {'rect': _rect_mon((282, 70, 200), (400, 0, 196), (282, 0, 230), (400, 70, 230)),
                 'walk': _p(330, 170)},
        'eines': {'rect': _rect_mon(_fons(128, 40), _fons(262, 200)),
                  'walk': _p(84, 246)},
    },
    'spawns': {'iri': _p(150, 150), 'vet': _p(330, 140)},
    'walkable': _WALK,
    'forats': [_caixa_terra(*BANC[:2], BANC[2], BANC[3], BANC[4], 4)]
              + [_caixa_terra(x, z, 54, 30, a, 4) for x, z, y0, a in SACS if y0 == 0]
              + [_caixa_terra(*TAMB, 26, 22, 0, 4)],
    'floorSquash': 0.45,
    'characterShadow': {'enabled': True, 'color': '#1a120c', 'alpha': 0.42, 'squash': 0.45, 'core': 0.6,
                        'light': {'x': _p(*BULB)[0], 'y': _p(*BULB)[1], 'stretch': 0.7, 'reach': 110}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    # La llum de la sala sobre els personatges (characterLights del motor): el cobert de fusta, fosc: la bombeta, el
    # sol del jardí per la porta i el raig de la finestra.
    'characterLights': {
        'ambient': '#7c6c5c',
        'lights': [
            llum_personatges(CAM, LLUMS[0].pos, LLUMS[0].r, '#ffd890', 0.45),  # la bombeta
            llum_personatges(CAM, LLUMS[1].pos, LLUMS[1].r, '#f4ffe0', 0.6),  # el sol del jardí, per la porta
            llum_personatges(CAM, LLUMS[2].pos, LLUMS[2].r, '#fff4c8', 0.4),  # el raig de la finestra
        ],
    },
}
