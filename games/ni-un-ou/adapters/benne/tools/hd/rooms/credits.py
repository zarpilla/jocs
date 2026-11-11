"""
Els crèdits: mar de nit en calma, la lluna i, petita a l'horitzó, l'Arenga amb els llums encesos, que torna
a sortir. Fons sobri: el cel del mig queda net per al text. Les espurnes de la lluna al mar es mouen (ANIMS).
"""
from hd.pix import Light, Canvas, W, H
from hd.rooms.comu import _diff
from hd.rooms.exterior import night_sky, night_sea, arenga, reflection

HOR = 178
MOON = (388, 120)
SHIP = (78, HOR + 2, 1.6)

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)


def sea(cv, frame=0):
    night_sea(cv, HOR, H - 1, moon_x=MOON[0], seed=42, phase=frame * 0.7, calm=0.6)
    reflection(cv, SHIP[0] - 6, SHIP[0] + 72, SHIP[1], 12, k=0.4, seed=43 + frame)


def bg(cv, frame=0):
    night_sky(cv, 0, HOR, moon=MOON, seed=41, clouds=0.42)
    arenga(cv, SHIP[0], SHIP[1], SHIP[2], 'night', facing=1, zodiac=False)
    sea(cv, frame)
    # el que sobresurt de l'Arenga per sota de l'horitzó (el buc) es torna a dibuixar damunt del mar
    arenga(cv, SHIP[0], SHIP[1], SHIP[2], 'night', facing=1, zodiac=False)


PROPS = {}


def _frames():
    base = Canvas(light=LIGHT)
    bg(base)
    frames = []
    for i in range(4):
        cv = Canvas(light=LIGHT, img=base.img.copy())
        sea(cv, i)
        arenga(cv, SHIP[0], SHIP[1], SHIP[2], 'night', facing=1, zodiac=False)
        frames.append(_diff(cv.img, base.img))
    return frames


ANIMS = {'mar': {'frames': _frames, 'frameDuration': 360}}

GEOMETRIA = {'things': {}, 'spawns': {}}
