"""
Prova a 640×360: el pròleg (vegeu hd/rooms/proleg_punt7.py, el de 480×270). Cinemàtica a pantalla sencera,
sense res clicable: l'Atlàntic Nord de nit, al Punt 7, a les tres de la matinada.
  - a l'esquerra, la popa de l'Arenga amb la grua, i en Bastida a la borda amb la pipa encesa i el missatger
    de satèl·lit que li il·lumina la mà;
  - al mig, la zòdiac amb la Juana: la llanterna, el feix, el pot de fang a contrallum;
  - a la dreta, al fons, la plataforma amb la silueta dels prismàtics;
  - a dalt, cel amb núvols i la lluna: lloc per al text.
Els personatges hi són dibuixats (no són sprites); a 640 tenen cara, barba, pipa amb fum, gorra amb pompó.
"""
import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

import math

from hd.pix import Light, Canvas, W, H, hr, mix
from hd.rooms.comu import _diff
from hd.rooms.exterior import arenga, platform, reflection, STEELX, ROPE, GLOW_WARM, sheer
from hd640.rooms.portada import night_sky, night_sea, K

HOR = 187
SHIP = (261, 243, 7.0 * K)    # popa (x), flotació (y), píxels per metre; la proa mira a l'esquerra
ZOD = (389, 272)              # la zòdiac (centre, flotació)
PLAT = (536, HOR + 4, 3.0 * K)
MOON = (128, 48)

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)

SIL = [(4, 5, 8), (8, 9, 14), (14, 16, 22), (22, 24, 32), (34, 36, 46)]
JACKET = [(20, 8, 6), (50, 16, 10), (96, 34, 16), (150, 62, 28), (196, 104, 50)]
SKINR = [(40, 22, 18), (90, 52, 40), (150, 96, 70), (200, 140, 104)]
ZODR = [(18, 18, 22), (30, 30, 36), (46, 46, 52), (66, 66, 72), (90, 90, 94), (120, 120, 122)]
HAT = [(14, 34, 20), (20, 50, 30), (40, 90, 50), (70, 130, 80)]
BEARD = [(110, 110, 108), (160, 160, 156), (200, 200, 196), (226, 226, 222)]
JAR = [(60, 56, 46), (110, 104, 84), (170, 164, 140), (220, 216, 196)]
CRANEW = [(60, 46, 10), (130, 100, 20), (200, 160, 40), (236, 200, 80)]


def bastida(cv, x, y):
    """En Bastida a la borda de popa: gorra, barba blanca, la pipa encesa i, a la mà, la pantalleta que fa llum."""
    # el cos (de la cintura amunt; la resta queda darrere la borda): l'anorac fosc amb el coll alçat
    cv.rect(x - 4, y - 15, x + 4, y, SIL, 2.4)
    cv.vline(x + 4, y - 14, y, SIL, 3.2)                                   # la vora de la dreta, amb la lluna
    cv.vline(x - 4, y - 14, y, SIL, 1.6)
    cv.hline(x - 4, x + 4, y - 15, SIL, 3.0)                               # el coll
    cv.vline(x, y - 13, y, SIL, 1.4)                                       # la cremallera
    # la cara, mig a l'ombra, i l'ull
    cv.rect(x - 3, y - 22, x + 3, y - 16, SKINR, 1.6)
    cv.vline(x + 2, y - 21, y - 17, SKINR, 2.6)
    cv.vline(x + 3, y - 21, y - 18, SKINR, 2.2)
    cv.flat(x + 1, y - 20, (16, 10, 10))
    cv.hline(x, x + 2, y - 21, BEARD, 1.2)                                 # la cella, blanca
    # la barba blanca, que s'aprima cap avall
    cv.rect(x - 3, y - 18, x + 3, y - 16, BEARD, 2.4, lit=0)
    cv.hline(x - 2, x + 2, y - 15, BEARD, 2.0, lit=0)
    cv.put(x + 2, y - 17, BEARD, 3.0, lit=0)
    # la gorra de llana, amb la vora girada
    cv.rect(x - 4, y - 26, x + 3, y - 23, SIL, 1.2)
    cv.hline(x - 4, x + 4, y - 23, SIL, 2.2)
    cv.hline(x - 3, x + 2, y - 26, SIL, 1.8)
    # la pipa, amb la brasa i un fil de fum
    cv.hline(x + 3, x + 5, y - 17, ROPE, 2.0)
    cv.rect(x + 5, y - 19, x + 6, y - 17, ROPE, 1.6)
    cv.flat(x + 5, y - 20, (255, 140, 60))
    cv.flat(x + 6, y - 20, (200, 80, 30))
    cv.glow(x + 5, y - 20, 3, (255, 140, 60), 0.4)
    for i in range(7):
        cv.flat(x + 6 + round(math.sin(i * 0.9) * 1.2), y - 22 - i * 2,
                mix(cv.get(x + 6 + round(math.sin(i * 0.9) * 1.2), y - 22 - i * 2), (120, 126, 140), 0.35 - i * 0.04))
    # el braç i la pantalleta (el missatger de satèl·lit), que li il·lumina la mà i la barba
    cv.line(x - 3, y - 12, x - 7, y - 7, SIL, 3.0)
    cv.line(x - 3, y - 11, x - 7, y - 6, SIL, 2.0)
    cv.rect(x - 10, y - 8, x - 7, y - 4, [(30, 50, 70)], 0, lit=0)
    cv.rect(x - 9, y - 7, x - 8, y - 5, [(150, 226, 255)], 0, lit=0)
    cv.glow(x - 8, y - 6, 9, (120, 210, 255), 0.5)
    cv.flat(x - 3, y - 16, mix(cv.get(x - 3, y - 16), (140, 210, 240), 0.35))


