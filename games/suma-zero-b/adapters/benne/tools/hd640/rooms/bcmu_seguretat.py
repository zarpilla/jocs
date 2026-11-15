"""
La sala de seguretat del BCMU (Escena 6, la Vet amb en Ballester) a 640×360: la composició de
hd/rooms/bcmu_seguretat.py ×4/3, dibuixada de nou amb més detall.
  - una sala de control fosca, sense finestres: plafons acústics blau marí, moqueta de rajoles gastada i un llum
    de sostre que ningú no encén; la llum és la de la paret de monitors (cian) i poca cosa més;
  - la paret de monitors (5×3): el vestíbul de marbre, el moll amb les furgonetes, passadissos, la porta de les
    caixes fortes, una sala buida i senyals de «SENSE SENYAL»; ningú no els mira;
  - la taula de control llarga: teclats, un micròfon, el got d'aigua (a la vora, massa a la vora), la tassa
    «MILLOR AVI», una foto de família girada i una planta morta; i on van l'entrepà, el clauer i el collaret;
  - la ràdio d'en Ballester al seu suport de paret (amb el llum vermell), un calendari de 1994 que ningú no ha
    canviat, la cadira giratòria amb el coixí aixafat, l'estació del tub i l'ascensor.
  Props: `entrepa`, `clauer`, `collaret` (es poden agafar), `got_trencat` i `collaret_taula`.
  Animació: `monitors` (els monitors canvien de pla, la gent s'hi mou i un fa neu).
"""
import math

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from hd.pix import Light, Canvas, W, H, hr
from hd.rooms.comu import obox, outline, text, text_width, _diff, SHEET, CARD, RED
from hd.rooms.bar_sala import STEELB, SLATE
from hd.rooms.pis_cuina import outline_poly
from hd.rooms.aeroport_terminal import CHROME
from hd.rooms.bcmu_seguretat import ACOUSTIC, TILEF, CONSOLE, FOIL, LEAF, POT, WATER, LEDR, PLASTICR  # noqa: F401
from hd640.rooms.bcmu import BRASS, MAHOG, NAVYB, SCREENB, CONCB, GLASSB, tub_station, logo

FLOOR_Y = 200
DESK_TOP = 157          # el tauler de la taula de control
DESK = (195, 485)       # x de la taula

LIGHT = Light(ambient=-0.9, vignette=(93, 48), floor_fade=(245, 40))
LIGHT.point(313, 75, r=307, k=3.4, squash=1.25, power=1.4)           # la paret de monitors
LIGHT.point(112, 40, r=80, k=0.6, squash=1.0, power=2.0)             # l'indicador de l'ascensor
LIGHT.point(532, 133, r=40, k=0.5, squash=1.0, power=2.0)            # el llum de la ràdio
LIGHT.point(45, 115, r=53, k=0.5, squash=1.0, power=2.0)             # el llautó del tub

MON = (173, 24, 453, 123)
COLS, ROWS = 5, 3


# ─── Paret, sostre, terra ──────────────────────────────────────────────────

