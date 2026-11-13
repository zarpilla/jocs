"""
Aigua Verne — `aqua_fons` (L), Escena 3: el fons de l'antic mar d'Aqua, vist des de baix.

Al fons, el moll és una paret altíssima de carreus: dalt de tot, la grua i el cable que baixa fins a la
**cistella**, aquí a baix, a la sorra. A la paret, les ratlles de sal de l'aigua de cada any, la franja d'algues
seques, l'escala que s'acaba a l'aire, pneumàtics de defensa penjats allà on abans tocaven els vaixells, i una
regla de marea pintada (0, 10, 20, 30, 40 metres). A la dreta, la paret s'acaba i es veu el mar sec fins a
l'horitzó, amb la Canonada d'Aqua.
A terra: sorra blanca amb ondulacions, algues seques, closques. Les **nanses** i les xarxes velles, les **boies**
de mesurar clavades a la sorra amb números pintats (marquen els creuaments del camí), els **ossos** d'un peix gros,
el **bassal** (l'única aigua) i, al costat, la platja de **sorra fina** (prop `sorra`). A la dreta, la **casa de la
Juana**: el casc d'una barca bolcat (la quilla a dalt), amb una porta, l'ull de bou amb llum a dins, la xemeneia i
l'antena de la ràdio.

ANIMS: `calitja`, `pols`, `llum_canonada`, `llum_juana` (la làmpada, a l'ull de bou), `fum` (la xemeneia),
`bassal` (el reflex de l'aigua).
"""
import math

import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

from hd.pix import Canvas, Light, W, H, hr, mix
from hd.rooms.comu import text, text_width
from hd.rooms.exterior import fbm, smooth
from hd640.rooms.aqua_comu import (RH, SKYA, SALT, SAND, STONEA, ALGA, ALGAS, WOODG, TEALH, REDF, PAINTW, RUSTA, OCHRE,
                                   STEELA, BLACKT, GLASSD, ROPEA, WICKER, BONE, WATERB, WARMW,
                                   cel, plana, canonada, canonada_llum, shade, to_screen, text180,
                                   calitja_frames, pols_frames, diff, amb_contorn)

HOR = 146                 # l'horitzó (a la dreta, on s'acaba la paret)
WALL_X1 = 420             # on s'acaba la paret del moll
WTOP = 20                 # el parapet, dalt de tot
WBASE = 174               # el peu de la paret
CAN_X, CAN_LY = 456, 18
CABLE_X = 198
BASKET = (182, 176, 216, 204)
HOUSE_X0 = 470            # on comença el casc bolcat (la roda de proa toca a terra)
GUNWALE = 214             # la regala, a terra
DOOR = (520, 118, 556, 214)
PORT = (596, 150, 9)      # l'ull de bou (cx, cy, r)
CHIMNEY = (612, 62)       # el capell de la xemeneia
POOL = (352, 226, 444, 252)
BEACH = (446, 224, 528, 257)

WETST = [mix(a, b, 0.45) for a, b in zip(STONEA[:8], [(26, 32, 30), (36, 44, 40), (50, 60, 52), (66, 76, 62),
                                                      (82, 92, 74), (100, 108, 88), (120, 126, 104),
                                                      (140, 144, 120)])]
BUOY = [(60, 14, 12), (110, 26, 20), (160, 44, 30), (200, 70, 44), (226, 110, 80), (244, 160, 130)]
TYRE = [(10, 10, 12), (20, 20, 24), (34, 34, 38), (50, 50, 56), (70, 70, 76)]

LIGHT = Light(ambient=0.5, vignette=(56, 14), floor_fade=None)
LIGHT.point(360, -140, r=760, k=1.1, power=1.0)            # el sol de migdia
LIGHT.point(PORT[0], PORT[1] + 30, r=46, k=0.5, power=1.6)   # la llum càlida que surt de l'ull de bou


# ─── La paret del moll ─────────────────────────────────────────────────────

MARKS = (0.12, 0.22, 0.31, 0.40, 0.48, 0.55, 0.61, 0.66)   # l'aigua de cada any, més avall


