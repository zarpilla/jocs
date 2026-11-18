"""
**El dibuix pla de sempre** (font de les textures de la sala en 3D, gavina_hangar.py).

Moll de l'hangar de La Gavina (hd/rooms/gavina_hangar.py) a 640×360: la mateixa composició ×4/3, dibuixada de nou.
Acte 2, Vet: el moll de càrrega de la fàbrica (fabrica_moll) cent vint anys després, tapat de planxes d'acer. Hi
sobreviuen la biga del sostre, el pilar 7 (pintura de fàbrica que salta), el conducte de pressió (rovellat,
manòmetre a zero), les reixes del terra i, darrere la comporta encallada, la mateixa llançadora, vella i sense els
tres components. Les peces comunes vénen de hd640.rooms.fabrica_moll.
Llums: dos fluorescents freds penjats de la biga, la balisa taronja de la comporta i el pilot cian de la porta.
Animació: `ambient` (la balisa gira, el fluorescent esquerre fa figa i regalima el conducte).
"""
import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)

import math
import random
from functools import lru_cache

from hd.pix import (Canvas, Light, B4, W, H, ramp, STEEL, PANEL, ORANGE, CYAN, TEAL, WARN, RUST, IRON, GRAY,  # noqa: F401
                    PAPER, MANILA, WALNUT, SIL, SPACE, PINK, COPPER, GOLD)
from hd.rooms.gavina_hangar import WATER, DUST
from hd640.rooms.fabrica_moll_pla_comu import (pillar, carved_mark, grate, shuttle, pipe, bricks, text, clip_frames, hr, _ys, _xs,
                                      _interp, VP, FLOOR_Y, MORTAR)  # noqa: F401

LIGHT = Light(vignette=(93, 53), floor_fade=(264, 59))
LIGHT.point(128, 45, r=213, k=2.7, squash=0.85, down=True)         # fluorescent esquerre
LIGHT.point(469, 45, r=240, k=2.5, squash=0.85, down=True)         # fluorescent dret
LIGHT.point(296, 29, r=93, k=1.1)                                  # balisa de la comporta
LIGHT.point(93, 128, r=61, k=0.9)                                  # pilot de la porta

COMPORTA = (285, 36, 635, 200)
PILAR_CX = 248                       # el pilar 7, a la dreta del conducte (com al moll)
PIPE_X = 196                         # el conducte (196..210), entre l'escala i el pilar
PIPE_W = 15
LAMPS = (128, 469)


