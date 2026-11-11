"""
El taller de l'Arenga (coberta de sota, porta amb porta amb la sala de màquines). Art definitiu:
  - un taller petit, endreçat com un quiròfan: paret verda de planxa, llum de fluorescent;
  - a l'esquerra, la porta estanca oberta cap a la sala de màquines;
  - el tauler d'eines, amb la silueta pintada de cada eina; una silueta és buida (la clau de vàlvules);
    a la barra de sota, la cisalla de mànecs vermells i la clau de tubs (props);
  - el banc de treball, amb el cargol de banc, un torn petit, calaixos i un entrepà vell en un plat;
  - un prestatge amb pots i capses, un extintor i una caixa d'eines a terra.
"""
import math

from hd.pix import Canvas, Light, W, H, hr, mix, RUST
from hd.rooms.arenga import (WALL, ENG_LIGHT as ENG, DECK, CAB, REDP, YELL, SEAG, DARK, WHITEP, BRASS, FLOOR_Y,
                             box, rrect, bolt, hpipe, vpipe, glow)
from hd.rooms.sota import (plate_wall, ceiling, checker_floor, door_frame, in_door, hinge_leaf, sill, sign,
                           floor_shadow)
from hd.rooms.comu import _diff

TUBE = (240, 16)                       # el fluorescent
COOL = (220, 236, 230)
PEG = [(20, 16, 10), (40, 32, 20), (62, 50, 32), (88, 72, 46), (116, 96, 62), (146, 124, 82), (178, 154, 106)]
WOOD = [(24, 14, 8), (44, 26, 14), (68, 42, 22), (96, 62, 32), (126, 84, 44), (156, 110, 60), (186, 140, 82),
        (212, 172, 112)]
SIL = [(150, 140, 110), (196, 186, 150), (232, 224, 196)]     # pintura de les siluetes
STEELT = [(14, 16, 20), (28, 32, 38), (46, 52, 60), (68, 76, 86), (96, 104, 114), (130, 138, 146), (170, 176, 182),
          (214, 218, 222)]
BREAD = [(60, 34, 14), (104, 62, 26), (150, 96, 44), (190, 134, 70), (220, 172, 108)]
GREENT = [(14, 26, 14), (26, 50, 24), (44, 80, 36), (70, 112, 50), (100, 146, 70)]

LIGHT = Light(ambient=-0.3, vignette=(60, 26), floor_fade=(186, 40))
LIGHT.point(TUBE[0], TUBE[1] + 6, r=230, k=2.7, squash=1.25, down=True, power=1.4)
LIGHT.point(34, 110, r=40, k=0.4, power=2.0)                      # la sala de màquines, per la porta

BOARD = (84, 30, 310, 120)            # el tauler d'eines (x0, y0, x1, y1)
RAIL_Y = 94                           # la barra de ganxos de baix, on pengen la cisalla i la clau de tubs
BENCH_TOP = 112


# ─── Paret, sostre, terra ─────────────────────────────────────────────────

def room(cv):
    plate_wall(cv, 0, W - 1, seed=3)
    ceiling(cv)
    # tub de serveis i safata de cables al llarg de la paret
    hpipe(cv, 60, W - 1, 24, 2, SEAG, 3.0, bands=range(90, W, 60), band_ramp=WHITEP)
    for x in range(70, W, 60):
        cv.vline(x, 20, 28, CAB, 3.0)
    # el fluorescent
    box(cv, TUBE[0] - 40, 15, TUBE[0] + 40, 21, CAB, 3.0)
    cv.rect(TUBE[0] - 37, 21, TUBE[0] + 37, 23, [(140, 150, 146), (200, 214, 208), (236, 246, 242), (255, 255, 255)], 2.6, lit=0)


def lights(cv):
    glow(cv, TUBE[0], 24, 70, COOL, 0.22)
    glow(cv, TUBE[0], 22, 20, (255, 255, 255), 0.4)


# ─── La porta (cap a la sala de màquines) ─────────────────────────────────

