"""
Els crèdits (cinemàtica del final): la portada sense el títol ni els botons, perquè el joc acabi on va començar.
La fàbrica i La Gavina, partides per l'esquerda de llum; l'espai, la Terra i la fàbrica es mouen com a la portada.
"""
from hd.rooms import portada as po
from hd.rooms.proleg_gavina import ambient_frames

LIGHT = po.LIGHT


def bg(cv, t=0.0):
    po.bg(cv, t=t, titol=False)


PROPS = {}

ANIMS = {'ambient': {'frames': lambda: ambient_frames(bg, LIGHT), 'frameDuration': 130}}
