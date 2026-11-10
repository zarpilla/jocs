"""
La sala de seguretat del BCMU (Escena 6, la Vet amb en Ballester). Art definitiu:
  - una sala de control fosca, sense finestres: plafons acústics blau marí, moqueta de rajoles gastada i un llum
    de sostre que ningú no encén; la llum és la de la paret de monitors (cian) i poca cosa més;
  - la paret de monitors (5×3): el vestíbul de marbre, el moll amb les furgonetes, passadissos, la porta de les
    caixes fortes, una sala buida i senyals de «SENSE SENYAL»; ningú no els mira;
  - la taula de control llarga: teclats, un micròfon, el got d'aigua (a la vora, massa a la vora), la tassa
    «MILLOR AVI», una foto de família girada i una planta morta; i on van l'entrepà, el clauer i el collaret;
  - la ràdio d'en Ballester al seu suport de paret (amb el llum vermell), un calendari de 1994 que ningú no ha
    canviat, la cadira giratòria amb el coixí aixafat, l'estació del tub i l'ascensor.
  Props: `entrepa`, `clauer`, `collaret` (es poden agafar), `got_trencat` i `collaret_taula`.
  Animació: els monitors canvien de pla i fan neu.
"""
import math

from hd.pix import Light, Canvas, W, H, hr
from hd.rooms.comu import obox, outline, text, text_width, _diff, SHEET, CARD, RED, YEL, GRAYC
from hd.rooms.bar_sala import STEELB, SLATE
from hd.rooms.pis_cuina import outline_poly
from hd.rooms.aeroport_terminal import CHROME, YELS
from hd.rooms.bcmu import BRASS, MAHOG, NAVYB, SCREENB, MARBLE, CONCB, GLASSB, tub_station, logo

FLOOR_Y = 150
DESK_TOP = 118          # el tauler de la taula de control
DESK = (146, 364)       # x de la taula

ACOUSTIC = [(6, 8, 16), (10, 14, 26), (16, 20, 36), (24, 30, 50), (34, 42, 66), (46, 56, 84), (62, 74, 104)]
TILEF = [(8, 10, 14), (14, 16, 22), (22, 24, 32), (32, 34, 44), (44, 46, 58), (58, 60, 74), (76, 78, 92)]
CONSOLE = [(8, 10, 14), (16, 18, 24), (26, 30, 38), (38, 42, 52), (52, 58, 70), (70, 78, 92), (94, 102, 118), (124, 132, 146)]
FOIL = [(40, 44, 52), (80, 86, 96), (130, 136, 146), (180, 186, 194), (220, 226, 232), (250, 252, 255)]
LEAF = [(20, 16, 8), (44, 34, 14), (74, 58, 22), (106, 84, 34), (140, 112, 50)]
POT = [(30, 10, 6), (60, 24, 12), (100, 44, 22), (140, 70, 38), (176, 100, 60)]
WATER = [(30, 50, 60), (60, 100, 116), (110, 160, 172), (180, 220, 226), (230, 250, 252)]
LEDR = (240, 40, 36)

LIGHT = Light(ambient=-0.9, vignette=(70, 36), floor_fade=(184, 30))
LIGHT.point(235, 56, r=230, k=3.4, squash=1.25, power=1.4)           # la paret de monitors
LIGHT.point(84, 30, r=60, k=0.6, squash=1.0, power=2.0)              # l'indicador de l'ascensor
LIGHT.point(399, 100, r=30, k=0.5, squash=1.0, power=2.0)            # el llum de la ràdio
LIGHT.point(34, 86, r=40, k=0.5, squash=1.0, power=2.0)              # el llautó del tub

MON = (130, 18, 340, 92)
COLS, ROWS = 5, 3


# ─── Paret, sostre, terra ──────────────────────────────────────────────────

