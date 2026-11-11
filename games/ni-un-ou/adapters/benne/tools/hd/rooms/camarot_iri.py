"""
El camarot de l'Iri (Escena 1, 3:40 de la matinada): el més petit del vaixell, al costat de les màquines.
La llitera feta, el carregador mossegat a l'endoll, la motxilla d'en Diu (amb forats per respirar), l'ull de bou
fosc, la porta entreoberta, la granota penjada i el pòster d'un motor amb una foto amb en Bastida.
"""
import math

from hd.pix import Canvas, Light, W, H, hr, mix, B4, WALNUT, NAVY, PAPER
from hd.rooms.arenga import (WALL, ENG, CAB, DARK, WHITEP, YELL, REDP, SEAG, BRASS, WARM, FLOOR_Y, BOTTOM,
                             box, rrect, bolt, hpipe, vpipe, glow)
from hd.rooms.comu import text, _diff
from hd.rooms import sota

LIGHT = Light(ambient=-0.45, vignette=(50, 26), floor_fade=None)
LIGHT.point(42, 100, r=190, k=2.9, squash=1.1, power=1.5)          # el llum de lectura de la llitera
LIGHT.point(450, 104, r=90, k=1.3, squash=0.8, power=1.8)         # el passadís, per la porta
LIGHT.point(310, 70, r=36, k=0.4, power=2.0)                      # l'ull de bou (gairebé res)

# rampes del camarot
PAINT = [(10, 14, 14), (18, 24, 23), (28, 36, 34), (40, 50, 46), (54, 66, 60), (70, 84, 76), (90, 104, 94),
         (114, 128, 114), (142, 154, 138), (172, 182, 164)]                       # paret pintada, verd pàl·lid
LINO = [(10, 9, 9), (18, 16, 15), (28, 25, 22), (40, 35, 30), (54, 47, 39), (70, 61, 50), (90, 78, 62),
        (112, 98, 78)]                                                             # linòleum
BLANKET = [(8, 10, 22), (14, 18, 36), (22, 28, 52), (32, 40, 70), (46, 56, 90), (64, 76, 112), (90, 102, 136)]
SHEET = [(40, 42, 48), (74, 78, 84), (118, 122, 126), (160, 162, 162), (196, 196, 190), (224, 222, 214)]
OLIVE = [(14, 16, 8), (24, 28, 14), (38, 44, 22), (54, 62, 32), (72, 82, 44), (94, 104, 58), (120, 130, 76)]
OVERALL = [(6, 10, 20), (12, 18, 34), (20, 28, 50), (30, 40, 68), (42, 56, 88), (60, 76, 110)]
SEA = [(2, 4, 8), (4, 8, 14), (8, 14, 22), (14, 22, 32), (24, 36, 48), (44, 60, 72), (80, 100, 110)]

DOOR = (406, 62, 454, FLOOR_Y)


# ─── Paret, sostre i terra ──────────────────────────────────────────────────

def walls(cv):
    sota.plate_wall(cv, 0, W - 1, ramp=PAINT, lvl=3.6, frames=96, frame0=-4, seams=(58,), socle=138, rust=8, seed=3)
    # sostre baix, amb un tub d'aigua de mar i una safata de cables (és al costat de les màquines)
    cv.rect(0, 0, W - 1, 15, DARK, 2.2)
    for bx in range(-4, W, 96):
        box(cv, bx - 2, 0, bx + 8, 17, PAINT, 2.0, grad=0.6)
    cv.hline(0, W - 1, 16, PAINT, 1.4)
    hpipe(cv, 0, W - 1, 8, 3, SEAG, 2.8, bands=range(30, W, 70), band_ramp=WHITEP)
    for x in range(20, W, 60):
        cv.vline(x, 3, 13, CAB, 2.4)
        cv.vline(x + 1, 3, 13, CAB, 3.6)
    # el llum del sostre, apagat
    rrect(cv, 228, 17, 260, 22, 2, CAB, 3.0)
    cv.rect(231, 20, 257, 22, [(40, 40, 36), (70, 68, 60), (100, 98, 88)], 1.4, lit=0.3)


