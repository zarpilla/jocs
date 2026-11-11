"""
Pròleg (cinemàtica, sense res clicable): l'Atlàntic Nord de nit, al Punt 7, a les tres de la matinada.
  - a l'esquerra, la popa de l'Arenga (de perfil, la proa fora de quadre) amb la grua i en Bastida a la borda,
    que mira la zòdiac; a la mà, una pantalleta que fa llum (el missatger de satèl·lit);
  - al mig, a l'aigua, la zòdiac amb la Juana i una llanterna; el cable de la grua encara penja;
  - a la dreta, al fons, la plataforma que no surt als mapes: el logotip tapat amb cinta americana, els llums,
    i una silueta a la barana amb uns prismàtics;
  - a dalt, cel de febrer amb núvols i la lluna: lloc per al text.
Els personatges hi són dibuixats (no són sprites).
"""
import math

from hd.pix import Light, Canvas, W, H, hr, mix
from hd.rooms.comu import _diff
from hd.rooms.exterior import (night_sky, night_sea, arenga, platform, reflection, HULLN, STEELX, NSEA, ROPE,
                               GLOW_WARM, sheer)

HOR = 140
SHIP = (196, 182, 7.0)        # popa (x), flotació (y), píxels per metre; la proa mira a l'esquerra
ZOD = (292, 204)              # la zòdiac (centre, flotació)
PLAT = (402, HOR + 3, 3.0)

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)

SIL = [(4, 5, 8), (8, 9, 14), (14, 16, 22), (22, 24, 32), (34, 36, 46)]
JACKET = [(20, 8, 6), (50, 16, 10), (96, 34, 16), (150, 62, 28), (196, 104, 50)]
SKINR = [(40, 22, 18), (90, 52, 40), (150, 96, 70), (200, 140, 104)]
ZODR = [(18, 18, 22), (30, 30, 36), (46, 46, 52), (66, 66, 72), (90, 90, 94), (120, 120, 122)]


def bastida(cv, x, y):
    """En Bastida a la borda de popa: gorra, l'anorac fosc, la pipa i, a la mà, la pantalleta que fa llum."""
    # cos (de la cintura amunt, la resta queda darrere la borda)
    cv.rect(x - 3, y - 11, x + 3, y, SIL, 2.4)
    cv.vline(x + 3, y - 10, y, SIL, 3.2)
    cv.rect(x - 2, y - 16, x + 2, y - 12, SKINR, 1.6)                     # cara, mig a l'ombra
    cv.put(x + 2, y - 14, SKINR, 2.6)
    cv.rect(x - 3, y - 18, x + 3, y - 17, SIL, 1.2)                       # gorra
    cv.hline(x - 3, x + 4, y - 16, SIL, 0.8)
    cv.rect(x - 2, y - 13, x + 2, y - 12, [(200, 200, 196)], 0, lit=0)   # la barba blanca
    cv.put(x + 3, y - 13, ROPE, 2.0)                                       # la pipa
    cv.put(x + 4, y - 13, ROPE, 2.0)
    cv.put(x + 4, y - 14, [(255, 140, 60)], 0, lit=0)
    # el braç i la pantalleta
    cv.line(x - 2, y - 9, x - 5, y - 5, SIL, 3.0)
    cv.rect(x - 7, y - 6, x - 5, y - 4, [(140, 220, 255)], 0, lit=0)
    cv.glow(x - 6, y - 5, 6, (120, 210, 255), 0.5)


