"""
La cuina (acte 2, de nit; la Vet, amb la Iri). Art definitiu, a 1×.

La cuina del monestir, monumental, vista de biaix cap a la cantonada del fons a l'esquerra i una mica des de dalt:
  - a la paret del fons, la **llar de foc** gegant: la boca de pedra, la campana ennegrida que puja fins al sostre, la
    llosa de la llar, la llenya, el **foc** (animació, `foc`) i l'olla que hi penja de la cadena. Tota la llum de la
    sala ve d'aquí: taronja, i les ombres llargues que fugen cap a la dreta i cap a nosaltres;
  - a la dreta de la llar, la biga amb les **olles** penjades (coure i ferro), que fan ombra a la paret;
  - a la cantonada, contra la paret de l'esquerra, la **pila d'olles** de terrissa i coure, a prop d'on és la Iri;
  - al mig, la **taula** llarga, girada, amb la **gerra** de vi i la **copa** (davant en Sunifred, que és al cap de la
    taula: la taula li tapa les cames), i el **banc** al davant (capes del davant amb la seva línia base);
  - primer pla: el pilar de la dreta i la pila de llenya de baix a l'esquerra, a contrallum.
Decorats: `olles_caigudes` (la pila per terra, escampada) i `sunifred_dorm` (la copa bolcada i el vi vessat: en
Sunifred adormit l'ha de fer el seu full, amb una animació).
"""
import functools
import math

from PIL import Image

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)

from hd.pix import Canvas, Light
from hd640.rooms.nit_comu import (W, BOTTOM, PEDRA, LLOSA, FUSTA, FERRO, COURE, BRASA, CENDRA, FANG, VI, CERA,
                                  fbm, hr, carreus, lloses, veta, flama, hud_negre, sense, _diff,
                                  llum_personatge, rect_de, ombra_terra, marca)
from hd640.tres_d import Camera, Escena, Llum

# ─── La càmera i el món ──────────────────────────────────────────────────────
EYE_H, F, CY, YAW = 180, 380, 30, -0.18
CAM = Camera(pos=(0, EYE_H, 0), yaw=YAW, pitch=0.0, f=F, centre=(320, CY))

ZB = 520                                            # la paret del fons
XL = -330                                           # la paret de l'esquerra
WALL_H = 460
LLAR = (-292, -112, 118, 44)                         # la boca: x0, x1, alçada, fondària
MANTELL = 54                                        # quant surt la campana de la paret
TAULA = (30, 440, 230, 58, 44, -0.16)               # cx, cz, llarg, ample, alt, angle
BANC = (20, 384, 180, 20, 26, -0.16)                # (davant la taula)
BIGA = (20, 196, 150)                              # la biga de les olles: x0, x1, y
PILA = (-300, 470)                                  # la pila d'olles: x, z (a terra, a la cantonada)
PILAR = (150, 184, 262, 292)                        # el pilar del primer pla: x0, x1, z0, z1

FOC_POS = ((LLAR[0] + LLAR[1]) / 2, 30, ZB + 20)
LIGHT = Light(ambient=0.0, vignette=(70, 30), floor_fade=None)
LIGHT.width = W
LLUMS = [Llum((FOC_POS[0], 110, ZB - 40), 820, 7.0, power=1.2),
         Llum((FOC_POS[0], 30, ZB + 6), 200, 3.0, power=1.6)]          # dins la boca
AMBIENT = -2.6


def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


def _girat(cx, cz, a):
    c, s = math.cos(a), math.sin(a)
    return lambda lx, lz, y=0.0: (cx + lx * c - lz * s, y, cz + lx * s + lz * c)


# ─── Parets i terra ─────────────────────────────────────────────────────────

def _fum(x, y):
    """La paret ennegrida pel fum, per sobre de la llar."""
    x0, x1, h, _ = LLAR
    cx = (x0 + x1) / 2
    if y < h:
        return 0.0
    dx = abs(x - cx) / ((x1 - x0) / 2 + 20 + (y - h) * 0.2)
    return max(0.0, 1 - dx) * min(1.0, (y - h) / 40) * 2.2


def terra(e):
    e.quad('terra', (XL, 0, ZB), (700, 0, ZB), (700, 0, -50), (XL, 0, -50), ramp=LLOSA,
           lvl=lambda s, t, P: lloses(P[0], P[2], mida=(46, 40), seed=17, base=2.2))


