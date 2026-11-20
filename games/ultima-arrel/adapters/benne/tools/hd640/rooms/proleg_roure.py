"""
L'Última Arrel — el pròleg (640×360). Cinemàtica a pantalla sencera, sense res clicable.

És el mateix pla que la portada (portada.py: el roure de la porta petita al capvespre, i a sota el tall del terra amb
la Xarxa Miceli), sense el títol: «Comença» esvaeix el títol i s'hi passa amb un tall net. L'Espora torna a casa: entra
per la dreta, s'atura a mirar el cartell del Bosc 2.0, va fins a la porta del roure i hi entra (la porta s'obre, amb la
llum càlida de la centraleta a dins, i es torna a tancar). Després, el rètol de temps i la vora del bosc.

  - PROPS `porta_oberta`: la porta oberta (porta_oberta de vora_comu, amb la llum càlida del capvespre). El guió
    (rooms/proleg_roure.json) l'amaga en començar i la mostra un moment quan l'Espora entra.
  - ANIMS `pols`: els polsos de llum pels fils de sota terra, com a la portada.
"""
import numpy as np
from PIL import Image

import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)
from hd.rooms.comu import _diff
from hd640.rooms.vora_comu import Mode, Llenc, porta_oberta
import hd640.rooms.portada as portada

LIGHT = portada.LIGHT
OY = portada.OY


def bg(cv):
    portada.bg(cv)


def _prop(fn):
    """Un prop: el que canvia en dibuixar-lo damunt del fons de la portada, i res més."""
    def draw(pc):
        base = portada._fons()
        cv = Llenc(OY, LIGHT, img=base.copy())
        fn(cv)
        d = _diff(cv.img, base)
        pc.img.alpha_composite(Image.fromarray(np.asarray(d).copy(), 'RGBA'))
        pc.P = pc.img.load()
    return draw


PROPS = {
    # la llum de dins, càlida com la de la centraleta del tall (la portada té el fanalet turquesa)
    'porta_oberta': _prop(lambda cv: porta_oberta(cv, Mode('capvespre'))),
}

ANIMS = {
    'pols': portada.ANIMS['pols'],
}

# L'Espora camina per l'herba de davant del roure (la porta: x 205..239, el graó a y ≈ 200 de pantalla). Entra de fora
# de la pantalla, per la dreta (el guió el posa a x = 654).
WALK = [(150, 196), (639, 196), (639, 213), (150, 213)]

GEOMETRIA = {
    'things': {},
    'spawns': {'espora': (600, 207)},
    'walkable': WALK,
    # el sol es pon a l'esquerra, entre els troncs: les ombres, llargues, cap a la dreta (com a la vora del bosc)
    'characterShadow': {'enabled': True, 'color': '#1c0e14', 'alpha': 0.42, 'squash': 0.28, 'core': 0.6,
                        'light': {'x': 1, 'y': 0.08, 'direction': True, 'stretch': 1.0}},
    'characterLights': {
        'ambient': '#9c8c98',
        'lights': [{'x': 40, 'y': 150, 'radius': 520, 'color': '#ffa868', 'intensity': 0.6},
                   {'x': 251, 'y': 158, 'radius': 60, 'color': '#5ee6e0', 'intensity': 0.35}],
    },
}
