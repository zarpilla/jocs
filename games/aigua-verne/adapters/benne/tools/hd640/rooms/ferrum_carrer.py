"""
Aigua Verne — `ferrum_carrer` (L): un carrer de miners de Ferrum, a la tarda, sota un cel de fum. EN 3D
(hd640/tres_d.py), a 1×.

Una càmera alta, girada cap a la dreta i mirant una mica avall (picat), en una cantonada: la fila de façanes fuig cap
a la dreta (el **sindicat** a la cantonada, les cases dels miners amb el **panell del preu**, la **fosa** amb el
portal gran i la xemeneia, i un magatzem), i a l'esquerra el carrer del costat, que just darrere el sindicat s'eixampla
en una plaça on hi ha aparcada de biaix la Cantimplora (el model canònic de cantimplora_comu.py: la popa amagada
darrere el sindicat i la proa que fuig cap al fons; se'n veu el costat de babord, amb el nom CANTIMPLORA sencer i la
porta de la bodega encesa) amb la **rampa** baixada fins a les llambordes; per sobre, la **Canonada**. Al mig del carrer, el
**piquet** (la pancarta girada, el bidó amb la foguera, la canalla en caixes, i una nena dreta amb una garrafa que
mira la font); la **font** de Verne, amb el lector vermell i, a sota, la pantalla «VERNE S.A. CONTRACTA»; la pila de
**comptadors** arrencats; el **condensador** vell, girat, amb el lector de targetes de Verne cargolat al costat. Primer pla: el fanal i unes caixes a l'esquerra, la
vagoneta al carril a la dreta. El sol, baix a l'esquerra, fa ombres llargues en diagonal cap a la dreta. Es passa per
darrere de la rampa (a banda i banda, arran del buc). El fanal és a la vora esquerra, gairebé fora de quadre.

Tot el detall ve del carrer pla de sempre (ferrum_carrer_pla_comu.py): les façanes, el condensador, la font, el
piquet i la canalla es dibuixen de cara i es projecten (textures i sprites). Decorats (PROPS): `barril_piquet`,
`condensador_arreglat` (també el lector en verd, amb la targeta de la Mosca), `pantalla_mosca` (la pantalla de la font,
«FELICITATS / MOSCA!»). ANIMS: `foc` (la foguera del bidó), `fum` (les xemeneies de les cases), `goteig` (l'aixeta
del condensador arreglat).

El món: x al llarg de la fila de façanes, y amunt, z cap al fons (z = 660: les façanes); 1 unitat = 1 px de sala on
un personatge fa la seva mida normal. Les façanes planes es posen a ×1,25 (al pla eren petites per a la gent).
"""
import functools
import math

import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)
from hd.pix import Canvas, Light, W, H, hr
from hd.rooms.comu import _diff
from hd.rooms.exterior import fbm, smooth
from hd640.rooms import ferrum_carrer_pla_comu as PL
from hd640.rooms.ferrum_carrer_pla_comu import _smoke_loop  # noqa: F401  (el fan servir els postcrèdits)
from hd640.rooms.ferrum_comu import (
    SOOT, MORTAR, COB, COAL, IRONF, RUSTF, TIN, PLANKF, WATER, GLOWF, REDV, BLUEV, BLACKT, smog_sky, canonada,
    brick_lvl, finestres_enceses, llum_finestra, bassa_fanal, con_fanal, fanal_paret, pantalla_contracta,
    PANTALLA_BASE, PANTALLA_W, PANTALLA_H)
from hd640.rooms.cantimplora_comu import Cantimplora
from hd640.tres_d import Camera, Escena, Llum, llum_personatges

BOTTOM = 259
HOR = 21                                           # l'horitzó a la pantalla (amagat darrere les cases)
CAM = Camera(pos=(0, 200, 0), yaw=0.45, pitch=0.15, f=520, centre=(320, 100))
KF = 1.25                                          # unitats del món per píxel del pla, a les façanes
KP = 1.0                                           # ... als objectes que hi ha al carrer (a la mida de la gent)

X0, ZR = 120.0, 560.0                              # la cantonada del sindicat; el pla de les façanes
XO = -170.0                                        # l'altra banda del carrer del costat
# el sindicat (retall del pla: x 59..208, y 54..193)
SC = (59, 54, 208, 193)
SX1 = X0 + (SC[2] - SC[0]) * KF
SH = (SC[3] - SC[1]) * KF
# les cases (una mica enrere) i la fosa (una mica endavant)
CC = (289, 85, 462, 193)
CX0, CZ = SX1, ZR + 8
CX1 = CX0 + (CC[2] - CC[0]) * KF
CH = (CC[3] - CC[1]) * KF
FC = (455, 22, 641, 193)
FX0, FZ = CX1, ZR - 8
FX1 = FX0 + (FC[2] - FC[0]) * KF
FH = (FC[3] - FC[1]) * KF
# la Cantimplora (el model canònic, cantimplora_comu), aparcada de biaix on el carrer del costat s'eixampla: la
# popa amagada darrere el sindicat i la proa que fuig cap al fons a l'esquerra (així el nom, CANTIMPLORA, cap sencer
# entre la vora i la porta); la porta, a babord (el costat que es veu), amb la rampa baixada fins a les llambordes
NAU = Cantimplora(popa=(240.0, 850.0), rumb=math.pi - 0.5, porta='babord')
PORTA_L, PORTA_T, RAMPA_OUT = NAU.PORTA_L, NAU.PORTA_T, NAU.RAMPA_OUT
ZE, ZF = ZR + 190, 1100.0                          # el carrer del costat s'eixampla en una plaça just darrere el
                                                   # sindicat (la nau); les cases tornen a començar més enllà
# el piquet, la font, els comptadors, el condensador (x, z)
BIDO = (X0 + 266, ZR - 196)
NENS = ((X0 + 218, ZR - 204), (X0 + 318, ZR - 182), (X0 + 180, ZR - 130))   # (la nena dreta, a la dreta de la font)
PANC = ((X0 + 186, ZR - 92), (X0 + 346, ZR - 126))  # els dos pals de la pancarta
FONT = (X0 + 168, ZR - 62)
COMPT = (X0 + 132, ZR - 40)
COND = (FX0 + 120, ZR - 96, 0.42)                  # (x, z, gir)
FANAL = (-34.0, 340.0)                            # (a la vora: deixa veure la porta de la nau)
VAGO = (500.0, 300.0)
BARRIL = (X0 + 360, ZR - 200)

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)       # (la llum és la del món: la de l'Escena)
SOL = (-6000.0, 3000.0, -1500.0)                   # el sol, baix a l'esquerra (una mica cap a la càmera)
LLUMS = [Llum(SOL, 1e6, 2.2, power=1.0),
         Llum((BIDO[0], 34, BIDO[1]), 110, 1.4, power=1.6)]      # la foguera
