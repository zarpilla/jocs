"""
Prova a 640×360: dalt del pal de l'Arenga, a les tres de la matinada de l'Escena 9, amb vent (vegeu hd/rooms/pal.py,
la de 480×270). Mateixa composició ×4/3, dibuixada de nou: el cel i el mar es calculen a la resolució nova (les
funcions de cel de hd640/rooms/coberta_popa.py), i hi ha detall que a 480 no hi cabia: la reixa més fina, la proa
d'allà baix amb la borda i els puntals, el rètol «ARNÈS» al pal, les brides i els cargols de la cúpula.
Decorat `fosc` (el generador parat). ANIMS: `vent` (la bandera i les ratxes d'esquitxos) i `mar` (les onades d'allà
baix i l'escuma de la roda).
"""
import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

import math
from functools import lru_cache

from hd.pix import Canvas, Light, W, H, hr, mix, B4
from hd.rooms.arenga import CAB, DARK, REDP, YELL, WHITEP, box, bolt, vpipe, hpipe, glow
from hd.rooms.comu import _diff, text, text_width
from hd.rooms.exterior import fbm, NSEA, REDH, ROPE, DECKX, LAMP, GLOW_WARM
from hd640.rooms.coberta_popa_pla_comu import night_sky, _wave

# Art a 2× (1280×720 per a una sala de 640×360): el mateix dibuix, amb les formes, el dither i la llum a la
# resolució real (hd1280/canvas2x.py); el motor el mostra a 1/2 (artScale al .room.json).
ART_SCALE = 2
from hd1280.canvas2x import Canvas2x as Canvas  # noqa: E402,F811
from hd.pix import Canvas as Canvas1x  # noqa: E402,F401  (llenços auxiliars en píxels de sala: figures, textos)

K = 4 / 3

MASTW = [(8, 10, 14), (16, 19, 25), (27, 31, 38), (41, 45, 52), (60, 63, 68), (84, 86, 88), (112, 112, 108),
         (146, 144, 134), (184, 180, 164), (220, 214, 194), (242, 238, 222)]
GRATE = [(3, 4, 6), (7, 9, 12), (13, 15, 19), (21, 24, 28), (32, 35, 39), (46, 49, 52), (64, 66, 66),
         (88, 88, 84), (116, 114, 104)]
DOME = [(14, 17, 24), (26, 30, 38), (42, 46, 54), (62, 66, 74), (88, 92, 98), (118, 120, 122), (150, 150, 148),
        (184, 182, 174), (214, 210, 198), (238, 234, 222)]
FLAGR = [(30, 6, 8), (60, 12, 14), (100, 22, 22), (146, 36, 32), (190, 58, 44), (226, 96, 70)]
ORANGEL = [(40, 12, 6), (84, 26, 10), (140, 48, 16), (196, 80, 26), (232, 118, 44), (250, 164, 90)]
ROPEW = ROPE

FLOOR_Y = 200          # vora del darrere de la plataforma
BOTTOM = 260
SEA_Y1 = 275           # fins on es dibuixa el mar (per sota hi ha la barra)
VP = (320, 53)
HOR = 123              # l'horitzó (som a dalt: queda alt)
MOON = (128, 35)
LAMP_XY = (429, 85)    # el focus del pal, que mira avall
PLAT_L = 211           # vora esquerra de la plataforma, al darrere (a baix s'eixampla)
MAST_X = 429           # eix del pal
ANT_X = 315            # eix de l'antena
HATCH = (517, 224, 603, 253)
RAIL_TOP = 139         # la barana del darrere (≈ 1 m)
POSTS = (FLOOR_Y, 227, 261)

LIGHT = Light(ambient=-0.3, vignette=(53, 19), floor_fade=None)
LIGHT.point(LAMP_XY[0], LAMP_XY[1] + 8, r=253, k=2.9, squash=0.9, down=True, power=1.5)
LIGHT.point(ANT_X, 80, r=80, k=0.5, power=2.0)          # la lluna a la cúpula


def plat_left(y):
    """x de la vora esquerra de la plataforma a l'alçada y (perspectiva)."""
    return VP[0] + (PLAT_L - VP[0]) * (y - VP[1]) / (FLOOR_Y - VP[1])


def scale(y):
    """Escala de perspectiva (1 a la vora del darrere)."""
    return (y - VP[1]) / (FLOOR_Y - VP[1])


# ─── El cel, el mar i l'Arenga, allà baix ──────────────────────────────────

def sky(cv):
    night_sky(cv, 0, HOR, MOON, seed=9, clouds=0.62)
    for y in range(5, HOR - 8):                                      # ratxes de núvol esfilagarsat (vent)
        for x in range(W):
            n = fbm(x / K / 110 + y / K / 9, y / K / 3.2, 31)
            if n > 0.66:
                cv.flat(x, y, mix(cv.get(x, y), (70, 80, 102), min(0.45, (n - 0.66) * 2.4)))


