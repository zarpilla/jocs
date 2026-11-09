"""
Cel·la 9 de La Gavina (Acte 1, Vet): acer fred i net, amb peces velles i rovellades de la fàbrica
(el panell, la reixa, el pany) encastades a la paret. Llums: el fluorescent del sostre, el cor rosa de
la MARE i la Terra a la finestreta.

`bg(cv, night=True)` el fa servir el pròleg (la mateixa cel·la, de nit).
"""
import math
import random

from hd.pix import (Light, B4, W, H, hr, ramp, STEEL, PANEL, RUST, GOLD, PAPER, PINK, CYAN, TEAL, SPACE, ORANGE,
                    IRON, WARN, SKIN, GRAY, MANILA, NAVY, RED, LAMPG, COPPER)

LIGHT = Light(vignette=(80, 46), floor_fade=(196, 36))
LIGHT.point(244, 4, r=270, k=4.2, squash=0.8, power=2.0)           # fluorescent del sostre
LIGHT.add(lambda x, y: max(0.0, 1 - math.hypot((x - 236) / 150, (y - 186) / 34)) ** 1.2 * 1.6 if y > 157 else 0.0)  # bassal de llum al terra
LIGHT.point(176, 30, r=46, k=0.9)                                   # el cor de la MARE
LIGHT.point(336, 50, r=64, k=0.8)                                   # la finestreta

# Rampes pròpies
DECK = ramp((6, 8, 14), (16, 20, 30), (30, 36, 48), (48, 56, 70), (72, 82, 98), (104, 114, 130), (150, 160, 172), n=9)
MATT = ramp((14, 18, 30), (34, 42, 60), (62, 74, 96), (98, 112, 132), (146, 158, 172), (196, 204, 212), n=8)
SHEET = ramp((40, 40, 56), (84, 86, 102), (136, 138, 150), (186, 188, 194), (228, 228, 230), n=7)
GRIME = ramp((10, 10, 14), (24, 22, 26), (40, 36, 38), (60, 52, 50), n=4)
LIME = ramp((20, 36, 10), (52, 84, 20), (96, 140, 36), (150, 196, 70), (210, 240, 140), n=6)
BEET = ramp((8, 6, 6), (26, 16, 14), (52, 32, 24), (88, 58, 40), (140, 104, 76), n=6)

FLOOR_Y = 158          # línia paret-terra
VPX, VPY = 240, -150   # punt de fuga del terra

FONT = {
    'C': ['###', '#..', '#..', '#..', '###'], '9': ['###', '#.#', '###', '..#', '###'],
    '-': ['...', '...', '###', '...', '...'], 'M': ['#.#', '###', '#.#', '#.#', '#.#'],
    'O': ['###', '#.#', '#.#', '#.#', '###'], 'D': ['##.', '#.#', '#.#', '#.#', '##.'],
    'U': ['#.#', '#.#', '#.#', '#.#', '###'], 'L': ['#..', '#..', '#..', '#..', '###'],
    ' ': ['...'] * 5, '3': ['###', '..#', '.##', '..#', '###'], 'A': ['###', '#.#', '###', '#.#', '#.#'],
    'I': ['#', '#', '#', '#', '#'],
}


def text(cv, s, x, y, rp, lvl, lit=1.0, worn=0.0):
    for ch in s:
        g = FONT[ch]
        for j, row in enumerate(g):
            for i, c in enumerate(row):
                if c == '#' and hr(x + i, y + j, 5) >= worn:
                    cv.put(x + i, y + j, rp, lvl, lit)
        x += len(g[0]) + 1


def rivet(cv, x, y, rp=STEEL, lvl=4.0):
    cv.put(x, y, rp, lvl + 1.6)
    cv.put(x + 1, y, rp, lvl + 0.4)
    cv.put(x, y + 1, rp, lvl - 0.6)
    cv.put(x + 1, y + 1, rp, lvl - 1.8)


def bolt(cv, cx, cy, rp, lvl, r=1.8):
    cv.disc(cx, cy, r, r, rp, lambda nx, ny: lvl - nx * 1.2 - ny * 1.4)
    cv.put(round(cx - 0.6), round(cy - 0.6), rp, lvl + 1.6)


def contact_shadow(cv, x0, x1, y0, y1, k=0.9):
    """Ombra al terra sota un objecte: més fosca a dalt, a quadres cap avall i als costats."""
    for y in range(y0, y1 + 1):
        for x in range(x0 - 3, x1 + 4):
            a = k * (1 - (y - y0) / max(1, y1 - y0 + 1)) * (1 - max(0, max(x0 - x, x - x1)) / 4)
            if a > B4[y & 3][x & 3]:
                o = cv.get(x, y)
                if o[3]:
                    cv.P[x, y] = tuple(int(c * 0.6) for c in o[:3]) + (o[3],)


# ─── Fons ─────────────────────────────────────────────────────────────────────

