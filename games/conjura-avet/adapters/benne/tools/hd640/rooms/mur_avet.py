"""
La Conjura de l'Avet — `mur_avet`, l'avet caigut (actes 1 i 4; les dues). La sala de mostra. Art definitiu, a 1×
(640×360; l'escena fins a y = 260). EN 3D: el dibuix és a avet_comu.py.

Matí de plugim, cel blanc i pla, llum difusa: la pedra fosca de mullada i els bassals del carrer que reflecteixen el
cel, l'absis i l'avet. Càmera de lluny, arran de carrer, en 3/4:
  - a l'esquerra, les `arrels` aixecades (una paret de terra més alta que l'Iri, amb el tall de serra) i a sota el
    `forat`; les `branques` escampades davant, que tapen el pas; el portell del `cami_riu`, al fons a l'esquerra;
  - l'`avet` travessa la sala en diagonal, de dalt a l'esquerra cap al mig, damunt el `mur` esbotzat de l'hort,
    amb la capçada fins a tocar l'absis;
  - a la dreta, l'`absis` en 3/4, amb la `porta_monestir` al mur del monestir; el `carrer` de la plaça, a l'esquerra;
  - el `faristol` del jutge (amb l'`ordre`) al mig del carrer, i l'abeurador de pedra a la dreta (s'hi passa per
    darrere i per davant).
Decorats: `branques_apartades`, `cera_agafada`, `llum_mati` (l'acte 4: el matí de sol net, a pantalla completa: hi
porta el faristol, la branca trencada i les branques apartades) i `poble_aplegant` (la gent que s'aplega, amb sol).
PROPS: `branca_trencada`, `cera`, `faristol`, `ordre`. ANIMS: `pluja` (el plugim i les ones als bassals; queda
sota `llum_mati`). FRONT: la branca del primer pla (tapa sempre) i l'abeurador (amb la línia base), amb la
variant `llum_mati`.
"""
import functools

import numpy as np

import hd640  # noqa: F401
from hd640.rooms import avet_comu as A
from hd640.rooms.avet_comu import Estat, CAM, HOR, CAMY, p, diff

LIGHT = None

BASE = Estat(llum='pluja', extres=('abeurador', 'primer_pla'))
APARTADES = Estat(llum='pluja', branques='apartades', extres=BASE.extres)
MATI = Estat(llum='sol', branques='apartades', faristol=True, branca_trencada=True, cera_agafada=True,
             extres=BASE.extres)


def _r(e):
    return A.render(e)


def bg(cv):
    img, _ = _r(BASE)
    cv.img.paste(img)
    cv.P = cv.img.load()


def _prop(e1, e0):
    def draw(pc):
        pc.img.alpha_composite(diff(_r(e1)[0], _r(e0)[0]))
        pc.P = pc.img.load()
    return draw


def _ple(e):
    def draw(pc):
        pc.img.alpha_composite(_r(e)[0])
        pc.P = pc.img.load()
    return draw


def _poble(v, e):
    A.gent(v, e, POBLE_APLEGANT, 'poble')


# La gent que s'aplega el matí del judici (acte 4): al fons del carrer, davant del mur i de l'absis
POBLE_APLEGANT = [
    (-60, 820, dict(roba=(96, 74, 54), cap='mocador', seed=1)), (-10, 840, dict(roba=(120, 96, 66), seed=2)),
    (40, 800, dict(roba=(70, 62, 58), cap='caputxa', seed=3)), (95, 860, dict(roba=(88, 58, 46), cap='mocador', seed=4)),
    (150, 820, dict(roba=(110, 100, 84), seed=5, mira=-1)), (200, 880, dict(roba=(64, 70, 60), cap='caputxa', seed=6)),
    (-120, 860, dict(roba=(132, 110, 80), cap='mocador', seed=7)), (60, 900, dict(roba=(78, 54, 40), nen=True, seed=8)),
    (250, 830, dict(roba=(100, 84, 70), cap='mocador', seed=9, mira=-1)), (-150, 790, dict(roba=(58, 52, 50), seed=10)),
]
POBLE_E = Estat(llum='sol', branques='apartades', faristol=True, branca_trencada=True, cera_agafada=True,
                extres=BASE.extres + ('poble',))


def _poble_render():
    return A.render(POBLE_E, _poble)[0]


def poble_aplegant(pc):
    pc.img.alpha_composite(diff(_poble_render(), _r(MATI)[0]))
    pc.P = pc.img.load()