def parets(e):
    x0, x1, h, d = LLAR

    def fons_lvl(s, t, P):
        return carreus(P[0] + 600, WALL_H - P[1], alt=34, ample=(48, 78), seed=7, base=2.4) - _fum(P[0], P[1])

    def forma(s, t):
        x, y = s + XL, WALL_H - t
        return not (x0 <= x <= x1 and y <= h)
    e.quad('paret', (XL, WALL_H, ZB), (700, WALL_H, ZB), (700, 0, ZB), (XL, 0, ZB), ramp=PEDRA, lvl=fons_lvl,
           forma=forma)
    e.quad('paret_esq', (XL, WALL_H, -50), (XL, WALL_H, ZB), (XL, 0, ZB), (XL, 0, -50), ramp=PEDRA,
           lvl=lambda s, t, P: carreus(s + 200, t, alt=34, ample=(48, 78), seed=8, base=2.0), dues_cares=True)


def llar(e):
    """La boca de la llar (endins: el fons, els costats, la llosa), la llenya i les brases; la campana a sobre."""
    x0, x1, h, d = LLAR
    zf = ZB + d
    e.quad('llar', (x0, h, zf), (x1, h, zf), (x1, 0, zf), (x0, 0, zf), ramp=PEDRA,
           lvl=lambda s, t, P: carreus(s, t, alt=22, ample=(26, 40), seed=9, base=0.8) - max(0.0, 1.6 - t / 30))
    e.quad('llar', (x0, h, ZB), (x0, h, zf), (x0, 0, zf), (x0, 0, ZB), ramp=PEDRA,
           lvl=lambda s, t, P: carreus(s, t, alt=22, ample=(20, 30), seed=10, base=1.2))
    e.quad('llar', (x1, h, zf), (x1, h, ZB), (x1, 0, ZB), (x1, 0, zf), ramp=PEDRA,
           lvl=lambda s, t, P: carreus(s, t, alt=22, ample=(20, 30), seed=11, base=1.0))
    e.quad('llar', (x0, h, zf), (x1, h, zf), (x1, h, ZB), (x0, h, ZB), ramp=CENDRA, lvl=0.4, dues_cares=True)
    # la llosa de la llar, una mica alçada, que surt cap a la cuina
    e.caixa('llar', x0 - 30, x1 + 30, 0, 8, ZB - 40, zf, PEDRA, 3.2,
            cares={'dalt': {'ramp': PEDRA, 'lvl': lambda s, t, P: lloses(P[0], P[2], mida=(40, 30), seed=5, base=2.0)
                            - max(0.0, 1.6 - abs(P[0] - FOC_POS[0]) / 40) * (1.0 if P[2] > ZB else 0)}})
    # els brancals de la llar, que surten de la paret (la cara de dins, encesa pel foc)
    for bx0, bx1 in ((x0 - 30, x0), (x1, x1 + 30)):
        e.caixa('llar', bx0, bx1, 8, h, ZB - MANTELL, ZB, PEDRA, 2.6,
                cares={n: {'ramp': PEDRA, 'lvl': (lambda s, t, P, sd=hash(n) % 7: carreus(s, t, alt=24, ample=(30, 40),
                                                                                       seed=40 + sd, base=2.6))}
                       for n in ('davant', 'esquerra', 'dreta')})
    # la campana: el mantell (una llinda grossa) i la campana que puja inclinada fins a la paret
    m = MANTELL
    # la llinda: una biga de roure grossa, damunt dels brancals
    e.caixa('campana', x0 - 34, x1 + 34, h, h + 16, ZB - m - 4, ZB, FUSTA, 3.0,
            cares={'davant': {'ramp': FUSTA, 'lvl': lambda s, t, P: veta(s, t, seed=61, base=3.2) + (1.2 if t > 13 else 0)},
                   'sota': {'ramp': FUSTA, 'lvl': 4.6}, 'dalt': {'ramp': FUSTA, 'lvl': 2.2},
                   'dreta': {'ramp': FUSTA, 'lvl': 2.2}, 'esquerra': {'ramp': FUSTA, 'lvl': 3.0}})
    top = WALL_H
    hc = h + 16
    e.quad('campana', (x0 + 6, top, ZB), (x1 - 6, top, ZB), (x1 + 30, hc, ZB - m), (x0 - 30, hc, ZB - m),
           ramp=PEDRA, lvl=lambda s, t, P: carreus(s, t, alt=30, ample=(40, 60), seed=13, base=3.0)
           - _fum(P[0], P[1] + 30) * 0.3 - max(0.0, (P[1] - hc) / 160))
    e.quad('campana', (x1 + 30, hc, ZB - m), (x1 - 6, top, ZB), (x1 - 6, top, ZB), (x1 + 30, hc, ZB),
           ramp=PEDRA, lvl=lambda s, t, P: carreus(s, t, alt=30, seed=14, base=1.8), dues_cares=True)