def floor(cv):
    """Linòleum amb rajoles en perspectiva i una catifa davant la llitera."""
    vp = (240, 30)
    mask = [[False] * W for _ in range(H)]
    for y in range(FLOOR_Y, BOTTOM + 12):
        d = y - vp[1]
        for x in range(W):
            u = vp[0] + (x - vp[0]) * 150 / d
            u2 = vp[0] + (x + 1 - vp[0]) * 150 / d
            lv = 3.0 + (hr(x // 2, y // 2, 5) - 0.5) * 0.5
            if int(u // 40) != int(u2 // 40):
                lv -= 0.9
            elif y in (160, 173, 191):
                lv -= 0.8
            cv.put(x, y, LINO, lv)
            mask[y][x] = True
    cv.hline(0, W - 1, FLOOR_Y, LINO, 1.2)
    # catifa (de ratlles, vella)
    pts = [(70, 164), (200, 164), (212, 186), (58, 186)]
    RUG = [(22, 14, 14), (40, 24, 22), (62, 36, 30), (86, 50, 38), (110, 68, 50), (134, 90, 66)]
    cv.poly(pts, RUG, lambda x, y: 2.8 + (1.0 if (y // 3) % 3 == 0 else 0) - (0.6 if hr(x // 3, y) > 0.85 else 0))
    for x in range(60, 212, 3):
        cv.put(x, 187, RUG, 3.6)
    cv.line(70, 164, 200, 164, RUG, 4.2)
    return mask


# ─── La llitera ─────────────────────────────────────────────────────────────

def bunk(cv):
    x0, x1 = 14, 172
    # la cortina recollida a l'esquerra i la barra
    cv.hline(10, 176, 64, CAB, 3.6)
    cv.hline(10, 176, 65, CAB, 1.8)
    CURT = [(16, 22, 30), (26, 36, 48), (40, 54, 68), (58, 74, 88), (80, 98, 110)]
    for y in range(66, 136):
        for x in range(8, 22):
            f = math.sin((x - 8) * 1.1 + y * 0.02)
            cv.put(x, y, CURT, 2.4 + f * 0.9 - (y - 66) * 0.006)
    for x in range(8, 22, 3):
        cv.put(x, 66, CAB, 4.0)
    # el plafó de fusta del capçal i dels peus
    box(cv, 14, 92, 22, 158, WALNUT, 3.4)
    box(cv, 164, 98, 172, 158, WALNUT, 3.0)
    # el matalàs, amb el llençol girat i la manta ben estirada (feta com un llit d'hospital)
    cv.rect(22, 118, 164, 132, BLANKET, lambda x, y: 3.2 - (y - 118) * 0.06)
    cv.hline(22, 164, 118, BLANKET, 4.4)
    for x in range(26, 162, 2):                                # la vora de la manta, ben plegada
        cv.put(x, 131, BLANKET, 1.6)
    cv.rect(52, 117, 62, 132, SHEET, lambda x, y: 3.6 - (y - 117) * 0.05)   # el llençol girat
    cv.vline(62, 117, 132, SHEET, 2.0)
    # el coixí
    rrect(cv, 24, 108, 50, 120, 4, SHEET, lambda x, y: 4.2 - (y - 108) * 0.08 - (x - 24) * 0.01)
    cv.hline(28, 46, 110, SHEET, 5.0)
    # el costat de la llitera (fusta) i els dos calaixos
    box(cv, 22, 132, 164, 158, WALNUT, 3.0, grad=0.6)
    cv.hline(22, 164, 133, WALNUT, 4.4)
    for dx in (28, 98):
        box(cv, dx, 138, dx + 62, 154, WALNUT, 2.6)
        box(cv, dx + 25, 144, dx + 37, 147, BRASS, 3.6)
    # el llum de lectura, a la paret del capçal
    box(cv, 28, 92, 36, 98, CAB, 3.0)
    cv.line(33, 94, 42, 92, CAB, 3.4)
    cv.poly([(38, 92), (50, 92), (48, 100), (40, 100)], BRASS, lambda x, y: 3.8 - (y - 92) * 0.12, lit=0.4)
    cv.hline(41, 47, 100, [(160, 130, 70), (255, 236, 180)], 1.2, lit=0)


def shelf(cv):
    """El prestatge de damunt la llitera: eines petites, un multímetre, una llauna i dos llibres."""
    box(cv, 60, 82, 162, 86, WALNUT, 3.4)
    for bx in (66, 156):
        cv.poly([(bx, 87), (bx + 2, 87), (bx + 2, 94)], CAB, 3.0)
    # barana (perquè no caigui res quan balla)
    cv.hline(60, 162, 76, BRASS, 3.0)
    for x in (61, 110, 161):
        cv.vline(x, 76, 82, BRASS, 2.6)
    # multímetre groc
    box(cv, 66, 66, 78, 81, YELL, 3.4)
    cv.rect(68, 68, 76, 72, [(20, 30, 24), (60, 80, 60), (130, 160, 120)], 1.6, lit=0.3)
    cv.disc(72, 77, 2, 2, CAB, 2.0)
    # llauna de galetes (plena de cargols)
    rrect(cv, 84, 70, 100, 81, 2, REDP, lambda x, y: 3.6 - (x - 84) * 0.05)
    cv.hline(84, 100, 70, REDP, 5.0)
    cv.hline(85, 99, 73, WHITEP, 3.6)
    # llibres (manuals) drets
    for i, (col, h) in enumerate((([(20, 30, 50), (40, 60, 100), (70, 100, 150)], 18),
                                  ([(40, 20, 16), (90, 40, 30), (140, 70, 50)], 15),
                                  ([(30, 40, 30), (60, 80, 60), (100, 120, 90)], 17))):
        x = 106 + i * 6
        cv.rect(x, 81 - h, x + 4, 81, col, 1.8)
        cv.vline(x, 81 - h, 81, col, 2.6)
        cv.hline(x + 1, x + 3, 81 - h + 3, PAPER, 3.0)
    # claus fixes, penjades de cantó a la barana
    for i, x in enumerate((128, 134, 140, 146)):
        ln = 8 + i * 2
        cv.vline(x, 77, 77 + ln, CAB, 4.4)
        cv.disc(x, 77 + ln, 2, 2, CAB, 4.0)
        cv.put(x, 77 + ln, DARK, 1.0)


# ─── Endoll, tauleta, pòster, ull de bou, granota ───────────────────────────

def locker(cv):
    # la tauleta (calaixera de planxa)
    box(cv, 176, 130, 206, 158, PAINT, 4.0, grad=0.8)
    cv.hline(176, 206, 131, PAINT, 5.4)
    box(cv, 180, 138, 202, 155, PAINT, 3.6)
    box(cv, 187, 143, 195, 145, CAB, 3.6)
    # el despertador: 3:40
    box(cv, 190, 122, 204, 129, CAB, 2.2)
    cv.rect(191, 123, 203, 128, DARK, 0.4, lit=0)
    for px, py in _digits('340', 192, 124):
        cv.flat(px, py, (255, 76, 52))
    cv.flat(196, 125, (200, 50, 40))
    cv.flat(196, 127, (200, 50, 40))
    glow(cv, 197, 125, 8, (255, 60, 40), 0.35)
    # l'endoll (doble, de paret)
    box(cv, 180, 112, 192, 120, WHITEP, 3.6)
    for sx in (183, 188):
        cv.put(sx, 115, DARK, 0.5)
        cv.put(sx + 1, 115, DARK, 0.5)
    # el carregador endollat i el cable (blanc) mossegat a trossos, que penja fins a la tauleta
    box(cv, 182, 114, 186, 121, WHITEP, 3.8)
    CABLE = [(60, 60, 58), (150, 150, 146), (214, 214, 206), (240, 240, 232)]
    pts = [(184, 122), (184, 125), (182, 128), (179, 130)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        cv.line(ax, ay, bx, by, CABLE, 2.8)
    # mossegades: el coure pelat a la punta i trossos de cable caiguts damunt la tauleta
    cv.put(179, 131, BRASS, 4.6)
    cv.put(178, 131, BRASS, 3.8)
    for x0, x1 in ((181, 186), (189, 192)):
        cv.line(x0, 129, x1, 129, CABLE, 2.6)
        cv.put(x1 + 1, 129, BRASS, 4.4)
        cv.put(x0, 129, CABLE, 1.4)
    cv.put(184, 125, BRASS, 4.4)                                  # una dentada a mig cable


def _digits(s, x, y):
    """Xifres de 3×5 per al despertador (amb un buit per als dos punts després de la primera)."""
    from hd.rooms.comu import GLYPHS
    pts = []
    cx = x
    for i, ch in enumerate(s):
        for j, row in enumerate(GLYPHS[ch]):
            for k, b in enumerate(row):
                if b == '1':
                    pts.append((cx + k, y + j))
        cx += 4 if i else 6
    return pts


def poster(cv):
    """Un pòster de motor (un tall d'un dièsel marí) i una foto, al cantó, de l'Iri amb en Bastida."""
    x0, y0, x1, y1 = 214, 34, 276, 98
    box(cv, x0, y0, x1, y1, PAPER, 3.6)
    cv.rect(x0 + 2, y0 + 2, x1 - 2, y1 - 12, [(10, 20, 40), (16, 34, 64), (24, 50, 88), (40, 74, 120)], 2.0)
    # el motor en tall: bloc, pistons, cigonyal
    cx = 244
    box(cv, cx - 18, 52, cx + 18, 78, [(30, 60, 80), (60, 110, 130), (110, 160, 170), (180, 210, 210)], 1.8)
    for i in range(4):
        px = cx - 15 + i * 8
        box(cv, px, 50 + (i % 2) * 4, px + 5, 60 + (i % 2) * 4, [(60, 40, 30), (150, 90, 50), (220, 150, 90)], 1.6)
        cv.vline(px + 2, 60 + (i % 2) * 4, 76, [(120, 120, 120), (200, 200, 200)], 0.8)
    cv.disc(cx, 79, 16, 4, [(40, 40, 40), (110, 110, 110), (180, 180, 180)], 1.2)
    cv.hline(cx - 22, cx + 22, 46, [(160, 40, 30), (240, 90, 60)], 1.0)
    # títol: dues ratlles
    for y in (y1 - 9, y1 - 6):
        for x in range(x0 + 5, x1 - 5):
            if hr(x // 2, y) > 0.3:
                cv.put(x, y, PAPER, 0.8)
    # la foto, posada al cantó: dues persones davant d'un motor
    fx0, fy0 = 258, 84
    box(cv, fx0, fy0, fx0 + 16, fy0 + 12, WHITEP, 4.4)
    cv.rect(fx0 + 1, fy0 + 1, fx0 + 15, fy0 + 9, SEAG, 2.2)
    for px, col in ((fx0 + 5, [(40, 20, 10), (120, 80, 50), (200, 150, 110)]), (fx0 + 10, [(60, 60, 60), (180, 180, 180), (240, 240, 240)])):
        cv.put(px, fy0 + 3, col, 1.6)
        cv.rect(px - 1, fy0 + 5, px + 1, fy0 + 9, OVERALL if px == fx0 + 5 else [(60, 50, 40), (130, 120, 100), (180, 170, 150)], 2.6)
    # xinxetes
    for px, py in ((x0 + 2, y0 + 2), (x1 - 2, y0 + 2), (x0 + 2, y1 - 2), (x1 - 2, y1 - 2), (fx0 + 8, fy0 + 1)):
        cv.put(px, py, REDP, 4.4)


def porthole_glass(cv, t=0.0):
    """L'interior de l'ull de bou: mar fosc i escuma que passa (t, de 0 a 1, per a l'animació)."""
    cx, cy = 310, 70
    for y in range(cy - 15, cy + 16):
        for x in range(cx - 15, cx + 16):
            if (x - cx) ** 2 + (y - cy) ** 2 <= 15 * 15:
                hor = cy - 2 + math.sin(x * 0.2 + t * 6.28) * 1.5
                if y < hor:
                    lv = 1.6 + (y - (cy - 15)) * 0.03
                    cv.put(x, y, SEA, lv, lit=0)
                else:
                    foam = math.sin(x * 0.45 + y * 1.3 - t * 6.28 * 2) + math.sin(x * 0.17 - t * 6.28) > 1.5
                    cv.put(x, y, SEA, 2.4 + (2.2 if foam else 0) - (y - hor) * 0.04, lit=0)
    # esquitxos al vidre
    for i in range(9):
        a = hr(i, 1) * 6.28
        r = hr(i, 2) * 12
        px, py = cx + math.cos(a) * r, cy + math.sin(a) * r
        py = py + (t * 8 + hr(i, 3) * 8) % 8
        if (px - cx) ** 2 + (py - cy) ** 2 < 13 * 13:
            cv.put(px, py, SEA, 5.4, lit=0)
    # reflex del llum de la cabina al vidre
    cv.line(cx - 8, cy - 9, cx - 4, cy - 12, WHITEP, 2.4, lit=0)


def porthole(cv):
    cx, cy = 310, 70
    cv.disc(cx, cy, 20, 20, BRASS, lambda nx, ny: 3.2 - nx * 1.1 - ny * 1.3)
    cv.disc(cx, cy, 17, 17, BRASS, lambda nx, ny: 2.0 + nx * 0.8 + ny * 0.9)
    porthole_glass(cv)
    for a in range(0, 360, 45):
        bolt(cv, round(cx + math.cos(math.radians(a)) * 18.5), round(cy + math.sin(math.radians(a)) * 18.5), BRASS, 3.2)
    # les dues palometes per tancar la tapa de tempesta
    for dx in (-24, 22):
        box(cv, cx + dx, cy - 2, cx + dx + 2, cy + 6, BRASS, 3.4)
    # la tapa de tempesta, oberta i penjant a sota (per de dins)
    cv.disc(cx, cy + 25, 14, 3, BRASS, lambda nx, ny: 2.6 - ny)
    cv.hline(cx - 2, cx + 2, cy + 21, BRASS, 3.6)


def overalls(cv):
    """La granota de recanvi i els protectors d'orelles, penjats d'uns ganxos al costat de la porta."""
    # ganxos
    box(cv, 344, 52, 394, 55, WALNUT, 3.2)
    for hx in (352, 380):
        cv.vline(hx, 55, 60, BRASS, 3.8)
        cv.put(hx + 1, 60, BRASS, 3.0)
    # la granota: espatlles, mànigues i camals penjant
    body = [(344, 62), (362, 60), (366, 70), (366, 120), (362, 146), (354, 146), (354, 122), (350, 122),
            (350, 146), (340, 146), (338, 118), (338, 70)]
    cv.poly(body, OVERALL, lambda x, y: 3.2 - abs(x - 352) * 0.05 - (y - 60) * 0.006)
    cv.poly([(338, 70), (344, 64), (338, 112), (334, 110)], OVERALL, 2.4)   # mànega
    cv.poly([(362, 62), (366, 70), (370, 110), (366, 112)], OVERALL, 2.0)
    cv.vline(352, 64, 118, OVERALL, 1.4)                                     # cremallera
    cv.vline(353, 64, 118, OVERALL, 4.0)
    cv.line(348, 120, 348, 145, OVERALL, 1.6)
    box(cv, 342, 82, 350, 90, OVERALL, 2.8)                                  # butxaca
    for y in (100, 101):                                                     # banda reflectant
        cv.hline(339, 365, y, YELL, 3.4 if y == 100 else 2.2)
    cv.rect(342, 66, 350, 69, YELL, 3.0)                                    # el nom brodat
    # protectors d'orelles, penjats de l'altre ganxo
    cv.ring(381, 66, 7, YELL, 3.6, step=6)
    for a in range(200, 341, 4):
        cv.put(381 + round(math.cos(math.radians(a)) * 7), 66 + round(math.sin(math.radians(a)) * 7), YELL, 3.6)
    for ex in (374, 388):
        rrect(cv, ex - 3, 66, ex + 3, 76, 2, YELL, lambda x, y: 3.4 - (x - ex + 3) * 0.12)
        cv.vline(ex, 68, 74, DARK, 1.0)


def door(cv):
    """La porta del camarot, entreoberta: la fulla gira cap endins i deixa veure el passadís, il·luminat."""
    x0, y0, x1, y1 = DOOR
    # el passadís, a l'altra banda, amb llum (una paret verda i un llum de gàbia)
    for y in range(y0, y1):
        for x in range(x0, x1 + 1):
            if sota.in_door(x, y, x0, y0, x1, y1, 6):
                if y > 140:
                    cv.put(x, y, sota.DECK, 3.4 + (0.8 if (x + y) % 4 == 0 else 0), lit=0.5)
                else:
                    cv.put(x, y, WALL, 4.0 - abs(y - 92) * 0.012 + (0.6 if y in (100, 101) else 0), lit=0.5)
    vpipe(cv, 446, y0 + 2, 140, 2, SEAG, 3.6, bands=(96,), band_ramp=WHITEP)
    cv.hline(x0, x1, 140, WALL, 2.0)
    sota.door_frame(cv, x0, y0, x1, y1, ramp=PAINT, lvl=4.6, r=6)
    # la fulla, girada cap a nosaltres: la vora lliure, més alta i més ampla (perspectiva)
    fx = 432
    leaf = [(x0, y0 + 1), (fx, y0 - 4), (fx, y1 + 6), (x0, y1)]
    cv.poly(leaf, PAINT, lambda x, y: 3.0 - (x - x0) * 0.025)
    cv.poly([(x0 + 5, y0 + 8), (fx - 5, y0 + 4), (fx - 5, y0 + 40), (x0 + 5, y0 + 42)], PAINT,
            lambda x, y: 3.4 - (x - x0) * 0.025)
    cv.poly([(x0 + 5, y1 - 26), (fx - 5, y1 - 24), (fx - 5, y1 - 2), (x0 + 5, y1 - 4)], PAINT,
            lambda x, y: 3.2 - (x - x0) * 0.025)
    # reixeta de ventilació a baix de la fulla
    for i in range(5):
        cv.line(x0 + 9, y1 - 21 + i * 3, fx - 9, y1 - 19 + i * 3, PAINT, 1.4)
    cv.vline(fx, y0 - 4, y1 + 6, PAINT, 5.0)                                # el cantell de la fulla
    cv.vline(fx + 1, y0 - 3, y1 + 6, PAINT, 2.0)
    # la maneta
    box(cv, fx - 7, 104, fx - 4, 112, BRASS, 3.6)
    cv.hline(fx - 12, fx - 5, 106, BRASS, 4.6)
    # número del camarot
    box(cv, 418, 70, 428, 76, BRASS, 3.6)
    cv.hline(420, 426, 73, BRASS, 1.4)


def door_light(cv):
    """La llum del passadís que entra per la porta i fa una falca a terra."""
    for y in range(FLOOR_Y, BOTTOM + 8):
        t = (y - FLOOR_Y) / 44
        xa, xb = 441 - t * 30, 454 - t * 6
        for x in range(int(xa), int(xb) + 1):
            k = 0.3 * (1 - t * 0.7)
            if k > B4[y & 3][x & 3] * 0.6:
                cv.flat(x, y, mix(cv.get(x, y), (150, 170, 140), k))


# ─── Motxilla ───────────────────────────────────────────────────────────────

def backpack(cv):
    """La motxilla d'en Diu, dreta a terra: oberta de dalt, amb forats per respirar fets a mà."""
    sota.floor_shadow(cv, 242, 158, 24, 3, 0.7)
    # el cos (cantons de dalt rodons)
    rrect(cv, 226, 126, 258, 157, 9, OLIVE, lambda x, y: 3.3 - (x - 226) * 0.035 - (y - 126) * 0.008)
    cv.vline(227, 134, 155, OLIVE, 4.2)
    # la boca oberta (fosca) i la tapa caiguda cap enrere
    cv.disc(242, 128, 11, 3, DARK, 1.0)
    cv.poly([(231, 126), (253, 126), (255, 121), (229, 121)], OLIVE, 2.4)
    cv.hline(229, 255, 121, OLIVE, 3.8)
    cv.hline(231, 253, 126, OLIVE, 4.6)
    # la butxaca de davant amb la cremallera
    rrect(cv, 231, 140, 253, 155, 4, OLIVE, lambda x, y: 3.9 - (x - 231) * 0.035)
    cv.hline(233, 251, 140, OLIVE, 5.2)
    cv.hline(234, 250, 143, CAB, 2.2)
    box(cv, 249, 142, 251, 146, CAB, 4.4)
    # forats per respirar, fets amb un punxó (amb la vora clara)
    for hx, hy in ((233, 131), (240, 132), (247, 131), (252, 134), (236, 136), (244, 136), (237, 149), (246, 150)):
        cv.put(hx, hy, DARK, 0.2)
        cv.put(hx + 1, hy, DARK, 0.6)
        cv.put(hx, hy - 1, OLIVE, 5.0)
        cv.put(hx + 1, hy + 1, OLIVE, 1.6)
    # les corretges, a banda i banda
    for x in (224, 259):
        cv.vline(x, 130, 156, OLIVE, 2.0)
        cv.vline(x + 1, 130, 156, OLIVE, 2.8)
    box(cv, 223, 140, 226, 143, CAB, 4.0)
    box(cv, 258, 140, 261, 143, CAB, 4.0)
    # una espina de sardina a terra
    cv.line(266, 158, 273, 157, WHITEP, 3.6)
    for x in (267, 269, 271):
        cv.put(x, 156, WHITEP, 3.2)
        cv.put(x, 159, WHITEP, 3.0)


# ─── Muntatge ───────────────────────────────────────────────────────────────

def bg(cv):
    walls(cv)
    floor(cv)
    bunk(cv)
    shelf(cv)
    locker(cv)
    poster(cv)
    porthole(cv)
    overalls(cv)
    door(cv)
    door_light(cv)
    backpack(cv)
    sota.floor_shadow(cv, 93, 159, 80, 3, 0.5)
    sota.floor_shadow(cv, 191, 159, 16, 2, 0.5)
    # resplendors
    glow(cv, 44, 102, 30, WARM, 0.5)
    glow(cv, 44, 101, 10, (255, 240, 200), 0.6)
    glow(cv, 448, 104, 26, (170, 190, 150), 0.25)


def ulls_dia(cv):
    """Escenes 2 i 3, de dia: el vidre de l'ull de bou clar, cel gris de febrer i mar gris (tapa l'animació)."""
    from hd.rooms.principal import day_sea
    cx, cy, r = 310, 70, 15
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                day_sea(cv, x, y, cx, cy - 3, r, seed=5)
    for i in range(7):                                                  # gotes seques de sal al vidre
        a, d = hr(i, 31) * 6.28, hr(i, 32) * 12
        cv.flat(cx + math.cos(a) * d, cy + math.sin(a) * d, (206, 212, 214))
    for i in range(-r // 2, r // 3):                                    # el reflex del vidre
        x, y = cx - r // 3 + i, cy - r // 2 - i // 2
        cv.flat(x, y, mix(cv.get(x, y), (236, 240, 244), 0.35))


PROPS = {'ulls_dia': ulls_dia}


def _porthole_frames():
    # els fotogrames porten només l'ull de bou (el que canvia respecte del fons ja dibuixat)
    full = Canvas(light=LIGHT)
    bg(full)
    res = []
    for i in range(8):
        cv = Canvas(light=LIGHT)
        cv.img = full.img.copy()
        cv.P = cv.img.load()
        porthole_glass(cv, i / 8)
        res.append(_diff(cv.img, full.img))
    return res


ANIMS = {'mar': {'frames': _porthole_frames, 'frameDuration': 160}}

GEOMETRIA = {
    'things': {
        'porta': {'rect': (404, 56, 458, 152), 'walk': (432, 168)},
        'carregador': {'rect': (174, 110, 206, 136), 'walk': (192, 170)},
        'llitera': {'rect': (14, 106, 172, 158), 'walk': (110, 172)},
        'motxilla': {'rect': (220, 120, 266, 160), 'walk': (244, 172)},
        'ull_de_bou': {'rect': (288, 48, 332, 92), 'walk': (310, 172)},
    },
    'spawns': {'iri': (300, 186), 'vet': (360, 190), 'diu': (201, 175)},
    'walkable': [(8, 166), (472, 166), (476, 196), (4, 196)],
}
