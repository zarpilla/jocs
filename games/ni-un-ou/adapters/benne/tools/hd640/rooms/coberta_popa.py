"""
Prova a 640×360: la coberta de popa de l'Arenga (vegeu hd/rooms/coberta_popa.py, la de 480×270).
Mateixa composició ×4/3, dibuixada de nou: el cel, el mar i els núvols es calculen a la resolució nova (no
s'amplien), i hi ha detall que a 480 no hi cabia: rètols llegibles (MENJADOR, la grua, la zòdiac), reblons i
soldadures, l'antilliscant de la coberta, el cable de la grua amb dos fils, la porta estanca més treballada.
Props: `dia`, `plataforma`, `taula`, `horitzo`. ANIMS: `mar`, `dia_mar`, `plataforma`.
"""
import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

import math

from hd.pix import Canvas, Light, W, H, hr, mix, B4
from hd.rooms.arenga import YELL, REDP
from hd.rooms.comu import _diff, text
from hd.rooms.exterior import (vnoise, fbm, smooth, platform, lifebuoy,
                               NSKY, NSEA, DSKY, DCLOUD, DSEA, TURBID, HULLN, REDH, STEELX, CABX, DECKX, ORANGEB,
                               ROPE, LAMP, WINDOW, GLOW_WARM, GLOW_MOON, RUST_)

# Art a 2× (1280×720 per a una sala de 640×360): el mateix dibuix, amb les formes, el dither i la llum a la
# resolució real (hd1280/canvas2x.py); el motor el mostra a 1/2 (artScale al .room.json).
ART_SCALE = 2
from hd1280.canvas2x import Canvas2x as Canvas  # noqa: E402,F811
from hd.pix import Canvas as Canvas1x  # noqa: E402,F401  (llenços auxiliars en píxels de sala: figures, textos)

K = 4 / 3
HOR = 115           # l'horitzó
RAIL = 141          # la regala de la borda
FLOOR_Y = 203
HOUSE = (493, 601)  # la caseta (porta del menjador)
DOOR = (528, 96, 584, 203)
MOON = (400, 35)
SUN = (53, 27)

LIGHT = Light(ambient=-0.1, vignette=(67, 32), floor_fade=(264, 40))
LIGHT.point(556, 80, r=267, k=3.2, squash=1.1, down=True, power=1.4)      # focus sobre la porta
LIGHT.point(69, 67, r=227, k=2.6, squash=0.9, down=True, power=1.5)       # focus de la grua
LIGHT.point(621, 40, r=61, k=1.0, power=1.8)                               # llum del pas lateral
LIGHT.point(320, 267, r=347, k=0.6, squash=2.5, power=1.2)                 # rebot de la coberta

LIGHT_DAY = Light(ambient=3.4, vignette=(53, 24), floor_fade=(267, 53))
LIGHT_DAY.point(80, -53, r=560, k=1.3, power=1.2)
LIGHT_DAY.add(lambda x, y: -1.6 if (x > 603 and 29 <= y < 213) else 0.0)


# ─── Cel i mar (calculats a 640: el soroll va en coordenades de 480, mostrejat més fi) ──────