def llenya(cv, e):
    """La llenya i les brases dins la llar, i l'olla que hi penja de la cadena."""
    x0, x1, h, d = LLAR
    cx = (x0 + x1) / 2
    for k, (lx, lz, ang) in enumerate(((-24, 10, 0.2), (18, 14, -0.3), (-4, 4, 0.05))):
        a = (cx + lx - 26 * math.cos(ang), 11, ZB + 18 + lz - 26 * math.sin(ang))
        b = (cx + lx + 26 * math.cos(ang), 11, ZB + 18 + lz + 26 * math.sin(ang))
        e.cable('llenya', [a, b], FUSTA, 1.6 + k * 0.3, gruix=7.0)
    u, v, _ = CAM.projecta((cx, 9, ZB + 20))
    s = CAM.escala((cx, 0, ZB + 20))
    for i in range(int(-36 * s), int(36 * s)):
        for j in range(int(-6 * s), int(4 * s)):
            if (i / (36 * s)) ** 2 + (j / (6 * s)) ** 2 < 1:
                cv.put(u + i, v + j, BRASA, 4.4 + (hr(int(u + i), int(v + j), 4) - 0.5) * 2.4 - abs(j) * 0.2, lit=0)
    # la cadena i l'olla de ferro
    ou, ov, _ = CAM.projecta((cx + 6, 40, ZB + 22))
    tu, tv, _ = CAM.projecta((cx + 6, h - 2, ZB + 22))
    for y in range(int(tv), int(ov - 14 * s)):
        if y % 3:
            cv.put(ou + (1 if y % 6 < 3 else 0), y, FERRO, 3.0, lit=0)
    r = 17 * s
    cv.disc(ou, ov, r, r * 0.8, FERRO, lambda nx, ny: 2.2 - nx * 1.0 + ny * 0.2 + (0.0 if ny > -0.3 else 0.6), lit=0)
    cv.disc(ou, ov - r * 0.62, r * 0.9, r * 0.22, FERRO, 0.8, lit=0)
    cv.disc(ou, ov - r * 0.62, r * 0.7, r * 0.15, CENDRA, 3.2, lit=0)             # el brou, amb el reflex
    for i in range(-int(r), int(r) + 1):                                          # el foc que la llepa per sota
        cv.put(ou + i, ov + r * 0.8 * math.sqrt(max(0.0, 1 - (i / r) ** 2)), BRASA, 5.0, lit=0)


def _calidesa(cv, e):
    """El to taronja del foc sobre tot el que és a prop (en pantalla, aixafat: s'escampa més pel terra)."""
    u, v, _ = CAM.projecta((FOC_POS[0], 30, ZB + 10))

    def k(x, y):
        d = math.hypot(x - u, (y - v) * (1.5 if y < v else 0.8)) / 460
        return 0.32 * max(0.0, 1 - d) ** 1.6
    davant = e._idx_de('davant')
    cv.tint(0, 0, W - 1, BOTTOM, (255, 120, 40), k, mask=lambda x, y: 0.25 if e.amo[y * W + x] == davant else 1.0)


def _foc(cv, fase):
    """Les flames de la llar (en pantalla): sis llengües que bateguen, i el resplendor."""
    x0, x1, h, d = LLAR
    cx = (x0 + x1) / 2
    s = CAM.escala((cx, 0, ZB + 20))
    u, v, _ = CAM.projecta((cx, 10, ZB + 18))
    for k, (dx, hh, ww) in enumerate(((-34, 36, 14), (-22, 56, 18), (-8, 70, 21), (6, 62, 19), (20, 48, 16),
                                      (32, 30, 12), (-42, 20, 9))):
        flama(cv, u + dx * s, v + 2, hh * s, ww * s, (fase + k * 0.17) % 1.0, seed=k * 1.3)
    for i in range(6):
        f = (fase * 2 + hr(i, 1, 3)) % 1.0
        if f < 0.6:
            gx = u + (hr(i, 2, 4) - 0.5) * 50 * s + math.sin(f * 8 + i) * 3
            gy = v - 40 * s - f * 60 * s
            cv.put(gx, gy, BRASA, 6.0 - f * 4, lit=0)
    bat = 1 + 0.06 * math.sin(2 * math.pi * fase * 3)
    cv.glow(u, v - 20 * s, 80 * s * bat, (255, 170, 80), 0.5)


