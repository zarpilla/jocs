"""
Moll de l'hangar de La Gavina (Acte 2, Vet): el moll de càrrega de la fàbrica (fabrica_moll) cent vint anys
després, tapat de planxes d'acer. Hi sobreviuen la biga del sostre, el pilar 7 (pintura de fàbrica que salta),
el conducte de pressió (rovellat, manòmetre a zero), les reixes del terra i, darrere la comporta encallada, la
mateixa llançadora, vella i sense els tres components. Les peces comunes vénen de fabrica_moll.
Llums: dos fluorescents freds penjats de la biga, la balisa taronja de la comporta i el pilot cian de la porta.
"""
import math
import random

from hd.pix import (Canvas, Light, B4, W, H, hr, mix, ramp, STEEL, PANEL, ORANGE, CYAN, TEAL, WARN, RUST, BRICK,
                    IRON, GRAY, PAPER, MANILA, WALNUT, SIL, SPACE, PINK, COPPER, GOLD)
from hd.rooms.fabrica_moll import (pillar, carved_mark, grate, shuttle, pipe, bricks, text, VP, FLOOR_Y, MORTAR)

WATER = [(4, 14, 22), (8, 26, 38), (14, 42, 58), (24, 64, 80), (40, 92, 110), (70, 130, 146), (130, 186, 196), (210, 240, 244)]
DUST = ramp((60, 58, 56), (120, 116, 108), (176, 170, 158), n=6)

LIGHT = Light(vignette=(70, 40), floor_fade=(198, 44))
LIGHT.point(96, 34, r=160, k=2.7, squash=0.85, down=True)          # fluorescent esquerre
LIGHT.point(352, 34, r=180, k=2.5, squash=0.85, down=True)         # fluorescent dret
LIGHT.point(222, 22, r=70, k=1.1)                                 # balisa de la comporta
LIGHT.point(70, 96, r=46, k=0.9)                                  # pilot de la porta

COMPORTA = (214, 27, 476, 150)
PILAR_CX = 186                       # el pilar 7, a la dreta del conducte (com al moll)
PIPE_X = 147                         # el conducte (147..157), entre l'escala i el pilar