def door(cv):
    x0, y0, x1, y1 = 14, 66, 54, FLOOR_Y
    # l'altra banda: la sala de màquines, verda i fosca, amb un tub i el resplendor d'un llum
    for y in range(y0, y1):
        for x in range(x0, x1 + 1):
            if in_door(x, y, x0, y0, x1, y1):
                cv.put(x, y, WALL, 2.0 - abs(x - 34) / 40 + (-1.0 if y > 136 else 0) - (y - y0) / 160, lit=0.3)
    for y in range(80, 84):
        for x in range(x0, x1 + 1):
            cv.put(x, y, SEAG, 2.4 - (y - 80) * 0.4, lit=0.2)
    for y in range(y0 + 30, y1 - 16):
        for x in range(36, 50):
            u = (x - 43) / 7
            cv.put(x, y, ENG, 2.6 - u * 0.8 - u * u, lit=0.2)
    cv.rect(x0, y1 - 14, x1, y1 - 1, DECK, 1.6, lit=0.2)
    door_frame(cv, x0, y0, x1, y1)
    sill(cv, x0, x1, y1)
    hinge_leaf(cv, 4, y0, 12, y1)
    for dx, dy in ((x1 + 2, 84), (x1 + 2, 124)):
        box(cv, dx, dy, dx + 2, dy + 6, CAB, 3.4)
    sign(cv, 12, 52, 'MÀQUINES')


# ─── El tauler d'eines ────────────────────────────────────────────────────

def _sil_rect(cv, x0, y0, x1, y1):
    """Silueta pintada: un contorn clar d'1 px."""
    for x in range(x0, x1 + 1):
        cv.put(x, y0, SIL, 1.6)
        cv.put(x, y1, SIL, 1.4)
    for y in range(y0, y1 + 1):
        cv.put(x0, y, SIL, 1.6)
        cv.put(x1, y, SIL, 1.4)


def _sil_line(cv, pts, w=1):
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        n = max(abs(bx - ax), abs(by - ay), 1)
        for i in range(n + 1):
            x, y = ax + (bx - ax) * i / n, ay + (by - ay) * i / n
            for d in range(-w, w + 1):
                cv.put(round(x + d * 0.0), round(y) , SIL, 1.5)


def _hook(cv, x, y):
    cv.put(x, y, STEELT, 4.6)
    cv.put(x, y + 1, STEELT, 3.6)
    cv.put(x + 1, y + 2, STEELT, 3.0)


