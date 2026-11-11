"""
Pal — dalt del pal de l'Arenga, a les tres de la matinada de l'Escena 9, amb vent.

  - una plataforma petita de reixa, amb barana blanca, penjada del pal; el focus del pal la il·lumina de groc;
  - l'antena del satèl·lit: la cúpula blanca damunt d'un pedestal, amb el collar lligat amb un nus Bastida
    (una volta de més) a la barana;
  - el pal, que continua amunt: creueta, la bandera de Mar Obert esquinçada pel vent, el llum de tope;
  - a l'esquerra, el buit: el mar fosc molt avall i la proa de l'Arenga, petita, amb els llums de coberta;
  - la boca de l'escala, a la plataforma (cap al pont).
ANIMS: `vent` (la bandera i les drisses, ratxes d'esquitxos) i `mar` (les onades d'allà baix).\nDecorat `fosc` (Escena 9, el generador parat): el focus i els llums de la proa, apagats. El Marcel, arrambat\nal pal i a la barana.
"""
import math

from hd.pix import Canvas, Light, W, H, hr, mix, B4
from hd.rooms.arenga import CAB, DARK, REDP, YELL, WHITEP, box, bolt, vpipe, hpipe, glow
from hd.rooms.comu import _diff
from hd.rooms.exterior import night_sky, night_sea, fbm, NSEA, REDH, ROPE, DECKX, LAMP, GLOW_WARM

# ─── Rampes (fosc → clar) ───────────────────────────────────────────────────
# blanc de vaixell, de nit (fred a l'ombra, càlid sota el focus)
MASTW = [(8, 10, 14), (16, 19, 25), (27, 31, 38), (41, 45, 52), (60, 63, 68), (84, 86, 88), (112, 112, 108),
         (146, 144, 134), (184, 180, 164), (220, 214, 194), (242, 238, 222)]
GRATE = [(3, 4, 6), (7, 9, 12), (13, 15, 19), (21, 24, 28), (32, 35, 39), (46, 49, 52), (64, 66, 66),
         (88, 88, 84), (116, 114, 104)]
DOME = [(14, 17, 24), (26, 30, 38), (42, 46, 54), (62, 66, 74), (88, 92, 98), (118, 120, 122), (150, 150, 148),
        (184, 182, 174), (214, 210, 198), (238, 234, 222)]
FLAGR = [(30, 6, 8), (60, 12, 14), (100, 22, 22), (146, 36, 32), (190, 58, 44), (226, 96, 70)]
ROPEW = ROPE

FLOOR_Y = 150          # vora del darrere de la plataforma
BOTTOM = 195
VP = (240, 40)
HOR = 92               # l'horitzó (som a dalt: queda alt)
MOON = (96, 26)
LAMP_XY = (322, 64)    # el focus del pal, que mira avall
PLAT_L = 158           # vora esquerra de la plataforma, al darrere (a baix s'eixampla)
MAST_X = 322           # eix del pal
ANT_X = 236            # eix de l'antena
HATCH = (388, 168, 452, 190)

LIGHT = Light(ambient=-0.3, vignette=(40, 14), floor_fade=None)
LIGHT.point(LAMP_XY[0], LAMP_XY[1] + 6, r=190, k=2.9, squash=0.9, down=True, power=1.5)
LIGHT.point(ANT_X, 60, r=60, k=0.5, power=2.0)          # la lluna a la cúpula


def plat_left(y):
    """x de la vora esquerra de la plataforma a l'alçada y (perspectiva)."""
    return VP[0] + (PLAT_L - VP[0]) * (y - VP[1]) / (FLOOR_Y - VP[1])


def scale(y):
    """Escala de perspectiva (1 a la vora del darrere)."""
    return (y - VP[1]) / (FLOOR_Y - VP[1])


# ─── El cel, el mar i l'Arenga, allà baix ──────────────────────────────────

def sky(cv):
    night_sky(cv, 0, HOR, moon=MOON, seed=9, clouds=0.62)
    # ratxes de núvol esfilagarsat que corre (vent)
    for y in range(4, HOR - 6):
        for x in range(W):
            n = fbm(x / 110 + y / 9, y / 3.2, 31)
            if n > 0.66:
                cv.flat(x, y, mix(cv.get(x, y), (70, 80, 102), min(0.45, (n - 0.66) * 2.4)))