def wall_panels(cv, x0, x1, y0, y1):
    """Planxes d'acer cargolades (la presó posada damunt de la fàbrica)."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            u, v = (x - 2) % 40, (y - y0) % 33
            lvl = 2.0 + (hr((x - 2) // 40, (y - y0) // 33, 3) - 0.5) * 0.5 - v * 0.012
            if u == 0 or v == 0:
                lvl = 0.6
            elif u == 1 or v == 1:
                lvl += 1.0
            elif u == 39 or v == 32:
                lvl -= 0.5
            if u in (4, 35) and v in (4, 28):
                cv.put(x, y, PANEL, lvl + 2.2)
                continue
            cv.put(x, y, PANEL, lvl)


def floor_deck(cv):
    """Terra de planxes estriades, en perspectiva cap a VP."""
    vx, vy = VP
    for y in range(FLOOR_Y, H):
        dep = y - vy
        for x in range(W):
            u = (x - vx) / dep * 2.2
            pl = math.floor(u)
            fr = (u - pl) * dep / 2.2
            t = 900 / dep
            seg = math.floor(t / 2.6)
            seg_up = math.floor(900 / (dep - 1) / 2.6)
            lvl = 1.8 + (hr(pl, seg, 2) - 0.5) * 0.5
            if (x + y * 2) % 7 == 0 or (x - y * 2) % 7 == 0:
                lvl += 0.45                                       # estries
            if fr < 1:
                lvl = 0.6
            elif seg != seg_up:
                lvl = 0.7
            if y < 160:
                lvl -= (160 - y) / 7 * 1.2
            cv.put(x, y, STEEL, lvl)


def bg(cv):
    # ─── Sostre: planxes, i la biga d'acer de la fàbrica (encara hi és) ────
    cv.rect(0, 0, W - 1, 12, PANEL, lambda x, y: 0.4 + (0.6 if x % 40 == 1 else 0), 0.4)
    cv.rect(0, 13, W - 1, 20, PANEL, lambda x, y: [3.6, 3.0, 2.2, 1.8, 1.8, 1.8, 1.4, 0.6][y - 13] + (hr(x // 3, y, 2) - 0.5) * 0.4)
    for x in range(4, W, 10):
        cv.put(x, 14, PANEL, 4.4)
        cv.put(x, 19, RUST, 2.0)
    for x in range(W):                                            # rovell que surt per sota la pintura
        if hr(x // 4, 77) > 0.7:
            cv.put(x, 18 + (x % 2), RUST, 2.2)
    # safata de cables penjada de la biga
    cv.rect(0, 21, W - 1, 23, STEEL, lambda x, y: 2.6 - (y - 21) * 0.8)
    for x in range(0, W):
        if hr(x // 6, 4) > 0.5:
            cv.put(x, 24, [(20, 20, 26), (40, 30, 40), (70, 40, 50)], 1.0 + (x % 3 == 0))

    # ─── Paret: planxes de la presó ────────────────────────────────────────
    wall_panels(cv, 0, W - 1, 25, FLOOR_Y - 1)
    cv.darken(0, 25, W - 1, 30, lambda x, y: (31 - y) / 6)
    # una planxa que falta: a sota, el maó de la fàbrica
    bricks(cv, 122, 32, 145, 62, base=1.4, seed=7)
    for y in range(32, 63):                                       # vora estripada
        for x in (121, 146):
            cv.put(x, y, PANEL, 0.4 if x == 121 else 3.0)
    for x in range(121, 147):
        cv.put(x, 31, PANEL, 0.4)
        cv.put(x, 63, PANEL, 3.2)
    cv.darken(122, 32, 145, 36, lambda x, y: 0.6)
    # sòcol d'acer
    cv.rect(0, FLOOR_Y - 5, W - 1, FLOOR_Y - 1, STEEL, lambda x, y: 1.6 + (1.2 if y == FLOOR_Y - 5 else 0))

    # ─── Terra ────────────────────────────────────────────────────────────
    floor_deck(cv)
    # línia groga de seguretat davant la comporta
    vx, vy = VP
    for y in range(156, 160):
        for x in range(212, W):
            yel = ((x - y) // 6) % 2 == 0
            cv.put(x, y, WARN if yel else STEEL, (3.0 if yel else 0.6) - (159 - y) * 0.1)
    # reixes de desguàs (les de la fàbrica, envellides): la 1a és la sortida del conducte; la 2a, la del pilar 7
    for xa, xb in ((16, 54), (118, 156), (214, 252), (296, 334)):
        grate(cv, round(xa * 480 / 352), round(xb * 480 / 352), aged=True)

    # ─── Porta del passadís (8..65 × 46..155) ─────────────────────────────
    cv.rect(8, 44, 64, FLOOR_Y - 1, STEEL, lambda x, y: 1.4 + (1.6 if x == 9 or y == 45 else 0) - (0.8 if x == 63 else 0))
    for y in range(50, FLOOR_Y - 1):
        for x in range(14, 59):
            u = (x - 14) / 44
            lvl = 3.2 - u * 1.4 + (0.6 if x in (15, 16) else 0) - (0.9 if x == 36 else 0) + (0.4 if x == 37 else 0)
            cv.put(x, y, STEEL, lvl)
    for y in range(52, 58):                                       # franges al capdamunt
        for x in range(14, 59):
            yel = ((x + y) // 4) % 2 == 0
            cv.put(x, y, WARN if yel else STEEL, 3.4 if yel else 0.8)
    for x0_ in (22, 44):                                          # finestretes
        cv.rect(x0_, 66, x0_ + 7, 80, STEEL, 0.6)
        cv.rect(x0_ + 1, 67, x0_ + 6, 79, TEAL, lambda x, y: 1.0 + (y - 67) * 0.05, 0.2)
        cv.put(x0_ + 2, 68, CYAN, 3.0, 0)
    # panell de la porta amb el pilot cian
    cv.rect(66, 88, 73, 104, STEEL, lambda x, y: 2.6 - (x - 66) * 0.15)
    cv.rect(68, 91, 71, 94, CYAN, 4.0, 0)
    for k in range(3):
        cv.rect(68, 97 + k * 2, 71, 97 + k * 2, STEEL, 4.0)
    cv.glow(69, 92, 14, (110, 220, 255), 0.4)
    text(cv, 20, 46, 'C', WARN, 3.0, 0.3)

    # ─── Cartell del somriure (decoració de la presó) ─────────────────────
    cv.rect(82, 50, 106, 82, PAPER, lambda x, y: 3.4 - (y - 50) * 0.02, 0.6)
    cv.disc(94, 63, 8, 8, WARN, lambda nx, ny: 3.8 - ny * 0.6, 0.4)
    cv.put(91, 61, SIL, 0.4, 0); cv.put(97, 61, SIL, 0.4, 0)
    for i in range(-4, 5):
        cv.put(94 + i, 66 + (1 if abs(i) < 3 else 0) - (1 if abs(i) == 4 else 0), SIL, 0.4, 0)
    text(cv, 85, 74, 'SOMRIU', [(140, 40, 60), (180, 60, 80)], 0.6, 0)
    cv.put(83, 51, GRAY, 1.0); cv.put(105, 51, GRAY, 1.0)
    cv.darken(103, 76, 106, 82, lambda x, y: 0.4)                  # cantonada pelada

    # ─── Escala cap al nivell de sota (76..136 × 100..155) ───────────────
    EX0, EX1, EY0 = 80, 132, 104
    cv.rect(EX0 - 4, EY0 - 4, EX1 + 4, FLOOR_Y - 1, STEEL, lambda x, y: 2.4 + (1.2 if y == EY0 - 4 else 0))
    for x in range(EX0 - 4, EX1 + 5):                             # franges
        if ((x // 4) % 2) == 0:
            cv.put(x, EY0 - 2, WARN, 3.2)
            cv.put(x, EY0 - 3, WARN, 3.4)
    for y in range(EY0, FLOOR_Y):
        for x in range(EX0, EX1 + 1):
            cv.put(x, y, SPACE, 1.4 - (y - EY0) * 0.02, 0)
    # reixa de l'arxiu al fons, amb la cadena i el rètol
    GX0, GX1, GY0, GY1 = 94, 118, 110, 134
    for y in range(GY0, GY1 + 1):
        for x in range(GX0, GX1 + 1):
            if (x - GX0) % 4 == 0 or y in (GY0, GY1):
                cv.put(x, y, STEEL, 2.6, 0.4)
    cv.rect(98, 112, 114, 116, MANILA, 3.0, 0.4)
    text(cv, 97, 112, 'ARXIU', [(30, 24, 20), (40, 30, 24)], 0.4, 0)
    for i in range(18):                                            # cadena
        x = 96 + i + (0 if i % 2 else 0)
        y = 122 + round(math.sin(i / 17 * math.pi) * 3)
        cv.put(x, y, IRON, 3.6 if i % 2 else 2.0, 0.4)
    cv.rect(104, 124, 108, 128, GOLD, 2.4, 0.4)                    # cadenat
    # graons que baixen
    for i, y in enumerate((150, 146, 142, 139, 136)):
        inset = i * 3
        cv.hline(EX0 + inset, EX1 - inset, y, STEEL, 3.6 - i * 0.5)
        cv.hline(EX0 + inset, EX1 - inset, y + 1, STEEL, 1.6 - i * 0.3)
    # baranes
    for s in (-1, 1):
        bx = EX0 + 2 if s < 0 else EX1 - 2
        cv.line(bx, 112, bx - s * 10, 150, STEEL, 4.2)
        cv.vline(bx, 112, 150, STEEL, 2.6)
    cv.glow(106, 130, 18, (80, 120, 140), 0.12)

    # ─── Conducte (rovellat): de dalt fins a terra i cap a la comporta ────
    pipe(cv, aged=True, x=PIPE_X, w=11, run_y=26, y_end=FLOOR_Y - 1)
    for yy in range(140, 151):                                     # tram cap a la llançadora
        i = yy - 140
        for xx in range(PIPE_X + 10, 216):                          # passa per darrere el pilar
            cv.put(xx, yy, RUST, [1.6, 3.0, 3.8, 3.4, 3.0, 2.6, 2.2, 1.8, 1.4, 1.0, 0.6][i] + (hr(xx // 3, yy) - 0.5) * 0.5)

    # ─── Pilar 7: el de la fàbrica, envellit ──────────────────────────────
    pillar(cv, PILAR_CX, 21, FLOOR_Y - 1, aged=True)
    # abraçadora de la presó amb un feix de cables
    for y in range(36, 41):
        for x in range(PILAR_CX - 9, PILAR_CX + 10):
            cv.put(x, y, STEEL, 3.0 - (x - PILAR_CX) * 0.15 + (1 if y == 36 else 0) - (1 if y == 40 else 0))
    cv.put(PILAR_CX - 7, 38, STEEL, 5.0); cv.put(PILAR_CX + 7, 38, STEEL, 3.0)
    cv.darken(PILAR_CX - 14, FLOOR_Y, PILAR_CX + 14, FLOOR_Y + 4, lambda x, y: 0.8 - abs(x - PILAR_CX) / 20)

    # ─── La comporta, tancada i rovellada (214..476 × 10..150) ────────────
    comporta(cv)

    # ─── Caixa de recanvis (409..450 × 151..173) ──────────────────────────
    cv.darken(408, 168, 452, 174, lambda x, y: 0.8)
    for y in range(154, 171):
        for x in range(412, 448):
            lvl = 2.6 + (hr(x // 5, 9) - 0.5) * 0.4 - (0.6 if (y - 154) % 6 == 5 else 0)
            if y < 157:
                lvl = 3.6 - (y - 154) * 0.2                        # tapa
            if x in (412, 447):
                lvl = 1.4 if x == 447 else 3.4
            cv.put(x, y, WALNUT, lvl)
    cv.hline(412, 447, 157, WALNUT, 0.8)
    cv.rect(420, 160, 440, 164, MANILA, 2.2)
    text(cv, 421, 160, 'RECAN', [(40, 30, 24), (60, 44, 30)], 0.4, 0)
    for x, y in ((415, 166), (444, 159), (433, 168)):
        cv.put(x, y, RUST, 3.0)
    cv.rect(410, 167, 414, 170, STEEL, 2.4)                        # un cargol caigut

    # ─── Fluorescents i balisa ────────────────────────────────────────────
    lamps(cv)
    # balisa
    cv.rect(217, 23, 227, 26, STEEL, 2.6)
    cv.disc(222, 20, 4, 4, ORANGE, lambda nx, ny: 5.0 - ny - abs(nx), 0)
    cv.glow(222, 22, 26, (255, 150, 60), 0.45)

    # tint fred general i una mica de calor de la balisa a la comporta
    cv.tint(0, 0, W - 1, H - 1, (40, 70, 110), 0.10)
    cv.tint(200, 10, 300, 90, (255, 140, 60), lambda x, y: max(0, 0.16 * (1 - math.hypot(x - 222, y - 22) / 80)))


def lamps(cv, only=(96, 352)):
    for lx in only:
        cv.vline(lx - 16, 24, 30, STEEL, 2.0)
        cv.vline(lx + 16, 24, 30, STEEL, 2.0)
        cv.rect(lx - 20, 30, lx + 20, 32, STEEL, lambda x, y: 3.2 - (y - 30) * 0.8)
        cv.hline(lx - 18, lx + 18, 33, [(230, 244, 255)], 0, 0)
        cv.hline(lx - 18, lx + 18, 34, CYAN, 4.4, 0)
        cv.glow(lx, 36, 34, (210, 236, 255), 0.35)


def comporta(cv):
    X0, Y0, X1, Y1 = COMPORTA
    # marc
    cv.rect(X0 - 2, Y0 - 2, X0 + 3, Y1, STEEL, lambda x, y: [1.0, 3.6, 2.8, 2.2, 1.6, 0.8][x - X0 + 2])
    cv.rect(X1 - 3, Y0 - 2, X1 + 2, Y1, STEEL, lambda x, y: [1.0, 2.4, 2.0, 1.6, 1.0, 0.6][x - X1 + 3])
    cv.rect(X0 - 2, Y0 - 2, X1 + 2, Y0 + 2, STEEL, lambda x, y: 3.0 - (y - Y0 + 2) * 0.5)
    rnd = random.Random(62)
    stains = [(rnd.randint(X0 + 8, X1 - 8), rnd.randint(Y0 + 6, Y1 - 30), rnd.uniform(5, 12)) for _ in range(10)]
    for y in range(Y0 + 3, Y1 - 6):
        k = (y - Y0 - 3) % 12
        for x in range(X0 + 4, X1 - 3):
            lvl = 2.6 + [1.2, 0.8, 0.4, 0.2, 0.1, 0.0, -0.1, -0.2, -0.3, -0.5, -0.9, -1.8][k]
            lvl += (hr(x // 24, (y - Y0) // 12, 5) - 0.5) * 0.3
            cv.put(x, y, STEEL, lvl)
            if k == 1 and x % 16 == 6:
                cv.put(x, y, STEEL, lvl + 2.2)                    # reblons
    # rovell: clapes suaus a les juntes i regalims que baixen pels cargols
    for y in range(Y0 + 3, Y1 - 6):
        k = (y - Y0 - 3) % 12
        for x in range(X0 + 4, X1 - 3):
            r = 0.0
            for sx, sy, rr in stains:
                d = math.hypot(x - sx, (y - sy) * 1.6) / rr
                if d < 1:
                    r = max(r, 1 - d)
            n = hr(x // 2, y // 2, 9)
            if r * 0.8 + n * 0.35 > 0.55:
                cv.put(x, y, RUST, 1.0 + r * 1.4 + (0.8 if k < 2 else 0) - (0.8 if k > 9 else 0))
    for x in range(X0 + 6, X1 - 4, 16):
        for row in range(0, (Y1 - Y0) // 12):
            if hr(x, row, 13) > 0.6:
                y0_ = Y0 + 5 + row * 12
                ln = 3 + int(hr(x, row, 14) * 9)
                for y in range(y0_, min(y0_ + ln, Y1 - 8)):
                    cv.put(x, y, RUST, 2.0 - (y - y0_) * 0.08)
    # franges de perill a baix
    for y in range(Y1 - 6, Y1 + 1):
        for x in range(X0 + 4, X1 - 3):
            yel = ((x + y) // 6) % 2 == 0
            cv.put(x, y, WARN if yel else STEEL, (3.0 if yel else 0.6) - (0.8 if hr(x // 3, y, 8) > 0.85 else 0))
    cv.hline(X0 + 4, X1 - 4, Y1 + 1, SIL, 0.0, 0)
    # rètol de plantilla
    text(cv, 380, 60, 'MOLL L-1', WARN, 2.2, 0.6)
    # encaix de la palanca, buit
    EX, EY0, EY1 = 226, 86, 138
    cv.rect(EX - 6, EY0, EX + 6, EY1, STEEL, lambda x, y: 3.4 - (x - EX + 6) * 0.22)
    cv.rect(EX - 3, EY0 + 2, EX + 3, EY1 - 2, SIL, 0.2, 0)
    cv.rect(EX - 7, EY0 - 2, EX + 7, EY0, STEEL, 4.2)
    for yy in (EY0 + 8, EY1 - 8):
        cv.rect(EX - 8, yy, EX + 8, yy + 2, STEEL, 3.0)
    cv.darken(EX + 7, EY0, EX + 10, EY1, lambda x, y: 0.6)


# ─── Props ──────────────────────────────────────────────────────────────────

def p_llancadora(cv):
    """La comporta oberta (plegada a dalt) i, a la badia, la llançadora vella."""
    X0, Y0, X1, Y1 = COMPORTA
    # badia fosca
    for y in range(Y0 + 3, Y1 + 1):
        for x in range(X0 + 4, X1 - 3):
            if y > 140:
                cv.put(x, y, STEEL, 0.8 + (y - 140) * 0.12 - (0.6 if x % 14 == 0 else 0), 0.5)
            else:
                cv.put(x, y, STEEL, 0.5 + (0.4 if (x - X0) % 40 == 0 else 0) + (hr(x // 40, y // 33) - 0.5) * 0.3, 0.5)
    # porta exterior de la badia, al fons, amb una finestreta a l'espai
    cv.rect(392, 50, 462, 136, STEEL, lambda x, y: 1.4 + (0.8 if x == 392 or y == 50 else 0), 0.5)
    cv.vline(427, 52, 136, STEEL, 0.4, 0.5)
    cv.rect(416, 60, 438, 76, SIL, 0.5, 0)
    for y in range(61, 76):
        for x in range(417, 438):
            cv.put(x, y, SPACE, 1.2 + (y - 61) * 0.08, 0)
    for x, y in ((420, 64), (431, 63), (426, 70), (435, 72), (419, 73)):
        cv.flat(x, y, (220, 226, 255))
    for y in range(120, 136):
        for x in range(394, 461):
            yel = ((x + y) // 5) % 2 == 0
            cv.put(x, y, WARN if yel else STEEL, (1.8 if yel else 0.4), 0.4)
    # comporta plegada a dalt
    for y in range(Y0 + 3, Y0 + 22):
        k = (y - Y0 - 3) % 6
        for x in range(X0 + 4, X1 - 3):
            lvl = 2.6 + [1.2, 0.6, 0.0, -0.3, -0.7, -1.8][k]
            if hr(x // 2, (y - Y0) // 2, 2) * 0.5 + hr(x // 23, 3) * 0.5 > 0.8:
                cv.put(x, y, RUST, 0.8 + lvl * 0.5)
            else:
                cv.put(x, y, STEEL, lvl)
    for y in range(Y0 + 22, Y0 + 27):
        for x in range(X0 + 4, X1 - 3):
            yel = ((x + y) // 6) % 2 == 0
            cv.put(x, y, WARN if yel else STEEL, 3.0 if yel else 0.6)
    cv.darken(X0 + 4, Y0 + 27, X1 - 4, Y0 + 34, lambda x, y: (Y0 + 35 - y) / 7)
    # pòrtic de manteniment i mànegues
    for gx in (240, 384):
        cv.rect(gx, 54, gx + 3, 148, STEEL, lambda x, y: 2.6 - (x - gx) * 0.4)
    cv.rect(240, 54, 387, 57, STEEL, lambda x, y: 3.0 - (y - 54) * 0.6)
    cv.line(250, 57, 262, 82, STEEL, 1.2)                          # teranyines
    cv.line(378, 57, 368, 80, STEEL, 1.2)
    for i in range(10):
        cv.put(244 + i * 2, 58 + i, DUST, 3.4)
    # la llançadora (vella, coberta de pols, amb tres forats)
    shuttle(cv, 250, 100, aged=True)
    # mànega del conducte fins a la llançadora
    for i in range(70):
        t = i / 69
        x = 218 + t * 110
        y = 146 - math.sin(t * math.pi) * -4 + 0 * t
        cv.put(x, y, RUST, 2.6)
        cv.put(x, y + 1, RUST, 1.2)
    cv.line(328, 146, 342, 112, RUST, 2.4)
    # etiqueta al costat dels forats
    cv.rect(352, 118, 360, 123, PAPER, 3.6, 0.6)
    cv.hline(353, 359, 120, RUST, 1.4, 0.5)
    # pols a l'aire, a la llum
    rnd = random.Random(3)
    for _ in range(40):
        x, y = rnd.randint(X0 + 10, X1 - 10), rnd.randint(60, 140)
        if cv.get(x, y)[3]:
            cv.put(x, y, DUST, 3.0)
    lamps(cv, only=(352,))                                        # el fluorescent penja per davant


def p_porta_llancadora(cv):
    """La porta de la llançadora oberta: la fulla girada i l'interior fosc."""
    x0, cy = 250, 100
    dx0, dx1, dy0, dy1 = x0 + 40, x0 + 58, cy - 17, cy + 19
    for y in range(dy0, dy1 + 1):
        for x in range(dx0, dx1 + 1):
            cv.put(x, y, SIL, 0.4 + (y - dy0) * 0.02, 0)
    # tauler de dins, amb un pilot
    cv.rect(dx0 + 4, dy0 + 10, dx1 - 3, dy0 + 14, STEEL, 1.4, 0)
    cv.put(dx0 + 6, dy0 + 11, CYAN, 3.6, 0)
    cv.put(dx0 + 10, dy0 + 11, ORANGE, 3.0, 0)
    cv.glow(dx0 + 8, dy0 + 12, 9, (100, 200, 255), 0.3)
    # seient
    cv.rect(dx0 + 5, dy1 - 10, dx1 - 4, dy1 - 7, WALNUT, 1.6, 0.4)
    cv.rect(dx1 - 6, dy1 - 18, dx1 - 4, dy1 - 7, WALNUT, 1.2, 0.4)
    # fulla oberta, vista de cantell
    for y in range(dy0 - 1, dy1 + 2):
        for x in range(dx0 - 7, dx0):
            cv.put(x, y, GRAY, 2.0 + (dx0 - x) * 0.25 - (y - dy0) * 0.01)
    cv.vline(dx0 - 7, dy0 - 1, dy1 + 1, GRAY, 4.0)


