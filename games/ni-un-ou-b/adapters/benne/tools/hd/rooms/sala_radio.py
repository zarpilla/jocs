"""
La sala de ràdio, rere el pont: petita, blau grisós com el pont però amb un llum càlid de taula.

  - a l'esquerra, la porta estanca del pont, oberta (en Bastida s'hi para);
  - la ràdio de llarg abast: un aparell vell, gros, amb dials, el visor de freqüència ambre, el vúmetre,
    l'altaveu i el micròfon de mà penjat;
  - el panell de la paret per on baixa el cable de l'antena, amb els cargols de pintura saltada;
  - el rellotge de ràdio (amb els sectors de silenci), el prestatge dels llibres de registre i un ull de bou.
Props: `dia` (Escenes 2 i 3, de dia), `panell_obert` (el panell sense la xapa, amb el cable de malla d'acer) , `cable` (el tram tallat) i
`panell_reparat` (el tram nou, amb les virolles crimpades).
ANIMS: `mar` (de nit) i `dia_mar` (de dia, amb el decorat `dia_mar`, per sobre de `dia`): el mar pel vidre del pont, que
es veu per la porta, i els pilots de la consola del pont. La ràdio no es mou: és morta fins que l'Iri l'arregla.
"""
import functools
import math

from hd.pix import Canvas, Light, W, H, hr, mix
from hd.rooms.arenga import CAB, ENG, DARK, WHITEP, REDP, YELL, BRASS, WARM, box, rrect, bolt, vpipe, hpipe, glow
from hd.rooms.comu import _diff, text
from hd.rooms.exterior import day_sky, day_sea
from hd.rooms.pont import (BRI, AMB, SCRG, WOOD, FLOOR_Y, wall, floor, door_frame, outside, _MODE, HORIZON)

LAMP = (226, 30)

LIGHT = Light(ambient=0.5, vignette=(60, 26), floor_fade=None)
LIGHT.point(226, 34, r=170, k=2.4, squash=1.1, down=True, power=1.5)     # el llum de la taula, càlid
LIGHT.point(28, 100, r=60, k=0.5, power=1.8)                             # la claror del pont
LIGHT.point(222, 84, r=50, k=0.5, power=1.8)                             # el visor de la ràdio

# `dia` (Escenes 2 i 3): claror grisa del matí per l'ull de bou i la porta del pont; el llum de taula, encès
LIGHT_DIA = Light(ambient=1.5, vignette=(60, 26), floor_fade=None)
LIGHT_DIA.point(226, 34, r=150, k=1.4, squash=1.1, down=True, power=1.5)
LIGHT_DIA.point(28, 100, r=90, k=1.0, power=1.6)                        # la claror del pont, de dia
LIGHT_DIA.point(440, 60, r=110, k=1.0, power=1.6)                       # l'ull de bou

CABLE = [(6, 6, 8), (16, 16, 20), (30, 30, 36), (48, 48, 56), (72, 72, 80)]
MESH = [(40, 40, 44), (90, 92, 96), (150, 152, 156), (210, 212, 214)]


# ─── Sostre ────────────────────────────────────────────────────────────────

def ceiling(cv):
    cv.rect(0, 0, W - 1, 17, DARK, 2.2)
    for bx in range(-20, W, 56):
        box(cv, bx - 2, 0, bx + 6, 19, BRI, 2.0, grad=0.8)
    cv.hline(0, W - 1, 18, BRI, 1.2)
    cv.hline(0, W - 1, 19, BRI, 3.0)
    # la canaleta de cables, que va del pont a l'antena (passa pel panell)
    box(cv, 0, 22, W - 1, 26, CAB, 2.4)
    for x in range(4, W, 40):
        box(cv, x, 21, x + 2, 27, CAB, 3.4)
    # el llum, un pantalla de metall verd de les d'abans
    cv.vline(LAMP[0], 0, LAMP[1] - 6, CAB, 2.0)
    cv.poly([(LAMP[0] - 3, LAMP[1] - 6), (LAMP[0] + 3, LAMP[1] - 6), (LAMP[0] + 12, LAMP[1]), (LAMP[0] - 12, LAMP[1])],
            [(10, 24, 18), (18, 44, 30), (30, 70, 46), (50, 100, 66), (80, 130, 90)], lambda x, y: 2.4 - (x - LAMP[0]) * 0.08)
    cv.disc(LAMP[0], LAMP[1] + 1, 7, 2, [(160, 120, 60), (250, 220, 150), (255, 246, 220)], 2.0, lit=0)