PROPS = {
    'branques_apartades': _prop(APARTADES, BASE),
    'cera_agafada': _prop(Estat(llum='pluja', branques='apartades', cera_agafada=True, extres=BASE.extres), APARTADES),
    'llum_mati': _ple(MATI),
    'poble_aplegant': poble_aplegant,
    'branca_trencada': _prop(Estat(llum='pluja', branques='apartades', branca_trencada=True, extres=BASE.extres), APARTADES),
    'cera': _prop(Estat(llum='pluja', branques='apartades', cera=True, extres=BASE.extres), APARTADES),
    'faristol': _prop(Estat(llum='pluja', faristol=True, extres=BASE.extres), BASE),
    'ordre': _prop(Estat(llum='pluja', faristol=True, ordre=True, extres=BASE.extres),
                   Estat(llum='pluja', faristol=True, extres=BASE.extres)),
}


# ─── Animacions ────────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _pluja():
    _, v = _r(BASE)
    return A.pluja_frames(n=8, dens=420, alpha=110, ones=A.ones_bassals(v, n=36))


ANIMS = {'pluja': {'frames': lambda: list(_pluja()), 'frameDuration': 90}}


# ─── Capes del davant ──────────────────────────────────────────────────────

def _amo(sids):
    def mask(x, y):
        _, v = _r(BASE)
        return y < v.h and v.ids[v.own[y, x]] in sids
    return mask


def _base_abeurador():
    """La línia base de l'abeurador: el cantó de davant que queda més al fons."""
    c, hx, hz, hy, rot = A.ABEURADOR
    ux, uz = np.array((np.cos(rot), 0, np.sin(rot))), np.array((-np.sin(rot), 0, np.cos(rot)))
    cants = [c - uz * hz + ux * hx, c - uz * hz - ux * hx]
    return max(p(P[0], P[2])[1] for P in cants)


FRONT = [
    {'id': 'davant_abeurador', 'mask': _amo({'abeurador'}), 'baseline': _base_abeurador(), 'zIndex': 20,
     'variants': ('llum_mati',)},
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20, 'variants': ('llum_mati',)},
]


# ─── Geometria (en píxels de sala) ─────────────────────────────────────────
# (només projeccions: el mòdul l'importen totes les eines, i no ha de dibuixar res en importar-se)

def _p(x, z, y=0.0):
    return p(x, z, y)


def _rect(pts, marge=0, retall=(0, 0, 639, 259)):
    """El rectangle que ocupen uns punts del món (x, y, z) a la pantalla."""
    uv = [CAM.projecta(tuple(P))[:2] for P in pts]
    x0, y0 = min(u for u, _ in uv) - marge, min(v for _, v in uv) - marge
    x1, y1 = max(u for u, _ in uv) + marge, max(v for _, v in uv) + marge
    return (max(retall[0], round(x0)), max(retall[1], round(y0)), min(retall[2], round(x1)), min(retall[3], round(y1)))


def _cercle(c, e1, e2, r1, r2, n=24):
    return [c + e1 * r1 * np.cos(2 * np.pi * k / n) + e2 * r2 * np.sin(2 * np.pi * k / n) for k in range(n)]


_UP = np.array((0, 1.0, 0))
_EX = A._n(np.cross(_UP, A.ARREL_N))
_FORAT = _cercle(A.FORAT_C, A.FORAT_U, A._n(np.cross(A.FORAT_U, _UP)), A.FORAT_R[0] * 1.2, A.FORAT_R[1] * 1.2)
_ARRELS = _cercle(A.ARREL_C, _EX, _UP, A.ARREL_R * 1.05, A.ARREL_R * 1.05)
_BT0, _BT1 = A.BRANCA_TRENCADA
_C_ABS = np.array((A.ABS_C[0], 0, A.ABS_C[1]))
_ABSIS = _cercle(_C_ABS, A.TW, A.NW, A.ABS_R, A.ABS_R) + [_C_ABS + _UP * 400]
_ABSIS = [P for P in _ABSIS if (P - _C_ABS) @ A.NW >= -1]
_ARBRE = [A.ARREL_C * np.array((1, 0, 1)) + A.TRONC_D * s + _UP * float(A.tronc_y(s) + A._capcada_r(s) * 0.9)
          for s in range(150, 900, 50)]
_PORTA = A.ARREL_C  # (només per a l'editor)
_P_PORTA = _C_ABS + A.TW * A.PORTA_T + A.NW * 2

# El terra on es camina (al món: x, z): el carrer, de z ≈ 405 (escala 1,09) a z ≈ 630 (0,70); a l'esquerra, fins a
# la vora del forat i de les branques; a la dreta, fins al mur del monestir.
WALK_MON = [(-700, 470), (-560, 470), (-470, 515), (-420, 548), (-220, 562), (-140, 598), (-60, 630), (200, 640),
            (420, 640), (520, 610), (520, 400), (-700, 400)]
WALK = [(max(0, min(639, u)), min(257, v)) for u, v in (p(x, z) for x, z in WALK_MON)]


