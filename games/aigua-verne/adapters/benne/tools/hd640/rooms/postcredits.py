"""
Aigua Verne — `postcredits` (L): la plaça de Ferrum, temps després. La font pública raja per a totes. EN 3D
(hd640/tres_d.py), a 1×.

Una càmera alta, girada una mica cap a la dreta i mirant avall (picat), cap a una cantonada de la plaça: a l'esquerra
la paret d'una casa fuig cap a la càmera, i al fons la fila de cases de maó ennegrit (amb les teulades de pissarra i
les xemeneies que fumen) fuig cap a la dreta. Entre les cases hi entra un carrer que s'allunya cap a les escombreres,
el castellet de la mina i la Canonada, que puja fins a dalt del cel. Ja ha plogut: el cel de fum és més clar, les
llambordes són molles i fan tolls que fan de mirall. Una tira de banderetes de festa travessa la plaça.

A la paret del fons, el rètol pintat a mà AIGUA PER A TOTES i el panell nou «AIGUA VESPER · 4 ▲». La font (la de
Verne, blanca, amb el lector de targetes tapat amb un cartró i cinta) és al fons, a prop de la cantonada, i raja; la
pica plena i el terra mullat, amb un rierol cap a la claveguera. La cua de la gent del barri que hi espera torn
(miners, dones amb mocador, un vell, canalla: figures de fons de ferrum_gent.py, no sprites ni es cliquen) surt de la
font i ve cap a la càmera, en diagonal: les figures del fons són petites i les de prop, grans; la primera omple una
garrafa. Ningú no fa el mateix alhora (l'animació `cua`: un es gira a fer petar
la xerrada, la canalla no s'està quieta, un altre canvia la garrafa de mà).

Al final de la cua hi van, com a sprites, la Rosa i en Verne (amb en Dividend): aquí no es dibuixen. Passen per
darrere del fanal del mig de la plaça. Primer pla, fosc i tallat per la vora: un fanal de ferro a l'esquerra, i
caixes, un barril i garrafes buides a la dreta.

La llum: el sol, baix a la dreta i una mica al fons; la paret de l'esquerra hi toca de ple i la del fons de biaix, i
les ombres (les de la cua i la dels personatges) cauen cap a l'esquerra i cap a la càmera.

ANIMS: `aigua` (el raig de la font i les esquitxades a la pica), `fum` (les xemeneies) i `cua` (la cua, que es mou).

El món: x a la dreta, y amunt, z cap al fons (z = 820: les cases del fons); 1 unitat = 1 px de sala on un personatge
fa la seva mida normal. Les façanes planes es posen a ×1,25.
"""
import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

import functools
import math

from hd.pix import Canvas, Light, W, H, hr
from hd.rooms.comu import _diff
from hd.rooms.exterior import fbm, smooth
from hd640.rooms import postcredits_pla_comu as PL
from hd640.rooms.ferrum_comu import (
    SOOT, MORTAR, COB, COAL, IRONF, RUSTF, PLANKF, WHITEV, BLUEV, CLOTH, REDP, WATER, SLAGF,
    smog_sky, canonada, far_skyline, brick_lvl, finestres_enceses, llum_finestra, bassa_fanal, con_fanal,
    fanal_paret, GLOWF)
from hd640.rooms.ferrum_carrer import _maons
from hd640.rooms.ferrum_gent import persona_c
from hd640.rooms.ferrum_carrer_pla_comu import _smoke_loop
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259
CAM = Camera(pos=(0, 200, 0), yaw=0.22, pitch=0.06, f=540, centre=(320, 62))
KF = 1.25                                          # unitats del món per píxel del pla, a les façanes

ZB = 820.0                                         # el pla de les cases del fons
XC = -70.0                                         # la cantonada (la paret de l'esquerra és a x = XC)
FX0 = -4                                           # el primer píxel del pla de les cases


def _fx(fx):
    """Un x del pla de les cases → x del món."""
    return XC + (fx - FX0) * KF


CARRER = (_fx(420) + 6, _fx(420) + 116)            # el carrer que entra a la plaça (x0, x1)
DX4 = CARRER[1] - _fx(500)                         # la casa de després del carrer, desplaçada
Z4 = ZB - 24
FONT = (41.0, 727.0)                               # la font (x, z)
FANAL = (389.0, 538.0)                             # el fanal del mig de la plaça
FANAL_PP = (-112.0, 400.0)                          # el fanal del primer pla
ROSA, VERNE, DIVIDEND = (237.0, 473.0), (274.0, 449.0), (295.0, 435.0)

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)       # (la llum és la del món: la de l'Escena)
SOL = (9000.0, 3200.0, 2600.0)                     # el sol, baix a la dreta i una mica al fons
LLUMS = [Llum(SOL, 1e6, 2.2, power=1.0)]
AMBIENT = -1.1
_D = (-SOL[0], -SOL[2])
_n = math.hypot(*_D)
OMBRA = (_D[0] / _n, _D[1] / _n)                   # cap on cauen les ombres, al terra (x, z)
OMBRA_K = 1.5                                      # llargada de l'ombra per unitat d'alçada (el sol és baix)

