"""
Final «Correspondència», l'última imatge: la cambra de ressonància vella, al present, de molt a prop. El Cargol
l'ha reparada durant cent vint anys (cargols nous, una bobina tornada a enrotllar, el formulari 27-B enganxat al
muntant i les ratlles dels dies a la paret), i torna a brillar amb la llum de fase. A dins, damunt les bobines,
una nota plegada: «Hola, V.».
Llums: el camp violeta de la cambra (gairebé l'única) i la nota, que fa una llum blanca i càlida.
"""
import math

from hd.pix import (Light, B4, W, H, hr, ramp, mix, GOLD, COPPER, RUST, BRICK, IRON, PAPER, STEEL, WARN, MANILA)
from hd.rooms.fabrica_cambra import FE9, FIELD, rivet
from hd.rooms.gavina_passadis import text, text_w

CX, CY = 240, 112                 # centre del camp
GX0, GX1, GY0, GY1 = 150, 330, 30, 214          # vidre
COILS = (190, 240, 290)
NOTE = (240, 208)                 # la nota, damunt l'anell de baix
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
    return 3.2 * max(0.0, 1 - d / 250) ** 1.5


def note_light(x, y):
    d = math.hypot(x - NOTE[0], (y - NOTE[1]) * 1.3)
    return 1.6 * max(0.0, 1 - d / 70) ** 1.6


LIGHT = Light(ambient=-0.6, vignette=(90, 40), floor_fade=None)
LIGHT.add(field_light)
LIGHT.add(note_light)


# ─── Parets: maó de la fàbrica i planxes de la presó, una damunt l'altra ────