def olles_penjades(cv, e):
    """La biga de fusta amb ganxos, i les olles de coure i de ferro que hi pengen (fan ombra a la paret)."""
    x0, x1, y = BIGA
    e.caixa('biga', x0, x1, y, y + 8, ZB - 14, ZB, FUSTA, 2.8,
            cares={'davant': {'ramp': FUSTA, 'lvl': lambda s, t, P: veta(s, t, seed=41, base=2.6)},
                   'sota': {'ramp': FUSTA, 'lvl': 1.4}, 'dalt': {'ramp': FUSTA, 'lvl': 3.6}})
    for k, (dx, r, ramp, prof) in enumerate(((12, 13, COURE, 15), (44, 10, FERRO, 12), (76, 15, COURE, 18),
                                             (110, 11, COURE, 13), (140, 9, FERRO, 10), (166, 12, COURE, 14))):
        x = x0 + dx
        if x > x1:
            continue
        hook = CAM.projecta((x, y, ZB - 8))
        s = CAM.escala((x, 0, ZB - 8))
        cy_ = hook[1] + (10 + r) * s
        # l'ombra a la paret: més amunt i a la dreta (el foc és avall a l'esquerra)
        cv.darken(hook[0] + 4 * s, cy_ - r * s - 6, hook[0] + 4 * s + r * 2.4 * s, cy_ - r * 0.4 * s,
                  lambda xx, yy, cx=hook[0] + 4 * s + r * 1.2 * s, cy2=cy_ - r * 0.7 * s, rr=r * s:
                  0.7 if ((xx - cx) / (rr * 1.2)) ** 2 + ((yy - cy2) / (rr * 0.8)) ** 2 < 1 else 0)
        for j in range(int(hook[1]), int(cy_ - r * s * 0.6)):
            cv.put(hook[0], j, FERRO, 3.4, lit=0)
        lit = lambda nx, ny, ramp=ramp: 3.6 - nx * 1.6 - ny * 1.0 + (1.6 if (nx + 0.45) ** 2 + (ny - 0.1) ** 2 < 0.05 else 0)
        cv.disc(hook[0], cy_, r * s, prof * s * 0.75, ramp, lit, lit=0)
        cv.disc(hook[0], cy_ - prof * s * 0.62, r * s * 0.95, r * s * 0.22, ramp, 2.0, lit=0)
        if k % 2 == 0:                                                              # el mànec
            for i in range(int(r * s), int(r * s + 8 * s)):
                cv.put(hook[0] - i, cy_ - prof * s * 0.5, ramp, 2.8, lit=0)


def pila(cv, e, caigudes):
    """La pila d'olles i cassoles de terrissa i coure, a la cantonada; o, caigudes, escampades per terra."""
    px, pz = PILA
    if caigudes:
        peces = ((-40, -34, 10, FANG, 0.3), (-4, -62, 9, COURE, 1.2), (30, -30, 12, FANG, -0.4), (20, -92, 8, FANG, 0.9),
                 (-30, -84, 7, COURE, 0.2), (50, -66, 10, FANG, -1.0), (4, -10, 13, FANG, 0.4))
        for dx, dz, r, ramp, a in sorted(peces, key=lambda p: -p[1]):
            u, v, _ = CAM.projecta((px + dx, 0, pz + dz))
            s = CAM.escala((px + dx, 0, pz + dz))
            cv.darken(u - r * s - 2, v - 2, u + r * s + 4, v + 4 * s, lambda x, y: 0.5)
            # una olla tombada: una el·lipse allargada amb la boca fosca
            cv.disc(u, v - r * s * 0.55, r * s * 1.1, r * s * 0.6, ramp,
                    lambda nx, ny: 3.4 - ny * 1.2 - nx * 0.6, lit=0)
            cv.disc(u + math.cos(a) * r * s * 0.9, v - r * s * 0.55, r * s * 0.3, r * s * 0.5, ramp, 0.6, lit=0)
        for k in range(14):                                                         # trossos
            u, v, _ = CAM.projecta((px + (hr(k, 1, 9) - 0.3) * 120, 0, pz - hr(k, 2, 9) * 110))
            cv.put(u, v, FANG, 3.2, lit=0)
            cv.put(u + 1, v, FANG, 2.2, lit=0)
        return
    u, v, _ = CAM.projecta((px, 0, pz))
    s = CAM.escala((px, 0, pz))
    cv.darken(u - 30 * s, v - 4, u + 34 * s, v + 6, lambda x, y: 0.6)
    # de baix a dalt: cassoles grosses, olles, i una olleta a dalt de tot, una mica tort
    peces = ((0, 0, 30, 14, FANG), (-2, 14, 26, 16, FANG), (2, 30, 22, 13, COURE), (0, 43, 18, 15, FANG),
             (-3, 58, 15, 11, COURE), (1, 69, 12, 12, FANG), (4, 81, 8, 8, COURE))
    for dx, y, r, hh, ramp in peces:
        cyy = v - y * s - hh * s / 2
        cv.disc(u + dx * s, cyy, r * s, hh * s / 2 + 1, ramp,
                lambda nx, ny: 3.4 - nx * 1.4 - ny * 0.8 + (1.4 if -0.7 < nx < -0.45 else 0), lit=0)
        cv.disc(u + dx * s, cyy - hh * s / 2 + 1, r * s * 0.9, max(1.2, r * s * 0.18), ramp, 1.6, lit=0)


