"""
**El dibuix pla de sempre** (font de les textures de la sala en 3D, gavina_arxiu.py).

Arxiu (La Gavina, Vet), a 640×360 (hd/rooms/gavina_arxiu.py redibuixat a ×4/3): cent vint anys de paperassa sota
el moll de l'hangar. Arxivadors vells, la taula dels expedients, la taula de llum amb els plànols del Projecte
Gavina. Era el despatx del director: encara en queda la canonada de coure, amb el manòmetre verd de rovell.
Llums: el flexo dels expedients, la taula de llum (cian) i la claror freda que baixa per l'escala de l'hangar.
"""
import math

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from hd.pix import (W, H, STEEL, PANEL, WARN, RED, PAPER, MANILA, IRON, SPACE, COPPER, BLUEP, TEAL, GRAY)
from hd.rooms.gavina_arxiu import OLIVE, VERDIGRIS, BULB
from hd640.rooms.gavina_passadis_pla_comu import (HULL, DECK, LAMPW, SIGN, FLOOR_Y, WALL_B, CachedLight, hr, text, text_w, wall,
                                         deck, pool, hazard, ambient_frames)

VX, VY = 333, 53                     # punt de fuga del terra
FS, FK = 2.4, 693.3

LIGHT = CachedLight(vignette=(99, 53), floor_fade=(261, 45))
LIGHT.point(405, 139, r=160, k=2.8, squash=1.2, down=True)           # flexo dels expedients
LIGHT.point(544, 133, r=128, k=1.6, squash=1.3)                       # taula de llum (plànols)
LIGHT.point(48, 40, r=147, k=2.2, squash=0.9)                         # claror de l'escala de l'hangar
LIGHT.add(pool(376, 235, 120, 29, 1.8))
LIGHT.add(pool(547, 229, 93, 24, 1.0))
LIGHT.add(pool(53, 229, 80, 24, 1.2))


