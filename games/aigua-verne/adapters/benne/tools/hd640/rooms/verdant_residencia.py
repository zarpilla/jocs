"""
Aigua Verne — `verdant_residencia` (P, de prop: persones de ≈100 px). Escena 5. EN 3D (hd640/tres_d.py), a 1×.

El despatx d'estiu del Magnat, a la residència de Verdant: tot blanc i or, net com una sala d'exposició on no viu
ningú. Vist de biaix i una mica des de dalt, com el pont de la Cantimplora: la paret de la **porta** (blanca, plafons
d'or, torna al jardí) fuig cap a la cantonada; a la paret del fons, el **quadre** enorme del Magnat amb en Dividend,
els apliques i el **finestral** al jardí, amb les cortines. L'**arxivador** blanc dels calaixos «DEUTORS», «DRETS» i
«PEIXOS» (amb el trofeu de la gota d'or) és a la dreta del finestral, girat cap a la sala; la **calaixera** de laca, separada de la
paret, sota el quadre, amb el gerro de flors de plàstic i el telèfon d'or; la **paperera daurada**, al mig, i s'hi
passa per darrere. El terra de marbre amb vetes d'or (les lloses s'empetiteixen cap al fons) i la catifa blanca amb
la gota; el sol del finestral entra en diagonal i fa una taca pel terra. Primer pla: una columna blanca a l'ombra,
a l'esquerra, i una butaca de pell blanca, a contrallum, a baix a la dreta.

El detall ve del despatx pla de sempre (verdant_residencia_pla_comu.py), dibuixat de cara i projectat: la paret, la
porta, el quadre, els apliques, el finestral, el davant de l'arxivador i de la calaixera, el trofeu, el gerro i el
telèfon.

El món: x a la dreta (0 = la paret de la porta), y amunt (0 = el terra), z cap al fons (300 = la paret del quadre);
1 unitat = 1 píxel de sala a la distància on un personatge fa 100 px (escala 1).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)

from hd.pix import Canvas, Light, W, H, hr
from hd.rooms.exterior import fbm
from hd640.rooms import verdant_residencia_pla_comu as PL
from hd640.rooms.verdant_comu import WHITEV, MARBLE, GOLDV, BLUEG
from hd640.tres_d import Camera, Escena, Llum

BOTTOM = 259                                       # la sala acaba aquí (a sota, la barra de verbs)
ZW = 300                                           # la paret del fons (el quadre)
TY0 = 8                                            # al dibuix pla, la paret comença aquí (la cornisa)
HW = PL.FLOOR_Y - TY0                              # l'alçada de les parets
XL = 100                                           # al dibuix pla, la cantonada: a l'esquerra, la paret de la porta
XR = W - XL                                        # on s'acaba el dibuix pla a la paret del fons
DOOR_Z = (ZW - XL + PL.DOOR[0], ZW - XL + PL.DOOR[2])
WIN_X = (PL.WIN[0] - XL, PL.WIN[2] - XL)           # el finestral, a la paret del fons
WIN_Y = (PL.FLOOR_Y - PL.WIN[3], PL.FLOOR_Y - PL.WIN[1])
ARX = (530, 262, 58, 40, 0.5)                     # l'arxivador: centre (x, z), amplada, fondària, gir
ARX_H = PL.FLOOR_Y - PL.ARX[1]
CALAIX = (176, 272, 136, 34, 0.06)                 # la calaixera
CAL_H = PL.FLOOR_Y - PL.CALAIX[1]
PAPER = (318, 214)                                 # la paperera (x, z)
CATIFA = (120, 120, 330, 230)                      # la catifa: x0, z0, x1, z1
APLIQUES = [(ax - XL, 140, ZW - 6) for ax in (176, 372)]

CAM = Camera(pos=(290, 190, -190), yaw=-0.12, pitch=0.16, f=380, centre=(330, 72))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)   # (la llum és la del món: la de l'Escena)
LLUMS = [Llum((x, y, z - 10), 150, 0.8, power=1.5) for x, y, z in APLIQUES] + [
    Llum(((WIN_X[0] + WIN_X[1]) / 2, 110, ZW - 30), 340, 1.6, power=1.2),     # el sol del finestral
    Llum((300, 180, 120), 420, 0.6, power=1.0),                                  # la claror general
]
AMBIENT = -0.4
TL = Light(ambient=0.5, vignette=None, floor_fade=None)       # la llum de les textures (plana: la posa el món)
SUN = (255, 252, 236)
# el sol entra pel finestral, de dalt a la dreta: cau cap endavant i a l'esquerra
RAIG = (-0.42, -1.0, -0.9)


# ─── Les textures: el despatx pla de sempre ──────────────────────────────────

def _pla(fn, transparent=True):
    cv = Canvas(light=TL, transparent=transparent)
    fn(cv)
    return cv.img


@functools.lru_cache(maxsize=None)
def _paret():
    def fn(cv):
        PL.paret(cv)
        PL.porta(cv)
        PL.quadre(cv)
        PL.apliques(cv)
        PL.finestral(cv)
    return _pla(fn, transparent=False)


@functools.lru_cache(maxsize=None)
def _retall(nom):
    """Un dibuix pla retallat: (imatge, (x0, y0, x1, y1) o el punt de la imatge que toca a terra)."""
    if nom == 'arxivador':
        img = _pla(PL.arxivador)
        x0, y0, x1, y1 = PL.ARX
        return img, (x0, y0, x1 + 1, y1)
    if nom == 'trofeu':
        img = _pla(PL.arxivador)
        tx = (PL.ARX[0] + PL.ARX[2]) // 2
        return img.crop((tx - 12, PL.ARX[1] - 38, tx + 12, PL.ARX[1] - 3)), (12, 35)
    if nom == 'calaixera':
        img = _pla(PL.calaixera)
        x0, y0, x1, y1 = PL.CALAIX
        return img, (x0 - 3, y0, x1 + 4, y1)
    if nom == 'damunt':
        img = _pla(PL.calaixera)
        x0, y0, x1, y1 = PL.CALAIX
        return img.crop((x0 - 4, y0 - 34, x1 + 4, y0)), ((x1 - x0) / 2 + 4, 34)
    raise KeyError(nom)


# ─── Les superfícies ────────────────────────────────────────────────────────

def _estuc(lvl0, seed=3):
    """Paret blanca llisa, amb plafons de motllura d'or (on el dibuix pla no arriba)."""
    def L(s, t, P):
        v = lvl0 + (fbm(s / 60, t / 40, seed) - 0.5) * 0.3
        u = s % 120
        if 8 < u < 112 and (abs(t - 22) < 0.8 or abs(t - 120) < 0.8):
            v += 1.0
        if 8 < t < 120 and (abs(u - 8) < 0.8 or abs(u - 112) < 0.8):
            v += 1.0
        if t > HW - 14:
            v -= 0.3
        return v
    return L