def night_sky(cv, y0, hor, moon, seed=4, clouds=0.55):
    for y in range(y0, hor + 1):
        t = (y - y0) / max(1, hor - y0)
        for x in range(W):
            u, v = x / K, y / K
            lvl = 1.0 + 3.0 * t ** 1.4
            near = max(0.0, 1 - math.hypot(u - moon[0] / K, (v - moon[1] / K) * 1.3) / 110)
            lvl += 2.0 * near ** 2
            c = fbm(u / 70, v / 16, seed)
            kk = smooth(1 - clouds, 1 - clouds + 0.16, c) * (0.5 + 0.5 * t)
            if kk > 0:
                up = fbm(u / 70, (v - 3) / 16, seed)
                rim = smooth(1 - clouds, 1 - clouds + 0.12, c) - smooth(1 - clouds, 1 - clouds + 0.12, up)
                body = 2.2 + 2.6 * t + 1.8 * near ** 1.5 + 2.6 * max(0.0, rim) * (0.4 + 1.6 * near)
                body += (fbm(u / 14, v / 6, seed + 5) - 0.5) * 0.8
                lvl = lvl * (1 - kk) + body * kk
            cv.put(x, y, NSKY, lvl, lit=0)
            if kk < 0.05 and t < 0.8 and hr(x, y, seed + 99) > 0.9986:
                cv.flat(x, y, (200, 210, 230) if hr(x, y, seed + 3) > 0.6 else (110, 120, 150))
    mx, my = moon
    cv.glow(mx, my, 35, GLOW_MOON, 0.35)
    moonr = [(150, 156, 168), (196, 200, 208), (226, 228, 230), (244, 244, 240)]
    cv.disc(mx, my, 7, 7, moonr, lambda nx, ny: 2.6 - nx * 0.9 - ny * 0.6, lit=0)
    for dx, dy, l in ((2, -2, 0.0), (-3, 1, 0.4), (-1, 3, 0.8), (3, 2, 1.0)):     # mars de la lluna
        cv.put(mx + dx, my + dy, moonr, l, lit=0)
    for x in range(mx - 19, mx + 20):                                             # un núvol prim per davant
        for y in (my + 1, my + 2, my + 3):
            if hr(x // 4, y) > 0.35 and not (y == my + 3 and hr(x, 5) > 0.5):
                cv.flat(x, y, mix(cv.get(x, y), (60, 66, 86), 0.55))


def day_sky(cv, y0, hor, sun, seed=12):
    for y in range(y0, hor + 1):
        t = (y - y0) / max(1, hor - y0)
        for x in range(W):
            u, v = x / K, y / K
            lvl = 1.2 + 5.0 * t ** 1.1 + 1.6 * max(0.0, 1 - math.hypot(u - sun[0] / K, v - sun[1] / K) / 120) ** 2
            c = fbm(u / 80, v / 12, seed)
            kk = smooth(0.55, 0.7, c) * (0.3 + 0.7 * t)
            if kk > 0:
                up = fbm(u / 80, (v - 2) / 12, seed)
                top = max(0.0, smooth(0.55, 0.7, c) - smooth(0.55, 0.7, up))
                body = 3.2 + 1.6 * t - 0.8 * (1 - top) + 2.0 * top
                cv.put(x, y, DCLOUD, lvl * (1 - kk) * 0.85 + body * kk + (fbm(u / 10, v / 5, seed + 4) - 0.5) * 0.6, lit=0)
            else:
                cv.put(x, y, DSKY, lvl, lit=0)


def _wave(x, y, hor, seed, phase):
    d = (y - hor) / K + 1
    dd = min(d, 70)
    sx, sy = 2.5 + dd * 0.3, 0.5 + dd * 0.045
    return vnoise((x / K + phase * sx * 0.6) / sx, ((y - hor) / K) / sy, seed)


def night_sea(cv, hor, y1, moon_x, seed=2, phase=0.0):
    for y in range(hor, y1 + 1):
        d = (y - hor) / K
        for x in range(W):
            lvl = 3.4 - min(2.0, d * 0.045)
            n = _wave(x, y, hor, seed, phase)
            lvl += (n - 0.5) * 1.6 + (1.2 if n > 0.78 else 0)
            m = max(0.0, 1 - abs(x - moon_x) / ((6 + d * 0.9) * K))
            if m > 0:
                lvl += m * 1.2
                if n > 0.62 and hr(x // 2, y, seed) > 0.25:
                    lvl += 3.6 * m
            cv.put(x, y, NSEA, lvl, lit=0)
    for x in range(W):
        cv.put(x, hor, NSEA, 4.0, lit=0)


def day_sea(cv, hor, y1, sun_x, seed=3, phase=0.0):
    for y in range(hor, y1 + 1):
        d = (y - hor) / K
        for x in range(W):
            lvl = 5.4 - min(3.2, d * 0.07)
            n = _wave(x, y, hor, seed, phase)
            lvl += (n - 0.5) * 1.8 + (1.4 if n > 0.8 else 0)
            m = max(0.0, 1 - abs(x - sun_x) / ((10 + d * 1.2) * K))
            if m > 0 and n > 0.6 and hr(x // 2, y, seed) > 0.3:
                lvl += 3.0 * m
            cv.put(x, y, DSEA, lvl, lit=0)
    for x in range(W):
        cv.put(x, hor, DSEA, 6.4, lit=0)


def sky_sea(cv, day, phase=0.0):
    if day:
        day_sky(cv, 0, HOR, SUN)
        day_sea(cv, HOR, RAIL + 5, sun_x=80, phase=phase)
    else:
        night_sky(cv, 0, HOR, MOON)
        night_sea(cv, HOR, RAIL + 5, moon_x=MOON[0], phase=phase)


# ─── La popa: el pal de la llum de popa ────────────────────────────────────

def stern(cv, day):
    for y in range(84, RAIL + 3):
        cv.put(10, y, STEELX, 4.8)
        cv.put(11, y, STEELX, 3.6)
        cv.put(12, y, STEELX, 2.4)
    cv.rect(7, 79, 15, 84, CABX, 3.4)
    cv.hline(7, 15, 79, CABX, 4.6)
    for y in (100, 120):                                                 # brides al pal
        cv.rect(9, y, 13, y + 1, CABX, 3.2)
    if not day:
        cv.disc(11, 76, 3, 3, LAMP, 3.2, lit=0)
        cv.glow(11, 76, 13, (255, 248, 224), 0.6)
    else:
        cv.disc(11, 76, 3, 3, CABX, lambda nx, ny: 5.4 - nx - ny)


# ─── La grua i la zòdiac ───────────────────────────────────────────────────

def crane(cv, day):
    # el peu: cilindre groc amb brida i reblons
    for y in range(59, FLOOR_Y + 8):
        for x in range(37, 60):
            u = (x - 48) / 11.5
            lvl = 2.4 - u * 1.3 - u * u * 0.8 - (0.6 if y > FLOOR_Y - 8 else 0)
            if y in (120, 121) or y in (170, 171):                       # soldadures de les virolles
                lvl += 0.8 if y % 2 == 0 else -0.8
            cv.put(x, y, YELL, lvl)
    for y in range(FLOOR_Y - 20, FLOOR_Y - 8):                            # franges de perill al peu
        for x in range(37, 60):
            if ((x + y) // 4) % 2:
                u = (x - 48) / 11.5
                cv.put(x, y, CABX, 2.2 - u * 1.2)
    for i in range(6):                                                   # degotalls de rovell
        rx = 39 + int(hr(i, 70) * 18)
        for y in range(122, 122 + 4 + int(hr(i, 71) * 14)):
            cv.flat(rx, y, mix(cv.get(rx, y), RUST_[3], 0.3))
    cv.rect(32, FLOOR_Y + 4, 64, FLOOR_Y + 9, STEELX, 2.6)
    cv.hline(32, 64, FLOOR_Y + 4, STEELX, 4.0)
    for bx in range(34, 64, 6):
        cv.put(bx, FLOOR_Y + 7, STEELX, 4.8)
        cv.put(bx + 1, FLOOR_Y + 8, STEELX, 1.2)
    cv.rect(33, 67, 63, 73, STEELX, 2.6)                                 # la corona de gir
    cv.hline(33, 63, 67, STEELX, 4.0)
    for x in range(35, 62, 3):
        cv.put(x, 70, STEELX, 1.4)
    # el cap de la grua (la caixa dels motors)
    cv.poly([(32, 48), (67, 48), (69, 67), (32, 67)], YELL, lambda x, y: 3.0 - (y - 48) * 0.045 - (x - 32) * 0.015)
    cv.hline(32, 67, 48, YELL, 4.4)
    cv.rect(35, 52, 47, 60, HULLN, 5.4)                                  # placa de càrrega
    text(cv, '2T', 38, 54, STEELX, 1.2)
    cv.rect(50, 59, 64, 64, STEELX, 1.6)                                 # reixeta
    for yy in (60, 62):
        cv.hline(51, 63, yy, STEELX, 3.0)
    # el braç: biga groga de 9 px que puja cap a la dreta
    ax, ay, bx, by = 56, 53, 187, 29

    def along(t):
        return ax + (bx - ax) * t, ay + (by - ay) * t
    n = 300
    for i in range(n + 1):
        x, y = along(i / n)
        for k in range(-4, 5):
            lvl = 3.2 + {-4: 1.4, -3: 0.8, -2: 0.3, 3: -0.5, 4: -1.3}.get(k, 0)
            cv.put(x, y + k, YELL, lvl)
    for t in (0.2, 0.4, 0.6, 0.8):                                       # plaques de reforç
        x, y = along(t)
        cv.rect(x - 1, y - 3, x + 1, y + 3, YELL, 1.8)
        cv.put(x - 1, y - 3, YELL, 4.6)
    x, y = along(0.5)                                                    # el rètol de la càrrega màxima
    for i, ch in enumerate('SWL'):
        text(cv, ch, x - 16 + i * 4, y - 1 + round(-i * 4 * 24 / 131), STEELX, 0.8)
    # el cilindre hidràulic
    for k, lv in ((0, 2.4), (1, 4.2), (2, 3.8), (3, 2.6)):
        cv.line(60 + k, 101, 87 + k, 54, STEELX, lv)
    for k, lv in ((0, 5.0), (1, 6.2)):
        cv.line(75 + k, 77, 88 + k, 54, STEELX, lv)
    cv.disc(62, 102, 3, 3, STEELX, lambda nx, ny: 4.0 - nx - ny)
    cv.disc(88, 54, 2.5, 2.5, STEELX, lambda nx, ny: 4.0 - nx - ny)
    # la politja de la punta i el cable (dos fils)
    cv.disc(185, 32, 4, 4, STEELX, lambda nx, ny: 3.6 - nx - ny)
    cv.put(185, 32, STEELX, 1.0)
    for y in range(36, 59):
        cv.put(185, y, CABX, 3.8)
        cv.put(186, y, CABX, 2.2 if y % 3 else 3.4)
    # el ganxo i les eslingues
    cv.rect(181, 59, 189, 65, STEELX, 3.4)
    cv.hline(181, 189, 59, STEELX, 4.8)
    cv.rect(182, 62, 188, 62, YELL, 3.4)
    for dx, dy in ((0, 66), (0, 67), (1, 68), (2, 68), (3, 67)):
        cv.put(185 + dx, dy, STEELX, 4.4)
    for tx in (93, 179):
        cv.line(186, 68, tx, 83, ROPE, 3.0)
        cv.line(186, 69, tx, 84, ROPE, 1.8)
    if not day:
        cv.rect(61, 61, 75, 65, CABX, 3.0)                               # el focus de la grua
        cv.hline(61, 75, 61, CABX, 4.2)
        cv.rect(63, 66, 73, 67, LAMP, 2.6, lit=0)
        cv.glow(68, 69, 19, GLOW_WARM, 0.4)


def zodiac(cv):
    """La zòdiac penjada: flotadors grisos amb una franja taronja, el motor fora borda a popa (esquerra)."""
    x0, x1 = 80, 187
    cv.poly([(85, 107), (181, 107), (195, 96), (187, 115), (93, 117), (83, 115)], STEELX,
            lambda x, y: 2.2 - (y - 107) * 0.11)
    cv.hline(90, 184, 114, STEELX, 3.2)                                  # la quilla
    TUBE = [(26, 26, 30), (40, 40, 44), (58, 58, 62), (80, 80, 84), (106, 106, 108), (138, 138, 138), (170, 170, 168)]
    for x in range(x0, x1 + 12):
        t = (x - x0) / (x1 + 11 - x0)
        lift = int(8 * smooth(0.75, 1.0, t))
        r = 9 if x < x1 else max(3, 9 - (x - x1))
        cy = 96 - lift
        for y in range(cy - r, cy + r + 1):
            u = (y - cy) / (r + 0.5)
            if 1 <= y - cy <= 3:
                cv.put(x, y, ORANGEB, 2.8 - u)
            else:
                cv.put(x, y, TUBE, 3.2 - u * 1.6 - u * u * 0.9)
        if x in (110, 140, 168):                                         # les juntes dels compartiments
            for y in range(cy - r + 1, cy + r):
                cv.put(x, y, TUBE, 1.8)
    text(cv, 'ARENGA 2', 118, 101, TUBE, 0.6)
    cv.rect(x0 - 1, 87, x0 + 1, 105, STEELX, 2.0)
    for hx in range(101, 172, 19):                                       # manetes
        cv.hline(hx, hx + 7, 88, ROPE, 3.6)
        cv.put(hx, 89, ROPE, 2.6)
        cv.put(hx + 7, 89, ROPE, 2.6)
    for x in range(x0 + 4, x1, 3):                                       # el cap salvavides de la vora
        cv.put(x, 87 + (1 if (x // 6) % 2 else 0), ROPE, 2.8)
    # el motor fora borda
    MOT = [(8, 8, 10), (18, 18, 22), (30, 30, 36), (46, 46, 54), (68, 68, 76), (96, 96, 104)]
    cv.poly([(64, 77), (80, 77), (81, 93), (63, 93)], MOT, lambda x, y: 3.2 - (x - 64) * 0.08 - (y - 77) * 0.06)
    cv.hline(64, 79, 77, MOT, 4.6)
    cv.hline(63, 81, 87, MOT, 1.2)
    cv.rect(69, 93, 73, 123, MOT[:4], 1.8)
    cv.vline(69, 93, 123, MOT, 3.2)
    cv.rect(67, 123, 76, 126, MOT[:4], 1.4)
    cv.rect(67, 82, 72, 84, ORANGEB, 3.0)
    cv.disc(73, 120, 3, 1.5, MOT, 2.6)                                    # l'hèlice, de cantó
    # les trinques: caps de la zòdiac a la regala, amb el nus
    for zx, rx in ((112, 123), (163, 155)):
        cv.line(zx, 112, rx, RAIL, ROPE, 3.0)
        cv.line(zx + 1, 112, rx + 1, RAIL, ROPE, 2.0)
    cv.disc(155, RAIL - 3, 2.5, 2.5, ROPE, lambda nx, ny: 3.8 - nx - ny)  # el nus (amb una volta de més)
    cv.disc(159, RAIL - 6, 2.5, 2.5, ROPE, lambda nx, ny: 3.4 - nx - ny)
    cv.line(157, RAIL - 1, 160, RAIL + 5, ROPE, 2.6)                       # el xicot que penja


# ─── La caseta, la porta i el pas lateral ──────────────────────────────────

def rrect_frame(cv, x0, y0, x1, y1, r, ramp, lvl, t=4):
    for k in range(t):
        for y in range(y0 - k, y1 + 1):
            for x in range(x0 - k, x1 + k + 1):
                dx = max(x0 - k + r - x, 0, x - (x1 + k - r))
                dy = max(y0 - k + r - y, 0)
                inside = dx * dx + dy * dy <= r * r
                ddx = max(x0 - k + 1 + r - x, 0, x - (x1 + k - 1 - r))
                ddy = max(y0 - k + 1 + r - y, 0)
                inner = x0 - k + 1 <= x <= x1 + k - 1 and y >= y0 - k + 1 and ddx * ddx + ddy * ddy <= r * r
                if inside and not inner:
                    cv.put(x, y, ramp, lvl - k * 0.7 + (0.6 if y < y0 + r else 0))


def wt_door(cv, x0, y0, x1, y1, ramp=HULLN, base=3.4, warm=True):
    """Porta estanca tancada: fulla de cantons rodons, ull de bou, sis palanques, frontisses i el llindar alt."""
    r = 11
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            dx = max(x0 + r - x, 0, x - (x1 - r))
            dy = max(y0 + r - y, 0)
            if dx * dx + dy * dy <= r * r:
                lvl = base - 0.5 + (0.5 if x < x0 + 4 else -0.6 if x > x1 - 4 else 0) + (hr(x // 3, y // 4) - 0.5) * 0.2
                cv.put(x, y, ramp, lvl)
    for yy in (y0 + 40, y0 + 75):                                        # costelles de la fulla
        cv.hline(x0 + 5, x1 - 5, yy, ramp, base + 0.8)
        cv.hline(x0 + 5, x1 - 5, yy + 1, ramp, base - 1.2)
    rrect_frame(cv, x0, y0, x1, y1, r, ramp, base + 1.0)
    for dy in (19, (y1 - y0) // 2, y1 - y0 - 24):                        # palanques («dogs»)
        for xx, d in ((x0 + 1, 1), (x1 - 5, -1)):
            cv.rect(xx, y0 + dy, xx + 4, y0 + dy + 3, CABX, 3.6)
            cv.hline(xx, xx + 4, y0 + dy, CABX, 4.6)
            cv.put(xx + (4 if d > 0 else 0), y0 + dy + 4, CABX, 2.4)
    for hy in (y0 + 14, y1 - 22):                                        # frontisses, a l'esquerra
        cv.rect(x0 - 5, hy, x0 - 1, hy + 7, CABX, 3.2)
        cv.vline(x0 - 3, hy - 1, hy + 8, CABX, 4.4)
    mx, my = (x0 + x1) // 2, y0 + (y1 - y0) // 2                          # maneta central
    cv.rect(mx + 8, my - 3, mx + 16, my, CABX, 3.4)
    cv.hline(mx + 8, mx + 16, my - 3, CABX, 4.6)
    cv.disc(mx + 8, my - 1, 2, 2, CABX, 2.6)
    cx, cy = mx, y0 + 24                                                  # l'ull de bou
    cv.disc(cx, cy, 9, 9, CABX, lambda nx, ny: 3.8 - nx - ny)
    for a in range(0, 360, 60):
        cv.put(cx + round(math.cos(math.radians(a)) * 8), cy + round(math.sin(math.radians(a)) * 8), CABX, 5.0)
    if warm:
        cv.disc(cx, cy, 6.5, 6.5, WINDOW, lambda nx, ny: 2.6 - ny * 0.8 + (0.8 if nx < -0.2 and ny < -0.2 else 0), lit=0)
        cv.glow(cx, cy, 19, GLOW_WARM, 0.25)
    else:
        cv.disc(cx, cy, 6.5, 6.5, STEELX, lambda nx, ny: 1.6 - ny * 0.6, lit=0.5)
    cv.put(cx - 3, cy - 3, [(255, 250, 230)], 0, lit=0)
    cv.put(cx - 2, cy - 3, [(255, 250, 230)], 0, lit=0)
    cv.rect(x0 - 3, y1 - 7, x1 + 3, y1, ramp, base - 0.6)                # el llindar alt
    cv.hline(x0 - 3, x1 + 3, y1 - 7, ramp, base + 1.4)
    for x in range(x0, x1, 9):
        cv.put(x, y1 - 4, ramp, base + 1.0)


def deck_lamp(cv, x, y, on=True):
    cv.rect(x - 8, y - 5, x + 8, y, CABX, 3.0)
    cv.hline(x - 8, x + 8, y - 5, CABX, 4.4)
    cv.vline(x + 8, y - 5, y, CABX, 1.8)
    cv.rect(x - 3, y - 9, x + 3, y - 6, CABX, 2.2)
    for gx in range(x - 6, x + 7, 3):                                    # la reixeta
        cv.put(gx, y + 1, CABX, 1.8)
    if on:
        cv.rect(x - 7, y + 1, x + 7, y + 2, LAMP, 2.6, lit=0)
        for gx in range(x - 6, x + 7, 3):
            cv.put(gx, y + 1, CABX, 1.8, lit=0)
        cv.glow(x, y + 4, 21, GLOW_WARM, 0.45)
        cv.glow(x, y + 4, 8, (255, 240, 200), 0.6)
    else:
        cv.rect(x - 7, y + 1, x + 7, y + 2, CABX, 4.0)


def house(cv, day):
    x0, x1 = HOUSE
    for y in range(29, FLOOR_Y):
        for x in range(x0, x1 + 1):
            lvl = 3.0 + (hr(x // 3, y // 5, 61) - 0.5) * 0.25 - (0.7 if y > FLOOR_Y - 13 else 0)
            if x <= x0 + 2:
                lvl -= 1.2
            cv.put(x, y, HULLN, lvl)
    for sy in (64, 149):                                                 # juntes de planxa amb reblons
        cv.hline(x0 + 3, x1, sy, HULLN, 1.8)
        cv.hline(x0 + 3, x1, sy + 1, HULLN, 4.2)
        for bx in range(x0 + 7, x1, 11):
            cv.put(bx, sy + 3, HULLN, 4.8)
            cv.put(bx + 1, sy + 4, HULLN, 1.8)
    cv.hline(x0, x1, FLOOR_Y - 13, HULLN, 1.4)
    for i in range(14):                                                  # ratlles de rovell
        rx = x0 + 5 + int(hr(i, 62) * (x1 - x0 - 10))
        if DOOR[0] - 6 <= rx <= DOOR[2] + 6:
            continue
        for y in range(67, 67 + 5 + int(hr(i, 63) * 20)):
            cv.flat(rx, y, mix(cv.get(rx, y), (120, 70, 40), 0.3 * (1 - (y - 67) / 30)))
    cv.vline(x1, 29, FLOOR_Y - 1, HULLN, 4.6)                             # aresta de la cantonada
    cv.vline(x1 + 1, 29, FLOOR_Y - 1, HULLN, 1.4)
    wt_door(cv, *DOOR)
    cv.rect(536, 82, 576, 90, HULLN, 1.6)                                # rètol
    cv.hline(536, 576, 82, HULLN, 2.8)
    text(cv, 'MENJADOR', 541, 84, HULLN, 5.6)
    deck_lamp(cv, 556, 75, on=not day)
    cv.disc(512, 53, 8, 8, CABX, lambda nx, ny: 3.8 - nx - ny)           # un ull de bou de la caseta
    if day:
        cv.disc(512, 53, 5.5, 5.5, STEELX, lambda nx, ny: 3.4 - ny + (1.6 if nx < -0.2 and ny < -0.2 else 0))
    else:
        cv.disc(512, 53, 5.5, 5.5, WINDOW, lambda nx, ny: 2.4 - ny * 0.6, lit=0)
        cv.glow(512, 53, 16, GLOW_WARM, 0.2)
    lifebuoy(cv, 509, 112, 12)                                           # el salvavides
    cv.rect(500, 157, 520, 181, [(40, 10, 10), (80, 18, 16), (130, 30, 26), (170, 48, 38), (206, 78, 56)], 2.4)
    cv.hline(500, 520, 157, REDP, 4.4)
    cv.rect(504, 162, 516, 176, [(40, 10, 10), (80, 18, 16), (130, 30, 26)], 1.2)
    cv.ring(510, 169, 4, [(40, 10, 10), (80, 18, 16), (130, 30, 26), (170, 48, 38)], 3.0, step=20)  # la mànega
    cv.rect(514, 166, 515, 170, CABX, 4.4)                                # la tanca
    for y in range(35, FLOOR_Y):                                         # respirador a la cantonada
        cv.put(595, y, HULLN, 4.4)
        cv.put(596, y, HULLN, 3.2)
        cv.put(597, y, HULLN, 2.0)
    for y in (53, 120, 173):
        cv.rect(593, y, 599, y + 1, CABX, 3.0)


def boat_deck(cv, day):
    x0 = HOUSE[0] - 8
    cv.rect(x0, 19, W - 1, 29, HULLN, lambda x, y: 3.6 - (y - 19) * 0.2)
    cv.hline(x0, W - 1, 19, HULLN, 5.0)
    cv.hline(x0, W - 1, 29, HULLN, 1.0)
    cv.rect(x0, 24, W - 1, 25, REDP, 2.6)
    for x in range(x0 + 6, W, 12):                                       # reblons del cantell
        cv.put(x, 21, HULLN, 5.4)
    for sx in range(x0 + 3, W, 19):                                      # barana
        cv.vline(sx, 0, 18, HULLN, 4.4)
        cv.vline(sx + 1, 0, 18, HULLN, 2.6)
    for ry in (3, 11):
        cv.hline(x0, W - 1, ry, HULLN, 4.6)
        cv.hline(x0, W - 1, ry + 1, HULLN, 2.4)


def side_passage(cv, day):
    x0 = HOUSE[1] + 3
    for y in range(31, 40):
        for x in range(x0, W):
            cv.put(x, y, HULLN, 1.4 - (y - 31) * 0.05)
    for y in range(29, FLOOR_Y + 3):                                     # el puntal de la coberta de botes
        cv.put(632, y, HULLN, 4.0)
        cv.put(633, y, HULLN, 2.8)
        cv.put(634, y, HULLN, 1.4)
    deck_lamp(cv, 619, 40, on=not day)
    cv.darken(x0, 31, W - 1, FLOOR_Y + 40, lambda x, y: 0.8 if y < FLOOR_Y else 0.6 - (y - FLOOR_Y) / 67, dither=False)


# ─── Coberta i borda ────────────────────────────────────────────────────────

def bulwark(cv, x0, x1, ytop, ybot, base=2.8, scuppers=(), seed=5):
    for y in range(ytop + 7, ybot):
        for x in range(x0, x1 + 1):
            cv.put(x, y, HULLN, base + (hr(x // 4, y // 6, seed) - 0.5) * 0.25 - (y - ytop) * 0.006)
    for sx in range(10, x1, 35):                                         # cartel·les (reforços)
        if sx < x0 + 2 or sx > x1 - 5:
            continue
        for y in range(ytop + 7, ybot):
            w = 2 + (y - ytop - 7) * 5 // (ybot - ytop - 7)
            for dx in range(w):
                cv.put(sx + dx, y, HULLN, base + (0.9 if dx == 0 else -0.6 if dx == w - 1 else 0.2))
        cv.put(sx + 1, ytop + 10, HULLN, base + 2.0)                     # reblons
    for sx in scuppers:                                                  # escopidors
        for y in range(ybot - 9, ybot):
            for x in range(sx, sx + 19):
                cv.put(x, y, NSEA if cv.light(x, y) < 3 else DSEA, 1.6 + hr(x, y, 3) * 1.4, lit=0.4)
        cv.hline(sx - 1, sx + 19, ybot - 10, HULLN, base + 1.2)
        cv.vline(sx - 1, ybot - 9, ybot - 1, HULLN, base - 1.0)
        for i in range(10):
            rx = sx + int(hr(sx, i) * 19)
            for y in range(ybot - 12 - int(hr(i, sx) * 8), ybot - 9):
                cv.flat(rx, y, mix(cv.get(rx, y), RUST_[2], 0.35))
    cv.rect(x0, ytop, x1, ytop + 6, REDH, lambda x, y: 3.4 + {0: 1.4, 1: 1.0, 2: 0.4, 5: -0.4, 6: -0.9}.get(y - ytop, 0))
    for x in range(x0 + 3, x1, 7):                                       # pintura saltada a la regala
        if hr(x, 9, seed) > 0.8:
            cv.put(x, ytop + 1, REDH, 1.4)
            cv.put(x + 1, ytop + 1, REDH, 2.0)
    cv.hline(x0, x1, ytop + 7, HULLN, base - 1.6)
    for i in range(int((x1 - x0) / 9)):                                  # rovell sota la regala
        rx = x0 + int(hr(i, seed, 7) * (x1 - x0))
        n = 4 + int(hr(i, seed, 8) * 16)
        for y in range(ytop + 8, ytop + 8 + n):
            kk = 0.4 * (1 - (y - ytop - 8) / n)
            if kk > B4[y & 3][rx & 3] * 0.5:
                cv.flat(rx, y, mix(cv.get(rx, y), RUST_[3], kk))


VP = (320, 53)


def deck_floor(cv, y0, y1, base=2.4):
    for y in range(y0, y1 + 1):
        d = y - VP[1]
        for x in range(W):
            u = VP[0] + (x - VP[0]) * 200 / d
            u2 = VP[0] + (x + 1 - VP[0]) * 200 / d
            lvl = base + (hr(x, y, 41) - 0.5) * 0.7
            if int(u // 120) != int(u2 // 120):
                lvl -= 1.3
            elif y in (217, 241):
                lvl -= 1.2
            elif y in (218, 242):
                lvl += 0.6
            elif (x + (y // 2) * 2) % 4 == 0 and y % 2 == 0 and y > y0 + 8:
                lvl += 0.35                                             # l'antilliscant, en relleu
            if y < y0 + 7:
                lvl -= 1.0 - (y - y0) * 0.11
            if 224 <= y <= 253 and fbm(x / 40, y / 8, 43) > 0.55:
                lvl += 0.5
            cv.put(x, y, DECKX, lvl)
            if hr(x // 2, y, 44) > 0.997:
                cv.put(x, y, [(30, 22, 16), (52, 36, 24), (74, 50, 32)], 0.6 + base * 0.2)


def bitts(cv, x, ybase, base=2.6):
    cv.rect(x - 3, ybase - 3, x + 29, ybase + 1, HULLN, base - 1.4)
    cv.hline(x - 3, x + 29, ybase - 3, HULLN, base)
    for bx in (x + 2, x + 19):
        for yy in range(ybase - 24, ybase - 2):
            for dx in range(8):
                u = (dx - 3.5) / 4
                cv.put(bx + dx, yy, STEELX, base + 1.6 - u * 1.4 - u * u)
        cv.disc(bx + 3.5, ybase - 24, 4.5, 1.6, STEELX, base + 2.6)
        cv.hline(bx, bx + 7, ybase - 18, STEELX, base + 0.2)            # el collar
    for i in range(3):                                                   # una volta de cap a les bites
        cv.line(x + 4, ybase - 12 - i * 3, x + 23, ybase - 15 - i * 3, ROPE, 3.0 - i * 0.2)


def coil(cv, cx, cy, rx, ry):
    cv.disc(cx, cy + 1, rx + 1, ry + 1, DECKX, 0.6)
    for k in range(7):
        r1, r2 = rx - k * 2.2, ry - k * 0.7
        for a in range(0, 360, 2):
            x = cx + math.cos(math.radians(a)) * r1
            y = cy - 1 - k * 0.5 + math.sin(math.radians(a)) * r2
            cv.put(round(x), round(y), ROPE, 3.0 - math.sin(math.radians(a)) * 0.9 + (0.6 if k % 2 else 0))
    cv.disc(cx, cy - 4, 4, 1.4, DECKX, 1.0)
    cv.line(cx + rx - 1, cy, cx + rx + 9, cy + 4, ROPE, 2.8)
    cv.line(cx + rx + 9, cy + 4, cx + rx + 12, cy + 3, ROPE, 3.2)


def deck_things(cv, day):
    bitts(cv, 339, FLOOR_Y + 3)
    coil(cv, 109, 227, 19, 5)
    WOODB = [(30, 18, 10), (56, 36, 20), (88, 60, 34), (124, 88, 52), (160, 120, 74), (190, 152, 100)]
    cv.rect(400, 176, 453, 205, WOODB, 2.4)                              # caixa de cordes
    cv.hline(400, 453, 176, WOODB, 4.0)
    for yy in (185, 195):
        cv.hline(401, 452, yy, WOODB, 1.0)
    for x in (403, 450):
        cv.vline(x, 177, 204, WOODB, 1.6)
    cv.rect(421, 181, 432, 186, STEELX, 3.6)
    cv.hline(421, 432, 181, STEELX, 5.0)
    BLUE = [(20, 40, 70), (30, 60, 110), (50, 90, 150), (80, 130, 190)]
    for y in range(187, 206):                                            # la galleda
        for x in range(283, 297):
            u = (x - 289.5) / 7.5
            cv.put(x, y, BLUE, 1.8 - u * 0.9 - u * u * 0.4)
    cv.hline(282, 298, 187, BLUE, 2.4)
    cv.hline(283, 296, 194, BLUE, 1.2)
    cv.line(283, 186, 290, 179, STEELX, 3.0)
    cv.line(290, 179, 297, 186, STEELX, 3.0)


def draw(cv, day, phase=0.0):
    sky_sea(cv, day, phase)
    stern(cv, day)
    bulwark(cv, 0, W - 1, RAIL, FLOOR_Y, base=2.6 if not day else 2.8, scuppers=(200, 373, 608))
    deck_floor(cv, FLOOR_Y, H - 1)
    deck_things(cv, day)
    zodiac(cv)
    crane(cv, day)
    house(cv, day)
    boat_deck(cv, day)
    side_passage(cv, day)
    if not day:
        cv.glow(556, 229, 61, GLOW_WARM, 0.10)
        cv.glow(80, 224, 53, GLOW_WARM, 0.08)
    else:
        cv.darken(HOUSE[0] - 40, FLOOR_Y, HOUSE[1], FLOOR_Y + 11, lambda x, y: 0.5 if x > HOUSE[0] - 40 + (y - FLOOR_Y) * 4 else 0)
        cv.darken(59, FLOOR_Y + 3, 107, FLOOR_Y + 12, 0.4)


def bg(cv):
    draw(cv, False)


def dia(cv):
    keep = cv.light
    cv.light = LIGHT_DAY
    draw(cv, True)
    cv.light = keep


# ─── Props ──────────────────────────────────────────────────────────────────

GULLS = ((320, 40, 35, 9, 0.0), (331, 35, 24, 7, 2.1), (315, 45, 45, 12, 4.0), (336, 43, 29, 8, 5.2))


def gull(cv, x, y, wing=1, col=(226, 228, 224)):
    """Gavina llunyana, una mica més gran que a 480: cos, ales amb la punta fosca."""
    dark = mix(col, (90, 90, 96), 0.55)
    cv.flat(x, y, col)
    cv.flat(x, y + 1, mix(col, (150, 150, 150), 0.4))
    for s in (-1, 1):
        cv.flat(x + s, y - wing, col)
        cv.flat(x + 2 * s, y - wing, col)
        cv.flat(x + 3 * s, y - (wing if wing <= 0 else wing - 1) + (1 if wing < 0 else 0), dark)


def _stain(cv, cx, ywl, rx, ry, k=1.0, seed=21):
    for X, Y, x, y in cv.pixels(int(cx - rx), int(ywl - ry), int(cx + rx), int(ywl + ry)):
        nx, ny = (x - cx) / rx, (y - ywl) / ry
        d = nx * nx + ny * ny + (fbm(x / K / 9, y / K / 2, seed) - 0.5) * 0.9
        a = k * smooth(0.0, 0.45, 1 - d)
        if a > B4[Y & 3][X & 3] * 0.9 and Y // cv.S > HOR:
            cv.P[X, Y] = TURBID[3 if hr(X // cv.S // 5, Y // cv.S) > 0.3 else 4] + (int(min(0.6, a) * 255),)


def plataforma(cv, t=0.0):
    keep = cv.light
    cv.light = LIGHT_DAY
    _stain(cv, 320, HOR + 7, 120, 9)
    platform(cv, 320, HOR + 4, 1.9 * K, 'day')
    for i, (gx, gy, rx, ry, ph) in enumerate(GULLS):
        a = ph + t * 2 * math.pi * (1 if i % 2 else -1)
        wing = (1, 2, 1, 0, -1, 0)[int(t * 24 + i * 2) % 6] if i != 2 else 1
        gull(cv, round(gx + math.cos(a) * rx), round(gy + math.sin(a) * ry), wing)
    cv.light = keep


def taula(cv):
    keep = cv.light
    cv.light = LIGHT_DAY
    x0, x1, top = 408, 504, 181
    TOPR = [(60, 60, 58), (96, 94, 90), (134, 132, 124), (170, 166, 156), (200, 196, 184), (226, 222, 210)]
    for lx in (x0 + 8, x1 - 8):                                          # potes plegables (en X)
        cv.line(lx - 5, top + 5, lx + 5, 235, STEELX, 3.6)
        cv.line(lx + 5, top + 5, lx - 5, 235, STEELX, 2.4)
        cv.disc(lx, (top + 240) // 2, 1.2, 1.2, STEELX, 5.0)
        cv.rect(lx - 8, 235, lx + 8, 236, STEELX, 1.6)
    cv.rect(x0, top, x1, top + 4, TOPR, lambda x, y: 3.4 - (y - top) * 0.4)
    cv.hline(x0, x1, top, TOPR, 4.8)
    cv.rect(x0, top + 5, x1, top + 6, TOPR, 1.2)
    TERMO = [(10, 30, 40), (20, 60, 76), (34, 96, 116), (60, 140, 160), (120, 190, 200)]
    for y in range(top - 21, top):                                       # el termo
        for x in range(421, 432):
            u = (x - 426) / 5.5
            cv.put(x, y, TERMO, 2.4 - u * 1.2 - u * u * 0.6)
    cv.rect(421, top - 25, 431, top - 22, STEELX, 4.4)
    cv.rect(424, top - 27, 428, top - 26, STEELX, 3.0)
    cv.rect(421, top - 12, 431, top - 10, STEELX, 3.6)
    GREEN = [(20, 50, 30), (40, 90, 50), (70, 130, 80), (110, 170, 120)]
    for mx, c, l in ((443, ORANGEB, 2.6), (459, HULLN, 6.0), (488, GREEN, 2.6)):    # tasses
        cv.rect(mx, top - 8, mx + 7, top - 1, c, l)
        cv.vline(mx, top - 8, top - 1, c, l + 0.8)
        cv.ring(mx + 9, top - 4, 2, c, l - 0.6, step=40)
        cv.hline(mx + 1, mx + 6, top - 8, [(30, 16, 8), (60, 34, 16)], 0.8)
    cv.disc(473, top - 1, 12, 3, HULLN, 6.6)                             # el plat dels croissants
    BREAD = [(70, 36, 12), (120, 70, 26), (176, 116, 50), (216, 160, 84), (240, 200, 130)]
    for cx, cy in ((467, top - 5), (479, top - 5), (473, top - 8)):
        cv.disc(cx, cy, 5.5, 2.5, BREAD, lambda nx, ny: 2.8 - ny * 1.2 - nx * 0.4)
        cv.put(cx - 2, cy - 1, BREAD, 4.2)
        cv.put(cx + 1, cy, BREAD, 1.4)
    cv.rect(495, top - 3, 503, top - 1, [(20, 20, 26), (40, 40, 50), (60, 60, 74)], 1.8)   # uns guants
    cv.light = keep


def horitzo(cv):
    """L'estela: una franja d'escuma que surt de sota la popa i s'aprima cap a l'horitzó."""
    for x in range(200, 459):
        t = (x - 200) / 259
        yc = RAIL - 7 - t * (RAIL - HOR - 12)
        hw = (4.5 * (1 - t) + 0.8) * K
        for y in range(int(yc - hw - 2), int(yc + hw + 3)):
            if not (HOR + 1 <= y < RAIL):
                continue
            d = abs(y - yc) / hw
            n = fbm(x / K / 10, y / K / 2.2, 77)
            kk = (1 - t) ** 0.7 * (1 - d) + (n - 0.5) * 0.8
            if kk > 0.12 + (hr(x, y, 78) - 0.5) * 0.2:
                cv.flat(x, y, mix(cv.get(x, y), (210, 220, 222), min(0.7, kk * 0.9)))
    for x in range(200, 440):
        t = (x - 200) / 240
        for sgn in (-1, 1):
            y = round(RAIL - 7 - t * (RAIL - HOR - 12) + sgn * (7 + 8 * (1 - t)) * (1 - t * 0.5))
            if HOR + 1 <= y < RAIL and hr(x // 2, y, 79) > 0.3 + t * 0.5:
                cv.flat(x, y, mix(cv.get(x, y), (190, 200, 204), 0.5 * (1 - t)))


PROPS = {'dia': dia, 'plataforma': plataforma, 'taula': taula, 'horitzo': horitzo}


# ─── Animacions ────────────────────────────────────────────────────────────

SEA_N, SEA_FADE, SEA_STEP = 12, 4, 0.32


def _sea_frames(base, sea):
    ref = Canvas(light=LIGHT)
    sea(ref, 0.0)
    rp, bp = ref.img.load(), base.load()
    S = base.width // W                                               # (en píxels reals: art a 2×)
    open_ = [(X, Y) for Y in range((HOR + 1) * S, (RAIL + 6) * S) for X in range(base.width) if bp[X, Y] == rp[X, Y]]
    frames = []
    for i in range(SEA_N):
        a, b = Canvas(light=LIGHT), Canvas(light=LIGHT)
        sea(a, i * SEA_STEP)
        sea(b, (i - SEA_N) * SEA_STEP)
        w = max(0, i - (SEA_N - SEA_FADE)) / SEA_FADE
        out = base.copy()
        o, ap, bpp = out.load(), a.img.load(), b.img.load()
        for X, Y in open_:
            o[X, Y] = bpp[X, Y] if hr(X // S, Y // S, 90) < w else ap[X, Y]
        frames.append(_diff(out, base))
    return frames


def _frames_mar():
    base = Canvas(light=LIGHT)
    bg(base)
    return _sea_frames(base.img, lambda cv, ph: night_sea(cv, HOR, RAIL + 5, moon_x=MOON[0], phase=ph))


def _frames_dia_mar():
    base = Canvas(light=LIGHT)
    dia(base)
    return _sea_frames(base.img, lambda cv, ph: day_sea(cv, HOR, RAIL + 5, sun_x=80, phase=ph))


def _frames_plataforma():
    frames = []
    for i in range(16):
        cv = Canvas(light=LIGHT, transparent=True)
        plataforma(cv, i / 16)
        frames.append(cv.img)
    return frames


ANIMS = {'mar': {'frames': _frames_mar, 'frameDuration': 260},
         'dia_mar': {'frames': _frames_dia_mar, 'frameDuration': 260},
         'plataforma': {'frames': _frames_plataforma, 'frameDuration': 180}}

FRONT = {'mask': lambda x, y: False, 'baseline': 235, 'zIndex': 20, 'props': ('taula',)}


def _s(*v):
    return tuple(round(c * K) for c in v)


GEOMETRIA = {
    'things': {
        'porta': {'rect': _s(394, 66, 440, 152), 'walk': _s(417, 168)},
        'proa': {'rect': _s(452, 24, 479, 168), 'walk': _s(468, 174)},
        'grua': {'rect': _s(22, 20, 148, 158), 'walk': _s(96, 174)},
        'borda': {'rect': _s(150, 104, 300, 154), 'walk': _s(226, 168)},
        'plataforma': {'rect': _s(204, 26, 278, 92), 'walk': _s(240, 168)},
        'taula': {'rect': _s(304, 118, 380, 178), 'walk': _s(342, 188)},
        'horitzo': {'rect': _s(150, 88, 340, 105), 'walk': _s(240, 168)},
    },
    'spawns': {cid: _s(*p) for cid, p in {
        'iri': (232, 190), 'vet': (150, 192), 'bastida': (190, 168),
        'capitana': (326, 168), 'tomas': (362, 168), 'nadia': (288, 186), 'marcel': (398, 190)}.items()},
    'walkable': [_s(*p) for p in [(56, 160), (440, 160), (460, 160), (479, 164), (479, 196), (0, 196), (0, 172), (20, 164)]],
}