def sea(cv, phase=0.0, x0=0, x1=W - 1):
    night_sea(cv, HOR, 205, moon_x=MOON[0], seed=4, phase=phase, x0=x0, x1=x1, calm=1.3)
    # vist de dalt: el mar, a prop (a baix), més fosc i amb escuma que es trenca
    for y in range(HOR + 40, 206):
        for x in range(x0, x1 + 1):
            cv.flat(x, y, mix(cv.get(x, y), (2, 4, 8), min(0.5, (y - HOR - 40) / 140)))
            n = fbm((x + phase * 3) / 9, y / 3.5, 77)
            if n > 0.74:
                cv.flat(x, y, mix(cv.get(x, y), (150, 166, 170), (n - 0.74) * 1.6))


BOW = (54, 132)        # la punta de la proa (lluny, cap a l'horitzó)


def arenga_below(cv, phase=0.0, lights=True):
    """La proa de l'Arenga vista de dalt del pal: la coberta, la borda blanca amb la línia vermella, el molinet,
    la balsa i dos llums de coberta. L'escuma de la roda."""
    bx, by = BOW
    # el solc d'escuma a banda i banda de la roda
    for side in (-1, 1):
        for i in range(70):
            t = i / 70
            x = bx + side * (6 + t * 42) + round(math.sin(i * 0.7 + phase * 2) * 1.5)
            y = by + 2 + t * 70
            for k in range(3):
                if hr(i, k, side, int(phase * 4) % 4) > 0.35:
                    cv.flat(x + side * k, y + k, mix(cv.get(x + side * k, y + k), (170, 186, 190), 0.6 - k * 0.15))
    # el casc: de la roda (lluny) cap a nosaltres (s'eixampla)
    hull = [(bx, by), (bx + 34, by + 36), (bx + 52, 206), (bx - 44, 206), (bx - 28, by + 36)]
    cv.poly(hull, MASTW, lambda x, y: 3.0 + (y - by) * 0.006, lit=0)
    # la borda (regala blanca) i, a dins, la coberta verd grisosa
    deck = [(bx, by + 6), (bx + 29, by + 37), (bx + 45, 206), (bx - 38, 206), (bx - 24, by + 37)]
    cv.poly(deck, DECKX, lambda x, y: 2.0 + (hr(x // 3, y // 2) - 0.5) * 0.5, lit=0)
    # la línia vermella, de fora
    for (ax, ay), (cx, cy) in ((hull[0], hull[1]), (hull[1], hull[2]), (hull[0], hull[4]), (hull[4], hull[3])):
        n = max(abs(cx - ax), abs(cy - ay))
        for i in range(n + 1):
            x = ax + (cx - ax) * i / n
            y = ay + (cy - ay) * i / n
            off = 2 if cx > ax else -2
            cv.put(round(x + off * 0.5), round(y + 1), REDH, 3.4, lit=0)
    # el molinet de l'àncora i les cadenes
    cv.rect(bx - 6, by + 22, bx + 6, by + 27, DECKX, 4.0, lit=0)
    cv.disc(bx - 6, by + 24, 2, 3, DECKX, 5.0, lit=0)
    cv.disc(bx + 6, by + 24, 2, 3, DECKX, 5.0, lit=0)
    cv.line(bx - 2, by + 21, bx - 1, by + 10, DECKX, 4.6, lit=0)
    cv.line(bx + 2, by + 21, bx + 1, by + 10, DECKX, 4.6, lit=0)
    # l'escotilla de la caixa de cadenes i la balsa salvavides (contenidor blanc)
    cv.rect(bx - 10, by + 36, bx - 2, by + 41, DECKX, 3.2, lit=0)
    cv.disc(bx + 14, by + 46, 6, 4, MASTW, lambda nx, ny: 4.2 - ny * 1.2, lit=0)
    cv.hline(bx + 9, bx + 19, by + 46, MASTW, 2.4, lit=0)
    # el pal de proa i la seva ombra
    cv.vline(bx, by + 4, by + 14, MASTW, 4.4, lit=0)
    if not lights:                                           # el generador parat: la proa a les fosques
        cv.flat(bx, by + 3, (60, 58, 56))
        return
    # dos llums de coberta (grocs), amb el seu cercle a terra
    for lx, ly in ((bx - 12, by + 54), (bx + 20, by + 62)):
        for y in range(ly - 8, ly + 9):
            for x in range(lx - 16, lx + 17):
                d = math.hypot((x - lx) / 16, (y - ly) / 8)
                if d < 1:
                    o = cv.get(x, y)
                    cv.flat(x, y, mix(o, (200, 160, 80), 0.32 * (1 - d) ** 1.4))
        cv.flat(lx, ly - 2, (255, 236, 180))
        glow(cv, lx, ly - 2, 5, GLOW_WARM, 0.6)
    # el llum de navegació de proa (blanc, al pal)
    cv.flat(bx, by + 3, (255, 250, 230))
    glow(cv, bx, by + 3, 5, (255, 250, 230), 0.6)


# ─── El pal, la creueta i la bandera ───────────────────────────────────────

def mast(cv, lights=True):
    # el pal: tub blanc, amb les juntes i els graons soldats (la mateixa escala que puja de coberta)
    for y in range(0, FLOOR_Y + 2):
        for x in range(MAST_X - 7, MAST_X + 8):
            u = (x - MAST_X) / 7.5
            cv.put(x, y, MASTW, 4.6 + 1.6 * (-0.15 - u) - 1.0 * u * u + (hr(x // 2, y // 5) - 0.5) * 0.25)
    for sy in (38, 112):                                     # juntes amb brida
        box(cv, MAST_X - 9, sy, MAST_X + 9, sy + 3, MASTW, 4.4)
        for bx in range(MAST_X - 7, MAST_X + 8, 4):
            bolt(cv, bx, sy + 1, MASTW, 4.8)
    # els graons (U de rodó) al costat esquerre
    for y in range(10, FLOOR_Y - 4, 9):
        cv.hline(MAST_X - 13, MAST_X - 7, y, MASTW, 5.2)
        cv.vline(MAST_X - 13, y, y + 2, MASTW, 3.4)
        cv.hline(MAST_X - 13, MAST_X - 7, y + 1, MASTW, 2.0)
    # ratlles de rovell
    for i in range(6):
        x = MAST_X - 5 + int(hr(i, 61) * 10)
        y0 = 40 + int(hr(i, 62) * 90)
        for y in range(y0, y0 + 6 + int(hr(i, 63) * 10)):
            if hr(x, y, 64) > 0.25:
                cv.flat(x, y, mix(cv.get(x, y), (120, 60, 30), 0.4))
    # la creueta (a dalt de tot), amb les drisses
    box(cv, MAST_X - 70, 16, MAST_X + 70, 20, MASTW, 4.4, grad=0.4)
    for bx in range(MAST_X - 66, MAST_X + 70, 10):
        bolt(cv, bx, 17, MASTW, 4.8)
    for cx in (MAST_X - 70, MAST_X + 70):                    # tirants
        cv.line(cx, 20, MAST_X - 7 if cx < MAST_X else MAST_X + 7, 34, MASTW, 3.0)
    # llums de navegació a la creueta: dos blancs de tope i el vermell/blanc de «sense govern» apagats
    for lx in (MAST_X - 50, MAST_X + 50):
        box(cv, lx - 3, 9, lx + 3, 15, CAB, 3.0)
        cv.disc(lx, 11, 2, 2, [(80, 30, 26), (140, 50, 40)], 0.6, lit=0)
    # el focus de coberta, mirant la plataforma
    fx, fy = LAMP_XY
    box(cv, fx - 9, fy - 6, fx + 9, fy + 2, CAB, 3.2)
    cv.hline(fx - 9, fx + 9, fy - 6, CAB, 4.6)
    cv.rect(fx - 3, fy - 10, fx + 3, fy - 7, CAB, 2.2)
    cv.rect(fx - 8, fy + 3, fx + 8, fy + 4, LAMP if lights else CAB, 2.6 if lights else 1.6, lit=0)
    for gx in range(fx - 7, fx + 8, 3):                      # reixeta
        cv.put(gx, fy + 3, CAB, 2.0, lit=0)


def flag(cv, t=0):
    """La bandera de Mar Obert (blanca, amb el cercle vermell), a la drissa de la creueta, batent cap a l'esquerra."""
    hx = MAST_X - 60                                         # on penja la drissa
    top = 22
    w, h = 34, 20
    # drissa (fins a la bandera i després avall, en panxa pel vent)
    cv.vline(hx, 20, top, ROPEW, 3.0)
    pts = []
    for i in range(w + 1):
        k = i / w
        dy = math.sin(i * 0.38 - t * 1.4) * (1.0 + k * 3.2)
        pts.append((hx - i, top + dy))
    for i, (x, y) in enumerate(pts):
        k = i / w
        hh = h * (1 - k * 0.12)
        slope = pts[min(i + 1, w)][1] - pts[max(i - 1, 0)][1]
        for j in range(int(hh) + 1):
            yy = y + j
            lvl = 7.4 - slope * 1.4 - j * 0.04
            # l'extrem, esfilagarsat
            if k > 0.86 and hr(i, j, 5) < (k - 0.86) * 5:
                continue
            # el cercle vermell de Mar Obert, al mig
            d = math.hypot(i - w * 0.42, j - hh * 0.5)
            if 3.2 < d < 6.6:
                cv.put(round(x), round(yy), FLAGR, 4.4 - slope * 1.0, lit=0.4)
            else:
                cv.put(round(x), round(yy), MASTW, lvl, lit=0.4)
    cv.line(hx, top + h, hx + 4, top + h + 30, ROPEW, 2.6)


# ─── L'antena del satèl·lit ────────────────────────────────────────────────

def antenna(cv):
    cx = ANT_X
    # el pedestal: tub amb brides, dret sobre la plataforma
    vpipe(cv, cx, 104, FLOOR_Y + 2, 5, MASTW, 4.4)
    for y in (126, FLOOR_Y - 2):
        box(cv, cx - 9, y, cx + 9, y + 3, MASTW, 4.0)
        for bx in range(cx - 7, cx + 8, 5):
            bolt(cv, bx, y + 1, MASTW, 4.6)
    # la caixa del pedestal (el motor que l'orienta) amb el pilot i el cable que baixa
    box(cv, cx - 12, 110, cx + 12, 124, MASTW, 4.2, grad=0.8)
    cv.flat(cx + 7, 114, (255, 120, 40))                    # pilot ambre: desorientada
    glow(cv, cx + 7, 114, 4, (255, 140, 60), 0.5)
    for x in range(cx - 9, cx + 4, 3):                       # reixeta
        cv.vline(x, 116, 121, MASTW, 2.6)
    cv.line(cx + 12, 120, cx + 16, 132, CAB, 2.0)
    cv.line(cx + 16, 132, cx + 18, FLOOR_Y, CAB, 2.0)
    # el collar giratori, amb les mordasses
    box(cv, cx - 20, 100, cx + 20, 108, MASTW, 4.0)
    cv.hline(cx - 20, cx + 20, 100, MASTW, 5.4)
    for bx in range(cx - 17, cx + 18, 6):
        bolt(cv, bx, 104, MASTW, 4.6)
    # la cúpula (radom) de fibra, blanca, amb les costures i la brutícia de la sal
    rx, ry, dy = 30, 38, 100
    for y in range(dy - ry, dy + 1):
        for x in range(cx - rx, cx + rx + 1):
            nx, ny = (x - cx) / rx, (y - dy) / ry
            if nx * nx + ny * ny <= 1:
                nz = math.sqrt(max(0.0, 1 - nx * nx - ny * ny))
                lvl = 2.6 + 2.6 * (0.35 * nx - 0.55 * ny + 0.6 * nz) + 1.6 * nz
                if abs(x - cx) == 0 or abs(ny + 0.5) < 0.02:
                    lvl -= 0.6                                # costures
                if y > dy - 6:
                    lvl -= 0.8                                # el faldó, a l'ombra
                if hr(x // 2, y // 3, 71) > 0.94 and ny > -0.6:
                    lvl -= 0.7                                # taques de sal
                cv.put(x, y, DOME, lvl, lit=0.7)
    cv.hline(cx - rx, cx + rx, dy - 6, DOME, 3.6, lit=0.5)
    # reflex de la lluna a dalt a l'esquerra
    for x, y in ((cx - 14, dy - 30), (cx - 12, dy - 31), (cx - 16, dy - 28)):
        cv.flat(x, y, (240, 238, 228))
    # l'adhesiu del fabricant (sense text) i la fletxa de proa
    box(cv, cx - 6, dy - 20, cx + 6, dy - 16, DOME, 6.4, edge=False)
    cv.hline(cx - 4, cx + 4, dy - 18, DOME, 4.0)
    cv.poly([(cx, dy - 4), (cx - 3, dy - 1), (cx + 3, dy - 1)], YELL, 3.6)


def knot(cv):
    """El nus Bastida: el cap passa dues voltes al collar (una de més), fa el nus i va a la barana."""
    cx = ANT_X
    # dues voltes al collar
    for k, y in enumerate((102, 105)):
        for x in range(cx - 20, cx + 21):
            ph = (x + k * 2) % 4
            cv.put(x, y + (1 if ph < 2 else 0), ROPEW, 3.6 - abs(ph - 1.5) * 0.4)
    # el nus, gros, a la dreta del collar
    cv.disc(cx + 20, 104, 4, 4, ROPEW, lambda nx, ny: 3.8 - nx * 0.8 - ny * 1.2)
    cv.disc(cx + 19, 103, 2, 2, ROPEW, 2.2)
    cv.put(cx + 22, 102, ROPEW, 1.4)
    # el cap tens fins a la barana i el xicotet que sobra, penjant
    cv.line(cx + 23, 106, 300, 116, ROPEW, 3.4)
    cv.line(cx + 23, 107, 300, 117, ROPEW, 2.0)
    for i, y in enumerate(range(108, 120)):
        cv.put(cx + 18 + round(math.sin(i * 0.8) * 1.2), y, ROPEW, 3.0)


# ─── La plataforma i la barana ─────────────────────────────────────────────

def platform(cv):
    """La reixa de la plataforma, en perspectiva, amb la vora de planxa al davant i la de l'esquerra."""
    for y in range(FLOOR_Y, 206):
        xl = plat_left(y)
        d = y - VP[1]
        for x in range(int(math.ceil(xl)), W):
            u = VP[0] + (x - VP[0]) * 110 / d
            v = 2200 / d
            lvl = 2.0
            # reixa: barres portants (en perspectiva) i travessers
            bar = (u % 6) < 1.2
            cross = (v % 3.4) < 0.9
            if bar and cross:
                lvl = 4.6
            elif bar:
                lvl = 3.9
            elif cross:
                lvl = 3.1
            else:
                lvl = 1.0                                    # el buit: a sota, la nit
            cv.put(x, y, GRATE, lvl + (hr(x // 3, y // 2, 81) - 0.5) * 0.3)
        # la vora de planxa a l'esquerra (cantell)
        for k in range(3):
            cv.put(xl + k, y, MASTW, 3.6 - k * 0.6)
    # la vora del darrere (sòcol de planxa contra el pal)
    for x in range(PLAT_L, W):
        cv.put(x, FLOOR_Y, MASTW, 2.4)
        cv.put(x, FLOOR_Y + 1, MASTW, 3.2)
    # sòcol de peu (planxa baixa, vertical) a la vora esquerra
    for y in range(FLOOR_Y, 206):
        xl = plat_left(y)
        hgt = round(6 * scale(y))
        for k in range(hgt):
            cv.put(xl - 1, y - k, MASTW, 2.8)


def hatch(cv):
    """La boca de l'escala: un forat a la reixa amb el marc, la tapa aixecada i els dos passamans de l'escala."""
    x0, y0, x1, y1 = HATCH
    # el forat: a baix, l'escala que s'enfonsa en la foscor i una mica de llum del pont
    cv.poly([(x0 + 4, y0), (x1 - 4, y0), (x1, y1), (x0, y1)], DARK, lambda x, y: 0.6 + (y - y0) * 0.05, lit=0.2)
    for y in range(y0 + 4, y1, 5):                          # els esglaons, avall
        xa, xb = x0 + 14, x1 - 14
        cv.hline(xa + (y - y0) // 6, xb - (y - y0) // 6, y, MASTW, 2.2 - (y - y0) * 0.02, lit=0.4)
    cv.vline(x0 + 13, y0 + 2, y1 - 1, MASTW, 2.6, lit=0.4)
    cv.vline(x1 - 13, y0 + 2, y1 - 1, MASTW, 2.6, lit=0.4)
    glow(cv, (x0 + x1) // 2, y1 - 2, 14, (200, 60, 50), 0.25)     # el llum vermell de nit del pont
    # el marc (planxa)
    for (ax, ay), (bx, by) in (((x0 + 4, y0), (x1 - 4, y0)), ((x1 - 4, y0), (x1, y1)),
                               ((x1, y1), (x0, y1)), ((x0, y1), (x0 + 4, y0))):
        cv.line(ax, ay, bx, by, YELL, 3.2)
        cv.line(ax, ay + 1, bx, by + 1, MASTW, 2.4)
    # la tapa de reixa, aixecada contra la barana del darrere (vertical, de cantó)
    cv.poly([(x0 + 6, y0 - 1), (x1 - 6, y0 - 1), (x1 - 8, y0 - 30), (x0 + 8, y0 - 30)], GRATE,
            lambda x, y: 3.4 if (x % 4 == 0 or y % 4 == 0) else 1.2)
    cv.hline(x0 + 8, x1 - 8, y0 - 30, MASTW, 4.0)
    cv.hline(x0 + 6, x1 - 6, y0 - 1, MASTW, 3.0)
    # els passamans: dues nanses que surten del forat
    for hx in (x0 + 12, x1 - 12):
        for y in range(y0 - 20, y0 + 6):
            cv.put(hx, y, MASTW, 5.0)
            cv.put(hx + 1, y, MASTW, 3.4)
        for k in range(5):                                   # la corba de dalt
            ang = math.pi * k / 4
            cv.put(hx + round((1 - math.cos(ang)) * 2) * (1 if hx < (x0 + x1) // 2 else -1),
                   y0 - 20 - round(math.sin(ang) * 2), MASTW, 5.2)
    # franges grogues i negres de perill a la tapa
    for y in range(y0 - 28, y0 - 24):
        for x in range(x0 + 9, x1 - 9):
            cv.put(x, y, YELL if ((x + y) // 3) % 2 else DARK, 3.6)


RAIL_TOP = 104         # la barana del darrere (≈ 1 m)


def rail_back(cv):
    """La barana del darrere: tres tubs blancs i els puntals, d'una banda a l'altra de la plataforma."""
    for ry, r, lvl in ((RAIL_TOP, 2, 5.0), (RAIL_TOP + 16, 1, 4.4), (RAIL_TOP + 31, 1, 4.0)):
        hpipe(cv, PLAT_L, W - 1, ry, r, MASTW, lvl)
    for px in list(range(PLAT_L + 2, W, 38)):
        vpipe(cv, px, RAIL_TOP - 1, FLOOR_Y, 2, MASTW, 4.4)
        cv.disc(px, RAIL_TOP - 1, 2.5, 1.5, MASTW, 5.4)
    # el sòcol de planxa al peu (per on no cau res)
    for x in range(PLAT_L, W):
        for y in range(FLOOR_Y - 7, FLOOR_Y):
            cv.put(x, y, MASTW, 3.4 - (y - FLOOR_Y + 7) * 0.12)
        cv.put(x, FLOOR_Y - 7, MASTW, 4.8)
    # un salvavides lligat a la barana, a la dreta
    rx, ry = 446, 122
    for y in range(ry - 9, ry + 10):
        for x in range(rx - 9, rx + 10):
            d = math.hypot(x - rx, y - ry)
            if 4.5 <= d <= 9:
                a = math.degrees(math.atan2(y - ry, x - rx)) % 360
                band = int((a + 22) // 45) % 2
                u = (d - 6.75) / 2.25
                cv.put(x, y, MASTW if band else [(40, 12, 6), (84, 26, 10), (140, 48, 16), (196, 80, 26),
                                                  (232, 118, 44), (250, 164, 90)],
                       (5.0 if band else 3.2) - u * 0.8 - (y - ry) / 9 * 0.8)


def rail_left(cv):
    """La barana del costat esquerre, en perspectiva (cap a nosaltres): puntals i tres tubs."""
    posts = [FLOOR_Y, 170, 196]
    tops = []
    for y in posts:
        x = plat_left(y) + 1
        s = scale(y)
        h = (FLOOR_Y - RAIL_TOP) * s
        tops.append((x, y, h, s))
        r = 2 if s > 1.2 else 1
        for yy in range(int(y - h), y + 1):
            for dx in range(-r, r + 1):
                cv.put(x + dx, yy, MASTW, 4.6 - dx * 0.8)
        cv.disc(x, y - h, r + 0.5, 1.2, MASTW, 5.4)
    for frac, lvl in ((1.0, 5.0), (0.65, 4.4), (0.32, 4.0)):
        pts = [(x, y - h * frac) for x, y, h, s in tops]
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            n = int(max(abs(bx - ax), abs(by - ay))) + 1
            for i in range(n + 1):
                t = i / n
                x, y = ax + (bx - ax) * t, ay + (by - ay) * t
                cv.put(round(x), round(y), MASTW, lvl + 0.6)
                cv.put(round(x), round(y) + 1, MASTW, lvl - 1.2)
                if frac == 1.0:
                    cv.put(round(x), round(y) + 2, MASTW, lvl - 2.0)


def cable_tray(cv):
    """El cable de l'antena i el del focus, que baixen pel pal dins d'una canaleta."""
    for x in (MAST_X + 9, MAST_X + 11):
        cv.vline(x, 40, FLOOR_Y, CAB, 2.4 if x == MAST_X + 9 else 1.4)
    for y in range(46, FLOOR_Y, 14):
        cv.hline(MAST_X + 8, MAST_X + 12, y, MASTW, 4.0)
    # i el de l'antena va del pal al pedestal per sota de la barana
    cv.line(MAST_X - 7, 140, ANT_X + 18, 146, CAB, 1.8)


# ─── Muntatge ───────────────────────────────────────────────────────────────

def _scene(cv, t=0, phase=0.0, flag_on=True, lights=True):
    sky(cv)
    sea(cv, phase)
    arenga_below(cv, phase, lights)
    # boira de l'altura sobre el mar d'allà baix (dona profunditat)
    cv.tint(0, HOR + 30, W - 1, 205, (20, 26, 36), lambda x, y: min(0.3, (y - HOR - 30) / 300))
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
    # el focus: con de llum (molt subtil, amb l'aire humit) i resplendor
    fx, fy = LAMP_XY
    for y in range(fy + 5, FLOOR_Y + 40):
        wdt = (y - fy) * 0.75
        for x in range(int(fx - wdt), int(fx + wdt) + 1):
            if 0 <= x < W:
                k = 0.10 * (1 - abs(x - fx) / max(1, wdt)) * (1 - (y - fy) / 130)
                if k > B4[y & 3][x & 3] * 0.2:
                    cv.flat(x, y, mix(cv.get(x, y), (255, 214, 140), k))
    # el cercle de llum a la reixa, sota el focus
    cv.tint(PLAT_L, FLOOR_Y, W - 1, 205, (255, 200, 120),
            lambda x, y: 0.16 * max(0.0, 1 - math.hypot((x - fx) / 120, (y - 172) / 26)) ** 1.5)
    glow(cv, fx, fy + 4, 22, GLOW_WARM, 0.55)
    glow(cv, fx, fy + 4, 8, (255, 244, 210), 0.7)


def bg(cv):
    _scene(cv)


# ─── Animacions ─────────────────────────────────────────────────────────────

_BASE = {}


def _base():
    if 'img' not in _BASE:
        cv = Canvas(light=LIGHT)
        bg(cv)
        _BASE['img'] = cv.img
    return _BASE['img']


FLAG_BOX = (MAST_X - 100, 14, MAST_X - 52, 56)


def _frames_vent():
    """La bandera que bat i ratxes d'esquitxos que travessen la pantalla."""
    base = _base()
    # el cel sense bandera (per esborrar-la a cada fotograma)
    clean = Canvas(light=LIGHT)
    sky(clean)
    sea(clean)
    mast(clean)
    frames = []
    n = 8
    x0, y0, x1, y1 = FLAG_BOX
    for i in range(n):
        cv = Canvas(light=LIGHT, img=base.copy())
        # esborra la bandera: torna a posar el cel (i el pal, la creueta) del rectangle
        reg = clean.img.crop((x0, y0, x1 + 1, y1 + 1))
        cv.img.paste(reg, (x0, y0))
        cv.P = cv.img.load()
        mast_patch(cv)
        flag(cv, t=i * (2 * math.pi / 1.4) / n)
        # ratxes d'esquitxos (de dreta a esquerra, molt ràpides)
        for k in range(5):
            sx = (W + 40) - ((i * 61 + k * 97) % (W + 80))
            sy = 30 + int(hr(k, 3) * 150)
            ln = 6 + int(hr(k, 4) * 8)
            for j in range(ln):
                x = sx + j
                if 0 <= x < W:
                    cv.flat(x, sy + j // 5, mix(cv.get(x, sy + j // 5), (180, 196, 206), 0.35 * (1 - j / ln)))
        frames.append(_diff(cv.img, base))
    return frames


def mast_patch(cv):
    """Torna a dibuixar la creueta i la drissa sobre el retall (la bandera hi penja a sota)."""
    box(cv, MAST_X - 70, 16, MAST_X + 70, 20, MASTW, 4.4, grad=0.4)
    for bx in range(MAST_X - 66, MAST_X + 70, 10):
        bolt(cv, bx, 17, MASTW, 4.8)
    cv.line(MAST_X - 70, 20, MAST_X - 7, 34, MASTW, 3.0)
    lx = MAST_X - 50
    box(cv, lx - 3, 9, lx + 3, 15, CAB, 3.0)
    cv.disc(lx, 11, 2, 2, [(80, 30, 26), (140, 50, 40)], 0.6, lit=0)


SEA_BOX = (0, HOR + 1, PLAT_L - 1, 205)


def _frames_mar():
    """Les onades d'allà baix, que corren; l'escuma de la roda."""
    base = _base()
    frames = []
    x0, y0, x1, y1 = SEA_BOX
    for i in range(6):
        cv = Canvas(light=LIGHT)
        ph = i * 1.6
        sea(cv, ph, x0=0, x1=PLAT_L + 50)
        arenga_below(cv, ph)
        cv.tint(0, HOR + 30, PLAT_L + 50, 205, (20, 26, 36), lambda x, y: min(0.3, (y - HOR - 30) / 300))
        out = base.copy()
        # només la part del mar que es veu (a l'esquerra de la plataforma i de la barana)
        src, dst, b = cv.img.load(), out.load(), base.load()
        for y in range(y0, y1 + 1):
            xl = plat_left(max(y, FLOOR_Y)) - 3 if y >= FLOOR_Y else PLAT_L - 3
            for x in range(x0, int(min(x1, xl))):
                if _is_open(x, y):
                    dst[x, y] = src[x, y]
        frames.append(_diff(out, base))
    return frames


def _is_open(x, y):
    """Fora de la barana de l'esquerra (els tubs i els puntals no es toquen)."""
    # deixem 3 px de marge al voltant dels tubs i els puntals
    for frac in (1.0, 0.65, 0.32):
        # la recta del tub, de (plat_left(150), 150 - 46*frac) a (plat_left(196), 196 - 46*s*frac)
        xa, ya = plat_left(FLOOR_Y) + 1, FLOOR_Y - (FLOOR_Y - RAIL_TOP) * frac
        xb, yb = plat_left(196) + 1, 196 - (FLOOR_Y - RAIL_TOP) * scale(196) * frac
        if min(xa, xb) - 3 <= x <= max(xa, xb) + 3:
            t = (x - xa) / (xb - xa) if xb != xa else 0
            ty = ya + (yb - ya) * t
            if abs(y - ty) <= 3:
                return False
    for yy in (FLOOR_Y, 170, 196):
        px = plat_left(yy) + 1
        if abs(x - px) <= 4 and y <= yy + 1 and y >= yy - (FLOOR_Y - RAIL_TOP) * scale(yy) - 3:
            return False
    return True


ANIMS = {'vent': {'frames': _frames_vent, 'frameDuration': 110},
         'mar': {'frames': _frames_mar, 'frameDuration': 260}}

# ─── El generador parat (Escena 9) ─────────────────────────────────────────

# sense el focus, només la lluna
LIGHT_FOSC = Light(ambient=-0.7, vignette=(40, 14), floor_fade=None)
LIGHT_FOSC.point(ANT_X, 60, r=60, k=0.5, power=2.0)
LIGHT_FOSC.point(MOON[0], MOON[1], r=420, k=0.5, power=1.2)


def fosc(cv):
    """Decorat `fosc`: el focus, el llum de tope i els llums de la proa, apagats. On hi ha animacions (la
    bandera, el mar d'allà baix) és una capa negra semitransparent, perquè es continuïn movent; la resta, el
    dibuix a les fosques."""
    base = _base()
    dark = Canvas(light=LIGHT_FOSC)
    _scene(dark, lights=False)
    # els llums de la proa: on canvia la proa amb llums i sense (amb la mateixa llum), va opac
    on, off = Canvas(light=LIGHT), Canvas(light=LIGHT)
    arenga_below(on)
    arenga_below(off, lights=False)
    pb, pd, pon, poff, o = base.load(), dark.img.load(), on.img.load(), off.img.load(), cv.P
    fx0, fy0, fx1, fy1 = FLAG_BOX
    for y in range(H):
        for x in range(W):
            anim = (fx0 <= x <= fx1 and fy0 <= y <= fy1) or (y >= SEA_BOX[1] and x < PLAT_L + 50 and _is_open(x, y)
                                                              and x < (plat_left(max(y, FLOOR_Y)) - 3))
            if anim and pon[x, y] == poff[x, y]:
                lb = sum(pb[x, y][:3]) + 1
                a = max(0.0, min(1.0, 1 - sum(pd[x, y][:3]) / lb))
                if a > 0.02:
                    o[x, y] = (0, 0, 0, int(a * 255))
            elif pd[x, y] != pb[x, y]:
                o[x, y] = pd[x, y]


PROPS = {'fosc': fosc}


# ─── Geometria ─────────────────────────────────────────────────────────────

def _t(x0, y0, x1, y1, wx=None, wy=184):
    return {'rect': (x0, y0, x1, y1), 'walk': (wx if wx is not None else (x0 + x1) // 2, wy)}


GEOMETRIA = {
    'things': {
        'escala': _t(HATCH[0], HATCH[1] - 30, HATCH[2], HATCH[3] + 2, wx=420, wy=192),
        'antena': _t(ANT_X - 31, 60, ANT_X + 31, FLOOR_Y, wy=172),
        'mar': _t(2, HOR + 4, 150, 192, wx=182, wy=184),
    },
    'spawns': {'iri': (262, 188), 'vet': (300, 192), 'marcel': (339, 166)},
    'walkable': [(178, 164), (470, 164), (476, 198), (168, 198)],
}
