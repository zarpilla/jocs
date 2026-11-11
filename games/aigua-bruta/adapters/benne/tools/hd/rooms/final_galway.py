"""
Els finals (cinemàtica): la terrassa d'un bar del port de Galway, a trenc d'alba, dues setmanes després.
  - mirem a ponent: cel de matinada, blau a dalt i rosat a l'horitzó, i a l'altra banda de la badia, els turons;
  - al moll, l'Arenga amarrada (espera un volant nou per a la vàlvula de popa). El sol surt per darrere nostre,
    per damunt de la ciutat, i ja n'encén la punta del pal;
  - la terrassa: el tendal a dalt, la barana de ferro, el terra de fusta i la taula llarga (dues taules
    ajuntades) amb cafès i el diari. Els personatges hi són com a sprites: els del darrere queden tapats per
    la taula (FRONT);
  - la tele, penjada sota el tendal, amb les notícies (ANIMS) i el cable que baixa fins a la taula;
    `tele_apagada`: la pantalla negra (en Diu ha mossegat el cable).
"""
import math

from hd.pix import Light, Canvas, W, H, hr, mix, IRON
from hd.rooms.comu import _diff
from hd.rooms.exterior import arenga, reflection, fbm, smooth, HULLN, STEELX, ROPE, REDH, GLOW_WARM

HOR = 98
QUAY = 128          # la vora del moll (el que hi ha per sota tapa la flotació)
RAILTOP = 132
FLOOR_Y = 150
SHIP = (176, 134, 4.2)
TABLE = (148, 334)  # x de la taula llarga
TOP = 146           # el sobre
TV = (378, 30, 440, 70)
SCR = (TV[0] + 3, TV[1] + 3, TV[2] - 3, TV[3] - 4)

DAWN = [(34, 42, 78), (46, 56, 96), (62, 72, 116), (82, 90, 134), (104, 110, 150), (128, 128, 162),
        (154, 144, 170), (182, 160, 174), (208, 176, 178), (228, 194, 184), (244, 214, 196)]
SHORE = [(40, 46, 72), (54, 60, 88), (70, 74, 102), (88, 90, 116), (110, 106, 128), (150, 120, 120)]
STONE = [(24, 26, 34), (38, 40, 50), (54, 56, 66), (72, 74, 84), (92, 92, 100), (114, 112, 116), (138, 134, 134)]
WOOD = [(22, 16, 16), (36, 26, 24), (52, 38, 32), (70, 50, 40), (92, 66, 50), (116, 84, 62), (142, 106, 78),
        (170, 132, 98)]
AWN = [(10, 30, 26), (16, 46, 38), (24, 66, 52), (34, 88, 68), (48, 112, 86), (70, 138, 106)]
CREAM = [(56, 54, 54), (92, 88, 84), (130, 124, 114), (168, 160, 144), (200, 192, 172), (224, 218, 198)]
TABLER = [(20, 22, 26), (36, 38, 44), (54, 56, 64), (74, 76, 86), (98, 100, 110), (126, 128, 136), (160, 162, 166)]
CUPR = [(60, 58, 60), (110, 108, 108), (160, 158, 154), (200, 198, 192), (232, 230, 222)]
GOLDLIT = (255, 196, 120)

LIGHT = Light(ambient=1.0, vignette=(50, 26), floor_fade=(220, 60))
LIGHT.point(30, 230, r=170, k=1.4, squash=0.8, power=1.5)        # la finestra del bar, darrere nostre
LIGHT.point(409, 52, r=70, k=0.8, power=1.8)                     # la tele


# ─── Cel, badia i turons ───────────────────────────────────────────────────

def sky(cv):
    for y in range(0, HOR + 1):
        t = y / HOR
        for x in range(W):
            lvl = 0.6 + 8.6 * t ** 1.7
            c = fbm(x / 90, y / 10, 51)
            k = smooth(0.58, 0.72, c) * (0.3 + 0.7 * smooth(0.1, 0.6, t))
            if k > 0:
                up = fbm(x / 90, (y + 2) / 10, 51)
                under = max(0.0, smooth(0.58, 0.72, c) - smooth(0.58, 0.72, up))   # la vora de sota: el sol de cara
                body = 2.6 + 3.0 * t + 4.2 * under
                lvl = lvl * (1 - k) + body * k
            cv.put(x, y, DAWN, lvl, lit=0)
    # la lluna, que se'n va, a ponent
    cv.disc(70, 30, 3, 3, [(170, 172, 190), (210, 210, 220), (234, 232, 236)], lambda nx, ny: 1.6 - nx * 0.8, lit=0)


