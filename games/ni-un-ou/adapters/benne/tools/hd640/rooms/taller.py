"""
Prova de resolució: el taller de l'Arenga a 640×360 (la composició de hd/rooms/taller.py ×4/3, dibuixada de nou
amb el detall que hi cap). Mateixes rampes, mateixos props i mateixes animacions.

  - un taller petit, endreçat com un quiròfan: paret verda de planxa, llum de fluorescent;
  - a l'esquerra, la porta estanca oberta cap a la sala de màquines;
  - el tauler d'eines, amb la silueta pintada de cada eina; una silueta és buida (la clau de vàlvules);
    a la barra de sota, la cisalla de mànecs vermells i la clau de tubs (props);
  - el banc de treball, amb el cargol de banc, un torn petit, calaixos i un entrepà vell en un plat;
  - un prestatge amb pots i capses (M6, M8), un extintor (CO2), un rotllo de cable i un bidó d'OLI.
Animacions: `fluorescent` (la reactància cansada: pampallugues) i `mosca` (no deixa en pau l'entrepà).
"""
import math
from functools import lru_cache

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from PIL import Image

from hd.pix import Canvas, Light, W, H, hr, mix
from hd.rooms.arenga import (WALL, ENG_LIGHT as ENG, DECK, CAB, REDP, YELL, SEAG, DARK, WHITEP, BRASS,
                             box, rrect, bolt, hpipe, vpipe, glow)
from hd.rooms.comu import _diff, text, text_width
from hd640.rooms.sala_maquines import ceiling
from hd640.rooms.rebost import plate_wall, checker_floor, floor_shadow, engine_door, FLOOR_Y

# Art a 2× (1280×720 per a una sala de 640×360): el mateix dibuix, amb les formes, el dither i la llum a la
# resolució real (hd1280/canvas2x.py); el motor el mostra a 1/2 (artScale al .room.json).
ART_SCALE = 2
from hd1280.canvas2x import Canvas2x as Canvas  # noqa: E402,F811
from hd.pix import Canvas as Canvas1x  # noqa: E402,F401  (llenços auxiliars en píxels de sala: figures, textos)

TUBE = (320, 21)                       # el fluorescent
COOL = (220, 236, 230)
PEG = [(20, 16, 10), (40, 32, 20), (62, 50, 32), (88, 72, 46), (116, 96, 62), (146, 124, 82), (178, 154, 106)]
WOOD = [(24, 14, 8), (44, 26, 14), (68, 42, 22), (96, 62, 32), (126, 84, 44), (156, 110, 60), (186, 140, 82),
        (212, 172, 112)]
SIL = [(150, 140, 110), (196, 186, 150), (232, 224, 196)]     # pintura de les siluetes
STEELT = [(14, 16, 20), (28, 32, 38), (46, 52, 60), (68, 76, 86), (96, 104, 114), (130, 138, 146), (170, 176, 182),
          (214, 218, 222)]
BREAD = [(60, 34, 14), (104, 62, 26), (150, 96, 44), (190, 134, 70), (220, 172, 108)]
GREENT = [(14, 26, 14), (26, 50, 24), (44, 80, 36), (70, 112, 50), (100, 146, 70)]
RUBBER = [(10, 10, 12), (22, 22, 26), (38, 38, 44), (58, 58, 66)]
TUBEC = [(140, 150, 146), (200, 214, 208), (236, 246, 242), (255, 255, 255)]

LIGHT = Light(ambient=-0.3, vignette=(80, 35), floor_fade=(248, 53))
LIGHT.point(TUBE[0], TUBE[1] + 8, r=307, k=2.7, squash=1.25, down=True, power=1.4)
LIGHT.point(45, 147, r=53, k=0.4, power=2.0)                      # la sala de màquines, per la porta

BOARD = (112, 40, 413, 160)           # el tauler d'eines (x0, y0, x1, y1)
RAIL_Y = 125                          # la barra de ganxos de baix, on pengen la cisalla i la clau de tubs
BENCH_TOP = 149


# ─── Paret, sostre, terra ─────────────────────────────────────────────────

