"""
La coberta de proa de l'Arenga: de nit (fons) i de dia (decorat `dia`, Escenes 2 i 3, amb el racó de la Juana).
EN 3D (hd640/tres_d.py), a 1×.

Exterior, com la de popa (coberta_popa.py, d'on surten el mar, les ombres i les animacions): una càmera a l'altura
dels ulls d'algú alt, sense picat, a popa de la coberta i mirant cap a proa, una mica girada cap a babord. L'horitzó
queda a y = 100, i el mar fuig cap a l'horitzó per damunt de la borda:
  - les dues **bordes** (el dibuix pla de sempre, projectat) s'ajunten a la **roda**, amb l'asta, al fons: es veu que
    el vaixell s'aprima, i la borda s'aixeca cap a proa;
  - el **molinet** de l'àncora, al mig, amb tres cares (el costat és el dibuix pla: el barbotí, el tambor, el volant del
    fre), i la **cadena** que corre per la coberta fins a l'escobenc; davant, l'**escotilla** de la caixa de cadenes,
    amb la balda (i el **cadenat**, decorat);
  - a l'esquerra, la **caseta** del passadís: el darrere (el dibuix pla, amb la porta estanca i el rètol) i el costat en
    escorç; s'hi pot passar per darrere; a l'esquerra de tot, la coberta lateral cap a popa;
  - a la dreta, la **balsa** salvavides (un cilindre blanc amb les cintes, sobre el bressol) i, de dia, el racó de la
    Juana (la caixa de peix amb la manta i el coixí); el **pal de proa**, amb el focus i la campana;
  - primer pla: el voladís del pont, fosc, a dalt a l'esquerra, i un respirador a baix a la dreta.

El món: x a la dreta (cap a estribord), y amunt (0 = la coberta), z endavant (cap a proa; la càmera és a z = 0).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from hd.pix import Canvas, Light, W, H, hr, GOLD
from hd.rooms.comu import _diff
from hd.rooms.exterior import smooth, fbm, HULLN, REDH, STEELX, CABX, DECKX, ROPE, ORANGEB, GLOW_WARM
from hd640.rooms import coberta_proa_pla_comu as PL
from hd640.rooms.coberta_popa import (_raig, mar, frames_mar, cilindre, _ombra, _ombra_caixa, _coberta, _planxa,
                                      FOSC, LIGHT, BOTTOM, HOR, CAM_Y, F, SEA, K, BH)
from hd640.tres_d import Camera, Escena, Llum

CAM = Camera(pos=(120, CAM_Y, 0), yaw=-0.3, pitch=0.0, f=F, centre=(320, HOR))

XB = 400                                           # mitja mànega: les bordes, a x = ±XB fins a ZC
ZC, ZR = 520, 1150                                 # on comença a aprimar-se i la roda
CX0, CX1, CZ0, CZ1 = -330, -180, 430, 560          # la caseta del passadís
CHT = round((PL.FLOOR_Y - 29) * K)
MOL = (20, 720, -0.12)                             # el molinet: x, z del centre, gir
MOL_L, MOL_W = round((284 - 184) * K), 56          # el llarg (al llarg del vaixell) i l'ample
MOL_H = round((PL.FLOOR_Y + 10 - 150) * K)
ESCO = (60, 560, 96, 64, -0.08)                    # l'escotilla: x, z, ample, fons, gir
ESCOBENC = (16, 1060)
BALSA = (250, 700)                                 # el centre de la balsa (al bressol)
BALSA_R, BALSA_L, BALSA_Y = 27, 128, 62
MANTA = (232, 620)                                 # el racó de la Juana (de dia)
PAL = (150, 960)                                   # el pal de proa
BITES = (-250, 780)
ROTLLO = (-120, 660)
MOON = (390, 30)
SUN = (90, 22)
SOL_D = (0.44, -0.33)                              # de dia, l'ombra (x, z) per unitat d'alçada


def _tx(fx):
    """Una x del dibuix pla de la caseta (40..149) → la x del món, al darrere de la caseta (la cara que mira a popa)."""
    return CX0 + (fx - PL.HOUSE[0]) * K


def _ty(fy):
    return (PL.FLOOR_Y - fy) * K


DOOR = (_tx(PL.DOOR[0]), _tx(PL.DOOR[2]), _ty(PL.DOOR[3]), _ty(PL.DOOR[1]))     # x0, x1, y0, y1
LAMP_P = (_tx(89), _ty(78), CZ0 - 12)              # el focus de la porta
MAST_K = 1.8                                       # el pal (el dibuix pla, dret): unitats per píxel
FOCUS_P = (PAL[0] + 8 * MAST_K, (PL.FLOOR_Y + 3 - 62) * MAST_K, PAL[1] - 10)


def _llums(dia):
    if dia:
        return [Llum((-4000, 9000, 3000), 1e6, 1.6, power=1.0)]
    return [Llum(LAMP_P, 330, 2.6, power=1.3),
            Llum(FOCUS_P, 520, 2.6, power=1.3),
            Llum((-6000, 4000, 9000), 1e6, 0.5, power=1.0)]


# ─── Les textures ─────────────────────────────────────────────────────────────

def _light(dia):
    return Light(ambient=3.0 if dia else 0.4, vignette=None, floor_fade=None)


def _pla(fn, dia):
    cv = Canvas(light=_light(dia), transparent=True)
    fn(cv)
    return cv.img


def _pal_img(dia, dx=0):
    PL._SWING['dx'] = dx
    try:
        return _pla(lambda cv: PL.mast(cv, dia), dia)
    finally:
        PL._SWING['dx'] = 0


MAST_BOX = (PL.MX - 22, 0, PL.MX + 24, PL.FLOOR_Y + 5)


@functools.lru_cache(maxsize=None)
def _textures(dia):
    from hd640.rooms.coberta_popa_pla_comu import bulwark
    return {
        'caseta': _pla(lambda cv: PL.house(cv, dia), dia),
        'borda': _pla(lambda cv: bulwark(cv, 0, W - 1, PL.RAIL, PL.FLOOR_Y, base=2.8 if dia else 2.6,
                                         scuppers=(173, 333)), dia),
        'molinet': _pla(PL.windlass, dia),
        'pal': _pal_img(dia),
        'balsa': _pla(lambda cv: PL.balsa(cv, dia), dia),
        'manta': _pla(PL.manta, True),
    }


# ─── El cel i el mar ──────────────────────────────────────────────────────────

def _cel(cv, dia):
    if dia:
        PL.day_sky(cv, 0, HOR, SUN, seed=14)
    else:
        PL.night_sky(cv, 0, HOR, MOON, seed=6, clouds=0.55)


def _mar(cv, dia, phase=0.0):
    mar(cv, CAM, SEA, dia, phase, v1=200, glint_u=None if dia else MOON[0], seed=5, wind=-0.4)


# ─── Les bordes ───────────────────────────────────────────────────────────────

def _bx(z):
    """Mitja mànega a la z: recta fins a ZC i després s'aprima fins a la roda."""
    if z <= ZC:
        return XB
    t = min(1.0, (z - ZC) / (ZR - ZC))
    return XB * (1 - t ** 1.7)


