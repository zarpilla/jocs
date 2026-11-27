"""
Aigua Verne — `aqua_fons` (L), Escena 3: el fons de l'antic mar d'Aqua, vist des de baix. EN 3D (hd640/tres_d.py), a 1×.

Una càmera baixa que mira una mica amunt (contrapicat) i girada cap a la dreta: la paret del moll és tan alta que no
cap al quadre; de prop (a l'esquerra) puja fins a fora de la pantalla, i fuig en diagonal cap a la dreta fins a la
cantonada de la bocana. Les verticals convergeixen cap amunt. A la paret, carreus que s'empetiteixen, les ratlles de sal
de l'aigua de cada any, la franja d'algues seques, la regla de marea pintada, pneumàtics de defensa penjats a l'aire,
una sortida de clavegueram i l'escala del moll, que baixa de fora del quadre i s'acaba a l'aire. El cable baixa de dalt
de tot fins a la **cistella**, a la sorra, al peu de la paret. Passada la cantonada, el mar sec fins a l'horitzó i la
Canonada d'Aqua.

A terra (sorra blanca amb ondulacions que fugen, crostes de sal, el camí de petjades): les **boies** de mesurar en
diagonal cap a la casa (es passa per darrere de cadascuna), els **ossos** del peix damunt el fang clivellat, el
**bassal** (el cel s'hi reflecteix, amb ones que s'empetiteixen cap al fons) i la platja de **sorra fina** (prop
`sorra`). A la dreta, la **casa de la Juana**: el casc bolcat, girat, fugint cap al fons i tallat pel quadre, amb la
porta, l'ull de bou encès, la xemeneia i l'antena; el barril i el banc al davant (es passa per darrere del barril). En
primer pla, fosques i tallades per la vora: les **nanses** i la xarxa a l'esquerra, i una roca amb algues a la dreta.

Llum de migdia: el sol alt, darrere la paret i una mica a la dreta: la paret és a l'ombra i en projecta una franja al
peu; les ombres curtes cauen cap endavant i a l'esquerra.

El detall (la casa de la Juana, la cistella, les boies, les nanses, els ossos, la regla, els pneumàtics) ve del fons pla
de sempre (aqua_fons_pla_comu.py), dibuixat de cara i projectat. La platja de sorra fina és al fons (sempre es veu).
PROPS: `lot9` (Acte 2: les estaques i la cinta de Verne al voltant de la platja, de la ratlla de sal de dimarts cap
amunt, amb el cartell «LOT 9»). ANIMS: `calitja`, `pols`,
`llum_canonada`, `llum_juana` (la làmpada, a l'ull de bou), `fum` (la xemeneia), `bassal` (el reflex de l'aigua).

El món: x a la dreta, y amunt (0 = la sorra), z endavant; 1 unitat = 1 px a la distància on un personatge fa la seva
mida normal (500, en la direcció de la mirada).
"""
import functools
import math

import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

from hd.pix import Canvas, Light, W, H, hr
from hd.rooms.comu import text
from hd.rooms.exterior import fbm, smooth
from hd640.rooms import aqua_fons_pla_comu as F
from hd640.rooms.aqua_comu import (RH, SKYA, SALT, SAND, STONEA, ALGA, ALGAS, WOODG, PAINTW, RUSTA, STEELA, BLACKT, BLUEV,
                                   WATERB, BONE, cel, canonada, canonada_llum, calitja_frames, pols_frames, diff,
                                   amb_contorn, _voronoi)
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = RH - 1
CAM = Camera(pos=(0, 130, 0), yaw=0.55, pitch=-0.15, f=500, centre=(320, 45))
HOR = round(CAM.projecta((0, 130, 1e7))[1])        # l'horitzó (≈120: la càmera mira amunt)

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)
LLUMS = [Llum((4000, 20000, 9000), 1e6, 2.0, power=1.0)]    # el sol, alt, darrere la paret i a la dreta
AMBIENT = -1.3

ZW = 900.0                                         # la cara de la paret del moll (al llarg de x)
XC = 950.0                                         # la cantonada de la bocana (on s'acaba la paret)
HWALL = 1000.0                                     # l'alçada de la paret (no cap al quadre)
STAIR = [(120.0 + i * 40, 650.0 - i * 30) for i in range(16)]   # els graons (x, y del trepig), de dalt a baix

WETST = F.WETST
BUOY = F.BUOY
MUD = F.MUD


def _add(a, b, k=1.0):
    return (a[0] + b[0] * k, a[1] + b[1] * k, a[2] + b[2] * k)


def _uv(P):
    u, v, _ = CAM.projecta(P)
    return u, v


def _mon(u, v, y=0.0):
    """El punt del terra (a l'alçada `y`) que es veu al píxel de sala (u, v): → (x, z)."""
    c = CAM
    X, Y, Z = (u - c.centre[0]) / c.f, -(v - c.centre[1]) / c.f, 1.0
    z1 = Y * c._sp + Z * c._cp
    dy = Y * c._cp - Z * c._sp
    dx = X * c._cy + z1 * c._sy
    dz = -X * c._sy + z1 * c._cy
    k = (y - c.pos[1]) / dy
    return c.pos[0] + dx * k, c.pos[2] + dz * k


# On van les coses (triades a la pantalla, i passades al món)
def _a_z(u, z, y=0.0):
    """La x del món, a la fondària `z`, que es veu a la columna `u` de la pantalla."""
    lo, hi = -20000.0, 20000.0
    for _ in range(60):
        m = (lo + hi) / 2
        if CAM.projecta((m, y, z))[0] < u:
            lo = m
        else:
            hi = m
    return (lo + hi) / 2


