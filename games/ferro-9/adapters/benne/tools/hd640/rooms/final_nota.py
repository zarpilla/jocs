"""
Final «Correspondència», l'última imatge, a 640×360: la composició de hd/rooms/final_nota.py ×4/3, dibuixada de nou.
La cambra de ressonància vella, al present, de molt a prop. El Cargol l'ha reparada durant cent vint anys (cargols
nous, una bobina tornada a enrotllar, el formulari 27-B enganxat al muntant i les ratlles dels dies a la paret), i
torna a brillar amb la llum de fase. A dins, damunt les bobines, una nota plegada: «Hola, V.».
Llums: el camp violeta de la cambra (gairebé l'única) i la nota, que fa una llum blanca i càlida.
A 640, la lletra de la nota és més gran i més de mà, les plaques es llegeixen amb la lletra de 4×7 i les
bobines, els muntants rovellats i les ratlles de la paret tenen més gra.
"""
import math
from functools import lru_cache

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from hd.pix import Canvas, Light, B4, W, H, ramp, mix, GOLD, COPPER, RUST, BRICK, IRON, PAPER, STEEL, WARN, MANILA
from hd640.rooms.fabrica_cambra import FE9, FIELD, rivet, hr, frame_diff, Baked
from hd640.rooms.gavina_passadis import text, text_w

CX, CY = 320, 149                 # centre del camp
GX0, GX1, GY0, GY1 = 200, 440, 40, 285          # vidre
COILS = (253, 320, 387)
NOTE = (320, 277)                 # la nota, damunt l'anell de baix
GLOWV = (170, 130, 255)
PAPERW = ramp((70, 56, 80), (130, 112, 128), (186, 170, 170), (226, 214, 200), (246, 238, 222), (255, 252, 240), n=7)


def vnoise(x, y, cell, seed):
    """Soroll suau (0..1): valors aleatoris en una graella, interpolats."""
    gx, gy = x / cell, y / cell
    ix, iy = math.floor(gx), math.floor(gy)
    fx, fy = gx - ix, gy - iy
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a, b = hr(ix, iy, seed), hr(ix + 1, iy, seed)
    c, d = hr(ix, iy + 1, seed), hr(ix + 1, iy + 1, seed)
    return (a + (b - a) * fx) * (1 - fy) + (c + (d - c) * fx) * fy


def field_light(x, y):
    d = math.hypot((x - CX) / 1.15, (y - CY) * 0.8)
    return 3.2 * max(0.0, 1 - d / 333) ** 1.5


def note_light(x, y):
    d = math.hypot(x - NOTE[0], (y - NOTE[1]) * 1.3)
    return 1.6 * max(0.0, 1 - d / 93) ** 1.6


_LT = Light(ambient=-0.6, vignette=(120, 53), floor_fade=None)
_LT.add(field_light)
_LT.add(note_light)
LIGHT = Baked(_LT)                 # (calculada un sol cop per píxel: l'animació redibuixa la sala 24 vegades)


# ─── Parets: maó de la fàbrica i planxes de la presó, una damunt l'altra ────

