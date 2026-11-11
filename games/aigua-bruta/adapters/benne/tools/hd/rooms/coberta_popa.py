"""
La coberta de popa de l'Arenga. Mirem a estribord: la popa és a l'esquerra, la proa a la dreta.
  - a l'esquerra, la grua de popa (groga) amb la zòdiac de la nit penjada i trincada a la borda;
  - al fons, la borda blanca amb la regala vermella, i per sobre el mar i el cel de febrer;
  - a la dreta, la caseta: la porta estanca del menjador (amb llum càlida a l'ull de bou) i, sota la
    coberta de botes, el pas lateral cap a proa;
  - de nit (per defecte), focus de coberta grocs; de dia (decorat `dia`, Escenes 2 i 3), sol fred de febrer.
Props: `plataforma` (de dia, a una milla), `taula` (l'esmorzar), `horitzo` (l'estela, de l'Escena 3 en endavant).
"""
import math

from hd.pix import Light, W, hr, mix
from hd.rooms.arenga import YELL, REDP
from hd.rooms.exterior import (night_sky, night_sea, day_sky, day_sea, platform, stain, gull, deck_floor,
                               bulwark, wt_door, deck_lamp, lifebuoy, coil, bitts, smooth, fbm,
                               HULLN, STEELX, CABX, DECKX, ORANGEB, ROPE, LAMP, WINDOW, GLOW_WARM, TAPE)

HOR = 86            # l'horitzó
RAIL = 106          # la regala de la borda
FLOOR_Y = 152
HOUSE = (370, 451)  # la caseta (porta del menjador)
DOOR = (396, 72, 438, 152)

LIGHT = Light(ambient=-0.1, vignette=(50, 24), floor_fade=(198, 30))
LIGHT.point(417, 60, r=200, k=3.2, squash=1.1, down=True, power=1.4)      # focus sobre la porta
LIGHT.point(52, 50, r=170, k=2.6, squash=0.9, down=True, power=1.5)       # focus de la grua
LIGHT.point(466, 30, r=46, k=1.0, power=1.8)                               # llum del pas lateral
LIGHT.point(240, 200, r=260, k=0.6, squash=2.5, power=1.2)                 # rebot de la coberta

# De dia: sol baix de febrer per l'esquerra (popa), llum freda i plana; ombra sota la coberta de botes.
LIGHT_DAY = Light(ambient=3.4, vignette=(40, 18), floor_fade=(200, 40))
LIGHT_DAY.point(60, -40, r=420, k=1.3, power=1.2)
LIGHT_DAY.add(lambda x, y: -1.6 if (x > 452 and 22 <= y < 160) else 0.0)


# ─── Cel i mar ──────────────────────────────────────────────────────────────

def sky_sea(cv, day):
    if day:
        day_sky(cv, 0, HOR, seed=12, sun=(40, 20))
        day_sea(cv, HOR, RAIL + 4, sun_x=60)
    else:
        night_sky(cv, 0, HOR, moon=(300, 26), seed=4, clouds=0.55)
        night_sea(cv, HOR, RAIL + 4, moon_x=300)


# ─── La popa: el pal de la llum de popa ────────────────────────────────────

def stern(cv, day):
    # pal de la bandera/llum, a tocar de la popa
    for y in range(64, RAIL + 2):
        cv.put(8, y, STEELX, 4.6)
        cv.put(9, y, STEELX, 3.0)
    cv.rect(5, 60, 12, 64, CABX, 3.4)
    if not day:
        cv.disc(8, 58, 2, 2, LAMP, 3.2, lit=0)
        cv.glow(8, 58, 10, (255, 248, 224), 0.6)
    else:
        cv.disc(8, 58, 2, 2, CABX, 5.0)


# ─── La grua i la zòdiac ───────────────────────────────────────────────────

