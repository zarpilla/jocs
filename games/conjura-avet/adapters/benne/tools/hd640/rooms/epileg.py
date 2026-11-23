"""
La Conjura de l'Avet — `epileg`, l'epíleg (l'Iri; la Vet hi és). Art definitiu, a 1× (640×360; l'escena fins a
y = 260). EN 3D: l'art de `mur_avet` (avet_comu.py) a la primavera.

Matí tebi, cel blau, verd tendre: el `mur` arreglat (les pedres noves, més clares, on l'avet l'havia esbotzat), un
arbre florit a l'hort, on hi havia l'avet; el tronc tallat en `rodanxes` apilades; les `arrels` velles encara al
seu lloc, amb molsa, i el forat vell ple d'herba; al costat, el `forat_nou` per al plançó, i la `carretilla` (una civera) amb
el plançó. El faristol d'en Ponç, al mig. El primer pla: herba i flors.
Decorats: `forat_gran` (el forat eixamplat, amb la terra treta), `planco_plantat` (el plançó al forat, amb la
cinta), `segell_planco` (el segell vermell del jutge a la cinta), `rotul_clavat` (la post amb «AVET») i `planco_agafat` (la civera buida). PROPS:
`rotul` (el cos clicable del rètol: buit, el dibuixa `rotul_clavat`).
"""
import numpy as np

import hd640  # noqa: F401
from hd640.rooms import avet_comu as A
from hd640.rooms import mur_avet as MA
from hd640.rooms.avet_comu import Estat, p, diff

LIGHT = None

_EXT = ('abeurador', 'herbes', 'florit', 'rodanxes', 'carretilla', 'forat_nou')
BASE = Estat(llum='primavera', arbre='cap', forat='vell', mur='arreglat', branques='cap', faristol=True, extres=_EXT)


def _e(*mes, treu=()):
    return Estat(llum='primavera', arbre='cap', forat='vell', mur='arreglat', branques='cap', faristol=True,
                 extres=tuple(x for x in _EXT if x not in treu) + mes)


GRAN = _e('forat_gran', treu=('forat_nou',))
PLANTAT = _e('forat_gran', 'planco', treu=('forat_nou',))


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


def _buit(pc):
    pass


PROPS = {
    'forat_gran': _prop(GRAN, BASE),
    'planco_plantat': _prop(PLANTAT, GRAN),
    'segell_planco': _prop(_e('forat_gran', 'planco', 'segell_planco', treu=('forat_nou',)), PLANTAT),
    'rotul_clavat': _prop(_e('forat_gran', 'planco', 'rotul', treu=('forat_nou',)), PLANTAT),
    'rotul': _buit,
    # la civera buida (l'Iri ja ha agafat el plançó, o l'ha plantat)
    'planco_agafat': _prop(_e('carretilla_buida'), BASE),
}


def _amo(sids):
    def mask(x, y):
        _, v = _r(BASE)
        return y < v.h and v.ids[v.own[y, x]] in sids
    return mask


FRONT = [
    {'id': 'davant_abeurador', 'mask': _amo({'abeurador'}), 'baseline': MA._base_abeurador(), 'zIndex': 20},
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20},
]


def _rect(pts, marge=0):
    return MA._rect([np.array(q, dtype=float) for q in pts], marge)


_C, _ROT = A.CARRETILLA
_R = A.RODANXES
_F = A.FORAT_NOU
_T = MA.GEOMETRIA['things']

GEOMETRIA = {
    'things': {
        'absis': _T['absis'],
        'arrels': _T['arrels'],
        'rodanxes': {'rect': _rect([_R + (-100, 0, 0), _R + (100, 150, 0)], 2), 'walk': p(60, 628)},
        'carretilla': {'rect': _rect([_C + (-64, 0, -20), _C + (64, 90, 20)], 1), 'walk': p(-10, 580)},
        'forat_nou': {'rect': _rect([_F + (-40, 0, -24), _F + (40, 8, 24)], 3), 'walk': p(-120, 600)},
        'rotul': {'rect': _rect([A.ROTUL + (-20, 0, 0), A.ROTUL + (20, 44, 0)], 1), 'walk': p(-90, 590)},
    },
    # en Ponç al faristol, en Sunifred amb la galleda, el pare, l'abadessa, la Gueraula, la Sança; l'Iri i la Vet
    'spawns': {
        'iri': p(60, 470), 'vet': p(-210, 478),
        'ponc': p(0, 500), 'sunifred': p(-80, 540), 'ramon': p(150, 560),
        'ingilberga': p(330, 612), 'gueraula': p(372, 640), 'sanca': p(-300, 520),
    },
    'walkable': MA.WALK,
    'forats': MA.GEOMETRIA['forats'],
    'floorSquash': 0.23,
    # el sol tebi del matí, a la dreta: ombres cap a l'esquerra, més suaus que al judici
    'characterShadow': {'enabled': True, 'color': '#1a1a14', 'alpha': 0.36, 'squash': 0.26, 'core': 0.65,
                        'light': {'x': -1, 'y': 0.3, 'direction': True, 'stretch': 0.7}},
    'characterLights': {
        'ambient': '#e6e8dc',
        'lights': [{'x': 900, 'y': 0, 'radius': 1000, 'color': '#fff0cc', 'intensity': 0.35}],
    },
    'regions': MA.GEOMETRIA['regions'],
}