def _marbre(s, t, P):
    """Marbre blanc en lloses de 60 (en coordenades del món), amb vetes d'or i grises, polit."""
    x, z = P[0], P[2]
    v = 4.2 + (fbm(x / 50, z / 40, 213) - 0.5) * 0.5
    vena = fbm(x / 70 + z / 30, z / 25 + x / 90, 211)
    if abs(vena - 0.5) < 0.0035:
        return 5.6                                                 # (a la rampa de marbre, l'or es fa amb un altre quad)
    if abs(vena - 0.6) < 0.01:
        v -= 0.9
    if x % 60 < 1.0 or z % 60 < 1.0:
        v -= 1.3
    return v


def _veta_or(s, t, P):
    x, z = P[0], P[2]
    vena = fbm(x / 70 + z / 30, z / 25 + x / 90, 211)
    return abs(vena - 0.5) < 0.0035


def _catifa(s, t, P):
    """La catifa blanca de pèl, amb la sanefa d'or i, al mig, la gota de Verne (vista des de dalt)."""
    w, d = CATIFA[2] - CATIFA[0], CATIFA[3] - CATIFA[1]
    v = 5.0 + (hr(int(s * 1.5), int(t * 1.5), 7) - 0.5) * 0.7
    b = min(s, t, w - s, d - t)
    if 6 < b < 9 or 11 < b < 12:
        return -1.0                                                # (la sanefa: es pinta d'or a part)
    return v


