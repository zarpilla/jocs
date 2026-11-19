"""
La coberta de popa de l'Arenga: de nit (fons) i de dia (decorat `dia`, Escenes 2 i 3). EN 3D (hd640/tres_d.py), a 1×.

Exterior: una càmera a l'altura dels ulls d'algú alt (sense picat: les verticals, verticals), a proa de la coberta i
mirant cap a popa, una mica girada cap a babord. L'horitzó queda a y = 100:
  - al fons, la **borda de popa** (la de sempre, projectada), amb la regala vermella; per damunt, el **mar**, que fuig
    fins a l'horitzó (les onades són del món: grans a prop, menudes al fons) i, de dia, la **plataforma** a babord;
  - l'**estela** (decorat `horitzo`) surt de sota la popa i s'aprima fins a l'horitzó;
  - a l'esquerra, la **grua** de popa, un cilindre groc amb el cap i el braç en 3D, i la **zòdiac** penjada per
    damunt de la borda, trincada amb dos caps (el nus Bastida);
  - a la dreta, la **caseta** del menjador amb tres cares: el davant (el dibuix pla, amb la porta estanca, el rètol, el
    salvavides i l'extintor), el costat en escorç i el ràfec; per darrere s'hi pot passar;
  - la **taula** plegable de l'esmorzar (decorat), girada, al mig de la coberta;
  - primer pla: un respirador de coll de cigne i un rotllo de cap a la dreta, caixes de peix a l'esquerra, en silueta.

De nit, la llum és la del focus de la porta, el de la grua i el llum de popa; de dia, el sol alt a babord fa ombres
curtes cap a estribord i cap al fons.

El món: x a la dreta (mirant a popa, cap a babord), y amunt (0 = la coberta), z endavant (cap a popa; la càmera és a z = 0);
1 unitat = 1 píxel de sala a la distància on un personatge fa la seva mida normal (z = 450). Al terra, l'escala d'un
personatge és (v − 100) / 135, exacta.
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from hd.pix import Canvas, Light, W, H, hr, mix, B4
from hd.rooms.arenga import YELL, REDP
from hd.rooms.comu import _diff
from hd.rooms.exterior import (vnoise, fbm, smooth, NSEA, DSEA, HULLN, REDH, STEELX, CABX, DECKX, ROPE, RUST_,
                               GLOW_WARM)
from hd640.rooms import coberta_popa_pla_comu as PL
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
HOR = 100                                          # l'horitzó (la càmera no mira avall)
CAM_Y = 135
F = 450
CAM = Camera(pos=(-120, CAM_Y, 0), yaw=0.35, pitch=0.0, f=F, centre=(320, HOR))
SEA = -230                                         # el mar, sota la coberta
K = 1.2                                            # unitats del món per píxel del dibuix pla

ZS = 690                                           # la borda de popa (la cara de dins)
XP, XE = -380, 470                                 # la borda de estribord i la d'babord (la cara de dins)
BH = round((PL.FLOOR_Y - PL.RAIL) * K)             # l'alçada de la borda (la regala, a dalt)
CX0, CX1, CZ0, CZ1 = 260, 400, 430, 560            # la caseta del menjador
CHT = round((PL.FLOOR_Y - 29) * K)                 # l'alçada de la caseta (el dibuix pla, de y 29 al terra)
GRUA = (-200, 620)                                 # el peu de la grua (x, z)
GRUA_R, GRUA_H = 15, 150
PUNTA = (-110, 252, 800)                           # la punta del braç, per damunt del mar
ZODIAC = (-110, 112, 810)                          # on penja la zòdiac (el punt de sota del ganxo)
TAULA = (80, 520, 112, 56, 46, 0.3)                # la taula: x, z, ample, fons, alçada, gir
BITES = (170, 668)
CAIXA = (20, 660)                                 # la caixa de cordes
GALLEDA = (-40, 650)
ROTLLO = (-250, 530)
PESCANT = (330, 330)                               # el pescant del primer pla (a la dreta)
BIDONS = ((-262, 478), (-218, 440), (-300, 530))  # els bidons del primer pla (a l'esquerra)
PAL_POPA = (-300, 676)                              # el pal del llum de popa
WAKE_X, WAKE_K = 40, 0.00004                       # l'estela surt de sota la popa, pel mig, i es corba
PLAT_U = 375                                       # la plataforma, a l'horitzó (x de pantalla), a babord
MOON = (300, 30)
SUN = (560, 22)


def _tz(fx):
    """Una x del dibuix pla de la caseta (493..601) → la z del món, al costat de estribord de la caseta (la cara que mira
    cap al mig de la coberta; el cantó de la dreta del dibuix és el del davant)."""
    return CZ0 + (PL.HOUSE[1] - fx) * K


def _ty(fy):
    """Una y del dibuix pla (el terra, a FLOOR_Y) → l'alçada del món."""
    return (PL.FLOOR_Y - fy) * K


DOOR = (_tz(PL.DOOR[2]), _tz(PL.DOOR[0]), _ty(PL.DOOR[3]), _ty(PL.DOOR[1]))   # z0, z1 (del davant al fons), y0, y1
LAMP_P = (CX0 - 12, _ty(78), _tz(556))             # el focus de la porta
SOL_D = (-0.44, 0.33)                              # de dia, l'ombra (x, z) per unitat d'alçada: cap a estribord i al fons


LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)   # (la llum és la del món: la de l'Escena)


def _llums(dia):
    if dia:
        return [Llum((4000, 9000, -3000), 1e6, 1.6, power=1.0)]          # el sol, alt a babord
    return [Llum(LAMP_P, 330, 2.8, power=1.3),                          # el focus de la porta
            Llum((GRUA[0] + 30, 168, GRUA[1] - 20), 280, 2.2, power=1.4),   # el focus de la grua
            Llum((PAL_POPA[0], 190, PAL_POPA[1]), 200, 1.2, power=1.6),     # el llum de popa
            Llum((-6000, 4000, 9000), 1e6, 0.5, power=1.0)]                 # la lluna, a estribord


