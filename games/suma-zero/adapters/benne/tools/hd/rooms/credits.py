"""
Els crèdits (cinemàtica del final): la mateixa Ginebra de nit del pròleg, perquè el joc acabi on va començar.
  - el llac, les muntanyes i la seu del BCMU, com al pròleg;
  - però la pantalla gegant de la façana ja no fa l'anunci del Director: està apagada, amb un rètol de
    «FORA DE SERVEI», i a la torre hi ha menys finestres enceses (avui tothom ha plegat a l'hora);
  - el raig d'aigua i els reflexos es mouen com al pròleg.
"""
from hd.pix import Light, Canvas, hr
from hd.rooms.comu import outline, text, text_width, _diff
from hd.rooms import proleg_ginebra as pr

LIGHT = Light(ambient=0.0)


def pantalla_apagada(cv):
    """La pantalla de la façana, apagada: negra, amb el reflex del llac i un rètol de «FORA DE SERVEI»."""
    x0, y0, x1, y1 = pr.SCREEN
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, [(2, 3, 6), (5, 7, 12), (9, 12, 20), (14, 18, 28)], 1.2 + (x - x0) / 60 - (y - y0) / 90, lit=0)
    for y in range(y0, y1 + 1, 2):                                       # les línies de la pantalla
        cv.tint(x0, y, x1, y, (0, 0, 0), 0.25)
    s = 'FORA DE SERVEI'
    tx = (x0 + x1) // 2 - text_width(s) // 2
    cv.rect(tx - 3, (y0 + y1) // 2 - 4, tx + text_width(s) + 2, (y0 + y1) // 2 + 6, [(200, 150, 30)], 0, lit=0)
    text(cv, s, tx, (y0 + y1) // 2 - 1, [(20, 14, 4)], 0, lit=0, flat=(20, 14, 4))
    outline(cv, x0 - 1, y0 - 1, x1 + 1, y1 + 1, [(4, 6, 10)])


def finestres_apagades(cv):
    """Avui la torre plega a l'hora: s'apaguen moltes de les finestres que al pròleg eren enceses."""
    x0, x1 = pr.TOWER
    for y in range(20, pr.BASE_Y):
        for x in range(x0, x1 + 1):
            if pr.SCREEN[0] - 2 <= x <= pr.SCREEN[2] + 2 and pr.SCREEN[1] - 2 <= y <= pr.SCREEN[3] + 2:
                continue
            r, g, b, _ = cv.img.getpixel((x, y))
            if r > 120 and r > b + 40 and hr(x // 6, y // 5, 31) > 0.3:     # una finestra càlida: s'apaga
                cv.img.putpixel((x, y), (r // 6, g // 6 + 6, b // 4 + 14, 255))


def bg(cv, frame=0):
    pr.sky(cv)
    pr.mountains(cv)
    pr.city(cv)
    pr.bcmu(cv)
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
