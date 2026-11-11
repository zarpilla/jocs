"""
La sala de màquines de l'Arenga (Escenes 1 i 9). Art definitiu, a partir de la mostra aprovada
(guio/art/mostra/sala_maquines.py):
  - a l'esquerra, la porta estanca del passadís (oberta) i l'escala inclinada que puja a l'escotilla del sostre
    (on seu en Bastida a l'Escena 9), amb el registre de la sentina a terra, als seus peus;
  - la boca del tub de veu de llautó i el cartell de «no abocar res al mar»;
  - el motor principal parat, amb el col·lector d'escapament folrat (on seu en Diu);
  - la porta del rebost (tancada) i, a la dreta, la del taller (oberta);
  - un altell de reixa amb el generador (i la caixa del relé de sincronització), i a sota el quadre de la bomba
    de sentina, l'alarma amb el sensor desendollat, la vàlvula de tres vies i el separador d'aigües oleoses;
  - a terra, la vàlvula de presa de mar sense volant (amb la planxa del terra aixecada) i la bomba de sentina.
Decorats: `aigua` (dos dits d'aigua), `valvula_tancada` (el travesser fa de volant), `brida` (a l'interruptor),
`fosc` (el generador parat: només els llums d'emergència).
"""
import math
from functools import lru_cache

from hd.pix import Canvas, Light, W, H, hr, mix, B4, RUST
from hd.rooms.arenga import (WALL, ENG_LIGHT, DECK, CAB, LAG, REDP, YELL, SEAG, FUEL, SEP, DARK, WHITEP, BRASS,
                             WARM, RED_GLOW, FLOOR_Y, BOTTOM, box, rrect, bolt, hpipe, vpipe, glow)
from hd.rooms.comu import _diff, text, text_width

ENG = ENG_LIGHT
LAMPS = ((186, 22), (372, 22))
MEZZ_Y = 74                     # el pis de reixa de l'altell
BRIDA = [(70, 70, 66), (150, 150, 142), (214, 214, 204), (246, 246, 238)]
STEELG = [(14, 16, 18), (26, 30, 32), (40, 46, 48), (58, 66, 68), (80, 90, 90), (108, 118, 116), (140, 150, 146)]

LIGHT = Light(ambient=-0.5, vignette=(56, 30), floor_fade=None)
LIGHT.point(186, 26, r=158, k=2.6, squash=1.05, down=True, power=1.5)
LIGHT.point(372, 26, r=120, k=2.2, squash=1.05, down=True, power=1.5)
LIGHT.point(346, 84, r=90, k=1.5, squash=1.2, down=True, power=1.6)    # el llum de sota l'altell
LIGHT.point(34, 60, r=40, k=0.7, power=2.0)                              # emergència, sobre la porta
LIGHT.point(449, 120, r=34, k=0.5, power=2.0)                            # el taller, de l'altra banda


# ─── La paret i el sostre ───────────────────────────────────────────────────