TEXL = PL.TEXL
FLAGS = [REDP, [(50, 36, 6), (110, 80, 10), (180, 136, 20), (230, 190, 50), (250, 230, 120)], BLUEV, CLOTH]


# ─── Les textures: la plaça plana ───────────────────────────────────────────

def _pla(fn):
    cv = Canvas(light=TEXL, transparent=True)
    fn(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _textures():
    return {'cases': _pla(PL.cases), 'font': _pla(PL.font)}


# ─── Utilitats del món ────────────────────────────────────────────────────────

def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


def ombra(e, x, z, r, alt, k=0.6, sid='ombres'):
    """L'ombra d'una cosa d'alçada `alt` dreta a (x, z): una taca allargada cap on cauen les ombres."""
    dx, dz = OMBRA
    nx, nz = -dz, dx
    L = r + alt * OMBRA_K
    A = (x - dx * r - nx * r, 0.4, z - dz * r - nz * r)
    B = (A[0] + dx * (L + r), 0.4, A[2] + dz * (L + r))
    D = (x - dx * r + nx * r, 0.4, z - dz * r + nz * r)
    C = (B[0] + D[0] - A[0], 0.4, B[2] + D[2] - A[2])

    def fn(s, t):
        a = 1 - ((t - r) / r) ** 2 * (0.4 + 0.6 * min(1.0, s / (2 * r)))
        return k * max(0.0, a) * 1.6 * max(0.0, 1 - max(0.0, s - r) / (L + 1)) ** 0.7
    e.foscor(sid, A, B, C, D, fn)


# ─── El cel i el fons (en pantalla) ─────────────────────────────────────────

def _hor_carrer():
    """On s'acaba el carrer del fons, a la pantalla: (u, v)."""
    return _p((CARRER[0] + CARRER[1]) / 2, 4200)


def fons(cv):
    u, v = _hor_carrer()
    smog_sky(cv, v + 4, sun=(626, 26), seed=17, bright=1.0)        # ja ha plogut: més clar
    far_skyline(cv, v + 2, x0=max(0, u - 120), x1=min(W - 1, u + 120), seed=19,
                headframes=((u - 18, v + 1, 46),), chimneys=((u + 34, v + 2, v - 60, 3),))
    canonada(cv, u + 10, v - 2)


# ─── El terra (en el món) ─────────────────────────────────────────────────────

def _mullat(x, z):
    """Com de mullat és el terra (0..1): els tolls, i el voltant de la font."""
    d = math.hypot((x - FONT[0]) / 120, (z - FONT[1]) / 70)
    w = max(0.0, 1 - d) * 1.4
    w += smooth(0.6, 0.7, fbm(x / 160, z / 120, 33))
    return min(1.0, w)


def _terra(s, t, P):
    """Llambordes de pedra fosca, molles: files al llarg de x, grans a prop i petites al fons."""
    x, z = P[0], P[2]
    far = smooth(1400, 3000, z)
    carrer = CARRER[0] < x < CARRER[1] and z > ZB
    a, b = (z, x) if carrer else (x, z)
    rh = 11.0
    row = int(b // rh)
    off = 9.0 if row % 2 else 0.0
    col = int((a + off) // 18.0)
    fa, fb = ((a + off) % 18.0) / 18.0, (b % rh) / rh
    v = 3.0 + (hr(row, col, 5) - 0.5) * 1.1 + (fbm(x / 90, z / 60, 6) - 0.5) * 1.2
    if fb < 0.16 or fa < 0.09:
        v -= 1.7 * (1 - far)
    elif fb < 0.4:
        v += 0.6 * (1 - far)
    v -= _mullat(x, z) * 0.7                                        # el terra mullat, més fosc
    return v * (1 - far * 0.4) + 2.6 * far * 0.4


def tolls(e):
    """Els tolls fan de mirall: el cel clar s'hi reflecteix, i el rierol de la font cap a la claveguera."""
    def fn(s, t):
        x, z = -800 + s, 200 + t
        m = smooth(0.66, 0.72, fbm(x / 160, z / 120, 33))
        d = math.hypot((x - FONT[0]) / 80, (z - FONT[1]) / 46)
        m = max(m, smooth(1.0, 0.7, d))
        if m <= 0:
            return 0
        streak = 0.2 if (int(x / 3) + int(z / 9)) % 5 == 0 else 0
        return m * (0.32 + streak)
    e.claror((-800, 0.3, 1600), (1600, 0.3, 1600), (1600, 0.3, 200), (-800, 0.3, 200), (176, 146, 122),
             lambda s, t: fn(s, 1400 - t))
    # el rierol, que surt del desguàs de la font i baixa en diagonal cap a la reixa de la claveguera
    pts = []
    for k in range(28):
        t = k / 27
        pts.append((FONT[0] + 26 + t * 230 + math.sin(t * 9) * 6, 0.6, FONT[1] - 4 - t * 150))
    e.cable('rierol', pts, WATER, 3.0, gruix=1.4)
    gx, gz = pts[-1][0], pts[-1][2]
    e.caixa('reixa', gx - 12, gx + 12, 0, 0.5, gz - 6, gz + 6, IRONF, 1.4,
            cares={'dalt': {'ramp': IRONF, 'lvl': lambda s, t, P: 0.6 if s % 4 < 1.6 else 2.4}})


# ─── Les parets ──────────────────────────────────────────────────────────────

def _teulada(e, x0, x1, top, z, fons=96, alt=48):
    e.quad('teulada', (x0 - 4, top + alt, z + fons), (x1 + 4, top + alt, z + fons), (x1 + 4, top - 1, z - 6),
           (x0 - 4, top - 1, z - 6), ramp=PL.SLATE,
           lvl=lambda s, t, P: 3.4 - (1.3 if t % 7 < 1.3 else 0) - (0.8 if (s + (t // 7) * 5) % 11 < 1 else 0)
           + (fbm(s / 14, t / 8, 21) - 0.5) * 0.9 + (0.6 if t < 4 else 0) - max(0.0, 1 - t / 30) * 0.0)


def _xemeneia(e, x, top, z):
    e.caixa('xemeneies', x - 7, x + 7, top - 10, top + 30, z + 40, z + 54, SOOT, 3.0,
            cares={'davant': {'ramp': SOOT, 'lvl': lambda s, t, P: brick_lvl(int(s), int(t), 0, 0, 7, 3, 3.0, 4)
                              - max(0.0, 1 - t / 10) * 1.8},
                   'dalt': {'ramp': COAL, 'lvl': 0.6}})
    e.caixa('xemeneies', x - 3, x + 2, top + 30, top + 35, z + 44, z + 49, RUSTF, 2.8)


XEMENEIES = []                                     # (x, y de dalt, z) del broc de cada xemeneia: d'on surt el fum


def cases(e, tex):
    """La fila de cases del fons (les del pla), amb el carrer que hi entra, i la paret de l'esquerra."""
    T = tex['cases']
    XEMENEIES.clear()
    # la paret de l'esquerra: una casa llarga que ve cap a la càmera, amb el sol de cara
    hl = 196.0
    e.quad('paret_esq', (XC, hl, 200), (XC, hl, ZB), (XC, 0, ZB), (XC, 0, 200), ramp=SOOT,
           lvl=_maons(2.9, 61, finestres=((60, 40, 26, 34, False), (160, 40, 26, 34, True), (290, 40, 26, 34, False),
                                          (430, 40, 26, 34, False), (100, 118, 28, 38, False),
                                          (360, 118, 28, 38, True), (500, 118, 28, 38, False))))
    e.quad('paret_esq', (XC + 3, hl + 6, 200), (XC + 3, hl + 6, ZB + 3), (XC + 3, hl, ZB + 3), (XC + 3, hl, 200),
           ramp=MORTAR, lvl=4.0)
    e.quad('teulada', (XC - 90, hl + 50, 200), (XC - 90, hl + 50, ZB + 4), (XC + 6, hl + 2, ZB + 4),
           (XC + 6, hl + 2, 200), ramp=PL.SLATE,
           lvl=lambda s, t, P: 3.6 - (1.3 if t % 7 < 1.3 else 0) + (fbm(s / 14, t / 8, 23) - 0.5) * 0.9)
    _xemeneia(e, XC - 30, hl + 20, 480)
    XEMENEIES.append((XC - 30.5, hl + 55, 527))
    # les cases del fons (del pla): cada una a la seva alçada, amb la teulada i una xemeneia
    for i, (x0, x1, top, seed, door, wins, lit) in enumerate(PL.CASES):
        dx, z = (DX4, Z4) if x0 >= 500 else (0.0, ZB + (8 if i == 1 else 0))
        X0, X1 = _fx(max(FX0, x0)) + dx, _fx(x1) + dx
        h = (PL.BASE - top + 1) * KF
        e.quad('cases', (X0, h, z), (X1, h, z), (X1, 0, z), (X0, 0, z), tex=(T, (max(FX0, x0), top - 1, x1, PL.BASE)))
        _teulada(e, X0, X1, h, z)
        cx = X0 + (X1 - X0) * (0.3 + 0.4 * hr(i, 9))
        _xemeneia(e, cx, h + 10, z)
        XEMENEIES.append((cx - 0.5, h + 45, z + 47))
    # el costat de la casa de després del carrer (dona al carrer, a l'ombra)
    h4 = (PL.BASE - PL.CASES[3][2] + 1) * KF
    e.quad('cases', (CARRER[1], h4, Z4), (CARRER[1], h4, ZB + 200), (CARRER[1], 0, ZB + 200), (CARRER[1], 0, Z4),
           ramp=SOOT, dues_cares=True,
           lvl=_maons(2.0, 71, finestres=((40, 40, 18, 24, False), (120, 40, 18, 24, False))))
    # més enllà, cap a la dreta: un magatzem llarg
    X5 = _fx(640) + DX4
    e.quad('cases', (X5, 210, Z4 + 6), (X5 + 1400, 210, Z4 + 6), (X5 + 1400, 0, Z4 + 6), (X5, 0, Z4 + 6), ramp=SOOT,
           lvl=_maons(2.8, 81, finestres=tuple((30 + k * 80, 50, 30, 40, k == 1) for k in range(16)), bw=12))
    e.quad('cases', (X5, 216, Z4 + 2), (X5 + 1400, 216, Z4 + 2), (X5 + 1400, 210, Z4 + 2), (X5, 210, Z4 + 2),
           ramp=MORTAR, lvl=3.6)


def carrer(e):
    """El carrer que entra a la plaça, cap al fons: cases a les dues bandes, cada una d'una alçada, amb la boira."""
    for side, x in ((1, CARRER[0]), (-1, CARRER[1])):
        z = ZB + (0 if side > 0 else 200)
        i = 0
        while z < 4200:
            w = 150 + hr(i, side, 1) * 110
            h = 140 + hr(i, side, 2) * 70
            P = ((x, h, z), (x, h, z + w), (x, 0, z + w), (x, 0, z))
            if side > 0:                                             # (la cara que mira cap al carrer)
                P = (P[1], P[0], P[3], P[2])
            e.quad('carrer', *P, ramp=SOOT, dues_cares=True,
                   lvl=_maons(2.8 - min(1.2, z / 3200), 90 + i + side,
                              finestres=tuple((16 + k * 44, 36 + j * 50, 16, 22, hr(i, k, j, side) > 0.8)
                                              for k in range(int(w // 44) - 1) for j in range(2))))
            z += w
            i += 1


def rerefons(e):
    """Les teulades de Ferrum per darrere de la plaça (la càmera és alta i hi veu per sobre): files de cases que
    s'empetiteixen i es perden en la boira de fum, a banda i banda del carrer."""
    for r, z in enumerate((1060.0, 1380.0, 1760.0, 2240.0, 2900.0)):
        for xa, xb in ((-2600.0, CARRER[0] - 4), (CARRER[1] + 4, 4200.0)):
            x = xa - hr(r, 3) * 120
            i = 0
            while x < xb:
                w = min(xb - x, 120 + hr(r, i, 1) * 160)
                h = 120 + hr(r, i, 2) * 60 - r * 6                      # (per sota de l'horitzó: es veu el cel)
                fosc = 2.6 - r * 0.25
                e.quad(f'rerefons{r}', (x, h, z), (x + w, h, z), (x + w, 0, z), (x, 0, z), ramp=SOOT,
                       lvl=_maons(fosc, 200 + r * 31 + i,
                                  finestres=tuple((14 + k * 40, 30, 14, 20, hr(r, i, k) > 0.85)
                                                  for k in range(int(w // 40) - 1))))
                e.quad(f'rerefons{r}', (x - 3, h + 40, z + 70), (x + w + 3, h + 40, z + 70), (x + w + 3, h, z - 3),
                       (x - 3, h, z - 3), ramp=PL.SLATE,
                       lvl=lambda s, t, P, r=r: 3.0 - r * 0.2 - (1.2 if t % 7 < 1.3 else 0))
                if hr(r, i, 5) > 0.55:
                    cx = x + w * (0.2 + 0.6 * hr(r, i, 6))
                    e.caixa(f'rerefons{r}', cx - 6, cx + 6, h, h + 40, z + 20, z + 32, SOOT, 2.4 - r * 0.2)
                x += w + (hr(r, i, 4) * 30 if hr(r, i, 7) > 0.7 else 0)
                i += 1
    # la boira de fum: com més lluny, més es confon amb el cel
    P, amo, ids = e.cv.P, e.amo, e.ids
    k_id = {i: 0.1 + 0.09 * int(sid[8:]) for i, sid in enumerate(ids) if sid.startswith('rerefons')}
    for i, a in enumerate(amo):
        k = k_id.get(a)
        if k:
            X, Y = i % e.cv.w, i // e.cv.w
            o = P[X, Y]
            P[X, Y] = (int(o[0] + (150 - o[0]) * k), int(o[1] + (120 - o[1]) * k), int(o[2] + (100 - o[2]) * k), 255)


# ─── La font, les banderetes ────────────────────────────────────────────────────

def font(e, tex):
    ombra(e, FONT[0], FONT[1], 22, 70, 0.5)
    fx, fy = PL.FONT
    e.sprite('font', tex['font'].crop((fx - 26, fy - 78, fx + 26, fy + 4)), (26, 78), (FONT[0], 0, FONT[1]))


def banderetes(e):
    """Una tira de banderetes de festa travessant la plaça, de la paret de l'esquerra a la casa del rètol."""
    A = (XC + 1, 172, 470)
    B = (_fx(244), 132, ZB + 7)
    n = 26
    pts = []
    for k in range(n + 1):
        t = k / n
        pts.append((A[0] + (B[0] - A[0]) * t, A[1] + (B[1] - A[1]) * t - math.sin(t * math.pi) * 44,
                    A[2] + (B[2] - A[2]) * t))
    e.cable('banderetes', pts, COAL, 1.0, gruix=0.8)
    for k in range(1, n):
        x, y, z = pts[k]
        ramp = FLAGS[k % 4]
        e.quad('banderetes', (x - 5, y, z), (x + 5, y, z), (x + 5, y - 12, z), (x - 5, y - 12, z), ramp=ramp,
               lvl=lambda s, t, P: 3.6 - t * 0.08, dues_cares=True,
               forma=lambda s, t: abs(s - 5) <= 5 * (1 - t / 12) + 0.3)


# ─── La cua ─────────────────────────────────────────────────────────────────────
# De la font cap a la càmera, en diagonal; l'última, abans de la Rosa. (x, z, alçada, var, extra, gestos)
# `gestos`: {fotograma: canvis} de l'animació `cua` (cadascú al seu ritme).

_CUA0 = (FONT[0] + 30, FONT[1] - 26)              # el primer de la cua (el segon: la primera omple la garrafa)
_CUA1 = (207.0, 507.0)                             # l'últim, just davant de la Rosa


def _lloc(i, n=8):
    """El lloc i-èssim de la cua (de la font cap a la càmera), amb una mica de corba i de desordre."""
    t = i / (n - 1)
    x = _CUA0[0] + (_CUA1[0] - _CUA0[0]) * t + math.sin(t * math.pi) * 18 + (hr(i, 41) - 0.5) * 8
    z = _CUA0[1] + (_CUA1[1] - _CUA0[1]) * t + (hr(i, 42) - 0.5) * 8
    return x, z


CUA = [
    (FONT[0] - 32, FONT[1] - 4, 76, 0, dict(tipus='dona', facing=1, hold='bidon'), {}),                 # omple la garrafa
    (*_lloc(0), 81, 0, dict(tipus='miner', hold='bidon'), {3: dict(facing=1), 4: dict(facing=1)}),
    (*_lloc(1), 58, 1, dict(tipus='nen', lamp=False), {1: dict(facing=1), 6: dict(facing=1), 7: dict(facing=1)}),
    (*_lloc(2), 79, 1, dict(tipus='dona', facing=1), {5: dict(facing=-1), 6: dict(facing=-1)}),     # fa petar la xerrada
    (*_lloc(3), 78, 2, dict(tipus='miner', cua=True, hold='butxaca'), {}),
    (*_lloc(4), 77, 1, dict(tipus='vell', hold='bidon'), {2: dict(hold='got'), 3: dict(hold='got')}),
    (*_lloc(5), 52, 0, dict(tipus='nena'), {0: dict(facing=1), 4: dict(facing=1)}),
    (*_lloc(6), 82, 3, dict(tipus='miner', hold='bidon', lamp=False), {7: dict(facing=1)}),
    (*_lloc(7), 77, 3, dict(tipus='dona', hold='bidon'), {}),
]
CUA_N = 8


@functools.lru_cache(maxsize=None)
def _figura(h, var, kw):
    cv = Canvas(70, 110, light=TEXL, transparent=True)
    k = dict(facing=-1, light_from=1)
    k.update(dict(kw))
    persona_c(cv, 35, 104, h=h, var=var, **k)
    return cv.img


def cua(e, f=None):
    for i, (x, z, h, var, ex, gestos) in sorted(enumerate(CUA), key=lambda p: -p[1][1]):
        ombra(e, x, z, 13 * h / 80, h, 0.45)
    for i, (x, z, h, var, ex, gestos) in sorted(enumerate(CUA), key=lambda p: -p[1][1]):
        kw = dict(ex)
        if f is not None:
            kw.update(gestos.get(f, {}))
        e.sprite(f'cua{i}', _figura(h, var, tuple(sorted(kw.items()))), (35, 104), (x, 0, z))


# ─── El primer pla i el fanal ───────────────────────────────────────────────────

def fanal(e, sid, x, z, alt=300, apagat=True):
    """Un fanal de ferro colat: la base, el pal, el braç i el llum."""
    e.caixa(sid, x - 4, x + 4, 0, alt, z - 4, z + 4, IRONF, 1.6,
            cares={'davant': {'ramp': IRONF, 'lvl': lambda s, t, P: 1.4 + (1.0 if int(P[1]) % 90 < 4 else 0)},
                   'dreta': {'ramp': IRONF, 'lvl': 2.6}, 'esquerra': {'ramp': IRONF, 'lvl': 1.0}})
    e.caixa(sid, x - 8, x + 8, 0, 20, z - 8, z + 8, IRONF, 1.8)
    e.caixa(sid, x - 40, x, alt - 6, alt - 2, z - 2, z + 2, IRONF, 1.8)
    e.caixa(sid, x - 50, x - 34, alt - 26, alt - 6, z - 8, z + 8, IRONF, 1.4,
            cares={'davant': ({'ramp': [(60, 50, 40), (110, 96, 70), (160, 140, 100)], 'lvl': 1.0} if apagat else
                              {'ramp': [(200, 120, 50), (255, 186, 80), (255, 236, 170)], 'lvl': 2.4})})


def primer_pla(e):
    # el fanal, molt a prop, a l'esquerra (tallat per dalt)
    fanal(e, 'primer_pla', FANAL_PP[0], FANAL_PP[1], alt=420)
    # caixes de fusta, un barril i garrafes buides, a la dreta i a baix (tallats per la vora)
    for (x, z, w, d, h, a, y0) in ((396, 392, 52, 36, 40, -0.3, 0), (388, 388, 40, 30, 30, -0.1, 40),
                                   (344, 366, 46, 34, 34, -0.5, 0)):
        e.caixa_girada('primer_pla', x, z, w, d, h, a, PLANKF, 1.4, y0=y0,
                       cares={'dalt': {'ramp': PLANKF, 'lvl': lambda s, t, P: 2.8 - (1.0 if int(t) % 7 == 0 else 0)},
                              'davant': {'ramp': PLANKF, 'lvl': lambda s, t, P: 1.2 - (0.8 if int(t) % 6 == 0 else 0)},
                              'dreta': {'ramp': PLANKF, 'lvl': 2.0}, 'esquerra': {'ramp': PLANKF, 'lvl': 0.8}})
    e.tub('primer_pla', (356, 0, 404), (356, 56, 404), 18, RUSTF, 1.6, brides=2)
    for k, (x, z) in enumerate(((330, 398), (318, 382), (340, 386))):
        e.caixa_girada('primer_pla', x, z, 14, 14, 22, 0.3 + k, WHITEV, 1.8,
                       cares={'dalt': {'ramp': BLUEV, 'lvl': 1.6}})
    for k, (x, z, r) in enumerate(((-96, 410, 14), (-78, 396, 10))):
        e.roca('primer_pla', (x, 0, z), r, COAL, 1.6, llum_dir=(0.7, -0.6), seed=k + 3)
    # en silueta: el primer pla, a contrallum i fora de la llum de la plaça, és fosc
    P, ids = e.cv.P, {i for i, sid in enumerate(e.ids) if sid == 'primer_pla'}
    for i, a in enumerate(e.amo):
        if a in ids:
            X, Y = i % e.cv.w, i // e.cv.w
            o = P[X, Y]
            P[X, Y] = (int(o[0] * 0.5), int(o[1] * 0.48), int(o[2] * 0.5), 255)


# ─── La llum càlida ─────────────────────────────────────────────────────────

def llum_finestres(e, tex):
    """La claror de les finestres enceses de les cases del fons, a les llambordes molles de davant."""
    T = tex['cases']
    for i, (x0, x1, top, seed, door, wins, lit) in enumerate(PL.CASES):
        dx, z = (DX4, Z4) if x0 >= 500 else (0.0, ZB + (8 if i == 1 else 0))
        box = (max(FX0, x0), top - 1, x1, PL.BASE)
        X0 = _fx(box[0]) + dx
        for fx0, fy0, fx1, fy1 in finestres_enceses(T, box):
            llum_finestra(e, X0 + (fx0 - box[0]) * KF, X0 + (fx1 - box[0]) * KF, (PL.BASE - fy1) * KF,
                          (PL.BASE - fy0) * KF, z, dx=-0.2, dz=1.8, k=0.55)


FANAL_ALT = 200
FANAL_CAP = (FANAL[0] - 42, FANAL_ALT - 16, FANAL[1])   # el llum del fanal del mig de la plaça
# els fanals de paret de les cases del fons (x, alçada, z de la façana): a la del rètol i a la del panell
FANALS_PARET = ((_fx(372), 100, ZB), (_fx(506) + DX4, 92, Z4))


def llum_fanal(e):
    """El fanal del mig de la plaça, encès: la bassa de llum a les llambordes i el con (abans de la cua: la gent
    hi passa per davant)."""
    x, _, z = FANAL_CAP
    bassa_fanal(e, x, z - 10, r=150, k=0.5)
    con_fanal(e, FANAL_CAP, r=80, k=0.2, salta=('primer_pla',))
    for x, y, z in FANALS_PARET:
        cap = fanal_paret(e, 'fanals', x, y, z, IRONF, GLOWF)
        bassa_fanal(e, x - 10, z - 80, r=110, k=0.55)
        con_fanal(e, cap, r=60, k=0.22, salta=('primer_pla',), terra=(x - 10, z - 80))


# ─── Composició ─────────────────────────────────────────────────────────────

def escena(cv, tex, amb_cua=True):
    e = Escena(cv, CAM, LLUMS, ambient=AMBIENT)
    fons(cv)
    e.quad('terra', (-80000, 0, 40000), (80000, 0, 40000), (80000, 0, 150), (-80000, 0, 150), ramp=COB, lvl=_terra)
    e.claror((-80000, 0.2, 40000), (80000, 0.2, 40000), (80000, 0.2, 1400), (-80000, 0.2, 1400), (160, 128, 104),
             lambda s, t: 0.6 * smooth(600, 7000, 40000 - t))
    rerefons(e)
    carrer(e)
    tolls(e)
    cases(e, tex)
    llum_finestres(e, tex)
    # la línia de les parets amb el terra: la foscor dels racons, i la vorera trencada
    e.foscor('racons', (XC, 0.5, ZB), (2000, 0.5, ZB), (2000, 0.5, ZB - 40), (XC, 0.5, ZB - 40),
             lambda s, t: 0.45 * max(0.0, 1 - t / 30) * (0.6 + 0.4 * fbm(s / 20, 0.3, 4)))
    e.foscor('racons', (XC, 0.5, 200), (XC, 0.5, ZB), (XC + 40, 0.5, ZB), (XC + 40, 0.5, 200),
             lambda s, t: 0.35 * max(0.0, 1 - t / 28))
    for k in range(7):                                              # sacs i trastos contra les parets
        x = _fx(20 + k * 92 + hr(k, 1) * 30)
        if CARRER[0] - 30 < x < CARRER[1] + 30:
            continue
        e.roca('trastos', (x, 0, ZB - 14 - hr(k, 2) * 10), 8 + hr(k, 3) * 6, SLAGF, 2.6, seed=20 + k)
    font(e, tex)
    llum_fanal(e)
    if amb_cua:
        cua(e)
    fanal(e, 'fanal', FANAL[0], FANAL[1], alt=FANAL_ALT, apagat=False)
    ombra(e, FANAL[0], FANAL[1], 8, FANAL_ALT, 0.35)
    u, v, _ = CAM.projecta(FANAL_CAP)
    cv.glow(u, v, 16, (255, 220, 160), 0.8)
    banderetes(e)
    primer_pla(e)
    return e


@functools.lru_cache(maxsize=None)
def _base():
    cv = Canvas(light=LIGHT)
    e = escena(cv, _textures())
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)    # sota la sala: negre
    return cv.img, e


def bg(cv):
    img, _ = _base()
    cv.img.paste(img)
    cv.P = cv.img.load()


PROPS = {}


# ─── Animacions ─────────────────────────────────────────────────────────────

def _sobre(fn, img=None):
    cv = Canvas(light=LIGHT, transparent=img is None, img=img)
    e = Escena(cv, CAM, LLUMS, ambient=AMBIENT)
    fn(e)
    return cv.img


def _frames_aigua():
    """El raig de la font: els fotogrames plans de sempre, posats a la font (a la seva mida)."""
    _, e0 = _base()
    fx, fy = PL.FONT
    out = []
    for fr in PL.frames_aigua(8):
        crop = fr.crop((fx - 26, fy - 78, fx + 26, fy + 4))

        def fn(e, crop=crop):
            e.sprite('aigua', crop, (26, 78), (FONT[0], 0, FONT[1]))
        img = _sobre(fn)
        # el que hi ha davant de la font (la cua) la continua tapant
        P, W_ = img.load(), e0.cv.w
        font_ids = {i for i, s in enumerate(e0.ids) if s in ('font', 'terra', 'tolls', 'ombres')}
        for y in range(img.height):
            for x in range(img.width):
                if P[x, y][3] and e0.amo[y * W_ + x] not in font_ids and e0.ids[e0.amo[y * W_ + x]] != '':
                    P[x, y] = (0, 0, 0, 0)
        out.append(img)
    return out


def _fonts_fum():
    out = []
    for P in XEMENEIES:
        u, v, _ = CAM.projecta(P)
        k = CAM.escala(P)
        out.append((u, v, 3 * k + 1, 40 * k))
    return out


def _frames_fum():
    base, _ = _base()
    return _smoke_loop(base, _fonts_fum(), 12)


@functools.lru_cache(maxsize=None)
def _base_sense_cua():
    cv = Canvas(light=LIGHT)
    escena(cv, _textures(), amb_cua=False)
    return cv.img


def _frames_cua():
    """La cua que es mou: cadascú fa el seu gest al seu moment (es redibuixa la cua i el que té davant)."""
    base, _ = _base()
    out = []
    for f in range(CUA_N):
        cv = Canvas(light=LIGHT, img=_base_sense_cua().copy())
        e = Escena(cv, CAM, LLUMS, ambient=AMBIENT)
        cua(e, f)
        fanal(e, 'fanal', FANAL[0], FANAL[1], alt=FANAL_ALT, apagat=False)
        banderetes(e)
        primer_pla(e)
        cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)
        out.append(_diff(cv.img, base))
    return out


ANIMS = {'aigua': {'frames': _frames_aigua, 'frameDuration': 90},
         'fum': {'frames': _frames_fum, 'frameDuration': 160},
         'cua': {'frames': _frames_cua, 'frameDuration': 520}}


# ─── Capes del davant ─────────────────────────────────────────────────────────

def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _v(x, z):
    return round(CAM.projecta((x, 0, z))[1])


FRONT = [
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20},
    {'id': 'davant_fanal', 'mask': _amo({'fanal'}), 'baseline': _v(*FANAL), 'zIndex': 20},
]


# ─── Geometria (coordenades de sala, projectades) ───────────────────────────────

def _escala_a(v):
    """L'escala d'un personatge amb els peus a la y de pantalla `v`."""
    lo, hi = 1.0, 40000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.projecta((300, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((300, 0, (lo + hi) / 2))


# El terra on es camina (al món): la part de la plaça de davant de la cua, fins al fanal; no arriba al primer pla.
WALK_MON = [(150, 640), (420, 600), (620, 470), (620, 380), (300, 360), (120, 420)]
_WALK = [_p(x, z) for x, z in WALK_MON]
_WALK = [(min(W - 1, max(0, u)), min(BOTTOM - 2, v)) for u, v in _WALK]
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)
_U_SOMBRA = CAM.projecta((300 + OMBRA[0] * 60, 0, 460 + OMBRA[1] * 60))
_U_SOMBRA0 = CAM.projecta((300, 0, 460))

GEOMETRIA = {
    'things': {},
    'spawns': {'rosa': _p(*ROSA), 'verne': _p(*VERNE), 'dividend': _p(*DIVIDEND)},
    'walkable': _WALK,
    'floorSquash': 0.32,
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 10), 3), 'scaleBottom': round(_escala_a(BOTTOM), 3),
                 'points': [(0, _V_FONS - 10), (W - 1, _V_FONS - 10), (W - 1, BOTTOM), (0, BOTTOM)]}],
    # el sol, baix a la dreta: les ombres de la gent cauen cap a l'esquerra i cap a la càmera, com les de la cua
    'characterShadow': {'enabled': True, 'color': '#1a1012', 'alpha': 0.4, 'squash': 0.32, 'core': 0.6,
                        'light': {'x': round(_U_SOMBRA[0] - _U_SOMBRA0[0], 2),
                                  'y': round(_U_SOMBRA[1] - _U_SOMBRA0[1], 2), 'direction': True, 'stretch': 0.9}},
}