# ─── Animació: fotograma actual (0 = el fons quiet) ────────────────────────
ANIM_N = 12
_ANIM = {'f': 0}
SEA_FADE, SEA_STEP = 4, 0.32


@functools.lru_cache(maxsize=None)
def _day_view(f):
    """El cel i el mar de dia per al fotograma f (com pont._day_outside, que és el f = 0). Perquè el bucle no
    salti, els darrers SEA_FADE fotogrames es fonen (a quadres) amb el principi."""
    def view(phase):
        cv = Canvas()
        day_sky(cv, 4, HORIZON - 1, seed=13)
        day_sea(cv, HORIZON, H - 1, seed=6, phase=phase)
        return cv.img
    if f == 0:
        return view(0.0)
    a, b = view(f * SEA_STEP), view((f - ANIM_N) * SEA_STEP)
    w = max(0, f - (ANIM_N - SEA_FADE)) / SEA_FADE
    out = a.copy()
    o, bp = out.load(), b.load()
    for y in range(HORIZON, H):
        for x in range(W):
            if hr(x, y, 90) < w:
                o[x, y] = bp[x, y]
    return out


def _outside(cv, x0, y0, x1, y1):
    """Com pont.outside, però amb el mar del fotograma actual (_ANIM)."""
    f = _ANIM['f']
    if _MODE['dia']:
        src, dst = _day_view(f).load(), cv.P
        for y in range(max(0, y0), min(H - 1, y1) + 1):
            for x in range(max(0, x0), min(W - 1, x1) + 1):
                dst[x, y] = src[x, y]
        return
    outside(cv, x0, y0, x1, y1, t=f * 2 * math.pi / 0.8 / ANIM_N)   # les onades de pont.outside: sin(... + t * 0.8)


# ─── La porta del pont, oberta ──────────────────────────────────────────────