AMBIENT = -1.2
_D = (-SOL[0], -SOL[2])
_n = math.hypot(*_D)
OMBRA = (_D[0] / _n, _D[1] / _n)                   # cap on cauen les ombres, al terra (x, z)
OMBRA_K = 1.7                                      # llargada de l'ombra per unitat d'alçada (el sol és baix)
_SOL_DIR = (SOL[0] / 6000, 1.0 / OMBRA_K, SOL[2] / 6000)   # cap al sol (per a l'ombra de la nau: igual de llarga)

TEXL = Light(ambient=0.8, vignette=None, floor_fade=None)        # la llum de les textures planes (neutra)


# ─── Les textures: el carrer pla de sempre ────────────────────────────────────

def _pla(fn):
    cv = Canvas(light=TEXL, transparent=True)
    fn(cv)
    return cv.img


def _cases_pla(cv):
    PL.cases(cv)
    PL.panell(cv, 330, 100, 'VERNE', '▲')


def _cond_pla(cv):
    PL.condensador(cv)


@functools.lru_cache(maxsize=None)
def _textures():
    return {
        'sindicat': _pla(PL.sindicat),
        'cases': _pla(_cases_pla),
        'fosa': _pla(lambda cv: PL.fosa(cv, xemeneia=False)),
        'cond': _pla(_cond_pla),
        'font': _pla(lambda cv: PL.font_verne(cv, *PL.FONT, alt=FONT_ALT)),
        'comptadors': _pla(lambda cv: PL.pila_comptadors(cv, 402, 456, 230, 26, seed=3)),
        'pancarta': _pla(PL.pancarta),
        'bido': _pla(PL.bido),
        'canalla': _pla(PL.canalla),
    }


def _retall(img, box):
    return img.crop(box)


# ─── Utilitats del món ────────────────────────────────────────────────────────

def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


def _sind(fx, fy):
    """Un punt del pla del sindicat al món."""
    return (X0 + (fx - SC[0]) * KF, (SC[3] - fy) * KF, ZR)


def _cases(fx, fy):
    return (CX0 + (fx - CC[0]) * KF, (CC[3] - fy) * KF, CZ)


def _fosa(fx, fy):
    return (FX0 + (fx - FC[0]) * KF, (FC[3] - fy) * KF, FZ)


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


# ─── El fons (en pantalla) ────────────────────────────────────────────────────

CAN_U = 162                                        # la Canonada, al fons del carrer del costat


def fons(cv):
    smog_sky(cv, 110, sun=(70, 22), seed=3)                          # (el cel de sempre: l'horitzó, sota les cases)


# ─── El terra (en el món) ─────────────────────────────────────────────────────

