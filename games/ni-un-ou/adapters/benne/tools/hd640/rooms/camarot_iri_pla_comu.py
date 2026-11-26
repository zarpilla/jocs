"""
**El dibuix pla de sempre** (font de les textures de la sala en 3D, camarot_iri.py).

Prova de resolució: el camarot de l'Iri (hd/rooms/camarot_iri.py) a 640×360, la composició ×4/3 dibuixada de nou.
El més petit del vaixell, al costat de les màquines, a les 3:40 de la matinada (Escena 1): la llitera feta com un
llit d'hospital, el carregador mossegat a l'endoll, la motxilla d'en Diu amb forats per respirar, l'ull de bou
fosc, la porta entreoberta amb el passadís il·luminat, la granota penjada i el pòster d'un dièsel amb la foto de
l'Iri i en Bastida.
Al cap del prestatge, el got d'aigua torçat (l'Arenga s'ha assegut de popa).
Props: `ulls_dia` (Escenes 2 i 3: el vidre de dia) i `maceta` (la maceta de goma, sota l'ull de bou). Animació: `mar` (l'ull de bou de nit: onades i esquitxos).
"""
import math
from functools import lru_cache

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from hd.pix import Canvas, Light, W, H, hr, mix, B4, WALNUT, PAPER
from hd.rooms.arenga import (WALL, CAB, DARK, WHITEP, YELL, REDP, SEAG, BRASS, WARM,
                             box, rrect, bolt, hpipe, vpipe, glow)
from hd.rooms.comu import text, text_width, GLYPHS
from hd.rooms.principal import day_sea
from hd.rooms.camarot_iri import PAINT, LINO, BLANKET, SHEET, OLIVE, OVERALL, SEA
from hd640.rooms import sota
from hd640.rooms.sota import FLOOR_Y, BOTTOM

from hd.pix import Canvas  # noqa: E402,F811  (a 1×: és la font de les textures de la sala en 3D)
Canvas1x = Canvas

LIGHT = Light(ambient=-0.45, vignette=(67, 35), floor_fade=None)
LIGHT.point(56, 133, r=253, k=2.9, squash=1.1, power=1.5)          # el llum de lectura de la llitera
LIGHT.point(600, 139, r=120, k=1.3, squash=0.8, power=1.8)        # el passadís, per la porta
LIGHT.point(413, 93, r=48, k=0.4, power=2.0)                      # l'ull de bou (gairebé res)

DOOR = (541, 83, 605, FLOOR_Y)
PORT = (413, 93)                                                  # centre de l'ull de bou
RUG = [(22, 14, 14), (40, 24, 22), (62, 36, 30), (86, 50, 38), (110, 68, 50), (134, 90, 66)]
CURT = [(16, 22, 30), (26, 36, 48), (40, 54, 68), (58, 74, 88), (80, 98, 110)]
CORD = [(60, 60, 58), (150, 150, 146), (214, 214, 206), (240, 240, 232)]


# ─── Paret, sostre i terra ──────────────────────────────────────────────────

def walls(cv):
    sota.plate_wall(cv, 0, W - 1, ramp=PAINT, lvl=3.6, frames=128, frame0=-5, seams=(77,), socle=184, rust=10, seed=3)
    # sostre baix, amb un tub d'aigua de mar i una safata de cables (és al costat de les màquines)
    cv.rect(0, 0, W - 1, 20, DARK, 2.2)
    for bx in range(-5, W, 128):
        box(cv, bx - 3, 0, bx + 11, 23, PAINT, 2.0, grad=0.6)
        cv.vline(bx - 2, 1, 22, PAINT, 3.0)
    cv.hline(0, W - 1, 21, PAINT, 1.4)
    cv.hline(0, W - 1, 22, PAINT, 2.6)
    hpipe(cv, 0, W - 1, 11, 4, SEAG, 2.8, bands=range(40, W, 93), band_ramp=WHITEP)
    for x in range(40, W, 93):                                        # fletxa del sentit, a cada anella
        for i in range(3):
            cv.vline(x + 4 + i, 9 + i, 13 - i, WHITEP, 4.4)
    for x in range(27, W, 80):                                        # abraçadores
        cv.vline(x, 4, 18, CAB, 2.4)
        cv.vline(x + 1, 4, 18, CAB, 3.6)
        cv.put(x, 17, CAB, 4.6)
    # el llum del sostre, apagat (rodó, de plàstic esmerilat)
    rrect(cv, 304, 22, 347, 29, 3, CAB, 3.0)
    cv.rect(308, 26, 343, 29, [(40, 40, 36), (70, 68, 60), (100, 98, 88)], 1.4, lit=0.3)
    cv.hline(310, 341, 27, [(40, 40, 36), (70, 68, 60), (100, 98, 88)], 2.2, lit=0.3)
    for sx in (306, 345):
        cv.put(sx, 24, CAB, 4.6)


