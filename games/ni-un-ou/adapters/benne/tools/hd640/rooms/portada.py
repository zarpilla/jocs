"""
Prova a 640×360: la portada (vegeu hd/rooms/portada.py, la de 480×270). Pantalla sencera, sense barra de verbs.
  - el títol «NI UN OU» en lletres de píxel grosses (cel·les de 10 px en lloc de 6): escuma blanca a dalt,
    fang gris verdós a baix, amb bombolles i un bisell a cada cel·la, i regalims de fang;
  - l'Arenga de perfil a l'esquerra, la plataforma al fons a la dreta amb el llum vermell;
  - la lluna entre núvols i el seu camí al mar.
Els botons de la GUI `portada` van a 220..420 × 224..328 (×4/3 de 165..315 × 168..246): allà només hi ha mar.
Aquí hi ha també el cel i el mar de nit de les cinemàtiques (night_sky, night_sea), que fan servir els crèdits i
el pròleg: es calculen a 640 amb la mida de núvols i onades de 480 (no s'amplien).
"""
import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

import math

from hd.pix import Light, Canvas, W, H, hr, mix
from hd.rooms.comu import _diff
from hd.rooms.exterior import vnoise, fbm, smooth, arenga, platform, reflection, NSKY, NSEA, GLOW_MOON
from room_designs import LLETRES

K = 4 / 3
HOR = 171
TITLE_Y = 21
S = 10                                    # mida del «píxel» de les lletres
SHIP = (104, 203, 4.0 * K)              # popa a x=104: sencer, i el camí de la lluna li queda a l'esquerra
PLAT = (539, HOR + 3, 2.2 * K)
MOON = (46, 100)
N = 8                                     # fotogrames del bucle
BOB = (0, 0, 0, 1, 1, 1, 1, 0)           # el vaixell puja i baixa un píxel amb l'onada

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)

FOAM = [(16, 30, 40), (40, 70, 84), (90, 130, 140), (150, 190, 196), (206, 230, 230), (240, 250, 248)]
MUD = [(20, 22, 16), (40, 42, 30), (62, 64, 44), (86, 86, 58), (110, 106, 72), (136, 128, 90), (160, 152, 112)]
EDGE = [(4, 8, 14)]


# ─── Cel i mar de nit (també per als crèdits i el pròleg) ───────────────────

