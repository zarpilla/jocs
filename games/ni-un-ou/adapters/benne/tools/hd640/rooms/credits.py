"""
Prova a 640×360: els crèdits (vegeu hd/rooms/credits.py, la de 480×270). Pantalla sencera, sense barra de verbs.
Mar de nit en calma, la lluna i, petita a l'horitzó, l'Arenga amb els llums encesos. El cel del mig queda net per
al text. Les espurnes de la lluna al mar es mouen (ANIMS).
"""
import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

from hd.pix import Light, Canvas, H
from hd.rooms.comu import _diff
from hd.rooms.exterior import arenga, reflection
from hd640.rooms.portada import night_sky, night_sea, K

HOR = 237
MOON = (517, 160)
SHIP = (104, HOR + 3, 1.6 * K)

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)


def sea(cv, frame=0):
    night_sea(cv, HOR, H - 1, moon_x=MOON[0], seed=42, phase=frame * 0.7, calm=0.6)
    reflection(cv, SHIP[0] - 8, SHIP[0] + 96, SHIP[1], 16, k=0.4, seed=43 + frame)


def ship(cv):
    arenga(cv, SHIP[0], SHIP[1], SHIP[2], 'night', facing=1, zodiac=False)


def bg(cv, frame=0):
    night_sky(cv, 0, HOR, moon=MOON, seed=41, clouds=0.42)
    ship(cv)
    sea(cv, frame)
    ship(cv)            # el que sobresurt per sota de l'horitzó (el buc) es torna a dibuixar damunt del mar


PROPS = {}


def _frames():
    base = Canvas(light=LIGHT)
    bg(base)
    frames = []
    for i in range(4):
        cv = Canvas(light=LIGHT, img=base.img.copy())
        sea(cv, i)
        ship(cv)
        frames.append(_diff(cv.img, base.img))
    return frames


ANIMS = {'mar': {'frames': _frames, 'frameDuration': 360}}

GEOMETRIA = {'things': {}, 'spawns': {}}