def sea(cv, phase=0.0, x0=0, x1=W - 1, seed=4, calm=1.3):
    mx = MOON[0]
    for y in range(HOR, SEA_Y1 + 1):
        d = (y - HOR) / K
        for x in range(x0, x1 + 1):
            lvl = 3.4 - min(2.0, d * 0.045)
            n = _wave(x, y, HOR, seed, phase)
            lvl += (n - 0.5) * 1.6 * calm + (1.2 * calm if n > 0.78 else 0)
            m = max(0.0, 1 - abs(x - mx) / ((6 + d * 0.9) * K))
            if m > 0:
                lvl += m * 1.2
                if n > 0.62 and hr(x // 2, y, seed) > 0.25:
                    lvl += 3.6 * m
            cv.put(x, y, NSEA, lvl, lit=0)
    for x in range(x0, x1 + 1):
        cv.put(x, HOR, NSEA, 4.0, lit=0)
    # vist de dalt: el mar, a prop (a baix), més fosc i amb escuma que es trenca
    for y in range(HOR + 53, SEA_Y1 + 1):
        for x in range(x0, x1 + 1):
            cv.flat(x, y, mix(cv.get(x, y), (2, 4, 8), min(0.5, (y - HOR - 53) / 187)))
            n = fbm((x / K + phase * 3) / 9, (y / K) / 3.5, 77)
            if n > 0.74:
                cv.flat(x, y, mix(cv.get(x, y), (150, 166, 170), (n - 0.74) * 1.6))


BOW = (72, 176)        # la punta de la proa (lluny, cap a l'horitzó)


def arenga_below(cv, phase=0.0, lights=True):
    """La proa de l'Arenga vista de dalt del pal: coberta, borda blanca amb la línia vermella, el molinet, la
    balsa, l'escotilla i dos llums de coberta. L'escuma de la roda."""
    bx, by = BOW
    for side in (-1, 1):                                             # el solc d'escuma de la roda
        for i in range(93):
            t = i / 93
            x = bx + side * (8 + t * 56) + round(math.sin(i * 0.53 + phase * 2) * 2)
            y = by + 3 + t * 93
            for k in range(4):
                if hr(i, k, side, int(phase * 4) % 4) > 0.35:
                    cv.flat(x + side * k, y + k, mix(cv.get(x + side * k, y + k), (170, 186, 190), 0.6 - k * 0.12))
    hull = [(bx, by), (bx + 45, by + 48), (bx + 69, SEA_Y1), (bx - 59, SEA_Y1), (bx - 37, by + 48)]
    cv.poly(hull, MASTW, lambda x, y: 3.0 + (y - by) * 0.005, lit=0)
    deck = [(bx, by + 8), (bx + 39, by + 49), (bx + 60, SEA_Y1), (bx - 51, SEA_Y1), (bx - 32, by + 49)]
    cv.poly(deck, DECKX, lambda x, y: 2.0 + (hr(x // 3, y // 2) - 0.5) * 0.5, lit=0)
    # la línia vermella, per fora de la borda, i els puntals de la barana (punts blancs)
    for (ax, ay), (cx, cy) in ((hull[0], hull[1]), (hull[1], hull[2]), (hull[0], hull[4]), (hull[4], hull[3])):
        n = max(abs(cx - ax), abs(cy - ay))
        for i in range(n + 1):
            x = ax + (cx - ax) * i / n
            y = ay + (cy - ay) * i / n
            off = 2 if cx > ax else -2
            cv.put(round(x + off * 0.6), round(y + 1), REDH, 3.4, lit=0)
            if i % 7 == 0 and i:
                cv.put(round(x - off * 0.5), round(y), MASTW, 6.4, lit=0)
    # el molinet de l'àncora i les cadenes que van a l'escobenc
    cv.rect(bx - 8, by + 29, bx + 8, by + 36, DECKX, 4.0, lit=0)
    cv.hline(bx - 8, bx + 8, by + 29, DECKX, 5.2, lit=0)
    for sx in (-1, 1):
        cv.disc(bx + sx * 8, by + 32, 3, 4, DECKX, 5.0, lit=0)
        for k in range(14):                                          # baules
            cv.put(bx + sx * 3 - sx * round(k * 0.15), by + 28 - k, DECKX, 4.6 if k % 2 else 3.4, lit=0)
    # l'escotilla de la caixa de cadenes i la balsa salvavides (contenidor blanc, amb les cintes)
    cv.rect(bx - 13, by + 48, bx - 3, by + 55, DECKX, 3.2, lit=0)
    cv.hline(bx - 13, bx - 3, by + 48, DECKX, 4.4, lit=0)
    cv.disc(bx + 19, by + 61, 8, 5, MASTW, lambda nx, ny: 4.2 - ny * 1.2, lit=0)
    cv.hline(bx + 12, bx + 26, by + 61, MASTW, 2.4, lit=0)
    for sx in (bx + 15, bx + 23):
        cv.vline(sx, by + 57, by + 65, [(20, 30, 60), (50, 70, 130)], 1.2, lit=0)
    # el pal de proa
    cv.vline(bx, by + 5, by + 19, MASTW, 4.4, lit=0)
    cv.vline(bx + 1, by + 6, by + 19, MASTW, 2.6, lit=0)
    if not lights:                                                   # el generador parat: la proa a les fosques
        cv.flat(bx, by + 4, (60, 58, 56))
        return
    for lx, ly in ((bx - 16, by + 72), (bx + 27, by + 83)):          # dos llums de coberta, amb el cercle a terra
        for y in range(ly - 11, ly + 12):
            for x in range(lx - 21, lx + 22):
                d = math.hypot((x - lx) / 21, (y - ly) / 11)
                if d < 1:
                    cv.flat(x, y, mix(cv.get(x, y), (200, 160, 80), 0.32 * (1 - d) ** 1.4))
        cv.flat(lx, ly - 3, (255, 236, 180))
        cv.flat(lx + 1, ly - 3, (240, 210, 150))
        glow(cv, lx, ly - 3, 7, GLOW_WARM, 0.6)
    cv.flat(bx, by + 4, (255, 250, 230))                             # el llum de navegació de proa
    glow(cv, bx, by + 4, 7, (255, 250, 230), 0.6)


# ─── El pal, la creueta i la bandera ───────────────────────────────────────

def crosstree(cv):
    box(cv, MAST_X - 93, 21, MAST_X + 93, 27, MASTW, 4.4, grad=0.4)
    for bx in range(MAST_X - 88, MAST_X + 93, 13):
        bolt(cv, bx, 23, MASTW, 4.8)
    for lx in (MAST_X - 67, MAST_X + 67):                            # llums de tope, apagats
        box(cv, lx - 4, 12, lx + 4, 20, CAB, 3.0)
        cv.disc(lx, 15, 3, 3, [(80, 30, 26), (140, 50, 40), (170, 70, 56)], 0.6, lit=0)
        cv.put(lx - 1, 14, [(80, 30, 26), (140, 50, 40), (170, 70, 56)], 2.0, lit=0)


def mast(cv, lights=True):
    for y in range(0, FLOOR_Y + 3):                                  # el pal: tub blanc
        for x in range(MAST_X - 9, MAST_X + 11):
            u = (x - MAST_X) / 10
            cv.put(x, y, MASTW, 4.6 + 1.6 * (-0.15 - u) - 1.0 * u * u + (hr(x // 2, y // 5) - 0.5) * 0.25)
    for sy in (51, 149):                                             # juntes amb brida
        box(cv, MAST_X - 12, sy, MAST_X + 12, sy + 4, MASTW, 4.4)
        cv.hline(MAST_X - 11, MAST_X + 11, sy, MASTW, 5.8)
        for bx in range(MAST_X - 9, MAST_X + 11, 5):
            bolt(cv, bx, sy + 2, MASTW, 4.8)
    for y in range(13, FLOOR_Y - 5, 12):                             # graons (U de rodó) al costat esquerre
        cv.hline(MAST_X - 17, MAST_X - 9, y, MASTW, 5.2)
        cv.hline(MAST_X - 17, MAST_X - 9, y + 1, MASTW, 3.6)
        cv.vline(MAST_X - 17, y, y + 3, MASTW, 3.4)
        cv.hline(MAST_X - 16, MAST_X - 9, y + 2, MASTW, 1.6)
    for i in range(8):                                               # ratlles de rovell
        x = MAST_X - 7 + int(hr(i, 61) * 14)
        y0 = 53 + int(hr(i, 62) * 120)
        for y in range(y0, y0 + 8 + int(hr(i, 63) * 13)):
            if hr(x, y, 64) > 0.25:
                cv.flat(x, y, mix(cv.get(x, y), (120, 60, 30), 0.4))
    # el rètol d'arnès obligatori, fixat al pal amb dues brides
    sx0, sx1, sy0 = MAST_X - 14, MAST_X + 14, 108
    box(cv, sx0, sy0, sx1, sy0 + 15, WHITEP, 3.8)
    cv.rect(sx0 + 1, sy0 + 1, sx1 - 1, sy0 + 5, [(10, 30, 70), (20, 60, 130), (40, 90, 170)], 1.8)
    s_ = 'ARNÈS'
    text(cv, s_, (sx0 + sx1 + 1 - text_width(s_)) // 2, sy0 + 8, None, 0, flat=(24, 28, 34))
    for by in (sy0 - 1, sy0 + 16):
        cv.hline(sx0 + 3, sx1 - 3, by, CAB, 2.8)
    crosstree(cv)
    for cx in (MAST_X - 93, MAST_X + 93):                            # tirants
        cv.line(cx, 27, MAST_X - 9 if cx < MAST_X else MAST_X + 10, 45, MASTW, 3.0)
    # el focus de coberta, mirant la plataforma
    fx, fy = LAMP_XY
    box(cv, fx - 12, fy - 8, fx + 12, fy + 3, CAB, 3.2)
    cv.hline(fx - 12, fx + 12, fy - 8, CAB, 4.6)
    for x in range(fx - 10, fx + 11, 4):                             # aletes de dissipació
        cv.vline(x, fy - 7, fy - 3, CAB, 2.2)
    cv.rect(fx - 4, fy - 13, fx + 4, fy - 9, CAB, 2.2)
    cv.rect(fx - 11, fy + 4, fx + 11, fy + 5, LAMP if lights else CAB, 2.6 if lights else 1.6, lit=0)
    for gx in range(fx - 10, fx + 11, 3):                            # reixeta
        cv.put(gx, fy + 4, CAB, 2.0, lit=0)


FLAG_HX, FLAG_TOP, FLAG_W, FLAG_H = MAST_X - 80, 29, 45, 27


def flag(cv, t=0):
    """La bandera de Mar Obert (blanca, amb el cercle vermell), a la drissa de la creueta, batent cap a l'esquerra."""
    hx, top, w, h = FLAG_HX, FLAG_TOP, FLAG_W, FLAG_H
    cv.vline(hx, 27, top, ROPEW, 3.0)
    pts = []
    for i in range(w + 1):
        k = i / w
        dy = math.sin(i / K * 0.38 - t * 1.4) * (1.0 + k * 3.2) * K
        pts.append((hx - i, top + dy))
    for i, (x, y) in enumerate(pts):
        k = i / w
        hh = h * (1 - k * 0.12)
        slope = (pts[min(i + 1, w)][1] - pts[max(i - 1, 0)][1]) / K
        for j in range(int(hh) + 1):
            yy = y + j
            lvl = 7.4 - slope * 1.4 - j * 0.03
            if k > 0.86 and hr(i, j, 5) < (k - 0.86) * 5:              # l'extrem, esfilagarsat
                continue
            d = math.hypot(i - w * 0.42, j - hh * 0.5)
            if 4.3 < d < 8.8:                                         # el cercle vermell de Mar Obert
                cv.put(round(x), round(yy), FLAGR, 4.4 - slope * 1.0, lit=0.4)
            else:
                cv.put(round(x), round(yy), MASTW, lvl, lit=0.4)
    cv.line(hx, top + h, hx + 5, top + h + 40, ROPEW, 2.6)
    cv.line(hx + 1, top + h, hx + 6, top + h + 40, ROPEW, 1.6)


# ─── L'antena del satèl·lit ────────────────────────────────────────────────

def antenna(cv):
    cx = ANT_X
    vpipe(cv, cx, 139, FLOOR_Y + 3, 7, MASTW, 4.4)                  # el pedestal
    for y in (168, FLOOR_Y - 3):
        box(cv, cx - 12, y, cx + 12, y + 4, MASTW, 4.0)
        cv.hline(cx - 11, cx + 11, y, MASTW, 5.4)
        for bx in range(cx - 9, cx + 11, 6):
            bolt(cv, bx, y + 2, MASTW, 4.6)
    # la caixa del motor que l'orienta, amb el pilot ambre (desorientada) i la reixeta
    box(cv, cx - 16, 147, cx + 16, 165, MASTW, 4.2, grad=0.8)
    cv.flat(cx + 9, 152, (255, 120, 40))
    cv.flat(cx + 10, 152, (230, 100, 30))
    glow(cv, cx + 9, 152, 5, (255, 140, 60), 0.5)
    for x in range(cx - 12, cx + 5, 3):
        cv.vline(x, 155, 161, MASTW, 2.6)
    box(cv, cx - 14, 149, cx - 8, 152, WHITEP, 4.4, edge=False)     # l'etiqueta
    cv.line(cx + 16, 160, cx + 21, 176, CAB, 2.0)
    cv.line(cx + 21, 176, cx + 24, FLOOR_Y, CAB, 2.0)
    # el collar giratori, amb les mordasses
    box(cv, cx - 27, 133, cx + 27, 144, MASTW, 4.0)
    cv.hline(cx - 27, cx + 27, 133, MASTW, 5.4)
    cv.hline(cx - 26, cx + 26, 143, MASTW, 2.6)
    for bx in range(cx - 23, cx + 24, 8):
        bolt(cv, bx, 138, MASTW, 4.6)
    # la cúpula (radom) de fibra, amb les costures i la sal
    rx, ry, dy = 40, 51, 133
    for y in range(dy - ry, dy + 1):
        for x in range(cx - rx, cx + rx + 1):
            nx, ny = (x - cx) / rx, (y - dy) / ry
            if nx * nx + ny * ny <= 1:
                nz = math.sqrt(max(0.0, 1 - nx * nx - ny * ny))
                lvl = 2.6 + 2.6 * (0.35 * nx - 0.55 * ny + 0.6 * nz) + 1.6 * nz
                if x == cx or abs(ny + 0.5) < 0.012 or abs(nx - 0.5 * math.sqrt(max(0, 1 - ny * ny))) < 0.012:
                    lvl -= 0.6                                       # costures
                if y > dy - 8:
                    lvl -= 0.8                                       # el faldó, a l'ombra
                if hr(x // 2, y // 3, 71) > 0.94 and ny > -0.6:
                    lvl -= 0.7                                       # taques de sal
                cv.put(x, y, DOME, lvl, lit=0.7)
    cv.hline(cx - rx, cx + rx, dy - 8, DOME, 3.6, lit=0.5)
    for bx in range(cx - rx + 4, cx + rx - 3, 7):                    # els cargols del faldó
        cv.put(bx, dy - 4, DOME, 5.6, lit=0.5)
    for x, y in ((cx - 19, dy - 40), (cx - 17, dy - 41), (cx - 21, dy - 38), (cx - 16, dy - 42)):
        cv.flat(x, y, (240, 238, 228))                               # reflex de la lluna
    box(cv, cx - 8, dy - 27, cx + 8, dy - 21, DOME, 6.4, edge=False) # l'adhesiu del fabricant
    cv.hline(cx - 6, cx + 6, dy - 25, DOME, 4.0)
    cv.hline(cx - 5, cx + 3, dy - 23, DOME, 4.6)
    cv.poly([(cx, dy - 5), (cx - 4, dy - 1), (cx + 4, dy - 1)], YELL, 3.6)   # la fletxa de proa


def knot(cv):
    """El nus Bastida: el cap passa dues voltes al collar (una de més), fa el nus i va a la barana."""
    cx = ANT_X
    for k, y in enumerate((136, 140)):
        for x in range(cx - 27, cx + 28):
            ph = (x + k * 2) % 4
            cv.put(x, y + (1 if ph < 2 else 0), ROPEW, 3.6 - abs(ph - 1.5) * 0.4)
            cv.put(x, y + (2 if ph < 2 else 1), ROPEW, 2.2 - abs(ph - 1.5) * 0.3)
    cv.disc(cx + 27, 139, 5, 5, ROPEW, lambda nx, ny: 3.8 - nx * 0.8 - ny * 1.2)
    cv.disc(cx + 25, 137, 2.5, 2.5, ROPEW, 2.2)
    cv.line(cx + 24, 141, cx + 30, 137, ROPEW, 1.6)                  # la volta que es veu
    cv.put(cx + 29, 136, ROPEW, 1.4)
    cv.line(cx + 31, 141, 400, 155, ROPEW, 3.4)                      # el cap tens fins a la barana
    cv.line(cx + 31, 142, 400, 156, ROPEW, 2.0)
    for i, y in enumerate(range(144, 160)):                          # el xicotet que sobra, penjant
        cv.put(cx + 24 + round(math.sin(i * 0.6) * 1.6), y, ROPEW, 3.0)


# ─── La plataforma i la barana ─────────────────────────────────────────────

def platform(cv):
    """La reixa de la plataforma, en perspectiva, amb la vora de planxa a l'esquerra."""
    for y in range(FLOOR_Y, SEA_Y1 + 1):
        xl = plat_left(y)
        d = y - VP[1]
        for x in range(int(math.ceil(xl)), W):
            u = VP[0] + (x - VP[0]) * 147 / d
            v = 2933 / d
            bar = (u % 7) < 1.4
            cross = (v % 3.4) < 0.7
            if bar and cross:
                lvl = 4.6
            elif bar:
                lvl = 3.9 + (0.4 if (u % 7) < 0.6 else 0)
            elif cross:
                lvl = 3.1
            else:
                lvl = 1.0                                            # el buit: a sota, la nit
            cv.put(x, y, GRATE, lvl + (hr(x // 3, y // 2, 81) - 0.5) * 0.3)
        for k in range(4):                                           # la vora de planxa (cantell)
            cv.put(xl + k, y, MASTW, 3.6 - k * 0.5)
    for x in range(PLAT_L, W):                                       # la vora del darrere
        cv.put(x, FLOOR_Y, MASTW, 2.4)
        cv.put(x, FLOOR_Y + 1, MASTW, 3.2)
    for y in range(FLOOR_Y, SEA_Y1 + 1):                             # el sòcol de peu a la vora esquerra
        xl = plat_left(y)
        hgt = round(8 * scale(y))
        for k in range(hgt):
            cv.put(xl - 1, y - k, MASTW, 2.8 + (0.6 if k == hgt - 1 else 0))


def hatch(cv):
    """La boca de l'escala: el forat a la reixa amb el marc, la tapa aixecada i els passamans."""
    x0, y0, x1, y1 = HATCH
    cv.poly([(x0 + 5, y0), (x1 - 5, y0), (x1, y1), (x0, y1)], DARK, lambda x, y: 0.6 + (y - y0) * 0.04, lit=0.2)
    for y in range(y0 + 5, y1, 7):                                   # els esglaons, avall
        xa, xb = x0 + 19, x1 - 19
        cv.hline(xa + (y - y0) // 8, xb - (y - y0) // 8, y, MASTW, 2.2 - (y - y0) * 0.015, lit=0.4)
    cv.vline(x0 + 17, y0 + 3, y1 - 1, MASTW, 2.6, lit=0.4)
    cv.vline(x1 - 17, y0 + 3, y1 - 1, MASTW, 2.6, lit=0.4)
    glow(cv, (x0 + x1) // 2, y1 - 3, 19, (200, 60, 50), 0.25)       # el llum vermell de nit del pont
    for (ax, ay), (bx, by) in (((x0 + 5, y0), (x1 - 5, y0)), ((x1 - 5, y0), (x1, y1)),
                               ((x1, y1), (x0, y1)), ((x0, y1), (x0 + 5, y0))):
        cv.line(ax, ay, bx, by, YELL, 3.2)
        cv.line(ax, ay + 1, bx, by + 1, MASTW, 2.4)
    # la tapa de reixa, aixecada contra la barana del darrere
    cv.poly([(x0 + 8, y0 - 1), (x1 - 8, y0 - 1), (x1 - 11, y0 - 40), (x0 + 11, y0 - 40)], GRATE,
            lambda x, y: 3.4 if (x % 4 == 0 or y % 4 == 0) else 1.2)
    cv.hline(x0 + 11, x1 - 11, y0 - 40, MASTW, 4.0)
    cv.hline(x0 + 8, x1 - 8, y0 - 1, MASTW, 3.0)
    cv.line(x0 + 8, y0 - 1, x0 + 11, y0 - 40, MASTW, 3.4)
    cv.line(x1 - 8, y0 - 1, x1 - 11, y0 - 40, MASTW, 2.6)
    for y in range(y0 - 37, y0 - 32):                                # franges de perill a la tapa
        for x in range(x0 + 12, x1 - 12):
            cv.put(x, y, YELL if ((x + y) // 4) % 2 else DARK, 3.6)
    for hx in (x0 + 16, x1 - 16):                                    # els passamans: dues nanses
        for y in range(y0 - 27, y0 + 8):
            cv.put(hx, y, MASTW, 5.0)
            cv.put(hx + 1, y, MASTW, 3.4)
        for k in range(7):
            ang = math.pi * k / 6
            cv.put(hx + round((1 - math.cos(ang)) * 3) * (1 if hx < (x0 + x1) // 2 else -1),
                   y0 - 27 - round(math.sin(ang) * 3), MASTW, 5.2)


def lifebuoy(cv, rx, ry, r0=6, r1=12):
    for y in range(ry - r1, ry + r1 + 1):
        for x in range(rx - r1, rx + r1 + 1):
            d = math.hypot(x - rx, y - ry)
            if r0 <= d <= r1:
                a = math.degrees(math.atan2(y - ry, x - rx)) % 360
                band = int((a + 22) // 45) % 2
                u = (d - (r0 + r1) / 2) / ((r1 - r0) / 2)
                cv.put(x, y, MASTW if band else ORANGEL, (5.0 if band else 3.2) - u * 0.8 - (y - ry) / r1 * 0.8)
    cv.line(rx - 3, ry - r1 - 1, rx + 3, ry - r1 - 1, ROPEW, 3.0)    # el cap que el lliga
    cv.line(rx, ry - r1 - 1, rx, RAIL_TOP + 2, ROPEW, 3.0)


def rail_back(cv):
    """La barana del darrere: tres tubs blancs i els puntals, d'una banda a l'altra de la plataforma."""
    for ry, r, lvl in ((RAIL_TOP, 3, 5.0), (RAIL_TOP + 21, 2, 4.4), (RAIL_TOP + 41, 2, 4.0)):
        hpipe(cv, PLAT_L, W - 1, ry, r, MASTW, lvl)
    for px in range(PLAT_L + 3, W, 51):
        vpipe(cv, px, RAIL_TOP - 1, FLOOR_Y, 3, MASTW, 4.4)
        cv.disc(px, RAIL_TOP - 1, 3.5, 2, MASTW, 5.4)
        for ry in (RAIL_TOP + 21, RAIL_TOP + 41):                    # les unions dels tubs
            cv.rect(px - 4, ry - 2, px + 4, ry + 2, MASTW, 4.0)
    for x in range(PLAT_L, W):                                       # el sòcol de planxa al peu
        for y in range(FLOOR_Y - 9, FLOOR_Y):
            cv.put(x, y, MASTW, 3.4 - (y - FLOOR_Y + 9) * 0.1)
        cv.put(x, FLOOR_Y - 9, MASTW, 4.8)
    lifebuoy(cv, 595, 163)


def rail_left(cv):
    """La barana del costat esquerre, en perspectiva (cap a nosaltres): puntals i tres tubs."""
    tops = []
    for y in POSTS:
        x = plat_left(y) + 1
        s = scale(y)
        h = (FLOOR_Y - RAIL_TOP) * s
        tops.append((x, y, h, s))
        r = 3 if s > 1.2 else 2
        for yy in range(int(y - h), y + 1):
            for dx in range(-r, r + 1):
                cv.put(x + dx, yy, MASTW, 4.6 - dx * 0.7)
        cv.disc(x, y - h, r + 0.5, 1.6, MASTW, 5.4)
    for frac, lvl in ((1.0, 5.0), (0.65, 4.4), (0.32, 4.0)):
        pts = [(x, y - h * frac) for x, y, h, s in tops]
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            n = int(max(abs(bx - ax), abs(by - ay))) + 1
            for i in range(n + 1):
                t = i / n
                x, y = ax + (bx - ax) * t, ay + (by - ay) * t
                cv.put(round(x), round(y), MASTW, lvl + 0.6)
                cv.put(round(x), round(y) + 1, MASTW, lvl - 0.4)
                cv.put(round(x), round(y) + 2, MASTW, lvl - 1.4)
                if frac == 1.0:
                    cv.put(round(x), round(y) + 3, MASTW, lvl - 2.0)


def cable_tray(cv):
    """Els cables de l'antena i del focus, que baixen pel pal dins d'una canaleta."""
    for x in (MAST_X + 12, MAST_X + 15):
        cv.vline(x, 53, FLOOR_Y, CAB, 2.4 if x == MAST_X + 12 else 1.4)
    for y in range(61, FLOOR_Y, 19):
        cv.hline(MAST_X + 11, MAST_X + 16, y, MASTW, 4.0)
        cv.hline(MAST_X + 11, MAST_X + 16, y + 1, MASTW, 2.4)
    cv.line(MAST_X - 9, 187, ANT_X + 24, 195, CAB, 1.8)              # el de l'antena, per sota la barana
    cv.line(MAST_X - 9, 188, ANT_X + 24, 196, CAB, 1.0)


# ─── Muntatge ───────────────────────────────────────────────────────────────

def _scene(cv, t=0, phase=0.0, flag_on=True, lights=True):
    sky(cv)
    sea(cv, phase)
    arenga_below(cv, phase, lights)
    cv.tint(0, HOR + 40, W - 1, SEA_Y1, (20, 26, 36), lambda x, y: min(0.3, (y - HOR - 40) / 400))
    mast(cv, lights)
    cable_tray(cv)
    if flag_on:
        flag(cv, t)
    rail_back(cv)
    antenna(cv)
    knot(cv)
    platform(cv)
    hatch(cv)
    rail_left(cv)
    if not lights:
        return
    fx, fy = LAMP_XY                                                 # el con de llum del focus, molt subtil
    for y in range(fy + 7, FLOOR_Y + 53):
        wdt = (y - fy) * 0.75
        for x in range(int(fx - wdt), int(fx + wdt) + 1):
            if 0 <= x < W:
                k = 0.10 * (1 - abs(x - fx) / max(1, wdt)) * (1 - (y - fy) / 173)
                if k > B4[y & 3][x & 3] * 0.2:
                    cv.flat(x, y, mix(cv.get(x, y), (255, 214, 140), k))
    cv.tint(PLAT_L, FLOOR_Y, W - 1, SEA_Y1, (255, 200, 120),
            lambda x, y: 0.16 * max(0.0, 1 - math.hypot((x - fx) / 160, (y - 229) / 35)) ** 1.5)
    glow(cv, fx, fy + 5, 29, GLOW_WARM, 0.55)
    glow(cv, fx, fy + 5, 11, (255, 244, 210), 0.7)


def bg(cv):
    _scene(cv)


# ─── Animacions ─────────────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv.img


FLAG_BOX = (MAST_X - 133, 19, MAST_X - 69, 75)


def mast_patch(cv):
    """Torna a dibuixar la creueta, el tirant i el llum de l'esquerra sobre el retall (la bandera hi penja a sota)."""
    box(cv, MAST_X - 93, 21, MAST_X + 93, 27, MASTW, 4.4, grad=0.4)
    for bx in range(MAST_X - 88, MAST_X + 93, 13):
        bolt(cv, bx, 23, MASTW, 4.8)
    cv.line(MAST_X - 93, 27, MAST_X - 9, 45, MASTW, 3.0)
    lx = MAST_X - 67
    box(cv, lx - 4, 12, lx + 4, 20, CAB, 3.0)
    cv.disc(lx, 15, 3, 3, [(80, 30, 26), (140, 50, 40), (170, 70, 56)], 0.6, lit=0)
    cv.put(lx - 1, 14, [(80, 30, 26), (140, 50, 40), (170, 70, 56)], 2.0, lit=0)


def _frames_vent():
    """La bandera que bat i ratxes d'esquitxos que travessen la pantalla."""
    base = _base()
    clean = Canvas(light=LIGHT)                                       # el cel sense bandera
    sky(clean)
    mast(clean)
    frames = []
    n = 8
    x0, y0, x1, y1 = FLAG_BOX
    for i in range(n):
        cv = Canvas(light=LIGHT, img=base.copy())
        S = cv.S                                                     # (el retall, en píxels reals)
        cv.img.paste(clean.img.crop((x0 * S, y0 * S, (x1 + 1) * S, (y1 + 1) * S)), (x0 * S, y0 * S))
        cv.P = cv.img.load()
        mast_patch(cv)
        flag(cv, t=i * (2 * math.pi / 1.4) / n)
        for k in range(6):                                           # ratxes d'esquitxos, molt ràpides
            sx = (W + 53) - ((i * 81 + k * 129) % (W + 107))
            sy = 40 + int(hr(k, 3) * 200)
            ln = 8 + int(hr(k, 4) * 11)
            for j in range(ln):
                x = sx + j
                if 0 <= x < W:
                    cv.flat(x, sy + j // 5, mix(cv.get(x, sy + j // 5), (180, 196, 206), 0.35 * (1 - j / ln)))
        frames.append(_diff(cv.img, base))
    return frames


def _sea_layer(ph):
    """El mar, la proa d'allà baix i la boira, sols (sense res al davant)."""
    cv = Canvas(light=LIGHT)
    sea(cv, ph)
    arenga_below(cv, ph)
    cv.tint(0, HOR + 40, W - 1, SEA_Y1, (20, 26, 36), lambda x, y: min(0.3, (y - HOR - 40) / 400))
    return cv.img


@lru_cache(maxsize=1)
def _sea_mask():
    """On es veu el mar: on el fons és igual que el mar quiet (ni barana, ni pal, ni la llum del focus).
    També darrere la barana del fons, entre els tubs. En píxels reals (X, Y) de l'art."""
    img = _base()
    S = img.width // W
    base, ref = img.load(), _sea_layer(0.0).load()
    return [(X, Y) for Y in range((HOR + 1) * S, (SEA_Y1 + 1) * S) for X in range(img.width) if base[X, Y] == ref[X, Y]]


def _frames_mar():
    """Les onades d'allà baix, que corren; l'escuma de la roda."""
    base = _base()
    frames = []
    for i in range(6):
        src = _sea_layer(i * 1.6).load()
        out = base.copy()
        dst = out.load()
        for X, Y in _sea_mask():
            dst[X, Y] = src[X, Y]
        frames.append(_diff(out, base))
    return frames


ANIMS = {'vent': {'frames': _frames_vent, 'frameDuration': 110},
         'mar': {'frames': _frames_mar, 'frameDuration': 260}}


# ─── El generador parat (Escena 9) ─────────────────────────────────────────

LIGHT_FOSC = Light(ambient=-0.7, vignette=(53, 19), floor_fade=None)
LIGHT_FOSC.point(ANT_X, 80, r=80, k=0.5, power=2.0)
LIGHT_FOSC.point(MOON[0], MOON[1], r=560, k=0.5, power=1.2)


def fosc(cv):
    """Decorat `fosc`: el focus, el llum de tope i els llums de la proa, apagats. On hi ha animacions (la
    bandera, el mar d'allà baix) és una capa negra semitransparent, perquè es continuïn movent; la resta, el
    dibuix a les fosques."""
    base = _base()
    dark = Canvas(light=LIGHT_FOSC)
    _scene(dark, lights=False)
    on, off = Canvas(light=LIGHT), Canvas(light=LIGHT)
    arenga_below(on)
    arenga_below(off, lights=False)
    pb, pd, pon, poff, o = base.load(), dark.img.load(), on.img.load(), off.img.load(), cv.P
    fx0, fy0, fx1, fy1 = FLAG_BOX
    seam = set(_sea_mask())
    for X, Y, _, _ in cv.pixels():
        x, y = X // cv.S, Y // cv.S
        anim = (fx0 <= x <= fx1 and fy0 <= y <= fy1) or (X, Y) in seam
        if anim and pon[X, Y] == poff[X, Y]:
            lb = sum(pb[X, Y][:3]) + 1
            a = max(0.0, min(1.0, 1 - sum(pd[X, Y][:3]) / lb))
            if a > 0.02:
                o[X, Y] = (0, 0, 0, int(a * 255))
        elif pd[X, Y] != pb[X, Y]:
            o[X, Y] = pd[X, Y]


PROPS = {'fosc': fosc}


# ─── Geometria ─────────────────────────────────────────────────────────────

def _s(*v):
    return tuple(round(c * K) for c in v)


GEOMETRIA = {
    'things': {
        'escala': {'rect': _s(388, 138, 452, 192), 'walk': _s(420, 192)},
        'antena': {'rect': _s(205, 60, 267, 150), 'walk': _s(236, 172)},
        'mar': {'rect': _s(2, 96, 150, 192), 'walk': _s(182, 184)},
    },
    'spawns': {cid: _s(*p) for cid, p in {'iri': (262, 188), 'vet': (300, 192), 'marcel': (339, 166)}.items()},
    'walkable': [_s(*p) for p in [(178, 164), (470, 164), (476, 198), (168, 198)]],
}