def wall(cv):
    for y in range(0, FLOOR_Y):
        for x in range(W):
            lvl = 3.1 + (hr(x // 3, y // 5) - 0.5) * 0.35
            if y >= 134:
                lvl -= 0.9 + (0.3 if hr(x // 6, y // 3) > 0.8 else 0)
            cv.put(x, y, WALL, lvl)
    for fx in range(-8, W, 64):                           # quadernes
        for x in range(fx, fx + 6):
            for y in range(20, FLOOR_Y):
                d = x - fx
                cv.put(x, y, WALL, 3.5 + (0.9 if d == 0 else 0.5 if d == 1 else -0.3 if d >= 4 else 0.1)
                       - (0.8 if y >= 134 else 0))
        for y in range(28, 132, 12):
            bolt(cv, fx + 2, y, WALL, 3.6)
    for sy in (64, 112):                                  # soldadures
        for x in range(W):
            cv.put(x, sy, WALL, 1.8)
            cv.put(x, sy + 1, WALL, 3.9 if hr(x // 2, sy) > 0.3 else 3.2)
    cv.hline(0, W - 1, 134, WALL, 4.0)
    cv.hline(0, W - 1, FLOOR_Y - 1, WALL, 1.0)
    for i in range(26):                                   # rovell
        x = int(hr(i, 7) * W)
        y0 = 66 if hr(i, 8) > 0.5 else 114
        n = 6 + int(hr(i, 9) * 18)
        for y in range(y0, min(FLOOR_Y - 2, y0 + n)):
            k = 0.55 * (1 - (y - y0) / n)
            if k > B4[y & 3][x & 3] * 0.6:
                cv.flat(x, y, mix(cv.get(x, y), RUST[3], k))


def ceiling(cv):
    cv.rect(0, 0, W - 1, 19, DARK, 2.0)
    for bx in range(-8, W, 64):
        box(cv, bx - 2, 0, bx + 8, 21, ENG, 1.6, grad=0.6)
    for y in (6, 13):
        cv.hline(0, W - 1, y, CAB, 2.8)
        cv.hline(0, W - 1, y + 4, CAB, 1.6)
        for x in range(0, W, 5):
            cv.vline(x, y, y + 4, CAB, 2.2)
        for x in range(W):
            if hr(x // 9, y) > 0.35:
                cv.flat(x, y + 2, [(20, 20, 24), (40, 36, 30), (70, 50, 34), (110, 40, 34)][int(hr(x // 11, y) * 4)])


def wall_pipes(cv):
    hpipe(cv, 92, W - 1, 40, 3, SEAG, 3.0, bands=range(104, W, 46), band_ramp=WHITEP)
    hpipe(cv, 92, W - 1, 51, 2, FUEL, 3.0, bands=range(126, W, 46), band_ramp=YELL)
    for x in range(98, W, 48):
        cv.vline(x, 35, 45, CAB, 2.0)
        cv.vline(x + 1, 35, 45, CAB, 3.4)
        cv.vline(x, 48, 54, CAB, 2.0)
    # el tub d'aigua de mar baixa a terra entre el rebost i el quadre
    vpipe(cv, 319, 40, FLOOR_Y + 2, 2, SEAG, 2.8, bands=(96, 128), band_ramp=WHITEP)


def lamps(cv):
    for lx, ly in LAMPS:
        box(cv, lx - 6, 16, lx + 6, 20, CAB, 3.0)
        cv.disc(lx, ly + 3, 6, 4, [(120, 90, 40), (200, 160, 80), (250, 220, 150), (255, 246, 220)], 2.6, lit=0)
        for gx in (-4, 0, 4):
            cv.vline(lx + gx, ly, ly + 7, CAB, 2.2, lit=0)
        cv.hline(lx - 6, lx + 6, ly + 4, CAB, 2.0, lit=0)


def lamp_glows(cv):
    for lx, ly in LAMPS:
        glow(cv, lx, ly + 4, 34, WARM, 0.55)
        glow(cv, lx, ly + 4, 12, (255, 240, 200), 0.6)
    glow(cv, 346, 82, 22, WARM, 0.45)
    glow(cv, 346, 82, 8, (255, 240, 200), 0.6)
    glow(cv, 34, 59, 26, RED_GLOW, 0.55)


# ─── Portes ────────────────────────────────────────────────────────────────

def _frame(cv, x0, y0, x1, y1, r=9):
    """Marc d'una porta estanca (cantons rodons a dalt)."""
    for t in range(3):
        for y in range(y0 - t, y1 + 1):
            for x in range(x0 - t, x1 + t + 1):
                dx = max(x0 - t + r - x, 0, x - (x1 + t - r))
                dy = max(y0 - t + r - y, 0)
                inside = dx * dx + dy * dy <= r * r
                inner = x0 - t + 1 <= x <= x1 + t - 1 and y >= y0 - t + 1
                ddx = max(x0 - t + 1 + r - x, 0, x - (x1 + t - 1 - r))
                ddy = max(y0 - t + 1 + r - y, 0)
                if inside and not (inner and ddx * ddx + ddy * ddy <= r * r):
                    cv.put(x, y, WALL, 4.2 - t * 0.9)


def _inside(x, y, x0, y0, x1, r=9):
    dx = max(x0 + r - x, 0, x - (x1 - r))
    dy = max(y0 + r - y, 0)
    return dx * dx + dy * dy <= r * r


def _sill(cv, x0, x1, y1):
    cv.rect(x0 + 1, y1 - 6, x1 - 1, y1 - 1, WALL, 2.6)
    cv.hline(x0 + 1, x1 - 1, y1 - 6, WALL, 4.0)


def _sign(cv, s, cx, y, ramp=WHITEP, lvl=4.0, ink=(20, 24, 28)):
    w = text_width(s)
    x0 = cx - (w + 6) // 2
    box(cv, x0, y, x0 + w + 5, y + 8, ramp, lvl)
    text(cv, s, x0 + 3, y + 2, None, 0, flat=ink)


def door_passadis(cv):
    """La porta del passadís, oberta: el passadís de baix, fosc, amb un llum llunyà."""
    x0, y0, x1, y1 = 14, 66, 54, FLOOR_Y
    for y in range(y0, y1):
        for x in range(x0, x1 + 1):
            if _inside(x, y, x0, y0, x1):
                cv.put(x, y, DARK, 1.6 - abs(x - 34) / 30 + (0.9 if y > 132 else 0) - (y - y0) / 120, lit=0.3)
    cv.disc(34, 76, 3, 1.5, [(80, 70, 50), (160, 140, 100)], 1.4, lit=0)
    glow(cv, 34, 78, 12, (140, 130, 100), 0.35)
    _frame(cv, x0, y0, x1, y1)
    _sill(cv, x0, x1, y1)
    cv.poly([(4, y0 + 4), (12, y0 - 1), (12, y1 - 2), (4, y1 - 4)], ENG, lambda x, y: 2.8 - (x - 4) * 0.06)
    for y in range(y0 + 10, y1 - 8, 22):
        box(cv, 6, y, 10, y + 3, ENG, 3.6)
    for dx, dy in ((x0 - 4, 84), (x0 - 4, 124), (x1 + 2, 84), (x1 + 2, 124)):
        box(cv, dx, dy, dx + 2, dy + 6, CAB, 3.4)
    # llum d'emergència i cartell verd de sortida
    box(cv, 28, 56, 40, 61, CAB, 2.6)
    cv.disc(34, 59, 5, 2.5, REDP, 4.6, lit=0)
    box(cv, 21, 46, 47, 52, SEAG, 3.4, edge=False)
    for x in range(23, 45, 3):
        cv.put(x, 49, WHITEP, 4.0, lit=0)
        cv.put(x + 1, 49, WHITEP, 4.0, lit=0)


def door_rebost(cv):
    """La porta del rebost, tancada (porta estanca amb palanques i nansa), amb el rètol."""
    x0, y0, x1, y1 = 280, 70, 314, FLOOR_Y
    _frame(cv, x0, y0, x1, y1)
    rrect(cv, x0, y0, x1, y1 - 6, 8, ENG, lambda x, y: 2.9 - (y - y0) * 0.006)
    rrect(cv, x0 + 4, y0 + 4, x1 - 4, y1 - 12, 5, ENG, lambda x, y: 3.25 - (y - y0) * 0.006)
    cv.hline(x0 + 6, x1 - 6, y0 + 4, ENG, 4.3)
    cv.hline(x0 + 6, x1 - 6, y1 - 12, ENG, 1.9)
    cv.vline(x1 - 4, y0 + 8, y1 - 14, ENG, 2.1)
    cv.vline(x0 + 4, y0 + 8, y1 - 14, ENG, 3.8)
    for dy in (y0 + 14, (y0 + y1) // 2 - 2, y1 - 24):     # palanques
        box(cv, x1 - 7, dy, x1 - 4, dy + 8, CAB, 3.8)
        cv.put(x1 - 6, dy + 1, CAB, 5.4)
    for dy in (y0 + 14, y1 - 24):
        box(cv, x0 + 4, dy, x0 + 7, dy + 6, CAB, 3.2)
    box(cv, x0 + 10, 108, x0 + 24, 112, CAB, 3.6)           # nansa
    cv.hline(x0 + 11, x0 + 23, 108, CAB, 5.0)
    _sill(cv, x0, x1, y1)
    # un rastre gastat a la pintura, a l'alçada de la mà (el cuiner d'abans hi baixava a fumar)
    for y in range(102, 118):
        for x in range(x0 + 8, x0 + 26):
            if hr(x, y, 5) > 0.82:
                cv.put(x, y, ENG, 4.4)
    _sign(cv, 'REBOST', (x0 + x1) // 2, 56)


def door_taller(cv):
    """La porta del taller, oberta: un taller petit amb llum de fluorescent i el tauler d'eines."""
    x0, y0, x1, y1 = 432, 66, 466, FLOOR_Y
    for y in range(y0, y1):
        for x in range(x0, x1 + 1):
            if _inside(x, y, x0, y0, x1):
                cv.put(x, y, WALL, 1.6 - abs(x - 449) / 40 - (y - y0) / 140, lit=0.4)
    # de l'altra banda: un tros de tauler d'eines i el cantó del banc
    cv.rect(436, 82, 462, 112, [(30, 24, 16), (52, 42, 26), (78, 64, 40), (104, 88, 56)], 1.6, lit=0.3)
    for i, (ex, ey, ew, eh) in enumerate(((440, 86, 2, 14), (446, 88, 5, 4), (454, 86, 2, 18), (446, 98, 4, 10))):
        cv.rect(ex, ey, ex + ew, ey + eh, [(14, 12, 10), (24, 22, 18), (40, 38, 32), (60, 58, 50)], 1.6, lit=0.3)
    cv.rect(436, 122, 466, 128, [(30, 22, 12), (56, 40, 22), (88, 64, 36), (120, 90, 52)], 2.2, lit=0.3)
    cv.rect(436, 129, 466, 146, DARK, 1.0, lit=0.2)
    cv.disc(449, 72, 8, 1.2, [(140, 150, 140), (220, 230, 220)], 1.2, lit=0)
    glow(cv, 449, 74, 18, (200, 220, 210), 0.3)
    _frame(cv, x0, y0, x1, y1)
    _sill(cv, x0, x1, y1)
    # la fulla, oberta contra la paret (de cantó, a la dreta)
    cv.poly([(476, y0 + 4), (470, y0 - 1), (470, y1 - 2), (476, y1 - 4)], ENG, lambda x, y: 2.4 + (x - 470) * 0.05)
    cv.vline(477, y0 + 5, y1 - 5, ENG, 1.2)
    for y in range(y0 + 10, y1 - 8, 22):
        box(cv, 472, y, 475, y + 3, ENG, 3.2)
    for dx, dy in ((x0 - 4, 84), (x0 - 4, 124)):
        box(cv, dx, dy, dx + 2, dy + 6, CAB, 3.4)
    _sign(cv, 'TALLER', (x0 + x1) // 2, 54)
    box(cv, 443, 42, 455, 47, CAB, 2.6)                              # llum d'emergència
    cv.disc(449, 45, 5, 2.5, REDP, 3.0, lit=0)


# ─── L'escala, l'escotilla i el registre de la sentina ────────────────────

def ladder(cv):
    """Escala de vaixell inclinada: del terra fins a l'escotilla del sostre (sortida d'emergència)."""
    # l'escotilla al sostre, de cantó (una boca fosca amb el marc)
    cv.rect(62, 0, 92, 19, DARK, 0.6, lit=0)
    box(cv, 60, 17, 94, 21, CAB, 3.2)
    for x in (64, 90):
        box(cv, x - 1, 8, x + 1, 17, CAB, 3.6)
    top, bot = 22, 170
    def edge(t, side):           # muntants: s'eixamplen cap a baix (vénen endavant)
        return (66 - t * 6, 88 + t * 6)[side]
    # els graons
    n = 13
    for i in range(1, n + 1):
        t = i / n
        y = round(top + (bot - top) * t ** 1.08)
        xa, xb = round(edge(t, 0)) + 2, round(edge(t, 1)) - 2
        d = 1 + round(t * 2)                               # la cara de dalt, més ample com més a prop
        cv.rect(xa, y - d, xb, y - 1, STEELG, 4.4 - t * 0.6)
        cv.hline(xa, xb, y, STEELG, 2.0)
        cv.hline(xa, xb, y + 1, DARK, 1.2)
        for x in range(xa + 1, xb, 3):                     # antilliscant
            cv.put(x, y - d, STEELG, 5.6)
    # muntants
    for side in (0, 1):
        for y in range(top, bot + 2):
            t = (y - top) / (bot - top)
            xc = round(edge(t, side))
            for k in range(3):
                cv.put(xc + k - 1, y, STEELG, (3.6 if side == 0 else 2.6) + (0.8 if k == 0 else -0.6 if k == 2 else 0))
    # passamans grocs, rectes, amb dos suports a cada muntant
    for (ax, ay), (bx, by), side in (((58, 16), (50, 142), 0), ((96, 16), (104, 142), 1)):
        cv.line(ax, ay, bx, by, YELL, 3.8)
        cv.line(ax + 1, ay, bx + 1, by, YELL, 2.4)
        for t in (0.3, 0.75):
            y = round(top + (bot - top) * t)
            xr = round(ax + (bx - ax) * (y - ay) / (by - ay))
            xe = round(edge((y - top) / (bot - top), side))
            cv.hline(min(xr, xe), max(xr, xe), y, YELL, 2.6)


def ladder_shadow(cv):
    cv.darken(54, 166, 102, 176, lambda x, y: 0.55 * max(0.0, 1 - abs(x - 78) / 26 - abs(y - 171) / 7))


def sentina(cv):
    """El registre de la sentina: una tapa de planxa amb cargols i dues nanses encastades."""
    x0, y0, x1, y1 = 98, 172, 140, 186
    cv.poly([(x0 + 3, y0), (x1 - 3, y0), (x1, y1), (x0, y1)], DECK, lambda x, y: 2.2)
    cv.poly([(x0 + 5, y0 + 2), (x1 - 5, y0 + 2), (x1 - 2, y1 - 2), (x0 + 2, y1 - 2)], DECK, lambda x, y: 3.4 - (y - y0) * 0.04)
    cv.hline(x0 + 3, x1 - 3, y0, DECK, 1.0)
    cv.hline(x0, x1, y1, DECK, 4.2)
    for i in range(7):                                      # cargols
        t = i / 6
        bolt(cv, round(x0 + 4 + (x1 - x0 - 8) * t), y0 + 2 - 0, DECK, 4.2)
        bolt(cv, round(x0 + 2 + (x1 - x0 - 4) * t), y1 - 2, DECK, 4.4)
    for hx in (x0 + 12, x1 - 16):                           # nanses encastades
        cv.rect(hx, y0 + 6, hx + 4, y0 + 8, DARK, 0.8)
        cv.hline(hx, hx + 4, y0 + 9, DECK, 4.6)
    # rètol estergit a la tapa
    for x in range(x0 + 14, x1 - 14, 2):
        cv.put(x, y0 + 12, YELL, 2.4)


# ─── El tub de veu i el cartell MARPOL ─────────────────────────────────────

def voice_tube(cv):
    vpipe(cv, 106, 20, 104, 2, BRASS, 2.8)
    for y in (34, 74):
        box(cv, 103, y, 109, y + 2, CAB, 3.2)
    cv.disc(106, 108, 4, 4, BRASS, lambda nx, ny: 3.2 - nx * 1.2 - ny * 1.0)
    cv.disc(106, 112, 7, 6, BRASS, lambda nx, ny: 3.5 - nx * 1.3 - ny * 1.2)
    cv.disc(106, 112, 5, 4, BRASS, lambda nx, ny: 1.2 + nx * 0.6 + ny * 0.8)
    cv.disc(106, 112, 3, 2, DARK, 0.6)
    for i, y in enumerate(range(119, 127)):
        cv.put(110 + (i % 2), y, BRASS, 3.0)
    cv.disc(112, 129, 3, 2, BRASS, 3.6)
    box(cv, 98, 134, 114, 138, BRASS, 3.0)
    for x in range(100, 113, 2):
        cv.put(x, 136, BRASS, 1.4)


def marpol(cv):
    x0, y0, x1, y1 = 100, 58, 120, 86
    box(cv, x0, y0, x1, y1, WHITEP, 4.0)
    cv.rect(x0 + 1, y0 + 1, x1 - 1, y0 + 6, [(20, 30, 70), (30, 50, 110), (50, 80, 150), (90, 120, 190)], 2.2)
    cx = (x0 + x1) // 2
    cv.disc(cx, y0 + 13, 3, 3, REDP, 4.2)
    cv.disc(cx, y0 + 13, 2, 2, WHITEP, 4.6)
    cv.disc(cx, y0 + 13, 1, 1, DARK, 1.0)
    for i in range(-3, 4):
        cv.put(cx + i, y0 + 13 + i, REDP, 4.2)
    for y in range(y0 + 19, y1 - 1, 2):
        for x in range(x0 + 2, x1 - 1):
            if hr(x // 3, y) > 0.25:
                cv.put(x, y, WHITEP, 1.6)


# ─── El motor principal ─────────────────────────────────────────────────────

def engine(cv):
    box(cv, 128, 140, 264, FLOOR_Y + 3, ENG, 2.0, grad=0.6)          # bancada
    for x in range(134, 262, 14):
        bolt(cv, x, 144, ENG, 2.6)
    box(cv, 136, 100, 256, 140, ENG, 3.0, grad=0.8)                  # càrter
    cv.hline(136, 256, 101, ENG, 4.1)
    for i in range(3):
        dx = 142 + i * 28
        rrect(cv, dx, 107, dx + 21, 131, 5, ENG, lambda x, y: 3.5 - (y - 107) * 0.03)
        rrect(cv, dx + 2, 109, dx + 19, 129, 4, ENG, lambda x, y: 2.9 - (y - 109) * 0.03)
        for bx, by in ((dx + 3, 110), (dx + 17, 110), (dx + 3, 127), (dx + 17, 127), (dx + 10, 108), (dx + 10, 129)):
            bolt(cv, bx, by, ENG, 3.4)
    box(cv, 140, 84, 252, 100, ENG, 3.3, grad=0.5)                   # bloc
    for i in range(4):
        dx = 143 + i * 27
        rrect(cv, dx, 72, dx + 23, 86, 4, ENG, lambda x, y: 4.1 - (y - 72) * 0.07)
        cv.hline(dx + 4, dx + 19, 73, ENG, 5.2)
        bolt(cv, dx + 4, 80, ENG, 3.8)
        bolt(cv, dx + 18, 80, ENG, 3.8)
        vpipe(cv, dx + 12, 86, 92, 1, ENG, 2.8)
    # col·lector d'escapament folrat (on seu en Diu) i la xemeneia cap al sostre
    hpipe(cv, 146, 256, 66, 4, LAG, 3.2, bands=range(160, 256, 26), band_ramp=CAB)
    vpipe(cv, 258, 20, 70, 6, LAG, 3.0, bands=range(28, 70, 14), band_ramp=CAB)
    cv.disc(258, 66, 6, 5, LAG, lambda nx, ny: 3.3 - nx - ny)
    # turbo
    cv.disc(264, 90, 10, 10, ENG, lambda nx, ny: 3.6 - nx * 1.4 - ny * 1.2)
    cv.disc(264, 90, 6, 6, ENG, lambda nx, ny: 2.6 + nx * 0.8 + ny * 0.8)
    cv.disc(264, 90, 2, 2, CAB, 4.6)
    # volant, amb protecció ratllada groc i negre
    box(cv, 122, 100, 136, 146, ENG, 2.4)
    for y in range(102, 145):
        for x in range(124, 135):
            if ((x + y) // 4) % 2 == 0:
                cv.put(x, y, YELL, 3.6)
            else:
                cv.put(x, y, DARK, 3.0)
    # panell local amb tres manòmetres (a zero: el motor és parat)
    box(cv, 226, 104, 254, 126, CAB, 2.4)
    for gx in (232, 240, 248):
        cv.disc(gx, 113, 3, 3, CAB, 1.4)
        cv.disc(gx, 113, 2, 2, WHITEP, 4.6)
        cv.put(gx, 113, DARK, 0)
        cv.put(gx - 1, 114, DARK, 0)
    for x in range(229, 252, 3):
        cv.put(x, 121, WHITEP, 3.0)
    box(cv, 180, 88, 212, 95, BRASS, 3.2)                            # placa de llautó
    for x in range(183, 210, 2):
        cv.put(x, 91, BRASS, 1.6)


# ─── L'altell i el generador ───────────────────────────────────────────────
def mezzanine(cv):
    """Un altell de reixa damunt del quadre i del separador, amb mènsules a la paret i barana groga."""
    x0, x1, y = 322, 428, MEZZ_Y
    # mènsules (sota)
    for mx in (330, 380, 420):
        cv.poly([(mx - 2, y + 4), (mx + 2, y + 4), (mx + 2, y + 18), (mx - 2, y + 6)], CAB, 2.6)
    # el pis de reixa: cantell i trama
    box(cv, x0, y, x1, y + 4, CAB, 3.0)
    for x in range(x0 + 1, x1, 2):
        cv.put(x, y + 2, DARK, 1.0)
    cv.hline(x0, x1, y, CAB, 4.6)
    cv.darken(x0, y + 5, x1, y + 12, lambda xx, yy: 0.7 - (yy - y - 5) * 0.09)
    # el llum de sota l'altell
    box(cv, 340, y + 5, 352, y + 7, CAB, 2.8)
    cv.disc(346, y + 9, 5, 2.5, [(120, 90, 40), (200, 160, 80), (250, 220, 150), (255, 246, 220)], 2.6, lit=0)


def railing(cv):
    """La barana groga de l'altell (per davant del generador)."""
    x0, x1, y = 322, 428, MEZZ_Y
    for px in range(x0 + 2, x1, 21):
        cv.vline(px, y - 18, y - 1, YELL, 3.2)
        cv.vline(px + 1, y - 18, y - 1, YELL, 2.2)
    cv.hline(x0 + 2, x1 - 1, y - 18, YELL, 3.8)
    cv.hline(x0 + 2, x1 - 1, y - 17, YELL, 2.4)
    cv.hline(x0 + 2, x1 - 1, y - 9, YELL, 3.0)


def generator(cv):
    """El generador auxiliar: un dièsel petit (verd), l'alternador (gris) i la caixa del relé."""
    y1 = MEZZ_Y - 1
    box(cv, 330, y1 - 4, 414, y1, ENG, 2.2)                           # bancada
    # el dièsel
    box(cv, 334, 46, 370, y1 - 5, ENG, 3.1, grad=0.8)
    for i in range(3):
        rrect(cv, 336 + i * 11, 38, 345 + i * 11, 48, 3, ENG, lambda x, y: 4.0 - (y - 38) * 0.08)
    for i in range(3):
        bolt(cv, 340 + i * 11, 43, ENG, 4.2)
    cv.rect(338, 54, 366, 60, ENG, 2.4)
    for x in range(339, 366, 3):
        cv.vline(x, 54, 60, ENG, 3.4)
    # la corretja i el volant (a l'esquerra)
    cv.disc(332, 58, 5, 5, ENG, lambda nx, ny: 3.4 - nx - ny)
    cv.disc(332, 58, 2, 2, CAB, 4.0)
    # l'alternador: cilindre ajagut amb aletes
    for y in range(44, y1 - 4):
        u = (y - 57) / 13
        for x in range(372, 404):
            fin = x % 3 == 0
            cv.put(x, y, STEELG, 3.6 + 1.5 * (-0.3 - u) - 0.8 * u * u + (0.6 if fin else 0))
    cv.disc(404, 57, 4, 13, STEELG, lambda nx, ny: 2.6 - nx * 0.6 - ny)
    box(cv, 380, 48, 394, 52, YELL, 3.2)                              # placa groga
    # la caixa del relé de sincronització, damunt de l'alternador
    box(cv, 384, 30, 406, 43, CAB, 3.4)
    cv.rect(388, 34, 394, 40, DARK, 0.6)                              # el sòcol del relé
    cv.rect(389, 35, 393, 39, CAB, 2.8)                               # el relé (un cub negre)
    cv.hline(389, 393, 35, CAB, 4.4)
    cv.flat(400, 35, (90, 240, 120))                                  # pilot verd
    glow(cv, 400, 35, 5, (90, 240, 120), 0.6)
    cv.flat(400, 39, (60, 30, 20))
    # el cable que baixa al quadre (per darrere de la barana)
    for y in range(y1 + 1, 84):
        cv.put(408, y, DARK, 1.6)
        cv.put(409, y, CAB, 2.2)
    # l'escapament, cap amunt
    vpipe(cv, 352, 20, 37, 2, LAG, 2.8, bands=(24,), band_ramp=CAB)


# ─── El quadre, l'alarma i el separador ─────────────────────────────────────

def panel(cv):
    x0, y0, x1, y1 = 324, 86, 368, FLOOR_Y + 2
    box(cv, x0, y0, x1, y1, CAB, 3.4, grad=1.0)
    box(cv, x0 - 2, y0 - 3, x1 + 2, y0, CAB, 3.8)
    for x in range(328, 364, 7):                                      # interruptors
        box(cv, x, 90, x + 4, 98, CAB, 2.0)
        cv.rect(x + 2, 92, x + 2, 95, DARK, 0.4)
        cv.put(x + 2, 92, CAB, 5.0)
        cv.rect(x, 100, x + 4, 101, WHITEP, 3.4)
    for x, col in ((330, (90, 240, 120)), (336, (90, 240, 120)), (342, (255, 190, 60))):
        cv.flat(x, 105, col)
        cv.flat(x + 1, 105, col)
        glow(cv, x, 105, 5, col, 0.6)
    cv.disc(358, 108, 6, 6, CAB, 1.8)                                 # amperímetre
    cv.disc(358, 108, 5, 5, WHITEP, 4.4)
    for a in range(200, 341, 28):
        cv.put(358 + round(math.cos(math.radians(a)) * 4), 108 + round(math.sin(math.radians(a)) * 4), DARK, 0)
    cv.line(358, 109, 360, 105, REDP, 4.0)
    # l'interruptor de la bomba de sentina (la maneta en OFF)
    box(cv, 330, 116, 346, 136, CAB, 2.6)
    cv.disc(338, 125, 5, 5, DARK, 1.6)
    cv.rect(337, 118, 339, 128, REDP, 4.2)
    cv.rect(332, 138, 344, 141, WHITEP, 3.6)                          # etiqueta «BOMBA SENTINA»
    for x in range(333, 344, 2):
        cv.put(x, 139, DARK, 1.0)
    box(cv, 352, 120, 354, 130, CAB, 4.4)                             # nansa de la porta
    cv.poly([(360, 132), (365, 141), (355, 141)], YELL, 4.0)          # alta tensió
    cv.vline(360, 135, 139, DARK, 0)
    for y in range(144, 152, 2):
        cv.hline(330, 362, y, CAB, 1.4)


def alarm(cv):
    """L'alarma de sentina, amb el cable del sensor desendollat penjant."""
    box(cv, 372, 88, 384, 102, CAB, 3.2)
    cv.disc(378, 86, 4, 3, REDP, lambda nx, ny: 2.0 - nx - ny)        # llum apagada
    cv.rect(374, 94, 382, 98, WHITEP, 3.0)
    pts = [(378, 103), (377, 110), (375, 117), (374, 124), (375, 130), (377, 134)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        cv.line(ax, ay, bx, by, DARK, 2.6)
        cv.line(ax + 1, ay, bx + 1, by, CAB, 2.6)
    box(cv, 375, 134, 379, 140, CAB, 3.4)
    cv.put(376, 140, BRASS, 4.0)
    cv.put(378, 140, BRASS, 4.0)
    box(cv, 372, 144, 380, 150, CAB, 2.8)                             # la presa buida
    cv.put(375, 147, DARK, 0)
    cv.put(377, 147, DARK, 0)


def separator(cv):
    """El separador d'aigües oleoses (dipòsit alt amb visor), la vàlvula de tres vies i la sortida a la borda."""
    x0, x1, top = 394, 424, 90
    cx, rx = (x0 + x1) / 2, (x1 - x0) / 2
    for y in range(top, FLOOR_Y + 3):
        for x in range(x0, x1 + 1):
            u = (x - cx) / (rx + 0.5)
            cv.put(x, y, SEP, 3.2 + 1.5 * (-0.3 - u) - 0.9 * u * u)
    cv.disc(cx, top, rx, 5, SEP, lambda nx, ny: 3.6 - nx * 1.3 - ny * 1.5)
    for y in (108, 138):
        for x in range(x0, x1 + 1):
            cv.put(x, y, SEP, 1.6)
    box(cv, 398, 96, 402, 132, CAB, 2.6)                              # visor: oli a dalt, aigua a sota
    for y in range(98, 131):
        col = FUEL if y < 108 else [(14, 30, 34), (24, 50, 54), (44, 80, 82), (80, 120, 120)]
        cv.put(399, y, col, 3.4 if y < 108 else 2.6, lit=0.4)
        cv.put(400, y, col, 2.6 if y < 108 else 2.0, lit=0.4)
    cv.hline(399, 400, 108, YELL, 4.0, lit=0)
    cv.disc(415, 98, 4, 4, CAB, 2.0)                                  # manòmetre
    cv.disc(415, 98, 3, 3, WHITEP, 4.6)
    cv.line(415, 98, 417, 96, DARK, 0)
    box(cv, 405, 112, 421, 126, CAB, 2.8)                             # caixa de control
    cv.rect(407, 114, 419, 117, [(6, 30, 14), (12, 70, 30), (40, 150, 70), (120, 240, 140)], 1.6, lit=0)
    for x in range(408, 418, 2):
        cv.put(x, 115, [(6, 30, 14), (40, 150, 70), (160, 255, 180)], 2, lit=0)
    cv.flat(410, 122, (90, 255, 120))
    glow(cv, 410, 122, 6, (90, 255, 120), 0.6)
    cv.flat(416, 122, (60, 30, 20))
    # la canonada de la bomba: puja per x=388 fins a la vàlvula de tres vies
    vpipe(cv, 388, 142, FLOOR_Y + 6, 2, CAB, 2.8)
    hpipe(cv, 388, 393, 140, 2, CAB, 3.0)                            # cap al separador
    vpipe(cv, 388, 82, 136, 2, CAB, 2.6)                             # cap a la borda (puja per l'altell)
    cv.disc(388, 140, 5, 5, REDP, lambda nx, ny: 3.8 - nx - ny)       # vàlvula de tres vies, cap a SEPARADOR
    cv.line(388, 140, 393, 146, REDP, 4.6)
    cv.line(389, 140, 394, 146, REDP, 3.2)
    box(cv, 384, 124, 392, 128, WHITEP, 3.0)                          # BORDA (a dalt)
    box(cv, 394, 144, 402, 148, YELL, 3.8)                            # SEPARADOR


# ─── El terra (planxa estriada) i l'aigua ─────────────────────────────────

VP = (240, 40)


def floor(cv):
    mask = [[False] * W for _ in range(H)]
    for y in range(FLOOR_Y, BOTTOM + 12):
        d = y - VP[1]
        for x in range(W):
            u = VP[0] + (x - VP[0]) * 150 / d
            u2 = VP[0] + (x + 1 - VP[0]) * 150 / d
            v = 2400 / d
            lvl = 2.5
            if int(u // 76) != int(u2 // 76):
                lvl = 1.0
            elif y in (158, 170, 187):
                lvl = 1.1
            elif y in (159, 171, 188):
                lvl = 3.3
            else:
                a, b = int(u * 0.5) % 4, int(v * 1.0) % 4
                if (a == 0 and b in (0, 1)) or (a == 2 and b in (2, 3)):
                    lvl += 0.9
            cv.put(x, y, DECK, lvl)
            mask[y][x] = True
    return mask


def water(cv, mask):
    """Dos dits d'aigua: tint fosc i verdós, reflex de la paret, ones i les espurnes dels llums."""
    src = cv.img.copy().load()
    WC = (10, 34, 40)
    for y in range(FLOOR_Y, BOTTOM + 12):
        depth = (y - FLOOR_Y) / (BOTTOM - FLOOR_Y)
        for x in range(W):
            if not mask[y][x]:
                continue
            c = mix(cv.get(x, y), WC, 0.38)
            sy = 2 * FLOOR_Y - y - 1
            sx = x + round(math.sin(y * 0.9 + x * 0.05) * 1.4)
            if 0 <= sy < FLOOR_Y and 0 <= sx < W:
                c = mix(c, src[sx, sy][:3], 0.55 * max(0.0, 1 - depth * 1.3))
            lit = LIGHT(x, y)
            if math.sin(x * 0.21 + y * 1.9 + math.sin(y * 0.37) * 4) > 0.93 and lit > 0.2 and hr(x // 4, y) > 0.3:
                c = mix(c, (140, 190, 180), min(0.5, 0.18 + lit * 0.12))
            cv.flat(x, y, c)
    for x in range(W):
        if mask[FLOOR_Y][x] and hr(x // 5, 5) > 0.55:
            cv.flat(x, FLOOR_Y, mix(cv.get(x, FLOOR_Y), (150, 190, 180), 0.25))
    for lx, _ in LAMPS:
        for y in range(FLOOR_Y + 3, BOTTOM + 8):
            t = (y - FLOOR_Y) / 46
            wdt = 3 + t * 9
            for x in range(int(lx - wdt * 2), int(lx + wdt * 2) + 1):
                if not (0 <= x < W) or not mask[y][x]:
                    continue
                g = math.exp(-((x - lx) / wdt) ** 2) * (1 - t * 0.55)
                seg = hr(x // (2 + int(t * 4)), y, lx)
                if seg < g * 0.55:
                    cv.flat(x, y, mix(cv.get(x, y), WARM, min(0.8, 0.35 + g * 0.5)))
                elif seg < g * 0.9:
                    cv.flat(x, y, mix(cv.get(x, y), WARM, 0.18))


def reflect_obj(cv, mask, x0, x1, top, base, k=0.4):
    src = cv.img.copy().load()
    for y in range(base + 1, min(BOTTOM + 12, base + (base - top) + 1)):
        sy = 2 * base - y
        f = k * (1 - (y - base) / (base - top + 1))
        for x in range(x0, x1 + 1):
            if not mask[y][x]:
                continue
            sx = x + round(math.sin(y * 0.9) * 1.2)
            if x0 <= sx <= x1 and top <= sy <= base and src[sx, sy][3] and not mask[sy][sx]:
                cv.flat(x, y, mix(cv.get(x, y), src[sx, sy][:3], f))


def unmask(mask, cv, x0, y0, x1, y1, before):
    a, b = before.load(), cv.img.load()
    for y in range(max(0, y0), min(H, y1 + 1)):
        for x in range(max(0, x0), min(W, x1 + 1)):
            if a[x, y] != b[x, y]:
                mask[y][x] = False


# ─── Objectes a terra ───────────────────────────────────────────────────────

VX = 236            # l'eix de la vàlvula de presa de mar


def sea_valve(cv):
    """La vàlvula de presa de mar: s'ha aixecat una planxa del terra. Sense volant."""
    cv.poly([(VX - 26, 172), (VX + 28, 172), (VX + 32, 186), (VX - 30, 186)], DARK, lambda x, y: 1.0 + (186 - y) * 0.04)
    cv.hline(VX - 26, VX + 28, 172, DECK, 1.0)
    cv.line(VX - 30, 186, VX + 32, 186, DECK, 4.0)
    for x in range(VX - 26, VX + 29):
        if hr(x // 3, 1) > 0.4:
            cv.put(x, 180 + int(hr(x, 2) * 3), [(10, 40, 46), (40, 90, 90), (110, 160, 150)], 1.4)
    # la planxa, recolzada de cantó contra la bancada del motor (a l'esquerra)
    cv.poly([(VX - 50, 142), (VX - 28, 140), (VX - 26, 178), (VX - 48, 176)], DECK, lambda x, y: 4.2 - (y - 140) * 0.03)
    for y in range(143, 176, 4):
        for x in range(VX - 48, VX - 28, 4):
            cv.put(x + (y // 4) % 2 * 2, y, DECK, 5.4)
    cv.line(VX - 28, 140, VX - 26, 178, DECK, 1.0)
    # el cos (vermell), la tapa i l'eix pelat
    cv.disc(VX, 178, 13, 6, REDP, lambda nx, ny: 3.4 - nx * 1.2 - ny * 1.4)
    for bx in range(VX - 10, VX + 12, 5):
        bolt(cv, bx, 175, REDP, 4.0)
    box(cv, VX - 5, 160, VX + 5, 173, REDP, 3.6)
    cv.hline(VX - 7, VX + 7, 160, REDP, 4.6)
    vpipe(cv, VX, 141, 160, 1, CAB, 4.6)
    box(cv, VX - 2, 139, VX + 2, 142, CAB, 5.0)                     # el quadradet on anava el volant


def bilge_pump(cv):
    """La bomba de sentina: motor elèctric i bomba vermella, amb el tub cap a la vàlvula de tres vies."""
    vpipe(cv, 388, 152, 164, 2, CAB, 2.8)
    box(cv, 330, 176, 392, 182, ENG, 2.0)
    for y in range(160, 177):
        u = (y - 168) / 9
        for x in range(334, 366):
            cv.put(x, y, ENG, 3.4 + 1.5 * (-0.3 - u) - 0.8 * u * u + (0.6 if x % 3 == 0 else 0))
    cv.disc(334, 168, 3, 8, ENG, 2.0)
    box(cv, 346, 156, 356, 161, CAB, 3.0)
    cv.disc(376, 168, 9, 9, REDP, lambda nx, ny: 3.8 - nx * 1.2 - ny * 1.2)
    cv.disc(376, 168, 3, 3, REDP, 2.0)
    box(cv, 366, 166, 369, 170, CAB, 3.6)
    hpipe(cv, 380, 388, 164, 2, CAB, 2.8)


# ─── Muntatge ───────────────────────────────────────────────────────────────

@lru_cache(maxsize=2)
def _render(wet):
    cv = Canvas(light=LIGHT)
    wall(cv)
    ceiling(cv)
    wall_pipes(cv)
    door_passadis(cv)
    door_rebost(cv)
    door_taller(cv)
    voice_tube(cv)
    marpol(cv)
    engine(cv)
    panel(cv)
    alarm(cv)
    separator(cv)
    mezzanine(cv)
    generator(cv)
    railing(cv)
    lamps(cv)
    mask = floor(cv)
    if wet:
        water(cv, mask)
    for fn, (x0, y0, x1, y1), base in ((ladder, (52, 0, 104, 176), 170), (sentina, (96, 170, 142, 188), 186),
                                       (sea_valve, (VX - 52, 138, VX + 34, 190), 182),
                                       (bilge_pump, (328, 150, 394, 184), 182)):
        before = cv.img.copy()
        fn(cv)
        unmask(mask, cv, x0, max(y0, FLOOR_Y), x1, y1, before)
        if wet and fn is not sentina:
            reflect_obj(cv, mask, x0, x1, max(y0, 120), base)
    ladder_shadow(cv)
    lamp_glows(cv)
    return cv.img


def bg(cv):
    cv.img.paste(_render(False), (0, 0))


# ─── Props i decorats ──────────────────────────────────────────────────────

def aigua(cv):
    """Dos dits d'aigua a terra (Escena 1, fins que la bomba la buida)."""
    cv.img.alpha_composite(_diff(_render(True), _render(False)))


def valvula_tancada(cv):
    """El travesser de la llitera, posat a l'eix com a volant (una barra de metall cromat amb tacs)."""
    y = 139
    CHR = [(30, 34, 40), (70, 78, 86), (120, 130, 138), (170, 178, 184), (214, 220, 224), (244, 246, 248)]
    hpipe(cv, VX - 20, VX + 20, y, 1, CHR, 3.0)
    for ex in (VX - 22, VX + 21):                                    # tacs de goma negra
        box(cv, ex, y - 2, ex + 1, y + 2, DARK, 2.2)
    box(cv, VX - 3, y - 3, VX + 3, y + 3, CAB, 4.4)                  # el nus al quadradet
    cv.put(VX, y, CAB, 1.2)


def brida(cv):
    """La brida blanca que lliga l'interruptor de la bomba a la nansa del quadre (nus Bastida)."""
    for y in range(120, 129):
        cv.put(335, y, BRIDA, 2.6)
        cv.put(341, y, BRIDA, 2.2)
    cv.hline(335, 341, 120, BRIDA, 3.0)
    cv.hline(335, 352, 128, BRIDA, 2.6)
    cv.disc(342, 129, 2, 1.5, BRIDA, 3.2)                             # el nus, amb una volta de més
    cv.put(343, 131, BRIDA, 2.4)
    cv.put(344, 132, BRIDA, 2.0)


def fosc(cv):
    """El generador parat: tot a les fosques, menys els llums d'emergència vermells."""
    lights = ((34, 59), (449, 45), (346, 83))
    P = cv.img.load()
    for y in range(H):
        for x in range(W):
            r = min(math.hypot(x - lx, (y - ly) * 1.1) for lx, ly in lights)
            red = max(0.0, 1 - r / 70) ** 1.6
            a = 0.84 - 0.42 * red
            k = 0.5 * red
            col = mix((2, 4, 10), (120, 14, 10), k)
            P[x, y] = col + (int(255 * a),)
    for lx, ly in lights:                                             # els llums mateixos
        for y in range(ly - 2, ly + 3):
            for x in range(lx - 5, lx + 6):
                if ((x - lx) / 5) ** 2 + ((y - ly) / 2.5) ** 2 <= 1:
                    P[x, y] = (255, 80 + int(60 * hr(x, y)), 60, 255)


def sentina_oberta(cv):
    """Escena 9: el registre de la sentina obert als peus d'en Bastida, amb l'aigua bruta i un vel de gasoil."""
    x0, y0, x1, y1 = 98, 172, 140, 186
    box(cv, x0 - 2, y0 - 2, x1 + 2, y1 + 2, ENG, 2.2)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            irid = math.sin(x * 0.7 + y * 1.3) * 0.5
            cv.put(x, y, FUEL if (x + y * 3) % 7 == 0 else DARK, 1.0 + irid, lit=0.3)
    # la tapa, aixecada contra el terra
    box(cv, x0 - 4, y0 - 14, x0 + 18, y0 - 4, ENG, 3.0)


PROPS = {'aigua': aigua, 'valvula_tancada': valvula_tancada, 'brida': brida, 'fosc': fosc, 'sentina_oberta': sentina_oberta}


def _frames_separador():
    """El pilot verd del separador parpelleja (treballa, a poc a poc)."""
    base = _render(False)
    cv = Canvas(light=LIGHT, img=base.copy())
    cv.rect(408, 120, 412, 124, CAB, 2.8)
    cv.flat(410, 122, (20, 60, 30))
    return [_diff(base, base), _diff(cv.img, base)]


ANIMS = {'separador': {'frames': _frames_separador, 'frameDuration': 700}}


# ─── Geometria ─────────────────────────────────────────────────────────────

GEOMETRIA = {
    'things': {
        'porta_passadis': {'rect': (2, 44, 60, 152), 'walk': (34, 176)},
        'boca': {'rect': (96, 98, 116, 132), 'walk': (106, 176)},
        'motor': {'rect': (122, 62, 272, 154), 'walk': (190, 176)},
        'porta_rebost': {'rect': (274, 54, 320, 152), 'walk': (297, 174)},
        'generador': {'rect': (328, 28, 416, 74), 'walk': (372, 186)},
        'quadre': {'rect': (322, 84, 368, 154), 'walk': (346, 186)},
        'sensor': {'rect': (370, 82, 386, 150), 'walk': (378, 186)},
        'vies': {'rect': (382, 132, 396, 150), 'walk': (392, 186)},
        'separador': {'rect': (398, 84, 426, 154), 'walk': (410, 186)},
        'porta_taller': {'rect': (428, 50, 479, 152), 'walk': (449, 176)},
        'valvula': {'rect': (VX - 14, 136, VX + 14, 186), 'walk': (VX + 30, 190)},
        'sentina': {'rect': (96, 170, 142, 188), 'walk': (150, 188)},
    },
    'spawns': {'iri': (176, 188), 'vet': (292, 190), 'bastida': (80, 180), 'diu': (200, 62)},
    'walkable': [(6, 172), (198, 172), (208, 189), (268, 189), (276, 172), (324, 172), (328, 185), (396, 185),
                 (400, 172), (474, 172), (478, 196), (2, 196)],
}