def room(cv):
    plate_wall(cv, seed=3)
    ceiling(cv)
    hpipe(cv, 80, W - 1, 32, 3, SEAG, 3.0, bands=range(120, W, 80), band_ramp=WHITEP)
    for x in range(93, W, 80):
        cv.vline(x, 26, 38, CAB, 2.0)
        cv.vline(x + 1, 26, 38, CAB, 3.4)
    # el fluorescent: la pantalla, els cables de penjar i el tub
    tx = TUBE[0]
    for hx in (tx - 44, tx + 44):
        cv.vline(hx, 12, 19, CAB, 2.4)
    box(cv, tx - 53, 20, tx + 53, 27, CAB, 3.0)
    cv.hline(tx - 52, tx + 52, 20, CAB, 4.4)
    for ex in (tx - 53, tx + 50):                                   # els capçals
        box(cv, ex, 27, ex + 3, 31, CAB, 2.6)
    cv.rect(tx - 49, 28, tx + 49, 31, TUBEC, 2.6, lit=0)
    cv.hline(tx - 49, tx + 49, 28, TUBEC, 3.6, lit=0)


def lights(cv):
    glow(cv, TUBE[0], 32, 93, COOL, 0.22)
    glow(cv, TUBE[0], 29, 27, (255, 255, 255), 0.4)


# ─── La porta (cap a la sala de màquines) ─────────────────────────────────

def _engine_far(cv):
    """L'altra banda: la sala de màquines, verda i fosca, amb un tub i un cilindre del motor."""
    x0, x1 = 19, 72
    for y in range(107, 112):
        for x in range(x0, x1 + 1):
            cv.put(x, y, SEAG, 2.4 - (y - 107) * 0.3, lit=0.2)
    for y in range(128, 182):
        for x in range(48, 67):
            u = (x - 57) / 9
            cv.put(x, y, ENG, 2.6 - u * 0.8 - u * u + (0.5 if (y - 128) % 12 == 0 else 0), lit=0.2)
    box(cv, 46, 122, 69, 128, ENG, 2.4)


def door(cv):
    engine_door(cv, _engine_far)


# ─── El tauler d'eines ────────────────────────────────────────────────────

def _sil_rect(cv, x0, y0, x1, y1):
    """Silueta pintada: un contorn clar d'1 px."""
    for x in range(x0, x1 + 1):
        cv.put(x, y0, SIL, 1.6)
        cv.put(x, y1, SIL, 1.4)
    for y in range(y0, y1 + 1):
        cv.put(x0, y, SIL, 1.6)
        cv.put(x1, y, SIL, 1.4)


def _hook(cv, x, y):
    cv.put(x, y, STEELT, 4.6)
    cv.put(x, y + 1, STEELT, 3.6)
    cv.put(x, y + 2, STEELT, 3.2)
    cv.put(x + 1, y + 3, STEELT, 3.0)