def paret(cv):
    """La paret del moll, altíssima: carreus petits (és lluny i molt alta), a l'ombra suau del migdia; la part de
    dalt, seca i clara; la de baix, verdosa d'algues seques; i les ratlles de sal de cada any."""
    h = WBASE - WTOP
    for x in range(0, WALL_X1 + 1):
        algtop = 0.46 + (fbm(x / 22, 0.5, 13) - 0.5) * 0.1
        for y in range(WTOP, WBASE + 1):
            f = (y - WTOP) / h
            row = int((y - WTOP) / 6)
            fr = ((y - WTOP) / 6) % 1
            bw = 15
            off = bw / 2 if row % 2 else 0
            sx = 210 + (x - 210) / (1 - (WBASE - y) / 1100)                     # mirem amunt: les verticals convergeixen
            col = int((sx + off) / bw)
            fc = ((sx + off) / bw) % 1
            lvl = 5.0 + (hr(row, col, 7) - 0.5) * 0.9 + (fbm(x / 16, y / 10, 8) - 0.5) * 0.8
            lvl -= f * 0.4
            lvl -= 0.9 * max(0.0, 1 - (WALL_X1 - x) / 30) * 0                 # (la cantonada es fa a part)
            joint = fr < 0.17 or fc < 0.07
            if joint:
                lvl -= 1.3
            elif fr < 0.34:
                lvl += 0.5
            if f > algtop:
                a = (f - algtop) / (1 - algtop)
                spot = fbm(x / 8, y / 6, 12)
                if spot > 0.56 + a * 0.08:
                    cv.put(x, y, ALGAS, 2.0 + (spot - 0.56) * 4 - (1.0 if joint else 0) - a * 0.4)
                else:
                    cv.put(x, y, WETST, lvl - 0.8 - a * 0.7)
            else:
                cv.put(x, y, STONEA, lvl)
            for m in MARKS:
                d = (f - m) * h + (fbm(x / 12, m * 10, 14) - 0.5) * 2.4
                if -0.5 <= d < 0.5 and fbm(x / 7, m * 7, 15) > 0.5:
                    cv.put(x, y, SALT, 6.4 if f < algtop else 5.4)
                elif 0.5 <= d < 1.5 and fbm(x / 7, m * 7, 15) > 0.55 and hr(x, int(m * 100), 1) < 0.5:
                    cv.put(x, y, SALT, 5.0)
    # el parapet i, al cim, la vora contra el cel
    for x in range(0, WALL_X1 + 1):
        for y in range(WTOP - 7, WTOP):
            k = y - (WTOP - 7)
            cv.put(x, y, STONEA, 6.6 - k * 0.35 - (1.2 if x % 30 == 0 else 0) + (fbm(x / 8, y / 3, 16) - 0.5) * 0.6)
        cv.put(x, WTOP - 8, STONEA, 8.2)
        cv.put(x, WTOP, STONEA, 2.4)
    # la cantonada (la bocana): carreus grans, una mica més clars, i la cara de l'extrem que fuig
    for y in range(WTOP - 8, WBASE + 1):
        for x in range(WALL_X1 - 6, WALL_X1 + 8):
            f = (y - WTOP) / h
            if x > WALL_X1:
                k = (x - WALL_X1) / 8
                if y < WTOP - 8 + k * 3:
                    continue
                lvl = 6.2 - k * 0.8 - (1.2 if (y - WTOP) % 12 == 0 else 0) - f * 0.6
            else:
                quoin = int((y - WTOP) / 12) % 2
                if quoin == 0 and x < WALL_X1 - 3:
                    continue
                lvl = 5.6 - f * 0.6 - (1.4 if (y - WTOP) % 12 == 0 else 0)
            cv.put(x, y, STONEA if f < 0.5 else WETST, lvl)
    # l'ombra al peu de la paret, i la calitja a dalt de tot (és molt amunt)
    cv.darken(0, WBASE, WALL_X1 + 7, WBASE + 2, lambda x, y: 0.9 - (y - WBASE) * 0.3)
    cv.tint(0, WTOP - 8, WALL_X1 + 7, WBASE, (214, 226, 238), lambda x, y: 0.22 * (1 - (y - WTOP + 8) / (WBASE - WTOP + 8)) ** 1.5)


