"""
L'Última Arrel — epíleg, tercera vinyeta (pantalla sencera de 640×360, sense HUD): «Les Fades d'Ortiga tenen un
gronxador nou, fet amb el cable de l'arbre Wi-Fi. La Pica diu que és brutal. La Card diu que és una traïció, i s'hi
gronxa cada dia.»

El campament de les fades (`campament_fades`, el mateix matí daurat), sense el gronxador de cinta rosa: al seu lloc,
el **gronxador nou**, fet amb el cable negre de l'arbre Wi-Fi (dos caps que pengen de la branca de dalt, el seient fet
d'un tros de cable enrotllat i el connector verd que balla al final). La Card s'hi gronxa, decantada cap a la flor,
amb els braços creuats; la Pica vola al costat, contenta. És un primer pla: el tros del gronxador, ampliat ×2.
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)

from hd640.rooms import campament_fades as C
from hd640.rooms.arrel_comu import IRONK, NEON
from hd import arrel as A

LIGHT = C.LIGHT
GIR = 22                                              # el gronxador, decantat cap a la flor (graus)


@functools.lru_cache(maxsize=None)
def _fons():
    """El campament sense el gronxador de cinta i sense la franja negra del HUD (aquí no n'hi ha)."""
    hud = C.hud_negre
    C.hud_negre = lambda cv: None
    try:
        return C._render(frozenset({'sense_gronxador'})).copy()
    finally:
        C.hud_negre = hud


def gronxador(cv):
    """Els dos cables que pengen de la branca de dalt, el seient de cable enrotllat i el connector que penja."""
    px, py = C._penja()
    sx, sy = C._seient(GIR)
    a = math.radians(GIR)
    ux, uy = math.cos(a), -math.sin(a)                                       # al llarg del seient
    dx, dy = math.sin(a), math.cos(a)                                        # avall, al llarg dels cables
    for off, lvl in ((1.5, 2.0), (-1.5, 3.0)):                               # el de darrere, i el del davant
        n = int(math.hypot(sx - px, sy - py))
        for i in range(n + 1):
            t = i / n
            x = px + off * 0.4 + (sx + ux * off * 5 - px) * t
            y = py + (sy + uy * off * 5 - py) * t
            cv.put(x, y, IRONK, lvl + (1.2 if i % 7 == 0 else 0), lit=0.4)
            cv.put(x + 1, y, IRONK, lvl - 0.8, lit=0.4)
    for k in range(3):                                                       # el nus (tres voltes de cable)
        cv.ring(px, py + 2, 3 + k, IRONK, 2.4 + k * 0.4, lit=0.4, step=12)
    for i in range(-11, 12):                                                 # el seient: cable enrotllat
        for j in range(4):
            lvl = 2.0 + (1.6 if (i + j) % 3 == 0 else 0) - j * 0.3
            cv.put(sx + ux * i + dx * j, sy + uy * i + dy * j, IRONK, lvl, lit=0.5)
    # el connector, que penja d'un extrem del seient
    ex, ey = sx + ux * 11 + dx * 3, sy + uy * 11 + dy * 3
    for i in range(12):
        cv.put(ex + math.sin(i / 3) * 1.5, ey + i, IRONK, 2.6, lit=0.4)
    cv.rect(ex - 2, ey + 12, ex + 2, ey + 17, NEON, 3.0, lit=0)
    cv.put(ex, ey + 18, NEON, 4.4, lit=0)


def _fada(qui, facing, k=0):
    img = A.fada(qui, facing, k=k)
    return img.crop(img.getbbox())


def fades(cv):
    """La Card asseguda al seient (de perfil, cap a la flor) i la Pica que vola al costat."""
    from PIL import ImageOps
    sx, sy = C._seient(GIR)
    card = ImageOps.mirror(_fada('card', 'L'))
    card = card.rotate(GIR * 0.6, resample=0, expand=True)
    cv.img.alpha_composite(card, (round(sx - card.width / 2), round(sy - card.height + 13)))
    pica = _fada('pica', 'D', k=1)
    cv.img.alpha_composite(pica, (round(sx - 92), round(sy - 128)))      # (a dalt: la caixa del text va al mig)
    cv.P = cv.img.load()


ZOOM = (318, 14, 638, 194)                            # el tros del campament que es veu, ampliat ×2


@functools.lru_cache(maxsize=None)
def _vinyeta():
    from hd.pix import Canvas
    cv = Canvas(light=LIGHT)
    cv.img.paste(_fons())
    cv.P = cv.img.load()
    gronxador(cv)
    fades(cv)
    return cv.img.crop(ZOOM).resize((cv.w, cv.h), 0)


def bg(cv):
    cv.img.paste(_vinyeta())
    cv.P = cv.img.load()


PROPS = {}
ANIMS = {}
GEOMETRIA = {'things': {}, 'spawns': {}}