def walls(cv):
    def brick(x, y):
        row = y // 7
        v = y % 7
        off = 8 if row % 2 else 0
        bx = (x + off) // 16
        u = (x + off) % 16
        if v == 6 or u == 15:
            return 0.6
        lvl = 1.6 + (hr(bx, row, 3) - 0.5) * 0.8
        if v == 0:
            lvl += 0.4
        if hr(bx, row, 7) > 0.8:
            lvl -= 0.7
        return lvl

    cv.rect(0, 0, W - 1, H - 1, BRICK, brick)
    # planxes d'acer de la presó, cargolades damunt del maó (dalt), amb regalims de rovell
    for x0, x1, y1 in ((0, 96, 70), (384, W - 1, 84)):
        for y in range(0, y1 + 1):
            for x in range(x0, x1 + 1):
                lvl = 2.0 - y / 140 + (hr(x // 40, 3) - 0.5) * 0.4
                if (x - x0) % 40 == 0:
                    lvl = 0.8
                elif (x - x0) % 40 == 1:
                    lvl += 0.8
                if y >= y1 - 1:
                    lvl = 0.6 if y == y1 else 3.4
                cv.put(x, y, STEEL, lvl)
        for x in range(x0 + 4, x1 - 2, 10):
            rivet(cv, x, y1 - 4, 2.0)
        for i in range(10):                                                 # regalims de rovell
            rx = x0 + int(hr(i, x0, 1) * (x1 - x0))
            ln = 8 + int(hr(i, x0, 2) * 30)
            for y in range(y1 - 2, y1 + ln):
                if hr(rx, y, 3) > 0.15:
                    cv.put(rx, y, RUST, 2.6 - (y - y1) / ln * 1.6)
    # terra: coberta de la presó, fosca
    for y in range(238, H):
        for x in range(W):
            lvl = 1.4 + (0.6 if (x + (y - 238) * (x - 240) // 80) % 24 == 0 else 0) - (y - 238) / 40
            cv.put(x, y, STEEL, lvl)


def tallies(cv, x0, y0, rows, per_row, seed=0):
    """Les ratlles dels dies, gratades al maó: grups de cinc."""
    for r in range(rows):
        x = x0 + (r % 2) * 2
        y = y0 + r * 9
        for g in range(per_row):
            if hr(r, g, seed) > 0.93:
                x += 8
                continue
            fade = 0.6 + hr(r, g, 5) * 0.9                                 # les més velles, gairebé esborrades
            for k in range(4):
                xx = x + k * 2
                h = 5 + (hr(xx, r, 3) > 0.6)
                lean = hr(xx, r, 4) > 0.5
                for j in range(h):
                    cv.put(xx + (1 if lean and j < 2 else 0), y + j, PAPERW, fade + hr(xx, y + j) * 0.7)
            for j in range(8):
                cv.put(x - 1 + j * 1.2, y + 5 - j * 0.7, PAPERW, fade + 0.3)
            x += 11 + int(hr(r, g, 9) * 2)


# ─── La cambra ──────────────────────────────────────────────────────────────

def chamber(cv):
    # ─── interior: el camp ───────────────────────────────────────────────
    for y in range(GY0, GY1 + 1):
        for x in range(GX0, GX1 + 1):
            d = math.hypot((x - CX) / 1.2, (y - CY) * 0.75) / 110
            lvl = 4.6 - d * 3.6
            for gx in ((COILS[0] + COILS[1]) / 2, (COILS[1] + COILS[2]) / 2):
                w = gx + math.sin(y / 7.0 + gx) * 4.0 + math.sin(y / 2.3 + gx * 2) * 1.0
                if abs(x - w) < 1.0 and GY0 + 14 < y < GY1 - 18:
                    lvl += 2.4
                elif abs(x - w) < 5:
                    lvl += 0.8 * (1 - abs(x - w) / 5)
            # arcs fins de les vores de les bobines cap a fora
            lvl += 0.4 * (math.sin(x / 9.0 + y / 13.0) * math.sin(y / 7.0 - x / 17.0))
            cv.put(x, y, FIELD, lvl, 0)

    # anells de llautó que aguanten les bobines
    for yy in (40, 196):
        cv.rect(GX0 + 3, yy, GX1 - 3, yy + 5, GOLD, lambda x, y: 3.6 - (y - yy) * 0.5 - abs(x - CX) / 120, 0.4)
        cv.hline(GX0 + 3, GX1 - 3, yy, GOLD, 5.4, 0.3)
        cv.hline(GX0 + 3, GX1 - 3, yy + 5, GOLD, 1.0, 0.3)
        for x in range(GX0 + 8, GX1 - 4, 14):
            cv.put(x, yy + 2, GOLD, 5.6, 0.3)
            cv.put(x + 1, yy + 3, GOLD, 1.6, 0.3)
    # tres bobines
    for k, cx in enumerate(COILS):
        new = k == 2                                                     # la del Cargol, tornada a enrotllar
        for y in range(48, 194):
            for x in range(cx - 13, cx + 14):
                s = (x - cx) / 13.5
                band = (y - 48) % 21
                if band in (18, 19, 20):                                 # el ferro-9 nu entre enrotllaments
                    if abs(s) < 0.6:
                        cv.put(x, y, FE9, 5.4 - s * 2.6 - (1.4 if band == 20 else 0), 0.3)
                    continue
                if abs(s) > 0.88 and (x - cx) * (CX - cx + 0.1) >= 0 and band not in (0, 17):
                    cv.put(x, y, FIELD, 5.6, 0)                          # vora encesa pel camp
                    continue
                lv = 3.4 - s * 1.6 - s * s * 1.6 + (y % 2) * 0.5 - (1.0 if band in (0, 17) else 0)
                if not new:
                    lv -= 0.4
                    if hr(x // 2, y // 3, k) > 0.9:
                        lv -= 1.2                                        # coure vell, enfosquit
                else:
                    lv += 0.4
                cv.put(x, y, COPPER, lv, 0.4)
        # caps de ferro-9 polit
        for yy in (46, 194):
            cv.rect(cx - 15, yy, cx + 15, yy + 2, FE9, lambda x, y: 5.6 - (x - cx) / 6.0 - (y - yy) * 0.6, 0.3)
        cv.rect(cx - 2, 34, cx + 1, 45, FE9, lambda x, y: 5.4 - (x - cx) * 0.7, 0.3)
        if new:
            # fil de coure nou que encara s'enrotlla fins al cap, i un lligam de filferro
            for i in range(10):
                cv.put(cx + 13 + (i % 2), 50 + i * 3, COPPER, 6.0, 0)
            for y in (110, 111):
                cv.hline(cx - 13, cx + 13, y, IRON, 4.6 - (y - 110) * 2, 0.4)
    # el camp, lluïssor entre les bobines
    for gx in ((COILS[0] + COILS[1]) / 2, (COILS[1] + COILS[2]) / 2):
        cv.glow(gx, 120, 34, (200, 170, 255), 0.5)
    cv.glow(CX, CY, 120, (150, 110, 240), 0.35)

    # ─── la nota, plegada en tenda damunt la base, davant la bobina del mig ─
    nx, ny = NOTE
    cv.glow(nx, ny - 8, 60, (255, 236, 214), 0.5)
    cv.darken(nx - 24, ny + 3, nx + 26, ny + 8, lambda x, y: 0.0 if x < nx - 20 else 0.8 - (y - ny - 3) / 6, dither=True)
    back = [(nx - 19, ny - 16), (nx + 20, ny - 20), (nx + 25, ny - 1), (nx - 14, ny + 3)]
    cv.poly(back, PAPERW, 2.4, 0.2)
    front = [(nx - 22, ny - 15), (nx + 18, ny - 19), (nx + 22, ny + 1), (nx - 19, ny + 6)]

    def face(x, y):
        return 5.0 - (y - ny + 19) / 30 + (hr(x // 2, y // 3, 17) - 0.5) * 0.25
    cv.poly(front, PAPERW, face, 0.15)
    cv.line(nx - 22, ny - 15, nx + 18, ny - 19, PAPERW, 6.6, 0)          # el plec, encès
    cv.line(nx - 21, ny - 14, nx + 17, ny - 18, PAPERW, 5.8, 0)
    cv.line(nx - 19, ny + 6, nx + 22, ny + 1, PAPERW, 3.4, 0)
    cv.line(nx + 18, ny - 19, nx + 22, ny + 1, PAPERW, 3.8, 0)
    # «Hola, V.» a mà, i la I. a sota
    G = {'H': ['#..#', '#..#', '####', '#..#', '#..#'], 'o': ['...', '...', '.#.', '#.#', '.#.'],
         'l': ['#.', '#.', '#.', '#.', '.#'], 'a': ['...', '...', '.##', '#.#', '.##'], ',': ['..', '..', '..', '.#', '#.'],
         ' ': ['.', '.', '.', '.', '.'], 'V': ['#.#', '#.#', '#.#', '#.#', '.#.'], '.': ['.', '.', '.', '.', '#'],
         'I': ['#', '#', '#', '#', '#'], '-': ['...', '...', '###', '...', '...']}
    INK = (58, 38, 92)

    def write(s_, x0, y0):
        x = x0
        for ch in s_:
            g = G[ch]
            for j, row in enumerate(g):
                for i, c in enumerate(row):
                    if c == '#':
                        X = x + i
                        cv.flat(X, y0 + j - round((X - (nx - 22)) * 0.1), INK)
            x += len(g[0]) + 1
    write('Hola, V.', nx - 16, ny - 11)
    for k, (x0, ln) in enumerate(((nx - 16, 26), (nx - 16, 18))):                # unes ratlles més, petites
        for i in range(ln):
            X = x0 + i
            if hr(X, k, 21) > 0.25:
                cv.flat(X, ny - 3 + k * 4 - round((X - (nx - 22)) * 0.1) + (1 if hr(X, k, 22) > 0.8 else 0),
                        mix(INK, (200, 190, 200), 0.45))
    write('-I.', nx + 8, ny + 1)
    # halo i guspires al voltant de la nota
    cv.glow(nx, ny - 8, 28, (255, 250, 236), 0.3)
    for i in range(22):
        a = hr(i, 1) * math.pi * 2
        r = 16 + hr(i, 2) * 40
        x, y = round(nx + math.cos(a) * r * 1.3), round(ny - 12 + math.sin(a) * r * 0.6)
        if GX0 < x < GX1 and GY0 < y < GY1:
            cv.flat(x, y, mix(cv.P[x, y], (255, 244, 255), 0.8))
            if hr(i, 3) > 0.6:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    cv.flat(x + dx, y + dy, mix(cv.P[x + dx, y + dy], (255, 236, 255), 0.35))
    # partícules del camp que pugen
    for i in range(60):
        x = GX0 + 4 + int(hr(i, 11) * (GX1 - GX0 - 8))
        y = GY0 + 4 + int(hr(i, 12) * (GY1 - GY0 - 8))
        c = cv.P[x, y]
        cv.flat(x, y, mix(c, (230, 214, 255), 0.6))
        if hr(i, 13) > 0.6:
            cv.flat(x, y + 1, mix(cv.P[x, y + 1], (200, 180, 255), 0.35))

    # ─── el vidre: tint fred, reflexos en diagonal, cantell gruixut ─────
    cv.tint(GX0, GY0, GX1, GY1, (180, 200, 240), 0.05)

    def streak(x, y):
        u = x - GX0 + (y - GY0) * 0.55
        return 0.30 if 14 <= u <= 24 else (0.18 if 30 <= u <= 32 else (0.14 if 150 <= u <= 160 else 0.0))

    cv.tint(GX0, GY0, GX1, GY1, (236, 244, 255), streak)
    # una esquerda vella al vidre, segellada amb resina
    for i in range(26):
        x, y = GX1 - 30 + i, GY0 + 12 + int(i * 0.7 + math.sin(i / 2.0) * 2)
        cv.flat(x, y, mix(cv.P[x, y], (236, 230, 255), 0.6))
    cv.vline(GX0 + 1, GY0 + 2, GY1 - 2, PAPER, 4.4, 0)
    cv.vline(GX0 + 2, GY0 + 2, GY1 - 2, FE9, 4.0, 0)
    cv.hline(GX0 + 1, GX1 - 1, GY1, FE9, 3.6, 0)
    cv.hline(GX0, GX1, GY0 - 1, FE9, 1.4)

    # ─── muntants laterals de ferro, vells però apanyats ────────────────
    for x0, lit in ((GX0 - 26, True), (GX1 + 1, False)):
        for y in range(16, 228):
            for x in range(x0, x0 + 26):
                u = (x - x0) / 25
                lvl = (3.6 - u * 2.4) if lit else (2.6 - u * 1.4)
                if x == x0:
                    lvl = 0.8
                if x == x0 + 25:
                    lvl = 0.6 if lit else 3.2
                # rovell en clapes
                rr = vnoise(x, y, 9, 41) * 0.75 + vnoise(x, y, 3, 42) * 0.25
                if rr > 0.62 + B4[y & 3][x & 3] * 0.06:
                    cv.put(x, y, RUST, 1.4 + (rr - 0.62) * 9 + (lvl - 2.4) * 0.6)
                    continue
                cv.put(x, y, IRON, lvl)
        sx = x0 + 23 if lit else x0 + 2
        cv.vline(sx, GY0, GY1, GOLD, 3.4)                               # ranura de llautó
        for y in range(26, 226, 14):
            for rx in (x0 + 6, x0 + 17):
                if hr(rx, y, 5) > 0.55:                                  # cargols nous de trinca, del Cargol
                    cv.disc(rx, y, 2.0, 2.0, STEEL, lambda a, b: 7.0 - a * 1.5 - b * 1.5)
                    cv.put(rx - 1, y, STEEL, 2.0); cv.put(rx + 1, y, STEEL, 2.0)
                else:
                    rivet(cv, rx, y, 2.0)
    # el formulari 27-B, enganxat al muntant esquerre amb cinta
    fx, fy = GX0 - 24, 150
    cv.darken(fx + 2, fy + 2, fx + 22, fy + 30, 0.7)
    cv.rect(fx, fy, fx + 20, fy + 28, MANILA, lambda x, y: 3.6 - (y - fy) / 40 + (hr(x, y, 9) - 0.5) * 0.3, 0.6)
    text(cv, fx + 3, fy + 3, '27-B', IRON, 1.2, 0)
    for y in range(fy + 11, fy + 26, 3):
        cv.hline(fx + 3, fx + 3 + int(hr(y, 2) * 8) + 6, y, MANILA, 1.4, 0.4)
    cv.disc(fx + 14, fy + 22, 3.4, 3.4, [(120, 20, 24), (170, 40, 36), (210, 70, 56)], 1.2, 0.3)   # el segell
    cv.rect(fx + 6, fy - 2, fx + 13, fy + 1, PAPERW, 4.0, 0.4)

    # ─── caixa superior i base ──────────────────────────────────────────
    cv.rect(GX0 - 30, 0, GX1 + 30, 28, IRON, lambda x, y: 2.6 - (y) * 0.04 + (0.3 if hr(x // 5, 1) > 0.8 else 0))
    cv.hline(GX0 - 30, GX1 + 30, 28, IRON, 0.4)
    cv.hline(GX0 - 30, GX1 + 30, 27, IRON, 3.4)
    for x in range(GX0 - 26, GX1 + 28, 10):
        rivet(cv, x, 23, 2.0)
    # la placa de llautó, vella i ratllada, i al costat una de nova gravada a mà
    cv.rect(196, 6, 284, 18, GOLD, lambda x, y: 3.8 - (y - 6) * 0.12 - (0.7 if vnoise(x, y, 5, 5) > 0.7 else 0), 0.2)
    cv.hline(196, 284, 6, GOLD, 5.0, 0.2)
    cv.hline(196, 284, 18, GOLD, 1.0, 0.2)
    t = 'ALDAIA · FERRO-9'
    text(cv, 240 - text_w(t) // 2, 9, t, GOLD, 0.6, 0)
    # cables que surten de la caixa, apedaçats amb cinta
    for x0, x1, lv in ((121, 50, 1.4), (124, 20, 1.0), (359, 430, 1.4), (356, 466, 1.0)):
        for i in range(60):
            t = i / 59
            x = round(x0 + (x1 - x0) * t)
            y = round(26 + math.sin(t * math.pi) * 18 + t * 30)
            cv.put(x, y - 1, IRON, lv + 2.4)
            cv.put(x, y, IRON, lv + 1.4)
            cv.put(x, y + 1, IRON, lv)
        mx = round(x0 + (x1 - x0) * 0.5)
        my = round(26 + 18 + 15)
        cv.rect(mx - 1, my - 3, mx + 2, my + 2, WARN, lambda x, y: 3.4 - (x - mx) * 0.5)    # cinta groga

    # base: plataforma amb franges de perill gastades
    cv.rect(GX0 - 34, 214, GX1 + 34, 239, IRON, lambda x, y: 2.2 - (y - 214) * 0.05)
    cv.hline(GX0 - 34, GX1 + 34, 214, IRON, 4.2)
    cv.hline(GX0 - 34, GX1 + 34, 215, IRON, 3.0)
    for y in range(221, 230):
        for x in range(GX0 - 30, GX1 + 30):
            yel = ((x + y) // 7) % 2 == 0
            worn = vnoise(x, y, 4, 7) > 0.68
            if yel and not worn:
                cv.put(x, y, WARN, 2.8)
            else:
                cv.put(x, y, IRON, 1.0 + (0.6 if worn and yel else 0))
    cv.hline(GX0 - 30, GX1 + 30, 220, IRON, 0.6)
    cv.hline(GX0 - 30, GX1 + 30, 230, IRON, 3.0)
    for x in range(GX0 - 28, GX1 + 30, 14):
        rivet(cv, x, 234, 2.0)
    cv.darken(GX0 - 40, 240, GX1 + 40, 248, lambda x, y: 0.9 - (y - 240) / 8)
    # plaqueta nova, gravada a mà amb una llima
    t = 'REPARADA PER CARGOL'
    tw = text_w(t)
    px0, px1 = 240 - tw // 2 - 5, 240 + (tw + 1) // 2 + 4
    cv.rect(px0, 219, px1, 231, STEEL, lambda x, y: 5.0 - (y - 219) * 0.15, 0.5)
    cv.hline(px0, px1, 219, STEEL, 7.4, 0.5)
    cv.hline(px0, px1, 231, STEEL, 2.4, 0.5)
    cv.vline(px1, 219, 231, STEEL, 3.0, 0.5)
    for x, y in ((px0 + 2, 221), (px1 - 2, 221), (px0 + 2, 229), (px1 - 2, 229)):
        cv.put(x, y, STEEL, 8.0, 0.5)
    text(cv, 240 - tw // 2, 223, t, STEEL, 1.0, 0)


def bg(cv):
    walls(cv)
    # ratlles dels dies a la paret de la dreta, i unes quantes a l'esquerra (cent vint anys no caben)
    tallies(cv, 384, 98, 12, 7, seed=1)
    tallies(cv, 6, 84, 14, 7, seed=2)
    chamber(cv)

    # ─── la llum de fase sobre el que hi ha al voltant ───────────────────
    cv.tint(0, 0, W - 1, H - 1, (130, 90, 220),
            lambda x, y: 0.30 * max(0.0, 1 - math.hypot((x - CX) / 300, (y - CY) / 200)) if not (GX0 <= x <= GX1 and GY0 <= y <= GY1) else 0)
    cv.tint(GX0 - 60, 214, GX1 + 60, H - 1, (255, 230, 200),
            lambda x, y: 0.16 * max(0.0, 1 - math.hypot((x - NOTE[0]) / 120, (y - 216) / 30)))
    # vinyeta forta: un pla íntim
    for y in range(H):
        for x in range(W):
            d = math.hypot((x - CX) / 290, (y - 130) / 190)
            k = max(0.0, d - 0.5) * 1.5
            if k > 0:
                o = cv.P[x, y]
                f = max(0.0, 1 - k)
                cv.P[x, y] = (int(o[0] * f), int(o[1] * f), int(o[2] * f), 255)


PROPS = {}
