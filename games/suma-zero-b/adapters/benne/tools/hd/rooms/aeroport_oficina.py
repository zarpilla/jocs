"""
L'oficina de facturació de l'aeroport (Escena 3, l'Iri), a dins de la porta de personal. Art definitiu:
  - una oficina petita de rerebotiga: parets de plafó beix, moqueta blava gastada, fluorescents freds i, per una
    finestra amb persianes, l'alba feta ratlles;
  - el terminal de facturació, un monitor vell de fòsfor verd: la llista de tripulació del vol BCMU-07
    (`llista_feta`: hi surten «I. I V., TÈCNIQUES», en groc);
  - la impressora làser del segle passat: `imprimint` (el full a mig sortir i el llum verd) i
    `acreditacions_llestes` (dues acreditacions plastificades a la safata);
  - arxivadors, un rellotge que marca les sis menys vint, un pòster de la companyia i la porta de sortida.
"""
import math

from hd.pix import Light, Canvas, W, H, hr
from hd.rooms.comu import obox, outline, cable, text, text_width, _diff, PLASTIC, SHEET, CARD, RED, YEL, GRAYC
from hd.rooms.bar_sala import STEELB, SLATE
from hd.rooms.pis_cuina import outline_poly
from hd.rooms.aeroport_terminal import CONC, CHROME, DESK, BLUE, YELS, DAWN
from hd.rooms.aeroport_personal import DOOR, REDB, GREENS

FLOOR_Y = 150
DESK_TOP = 122

PANEL = [(20, 18, 16), (36, 32, 28), (54, 50, 44), (74, 70, 62), (98, 92, 82), (124, 118, 104), (150, 144, 128), (176, 170, 154), (200, 196, 182)]
CARPET = [(6, 10, 22), (12, 18, 36), (20, 28, 52), (30, 40, 70), (42, 54, 88), (58, 72, 108)]
BEIGE = [(30, 28, 24), (60, 56, 48), (96, 90, 78), (136, 130, 114), (176, 170, 152), (210, 206, 190), (236, 234, 222)]
PHOS = [(2, 12, 6), (4, 24, 10), (8, 40, 16), (14, 64, 24), (30, 110, 40), (80, 200, 90), (170, 255, 170)]
CABINET = [(16, 20, 26), (30, 36, 44), (48, 56, 66), (70, 80, 92), (96, 106, 118), (128, 138, 150), (166, 174, 184)]

LIGHT = Light(ambient=-0.25, vignette=(60, 30), floor_fade=(188, 30))
LIGHT.point(210, -20, r=280, k=2.4, squash=0.8, power=1.3)           # els fluorescents
LIGHT.point(350, 60, r=90, k=0.8, squash=1.2, power=2.0)             # l'alba per la finestra
LIGHT.point(150, 104, r=40, k=0.5, squash=1.0, power=2.0)            # la pantalla

SCREEN = (124, 90, 176, 116)


# ─── Paret, sostre, terra ──────────────────────────────────────────────────