def wall(cv):
    """Plafons acústics blau marí, perforats, amb juntes; un sòcol d'alumini."""
    for y in range(0, FLOOR_Y):
        for x in range(W):
            seam = x % 40 == 0 or y % 50 == 0
            hole = (x % 4 == 2 and y % 4 == 2)
            n = (hr(x // 40, y // 50, 4) - 0.5) * 0.4
            cv.put(x, y, ACOUSTIC, 1.6 if seam else (3.0 + n - (0.6 if hole else 0)))
    # el sostre baix amb el llum apagat i un conducte
    cv.rect(0, 0, W - 1, 7, CONCB, 2.4)
    cv.hline(0, W - 1, 8, CONCB, 1.0)
    obox(cv, 380, 1, 450, 5, CHROME, 1.6)
    cv.rect(384, 3, 446, 3, [(70, 76, 84)], 0, lit=0)
    cv.rect(0, FLOOR_Y - 4, W - 1, FLOOR_Y - 1, CHROME, 1.8)
    cv.hline(0, W - 1, FLOOR_Y, SLATE, 0)


def floor(cv):
    """Rajoles de moqueta grises, gastades davant la taula i el camí de l'ascensor; el reflex dels monitors."""
    for y in range(FLOOR_Y + 1, H):
        for x in range(W):
            tx, ty = (x + (y - FLOOR_Y) // 2) // 24, (y - FLOOR_Y) // 12
            n = (hr(x, y, 3) - 0.5) * 0.6 + (hr(tx, ty, 8) - 0.5) * 0.5
            seam = (x + (y - FLOOR_Y) // 2) % 24 == 0 or (y - FLOOR_Y) % 12 == 0
            worn = max(0, 1 - math.hypot((x - 300) / 60, (y - 168) / 14)) * 0.8 + max(0, 1 - abs(x - 84) / 30) * max(0, 1 - (y - FLOOR_Y) / 26) * 0.6
            cv.put(x, y, TILEF, (2.4 if seam else 3.4 + n) + worn)
    cv.tint(140, 152, 350, 196, (80, 220, 230), lambda x, y: 0.10 * max(0, 1 - abs(x - 240) / 110) * max(0, 1 - (y - 152) / 44))


# ─── L'ascensor i el tub ───────────────────────────────────────────────────

def lift(cv):
    """L'ascensor: marc de llautó (la casa), portes d'acer raspallat i l'indicador de planta."""
    x0, y0, x1, y1 = 56, 40, 108, FLOOR_Y
    obox(cv, x0 - 4, y0 - 4, x1 + 4, y1, BRASS, 2.6)
    for x in range(x0, x1 + 1):
        for y in range(y0, y1):
            cv.put(x, y, STEELB, 3.4 + (hr(x, 7) - 0.5) * 0.5 - (0.8 if x in (x0, x1) else 0))
    cx = (x0 + x1) // 2
    cv.vline(cx, y0, y1 - 1, SLATE, 0.6)
    cv.vline(cx + 1, y0, y1 - 1, STEELB, 5.0)
    outline(cv, x0, y0, x1, y1, SLATE)
    # l'indicador: «-1» en ambre
    obox(cv, cx - 10, y0 - 16, cx + 10, y0 - 6, MAHOG, 1.4)
    text(cv, '-1', cx - text_width('-1') // 2, y0 - 13, [(255, 170, 60)], 0, lit=0, flat=(255, 176, 70))
    cv.glow(cx, y0 - 11, 10, (255, 160, 60), 0.3)
    # el botó
    obox(cv, x1 + 7, 96, x1 + 13, 108, BRASS, 3.2)
    cv.disc(x1 + 10, 102, 1.4, 1.4, [(255, 200, 120)], 0, lit=0)


# ─── La paret de monitors ──────────────────────────────────────────────────

def _cell(i):
    x0, y0, x1, y1 = MON
    cw, ch = (x1 - x0) // COLS, (y1 - y0) // ROWS
    c, r = i % COLS, i // COLS
    return x0 + c * cw + 2, y0 + r * ch + 2, x0 + (c + 1) * cw - 2, y0 + (r + 1) * ch - 2


def _scr(cv, x0, y0, x1, y1, lvl):
    """Fons d'una pantalla, amb línies d'escaneig."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, SCREENB, lvl - (0.5 if y % 2 else 0), lit=0)


def _fig(cv, x, y, col=(10, 30, 36)):
    """Una silueta petita (3×7) en una pantalla."""
    cv.rect(x - 1, y - 6, x + 1, y, [col], 0, lit=0)
    cv.flat(x, y - 7, col)


def view(cv, i, kind, t=0):
    """Una pantalla: `kind` = vestibul, moll, passadis, caixes, buida, escala, neu, senyal, ascensor."""
    x0, y0, x1, y1 = _cell(i)
    if kind == 'neu':
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                cv.put(x, y, SCREENB, 1.5 + hr(x, y, t, 9) * 4.5, lit=0)
        return
    _scr(cv, x0, y0, x1, y1, 2.0)
    mx, my = (x0 + x1) // 2, (y0 + y1) // 2
    dark, mid, light = SCREENB[1], SCREENB[3], SCREENB[5]
    if kind == 'vestibul':
        # el terra de marbre en perspectiva, l'ascensor i el Director (o algú) al mig
        for y in range(my, y1 + 1):
            for x in range(x0, x1 + 1):
                cv.put(x, y, SCREENB, 3.2 + ((x + y) % 6 == 0) * 0.8, lit=0)
        cv.rect(x1 - 8, y0 + 3, x1 - 3, my, [light], 0, lit=0)
        cv.rect(x0 + 4, y0 + 4, x0 + 10, y0 + 10, [mid], 0, lit=0)        # el retrat
        _fig(cv, mx - 2 + (t % 3), y1 - 3)
    elif kind == 'moll':
        cv.rect(x0, my + 2, x1, y1, [mid], 0, lit=0)
        for k in range(2):                                              # dues furgonetes
            fx = x0 + 3 + k * 16
            cv.rect(fx, my - 4, fx + 12, my + 4, [light], 0, lit=0)
            cv.rect(fx + 9, my - 2, fx + 11, my, [dark], 0, lit=0)
        _fig(cv, x1 - 6, y1 - 2)
    elif kind == 'passadis':
        # un passadís en fuga, amb portes als costats
        for y in range(y0, y1 + 1):
            d = abs(y - my) / max(1, (y1 - y0) / 2)
            for x in range(x0, x1 + 1):
                if abs(x - mx) < 3 + d * (x1 - x0) / 2.2:
                    cv.put(x, y, SCREENB, 3.0 + (1.2 if y > my else 0), lit=0)
        cv.rect(mx - 2, my - 3, mx + 2, my + 3, [dark], 0, lit=0)
        cv.rect(x0 + 4, y0 + 4, x0 + 7, y1 - 4, [dark], 0, lit=0)
    elif kind == 'caixes':
        cv.disc(mx, my, 9, 9, SCREENB, lambda nx, ny: 4.0 - (nx + ny) * 0.6, lit=0)
        cv.ring(mx, my, 6, SCREENB, 1.5, lit=0, step=10)
        for a in range(0, 360, 60):
            cv.line(mx, my, mx + round(math.cos(math.radians(a + t * 20)) * 5), my + round(math.sin(math.radians(a + t * 20)) * 5), [dark], 0, lit=0)
        _fig(cv, x0 + 6, y1 - 2)
        _fig(cv, x0 + 10, y1 - 2)
    elif kind == 'buida':
        cv.rect(x0, my + 4, x1, y1, [mid], 0, lit=0)
        cv.rect(mx - 6, my - 2, mx + 6, my + 4, [dark], 0, lit=0)          # una taula buida
    elif kind == 'escala':
        for k in range(6):
            cv.rect(x0 + 3 + k * 5, y1 - 3 - k * 3, x1, y1 - 2 - k * 3, [mid], 0, lit=0)
    elif kind == 'senyal':
        _scr(cv, x0, y0, x1, y1, 1.0)
        for k, word in enumerate(('SENSE', 'SENYAL')):
            text(cv, word, mx - text_width(word) // 2, my - 6 + k * 7, [light], 0, lit=0, flat=light)
    elif kind == 'ascensor':
        cv.rect(mx - 8, y0 + 3, mx + 8, y1, [mid], 0, lit=0)
        cv.vline(mx, y0 + 3, y1, [dark], 0, lit=0)
    # la data i l'hora a la cantonada, i el punt vermell de gravació (que parpelleja)
    cv.rect(x0 + 1, y0 + 1, x0 + 6, y0 + 1, [light], 0, lit=0)
    if (i + t) % 3:
        cv.flat(x1 - 2, y0 + 2, LEDR)


VIEWS = ['vestibul', 'moll', 'passadis', 'caixes', 'buida',
         'passadis', 'senyal', 'escala', 'ascensor', 'passadis',
         'caixes', 'buida', 'moll', 'neu', 'vestibul']


def monitors(cv, t=0, views=None):
    """La paret de monitors: un bastidor negre amb quinze pantalles i la seva claror."""
    x0, y0, x1, y1 = MON
    obox(cv, x0 - 3, y0 - 3, x1 + 3, y1 + 3, CONSOLE, 1.4)
    for i, kind in enumerate(views or VIEWS):
        a, b, c, d = _cell(i)
        outline(cv, a - 1, b - 1, c + 1, d + 1, CONSOLE)
        view(cv, i, kind, t)
        cv.tint(a, b, c, d, (200, 255, 250), lambda x, y: 0.10 if x + y < a + b + 6 else 0)   # el reflex del vidre
    # el rètol de la casa, damunt
    obox(cv, 214, y0 - 14, 256, y0 - 5, NAVYB, 2.0)
    logo(cv, 220, y0 - 10, k=0.6, lvl=3.6)
    text(cv, 'BCMU', 228, y0 - 12, BRASS, 4.6)


# ─── El que hi ha a la paret ───────────────────────────────────────────────

def calendar(cv):
    """Un calendari de 1994 amb una foto de muntanya: ningú no l'ha canviat mai."""
    x0, y0, x1, y1 = 350, 22, 374, 60
    obox(cv, x0, y0, x1, y1, SHEET, 4.0)
    for y in range(y0 + 2, y0 + 16):
        for x in range(x0 + 2, x1 - 1):
            cv.put(x, y, GLASSB, 2.4 + (y - y0) * 0.12)
    cv.poly([(x0 + 2, y0 + 15), (x0 + 9, y0 + 6), (x0 + 14, y0 + 11), (x0 + 18, y0 + 7), (x1 - 2, y0 + 15)], [(220, 230, 236), (240, 246, 250)], 1)
    text(cv, '1994', x0 + (x1 - x0 - text_width('1994')) // 2, y0 + 18, RED, 2.6)
    for j in range(4):
        for i in range(5):
            cv.flat(x0 + 4 + i * 4, y0 + 26 + j * 3, (60, 60, 70))
    cv.disc(x0 + 12, y0, 1.2, 1.2, CHROME, 3.0)


def radio(cv, led=True):
    """La ràdio d'en Ballester al seu suport: aparell negre, antena, el cable rinxolat i el llum."""
    x0, y0, x1, y1 = 392, 92, 406, 112
    obox(cv, x0 - 3, y1 - 1, x1 + 3, y1 + 2, CHROME, 2.6)                # el suport
    cv.line(x0 - 2, y1 + 2, x0 - 2, y1 + 8, CHROME, 2.0)
    obox(cv, x0 + 1, y0 + 4, x1 - 1, y1 - 1, PLASTICR, 1.6)
    for k in range(4):                                                   # la reixeta de l'altaveu
        cv.hline(x0 + 4, x1 - 4, y0 + 7 + k * 2, PLASTICR, 0.4)
    cv.rect(x0 + 3, y1 - 6, x1 - 3, y1 - 4, [(40, 90, 70)], 0, lit=0)     # la pantalleta
    cv.vline(x1 - 3, y0 - 8, y0 + 3, PLASTICR, 1.4)                       # l'antena
    cv.disc(x1 - 3, y0 - 9, 1, 1, PLASTICR, 2.0)
    cv.flat(x0 + 3, y0 + 5, LEDR if led else (90, 20, 20))
    if led:
        cv.glow(x0 + 3, y0 + 5, 5, LEDR, 0.5)
    # el cable rinxolat fins a la taula
    for k in range(10):
        cv.put(x0 + 1 - k // 3, y1 + 1 + k, PLASTICR, 1.8 + (k % 2))


PLASTICR = [(6, 6, 8), (14, 14, 18), (24, 24, 30), (36, 36, 44), (52, 52, 62), (74, 74, 86)]


# ─── La taula de control ───────────────────────────────────────────────────

def desk(cv):
    """La consola: tauler fosc de laminat, frontal amb ventilació, i la cadira giratòria."""
    x0, x1 = DESK
    # el tauler (vist una mica de dalt)
    cv.rect(x0, DESK_TOP - 4, x1, DESK_TOP, CONSOLE, lambda x, y: 3.4 + (0.8 if y == DESK_TOP - 4 else 0))
    cv.hline(x0, x1, DESK_TOP + 1, CONSOLE, 5.2)
    # la claror dels monitors damunt el tauler i el cantell
    cv.tint(x0, DESK_TOP - 4, x1, DESK_TOP + 1, (90, 200, 210), lambda x, y: 0.22 * max(0, 1 - abs(x - 235) / 140))
    # el frontal
    obox(cv, x0, DESK_TOP + 2, x1, FLOOR_Y + 2, CONSOLE, 2.2, top=1.4)
    for px in range(x0 + 10, x1 - 10, 52):                               # panells amb reixetes
        obox(cv, px, DESK_TOP + 8, px + 40, FLOOR_Y - 4, CONSOLE, 1.8)
        for k in range(5):
            cv.hline(px + 6, px + 34, DESK_TOP + 12 + k * 3, CONSOLE, 0.8)
    cv.darken(x0 - 2, FLOOR_Y + 3, x1 + 4, FLOOR_Y + 6, 0.5)
    # els teclats i el micròfon
    for kx in (160, 270):
        obox(cv, kx, DESK_TOP - 5, kx + 30, DESK_TOP - 2, CONSOLE, 3.2)
        for i in range(8):
            cv.flat(kx + 3 + i * 3, DESK_TOP - 4, (130, 140, 154))
            cv.flat(kx + 4 + i * 3, DESK_TOP - 3, (110, 118, 130))
    cv.line(320, DESK_TOP - 2, 324, DESK_TOP - 14, CHROME, 2.6)          # el micròfon de peu
    cv.disc(325, DESK_TOP - 16, 2, 2.4, PLASTICR, 2.6)
    obox(cv, 316, DESK_TOP - 3, 328, DESK_TOP - 1, CHROME, 2.4)
    # botons i llums de la consola
    for i in range(10):
        bx = 196 + i * 6
        col = [(60, 220, 120), (240, 190, 60), (240, 70, 60)][int(hr(i, 2) * 3)]
        cv.flat(bx, DESK_TOP - 2, col)


def mug(cv):
    """La tassa d'en Ballester: «MILLOR AVI», amb una cullereta."""
    x0, y0 = 282, DESK_TOP - 12
    obox(cv, x0, y0, x0 + 8, y0 + 9, SHEET, 4.2)
    cv.ring(x0 + 10, y0 + 4, 2.5, SHEET, 3.6, step=20)
    cv.hline(x0 + 2, x0 + 6, y0 + 4, RED, 2.6)
    cv.line(x0 + 5, y0 - 4, x0 + 6, y0 + 1, CHROME, 4.0)


def photo(cv):
    """Una foto de família en un marc daurat, mig girada cap a la paret."""
    pts = [(296, DESK_TOP - 16), (306, DESK_TOP - 14), (306, DESK_TOP - 2), (296, DESK_TOP - 3)]
    cv.poly(pts, BRASS, 3.2)
    outline_poly(cv, pts, BRASS)
    cv.rect(298, DESK_TOP - 13, 304, DESK_TOP - 5, GLASSB, 2.4)
    for fx in (300, 302):
        cv.disc(fx, DESK_TOP - 9, 1, 1, [(220, 180, 150)], 0, lit=0)
    cv.line(306, DESK_TOP - 6, 309, DESK_TOP - 1, BRASS, 2.0)            # el peu


def dead_plant(cv):
    """Una planta morta en un test, a la punta de la taula. Ningú no la rega des de la reestructuració."""
    x0 = 340
    cv.poly([(x0, DESK_TOP - 10), (x0 + 14, DESK_TOP - 10), (x0 + 12, DESK_TOP - 1), (x0 + 2, DESK_TOP - 1)], POT, 2.8)
    outline_poly(cv, [(x0, DESK_TOP - 10), (x0 + 14, DESK_TOP - 10), (x0 + 12, DESK_TOP - 1), (x0 + 2, DESK_TOP - 1)], POT)
    for k, (dx, dy, ex, ey) in enumerate(((7, -10, 2, -22), (7, -10, 10, -26), (7, -10, 16, -18), (7, -10, 6, -16))):
        cv.line(x0 + dx, DESK_TOP + dy, x0 + ex, DESK_TOP + ey, LEAF, 2.2 + k * 0.2)
    for (lx, ly) in ((2, -22), (16, -18), (10, -26)):                    # fulles penjant
        cv.line(x0 + lx, DESK_TOP + ly, x0 + lx + 2, DESK_TOP + ly + 5, LEAF, 3.0)
    cv.put(x0 + 18, DESK_TOP - 1, LEAF, 2.6)                             # una fulla caiguda


def glass(cv):
    """El got d'aigua, a la vora de la taula."""
    x0, y0, x1, y1 = 175, 106, 183, DESK_TOP - 1
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            edge = x in (x0, x1)
            water = y > y0 + 3
            cv.put(x, y, WATER, (3.8 if edge else (2.6 if water else 1.6)) + (1.2 if x == x0 + 2 else 0), lit=0)
    cv.hline(x0 + 1, x1 - 1, y0 + 4, WATER, 4.4, lit=0)
    cv.hline(x0, x1, y0, WATER, 4.0, lit=0)
    cv.hline(x0, x1, y1, WATER, 3.2, lit=0)
    cv.glow(x0 + 2, y0 + 3, 4, (220, 250, 255), 0.4)


def chair(cv):
    """La cadira giratòria d'en Ballester, de cara a la taula, amb el coixí aixafat per trenta anys."""
    cx = 300
    # el respatller (de darrere)
    cv.rect(cx - 13, 128, cx + 13, 156, PLASTICR, lambda x, y: 3.0 + (0.8 if x < cx - 9 else 0) - (0.8 if x > cx + 9 else 0))
    outline(cv, cx - 13, 128, cx + 13, 156, PLASTICR)
    cv.rect(cx - 10, 131, cx + 10, 152, PLASTICR, 2.2)
    # el seient, els braços i la columna
    cv.rect(cx - 16, 157, cx + 16, 161, PLASTICR, 3.4)
    outline(cv, cx - 16, 157, cx + 16, 161, PLASTICR)
    for ax in (cx - 18, cx + 15):
        cv.rect(ax, 146, ax + 3, 156, PLASTICR, 2.6)
    cv.rect(cx - 1, 162, cx + 1, 172, CHROME, 2.6)
    for dx in (-14, -6, 6, 14):                                          # la creueta amb rodes
        cv.line(cx, 172, cx + dx, 175, CHROME, 2.2)
        cv.disc(cx + dx, 176, 1.6, 1.4, PLASTICR, 2.0)
    cv.darken(cx - 20, 176, cx + 20, 180, 0.5)


def bg(cv, got=True):
    wall(cv)
    floor(cv)
    tub_station(cv, 24, 64, 44, 108)
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
    x0, y0, x1, y1 = 197, 111, 215, DESK_TOP - 1
    pts = [(x0, y1), (x0 + 2, y0 + 1), (x1 - 3, y0), (x1, y1)]
    cv.poly(pts, FOIL, lambda x, y: 3.2 + (hr(x, y, 4) - 0.5) * 1.6 - (y - y0) * 0.15)
    outline_poly(cv, pts, FOIL)
    cv.rect(x1 - 4, y0 + 1, x1 - 1, y0 + 3, CARD, 4.6)                   # el pa, per un cantó
    cv.flat(x1 - 2, y0 + 3, (200, 120, 130))                             # la mortadel·la
    cv.darken(x0, y1 + 1, x1 + 1, y1 + 1, 0.5)


def clauer(cv):
    """El clauer «Visiteu Ginebra»: una anella i una xapa amb la bandera suïssa (sense cap clau)."""
    cv.ring(229, 114, 2.4, CHROME, 4.2, step=15)
    obox(cv, 231, 112, 238, DESK_TOP - 1, RED, 3.4)
    cv.rect(234, 113, 235, 116, [(250, 250, 250)], 0, lit=0)
    cv.rect(233, 114, 236, 115, [(250, 250, 250)], 0, lit=0)


def _collaret(cv):
    """El collaret d'en Ballester: cadena de llautó i una clau grossa i antiga."""
    for k in range(18):                                                  # la cadena, enrotllada
        a = k / 18 * 2 * math.pi
        cv.put(258 + round(math.cos(a) * 5), 114 + round(math.sin(a) * 2.2), BRASS, 4.0 + (k % 2))
    cv.disc(265, 113, 2.2, 2.2, BRASS, lambda nx, ny: 4.2 - ny)           # l'anella de la clau
    cv.flat(265, 113, CONSOLE[2])
    cv.rect(267, 113, 268, 113, BRASS, 3.6)
    cv.line(267, 114, 268, 117, BRASS, 3.4)                              # la tija, de biaix
    cv.rect(266, 116, 268, 117, BRASS, 3.0)                              # les dents
    cv.darken(252, DESK_TOP - 1, 269, DESK_TOP - 1, 0.4)


def collaret(cv):
    _collaret(cv)


def collaret_taula(cv):
    _collaret(cv)


def got_trencat(cv):
    """El got, trencat: el que queda del got a la taula, el toll i els vidres per terra."""
    var = Canvas(light=LIGHT)
    bg(var, got=False)
    # el cul del got, de costat, i el toll
    for x in range(170, 192):
        var.put(x, DESK_TOP - 1, WATER, 2.6 + (0.8 if x % 3 == 0 else 0), lit=0.4)
    var.rect(176, DESK_TOP - 3, 181, DESK_TOP - 1, WATER, 3.4, lit=0)
    var.flat(178, DESK_TOP - 4, (230, 250, 252))
    # l'aigua que regalima pel frontal
    for k in range(10):
        var.put(184, DESK_TOP + 2 + k, WATER, 2.4, lit=0.3)
    # els vidres per terra
    for i in range(12):
        gx = 168 + int(hr(i, 6) * 32)
        gy = 154 + int(hr(i, 7) * 8)
        var.flat(gx, gy, (200, 236, 240) if i % 2 else (120, 170, 180))
        if i % 3 == 0:
            var.flat(gx + 1, gy, (230, 250, 252))
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
            cv.tint(a, b, c, d, (200, 255, 250), lambda x, y, a=a, b=b: 0.10 if x + y < a + b + 6 else 0)
        frames.append(_diff(cv.img, base))
    return frames


ANIMS = {'monitors': {'frames': _frames, 'frameDuration': 260}}
