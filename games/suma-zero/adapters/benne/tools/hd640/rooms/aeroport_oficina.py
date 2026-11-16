"""
L'oficina de facturació de l'aeroport (hd/rooms/aeroport_oficina.py) a 640×360, la composició ×4/3 dibuixada de
nou. Escena 3, l'Iri, a dins de la porta de personal:
  - una oficina petita de rerebotiga: parets de plafó beix, moqueta blava gastada, fluorescents freds i, per una
    finestra amb persianes, l'alba feta ratlles;
  - el terminal de facturació, un monitor vell de fòsfor verd: la llista de tripulació del vol BCMU-07
    (`llista_feta`: hi surten «I. I V., TÈCNIQUES», en groc);
  - la impressora làser del segle passat: `imprimint` (el full a mig sortir i el llum verd) i
    `acreditacions_llestes` (dues acreditacions plastificades a la safata);
  - arxivadors, un rellotge que marca les sis menys vint, un pòster de la companyia i la porta de sortida.
Animacions: `ventilador` (les aspes giren), `persiana` (el corrent gronxa el cordill i les lamel·les de baix) i
`segons` (l'agulla dels segons, amb la pila gastada, prova d'avançar i torna enrere).
"""
import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)

import math

from hd.pix import Light, Canvas, W, H, hr
from hd.rooms.comu import obox, outline, cable, text, text_width, _diff, PLASTIC, SHEET, CARD
from hd.rooms.bar_sala import STEELB, SLATE  # noqa: F401
from hd.rooms.pis_cuina import outline_poly
from hd.rooms.aeroport_terminal import CONC, CHROME, DESK, BLUE, YELS, DAWN  # noqa: F401
from hd.rooms.aeroport_personal import DOOR, REDB, GREENS
from hd.rooms.aeroport_oficina import PANEL, CARPET, BEIGE, PHOS, CABINET

# Art a 2× (1280×720 per a una sala de 640×360): el mateix dibuix, amb les formes, el dither i la llum a la
# resolució real (hd1280/canvas2x.py); el motor el mostra a 1/2 (artScale al .room.json).
ART_SCALE = 2
from hd1280.canvas2x import Canvas2x as Canvas  # noqa: E402,F811
from hd.pix import Canvas as Canvas1x  # noqa: E402,F401  (llenços auxiliars en píxels de sala: figures, textos)

FLOOR_Y = 200
DESK_TOP = 163

LIGHT = Light(ambient=-0.25, vignette=(80, 40), floor_fade=(251, 40))
LIGHT.point(280, -27, r=373, k=2.4, squash=0.8, power=1.3)           # els fluorescents
LIGHT.point(467, 80, r=120, k=0.8, squash=1.2, power=2.0)            # l'alba per la finestra
LIGHT.point(200, 139, r=53, k=0.5, squash=1.0, power=2.0)            # la pantalla

SCREEN = (165, 120, 235, 155)
WINDOW = (440, 29, 517, 107)
CLOCK = (320, 40)
FAN = (435, DESK_TOP - 4 - 24)


# ─── Paret, sostre, terra ──────────────────────────────────────────────────

