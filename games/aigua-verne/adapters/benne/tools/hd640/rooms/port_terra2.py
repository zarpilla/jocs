"""
El port de Terra-2 (Escena 2). Sala «de lluny» (persones de ≈83 px). EN 3D (hd640/tres_d.py), a 1×.

Una càmera baixa (sense picat: les verticals, verticals), amb l'horitzó a y = 112, que fa la nau imponent:
  - a la dreta, la **Cantimplora** en 3/4: se'n veu la popa (els dos motors i el sutge) i el costat panxut, que fuig
    cap al fons a la dreta, amb els nou dipòsits rodons a l'esquena, les potes de terratge i la porta de la bodega
    oberta, amb la rampa abaixada fins a terra i la llum càlida de dins que s'hi vessa;
  - el cercle d'aterratge, pintat i mig esborrat, al terra al voltant de la nau; roderes, taques d'oli i fang clivellat
    que s'empetiteixen cap al fons;
  - a l'esquerra, el tauler d'anuncis de suro (girat, damunt dels pals) i el pal indicador del camí de la granja, que
    surt per l'esquerra;
  - al fons, una pila de contenidors de Verne (blancs, la gota blava) i un de rovellat, girats; la grua de pòrtic
    parada, amb el ganxo penjant; el panell del preu; uns bidons; els hangars i la **Canonada** a l'horitzó, entre
    dunes;
  - primer pla: unes roques i matolls secs a baix a l'esquerra, i la mànega de combustible i el seu sortidor, foscos,
    a baix a la dreta.
Es passa per darrere del tauler, dels bidons, del sortidor, de la rampa i de la nau (per trams).

El detall (el tauler, els contenidors, els dipòsits, els hangars, el rètol del pal) ve del port pla de sempre
(port_terra2_pla_comu.py), dibuixat de cara i projectat. ANIMS: `pols`, `llum_canonada` i `balisa` (el llum de navegació
vermell, dalt del pal de proa). La nau és la canònica (cantimplora_comu.py).

El món: x a la dreta (0 = la càmera), y amunt, z endavant; 1 unitat = 1 px a la distància on un personatge fa la seva
mida normal (z = 500·130/(v − 112)). Al terra, l'escala d'un personatge és (v − 112) / 130, exacta.
"""
import functools
import math
from array import array

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from PIL import Image

from hd.pix import Canvas, Light, W, H, hr, mix
from hd.rooms.exterior import fbm, smooth, vnoise
from hd640.rooms import port_terra2_pla_comu as PL
from hd640.rooms.terra2_comu import (
    RH, EARTH, STONE, PLANK, GREYW, WHITEP, BLUE, BLACKT, IRONR, RUSTT, OLIVE, ORANGE, WARN, GRASS, HILL, COL,
    gota, dust_sky, canonada, panell_preu, cracks, dust_wind_frames, llum_canonada_frames)
from hd640.rooms.cantimplora_comu import Cantimplora
from hd640.tres_d import Camera, Escena, Llum

HOR = 112                                          # l'horitzó
CH = 130                                           # l'alçada de la càmera
CAM = Camera(pos=(0, CH, 0), yaw=0.0, pitch=0.0, f=500, centre=(320, HOR))
CAN_U = 252                                        # la Canonada, a l'horitzó (x de pantalla)
SUN = (590, 24)

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)
LLUMS = [Llum((6000, 5000, 2000), 1e6, 2.0, power=1.0)]   # el sol, a dalt a la dreta (ombres cap a l'esquerra)
AMBIENT = -1.1

# La Cantimplora (el model canònic, cantimplora_comu): la popa, a prop i a la dreta; l'eix fuig cap al fons a
# l'esquerra, cap a la Canonada; la porta, a babord (el costat que es veu)
STERN = (250.0, 650.0)                             # la popa (x, z), arran de terra sota l'eix
NAU_B = math.radians(35)
SEGS = (0, 80, 160, 240, 320, 400)                 # els trams del buc (cada un, una capa del davant)
NAU = Cantimplora(popa=STERN, rumb=math.pi / 2 + NAU_B, porta='babord', trams=SEGS)
NAU_T = Cantimplora(popa=STERN, rumb=math.pi / 2 + NAU_B, porta='babord', sid='naut')   # la de l'enlairament
NAU_A = NAU.ang                                  # (el gir de les peces alineades amb l'eix)
NR, NL = NAU.NR, NAU.NL
PORTA_L, PORTA_T, RAMPA_OUT = NAU.PORTA_L, NAU.PORTA_T, NAU.RAMPA_OUT
SOL = (0.55, 1.0, -0.1)                            # cap al sol (a dalt a la dreta): les ombres, cap a l'esquerra

TAULER = (-300.0, 720.0, 0.62)                     # x, z, gir
PAL = (-330.0, 590.0)
PANELL = (-150.0, 1200.0)
BIDONS = (-226.0, 900.0)
SORTIDOR = (300.0, 545.0)
GRUA = (-720.0, 1950.0)


def _add(a, b, k=1.0):
    return (a[0] + b[0] * k, a[1] + b[1] * k, a[2] + b[2] * k)


