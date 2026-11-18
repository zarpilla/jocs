"""
**El dibuix pla de sempre** (font de les textures de la sala en 3D, portada.py).

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
from hd.rooms.exterior import vnoise, fbm, smooth, arenga, platform, reflection, sheer, NSKY, NSEA, GLOW_MOON
from room_designs import LLETRES

from hd.pix import Canvas  # noqa: E402,F811  (a 1×: és la font de les textures de la sala en 3D)
Canvas1x = Canvas

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

def bg(cv, frame=0, watcher=False):
    """L'escena sense el títol (el títol és la capa «titol»; el pròleg fa servir aquest mateix fons).
    `watcher`: la silueta dels prismàtics a la plataforma, amb el focus (per a la capa «vigia» del pròleg)."""
    night_sky(cv, 0, HOR, moon=MOON, seed=31, clouds=0.55)
    phase = 1.4 * math.sin(2 * math.pi * frame / N)       # l'onada va i ve: el bucle no salta
    night_sea(cv, HOR, H - 1, moon_x=MOON[0], seed=32, phase=phase, path=(2.5, 0.27), twinkle=frame)
    platform(cv, PLAT[0], PLAT[1], PLAT[2], 'night', watcher=watcher)
    reflection(cv, PLAT[0] - 67, PLAT[0] + 67, PLAT[1], 40, k=0.45, seed=33 + frame)
    xs, ywl, s = SHIP
    ywl -= BOB[frame % N]
    arenga(cv, xs, ywl, s, 'night', facing=1, zodiac=False)     # la zòdiac és a les animacions «zodiac»
    reflection(cv, xs - 11, xs + 224, ywl, 40, k=0.3, seed=35 + frame)
    if frame % 4 == 3:                                     # el llum vermell de la plataforma, que fa pampallugues
        lx, ly = round(PLAT[0] + 10 * PLAT[2]), round(PLAT[1] - 30 * PLAT[2])
        cv.rect(lx, ly, lx + 1, ly + 1, [(90, 20, 20)], 0, lit=0)


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


def _title_frames():
    cv = Canvas(light=LIGHT, transparent=True)
    title(cv)
    return [cv.img]


# ─── La zòdiac ──────────────────────────────────────────────────────────────
# De fons i sense detall, en capa transparent damunt del mar (que continua sent l'animació «mar»). A la portada,
# penja de la grua amb la Juana a dins («zodiac», en bucle). Al pròleg, cada tros comença amb una frase (vegeu
# rooms/proleg_punt7.json) i es queda a l'últim fotograma: la grua la baixa («z_baixa»), va a poc a poc cap a la
# plataforma («z_travessa») i la Juana treu la mostra a contrallum («z_mostra»).
# Els temps són d'una sola història contínua; cada tros n'és una finestra (CLIPS).

ZT = 0.15                                 # segons per fotograma
Z_LOWER = (0.3, 5.3)
Z_TOUCH = 5.3
Z_HOOK = (5.8, 7.3)
Z_MOTOR = 10.0
Z_MOVE = (10.5, 27.5)
Z_LANTERN = 28.8
Z_DIP = (29.3, 30.5)
Z_SCOOP = (30.5, 31.1)
Z_RAISE = (31.1, 32.6)
Z_WRITE = (40.0, 40.5, 42.2)              # abaixa el pot fins al pit, hi escriu, i el deixa allà
CLIPS = {'z_baixa': (0.0, 10.0), 'z_travessa': (10.0, 28.5), 'z_mostra': (28.5, 40.0), 'z_escriu': (40.0, 43.0)}

ZODR = [(18, 18, 22), (30, 30, 36), (46, 46, 52), (66, 66, 72), (90, 90, 94), (120, 120, 122)]
STRIPE = [(140, 50, 20), (200, 90, 40)]
JACKET = [(50, 16, 10), (96, 34, 16), (150, 62, 28)]
HATC = (40, 90, 50)
SKINC = (150, 96, 70)
WIRE = [(6, 8, 12), (20, 24, 30), (42, 48, 56), (78, 84, 90)]
FOAMC = (110, 130, 145)
LAMPC = (255, 236, 180)
JARC = (206, 200, 172)
WL_HANG, WL_WATER, WL_FAR = 179, 209, 189
ZX0, ZX1 = 106, 468


def _ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def _seg(t, ab):
    return _ease((t - ab[0]) / (ab[1] - ab[0]))


def _zpos(t, bob=0, sway_t=None):
    """→ (x del centre, flotació, escala, a l'aigua?)"""
    if t < Z_TOUCH:
        k = _seg(t, Z_LOWER)
        st = t if sway_t is None else sway_t
        sway = 1.0 * math.sin(st * 2 * math.pi / 2.4) * (1 - k)
        return ZX0 + sway, WL_HANG + (WL_WATER - WL_HANG) * k - bob, 1.0, False
    k = _seg(t, Z_MOVE)
    x = ZX0 + (ZX1 - ZX0) * k
    ky = _ease((k - 0.45) / 0.55)                 # passat el vaixell, s'allunya cap a l'horitzó
    d = t - Z_TOUCH
    wave = 1.6 * math.exp(-d * 2) * math.sin(d * 8) + 0.6 * math.sin(t * 2.4)
    return x, WL_WATER + (WL_FAR - WL_WATER) * ky + wave, 1.0 - 0.38 * ky, True


def _apx(cv, X, Y, col, a):
    """Un píxel real (X, Y) semitransparent, si encara és buit."""
    if 0 <= X < cv.w and 0 <= Y < cv.h and a > 0.03 and not cv.P[X, Y][3]:
        cv.P[X, Y] = tuple(col) + (int(255 * min(1.0, a)),)


def _aput(cv, x, y, col, a):
    """Un píxel de sala (un bloc S×S a l'art a 2×)."""
    x, y = int(x), int(y)
    if 0 <= x < W and 0 <= y < H:
        for dy in range(cv.S):
            for dx in range(cv.S):
                _apx(cv, x * cv.S + dx, y * cv.S + dy, col, a)


def _aglow(cv, cx, cy, r, col, a0):
    for X, Y, x, y in cv.pixels(int(cx - r), int(cy - r), int(cx + r), int(cy + r)):
        d = math.hypot(x - cx, (y - cy) * 1.2) / r
        if d < 1:
            _apx(cv, X, Y, col, a0 * (1 - d) ** 2)


def _ring(cv, cx, cy, r, a, seed):
    for ang in range(0, 360, 3):
        if hr(ang, seed) > 0.4:
            _aput(cv, round(cx + math.cos(math.radians(ang)) * r), round(cy + math.sin(math.radians(ang)) * r * 0.15),
                  FOAMC, a)


def _zodiac(cv, cx, wl, sc, motor, t):
    """La zòdiac, petita: els flotadors amb la franja taronja, el motor i la Juana. → (x0, llargada, x de la Juana, dalt)"""
    L = max(12, round(22 * sc))
    hgt = 3 if sc > 0.8 else 2
    x0 = round(cx - L / 2)
    wl = round(wl)
    for x in range(x0, x0 + L + 1):
        lift = 1 if (x - x0) / L > 0.85 else 0
        for k in range(hgt + 1):
            cv.put(x, wl - k - lift, ZODR, 1.4 + k * 0.9, lit=0)
        if hgt >= 3 and (x - x0) / L < 0.95:
            cv.put(x, wl - 1 - lift, STRIPE, 0.4, lit=0)
    shake = 1 if motor and int(t / ZT) % 2 else 0
    cv.rect(x0 - 2, wl - hgt - 3 - shake, x0, wl - 1, ZODR, 0.8, lit=0)    # el motor
    cv.put(x0 - 1, wl, ZODR, 0.4, lit=0)
    # la Juana: l'anorac vermell, la cara i la gorra verda
    jx = x0 + round(L * 0.45)
    top = wl - hgt - 1
    cv.rect(jx, top - 2, jx + 1, top, JACKET, 1.4, lit=0)
    cv.put(jx, top - 2, JACKET, 2.4, lit=0)
    cv.flat(jx + 1, top - 3, SKINC)
    cv.flat(jx, top - 3, (40, 26, 18))
    cv.flat(jx, top - 4, HATC)
    cv.flat(jx + 1, top - 4, HATC)
    if motor:                                                               # l'aigua remenada per l'hèlix
        for i in range(4):
            if hr(i, int(t / ZT), 5) > 0.4:
                _aput(cv, x0 - 3 - round(hr(i, int(t / ZT), 6) * 4), wl + (i % 2), (160, 180, 190), 0.8)
    return x0, L, jx, top


def _sample(cv, t, jx, top, wl):
    """La mostra: la llanterna, la mà a l'aigua i el pot enlaire a contrallum."""
    if t < Z_LANTERN:
        return
    on = t - Z_LANTERN > 0.3 or int((t - Z_LANTERN) / ZT) % 2
    lx, ly = jx - 1, top - 1
    hand = None
    if t >= Z_DIP[0]:
        if t < Z_DIP[1]:
            k = _seg(t, Z_DIP)
            hand = (jx + 2 + round(2 * k), round(top - 1 + (wl + 1 - (top - 1)) * k))
        elif t < Z_RAISE[0]:
            hand = (jx + 4, wl + 1)
        elif t < Z_WRITE[0]:
            k = _seg(t, Z_RAISE)
            hand = (jx + 4 - round(k), round(wl + 1 + (top - 5 - (wl + 1)) * k))
        else:
            k = _seg(t, Z_WRITE[:2])
            hand = (jx + 3, round(top - 5 + 4 * k))
        cv.line(jx + 2, top - 2, hand[0], hand[1], JACKET, 1.8, lit=0)
        if Z_SCOOP[0] - 0.2 <= t < Z_RAISE[0] + 0.6:                         # l'aigua on hi fica la mà
            _ring(cv, jx + 4, wl + 1, 2 + (t - Z_SCOOP[0] + 0.2) * 4, 0.6, 3)
        if t >= Z_SCOOP[1] and hand[1] < wl:                                 # el pot, pàl·lid, amb el fang
            cv.flat(hand[0], hand[1] - 1, JARC)
            cv.flat(hand[0], hand[1] - 2, JARC)
            cv.flat(hand[0] + 1, hand[1] - 1, (110, 106, 88))
            cv.flat(hand[0] + 1, hand[1] - 2, JARC)
        if Z_WRITE[1] <= t < Z_WRITE[2]:                                      # el retolador, que va i ve
            cv.flat(hand[0] - 1 + int(t / ZT) % 2, hand[1] - 3, (20, 20, 24))
    if on:
        cv.flat(lx, ly, LAMPC)
        _aglow(cv, lx, ly, 5, LAMPC, 0.5)
        for k in range(1, 5):                                               # el reflex a l'aigua
            if hr(k, int(t / 0.3)) > 0.3:
                _aput(cv, lx + round((hr(k, 7) - 0.5) * 4), wl + 1 + k, (200, 170, 110), 0.5 - k * 0.08)
        if hand and t >= Z_RAISE[1] - 0.3:
            _aglow(cv, hand[0], hand[1] - 2, 5, (255, 206, 120), 0.45)


def _zframe(t, bob=0, sway_t=None):
    cv = Canvas(light=LIGHT, transparent=True)
    xs, ywl, s = SHIP
    tip = (round(xs + 0.4 * s), round(ywl - 7.5 * s) - bob)
    cx, wl, sc, water = _zpos(t, bob if t < Z_TOUCH else 0, sway_t)
    motor = Z_MOTOR <= t < Z_MOVE[1] + 0.3
    if water:
        d = t - Z_TOUCH
        if d < 2.5:
            _ring(cv, cx, wl + 1, 14 + d * 12, 0.7 * (1 - d / 2.5), 1)
            _ring(cv, cx, wl + 1, 10 + d * 9, 0.5 * (1 - d / 2.5), 2)
        for k in range(1, 16):                                            # l'estela, curta
            tp = t - k * ZT
            if tp < Z_MOVE[0] or tp > Z_MOVE[1] - 0.6:
                continue
            px, pw, psc, _ = _zpos(tp)
            pl = max(12, round(22 * psc))
            for dx in range(3):
                for side in (0, 1):
                    if hr(k, dx, side, int(tp * 10)) > 0.5:
                        _aput(cv, round(px - pl / 2) - 3 - dx - k // 3, round(pw) + 1 + side * (k // 5), FOAMC,
                              0.7 * (1 - k / 16))
    # el cable de la grua i el ganxo
    if t < Z_HOOK[0]:
        hook = (round(cx), round(wl) - 13)
    else:
        k = _seg(t, Z_HOOK)
        hook = (round(ZX0 + (tip[0] - ZX0) * k), round(WL_WATER - 13 + (tip[1] + 6 - (WL_WATER - 13)) * k))
    cv.line(tip[0], tip[1], hook[0], hook[1], WIRE, 2.4, lit=0)
    cv.put(hook[0], hook[1] + 1, WIRE, 3.4, lit=0)
    x0, L, jx, top = _zodiac(cv, cx, wl, sc, motor, t)
    if t < Z_HOOK[0]:                                                       # les eslingues
        cv.line(hook[0], hook[1] + 1, x0 + 2, round(wl) - 3, WIRE, 1.8, lit=0)
        cv.line(hook[0], hook[1] + 1, x0 + L - 2, round(wl) - 4, WIRE, 1.8, lit=0)
    if Z_MOTOR <= t < Z_MOTOR + 1.6:                                        # el motor arrenca: una bufada de fum
        a = t - Z_MOTOR
        for j in range(5):
            _aput(cv, x0 - 2 - round(a * 4) + (j % 3) - 1, round(wl) - 6 - round(a * 6) - j // 3, (90, 94, 104),
                  0.6 * (1 - a / 1.6))
    _sample(cv, t, jx, top, round(wl))
    return cv.img


def _wait_frames():
    """A la portada: penja de la grua i es gronxa amb el vaixell (8 fotogrames de 300 ms, com el mar)."""
    return [_zframe(0.0, BOB[i], sway_t=i * 0.3) for i in range(N)]


def _clip(name):
    a, b = CLIPS[name]
    return lambda: [_zframe(a + i * ZT, BOB[int((a + i * ZT) / 0.3) % N]) for i in range(round((b - a) / ZT) + 1)]


ZODIAC_ESPERA = {'frames': _wait_frames, 'frameDuration': 300, 'zIndex': 2}
ZODIAC_CLIPS = {name: {'frames': _clip(name), 'frameDuration': round(ZT * 1000), 'loop': False, 'prop': 'zodiac'}
                for name in CLIPS}

# ─── En Bastida, a popa ─────────────────────────────────────────────────────
# Petit, mig amagat per la borda: l'anorac fosc, la barba blanca i la brasa de la pipa. Al pròleg, quan la Juana ja
# té la mostra, treu de la butxaca el missatger de satèl·lit, que fa llum blava, i escriu («bastida_escriu»).
# 8 fotogrames de 300 ms, com el mar, perquè pugi i baixi amb el vaixell.

BSIL = [(4, 5, 8), (10, 11, 16), (20, 22, 30), (34, 36, 46)]
SCREEN = (150, 226, 255)


def _bastida(i, device=False):
    cv = Canvas(light=LIGHT, transparent=True)
    xs, ywl, s = SHIP
    x = round(xs + 4.6 * s)
    y = round(ywl - sheer(4.6) * s) - BOB[i % N]           # la regala de la borda
    cv.rect(x - 1, y - 5, x + 1, y - 1, BSIL, 1.2, lit=0)   # l'anorac
    cv.vline(x - 1, y - 5, y - 1, BSIL, 2.4, lit=0)        # la vora que mira la lluna
    cv.rect(x - 1, y - 7, x, y - 7, [(150, 96, 70)], 0, lit=0)       # la cara, girada cap a popa
    cv.flat(x + 1, y - 7, (40, 30, 26))
    cv.hline(x - 1, x, y - 6, [(200, 200, 196)], 0, lit=0)          # la barba blanca
    cv.hline(x - 1, x + 1, y - 8, BSIL, 1.6, lit=0)                 # la gorra
    ember = (255, 140, 60) if (i % 4) else (200, 80, 30)
    cv.flat(x - 2, y - 6, ember)                                     # la pipa
    if device:
        cv.flat(x - 2, y - 4, BSIL[2])                               # la mà
        bright = SCREEN if i % 3 else (220, 245, 255)
        cv.flat(x - 3, y - 4, bright)
        cv.flat(x - 3, y - 3, (60, 110, 140))
        _aglow(cv, x - 3, y - 4, 4, (120, 210, 255), 0.4)
        cv.flat(x - 1, y - 6, (176, 210, 226))                       # la barba, il·luminada de blau
    return cv.img


BASTIDA = {'frames': lambda: [_bastida(i) for i in range(N)], 'frameDuration': 300, 'zIndex': 2}
BASTIDA_ESCRIU = {'frames': lambda: [_bastida(i, device=True) for i in range(N)], 'frameDuration': 300,
                  'prop': 'bastida_popa'}


# ─── La silueta de la plataforma ────────────────────────────────────────────
# Al pròleg, quan la narració la diu, s'encén el focus de la plataforma i retalla la silueta dels prismàtics
# («vigia_on», amb un parpelleig de fluorescent). Fins llavors la capa és buida («vigia»). Només el cel: el reflex
# al mar el faria quiet damunt de l'onada.

def _watcher_layer():
    a, b = Canvas(light=LIGHT), Canvas(light=LIGHT)
    bg(a)
    bg(b, watcher=True)
    d = _diff(b.img, a.img)
    d.paste((0, 0, 0, 0), (0, HOR * a.S, d.width, d.height))       # (en píxels reals)
    return d


def _watcher_frames():
    on = _watcher_layer()
    off = Canvas(light=LIGHT, transparent=True).img
    return [on if k else off for k in (1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1)]


VIGIA = {'frames': lambda: [Canvas(light=LIGHT, transparent=True).img], 'frameDuration': 1000, 'loop': False,
         'zIndex': 2}
VIGIA_ON = {'frames': _watcher_frames, 'frameDuration': 90, 'loop': False, 'prop': 'vigia'}


ANIMS = {
    'mar': {'frames': _frames, 'frameDuration': 300},
    'zodiac': ZODIAC_ESPERA,
    'bastida_popa': BASTIDA,       # «bastida» sol xocaria amb la seva veu (el personatge) a BenneScript
    'titol': {'frames': _title_frames, 'frameDuration': 1000, 'loop': False, 'zIndex': 3},
}
