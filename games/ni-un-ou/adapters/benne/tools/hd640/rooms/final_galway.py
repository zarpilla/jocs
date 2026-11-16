"""
Prova a 640×360: els finals (cinemàtica), la terrassa d'un bar del port de Galway a trenc d'alba (vegeu
hd/rooms/final_galway.py, la de 480×270). Mateixa composició ×4/3, dibuixada de nou: el cel, la badia i el terra
es calculen a la resolució nova (el soroll va en coordenades de 480, mostrejat més fi), i hi ha detall que a 480
no hi cabia: la cinta de les notícies es llegeix i corre, plats i culleretes a les tasses, el sucrer, melmelada als
scones, cadires de vímet, la barana amb volutes, una gavina a la bita, el caseriu de l'altra riba, el far amb el feix.
Cinemàtica: no hi ha barra de verbs, la pantalla és sencera.
Props: `tele_apagada`. ANIMS: `tele`, `badia`, `vapor`. FRONT: la taula tapa les cames de qui seu al darrere.
"""
import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

import math

from hd.pix import Light, Canvas, W, H, hr, mix, IRON
from hd.rooms.comu import _diff, text, text_width
from hd.rooms.exterior import arenga, fbm, smooth, sheer, STEELX, ROPE

# Art a 2× (1280×720 per a una sala de 640×360): el mateix dibuix, amb les formes, el dither i la llum a la
# resolució real (hd1280/canvas2x.py); el motor el mostra a 1/2 (artScale al .room.json).
ART_SCALE = 2
from hd1280.canvas2x import Canvas2x as Canvas  # noqa: E402,F811
from hd.pix import Canvas as Canvas1x  # noqa: E402,F401  (llenços auxiliars en píxels de sala: figures, textos)

K = 4 / 3
HOR = 131
QUAY = 171          # la vora del moll (el que hi ha per sota tapa la flotació)
RAILTOP = 176
FLOOR_Y = 200
SHIP = (235, 179, 5.6)
TABLE = (197, 445)  # x de la taula llarga
TOP = 195           # el sobre
TV = (504, 40, 587, 93)
SCR = (TV[0] + 4, TV[1] + 4, TV[2] - 4, TV[3] - 6)

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
TEAPOT = [(20, 40, 60), (36, 66, 96), (60, 100, 136), (100, 150, 180), (160, 200, 220)]
SCONE = [(80, 46, 20), (140, 90, 46), (196, 146, 86), (230, 190, 130), (246, 222, 174)]
JAM = [(70, 10, 20), (130, 20, 36), (180, 40, 56)]
HEATHER = [(40, 20, 40), (90, 40, 90), (150, 80, 140), (200, 130, 180)]
LEAF = [(20, 40, 24), (40, 70, 40), (64, 100, 56)]
GOLDLIT = (255, 196, 120)

LIGHT = Light(ambient=1.0, vignette=(67, 35), floor_fade=(293, 80))
LIGHT.point(40, 307, r=227, k=1.4, squash=0.8, power=1.5)        # la finestra del bar, darrere nostre
LIGHT.point(545, 69, r=93, k=0.8, power=1.8)                     # la tele


# ─── Cel, badia i turons ───────────────────────────────────────────────────

def sky(cv):
    for y in range(0, HOR + 1):
        t = y / HOR
        v = y / K
        for x in range(W):
            u = x / K
            lvl = 0.6 + 8.6 * t ** 1.7
            c = fbm(u / 90, v / 10, 51)
            k = smooth(0.58, 0.72, c) * (0.3 + 0.7 * smooth(0.1, 0.6, t))
            if k > 0:
                up = fbm(u / 90, (v + 1.5) / 10, 51)
                under = max(0.0, smooth(0.58, 0.72, c) - smooth(0.58, 0.72, up))   # la vora de sota: el sol de cara
                body = 2.6 + 3.0 * t + 4.2 * under + (fbm(u / 12, v / 4, 59) - 0.5) * 0.6
                lvl = lvl * (1 - k) + body * k
            cv.put(x, y, DAWN, lvl, lit=0)
    # la lluna, que se'n va, a ponent: mig plena, amb dues taques
    cv.disc(93, 40, 4, 4, [(150, 152, 176), (180, 182, 200), (210, 210, 220), (234, 232, 236)],
            lambda nx, ny: 2.6 - nx * 1.2 - ny * 0.3, lit=0)
    cv.flat(92, 39, (176, 178, 196))
    cv.flat(94, 42, (186, 186, 202))
    cv.glow(93, 40, 10, (200, 200, 220), 0.2)
    # dues estrelles que queden
    cv.flat(30, 14, (210, 210, 230))
    cv.flat(150, 22, (180, 182, 210))


