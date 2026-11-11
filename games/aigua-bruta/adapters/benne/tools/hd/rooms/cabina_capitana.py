"""
Cabina de la Capitana (coberta principal): sòbria, endreçada, de fusta i crema.

  - la porta estanca del passadís a l'esquerra, amb la gorra penjada al costat;
  - l'ull de bou, el rellotge i el baròmetre de llautó;
  - l'escriptori de teca amb el contracte de Blau Net (`contracte`), la novel·la romàntica (`novella`), el flexo,
    una tassa i una foto; a sobre, un prestatge amb barana amb els llibres de navegació;
  - la carta nàutica a la paret (`carta`), amb Galway i Port Hallen encerclats (Port Hallen, en vermell i més fort);
  - la llitera de teca amb la manta blava, sota la carta; una catifa al linòleum.
"""
import math

from hd.pix import Canvas, Light, W, H, hr, mix  # noqa: F401
from hd.rooms.arenga import box, rrect, bolt, glow, CAB, DARK, WHITEP, REDP, YELL, BRASS, FLOOR_Y
from hd.rooms.principal import day_porthole
from hd.rooms.laboratori import (cream_wall, ceiling, lamps, lamp_glow, watertight_door, porthole, linoleum,
                                 CREAM, LINO_RED, TEAK, PAPERC, BLUEB, SEA)

LAMPS = ((128, 22), (372, 22))

LIGHT = Light(ambient=0.3, vignette=(60, 26), floor_fade=None)
LIGHT.point(128, 26, r=150, k=2.0, squash=1.05, down=True, power=1.5)
LIGHT.point(372, 26, r=150, k=2.0, squash=1.05, down=True, power=1.5)
LIGHT.point(282, 96, r=90, k=1.6, power=1.6)                   # el flexo de l'escriptori

NAVY = [(6, 8, 16), (10, 14, 28), (16, 22, 44), (24, 32, 62), (36, 46, 84), (52, 64, 108), (76, 90, 136)]
SHADE = [(8, 24, 14), (14, 44, 26), (22, 70, 40), (36, 100, 58), (56, 132, 80)]
WAINSCOT_Y = 110