def taula(cv, e, estat):
    cx, cz, ll, am, h, a = TAULA
    g = _girat(cx, cz, a)
    ombra_terra(e, (FOC_POS[0], 96, ZB - 30), [g(-ll / 2, am / 2, h), g(ll / 2, am / 2, h), g(ll / 2, -am / 2, h),
                                               g(-ll / 2, -am / 2, h)], k=0.7, vora=0.2)
    for lx, lz in ((-ll / 2 + 16, -am / 2 + 8), (ll / 2 - 16, -am / 2 + 8), (-ll / 2 + 16, am / 2 - 8),
                   (ll / 2 - 16, am / 2 - 8)):
        X, _, Z = g(lx, lz)
        e.caixa_girada('taula', X, Z, 8, 8, h - 5, a, FUSTA, 2.6)
    e.caixa_girada('taula', cx, cz, ll, am, 5, a, FUSTA, 3.0, y0=h - 5,
                   cares={'dalt': {'ramp': FUSTA, 'lvl': lambda s, t, P: veta(s, t, seed=51, base=3.4)
                                   - (1.0 if int(t) % 20 == 0 else 0)},
                          'davant': {'ramp': FUSTA, 'lvl': lambda s, t, P: veta(s, t, seed=52, base=2.6)}})
    # el banc, al davant
    bx, bz, bl, ba, bh, ba_ = BANC
    gb = _girat(bx, bz, ba_)
    ombra_terra(e, (FOC_POS[0], 96, ZB - 30), [gb(-bl / 2, ba / 2, bh), gb(bl / 2, ba / 2, bh), gb(bl / 2, -ba / 2, bh),
                                               gb(-bl / 2, -ba / 2, bh)], k=0.5, vora=0.2)
    for lx in (-bl / 2 + 12, bl / 2 - 12):
        X, _, Z = gb(lx, 0)
        e.caixa_girada('banc', X, Z, 6, ba - 4, bh - 4, ba_, FUSTA, 2.4)
    e.caixa_girada('banc', bx, bz, bl, ba, 4, ba_, FUSTA, 3.0, y0=bh - 4,
                   cares={'dalt': {'ramp': FUSTA, 'lvl': lambda s, t, P: veta(s, t, seed=53, base=3.6)}})
    # damunt la taula: pa, una escudella, la gerra i la copa (davant en Sunifred, al cap de la dreta)
    def obj(lx, lz):
        X, Y, Z = g(lx, lz, h)
        return CAM.projecta((X, Y, Z))[:2], CAM.escala((X, 0, Z))
    marca(e, 'taula', lambda: _damunt(cv, obj, estat))


def _damunt(cv, obj, estat):
    (u, v), s = obj(-60, 4)
    cv.disc(u, v - 3 * s, 12 * s, 5 * s, FANG, lambda nx, ny: 4.6 - ny * 1.4 - nx * 0.6, lit=0)         # el pa
    for i in range(3):
        cv.line(u - 6 * s + i * 5 * s, v - 6 * s, u - 3 * s + i * 5 * s, v - 2 * s, FANG, 2.6, lit=0)
    (u, v), s = obj(-20, -8)
    cv.disc(u, v - 2 * s, 9 * s, 3.5 * s, FANG, lambda nx, ny: 3.8 - nx * 0.8, lit=0)                    # l'escudella
    cv.disc(u, v - 3.5 * s, 7 * s, 2 * s, FANG, 1.4, lit=0)
    gerra(cv, *obj(58, 6))
    if 'dorm' in estat:
        copa_bolcada(cv, *obj(96, -4))
    else:
        copa(cv, *obj(96, -4))


def gerra(cv, uv, s):
    """La gerra de vi, de terrissa vidriada."""
    u, v = uv
    hh = 30 * s
    for j in range(int(hh)):
        t = j / hh
        rr = (7 + 5 * math.sin(math.pi * min(1.0, t * 1.15))) * s if t < 0.8 else 4.2 * s
        for i in range(int(-rr), int(rr) + 1):
            nx = i / max(1, rr)
            cv.put(u + i, v - j, FANG, 3.8 - nx * 1.8 + (1.6 if -0.62 < nx < -0.4 and 0.2 < t < 0.6 else 0), lit=0)
    cv.disc(u, v - hh, 5 * s, 1.6 * s, FANG, 1.2, lit=0)
    for j in range(int(8 * s)):                                                     # la nansa
        cv.put(u + 9 * s + math.sin(j / (8 * s) * math.pi) * 3 * s, v - hh * 0.5 - j, FANG, 2.6, lit=0)


