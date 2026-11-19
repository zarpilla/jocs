"""
L'Última Arrel — la vora del bosc (Escena 1, la Iri), dissabte al capvespre. Art definitiu, a 1× (640×360; l'escena
fins a y = 260). El dibuix és a vora_comu.py (mode 'capvespre'), comú amb `bosc_obert`, `credits` i `portada`.

La càmera és arran de terra, una mica contrapicada: el roure és enorme i les falgueres del primer pla són gairebé
tan altes com la Iri. El sol es pon entre els troncs, a l'esquerra.
  - **Esquerra, el bosc viu:** el roure gegant amb la porta d'un metre (`porta_roure`), la `campaneta`, la
    `bustia` amb la nota, el fanalet vermell (`llum_vermell`, que parpelleja: ANIMS `llum`), l'`estaca` de topògraf
    (PROP: es treu) clavada davant del cantell de la porta, que s'obre cap enfora; els `bolets` turquesa apagats a
    l'arrel de l'esquerra; i el `cami` per on s'ha arribat (la sortida, a l'esquerra).
  - **Dreta, NaturaPlus (fred i pla):** la `tanca` (amb la porta i el cadenat de codi QR), el `cartell` lluminós,
    els rotllos de `gespa` artificial al peu de la tanca, l'`excavadora` a darrere, la caseta d'obra i els cons (de
    fons, sense id), i el `cargol` (PROP) entre el fang, al peu de la tanca.
  - Decorat `porta_oberta`: la porta oberta, amb la llum càlida de la centraleta a dins.
  - ANIMS: `llum` (el fanalet parpelleja) i `fulles` (fulles de tardor que cauen de la capçada).
  - FRONT: el primer pla (falgueres, una arrel i una pedra en silueta), que tapa sempre.
"""
import functools

import numpy as np
from PIL import Image

import hd640  # noqa: F401
from hd.rooms.comu import _diff
from hd640.rooms.vora_comu import (Mode, Llenc, llum, escena, mascara, fons_sala, fulles_frames, estaca, cargol,
                                   porta_oberta, sala, DY)

M = Mode('capvespre')
LIGHT = llum(M)


def _fons():
    return escena('capvespre')[0]


def bg(cv):
    fons_sala(_fons(), cv)


def _prop(fn):
    """Un prop: el que canvia en dibuixar-lo damunt del fons (amb la seva ombra i la seva llum), i res més."""
    def draw(pc):
        base = _fons()
        cv = Llenc(-DY, LIGHT, img=base.copy())
        fn(cv)
        d = _diff(cv.img, base)
        a = np.asarray(d).copy()
        a[sala(288):] = 0                                   # (sota l'escena, res)
        pc.img.alpha_composite(Image.fromarray(a, 'RGBA'))
        pc.P = pc.img.load()
    return draw


PROPS = {
    'estaca': _prop(estaca),
    'cargol': _prop(cargol),
    'porta_oberta': _prop(lambda cv: porta_oberta(cv, M)),
}


# ─── Animacions ────────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _llum_frames():
    base = _fons()
    off = _diff(escena('capvespre', -DY, False)[0], base)
    on = Image.new('RGBA', base.size, (0, 0, 0, 0))
    # un llum d'avís que s'espatlla: encès, i de tant en tant un parpelleig doble
    return [on, on, on, on, on, off, on, off, on, on, on, off]


def _fulles():
    return fulles_frames(-DY, n=24, seed=3, leaves=7, area=(40, 470, 30, 280))


ANIMS = {
    'llum': {'frames': lambda: list(_llum_frames()), 'frameDuration': 160},
    'fulles': {'frames': _fulles, 'frameDuration': 120},
}

FRONT = [{'id': 'davant', 'mask': lambda x, y: _MASK()(x, y), 'baseline': 999, 'zIndex': 20}]


@functools.lru_cache(maxsize=None)
def _MASK():
    return mascara(escena('capvespre')[2])


# ─── Geometria (en píxels de sala) ─────────────────────────────────────────

def _r(x0, y0, x1, y1):
    """Un rectangle en coordenades del món (les del dibuix) → de sala."""
    return (x0, sala(y0), x1, sala(y1))


def _p(x, y):
    return (x, sala(y))


# El terra on es camina: davant del roure i fins al peu de la tanca, sense els rotllos de gespa ni el primer pla.
WALK = [(0, 238), (104, 240), (140, 251), (300, 251), (340, 248), (380, 251), (498, 251), (502, 238), (540, 242),
        (590, 257), (596, 264), (560, 272), (540, 281), (0, 281)]

# L'escala: la Iri (el full fa 68 px a escala 1) fa ≈66 px davant la porta, i de ≈62 (al fons) a ≈75 (a prop) d'on
# camina. Si el full de la Iri canvia d'alçada, n'hi ha prou de canviar IRI_ALT.
IRI_ALT = 68
_Y0, _Y1 = sala(236), sala(282)


def _alt(y):
    return 66 + (y - sala(250)) * 0.28


GEOMETRIA = {
    'things': {
        'porta_roure': {'rect': _r(204, 182, 237, 241), 'walk': _p(226, 255)},
        'campaneta': {'rect': _r(184, 188, 201, 214), 'walk': _p(196, 256)},
        'bustia': {'rect': _r(265, 208, 288, 244), 'walk': _p(282, 256)},
        'llum_vermell': {'rect': _r(244, 186, 262, 207), 'walk': _p(256, 256)},
        'estaca': {'rect': _r(238, 219, 263, 252), 'walk': _p(252, 258)},
        'cargol': {'rect': _r(500, 224, 526, 242), 'walk': _p(506, 246)},
        'cartell': {'rect': _r(484, 63, 622, 142), 'walk': _p(520, 248)},
        'tanca': {'rect': _r(532, 146, 639, 276), 'walk': _p(552, 250)},
        'gespa': {'rect': _r(376, 214, 498, 249), 'walk': _p(430, 256)},
        'excavadora': {'rect': _r(430, 140, 530, 210), 'walk': _p(470, 252)},
        'bolets': {'rect': _r(118, 198, 176, 226), 'walk': _p(150, 256)},
        'cami': {'rect': _r(0, 236, 70, 281), 'walk': _p(4, 262)},
    },
    # l'àvia i la Iri arriben pel camí, de l'esquerra
    'spawns': {'iri': _p(124, 268), 'avia': _p(76, 262)},
    'walkable': [_p(x, y) for x, y in WALK],
    # el sol es pon a l'esquerra, arran de terra: les ombres, llargues, cap a la dreta
    'characterShadow': {'enabled': True, 'color': '#1c0e14', 'alpha': 0.42, 'squash': 0.28, 'core': 0.6,
                        'light': {'x': 1, 'y': 0.08, 'direction': True, 'stretch': 1.0}},
    'regions': [{'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
                 'scaleTop': round(_alt(_Y0) / IRI_ALT, 3), 'scaleBottom': round(_alt(_Y1) / IRI_ALT, 3),
                 'points': [(0, _Y0), (639, _Y0), (639, _Y1), (0, _Y1)]}],
}