def wall(cv):
    """Plafons acústics blau marí, perforats, amb juntes; un sostre baix amb el llum apagat i un sòcol d'alumini."""
    for y in range(0, FLOOR_Y):
        for x in range(W):
            seam = x % 53 == 0 or y % 66 == 0
            lip = x % 53 == 1 or y % 66 == 1                              # el bisell del plafó
            hole = (x % 4 == 2 and y % 4 == 2) or (x % 4 == 0 and y % 4 == 0)
            n = (hr(x // 53, y // 66, 4) - 0.5) * 0.4 + (hr(x, y, 5) - 0.5) * 0.1
            cv.put(x, y, ACOUSTIC, 1.6 if seam else (3.0 + n - (0.5 if hole else 0) + (0.5 if lip else 0)))
    # el sostre baix amb el llum apagat i un conducte
    cv.rect(0, 0, W - 1, 9, CONCB, lambda x, y: 2.4 + (0.3 if x % 80 == 0 else 0))
    cv.hline(0, W - 1, 10, CONCB, 1.0)
    obox(cv, 507, 1, 600, 7, CHROME, 1.6)
    cv.rect(512, 3, 595, 4, [(70, 76, 84)], 0, lit=0)
    for lx in range(520, 595, 12):                                       # la reixeta del llum
        cv.vline(lx, 3, 4, CHROME, 1.0)
    cv.rect(0, FLOOR_Y - 5, W - 1, FLOOR_Y - 1, CHROME, lambda x, y: 2.6 if y == FLOOR_Y - 5 else 1.8)
    cv.hline(0, W - 1, FLOOR_Y, SLATE, 0)


def floor(cv):
    """Rajoles de moqueta grises, gastades davant la taula i el camí de l'ascensor; el reflex dels monitors."""
    for y in range(FLOOR_Y + 1, H):
        for x in range(W):
            dy = y - FLOOR_Y
            tx, ty = (x + dy // 2) // 32, dy // 16
            n = (hr(x, y, 3) - 0.5) * 0.5 + (hr(tx, ty, 8) - 0.5) * 0.5
            seam = (x + dy // 2) % 32 == 0 or dy % 16 == 0
            pile = 0.25 if (tx + ty) % 2 and (x + y) % 3 == 0 else 0         # el pèl de la moqueta, girat a quadres
            worn = max(0, 1 - math.hypot((x - 400) / 80, (y - 224) / 19)) * 0.8 + \
                max(0, 1 - abs(x - 112) / 40) * max(0, 1 - dy / 35) * 0.6
            cv.put(x, y, TILEF, (2.4 if seam else 3.4 + n + pile) + worn)
    cv.tint(187, 203, 467, 261, (80, 220, 230), lambda x, y: 0.10 * max(0, 1 - abs(x - 320) / 147) * max(0, 1 - (y - 203) / 59))


# ─── L'ascensor i el tub ───────────────────────────────────────────────────

def lift(cv):
    """L'ascensor: marc de llautó (la casa), portes d'acer raspallat i l'indicador de planta."""
    x0, y0, x1, y1 = 75, 53, 144, FLOOR_Y
    obox(cv, x0 - 5, y0 - 5, x1 + 5, y1, BRASS, 2.6)
    cv.hline(x0 - 4, x1 + 4, y0 - 4, BRASS, 3.6)
    cv.vline(x0 - 4, y0 - 4, y1 - 1, BRASS, 3.4)
    for x in range(x0, x1 + 1):
        for y in range(y0, y1):
            cv.put(x, y, STEELB, 3.4 + (hr(x, 7) - 0.5) * 0.5 + (hr(x, y // 9, 8) - 0.5) * 0.15 - (0.8 if x in (x0, x1) else 0))
    cx = (x0 + x1) // 2
    cv.vline(cx, y0, y1 - 1, SLATE, 0.6)
    cv.vline(cx + 1, y0, y1 - 1, STEELB, 5.0)
    cv.tint(x0 + 1, y0, x1 - 1, y1 - 1, (120, 230, 240), lambda x, y: 0.06 if (x - x0) % 34 < 6 else 0)   # el reflex dels monitors
    outline(cv, x0, y0, x1, y1, SLATE)
    cv.hline(x0, x1, y1 - 1, SLATE, 1.2)                                  # el carril de terra
    # l'indicador: «-1» en ambre
    obox(cv, cx - 13, y0 - 21, cx + 13, y0 - 8, MAHOG, 1.4)
    cv.rect(cx - 11, y0 - 19, cx + 11, y0 - 10, [(30, 10, 6)], 0, lit=0)
    text(cv, '-1', cx - text_width('-1') // 2, y0 - 17, [(255, 170, 60)], 0, lit=0, flat=(255, 176, 70))
    cv.flat(cx + 8, y0 - 17, (255, 176, 70))                              # la fletxeta de baixada
    cv.hline(cx + 7, cx + 9, y0 - 18, [(140, 80, 30)], 0, lit=0)
    cv.glow(cx, y0 - 14, 13, (255, 160, 60), 0.3)
    # el botó
    obox(cv, x1 + 9, 128, x1 + 17, 144, BRASS, 3.2)
    cv.disc(x1 + 13, 136, 2, 2, [(200, 120, 60), (255, 200, 120), (255, 236, 190)], lambda nx, ny: 1.6 - ny, lit=0)


# ─── La paret de monitors ──────────────────────────────────────────────────

def _cell(i):
    x0, y0, x1, y1 = MON
    cw, ch = (x1 - x0) // COLS, (y1 - y0) // ROWS
    c, r = i % COLS, i // COLS
    return x0 + c * cw + 3, y0 + r * ch + 3, x0 + (c + 1) * cw - 3, y0 + (r + 1) * ch - 3


def _scr(cv, x0, y0, x1, y1, lvl):
    """Fons d'una pantalla, amb línies d'escaneig."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, SCREENB, lvl - (0.5 if y % 2 else 0), lit=0)


def _fig(cv, x, y, col=(10, 30, 36)):
    """Una silueta petita (3×10, amb cap) en una pantalla."""
    cv.rect(x - 1, y - 7, x + 1, y - 3, [col], 0, lit=0)
    cv.flat(x - 1, y - 2, col)
    cv.flat(x - 1, y - 1, col)
    cv.flat(x + 1, y - 2, col)
    cv.flat(x + 1, y, col)
    cv.flat(x - 1, y, col)
    cv.rect(x - 1, y - 9, x, y - 8, [col], 0, lit=0)


def view(cv, i, kind, t=0):
    """Una pantalla: `kind` = vestibul, moll, passadis, caixes, buida, escala, neu, senyal, ascensor."""
    x0, y0, x1, y1 = _cell(i)
    if kind == 'neu':
        for y in range(y0, y1 + 1):
            roll = (y - y0 - t * 5) % (y1 - y0 + 1) < 3                      # la franja que corre
            for x in range(x0, x1 + 1):
                cv.put(x, y, SCREENB, 1.5 + hr(x, y, t, 9) * 4.5 + (0.8 if roll else 0), lit=0)
        return
    _scr(cv, x0, y0, x1, y1, 2.0)
    mx, my = (x0 + x1) // 2, (y0 + y1) // 2
    dark, mid, light = SCREENB[1], SCREENB[3], SCREENB[5]
    if kind == 'vestibul':
        # el terra de marbre en perspectiva, l'ascensor, el retrat i el Director (o algú) al mig
        for y in range(my, y1 + 1):
            for x in range(x0, x1 + 1):
                cv.put(x, y, SCREENB, 3.2 + ((x + y) % 8 == 0) * 0.8 + ((x - y) % 8 == 0) * 0.5, lit=0)
        cv.rect(x1 - 11, y0 + 4, x1 - 4, my, [light], 0, lit=0)
        cv.vline(x1 - 7, y0 + 5, my, [mid], 0, lit=0)
        cv.rect(x0 + 5, y0 + 5, x0 + 13, y0 + 13, [mid], 0, lit=0)        # el retrat
        cv.rect(x0 + 7, y0 + 7, x0 + 11, y0 + 11, [dark], 0, lit=0)
        cv.rect(mx - 6, my - 2, mx + 6, my, [mid], 0, lit=0)                # el taulell de recepció
        _fig(cv, mx - 3 + (t % 4), y1 - 3)
    elif kind == 'moll':
        cv.rect(x0, my + 3, x1, y1, [mid], 0, lit=0)
        for k in range(2):                                              # dues furgonetes
            fx = x0 + 4 + k * 21
            cv.rect(fx, my - 5, fx + 16, my + 5, [light], 0, lit=0)
            cv.rect(fx + 12, my - 3, fx + 15, my, [dark], 0, lit=0)
            cv.hline(fx, fx + 16, my + 1, [mid], 0, lit=0)
            for wx in (fx + 3, fx + 13):
                cv.rect(wx - 1, my + 5, wx + 1, my + 6, [dark], 0, lit=0)
        _fig(cv, x1 - 8 - (t % 4 == 3), y1 - 2)
    elif kind == 'passadis':
        # un passadís en fuga, amb portes als costats
        for y in range(y0, y1 + 1):
            d = abs(y - my) / max(1, (y1 - y0) / 2)
            for x in range(x0, x1 + 1):
                if abs(x - mx) < 4 + d * (x1 - x0) / 2.2:
                    cv.put(x, y, SCREENB, 3.0 + (1.2 if y > my else 0), lit=0)
        cv.rect(mx - 3, my - 4, mx + 3, my + 4, [dark], 0, lit=0)
        cv.rect(x0 + 5, y0 + 5, x0 + 9, y1 - 5, [dark], 0, lit=0)
        cv.rect(x1 - 8, y0 + 7, x1 - 6, y1 - 7, [dark], 0, lit=0)
        for k in range(3):                                              # els llums del sostre
            cv.flat(mx - 1 + k, y0 + 2 + k * 2, light)
    elif kind == 'caixes':
        cv.disc(mx, my, 12, 12, SCREENB, lambda nx, ny: 4.0 - (nx + ny) * 0.6, lit=0)
        cv.ring(mx, my, 8, SCREENB, 1.5, lit=0, step=8)
        cv.ring(mx, my, 11, SCREENB, 2.2, lit=0, step=6)
        for a in range(0, 360, 60):
            cv.line(mx, my, mx + round(math.cos(math.radians(a + t * 20)) * 7), my + round(math.sin(math.radians(a + t * 20)) * 7), [dark], 0, lit=0)
        cv.disc(mx, my, 1.5, 1.5, [dark], 0, lit=0)
        _fig(cv, x0 + 7, y1 - 2)
        _fig(cv, x0 + 12, y1 - 2)
    elif kind == 'buida':
        cv.rect(x0, my + 5, x1, y1, [mid], 0, lit=0)
        cv.rect(mx - 8, my - 3, mx + 8, my + 1, [dark], 0, lit=0)          # una taula buida
        cv.vline(mx - 7, my + 2, my + 6, [dark], 0, lit=0)
        cv.vline(mx + 7, my + 2, my + 6, [dark], 0, lit=0)
        cv.rect(mx + 11, my - 1, mx + 13, my + 6, [dark], 0, lit=0)        # una cadira
    elif kind == 'escala':
        for k in range(7):
            cv.rect(x0 + 4 + k * 6, y1 - 4 - k * 3, x1, y1 - 3 - k * 3, [mid], 0, lit=0)
        cv.line(x0 + 4, y1 - 9, x0 + 40, y1 - 27, [light], 0, lit=0)       # la barana
    elif kind == 'senyal':
        _scr(cv, x0, y0, x1, y1, 1.0)
        for k, word in enumerate(('SENSE', 'SENYAL')):
            text(cv, word, mx - text_width(word) // 2, my - 7 + k * 8, [light], 0, lit=0, flat=light)
    elif kind == 'ascensor':
        cv.rect(mx - 11, y0 + 4, mx + 11, y1, [mid], 0, lit=0)
        cv.vline(mx, y0 + 4, y1, [dark], 0, lit=0)
        cv.rect(mx - 4, y0 + 1, mx + 4, y0 + 2, [light], 0, lit=0)
    # la data i l'hora a la cantonada, i el punt vermell de gravació (que parpelleja)
    cv.rect(x0 + 1, y0 + 1, x0 + 8, y0 + 1, [light], 0, lit=0)
    cv.rect(x0 + 1, y1 - 1, x0 + 4, y1 - 1, [light], 0, lit=0)
    if (i + t) % 3:
        cv.flat(x1 - 2, y0 + 2, LEDR)
        cv.flat(x1 - 3, y0 + 2, LEDR)


VIEWS = ['vestibul', 'moll', 'passadis', 'caixes', 'buida',
         'passadis', 'senyal', 'escala', 'ascensor', 'passadis',
         'caixes', 'buida', 'moll', 'neu', 'vestibul']


def _glass(cv, a, b, c, d):
    """El reflex del vidre i la corba del tub de raigs catòdics."""
    cv.tint(a, b, c, d, (200, 255, 250), lambda x, y: 0.10 if x + y < a + b + 8 else 0)
    cv.darken(a, b, c, d, lambda x, y: 0.5 if (x in (a, c) or y in (b, d)) else 0)


def monitors(cv, t=0, views=None):
    """La paret de monitors: un bastidor negre amb quinze pantalles i la seva claror."""
    x0, y0, x1, y1 = MON
    obox(cv, x0 - 4, y0 - 4, x1 + 4, y1 + 4, CONSOLE, 1.4)
    cv.hline(x0 - 3, x1 + 3, y0 - 3, CONSOLE, 2.6)
    for i, kind in enumerate(views or VIEWS):
        a, b, c, d = _cell(i)
        outline(cv, a - 1, b - 1, c + 1, d + 1, CONSOLE)
        cv.hline(a - 1, c + 1, d + 2, CONSOLE, 3.0)
        view(cv, i, kind, t)
        _glass(cv, a, b, c, d)
        cv.flat(c - 1, d + 2, (60, 220, 120))                            # el llum de posada en marxa
    for sx in (x0 + 12, x1 - 12):                                        # els cargols del bastidor
        for sy in (y0 - 2, y1 + 2):
            cv.flat(sx, sy, CONSOLE[5])
    # el rètol de la casa, damunt
    obox(cv, 285, y0 - 19, 341, y0 - 7, NAVYB, 2.0)
    cv.hline(286, 340, y0 - 18, NAVYB, 3.0)
    logo(cv, 293, y0 - 13, k=0.8, lvl=3.6)
    text(cv, 'BCMU', 303, y0 - 16, BRASS, 4.6)
    # els cables que pugen al sostre
    for cx, ramp in ((190, PLASTICR), (196, PLASTICR), (436, PLASTICR)):
        cv.vline(cx, 11, y0 - 5, ramp, 1.6)


# ─── El que hi ha a la paret ───────────────────────────────────────────────

def calendar(cv):
    """Un calendari de 1994 amb una foto de muntanya: ningú no l'ha canviat mai."""
    x0, y0, x1, y1 = 467, 29, 499, 84
    obox(cv, x0, y0, x1, y1, SHEET, 4.0)
    for y in range(y0 + 2, y0 + 21):
        for x in range(x0 + 2, x1 - 1):
            cv.put(x, y, GLASSB, 2.4 + (y - y0) * 0.09)
    cv.poly([(x0 + 2, y0 + 20), (x0 + 11, y0 + 8), (x0 + 18, y0 + 14), (x0 + 23, y0 + 9), (x1 - 2, y0 + 20)],
            [(220, 230, 236), (240, 246, 250)], 1)
    cv.poly([(x0 + 2, y0 + 20), (x0 + 11, y0 + 8), (x0 + 13, y0 + 20)], [(150, 160, 170), (190, 200, 206)], 1)   # la cara a l'ombra
    text(cv, '1994', x0 + (x1 - x0 - text_width('1994')) // 2 + 1, y0 + 23, RED, 2.6)
    text(cv, 'GENER', x0 + (x1 - x0 - text_width('GENER')) // 2 + 1, y0 + 32, [(60, 60, 70)], 0, flat=(70, 70, 80))
    for j in range(4):
        for i in range(7):
            cv.flat(x0 + 4 + i * 4, y0 + 42 + j * 3, (200, 40, 40) if i == 6 else (60, 60, 70))
    cv.hline(x0 + 1, x1 - 1, y0 + 21, SHEET, 2.6)
    cv.disc(x0 + 16, y0, 1.6, 1.6, CHROME, 3.0)
    cv.darken(x0 + 2, y1 + 1, x1 + 2, y1 + 2, 0.4)
    cv.darken(x1 + 1, y0 + 2, x1 + 2, y1, 0.4)


def radio(cv, led=True):
    """La ràdio d'en Ballester al seu suport: aparell negre, antena, el cable rinxolat i el llum."""
    x0, y0, x1, y1 = 523, 123, 541, 149
    obox(cv, x0 - 4, y1 - 1, x1 + 4, y1 + 3, CHROME, 2.6)                # el suport
    cv.hline(x0 - 3, x1 + 3, y1 - 1, CHROME, 3.6)
    cv.line(x0 - 3, y1 + 3, x0 - 3, y1 + 11, CHROME, 2.0)
    cv.line(x1 + 3, y1 + 3, x1 + 3, y1 + 11, CHROME, 2.0)
    obox(cv, x0 + 1, y0 + 5, x1 - 1, y1 - 1, PLASTICR, 1.6)
    cv.vline(x0 + 2, y0 + 6, y1 - 2, PLASTICR, 3.0)
    for k in range(5):                                                   # la reixeta de l'altaveu
        cv.hline(x0 + 5, x1 - 5, y0 + 9 + k * 2, PLASTICR, 0.4)
    cv.rect(x0 + 4, y1 - 8, x1 - 4, y1 - 5, [(40, 90, 70)], 0, lit=0)     # la pantalleta
    cv.hline(x0 + 5, x0 + 8, y1 - 7, [(110, 200, 150)], 0, lit=0)
    cv.rect(x0 + 6, y0 + 1, x0 + 8, y0 + 4, PLASTICR, 2.2)               # el comandament
    cv.vline(x1 - 4, y0 - 11, y0 + 4, PLASTICR, 1.4)                      # l'antena
    cv.vline(x1 - 3, y0 - 9, y0 + 4, PLASTICR, 2.6)
    cv.disc(x1 - 4, y0 - 12, 1.4, 1.4, PLASTICR, 2.0)
    cv.flat(x0 + 4, y0 + 7, LEDR if led else (90, 20, 20))
    cv.flat(x0 + 5, y0 + 7, LEDR if led else (70, 20, 20))
    if led:
        cv.glow(x0 + 4, y0 + 7, 7, LEDR, 0.5)
    # el cable rinxolat fins a la taula
    for k in range(14):
        cv.put(x0 + 1 - k // 3 + (1 if k % 3 == 1 else 0), y1 + 2 + k, PLASTICR, 1.8 + (k % 2))


# ─── La taula de control ───────────────────────────────────────────────────

def desk(cv):
    """La consola: tauler fosc de laminat, frontal amb ventilació, teclats, micròfon i llums."""
    x0, x1 = DESK
    # el tauler (vist una mica de dalt)
    cv.rect(x0, DESK_TOP - 5, x1, DESK_TOP, CONSOLE, lambda x, y: 3.4 + (0.8 if y == DESK_TOP - 5 else 0) + (hr(x // 6, y, 11) - 0.5) * 0.2)
    cv.hline(x0, x1, DESK_TOP + 1, CONSOLE, 5.2)
    cv.hline(x0, x1, DESK_TOP + 2, CONSOLE, 3.6)
    # la claror dels monitors damunt el tauler i el cantell
    cv.tint(x0, DESK_TOP - 5, x1, DESK_TOP + 2, (90, 200, 210), lambda x, y: 0.22 * max(0, 1 - abs(x - 313) / 187))
    # el frontal
    obox(cv, x0, DESK_TOP + 3, x1, FLOOR_Y + 3, CONSOLE, 2.2, top=1.4)
    for px in range(x0 + 13, x1 - 13, 69):                               # panells amb reixetes
        obox(cv, px, DESK_TOP + 11, px + 53, FLOOR_Y - 5, CONSOLE, 1.8)
        for k in range(7):
            cv.hline(px + 8, px + 45, DESK_TOP + 16 + k * 3, CONSOLE, 0.8)
            cv.hline(px + 8, px + 45, DESK_TOP + 17 + k * 3, CONSOLE, 2.4)
        for sx in (px + 2, px + 51):
            cv.flat(sx, DESK_TOP + 13, CONSOLE[5])
    cv.darken(x0 - 3, FLOOR_Y + 4, x1 + 5, FLOOR_Y + 8, 0.5)
    # els teclats i el micròfon
    for kx in (213, 360):
        obox(cv, kx, DESK_TOP - 7, kx + 40, DESK_TOP - 2, CONSOLE, 3.2)
        for j in range(2):
            for i in range(11):
                cv.flat(kx + 3 + i * 3 + j, DESK_TOP - 5 + j, (130, 140, 154) if j == 0 else (110, 118, 130))
        cv.hline(kx + 12, kx + 28, DESK_TOP - 3, CONSOLE, 5.6)            # la barra d'espai
    cv.line(427, DESK_TOP - 2, 432, DESK_TOP - 19, CHROME, 2.6)          # el micròfon de peu
    cv.line(428, DESK_TOP - 2, 433, DESK_TOP - 19, CHROME, 1.4)
    cv.disc(433, DESK_TOP - 21, 2.4, 3.2, PLASTICR, lambda nx, ny: 2.6 - nx)
    obox(cv, 421, DESK_TOP - 4, 437, DESK_TOP - 1, CHROME, 2.4)
    cv.flat(435, DESK_TOP - 3, (60, 220, 120))
    # botons i llums de la consola
    for i in range(10):
        bx = 261 + i * 8
        col = [(60, 220, 120), (240, 190, 60), (240, 70, 60)][int(hr(i, 2) * 3)]
        cv.flat(bx, DESK_TOP - 2, col)
        cv.flat(bx + 1, DESK_TOP - 2, col)
        cv.flat(bx, DESK_TOP - 3, (20, 22, 28))


def mug(cv):
    """La tassa d'en Ballester: «MILLOR AVI», amb una cullereta."""
    x0, y0 = 376, DESK_TOP - 16
    obox(cv, x0, y0, x0 + 11, y0 + 12, SHEET, 4.2)
    cv.vline(x0 + 1, y0 + 1, y0 + 11, SHEET, 5.0)
    cv.ring(x0 + 13, y0 + 5, 3.2, SHEET, 3.6, step=15)
    cv.hline(x0 + 1, x0 + 10, y0 + 1, [(60, 36, 20)], 0)                  # el cafè fred
    cv.hline(x0 + 2, x0 + 8, y0 + 5, RED, 2.6)
    cv.hline(x0 + 3, x0 + 7, y0 + 7, RED, 2.2)
    cv.line(x0 + 7, y0 - 5, x0 + 8, y0 + 1, CHROME, 4.0)


def photo(cv):
    """Una foto de família en un marc daurat, mig girada cap a la paret."""
    pts = [(395, DESK_TOP - 21), (408, DESK_TOP - 19), (408, DESK_TOP - 3), (395, DESK_TOP - 4)]
    cv.poly(pts, BRASS, 3.2)
    outline_poly(cv, pts, BRASS)
    cv.rect(397, DESK_TOP - 17, 405, DESK_TOP - 7, GLASSB, 2.4)
    for fx, fy in ((399, 12), (401, 11), (403, 12)):
        cv.disc(fx, DESK_TOP - fy, 1, 1, [(220, 180, 150)], 0, lit=0)
        cv.flat(fx, DESK_TOP - fy + 2, (80, 90, 120))
    cv.line(408, DESK_TOP - 8, 412, DESK_TOP - 1, BRASS, 2.0)            # el peu


def dead_plant(cv):
    """Una planta morta en un test, a la punta de la taula. Ningú no la rega des de la reestructuració."""
    x0 = 453
    pot = [(x0, DESK_TOP - 13), (x0 + 19, DESK_TOP - 13), (x0 + 16, DESK_TOP - 1), (x0 + 3, DESK_TOP - 1)]
    cv.poly(pot, POT, lambda x, y: 2.8 + (0.6 if x < x0 + 5 else 0) - (0.6 if x > x0 + 14 else 0))
    outline_poly(cv, pot, POT)
    cv.rect(x0 - 1, DESK_TOP - 14, x0 + 20, DESK_TOP - 12, POT, lambda x, y: 3.6 if y == DESK_TOP - 14 else 2.6)
    cv.hline(x0 + 1, x0 + 18, DESK_TOP - 15, [(30, 22, 14), (50, 38, 24)], 0.6)   # la terra seca, esquerdada
    for k, (dx, dy, ex, ey) in enumerate(((9, -13, 3, -29), (9, -13, 13, -35), (9, -13, 21, -24), (9, -13, 8, -21))):
        cv.line(x0 + dx, DESK_TOP + dy, x0 + ex, DESK_TOP + ey, LEAF, 2.2 + k * 0.2)
    for (lx, ly) in ((3, -29), (21, -24), (13, -35), (8, -21)):           # fulles penjant
        cv.line(x0 + lx, DESK_TOP + ly, x0 + lx + 3, DESK_TOP + ly + 7, LEAF, 3.0)
        cv.put(x0 + lx + 1, DESK_TOP + ly + 3, LEAF, 4.0)
    cv.put(x0 + 24, DESK_TOP - 1, LEAF, 2.6)                             # unes fulles caigudes
    cv.put(x0 + 25, DESK_TOP - 1, LEAF, 3.2)
    cv.put(x0 - 4, DESK_TOP - 1, LEAF, 2.4)


def glass(cv):
    """El got d'aigua, a la vora de la taula."""
    x0, y0, x1, y1 = 233, 141, 244, DESK_TOP - 1
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            edge = x in (x0, x1)
            water = y > y0 + 4
            cv.put(x, y, WATER, (3.8 if edge else (2.6 if water else 1.6)) + (1.2 if x == x0 + 2 else 0) - (0.5 if x == x1 - 1 else 0), lit=0)
    cv.hline(x0 + 1, x1 - 1, y0 + 5, WATER, 4.4, lit=0)
    cv.hline(x0, x1, y0, WATER, 4.0, lit=0)
    cv.hline(x0, x1, y1, WATER, 3.2, lit=0)
    cv.hline(x0 + 1, x1 - 1, y1 - 1, WATER, 3.6, lit=0)
    cv.glow(x0 + 3, y0 + 4, 5, (220, 250, 255), 0.4)


def chair(cv):
    """La cadira giratòria d'en Ballester, de cara a la taula, amb el coixí aixafat per trenta anys."""
    cx = 400
    # el respatller (de darrere)
    cv.rect(cx - 17, 171, cx + 17, 208, PLASTICR, lambda x, y: 3.0 + (0.8 if x < cx - 12 else 0) - (0.8 if x > cx + 12 else 0))
    outline(cv, cx - 17, 171, cx + 17, 208, PLASTICR)
    cv.rect(cx - 13, 175, cx + 13, 203, PLASTICR, lambda x, y: 2.2 + (hr(x // 2, y // 2, 12) - 0.5) * 0.4)
    cv.hline(cx - 16, cx + 16, 172, PLASTICR, 4.2)
    cv.tint(cx - 16, 172, cx + 16, 176, (90, 200, 210), 0.12)              # la claror dels monitors al cantell
    # el seient, els braços i la columna
    cv.rect(cx - 21, 209, cx + 21, 215, PLASTICR, lambda x, y: 3.8 if y == 209 else 3.2)
    outline(cv, cx - 21, 209, cx + 21, 215, PLASTICR)
    for ax in (cx - 24, cx + 20):
        cv.rect(ax, 195, ax + 4, 208, PLASTICR, 2.6)
        cv.hline(ax, ax + 4, 195, PLASTICR, 3.6)
    cv.rect(cx - 2, 216, cx + 1, 229, CHROME, lambda x, y: 3.4 if x == cx - 1 else 2.4)
    cv.rect(cx - 3, 220, cx + 2, 222, CHROME, 2.0)                        # la palanca d'alçada
    for dx in (-19, -8, 8, 19):                                          # la creueta amb rodes
        cv.line(cx, 229, cx + dx, 233, CHROME, 2.2)
        cv.disc(cx + dx, 235, 2.2, 1.8, PLASTICR, 2.0)
    cv.darken(cx - 27, 235, cx + 27, 240, 0.5)


def bg(cv, got=True):
    wall(cv)
    floor(cv)
    tub_station(cv, 32, 85, 59, 144)
    lift(cv)
    monitors(cv)
    calendar(cv)
    radio(cv)
    desk(cv)
    if got:
        glass(cv)
    mug(cv)
    photo(cv)
    dead_plant(cv)
    chair(cv)


# ─── Props ──────────────────────────────────────────────────────────────────

_BASE = {}


def _base():
    if 'img' not in _BASE:
        cv = Canvas(light=LIGHT)
        bg(cv)
        _BASE['img'] = cv.img
    return _BASE['img']


def entrepa(cv):
    """L'entrepà d'en Ballester, embolicat amb paper d'alumini arrugat, amb un mos de pa que en surt."""
    x0, y0, x1, y1 = 263, 148, 287, DESK_TOP - 1
    pts = [(x0, y1), (x0 + 2, y0 + 1), (x1 - 4, y0), (x1, y1)]
    cv.poly(pts, FOIL, lambda x, y: 3.2 + (hr(x // 2, y, 4) - 0.5) * 1.6 + (hr(x, y, 5) - 0.5) * 0.6 - (y - y0) * 0.12)
    outline_poly(cv, pts, FOIL)
    for k in range(3):                                                   # els plecs de l'alumini
        fx = x0 + 5 + k * 6
        cv.line(fx, y0 + 2, fx + 2, y1 - 1, FOIL, 4.6 if k % 2 else 1.8)
    cv.rect(x1 - 6, y0 + 1, x1 - 1, y0 + 4, CARD, 4.6)                   # el pa, per un cantó
    cv.hline(x1 - 6, x1 - 1, y0 + 1, CARD, 3.4)
    cv.hline(x1 - 5, x1 - 2, y0 + 4, [(200, 120, 130)], 0)               # la mortadel·la
    cv.flat(x1 - 3, y0 + 5, (200, 120, 130))
    cv.darken(x0, y1 + 1, x1 + 1, y1 + 1, 0.5)


def clauer(cv):
    """El clauer «Visiteu Ginebra»: una anella i una xapa amb la bandera suïssa (sense cap clau)."""
    cv.ring(305, 152, 3.2, CHROME, 4.2, step=10)
    cv.flat(303, 150, CHROME[-1])
    obox(cv, 308, 149, 318, DESK_TOP - 1, RED, 3.4)
    cv.hline(309, 317, 150, RED, 4.6)
    cv.rect(312, 151, 314, 155, [(250, 250, 250)], 0, lit=0)
    cv.rect(311, 152, 315, 154, [(250, 250, 250)], 0, lit=0)
    cv.darken(305, DESK_TOP, 319, DESK_TOP, 0.4)


def _collaret(cv):
    """El collaret d'en Ballester: cadena de llautó i una clau grossa i antiga."""
    for k in range(26):                                                  # la cadena, enrotllada, a baules
        a = k / 26 * 2 * math.pi
        cv.put(344 + round(math.cos(a) * 7), 152 + round(math.sin(a) * 3), BRASS, 4.0 + (k % 2) * 1.2)
    cv.disc(353, 151, 3, 3, BRASS, lambda nx, ny: 4.2 - ny)              # l'anella de la clau
    cv.disc(353, 151, 1.2, 1.2, CONSOLE, 2.0)
    cv.rect(356, 151, 357, 152, BRASS, 3.6)
    cv.line(356, 152, 357, 156, BRASS, 3.4)                              # la tija, de biaix
    cv.line(357, 152, 358, 156, BRASS, 4.4)
    cv.rect(355, 155, 357, 156, BRASS, 3.0)                              # les dents
    cv.flat(355, 154, BRASS[2])
    cv.darken(336, DESK_TOP - 1, 359, DESK_TOP - 1, 0.4)


def collaret(cv):
    _collaret(cv)


def collaret_taula(cv):
    _collaret(cv)


def got_trencat(cv):
    """El got, trencat: el que queda del got a la taula, el toll i els vidres per terra."""
    var = Canvas(light=LIGHT)
    bg(var, got=False)
    # el cul del got, de costat, i el toll
    for x in range(227, 256):
        var.put(x, DESK_TOP - 1, WATER, 2.6 + (0.8 if x % 3 == 0 else 0), lit=0.4)
    for x in range(231, 250):
        var.put(x, DESK_TOP - 2, WATER, 2.2 + (0.8 if x % 4 == 0 else 0), lit=0.4)
    var.rect(235, DESK_TOP - 4, 241, DESK_TOP - 1, WATER, 3.4, lit=0)
    var.hline(235, 241, DESK_TOP - 5, WATER, 4.2, lit=0)
    var.flat(237, DESK_TOP - 5, (230, 250, 252))
    # l'aigua que regalima pel frontal
    for k in range(14):
        var.put(245, DESK_TOP + 3 + k, WATER, 2.4 + (0.6 if k % 4 == 0 else 0), lit=0.3)
    var.put(245, DESK_TOP + 18, WATER, 3.6, lit=0.3)                     # la gota que cau
    for x in range(240, 251):                                            # el bassal a terra
        var.put(x, FLOOR_Y + 9 + (x % 2), WATER, 1.8, lit=0.3)
    # els vidres per terra
    for i in range(18):
        gx = 224 + int(hr(i, 6) * 43)
        gy = 205 + int(hr(i, 7) * 11)
        var.flat(gx, gy, (200, 236, 240) if i % 2 else (120, 170, 180))
        if i % 3 == 0:
            var.flat(gx + 1, gy, (230, 250, 252))
        if i % 4 == 1:
            var.flat(gx, gy - 1, (160, 210, 220))
    cv.img.alpha_composite(_diff(var.img, _base()))


PROPS = {'entrepa': entrepa, 'clauer': clauer, 'collaret': collaret, 'got_trencat': got_trencat, 'collaret_taula': collaret_taula}


# ─── Animació: els monitors canvien de pla, i un fa neu ────────────────────

def _frames():
    base = _base()
    frames = []
    for t in range(8):
        cv = Canvas(light=LIGHT, img=base.copy())
        views = list(VIEWS)
        views[13] = 'neu'
        if t >= 4:                                                       # canvien de càmera
            views[2], views[9] = 'escala', 'buida'
            views[11] = 'passadis'
        if t in (3, 7):
            views[6] = 'neu'
        # només redibuixem les pantalles (el bastidor és el mateix)
        for i, kind in enumerate(views):
            a, b, c, d = _cell(i)
            view(cv, i, kind, t)
            _glass(cv, a, b, c, d)
        frames.append(_diff(cv.img, base))
    return frames


ANIMS = {'monitors': {'frames': _frames, 'frameDuration': 260}}


GEOMETRIA = {
    'things': {
        'tub': {'rect': (32, 85, 63, 144), 'walk': (48, 248)},
        'ascensor': {'rect': (75, 53, 144, 200), 'walk': (112, 248)},
        'monitors': {'rect': (173, 24, 453, 123), 'walk': (315, 248)},
        'got': {'rect': (232, 141, 246, 157), 'walk': (240, 251)},
        'entrepa': {'rect': (261, 147, 289, 157), 'walk': (275, 251)},
        'clauer': {'rect': (301, 147, 319, 157), 'walk': (309, 251)},
        'collaret': {'rect': (336, 147, 359, 157), 'walk': (347, 251)},
        'radio': {'rect': (519, 111, 545, 152), 'walk': (528, 251)},
    },
    'spawns': {'vet': (200, 261), 'ballester': (496, 248)},
    'walkable': [(19, 236), (621, 236), (632, 271), (8, 271)],
}
