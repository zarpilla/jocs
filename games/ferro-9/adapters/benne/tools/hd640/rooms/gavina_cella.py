"""
Cel·la 9 de La Gavina (Acte 1, Vet) a 640×360 (vegeu hd/rooms/gavina_cella.py, la de 480×270): acer fred i net,
amb peces velles i rovellades de la fàbrica (el panell, la reixa, el pany) encastades a la paret. Llums: el
fluorescent del sostre, el cor rosa de la MARE i la Terra a la finestreta.
  - la mateixa composició ×4/3, dibuixada de nou: les planxes de la paret amb reblons de debò (cúpula de 3×3),
    un brunyit horitzontal molt suau i regalims de brutícia; el terra de planxes en perspectiva amb el mateix
    punt de fuga i el desguàs amb lamel·les;
  - rètols estarcits llegibles («C-9», «MODUL C», «ALDAIA» a la tapa) amb una lletra de 4×6;
  - la porta amb frontisses i la trapa del menjar amb el pestell; el pany Aldaia M-3 amb la pantalleta;
  - la finestreta amb la junta de goma, vuit cargols amb ranura i més estrelles; la Terra amb continents i núvols;
  - la llitera amb el somier de molles, la manta d'en Mos, el coixí de la Vet i les ratlles dels dies.
`bg(cv, night=True)` el fa servir el pròleg (la mateixa cel·la, de nit).

Animació `ambient`: el fons es parteix en el que és quiet (`_static`, a la memòria cau), el que es mou (`_dyn`:
el fluorescent, el cor que batega, els estels, el LED de la càmera) i uns retocs finals píxel a píxel que no
depenen del temps (`_post`: el halo del fluorescent). Cada fotograma només torna a pintar el que es mou
(vegeu `Ambient`), i el pròleg fa servir la mateixa màquina.
"""
import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

import math
import random
from functools import lru_cache

import numpy as np
from PIL import Image

from hd.pix import (Canvas, Light, B4, W, H, hr, mix, ramp, STEEL, PANEL, RUST, GOLD, PAPER, PINK, CYAN, TEAL,
                    SPACE, ORANGE, IRON, WARN, SKIN, MANILA, NAVY, RED, LAMPG, COPPER)
from hd.rooms.gavina_cella import DECK, MATT, SHEET, GRIME, LIME, BEET  # noqa: F401  (les rampes de 480)

LIGHT = Light(vignette=(107, 61), floor_fade=(261, 48))
LIGHT.point(325, 5, r=360, k=4.2, squash=0.8, power=2.0)            # fluorescent del sostre
LIGHT.add(lambda x, y: max(0.0, 1 - math.hypot((x - 315) / 200, (y - 248) / 45)) ** 1.2 * 1.6 if y > 209 else 0.0)  # bassal de llum al terra
LIGHT.point(235, 40, r=61, k=0.9)                                    # el cor de la MARE
LIGHT.point(448, 67, r=85, k=0.8)                                    # la finestreta

PINK_NIGHT = ramp((24, 8, 22), (60, 16, 44), (110, 34, 80), (160, 60, 120), n=6)
RUBBER = ramp((6, 6, 10), (16, 16, 22), (30, 30, 38), (48, 48, 58), n=4)

FLOOR_Y = 211          # línia paret-terra
VPX, VPY = 320, -200   # punt de fuga del terra

