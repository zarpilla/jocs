"""
Arxiu (La Gavina, Vet): cent vint anys de paperassa sota el moll de l'hangar. Arxivadors vells, la taula dels
expedients, la taula de llum amb els plànols del Projecte Gavina. Era el despatx del director: encara en
queda la canonada de coure, amb el manòmetre verd de rovell.
Llums: el flexo dels expedients, la taula de llum (cian) i la claror freda que baixa per l'escala de l'hangar.
"""
import math

from hd.pix import (Light, W, H, hr, ramp, STEEL, PANEL, CYAN, WARN, ORANGE, RED, PAPER, MANILA, IRON, SPACE,
                    COPPER, GOLD, BLUEP, TEAL, GRAY)
from hd.rooms.gavina_passadis import (HULL, DECK, LAMPW, SIGN, RUSTG, FLOOR_Y, text, wall, deck, pool, hazard,
                                      rivet)

# Pintura vella dels arxivadors: verd oliva institucional
OLIVE = ramp((10, 12, 12), (24, 28, 26), (40, 46, 40), (60, 68, 58), (84, 92, 78), (112, 120, 100), (146, 152, 128),
             (186, 188, 162), n=9)
VERDIGRIS = [(16, 34, 32), (30, 62, 56), (52, 98, 84), (84, 140, 116), (130, 184, 156)]
BULB = [(90, 70, 40), (170, 140, 80), (240, 210, 140), (255, 240, 200), (255, 255, 240)]

VX, VY = 250, 40                     # punt de fuga del terra
FS, FK = 2.4, 520.0

LIGHT = Light(vignette=(74, 40), floor_fade=(196, 34))
LIGHT.point(304, 104, r=120, k=2.8, squash=1.2, down=True)           # flexo dels expedients
LIGHT.point(408, 100, r=96, k=1.6, squash=1.3)                        # taula de llum (plànols)
LIGHT.point(36, 30, r=110, k=2.2, squash=0.9)                         # claror de l'escala de l'hangar
LIGHT.add(pool(282, 176, 90, 22, 1.8))
LIGHT.add(pool(410, 172, 70, 18, 1.0))
LIGHT.add(pool(40, 172, 60, 18, 1.2))


