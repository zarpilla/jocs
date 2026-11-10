"""
El final (els tres finals): una setmana després, el bar La Propina, a la tarda. Cinemàtica, sense res clicable.
Es dibuixa damunt del bar de l'Escena 2 (bar_sala), amb llum de dia:
  - per l'aparador i la porta entra el sol de la tarda; el neó «LA PROPINA», apagat;
  - una tele nova i més grossa: la roda de premsa del BCMU, un banquer al faristol, el rètol «EL SISTEMA HA
    RESISTIT» i, a la cinta de sota, «CAL MÉS REGULACIÓ»;
  - un paper escrit a mà a la barra, «TORNEM A ESTAR OBERTS», amb cinta adhesiva;
  - la taula llarga: tres taules diferents ajuntades, amb gots, ampolles i pa amb tomàquet;
  - a la punta, una cadira amb la cistella d'en Diu (en Diu no: és un personatge). Els personatges seuen darrere la taula (FRONT);
  - el cable de la tele, que penja fins a la barra; i la tele apagada (`tele_apagada`), quan en Diu el mossega.
"""
import math

from hd.pix import Light, Canvas, hr
from hd.rooms.comu import obox, outline, text, text_width, _diff, PLASTIC, SHEET, YEL
from hd.rooms.bar_sala import (bg as bar_bg, slot_machine, WOOD, FORMICA, STEELB, BRASS, ENAMEL, PORC,
                               BOTTLES, FLOOR_Y, SLATE)
from hd.rooms.pis_cuina import outline_poly

DAYSKY = [(70, 96, 130), (100, 130, 166), (136, 166, 196), (176, 196, 214), (216, 214, 206), (240, 222, 186), (252, 236, 200)]
HILL = [(40, 44, 30), (64, 70, 42), (92, 96, 56), (124, 120, 72), (156, 146, 92)]
ASPH = [(40, 40, 46), (64, 64, 70), (92, 92, 96), (124, 122, 122)]
NEONOFF = [(70, 50, 60), (110, 84, 96), (150, 120, 130)]
STUDIO = [(4, 8, 24), (8, 16, 46), (14, 28, 78), (22, 44, 112), (36, 70, 150), (70, 110, 190), (140, 170, 230)]
NEWSRED = [(60, 6, 10), (120, 14, 20), (180, 26, 30), (220, 50, 44)]
TIE = [(60, 10, 20), (130, 20, 40), (190, 40, 60)]
SUITN = [(6, 6, 12), (12, 12, 22), (20, 22, 36), (32, 36, 54), (50, 56, 78)]
FACE = [(70, 40, 34), (130, 86, 66), (190, 140, 110), (226, 186, 156)]
WICKER = [(30, 18, 8), (60, 38, 16), (96, 64, 28), (136, 96, 44), (176, 132, 66), (210, 170, 98), (236, 206, 140)]
BLANKET = [(40, 30, 60), (70, 56, 100), (110, 90, 150), (160, 140, 200)]
TOMATO = [(60, 10, 8), (120, 24, 14), (180, 50, 26), (220, 90, 50)]
BREAD = [(60, 34, 14), (110, 70, 30), (170, 120, 60), (214, 170, 100), (240, 210, 150)]
BEER = [(60, 30, 4), (130, 76, 10), (200, 130, 24), (240, 190, 60), (255, 236, 170)]
INK = [(10, 14, 40), (20, 30, 80), (30, 46, 120)]

# De dia: el sol de la tarda per l'aparador i per la porta; el fluorescent, encès però sense protagonisme.
LIGHT = Light(ambient=0.9, vignette=(60, 34), floor_fade=(196, 34))
LIGHT.point(240, 58, r=220, k=2.4, squash=1.3, power=1.5)        # el fluorescent
LIGHT.point(110, 50, r=110, k=1.4, squash=1.0, power=1.6)        # l'aparador
LIGHT.point(468, 110, r=120, k=1.6, squash=0.8, power=1.6)       # la porta del carrer
LIGHT.point(368, 56, r=60, k=0.6, squash=1.0, power=2.0)         # la tele