def wall_panels(cv, x0, x1, y0, y1):
    """Planxes d'acer cargolades (la presó posada damunt de la fàbrica)."""
    for y in _ys(cv, y0, y1):
        for x in _xs(cv, x0, x1):
            u, v = (x - 3) % 53, (y - y0) % 44
            lvl = 2.0 + (hr((x - 3) // 53, (y - y0) // 44, 3) - 0.5) * 0.5 - v * 0.009
            lvl += (hr(x // 3, y // 2, 4) - 0.5) * 0.15                     # el gra de la planxa
            if u == 0 or v == 0:
                lvl = 0.6
            elif u == 1 or v == 1:
                lvl += 1.0
            elif u == 52 or v == 43:
                lvl -= 0.5
            if u in (5, 47) and v in (5, 38):
                cv.put(x, y, PANEL, lvl + 2.2)                              # cargols
                continue
            if u in (6, 48) and v in (6, 39):
                cv.put(x, y, PANEL, lvl - 0.8)
                continue
            cv.put(x, y, PANEL, lvl)


def floor_deck(cv):
    """Terra de planxes estriades, en perspectiva cap a VP."""
    vx, vy = VP
    for y in _ys(cv, FLOOR_Y, H - 1):
        dep = y - vy
        sh = (213 - y) / 9 * 1.2 if y < 213 else 0
        for x in _xs(cv, 0, W - 1):
            u = (x - vx) / dep * 2.2
            pl = math.floor(u)
            fr = (u - pl) * dep / 2.2
            t = 1200 / dep
            seg = math.floor(t / 2.6)
            seg_up = math.floor(1200 / (dep - 1) / 2.6)
            lvl = 1.8 + (hr(pl, seg, 2) - 0.5) * 0.5
            if (x + y * 2) % 9 == 0 or (x - y * 2) % 9 == 0:
                lvl += 0.45                                       # estries
            if fr < 1:
                lvl = 0.6
            elif fr < 2:
                lvl += 0.3
            elif seg != seg_up:
                lvl = 0.7
            cv.put(x, y, STEEL, lvl - sh)


def bg(cv, t=0.0):
    tt = t                                   # moment del cicle de l'animació (0..1)
    ph = 2 * math.pi * tt
    # ─── Sostre: planxes, i la biga d'acer de la fàbrica (encara hi és) ────
    cv.rect(0, 0, W - 1, 16, PANEL, lambda x, y: 0.4 + (0.6 if x % 53 == 1 else 0) - (0.2 if x % 53 == 2 else 0), 0.4)
    beam = [3.6, 3.2, 3.0, 2.2, 1.8, 1.8, 1.8, 1.6, 1.4, 1.0, 0.6]
    cv.rect(0, 17, W - 1, 27, PANEL, lambda x, y: beam[y - 17] + (hr(x // 4, y, 2) - 0.5) * 0.4)
    for x in range(5, W, 13):
        cv.put(x, 19, PANEL, 4.4)
        cv.put(x + 1, 20, PANEL, 1.6)
        cv.put(x, 25, RUST, 2.0)
    for x in range(W):                                            # rovell que surt per sota la pintura
        if hr(x // 5, 77) > 0.7:
            cv.put(x, 24 + (x % 2), RUST, 2.2)
            if hr(x, 78) > 0.6:
                cv.put(x, 26, RUST, 1.6)

    # ─── Paret: planxes de la presó ────────────────────────────────────────
    wall_panels(cv, 0, W - 1, 32, FLOOR_Y - 1)
    cv.darken(0, 32, W - 1, 40, lambda x, y: (41 - y) / 8)
    # safata de cables penjada de la biga
    cv.rect(0, 28, W - 1, 31, STEEL, lambda x, y: 2.8 - (y - 28) * 0.6)
    for x in range(0, W):
        if hr(x // 8, 4) > 0.5:
            cv.put(x, 32, [(20, 20, 26), (40, 30, 40), (70, 40, 50)], 1.0 + (x % 4 == 0))
        if hr(x // 11, 5) > 0.7:
            cv.put(x, 33, [(20, 20, 26), (30, 40, 30), (50, 70, 50)], 1.0 + (x % 3 == 0))
    # una planxa que falta: a sota, el maó de la fàbrica
    bricks(cv, 163, 43, 193, 83, base=1.4, seed=7)
    for y in range(43, 84):                                       # vora estripada
        for x in (162, 194):
            cv.put(x, y, PANEL, 0.4 if x == 162 else 3.0)
        if hr(y // 3, 79) > 0.6:
            cv.put(195, y, PANEL, 2.2)
    for x in range(162, 195):
        cv.put(x, 42, PANEL, 0.4)
        cv.put(x, 84, PANEL, 3.2)
        if hr(x // 3, 80) > 0.6:
            cv.put(x, 85, PANEL, 2.4)
    cv.darken(163, 43, 193, 48, lambda x, y: 0.6)
    # sòcol d'acer
    cv.rect(0, FLOOR_Y - 7, W - 1, FLOOR_Y - 1, STEEL, lambda x, y: 1.6 + (1.2 if y == FLOOR_Y - 7 else 0)
            - (0.6 if x % 53 == 0 else 0))

    # ─── Terra ────────────────────────────────────────────────────────────
    floor_deck(cv)
    # línia groga de seguretat davant la comporta
    for y in _ys(cv, 208, 213):
        for x in _xs(cv, 283, W - 1):
            yel = ((x - y) // 8) % 2 == 0
            cv.put(x, y, WARN if yel else STEEL, (3.0 if yel else 0.6) - (213 - y) * 0.08
                   - (0.8 if yel and hr(x // 3, y, 15) > 0.88 else 0))
    # reixes de desguàs (les de la fàbrica, envellides): la 1a és la sortida del conducte; la 2a, la del pilar 7
    for xa, xb in ((16, 54), (118, 156), (214, 252), (296, 334)):
        grate(cv, round(xa * 640 / 352), round(xb * 640 / 352), aged=True)

    # ─── Porta del passadís (11..85 × 59..203) ────────────────────────────
    cv.rect(11, 59, 85, FLOOR_Y - 1, STEEL, lambda x, y: 1.4 + (1.6 if x == 12 or y == 60 else 0) - (0.8 if x == 84 else 0))
    for y in _ys(cv, 67, FLOOR_Y - 2):
        for x in _xs(cv, 19, 78):
            u = (x - 19) / 59
            lvl = 3.2 - u * 1.4 + (0.6 if x in (20, 21) else 0) - (0.9 if x == 48 else 0) + (0.4 if x == 49 else 0)
            lvl += (hr(x // 2, y // 3, 16) - 0.5) * 0.15
            cv.put(x, y, STEEL, lvl)
    for y in range(69, 77):                                       # franges al capdamunt
        for x in range(19, 79):
            yel = ((x + y) // 5) % 2 == 0
            cv.put(x, y, WARN if yel else STEEL, (3.4 if yel else 0.8) - (0.6 if y == 76 else 0))
    for x0_ in (29, 59):                                          # finestretes
        cv.rect(x0_, 88, x0_ + 9, 107, STEEL, 0.6)
        cv.rect(x0_ + 1, 89, x0_ + 8, 106, TEAL, lambda x, y: 1.0 + (y - 89) * 0.04, 0.2)
        cv.put(x0_ + 2, 90, CYAN, 3.0, 0)
        cv.put(x0_ + 3, 91, CYAN, 2.4, 0)
        cv.hline(x0_, x0_ + 9, 108, STEEL, 3.6)
    # panell de la porta amb el pilot cian
    cv.rect(88, 117, 97, 139, STEEL, lambda x, y: 2.6 - (x - 88) * 0.12 + (0.8 if y == 117 else 0))
    cv.rect(90, 121, 95, 126, STEEL, 0.6)
    cv.rect(91, 122, 94, 125, CYAN, 4.0, 0)
    cv.put(91, 122, CYAN, 5.0, 0)
    for k in range(3):
        cv.hline(91, 94, 130 + k * 3, STEEL, 4.0)
        cv.hline(91, 94, 131 + k * 3, STEEL, 1.0)
    cv.glow(92, 123, 19, (110, 220, 255), 0.4)
    text(cv, 27, 61, 'C', WARN, 3.0, 0.3)

    # ─── Cartell del somriure (decoració de la presó) ─────────────────────
    cv.rect(109, 67, 141, 109, PAPER, lambda x, y: 3.4 - (y - 67) * 0.015 + (hr(x // 3, y // 3, 17) - 0.5) * 0.2, 0.6)
    cv.disc(125, 84, 11, 11, WARN, lambda nx, ny: 3.8 - ny * 0.6 - nx * 0.2, 0.4)
    for ex in (121, 129):
        cv.rect(ex, 80, ex + 1, 82, SIL, 0.4, 0)
    for i in range(-6, 7):                                        # el somriure
        cv.put(125 + i, 88 + round(math.sqrt(max(0, 36 - i * i)) * 0.45) - 1, SIL, 0.4, 0)
    cv.put(118, 86, SIL, 0.4, 0); cv.put(132, 86, SIL, 0.4, 0)
    text(cv, 111, 98, 'SOMRIU', [(140, 40, 60), (180, 60, 80)], 0.6, 0)
    cv.put(111, 68, GRAY, 1.0); cv.put(139, 68, GRAY, 1.0)
    cv.darken(137, 101, 141, 109, lambda x, y: 0.4)                # cantonada pelada
    for x in range(109, 142):
        cv.put(x, 110, PANEL, 0.6)                                 # ombra del cartell

    # ─── Escala cap al nivell de sota (102..183 × 134..208) ──────────────
    EX0, EX1, EY0 = 107, 176, 139
    cv.rect(EX0 - 5, EY0 - 5, EX1 + 5, FLOOR_Y - 1, STEEL, lambda x, y: 2.4 + (1.2 if y == EY0 - 5 else 0) - (0.6 if y == EY0 - 1 else 0))
    for x in range(EX0 - 5, EX1 + 6):                             # franges
        if ((x // 5) % 2) == 0:
            cv.put(x, EY0 - 2, WARN, 3.0)
            cv.put(x, EY0 - 3, WARN, 3.2)
            cv.put(x, EY0 - 4, WARN, 3.4)
    for y in _ys(cv, EY0, FLOOR_Y - 1):
        for x in _xs(cv, EX0, EX1):
            cv.put(x, y, SPACE, 1.4 - (y - EY0) * 0.015, 0)
    # reixa de l'arxiu al fons, amb la cadena i el rètol
    GX0, GX1, GY0, GY1 = 125, 157, 147, 179
    for y in range(GY0, GY1 + 1):
        for x in range(GX0, GX1 + 1):
            if (x - GX0) % 5 == 0 or y in (GY0, GY1):
                cv.put(x, y, STEEL, 2.6 + (0.6 if y == GY0 else 0), 0.4)
            elif (x - GX0) % 5 == 1:
                cv.put(x, y, STEEL, 1.2, 0.4)
    cv.rect(128, 149, 154, 157, MANILA, 3.0, 0.4)
    cv.hline(128, 154, 157, MANILA, 1.8, 0.4)
    text(cv, 130, 150, 'ARXIU', [(30, 24, 20), (40, 30, 24)], 0.4, 0)
    for i in range(24):                                            # cadena
        x = 128 + i
        y = 163 + round(math.sin(i / 23 * math.pi) * 4)
        cv.put(x, y, IRON, 3.6 if i % 2 else 2.0, 0.4)
        if i % 2 == 0:
            cv.put(x, y - 1, IRON, 2.8, 0.4)
    cv.rect(139, 165, 144, 171, GOLD, lambda x, y: 2.8 - (y - 165) * 0.15, 0.4)   # cadenat
    cv.rect(140, 162, 143, 164, IRON, 3.0, 0.4)
    cv.put(141, 163, SIL, 0.2, 0)
    cv.put(141, 168, SIL, 0.4, 0)
    # graons que baixen
    for i, y in enumerate((200, 195, 189, 185, 181)):
        inset = i * 4
        cv.hline(EX0 + inset, EX1 - inset, y, STEEL, 3.6 - i * 0.5)
        cv.hline(EX0 + inset, EX1 - inset, y + 1, STEEL, 2.4 - i * 0.4)
        cv.hline(EX0 + inset, EX1 - inset, y + 2, STEEL, 1.2 - i * 0.3)
    # baranes
    for s in (-1, 1):
        bx = EX0 + 3 if s < 0 else EX1 - 3
        cv.line(bx, 149, bx - s * 13, 200, STEEL, 4.2)
        cv.line(bx + 1, 149, bx + 1 - s * 13, 200, STEEL, 2.8)
        cv.vline(bx, 149, 200, STEEL, 2.6)
    cv.glow(141, 173, 24, (80, 120, 140), 0.12)

    # ─── Conducte (rovellat): de dalt fins a terra i cap a la comporta ────
    pipe(cv, aged=True, x=PIPE_X, w=PIPE_W, run_y=35, y_end=FLOOR_Y - 1)
    LV = [1.6, 3.0, 3.8, 3.4, 3.0, 2.6, 2.2, 1.8, 1.4, 1.0, 0.6]
    for yy in _ys(cv, 187, 201):                                  # tram cap a la llançadora
        lv = _interp(LV, (yy - 187) / 14)
        for xx in _xs(cv, PIPE_X + 14, 287):                       # passa per darrere el pilar
            cv.put(xx, yy, RUST, lv + (hr(xx // 3, yy) - 0.5) * 0.5)
    cv.rect(228, 186, 231, 202, RUST, lambda a, b: 3.2 - (b - 186) * 0.12)      # una brida, a l'ombra del pilar

    # ─── Pilar 7: el de la fàbrica, envellit ──────────────────────────────
    pillar(cv, PILAR_CX, 28, FLOOR_Y - 1, aged=True)
    # abraçadora de la presó amb un feix de cables
    for y in range(48, 55):
        for x in range(PILAR_CX - 12, PILAR_CX + 13):
            cv.put(x, y, STEEL, 3.0 - (x - PILAR_CX) * 0.11 + (1 if y == 48 else 0) - (1 if y == 54 else 0))
    cv.put(PILAR_CX - 9, 51, STEEL, 5.0); cv.put(PILAR_CX + 9, 51, STEEL, 3.0)
    cv.darken(PILAR_CX - 19, FLOOR_Y, PILAR_CX + 19, FLOOR_Y + 5, lambda x, y: 0.8 - abs(x - PILAR_CX) / 26)

    # ─── La comporta, tancada i rovellada (285..635 × 36..200) ────────────
    comporta(cv)

    # ─── Caixa de recanvis (545..601 × 201..232) ──────────────────────────
    cv.darken(544, 224, 603, 232, lambda x, y: 0.8)
    for y in range(205, 229):
        for x in range(549, 598):
            lvl = 2.6 + (hr(x // 7, 9) - 0.5) * 0.4 - (0.6 if (y - 205) % 8 == 7 else 0) + (0.2 if (y - 205) % 8 == 0 else 0)
            if y < 209:
                lvl = 3.6 - (y - 205) * 0.2                        # tapa
            if x in (549, 597):
                lvl = 1.4 if x == 597 else 3.4
            cv.put(x, y, WALNUT, lvl)
    cv.hline(549, 597, 209, WALNUT, 0.8)
    cv.rect(560, 212, 588, 220, MANILA, 2.2)
    cv.hline(560, 588, 220, MANILA, 1.2)
    text(cv, 562, 213, 'RECAN', [(40, 30, 24), (60, 44, 30)], 0.4, 0)
    for x, y in ((553, 221), (592, 212), (577, 224), (555, 211)):
        cv.put(x, y, RUST, 3.0)
        cv.put(x + 1, y + 1, RUST, 1.8)
    cv.rect(547, 223, 552, 227, STEEL, lambda x, y: 2.8 - (y - 223) * 0.3)    # un cargol caigut
    cv.put(548, 223, STEEL, 4.4)

    # ─── Fluorescents i balisa ────────────────────────────────────────────
    lamps(cv, tt=tt)
    # balisa: gira (tres voltes per cicle); quan el feix mira cap a nosaltres, la cúpula i l'halo s'encenen
    a = ph * 3
    s, face = math.sin(a) * 0.9, (1 + math.cos(a)) / 2
    cv.rect(289, 31, 303, 35, STEEL, lambda x, y: 2.8 - (y - 31) * 0.3)
    cv.hline(289, 303, 31, STEEL, 4.0)
    cv.disc(296, 27, 5.3, 5.3, ORANGE, lambda nx, ny: 5.0 - ny - abs(nx - s) - 1.6 * (1 - face), 0)
    for gx in (293, 296, 299):                                    # la gàbia de la cúpula
        cv.vline(gx, 22, 30, STEEL, 2.2 + (0.8 if gx == 293 else 0))
    cv.glow(296, 29, 35, (255, 150, 60), 0.45 * (0.55 + 0.45 * max(0.0, math.cos(a)) ** 2))

    # tint fred general i una mica de calor de la balisa a la comporta
    cv.tint(0, 0, W - 1, H - 1, (40, 70, 110), 0.10)
    cv.tint(189, 0, 403, 136, (255, 140, 60), lambda x, y: max(0, 0.16 * (1 - math.hypot(x - 296, y - 29) / 107)))
    # el feix de la balisa escombra la biga i el capdamunt de la comporta quan mira de costat
    w = 0.2 * math.sin(a) ** 2
    if w > 0.004:
        bx = 296 + 173 * math.sin(a)
        cv.tint(bx - 61, 8, bx + 61, 85, (255, 150, 60),
                lambda x, y: w * max(0.0, 1 - math.hypot((x - bx) / 61, (y - 32) / 45)))
    drips(cv, tt)


def drips(cv, tt):
    """Gotes que regalimen de la brida del conducte (x = 102) i esclaten a la vora de l'escala."""
    DX, Y0, Y1 = 102, 48, 133
    for start in (0.0, 0.48):
        u = (tt - start) % 1
        if u < 0.28:                                             # la gota s'infla, penjada de la brida
            if u > 0.08:
                cv.put(DX, Y0, WATER, 5.4, 0)
            if u > 0.14:
                cv.put(DX, Y0 + 1, WATER, 6.0, 0)
            if u > 0.20:
                cv.put(DX, Y0 + 2, WATER, 6.6, 0)
                cv.put(DX + 1, Y0 + 1, WATER, 4.6, 0)
        elif u < 0.43:                                           # cau (accelerant)
            k = (u - 0.28) / 0.15
            y = round(Y0 + 2 + k * k * (Y1 - Y0 - 2))
            cv.put(DX, y, WATER, 7.0, 0)
            cv.put(DX, y - 1, WATER, 5.8, 0)
            if k > 0.4:
                for j in range(2, 6):
                    cv.put(DX, y - j, WATER, 5.0 - j * 0.4, 0)
        elif u < 0.51:                                           # esquitx
            k = (u - 0.43) / 0.08
            r = 1 + round(k * 3)
            for dx, dy in ((-r, -1), (r, -1), (-r - 1, 0), (r + 1, 0), (-r // 2, -2), (r // 2 + 1, -2)):
                cv.put(DX + dx, Y1 + dy - (1 if k < 0.5 else 0), WATER, 6.6 - k * 1.6, 0)


def lamps(cv, only=LAMPS, tt=0.0):
    for lx in only:
        # el fluorescent esquerre fa figa de tant en tant (dos fotogrames, amb un d'encès al mig)
        dim = 0.0
        if lx == LAMPS[0] and (0.62 <= tt < 0.66 or 0.70 <= tt < 0.74):
            dim = 1.0 if tt < 0.66 else 0.6
        cv.vline(lx - 21, 32, 40, STEEL, 2.0)
        cv.vline(lx + 21, 32, 40, STEEL, 2.0)
        cv.rect(lx - 27, 40, lx + 27, 43, STEEL, lambda x, y: 3.4 - (y - 40) * 0.6)
        for ex in (lx - 26, lx + 26):                              # portalàmpades
            cv.rect(ex - 1, 44, ex + 1, 46, STEEL, 2.4)
        if dim:
            cv.hline(lx - 24, lx + 24, 44, CYAN, 4.4 - dim * 2.6, 0)
            cv.hline(lx - 24, lx + 24, 45, CYAN, 3.6 - dim * 2.2, 0)
            cv.hline(lx - 24, lx + 24, 46, CYAN, 3.0 - dim * 2.0, 0)
        else:
            cv.hline(lx - 24, lx + 24, 44, [(230, 244, 255)], 0, 0)
            cv.hline(lx - 24, lx + 24, 45, [(230, 244, 255)], 0, 0)
            cv.hline(lx - 24, lx + 24, 46, CYAN, 4.4, 0)
        cv.glow(lx, 48, 45, (210, 236, 255), 0.35 * (1 - dim * 0.75))


def comporta(cv):
    X0, Y0, X1, Y1 = COMPORTA
    # marc
    cv.rect(X0 - 3, Y0 - 3, X0 + 4, Y1, STEEL, lambda x, y: [1.0, 3.8, 3.4, 2.8, 2.4, 2.0, 1.4, 0.8][x - X0 + 3])
    cv.rect(X1 - 4, Y0 - 3, X1 + 3, Y1, STEEL, lambda x, y: [1.0, 2.6, 2.2, 2.0, 1.6, 1.2, 0.8, 0.6][x - X1 + 4])
    cv.rect(X0 - 3, Y0 - 3, X1 + 3, Y0 + 3, STEEL, lambda x, y: 3.2 - (y - Y0 + 3) * 0.4)
    for y in range(Y0 + 10, Y1, 21):
        cv.put(X0 - 1, y, STEEL, 5.0)
    rnd = random.Random(62)
    stains = [(rnd.randint(X0 + 11, X1 - 11), rnd.randint(Y0 + 8, Y1 - 40), rnd.uniform(7, 16)) for _ in range(14)]
    K = [1.2, 0.9, 0.6, 0.4, 0.25, 0.15, 0.05, 0.0, -0.05, -0.1, -0.2, -0.3, -0.45, -0.7, -1.1, -1.8]
    for y in _ys(cv, Y0 + 4, Y1 - 9):
        k = (y - Y0 - 4) % 16
        for x in _xs(cv, X0 + 5, X1 - 5):
            lvl = 2.6 + K[k]
            lvl += (hr(x // 32, (y - Y0) // 16, 5) - 0.5) * 0.3 + (hr(x // 3, y // 2, 6) - 0.5) * 0.12
            if k == 1 and x % 21 == 8:
                cv.put(x, y, STEEL, lvl + 2.2)                    # reblons
                continue
            if k == 2 and x % 21 == 9:
                cv.put(x, y, STEEL, lvl - 0.8)
                continue
            # rovell: clapes suaus a les juntes
            r = 0.0
            for sx, sy, rr in stains:
                d = math.hypot(x - sx, (y - sy) * 1.6) / rr
                if d < 1:
                    r = max(r, 1 - d)
            n = hr(x // 2, y // 2, 9)
            if r * 0.8 + n * 0.35 > 0.55:
                cv.put(x, y, RUST, 1.0 + r * 1.4 + (0.8 if k < 3 else 0) - (0.8 if k > 12 else 0) + (0.4 if n > 0.9 else 0))
            else:
                cv.put(x, y, STEEL, lvl)
    # regalims que baixen pels cargols
    for x in range(X0 + 8, X1 - 5, 21):
        for row in range(0, (Y1 - Y0) // 16):
            if hr(x, row, 13) > 0.6:
                y0_ = Y0 + 6 + row * 16
                ln = 4 + int(hr(x, row, 14) * 12)
                for y in _ys(cv, y0_, min(y0_ + ln, Y1 - 11) - 1):
                    cv.put(x, y, RUST, 2.0 - (y - y0_) * 0.06)
                    if hr(x, y, 15) > 0.7:
                        cv.put(x + 1, y, RUST, 1.4 - (y - y0_) * 0.06)
    # franges de perill a baix
    for y in _ys(cv, Y1 - 8, Y1):
        for x in _xs(cv, X0 + 5, X1 - 5):
            yel = ((x + y) // 8) % 2 == 0
            cv.put(x, y, WARN if yel else STEEL, (3.0 if yel else 0.6) - (0.8 if hr(x // 3, y, 8) > 0.85 else 0)
                   + (0.4 if y == Y1 - 8 else 0))
    cv.hline(X0 + 5, X1 - 5, Y1 + 1, SIL, 0.0, 0)
    # rètol de plantilla
    text(cv, 507, 80, 'MOLL L-1', WARN, 2.2, 0.6)
    # encaix de la palanca, buit
    EX, EY0, EY1 = 301, 115, 184
    cv.rect(EX - 8, EY0, EX + 8, EY1, STEEL, lambda x, y: 3.4 - (x - EX + 8) * 0.16)
    cv.rect(EX - 4, EY0 + 3, EX + 4, EY1 - 3, SIL, 0.2, 0)
    cv.vline(EX - 4, EY0 + 3, EY1 - 3, SIL, 1.2, 0)
    cv.rect(EX - 9, EY0 - 3, EX + 9, EY0, STEEL, lambda x, y: 4.4 - (y - EY0 + 3) * 0.2)
    for yy in (EY0 + 11, EY1 - 11):
        cv.rect(EX - 11, yy, EX + 11, yy + 3, STEEL, lambda x, y: 3.4 - (y - yy) * 0.4)
        cv.put(EX - 9, yy + 1, STEEL, 5.0); cv.put(EX + 9, yy + 1, STEEL, 3.6)
    cv.darken(EX + 9, EY0, EX + 13, EY1, lambda x, y: 0.6)


# ─── Props ──────────────────────────────────────────────────────────────────

def p_llancadora(cv):
    """La comporta oberta (plegada a dalt) i, a la badia, la llançadora vella."""
    X0, Y0, X1, Y1 = COMPORTA
    # badia fosca
    for y in range(Y0 + 4, Y1 + 1):
        for x in range(X0 + 5, X1 - 4):
            if y > 187:
                cv.put(x, y, STEEL, 0.8 + (y - 187) * 0.09 - (0.6 if x % 19 == 0 else 0), 0.5)
            else:
                cv.put(x, y, STEEL, 0.5 + (0.4 if (x - X0) % 53 == 0 else 0) + (hr(x // 53, y // 44) - 0.5) * 0.3
                       + (0.3 if (y - Y0) % 44 == 1 else 0), 0.5)
    # porta exterior de la badia, al fons, amb una finestreta a l'espai
    cv.rect(523, 67, 616, 181, STEEL, lambda x, y: 1.4 + (0.8 if x == 523 or y == 67 else 0), 0.5)
    cv.vline(569, 69, 181, STEEL, 0.4, 0.5)
    cv.vline(570, 69, 181, STEEL, 1.8, 0.5)
    cv.rect(555, 80, 584, 101, SIL, 0.5, 0)
    for y in range(81, 101):
        for x in range(556, 584):
            cv.put(x, y, SPACE, 1.2 + (y - 81) * 0.06, 0)
    for x, y in ((560, 85), (575, 84), (568, 93), (580, 96), (559, 97), (571, 88)):
        cv.flat(x, y, (220, 226, 255))
    cv.flat(577, 91, (160, 170, 220))
    for y in range(160, 181):
        for x in range(525, 615):
            yel = ((x + y) // 7) % 2 == 0
            cv.put(x, y, WARN if yel else STEEL, (1.8 if yel else 0.4), 0.4)
    # comporta plegada a dalt
    KF = [1.2, 0.9, 0.6, 0.2, 0.0, -0.3, -0.8, -1.8]
    for y in range(Y0 + 4, Y0 + 29):
        k = (y - Y0 - 4) % 8
        for x in range(X0 + 5, X1 - 4):
            lvl = 2.6 + KF[k]
            if hr(x // 2, (y - Y0) // 2, 2) * 0.5 + hr(x // 31, 3) * 0.5 > 0.8:
                cv.put(x, y, RUST, 0.8 + lvl * 0.5)
            else:
                cv.put(x, y, STEEL, lvl)
    for y in range(Y0 + 29, Y0 + 36):
        for x in range(X0 + 5, X1 - 4):
            yel = ((x + y) // 8) % 2 == 0
            cv.put(x, y, WARN if yel else STEEL, 3.0 if yel else 0.6)
    cv.darken(X0 + 5, Y0 + 36, X1 - 5, Y0 + 45, lambda x, y: (Y0 + 46 - y) / 9)
    # pòrtic de manteniment i mànegues
    for gx in (320, 512):
        cv.rect(gx, 72, gx + 4, 197, STEEL, lambda x, y: 2.6 - (x - gx) * 0.3)
        for by in range(84, 197, 24):
            cv.put(gx + 1, by, STEEL, 4.4)
    cv.rect(320, 72, 516, 76, STEEL, lambda x, y: 3.0 - (y - 72) * 0.5)
    cv.line(333, 76, 349, 109, STEEL, 1.2)                          # teranyines
    cv.line(504, 76, 491, 107, STEEL, 1.2)
    cv.line(333, 84, 341, 76, STEEL, 1.0)
    for i in range(13):
        cv.put(325 + i * 2, 77 + i, DUST, 3.4)
    # la llançadora (vella, coberta de pols, amb tres forats)
    shuttle(cv, 333, 133, aged=True)
    # mànega del conducte fins a la llançadora
    for i in range(94):
        f = i / 93
        x = 291 + f * 146
        y = 195 + math.sin(f * math.pi) * 5
        cv.put(x, y, RUST, 2.8)
        cv.put(x, y + 1, RUST, 2.0)
        cv.put(x, y + 2, RUST, 1.0)
    cv.line(437, 195, 456, 149, RUST, 2.6)
    cv.line(438, 195, 457, 149, RUST, 1.4)
    # etiqueta al costat dels forats
    cv.rect(469, 157, 480, 164, PAPER, 3.6, 0.6)
    cv.hline(471, 478, 159, RUST, 1.4, 0.5)
    cv.hline(471, 476, 161, RUST, 1.4, 0.5)
    cv.line(470, 157, 466, 151, GRAY, 2.0, 0.5)
    # pols a l'aire, a la llum
    rnd = random.Random(3)
    for _ in range(71):
        x, y = rnd.randint(X0 + 13, X1 - 13), rnd.randint(80, 187)
        if cv.get(x, y)[3]:
            cv.put(x, y, DUST, 3.0)
    lamps(cv, only=(LAMPS[1],))                                   # el fluorescent penja per davant


def p_porta_llancadora(cv):
    """La porta de la llançadora oberta: la fulla girada i l'interior fosc."""
    x0, cy = 333, 133
    dx0, dx1, dy0, dy1 = x0 + 53, x0 + 77, cy - 23, cy + 25
    for y in range(dy0, dy1 + 1):
        for x in range(dx0, dx1 + 1):
            cv.put(x, y, SIL, 0.4 + (y - dy0) * 0.015, 0)
    # tauler de dins, amb dos pilots
    cv.rect(dx0 + 5, dy0 + 13, dx1 - 4, dy0 + 19, STEEL, 1.4, 0)
    cv.hline(dx0 + 5, dx1 - 4, dy0 + 13, STEEL, 2.2, 0)
    cv.put(dx0 + 8, dy0 + 15, CYAN, 3.6, 0)
    cv.put(dx0 + 8, dy0 + 16, CYAN, 3.0, 0)
    cv.put(dx0 + 13, dy0 + 15, ORANGE, 3.0, 0)
    for x in range(dx0 + 16, dx1 - 5, 2):
        cv.put(x, dy0 + 16, STEEL, 2.6, 0)
    cv.glow(dx0 + 11, dy0 + 16, 12, (100, 200, 255), 0.3)
    # seient
    cv.rect(dx0 + 7, dy1 - 13, dx1 - 5, dy1 - 9, WALNUT, lambda x, y: 1.8 - (y - dy1 + 13) * 0.15, 0.4)
    cv.rect(dx1 - 8, dy1 - 24, dx1 - 5, dy1 - 9, WALNUT, 1.2, 0.4)
    cv.vline(dx1 - 8, dy1 - 24, dy1 - 9, WALNUT, 1.8, 0.4)
    # fulla oberta, vista de cantell
    for y in range(dy0 - 1, dy1 + 2):
        for x in range(dx0 - 9, dx0):
            cv.put(x, y, GRAY, 2.0 + (dx0 - x) * 0.19 - (y - dy0) * 0.008)
    cv.vline(dx0 - 9, dy0 - 1, dy1 + 1, GRAY, 4.0)
    for hy in (dy0 + 8, dy1 - 10):
        cv.rect(dx0 - 3, hy, dx0 - 1, hy + 3, COPPER, 3.0)


def p_aigua(cv):
    """El moll inundat: aigua al terra (mig transparent), l'escala plena i el raig del conducte rebentat."""
    P = cv.P
    for y in range(FLOOR_Y + 1, H):
        tt = (y - FLOOR_Y) / 80
        for x in range(W):
            lvl = 2.2 + LIGHT(x, y) * 0.8 + math.sin(x / 9.3 + y * 0.98) * 0.35
            # reflexos dels fluorescents i de la balisa
            for lx, col in ((LAMPS[0], 1.6), (LAMPS[1], 1.6), (296, 1.0)):
                if abs(x - lx) < 24 - tt * 5 and (y + x // 7) % 4 == 0:
                    lvl += col * (1 - abs(x - lx) / 24)
            i = max(0, min(len(WATER) - 1, math.floor(lvl + B4[y & 3][x & 3] - 0.5)))
            a = 110 if i < 5 else 210
            P[x, y] = WATER[i] + (a,)
    # vora d'aigua a la paret
    for x in range(W):
        P[x, FLOOR_Y] = WATER[6] + (200,)
        if x % 3:
            P[x, FLOOR_Y - 1] = WATER[5] + (120,)
    # l'escala, plena fins dalt
    for y in range(141, FLOOR_Y):
        for x in range(107, 178):
            lvl = 1.4 + (y - 141) * 0.015 + (1.4 if y == 141 else 0) + (0.8 if (x + y * 3) % 14 == 0 else 0)
            cv.put(x, y, WATER, lvl, 0)
    # raig del conducte rebentat
    for i in range(35):
        f = i / 34
        for k in range(5):
            x = PIPE_X - 1 - f * 17 - k
            y = 165 + f * f * 37 + k * 2
            cv.put(x, y, WATER, 6.4 - k * 0.6, 0)
    for k in range(11):
        cv.put(PIPE_X - 2 - k % 4, 160 + k, WATER, 5.6, 0)
    cv.put(PIPE_X, 163, SIL, 0.0, 0)
    cv.put(PIPE_X, 164, SIL, 0.0, 0)
    # esquitxos on cau
    for dx in (-4, -2, -1, 2, 3, 5, 8):
        cv.put(PIPE_X - 21 + dx, 203 - abs(dx) // 2, WATER, 7, 0)
    cv.put(PIPE_X - 21, 200, WATER, 7, 0)
    cv.put(PIPE_X - 19, 199, WATER, 6.4, 0)


def p_caixa_flotant(cv):
    """Caixa de fusta que sura davant l'escala: «ARXIU · NIVELL -1»."""
    x0, x1, y0, y1 = 112, 157, 195, 217
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            lvl = 2.6 + (hr(x // 5, 3) - 0.5) * 0.4 - (0.6 if (y - y0) % 8 == 7 else 0)
            if y < y0 + 4:
                lvl = 3.6 - (y - y0) * 0.15
            if x in (x0, x1):
                lvl = 3.4 if x == x0 else 1.4
            cv.put(x, y, WALNUT, lvl)
    cv.rect(x0 + 5, y0 + 7, x1 - 5, y0 + 14, MANILA, 2.8)
    xe = text(cv, x0 + 7, y0 + 8, 'ARXIU', [(40, 30, 24), (60, 44, 30)], 0.4, 0)
    text(cv, xe + 3, y0 + 8, '-1', [(140, 30, 30)], 0, 0)
    # part de sota, dins l'aigua (enfosquida i tremolosa)
    for y in range(y1 + 1, y1 + 7):
        for x in range(x0, x1 + 1):
            if (x + y) % 2:
                cv.put(x + (1 if y % 2 else 0), y, WATER, 2.4 - (y - y1) * 0.1)
    for x in range(x0 - 5, x1 + 6):                                # onades al voltant
        if x % 3:
            cv.put(x, y1 + 1, WATER, 6.0)
        if x % 4 == 0:
            cv.put(x, y1 + 4, WATER, 5.0)
        if x % 5 == 2:
            cv.put(x, y1 + 6, WATER, 4.4)


def p_marca(cv):
    carved_mark(cv, PILAR_CX - 7, 107, aged=True)


def p_nota_caixa(cv):
    """Una nota perduda: un paper doblegat que surt d'entre la tapa i la caixa."""
    cv.rect(581, 201, 588, 205, PAPER, lambda x, y: 4.4 - (y - 201) * 0.35, 0.6)
    cv.put(588, 201, PAPER, 2.4, 0.6)
    cv.hline(583, 586, 203, PAPER, 2.6, 0.6)


PROPS = {
    'llancadora': p_llancadora,
    'porta_llancadora': p_porta_llancadora,
    'aigua': p_aigua,
    'caixa_flotant': p_caixa_flotant,
    'marca_pilar': p_marca,
    'caixa_recanvis': p_nota_caixa,
}


# ─── Animació de fons: la balisa gira, el fluorescent esquerre fa figa i regalima el conducte ─────
_ANIM_BOXES = [
    (55, 0, 535, 95),           # la balisa, el seu feix, i el fluorescent esquerre
    (92, 96, 112, 137),         # les gotes del conducte
]


@lru_cache(maxsize=None)
def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv.img


def _ambient_frames():
    return clip_frames(bg, LIGHT, 24, _ANIM_BOXES, base=_base())


ANIMS = {'ambient': {'frames': _ambient_frames, 'frameDuration': 120}}