def juana_zodiac(cv):
    """La zòdiac a l'aigua: flotadors grisos amb la franja taronja, el motor, i la Juana amb la llanterna i el pot."""
    cx, wl = ZOD
    # el flotador, amb volum; s'aixeca una mica a proa
    for x in range(cx - 35, cx + 36):
        t = (x - cx + 35) / 70
        lift = int(4 * max(0.0, (t - 0.8) / 0.2) ** 1.5) if t > 0.8 else 0
        r = 5 if t < 0.95 else 4
        cyy = wl - 4 - lift
        for y in range(cyy - r, cyy + r + 1):
            u = (y - cyy) / (r + 0.5)
            cv.put(x, y, ZODR, 2.6 - u * 1.4 - u * u, lit=0)
        if t < 0.98:
            cv.put(x, cyy + 1, [(140, 50, 20), (200, 90, 40)], 0.4, lit=0)
            cv.put(x, cyy + 2, [(140, 50, 20), (200, 90, 40)], 0.0, lit=0)
        if x % 9 == 0 and t < 0.95:                                         # les manetes de corda
            cv.put(x, cyy - r + 1, ROPE, 2.4, lit=0)
            cv.put(x + 1, cyy - r + 1, ROPE, 2.4, lit=0)
    # el motor fora borda (a popa, a l'esquerra)
    cv.rect(cx - 43, wl - 16, cx - 35, wl - 7, ZODR, 1.0, lit=0)
    cv.hline(cx - 43, cx - 35, wl - 16, ZODR, 2.2, lit=0)
    cv.rect(cx - 41, wl - 7, cx - 38, wl + 2, ZODR, 0.6, lit=0)
    cv.put(cx - 42, wl - 13, [(140, 50, 20), (200, 90, 40)], 1.0, lit=0)
    # la Juana, asseguda, inclinada sobre l'aigua
    jx, jy = cx + 5, wl - 9
    cv.rect(jx - 4, jy - 12, jx + 4, jy, JACKET, 2.0, lit=0)                # l'anorac vermell
    cv.vline(jx - 4, jy - 12, jy, JACKET, 3.0, lit=0)
    cv.hline(jx - 3, jx + 3, jy - 6, JACKET, 1.2, lit=0)                   # la costura de la butxaca
    cv.rect(jx - 3, jy - 19, jx + 3, jy - 13, SKINR, 1.8, lit=0)            # la cara
    cv.vline(jx - 3, jy - 18, jy - 14, SKINR, 2.8, lit=0)                  # il·luminada per la llanterna
    cv.flat(jx - 2, jy - 17, (16, 10, 10))
    cv.hline(jx - 3, jx - 1, jy - 17, [(200, 210, 220)], 0, lit=0)          # les ulleres, un reflex
    cv.flat(jx - 2, jy - 17, (16, 10, 10))
    for yy in range(jy - 18, jy - 12):                                      # els cabells, castanys, sota la gorra
        cv.put(jx + 3, yy, [(30, 20, 14), (56, 36, 24)], 0.6, lit=0)
    cv.put(jx + 4, jy - 14, [(30, 20, 14), (56, 36, 24)], 0.4, lit=0)
    cv.rect(jx - 4, jy - 22, jx + 4, jy - 19, HAT, 1.6, lit=0)             # la gorra verda, amb la vora i el pompó
    cv.hline(jx - 4, jx + 4, jy - 19, HAT, 2.6, lit=0)
    cv.disc(jx, jy - 23, 1.6, 1.4, HAT, 3.0, lit=0)
    # el braç enlaire amb el pot a contrallum
    cv.line(jx + 3, jy - 10, jx + 11, jy - 20, JACKET, 2.4, lit=0)
    cv.line(jx + 3, jy - 9, jx + 11, jy - 19, JACKET, 1.4, lit=0)
    cv.rect(jx + 9, jy - 28, jx + 13, jy - 20, JAR, 1.6, lit=0)
    cv.hline(jx + 9, jx + 13, jy - 29, [(120, 120, 124), (170, 170, 172)], 1.0, lit=0)   # la tapa
    cv.vline(jx + 10, jy - 27, jy - 21, JAR, 3.0, lit=0)                    # el reflex del vidre
    cv.rect(jx + 11, jy - 24, jx + 12, jy - 21, [(90, 86, 76)], 0, lit=0)   # el fang gris, al fons
    cv.hline(jx + 10, jx + 12, jy - 24, [(130, 126, 106)], 0, lit=0)
    # la llanterna (a l'altra mà), amb el feix cap al pot
    lx, ly = jx - 5, jy - 8
    cv.rect(lx - 3, ly - 1, lx, ly + 1, SIL, 3.0, lit=0)
    cv.flat(lx + 1, ly, (255, 246, 220))
    for i in range(1, 32):
        for w in range(-i // 4, i // 4 + 1):
            px, py = lx + 1 + round(i * 0.55) + w // 2, ly - round(i * 0.55) + w
            if 0 <= px < W and 0 <= py < H and hr(px, py, 9) > i / 40:
                cv.flat(px, py, mix(cv.get(px, py), (255, 236, 180), 0.35 * (1 - i / 34)))
    cv.glow(lx, ly, 8, (255, 240, 200), 0.8)
    cv.glow(jx + 11, jy - 24, 12, GLOW_WARM, 0.35)
    # el reflex de la llanterna a l'aigua
    for y in range(wl + 1, wl + 18):
        for x in range(cx - 40, cx + 40):
            k = 0.35 * (1 - (y - wl) / 18) * max(0.0, 1 - abs(x - (cx - 3)) / 40)
            if hr(x // 2, y, 31) > 0.45 and k > 0.05:
                cv.flat(x, y, mix(cv.get(x, y), (255, 214, 140), k))
    # anells a l'aigua
    for k, rr in enumerate((45, 53)):
        for a in range(0, 360, 2):
            px = cx + round(math.cos(math.radians(a)) * rr)
            py = wl + 3 + round(math.sin(math.radians(a)) * rr * 0.12)
            if py > wl and hr(a, k) > 0.4:
                cv.flat(px, py, mix(cv.get(px, py), (120, 140, 160), 0.35))


def crane_wire(cv, X, Y):
    """El cable de la grua, que penja fins a tocar l'aigua (la zòdiac ja s'ha deixat anar)."""
    tx, ty = X(-1.6), Y(7.9)
    cv.line(X(3.2), Y(5.8), tx, ty, CRANEW, 2.0, lit=0)
    cv.line(X(3.2), Y(5.5), tx, ty + 1, CRANEW, 3.0, lit=0)
    cv.line(X(3.2), Y(5.3), tx, ty + 2, CRANEW, 1.0, lit=0)
    for y in range(int(ty), int(SHIP[1]) + 5):
        cv.put(tx, y, STEELX, 3.0, lit=0)
        cv.put(tx + 1, y, STEELX, 1.8, lit=0)
    cv.rect(tx - 1, SHIP[1] + 5, tx + 2, SHIP[1] + 8, STEELX, 3.6, lit=0)   # el ganxo, que toca l'aigua
    cv.put(tx + 2, SHIP[1] + 9, STEELX, 4.2, lit=0)


def bg(cv, frame=0):
    night_sky(cv, 0, HOR, moon=MOON, seed=21, clouds=0.6)
    night_sea(cv, HOR, H - 1, moon_x=MOON[0], seed=22, phase=frame * 0.8)
    platform(cv, PLAT[0], PLAT[1], PLAT[2], 'night', watcher=True)
    reflection(cv, PLAT[0] - 80, PLAT[0] + 80, PLAT[1], 53, k=0.45, seed=23 + frame)
    xs, ywl, s = SHIP
    X, Y = arenga(cv, xs, ywl, s, 'night', facing=-1, crane=True, zodiac=False)
    crane_wire(cv, X, Y)
    bastida(cv, round(X(5.5)), round(Y(sheer(5.5)) - 1))
    reflection(cv, 0, xs + 21, ywl, 45, k=0.32, seed=25 + frame)
    juana_zodiac(cv)
    if frame % 2:                                          # el llum vermell de la plataforma
        cv.glow(PLAT[0] + 10 * PLAT[2], PLAT[1] - 30 * PLAT[2], 8, (255, 40, 30), 0.3)


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


ANIMS = {'mar': {'frames': _frames, 'frameDuration': 320}}

GEOMETRIA = {
    'things': {},
    'spawns': {'bastida': (205, 200), 'juana': (395, 267)},
}