def bg(cv):
    # ─── Paret i sostre ───────────────────────────────────────────────────
    wall(cv, 0, W - 1, seed=5, base=2.6)
    cv.rect(0, 0, W - 1, 7, HULL, lambda x, y: 0.7 + (0.5 if y in (5, 6) else 0))
    cv.hline(0, W - 1, 8, HULL, 3.0)
    cv.hline(0, W - 1, 9, HULL, 0.8)
    # conducte de ventilació al llarg del sostre
    for x in range(70, W):
        for y in range(11, 20):
            lvl = [1.0, 3.4, 3.0, 2.7, 2.4, 2.1, 1.8, 1.4, 0.6][y - 11]
            if (x - 70) % 46 in (0, 1):
                lvl += 0.8 if (x - 70) % 46 == 0 else -0.8
            cv.put(x, y, HULL, lvl)
    cv.darken(70, 20, W - 1, 22, 0.5)

    # ─── Canonada de coure de l'antiga fàbrica (el despatx del director era aquí) ──
    for y in range(20, 154):
        for x in range(212, 217):
            lvl = [2.0, 3.6, 3.0, 2.2, 1.0][x - 212]
            if hr(x, y // 3, 17) > 0.72:
                cv.put(x, y, VERDIGRIS, lvl - 0.6)
            else:
                cv.put(x, y, COPPER, lvl - 0.4)
        if y % 34 == 0:
            cv.rect(211, y, 217, y + 2, COPPER, 1.6)
            cv.hline(211, 217, y, VERDIGRIS, 2.6)
    # manòmetre vell, amb el vidre trencat
    cv.disc(214, 68, 5, 5, VERDIGRIS, lambda nx, ny: 2.8 - nx - ny)
    cv.disc(214, 68, 3.6, 3.6, PAPER, lambda nx, ny: 1.8 - ny * 0.5)
    cv.line(214, 68, 216, 66, RED, 1.6, 0.5)
    cv.line(212, 66, 215, 70, PAPER, 3.4, 0.5)
    # brida que entra al sostre, tallada amb una planxa nova
    cv.rect(208, 17, 221, 20, HULL, 3.4)

    # ─── Escala cap al moll de l'hangar (8..68 × 38..155) ─────────────────
    SX0, SX1, ST = 10, 66, 40
    cv.rect(SX0 - 2, ST - 4, SX1 + 2, 153, HULL, lambda x, y: 3.6 if x < SX0 or y < ST else (1.0 if x > SX1 else 2.0))
    # buc fosc, amb la claror de l'hangar que baixa de dalt
    for y in range(ST, 154):
        for x in range(SX0, SX1 + 1):
            lvl = 0.6 + max(0.0, 1 - (y - ST) / 70) * 2.4 - (x - SX0) / 70
            cv.put(x, y, SPACE, lvl + 0.8, 0.3)
    cv.tint(SX0, ST, SX1, 153, (90, 140, 190), lambda x, y: max(0.0, 0.35 - (y - ST) / 300))
    # trapa oberta al sostre, per on entra la llum
    cv.rect(SX0 + 2, ST, SX1 - 2, ST + 3, LAMPW, lambda x, y: 2.5 - (y - ST) * 0.5, 0)
    # graons d'acer pujant cap a l'esquerra
    steps = 12
    for i in range(steps):
        t = i / (steps - 1)
        sy = round(150 - t * 100)
        sx0 = round(SX1 - 6 - t * 38)
        cv.rect(sx0 - 16, sy, sx0, sy + 2, STEEL, lambda x, y: [6.4, 4.6, 2.6][y - sy] - (sx0 - x) / 30)
        cv.rect(sx0 - 16, sy + 3, sx0, sy + 4, STEEL, 0.6)
        for x in range(sx0 - 13, sx0, 3):
            cv.put(x, sy, STEEL, 3.4)                                       # trama antilliscant
    # llimonera (planxa lateral de l'escala)
    for k in range(4):
        cv.line(SX1 - 2 + k, 153, SX1 - 46 + k, 46, STEEL, [5.0, 3.4, 2.6, 1.2][k])
    # barana
    cv.line(SX1 + 0, 120, SX1 - 42, 16 + 26, STEEL, 5.0)
    cv.line(SX1 + 0, 121, SX1 - 42, 17 + 26, STEEL, 2.0)
    for t in (0.0, 0.33, 0.66):
        x = round(SX1 - t * 42)
        y = round(120 - t * 78)
        cv.vline(x, y, y + 30, STEEL, 3.4)
    # rètol de l'hangar
    cv.rect(SX0 + 2, ST + 8, SX0 + 28, ST + 15, SIGN, 3.5, 0.3)
    text(cv, SX0 + 4, ST + 9, 'HANGAR', HULL, 0.5, 0)
    hazard(cv, SX0 - 2, 150, SX1 + 2, 153, lvl=3.0, w=3)

    # ─── Arxivadors (79..204 × 38..153) ───────────────────────────────────
    CABS = [(80, 110), (112, 142), (144, 174), (176, 203)]
    CT = 50
    # caixes d'arxiu damunt dels arxivadors
    for i, (bx0, bx1, bh) in enumerate(((82, 104, 10), (106, 126, 8), (150, 178, 11), (182, 200, 7))):
        cv.rect(bx0, CT - bh, bx1, CT - 1, MANILA, lambda x, y: 2.6 - (x - bx0) / 30 + (0.8 if y == CT - bh else 0))
        cv.rect(bx0 + 4, CT - bh + 3, bx0 + 12, CT - bh + 5, PAPER, 3.6)
        cv.vline(bx1, CT - bh, CT - 1, MANILA, 1.0)
    for ci, (x0, x1) in enumerate(CABS):
        cv.rect(x0, CT, x1, 153, OLIVE, lambda x, y: 3.0 - (x - x0) / 60 - (0.6 if y > 148 else 0))
        cv.vline(x0, CT, 153, OLIVE, 4.4)
        cv.vline(x1, CT, 153, OLIVE, 1.2)
        cv.hline(x0, x1, CT, OLIVE, 5.0)
        cv.hline(x0, x1, CT + 1, OLIVE, 4.0)
        dh = 24
        for di in range(4):
            y0 = CT + 4 + di * (dh + 1)
            y1 = y0 + dh - 1
            open_ = (ci == 2 and di == 1)
            if open_:
                # calaix obert: cartes confiscades a munts
                cv.rect(x0 + 2, y0 - 3, x1 - 2, y0 + 4, OLIVE, 0.4)
                for k in range(7):
                    lx = x0 + 3 + k * 4
                    cv.rect(lx, y0 - 5 - int(hr(k, 3) * 4), lx + 3, y0 + 2, PAPER, 3.6 + hr(k, 5) * 0.8 - (k % 2) * 0.5)
                cv.rect(x0 + 1, y0 + 3, x1 - 1, y1 + 4, OLIVE, lambda x, y: 3.4 - (y - y0) / 30)
                cv.hline(x0 + 1, x1 - 1, y0 + 3, OLIVE, 5.4)
                cv.hline(x0 + 1, x1 - 1, y1 + 4, OLIVE, 0.6)
                cv.darken(x0 + 1, y1 + 5, x1 - 1, y1 + 7, 0.6)
                yy = y0 + 8
            else:
                cv.rect(x0 + 3, y0, x1 - 3, y1, OLIVE, lambda x, y: 3.2 - (x - x0) / 50)
                cv.hline(x0 + 3, x1 - 3, y0, OLIVE, 4.6)
                cv.vline(x0 + 3, y0, y1, OLIVE, 4.0)
                cv.hline(x0 + 3, x1 - 3, y1, OLIVE, 1.0)
                cv.vline(x1 - 3, y0, y1, OLIVE, 1.6)
                yy = y0 + 5
            cx = (x0 + x1) // 2
            # portaetiquetes i tirador
            cv.rect(cx - 5, yy, cx + 5, yy + 4, IRON, 3.2)
            cv.rect(cx - 4, yy + 1, cx + 4, yy + 3, PAPER, 3.6 - hr(ci, di) * 1.2)
            cv.hline(cx - 3, cx - 3 + int(hr(ci, di, 2) * 6), yy + 2, HULL, 1.6, 0.4)
            cv.rect(cx - 4, yy + 8, cx + 4, yy + 9, IRON, lambda x, y: 4.4 - (y - yy - 8) * 2)
        # bonys i rascades
        for k in range(3):
            if hr(ci, k, 8) > 0.5:
                rx, ry = x0 + 4 + int(hr(ci, k) * (x1 - x0 - 8)), CT + 10 + int(hr(ci, k, 1) * 90)
                cv.line(rx, ry, rx + 4, ry + 1, OLIVE, 4.8)
    cv.darken(78, 150, 206, 153, 0.7)

    # ─── Prestatge de caixes d'arxiu sobre la taula ───────────────────────
    for sy, boxes in ((70, 7), (96, 6)):
        cv.rect(232, sy, 328, sy + 2, HULL, lambda x, y: [4.4, 3.0, 1.2][y - sy])
        for sx in (236, 324):
            cv.rect(sx, sy + 3, sx + 1, sy + 7, HULL, 2.4)
        x = 236 if sy == 70 else 240
        for k in range(boxes):
            bw = 11 + int(hr(sy, k) * 3)
            bh = 14 + int(hr(sy, k, 2) * 6)
            if sy == 96:
                bh = min(bh, 14)
            col = MANILA if hr(sy, k, 3) > 0.25 else PAPER
            cv.rect(x, sy - bh, x + bw - 1, sy - 1, col, lambda xx, yy: 2.4 - (xx - x) / 24 + (0.6 if yy == sy - bh else 0))
            cv.vline(x + bw - 1, sy - bh, sy - 1, col, 0.8)
            cv.rect(x + 2, sy - bh + 3, x + bw - 3, sy - bh + 6, PAPER, 3.6, 0.6)
            text(cv, x + 2, sy - bh + 8, str(int(hr(sy, k, 4) * 9) + 1), HULL, 1.0, 0.3) if bw >= 12 else None
            x += bw + 1
            if x > 318:
                break
    # caixa tombada al prestatge de dalt
    cv.rect(306, 62, 324, 69, MANILA, lambda x, y: 2.2 - (y - 62) * 0.05)
    cv.hline(306, 324, 62, MANILA, 3.2)

    # ─── Taula dels expedients (229..322 × 106..131) ──────────────────────
    TX0, TX1, TT, TF = 226, 326, 122, 127
    # ombra al terra
    cv.darken(TX0 - 2, 154, TX1 + 6, 162, lambda x, y: 0.8 - (y - 154) / 10)
    # potes
    for lx in (TX0 + 4, TX1 - 7):
        cv.rect(lx, TF + 1, lx + 3, 158, STEEL, lambda x, y: 3.4 - (x - lx) * 0.6)
    cv.rect(TX0 + 4, 146, TX1 - 4, 147, STEEL, 2.0)                    # travesser
    # tauler (gruix i superfície)
    for y in range(TT - 6, TT + 1):
        t = (y - TT + 6) / 6
        cv.hline(TX0 + 3 - round(t * 3), TX1 - 3 + round(t * 3), y, PANEL, 3.4 + t * 0.6)
    cv.rect(TX0, TT + 1, TX1, TF, PANEL, lambda x, y: [5.0, 4.0, 3.4, 3.0, 2.4, 1.0][y - TT - 1])
    # calaixera sota el tauler
    cv.rect(TX1 - 34, TF + 1, TX1 - 8, 150, PANEL, lambda x, y: 2.6 - (x - TX1 + 34) / 50)
    for y0 in (TF + 3, TF + 11):
        cv.rect(TX1 - 32, y0, TX1 - 10, y0 + 6, PANEL, 3.0)
        cv.hline(TX1 - 32, TX1 - 10, y0, PANEL, 4.2)
        cv.rect(TX1 - 23, y0 + 3, TX1 - 19, y0 + 3, IRON, 4.6)
    cv.vline(TX1 - 8, TF + 1, 150, PANEL, 1.0)

    # expedients: piles de carpetes, una d'oberta amb la fitxa de la I.
    def folder(x0, y0, w, h, lvl, ramp_=MANILA, tab=True):
        cv.rect(x0, y0, x0 + w, y0 + h, ramp_, lambda x, y: lvl + (0.8 if y == y0 else 0) - (0.8 if y == y0 + h else 0))
        if tab:
            cv.rect(x0 + 3, y0 - 1, x0 + 9, y0, ramp_, lvl + 0.6)
    # pila esquerra
    for k in range(6):
        folder(232 + int(hr(k, 1) * 3), 117 - k * 2, 24, 1, 2.6 + (k % 2) * 0.6, MANILA if k % 3 else RED, tab=k == 5)
    cv.rect(234, 109, 254, 111, MANILA, 3.4)
    # carpeta oberta al centre: fitxa amb foto i segell vermell
    cv.poly([(262, 118), (300, 118), (303, 122), (259, 122)], MANILA, 3.0)
    cv.poly([(264, 113), (281, 113), (282, 121), (262, 121)], PAPER, 4.2)
    cv.poly([(282, 113), (299, 113), (301, 121), (282, 121)], PAPER, 3.8)
    cv.rect(266, 114, 270, 118, GRAY, 2.0)                                # foto carnet
    cv.rect(267, 115, 269, 116, GRAY, 3.4)
    for y in (114, 116, 118):
        cv.hline(272, 279, y, HULL, 2.2, 0.4)
    cv.hline(266, 278, 120, HULL, 1.6, 0.4)                                # el cognom, ratllat
    cv.hline(266, 278, 119, HULL, 0.8, 0.4)
    for y in (114, 116, 118):
        cv.hline(285, 296, y, HULL, 2.2, 0.4)
    cv.rect(287, 117, 297, 120, RED, 3.0, 0.5)                             # segell «TANCAT»
    cv.rect(288, 118, 296, 119, RED, 4.0, 0.5)
    # pila dreta, més desordenada
    for k in range(4):
        folder(304 + int(hr(k, 7) * 4), 119 - k * 2, 16, 1, 2.8 + (k % 2) * 0.5)
    cv.put(318, 112, PAPER, 4.6)
    # tassa de cafè freda
    cv.rect(253, 114, 257, 120, PAPER, lambda x, y: 4.0 - (x - 253) * 0.4)
    cv.vline(258, 116, 118, PAPER, 2.4)

    # flexo articulat (llum càlida i vella)
    cv.rect(311, 119, 321, 121, IRON, lambda x, y: 3.0 - (y - 119) * 0.6)
    cv.line(316, 119, 310, 104, IRON, 3.4)
    cv.line(317, 119, 311, 104, IRON, 1.8)
    cv.line(310, 104, 300, 96, IRON, 3.4)
    cv.line(310, 105, 300, 97, IRON, 1.8)
    cv.disc(310, 104, 1.4, 1.4, IRON, 4.0)
    for y in range(94, 102):
        t = (y - 94) / 7
        half = 3 + t * 4
        for x in range(round(299 - half), round(299 + half) + 1):
            cv.put(x, y, STEEL, 5.0 - (x - 299) / half * 1.2 - t * 1.4 + (1.2 if y == 94 else 0), 0.2)
    # pols que balla a la llum del flexo
    for i in range(14):
        px, py = 286 + int(hr(i, 61) * 26), 104 + int(hr(i, 62) * 14)
        cv.put(px, py, BULB, 2.6 + hr(i, 63), 0)
    cv.hline(294, 304, 102, BULB, 3.5, 0)
    cv.hline(296, 302, 103, BULB, 4.5, 0)
    cv.glow(299, 106, 30, (255, 220, 150), 0.4)

    # ─── Taula de llum amb els plànols (351..466 × 81..136) ───────────────
    LX0, LX1 = 354, 463
    LB, LT = 120, 86                                                  # vora de davant / del fons
    # potes i travesser
    for lx in (LX0 + 6, LX1 - 9):
        cv.rect(lx, LB + 4, lx + 3, 158, STEEL, lambda x, y: 3.2 - (x - lx) * 0.6)
    cv.rect(LX0 + 6, 142, LX1 - 6, 143, STEEL, 2.0)
    cv.darken(LX0 + 2, 154, LX1 + 4, 161, lambda x, y: 0.7 - (y - 154) / 10)
    # marc inclinat
    for y in range(LT - 2, LB + 5):
        t = (y - LT) / (LB - LT)
        xl, xr = LX0 + 6 - t * 6, LX1 - 6 + t * 6
        for x in range(round(xl), round(xr) + 1):
            if y > LB:
                lvl = [4.6, 3.6, 2.8, 2.0][min(3, y - LB - 1)]
            else:
                lvl = 2.4 + t * 0.6
            cv.put(x, y, PANEL, lvl)
    # vidre de llum: el plànol cian, encès des de sota
    GX0, GX1 = LX0 + 9, LX1 - 9
    for y in range(LT + 2, LB - 1):
        t = (y - LT) / (LB - LT)
        xl, xr = GX0 - t * 6, GX1 + t * 6
        for x in range(round(xl), round(xr) + 1):
            u = (x - xl) / (xr - xl)
            lvl = 2.2 + (1 - abs(u - 0.5) * 2) * 0.6 + (0.4 if (x % 6 == 0 or y % 5 == 0) else 0)
            cv.put(x, y, BLUEP, lvl, 0.2)

    def bp(x, y, lvl=5.5):
        cv.put(x, y, BLUEP, lvl, 0)

    # La Gavina: anell de l'estació, mòduls i, a sota, la cambra 1
    cx, cy = 392, 101
    for a in range(0, 360, 3):
        bp(round(cx + math.cos(math.radians(a)) * 18), round(cy + math.sin(math.radians(a)) * 7))
        if a % 9 == 0:
            bp(round(cx + math.cos(math.radians(a)) * 12), round(cy + math.sin(math.radians(a)) * 4.6), 4.5)
    for a in range(0, 360, 45):
        bp(round(cx + math.cos(math.radians(a)) * 15), round(cy + math.sin(math.radians(a)) * 5.8))
    cv.rect(cx - 2, cy - 2, cx + 2, cy + 2, BLUEP, 4.5, 0)
    cv.vline(cx, cy + 3, cy + 13, BLUEP, 5.5, 0)                          # el pou fins a la cambra
    for a in range(0, 360, 20):
        bp(round(cx + math.cos(math.radians(a)) * 4), round(cy + 14 + math.sin(math.radians(a)) * 2))
    # rètol i línies de text del plànol
    text(cv, 418, 90, 'GAVINA', BLUEP, 5.5, 0)
    for y in (97, 100, 103):
        cv.hline(418, 418 + int(hr(y, 2) * 22) + 10, y, BLUEP, 4.5, 0)
    cv.rect(418, 108, 452, 115, BLUEP, 3.5, 0)
    cv.hline(418, 452, 108, BLUEP, 5.5, 0)
    cv.vline(436, 108, 115, BLUEP, 5.5, 0)
    # cota
    for x in range(372, 413, 2):
        bp(x, 89, 4.5)
    # llapis i un pes de paper damunt del plànol
    cv.line(366, 114, 378, 110, WARN, 3.6, 0.4)
    cv.put(379, 110, PAPER, 4.0, 0.4)
    cv.disc(448, 92, 2.4, 1.6, IRON, lambda nx, ny: 3.4 - nx - ny, 0.5)
    cv.glow(408, 102, 54, (120, 210, 255), 0.35)

    # ─── Detalls de paret ─────────────────────────────────────────────────
    # rètol de l'arxiu
    cv.rect(360, 32, 456, 52, SIGN, 3.5, 0.4)
    cv.rect(360, 32, 456, 39, RED, 2.5, 0.2)
    text(cv, 364, 33, 'ARXIU CENTRAL', SIGN, 4.5, 0)
    text(cv, 364, 42, 'ACCES RESTRINGIT', HULL, 1.5, 0)
    cv.hline(364, 430, 48, HULL, 2.5, 0.3)
    cv.darken(361, 53, 457, 54, 0.4)
    # termòstat/higròmetre (per al paper)
    cv.rect(336, 60, 346, 74, HULL, lambda x, y: 1.0 if x == 346 or y == 74 else 3.4)
    cv.rect(338, 62, 344, 66, TEAL, 3.0, 0)
    cv.hline(339, 342, 64, TEAL, 5.0, 0)
    # rajola d'avís d'incendi
    cv.rect(468, 96, 477, 104, RED, 3.0)
    cv.rect(470, 98, 475, 102, PAPER, 3.6)

    # Ombres de contacte paret-terra
    cv.darken(0, 154, W - 1, 157, lambda x, y: 0.6 - (y - 154) * 0.15)

    # ─── Terra ────────────────────────────────────────────────────────────
    # (es dibuixa per sota de la paret; les ombres dels mobles ja hi són a sobre)


def _floor(cv):
    def dust(x, y):
        return -0.3 if hr(x // 5, y // 3, 44) > 0.92 else 0.0
    deck(cv, VX, VY, FS, FK, 0.0, 0.0, y0=FLOOR_Y, extra=dust, base=2.3)


_bg = bg


def bg(cv):  # noqa: F811
    _floor(cv)
    _bg(cv)


# ─── Carpeta caiguda (prop): darrere l'arxivador, a terra, amb els fulls escampats ──

def carpeta(cv):
    # ombra
    cv.poly([(204, 166), (232, 163), (234, 166), (206, 169)], DECK, 0.2, 0)
    # carpeta oberta en V, recolzada al costat de l'arxivador
    cv.poly([(203, 158), (219, 152), (222, 163), (205, 166)], MANILA, lambda x, y: 2.6 + (x - 203) / 20)
    cv.poly([(219, 152), (232, 156), (233, 164), (222, 163)], MANILA, lambda x, y: 3.4 - (x - 219) / 20)
    cv.line(219, 152, 222, 163, MANILA, 1.2)
    # fulls que en surten
    cv.poly([(208, 157), (218, 154), (220, 161), (209, 163)], PAPER, 3.8)
    cv.poly([(224, 158), (233, 160), (231, 165), (222, 164)], PAPER, 4.2)
    for y in (157, 159, 161):
        cv.line(210, y, 217, y - 2, PAPER, 2.2)
    # pols al damunt
    for i in range(6):
        cv.put(205 + int(hr(i, 1) * 26), 156 + int(hr(i, 2) * 9), PAPER, 1.6)
    # pestanya amb número
    cv.rect(211, 150, 216, 152, MANILA, 4.0)


PROPS = {'carpeta': carpeta}