def cilindre(e, sid, cx, cz, r, y0, y1, ramp, lvl, n=24):
    """Un cilindre vertical: les facetes que es veuen. `lvl(angle, y, P)`."""
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        p0 = (cx + r * math.cos(a0), cz + r * math.sin(a0))
        p1 = (cx + r * math.cos(a1), cz + r * math.sin(a1))
        e.quad(sid, (p0[0], y1, p0[1]), (p1[0], y1, p1[1]), (p1[0], y0, p1[1]), (p0[0], y0, p0[1]), ramp=ramp,
               lvl=lambda s, t, P: lvl(math.atan2(P[2] - cz, P[0] - cx), P[1], P))


def _raig_terra(x, y, z):
    k = y / -RAIG[1]
    return (x + RAIG[0] * k, 0.0, z + RAIG[2] * k)


def _ombra_el(e, sid, cx, cz, rx, rz, k=0.5):
    e.foscor(sid, (cx - rx, 0.6, cz + rz), (cx + rx, 0.6, cz + rz), (cx + rx, 0.6, cz - rz), (cx - rx, 0.6, cz - rz),
             lambda s, t: k * min(1.0, 1.6 * max(0.0, 1 - ((s - rx) / rx) ** 2 - ((t - rz) / rz) ** 2)))


