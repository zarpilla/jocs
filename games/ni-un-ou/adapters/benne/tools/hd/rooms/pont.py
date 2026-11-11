"""
El pont de l'Arenga, de nit: blau grisós, poca llum (per no enlluernar qui és de guàrdia) i els instruments.

  - els vidres grans del davant: cel de febrer amb núvols, la lluna rere els núvols i el mar fosc;
  - la consola sota els vidres: el radar, el timó (una roda petita de llautó i fusta), el terminal de satèl·lit
    (pantalla verda amb la barra de senyal) i la impressora;
  - a l'esquerra, l'escala que baixa al passadís i la porta estanca de la sala de ràdio;
  - a la dreta, la parada del muntacàrregues, la boca del tub de veu i la porta de l'escala exterior del pal.
Props: `dia` (Escenes 2 i 3, el pont de dia), `safata`, `guardacostes` (els llums del guardacostes de Valmark a l'horitzó) i `fosc` (generador parat).
"""
import functools
import math

from hd.pix import Canvas, Light, W, H, hr, mix, B4
from hd.rooms.arenga import (ENG, CAB, DARK, WHITEP, REDP, YELL, BRASS, WARM, RED_GLOW,
                             box, rrect, bolt, hpipe, vpipe, glow)
from hd.rooms.comu import _diff, text
from hd.rooms.exterior import day_sky, day_sea

# ─── Rampes (fosc → clar) ───────────────────────────────────────────────────
BRI = [(6, 9, 14), (11, 15, 22), (17, 22, 31), (25, 31, 42), (35, 42, 55), (47, 55, 69), (61, 70, 85),
       (78, 88, 103), (100, 110, 124), (128, 137, 150)]
FLOORB = [(5, 6, 9), (9, 11, 15), (14, 17, 22), (20, 24, 30), (28, 32, 39), (38, 43, 51), (50, 56, 64)]
NSKY = [(4, 6, 12), (7, 10, 19), (11, 15, 27), (16, 21, 36), (23, 29, 46), (32, 39, 57), (44, 52, 70),
        (62, 70, 88), (90, 98, 112)]
NSEA = [(2, 5, 9), (4, 9, 15), (7, 14, 22), (11, 20, 30), (16, 28, 40), (24, 38, 52), (40, 58, 72),
        (70, 92, 104), (120, 140, 150)]
SCRG = [(3, 14, 10), (6, 30, 20), (12, 60, 36), (28, 110, 64), (70, 180, 110), (150, 240, 180), (220, 255, 230)]
AMB = [(30, 14, 4), (70, 36, 8), (130, 80, 18), (200, 140, 40), (250, 200, 100), (255, 236, 180)]
WOOD = [(24, 12, 8), (44, 24, 14), (68, 38, 20), (96, 56, 30), (126, 78, 42), (158, 104, 58), (190, 136, 82)]
GREENL = (90, 240, 140)

FLOOR_Y = 152
BOTTOM = 195
WIN = (118, 24, 362, 96)              # els vidres (rectangle exterior dels marcs)
HORIZON = 70
MOON = (150, 40)
LAMP = (300, 10)                      # el llum de sostre (vermellós, de nit)

# `dia` (Escenes 2 i 3): el mateix pont amb la claror grisa d'un matí de febrer pels vidres (vegeu dia())
_MODE = {'dia': False}

LIGHT = Light(ambient=0.35, vignette=(60, 26), floor_fade=None)
LIGHT.point(300, 12, r=170, k=2.0, squash=1.1, down=True, power=1.5)     # llum de sostre, esmorteït
LIGHT.point(276, 112, r=60, k=0.9, power=1.8)                            # pantalla del terminal
LIGHT.point(150, 112, r=50, k=0.7, power=1.8)                            # el radar
LIGHT.point(30, 150, r=60, k=0.7, power=1.8)                             # la llum que puja de l'escala
LIGHT.point(240, 60, r=200, k=0.5, squash=1.4, power=1.2)                # la claror de fora (lluna)

LIGHT_DIA = Light(ambient=1.2, vignette=(60, 26), floor_fade=None)
LIGHT_DIA.point(240, 56, r=280, k=1.9, squash=1.3, power=1.2)            # la claror grisa dels vidres
LIGHT_DIA.point(30, 150, r=60, k=0.4, power=1.8)                         # la llum que puja de l'escala


# ─── Parets i sostre ────────────────────────────────────────────────────────

