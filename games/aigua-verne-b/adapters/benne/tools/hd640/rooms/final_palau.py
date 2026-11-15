"""
La cinemàtica final del palau: la galeria de les piscines (palau_galeria.py) amb totes les piscines plenes i el
reflex de l'aigua. Sense res per clicar.
"""
import hd640  # noqa: F401

from hd640.rooms import palau_galeria as G

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