def floor(cv):
    """Linòleum amb rajoles en perspectiva i una catifa de ratlles davant la llitera."""
    vp = (320, 40)
    for y in range(FLOOR_Y, BOTTOM + 16):
        d = y - vp[1]
        for x in range(W):
            u = vp[0] + (x - vp[0]) * 200 / d
            u2 = vp[0] + (x + 1 - vp[0]) * 200 / d
            lv = 3.0 + (hr(x // 2, y // 2, 5) - 0.5) * 0.5
            if int(u // 53) != int(u2 // 53):
                lv -= 0.9
            elif y in (213, 231, 255):
                lv -= 0.8
            elif y in (214, 232, 256):
                lv += 0.3
            if hr(x // 5, y // 2, 6) > 0.985:                          # rascades
                lv += 0.6
            cv.put(x, y, LINO, lv)
    cv.hline(0, W - 1, FLOOR_Y, LINO, 1.2)
    # la catifa (de ratlles, vella, amb el serrell)
    pts = [(93, 219), (267, 219), (283, 248), (77, 248)]
    cv.poly(pts, RUG, lambda x, y: 2.8 + (1.0 if (y // 4) % 3 == 0 else 0) + (0.5 if (y // 4) % 3 == 1 and (x // 2) % 2 else 0)
            - (0.6 if hr(x // 3, y) > 0.86 else 0))
    cv.line(93, 219, 267, 219, RUG, 4.2)
    cv.line(77, 248, 283, 248, RUG, 1.4)
    for x in range(80, 282, 3):
        cv.put(x, 249, RUG, 3.6)
        cv.put(x + (1 if hr(x, 9) > 0.5 else 0), 250, RUG, 2.8)
    for x in range(96, 266, 3):
        cv.put(x, 218, RUG, 3.4)


# ─── La llitera ─────────────────────────────────────────────────────────────

def bunk(cv):
    # la cortina recollida a l'esquerra i la barra
    cv.hline(13, 235, 85, CAB, 3.6)
    cv.hline(13, 235, 86, CAB, 1.8)
    for ex in (13, 235):
        cv.disc(ex, 85, 2, 2, CAB, 4.0)
    for y in range(88, 182):
        for x in range(11, 30):
            f = math.sin((x - 11) * 0.85 + y * 0.015)
            cv.put(x, y, CURT, 2.4 + f * 0.9 - (y - 88) * 0.005)
    for x in range(11, 30, 4):                                        # les anelles
        cv.put(x, 87, BRASS, 4.4)
        cv.put(x + 1, 87, BRASS, 3.0)
    cv.hline(10, 30, 140, CURT, 0.8)                                  # la beta que la recull
    cv.hline(10, 30, 141, [(60, 50, 30), (140, 120, 80), (200, 180, 130)], 1.6)
    # el plafó de fusta del capçal i dels peus
    box(cv, 19, 123, 29, 211, WALNUT, 3.4)
    box(cv, 219, 131, 229, 211, WALNUT, 3.0)
    for px, py in ((24, 128), (224, 136)):                            # els poms
        cv.disc(px, py, 2, 2, WALNUT, 4.6)
    # el matalàs, amb el llençol girat i la manta ben estirada (feta com un llit d'hospital)
    cv.rect(29, 157, 219, 176, BLANKET, lambda x, y: 3.2 - (y - 157) * 0.045)
    cv.hline(29, 219, 157, BLANKET, 4.4)
    cv.hline(29, 219, 158, BLANKET, 3.6)
    for x in range(33, 216, 2):                                       # la vora de la manta, ben plegada
        cv.put(x, 175, BLANKET, 1.6)
    for x in range(96, 216, 30):                                      # les arrugues estirades
        cv.line(x, 161, x + 14, 171, BLANKET, 2.6)
    cv.rect(69, 156, 83, 176, SHEET, lambda x, y: 3.6 - (y - 156) * 0.04)    # el llençol girat
    cv.vline(83, 156, 176, SHEET, 2.0)
    cv.hline(69, 83, 156, SHEET, 4.8)
    # el coixí
    rrect(cv, 32, 144, 67, 160, 5, SHEET, lambda x, y: 4.2 - (y - 144) * 0.06 - (x - 32) * 0.008)
    cv.hline(37, 61, 147, SHEET, 5.0)
    cv.line(40, 152, 46, 155, SHEET, 2.8)                             # el sot del cap
    # el costat de la llitera (fusta) i els dos calaixos
    box(cv, 29, 176, 219, 211, WALNUT, 3.0, grad=0.6)
    cv.hline(29, 219, 177, WALNUT, 4.4)
    for dx in (37, 131):
        box(cv, dx, 184, dx + 83, 205, WALNUT, 2.6)
        for x in range(dx + 3, dx + 81, 9):                           # la veta
            if hr(x, 4) > 0.4:
                cv.hline(x, x + 5, 195, WALNUT, 2.0)
        box(cv, dx + 33, 192, dx + 49, 196, BRASS, 3.6)
        cv.hline(dx + 34, dx + 48, 193, BRASS, 5.0)
    # el llum de lectura, a la paret del capçal
    box(cv, 37, 123, 48, 131, CAB, 3.0)
    cv.put(39, 125, CAB, 4.6)
    cv.line(44, 125, 56, 123, CAB, 3.4)
    cv.line(44, 126, 56, 124, CAB, 2.0)
    cv.poly([(51, 122), (67, 122), (64, 133), (53, 133)], BRASS, lambda x, y: 3.8 - (y - 122) * 0.09, lit=0.4)
    cv.hline(51, 67, 122, BRASS, 5.0, lit=0.4)
    cv.hline(55, 62, 133, [(160, 130, 70), (255, 236, 180)], 1.2, lit=0)
    cv.hline(56, 61, 134, [(255, 236, 180), (255, 250, 230)], 1.0, lit=0)
    # l'interruptor amb el cable
    box(cv, 31, 136, 35, 141, WHITEP, 3.6)
    cv.line(33, 131, 33, 135, CORD, 2.4)


def shelf(cv):
    """El prestatge de damunt la llitera: un multímetre, una llauna de cargols, tres manuals i claus fixes."""
    box(cv, 80, 109, 216, 115, WALNUT, 3.4)
    cv.hline(80, 216, 110, WALNUT, 4.6)
    for bx in (88, 208):
        cv.poly([(bx, 116), (bx + 3, 116), (bx + 3, 126)], CAB, 3.0)
        cv.put(bx + 2, 118, CAB, 4.6)
    # barana (perquè no caigui res quan balla)
    cv.hline(80, 216, 101, BRASS, 3.4)
    cv.hline(80, 216, 102, BRASS, 2.0)
    for x in (81, 147, 215):
        cv.vline(x, 101, 109, BRASS, 2.6)
    # el multímetre groc, amb la pantalla i el selector
    box(cv, 88, 87, 104, 108, YELL, 3.4)
    cv.rect(90, 89, 102, 95, [(20, 30, 24), (60, 80, 60), (130, 160, 120)], 1.6, lit=0.3)
    for px in (92, 95, 98):                                           # «0.0»
        cv.put(px, 91, [(20, 30, 24), (60, 80, 60)], 0.2, lit=0)
        cv.put(px, 93, [(20, 30, 24), (60, 80, 60)], 0.2, lit=0)
    cv.disc(96, 101, 3, 3, CAB, lambda nx, ny: 2.6 - nx - ny)
    cv.line(96, 101, 98, 99, WHITEP, 4.0)
    for px in (90, 102):
        cv.put(px, 106, REDP if px == 90 else DARK, 4.0 if px == 90 else 0.6)
    # la llauna de galetes (plena de cargols)
    rrect(cv, 112, 93, 133, 108, 3, REDP, lambda x, y: 3.6 - (x - 112) * 0.04)
    cv.hline(112, 133, 93, REDP, 5.0)
    cv.hline(113, 132, 97, WHITEP, 3.6)
    cv.hline(113, 132, 98, WHITEP, 2.6)
    cv.disc(122, 103, 3, 2, YELL, 3.4)
    # els manuals drets
    for i, (col, h) in enumerate((([(20, 30, 50), (40, 60, 100), (70, 100, 150)], 24),
                                  ([(40, 20, 16), (90, 40, 30), (140, 70, 50)], 20),
                                  ([(30, 40, 30), (60, 80, 60), (100, 120, 90)], 23))):
        x = 141 + i * 8
        cv.rect(x, 108 - h, x + 6, 108, col, 1.8)
        cv.vline(x, 108 - h, 108, col, 2.6)
        cv.hline(x + 1, x + 5, 108 - h + 4, PAPER, 3.0)
        cv.hline(x + 1, x + 5, 108 - h + 5, PAPER, 2.2)
        cv.hline(x + 1, x + 5, 105, col, 0.8)
    glass(cv)
    # les claus fixes, penjades de la barana
    for i, x in enumerate((171, 179, 187, 195)):
        ln = 11 + i * 3
        cv.vline(x, 103, 103 + ln, CAB, 4.4)
        cv.vline(x + 1, 103, 103 + ln, CAB, 2.4)
        cv.disc(x, 103 + ln, 3, 3, CAB, 4.0)
        cv.put(x, 103 + ln, DARK, 1.0)
        cv.put(x, 104 + ln, DARK, 1.0)


def glass(cv):
    """El got d'aigua, al cap del prestatge: l'aigua no és plana (l'Arenga s'ha assegut de popa, Escena 1)."""
    x0, x1, y0, y1 = 202, 212, 94, 108
    GL = [(40, 52, 58), (90, 110, 116), (150, 170, 172), (210, 222, 220)]
    WAT = [(14, 34, 44), (30, 64, 78), (56, 100, 112), (110, 160, 168), (190, 226, 228)]
    for y in range(y0 + 1, y1):
        for x in range(x0 + 1, x1):
            s = 99 + (x - x0) * 0.45                                       # més alta a l'esquerra: pendent
            if y >= s:
                cv.put(x, y, WAT, 2.2 + (0.6 if x == x0 + 2 else 0) - (y - s) * 0.04, lit=0.6)
            else:
                cv.put(x, y, GL, 0.6, lit=0.6)
    for x in range(x0 + 1, x1):                                            # la línia de l'aigua, torta
        cv.put(x, round(99 + (x - x0) * 0.45), WAT, 4.4, lit=0.4)
    for y in range(y0, y1 + 1):                                            # les parets del vidre
        cv.put(x0, y, GL, 2.6 if y > y0 else 3.4)
        cv.put(x1, y, GL, 2.0 if y > y0 else 3.4)
    cv.hline(x0, x1, y1, GL, 2.0)
    cv.vline(x0 + 1, y0 + 1, y1 - 2, GL, 3.8, lit=0.4)                     # el reflex
    cv.put(x0 + 1, y0 + 2, GL, 4.6, lit=0.2)


def maceta(cv):
    """
    La maceta de goma, penjada d'un ganxo sota l'ull de bou, amb el cap avall (l'Iri l'agafa a l'Escena 1). És la clau
    del primer trencaclosques: la cinta groga del puny i el reflex del cap la fan destacar a la paret fosca.
    """
    RUB = [(16, 16, 20), (34, 34, 40), (58, 58, 66), (88, 88, 98), (128, 130, 140)]
    box(cv, 410, 140, 416, 143, CAB, 3.6)                                   # el ganxo
    cv.put(413, 144, CAB, 4.4)
    cv.line(413, 145, 411, 149, CORD, 2.8)                                  # el cordill del mànec
    cv.line(413, 145, 415, 149, CORD, 2.4)
    cv.rect(411, 149, 415, 175, WALNUT, lambda x, y: 4.4 - (x - 411) * 0.5)  # el mànec
    cv.vline(411, 149, 175, WALNUT, 5.2)
    for y0 in (154, 162):                                                   # la cinta groga del puny
        for y in (y0, y0 + 1, y0 + 2):
            cv.hline(411, 415, y, YELL, 4.6 if y == y0 else 3.8)
    rrect(cv, 399, 175, 427, 188, 4, RUB, lambda x, y: 3.4 - (y - 175) * 0.12)  # el cap, de goma negra
    cv.hline(402, 424, 177, RUB, 4.6)                                       # el reflex de dalt
    cv.hline(403, 423, 178, RUB, 3.8)
    for ex in (399, 427):                                                   # les cares de picar
        cv.vline(ex, 177, 186, RUB, 1.6)
    for x in (405, 406, 407):                                               # una lluentor al cap
        cv.put(x, 180, RUB, 4.8)
    cv.put(413, 187, RUB, 0.8)
    sota.floor_shadow(cv, 413, 190, 13, 1, 0.25)


# ─── Endoll, tauleta, pòster, ull de bou, granota ───────────────────────────

def locker(cv):
    # la tauleta (calaixera de planxa)
    box(cv, 235, 173, 275, 211, PAINT, 4.0, grad=0.8)
    cv.hline(235, 275, 175, PAINT, 5.4)
    box(cv, 240, 184, 269, 207, PAINT, 3.6)
    box(cv, 249, 191, 260, 194, CAB, 3.6)
    cv.hline(250, 259, 191, CAB, 5.0)
    # el despertador: 3:40
    box(cv, 253, 162, 272, 172, CAB, 2.2)
    cv.rect(254, 163, 271, 171, DARK, 0.4, lit=0)
    x = 256
    for i, ch in enumerate('340'):
        for j, row in enumerate(GLYPHS[ch]):
            for k, b in enumerate(row):
                if b == '1':
                    cv.flat(x + k, 165 + j, (255, 76, 52))
        x += 5 if i else 7
    cv.flat(261, 166, (200, 50, 40))
    cv.flat(261, 168, (200, 50, 40))
    for px in (254, 271):                                             # les potes
        cv.put(px, 173, CAB, 3.0)
    glow(cv, 263, 167, 11, (255, 60, 40), 0.35)
    # l'endoll (doble, de paret)
    box(cv, 240, 149, 256, 160, WHITEP, 3.6)
    cv.hline(241, 255, 150, WHITEP, 4.6)
    for sx in (243, 251):
        cv.rect(sx, 153, sx + 1, 154, DARK, 0.5)
    cv.put(248, 157, WHITEP, 2.0)                                     # el cargol del mig
    # el carregador endollat i el cable (blanc) mossegat a trossos, que penja fins a la tauleta
    box(cv, 242, 151, 248, 162, WHITEP, 3.8)
    cv.hline(243, 247, 152, WHITEP, 5.0)
    pts = [(245, 163), (245, 167), (243, 171), (239, 173)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        cv.line(ax, ay, bx, by, CORD, 2.8)
    # mossegades: el coure pelat a la punta i trossos de cable caiguts damunt la tauleta
    cv.put(238, 174, BRASS, 4.6)
    cv.put(237, 174, BRASS, 3.8)
    cv.put(237, 175, BRASS, 3.0)
    for x0, x1 in ((241, 248), (252, 256)):
        cv.line(x0, 172, x1, 172, CORD, 2.6)
        cv.put(x1 + 1, 172, BRASS, 4.4)
        cv.put(x0, 172, CORD, 1.4)
    cv.put(245, 167, BRASS, 4.4)                                      # una dentada a mig cable
    cv.put(244, 167, DARK, 1.6)


def poster(cv):
    """Un pòster de motor (un tall d'un dièsel marí), i al cantó una foto de l'Iri amb en Bastida."""
    x0, y0, x1, y1 = 285, 45, 368, 131
    box(cv, x0, y0, x1, y1, PAPER, 3.6)
    BLUEP = [(10, 20, 40), (16, 34, 64), (24, 50, 88), (40, 74, 120), (70, 110, 160)]
    cv.rect(x0 + 3, y0 + 3, x1 - 3, y1 - 17, BLUEP, 2.0)
    for gx in range(x0 + 6, x1 - 3, 8):                               # la quadrícula del plànol
        cv.vline(gx, y0 + 3, y1 - 17, BLUEP, 2.6)
    for gy in range(y0 + 6, y1 - 17, 8):
        cv.hline(x0 + 3, x1 - 3, gy, BLUEP, 2.6)
    # el motor en tall: bloc, pistons i bieles, cigonyal
    cx = 325
    STEELB = [(30, 60, 80), (60, 110, 130), (110, 160, 170), (180, 210, 210)]
    box(cv, cx - 24, 69, cx + 24, 104, STEELB, 1.8)
    for i in range(4):
        px = cx - 20 + i * 11
        up = 7 if i % 2 else 0
        box(cv, px, 67 + up, px + 7, 80 + up, [(60, 40, 30), (150, 90, 50), (220, 150, 90)], 1.6)
        cv.hline(px + 1, px + 6, 70 + up, [(60, 40, 30), (150, 90, 50)], 0.4)          # segments
        cv.vline(px + 3, 81 + up, 101, [(120, 120, 120), (200, 200, 200)], 0.8)          # la biela
        cv.vline(px + 4, 81 + up, 101, [(120, 120, 120), (200, 200, 200)], 0.2)
    cv.disc(cx, 105, 21, 5, [(40, 40, 40), (110, 110, 110), (180, 180, 180)], 1.2)
    cv.hline(cx - 29, cx + 29, 61, [(160, 40, 30), (240, 90, 60)], 1.0)
    for ax in (cx - 26, cx + 26):                                     # cotes
        cv.vline(ax, 59, 63, [(160, 40, 30), (240, 90, 60)], 1.0)
    # el títol
    text(cv, 'DIÈSEL', cx - text_width('DIÈSEL') // 2, y1 - 13, None, 0, flat=(40, 44, 58))
    for x in range(x0 + 8, x1 - 8):
        if hr(x // 2, y1 - 5) > 0.35:
            cv.put(x, y1 - 5, PAPER, 0.8)
    # la foto, posada al cantó: dues persones davant d'un motor
    fx0, fy0 = 344, 112
    box(cv, fx0, fy0, fx0 + 21, fy0 + 16, WHITEP, 4.4)
    cv.rect(fx0 + 2, fy0 + 2, fx0 + 19, fy0 + 12, SEAG, 2.2)
    cv.rect(fx0 + 2, fy0 + 10, fx0 + 19, fy0 + 12, SEAG, 1.0)
    for px, skin, cloth in ((fx0 + 7, [(40, 20, 10), (120, 80, 50), (200, 150, 110)], OVERALL),
                            (fx0 + 14, [(60, 60, 60), (180, 180, 180), (240, 240, 240)],
                             [(60, 50, 40), (130, 120, 100), (180, 170, 150)])):
        cv.rect(px - 1, fy0 + 3, px, fy0 + 4, skin, 1.6)
        cv.rect(px - 2, fy0 + 6, px + 1, fy0 + 12, cloth, 2.6)
    # xinxetes
    for px, py in ((x0 + 3, y0 + 3), (x1 - 3, y0 + 3), (x0 + 3, y1 - 3), (x1 - 3, y1 - 3), (fx0 + 10, fy0 + 1)):
        cv.put(px, py, REDP, 4.4)
        cv.put(px + 1, py + 1, REDP, 2.0)
    cv.poly([(x1 - 9, y1), (x1, y1 - 9), (x1, y1)], PAPER, 2.2)      # el cantó doblegat


def porthole_glass(cv, t=0.0):
    """L'interior de l'ull de bou: mar fosc i escuma que passa (t, de 0 a 1, per a l'animació)."""
    cx, cy = PORT
    r = 20
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                hor = cy - 3 + math.sin(x * 0.15 + t * 6.28) * 2
                if y < hor:
                    lv = 1.6 + (y - (cy - r)) * 0.022
                    cv.put(x, y, SEA, lv, lit=0)
                else:
                    foam = math.sin(x * 0.34 + y * 1.0 - t * 6.28 * 2) + math.sin(x * 0.13 - t * 6.28) > 1.5
                    cv.put(x, y, SEA, 2.4 + (2.2 if foam else 0) - (y - hor) * 0.03, lit=0)
    # esquitxos al vidre, que llisquen avall
    for i in range(12):
        a = hr(i, 1) * 6.28
        d = hr(i, 2) * 16
        px, py = cx + math.cos(a) * d, cy + math.sin(a) * d
        py = py + (t * 11 + hr(i, 3) * 11) % 11
        if (px - cx) ** 2 + (py - cy) ** 2 < 18 * 18:
            cv.put(px, py, SEA, 5.4, lit=0)
            if hr(i, 4) > 0.5:
                cv.put(px, py - 1, SEA, 4.0, lit=0)
    # reflex del llum de la cabina al vidre
    cv.line(cx - 11, cy - 12, cx - 5, cy - 16, WHITEP, 2.4, lit=0)
    cv.line(cx - 12, cy - 9, cx - 10, cy - 10, WHITEP, 1.8, lit=0)


def porthole(cv):
    cx, cy = PORT
    cv.disc(cx, cy, 27, 27, BRASS, lambda nx, ny: 3.2 - nx * 1.1 - ny * 1.3)
    cv.disc(cx, cy, 23, 23, BRASS, lambda nx, ny: 2.0 + nx * 0.8 + ny * 0.9)
    cv.ring(cx, cy, 21, BRASS, 1.2, step=3)
    porthole_glass(cv)
    for a in range(0, 360, 45):
        bolt(cv, round(cx + math.cos(math.radians(a)) * 25), round(cy + math.sin(math.radians(a)) * 25), BRASS, 3.2)
    # les dues palometes per tancar la tapa de tempesta
    for dx in (-32, 29):
        box(cv, cx + dx, cy - 3, cx + dx + 3, cy + 8, BRASS, 3.4)
        cv.hline(cx + dx - 1, cx + dx + 4, cy - 3, BRASS, 4.6)
    # la tapa de tempesta, oberta i penjant a sota (per de dins)
    cv.disc(cx, cy + 33, 19, 4, BRASS, lambda nx, ny: 2.6 - ny)
    cv.hline(cx - 3, cx + 3, cy + 28, BRASS, 3.6)
    cv.hline(cx - 3, cx + 3, cy + 29, BRASS, 2.2)


def overalls(cv):
    """La granota de recanvi (amb el nom brodat) i els protectors d'orelles, penjats al costat de la porta."""
    box(cv, 459, 69, 525, 73, WALNUT, 3.2)
    for hx in (469, 507):
        cv.vline(hx, 73, 80, BRASS, 3.8)
        cv.put(hx + 1, 80, BRASS, 3.0)
        cv.put(hx + 1, 79, BRASS, 2.2)
    body = [(459, 83), (483, 80), (488, 93), (488, 160), (483, 195), (472, 195), (472, 163), (467, 163),
            (467, 195), (453, 195), (451, 157), (451, 93)]
    cv.poly(body, OVERALL, lambda x, y: 3.2 - abs(x - 469) * 0.04 - (y - 80) * 0.005)
    cv.poly([(451, 93), (459, 85), (451, 149), (445, 147)], OVERALL, 2.4)    # mànigues
    cv.poly([(483, 83), (488, 93), (493, 147), (488, 149)], OVERALL, 2.0)
    cv.hline(445, 451, 147, OVERALL, 1.2)                                     # punys
    cv.hline(488, 493, 147, OVERALL, 1.2)
    cv.vline(469, 85, 157, OVERALL, 1.4)                                      # cremallera
    cv.vline(470, 85, 157, OVERALL, 4.0)
    cv.put(470, 86, BRASS, 4.4)
    cv.line(464, 160, 464, 193, OVERALL, 1.6)
    box(cv, 456, 109, 467, 120, OVERALL, 2.8)                                 # butxaca, amb un bolígraf
    cv.vline(462, 106, 110, REDP, 3.6)
    for y in (133, 134, 135):                                                 # banda reflectant
        cv.hline(452, 487, y, YELL, 3.4 if y == 133 else 2.6 if y == 134 else 1.8)
    for y in (176, 177):
        cv.hline(453, 466, y, YELL, 3.0 if y == 176 else 2.0)
        cv.hline(473, 482, y, YELL, 3.0 if y == 176 else 2.0)
    cv.rect(472, 87, 485, 93, YELL, 3.0)                                      # el nom brodat
    text(cv, 'IRI', 473, 88, None, 0, flat=(20, 28, 50))
    # els protectors d'orelles, penjats de l'altre ganxo
    for a in range(180, 361, 3):
        cv.put(508 + round(math.cos(math.radians(a)) * 10), 91 + round(math.sin(math.radians(a)) * 10), YELL, 3.6)
        cv.put(508 + round(math.cos(math.radians(a)) * 9), 91 + round(math.sin(math.radians(a)) * 9), YELL, 2.2)
    for ex in (498, 518):
        rrect(cv, ex - 4, 88, ex + 4, 103, 3, YELL, lambda x, y: 3.4 - (x - ex + 4) * 0.1)
        cv.vline(ex, 91, 100, DARK, 1.0)
        cv.hline(ex - 3, ex + 3, 103, DARK, 1.6)


def door(cv):
    """La porta del camarot, entreoberta: la fulla gira cap endins i deixa veure el passadís, il·luminat."""
    x0, y0, x1, y1 = DOOR
    for y in range(y0, y1):
        for x in range(x0, x1 + 1):
            if sota.in_door(x, y, x0, y0, x1, y1, 8):
                if y > 187:
                    cv.put(x, y, sota.DECK, 3.4 + (0.8 if (x + y) % 4 == 0 else 0), lit=0.5)
                else:
                    cv.put(x, y, WALL, 4.0 - abs(y - 123) * 0.009 + (0.6 if y in (133, 134) else 0), lit=0.5)
    vpipe(cv, 595, y0 + 2, 187, 3, SEAG, 3.6, bands=(128,), band_ramp=WHITEP)
    cv.hline(x0, x1, 187, WALL, 2.0)
    for by in range(y0 + 16, 180, 16):                                # reblons de la paret del passadís
        cv.put(586, by, WALL, 5.0)
    sota.door_frame(cv, x0, y0, x1, y1, ramp=PAINT, lvl=4.6, r=8)
    # la fulla, girada cap a nosaltres: la vora lliure, més alta i més ampla (perspectiva)
    fx = 576
    cv.poly([(x0, y0 + 1), (fx, y0 - 5), (fx, y1 + 8), (x0, y1)], PAINT, lambda x, y: 3.0 - (x - x0) * 0.019)
    cv.poly([(x0 + 7, y0 + 11), (fx - 7, y0 + 5), (fx - 7, y0 + 53), (x0 + 7, y0 + 56)], PAINT,
            lambda x, y: 3.4 - (x - x0) * 0.019)
    cv.line(x0 + 7, y0 + 11, fx - 7, y0 + 5, PAINT, 4.6)
    cv.poly([(x0 + 7, y1 - 35), (fx - 7, y1 - 32), (fx - 7, y1 - 3), (x0 + 7, y1 - 5)], PAINT,
            lambda x, y: 3.2 - (x - x0) * 0.019)
    for i in range(6):                                                # reixeta de ventilació
        cv.line(x0 + 11, y1 - 28 + i * 4, fx - 11, y1 - 26 + i * 4, PAINT, 1.4)
        cv.line(x0 + 11, y1 - 27 + i * 4, fx - 11, y1 - 25 + i * 4, PAINT, 3.8)
    cv.vline(fx, y0 - 5, y1 + 8, PAINT, 5.0)                          # el cantell de la fulla
    cv.vline(fx + 1, y0 - 4, y1 + 8, PAINT, 2.0)
    # la maneta
    box(cv, fx - 9, 139, fx - 5, 149, BRASS, 3.6)
    cv.hline(fx - 16, fx - 7, 141, BRASS, 4.6)
    cv.hline(fx - 16, fx - 7, 142, BRASS, 2.6)
    # el número del camarot
    box(cv, 555, 93, 569, 101, BRASS, 3.6)
    text(cv, '4', 560, 95, None, 0, flat=(60, 40, 16))


def door_light(cv):
    """La llum del passadís que entra per la porta i fa una falca a terra."""
    for y in range(FLOOR_Y, BOTTOM + 10):
        t = (y - FLOOR_Y) / 59
        xa, xb = 588 - t * 40, 605 - t * 8
        for x in range(int(xa), int(xb) + 1):
            k = 0.3 * (1 - t * 0.7)
            if k > B4[y & 3][x & 3] * 0.6:
                cv.flat(x, y, mix(cv.get(x, y), (150, 170, 140), k))


# ─── La motxilla d'en Diu ───────────────────────────────────────────────────

def backpack(cv):
    """La motxilla d'en Diu, dreta a terra: oberta de dalt, amb forats per respirar fets amb un punxó."""
    sota.floor_shadow(cv, 323, 211, 32, 4, 0.7)
    rrect(cv, 301, 168, 344, 209, 12, OLIVE, lambda x, y: 3.3 - (x - 301) * 0.026 - (y - 168) * 0.006)
    cv.vline(303, 179, 207, OLIVE, 4.2)
    for y in range(176, 207, 7):                                      # costures de la tela
        cv.put(341, y, OLIVE, 1.8)
    # la boca oberta (fosca) i la tapa caiguda cap enrere
    cv.disc(323, 171, 15, 4, DARK, 1.0)
    cv.poly([(308, 168), (337, 168), (340, 161), (305, 161)], OLIVE, 2.4)
    cv.hline(305, 340, 161, OLIVE, 3.8)
    cv.hline(308, 337, 168, OLIVE, 4.6)
    cv.hline(310, 335, 164, OLIVE, 1.6)                               # el ribet de la tapa
    # la butxaca de davant amb la cremallera
    rrect(cv, 308, 187, 337, 207, 5, OLIVE, lambda x, y: 3.9 - (x - 308) * 0.026)
    cv.hline(311, 334, 187, OLIVE, 5.2)
    cv.hline(312, 333, 191, CAB, 2.2)
    for x in range(312, 334, 2):
        cv.put(x, 192, CAB, 3.4)
    box(cv, 332, 189, 335, 195, CAB, 4.4)
    # forats per respirar (amb la vora clara)
    for hx, hy in ((311, 175), (320, 176), (329, 175), (336, 179), (315, 181), (325, 181), (316, 199), (328, 200)):
        cv.rect(hx, hy, hx + 1, hy, DARK, 0.2)
        cv.put(hx + 1, hy + 1, DARK, 0.6)
        cv.hline(hx, hx + 1, hy - 1, OLIVE, 5.0)
        cv.put(hx + 2, hy + 1, OLIVE, 1.6)
    # les corretges, a banda i banda
    for x in (299, 345):
        cv.vline(x, 173, 208, OLIVE, 2.0)
        cv.vline(x + 1, 173, 208, OLIVE, 2.8)
    box(cv, 297, 187, 301, 191, CAB, 4.0)
    box(cv, 344, 187, 348, 191, CAB, 4.0)
    # una espina de sardina a terra
    cv.line(355, 211, 364, 209, WHITEP, 3.6)
    for x in (357, 359, 361, 363):
        cv.put(x, 208 - (x > 360), WHITEP, 3.2)
        cv.put(x, 212 - (x > 360), WHITEP, 3.0)
    cv.poly([(364, 209), (368, 206), (367, 212)], WHITEP, 3.0)


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
    sota.floor_shadow(cv, 124, 212, 107, 4, 0.5)
    sota.floor_shadow(cv, 255, 212, 21, 3, 0.5)
    glow(cv, 59, 136, 40, WARM, 0.5)
    glow(cv, 59, 135, 13, (255, 240, 200), 0.6)
    glow(cv, 597, 139, 35, (170, 190, 150), 0.25)


def ulls_dia(cv):
    """Escenes 2 i 3, de dia: el vidre de l'ull de bou clar, cel gris de febrer i mar gris (tapa l'animació)."""
    cx, cy = PORT
    r = 20
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                day_sea(cv, x, y, cx, cy - 4, r, seed=5)
    for i in range(10):                                                 # gotes seques de sal al vidre
        a, d = hr(i, 31) * 6.28, hr(i, 32) * 16
        cv.flat(cx + math.cos(a) * d, cy + math.sin(a) * d, (206, 212, 214))
    for i in range(-r // 2, r // 3):                                    # el reflex del vidre
        x, y = cx - r // 3 + i, cy - r // 2 - i // 2
        cv.flat(x, y, mix(cv.get(x, y), (236, 240, 244), 0.35))
        cv.flat(x, y + 1, mix(cv.get(x, y + 1), (236, 240, 244), 0.2))


PROPS = {'ulls_dia': ulls_dia, 'maceta': maceta}


# ─── Animació: el mar per l'ull de bou ──────────────────────────────────────

@lru_cache(maxsize=None)
def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv.img


def _porthole_frames():
    """Els fotogrames porten només l'ull de bou (el que canvia respecte del fons)."""
    full = _base()
    cx, cy = PORT
    area = (cx - 22, cy - 22, cx + 23, cy + 23)
    res = []
    for i in range(8):
        cv = Canvas(light=LIGHT, img=full.copy())
        porthole_glass(cv, i / 8)
        res.append(sota.fast_diff(cv.img, full, area))
    return res


ANIMS = {'mar': {'frames': _porthole_frames, 'frameDuration': 160}}


# ─── Geometria (coordenades de 640×360) ─────────────────────────────────────