def copa(cv, uv, s):
    """La copa de peu (d'estany), dreta, amb el vi fosc a dins."""
    u, v = uv
    cv.disc(u, v - 1, 5 * s, 1.6 * s, FERRO, 4.4, lit=0)
    for j in range(int(8 * s)):
        cv.put(u, v - 2 - j, FERRO, 5.0, lit=0)
    top = v - 2 - 8 * s
    for j in range(int(9 * s)):
        rr = (3 + 4 * j / (9 * s)) * s
        for i in range(int(-rr), int(rr) + 1):
            cv.put(u + i, top - j, FERRO, 5.0 - i / max(1, rr) * 1.8, lit=0)
    cv.disc(u, top - 9 * s, 6.5 * s, 1.6 * s, VI, 3.0, lit=0)


def copa_bolcada(cv, uv, s):
    """La copa tombada damunt la taula i el vi vessat, que fa un bassal fosc i regalima pel cantell."""
    u, v = uv
    cv.disc(u + 4 * s, v + 1, 20 * s, 5 * s, VI, lambda nx, ny: 2.2 + (1.4 if nx < -0.4 and ny < -0.2 else 0), lit=0)
    for j in range(int(10 * s)):
        rr = (2 + 3 * j / (10 * s)) * s
        cv.line(u - 6 * s + j, v - rr, u - 6 * s + j, v + rr * 0.4, [(30, 28, 30), (70, 64, 62), (140, 132, 120),
                                                                      (200, 192, 176)], 2.4 - j * 0.05, lit=0)
    cv.disc(u - 7 * s, v - 1, 1.6 * s, 3 * s, [(30, 28, 30), (90, 84, 80), (160, 150, 140)], 1.6, lit=0)
    for k in range(3):
        cv.line(u + 14 * s + k * 3, v + 4 * s, u + 14 * s + k * 3, v + (10 + k * 3) * s, VI, 2.2, lit=0)


def primer_pla(e, cv):
    """El pilar de pedra de la dreta (tallat per la vora) i la pila de llenya de baix a l'esquerra."""
    x0, x1, z0, z1 = PILAR
    e.caixa('davant', x0, x1, 0, WALL_H, z0, z1, PEDRA, 1.8,
            cares={'davant': {'ramp': PEDRA, 'lvl': lambda s, t, P: carreus(s, t, alt=36, ample=(40, 40), seed=21,
                                                                            base=1.6)},
                   'esquerra': {'ramp': PEDRA, 'lvl': lambda s, t, P: carreus(s, t, alt=36, ample=(36, 36), seed=22,
                                                                              base=2.6)}})
    # la llenya: troncs apilats, vistos de cap (cercles amb anelles) i de costat
    marca(e, 'davant', lambda: _llenya_davant(cv, e))


def _llenya_davant(cv, e):
    for k, (x, y, z) in enumerate(((-210, 8, 250), (-190, 8, 250), (-170, 8, 250), (-200, 24, 250), (-180, 24, 250),
                                   (-190, 40, 250), (-226, 8, 250))):
        e.cable('davant', [(x, y, z), (x - 4, y, z + 70)], FUSTA, 2.0 + hr(k, 3, 3), gruix=16.0)
        u, v, _ = CAM.projecta((x, y, z))
        s = CAM.escala((x, 0, z))
        cv.disc(u, v, 8 * s, 8 * s, FUSTA, lambda nx, ny: 4.2 + (0.8 if int(math.hypot(nx, ny) * 4) % 2 else 0)
                - math.hypot(nx, ny) * 1.4, lit=0)


# ─── Composició ────────────────────────────────────────────────────────────

def escena(cv, estat):
    e = Escena(cv, CAM, LLUMS, ambient=AMBIENT)
    terra(e)
    parets(e)
    llar(e)
    llenya(cv, e)
    # la foscor dels racons: la cantonada del fons a l'esquerra (darrere la pila) i la dreta, lluny del foc
    e.foscor('ombra', (XL, 0.2, ZB), (-150, 0.2, ZB), (-150, 0.2, 200), (XL, 0.2, 200),
             lambda s, t: 0.35 * max(0.0, 1 - s / 150))
    olles_penjades(cv, e)
    pila(cv, e, 'caigudes' in estat)
    taula(cv, e, estat)
    primer_pla(e, cv)
    e.silueta({'davant'}, k=0.55, col=(10, 5, 4))
    return e


