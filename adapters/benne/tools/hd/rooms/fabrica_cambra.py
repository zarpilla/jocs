"""
Cambra de ressonància (Iri): un racó de maó i ferro al fons de la sala de calderes. La cambra de vidre gruixut
amb les bobines de ferro-9, la consola (palanca, rellotges, el llum d'alarma) i la reixa del conducte de servei.
Llums: làmpada industrial sobre la consola, una altra sobre la pissarra, la lluïssor violeta de la cambra i el
foc de les calderes que entra per l'espiell de la porta.

`bg(cv, alarm=True)` el fa servir el pròleg: làmpades apagades i el llum d'alarma encès (vegeu proleg_cambra).
"""
import math

from hd.pix import (Light, B4, W, H, hr, ramp, mix, R, WALNUT, GOLD, COPPER, RUST, BRICK, IRON, FIRE, RED, PAPER,
                    MANILA, GRAY, WARN, SIL)

# ─── Rampes pròpies ─────────────────────────────────────────────────────────
STONE = ramp((14, 10, 16), (34, 26, 30), (62, 48, 46), (96, 76, 64), (134, 108, 84), (174, 146, 110), (212, 188, 148), n=9)
FE9 = [(12, 14, 30), (24, 28, 54), (40, 48, 84), (64, 76, 116), (96, 112, 152), (138, 156, 194), (186, 204, 232), (232, 242, 255)]
FIELD = [(8, 6, 18), (18, 12, 36), (32, 20, 60), (52, 32, 92), (78, 50, 132), (112, 80, 180), (160, 130, 222), (214, 196, 250)]
SLATE = [(10, 12, 14), (18, 22, 24), (28, 34, 34), (40, 48, 46), (56, 64, 60)]
CHALK = [(70, 78, 74), (120, 128, 120), (176, 182, 170), (226, 228, 216)]
BULB = [(255, 236, 170)]
REDGL = [(40, 6, 8), (80, 12, 12), (130, 22, 18), (180, 40, 26), (230, 80, 50), (255, 150, 110), (255, 220, 190)]

FLOOR_Y = 154
LAMP1 = (134, 33)          # làmpada sobre la consola
LAMP2 = (430, 31)          # làmpada sobre la pissarra
CORE = (259, 84)           # centre de la cambra
BEACON = (102, 76)         # llum d'alarma de la consola


def make_light(alarm=False):
    lt = Light(vignette=(70, 40), floor_fade=(198, 34))
    if not alarm:
        lt.point(*LAMP1, r=150, k=2.5, squash=1.1, down=True)
        lt.point(*LAMP2, r=110, k=1.6, squash=1.1, down=True)
        lt.point(*CORE, r=110, k=1.3, squash=0.9)
        lt.point(32, 88, r=46, k=0.9)                                   # espiell de la porta
        lt.add(floor_pools)
    else:
        lt.ambient = -0.7
        lt.point(*BEACON, r=170, k=2.0, squash=1.0, power=1.5)
        lt.point(*CORE, r=80, k=0.6, squash=0.9)
    return lt


def floor_pools(x, y):
    """Taques de llum al terra sota les làmpades."""
    if y < 150:
        return 0.0
    v = 0.0
    for (lx, k, rx) in ((LAMP1[0], 1.8, 80), (LAMP2[0], 1.1, 56)):
        d = math.hypot((x - lx) / rx, (y - 168) / 22)
        if d < 1:
            v += (1 - d) ** 1.5 * k
    return v


LIGHT = make_light()


# ─── Ajudes ────────────────────────────────────────────────────────────────

def rivet(cv, x, y, base=2.6):
    cv.put(x, y, IRON, base + 1.6)
    cv.put(x + 1, y + 1, IRON, base - 1.4)


def thick(cv, x0, y0, x1, y1, w, rp, lvl):
    """Barra gruixuda: lvl(s) amb s = -1..1 a través del gruix."""
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    dx, dy = (x1 - x0) / n, (y1 - y0) / n
    nx, ny = -dy, dx
    for i in range(int(n * 2) + 1):
        t = i / 2
        cx, cy = x0 + dx * t, y0 + dy * t
        for k in range(-w * 2, w * 2 + 1):
            s = k / (w * 2) if w else 0
            cv.put(round(cx + nx * k / 2), round(cy + ny * k / 2), rp, lvl(s))


def contact_shadow(cv, x0, x1, y0, depth, fall=8):
    for y in range(y0, y0 + depth):
        for x in range(x0 - fall, x1 + fall):
            a = (1 - (y - y0) / depth) * (1 - max(0, max(x0 - x, x - x1)) / fall)
            if a > B4[y & 3][x & 3] and 0 <= x < W:
                o = cv.P[x, y]
                cv.P[x, y] = tuple(int(c * 0.55) for c in o[:3]) + (255,)


# ─── Fons ──────────────────────────────────────────────────────────────────