def escena(cv, tex):
    """Tota la sala, de lluny a prop. → l'Escena (qui ha pintat què)."""
    e = Escena(cv, CAM, LLUMS, ambient=AMBIENT)
    zn = CAM.pos[2] - 100
    paret = tex['paret']
    # el sostre: blanc, amb un cassetonat d'or
    e.quad('sostre', (0, HW, zn), (W + 260, HW, zn), (W + 260, HW, ZW), (0, HW, ZW), ramp=WHITEV,
           lvl=lambda s, t, P: 3.4 + (1.2 if (P[0] % 80 < 2 or P[2] % 80 < 2) else 0), dues_cares=True)
    # la paret de la porta (x = 0): de prop, estuc; de la porta a la cantonada, el dibuix pla (x 0..100)
    e.quad('paret_esq_prop', (0, HW, zn), (0, HW, ZW - XL), (0, 0, ZW - XL), (0, 0, zn), ramp=WHITEV,
           lvl=_estuc(3.0, 5))
    e.quad('paret_esq', (0, HW, ZW - XL), (0, HW, ZW), (0, 0, ZW), (0, 0, ZW - XL), tex=(paret, (0, TY0, XL, PL.FLOOR_Y)))
    # la paret del fons (z = 300): el dibuix pla (x 100..640) i, a la dreta, més estuc
    e.quad('paret_fons', (0, HW, ZW), (XR, HW, ZW), (XR, 0, ZW), (0, 0, ZW), tex=(paret, (XL, TY0, W, PL.FLOOR_Y)))
    e.quad('paret_fons_dreta', (XR, HW, ZW), (W + 260, HW, ZW), (W + 260, 0, ZW), (XR, 0, ZW), ramp=WHITEV,
           lvl=_estuc(3.6, 7))
    # el terra de marbre, amb les vetes d'or
    e.quad('terra', (0, 0, ZW), (W + 260, 0, ZW), (W + 260, 0, zn), (0, 0, zn), ramp=MARBLE, lvl=_marbre)
    e.quad('terra', (0, 0.1, ZW), (W + 260, 0.1, ZW), (W + 260, 0.1, zn), (0, 0.1, zn), ramp=GOLDV, lvl=4.0,
           forma=lambda s, t: _veta_or(s, t, (s, 0, ZW - t)))
    # la foscor dels racons (poca: tot és blanc i net)
    e.foscor('racons', (0, 0.5, ZW), (W + 260, 0.5, ZW), (W + 260, 0.5, zn), (0, 0.5, zn),
             lambda s, t: max(0.35 * max(0.0, 1 - t / 18), 0.3 * max(0.0, 1 - s / 18)))
    e.foscor('cantonada', (0, HW, ZW - 0.5), (40, HW, ZW - 0.5), (40, 0, ZW - 0.5), (0, 0, ZW - 0.5),
             lambda s, t: 0.3 * max(0.0, 1 - s / 40))
    e.foscor('cantonada2', (0.5, HW, ZW - 40), (0.5, HW, ZW), (0.5, 0, ZW), (0.5, 0, ZW - 40),
             lambda s, t: 0.3 * max(0.0, 1 - (40 - s) / 40))
    # el sol del finestral, pel terra: la taca de les vidrieres, en diagonal, amb els muntants
    g = [_raig_terra(*P) for P in ((WIN_X[0], WIN_Y[1], ZW), (WIN_X[1], WIN_Y[1], ZW), (WIN_X[1], WIN_Y[0], ZW),
                                    (WIN_X[0], WIN_Y[0], ZW))]
    mw = (WIN_X[1] - WIN_X[0])
    e.claror((g[3][0], 0.5, g[3][2]), (g[2][0], 0.5, g[2][2]), (g[1][0], 0.5, g[1][2]), (g[0][0], 0.5, g[0][2]),
             SUN, lambda s, t: 0.0 if (abs(s - mw / 3) < 2.5 or abs(s - 2 * mw / 3) < 2.5) else
             0.32 * (1 if (int(s) + int(t)) % 2 else 0.85) * min(1.0, t / 30))
    # la catifa, amb la sanefa i la gota
    cx0, cz0, cx1, cz1 = CATIFA
    e.quad('catifa', (cx0, 0.4, cz1), (cx1, 0.4, cz1), (cx1, 0.4, cz0), (cx0, 0.4, cz0), ramp=WHITEV, lvl=_catifa)
    w, d = cx1 - cx0, cz1 - cz0
    e.quad('catifa', (cx0, 0.5, cz1), (cx1, 0.5, cz1), (cx1, 0.5, cz0), (cx0, 0.5, cz0), ramp=GOLDV, lvl=4.4,
           forma=lambda s, t: (6 < min(s, t, w - s, d - t) < 9) or (11 < min(s, t, w - s, d - t) < 12))
    mx, mz = (cx0 + cx1) / 2, (cz0 + cz1) / 2

    def gota(s, t):
        x, z = s - 20, t - 20                                      # z: cap al fons (la punta)
        if z < 0:
            return x * x + z * z < 100
        return abs(x) < 10 * (1 - z / 20) and z < 20
    e.quad('catifa', (mx - 20, 0.6, mz + 20), (mx + 20, 0.6, mz + 20), (mx + 20, 0.6, mz - 20), (mx - 20, 0.6, mz - 20),
           ramp=BLUEG, lvl=lambda s, t, P: 2.6 - (s - 20) * 0.03 + (2.0 if (s - 15) ** 2 + (t - 26) ** 2 < 6 else 0),
           forma=lambda s, t: gota(s, 40 - t))
    # l'arxivador, a la dreta del finestral, girat cap a la sala; a dalt, el trofeu
    ax, az, aw, ad, aa = ARX
    img, crop = _retall('arxivador')
    _ombra_el(e, 'ombra_arx', ax - 10, az - 10, aw / 2 + 14, ad / 2 + 10, 0.45)
    e.caixa_girada('arxivador', ax, az, aw, ad, ARX_H, aa, WHITEV, 3.6,
                   cares={'davant': {'tex': (img, crop)}, 'dalt': {'ramp': GOLDV, 'lvl': 4.6},
                          'dreta': {'ramp': WHITEV, 'lvl': lambda s, t, P: 3.0 - (0.8 if t < 3 else 0)},
                          'esquerra': {'ramp': WHITEV, 'lvl': 4.2}})
    img, peu = _retall('trofeu')
    e.sprite('arxivador', img, peu, (ax, ARX_H, az))
    # la calaixera de laca, sota el quadre, separada de la paret; a sobre, el gerro i el telèfon
    kx, kz, kw, kd, ka = CALAIX
    img, crop = _retall('calaixera')
    _ombra_el(e, 'ombra_cal', kx + 8, kz - 8, kw / 2 + 10, kd / 2 + 8, 0.4)
    e.caixa_girada('calaixera', kx, kz, kw, kd, CAL_H, ka, WHITEV, 3.6,
                   cares={'davant': {'tex': (img, crop)},
                          'dalt': {'ramp': MARBLE, 'lvl': lambda s, t, P: 5.0 + (fbm(s / 20, t / 6, 5) - 0.5) * 0.6},
                          'dreta': {'ramp': WHITEV, 'lvl': lambda s, t, P: 3.0 if t > 6 else 4.4},
                          'esquerra': {'ramp': WHITEV, 'lvl': 4.0}})
    img, peu = _retall('damunt')
    e.sprite('calaixera', img, peu, (kx, CAL_H, kz))
    # la paperera daurada, al mig: el cilindre, les anelles, la boca i els papers
    px, pz = PAPER
    _ombra_el(e, 'ombra_paper', px - 10, pz - 6, 18, 10, 0.5)
    cilindre(e, 'paperera', px, pz, 10, 0, 26, GOLDV,
             lambda a, y, P: 3.6 + math.cos(a - 2.2) * 1.4 + (1.2 if abs(y - 3) < 1 or abs(y - 23) < 1 else 0)
             + (1.6 if abs(a + 1.9) < 0.15 else 0))
    e.quad('paperera', (px - 10, 26, pz + 10), (px + 10, 26, pz + 10), (px + 10, 26, pz - 10), (px - 10, 26, pz - 10),
           ramp=GOLDV, lvl=lambda s, t, P: 1.4 if (s - 10) ** 2 + (t - 10) ** 2 < 72 else 5.2,
           forma=lambda s, t: (s - 10) ** 2 + (t - 10) ** 2 < 100)
    for k, (dx, dz, r) in enumerate(((-3, 1, 4.0), (3, -2, 3.6))):
        cilindre(e, 'paperera', px + dx, pz + dz, r, 22, 29 + k, MARBLE, lambda a, y, P: 4.6 + math.cos(a - 2.2)
                 + (0.8 if hr(int(a * 4), int(y)) > 0.6 else 0), n=10)
    # els apliques: la claror a la paret (les espelmes són al dibuix pla)
    for x, y, z in APLIQUES:
        e.claror((x - 40, y + 40, ZW - 0.6), (x + 40, y + 40, ZW - 0.6), (x + 40, y - 40, ZW - 0.6),
                 (x - 40, y - 40, ZW - 0.6), (255, 236, 190),
                 lambda s, t: 0.25 * max(0.0, 1 - math.hypot(s - 40, (t - 40) * 1.2) / 40))
    # primer pla: una columna blanca a l'ombra (esquerra) i el respatller d'una butaca de pell (baix a la dreta)
    cilindre(e, 'primer_pla', 46, 56, 15, 0, HW, WHITEV,
             lambda a, y, P: 1.2 + math.cos(a - 0.6) * 0.9 - (1.2 if (a * 24 / math.pi) % 3 < 0.4 else 0), n=36)
    for y0, h in ((0, 10), (HW - 12, 12)):
        e.caixa('primer_pla', 28, 64, y0, y0 + h, 38, 74, GOLDV, 1.6,
                cares={'dalt': {'ramp': GOLDV, 'lvl': 2.6}, 'davant': {'ramp': GOLDV, 'lvl': 1.4},
                       'dreta': {'ramp': GOLDV, 'lvl': 2.0}})
    e.caixa_girada('primer_pla', 444, 30, 84, 60, 40, -0.5, WHITEV, 1.2,
                   cares={'dalt': {'ramp': WHITEV, 'lvl': lambda s, t, P: 2.2 + (0.6 if (s % 24 < 1.4) else 0)},
                          'esquerra': {'ramp': WHITEV, 'lvl': 1.0}, 'davant': {'ramp': WHITEV, 'lvl': 0.8}})
    e.caixa_girada('primer_pla', 426, 52, 84, 18, 50, -0.5, WHITEV, 1.4, y0=10,
                   cares={'dalt': {'ramp': GOLDV, 'lvl': 2.4}, 'esquerra': {'ramp': WHITEV, 'lvl': 1.2},
                          'davant': {'ramp': WHITEV, 'lvl': lambda s, t, P: 1.0 + (0.8 if abs(t - 30) < 1 else 0)
                                     + (0.5 if (s % 24) < 1.2 else 0)}})
    return e


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