# ─── Les textures: el dibuix pla de sempre ───────────────────────────────────

def _pla(fn, dia, transparent=True):
    cv = Canvas(light=Light(ambient=3.0 if dia else 0.4, vignette=None, floor_fade=None), transparent=transparent)
    fn(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _textures(dia):
    return {
        'caseta': _pla(lambda cv: PL.house(cv, dia), dia),
        'borda': _pla(lambda cv: PL.bulwark(cv, 0, W - 1, PL.RAIL, PL.FLOOR_Y, base=2.8 if dia else 2.6,
                                            scuppers=(200, 373, 608)), dia),
        'zodiac': _pla(PL.zodiac, dia),
        'taula': _pla(PL.taula, True),
    }


# ─── El cel i el mar (en pantalla; el mar, amb les onades del món) ─────────────

def _raig(cam, u, v, y):
    """El punt del pla horitzontal d'alçada `y` que es veu al píxel (u, v), o None (si és per damunt l'horitzó)."""
    xc, yc = (u - cam.centre[0]) / cam.f, -(v - cam.centre[1]) / cam.f
    cp, sp, cy, sy = cam._cp, cam._sp, cam._cy, cam._sy
    dy = yc * cp - sp
    z1 = yc * sp + cp
    dx = xc * cy + z1 * sy
    dz = -xc * sy + z1 * cy
    if dy >= -1e-6:
        return None
    t = (y - cam.pos[1]) / dy
    return cam.pos[0] + dx * t, y, cam.pos[2] + dz * t


def mar(cv, cam, ysea, dia, phase=0.0, v0=None, v1=200, glint_u=None, seed=2, wind=0.5, x0=0, x1=None):
    """El mar en pantalla, de l'horitzó a `v1`: les onades són del món (vnoise en x, z, allargades al llarg de les
    crestes), i es fonen amb la mitjana quan un píxel ja n'abasta més d'una (cap a l'horitzó). `phase`: corre."""
    hor = cam.centre[1] - cam.f * math.tan(cam.pitch)
    v0 = int(math.ceil(hor)) if v0 is None else v0
    x1 = cv.w - 1 if x1 is None else x1
    ca, sa = math.cos(wind), math.sin(wind)
    ramp = DSEA if dia else NSEA
    for v in range(max(0, v0), v1 + 1):
        d = v - hor
        if d <= 0.3:
            for u in range(x0, x1 + 1):
                cv.put(u, v, ramp, 6.4 if dia else 4.4, lit=0)
            continue
        Pa = _raig(cam, cam.centre[0], v + 0.5, ysea)
        Pb = _raig(cam, cam.centre[0], v + 1.5, ysea)
        if Pa is None or Pb is None:
            continue
        foot = abs(math.hypot(Pa[0] - Pb[0], Pa[2] - Pb[2]))      # la mida d'un píxel al mar (en fondària)
        # les onades: llargues de debò (≈4 m de cresta a cresta) a prop; cap a l'horitzó, cada fila n'abasta més d'una
        # i es fan més llargues i primes (com les veu l'ull): sempre de ≥ 2 píxels d'alt
        la = max(240.0, foot * 2.2)
        lb = la * 3.6
        near = max(0.0, 1 - foot / 400)
        base = (5.6 - min(3.0, d * 0.05)) if dia else (3.7 - min(1.4, d * 0.028))
        for u in range(x0, x1 + 1):
            P = _raig(cam, u + 0.5, v + 0.5, ysea)
            a = P[0] * ca + P[2] * sa
            b = -P[0] * sa + P[2] * ca
            n = vnoise(a / la + phase, b / lb, seed) * 0.7 + vnoise(a / (la * 0.3) + phase * 2.2, b / (lb * 0.25), seed + 5) * 0.3
            lvl = base + (n - 0.5) * (2.0 if dia else 2.2) * (0.55 + 0.45 * near)
            if n > 0.72:
                lvl += (1.2 if dia else 1.3) * (0.5 + 0.5 * near)
            if glint_u is not None:                                 # el reflex de la lluna (o del sol)
                m = max(0.0, 1 - abs(u - glint_u) / (3 + d * 0.8))
                if m > 0:
                    lvl += m * (0.6 if dia else 1.0)
                    if n > 0.55 and hr(u // 2, v, seed) > 0.3:
                        lvl += (2.6 if dia else 3.8) * m
            elif hr(u, v, seed + 9) > 0.996:
                lvl += 1.4
            cv.put(u, v, ramp, lvl, lit=0)


def _cel(cv, dia):
    if dia:
        PL.day_sky(cv, 0, HOR, SUN)
    else:
        PL.night_sky(cv, 0, HOR, MOON)


def _mar(cv, dia, phase=0.0):
    mar(cv, CAM, SEA, dia, phase, v1=210, glint_u=None if dia else MOON[0])


# ─── El terra i les peces ─────────────────────────────────────────────────────

def _coberta(dia):
    """La coberta de planxa d'acer, en coordenades del món: planxes de 120 × 160 amb la soldadura, l'antilliscant en
    relleu, rovell i aigua a les juntes (més grosses a prop, menudes al fons)."""
    b0 = 2.6 if dia else 2.4

    def L(s, t, P):
        x, z = P[0], P[2]
        v = b0 + (fbm(x / 70, z / 50, 41) - 0.5) * 0.7
        if x % 120 < 1.6 or z % 160 < 1.6:
            return v - 1.3
        if (x % 120) < 3.4 or (z % 160) < 3.4:
            v += 0.5
        elif int(x / 3) % 2 == 0 and int(z / 3 + int(x / 6)) % 2 == 0:
            v += 0.35                                                # l'antilliscant
        if fbm(x / 40, z / 30, 43) > 0.62:
            v -= 0.5                                                 # la coberta, molla
        return v
    return L


def _planxa(lvl0, seed=61):
    """Planxa de la caseta (on el dibuix pla no arriba): juntes amb reblons i ratlles de rovell."""
    def L(s, t, P):
        y = P[1]
        v = lvl0 + (hr(int(s) // 3, int(y) // 5, seed) - 0.5) * 0.25
        for sy in (_ty(64), _ty(149)):
            if abs(y - sy) < 1.2:
                return lvl0 - 1.2
            if abs(y - sy + 3) < 1.0 and int(s) % 11 < 2:
                return lvl0 + 1.8                                    # reblons
        if y < 16:
            v -= 0.7
        return v
    return L


def cilindre(e, sid, cx, cz, r, y0, y1, ramp, lvl, n=24):
    """Un cilindre vertical: les facetes que es veuen. `lvl(angle, y, P)`."""
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        p0 = (cx + r * math.cos(a0), cz + r * math.sin(a0))
        p1 = (cx + r * math.cos(a1), cz + r * math.sin(a1))
        e.quad(sid, (p0[0], y1, p0[1]), (p1[0], y1, p1[1]), (p1[0], y0, p1[1]), (p0[0], y0, p0[1]), ramp=ramp,
               lvl=lambda s, t, P: lvl(math.atan2(P[2] - cz, P[0] - cx), P[1], P))


def _ombra(e, cx, cz, rx, rz, k=0.55, dx=0.0, dz=0.0):
    """Una ombra el·líptica al terra (desplaçada dx, dz: la llum no és a sobre)."""
    cx, cz = cx + dx, cz + dz
    e.foscor('ombra', (cx - rx, 0.3, cz + rz), (cx + rx, 0.3, cz + rz), (cx + rx, 0.3, cz - rz), (cx - rx, 0.3, cz - rz),
             lambda s, t: k * min(1.0, 1.8 * max(0.0, 1 - ((s - rx) / rx) ** 2 - ((t - rz) / rz) ** 2)))


def _ombra_pal(e, x, z, h, d, w=8, k=0.5):
    """L'ombra allargada d'una cosa dreta (alçada h) al terra, en la direcció d = (dx, dz) per unitat d'alçada."""
    lx, lz = d[0] * h, d[1] * h
    n = math.hypot(lx, lz) or 1
    px, pz = -lz / n * w / 2, lx / n * w / 2
    e.foscor('ombra', (x + px, 0.3, z + pz), (x + lx + px, 0.3, z + lz + pz), (x + lx - px, 0.3, z + lz - pz),
             (x - px, 0.3, z - pz), lambda s, t: k * (1 - 0.6 * s / n))


def borda(e, tex, dia):
    """Les tres bordes (popa, estribord, babord): el dibuix pla de sempre, amb la regala vermella per damunt."""
    tb = tex['borda']
    crop = (0, PL.RAIL, W, PL.FLOOR_Y)
    zn = -200
    e.quad('borda', (XP, BH, ZS), (XE, BH, ZS), (XE, 0, ZS), (XP, 0, ZS), tex=(tb, crop))
    e.quad('borda_b', (XP, BH, zn), (XP, BH, ZS), (XP, 0, ZS), (XP, 0, zn), tex=(tb, crop))
    e.quad('borda_e', (XE, BH, ZS), (XE, BH, zn), (XE, 0, zn), (XE, 0, ZS), tex=(tb, crop))
    red = lambda s, t, P: 3.6 + (0.8 if t < 2 else 0) - (1.2 if hr(int(s) // 7, 3) > 0.9 else 0)  # noqa: E731
    e.quad('borda', (XP - 10, BH, ZS + 10), (XE + 10, BH, ZS + 10), (XE + 10, BH, ZS), (XP - 10, BH, ZS),
           ramp=REDH, lvl=red)
    e.quad('borda_b', (XP - 10, BH, zn), (XP - 10, BH, ZS + 10), (XP, BH, ZS + 10), (XP, BH, zn), ramp=REDH, lvl=red)
    e.quad('borda_e', (XE, BH, zn), (XE, BH, ZS + 10), (XE + 10, BH, ZS + 10), (XE + 10, BH, zn), ramp=REDH, lvl=red)
    # el pal del llum de popa, a la cantonada d'babord
    px, pz = PAL_POPA
    e.tub('pal_popa', (px, 0, pz), (px, 200, pz), 3.0, STEELX, 3.6, brides=60)
    e.caixa('pal_popa', px - 6, px + 6, 200, 210, pz - 6, pz + 6, CABX, 3.0)


def grua(e, tex, dia):
    gx, gz = GRUA
    _ombra(e, gx, gz, 34, 22, 0.55, *_desp(gx, gz, 60, dia))

    def groc(a, y, P):
        v = 3.0 + 1.3 * math.cos(a + 2.2)
        if 16 < y < 34 and (int(y) + int(a * 12)) // 5 % 2:
            return 1.2 + 0.8 * math.cos(a + 2.2)                    # les franges de perill
        if abs(y - 70) < 1 or abs(y - 118) < 1:
            v -= 0.9                                                # les soldadures de les virolles
        return v
    e.caixa('grua_peu', gx - 24, gx + 24, 0, 6, gz - 24, gz + 24, STEELX, 2.6)
    cilindre(e, 'grua_peu', gx, gz, GRUA_R, 6, GRUA_H, YELL, groc)
    cilindre(e, 'grua_peu', gx, gz, GRUA_R + 4, GRUA_H - 8, GRUA_H, STEELX,
             lambda a, y, P: 2.8 + 1.2 * math.cos(a + 2.2) - (1.0 if int(a * 8) % 2 else 0))
    # el cap (la caixa dels motors), girat cap al braç
    ang = math.atan2(PUNTA[2] - gz, PUNTA[0] - gx)
    e.caixa_girada('grua', gx + 6, gz + 4, 40, 30, 26, -ang + math.pi / 2, YELL, 3.0, y0=GRUA_H,
                   cares={'dalt': {'ramp': YELL, 'lvl': 4.2}, 'esquerra': {'ramp': YELL, 'lvl': 2.2},
                          'dreta': {'ramp': YELL, 'lvl': 2.0},
                          'davant': {'ramp': YELL, 'lvl': lambda s, t, P: 1.6 if 4 < s < 16 and 6 < t < 16 else 2.6}})
    # el braç, el cilindre hidràulic i el cable amb el ganxo
    base = (gx + 8, GRUA_H + 18, gz + 8)
    e.tub('grua', base, PUNTA, 4.5, YELL, 3.0, llum_dir=(-0.3, 1.0))
    mid = (base[0] + (PUNTA[0] - base[0]) * 0.45, base[1] + (PUNTA[1] - base[1]) * 0.45 - 2, base[2] + (PUNTA[2] - base[2]) * 0.45)
    e.tub('grua', (gx + 4, GRUA_H - 30, gz + 6), mid, 2.0, STEELX, 4.0)
    e.cable('grua', [PUNTA, (PUNTA[0], ZODIAC[1] + 50, PUNTA[2])], CABX, 3.4, gruix=1.0)
    e.caixa('grua', PUNTA[0] - 3, PUNTA[0] + 3, ZODIAC[1] + 40, ZODIAC[1] + 50, PUNTA[2] - 3, PUNTA[2] + 3, STEELX, 3.4)
    # la zòdiac penjada (el dibuix pla, dret) i les eslingues
    zx, zy, zz = ZODIAC
    zimg = tex['zodiac']
    box = (62, 76, 197, 128)
    e.sprite('grua', zimg.crop(box), (185 - box[0], 128 - box[1]), (zx, zy - 22, zz), escala_img=K)
    for dxs in (-60, 50):
        e.cable('grua', [(PUNTA[0], ZODIAC[1] + 40, PUNTA[2]), (zx + dxs, zy + 18, zz)], ROPE, 3.0, gruix=0.8)
    # les trinques: dos caps de la zòdiac a la regala, amb el nus Bastida
    for dxs in (-36, 28):
        e.cable('grua', [(zx + dxs, zy - 6, zz - 4), (zx + dxs * 0.8, BH + 2, ZS + 4)], ROPE, 3.2, gruix=1.2)
    e.caixa('grua', zx + 18, zx + 26, BH, BH + 7, ZS, ZS + 7, ROPE, 3.6)


def _ombra_caixa(e, x0, x1, z0, z1, h, d, k=0.5):
    """L'ombra d'una caixa (x0..x1, z0..z1, alçada h) al terra, amb la llum en la direcció d (per unitat d'alçada)."""
    ox, oz = d[0] * h, d[1] * h
    pts = [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]
    pts = pts + [(x + ox, z + oz) for x, z in pts]
    ax0, ax1 = min(p[0] for p in pts), max(p[0] for p in pts)
    az0, az1 = min(p[1] for p in pts), max(p[1] for p in pts)
    hull = _envolupant(pts)

    def fn(s, t):
        x, z = ax0 + s, az1 - t
        return k if _dins2(x, z, hull) else 0.0
    e.foscor('ombra', (ax0, 0.3, az1), (ax1, 0.3, az1), (ax1, 0.3, az0), (ax0, 0.3, az0), fn)


def _envolupant(pts):
    """L'envolupant convexa (monotone chain) de punts (x, z), en sentit antihorari."""
    pts = sorted(set(pts))

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


def _dins2(x, z, poly):
    for (ax, az), (bx, bz) in zip(poly, poly[1:] + poly[:1]):
        if (bx - ax) * (z - az) - (bz - az) * (x - ax) < 0:
            return False
    return True


def _desp(x, z, h, dia):
    """On cau el centre de l'ombra d'una cosa d'alçada h a (x, z): de dia, el sol; de nit, lluny del focus de la porta."""
    if dia:
        return SOL_D[0] * h * 0.5, SOL_D[1] * h * 0.5
    dx, dz = x - LAMP_P[0], z - LAMP_P[2]
    n = math.hypot(dx, dz) or 1
    k = h * 0.5 * min(1.0, 160 / n)
    return dx / n * k, dz / n * k


def caseta(e, tex, dia):
    """La caseta del menjador: el costat de estribord (el dibuix pla, amb la porta estanca, el rètol, el salvavides i
    l'extintor), el davant en escorç (planxa, un ull de bou) i el ràfec amb la barana."""
    if dia:
        _ombra_caixa(e, CX0, CX1, CZ0, CZ1, CHT, SOL_D, 0.5)
    else:
        _ombra(e, (CX0 + CX1) / 2 + 30, CZ1 + 16, 110, 34, 0.6)
    tc = tex['caseta']
    hx0, hx1 = PL.HOUSE
    e.quad('caseta', (CX0, CHT, CZ1), (CX0, CHT, CZ0), (CX0, 0, CZ0), (CX0, 0, CZ1),
           tex=(tc, (hx0, 29, hx1 + 1, PL.FLOOR_Y)))
    e.quad('caseta_davant', (CX0, CHT, CZ0), (CX1, CHT, CZ0), (CX1, 0, CZ0), (CX0, 0, CZ0), ramp=HULLN,
           lvl=_planxa(2.0 if not dia else 2.6, seed=67))
    # un ull de bou al davant
    ox, oy = CX0 + 70, _ty(53)
    e.quad('caseta_davant', (ox - 10, oy + 10, CZ0 - 1), (ox + 10, oy + 10, CZ0 - 1), (ox + 10, oy - 10, CZ0 - 1),
           (ox - 10, oy - 10, CZ0 - 1), ramp=CABX, lvl=lambda s, t, P: 3.8 - s * 0.05 - t * 0.05,
           forma=lambda s, t: (s - 10) ** 2 + (t - 10) ** 2 < 100)
    WIN = [(40, 26, 10), (110, 74, 28), (190, 140, 60), (240, 200, 110)]
    e.quad('caseta_davant', (ox - 7, oy + 7, CZ0 - 1.5), (ox + 7, oy + 7, CZ0 - 1.5), (ox + 7, oy - 7, CZ0 - 1.5),
           (ox - 7, oy - 7, CZ0 - 1.5), ramp=CABX if dia else WIN,
           lvl=(lambda s, t, P: 4.6 - t * 0.2 + (1.4 if s < 5 and t < 5 else 0)) if dia else (lambda s, t, P: 2.4 - t * 0.08),
           forma=lambda s, t: (s - 7) ** 2 + (t - 7) ** 2 < 49)
    # el ràfec (la coberta de botes, per damunt) i la barana
    e.caixa('caseta', CX0 - 12, CX1 + 10, CHT, CHT + 12, CZ0 - 10, CZ1 + 10, HULLN, 3.4,
            cares={'davant': {'ramp': HULLN, 'lvl': lambda s, t, P: 2.4 if 5 < t < 8 else 3.6},
                   'esquerra': {'ramp': HULLN, 'lvl': lambda s, t, P: 2.6 if 5 < t < 8 else 4.0},
                   'sota': {'ramp': HULLN, 'lvl': 1.0}})
    for k in range(7):
        x = CX0 - 8 + k * (CX1 - CX0 + 14) / 6
        e.caixa('caseta', x - 1.2, x + 1.2, CHT + 12, CHT + 44, CZ0 - 7, CZ0 - 5, HULLN, 3.6)
    for k in range(7):
        z = CZ0 - 6 + k * (CZ1 - CZ0 + 12) / 6
        e.caixa('caseta', CX0 - 9, CX0 - 7, CHT + 12, CHT + 44, z - 1.2, z + 1.2, HULLN, 4.4)
    for hgt in (CHT + 28, CHT + 44):
        e.caixa('caseta', CX0 - 9, CX1 + 8, hgt - 1.5, hgt, CZ0 - 7, CZ0 - 5, HULLN, 3.8)
        e.caixa('caseta', CX0 - 9, CX0 - 7, hgt - 1.5, hgt, CZ0 - 7, CZ1 + 6, HULLN, 4.6)


def coses(e, dia):
    """Les bites, la caixa de cordes, la galleda i el rotllo de cap, contra la borda de popa."""
    WOODB = [(30, 18, 10), (56, 36, 20), (88, 60, 34), (124, 88, 52), (160, 120, 74), (190, 152, 100)]
    sh = (-0.35, 0.25) if dia else (0.0, 0.0)
    bx, bz = BITES
    _ombra(e, bx, bz, 30, 12, 0.5, *_desp(bx, bz, 30, dia))
    e.caixa('coses', bx - 26, bx + 26, 0, 5, bz - 9, bz + 9, HULLN, 2.0)
    for dx in (-15, 15):
        cilindre(e, 'coses', bx + dx, bz, 5.5, 5, 30, STEELX, lambda a, y, P: 2.6 + 1.4 * math.cos(a + 2.2), n=12)
        e.caixa('coses', bx + dx - 6.5, bx + dx + 6.5, 30, 33, bz - 6.5, bz + 6.5, STEELX, 4.0)
    for k in range(3):
        e.cable('coses', [(bx - 15, 12 + k * 4, bz - 5), (bx + 15, 14 + k * 4, bz - 5)], ROPE, 3.2, gruix=2.0)
    cx_, cz_ = CAIXA
    _ombra(e, cx_, cz_, 40, 18, 0.5, *_desp(cx_, cz_, 36, dia))
    e.caixa_girada('coses', cx_, cz_, 62, 32, 34, -0.12, WOODB, 2.4,
                   cares={'davant': {'ramp': WOODB, 'lvl': lambda s, t, P: 1.2 if int(t) % 11 < 1 or s < 3 or s > 59 else 2.6},
                          'dalt': {'ramp': WOODB, 'lvl': lambda s, t, P: 3.8 - (1.4 if int(t) % 8 < 1 else 0)},
                          'esquerra': {'ramp': WOODB, 'lvl': 1.6}, 'dreta': {'ramp': WOODB, 'lvl': 1.4}})
    e.caixa_girada('coses', cx_ + 2, cz_, 14, 8, 6, -0.12, STEELX, 3.6, y0=34)
    gx, gz = GALLEDA
    BLUE = [(20, 40, 70), (30, 60, 110), (50, 90, 150), (80, 130, 190)]
    cilindre(e, 'coses', gx, gz, 8, 0, 20, BLUE, lambda a, y, P: 1.6 + 1.0 * math.cos(a + 2.2), n=12)
    e.cable('coses', [(gx - 8, 20, gz), (gx, 28, gz - 2), (gx + 8, 20, gz)], STEELX, 3.0, gruix=0.8)
    # el rotllo de cap, a terra
    rx, rz = ROTLLO
    for k in range(6):
        r = 24 - k * 3
        e.quad('coses', (rx - r, 1 + k * 0.8, rz + r), (rx + r, 1 + k * 0.8, rz + r), (rx + r, 1 + k * 0.8, rz - r),
               (rx - r, 1 + k * 0.8, rz - r), ramp=ROPE,
               lvl=lambda s, t, P, r=r: 3.0 + (0.8 if int(math.hypot(s - r, t - r)) % 3 == 0 else 0) - (s - r) / r * 0.6,
               forma=lambda s, t, r=r: (r - 3.2) ** 2 < (s - r) ** 2 + (t - r) ** 2 < r * r)
    e.cable('coses', [(rx + 22, 1, rz - 6), (rx + 40, 1, rz - 18), (rx + 52, 1, rz - 16)], ROPE, 3.0, gruix=2.4)


FOSC = [(3, 4, 6), (7, 9, 12), (12, 15, 19), (19, 23, 28), (28, 33, 39), (40, 46, 52)]


def primer_pla(e, dia):
    """Un pescant fosc a la dreta (el pal, el braç i un bossell que penja) i caixes de peix a l'esquerra, a prop i en
    silueta, tallats per la vora."""
    px, pz = PESCANT
    e.tub('primer_pla', (px, 0, pz), (px, 250, pz), 7, FOSC, 2.2, brides=80, llum_dir=(-0.6, 1.0))
    e.tub('primer_pla', (px, 250, pz), (px - 10, 280, pz - 10), 7, FOSC, 2.0)
    e.tub('primer_pla', (px - 10, 280, pz - 10), (px - 90, 300, pz - 60), 6, FOSC, 1.8)
    e.caixa('primer_pla', px - 16, px + 16, 0, 6, pz - 16, pz + 16, FOSC, 1.8)
    for k, (bx, bz) in enumerate(BIDONS):                  # els bidons de gasoil, a l'esquerra
        cilindre(e, 'primer_pla', bx, bz, 24, 0, 80, FOSC,
                 lambda a, y, P: 1.8 + 1.2 * math.cos(a + 2.6) + (0.9 if abs(y - 26) < 2 or abs(y - 54) < 2 else 0), n=20)
        e.quad('primer_pla', (bx - 24, 80, bz + 24), (bx + 24, 80, bz + 24), (bx + 24, 80, bz - 24), (bx - 24, 80, bz - 24),
               ramp=FOSC, lvl=lambda s, t, P: 3.0 - (1.2 if abs(math.hypot(s - 24, t - 24) - 21) < 1.2 else 0)
               + (1.4 if math.hypot(s - 32, t - 30) < 3 else 0),
               forma=lambda s, t: (s - 24) ** 2 + (t - 24) ** 2 < 576)


def taula(e, tex):
    """La taula plegable de l'esmorzar, girada: la tapa, les potes en X i les coses de damunt (el dibuix pla)."""
    tx, tz, tw, td, th, ta = TAULA
    _ombra(e, tx, tz, tw * 0.6, td * 0.7, 0.5, *_desp(tx, tz, 46, True))
    TOPR = [(60, 60, 58), (96, 94, 90), (134, 132, 124), (170, 166, 156), (200, 196, 184), (226, 222, 210)]
    c, s_ = math.cos(ta), math.sin(ta)

    def P(lx, y, lz):
        return (tx + lx * c - lz * s_, y, tz + lx * s_ + lz * c)
    for lx in (-tw / 2 + 10, tw / 2 - 10):
        for lz0, lz1 in ((-td / 2 + 4, td / 2 - 4), (td / 2 - 4, -td / 2 + 4)):
            e.cable('taula', [P(lx, 1, lz0), P(lx, th - 2, lz1)], STEELX, 3.2, gruix=2.0)
    e.caixa_girada('taula', tx, tz, tw, td, 3, ta, TOPR, 3.6, y0=th - 3,
                   cares={'dalt': {'ramp': TOPR, 'lvl': lambda s_, t, P_: 4.2 - t * 0.01}, 'davant': {'ramp': TOPR, 'lvl': 1.6},
                          'esquerra': {'ramp': TOPR, 'lvl': 1.4}, 'dreta': {'ramp': TOPR, 'lvl': 1.2}})
    box = (412, 152, 505, 181)
    e.sprite('taula', tex['taula'].crop(box), ((box[2] - box[0]) / 2, box[3] - box[1]), P(0, th, 4), escala_img=1.0)


# ─── Composició ─────────────────────────────────────────────────────────────

def escena(cv, dia, estat=frozenset()):
    """Tota la sala, de lluny a prop. `estat`: 'taula'. → l'Escena (qui ha pintat què)."""
    tex = _textures(dia)
    _cel(cv, dia)
    _mar(cv, dia)
    e = Escena(cv, CAM, _llums(dia), ambient=0.8 if dia else -0.5)
    e.quad('terra', (XP - 20, 0, ZS + 10), (XE + 20, 0, ZS + 10), (XE + 20, 0, 40), (XP - 20, 0, 40), ramp=DECKX,
           lvl=_coberta(dia))
    # la llum dels focus al terra i la foscor arran de les bordes
    if not dia:
        lx, ly, lz = LAMP_P
        e.claror((lx - 200, 0.3, lz + 160), (lx + 160, 0.3, lz + 160), (lx + 160, 0.3, lz - 220), (lx - 200, 0.3, lz - 220),
                 GLOW_WARM, lambda s, t: 0.22 * max(0.0, 1 - math.hypot((s - 200) / 190, (t - 160) / 150)) ** 1.3)
        gx, gz = GRUA
        e.claror((gx - 120, 0.3, gz + 90), (gx + 160, 0.3, gz + 90), (gx + 160, 0.3, gz - 170), (gx - 120, 0.3, gz - 170),
                 GLOW_WARM, lambda s, t: 0.16 * max(0.0, 1 - math.hypot((s - 150) / 140, (t - 110) / 120)) ** 1.3)
    e.foscor('racons', (XP, 0.4, ZS), (XE, 0.4, ZS), (XE, 0.4, ZS - 40), (XP, 0.4, ZS - 40),
             lambda s, t: 0.45 * max(0.0, 1 - t / 40))
    e.foscor('racons', (XP, 0.4, ZS), (XP + 40, 0.4, ZS), (XP + 40, 0.4, 40), (XP, 0.4, 40),
             lambda s, t: 0.45 * max(0.0, 1 - s / 40))
    e.foscor('racons', (XE - 40, 0.4, ZS), (XE, 0.4, ZS), (XE, 0.4, 40), (XE - 40, 0.4, 40),
             lambda s, t: 0.45 * max(0.0, (s - 0) / 40))
    borda(e, tex, dia)
    coses(e, dia)
    grua(e, tex, dia)
    caseta(e, tex, dia)
    if 'taula' in estat:
        taula(e, tex)
    primer_pla(e, dia)
    return e


def _render(dia, estat=frozenset()):
    cv = Canvas(light=LIGHT)
    e = escena(cv, dia, estat)
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)        # la barra de verbs: negre
    return cv.img, e


@functools.lru_cache(maxsize=None)
def _base(dia=False):
    return _render(dia)


def bg(cv):
    cv.img.paste(_base(False)[0])
    cv.P = cv.img.load()


def dia(cv):
    cv.img.alpha_composite(_base(True)[0])
    cv.P = cv.img.load()


def _amo(ids):
    def mask(x, y):
        _, e = _base(False)
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


@functools.lru_cache(maxsize=None)
def _obert():
    """Els píxels (x, y) on es veu el cel o el mar (ningú no hi ha pintat res de l'escena)."""
    _, e = _base(False)
    return [(x, y) for y in range(BOTTOM) for x in range(W) if e.amo[y * W + x] == 0]


# ─── Props ──────────────────────────────────────────────────────────────────

def _taula(cv):
    img, _ = _render(True, frozenset({'taula'}))
    cv.img.alpha_composite(_diff(img, _base(True)[0]))
    cv.P = cv.img.load()


PLAT_DX, PLAT_DY = PLAT_U - 320, HOR - PL.HOR


def _plataforma_img(t=0.0):
    """La plataforma (i les gavines) del dibuix pla, moguda a l'horitzó d'aquí, només on es veu el cel o el mar."""
    from PIL import Image
    src = Canvas(light=LIGHT, transparent=True)
    PL.plataforma(src, t)
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    sp, dp = src.img.load(), out.load()
    obert = set(_obert())
    for x, y in obert:
        sx, sy = x - PLAT_DX, y - PLAT_DY
        if 0 <= sx < W and 0 <= sy < H:
            c = sp[sx, sy]
            if c[3]:
                dp[x, y] = c
    return out


def plataforma(cv, t=0.0):
    cv.img.alpha_composite(_plataforma_img(t))
    cv.P = cv.img.load()


def _estela(x, z):
    """Quanta escuma (0..1) hi ha al punt del mar (x, z): l'estela que surt de sota la popa i s'obre i s'esvaeix."""
    d = z - ZS
    if d < 0:
        return 0.0
    x -= WAKE_X + WAKE_K * d * d                                     # (l'Arenga ha virat: l'estela es corba)
    hw = 70 + d * 0.06
    c = abs(x - math.sin(d / 900) * 60) / hw
    k = max(0.0, 1 - c) ** 0.8 * (1 - smooth(1500, 16000, d))
    arm = abs(abs(x) - (40 + d * 0.33)) / (6 + d * 0.012)   # els dos braços (les ones de Kelvin)
    k = max(k, 0.5 * max(0.0, 1 - arm) * (1 - smooth(600, 6000, d)))
    n = fbm(x / 40, z / 90, 77)
    return k * (0.6 + 0.8 * (n - 0.5) + 0.4)


def horitzo(cv):
    """L'estela: escuma al mar (al món), que s'aprima cap a l'horitzó; només on es veu el mar."""
    for x, y in _obert():
        if y <= HOR:
            continue
        P = _raig(CAM, x + 0.5, y + 0.5, SEA)
        if P is None:
            continue
        k = _estela(P[0], P[2])
        if k > 0.15 + (B4[y & 3][x & 3] - 0.5) * 0.25:
            cv.P[x, y] = (206, 216, 218, int(min(0.75, k * 0.9) * 255))


PROPS = {'dia': dia, 'plataforma': plataforma, 'taula': _taula, 'horitzo': horitzo}


# ─── Animacions ────────────────────────────────────────────────────────────

SEA_N, SEA_FADE, SEA_STEP = 12, 4, 0.09


def frames_mar(base, punts, pinta):
    """Els fotogrames del mar que corre: `pinta(cv, phase)` el dibuixa sol; es copia als `punts` (x, y) on el fons és
    el mar quiet. Els darrers SEA_FADE es fonen amb el principi (el bucle no salta)."""
    ref = Canvas(light=LIGHT)
    pinta(ref, 0.0)
    rp, bp = ref.img.load(), base.load()
    obert = [(x, y) for x, y in punts if bp[x, y] == rp[x, y]]
    frames = []
    for i in range(SEA_N):
        a, b = Canvas(light=LIGHT), Canvas(light=LIGHT)
        pinta(a, i * SEA_STEP)
        pinta(b, (i - SEA_N) * SEA_STEP)
        w = max(0, i - (SEA_N - SEA_FADE)) / SEA_FADE
        out = base.copy()
        o, ap, bpp = out.load(), a.img.load(), b.img.load()
        for x, y in obert:
            o[x, y] = bpp[x, y] if hr(x, y, 90) < w else ap[x, y]
        frames.append(_diff(out, base))
    return frames


def _punts_mar():
    return [(x, y) for x, y in _obert() if y > HOR]


def _frames_mar():
    return frames_mar(_base(False)[0], _punts_mar(), lambda cv, ph: _mar(cv, False, ph))


def _frames_dia_mar():
    return frames_mar(_base(True)[0], _punts_mar(), lambda cv, ph: _mar(cv, True, ph))


def _frames_plataforma():
    return [_plataforma_img(i / 16) for i in range(16)]


ANIMS = {'mar': {'frames': _frames_mar, 'frameDuration': 260},
         'dia_mar': {'frames': _frames_dia_mar, 'frameDuration': 260},
         'plataforma': {'frames': _frames_plataforma, 'frameDuration': 180}}


# ─── Geometria (coordenades de sala, projectades) ────────────────────────────

def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


def _v(z, x=0.0):
    return round(CAM.projecta((x, 0, z))[1])


# Capes del davant: el primer pla (sempre davant), la grua, la caseta (s'hi passa per darrere) i la taula.
FRONT = [
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20, 'variants': ('dia',)},
    {'id': 'davant_grua', 'mask': _amo({'grua_peu'}), 'baseline': _v(GRUA[1] - GRUA_R, GRUA[0]), 'zIndex': 20, 'variants': ('dia',)},
    {'id': 'davant_caseta', 'mask': _amo({'caseta', 'caseta_davant'}), 'baseline': _v(CZ1, CX0), 'zIndex': 20, 'variants': ('dia',)},
    {'id': 'davant_taula', 'mask': lambda x, y: False, 'baseline': _v(TAULA[1] - 20, TAULA[0]), 'zIndex': 20,
     'props': ('taula',)},
]

# El terra on es camina (al món): de la borda de popa fins a prop de la càmera, entre les bordes, amb la caseta
# (es pot passar per darrere i pel costat d'babord, cap a proa) i el peu de la grua com a forats.
V_PROP = 256                                       # el terra on es camina, fins aquí (l'escala, ≈1,16)
_NL, _NR = _raig(CAM, 60, V_PROP, 0), _raig(CAM, W - 1, V_PROP, 0)
WALK_MON = [(XP + 60, ZS - 36), (XE - 26, ZS - 36), (XE - 26, 340), (_NR[0], _NR[2]), (_NL[0], _NL[2]),
            (XP + 60, 520)]
_WALK = [(min(W - 1, max(0, u)), v) for u, v in (_p(x, z) for x, z in WALK_MON)]
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)


def _cercle(cx, cz, r, n=10):
    return [_p(cx + r * math.cos(2 * math.pi * i / n), cz + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


_FORATS = [_cercle(GRUA[0], GRUA[1], GRUA_R + 22, 10),
           [_p(CX0 - 14, CZ0 - 14), _p(CX1 + 14, CZ0 - 14), _p(CX1 + 14, CZ1 + 14), _p(CX0 - 14, CZ1 + 14)]]

_PLAT = (272 + PLAT_DX, 35 + PLAT_DY, 371 + PLAT_DX, 123 + PLAT_DY)

GEOMETRIA = {
    'things': {
        'porta': {'rect': _rect_mon((CX0, DOOR[3], DOOR[0]), (CX0, DOOR[2], DOOR[1])),
                  'walk': _p(CX0 - 36, (DOOR[0] + DOOR[1]) / 2)},
        'proa': {'rect': (W - 34, 130, W - 1, BOTTOM), 'walk': _p(XE - 50, 380)},
        'grua': {'rect': _rect_mon((GRUA[0] - GRUA_R, 0, GRUA[1]), (GRUA[0], GRUA_H + 30, GRUA[1]), PUNTA,
                                   (ZODIAC[0] - 80, ZODIAC[1] - 20, ZODIAC[2]), (ZODIAC[0] + 70, ZODIAC[1] + 30, ZODIAC[2])),
                 'walk': _p(GRUA[0] + 50, GRUA[1] - 60)},
        'borda': {'rect': _rect_mon((-120, BH + 4, ZS), (CX0 - 10, 0, ZS)), 'walk': _p(30, ZS - 50)},
        'plataforma': {'rect': _PLAT, 'walk': _p(140, ZS - 50)},
        'taula': {'rect': _rect_mon(*[(TAULA[0] + dx, y, TAULA[1] + dz) for dx in (-60, 60) for dz in (-40, 40)
                                      for y in (0, TAULA[4] + 22)]),
                  'walk': _p(TAULA[0] + 10, TAULA[1] - 70)},
        'horitzo': {'rect': _rect_mon(*[(WAKE_X + WAKE_K * d * d + dx, SEA, ZS + d) for d in (2600, 20000)
                                        for dx in (-160, 160)]),
                    'walk': _p(20, ZS - 50)},
    },
    'spawns': {'iri': _p(0, 450), 'vet': _p(-110, 440), 'bastida': _p(-40, ZS - 50),
               'capitana': _p(160, 570), 'tomas': _p(210, 610), 'nadia': _p(-30, 540), 'marcel': _p(440, 400)},
    'walkable': _WALK,
    'forats': _FORATS,
    # La càmera no mira avall: el terra es veu aixafat com (alçada de la càmera) / (fons on es camina).
    'floorSquash': 0.27,
    # L'ombra de contacte: de nit, el focus de la porta; de dia, el sol alt a babord: cap a estribord i una mica al fons.
    'characterShadow': {'enabled': True, 'color': '#0a0e16', 'alpha': 0.42, 'squash': 0.3, 'core': 0.6,
                        'light': {'x': -1, 'y': -0.18, 'direction': True, 'stretch': 0.5}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round((_V_FONS - 2 - HOR) / CAM_Y, 3), 'scaleBottom': round((_V_PROP + 2 - HOR) / CAM_Y, 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
}