def board(cv):
    x0, y0, x1, y1 = BOARD
    # marc de fusta i tauler perforat
    box(cv, x0 - 3, y0 - 3, x1 + 3, y1 + 3, WOOD, 3.4)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            v = 3.6 + (hr(x // 7, y // 30, 4) - 0.5) * 0.3
            if (x - x0) % 6 == 3 and (y - y0) % 6 == 3:
                v = 0.6                                           # forats
            cv.put(x, y, PEG, v)
    cv.hline(x0, x1, y0, PEG, 5.0)
    cv.hline(x0, x1, y1, PEG, 1.8)
    # la barra de ganxos de baix
    hpipe(cv, x0 + 2, x1 - 2, RAIL_Y, 1, STEELT, 3.6)

    # fila de dalt: martells, tornavisos, claus fixes (eina damunt la seva silueta, desplaçada 1 px)
    def wrench(x, y, ln, lvl=4.2):
        _sil_rect(cv, x - 2, y - 1, x + 3, y + ln + 1)
        cv.rect(x - 1, y + 4, x + 1, y + ln - 3, STEELT, lvl)
        cv.disc(x, y + 2, 3, 2.5, STEELT, lvl + 0.6)
        cv.put(x, y + 1, PEG, 1.0)
        cv.disc(x, y + ln - 1, 2.5, 2.5, STEELT, lvl + 0.4)
        cv.put(x, y + ln - 1, PEG, 1.0)
    for i, ln in enumerate((18, 21, 24, 27, 30)):
        x = 96 + i * 9
        _hook(cv, x, 36)
        wrench(x, 39, ln)

    def screwdriver(x, y, col, ln=24):
        _sil_rect(cv, x - 2, y - 1, x + 2, y + ln)
        cv.rect(x - 1, y, x + 1, y + 9, col, 3.6)
        cv.vline(x - 1, y, y + 9, col, 4.8)
        cv.vline(x, y + 10, y + ln - 1, STEELT, 5.0)
    for i, col in enumerate((REDP, YELL, REDP, SEAG)):
        x = 150 + i * 7
        _hook(cv, x, 36)
        screwdriver(x, 39, col, 20 + i * 2)

    def hammer(x, y):
        _sil_rect(cv, x - 7, y - 1, x + 7, y + 32)
        box(cv, x - 6, y, x + 6, y + 5, STEELT, 3.6)
        cv.rect(x - 1, y + 6, x + 1, y + 31, WOOD, 4.4)
        cv.vline(x - 1, y + 6, y + 31, WOOD, 5.4)
    hammer(188, 38)
    _hook(cv, 188, 35)

    # la silueta buida: la clau de vàlvules (barra llarga amb el cap de forquilla)
    sx = 214
    _hook(cv, sx, 35)
    for y in range(38, 112):
        cv.put(sx - 2, y, SIL, 2.4)
        cv.put(sx + 2, y, SIL, 2.4)
    for dx in range(-7, 8):                                         # el cap: una U oberta cap avall
        cv.put(sx + dx, 38, SIL, 2.4)
    for y in range(38, 50):
        cv.put(sx - 7, y, SIL, 2.4)
        cv.put(sx + 7, y, SIL, 2.4)
    for y in range(44, 50):
        cv.put(sx - 3, y, SIL, 2.4)
        cv.put(sx + 3, y, SIL, 2.4)
    cv.hline(sx - 7, sx - 3, 49, SIL, 2.4)
    cv.hline(sx + 3, sx + 7, 49, SIL, 2.4)
    cv.hline(sx - 2, sx + 2, 111, SIL, 2.4)
    # la pols marca on hi havia l'eina: el tauler una mica més net a dins
    for y in range(39, 111):
        for x in range(sx - 1, sx + 2):
            if hr(x, y, 9) > 0.6:
                cv.put(x, y, PEG, 4.4)

    # serres, alicates i un nivell, a la dreta
    _hook(cv, 236, 35)
    _sil_rect(cv, 228, 37, 270, 50)
    cv.poly([(230, 39), (262, 39), (262, 46), (230, 49)], STEELT, lambda x, y: 4.6 - (x - 230) * 0.02)
    for x in range(231, 262, 2):
        cv.put(x, 49 - (x - 230) // 11, STEELT, 2.6)
    box(cv, 260, 38, 270, 48, WOOD, 4.0)
    cv.rect(263, 41, 267, 45, PEG, 0.8)
    for i, x in enumerate((240, 252, 264)):                         # alicates
        _hook(cv, x, 56)
        _sil_rect(cv, x - 4, 58, x + 4, 82)
        cv.rect(x - 1, 59, x + 1, 64, STEELT, 4.6)
        cv.line(x - 1, 65, x - 3, 81, REDP if i != 1 else YELL, 3.8)
        cv.line(x + 1, 65, x + 3, 81, REDP if i != 1 else YELL, 3.0)
    _hook(cv, 290, 35)                                               # nivell
    _sil_rect(cv, 285, 37, 296, 104)
    box(cv, 286, 38, 295, 103, YELL, 3.6)
    for yy in (48, 70, 92):
        cv.rect(288, yy, 293, yy + 3, [(30, 70, 40), (80, 170, 90), (170, 240, 160)], 1.6, lit=0)

    # siluetes de la barra de baix (la cisalla i la clau de tubs hi pengen: són props)
    _sil_rect(cv, 104, 96, 158, 107)
    _sil_rect(cv, 170, 96, 182, 117)
    for x in (112, 148, 176):
        _hook(cv, x, RAIL_Y + 1)


# ─── El banc de treball ───────────────────────────────────────────────────

def bench(cv):
    x0, x1 = 322, 468
    # prestatge a la paret, damunt del banc
    box(cv, 326, 56, 462, 60, WOOD, 3.6)
    for bx in (334, 454):
        cv.poly([(bx, 61), (bx + 3, 61), (bx + 3, 72), (bx, 64)], CAB, 2.8)
    # pots i capses al prestatge
    jars = [(330, 44, 340, (120, 120, 110)), (344, 46, 354, None), (358, 40, 372, 'box'), (376, 46, 386, None),
            (390, 42, 398, (200, 60, 40)), (402, 38, 424, 'box2'), (428, 46, 438, None), (442, 44, 456, 'box')]
    for (a, top, b, kind) in jars:
        if kind == 'box':
            box(cv, a, top, b, 55, [(40, 30, 14), (80, 60, 26), (130, 100, 48), (170, 136, 70), (200, 170, 100)], 2.6)
            cv.rect(a + 2, top + 3, b - 2, top + 6, WHITEP, 3.2)
        elif kind == 'box2':
            box(cv, a, top, b, 55, REDP, 3.0)
            cv.rect(a + 3, top + 4, b - 3, top + 8, YELL, 3.6)
        else:
            for y in range(top, 56):
                for x in range(a, b + 1):
                    u = (x - (a + b) / 2) / ((b - a) / 2 + 0.5)
                    cv.put(x, y, STEELT if kind is None else [mix(kind, (0, 0, 0), 0.7), mix(kind, (0, 0, 0), 0.4),
                                                                kind, mix(kind, (255, 255, 255), 0.3)],
                           3.4 - u * 1.2 - u * u if kind is None else 2.4 - u - u * u)
            cv.rect(a, top - 2, b, top, CAB, 3.4)
    # el sobre del banc (fusta gruixuda)
    cv.rect(x0, BENCH_TOP, x1, BENCH_TOP + 6, WOOD, lambda x, y: 4.2 - (y - BENCH_TOP) * 0.25)
    cv.hline(x0, x1, BENCH_TOP, WOOD, 5.6)
    cv.hline(x0, x1, BENCH_TOP + 7, WOOD, 1.2)
    for x in range(x0, x1, 23):
        cv.vline(x, BENCH_TOP + 1, BENCH_TOP + 6, WOOD, 2.4)
    # calaixera i potes
    box(cv, x0 + 2, BENCH_TOP + 8, x0 + 44, FLOOR_Y + 4, ENG, 3.0)
    for i in range(3):
        y = BENCH_TOP + 10 + i * 11
        box(cv, x0 + 5, y, x0 + 41, y + 9, ENG, 3.4)
        box(cv, x0 + 18, y + 3, x0 + 28, y + 5, CAB, 4.4)
    for lx in (x1 - 6,):
        box(cv, lx, BENCH_TOP + 8, lx + 4, FLOOR_Y + 4, ENG, 2.6)
    cv.hline(x0 + 46, x1 - 6, FLOOR_Y - 8, ENG, 2.4)                # travesser de baix
    cv.darken(x0 + 46, BENCH_TOP + 8, x1 - 7, FLOOR_Y + 3, 0.5)
    # caixa d'eines vermella, a sota
    box(cv, 380, 134, 414, FLOOR_Y + 3, REDP, 3.0)
    cv.hline(380, 414, 140, REDP, 1.6)
    box(cv, 392, 130, 402, 133, CAB, 3.8)
    # el cargol de banc (esquerra)
    box(cv, 330, 100, 352, 111, STEELT, 3.4)
    box(cv, 334, 94, 348, 100, STEELT, 4.0)
    cv.rect(340, 94, 342, 100, DARK, 0.8)
    hpipe(cv, 324, 352, 106, 1, STEELT, 4.4)
    cv.disc(324, 106, 2, 2, STEELT, 4.0)
    # un torn petit (dreta)
    box(cv, 418, 96, 434, 111, SEAG, 3.4)                            # capçal
    cv.disc(438, 103, 5, 5, STEELT, lambda nx, ny: 4.0 - nx - ny)    # plat
    hpipe(cv, 438, 456, 103, 1, STEELT, 4.4)                         # bancada
    box(cv, 452, 98, 462, 111, SEAG, 3.2)                            # contrapunt
    box(cv, 416, 108, 464, 111, STEELT, 2.8)
    # l'entrepà vell, en un plat
    cv.disc(386, 110, 13, 2.5, WHITEP, lambda nx, ny: 4.2 - ny)
    cv.rect(376, 104, 396, 108, BREAD, lambda x, y: 3.6 - (y - 104) * 0.4)
    cv.hline(377, 395, 103, BREAD, 4.2)
    for x in range(377, 396, 3):
        cv.put(x, 104, BREAD, 4.6)
    cv.hline(377, 395, 106, GREENT, 3.0)                             # un enciam que ja no és verd
    for x in range(378, 396, 4):
        cv.put(x, 107, [(60, 20, 20), (130, 50, 40), (180, 90, 70)], 1.6)
    cv.put(397, 105, BREAD, 1.6)
    # un pot de cafè amb llapis i una llanterna petita
    vpipe(cv, 362, 102, 111, 3, WHITEP, 3.2)
    for i, c in enumerate((YELL, REDP, SEAG)):
        cv.line(361 + i, 101, 359 + i * 2, 94, c, 3.6)


def extras(cv):
    # extintor a la paret, entre el tauler i el banc
    vpipe(cv, 316, 116, 146, 4, REDP, 3.4)
    cv.disc(316, 116, 4, 3, REDP, 3.8)
    box(cv, 313, 108, 319, 113, CAB, 3.6)
    cv.line(319, 110, 323, 124, DARK, 1.6)
    box(cv, 311, 128, 321, 134, WHITEP, 3.6)
    # un rotllo de cable penjat a l'esquerra del tauler
    for r in (8, 7):
        cv.ring(70, 74, r, CAB, 3.4, step=4)
    cv.ring(70, 74, 6, YELL, 3.0, step=5)
    box(cv, 68, 64, 72, 66, CAB, 4.2)
    # bidó d'oli a terra, a la dreta del tauler
    for y in range(124, FLOOR_Y + 4):
        for x in range(278, 304):
            u = (x - 291) / 13.5
            cv.put(x, y, SEAG, 3.4 - u * 1.4 - u * u + (0.6 if y in (132, 144) else 0))
    cv.disc(291, 124, 13, 2.5, SEAG, 4.2)
    cv.disc(296, 124, 2, 1, DARK, 1.0)
    box(cv, 284, 134, 298, 141, YELL, 3.4)


# ─── Muntatge ─────────────────────────────────────────────────────────────

def bg(cv):
    room(cv)
    door(cv)
    board(cv)
    bench(cv)
    extras(cv)
    checker_floor(cv)
    floor_shadow(cv, 395, FLOOR_Y + 3, 80, 6, 0.5)
    floor_shadow(cv, 291, FLOOR_Y + 3, 16, 3, 0.6)
    lights(cv)


# ─── Props: la cisalla i la clau de tubs, penjades a la barra ─────────────

def cisalla(cv):
    """La cisalla de mànecs vermells, ajaguda en dos ganxos: les mordasses a l'esquerra, els mànecs a la dreta."""
    # mordasses i articulació
    cv.poly([(106, 101), (114, 98), (120, 100), (120, 104), (114, 105)], STEELT, lambda x, y: 5.0 - (y - 98) * 0.3)
    cv.hline(106, 114, 101, DARK, 1.0)
    box(cv, 118, 98, 124, 105, STEELT, 3.8)
    bolt(cv, 120, 100, STEELT, 4.4)
    bolt(cv, 121, 103, STEELT, 4.4)
    # els dos braços d'acer i els mànecs vermells (s'obren una mica cap a la dreta)
    cv.line(124, 99, 134, 98, STEELT, 4.6)
    cv.line(124, 104, 134, 105, STEELT, 3.4)
    for (ya, yb) in ((98, 97), (105, 106)):
        for d in (0, 1):
            cv.line(134, ya + d, 156, yb + d + (0 if ya < 100 else 0), REDP, 4.2 - d * 1.4)
    for (gy) in (97, 106):
        cv.rect(150, gy - (1 if gy < 100 else 0), 157, gy + (1 if gy < 100 else 1), DARK, 2.6)   # punys de goma


def clau_tubs(cv):
    """La clau de tubs (Stillson): mànec de ferro vermell penjat per la punta i el cap de rosca a baix."""
    x = 176
    cv.disc(x, 99, 2, 1.5, STEELT, 1.6)                             # el forat del mànec
    for y in range(98, 111):
        cv.put(x - 2, y, REDP, 4.0)
        cv.put(x - 1, y, REDP, 3.6)
        cv.put(x, y, REDP, 3.0)
        cv.put(x + 1, y, REDP, 2.2)
    box(cv, x - 3, 110, x + 3, 116, STEELT, 3.6)                     # mordassa fixa
    cv.rect(x + 3, 111, x + 5, 115, STEELT, 4.4)                     # rosca
    for y in range(111, 116, 2):
        cv.hline(x + 3, x + 5, y, STEELT, 2.4)
    cv.rect(x - 5, 108, x - 3, 116, STEELT, 4.2)                     # mordassa mòbil (el ganxo)
    cv.hline(x - 5, x - 3, 108, STEELT, 5.4)


PROPS = {'cisalla': cisalla, 'clau_tubs': clau_tubs}


# ─── Animacions ─────────────────────────────────────────────────────────────

def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv


def _frames_fluorescent():
    """El fluorescent té la reactància cansada: de tant en tant fa pampallugues, com quan s'encén."""
    base = _base()
    tx, ty = TUBE[0], 22
    dims = {44: 0.8, 45: 0.15, 46: 0.85, 47: 0.85, 48: 0.4, 50: 0.25}   # fotograma → quant s'apaga
    frames = []
    for i in range(56):
        cv = Canvas(light=LIGHT, img=base.img.copy())
        k = dims.get(i, 0)
        if k:
            cv.darken(0, 0, W - 1, FLOOR_Y + 44,
                      lambda x, y: k * max(0.0, 1 - math.hypot(x - tx, (y - ty) * 1.2) / 300), dither=False)
            if k > 0.5:                                               # el tub, gairebé apagat (els extrems roents)
                cv.rect(tx - 37, 21, tx + 37, 23, [(70, 76, 74), (96, 104, 100), (120, 128, 124)], 1.4, lit=0)
                for ex in (tx - 37, tx - 36, tx + 36, tx + 37):
                    cv.vline(ex, 21, 23, [(150, 120, 110), (200, 160, 140)], 1.4, lit=0)
        frames.append(_diff(cv.img, base.img))
    return frames


def _frames_mosca():
    """Una mosca que no deixa en pau l'entrepà vell: s'aixeca, fa voltes i hi torna a parar."""
    base = _base()
    lx, ly = 384, 102                                                # on es para (damunt del pa)
    fly_n, rest_n = 34, 22
    frames = []
    for i in range(fly_n + rest_n):
        cv = Canvas(light=LIGHT, img=base.img.copy())
        if i < fly_n:
            s = i / fly_n
            x = lx + 16 * math.sin(2 * math.pi * s) + 7 * math.sin(6 * math.pi * s)
            y = ly - 14 * math.sin(math.pi * s) - 5 * math.sin(4 * math.pi * s)
            x, y = round(x), round(y)
            cv.flat(x, y, (16, 14, 18))
            cv.flat(x + 1, y, (30, 26, 30))
            wy = y - 1 if i % 2 else y + 1                           # les ales, que vibren
            cv.flat(x, wy, mix(cv.get(x, wy), (200, 210, 220), 0.55))
            cv.flat(x + 1, wy, mix(cv.get(x + 1, wy), (200, 210, 220), 0.4))
        else:
            j = i - fly_n
            dx = 1 if (j // 6) % 2 else 0                            # camina una mica per l'entrepà
            cv.flat(lx + dx, ly, (16, 14, 18))
            cv.flat(lx + dx + 1, ly, (30, 26, 30))
            if j % 7 in (2, 3):                                      # es frega les potes
                cv.flat(lx + dx - 1, ly, (40, 34, 30))
        frames.append(_diff(cv.img, base.img))
    return frames


ANIMS = {'fluorescent': {'frames': _frames_fluorescent, 'frameDuration': 100},
         'mosca': {'frames': _frames_mosca, 'frameDuration': 70}}


# ─── Geometria ─────────────────────────────────────────────────────────────

GEOMETRIA = {
    'things': {
        'porta': {'rect': (2, 46, 60, 152), 'walk': (34, 174)},
        'tauler': {'rect': (81, 27, 313, 92), 'walk': (198, 174)},
        'cisalla': {'rect': (103, 94, 159, 109), 'walk': (130, 176)},
        'clau_tubs': {'rect': (168, 94, 184, 119), 'walk': (176, 176)},
        'banc': {'rect': (322, 92, 470, 154), 'walk': (396, 176)},
    },
    'spawns': {'iri': (220, 188), 'vet': (290, 190)},
    'walkable': [(6, 170), (474, 170), (478, 196), (2, 196)],
}