def _bh(z):
    """L'alçada de la borda: s'aixeca cap a proa."""
    return BH + 34 * smooth(ZC, ZR, z)


def _borda_punts(side, z0=-200, n=26):
    pts = [(side * XB, z0), (side * XB, ZC)]
    for i in range(1, n + 1):
        z = ZC + (ZR - ZC) * i / n
        pts.append((side * _bx(z), z))
    return pts


def bordes(e, tex):
    """Les bordes: trams rectes amb la textura de la borda plana (a tires que segueixen la llargada) i la regala."""
    tb = tex['borda']
    red = lambda s, t, P: 3.6 + (0.8 if t < 2 else 0) - (1.2 if hr(int(s) // 7, 3) > 0.9 else 0)  # noqa: E731
    for side in (-1, 1):
        pts = _borda_punts(side)
        acc = 0.0
        for (ax, az), (bx, bz) in zip(pts, pts[1:]):
            L = math.hypot(bx - ax, bz - az)
            h = _bh((az + bz) / 2)
            fx0 = (acc / K) % W
            fx1 = min(W, fx0 + L / K)
            acc += L
            sid = 'borda'
            if side < 0:
                e.quad(sid, (ax, h, az), (bx, h, bz), (bx, 0, bz), (ax, 0, az), tex=(tb, (fx0, PL.RAIL, fx1, PL.FLOOR_Y)))
            else:
                e.quad(sid, (bx, h, bz), (ax, h, az), (ax, 0, az), (bx, 0, bz), tex=(tb, (fx1, PL.RAIL, fx0, PL.FLOOR_Y)))
            # la regala, per damunt (cap enfora)
            ux, uz = (bx - ax) / L, (bz - az) / L
            ox, oz = side * uz * 10, -side * ux * 10
            e.quad(sid, (ax, h, az), (bx, h, bz), (bx + ox, h, bz + oz), (ax + ox, h, az + oz), ramp=REDH,
                   lvl=red, dues_cares=True)
    # l'asta de la roda, amb la drissa
    e.tub('borda', (0, _bh(ZR), ZR - 4), (0, _bh(ZR) + 230, ZR - 4), 2.4, STEELX, 3.6)
    e.cable('borda', [(4, _bh(ZR) + 226, ZR - 4), (5, _bh(ZR) + 20, ZR - 6)], ROPE, 2.6, gruix=0.6)


# ─── Les peces ───────────────────────────────────────────────────────────────

def _desp(x, z, h, dia):
    if dia:
        return SOL_D[0] * h * 0.5, SOL_D[1] * h * 0.5
    best = None
    for L in (LAMP_P, FOCUS_P):
        dx, dz = x - L[0], z - L[2]
        n = math.hypot(dx, dz) or 1
        if best is None or n < best[0]:
            best = (n, dx, dz)
    n, dx, dz = best
    k = h * 0.5 * min(1.0, 160 / n)
    return dx / n * k, dz / n * k


def caseta(e, tex, dia):
    """La caseta del passadís: el darrere (el dibuix pla, amb la porta), el costat d'estribord en escorç i el ràfec."""
    if dia:
        _ombra_caixa(e, CX0, CX1, CZ0, CZ1, CHT, SOL_D, 0.5)
    else:
        _ombra(e, (CX0 + CX1) / 2, CZ1 + 16, 100, 34, 0.6)
    hx0, hx1 = PL.HOUSE
    e.quad('caseta', (CX0, CHT, CZ0), (_tx(hx1 + 1), CHT, CZ0), (_tx(hx1 + 1), 0, CZ0), (CX0, 0, CZ0),
           tex=(tex['caseta'], (hx0, 29, hx1 + 1, PL.FLOOR_Y)))
    if _tx(hx1 + 1) < CX1:
        e.quad('caseta', (_tx(hx1 + 1), CHT, CZ0), (CX1, CHT, CZ0), (CX1, 0, CZ0), (_tx(hx1 + 1), 0, CZ0), ramp=HULLN,
               lvl=_planxa(1.8 if not dia else 2.4))
    e.quad('caseta_costat', (CX1, CHT, CZ0), (CX1, CHT, CZ1), (CX1, 0, CZ1), (CX1, 0, CZ0), ramp=HULLN,
           lvl=_planxa(1.6 if not dia else 2.2, seed=71))
    # un ull de bou al costat
    oz, oy = (CZ0 + CZ1) / 2 + 6, _ty(53)
    WIN = [(40, 26, 10), (110, 74, 28), (190, 140, 60), (240, 200, 110)]
    e.quad('caseta_costat', (CX1 + 1, oy + 10, oz - 10), (CX1 + 1, oy + 10, oz + 10), (CX1 + 1, oy - 10, oz + 10),
           (CX1 + 1, oy - 10, oz - 10), ramp=CABX, lvl=lambda s, t, P: 3.8 - s * 0.05,
           forma=lambda s, t: (s - 10) ** 2 + (t - 10) ** 2 < 100)
    e.quad('caseta_costat', (CX1 + 1.5, oy + 7, oz - 7), (CX1 + 1.5, oy + 7, oz + 7), (CX1 + 1.5, oy - 7, oz + 7),
           (CX1 + 1.5, oy - 7, oz - 7), ramp=CABX if dia else WIN,
           lvl=(lambda s, t, P: 4.6 - t * 0.2) if dia else (lambda s, t, P: 2.4 - t * 0.08),
           forma=lambda s, t: (s - 7) ** 2 + (t - 7) ** 2 < 49)
    # el ràfec i la barana
    e.caixa('caseta', CX0 - 10, CX1 + 12, CHT, CHT + 12, CZ0 - 10, CZ1 + 10, HULLN, 3.4,
            cares={'davant': {'ramp': HULLN, 'lvl': lambda s, t, P: 2.4 if 5 < t < 8 else 3.6},
                   'dreta': {'ramp': HULLN, 'lvl': lambda s, t, P: 2.6 if 5 < t < 8 else 4.0},
                   'sota': {'ramp': HULLN, 'lvl': 1.0}})
    for k in range(7):
        x = CX0 - 6 + k * (CX1 - CX0 + 14) / 6
        e.caixa('caseta', x - 1.2, x + 1.2, CHT + 12, CHT + 44, CZ0 - 7, CZ0 - 5, HULLN, 3.6)
    for k in range(7):
        z = CZ0 - 6 + k * (CZ1 - CZ0 + 12) / 6
        e.caixa('caseta', CX1 + 7, CX1 + 9, CHT + 12, CHT + 44, z - 1.2, z + 1.2, HULLN, 4.4)
    for hgt in (CHT + 28, CHT + 44):
        e.caixa('caseta', CX0 - 8, CX1 + 9, hgt - 1.5, hgt, CZ0 - 7, CZ0 - 5, HULLN, 3.8)
        e.caixa('caseta', CX1 + 7, CX1 + 9, hgt - 1.5, hgt, CZ0 - 7, CZ1 + 6, HULLN, 4.6)


GR = PL.GR


def molinet(e, tex, dia):
    """El molinet: la bancada, la caixa amb el dibuix pla al costat (el barbotí, el tambor, el fre) i la cadena."""
    mx, mz, ma = MOL
    _ombra(e, mx, mz, MOL_W, MOL_L * 0.6, 0.55, *_desp(mx, mz, MOL_H, dia))
    e.caixa_girada('molinet', mx, mz, MOL_W + 16, MOL_L + 16, 8, ma, STEELX, 2.6,
                   cares={'dalt': {'ramp': STEELX, 'lvl': lambda s, t, P: 3.6 + (1.2 if int(s) % 9 < 1 and int(t) % 9 < 1 else 0)}})
    box = (182, 145, 285, PL.FLOOR_Y + 10)
    e.caixa_girada('molinet', mx, mz, MOL_W, MOL_L, MOL_H, ma, GR, 2.4, y0=8,
                   cares={'dreta': {'tex': (tex['molinet'], box)},
                          'davant': {'ramp': GR, 'lvl': lambda s, t, P: 2.2 - (1.2 if int(t) % 6 < 1 and 8 < s < MOL_W - 8 else 0)},
                          'dalt': {'ramp': GR, 'lvl': lambda s, t, P: 3.6 + (1.0 if abs(s - MOL_W / 2) < 6 and abs(t - 40) < 4 else 0)},
                          'esquerra': {'ramp': GR, 'lvl': 1.6}})
    # la cadena: del barbotí (al costat d'estribord, a dalt) a l'escobenc, baula a baula
    c, s_ = math.cos(ma), math.sin(ma)

    def Pm(lx, y, lz):
        return (mx + lx * c - lz * s_, y, mz + lx * s_ + lz * c)
    a = Pm(MOL_W / 2 + 4, MOL_H - 6, MOL_L * 0.05)
    b = Pm(MOL_W / 2 + 6, 18, MOL_L * 0.5 + 20)
    pts = [a, b]
    ex, ez = ESCOBENC
    for i in range(1, 9):
        t = i / 8
        pts.append((b[0] + (ex - b[0]) * t, 2 + 2 * math.sin(t * math.pi), b[2] + (ez - 10 - b[2]) * t))
    acc = 0
    for A, B in zip(pts, pts[1:]):
        L = math.dist(A, B)
        n = max(1, int(L / 7))
        for k in range(n):
            P0 = tuple(A[j] + (B[j] - A[j]) * k / n for j in range(3))
            P1 = tuple(A[j] + (B[j] - A[j]) * (k + 0.8) / n for j in range(3))
            acc += 1
            e.cable('cadena', [P0, P1], PL.CHAIN, 3.8 if acc % 2 else 2.4, gruix=3.4 if acc % 2 else 2.2)
    # l'escobenc: la boca de ferro on la cadena se'n va
    e.quad('cadena', (ex - 16, 0.6, ez + 8), (ex + 16, 0.6, ez + 8), (ex + 16, 0.6, ez - 8), (ex - 16, 0.6, ez - 8),
           ramp=STEELX, lvl=lambda s, t, P: 3.8 if (s - 16) ** 2 / 256 + (t - 8) ** 2 / 64 > 0.5 else 0.5,
           forma=lambda s, t: (s - 16) ** 2 / 256 + (t - 8) ** 2 / 64 < 1)
    # el tub que baixa del molinet a la caixa de cadenes
    p = Pm(MOL_W / 2 + 10, 0.6, -MOL_L / 2 + 8)
    e.quad('cadena', (p[0] - 8, 0.6, p[2] + 6), (p[0] + 8, 0.6, p[2] + 6), (p[0] + 8, 0.6, p[2] - 6), (p[0] - 8, 0.6, p[2] - 6),
           ramp=STEELX, lvl=lambda s, t, P: 3.6 if (s - 8) ** 2 / 64 + (t - 6) ** 2 / 36 > 0.45 else 0.4,
           forma=lambda s, t: (s - 8) ** 2 / 64 + (t - 6) ** 2 / 36 < 1)


def escotilla(e, dia, cadenat=False):
    """L'escotilla de la caixa de cadenes: el brocal baix, la tapa d'antilliscant, les frontisses, la balda i la nansa."""
    hx, hz, hw, hd, ha = ESCO
    _ombra(e, hx, hz, hw * 0.6, hd * 0.6, 0.45, *_desp(hx, hz, 10, dia))
    e.caixa_girada('escotilla', hx, hz, hw, hd, 10, ha, STEELX, 2.4,
                   cares={'dalt': {'ramp': STEELX,
                                   'lvl': lambda s, t, P: 4.4 if (s < 4 or s > hw - 4 or t < 4 or t > hd - 4) else
                                   3.0 + (1.2 if (int(s / 5) + int(t / 5)) % 2 == 0 and int(s) % 5 < 2 and int(t) % 5 < 2 else 0)},
                          'davant': {'ramp': STEELX, 'lvl': 2.2}, 'dreta': {'ramp': STEELX, 'lvl': 1.6},
                          'esquerra': {'ramp': STEELX, 'lvl': 1.8}})
    c, s_ = math.cos(ha), math.sin(ha)

    def Pe(lx, lz):
        return hx + lx * c - lz * s_, hz + lx * s_ + lz * c
    for lx in (-hw / 2 + 16, hw / 2 - 26):                          # frontisses, al fons
        x, z = Pe(lx, hd / 2 - 4)
        e.caixa_girada('escotilla', x + 5, z, 12, 6, 4, ha, STEELX, 4.2, y0=10)
    x, z = Pe(10, -hd / 2 + 2)                                       # la balda, al davant
    e.caixa_girada('escotilla', x, z, 12, 5, 7, ha, STEELX, 4.4, y0=4)
    x, z = Pe(-18, -hd / 2 + 8)                                      # la nansa
    e.caixa_girada('escotilla', x, z, 16, 2, 3, ha, STEELX, 4.6, y0=10)
    if cadenat:
        x, z = Pe(10, -hd / 2 - 1)
        e.caixa_girada('cadenat', x, z, 9, 4, 9, ha, GOLD, 4.2, y0=-1,
                       cares={'davant': {'ramp': GOLD, 'lvl': lambda s, t, P: 5.2 if s < 3 and t < 3 else 4.0 - t * 0.2},
                              'dalt': {'ramp': GOLD, 'lvl': 5.0}})
        e.cable('cadenat', [(x - 3, 7.5, z), (x - 2, 11.5, z), (x + 2, 11.5, z), (x + 3, 7.5, z)], STEELX, 5.0, gruix=0.7)


BALSA_BOX = (414, 88, 546, PL.FLOOR_Y + 4)


def balsa(e, tex, dia):
    """La balsa: el contenidor blanc sobre el bressol, amb les cintes, el rètol i l'alliberador (el dibuix pla, dret:
    el cilindre és de través i es veu de costat)."""
    bx, bz = BALSA
    _ombra(e, bx, bz, 76, 30, 0.55, *_desp(bx, bz, 50, dia))
    x0, y0, x1, y1 = BALSA_BOX
    e.sprite('balsa', tex['balsa'].crop(BALSA_BOX), ((PL.BALSA[0] + PL.BALSA[2]) / 2 - x0, PL.FLOOR_Y + 3 - y0),
             (bx, 0, bz), escala_img=K)


def pal(e, tex, dia, img=None):
    """El pal de proa (el dibuix pla, dret: el tub, la creueta amb el focus, el llum de tope i la campana)."""
    px, pz = PAL
    _ombra(e, px, pz, 22, 12, 0.5, *_desp(px, pz, 30, dia))
    im = (img or tex['pal']).crop(MAST_BOX)
    e.sprite('pal', im, (PL.MX - MAST_BOX[0], PL.FLOOR_Y + 3 - MAST_BOX[1]), (px, 0, pz), escala_img=MAST_K)


def coses(e, dia):
    bx, bz = BITES
    _ombra(e, bx, bz, 30, 12, 0.5, *_desp(bx, bz, 30, dia))
    e.caixa('coses', bx - 9, bx + 9, 0, 5, bz - 26, bz + 26, HULLN, 2.0)
    for dz in (-15, 15):
        cilindre(e, 'coses', bx, bz + dz, 5.5, 5, 30, STEELX, lambda a, y, P: 2.6 + 1.4 * math.cos(a + 0.6), n=12)
        e.caixa('coses', bx - 6.5, bx + 6.5, 30, 33, bz + dz - 6.5, bz + dz + 6.5, STEELX, 4.0)
    for k in range(3):
        e.cable('coses', [(bx + 5, 12 + k * 4, bz - 15), (bx + 5, 14 + k * 4, bz + 15)], ROPE, 3.2, gruix=2.0)
    rx, rz = ROTLLO
    for k in range(6):
        r = 22 - k * 3
        e.quad('coses', (rx - r, 1 + k * 0.8, rz + r), (rx + r, 1 + k * 0.8, rz + r), (rx + r, 1 + k * 0.8, rz - r),
               (rx - r, 1 + k * 0.8, rz - r), ramp=ROPE,
               lvl=lambda s, t, P, r=r: 3.0 + (0.8 if int(math.hypot(s - r, t - r)) % 3 == 0 else 0) - (s - r) / r * 0.6,
               forma=lambda s, t, r=r: (r - 3.2) ** 2 < (s - r) ** 2 + (t - r) ** 2 < r * r)


def racó_juana(e, tex):
    """De dia: la caixa de peix per seure, amb la manta de quadres (el dibuix pla), i el coixí salvavides a terra."""
    mx, mz = MANTA
    _ombra(e, mx, mz, 36, 24, 0.5, *_desp(mx, mz, 50, True))
    box = (474, 176, 521, 227)
    w = (box[2] - box[0]) * K
    hgt = (box[3] - box[1]) * K
    BL = [(30, 14, 18), (60, 24, 30), (100, 38, 44), (140, 56, 56), (176, 84, 72), (206, 120, 96)]
    e.caixa_girada('manta', mx, mz, w, 40, hgt - 4, 0.2, BL, 3.0,
                   cares={'davant': {'tex': (tex['manta'], box)},
                          'dalt': {'ramp': BL, 'lvl': lambda s, t, P: 2.8 + (0.9 if (int(s) // 6 + int(t) // 5) % 2 else 0)},
                          'esquerra': {'ramp': BL, 'lvl': lambda s, t, P: 2.0 + (0.9 if (int(s) // 6 + int(t) // 5) % 2 else 0)},
                          'dreta': {'ramp': BL, 'lvl': lambda s, t, P: 1.6 + (0.9 if (int(s) // 6 + int(t) // 5) % 2 else 0)}})
    e.caixa_girada('manta', mx + 52, mz - 30, 28, 18, 11, -0.3, ORANGEB, 2.6,
                   cares={'dalt': {'ramp': ORANGEB, 'lvl': lambda s, t, P: 3.4 if not (8 < s < 10 or 18 < s < 20) else 5.0}})


def primer_pla(e):
    """A baix a la dreta, unes bites fosques amb l'amarra que hi fa voltes i se'n va per l'escobenc de la borda."""
    vx, vz = VENT
    e.caixa('primer_pla', vx - 16, vx + 16, 0, 8, vz - 50, vz + 50, FOSC, 1.8)
    for dz in (-30, 30):
        cilindre(e, 'primer_pla', vx, vz + dz, 12, 8, 70, FOSC, lambda a, y, P: 1.6 + 1.2 * math.cos(a + 2.6), n=16)
        cilindre(e, 'primer_pla', vx, vz + dz, 16, 70, 76, FOSC, lambda a, y, P: 2.4 + 1.0 * math.cos(a + 2.6), n=16)
    for k in range(4):                                               # l'amarra, en vuit
        e.cable('primer_pla', [(vx - 10, 24 + k * 10, vz - 36), (vx + 10, 30 + k * 10, vz + 36)], FOSC, 2.6, gruix=7)
        e.cable('primer_pla', [(vx + 10, 24 + k * 10, vz - 36), (vx - 10, 30 + k * 10, vz + 36)], FOSC, 2.2, gruix=7)
    e.cable('primer_pla', [(vx, 30, vz + 30), (vx + 60, 20, vz + 90), (XB - 4, BH - 10, vz + 160)], FOSC, 2.0, gruix=8)


VENT = (262, 470)


# ─── Composició ─────────────────────────────────────────────────────────────

def escena(cv, dia, estat=frozenset(), tex=None):
    tex = tex or _textures(dia)
    _cel(cv, dia)
    _mar(cv, dia)
    e = Escena(cv, CAM, _llums(dia), ambient=0.8 if dia else -0.5)
    pts = _borda_punts(-1) + list(reversed(_borda_punts(1)))
    zmin = min(p[1] for p in pts)
    # el terra: un rectangle gran, retallat per les bordes (forma)
    e.quad('terra', (-XB - 20, 0, ZR + 10), (XB + 20, 0, ZR + 10), (XB + 20, 0, zmin), (-XB - 20, 0, zmin), ramp=DECKX,
           lvl=_coberta(dia), forma=lambda s, t: abs(s - XB - 20) <= _bx(ZR + 10 - t) + 2)
    if not dia:
        lx, ly, lz = LAMP_P
        e.claror((lx - 160, 0.3, lz + 200), (lx + 220, 0.3, lz + 200), (lx + 220, 0.3, lz - 200), (lx - 160, 0.3, lz - 200),
                 GLOW_WARM, lambda s, t: 0.2 * max(0.0, 1 - math.hypot((s - 160) / 190, (t - 200) / 160)) ** 1.3)
        fx, fy, fz = FOCUS_P
        e.claror((fx - 300, 0.3, fz + 120), (fx + 160, 0.3, fz + 120), (fx + 160, 0.3, fz - 400), (fx - 300, 0.3, fz - 400),
                 GLOW_WARM, lambda s, t: 0.2 * max(0.0, 1 - math.hypot((s - 300) / 260, (t - 120) / 240)) ** 1.3)
    # la foscor arran de les bordes
    e.foscor('racons', (-XB, 0.4, ZC), (-XB + 40, 0.4, ZC), (-XB + 40, 0.4, -100), (-XB, 0.4, -100),
             lambda s, t: 0.45 * max(0.0, 1 - s / 40))
    e.foscor('racons', (XB - 40, 0.4, ZC), (XB, 0.4, ZC), (XB, 0.4, -100), (XB - 40, 0.4, -100),
             lambda s, t: 0.45 * max(0.0, s / 40))
    e.foscor('racons', (-XB, 0.4, ZR), (XB, 0.4, ZR), (XB, 0.4, ZC), (-XB, 0.4, ZC),
             lambda s, t: 0.5 * max(0.0, 1 - (_bx(ZR - t) - abs(s - XB)) / 40))
    bordes(e, tex)
    pal(e, tex, dia, tex.get('pal_swing'))
    molinet(e, tex, dia)
    coses(e, dia)
    balsa(e, tex, dia)
    if dia:
        racó_juana(e, tex)
    escotilla(e, dia, 'cadenat' in estat)
    caseta(e, tex, dia)
    primer_pla(e)
    return e


def _render(dia, estat=frozenset(), tex=None):
    cv = Canvas(light=LIGHT)
    e = escena(cv, dia, estat, tex)
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)
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


def cadenat(cv):
    img, _ = _render(False, frozenset({'cadenat'}))
    cv.img.alpha_composite(_diff(img, _base(False)[0]))
    cv.P = cv.img.load()


PROPS = {'dia': dia, 'cadenat': cadenat}


# ─── Animacions: el mar i el cap de la campana que es gronxa ─────────────────

SWING = PL.SWING


def _sprite_capa(e, sid, img, peu_img, peu, escala_img=1.0):
    """Un fotograma d'un dibuix pla dret (un sprite de l'escena), on aquell sprite és el que es veu."""
    from PIL import Image
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
            if 0 <= X < W_ and e.amo[Y * W_ + X] in (idx, 0) and src[x, y][3] >= 128:
                dst[X, Y] = src[x, y]
    return out


def _punts_mar(dia):
    _, e = _base(dia)
    return [(x, y) for y in range(HOR + 1, BOTTOM) for x in range(W) if e.amo[y * W + x] == 0]


@functools.lru_cache(maxsize=None)
def _campanes(dia):
    """Per a cada gronxada, la capa del pal amb el cap de la campana en aquella posició (i el cel de darrere)."""
    img, e = _base(dia)
    out = {}
    for dx in set(SWING):
        if dx == 0:
            continue
        lay = _sprite_capa(e, 'pal', _pal_img(dia, dx).crop(MAST_BOX), (PL.MX - MAST_BOX[0], PL.FLOOR_Y + 3 - MAST_BOX[1]),
                           (PAL[0], 0, PAL[1]), MAST_K)
        out[dx] = lay
    return out


def _frames(dia):
    base, _ = _base(dia)
    sea = frames_mar(base, _punts_mar(dia), lambda cv, ph: _mar(cv, dia, ph))
    lays = _campanes(dia)
    _, e = _base(dia)
    # on hi ha el pal: es torna a pintar el pal quiet (dx 0) i, damunt, el de la gronxada
    still = _sprite_capa(e, 'pal', _textures(dia)['pal'].crop(MAST_BOX), (PL.MX - MAST_BOX[0], PL.FLOOR_Y + 3 - MAST_BOX[1]),
                         (PAL[0], 0, PAL[1]), MAST_K)
    frames = []
    for i, fr in enumerate(sea):
        dx = SWING[i % len(SWING)]
        if dx:
            full = base.copy()
            full.alpha_composite(fr)
            sp = still.load()
            pp = full.load()
            # (el cap de la campana: on el pal quiet era transparent i ara hi ha corda, o al revés, es repinta el fons)
            lay = lays[dx]
            lp = lay.load()
            for y in range(lay.height):
                for x in range(lay.width):
                    a, b = sp[x, y], lp[x, y]
                    if a != b:
                        if b[3]:
                            pp[x, y] = b
                        else:
                            pp[x, y] = base.getpixel((x, y))
            fr = _diff(full, base)
        frames.append(fr)
    return frames


ANIMS = {'mar': {'frames': lambda: _frames(False), 'frameDuration': 260},
         'dia_mar': {'frames': lambda: _frames(True), 'frameDuration': 260}}


# ─── Geometria ───────────────────────────────────────────────────────────────

def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


def _llum_pj(P, radius, color, intensity, **kw):
    """Una llum del món (x, y, z), a la pantalla: una llum dels personatges (`characterLights`)."""
    u, v = _p(P[0], P[2], P[1])
    return {'x': u, 'y': v, 'radius': radius, 'color': color, 'intensity': intensity, **kw}


def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


def _v(z, x=0.0):
    return round(CAM.projecta((x, 0, z))[1])


def _amo(ids):
    def mask(x, y):
        _, e = _base(False)
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


FRONT = [
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20, 'variants': ('dia',)},
    {'id': 'davant_caseta', 'mask': _amo({'caseta', 'caseta_costat'}), 'baseline': _v(CZ1, CX1), 'zIndex': 20, 'variants': ('dia',)},
    {'id': 'davant_molinet', 'mask': _amo({'molinet'}), 'baseline': _v(MOL[1] - MOL_L / 2, MOL[0]), 'zIndex': 20, 'variants': ('dia',)},
    {'id': 'davant_balsa', 'mask': _amo({'balsa'}), 'baseline': _v(BALSA[1] - 22, BALSA[0]), 'zIndex': 20, 'variants': ('dia',)},
    {'id': 'davant_pal', 'mask': _amo({'pal'}), 'baseline': _v(PAL[1], PAL[0]), 'zIndex': 20, 'variants': ('dia',)},
]

V_PROP = 256
_NL, _NR = _raig(CAM, 0, V_PROP, 0), _raig(CAM, W - 1, V_PROP, 0)
Z_FONS = 930                                       # fins on es camina, cap a proa


def _walk_mon():
    pts = [(_NL[0], _NL[2]), (-XB + 26, _NL[2] + 30)]
    zs = [ZC + (Z_FONS - ZC) * i / 4 for i in range(5)]
    pts += [(-XB + 26, ZC)] + [(-(_bx(z) - 30), z) for z in zs[1:]]
    pts += [(_bx(z) - 30, z) for z in reversed(zs[1:])] + [(XB - 26, ZC), (_NR[0], _NR[2])]
    return pts


_WALK = [(min(W - 1, max(0, u)), v) for u, v in (_p(x, z) for x, z in _walk_mon())]
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)


def _caixa_mon(cx, cz, w, d, ang, m=0):
    c, s_ = math.cos(ang), math.sin(ang)
    return [_p(cx + lx * c - lz * s_, cz + lx * s_ + lz * c) for lx, lz in
            ((-w / 2 - m, -d / 2 - m), (w / 2 + m, -d / 2 - m), (w / 2 + m, d / 2 + m), (-w / 2 - m, d / 2 + m))]


_FORATS = [[_p(CX0 - 12, CZ0 - 14), _p(CX1 + 14, CZ0 - 14), _p(CX1 + 14, CZ1 + 12), _p(CX0 - 12, CZ1 + 12)],
           _caixa_mon(MOL[0], MOL[1], MOL_W + 16, MOL_L + 16, MOL[2], 14),
           _caixa_mon(ESCO[0], ESCO[1], ESCO[2], ESCO[3], ESCO[4], 8),
           _caixa_mon(BALSA[0], BALSA[1], 110, 56, 0, 10)]

GEOMETRIA = {
    'things': {
        'popa': {'rect': (0, 120, 30, BOTTOM), 'walk': _p(_NL[0] + 20, _NL[2] + 20)},
        'porta': {'rect': _rect_mon((DOOR[0], DOOR[3], CZ0), (DOOR[1], DOOR[2], CZ0)),
                  'walk': _p((DOOR[0] + DOOR[1]) / 2, CZ0 - 40)},
        'balsa': {'rect': _rect_mon(*[(BALSA[0] + dx, y, BALSA[1] + dz) for dx in (-66, 66) for dz in (-30, 30)
                                      for y in (0, BALSA_Y + BALSA_R)]),
                  'walk': _p(BALSA[0] - 40, BALSA[1] - 70)},
        'molinet': {'rect': _rect_mon(*[(x, y, z) for x, z in ((MOL[0] - 40, MOL[1] - 70), (MOL[0] + 40, MOL[1] + 70))
                                        for y in (0, MOL_H + 8)] + [(MOL[0] + 40, 0, MOL[1] - 70)]),
                    'walk': _p(MOL[0] + 70, MOL[1] - 60)},
        'escotilla': {'rect': _rect_mon(*[(ESCO[0] + dx, y, ESCO[1] + dz) for dx in (-50, 50) for dz in (-34, 34)
                                          for y in (0, 12)]),
                      'walk': _p(ESCO[0], ESCO[1] - 66)},
    },
    'spawns': {'iri': _p(60, 470), 'vet': _p(-60, 470), 'juana': _p(MANTA[0] - 30, MANTA[1] - 56)},
    'walkable': _WALK,
    'forats': _FORATS,
    'floorSquash': 0.27,
    'characterShadow': {'enabled': True, 'color': '#0a0e16', 'alpha': 0.42, 'squash': 0.3, 'core': 0.6,
                        'light': {'x': 1, 'y': 0.18, 'direction': True, 'stretch': 0.5}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round((_V_FONS - 2 - HOR) / CAM_Y, 3), 'scaleBottom': round((_V_PROP + 2 - HOR) / CAM_Y, 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    # La llum de la sala sobre els personatges (les de _llums, a la pantalla): de nit, la claror freda de la lluna i
    # el mar, el focus càlid de la porta de la caseta i el del pal, que il·lumina la coberta des de dalt.
    'characterLights': {
        'ambient': '#7484a2',
        'lights': [
            _llum_pj(LAMP_P, 250, '#ffd28c', 0.7),                                        # el focus de la porta
            _llum_pj(FOCUS_P, 330, '#ffe2b0', 0.6),                                       # el focus del pal
        # de dia (el decorat `dia`): el sol, alt; gairebé igual a tota la coberta, i treu el blau de la nit
        {'x': W // 2, 'y': 200, 'radius': 4000, 'power': 1.0, 'color': '#ffe4b0', 'intensity': 0.56,
         'whenPropVisible': 'dia'},
        ],
    },
}
