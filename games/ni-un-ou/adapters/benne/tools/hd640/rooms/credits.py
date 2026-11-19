"""
Ni un ou — els crèdits (640×360, pantalla sencera, sense barra de verbs). EN 3D, a 1×: el mar, el cel i l'Arenga
de la portada (portada.py), amb una altra càmera.

Mar de nit en calma, vist des d'una mica amunt (la càmera a 14 m, l'horitzó baix: el cel del mig queda net per al
text). L'Arenga, petita i en 3/4 des de popa, just a la dreta del mig, se'n va cap al fons, cap al camí de la lluna,
amb els llums encesos; la seva estela, llarga, ve des de baix a l'esquerra i porta l'ull fins a la popa (és el que
fa la profunditat: ampla i desfeta a prop, prima al costat de la nau). El mar i la nau es mouen i es gronxen
(ANIMS `mar`).
"""
import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

import functools

from hd.rooms.comu import _diff
from hd640.rooms.portada import Pla, fons, LIGHT, N

PLA = Pla(hor=237, f=420.0, h=14.0, ship=(16.0, 160.0), psi=0.42, moon=(517, 150), plat=None,
          buoy=(19.0, 42.0))
COSES = ('nau',)


@functools.lru_cache(maxsize=None)
def _fons(i=0):
    return fons(PLA, i, COSES, seed=41, clouds=0.42, calm=0.7, estela=160.0, path=(2.0, 0.34))


def bg(cv, frame=0):
    cv.img.paste(_fons(frame))
    cv.P = cv.img.load()


PROPS = {}


def _frames():
    base = _fons(0)
    return [_diff(_fons(i), base) for i in range(N)]


ANIMS = {'mar': {'frames': _frames, 'frameDuration': 360}}

GEOMETRIA = {'things': {}, 'spawns': {}}