def crane(cv, day):
    # el peu: cilindre groc amb brida i reblons
    for y in range(44, FLOOR_Y + 6):
        for x in range(28, 45):
            u = (x - 36) / 8.5
            cv.put(x, y, YELL, 2.4 - u * 1.3 - u * u * 0.8 - (0.6 if y > FLOOR_Y - 6 else 0))
    cv.rect(24, FLOOR_Y + 3, 48, FLOOR_Y + 7, STEELX, 2.6)
    cv.hline(24, 48, FLOOR_Y + 3, STEELX, 4.0)
    for bx in range(26, 48, 5):
        cv.put(bx, FLOOR_Y + 5, STEELX, 4.6)
    cv.rect(25, 50, 47, 55, STEELX, 2.6)                                  # la corona de gir
    cv.hline(25, 47, 50, STEELX, 4.0)
    # el cap de la grua (la caixa dels motors)
    cv.poly([(24, 36), (50, 36), (52, 50), (24, 50)], YELL, lambda x, y: 3.0 - (y - 36) * 0.06 - (x - 24) * 0.02)
    cv.hline(24, 50, 36, YELL, 4.4)
    cv.rect(27, 40, 34, 44, STEELX, 1.6)                                  # reixeta
    for yy in (41, 43):
        cv.hline(28, 33, yy, STEELX, 3.0)
    # cartell petit de càrrega
    cv.rect(38, 40, 47, 45, HULLN, 5.4)
    cv.hline(39, 46, 42, STEELX, 1.4)
    # el braç: biga groga de 6 px que puja cap a la dreta
    ax, ay, bx, by = 42, 40, 140, 22

    def along(t):
        return ax + (bx - ax) * t, ay + (by - ay) * t
    n = 220
    for i in range(n + 1):
        x, y = along(i / n)
        for k in range(-3, 4):
            lvl = 3.2 + (1.2 if k == -3 else 0.6 if k == -2 else -1.2 if k == 3 else -0.4 if k == 2 else 0)
            cv.put(x, y + k, YELL, lvl)
    for t in (0.25, 0.5, 0.75):                                          # plaques de reforç
        x, y = along(t)
        cv.rect(x - 1, y - 2, x + 1, y + 2, YELL, 1.8)
    # el cilindre hidràulic
    for k, lv in ((0, 2.4), (1, 4.2), (2, 3.0)):
        cv.line(45 + k, 76, 66 + k, 40, STEELX, lv)
    for k, lv in ((0, 5.0), (1, 6.0)):
        cv.line(56 + k, 58, 66 + k, 40, STEELX, lv)
    cv.disc(46, 77, 2, 2, STEELX, 3.6)
    # la politja de la punta i el cable
    cv.disc(139, 24, 3, 3, STEELX, lambda nx, ny: 3.6 - nx - ny)
    cv.put(139, 24, STEELX, 1.0)
    for y in range(27, 44):
        cv.put(139, y, CABX, 3.8)
    # el ganxo i les eslingues
    cv.rect(137, 44, 141, 48, STEELX, 3.4)
    cv.put(139, 49, STEELX, 4.2)
    cv.put(140, 50, STEELX, 4.2)
    for tx in (70, 134):
        cv.line(139, 50, tx, 62, ROPE, 3.0)
    if not day:
        cv.rect(46, 46, 56, 49, CABX, 3.0)                                # el focus de la grua
        cv.rect(47, 50, 55, 51, LAMP, 2.6, lit=0)
        cv.glow(51, 52, 14, GLOW_WARM, 0.4)