def regla(cv, x0=86):
    """Una regla de marea pintada a la paret: blanca i negra, amb els metres (0 a dalt, on era el mar)."""
    h = WBASE - WTOP
    y0 = WTOP + int(MARKS[0] * h) - 2
    for y in range(y0, WBASE - 2):
        for x in range(x0, x0 + 4):
            band = ((y - y0) // 4) % 2
            cv.put(x, y, PAINTW if band else BLACKT, (4.4 if band else 2.4) - (y - y0) * 0.01 - (fbm(x, y / 3, 17) > 0.7))
    for i, n in enumerate(('0', '10', '20', '30')):
        yy = y0 + 2 + i * int((WBASE - 6 - y0) / 4)
        cv.hline(x0 + 5, x0 + 8, yy + 2, PAINTW, 4.2)
        text(cv, n, x0 + 10, yy, PAINTW, 4.6)


def escala(cv):
    """L'escala del moll, que baixa arrapada a la paret i s'acaba a mitja altura: a sota, res."""
    steps = [(292 + i * 6, WTOP + 1 + i * 4) for i in range(16)]
    for i, (sx, sy) in enumerate(steps):
        w = 7 if i < 15 else 3
        cv.darken(sx, sy + 3, sx + w + 1, sy + 8, lambda x, y: 0.95 - (y - sy - 3) * 0.16)
        cv.rect(sx, sy, sx + w, sy, STONEA, 8.6)
        cv.rect(sx, sy + 1, sx + w, sy + 2, STONEA, lambda x, y: 5.6 - (1.4 if x == sx + w else 0) + (y == sy + 1) * 0.6)
    lx, ly = steps[-1]
    cv.line(lx + 4, ly + 1, lx + 7, ly + 4, RUSTA, 3.4)                        # la vareta del graó trencat
    for i in range(0, 15, 2):
        sx, sy = steps[i]
        cv.vline(sx + 1, sy - 6, sy - 1, RUSTA, 3.0)
    for i in range(13):
        (ax, ay), (bx, by) = steps[i], steps[i + 1]
        cv.line(ax + 1, ay - 6, bx + 1, by - 6, RUSTA, 3.8)
    ax, ay = steps[13]
    cv.line(ax + 1, ay - 6, ax + 9, ay + 4, RUSTA, 3.2)                        # la barana, doblegada


def defenses(cv):
    """Pneumàtics de defensa penjats amb cadenes: eren on tocaven els vaixells. Ara pengen a l'aire."""
    h = WBASE - WTOP
    for x, m in ((40, 0.19), (150, 0.19), (246, 0.27)):
        y = WTOP + int(m * h)
        cv.line(x, WTOP - 1, x, y - 6, STEELA, 3.0)
        cv.disc(x, y, 7, 6, TYRE, lambda nx, ny: 2.6 - ny * 1.2 - nx * 0.4)
        cv.disc(x, y, 3, 2.6, TYRE, 0.4)
        cv.darken(x - 6, y + 6, x + 6, y + 8, 0.7)
        for k in range(-5, 6, 3):
            cv.put(x + k, y - 5, SALT, 6.4)


def desguas(cv, x=360, y=120):
    """Una sortida de clavegueram amb la reixa rovellada i el regalim fosc a sota."""
    cv.disc(x, y, 7, 6, BLACKT, lambda nx, ny: 0.8 + ny * 0.4)
    cv.ring(x, y, 7, RUSTA, 3.0, step=8)
    for k in range(-5, 6, 3):
        cv.vline(x + k, y - 5, y + 5, RUSTA, 2.6)
    for yy in range(y + 7, WBASE):
        for xx in range(x - 3, x + 4):
            if hr(xx, yy // 3, 18) > 0.35 + abs(xx - x) * 0.12:
                cv.put(xx, yy, ALGA, 1.6 + (yy - y) * 0.02)


def grua_dalt(cv):
    """La grua, vista des de baix: la caseta i la ploma treuen el cap per damunt del parapet; el cable baixa
    fins a la cistella."""
    cv.rect(150, 0, 192, WTOP - 9, OCHRE, lambda x, y: 3.6 - (x - 150) * 0.01 - (1.2 if x >= 190 else 0) + (y == 0) * 0.4)
    cv.rect(176, 3, 189, 9, GLASSD, 1.8)
    for k in range(4):
        cv.hline(154, 170, 3 + k * 3, OCHRE, 2.0)
    cv.rect(160, WTOP - 9, 178, WTOP - 8, STEELA, 3.0)
    # la ploma, que surt cap a nosaltres (curta, en escorç)
    for i in range(9):
        y = 6 - i * 0.6
        cv.line(188, 10 + i * 0.3, CABLE_X, 1, OCHRE, 4.0 - (i % 2) * 1.4)
    cv.disc(CABLE_X, 2, 2.5, 2.5, STEELA, 4.0)
    cv.vline(CABLE_X, 4, BASKET[1] - 16, STEELA, 3.2)


def cistella(cv):
    """La cistella, baixada fins a la sorra (la sortida cap amunt)."""
    x0, y0, x1, y1 = BASKET
    cx = (x0 + x1) / 2
    hx, hy = CABLE_X, y0 - 16
    cv.disc(hx, hy, 2, 3, STEELA, lambda nx, ny: 4.2 - nx)
    for ax in (x0 + 1, x0 + 10, x1 - 10, x1 - 1):
        cv.line(hx, hy + 2, ax, y0 + 1, STEELA, 3.0 + (0.8 if ax < hx else 0))
    cv.darken(x0 - 3, y1 - 1, x1 + 4, y1 + 3, lambda x, y: 0.95 if abs(x - cx - 1) < (x1 - x0) / 2 + 3 - (y - y1) else 0)
    for y in range(y0, y1 + 1):
        t = (y - y0) / (y1 - y0)
        inset = int(t * 3)
        for x in range(x0 + inset, x1 - inset + 1):
            u = (x - cx) / ((x1 - x0) / 2)
            weave = ((x // 2) + (y // 2)) % 2
            cv.put(x, y, WICKER, 3.8 - u * 1.2 - u * u * 0.8 + (0.6 if weave else -0.4) - t * 0.6)
    cv.disc(cx, y0 + 1, (x1 - x0) / 2 + 1, 3, STEELA, lambda nx, ny: 3.6 + ny * 1.0 if ny > 0 else 2.2)
    cv.disc(cx, y0 + 1, (x1 - x0) / 2 - 1, 1.6, WICKER, 0.8)
    for yy in (y0 + 10, y1 - 4):
        ins = int((yy - y0) / (y1 - y0) * 3)
        cv.hline(x0 + ins, x1 - ins, yy, STEELA, 3.2)
    for x in range(x0 - 2, x1 + 3):                                               # sorra contra la base
        if hr(x, 19) > 0.3:
            cv.put(x, y1 + (1 if hr(x, 20) > 0.5 else 0), SAND, 6.8)


# ─── La dreta: el mar sec fins a l'horitzó ─────────────────────────────────

def lluny(cv):
    cel(cv, HOR, x0=0, seed=6)
    plana(cv, HOR, 200, x0=WALL_X1 - 6, seed=8)
    canonada(cv, CAN_X, HOR, w0=2.0, w1=4.2, light_y=CAN_LY)
    # un vaixell petit encallat a l'horitzó, entre la paret i la casa
    for x in range(436, 452):
        top = HOR - 2 - (3 if 440 < x < 446 else 0) - (5 if 441 < x < 443 else 0)
        for y in range(top, HOR + 1):
            cv.put(x, y, REDF if y > HOR - 3 else PAINTW, 3.0, lit=0.4)
    cv.tint(434, HOR - 10, 454, HOR + 1, (226, 234, 240), 0.3)


# ─── El terra ──────────────────────────────────────────────────────────────

def _path_y(x):
    """El camí de petjades: de la cistella a la porta de la Juana, passant per les boies."""
    pts = ((180, 210), (258, 214), (344, 208), (424, 216), (500, 218), (540, 216))
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        if ax <= x <= bx:
            t = (x - ax) / (bx - ax)
            t = t * t * (3 - 2 * t)
            return ay + (by - ay) * t
    return None


def terra(cv):
    """El fons del mar: sorra blanca amb ondulacions de vent (el costat d'ombra, blavós), crostes de sal, una
    taca de fang sec clivellat (on hi ha els ossos) i, més a prop, més gra."""
    for y in range(WBASE - 4, RH):
        dz = y - (HOR - 30)
        gy = 900 / dz
        t = (y - WBASE) / (RH - WBASE)
        for x in range(W):
            if y < WBASE + 1 and x <= WALL_X1 + 7:
                continue
            if x > WALL_X1 + 7 and y < HOR + 30:
                continue
            gx = (x - 320) / dz * 3.0
            ph = gy * 7.0 + fbm(gx * 0.5, gy * 0.3, 21) * 6 + math.sin(gx * 1.3) * 0.6
            rip = math.sin(ph)
            lvl = 5.9 + t * 0.4 + (fbm(x / 34, y / 9, 22) - 0.5) * 0.9
            ramp = SAND
            py = _path_y(x)
            on_path = py is not None and abs(y - py) < 5 + t * 6
            if on_path:
                lvl = 5.4 + (fbm(x / 10, y / 4, 23) - 0.5) * 0.6                    # el camí, trepitjat
                if hr(x // 4, y // 2, 24) > 0.93:
                    lvl -= 1.4                                                     # petjades
            elif rip > 0.6:
                lvl += 0.9
            elif rip < -0.5:
                lvl -= 1.1 + t * 0.3                                               # la cara d'ombra de l'ondulació
            fang = ((x - 276) / 66) ** 2 + ((y - 238) / 15) ** 2 + (fbm(x / 10, y / 5, 28) - 0.5) * 0.8
            if fang < 1:
                c = _mud(x, y)
                cv.put(x, y, MUD, 3.6 + (fbm(x / 8, y / 4, 29) - 0.5) * 0.8 - (2.0 if c else 0) + (0.8 if fang > 0.8 else 0))
                continue
            crust = fbm(x / 30, y / 8, 25)
            if crust > 0.66 and not on_path:
                cv.put(x, y, SALT, 7.0 + (crust - 0.66) * 6 + (hr(x, y, 26) - 0.5))
                continue
            cv.put(x, y, ramp, lvl + (hr(x, y, 27) - 0.5) * 0.5 * t)
    # algues seques, closques i pedretes
    for k in range(22):
        x = int(hr(k, 30) * W)
        y = int(WBASE + 8 + hr(k, 31) * (RH - WBASE - 12))
        kind = hr(k, 32)
        if POOL[0] - 6 < x < BEACH[2] + 6 and y > POOL[1] - 6:
            continue
        if x > HOUSE_X0 and y < GUNWALE + 4:
            continue
        if kind < 0.4:                                                             # una mata d'algues seques
            for i in range(6):
                a = math.pi * (0.2 + 0.6 * hr(k, i, 33))
                l = 3 + hr(k, i, 34) * 4
                cv.line(x, y, x + math.cos(a) * l, y - math.sin(a) * l * 0.6, ALGA, 3.0 + hr(k, i) * 1.6)
            cv.hline(x - 2, x + 2, y + 1, SAND, 4.2)
        elif kind < 0.8:                                                           # una closca
            cv.disc(x, y, 2.2, 1.4, BONE, lambda nx, ny: 4.4 - ny * 1.4)
            cv.put(x, y + 1, BONE, 1.0)
        else:                                                                      # una pedreta
            cv.disc(x, y, 2.5, 1.6, STONEA, lambda nx, ny: 5.0 - ny * 1.6 - nx * 0.6)
            cv.darken(x - 2, y + 2, x + 3, y + 2, 0.7)


MUD = [(40, 42, 48), (62, 64, 70), (88, 90, 94), (114, 116, 118), (140, 140, 140), (164, 164, 160)]


def _mud(x, y):
    """Les clivelles del fang sec (Voronoi aixafat)."""
    from hd640.rooms.aqua_comu import _voronoi
    e, _ = _voronoi(x / 9, y / 4, 31)
    return e < 0.08


# ─── Les coses del fons ────────────────────────────────────────────────────

def nansa(cv, x0, y0, w, h, ang=0.0, flip=False):
    """Una nansa: una trampa de vímet en forma d'ampolla tombada, amb cèrcols clars, el teixit en diagonal i la
    boca d'embut fosca."""
    def fn(u, v):
        if 0 <= u <= w:
            t = u / w
            r = h / 2 * (0.62 + 0.38 * math.sin(math.pi * min(1.0, 0.2 + t * 0.95))) * (1 - smooth(0.85, 1, t) * 0.45)
            if abs(v) <= r:
                if t < 0.1 and abs(v) < r * 0.6:
                    return (WICKER, 0.4 + abs(v) / r * 1.2)                       # la boca, fosca
                ring = int(u) % 8 in (0, 1) and t > 0.08
                vv = v / r
                shadeb = 3.4 - vv * 1.4 - vv * vv * 0.8
                if ring:
                    return (WICKER, shadeb + 1.4)
                weave = (int(u) + int(v + 40)) % 4
                if weave == 0:
                    return (WICKER, shadeb - 1.6)                                   # els forats del teixit
                return (WICKER, shadeb + (0.4 if weave == 1 else 0))
        return None
    cx, cy = (x0 + w, y0) if flip else (x0, y0)
    amb_contorn(cv, lambda c: shade(c, (x0 - h, y0 - h, x0 + w + h, y0 + h), cx, cy, ang + (math.pi if flip else 0), fn))


def nanses(cv):
    """Les nanses i la xarxa vella amb els suros, a l'esquerra."""
    cv.darken(6, 228, 136, 238, lambda x, y: 0.9 if ((x - 70) / 64) ** 2 + ((y - 233) / 5) ** 2 < 1 else 0)
    NET = [(30, 26, 20), (50, 44, 32), (74, 64, 46), (98, 86, 62), (124, 110, 80), (150, 136, 102)]

    def xarxa(c):
        for y in range(198, 238):
            for x in range(54, 136):
                top = 237 - 30 * math.exp(-((x - 96) / 22) ** 2) - 5 * fbm(x / 7, 1, 35) - 3 * math.exp(-((x - 64) / 8) ** 2)
                if y >= top:
                    mesh = (x + y) % 4 == 0 or (x - y) % 4 == 0
                    fold = fbm(x / 6, y / 4, 36)
                    c.put(x, y, NET, 3.4 - (y - top) * 0.04 + (fold - 0.5) * 2.4 - (1.6 if mesh else 0))
        for k in range(8):
            fx = 64 + k * 9 + int(hr(k, 37) * 4)
            fy = int(237 - 28 * math.exp(-((fx - 96) / 22) ** 2) + 3 + hr(k, 38) * 6)
            c.disc(fx, fy, 2.6, 2.0, OCHRE, lambda nx, ny: 4.6 - ny * 1.6 - nx * 0.4)  # els suros
    amb_contorn(cv, xarxa)
    nansa(cv, 14, 220, 46, 26, ang=-0.12)
    nansa(cv, 66, 242, 42, 22, ang=0.08, flip=True)
    nansa(cv, 2, 247, 32, 18, ang=0.2)
    for i in range(70):                                                              # una corda que se'n va
        x = 126 + i
        y = 238 + math.sin(i * 0.18) * 2 + i * 0.1
        cv.put(x, y, ROPEA, 3.0 + (i % 3 == 0) * 0.9)
        cv.put(x, y + 1, SAND, 3.6)


def boia(cv, x, base, n, h=44, lean=0.0):
    """Una boia de mesurar: un pal clavat a la sorra amb un flotador rodó, vermell i blanc, amb el número pintat
    en gran. Marquen els creuaments del camí."""
    tx = x + lean * h
    cv.line(x, base, tx, base - h, WOODG, 3.6)
    cv.line(x + 1, base, tx + 1, base - h, WOODG, 2.2)
    fy = base - h + 16
    fx = x + lean * (h - 16)
    cv.disc(fx, fy, 9, 9, BUOY, lambda nx, ny: 4.2 - nx * 1.4 - ny * 0.8 - (nx * nx + ny * ny) * 0.6)
    for yy in range(int(fy - 9), int(fy + 10)):                                     # la franja blanca
        for xx in range(int(fx - 9), int(fx + 10)):
            nx, ny = (xx - fx) / 9, (yy - fy) / 9
            if nx * nx + ny * ny <= 1 and abs(ny) < 0.42:
                cv.put(xx, yy, PAINTW, 5.4 - nx * 1.4)
    w = text_width(n)
    text(cv, n, int(fx - w / 2), int(fy - 2), BLACKT, 0.6)
    cv.put(fx - 4, fy - 6, BUOY, 5.6)                                                  # el reflex
    # el gallardet de dalt i la marca de nivell (una ratlla de pintura al pal)
    cv.line(tx, base - h, tx + 5, base - h + 2, BUOY, 3.6)
    cv.line(tx, base - h + 1, tx + 4, base - h + 3, BUOY, 2.6)
    cv.hline(int(x + lean * 6) - 1, int(x + lean * 6) + 2, base - 6, PAINTW, 5.6)



def ossos(cv, x0=232, y0=238):
    """Els ossos d'un peix gros, damunt el fang sec: el crani, l'espina amb les costelles, la cua."""
    cv.darken(x0 + 4, y0 + 4, x0 + 86, y0 + 7, lambda x, y: 0.8 if abs(y - y0 - 5) < 2 - abs(x - x0 - 44) / 44 else 0)

    def draw(c):
        c.poly([(x0, y0 + 1), (x0 + 6, y0 - 8), (x0 + 17, y0 - 10), (x0 + 22, y0 - 2), (x0 + 20, y0 + 5), (x0 + 6, y0 + 6)],
               BONE, lambda x, y: 4.8 - (y - y0 + 10) * 0.14 - (x - x0) * 0.02)
        c.disc(x0 + 12, y0 - 3, 2.6, 2.4, BLACKT, 1.0)
        c.line(x0 + 1, y0 + 3, x0 + 12, y0 + 6, BONE, 2.6)
        for k in range(5):
            c.put(x0 + 2 + k * 2, y0 + 4, BONE, 5.6)
        for i in range(54):
            x = x0 + 22 + i
            y = y0 - 1 + math.sin(i * 0.07) * 1.5
            c.put(x, y, BONE, 5.0 if i % 3 else 3.4)
            c.put(x, y + 1, BONE, 3.0)
            if i % 4 == 0 and i < 46:
                l = 9 * math.sin(math.pi * (i + 6) / 56)
                c.line(x, y - 1, x + 2, y - 1 - l, BONE, 4.6)
                c.line(x, y + 2, x + 3, y + 2 + l * 0.6, BONE, 3.6)
        tx, ty = x0 + 76, y0
        c.poly([(tx, ty), (tx + 11, ty - 9), (tx + 7, ty + 1), (tx + 11, ty + 8)], BONE, 4.2)
        for k in range(3):
            c.line(tx + 1, ty, tx + 10, ty - 7 + k * 6, BONE, 2.6)
    amb_contorn(cv, draw, k=0.5)


def bassal(cv, phase=0.0):
    """El bassal: l'única aigua. Un tros de cel blau, la vora de sorra mullada i un anell de sal."""
    x0, y0, x1, y1 = POOL
    cx, cy, rx, ry = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2, (y1 - y0) / 2
    for y in range(y0 - 3, y1 + 4):
        for x in range(x0 - 6, x1 + 7):
            n = fbm(x / 9, y / 4, 40) - 0.5
            d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 + n * 0.5
            if d < 1:
                v = (y - y0) / (y1 - y0)
                lvl = 4.8 - v * 1.6 + (fbm(x / 20 + phase, y / 2, 41) - 0.5) * 0.8
                if d > 0.82:
                    lvl -= 1.4                                                     # la vora, una mica fonda
                cv.put(x, y, WATERB, lvl, lit=0.4)
            elif d < 1.35:
                cv.put(x, y, SAND, 3.4 + (d - 1) * 4)                                # sorra mullada
            elif d < 1.6 and hr(x, y, 42) > 0.3:
                cv.put(x, y, SALT, 7.6)                                              # l'anell de sal
    # el reflex de la boia número 3, ballant una mica
    bx = 424 + 4
    for y in range(y0 + 2, y0 + 12):
        if hr(y, int(phase * 10), 43) > 0.4:
            cv.put(bx + round(math.sin(y * 1.3 + phase * 6)), y, [(110, 50, 50), (150, 80, 76)], 1.0, lit=0)


def sorra(cv):
    """La platja de sorra fina, al costat del bassal: una lloma baixa i llisa, sense ondulacions, d'un blanc més
    càlid que la resta, amb el gra finíssim; la vora de baix fa una ombra suau i té un sotet on algú n'ha agafat."""
    x0, y0, x1, y1 = BEACH
    cx, cy, rx, ry = (x0 + x1) / 2, (y0 + y1) / 2 + 2, (x1 - x0) / 2, (y1 - y0) / 2
    FINE = [(120, 110, 92), (160, 150, 126), (196, 186, 160), (222, 214, 190), (240, 234, 214), (250, 247, 232),
            (255, 253, 244)]
    for y in range(y0 - 2, y1 + 3):
        for x in range(x0 - 4, x1 + 5):
            n = fbm(x / 10, y / 4, 44) - 0.5
            nx, ny = (x - cx) / rx, (y - cy) / ry
            d = nx * nx + ny * ny + n * 0.5
            if d < 1:
                h = (1 - d) ** 0.5
                lvl = 4.0 + h * 1.6 - ny * 0.9 - nx * 0.4 + (0.4 if (x * 3 + y * 5) % 11 == 0 else 0)
                if ny > 0.55 and d > 0.7:
                    lvl -= 1.0                                                       # el pendent de davant, a l'ombra
                cv.put(x, y, FINE, lvl)
            elif d < 1.2 and ny > -0.2:
                cv.darken(x, y, x, y, 0.45)
    # un sotet: algú n'ha agafat un grapat
    cv.disc(cx + 14, cy - 2, 5, 2, FINE, lambda nx, ny: 2.6 + ny * 1.8)
    cv.hline(int(cx + 10), int(cx + 18), int(cy - 4), FINE, 5.6)


# ─── La casa de la Juana ───────────────────────────────────────────────────

def _keel(x):
    """L'alçada de la quilla (la línia de dalt del casc bolcat): la roda de proa baixa fins a terra a l'esquerra."""
    u = (x - HOUSE_X0) / 70
    if u < 0:
        return None
    if u < 1:
        return GUNWALE - (GUNWALE - 98) * math.sin(u * math.pi / 2) ** 0.7
    return 98 - (x - HOUSE_X0 - 70) * 0.03


def casa(cv):
    """La casa de la Juana: una barca gran bolcada. Dalt, l'obra viva (antifouling vermell esvaït); una ratlla
    blanca de flotació; a baix, el costat blau amb la pintura pelada (la fusta grisa a sota). Taules (traques)
    que convergeixen a la roda. Recolzada sobre pedres."""
    for x in range(HOUSE_X0, W):
        yk = _keel(x)
        if yk is None:
            continue
        hh = GUNWALE - yk
        for y in range(int(yk), GUNWALE + 1):
            f = (y - yk) / max(1, hh)
            strake = f * 11
            sf = strake % 1
            u = (x - HOUSE_X0) / (W - HOUSE_X0)
            # el volum: la panxa del casc, més clara a dalt (el sol)
            lvl = 4.0 - f * 1.2 + (1.0 if f < 0.12 else 0) - (0.9 if sf < 0.12 else 0) + (0.5 if 0.12 <= sf < 0.3 else 0)
            lvl += (fbm(x / 10, y / 5, 50) - 0.5) * 0.6
            if f < 0.40:
                ramp = REDF
                lvl -= 0.4
            elif f < 0.47:
                ramp = PAINTW
                lvl += 0.4
            else:
                ramp = TEALH
                peel = fbm(x / 7, y / 4, 51)
                if peel > 0.64:
                    ramp = WOODG
                    lvl += 0.8
            if ramp in (REDF, TEALH) and (x - HOUSE_X0) % 9 == 4 and 0.4 < sf < 0.55:
                ramp, lvl = RUSTA, 2.6                                               # els claus, rovellats
            cv.put(x, y, ramp, lvl)
        cv.put(x, int(yk), WOODG, 6.0)                                               # el cantell de la quilla
        cv.put(x, int(yk) - 1, WOODG, 4.4)
    # la roda de proa (el tallamar), una peça de fusta
    for y in range(100, GUNWALE + 1):
        for x in range(HOUSE_X0, W):
            yk = _keel(x)
            if yk is not None and abs(y - yk) < 2 and y > 110:
                cv.put(x, y, WOODG, 5.0)
                break
    # el nom, de cap per avall (la barca és bolcada)
    text180(cv, 'AURORA', 486, 176, PAINTW, 3.6)
    text180(cv, 'AQ-7', 500, 192, PAINTW, 3.2)
    # les pedres que l'aguanten
    for sx in (480, 508, 572, 612):
        cv.disc(sx, GUNWALE + 1, 6, 3, STONEA, lambda nx, ny: 5.2 - ny * 1.4 - nx * 0.6)
    cv.darken(HOUSE_X0, GUNWALE + 2, W - 1, GUNWALE + 4, 0.85)


def porta(cv):
    x0, y0, x1, y1 = DOOR
    cv.rect(x0 - 3, y0 - 3, x1 + 3, y1, WOODG, lambda x, y: 5.2 - (1.4 if x > x1 else 0) + (0.8 if y == y0 - 3 else 0))
    cv.rect(x0, y0, x1, y1, WOODG, lambda x, y: 3.0 - (1.4 if (x - x0) % 6 == 0 else 0) + (0.6 if (x - x0) % 6 == 1 else 0)
            + (fbm(x / 4, y / 8, 53) - 0.5) * 0.8)
    for yy in (y0 + 12, y1 - 16):                                                    # travessers
        cv.rect(x0 + 1, yy, x1 - 1, yy + 3, WOODG, lambda x, y: 4.0 - (y - yy) * 0.5)
    cv.line(x0 + 2, y0 + 16, x1 - 2, y1 - 18, WOODG, 3.6)                           # la diagonal
    cv.disc(x1 - 6, (y0 + y1) // 2 + 4, 1.6, 1.6, OCHRE, 4.6)                        # el pom de llautó
    # una ferradura i un número de casa fet amb una closca
    cv.ring(x0 + 18, y0 + 6, 3, RUSTA, 3.4, step=24)
    cv.rect(x0 - 2, y1 - 2, x1 + 2, y1 + 2, STONEA, 5.0)                              # el graó de pedra


def ull_de_bou(cv):
    """L'ull de bou: anell de bronze amb cargols, el vidre amb la llum càlida de la làmpada de dins, una cortina
    mig corruda, i el reflex del cel a dalt."""
    cx, cy, r = PORT
    BRONZE = [(40, 26, 14), (74, 50, 24), (112, 80, 40), (152, 114, 60), (190, 152, 90), (222, 190, 130)]
    cv.glow(cx, cy, r + 10, (255, 214, 140), 0.25)
    cv.disc(cx, cy, r + 2, r + 2, BRONZE, lambda nx, ny: 3.6 - nx * 0.8 - ny * 1.4)
    WARM = [(60, 34, 14), (120, 74, 30), (190, 126, 56), (240, 184, 96), (255, 226, 150), (255, 244, 200)]
    cv.disc(cx, cy, r - 0.5, r - 0.5, WARM, lambda nx, ny: 1.6 + (1 - nx * nx - ny * ny) * 2.6 - (1.6 if nx < -0.35 else 0), lit=0)
    cv.ring(cx, cy, r - 0.5, BRONZE, 0.6, step=6)
    for yy in range(cy - r + 1, cy - r + 4):                                         # el reflex del cel
        for xx in range(cx - 2, cx + 4):
            if (xx - cx) ** 2 + (yy - cy) ** 2 < (r - 1) ** 2 and hr(xx, yy) > 0.4:
                cv.flat(xx, yy, (200, 220, 236))
    for a in range(0, 360, 60):
        cv.put(cx + math.cos(math.radians(a + 30)) * (r + 1), cy + math.sin(math.radians(a + 30)) * (r + 1), BRONZE, 5.6)


def xemeneia(cv):
    x, y = CHIMNEY
    yk = _keel(x)
    cv.rect(x - 2, y, x + 2, int(yk) + 2, STEELA, lambda xx, yy: 4.0 - (xx - x) * 0.6)
    cv.rect(x - 5, y - 3, x + 5, y - 1, STEELA, lambda xx, yy: 4.6 - (yy - y + 3) * 0.6)
    cv.rect(x - 3, y - 5, x + 3, y - 4, STEELA, 3.6)
    for yy in range(y + 2, int(yk)):
        if hr(yy, 54) > 0.7:
            cv.put(x + 2, yy, RUSTA, 3.0)


def antena(cv):
    """L'antena de la ràdio (la Juana parla amb la Capitana per ràdio) i el cable fins a un pal."""
    x = 560
    yk = int(_keel(x))
    cv.vline(x, 34, yk, STEELA, 4.2)
    for k, y in enumerate(range(40, yk - 6, 10)):
        cv.hline(x - 4 + k // 2, x + 4 - k // 2, y, STEELA, 3.6)
    cv.put(x, 33, [(120, 30, 30), (220, 60, 50)], 1.0, lit=0)
    # el tensor i el cable que va cap a terra
    cv.line(x, 46, 636, 96, STEELA, 2.8)


def barril_i_banc(cv):
    """Un barril de pluja (buit) i un banc fet amb una taula vella, al costat de la porta."""
    bx, by = 494, 214
    cv.darken(bx - 9, by, bx + 10, by + 2, 0.85)
    cv.rect(bx - 8, by - 22, bx + 8, by, WOODG, lambda x, y: 3.8 - abs(x - bx) * 0.12 - (1.0 if (x - bx) % 4 == 0 else 0))
    for yy in (by - 19, by - 4):
        cv.hline(bx - 8, bx + 8, yy, RUSTA, 3.0)
    cv.disc(bx, by - 22, 8, 2, WOODG, lambda nx, ny: 1.6 + ny)
    # el banc
    cv.rect(562, 196, 590, 198, WOODG, lambda x, y: 5.0 - (y - 196) * 0.8)
    for lx in (565, 586):
        cv.rect(lx, 199, lx + 2, 212, WOODG, 3.0)
    cv.darken(560, 212, 592, 214, 0.8)
    # una tassa al banc
    cv.rect(580, 191, 584, 195, PAINTW, 4.6)
    cv.put(585, 193, PAINTW, 3.4)


# ─── Composició ────────────────────────────────────────────────────────────

def bg(cv):
    lluny(cv)
    paret(cv)
    regla(cv)
    defenses(cv)
    desguas(cv)
    escala(cv)
    terra(cv)
    grua_dalt(cv)
    nanses(cv)
    for bx, by in ((258, 206), (344, 198), (424, 212)):
        cv.darken(bx - 8, by, bx + 9, by + 2, lambda xx, yy, bx=bx, by=by: 0.9 if abs(xx - bx) < 8 - (yy - by) * 2 else 0)
    amb_contorn(cv, lambda c: boia(c, 258, 206, '1', h=46, lean=0.06))
    amb_contorn(cv, lambda c: boia(c, 344, 198, '2', h=42, lean=-0.08))
    amb_contorn(cv, lambda c: boia(c, 424, 212, '3', h=48, lean=0.04))
    ossos(cv)
    bassal(cv)
    casa(cv)
    antena(cv)
    xemeneia(cv)
    porta(cv)
    ull_de_bou(cv)
    barril_i_banc(cv)
    x0, y0, x1, y1 = BASKET
    cv.darken(x0 - 3, y1 - 1, x1 + 5, y1 + 3, lambda x, y: 0.95 if abs(x - (x0 + x1) / 2 - 1) < (x1 - x0) / 2 + 3 - (y - y1) else 0)
    amb_contorn(cv, cistella)
    for y in range(RH, H):                                                       # la barra de verbs: negre
        for x in range(W):
            cv.P[x, y] = (0, 0, 0, 255)


PROPS = {'sorra': sorra}


# ─── Animacions ────────────────────────────────────────────────────────────

def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv.img


def _frames_calitja():
    return calitja_frames(_base(), WALL_X1 + 8, HOUSE_X0 + 40, HOR - 3, HOR + 8, n=8, amp=1.0, seed=2)


def _frames_pols():
    return pols_frames(24, 30, (0, 180, W - 1, RH - 6), seed=9)


def _frames_llum():
    on = canonada_llum(CAN_X, CAN_LY, True)
    off = Canvas(transparent=True).img
    return [on, on, off, off, off, off, off, off]


def _frames_llum_juana():
    """La flama de la làmpada de la Juana, que tremola darrere l'ull de bou."""
    cx, cy, r = PORT
    out = []
    for i in range(8):
        cv = Canvas(transparent=True)
        k = 0.5 + 0.5 * math.sin(i / 8 * 2 * math.pi) * (0.6 + 0.4 * hr(i, 60))
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                d = math.hypot(x - cx - 1, y - cy - 1) / r
                if d < 1 and hr(x, y, i) < (1 - d) * 0.6 * k:
                    cv.P[x, y] = (255, 236, 180, 255) if d < 0.4 else (250, 206, 120, 255)
        out.append(cv.img)
    return out


def _frames_fum():
    """Un fil de fum de la xemeneia, que puja i s'esfilagarsa."""
    x0, y0 = CHIMNEY
    out = []
    n = 12
    for i in range(n):
        cv = Canvas(transparent=True)
        for k in range(16):
            t = ((k + i / n * 4) % 16) / 16
            y = y0 - 6 - t * 50
            x = x0 + math.sin(t * 5 + k * 0.3) * (1 + t * 4) + t * 10
            a = int(150 * (1 - t))
            for dx in range(int(1 + t * 3)):
                if 0 <= y < H:
                    cv.P[int(x + dx), int(y)] = (236, 238, 240, a)
        out.append(cv.img)
    return out


def _frames_bassal():
    base = _base()
    out = []
    for i in range(6):
        cv = Canvas(light=LIGHT, img=base.copy())
        bassal(cv, phase=i / 6 * 2)
        out.append(diff(cv.img, base))
    return out


ANIMS = {'calitja': {'frames': _frames_calitja, 'frameDuration': 160},
         'pols': {'frames': _frames_pols, 'frameDuration': 110},
         'llum_canonada': {'frames': _frames_llum, 'frameDuration': 250},
         'llum_juana': {'frames': _frames_llum_juana, 'frameDuration': 140},
         'fum': {'frames': _frames_fum, 'frameDuration': 160},
         'bassal': {'frames': _frames_bassal, 'frameDuration': 220}}


GEOMETRIA = {
    'things': {
        'cistella': {'rect': (178, 156, 220, 206), 'walk': (204, 216)},
        'porta_juana': {'rect': (517, 115, 559, 216), 'walk': (538, 224)},
        'nanses': {'rect': (2, 196, 132, 256), 'walk': (146, 238)},
        'boies': {'rect': (244, 150, 438, 214), 'walk': (344, 218)},
        'bassal': {'rect': (346, 222, 450, 256), 'walk': (396, 218)},
        'sorra': {'rect': (444, 222, 530, 257), 'walk': (486, 240)},
        'ossos': {'rect': (228, 226, 322, 248), 'walk': (334, 246)},
    },
    'spawns': {'iri': (226, 236), 'vet': (162, 242)},
    'walkable': [(136, 256), (134, 214), (176, 210), (470, 214), (560, 220), (639, 224), (639, 256),
                 (446, 256), (446, 230), (350, 230), (348, 256)],
}