PROPS = {}


def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _v(x, z):
    return round(CAM.projecta((x, 0, z))[1])


# Capes del davant: es passa per darrere de la paperera; la columna i la butaca tapen sempre.
FRONT = [
    {'id': 'davant_paperera', 'mask': _amo({'paperera'}), 'baseline': _v(*PAPER), 'zIndex': 20},
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


def _escala_a(v):
    """L'escala d'un personatge amb els peus a la y de pantalla `v` (al terra, la profunditat només depèn de v)."""
    return CAM.escala((260, 0, _z_a(260, v)))


V_PROP = 236                                       # el terra on es camina no baixa d'aquí (escala ≈1,2)
# El terra on es camina (al món): de la porta fins al finestral, de la calaixera fins a la columna i la butaca.
# Forats: l'arxivador, la calaixera i la paperera (s'hi pot fer la volta).
WALK_MON = [(14, _z_a(14, V_PROP)), (420, _z_a(420, V_PROP)), (520, 196), (520, 228), (500, 288), (262, 288), (250, 250),
            (100, 250), (90, 290), (14, 290)]
_WALK = [_p(x, z) for x, z in WALK_MON]
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)

GEOMETRIA = {
    'things': {
        'porta': {'rect': _rect_mon((0, PL.FLOOR_Y - PL.DOOR[1] + 22, DOOR_Z[0] - 10), (0, 0, DOOR_Z[1] + 10)),
                  'walk': _p(28, 252)},
        'arxivador': {'rect': _rect_mon((ARX[0] - 34, ARX_H + 38, ARX[1] - 20), (ARX[0] + 34, 0, ARX[1] + 10)),
                      'walk': _p(ARX[0] - 50, ARX[1] - 40)},
        'quadre': {'rect': _rect_mon(_fons(PL.PAINT[0] - 2, PL.PAINT[1] - 2), _fons(PL.PAINT[2] + 2, PL.PAINT[3] + 2)),
                   'walk': _p(170, 236)},
        'calaixera': {'rect': _rect_mon((CALAIX[0] - 70, CAL_H + 30, CALAIX[1] - 17), (CALAIX[0] + 70, 0, CALAIX[1] - 17)),
                      'walk': _p(CALAIX[0] + 20, CALAIX[1] - 50)},
        'paperera': {'rect': _rect_mon((PAPER[0] - 12, 32, PAPER[1]), (PAPER[0] + 12, 0, PAPER[1])),
                     'walk': _p(PAPER[0] + 28, PAPER[1] - 22)},
        'finestral': {'rect': _rect_mon(_fons(PL.WIN[0] - 14, PL.WIN[1] - 12), _fons(PL.WIN[2] + 14, PL.WIN[3])),
                      'walk': _p((WIN_X[0] + WIN_X[1]) / 2, 250)},
    },
    'spawns': {'iri': _p(170, 170), 'vet': _p(400, 190)},
    'walkable': _WALK,
    'forats': [_caixa_terra(*ARX[:2], ARX[2], ARX[3], ARX[4], 4), _caixa_terra(*CALAIX, 4),
               _caixa_terra(*PAPER, 22, 22, 0, 2)],
    'floorSquash': 0.45,
    # l'ombra de contacte: la llum dominant és el finestral (el peu de la finestra, a terra)
    'characterShadow': {'enabled': True, 'color': '#5a5a78', 'alpha': 0.35, 'squash': 0.45, 'core': 0.6,
                        'light': {'x': _p((WIN_X[0] + WIN_X[1]) / 2, ZW - 30)[0],
                                  'y': _p((WIN_X[0] + WIN_X[1]) / 2, ZW - 30)[1], 'stretch': 0.7, 'reach': 140}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (W - 1, _V_FONS - 2), (W - 1, _V_PROP + 2), (0, _V_PROP + 2)]}],
}