def juana_zodiac(cv):
    """La zòdiac a l'aigua: flotadors grisos, el motor, i la Juana amb la llanterna i el pot."""
    cx, wl = ZOD
    # flotador amb volum
    for x in range(cx - 26, cx + 27):
        t = (x - cx + 26) / 52
        lift = int(3 * max(0.0, (t - 0.8) / 0.2) ** 1.5) if t > 0.8 else 0
        r = 4 if t < 0.95 else 3
        cyy = wl - 3 - lift
        for y in range(cyy - r, cyy + r + 1):
            u = (y - cyy) / (r + 0.5)
            cv.put(x, y, ZODR, 2.6 - u * 1.4 - u * u, lit=0)
        if 1 <= (wl - 3 - lift) and t < 0.98:
            cv.put(x, cyy + 1, [(140, 50, 20), (200, 90, 40)], 0.4, lit=0)
    # el motor (popa, a l'esquerra)
    cv.rect(cx - 32, wl - 12, cx - 26, wl - 5, ZODR, 1.0, lit=0)
    cv.rect(cx - 30, wl - 5, cx - 28, wl + 1, ZODR, 0.6, lit=0)
    # la Juana, asseguda, inclinada sobre l'aigua amb el pot
    jx, jy = cx + 4, wl - 7
    cv.rect(jx - 3, jy - 9, jx + 3, jy, JACKET, 2.0, lit=0)             # anorac vermell
    cv.vline(jx - 3, jy - 9, jy, JACKET, 3.0, lit=0)
    cv.rect(jx - 2, jy - 14, jx + 2, jy - 10, SKINR, 1.8, lit=0)
    cv.rect(jx - 3, jy - 16, jx + 3, jy - 14, [(20, 50, 30), (40, 90, 50), (70, 130, 80)], 1.0, lit=0)   # gorra verda
    cv.put(jx - 3, jy - 13, [(30, 20, 14)], 0, lit=0)
    cv.put(jx - 3, jy - 12, [(30, 20, 14)], 0, lit=0)
    # el braç enlaire amb el pot a contrallum
    cv.line(jx + 2, jy - 8, jx + 8, jy - 15, JACKET, 2.4, lit=0)
    cv.rect(jx + 7, jy - 21, jx + 10, jy - 15, [(60, 56, 46), (110, 104, 84), (170, 164, 140), (220, 216, 196)], 1.6, lit=0)
    cv.rect(jx + 7, jy - 22, jx + 10, jy - 22, [(220, 216, 196)], 0, lit=0)
    cv.rect(jx + 8, jy - 18, jx + 9, jy - 15, [(90, 86, 76)], 0, lit=0)        # el fang gris
    # la llanterna (a l'altra mà), amb el feix cap al pot
    lx, ly = jx - 4, jy - 6
    cv.rect(lx - 2, ly - 1, lx, ly + 1, SIL, 3.0, lit=0)
    for i in range(1, 24):
        for w in range(-i // 4, i // 4 + 1):
            px, py = lx + 1 + round(i * 0.55) + w // 2, ly - round(i * 0.55) + w
            if 0 <= px < W and 0 <= py < H and hr(px, py, 9) > i / 30:
                cv.flat(px, py, mix(cv.get(px, py), (255, 236, 180), 0.35 * (1 - i / 26)))
    cv.glow(lx, ly, 6, (255, 240, 200), 0.8)
    cv.glow(jx + 8, jy - 18, 9, GLOW_WARM, 0.35)
    # l'ombra i el reflex de la llanterna a l'aigua
    for y in range(wl + 1, wl + 14):
        for x in range(cx - 30, cx + 30):
            k = 0.35 * (1 - (y - wl) / 14) * max(0.0, 1 - abs(x - (cx - 2)) / 30)
            if hr(x // 2, y, 31) > 0.45 and k > 0.05:
                cv.flat(x, y, mix(cv.get(x, y), (255, 214, 140), k))
    # anells a l'aigua
    for k, rr in enumerate((34, 40)):
        for a in range(0, 360, 3):
            px = cx + round(math.cos(math.radians(a)) * rr)
            py = wl + 2 + round(math.sin(math.radians(a)) * rr * 0.12)
            if py > wl and hr(a, k) > 0.4:
                cv.flat(px, py, mix(cv.get(px, py), (120, 140, 160), 0.35))


def crane_wire(cv, X, Y):
    """El cable de la grua, que penja fins a tocar l'aigua (la zòdiac ja s'ha deixat anar)."""
    tx, ty = X(-1.6), Y(7.9)
    cv.line(X(3.2), Y(5.8), tx, ty, [(60, 46, 10), (130, 100, 20), (200, 160, 40), (236, 200, 80)], 2.0, lit=0)
    cv.line(X(3.2), Y(5.3), tx, ty + 1, [(60, 46, 10), (130, 100, 20), (200, 160, 40), (236, 200, 80)], 1.0, lit=0)
    for y in range(int(ty), int(SHIP[1]) + 4):
        cv.put(tx, y, STEELX, 3.0, lit=0)
    cv.rect(tx - 1, SHIP[1] + 4, tx + 1, SHIP[1] + 6, STEELX, 3.6, lit=0)


def bg(cv, frame=0):
    night_sky(cv, 0, HOR, moon=(96, 36), seed=21, clouds=0.6)
    night_sea(cv, HOR, H - 1, moon_x=96, seed=22, phase=frame * 0.8)
    platform(cv, PLAT[0], PLAT[1], PLAT[2], 'night', watcher=True)
    reflection(cv, PLAT[0] - 60, PLAT[0] + 60, PLAT[1], 40, k=0.45, seed=23 + frame)
    xs, ywl, s = SHIP
    X, Y = arenga(cv, xs, ywl, s, 'night', facing=-1, crane=True, zodiac=False)
    crane_wire(cv, X, Y)
    bastida(cv, round(X(5.5)), round(Y(sheer(5.5)) - 1))
    reflection(cv, 0, xs + 16, ywl, 34, k=0.32, seed=25 + frame)
    juana_zodiac(cv)
    if frame % 2:
        cv.glow(PLAT[0] + 10 * PLAT[2], PLAT[1] - 30 * PLAT[2], 6, (255, 40, 30), 0.3)


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
    'spawns': {'bastida': (154, 150), 'juana': (296, 200)},
}