def board(cv):
    x0, y0, x1, y1 = BOARD
    box(cv, x0 - 4, y0 - 4, x1 + 4, y1 + 4, WOOD, 3.4)               # marc de fusta
    for bx, by in ((x0 - 2, y0 - 2), (x1 + 1, y0 - 2), (x0 - 2, y1 + 1), (x1 + 1, y1 + 1)):
        cv.put(bx, by, STEELT, 5.0)
    for y in range(y0, y1 + 1):                                      # tauler perforat
        for x in range(x0, x1 + 1):
            v = 3.6 + (hr(x // 9, y // 40, 4) - 0.5) * 0.3
            if (x - x0) % 8 == 4 and (y - y0) % 8 == 4:
                v = 0.6                                              # forats
            elif (x - x0) % 8 == 5 and (y - y0) % 8 == 5:
                v = 4.4                                              # la vora clara del forat
            cv.put(x, y, PEG, v)
    cv.hline(x0, x1, y0, PEG, 5.0)
    cv.hline(x0, x1, y1, PEG, 1.8)
    hpipe(cv, x0 + 3, x1 - 3, RAIL_Y, 1, STEELT, 3.6)                # la barra de ganxos de baix
    for bx in (x0 + 3, x1 - 3):
        box(cv, bx - 2, RAIL_Y - 3, bx + 2, RAIL_Y + 3, STEELT, 3.2)

    # fila de dalt: claus fixes (boca oberta a dalt i estrella a baix), damunt de la seva silueta
    def wrench(x, y, ln, lvl=4.2):
        _sil_rect(cv, x - 3, y - 1, x + 4, y + ln + 1)
        cv.rect(x - 1, y + 5, x + 1, y + ln - 4, STEELT, lvl)
        cv.vline(x - 1, y + 5, y + ln - 4, STEELT, lvl + 1.0)
        cv.disc(x, y + 2, 3.5, 3, STEELT, lvl + 0.6)                 # la boca
        cv.rect(x - 1, y - 1, x + 1, y + 1, PEG, 1.0)
        cv.disc(x, y + ln - 1, 3, 3, STEELT, lvl + 0.4)              # l'estrella
        cv.put(x, y + ln - 1, PEG, 1.0)
        cv.put(x - 1, y + ln - 1, PEG, 1.6)
    for i, ln in enumerate((24, 28, 32, 36, 40)):
        x = 128 + i * 12
        _hook(cv, x, 47)
        wrench(x, 52, ln)

    def screwdriver(x, y, col, ln):
        _sil_rect(cv, x - 3, y - 1, x + 3, y + ln)
        cv.rect(x - 2, y, x + 2, y + 12, col, 3.6)
        cv.vline(x - 2, y, y + 12, col, 4.8)
        cv.vline(x + 2, y, y + 12, col, 2.6)
        for yy in range(y + 2, y + 11, 3):                           # les estries del mànec
            cv.hline(x - 1, x + 1, yy, col, 2.4)
        cv.vline(x, y + 13, y + ln - 2, STEELT, 5.0)
        cv.vline(x + 1, y + 13, y + ln - 2, STEELT, 3.0)
        cv.put(x, y + ln - 1, STEELT, 4.0)
    for i, col in enumerate((REDP, YELL, REDP, SEAG)):
        x = 200 + i * 9
        _hook(cv, x, 47)
        screwdriver(x, 52, col, 27 + i * 3)

    def hammer(x, y):
        _sil_rect(cv, x - 10, y - 1, x + 10, y + 43)
        box(cv, x - 9, y, x + 9, y + 7, STEELT, 3.6)
        cv.hline(x - 9, x + 9, y, STEELT, 5.2)
        cv.poly([(x + 9, y), (x + 9, y + 7), (x + 7, y + 7)], PEG, 3.4)    # l'orella d'arrencar claus
        cv.rect(x - 2, y + 8, x + 2, y + 42, WOOD, 4.4)
        cv.vline(x - 2, y + 8, y + 42, WOOD, 5.4)
        cv.vline(x + 2, y + 8, y + 42, WOOD, 3.2)
        cv.rect(x - 2, y + 33, x + 2, y + 42, RUBBER, 2.4)            # el puny
    hammer(251, 51)
    _hook(cv, 251, 46)

    # la silueta buida: la clau de vàlvules (barra llarga amb el cap de forquilla); la pols marca on era
    sx = 285
    _hook(cv, sx, 46)
    for y in range(51, 149):
        cv.put(sx - 3, y, SIL, 2.4)
        cv.put(sx + 3, y, SIL, 2.4)
    for dx in range(-9, 10):
        cv.put(sx + dx, 51, SIL, 2.4)
    for y in range(51, 67):
        cv.put(sx - 9, y, SIL, 2.4)
        cv.put(sx + 9, y, SIL, 2.4)
    for y in range(59, 67):
        cv.put(sx - 4, y, SIL, 2.4)
        cv.put(sx + 4, y, SIL, 2.4)
    cv.hline(sx - 9, sx - 4, 66, SIL, 2.4)
    cv.hline(sx + 4, sx + 9, 66, SIL, 2.4)
    cv.hline(sx - 3, sx + 3, 148, SIL, 2.4)
    for y in range(52, 148):                                         # el tauler, més net a dins
        for x in range(sx - 2, sx + 3):
            if hr(x, y, 9) > 0.55:
                cv.put(x, y, PEG, 4.4)
    for x in range(sx - 8, sx + 9):
        for y in range(52, 66):
            if (abs(x - sx) > 4 or y < 59) and hr(x, y, 10) > 0.55:
                cv.put(x, y, PEG, 4.4)

    # la serra, a la dreta, damunt de la seva silueta
    _hook(cv, 315, 46)
    _sil_rect(cv, 304, 49, 360, 67)
    cv.poly([(307, 52), (349, 52), (349, 61), (307, 65)], STEELT, lambda x, y: 4.6 - (x - 307) * 0.015)
    cv.hline(307, 349, 52, STEELT, 6.0)
    for x in range(308, 349, 2):                                     # les dents
        cv.put(x, 65 - (x - 307) // 11, STEELT, 2.4)
    cv.put(311, 55, PEG, 0.8)                                        # el forat per penjar-la
    box(cv, 347, 51, 360, 64, WOOD, 4.0)                             # el mànec, amb el forat dels dits
    rrect(cv, 351, 55, 357, 60, 2, PEG, 0.8)
    cv.put(349, 54, BRASS, 5.0)                                      # els reblons del mànec
    cv.put(349, 61, BRASS, 5.0)
    # tres alicates (de punta, universals, de tall)
    for i, x in enumerate((320, 336, 352)):
        _hook(cv, x, 75)
        _sil_rect(cv, x - 5, 77, x + 5, 109)
        cv.poly([(x - 2, 78), (x + 2, 78), (x + 2, 86 - i), (x - 2, 86 - i)], STEELT, 4.6)
        cv.vline(x, 78, 84 - i, PEG, 1.2)                            # la boca
        cv.disc(x, 87, 2, 2, STEELT, 5.2)                            # el reblon
        col = REDP if i != 1 else YELL
        cv.line(x - 1, 89, x - 4, 108, col, 3.8)
        cv.line(x - 2, 89, x - 5, 108, col, 4.8)
        cv.line(x + 1, 89, x + 4, 108, col, 3.0)
        cv.line(x + 2, 89, x + 5, 108, col, 2.2)
    # el nivell, amb les tres bombolles
    _hook(cv, 387, 46)
    _sil_rect(cv, 380, 49, 395, 139)
    box(cv, 381, 51, 393, 137, YELL, 3.6)
    cv.vline(381, 51, 137, YELL, 4.8)
    for yy in (64, 93, 123):
        cv.rect(384, yy, 390, yy + 4, [(30, 70, 40), (80, 170, 90), (170, 240, 160)], 1.6, lit=0)
        cv.put(386, yy + 2, WHITEP, 5.6, lit=0)                      # la bombolla
        cv.vline(383, yy, yy + 4, CAB, 2.6)
        cv.vline(391, yy, yy + 4, CAB, 2.6)
    for yy in range(56, 135, 6):                                     # l'escala
        cv.hline(392, 393, yy, CAB, 2.0)
    # les siluetes de la barra de baix (la cisalla i la clau de tubs hi pengen: són props)
    _sil_rect(cv, 139, 128, 211, 143)
    _sil_rect(cv, 227, 128, 243, 156)
    for x in (149, 197, 235):
        _hook(cv, x, RAIL_Y + 1)
    # l'etiqueta del tauler, a dalt al mig
    box(cv, 200, 41, 230, 47, WHITEP, 4.0)
    s = 'EINES'
    text(cv, s, 215 - text_width(s) // 2, 42, None, 0, flat=(40, 44, 48))


# ─── El banc de treball ───────────────────────────────────────────────────

def bench(cv):
    x0, x1 = 429, 624
    # prestatge a la paret, damunt del banc
    box(cv, 435, 75, 616, 80, WOOD, 3.6)
    cv.hline(435, 616, 75, WOOD, 5.0)
    for bx in (445, 605):
        cv.poly([(bx, 81), (bx + 4, 81), (bx + 4, 96), (bx, 85)], CAB, 2.8)
    jars = [(440, 59, 453, (120, 120, 110)), (459, 61, 472, None), (477, 53, 496, 'box'), (501, 61, 515, None),
            (520, 56, 531, (200, 60, 40)), (536, 51, 565, 'box2'), (571, 61, 584, None), (589, 59, 608, 'box')]
    labels = {477: 'M6', 589: 'M8'}
    for (a, top, b, kind) in jars:
        if kind == 'box':
            box(cv, a, top, b, 73, [(40, 30, 14), (80, 60, 26), (130, 100, 48), (170, 136, 70), (200, 170, 100)], 2.6)
            cv.hline(a, b, top, [(80, 60, 26), (170, 136, 70), (220, 196, 140)], 2.0)
            cv.rect(a + 3, top + 4, b - 3, top + 11, WHITEP, 3.4)
            s = labels.get(a, '')
            text(cv, s, (a + b) // 2 - text_width(s) // 2, top + 5, None, 0, flat=(40, 40, 44))
        elif kind == 'box2':
            box(cv, a, top, b, 73, REDP, 3.0)
            cv.rect(a + 4, top + 5, b - 4, top + 11, YELL, 3.6)
            cv.hline(a + 6, b - 6, top + 8, REDP, 2.4)
            cv.rect(a + 4, top + 14, b - 4, top + 16, WHITEP, 3.6)
        else:
            for y in range(top, 74):
                for x in range(a, b + 1):
                    u = (x - (a + b) / 2) / ((b - a) / 2 + 0.5)
                    if kind is None:
                        cv.put(x, y, STEELT, 3.4 - u * 1.2 - u * u)
                    else:
                        cv.put(x, y, [mix(kind, (0, 0, 0), 0.7), mix(kind, (0, 0, 0), 0.4), kind,
                                      mix(kind, (255, 255, 255), 0.3)], 2.4 - u - u * u)
            cv.vline(a + 2, top + 2, 72, WHITEP, 4.6 if kind is not None else 5.4)
            cv.rect(a, top - 3, b, top, CAB, 3.4)
            cv.hline(a, b, top - 3, CAB, 4.6)
            if kind is None:
                cv.rect(a + 2, top + 5, b - 2, top + 8, YELL, 3.4)   # la llauna d'oli, amb l'etiqueta
    # el sobre del banc (fusta gruixuda, amb taques i marques)
    cv.rect(x0, BENCH_TOP, x1, BENCH_TOP + 8, WOOD, lambda x, y: 4.2 - (y - BENCH_TOP) * 0.2)
    cv.hline(x0, x1, BENCH_TOP, WOOD, 5.6)
    cv.hline(x0, x1, BENCH_TOP + 9, WOOD, 1.2)
    for x in range(x0, x1, 31):
        cv.vline(x, BENCH_TOP + 1, BENCH_TOP + 8, WOOD, 2.4)
    for i in range(6):
        cx = x0 + 60 + int(hr(i, 31) * 120)
        cv.put(cx, BENCH_TOP + 3 + int(hr(i, 32) * 4), WOOD, 2.8)
        cv.put(cx + 1, BENCH_TOP + 3 + int(hr(i, 32) * 4), WOOD, 3.0)
    # calaixera i potes
    box(cv, x0 + 3, BENCH_TOP + 11, x0 + 59, FLOOR_Y + 5, ENG, 3.0)
    for i in range(3):
        y = BENCH_TOP + 13 + i * 15
        box(cv, x0 + 7, y, x0 + 55, y + 12, ENG, 3.4)
        box(cv, x0 + 24, y + 4, x0 + 38, y + 6, CAB, 4.4)
        cv.rect(x0 + 10, y + 3, x0 + 18, y + 6, WHITEP, 3.6)         # l'etiqueta del calaix
    box(cv, x1 - 8, BENCH_TOP + 11, x1 - 3, FLOOR_Y + 5, ENG, 2.6)
    cv.hline(x0 + 61, x1 - 8, FLOOR_Y - 11, ENG, 2.4)                # travesser de baix
    cv.hline(x0 + 61, x1 - 8, FLOOR_Y - 10, ENG, 1.2)
    cv.darken(x0 + 61, BENCH_TOP + 11, x1 - 9, FLOOR_Y + 4, 0.5)
    # caixa d'eines vermella, a sota
    box(cv, 507, 179, 552, FLOOR_Y + 4, REDP, 3.0)
    cv.hline(507, 552, 187, REDP, 1.6)
    cv.hline(507, 552, 188, REDP, 4.0)
    box(cv, 523, 173, 536, 177, CAB, 3.8)
    for cx in (510, 549):
        box(cv, cx - 1, 185, cx + 1, 190, CAB, 4.0)                  # els tancs
    # el cargol de banc (esquerra)
    box(cv, 440, 133, 469, 148, STEELT, 3.4)
    box(cv, 445, 125, 464, 133, STEELT, 4.0)
    cv.rect(453, 125, 456, 133, DARK, 0.8)
    for yy in range(126, 133, 2):                                    # l'estriat de les mordasses
        cv.hline(450, 452, yy, STEELT, 2.6)
        cv.hline(457, 459, yy, STEELT, 2.6)
    hpipe(cv, 432, 469, 141, 1, STEELT, 4.4)
    cv.disc(432, 141, 3, 3, STEELT, 4.0)
    cv.disc(469, 141, 2, 2, STEELT, 3.4)
    # un torn petit (dreta)
    box(cv, 557, 128, 579, 148, SEAG, 3.4)                           # capçal
    cv.rect(560, 132, 568, 136, WHITEP, 3.6)                         # la placa de velocitats
    cv.disc(584, 137, 7, 7, STEELT, lambda nx, ny: 4.0 - nx - ny)    # plat
    for a in (0, 120, 240):
        cv.put(584 + round(math.cos(math.radians(a)) * 5), 137 + round(math.sin(math.radians(a)) * 5), STEELT, 1.4)
    hpipe(cv, 584, 608, 137, 1, STEELT, 4.4)                         # bancada
    box(cv, 603, 131, 616, 148, SEAG, 3.2)                           # contrapunt
    box(cv, 555, 144, 619, 148, STEELT, 2.8)
    cv.line(612, 131, 618, 125, STEELT, 3.6)                          # la maneta del contrapunt
    cv.disc(618, 125, 1.5, 1.5, DARK, 1.6)
    # l'entrepà vell, en un plat
    cv.disc(515, 147, 17, 3, WHITEP, lambda nx, ny: 4.2 - ny)
    cv.rect(501, 139, 528, 144, BREAD, lambda x, y: 3.6 - (y - 139) * 0.4)
    cv.hline(502, 527, 137, BREAD, 4.2)
    cv.hline(501, 528, 138, BREAD, 3.8)
    for x in range(503, 527, 4):
        cv.put(x, 138, BREAD, 4.8)
    cv.hline(502, 527, 141, GREENT, 3.0)                             # un enciam que ja no és verd
    for x in range(503, 527, 3):
        if hr(x, 41) > 0.3:
            cv.put(x, 142, GREENT, 2.2)
    for x in range(504, 527, 5):
        cv.put(x, 143, [(60, 20, 20), (130, 50, 40), (180, 90, 70)], 1.6)
    cv.put(529, 140, BREAD, 1.6)                                     # unes engrunes
    cv.put(531, 146, BREAD, 2.6)
    # un pot de cafè amb llapis
    vpipe(cv, 483, 136, 148, 4, WHITEP, 3.2)
    cv.hline(480, 486, 140, REDP, 3.4)
    for i, c in enumerate((YELL, REDP, SEAG)):
        cv.line(481 + i * 2, 135, 478 + i * 3, 124, c, 3.6)
        cv.flat(478 + i * 3, 123, (40, 36, 30))


def extras(cv):
    # extintor a la paret, entre el tauler i el banc
    vpipe(cv, 421, 155, 195, 5, REDP, 3.4)
    cv.disc(421, 155, 5, 4, REDP, 3.8)
    box(cv, 417, 144, 425, 151, CAB, 3.6)
    cv.line(425, 147, 430, 165, DARK, 1.6)
    cv.line(430, 165, 428, 172, DARK, 1.6)
    box(cv, 415, 171, 428, 179, WHITEP, 3.6)
    s = 'CO2'
    text(cv, s, 421 - text_width(s) // 2 + 1, 173, None, 0, flat=(40, 40, 44))
    box(cv, 413, 182, 430, 184, CAB, 2.6)                             # la brida a la paret
    # un rotllo de cable penjat a l'esquerra del tauler
    for r in (11, 10, 9):
        cv.ring(93, 99, r, CAB, 3.4 - (11 - r) * 0.4, step=3)
    cv.ring(93, 99, 8, YELL, 3.0, step=4)
    box(cv, 91, 85, 96, 88, CAB, 4.2)
    cv.line(100, 107, 104, 122, CAB, 3.0)                             # la punta que penja
    cv.put(104, 123, BRASS, 4.4)
    # bidó d'oli a terra, a la dreta del tauler
    for y in range(165, FLOOR_Y + 5):
        for x in range(371, 406):
            u = (x - 388) / 18
            cv.put(x, y, SEAG, 3.4 - u * 1.4 - u * u + (0.6 if y in (176, 192) else 0))
    cv.disc(388, 165, 18, 3, SEAG, 4.2)
    cv.ring(388, 165, 15, SEAG, 2.6, step=6)
    cv.disc(395, 165, 3, 1, DARK, 1.0)
    box(cv, 379, 179, 397, 188, YELL, 3.4)
    s = 'OLI'
    text(cv, s, 388 - text_width(s) // 2, 181, None, 0, flat=(40, 30, 10))
    for x in range(373, 404):                                        # degotalls d'oli
        if hr(x, 61) > 0.85:
            cv.vline(x, 168, 168 + int(hr(x, 62) * 8), DARK, 1.6)


# ─── Muntatge ─────────────────────────────────────────────────────────────

def bg(cv):
    room(cv)
    door(cv)
    board(cv)
    bench(cv)
    extras(cv)
    checker_floor(cv)
    floor_shadow(cv, 527, FLOOR_Y + 4, 107, 8, 0.5)
    floor_shadow(cv, 388, FLOOR_Y + 4, 21, 4, 0.6)
    lights(cv)


# ─── Props: la cisalla i la clau de tubs, penjades a la barra ─────────────

def cisalla(cv):
    """La cisalla de mànecs vermells, ajaguda en dos ganxos: les mordasses a l'esquerra, els mànecs a la dreta."""
    # mordasses (amb el tall esmolat) i articulació
    cv.poly([(141, 135), (152, 131), (160, 133), (160, 139), (152, 140)], STEELT, lambda x, y: 5.0 - (y - 131) * 0.25)
    cv.hline(142, 152, 135, DARK, 1.0)
    cv.line(144, 134, 152, 132, STEELT, 6.6)                         # el tall, lluent
    box(cv, 157, 131, 165, 140, STEELT, 3.8)
    bolt(cv, 160, 133, STEELT, 4.4)
    bolt(cv, 161, 137, STEELT, 4.4)
    cv.disc(163, 135, 1.5, 1.5, STEELT, 5.4)                         # el pivot
    # els dos braços d'acer i els mànecs vermells
    for d in (0, 1):
        cv.line(165, 132 + d, 179, 131 + d, STEELT, 4.6 - d * 1.2)
        cv.line(165, 139 - d, 179, 140 - d, STEELT, 3.4 - d * 0.8)
    for (ya, yb) in ((131, 129), (140, 142)):
        for d in (0, 1, 2):
            cv.line(179, ya + d - (1 if ya < 135 else 0), 208, yb + d - (1 if ya < 135 else 0), REDP, 4.4 - d * 1.2)
    for gy in (129, 142):                                            # punys de goma
        cv.rect(200, gy - 1, 209, gy + 2, RUBBER, 2.4)
        cv.hline(200, 209, gy - 1, RUBBER, 3.4)


def clau_tubs(cv):
    """La clau de tubs (Stillson): mànec de ferro vermell penjat per la punta i el cap de rosca a baix."""
    x = 235
    cv.disc(x, 132, 2.5, 2, STEELT, 1.6)                             # el forat del mànec
    for y in range(130, 148):
        cv.put(x - 3, y, REDP, 4.4)
        cv.put(x - 2, y, REDP, 4.0)
        cv.put(x - 1, y, REDP, 3.6)
        cv.put(x, y, REDP, 3.0)
        cv.put(x + 1, y, REDP, 2.2)
    cv.put(x - 1, 140, YELL, 3.6)                                    # la mida, pintada
    cv.put(x - 1, 142, YELL, 3.6)
    box(cv, x - 4, 147, x + 4, 155, STEELT, 3.6)                     # mordassa fixa
    cv.rect(x + 4, 148, x + 7, 154, STEELT, 4.4)                     # rosca
    for y in range(148, 155, 2):
        cv.hline(x + 4, x + 7, y, STEELT, 2.4)
    cv.rect(x - 7, 144, x - 4, 155, STEELT, 4.2)                     # mordassa mòbil (el ganxo)
    cv.hline(x - 7, x - 4, 144, STEELT, 5.4)
    for y in range(146, 155, 2):                                     # les dents
        cv.put(x - 4, y, STEELT, 2.0)


PROPS = {'cisalla': cisalla, 'clau_tubs': clau_tubs}


# ─── Animacions ─────────────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv.img


def _frames_fluorescent():
    """El fluorescent té la reactància cansada: de tant en tant fa pampallugues, com quan s'encén.
    Només els fotogrames on s'apaga porten res; la resta són buits (no cal comparar la sala sencera)."""
    tx, ty = TUBE[0], 29
    dims = {44: 0.8, 45: 0.15, 46: 0.85, 47: 0.85, 48: 0.4, 50: 0.25}   # fotograma → quant s'apaga
    frames = []
    done = {}
    for i in range(56):
        k = dims.get(i, 0)
        if not k:
            frames.append(Image.new('RGBA', _base().size, (0, 0, 0, 0)))
            continue
        if k not in done:
            base = _base()
            cv = Canvas(light=LIGHT, img=base.copy())
            cv.darken(0, 0, W - 1, FLOOR_Y + 59,
                      lambda x, y: k * max(0.0, 1 - math.hypot(x - tx, (y - ty) * 1.2) / 400), dither=False)
            if k > 0.5:                                               # el tub, gairebé apagat (els extrems roents)
                cv.rect(tx - 49, 28, tx + 49, 31, [(70, 76, 74), (96, 104, 100), (120, 128, 124)], 1.4, lit=0)
                for ex in (tx - 49, tx - 48, tx - 47, tx + 47, tx + 48, tx + 49):
                    cv.vline(ex, 28, 31, [(150, 120, 110), (200, 160, 140)], 1.4, lit=0)
            done[k] = _diff(cv.img, base)
        frames.append(done[k])
    return frames


def _frames_mosca():
    """Una mosca que no deixa en pau l'entrepà vell: s'aixeca, fa voltes i hi torna a parar."""
    src = _base().load()
    S = _base().width // W                                           # un píxel de sala = un bloc S×S
    lx, ly = 512, 136                                                # on es para (damunt del pa)
    fly_n, rest_n = 34, 22
    frames = []

    def put(p, x, y, col):
        if 0 <= x < W and 0 <= y < H:
            for dy in range(S):
                for dx in range(S):
                    p[x * S + dx, y * S + dy] = tuple(col[:3]) + (255,)
    for i in range(fly_n + rest_n):
        img = Image.new('RGBA', _base().size, (0, 0, 0, 0))
        p = img.load()
        if i < fly_n:
            s = i / fly_n
            x = round(lx + 21 * math.sin(2 * math.pi * s) + 9 * math.sin(6 * math.pi * s))
            y = round(ly - 19 * math.sin(math.pi * s) - 7 * math.sin(4 * math.pi * s))
            put(p, x, y, (16, 14, 18))
            put(p, x + 1, y, (30, 26, 30))
            wy = y - 1 if i % 2 else y + 1                           # les ales, que vibren
            put(p, x, wy, mix(src[x * S, wy * S][:3], (200, 210, 220), 0.55))
            put(p, x + 1, wy, mix(src[(x + 1) * S, wy * S][:3], (200, 210, 220), 0.4))
            if i % 2:
                put(p, x - 1, wy, mix(src[(x - 1) * S, wy * S][:3], (200, 210, 220), 0.3))
        else:
            j = i - fly_n
            dx = 1 if (j // 6) % 2 else 0                            # camina una mica per l'entrepà
            put(p, lx + dx, ly, (16, 14, 18))
            put(p, lx + dx + 1, ly, (30, 26, 30))
            put(p, lx + dx, ly - 1, mix(src[(lx + dx) * S, (ly - 1) * S][:3], (170, 180, 190), 0.35))   # les ales, plegades
            if j % 7 in (2, 3):                                      # es frega les potes
                put(p, lx + dx - 1, ly, (40, 34, 30))
        frames.append(img)
    return frames


ANIMS = {'fluorescent': {'frames': _frames_fluorescent, 'frameDuration': 100},
         'mosca': {'frames': _frames_mosca, 'frameDuration': 70}}


# ─── Geometria (coordenades de 640×360) ─────────────────────────────────────

GEOMETRIA = {
    'things': {
        'porta': {'rect': (3, 61, 80, 203), 'walk': (45, 232)},
        'tauler': {'rect': (108, 36, 417, 123), 'walk': (264, 232)},
        'cisalla': {'rect': (137, 125, 212, 145), 'walk': (173, 235)},
        'clau_tubs': {'rect': (224, 125, 245, 159), 'walk': (235, 235)},
        'banc': {'rect': (429, 123, 627, 205), 'walk': (528, 235)},
    },
    'spawns': {'iri': (293, 251), 'vet': (387, 253)},
    'walkable': [(8, 227), (632, 227), (637, 261), (3, 261)],
}