def night_sky(cv, y0, hor, moon=None, seed=1, clouds=0.5, stars=True):
    """Com exterior.night_sky, però calculat a 640 amb la mida de núvols de 480; la lluna, amb taques."""
    for y in range(y0, hor + 1):
        t = (y - y0) / max(1, hor - y0)
        for x in range(W):
            u, v = x / K, y / K
            lvl = 1.0 + 3.0 * t ** 1.4
            near = 0.0
            if moon:
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
            if stars and kk < 0.05 and t < 0.8 and hr(x, y, seed + 99) > 0.9986:
                bright = hr(x, y, seed + 3) > 0.6
                cv.flat(x, y, (200, 210, 230) if bright else (110, 120, 150))
                if bright and hr(x, y, seed + 7) > 0.8:                      # alguna estrella amb creu
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        cv.flat(x + dx, y + dy, mix(cv.get(x + dx, y + dy), (150, 160, 190), 0.5))
    if moon:
        mx, my = moon
        cv.glow(mx, my, 35, GLOW_MOON, 0.35)
        moonr = [(150, 156, 168), (196, 200, 208), (226, 228, 230), (244, 244, 240)]
        cv.disc(mx, my, 7, 7, moonr, lambda nx, ny: 2.6 - nx * 0.9 - ny * 0.6, lit=0)
        for dx, dy, l in ((2, -2, 0.0), (-3, 1, 0.4), (-1, 3, 0.8), (3, 2, 1.0)):     # les taques de la lluna
            cv.put(mx + dx, my + dy, moonr, l, lit=0)
        for x in range(mx - 19, mx + 20):                                         # un núvol prim per davant
            for y in (my + 1, my + 2, my + 3):
                if hr(x // 4, y) > 0.35 and not (y == my + 3 and hr(x, 5) > 0.5):
                    cv.flat(x, y, mix(cv.get(x, y), (60, 66, 86), 0.55))


def _wave(x, y, hor, seed, phase):
    d = (y - hor) / K + 1
    dd = min(d, 70)
    sx, sy = 2.5 + dd * 0.3, 0.5 + dd * 0.045
    return vnoise((x / K + phase * sx * 0.6) / sx, ((y - hor) / K) / sy, seed)


def night_sea(cv, hor, y1, moon_x=None, seed=2, phase=0.0, calm=1.0, path=(6, 0.9), twinkle=0):
    """Com exterior.night_sea, calculat a 640: onades, el camí de la lluna; `calm` < 1, mar més plana.
    `path`: amplada del camí de la lluna (a l'horitzó i com s'eixampla); `twinkle`: canvia les guspires."""
    for y in range(hor, y1 + 1):
        d = (y - hor) / K
        for x in range(W):
            lvl = 3.4 - min(2.0, d * 0.045)
            n = _wave(x, y, hor, seed, phase)
            lvl += (n - 0.5) * 1.6 * calm + (1.2 * calm if n > 0.78 else 0)
            if moon_x is not None:
                m = max(0.0, 1 - abs(x - moon_x) / ((path[0] + d * path[1]) * K))
                if m > 0:
                    lvl += m * 1.2
                    if n > 0.62 and hr(x // 2, y, seed + twinkle) > 0.25:
                        lvl += 3.6 * m
            cv.put(x, y, NSEA, lvl, lit=0)
    for x in range(W):
        cv.put(x, hor, NSEA, 4.0, lit=0)


# ─── El títol ──────────────────────────────────────────────────────────────

def title(cv):
    word = 'NI UN OU'
    advance = [3 if ch == ' ' else 6 for ch in word]       # l'espai, mitja lletra: es llegeix com una frase
    width = sum(advance) * S - S
    x0 = (W - width) // 2
    cells = []
    col = 0
    for ch, adv in zip(word, advance):
        for r, bits in enumerate(LLETRES[ch]):
            for c, bit in enumerate(bits):
                if bit == '1':
                    cells.append((x0 + (col + c) * S, TITLE_Y + r * S))
        col += adv
    filled = set(cells)
    # ombra i vora
    for x, y in cells:
        cv.rect(x + 4, y + 5, x + S + 3, y + S + 4, [(2, 3, 8)], 0, lit=0)
    for x, y in cells:
        cv.rect(x - 1, y - 1, x + S, y + S, EDGE, 0, lit=0)
    # el cos: escuma a dalt, fang a baix (la línia de l'aigua bruta fa onades)
    for x, y in cells:
        top_open = (x, y - S) not in filled
        left_open = (x - S, y) not in filled
        right_open = (x + S, y) not in filled
        for py in range(y, y + S):
            for px in range(x, x + S):
                line = TITLE_Y + 4.1 * S + math.sin(px / 12 + 0.6) * 3.2 + math.sin(px / 4.9) * 1.1
                bevel = 0.0
                if py == y and top_open:
                    bevel += 0.9                                  # el cantell de dalt, amb llum
                if px == x and left_open:
                    bevel += 0.4
                if px == x + S - 1 and right_open:
                    bevel -= 0.7                                  # el de la dreta, a l'ombra
                if py < line:
                    t = (py - TITLE_Y) / (4.1 * S)
                    lvl = 5.2 - t * 1.6 + bevel
                    cv.put(px, py, FOAM, lvl, lit=0)
                else:
                    t = (py - line) / (2.9 * S)
                    lvl = 4.6 - t * 1.8 + (hr(px // 2, py // 2, 5) - 0.5) * 0.9 + bevel * 0.6
                    cv.put(px, py, MUD, lvl, lit=0)
                if abs(py - line) < 0.8:
                    cv.flat(px, py, (196, 206, 180))
                elif line - 3 < py < line and hr(px, py, 6) > 0.9:  # bombolles d'escuma just sobre el fang
                    cv.flat(px, py, (226, 236, 222))
                elif line < py < line + 10 and hr(px, py, 8) > 0.96:  # grumolls més foscos al fang
                    cv.put(px, py, MUD, 1.6, lit=0)
    # regalims de fang sota algunes lletres
    bottoms = {}
    for x, y in cells:
        for px in range(x, x + S):
            bottoms[px] = max(bottoms.get(px, 0), y + S)
    for px in sorted(bottoms):
        if hr(px // 4, 77) > 0.86 and hr(px, 78) > 0.3:
            n = 4 + int(hr(px // 4, 79) * 16)
            y0 = bottoms[px]
            for dx in (0, 1, 2):
                if bottoms.get(px + dx) != y0:
                    continue
                for y in range(y0, y0 + n - dx * 3):
                    cv.put(px + dx, y, MUD, 2.4 - (y - y0) * 0.06 + (0.6 if dx == 0 else 0), lit=0)
            cv.disc(px + 1, y0 + n, 1.6, 2.0, MUD, 2.6, lit=0)
            cv.flat(px, y0 + n - 1, (150, 146, 110))
    cv.glow(W // 2, TITLE_Y + round(3.4 * S), 226, (120, 170, 190), 0.05)


# ─── L'escena ──────────────────────────────────────────────────────────────

def bg(cv, frame=0):
    night_sky(cv, 0, HOR, moon=MOON, seed=31, clouds=0.55)
    phase = 1.4 * math.sin(2 * math.pi * frame / N)       # l'onada va i ve: el bucle no salta
    night_sea(cv, HOR, H - 1, moon_x=MOON[0], seed=32, phase=phase, path=(2.5, 0.27), twinkle=frame)
    platform(cv, PLAT[0], PLAT[1], PLAT[2], 'night')
    reflection(cv, PLAT[0] - 67, PLAT[0] + 67, PLAT[1], 40, k=0.45, seed=33 + frame)
    xs, ywl, s = SHIP
    ywl -= BOB[frame % N]
    arenga(cv, xs, ywl, s, 'night', facing=1)
    reflection(cv, xs - 11, xs + 224, ywl, 40, k=0.3, seed=35 + frame)
    if frame % 4 == 3:                                     # el llum vermell de la plataforma, que fa pampallugues
        lx, ly = round(PLAT[0] + 10 * PLAT[2]), round(PLAT[1] - 30 * PLAT[2])
        cv.rect(lx, ly, lx + 1, ly + 1, [(90, 20, 20)], 0, lit=0)
    title(cv)


PROPS = {}


def _frames():
    base = Canvas(light=LIGHT)
    bg(base)
    frames = []
    for i in range(N):
        cv = Canvas(light=LIGHT)
        bg(cv, i)
        frames.append(_diff(cv.img, base.img))
    return frames


ANIMS = {'mar': {'frames': _frames, 'frameDuration': 300}}

GEOMETRIA = {'things': {}, 'spawns': {}}