def _canonada(cv):
    """La canonada de coure de l'antiga fàbrica, amb el manòmetre."""
    # ─── Canonada de coure de l'antiga fàbrica (el despatx del director era aquí) ──
    PL = [1.8, 3.0, 3.6, 3.2, 2.6, 1.8, 1.0]
    for y in range(27, FLOOR_Y):
        for x in range(283, 290):
            lvl = PL[x - 283]
            if hr(x, y // 4, 17) > 0.72:
                cv.put(x, y, VERDIGRIS, lvl - 0.6)
            else:
                cv.put(x, y, COPPER, lvl - 0.4)
        if y % 45 == 0:
            cv.rect(281, y, 291, y + 3, COPPER, lambda x, y_: 1.6 + (0.8 if y_ == y else 0) - (x - 281) * 0.05)
            cv.hline(281, 291, y, VERDIGRIS, 2.6)
            cv.put(282, y + 2, COPPER, 4.4)
            cv.put(290, y + 2, COPPER, 2.4)
    # manòmetre vell, amb el vidre trencat
    cv.disc(286, 91, 7, 7, VERDIGRIS, lambda nx, ny: 2.8 - nx - ny)
    cv.disc(286, 91, 5, 5, PAPER, lambda nx, ny: 1.8 - ny * 0.5)
    for a in range(200, 341, 28):                                           # l'escala del manòmetre
        cv.put(round(286 + math.cos(math.radians(a)) * 4), round(91 + math.sin(math.radians(a)) * 4), GRAY, 1.2, 0.5)
    cv.line(286, 91, 289, 88, RED, 1.6, 0.5)
    cv.put(286, 91, IRON, 2.0, 0.5)
    cv.line(283, 88, 287, 94, PAPER, 3.4, 0.5)
    cv.line(287, 94, 289, 93, PAPER, 3.0, 0.5)
    # brida que entra al sostre, tallada amb una planxa nova
    cv.rect(277, 23, 295, 27, HULL, lambda x, y: 3.4 + (0.6 if y == 23 else 0))
    for x in (279, 293):
        cv.put(x, 25, HULL, 5.0)


def _arxivadors(cv):
    """Els quatre arxivadors, amb les caixes al damunt i el calaix obert."""
    # ─── Arxivadors (105..274 × 50..205) ──────────────────────────────────
    CABS = [(107, 147), (149, 189), (192, 232), (235, 271)]
    CT = 67
    # caixes d'arxiu damunt dels arxivadors
    for i, (bx0, bx1, bh) in enumerate(((109, 139, 13), (141, 168, 11), (200, 237, 15), (243, 267, 9))):
        cv.rect(bx0, CT - bh, bx1, CT - 1, MANILA, lambda x, y: 2.6 - (x - bx0) / 40 + (0.8 if y == CT - bh else 0))
        cv.rect(bx0 + 5, CT - bh + 4, bx0 + 16, CT - bh + 7, PAPER, 3.6)
        cv.hline(bx0 + 6, bx0 + 6 + int(hr(i, 9) * 8), CT - bh + 5, HULL, 2.0, 0.4)
        cv.vline(bx1, CT - bh, CT - 1, MANILA, 1.0)
        cv.rect(bx1 - 7, CT - bh + 3, bx1 - 4, CT - bh + 5, MANILA, 0.8)       # la nansa de la caixa
    for ci, (x0, x1) in enumerate(CABS):
        cv.rect(x0, CT, x1, WALL_B, OLIVE, lambda x, y: 3.0 - (x - x0) / 80 - (0.6 if y > 198 else 0) +
                (0.15 if hr(x // 3, y // 2, ci, 8) > 0.9 else 0))
        cv.vline(x0, CT, WALL_B, OLIVE, 4.4)
        cv.vline(x0 + 1, CT, WALL_B, OLIVE, 3.6)
        cv.vline(x1, CT, WALL_B, OLIVE, 1.2)
        cv.hline(x0, x1, CT, OLIVE, 5.0)
        cv.hline(x0, x1, CT + 1, OLIVE, 4.0)
        dh = 32
        for di in range(4):
            y0 = CT + 5 + di * (dh + 1)
            y1 = y0 + dh - 1
            open_ = (ci == 2 and di == 1)
            if open_:
                # calaix obert: cartes confiscades a munts
                cv.rect(x0 + 2, y0 - 4, x1 - 2, y0 + 5, OLIVE, 0.4)
                for k in range(7):
                    lx = x0 + 3 + k * 5
                    top = y0 - 7 - int(hr(k, 3) * 5)
                    lv = 3.6 + hr(k, 5) * 0.8 - (k % 2) * 0.5
                    cv.rect(lx, top, lx + 4, y0 + 3, PAPER, lv)
                    cv.vline(lx + 4, top, y0 + 3, PAPER, lv - 1.2)
                    if hr(k, 6) > 0.5:
                        cv.put(lx + 3, top + 1, RED, 3.0)                      # el segell de la carta
                cv.rect(x0 + 1, y0 + 4, x1 - 1, y1 + 5, OLIVE, lambda x, y: 3.4 - (y - y0) / 40)
                cv.hline(x0 + 1, x1 - 1, y0 + 4, OLIVE, 5.4)
                cv.hline(x0 + 1, x1 - 1, y1 + 5, OLIVE, 0.6)
                cv.darken(x0 + 1, y1 + 6, x1 - 1, y1 + 9, 0.6)
                yy = y0 + 11
            else:
                cv.rect(x0 + 4, y0, x1 - 4, y1, OLIVE, lambda x, y: 3.2 - (x - x0) / 65)
                cv.hline(x0 + 4, x1 - 4, y0, OLIVE, 4.6)
                cv.vline(x0 + 4, y0, y1, OLIVE, 4.0)
                cv.hline(x0 + 4, x1 - 4, y1, OLIVE, 1.0)
                cv.vline(x1 - 4, y0, y1, OLIVE, 1.6)
                yy = y0 + 7
            cx = (x0 + x1) // 2
            # portaetiquetes i tirador
            cv.rect(cx - 7, yy, cx + 7, yy + 5, IRON, lambda x, y: 3.6 if y == yy else 3.0)
            cv.rect(cx - 6, yy + 1, cx + 6, yy + 4, PAPER, 3.6 - hr(ci, di) * 1.2)
            cv.hline(cx - 5, cx - 5 + int(hr(ci, di, 2) * 9), yy + 2, HULL, 1.6, 0.4)
            cv.hline(cx - 5, cx - 5 + int(hr(ci, di, 3) * 6), yy + 3, HULL, 2.2, 0.4)
            cv.rect(cx - 5, yy + 10, cx + 5, yy + 12, IRON, lambda x, y: [4.6, 3.0, 1.4][y - yy - 10])
            cv.put(cx - 6, yy + 11, IRON, 2.0)
            cv.put(cx + 6, yy + 11, IRON, 2.0)
        # bonys i rascades
        for k in range(4):
            if hr(ci, k, 8) > 0.45:
                rx, ry = x0 + 5 + int(hr(ci, k) * (x1 - x0 - 11)), CT + 13 + int(hr(ci, k, 1) * 120)
                cv.line(rx, ry, rx + 5, ry + 1, OLIVE, 4.8)
                cv.line(rx, ry + 1, rx + 5, ry + 2, OLIVE, 2.0)
    cv.darken(104, 200, 275, WALL_B, 0.7)


def _prestatge(cv):
    """Els dos prestatges de caixes d'arxiu, damunt la taula."""
    # ─── Prestatge de caixes d'arxiu sobre la taula ───────────────────────
    for sy, boxes in ((93, 7), (128, 6)):
        cv.rect(309, sy, 437, sy + 3, HULL, lambda x, y: [4.4, 3.4, 2.4, 1.2][y - sy])
        for sx in (315, 432):
            cv.rect(sx, sy + 4, sx + 1, sy + 10, HULL, 2.4)
            cv.line(sx, sy + 10, sx + (5 if sx < 400 else -5), sy + 4, HULL, 2.0)
        x = 315 if sy == 93 else 320
        for k in range(boxes):
            bw = 15 + int(hr(sy, k) * 4)
            bh = 19 + int(hr(sy, k, 2) * 8)
            if sy == 128:
                bh = min(bh, 19)
            col = MANILA if hr(sy, k, 3) > 0.25 else PAPER
            cv.rect(x, sy - bh, x + bw - 1, sy - 1, col, lambda xx, yy: 2.4 - (xx - x) / 32 + (0.6 if yy == sy - bh else 0))
            cv.vline(x + bw - 1, sy - bh, sy - 1, col, 0.8)
            cv.rect(x + 3, sy - bh + 4, x + bw - 4, sy - bh + 8, PAPER, 3.6, 0.6)
            cv.hline(x + 4, x + 4 + int(hr(sy, k, 5) * (bw - 9)), sy - bh + 6, HULL, 2.2, 0.4)
            n = str(int(hr(sy, k, 4) * 9) + 1)
            text(cv, x + bw // 2 - 2, sy - bh + 10, n, HULL, 1.0, 0.3)
            x += bw + 1
            if x > 424:
                break
    # caixa tombada al prestatge de dalt
    cv.rect(408, 83, 432, 92, MANILA, lambda x, y: 2.2 - (y - 83) * 0.05)
    cv.hline(408, 432, 83, MANILA, 3.2)
    cv.rect(412, 85, 420, 89, PAPER, 3.2)


def _taula_moble(cv):
    """La taula dels expedients: el tauler, les potes i la calaixera (sense res al damunt)."""
    # ─── Taula dels expedients (305..430 × 141..176) ──────────────────────
    TX0, TX1, TT, TF = 301, 435, 163, 169
    # ombra al terra
    cv.darken(TX0 - 3, FLOOR_Y, TX1 + 8, 216, lambda x, y: 0.8 - (y - FLOOR_Y) / 13)
    # potes
    for lx in (TX0 + 5, TX1 - 9):
        cv.rect(lx, TF + 1, lx + 4, 210, STEEL, lambda x, y: 3.4 - (x - lx) * 0.5)
        cv.rect(lx - 1, 209, lx + 5, 211, STEEL, 1.6)                       # els peus
    cv.rect(TX0 + 5, 195, TX1 - 5, 196, STEEL, lambda x, y: 2.4 if y == 195 else 1.4)   # travesser
    # tauler (gruix i superfície)
    for y in range(TT - 8, TT + 1):
        t = (y - TT + 8) / 8
        cv.hline(TX0 + 4 - round(t * 4), TX1 - 4 + round(t * 4), y, PANEL, 3.4 + t * 0.6)
    cv.rect(TX0, TT + 1, TX1, TF, PANEL, lambda x, y: [5.0, 4.2, 3.6, 3.0, 2.4, 1.0][y - TT - 1])
    # calaixera sota el tauler
    cv.rect(TX1 - 45, TF + 1, TX1 - 11, 200, PANEL, lambda x, y: 2.6 - (x - TX1 + 45) / 65)
    for y0 in (TF + 4, TF + 15):
        cv.rect(TX1 - 43, y0, TX1 - 13, y0 + 8, PANEL, 3.0)
        cv.hline(TX1 - 43, TX1 - 13, y0, PANEL, 4.2)
        cv.hline(TX1 - 43, TX1 - 13, y0 + 8, PANEL, 1.6)
        cv.rect(TX1 - 31, y0 + 4, TX1 - 25, y0 + 4, IRON, 4.6)
        cv.rect(TX1 - 31, y0 + 5, TX1 - 25, y0 + 5, IRON, 1.6)
    cv.vline(TX1 - 11, TF + 1, 200, PANEL, 1.0)


def _taula_objectes(cv, tt=0.0):
    """El que hi ha damunt la taula: els expedients, la tassa, el flexo, la pols i la bombeta."""
    ph = 2 * math.pi * tt
    # expedients: piles de carpetes, una d'oberta amb la fitxa de la I.
    def folder(x0, y0, w, h, lvl, ramp_=MANILA, tab=True):
        cv.rect(x0, y0, x0 + w, y0 + h, ramp_, lambda x, y: lvl + (0.8 if y == y0 else 0) - (0.8 if y == y0 + h else 0))
        if tab:
            cv.rect(x0 + 4, y0 - 2, x0 + 12, y0 - 1, ramp_, lvl + 0.6)
    # pila esquerra
    for k in range(6):
        folder(309 + int(hr(k, 1) * 4), 156 - k * 3, 32, 2, 2.6 + (k % 2) * 0.6, MANILA if k % 3 else RED, tab=k == 5)
    cv.rect(312, 145, 339, 147, MANILA, 3.4)
    cv.hline(314, 330, 146, MANILA, 2.4)
    # carpeta oberta al centre: fitxa amb foto i segell vermell
    cv.poly([(349, 157), (400, 157), (404, 163), (345, 163)], MANILA, 3.0)
    cv.poly([(352, 151), (375, 151), (376, 161), (349, 161)], PAPER, 4.2)
    cv.poly([(376, 151), (399, 151), (401, 161), (376, 161)], PAPER, 3.8)
    cv.vline(376, 151, 161, PAPER, 2.4)                                    # el plec
    cv.rect(354, 152, 360, 158, GRAY, 2.0)                                # foto carnet
    cv.disc(357, 154, 1.6, 1.6, GRAY, 3.6)
    cv.rect(355, 156, 359, 158, GRAY, 3.0)
    for y in (152, 154, 156):
        cv.hline(362, 362 + 6 + int(hr(y, 21) * 6), y, HULL, 2.2, 0.4)
    cv.hline(354, 371, 160, HULL, 1.6, 0.4)                                # el cognom, ratllat
    cv.hline(354, 371, 159, HULL, 0.8, 0.4)
    for y in (152, 154, 156):
        cv.hline(380, 380 + 8 + int(hr(y, 22) * 8), y, HULL, 2.2, 0.4)
    cv.rect(383, 156, 396, 160, RED, 3.0, 0.5)                             # segell «TANCAT»
    cv.rect(384, 157, 395, 159, RED, 4.0, 0.5)
    for x in range(385, 395, 2):
        cv.put(x, 158, RED, 3.0, 0.5)
    # pila dreta, més desordenada
    for k in range(4):
        folder(405 + int(hr(k, 7) * 5), 159 - k * 3, 21, 2, 2.8 + (k % 2) * 0.5)
    cv.put(424, 149, PAPER, 4.6)
    cv.put(425, 149, PAPER, 3.6)
    # tassa de cafè freda
    cv.rect(337, 152, 343, 160, PAPER, lambda x, y: 4.0 - (x - 337) * 0.3)
    cv.hline(338, 342, 152, GRAY, 1.0)                                     # el cafè, a dins
    cv.vline(344, 154, 158, PAPER, 2.4)
    cv.vline(345, 155, 157, PAPER, 1.8)

    # flexo articulat (llum càlida i vella)
    cv.rect(415, 159, 428, 162, IRON, lambda x, y: 3.0 - (y - 159) * 0.5)
    cv.line(421, 159, 413, 139, IRON, 3.4)
    cv.line(422, 159, 414, 139, IRON, 1.8)
    cv.line(413, 139, 400, 128, IRON, 3.4)
    cv.line(413, 140, 400, 129, IRON, 1.8)
    cv.line(418, 150, 412, 136, IRON, 1.2)                                  # la molla
    cv.disc(413, 139, 1.8, 1.8, IRON, 4.0)
    for y in range(125, 136):
        t = (y - 125) / 10
        half = 4 + t * 5
        for x in range(round(399 - half), round(399 + half) + 1):
            cv.put(x, y, STEEL, 5.0 - (x - 399) / half * 1.2 - t * 1.4 + (1.2 if y == 125 else 0), 0.2)
    # pols que balla a la llum del flexo
    # (cada mota sura a poc a poc pel seu compte; amb tt = 0 són al lloc de sempre)
    for i in range(18):
        kx, ky = 1 + int(hr(i, 64) * 3), 1 + int(hr(i, 65) * 2)
        fx, fy = hr(i, 66) * 6.283, hr(i, 67) * 6.283
        dx = round(3.2 * (math.sin(ph * kx + fx) - math.sin(fx)))
        dy = round(2.4 * (math.sin(ph * ky + fy) - math.sin(fy)))
        tw = 0.7 * (math.sin(ph * (kx + ky) + fx) - math.sin(fx))
        px, py = 381 + int(hr(i, 61) * 35) + dx, 139 + int(hr(i, 62) * 19) + dy
        cv.put(px, py, BULB, 2.6 + hr(i, 63) + tw, 0)
    # la bombeta és vella: un cop per cicle fa una mica de figa
    fl = 0.8 if 0.79 <= tt < 0.83 else 0.0
    cv.hline(392, 405, 136, BULB, 3.5 - fl, 0)
    cv.hline(395, 403, 137, BULB, 4.5 - fl, 0)
    cv.hline(397, 401, 138, BULB, 3.6 - fl, 0)
    cv.glow(399, 141, 40, (255, 220, 150), 0.4 - fl * 0.1)


def _taula_llum(cv, tt=0.0):
    """La taula de llum amb els plànols del Projecte Gavina (i la línia d'escaneig)."""
    ph = 2 * math.pi * tt
    # ─── Taula de llum amb els plànols (469..623 × 109..183) ──────────────
    LX0, LX1 = 472, 617
    LB, LT = 160, 115                                                 # vora de davant / del fons
    # potes i travesser
    for lx in (LX0 + 8, LX1 - 12):
        cv.rect(lx, LB + 5, lx + 4, 210, STEEL, lambda x, y: 3.2 - (x - lx) * 0.5)
        cv.rect(lx - 1, 209, lx + 5, 211, STEEL, 1.6)
    cv.rect(LX0 + 8, 189, LX1 - 8, 190, STEEL, lambda x, y: 2.4 if y == 189 else 1.4)
    cv.darken(LX0 + 3, FLOOR_Y, LX1 + 5, 215, lambda x, y: 0.7 - (y - FLOOR_Y) / 13)
    # marc inclinat
    for y in range(LT - 3, LB + 7):
        t = (y - LT) / (LB - LT)
        xl, xr = LX0 + 8 - t * 8, LX1 - 8 + t * 8
        for x in range(round(xl), round(xr) + 1):
            if y > LB:
                lvl = [4.6, 3.8, 3.0, 2.2, 1.4, 1.0][min(5, y - LB - 1)]
            else:
                lvl = 2.4 + t * 0.6
            cv.put(x, y, PANEL, lvl)
    # vidre de llum: el plànol cian, encès des de sota
    GX0, GX1 = LX0 + 12, LX1 - 12
    for y in range(LT + 3, LB - 1):
        t = (y - LT) / (LB - LT)
        xl, xr = GX0 - t * 8, GX1 + t * 8
        for x in range(round(xl), round(xr) + 1):
            u = (x - xl) / (xr - xl)
            lvl = 2.2 + (1 - abs(u - 0.5) * 2) * 0.6 + (0.4 if (x % 8 == 0 or y % 7 == 0) else 0)
            cv.put(x, y, BLUEP, lvl, 0.2)

    def bp(x, y, lvl=5.5):
        cv.put(x, y, BLUEP, lvl, 0)

    # La Gavina: anell de l'estació, mòduls i, a sota, la cambra 1
    cx, cy = 523, 135
    for a in range(0, 360, 2):
        bp(round(cx + math.cos(math.radians(a)) * 24), round(cy + math.sin(math.radians(a)) * 9))
        if a % 8 == 0:
            bp(round(cx + math.cos(math.radians(a)) * 16), round(cy + math.sin(math.radians(a)) * 6), 4.5)
    for a in range(0, 360, 45):
        r0, r1 = 16, 24
        for k in range(r0, r1 + 1, 2):
            bp(round(cx + math.cos(math.radians(a)) * k), round(cy + math.sin(math.radians(a)) * k * 0.375), 4.8)
        mx, my = round(cx + math.cos(math.radians(a)) * 24), round(cy + math.sin(math.radians(a)) * 9)
        cv.rect(mx - 1, my - 1, mx + 1, my + 1, BLUEP, 5.5, 0)                 # els mòduls de l'anell
    cv.rect(cx - 3, cy - 3, cx + 3, cy + 3, BLUEP, 4.5, 0)
    cv.rect(cx - 1, cy - 1, cx + 1, cy + 1, BLUEP, 3.2, 0)
    cv.vline(cx, cy + 4, cy + 17, BLUEP, 5.5, 0)                          # el pou fins a la cambra
    for a in range(0, 360, 15):
        bp(round(cx + math.cos(math.radians(a)) * 5), round(cy + 19 + math.sin(math.radians(a)) * 3))
    # rètol i línies de text del plànol
    text(cv, 557, 120, 'GAVINA', BLUEP, 5.5, 0)
    for y in (131, 135, 139):
        cv.hline(557, 557 + int(hr(y, 2) * 29) + 13, y, BLUEP, 4.5, 0)
    cv.rect(557, 144, 603, 153, BLUEP, 3.5, 0)
    cv.hline(557, 603, 144, BLUEP, 5.5, 0)
    cv.vline(581, 144, 153, BLUEP, 5.5, 0)
    for y in (147, 150):
        cv.hline(560, 560 + int(hr(y, 4) * 12) + 6, y, BLUEP, 4.8, 0)
    # cota
    for x in range(496, 550, 2):
        bp(x, 118, 4.5)
    for x in (496, 549):
        cv.vline(x, 116, 120, BLUEP, 4.5, 0)
    # llapis i un pes de paper damunt del plànol
    cv.line(488, 152, 504, 147, WARN, 3.6, 0.4)
    cv.line(488, 153, 504, 148, WARN, 2.4, 0.4)
    cv.put(505, 147, PAPER, 4.0, 0.4)
    cv.put(506, 147, IRON, 1.4, 0.4)
    cv.disc(597, 123, 3.2, 2.1, IRON, lambda nx, ny: 3.4 - nx - ny, 0.5)
    # línia d'escaneig que recorre el vidre de llum, del fons cap endavant
    f = tt % 1
    env = math.sin(math.pi * f)
    if env > 0.02:
        ys = LT + 3 + f * (LB - LT - 6)
        for k, a in enumerate((0.42, 0.2, 0.1, 0.05)):
            y = int(ys) - k
            tl = (y - LT) / (LB - LT)
            cv.tint(GX0 - tl * 8, y, GX1 + tl * 8, y, (190, 245, 255), env * a)
    cv.glow(544, 136, 72, (120, 210, 255), 0.35)


def _walls(cv, t=0.0, mobles=True):
    """La paret amb tot el que hi ha; amb `mobles` = False, sense la canonada, els arxivadors, els prestatges, la
    taula ni la taula de llum (la sala en 3D els fa a part)."""
    tt = t                                   # (dins la funció, `t` es fa servir per a altres coses)
    ph = 2 * math.pi * tt
    # ─── Paret i sostre ───────────────────────────────────────────────────
    wall(cv, 0, W - 1, seed=5, base=2.6)
    cv.rect(0, 0, W - 1, 9, HULL, lambda x, y: 0.7 + (0.5 if y in (7, 8) else 0))
    cv.hline(0, W - 1, 10, HULL, 3.0)
    cv.hline(0, W - 1, 11, HULL, 1.6)
    cv.hline(0, W - 1, 12, HULL, 0.8)
    # conducte de ventilació al llarg del sostre
    DL = [1.0, 3.4, 3.2, 3.0, 2.8, 2.6, 2.4, 2.1, 1.8, 1.5, 1.0, 0.6]
    for x in range(93, W):
        for y in range(15, 27):
            lvl = DL[y - 15]
            j = (x - 93) % 61
            if j in (0, 1, 2):
                lvl += (0.8, 0.3, -0.8)[j]                                  # brides entre trams
            cv.put(x, y, HULL, lvl)
        if (x - 93) % 61 == 30:
            for y in (17, 23):
                cv.put(x, y, HULL, 4.4)                                     # cargols de la brida del mig
    for x in range(400, 425):                                               # reixeta del conducte
        if x % 3 == 0:
            cv.vline(x, 18, 24, HULL, 0.8)
    cv.darken(93, 27, W - 1, 29, 0.5)

    if mobles:
        _canonada(cv)

    # ─── Escala cap al moll de l'hangar (10..92 × 50..208) ────────────────
    SX0, SX1, ST = 13, 88, 53
    cv.rect(SX0 - 3, ST - 5, SX1 + 3, WALL_B, HULL, lambda x, y: 3.6 if x < SX0 or y < ST else (1.0 if x > SX1 else 2.0))
    cv.hline(SX0 - 3, SX1 + 3, ST - 5, HULL, 4.4)
    # buc fosc, amb la claror de l'hangar que baixa de dalt
    for y in range(ST, FLOOR_Y):
        for x in range(SX0, SX1 + 1):
            lvl = 0.6 + max(0.0, 1 - (y - ST) / 93) * 2.4 - (x - SX0) / 93
            if (y - ST) % 27 == 0 and y > ST + 30:
                lvl -= 0.3                                                  # costures de la paret del buc
            cv.put(x, y, SPACE, lvl + 0.8, 0.3)
    cv.tint(SX0, ST, SX1, WALL_B, (90, 140, 190), lambda x, y: max(0.0, 0.35 - (y - ST) / 400))
    # trapa oberta al sostre, per on entra la llum
    cv.rect(SX0 + 3, ST, SX1 - 3, ST + 4, LAMPW, lambda x, y: 2.5 - (y - ST) * 0.4, 0)
    cv.glow((SX0 + SX1) / 2, ST + 2, 30, (170, 210, 240), 0.25)
    # graons d'acer pujant cap a l'esquerra
    steps = 12
    for i in range(steps):
        t = i / (steps - 1)
        sy = round(200 - t * 133)
        sx0 = round(SX1 - 8 - t * 51)
        cv.rect(sx0 - 21, sy, sx0, sy + 3, STEEL, lambda x, y: [6.4, 5.2, 3.8, 2.4][y - sy] - (sx0 - x) / 40)
        cv.rect(sx0 - 21, sy + 4, sx0, sy + 6, STEEL, 0.6)
        for x in range(sx0 - 18, sx0, 4):
            cv.put(x, sy, STEEL, 3.4)                                       # trama antilliscant
            cv.put(x + 1, sy + 1, STEEL, 3.6)
    # llimonera (planxa lateral de l'escala)
    for k in range(5):
        cv.line(SX1 - 2 + k, WALL_B, SX1 - 61 + k, 61, STEEL, [5.0, 4.0, 3.0, 2.2, 1.2][k])
    for i in range(1, 6):                                                   # reblons de la llimonera
        x, y = SX1 - i * 10, WALL_B - i * 24
        cv.put(x + 2, y, STEEL, 6.4)
    # barana
    cv.line(SX1, 160, SX1 - 56, 56, STEEL, 5.0)
    cv.line(SX1, 161, SX1 - 56, 57, STEEL, 3.0)
    cv.line(SX1, 162, SX1 - 56, 58, STEEL, 1.6)
    for t in (0.0, 0.33, 0.66):
        x = round(SX1 - t * 56)
        y = round(160 - t * 104)
        cv.vline(x, y, y + 40, STEEL, 3.4)
        cv.vline(x + 1, y + 1, y + 40, STEEL, 1.6)
    # rètol de l'hangar
    cv.rect(SX0 + 3, ST + 10, SX0 + 37, ST + 21, SIGN, lambda x, y: 3.5 - (0.6 if y == ST + 21 else 0), 0.3)
    text(cv, SX0 + 6, ST + 12, 'HANGAR', HULL, 0.5, 0)
    cv.put(SX0 + 4, ST + 11, SIGN, 1.6, 0.3)
    cv.put(SX0 + 36, ST + 11, SIGN, 1.6, 0.3)
    hazard(cv, SX0 - 3, 200, SX1 + 3, WALL_B, lvl=3.0, w=4)

    if mobles:
        _arxivadors(cv)

    if mobles:
        _prestatge(cv)

    if mobles:
        _taula_moble(cv)

    if mobles:
        _taula_objectes(cv, tt)

    if mobles:
        _taula_llum(cv, tt)

    # ─── Detalls de paret ─────────────────────────────────────────────────
    # rètol de l'arxiu
    cv.rect(480, 43, 608, 69, SIGN, 3.5, 0.4)
    cv.rect(480, 43, 608, 53, RED, lambda x, y: 2.5 + (0.6 if y == 43 else 0), 0.2)
    text(cv, 485, 45, 'ARXIU CENTRAL', SIGN, 4.5, 0)
    text(cv, 485, 57, 'ACCÉS RESTRINGIT', HULL, 1.5, 0)
    cv.hline(485, 485 + text_w('ACCÉS RESTRINGIT'), 66, HULL, 2.5, 0.3)
    for sx in (482, 606):
        cv.put(sx, 63, SIGN, 1.6, 0.3)
    cv.darken(481, 70, 609, 72, 0.4)
    # termòstat/higròmetre (per al paper)
    cv.rect(448, 80, 461, 99, HULL, lambda x, y: 1.0 if x == 461 or y == 99 else (4.2 if x == 448 or y == 80 else 3.4))
    cv.rect(451, 83, 459, 89, TEAL, 3.0, 0)
    cv.hline(452, 456, 85, TEAL, 5.0, 0)
    cv.hline(452, 454, 87, TEAL, 4.4, 0)
    cv.rect(451, 92, 453, 93, HULL, 2.0)
    # pilot del termòstat que fa pampallugues
    if (tt * 2) % 1 >= 0.62 and (tt * 2) % 1 < 0.72:
        cv.put(457, 95, TEAL, 6.0, 0)
        cv.put(457, 94, TEAL, 3.0, 0)
        cv.put(458, 95, TEAL, 3.0, 0)
    # rajola d'avís d'incendi
    cv.rect(624, 128, 636, 139, RED, lambda x, y: 3.0 + (0.6 if x == 624 or y == 128 else 0))
    cv.rect(627, 131, 633, 136, PAPER, 3.6)
    cv.hline(628, 632, 133, RED, 2.6)

    # Ombres de contacte paret-terra
    cv.darken(0, FLOOR_Y, W - 1, FLOOR_Y + 4, lambda x, y: 0.6 - (y - FLOOR_Y) * 0.12)


def _floor(cv):
    def dust(x, y):
        return -0.3 if hr(x // 7, y // 4, 44) > 0.92 else 0.0
    deck(cv, VX, VY, FS, FK, 0.0, 0.0, y0=FLOOR_Y, extra=dust, base=2.3)


def bg(cv, t=0.0):
    """`t` (0..1): moment del cicle de l'animació de fons (t = 0 és el fons quiet)."""
    _floor(cv)
    _walls(cv, t)


# ─── Carpeta caiguda (prop): darrere l'arxivador, a terra, amb els fulls escampats ──

def carpeta(cv):
    # ombra
    cv.poly([(272, 221), (309, 217), (312, 221), (275, 225)], DECK, 0.2, 0)
    # carpeta oberta en V, recolzada al costat de l'arxivador
    cv.poly([(271, 211), (292, 203), (296, 217), (273, 221)], MANILA, lambda x, y: 2.6 + (x - 271) / 27)
    cv.poly([(292, 203), (309, 208), (311, 219), (296, 217)], MANILA, lambda x, y: 3.4 - (x - 292) / 27)
    cv.line(292, 203, 296, 217, MANILA, 1.2)
    cv.line(271, 211, 292, 203, MANILA, 4.0)
    # fulls que en surten
    cv.poly([(277, 209), (291, 205), (293, 215), (279, 217)], PAPER, 3.8)
    cv.poly([(299, 211), (311, 213), (308, 220), (296, 219)], PAPER, 4.2)
    for y in (209, 212, 215):
        cv.line(280, y, 289, y - 3, PAPER, 2.2)
    cv.line(300, 214, 307, 215, PAPER, 2.6)
    cv.line(299, 216, 305, 217, PAPER, 2.6)
    # pols al damunt
    for i in range(8):
        cv.put(273 + int(hr(i, 1) * 35), 208 + int(hr(i, 2) * 12), PAPER, 1.6)
    # pestanya amb número
    cv.rect(281, 200, 288, 203, MANILA, 4.0)
    cv.hline(283, 286, 201, HULL, 2.0)


PROPS = {'carpeta': carpeta}


# ─── Animació de fons: la pols sura a la llum del flexo, la taula de llum escaneja el plànol,
# el pilot del termòstat fa pampallugues i la bombeta vella fa figa un moment ──────────────────

def _ambient_frames(n=24):
    return ambient_frames(bg, LIGHT, n)


ANIMS = {'ambient': {'frames': _ambient_frames, 'frameDuration': 120}}