def zodiac(cv):
    """La zòdiac penjada: flotadors grisos amb una franja taronja, el motor fora borda a popa (esquerra)."""
    x0, x1, yt, yb = 60, 140, 62, 82
    # el casc rígid (a sota)
    cv.poly([(64, 80), (136, 80), (146, 72), (140, 86), (70, 88), (62, 86)], STEELX, lambda x, y: 2.2 - (y - 80) * 0.15)
    # el flotador: un tub llarg amb volum, que s'aixeca a proa (dreta)
    for x in range(x0, x1 + 9):
        t = (x - x0) / (x1 + 8 - x0)
        lift = int(6 * smooth(0.75, 1.0, t))
        r = 7 if x < x1 else max(2, 7 - (x - x1))
        cy = 72 - lift
        for y in range(cy - r, cy + r + 1):
            u = (y - cy) / (r + 0.5)
            lvl = 3.2 - u * 1.6 - u * u * 0.9
            ramp = [(26, 26, 30), (40, 40, 44), (58, 58, 62), (80, 80, 84), (106, 106, 108), (138, 138, 138), (170, 170, 168)]
            if 1 <= y - cy <= 2:
                cv.put(x, y, ORANGEB, 2.6 - u)
            else:
                cv.put(x, y, ramp, lvl)
    # la popa del flotador, tallada, i les manetes
    cv.rect(x0 - 1, 65, x0 + 1, 79, STEELX, 2.0)
    for hx in range(76, 128, 14):
        cv.hline(hx, hx + 5, 67, ROPE, 3.6)
        cv.put(hx, 68, ROPE, 2.6)
        cv.put(hx + 5, 68, ROPE, 2.6)
    # el motor fora borda
    cv.poly([(48, 58), (60, 58), (61, 70), (47, 70)], [(8, 8, 10), (18, 18, 22), (30, 30, 36), (46, 46, 54), (68, 68, 76)],
            lambda x, y: 3.0 - (x - 48) * 0.1 - (y - 58) * 0.08)
    cv.hline(48, 59, 58, [(46, 46, 54), (68, 68, 76), (96, 96, 104)], 2.0)
    cv.rect(52, 70, 55, 92, [(8, 8, 10), (18, 18, 22), (30, 30, 36), (46, 46, 54)], 1.8)
    cv.rect(50, 92, 57, 94, [(8, 8, 10), (18, 18, 22), (30, 30, 36), (46, 46, 54)], 1.4)
    cv.rect(50, 62, 54, 63, ORANGEB, 3.0)
    # les trinques: caps de la zòdiac a la regala, amb el nus
    for (zx, rx) in ((84, 92), (122, 116)):
        cv.line(zx, 84, rx, RAIL, ROPE, 3.0)
        cv.line(zx + 1, 84, rx + 1, RAIL, ROPE, 2.0)
    cv.disc(116, RAIL - 2, 2, 2, ROPE, 3.6)                              # el nus (amb una volta de més)
    cv.disc(119, RAIL - 4, 2, 2, ROPE, 3.2)


# ─── La caseta, la porta i el pas lateral ──────────────────────────────────

