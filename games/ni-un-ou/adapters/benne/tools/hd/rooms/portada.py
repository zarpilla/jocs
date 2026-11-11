"""
La portada: «NI UN OU» damunt l'Atlàntic Nord, de nit.
  - el títol en lletres de píxel grosses: blanc d'escuma a dalt, que s'embruta cap a baix de fang gris
    verdós i regalima;
  - l'Arenga de perfil a l'esquerra, amb els llums encesos, i la plataforma al fons a la dreta, amb el seu
    llum vermell;
  - la lluna entre núvols i el seu camí al mar.
Els botons de la GUI `portada` van a 165..315 × 168..246: allà només hi ha mar.
"""
import math

from hd.pix import Light, Canvas, W, H, hr, mix
from hd.rooms.comu import _diff
from hd.rooms.exterior import night_sky, night_sea, arenga, platform, reflection, NSEA
from room_designs import LLETRES

HOR = 128
TITLE_Y = 16
S = 6                                    # mida del píxel de les lletres
SHIP = (14, 152, 4.0)
PLAT = (404, HOR + 2, 2.2)

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)

FOAM = [(16, 30, 40), (40, 70, 84), (90, 130, 140), (150, 190, 196), (206, 230, 230), (240, 250, 248)]
MUD = [(20, 22, 16), (40, 42, 30), (62, 64, 44), (86, 86, 58), (110, 106, 72), (136, 128, 90), (160, 152, 112)]
EDGE = [(4, 8, 14)]


def title(cv):
    word = 'NI UN OU'
    width = len(word) * 6 * S - S
    x0 = (W - width) // 2
    cells = []
    for i, ch in enumerate(word):
        for r, bits in enumerate(LLETRES[ch]):
            for c, bit in enumerate(bits):
                if bit == '1':
                    cells.append((x0 + (i * 6 + c) * S, TITLE_Y + r * S, r, i, c))
    # ombra i vora
    for x, y, r, i, c in cells:
        cv.rect(x + 3, y + 4, x + S + 2, y + S + 3, [(2, 3, 8)], 0, lit=0)
    for x, y, r, i, c in cells:
        cv.rect(x - 1, y - 1, x + S, y + S, EDGE, 0, lit=0)
    # el cos: escuma a dalt, fang a baix (la línia de l'aigua bruta fa onades)
    for x, y, r, i, c in cells:
        for py in range(y, y + S):
            for px in range(x, x + S):
                line = TITLE_Y + 4.1 * S + math.sin(px / 9 + 0.6) * 2.4 + math.sin(px / 3.7) * 0.8
                if py < line:
                    t = (py - TITLE_Y) / (4.1 * S)
                    lvl = 5.2 - t * 1.6 + (0.8 if py == y else 0) - (0.6 if px == x + S - 1 else 0)
                    cv.put(px, py, FOAM, lvl, lit=0)
                else:
                    t = (py - line) / (2.9 * S)
                    lvl = 4.6 - t * 1.8 + (hr(px // 2, py // 2, 5) - 0.5) * 0.9 - (0.6 if px == x + S - 1 else 0)
                    cv.put(px, py, MUD, lvl, lit=0)
                if abs(py - line) < 0.8:
                    cv.flat(px, py, (196, 206, 180))
    # regalims de fang sota algunes lletres
    bottoms = {}
    for x, y, r, i, c in cells:
        for px in range(x, x + S):
            bottoms[px] = max(bottoms.get(px, 0), y + S)
    for k, px in enumerate(sorted(bottoms)):
        if hr(px // 3, 77) > 0.86 and hr(px, 78) > 0.3:
            n = 3 + int(hr(px // 3, 79) * 12)
            y0 = bottoms[px]
            for dx in (0, 1):
                if bottoms.get(px + dx) != y0:
                    continue
                for y in range(y0, y0 + n - dx * 2):
                    cv.put(px + dx, y, MUD, 2.4 - (y - y0) * 0.08, lit=0)
            cv.disc(px + 0.5, y0 + n, 1.2, 1.5, MUD, 2.6, lit=0)
            cv.flat(px, y0 + n - 1, (150, 146, 110))
    cv.glow(W // 2, TITLE_Y + 20, 170, (120, 170, 190), 0.05)


def bg(cv, frame=0):
    night_sky(cv, 0, HOR, moon=(44, 82), seed=31, clouds=0.55)
    night_sea(cv, HOR, H - 1, moon_x=44, seed=32, phase=frame * 0.8)
    platform(cv, PLAT[0], PLAT[1], PLAT[2], 'night')
    reflection(cv, PLAT[0] - 50, PLAT[0] + 50, PLAT[1], 30, k=0.45, seed=33 + frame)
    xs, ywl, s = SHIP
    arenga(cv, xs, ywl, s, 'night', facing=1)
    reflection(cv, xs - 8, xs + 168, ywl, 30, k=0.3, seed=35 + frame)
    if frame % 4 == 3:
        cv.flat(PLAT[0] + 10 * PLAT[2], PLAT[1] - 30 * PLAT[2], (90, 20, 20))
    title(cv)


PROPS = {}


def _frames():
    base = Canvas(light=LIGHT)
    bg(base)
    frames = []
    for i in range(4):
        cv = Canvas(light=LIGHT)
        bg(cv, i)
        frames.append(_diff(cv.img, base.img))
    return frames


ANIMS = {'mar': {'frames': _frames, 'frameDuration': 360}}

GEOMETRIA = {'things': {}, 'spawns': {}}