def wall(cv):
    """Plafons de melamina beix amb juntes i un sòcol de goma."""
    for y in range(0, FLOOR_Y):
        for x in range(W):
            seam = x % 48 == 0
            n = (hr(x // 2, y // 2, 6) - 0.5) * 0.25 + (hr(x // 48, 3) - 0.5) * 0.4
            cv.put(x, y, PANEL, 2.4 if seam else 4.2 + n)
    # el fals sostre i els fluorescents
    for x in range(W):
        for y in range(0, 6):
            cv.put(x, y, PANEL, 5.6 - y * 0.2 + (0.6 if x % 30 == 0 else 0))
    cv.hline(0, W - 1, 6, PANEL, 1.6)
    for fx in (60, 260):
        cv.rect(fx, 1, fx + 70, 3, [(232, 244, 255)], 0, lit=0)
        cv.glow(fx + 35, 3, 26, (220, 236, 255), 0.22)
    cv.rect(0, FLOOR_Y - 4, W - 1, FLOOR_Y - 1, SLATE, 1.6)
    cv.hline(0, W - 1, FLOOR_Y, SLATE, 0)


def floor(cv):
    """Moqueta blava de despatx, gastada sota la cadira i al camí de la porta."""
    for y in range(FLOOR_Y + 1, H):
        for x in range(W):
            n = (hr(x, y, 2) - 0.5) * 0.7
            worn = max(0, 1 - math.hypot((x - 160) / 50, (y - 170) / 14)) * 0.9 + max(0, 1 - abs(x - 420) / 40) * max(0, 1 - (y - FLOOR_Y) / 30) * 0.6
            cv.put(x, y, CARPET, 3.2 + n + worn)
    cv.tint(300, 152, 420, 200, (255, 190, 150), lambda x, y: 0.12 * max(0, 1 - abs(x - 360) / 60) * max(0, 1 - (y - 152) / 48) * (1 if (y // 3) % 2 else 0.4))


# ─── La finestra, el rellotge, el pòster ───────────────────────────────────

def window(cv, sway=0.0):
    """Una finestra amb persianes venecianes: l'alba, a ratlles. `sway`: el corrent del ventilador (-1..1)."""
    x0, y0, x1, y1 = 330, 22, 388, 80
    obox(cv, x0 - 3, y0 - 3, x1 + 3, y1 + 3, CHROME, 3.6)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if (y - y0) % 5 < 3:
                tilt = sway * 0.8 * ((y - y0) / (y1 - y0)) ** 2 * ((y - y0) % 5 - 1)   # les de baix es gronxen
                cv.put(x, y, BEIGE, 4.6 - (x - x0) * 0.01 + tilt)        # les lamel·les
            else:
                cv.put(x, y, DAWN, 3.0 + (y - y0) / 14, lit=0)            # el cel, entre lamel·les
    cv.vline(345, y0, y1, BEIGE, 2.4)
    cv.vline(373, y0, y1, BEIGE, 2.4)
    dx = round(sway * 2)
    cv.line(386, y0 + 2, 386 + dx, y1 + 14, SHEET, 3.4)                  # el cordill
    cv.disc(386 + dx, y1 + 15, 1.4, 2, BEIGE, 3.4)
    # la claror a ratlles a la paret de sota
    cv.tint(320, 84, 400, 140, (255, 196, 160), lambda x, y: 0.10 if (y // 3) % 2 else 0.0)


def clock(cv):
    """El rellotge de paret: les sis menys vint."""
    cx, cy = 240, 30
    cv.disc(cx, cy, 10, 10, BEIGE, lambda nx, ny: 5.2 - (nx + ny) * 0.3)
    cv.ring(cx, cy, 10, SLATE, 1.0, step=4)
    cv.ring(cx, cy, 11, CHROME, 3.0, step=4)
    for h in range(12):
        a = h / 12 * 2 * math.pi
        cv.flat(cx + round(math.sin(a) * 8), cy - round(math.cos(a) * 8), (40, 40, 44))
    # les 5:40: l'agulla petita entre el 5 i el 6, la gran al 8
    ah = (5 + 40 / 60) / 12 * 2 * math.pi
    am = 40 / 60 * 2 * math.pi
    cv.line(cx, cy, cx + round(math.sin(ah) * 5), cy - round(math.cos(ah) * 5), [(20, 20, 24)], 0)
    cv.line(cx, cy, cx + round(math.sin(am) * 8), cy - round(math.cos(am) * 8), [(20, 20, 24)], 0)
    cv.flat(cx, cy, (200, 40, 40))


def poster(cv):
    """El pòster de la companyia: un avió damunt d'un mar massa blau, «VOLA AMB NOSALTRES»."""
    x0, y0, x1, y1 = 262, 22, 312, 76
    obox(cv, x0, y0, x1, y1, SHEET, 4.6)
    for y in range(y0 + 3, y1 - 12):
        for x in range(x0 + 3, x1 - 2):
            cv.put(x, y, BLUE, 2.6 + (y - y0) / 12)
    cv.disc(296, y0 + 12, 5, 5, YELS, 4.0, lit=0)                         # el sol
    cv.poly([(272, 50), (300, 42), (302, 44), (290, 50), (296, 56), (292, 57), (284, 52), (274, 53)], [(240, 244, 250)], 0)
    for k, word in enumerate(('VOLA AMB', 'NOSALTRES')):
        text(cv, word, (x0 + x1 - text_width(word)) // 2, y1 - 11 + k * 6, BLUE, 1.0)
    for (px, py) in ((x0 + 2, y0 + 2), (x1 - 2, y0 + 2)):
        cv.flat(px, py, (60, 60, 64))


# ─── Arxivadors, porta ─────────────────────────────────────────────────────

def cabinets(cv):
    """Tres arxivadors grisos, amb carpetes i una planta morta a sobre."""
    for i in range(3):
        x0 = 20 + i * 22
        obox(cv, x0, 70, x0 + 20, FLOOR_Y, CABINET, 3.2, top=0.8)
        for k in range(4):
            yy = 74 + k * 19
            obox(cv, x0 + 2, yy, x0 + 18, yy + 16, CABINET, 3.6, top=0.6)
            cv.rect(x0 + 7, yy + 3, x0 + 13, yy + 4, CHROME, 4.4)
            cv.rect(x0 + 8, yy + 7, x0 + 12, yy + 10, SHEET, 4.6)
    cv.darken(84, 71, 86, FLOOR_Y - 1, 0.4)
    # una calaixera mig oberta, amb carpetes
    obox(cv, 44, 112, 60, 118, CABINET, 3.0)
    for k in range(5):
        cv.rect(46 + k * 3, 108, 47 + k * 3, 112, [YELS[2], BLUE[3], REDB[2], YELS[3], SHEET[4]][k:k + 1] * 3, 0)
    # a sobre: carpetes apilades i la planta morta
    for k in range(4):
        cv.rect(24, 66 - k * 3, 40, 68 - k * 3, [BLUE, YELS, REDB, SHEET][k], 2.8)
    obox(cv, 70, 58, 80, 70, CARD, 3.0)
    for k in range(5):
        cv.line(75, 58, 70 + k * 3, 48 + (k % 2) * 3, [(50, 40, 20), (100, 80, 40), (140, 110, 60)], 1.6)


def door(cv):
    """La porta de sortida (al passadís de servei), vista des de dins: barra antipànic i finestreta."""
    x0, y0, x1, y1 = 400, 50, 450, FLOOR_Y
    obox(cv, x0 - 4, y0 - 4, x1 + 4, y1, CHROME, 2.8)
    obox(cv, x0, y0, x1, y1, DOOR, 3.6, top=0.6)
    cv.rect(x0 + 14, y0 + 8, x1 - 14, y0 + 30, [(10, 30, 20), (20, 60, 40), (50, 100, 70)], 1.4, lit=0)   # finestreta: el passadís verd
    outline(cv, x0 + 13, y0 + 7, x1 - 13, y0 + 31, CHROME)
    cv.rect(x0 + 4, 102, x1 - 4, 106, CHROME, lambda x, y: 3.6 + (1.2 if y == 103 else 0))
    obox(cv, x0 + 2, 100, x0 + 6, 108, CHROME, 3.0)
    obox(cv, x1 - 6, 100, x1 - 2, 108, CHROME, 3.0)
    obox(cv, 410, 30, 440, 40, GREENS, 2.6, lit=0)                        # sortida
    cv.rect(414, 32, 418, 38, [(240, 255, 240)], 0, lit=0)
    cv.line(421, 35, 436, 35, [(240, 255, 240)], 0, lit=0)
    cv.line(433, 33, 436, 35, [(240, 255, 240)], 0, lit=0)
    cv.line(433, 37, 436, 35, [(240, 255, 240)], 0, lit=0)
    cv.glow(425, 35, 16, (120, 255, 150), 0.16)
    cv.darken(x1 + 5, y0, x1 + 9, y1, 0.4)


# ─── L'escriptori ──────────────────────────────────────────────────────────

def desk(cv):
    """Un taulell llarg de melamina gris, amb faldó."""
    x0, x1 = 90, 330
    cv.poly([(x0 + 3, DESK_TOP - 6), (x1 - 3, DESK_TOP - 6), (x1 + 2, DESK_TOP), (x0 - 2, DESK_TOP)], BEIGE,
            lambda x, y: 4.4 + (y - DESK_TOP) * 0.08)
    cv.rect(x0 - 2, DESK_TOP, x1 + 2, DESK_TOP + 3, BEIGE, 3.0)
    cv.hline(x0 - 2, x1 + 2, DESK_TOP + 3, BEIGE, 0.6)
    obox(cv, x0, DESK_TOP + 4, x1, FLOOR_Y + 6, CABINET, 2.2, top=0.2)
    obox(cv, x1 - 44, DESK_TOP + 6, x1 - 4, FLOOR_Y + 4, CABINET, 2.8)      # la calaixera
    for k in range(3):
        cv.rect(x1 - 30, DESK_TOP + 12 + k * 9, x1 - 18, DESK_TOP + 13 + k * 9, CHROME, 4.0)
    cv.darken(x0 - 2, FLOOR_Y + 7, x1 + 4, FLOOR_Y + 11, lambda x, y: 0.65 - (y - FLOOR_Y - 7) * 0.12)


def terminal(cv):
    """El monitor de fòsfor verd (caixa beix, groguenca pels anys), el teclat i la torre."""
    x0, y0, x1, y1 = 118, 84, 182, 120
    obox(cv, x0, y0, x1, y1, BEIGE, 3.8, top=1.0)
    cv.rect(x0 + 3, y0 + 3, x1 - 3, y1 - 3, BEIGE, 2.6)
    screen(cv, llista=False)
    cv.rect(146, y1, 154, DESK_TOP - 3, BEIGE, 3.2)                        # el peu
    cv.disc(150, DESK_TOP - 3, 12, 1.6, BEIGE, 3.4)
    cv.flat(x1 - 6, y1 - 2, (60, 230, 90))                                 # el llum d'engegat
    # un pòsit amb la contrasenya, enganxat al marc (és clar)
    obox(cv, x1 - 2, y0 + 2, x1 + 8, y0 + 12, YELS, 4.0)
    for k in range(2):
        cv.hline(x1, x1 + 6 - k * 2, y0 + 5 + k * 3, [(30, 30, 80)], 0)
    # el teclat
    kb = [(116, DESK_TOP - 2), (186, DESK_TOP - 2), (190, DESK_TOP + 1), (112, DESK_TOP + 1)]
    cv.poly(kb, BEIGE, 3.4)
    outline_poly(cv, kb, BEIGE)
    for i in range(18):
        cv.flat(118 + i * 4, DESK_TOP - 1, (110, 104, 92))
    # la torre, a terra a l'esquerra del faldó
    obox(cv, 96, 128, 112, FLOOR_Y + 4, BEIGE, 3.4)
    cv.rect(99, 132, 109, 134, SLATE, 1.4)
    cv.flat(108, FLOOR_Y, (60, 230, 90))
    cable(cv, [(110, 128), (114, 122), (120, 121)], SLATE, 1.2)


def screen(cv, llista=False):
    """La pantalla: la llista de tripulació del BCMU-07 i, si l'Iri ja hi ha posat mà, les dues «tècniques»."""
    x0, y0, x1, y1 = SCREEN
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, PHOS, 1.2 + (0.6 if y % 2 else 0) - (0.5 if x in (x0, x1) or y in (y0, y1) else 0), lit=0)
    g = (110, 230, 120)
    text(cv, 'BCMU-07', x0 + 3, y0 + 2, PHOS, 0, lit=0, flat=g)
    for k, r in enumerate(('1 PILOT', '2 COPILOT')):
        text(cv, r, x0 + 3, y0 + 8 + k * 6, PHOS, 0, lit=0, flat=(80, 190, 90))
    if llista:
        text(cv, '3 I. I V.', x0 + 3, y0 + 20, PHOS, 0, lit=0, flat=(250, 230, 90))
    else:
        cv.hline(x0 + 3, x0 + 5, y0 + 24, [g], 0, lit=0)                  # el cursor
    cv.glow((x0 + x1) // 2, (y0 + y1) // 2, 30, (80, 220, 110), 0.10)


def printer(cv, estat='parada'):
    """La impressora làser, beix i enorme. `estat`: parada, imprimint o llestes (les acreditacions a la safata)."""
    x0, y0, x1, y1 = 256, 98, 306, DESK_TOP - 2
    obox(cv, x0, y0, x1, y1, BEIGE, 4.0, top=1.0)
    cv.rect(x0 + 6, y0 - 4, x1 - 6, y0, BEIGE, 3.2)                         # la safata d'entrada, amb paper
    cv.rect(x0 + 8, y0 - 6, x1 - 8, y0 - 4, SHEET, 5.0)
    cv.rect(x0 + 4, y0 + 8, x1 - 4, y0 + 10, SLATE, 0.8)                    # la boca
    obox(cv, x1 - 14, y0 + 3, x1 - 3, y0 + 7, PLASTIC, 1.6)                 # el panell
    led = {'parada': (200, 120, 40), 'imprimint': (60, 240, 100), 'llestes': (60, 240, 100)}[estat]
    cv.flat(x1 - 5, y0 + 5, led)
    cv.rect(x0 + 2, y1 - 3, x1 - 2, y1 - 2, BEIGE, 2.4)
    if estat == 'imprimint':
        # el full a mig sortir
        cv.rect(x0 + 10, y0 + 6, x1 - 10, y0 + 10, SHEET, 5.2)
        cv.hline(x0 + 12, x1 - 18, y0 + 8, SLATE, 2.6)
        cv.glow(x1 - 5, y0 + 5, 8, (60, 240, 100), 0.6)
    if estat == 'llestes':
        # dues acreditacions plastificades, damunt la safata de sortida
        for k, face in enumerate(((150, 90, 70), (110, 80, 66))):
            ax = x0 + 8 + k * 18
            obox(cv, ax, y0 + 10, ax + 14, y0 + 19, SHEET, 5.0)
            cv.rect(ax + 2, y0 + 12, ax + 5, y0 + 16, [face], 0, lit=0)
            cv.rect(ax + 7, y0 + 12, ax + 12, y0 + 12, [(40, 70, 160)], 0, lit=0)
            cv.rect(ax + 7, y0 + 14, ax + 11, y0 + 14, SLATE, 1.6)
            cv.rect(ax + 1, y0 + 17, ax + 13, y0 + 18, [(220, 40, 40)], 0, lit=0)
        cv.glow(x1 - 5, y0 + 5, 8, (60, 240, 100), 0.6)
    cable(cv, [(x1, y0 + 14), (x1 + 6, y0 + 22), (x1 + 4, DESK_TOP + 4)], SLATE, 1.2)


def desk_things(cv):
    """Un telèfon, un tampó, etiquetes de maletes, la tassa amb restes de cafè i un ventilador."""
    t = DESK_TOP - 3
    obox(cv, 196, t - 6, 214, t, PLASTIC, 2.0)                             # telèfon
    cv.rect(196, t - 9, 214, t - 7, PLASTIC, 2.8)
    cable(cv, [(198, t - 6), (192, t + 4), (200, t + 8), (204, t + 2)], PLASTIC, 1.6)
    obox(cv, 220, t - 3, 232, t, REDB, 2.4)                                 # el tampó
    cv.rect(236, t - 2, 250, t - 1, [(240, 220, 120)], 0)                   # etiquetes de maleta
    cv.rect(237, t - 4, 249, t - 3, [(250, 250, 250)], 0)
    obox(cv, 312, t - 7, 319, t, SHEET, 4.6)                                # la tassa
    cv.hline(313, 318, t - 6, [(70, 40, 20)], 0)
    # el ventilador, a la punta del taulell
    cv.rect(325, t - 12, 326, t, CHROME, 3.0)
    cv.disc(326, t - 18, 8, 8, CHROME, lambda nx, ny: 2.6 + (0.6 if (nx * 7 + ny * 5) % 2 < 0.3 else 0))
    cv.ring(326, t - 18, 8, CHROME, 4.0, step=6)
    cv.disc(326, t - 18, 1.6, 1.6, SLATE, 1.6)
    cv.disc(326, t, 5, 1.2, CHROME, 2.6)


def chair(cv):
    """La cadira d'oficina, amb rodes, girada cap a la pantalla."""
    cx = 226
    cv.rect(cx - 1, 140, cx + 1, 160, CHROME, 3.0)
    for dx in (-11, -5, 5, 11):
        cv.line(cx, 160, cx + dx, 165, CHROME, 2.6)
        cv.disc(cx + dx, 166, 1.4, 1, SLATE, 1.6)
    back = [(cx - 14, 112), (cx + 10, 112), (cx + 12, 134), (cx - 16, 134)]
    cv.poly(back, BLUE, lambda x, y: 1.8 + (0.6 if y < 116 else 0))
    outline_poly(cv, back, BLUE)
    seat = [(cx - 18, 134), (cx + 18, 134), (cx + 20, 142), (cx - 20, 142)]
    cv.poly(seat, BLUE, lambda x, y: 2.6 - (y - 134) * 0.12)
    outline_poly(cv, seat, BLUE)
    cv.darken(cx - 12, 167, cx + 14, 169, 0.55)


def bg(cv, llista=False, impressora='parada', sway=0.0):
    wall(cv)
    floor(cv)
    window(cv, sway)
    clock(cv)
    poster(cv)
    cabinets(cv)
    door(cv)
    desk(cv)
    if llista:
        terminal(cv)
        screen(cv, llista=True)
    else:
        terminal(cv)
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


# ─── Animació: el ventilador i el cursor ───────────────────────────────────

def _frames():
    base = _base()
    frames = []
    for i in range(6):
        cv = Canvas(light=LIGHT, img=base.copy())
        t = DESK_TOP - 3
        cv.disc(326, t - 18, 7, 7, CHROME, lambda nx, ny, i=i: 2.4 + (0.8 if math.sin(math.atan2(ny, nx) * 3 + i * 1.1) > 0.4 else 0))
        cv.ring(326, t - 18, 8, CHROME, 4.0, step=6)
        cv.disc(326, t - 18, 1.6, 1.6, SLATE, 1.6)
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
    cx, cy = 240, 30
    out = []
    for s in (15, 16):
        cv = Canvas(light=LIGHT, img=base.copy())
        a = s / 60 * 2 * math.pi
        cv.line(cx - round(math.sin(a) * 2), cy + round(math.cos(a) * 2), cx + round(math.sin(a) * 8), cy - round(math.cos(a) * 8), [(190, 36, 36)], 0, lit=0)
        cv.flat(cx, cy, (200, 40, 40))
        out.append(_diff(cv.img, base))
    return [out[0]] * 4 + [out[1]]


ANIMS = {'ventilador': {'frames': _frames, 'frameDuration': 70},
         'persiana': {'frames': _frames_persiana, 'frameDuration': 180},
         'segons': {'frames': _frames_segons, 'frameDuration': 200}}