def wall(cv):
    for y in range(0, FLOOR_Y):
        for x in range(W):
            lvl = 3.4 + (hr(x // 3, y // 5) - 0.5) * 0.3
            if y >= 136:
                lvl -= 0.8
            cv.put(x, y, BRI, lvl)
    # costures de les planxes i reblons
    for fx in range(-20, W, 56):
        cv.vline(fx, 18, FLOOR_Y - 1, BRI, 2.2)
        cv.vline(fx + 1, 18, FLOOR_Y - 1, BRI, 4.2)
        for y in range(26, 134, 14):
            bolt(cv, fx + 3, y, BRI, 3.8)
    cv.hline(0, W - 1, 135, BRI, 4.4)
    cv.hline(0, W - 1, 136, BRI, 2.0)
    cv.hline(0, W - 1, FLOOR_Y - 1, BRI, 1.0)


def ceiling(cv):
    cv.rect(0, 0, W - 1, 17, DARK, 2.2)
    for bx in range(-10, W, 56):                       # baos
        box(cv, bx - 2, 0, bx + 6, 19, BRI, 2.0, grad=0.8)
    cv.hline(0, W - 1, 18, BRI, 1.2)
    cv.hline(0, W - 1, 19, BRI, 3.0)
    # el llum de sostre, amb filtre vermell (llum de nit del pont)
    box(cv, LAMP[0] - 10, 8, LAMP[0] + 10, 13, CAB, 2.6)
    if _MODE['dia']:                                   # de dia, apagat
        cv.rect(LAMP[0] - 8, 13, LAMP[0] + 8, 15, [(60, 14, 12), (90, 50, 46), (120, 96, 92)], 1.6)
    else:
        cv.rect(LAMP[0] - 8, 13, LAMP[0] + 8, 15, [(60, 14, 12), (130, 30, 24), (200, 70, 50), (250, 140, 110)], 2.4,
                lit=0)


def repeaters(cv):
    """La fila d'instruments penjats sobre els vidres: rumb, vent, angle del timó, rellotge."""
    box(cv, 150, 2, 340, 16, ENG, 2.0, grad=0.5)
    cv.hline(152, 338, 3, ENG, 3.4)
    for i, cx in enumerate((168, 206, 244, 282, 320)):
        cv.disc(cx, 9, 6, 6, CAB, 1.4)
        if i == 0:                                        # repetidor de la giroscòpica: esfera ambre
            cv.disc(cx, 9, 5, 5, AMB, lambda nx, ny: 2.6 - ny * 0.6, lit=0)
            cv.vline(cx, 5, 9, DARK, 0, lit=0)
        elif i == 3:                                      # rellotge
            cv.disc(cx, 9, 5, 5, WHITEP, 3.4)
            cv.line(cx, 9, cx, 6, DARK, 0)
            cv.line(cx, 9, cx + 2, 10, DARK, 0)
        else:                                             # vent, angle del timó, ecosonda: digitals
            cv.disc(cx, 9, 5, 5, SCRG, 0.8, lit=0)
            cv.hline(cx - 3, cx + 2, 9, SCRG, 3.6, lit=0)
            cv.put(cx + 3, 8, SCRG, 4.2, lit=0)
        glow(cv, cx, 9, 9, (120, 200, 160) if i in (1, 2, 4) else (230, 170, 80), 0.25)


# ─── Els vidres: cel, lluna i mar ──────────────────────────────────────────

def _cloud(x, y):
    """Densitat de núvols (0..1): bandes horitzontals deformades."""
    v = math.sin(x * 0.031 + math.sin(y * 0.21) * 2.2 + y * 0.12) * 0.5 + 0.5
    v *= math.sin(x * 0.013 - y * 0.05 + 1.3) * 0.5 + 0.5
    return v + (hr(x // 6, y // 3) - 0.5) * 0.25


@functools.lru_cache(maxsize=None)
def _day_outside():
    """El cel i el mar de dia, de tota l'amplada (el cel comença una mica més amunt dels vidres: més clar)."""
    cv = Canvas()
    day_sky(cv, 4, HORIZON - 1, seed=13)
    day_sea(cv, HORIZON, H - 1, seed=6)
    return cv.img


def outside(cv, x0, y0, x1, y1, t=0):
    """Pinta el que es veu per una obertura de (x0, y0) a (x1, y1): cel de nit, núvols, mar. `t` = fotograma."""
    if _MODE['dia']:                                   # de dia: cel gris de febrer i mar gris
        src, dst = _day_outside().load(), cv.P
        for y in range(max(0, y0), min(H - 1, y1) + 1):
            for x in range(max(0, x0), min(W - 1, x1) + 1):
                dst[x, y] = src[x, y]
        return
    mx, my = MOON
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if y < HORIZON:
                d = math.hypot(x - mx, (y - my) * 1.4)
                lvl = 2.6 + (y - 10) * 0.03 + max(0, 1 - d / 70) * 2.8
                c = _cloud(x, y)
                if c > 0.55:
                    lvl += (c - 0.55) * 4.0 * (0.6 + max(0, 1 - d / 90) * 1.6)
                if d < 5.5 and c < 0.75:
                    lvl = 7.4 - d * 0.3                      # la lluna, entre núvols
                if HORIZON - y < 5:
                    lvl += 0.6                               # boirina a l'horitzó
                cv.put(x, y, NSKY, lvl, lit=0)
            else:
                dd = y - HORIZON
                lvl = 2.8 - dd * 0.03
                # onades: franges que es fan grosses a prop
                ph = math.sin(x * (0.18 - dd * 0.002) + dd * 0.9 + math.sin(x * 0.05 + dd * 0.3) * 1.6 + t * 0.8)
                if ph > 0.7:
                    lvl += 0.9
                elif ph < -0.6:
                    lvl -= 0.5
                # el camí de la lluna
                w = 10 + dd * 1.5
                g = math.exp(-((x - mx) / w) ** 2)
                if g > 0.15 and ph > 0.4 and hr(x // 2, y, t // 2) < g * 0.9:
                    lvl += 2.6 * g
                cv.put(x, y, NSEA, lvl, lit=0)
    # la línia de l'horitzó
    for x in range(x0, x1 + 1):
        if y0 <= HORIZON <= y1:
            cv.put(x, HORIZON, NSEA, 3.0 + (0.8 if abs(x - mx) < 18 else 0), lit=0)
    if x0 <= mx <= x1 and y0 <= my <= y1:
        glow(cv, mx, my, 16, (150, 160, 180), 0.35)


PANES = ((122, 178), (184, 240), (246, 302), (308, 358))


def windows(cv, t=0):
    x0, y0, x1, y1 = WIN
    box(cv, x0, y0, x1, y1, BRI, 4.0)
    for a, b in PANES:
        rrect(cv, a, y0 + 4, b, y1 - 4, 4, DARK, 1.0)
        outside(cv, a + 1, y0 + 5, b - 1, y1 - 5, t)
        # la goma del vidre (cantons rodons)
        for y in range(y0 + 4, y1 - 3):
            for x in range(a, b + 1):
                dx = max(a + 4 - x, 0, x - (b - 4))
                dy = max(y0 + 8 - y, 0, y - (y1 - 8))
                d = math.hypot(dx, dy)
                if 3 <= d <= 4.6 or (dx == 0 and dy == 0 and (x in (a, b) or y in (y0 + 4, y1 - 4))):
                    cv.put(x, y, DARK, 0.6, lit=0)
        # reflex del vidre: dues ratlles en diagonal
        for k in (0, 7):
            for i in range(26):
                x, y = a + 8 + k + i, y1 - 10 - i
                if a < x < b and y0 + 6 < y < y1 - 6 and hr(i, k, a) > 0.35:
                    cv.flat(x, y, mix(cv.get(x, y)[:3], (230, 234, 236) if _MODE['dia'] else (120, 130, 150), 0.18))
    # el «clear view», un disc giratori al segon vidre
    cv.ring(212, 46, 11, BRI, 3.0, lit=0.5, step=4)
    cv.disc(212, 46, 2, 2, CAB, 3.6)
    # eixugaparabrises al tercer i quart
    for a, b in PANES[2:]:
        cv.line(a + 8, y1 - 6, (a + b) // 2 + 10, y0 + 14, DARK, 1.4, lit=0)
        cv.put(a + 8, y1 - 6, CAB, 3.4)
    # el marc de dalt, més gruixut, i l'ampit
    cv.hline(x0, x1, y0 + 1, BRI, 5.2)
    box(cv, x0 - 4, y1 + 1, x1 + 4, y1 + 5, BRI, 4.6)
    cv.hline(x0 - 4, x1 + 4, y1 + 6, BRI, 1.0)


# ─── La consola ────────────────────────────────────────────────────────────

CON_TOP = 108


def console(cv):
    # el cos: de paret a paret dels vidres, amb el frontal inclinat
    x0, x1 = 112, 366
    box(cv, x0, CON_TOP, x1, FLOOR_Y + 2, ENG, 2.6, grad=1.0)
    cv.poly([(x0, CON_TOP - 6), (x1, CON_TOP - 6), (x1 + 2, CON_TOP), (x0 - 2, CON_TOP)], ENG,
            lambda x, y: 3.8 + (y - CON_TOP) * 0.08)
    cv.hline(x0 - 2, x1 + 2, CON_TOP - 6, ENG, 4.8)
    cv.hline(x0 - 2, x1 + 2, CON_TOP + 1, ENG, 1.2)
    # portes de servei del frontal
    for dx in range(118, 360, 40):
        rrect(cv, dx, 118, dx + 34, 146, 2, ENG, lambda x, y: 2.2 - (y - 118) * 0.02)
        cv.hline(dx + 2, dx + 32, 118, ENG, 3.4)
        for y in range(124, 142, 3):
            cv.hline(dx + 6, dx + 28, y, ENG, 1.2)
        box(cv, dx + 30, 128, dx + 32, 134, CAB, 3.2)
    # sòcol (puntapeus)
    cv.rect(x0, FLOOR_Y - 2, x1, FLOOR_Y + 2, DARK, 1.4)
    # fila de commutadors i pilots damunt del frontal inclinat
    for i, x in enumerate(range(118, 360, 7)):
        if 168 <= x <= 232 or 246 <= x <= 304:
            continue
        cv.rect(x, CON_TOP - 4, x + 3, CON_TOP - 2, CAB, 1.6)
        cv.put(x + 1, CON_TOP - 4, CAB, 4.4)
        if hr(i, 3) > 0.6:
            col = (90, 240, 140) if hr(i, 4) > 0.4 else (255, 180, 60)
            cv.flat(x + 1, CON_TOP - 2, col)


def radar(cv):
    """El radar: una caixa amb la pantalla rodona, amb la costa a l'est i ecos."""
    cx, cy = 150, 92
    box(cv, 126, 74, 174, CON_TOP - 6, CAB, 2.4, grad=0.6)
    cv.hline(127, 173, 75, CAB, 3.8)
    cv.disc(cx, cy, 13, 13, DARK, 1.0)
    cv.disc(cx, cy, 12, 12, SCRG, lambda nx, ny: 1.1 - math.hypot(nx, ny) * 0.3, lit=0)
    for r in (4, 8, 12):
        cv.ring(cx, cy, r, SCRG, 2.0, lit=0, step=12)
    for x, y in ((cx + 6, cy - 4), (cx - 5, cy + 7), (cx + 2, cy + 9)):
        cv.put(x, y, SCRG, 4.0, lit=0)
    for i in range(6):                                       # la costa
        cv.put(cx + 9 + (i % 2), cy - 6 + i * 2, SCRG, 3.4, lit=0)
    _sweep(cv, cx, cy, 30)
    for i, bx in enumerate((130, 136, 164, 170)):
        cv.disc(bx, 101, 1.5, 1.5, CAB, 3.8)
    glow(cv, cx, cy, 20, (90, 220, 140), 0.25)


def _sweep(cv, cx, cy, ang):
    for r in range(1, 12):
        x = cx + round(math.cos(math.radians(ang)) * r)
        y = cy + round(math.sin(math.radians(ang)) * r)
        cv.put(x, y, SCRG, 4.6, lit=0)
        for k in (1, 2):
            a = math.radians(ang - k * 12)
            cv.put(cx + round(math.cos(a) * r), cy + round(math.sin(a) * r), SCRG, 3.4 - k * 0.8, lit=0)


def wheel(cv):
    """El timó: pedestal davant la consola i una roda petita de fusta amb puny de llautó."""
    cx, cy = 202, 120
    # pedestal
    box(cv, 194, 132, 210, FLOOR_Y + 4, ENG, 2.8, grad=0.8)
    cv.hline(194, 210, 132, ENG, 4.2)
    box(cv, 190, FLOOR_Y + 2, 214, FLOOR_Y + 6, ENG, 2.0)
    # la roda
    for a in range(0, 360, 2):
        for rr in (12, 13):
            x = cx + round(math.cos(math.radians(a)) * rr)
            y = cy + round(math.sin(math.radians(a)) * rr * 0.92)
            cv.put(x, y, WOOD, 4.0 - math.sin(math.radians(a)) * 1.2 - (rr - 12) * 0.8)
    for a in range(0, 360, 45):
        cv.line(cx, cy, cx + round(math.cos(math.radians(a)) * 12), cy + round(math.sin(math.radians(a)) * 11),
                WOOD, 3.2)
        hx, hy = cx + round(math.cos(math.radians(a)) * 16), cy + round(math.sin(math.radians(a)) * 15)
        cv.line(cx + round(math.cos(math.radians(a)) * 13), cy + round(math.sin(math.radians(a)) * 12), hx, hy,
                WOOD, 4.4)
    cv.disc(cx, cy, 3, 3, BRASS, lambda nx, ny: 4.0 - nx - ny)


def terminal(cv, bar=7):
    """El terminal de satèl·lit: pantalla verda, amb el text i la barra de senyal; el SAI a sota."""
    x0, y0, x1, y1 = 252, 76, 300, 104
    box(cv, x0, y0, x1, y1, CAB, 2.2, grad=0.6)
    cv.hline(x0 + 1, x1 - 1, y0 + 1, CAB, 3.8)
    screen(cv, bar)
    # peu i teclat
    box(cv, 272, y1 + 1, 280, CON_TOP - 5, CAB, 1.8)
    cv.poly([(254, CON_TOP - 5), (298, CON_TOP - 5), (300, CON_TOP - 1), (252, CON_TOP - 1)], CAB, 2.8)
    for x in range(256, 297, 3):
        cv.put(x, CON_TOP - 3, CAB, 4.4)
    # el SAI, al frontal, amb el pilot verd i la marca de bateria
    box(cv, 252, 112, 296, 126, CAB, 2.0)
    for i in range(5):
        cv.rect(256 + i * 5, 117, 259 + i * 5, 121, SCRG, 3.4 if i < 4 else 1.4, lit=0)
    cv.rect(282, 116, 292, 121, WHITEP, 3.0)
    cv.flat(286, 124, GREENL)
    glow(cv, 286, 124, 4, GREENL, 0.5)
    # el cable de l'antena, que baixa del sostre
    vpipe(cv, 305, 20, 92, 1, CAB, 2.4)
    cv.line(305, 92, 300, 96, CAB, 2.4)


def screen(cv, bar=7, blink=True):
    x0, y0, x1, y1 = 256, 80, 296, 100
    cv.rect(x0, y0, x1, y1, SCRG, lambda x, y: 1.0 + (0.3 if y % 2 else 0), lit=0)
    text(cv, 'SAT', x0 + 3, y0 + 3, SCRG, 4.6, lit=0)
    cv.hline(x0 + 17, x0 + 28, y0 + 5, SCRG, 3.0, lit=0)
    # la barra de senyal: 10 graons que pugen
    for i in range(10):
        bx = x0 + 3 + i * 3
        h = 2 + i // 2
        on = i < bar
        cv.rect(bx, y1 - 3 - h, bx + 1, y1 - 3, SCRG, 4.4 if on else 2.0, lit=0)
    if blink:
        cv.rect(x1 - 5, y1 - 6, x1 - 3, y1 - 3, SCRG, 5.0, lit=0)
    glow(cv, (x0 + x1) / 2, (y0 + y1) / 2, 26, (90, 220, 140), 0.22)


def printer(cv):
    """La impressora: capsa beix amb la safata de paper i un full a mig sortir."""
    x0, y0, x1, y1 = 308, 90, 346, CON_TOP - 4
    box(cv, x0, y0, x1, y1, WHITEP, 2.8, grad=0.8)
    cv.hline(x0 + 1, x1 - 1, y0 + 1, WHITEP, 3.8)
    cv.rect(x0 + 4, y0 + 4, x1 - 4, y0 + 6, DARK, 1.0)          # la boca
    cv.poly([(x0 + 6, y0 + 5), (x1 - 6, y0 + 5), (x1 - 9, y0 - 6), (x0 + 9, y0 - 6)], WHITEP, 4.2)
    for y in range(y0 - 4, y0 + 3, 2):
        cv.hline(x0 + 12, x1 - 14, y, WHITEP, 3.0)
    cv.flat(x1 - 6, y1 - 4, GREENL)
    cv.rect(x0 + 4, y1 - 5, x0 + 14, y1 - 3, CAB, 2.0)


# ─── A l'esquerra: l'escala avall i la porta de la ràdio ──────────────────

def stairs_down(cv):
    """La boca de l'escala que baixa al passadís: sense porta, amb passamans i la llum càlida de baix."""
    x0, y0, x1, y1 = 8, 66, 52, FLOOR_Y
    for y in range(y0, y1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, DARK, 1.0 + (y - y0) * 0.01, lit=0.2)
    # els graons que baixen (es veuen els cantells, cada cop més avall i amb llum càlida)
    for i in range(7):
        sy = 108 + i * 7
        cv.rect(x0 + 2, sy, x1 - 2, sy + 1, BRI, 3.2 + i * 0.25, lit=0.5)
        cv.rect(x0 + 2, sy + 2, x1 - 2, sy + 6, BRI, 1.4 + i * 0.2, lit=0.3)
        cv.hline(x0 + 2, x1 - 2, sy, YELL, 2.4, lit=0.2)         # cantell antilliscant
    for y in range(100, y1):
        k = (y - 100) / (y1 - 100) * 0.5
        cv.tint(x0 + 1, y, x1 - 1, y, WARM, k * 0.5)
    # el marc
    for t in range(3):
        cv.vline(x0 - t, y0 - t, y1, BRI, 4.4 - t)
        cv.vline(x1 + t, y0 - t, y1, BRI, 3.8 - t)
        cv.hline(x0 - t, x1 + t, y0 - t, BRI, 4.6 - t)
    # els passamans, de tub
    for hx in (x0 + 4, x1 - 4):
        cv.line(hx, 100, hx, 148, CAB, 3.4)
        cv.line(hx + 1, 100, hx + 1, 148, CAB, 1.8)
        cv.line(hx, 100, hx + (6 if hx < 30 else -6), 92, CAB, 3.6)
    # un rètol: fletxa avall
    box(cv, 22, 54, 38, 61, WHITEP, 3.6)
    for i in range(3):
        cv.hline(30 - i, 30 + i, 59 - i, DARK, 0.5)
    cv.vline(30, 55, 57, DARK, 0.5)
    glow(cv, 30, 140, 22, WARM, 0.25)


def door_frame(cv, x0, y0, x1, y1, ramp, r=9):
    """El marc d'una porta estanca (cantons rodons de dalt), tres gruixos."""
    for t in range(3):
        for y in range(y0 - t, y1 + 1):
            for x in range(x0 - t, x1 + t + 1):
                dx = max(x0 - t + r - x, 0, x - (x1 + t - r))
                dy = max(y0 - t + r - y, 0)
                inside = dx * dx + dy * dy <= r * r
                ddx = max(x0 - t + 1 + r - x, 0, x - (x1 + t - 1 - r))
                ddy = max(y0 - t + 1 + r - y, 0)
                inner = x0 - t + 1 <= x <= x1 + t - 1 and y >= y0 - t + 1 and ddx * ddx + ddy * ddy <= r * r
                if inside and not inner:
                    cv.put(x, y, ramp, 4.4 - t * 0.9)


def ws_door(cv, x0, y0, x1, y1, ramp, lvl=3.0, wheel=True):
    """Fulla de porta estanca tancada: cantons rodons, nervis, palanques i volant."""
    rrect(cv, x0, y0, x1, y1, 8, ramp, lambda x, y: lvl - (y - y0) * 0.006 - (x - x0) * 0.008)
    for yy in (y0 + 3, y1 - 3):
        cv.hline(x0 + 6, x1 - 6, yy, ramp, lvl + 1.0)
    # nervi vertical i horitzontal
    cv.hline(x0 + 3, x1 - 3, (y0 + y1) // 2, ramp, lvl + 0.8)
    cv.hline(x0 + 3, x1 - 3, (y0 + y1) // 2 + 1, ramp, lvl - 1.0)
    # palanques («dogs»)
    for dy in (y0 + 14, y1 - 14):
        box(cv, x1 - 4, dy, x1 + 2, dy + 2, CAB, 3.6)
        box(cv, x0 - 2, dy, x0 + 4, dy + 2, CAB, 3.6)
    if wheel:
        cx, cy = (x0 + x1) // 2, (y0 + y1) // 2 - 10
        cv.ring(cx, cy, 6, CAB, 3.6, step=6)
        cv.ring(cx, cy, 5, CAB, 2.2, step=6)
        cv.disc(cx, cy, 1.5, 1.5, CAB, 4.0)
        cv.line(cx - 5, cy, cx + 5, cy, CAB, 3.0)


def radio_door(cv):
    x0, y0, x1, y1 = 66, 66, 106, FLOOR_Y
    door_frame(cv, x0, y0, x1, y1, BRI)
    ws_door(cv, x0 + 1, y0 + 1, x1 - 1, y1 - 2, BRI, 3.2)
    cv.rect(x0 + 1, y1 - 2, x1 - 1, y1, BRI, 2.0)
    # plaqueta «RÀDIO»
    box(cv, 72, 54, 100, 61, WHITEP, 3.8)
    text(cv, 'RÀDIO', 75, 56, BRI, 1.0)
    # un fil de llum per sota (hi ha el llum encès)
    cv.hline(x0 + 4, x1 - 4, y1 - 1, [(60, 50, 30), (140, 120, 80)], 1.2, lit=0)


def barometer(cv):
    """El baròmetre i el rellotge de llautó, a la paret, sobre la porta de la ràdio."""
    for cx, kind in ((76, 'b'), (98, 'r')):
        cv.disc(cx, 34, 9, 9, BRASS, lambda nx, ny: 3.6 - nx - ny * 1.2)
        cv.disc(cx, 34, 7, 7, WHITEP, lambda nx, ny: 3.8 - ny * 0.6)
        if kind == 'b':
            for a in range(200, 341, 28):
                cv.put(cx + round(math.cos(math.radians(a)) * 5), 34 + round(math.sin(math.radians(a)) * 5), DARK, 0.4)
            cv.line(cx, 34, cx + 3, 30, DARK, 0.2)
            cv.line(cx, 34, cx - 2, 30, BRASS, 3.0)
        else:
            for a in range(0, 360, 90):
                cv.put(cx + round(math.cos(math.radians(a)) * 5), 34 + round(math.sin(math.radians(a)) * 5), DARK, 0.4)
            cv.line(cx, 34, cx, 29, DARK, 0.2)
            cv.line(cx, 34, cx + 3, 35, DARK, 0.2)
        cv.ring(cx, 34, 9, BRASS, 1.8, step=8)
    box(cv, 82, 46, 92, 49, BRASS, 3.0)


# ─── A la dreta: muntacàrregues, tub de veu i la porta del pal ────────────

def dumbwaiter(cv):
    x0, y0, x1, y1 = 372, 60, 414, 110
    box(cv, x0, y0, x1, y1, CAB, 3.0, grad=0.6)
    # l'obertura, amb la porteta de guillotina pujada
    box(cv, x0 + 4, y0 + 14, x1 - 4, y1 - 4, DARK, 1.0)
    for y in range(y0 + 16, y1 - 5):
        cv.hline(x0 + 5, x1 - 5, y, DARK, 1.4 + (y - y0 - 16) * 0.03, lit=0.3)
    cv.vline(x0 + 5, y0 + 16, y1 - 5, CAB, 1.8)
    cv.hline(x0 + 4, x1 - 4, y1 - 6, CAB, 3.6)                 # el replà de la safata
    box(cv, x0 + 4, y0 + 4, x1 - 4, y0 + 12, CAB, 3.6)          # la porteta, a dalt
    box(cv, (x0 + x1) // 2 - 4, y0 + 10, (x0 + x1) // 2 + 4, y0 + 12, BRASS, 3.4)
    # els botons (puja / baixa) i el timbre
    box(cv, x1 + 2, 74, x1 + 6, 88, CAB, 2.6)
    cv.disc(x1 + 4, 78, 1.5, 1.5, REDP, 4.4, lit=0.5)
    cv.disc(x1 + 4, 84, 1.5, 1.5, SCRG, 3.6, lit=0.5)


def voice_tube(cv):
    """La boca del tub de veu: el tub de llautó que baixa del sostre i la campana amb tapa."""
    cx = 426
    vpipe(cv, cx, 20, 80, 2, BRASS, 2.6)
    for y in (32, 60):
        box(cv, cx - 3, y, cx + 3, y + 2, CAB, 3.2)
    cv.disc(cx, 84, 4, 4, BRASS, lambda nx, ny: 3.2 - nx * 1.2 - ny)
    cv.disc(cx, 88, 6, 5, BRASS, lambda nx, ny: 3.5 - nx * 1.3 - ny * 1.2)
    cv.disc(cx, 88, 4, 3, BRASS, lambda nx, ny: 1.2 + nx * 0.6 + ny * 0.8)
    cv.disc(cx, 88, 2, 1.5, DARK, 0.6)
    for i, y in enumerate(range(94, 100)):
        cv.put(cx + 3 + (i % 2), y, BRASS, 3.0)
    cv.disc(cx + 4, 101, 2.5, 1.5, BRASS, 3.6)
    box(cv, cx - 7, 106, cx + 7, 109, BRASS, 2.8)


MAST_DOOR = (444, 60, 478, FLOOR_Y)


def mast_door(cv):
    """La porta de l'escala exterior del pal, oberta: fora, la nit, la barana i els esglaons del pal."""
    x0, y0, x1, y1 = MAST_DOOR
    outside(cv, x0, y0, x1, y1)
    # la coberta del costat (ala del pont), la barana blanca i la línia vermella
    for y in range(126, y1):
        cv.hline(x0, x1, y, DARK, 1.6 + (y - 126) * 0.03, lit=0)
    cv.hline(x0, x1, 112, WHITEP, 2.0, lit=0)
    cv.hline(x0, x1, 120, WHITEP, 1.6, lit=0)
    cv.rect(x0, 124, x1, 127, REDP, 2.2, lit=0)
    for x in range(x0 + 2, x1, 12):
        cv.vline(x, 112, 126, WHITEP, 1.4, lit=0)
    # l'escala del pal, que puja: dos muntants i els esglaons
    for sx in (458, 470):
        cv.vline(sx, y0, 140, CAB, 2.6, lit=0)
    for y in range(y0 + 4, 140, 6):
        cv.hline(458, 470, y, CAB, 2.2, lit=0)
    # una mica de llum groga de coberta
    glow(cv, 466, 70, 12, (255, 200, 110), 0.4)
    cv.disc(466, 66, 2, 2, YELL, 5, lit=0)
    # el marc i la fulla oberta cap a dins (de cantó)
    door_frame(cv, x0, y0, x1 + 4, y1, BRI)
    cv.rect(x0 + 1, y1 - 5, x1, y1 - 1, BRI, 2.6)                 # el llindar alt
    cv.hline(x0 + 1, x1, y1 - 5, BRI, 4.0)
    cv.poly([(432, y0 + 4), (440, y0 - 1), (440, y1 - 2), (432, y1 - 4)], BRI, lambda x, y: 3.2 - (x - 432) * 0.08)
    box(cv, 434, 100, 438, 104, CAB, 3.6)


# ─── El terra ───────────────────────────────────────────────────────────────

VP = (240, 40)


def floor(cv):
    """Linòleum gris blavós de rajoles, gastat pel camí del timó."""
    for y in range(FLOOR_Y, BOTTOM + 12):
        d = y - VP[1]
        for x in range(W):
            u = VP[0] + (x - VP[0]) * 150 / d
            u2 = VP[0] + (x + 1 - VP[0]) * 150 / d
            v = 2400 / d
            lvl = 3.6 + (hr(int(u // 30), int(v // 2.5)) - 0.5) * 0.5
            if int(u // 30) != int(u2 // 30) or int(v // 2.5) != int(2400 / (d + 1) // 2.5):
                lvl = 2.4
            if abs(x - 210) < 40 - (y - FLOOR_Y) * 0.2 and hr(x // 2, y) > 0.5:
                lvl += 0.4                                      # gastat davant del timó
            cv.put(x, y, FLOORB, lvl)
    cv.hline(0, W - 1, FLOOR_Y, FLOORB, 1.0)
    # una estora de goma davant la consola
    for y in range(FLOOR_Y + 6, FLOOR_Y + 16):
        for x in range(150 - (y - FLOOR_Y), 330 + (y - FLOOR_Y)):
            cv.put(x, y, FLOORB, 1.6 + (0.6 if (x + y) % 4 == 0 else 0))


def chair(cv):
    """La cadira alta del pont, girada, a la dreta del timó (fixada a terra)."""
    cx = 346
    box(cv, cx - 2, 138, cx + 2, FLOOR_Y + 12, CAB, 2.6)
    cv.disc(cx, FLOOR_Y + 12, 10, 2.5, CAB, 1.8)
    box(cv, cx - 12, 128, cx + 12, 136, ENG, 3.4, grad=0.6)      # seient
    box(cv, cx + 8, 100, cx + 13, 130, ENG, 3.2)                  # respatller
    box(cv, cx - 12, 124, cx - 8, 128, CAB, 3.0)                  # braç


# ─── Muntatge ───────────────────────────────────────────────────────────────

def bg(cv, t=0, sweep=30, bar=7, blink=True):
    wall(cv)
    ceiling(cv)
    windows(cv, t)
    repeaters(cv)
    console(cv)
    radar(cv)
    terminal(cv, bar)
    printer(cv)
    stairs_down(cv)
    radio_door(cv)
    barometer(cv)
    dumbwaiter(cv)
    voice_tube(cv)
    mast_door(cv)
    floor(cv)
    wheel(cv)
    chair(cv)
    if not _MODE['dia']:
        glow(cv, LAMP[0], 16, 24, (255, 120, 90), 0.35)


# ─── Props ──────────────────────────────────────────────────────────────────

def safata(cv):
    """Una safata d'acer al replà del muntacàrregues, amb una tassa."""
    cv.poly([(378, 103), (408, 103), (410, 106), (376, 106)], CAB, 4.0)
    cv.hline(376, 410, 106, CAB, 2.0)
    cv.rect(386, 97, 392, 103, WHITEP, 3.6)
    cv.vline(393, 99, 101, WHITEP, 3.0)
    cv.rect(398, 100, 404, 103, [(30, 20, 10), (70, 50, 30)], 1.0)


def guardacostes(cv):
    """Els llums del guardacostes de Valmark, a l'horitzó del tercer vidre: la silueta, el llum blanc de pal,
    el vermell de babord i el blau del pont."""
    cx, hy = 276, HORIZON
    cv.poly([(cx - 14, hy), (cx + 12, hy), (cx + 10, hy + 2), (cx - 12, hy + 2)], NSKY, 0.4, lit=0)
    cv.rect(cx - 4, hy - 4, cx + 4, hy - 1, NSKY, 0.6, lit=0)
    cv.vline(cx, hy - 8, hy - 4, NSKY, 0.6, lit=0)
    for x, y, col in ((cx, hy - 9, (255, 250, 230)), (cx - 6, hy - 2, (255, 60, 50)),
                      (cx + 3, hy - 4, (230, 240, 255)), (cx + 8, hy - 1, (255, 230, 200))):
        cv.flat(x, y, col)
    # els reflexos a l'aigua
    for i in range(1, 9, 2):
        cv.flat(cx - 6, hy + 2 + i, (150, 40, 40))
        cv.flat(cx, hy + 3 + i, (140, 140, 130))
    # el blau intermitent (fix al dibuix, l'anima la mida del glow)
    cv.flat(cx - 2, hy - 6, (90, 150, 255))
    cv.flat(cx - 1, hy - 6, (90, 150, 255))


def _guardacostes_glow(cv):
    guardacostes(cv)


def fosc(cv):
    """El generador parat: tot fosc, només els llums d'emergència vermells i les pantalles amb el SAI."""
    P = cv.P
    lamps = ((40, 26), (398, 26))
    for y in range(H):
        for x in range(W):
            a = 165
            r = g = b = 0
            for lx, ly in lamps:
                d = math.hypot(x - lx, (y - ly) * 1.1)
                if d < 110:
                    f = (1 - d / 110) ** 1.6
                    a -= int(70 * f)
                    r += int(150 * f)
            # el terminal (SAI) encara fa claror
            d = math.hypot(x - 276, y - 92)
            if d < 46:
                a -= int(80 * (1 - d / 46) ** 1.5)
            a = max(0, min(255, a))
            if a > 0:
                P[x, y] = (min(255, 4 + r // 3), 2, 8, a)
    # els llums d'emergència: caixeta i bombeta vermella encesa
    for lx, ly in lamps:
        for y in range(ly - 3, ly + 3):
            for x in range(lx - 7, lx + 8):
                P[x, y] = (40, 40, 46, 255)
        for y in range(ly - 1, ly + 3):
            for x in range(lx - 5, lx + 6):
                if ((x - lx) / 5.5) ** 2 + ((y - ly - 1) / 2.2) ** 2 <= 1:
                    P[x, y] = (255, 80 if y == ly else 40, 30, 255)


def dia(cv):
    """Decorat `dia` (sota, Escenes 2 i 3): el pont sencer de dia, amb el cel i el mar grisos pels vidres i la
    claror freda que entra. Deixa forats a les pantalles del radar i del terminal (s'hi veuen les animacions)."""
    _MODE['dia'] = True
    try:
        day = Canvas(light=LIGHT_DIA)
        bg(day)
    finally:
        _MODE['dia'] = False
    # la claror de fora és freda: tot una mica cap al gris blavós
    day.tint(0, 0, W - 1, H - 1, (150, 160, 172), 0.1)
    src, o = day.img.load(), cv.P
    for y in range(H):
        for x in range(W):
            if math.hypot(x - 150, y - 92) <= 12.5 or (256 <= x <= 296 and 80 <= y <= 100):
                continue
            o[x, y] = src[x, y]


PROPS = {'dia': dia, 'safata': safata, 'guardacostes': guardacostes, 'fosc': fosc}


# ─── Animacions ────────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv.img


def _frames_radar():
    base = _base()
    frames = []
    for i in range(12):
        cv = Canvas(light=LIGHT, img=base.copy())
        cx, cy = 150, 92
        cv.disc(cx, cy, 12, 12, SCRG, lambda nx, ny: 1.1 - math.hypot(nx, ny) * 0.3, lit=0)
        for r in (4, 8, 12):
            cv.ring(cx, cy, r, SCRG, 2.0, lit=0, step=12)
        ang = 30 + i * 30
        for k, (x, y) in enumerate(((cx + 6, cy - 4), (cx - 5, cy + 7), (cx + 2, cy + 9))):
            a = (math.degrees(math.atan2(y - cy, x - cx)) - ang) % 360
            cv.put(x, y, SCRG, 4.6 if a > 300 else 3.0, lit=0)
        for j in range(6):
            cv.put(cx + 9 + (j % 2), cy - 6 + j * 2, SCRG, 3.4, lit=0)
        _sweep(cv, cx, cy, ang)
        glow(cv, cx, cy, 20, (90, 220, 140), 0.25)
        frames.append(_diff(cv.img, base))
    return frames


def _frames_terminal():
    """El cursor de la pantalla, que parpelleja."""
    base = _base()
    cv = Canvas(light=LIGHT, img=base.copy())
    cv.rect(291, 94, 293, 97, SCRG, 1.0, lit=0)
    return [_diff(base, base), _diff(cv.img, base)]


def _frames_mar():
    """El mar pel vidre: les onades corren i el camí de la lluna espurneja."""
    base = _base()
    frames = []
    x0, y0, x1, y1 = WIN
    for i in range(8):
        cv = Canvas(light=LIGHT, img=base.copy())
        tmp = Canvas(light=LIGHT)
        outside(tmp, x0, HORIZON + 1, x1, y1, t=i)
        src, dst = tmp.img.load(), cv.img.load()
        orig = base.load()
        ref = Canvas(light=LIGHT)
        outside(ref, x0, HORIZON + 1, x1, y1, t=0)
        rp = ref.img.load()
        for y in range(HORIZON + 1, y1):
            for x in range(x0, x1 + 1):
                if orig[x, y] == rp[x, y]:                     # només on es veu el mar (no els marcs)
                    dst[x, y] = src[x, y]
        frames.append(_diff(cv.img, base))
    return frames


ANIMS = {'radar': {'frames': _frames_radar, 'frameDuration': 220},
         'terminal': {'frames': _frames_terminal, 'frameDuration': 530},
         'mar': {'frames': _frames_mar, 'frameDuration': 260}}


# ─── Geometria ─────────────────────────────────────────────────────────────

def _t(x0, y0, x1, y1, wx=None, wy=180):
    return {'rect': (x0, y0, x1, y1), 'walk': (wx if wx is not None else (x0 + x1) // 2, wy)}


GEOMETRIA = {
    'things': {
        'escala': _t(8, 64, 52, 150, wx=32, wy=170),
        'porta_radio': _t(64, 62, 108, 150, wy=170),
        'vidre': _t(118, 24, 362, 96, wx=250, wy=172),
        'timo': _t(186, 104, 218, 156, wx=204, wy=176),
        'terminal': _t(252, 76, 300, 126, wx=276, wy=172),
        'impressora': _t(306, 82, 348, 106, wx=326, wy=172),
        'munta': _t(372, 60, 414, 110, wx=392, wy=172),
        'safata': _t(376, 96, 410, 107, wx=392, wy=172),
        'boca': _t(418, 78, 434, 104, wx=424, wy=172),
        'escala_pal': _t(440, 58, 478, 150, wx=462, wy=172),
    },
    'spawns': {'iri': (300, 188), 'vet': (150, 192), 'capitana': (236, 184)},
    'walkable': [(10, 164), (470, 164), (476, 200), (4, 200)],
}