def shore(cv):
    """Els turons de l'altra banda de la badia, amb els cims ja tocats de rosa."""
    for x in range(W):
        top = HOR - 4 - 7 * fbm(x / 60, 0.5, 52) - 4 * fbm(x / 18, 1.5, 53)
        for y in range(int(top), HOR + 2):
            lvl = 2.4 - (y - top) * 0.08 + (1.6 if y - top < 1.2 else 0)
            cv.put(x, y, SHORE, lvl, lit=0)
    # un far petit
    cv.rect(452, HOR - 12, 454, HOR - 2, CREAM, 4.4, lit=0)
    cv.flat(453, HOR - 13, (255, 230, 170))
    cv.glow(453, HOR - 13, 4, (255, 220, 160), 0.6)


def bay(cv):
    for y in range(HOR + 2, QUAY + 4):
        d = y - HOR
        for x in range(W):
            sy = HOR - d * 2                                      # reflex del cel
            lvl = 0.6 + 8.6 * max(0, sy / HOR) ** 1.7 - 1.2
            n = fbm(x / (4 + d * 0.4), y / 1.2, 54)
            lvl += (n - 0.5) * 2.0
            cv.put(x, y, DAWN, lvl, lit=0)
    # una barqueta de pesca, lluny
    cv.rect(60, HOR + 6, 72, HOR + 8, CREAM, 2.0, lit=0)
    cv.rect(64, HOR + 2, 67, HOR + 5, CREAM, 2.6, lit=0)
    cv.vline(66, HOR - 6, HOR + 2, STEELX, 2.0, lit=0)


# ─── L'Arenga, amarrada ────────────────────────────────────────────────────

def ship(cv):
    xs, ywl, s = SHIP
    X, Y = arenga(cv, xs, ywl, s, 'dawn', facing=1, crane=True, zodiac=True)
    # el primer sol: la punta del pal, la creueta i el radar, daurats
    SUN = [(120, 70, 30), (190, 120, 50), (240, 176, 96), (255, 220, 160), (255, 244, 214)]
    for y in range(round(Y(16)), round(Y(10.5))):
        k = (Y(10.5) - y) / (Y(10.5) - Y(16))
        cv.put(X(27), y, SUN, 1.6 + 2.4 * k, lit=0)
        cv.put(X(27) + 1, y, SUN, 0.6 + 1.6 * k, lit=0)
    for m in (25.5, 26, 26.5, 27.5, 28, 28.5):
        cv.put(X(m), Y(13.5), SUN, 3.0, lit=0)
        cv.put(X(m), Y(11.6), SUN, 2.4, lit=0)
    cv.glow(X(27), Y(15.6), 10, (255, 210, 140), 0.55)
    cv.flat(X(27), Y(15.6), (255, 244, 214))
    # caps d'amarratge cap al moll
    for m, qx in ((2, 150), (36, 360)):
        cv.line(X(m), Y(sheer_at(m) - 0.6), qx, QUAY + 2, ROPE, 3.0, lit=0)


def _is_ship(cv, x, y):
    r, g, b, _ = cv.get(x, y)
    return abs(r - b) < 40 and r > 60                # el pal és gris; el cel no


def sheer_at(m):
    from hd.rooms.exterior import sheer
    return sheer(m)