def wainscot(cv):
    """Folre de teca a la part de baix de la paret (la cabina del capità sempre en té)."""
    for y in range(WAINSCOT_Y, FLOOR_Y):
        for x in range(W):
            grain = math.sin(x * 0.9 + math.sin(y * 0.15 + x * 0.05) * 3) * 0.25
            lv = 3.6 + grain + (hr(x // 30, 3) - 0.5) * 0.4
            if x % 30 == 0:
                lv = 2.0
            elif x % 30 == 1:
                lv = 4.6
            cv.put(x, y, TEAK, lv)
    box(cv, 0, WAINSCOT_Y - 3, W - 1, WAINSCOT_Y, TEAK, 4.8)
    cv.hline(0, W - 1, WAINSCOT_Y + 1, TEAK, 1.6)
    box(cv, 0, FLOOR_Y - 6, W - 1, FLOOR_Y - 1, TEAK, 3.0)


def cap_hook(cv):
    """La gorra de capitana (blanca, visera negra i ancoreta daurada) i un anorac, penjats al costat de la porta."""
    box(cv, 68, 70, 72, 73, BRASS, 3.6)
    box(cv, 68, 92, 72, 95, BRASS, 3.6)
    cv.disc(70, 78, 8, 4, WHITEP, lambda nx, ny: 4.6 - nx * 0.6 - ny * 0.8)
    cv.rect(62, 79, 78, 82, NAVY, 1.4)
    cv.poly([(63, 83), (77, 83), (80, 86), (60, 86)], DARK, 2.4)
    cv.put(70, 80, YELL, 5.0)
    cv.put(69, 81, YELL, 4.0)
    cv.put(71, 81, YELL, 4.0)
    # l'anorac, groc de mar
    cv.poly([(66, 96), (74, 96), (80, 104), (80, 138), (62, 138), (62, 104)], YELL,
            lambda x, y: 3.6 - (x - 62) * 0.05 + (0.5 if (x * 3 + y) % 11 == 0 else 0))
    cv.vline(71, 98, 138, YELL, 2.0)
    cv.line(64, 104, 61, 132, YELL, 2.4)
    cv.hline(62, 80, 124, [(120, 120, 110), (220, 220, 200), (250, 250, 240)], 1.8)


def clock_barometer(cv):
    """Rellotge i baròmetre de llautó, aparellats en una post de teca."""
    box(cv, 130, 40, 178, 62, TEAK, 4.0)
    for cx in (143, 165):
        cv.disc(cx, 51, 9, 9, BRASS, lambda nx, ny: 3.8 - nx * 1.2 - ny * 1.2)
        cv.disc(cx, 51, 7, 7, WHITEP, lambda nx, ny: 4.8 - ny * 0.3)
        for a in range(0, 360, 30):
            cv.put(cx + round(math.cos(math.radians(a)) * 6), 51 + round(math.sin(math.radians(a)) * 6), CAB, 1.4)
    cv.line(143, 51, 143, 46, CAB, 0.6)                              # les quatre menys deu
    cv.line(143, 51, 147, 51, CAB, 0.6)
    cv.line(165, 51, 161, 47, REDP, 3.0)                             # el baròmetre, baixant
    cv.line(165, 51, 168, 53, CAB, 1.0)


def bookshelf(cv):
    """Prestatge amb barana sobre l'escriptori: derroters, l'almanac, carpetes i un model de l'Arenga."""
    x0, x1, y = 186, 300, 70
    box(cv, x0, y, x1, y + 3, TEAK, 4.6)
    for bx in (x0 + 6, x1 - 6):
        cv.poly([(bx - 1, y + 4), (bx + 1, y + 4), (bx + 1, y + 12), (bx - 1, y + 6)], CAB, 3.2)
    cols = [NAVY, REDP, TEAK, [(20, 40, 30), (40, 80, 56), (70, 120, 84), (110, 160, 120)], NAVY, PAPERC]
    x = x0 + 3
    i = 0
    while x < 254:
        w = 3 + int(hr(i, 81) * 3)
        h = 12 + int(hr(i, 82) * 6)
        c = cols[int(hr(i, 83) * len(cols))]
        lean = i == 9
        for xx in range(x, x + w):
            for yy in range(y - h, y):
                cv.put(xx + (1 if lean and yy < y - h // 2 else 0), yy, c, 3.0 - (xx - x) * 0.3 + (0.8 if xx == x else 0))
        if h > 14:
            cv.hline(x, x + w - 1, y - h + 4, BRASS, 4.0)
        x += w + 1
        i += 1
    # un model de l'Arenga: casc blanc, línia vermella, el pont
    cv.poly([(262, 62), (296, 62), (292, 69), (266, 69)], WHITEP, 4.4)
    cv.hline(264, 294, 64, REDP, 4.2)
    box(cv, 274, 54, 286, 61, WHITEP, 4.6)
    cv.vline(282, 44, 53, CAB, 3.0)
    cv.hline(x0, x1, y - 7, BRASS, 3.6)                              # la barana
    for bx in range(x0 + 2, x1, 19):
        cv.vline(bx, y - 7, y - 1, BRASS, 3.0)


DESK = (172, 108, 312, 158)     # x0, y del sobre (darrere), x1, y dels peus


def desk(cv):
    x0, ytop, x1, ybot = DESK
    # el sobre, una mica en perspectiva
    cv.poly([(x0 + 3, ytop), (x1 - 3, ytop), (x1, ytop + 6), (x0, ytop + 6)], TEAK,
            lambda x, y: 4.0 + (y - ytop) * 0.15 + math.sin(x * 0.4 + y) * 0.15)
    cv.rect(x0, ytop + 7, x1, ytop + 10, TEAK, 4.4)
    cv.hline(x0, x1, ytop + 7, TEAK, 5.6)
    cv.hline(x0, x1, ytop + 11, TEAK, 1.0)
    # el caixó dels calaixos (a la dreta) i la pota de l'esquerra
    box(cv, x1 - 46, ytop + 11, x1 - 2, ybot, TEAK, 3.6, grad=0.8)
    for i, cy in enumerate((ytop + 14, ytop + 26, ytop + 38)):
        box(cv, x1 - 43, cy, x1 - 5, cy + 10, TEAK, 4.0)
        box(cv, x1 - 28, cy + 4, x1 - 20, cy + 5, BRASS, 4.0)
    box(cv, x0 + 2, ytop + 11, x0 + 8, ybot, TEAK, 3.2)
    # el buit de sota, fosc
    cv.rect(x0 + 9, ytop + 11, x1 - 47, ybot, TEAK, lambda x, y: 1.0 + (y - ytop) * 0.01)
    cv.rect(x0 + 9, ytop + 11, x1 - 47, ytop + 18, TEAK, 3.2)               # el calaix del mig
    box(cv, (x0 + x1 - 38) // 2 - 4, ytop + 14, (x0 + x1 - 38) // 2 + 4, ytop + 15, BRASS, 4.0)
    # la paperera, sota
    for y in range(ybot - 14, ybot + 1):
        for x in range(196, 210):
            u = (x - 203) / 7
            if (x + y) % 3:
                cv.put(x, y, CAB, 3.0 - u * 1.2)
    cv.disc(203, ybot - 14, 7, 1.5, CAB, 1.0)
    cv.rect(199, ybot - 16, 203, ybot - 14, PAPERC, 4.0)


def chair(cv):
    """La cadira de l'escriptori, de teca amb el coixí blau, separada de la taula."""
    cx, y0 = 236, 106
    # el respatller, de llistons
    rrect(cv, cx - 13, y0, cx + 13, y0 + 6, 3, TEAK, lambda x, y: 4.6 - (y - y0) * 0.1)
    for x in range(cx - 10, cx + 11, 5):
        cv.vline(x, y0 + 6, y0 + 22, TEAK, 3.4)
        cv.vline(x + 1, y0 + 6, y0 + 22, TEAK, 2.2)
    cv.vline(cx - 13, y0 + 3, y0 + 26, TEAK, 3.8)
    cv.vline(cx + 13, y0 + 3, y0 + 26, TEAK, 2.6)
    # el seient, amb coixí
    cv.disc(cx, y0 + 29, 16, 4, TEAK, lambda nx, ny: 3.8 - ny * 1.4)
    cv.disc(cx, y0 + 27, 13, 3, NAVY, lambda nx, ny: 4.0 - ny * 1.2)
    # el peu giratori
    cv.vline(cx, y0 + 33, y0 + 50, CAB, 3.6)
    cv.vline(cx + 1, y0 + 33, y0 + 50, CAB, 2.2)
    for dx in (-15, -6, 6, 15):
        cv.line(cx, y0 + 50, cx + dx, y0 + 55, CAB, 3.0)
        cv.put(cx + dx, y0 + 56, DARK, 0.6)
    cv.darken(cx - 16, y0 + 56, cx + 16, y0 + 58, 0.6)


def contract(cv):
    """El contracte de Blau Net: un plec grapat, amb la capçalera blava i el logotip (una gota)."""
    x0, y0 = 194, 104
    cv.poly([(x0 + 2, y0), (x0 + 24, y0 - 1), (x0 + 26, y0 + 8), (x0, y0 + 9)], PAPERC, lambda x, y: 4.4 - (y - y0) * 0.05)
    cv.poly([(x0 + 8, y0 + 1), (x0 + 36, y0 + 1), (x0 + 38, y0 + 9), (x0 + 6, y0 + 9)], PAPERC,
            lambda x, y: 4.8 - (y - y0) * 0.05)
    cv.rect(x0 + 9, y0 + 2, x0 + 36, y0 + 3, [(10, 40, 90), (20, 80, 160), (60, 140, 220)], 1.6)
    cv.put(x0 + 10, y0 + 2, [(240, 250, 255)], 0, lit=0)
    for y in (y0 + 5, y0 + 7):
        for x in range(x0 + 10, x0 + 36):
            if hr(x // 2, y) > 0.3:
                cv.put(x, y, PAPERC, 2.4)
    cv.put(x0 + 9, y0 + 1, CAB, 4.6)                                  # la grapa
    # el bolígraf al damunt
    cv.line(x0 + 20, y0 + 10, x0 + 34, y0 + 6, NAVY, 3.0)


def novel(cv):
    """«Amor a alta mar», volum tres: butxaca de tapa rosa, amb un punt de llibre amb una àncora."""
    x0, y0 = 248, 106
    cv.poly([(x0 + 2, y0), (x0 + 20, y0), (x0 + 22, y0 + 5), (x0, y0 + 5)],
            [(60, 10, 30), (120, 30, 60), (180, 60, 100), (220, 110, 140), (246, 170, 190)],
            lambda x, y: 3.0 + (y - y0) * 0.1)
    cv.rect(x0, y0 + 6, x0 + 22, y0 + 7, PAPERC, 4.0)
    cv.hline(x0, x0 + 22, y0 + 8, [(60, 10, 30), (120, 30, 60)], 1.4)
    # un cor a la tapa
    for dx, dy in ((9, 1), (11, 1), (8, 2), (9, 2), (10, 2), (11, 2), (12, 2), (10, 3)):
        cv.flat(x0 + dx, y0 + dy, (250, 220, 230))
    # el punt de llibre que surt per dalt, amb l'àncora
    cv.rect(x0 + 16, y0 - 5, x0 + 17, y0, BRASS, 4.4)
    cv.put(x0 + 16, y0 - 6, BRASS, 5.4)


def desk_things(cv):
    """El flexo, una tassa i la foto."""
    # flexo de llautó amb la pantalla verda
    bx = 292
    cv.disc(bx, 112, 7, 2, BRASS, lambda nx, ny: 3.6 - nx)
    cv.line(bx, 111, bx - 4, 96, BRASS, 4.0)
    cv.line(bx + 1, 111, bx - 3, 96, BRASS, 2.6)
    cv.line(bx - 4, 96, bx + 6, 88, BRASS, 4.0)
    cv.poly([(bx + 2, 86), (bx + 10, 84), (bx + 16, 94), (bx + 2, 96)], SHADE, lambda x, y: 3.4 - (y - 84) * 0.1)
    cv.hline(bx + 3, bx + 15, 95, [(200, 170, 100), (255, 240, 190)], 1.4, lit=0)
    # la tassa (blanca, amb el logotip de Mar Obert: un cercle vermell)
    for y in range(102, 112):
        for x in range(178, 186):
            cv.put(x, y, WHITEP, 4.4 - (x - 178) * 0.15)
    cv.disc(181, 106, 1.5, 1.5, REDP, 4.4)
    cv.ring(187, 106, 2, WHITEP, 3.6, step=30)
    cv.disc(182, 102, 4, 1, [(30, 18, 10), (60, 36, 20)], 1.0)
    # la foto: un marc de llautó amb un vaixell petit
    box(cv, 276, 96, 286, 110, BRASS, 3.2)
    cv.rect(278, 98, 284, 108, [(60, 90, 120), (120, 150, 170), (180, 200, 210)], 1.6)
    cv.rect(278, 105, 284, 108, [(20, 40, 70), (40, 70, 100)], 1.0)
    cv.hline(279, 283, 104, WHITEP, 4.0)


def sea_chart(cv):
    """La carta nàutica de la campanya: mar blau pàl·lid, terra groguenca, batimètriques, la ruta, Galway i
    Port Hallen encerclats. El Punt 7 és a l'Atlàntic, a l'oest d'Irlanda: Irlanda (amb Galway a la costa de
    ponent) queda a la dreta, i la costa de Valmark (Port Hallen) a dalt, cap al nord-est."""
    x0, y0, x1, y1 = 330, 36, 452, 100
    box(cv, x0 - 2, y0 - 2, x1 + 2, y1 + 2, TEAK, 4.2)

    def irlanda(x, y):
        """Irlanda, a l'est (dreta): costa de ponent retallada, amb la badia de Galway."""
        u, v = x - x0, y - y0
        if not 24 <= v <= 62:
            return False
        costa = 82 + 4 * math.sin(v * 0.45) + 1.5 * math.sin(v * 1.3) + abs(v - 42) ** 2 * 0.04
        if 33 <= v <= 37:                                                # la badia de Galway
            costa += 5 - abs(v - 35) * 1.5
        return u > costa

    def valmark(x, y):
        """La costa de Valmark, al nord-est (a dalt a la dreta)."""
        u, v = x - x0, y - y0
        return u > 64 and v < 3 + (u - 64) * 0.12 + 1.5 * math.sin(u * 0.3)

    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if irlanda(x, y) or valmark(x, y):
                cv.put(x, y, [(150, 134, 90), (196, 180, 128), (226, 212, 160)], 1.6 + (0.4 if (x * 7 + y) % 13 == 0 else 0))
            else:
                deep = math.sin((x - x0) * 0.08 + (y - y0) * 0.05)
                lv = 1.8 if deep > 0.6 else 2.2
                cv.put(x, y, [(120, 150, 170), (160, 190, 206), (200, 222, 232), (226, 238, 242)], lv)
                if abs(deep - 0.6) < 0.04:
                    cv.put(x, y, [(90, 120, 150), (120, 150, 170)], 1.0)
    # la quadrícula de longitud i latitud
    for x in range(x0 + 20, x1, 30):
        for y in range(y0, y1, 2):
            cv.put(x, y, [(90, 110, 130), (130, 150, 170)], 1.0)
    for y in range(y0 + 16, y1, 22):
        for x in range(x0, x1, 2):
            cv.put(x, y, [(90, 110, 130), (130, 150, 170)], 1.0)
    # la rosa dels vents, a baix a l'esquerra (mar obert)
    rx, ry = x0 + 14, y0 + 50
    cv.ring(rx, ry, 6, [(90, 60, 80), (150, 100, 120)], 1.4, step=20)
    cv.line(rx, ry - 7, rx, ry + 7, [(90, 60, 80), (150, 100, 120)], 1.4)
    cv.line(rx - 7, ry, rx + 7, ry, [(90, 60, 80), (150, 100, 120)], 1.4)
    cv.flat(rx, ry - 8, (90, 60, 80))                                  # el nord
    # la ruta, a llapis, del Punt 7 cap a Galway (a l'est)
    gal = (x0 + 86, y0 + 35)
    hal = (x0 + 98, y0 + 9)
    p7 = (x0 + 42, y0 + 40)
    for i in range(0, 40):
        t = i / 40
        x = round(p7[0] + (gal[0] - p7[0]) * t)
        y = round(p7[1] + (gal[1] - p7[1]) * t)
        if i % 3 != 2:
            cv.flat(x, y, (70, 70, 80))
    cv.flat(p7[0], p7[1], (30, 30, 40))
    cv.flat(p7[0] + 1, p7[1], (30, 30, 40))
    cv.flat(p7[0], p7[1] + 1, (30, 30, 40))
    cv.flat(p7[0] + 1, p7[1] + 1, (30, 30, 40))
    # Galway: un cercle fi, a llapis blau
    cv.ring(gal[0], gal[1], 5, BLUEB, 2.4, step=12)
    # Port Hallen: en vermell, repassat dues vegades
    cv.ring(hal[0], hal[1], 6, REDP, 4.0, step=8)
    cv.ring(hal[0] + 1, hal[1], 7, REDP, 3.4, step=8)
    cv.flat(hal[0], hal[1], (40, 20, 20))
    # xinxetes
    for x, y in ((x0 + 1, y0 + 1), (x1 - 1, y0 + 1), (x0 + 1, y1 - 1), (x1 - 1, y1 - 1)):
        cv.flat(x, y, (200, 40, 40))


def bunk(cv):
    """La llitera de teca amb calaixos, la manta blava de ratlla vermella i el coixí; un llum de lectura."""
    x0, x1, top = 324, 478, 120
    # el llum de lectura de llautó
    box(cv, 462, 104, 470, 108, BRASS, 3.4)
    cv.disc(466, 110, 4, 2, [(120, 96, 50), (210, 176, 110), (250, 228, 170)], 1.6, lit=0)
    # el matalàs i la manta
    cv.rect(x0 + 4, top, x1, top + 4, PAPERC, lambda x, y: 3.6 + (0.4 if y == top else 0))
    for y in range(top + 3, top + 16):
        for x in range(x0 + 4, x1 + 1):
            fold = math.sin(x * 0.12 + y * 0.3) * 0.3
            cv.put(x, y, NAVY, 3.6 - (y - top) * 0.06 + fold)
    cv.hline(x0 + 4, x1, top + 3, NAVY, 5.0)
    for x in range(x0 + 4, x1 + 1):
        cv.put(x, top + 9, REDP, 3.6)
        cv.put(x, top + 10, REDP, 2.8)
    # el coixí, a la dreta
    rrect(cv, 446, top - 6, 474, top + 3, 3, PAPERC, lambda x, y: 4.6 - (y - top + 6) * 0.08)
    # la post de davant (la vora alta perquè no et tiri la mar) i els calaixos
    box(cv, x0, top + 14, x1, top + 20, TEAK, 4.6)
    box(cv, x0, top + 21, x1, FLOOR_Y + 4, TEAK, 3.4, grad=0.6)
    for dx in range(x0 + 6, x1 - 30, 50):
        box(cv, dx, top + 24, dx + 42, FLOOR_Y, TEAK, 3.8)
        box(cv, dx + 17, top + 28, dx + 25, top + 29, BRASS, 4.0)
    box(cv, x0, top - 4, x0 + 4, FLOOR_Y + 4, TEAK, 4.2)                    # el capçal dels peus


def rug(cv):
    """Una catifa gastada, blau marí amb vora vermella, a terra davant l'escriptori."""
    pts = [(176, 164), (318, 164), (334, 188), (160, 188)]
    cv.poly(pts, NAVY, lambda x, y: 2.6 + (0.4 if (x // 3 + y) % 6 == 0 else 0) + (hr(x // 5, y) - 0.5) * 0.3)
    cv.poly([(182, 167), (312, 167), (326, 185), (168, 185)], REDP, 2.2)
    cv.poly([(186, 169), (308, 169), (320, 183), (174, 183)], NAVY, lambda x, y: 2.8 + (hr(x // 4, y // 2) - 0.5) * 0.3)
    for x in range(160, 334, 3):
        cv.put(x, 189, PAPERC, 2.0)


def bg(cv):
    cream_wall(cv, dado=FLOOR_Y)
    wainscot(cv)
    ceiling(cv)
    linoleum(cv, lvl=3.8, lamps=LAMPS)
    rug(cv)
    watertight_door(cv, leaf_ramp=TEAK, leaf_lvl=4.0)
    cap_hook(cv)
    porthole(cv, 106, 76)
    clock_barometer(cv)
    bookshelf(cv)
    desk(cv)
    chair(cv)
    desk_things(cv)
    contract(cv)
    novel(cv)
    sea_chart(cv)
    bunk(cv)
    lamps(cv, LAMPS)
    cv.darken(DESK[0], DESK[3] + 1, DESK[2], DESK[3] + 4, lambda x, y: 0.8 - (y - DESK[3]) * 0.2)
    cv.darken(324, FLOOR_Y + 5, 479, FLOOR_Y + 8, lambda x, y: 0.7 - (y - FLOOR_Y - 5) * 0.2)
    lamp_glow(cv, LAMPS)
    glow(cv, 301, 98, 26, (255, 220, 150), 0.35)                    # el flexo


# Escenes 2 i 3: de dia, el vidre de l'ull de bou clar
PROPS = {'ulls_dia': lambda cv: day_porthole(cv, 106, 76, 11)}

GEOMETRIA = {
    'things': {
        'porta': {'rect': (4, 50, 60, 152), 'walk': (36, 182)},
        'contracte': {'rect': (192, 99, 234, 114), 'walk': (214, 180)},
        'novella': {'rect': (246, 100, 272, 115), 'walk': (260, 180)},
        'carta': {'rect': (326, 32, 456, 104), 'walk': (390, 180)},
    },
    'spawns': {'iri': (150, 192), 'vet': (200, 196), 'capitana': (330, 184)},
    'walkable': [(12, 168), (468, 168), (476, 198), (4, 198)],
}