@functools.lru_cache(maxsize=None)
def _render(estat=frozenset(), fase=0.0, foc=True):
    cv = Canvas(light=LIGHT)
    e = escena(cv, estat)
    _calidesa(cv, e)
    if foc:
        _foc(cv, fase)
    hud_negre(cv)
    for y in range(BOTTOM + 1, cv.h):
        for x in range(W):
            e.amo[y * W + x] = 0
    return cv.img, e


def _base():
    return _render(frozenset())[0]


def bg(cv):
    cv.img.paste(_base())
    cv.P = cv.img.load()


@functools.lru_cache(maxsize=None)
def _davant_img():
    img, e = _render(frozenset())
    out = Image.new('RGBA', img.size, (0, 0, 0, 0))
    src, dst = img.load(), out.load()
    ids = {i for i, s in enumerate(e.ids) if s == 'davant'}
    for y in range(BOTTOM + 1):
        for x in range(W):
            if e.amo[y * W + x] in ids:
                dst[x, y] = src[x, y]
    return out


def _decorat(estat):
    def draw(cv):
        img = _render(frozenset(estat))[0]
        cv.img.alpha_composite(sense(_diff(img, _base()), _davant_img()))
        cv.P = cv.img.load()
    return draw


PROPS = {
    'olles_caigudes': _decorat(('caigudes',)),
    'sunifred_dorm': _decorat(('dorm',)),
}


# ─── Animacions ─────────────────────────────────────────────────────────────

def _frames_foc():
    """El foc de la llar, en bucle (16 fotogrames): les flames, les guspires i el resplendor."""
    base = _base()
    net = _render(frozenset(), 0.0, False)[0]
    x0, x1, h, _ = LLAR
    a = CAM.projecta((x0 - 30, h + 90, ZB))
    b = CAM.projecta((x1 + 30, 0, ZB - 40))
    box = (int(a[0]) - 10, max(0, int(a[1]) - 10), int(b[0]) + 10, int(b[1]) + 10)
    out = []
    n = 16
    for i in range(n):
        cv = Canvas(light=LIGHT, img=base.copy())
        cv.img.paste(net.crop(box), box[:2])
        cv.P = cv.img.load()
        _foc(cv, i / n)
        out.append(sense(_diff(cv.img, base), _davant_img()))
    return out


ANIMS = {'foc': {'frames': _frames_foc, 'frameDuration': 85}}


# ─── Capes del davant ─────────────────────────────────────────────────────

def _amo(ids):
    def mask(x, y):
        _, e = _render(frozenset())
        return e.ids[e.amo[y * W + x]] in ids
    return mask


def _baseline(cx, cz, ll, am, a):
    g = _girat(cx, cz, a)
    # la línia base d'un moble girat: el cantó de davant que queda més al fons
    return max(_p(*[g(lx, -am / 2)[k] for k in (0, 2)])[1] for lx in (-ll / 2, ll / 2)) - 0


FRONT = [
    {'id': 'davant_banc', 'mask': _amo({'banc'}), 'baseline': _baseline(*BANC[:4], BANC[5]), 'zIndex': 20},
    {'id': 'davant_taula', 'mask': _amo({'taula'}), 'baseline': _baseline(*TAULA[:4], TAULA[5]), 'zIndex': 20,
     'variants': ('sunifred_dorm',)},
    {'id': 'davant', 'mask': _amo({'davant'}), 'baseline': 999, 'zIndex': 20},
]


# ─── Geometria (coordenades de sala) ─────────────────────────────────────────

def _escala_v(v):
    return round((v - CY) / EYE_H, 3)


def _sota(cx, cz, ll, am, a, marge=8):
    g = _girat(cx, cz, a)
    return [_p(*[g(lx, lz)[k] for k in (0, 2)]) for lx, lz in ((-ll / 2 - marge, -am / 2 - marge),
                                                                 (ll / 2 + marge, -am / 2 - marge),
                                                                 (ll / 2 + marge, am / 2 + marge),
                                                                 (-ll / 2 - marge, am / 2 + marge))]