def bg(cv, alarm=False):
    # ─── Sostre: biga de ferro reblonada i canonada de coure ─────────────────
    cv.rect(0, 0, W - 1, 3, IRON, 0.4)
    cv.rect(0, 4, W - 1, 9, IRON, lambda x, y: 2.0 + (0.6 if y == 4 else 0) - (y - 4) * 0.15)
    cv.hline(0, W - 1, 10, IRON, 3.0)
    cv.hline(0, W - 1, 11, IRON, 0.6)
    for x in range(6, W, 16):
        rivet(cv, x, 6, 2.2)
    # canonada de coure horitzontal
    for y in range(13, 18):
        cv.hline(0, W - 1, y, COPPER, [1.6, 3.4, 3.0, 2.2, 0.8][y - 13])
    for x in range(30, W, 70):                                     # brides i abraçadores
        cv.rect(x, 12, x + 3, 18, COPPER, lambda xx, yy: 3.6 - (xx - x) * 0.5)
        cv.vline(x + 1, 10, 11, IRON, 1.6)

    # ─── Paret de maó (12..145) ───────────────────────────────────────────────
    def brick(x, y):
        row = (y - 19) // 6
        v = (y - 19) % 6
        off = 7 if row % 2 else 0
        bx = (x + off) // 14
        u = (x + off) % 14
        if v == 5 or u == 13:
            return 0.7                                             # morter
        lvl = 1.5 + (hr(bx, row, 3) - 0.5) * 0.7
        if v == 0:
            lvl += 0.4
        if v == 4 or u == 12:
            lvl -= 0.3
        if hr(bx, row, 7) > 0.85:                                  # maó socarrimat
            lvl -= 0.6
        lvl -= max(0, 1 - (y - 19) / 22) * 1.3                       # sutge de sota la canonada
        return lvl

    cv.rect(0, 18, W - 1, 145, BRICK, brick)
    cv.hline(0, W - 1, 18, BRICK, 0.2)
    # sòcol de pedra
    cv.hline(0, W - 1, 146, STONE, 4.0)
    cv.rect(0, 147, W - 1, 152, STONE, lambda x, y: 2.6 - (y - 147) * 0.2 + (hr(x // 22, 5) - 0.5) * 0.4
            - (0.8 if x % 22 == 0 else 0))
    cv.hline(0, W - 1, 153, STONE, 0.4)

    # ─── Terra de lloses de pedra en perspectiva ─────────────────────────────
    VPX, VPY = 240, -160
    for y in range(FLOOR_Y, H):
        dep = y - VPY
        t = 3800 / dep
        row = math.floor(t / 0.95)
        row_up = math.floor(3800 / (dep - 1) / 0.95)
        for x in range(W):
            u = (x - VPX) / dep * 30 / 3 + (0.5 if row % 2 else 0)
            col = math.floor(u)
            fr = (u - col) * dep / 10
            lvl = 2.0 + (hr(col, row, 1) - 0.5) * 0.6 + (hr(x // 3, y // 2, col) - 0.5) * 0.25
            if fr < 1 or row != row_up:
                lvl = 1.0
            elif fr < 2:
                lvl += 0.3
            if y < 162:
                lvl -= (162 - y) / 8 * 1.2                          # ombra de contacte amb la paret
            cv.put(x, y, STONE, lvl)

    # ─── Porta cap a la sala de calderes (8..57 × 65..155) ───────────────────
    cv.rect(6, 61, 59, 153, IRON, lambda x, y: 2.4 + (0.9 if x in (6, 7) or y in (61, 62) else 0) - (1.2 if x in (58, 59) else 0))
    cv.rect(11, 66, 54, 153, IRON, 0.3)
    for x in range(8, 58, 6):
        rivet(cv, x, 63, 2.4)
    for y in range(68, 152, 7):
        rivet(cv, 8, y, 2.4)
        rivet(cv, 56, y, 2.0)

    def door(x, y):
        lvl = 2.0 + (0.9 if x == 12 else 0) - (1.0 if x == 53 else 0)
        if y in (100, 124):
            lvl += 0.9
        if y in (101, 125):
            lvl -= 1.0
        if (x - 12) % 41 in (3, 38) and (y - 69) % 8 == 0:
            lvl += 1.6
        return lvl + (hr(x // 3, y // 5, 61) - 0.5) * 0.3

    cv.rect(12, 67, 53, 153, IRON, door)
    # rovell a la part baixa
    for y in range(136, 154):
        for x in range(12, 54):
            if hr(x // 2, y // 2, 62) < (y - 136) / 24 - 0.1:
                cv.put(x, y, RUST, 1.6 + hr(x // 2, y // 2) * 0.6)
    # espiell amb barrots: el foc de les calderes
    cv.rect(21, 76, 44, 95, IRON, 0.6)
    for y in range(78, 94):
        for x in range(23, 43):
            f = 1 - abs(x - 33) / 14 + (y - 78) / 16 * 0.6 + (hr(x // 2, y // 3, 5) - 0.5) * 0.6
            cv.put(x, y, FIRE, 1.4 + f * 2.2, 0)
    for x in (28, 33, 38):
        cv.vline(x, 78, 93, IRON, 1.4, 0)
        cv.vline(x + 1, 78, 93, IRON, 0.4, 0)
    cv.hline(21, 44, 76, IRON, 3.6)
    cv.hline(21, 44, 95, IRON, 0.8)
    cv.glow(33, 88, 26, (255, 150, 70), 0.0 if alarm else 0.35)
    # maneta de palanca i pany
    cv.rect(44, 108, 47, 120, IRON, lambda x, y: 3.2 - (x - 44) * 0.5)
    cv.rect(38, 111, 49, 113, IRON, lambda x, y: 4.0 - (y - 111) * 1.2)
    cv.disc(37, 112, 2, 2, IRON, lambda nx, ny: 4.2 - nx - ny)
    # frontissa
    for y in (74, 140):
        cv.rect(10, y, 15, y + 5, IRON, lambda x, yy: 3.4 - (yy - y) * 0.4)
    # rètol esmaltat sobre la porta
    cv.rect(16, 50, 49, 57, PAPER, lambda x, y: 3.6 - (y - 50) * 0.15)
    cv.hline(16, 49, 50, IRON, 1.2); cv.hline(16, 49, 57, IRON, 0.8)
    cv.vline(16, 50, 57, IRON, 1.2); cv.vline(49, 50, 57, IRON, 0.8)
    for x in range(19, 47):
        if (x - 19) % 4 != 3 and hr(x // 4, 2) > 0.15:
            cv.put(x, 53, IRON, 1.0)
            cv.put(x, 54, IRON, 1.0 if (x * 3) % 4 else 2.0)

    # ─── Pilars de ferro ─────────────────────────────────────────────────────
    for px in (64, 448):
        cv.rect(px, 12, px + 9, 153, IRON, lambda x, y: [1.2, 3.6, 3.0, 2.4, 2.2, 2.0, 1.8, 1.4, 0.8, 0.4][x - px])
        cv.rect(px - 2, 140, px + 11, 153, IRON, lambda x, y: 2.6 - (y - 140) * 0.1 - (x - px) * 0.08)
        cv.hline(px - 2, px + 11, 140, IRON, 3.8)
        for y in range(20, 138, 9):
            rivet(cv, px + 2, y, 2.6)
            rivet(cv, px + 6, y, 2.2)

    # ─── Avís de reglament, clavat al maó (75..90 × 62..84) ──────────────────
    cv.rect(77, 62, 91, 82, PAPER, lambda x, y: 3.2 - (y - 62) * 0.04 + (hr(x, y, 3) - 0.5) * 0.3)
    cv.rect(77, 62, 91, 64, PAPER, 4.0)
    for y in range(67, 81, 2):
        for x in range(79, 90):
            if hr(x // 2, y, 4) > 0.3:
                cv.put(x, y, SIL, 2.0)
    cv.put(84, 61, GOLD, 4.0)                                      # xinxeta
    cv.darken(92, 63, 92, 83, 0.6)
    cv.darken(78, 83, 92, 83, 0.6)

    # ─── Consola (90..181 × 84..153) ─────────────────────────────────────────
    CX0, CX1 = 89, 182
    contact_shadow(cv, CX0, CX1, FLOOR_Y, 9)
    # cos de fusta amb sòcol de ferro
    cv.rect(CX0, 104, CX1, 150, WALNUT, lambda x, y: 2.2 + (hr(x // 2, 7) - 0.5) * 0.3)
    cv.vline(CX0, 104, 150, WALNUT, 3.6)
    cv.vline(CX1, 104, 150, WALNUT, 0.8)
    cv.rect(CX0, 147, CX1, 153, IRON, lambda x, y: 1.8 - (y - 147) * 0.15)
    cv.hline(CX0, CX1, 147, IRON, 3.0)
    # tauler frontal de llautó negre amb rellotges
    cv.rect(CX0 + 4, 107, CX1 - 4, 140, IRON, lambda x, y: 1.4 + (hr(x // 4, y // 4, 8) - 0.5) * 0.15)
    cv.hline(CX0 + 4, CX1 - 4, 107, IRON, 0.4)
    cv.hline(CX0 + 4, CX1 - 4, 140, IRON, 2.6)
    for x, y in ((CX0 + 6, 109), (CX1 - 7, 109), (CX0 + 6, 138), (CX1 - 7, 138)):
        cv.put(x, y, GOLD, 4.0)

    def gauge(cx, cy, r, ang):
        cv.disc(cx, cy, r + 1.6, r + 1.6, GOLD, lambda nx, ny: 3.4 - nx * 1.2 - ny * 1.2)
        cv.disc(cx, cy, r, r, PAPER, lambda nx, ny: 3.8 - ny * 0.8 - nx * 0.3)
        for a in range(200, 341, 28):
            cv.put(round(cx + math.cos(math.radians(a)) * (r - 1)), round(cy + math.sin(math.radians(a)) * (r - 1)), SIL, 1.0)
        for i in range(int(r)):
            cv.flat(round(cx + math.cos(ang) * i), round(cy + math.sin(ang) * i), (150, 26, 24))
        cv.flat(round(cx), round(cy), (30, 24, 24))
        cv.put(round(cx - r * 0.4), round(cy - r * 0.5), PAPER, 6, 0)

    gauge(106, 120, 7, math.radians(-30))
    gauge(126, 120, 7, math.radians(-120))
    # fila de llums de senyal (vidres apagats)
    for i, (rp, lv) in enumerate(((FE9, 2.0), (WARN, 1.4), (FE9, 2.0), (WARN, 1.4))):
        x = 142 + i * 8
        cv.disc(x, 115, 2.2, 2.2, GOLD, 3.0)
        cv.disc(x, 115, 1.4, 1.4, rp, lambda nx, ny: lv + 1 - nx - ny)
    # interruptors de ganivet
    for i in range(3):
        x = 144 + i * 9
        cv.rect(x, 124, x + 4, 135, SIL, 1.2)
        cv.rect(x + 1, 126, x + 3, 127, COPPER, 3.4)
        cv.rect(x + 1, 132, x + 3, 133, COPPER, 3.0)
        cv.line(x + 2, 133, x + 2 + (2 if i != 1 else -1), 124, COPPER, 4.0)
        cv.put(x + 2 + (2 if i != 1 else -1), 123, SIL, 3.0)
    # reixeta de ventilació de la consola
    for x in range(97, 136, 3):
        cv.vline(x, 131, 137, IRON, 0.2)
        cv.vline(x + 1, 131, 137, IRON, 2.4)
    # placa de llautó
    cv.rect(112, 142, 158, 145, GOLD, lambda x, y: 3.6 - (y - 142) * 0.5)
    for x in range(115, 156, 2):
        if hr(x // 4, 9) > 0.2:
            cv.put(x, 143, GOLD, 1.2)
    # sobre inclinat (84..104): on hi ha el botó i la palanca
    for y in range(88, 104):
        t = (y - 88) / 15
        xl, xr = CX0 + 3 - t * 3, CX1 - 3 + t * 3
        for x in range(round(xl), round(xr) + 1):
            edge = x <= xl + 1 or x >= xr - 1
            cv.put(x, y, WALNUT, (3.6 if edge else 2.6) + t * 0.5 - (1.2 if x >= xr - 1 else 0))
    cv.rect(CX0 + 8, 90, CX1 - 22, 101, IRON, lambda x, y: 1.8 + (y - 90) * 0.06)   # placa de ferro del sobre
    cv.hline(CX0 + 8, CX1 - 22, 90, IRON, 0.6)
    cv.hline(CX0 + 8, CX1 - 22, 101, IRON, 3.0)
    for x, y in ((CX0 + 10, 92), (CX1 - 24, 92), (CX0 + 10, 99), (CX1 - 24, 99)):
        rivet(cv, x, y, 2.0)
    cv.rect(CX0, 102, CX1, 104, WALNUT, lambda x, y: [4.4, 3.4, 1.0][y - 102])
    # cables que surten de la consola cap a la cambra
    for i, (y0, lv) in enumerate(((128, 1.4), (134, 1.0), (140, 1.2))):
        pts = []
        for k in range(30):
            t = k / 29
            x = CX1 + t * (206 - CX1)
            y = y0 + (1 - t) * 0 + t * (150 - y0) + math.sin(t * math.pi) * (16 - i * 3)
            pts.append((x, y))
        for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
            cv.line(round(xa), round(ya), round(xb), round(yb), GRAY, lv + 0.6)
            cv.line(round(xa), round(ya) + 1, round(xb), round(yb) + 1, SIL, lv + 0.6)
            cv.line(round(xa), round(ya) + 2, round(xb), round(yb) + 2, SIL, 0.2)

    # ─── Base de la palanca (152..181 × 54..93): quadrant dentat i ranura ────
    # (el braç és un prop: palanca_alcada / palanca_baixada)
    cv.disc(166, 92, 11, 5, IRON, lambda nx, ny: 2.6 - ny * 1.2 - nx * 0.4)       # quadrant
    for a in range(200, 341, 20):
        cv.put(round(166 + math.cos(math.radians(a)) * 10), round(92 + math.sin(math.radians(a)) * 4.5), GOLD, 3.6)
    cv.rect(162, 91, 170, 97, IRON, lambda x, y: 2.8 - (x - 162) * 0.25)
    cv.hline(162, 170, 91, IRON, 4.0)
    cv.hline(164, 169, 93, IRON, 0.2)                                            # ranura per on corre el braç
    cv.disc(166, 92, 2, 2, GOLD, lambda nx, ny: 4.4 - nx - ny)                   # eix

    # ─── Llum d'alarma de la consola (gàbia amb vidre vermell) ───────────────
    bx, by = BEACON
    cv.rect(bx - 6, by + 9, bx + 6, by + 12, IRON, lambda x, y: 3.0 - (y - by - 9) * 0.6)
    cv.rect(bx - 2, by + 12, bx + 2, by + 13, IRON, 1.2)
    if alarm:
        cv.disc(bx, by + 3, 5, 7, REDGL, lambda nx, ny: 5.6 - (nx * nx + ny * ny) * 2.4 - ny * 0.6, 0)
    else:
        cv.disc(bx, by + 3, 5, 7, REDGL, lambda nx, ny: 2.6 - nx * 1.2 - ny * 0.8)
        cv.put(bx - 2, by - 1, REDGL, 5.0)
    for k in (-4, 0, 4):                                                         # gàbia
        cv.line(bx + k, by - 3 + abs(k) // 2, bx + k, by + 9, IRON, 3.4 if k < 0 else 2.0)
    cv.hline(bx - 5, bx + 5, by + 3, IRON, 2.4)
    cv.disc(bx, by - 4, 2, 1.4, IRON, 3.0)
    # campana de l'alarma (a la paret, sobre la consola)
    cv.disc(116, 68, 6.5, 6.5, GOLD, lambda nx, ny: 3.2 - nx * 1.2 - ny * 1.2)      # gong de la campana
    cv.ring(116, 68, 4.5, GOLD, 4.6, step=6)
    cv.ring(116, 68, 6.5, GOLD, 1.2, step=4)
    cv.disc(116, 68, 1.5, 1.5, IRON, 3.0)
    cv.rect(112, 76, 120, 81, IRON, lambda x, y: 3.0 - (x - 112) * 0.2 - (y - 76) * 0.2)   # caixa del timbre
    cv.hline(112, 120, 76, IRON, 4.0)
    cv.line(119, 76, 122, 70, IRON, 3.0)                                         # martell
    cv.disc(122.5, 69.5, 1.3, 1.3, IRON, 3.6)
    cv.line(116, 81, 116, 88, SIL, 1.2)                                         # cable de la campana

    # ─── Cables que pugen de la cambra al sostre ─────────────────────────────
    for x, lv in ((222, 1.4), (226, 1.0), (292, 1.4), (296, 1.0)):
        cv.vline(x, 19, 22, SIL, lv)
        cv.vline(x + 1, 19, 22, SIL, lv + 0.8)

    # ─── Cambra de ressonància (201..317 × 13..161) ──────────────────────────
    PX0, PX1 = 199, 319
    contact_shadow(cv, PX0, PX1, FLOOR_Y + 6, 7)
    # plataforma de ferro amb franges de perill
    cv.rect(PX0, 141, PX1, 160, IRON, lambda x, y: 2.0 - (y - 141) * 0.05)
    cv.hline(PX0, PX1, 141, IRON, 4.2)
    cv.hline(PX0, PX1, 142, IRON, 3.2)
    cv.vline(PX0, 141, 160, IRON, 3.0)
    cv.vline(PX1, 141, 160, IRON, 0.8)
    for y in range(146, 151):
        for x in range(PX0 + 3, PX1 - 2):
            yel = ((x + y) // 5) % 2 == 0
            cv.put(x, y, WARN if yel else SIL, (2.6 if yel else 1.0) - (hr(x, y, 4) > 0.9) * 1.0)
    cv.hline(PX0 + 3, PX1 - 3, 145, IRON, 0.6)
    cv.hline(PX0 + 3, PX1 - 3, 151, IRON, 3.0)
    for x in range(PX0 + 4, PX1 - 2, 12):
        rivet(cv, x, 155, 2.0)
    cv.hline(PX0, PX1, 160, IRON, 0.3)
    # graó davant
    cv.rect(226, 156, 292, 161, IRON, lambda x, y: 3.2 - (y - 156) * 0.4)
    cv.hline(226, 292, 156, IRON, 4.4)
    for x in range(228, 292, 3):
        cv.put(x, 158, IRON, 1.4)

    # interior: fons fosc de la cambra, il·luminat pel camp
    GX0, GX1, GY0, GY1 = 216, 302, 34, 138
    dim = 1 if alarm else 0                                      # el camp, de nit, és més apagat
    for y in range(GY0, GY1 + 1):
        for x in range(GX0, GX1 + 1):
            d = math.hypot(x - CORE[0], (y - CORE[1]) * 0.7) / 70
            lvl = 4.2 - d * 3.2 - dim
            for gx in (247.5, 270.5):                                # fils d'energia entre bobines
                w = gx + math.sin(y / 5.0 + gx) * 2.2
                if abs(x - w) < 0.8 and 52 < y < 124:
                    lvl += 1.8
                elif abs(x - w) < 3:
                    lvl += 0.6
            cv.put(x, y, FIELD, lvl, 0)
    # anells de llautó que aguanten les bobines
    for yy in (46, 126):
        cv.rect(GX0 + 2, yy, GX1 - 2, yy + 3, GOLD, lambda x, y: 3.4 - (y - yy) * 0.6 - abs(x - CORE[0]) / 60, 0.4)
    # tres bobines: nucli de ferro-9 enrotllat amb fil de coure
    for cx in (236, 259, 282):
        for y in range(50, 126):
            for x in range(cx - 6, cx + 7):
                s = (x - cx) / 6.5
                band = (y - 50) % 13
                if band in (11, 12):                                 # espai entre enrotllaments: el ferro-9 nu
                    if abs(s) < 0.6:
                        cv.put(x, y, FE9, 5.0 - s * 2.4 - (1.2 if band == 12 else 0), 0.3)
                    continue
                if abs(s) > 0.9 and (x - cx) * (CORE[0] - cx) > 0 and band not in (0, 10):            # vora encesa pel camp
                    cv.put(x, y, FIELD, 5.5 - dim, 0)
                    continue
                lv = 3.2 - s * 1.4 - s * s * 1.4 + (y % 2) * 0.5 - (1.0 if band in (0, 10) else 0)
                cv.put(x, y, COPPER, round(lv - dim) + 0.5, 0)
        # caps de ferro-9 polit
        for yy in (49, 125):
            cv.rect(cx - 7, yy, cx + 7, yy + 1, FE9, lambda x, y: 5.4 - (x - cx) / 4.0, 0.3)
        cv.vline(cx - 1, 42, 49, FE9, 5.6, 0.3)
        cv.vline(cx, 42, 49, FE9, 4.4, 0.3)
        cv.vline(cx - 1, 127, 136, FE9, 4.4, 0.3)
    # el camp: lluïssor entre les bobines
    for cx in (247, 271):
        cv.glow(cx, 88, 18, (190, 160, 255), 0.0 if alarm else 0.45)
    cv.glow(CORE[0], CORE[1], 60, (150, 110, 240), 0.22 if alarm else 0.4)
    # el vidre: lleuger tint fred i reflexos en diagonal
    cv.tint(GX0, GY0, GX1, GY1, (170, 200, 230), 0.06)

    def streak(x, y):
        u = x - GX0 + (y - GY0) * 0.55
        return 0.32 if 8 <= u <= 14 else (0.2 if 18 <= u <= 19 else (0.16 if 70 <= u <= 76 else 0.0))

    cv.tint(GX0, GY0, GX1, GY1, (230, 244, 255), streak)
    cv.vline(GX0 + 1, GY0 + 2, GY1 - 2, PAPER, 4.4, 0)                          # cantell gruixut del vidre
    cv.vline(GX0 + 2, GY0 + 2, GY1 - 2, FE9, 4.0, 0)
    cv.hline(GX0 + 1, GX1 - 1, GY1 - 1, FE9, 3.4, 0)
    # muntants laterals (guies del vidre que baixa)
    for x0, lit in ((203, True), (303, False)):
        cv.rect(x0, 26, x0 + 12, 140, IRON, lambda x, y: [1.0, 3.8, 3.2, 2.8, 2.6, 2.4, 2.2, 2.0, 1.8, 1.6, 1.4, 1.0, 0.4][x - x0]
                - (0 if lit else 0.5))
        cv.vline(x0 + 11 if lit else x0 + 1, 34, 138, GOLD, 3.4)                # ranura de llautó
        for y in range(32, 138, 10):
            rivet(cv, x0 + 4, y, 2.4)
            rivet(cv, x0 + 8, y, 2.0)
    # caixa superior on s'amaga el vidre, amb aïlladors
    cv.rect(199, 20, 319, 33, IRON, lambda x, y: 2.6 - (y - 20) * 0.08)
    cv.hline(199, 319, 20, IRON, 4.2)
    cv.hline(199, 319, 33, IRON, 0.4)
    cv.rect(234, 23, 284, 30, GOLD, lambda x, y: 3.2 - (y - 23) * 0.25)          # placa
    cv.hline(234, 284, 23, GOLD, 4.6)
    for x in range(238, 281, 2):
        if hr(x // 3, 11) > 0.25:
            cv.put(x, 26, GOLD, 1.2); cv.put(x, 27, GOLD, 1.4)
    for x in range(203, 318, 8):
        rivet(cv, x, 31, 2.0)
    for ix in (210, 222, 296, 308):                                              # aïlladors de porcellana
        for j in range(3):
            cv.disc(ix, 17 - j * 2, 2.6 - j * 0.3, 1.0, PAPER, lambda nx, ny: 3.6 - nx * 1.2, 0.8)
        cv.vline(ix, 11, 13, COPPER, 3.0)
    # llengua de vidre a la ranura de dalt
    cv.hline(GX0, GX1, GY0 - 1, FE9, 1.4)
    # lluïssor violeta del camp sobre el que hi ha al voltant
    if not alarm:
        cv.glow(CORE[0], 120, 90, (120, 90, 220), 0.16)
        cv.glow(CORE[0], 158, 60, (150, 120, 240), 0.12)
        cv.tint(150, 161, 370, 205, (150, 120, 240),
                lambda x, y: 0.28 * max(0.0, 1 - math.hypot((x - CORE[0]) / 100, (y - 163) / 26)) ** 1.2)

    # ─── Reixa del conducte de servei (335..393 × 114..150) ──────────────────
    RX0, RY0, RX1, RY1 = 335, 114, 393, 150
    cv.rect(RX0, RY0, RX1, RY1, IRON, lambda x, y: 2.8 - (y - RY0) * 0.02)
    cv.hline(RX0, RX1, RY0, IRON, 4.0)
    cv.vline(RX0, RY0, RY1, IRON, 3.6)
    cv.hline(RX0, RX1, RY1, IRON, 0.8)
    cv.vline(RX1, RY0, RY1, IRON, 1.0)
    cv.rect(RX0 + 4, RY0 + 4, RX1 - 4, RY1 - 4, SIL, lambda x, y: 0.4 + max(0, 1 - abs(x - 364) / 30) * 0.6)  # conducte fosc
    for y in range(RY0 + 5, RY1 - 4, 4):                                         # lamel·les
        cv.hline(RX0 + 4, RX1 - 4, y, IRON, 3.4)
        cv.hline(RX0 + 4, RX1 - 4, y + 1, IRON, 2.2)
        cv.hline(RX0 + 4, RX1 - 4, y + 2, IRON, 0.6)
    cv.vline(364, RY0 + 4, RY1 - 4, IRON, 2.6)                                   # travesser
    cv.vline(365, RY0 + 4, RY1 - 4, IRON, 1.2)
    for x, y in ((RX0 + 2, RY0 + 2), (RX1 - 2, RY0 + 2), (RX0 + 2, RY1 - 2), (RX1 - 2, RY1 - 2)):
        cv.disc(x, y, 1.8, 1.8, IRON, lambda nx, ny: 4.6 - nx * 1.2 - ny * 1.2)   # cargols d'acer nous
        cv.put(x, y, IRON, 1.0)
    contact_shadow(cv, RX0, RX1, FLOOR_Y, 4, fall=3)

    # ─── Canonada vertical amb vàlvula i manòmetre (404..410) ────────────────
    for y in range(18, 154):
        for x in range(404, 411):
            cv.put(x, y, COPPER, [1.4, 3.2, 3.8, 3.2, 2.4, 1.6, 0.6][x - 404])
    cv.rect(402, 17, 412, 20, COPPER, 3.0)
    for y in (46, 120):
        cv.rect(402, y, 412, y + 2, COPPER, lambda x, yy: 3.6 - (yy - y) * 0.8)
    cv.rect(400, 148, 414, 153, IRON, lambda x, y: 2.4 - (y - 148) * 0.3)
    cv.ring(407, 96, 7, IRON, 3.0, step=4)                                        # volant de la vàlvula
    cv.ring(407, 96, 6, IRON, 1.8, step=4)
    for a in (0, 90, 180, 270):
        cv.line(407, 96, 407 + round(math.cos(math.radians(a + 45)) * 6), 96 + round(math.sin(math.radians(a + 45)) * 6), IRON, 2.6)
    cv.disc(407, 96, 1.6, 1.6, RED, 3.2)
    cv.disc(419, 72, 5.6, 5.6, GOLD, lambda nx, ny: 3.4 - nx - ny)              # manòmetre
    cv.disc(419, 72, 4.2, 4.2, PAPER, lambda nx, ny: 3.8 - ny * 0.6)
    cv.line(419, 72, 422, 70, RED, 2.6)
    cv.hline(411, 414, 72, COPPER, 3.0)
    # rètol de perill sobre la reixa
    cv.rect(346, 72, 382, 92, WARN, lambda x, y: 3.2 - (y - 72) * 0.04)
    for x in range(346, 383):
        for y in (72, 73, 91, 92):
            if ((x + y) // 3) % 2 == 0:
                cv.put(x, y, SIL, 0.6)
    cv.poly([(364, 76), (359, 83), (363, 83), (361, 89), (369, 80), (365, 80), (367, 76)], SIL, 0.4)   # llamp
    cv.darken(347, 93, 383, 94, 0.5)
    cv.darken(383, 73, 384, 94, 0.5)

    # ─── Pissarra amb càlculs de ressonància (420..444 × 40..112) ────────────
    QX0, QY0, QX1, QY1 = 422, 46, 444, 112
    cv.rect(QX0 - 3, QY0 - 3, QX1 + 3, QY1 + 3, WALNUT, lambda x, y: 3.2 - (1.6 if x > QX1 or y > QY1 else 0))
    cv.rect(QX0, QY0, QX1, QY1, SLATE, lambda x, y: 1.6 + (hr(x // 2, y // 3, 6) - 0.5) * 0.5)
    for i in range(3):                                                           # ones
        yb = 56 + i * 16
        for x in range(QX0 + 2, QX1 - 1):
            y = yb + round(math.sin((x - QX0) / (2.2 + i) ) * (3 - i * 0.6))
            cv.put(x, y, CHALK, 2.0 - i * 0.3, 0.5)
    for y in range(102, 109, 3):
        for x in range(QX0 + 2, QX1 - 2):
            if hr(x // 2, y, 7) > 0.35:
                cv.put(x, y, CHALK, 1.4, 0.5)
    cv.rect(QX0 - 4, QY1 + 3, QX1 + 4, QY1 + 5, WALNUT, lambda x, y: 3.8 - (y - QY1 - 3))
    cv.rect(428, QY1 + 1, 431, QY1 + 2, CHALK, 3.0)

    # ─── Galleda de sorra contra el foc (dreta) ─────────────────────────────
    contact_shadow(cv, 462, 476, 160, 4, fall=3)
    for y in range(140, 162):
        t = (y - 140) / 21
        xl, xr = 462 + t * 1.5, 476 - t * 1.5
        for x in range(round(xl), round(xr) + 1):
            s = (x - (xl + xr) / 2) / ((xr - xl) / 2)
            cv.put(x, y, RED, 3.4 - s * 1.6 - s * s)
    cv.disc(469, 140, 7.5, 1.6, MANILA, 2.2)
    cv.hline(461, 477, 139, RED, 4.2)
    for y in (146, 156):
        cv.hline(round(462 + (y - 140) / 21 * 1.5), round(476 - (y - 140) / 21 * 1.5), y, RED, 1.6)

    # ─── Làmpades industrials penjades ───────────────────────────────────────
    for (lx, ly) in (LAMP1, LAMP2):
        cv.vline(lx, 18, ly - 6, SIL, 1.0)
        for y in range(ly - 6, ly + 1):
            t = (y - ly + 6) / 6
            half = 2 + t * 9
            for x in range(round(lx - half), round(lx + half) + 1):
                u = (x - lx) / half
                cv.put(x, y, GRAY if not alarm else IRON, 3.6 - u * 1.4 - (1 - t) * 0.8)
        cv.hline(lx - 11, lx + 11, ly + 1, GRAY, 1.0)
        cv.rect(lx - 2, ly - 8, lx + 2, ly - 6, IRON, 2.4)
        if not alarm:
            cv.disc(lx, ly + 2, 3, 1.8, BULB, 0, 0)
            cv.glow(lx, ly + 3, 30, (255, 220, 150), 0.5)
        else:
            cv.disc(lx, ly + 2, 3, 1.8, GLASSD, lambda nx, ny: 1.0 - nx, 0)

    # ─── Retoc: escalfor de les làmpades i frescor del camp ──────────────────
    if not alarm:
        cv.tint(0, 0, W - 1, H - 1, (255, 200, 130),
                lambda x, y: 0.10 * max(0.0, 1 - math.hypot(x - LAMP1[0], (y - LAMP1[1]) * 1.1) / 120))


GLASSD = [(30, 26, 26), (56, 50, 48), (90, 84, 80)]


# ─── Props ─────────────────────────────────────────────────────────────────

def boto(cv):
    """El botó vermell de sincronia, encès, amb la placa «SINCRONIA» (114..140 × 84..104)."""
    cv.rect(116, 89, 138, 101, IRON, lambda x, y: 2.2 + (y - 89) * 0.04)
    cv.hline(116, 138, 89, IRON, 3.8)
    cv.vline(116, 89, 101, IRON, 3.2)
    cv.hline(116, 138, 101, IRON, 0.6)
    cv.vline(138, 89, 101, IRON, 0.8)
    # placa de llautó amb el rètol
    cv.rect(118, 98, 136, 100, GOLD, lambda x, y: 3.8 - (y - 98) * 0.6)
    for x in range(120, 135):
        if (x - 120) % 2 == 0 or hr(x, 3) > 0.5:
            cv.put(x, 99, GOLD, 1.0)
    # bisell i bolet vermell
    cv.disc(127, 92.5, 6.2, 3.6, GOLD, lambda nx, ny: 4.2 - nx * 1.4 - ny * 1.4)
    cv.disc(127, 92.5, 5.0, 2.8, IRON, 0.6)
    cv.disc(127, 90.5, 4.4, 3.2, REDGL, lambda nx, ny: 5.2 - (nx * nx + ny * ny) * 1.6 - ny * 1.0 - nx * 0.6, 0)
    cv.put(125, 89, REDGL, 6.0, 0)
    cv.put(126, 89, REDGL, 6.0, 0)
    cv.glow(127, 91, 16, (255, 70, 50), 0.6)


def lever(cv, ang, arm=29):
    """Braç de la palanca amb mànec de fusta; ang en graus des de la vertical (+ cap a la dreta)."""
    px, py = 166.5, 92
    ux, uy = math.sin(math.radians(ang)), -math.cos(math.radians(ang))
    nx, ny = -uy, ux                                                              # normal (cap a la dreta del braç)
    tx, ty = px + ux * arm, py + uy * arm
    cv.poly([(px - nx * 2.6, py - ny * 2.6), (px + nx * 2.6, py + ny * 2.6),
             (tx + nx * 2.0, ty + ny * 2.0), (tx - nx * 2.0, ty - ny * 2.0)], IRON,
            lambda x, y: 4.6 - (((x - px) * nx + (y - py) * ny) / 2.4 + 1) * 2.1)
    # mànec de fusta
    hx, hy = tx + ux * 7, ty + uy * 7
    thick(cv, round(tx), round(ty), round(hx), round(hy), 2, WALNUT, lambda s: 4.4 - s * 2.2)
    cv.disc(hx + ux * 0.5, hy + uy * 0.5, 2.6, 2.4, WALNUT, lambda a, b: 4.6 - a - b)
    cv.disc(166, 92, 2, 2, GOLD, lambda a, b: 4.4 - a - b)                       # eix, per sobre del braç


def palanca_alcada(cv):
    """La palanca alçada: l'alarma encara funciona."""
    lever(cv, 11.7)


def palanca_baixada(cv):
    """La palanca abatuda contra el tope esquerre del quadrant."""
    lever(cv, -52, arm=21)
    # el tope de goma que l'atura
    cv.disc(156, 89, 1.6, 1.4, IRON, lambda a, b: 1.6 - a - b)


def reixa_llimada(cv):
    """Els cargols de la reixa, llimats (llueixen), i una ratlla de llima al marc."""
    RX0, RY0, RX1, RY1 = 335, 114, 393, 150
    for x, y in ((RX0 + 2, RY0 + 2), (RX1 - 2, RY0 + 2), (RX0 + 2, RY1 - 2), (RX1 - 2, RY1 - 2)):
        cv.disc(x, y, 1.8, 1.8, IRON, lambda nx, ny: 7.0 - nx - ny, 0.3)
        cv.flat(x, y, (255, 250, 226))
        for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
            cv.put(x + dx, y + dy, IRON, 6.0, 0.3)                       # llimadures brillants al voltant
    for x in range(RX0 + 6, RX1 - 6):                                      # ratlles de llima al marc
        if hr(x, 5) > 0.35:
            cv.put(x, RY1 - 1, IRON, 6.4, 0.3)
    for x in range(RX0 + 1, RX0 + 4):
        cv.put(x, RY1 + 3, IRON, 5.6, 0.3)
    # llimadures a terra
    for i in range(14):
        x = RX0 + 2 + int(hr(i, 8) * (RX1 - RX0 - 4))
        y = 155 + int(hr(i, 9) * 4)
        cv.put(x, y, IRON, 5.4 + hr(i, 1), 0.3)


PROPS = {'boto': boto, 'reixa_llimada': reixa_llimada,
         'palanca_alcada': palanca_alcada, 'palanca_baixada': palanca_baixada}