def quay(cv):
    """El moll: pedra grisa, la vora amb les bites, un fanal encara encès."""
    for y in range(QUAY, RAILTOP + 4):
        for x in range(W):
            lvl = 3.2 - (y - QUAY) * 0.15 + (hr(x // 8, y // 3, 55) - 0.5) * 0.5
            if (x + (y // 3) * 4) % 16 == 0:
                lvl -= 1.0
            cv.put(x, y, STONE, lvl)
    cv.hline(0, W - 1, QUAY, STONE, 5.2)
    for bx in (148, 358):                                         # bites
        cv.rect(bx - 2, QUAY - 5, bx + 3, QUAY, IRON, 2.6)
        cv.disc(bx + 0.5, QUAY - 5, 3.5, 1.2, IRON, 4.0)
    # fanal
    cv.vline(456, 60, QUAY, IRON, 2.6)
    cv.vline(457, 60, QUAY, IRON, 1.6)
    cv.rect(452, 54, 461, 60, IRON, 2.4)
    cv.rect(454, 56, 459, 59, [(160, 120, 60), (240, 200, 120), (255, 236, 190)], 1.6, lit=0)
    cv.glow(456, 58, 12, (255, 210, 140), 0.35)


# ─── La terrassa ───────────────────────────────────────────────────────────

def railing(cv):
    cv.rect(0, RAILTOP, W - 1, RAILTOP + 2, IRON, 3.6)
    cv.hline(0, W - 1, RAILTOP, IRON, 5.4)
    cv.rect(0, FLOOR_Y - 4, W - 1, FLOOR_Y - 2, IRON, 2.4)
    for x in range(3, W, 7):
        cv.vline(x, RAILTOP + 3, FLOOR_Y - 5, IRON, 2.6)
        cv.put(x + 1, RAILTOP + 6, IRON, 3.6)
    # testos amb bruc als extrems
    for px in (12, 438):
        cv.rect(px, FLOOR_Y - 14, px + 30, FLOOR_Y, WOOD, lambda x, y: 3.2 - (y - FLOOR_Y + 14) * 0.08)
        cv.hline(px, px + 30, FLOOR_Y - 14, WOOD, 5.0)
        for i in range(40):
            fx = px + 2 + int(hr(i, px) * 26)
            fy = FLOOR_Y - 15 - int(hr(i, px + 1) * 10)
            cv.put(fx, fy, [(40, 20, 40), (90, 40, 90), (150, 80, 140), (200, 130, 180)], 1.0 + hr(i, 3) * 2.4)
            cv.put(fx, fy + 1, [(20, 40, 24), (40, 70, 40)], 1.0)


def floor(cv):
    """Terra de fusta de la terrassa, en perspectiva, amb el reflex càlid de la finestra del bar."""
    vp = (240, 60)
    for y in range(FLOOR_Y, H):
        d = y - vp[1]
        for x in range(W):
            u = vp[0] + (x - vp[0]) * 120 / d
            u2 = vp[0] + (x + 1 - vp[0]) * 120 / d
            lvl = 2.8 + (hr(int(u // 14), y // 9, 56) - 0.5) * 0.6 + (fbm(u / 6, y / 30, 57) - 0.5) * 0.6
            if int(u // 14) != int(u2 // 14):
                lvl -= 1.6
            cv.put(x, y, WOOD, lvl)


def awning(cv):
    """El tendal, a dalt: la tela a ratlles verdes i crema, amb la vora de festons, i el pal de la dreta."""
    for y in range(0, 12):
        for x in range(W):
            stripe = (x // 16) % 2
            lvl = 3.0 - y * 0.12 + (0.6 if y == 0 else 0)
            cv.put(x, y, AWN if stripe else CREAM, lvl + (0 if stripe else 0.8), lit=0.5)
    for x in range(W):                                            # festons
        u = (x % 16) / 16
        h = 12 + int(4 * math.sin(u * math.pi))
        stripe = (x // 16) % 2
        for y in range(12, h + 1):
            cv.put(x, y, AWN if stripe else CREAM, 2.4 - (y - 12) * 0.2 + (0 if stripe else 0.8), lit=0.5)
        cv.put(x, h + 1, [(8, 10, 14)], 0, lit=0)
    # pals del tendal
    for px in (2, 470):
        for y in range(12, FLOOR_Y + 8):
            cv.put(px, y, IRON, 3.2)
            cv.put(px + 1, y, IRON, 4.2)
            cv.put(px + 2, y, IRON, 2.0)


def tv_frame(cv):
    x0, y0, x1, y1 = TV
    cv.vline((x0 + x1) // 2, 14, y0, IRON, 3.0)                   # el braç que la penja del tendal
    cv.vline((x0 + x1) // 2 + 1, 14, y0, IRON, 1.8)
    cv.rect(x0, y0, x1, y1, TABLER, 1.4)
    cv.hline(x0, x1, y0, TABLER, 3.0)
    cv.hline(x0, x1, y1, TABLER, 0.6)
    cv.put(x1 - 3, y1 - 2, [(60, 255, 120)], 0, lit=0)


def tv_news(cv, frame=0):
    """Les notícies: el plató blau, la imatge de la plataforma i la cinta vermella de sota."""
    x0, y0, x1, y1 = SCR
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, [(8, 16, 46), (14, 28, 78), (22, 44, 112), (36, 70, 150), (70, 110, 190)],
                   2.4 - (y - y0) / 20 + (x - x0) / 60, lit=0)
    # la finestra amb la plataforma (gris, amb la taca)
    cv.rect(x0 + 3, y0 + 3, x0 + 30, y0 + 22, [(70, 80, 90), (110, 120, 128), (150, 160, 166)], 1.4, lit=0)
    cv.rect(x0 + 3, y0 + 17, x0 + 30, y0 + 22, [(30, 46, 58), (50, 70, 80)], 1.0, lit=0)
    cv.rect(x0 + 10, y0 + 9, x0 + 22, y0 + 12, [(30, 30, 34)], 0, lit=0)
    for lx in (x0 + 11, x0 + 15, x0 + 19):
        cv.vline(lx, y0 + 13, y0 + 18, [(30, 30, 34)], 0, lit=0)
    cv.rect(x0 + 8, y0 + 18, x0 + 26, y0 + 19, [(110, 100, 70)], 0, lit=0)
    # el presentador (una silueta amb americana) a la dreta
    cv.disc(x1 - 12, y0 + 9, 3, 3, [(150, 110, 90), (200, 150, 120)], 1.2, lit=0)
    cv.rect(x1 - 18, y0 + 13, x1 - 6, y0 + 22, [(10, 10, 20), (24, 24, 40)], 1.0, lit=0)
    # la cinta vermella amb text que corre
    cv.rect(x0, y1 - 8, x1, y1 - 4, [(120, 14, 20), (180, 26, 30), (220, 50, 44)], 1.6, lit=0)
    cv.rect(x0, y1 - 3, x1, y1, [(230, 230, 226)], 0, lit=0)
    off = frame * 3
    for x in range(x0 + 1, x1):
        if ((x + off) // 2) % 5 not in (0,) and hr((x + off) // 9, 61) > 0.25:
            cv.flat(x, y1 - 2, (30, 30, 40))
    for x in range(x0 + 2, x0 + 24):
        if (x // 2) % 4:
            cv.flat(x, y1 - 6, (255, 240, 230))
    cv.glow((x0 + x1) // 2, (y0 + y1) // 2, 34, (90, 140, 230), 0.10)


def tv_cable(cv):
    """El cable de la tele, que baixa pel braç i va fins a l'endoll del pal, passant per la punta de la taula."""
    x0, y0, x1, y1 = TV
    pts = [(x1 - 6, y1), (x1 - 4, y1 + 30), (TABLE[1] + 4, TOP - 2), (TABLE[1] + 10, TOP + 6), (470, 120)]
    n = 120
    for i in range(n + 1):
        t = i / n
        p = list(pts)
        while len(p) > 1:
            p = [((a[0] * (1 - t) + b[0] * t), (a[1] * (1 - t) + b[1] * t)) for a, b in zip(p, p[1:])]
        cv.put(round(p[0][0]), round(p[0][1]), [(8, 8, 10), (20, 20, 24), (36, 36, 42)], 1.4)


def chairs(cv):
    """Cadires de bistrot darrere la taula (se'n veu el respatller)."""
    for cx in range(166, TABLE[1] - 8, 40):
        cv.rect(cx - 7, TOP - 22, cx + 7, TOP - 20, IRON, 3.0)
        for k in (-7, 7):
            cv.vline(cx + k, TOP - 22, TOP, IRON, 2.4)
        for k in (-3, 0, 3):
            cv.vline(cx + k, TOP - 19, TOP - 8, IRON, 2.0)
        cv.hline(cx - 7, cx + 7, TOP - 8, IRON, 2.6)


def table(cv):
    """La taula llarga: dues taules de terrassa ajuntades, amb cafès, una tetera, el diari i un plat de scones."""
    x0, x1 = TABLE
    # el sobre (es veu una mica de dalt) i el cantell
    cv.rect(x0, TOP - 3, x1, TOP, WOOD, lambda x, y: 5.6 - (TOP - y) * 0.3 + (hr(x // 5, y, 58) - 0.5) * 0.5)
    cv.rect(x0, TOP + 1, x1, TOP + 5, WOOD, lambda x, y: 3.6 - (y - TOP) * 0.2)
    cv.hline(x0, x1, TOP + 1, WOOD, 6.4)
    cv.hline(x0, x1, TOP + 5, WOOD, 1.6)
    cv.vline((x0 + x1) // 2, TOP - 3, TOP + 5, WOOD, 1.0)
    # potes
    for lx in (x0 + 6, (x0 + x1) // 2 - 6, (x0 + x1) // 2 + 6, x1 - 6):
        cv.rect(lx - 1, TOP + 6, lx + 1, 178, TABLER, 2.6)
        cv.vline(lx - 1, TOP + 6, 178, TABLER, 3.8)
        cv.rect(lx - 6, 178, lx + 6, 180, TABLER, 1.8)
    # el que hi ha a damunt
    for i, mx in enumerate((168, 206, 252, 292, 322)):
        cv.rect(mx, TOP - 8, mx + 5, TOP - 3, CUPR, 3.0)
        cv.vline(mx + 6, TOP - 7, TOP - 5, CUPR, 2.4)
        cv.hline(mx + 1, mx + 4, TOP - 8, [(40, 22, 10), (70, 40, 20)], 0.8)
        cv.disc(mx + 2.5, TOP - 3, 5, 1.2, CUPR, 3.6)
    # la tetera
    cv.disc(232, TOP - 8, 6, 5, [(20, 40, 60), (36, 66, 96), (60, 100, 136), (100, 150, 180)], lambda nx, ny: 2.2 - nx - ny)
    cv.line(238, TOP - 9, 242, TOP - 12, [(36, 66, 96), (60, 100, 136)], 1.4)
    cv.rect(230, TOP - 14, 234, TOP - 13, [(36, 66, 96), (60, 100, 136)], 1.2)
    # el diari, plegat
    cv.poly([(266, TOP - 2), (286, TOP - 3), (288, TOP), (268, TOP)], CREAM, 4.6)
    for k in range(3):
        cv.hline(270, 284, TOP - 2 + k, CREAM, 2.6)
    # scones
    cv.disc(190, TOP - 1, 8, 1.6, CUPR, 4.0)
    for sx in (186, 193):
        cv.disc(sx, TOP - 4, 3, 2, [(80, 46, 20), (140, 90, 46), (196, 146, 86), (230, 190, 130)], lambda nx, ny: 2.6 - ny)


def bg(cv, frame=0):
    sky(cv)
    shore(cv)
    bay(cv)
    ship(cv)
    quay(cv)
    railing(cv)
    floor(cv)
    awning(cv)
    tv_frame(cv)
    tv_news(cv, frame)
    chairs(cv)
    tv_cable(cv)
    table(cv)
    cv.glow(40, 230, 70, GOLDLIT, 0.10)                            # la llum del bar, darrere nostre


def tele_apagada(cv):
    x0, y0, x1, y1 = SCR
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, [(4, 5, 8), (8, 10, 14), (14, 16, 22), (22, 26, 34)], 1.0 + (x - x0) / 50 - (y - y0) / 60, lit=0)
    # el reflex del cel a la pantalla negra
    for k in range(6):
        cv.line(x0 + 6 + k, y0 + 2, x0 + 2 + k, y0 + 10, [(60, 60, 90)], 0, lit=0)


PROPS = {'tele_apagada': tele_apagada}

# La taula tapa les cames de qui seu al darrere. El sobre (de TOP-3 a TOP) queda fora, perquè en Diu s'hi
# pugui enfilar sense quedar tallat.
FRONT = {'mask': lambda x, y: TABLE[0] - 6 <= x <= TABLE[1] + 6 and TOP + 1 <= y <= 180,
         'baseline': 182, 'zIndex': 20}


def _frames():
    base = Canvas(light=LIGHT)
    bg(base)
    frames = []
    for i in range(8):
        cv = Canvas(light=LIGHT, img=base.img.copy())
        tv_news(cv, i)
        frames.append(_diff(cv.img, base.img))
    return frames


ANIMS = {'tele': {'frames': _frames, 'frameDuration': 220}}

GEOMETRIA = {
    'things': {},
    'spawns': {'iri': (124, 192), 'vet': (360, 192), 'diu': (318, 146), 'capitana': (176, 170),
               'nadia': (218, 170), 'marcel': (262, 170), 'tomas': (304, 170)},
    'walkable': [(100, 186), (380, 186), (380, 200), (100, 200)],
}