def door(cv):
    x0, y0, x1, y1 = 12, 66, 52, FLOOR_Y
    # el pont, fosc: el vidre amb la nit i un tros de consola
    for y in range(y0, y1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, BRI, 1.8 - (y - y0) * 0.004, lit=0.3)
    _outside(cv, x0 + 6, y0 + 8, x1 - 4, y0 + 40)
    cv.rect(x0 + 4, y0 + 6, x1 - 2, y0 + 7, BRI, 3.0, lit=0.3)
    cv.rect(x0 + 4, y0 + 41, x1 - 2, y0 + 44, BRI, 3.0, lit=0.3)
    box(cv, x0, 110, x1, 150, ENG, 1.6, edge=False)                   # la consola, al fons
    cv.hline(x0, x1, 110, ENG, 3.0)
    f = _ANIM['f']
    for x in range(x0 + 4, x1, 6):
        if hr(x, 1) > 0.5 and not (x == x0 + 34 and f in (7, 8)):     # un pilot verd que fa un pampallugueig
            cv.flat(x, 113, (90, 240, 140))
    if (f // 3) % 2:                                                   # el d'alarma de la sentina, ambre, a poc a poc
        cv.flat(x0 + 16, 113, (240, 170, 60))
    cv.rect(x0 + 1, y1 - 5, x1 - 1, y1, BRI, 2.6)                      # el llindar alt
    cv.hline(x0 + 1, x1 - 1, y1 - 5, BRI, 4.0)
    door_frame(cv, x0, y0, x1, y1, BRI)
    # la fulla, oberta contra la paret (de cantó)
    cv.poly([(2, y0 + 4), (10, y0 - 1), (10, y1 - 2), (2, y1 - 4)], BRI, lambda x, y: 3.0 - (x - 2) * 0.06)
    for y in range(y0 + 12, y1 - 8, 24):
        box(cv, 4, y, 8, y + 3, CAB, 3.6)
    box(cv, 22, 54, 44, 61, WHITEP, 3.8)
    text(cv, 'PONT', 25, 56, BRI, 1.0)


# ─── La ràdio de llarg abast ────────────────────────────────────────────────

DESK_TOP = 108


def desk(cv):
    x0, x1 = 138, 312
    box(cv, x0, DESK_TOP, x1, DESK_TOP + 4, WOOD, 4.0)
    cv.hline(x0, x1, DESK_TOP, WOOD, 5.4)
    # el cos de la taula: calaixos a la dreta, forat per a les cames
    box(cv, 252, DESK_TOP + 5, x1 - 2, FLOOR_Y + 2, CAB, 2.6, grad=0.6)
    for y in (118, 130, 142):
        box(cv, 256, y, x1 - 6, y + 9, CAB, 3.2)
        box(cv, 274, y + 3, 290, y + 5, BRASS, 3.0)
    box(cv, x0 + 2, DESK_TOP + 5, x0 + 8, FLOOR_Y + 2, CAB, 2.4)
    for y in range(DESK_TOP + 5, FLOOR_Y + 1):                        # l'ombra de sota
        cv.darken(x0 + 9, y, 251, y, 0.5 + (y - DESK_TOP) * 0.01)
    # el tamboret, amagat a sota
    box(cv, 180, 132, 214, 136, WOOD, 3.4)
    for lx in (184, 210):
        cv.vline(lx, 137, FLOOR_Y + 4, CAB, 2.4)
    cv.hline(184, 210, 146, CAB, 2.0)


def radio(cv, dead=False):
    x0, y0, x1, y1 = 152, 60, 300, DESK_TOP - 1
    # la caixa gran, gris verdós de les d'abans, amb nanses al davant
    box(cv, x0, y0, x1, y1, CAB, 3.2, grad=0.8)
    cv.hline(x0 + 1, x1 - 1, y0 + 1, CAB, 4.4)
    for hx in (x0 + 3, x1 - 7):
        box(cv, hx, y0 + 10, hx + 4, y1 - 10, BRASS, 2.6)
        cv.vline(hx + 1, y0 + 11, y1 - 11, BRASS, 4.2)
    for bx, by in ((x0 + 2, y0 + 3), (x1 - 4, y0 + 3), (x0 + 2, y1 - 4), (x1 - 4, y1 - 4)):
        bolt(cv, bx, by, CAB, 3.6)
    # l'altaveu, a l'esquerra (reixeta)
    rrect(cv, 164, 66, 196, 100, 4, CAB, 1.8)
    for y in range(69, 99, 3):
        for x in range(167, 194, 3):
            cv.put(x, y, DARK, 0.4)
    # el visor de freqüència, ambre
    box(cv, 204, 66, 262, 78, DARK, 1.0)
    cv.rect(206, 68, 260, 76, AMB, 1.0, lit=0)
    text(cv, '2182.0', 210, 70, AMB, 4.4, lit=0)
    glow(cv, 233, 72, 22, (255, 170, 60), 0.3)
    # el vúmetre
    box(cv, 268, 66, 292, 80, DARK, 1.0)
    cv.rect(270, 68, 290, 78, [(120, 100, 60), (200, 180, 120), (240, 226, 180)], 1.6, lit=0.5)
    for a in range(210, 331, 20):
        cv.put(280 + round(math.cos(math.radians(a)) * 8), 80 + round(math.sin(math.radians(a)) * 8), DARK, 0.4)
    cv.line(280, 79, 274, 71, DARK, 0.2)
    cv.rect(286, 70, 289, 71, REDP, 3.4)
    # els dials grans (sintonia i guany) i una fila de botons
    for cx in (216, 248):
        cv.disc(cx, 92, 8, 8, DARK, 1.2)
        cv.disc(cx, 92, 7, 7, CAB, lambda nx, ny: 4.2 - nx * 1.2 - ny * 1.4)
        cv.disc(cx, 92, 3, 3, CAB, lambda nx, ny: 2.4 + nx + ny)
        for a in range(0, 360, 30):
            cv.put(cx + round(math.cos(math.radians(a)) * 10), 92 + round(math.sin(math.radians(a)) * 10), WHITEP, 2.6)
    for i, x in enumerate(range(266, 294, 7)):
        box(cv, x, 88, x + 4, 92, CAB, 4.0 if i != 1 else 2.4)
    for i, x in enumerate(range(266, 294, 7)):
        cv.disc(x + 2, 99, 2, 2, CAB, lambda nx, ny: 3.8 - nx - ny)
    # el pilot d'encès (apagat: la ràdio és morta fins que l'Iri l'arregla)
    cv.disc(204, 96, 2, 2, REDP, 1.4)
    # el micròfon de mà, penjat al ganxo del costat, amb el cordó en espiral
    box(cv, 302, 70, 306, 74, CAB, 3.4)
    rrect(cv, 302, 74, 312, 92, 3, DARK, lambda x, y: 2.4 - (x - 302) * 0.1)
    cv.rect(304, 78, 308, 82, CABLE, 3.6)
    box(cv, 312, 80, 314, 84, CAB, 3.6)
    for i in range(16):
        y = 93 + i
        cv.put(306 + round(math.sin(i * 1.4) * 2), y, DARK, 2.2)
    # els auriculars, damunt de la taula
    cv.ring(178, DESK_TOP - 4, 6, DARK, 2.4, step=12)
    cv.disc(172, DESK_TOP - 2, 3, 2, DARK, 1.6)
    cv.disc(184, DESK_TOP - 2, 3, 2, DARK, 1.6)
    # el llibre de registre de ràdio, obert, i un llapis
    cv.poly([(232, DESK_TOP - 2), (268, DESK_TOP - 2), (270, DESK_TOP), (230, DESK_TOP)], WHITEP, 4.4)
    cv.vline(250, DESK_TOP - 2, DESK_TOP, WHITEP, 2.4)
    for y in (DESK_TOP - 1,):
        for x in range(234, 266, 2):
            if hr(x, 9) > 0.3 and x != 250:
                cv.put(x, y, DARK, 1.8)
    cv.line(272, DESK_TOP - 1, 282, DESK_TOP - 3, YELL, 4.0)


# ─── El panell de l'antena (tancat) ─────────────────────────────────────────

PANEL = (330, 60, 390, 120)


def panel(cv):
    """La xapa del panell, amb quatre cargols de pintura saltada; la canaleta hi baixa del sostre."""
    x0, y0, x1, y1 = PANEL
    # la canaleta que baixa del sostre fins al panell, i la que surt cap a la ràdio
    box(cv, 354, 26, 366, y0, CAB, 2.6, grad=0.4)
    cv.vline(356, 27, y0 - 1, CAB, 3.6)
    box(cv, 316, 104, x0, 110, CAB, 2.4)
    cv.hline(316, x0, 105, CAB, 3.4)
    # el marc i la xapa
    box(cv, x0 - 2, y0 - 2, x1 + 2, y1 + 2, BRI, 2.2)
    box(cv, x0, y0, x1, y1, BRI, 4.0, grad=0.8)
    cv.hline(x0 + 2, x1 - 2, y0 + 2, BRI, 5.0)
    for bx, by in ((x0 + 4, y0 + 4), (x1 - 5, y0 + 4), (x0 + 4, y1 - 5), (x1 - 5, y1 - 5)):
        cv.disc(bx, by, 1.6, 1.6, CAB, 4.4)
        cv.put(bx - 1, by, CAB, 1.4)
        cv.put(bx + 1, by, CAB, 1.4)
        for dx, dy in ((2, -1), (-2, 1), (1, 2)):                         # la pintura saltada
            cv.put(bx + dx, by + dy, WHITEP, 2.6)
    # el rètol: llamp groc i ANTENA
    cv.poly([(360, 70), (368, 84), (352, 84)], YELL, 4.2)
    cv.vline(360, 74, 80, DARK, 0.4)
    box(cv, 338, 90, 382, 97, WHITEP, 3.8)
    text(cv, 'ANTENA', 343, 91, BRI, 1.0)


# ─── El racó de la dreta ────────────────────────────────────────────────────

def radio_clock(cv):
    """El rellotge de ràdio, amb els sectors vermells i verds dels minuts de silenci."""
    cx, cy, r = 112, 44, 13
    cv.disc(cx, cy, r + 2, r + 2, BRASS, lambda nx, ny: 3.6 - nx - ny * 1.2)
    cv.disc(cx, cy, r, r, WHITEP, 4.0)
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            d = math.hypot(x - cx, y - cy)
            if r - 4 <= d <= r - 1:
                a = (math.degrees(math.atan2(x - cx, cy - y)) + 360) % 360
                m = a / 6
                if 15 <= m < 18 or 45 <= m < 48:
                    cv.put(x, y, REDP, 4.0)
                elif 0 <= m < 3 or 30 <= m < 33:
                    cv.put(x, y, SCRG, 3.4)
    for a in range(0, 360, 30):
        cv.put(cx + round(math.sin(math.radians(a)) * (r - 1)), cy - round(math.cos(math.radians(a)) * (r - 1)), DARK, 0.4)
    cv.line(cx, cy, cx + 5, cy - 4, DARK, 0.2)                          # les tres i quart, més o menys
    cv.line(cx, cy, cx - 2, cy - 9, DARK, 0.2)
    cv.disc(cx, cy, 1, 1, REDP, 3.0)


def shelf(cv):
    """El prestatge dels llibres de registre i dels manuals, amb una barana perquè no caiguin."""
    x0, x1 = 410, 470
    box(cv, x0, 92, x1, 95, WOOD, 3.6)
    x = x0 + 2
    i = 0
    while x < x1 - 4:
        w = 4 + int(hr(i, 2) * 4)
        h = 14 + int(hr(i, 3) * 6)
        ramp = [CABLE, [(20, 30, 60), (36, 52, 96), (60, 80, 130), (100, 120, 170)],
                [(60, 20, 20), (100, 34, 30), (140, 54, 44), (180, 90, 70)], WOOD][int(hr(i, 4) * 4)]
        box(cv, x, 92 - h, x + w - 1, 91, ramp, 2.4, edge=False)
        cv.vline(x, 92 - h, 91, ramp, 3.4)
        cv.hline(x + 1, x + w - 2, 92 - h + 3, WHITEP, 2.6)
        x += w + 1
        i += 1
    cv.hline(x0, x1, 84, BRASS, 3.2)
    for px in (x0 + 2, x1 - 2):
        cv.vline(px, 84, 91, BRASS, 2.8)


def porthole(cv):
    """Un ull de bou petit: fora, la nit."""
    cx, cy = 440, 54
    cv.disc(cx, cy, 13, 13, BRASS, lambda nx, ny: 3.6 - nx - ny * 1.2)
    cv.disc(cx, cy, 10, 10, DARK, 1.0)
    for y in range(cy - 9, cy + 10):
        for x in range(cx - 9, cx + 10):
            if (x - cx) ** 2 + (y - cy) ** 2 <= 81:
                outside(cv, x, y, x, y)
    for a in range(0, 360, 60):
        bolt(cv, cx + round(math.cos(math.radians(a)) * 11.5), cy + round(math.sin(math.radians(a)) * 11.5), BRASS, 3.0)
    for i in range(6):
        cv.flat(cx - 5 + i, cy - 6 + i, mix(cv.get(cx - 5 + i, cy - 6 + i)[:3],
                                            (236, 240, 244) if _MODE['dia'] else (150, 160, 180), 0.25))


def extinguisher(cv):
    """Un extintor de CO2 (per als aparells elèctrics), a terra al costat del panell."""
    x0, x1 = 452, 462
    for y in range(116, FLOOR_Y + 2):
        for x in range(x0, x1 + 1):
            u = (x - (x0 + x1) / 2) / 5.5
            cv.put(x, y, REDP, 3.6 + 1.4 * (-0.3 - u) - 0.8 * u * u)
    cv.disc((x0 + x1) / 2, 116, 5, 3, REDP, 4.2)
    box(cv, 455, 108, 459, 113, CAB, 3.4)
    cv.line(459, 110, 464, 108, CAB, 3.4)
    cv.rect(x0 + 1, 128, x1 - 1, 134, WHITEP, 3.6)


def bg(cv):
    wall(cv)
    ceiling(cv)
    door(cv)
    panel(cv)
    desk(cv)
    radio(cv)
    radio_clock(cv)
    shelf(cv)
    porthole(cv)
    floor(cv)
    extinguisher(cv)
    glow(cv, LAMP[0], LAMP[1] + 2, 30, WARM, 0.25 if _MODE['dia'] else 0.45)
    glow(cv, LAMP[0], LAMP[1] + 2, 10, (255, 240, 200), 0.6)


# ─── Props ──────────────────────────────────────────────────────────────────

def panell_obert(cv):
    """El panell sense la xapa: el forat fosc, el cable de l'antena que hi baixa i el born de connexió. La xapa,
    a terra, recolzada a la paret; una gota de sang seca a la vora."""
    x0, y0, x1, y1 = PANEL
    box(cv, x0, y0, x1, y1, DARK, 1.2)
    for y in range(y0 + 1, y1):
        cv.hline(x0 + 1, x1 - 1, y, DARK, 1.4 + (y - y0) * 0.02)
    # forats dels cargols i la vora tallant
    for bx, by in ((x0 + 4, y0 + 4), (x1 - 5, y0 + 4), (x0 + 4, y1 - 5), (x1 - 5, y1 - 5)):
        cv.disc(bx, by, 1.6, 1.6, BRI, 4.4)
        cv.put(bx, by, DARK, 0)
    cv.hline(x0, x1, y0, BRI, 5.4)
    cv.vline(x0, y0, y1, BRI, 4.8)
    cv.flat(x1, y0 + 30, (110, 20, 18))                              # la gota de sang
    cv.flat(x1, y0 + 31, (80, 14, 14))
    # els cables secundaris, al fons, en una safata
    for i, (yy, col) in enumerate(((68, CABLE), (72, [(60, 20, 20), (120, 40, 34), (180, 70, 50)]), (114, CABLE))):
        cv.hline(x0 + 3, x1 - 3, yy, col, 2.2)
    # el cable de l'antena: baixa del sostre fins al tall (a dalt) i del tall al born (a baix)
    cx = 360
    _cable(cv, cx, y0 + 1, 76)
    _end(cv, cx, 76, up=True)
    _cable(cv, cx, 105, 108)
    _end(cv, cx, 105, up=False)
    # el born de connexió i la sortida cap a la ràdio
    box(cv, 350, 108, 370, 114, CAB, 3.2)
    for bx in (354, 360, 366):
        cv.disc(bx, 111, 1.5, 1.5, BRASS, 4.2)
    cv.hline(x0 + 1, 350, 107, CABLE, 2.4)
    # la xapa, a terra, recolzada a la paret
    cv.poly([(394, FLOOR_Y + 4), (436, FLOOR_Y + 4), (442, 102), (402, 102)], BRI, lambda x, y: 3.8 - (y - 102) * 0.03)
    cv.line(402, 102, 442, 102, BRI, 5.0)
    cv.line(394, FLOOR_Y + 4, 402, 102, BRI, 4.6)
    cv.line(436, FLOOR_Y + 4, 442, 102, BRI, 1.6)
    for bx, by in ((405, 106), (437, 106), (399, 150), (432, 150)):
        cv.disc(bx, by, 1.2, 1.2, DARK, 0.6)
    cv.poly([(419, 110), (425, 121), (413, 121)], YELL, 3.8)
    box(cv, 404, 126, 432, 131, WHITEP, 3.4)


def _cable(cv, cx, y0, y1):
    """Cable gruixut de funda negra (5 px)."""
    for y in range(y0, y1 + 1):
        for x in range(cx - 2, cx + 3):
            u = (x - cx) / 2.5
            cv.put(x, y, CABLE, 3.9 + 1.6 * (-0.3 - u) - 0.8 * u * u, lit=0.5)


def _end(cv, cx, y, up):
    """El cap tallat: la funda s'acaba i en surt la malla d'acer, esfilagarsada."""
    d = 1 if up else -1
    for i in range(4):
        yy = y + d * (i + 1)
        for x in range(cx - 2, cx + 3):
            if hr(x, yy) > 0.25 + i * 0.12:
                cv.put(x + (1 if i == 3 and x > cx else 0), yy, MESH, 2.6 - i * 0.3)
    cv.put(cx, y + d * 5, MESH, 3.4)                                  # el fil de coure del mig
    cv.put(cx, y + d * 6, [(80, 40, 20), (200, 120, 60)], 1.4)


def cable(cv):
    """El tram tallat: el tros del mig, encara al seu lloc, amb el tall net (i l'osca de la cisalla mellada)."""
    cx = 360
    _cable(cv, cx, 77, 88)
    _cable(cv, cx + 1, 92, 104)                                       # el tros de sota, una mica de biaix
    for x in range(cx - 2, cx + 3):                                   # la malla d'acer, a cada costat del tall
        cv.put(x, 89, MESH, 3.0 if x % 2 else 2.0)
        cv.put(x + 1, 91, MESH, 3.0 if x % 2 else 2.0)
    cv.put(cx, 90, [(80, 40, 20), (200, 120, 60)], 1.4)               # el fil de coure del mig
    cv.put(cx - 2, 89, DARK, 0)                                       # l'osca
    cv.put(cx - 1, 91, DARK, 0)


def panell_reparat(cv):
    """Decorat `panell_reparat` (connector crimpat, panell encara obert): el tram nou al forat del tallat, amb la
    funda més lluent, i una virolla crimpada a cada empalmament, tapant la malla esfilagarsada."""
    cx = 360
    _cable(cv, cx, 77, 104)
    for y in range(79, 103):                                          # funda nova: una lluentor que la deixa veure
        cv.put(cx - 1, y, CABLE, 4.4, lit=0.5)
    _virolla(cv, cx, 77, 83)
    _virolla(cv, cx, 98, 104)


def _virolla(cv, cx, y0, y1):
    """Virolla de metall (7 px d'ample) crimpada: un cilindre lluent amb les marques de la crimpadora."""
    for y in range(y0, y1 + 1):
        for x in range(cx - 3, cx + 4):
            u = (x - cx) / 3.5
            lvl = 2.4 + 1.2 * (-0.3 - u) - 0.7 * u * u
            if y in (y0 + 2, y1 - 2):                                 # les dues marques del crimpat
                lvl -= 1.1
            cv.put(x, y, MESH, lvl, lit=0.5)
    cv.hline(cx - 2, cx + 2, y0, MESH, 1.2, lit=0.3)                  # les vores
    cv.hline(cx - 2, cx + 2, y1, MESH, 1.0, lit=0.3)


def dia(cv):
    """Decorat `dia` (sota, Escenes 2 i 3): la sala sencera de dia, amb el cel gris a l'ull de bou i al vidre
    del pont, que es veu per la porta."""
    _MODE['dia'] = True
    try:
        day = Canvas(light=LIGHT_DIA)
        bg(day)
    finally:
        _MODE['dia'] = False
    day.tint(0, 0, W - 1, H - 1, (150, 160, 172), 0.08)
    cv.img.paste(day.img)


PROPS = {'dia': dia, 'panell_obert': panell_obert, 'cable': cable, 'panell_reparat': panell_reparat}


# ─── Animacions ────────────────────────────────────────────────────────────

def _frames(draw):
    """Fotogrames: la sala sencera a cada fotograma, menys el fons quiet (només el que canvia)."""
    def render(f):
        _ANIM['f'] = f
        try:
            cv = Canvas(light=LIGHT)
            draw(cv)
            return cv.img
        finally:
            _ANIM['f'] = 0
    base = render(0)
    return [_diff(render(f), base) for f in range(ANIM_N)]


ANIMS = {'mar': {'frames': lambda: _frames(bg), 'frameDuration': 260},
         'dia_mar': {'frames': lambda: _frames(dia), 'frameDuration': 260}}


# ─── Geometria ─────────────────────────────────────────────────────────────

def _t(x0, y0, x1, y1, wx=None, wy=180):
    return {'rect': (x0, y0, x1, y1), 'walk': (wx if wx is not None else (x0 + x1) // 2, wy)}


GEOMETRIA = {
    'things': {
        'porta': _t(4, 62, 54, 150, wx=34, wy=172),
        'radio': _t(150, 58, 314, 108, wx=226, wy=174),
        'panell': _t(328, 58, 392, 122, wx=318, wy=176),
        'cable': _t(344, 74, 376, 106, wx=318, wy=176),
    },
    'spawns': {'iri': (318, 188), 'vet': (200, 192), 'bastida': (34, 186)},
    'walkable': [(10, 164), (470, 164), (476, 200), (4, 200)],
}
