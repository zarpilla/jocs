"""
La Conjura de l'Avet — `judici`, el judici (acte 4; la Vet, i l'Iri hi és). Art definitiu, a 1× (640×360; l'escena
fins a y = 260). EN 3D: l'art de `mur_avet` (avet_comu.py) amb un altre estat.

Matí de sol net després de la tempesta: cel blau, ombres llargues i dures cap a l'esquerra (el sol ve de la dreta,
darrere l'absis), tot moll i brillant. Les branques, apartades; el faristol al mig del carrer. El poble al voltant,
de fons i sense animar (només volen els coloms de l'absis: `coloms`), en dues colles: les dones de la Sança i la gent del poble a l'esquerra i al mig (`poble`),
i les monges a la dreta, davant l'absis (`monges`). Les `arrels`, l'`avet` i el `faristol`, com a `mur_avet`.
Els personatges: tot el repartiment, al carrer (vegeu `spawns`).
"""
import numpy as np

import hd640  # noqa: F401
from hd640.rooms import avet_comu as A
from hd640.rooms import mur_avet as MA
from hd640.rooms.avet_comu import Estat, CAM, HOR, CAMY, p
from hd640 import coloms

LIGHT = None

# La gent de fons: les dones (i algun home) a l'esquerra, davant el mur; més poble al mig; les monges a la dreta
POBLE = [
    (-520, 820, dict(roba=(150, 120, 90), cap='mocador', seed=21)), (-470, 860, dict(roba=(96, 74, 54), cap='mocador', seed=22)),
    (-430, 800, dict(roba=(120, 96, 66), cap='mocador', seed=23, mira=1)), (-560, 880, dict(roba=(88, 58, 46), cap='mocador', seed=24)),
    (-470, 780, dict(roba=(78, 54, 40), nen=True, seed=25)),
    (-40, 870, dict(roba=(70, 62, 58), cap='caputxa', seed=26)), (10, 900, dict(roba=(110, 100, 84), seed=27)),
    (60, 860, dict(roba=(132, 110, 80), cap='mocador', seed=28)), (110, 910, dict(roba=(64, 70, 60), seed=29)),
    (150, 870, dict(roba=(100, 84, 70), cap='caputxa', seed=30, mira=1)), (-90, 910, dict(roba=(96, 74, 54), cap='mocador', seed=31)),
]
MONGES = [(250 + k * 34, 830 + (k % 2) * 44, dict(monja=True, seed=40 + k, mira=-1)) for k in range(6)]


def _gent(v, e):
    A.gent(v, e, POBLE, 'poble')
    A.gent(v, e, MONGES, 'monges')


ESTAT = Estat(llum='sol', branques='apartades', faristol=True, branca_trencada=True, cera_agafada=True,
              extres=('abeurador', 'primer_pla', 'judici'))


def _r():
    return A.render(ESTAT, _gent)


def bg(cv):
    img, _ = _r()
    cv.img.paste(img)
    cv.P = cv.img.load()


PROPS = {}


def _coloms_frames():
    """Els coloms de l'absis, que volten el campanar (per darrere, el campanar els tapa), i un altre parell que
    passa per damunt de l'avet."""
    img, v = _r()

    def mask(noms):
        return lambda x, y: y < v.h and v.ids[v.own[y, x]] in noms
    vols = [(480, 24, 78, 12, 0.0, 1), (486, 34, 104, 16, 0.5, -1), (476, 16, 56, 8, 0.3, 1),
            (250, 26, 150, 10, 0.7, 1), (262, 34, 120, 8, 0.15, 1)]
    alt = {'cel', 'campanar', 'absis_teulada', 'absis', 'absis_mur', 'avet', 'muntanyes', 'cases'}
    return coloms.frames(img.width, img.height, vols, mask({'cel', 'muntanyes'}), mask(alt))


ANIMS = {'coloms': {'frames': _coloms_frames, 'frameDuration': 90}}


def _amo(sids):
    def mask(x, y):
        _, v = _r()
        return y < v.h and v.ids[v.own[y, x]] in sids
    return mask


FRONT = [
    {'id': 'davant_abeurador', 'mask': _amo({'abeurador'}), 'baseline': MA._base_abeurador(), 'zIndex': 20},
    {'id': 'davant', 'mask': _amo({'primer_pla'}), 'baseline': 999, 'zIndex': 20},
]


def _caixa_gent(llista, alt=86):
    pts = []
    for (x, z, o) in llista:
        pts += [np.array((x - 22, 0, z)), np.array((x + 22, alt * (0.62 if o.get('nen') else 1), z))]
    return MA._rect(pts, 1)


_T = MA.GEOMETRIA['things']
_P = p
GEOMETRIA = {
    'things': {
        'avet': _T['avet'],
        'arrels': _T['arrels'],
        'faristol': _T['faristol'],
        'poble': {'rect': _caixa_gent(POBLE[:5]), 'walk': (60, 222)},
        'monges': {'rect': _caixa_gent(MONGES), 'walk': (560, 210)},
    },
    # Tot el repartiment: el jutge al faristol i l'escrivà al costat; en Bonfill i en Ramon (lligat), a la dreta;
    # l'abadessa i la Gueraula, davant de les monges; la Sança, en Joanet i l'Ermessenda, a l'esquerra, amb el poble.
    'spawns': {
        'ponc': _P(0, 500), 'sunifred': _P(-76, 530),
        'bonfill': _P(150, 596), 'ramon': _P(196, 612),
        'ingilberga': _P(392, 636), 'gueraula': _P(352, 612),
        'sanca': _P(-262, 486), 'joanet': _P(-212, 452), 'ermessenda': _P(-150, 524),
        'iri': _P(84, 440), 'vet': _P(178, 432),
    },
    'walkable': MA.WALK,
    'forats': MA.GEOMETRIA['forats'],
    'floorSquash': 0.23,
    # el sol a la dreta i darrere l'absis: les ombres, llargues, cap a l'esquerra i una mica cap a la càmera
    'characterShadow': {'enabled': True, 'color': '#1c1418', 'alpha': 0.42, 'squash': 0.26, 'core': 0.6,
                        'light': {'x': -1, 'y': 0.3, 'direction': True, 'stretch': 1.0}},
    # la llum del matí net: gairebé neutra, i el sol càlid per la dreta
    'characterLights': {
        'ambient': '#e2e0dc',
        'lights': [{'x': 900, 'y': 0, 'radius': 1000, 'color': '#ffe6bc', 'intensity': 0.45}],
    },
    'regions': MA.GEOMETRIA['regions'],
}