def _terra(s, t, P):
    """Llambordes de pedra fosca amb pols de carbó: files al llarg dels carrers, grans a prop i petites al fons."""
    x, z = P[0], P[2]
    far = smooth(1300, 2600, z + max(0.0, x - 600) * 0.5)
    lateral = x < X0 - 10 and z > ZR + 20                         # el carrer del costat: les files van al llarg de z
    a, b = (z, x) if lateral else (x, z)
    rh = 11.0
    row = int(b // rh)
    off = 9.0 if row % 2 else 0.0
    col = int((a + off) // 18.0)
    fa, fb = ((a + off) % 18.0) / 18.0, (b % rh) / rh
    v = 3.0 + (hr(row, col, 5) - 0.5) * 1.1 + (fbm(x / 90, z / 60, 6) - 0.5) * 1.4
    if fb < 0.16 or fa < 0.09:
        v -= 1.7 * (1 - far)
    elif fb < 0.4:
        v += 0.5 * (1 - far)
    if fbm(x / 70, z / 40, 91) > 0.62:
        v -= 0.6                                                    # pols de carbó a clapes
    return v * (1 - far * 0.4) + 2.6 * far * 0.4


def carrils(e):
    """El carril de les vagonetes: surt del portal de la fosa i fa corba cap a baix a la dreta."""
    px = (_fosa(531, 0)[0])
    for dx in (-17, 17):
        pts = []
        for k in range(9):
            t = k / 8
            pts.append((px + dx + t * t * 120 + t * 10, 0.5, FZ - 6 - t * 290))
        e.cable('carril', pts, IRONF, 4.4, gruix=1.6)
    for k in range(14):                                             # les travesses, mig colgades
        t = k / 13
        cx, cz = px + t * t * 120 + t * 10, FZ - 6 - t * 290
        e.caixa('carril', cx - 22, cx + 22, 0, 0.6, cz - 2, cz + 2, PLANKF, 1.8)


# ─── Les façanes ─────────────────────────────────────────────────────────────

def _maons(base=3.2, seed=1, finestres=(), bw=11, bh=4, sutge=1.6):
    """Paret de maó procedural (s, t des de dalt a l'esquerra), amb finestres fosques o enceses: (s0, t0, w, h, encesa)."""
    def L(s, t, P):
        for s0, t0, w, h, on in finestres:
            if s0 <= s < s0 + w and t0 <= t < t0 + h:
                if s - s0 < 2 or s0 + w - s < 2 or t - t0 < 2:
                    return 1.6
                bar = abs(s - s0 - w / 2) < 1 or abs(t - t0 - h / 2) < 1
                if on:
                    return 1.0 if bar else 5.6 + (fbm(s / 4, t / 4, seed) - 0.5) * 1.4
                return 0.6 if bar else 0.9 + (0.8 if int(s + t) % 7 == 0 else 0)
            if s0 - 2 <= s < s0 + w + 2 and t0 + h <= t < t0 + h + 3:
                return 4.0                                          # l'ampit
        v = brick_lvl(int(s), int(t), 0, 0, bw, bh, base, seed)
        v -= sutge * max(0.0, 1 - t / 46) * (0.6 + fbm(s / 6, 0.5, seed) * 0.8)
        return v
    return L


def facanes(e, tex):
    T = tex
    # el sindicat: la façana (el pla) i el costat, que dona al carrer del costat i li toca el sol
    e.quad('sindicat', (X0, SH, ZR), (SX1, SH, ZR), (SX1, 0, ZR), (X0, 0, ZR), tex=(T['sindicat'], SC))
    e.quad('sindicat_costat', (X0, SH - 4, ZR + 190), (X0, SH - 4, ZR), (X0, 0, ZR), (X0, 0, ZR + 190), ramp=SOOT,
           lvl=_maons(3.6, 11, finestres=((40, 34, 20, 26, False), (110, 34, 20, 26, True), (70, 96, 22, 30, False))))
    e.quad('sindicat_costat', (X0 - 3, SH, ZR + 190), (X0 - 3, SH, ZR - 3), (X0 - 3, SH - 5, ZR - 3),
           (X0 - 3, SH - 5, ZR + 190), ramp=MORTAR, lvl=4.2)
    # les cases dels miners: la façana, la teulada de pissarra i les xemeneies
    e.quad('cases_costat', (CX0, CH, CZ), (CX0, CH, ZR), (CX0, 0, ZR), (CX0, 0, CZ), ramp=SOOT, lvl=1.6)
    e.quad('cases', (CX0, CH, CZ), (CX1, CH, CZ), (CX1, 0, CZ), (CX0, 0, CZ), tex=(T['cases'], CC))
    e.quad('teulada', (CX0 - 4, CH + 52, CZ + 96), (CX1 + 4, CH + 52, CZ + 96), (CX1 + 4, CH - 1, CZ - 6),
           (CX0 - 4, CH - 1, CZ - 6), ramp=PL.SLATE,
           lvl=lambda s, t, P: 3.4 - (1.3 if t % 7 < 1.3 else 0) - (0.8 if (s + (t // 7) * 5) % 11 < 1 else 0)
           + (fbm(s / 14, t / 8, 21) - 0.5) * 0.9 + (0.6 if t < 4 else 0))
    for fx, ct in PL.CHIMNEYS:
        x = CX0 + (fx - CC[0]) * KF
        top = CH + 52 + (60 - ct) * 0.6
        e.caixa('xemeneies', x - 7, x + 7, CH + 10, top, CZ + 44, CZ + 58, SOOT, 3.0,
                cares={'davant': {'ramp': SOOT, 'lvl': lambda s, t, P: brick_lvl(int(s), int(t), 0, 0, 7, 3, 3.0, 4)
                                  - max(0.0, 1 - t / 10) * 1.8},
                       'dalt': {'ramp': COAL, 'lvl': 0.6}})
        e.caixa('xemeneies', x - 3, x + 2, top, top + 5, CZ + 48, CZ + 53, RUSTF, 2.8)
    # la fosa: la façana del pla (sense la xemeneia), el costat, i la xemeneia de debò, altíssima
    e.quad('fosa_costat', (FX0, FH - 40, CZ), (FX0, FH - 40, FZ), (FX0, 0, FZ), (FX0, 0, CZ), ramp=SOOT, lvl=2.0)
    xc = FX0 + (616 - FC[0]) * KF
    e.caixa('fosa_xemeneia', xc - 13, xc + 13, FH - 60, 1400, FZ + 70, FZ + 96, SOOT, 3.0,
            cares={'davant': {'ramp': SOOT, 'lvl': lambda s, t, P: brick_lvl(int(s), int(t), 0, 0, 9, 4, 2.9, 31)
                              - (1.5 if int(P[1]) % 160 < 5 else 0) - max(0.0, 1 - (P[1] - 300) / 300) * 0.0},
                   'esquerra': {'ramp': SOOT, 'lvl': lambda s, t, P: brick_lvl(int(s), int(t), 0, 0, 9, 4, 3.6, 32)
                                - (1.5 if int(P[1]) % 160 < 5 else 0)}})
    e.quad('fosa', (FX0, FH, FZ), (FX1, FH, FZ), (FX1, 0, FZ), (FX0, 0, FZ), tex=(T['fosa'], FC))
    # el magatzem, després de la fosa, i més enllà
    e.quad('magatzem', (FX1, 196, ZR), (FX1 + 900, 196, ZR), (FX1 + 900, 0, ZR), (FX1, 0, ZR), ramp=SOOT,
           lvl=_maons(2.6, 41, finestres=tuple((40 + i * 90, 50, 36, 40, i == 2) for i in range(10)), bw=12))
    e.quad('magatzem', (FX1, 202, ZR - 4), (FX1 + 900, 202, ZR - 4), (FX1 + 900, 196, ZR - 4), (FX1, 196, ZR - 4),
           ramp=MORTAR, lvl=3.6)


def _tram_cases(z, w, lluny):
    """El tros [z, z + w) d'una casa del carrer del costat que toca pintar: les de prop (fins a ZE) es pinten després
    de la nau, les de lluny (des de ZF) abans; entre les dues, la plaça on és aparcada la nau. → (z0, z1) o None."""
    a, b = (max(z, ZF), z + w) if lluny else (z, min(z + w, ZE))
    return (a, b) if b - a > 4 else None


def carrer_costat(e, lluny):
    """El carrer del costat, que s'allunya cap al fons: cases a les dues bandes, cada una d'una alçada. S'obre en una
    plaça on hi ha la Cantimplora (`lluny`: les cases de més enllà de la nau; si no, les d'abans)."""
    z = ZR + 190
    i = 0
    while z < 5200:
        w = 150 + hr(i, 1) * 120
        h = 150 + hr(i, 2) * 70
        tr = _tram_cases(z, w, lluny)
        if tr:
            a, b = tr
            e.quad('fons_costat', (X0, h, b), (X0, h, a), (X0, 0, a), (X0, 0, b), ramp=SOOT,
                   lvl=_maons(2.6 - min(1.0, z / 4000), 50 + i,
                              finestres=tuple((20 + k * 46, 40 + j * 50, 18, 24, hr(i, k, j) > 0.8)
                                              for k in range(int((b - a) // 46) - 1) for j in range(2))))
        z += w
        i += 1
    z = ZR - 120
    i = 0
    while z < 5200:
        w = 130 + hr(i, 7) * 140
        h = 140 + hr(i, 8) * 80
        tr = _tram_cases(z, w, lluny)
        if tr:
            a, b = tr
            e.quad('fons_costat', (XO, h, a), (XO, h, b), (XO, 0, b), (XO, 0, a), ramp=SOOT,
                   lvl=_maons(3.0 - min(1.2, z / 3000), 70 + i,
                              finestres=tuple((20 + k * 46, 40 + j * 50, 18, 24, hr(i, k, j, 3) > 0.8)
                                              for k in range(int((b - a) // 46) - 1) for j in range(2))))
        z += w
        i += 1


def voreres(e, lluny):
    """Les voreres: trenquen la línia de la paret amb el terra (`lluny`: les del carrer del costat, més enllà de la
    plaça; si no, les d'abans, que es pinten després de la nau)."""
    lv = {'ramp': MORTAR, 'lvl': lambda s, t, P: 3.8 - (1.4 if s % 28 < 1.2 else 0)}
    if lluny:
        e.caixa('vorera', X0 - 28, X0, 0, 4, ZF, 5200, MORTAR, 2.2,
                cares={'dalt': lv, 'esquerra': {'ramp': MORTAR, 'lvl': 2.6}})
        e.caixa('vorera', XO, XO + 26, 0, 4, ZF, 5200, MORTAR, 2.2,
                cares={'dalt': lv, 'dreta': {'ramp': MORTAR, 'lvl': 2.0}})
        return
    e.caixa('vorera', X0 - 28, 3000, 0, 4, ZR - 32, ZR, MORTAR, 2.2,
            cares={'dalt': lv, 'davant': {'ramp': MORTAR, 'lvl': lambda s, t, P: 2.6 - (1.0 if s % 28 < 1 else 0)}})
    e.caixa('vorera', X0 - 28, X0, 0, 4, ZR - 32, ZE, MORTAR, 2.2,
            cares={'dalt': lv, 'esquerra': {'ramp': MORTAR, 'lvl': 2.6}, 'darrere': {'ramp': MORTAR, 'lvl': 2.0}})
    e.caixa('vorera', XO, XO + 26, 0, 4, ZR - 120, ZE, MORTAR, 2.2,
            cares={'dalt': lv, 'dreta': {'ramp': MORTAR, 'lvl': 2.0}})


# ─── La Cantimplora ──────────────────────────────────────────────────────────

def nau(e):
    """La Cantimplora canònica, de través a la plaça: el costat de la porta, la bodega encesa i la rampa baixada. El
    sol baix de l'esquerra la il·lumina de biaix i el fum de Ferrum l'empolsa (el to de la sala); l'ombra cau cap a
    la dreta i enrere, per la plaça."""
    NAU.dibuixa(e, ombra={'sol': _SOL_DIR, 'k': 0.5, 'esvaeix': 400}, to=((120, 86, 72), 0.22))
    NAU.resplendor(e.cv, k=0.7)


# ─── El piquet, la font, els comptadors, el condensador ─────────────────────────

def piquet(e, tex):
    T = tex
    (ax, az), (bx, bz) = PANC
    # les ombres, primer
    ombra(e, BIDO[0], BIDO[1], 14, 26)
    for nx, nz in NENS:
        ombra(e, nx, nz, 14, 40, 0.5)
    for px, pz in PANC:
        ombra(e, px, pz, 6, 70, 0.4)
    e.foscor('ombres', (ax + 40, 0.5, az + 40), (bx + 120, 0.5, bz + 70), (bx + 120, 0.5, bz + 20), (ax + 40, 0.5, az - 10),
             lambda s, t: 0.35 * max(0.0, 1 - abs(t - 25) / 25))
    # la llum de la foguera, al terra
    e.claror((BIDO[0] - 90, 0.6, BIDO[1] + 90), (BIDO[0] + 90, 0.6, BIDO[1] + 90), (BIDO[0] + 90, 0.6, BIDO[1] - 90),
             (BIDO[0] - 90, 0.6, BIDO[1] - 90), (255, 150, 70),
             lambda s, t: 0.42 * max(0.0, 1 - math.hypot(s - 90, t - 90) / 90) ** 1.4)
    # la pancarta, girada, entre els dos pals (el pla: x 194..310, y 126..218; els pals, a 200 i 306)
    k = KP * 1.25
    pw = (PL.BANNER[1] + 2) - (PL.BANNER[0] - 2)                    # entre pals, en píxels del pla
    dx, dz = bx - ax, bz - az
    L = math.hypot(dx, dz)
    ux, uz = dx / L, dz / L
    x0f, x1f = 194, 312
    s0 = (x0f - (PL.BANNER[0] - 2)) * L / pw
    s1 = (x1f - (PL.BANNER[0] - 2)) * L / pw
    yt, yb = (216 - 126) * k, (216 - 218) * k
    A = (ax + ux * s0, yt, az + uz * s0)
    B = (ax + ux * s1, yt, az + uz * s1)
    e.quad('pancarta', A, B, (B[0], yb, B[2]), (A[0], yb, A[2]), tex=(T['pancarta'], (x0f, 126, x1f, 218)),
           dues_cares=True)
    # la canalla, en caixes, i el bidó
    peus = ((204, 140, 242, 229, 224, 226), (262, 140, 298, 231, 282, 228), (298, 140, 320, 225, 308, 222))
    for i, ((nx, nz), (x0, y0, x1, y1, fx, fy)) in enumerate(zip(NENS, peus)):
        e.sprite(f'nen{i}', T['canalla'].crop((x0, y0, x1, y1)), (fx - x0, fy - y0), (nx, 0, nz), escala_img=KP)
    e.sprite('bido', T['bido'].crop((236, 192, 268, 227)), (16, 32), (BIDO[0], 0, BIDO[1]), escala_img=KP)


FONT_ALT = 88                                      # (el pilar de la font, més alt que el de sempre: hi cap la pantalla)


def _pantalla_img(mosca=False):
    """La pantalla «VERNE S.A. CONTRACTA», a 1:1 (és text: escalada amb la font es desfaria)."""
    cv = Canvas(PANTALLA_W + 4, PANTALLA_H + 4, light=TEXL, transparent=True)
    pantalla_contracta(cv, 2 + PANTALLA_W // 2, PANTALLA_H + 1, mosca)
    return cv.img.crop(cv.img.getbbox())


def font(e, tex):
    ombra(e, FONT[0], FONT[1], 22, 70, 0.55)
    fx, fy = PL.FONT
    top = FONT_ALT + 8
    e.sprite('font', tex['font'].crop((fx - 26, fy - top, fx + 26, fy + 4)), (26, top), (FONT[0], 0, FONT[1]),
             escala_img=KP)
    pantalla(e)


def pantalla(e, mosca=False):
    """La pantalla, damunt el pilar (entre el lector i el broc), píxel a píxel."""
    img = _pantalla_img(mosca)
    peu = (FONT[0], PANTALLA_BASE * KP, FONT[1])
    e.sprite('font', img, (img.width // 2, img.height - 1), peu, escala_img=1 / CAM.escala(peu))


def comptadors(e, tex):
    ombra(e, COMPT[0], COMPT[1], 28, 18, 0.5)
    e.sprite('comptadors', tex['comptadors'].crop((394, 198, 464, 236)), (35, 32), (COMPT[0], 0, COMPT[1]),
             escala_img=KP * 1.1)


def condensador(e, tex):
    """El condensador vell de la mina: una caixa de llauna girada, sobre un dipòsit i quatre potes."""
    cx, cz, ang = COND
    x0, x1, base = PL.COND
    w = (x1 - x0 + 2) * KP
    d = 34.0
    ombra(e, cx, cz, 40, 74, 0.55)
    c, s_ = math.cos(ang), math.sin(ang)
    for lx, lz in ((-w / 2 + 5, -d / 2 + 4), (w / 2 - 5, -d / 2 + 4), (-w / 2 + 5, d / 2 - 4), (w / 2 - 5, d / 2 - 4)):
        e.caixa_girada('cond', cx + lx * c - lz * s_, cz + lx * s_ + lz * c, 3, 3, 16, ang, IRONF, 2.6)
    T = tex['cond']
    aletes = {'ramp': TIN, 'lvl': lambda s, t, P: 3.0 + (1.4 if s % 3 < 1 else -0.4) - t * 0.01}
    e.caixa_girada('cond_diposit', cx, cz, w - 4, d - 4, 15, ang, RUSTF, 3.0, y0=15,
                   cares={'davant': {'tex': (T, (x0 + 2, base - 30, x1 - 1, base - 15))},
                          'dalt': {'ramp': RUSTF, 'lvl': 3.6}, 'esquerra': {'ramp': RUSTF, 'lvl': 2.4},
                          'dreta': {'ramp': RUSTF, 'lvl': 2.0}})
    e.caixa_girada('cond_cos', cx, cz, w, d, 44, ang, TIN, 3.0, y0=30,
                   cares={'davant': {'tex': (T, (x0, base - 74, x1 + 1, base - 30))},
                          'dalt': {'ramp': TIN, 'lvl': lambda s, t, P: 4.8 - (1.0 if s % 9 < 1 else 0)},
                          'esquerra': aletes, 'dreta': aletes})
    # el tub, que puja i se'n va cap a la paret de la fosa
    top = (cx + (w / 2 - 10) * c - 4 * s_, 74, cz + (w / 2 - 10) * s_ + 4 * c)
    e.tub('cond', top, (top[0], 118, top[2]), 3.4, IRONF, 2.8)
    e.tub('cond', (top[0], 118, top[2]), (top[0], 118, FZ - 1), 3.4, IRONF, 2.8, brides=40)
    lector(e)


# el lector de targetes de Verne, cargolat al costat que es veu (el de les aletes): (lz0, lz1, y0, y1) i el gruix
LECTOR = (-7.0, 7.0, 38.0, 54.0)
LECTOR_G = 3.0
GREENL = PL.GREENL
LECTOR_RAMP = BLACKT[:3] + REDV                     # (0..2: la pantalleta i la ranura; 3..8: la caixa vermella)


def lector(e):
    """El lector de targetes nou de trinca: una caixa vermella cargolada a la cara de les aletes, amb la pantalleta,
    la ranura i el llum vermell (engegat, el posa verd lector_engegat)."""
    x0, x1, base = PL.COND
    w = (x1 - x0 + 2) * KP
    lz0, lz1, y0, y1 = LECTOR
    cx, _, cz = _cond_punt(-w / 2 - LECTOR_G / 2, 0, (lz0 + lz1) / 2)
    L, H_ = lz1 - lz0, y1 - y0

    def cara(s, t, P):                                   # s: d'esquerra a dreta (de lz1 a lz0); t: de dalt avall
        if 2 <= s <= L - 4 and 3 <= t <= 6:
            return 6.4 if s < 4 and 4 <= t <= 5 else 1.2                               # la pantalleta (i el text)
        if 2 <= s <= L - 2 and 9 <= t <= 10:
            return 0.4                                                                   # la ranura
        if L - 3.5 <= s <= L - 1.5 and H_ - 4.5 <= t <= H_ - 2:
            return 8.4                                                                   # el llum, vermell
        return 6.0 - s * 0.08 + (1.0 if t < 1.2 else 0) - (1.2 if t > H_ - 1.2 else 0)
    e.caixa_girada('cond', cx, cz, LECTOR_G, L, H_, COND[2], REDV, 3.0, y0=y0,
                   cares={'esquerra': {'ramp': LECTOR_RAMP, 'lvl': cara}, 'dalt': {'ramp': REDV, 'lvl': 4.4},
                          'davant': {'ramp': REDV, 'lvl': 2.2}})


# ─── El primer pla ──────────────────────────────────────────────────────────

def primer_pla(e):
    # el fanal de ferro colat, molt a prop, a l'esquerra: el pal, el braç i el llum (encès)
    fx, fz = FANAL
    e.caixa('primer_pla', fx - 5, fx + 5, 0, 330, fz - 5, fz + 5, IRONF, 1.4,
            cares={'davant': {'ramp': IRONF, 'lvl': lambda s, t, P: 1.0 + (1.2 if s > 7 else 0) - (0.8 if s < 2 else 0)
                              + (1.0 if int(P[1]) % 90 < 4 else 0)},
                   'dreta': {'ramp': IRONF, 'lvl': 1.8}})
    e.caixa('primer_pla', fx - 9, fx + 9, 0, 22, fz - 9, fz + 9, IRONF, 1.6)                  # la base
    e.caixa('primer_pla', fx, fx + 60, 300, 305, fz - 2, fz + 2, IRONF, 1.6)                 # el braç
    e.caixa('primer_pla', fx + 52, fx + 68, 280, 300, fz - 8, fz + 8, IRONF, 1.2,
            cares={'davant': {'ramp': GLOWF, 'lvl': 4.6}, 'dalt': {'ramp': IRONF, 'lvl': 1.2}})
    # els cables: del fanal a la cantonada del sindicat i a les cases, amb panxa
    for B in ((X0 + 8, SH - 10, ZR - 1), (CX0 + 60, CH - 6, CZ - 1), (FX0 + 100, FH - 30, FZ - 1)):
        A = (fx + 60, 296, fz)
        M = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2 - 34, (A[2] + B[2]) / 2)
        e.cable('cables', [A, M, B], COAL, 0.8, gruix=1.0)
    # caixes de fusta i sacs de carbó, a terra, a l'esquerra (es veuen tallats)
    for (x, z, w, d, h, a, y0) in ((-14, 404, 44, 30, 30, 0.35, 0), (-18, 400, 36, 26, 24, 0.6, 30)):
        e.caixa_girada('primer_pla', x, z, w, d, h, a, PLANKF, 1.4, y0=y0,
                       cares={'dalt': {'ramp': PLANKF, 'lvl': lambda s, t, P: 2.6 - (1.0 if int(t) % 7 == 0 else 0)},
                              'davant': {'ramp': PLANKF, 'lvl': lambda s, t, P: 1.6 - (0.8 if int(t) % 6 == 0 else 0)},
                              'dreta': {'ramp': PLANKF, 'lvl': 1.0}})
    for k, (x, z, r) in enumerate(((34, 392, 15), (22, 380, 12))):
        e.roca('primer_pla', (x, 0, z), r, COAL, 1.6, llum_dir=(-0.7, -0.6), seed=k + 3)
    # la vagoneta, al carril, a la dreta (tallada per la vora)
    vx, vz = VAGO
    e.caixa_girada('primer_pla', vx, vz, 70, 46, 40, -0.25, RUSTF, 1.6, y0=12,
                   cares={'dalt': {'ramp': COAL, 'lvl': lambda s, t, P: 1.4 + (fbm(s / 4, t / 4, 9) - 0.5) * 1.6},
                          'davant': {'ramp': RUSTF, 'lvl': lambda s, t, P: 1.8 - (0.9 if s % 23 < 2 else 0)
                                     + (0.8 if t < 3 else 0)},
                          'esquerra': {'ramp': RUSTF, 'lvl': 2.4}})
    for k in range(5):                                                  # el carbó, en munt
        e.roca('primer_pla', (vx - 26 + k * 13, 50, vz + (k % 2) * 6), 9, COAL, 2.0, seed=10 + k)
    for wx in (-22, 22):
        c, s_ = math.cos(-0.25), math.sin(-0.25)
        e.caixa_girada('primer_pla', vx + wx * c, vz + wx * s_ - 22, 14, 3, 14, -0.25, IRONF, 1.2)


# ─── La llum càlida ─────────────────────────────────────────────────────────

def llum_finestres(e, tex):
    """La claror de les finestres enceses del sindicat, les cases i la fosa, a les llambordes de davant."""
    for key, box, x0, z in (('sindicat', SC, X0, ZR), ('cases', CC, CX0, CZ), ('fosa', FC, FX0, FZ)):
        for fx0, fy0, fx1, fy1 in finestres_enceses(tex[key], box):
            llum_finestra(e, x0 + (fx0 - box[0]) * KF, x0 + (fx1 - box[0]) * KF, (box[3] - fy1) * KF,
                          (box[3] - fy0) * KF, z, dx=0.35)


# els fanals de paret (x a la façana, l'alçada, z de la façana): el del sindicat, entre la cantonada i la porta; el de
# les cases; el del portal de la fosa
FANALS_PARET = ((X0 + 26, 150, ZR), (CX0 + 104, 132, CZ), (FX0 + 36, 150, FZ))


def fanals_paret(e):
    return [fanal_paret(e, 'fanals', x, y, z, IRONF, GLOWF) for x, y, z in FANALS_PARET]


def llum_fanals(e, caps, cons=True):
    """Els fanals encesos: el del primer pla (la bassa de llum, a baix a l'esquerra) i els de paret (la bassa a les
    llambordes, endavant i a la dreta, i el con en diagonal). `cons`: el con a l'aire (després de tot, menys el
    primer pla)."""
    fx, fz = FANAL
    if not cons:
        bassa_fanal(e, fx + 60, fz + 20, r=130, k=0.5)
        for x, y, z in caps:
            bassa_fanal(e, x + 30, z - 70, r=105, k=0.55)
        return
    for x, y, z in caps:
        con_fanal(e, (x, y, z), r=60, k=0.22, salta=('primer_pla', 'cables'), terra=(x + 30, z - 70))


# ─── Composició ─────────────────────────────────────────────────────────────

def escena(cv, tex):
    e = Escena(cv, CAM, LLUMS, ambient=AMBIENT)
    fons(cv)
    e.quad('terra', (-80000, 0, 40000), (80000, 0, 40000), (80000, 0, 200), (-80000, 0, 200), ramp=COB, lvl=_terra)
    # la boira de fum: el fons es confon amb el cel
    e.claror((-80000, 0.2, 40000), (80000, 0.2, 40000), (80000, 0.2, 1400), (-80000, 0.2, 1400), (150, 112, 90),
             lambda s, t: 0.6 * smooth(600, 9000, 40000 - t))
    canonada(cv, CAN_U, 70)                                         # (la base, darrere les cases del carrer del costat)
    carrer_costat(e, lluny=True)
    voreres(e, lluny=True)
    nau(e)
    carrer_costat(e, lluny=False)
    voreres(e, lluny=False)
    e.foscor('racons', (X0 - 28, 4.5, ZR), (3000, 4.5, ZR), (3000, 4.5, ZR - 32), (X0 - 28, 4.5, ZR - 32),
             lambda s, t: 0.5 * max(0.0, 1 - t / 18))
    facanes(e, tex)
    llum_finestres(e, tex)
    caps = fanals_paret(e)
    llum_fanals(e, caps, cons=False)
    carrils(e)
    comptadors(e, tex)
    font(e, tex)
    condensador(e, tex)
    piquet(e, tex)
    llum_fanals(e, caps)
    primer_pla(e)
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


# ─── Decorats ───────────────────────────────────────────────────────────────

def _sobre(fn):
    """Un llenç transparent de sala amb una Escena de la mateixa càmera: per pintar-hi coses del món soltes."""
    cv = Canvas(light=LIGHT, transparent=True)
    e = Escena(cv, CAM, LLUMS, ambient=AMBIENT)
    fn(e)
    return cv.img


def barril_piquet(cv):
    """L'últim barril de la Cantimplora, al piquet, amb gots de llauna a sobre (i la seva ombra)."""
    img = _pla(PL.barril_piquet)

    def fn(e):
        ombra(e, BARRIL[0], BARRIL[1], 12, 30, 0.5)
        e.sprite('barril', img.crop((310, 198, 336, 234)), (12, 32), (BARRIL[0], 0, BARRIL[1]), escala_img=KP)
    # (l'ombra només es veu sobre el terra: es pinta sobre una còpia del fons i es queda la diferència)
    base, _ = _base()
    on = base.copy()
    cv2 = Canvas(light=LIGHT, img=on)
    e = Escena(cv2, CAM, LLUMS, ambient=AMBIENT)
    fn(e)
    cv.img.alpha_composite(_diff(on, base))


def _cond_punt(lx, y, lz=None):
    """Un punt de la cara del davant del condensador (lx des del centre, en unitats; y amunt) al món."""
    cx, cz, ang = COND
    d = 34.0
    lz = -d / 2 if lz is None else lz
    c, s_ = math.cos(ang), math.sin(ang)
    return (cx + lx * c - lz * s_, y, cz + lx * s_ + lz * c)


def lector_engegat(e):
    """El lector, engegat: el llum verd, la pantalleta en verd i la targeta blava de la Mosca a la ranura, que en
    sobresurt."""
    x0, x1, base = PL.COND
    w = (x1 - x0 + 2) * KP
    lz0, lz1, y0, y1 = LECTOR
    a = -w / 2 - LECTOR_G - 0.3                          # (just davant la cara del lector)
    L, H_ = lz1 - lz0, y1 - y0

    def q(sid, s0, s1, t0, t1, ramp, lvl, lx=a):        # un rectangle de la cara (s, t com a `lector`)
        e.quad(sid, _cond_punt(lx, y1 - t0, lz1 - s0), _cond_punt(lx, y1 - t0, lz1 - s1),
               _cond_punt(lx, y1 - t1, lz1 - s1), _cond_punt(lx, y1 - t1, lz1 - s0), ramp=ramp, lvl=lvl,
               dues_cares=True)
    q('lector_on', L - 3.5, L - 1.5, H_ - 4.5, H_ - 2, GREENL, 3.6)                     # el llum, verd
    q('lector_on', 2, 4, 4, 5, GREENL, 3.0)                                              # la pantalleta: «OK»
    q('lector_on', 2.5, L - 2.5, 9, 12.5, BLUEV, lambda s, t, P: 2.6 + (1.0 if t < 1 else 0))   # la targeta
    # el tros que sobresurt de la ranura, cap enfora
    ys = y1 - 9
    e.quad('lector_on', _cond_punt(a - 5, ys, lz1 - 2.5), _cond_punt(a - 5, ys, lz0 + 2.5),
           _cond_punt(a, ys, lz0 + 2.5), _cond_punt(a, ys, lz1 - 2.5), ramp=BLUEV, lvl=3.6, dues_cares=True)


def condensador_arreglat(cv):
    """El condensador arreglat: el llum verd encès, la corretja posada, l'aixeta oberta i un toll a terra; i el lector
    de Verne, engegat amb la targeta de la Mosca."""
    base_img, e = _base()
    flat = _pla(PL.condensador_arreglat)
    cv.img.alpha_composite(e.capa(flat, {'cond_cos', 'cond_diposit'}))
    on = base_img.copy()
    e2 = Escena(Canvas(light=LIGHT, img=on), CAM, LLUMS, ambient=AMBIENT)
    lector_engegat(e2)
    cv.img.alpha_composite(_diff(on, base_img))
    x0, x1, base = PL.COND
    w = (x1 - x0 + 2) * KP
    tap = _cond_punt(-w / 2 + 12.5, 12)
    # el raig d'aigua de l'aixeta i el toll
    u0, v0, _ = CAM.projecta(tap)
    u1, v1, _ = CAM.projecta((tap[0], 0, tap[2]))
    for k in range(int(v1 - v0) + 1):
        cv.flat(u0, v0 + k, WATER[3 if k % 2 else 4])

    def toll(e2):
        e2.quad('toll', (tap[0] - 18, 0.4, tap[2] + 6), (tap[0] + 18, 0.4, tap[2] + 6), (tap[0] + 18, 0.4, tap[2] - 16),
                (tap[0] - 18, 0.4, tap[2] - 16), ramp=WATER, lvl=lambda s, t, P: 2.0 + (1.6 if (s + t) % 9 < 1.5 else 0),
                forma=lambda s, t: ((s - 18) / 18) ** 2 + ((t - 11) / 11) ** 2 <= 1)
    cv.img.alpha_composite(_sobre(toll))


def pantalla_mosca(cv):
    """La pantalla de la font, un cop Verne ha contractat la Mosca: «FELICITATS / MOSCA!»."""
    cv.img.alpha_composite(_sobre(lambda e: pantalla(e, mosca=True)))


PROPS = {'barril_piquet': barril_piquet, 'condensador_arreglat': condensador_arreglat,
         'pantalla_mosca': pantalla_mosca}


# ─── Animacions ─────────────────────────────────────────────────────────────

def _frames_foc():
    """La foguera del bidó: les flames planes de sempre, posades al bidó (a la seva mida)."""
    out = []
    for fr in PL._frames_foc():
        crop = fr.crop((236, 150, 268, 227))

        def fn(e, crop=crop):
            e.sprite('foc', crop, (16, 74), (BIDO[0], 0, BIDO[1]), escala_img=KP)
        out.append(_sobre(fn))
    return out


def _fonts_fum():
    out = []
    for fx, ct in PL.CHIMNEYS:
        x = CX0 + (fx - CC[0]) * KF
        top = CH + 52 + (60 - ct) * 0.6 + 5
        u, v, _ = CAM.projecta((x, top, CZ + 51))
        k = CAM.escala((x, top, CZ + 51))
        out.append((u, v, 3 * k + 1, 40 * k))
    return out


def _frames_fum():
    """El fum de les xemeneies de les cases (estufes de carbó): puja i el vent l'estira cap a la dreta."""
    base, _ = _base()
    return _smoke_loop(base, _fonts_fum(), 12)


def _frames_goteig():
    """La gota de l'aixeta del condensador arreglat: es fa, cau i esquitxa el toll."""
    x0, x1, base = PL.COND
    w = (x1 - x0 + 2) * KP
    tap = _cond_punt(-w / 2 + 12.5, 12)
    u0, v0, _ = CAM.projecta(tap)
    u1, v1, _ = CAM.projecta((tap[0], 0, tap[2]))
    frames = []
    n = 10
    for f in range(n):
        cv = Canvas(transparent=True)
        if f < 5:
            cv.flat(u0, v0 + 1, WATER[3])
            if f >= 3:
                cv.flat(u0, v0 + 2, WATER[4])
        elif f < 8:
            y = v0 + 2 + (f - 4) ** 2 * (v1 - v0) / 16
            if y < v1:
                cv.flat(u0, y, WATER[4])
                cv.flat(u0, y - 1, WATER[2])
        else:
            for dx in ((-2, 2) if f == 8 else (-3, 3)):
                cv.flat(u1 + dx, v1, WATER[5])
        frames.append(cv.img)
    return frames


ANIMS = {'foc': {'frames': _frames_foc, 'frameDuration': 110},
         'fum': {'frames': _frames_fum, 'frameDuration': 160},
         'goteig': {'frames': _frames_goteig, 'frameDuration': 120}}


# ─── Capes del davant ─────────────────────────────────────────────────────────

def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _v(x, z):
    return round(CAM.projecta((x, 0, z))[1])


FRONT = [
    {'id': 'davant', 'mask': _amo({'primer_pla', 'cables'}), 'baseline': 999, 'zIndex': 20},
    {'id': 'davant_font', 'mask': _amo({'font'}), 'baseline': _v(FONT[0], FONT[1]), 'zIndex': 20},
    {'id': 'davant_bido', 'mask': _amo({'bido'}), 'baseline': _v(*BIDO), 'zIndex': 20},
    *[{'id': f'davant_nen{i}', 'mask': _amo({f'nen{i}'}), 'baseline': _v(*p), 'zIndex': 20} for i, p in enumerate(NENS)],
    {'id': 'davant_pancarta', 'mask': _amo({'pancarta'}),
     'baseline': _v((PANC[0][0] + PANC[1][0]) / 2, (PANC[0][1] + PANC[1][1]) / 2), 'zIndex': 20},
    # la rampa de la Cantimplora: qui va entre la rampa i la vorera, cap al buc, hi passa per darrere
    {'id': 'davant_rampa', 'mask': _amo({'rampa'}), 'baseline': _v(*NAU.terra(sum(PORTA_L) / 2, RAMPA_OUT * 0.75)),
     'zIndex': 20},
    {'id': 'davant_condensador', 'mask': _amo({'cond', 'cond_cos', 'cond_diposit'}), 'baseline': _v(COND[0], COND[1] - 14),
     'zIndex': 20},
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


def _cercle(cx, cz, r, n=8):
    return [_p(cx + r * math.cos(2 * math.pi * i / n), cz + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


# El terra on es camina (al món): el carrer davant les façanes (sense pujar a la vorera), i el carrer del costat fins
# a la Cantimplora: el peu de la rampa, per davant, i entre la rampa i la vorera fins arran del buc (allà es passa
# per darrere de la rampa: la càmera és a l'altra banda); no arriba a les caixes del primer pla ni al fanal.
_VMAX = 256
_ZV = ZR - 36                                     # davant la vorera
_SL = sum(PORTA_L) / 2
_NAU_W = [NAU.terra(PORTA_L[1] + 44, 130), NAU.terra(PORTA_L[1] + 10, 130), NAU.terra(PORTA_L[1] + 10, RAMPA_OUT + 14),
          NAU.terra(PORTA_L[0] - 10, RAMPA_OUT + 14), NAU.terra(PORTA_L[0] - 8, 112)]
_NAU_W = [(min(x, X0 - 34), z) for x, z in _NAU_W]                 # (sense pujar a la vorera del sindicat)
WALK_MON = [
    *_NAU_W, (X0 - 34, _NAU_W[-1][1]), (X0 - 34, ZR - 4), (X0 - 34, _ZV),
    (FX0 - 10, _ZV), (FX0 - 10, FZ - 36), (FX1 + 300, FZ - 36),
]
_WALK = [_p(x, z) for x, z in WALK_MON]
_WALK = [(min(W - 1, max(0, u)), v) for u, v in _WALK]
_WALK += [(W - 1, _p(FX1 + 300, FZ - 36)[1]), (W - 1, _VMAX), (0, _VMAX), (0, _p(*_NAU_W[0])[1] + 6)]
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)


_PORTA_S = (_sind(108, 101), _sind(150, 193))
_PORTAL = (_fosa(482, 82), _fosa(580, 193))
_PANELL = (_cases(327, 97), _cases(388, 122))
_U_SOMBRA = CAM.projecta((300 + OMBRA[0] * 60, 0, 560 + OMBRA[1] * 60))
_U_SOMBRA0 = CAM.projecta((300, 0, 560))

GEOMETRIA = {
    'things': {
        'rampa': {'rect': _rect_mon(NAU.buc(PORTA_L[0] - 6, PORTA_T[1] + 0.06), NAU.buc(PORTA_L[1] + 6, PORTA_T[1] + 0.06),
                                    *NAU.rampa_cantons()),
                  'walk': _p(*NAU.terra(_SL, RAMPA_OUT + 22))},
        'porta_sindicat': {'rect': _rect_mon(*_PORTA_S), 'walk': _p(_PORTA_S[0][0] + 26, ZR - 46)},
        'porta_fosa': {'rect': _rect_mon(*_PORTAL), 'walk': _p((_PORTAL[0][0] + _PORTAL[1][0]) / 2, FZ - 44)},
        'font': {'rect': _rect_mon((FONT[0] - 26, FONT_ALT + 6, FONT[1]), (FONT[0] + 26, 0, FONT[1])),
                 'walk': _p(FONT[0] - 40, FONT[1] - 30)},
        'condensador': {'rect': _rect_mon(_cond_punt(-36, 128), _cond_punt(36, 0), _cond_punt(36, 0, 17),
                                          _cond_punt(-36, 0, 17), (_cond_punt(30, 118)[0], 118, FZ)),
                        'walk': _p(COND[0] - 30, COND[1] - 60)},
        'piquet': {'rect': _rect_mon((PANC[0][0], 120, PANC[0][1]), (PANC[1][0], 120, PANC[1][1]),
                                     (NENS[0][0] - 20, 0, NENS[0][1]), (NENS[2][0] + 10, 0, NENS[2][1])),
                   'walk': _p(BIDO[0] - 70, BIDO[1] - 36)},
        'comptadors': {'rect': _rect_mon((COMPT[0] - 40, 34, COMPT[1]), (COMPT[0] + 40, 0, COMPT[1] + 6)),
                       'walk': _p(COMPT[0] - 10, COMPT[1] - 46)},
        'panell_preu': {'rect': _rect_mon(*_PANELL), 'walk': _p(_PANELL[0][0] + 30, ZR - 46)},
        'canonada': {'rect': (CAN_U - 7, 0, CAN_U + 7, 60), 'walk': _p(X0 - 60, ZR + 40)},
    },
    # l'Iri i la Vet, al peu de la rampa de la Cantimplora (hi arriben baixant de la nau), en píxels de pantalla
    'spawns': {'rosa': _p(NENS[0][0] - 50, NENS[0][1] + 20), 'iri': (122, 206), 'vet': (88, 193)},
    'walkable': _WALK,
    'forats': [_cercle(FONT[0], FONT[1], 26), _cercle(BIDO[0], BIDO[1], 20, 6),
               *[_cercle(x, z, 16, 6) for x, z in NENS], _cercle(COND[0], COND[1], 46),
               _cercle(COMPT[0], COMPT[1] + 4, 34, 6), _cercle(FANAL[0], FANAL[1], 14, 6),
               [_p(*PANC[0]), _p(*PANC[1]), _p(PANC[1][0], PANC[1][1] - 8), _p(PANC[0][0], PANC[0][1] - 8)]],
    # la càmera, a 1,7 m i mirant avall, veu el terra aixafat: 170 d'alçada a ≈600 de fons
    'floorSquash': 0.3,
    # el sol, baix a l'esquerra: les ombres de la gent cauen cap a la dreta, com les dels objectes
    'characterShadow': {'enabled': True, 'color': '#1a1012', 'alpha': 0.42, 'squash': 0.3, 'core': 0.6,
                        'light': {'x': round(_U_SOMBRA[0] - _U_SOMBRA0[0], 2), 'y': round(_U_SOMBRA[1] - _U_SOMBRA0[1], 2),
                                  'direction': True, 'stretch': 1.0}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
    # La llum de la sala sobre els personatges (characterLights del motor): el carrer al capvespre: una mica fosc i
    # morat, el sol baix a l'esquerra i la foguera.
    'characterLights': {
        'ambient': '#8a7a7c',
        'lights': [
            {'x': -200, 'y': 100, 'radius': 900, 'color': '#ffb478', 'intensity': 0.25},  # el sol baix, a l'esquerra
            llum_personatges(CAM, LLUMS[1].pos, LLUMS[1].r, '#ff9040', 0.7),  # la foguera
        ],
    },
}
