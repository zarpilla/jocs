"""
La cinemàtica final del palau: la galeria de les piscines (palau_galeria.py) amb totes les piscines plenes i el
reflex de l'aigua. Sense res per clicar.
"""
import hd640  # noqa: F401

from hd640.rooms import palau_galeria as G

# Art a 2× (1280×720 per a una sala de 640×360): el mateix dibuix, amb les formes, el dither i la llum a la
# resolució real (hd1280/canvas2x.py); el motor el mostra a 1/2 (artScale al .room.json).
ART_SCALE = 2
from hd1280.canvas2x import Canvas2x as Canvas  # noqa: E402,F811
from hd.pix import Canvas as Canvas1x  # noqa: E402,F401  (llenços auxiliars en píxels de sala: figures, textos)

LIGHT = G.LIGHT


def bg(cv):
    G.bg(cv)
    G.piscines_plenes(cv)


PROPS = {}
ANIMS = dict(G.ANIMS)
GEOMETRIA = {
    'things': {},
    'spawns': {'iri': (300, 236), 'verne': (190, 214), 'dividend': (444, 214), 'holm': (250, 232)},
    'walkable': G.GEOMETRIA['walkable'],
}