def walls(cv):
    def brick(x, y):
        row = y // 9
        v = y % 9
        off = 10 if row % 2 else 0
        bx = (x + off) // 21
        u = (x + off) % 21
        if v == 8 or u == 20:
            return 0.6 + (0.3 if hr(x, y, 14) > 0.85 else 0)
        lvl = 1.6 + (hr(bx, row, 3) - 0.5) * 0.8
        if v == 0:
            lvl += 0.4
        if v == 7 or u == 19:
            lvl -= 0.25
        if hr(bx, row, 7) > 0.8:
            lvl -= 0.7
        return lvl + (hr(x, y, 15) - 0.5) * 0.35

    cv.rect(0, 0, W - 1, H - 1, BRICK, brick)
    # planxes d'acer de la presó, cargolades damunt del maó (dalt), amb regalims de rovell
    for x0, x1, y1 in ((0, 128, 93), (512, W - 1, 112)):
        for y in range(0, y1 + 1):
            for x in range(x0, x1 + 1):
                lvl = 2.0 - y / 187 + (hr(x // 53, 3) - 0.5) * 0.4 + (hr(x // 2, y // 3, 16) - 0.5) * 0.15
                if (x - x0) % 53 == 0:
                    lvl = 0.8
                elif (x - x0) % 53 == 1:
                    lvl += 0.8
                if y >= y1 - 1:
                    lvl = 0.6 if y == y1 else 3.4
                cv.put(x, y, STEEL, lvl)
        for x in range(x0 + 5, x1 - 2, 13):
            rivet(cv, x, y1 - 6, 2.0)
        for i in range(13):                                                 # regalims de rovell
            rx = x0 + int(hr(i, x0, 1) * (x1 - x0))
            ln = 11 + int(hr(i, x0, 2) * 40)
            for y in range(y1 - 2, y1 + ln):
                if hr(rx, y, 3) > 0.15:
                    cv.put(rx, y, RUST, 2.6 - (y - y1) / ln * 1.6)
                if y < y1 + ln // 3 and hr(rx + 1, y, 3) > 0.5:
                    cv.put(rx + 1, y, RUST, 1.8 - (y - y1) / ln * 1.6)
    # terra: coberta de la presó, fosca
    for y in range(317, H):
        for x in range(W):
            lvl = 1.4 + (0.6 if (x + (y - 317) * (x - 320) // 107) % 32 == 0 else 0) - (y - 317) / 53
            cv.put(x, y, STEEL, lvl)


def tallies(cv, x0, y0, rows, per_row, seed=0):
    """Les ratlles dels dies, gratades al maó: grups de cinc."""
    for r in range(rows):
        x = x0 + (r % 2) * 3
        y = y0 + r * 12
        for g in range(per_row):
            if hr(r, g, seed) > 0.93:
                x += 11
                continue
            fade = 0.6 + hr(r, g, 5) * 0.9                                 # les més velles, gairebé esborrades
            for k in range(4):
                xx = x + k * 3
                h = 7 + (hr(xx, r, 3) > 0.6)
                lean = hr(xx, r, 4) > 0.5
                for j in range(h):
                    cv.put(xx + (1 if lean and j < 3 else 0), y + j, PAPERW, fade + hr(xx, y + j) * 0.7)
            for j in range(11):                                             # la ratlla que travessa el grup
                cv.put(x - 1 + j * 1.25, y + 7 - j * 0.7, PAPERW, fade + 0.3)
            x += 15 + int(hr(r, g, 9) * 3)


# ─── La cambra ──────────────────────────────────────────────────────────────

# Lletra de mà de la nota (7 files; les minúscules només en fan quatre)
HAND = {'H': ['#..#', '#..#', '#..#', '####', '#..#', '#..#', '#..#'],
        'o': ['...', '...', '...', '.#.', '#.#', '#.#', '.#.'],
        'l': ['#.', '#.', '#.', '#.', '#.', '#.', '.#'],
        'a': ['...', '...', '...', '.##', '#.#', '#.#', '.##'],
        ',': ['..', '..', '..', '..', '..', '.#', '#.'],
        ' ': ['.', '.', '.', '.', '.', '.', '.'],
        'V': ['#...#', '#...#', '#...#', '#...#', '.#.#.', '.#.#.', '..#..'],
        '.': ['.', '.', '.', '.', '.', '.', '#'],
        'I': ['#', '#', '#', '#', '#', '#', '#'],
        '-': ['...', '...', '...', '###', '...', '...', '...']}
INK = (58, 38, 92)


def chamber(cv, t=0.0):
    TAU = 2 * math.pi
    # ─── interior: el camp ───────────────────────────────────────────────
    for y in range(GY0, GY1 + 1):
        for x in range(GX0, GX1 + 1):
            d = math.hypot((x - CX) / 1.2, (y - CY) * 0.75) / 147
            lvl = 4.6 - d * 3.6
            for j, gx in enumerate(((COILS[0] + COILS[1]) / 2, (COILS[1] + COILS[2]) / 2)):
                sg = 1 if j == 0 else -1                                 # els dos fils corren en sentits contraris
                w = (gx + math.sin(y / 9.33 + gx + sg * TAU * t) * 5.33
                     + math.sin(y / 3.07 + gx * 2 - sg * TAU * 3 * t) * 1.33)
                if abs(x - w) < 1.3 and GY0 + 19 < y < GY1 - 24:
                    # el fil crepita: polsos de llum que hi corren amunt i avall
                    lvl += 2.4 + 0.9 * max(0.0, math.sin(y / 14.7 - sg * TAU * 2 * t + j)) ** 3
                elif abs(x - w) < 6.7:
                    lvl += 0.8 * (1 - abs(x - w) / 6.7)
            # arcs fins de les vores de les bobines cap a fora
            lvl += 0.4 * (math.sin(x / 12.0 + y / 17.3 + TAU * t) * math.sin(y / 9.33 - x / 22.7 - TAU * 2 * t))
            cv.put(x, y, FIELD, lvl, 0)

    # anells de llautó que aguanten les bobines
    for yy in (53, 261):
        cv.rect(GX0 + 4, yy, GX1 - 4, yy + 7, GOLD, lambda x, y: 3.6 - (y - yy) * 0.38 - abs(x - CX) / 160
                - (0.5 if vnoise(x, y, 6, 31) > 0.72 else 0), 0.4)
        cv.hline(GX0 + 4, GX1 - 4, yy, GOLD, 5.4, 0.3)
        cv.hline(GX0 + 4, GX1 - 4, yy + 7, GOLD, 1.0, 0.3)
        for x in range(GX0 + 11, GX1 - 5, 19):
            cv.put(x, yy + 3, GOLD, 5.6, 0.3)
            cv.put(x + 1, yy + 3, GOLD, 4.4, 0.3)
            cv.put(x + 1, yy + 4, GOLD, 1.6, 0.3)
    # tres bobines
    for k, cx in enumerate(COILS):
        new = k == 2                                                     # la del Cargol, tornada a enrotllar
        for y in range(64, 259):
            for x in range(cx - 17, cx + 19):
                s = (x - cx) / 18
                band = (y - 64) % 28
                if band in (24, 25, 26, 27):                             # el ferro-9 nu entre enrotllaments
                    if abs(s) < 0.6:
                        cv.put(x, y, FE9, 5.4 - s * 2.6 - (1.4 if band == 27 else 0), 0.3)
                    continue
                if abs(s) > 0.88 and (x - cx) * (CX - cx + 0.1) >= 0 and band not in (0, 23):
                    cv.put(x, y, FIELD, 5.6, 0)                          # vora encesa pel camp
                    continue
                lv = 3.4 - s * 1.6 - s * s * 1.6 + (y % 2) * 0.5 - (1.0 if band in (0, 23) else 0)
                if not new:
                    lv -= 0.4
                    if hr(x // 3, y // 4, k) > 0.9:
                        lv -= 1.2                                        # coure vell, enfosquit
                    elif hr(x // 2, y // 3, k + 7) > 0.96:
                        cv.put(x, y, COPPER, 1.6, 0.4)                   # verdet i cremades
                        continue
                else:
                    lv += 0.4
                cv.put(x, y, COPPER, lv, 0.4)
        # caps de ferro-9 polit
        for yy in (61, 259):
            cv.rect(cx - 20, yy, cx + 20, yy + 3, FE9, lambda x, y: 5.6 - (x - cx) / 8.0 - (y - yy) * 0.45, 0.3)
        cv.rect(cx - 3, 45, cx + 1, 60, FE9, lambda x, y: 5.4 - (x - cx) * 0.5, 0.3)
        if new:
            # fil de coure nou que encara s'enrotlla fins al cap, i un lligam de filferro
            for i in range(13):
                cv.put(cx + 17 + (i % 2), 67 + i * 4, COPPER, 6.0, 0)
                cv.put(cx + 18 - (i % 2), 69 + i * 4, COPPER, 4.6, 0)
            for y in (147, 148, 149):
                cv.hline(cx - 17, cx + 17, y, IRON, 4.6 - (y - 147) * 1.4, 0.4)
            cv.put(cx + 18, 150, IRON, 4.0, 0.4); cv.put(cx + 19, 151, IRON, 3.0, 0.4)   # la cua del lligam
    # el camp, lluïssor entre les bobines
    for gx in ((COILS[0] + COILS[1]) / 2, (COILS[1] + COILS[2]) / 2):
        cv.glow(gx, 160, 45, (200, 170, 255), 0.5 + 0.1 * math.sin(TAU * (2 * t + gx / 53)))
    cv.glow(CX, CY, 160, (150, 110, 240), 0.35)

    # ─── la nota, plegada en tenda damunt la base, davant la bobina del mig ─
    nx, ny = NOTE
    pulse = math.sin(TAU * t)                                        # la nota fa llum, polsant a poc a poc
    cv.glow(nx, ny - 11, 80, (255, 236, 214), 0.5 + 0.12 * pulse)
    cv.darken(nx - 32, ny + 4, nx + 35, ny + 11, lambda x, y: 0.0 if x < nx - 27 else 0.8 - (y - ny - 4) / 8, dither=True)
    back = [(nx - 25, ny - 21), (nx + 27, ny - 27), (nx + 33, ny - 1), (nx - 19, ny + 4)]
    cv.poly(back, PAPERW, 2.4, 0.2)
    front = [(nx - 29, ny - 20), (nx + 24, ny - 25), (nx + 29, ny + 1), (nx - 25, ny + 8)]

    def face(x, y):
        return 5.0 - (y - ny + 25) / 40 + (hr(x // 2, y // 3, 17) - 0.5) * 0.25
    cv.poly(front, PAPERW, face, 0.15)
    cv.line(nx - 29, ny - 20, nx + 24, ny - 25, PAPERW, 6.6, 0)          # el plec, encès
    cv.line(nx - 28, ny - 19, nx + 23, ny - 24, PAPERW, 5.8, 0)
    cv.line(nx - 25, ny + 8, nx + 29, ny + 1, PAPERW, 3.4, 0)
    cv.line(nx + 24, ny - 25, nx + 29, ny + 1, PAPERW, 3.8, 0)
    cv.line(nx + 25, ny - 24, nx + 30, ny + 1, PAPERW, 2.8, 0)
    # «Hola, V.» a mà, i la I. a sota

    def write(s_, x0, y0):
        x = x0
        for ch in s_:
            g = HAND[ch]
            for j, row in enumerate(g):
                for i, c in enumerate(row):
                    if c == '#':
                        X = x + i
                        cv.flat(X, y0 + j - round((X - (nx - 29)) * 0.1), INK)
            x += len(g[0]) + 1
    write('Hola, V.', nx - 21, ny - 15)
    for k, (x0, ln) in enumerate(((nx - 21, 35), (nx - 21, 24))):                # unes ratlles més, petites
        for i in range(ln):
            X = x0 + i
            if hr(X, k, 21) > 0.25:
                cv.flat(X, ny - 4 + k * 5 - round((X - (nx - 29)) * 0.1) + (1 if hr(X, k, 22) > 0.8 else 0),
                        mix(INK, (200, 190, 200), 0.45))
    write('-I.', nx + 11, ny - 1)
    # halo i guspires al voltant de la nota
    cv.glow(nx, ny - 11, 37, (255, 250, 236), 0.3 + 0.1 * pulse)
    for i in range(29):
        a = hr(i, 1) * math.pi * 2
        r = 21 + hr(i, 2) * 53
        x, y = round(nx + math.cos(a) * r * 1.3), round(ny - 16 + math.sin(a) * r * 0.6)
        tw = 0.5 + 0.5 * math.sin(TAU * ((1 + i % 3) * t + hr(i, 4)))   # parpellegen
        if GX0 < x < GX1 and GY0 < y < GY1 and tw > 0.15:
            cv.flat(x, y, mix(cv.P[x, y], (255, 244, 255), 0.8 * tw))
            if hr(i, 3) > 0.6:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    cv.flat(x + dx, y + dy, mix(cv.P[x + dx, y + dy], (255, 236, 255), 0.35 * tw))
    # partícules del camp que pugen
    for i in range(80):
        f = (t * (1 + int(hr(i, 14) * 2)) + hr(i, 15)) % 1                # cada una puja un tros i s'esvaeix
        x = GX0 + 5 + int(hr(i, 11) * (GX1 - GX0 - 10)) + round(math.sin(TAU * f + i) * 2)
        y = GY0 + 5 + int(hr(i, 12) * (GY1 - GY0 - 10)) - round(f * (19 + hr(i, 16) * 21))
        a = math.sin(math.pi * f)
        if y < GY0 + 3 or a < 0.12:
            continue
        cv.flat(x, y, mix(cv.P[x, y], (230, 214, 255), 0.75 * a))
        if hr(i, 13) > 0.6:
            cv.flat(x, y + 1, mix(cv.P[x, y + 1], (200, 180, 255), 0.4 * a))

    # ─── el vidre: tint fred, reflexos en diagonal, cantell gruixut ─────
    cv.tint(GX0, GY0, GX1, GY1, (180, 200, 240), 0.05)

    def streak(x, y):
        u = x - GX0 + (y - GY0) * 0.55
        return 0.30 if 19 <= u <= 32 else (0.18 if 40 <= u <= 43 else (0.14 if 200 <= u <= 213 else 0.0))

    cv.tint(GX0, GY0, GX1, GY1, (236, 244, 255), streak)
    # una esquerda vella al vidre, segellada amb resina
    for i in range(35):
        x, y = GX1 - 40 + i, GY0 + 16 + int(i * 0.7 + math.sin(i / 2.67) * 2.67)
        cv.flat(x, y, mix(cv.P[x, y], (236, 230, 255), 0.6))
        if i % 9 == 4:
            cv.flat(x, y + 1, mix(cv.P[x, y + 1], (236, 230, 255), 0.35))
    cv.vline(GX0 + 1, GY0 + 3, GY1 - 3, PAPER, 4.4, 0)
    cv.vline(GX0 + 2, GY0 + 3, GY1 - 3, FE9, 4.0, 0)
    cv.vline(GX0 + 3, GY0 + 3, GY1 - 3, FE9, 3.0, 0)
    cv.hline(GX0 + 1, GX1 - 1, GY1, FE9, 3.6, 0)
    cv.hline(GX0, GX1, GY0 - 1, FE9, 1.4)

    # ─── muntants laterals de ferro, vells però apanyats ────────────────
    for x0, lit in ((GX0 - 35, True), (GX1 + 1, False)):
        for y in range(21, 304):
            for x in range(x0, x0 + 35):
                u = (x - x0) / 34
                lvl = (3.6 - u * 2.4) if lit else (2.6 - u * 1.4)
                if x == x0:
                    lvl = 0.8
                if x == x0 + 34:
                    lvl = 0.6 if lit else 3.2
                # rovell en clapes
                rr = vnoise(x, y, 12, 41) * 0.75 + vnoise(x, y, 4, 42) * 0.25
                if rr > 0.62 + B4[y & 3][x & 3] * 0.06:
                    cv.put(x, y, RUST, 1.4 + (rr - 0.62) * 9 + (lvl - 2.4) * 0.6)
                    continue
                cv.put(x, y, IRON, lvl + (hr(x // 2, y // 3, 43) - 0.5) * 0.2)
        sx = x0 + 31 if lit else x0 + 2
        cv.vline(sx, GY0, GY1, GOLD, 3.4)                               # ranura de llautó
        cv.vline(sx + (1 if lit else -1), GY0, GY1, GOLD, 1.8)
        for y in range(35, 301, 19):
            for rx in (x0 + 8, x0 + 23):
                if hr(rx, y, 5) > 0.55:                                  # cargols nous de trinca, del Cargol
                    cv.disc(rx, y, 2.7, 2.7, STEEL, lambda a, b: 7.0 - a * 1.5 - b * 1.5)
                    cv.put(rx - 1, y, STEEL, 2.0); cv.put(rx, y, STEEL, 2.0); cv.put(rx + 1, y, STEEL, 2.0)
                else:
                    rivet(cv, rx, y, 2.0)
    # el formulari 27-B, enganxat al muntant esquerre amb cinta
    fx, fy = GX0 - 32, 200
    cv.darken(fx + 3, fy + 3, fx + 29, fy + 40, 0.7)
    cv.rect(fx, fy, fx + 27, fy + 37, MANILA, lambda x, y: 3.6 - (y - fy) / 53 + (hr(x, y, 9) - 0.5) * 0.3, 0.6)
    text(cv, fx + 4, fy + 4, '27-B', IRON, 1.2, 0)
    for y in range(fy + 15, fy + 34, 4):
        cv.hline(fx + 4, fx + 4 + int(hr(y, 2) * 11) + 8, y, MANILA, 1.4, 0.4)
    cv.disc(fx + 19, fy + 29, 4.5, 4.5, [(120, 20, 24), (170, 40, 36), (210, 70, 56)],
            lambda a, b: 1.2 - (0.8 if 0.45 < a * a + b * b < 0.6 else 0), 0.3)   # el segell
    cv.rect(fx + 8, fy - 3, fx + 17, fy + 1, PAPERW, 4.0, 0.4)

    # ─── caixa superior i base ──────────────────────────────────────────
    cv.rect(GX0 - 40, 0, GX1 + 40, 37, IRON, lambda x, y: 2.6 - y * 0.03 + (0.3 if hr(x // 7, 1) > 0.8 else 0)
            + (hr(x // 2, y // 2, 44) - 0.5) * 0.15)
    cv.hline(GX0 - 40, GX1 + 40, 37, IRON, 0.4)
    cv.hline(GX0 - 40, GX1 + 40, 36, IRON, 3.4)
    for x in range(GX0 - 35, GX1 + 37, 13):
        rivet(cv, x, 30, 2.0)
    # la placa de llautó, vella i ratllada
    cv.rect(261, 8, 379, 24, GOLD, lambda x, y: 3.8 - (y - 8) * 0.09 - (0.7 if vnoise(x, y, 7, 5) > 0.7 else 0), 0.2)
    cv.hline(261, 379, 8, GOLD, 5.0, 0.2)
    cv.hline(261, 379, 24, GOLD, 1.0, 0.2)
    for i in range(6):                                                   # ratllades
        x = 266 + int(hr(i, 45) * 100)
        for j in range(8):
            cv.put(x + j, 10 + int(hr(i, 46) * 12) + j // 3, GOLD, 5.0, 0.2)
    s = 'ALDAIA · FERRO-9'
    text(cv, 320 - text_w(s) // 2, 12, s, GOLD, 0.6, 0)
    # cables que surten de la caixa, apedaçats amb cinta
    for x0, x1, lv in ((161, 67, 1.4), (165, 27, 1.0), (479, 573, 1.4), (475, 621, 1.0)):
        for i in range(80):
            u = i / 79
            x = round(x0 + (x1 - x0) * u)
            y = round(35 + math.sin(u * math.pi) * 24 + u * 40)
            cv.put(x, y - 1, IRON, lv + 2.4)
            cv.put(x, y, IRON, lv + 1.6)
            cv.put(x, y + 1, IRON, lv + 0.8)
            cv.put(x, y + 2, IRON, lv)
        mx = round(x0 + (x1 - x0) * 0.5)
        my = round(35 + 24 + 20)
        cv.rect(mx - 1, my - 4, mx + 3, my + 3, WARN, lambda x, y: 3.4 - (x - mx) * 0.4)    # cinta groga

    # base: plataforma amb franges de perill gastades
    cv.rect(GX0 - 45, 285, GX1 + 45, 318, IRON, lambda x, y: 2.2 - (y - 285) * 0.04)
    cv.hline(GX0 - 45, GX1 + 45, 285, IRON, 4.2)
    cv.hline(GX0 - 45, GX1 + 45, 286, IRON, 3.0)
    for y in range(295, 307):
        for x in range(GX0 - 40, GX1 + 40):
            yel = ((x + y) // 9) % 2 == 0
            worn = vnoise(x, y, 5, 7) > 0.68
            if yel and not worn:
                cv.put(x, y, WARN, 2.8 - (0.5 if hr(x, y, 47) > 0.9 else 0))
            else:
                cv.put(x, y, IRON, 1.0 + (0.6 if worn and yel else 0))
    cv.hline(GX0 - 40, GX1 + 40, 294, IRON, 0.6)
    cv.hline(GX0 - 40, GX1 + 40, 307, IRON, 3.0)
    for x in range(GX0 - 37, GX1 + 40, 19):
        rivet(cv, x, 311, 2.0)
    cv.darken(GX0 - 53, 320, GX1 + 53, 331, lambda x, y: 0.9 - (y - 320) / 11)
    # plaqueta nova, gravada a mà amb una llima
    s = 'REPARADA PER CARGOL'
    tw = text_w(s)
    px0, px1 = 320 - tw // 2 - 7, 320 + (tw + 1) // 2 + 6
    cv.rect(px0, 292, px1, 308, STEEL, lambda x, y: 5.0 - (y - 292) * 0.11 + (hr(x, y, 48) - 0.5) * 0.3, 0.5)
    cv.hline(px0, px1, 292, STEEL, 7.4, 0.5)
    cv.hline(px0, px1, 308, STEEL, 2.4, 0.5)
    cv.vline(px1, 292, 308, STEEL, 3.0, 0.5)
    for x, y in ((px0 + 3, 295), (px1 - 3, 295), (px0 + 3, 305), (px1 - 3, 305)):
        cv.put(x, y, STEEL, 8.0, 0.5)
        cv.put(x + 1, y + 1, STEEL, 3.0, 0.5)
    text(cv, 320 - tw // 2, 297, s, STEEL, 1.0, 0)


def bg(cv, t=0.0):
    walls(cv)
    # ratlles dels dies a la paret de la dreta, i unes quantes a l'esquerra (cent vint anys no caben)
    tallies(cv, 512, 131, 12, 7, seed=1)
    tallies(cv, 8, 112, 14, 7, seed=2)
    chamber(cv, t)

    # ─── la llum de fase sobre el que hi ha al voltant ───────────────────
    cv.tint(0, 0, W - 1, H - 1, (130, 90, 220),
            lambda x, y: 0.30 * max(0.0, 1 - math.hypot((x - CX) / 400, (y - CY) / 267)) if not (GX0 <= x <= GX1 and GY0 <= y <= GY1) else 0)
    cv.tint(GX0 - 80, 285, GX1 + 80, H - 1, (255, 230, 200),
            lambda x, y: 0.16 * max(0.0, 1 - math.hypot((x - NOTE[0]) / 160, (y - 288) / 40)))
    # vinyeta forta: un pla íntim
    P = cv.P
    for y in range(H):
        for x in range(W):
            d = math.hypot((x - CX) / 387, (y - 173) / 253)
            k = max(0.0, d - 0.5) * 1.5
            if k > 0:
                o = P[x, y]
                f = max(0.0, 1 - k)
                P[x, y] = (int(o[0] * f), int(o[1] * f), int(o[2] * f), 255)


PROPS = {}


# ─── Animació de fons ──────────────────────────────────────────────────────
# El camp crepita i els dos fils d'energia s'ondulen en sentits contraris, les partícules pugen i
# s'esvaeixen, les guspires parpellegen i la nota fa llum polsant. Cada fotograma només té els píxels
# que canvien respecte del fons quiet (t = 0).

@lru_cache(maxsize=None)
def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv.img


def _ambient_frames(n=24):
    base = _base()
    frames = []
    for i in range(n):
        cv = Canvas(light=LIGHT)
        bg(cv, t=i / n)
        frames.append(frame_diff(base, cv.img))
    return frames


ANIMS = {'ambient': {'frames': _ambient_frames, 'frameDuration': 120}}