def wall(cv):
    """Plafons de melamina beix amb juntes i un sòcol de goma."""
    for y in range(0, FLOOR_Y):
        for x in range(W):
            seam = x % 64 == 0
            n = (hr(x // 2, y // 2, 6) - 0.5) * 0.25 + (hr(x, y, 9) - 0.5) * 0.1 + (hr(x // 64, 3) - 0.5) * 0.4
            cv.put(x, y, PANEL, 2.4 if seam else 4.2 + n + (0.4 if x % 64 == 1 else 0))
    # el fals sostre i els fluorescents
    for x in range(W):
        for y in range(0, 8):
            cv.put(x, y, PANEL, 5.6 - y * 0.15 + (0.6 if x % 40 == 0 else 0))
    cv.hline(0, W - 1, 8, PANEL, 1.6)
    for fx in (80, 347):
        obox(cv, fx - 3, 0, fx + 96, 6, CHROME, 3.6)
        cv.rect(fx, 1, fx + 93, 4, [(232, 244, 255)], 0, lit=0)
        for gx in range(fx + 8, fx + 93, 12):                           # la reixeta del difusor
            cv.vline(gx, 1, 4, [(200, 214, 228)], 0, lit=0)
        cv.glow(fx + 47, 4, 35, (220, 236, 255), 0.22)
    # un endoll i l'interruptor
    obox(cv, 516, 168, 524, 176, BEIGE, 4.6)
    cv.rect(518, 171, 518, 173, SLATE, 0.6)
    cv.rect(522, 171, 522, 173, SLATE, 0.6)
    cv.rect(0, FLOOR_Y - 5, W - 1, FLOOR_Y - 1, SLATE, 1.6)
    cv.hline(0, W - 1, FLOOR_Y - 5, SLATE, 2.6)
    cv.hline(0, W - 1, FLOOR_Y, SLATE, 0)


def floor(cv):
    """Moqueta blava de despatx, gastada sota la cadira i al camí de la porta."""
    for y in range(FLOOR_Y + 1, H):
        for x in range(W):
            n = (hr(x, y, 2) - 0.5) * 0.7 + (hr(x // 3, y // 2, 5) - 0.5) * 0.2
            worn = max(0, 1 - math.hypot((x - 213) / 67, (y - 227) / 19)) * 0.9 + max(0, 1 - abs(x - 560) / 53) * max(0, 1 - (y - FLOOR_Y) / 40) * 0.6
            cv.put(x, y, CARPET, 3.2 + n + worn)
    cv.tint(400, 203, 560, 267, (255, 190, 150),
            lambda x, y: 0.12 * max(0, 1 - abs(x - 480) / 80) * max(0, 1 - (y - 203) / 64) * (1 if (y // 4) % 2 else 0.4))


# ─── La finestra, el rellotge, el pòster ───────────────────────────────────

def window(cv, sway=0.0):
    """Una finestra amb persianes venecianes: l'alba, a ratlles. `sway`: el corrent del ventilador (-1..1)."""
    x0, y0, x1, y1 = WINDOW
    obox(cv, x0 - 4, y0 - 4, x1 + 4, y1 + 4, CHROME, 3.6)
    cv.rect(x0 - 6, y1 + 4, x1 + 6, y1 + 6, CHROME, lambda x, y: 4.2 - (y - y1 - 4) * 0.8)   # l'ampit
    obox(cv, x0 - 2, y0 - 3, x1 + 2, y0, BEIGE, 4.0)                     # el calaix de la persiana
    for y in range(y0 + 1, y1 + 1):
        for x in range(x0, x1 + 1):
            p = (y - y0) % 7
            if p < 4:
                tilt = sway * 0.8 * ((y - y0) / (y1 - y0)) ** 2 * (p - 1.5)    # les de baix es gronxen
                cv.put(x, y, BEIGE, 4.6 - (x - x0) * 0.008 + tilt + (0.5 if p == 0 else 0) - (0.6 if p == 3 else 0))   # les lamel·les
            else:
                cv.put(x, y, DAWN, 3.0 + (y - y0) / 19, lit=0)            # el cel, entre lamel·les
    cv.vline(460, y0, y1, BEIGE, 2.4)
    cv.vline(497, y0, y1, BEIGE, 2.4)
    dx = round(sway * 3)
    cv.line(515, y0 + 3, 515 + dx, y1 + 19, SHEET, 3.4)                  # el cordill
    cv.disc(515 + dx, y1 + 20, 2, 2.7, BEIGE, 3.4)
    # la claror a ratlles a la paret de sota
    cv.tint(427, 113, 533, 187, (255, 196, 160), lambda x, y: 0.10 if (y // 4) % 2 else 0.0)


def clock(cv):
    """El rellotge de paret: les sis menys vint."""
    cx, cy = CLOCK
    cv.disc(cx, cy, 13, 13, BEIGE, lambda nx, ny: 5.2 - (nx + ny) * 0.3)
    cv.ring(cx, cy, 13, SLATE, 1.0, step=3)
    cv.ring(cx, cy, 14, CHROME, 3.0, step=3)
    cv.ring(cx, cy, 15, CHROME, 2.0, step=3)
    for m in range(60):
        a = m / 60 * 2 * math.pi
        r = 10 if m % 5 == 0 else 11
        cv.flat(cx + round(math.sin(a) * r), cy - round(math.cos(a) * r), (40, 40, 44) if m % 5 == 0 else (120, 116, 104))
    for m in (0, 15, 30, 45):                                           # les hores grosses
        a = m / 60 * 2 * math.pi
        cv.flat(cx + round(math.sin(a) * 9), cy - round(math.cos(a) * 9), (40, 40, 44))
    # les 5:40: l'agulla petita entre el 5 i el 6, la gran al 8
    ah = (5 + 40 / 60) / 12 * 2 * math.pi
    am = 40 / 60 * 2 * math.pi
    cv.line(cx, cy, cx + round(math.sin(ah) * 7), cy - round(math.cos(ah) * 7), [(20, 20, 24)], 0)
    cv.line(cx, cy, cx + round(math.sin(am) * 10), cy - round(math.cos(am) * 10), [(20, 20, 24)], 0)
    cv.flat(cx, cy, (200, 40, 40))
    cv.flat(cx - 5, cy - 6, (250, 250, 244))                            # el reflex del vidre
    cv.flat(cx - 6, cy - 5, (250, 250, 244))


def poster(cv):
    """El pòster de la companyia: un avió damunt d'un mar massa blau, «VOLA AMB NOSALTRES»."""
    x0, y0, x1, y1 = 349, 29, 416, 101
    obox(cv, x0, y0, x1, y1, SHEET, 4.6)
    for y in range(y0 + 4, y1 - 16):
        for x in range(x0 + 4, x1 - 3):
            sea = y > y1 - 30
            lvl = (2.0 + (y - y1 + 30) / 10 + (0.8 if (x + (y // 2) * 3) % 11 == 0 else 0)) if sea else 2.6 + (y - y0) / 16
            cv.put(x, y, BLUE, lvl)
    cv.disc(395, y0 + 16, 7, 7, YELS, lambda nx, ny: 4.0 - ny * 0.4, lit=0)   # el sol
    plane = [(363, 67), (400, 56), (403, 59), (387, 67), (395, 75), (389, 76), (379, 69), (365, 71)]
    cv.poly(plane, [(240, 244, 250)], 0)
    cv.poly([(366, 61), (369, 61), (372, 66), (368, 67)], [(240, 244, 250)], 0)   # la cua
    for k, word in enumerate(('VOLA AMB', 'NOSALTRES')):
        text(cv, word, (x0 + x1 - text_width(word)) // 2, y1 - 14 + k * 7, BLUE, 1.0)
    for (px, py) in ((x0 + 3, y0 + 3), (x1 - 3, y0 + 3)):
        cv.rect(px, py, px + 1, py + 1, [(60, 60, 64)], 0)
    cv.line(x1 - 1, y1 - 6, x1 - 6, y1 - 1, SHEET, 3.2)                  # una punta que s'aixeca


# ─── Arxivadors, porta ─────────────────────────────────────────────────────

def cabinets(cv):
    """Tres arxivadors grisos, amb carpetes i una planta morta a sobre."""
    for i in range(3):
        x0 = 27 + i * 29
        obox(cv, x0, 93, x0 + 27, FLOOR_Y, CABINET, 3.2, top=0.8)
        for k in range(4):
            yy = 99 + k * 25
            obox(cv, x0 + 3, yy, x0 + 24, yy + 21, CABINET, 3.6, top=0.6)
            cv.rect(x0 + 9, yy + 4, x0 + 17, yy + 5, CHROME, lambda x, y, yy=yy: 4.4 + (0.6 if y == yy + 4 else 0))
            obox(cv, x0 + 10, yy + 9, x0 + 16, yy + 14, CHROME, 3.0)     # el portaetiquetes
            cv.rect(x0 + 11, yy + 10, x0 + 15, yy + 13, SHEET, 4.6)
        cv.disc(x0 + 21, 96, 1.4, 1.4, CHROME, 4.0)                      # el pany
    cv.darken(112, 95, 115, FLOOR_Y - 1, 0.4)
    # una calaixera mig oberta, amb carpetes
    obox(cv, 59, 149, 80, 157, CABINET, 3.0)
    for k in range(5):
        cv.rect(61 + k * 4, 144, 62 + k * 4, 149, [YELS[2], BLUE[3], REDB[2], YELS[3], SHEET[4]][k:k + 1] * 3, 0)
        cv.flat(61 + k * 4, 143, [YELS[3], BLUE[4], REDB[3], YELS[4], SHEET[5]][k])
    # a sobre: carpetes apilades i la planta morta
    for k in range(4):
        cv.rect(32, 88 - k * 4, 53, 91 - k * 4, [BLUE, YELS, REDB, SHEET][k], lambda x, y, k=k: 2.8 + (0.8 if y == 88 - k * 4 else 0))
    obox(cv, 93, 77, 107, 93, CARD, 3.0)
    cv.hline(93, 107, 79, CARD, 4.2)
    for k in range(6):
        cv.line(100, 77, 92 + k * 3, 63 + (k % 2) * 4, [(50, 40, 20), (100, 80, 40), (140, 110, 60)], 1.6)
    for k in range(3):                                                  # les fulles que han caigut
        cv.flat(88 + k * 9, 92 - (k % 2), (120, 96, 50))


def door(cv):
    """La porta de sortida (al passadís de servei), vista des de dins: barra antipànic i finestreta."""
    x0, y0, x1, y1 = 533, 67, 600, FLOOR_Y
    obox(cv, x0 - 5, y0 - 5, x1 + 5, y1, CHROME, 2.8)
    obox(cv, x0, y0, x1, y1, DOOR, 3.6, top=0.6)
    cv.rect(x0 + 19, y0 + 11, x1 - 19, y0 + 40, [(10, 30, 20), (20, 60, 40), (50, 100, 70)],
            lambda x, y: 1.4 + (0.6 if (x - y) % 13 < 2 else 0), lit=0)   # finestreta: el passadís verd
    for k in range(0, 30, 6):                                           # la malla del vidre armat
        cv.hline(x0 + 19, x1 - 19, y0 + 11 + k, [(30, 60, 40)], 0, lit=0)
    outline(cv, x0 + 18, y0 + 10, x1 - 18, y0 + 41, CHROME)
    cv.rect(x0 + 5, 136, x1 - 5, 141, CHROME, lambda x, y: 3.6 + (1.2 if y == 137 else 0))
    obox(cv, x0 + 3, 133, x0 + 8, 144, CHROME, 3.0)
    obox(cv, x1 - 8, 133, x1 - 3, 144, CHROME, 3.0)
    cv.rect(x0 + 1, y1 - 9, x1 - 1, y1 - 1, DOOR, 4.4)                  # la xapa de cops
    obox(cv, 547, 40, 587, 53, GREENS, 2.6, lit=0)                       # sortida
    cv.rect(551, 43, 556, 50, [(240, 255, 240)], 0, lit=0)
    wt = [(240, 255, 240)]
    cv.line(561, 47, 581, 47, wt, 0, lit=0)
    cv.line(577, 44, 581, 47, wt, 0, lit=0)
    cv.line(577, 50, 581, 47, wt, 0, lit=0)
    cv.glow(567, 47, 21, (120, 255, 150), 0.16)
    cv.darken(x1 + 7, y0, x1 + 12, y1, 0.4)


# ─── L'escriptori ──────────────────────────────────────────────────────────

def desk(cv):
    """Un taulell llarg de melamina gris, amb faldó."""
    x0, x1 = 120, 440
    cv.poly([(x0 + 4, DESK_TOP - 8), (x1 - 4, DESK_TOP - 8), (x1 + 3, DESK_TOP), (x0 - 3, DESK_TOP)], BEIGE,
            lambda x, y: 4.4 + (y - DESK_TOP) * 0.06 + (hr(x // 3, y, 22) - 0.5) * 0.2)
    cv.rect(x0 - 3, DESK_TOP, x1 + 3, DESK_TOP + 4, BEIGE, lambda x, y: 3.0 + (0.6 if y == DESK_TOP else 0))
    cv.hline(x0 - 3, x1 + 3, DESK_TOP + 4, BEIGE, 0.6)
    obox(cv, x0, DESK_TOP + 5, x1, FLOOR_Y + 8, CABINET, 2.2, top=0.2)
    obox(cv, x1 - 59, DESK_TOP + 8, x1 - 5, FLOOR_Y + 5, CABINET, 2.8)   # la calaixera
    for k in range(3):
        cv.hline(x1 - 57, x1 - 7, DESK_TOP + 20 + k * 12, CABINET, 1.6)
        cv.rect(x1 - 40, DESK_TOP + 16 + k * 12, x1 - 24, DESK_TOP + 17 + k * 12, CHROME, 4.0)
    cv.darken(x0 - 3, FLOOR_Y + 9, x1 + 5, FLOOR_Y + 14, lambda x, y: 0.65 - (y - FLOOR_Y - 9) * 0.1)


def terminal(cv, llista=False):
    """El monitor de fòsfor verd (caixa beix, groguenca pels anys), el teclat i la torre."""
    x0, y0, x1, y1 = 157, 112, 243, 160
    obox(cv, x0, y0, x1, y1, BEIGE, 3.8, top=1.0)
    cv.rect(x0 + 4, y0 + 4, x1 - 4, y1 - 4, BEIGE, 2.6)
    screen(cv, llista)
    for vx in range(x0 + 6, x0 + 20, 3):                                 # les reixetes de ventilació
        cv.vline(vx, y1 - 3, y1 - 2, BEIGE, 2.0)
    cv.disc(200, DESK_TOP - 4, 16, 2.1, BEIGE, 3.4)                      # el peu
    cv.flat(x1 - 8, y1 - 3, (60, 230, 90))                               # el llum d'engegat
    # un pòsit amb la contrasenya, enganxat al marc (és clar)
    obox(cv, x1 - 3, y0 + 3, x1 + 11, y0 + 16, YELS, 4.0)
    for k in range(2):
        cv.hline(x1, x1 + 8 - k * 3, y0 + 7 + k * 4, [(30, 30, 80)], 0)
    # el teclat
    kb = [(155, DESK_TOP - 3), (248, DESK_TOP - 3), (253, DESK_TOP + 1), (149, DESK_TOP + 1)]
    cv.poly(kb, BEIGE, 3.4)
    outline_poly(cv, kb, BEIGE)
    for i in range(23):
        cv.flat(157 + i * 4, DESK_TOP - 2, (110, 104, 92))
        cv.flat(155 + i * 4, DESK_TOP, (110, 104, 92))
    # la torre, a terra a l'esquerra del faldó
    obox(cv, 128, 171, 149, FLOOR_Y + 5, BEIGE, 3.4)
    cv.rect(132, 176, 145, 178, SLATE, 1.4)
    cv.rect(132, 182, 145, 183, SLATE, 1.8)
    cv.disc(140, 190, 2, 2, BEIGE, 4.6)                                  # el botó
    cv.flat(144, FLOOR_Y, (60, 230, 90))
    cable(cv, [(147, 171), (152, 163), (160, 161)], SLATE, 1.2)


def screen(cv, llista=False):
    """La pantalla: la llista de tripulació del BCMU-07 i, si l'Iri ja hi ha posat mà, les dues «tècniques»."""
    x0, y0, x1, y1 = SCREEN
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            edge = min(x - x0, x1 - x, y - y0, y1 - y)
            cv.put(x, y, PHOS, 1.2 + (0.6 if y % 2 else 0) - (0.5 if edge == 0 else (0.2 if edge == 1 else 0)), lit=0)
    g = (110, 230, 120)
    text(cv, 'BCMU-07', x0 + 4, y0 + 3, PHOS, 0, lit=0, flat=g)
    text(cv, 'GVA', x1 - 4 - text_width('GVA'), y0 + 3, PHOS, 0, lit=0, flat=(80, 190, 90))
    cv.hline(x0 + 4, x1 - 4, y0 + 9, [(50, 140, 60)], 0, lit=0)
    for k, r in enumerate(('1 PILOT', '2 COPILOT')):
        text(cv, r, x0 + 4, y0 + 12 + k * 7, PHOS, 0, lit=0, flat=(80, 190, 90))
    if llista:
        text(cv, '3 I. I V.', x0 + 4, y0 + 26, PHOS, 0, lit=0, flat=(250, 230, 90))
    else:
        cv.hline(x0 + 4, x0 + 7, y0 + 31, [g], 0, lit=0)                  # el cursor
    cv.glow((x0 + x1) // 2, (y0 + y1) // 2, 40, (80, 220, 110), 0.10)


def printer(cv, estat='parada'):
    """La impressora làser, beix i enorme. `estat`: parada, imprimint o llestes (les acreditacions a la safata)."""
    x0, y0, x1, y1 = 341, 131, 408, DESK_TOP - 3
    obox(cv, x0, y0, x1, y1, BEIGE, 4.0, top=1.0)
    cv.rect(x0 + 8, y0 - 5, x1 - 8, y0, BEIGE, 3.2)                         # la safata d'entrada, amb paper
    cv.rect(x0 + 11, y0 - 8, x1 - 11, y0 - 5, SHEET, lambda x, y: 5.0 - (0.6 if y == y0 - 6 else 0))
    cv.rect(x0 + 5, y0 + 11, x1 - 5, y0 + 13, SLATE, 0.8)                   # la boca
    obox(cv, x1 - 19, y0 + 3, x1 - 4, y0 + 9, PLASTIC, 1.6)                 # el panell
    cv.rect(x1 - 17, y0 + 5, x1 - 11, y0 + 7, [(20, 40, 20), (60, 100, 60)], 0.6, lit=0)
    led = {'parada': (200, 120, 40), 'imprimint': (60, 240, 100), 'llestes': (60, 240, 100)}[estat]
    cv.flat(x1 - 7, y0 + 6, led)
    cv.rect(x0 + 3, y1 - 4, x1 - 3, y1 - 3, BEIGE, 2.4)
    cv.rect(x0 + 6, y0 + 4, x0 + 30, y0 + 4, BEIGE, 4.8)                    # el logotip, gastat
    if estat == 'imprimint':
        # el full a mig sortir
        cv.rect(x0 + 13, y0 + 8, x1 - 13, y0 + 13, SHEET, 5.2)
        cv.hline(x0 + 16, x1 - 24, y0 + 10, SLATE, 2.6)
        cv.hline(x0 + 16, x1 - 30, y0 + 12, SLATE, 2.6)
        cv.glow(x1 - 7, y0 + 6, 11, (60, 240, 100), 0.6)
    if estat == 'llestes':
        # dues acreditacions plastificades, damunt la safata de sortida
        for k, (face, hair) in enumerate((((150, 90, 70), (30, 20, 16)), ((110, 80, 66), (120, 60, 30)))):
            ax = x0 + 11 + k * 24
            obox(cv, ax, y0 + 13, ax + 19, y0 + 25, SHEET, 5.0)
            cv.rect(ax + 3, y0 + 16, ax + 7, y0 + 21, [face], 0, lit=0)
            cv.rect(ax + 3, y0 + 16, ax + 7, y0 + 17, [hair], 0, lit=0)
            cv.rect(ax + 9, y0 + 16, ax + 16, y0 + 16, [(40, 70, 160)], 0, lit=0)
            cv.rect(ax + 9, y0 + 19, ax + 15, y0 + 19, SLATE, 1.6)
            cv.rect(ax + 1, y0 + 23, ax + 18, y0 + 24, [(220, 40, 40)], 0, lit=0)
            cv.flat(ax + 2, y0 + 14, (255, 255, 255))                      # el reflex del plàstic
        cv.glow(x1 - 7, y0 + 6, 11, (60, 240, 100), 0.6)
    cable(cv, [(x1, y0 + 19), (x1 + 8, y0 + 29), (x1 + 5, DESK_TOP + 5)], SLATE, 1.2)


def desk_things(cv):
    """Un telèfon, un tampó, etiquetes de maletes, la tassa amb restes de cafè i un ventilador."""
    t = DESK_TOP - 4
    obox(cv, 261, t - 8, 285, t, PLASTIC, 2.0)                             # telèfon
    cv.rect(261, t - 12, 285, t - 9, PLASTIC, lambda x, y: 2.8 + (0.6 if y == t - 12 else 0))
    for k in range(3):
        cv.hline(267 + k * 5, 269 + k * 5, t - 5, PLASTIC, 3.6)
    cable(cv, [(264, t - 8), (256, t + 5), (267, t + 11), (272, t + 3)], PLASTIC, 1.6)
    obox(cv, 293, t - 4, 309, t, REDB, 2.4)                                 # el tampó
    cv.rect(298, t - 9, 303, t - 5, CARD, 3.0)                              # el segell
    cv.rect(315, t - 3, 333, t - 1, [(240, 220, 120)], 0)                   # etiquetes de maleta
    cv.rect(316, t - 5, 332, t - 4, [(250, 250, 250)], 0)
    cv.hline(318, 326, t - 2, [(60, 50, 20)], 0)
    obox(cv, 416, t - 9, 425, t, SHEET, 4.6)                                # la tassa
    cv.hline(417, 424, t - 8, [(70, 40, 20)], 0)
    cv.ring(427, t - 5, 2, SHEET, 4.0, step=30)
    # el ventilador, a la punta del taulell
    fx, fy = FAN
    cv.rect(fx - 1, fy + 8, fx, t, CHROME, 3.0)
    fan_blades(cv, 0)
    cv.disc(fx, t, 7, 1.6, CHROME, 2.6)


def fan_blades(cv, i):
    """Les aspes del ventilador (i: el fotograma; 0 = quietes) i la reixa."""
    fx, fy = FAN
    if i:
        cv.disc(fx, fy, 10, 10, CHROME, lambda nx, ny: 2.4 + (0.8 if math.sin(math.atan2(ny, nx) * 3 + i * 1.1) > 0.4 else 0))
    else:
        cv.disc(fx, fy, 11, 11, CHROME, lambda nx, ny: 2.6 + (0.6 if (nx * 7 + ny * 5) % 2 < 0.3 else 0))
    for a in range(0, 360, 30):                                            # els radis de la reixa
        for r in (4, 7, 9):
            cv.put(fx + round(math.cos(math.radians(a)) * r), fy + round(math.sin(math.radians(a)) * r), CHROME, 4.2)
    cv.ring(fx, fy, 11, CHROME, 4.0, step=4)
    cv.disc(fx, fy, 2, 2, SLATE, 1.6)


def chair(cv):
    """La cadira d'oficina, amb rodes, girada cap a la pantalla."""
    cx = 301
    cv.rect(cx - 1, 187, cx + 1, 213, CHROME, lambda x, y: 3.0 + (0.8 if x == cx - 1 else 0))
    for dx in (-15, -7, 7, 15):
        cv.line(cx, 213, cx + dx, 220, CHROME, 2.6)
        cv.disc(cx + dx, 221, 2, 1.4, SLATE, 1.6)
    back = [(cx - 19, 149), (cx + 13, 149), (cx + 16, 179), (cx - 21, 179)]
    cv.poly(back, BLUE, lambda x, y: 1.8 + (0.6 if y < 154 else 0) + (0.3 if (x * 3 + y) % 4 == 0 else 0))
    outline_poly(cv, back, BLUE)
    cv.rect(cx - 3, 180, cx + 1, 186, CHROME, 2.4)                         # el suport del respatller
    seat = [(cx - 24, 179), (cx + 24, 179), (cx + 27, 189), (cx - 27, 189)]
    cv.poly(seat, BLUE, lambda x, y: 2.6 - (y - 179) * 0.1)
    outline_poly(cv, seat, BLUE)
    cv.darken(cx - 16, 223, cx + 19, 225, 0.55)


def bg(cv, llista=False, impressora='parada', sway=0.0):
    wall(cv)
    floor(cv)
    window(cv, sway)
    clock(cv)
    poster(cv)
    cabinets(cv)
    door(cv)
    desk(cv)
    terminal(cv, llista)
    printer(cv, impressora)
    desk_things(cv)
    chair(cv)


# ─── Props: el que canvia respecte del fons ────────────────────────────────

_BASE = {}


def _base():
    if 'img' not in _BASE:
        cv = Canvas(light=LIGHT)
        bg(cv)
        _BASE['img'] = cv.img
    return _BASE['img']


def _state(cv, **kw):
    var = Canvas(light=LIGHT)
    bg(var, **kw)
    cv.img.alpha_composite(_diff(var.img, _base()))


def llista_feta(cv):
    _state(cv, llista=True)


def imprimint(cv):
    _state(cv, impressora='imprimint')


def acreditacions_llestes(cv):
    _state(cv, impressora='llestes')


PROPS = {'llista_feta': llista_feta, 'imprimint': imprimint, 'acreditacions_llestes': acreditacions_llestes}


# ─── Animació: el ventilador, la persiana i el rellotge ────────────────────

def _frames():
    base = _base()
    frames = []
    for i in range(1, 9):
        cv = Canvas(light=LIGHT, img=base.copy())
        fan_blades(cv, i * math.tau / 1.1 / 8)
        frames.append(_diff(cv.img, base))
    return frames


def _frames_persiana():
    """El corrent del ventilador gronxa una mica el cordill i les lamel·les de baix de la persiana."""
    base = _base()
    frames = []
    for i in range(10):
        cv = Canvas(light=LIGHT)
        bg(cv, sway=math.sin(i * math.tau / 10))
        frames.append(_diff(cv.img, base))
    return frames


def _frames_segons():
    """El rellotge té la pila gastada: l'agulla dels segons prova d'avançar i torna enrere."""
    base = _base()
    cx, cy = CLOCK
    out = []
    for s in (15, 16):
        cv = Canvas(light=LIGHT, img=base.copy())
        a = s / 60 * 2 * math.pi
        cv.line(cx - round(math.sin(a) * 3), cy + round(math.cos(a) * 3), cx + round(math.sin(a) * 11), cy - round(math.cos(a) * 11),
                [(190, 36, 36)], 0, lit=0)
        cv.flat(cx, cy, (200, 40, 40))
        out.append(_diff(cv.img, base))
    return [out[0]] * 4 + [out[1]]


ANIMS = {'ventilador': {'frames': _frames, 'frameDuration': 70},
         'persiana': {'frames': _frames_persiana, 'frameDuration': 180},
         'segons': {'frames': _frames_segons, 'frameDuration': 200}}


# ─── Geometria a 640×360 (room_designs.AEROPORT_OFICINA ×4/3) ──────────────

GEOMETRIA = {
    'things': {
        'terminal': {'rect': (157, 112, 243, 166), 'walk': (200, 251)},
        'impressora': {'rect': (341, 120, 408, 166), 'walk': (373, 251)},
        'porta': {'rect': (533, 67, 600, 214), 'walk': (565, 248)},
    },
    'spawns': {'iri': (267, 259)},
    'walkable': [(19, 236), (621, 236), (632, 271), (8, 271)],
}