def bg(cv, night=False):
    # ─── Sostre amb el fluorescent ────────────────────────────────────────────
    cv.rect(0, 0, W - 1, 10, STEEL, lambda x, y: 1.0 + y * 0.12 + (0.5 if x % 40 == 0 else 0))
    for x in range(0, W, 40):
        cv.vline(x + 1, 0, 10, STEEL, 2.4)
    cv.hline(0, W - 1, 11, STEEL, 4.0)
    cv.hline(0, W - 1, 12, STEEL, 2.6)
    cv.hline(0, W - 1, 13, STEEL, 0.4)
    # canal de cables al llarg de la paret (porta el cable fins al cor)
    cv.rect(0, 15, W - 1, 18, STEEL, lambda x, y: [3.6, 3.0, 2.4, 1.2][y - 15])
    for x in range(6, W, 32):
        cv.rect(x, 14, x + 2, 19, STEEL, lambda xx, yy: 4.2 - (xx - x) * 0.8)
    # el fluorescent (196..292)
    cv.rect(194, 1, 294, 9, STEEL, lambda x, y: 2.0 - (y - 1) * 0.1)
    cv.hline(194, 294, 9, STEEL, 4.6)
    if night:
        cv.rect(198, 3, 290, 7, CYAN, lambda x, y: 0.6 + (0.4 if (x // 6) % 2 else 0), 0)
        cv.rect(240, 4, 248, 6, CYAN, 2.4, 0)                          # llum de vigilància, tènue
    else:
        cv.rect(198, 3, 290, 7, CYAN, lambda x, y: 4.6 - (0.6 if x % 12 == 0 else 0), 0)
        cv.hline(198, 290, 5, [(250, 254, 255)], 0, 0)
        for x in range(198, 291, 12):
            cv.vline(x, 3, 7, STEEL, 3.0, 0)

    # ─── Paret: planxes d'acer reblades ───────────────────────────────────────
    WALL_T, BAND_Y, WALL_B = 19, 124, 149
    COLS = [0, 54, 118, 172, 226, 296, 352, 412, W]
    ROWS = [WALL_T, 60, 102, BAND_Y]

    def wall(x, y):
        ci = max(i for i, c in enumerate(COLS[:-1]) if c <= x)
        ri = max(i for i, r in enumerate(ROWS[:-1]) if r <= y)
        x0, x1 = COLS[ci], COLS[ci + 1] - 1
        y0, y1 = ROWS[ri], ROWS[ri + 1] - 1
        lvl = 2.2 + (hr(ci, ri, 1) - 0.5) * 0.5 - (y - y0) / (y1 - y0 + 1) * 0.6
        if x == x0 or y == y0:
            return 1.0                                                    # junta
        if x == x0 + 1 or y == y0 + 1:
            return lvl + 1.0                                              # cantell il·luminat
        if x == x1:
            return lvl - 0.8
        # brutícia: regalims suaus cap avall
        g = hr(x // 3, ci, 7)
        if g > 0.86 and y > y0 + 6:
            lvl -= 0.35 * min(1, (y - y0) / 20)
        return lvl

    cv.rect(0, WALL_T, W - 1, BAND_Y - 1, STEEL, wall)
    # reblons al llarg de les juntes
    for ri in range(len(ROWS) - 1):
        for ci in range(len(COLS) - 1):
            x0, x1, y0, y1 = COLS[ci], COLS[ci + 1] - 1, ROWS[ri], ROWS[ri + 1] - 1
            n = max(2, round((x1 - x0) / 13))
            for k in range(n + 1):
                rx = round(x0 + 4 + (x1 - x0 - 9) * k / n)
                rivet(cv, rx, y0 + 3, STEEL, 2.6)
                if ri == len(ROWS) - 2:
                    rivet(cv, rx, y1 - 3, STEEL, 2.6)
    # ombra del canal de cables
    cv.darken(0, 19, W - 1, 22, lambda x, y: 1 - (y - 19) / 4)

    # franja pintada (verd blavós de presó) i sòcol fosc
    cv.rect(0, BAND_Y, W - 1, BAND_Y + 1, STEEL, 4.4)
    cv.rect(0, BAND_Y + 2, W - 1, BAND_Y + 5, TEAL, lambda x, y: 2.6 - (y - BAND_Y - 2) * 0.2 - (0.5 if hr(x // 4, 3) > 0.85 else 0))
    cv.hline(0, W - 1, BAND_Y + 6, STEEL, 1.0)

    def kick(x, y):
        px = x % 60
        lvl = 2.0 - (y - BAND_Y - 7) * 0.02
        if px == 0:
            return 0.8
        if px == 1:
            return 2.8
        if (y - BAND_Y) % 9 == 0:
            lvl -= 0.4
        return lvl + (hr(x // 2, y // 5, 2) - 0.5) * 0.2

    cv.rect(0, BAND_Y + 7, W - 1, WALL_B, STEEL, kick)
    cv.hline(0, W - 1, WALL_B + 1, STEEL, 3.8)
    cv.rect(0, WALL_B + 2, W - 1, FLOOR_Y - 1, STEEL, lambda x, y: [2.4, 2.0, 1.6, 1.2, 0.8, 0.5][min(5, y - WALL_B - 2)])

    # ─── Terra: planxes en perspectiva ────────────────────────────────────────
    for y in range(FLOOR_Y, H):
        dep = y - VPY
        t = 3600 / dep
        row = math.floor(t / 2.3)
        row_up = math.floor(3600 / (dep - 1) / 2.3)
        for x in range(W):
            u = (x - VPX) / dep * 30 / 3.2
            col = math.floor(u)
            fr = (u - col) * dep / 30 * 3.2
            lvl = 2.4 + (hr(col, row, 4) - 0.5) * 0.35
            if fr < 1:
                lvl = 0.8
            elif fr < 2:
                lvl += 0.6
            elif row != row_up:
                lvl = 0.9
            elif math.floor(3600 / (dep - 2) / 2.3) != row:
                lvl += 0.5
            else:
                # textura de llàgrimes (planxa antilliscant) molt suau
                if (hr(col, row, 9) > 0.5) and ((x + (y % 2) * 2) % 4 == 0) and y % 2 == 0:
                    lvl += 0.35
            if y < FLOOR_Y + 6:
                lvl -= (FLOOR_Y + 6 - y) / 6 * 1.2                      # ombra de contacte amb la paret
            cv.put(x, y, DECK, lvl)
    # reblons a les cantonades de les planxes (només a la part visible)
    for y in range(FLOOR_Y + 2, 205):
        dep = y - VPY
        t = 3600 / dep
        if math.floor(t / 2.3) != math.floor(3600 / (dep - 3) / 2.3):
            for c in range(-14, 15):
                x = round(VPX + (c + 0.12) * 3.2 * dep / 30) + 3
                if 0 <= x < W:
                    cv.put(x, y, DECK, 4.0)
                    cv.put(x + 1, y + 1, DECK, 1.2)
    # desguàs al mig del terra
    cv.disc(206, 192, 11, 3.4, DECK, 0.6)
    for x in range(197, 216, 3):
        cv.vline(x, 190, 194, DECK, 2.8)
    cv.hline(198, 214, 189, DECK, 3.6)

    # ─── Porta de la cel·la (8..65 × 49..155) ─────────────────────────────────
    cv.rect(8, 49, 65, 157, STEEL, lambda x, y: 1.6 + (1.4 if x in (9, 10) or y in (50, 51) else 0) - (0.8 if x > 62 else 0))
    # bandes d'avís grogues i negres al marc
    for y in range(52, 156):
        for x in list(range(10, 14)) + list(range(59, 63)):
            k = ((x + y) // 4) % 2
            cv.put(x, y, WARN if k else STEEL, 2.8 if k else 0.8)
    for x in range(10, 63):
        for y in range(51, 55):
            k = ((x + y) // 4) % 2
            cv.put(x, y, WARN if k else STEEL, 3.0 if k else 0.8)
    cv.vline(14, 55, 157, STEEL, 0.3)
    cv.hline(14, 58, 55, STEEL, 0.3)

    # fulla de la porta (corredissa), més vella que les planxes de la paret
    def door(x, y):
        lvl = 2.8 - abs(x - 30) / 30 * 0.6 + (hr(x // 2, 41) - 0.5) * 0.15
        if x == 15:
            return 4.2
        if x == 58:
            return 1.0
        # reforços horitzontals
        for ry in (88, 122):
            if ry <= y <= ry + 3:
                return [4.4, 3.6, 3.0, 1.2][y - ry]
        if y in (126, 127) and 18 <= x <= 55:
            return 1.5
        return lvl

    cv.rect(15, 56, 58, 155, STEEL, door)
    # finestreta amb barrots
    cv.rect(21, 63, 52, 82, STEEL, 0.6)
    cv.hline(21, 52, 63, STEEL, 0.2)
    cv.rect(22, 64, 51, 81, NAVY, lambda x, y: 1.0 + (y - 64) / 18 * 1.6, 0.2)   # el passadís, fosc
    cv.glow(36, 74, 14, (120, 60, 70), 0.25)                                    # llum vermella del passadís
    for x in range(24, 51, 4):
        cv.vline(x, 64, 81, STEEL, 4.0)
        cv.vline(x + 1, 64, 81, STEEL, 2.4)
    cv.hline(21, 52, 83, STEEL, 4.2)
    # número de la cel·la, estarcit
    text(cv, 'C-9', 28, 95, PAPER, 3.0, worn=0.12)
    # trapa del menjar
    cv.rect(23, 132, 48, 141, STEEL, lambda x, y: 2.0 + (1.4 if y == 132 else 0) - (1.2 if y == 141 else 0))
    cv.rect(33, 135, 38, 136, STEEL, 4.0)
    # escletxa de sota la porta (per on la MARE passa els avisos)
    cv.hline(15, 58, 155, STEEL, 0.0)
    cv.hline(15, 58, 156, NAVY, 2.0, 0.2)
    # pany magnètic Aldaia M-3: una caixa de ferro vella amb placa de llautó
    cv.rect(47, 98, 57, 119, IRON, lambda x, y: 3.0 - (x - 47) * 0.12 - (y - 98) * 0.03)
    cv.vline(47, 98, 119, IRON, 4.4)
    cv.hline(47, 57, 119, IRON, 0.8)
    cv.vline(57, 98, 119, IRON, 1.0)
    cv.rect(48, 101, 56, 104, GOLD, lambda x, y: 3.6 - (y - 101) * 0.4)          # placa «ALDAIA M-3»
    for x in range(49, 56):
        if x % 2:
            cv.put(x, 102, GOLD, 1.4)
    cv.rect(49, 108, 55, 112, IRON, 0.6)
    cv.rect(50, 109, 54, 111, CYAN, lambda x, y: 3.0 - (x - 50) * 0.3, 0)
    cv.put(51, 109, CYAN, 5, 0)
    cv.glow(52, 110, 9, (90, 200, 255), 0.5)
    bolt(cv, 49, 116, IRON, 3.0, 0.9)
    bolt(cv, 55, 116, IRON, 3.0, 0.9)

    # ─── Altaveu de la MARE: un cor de plàstic rosa (158..193 × 13..44) ──────
    # suport i cable
    cv.rect(173, 15, 179, 18, STEEL, 2.6)
    cv.vline(176, 18, 20, STEEL, 1.2)
    HX, HY = 176, 28
    pink_ramp = PINK if not night else ramp((24, 8, 22), (60, 16, 44), (110, 34, 80), (160, 60, 120), n=6)

    def heart_in(x, y):
        nx, ny = (x - HX) / 15.0, (y - HY) / 14.0
        # cor clàssic: (x²+y²−1)³ − x²y³ ≤ 0 (amb y cap amunt)
        X, Y = nx * 1.15, -ny * 1.15 + 0.25
        return (X * X + Y * Y - 1) ** 3 - X * X * Y ** 3 <= 0

    for y in range(14, 45):
        for x in range(158, 195):
            if not heart_in(x, y):
                continue
            edge = not (heart_in(x - 1, y) and heart_in(x + 1, y) and heart_in(x, y - 1) and heart_in(x, y + 1))
            edge2 = not (heart_in(x - 2, y) and heart_in(x + 2, y) and heart_in(x, y - 2) and heart_in(x, y + 2))
            nx, ny = (x - HX) / 15, (y - HY) / 14
            lvl = 3.0 - nx * 0.9 - ny * 1.1
            if edge:
                lvl = 0.8 if (nx > 0 or ny > 0.3) else 2.0
            elif edge2:
                lvl += 0.8
            # forats de la reixeta
            elif -0.8 < ny < 0.55 and abs(nx) < 0.75 - max(0, ny) * 0.6 and (x % 3 == 0) and (y % 3 == 1):
                lvl = 0.6
            cv.put(x, y, pink_ramp, lvl, 0.4)
    # brillantor de plàstic
    for x, y in ((166, 20), (167, 19), (168, 19), (165, 21), (165, 22)):
        cv.put(x, y, PINK, 5.6, 0)
    if not night:
        cv.glow(HX, HY, 30, (255, 120, 190), 0.32)
    else:
        cv.glow(HX, HY, 18, (200, 70, 150), 0.25)

    # ─── Finestreta amb la Terra (308..365 × 21..79) ──────────────────────────
    PX, PY, PR = 336, 50, 27
    for y in range(PY - PR - 1, PY + PR + 2):
        for x in range(PX - PR - 1, PX + PR + 2):
            d = math.hypot(x - PX, y - PY)
            if d > PR + 0.5:
                continue
            a = math.atan2(y - PY, x - PX)
            if d > PR - 1.2:
                cv.put(x, y, STEEL, 1.0)
            elif d > 20.5:
                # anella gruixuda: bisellada (llum de dalt)
                lvl = 3.4 - math.sin(a) * 1.2 + (0.6 if d < 22 else 0)
                cv.put(x, y, STEEL, lvl)
            elif d > 19.3:
                cv.put(x, y, STEEL, 0.6)
    # vuit cargols a l'anella
    for i in range(8):
        a = i * math.pi / 4 + math.pi / 8
        bolt(cv, PX + math.cos(a) * 24, PY + math.sin(a) * 24, STEEL, 4.0, 1.3)
    # l'espai
    stars = random.Random(19)
    STARS = {(stars.randint(PX - 19, PX + 19), stars.randint(PY - 19, PY + 19)): stars.random() for _ in range(34)}
    EX, EY, ER = 342, 55, 7.5
    for y in range(PY - 19, PY + 20):
        for x in range(PX - 19, PX + 20):
            if math.hypot(x - PX, y - PY) > 19.2:
                continue
            de = math.hypot(x - EX, y - EY)
            if de <= ER:
                # la Terra: blava i petita, amb continents, núvols i el terminador
                nx, ny = (x - EX) / ER, (y - EY) / ER
                shade = 3.6 - nx * 1.4 - ny * 0.9 - (nx * nx + ny * ny) * 0.8
                land = math.sin(nx * 3.4 + 0.6) + math.cos(ny * 4.2 - nx * 1.6) > 1.25
                cloud = hr(x // 2, y, 81) > 0.8 and abs(ny) < 0.8
                if nx * 0.8 + ny * 0.5 > 0.75:
                    cv.put(x, y, NAVY, 1.4, 0)                           # costat de nit
                elif cloud:
                    cv.put(x, y, PAPER, shade + 1.6, 0)
                elif land:
                    cv.put(x, y, LAMPG, shade, 0)
                else:
                    cv.put(x, y, CYAN, shade - 1.2, 0)
            elif de <= ER + 1.2:
                cv.put(x, y, CYAN, 3.2 if (x - EX) + (y - EY) < 2 else 1.4, 0)  # atmosfera
            else:
                lvl = 1.0 + max(0, 1 - de / 26) * 1.6
                cv.put(x, y, SPACE, lvl, 0)
                s = STARS.get((x, y))
                if s is not None and de > 13:
                    cv.flat(x, y, (230, 232, 255) if s > 0.6 else (130, 136, 190))
    # reflex al vidre
    for i in range(7):
        cv.put(326 + i, 41 - i // 2 - (1 if i > 4 else 0), CYAN, 4.4, 0)
    cv.put(325, 44, CYAN, 3.6, 0)
    cv.put(345, 66, CYAN, 3.0, 0)
    cv.put(347, 65, CYAN, 3.0, 0)
    cv.glow(PX, PY, 40, (90, 150, 255), 0.14 if not night else 0.22)

    # ─── Rètol estarcit a la paret ────────────────────────────────────────────
    text(cv, 'MODUL C', 76, 44, STEEL, 1.6, worn=0.2)

    # ─── Panell rovellat (marc a la paret; la tapa tancada) ───────────────────
    panel_frame(cv)
    panel_cover(cv, 0, 0)
    # regalims de rovell per sota el panell
    for x in range(244, 281):
        if hr(x, 61) > 0.72:
            ln = int(4 + hr(x, 62) * 18)
            for y in range(126, 126 + ln):
                if hr(x, y, 63) > (y - 126) / ln:
                    cv.put(x, y, RUST, 1.6 + hr(x, 64) * 0.8)

    # ─── Esquerda a la paret (201..223 × 87..117) ─────────────────────────────
    CRACK = [(207, 89), (209, 93), (208, 96), (211, 99), (210, 102), (213, 105), (212, 108), (215, 111), (214, 114)]
    for (xa, ya), (xb, yb) in zip(CRACK, CRACK[1:]):
        cv.line(xa, ya, xb, yb, GRIME, 0.0, 0)
        cv.line(xa + 1, ya, xb + 1, yb, STEEL, 1.6)
        cv.line(xa - 1, ya, xb - 1, yb, STEEL, 4.2)
    for (xa, ya), (xb, yb) in (((209, 93), (204, 91)), ((211, 99), (217, 97)), ((217, 97), (219, 94)), ((213, 105), (218, 107))):
        cv.line(xa, ya, xb, yb, GRIME, 1.0, 0)
    # el forat on hi ha encastada la nota (fosc)
    cv.rect(210, 100, 212, 103, GRIME, 0.0, 0)
    cv.put(209, 101, STEEL, 4.4)

    # ─── Reixa del conducte, arran de terra (81..139 × 111..150) ──────────────
    vent_hole(cv)            # sota la reixa, perquè la reixa oberta hi encaixi
    vent_grille(cv, 84, 114)

    # ─── Llitera de dos pisos (368..472 × 62..172) ────────────────────────────
    bunk(cv, night)

    # ─── Tallets de la paret: decorat ─────────────────────────────────────────
    # (l'ombra de la llitera i de la porta a la paret)
    cv.darken(66, 49, 70, 157, lambda x, y: 1 - (x - 66) / 5)

    # ─── Decorat: càmera de la MARE i rascades al terra ───────────────────────
    # càmera de vigilància al racó del sostre (la MARE ho veu tot)
    cv.rect(98, 19, 104, 21, STEEL, 3.0)
    cv.vline(101, 22, 24, STEEL, 2.0)
    cv.disc(101, 27, 5, 3.4, STEEL, lambda nx, ny: 3.6 - nx - ny * 1.2)
    cv.disc(99.5, 28, 1.6, 1.4, NAVY, 0.6, 0)
    cv.put(99, 27, CYAN, 3.4, 0)
    cv.put(104, 26, [(255, 60, 60)], 0, 0)
    cv.glow(104, 26, 4, (255, 60, 60), 0.5)
    # rascades i un camí gastat al terra, de la porta a la llitera
    for y in range(166, 205):
        for x in range(40, 440):
            w = math.sin(x / 70.0) * 4 + 182
            if abs(y - w) < 7 and hr(x // 2, y, 91) > 0.82:
                o = cv.get(x, y)
                cv.P[x, y] = tuple(min(255, int(c * 1.18 + 4)) for c in o[:3]) + (255,)
    sc = random.Random(77)
    for _ in range(26):
        x, y = sc.randint(20, 460), sc.randint(165, 204)
        ln = sc.randint(3, 9)
        for k in range(ln):
            cv.put(x + k, y + (k * sc.choice((0, 1)) // 4), DECK, 4.2)

    # ─── Llums de color sobre el conjunt ──────────────────────────────────────
    if not night:
        cv.glow(244, 14, 110, (200, 235, 255), 0.2)
        cv.tint(150, 14, 205, 70, (255, 110, 180), lambda x, y: max(0, 1 - math.hypot(x - HX, y - HY) / 34) * 0.18)
        cv.tint(290, 20, 380, 100, (80, 140, 255), lambda x, y: max(0, 1 - math.hypot(x - PX, y - PY) / 45) * 0.12)


# ─── Peces (també les fan servir els props) ───────────────────────────────────

PANEL_O = (239, 79, 284, 125)     # marc del panell
COVER = (243, 83, 280, 121)       # la tapa


def panel_frame(cv):
    x0, y0, x1, y1 = PANEL_O
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            d = min(x - x0, x1 - x, y - y0, y1 - y)
            if d > 3:
                continue
            lvl = [0.6, 2.6, 1.8, 0.2][d]
            if d in (1, 2) and (x - x0 > x1 - x or y - y0 > y1 - y):
                lvl -= 0.8
            lvl += (hr(x, y, 31) - 0.5) * 0.9
            cv.put(x, y, RUST, lvl)
    for cx, cy in ((x0 + 1, y0 + 1), (x1 - 2, y0 + 1), (x0 + 1, y1 - 2), (x1 - 2, y1 - 2)):
        rivet(cv, cx, cy, RUST, 3.0)


def _rust_plate(cv, x0, y0, x1, y1, dx=0, dy=0, missing=(), dent=None):
    """La tapa del panell: ferro vell de la fàbrica, rovellat, amb nervis i quatre cargols."""
    X0, Y0, X1, Y1 = x0 + dx, y0 + dy, x1 + dx, y1 + dy
    for y in range(Y0, Y1 + 1):
        for x in range(X0, X1 + 1):
            u, v = x - X0, y - Y0
            n = hr(x // 2 - dx, y // 2 - dy, 33)
            lvl = 2.0 + (n - 0.5) * 0.7 - v / (Y1 - Y0) * 0.5
            if u == 0 or v == 0:
                lvl = 3.4
            elif u == X1 - X0 or v == Y1 - Y0:
                lvl = 0.4
            elif 6 <= u <= X1 - X0 - 6 and 9 <= v <= Y1 - Y0 - 9:
                # nervis horitzontals en relleu (fan de reixeta)
                k = (v - 9) % 5
                lvl = [3.0, 2.2, 1.8, 0.5, 1.6][k] + (n - 0.5) * 0.5
            if dent:
                dd = math.hypot(x - dent[0] - dx, (y - dent[1] - dy) * 1.2)
                if dd < 5:
                    lvl += (-(x - dent[0] - dx) - (y - dent[1] - dy)) / 5 * 0.9 - 0.4
            # taques de rovell més fosc i més clar
            m = hr(x // 3 - dx, y // 3 - dy, 34)
            if n > 0.94 or m > 0.92:
                lvl -= 1.1                                               # crostes de rovell fosc
            if m < 0.1:
                lvl += 1.0                                               # rovell viu, ataronjat
            cv.put(x, y, RUST, lvl)
    # estampat «ALDAIA» a la part de dalt
    text(cv, 'ALDAIA', X0 + 7, Y0 + 2, RUST, 0.4, worn=0.15)
    text(cv, 'ALDAIA', X0 + 7, Y0 + 3, RUST, 2.8, worn=0.5)
    for i, (cx, cy) in enumerate(((X0 + 3, Y0 + 3), (X1 - 3, Y0 + 3), (X0 + 3, Y1 - 3), (X1 - 3, Y1 - 3))):
        if i in missing:
            cv.disc(cx, cy, 1.4, 1.4, GRIME, 0.0, 0)
        else:
            bolt(cv, cx, cy, IRON, 3.4, 1.6)


def panel_cover(cv, dx, dy):
    _rust_plate(cv, *COVER, dx=dx, dy=dy)


def vent_hole(cv):
    """L'interior del conducte: fosc, en perspectiva, amb la marca de l'Iri a la paret de dins."""
    x0, y0, x1, y1 = 86, 116, 135, 148
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            # fons del conducte cap a la dreta (el conducte gira cap a l'hangar)
            ix0, iy0, ix1, iy1 = 104, 124, 128, 141
            if ix0 <= x <= ix1 and iy0 <= y <= iy1:
                lvl = 0.2
            elif y > iy1 and x0 + (y - iy1) * 0 <= x:
                lvl = 1.2 - (y1 - y) * 0.05                               # terra del conducte
            elif x < ix0:
                lvl = 1.6 - (ix0 - x) / 18 * 0.8                         # paret esquerra del conducte
            elif y < iy0:
                lvl = 0.8
            else:
                lvl = 0.6
            cv.put(x, y, GRIME, lvl * 0.9, 0)
    # la marca de l'Iri: una I. i una clau anglesa, gravades a la paret esquerra del conducte
    M = RUST
    cv.vline(90, 122, 133, M, 3.4, 0)
    cv.vline(91, 122, 133, M, 2.4, 0)
    cv.put(93, 133, M, 3.4, 0)
    cv.line(96, 135, 100, 127, M, 3.0, 0)
    cv.ring(101.5, 124.5, 2.4, M, 3.0, 0, step=30)
    # i la fletxa, cap endins
    cv.hline(105, 116, 144, M, 3.0, 0)
    cv.line(113, 141, 116, 144, M, 3.0, 0)
    cv.line(113, 147, 116, 144, M, 3.0, 0)


def vent_grille(cv, x0, y0, w=54, h=37):
    """La reixa: ferro rovellat, lamel·les, quatre cargols. (x0, y0) cantonada de dalt a l'esquerra."""
    x1, y1 = x0 + w - 1, y0 + h - 1
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            u, v = x - x0, y - y0
            n = hr(x - x0, y - y0, 51)
            if u < 3 or v < 3 or u > w - 4 or v > h - 4:
                lvl = [0.6, 3.0, 2.0, 1.6][min(u, v, 3)] if (u < 3 or v < 3) else [0.4, 0.8, 1.2][min(w - 1 - u, h - 1 - v, 2)]
            else:
                k = (v - 3) % 5
                lvl = [2.8, 2.2, 1.4, 0.4, 0.2][k]                       # lamel·la inclinada i buit
                if k >= 3:
                    cv.put(x, y, GRIME, 0.3 + (0.6 if n > 0.8 else 0), 0.2)
                    continue
            lvl += (n - 0.5) * 0.8
            if n > 0.94 or hr((x - x0) // 3, (y - y0) // 2, 55) > 0.93:
                lvl -= 1.1
            cv.put(x, y, RUST, lvl)
    for cx, cy in ((x0 + 1, y0 + 1), (x1 - 2, y0 + 1), (x0 + 1, y1 - 2), (x1 - 2, y1 - 2)):
        rivet(cv, cx, cy, IRON, 2.6)


def bunk(cv, night):
    FL, FR = 369, 466          # pals del davant (x esquerra)
    BL, BR = 376, 473          # pals del darrere
    # ombra al terra i a la paret
    cv.darken(BL - 2, FLOOR_Y, BR + 4, 162, lambda x, y: 0.7 - (y - FLOOR_Y) * 0.12, dither=False)
    for y in range(162, 176):
        for x in range(FL - 2, FR + 8):
            a = 0.75 * max(0, 1 - abs(y - 167) / 9) * min(1, (x - FL + 3) / 6, (FR + 8 - x) / 6)
            o = cv.get(x, y)
            cv.P[x, y] = tuple(int(c * (1 - a * 0.6)) for c in o[:3]) + (255,)
    # pals del darrere
    for x in (BL, BR):
        cv.rect(x, 66, x + 2, 160, STEEL, lambda xx, yy: [2.6, 2.0, 1.2][xx - x])

    # escala i ratlles de dies a la paret (en Mos ho compta tot)
    for i in range(6):
        tx = 392 + i * 8
        for j in range(4):
            cv.vline(tx + j * 2 - 2, 99, 104, STEEL, 4.4)
        cv.line(tx - 3, 103, tx + 5, 100, STEEL, 4.8)
    for j in range(2):
        cv.vline(440 + j * 2, 99, 104, STEEL, 4.4)
    # una foto vella enganxada a la paret (de la Nura?)
    cv.rect(452, 90, 461, 101, PAPER, lambda x, y: 3.2 - (y - 90) * 0.06)
    cv.rect(453, 91, 460, 97, ORANGE, lambda x, y: 1.4 + (y - 91) * 0.1)
    cv.disc(456.5, 94, 1.6, 2, SKIN, 2.4)
    cv.rect(455, 89, 458, 90, MANILA, 4.0)                           # cinta adhesiva

    def tier(top):
        """Un pis: matalàs (gruix + superfície) i travesser del davant. top = y de la superfície."""
        # superfície del matalàs (en perspectiva, fins a la paret)
        for y in range(top - 3, top + 1):
            t = (y - top + 3) / 3
            xl, xr = BL + 2 - t * 6, BR - t * 6
            for x in range(round(xl), round(xr) + 1):
                cv.put(x, y, MATT, 3.0 + t * 0.8)
        # ombra a la paret, sota el pis
        cv.darken(FL, top + 12, BR + 2, top + 34, lambda x, y: 0.8 - (y - top - 12) / 26, dither=False)
        # gruix del matalàs: vores arrodonides, ribet i ratlles de tela
        for y in range(top + 1, top + 8):
            for x in range(FL + 3, FR + 2):
                if (x in (FL + 3, FR + 1)) and y in (top + 1, top + 7):
                    continue
                lvl = 3.0 - (y - top - 1) * 0.18 + (0.3 if x % 4 == 0 else 0)
                if y == top + 1:
                    lvl += 1.0
                elif y == top + 2:
                    lvl += 0.5
                if y == top + 7:
                    lvl -= 1.2
                if x == FL + 3:
                    lvl += 0.6
                cv.put(x, y, MATT, lvl)
        # travesser d'acer
        cv.rect(FL, top + 8, FR + 3, top + 11, STEEL, lambda x, y: [4.8, 3.8, 2.8, 1.0][y - top - 8])
        # el somier de molles, que es veu per sota el travesser
        for x in range(FL + 4, FR + 1):
            k = (x - FL) % 6
            yy = top + 12 + (k if k < 3 else 6 - k)
            cv.put(x, yy, STEEL, 3.4)
            cv.put(x, yy + 1, STEEL, 1.4)
        cv.hline(FL + 3, FR + 1, top + 16, STEEL, 2.4)

    # pis de dalt (el d'en Mos)
    tier(77)
    # manta d'en Mos, rebregada i amb el coixí
    for y in range(70, 86):
        for x in range(398, 446):
            s = math.sin((x - 398) / 5.0 + (y - 70) / 4.0)
            top = 76 - math.sin((x - 398) / 48 * math.pi) * 4 - (2 if 410 < x < 420 else 0)
            if y >= top:
                lvl = 2.6 + s * 0.6 - (y - top) * 0.05 + (1.0 if y == math.ceil(top) else 0)
                cv.put(x, y, MATT, lvl + 0.2 - (0.6 if y > 84 else 0))
    cv.disc(453, 73, 9, 3.6, SHEET, lambda nx, ny: 3.8 - nx * 0.4 - ny * 1.2)
    # pis de baix (el de la Vet)
    tier(127)
    # el coixí de la Vet (el fullet treu el nas per sota)
    cv.disc(451, 123, 11, 4.2, SHEET, lambda nx, ny: 4.0 - nx * 0.4 - ny * 1.2)
    cv.hline(441, 461, 127, SHEET, 1.4)
    # manta plegada als peus
    cv.rect(384, 120, 404, 126, NAVY, lambda x, y: 3.0 - (y - 120) * 0.15 + (0.6 if y in (120, 123) else 0))
    cv.hline(384, 404, 127, NAVY, 1.0)
    # pals del davant i escala
    for x in (FL, FR):
        cv.rect(x, 64, x + 3, 173, STEEL, lambda xx, yy: [4.4, 3.6, 2.6, 1.2][xx - x] - (0.6 if yy > 165 else 0))
        cv.rect(x - 1, 62, x + 4, 64, STEEL, lambda xx, yy: 4.6 - (yy - 62) * 0.8)
        cv.rect(x - 1, 171, x + 4, 173, STEEL, 1.6)
    for y in range(96, 128, 8):
        cv.hline(FL + 4, FL + 10, y, STEEL, 3.8)
        cv.hline(FL + 4, FL + 10, y + 1, STEEL, 1.4)
    cv.rect(FL + 10, 90, FL + 11, 130, STEEL, lambda x, y: 3.4 - (x - FL - 10) * 1.6)
    # sota el llit: unes espardenyes de presó i una caixa
    cv.rect(420, 154, 446, 166, PANEL, lambda x, y: 2.4 - (y - 154) * 0.06 + (1.2 if y == 154 else 0))
    cv.hline(420, 446, 167, PANEL, 0.6)
    cv.rect(428, 158, 438, 160, PANEL, 1.0)
    for sx in (393, 401):
        cv.disc(sx, 166, 3.4, 1.5, ORANGE, lambda nx, ny: 2.4 - ny)
        cv.put(sx - 1, 165, ORANGE, 3.6)


# ─── Props ────────────────────────────────────────────────────────────────────

def p_avis(cv):
    """L'avís de reciclatge, a terra, passat per sota la porta."""
    pts = [(75, 178), (99, 174), (102, 186), (77, 190)]
    contact_shadow(cv, 76, 102, 187, 191, 0.0)
    cv.poly([(76, 180), (101, 176), (103, 188), (78, 191)], GRIME, 0.0, 0)   # ombra
    cv.poly(pts, PAPER, lambda x, y: 4.0 + (x - 75) / 26 * 0.4 - (y - 174) / 16 * 0.3)
    for i, ln in enumerate((16, 18, 12)):
        yy = 179 + i * 3
        for k in range(ln):
            x = 79 + k
            y = yy - round(k * 0.17)
            if hr(x, y, 71) > 0.25:
                cv.put(x, y, PAPER, 1.6)
    # el cor de la MARE a la capçalera
    for x, y in ((92, 177), (94, 177), (91, 178), (92, 178), (93, 178), (94, 178), (95, 178), (92, 179), (93, 179), (94, 179), (93, 180)):
        cv.put(x, y, PINK, 3.2)
    cv.put(92, 177, PINK, 4.4)
    # plec
    cv.line(88, 176, 90, 189, PAPER, 3.2)


def p_escarabat(cv):
    """El Senyor Bigotis: escarabat lluent, amb unes antenes llargues i arrissades com un bigoti."""
    cx, cy = 132, 165
    cv.disc(cx + 1, cy + 4, 9, 1.8, GRIME, 0.0, 0)                          # ombra
    for k in (-4, 0, 4):                                                   # potes
        cv.put(cx + k, cy + 4, BEET, 0.6)
        cv.put(cx + k - 1, cy + 5, BEET, 0.4)
        cv.put(cx + k + 1, cy + 5, BEET, 0.4)
    cv.disc(cx + 1, cy, 7, 4.4, BEET, lambda nx, ny: 2.8 - nx * 0.7 - ny * 1.5)
    cv.vline(cx + 1, cy - 4, cy + 4, BEET, 0.4)                             # separació dels èlitres
    for x, y in ((cx - 2, cy - 3), (cx - 1, cy - 3), (cx, cy - 2), (cx + 3, cy - 3), (cx + 4, cy - 3)):
        cv.put(x, y, BEET, 5.0)                                            # reflex lluent
    cv.disc(cx - 6.5, cy + 0.5, 2.4, 2.2, BEET, lambda nx, ny: 1.8 - ny)   # cap
    cv.put(cx - 7, cy - 1, BEET, 4.0)
    # el «bigoti»: dues antenes llargues i arrissades
    for x, y in ((cx - 9, cy - 1), (cx - 10, cy - 2), (cx - 11, cy - 3), (cx - 12, cy - 3), (cx - 13, cy - 2),
                 (cx - 13, cy - 1), (cx - 12, cy), (cx - 9, cy + 2), (cx - 10, cy + 3), (cx - 11, cy + 4),
                 (cx - 12, cy + 4), (cx - 13, cy + 3), (cx - 13, cy + 2)):
        cv.put(x, y, BEET, 3.2)


def p_safata(cv):
    """Safata de sopar amb la sopa de reinserció: verda i fent bombolles."""
    contact_shadow(cv, 320, 356, 180, 185, 0.9)
    cv.poly([(322, 171), (354, 171), (357, 181), (319, 181)], PANEL, lambda x, y: 3.6 - (y - 171) * 0.04)
    cv.poly([(325, 172), (351, 172), (353, 179), (323, 179)], PANEL, 2.8)       # fons de la safata
    cv.hline(319, 357, 182, PANEL, 1.4)
    cv.hline(319, 357, 183, PANEL, 0.6)
    cv.hline(322, 354, 171, PANEL, 5.0)
    # bol
    cv.disc(339, 176, 9, 3.6, PANEL, lambda nx, ny: 5.0 - ny * 1.2 - nx * 0.4)
    cv.rect(331, 176, 347, 179, PANEL, lambda x, y: 4.0 - (x - 331) * 0.15)
    cv.disc(339, 179, 8, 1.6, PANEL, lambda nx, ny: 2.0 - nx)
    cv.disc(339, 175.5, 7.4, 2.5, LIME, lambda nx, ny: 3.0 + ny * 0.6 - nx * 0.4, 0.4)
    for x, y, r in ((336, 175, 1.0), (341, 174, 1.4), (343, 176, 0.8)):
        cv.disc(x, y, r, r, LIME, 4.6, 0.3)
    # bombolles que pugen
    for x, y in ((338, 170), (342, 167), (339, 164)):
        cv.ring(x, y, 1.5, LIME, 3.6, 0.2, step=30)
        cv.put(x - 1, y - 1, LIME, 5.4, 0)
    # cullera i un tros de pa
    cv.line(326, 178, 331, 174, PANEL, 4.4)
    cv.disc(350.5, 174.5, 2.5, 1.5, MANILA, lambda nx, ny: 3.4 - ny)
    cv.glow(339, 174, 10, (150, 220, 90), 0.25)


def p_panell_afluixat(cv):
    """La tapa, afluixada pel cop de puny: desplaçada, un cargol menys i el bony del cop."""
    x0, y0, x1, y1 = COVER
    # escletxa fosca on era la tapa
    cv.rect(x0, y0, x1, y1, GRIME, 0.0, 0)
    _rust_plate(cv, x0, y0, x1, y1, dx=2, dy=3, missing=(0,), dent=(262, 102))
    # el cargol que ha saltat, penjant del forat
    cv.put(243, 128, IRON, 3.4)


def _console(cv, lit):
    """El forat del panell amb la consola vella a dins (i la tapa recolzada a terra)."""
    x0, y0, x1, y1 = COVER
    # el buit de darrere: una petita cambra fosca
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            d = min(x - x0, x1 - x, y - y0, y1 - y)
            lvl = 0.3 + min(d, 5) * 0.08 + (0.6 if (y - y0) < 2 else 0)
            cv.put(x, y, GRIME, lvl * 1.4, 0.3)
    # canonades de coure, al fons del buit
    cv.hline(x0 + 3, x1 - 3, y0 + 5, COPPER, 1.4, 0.3)
    cv.hline(x0 + 3, x1 - 3, y0 + 6, COPPER, 0.6, 0.3)
    # consola: caixa de ferro amb tauler de llautó
    cx0, cy0, cx1, cy1 = 246, 96, 277, 119
    cv.rect(cx0, cy0, cx1, cy1, IRON, lambda x, y: 2.6 - (y - cy0) * 0.03)
    cv.hline(cx0, cx1, cy0, IRON, 4.6)
    cv.vline(cx0, cy0, cy1, IRON, 3.8)
    cv.vline(cx1, cy0, cy1, IRON, 1.0)
    cv.hline(cx0, cx1, cy1, IRON, 0.8)
    cv.rect(cx0 + 2, cy0 + 2, cx1 - 2, cy0 + 3, GOLD, lambda x, y: 3.4 - (y - cy0 - 2))
    # rellotge (manòmetre)
    cv.disc(255, 108, 6.2, 6.2, GOLD, lambda nx, ny: 3.6 - nx - ny)
    cv.disc(255, 108, 4.8, 4.8, PAPER, lambda nx, ny: 4.6 - ny * 0.5 - nx * 0.3)
    for a in range(200, 341, 35):
        cv.put(255 + round(math.cos(math.radians(a)) * 4), 108 + round(math.sin(math.radians(a)) * 4), PAPER, 1.2)
    ang = math.radians(300 if lit else 215)
    for r in range(0, 4):
        cv.flat(255 + round(math.cos(ang) * r), 108 + round(math.sin(ang) * r), (170, 30, 30))
    cv.flat(255, 108, (40, 30, 30))
    # forat de la palanca
    cv.rect(266, 98, 271, 103, GRIME, 0.0, 0)
    cv.hline(266, 271, 104, IRON, 4.0)
    # tres llums
    for i, lx in enumerate((265, 269, 273)):
        on = lit and i == 0
        if on:
            cv.disc(lx, 113, 1.6, 1.6, LAMPG, 6, 0)
        else:
            cv.disc(lx, 113, 1.6, 1.6, RED if i == 2 else LAMPG, 0.6, 0.2)
            cv.put(lx - 1, 112, PAPER, 1.6, 0.2)
    # cargols de la consola
    for bx, by in ((cx0 + 2, cy1 - 2), (cx1 - 2, cy1 - 2)):
        cv.put(bx, by, IRON, 4.0)
    # la tapa, a terra, recolzada a la paret (la mateixa planxa, una mica escurçada)
    cv.darken(326, 126, 331, 157, lambda x, y: 0.8 - (x - 326) * 0.15, dither=False)    # ombra a la paret
    _rust_plate(cv, 290, 124, 327, 158)
    cv.vline(328, 125, 159, RUST, 0.4)                                          # gruix de la planxa
    cv.hline(290, 328, 159, RUST, 0.2)
    contact_shadow(cv, 288, 330, 160, 163, 0.9)


def p_panell_obert(cv):
    _console(cv, False)


def p_panell_reparat(cv):
    _console(cv, True)
    # la clau anglesa, fent de palanca: reluent, de ferro-9 (acer blavós)
    WR = ramp((24, 30, 46), (62, 78, 104), (112, 136, 166), (168, 194, 220), (220, 236, 248), (250, 254, 255), n=6)
    x0, y0, x1, y1 = 268.5, 101, 276.5, 71
    n = 32
    for i in range(n + 1):
        t = i / n
        x, y = round(x0 + (x1 - x0) * t), round(y0 + (y1 - y0) * t)
        cv.put(x - 1, y, WR, 4.4)
        cv.put(x, y, WR, 3.2)
        cv.put(x + 1, y, WR, 1.6)
    cv.put(268, 100, WR, 1.0)
    # cap ajustable: boca oberta cap amunt i el cargol sens fi
    HX, HY = 278, 66
    for y in range(HY - 6, HY + 6):
        for x in range(HX - 6, HX + 6):
            nx, ny = (x - HX) / 5.6, (y - HY) / 5.2
            if nx * nx + ny * ny > 1:
                continue
            if -1.5 <= x - HX <= 1.5 and y < HY + 1:
                continue                                                      # la boca
            cv.put(x, y, WR, 3.6 - nx * 1.4 - ny * 1.2)
    cv.vline(HX - 2, HY - 5, HY, WR, 5.0)
    cv.vline(HX + 2, HY - 5, HY, WR, 1.4)
    for k in range(3):
        cv.put(HX - 3 + k * 2, HY + 3, WR, 1.0)                              # cargol sens fi
    cv.glow(275, 74, 16, (170, 220, 255), 0.16)
    # la llumeta verda encesa
    cv.glow(265, 113, 14, (90, 240, 120), 0.6)
    cv.put(264, 112, [(230, 255, 235)], 0, 0)


def p_panell_sincronitzat(cv):
    """Sense la clau anglesa: la cambra de la I. ho sincronitza tot sola. La consola, viva i tranquil·la."""
    _console(cv, True)
    x0, y0, x1, y1 = COVER
    # lluïssor cian que surt del buit de darrere, per les vores de la consola
    for y in range(y0 + 1, y1):
        for x in range(x0 + 1, x1):
            if 246 <= x <= 277 and 96 <= y <= 119:
                continue
            d = math.hypot((x - 261) / 24, (y - 106) / 22)
            a = max(0.0, 1 - d) * 1.6
            if a > B4[y & 3][x & 3] * 0.8:
                cv.put(x, y, TEAL, 0.6 + a * 2.2, 0)
    # contrallum cian a les vores de la caixa de la consola
    for x in range(247, 277):
        cv.put(x, 95, TEAL, 4.0 + hr(x, 3), 0)
    for y in range(97, 119):
        cv.put(245, y, TEAL, 4.2 - (y - 97) * 0.1, 0)
        cv.put(278, y, TEAL, 3.4 - (y - 97) * 0.1, 0)
    # l'agulla, més enllà: a la zona verda
    cv.disc(255, 108, 4.8, 4.8, PAPER, lambda nx, ny: 4.6 - ny * 0.5 - nx * 0.3)
    for a in range(200, 341, 35):
        cv.put(255 + round(math.cos(math.radians(a)) * 4), 108 + round(math.sin(math.radians(a)) * 4), PAPER, 1.2)
    for a in range(300, 341, 10):
        cv.flat(255 + round(math.cos(math.radians(a)) * 4), 108 + round(math.sin(math.radians(a)) * 4), (60, 170, 80))
    ang = math.radians(318)
    for r in range(0, 4):
        cv.flat(255 + round(math.cos(ang) * r), 108 + round(math.sin(ang) * r), (170, 30, 30))
    cv.flat(255, 108, (40, 30, 30))
    # el forat de la palanca, buit (ja no cal)
    cv.rect(266, 98, 271, 103, GRIME, 0.0, 0)
    cv.rect(267, 99, 270, 100, TEAL, 0.8, 0)                          # el cian de dins, pel forat
    # els tres llums encesos, en verd
    for lx in (265, 269, 273):
        cv.disc(lx, 113, 1.6, 1.6, LAMPG, 6, 0)
        cv.put(lx - 1, 112, [(230, 255, 235)], 0, 0)
    cv.glow(269, 113, 18, (90, 240, 120), 0.5)
    cv.glow(261, 104, 30, (110, 230, 240), 0.18)


def p_reixa_oberta(cv):
    """La reixa, treta i recolzada a la paret; a dins, la marca de l'Iri i una fletxa."""
    # el marc de la reixa queda: el forat (ja dibuixat al fons, sota la reixa)
    tmp_x0, tmp_y0 = 84, 114
    vent_hole(cv)
    # restes del marc (els forats dels cargols, rovellats)
    for x in range(tmp_x0, tmp_x0 + 54):
        cv.put(x, tmp_y0, RUST, 1.6)
        cv.put(x, tmp_y0 + 1, RUST, 2.4)
    for y in range(tmp_y0, tmp_y0 + 37):
        cv.put(tmp_x0, y, RUST, 1.6)
        cv.put(tmp_x0 + 1, y, RUST, 2.4)
        cv.put(tmp_x0 + 53, y, RUST, 1.2)
    # la reixa, recolzada dreta contra la paret (girada: les lamel·les queden verticals; s'hi veu la paret)
    gx0, gy0, gw, gh = 143, 105, 37, 53
    cv.darken(gx0 + gw, gy0 + 2, gx0 + gw + 4, gy0 + gh, lambda x, y: 0.8 - (x - gx0 - gw) * 0.18, dither=False)
    for y in range(gy0, gy0 + gh):
        for x in range(gx0, gx0 + gw):
            u, v = x - gx0, y - gy0
            n = hr(u, v, 52)
            if u < 3 or v < 3 or u > gw - 4 or v > gh - 4:
                lvl = [0.6, 3.0, 2.0, 1.6][min(u, v, 3)] if (u < 3 or v < 3) else [0.4, 0.8, 1.2][min(gw - 1 - u, gh - 1 - v, 2)]
            else:
                k = (u - 3) % 5
                if k >= 3:
                    if k == 3:
                        cv.put(x, y, GRIME, 0.6, 0)                         # ombra de la lamel·la; després, la paret
                    continue
                lvl = [2.8, 2.0, 1.2][k]
            lvl += (n - 0.5) * 0.8
            if n > 0.94:
                lvl -= 1.1
            cv.put(x, y, RUST, lvl)
    for cx, cy in ((gx0 + 1, gy0 + 1), (gx0 + gw - 3, gy0 + 1), (gx0 + 1, gy0 + gh - 3), (gx0 + gw - 3, gy0 + gh - 3)):
        cv.put(cx, cy, GRIME, 0.0, 0)                                         # forats dels cargols, buits
        cv.put(cx + 1, cy, GRIME, 0.0, 0)
    contact_shadow(cv, gx0, gx0 + gw, gy0 + gh, gy0 + gh + 3, 0.9)


def p_esquerda(cv):
    """La nota de la interna 4, plegada i encastada a l'esquerda."""
    cv.poly([(209, 99), (215, 97), (216, 102), (210, 104)], MANILA, lambda x, y: 3.6 - (y - 97) * 0.15)
    cv.line(210, 100, 215, 98, MANILA, 5.0)
    cv.line(211, 103, 216, 101, MANILA, 2.4)
    cv.put(212, 101, MANILA, 2.6)


def p_fullet(cv):
    """El fullet de reeducació, que treu el nas per sota el coixí de la llitera de baix."""
    cv.poly([(428, 127), (446, 125), (447, 131), (429, 133)], PAPER, lambda x, y: 4.6 - (y - 125) * 0.12)
    cv.hline(429, 446, 133, PAPER, 1.4)
    # portada: el cor de la MARE i el títol
    for x, y in ((432, 128), (434, 128), (431, 129), (432, 129), (433, 129), (434, 129), (435, 129), (432, 130), (433, 130), (434, 130), (433, 131)):
        cv.put(x, y, PINK, 3.4)
    for k in range(7):
        cv.put(438 + k, 128 - k // 6, TEAL, 2.4)
        if k % 2:
            cv.put(438 + k, 130 - k // 6, PAPER, 2.0)
    # l'ombra del coixí que hi cau a sobre
    cv.darken(440, 125, 447, 127, 0.6)


PROPS = {
    'avis': p_avis,
    'escarabat': p_escarabat,
    'safata': p_safata,
    'panell_afluixat': p_panell_afluixat,
    'panell_obert': p_panell_obert,
    'panell_reparat': p_panell_reparat,
    'panell_sincronitzat': p_panell_sincronitzat,
    'reixa_oberta': p_reixa_oberta,
    'esquerda': p_esquerda,
    'fullet': p_fullet,
}
