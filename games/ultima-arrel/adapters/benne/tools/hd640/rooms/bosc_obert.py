"""
L'Última Arrel — el bosc obert (Escena 7, la Vet; l'Iri hi és), una setmana després, de dia. Art definitiu, a 1×
(640×360; l'escena fins a y = 260). És la vora del bosc de l'escena 1 sense la tanca (vora_comu.py, mode 'dia').

  - El bosc és viu, i no ha de semblar la vora de l'escena 1 amb un altre llum: el sol del matí entra baix i daurat
    per la dreta, per la clariana on hi havia l'obra (raigs llargs i tot el quadre cap a l'or), la xarxa és encesa
    (els filaments i els `bolets` brillen de turquesa, i n'han sortit de nous), el prat ha florit (margarides, safrà
    de tardor, botons d'or) i on hi havia l'obra hi ha herba nova, les soques amb brots i tres plançons amb el tutor.
    De l'obra no en queda res més que els `forats`.
  - La `porta_oberta` del roure, amb llum turquesa (i el fanalet, ja turquesa); la `taula` feta d'una soca, amb les
    tasses de te de menta, la tetera i el pot de melmelada (capa del davant: l'Espora hi és darrere); els `forats`
    on hi havia els pals de la tanca; el bassal del Registrador, al davant a la dreta.
  - ANIMS: `espores` (punts turquesa que pugen a poc a poc) i `fulles` (fulles de tardor que cauen).
  - FRONT: la taula (amb la seva línia base) i el primer pla, que tapa sempre: les falgueres i, a dalt a la dreta,
    una branca de roure a contrallum que emmarca el quadre.
"""
import functools

import hd640  # noqa: F401
from hd640.rooms.vora_comu import (Mode, llum, escena, mascara, fons_sala, fulles_frames, espores_frames, sala, DY,
                                   TAULA, BASSAL, SUN_M, DOOR)
from hd640.rooms.vora_bosc import WALK as _WALK_VORA, _alt, IRI_ALT, _r, _p

M = Mode('dia')
LIGHT = llum(M)


def bg(cv):
    fons_sala(escena('dia')[0], cv)


PROPS = {}


def _espores():
    return espores_frames(-DY, n=24, seed=7, count=16, area=(20, 620, 150, 290), k=0.8)


def _fulles():
    return fulles_frames(-DY, n=24, seed=5, leaves=6, area=(40, 620, 30, 280))


ANIMS = {
    'espores': {'frames': _espores, 'frameDuration': 140},
    'fulles': {'frames': _fulles, 'frameDuration': 120},
}


@functools.lru_cache(maxsize=None)
def _masks():
    _, taula, front = escena('dia')
    return mascara(taula), mascara(front)


_TX, _TY, _TRX, _TRY, _TH = TAULA
DOOR_C = (DOOR[0], DOOR[2] - 8)           # la porta oberta, a l'alçada dels genolls (al món)
_TBASE = _TY + _TH + 1                    # on la soca toca a terra, al mig (al món)

FRONT = [
    {'id': 'davant_taula', 'mask': lambda x, y: _masks()[0](x, y), 'baseline': sala(_TBASE), 'zIndex': 20},
    {'id': 'davant', 'mask': lambda x, y: _masks()[1](x, y), 'baseline': 999, 'zIndex': 20},
]

# El terra on es camina (al món): el de l'escena 1, però ara arriba fins on hi havia la tanca, i més enllà, a la
# clariana; sense la taula (un forat: s'hi fa la volta).
WALK = [(0, 238), (104, 240), (140, 251), (300, 251), (340, 248), (364, 251), (500, 251), (504, 232), (560, 230),
        (620, 244), (630, 256), (600, 264), (560, 272), (540, 281), (0, 281)]


def _el(cx, cy, rx, ry, n=12):
    import math
    return [(round(cx + rx * math.cos(2 * math.pi * i / n)), round(sala(cy + ry * math.sin(2 * math.pi * i / n))))
            for i in range(n)]


_Y0, _Y1 = sala(228), sala(282)

GEOMETRIA = {
    'things': {
        'taula': {'rect': _r(316, 230, 386, 270), 'walk': _p(396, 272)},
        'porta_oberta': {'rect': _r(190, 182, 237, 241), 'walk': _p(226, 255)},
        'bolets': {'rect': _r(118, 198, 176, 226), 'walk': _p(150, 256)},
        'forats': {'rect': _r(484, 214, 632, 266), 'walk': _p(560, 262)},
    },
    'spawns': {
        'vet': _p(110, 268),
        'iri': _p(400, 268),                     # a la taula, a la dreta
        'avia': _p(304, 268),                    # a la taula, a l'esquerra
        'espora': _p(356, 254),                  # darrere la taula (la soca li tapa les cames)
        'urtica': _p(304, 68),                   # dreta damunt la branca de la dreta del roure
        'bufo': _p(BASSAL[0] - 4, BASSAL[1] + 2),  # al bassal
    },
    'walkable': [_p(x, y) for x, y in WALK],
    'forats': [_el(_TX, _TBASE, _TRX + 6, 7)],
    # el sol del matí és baix a la dreta: les ombres, llargues, cap a l'esquerra
    'characterShadow': {'enabled': True, 'color': '#2a1a08', 'alpha': 0.4, 'squash': 0.28, 'core': 0.6,
                        'light': {'x': -1, 'y': 0.12, 'direction': True, 'stretch': 0.9}},
    # La llum de la sala sobre els personatges: el matí daurat (l'ambient, càlid), el sol baix de la clariana, que
    # els toca pel costat dret, i la claror turquesa de la porta oberta del roure, una mica.
    'characterLights': {
        'ambient': '#c4b49a',
        'lights': [{'x': _p(*SUN_M)[0] + 60, 'y': _p(*SUN_M)[1], 'radius': 560, 'color': '#ffd27e', 'intensity': 0.6},
                   {'x': _p(*DOOR_C)[0], 'y': _p(*DOOR_C)[1], 'radius': 80, 'color': '#50e6d2', 'intensity': 0.35}],
    },
    'regions': [
        {'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
         'scaleTop': round(_alt(_Y0) / IRI_ALT, 3), 'scaleBottom': round(_alt(_Y1) / IRI_ALT, 3),
         'points': [(0, _Y0), (639, _Y0), (639, _Y1), (0, _Y1)]},
        # la branca de l'Urtica: lluny i amunt, una fada fa ≈20 px
        {'id': 'branca', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': False,
         'scaleTop': 0.55, 'scaleBottom': 0.55,
         'points': [(270, sala(40)), (340, sala(40)), (340, sala(90)), (270, sala(90))]},
    ],
}