ZCAMI = 740.0                                      # fins on es camina (més enllà, el personatge seria massa petit)
CIST = (_a_z(205, 790), 790.0)                     # la cistella, penjada de la grua (que treu el braç per damunt)
BOIES = [(*_mon(272, 226), '1', 1.0, 0.06), (*_mon(352, 203), '2', 0.95, -0.08), (*_mon(424, 213), '3', 1.0, 0.04)]
POOL = (*_mon(398, 238), 58.0, 30.0)               # el bassal: el centre (x, z) i els semieixos
BEACH = (*_mon(500, 245), 44.0, 24.0)              # la platja de sorra fina
OSSOS = _mon(280, 246)
NANSES = _mon(62, 252)
ROCA = _mon(616, 258)
# La casa de la Juana: el costat del casc és un pla dret que comença a la roda de proa (B0) i fuig cap al fons a la
# dreta (angle CASA_ANG); el dibuix pla (x 466..820, y 28..222, amb la regala a y = 214) es projecta a escala CASA_K.
CASA_ANG = 0.0
CASA_K = 1.15
CASA_X0, CASA_X1, CASA_Y0, CASA_Y1 = 466, 820, 28, 222
B0 = _mon(452, 222)
TD = (math.cos(CASA_ANG), 0.0, math.sin(CASA_ANG))
CASA_N = (TD[2], 0.0, -TD[0])                      # la normal del costat (cap a la càmera)


def casa_mon(fx, fy):
    """Un punt del dibuix pla de la casa (x, y de sala del pla) al món, al costat del casc."""
    d = (fx - CASA_X0) * CASA_K
    return (B0[0] + TD[0] * d, (F.GUNWALE - fy) * CASA_K, B0[1] + TD[2] * d)


BARRIL = _add(casa_mon(F.DOOR[0] - 30, F.GUNWALE), CASA_N, 26)
BANC = _add(casa_mon(F.DOOR[2] + 30, F.GUNWALE), CASA_N, 22)


def _loc(dx, dz):
    """Un desplaçament del terra en els eixos de la càmera: (a la dreta de la pantalla, cap al fons)."""
    c, s_ = math.cos(CAM.yaw), math.sin(CAM.yaw)
    return dx * c - dz * s_, dx * s_ + dz * c


def _ell(E, a, k=1.0):
    """Un punt (x, z) de la vora de l'el·lipse E = (cx, cz, ra, rb), girada com la càmera."""
    cx, cz, ra, rb = E
    la, lb = ra * k * math.cos(a), rb * k * math.sin(a)
    c, s_ = math.cos(CAM.yaw), math.sin(CAM.yaw)
    return cx + la * c + lb * s_, cz - la * s_ + lb * c


# ─── Diverses rampes en una ──────────────────────────────────────────────────

class _Rampes:
    """Diverses rampes en una (per a una superfície procedural que canvia de material): el nivell 100·k + 50 + l és el
    nivell l de la rampa k (el dither i la llum del món hi continuen sumant)."""

    def __init__(self, *ramps):
        self.r = ramps

    def __len__(self):
        return 100 * len(self.r)

    def __getitem__(self, i):
        k, j = divmod(i, 100)
        ramp = self.r[min(k, len(self.r) - 1)]
        return ramp[max(0, min(len(ramp) - 1, j - 50))]

    def lvl(self, fn):
        idx = {id(r): k for k, r in enumerate(self.r)}

        def L(s, t, P):
            ramp, l = fn(s, t, P)
            return 100 * idx[id(ramp)] + 50 + l
        return L


PARET = _Rampes(STONEA, WETST, ALGAS, SALT)
TERRA = _Rampes(SAND, SALT, MUD, ALGA, BONE)
FINE = [(120, 110, 92), (160, 150, 126), (196, 186, 160), (222, 214, 190), (240, 234, 214), (250, 247, 232),
        (255, 253, 244)]
AIGUA = _Rampes(WATERB, BUOY)


# ─── Les textures: el fons pla de sempre ─────────────────────────────────────

def _pla(fn, w=W):
    cv = Canvas(w, H, light=F.LIGHT, transparent=True)
    fn(cv)
    return cv.img


def _casa_pla(cv, llum=True):
    """La casa de la Juana, plana i més llarga que al pla (fins a x = 820): el casc, l'antena, la xemeneia, la porta i
    l'ull de bou."""
    w0 = F.W
    F.W = CASA_X1                                  # (casa() pinta fins a W: el casc continua fora de la pantalla)
    try:
        F.casa(cv)
    finally:
        F.W = w0
    F.antena(cv)
    F.xemeneia(cv)
    F.porta(cv)
    if llum:
        F.ull_de_bou(cv)


@functools.lru_cache(maxsize=None)
def _textures():
    return {
        'casa': _pla(_casa_pla, CASA_X1 + 4),
        'cistella': _pla(lambda cv: amb_contorn(cv, F.cistella)),
        'boies': [_pla(lambda cv, n=n, h=h, l=l: amb_contorn(cv, lambda c: F.boia(c, 100, 150, n, h=round(46 * h), lean=l)))
                  for (_, _, n, h, l) in BOIES],
        'nanses': _pla(F.nanses),
        'ossos': _pla(F.ossos),
        'regla': _pla(lambda cv: F.regla(cv, 100)),
        'defenses': _pla(F.defenses),
        'desguas': _pla(lambda cv: F.desguas(cv, 100, 120)),
    }


# ─── El fons (en pantalla): el cel i la Canonada ─────────────────────────────

CAN_U = 572
CAN_LY = 14


def fons(cv):
    cel(cv, HOR, seed=6)
    for y in range(HOR + 1, RH):                                   # (sota l'horitzó, la calitja; el terra ho tapa)
        for x in range(W):
            cv.put(x, y, SALT, 6.6, lit=0)
    canonada(cv, CAN_U, HOR, w0=1.6, w1=3.4, light_y=CAN_LY)
    # un vaixell petit encallat a l'horitzó
    x0 = CAN_U - 52
    for x in range(x0, x0 + 14):
        top = HOR - 2 - (3 if x0 + 4 < x < x0 + 10 else 0) - (5 if x0 + 5 < x < x0 + 7 else 0)
        for y in range(top, HOR + 1):
            cv.put(x, y, F.REDF if y > HOR - 3 else PAINTW, 3.0, lit=0)
    cv.tint(x0 - 2, HOR - 10, x0 + 16, HOR + 1, (226, 234, 240), 0.35)


# ─── Les superfícies ────────────────────────────────────────────────────────

def _dist_cami(x, z):
    """La distància al camí de petjades (de la cistella a la porta de la Juana, passant per les boies)."""
    pts = [(CIST[0] + 30, CIST[1] - 60)] + [(bx + 30, bz - 26) for bx, bz, *_ in BOIES] + \
          [casa_mon((F.DOOR[0] + F.DOOR[2]) / 2, F.GUNWALE)[::2]]
    pts[-1] = (pts[-1][0] + CASA_N[0] * 40, pts[-1][1] + CASA_N[2] * 40)
    best = 1e9
    for (ax, az), (bx, bz) in zip(pts, pts[1:]):
        dx, dz = bx - ax, bz - az
        u = max(0.0, min(1.0, ((x - ax) * dx + (z - az) * dz) / (dx * dx + dz * dz)))
        best = min(best, math.hypot(x - ax - dx * u, z - az - dz * u))
    return best