def _geometria():
    x0, x1, h, d = LLAR
    llar_r = rect_de(*(CAM.projecta(P)[:2] for P in ((x0 - 18, h + 120, ZB), (x1 + 18, 0, ZB - 26))))
    bx0, bx1, by = BIGA
    olles_r = rect_de(*(CAM.projecta(P)[:2] for P in ((bx0, by + 10, ZB), (bx1, by - 44, ZB))), pad=2)
    px, pz = PILA
    pu, pv = _p(px, pz)
    ps = CAM.escala((px, 0, pz))
    pila_r = (round(pu - 32 * ps), round(pv - 92 * ps), round(pu + 32 * ps), pv + 4)
    cx, cz, ll, am, hh, a = TAULA
    g = _girat(cx, cz, a)
    corners = [CAM.projecta(g(lx, lz, y))[:2] for lx in (-ll / 2, ll / 2) for lz in (-am / 2, am / 2) for y in (0, hh)]
    taula_r = rect_de(*corners)

    def obj_r(lx, lz, w_, hh_):
        X, Y, Z = g(lx, lz, hh)
        u, v, _ = CAM.projecta((X, Y, Z))
        s = CAM.escala((X, 0, Z))
        return (round(u - w_ * s), round(v - hh_ * s), round(u + w_ * s), round(v + 3))
    bx, bz, bl, ba, bh, ba_ = BANC
    gb = _girat(bx, bz, ba_)
    banc_r = rect_de(*(CAM.projecta(gb(lx, lz, y))[:2] for lx in (-bl / 2, bl / 2) for lz in (-ba / 2, ba / 2)
                       for y in (0, bh)))
    # Sunifred: al cap de la taula (la dreta), darrere el cantell, perquè la taula li tapi les cames
    sun = g(ll / 2 - 34, am / 2 + 14)
    things = {
        'llar_foc': {'rect': llar_r, 'walk': _p((x0 + x1) / 2 + 30, ZB - 64)},
        'olles': {'rect': olles_r, 'walk': _p((bx0 + bx1) / 2, ZB - 50)},
        'pila_olles': {'rect': pila_r, 'walk': _p(px + 44, pz - 40)},
        'taula': {'rect': taula_r, 'walk': _p(*[g(-30, -am / 2 - 70)[k] for k in (0, 2)])},
        'gerra': {'rect': obj_r(58, 6, 12, 34), 'walk': _p(*[g(50, -am / 2 - 70)[k] for k in (0, 2)])},
        'copa': {'rect': obj_r(96, -4, 9, 22), 'walk': _p(*[g(96, -am / 2 - 70)[k] for k in (0, 2)])},
        'banc': {'rect': banc_r, 'walk': _p(*[gb(-40, -ba / 2 - 30)[k] for k in (0, 2)])},
    }
    # el terra on es camina: de la llosa de la llar i la pila (al fons) fins on la Vet fa ≈1,2; a la dreta, fins al
    # pilar del primer pla
    walk = [_p(XL + 30, ZB - 30), _p(x0 - 10, ZB - 34), _p(x1 + 10, ZB - 34), _p(150, ZB - 26), _p(140, 300),
            (W - 1, 246), (40, 246), _p(XL + 20, 300)]
    walk = [(max(0, min(W - 1, u)), min(246, v)) for u, v in walk]
    vs = [v for _, v in walk]
    forats = [_sota(cx, cz, ll, am, a, marge=6), _sota(bx, bz, bl, ba, ba_, marge=4),
              [_p(px + 30 * math.cos(k * math.pi / 4), pz + 22 * math.sin(k * math.pi / 4)) for k in range(8)]]
    lights = [llum_personatge(CAM, (FOC_POS[0], 40, ZB - 10), 520, (255, 150, 70), 0.95),
              llum_personatge(CAM, (FOC_POS[0], 40, ZB - 10), 200, (255, 200, 120), 0.4)]
    return {
        'things': things,
        # la Vet ve de l'esquerra; la Iri (disfressada), al costat de la llar, a prop de la pila; en Sunifred al cap de
        # la taula
        'spawns': {'vet': _p(-90, 330), 'iri': _p(-222, 430), 'sunifred': _p(sun[0], sun[2])},
        'walkable': walk,
        'forats': forats,
        'floorSquash': 0.42,
        'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                     'scaleTop': _escala_v(min(vs) - 2), 'scaleBottom': _escala_v(max(vs) + 2),
                     'points': [(0, min(vs) - 2), (W - 1, min(vs) - 2), (W - 1, max(vs) + 2), (0, max(vs) + 2)]}],
        # L'ombra de contacte: tota la llum ve del foc (al fons a l'esquerra): les ombres fugen cap a la dreta i cap a
        # nosaltres, llargues.
        'characterShadow': {'enabled': True, 'color': '#0c0504', 'alpha': 0.52, 'squash': 0.4, 'core': 0.6,
                            'light': {'x': _p(FOC_POS[0], ZB)[0], 'y': _p(FOC_POS[0], ZB)[1], 'stretch': 1.0,
                                      'reach': 260}},
        'characterLights': {'ambient': '#584440', 'lights': lights},
    }


GEOMETRIA = _geometria()