def _forat_abeurador():
    c, hx, hz, hy, rot = A.ABEURADOR
    ux, uz = np.array((np.cos(rot), 0, np.sin(rot))), np.array((-np.sin(rot), 0, np.cos(rot)))
    m = 8
    return [p(*(c + ux * sx * (hx + m) + uz * sz * (hz + m))[[0, 2]]) for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


def _caixa_abeurador():
    """Els vuit cantons de l'abeurador (al món), per al rectangle del punt."""
    c, hx, hz, hy, rot = A.ABEURADOR
    ux, uz = np.array((np.cos(rot), 0, np.sin(rot))), np.array((-np.sin(rot), 0, np.cos(rot)))
    return [c + ux * sx * hx + uz * sz * hz + _UP * y for sx in (-1, 1) for sz in (-1, 1) for y in (0, 2 * hy)]


# L'escala: un personatge fa (v − 128) / 115 de la mida del seu full a la fila v (exacte: la càmera no mira avall;
# l'Iri, 84 px a escala 1, fa ≈60 px al fons del carrer i ≈90 a baix de tot).
_Y0, _Y1 = 196, 260
_CERA_UV = CAM.projecta(tuple(A.CERA_P))[:2]
_FAR = A.FARISTOL

GEOMETRIA = {
    'things': {
        'absis': {'rect': _rect(_ABSIS, 2), 'walk': _p(250, 628)},
        'mur': {'rect': (0, 132, 34, 178), 'walk': (14, 224)},
        'abeurador': {'rect': _rect(_caixa_abeurador(), 2), 'walk': _p(160, 520)},
        'avet': {'rect': (_rect(_ARRELS)[2] + 2, 0, _rect(_ABSIS)[0] - 4, 176), 'walk': _p(-40, 612)},
        'branques': {'rect': (24, 176, 232, 214), 'walk': (110, 223)},
        'branca_trencada': {'rect': _rect([_BT0, _BT1], 10), 'walk': _p(-90, 596)},
        'arrels': {'rect': _rect(_ARRELS)[:3] + (190,), 'walk': (124, 222)},
        # (el forat arriba a la vora esquerra, però allà la vora és el carrer: comença on s'acaba el carrer)
        'forat': {'rect': (max(23, _rect(_FORAT)[0]),) + _rect(_FORAT)[1:], 'walk': (92, 223)},
        'cera': {'rect': (round(_CERA_UV[0]) - 7, round(_CERA_UV[1]) - 5, round(_CERA_UV[0]) + 7, round(_CERA_UV[1]) + 4),
                 'walk': (100, 223)},
        'faristol': {'rect': _rect([_FAR + (-26, 0, 0), _FAR + (26, 80, 0)]), 'walk': _p(100, 485)},
        'ordre': {'rect': _rect([_FAR + (-18, 52, 0), _FAR + (18, 76, 0)]), 'walk': _p(100, 485)},
        'carrer': {'rect': (0, 190, 22, 259), 'walk': (2, 242)},
        'cami_riu': {'rect': (35, 128, 84, 184), 'walk': (46, 222)},
        'porta_monestir': {'rect': _rect([_P_PORTA - A.TW * 40, _P_PORTA + A.TW * 40 + _UP * 130]),
                           'walk': _p(410, 640)},
    },
    'spawns': {
        'iri': _p(130, 455), 'vet': _p(-300, 455),
        'ponc': _p(0, 500), 'sunifred': _p(-76, 530), 'ramon': _p(-130, 575), 'bonfill': _p(330, 616),
    },
    'walkable': WALK,
    'forats': [_forat_abeurador()],
    # La llum difusa del cel tapat: l'ombra de contacte, rodona i suau (la càmera aixafa el terra: 115 a ≈500)
    'floorSquash': 0.23,
    'characterShadow': {'enabled': True, 'color': '#1a1a20', 'alpha': 0.34, 'squash': 0.26, 'core': 0.7},
    # La llum de la sala sobre els personatges: el cel blanc, fred i una mica fosc (pluja); amb el decorat
    # `llum_mati`, el sol del matí a la dreta, darrere l'absis (càlid).
    'characterLights': {
        'ambient': '#b4b8c0',
        'lights': [{'x': 300, 'y': -200, 'radius': 700, 'color': '#e6eaf0', 'intensity': 0.25,
                    'whenPropHidden': 'llum_mati'},
                   {'x': 900, 'y': 0, 'radius': 900, 'color': '#ffe8c0', 'intensity': 0.55,
                    'whenPropVisible': 'llum_mati'}],
    },
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round((_Y0 - HOR) / CAMY, 3), 'scaleBottom': round((_Y1 - HOR) / CAMY, 3),
                 'points': [(0, _Y0), (639, _Y0), (639, _Y1), (0, _Y1)]}],
}