def p_aigua(cv):
    """El moll inundat: aigua al terra (mig transparent), l'escala plena i el raig del conducte rebentat."""
    P = cv.P
    for y in range(FLOOR_Y + 1, H):
        for x in range(W):
            t = (y - FLOOR_Y) / 60
            lvl = 2.2 + LIGHT(x, y) * 0.8 + math.sin(x / 7.0 + y * 1.3) * 0.35
            # reflexos dels fluorescents i de la balisa
            for lx, col in ((96, 1.6), (352, 1.6), (222, 1.0)):
                if abs(x - lx + (y - FLOOR_Y) * 0.0) < 18 - t * 4 and (y + x // 5) % 3 == 0:
                    lvl += col * (1 - abs(x - lx) / 18)
            i = max(0, min(len(WATER) - 1, math.floor(lvl + B4[y & 3][x & 3] - 0.5)))
            a = 110 if i < 5 else 210
            P[x, y] = WATER[i] + (a,)
    # vora d'aigua a la paret
    for x in range(W):
        P[x, FLOOR_Y] = WATER[6] + (200,)
        if x % 3:
            P[x, FLOOR_Y - 1] = WATER[5] + (120,)
    # l'escala, plena fins dalt
    for y in range(106, FLOOR_Y):
        for x in range(80, 133):
            lvl = 1.4 + (y - 106) * 0.02 + (1.4 if y == 106 else 0) + (0.8 if (x + y * 3) % 11 == 0 else 0)
            cv.put(x, y, WATER, lvl, 0)
    # raig del conducte rebentat
    for i in range(26):
        t = i / 25
        for k in range(4):
            x = PIPE_X - 1 - t * 13 - k
            y = 124 + t * t * 28 + k * 2
            cv.put(x, y, WATER, 6.4 - k * 0.8, 0)
    for k in range(8):
        cv.put(PIPE_X - 2 - k % 3, 120 + k, WATER, 5.6, 0)
    cv.put(PIPE_X, 122, SIL, 0.0, 0)
    # esquitxos on cau
    for dx in (-3, -1, 2, 4, 6):
        cv.put(PIPE_X - 16 + dx, 152 - abs(dx) // 2, WATER, 7, 0)
    cv.put(PIPE_X - 16, 150, WATER, 7, 0)


def p_caixa_flotant(cv):
    """Caixa de fusta que sura davant l'escala: «ARXIU · NIVELL -1»."""
    x0, x1, y0, y1 = 84, 118, 146, 163
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            lvl = 2.6 + (hr(x // 4, 3) - 0.5) * 0.4 - (0.6 if (y - y0) % 6 == 5 else 0)
            if y < y0 + 3:
                lvl = 3.6
            if x in (x0, x1):
                lvl = 3.4 if x == x0 else 1.4
            cv.put(x, y, WALNUT, lvl)
    cv.rect(x0 + 4, y0 + 5, x1 - 4, y0 + 11, MANILA, 2.8)
    text(cv, x0 + 6, y0 + 6, 'ARXIU', [(40, 30, 24), (60, 44, 30)], 0.4, 0)
    text(cv, x0 + 6 + 21, y0 + 6, '-1', [(140, 30, 30)], 0, 0)
    # part de sota, dins l'aigua (enfosquida i tremolosa)
    for y in range(y1 + 1, y1 + 5):
        for x in range(x0, x1 + 1):
            if (x + y) % 2:
                cv.put(x + (1 if y % 2 else 0), y, WATER, 2.4)
    for x in range(x0 - 4, x1 + 5):                                # onades al voltant
        if x % 3:
            cv.put(x, y1 + 1, WATER, 6.0)
        if x % 4 == 0:
            cv.put(x, y1 + 3, WATER, 5.0)


def p_marca(cv):
    carved_mark(cv, PILAR_CX - 5, 80, aged=True)


def p_nota_caixa(cv):
    """Una nota perduda: un paper doblegat que surt d'entre la tapa i la caixa."""
    cv.rect(436, 151, 441, 154, PAPER, lambda x, y: 4.4 - (y - 151) * 0.4, 0.6)
    cv.put(441, 151, PAPER, 2.4, 0.6)


PROPS = {
    'llancadora': p_llancadora,
    'porta_llancadora': p_porta_llancadora,
    'aigua': p_aigua,
    'caixa_flotant': p_caixa_flotant,
    'marca_pilar': p_marca,
    'caixa_recanvis': p_nota_caixa,
}
