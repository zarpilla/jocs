"""
El final (els tres finals) (hd/rooms/final_bar.py) a 640×360: la mateixa composició ×4/3, dibuixada de nou.
Una setmana després, el bar La Propina, a la tarda. Cinemàtica, sense res clicable.
Es dibuixa damunt del bar de l'Escena 2 (hd640/rooms/bar_sala.py), amb llum de dia:
  - per l'aparador i la porta entra el sol de la tarda; el neó «LA PROPINA», apagat;
  - una tele nova i més grossa: la roda de premsa del BCMU, un banquer al faristol, el rètol «EL SISTEMA HA
    RESISTIT» i, a la cinta de sota, «CAL MÉS REGULACIÓ»;
  - un paper escrit a mà a la barra, «TORNEM A ESTAR OBERTS», amb cinta adhesiva;
  - la taula llarga: tres taules diferents ajuntades, amb gots, ampolles i pa amb tomàquet;
  - a la punta, una cadira amb la cistella d'en Diu. Els personatges seuen darrere la taula (FRONT);
  - el cable de la tele, que penja fins a la barra; i la tele apagada (`tele_apagada`), quan en Diu el mossega.
Animació: `tele` (el banquer parla i fa que sí, el punt d'«EN DIRECTE» i l'escurabutxaques).
"""
import math
from functools import lru_cache

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from hd.pix import Light, Canvas, hr
from hd.rooms.comu import obox, outline, text, text_width, PLASTIC, SHEET, YEL
from hd.rooms.pis_cuina import outline_poly
from hd.rooms.final_bar import (DAYSKY, HILL, ASPH, NEONOFF, STUDIO, NEWSRED, TIE, SUITN, FACE, WICKER,  # noqa: F401
                                BLANKET, TOMATO, BREAD, BEER, INK, CLOTH, VICHY, PAPER)
from hd640.rooms.bar_sala import (bg as bar_bg, slot_machine, fast_diff, WIN, WOOD, STEELB, BRASS, ENAMEL, PORC,
                                  BOTTLES, FLOOR_Y, BAR_TOP, SLATE)

# Art a 2× (1280×720 per a una sala de 640×360): el mateix dibuix, amb les formes, el dither i la llum a la
# resolució real (hd1280/canvas2x.py); el motor el mostra a 1/2 (artScale al .room.json).
ART_SCALE = 2
from hd1280.canvas2x import Canvas2x as Canvas  # noqa: E402,F811
from hd.pix import Canvas as Canvas1x  # noqa: E402,F401  (llenços auxiliars en píxels de sala: figures, textos)

# De dia: el sol de la tarda per l'aparador i per la porta; el fluorescent, encès però sense protagonisme.
LIGHT = Light(ambient=0.9, vignette=(80, 45), floor_fade=(261, 45))
LIGHT.point(320, 77, r=293, k=2.4, squash=1.3, power=1.5)        # el fluorescent
LIGHT.point(147, 67, r=147, k=1.4, squash=1.0, power=1.6)        # l'aparador
LIGHT.point(624, 147, r=160, k=1.6, squash=0.8, power=1.6)       # la porta del carrer
LIGHT.point(491, 75, r=80, k=0.6, squash=1.0, power=2.0)         # la tele

TV = (429, 29, 549, 116)                      # la tele nova (tapa la vella)
SCR = (TV[0] + 4, TV[1] + 4, TV[2] - 4, TV[3] - 9)


# ─── La paret del fons, de dia ─────────────────────────────────────────────