def shore(cv):
    """Els turons de l'altra banda de la badia, amb els cims ja tocats de rosa, i cases petites a la vora."""
    for x in range(W):
        u = x / K
        top = HOR - (4 + 7 * fbm(u / 60, 0.5, 52) + 4 * fbm(u / 18, 1.5, 53)) * K
        for y in range(int(top), HOR + 2):
            lvl = 2.4 - (y - top) * 0.06 + (1.6 if y - top < 1.5 else 0)
            if (y - top) > 3 and hr(x // 3, y // 2, 60) > 0.93:
                lvl += 0.6                                         # camps i marges
            cv.put(x, y, SHORE, lvl, lit=0)
    # caseriu a la riba: cases blanques amb una finestra encesa
    for i, hx in enumerate((160, 176, 186, 300, 316, 520)):
        hy = HOR - 1
        cv.rect(hx, hy - 4, hx + 6, hy, SHORE, 4.0, lit=0)
        cv.poly([(hx - 1, hy - 4), (hx + 3, hy - 7), (hx + 7, hy - 4)], SHORE, 1.4, lit=0)
        if hr(i, 61) > 0.5:
            cv.flat(hx + 2, hy - 2, (255, 214, 140))
    # el far: torre blanca, el llum encès i el feix que s'esvaeix amb el dia
    fx, fy = 603, HOR - 17
    cv.rect(fx - 2, fy, fx + 2, HOR - 2, CREAM, lambda x, y: 4.6 - (x - fx + 2) * 0.4, lit=0)
    cv.hline(fx - 2, fx + 2, fy + 6, [(140, 30, 30), (190, 50, 44)], 1.0, lit=0)
    cv.rect(fx - 1, fy - 3, fx + 1, fy - 1, [(255, 230, 170)], 0, lit=0)
    cv.poly([(fx - 2, fy - 3), (fx, fy - 6), (fx + 2, fy - 3)], [(40, 30, 30), (90, 50, 44)], 1.0, lit=0)
    cv.glow(fx, fy - 2, 6, (255, 220, 160), 0.6)
    for i in range(36):                                           # el feix, cap a l'esquerra
        x = fx - 4 - i
        for y in (fy - 2, fy - 1):
            if hr(x, y, 62) < 0.5 * (1 - i / 36):
                cv.flat(x, y, mix(cv.get(x, y)[:3], (255, 230, 180), 0.35))


def bay(cv, phase=0.0, boat=True):
    for y in range(HOR + 2, QUAY + 5):
        v = y / K
        d = v - HOR / K
        for x in range(W):
            u = x / K
            sy = HOR / K - d * 2                                  # reflex del cel
            lvl = 0.6 + 8.6 * max(0, sy / (HOR / K)) ** 1.7 - 1.2
            n = fbm(u / (4 + d * 0.4) + phase, v / 1.2, 54)
            lvl += (n - 0.5) * 2.0
            cv.put(x, y, DAWN, lvl, lit=0)
    if not boat:
        return
    # una barqueta de pesca, lluny: casc, timoneria, pal amb el llum i el reflex
    bx, by = 80, HOR + 9
    cv.poly([(bx - 1, by - 2), (bx + 18, by - 2), (bx + 16, by + 2), (bx + 1, by + 2)], CREAM, 2.0, lit=0)
    cv.hline(bx, bx + 17, by - 2, CREAM, 3.6, lit=0)
    cv.hline(bx + 1, bx + 16, by + 1, [(120, 40, 40), (160, 60, 50)], 0.8, lit=0)
    cv.rect(bx + 5, by - 7, bx + 9, by - 3, CREAM, 2.8, lit=0)
    cv.flat(bx + 7, by - 5, (90, 110, 140))
    cv.vline(bx + 12, by - 15, by - 3, STEELX, 2.0, lit=0)
    cv.line(bx + 12, by - 15, bx + 2, by - 3, STEELX, 1.4, lit=0)
    cv.flat(bx + 12, by - 16, (255, 236, 200))
    for k in range(4):
        cv.hline(bx + 2 + k, bx + 15 - k, by + 3 + k, DAWN, 4.4 - k * 0.6, lit=0)


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
    for m in (25.5, 25.8, 26, 26.3, 26.5, 27.5, 27.8, 28, 28.3, 28.5):
        cv.put(X(m), Y(13.5), SUN, 3.0, lit=0)
        cv.put(X(m), Y(11.6), SUN, 2.4, lit=0)
    cv.glow(X(27), Y(15.6), 13, (255, 210, 140), 0.55)
    cv.flat(X(27), Y(15.6), (255, 244, 214))
    # caps d'amarratge cap al moll (dos fils)
    for m, qx in ((2, 200), (36, 480)):
        cv.line(X(m), Y(sheer(m) - 0.6), qx, QUAY + 2, ROPE, 3.0, lit=0)
        cv.line(X(m), Y(sheer(m) - 0.6) + 1, qx, QUAY + 3, ROPE, 1.8, lit=0)


def quay(cv):
    """El moll: carreus de pedra grisa, la vora amb les bites, una gavina i un fanal encara encès."""
    for y in range(QUAY, RAILTOP + 6):
        row = (y - QUAY) // 4
        for x in range(W):
            lvl = 3.2 - (y - QUAY) * 0.11 + (hr(x // 10, y // 4, 55) - 0.5) * 0.5
            if (y - QUAY) % 4 == 3 or (x + row * 9) % 22 == 0:
                lvl -= 1.0                                         # juntes dels carreus
            cv.put(x, y, STONE, lvl)
    cv.hline(0, W - 1, QUAY, STONE, 5.2)
    cv.hline(0, W - 1, QUAY + 1, STONE, 4.4)
    for bx in (197, 477):                                         # bites amb el cap fet una volta
        cv.rect(bx - 3, QUAY - 7, bx + 4, QUAY, IRON, lambda x, y: 3.4 - (x - bx + 3) * 0.25)
        cv.disc(bx + 0.5, QUAY - 7, 4.5, 1.6, IRON, 4.0)
        cv.hline(bx - 3, bx + 4, QUAY - 3, ROPE, 3.4)
    # la gavina, dreta damunt la bita de la dreta
    gx, gy = 478, QUAY - 9
    cv.disc(gx, gy - 3, 3, 2, [(150, 150, 150), (210, 210, 206), (240, 240, 236)], lambda nx, ny: 2.2 - ny, lit=0)
    cv.disc(gx + 3, gy - 6, 1.5, 1.5, [(210, 210, 206), (240, 240, 236)], 1.4, lit=0)
    cv.flat(gx + 5, gy - 6, (240, 180, 60))
    cv.hline(gx - 3, gx + 1, gy - 3, [(90, 92, 100), (120, 122, 130)], 1.0, lit=0)
    cv.vline(gx, gy - 1, gy, [(200, 140, 70)], 0, lit=0)
    # fanal
    for y in range(80, QUAY):
        cv.put(608, y, IRON, 2.6)
        cv.put(609, y, IRON, 1.6)
    cv.rect(603, 72, 614, 80, IRON, 2.4)
    cv.poly([(602, 72), (608, 67), (615, 72)], IRON, 3.0)
    cv.rect(605, 74, 612, 79, [(160, 120, 60), (240, 200, 120), (255, 236, 190)], 1.6, lit=0)
    cv.vline(608, 74, 79, IRON, 2.0)
    cv.glow(608, 77, 16, (255, 210, 140), 0.35)


# ─── La terrassa ───────────────────────────────────────────────────────────

def railing(cv):
    cv.rect(0, RAILTOP, W - 1, RAILTOP + 3, IRON, 3.6)
    cv.hline(0, W - 1, RAILTOP, IRON, 5.4)
    cv.hline(0, W - 1, RAILTOP + 3, IRON, 1.6)
    cv.rect(0, FLOOR_Y - 5, W - 1, FLOOR_Y - 3, IRON, 2.4)
    for x in range(4, W, 9):
        cv.vline(x, RAILTOP + 4, FLOOR_Y - 6, IRON, 2.6)
        cv.vline(x + 1, RAILTOP + 4, FLOOR_Y - 6, IRON, 1.4)
    # volutes entre els barrots, una de cada tres
    for x in range(8, W - 8, 27):
        cy = RAILTOP + 11
        for a in range(0, 330, 20):
            r = 2.5 + a / 150
            cv.put(x + 4 + round(math.cos(math.radians(a)) * r), cy + round(math.sin(math.radians(a)) * r), IRON, 3.0)
    # testos amb bruc als extrems
    for px in (16, 584):
        cv.rect(px, FLOOR_Y - 19, px + 40, FLOOR_Y, WOOD, lambda x, y: 3.2 - (y - FLOOR_Y + 19) * 0.06)
        cv.hline(px, px + 40, FLOOR_Y - 19, WOOD, 5.0)
        cv.hline(px, px + 40, FLOOR_Y - 10, WOOD, 1.8)
        for vx in range(px + 8, px + 40, 10):
            cv.vline(vx, FLOOR_Y - 18, FLOOR_Y, WOOD, 2.2)
        for i in range(90):
            fx = px + 2 + int(hr(i, px) * 36)
            fy = FLOOR_Y - 20 - int(hr(i, px + 1) * 14 * (1 - abs(fx - px - 20) / 30))
            cv.put(fx, fy, HEATHER, 1.0 + hr(i, 3) * 2.6)
            cv.put(fx, fy + 1, LEAF, 1.0 + hr(i, 4))


def floor(cv):
    """Terra de fusta de la terrassa, en perspectiva, amb claus a les juntes i el reflex càlid del bar."""
    vp = (240, 60)
    for y in range(FLOOR_Y, H):
        v = y / K
        d = v - vp[1]
        for x in range(W):
            u0 = x / K
            u = vp[0] + (u0 - vp[0]) * 120 / d
            u2 = vp[0] + (u0 + 1 / K - vp[0]) * 120 / d
            plank = int(u // 14)
            lvl = 2.8 + (hr(plank, int(v // 9), 56) - 0.5) * 0.6 + (fbm(u / 6, v / 30, 57) - 0.5) * 0.7
            if plank != int(u2 // 14):
                lvl -= 1.6
            elif int(v) % 9 == 0 and abs(u - plank * 14 - 2) < 0.6:
                lvl += 1.4                                       # un clau
            cv.put(x, y, WOOD, lvl)


def awning(cv):
    """El tendal: tela a ratlles verdes i crema, la vora de festons amb serrell, i els pals."""
    sw = 21
    for y in range(0, 16):
        for x in range(W):
            stripe = (x // sw) % 2
            lvl = 3.0 - y * 0.09 + (0.6 if y == 0 else 0) + (0.3 if x % sw == 0 else 0)
            cv.put(x, y, AWN if stripe else CREAM, lvl + (0 if stripe else 0.8), lit=0.5)
    for x in range(W):                                            # festons
        u = (x % sw) / sw
        h = 16 + int(5 * math.sin(u * math.pi))
        stripe = (x // sw) % 2
        for y in range(16, h + 1):
            cv.put(x, y, AWN if stripe else CREAM, 2.4 - (y - 16) * 0.16 + (0 if stripe else 0.8), lit=0.5)
        cv.put(x, h + 1, [(8, 10, 14)], 0, lit=0)
        if x % 2 == 0:                                           # serrell
            cv.put(x, h + 2, AWN if stripe else CREAM, 1.4 + (0 if stripe else 0.8), lit=0.5)
    cv.hline(0, W - 1, 15, AWN, 0.8, lit=0.5)                     # la vareta del tendal
    for px in (3, 627):
        for y in range(16, FLOOR_Y + 10):
            cv.put(px, y, IRON, 3.2)
            cv.put(px + 1, y, IRON, 4.2)
            cv.put(px + 2, y, IRON, 2.0)
        cv.rect(px - 1, FLOOR_Y + 8, px + 3, FLOOR_Y + 10, IRON, 2.4)


def tv_frame(cv):
    x0, y0, x1, y1 = TV
    cx = (x0 + x1) // 2
    for y in range(18, y0):                                        # el braç que la penja del tendal
        cv.put(cx, y, IRON, 3.0)
        cv.put(cx + 1, y, IRON, 1.8)
    cv.rect(cx - 6, y0 - 2, cx + 7, y0, IRON, 2.6)
    cv.rect(x0, y0, x1, y1, TABLER, 1.4)
    cv.hline(x0, x1, y0, TABLER, 3.0)
    cv.vline(x0, y0, y1, TABLER, 2.4)
    cv.hline(x0, x1, y1, TABLER, 0.6)
    cv.rect(x0 + 2, y1 - 2, x1 - 2, y1 - 1, TABLER, 0.8)
    cv.put(x1 - 4, y1 - 2, [(60, 255, 120)], 0, lit=0)


TICKER = 'SKARN NEGA ELS ABOCAMENTS AL PUNT 7  -  LES MOSTRES DE LA GAVINA ARRIBEN AL LABORATORI  -  '


def tv_news(cv, frame=0):
    """Les notícies: el plató blau, la imatge de la plataforma amb la taca, el presentador i la cinta que corre."""
    x0, y0, x1, y1 = SCR
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, [(8, 16, 46), (14, 28, 78), (22, 44, 112), (36, 70, 150), (70, 110, 190)],
                   2.4 - (y - y0) / 26 + (x - x0) / 80, lit=0)
    # la finestra amb la plataforma (gris, amb la taca)
    fx0, fy0, fx1, fy1 = x0 + 4, y0 + 4, x0 + 41, y0 + 29
    cv.rect(fx0 - 1, fy0 - 1, fx1 + 1, fy1 + 1, [(200, 210, 230)], 0, lit=0)
    cv.rect(fx0, fy0, fx1, fy1, [(70, 80, 90), (110, 120, 128), (150, 160, 166)], lambda x, y: 2.2 - (y - fy0) / 20, lit=0)
    cv.rect(fx0, fy1 - 7, fx1, fy1, [(30, 46, 58), (50, 70, 80)], 1.0, lit=0)
    cv.rect(fx0 + 8, fy0 + 7, fx0 + 26, fy0 + 11, [(30, 30, 34)], 0, lit=0)
    cv.rect(fx0 + 12, fy0 + 3, fx0 + 18, fy0 + 6, [(30, 30, 34)], 0, lit=0)
    cv.vline(fx0 + 23, fy0 + 1, fy0 + 6, [(30, 30, 34)], 0, lit=0)
    for lx in (fx0 + 10, fx0 + 16, fx0 + 22):
        cv.vline(lx, fy0 + 12, fy1 - 6, [(30, 30, 34)], 0, lit=0)
    cv.rect(fx0 + 4, fy1 - 6, fx0 + 32, fy1 - 4, [(110, 100, 70), (130, 118, 80)], 0.6, lit=0)
    # «EN DIRECTE» damunt la imatge
    cv.rect(fx0, fy0, fx0 + 8, fy0 + 6, [(180, 26, 30)], 0, lit=0)
    cv.flat(fx0 + 2, fy0 + 3, (255, 255, 255))
    # el presentador, a la dreta: cara, cabell, americana i corbata
    px = x1 - 15
    cv.disc(px, y0 + 12, 4, 5, [(150, 110, 90), (200, 150, 120), (226, 184, 150)], lambda nx, ny: 1.6 - nx * 0.5, lit=0)
    cv.rect(px - 4, y0 + 6, px + 4, y0 + 8, [(40, 30, 26), (70, 50, 40)], 0.8, lit=0)
    cv.rect(px - 9, y0 + 18, px + 9, y0 + 30, [(10, 10, 20), (24, 24, 40), (40, 40, 60)], 1.2, lit=0)
    cv.rect(px - 2, y0 + 18, px + 2, y0 + 23, [(230, 230, 230)], 0, lit=0)
    cv.vline(px, y0 + 19, y0 + 25, [(160, 30, 40)], 0, lit=0)
    # la cinta vermella («ÚLTIMA HORA») i la de sota, blanca, amb el text que corre
    cv.rect(x0, y1 - 13, x1, y1 - 7, [(120, 14, 20), (180, 26, 30), (220, 50, 44)], 1.6, lit=0)
    text(cv, 'ULTIMA HORA', x0 + 2, y1 - 12, [(255, 240, 230)], 0, lit=0, flat=(255, 240, 230))
    cv.rect(x0, y1 - 6, x1, y1, [(230, 230, 226)], 0, lit=0)
    tw = text_width(TICKER)
    off = (frame * 4) % tw
    tmp = Canvas1x(w=tw * 2 + 4, h=6, transparent=True)            # (en píxels de sala)
    text(tmp, TICKER + TICKER, 0, 0, [(30, 30, 40)], 0, lit=0, flat=(30, 30, 40))
    tp = tmp.img.load()
    for x in range(x0 + 1, x1):
        for y in range(5):
            if tp[x - x0 + off, y][3]:
                cv.flat(x, y1 - 5 + y, (30, 30, 40))
    cv.glow((x0 + x1) // 2, (y0 + y1) // 2, 45, (90, 140, 230), 0.10)


def tv_cable(cv):
    """El cable de la tele, que baixa pel braç i va fins a l'endoll del pal, passant per la punta de la taula."""
    x0, y0, x1, y1 = TV
    pts = [(x1 - 8, y1), (x1 - 5, y1 + 40), (TABLE[1] + 5, TOP - 3), (TABLE[1] + 13, TOP + 8), (627, 160)]
    n = 200
    for i in range(n + 1):
        t = i / n
        p = list(pts)
        while len(p) > 1:
            p = [((a[0] * (1 - t) + b[0] * t), (a[1] * (1 - t) + b[1] * t)) for a, b in zip(p, p[1:])]
        cv.put(round(p[0][0]), round(p[0][1]), [(8, 8, 10), (20, 20, 24), (36, 36, 42)], 1.4)
        cv.put(round(p[0][0]) + 1, round(p[0][1]), [(8, 8, 10), (20, 20, 24), (36, 36, 42)], 0.6)
    cv.rect(622, 156, 627, 164, [(200, 200, 196), (230, 230, 226)], 1.0)   # l'endoll


def chairs(cv):
    """Cadires de bistrot darrere la taula: respatller de vímet amb el marc de ferro."""
    for cx in range(221, TABLE[1] - 10, 53):
        cv.rect(cx - 9, TOP - 30, cx + 9, TOP - 27, IRON, 3.0)
        cv.hline(cx - 9, cx + 9, TOP - 30, IRON, 4.4)
        for k in (-9, 9):
            cv.vline(cx + k, TOP - 30, TOP, IRON, 2.4)
        for y in range(TOP - 26, TOP - 11):
            for x in range(cx - 8, cx + 9):
                if (x + y) % 3 == 0:
                    cv.put(x, y, [(60, 40, 24), (110, 80, 48), (160, 120, 76)], 1.4 + (y - TOP + 26) * 0.04)
        cv.hline(cx - 9, cx + 9, TOP - 11, IRON, 2.6)


def table(cv):
    """La taula llarga: dues taules ajuntades, amb cafès, una tetera, el diari, el sucrer i un plat de scones."""
    x0, x1 = TABLE
    cv.rect(x0, TOP - 4, x1, TOP, WOOD, lambda x, y: 5.6 - (TOP - y) * 0.25 + (hr(x // 6, y, 58) - 0.5) * 0.5)
    for gx in range(x0 + 4, x1, 7):                                  # veta
        if hr(gx, 63) > 0.5:
            cv.hline(gx, gx + 4, TOP - 2, WOOD, 4.6)
    cv.rect(x0, TOP + 1, x1, TOP + 7, WOOD, lambda x, y: 3.6 - (y - TOP) * 0.15)
    cv.hline(x0, x1, TOP + 1, WOOD, 6.4)
    cv.hline(x0, x1, TOP + 7, WOOD, 1.6)
    cv.vline((x0 + x1) // 2, TOP - 4, TOP + 7, WOOD, 1.0)
    for lx in (x0 + 8, (x0 + x1) // 2 - 8, (x0 + x1) // 2 + 8, x1 - 8):
        cv.rect(lx - 1, TOP + 8, lx + 2, 237, TABLER, 2.6)
        cv.vline(lx - 1, TOP + 8, 237, TABLER, 3.8)
        cv.rect(lx - 8, 237, lx + 8, 240, TABLER, 1.8)
        cv.hline(lx - 8, lx + 8, 237, TABLER, 3.4)
    # tasses amb plat i cullereta
    for mx in CUPS:
        cv.disc(mx + 3.5, TOP - 3, 7, 1.6, CUPR, 3.8)
        cv.rect(mx, TOP - 11, mx + 7, TOP - 4, CUPR, lambda x, y: 3.6 - (x - mx) * 0.2)
        cv.hline(mx, mx + 7, TOP - 11, CUPR, 4.4)
        cv.hline(mx + 1, mx + 6, TOP - 10, [(40, 22, 10), (70, 40, 20)], 0.8)
        for yy in (TOP - 10, TOP - 9, TOP - 8, TOP - 7):
            cv.put(mx + 8 + (1 if TOP - 9 <= yy <= TOP - 8 else 0), yy, CUPR, 2.4)
        cv.line(mx - 3, TOP - 3, mx - 7, TOP - 2, STEELX, 4.2)
    # la tetera amb la tapa i la nansa
    tx, ty = 309, TOP - 11
    cv.disc(tx, ty, 8, 7, TEAPOT, lambda nx, ny: 2.4 - nx - ny)
    cv.disc(tx - 2, ty - 3, 2, 1.5, TEAPOT, 4.4)                     # la lluentor
    cv.line(tx + 8, ty - 1, tx + 13, ty - 5, TEAPOT, 1.8)
    cv.line(tx + 8, ty, tx + 13, ty - 4, TEAPOT, 1.0)
    cv.rect(tx - 3, ty - 9, tx + 3, ty - 7, TEAPOT, 1.6)
    cv.disc(tx, ty - 10, 1.5, 1, TEAPOT, 3.0)
    cv.ring(tx - 10, ty, 4, TEAPOT, 1.6, step=20)
    # el sucrer
    cv.rect(437, TOP - 8, 443, TOP - 1, CUPR, 3.0)
    cv.disc(440, TOP - 9, 3.5, 1, CUPR, 4.2)
    cv.line(441, TOP - 9, 444, TOP - 14, STEELX, 4.0)
    # el diari, plegat, amb les columnes i la foto
    cv.poly([(349, TOP - 3), (379, TOP - 5), (382, TOP), (352, TOP)], CREAM, 4.8)
    cv.hline(353, 364, TOP - 2, CREAM, 1.8)
    cv.hline(367, 378, TOP - 3, CREAM, 2.6)
    cv.hline(367, 378, TOP - 2, CREAM, 2.6)
    cv.rect(355, TOP - 1, 360, TOP - 1, [(90, 90, 96)], 0)
    # scones amb melmelada i nata
    cv.disc(253, TOP - 2, 11, 2, CUPR, 4.0)
    for sx in (247, 257):
        cv.disc(sx, TOP - 6, 4, 3, SCONE, lambda nx, ny: 2.8 - ny - nx * 0.4)
        cv.hline(sx - 3, sx + 3, TOP - 6, SCONE, 1.2)
    cv.disc(247, TOP - 8, 2, 1, JAM, 1.6)
    cv.disc(257, TOP - 8, 2, 1, [(200, 196, 180), (240, 236, 222)], 1.0)


CUPS = (224, 275, 336, 389, 429)


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
    cv.glow(53, 307, 93, GOLDLIT, 0.10)                          # la llum del bar, darrere nostre


def tele_apagada(cv):
    x0, y0, x1, y1 = SCR
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, [(4, 5, 8), (8, 10, 14), (14, 16, 22), (22, 26, 34)], 1.0 + (x - x0) / 66 - (y - y0) / 80, lit=0)
    # el reflex del cel a la pantalla negra, i la silueta del tendal
    for k in range(8):
        cv.line(x0 + 8 + k, y0 + 2, x0 + 3 + k, y0 + 13, [(60, 60, 90)], 0, lit=0)
    for x in range(x0, x1 + 1):
        if (x // 5) % 2:
            cv.flat(x, y0 + 1, (30, 36, 40))


PROPS = {'tele_apagada': tele_apagada}

# La taula tapa les cames de qui seu al darrere. El sobre queda fora, perquè en Diu s'hi pugui enfilar.
FRONT = {'mask': lambda x, y: TABLE[0] - 8 <= x <= TABLE[1] + 8 and TOP + 1 <= y <= 240,
         'baseline': 243, 'zIndex': 20}


def _frames():
    base = Canvas(light=LIGHT)
    bg(base)
    frames = []
    for i in range(8):
        cv = Canvas(light=LIGHT, img=base.img.copy())
        tv_news(cv, i)
        frames.append(_diff(cv.img, base.img))
    return frames


# L'aigua de la badia: el soroll corre de costat; els darrers BAY_FADE fotogrames es fonen amb el principi
# perquè el bucle no salti. Només es toquen els píxels on es veu l'aigua (no el vaixell, el moll ni la barqueta).
BAY_N, BAY_FADE, BAY_STEP = 12, 4, 0.09


def _frames_badia():
    base = Canvas(light=LIGHT)
    bg(base)
    ref = Canvas(light=LIGHT)
    bay(ref, 0.0, boat=False)
    rp, bp = ref.img.load(), base.img.load()
    S = base.S                                                        # (en píxels reals: art a 2×)
    open_ = [(X, Y) for Y in range((HOR + 3) * S, (QUAY + 5) * S) for X in range(base.w) if bp[X, Y] == rp[X, Y]]
    frames = []
    for i in range(BAY_N):
        a, b = Canvas(light=LIGHT), Canvas(light=LIGHT)
        bay(a, i * BAY_STEP, boat=False)
        bay(b, (i - BAY_N) * BAY_STEP, boat=False)
        w = max(0, i - (BAY_N - BAY_FADE)) / BAY_FADE
        out = base.img.copy()
        o, ap, bpp = out.load(), a.img.load(), b.img.load()
        for X, Y in open_:
            o[X, Y] = bpp[X, Y] if hr(X // S, Y // S, 91) < w else ap[X, Y]
        frames.append(_diff(out, base.img))
    return frames


# El vapor: tres bufs per tassa (i el broc de la tetera) que pugen, es tremolen i s'esvaeixen.
STEAM = [(mx + 3.5, TOP - 12) for mx in CUPS] + [(322, TOP - 17)]
STEAM_N = 32


def _frames_vapor():
    base = Canvas(light=LIGHT)
    bg(base)
    frames = []
    for i in range(STEAM_N):
        cv = Canvas(light=LIGHT, img=base.img.copy())
        for j, (sx, sy) in enumerate(STEAM):
            for k in range(3):
                t = (i / STEAM_N + k / 3 + hr(j, 92)) % 1.0         # 0: surt de la tassa, 1: s'ha esvaït
                x = sx + math.sin(t * 5 + j * 1.7) * (0.7 + 2.7 * t)
                y = sy - t * 19
                a = 0.45 * (1 - t) ** 1.2
                pts = ((0, 0), (1, 0), (0, -1), (1, -1)) if t < 0.4 else ((0, 0), (0, -1)) if t < 0.7 else ((0, 0),)
                for dx, dy in pts:
                    px, py = round(x + dx), round(y + dy)
                    o = cv.get(px, py)
                    cv.flat(px, py, mix(o[:3], (236, 232, 226), a))
        frames.append(_diff(cv.img, base.img))
    return frames


ANIMS = {'tele': {'frames': _frames, 'frameDuration': 220},
         'badia': {'frames': _frames_badia, 'frameDuration': 240},
         'vapor': {'frames': _frames_vapor, 'frameDuration': 150}}

GEOMETRIA = {
    'things': {},
    'spawns': {'iri': (165, 256), 'vet': (480, 256), 'diu': (424, 195), 'capitana': (235, 227),
               'nadia': (291, 227), 'marcel': (349, 227), 'tomas': (405, 227)},
    'walkable': [(133, 248), (507, 248), (507, 267), (133, 267)],
}