TV = (322, 22, 412, 87)                       # la tele nova (tapa la vella)
SCR = (TV[0] + 3, TV[1] + 3, TV[2] - 3, TV[3] - 7)


# ─── La paret del fons, de dia ─────────────────────────────────────────────

def window_day(cv):
    """L'aparador de tarda: cel pàl·lid, el talús amb herba seca, l'autopista i el neó apagat."""
    x0, y0, x1, y1 = 78, 20, 140, 60
    for y in range(y0 + 2, y1 - 1):
        for x in range(x0 + 2, x1 - 1):
            cv.put(x, y, DAYSKY, 2.2 + (y - y0) / 12, lit=0)
    for x in range(x0 + 2, x1 - 1):
        top = 48 - int(3 * math.sin(x / 9))
        for y in range(top, y1 - 1):
            cv.put(x, y, HILL, 2.2 + (hr(x // 2, y // 2) - 0.5) * 0.8 - (y - top) * 0.15, lit=0)
    cv.rect(x0 + 2, 53, x1 - 2, 55, ASPH, 1.6, lit=0)                  # el carril de servei
    cv.hline(x0 + 2, x1 - 2, 54, ASPH, 3.2, lit=0)
    for lx in (88, 112, 134):                                            # fanals, apagats
        cv.vline(lx, 30, 47, ASPH, 1.0, lit=0)
        cv.hline(lx, lx + 3, 30, ASPH, 1.0, lit=0)
    # un camió blanc que passa
    cv.rect(118, 44, 132, 51, SHEET, 4.4, lit=0)
    cv.rect(114, 46, 117, 51, NEWSRED, 2.4, lit=0)
    cv.flat(119, 52, (20, 20, 24))
    cv.flat(129, 52, (20, 20, 24))
    # el neó, apagat: tubs grisos, del revés
    w = text_width('LA PROPINA')
    text(cv, 'LA PROPINA', (x0 + x1 - w) // 2, 36, NEONOFF, 1.4, lit=0, mirror=True)
    # reflex del vidre
    cv.tint(x0 + 2, y0 + 2, x1 - 2, y1 - 2, (255, 250, 230),
            lambda x, y: 0.18 if 0 <= (x - x0) - (y1 - y) * 0.6 - 20 < 8 else 0)
    for (a, b, c, d) in ((x0, y0, x1, y0 + 1), (x0, y1 - 1, x1, y1), (x0, y0, x0 + 1, y1), (x1 - 1, y0, x1, y1)):
        cv.rect(a, b, c, d, STEELB, 3.8)
    outline(cv, x0 - 1, y0 - 1, x1 + 1, y1 + 1, STEELB)
    cv.glow(110, 62, 30, (255, 220, 160), 0.18)                         # el sol a la bufanda


def door_day(cv):
    """La porta del carrer, de dia: el pàrquing, un arbre i el sol que entra a terra."""
    x0, y0, x1, y1 = 456, 48, 479, FLOOR_Y
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, DAYSKY, 2.4 + (y - y0) / 26, lit=0)
    for y in range(96, y1 + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, ASPH, 2.0 + (0.6 if (x + y * 3) % 19 == 0 else 0), lit=0)
    cv.hline(x0, x1, 104, [(240, 230, 200)], 0, lit=0)                 # la ratlla del pàrquing
    cv.disc(472, 66, 10, 12, HILL, lambda nx, ny: 2.6 - ny + (hr(int(nx * 5), int(ny * 5)) - 0.5), lit=0)
    cv.vline(472, 76, 96, WOOD, 3.0, lit=0)
    for (a, b, c, d) in ((x0, y0, x1, y0 + 2), (x0, y0, x0 + 2, y1), (x0, 108, x1, 111)):
        cv.rect(a, b, c, d, STEELB, 4.0)
    cv.rect(x0 + 6, 96, x0 + 16, 100, [(10, 30, 60), (30, 80, 150), (200, 220, 240)], 1.6, lit=0)
    cv.vline(x0 + 4, 112, 128, STEELB, 5.4)
    # el sol de la tarda que entra pel vidre i es posa a terra
    cv.tint(380, FLOOR_Y + 1, 479, 205, (255, 214, 150),
            lambda x, y: 0.22 if 0 <= (x - 456) + (y - FLOOR_Y) * 1.6 < 30 + (y - FLOOR_Y) * 0.6 else 0)


# ─── La tele: la roda de premsa ────────────────────────────────────────────

def tv_frame(cv):
    x0, y0, x1, y1 = TV
    cv.rect(360, 14, 374, y0, STEELB, 2.8)                              # el braç de la paret
    obox(cv, x0, y0, x1, y1, PLASTIC, 1.4)
    cv.hline(x0 + 1, x1 - 1, y0 + 1, PLASTIC, 3.0)
    cv.rect(x1 - 10, y1 - 4, x1 - 8, y1 - 3, [(40, 200, 80)], 0, lit=0)
    cv.darken(x0 + 2, y1 + 1, x1 + 2, y1 + 1, 0.5)


def tv_news(cv, frame=0):
    """El BCMU en roda de premsa: fons amb logos, el banquer al faristol, el rètol i la cinta."""
    sx0, sy0, sx1, sy1 = SCR
    for y in range(sy0, sy1 + 1):
        for x in range(sx0, sx1 + 1):
            spot = max(0, 1 - math.hypot(x - 368, (y - 40) * 1.4) / 46)
            cv.put(x, y, STUDIO, 1.8 + spot * 2.2 + (0.15 if y % 2 else 0), lit=0)
    # el plafó de logos de darrere (com a totes les rodes de premsa)
    for j, ly in enumerate(range(sy0 + 3, sy0 + 34, 8)):
        for lx in range(sx0 + 2 - (j % 2) * 11, sx1, 22):
            if sx0 <= lx and lx + 17 <= sx1:
                text(cv, 'BCMU', lx, ly, STUDIO, 3.6, lit=0)
    # el banquer: americana fosca, corbata granat, cabell gris, ulleres
    bx, hy = 368, 34 + (1 if frame % 4 == 2 else 0)
    cv.poly([(bx - 13, 58), (bx - 11, 46), (bx - 4, 43), (bx + 4, 43), (bx + 11, 46), (bx + 13, 58)], SUITN,
            lambda x, y: 2.6 - abs(x - bx) * 0.06, lit=0)
    cv.poly([(bx - 3, 43), (bx + 3, 43), (bx, 49)], [(200, 200, 210), (240, 240, 246)], 1.0, lit=0)   # la camisa
    cv.rect(bx, 44, bx, 50, TIE, 1.6, lit=0)
    cv.disc(bx, hy + 3, 4.4, 5.4, FACE, lambda nx, ny: 2.2 - nx * 0.6 - ny * 0.3, lit=0)
    cv.disc(bx, hy - 1, 4.6, 2.4, [(70, 70, 80), (140, 140, 150), (190, 190, 200)], 1.4, lit=0)
    cv.hline(bx - 3, bx - 1, hy + 3, [(20, 20, 24)], 0, lit=0)
    cv.hline(bx + 1, bx + 3, hy + 3, [(20, 20, 24)], 0, lit=0)
    cv.hline(bx - 1, bx + 1, hy + 6 + (frame % 2), [(110, 50, 44)], 0, lit=0)   # parla
    # el faristol, amb el logo i els micròfons
    cv.poly([(bx - 12, 50), (bx + 12, 50), (bx + 10, 60), (bx - 10, 60)], [(30, 30, 36), (70, 70, 80), (130, 130, 140), (200, 200, 210)],
            lambda x, y: 2.4 - (0.6 if y > 52 else -0.4), lit=0)
    text(cv, 'BCMU', bx - 8, 53, STUDIO, 0, lit=0, flat=(240, 210, 110))
    for mx, top in ((bx - 4, 46), (bx + 3, 45), (bx + 6, 47)):
        cv.line(mx, top, bx + (mx - bx) // 2, 50, [(10, 10, 12), (40, 40, 44)], 1.0, lit=0)
        cv.flat(mx, top, (20, 20, 22))
    # una bandera blava amb estrelles al costat
    cv.vline(sx0 + 12, sy0 + 10, 60, STEELB, 5.0, lit=0)
    cv.poly([(sx0 + 13, sy0 + 10), (sx0 + 26, sy0 + 12), (sx0 + 25, sy0 + 28), (sx0 + 13, sy0 + 26)], STUDIO, 4.2, lit=0)
    for a in range(0, 360, 60):
        cv.flat(sx0 + 19 + round(3 * math.cos(math.radians(a))), sy0 + 19 + round(3 * math.sin(math.radians(a))), (250, 220, 80))
    # «EN DIRECTE»
    cv.rect(sx0 + 1, sy0 + 1, sx0 + 43, sy0 + 7, NEWSRED, 2.6, lit=0)
    text(cv, 'EN DIRECTE', sx0 + 3, sy0 + 2, NEWSRED, 0, lit=0, flat=(250, 246, 240))
    # el rètol: «EL SISTEMA / HA RESISTIT»
    ly0 = 59
    cv.rect(sx0, ly0, sx1, ly0 + 12, [(220, 222, 228), (244, 244, 248)], 1.6, lit=0)
    cv.rect(sx0, ly0, sx0 + 2, ly0 + 12, NEWSRED, 3.0, lit=0)
    text(cv, 'EL SISTEMA', sx0 + 5, ly0 + 1, STUDIO, 0, lit=0, flat=(14, 20, 50))
    text(cv, 'HA RESISTIT', sx0 + 5, ly0 + 7, STUDIO, 0, lit=0, flat=(14, 20, 50))
    cv.rect(sx1 - 17, ly0 + 2, sx1 - 2, ly0 + 10, STUDIO, 3.0, lit=0)    # el logo de la cadena: «24H»
    text(cv, '24H', sx1 - 15, ly0 + 4, STUDIO, 0, lit=0, flat=(250, 250, 250))
    # la cinta de sota: «CAL MÉS REGULACIÓ»
    cv.rect(sx0, ly0 + 13, sx1, sy1, NEWSRED, 1.2, lit=0)
    s = 'CAL MÉS REGULACIÓ'
    text(cv, s, (sx0 + sx1 - text_width(s)) // 2, sy1 - 5, WOOD, 0, lit=0, flat=(255, 226, 110))
    cv.glow((sx0 + sx1) // 2, (sy0 + sy1) // 2, 56, (90, 140, 220), 0.10)


# ─── La barra i la sala ────────────────────────────────────────────────────

def paper_sign(cv):
    """«TORNEM A ESTAR OBERTS», escrit amb retolador en un full, enganxat al frontal de la barra."""
    x0, y0, x1, y1 = 228, 123, 290, 141
    pts = [(x0, y0 + 1), (x1, y0), (x1 + 1, y1), (x0 + 1, y1 + 1)]
    cv.poly(pts, SHEET, lambda x, y: 4.6 - (0.6 if y > y1 - 2 else 0))
    outline_poly(cv, pts, SHEET)
    text(cv, 'TORNEM A ESTAR', x0 + 3, y0 + 3, INK, 1.6)
    s = 'OBERTS'
    w = text(cv, s, (x0 + x1 - text_width(s)) // 2, y0 + 10, NEWSRED, 2.4)
    cv.line((x0 + x1 - w) // 2, y0 + 16, (x0 + x1 + w) // 2 + 2, y0 + 16, NEWSRED, 2.0)   # subratllat
    cv.flat((x0 + x1 + w) // 2 + 3, y0 + 10, NEWSRED[3])                     # i un signe d'exclamació
    cv.flat((x0 + x1 + w) // 2 + 3, y0 + 11, NEWSRED[3])
    cv.flat((x0 + x1 + w) // 2 + 3, y0 + 12, NEWSRED[3])
    cv.flat((x0 + x1 + w) // 2 + 3, y0 + 14, NEWSRED[3])
    for (tx, ty) in ((x0 - 2, y0 - 1), (x1 - 4, y0 - 2)):                    # cinta adhesiva
        cv.rect(tx, ty, tx + 6, ty + 2, YEL, 3.2)


def bar_extras(cv):
    """Damunt la barra, la festa: gots, una ampolla de cava i un pastís a mig menjar."""
    # gerres de cervesa
    for gx in (176, 190, 336):
        cv.rect(gx, 104, gx + 5, 113, BEER, lambda x, y: 2.6 + (1.4 if x == gx + 1 else 0) - (0.6 if x == gx + 5 else 0))
        cv.rect(gx, 102, gx + 5, 104, SHEET, 5.0)
        cv.vline(gx + 6, 106, 110, SHEET, 3.6)
    # cava
    cv.rect(268, 96, 273, 113, BOTTLES[0], lambda x, y: 1.6 + (1.4 if x == 269 else 0))
    cv.rect(269, 90, 272, 96, BOTTLES[0], 1.6)
    cv.rect(269, 88, 272, 91, BRASS, 4.0)
    cv.rect(268, 101, 273, 105, ENAMEL, 4.4)


def table_chair(cv, x, y, back=True):
    """Una cadira de bar, de fusta, vista de cara."""
    if back:
        cv.rect(x - 7, y - 22, x + 7, y - 20, WOOD, 4.0)
        cv.rect(x - 7, y - 14, x + 7, y - 13, WOOD, 3.4)
        for px in (x - 7, x + 6):
            cv.rect(px, y - 22, px + 1, y, WOOD, 3.0)
    cv.rect(x - 9, y, x + 9, y + 3, WOOD, lambda xx, yy: 4.2 if yy == y else 2.6)
    for px in (x - 8, x + 7):
        cv.rect(px, y + 4, px + 1, y + 24, WOOD, 2.2)
    cv.darken(x - 9, y + 25, x + 10, y + 27, 0.6)


CLOTH = [(70, 66, 62), (120, 116, 108), (170, 166, 156), (210, 206, 196), (236, 232, 222), (250, 248, 240)]
VICHY = [(50, 8, 10), (96, 20, 22), (150, 38, 36), (196, 68, 62), (228, 116, 106), (244, 170, 160)]
PAPER = [(100, 86, 50), (150, 134, 90), (196, 182, 136), (226, 214, 172), (244, 236, 204)]
HEM = 194          # on acaben les estovalles: tapen les cames de qui seu al darrere


def long_table(cv):
    """La taula llarga: tres taules que no lliguen, ajuntades, i cadascuna amb les seves estovalles (de quadres
    vermells, de fil blanc i de paper), que pengen fins gairebé a terra i tapen les cames de qui hi seu."""
    top, front = 164, 171
    parts = ((112, 204, 'quadres', 0), (205, 306, 'fil', -1), (307, 404, 'paper', 0))
    for x0, x1, kind, dy in parts:
        # les potes: només en surt la punta per sota les estovalles
        for lx in (x0 + 3, x1 - 4):
            cv.rect(lx, HEM, lx + 1, 199, STEELB if kind == 'paper' else WOOD, 1.6)

        def cloth(x, y, lv, x0=x0, kind=kind):
            """Un punt de les estovalles (`lv`: la llum que hi toca)."""
            if kind == 'quadres':
                a, b = (x // 4) % 2, (y // 3) % 2
                if a and b:
                    cv.put(x, y, VICHY, lv - 0.8)
                elif a or b:
                    cv.put(x, y, VICHY, lv + 0.6)
                else:
                    cv.put(x, y, CLOTH, lv + 0.6)
            elif kind == 'fil':
                cv.put(x, y, CLOTH, lv + 0.4 + (hr(x // 2, y // 3, 3) - 0.5) * 0.15)
            else:
                cv.put(x, y, PAPER, lv + (hr(x // 3, y // 2, 4) - 0.5) * 0.3)

        # damunt: el sobre, en perspectiva
        for y in range(top + dy, front + dy + 1):
            inset = round((front + dy - y) * 3 / max(1, front - top))
            for x in range(x0 - 1 + inset, x1 + 2 - inset):
                cloth(x, y, 3.6 + (y - top) * 0.05)
        # la caiguda: plecs verticals i la vora una mica ondulada
        for x in range(x0 - 2, x1 + 3):
            fold = math.sin((x - x0) * 0.55) * 0.45 + math.sin((x - x0) * 0.17 + dy) * 0.25
            hem = HEM - (1 if math.sin(x * 0.45 + dy) > 0.6 else 0)
            for y in range(front + dy + 1, hem + 1):
                lv = 3.0 + fold - (y - front) * 0.025
                if y == front + dy + 1:
                    lv += 0.8                                        # el cantell de la taula, que marca
                cloth(x, y, lv)
            if kind == 'paper' and x % 9 == 0:                       # el paper, amb un estrip
                cv.put(x, hem, PAPER, 1.0)
        cv.darken(x0 - 2, front + dy + 2, x1 + 2, front + dy + 4, 0.25)  # l'ombra del sobre
        cv.vline(x0 - 2, front + dy + 1, HEM, CLOTH, 0.6)
        cv.vline(x1 + 2, front + dy + 1, HEM, CLOTH, 0.6)
    cv.darken(112, 196, 404, 202, 0.5)                               # l'ombra a terra
    # damunt: gots, plats de pa amb tomàquet, ampolles, un porró
    for i, gx in enumerate((124, 156, 222, 262, 318, 352, 388)):
        if i in (1, 4):                                              # pa amb tomàquet
            cv.disc(gx, top + 3, 9, 2.4, PORC, lambda nx, ny: 4.6 - ny)
            for k in range(3):
                cv.rect(gx - 6 + k * 4, top + 1, gx - 3 + k * 4, top + 3, BREAD, 3.4)
                cv.hline(gx - 6 + k * 4, gx - 3 + k * 4, top + 1, TOMATO, 2.6)
        else:
            cv.rect(gx, top - 7, gx + 3, top + 1, BEER if i % 2 else SHEET, lambda x, y: 2.6 + (1.2 if x == gx else 0))
            cv.hline(gx, gx + 3, top - 7, SHEET, 5.0)
    for bx, r in ((140, BOTTLES[1]), (238, BOTTLES[0]), (336, BOTTLES[3])):
        cv.rect(bx, top - 12, bx + 3, top + 1, r, lambda x, y: 2.0 + (1.4 if x == bx else 0))
        cv.rect(bx + 1, top - 16, bx + 2, top - 12, r, 1.8)
    # el porró, a la taula del mig
    cv.poly([(282, top - 8), (290, top - 8), (292, top + 1), (280, top + 1)], [(40, 10, 20), (90, 20, 40), (160, 70, 90), (220, 200, 210)],
            lambda x, y: 1.6 + (1.4 if x == 283 else 0))
    cv.rect(285, top - 14, 287, top - 8, SHEET, 3.4)
    cv.line(291, top - 5, 297, top - 11, SHEET, 3.6)
    # tovallons
    for nx in (176, 300, 370):
        cv.poly([(nx, top + 2), (nx + 6, top + 1), (nx + 7, top + 4), (nx + 1, top + 5)], SHEET, 4.8)


def cat_basket(cv):
    """La cistella d'en Diu, damunt d'una cadira a la punta de la taula: vímet, la porteta de reixa oberta i una manta."""
    table_chair(cv, 430, 172)
    cx, by = 430, 171
    # el cos de la cistella, de vímet trenat
    for y in range(by - 14, by + 1):
        for x in range(cx - 13, cx + 14):
            nx, ny = (x - cx) / 13, (y - (by - 2)) / 12
            if y > by - 6 or nx * nx + ny * ny <= 1:
                weave = 0.8 if (x // 2 + y // 2) % 2 else -0.2
                cv.put(x, y, WICKER, 3.2 + weave - ny * 0.4 + (0.6 if x < cx - 8 else 0) - (0.8 if x > cx + 9 else 0))
    # la boca, fosca, amb la manta que treu el cap
    cv.disc(cx - 1, by - 5, 7, 6, [(8, 6, 6), (20, 14, 10), (34, 24, 16)], lambda nx, ny: 0.6 + ny * 0.8)
    cv.poly([(cx - 8, by - 1), (cx + 6, by - 1), (cx + 9, by + 3), (cx - 10, by + 3)], BLANKET,
            lambda x, y: 2.4 + (0.8 if (x + y) % 4 == 0 else 0))
    # la porteta de reixa, oberta cap a fora
    for k in range(4):
        cv.line(cx + 8 + k * 2, by - 11 + k, cx + 8 + k * 2, by + 1, STEELB, 4.2)
    cv.hline(cx + 8, cx + 14, by - 11, STEELB, 4.6)
    # l'ansa
    for a in range(200, 341, 8):
        cv.put(round(cx + math.cos(math.radians(a)) * 10), round(by - 13 + math.sin(math.radians(a)) * 7), WICKER, 4.2)
    cv.line(cx - 13, by + 1, cx + 13, by + 1, WICKER, 1.0)


def tv_cable(cv):
    """El cable de la tele: surt de sota, penja per la paret i s'amaga darrere la barra (el que mossega en Diu)."""
    x0, y0 = TV[2] - 6, TV[3] + 1
    for y in range(y0, 113):
        x = x0 + round(math.sin((y - y0) / 25 * math.pi) * 2)          # una mica de panxa
        cv.put(x, y, SLATE, 1.6)
        cv.put(x + 1, y, SLATE, 0.6)


def tele_apagada(cv):
    """La tele, apagada (en Diu ha mossegat el cable): la pantalla negra amb un reflex, i el llum verd, apagat."""
    sx0, sy0, sx1, sy1 = SCR
    for y in range(sy0, sy1 + 1):
        for x in range(sx0, sx1 + 1):
            cv.put(x, y, SLATE, 1.0 + (0.9 if (x - sx0) + (y - sy0) < 18 and (x - sx0) + (y - sy0) > 12 else 0)
                   + (hr(x, y, 9) - 0.5) * 0.2, lit=0)
    cv.rect(TV[2] - 10, TV[3] - 4, TV[2] - 8, TV[3] - 3, [(20, 40, 24)], 0, lit=0)


def bg(cv):
    bar_bg(cv)
    window_day(cv)
    door_day(cv)
    tv_cable(cv)
    tv_frame(cv)
    tv_news(cv, 0)
    bar_extras(cv)
    paper_sign(cv)
    table_chair(cv, 96, 172)
    long_table(cv)
    cat_basket(cv)


PROPS = {'tele_apagada': tele_apagada}

# La taula llarga tapa les cames de qui hi seu al darrere (tothom: vegeu FINAL_BAR a room_designs.py).
# El que hi ha damunt la taula i sobresurt per sobre del sobre (gots, ampolles, el porró): també va davant.
_DAMUNT = ([(gx, 157, gx + 3, 165) for i, gx in enumerate((124, 156, 222, 262, 318, 352, 388)) if i not in (1, 4)]
           + [(bx, 148, bx + 3, 165) for bx in (140, 238, 336)] + [(280, 150, 298, 165)])
FRONT = {'mask': lambda x, y: (110 <= x <= 406 and 164 <= y <= HEM)
                              or any(a <= x <= c and b <= y <= d for a, b, c, d in _DAMUNT),
         'baseline': 200, 'zIndex': 20}


def _frames():
    base = Canvas(light=LIGHT)
    bg(base)
    frames = []
    for i in range(8):
        cv = Canvas(light=LIGHT, img=base.img.copy())
        tv_news(cv, i)
        slot_machine(cv, i)
        frames.append(_diff(cv.img, base.img))
    return frames


ANIMS = {'tele': {'frames': _frames, 'frameDuration': 260}}