def _terra(s, t, P):
    """La sorra del fons del mar: ondulacions de vent (el costat d'ombra, blavós), crostes de sal, el camí trepitjat
    amb petjades, el fang clivellat sota els ossos, algues seques i closques; més lluny, la plana de sal. Tot en
    coordenades del món: grans a prop, menudes al fons."""
    x, z = P[0], P[2]
    far = smooth(2500, 9000, z)
    near = 1 - far
    # ondulacions de vent (perpendiculars al vent, de biaix)
    ph = (z * 0.9 + x * 0.25) / 26 + fbm(x / 160, z / 120, 21) * 5
    rip = math.sin(ph)
    lvl = 5.9 + (fbm(x / 140, z / 60, 22) - 0.5) * 0.9
    if rip > 0.6:
        lvl += 0.8 * near
    elif rip < -0.5:
        lvl -= 1.1 * near
    # la plana de sal, lluny (crostes poligonals)
    if far > 0:
        edge, cid = _voronoi(x / 220, z / 160, 3)
        lp = 6.0 + (hr(*cid, 3) - 0.5) * 0.6 + (0.8 if edge < 0.06 else -0.5 if edge < 0.12 else 0) * (1 - smooth(9000, 20000, z))
        lp -= smooth(0.55, 0.72, fbm(x / 900, z / 1600, 9)) * 1.4
        if far > 0.5:
            return (SALT, lvl * (1 - far) + lp * far)
        lvl = lvl * (1 - far) + lp * far
    # el fang clivellat (on hi ha els ossos)
    ox, oz = OSSOS
    fang = ((x - ox - 10) / 90) ** 2 + ((z - oz - 6) / 40) ** 2 + (fbm(x / 30, z / 20, 28) - 0.5) * 0.8
    if fang < 1:
        e, _ = _voronoi(x / 16, z / 11, 31)
        return (MUD, 3.6 + (fbm(x / 20, z / 14, 29) - 0.5) * 0.8 - (2.0 if e < 0.09 else 0) + (0.8 if fang > 0.8 else 0))
    # el camí de petjades
    d = _dist_cami(x, z)
    if d < 16:
        l2 = 5.3 + (fbm(x / 30, z / 20, 23) - 0.5) * 0.6
        if hr(int(x) // 7, int(z) // 5, 24) > 0.9 and d < 12:
            l2 -= 1.4                                              # petjades
        return (SAND, l2)
    # crostes de sal
    crust = fbm(x / 110, z / 50, 25)
    if crust > 0.66:
        return (SALT, 7.0 + (crust - 0.66) * 6 + (hr(int(x), int(z), 26) - 0.5))
    # algues seques i closques escampades (taques en coordenades del món)
    cx, cz = math.floor(x / 60), math.floor(z / 50)
    if hr(cx, cz, 32) > 0.93 and near > 0.5:
        lx, lz = x - (cx + 0.5) * 60, z - (cz + 0.5) * 50
        if lx * lx / 64 + lz * lz / 9 < 1:
            if hr(cx, cz, 33) < 0.6:
                return (ALGA, 2.6 + hr(int(x / 2), int(z / 2), 34) * 1.4)
            return (BONE, 4.6 - (0 if lz < 0 else 1.6))
    return (SAND, lvl)


def _paret(s, t, P):
    """La cara de la paret del moll: carreus (s = x, des de l'esquerra; t = des de dalt), la part de baix verdosa i amb
    algues seques, les ratlles de sal de l'aigua de cada any i, a la cantonada, els carreus grans més clars."""
    y, x = P[1], P[0]
    row = int(y // 36)
    off = 46 if row % 2 else 0
    col = int((x + 4000 + off) // 92)
    fr, fc = (y % 36) / 36, ((x + 4000 + off) % 92) / 92
    lvl = 4.6 + (hr(row, col, 7) - 0.5) * 0.9 + (fbm(x / 60, y / 40, 8) - 0.5) * 0.8
    if XC - x < 70:                                                # els carreus de la cantonada
        if row % 2 == 0 or XC - x < 36:
            lvl += 0.9
            fc = ((XC - x) % 70) / 70
    joint = fr > 0.9 or fc < 0.035
    if joint:
        lvl -= 1.4
    elif fr > 0.78:
        lvl += 0.5                                                 # el cantell de dalt de cada carreu
    alg = 170 + (fbm(x / 90, 0.5, 13) - 0.5) * 50
    if y < alg:
        a = min(1.0, (alg - y) / alg)
        spot = fbm(x / 34, y / 24, 12)
        if spot > 0.56 + a * 0.08:
            return (ALGAS, 2.2 + (spot - 0.56) * 4 - (1.0 if joint else 0) - a * 0.4)
        return (WETST, lvl - 0.6 - a * 0.7)
    for m in (420, 330, 262, 214):                       # l'aigua de cada any, més avall
        dd = y - m + (fbm(x / 50, m, 14) - 0.5) * 12
        if abs(dd) < 1.6 and fbm(x / 26, m / 7, 15) > 0.42:
            return (SALT, 6.0)
        if -6 < dd < -1.6 and hr(int(x) // 5, m, 1) < 0.12:
            return (SALT, 5.0)
    return (STONEA, lvl)


def cilindre(e, sid, cx, cz, r, y0, y1, ramp, lvl, n=20):
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        p0 = (cx + r * math.cos(a0), cz + r * math.sin(a0))
        p1 = (cx + r * math.cos(a1), cz + r * math.sin(a1))
        e.quad(sid, (p0[0], y1, p0[1]), (p1[0], y1, p1[1]), (p1[0], y0, p1[1]), (p0[0], y0, p0[1]), ramp=ramp,
               lvl=lambda s, t, P: lvl(math.atan2(P[2] - cz, P[0] - cx), P[1], P))


def _ombra(e, cx, cz, rx, rz, k=0.55, dx=-0.4, dz=-0.3, sid='ombra'):
    """Una ombra curta al terra (el sol és alt, darrere a la dreta): una mica cap endavant i a l'esquerra."""
    cx, cz = cx + dx * rx, cz + dz * rz
    e.foscor(sid, (cx - rx, 0.3, cz + rz), (cx + rx, 0.3, cz + rz), (cx + rx, 0.3, cz - rz), (cx - rx, 0.3, cz - rz),
             lambda s, t: k * min(1.0, 1.8 * max(0.0, 1 - ((s - rx) / rx) ** 2 - ((t - rz) / rz) ** 2)))


# ─── Les peces ──────────────────────────────────────────────────────────────

def terra(e):
    zn = 300
    e.quad('terra', (-80000, 0, 40000), (80000, 0, 40000), (80000, 0, zn), (-80000, 0, zn), ramp=TERRA,
           lvl=TERRA.lvl(_terra))
    # la calitja: lluny, la plana es confon amb el cel
    e.claror((-80000, 0.2, 40000), (80000, 0.2, 40000), (80000, 0.2, ZW), (-80000, 0.2, ZW), (228, 236, 244),
             lambda s, t: 0.7 * smooth(3000, 36000, 40000 - t))
    # l'ombra de la paret al peu (el sol és darrere la paret): una franja que s'eixampla cap a l'esquerra, en diagonal
    e.foscor('ombra', (-3000, 0.4, ZW), (XC, 0.4, ZW), (XC - 40, 0.4, ZW - 60), (-3000, 0.4, ZW - 150),
             lambda s, t: 0.7 * (1 - smooth(0.7, 1.0, t / (60 + 90 * (1 - s / (XC + 3000))))))


def bassal(e, phase=0.0, sid='bassal'):
    """El bassal: el cel s'hi reflecteix (més clar lluny, més blau a prop), amb ones en coordenades del món que
    s'empetiteixen cap al fons, la vora de sorra mullada, l'anell de sal, i el reflex de la boia número 3."""
    cx, cz, rx, rz = POOL
    QX = QZ = max(rx, rz) * 1.7
    bx, bz = BOIES[2][0], BOIES[2][1]

    def forma(x, z, k=1.0):
        n = fbm(x / 40, z / 24, 40) - 0.5
        a, b = _loc(x - cx, z - cz)
        return (a / (rx * k)) ** 2 + (b / (rz * k)) ** 2 + n * 0.5

    def aigua(s, t, P):
        x, z = P[0], P[2]
        dd = forma(x, z)
        if dd >= 1:
            return (WATERB, -9)
        tt = (z - (cz - rz)) / (2 * rz)                            # 0 a prop, 1 al fons
        lvl = 3.6 + tt * 2.0                                       # el cel: més clar cap a l'horitzó
        ona = math.sin(x / 7.0 + phase * 2 * math.pi) * math.sin(z / 4.0 - phase * 2 * math.pi * 2)
        lvl += ona * 0.7 * (1 - tt * 0.5)
        # el reflex de la boia 3 (el pal i el flotador, cap per avall: cap a la càmera des del peu)
        if abs(x - bx - math.sin(z / 3 + phase * 6) * 2) < 5 and bz - 70 < z < bz:
            return (BUOY, 1.6 + (0.8 if hr(int(z), int(phase * 10), 43) > 0.5 else 0))
        if dd > 0.82:
            lvl -= 1.2                                             # la vora, una mica fonda
        return (WATERB, lvl)
    e.quad(sid, (cx - QX, 0.3, cz + QZ), (cx + QX, 0.3, cz + QZ),
           (cx + QX, 0.3, cz - QZ), (cx - QX, 0.3, cz - QZ), ramp=AIGUA, lvl=AIGUA.lvl(aigua),
           forma=lambda s, t: forma(cx - QX + s, cz + QZ - t) < 1)
    if sid == 'bassal':
        # la sorra mullada i l'anell de sal
        e.quad('bassal_vora', (cx - QX, 0.2, cz + QZ), (cx + QX, 0.2, cz + QZ),
               (cx + QX, 0.2, cz - QZ), (cx - QX, 0.2, cz - QZ), ramp=TERRA,
               lvl=TERRA.lvl(lambda s, t, P: (SAND, 3.4 + (forma(P[0], P[2]) - 1) * 4) if forma(P[0], P[2]) < 1.35
                             else (SALT, 7.6)),
               forma=lambda s, t: (lambda d: 1 <= d < 1.35 or (1.35 <= d < 1.6 and hr(int(s), int(t), 42) > 0.3))(
                   forma(cx - QX + s, cz + QZ - t)))


def sorra(e):
    """La platja de sorra fina: una lloma baixa i llisa, d'un blanc més càlid, amb un sotet on algú n'ha agafat."""
    cx, cz, rx, rz = BEACH
    BX = max(rx, rz) * 1.2
    hmax = 9.0

    def h(x, z):
        n = fbm(x / 40, z / 24, 44) - 0.5
        a, b = _loc(x - cx, z - cz)
        d = (a / rx) ** 2 + (b / rz) ** 2 + n * 0.4
        return max(0.0, 1 - d) ** 0.6 * hmax, d
    # la lloma, per llesques de fondària (de lluny a prop): cada llesca és un perfil dret
    n = 26
    for i in range(n, -1, -1):
        z = cz - BX + 2 * BX * i / n

        def lv(s, t, P, z=z):
            x = P[0]
            hh, d = h(x, z)
            nx = _loc(x - cx, z - cz)[0] / rx
            lvl = 4.2 + (1 - d) * 1.4 - nx * 0.4 + (0.4 if hr(int(x * 3), int(z), 5) > 0.85 else 0)
            if abs(x - cx - 16) < 7 and abs(z - cz + 6) < 6:
                lvl -= 1.4                                         # el sotet
            return lvl
        e.quad('sorra', (cx - BX, hmax, z), (cx + BX, hmax, z), (cx + BX, 0.0, z),
               (cx - BX, 0.0, z), ramp=FINE, lvl=lv, forma=lambda s, t, z=z: hmax - t < h(cx - BX + s, z)[0])
    # l'ombra suau a la vora de davant
    e.foscor('sorra_ombra', (cx - BX, 0.3, cz - rz * 0.6), (cx + BX, 0.3, cz - rz * 0.6),
             (cx + BX, 0.3, cz - rz * 1.25), (cx - BX, 0.3, cz - rz * 1.25),
             lambda s, t: 0.35 * max(0.0, 1 - abs(t - rz * 0.35) / (rz * 0.35)) * max(0.0, 1 - abs(s - BX) / (BX * 0.9)))


def paret(e, tex):
    e.quad('paret', (-4000, HWALL, ZW), (XC, HWALL, ZW), (XC, 0, ZW), (-4000, 0, ZW), ramp=PARET, lvl=PARET.lvl(_paret))
    # la foscor al peu de la paret (la humitat i l'ombra) i la calitja cap amunt (és molt alta)
    e.foscor('paret_peu', (-4000, 40, ZW - 0.5), (XC, 40, ZW - 0.5), (XC, 0, ZW - 0.5), (-4000, 0, ZW - 0.5),
             lambda s, t: 0.5 * t / 40)
    e.claror((-4000, HWALL, ZW - 0.6), (XC, HWALL, ZW - 0.6), (XC, 0, ZW - 0.6), (-4000, 0, ZW - 0.6), (214, 226, 238),
             lambda s, t: 0.28 * smooth(400, HWALL, HWALL - t))
    # la regla de marea, pintada (el pla: x 100..122, de y ≈ 34 a 172)
    rx = 40.0
    e.quad('paret', (rx, 700, ZW - 0.5), (rx + 70, 700, ZW - 0.5), (rx + 70, 140, ZW - 0.5), (rx, 140, ZW - 0.5),
           tex=(tex['regla'], (99, 36, 121, 172)))
    # la sortida de clavegueram, amb el regalim d'algues
    dx = 330.0
    e.quad('paret', (dx - 30, 300, ZW - 0.5), (dx + 30, 300, ZW - 0.5), (dx + 30, 40, ZW - 0.5), (dx - 30, 40, ZW - 0.5),
           tex=(tex['desguas'], (92, 112, 108, F.WBASE)))
    # els pneumàtics de defensa, penjats a l'aire
    for k, (fx, fy, x, y) in enumerate(((40, 59, 200, 330), (150, 59, 470, 300), (246, 72, 760, 280))):
        e.sprite('paret', tex['defenses'].crop((fx - 9, F.WTOP - 1, fx + 10, fy + 9)), (9, fy + 9 - F.WTOP + 1),
                 (x, y, ZW - 12), escala_img=3.6)
    # l'escala del moll: baixa de fora del quadre i s'acaba a l'aire
    for i, (x, y) in enumerate(STAIR):
        last = i == len(STAIR) - 1
        e.caixa('escala', x, x + (20 if last else 40), y - 14, y, ZW - 44, ZW, STONEA, 4.2,
                cares={'dalt': {'ramp': STONEA, 'lvl': 7.0}, 'esquerra': {'ramp': STONEA, 'lvl': 3.4},
                       'sota': {'ramp': STONEA, 'lvl': 2.4}, 'davant': {'ramp': STONEA, 'lvl': 4.6}})
        e.foscor('ombra', (x + 4, y - 14, ZW - 0.5), (x + 52, y - 14, ZW - 0.5), (x + 52, y - 60, ZW - 0.5),
                 (x + 4, y - 60, ZW - 0.5), lambda s, t: 0.45 * max(0.0, 1 - t / 46))
    for i in range(0, len(STAIR) - 1, 2):
        x, y = STAIR[i]
        e.cable('escala', [(x + 20, y, ZW - 40), (x + 20, y + 36, ZW - 40)], RUSTA, 3.0, gruix=2.4)
    rail = [(x + 20, y + 36, ZW - 40) for x, y in STAIR[:-2]]
    x, y = STAIR[-2]
    rail.append((x + 46, y + 4, ZW - 46))
    e.cable('escala', rail, RUSTA, 3.8, gruix=2.6)


def cistella(e, tex):
    x0, y0, x1, y1 = F.BASKET
    cx, cz = CIST
    _ombra(e, cx, cz, 30, 18, 0.6)
    e.sprite('cistella', tex['cistella'], ((x0 + x1) / 2, y1), (cx, 0, cz), escala_img=1.5)
    hy = (y1 - (y0 - 16)) * 1.5                                    # el ganxo, a l'alçada del món
    e.cable('cistella', [(cx, hy, cz), (cx, 2600, cz)], STEELA, 3.4, gruix=1.6)


def boies(e, tex):
    for k, (bx, bz, n, h, lean) in enumerate(BOIES):
        _ombra(e, bx, bz, 14, 8, 0.6)
        e.sprite(f'boia{k}', tex['boies'][k], (100, 150), (bx, 0, bz), escala_img=1.15)


def ossos(e, tex):
    ox, oz = OSSOS
    _ombra(e, ox + 30, oz, 60, 10, 0.4)
    e.sprite('ossos', tex['ossos'].crop((228, 226, 322, 248)), (48, 18), (ox, 0, oz), escala_img=1.1)


def casa(e, tex):
    # l'ombra del casc al terra (curta, cap endavant i a l'esquerra)
    A, B = casa_mon(CASA_X0, F.GUNWALE), casa_mon(CASA_X1, F.GUNWALE)
    e.foscor('ombra', (A[0], 0.4, A[2]), (B[0], 0.4, B[2]), _add(B, CASA_N, 34)[:1] + (0.4,) + _add(B, CASA_N, 34)[2:],
             _add(A, CASA_N, 16)[:1] + (0.4,) + _add(A, CASA_N, 16)[2:], lambda s, t: 0.55 * (1 - smooth(0.4, 1, t / 30)))
    P0, P1 = casa_mon(CASA_X0, CASA_Y0), casa_mon(CASA_X1, CASA_Y0)
    P2, P3 = casa_mon(CASA_X1, CASA_Y1), casa_mon(CASA_X0, CASA_Y1)
    e.quad('casa', P0, P1, P2, P3, tex=(tex['casa'], (CASA_X0, CASA_Y0, CASA_X1, CASA_Y1)))
    # el barril de pluja i el banc, separats del casc
    bx, _, bz = BARRIL
    _ombra(e, bx, bz, 14, 9, 0.6)
    cilindre(e, 'barril', bx, bz, 10, 0, 24, WOODG,
             lambda a, y, P: 3.4 + math.cos(a + 0.5) * 1.2 - (1.0 if y % 9 < 1.5 else 0) - (0.8 if (a * 8) % 1 < 0.15 else 0))
    e.quad('barril', (bx - 9, 24, bz + 9), (bx + 9, 24, bz + 9), (bx + 9, 24, bz - 9), (bx - 9, 24, bz - 9), ramp=WOODG,
           lvl=1.4, forma=lambda s, t: (s - 9) ** 2 + (t - 9) ** 2 < 81)
    for y in (4, 20):
        cilindre(e, 'barril', bx, bz, 10.6, y, y + 2, RUSTA, lambda a, yy, P: 2.8 + math.cos(a + 0.5))
    nx, _, nz = BANC
    _ombra(e, nx, nz, 20, 8, 0.5)
    e.caixa_girada('banc', nx, nz, 32, 9, 3, CASA_ANG, WOODG, 4.0, y0=14,
                   cares={'dalt': {'ramp': WOODG, 'lvl': 5.0}, 'davant': {'ramp': WOODG, 'lvl': 3.2}})
    for lx in (-12, 12):
        p = _add(BANC, TD, lx)
        e.caixa_girada('banc', p[0], p[2], 3, 7, 14, CASA_ANG, WOODG, 2.6)
    p = _add(_add(BANC, TD, 8), (0, 17, 0))
    e.caixa_girada('banc', p[0], p[2], 5, 5, 5, CASA_ANG, PAINTW, 4.4, y0=17)   # la tassa


def primer_pla(e, tex):
    """A l'esquerra, les nanses i la xarxa (a l'ombra, fosques); a la dreta, una roca amb algues. Tallades per la vora."""
    nx, nz = NANSES
    e.sprite('nanses', tex['nanses'].crop((0, 194, 200, 260)), (70, 58), (nx, 0, nz), escala_img=1.25)
    rx, rz = ROCA
    e.roca('primer_pla', (rx, 0, rz), 46, STONEA, 2.6, seed=5)
    e.roca('primer_pla', (rx - 50, 0, rz + 12), 20, STONEA, 2.8, seed=6)
    for j in range(7):                                             # algues seques penjant de la roca
        a = 1.3 + (j - 3) * 0.25
        e.cable('primer_pla', [(rx - 40 + j * 6, 30 + hr(j, 3) * 10, rz - 20),
                               (rx - 40 + j * 6 + math.cos(a) * 12, 4, rz - 26)], ALGA, 2.6, gruix=1.4)


def _enfosqueix(e, ids, k):
    """El primer pla, més fosc (és a l'ombra, i a contrallum)."""
    W_ = e.cv.w
    P = e.cv.P
    for i, o in enumerate(e.amo):
        if o and e.ids[o] in ids:
            X, Y = i % W_, i // W_
            c = P[X, Y]
            P[X, Y] = (int(c[0] * k), int(c[1] * k), int(c[2] * k), c[3])


# ─── Composició ─────────────────────────────────────────────────────────────

def escena(cv, tex):
    e = Escena(cv, CAM, LLUMS, ambient=AMBIENT)
    fons(cv)
    terra(e)
    paret(e, tex)
    cistella(e, tex)
    casa(e, tex)
    bassal(e)
    ossos(e, tex)
    boies(e, tex)
    sorra(e)
    primer_pla(e, tex)
    _enfosqueix(e, {'nanses', 'primer_pla'}, 0.5)
    return e


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


def _nomes(img, base, e, ids):
    """Els píxels de `img` que canvien respecte de `base` i que, al fons, són de les superfícies `ids`."""
    out = diff(img, base)
    o = out.load()
    for i, a in enumerate(e.amo):
        X, Y = i % e.cv.w, i // e.cv.w
        if o[X, Y][3] and e.ids[a] not in ids:
            o[X, Y] = (0, 0, 0, 0)
    return out


# ─── El lot 9 (Acte 2): les estaques i la cinta de Verne al voltant de la platja de sorra fina ───────────────

# La línia de l'aigua «amidada dimarts»: la ratlla de sal al voltant del bassal (bassal_vora, ≈1,45 vegades el bassal
# d'ara). Les estaques tanquen la platja d'aquesta línia cap amunt; entre la cinta i l'aigua d'avui queda una franja
# de sorra que dimarts era sota l'aigua. Coordenades locals de la platja (a: cap a la dreta de la pantalla, b: cap al
# fons; vegeu _ell).
LOT9_A0 = POOL[2] * 1.45 - _loc(BEACH[0] - POOL[0], BEACH[1] - POOL[1])[0]     # la cinta de l'esquerra (dimarts)
LOT9 = (LOT9_A0, BEACH[2] * 1.3, -BEACH[3] * 1.4, BEACH[3] * 1.3)              # a0, a1, b0 (davant), b1 (darrere)
ESTACA_H, CINTA_Y = 15.0, 11.0
CARTELL_H = 20.0


def _lot9_mon(a, b):
    cx, cz = BEACH[0], BEACH[1]
    c, s_ = math.cos(CAM.yaw), math.sin(CAM.yaw)
    return cx + a * c + b * s_, cz - a * s_ + b * c


def _lot9_tram(a0, b0, a1, b1, n):
    return [(a0 + (a1 - a0) * i / n, b0 + (b1 - b0) * i / n) for i in range(n + 1)]


def _lot9_estaques():
    """Les estaques, de darrere (la cinta del fons) a davant, en tres trams: el fons, la dreta i el davant; i la línia
    de dimarts, a l'esquerra (que és la que toca l'aigua)."""
    a0, a1, b0, b1 = LOT9
    fons = _lot9_tram(a0, b1, a1, b1, 4)
    dreta = _lot9_tram(a1, b1, a1, b0, 2)[1:]
    davant = _lot9_tram(a1, b0, a0, b0, 4)[1:]
    dimarts = _lot9_tram(a0, b0, a0, b1, 2)[1:-1]
    return fons, dreta, davant, dimarts


def _cartell_img():
    """El cartell del lot (a 1:1: és text): «LOT 9», en blau de Verne damunt la planxa blanca."""
    cv = Canvas(30, 14, light=LIGHT, transparent=True)
    cv.rect(1, 1, 25, 11, PAINTW, lambda x, y: 5.4 - (1.6 if y == 11 or x == 25 else 0) + (0.6 if y == 1 else 0), lit=0)
    cv.rect(2, 2, 24, 2, BLUEV, 2.4, lit=0)
    x9 = 4 + text(cv, 'LOT ', 4, 4, None, 0, flat=BLUEV[1]) + 1
    for j, row in enumerate(['111', '101', '111', '001', '111']):      # el 9 tancat: el de la font, de lluny, fa un 3
        for i, bit in enumerate(row):
            if bit == '1':
                cv.flat(x9 + i, 4 + j, BLUEV[1])
    cv.rect(2, 10, 24, 10, BLUEV, 2.4, lit=0)
    return cv.img.crop(cv.img.getbbox())


def _lot9_peces(e, quines):
    """Pinta les estaques i la cinta dels trams `quines` ('fons' o 'davant')."""
    fons, dreta, davant, dimarts = _lot9_estaques()
    trams = {'fons': [fons], 'davant': [[fons[0]] + dimarts + [davant[-1]], [fons[-1]] + dreta, [dreta[-1]] + davant]}
    for punts in trams[quines]:
        P = [(*_lot9_mon(a, b),) for a, b in punts]
        for (xa, za), (xb, zb) in zip(P, P[1:]):                                   # la cinta, a ratlles blau i blanc
            e.quad('lot9', (xa, CINTA_Y + 1.6, za), (xb, CINTA_Y + 1.6, zb), (xb, CINTA_Y, zb), (xa, CINTA_Y, za),
                   ramp=BLUEV, lvl=lambda s, t, P_: 2.4 if int(P_[0] / 4 + P_[2] / 4) % 2 else 4.4,
                   dues_cares=True)
        for x, z in P:
            _ombra(e, x, z, 3, 2, 0.4, sid='lot9_ombra')
            e.caixa('lot9', x - 1, x + 1, 0, ESTACA_H, z - 1, z + 1, WOODG, 4.4,
                    cares={'dalt': {'ramp': WOODG, 'lvl': 6.0}, 'esquerra': {'ramp': WOODG, 'lvl': 3.0}})
    if quines == 'davant':                                                         # el cartell, a la cantonada
        x, z = _lot9_mon(LOT9[0], LOT9[2])
        x, z = x + 3, z - 3
        e.caixa('lot9', x - 1.2, x + 1.2, 0, CARTELL_H, z - 1.2, z + 1.2, WOODG, 4.0,
                cares={'esquerra': {'ramp': WOODG, 'lvl': 2.8}})
        img = _cartell_img()
        peu = (x, CARTELL_H - 2, z - 1.5)
        e.sprite('lot9', img, (img.width // 2, img.height - 1), peu, escala_img=1 / CAM.escala(peu))


def prop_lot9(cv):
    """Les estaques i la cinta de Verne del lot 9, amb el cartell: les del fons, darrere la lloma de sorra fina, i les
    de davant, per davant (es torna a pintar la lloma entre les unes i les altres, i es queda la diferència)."""
    base, e = _base()
    amb = Canvas(light=LIGHT, img=base.copy())
    e2 = Escena(amb, CAM, LLUMS, ambient=AMBIENT)
    _lot9_peces(e2, 'fons')
    sorra(e2)
    _lot9_peces(e2, 'davant')
    out = diff(amb.img, base)
    o = out.load()
    for i, a in enumerate(e.amo):                                  # no per sobre del primer pla
        X, Y = i % W, i // W
        if o[X, Y][3] and e.ids[a] in ('nanses', 'primer_pla'):
            o[X, Y] = (0, 0, 0, 0)
    cv.img.alpha_composite(out)


PROPS = {'lot9': prop_lot9}


# ─── Animacions ────────────────────────────────────────────────────────────

def _frames_calitja():
    x0 = round(_uv((XC, 0, ZW))[0]) + 2
    return calitja_frames(_base()[0], x0, W - 1, HOR - 3, HOR + 6, n=8, amp=1.0, seed=2)


def _frames_pols():
    return pols_frames(24, 30, (0, 180, W - 1, RH - 6), seed=9, C=Canvas)


def _frames_llum():
    on = canonada_llum(CAN_U, CAN_LY, True, Canvas)
    off = Canvas(transparent=True).img
    return [on, on, off, off, off, off, off, off]


def _frames_llum_juana():
    """La flama de la làmpada de la Juana, que tremola darrere l'ull de bou (dibuixada plana i projectada pel casc)."""
    _, e = _base()
    cx, cy, r = F.PORT
    out = []
    for i in range(8):
        cv = Canvas(CASA_X1 + 4, H, transparent=True)
        k = 0.5 + 0.5 * math.sin(i / 8 * 2 * math.pi) * (0.6 + 0.4 * hr(i, 60))
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                d = math.hypot(x - cx - 1, y - cy - 1) / r
                if d < 1 and hr(x, y, i) < (1 - d) * 0.6 * k:
                    cv.P[x, y] = (255, 236, 180, 255) if d < 0.4 else (250, 206, 120, 255)
        out.append(e.capa(cv.img, {'casa'}))
    return out


def _frames_fum():
    """Un fil de fum de la xemeneia, que puja i s'esfilagarsa (a la mida que toca a aquella distància)."""
    top = casa_mon(F.CHIMNEY[0], F.CHIMNEY[1] - 5)
    x0, y0 = _uv(top)
    k = CAM.escala(top)
    out = []
    n = 12
    for i in range(n):
        cv = Canvas(transparent=True)
        for j in range(16):
            t = ((j + i / n * 4) % 16) / 16
            y = y0 - t * 50 * k
            x = x0 + (math.sin(t * 5 + j * 0.3) * (1 + t * 4) + t * 10) * k
            a = int(150 * (1 - t))
            for dx in range(int(1 + t * 3 * k)):
                if 0 <= int(y) < H and 0 <= int(x + dx) < W:
                    cv.P[int(x + dx), int(y)] = (236, 238, 240, a)
        out.append(cv.img)
    return out


def _frames_bassal():
    base, e = _base()
    out = []
    for i in range(6):
        c2 = Canvas(light=LIGHT, img=base.copy())
        e2 = Escena(c2, CAM, LLUMS, ambient=AMBIENT)
        bassal(e2, phase=i / 6, sid='bassal_f')
        out.append(_nomes(c2.img, base, e, {'bassal'}))
    return out


ANIMS = {'calitja': {'frames': _frames_calitja, 'frameDuration': 160},
         'pols': {'frames': _frames_pols, 'frameDuration': 110},
         'llum_canonada': {'frames': _frames_llum, 'frameDuration': 250},
         'llum_juana': {'frames': _frames_llum_juana, 'frameDuration': 140},
         'fum': {'frames': _frames_fum, 'frameDuration': 160},
         'bassal': {'frames': _frames_bassal, 'frameDuration': 220}}


def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _v(x, z):
    return CAM.projecta((x, 0, z))[1]


# Capes del davant: el personatge hi passa per darrere si té els peus més amunt (més lluny) que la seva base.
FRONT = [
    *[{'id': f'davant_boia{k}', 'mask': _amo({f'boia{k}'}), 'baseline': round(_v(bx, bz)), 'zIndex': 20}
      for k, (bx, bz, *_) in enumerate(BOIES)],
    {'id': 'davant_cistella', 'mask': _amo({'cistella'}), 'baseline': round(_v(*CIST)), 'zIndex': 20},
    {'id': 'davant_barril', 'mask': _amo({'barril', 'banc'}), 'baseline': round(_v(BARRIL[0], BARRIL[2])), 'zIndex': 20},
    {'id': 'davant', 'mask': _amo({'nanses', 'primer_pla'}), 'baseline': 999, 'zIndex': 20},
]


# ─── Geometria (coordenades de sala, projectades) ─────────────────────────────

def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


def _rect(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


def _cercle(cx, cz, r, n=8):
    return [_p(cx + r * math.cos(2 * math.pi * i / n), cz + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def _escala_a(v):
    """L'escala d'un personatge amb els peus a la y de pantalla `v` (al terra, la profunditat només depèn de v)."""
    x, z = _mon(320, v)
    return CAM.escala((x, 0, z))


# El terra on es camina (al món): de prop fins al peu de la paret i de la casa; no arriba al primer pla.
_PORTA = casa_mon((F.DOOR[0] + F.DOOR[2]) / 2, F.GUNWALE)
_DAVANT_CASA = [_add(casa_mon(fx, F.GUNWALE), CASA_N, 22) for fx in (CASA_X0 - 40, CASA_X0 + 60, CASA_X1 - 60)]
WALK_MON = ([_mon(150, 259), _mon(122, 226), (_a_z(0, ZCAMI), ZCAMI), (_a_z(420, ZCAMI), ZCAMI)] +
            [(p[0], p[2]) for p in _DAVANT_CASA] + [_mon(639, 214), _mon(639, 236), _mon(572, 259)])
_WALK = [_p(x, z) for x, z in WALK_MON]
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)

GEOMETRIA = {
    'things': {
        'cistella': {'rect': _rect((CIST[0] - 26, 70, CIST[1]), (CIST[0] + 26, 0, CIST[1])),
                     'walk': _p(CIST[0] + 20, CIST[1] - 70)},
        'porta_juana': {'rect': _rect(casa_mon(F.DOOR[0] - 3, F.DOOR[1] - 3), casa_mon(F.DOOR[2] + 3, F.GUNWALE + 2)),
                        'walk': _p(*_add(_PORTA, CASA_N, 34)[::2])},
        'nanses': {'rect': (0, round(_uv((NANSES[0], 60, NANSES[1]))[1]), round(_uv((NANSES[0] + 160, 0, NANSES[1]))[0]),
                            BOTTOM),
                   'walk': _p(*_mon(170, 232))},
        'boies': {'rect': _rect(*[(bx - 12, 0, bz) for bx, bz, *_ in BOIES], *[(bx + 12, 56, bz) for bx, bz, *_ in BOIES]),
                  'walk': _p(BOIES[1][0] - 10, BOIES[1][1] - 40)},
        'bassal': {'rect': _rect(*[(*_ell(POOL, a)[:1], 0, _ell(POOL, a)[1]) for a in (0, 1.57, 3.14, 4.71)]),
                   'walk': _p(*_ell(POOL, 1.9, 1.3))},
        # (la lloma i, a l'Acte 2, les estaques i el cartell del lot 9 al seu voltant)
        'sorra': {'rect': _rect(*[(_ell(BEACH, a)[0], 10, _ell(BEACH, a)[1]) for a in (0, 1.57, 3.14, 4.71)],
                                (_ell(BEACH, 4.71)[0], 0, _ell(BEACH, 4.71)[1]),
                                *[(*_lot9_mon(a, b)[:1], y, _lot9_mon(a, b)[1]) for a in LOT9[:2] for b in LOT9[2:]
                                  for y in (0, ESTACA_H)],
                                (_lot9_mon(LOT9[0], LOT9[2])[0] + 3, CARTELL_H + 8, _lot9_mon(LOT9[0], LOT9[2])[1] - 3)),
                  'walk': _p(*_ell(BEACH, 4.4, 1.4))},
        'ossos': {'rect': _rect((OSSOS[0] - 52, 0, OSSOS[1]), (OSSOS[0] + 56, 24, OSSOS[1])),
                  'walk': _p(OSSOS[0] + 70, OSSOS[1] + 10)},
    },
    'spawns': {'iri': _p(CIST[0] + 50, CIST[1] - 110), 'vet': _p(CIST[0] - 20, CIST[1] - 170)},
    'walkable': _WALK,
    'forats': [_cercle(*CIST, 30), *[_cercle(bx, bz, 12, 6) for bx, bz, *_ in BOIES],
               [_p(*_ell(POOL, a, 0.85))
                for a in [2 * math.pi * i / 10 for i in range(10)]],
               _cercle(BARRIL[0], BARRIL[2], 18, 6)],
    'floorSquash': 0.3,
    'characterShadow': {'enabled': True, 'color': '#2a3040', 'alpha': 0.4, 'squash': 0.3, 'core': 0.6,
                        'light': {'x': -0.5, 'y': 0.4, 'direction': True, 'stretch': 0.35}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    # La llum de la sala sobre els personatges (characterLights del motor): la sal enlluernadora del fons del mar:
    # gairebé neutra, una mica freda, i el sol de dalt.
    'characterLights': {
        'ambient': '#eceef2',
        'lights': [
            {'x': W, 'y': -300, 'radius': 1000, 'color': '#fff6e6', 'intensity': 0.15},  # el sol: una mica més de llum, i càlida
        ],
    },
}