def house(cv, day):
    x0, x1 = HOUSE
    # paret blanca amb juntes de planxa i reblons
    for y in range(22, FLOOR_Y):
        for x in range(x0, x1 + 1):
            lvl = 3.0 + (hr(x // 3, y // 5, 61) - 0.5) * 0.25 - (0.7 if y > FLOOR_Y - 10 else 0)
            if x <= x0 + 1:
                lvl -= 1.2
            cv.put(x, y, HULLN, lvl)
    for sy in (48, 112):
        cv.hline(x0 + 2, x1, sy, HULLN, 1.8)
        cv.hline(x0 + 2, x1, sy + 1, HULLN, 4.2)
    for bx in range(x0 + 6, x1, 12):
        cv.put(bx, 50, HULLN, 4.8)
        cv.put(bx, 114, HULLN, 4.8)
    cv.hline(x0, x1, FLOOR_Y - 10, HULLN, 1.4)
    # ratlles de rovell
    for i in range(10):
        rx = x0 + 4 + int(hr(i, 62) * (x1 - x0 - 8))
        if DOOR[0] - 4 <= rx <= DOOR[2] + 4:
            continue
        for y in range(50, 50 + 4 + int(hr(i, 63) * 14)):
            cv.flat(rx, y, mix(cv.get(rx, y), (120, 70, 40), 0.3))
    # cantonada de la caseta (aresta clara)
    cv.vline(x1, 22, FLOOR_Y - 1, HULLN, 4.6)
    cv.vline(x1 + 1, 22, FLOOR_Y - 1, HULLN, 1.4)
    # la porta del menjador
    wt_door(cv, DOOR[0], DOOR[1], DOOR[2], DOOR[3], base=3.4, warm=True)
    # rètol
    cv.rect(404, 62, 430, 67, HULLN, 1.6)
    for i, x in enumerate(range(406, 429, 3)):
        cv.put(x, 64, HULLN, 5.4)
        cv.put(x + 1, 64, HULLN, 5.4)
    deck_lamp(cv, 417, 56, on=not day)
    # un ull de bou de la caseta
    cv.disc(384, 40, 6, 6, CABX, lambda nx, ny: 3.8 - nx - ny)
    if day:
        cv.disc(384, 40, 4, 4, STEELX, lambda nx, ny: 3.4 - ny + (1.6 if nx < -0.2 and ny < -0.2 else 0))
    else:
        cv.disc(384, 40, 4, 4, WINDOW, lambda nx, ny: 2.4 - ny * 0.6, lit=0)
        cv.glow(384, 40, 12, GLOW_WARM, 0.2)
    # el salvavides i la caixa de la mànega
    lifebuoy(cv, 382, 84, 9)
    cv.rect(375, 118, 390, 136, [(40, 10, 10), (80, 18, 16), (130, 30, 26), (170, 48, 38), (206, 78, 56)], 2.4)
    cv.hline(375, 390, 118, REDP, 4.4)
    cv.rect(378, 122, 387, 132, [(40, 10, 10), (80, 18, 16), (130, 30, 26)], 1.2)
    # tub vertical (respirador) a la cantonada
    for y in range(26, FLOOR_Y):
        cv.put(447, y, HULLN, 4.2)
        cv.put(448, y, HULLN, 2.4)
    for y in (40, 90, 130):
        cv.rect(445, y, 449, y + 1, CABX, 3.0)


def boat_deck(cv, day):
    """La coberta de botes, que fa de sostre al pas lateral, amb la barana contra el cel."""
    x0 = HOUSE[0] - 6
    cv.rect(x0, 14, W - 1, 22, HULLN, lambda x, y: 3.6 - (y - 14) * 0.25)
    cv.hline(x0, W - 1, 14, HULLN, 5.0)
    cv.hline(x0, W - 1, 22, HULLN, 1.0)
    cv.rect(x0, 18, W - 1, 19, REDP, 2.6)
    # barana: puntals i dues barres
    for sx in range(x0 + 2, W, 14):
        cv.vline(sx, 0, 13, HULLN, 4.4)
        cv.vline(sx + 1, 0, 13, HULLN, 2.6)
    for ry in (2, 8):
        cv.hline(x0, W - 1, ry, HULLN, 4.6)
        cv.hline(x0, W - 1, ry + 1, HULLN, 2.4)


def side_passage(cv, day):
    """El pas lateral cap a proa: sota la coberta de botes, la borda continua a l'ombra."""
    x0 = HOUSE[1] + 2
    # sota la coberta: el fons, fosc
    for y in range(23, 30):
        for x in range(x0, W):
            cv.put(x, y, HULLN, 1.4 - (y - 23) * 0.05)
    # el puntal de la coberta de botes, a la dreta
    for y in range(22, FLOOR_Y + 2):
        cv.put(474, y, HULLN, 4.0)
        cv.put(475, y, HULLN, 2.8)
        cv.put(476, y, HULLN, 1.4)
    deck_lamp(cv, 464, 30, on=not day)
    # sota el sostre, tot més fosc
    cv.darken(x0, 23, W - 1, FLOOR_Y + 30, lambda x, y: 0.8 if y < FLOOR_Y else 0.6 - (y - FLOOR_Y) / 50, dither=False)


# ─── Coberta i borda ────────────────────────────────────────────────────────

def deck_things(cv, day):
    # una bita doble a la borda, i un rotllo de cap al costat de la grua
    bitts(cv, 254, FLOOR_Y + 2)
    coil(cv, 82, 170, 14, 4)
    # una caixa de cordes (fusta) sota la borda
    cv.rect(300, 132, 340, 154, [(30, 18, 10), (56, 36, 20), (88, 60, 34), (124, 88, 52), (160, 120, 74), (190, 152, 100)], 2.4)
    cv.hline(300, 340, 132, [(56, 36, 20), (124, 88, 52), (190, 152, 100)], 2.0)
    for yy in (139, 146):
        cv.hline(301, 339, yy, [(30, 18, 10), (56, 36, 20)], 1.0)
    cv.rect(316, 136, 324, 140, STEELX, 3.6)
    # una bossa de mostres oblidada? No: una galleda
    cv.rect(212, 140, 222, 154, [(20, 40, 70), (30, 60, 110), (50, 90, 150), (80, 130, 190)], 1.8)
    cv.hline(211, 223, 140, [(30, 60, 110), (80, 130, 190)], 1.8)
    cv.line(212, 139, 217, 134, STEELX, 3.0)
    cv.line(217, 134, 222, 139, STEELX, 3.0)


def draw(cv, day):
    sky_sea(cv, day)
    stern(cv, day)
    bulwark(cv, 0, W - 1, RAIL, FLOOR_Y, base=2.6 if not day else 2.8, scuppers=(150, 280, 456))
    deck_floor(cv, FLOOR_Y, 206)
    deck_things(cv, day)
    zodiac(cv)
    crane(cv, day)
    house(cv, day)
    boat_deck(cv, day)
    side_passage(cv, day)
    if not day:
        cv.glow(417, 172, 46, GLOW_WARM, 0.10)                         # el toll de llum dels focus
        cv.glow(60, 168, 40, GLOW_WARM, 0.08)
    if day:
        # ombres de dia: la caseta damunt la coberta i la grua
        cv.darken(HOUSE[0] - 30, FLOOR_Y, HOUSE[1], FLOOR_Y + 8, lambda x, y: 0.5 if x > HOUSE[0] - 30 + (y - FLOOR_Y) * 3 else 0)
        cv.darken(44, FLOOR_Y + 2, 80, FLOOR_Y + 9, 0.4)


def bg(cv):
    draw(cv, False)


def dia(cv):
    keep = cv.light
    cv.light = LIGHT_DAY
    draw(cv, True)
    cv.light = keep


# ─── Props ──────────────────────────────────────────────────────────────────

def plataforma(cv):
    """A una milla, a estribord: la plataforma, la taca tèrbola i les gavines que no s'hi posen."""
    keep = cv.light
    cv.light = LIGHT_DAY
    # el tros de mar al voltant (per poder-hi pintar la taca)
    day_sea(cv, HOR, 100, x0=150, x1=330)
    stain(cv, 240, HOR + 5, 90, 7, k=1.0)
    for x in range(150, 331):                                         # tornem a posar l'horitzó net a les vores
        if abs(x - 240) > 70:
            cv.P[x, HOR] = cv.P[x, HOR]
    # la vora del mar retallat: barreja suau amb transparència a les vores
    for y in range(HOR, 101):
        for x in range(150, 331):
            e = min(x - 150, 330 - x)
            if e < 12 and hr(x, y, 7) > e / 12:
                cv.P[x, y] = (0, 0, 0, 0)
    platform(cv, 240, HOR + 3, 1.9, 'day')
    for gx, gy in ((214, 34), (232, 28), (262, 38), (250, 24), (276, 30)):
        gull(cv, gx, gy, (226, 228, 224))
    cv.light = keep


def taula(cv):
    """L'esmorzar: taula plegable amb cafè, tasses i croissants."""
    keep = cv.light
    cv.light = LIGHT_DAY
    x0, x1, top = 306, 378, 136
    TOPR = [(60, 60, 58), (96, 94, 90), (134, 132, 124), (170, 166, 156), (200, 196, 184), (226, 222, 210)]
    LEG = STEELX
    # potes plegables (en X)
    for lx in (x0 + 6, x1 - 6):
        cv.line(lx - 4, top + 4, lx + 4, 176, LEG, 3.6)
        cv.line(lx + 4, top + 4, lx - 4, 176, LEG, 2.4)
        cv.rect(lx - 6, 176, lx + 6, 177, LEG, 1.6)
    # el sobre
    cv.rect(x0, top, x1, top + 3, TOPR, lambda x, y: 3.4 - (y - top) * 0.5)
    cv.hline(x0, x1, top, TOPR, 4.8)
    cv.rect(x0, top + 4, x1, top + 5, TOPR, 1.2)
    # el termo
    cv.rect(316, top - 16, 323, top - 1, [(10, 30, 40), (20, 60, 76), (34, 96, 116), (60, 140, 160)], 2.2)
    cv.vline(317, top - 15, top - 2, [(34, 96, 116), (60, 140, 160), (120, 190, 200)], 2.0)
    cv.rect(316, top - 19, 323, top - 17, STEELX, 4.4)
    # tasses
    for mx, c in ((332, ORANGEB), (344, HULLN), (366, [(20, 50, 30), (40, 90, 50), (70, 130, 80), (110, 170, 120)])):
        cv.rect(mx, top - 6, mx + 5, top - 1, c, 2.6 if c is not HULLN else 6.0)
        cv.put(mx + 6, top - 4, c, 2.0 if c is not HULLN else 5.0)
        cv.put(mx + 6, top - 3, c, 2.0 if c is not HULLN else 5.0)
        cv.hline(mx + 1, mx + 4, top - 6, [(30, 16, 8), (60, 34, 16)], 0.8)
    # el plat dels croissants
    cv.disc(355, top - 1, 9, 2, HULLN, 6.6)
    BREAD = [(70, 36, 12), (120, 70, 26), (176, 116, 50), (216, 160, 84), (240, 200, 130)]
    for cx, cy in ((351, top - 4), (359, top - 4), (355, top - 6)):
        cv.disc(cx, cy, 4, 2, BREAD, lambda nx, ny: 2.8 - ny * 1.2 - nx * 0.4)
        cv.put(cx - 1, cy - 1, BREAD, 4.2)
    # unes guants damunt la taula
    cv.rect(372, top - 2, 377, top - 1, [(20, 20, 26), (40, 40, 50), (60, 60, 74)], 1.8)
    cv.light = keep


def horitzo(cv):
    """L'estela: una franja d'escuma que surt de sota la popa (esquerra) i s'aprima cap a l'horitzó."""
    for x in range(150, 344):
        t = (x - 150) / 194                              # 0 a tocar de la popa, 1 lluny
        yc = RAIL - 5 - t * (RAIL - HOR - 9)
        hw = 4.5 * (1 - t) + 0.8
        for y in range(int(yc - hw - 2), int(yc + hw + 3)):
            if not (HOR + 1 <= y < RAIL):
                continue
            d = abs(y - yc) / hw
            n = fbm(x / 10, y / 2.2, 77)
            k = (1 - t) ** 0.7 * (1 - d) + (n - 0.5) * 0.8
            if k > 0.12 + (hr(x, y, 78) - 0.5) * 0.2:
                cv.flat(x, y, mix(cv.get(x, y), (210, 220, 222), min(0.7, k * 0.9)))
    # les dues ones divergents (el solc), més fines
    for x in range(150, 330):
        t = (x - 150) / 180
        for sgn in (-1, 1):
            y = round(RAIL - 5 - t * (RAIL - HOR - 9) + sgn * (5 + 6 * (1 - t)) * (1 - t * 0.5))
            if HOR + 1 <= y < RAIL and hr(x // 2, y, 79) > 0.3 + t * 0.5:
                cv.flat(x, y, mix(cv.get(x, y), (190, 200, 204), 0.5 * (1 - t)))


PROPS = {'dia': dia, 'plataforma': plataforma, 'taula': taula, 'horitzo': horitzo}

# La taula de l'esmorzar tapa les cames de qui hi ha al darrere (la Capitana i en Tomàs).
FRONT = {'mask': lambda x, y: False, 'baseline': 176, 'zIndex': 20, 'props': ('taula',)}

GEOMETRIA = {
    'things': {
        'porta': {'rect': (394, 66, 440, 152), 'walk': (417, 168)},
        'proa': {'rect': (452, 24, 479, 168), 'walk': (468, 174)},
        'grua': {'rect': (22, 20, 148, 158), 'walk': (96, 174)},
        'borda': {'rect': (150, 104, 300, 154), 'walk': (226, 168)},
        'plataforma': {'rect': (204, 26, 278, 92), 'walk': (240, 168)},
        'taula': {'rect': (304, 118, 380, 178), 'walk': (342, 188)},
        'horitzo': {'rect': (150, 88, 340, 105), 'walk': (240, 168)},
    },
    'spawns': {
        'iri': (232, 190), 'vet': (150, 192), 'bastida': (190, 168),
        'capitana': (326, 168), 'tomas': (362, 168), 'nadia': (288, 186), 'marcel': (398, 190),
    },
    'walkable': [(56, 160), (440, 160), (460, 160), (479, 164), (479, 196), (0, 196), (0, 172), (20, 164)],
}