# Lletra d'estarcit de 4×6 (la I i el guió, de 3)
FONT = {
    'C': ['.###', '#...', '#...', '#...', '#...', '.###'],
    '9': ['.##.', '#..#', '#..#', '.###', '...#', '.##.'],
    '-': ['...', '...', '###', '...', '...', '...'],
    'M': ['#...#', '##.##', '#.#.#', '#...#', '#...#', '#...#'],
    'O': ['.##.', '#..#', '#..#', '#..#', '#..#', '.##.'],
    'D': ['###.', '#..#', '#..#', '#..#', '#..#', '###.'],
    'U': ['#..#', '#..#', '#..#', '#..#', '#..#', '.##.'],
    'L': ['#...', '#...', '#...', '#...', '#...', '####'],
    'A': ['.##.', '#..#', '#..#', '####', '#..#', '#..#'],
    'I': ['###', '.#.', '.#.', '.#.', '.#.', '###'],
    '3': ['###.', '...#', '.##.', '...#', '...#', '###.'],
    ' ': ['..'] * 6,
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
    """Rebló de cúpula, 3×3, amb la llum de dalt a l'esquerra."""
    for j, row in enumerate(((1.4, 1.0, -0.2), (0.8, 0.2, -1.0), (-0.4, -1.0, -1.8))):
        for i, d in enumerate(row):
            cv.put(x + i, y + j, rp, lvl + d)


def bolt(cv, cx, cy, rp, lvl, r=2.4, slot=None):
    """Cargol de cap rodó; `slot` (angle en graus) hi fa la ranura."""
    cv.disc(cx, cy, r, r, rp, lambda nx, ny: lvl - nx * 1.2 - ny * 1.4)
    cv.put(round(cx - r * 0.4), round(cy - r * 0.4), rp, lvl + 1.6)
    if slot is not None and r >= 1.8:
        a = math.radians(slot)
        for k in (-1, 0, 1):
            cv.put(round(cx + math.cos(a) * k), round(cy + math.sin(a) * k), rp, lvl - 2.2)


def contact_shadow(cv, x0, x1, y0, y1, k=0.9):
    """Ombra al terra sota un objecte: més fosca a dalt, a quadres cap avall i als costats."""
    for y in range(y0, y1 + 1):
        for x in range(x0 - 4, x1 + 5):
            a = k * (1 - (y - y0) / max(1, y1 - y0 + 1)) * (1 - max(0, max(x0 - x, x - x1)) / 5)
            if a > B4[y & 3][x & 3]:
                o = cv.get(x, y)
                if o[3]:
                    cv.P[x, y] = tuple(int(c * 0.6) for c in o[:3]) + (o[3],)


# ─── Ritmes de l'animació ─────────────────────────────────────────────────────

def _bump(u, c, w):
    """Pols triangular centrat a `c` (d'amplada `w`), 0 fora."""
    return max(0.0, 1 - abs(u - c) / w)


def heartbeat(t):
    """El cor de la MARE: dos batecs per cicle (lub-dub), suaus. 0 a t = 0."""
    u = (t * 2) % 1
    return _bump(u, 0.36, 0.1) + 0.6 * _bump(u, 0.56, 0.1)


# ─── Fons: la part quieta ─────────────────────────────────────────────────────

WALL_T, BAND_Y, WALL_B = 25, 165, 199
COLS = [0, 72, 157, 229, 301, 395, 469, 549, W]
ROWS = [WALL_T, 80, 136, BAND_Y]


def _ceiling(cv):
    cv.rect(0, 0, W - 1, 13, STEEL, lambda x, y: 1.0 + y * 0.09 + (0.5 if x % 53 == 0 else 0))
    for x in range(0, W, 53):
        cv.vline(x + 1, 0, 13, STEEL, 2.4)
        cv.vline(x + 2, 0, 13, STEEL, 1.6)
    cv.hline(0, W - 1, 14, STEEL, 4.0)
    cv.hline(0, W - 1, 15, STEEL, 3.2)
    cv.hline(0, W - 1, 16, STEEL, 2.0)
    cv.hline(0, W - 1, 17, STEEL, 0.4)
    # canal de cables al llarg de la paret (porta el cable fins al cor)
    cv.rect(0, 20, W - 1, 24, STEEL, lambda x, y: [3.8, 3.4, 3.0, 2.4, 1.2][y - 20])
    cv.hline(0, W - 1, 22, STEEL, lambda x, y: 2.6 if x % 6 < 3 else 3.0)          # la tapa del canal, ondulada
    for x in range(8, W, 43):
        cv.rect(x, 19, x + 3, 25, STEEL, lambda xx, yy: 4.4 - (xx - x) * 0.7 - (0.6 if yy == 25 else 0))
        cv.put(x + 1, 22, STEEL, 1.4)                                              # el cargol de la brida
    # la carcassa del fluorescent (el tub és a `_dyn`)
    cv.rect(259, 1, 392, 12, STEEL, lambda x, y: 2.0 - (y - 1) * 0.08)
    cv.hline(259, 392, 12, STEEL, 4.6)
    cv.hline(259, 392, 13, STEEL, 1.0)
    for x in (261, 390):
        cv.vline(x, 2, 11, STEEL, 3.4)


def _wall(cv):
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
        if x == x0 + 2 or y == y0 + 2:
            lvl += 0.35
        if x == x1:
            return lvl - 0.8
        if y == y1:
            lvl -= 0.4
        lvl += (hr(y, ci, ri, 8) - 0.5) * 0.14                           # brunyit horitzontal, molt suau
        # brutícia: regalims suaus cap avall
        g = hr(x // 4, ci, 7)
        if g > 0.86 and y > y0 + 8:
            lvl -= 0.35 * min(1, (y - y0) / 27)
        return lvl

    cv.rect(0, WALL_T, W - 1, BAND_Y - 1, STEEL, wall)
    # reblons al llarg de les juntes
    for ri in range(len(ROWS) - 1):
        for ci in range(len(COLS) - 1):
            x0, x1, y0, y1 = COLS[ci], COLS[ci + 1] - 1, ROWS[ri], ROWS[ri + 1] - 1
            n = max(2, round((x1 - x0) / 17))
            for k in range(n + 1):
                rx = round(x0 + 5 + (x1 - x0 - 12) * k / n)
                rivet(cv, rx, y0 + 4, STEEL, 2.6)
                if ri == len(ROWS) - 2:
                    rivet(cv, rx, y1 - 5, STEEL, 2.6)
    # ombra del canal de cables
    cv.darken(0, 25, W - 1, 29, lambda x, y: 1 - (y - 25) / 5)

    # franja pintada (verd blavós de presó) i sòcol fosc
    cv.hline(0, W - 1, BAND_Y, STEEL, 4.6)
    cv.hline(0, W - 1, BAND_Y + 1, STEEL, 3.8)
    cv.rect(0, BAND_Y + 2, W - 1, BAND_Y + 7, TEAL,
            lambda x, y: 2.7 - (y - BAND_Y - 2) * 0.15 + (0.5 if y == BAND_Y + 2 else 0)
            - (0.6 if hr(x // 4, y // 3, 3) > 0.86 else 0))                   # la pintura, amb esgrafiats
    cv.hline(0, W - 1, BAND_Y + 8, STEEL, 1.0)

    def kick(x, y):
        px = x % 80
        lvl = 2.0 - (y - BAND_Y - 9) * 0.015
        if px == 0:
            return 0.8
        if px == 1:
            return 2.8
        if (y - BAND_Y) % 12 == 0:
            lvl -= 0.4
        elif (y - BAND_Y) % 12 == 1:
            lvl += 0.25
        return lvl + (hr(x // 3, y // 6, 2) - 0.5) * 0.2

    cv.rect(0, BAND_Y + 9, W - 1, WALL_B, STEEL, kick)
    cv.hline(0, W - 1, WALL_B, STEEL, 4.0)
    cv.hline(0, W - 1, WALL_B + 1, STEEL, 3.2)
    cv.rect(0, WALL_B + 2, W - 1, FLOOR_Y - 1, STEEL, lambda x, y: 2.4 - (y - WALL_B - 2) * 0.2)


def _floor(cv):
    """Planxes en perspectiva (el mateix punt de fuga que a 480), amb el relleu antilliscant."""
    for y in range(FLOOR_Y, H):
        dep = y - VPY
        row = math.floor(4800 / dep / 2.3)
        row_up = math.floor(4800 / (dep - 1) / 2.3)
        row_up2 = math.floor(4800 / (dep - 2) / 2.3)
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
            elif row != row_up2:
                lvl += 0.5
            else:
                # textura de llàgrimes (planxa antilliscant) molt suau: ratlletes de 2 px, alternades
                if hr(col, row, 9) > 0.5 and y % 3 == 0 and ((x + (y // 3 % 2) * 3) % 6) < 2:
                    lvl += 0.35
            if y < FLOOR_Y + 8:
                lvl -= (FLOOR_Y + 8 - y) / 8 * 1.2                      # ombra de contacte amb la paret
            cv.put(x, y, DECK, lvl)
    # reblons a les cantonades de les planxes (només a la part visible)
    for y in range(FLOOR_Y + 2, 273):
        dep = y - VPY
        if math.floor(4800 / dep / 2.3) != math.floor(4800 / (dep - 4) / 2.3) and \
                math.floor(4800 / (dep - 3) / 2.3) == math.floor(4800 / (dep - 4) / 2.3):
            for c in range(-14, 15):
                x = round(VPX + (c + 0.12) * 3.2 * dep / 30) + 4
                if 0 <= x < W - 1:
                    cv.put(x, y, DECK, 4.2)
                    cv.put(x + 1, y, DECK, 3.0)
                    cv.put(x + 1, y + 1, DECK, 1.2)
    # desguàs al mig del terra
    cv.disc(275, 256, 15, 4.5, DECK, 0.5)
    cv.hline(263, 287, 252, DECK, 3.6)
    for x in range(264, 288, 3):
        cv.vline(x, 253, 259, DECK, 2.8)
        cv.vline(x + 1, 253, 259, DECK, 1.6)
    cv.hline(262, 288, 260, DECK, 3.0)


def _door(cv):
    """La porta de la cel·la (11..87 × 65..210), corredissa, amb el pany Aldaia M-3."""
    cv.rect(11, 65, 87, 210, STEEL, lambda x, y: 1.6 + (1.4 if x in (12, 13) or y in (66, 67) else 0) - (0.8 if x > 84 else 0))
    # bandes d'avís grogues i negres al marc
    for y in range(68, 209):
        for x in list(range(13, 19)) + list(range(79, 85)):
            k = ((x + y) // 5) % 2
            cv.put(x, y, WARN if k else STEEL, (2.8 if k else 0.8) - (0.5 if x in (18, 84) else 0))
    for x in range(13, 85):
        for y in range(68, 74):
            k = ((x + y) // 5) % 2
            cv.put(x, y, WARN if k else STEEL, (3.0 if k else 0.8) + (0.5 if y == 68 else 0))
    cv.vline(19, 74, 210, STEEL, 0.3)
    cv.hline(19, 78, 74, STEEL, 0.3)

    # fulla de la porta (corredissa), més vella que les planxes de la paret
    def door(x, y):
        lvl = 2.8 - abs(x - 40) / 40 * 0.6 + (hr(x // 2, 41) - 0.5) * 0.15
        if x == 20:
            return 4.2
        if x == 21:
            return 3.4
        if x == 78:
            return 1.0
        if x == 77:
            lvl -= 0.6
        # reforços horitzontals
        for ry in (117, 162):
            if ry <= y <= ry + 4:
                return [4.4, 3.8, 3.2, 2.4, 1.0][y - ry] + (hr(x // 3, ry, 42) - 0.5) * 0.3
        if y in (167, 168) and 24 <= x <= 74:
            return 1.5
        if hr(x, y // 3, 43) > 0.97:
            lvl -= 0.5                                                    # rascades verticals
        return lvl

    cv.rect(20, 75, 78, 207, STEEL, door)
    # finestreta amb barrots
    cv.rect(28, 84, 70, 110, STEEL, 0.6)
    cv.hline(28, 70, 84, STEEL, 0.2)
    cv.rect(29, 85, 69, 109, NAVY, lambda x, y: 1.0 + (y - 85) / 24 * 1.6, 0.2)    # el passadís, fosc
    cv.glow(48, 99, 19, (120, 60, 70), 0.25)                                     # llum vermella del passadís
    for x in range(32, 68, 5):
        cv.vline(x, 85, 109, STEEL, 4.0)
        cv.vline(x + 1, 85, 109, STEEL, 2.6)
        cv.vline(x + 2, 86, 109, NAVY, 0.2, 0)                                   # l'ombra del barrot
    cv.hline(28, 70, 111, STEEL, 4.2)
    cv.hline(28, 70, 112, STEEL, 2.2)
    cv.hline(28, 70, 113, STEEL, 0.8)
    # número de la cel·la, estarcit
    text(cv, 'C-9', 37, 127, PAPER, 3.0, worn=0.12)
    # trapa del menjar, amb les frontisses i el pestell
    cv.rect(31, 176, 64, 188, STEEL, lambda x, y: 2.0 + (1.4 if y == 176 else 0) - (1.2 if y == 188 else 0) - (0.5 if x == 64 else 0))
    for hx in (34, 59):
        cv.rect(hx, 174, hx + 3, 176, STEEL, lambda x, y: 3.6 - (y - 174) * 0.6)
    cv.rect(44, 180, 51, 181, STEEL, 4.0)
    cv.hline(44, 51, 182, STEEL, 1.0)
    # escletxa de sota la porta (per on la MARE passa els avisos)
    cv.hline(20, 78, 207, STEEL, 0.0)
    cv.hline(20, 78, 208, NAVY, 2.0, 0.2)
    # pany magnètic Aldaia M-3: una caixa de ferro vella amb placa de llautó
    cv.rect(63, 131, 76, 159, IRON, lambda x, y: 3.0 - (x - 63) * 0.09 - (y - 131) * 0.022)
    cv.vline(63, 131, 159, IRON, 4.4)
    cv.hline(63, 76, 131, IRON, 4.0)
    cv.hline(63, 76, 159, IRON, 0.8)
    cv.vline(76, 131, 159, IRON, 1.0)
    cv.rect(64, 134, 75, 139, GOLD, lambda x, y: 3.6 - (y - 134) * 0.3)          # placa «ALDAIA M-3»
    cv.hline(64, 75, 134, GOLD, 4.6)
    for x in range(65, 75):
        if x % 2 and x != 70:
            cv.put(x, 136, GOLD, 1.4)
            cv.put(x, 137, GOLD, 2.0)
    cv.rect(65, 143, 74, 150, IRON, 0.6)
    cv.rect(66, 144, 73, 149, CYAN, lambda x, y: 3.0 - (x - 66) * 0.22 - (y - 144) * 0.05, 0)
    cv.hline(67, 72, 146, CYAN, 4.2, 0)                                           # una ratlleta de lectura
    cv.put(67, 144, CYAN, 5, 0)
    cv.glow(70, 147, 12, (90, 200, 255), 0.5)
    bolt(cv, 66, 155, IRON, 3.0, 1.3)
    bolt(cv, 73, 155, IRON, 3.0, 1.3)
    # (l'ombra de la porta a la paret)
    cv.darken(88, 65, 94, 210, lambda x, y: 1 - (x - 88) / 7)


PANEL_O = (319, 105, 379, 167)    # marc del panell
COVER = (324, 111, 373, 161)      # la tapa


def panel_frame(cv):
    x0, y0, x1, y1 = PANEL_O
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            d = min(x - x0, x1 - x, y - y0, y1 - y)
            if d > 4:
                continue
            lvl = [0.6, 2.8, 2.2, 1.6, 0.2][d]
            if d in (1, 2, 3) and (x - x0 > x1 - x or y - y0 > y1 - y):
                lvl -= 0.8
            lvl += (hr(x, y, 31) - 0.5) * 0.9
            cv.put(x, y, RUST, lvl)
    for cx, cy in ((x0 + 1, y0 + 1), (x1 - 3, y0 + 1), (x0 + 1, y1 - 3), (x1 - 3, y1 - 3)):
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
            elif u == 1 or v == 1:
                lvl = 2.8
            elif u == X1 - X0 or v == Y1 - Y0:
                lvl = 0.4
            elif u == X1 - X0 - 1 or v == Y1 - Y0 - 1:
                lvl = 1.2
            elif 8 <= u <= X1 - X0 - 8 and 12 <= v <= Y1 - Y0 - 12:
                # nervis horitzontals en relleu (fan de reixeta)
                k = (v - 12) % 6
                lvl = [3.0, 2.6, 2.0, 1.4, 0.5, 1.6][k] + (n - 0.5) * 0.5
                if u in (8, X1 - X0 - 8):
                    lvl -= 0.6                                           # el nervi s'acaba arrodonit
            if dent:
                dd = math.hypot(x - dent[0] - dx, (y - dent[1] - dy) * 1.2)
                if dd < 7:
                    lvl += (-(x - dent[0] - dx) - (y - dent[1] - dy)) / 7 * 0.9 - 0.4
            # taques de rovell més fosc i més clar
            m = hr(x // 4 - dx, y // 4 - dy, 34)
            if n > 0.94 or m > 0.92:
                lvl -= 1.1                                               # crostes de rovell fosc
            if m < 0.1:
                lvl += 1.0                                               # rovell viu, ataronjat
            cv.put(x, y, RUST, lvl)
    # estampat «ALDAIA» a la part de dalt
    text(cv, 'ALDAIA', X0 + 12, Y0 + 5, RUST, 0.2, worn=0.15)            # en relleu: l'ombra i la llum
    text(cv, 'ALDAIA', X0 + 11, Y0 + 4, RUST, 3.8, worn=0.3)
    for i, (cx, cy) in enumerate(((X0 + 4, Y0 + 4), (X1 - 4, Y0 + 4), (X0 + 4, Y1 - 4), (X1 - 4, Y1 - 4))):
        if i in missing:
            cv.disc(cx, cy, 1.9, 1.9, GRIME, 0.0, 0)
        else:
            bolt(cv, cx, cy, IRON, 3.4, 2.1, slot=30 + i * 50)


def panel_cover(cv, dx, dy):
    _rust_plate(cv, *COVER, dx=dx, dy=dy)


def _panel(cv):
    panel_frame(cv)
    panel_cover(cv, 0, 0)
    # regalims de rovell per sota el panell
    for x in range(325, 375):
        if hr(x, 61) > 0.74:
            ln = int(5 + hr(x, 62) * 24)
            for y in range(168, 168 + ln):
                if hr(x, y, 63) > (y - 168) / ln:
                    cv.put(x, y, RUST, 1.6 + hr(x, 64) * 0.8 - (y - 168) / ln * 0.6)


CRACK = [(276, 119), (279, 124), (277, 128), (281, 132), (280, 136), (284, 140), (283, 144), (287, 148), (285, 152)]


def _crack(cv):
    """L'esquerda a la paret (269..299 × 116..157), amb el forat on hi ha encastada la nota."""
    for (xa, ya), (xb, yb) in zip(CRACK, CRACK[1:]):
        cv.line(xa + 1, ya, xb + 1, yb, STEEL, 1.4)
        cv.line(xa - 1, ya, xb - 1, yb, STEEL, 4.2)
        cv.line(xa, ya, xb, yb, GRIME, 0.0, 0)
    for (xa, ya), (xb, yb) in (((279, 124), (272, 121)), ((272, 121), (269, 122)), ((281, 132), (289, 129)),
                               ((289, 129), (292, 125)), ((284, 140), (291, 143)), ((283, 144), (279, 147))):
        cv.line(xa, ya, xb, yb, GRIME, 1.0, 0)
    # el forat on hi ha encastada la nota (fosc), amb el cantell de la planxa doblegat
    cv.rect(280, 133, 283, 137, GRIME, 0.0, 0)
    cv.vline(279, 133, 137, STEEL, 4.4)
    cv.hline(280, 283, 138, STEEL, 1.2)


VENT = (112, 152)                 # la reixa del conducte, tancada (cantonada de dalt a l'esquerra)
VENT_W, VENT_H = 72, 49


def vent_hole(cv):
    """L'interior del conducte: fosc, en perspectiva, amb la marca de l'Iri a la paret de dins."""
    x0, y0, x1, y1 = 115, 155, 180, 197
    ix0, iy0, ix1, iy1 = 139, 165, 171, 188
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            # fons del conducte cap a la dreta (el conducte gira cap a l'hangar)
            if ix0 <= x <= ix1 and iy0 <= y <= iy1:
                lvl = 0.2
            elif y > iy1:
                lvl = 1.2 - (y1 - y) * 0.04                               # terra del conducte
            elif x < ix0:
                lvl = 1.6 - (ix0 - x) / 24 * 0.8                         # paret esquerra del conducte
            elif y < iy0:
                lvl = 0.8
            else:
                lvl = 0.6
            if (x == ix0 - 1 and iy0 <= y <= iy1) or (y == iy1 + 1 and x >= ix0):
                lvl += 0.4                                                # l'aresta del gir
            cv.put(x, y, GRIME, lvl * 0.9, 0)
    # la marca de l'Iri: una I. i una clau anglesa, gravades a la paret esquerra del conducte
    M = RUST
    cv.vline(120, 163, 177, M, 3.4, 0)
    cv.vline(121, 163, 177, M, 2.4, 0)
    cv.rect(124, 176, 125, 177, M, 3.4, 0)
    cv.line(128, 180, 133, 169, M, 3.0, 0)
    cv.line(129, 180, 134, 169, M, 2.2, 0)
    cv.ring(135.5, 166, 3.2, M, 3.0, 0, step=20)
    cv.put(136, 164, GRIME, 0.0, 0)                                       # la boca de la clau
    # i la fletxa, cap endins
    cv.hline(140, 155, 192, M, 3.0, 0)
    cv.hline(140, 154, 193, M, 2.0, 0)
    cv.line(151, 188, 155, 192, M, 3.0, 0)
    cv.line(151, 196, 155, 192, M, 3.0, 0)


def vent_grille(cv, x0, y0, w=VENT_W, h=VENT_H):
    """La reixa: ferro rovellat, lamel·les, quatre cargols. (x0, y0) cantonada de dalt a l'esquerra."""
    x1, y1 = x0 + w - 1, y0 + h - 1
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            u, v = x - x0, y - y0
            n = hr(x - x0, y - y0, 51)
            if u < 4 or v < 4 or u > w - 5 or v > h - 5:
                lvl = [0.6, 3.0, 2.4, 1.8][min(u, v, 3)] if (u < 4 or v < 4) else [0.4, 0.8, 1.2, 1.4][min(w - 1 - u, h - 1 - v, 3)]
            else:
                k = (v - 4) % 6
                lvl = [2.8, 2.4, 1.8, 1.2, 0.4, 0.2][k]                   # lamel·la inclinada i buit
                if k >= 4:
                    cv.put(x, y, GRIME, 0.3 + (0.6 if n > 0.8 else 0), 0.2)
                    continue
            lvl += (n - 0.5) * 0.8
            if n > 0.94 or hr((x - x0) // 4, (y - y0) // 3, 55) > 0.93:
                lvl -= 1.1
            cv.put(x, y, RUST, lvl)
    for cx, cy in ((x0 + 1, y0 + 1), (x1 - 3, y0 + 1), (x0 + 1, y1 - 3), (x1 - 3, y1 - 3)):
        rivet(cv, cx, cy, IRON, 2.6)


FL, FR = 492, 621          # pals del davant de la llitera (x esquerra)
BL, BR = 501, 631          # pals del darrere


def _tier(cv, top):
    """Un pis de la llitera: matalàs (gruix + superfície) i travesser del davant. top = y de la superfície."""
    # superfície del matalàs (en perspectiva, fins a la paret)
    for y in range(top - 4, top + 1):
        t = (y - top + 4) / 4
        xl, xr = BL + 3 - t * 8, BR - t * 8
        for x in range(round(xl), round(xr) + 1):
            cv.put(x, y, MATT, 3.0 + t * 0.8 + (0.3 if (x + y) % 5 == 0 else 0))
    # ombra a la paret, sota el pis
    cv.darken(FL, top + 16, BR + 3, top + 45, lambda x, y: 0.8 - (y - top - 16) / 35, dither=False)
    # gruix del matalàs: vores arrodonides, ribet i ratlles de tela
    for y in range(top + 1, top + 11):
        for x in range(FL + 4, FR + 3):
            if (x in (FL + 4, FR + 2)) and y in (top + 1, top + 10):
                continue
            lvl = 3.0 - (y - top - 1) * 0.13 + (0.3 if x % 5 == 0 else 0)
            if y == top + 1:
                lvl += 1.0
            elif y == top + 2:
                lvl += 0.5
            elif y == top + 8:
                lvl -= 0.4                                                # el ribet de baix
            if y == top + 10:
                lvl -= 1.2
            if x == FL + 4:
                lvl += 0.6
            cv.put(x, y, MATT, lvl)
    # travesser d'acer
    cv.rect(FL, top + 11, FR + 4, top + 15, STEEL, lambda x, y: [4.8, 4.2, 3.6, 2.6, 1.0][y - top - 11])
    # el somier de molles, que es veu per sota el travesser
    for x in range(FL + 5, FR + 1):
        k = (x - FL) % 8
        yy = top + 16 + (k if k < 4 else 8 - k)
        cv.put(x, yy, STEEL, 3.4)
        cv.put(x, yy + 1, STEEL, 1.4)
    cv.hline(FL + 4, FR + 1, top + 21, STEEL, 2.4)
    cv.hline(FL + 4, FR + 1, top + 22, STEEL, 1.0)


def _bunk(cv):
    # ombra al terra i a la paret
    cv.darken(BL - 3, FLOOR_Y, BR + 5, 216, lambda x, y: 0.7 - (y - FLOOR_Y) * 0.09, dither=False)
    for y in range(216, 235):
        for x in range(FL - 3, FR + 11):
            a = 0.75 * max(0, 1 - abs(y - 223) / 12) * min(1, (x - FL + 4) / 8, (FR + 11 - x) / 8)
            o = cv.get(x, y)
            cv.P[x, y] = tuple(int(c * (1 - a * 0.6)) for c in o[:3]) + (255,)
    # pals del darrere
    for x in (BL, BR):
        cv.rect(x, 88, x + 3, 213, STEEL, lambda xx, yy: [2.6, 2.2, 1.6, 1.0][xx - x])

    # ratlles de dies a la paret (en Mos ho compta tot)
    for i in range(6):
        tx = 523 + i * 11
        for j in range(4):
            cv.vline(tx + j * 3 - 3, 132 + (j % 2), 139, STEEL, 4.4)
        cv.line(tx - 4, 137, tx + 7, 133, STEEL, 4.8)
    for j in range(2):
        cv.vline(587 + j * 3, 132, 139, STEEL, 4.4)
    # una foto vella enganxada a la paret (de la Nura?)
    cv.rect(603, 120, 615, 135, PAPER, lambda x, y: 3.2 - (y - 120) * 0.05)
    cv.rect(604, 121, 614, 130, ORANGE, lambda x, y: 1.4 + (y - 121) * 0.08)
    cv.disc(609, 126, 2.2, 2.8, SKIN, lambda nx, ny: 2.6 - nx * 0.5 - ny * 0.5)
    cv.hline(607, 611, 123, GRIME, 1.0)                                    # el cabell
    cv.rect(607, 129, 611, 130, NAVY, 2.0)                                 # les espatlles
    cv.rect(607, 118, 611, 120, MANILA, lambda x, y: 4.0 - (y - 118) * 0.3)   # cinta adhesiva
    cv.put(615, 135, PAPER, 1.6)                                           # la punta, doblegada

    # pis de dalt (el d'en Mos)
    _tier(cv, 103)
    # manta d'en Mos, rebregada i amb el coixí
    for y in range(93, 115):
        for x in range(531, 595):
            s = math.sin((x - 531) / 6.7 + (y - 93) / 5.3)
            top = 101 - math.sin((x - 531) / 64 * math.pi) * 5.3 - (2.7 if 547 < x < 560 else 0)
            if y >= top:
                lvl = 2.6 + s * 0.6 - (y - top) * 0.04 + (1.0 if y == math.ceil(top) else 0)
                cv.put(x, y, MATT, lvl + 0.2 - (0.6 if y > 112 else 0))
    cv.disc(604, 97, 12, 4.8, SHEET, lambda nx, ny: 3.8 - nx * 0.4 - ny * 1.2)
    cv.line(597, 95, 602, 97, SHEET, 2.6)                                  # el plec del coixí
    # pis de baix (el de la Vet)
    _tier(cv, 169)
    # el coixí de la Vet (el fullet treu el nas per sota)
    cv.disc(601, 164, 14.7, 5.6, SHEET, lambda nx, ny: 4.0 - nx * 0.4 - ny * 1.2)
    cv.line(592, 162, 598, 164, SHEET, 3.0)
    cv.hline(588, 615, 169, SHEET, 1.4)
    # manta plegada als peus
    cv.rect(512, 160, 539, 168, NAVY, lambda x, y: 3.0 - (y - 160) * 0.12 + (0.6 if y in (160, 164) else 0) - (0.6 if y == 163 else 0))
    cv.vline(539, 161, 168, NAVY, 1.6)
    cv.hline(512, 539, 169, NAVY, 1.0)
    # pals del davant i escala
    for x in (FL, FR):
        cv.rect(x, 85, x + 4, 231, STEEL, lambda xx, yy: [4.4, 3.8, 3.2, 2.4, 1.2][xx - x] - (0.6 if yy > 220 else 0))
        cv.rect(x - 1, 83, x + 5, 85, STEEL, lambda xx, yy: 4.6 - (yy - 83) * 0.8)
        cv.rect(x - 1, 228, x + 5, 231, STEEL, lambda xx, yy: 1.8 - (yy - 228) * 0.2)
    for y in range(128, 171, 11):
        cv.hline(FL + 5, FL + 13, y, STEEL, 3.8)
        cv.hline(FL + 5, FL + 13, y + 1, STEEL, 2.6)
        cv.hline(FL + 5, FL + 13, y + 2, STEEL, 1.2)
    cv.rect(FL + 13, 120, FL + 15, 173, STEEL, lambda x, y: 3.6 - (x - FL - 13) * 1.1)
    # sota el llit: unes espardenyes de presó i una caixa
    cv.rect(560, 205, 595, 221, PANEL, lambda x, y: 2.4 - (y - 205) * 0.05 + (1.2 if y == 205 else 0) - (0.5 if x == 595 else 0))
    cv.hline(560, 595, 222, PANEL, 0.6)
    cv.rect(571, 211, 584, 213, PANEL, lambda x, y: 1.0 + (0.6 if y == 213 else 0))
    for sx in (524, 535):
        cv.disc(sx, 221, 4.5, 2.0, ORANGE, lambda nx, ny: 2.4 - ny)
        cv.put(sx - 1, 220, ORANGE, 3.6)
        cv.put(sx, 220, ORANGE, 3.2)
        cv.hline(sx - 2, sx + 2, 219, NAVY, 1.4)                           # la tira de goma


def _camera(cv):
    """La càmera de vigilància al racó del sostre (la MARE ho veu tot). El LED és a `_dyn`."""
    cv.rect(131, 25, 139, 28, STEEL, lambda x, y: 3.4 - (y - 25) * 0.3)
    cv.vline(135, 29, 32, STEEL, 2.0)
    cv.vline(136, 29, 32, STEEL, 1.0)
    cv.disc(135, 36, 6.7, 4.5, STEEL, lambda nx, ny: 3.6 - nx - ny * 1.2)
    cv.disc(132.6, 37.3, 2.4, 2.0, NAVY, 0.6, 0)
    cv.put(132, 36, CYAN, 3.4, 0)
    cv.put(133, 36, CYAN, 2.2, 0)


def _floor_wear(cv):
    """Rascades i un camí gastat al terra, de la porta a la llitera."""
    for y in range(221, 274):
        for x in range(53, 587):
            w = math.sin(x / 93.0) * 5.3 + 243
            if abs(y - w) < 9.3 and hr(x // 2, y, 91) > 0.82:
                o = cv.get(x, y)
                cv.P[x, y] = tuple(min(255, int(c * 1.18 + 4)) for c in o[:3]) + (255,)
    sc = random.Random(77)
    for _ in range(30):
        x, y = sc.randint(27, 613), sc.randint(220, 272)
        ln = sc.randint(4, 12)
        dy = sc.choice((0, 1))
        for k in range(ln):
            cv.put(x + k, y + (k * dy // 5), DECK, 4.2)


def _static(cv, night=False):
    """Tot el fons que no es mou (el fluorescent encès, el cor, la finestreta i el LED són a `_dyn`)."""
    _ceiling(cv)
    _wall(cv)
    _floor(cv)
    _door(cv)
    text(cv, 'MODUL C', 101, 59, STEEL, 0.9, worn=0.2)                   # rètol estarcit a la paret
    _panel(cv)
    _crack(cv)
    vent_hole(cv)            # sota la reixa, perquè la reixa oberta hi encaixi
    vent_grille(cv, *VENT)
    _bunk(cv)
    _camera(cv)
    _floor_wear(cv)


# ─── Fons: el que es mou ──────────────────────────────────────────────────────

def _tube(cv, night, t):
    """El fluorescent (264..387 × 4..9): de dia, un parpelleig un cop per cicle; de nit, la llum de vigilància."""
    ph = 2 * math.pi * t
    if night:
        cv.rect(264, 4, 387, 9, CYAN, lambda x, y: 0.6 + (0.4 if (x // 8) % 2 else 0), 0)
        cv.rect(320, 5, 331, 8, CYAN, 2.4 + 0.7 * math.sin(ph), 0)       # llum de vigilància, tènue
        return
    flick = 0.70 <= t < 0.74
    cv.rect(264, 4, 387, 9, CYAN, lambda x, y: 4.6 - (0.6 if x % 16 == 0 else 0) - (2.0 if flick and x < 349 else 0)
            - (0.4 if y == 9 else 0), 0)
    cv.hline(349 if flick else 264, 387, 6, [(250, 254, 255)], 0, 0)
    cv.hline(349 if flick else 264, 387, 5, [(236, 248, 255)], 0, 0)
    for x in range(264, 388, 16):
        cv.vline(x, 4, 9, STEEL, 3.0, 0)                                  # les pinces de la reixeta difusora


HX, HY = 235, 37


def _heart_in(x, y):
    nx, ny = (x - HX) / 20.0, (y - HY) / 18.7
    # cor clàssic: (x²+y²−1)³ − x²y³ ≤ 0 (amb y cap amunt)
    X, Y = nx * 1.15, -ny * 1.15 + 0.25
    return (X * X + Y * Y - 1) ** 3 - X * X * Y ** 3 <= 0


@lru_cache(maxsize=None)
def _heart_px():
    """Els píxels del cor: [(x, y, vora, vora2, nx, ny)] (es fa servir a cada fotograma)."""
    out = []
    for y in range(17, 62):
        for x in range(210, 261):
            if not _heart_in(x, y):
                continue
            edge = not (_heart_in(x - 1, y) and _heart_in(x + 1, y) and _heart_in(x, y - 1) and _heart_in(x, y + 1))
            edge2 = not (_heart_in(x - 2, y) and _heart_in(x + 2, y) and _heart_in(x, y - 2) and _heart_in(x, y + 2))
            edge3 = not (_heart_in(x - 3, y) and _heart_in(x + 3, y) and _heart_in(x, y - 3) and _heart_in(x, y + 3))
            out.append((x, y, edge, edge2, edge3, (x - HX) / 20, (y - HY) / 18.7))
    return out


def _heart(cv, night, t):
    """L'altaveu de la MARE: un cor de plàstic rosa (211..259 × 17..60) que batega."""
    beat = heartbeat(t)
    # suport i cable
    cv.rect(231, 19, 239, 25, STEEL, lambda x, y: 3.0 - (y - 19) * 0.25)
    cv.vline(235, 26, 27, STEEL, 1.2)
    cv.vline(234, 26, 27, STEEL, 2.4)
    prp = PINK if not night else PINK_NIGHT
    for x, y, edge, edge2, edge3, nx, ny in _heart_px():
        lvl = 3.0 - nx * 0.9 - ny * 1.1 + beat * 0.45
        if edge:
            lvl = 0.8 if (nx > 0 or ny > 0.3) else 2.0
        elif edge2:
            lvl += 0.8 if (nx < 0.1 and ny < 0.3) else -0.4
        elif edge3:
            lvl += 0.4
        # forats de la reixeta (2×1 cada 4 px, amb el cantell de sota il·luminat)
        elif -0.8 < ny < 0.55 and abs(nx) < 0.75 - max(0, ny) * 0.6 and x % 4 < 2 and y % 4 == 1:
            lvl = 0.8
        elif -0.8 < ny < 0.55 and abs(nx) < 0.75 - max(0, ny) * 0.6 and x % 4 < 2 and y % 4 == 2:
            lvl += 0.5
        cv.put(x, y, prp, lvl, 0.4)
    # brillantor de plàstic
    for x, y in ((221, 27), (222, 26), (223, 25), (224, 25), (225, 24), (226, 24), (220, 28), (220, 29), (219, 31)):
        cv.put(x, y, PINK, 5.6, 0)
    cv.put(248, 26, PINK, 4.6, 0)
    cv.put(249, 26, PINK, 4.6, 0)
    if not night:
        cv.glow(HX, HY, 40, (255, 120, 190), 0.32 * (1 + 0.45 * beat))
        cv.tint(200, 19, 273, 93, (255, 110, 180),
                lambda x, y: max(0, 1 - math.hypot(x - HX, y - HY) / 45) * 0.18 * (1 + 0.5 * beat))
    else:
        cv.glow(HX, HY, 24, (200, 70, 150), 0.25 * (1 + 0.6 * beat))


PX, PY, PR = 448, 67, 36           # la finestreta
EX, EY, ER = 456, 73, 10.0         # la Terra


@lru_cache(maxsize=None)
def _stars():
    rnd = random.Random(19)
    return {(rnd.randint(PX - 25, PX + 25), rnd.randint(PY - 25, PY + 25)): rnd.random() for _ in range(60)}


def _window(cv, night, t):
    """La finestreta amb la Terra (412..484 × 31..103): l'anella, els estels que titil·len i la Terra."""
    ph = 2 * math.pi * t
    for y in range(PY - PR - 1, PY + PR + 2):
        for x in range(PX - PR - 1, PX + PR + 2):
            d = math.hypot(x - PX, y - PY)
            if d > PR + 0.5 or d <= 25.7:
                continue
            a = math.atan2(y - PY, x - PX)
            if d > PR - 1.6:
                cv.put(x, y, STEEL, 1.0)
            elif d > PR - 2.6:
                cv.put(x, y, STEEL, 2.4 - math.sin(a) * 0.8)                 # el cantell de fora
            elif d > 27.3:
                # anella gruixuda: bisellada (llum de dalt)
                lvl = 3.4 - math.sin(a) * 1.2 + (0.6 if d < 29.3 else 0)
                cv.put(x, y, STEEL, lvl)
            else:
                cv.put(x, y, RUBBER, 1.4 - math.sin(a) * 0.6)                # la junta de goma
    # vuit cargols a l'anella
    for i in range(8):
        a = i * math.pi / 4 + math.pi / 8
        bolt(cv, PX + math.cos(a) * 32, PY + math.sin(a) * 32, STEEL, 4.0, 1.8, slot=i * 37)
    # l'espai
    stars = _stars()

    def twinkle(x, y, s):
        """Els estels titil·len, cadascun al seu ritme (harmònics 1..3). A t = 0, com sempre."""
        k = 1 + int(hr(x, y, 23) * 3)
        f = hr(x, y, 24) * 2 * math.pi
        v = math.sin(ph * k + f) - math.sin(f)
        if v > 0.9:
            return (255, 255, 255) if s > 0.6 else (200, 206, 250)
        if v < -0.9:
            return (110, 114, 170) if s > 0.6 else None
        return (230, 232, 255) if s > 0.6 else (130, 136, 190)
    for y in range(PY - 26, PY + 27):
        for x in range(PX - 26, PX + 27):
            if math.hypot(x - PX, y - PY) > 25.7:
                continue
            de = math.hypot(x - EX, y - EY)
            if de <= ER:
                # la Terra: blava i petita, amb continents, núvols i el terminador
                nx, ny = (x - EX) / ER, (y - EY) / ER
                shade = 3.6 - nx * 1.4 - ny * 0.9 - (nx * nx + ny * ny) * 0.8
                land = math.sin(nx * 3.4 + 0.6) + math.cos(ny * 4.2 - nx * 1.6) > 1.25
                cloud = hr(x // 2, y, 81) > 0.8 and abs(ny) < 0.8
                term = nx * 0.8 + ny * 0.5
                if term > 0.75:
                    cv.put(x, y, NAVY, 1.4, 0)                           # costat de nit
                elif cloud:
                    cv.put(x, y, PAPER, shade + 1.6 - (1.0 if term > 0.55 else 0), 0)
                elif land:
                    cv.put(x, y, LAMPG, shade - (0.8 if term > 0.55 else 0), 0)
                else:
                    cv.put(x, y, CYAN, shade - 1.2 - (0.8 if term > 0.55 else 0), 0)
            elif de <= ER + 1.4:
                cv.put(x, y, CYAN, 3.2 if (x - EX) + (y - EY) < 3 else 1.4, 0)  # atmosfera
            else:
                lvl = 1.0 + max(0, 1 - de / 35) * 1.6
                cv.put(x, y, SPACE, lvl, 0)
                s = stars.get((x, y))
                if s is not None and de > 17:
                    col = twinkle(x, y, s)
                    if col:
                        cv.flat(x, y, col)
                        if s > 0.9 and col[0] > 220:                     # els estels grossos fan creu
                            for ddx, ddy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                                if math.hypot(x + ddx - PX, y + ddy - PY) <= 25.7:
                                    cv.flat(x + ddx, y + ddy, (120, 124, 180))
    # reflex al vidre
    for i in range(10):
        cv.put(434 + i, 55 - i // 2 - (1 if i > 6 else 0), CYAN, 4.4, 0)
        if i < 7:
            cv.put(435 + i, 57 - i // 2, CYAN, 2.6, 0)
    cv.put(433, 59, CYAN, 3.6, 0)
    cv.put(433, 61, CYAN, 3.0, 0)
    cv.put(460, 88, CYAN, 3.0, 0)
    cv.put(463, 87, CYAN, 3.0, 0)
    cv.put(465, 85, CYAN, 2.6, 0)
    cv.glow(PX, PY, 53, (90, 150, 255), 0.14 if not night else 0.22)
    if not night:
        cv.tint(387, 27, 507, 133, (80, 140, 255), lambda x, y: max(0, 1 - math.hypot(x - PX, y - PY) / 60) * 0.12)


def _led(cv, t):
    """El LED de la càmera fa pampallugues."""
    if (t * 3) % 1 < 0.6:
        cv.put(139, 35, [(255, 60, 60)], 0, 0)
        cv.put(140, 35, [(200, 40, 44)], 0, 0)
        cv.glow(139, 35, 5, (255, 60, 60), 0.5)
    else:
        cv.put(139, 35, [(110, 30, 34)], 0, 0)
        cv.put(140, 35, [(80, 24, 28)], 0, 0)


def _dyn(cv, night=False, t=0.0):
    _tube(cv, night, t)
    _heart(cv, night, t)
    _window(cv, night, t)
    _led(cv, t)


# ─── Retocs finals (no depenen del temps): el halo del fluorescent ────────────

GLOW_C, GLOW_R, GLOW_COL = (325, 19), 147, (200, 235, 255)
POST_BOX = (GLOW_C[0] - GLOW_R, 0, GLOW_C[0] + GLOW_R, GLOW_C[1] + GLOW_R)


def _post(x, y, o):
    """El mateix que `cv.glow(325, 19, 147, …, 0.2)`, píxel a píxel."""
    d = math.hypot(x - GLOW_C[0], y - GLOW_C[1]) / GLOW_R
    if d < 1:
        a = 0.2 * (1 - d) ** 2
        if o[3] and a > B4[y & 3][x & 3] * 0.35:
            return mix(o, GLOW_COL, min(1, a)) + (o[3],)
    return o


# ─── La màquina de l'animació de fons ─────────────────────────────────────────

class Ambient:
    """
    Un fons animat partit en tres: `static(cv)` (quiet), `dyn(cv, t)` (el que es mou, pintat a sobre) i `post(x, y,
    rgba) → rgba` (retocs finals píxel a píxel dins `post_box`, que no depenen de t). `draw(cv, t)` ho pinta tot;
    `frames(n)` dona els fotogrames transparents (només els píxels que canvien respecte de t = 0) sense tornar a
    pintar la part quieta: es parteix de la imatge quieta, s'hi pinta `dyn(t)`, i els retocs només es tornen a fer
    allà on `dyn` ha canviat algun píxel (a la resta, la imatge quieta ja retocada).
    """

    def __init__(self, light, static, dyn, post=None, post_box=None):
        self.light, self.static, self.dyn, self.post = light, static, dyn, post
        self.post_box = post_box or (0, 0, W - 1, H - 1)

    def apply_post(self, cv):
        if not self.post:
            return
        x0, y0, x1, y1 = self.post_box
        P, f = cv.P, self.post
        for y in range(max(0, y0), min(H - 1, y1) + 1):
            for x in range(max(0, x0), min(W - 1, x1) + 1):
                P[x, y] = f(x, y, P[x, y])

    def draw(self, cv, t=0.0):
        self.static(cv)
        self.dyn(cv, t)
        self.apply_post(cv)

    def _static_img(self):
        if not hasattr(self, '_S'):
            cv = Canvas(light=self.light)
            self.static(cv)
            self._S = cv.img
            sp = Canvas(light=self.light, img=cv.img.copy())
            self.apply_post(sp)
            self._SP = np.asarray(sp.img).copy()
        return self._S, self._SP

    def _final(self, t):
        S, SP = self._static_img()
        cv = Canvas(light=self.light, img=S.copy())
        self.dyn(cv, t)
        pre = np.asarray(cv.img)
        changed = np.any(pre != np.asarray(S), axis=2)
        out = SP.copy()
        ys, xs = np.nonzero(changed)
        x0, y0, x1, y1 = self.post_box
        f = self.post
        for y, x in zip(ys.tolist(), xs.tolist()):
            o = tuple(int(c) for c in pre[y, x])
            if f and x0 <= x <= x1 and y0 <= y <= y1:
                o = f(x, y, o)
            out[y, x] = o
        return out

    def frames(self, n):
        base = self._final(0.0)
        res = []
        for i in range(n):
            fin = base if i == 0 else self._final(i / n)
            diff = np.any(fin != base, axis=2)
            arr = np.zeros_like(fin)
            arr[diff] = fin[diff]
            arr[diff, 3] = 255
            res.append(Image.fromarray(arr, 'RGBA'))
        return res


DAY = Ambient(LIGHT, lambda cv: _static(cv, False), lambda cv, t: _dyn(cv, False, t), _post, POST_BOX)
NIGHT = Ambient(LIGHT, lambda cv: _static(cv, True), lambda cv, t: _dyn(cv, True, t))


def bg(cv, night=False, t=0.0):
    """`t` (0..1): moment del cicle de l'animació de fons (t = 0 és el fons quiet)."""
    (NIGHT if night else DAY).draw(cv, t)


# ─── Props ────────────────────────────────────────────────────────────────────

def p_avis(cv):
    """L'avís de reciclatge, a terra, passat per sota la porta."""
    pts = [(100, 237), (132, 232), (136, 248), (103, 253)]
    contact_shadow(cv, 101, 136, 249, 254, 0.0)
    cv.poly([(101, 240), (135, 235), (138, 251), (104, 255)], GRIME, 0.0, 0)   # ombra
    cv.poly(pts, PAPER, lambda x, y: 4.0 + (x - 100) / 35 * 0.4 - (y - 232) / 21 * 0.3)
    # la capçalera i les ratlles del text
    for k in range(10):
        cv.put(105 + k, 239 - round(k * 0.16), PAPER, 1.2)
    for i, ln in enumerate((24, 26, 22, 17)):
        yy = 242 + i * 3
        for k in range(ln):
            x = 105 + k
            y = yy - round(k * 0.16)
            if hr(x, y, 71) > 0.25:
                cv.put(x, y, PAPER, 1.8)
    # el cor de la MARE a la capçalera
    for j, row in enumerate(('.##.##.', '#######', '#######', '.#####.', '..###..', '...#...')):
        for i, c in enumerate(row):
            if c == '#':
                cv.put(121 + i, 233 + j - round(i * 0.16), PINK, 3.2 + (1.0 if j == 1 and i < 3 else 0))
    # plec
    cv.line(117, 234, 120, 251, PAPER, 3.2)
    cv.line(118, 234, 121, 251, PAPER, 4.6)


def p_escarabat(cv):
    """El Senyor Bigotis: escarabat lluent, amb unes antenes llargues i arrissades com un bigoti."""
    cx, cy = 176, 220
    cv.disc(cx + 1, cy + 5, 12, 2.4, GRIME, 0.0, 0)                          # ombra
    for k in (-5, 0, 5):                                                   # potes
        for s in (-1, 1):
            cv.put(cx + k, cy + 5, BEET, 0.6)
            cv.put(cx + k + s, cy + 6, BEET, 0.4)
            cv.put(cx + k + 2 * s, cy + 7, BEET, 0.4)
    cv.disc(cx + 1, cy, 9.3, 5.9, BEET, lambda nx, ny: 2.8 - nx * 0.7 - ny * 1.5)
    cv.vline(cx + 1, cy - 5, cy + 5, BEET, 0.4)                             # separació dels èlitres
    cv.disc(cx - 5, cy - 1, 2.6, 2.6, BEET, lambda nx, ny: 2.6 - nx * 0.4 - ny * 0.4)   # el protòrax
    for x, y in ((cx - 2, cy - 4), (cx - 1, cy - 4), (cx, cy - 3), (cx + 1, cy - 4), (cx + 4, cy - 4), (cx + 5, cy - 4),
                 (cx + 6, cy - 3), (cx - 2, cy - 3)):
        cv.put(x, y, BEET, 5.0)                                            # reflex lluent
    cv.disc(cx - 8.7, cy + 0.7, 3.2, 2.9, BEET, lambda nx, ny: 1.8 - ny)   # cap
    cv.put(cx - 9, cy - 1, BEET, 4.0)
    cv.put(cx - 10, cy - 1, BEET, 3.4)
    # el «bigoti»: dues antenes llargues i arrissades
    for pts in (((-11, -1), (-13, -3), (-15, -4), (-16, -4), (-17, -3), (-17, -1), (-16, 0)),
                ((-11, 2), (-13, 4), (-15, 5), (-16, 5), (-17, 4), (-17, 3))):
        for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
            cv.line(cx + xa, cy + ya, cx + xb, cy + yb, BEET, 3.2)


def p_safata(cv):
    """Safata de sopar amb la sopa de reinserció: verda i fent bombolles."""
    contact_shadow(cv, 427, 475, 240, 247, 0.9)
    cv.poly([(429, 228), (472, 228), (476, 242), (425, 242)], PANEL, lambda x, y: 3.6 - (y - 228) * 0.03)
    cv.poly([(433, 229), (468, 229), (471, 239), (431, 239)], PANEL, lambda x, y: 2.8 - (y - 229) * 0.02)  # fons
    cv.line(433, 230, 431, 239, PANEL, 1.8)                                 # el cantell de dins, a l'ombra
    cv.hline(425, 476, 242, PANEL, 1.6)
    cv.hline(425, 476, 243, PANEL, 1.0)
    cv.hline(426, 475, 244, PANEL, 0.6)
    cv.hline(429, 472, 228, PANEL, 5.0)
    # bol
    cv.disc(452, 235, 12, 4.8, PANEL, lambda nx, ny: 5.0 - ny * 1.2 - nx * 0.4)
    cv.rect(441, 235, 463, 239, PANEL, lambda x, y: 4.0 - (x - 441) * 0.11)
    cv.disc(452, 239, 10.7, 2.1, PANEL, lambda nx, ny: 2.0 - nx)
    cv.disc(452, 234, 9.9, 3.3, LIME, lambda nx, ny: 3.0 + ny * 0.6 - nx * 0.4, 0.4)
    for x, y, r in ((448, 233, 1.3), (455, 232, 1.9), (457, 235, 1.1), (450, 236, 0.9)):
        cv.disc(x, y, r, r, LIME, 4.6, 0.3)
    # bombolles que pugen
    for x, y, r in ((451, 227, 2.0), (456, 223, 1.6), (452, 218, 1.3)):
        cv.ring(x, y, r, LIME, 3.6, 0.2, step=20)
        cv.put(x - 1, y - 1, LIME, 5.4, 0)
    # cullera i un tros de pa
    cv.line(435, 237, 441, 232, PANEL, 4.4)
    cv.line(436, 238, 441, 233, PANEL, 2.6)
    cv.disc(443, 231, 1.8, 1.3, PANEL, lambda nx, ny: 4.6 - ny)
    cv.disc(467, 233, 3.3, 2.0, MANILA, lambda nx, ny: 3.4 - ny)
    cv.put(466, 232, MANILA, 4.6)
    cv.put(468, 234, MANILA, 1.6)
    cv.glow(452, 232, 13, (150, 220, 90), 0.25)


def p_panell_afluixat(cv):
    """La tapa, afluixada pel cop de puny: desplaçada, un cargol menys i el bony del cop."""
    x0, y0, x1, y1 = COVER
    # escletxa fosca on era la tapa
    cv.rect(x0, y0, x1, y1, GRIME, 0.0, 0)
    _rust_plate(cv, x0, y0, x1, y1, dx=3, dy=4, missing=(0,), dent=(349, 136))
    # el cargol que ha saltat, penjant del forat
    cv.put(324, 170, IRON, 3.4)
    cv.put(324, 171, IRON, 2.4)
    cv.put(325, 171, IRON, 1.4)


def _console(cv, lit):
    """El forat del panell amb la consola vella a dins (i la tapa recolzada a terra)."""
    x0, y0, x1, y1 = COVER
    # el buit de darrere: una petita cambra fosca
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            d = min(x - x0, x1 - x, y - y0, y1 - y)
            lvl = 0.3 + min(d, 7) * 0.06 + (0.6 if (y - y0) < 3 else 0)
            cv.put(x, y, GRIME, lvl * 1.4, 0.3)
    # canonades de coure, al fons del buit
    for py in (y0 + 6, y0 + 10):
        cv.hline(x0 + 4, x1 - 4, py, COPPER, 1.6, 0.3)
        cv.hline(x0 + 4, x1 - 4, py + 1, COPPER, 0.6, 0.3)
    for bx in (x0 + 10, x1 - 10):
        cv.vline(bx, y0 + 5, y0 + 12, COPPER, 2.4, 0.3)                  # les brides
    # consola: caixa de ferro amb tauler de llautó
    cx0, cy0, cx1, cy1 = 328, 128, 369, 159
    cv.rect(cx0, cy0, cx1, cy1, IRON, lambda x, y: 2.6 - (y - cy0) * 0.025)
    cv.hline(cx0, cx1, cy0, IRON, 4.6)
    cv.vline(cx0, cy0, cy1, IRON, 3.8)
    cv.vline(cx1, cy0, cy1, IRON, 1.0)
    cv.hline(cx0, cx1, cy1, IRON, 0.8)
    cv.rect(cx0 + 2, cy0 + 2, cx1 - 2, cy0 + 4, GOLD, lambda x, y: 3.4 - (y - cy0 - 2) * 0.8)
    # rellotge (manòmetre)
    cv.disc(340, 144, 8.3, 8.3, GOLD, lambda nx, ny: 3.6 - nx - ny)
    _gauge(cv, 300 if lit else 215)
    # forat de la palanca
    cv.rect(355, 131, 361, 137, GRIME, 0.0, 0)
    cv.hline(355, 361, 138, IRON, 4.0)
    cv.vline(362, 131, 137, IRON, 3.2)
    # tres llums
    for i, lx in enumerate((353, 359, 365)):
        on = lit and i == 0
        if on:
            cv.disc(lx, 151, 2.1, 2.1, LAMPG, 6, 0)
        else:
            cv.disc(lx, 151, 2.1, 2.1, RED if i == 2 else LAMPG, 0.6, 0.2)
            cv.put(lx - 1, 150, PAPER, 1.6, 0.2)
    # cargols de la consola
    for bx, by in ((cx0 + 3, cy1 - 3), (cx1 - 3, cy1 - 3)):
        cv.put(bx, by, IRON, 4.0)
        cv.put(bx + 1, by + 1, IRON, 1.0)
    # la tapa, a terra, recolzada a la paret (la mateixa planxa, una mica escurçada)
    cv.darken(435, 168, 441, 209, lambda x, y: 0.8 - (x - 435) * 0.12, dither=False)    # ombra a la paret
    _rust_plate(cv, 387, 165, 436, 210)
    cv.vline(437, 166, 211, RUST, 0.4)                                          # gruix de la planxa
    cv.hline(387, 437, 211, RUST, 0.2)
    contact_shadow(cv, 385, 440, 213, 217, 0.9)


def _gauge(cv, deg, green=False):
    """L'esfera del manòmetre i l'agulla (a `deg` graus)."""
    cv.disc(340, 144, 6.4, 6.4, PAPER, lambda nx, ny: 4.6 - ny * 0.5 - nx * 0.3)
    for a in range(200, 341, 28):
        cv.put(340 + round(math.cos(math.radians(a)) * 5.3), 144 + round(math.sin(math.radians(a)) * 5.3), PAPER, 1.2)
    if green:
        for a in range(296, 341, 7):
            cv.flat(340 + round(math.cos(math.radians(a)) * 5.3), 144 + round(math.sin(math.radians(a)) * 5.3), (60, 170, 80))
    ang = math.radians(deg)
    for r in range(0, 6):
        cv.flat(340 + round(math.cos(ang) * r), 144 + round(math.sin(ang) * r), (170, 30, 30))
    cv.flat(340, 144, (40, 30, 30))


def p_panell_obert(cv):
    _console(cv, False)


def p_panell_reparat(cv):
    _console(cv, True)
    # la clau anglesa, fent de palanca: reluent, de ferro-9 (acer blavós)
    WR = ramp((24, 30, 46), (62, 78, 104), (112, 136, 166), (168, 194, 220), (220, 236, 248), (250, 254, 255), n=6)
    x0, y0, x1, y1 = 358.5, 135, 368.5, 95
    n = 42
    for i in range(n + 1):
        t = i / n
        x, y = round(x0 + (x1 - x0) * t), round(y0 + (y1 - y0) * t)
        cv.put(x - 1, y, WR, 4.4)
        cv.put(x, y, WR, 3.4)
        cv.put(x + 1, y, WR, 2.2)
        cv.put(x + 2, y, WR, 1.0)
    cv.put(358, 134, WR, 1.0)
    cv.put(359, 134, WR, 1.0)
    # cap ajustable: boca oberta cap amunt i el cargol sens fi
    hx, hy = 371, 88
    for y in range(hy - 8, hy + 8):
        for x in range(hx - 8, hx + 8):
            nx, ny = (x - hx) / 7.5, (y - hy) / 6.9
            if nx * nx + ny * ny > 1:
                continue
            if -2 <= x - hx <= 2 and y < hy + 1:
                continue                                                      # la boca
            cv.put(x, y, WR, 3.6 - nx * 1.4 - ny * 1.2)
    cv.vline(hx - 3, hy - 6, hy, WR, 5.0)
    cv.vline(hx + 3, hy - 6, hy, WR, 1.4)
    for k in range(4):
        cv.put(hx - 4 + k * 2, hy + 4, WR, 1.0)                              # cargol sens fi
        cv.put(hx - 3 + k * 2, hy + 4, WR, 3.0)
    cv.glow(367, 99, 21, (170, 220, 255), 0.16)
    # la llumeta verda encesa
    cv.glow(353, 151, 19, (90, 240, 120), 0.6)
    cv.put(352, 150, [(230, 255, 235)], 0, 0)


def p_panell_sincronitzat(cv):
    """Sense la clau anglesa: la cambra de la I. ho sincronitza tot sola. La consola, viva i tranquil·la."""
    _console(cv, True)
    x0, y0, x1, y1 = COVER
    # lluïssor cian que surt del buit de darrere, per les vores de la consola
    for y in range(y0 + 1, y1):
        for x in range(x0 + 1, x1):
            if 328 <= x <= 369 and 128 <= y <= 159:
                continue
            d = math.hypot((x - 348) / 32, (y - 141) / 29)
            a = max(0.0, 1 - d) * 1.6
            if a > B4[y & 3][x & 3] * 0.8:
                cv.put(x, y, TEAL, 0.6 + a * 2.2, 0)
    # contrallum cian a les vores de la caixa de la consola
    for x in range(329, 369):
        cv.put(x, 127, TEAL, 4.0 + hr(x, 3), 0)
    for y in range(129, 159):
        cv.put(327, y, TEAL, 4.2 - (y - 129) * 0.075, 0)
        cv.put(370, y, TEAL, 3.4 - (y - 129) * 0.075, 0)
    # l'agulla, més enllà: a la zona verda
    _gauge(cv, 318, green=True)
    # el forat de la palanca, buit (ja no cal)
    cv.rect(355, 131, 361, 137, GRIME, 0.0, 0)
    cv.rect(356, 132, 360, 134, TEAL, 0.8, 0)                          # el cian de dins, pel forat
    # els tres llums encesos, en verd
    for lx in (353, 359, 365):
        cv.disc(lx, 151, 2.1, 2.1, LAMPG, 6, 0)
        cv.put(lx - 1, 150, [(230, 255, 235)], 0, 0)
    cv.glow(359, 151, 24, (90, 240, 120), 0.5)
    cv.glow(348, 139, 40, (110, 230, 240), 0.18)


def p_reixa_oberta(cv):
    """La reixa, treta i recolzada a la paret; a dins, la marca de l'Iri i una fletxa."""
    vx0, vy0 = VENT
    vent_hole(cv)
    # restes del marc (els forats dels cargols, rovellats)
    for x in range(vx0, vx0 + VENT_W):
        cv.put(x, vy0, RUST, 1.6)
        cv.put(x, vy0 + 1, RUST, 2.4)
        cv.put(x, vy0 + 2, RUST, 1.2)
    for y in range(vy0, vy0 + VENT_H):
        cv.put(vx0, y, RUST, 1.6)
        cv.put(vx0 + 1, y, RUST, 2.4)
        cv.put(vx0 + 2, y, RUST, 1.2)
        cv.put(vx0 + VENT_W - 1, y, RUST, 1.2)
        cv.put(vx0 + VENT_W - 2, y, RUST, 0.8)
    for cx, cy in ((vx0 + 1, vy0 + 1), (vx0 + VENT_W - 3, vy0 + 1), (vx0 + 1, vy0 + VENT_H - 3), (vx0 + VENT_W - 3, vy0 + VENT_H - 3)):
        cv.rect(cx, cy, cx + 1, cy + 1, GRIME, 0.0, 0)                     # els forats dels cargols
    # la reixa, recolzada dreta contra la paret (girada: les lamel·les queden verticals; s'hi veu la paret)
    gx0, gy0, gw, gh = 191, 140, 49, 71
    cv.darken(gx0 + gw, gy0 + 3, gx0 + gw + 5, gy0 + gh, lambda x, y: 0.8 - (x - gx0 - gw) * 0.14, dither=False)
    for y in range(gy0, gy0 + gh):
        for x in range(gx0, gx0 + gw):
            u, v = x - gx0, y - gy0
            n = hr(u, v, 52)
            if u < 4 or v < 4 or u > gw - 5 or v > gh - 5:
                lvl = [0.6, 3.0, 2.4, 1.8][min(u, v, 3)] if (u < 4 or v < 4) else [0.4, 0.8, 1.2, 1.4][min(gw - 1 - u, gh - 1 - v, 3)]
            else:
                k = (u - 4) % 6
                if k >= 4:
                    if k == 4:
                        cv.put(x, y, GRIME, 0.6, 0)                         # ombra de la lamel·la; després, la paret
                    continue
                lvl = [2.8, 2.4, 1.8, 1.2][k]
            lvl += (n - 0.5) * 0.8
            if n > 0.94 or hr(u // 3, v // 4, 56) > 0.94:
                lvl -= 1.1
            cv.put(x, y, RUST, lvl)
    for cx, cy in ((gx0 + 1, gy0 + 1), (gx0 + gw - 3, gy0 + 1), (gx0 + 1, gy0 + gh - 3), (gx0 + gw - 3, gy0 + gh - 3)):
        cv.rect(cx, cy, cx + 1, cy + 1, GRIME, 0.0, 0)                     # forats dels cargols, buits
    contact_shadow(cv, gx0, gx0 + gw, gy0 + gh, gy0 + gh + 4, 0.9)


def p_esquerda(cv):
    """La nota de la interna 4, plegada i encastada a l'esquerda."""
    cv.poly([(279, 132), (287, 129), (288, 136), (280, 139)], MANILA, lambda x, y: 3.6 - (y - 129) * 0.12)
    cv.line(280, 133, 287, 130, MANILA, 5.0)
    cv.line(281, 138, 288, 135, MANILA, 2.2)
    cv.line(283, 134, 285, 137, MANILA, 2.6)                                # el plec
    cv.put(284, 133, MANILA, 1.6)                                           # una lletra que es transparenta
    cv.put(286, 132, MANILA, 1.8)


def p_fullet(cv):
    """El fullet de reeducació, que treu el nas per sota el coixí de la llitera de baix."""
    cv.poly([(571, 169), (595, 167), (596, 175), (572, 177)], PAPER, lambda x, y: 4.6 - (y - 167) * 0.1)
    cv.hline(572, 595, 177, PAPER, 1.4)
    cv.line(571, 169, 572, 177, PAPER, 3.6)
    # portada: el cor de la MARE i el títol
    for j, row in enumerate(('##.##', '#####', '.###.', '..#..')):
        for i, c in enumerate(row):
            if c == '#':
                cv.put(575 + i, 170 + j, PINK, 3.4)
    cv.put(575, 170, PINK, 4.6)
    for k in range(10):
        cv.put(583 + k, 171 - k // 8, TEAL, 2.4)
        if k % 2:
            cv.put(583 + k, 173 - k // 8, PAPER, 2.0)
        if k % 3 and k < 8:
            cv.put(583 + k, 175 - k // 8, PAPER, 2.4)
    # l'ombra del coixí que hi cau a sobre
    cv.darken(587, 167, 596, 169, 0.6)


def p_molla(cv):
    """Una molla del somier de la Vet, mig deslligada, que penja per sota el travesser de la llitera de baix."""
    cx, y0 = 548, 185
    cv.darken(cx - 5, y0, cx + 6, y0 + 2, 0.7)                             # el forat que deixa al somier
    for k in range(7):                                                      # les espires, cada cop més obertes
        y = y0 + 1 + k * 2 + k // 3
        w = 3 + (k > 1)
        cv.line(cx - w, y, cx + w, y + 1, STEEL, 4.6 - k * 0.15)
        cv.put(cx + w, y + 2, STEEL, 1.8)
        cv.put(cx - w + 1, y, STEEL, 5.2)                                   # el reflex
    cv.line(cx + 1, y0 + 17, cx + 3, y0 + 21, STEEL, 3.6)                    # la punta, estirada
    cv.put(cx + 3, y0 + 21, STEEL, 5.0)


# ─── Animació ─────────────────────────────────────────────────────────────────

def _ambient_frames(n=24):
    return DAY.frames(n)


ANIMS = {'ambient': {'frames': _ambient_frames, 'frameDuration': 125}}


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
    'molla': p_molla,
}
