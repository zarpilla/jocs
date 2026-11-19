"""
Els crèdits (cinemàtica del final), a 640×360: la portada en 3D sense el títol ni els botons, perquè el joc acabi on
va començar. La fàbrica des de l'altra riba del canal i La Gavina des de sota, partides per l'esquerda de llum; el
fum, el canal, les estrelles, la Terra i les llums de l'estació es mouen com a la portada (vegeu portada.py; el
dibuix pla d'abans és a credits_pla_comu.py).
"""
import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

from hd640.rooms import portada as po
from hd640.rooms.proleg_gavina_pla_comu import ambient_frames

LIGHT = po.LIGHT


def bg(cv, t=0.0):
    po.bg(cv, t=t, titol=False)


PROPS = {}

ANIMS = {'ambient': {'frames': lambda: ambient_frames(bg, LIGHT), 'frameDuration': 130}}