def _up(P, h):
    return (P[0], P[1] + h, P[2])


def nau_terra(l, off):
    """Un punt del terra: `l` al llarg de l'eix, `off` cap al costat que es veu."""
    return NAU.terra(l, off)


# ─── Les textures: el port pla de sempre, i el buc desenrotllat ──────────────

def _pla(fn, w=W, h=H):
    cv = Canvas(w, h, light=PL.LIGHT, transparent=True)
    fn(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _textures():
    def contenidor(kind, lvl):
        cv = Canvas(140, 62, light=PL.LIGHT, transparent=True)
        PL.container(cv, 0, 60, 139, 58, kind, lvl, gr=9, portes=False)
        return cv.img

    def tauler(cv):
        PL.tauler(cv)

    def pal(cv):
        PL.cami(cv)

    def hangars(cv):
        PL.hangars(cv)
    return {
        'verne': contenidor('verne', 3.6),
        'verne2': contenidor('verne', 4.0),
        'rovell': contenidor('rovell', 3.4),
        'tauler': _pla(tauler),
        'pal': _pla(pal),
        'hangars': _pla(hangars),
        'panell': _pla(lambda cv: panell_preu(cv, 10, 10, post=0)),
    }


# ─── El fons (en pantalla): el cel, les dunes, la Canonada ─────────────────────

def fons(cv):
    dust_sky(cv, HOR, sun=SUN)
    for x in range(W):                                             # dunes: dues capes, amb desnivells
        h1 = HOR - 4 - 14 * fbm(x / 150, 0.3, 7) - 5 * fbm(x / 40, 0.9, 8)
        h2 = HOR - 1 - 6 * fbm(x / 60, 1.7, 9)
        for y in range(int(h1), HOR + 5):
            cv.put(x, y, HILL, 4.6 - (y - h1) * 0.04 + (fbm(x / 30, y / 6, 4) - 0.5) * 0.6, lit=0)
        for y in range(int(h2), HOR + 5):
            cv.put(x, y, HILL, 3.4 + (fbm(x / 8, y / 4, 3) - 0.5) * 0.8 - (y - h2) * 0.05, lit=0)
    canonada(cv, CAN_U, HOR + 1, haze=(230, 214, 180))


# ─── El terra (en el món) ────────────────────────────────────────────────────

def _dist_seg(x, z, A, B):
    dx, dz = B[0] - A[0], B[1] - A[1]
    u = max(0.0, min(1.0, ((x - A[0]) * dx + (z - A[1]) * dz) / (dx * dx + dz * dz)))
    return math.hypot(x - A[0] - dx * u, z - A[1] - dz * u), u


CAMI = [(-900.0, 700.0), (-420.0, 670.0), (-150.0, 700.0)]       # el camí de la granja (cap a l'esquerra)
CERCLE = (nau_terra(270, 0), 360.0)                                # el cercle d'aterratge: el centre i el radi
TAQUES = [(-60, 600, 26, 12), (150, 520, 34, 14), (-260, 900, 30, 12), (330, 700, 40, 16), (90, 1150, 50, 18)]


def _terra(s, t, P):
    x, z = P[0], P[2]
    far = smooth(800, 2200, z)
    c = cracks(int(x), int(z * 0.6), cell=24)
    lvl = 4.6 + (fbm(x / 70, z / 50, 17) - 0.5) * 1.3
    if c < 1.4 * (1 - far * 0.8) and vnoise(x / 120, z / 90, 3) > 0.45:
        lvl -= 1.8 * (1 - far)                                     # clivelles, només a clapes
    elif c < 2.8:
        lvl += 0.3 * (1 - far)
    # el camí de la granja: terra trepitjada, amb les roderes
    for A, B in zip(CAMI, CAMI[1:]):
        d, _ = _dist_seg(x, z, A, B)
        if d < 38 + (fbm(x / 40, z / 40, 6) - 0.5) * 16:
            rut = abs(d / 38 - 0.5) < 0.1
            lvl = 6.2 + (hr(int(x) // 3, int(z) // 3) - 0.5) * 0.6 - (1.0 if rut else 0)
    # les roderes de les vagonetes, del camí cap a la rampa
    rx, rz = nau_terra(sum(PORTA_L) / 2, RAMPA_OUT + 20)
    for off in (-14, 14):
        d, u = _dist_seg(x, z, (CAMI[-1][0], CAMI[-1][1] + off), (rx, rz + off))
        if d < 2.2 and 0 < u < 1:
            lvl -= 0.8 * (1 - far)
    # el cercle d'aterratge, pintat i mig esborrat
    (cx, cz), cr = CERCLE
    dc = math.hypot(x - cx, z - cz)
    if abs(dc - cr) < 7 or abs(dc - cr + 22) < 3:
        if hr(int(math.atan2(z - cz, x - cx) * 60), int(dc) // 6, 5) > 0.3:
            lvl = 7.4 - far * 1.4
    # les taques d'oli
    for ox, oz, rx_, rz_ in TAQUES:
        q = ((x - ox) / rx_) ** 2 + ((z - oz) / rz_) ** 2
        if q < 1.6 and q < 1 + vnoise(x / 9, z / 9, ox) * 0.6:
            lvl -= 1.6 * (1 - q * 0.4)
    return lvl


# ─── Les peces ──────────────────────────────────────────────────────────────

def cilindre(e, sid, cx, cz, r, y0, y1, ramp, lvl, n=24):
    """Un cilindre vertical: les facetes que es veuen. `lvl(angle, y, P)`."""
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        p0 = (cx + r * math.cos(a0), cz + r * math.sin(a0))
        p1 = (cx + r * math.cos(a1), cz + r * math.sin(a1))
        e.quad(sid, (p0[0], y1, p0[1]), (p1[0], y1, p1[1]), (p1[0], y0, p1[1]), (p0[0], y0, p0[1]), ramp=ramp,
               lvl=lambda s, t, P: lvl(math.atan2(P[2] - cz, P[0] - cx), P[1], P))


def tapa(e, sid, cx, cz, r, y, ramp, lvl):
    sq = ((cx - r, y, cz + r), (cx + r, y, cz + r), (cx + r, y, cz - r), (cx - r, y, cz - r))
    e.quad(sid, *sq, ramp=ramp, lvl=lvl, forma=lambda s, t: (s - r) ** 2 + (t - r) ** 2 <= r * r)


def ombra(e, cx, cz, rx, rz, k=0.55, ang=0.0):
    """Una ombra el·líptica al terra (girada `ang`)."""
    c, s_ = math.cos(ang), math.sin(ang)

    def P(a, b):
        return (cx + a * c - b * s_, 0.3, cz + a * s_ + b * c)
    e.foscor('ombra', P(-rx, rz), P(rx, rz), P(rx, -rz), P(-rx, -rz),
             lambda s, t: k * min(1.0, 1.8 * max(0.0, 1 - ((s - rx) / rx) ** 2 - ((t - rz) / rz) ** 2)))


def nau(e, tex, mode='oberta'):
    """`mode`: 'oberta' (la de sempre: la porta oberta, la rampa baixada i la mànega), 'tancada' (a punt d'enlairar-se:
    la porta tancada, sense rampa ni mànega; amb un model a part, perquè el de sempre és el de les capes) o None."""
    if mode is None:
        return
    if mode in ('tancada', 'sola'):
        NAU_T.dibuixa(e, porta_oberta=False, ombra={'sol': SOL, 'k': 0.55})
        return
    NAU.dibuixa(e, ombra={'sol': SOL, 'k': 0.55})
    # la mànega de combustible: del ventre de la nau al sortidor
    e.cable('sortidor', [NAU.buc(-6, -1.2), (nau_terra(-10, 90)[0], 6, nau_terra(-10, 90)[1]),
                         (SORTIDOR[0] - 4, 3, SORTIDOR[1] + 14), (SORTIDOR[0], 26, SORTIDOR[1] + 4)], BLACKT, 2.2, gruix=4)


def grua(e):
    """La grua de pòrtic, parada: quatre potes, la torre de gelosia, la cabina, el braç i el ganxo."""
    gx, gz = GRUA
    Y = [(40, 30, 10), (76, 58, 18), (116, 90, 30), (156, 124, 44), (192, 158, 64), (220, 190, 96)]
    for dx, dz in ((-40, -30), (40, -30), (-40, 30), (40, 30)):
        e.caixa('grua', gx + dx - 3, gx + dx + 3, 0, 80, gz + dz - 3, gz + dz + 3, Y, 3.0)
    e.caixa('grua', gx - 44, gx + 44, 80, 90, gz - 34, gz + 34, Y, 3.6)
    for (a, b) in (((-40, -30), (40, -30)), ((-40, 30), (40, 30))):                 # creus del pòrtic
        e.cable('grua', [(gx + a[0], 78, gz + a[1]), (gx + b[0], 4, gz + b[1])], Y, 2.6, gruix=2)
        e.cable('grua', [(gx + b[0], 78, gz + b[1]), (gx + a[0], 4, gz + a[1])], Y, 2.2, gruix=2)
    top = 330
    for dx, dz in ((-9, -9), (9, -9), (-9, 9), (9, 9)):                            # la torre
        e.caixa('grua', gx + dx - 1.5, gx + dx + 1.5, 90, top, gz + dz - 1.5, gz + dz + 1.5, Y, 3.6 if dx > 0 else 2.6)
    for y in range(90, top - 10, 20):
        e.cable('grua', [(gx - 9, y, gz - 9), (gx + 9, y + 20, gz - 9)], Y, 2.6, gruix=1.2)
        e.cable('grua', [(gx + 9, y, gz - 9), (gx + 9, y + 20, gz + 9)], Y, 3.4, gruix=1.2)
    # la cabina i el braç (cap a l'esquerra i endavant, sobre els contenidors), i el contrapès
    e.caixa('grua', gx - 12, gx + 14, top, top + 20, gz - 12, gz + 12, Y, 3.6,
            cares={'davant': {'ramp': Y, 'lvl': lambda s, t, P: 1.0 if 3 < s < 16 and 4 < t < 12 else 3.8}})
    ja = math.radians(160)
    dj = (math.cos(ja), 0, math.sin(ja))
    J0 = (gx, top + 26, gz)
    J1 = _add(J0, dj, 260)
    for h in (0, -7):
        e.cable('grua', [_up(J0, h), _up(J1, h + 4)], Y, 4.0 if h == 0 else 2.6, gruix=1.6)
    for k in range(0, 250, 14):
        A = _up(_add(J0, dj, k), 0)
        B = _up(_add(J0, dj, k + 14), -7)
        e.cable('grua', [A, B], Y, 2.2, gruix=1.0)
    CW = _add(J0, dj, -50)
    e.caixa('grua', CW[0] - 14, CW[0] + 14, top + 6, top + 26, CW[2] - 10, CW[2] + 10, IRONR, 2.4)
    e.cable('grua', [_up(J0, 34), _up(J1, 4)], IRONR, 1.6, gruix=0.8)
    e.cable('grua', [_up(J0, 34), _up(CW, 26)], IRONR, 1.6, gruix=0.8)
    H_ = _add(J0, dj, 150)
    e.cable('grua', [_up(H_, -6), (H_[0], 120, H_[2])], IRONR, 1.8, gruix=1.2)
    e.caixa('grua', H_[0] - 6, H_[0] + 6, 104, 120, H_[2] - 4, H_[2] + 4, WARN, 3.4)
    ombra(e, gx - 30, gz, 70, 40, 0.4)


def contenidors(e, tex):
    """Una pila de contenidors de Verne, girats, i un de rovellat a part."""
    CW, CHt, CD = 210, 88, 86

    def cont(cx, cz, ang, y0, kind):
        img = tex[kind]
        ramp = RUSTT if kind == 'rovell' else WHITEP

        def cap(s, t, P):
            return 3.0 + (0.8 if s % 9 < 4 else -0.2) - (1.4 if abs(s - CD / 2) < 1.2 else 0) \
                + (1.4 if abs(s - CD / 2 + 14) < 1 or abs(s - CD / 2 - 14) < 1 else 0)
        e.caixa_girada('contenidors', cx, cz, CW, CD, CHt, ang, ramp, 3.4, y0=y0,
                       cares={'davant': {'tex': (img, (0, 2, 140, 61))},
                              'darrere': {'tex': (img, (0, 2, 140, 61))},
                              'esquerra': {'ramp': ramp, 'lvl': cap},
                              'dreta': {'ramp': ramp, 'lvl': cap},
                              'dalt': {'ramp': ramp, 'lvl': lambda s, t, P: 4.6 - (1.0 if s % 24 < 2 else 0)}})
    ombra(e, -470, 1480, 220, 80, 0.5, ang=0.45)
    cont(-560, 1380, -0.5, 0, 'rovell')
    cont(-420, 1520, 0.45, 0, 'verne')
    cont(-290, 1590, 0.45, 0, 'verne2')
    cont(-370, 1550, 0.5, CHt, 'verne')


def tauler(e, tex):
    """El tauler d'anuncis de suro, damunt de dos pals, amb la teuladeta: girat cap a la plaça."""
    x, z, ang = TAULER
    tb = (math.cos(ang), 0, math.sin(ang))
    nb = (math.sin(ang), 0, -math.cos(ang))
    img = tex['tauler']
    # al pla: el tauler és x 42..130, y 92..204 (la base); 1 px del pla = 1,15 unitats
    k = 1.15
    W_ = (130 - 42) * k

    def fp(fx, fy):
        return _add((x, (204 - fy) * k, z), tb, (fx - 86) * k)
    ombra(e, x - 50, z + 10, 70, 20, 0.45, ang=ang)
    for px_ in (54, 116):                                                  # els pals
        P = fp(px_ + 1, 204)
        e.caixa_girada('tauler', P[0], P[2], 4, 4, (204 - 102) * k, ang, GREYW, 3.0)
    e.quad('tauler', fp(42, 92), fp(130, 92), fp(130, 160), fp(42, 160), tex=(img, (42, 92, 130, 160)))
    # el gruix del marc i la teuladeta, de xapa
    A, B = fp(36, 96), fp(136, 96)
    e.quad('tauler', _add(A, nb, 9), _add(B, nb, 9), _up(B, 2), _up(A, 2), ramp=RUSTT, dues_cares=True,
           lvl=lambda s, t, P: 3.2 + (0.8 if s % 5 < 2.4 else -0.4))
    e.quad('tauler', _add(fp(130, 158), nb, 0), _add(fp(130, 158), nb, -4), _add(fp(130, 108), nb, -4),
           _add(fp(130, 108), nb, 0), ramp=PLANK, lvl=2.6, dues_cares=True)
    return W_


def pal(e, tex):
    """El pal indicador del camí de la granja (el rètol, del pla)."""
    x, z = PAL
    img = tex['pal']
    ombra(e, x - 16, z + 4, 22, 8, 0.45)
    e.sprite('pal', img.crop((0, 172, 46, 204)), (23, 32), (x, 0, z), escala_img=1.4)


def panell(e, tex):
    cx, cz = PANELL
    ang = -0.35
    tb = (math.cos(ang), 0, math.sin(ang))
    img = tex['panell']
    hw, hh = 64, 27
    c = (cx, 60 + hh, cz)
    ombra(e, cx - 50, cz, 70, 20, 0.4, ang=ang)
    for k in (-36, 36):
        p = _add((cx, 0, cz), tb, k)
        e.caixa('panell', p[0] - 3, p[0] + 3, 0, 60, p[2] - 3, p[2] + 3, IRONR, 2.6)
    e.quad('panell', _up(_add(c, tb, -hw), hh), _up(_add(c, tb, hw), hh), _up(_add(c, tb, hw), -hh),
           _up(_add(c, tb, -hw), -hh), tex=(img, (9, 9, 69, 35)))


def bidons(e):
    bx, bz = BIDONS
    ombra(e, bx - 26, bz + 4, 46, 18, 0.55)
    for k, (dx, dz, y0) in enumerate(((-14, 6, 0), (12, 0, 0), (0, -16, 0), (-2, 2, 40))):
        ramp = (ORANGE, OLIVE, RUSTT, OLIVE)[k]
        x, z = bx + dx, bz + dz
        cilindre(e, 'bidons', x, z, 13, y0, y0 + 40, ramp, n=14, lvl=
                 lambda a, y, P, y0=y0: 3.0 + math.cos(a + 0.9) * -0.9 - (1.2 if (y - y0) % 13 < 1.6 else 0)
                 + (fbm(P[0] / 4, y / 6, 3) - 0.5) * 0.8)
        tapa(e, 'bidons', x, z, 13, y0 + 40, ramp, lambda s, t, P: 4.4 - (1.4 if abs(math.hypot(s - 13, t - 13) - 9) < 1 else 0))


def sortidor(e):
    """El sortidor de combustible i la mànega, gruixuda i fosca, que va de la nau cap a la càmera."""
    sx, sz = SORTIDOR
    ombra(e, sx - 30, sz + 6, 40, 16, 0.55)
    e.caixa_girada('sortidor', sx, sz, 34, 24, 70, 0.25, IRONR, 2.2,
                   cares={'davant': {'ramp': IRONR, 'lvl': lambda s, t, P: 2.4 + (2.0 if 6 < s < 28 and 10 < t < 22 else 0)
                                     - (1.0 if t % 30 < 1.4 else 0)},
                          'dalt': {'ramp': IRONR, 'lvl': 3.6}})
    e.caixa_girada('sortidor', sx, sz, 30, 20, 6, 0.25, WARN, 3.0, y0=64)
    pts = [(sx - 10, 30, sz - 8), (sx - 30, 8, sz - 30), (sx - 10, 4, sz - 70), (sx + 40, 4, sz - 110),
           (sx + 70, 6, sz - 150)]
    e.cable('primer_pla', pts, BLACKT, 2.0, gruix=9)


def roques(e):
    for (x, z, r, seed) in ((-292, 476, 44, 1), (-222, 452, 22, 2), (-330, 540, 20, 3), (-170, 470, 11, 4)):
        e.roca('primer_pla', (x, 0, z), r, STONE, 0.9, seed=seed)
    for k, (x, z) in enumerate(((-232, 460), (-180, 462), (-140, 476))):         # herba seca entre les roques
        for j in range(5):
            a = 1.2 + (j - 2) * 0.22
            e.cable('primer_pla', [(x + j * 2, 0, z), (x + j * 2 + math.cos(a) * 10, math.sin(a) * 14 + hr(k, j) * 4, z)],
                    GRASS, 2.4, gruix=0.9)


# ─── Composició ─────────────────────────────────────────────────────────────

def escena(cv, tex, nau_mode='oberta'):
    e = Escena(cv, CAM, LLUMS, ambient=AMBIENT)
    e.amo = array('H', bytes(2 * cv.w * cv.h))         # (més de 255 superfícies: l'amo de cada píxel, en 16 bits)
    fons(cv)
    zn = 300
    e.quad('terra', (-80000, 0, 20000), (80000, 0, 20000), (80000, 0, zn), (-80000, 0, zn), ramp=EARTH, lvl=_terra)
    e.claror((-80000, 0.2, 20000), (80000, 0.2, 20000), (80000, 0.2, 900), (-80000, 0.2, 900), (232, 210, 170),
             lambda s, t: 0.6 * smooth(1400, 12000, 20000 - t))           # la calitja: el fons es confon amb el cel
    # els hangars, lluny, a l'horitzó de l'esquerra (del pla)
    e.sprite('hangars', tex['hangars'].crop((0, 60, 200, 123)), (0, 62), (-2600, 0, 5200), escala_img=8.6)
    # de lluny a prop
    grua(e)
    contenidors(e, tex)
    panell(e, tex)
    bidons(e)
    tauler(e, tex)
    nau(e, tex, nau_mode)
    if nau_mode != 'sola':
        pal(e, tex)
        sortidor(e)
        roques(e)
    return e


@functools.lru_cache(maxsize=None)
def _base(nau_mode='oberta'):
    cv = Canvas(light=LIGHT)
    e = escena(cv, _textures(), nau_mode)
    cv.tint(0, 0, W - 1, RH - 1, (240, 200, 140), 0.05)                   # la calitja de pols
    for y in range(RH, H):                                                # sota la sala: negre
        for x in range(W):
            cv.flat(x, y, (0, 0, 0))
    return cv.img, e


def bg(cv):
    img, _ = _base()
    cv.img.paste(img)
    cv.P = cv.img.load()


# ─── L'enlairament (tasca 086) ──────────────────────────────────────────────
# El primer vol, amb tothom a bord: la porta tancada, la nau tus (sacsejades i bufades de fum negre dels motors) i
# s'enlaira fins a sortir per dalt, amb la pols del terra que s'aixeca. Un decorat que tapa tota la sala (`enlairament`,
# a la capa de més davant) amb dues animacions: `tus` (en bucle) i `enlaira` (es queda a l'últim fotograma).
# Es compon a partir de tres renders: el port sense nau (`buit`), la nau tancada amb el port (`tancada`, per a la
# claror i l'ombra) i la nau tancada sense res al davant (`sola`, per retallar-la sencera); el pal, el sortidor i el
# primer pla del port buit es tornen a posar al davant de la nau que puja.

_DAVANT_IDS = {'pal', 'sortidor', 'primer_pla'}


@functools.lru_cache(maxsize=None)
def _peces_vol():
    buit, eb = _base(None)
    tanc, _ = _base('tancada')
    sola, es = _base('sola')
    W_ = es.cv.w
    zb = NAU_T.zb                                                         # (l'últim dibuix de la nau: el de `sola`)
    nau = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    pn, ps = nau.load(), sola.load()
    for i, z in enumerate(zb):
        if z < 1e9:
            x, y = i % W_, i // W_
            if y < RH:
                pn[x, y] = ps[x, y][:3] + (255,)
    davant = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    pd, pb = davant.load(), buit.load()
    for i, idx in enumerate(eb.amo):
        if eb.ids[idx] in _DAVANT_IDS:
            x, y = i % W_, i // W_
            if y < RH:
                pd[x, y] = pb[x, y][:3] + (255,)
    return buit.convert('RGBA'), tanc.convert('RGBA'), nau, davant


def _fum(img, x, y, r, col, a, seed):
    """Una bufada de fum: un núvol tou de cercles, amb la vora desfeta."""
    p = img.load()
    for j in range(7):
        cx = x + (hr(seed, j) - 0.5) * r * 1.4
        cy = y + (hr(seed + 1, j) - 0.5) * r * 0.9
        rr = r * (0.45 + 0.5 * hr(seed + 2, j))
        for yy in range(int(cy - rr), int(cy + rr) + 1):
            for xx in range(int(cx - rr), int(cx + rr) + 1):
                if 0 <= xx < W and 0 <= yy < RH:
                    d = ((xx - cx) ** 2 + (yy - cy) ** 2) / (rr * rr)
                    if d < 1 and hr(xx * 7 + yy, seed) > d * 0.6:
                        o = p[xx, yy]
                        k = a * (1 - d * 0.5)
                        p[xx, yy] = (int(o[0] + (col[0] - o[0]) * k), int(o[1] + (col[1] - o[1]) * k),
                                     int(o[2] + (col[2] - o[2]) * k), 255)


def _fotograma(dx, dy, ombra, fums=(), flama=0.0, pols=0.0):
    buit, tanc, nau, davant = _peces_vol()
    if ombra >= 1:
        img = tanc.copy()
    else:
        img = Image.blend(buit, tanc, ombra) if ombra > 0 else buit.copy()
        # on hi havia la nau, el port buit (la mescla hi deixaria un fantasma)
        img.paste(buit, (0, 0), nau)
    img.alpha_composite(nau, (dx, dy))
    if flama > 0:                                                         # la flama dels broquets, quan empenyen
        for P in NAU_T.TOVERES:
            u, v = NAU_T.xy(CAM, P)
            _fum(img, u + dx, v + dy + 6, 5 + 4 * flama, (255, 190, 90), 0.9, 71)
            _fum(img, u + dx, v + dy + 3, 3 + 2 * flama, (255, 245, 200), 0.9, 72)
    for (x, y, r, col, a, s) in fums:
        _fum(img, x, y, r, col, a, s)
    if pols > 0:                                                          # la pols del terra, sota la nau
        cx, cz = nau_terra(NL / 2, 0)
        u, v = _p(cx, cz)
        for j in range(9):
            _fum(img, u + (j - 4) * (22 + 18 * pols), v + 4 - hr(5, j) * 8, 10 + 16 * pols, (214, 186, 140),
                 0.55 * min(1.0, pols * 1.5), 90 + j)
    img.alpha_composite(davant)
    return img


def enlairament(cv):
    """El decorat fix: la nau, ja tancada, abans d'engegar (el primer fotograma de `tus`)."""
    cv.img.paste(_fotograma(0, 0, 1.0))
    cv.P = cv.img.load()


def _broquets():
    return [NAU_T.xy(CAM, P) for P in NAU_T.TOVERES]


def _frames_tus():
    """Tus: tremola i escup bufades de fum negre pels motors (en bucle mentre es diu la línia)."""
    frames = []
    sac = [(0, 0), (1, 0), (-1, 1), (0, -1), (2, 0), (0, 0), (-1, 0), (1, 1), (0, 0), (-2, 0), (1, -1), (0, 0)]
    for i, (dx, dy) in enumerate(sac):
        fums = []
        for k, (u, v) in enumerate(_broquets()):
            t = (i + 4 * k) % 12                                          # una bufada cada 12 fotogrames, per motor
            if t < 6:
                fums.append((u + dx + 5 * t, v + dy - 3 * t, 6 + 4 * t, (34, 30, 28), 0.95 - 0.13 * t, 30 + k))
        frames.append(_fotograma(dx, dy, 1.0, fums))
    return frames


def _frames_enlaira():
    """S'enlaira: s'aixeca a poc a poc, amb flama i pols, i després accelera fins que surt per dalt."""
    frames = []
    n = 34
    for i in range(n):
        t = i / (n - 1)
        dy = -round(300 * t ** 2.2)
        dx = (-1) ** i if t < 0.35 else 0
        ombra = max(0.0, 1 - t * 2.2)
        fums = []
        if t < 0.5:
            for k, (u, v) in enumerate(_broquets()):
                fums.append((u - 6 - 10 * t, v + 8, 8 + 20 * t, (90, 80, 70), 0.5 * (1 - t), 40 + k))
        frames.append(_fotograma(dx, dy, ombra, fums, flama=min(1.0, t * 3) if dy > -320 else 0,
                                 pols=min(1.0, t * 2.5) * (1 - max(0.0, t - 0.7) / 0.3 * 0.6)))
    # la pols que es posa, amb el port buit
    for j in range(8):
        frames.append(_fotograma(0, -400, 0.0, pols=0.4 * (1 - j / 8)))
    return frames


PROPS = {'enlairament': enlairament}


# ─── Animacions ─────────────────────────────────────────────────────────────

def _frames_pols():
    return dust_wind_frames(_base()[0], 150, 258, n=64, step=10, k=0.55, seed=53)


def _frames_llum():
    return llum_canonada_frames(CAN_U, s=1)


def _balisa():
    return NAU.xy(CAM, NAU.LLUM_NAV)


def _frames_balisa():
    """El llum de navegació vermell, dalt del pal de proa de la Cantimplora: s'encén i s'apaga a poc a poc."""
    x, y = _balisa()
    frames = []
    for i in range(10):
        img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        k = max(0.0, math.cos(i / 10 * 2 * math.pi))
        cv = Canvas(img=img)
        col = mix((150, 30, 24), (255, 90, 60), k) if k > 0.1 else (100, 26, 22)
        for dx in (-1, 0, 1):
            cv.flat(x + dx, y, col)
            cv.flat(x + dx, y + 1, col)
        if k > 0.6:
            for dx, dy in ((-2, 0), (2, 0), (0, -1), (-3, 1), (3, 1)):
                cv.flat(x + dx, y + dy, (240, 90, 70))
        frames.append(img)
    return frames


ANIMS = {'pols': {'frames': _frames_pols, 'frameDuration': 110},
         'llum_canonada': {'frames': _frames_llum, 'frameDuration': 220},
         'balisa': {'frames': _frames_balisa, 'frameDuration': 120},
         'tus': {'frames': _frames_tus, 'frameDuration': 70, 'prop': 'enlairament'},
         'enlaira': {'frames': _frames_enlaira, 'frameDuration': 80, 'prop': 'enlairament', 'loop': False}}


# ─── Capes del davant ───────────────────────────────────────────────────────

def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _v(z):
    return HOR + CAM.f * CH / z


def _vt(P):
    """La y de pantalla d'un punt del terra (x, z)."""
    return _v(P[1])


# Els trams del buc: cadascun amb la línia base del terra que té just davant (el costat que es veu).
FRONT = [
    *[{'id': f'davant_nau{k}', 'mask': _amo(NAU.sids_tram(k)),
       'baseline': round(_vt(nau_terra((a + b) / 2, NR + 10))), 'zIndex': 20}
      for k, (a, b) in enumerate(zip(SEGS, SEGS[1:]))],
    {'id': 'davant_rampa', 'mask': _amo({'rampa'}),
     'baseline': round(_vt(nau_terra(sum(PORTA_L) / 2, RAMPA_OUT * 0.75))), 'zIndex': 20},
    {'id': 'davant_tauler', 'mask': _amo({'tauler'}), 'baseline': round(_v(TAULER[1])), 'zIndex': 20},
    {'id': 'davant_bidons', 'mask': _amo({'bidons'}), 'baseline': round(_v(BIDONS[1])), 'zIndex': 20},
    {'id': 'davant_pal', 'mask': _amo({'pal'}), 'baseline': round(_v(PAL[1])), 'zIndex': 20},
    {'id': 'davant_sortidor', 'mask': _amo({'sortidor'}), 'baseline': round(_v(SORTIDOR[1])), 'zIndex': 20},
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20,
     'props': ('enlairament',)},                   # (l'enlairament tapa tota la sala: a la capa de més davant)
]


# ─── Geometria (coordenades de sala, projectades) ─────────────────────────────

def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


def _rect(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(RH - 1, round(max(p[1] for p in pts))))


def _tauler_p(k):
    """Un punt del terra al llarg del tauler (k unitats des del mig)."""
    return _add((TAULER[0], 0, TAULER[1]), (math.cos(TAULER[2]), 0, math.sin(TAULER[2])), k)


def _cercle(cx, cz, r, n=8):
    return [_p(cx + r * math.cos(2 * math.pi * i / n), cz + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def _z_v(v):
    return CAM.f * CH / (v - HOR)


def _x_u(u, z):
    return (u - 320) * z / CAM.f


# El terra on es camina (al món): la plaça, del primer pla (sense les roques) fins als bidons i el tauler, al llarg
# del costat de la nau (sense la rampa ni les potes) i, per sota del morro, una franja per darrere de la proa.
_ZP = _z_v(256)                                                      # la vora de baix
_ZF = 1000.0                                                         # el fons
WALK_MON = ([(_x_u(1, _ZP) + 70, _ZP), (_x_u(1, 560), 560), (_x_u(1, 700), 700), (_x_u(1, _ZF), _ZF),
             (-170, _ZF), (-110, 1070), (120, 1075), (60, 1035), nau_terra(NL + 24, 50), nau_terra(NL - 20, 112), nau_terra(240, NR + 36), nau_terra(PORTA_L[1] + 8, NR + 36),
             nau_terra(PORTA_L[1] + 8, RAMPA_OUT + 8), nau_terra(PORTA_L[0] - 8, RAMPA_OUT + 8),
             nau_terra(PORTA_L[0] - 8, NR + 36), nau_terra(0, NR + 24), nau_terra(-70, 60)]
            + [(_x_u(638, z), z) for z in (590,)]
            + [(_x_u(638, _ZP), _ZP)])
_WALK = [_p(x, z) for x, z in WALK_MON]
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)
_SL = sum(PORTA_L) / 2
_RAMPA = NAU.rampa_cantons()

GEOMETRIA = {
    'things': {
        'cami_granja': {'rect': (0, _p(*CAMI[1])[1] - 30, 46, 258), 'walk': _p(_x_u(14, 620), 620)},
        'rampa': {'rect': _rect(NAU.buc(PORTA_L[0] - 6, PORTA_T[1] + 0.06), NAU.buc(PORTA_L[1] + 6, PORTA_T[1] + 0.06),
                                *_RAMPA),
                  'walk': _p(*nau_terra(_SL, RAMPA_OUT + 24))},
        'tauler': {'rect': _rect(*[_up(_tauler_p(k), y) for y in (0, 132) for k in (-58, 58)]),
                   'walk': _p(TAULER[0] + 20, TAULER[1] - 70)},
        'panell_preu': {'rect': _rect(*[_add((PANELL[0], y, PANELL[1]), (math.cos(-0.35), 0, math.sin(-0.35)), k)
                                        for y in (0, 114) for k in (-64, 64)]),
                        'walk': _p(PANELL[0] + 40, 960)},
        'canonada': {'rect': (CAN_U - 7, 0, CAN_U + 7, HOR - 1), 'walk': _p(-60, 900)},
    },
    'spawns': {'iri': _p(-150, 640), 'vet': _p(-260, 600)},
    'walkable': _WALK,
    # (els pals del tauler i del rètol són prims: un forat d'un parell de píxels d'alt espatlla el camí)
    'forats': [_cercle(BIDONS[0], BIDONS[1], 34), _cercle(SORTIDOR[0], SORTIDOR[1], 30)],
    # L'ombra de contacte: el sol és a dalt a la dreta, l'ombra cau cap a l'esquerra (com les dels objectes).
    # La càmera aixafa el terra: 130 d'alçada a ≈550 de fons (on es camina) → 0,24.
    'floorSquash': 0.25,
    'characterShadow': {'enabled': True, 'color': '#2a1a10', 'alpha': 0.42, 'squash': 0.27, 'core': 0.6,
                        'light': {'x': -1, 'y': 0.12, 'direction': True, 'stretch': 0.7}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round((_V_FONS - 2 - HOR) / CH, 3),
                 'scaleBottom': round((_V_PROP + 2 - HOR) / CH, 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    # La llum de la sala sobre els personatges (characterLights del motor): el port al ple sol del desert: neutra i
    # una mica càlida, el sol a dalt a la dreta.
    'characterLights': {
        'ambient': '#f6ead8',
        'lights': [
            {'x': W + 200, 'y': -300, 'radius': 1000, 'color': '#fff2d8', 'intensity': 0.15},  # el sol: una mica més de llum, i càlida
        ],
    },
}
