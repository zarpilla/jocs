"""
Prova de resolució: la sala de màquines de l'Arenga a 640×360 (la composició de hd/rooms/sala_maquines.py ×4/3,
dibuixada de nou amb el detall que hi cap). Mateixes rampes, mateixos decorats i mateixes animacions.

  - la porta del passadís (oberta, amb el passadís de fons i el rètol SORTIDA) i l'escala a l'escotilla;
  - el tub de veu (placa PONT), el cartell MARPOL i el registre de la sentina (estergit SENTINA);
  - el motor principal parat: culates, injectors, portes del càrter, turbo, volant ratllat, panell local
    amb tres manòmetres a zero i la placa MOTOR 1;
  - les portes del REBOST (tancada) i del TALLER (oberta);
  - l'altell amb el generador i la caixa del relé; a sota, el quadre (interruptors, amperímetre, BOMBA),
    l'alarma amb el sensor desendollat, la vàlvula de tres vies i el separador;
  - a terra, la vàlvula de presa de mar sense volant i la bomba de sentina.
Decorats: `aigua`, `valvula_tancada`, `brida`, `fosc`, `sentina_oberta`.
Animacions: `separador`, `generador_marxa`, `bomba_marxa`, `aigua`.
"""
import math
from functools import lru_cache

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from hd.pix import Canvas, Light, W, H, hr, mix, B4, RUST
from hd.rooms.arenga import (WALL, ENG_LIGHT, DECK, CAB, LAG, REDP, YELL, SEAG, FUEL, SEP, DARK, WHITEP, BRASS,
                             WARM, RED_GLOW, box, rrect, bolt, hpipe, vpipe, glow)
from hd.rooms.comu import _diff, text, text_width

ENG = ENG_LIGHT
FLOOR_Y = 203
BOTTOM = 260                      # per sota hi ha la barra de verbs
LAMPS = ((248, 29), (496, 29))
MEZZ_Y = 99                       # el pis de reixa de l'altell
BRIDA = [(70, 70, 66), (150, 150, 142), (214, 214, 204), (246, 246, 238)]
STEELG = [(14, 16, 18), (26, 30, 32), (40, 46, 48), (58, 66, 68), (80, 90, 90), (108, 118, 116), (140, 150, 146)]
OILST = (16, 14, 10)

# Estat de les animacions mentre es dibuixa un fotograma (None = quiet, com el fons).
_ST = {'gen': None, 'pump': None, 'wt': 0.0}

LIGHT = Light(ambient=-0.5, vignette=(75, 40), floor_fade=None)
LIGHT.point(248, 35, r=211, k=2.6, squash=1.05, down=True, power=1.5)
LIGHT.point(496, 35, r=160, k=2.2, squash=1.05, down=True, power=1.5)
LIGHT.point(461, 112, r=120, k=1.5, squash=1.2, down=True, power=1.6)    # el llum de sota l'altell
LIGHT.point(45, 80, r=53, k=0.7, power=2.0)                               # emergència, sobre la porta
LIGHT.point(599, 160, r=45, k=0.5, power=2.0)                             # el taller, de l'altra banda


def _label(cv, s, cx, y, ramp=WHITEP, lvl=4.0, ink=(20, 24, 28), pad=3):
    """Rètol: placa amb vora i el text centrat (la font fa 5 px d'alt)."""
    w = text_width(s)
    x0 = cx - (w + 2 * pad) // 2
    box(cv, x0, y, x0 + w + 2 * pad - 1, y + 9, ramp, lvl)
    text(cv, s, x0 + pad, y + 2, None, 0, flat=ink)


# ─── La paret i el sostre ───────────────────────────────────────────────────

