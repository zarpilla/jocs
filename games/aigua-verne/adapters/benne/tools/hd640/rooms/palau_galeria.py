"""
Aigua Verne — `palau_galeria` (L: persones de ≈83 px): la galeria de les vint-i-tres piscines, al palau orbital del
Magnat. EN 3D (hd640/tres_d.py), a 1×.

Una càmera alta, a la dreta de la galeria, que mira de biaix cap a la cantonada de l'esquerra: la paret de la porta del
saló fuig cap al fons, i la del finestral travessa el quadre en diagonal. Al fons, el finestral a l'espai entre
columnes (Terra-2, i un dels dipòsits orbitals de Verne); davant, les tres terrasses de marbre que pugen cap al
finestral, amb les piscines buides (5 + 7 + 10) enfonsades a la terrassa, vistes des de dalt; a l'esquerra, l'escala de
marbre que hi puja, arran de la paret i amb la barana cromada; al terra de la galeria, la **piscina central** (la 23a),
fonda, amb les escales cromades a la vora del fons; a la dreta, l'**aquari** dels trenta-tres peixos, exempt i girat,
damunt el peu del rètol «LOT 12», i una gandula. Dos llums d'aranya pengen del sostre. Primer pla: un pilar en ombra
tallat per la vora de la dreta (una capa amb parallax: la sala fa 960 px i la càmera la recorre) i un cordó de vellut entre dos pals daurats, a baix a l'esquerra. Es passa per darrere de la gandula
(a la vora de la piscina central), de les escales cromades de la piscina i de l'aquari (entre l'aquari i la primera
terrassa hi ha un pas).

El detall ve del dibuix pla (palau_galeria_pla_comu.py): el finestral, la porta, el vidre de l'aquari i el seu peu, les
columnes i els llums. PROPS: `piscines_plenes` (aigua a totes, quan s'obre la reserva). ANIMS: `peixos`, `estrelles`, i
`aigua` (els reflexos de l'aigua de l'aquari, que juguen pel terra). La cinemàtica final (final_palau.py) fa servir
aquesta mateixa escena amb les piscines plenes.

El món: x a la dreta (0 = la paret de la porta), y amunt (0 = el terra de la galeria), z cap al fons (560 = la paret
del finestral); 1 unitat = 1 píxel de sala a la distància on un personatge fa ≈83 px (escala 1).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from hd.pix import Canvas, Light, W, hr
from hd.rooms.comu import _diff
from hd640.rooms import palau_galeria_pla_comu as PL
from hd640.rooms.palau_comu import MARB, ORP, TURQ, CROM, GRANAT, BLAU, RH
from hd640.tres_d import Camera, Escena, Llum, llum_personatges

PERSONA = 83
BOTTOM = RH - 1                                    # la sala acaba aquí (a sota, la barra de verbs)
XR, ZW, YC = 900, 560, 270                         # la paret de la dreta (no es veu), la del finestral, el sostre
ZN = -300                                          # el terra i les parets comencen aquí (darrere la càmera)
ZT = (300, 387, 474)                               # el davant de cada terrassa
TH = (28, 56, 84)                                  # l'alçada de cada terrassa
XT = 100                                           # les terrasses comencen aquí (a l'esquerra, l'escala)
NPOOL = (5, 7, 10)                                 # piscines a cada terrassa (+ la central: 23)
POOL_D = 20                                        # la fondària de les piscines de les terrasses
CEN = (262, 438, 150, 214, 56)                     # la piscina central: x0, x1, z0, z1, fondària
ESC = (0, XT, 196, 7, 12, 29)                      # l'escala: x0, x1, z del primer graó, graons, alçada, petja
AQ = (550, 232, -0.30)                             # l'aquari: centre (x, z) i gir (separat de la terrassa: s'hi
#                                                    passa per darrere)
ARANYES = ((420, 204, 140), (660, 214, 400))       # els llums d'aranya (x, y, z)
ESCALETES = (CEN[0] + 40, CEN[1] - 56)             # les dues escales cromades de la piscina central (x)
COLUMNA = (646, 96)                                # la columna del primer pla (x, z)
GANDULA = (490, 158, -0.38)                        # la gandula, a la vora de la piscina central (x, z, gir)
PALS = ((176, 6), (326, 22))                      # els pals del cordó de vellut (x, z), en primer pla

ROOM_W = 960                                       # més ampla que la pantalla: la càmera la recorre
PARALLAX = 1.25                                    # la columna del primer pla es mou un 25% més de pressa
CAM = Camera(pos=(520, 230, -250), yaw=-0.30, pitch=0.16, f=420, centre=(ROOM_W // 2, 76))

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)   # (la llum és la del món: la de l'Escena)
LLUMS = [Llum((x, y - 10, z), 420, 1.5, power=1.3) for x, y, z in ARANYES] + [
    Llum((AQ[0], 90, AQ[1]), 150, 1.4, power=1.6),                # la claror blava de l'aquari
    Llum((380, 160, ZW - 10), 420, 0.6, power=1.0),               # la claror del finestral
    Llum((40, 120, 140), 160, 0.9, power=1.5),                    # els llums de paret de la porta
]
AMBIENT = -0.6


# ─── Les piscines ───────────────────────────────────────────────────────────

def piscines_terrassa(k):
    """Les piscines de la terrassa k: [(x0, x1, z0, z1)]."""
    n = NPOOL[k]
    gap = (36, 24, 16)[k]
    x0, x1 = XT + 26, XR - 20
    w = (x1 - x0 - gap * (n - 1)) / n
    z0, z1 = ZT[k] + 14, (ZT[k + 1] if k < 2 else ZW) - 16
    return [(x0 + i * (w + gap), x0 + i * (w + gap) + w, z0, z1) for i in range(n)]


def totes_piscines():
    """[(sid, x0, x1, z0, z1, y de la vora, fondària)]: les 22 de les terrasses i la central."""
    out = [(f'piscina{k}_{i}', *p, TH[k], POOL_D) for k in range(3) for i, p in enumerate(piscines_terrassa(k))]
    return out + [('piscina_central', CEN[0], CEN[1], CEN[2], CEN[3], 0.0, CEN[4])]


def _rajola(tile):
    """La rajola turquesa de dins les piscines, en coordenades del món (s'empetiteix sola cap al fons)."""
    def L(s, t, P):
        a, b = s % tile, t % tile
        val = 4.0 + (hr(int(s // tile), int(t // tile), 5) - 0.5) * 0.5
        if a < 0.9 or b < 0.9:
            val += 1.4
        return val
    return L


def piscines(e, sid, pools, yv, D, plena, tex_aigua=None):
    """Un grup de piscines enfonsades a la mateixa alçada i fondària (les d'una terrassa, o la central): el fons, les
    parets de dins (rajola) i, si són plenes, l'aigua (textura). Una sola superfície per a tot el grup on es pot (el
    fons, la paret del fons, l'aigua): l'Escena en recorda 255 com a màxim."""
    yb = yv - D
    tile = 6 if D < 30 else 9
    xa, xb = min(p[0] for p in pools), max(p[1] for p in pools)
    z0, z1 = pools[0][2], pools[0][3]

    def dins(s, t=None):
        x = xa + s
        return any(a <= x <= b for a, b, _, _ in pools)

    def mig(s):
        x = xa + s
        return any(abs(x - (a + b) / 2) < max(0.8, (b - a) * 0.012) for a, b, _, _ in pools)
    e.quad(sid, (xa, yb, z1), (xb, yb, z1), (xb, yb, z0), (xa, yb, z0), ramp=TURQ, forma=dins,
           lvl=lambda s, t, P: _rajola(tile)(s, t, P) + 0.4 * (t / max(1, z1 - z0)) - (2.6 if mig(s) else 0))
    if sid == 'piscina_central':                                   # la gota de Verne, de mosaic, al fons
        cx, cz = (xa + xb) / 2, (z0 + z1) / 2

        def gota(s, t):
            dx, dz = s - 18, t - 22
            if dz < 0:
                return math.hypot(dx, dz) < 12
            return abs(dx) < 12 * max(0.0, 1 - dz / 26) ** 0.9
        e.quad(sid, (cx - 18, yb + 0.3, cz + 22), (cx + 18, yb + 0.3, cz + 22), (cx + 18, yb + 0.3, cz - 22),
               (cx - 18, yb + 0.3, cz - 22), ramp=BLAU, lvl=lambda s, t, P: 2.6 - (s - 18) * 0.06, forma=gota)
    # les parets de dins: la del fons (de cara a la càmera) i, de cada piscina, el costat que es veu
    e.quad(sid, (xa, yv, z1), (xb, yv, z1), (xb, yb, z1), (xa, yb, z1), ramp=TURQ, forma=dins,
           lvl=lambda s, t, P: _rajola(tile)(s, t, P) - 1.0 - (t / D) * 0.6)
    cx_ = CAM.pos[0]
    for x0, x1, _, _ in pools:
        if x0 < cx_:
            e.quad(sid, (x0, yv, z1), (x0, yv, z0), (x0, yb, z0), (x0, yb, z1), ramp=TURQ,
                   lvl=lambda s, t, P: _rajola(tile)(s, t, P) + 0.2, dues_cares=True)
        if x1 > cx_:
            e.quad(sid, (x1, yv, z0), (x1, yv, z1), (x1, yb, z1), (x1, yb, z0), ramp=TURQ,
                   lvl=lambda s, t, P: _rajola(tile)(s, t, P) - 1.4, dues_cares=True)
    if plena:
        yw = yv - 3
        e.quad(f'aigua_{sid}', (xa, yw, z1), (xb, yw, z1), (xb, yw, z0), (xa, yw, z0), forma=dins,
               tex=(tex_aigua, (xa, PL.ZMAP - z1, xb, PL.ZMAP - z0), 1))


def _forats(pools, marge=3.0):
    """forma(s, t) d'un terra que comença a (x0, z1) del món i va cap a +x i −z: fals dins les piscines (i la vora)."""
    def f(x0, z1):
        def forma(s, t):
            x, z = x0 + s, z1 - t
            return not any(a <= x <= b and c <= z <= d for a, b, c, d in pools)
        return forma
    return f


def _vora(pools, w=4.0):
    """Nivells que se sumen al terra (o a la terrassa) a tocar de les piscines: el coronament de pedra blanca."""
    def f(x, z):
        for a, b, c, d in pools:
            if a - w <= x <= b + w and c - w <= z <= d + w:
                return 1.8 if z > d else 0.6 if z < c else 1.2
        return 0.0
    return f


# ─── Superfícies procedurals ────────────────────────────────────────────────

_VT = PL.venes(XR + 2, ZW - ZN + 2, 21)               # les venes del marbre, al món: [z − ZN, x]
_NT = PL.soroll(XR + 2, ZW - ZN + 2, 40, 22)


def _vena(x, z):
    return float(_VT[min(ZW - ZN + 1, max(0, int(z - ZN))), min(XR + 1, max(0, int(x)))])


def _es_or(x, z, tile, or_cada=2):
    iu, iv = math.floor(x / tile), math.floor(z / tile)
    ax, az = x - iu * tile, z - iv * tile
    return (iu % or_cada == 0 and ax < 1.3) or (iv % or_cada == 0 and az < 1.3)


def _marbre(base, tile=48, seed=5):
    """Lloses de marbre blanc amb venes i filets d'or, en coordenades del món (x, z): s'empetiteixen cap al fons.
    → el nivell (els filets d'or es pinten a part, amb `_es_or`)."""
    def L(x, z):
        iu, iv = math.floor(x / tile), math.floor(z / tile)
        ax, az = x - iu * tile, z - iv * tile
        if ax < 1.3 or az < 1.3:
            return base - 1.4
        zi = min(ZW - ZN + 1, max(0, int(z - ZN)))
        xi = min(XR + 1, max(0, int(x)))
        return (base + (hr(iu, iv, seed) - 0.5) * 0.6 - float(_VT[zi, (xi + seed * 131) % (XR + 2)]) * 1.8
                + (float(_NT[zi, xi]) - 0.5) * 0.5)
    return L


_TILE_TERRA = 56
_MARBRE_TERRA = _marbre(6.4, tile=_TILE_TERRA)


def _terra_lvl(s, t, P):
    return _MARBRE_TERRA(P[0], P[2])


def _or_terra(s, t, P):
    return 4.6


def _sostre(s, t, P):
    x, z = P[0], P[2]
    a, b = x % 90, z % 90
    v = 4.6
    if a < 3 or b < 3:
        v = 3.4 if (a < 1.2 or b < 1.2) else 5.6
    elif 14 < a < 76 and 14 < b < 76:
        v = 5.4
    return v


# ─── L'escena ───────────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _tex():
    fons = Canvas(PL.FONS_W, PL.FONS_H, light=PL.LLUM_PLA)
    bright = PL.paret_fons(fons)
    esq = Canvas(PL.ESQ_W, PL.ESQ_H, light=PL.LLUM_PLA)
    PL.paret_esq(esq)
    return {'fons': fons.img, 'bright': bright, 'esq': esq.img, 'peu': PL.aquari_peu(),
            'aq': PL.aquari_vidre(0.0), 'aq_costat': PL.aquari_vidre(0.0, costat=True)}


def _rects_aigua():
    return [(x0, z0, x1, z1) for _, x0, x1, z0, z1, _, _ in totes_piscines()]


@functools.lru_cache(maxsize=None)
def aigua_tex(frame=0):
    return PL.aigua_mapa(_rects_aigua(), frame, focus=[(x, z) for x, _, z in ARANYES])


def escena(cv, plena=False, columna=False):
    """Tota la galeria, de lluny a prop. → l'Escena (qui ha pintat què)."""
    T = _tex()
    e = Escena(cv, CAM, LLUMS, ambient=AMBIENT)
    aigua = aigua_tex(0) if plena else None
    # el sostre, de cassetons
    e.quad('sostre', (0, YC, ZN), (XR, YC, ZN), (XR, YC, ZW), (0, YC, ZW), ramp=MARB, lvl=_sostre, dues_cares=True)
    # la paret del finestral i la de la porta (els dibuixos plans)
    e.quad('paret_fons', (0, YC, ZW), (XR, YC, ZW), (XR, TH[2], ZW), (0, TH[2], ZW),
           tex=(T['fons'], (0, 0, PL.FONS_W, PL.FONS_H), 1))
    e.quad('paret_esq', (0, YC, ZN), (0, YC, ZW), (0, 0, ZW), (0, 0, ZN),
           tex=(T['esq'], (0, 0, PL.ESQ_W, PL.ESQ_H), 1))
    e.quad('paret_dreta', (XR, YC, ZW), (XR, YC, ZN), (XR, 0, ZN), (XR, 0, ZW), ramp=MARB, lvl=4.6)
    # la piscina central (de dins) i el terra de la galeria, amb el forat
    cx0, cx1, cz0, cz1, cd = CEN
    piscines(e, 'piscina_central', [(cx0, cx1, cz0, cz1)], 0.0, cd, plena, aigua)
    vora_c = _vora([(cx0, cx1, cz0, cz1)], 6)
    forats = _forats([(cx0, cx1, cz0, cz1)])
    e.quad('terra', (0, 0, ZW), (XR, 0, ZW), (XR, 0, ZN), (0, 0, ZN), ramp=MARB,
           lvl=lambda s, t, P: _terra_lvl(s, t, P) + vora_c(P[0], P[2]), forma=forats(0, ZW))
    # els filets d'or del terra (a sobre, només on toca)
    e.quad('terra', (0, 0.1, ZW), (XR, 0.1, ZW), (XR, 0.1, ZN), (0, 0.1, ZN), ramp=ORP, lvl=_or_terra,
           forma=lambda s, t: _es_or(s, ZW - t, _TILE_TERRA) and forats(0, ZW)(s, t) and not vora_c(s, ZW - t))
    # el reflex del finestral i dels llums al marbre polit
    e.claror((XT, 0.4, ZT[0]), (XR, 0.4, ZT[0]), (XR, 0.4, 40), (XT, 0.4, 40), (236, 240, 255),
             lambda s, t: 0.16 * max(0.0, 1 - t / 160) * (0.6 + 0.4 * math.sin(s * 0.02)))
    # la foscor dels racons: on la paret de l'esquerra toca el terra
    e.foscor('racons', (0.5, 0.5, ZW), (160, 0.5, ZW), (160, 0.5, ZN), (0.5, 0.5, ZN),
             lambda s, t: 0.55 * max(0.0, 1 - s / 70) ** 1.4)
    # les terrasses, de lluny a prop: les piscines (de dins), i la terrassa amb els forats
    for k in (2, 1, 0):
        pools = piscines_terrassa(k)
        piscines(e, f'piscines{k}', pools, TH[k], POOL_D, plena, aigua)
        vora = _vora(pools)
        zb = ZT[k + 1] if k < 2 else ZW
        f = _forats(pools)(XT, zb)
        top = _marbre(6.8, tile=(34, 40, 46)[k], seed=7 + k)
        e.caixa(f'terrassa{k}', XT, XR, 0, TH[k], ZT[k], zb, MARB, 5.0, cares={
            'dalt': {'ramp': MARB, 'lvl': lambda s, t, P, top=top, vora=vora: top(P[0], P[2]) + vora(P[0], P[2]),
                     'forma': f},
            'davant': {'ramp': MARB, 'lvl': lambda s, t, P, k=k: 5.0 - (t / TH[k]) * 1.4
                       - _vena(P[0] * 1.3, ZN + 40 + k * 60 + t * 3) * 1.4
                       + (1.6 if t < 2 else -1.0 if t > TH[k] - 3 else 0)},
            'esquerra': {'ramp': MARB, 'lvl': 4.0}})
        e.quad(f'terrassa{k}', (XT, TH[k] - 3, ZT[k] - 0.4), (XR, TH[k] - 3, ZT[k] - 0.4),
               (XR, TH[k] - 5, ZT[k] - 0.4), (XT, TH[k] - 5, ZT[k] - 0.4), ramp=ORP, lvl=4.4)  # el filet d'or
        # l'ombra que fa la terrassa de dalt sobre la de sota (i la paret del fons a la de dalt)
        e.foscor(f'ombra_t{k}', (XT, TH[k] + 0.5, zb), (XR, TH[k] + 0.5, zb), (XR, TH[k] + 0.5, zb - 20),
                 (XT, TH[k] + 0.5, zb - 20), lambda s, t: 0.4 * max(0.0, 1 - t / 20))
    # al peu de la primera terrassa, una franja d'ombra al terra
    e.foscor('ombra_terrassa', (XT, 0.6, ZT[0]), (XR, 0.6, ZT[0]), (XR, 0.6, ZT[0] - 26), (XT, 0.6, ZT[0] - 26),
             lambda s, t: 0.35 * max(0.0, 1 - t / 26))
    # l'escala de marbre, arran de la paret: cada graó, de lluny a prop, i la barana cromada
    ex0, ex1, ez, n, eh, ep = ESC
    for i in range(n - 1, -1, -1):
        z0 = ez + i * ep
        z1 = z0 + ep if i < n - 1 else ZW
        e.caixa('escales', ex0, ex1, 0, eh * (i + 1), z0, z1, MARB, 5.6, cares={
            'davant': {'ramp': MARB, 'lvl': lambda s, t, P: 5.2 - t * 0.08 + (1.4 if t < 1.5 else 0)},
            'dalt': {'ramp': MARB, 'lvl': lambda s, t, P: 7.0 - (0.8 if t < 2 else 0)
                     - _vena(P[0] * 3 + 300, P[2]) * 1.4},
            'dreta': {'ramp': MARB, 'lvl': lambda s, t, P: 4.2 - (1.2 if t > eh * (i + 1) - 2 else 0)}})
    e.foscor('ombra_escala', (ex1, 0.6, ZT[0]), (ex1 + 30, 0.6, ZT[0]), (ex1 + 30, 0.6, ez), (ex1, 0.6, ez),
             lambda s, t: 0.4 * max(0.0, 1 - s / 30))
    top = [(ex1 - 4, eh * (i + 1) + 34, ez + i * ep + 4) for i in range(n)]
    e.cable('escales', [(ex1 - 4, 34, ez - 6)] + top, CROM, 3.0, gruix=2.6)
    for x, y, z in top[::2] + [(ex1 - 4, 34, ez - 6)]:
        e.cable('escales', [(x, y, z), (x, y - 34, z)], CROM, 2.4, gruix=1.6)
    # les escales cromades de la piscina central, a la vora del fons
    for lx in ESCALETES:
        for dx in (0, 14):
            x = lx + dx
            e.cable('escaleta', [(x, 0.5, cz1 + 10), (x, 22, cz1 + 7), (x, 27, cz1 + 1), (x, 18, cz1 - 3),
                                 (x, -cd + 6, cz1 - 5)], CROM, 3.2, gruix=2.6)
        for yy in (-8, -22, -36):
            e.cable('escaleta', [(lx, yy, cz1 - 4), (lx + 14, yy, cz1 - 4)], CROM, 2.6, gruix=1.8)
    # l'aquari: el peu, el vidre (davant i costat), el capçal d'or; l'ombra a terra
    ax, az, ang = AQ
    e.foscor('ombra_aquari', (ax - 90, 0.6, az + 60), (ax + 90, 0.6, az + 60), (ax + 90, 0.6, az - 70),
             (ax - 90, 0.6, az - 70),
             lambda s, t: 0.6 * max(0.0, 1 - ((s - 90) / 84) ** 2 - ((t - 70) / 52) ** 2) * 1.4)
    w, d = PL.AQ_W, PL.AQ_D
    e.caixa_girada('aquari', ax, az, w + 8, d + 8, PL.AQ_PEU, ang, MARB, 5.0, cares={
        'davant': {'tex': (T['peu'], (0, 0, w + 8, PL.AQ_PEU), 1)},
        'dreta': {'ramp': MARB, 'lvl': lambda s, t, P: 4.4 - t * 0.03},
        'dalt': {'ramp': ORP, 'lvl': 4.8}})
    e.caixa_girada('aquari', ax, az, w, d, PL.AQ_H, ang, CROM, 4.0, y0=PL.AQ_PEU,
                   cares={'dalt': {'ramp': BLAU, 'lvl': 4.6}})
    c, s_ = math.cos(ang), math.sin(ang)

    def G(lx, y, lz):
        return (ax + lx * c - lz * s_, y, az + lx * s_ + lz * c)
    y0, y1, a2, b2 = PL.AQ_PEU, PL.AQ_PEU + PL.AQ_H, w / 2, d / 2
    e.quad('aquari_vidre', G(-a2, y1, -b2), G(a2, y1, -b2), G(a2, y0, -b2), G(-a2, y0, -b2),
           tex=(T['aq'], (0, 0, w, PL.AQ_H), 1))
    e.quad('aquari_costat', G(a2, y1, -b2), G(a2, y1, b2), G(a2, y0, b2), G(a2, y0, -b2),
           tex=(T['aq_costat'], (0, 0, d, PL.AQ_H), 1))
    e.caixa_girada('aquari', ax, az, w + 10, d + 10, 12, ang, ORP, 4.2, y0=PL.AQ_PEU + PL.AQ_H, cares={
        'davant': {'ramp': ORP, 'lvl': lambda s, t, P: 5.4 - t * 0.2 + (1.2 if t < 1.5 else 0)},
        'dreta': {'ramp': ORP, 'lvl': lambda s, t, P: 3.6 - t * 0.15},
        'dalt': {'ramp': ORP, 'lvl': 5.6}})
    # els llums d'aranya, penjats del sostre
    img, peu = PL.aranya_img()
    for x, y, z in ARANYES:
        e.cable('aranya', [(x, YC, z), (x, y, z)], ORP, 4.0, gruix=1.4)
        e.sprite('aranya', img, peu, (x, y, z))
    # la gandula, a la vora de la piscina central: el bastidor d'or, el matalàs blanc i el respatller aixecat
    gx, gz, ga = GANDULA
    e.foscor('ombra_gandula', (gx - 50, 0.6, gz + 30), (gx + 50, 0.6, gz + 30), (gx + 50, 0.6, gz - 34),
             (gx - 50, 0.6, gz - 34),
             lambda s, t: 0.55 * max(0.0, 1 - ((s - 50) / 46) ** 2 - ((t - 30) / 26) ** 2) * 1.5)
    c, s_ = math.cos(ga), math.sin(ga)

    def Gg(lx, y, lz):
        return (gx + lx * c - lz * s_, y, gz + lx * s_ + lz * c)
    for lx, lz in ((-36, -11), (36, -11), (-36, 11), (36, 11)):
        p_ = Gg(lx, 0, lz)
        e.caixa_girada('gandula', p_[0], p_[2], 3, 3, 14, ga, ORP, 3.0)
    e.caixa_girada('gandula', gx, gz, 80, 26, 4, ga, ORP, 4.4, y0=14, cares={'dalt': {'ramp': ORP, 'lvl': 5.6}})
    # el respatller, aixecat (a l'esquerra), i el matalàs blanc amb ratlles granat
    e.quad('gandula', Gg(-40, 48, 12), Gg(-40, 48, -12), Gg(-20, 18, -12), Gg(-20, 18, 12), ramp=ORP, lvl=3.2,
           dues_cares=True)
    e.quad('gandula', Gg(-37, 49, -12), Gg(-37, 49, 12), Gg(-17, 19, 12), Gg(-17, 19, -12), ramp=MARB,
           lvl=lambda s, t, P: 7.0 - t * 0.03 - (2.0 if int(s) % 6 < 2 else 0), dues_cares=True)
    mx, _, mz = Gg(10, 0, 0)
    e.caixa_girada('gandula', mx, mz, 56, 24, 5, ga, MARB, 7.0, y0=18, cares={
        'dalt': {'ramp': MARB, 'lvl': lambda s, t, P: 7.4 - (2.2 if int(t) % 6 < 2 else 0)},
        'davant': {'ramp': MARB, 'lvl': 5.4}, 'dreta': {'ramp': MARB, 'lvl': 4.6}})
    e.caixa_girada('gandula', *Gg(22, 0, 2)[::2], 14, 18, 3, ga + 0.3, GRANAT, 4.6, y0=23)  # la tovallola plegada
    # primer pla: la columna en ombra (a la dreta, tallada per la vora) i el cordó de vellut entre dos pals daurats
    # (la columna és una capa a part, amb parallax: el fons de la sala no la porta; vegeu _capa_columna)
    cx_, cz_ = COLUMNA

    def estries(base):
        return lambda s, t, P: base + (0.9 if s % 9 < 2 else -0.5 if s % 9 > 7 else 0) - (0.6 if t > YC - 30 else 0)
    if columna:
        e.caixa('columna', cx_ - 22, cx_ + 22, 0, YC, cz_ - 22, cz_ + 22, MARB, 1.6, cares={
            'esquerra': {'ramp': MARB, 'lvl': estries(2.4)}, 'davant': {'ramp': MARB, 'lvl': estries(1.2)}})
        for y0, h in ((0, 16), (YC - 60, 8)):                    # el sòcol i un anell d'or
            e.caixa('columna', cx_ - 24, cx_ + 24, y0, y0 + h, cz_ - 24, cz_ + 24, ORP, 1.8,
                    cares={'esquerra': {'ramp': ORP, 'lvl': 2.8}, 'davant': {'ramp': ORP, 'lvl': 1.6}})
    # la foscor del primer pla: el terra de prop i el racó de la dreta, en ombra
    e.foscor('ombra_prop', (0, 0.7, 90), (XR, 0.7, 90), (XR, 0.7, -60), (0, 0.7, -60),
             lambda s, t: 0.6 * min(1.0, t / 110) ** 1.2)
    e.foscor('ombra_dreta', (560, 0.7, 300), (XR, 0.7, 300), (XR, 0.7, -60), (560, 0.7, -60),
             lambda s, t: 0.45 * min(1.0, s / 200) ** 1.5)
    for px_, pz in PALS:
        e.tub('primer_pla', (px_, 0, pz), (px_, 46, pz), 2.6, ORP, 2.4)
        e.tub('primer_pla', (px_, 47, pz), (px_, 51, pz), 4.4, ORP, 3.4)
    (a, az0), (b, bz0) = PALS
    e.cable('primer_pla', [(a, 44, az0)] + [(a + (b - a) * k / 8, 44 - 14 * math.sin(math.pi * k / 8),
                                             az0 + (bz0 - az0) * k / 8) for k in range(1, 8)] + [(b, 44, bz0)],
            GRANAT, 2.2, gruix=4.4)
    return e


# ─── Composició ─────────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _base(plena=False, columna=False):
    cv = Canvas(ROOM_W, light=LIGHT)
    e = escena(cv, plena, columna)
    cv.rect(0, BOTTOM + 1, ROOM_W - 1, cv.h - 1, [(0, 0, 0)], 0, lit=0)    # la barra de verbs: negre
    return cv.img, e


def _capa_columna():
    """La columna del primer pla, retallada de la sala sencera (la capa del davant que fa parallax)."""
    from PIL import Image
    full, e = _base(columna=True)
    out = Image.new('RGBA', full.size, (0, 0, 0, 0))
    src, dst, ids, amo, w = full.load(), out.load(), e.ids, e.amo, e.cv.w
    for y in range(BOTTOM + 1):
        for x in range(full.width):
            if ids[amo[y * w + x]] == 'columna':
                dst[x, y] = src[x, y]
    return out


def bg(cv):
    img, _ = _base()
    cv.img.paste(img)
    cv.P = cv.img.load()


def piscines_plenes(cv):
    """Aigua a totes les piscines (quan s'obre la reserva, i a la cinemàtica final)."""
    cv.img.alpha_composite(_diff(_base(True)[0], _base()[0]))


PROPS = {'piscines_plenes': piscines_plenes}


def _capa_idx(e, flat, idx):
    from PIL import Image
    out = Image.new('RGBA', (e.cv.w, e.cv.h), (0, 0, 0, 0))
    dst, src, W_ = out.load(), flat.load(), e.cv.w
    Xs, Ys, TXs, TYs, ks = e.mapes[idx]
    for X, Y, TX, TY, k in zip(Xs, Ys, TXs, TYs, ks):
        if e.amo[Y * W_ + X] != idx or TX >= flat.width or TY >= flat.height:
            continue
        c = src[TX, TY]
        if c[3]:
            dst[X, Y] = (min(255, int(c[0] * k)), min(255, int(c[1] * k)), min(255, int(c[2] * k)), c[3])
    return out


def frames_peixos(e, n=24):
    """Els peixos que neden, projectats pel vidre del davant i pel del costat de l'aquari."""
    idx = {e.ids[i]: i for i in e.mapes if e.ids[i] in ('aquari_vidre', 'aquari_costat')}
    out = []
    for i in range(n):
        t = i / n
        img = _capa_idx(e, PL.aquari_vidre(t), idx['aquari_vidre'])
        img.alpha_composite(_capa_idx(e, PL.aquari_vidre(t, costat=True), idx['aquari_costat']))
        out.append(img)
    return out


def frames_estrelles(e, n=10, seed=3):
    """Les estrelles brillants del finestral que parpellegen, projectades per la paret del fons."""
    T = _tex()
    base = T['fons']
    out = []
    for i in range(n):
        cv = Canvas(PL.FONS_W, PL.FONS_H, img=base.copy())
        for k, (x, y) in enumerate(T['bright']):
            ph = (hr(k, seed) * n + i) % n
            if ph < 1:
                for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                    cv.flat(x + dx, y + dy, (40, 40, 70) if (dx or dy) else (130, 136, 170))
            elif ph < 2:
                for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)):
                    cv.flat(x + dx, y + dy, (80, 86, 130))
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    cv.flat(x + dx, y + dy, (190, 196, 230))
        out.append(e.capa(_diff(cv.img, base), {'paret_fons'}))
    return out


def frames_reflexos(img, e, n=8):
    """Els reflexos de l'aigua de l'aquari que juguen pel terra, al seu voltant (només on es veu el terra)."""
    import numpy as np
    from PIL import Image
    ax, az, _ = AQ
    terra = [i for i, s in enumerate(e.ids) if s == 'terra']
    mask = np.isin(np.frombuffer(e.amo, np.uint16).reshape(e.cv.h, e.cv.w), terra)[..., None]
    base = np.asarray(img)
    out = []
    for i in range(n):
        ph = i / n * 2 * math.pi
        cv = Canvas(light=None, img=img.copy())

        def fn(s, t, ph=ph):
            x, z = ax - 130 + s, az + 110 - t
            d = math.hypot((x - ax) / 130, (z - az) / 110)
            if d >= 1:
                return 0.0
            w = math.sin(x * 0.16 + math.sin(z * 0.11 + ph) * 2.2) * math.sin(z * 0.19 - ph + math.sin(x * 0.07) * 1.6)
            return (0.34 if w > 0.55 else 0.12 if w > 0.3 else 0.0) * (1 - d) ** 0.7
        Escena(cv, CAM).claror((ax - 130, 0.4, az + 110), (ax + 130, 0.4, az + 110), (ax + 130, 0.4, az - 110),
                               (ax - 130, 0.4, az - 110), (150, 220, 255), fn)
        nou = np.where(mask, np.asarray(cv.img), base).astype(np.uint8)
        out.append(_diff(Image.fromarray(nou, 'RGBA'), img))
    return out


def _frames_peixos_anim():
    _, e = _base()
    return frames_peixos(e)


def _frames_estrelles_anim():
    _, e = _base()
    return frames_estrelles(e)


def _frames_aigua_anim():
    img, e = _base()
    return frames_reflexos(img, e)


ANIMS = {'peixos': {'frames': _frames_peixos_anim, 'frameDuration': 140},
         'estrelles': {'frames': _frames_estrelles_anim, 'frameDuration': 300},
         'aigua': {'frames': _frames_aigua_anim, 'frameDuration': 160}}


# ─── Capes del davant ───────────────────────────────────────────────────────

def _amo(ids):
    def mask(x, y):
        _, e = _base()
        return e.ids[e.amo[y * e.cv.w + x]] in ids
    return mask


def _v(x, z, y=0.0):
    return CAM.projecta((x, y, z))[1]


def _caixa_girada_terra(cx, cz, w, d, ang, marge):
    c, s = math.cos(ang), math.sin(ang)
    a, b = w / 2 + marge, d / 2 + marge
    return [(cx + lx * c - lz * s, cz + lx * s + lz * c) for lx, lz in ((-a, -b), (a, -b), (a, b), (-a, b))]


_AQ_CANTO = _caixa_girada_terra(AQ[0], AQ[1], PL.AQ_W + 8, PL.AQ_D + 8, AQ[2], 0)[0]   # (x, z) davant-esquerra


FRONT = [
    # les escales cromades de la piscina central: qui és darrere la piscina hi passa per darrere
    {'id': 'davant_escaleta', 'mask': _amo({'escaleta'}), 'baseline': round(_v(350, CEN[3] + 6)), 'zIndex': 20},
    # l'aquari (el peu, el vidre i el capçal): la línia base, la del cantó de davant que queda més al fons (el de
    # l'esquerra); els peixos hi neden per sobre (si no, la capa els tapa)
    {'id': 'davant_aquari', 'mask': _amo({'aquari', 'aquari_vidre', 'aquari_costat'}),
     'baseline': round(_v(*_AQ_CANTO)), 'zIndex': 20, 'props': ('peixos',)},
    # la gandula
    {'id': 'davant_gandula', 'mask': _amo({'gandula'}), 'baseline': round(_v(GANDULA[0], GANDULA[1])), 'zIndex': 20},
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20},
    # la columna, a la dreta: es mou més de pressa que la sala (alineada a mig recorregut)
    {'id': 'davant_columna', 'mask': _amo({'columna'}), 'image': _capa_columna, 'baseline': 999, 'zIndex': 21,
     'parallaxDepth': PARALLAX, 'x': round((PARALLAX - 1) * (ROOM_W - W) / 2 / PARALLAX)},
]


# ─── Geometria (coordenades de sala, projectades) ────────────────────────────

def _p(x, z, y=0.0):
    u, v, _ = CAM.projecta((x, y, z))
    return round(u), round(v)


def _rect_mon(*Ps):
    pts = [CAM.projecta(P) for P in Ps]
    return (max(0, round(min(p[0] for p in pts))), max(0, round(min(p[1] for p in pts))),
            min(ROOM_W - 1, round(max(p[0] for p in pts))), min(BOTTOM, round(max(p[1] for p in pts))))


# El terra on es camina (al món): la galeria, davant les terrasses, fins a la paret de la porta i el peu de l'escala;
# a prop, fins on el personatge no passa de ≈1,2. Forats: la piscina central i l'aquari (s'hi pot fer la volta).
WALK_MON = [(14, 44), (14, ESC[2] - 8), (ESC[1] + 8, ESC[2] - 8), (ESC[1] + 8, ZT[0] - 6), (XR - 10, ZT[0] - 6),
            (XR - 10, 44)]
_WALK = PL.retalla([CAM.projecta((x, 0, z))[:2] for x, z in WALK_MON], x1=ROOM_W - 3)
_V_FONS, _V_PROP = min(v for _, v in _WALK), max(v for _, v in _WALK)


def _escala_a(v):
    """L'escala d'un personatge amb els peus a la y de pantalla `v` (al terra, la profunditat només depèn de v)."""
    lo, hi = -200.0, 3000.0
    for _ in range(60):
        z = (lo + hi) / 2
        if CAM.projecta((360, 0, z))[1] > v:
            lo = z
        else:
            hi = z
    return CAM.escala((360, 0, (lo + hi) / 2))


_CEN_FORAT = [_p(x, z) for x, z in ((CEN[0] - 8, CEN[2] - 8), (CEN[1] + 8, CEN[2] - 8), (CEN[1] + 8, CEN[3] + 8),
                                     (CEN[0] - 8, CEN[3] + 8))]
_AQ_FORAT = [_p(x, z) for x, z in _caixa_girada_terra(AQ[0], AQ[1], PL.AQ_W + 8, PL.AQ_D + 8, AQ[2], 6)]
_GAN_FORAT = [_p(x, z) for x, z in _caixa_girada_terra(GANDULA[0], GANDULA[1], 78, 26, GANDULA[2], 6)]
_PZ = PL.PORTA[0] + PL.ESQ_Z0, PL.PORTA[1] + PL.ESQ_Z0     # la porta, en z del món
_AQ_PUNTS = [(x, y, z) for x, z in _caixa_girada_terra(AQ[0], AQ[1], PL.AQ_W + 10, PL.AQ_D + 10, AQ[2], 0)
             for y in (0, PL.AQ_PEU + PL.AQ_H + 12)]

GEOMETRIA = {
    'things': {
        'porta_salo': {'rect': _rect_mon((0, PL.PORTA[2] + 26, _PZ[0] - 10), (0, 0, _PZ[1] + 10)),
                       'walk': _p(34, (_PZ[0] + _PZ[1]) / 2)},
        'finestral': {'rect': _rect_mon((PL.FONS_COLS[0], YC - PL.WIN_Y0 + 4, ZW),
                                        (PL.FONS_COLS[-1], YC - PL.WIN_Y1, ZW)),
                      'walk': _p(300, ZT[0] - 30)},
        'piscines': {'rect': _rect_mon((XT, TH[2], ZW), (XR, 0, ZT[0]), (XT, 0, ZT[0])),
                     'walk': _p(420, ZT[0] - 24)},
        # les escales cromades de la piscina central (l'escala de marbre de l'esquerra no és clicable)
        'escales': {'rect': _rect_mon(*[(x, y, CEN[3] + dz) for x in (ESCALETES[0] - 6, ESCALETES[1] + 20)
                                        for y in (30, -20) for dz in (-6, 12)]),
                    'walk': _p((CEN[0] + CEN[1]) / 2, CEN[2] - 16)},
        'aquari': {'rect': _rect_mon(*_AQ_PUNTS), 'walk': _p(AQ[0] - 90, AQ[1] + 18)},
    },
    'spawns': {'iri': _p(60, (_PZ[0] + _PZ[1]) / 2 - 10), 'verne': _p(200, 150),
               'dividend': _p(628, 212)},          # (entre l'aquari i la columna)
    'walkable': _WALK,
    'forats': [_CEN_FORAT, _AQ_FORAT, _GAN_FORAT],
    'floorSquash': 0.45,                           # (la càmera, a 2,3 m i picada: el terra es veu aixafat)
    # (el marbre blanc i els reflexos de l'aigua: l'ombra, ben fosca, i un contorn als personatges)
    'characterOutline': {'color': '#1c1626', 'alpha': 0.75},
    'characterShadow': {'enabled': True, 'color': '#1e1826', 'alpha': 0.58, 'squash': 0.45, 'core': 0.7,
                        'light': {'x': _p(ARANYES[0][0], ARANYES[0][2])[0], 'y': _p(ARANYES[0][0], ARANYES[0][2])[1],
                                  'stretch': 0.6, 'reach': 140}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_escala_a(_V_FONS - 2), 3), 'scaleBottom': round(_escala_a(_V_PROP + 2), 3),
                 'points': [(0, _V_FONS - 2), (ROOM_W - 1, _V_FONS - 2), (ROOM_W - 1, _V_PROP + 2),
                            (0, _V_PROP + 2)]}],
    # La llum de la sala sobre els personatges (characterLights del motor): la galeria de marbre, molt clara: les
    # aranyes, l'aquari i els llums de la porta.
    'characterLights': {
        'ambient': '#e4e2ea',
        'lights': [
            *[llum_personatges(CAM, l.pos, l.r, '#fff0d4', 0.18) for l in LLUMS[:len(ARANYES)]],  # les aranyes
            llum_personatges(CAM, LLUMS[len(ARANYES)].pos, LLUMS[len(ARANYES)].r, '#78d0ff', 0.35),  # l'aquari
            llum_personatges(CAM, LLUMS[len(ARANYES) + 2].pos, LLUMS[len(ARANYES) + 2].r, '#ffe0b0', 0.2),  # els llums de la porta
        ],
    },
}