def window_day(cv):
    """L'aparador de tarda: cel pàl·lid, el talús amb herba seca, l'autopista i el neó apagat."""
    x0, y0, x1, y1 = WIN
    for y in range(y0 + 2, y1 - 1):
        for x in range(x0 + 3, x1 - 2):
            cv.put(x, y, DAYSKY, 2.2 + (y - y0) / 16, lit=0)
    for (cx, cy, rx) in ((128, 36, 9), (166, 41, 7)):                    # dos núvols prims
        cv.disc(cx, cy, rx, 1.6, DAYSKY, 5.4, lit=0)
    for x in range(x0 + 3, x1 - 2):
        top = 64 - int(4 * math.sin(x / 12))
        for y in range(top, y1 - 1):
            cv.put(x, y, HILL, 2.2 + (hr(x // 2, y // 2) - 0.5) * 0.8 - (y - top) * 0.11, lit=0)
            if y == top and hr(x, 5) > 0.6:                              # l'herba seca, punxeguda
                cv.put(x, y - 1, HILL, 3.4, lit=0)
    cv.rect(x0 + 3, 71, x1 - 3, 74, ASPH, 1.6, lit=0)                    # el carril de servei
    cv.hline(x0 + 3, x1 - 3, 72, ASPH, 3.2, lit=0)
    for dx in range(x0 + 6, x1 - 3, 9):                                  # la ratlla discontínua
        cv.hline(dx, dx + 3, 73, [(230, 226, 210)], 0, lit=0)
    cv.hline(x0 + 3, x1 - 3, 61, ASPH, 3.0, lit=0)                       # la bionda
    for gx in range(x0 + 4, x1 - 2, 7):
        cv.vline(gx, 61, 64, ASPH, 2.4, lit=0)
    for lx in (117, 149, 179):                                           # fanals, apagats
        cv.vline(lx, 40, 62, ASPH, 1.0, lit=0)
        cv.hline(lx, lx + 4, 40, ASPH, 1.0, lit=0)
        cv.put(lx + 4, 41, ASPH, 2.4, lit=0)
    # un camió blanc que passa
    cv.rect(157, 59, 176, 68, SHEET, lambda x, y: 4.4 + (0.6 if y == 59 else 0), lit=0)
    cv.hline(158, 175, 64, NEWSRED, 2.6, lit=0)                          # la franja de l'empresa
    cv.rect(152, 61, 156, 68, NEWSRED, 2.4, lit=0)                       # la cabina
    cv.rect(153, 62, 155, 64, DAYSKY, 4.0, lit=0)
    for wx in (159, 172):
        cv.rect(wx, 69, wx + 1, 70, [(20, 20, 24)], 0, lit=0)
    # el neó, apagat: tubs grisos, del revés, amb els suports
    w = text_width('LA PROPINA')
    tx = (x0 + x1 - w) // 2
    text(cv, 'LA PROPINA', tx, 48, NEONOFF, 1.4, lit=0, mirror=True)
    cv.hline(tx - 2, tx + w + 1, 55, SLATE, 1.6, lit=0)
    cv.rect(tx + w // 2 - 3, 56, tx + w // 2 + 3, 59, SLATE, 1.8, lit=0)
    # reflex del vidre
    cv.tint(x0 + 3, y0 + 3, x1 - 3, y1 - 3, (255, 250, 230),
            lambda x, y: 0.18 if 0 <= (x - x0) - (y1 - y) * 0.6 - 27 < 11 else 0)
    for (a, b, c, d) in ((x0, y0, x1, y0 + 2), (x0, y1 - 2, x1, y1), (x0, y0, x0 + 2, y1), (x1 - 2, y0, x1, y1)):
        cv.rect(a, b, c, d, STEELB, 3.8)
    cv.hline(x0, x1, y0, STEELB, 5.0)
    outline(cv, x0 - 1, y0 - 1, x1 + 1, y1 + 1, STEELB)
    cv.glow(147, 83, 40, (255, 220, 160), 0.18)                          # el sol a la bufanda


def door_day(cv):
    """La porta del carrer, de dia: el pàrquing, un arbre i el sol que entra a terra."""
    x0, y0, x1, y1 = 608, 64, 639, FLOOR_Y
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, DAYSKY, 2.4 + (y - y0) / 35, lit=0)
    for y in range(128, y1 + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, ASPH, 2.0 + (0.6 if (x + y * 3) % 23 == 0 else 0), lit=0)
    cv.hline(x0, x1, 139, [(240, 230, 200)], 0, lit=0)                 # la ratlla del pàrquing
    cv.vline(629, 101, 128, WOOD, 3.0, lit=0)
    cv.vline(630, 101, 128, WOOD, 2.0, lit=0)
    cv.disc(629, 88, 13, 16, HILL, lambda nx, ny: 2.6 - ny + (hr(int(nx * 7), int(ny * 7)) - 0.5), lit=0)
    for (a, b, c, d) in ((x0, y0, x1, y0 + 3), (x0, y0, x0 + 3, y1), (x0, 144, x1, 148)):
        cv.rect(a, b, c, d, STEELB, 4.0)
    cv.hline(x0, x1, y0, STEELB, 5.0)
    cv.rect(x0 + 8, 128, x0 + 21, 133, [(10, 30, 60), (30, 80, 150), (200, 220, 240)], 1.6, lit=0)
    cv.hline(x0 + 9, x0 + 20, 131, [(200, 160, 40)], 0, lit=0)
    cv.rect(x0 + 5, 149, x0 + 6, 171, STEELB, lambda x, y: 5.4 if x == x0 + 5 else 3.8)
    text(cv, 'TIBAR', x0 + 9, 156, STEELB, 0, lit=0, flat=(60, 60, 70))
    # el sol de la tarda que entra pel vidre i es posa a terra
    cv.tint(507, FLOOR_Y + 1, 639, 273, (255, 214, 150),
            lambda x, y: 0.22 if 0 <= (x - 608) + (y - FLOOR_Y) * 1.6 < 40 + (y - FLOOR_Y) * 0.6 else 0)


# ─── La tele: la roda de premsa ────────────────────────────────────────────

def tv_frame(cv):
    x0, y0, x1, y1 = TV
    cv.rect(480, 19, 499, y0, STEELB, lambda x, y: 2.8 + (0.8 if x == 480 else 0))   # el braç de la paret
    cv.rect(476, 15, 503, 19, STEELB, 3.4)
    obox(cv, x0, y0, x1, y1, PLASTIC, 1.4)
    cv.hline(x0 + 1, x1 - 1, y0 + 1, PLASTIC, 3.0)
    cv.hline(x0 + 2, x1 - 2, y1 - 2, PLASTIC, 2.2)
    text(cv, 'KOLOR', (x0 + x1 - text_width('KOLOR')) // 2, y1 - 6, PLASTIC, 3.8)
    cv.rect(x1 - 13, y1 - 5, x1 - 10, y1 - 4, [(40, 200, 80)], 0, lit=0)
    cv.darken(x0 + 3, y1 + 1, x1 + 3, y1 + 2, 0.5)


def tv_news(cv, frame=0):
    """El BCMU en roda de premsa: fons amb logos, el banquer al faristol, el rètol i la cinta."""
    sx0, sy0, sx1, sy1 = SCR
    for y in range(sy0, sy1 + 1):
        for x in range(sx0, sx1 + 1):
            spot = max(0, 1 - math.hypot(x - 491, (y - 53) * 1.4) / 61)
            cv.put(x, y, STUDIO, 1.8 + spot * 2.2 + (0.15 if y % 2 else 0), lit=0)
    # el plafó de logos de darrere (com a totes les rodes de premsa)
    for j, ly in enumerate(range(sy0 + 4, sy0 + 44, 11)):
        for lx in range(sx0 + 3 - (j % 2) * 15, sx1, 29):
            if sx0 <= lx and lx + 17 <= sx1:
                text(cv, 'BCMU', lx, ly, STUDIO, 3.6, lit=0)
    # una bandera blava amb estrelles al costat
    cv.vline(sx0 + 16, sy0 + 13, 80, STEELB, 5.0, lit=0)
    cv.put(sx0 + 16, sy0 + 12, BRASS, 5.0, lit=0)
    cv.poly([(sx0 + 17, sy0 + 13), (sx0 + 35, sy0 + 16), (sx0 + 33, sy0 + 37), (sx0 + 17, sy0 + 35)], STUDIO,
            lambda x, y: 4.2 + (0.4 if (x - sx0) % 6 < 2 else 0), lit=0)
    for a in range(0, 360, 30):
        cv.flat(sx0 + 25 + round(5 * math.cos(math.radians(a))), sy0 + 25 + round(5 * math.sin(math.radians(a))),
                (250, 220, 80))
    # el banquer: americana fosca, corbata granat, cabell gris, ulleres; parla i fa que sí
    bx, hy = 491, 45 + (1 if frame % 4 == 2 else 0)
    cv.poly([(bx - 17, 77), (bx - 15, 61), (bx - 5, 57), (bx + 5, 57), (bx + 15, 61), (bx + 17, 77)], SUITN,
            lambda x, y: 2.6 - abs(x - bx) * 0.05, lit=0)
    cv.line(bx - 5, 58, bx - 2, 66, SUITN, 4.0, lit=0)                    # les solapes
    cv.line(bx + 5, 58, bx + 2, 66, SUITN, 4.0, lit=0)
    cv.poly([(bx - 4, 57), (bx + 4, 57), (bx, 65)], [(200, 200, 210), (240, 240, 246)], 1.0, lit=0)   # la camisa
    cv.rect(bx, 59, bx + 1, 67, TIE, lambda x, y: 1.6 + (0.6 if x == bx else 0), lit=0)
    cv.put(bx - 9, 62, [(240, 210, 110)], 0, lit=0)                       # el pin del banc
    cv.disc(bx, hy + 4, 6, 7.2, FACE, lambda nx, ny: 2.2 - nx * 0.6 - ny * 0.3, lit=0)
    cv.put(bx - 6, hy + 4, FACE, 1.6, lit=0)                              # les orelles
    cv.put(bx + 6, hy + 4, FACE, 1.2, lit=0)
    cv.disc(bx, hy - 1, 6, 3.2, [(70, 70, 80), (140, 140, 150), (190, 190, 200)], lambda nx, ny: 1.4 - ny * 0.4, lit=0)
    cv.hline(bx - 4, bx - 1, hy + 4, [(20, 20, 24)], 0, lit=0)
    cv.hline(bx + 1, bx + 4, hy + 4, [(20, 20, 24)], 0, lit=0)
    cv.put(bx - 3, hy + 5, [(200, 220, 240)], 0, lit=0)                   # el reflex de les ulleres
    cv.hline(bx - 2, bx + 2, hy + 8 + (frame % 2), [(110, 50, 44)], 0, lit=0)   # parla
    # el faristol, amb el logo i els micròfons
    cv.poly([(bx - 16, 67), (bx + 16, 67), (bx + 13, 80), (bx - 13, 80)],
            [(30, 30, 36), (70, 70, 80), (130, 130, 140), (200, 200, 210)],
            lambda x, y: 2.4 - (0.6 if y > 69 else -0.4), lit=0)
    text(cv, 'BCMU', bx - 8, 72, STUDIO, 0, lit=0, flat=(240, 210, 110))
    for mx, top in ((bx - 5, 61), (bx + 4, 60), (bx + 8, 63)):
        cv.line(mx, top, bx + (mx - bx) // 2, 67, [(10, 10, 12), (40, 40, 44)], 1.0, lit=0)
        cv.flat(mx, top, (20, 20, 22))
        cv.flat(mx, top - 1, (40, 40, 44))
    # «EN DIRECTE», amb el punt que fa pampallugues
    cv.rect(sx0 + 1, sy0 + 1, sx0 + 50, sy0 + 8, NEWSRED, 2.6, lit=0)
    if frame % 4 < 2:
        cv.rect(sx0 + 3, sy0 + 3, sx0 + 5, sy0 + 5, [(255, 250, 250)], 0, lit=0)
    text(cv, 'EN DIRECTE', sx0 + 8, sy0 + 2, NEWSRED, 0, lit=0, flat=(250, 246, 240))
    # el rètol: «EL SISTEMA / HA RESISTIT»
    ly0 = 79
    cv.rect(sx0, ly0, sx1, ly0 + 16, [(220, 222, 228), (244, 244, 248)], 1.6, lit=0)
    cv.rect(sx0, ly0, sx0 + 3, ly0 + 16, NEWSRED, 3.0, lit=0)
    text(cv, 'EL SISTEMA', sx0 + 7, ly0 + 2, STUDIO, 0, lit=0, flat=(14, 20, 50))
    text(cv, 'HA RESISTIT', sx0 + 7, ly0 + 9, STUDIO, 0, lit=0, flat=(14, 20, 50))
    cv.rect(sx1 - 21, ly0 + 3, sx1 - 3, ly0 + 13, STUDIO, 3.0, lit=0)    # el logo de la cadena: «24H»
    text(cv, '24H', sx1 - 17, ly0 + 6, STUDIO, 0, lit=0, flat=(250, 250, 250))
    # la cinta de sota: «CAL MÉS REGULACIÓ»
    cv.rect(sx0, ly0 + 17, sx1, sy1, NEWSRED, 1.2, lit=0)
    cv.hline(sx0, sx1, ly0 + 17, NEWSRED, 3.2, lit=0)
    s = 'CAL MÉS REGULACIÓ'
    text(cv, s, (sx0 + sx1 - text_width(s)) // 2, sy1 - 6, WOOD, 0, lit=0, flat=(255, 226, 110))
    cv.glow((sx0 + sx1) // 2, (sy0 + sy1) // 2, 75, (90, 140, 220), 0.10)


# ─── La barra i la sala ────────────────────────────────────────────────────

def paper_sign(cv):
    """«TORNEM A ESTAR OBERTS», escrit amb retolador en un full, enganxat al frontal de la barra."""
    x0, y0, x1, y1 = 304, 164, 387, 188
    pts = [(x0, y0 + 1), (x1, y0), (x1 + 1, y1), (x0 + 1, y1 + 1)]
    cv.poly(pts, SHEET, lambda x, y: 4.6 - (0.6 if y > y1 - 3 else 0) + (hr(x, y, 4) - 0.5) * 0.15)
    outline_poly(cv, pts, SHEET)
    s1 = 'TORNEM A ESTAR'
    text(cv, s1, (x0 + x1 - text_width(s1)) // 2, y0 + 5, INK, 1.6)
    s = 'OBERTS'
    w = text_width(s)
    sx = (x0 + x1 - w) // 2
    text(cv, s, sx, y0 + 13, NEWSRED, 2.4)
    text(cv, s, sx + 1, y0 + 13, NEWSRED, 2.4)                               # retolador gruixut: dues passades
    cv.line(sx - 1, y0 + 20, sx + w + 3, y0 + 20, NEWSRED, 2.0)              # subratllat
    for ey in (13, 14, 15, 17):                                              # i un signe d'exclamació
        cv.flat(sx + w + 4, y0 + ey, NEWSRED[3])
    for (tx, ty) in ((x0 - 3, y0 - 1), (x1 - 5, y0 - 2)):                    # cinta adhesiva
        cv.rect(tx, ty, tx + 8, ty + 3, YEL, lambda x, y: 3.2 + (0.6 if y == ty else 0))


def bar_extras(cv):
    """Damunt la barra, la festa: gerres de cervesa i una ampolla de cava."""
    for gx in (235, 253, 448):
        cv.rect(gx, 139, gx + 6, 151, BEER, lambda x, y: 2.6 + (1.4 if x == gx + 1 else 0) - (0.6 if x == gx + 6 else 0))
        for by in (143, 147):                                                # les bombolles
            cv.put(gx + 3 + by % 2, by, BEER, 4.6)
        cv.rect(gx, 136, gx + 6, 139, SHEET, lambda x, y: 5.0 - (0.6 if y == 139 else 0))
        cv.vline(gx + 7, 141, 148, SHEET, 3.6)
        cv.vline(gx + 8, 142, 147, SHEET, 2.4)
    # cava
    cv.rect(357, 128, 364, 151, BOTTLES[0], lambda x, y: 1.6 + (1.4 if x == 358 else 0))
    cv.rect(359, 120, 362, 128, BOTTLES[0], 1.6)
    cv.rect(359, 116, 362, 121, BRASS, lambda x, y: 4.0 + (0.6 if x == 359 else 0))
    cv.rect(357, 135, 364, 141, ENAMEL, 4.4)
    cv.hline(358, 363, 138, BRASS, 3.4)


def table_chair(cv, x, y, back=True):
    """Una cadira de bar, de fusta, vista de cara."""
    if back:
        cv.rect(x - 9, y - 29, x + 9, y - 27, WOOD, lambda xx, yy: 4.0 + (0.6 if yy == y - 29 else 0))
        cv.rect(x - 9, y - 19, x + 9, y - 17, WOOD, 3.4)
        for px in (x - 9, x + 8):
            cv.rect(px, y - 29, px + 1, y, WOOD, lambda xx, yy: 3.0 + (0.6 if xx == px else 0))
    cv.rect(x - 12, y, x + 12, y + 4, WOOD, lambda xx, yy: 4.2 if yy == y else 2.6)
    cv.hline(x - 12, x + 12, y + 4, WOOD, 1.0)
    for px in (x - 11, x + 10):
        cv.rect(px, y + 5, px + 1, y + 32, WOOD, lambda xx, yy: 2.2 + (0.6 if xx == px else 0))
    cv.hline(x - 10, x + 10, y + 22, WOOD, 2.0)                              # el travesser de les potes
    cv.darken(x - 12, y + 33, x + 13, y + 36, 0.6)


HEM = 259          # on acaben les estovalles: tapen les cames de qui seu al darrere
T_TOP, T_FRONT = 219, 228
GLASSES = (165, 208, 296, 349, 424, 469, 517)
T_BOTTLES = (187, 317, 448)


def long_table(cv):
    """La taula llarga: tres taules que no lliguen, ajuntades, i cadascuna amb les seves estovalles (de quadres
    vermells, de fil blanc i de paper), que pengen fins gairebé a terra i tapen les cames de qui hi seu."""
    top, front = T_TOP, T_FRONT
    parts = ((149, 272, 'quadres', 0), (273, 408, 'fil', -1), (409, 539, 'paper', 0))
    for x0, x1, kind, dy in parts:
        # les potes: només en surt la punta per sota les estovalles
        for lx in (x0 + 4, x1 - 5):
            cv.rect(lx, HEM, lx + 1, 265, STEELB if kind == 'paper' else WOOD, 1.6)

        def cloth(x, y, lv, kind=kind):
            """Un punt de les estovalles (`lv`: la llum que hi toca)."""
            if kind == 'quadres':
                a, b = (x // 5) % 2, (y // 4) % 2
                if a and b:
                    cv.put(x, y, VICHY, lv - 0.8)
                elif a or b:
                    cv.put(x, y, VICHY, lv + 0.6)
                else:
                    cv.put(x, y, CLOTH, lv + 0.6)
            elif kind == 'fil':
                cv.put(x, y, CLOTH, lv + 0.4 + (hr(x // 2, y // 3, 3) - 0.5) * 0.15
                       + (0.3 if (x * 2 + y) % 11 == 0 else 0))                   # el brodat
            else:
                cv.put(x, y, PAPER, lv + (hr(x // 3, y // 2, 4) - 0.5) * 0.3)

        # damunt: el sobre, en perspectiva
        for y in range(top + dy, front + dy + 1):
            inset = round((front + dy - y) * 4 / max(1, front - top))
            for x in range(x0 - 1 + inset, x1 + 2 - inset):
                cloth(x, y, 3.6 + (y - top) * 0.04)
        # la caiguda: plecs verticals i la vora una mica ondulada
        for x in range(x0 - 2, x1 + 3):
            fold = math.sin((x - x0) * 0.41) * 0.45 + math.sin((x - x0) * 0.13 + dy) * 0.25
            hem = HEM - (1 if math.sin(x * 0.34 + dy) > 0.6 else 0)
            for y in range(front + dy + 1, hem + 1):
                lv = 3.0 + fold - (y - front) * 0.02
                if y == front + dy + 1:
                    lv += 0.8                                        # el cantell de la taula, que marca
                cloth(x, y, lv)
            if kind == 'paper' and x % 12 == 0:                      # el paper, amb un estrip
                cv.put(x, hem, PAPER, 1.0)
                cv.put(x + 1, hem - 1, PAPER, 1.4)
        cv.darken(x0 - 2, front + dy + 2, x1 + 2, front + dy + 5, 0.25)  # l'ombra del sobre
        cv.vline(x0 - 2, front + dy + 1, HEM, CLOTH, 0.6)
        cv.vline(x1 + 2, front + dy + 1, HEM, CLOTH, 0.6)
    cv.darken(149, 261, 539, 269, 0.5)                               # l'ombra a terra
    # damunt: gots, plats de pa amb tomàquet, ampolles, un porró
    for i, gx in enumerate(GLASSES):
        if i in (1, 4):                                              # pa amb tomàquet
            cv.disc(gx, top + 4, 12, 3, PORC, lambda nx, ny: 4.6 - ny)
            for k in range(3):
                cv.rect(gx - 8 + k * 5, top + 1, gx - 4 + k * 5, top + 4, BREAD, lambda x, y: 3.4 + (0.6 if y == top + 1 else 0))
                cv.hline(gx - 8 + k * 5, gx - 4 + k * 5, top + 1, TOMATO, 2.6)
                cv.put(gx - 7 + k * 5, top + 2, TOMATO, 3.0)
        else:
            ramp = BEER if i % 2 else SHEET
            cv.rect(gx, top - 9, gx + 4, top + 1, ramp, lambda x, y: 2.6 + (1.2 if x == gx else 0) - (0.4 if x == gx + 4 else 0))
            cv.hline(gx, gx + 4, top - 9, SHEET, 5.0)
            cv.hline(gx + 1, gx + 3, top + 1, ramp, 1.6)
    for bx, r in ((187, BOTTLES[1]), (317, BOTTLES[0]), (448, BOTTLES[3])):
        cv.rect(bx, top - 16, bx + 4, top + 1, r, lambda x, y: 2.0 + (1.4 if x == bx else 0))
        cv.rect(bx + 1, top - 21, bx + 3, top - 16, r, 1.8)
        cv.rect(bx + 1, top - 22, bx + 3, top - 22, [(140, 120, 40), (200, 170, 60)], 1.4)
        cv.rect(bx, top - 10, bx + 4, top - 6, ENAMEL, 3.8)
    # el porró, a la taula del mig
    cv.poly([(376, top - 11), (387, top - 11), (389, top + 1), (373, top + 1)],
            [(40, 10, 20), (90, 20, 40), (160, 70, 90), (220, 200, 210)],
            lambda x, y: 1.6 + (1.4 if x == 377 else 0))
    cv.rect(380, top - 19, 382, top - 11, SHEET, 3.4)
    cv.line(388, top - 7, 396, top - 15, SHEET, 3.6)
    cv.put(396, top - 16, SHEET, 4.6)
    # tovallons
    for nx in (235, 400, 493):
        cv.poly([(nx, top + 3), (nx + 8, top + 1), (nx + 9, top + 5), (nx + 1, top + 7)], SHEET, 4.8)


def cat_basket(cv):
    """La cistella d'en Diu, damunt d'una cadira a la punta de la taula: vímet, la porteta de reixa oberta i una manta."""
    table_chair(cv, 573, 229)
    cx, by = 573, 228
    # el cos de la cistella, de vímet trenat
    for y in range(by - 19, by + 1):
        for x in range(cx - 17, cx + 18):
            nx, ny = (x - cx) / 17, (y - (by - 3)) / 16
            if y > by - 8 or nx * nx + ny * ny <= 1:
                weave = 0.8 if (x // 2 + y // 2) % 2 else -0.2
                cv.put(x, y, WICKER, 3.2 + weave - ny * 0.4 + (0.6 if x < cx - 11 else 0) - (0.8 if x > cx + 12 else 0))
    cv.hline(cx - 17, cx + 17, by - 8, WICKER, 4.6)                         # el cantell de la boca
    # la boca, fosca, amb la manta que treu el cap
    cv.disc(cx - 1, by - 7, 9, 8, [(8, 6, 6), (20, 14, 10), (34, 24, 16)], lambda nx, ny: 0.6 + ny * 0.8)
    cv.poly([(cx - 11, by - 1), (cx + 8, by - 1), (cx + 12, by + 4), (cx - 13, by + 4)], BLANKET,
            lambda x, y: 2.4 + (0.8 if (x + y) % 4 == 0 else 0))
    # la porteta de reixa, oberta cap a fora
    for k in range(5):
        cv.line(cx + 11 + k * 2, by - 15 + k, cx + 11 + k * 2, by + 1, STEELB, 4.2)
    cv.hline(cx + 11, cx + 19, by - 15, STEELB, 4.6)
    cv.hline(cx + 11, cx + 19, by - 7, STEELB, 3.6)
    # l'ansa
    for a in range(200, 341, 6):
        cv.put(round(cx + math.cos(math.radians(a)) * 13), round(by - 17 + math.sin(math.radians(a)) * 9), WICKER, 4.2)
        cv.put(round(cx + math.cos(math.radians(a)) * 13), round(by - 16 + math.sin(math.radians(a)) * 9), WICKER, 2.6)
    cv.line(cx - 17, by + 1, cx + 17, by + 1, WICKER, 1.0)


def tv_cable(cv):
    """El cable de la tele: surt de sota, penja per la paret i s'amaga darrere la barra (el que mossega en Diu)."""
    x0, y0 = TV[2] - 8, TV[3] + 1
    for y in range(y0, BAR_TOP + 2):
        x = x0 + round(math.sin((y - y0) / 33 * math.pi) * 3)          # una mica de panxa
        cv.put(x, y, SLATE, 1.6)
        cv.put(x + 1, y, SLATE, 0.6)


def tele_apagada(cv):
    """La tele, apagada (en Diu ha mossegat el cable): la pantalla negra amb un reflex, i el llum verd, apagat."""
    sx0, sy0, sx1, sy1 = SCR
    for y in range(sy0, sy1 + 1):
        for x in range(sx0, sx1 + 1):
            d = (x - sx0) + (y - sy0)
            cv.put(x, y, SLATE, 1.0 + (0.9 if 16 < d < 24 else 0) + (0.5 if 28 < d < 31 else 0)
                   + (hr(x, y, 9) - 0.5) * 0.2, lit=0)
    cv.rect(TV[2] - 13, TV[3] - 5, TV[2] - 10, TV[3] - 4, [(20, 40, 24)], 0, lit=0)


def bg(cv):
    bar_bg(cv)
    window_day(cv)
    door_day(cv)
    tv_cable(cv)
    tv_frame(cv)
    tv_news(cv, 0)
    bar_extras(cv)
    paper_sign(cv)
    table_chair(cv, 128, 229)
    long_table(cv)
    cat_basket(cv)


PROPS = {'tele_apagada': tele_apagada}

# La taula llarga tapa les cames de qui hi seu al darrere (tothom: vegeu FINAL_BAR a room_designs.py).
# El que hi ha damunt la taula i sobresurt per sobre del sobre (gots, ampolles, el porró): també va davant.
_DAMUNT = ([(gx, T_TOP - 10, gx + 4, T_TOP + 2) for i, gx in enumerate(GLASSES) if i not in (1, 4)]
           + [(bx, T_TOP - 23, bx + 4, T_TOP + 2) for bx in T_BOTTLES] + [(373, T_TOP - 20, 397, T_TOP + 2)])
FRONT = {'mask': lambda x, y: (146 <= x <= 542 and T_TOP <= y <= HEM)
                              or any(a <= x <= c and b <= y <= d for a, b, c, d in _DAMUNT),
         'baseline': 267, 'zIndex': 20}


# ─── Animació ───────────────────────────────────────────────────────────────

@lru_cache(maxsize=None)
def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv.img


def _frames():
    base = _base()
    frames = []
    for i in range(16):
        cv = Canvas(light=LIGHT, img=base.copy())
        tv_news(cv, i)
        slot_machine(cv, i)
        frames.append(fast_diff(cv.img, base, (80, 20, 560, FLOOR_Y + 8)))
    return frames


ANIMS = {'tele': {'frames': _frames, 'frameDuration': 260}}


# ─── Geometria (coordenades de 640×360) ─────────────────────────────────────

GEOMETRIA = {
    'things': {},
    'spawns': {'ballester': (235, 259), 'diu': (573, 227), 'iri': (336, 259), 'marcel': (285, 259),
               'neta': (125, 269), 'pons': (491, 259), 'rius': (181, 259), 'tomas': (437, 259), 'vet': (387, 259)},
    'walkable': [(200, 253), (267, 253), (267, 261), (200, 261)],
}