def wall(cv):
    for y in range(0, FLOOR_Y):
        for x in range(W):
            lvl = 3.1 + (hr(x // 3, y // 5) - 0.5) * 0.35
            if y >= 179:
                lvl -= 0.9 + (0.3 if hr(x // 6, y // 3) > 0.8 else 0)
            cv.put(x, y, WALL, lvl)
    for fx in range(-11, W, 85):                          # quadernes
        for x in range(fx, fx + 8):
            for y in range(27, FLOOR_Y):
                d = x - fx
                cv.put(x, y, WALL, 3.5 + (0.9 if d == 0 else 0.5 if d == 1 else -0.3 if d >= 6 else 0.1)
                       - (0.8 if y >= 179 else 0))
        for y in range(37, 176, 16):
            bolt(cv, fx + 3, y, WALL, 3.6)
            bolt(cv, fx + 5, y + 8, WALL, 3.4)
    for sy in (85, 149):                                  # soldadures, amb el cordó
        for x in range(W):
            cv.put(x, sy, WALL, 1.8)
            cv.put(x, sy + 1, WALL, 3.9 if (x // 2) % 2 else 3.4)
    cv.hline(0, W - 1, 179, WALL, 4.0)
    cv.hline(0, W - 1, 180, WALL, 2.2)
    cv.hline(0, W - 1, FLOOR_Y - 1, WALL, 1.0)
    for i in range(40):                                   # rovell que baixa de les soldadures
        x = int(hr(i, 7) * W)
        y0 = 88 if hr(i, 8) > 0.5 else 152
        n = 8 + int(hr(i, 9) * 24)
        for y in range(y0, min(FLOOR_Y - 2, y0 + n)):
            k = 0.55 * (1 - (y - y0) / n)
            for xx in (x, x + 1) if hr(i, 10) > 0.6 else (x,):
                if k > B4[y & 3][xx & 3] * 0.6:
                    cv.flat(xx, y, mix(cv.get(xx, y), RUST[3], k))


def ceiling(cv):
    cv.rect(0, 0, W - 1, 25, DARK, 2.0)
    for bx in range(-11, W, 85):
        box(cv, bx - 3, 0, bx + 11, 28, ENG, 1.6, grad=0.6)
        cv.vline(bx - 2, 1, 27, ENG, 2.6)
    for y in (7, 17):                                     # safates de cables, amb els cables de colors
        cv.hline(0, W - 1, y, CAB, 2.8)
        cv.hline(0, W - 1, y + 5, CAB, 1.6)
        for x in range(0, W, 6):
            cv.vline(x, y, y + 5, CAB, 2.2)
        for k, row in enumerate((y + 2, y + 3)):
            for x in range(W):
                if hr(x // 12, y, k) > 0.3:
                    cv.flat(x, row, [(20, 20, 24), (40, 36, 30), (70, 50, 34), (110, 40, 34), (30, 50, 80)]
                            [int(hr(x // 14, y, k + 3) * 5)])
        for x in range(30, W, 70):                        # brides de les safates
            cv.vline(x, y - 1, y + 6, CAB, 3.6)


def wall_pipes(cv):
    hpipe(cv, 123, W - 1, 53, 4, SEAG, 3.0, bands=range(139, W, 61), band_ramp=WHITEP)
    hpipe(cv, 123, W - 1, 68, 3, FUEL, 3.0, bands=range(168, W, 61), band_ramp=YELL)
    for x in range(139, W, 61):                           # fletxes del sentit, a les anelles
        for i in range(3):
            cv.vline(x + 4 + i, 53 - 2 + i, 53 + 2 - i, WHITEP, 4.4)
    for x in range(131, W, 64):                           # abraçadores
        cv.vline(x, 47, 59, CAB, 2.0)
        cv.vline(x + 1, 47, 59, CAB, 3.4)
        cv.vline(x, 64, 72, CAB, 2.0)
        cv.vline(x + 1, 64, 72, CAB, 3.4)
    # el tub d'aigua de mar baixa a terra entre el rebost i el quadre
    vpipe(cv, 425, 53, FLOOR_Y + 2, 3, SEAG, 2.8, bands=(128, 171), band_ramp=WHITEP)
    cv.disc(425, 57, 4, 4, SEAG, lambda nx, ny: 3.2 - nx - ny)


def lamps(cv):
    for lx, ly in LAMPS:
        box(cv, lx - 8, 21, lx + 8, 26, CAB, 3.0)
        cv.disc(lx, ly + 4, 8, 5, [(120, 90, 40), (200, 160, 80), (250, 220, 150), (255, 246, 220)], 2.6, lit=0)
        for gx in (-5, 0, 5):
            cv.vline(lx + gx, ly, ly + 9, CAB, 2.2, lit=0)
        cv.hline(lx - 8, lx + 8, ly + 5, CAB, 2.0, lit=0)


def lamp_glows(cv):
    for lx, ly in LAMPS:
        glow(cv, lx, ly + 5, 45, WARM, 0.55)
        glow(cv, lx, ly + 5, 16, (255, 240, 200), 0.6)
    glow(cv, 461, 109, 29, WARM, 0.45)
    glow(cv, 461, 109, 11, (255, 240, 200), 0.6)
    glow(cv, 45, 79, 35, RED_GLOW, 0.55)


# ─── Portes ────────────────────────────────────────────────────────────────

def _frame(cv, x0, y0, x1, y1, r=12):
    """Marc d'una porta estanca (cantons rodons a dalt)."""
    for t in range(4):
        for y in range(y0 - t, y1 + 1):
            for x in range(x0 - t, x1 + t + 1):
                dx = max(x0 - t + r - x, 0, x - (x1 + t - r))
                dy = max(y0 - t + r - y, 0)
                inside = dx * dx + dy * dy <= r * r
                inner = x0 - t + 1 <= x <= x1 + t - 1 and y >= y0 - t + 1
                ddx = max(x0 - t + 1 + r - x, 0, x - (x1 + t - 1 - r))
                ddy = max(y0 - t + 1 + r - y, 0)
                if inside and not (inner and ddx * ddx + ddy * ddy <= r * r):
                    cv.put(x, y, WALL, 4.4 - t * 0.8)


def _inside(x, y, x0, y0, x1, r=12):
    dx = max(x0 + r - x, 0, x - (x1 - r))
    dy = max(y0 + r - y, 0)
    return dx * dx + dy * dy <= r * r


def _sill(cv, x0, x1, y1):
    cv.rect(x0 + 1, y1 - 8, x1 - 1, y1 - 1, WALL, 2.6)
    cv.hline(x0 + 1, x1 - 1, y1 - 8, WALL, 4.0)
    for x in range(x0 + 4, x1 - 3, 6):
        bolt(cv, x, y1 - 5, WALL, 3.4)


def door_passadis(cv):
    """La porta del passadís, oberta: el passadís de baix, fosc, amb un llum llunyà i una porta al fons."""
    x0, y0, x1, y1 = 19, 88, 72, FLOOR_Y
    for y in range(y0, y1):
        for x in range(x0, x1 + 1):
            if _inside(x, y, x0, y0, x1):
                cv.put(x, y, DARK, 1.6 - abs(x - 45) / 40 + (0.9 if y > 176 else 0) - (y - y0) / 160, lit=0.3)
    # el fons del passadís: un marc més petit i el terra que s'allunya
    for y in range(122, 177):
        for x in (34, 56):
            cv.put(x, y, DARK, 2.6, lit=0)
    cv.hline(34, 56, 122, DARK, 2.6, lit=0)
    for y in range(177, y1 - 8):
        k = (y - 177) / (y1 - 185)
        xl, xr = round(34 - k * 14), round(56 + k * 15)
        for x in range(max(x0 + 1, xl), min(x1, xr) + 1):
            cv.put(x, y, DARK, 2.2 + k * 0.8 + (0.6 if (y % 5 == 0) else 0), lit=0.3)
    cv.disc(45, 101, 4, 2, [(80, 70, 50), (160, 140, 100), (210, 196, 150)], 1.6, lit=0)
    glow(cv, 45, 104, 16, (140, 130, 100), 0.35)
    _frame(cv, x0, y0, x1, y1)
    _sill(cv, x0, x1, y1)
    # la fulla, oberta contra la paret
    cv.poly([(5, y0 + 5), (16, y0 - 1), (16, y1 - 3), (5, y1 - 5)], ENG, lambda x, y: 2.8 - (x - 5) * 0.05)
    cv.vline(16, y0, y1 - 3, ENG, 4.2)
    for y in range(y0 + 13, y1 - 10, 29):
        box(cv, 7, y, 13, y + 4, ENG, 3.6)
        cv.put(8, y + 1, ENG, 5.2)
    for dx, dy in ((x0 - 6, 112), (x0 - 6, 165), (x1 + 3, 112), (x1 + 3, 165)):   # palanques del marc
        box(cv, dx, dy, dx + 3, dy + 8, CAB, 3.4)
    # llum d'emergència i el rètol verd de sortida
    box(cv, 37, 75, 53, 81, CAB, 2.6)
    cv.disc(45, 79, 7, 3, REDP, 4.6, lit=0)
    box(cv, 26, 61, 64, 71, SEAG, 3.4)
    text(cv, 'SORTIDA', 45 - text_width('SORTIDA') // 2, 64, None, 0, flat=(220, 240, 226))


def door_rebost(cv):
    """La porta del rebost, tancada (porta estanca amb palanques i nansa), amb el rètol."""
    x0, y0, x1, y1 = 373, 93, 419, FLOOR_Y
    _frame(cv, x0, y0, x1, y1)
    rrect(cv, x0, y0, x1, y1 - 8, 11, ENG, lambda x, y: 2.9 - (y - y0) * 0.005)
    rrect(cv, x0 + 5, y0 + 5, x1 - 5, y1 - 16, 7, ENG, lambda x, y: 3.25 - (y - y0) * 0.005)
    cv.hline(x0 + 8, x1 - 8, y0 + 5, ENG, 4.3)
    cv.hline(x0 + 8, x1 - 8, y1 - 16, ENG, 1.9)
    cv.vline(x1 - 5, y0 + 11, y1 - 19, ENG, 2.1)
    cv.vline(x0 + 5, y0 + 11, y1 - 19, ENG, 3.8)
    for dy in (y0 + 19, (y0 + y1) // 2 - 3, y1 - 32):     # palanques
        box(cv, x1 - 9, dy, x1 - 5, dy + 11, CAB, 3.8)
        cv.put(x1 - 8, dy + 1, CAB, 5.4)
        cv.put(x1 - 7, dy + 10, CAB, 1.6)
    for dy in (y0 + 19, y1 - 32):                         # frontisses
        box(cv, x0 + 5, dy, x0 + 9, dy + 8, CAB, 3.2)
        cv.put(x0 + 7, dy + 4, CAB, 5.0)
    box(cv, x0 + 13, 144, x0 + 32, 149, CAB, 3.6)         # nansa
    cv.hline(x0 + 14, x0 + 31, 144, CAB, 5.0)
    _sill(cv, x0, x1, y1)
    # un rastre gastat a la pintura, a l'alçada de la mà
    for y in range(136, 157):
        for x in range(x0 + 11, x0 + 35):
            if hr(x, y, 5) > 0.84:
                cv.put(x, y, ENG, 4.4)
    _label(cv, 'REBOST', (x0 + x1) // 2, 74)


def door_taller(cv):
    """La porta del taller, oberta: un taller petit amb llum de fluorescent i el tauler d'eines."""
    x0, y0, x1, y1 = 576, 88, 621, FLOOR_Y
    for y in range(y0, y1):
        for x in range(x0, x1 + 1):
            if _inside(x, y, x0, y0, x1):
                cv.put(x, y, WALL, 1.6 - abs(x - 599) / 53 - (y - y0) / 186, lit=0.4)
    # de l'altra banda: el tauler d'eines (amb les siluetes pintades) i el cantó del banc
    PEG = [(30, 24, 16), (52, 42, 26), (78, 64, 40), (104, 88, 56)]
    cv.rect(581, 109, 616, 149, PEG, 1.6, lit=0.3)
    for y in range(111, 148, 4):
        for x in range(583, 615, 4):
            cv.put(x, y, PEG, 0.6, lit=0.3)
    TOOL = [(14, 12, 10), (24, 22, 18), (40, 38, 32), (60, 58, 50), (90, 88, 80)]
    cv.rect(586, 114, 588, 133, TOOL, 1.8, lit=0.3)                   # tornavís
    cv.rect(585, 114, 589, 117, REDP, 2.2, lit=0.3)
    cv.rect(594, 117, 600, 122, TOOL, 1.8, lit=0.3)                   # martell
    cv.rect(596, 122, 598, 136, PEG, 2.6, lit=0.3)
    cv.rect(606, 114, 608, 137, TOOL, 1.8, lit=0.3)                   # clau anglesa
    cv.disc(607, 114, 3, 3, TOOL, 2.2, lit=0.3)
    cv.rect(593, 140, 611, 146, TOOL, 1.4, lit=0.3)
    cv.rect(581, 163, 621, 170, [(30, 22, 12), (56, 40, 22), (88, 64, 36), (120, 90, 52)], 2.2, lit=0.3)
    cv.hline(581, 621, 163, [(56, 40, 22), (120, 90, 52)], 2.4, lit=0.3)
    box(cv, 588, 156, 600, 162, REDP, 1.6)                            # una caixa d'eines vermella
    cv.rect(581, 171, 621, 194, DARK, 1.0, lit=0.2)
    cv.disc(599, 96, 11, 1.6, [(140, 150, 140), (220, 230, 220), (244, 250, 244)], 1.4, lit=0)
    glow(cv, 599, 99, 24, (200, 220, 210), 0.3)
    _frame(cv, x0, y0, x1, y1)
    _sill(cv, x0, x1, y1)
    # la fulla, oberta contra la paret (de cantó, a la dreta)
    cv.poly([(636, y0 + 5), (627, y0 - 1), (627, y1 - 3), (636, y1 - 5)], ENG, lambda x, y: 2.4 + (x - 627) * 0.04)
    cv.vline(637, y0 + 6, y1 - 6, ENG, 1.2)
    for y in range(y0 + 13, y1 - 10, 29):
        box(cv, 629, y, 633, y + 4, ENG, 3.2)
    for dx, dy in ((x0 - 6, 112), (x0 - 6, 165)):
        box(cv, dx, dy, dx + 3, dy + 8, CAB, 3.4)
    _label(cv, 'TALLER', (x0 + x1) // 2, 70)
    box(cv, 591, 56, 607, 63, CAB, 2.6)                               # llum d'emergència
    cv.disc(599, 60, 7, 3, REDP, 3.0, lit=0)


# ─── L'escala, l'escotilla i el registre de la sentina ────────────────────

def ladder(cv):
    """Escala de vaixell inclinada: del terra fins a l'escotilla del sostre (sortida d'emergència)."""
    cv.rect(83, 0, 123, 25, DARK, 0.6, lit=0)
    box(cv, 80, 23, 125, 28, CAB, 3.2)
    cv.hline(81, 124, 23, CAB, 4.6)
    for x in (85, 120):
        box(cv, x - 1, 10, x + 1, 23, CAB, 3.6)
    top, bot = 29, 227

    def edge(t, side):           # muntants: s'eixamplen cap a baix (vénen endavant)
        return (88 - t * 8, 117 + t * 8)[side]
    n = 17
    for i in range(1, n + 1):
        t = i / n
        y = round(top + (bot - top) * t ** 1.08)
        xa, xb = round(edge(t, 0)) + 2, round(edge(t, 1)) - 2
        d = 1 + round(t * 3)
        cv.rect(xa, y - d, xb, y - 1, STEELG, 4.4 - t * 0.6)
        cv.hline(xa, xb, y, STEELG, 2.0)
        cv.hline(xa, xb, y + 1, DARK, 1.2)
        for x in range(xa + 1, xb, 3):                     # antilliscant
            for yy in range(y - d, y):
                if (x + yy) % 2 == 0:
                    cv.put(x, yy, STEELG, 5.6)
        cv.hline(xa, xa + 2, y - d, YELL, 3.6)              # la vora del graó, pintada
        cv.hline(xb - 2, xb, y - d, YELL, 3.6)
    for side in (0, 1):
        for y in range(top, bot + 2):
            t = (y - top) / (bot - top)
            xc = round(edge(t, side))
            for k in range(4):
                cv.put(xc + k - 1, y, STEELG, (3.6 if side == 0 else 2.6) + (0.8 if k == 0 else -0.6 if k >= 2 else 0))
    for (ax, ay), (bx, by), side in (((77, 21), (67, 189), 0), ((128, 21), (139, 189), 1)):
        cv.line(ax, ay, bx, by, YELL, 3.8)
        cv.line(ax + 1, ay, bx + 1, by, YELL, 2.4)
        for t in (0.3, 0.75):
            y = round(top + (bot - top) * t)
            xr = round(ax + (bx - ax) * (y - ay) / (by - ay))
            xe = round(edge((y - top) / (bot - top), side))
            cv.hline(min(xr, xe), max(xr, xe), y, YELL, 2.6)
            cv.put(xr, y, YELL, 4.4)


def ladder_shadow(cv):
    cv.darken(72, 221, 136, 235, lambda x, y: 0.55 * max(0.0, 1 - abs(x - 104) / 35 - abs(y - 228) / 9))


def sentina(cv):
    """El registre de la sentina: una tapa de planxa amb cargols, dues nanses i l'estergit."""
    x0, y0, x1, y1 = 131, 229, 187, 248
    cv.poly([(x0 + 4, y0), (x1 - 4, y0), (x1, y1), (x0, y1)], DECK, lambda x, y: 2.2)
    cv.poly([(x0 + 7, y0 + 3), (x1 - 7, y0 + 3), (x1 - 3, y1 - 3), (x0 + 3, y1 - 3)], DECK,
            lambda x, y: 3.4 - (y - y0) * 0.03)
    cv.hline(x0 + 4, x1 - 4, y0, DECK, 1.0)
    cv.hline(x0, x1, y1, DECK, 4.2)
    for i in range(9):                                      # cargols
        t = i / 8
        bolt(cv, round(x0 + 5 + (x1 - x0 - 10) * t), y0 + 2, DECK, 4.2)
        bolt(cv, round(x0 + 3 + (x1 - x0 - 6) * t), y1 - 2, DECK, 4.4)
    for hx in (x0 + 9, x1 - 15):                            # nanses encastades
        cv.rect(hx, y0 + 6, hx + 5, y0 + 8, DARK, 0.8)
        cv.hline(hx, hx + 5, y0 + 9, DECK, 4.6)
    text(cv, 'SENTINA', (x0 + x1) // 2 - text_width('SENTINA') // 2, y0 + 11, YELL, 2.4)


# ─── El tub de veu i el cartell MARPOL ─────────────────────────────────────

def voice_tube(cv):
    vpipe(cv, 141, 27, 139, 3, BRASS, 2.8)
    for y in (45, 99):
        box(cv, 137, y, 145, y + 3, CAB, 3.2)
    cv.disc(141, 144, 5, 5, BRASS, lambda nx, ny: 3.2 - nx * 1.2 - ny * 1.0)
    cv.disc(141, 149, 9, 8, BRASS, lambda nx, ny: 3.5 - nx * 1.3 - ny * 1.2)
    cv.disc(141, 149, 7, 5, BRASS, lambda nx, ny: 1.2 + nx * 0.6 + ny * 0.8)
    cv.disc(141, 149, 4, 3, DARK, 0.6)
    for i, y in enumerate(range(158, 169)):                  # la cadeneta i el tap
        cv.put(147 + (i % 2), y, BRASS, 3.0 if i % 2 else 4.0)
    cv.disc(149, 172, 4, 3, BRASS, lambda nx, ny: 3.8 - nx - ny)
    box(cv, 142, 178, 164, 186, BRASS, 3.0)                  # la placa: PONT (a la dreta del passamà)
    text(cv, 'PONT', 153 - text_width('PONT') // 2, 180, BRASS, 0.8)


def marpol(cv):
    x0, y0, x1, y1 = 131, 75, 161, 115
    box(cv, x0, y0, x1, y1, WHITEP, 4.0)
    cv.rect(x0 + 1, y0 + 1, x1 - 1, y0 + 9, [(20, 30, 70), (30, 50, 110), (50, 80, 150), (90, 120, 190)], 2.2)
    text(cv, 'MARPOL', (x0 + x1) // 2 - text_width('MARPOL') // 2 + 1, y0 + 3, None, 0, flat=(226, 232, 240))
    cx, cy = (x0 + x1) // 2, y0 + 19
    cv.disc(cx, cy, 5, 5, REDP, 4.2)                         # prohibit: una gota d'oli barrada
    cv.disc(cx, cy, 4, 4, WHITEP, 4.6)
    cv.disc(cx, cy + 1, 1.6, 1.6, DARK, 1.0)
    cv.put(cx, cy - 1, DARK, 1.0)
    for i in range(-4, 5):
        cv.put(cx + i, cy + i, REDP, 4.2)
    for y in range(y0 + 27, y1 - 1, 2):
        for x in range(x0 + 3, x1 - 2):
            if hr(x // 3, y) > 0.25:
                cv.put(x, y, WHITEP, 1.6)


# ─── El motor principal ─────────────────────────────────────────────────────

def engine(cv):
    box(cv, 171, 187, 352, FLOOR_Y + 4, ENG, 2.0, grad=0.6)          # bancada
    for x in range(178, 350, 19):
        bolt(cv, x, 192, ENG, 2.6)
        bolt(cv, x + 1, 199, ENG, 2.4)
    box(cv, 181, 133, 341, 187, ENG, 3.0, grad=0.8)                  # càrter
    cv.hline(181, 341, 134, ENG, 4.1)
    for i in range(3):                                               # portes del càrter
        dx = 189 + i * 37
        rrect(cv, dx, 143, dx + 28, 175, 7, ENG, lambda x, y: 3.5 - (y - 143) * 0.025)
        rrect(cv, dx + 3, 146, dx + 25, 172, 5, ENG, lambda x, y: 2.9 - (y - 146) * 0.025)
        for bx, by in ((dx + 4, 147), (dx + 23, 147), (dx + 4, 170), (dx + 23, 170), (dx + 14, 145), (dx + 14, 173)):
            bolt(cv, bx, by, ENG, 3.4)
        cv.rect(dx + 10, 156, dx + 18, 160, WHITEP, 2.6)              # l'etiqueta de cada porta
        cv.put(dx + 12 + i, 158, DARK, 0.8)
    box(cv, 187, 112, 336, 133, ENG, 3.3, grad=0.5)                  # bloc
    hpipe(cv, 189, 334, 127, 1, FUEL, 3.2)                           # rail de combustible
    for i in range(4):                                               # culates, amb els injectors
        dx = 191 + i * 36
        rrect(cv, dx, 96, dx + 31, 115, 5, ENG, lambda x, y: 4.1 - (y - 96) * 0.055)
        cv.hline(dx + 5, dx + 26, 97, ENG, 5.2)
        for bx in (dx + 5, dx + 26):
            bolt(cv, bx, 101, ENG, 3.8)
            bolt(cv, bx, 110, ENG, 3.6)
        vpipe(cv, dx + 16, 115, 123, 1, ENG, 2.8)
        cv.line(dx + 20, 106, dx + 24, 126, FUEL, 3.6)               # el tub de l'injector
        cv.disc(dx + 20, 106, 1.5, 1.5, BRASS, 3.6)
    # col·lector d'escapament folrat (on seu en Diu) i la xemeneia cap al sostre
    hpipe(cv, 195, 341, 88, 5, LAG, 3.2, bands=range(213, 341, 35), band_ramp=CAB)
    for x in range(197, 340, 7):                                     # la costura del folre
        cv.put(x, 85, LAG, 2.2)
    vpipe(cv, 344, 27, 93, 8, LAG, 3.0, bands=range(37, 93, 19), band_ramp=CAB)
    cv.disc(344, 88, 8, 7, LAG, lambda nx, ny: 3.3 - nx - ny)
    # turbo
    cv.disc(352, 120, 13, 13, ENG, lambda nx, ny: 3.6 - nx * 1.4 - ny * 1.2)
    cv.disc(352, 120, 8, 8, ENG, lambda nx, ny: 2.6 + nx * 0.8 + ny * 0.8)
    for a in range(0, 360, 45):
        cv.put(352 + round(math.cos(math.radians(a)) * 6), 120 + round(math.sin(math.radians(a)) * 6), ENG, 1.6)
    cv.disc(352, 120, 3, 3, CAB, 4.6)
    # volant, amb la protecció ratllada groc i negre
    box(cv, 163, 133, 181, 195, ENG, 2.4)
    for y in range(136, 194):
        for x in range(165, 180):
            if ((x + y) // 5) % 2 == 0:
                cv.put(x, y, YELL, 3.6)
            else:
                cv.put(x, y, DARK, 3.0)
    # panell local amb tres manòmetres (a zero: el motor és parat)
    box(cv, 301, 139, 339, 168, CAB, 2.4)
    for gx in (309, 320, 331):
        cv.disc(gx, 150, 4.5, 4.5, CAB, 1.4)
        cv.disc(gx, 150, 3.5, 3.5, WHITEP, 4.6)
        for a in range(150, 391, 40):
            cv.put(gx + round(math.cos(math.radians(a)) * 3), 150 + round(math.sin(math.radians(a)) * 3), DARK, 1.2)
        cv.line(gx, 150, gx - 2, 152, DARK, 0)
        cv.flat(gx, 150, (180, 40, 30))
    for x in range(304, 337, 3):
        cv.put(x, 162, WHITEP, 3.0)
        cv.put(x + 1, 162, WHITEP, 2.2)
    box(cv, 236, 115, 286, 126, BRASS, 3.2)                          # placa de llautó
    text(cv, 'MOTOR 1', 261 - text_width('MOTOR 1') // 2, 118, BRASS, 0.9)
    # taques d'oli a la bancada i a terra
    for i in range(14):
        x = 186 + int(hr(i, 31) * 150)
        for y in range(196, 196 + 2 + int(hr(i, 32) * 6)):
            cv.flat(x, y, mix(cv.get(x, y), OILST, 0.5))


# ─── L'altell i el generador ───────────────────────────────────────────────

def mezzanine(cv):
    """Un altell de reixa damunt del quadre i del separador, amb mènsules a la paret i barana groga."""
    x0, x1, y = 429, 571, MEZZ_Y
    for mx in (440, 507, 560):                                        # mènsules
        cv.poly([(mx - 3, y + 5), (mx + 3, y + 5), (mx + 3, y + 24), (mx - 3, y + 8)], CAB, 2.6)
        cv.line(mx + 3, y + 5, mx + 3, y + 24, CAB, 3.6)
    box(cv, x0, y, x1, y + 5, CAB, 3.0)
    for x in range(x0 + 1, x1, 2):
        cv.put(x, y + 2, DARK, 1.0)
        cv.put(x + 1, y + 3, DARK, 1.0)
    cv.hline(x0, x1, y, CAB, 4.6)
    cv.darken(x0, y + 6, x1, y + 16, lambda xx, yy: 0.7 - (yy - y - 6) * 0.07)
    box(cv, 453, y + 6, 469, y + 9, CAB, 2.8)                         # el llum de sota l'altell
    cv.disc(461, y + 12, 7, 3, [(120, 90, 40), (200, 160, 80), (250, 220, 150), (255, 246, 220)], 2.6, lit=0)
    for gx in (-4, 0, 4):
        cv.vline(461 + gx, y + 10, y + 14, CAB, 2.2, lit=0)


def railing(cv):
    """La barana groga de l'altell (per davant del generador)."""
    x0, x1, y = 429, 571, MEZZ_Y
    for px in range(x0 + 3, x1, 28):
        cv.vline(px, y - 24, y - 1, YELL, 3.2)
        cv.vline(px + 1, y - 24, y - 1, YELL, 2.2)
    cv.hline(x0 + 3, x1 - 1, y - 24, YELL, 3.8)
    cv.hline(x0 + 3, x1 - 1, y - 23, YELL, 2.4)
    cv.hline(x0 + 3, x1 - 1, y - 12, YELL, 3.0)
    cv.hline(x0 + 3, x1 - 1, y - 11, YELL, 1.8)
    cv.hline(x0 + 3, x1 - 1, y - 3, YELL, 2.6)                       # el sòcol de la barana


def generator(cv):
    """El generador auxiliar: un dièsel petit (verd), l'alternador (gris) i la caixa del relé."""
    y1 = MEZZ_Y - 1
    box(cv, 440, y1 - 5, 552, y1, ENG, 2.2)                          # bancada
    for x in range(444, 552, 12):
        bolt(cv, x, y1 - 3, ENG, 3.4)
    box(cv, 445, 61, 493, y1 - 6, ENG, 3.1, grad=0.8)                # el dièsel
    g = _ST['gen']
    sh = 0 if g is None else (0, 1, 0, -1)[g % 4]                    # en marxa, les culates vibren
    for i in range(3):
        rrect(cv, 448 + i * 15 + sh, 51, 460 + i * 15 + sh, 64, 4, ENG, lambda x, y: 4.0 - (y - 51) * 0.07)
        bolt(cv, 451 + i * 15 + sh, 57, ENG, 4.2)
        bolt(cv, 457 + i * 15 + sh, 57, ENG, 4.0)
    cv.rect(451, 72, 488, 80, ENG, 2.4)                               # reixeta
    for x in range(452, 488, 3):
        cv.vline(x, 72, 80, ENG, 3.4)
    box(cv, 470, 84, 488, 90, YELL, 2.6, edge=False)                  # filtre d'oli
    cv.hline(470, 488, 84, YELL, 3.8)
    # la corretja i el volant (a l'esquerra)
    cv.disc(443, 77, 7, 7, ENG, lambda nx, ny: 3.4 - nx - ny)
    if g is not None:                                                 # el radi del volant, que gira
        a = math.radians(g * 67.5)
        for r in (3, 4, 5):
            cv.put(443 + round(math.cos(a) * r), 77 + round(math.sin(a) * r), CAB, 0.8)
            cv.put(443 - round(math.cos(a) * r), 77 - round(math.sin(a) * r), ENG, 5.0)
    cv.disc(443, 77, 2.5, 2.5, CAB, 4.0)
    # l'alternador: cilindre ajagut amb aletes
    for y in range(59, y1 - 5):
        u = (y - 76) / 17
        for x in range(496, 539):
            fin = x % 3 == 0
            cv.put(x, y, STEELG, 3.6 + 1.5 * (-0.3 - u) - 0.8 * u * u + (0.6 if fin else 0))
    cv.disc(539, 76, 5, 17, STEELG, lambda nx, ny: 2.6 - nx * 0.6 - ny)
    box(cv, 505, 64, 527, 70, YELL, 3.2)                              # placa groga
    text(cv, 'KVA', 516 - text_width('KVA') // 2, 65, None, 0, flat=(40, 30, 8))
    # la caixa del relé de sincronització, damunt de l'alternador
    box(cv, 512, 38, 541, 57, CAB, 3.4)
    cv.rect(517, 44, 526, 53, DARK, 0.6)                              # el sòcol del relé
    cv.rect(518, 45, 525, 52, CAB, 2.8)                               # el relé (un cub negre)
    cv.hline(518, 525, 45, CAB, 4.4)
    for px in (519, 521, 523):
        cv.put(px, 53, BRASS, 4.0)
    cv.flat(533, 45, (90, 240, 120))                                  # pilot verd
    glow(cv, 533, 45, 6, (90, 240, 120), 0.6)
    cv.flat(533, 51, (60, 30, 20))
    # el cable que baixa al quadre (per darrere de la barana)
    for y in range(y1 + 1, 112):
        cv.put(544, y, DARK, 1.6)
        cv.put(545, y, CAB, 2.2)
    # l'escapament, cap amunt
    vpipe(cv, 469, 27, 49, 3, LAG, 2.8, bands=(32,), band_ramp=CAB)


# ─── El quadre, l'alarma i el separador ─────────────────────────────────────

def panel(cv):
    x0, y0, x1, y1 = 432, 115, 491, FLOOR_Y + 2
    box(cv, x0, y0, x1, y1, CAB, 3.4, grad=1.0)
    box(cv, x0 - 3, y0 - 4, x1 + 3, y0, CAB, 3.8)
    for x in range(437, 486, 9):                                      # interruptors
        box(cv, x, 120, x + 5, 131, CAB, 2.0)
        cv.rect(x + 2, 122, x + 3, 127, DARK, 0.4)
        cv.rect(x + 2, 122, x + 3, 123, CAB, 5.0)
        cv.rect(x, 133, x + 5, 134, WHITEP, 3.4)
    for x, col in ((440, (90, 240, 120)), (448, (90, 240, 120)), (456, (255, 190, 60))):
        cv.flat(x, 140, col)
        cv.flat(x + 1, 140, col)
        cv.flat(x, 141, col)
        cv.flat(x + 1, 141, col)
        glow(cv, x, 140, 7, col, 0.6)
    cv.disc(477, 144, 8, 8, CAB, 1.8)                                 # amperímetre
    cv.disc(477, 144, 7, 7, WHITEP, 4.4)
    for a in range(200, 341, 20):
        cv.put(477 + round(math.cos(math.radians(a)) * 5.5), 144 + round(math.sin(math.radians(a)) * 5.5), DARK, 0)
    cv.put(482, 140, REDP, 4.0)
    g = _ST['gen']
    tip = (480, 139) if g is None else ((480, 139), (481, 139), (480, 139), (479, 139))[g % 4]
    cv.line(477, 145, tip[0], tip[1], REDP, 4.0)
    cv.put(477, 145, DARK, 0)
    # l'interruptor de la bomba de sentina (la maneta en OFF)
    box(cv, 440, 155, 461, 181, CAB, 2.6)
    cv.disc(451, 167, 7, 7, DARK, 1.6)
    cv.disc(451, 167, 5, 5, CAB, 2.4)
    cv.rect(449, 157, 453, 171, REDP, 4.2)
    cv.vline(449, 157, 171, REDP, 5.0)
    text(cv, 'OFF', 443, 174, WHITEP, 3.4)
    box(cv, 439, 183, 462, 191, WHITEP, 3.6)                          # etiqueta «BOMBA»
    text(cv, 'BOMBA', 451 - text_width('BOMBA') // 2, 185, None, 0, flat=(24, 26, 30))
    box(cv, 469, 160, 472, 173, CAB, 4.4)                             # nansa de la porta
    cv.poly([(480, 176), (487, 188), (473, 188)], YELL, 4.0)          # alta tensió
    cv.line(481, 179, 479, 183, DARK, 0)
    cv.line(479, 183, 481, 186, DARK, 0)
    for y in range(194, 202, 2):
        cv.hline(469, 487, y, CAB, 1.4)


def alarm(cv):
    """L'alarma de sentina, amb el cable del sensor desendollat penjant."""
    box(cv, 496, 117, 512, 136, CAB, 3.2)
    cv.disc(504, 115, 5, 4, REDP, lambda nx, ny: 2.0 - nx - ny)        # llum apagada
    for x in range(500, 509, 2):
        cv.put(x, 113, REDP, 1.0)
    cv.rect(499, 125, 509, 131, WHITEP, 3.0)
    for x in range(500, 509, 2):
        cv.put(x, 128, DARK, 1.2)
    pts = [(504, 137), (503, 147), (500, 156), (499, 165), (500, 173), (503, 179)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        cv.line(ax, ay, bx, by, DARK, 2.6)
        cv.line(ax + 1, ay, bx + 1, by, CAB, 2.6)
    box(cv, 500, 179, 505, 187, CAB, 3.4)                             # la clavilla
    cv.put(501, 188, BRASS, 4.0)
    cv.put(504, 188, BRASS, 4.0)
    box(cv, 496, 192, 507, 200, CAB, 2.8)                             # la presa buida
    cv.put(500, 196, DARK, 0)
    cv.put(503, 196, DARK, 0)


def separator(cv):
    """El separador d'aigües oleoses (dipòsit alt amb visor), la vàlvula de tres vies i la sortida a la borda."""
    x0, x1, top = 525, 565, 120
    cx, rx = (x0 + x1) / 2, (x1 - x0) / 2
    for y in range(top, FLOOR_Y + 4):
        for x in range(x0, x1 + 1):
            u = (x - cx) / (rx + 0.5)
            cv.put(x, y, SEP, 3.2 + 1.5 * (-0.3 - u) - 0.9 * u * u)
    cv.disc(cx, top, rx, 7, SEP, lambda nx, ny: 3.6 - nx * 1.3 - ny * 1.5)
    for y in (144, 184):                                              # les brides
        for x in range(x0, x1 + 1):
            cv.put(x, y, SEP, 1.6)
            cv.put(x, y + 1, SEP, 4.4)
        for x in range(x0 + 3, x1, 6):
            cv.put(x, y - 1, SEP, 5.0)
    box(cv, 531, 128, 536, 176, CAB, 2.6)                             # visor: oli a dalt, aigua a sota
    for y in range(130, 175):
        col = FUEL if y < 144 else [(14, 30, 34), (24, 50, 54), (44, 80, 82), (80, 120, 120)]
        for x, lv in ((532, 3.4), (533, 2.9), (534, 2.6)):
            cv.put(x, y, col, (lv if y < 144 else lv - 0.8), lit=0.4)
    cv.hline(532, 534, 144, YELL, 4.0, lit=0)
    cv.disc(553, 131, 5, 5, CAB, 2.0)                                 # manòmetre
    cv.disc(553, 131, 4, 4, WHITEP, 4.6)
    for a in range(150, 391, 48):
        cv.put(553 + round(math.cos(math.radians(a)) * 3), 131 + round(math.sin(math.radians(a)) * 3), DARK, 1.2)
    g = _ST['gen']
    cv.line(553, 131, 556, 128 + (0 if g is None or g % 2 == 0 else 1), DARK, 0)
    box(cv, 540, 149, 561, 168, CAB, 2.8)                             # caixa de control
    cv.rect(543, 152, 558, 156, [(6, 30, 14), (12, 70, 30), (40, 150, 70), (120, 240, 140)], 1.6, lit=0)
    for x in range(544, 557, 2):
        cv.put(x, 154, [(6, 30, 14), (40, 150, 70), (160, 255, 180)], 2, lit=0)
    cv.flat(547, 163, (90, 255, 120))
    cv.flat(548, 163, (90, 255, 120))
    glow(cv, 547, 163, 8, (90, 255, 120), 0.6)
    cv.flat(555, 163, (60, 30, 20))
    cv.flat(556, 163, (60, 30, 20))
    text(cv, '15PPM', 551 - text_width('15PPM') // 2, 172, None, 0, flat=(40, 36, 22))
    # la canonada de la bomba: puja per x=517 fins a la vàlvula de tres vies
    vpipe(cv, 517, 189, FLOOR_Y + 8, 3, CAB, 2.8)
    hpipe(cv, 517, 524, 187, 3, CAB, 3.0)                             # cap al separador
    vpipe(cv, 517, 109, 181, 3, CAB, 2.6)                             # cap a la borda (puja per l'altell)
    cv.disc(517, 187, 7, 7, REDP, lambda nx, ny: 3.8 - nx - ny)       # vàlvula de tres vies, cap a SEPARADOR
    cv.line(517, 187, 524, 195, REDP, 4.6)
    cv.line(518, 187, 525, 195, REDP, 3.2)
    cv.disc(517, 187, 2, 2, CAB, 4.4)
    box(cv, 512, 165, 523, 171, WHITEP, 3.0)                          # BORDA (a dalt)
    cv.poly([(517, 166), (520, 170), (514, 170)], DARK, 1.0)
    box(cv, 525, 192, 536, 198, YELL, 3.8)                            # SEPARADOR
    cv.poly([(527, 195), (532, 193), (532, 197)], DARK, 1.0)


# ─── El terra (planxa estriada) i l'aigua ─────────────────────────────────

VP = (320, 53)


def floor(cv):
    mask = [[False] * W for _ in range(H)]
    for y in range(FLOOR_Y, BOTTOM + 16):
        d = y - VP[1]
        for x in range(W):
            u = VP[0] + (x - VP[0]) * 200 / d
            u2 = VP[0] + (x + 1 - VP[0]) * 200 / d
            v = 4267 / d
            lvl = 2.5
            if int(u // 101) != int(u2 // 101):
                lvl = 1.0
            elif y in (211, 227, 249):
                lvl = 1.1
            elif y in (212, 228, 250):
                lvl = 3.3
            else:
                a, b = int(u * 0.5) % 4, int(v * 1.6) % 4
                if (a == 0 and b in (0, 1)) or (a == 2 and b in (2, 3)):
                    lvl += 0.9
                elif (a == 1 and b == 1) or (a == 3 and b == 3):
                    lvl -= 0.3
            cv.put(x, y, DECK, lvl)
            mask[y][x] = True
    for i in range(10):                                               # taques d'oli velles
        cx, cy = 150 + int(hr(i, 51) * 360), FLOOR_Y + 8 + int(hr(i, 52) * 40)
        rx, ry = 4 + hr(i, 53) * 9, 1.5 + hr(i, 54) * 2.5
        for y in range(int(cy - ry), int(cy + ry) + 1):
            for x in range(int(cx - rx), int(cx + rx) + 1):
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1 and hr(x, y, 55) > 0.3:
                    cv.flat(x, y, mix(cv.get(x, y), OILST, 0.35))
    return mask


def water(cv, mask):
    """Dos dits d'aigua: tint fosc i verdós, reflex de la paret, ones i les espurnes dels llums."""
    src = cv.img.copy().load()
    WC = (10, 34, 40)
    for y in range(FLOOR_Y, BOTTOM + 16):
        depth = (y - FLOOR_Y) / (BOTTOM - FLOOR_Y)
        for x in range(W):
            if not mask[y][x]:
                continue
            c = mix(cv.get(x, y), WC, 0.38)
            sy = 2 * FLOOR_Y - y - 1
            sx = x + round(math.sin(y * 0.68 + x * 0.04 + _ST['wt']) * 1.9)
            if 0 <= sy < FLOOR_Y and 0 <= sx < W:
                c = mix(c, src[sx, sy][:3], 0.55 * max(0.0, 1 - depth * 1.3))
            lit = LIGHT(x, y)
            if (math.sin(x * 0.16 + y * 1.42 + math.sin(y * 0.28) * 4 - _ST['wt']) > 0.93 and lit > 0.2
                    and hr(x // 5, y) > 0.3):
                c = mix(c, (140, 190, 180), min(0.5, 0.18 + lit * 0.12))
            cv.flat(x, y, c)
    for x in range(W):
        if mask[FLOOR_Y][x] and hr(x // 6, 5) > 0.55:
            cv.flat(x, FLOOR_Y, mix(cv.get(x, FLOOR_Y), (150, 190, 180), 0.25))
    for lx, _ in LAMPS:
        for y in range(FLOOR_Y + 4, BOTTOM + 10):
            t = (y - FLOOR_Y) / 61
            wdt = 4 + t * 12
            for x in range(int(lx - wdt * 2), int(lx + wdt * 2) + 1):
                if not (0 <= x < W) or not mask[y][x]:
                    continue
                g = math.exp(-((x - lx) / wdt) ** 2) * (1 - t * 0.55)
                seg = hr(x // (2 + int(t * 5)), y, lx, round(_ST['wt'] * 4 / math.pi) % 8)
                if seg < g * 0.55:
                    cv.flat(x, y, mix(cv.get(x, y), WARM, min(0.8, 0.35 + g * 0.5)))
                elif seg < g * 0.9:
                    cv.flat(x, y, mix(cv.get(x, y), WARM, 0.18))


def reflect_obj(cv, mask, x0, x1, top, base, k=0.4):
    src = cv.img.copy().load()
    for y in range(base + 1, min(BOTTOM + 16, base + (base - top) + 1)):
        sy = 2 * base - y
        f = k * (1 - (y - base) / (base - top + 1))
        for x in range(x0, x1 + 1):
            if not mask[y][x]:
                continue
            sx = x + round(math.sin(y * 0.68 + _ST['wt']) * 1.6)
            if x0 <= sx <= x1 and top <= sy <= base and src[sx, sy][3] and not mask[sy][sx]:
                cv.flat(x, y, mix(cv.get(x, y), src[sx, sy][:3], f))


def unmask(mask, cv, x0, y0, x1, y1, before):
    a, b = before.load(), cv.img.load()
    for y in range(max(0, y0), min(H, y1 + 1)):
        for x in range(max(0, x0), min(W, x1 + 1)):
            if a[x, y] != b[x, y]:
                mask[y][x] = False


# ─── Objectes a terra ───────────────────────────────────────────────────────

VX = 315            # l'eix de la vàlvula de presa de mar


def sea_valve(cv):
    """La vàlvula de presa de mar: s'ha aixecat una planxa del terra. Sense volant."""
    cv.poly([(VX - 35, 229), (VX + 37, 229), (VX + 43, 248), (VX - 40, 248)], DARK,
            lambda x, y: 1.0 + (248 - y) * 0.03)
    cv.hline(VX - 35, VX + 37, 229, DECK, 1.0)
    cv.line(VX - 40, 248, VX + 43, 248, DECK, 4.0)
    for x in range(VX - 34, VX + 38):                                  # l'aigua de la sentina, al fons del forat
        if hr(x // 3, 1) > 0.4:
            cv.put(x, 240 + int(hr(x, 2) * 4), [(10, 40, 46), (40, 90, 90), (110, 160, 150)], 1.4)
    for x in range(VX - 33, VX + 36, 9):                               # les costelles de sota el terra
        cv.vline(x, 231, 238, DECK, 1.8)
    # la planxa, recolzada de cantó contra la bancada del motor (a l'esquerra)
    cv.poly([(VX - 67, 189), (VX - 37, 187), (VX - 35, 237), (VX - 64, 235)], DECK,
            lambda x, y: 4.2 - (y - 187) * 0.022)
    for y in range(191, 235, 4):
        for x in range(VX - 64, VX - 37, 4):
            cv.put(x + (y // 4) % 2 * 2, y, DECK, 5.4)
    cv.line(VX - 37, 187, VX - 35, 237, DECK, 1.0)
    for bx, by in ((VX - 63, 192), (VX - 40, 190), (VX - 61, 232), (VX - 38, 234)):
        cv.put(bx, by, DARK, 0.4)
    # el cos (vermell), la tapa i l'eix pelat
    cv.disc(VX, 237, 17, 8, REDP, lambda nx, ny: 3.4 - nx * 1.2 - ny * 1.4)
    for bx in range(VX - 13, VX + 16, 7):
        bolt(cv, bx, 233, REDP, 4.0)
    box(cv, VX - 7, 213, VX + 7, 231, REDP, 3.6)
    cv.hline(VX - 9, VX + 9, 213, REDP, 4.6)
    for bx in (VX - 7, VX + 7):
        bolt(cv, bx, 215, REDP, 4.2)
    vpipe(cv, VX, 188, 213, 1, CAB, 4.6)
    box(cv, VX - 3, 185, VX + 3, 189, CAB, 5.0)                       # el quadradet on anava el volant
    cv.put(VX, 187, CAB, 2.0)


def bilge_pump(cv):
    """La bomba de sentina: motor elèctric i bomba vermella, amb el tub cap a la vàlvula de tres vies."""
    vpipe(cv, 517, 203, 219, 3, CAB, 2.8)
    box(cv, 440, 235, 523, 243, ENG, 2.0)
    for x in (444, 518):
        bolt(cv, x, 239, ENG, 3.6)
    pp = _ST['pump']
    ph = 0 if pp is None else pp % 3                                  # en marxa, les aletes brunzeixen
    jig = 0 if pp is None else (0, 1)[pp % 2]
    for y in range(213, 236):
        u = (y - 224) / 12
        for x in range(445, 488):
            cv.put(x, y + (jig if y < 216 else 0), ENG,
                   3.4 + 1.5 * (-0.3 - u) - 0.8 * u * u + (0.6 if (x + ph) % 3 == 0 else 0))
    cv.disc(445, 224, 4, 11, ENG, 2.0)
    box(cv, 461, 207, 475, 214, CAB, 3.0)                             # caixa de borns
    cv.put(464, 210, BRASS, 4.0)
    cv.put(472, 210, BRASS, 4.0)
    box(cv, 449, 219, 459, 223, WHITEP, 3.6)                          # la placa del motor
    cv.hline(450, 458, 221, DARK, 1.6)
    cv.disc(501, 224, 12, 12, REDP, lambda nx, ny: 3.8 - nx * 1.2 - ny * 1.2)
    cv.disc(501, 224, 4, 4, REDP, 2.0)
    for a in range(0, 360, 60):
        bolt(cv, 501 + round(math.cos(math.radians(a)) * 9), 224 + round(math.sin(math.radians(a)) * 9), REDP, 4.4)
    if pp is not None:                                                # l'eix de la bomba, que gira
        a = math.radians(pp * 60)
        for r in (2, 3):
            cv.put(501 + round(math.cos(a) * r), 224 + round(math.sin(a) * r), REDP, 5.4)
            cv.put(501 - round(math.cos(a) * r), 224 - round(math.sin(a) * r), REDP, 0.6)
    j = 0 if pp is None else pp % 2
    box(cv, 488 + j, 221, 492 + j, 227, CAB, 3.6)                     # l'acoblament
    hpipe(cv, 507, 517, 219, 3, CAB, 2.8)


# ─── Muntatge ───────────────────────────────────────────────────────────────

@lru_cache(maxsize=2)
def _render(wet):
    return _draw(wet)


def _draw(wet, gen=None, pump=None, wt=0.0):
    """La sala sencera; `gen`, `pump` i `wt` són el fotograma de cada animació (None/0 = quiet)."""
    _ST.update(gen=gen, pump=pump, wt=wt)
    try:
        return _draw_room(wet)
    finally:
        _ST.update(gen=None, pump=None, wt=0.0)


def _draw_room(wet):
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
    for fn, (x0, y0, x1, y1), base in ((ladder, (69, 0, 139, 235), 227), (sentina, (128, 227, 189, 251), 248),
                                       (sea_valve, (VX - 69, 184, VX + 45, 253), 243),
                                       (bilge_pump, (437, 200, 525, 245), 243)):
        before = cv.img.copy()
        fn(cv)
        unmask(mask, cv, x0, max(y0, FLOOR_Y), x1, y1, before)
        if wet and fn is not sentina:
            reflect_obj(cv, mask, x0, x1, max(y0, 160), base)
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
    y = 185
    CHR = [(30, 34, 40), (70, 78, 86), (120, 130, 138), (170, 178, 184), (214, 220, 224), (244, 246, 248)]
    hpipe(cv, VX - 27, VX + 27, y, 2, CHR, 3.0)
    for ex in (VX - 30, VX + 28):                                    # tacs de goma negra
        box(cv, ex, y - 3, ex + 2, y + 3, DARK, 2.2)
    box(cv, VX - 4, y - 4, VX + 4, y + 4, CAB, 4.4)                  # el nus al quadradet
    cv.put(VX, y, CAB, 1.2)
    cv.put(VX - 1, y - 1, CAB, 1.6)


def brida(cv):
    """La brida blanca que lliga l'interruptor de la bomba a la nansa del quadre (nus Bastida)."""
    for y in range(160, 172):
        cv.put(447, y, BRIDA, 2.6)
        cv.put(455, y, BRIDA, 2.2)
    cv.hline(447, 455, 160, BRIDA, 3.0)
    cv.hline(447, 469, 171, BRIDA, 2.6)
    cv.hline(455, 469, 172, BRIDA, 1.6)
    cv.disc(456, 172, 3, 2, BRIDA, 3.2)                               # el nus, amb una volta de més
    cv.disc(459, 173, 2, 1.5, BRIDA, 2.8)
    cv.put(460, 175, BRIDA, 2.4)
    cv.put(461, 176, BRIDA, 2.0)
    cv.put(462, 177, BRIDA, 1.6)


def fosc(cv):
    """El generador parat: tot a les fosques, menys els llums d'emergència vermells."""
    lights = ((45, 79), (599, 60), (461, 111))
    P = cv.img.load()
    for y in range(H):
        for x in range(W):
            r = min(math.hypot(x - lx, (y - ly) * 1.1) for lx, ly in lights)
            red = max(0.0, 1 - r / 93) ** 1.6
            a = 0.84 - 0.42 * red
            k = 0.5 * red
            col = mix((2, 4, 10), (120, 14, 10), k)
            P[x, y] = col + (int(255 * a),)
    for lx, ly in lights:                                             # els llums mateixos
        for y in range(ly - 3, ly + 4):
            for x in range(lx - 7, lx + 8):
                if ((x - lx) / 7) ** 2 + ((y - ly) / 3) ** 2 <= 1:
                    P[x, y] = (255, 80 + int(60 * hr(x, y)), 60, 255)


def sentina_oberta(cv):
    """Escena 9: el registre de la sentina obert als peus d'en Bastida, amb l'aigua bruta i un vel de gasoil."""
    x0, y0, x1, y1 = 131, 229, 187, 248
    box(cv, x0 - 3, y0 - 3, x1 + 3, y1 + 3, ENG, 2.2)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            irid = math.sin(x * 0.52 + y * 0.98) * 0.5
            c = FUEL if (x + y * 3) % 7 == 0 else DARK
            cv.put(x, y, c, 1.0 + irid, lit=0.3)
            if (x * 3 + y * 5) % 23 == 0:                             # l'irisació del gasoil
                cv.flat(x, y, mix(cv.get(x, y), (90, 60, 120), 0.4))
    # la tapa, aixecada contra el terra
    box(cv, x0 - 5, y0 - 19, x0 + 24, y0 - 5, ENG, 3.0)
    for bx in range(x0 - 2, x0 + 23, 6):
        bolt(cv, bx, y0 - 17, ENG, 4.2)


PROPS = {'aigua': aigua, 'valvula_tancada': valvula_tancada, 'brida': brida, 'fosc': fosc, 'sentina_oberta': sentina_oberta}


# ─── Animacions ────────────────────────────────────────────────────────────

def _frames_separador():
    """El pilot verd del separador parpelleja (treballa, a poc a poc)."""
    base = _render(False)
    cv = Canvas(light=LIGHT, img=base.copy())
    cv.rect(544, 160, 551, 166, CAB, 2.8)
    cv.flat(547, 163, (20, 60, 30))
    cv.flat(548, 163, (20, 60, 30))
    return [_diff(base, base), _diff(cv.img, base)]


def _frames_generador():
    """El generador en marxa: les culates vibren, el volant gira i les agulles de l'amperímetre i del
    manòmetre del separador tremolen."""
    base = _render(False)
    return [_diff(_draw(False, gen=i), base) for i in range(8)]


def _frames_bomba():
    """La bomba de sentina en marxa (Escena 1, un cop engegada): el motor brunzeix i l'eix gira."""
    base = _render(False)
    return [_diff(_draw(False, pump=i), base) for i in range(6)]


def _frames_aigua():
    """El decorat `aigua`, amb les ones: el reflex de la paret es gronxa i les espurnes dels llums corren."""
    dry = _render(False)
    return [_diff(_draw(True, wt=i * 2 * math.pi / 8), dry) for i in range(8)]


ANIMS = {'separador': {'frames': _frames_separador, 'frameDuration': 700},
         'generador_marxa': {'frames': _frames_generador, 'frameDuration': 90},
         'bomba_marxa': {'frames': _frames_bomba, 'frameDuration': 100},
         'aigua': {'frames': _frames_aigua, 'frameDuration': 200}}


# ─── Geometria (coordenades de 640×360) ─────────────────────────────────────

GEOMETRIA = {
    'things': {
        'porta_passadis': {'rect': (3, 59, 80, 203), 'walk': (45, 235)},
        'boca': {'rect': (128, 131, 155, 176), 'walk': (141, 235)},
        'motor': {'rect': (163, 83, 363, 205), 'walk': (253, 235)},
        'porta_rebost': {'rect': (365, 72, 427, 203), 'walk': (396, 232)},
        'generador': {'rect': (437, 37, 555, 99), 'walk': (496, 248)},
        'quadre': {'rect': (429, 112, 491, 205), 'walk': (461, 248)},
        'sensor': {'rect': (493, 109, 515, 200), 'walk': (504, 248)},
        'vies': {'rect': (509, 176, 528, 200), 'walk': (523, 248)},
        'separador': {'rect': (531, 112, 568, 205), 'walk': (547, 248)},
        'porta_taller': {'rect': (571, 67, 639, 203), 'walk': (599, 235)},
        'valvula': {'rect': (VX - 19, 181, VX + 19, 248), 'walk': (VX + 40, 253)},
        'sentina': {'rect': (128, 227, 189, 251), 'walk': (200, 251)},
    },
    'spawns': {'iri': (235, 251), 'vet': (389, 253), 'bastida': (107, 240), 'diu': (267, 83)},
    'walkable': [(8, 229), (264, 229), (277, 252), (357, 252), (368, 229), (432, 229), (437, 247), (528, 247),
                 (533, 229), (632, 229), (637, 261), (3, 261)],
}
