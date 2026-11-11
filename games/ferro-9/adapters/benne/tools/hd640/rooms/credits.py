"""
Els crèdits (cinemàtica del final), a 640×360 (vegeu hd/rooms/credits.py, la de 480×270): la portada sense el
títol ni els botons, perquè el joc acabi on va començar. La fàbrica i La Gavina, partides per l'esquerda de llum;
l'espai, la Terra i la fàbrica es mouen com a la portada.
"""
import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

from hd640.rooms import portada as po
from hd640.rooms.proleg_gavina import ambient_frames

LIGHT = po.LIGHT


def bg(cv, t=0.0):
    po.bg(cv, t=t, titol=False)


PROPS = {}

ANIMS = {'ambient': {'frames': lambda: ambient_frames(bg, LIGHT), 'frameDuration': 130}}
