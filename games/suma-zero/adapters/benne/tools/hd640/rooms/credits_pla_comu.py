"""
**El dibuix pla de sempre** (font de les textures de credits.py, que és en 3D).

Els crèdits (cinemàtica del final), a 640×360 (vegeu hd/rooms/credits.py, la de 480×270): la mateixa Ginebra
de nit del pròleg, perquè el joc acabi on va començar.
  - el llac, les muntanyes i la seu del BCMU, com al pròleg;
  - però la pantalla gegant de la façana ja no fa l'anunci del Director: està apagada (només hi queda el reflex
    de la lluna), amb un rètol de «FORA DE SERVEI», i a la torre hi ha menys finestres enceses (avui tothom ha
    plegat a l'hora);
  - el raig d'aigua, els reflexos i el llum de l'antena es mouen com al pròleg.
Animació: `nit`.
"""
import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

from hd.pix import Light, Canvas, hr
from hd.rooms.comu import outline, text, text_width, _diff
from hd640.rooms import proleg_ginebra_pla_comu as pr

Canvas1x = Canvas                                   # (a 1×, com la sala en 3D)

LIGHT = Light(ambient=0.0)


def pantalla_apagada(cv):
    """La pantalla de la façana, apagada: negra, amb el reflex de la lluna i un rètol de «FORA DE SERVEI»."""
    x0, y0, x1, y1 = pr.SCREEN
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            sheen = max(0, 1 - abs((x - x0) - 70 + (y - y0) * 0.6) / 9) * 0.9      # el reflex, en diagonal
            cv.put(x, y, [(2, 3, 6), (5, 7, 12), (9, 12, 20), (14, 18, 28)], 1.2 + (x - x0) / 80 - (y - y0) / 120 + sheen, lit=0)
    for y in range(y0, y1 + 1, 2):                                       # les línies de la pantalla
        cv.tint(x0, y, x1, y, (0, 0, 0), 0.25)
    cv.flat(x1 - 6, y1 - 5, (60, 10, 10))                                # el pilot d'espera, apagat
    s = 'FORA DE SERVEI'
    tw = text_width(s)
    tx = (x0 + x1) // 2 - tw // 2
    ty = (y0 + y1) // 2 - 1
    cv.rect(tx - 4, ty - 4, tx + tw + 3, ty + 8, [(130, 92, 16), (200, 150, 30), (240, 200, 70)],
            lambda x, y: 1 + (1 if y == ty - 4 else 0) - (1 if y == ty + 8 else 0), lit=0)
    for (px, py) in ((tx - 3, ty - 3), (tx + tw + 2, ty - 3), (tx - 3, ty + 7), (tx + tw + 2, ty + 7)):
        cv.flat(px, py, (90, 60, 10))                                    # els cargols del rètol
    text(cv, s, tx, ty, [(20, 14, 4)], 0, lit=0, flat=(20, 14, 4))
    outline(cv, x0 - 1, y0 - 1, x1 + 1, y1 + 1, [(4, 6, 10)])
    outline(cv, x0 - 2, y0 - 2, x1 + 2, y1 + 2, [(30, 34, 40)])


def finestres_apagades(cv):
    """Avui la torre plega a l'hora: s'apaguen moltes de les finestres que al pròleg eren enceses."""
    x0, x1 = pr.TOWER
    sx0, sy0, sx1, sy1 = pr.SCREEN
    for X, Y, _, _ in cv.pixels(x0, pr.TOP, x1, pr.BASE_Y - 1):
        x, y = X // cv.S, Y // cv.S
        if sx0 - 3 <= x <= sx1 + 3 and sy0 - 3 <= y <= sy1 + 3:
            continue
        r, g, b, _ = cv.P[X, Y]
        lit = (r > 120 and r > b + 40) or (b > 150 and g > 120)        # una finestra càlida o un fluorescent
        if lit and hr((x - x0) // pr.BAY, (y - pr.TOP) // pr.FLOOR, 31) > 0.3:     # s'apaga
            cv.P[X, Y] = (r // 6, g // 6 + 6, b // 4 + 14, 255)


def bg(cv, frame=0):
    pr.sky(cv)
    pr.mountains(cv)
    pr.city(cv)
    pr.bcmu(cv, antenna=frame % 3 != 2)
    finestres_apagades(cv)
    pantalla_apagada(cv)
    pr.lake(cv)
    pr.jet(cv, frame)
    pr.reflections(cv, frame)


PROPS = {}


def _frames():
    base = Canvas(light=LIGHT)
    bg(base)
    frames = []
    for i in range(6):
        cv = Canvas(light=LIGHT)
        bg(cv, i)
        frames.append(_diff(cv.img, base.img))
    return frames


ANIMS = {'nit': {'frames': _frames, 'frameDuration': 260}}

GEOMETRIA = {'things': {}, 'spawns': {}, 'walkable': [(200, 253), (267, 253), (267, 261), (200, 261)]}
