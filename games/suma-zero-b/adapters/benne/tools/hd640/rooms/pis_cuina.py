"""
La cuina del pis (Escena 1, la Vet), de nit, a 640×360: la composició de hd/rooms/pis_cuina.py ×4/3, dibuixada de
nou amb l'estil de la sala de mostra (pis_estudi):
  - és la peça **càlida** del pis: un llum penjant groguenc, rajoles verdes de cuina de lloguer vella i
    terra de **mosaic hidràulic**;
  - la finestra dona al **pati de llums** (roba estesa, la finestra del veí amb la tele, pluja);
  - el **passaplats**, tancat com a l'estudi (vidre glaçat), deixa passar la llum cian de les pantalles de
    l'Iri (a l'estudi, al revés, hi passa la llum càlida de la cuina);
  - detalls: la llimona sola al fruiter, la bomber de la Vet al penjador (l'Escena 3), el plat d'en Diu i
    un pòsit «CLAUS» a la porta (la Vet sempre s'endú la clau de casa).
Animacions: `pluja` (regalims al vidre), `tele` (la tele del veí canvia de pla) i `rellotge` (el 00:00 del
microones).
"""
import math

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from hd.pix import Light, Canvas, W, H, hr
from hd.rooms.comu import obox, outline, cable, text, _diff, PLASTIC, SCREEN, SHEET, GRAYC, YEL, CARD, RED
from hd.rooms.pis_cuina import (PLASTER, TILEW, CREAM, FRIDGEB, WOOD, STEELB, PORC, COFFEE, TILEF, TERRA, SLATE, GLASSA,
                                LEMON, BOMBER, RIB, CYANL, BRICKL, COURT, CLOTH, FRIDGE_IN, TV_SEQ, outline_poly)

FLOOR_Y = 200
TOP_Y = 152        # taulell: el cantell del darrere (contra la paret)
FRONT_Y = 161      # taulell: el cantell del davant

LAMP = (273, 43)
HATCH = (400, 88, 469, 147)
WINDOW = (147, 32, 229, 101)
TVWIN = (165, 77, 179, 93)        # la finestra del veí amb la tele
CLOCK = (56, 131, 63, 135)        # el 00:00 del microones
INK = [(60, 20, 20), (120, 30, 30)]

LIGHT = Light(ambient=-0.5, vignette=(85, 48), floor_fade=(256, 35))
LIGHT.point(LAMP[0], LAMP[1], r=333, k=3.4, squash=1.05, down=True, power=1.5)   # el llum penjant
LIGHT.point(435, 123, r=67, k=0.5, squash=1.0, power=2.0)                         # passaplats (pantalles, a través del vidre)
LIGHT.point(188, 72, r=67, k=0.5, squash=1.0, power=2.0)                          # finestra


def marc(cv, x0, y0, x1, y1, ramp, lvl, t=3):
    """Marc de gruix t."""
    for (a, b, c, d) in ((x0, y0, x1, y0 + t - 1), (x0, y1 - t + 1, x1, y1), (x0, y0, x0 + t - 1, y1), (x1 - t + 1, y0, x1, y1)):
        cv.rect(a, b, c, d, ramp, lvl)


# ─── Paret i terra ──────────────────────────────────────────────────────────

def wall(cv):
    """Arrebossat pintat de color mostassa, vell: taques, una esquerda i el sòcol."""
    for y in range(0, FLOOR_Y):
        for x in range(W):
            n = (hr(x // 3, y // 3) - 0.5) * 0.35 + (hr(x // 15, y // 12, 7) - 0.5) * 0.4
            cv.put(x, y, PLASTER, 2.7 + n)
    # una taca d'humitat al sostre, a sobre de la nevera
    cv.darken(330, 0, 420, 14, lambda x, y: 0.5 * max(0, 1 - math.hypot((x - 375) / 45, y / 14)) ** 0.5)
    # una esquerda que baixa del sostre (entre el llum i la nevera), amb una branca
    x = 389
    for y in range(0, 53):
        x += (1 if hr(y, 3) > 0.62 else -1 if hr(y, 4) > 0.7 else 0)
        cv.put(x, y, PLASTER, 0.8)
        if y == 24:
            bx = x
    for k in range(9):
        cv.put(bx + k, 24 + k // 2 + (1 if hr(k, 8) > 0.6 else 0), PLASTER, 1.2)
    # sòcol de fusta
    cv.rect(0, FLOOR_Y - 8, W - 1, FLOOR_Y - 1, WOOD, 2.2)
    cv.hline(0, W - 1, FLOOR_Y - 8, WOOD, 3.4)
    cv.hline(0, W - 1, FLOOR_Y - 7, WOOD, 2.8)
    cv.hline(0, W - 1, FLOOR_Y, WOOD, 0)


def floor(cv):
    """Mosaic hidràulic en perspectiva: rajola crema amb un cercle i quarts de cercle terracota."""
    for y in range(FLOOR_Y + 1, H):
        dep = (y - FLOOR_Y) / (H - FLOOR_Y)
        v = (y - FLOOR_Y) * 2.1 / (1 + dep * 0.6)
        for x in range(W):
            u = (x - W / 2) / (1 + dep * 0.6) + W / 2
            fu, fv = (u / 29) % 1.0, (v / 29) % 1.0
            if fu < 0.04 or fv < 0.06:
                cv.put(x, y, SLATE, 1.4)                          # junta
                continue
            dc = math.hypot(fu - 0.5, (fv - 0.5))
            dk = min(math.hypot(fu - a, fv - b) for a in (0, 1) for b in (0, 1))
            wear = (hr(int(u // 29), int(v // 29)) - 0.5) * 0.5 + (hr(x // 2, y // 2) - 0.5) * 0.2
            if 0.24 < dc < 0.33:
                cv.put(x, y, TERRA, 2.0 + wear)
            elif dk < 0.2:
                cv.put(x, y, SLATE, 2.4 + wear)
            elif dc < 0.1:
                cv.put(x, y, TERRA, 1.8 + wear)
            else:
                cv.put(x, y, TILEF, 2.9 + wear)
    # la llum del passaplats al terra (cian) i el reflex del llum
    cv.tint(347, FLOOR_Y + 3, 533, 273, (60, 170, 180), lambda x, y: 0.07 * max(0, 1 - abs(x - 435) / 93) * max(0, 1 - (y - 208) / 53))


def backsplash(cv):
    """Rajoles verdes de 12×12 darrere el taulell (de 16 a 280)."""
    x0, x1, y0, y1 = 16, 280, 96, TOP_Y
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if (y - y0) % 12 == 11 or (x - x0) % 12 == 11:
                cv.put(x, y, TILEW, 1.6)
            else:
                tx, ty = (x - x0) // 12, (y - y0) // 12
                gloss = 0.9 if (x - x0) % 12 == 1 and (y - y0) % 12 < 5 else 0
                crack = 1.4 if (tx, ty) == (13, 2) and abs((x - x0) % 12 - (y - y0) % 12) < 1 else 0   # una rajola esquerdada
                cv.put(x, y, TILEW, 3.0 + (hr(tx, ty) - 0.5) * 0.7 + gloss - crack)
    cv.hline(x0, x1, y0 - 1, TILEW, 0.6)
    # l'endoll de la paret (el de la cafetera)
    obox(cv, 123, 131, 133, 144, CREAM, 4.6)
    cv.vline(126, 136, 138, [(20, 16, 14)], 0)
    cv.vline(130, 136, 138, [(20, 16, 14)], 0)


# ─── Mobles ─────────────────────────────────────────────────────────────────

def upper_cabinets(cv):
    for (x0, x1) in ((19, 75), (76, 133)):
        obox(cv, x0, 29, x1, 88, CREAM, 3.4, top=0.6)
        cv.rect(x0 + 4, 33, x1 - 4, 84, CREAM, 3.0)
        outline(cv, x0 + 4, 33, x1 - 4, 84, CREAM)
        cv.hline(x0 + 5, x1 - 5, 34, CREAM, 3.8)
        hx = x1 - 8 if x0 == 19 else x0 + 7
        cv.rect(hx, 69, hx + 1, 80, STEELB, 5.0)
        cv.vline(hx + 2, 70, 80, STEELB, 1.6)
    cv.rect(19, 27, 133, 28, CREAM, 1.4)
    # ombra a les rajoles, a sota dels armaris
    cv.darken(19, 89, 133, 99, lambda x, y: 0.75 - (y - 89) * 0.075)
    # a sobre: un pot de galetes i una ampolla de vi buida
    obox(cv, 32, 11, 53, 27, RED, 2.6)
    cv.rect(35, 13, 51, 16, PORC, 4.0)
    cv.rect(38, 20, 47, 23, PORC, 3.0)
    green = [(6, 16, 10), (14, 34, 20), (24, 56, 32), (40, 86, 50)]
    cv.rect(107, 7, 113, 27, green, 2.0)
    cv.rect(108, 3, 112, 6, green, 1.6)
    cv.rect(108, 0, 112, 2, green, 1.2)
    cv.vline(108, 8, 25, green, 3.6)
    cv.rect(108, 15, 112, 20, [(80, 70, 50), (160, 146, 110)], 1.4)        # l'etiqueta


def window(cv, rain=0, tv=None):
    """Finestra al pati de llums, damunt de l'aigüera."""
    x0, y0, x1, y1 = WINDOW
    # la paret del davant del pati: arrebossat fosc, un baixant i finestres petites de veïns
    for y in range(y0 + 3, y1 - 2):
        for x in range(x0 + 3, x1 - 2):
            cv.put(x, y, COURT, 2.0 + (hr(x // 3, y // 3) - 0.5) * 0.6 + (y - y0) * 0.015, lit=0)
    cv.rect(195, y0 + 3, 197, y1 - 3, COURT, 3.4, lit=0)                         # el baixant
    cv.vline(195, y0 + 3, y1 - 3, COURT, 4.0, lit=0)
    for yy in range(y0 + 11, y1 - 3, 16):
        cv.hline(193, 199, yy, COURT, 4.2, lit=0)
    tv_col, tv_k = tv or ((90, 130, 210), 0.35)                    # tv: (color, força del halo) de la tele del veí
    for (wx0, wy0, wx1, wy1, col) in ((157, 40, 171, 56, (210, 160, 90)), (208, 40, 221, 56, None), TVWIN + (tv_col,), (208, 77, 221, 93, None)):
        cv.rect(wx0 - 1, wy0 - 1, wx1 + 1, wy1 + 1, COURT, 0.6, lit=0)
        cv.hline(wx0 - 2, wx1 + 2, wy1 + 2, COURT, 3.0, lit=0)                  # l'ampit
        if col:
            for y in range(wy0, wy1 + 1):
                for x in range(wx0, wx1 + 1):
                    cv.flat(x, y, col if (x + y) % 5 else tuple(int(c * 0.75) for c in col))
            cv.vline((wx0 + wx1) // 2, wy0, wy1, COURT, 0.5, lit=0)
        else:
            cv.rect(wx0, wy0, wx1, wy1, COURT, 1.0, lit=0)
            for yy in range(wy0, wy1 + 1, 2):                                    # persiana de llibret, tancada
                cv.hline(wx0, wx1, yy, COURT, 1.8, lit=0)
    cv.rect(160, 50, 163, 56, [(60, 40, 20), (120, 80, 40)], 1.0, lit=0)       # una planta a la finestra del veí
    cv.glow(172, 85, 19, (90, 140, 220) if tv is None else tv_col, tv_k)        # el veí mira la tele
    cv.glow(164, 48, 16, (230, 170, 90), 0.3)
    # l'estenedor: una corda amb roba i pinces
    cv.line(x0 + 4, 61, x1 - 4, 65, GRAYC, 3.4, lit=0)
    for i, (cx, w, h) in enumerate(((155, 11, 13), (171, 12, 9), (184, 8, 16), (203, 12, 11))):
        cy = 61 + (cx - x0) * 4 // (x1 - x0)
        cv.rect(cx, cy + 1, cx + w, cy + h, CLOTH[i], lambda x, y: 1.6 + (0.4 if (x + y) % 4 == 0 else 0), lit=0)
        cv.hline(cx, cx + w, cy + 1, CLOTH[i], 2.4, lit=0)
        cv.vline(cx + w, cy + 2, cy + h, CLOTH[i], 0.8, lit=0)
        for px in (cx + 1, cx + w - 1):
            cv.flat(px, cy, (150, 150, 140))
    # pluja: regalims al vidre
    for i in range(19):
        rx = x0 + 5 + int(hr(i, 9) * (x1 - x0 - 10))
        ry = y0 + 5 + int((hr(i, 3) * (y1 - y0) + rain * 8 + i * 4) % (y1 - y0 - 13))
        n = 3 + int(hr(i, 5) * 5)
        for d in range(n):
            cv.tint(rx, ry + d, rx, ry + d, (170, 200, 230), 0.45 if d < n - 1 else 0.7)
    # marc de fusta pintada de blanc (vell) i el travesser
    marc(cv, x0, y0, x1, y1, CREAM, 3.6)
    cv.rect((x0 + x1) // 2 - 1, y0, (x0 + x1) // 2 + 1, y1, CREAM, 3.3)
    cv.vline((x0 + x1) // 2 + 1, y0, y1, CREAM, 2.4)
    outline(cv, x0, y0, x1, y1, CREAM)
    for (px, py) in ((x0 + 6, y0 + 9), (x1 - 9, y1 - 14)):                     # la pintura pelada
        cv.flat(px, py, PLASTER[3])
    obox(cv, x0 - 4, y1, x1 + 4, y1 + 4, CREAM, 4.0)              # ampit
    # un test amb una planta que ha vist dies millors
    obox(cv, 213, y1 - 9, 224, y1, TERRA, 3.0)
    cv.hline(212, 225, y1 - 9, TERRA, 4.0)
    plant = [(20, 24, 8), (40, 50, 14), (70, 80, 20), (110, 110, 40)]
    for i in range(6):
        cv.line(219, y1 - 9, 213 + i * 2.4, y1 - 17 - (i % 2) * 4, plant, 2.2)
    cv.line(222, y1 - 9, 227, y1 - 5, plant, 1.4)                               # una fulla caiguda, groga
    cv.flat(227, y1 - 5, (140, 120, 40))


def counter(cv):
    """Armaris de sota (formica crema), el taulell de fusta i el sòcol."""
    x0, x1 = 16, 277
    # el taulell, vist una mica des de dalt
    cv.poly([(x0, TOP_Y), (x1, TOP_Y), (x1 + 3, FRONT_Y), (x0 - 3, FRONT_Y)], WOOD, lambda x, y: 3.2 + (y - TOP_Y) * 0.09 + (hr(x // 6, 1) - 0.5) * 0.3)
    cv.rect(x0 - 3, FRONT_Y, x1 + 3, FRONT_Y + 3, WOOD, 2.2)
    cv.hline(x0 - 3, x1 + 3, FRONT_Y, WOOD, 4.2)
    cv.hline(x0 - 3, x1 + 3, FRONT_Y + 4, WOOD, 0)
    # portes (la nansa, a l'esquerra o a la dreta)
    doors = [(16, 59, 'r'), (60, 103, 'l'), (104, 144, 'r'), (145, 235, '2'), (236, 277, 'l')]
    for (a, b, side) in doors:
        obox(cv, a, FRONT_Y + 5, b, 211, CREAM, 3.0, top=0.5)
        cv.rect(a + 3, FRONT_Y + 8, b - 3, 208, CREAM, 2.8)                       # el plafó, una mica enfonsat
        cv.hline(a + 3, b - 3, FRONT_Y + 8, CREAM, 2.0)
        cv.vline(b - 3, FRONT_Y + 8, 208, CREAM, 3.6)
        if side == '2':                                                # sota l'aigüera: dues portes
            m = (a + b) // 2
            cv.vline(m, FRONT_Y + 6, 210, CREAM, 0.6)
            for hx in (m - 5, m + 4):
                cv.rect(hx, FRONT_Y + 13, hx + 1, FRONT_Y + 21, STEELB, 4.6)
        else:
            hx = b - 8 if side == 'r' else a + 6
            cv.rect(hx, FRONT_Y + 13, hx + 1, FRONT_Y + 21, STEELB, 4.6)
    # calaixos del primer mòdul (els coberts)
    cv.hline(17, 58, FRONT_Y + 21, CREAM, 0.6)
    cv.rect(33, FRONT_Y + 12, 41, FRONT_Y + 13, STEELB, 4.6)
    # un drap penjat a la nansa de l'aigüera
    cv.rect(186, FRONT_Y + 14, 194, FRONT_Y + 32, [(30, 30, 40), (60, 70, 100), (110, 130, 170), (170, 190, 220)],
            lambda x, y: 2.0 + (0.8 if (y // 3) % 2 else 0) - (0.6 if x > 192 else 0))
    # sòcol, enfonsat
    cv.rect(19, 212, 275, 219, SLATE, 0.8)
    cv.hline(19, 275, 212, SLATE, 0)
    # ombra al terra davant dels armaris
    cv.darken(13, 220, 283, 227, lambda x, y: 0.7 - (y - 220) * 0.1)


def microwave(cv):
    obox(cv, 21, 125, 67, TOP_Y + 2, PLASTIC, 2.4, top=0.8)
    cv.rect(25, 129, 52, TOP_Y - 2, SLATE, 1.6)
    outline(cv, 25, 129, 52, TOP_Y - 2, SLATE)
    cv.hline(28, 49, 132, SLATE, 3.0, lit=0)                          # el reflex del vidre
    cv.line(28, 146, 36, 133, SLATE, 2.4, lit=0)
    cv.rect(*CLOCK, [(20, 40, 20), (40, 120, 60), (80, 220, 110)], 2.0, lit=0)   # 00:00
    for j in range(3):
        cv.hline(56, 63, 139 + j * 4, PLASTIC, 4.0)
    cv.rect(58, 150, 61, 151, PLASTIC, 4.6)                            # el botó d'obrir


def cafetera(cv):
    """Cafetera de goteig: dipòsit, filtre, gerra de vidre amb cafè."""
    x0, x1 = 77, 112
    obox(cv, x0, 117, x1, 128, PLASTIC, 2.6, top=1.0)                # tapa i dipòsit
    cv.rect(x0 + 3, 121, x0 + 10, 125, CYANL, 1.4)                  # el nivell de l'aigua
    obox(cv, x0 + 3, 128, x0 + 11, TOP_Y + 2, PLASTIC, 2.0)         # columna
    obox(cv, x0, TOP_Y - 1, x1, TOP_Y + 4, PLASTIC, 2.4)            # base (placa)
    obox(cv, x0 + 14, 129, x1 - 3, 135, PLASTIC, 2.0)               # porta-filtres
    # la gerra
    cv.poly([(x0 + 15, 137), (x1 - 4, 137), (x1 - 1, TOP_Y - 2), (x0 + 12, TOP_Y - 2)], SHEET, 1.4)
    cv.rect(x0 + 14, 144, x1 - 3, TOP_Y - 3, COFFEE, 2.4)
    cv.hline(x0 + 14, x1 - 3, 144, COFFEE, 3.6)
    cv.vline(x0 + 16, 139, TOP_Y - 4, SHEET, 4.4)
    cv.line(x1 - 1, 139, x1 + 3, 144, PLASTIC, 2.0)
    cv.line(x1 + 3, 144, x1, 149, PLASTIC, 2.0)
    # el llum de la placa (apagat: s'encén al prop del cable)
    cv.rect(x0 + 4, TOP_Y, x0 + 7, TOP_Y + 1, [(30, 6, 6), (60, 12, 12)], 1.0, lit=0)
    # una tassa a tocar
    obox(cv, 120, TOP_Y - 8, 128, TOP_Y, PORC, 4.0)
    cv.line(129, TOP_Y - 6, 130, TOP_Y - 2, PORC, 3.4)
    cv.hline(121, 127, TOP_Y - 7, COFFEE, 1.6)


def sink(cv):
    """Aigüera d'acer, l'aixeta i la pila de plats de nou dies."""
    cv.rect(147, TOP_Y + 1, 229, FRONT_Y - 1, STEELB, 2.8)
    cv.rect(151, TOP_Y + 2, 225, FRONT_Y - 2, STEELB, 1.2)
    cv.vline(188, TOP_Y + 1, FRONT_Y - 1, STEELB, 3.4)
    # aixeta, amb la gota que penja
    cv.rect(185, 139, 189, TOP_Y, STEELB, 4.2)
    cv.line(187, 139, 187, 131, STEELB, 4.6)
    cv.line(187, 131, 200, 131, STEELB, 4.6)
    cv.line(187, 130, 199, 130, STEELB, 5.6)
    cv.line(200, 131, 201, 136, STEELB, 4.4)
    for hx in (180, 194):
        cv.rect(hx - 2, 147, hx + 2, 149, STEELB, 4.0)                          # les manetes
    # la pila: plats (el·lipses amb vora i ombra), del de baix al de dalt, una mica torts
    for i, (px, py, rx, sk) in enumerate(((165, 155, 17, 0), (168, 149, 16, 1), (164, 144, 16, -1), (169, 139, 15, 1),
                                          (167, 133, 13, 0), (208, 155, 16, 0), (205, 149, 15, -1))):
        cv.disc(px, py + 1, rx, 4, PORC, 1.6)                                    # el cantell, a l'ombra
        cv.disc(px + sk, py, rx, 3.5, PORC, lambda nx, ny: 4.6 - ny * 0.8 - nx * 0.4)
        cv.disc(px + sk, py, rx * 0.55, 1.7, PORC, 3.8)                          # el fons del plat
        cv.hline(px + sk - rx + 3, px + sk - rx + 6, py - 2, PORC, 6.0)          # la lluïssor
    # restes de menjar (tomàquet, formatge) als plats
    for (x, y, c) in ((169, 133, (160, 50, 30)), (163, 139, (150, 46, 28)), (208, 149, (200, 160, 60)), (172, 144, (150, 46, 28)),
                      (203, 149, (150, 46, 28))):
        cv.flat(x, y, c)
        cv.flat(x + 1, y, c)
        cv.flat(x + 1, y + 1, tuple(int(v * 0.7) for v in c))
    # la paella, recolzada damunt dels plats, amb el mànec en l'aire
    cv.disc(211, 141, 12, 4, SLATE, lambda nx, ny: 2.6 - ny * 1.2)
    cv.disc(211, 141, 9, 3, SLATE, 1.2)
    cv.line(221, 140, 237, 128, SLATE, 3.0)
    cv.line(222, 141, 237, 129, SLATE, 1.6)
    cv.line(234, 130, 239, 126, WOOD, 3.4)
    # una tassa a dalt de tot, i una forquilla clavada
    obox(cv, 161, 123, 171, 132, RED, 3.0)
    cv.line(172, 124, 174, 129, RED, 2.6)
    cv.line(179, 124, 181, 133, STEELB, 5.0)
    for k in range(3):
        cv.flat(178 + k, 122 + (k % 2), STEELB[5])


def fruit_bowl(cv):
    """El fruiter, amb una sola llimona (COMPTE, LLIMONA)."""
    cv.disc(257, TOP_Y - 4, 15, 5, PORC, lambda nx, ny: 3.8 - ny * 1.2)
    cv.rect(244, TOP_Y - 4, 271, TOP_Y - 3, PORC, 2.0)
    cv.disc(261, TOP_Y - 8, 5, 4, LEMON, lambda nx, ny: 3.6 - nx - ny)
    cv.flat(267, TOP_Y - 8, (110, 90, 14))
    cv.flat(259, TOP_Y - 10, LEMON[5])


def fridge(cv):
    """Nevera combi vella, crema, amb imants. S'obre cap a la dreta (frontissa a la dreta)."""
    x0, y0, x1, y1 = 293, 67, 376, 211
    obox(cv, x0, y0, x1, y1, FRIDGEB, 3.6, top=0.6)
    cv.rect(x0 + 1, y0 + 1, x0 + 3, y1 - 1, FRIDGEB, 4.6)                     # cantell il·luminat
    cv.hline(x0 + 1, x1 - 1, 96, FRIDGEB, 1.0)                                 # congelador / nevera
    cv.hline(x0 + 1, x1 - 1, 97, FRIDGEB, 2.6)
    for (a, b) in ((75, 91), (107, 144)):                                      # nanses a l'esquerra
        cv.rect(x0 + 5, a, x0 + 7, b, FRIDGEB, 5.6)
        cv.vline(x0 + 8, a, b, FRIDGEB, 1.6)
    cv.rect(x0 + 30, y1 - 9, x0 + 52, y1 - 7, FRIDGEB, 2.2)                    # la reixeta de baix
    cv.vline(x1 - 3, y0 + 4, y1 - 4, FRIDGEB, 2.8)                            # la goma de la porta
    # imants i papers
    obox(cv, 315, 109, 336, 128, SHEET, 4.0)                                  # una foto de les dues
    cv.rect(317, 112, 333, 124, [(40, 30, 40), (80, 60, 70), (140, 100, 100), (200, 160, 140)], 2.0)
    cv.disc(322, 117, 3, 3, [(20, 10, 30), (54, 28, 76), (100, 60, 128)], 2.0)  # la Vet (lila)
    cv.disc(328, 117, 3, 3, [(4, 22, 26), (16, 66, 72), (50, 140, 140)], 2.0)   # l'Iri (verd)
    cv.rect(320, 121, 330, 124, [(30, 20, 30), (60, 40, 50)], 1.4)
    cv.rect(316, 105, 319, 108, RED, 3.0)
    obox(cv, 344, 115, 360, 131, YEL, 3.0)                                     # pòsit: «PLATS!!»
    for j in range(3):
        cv.hline(347, 347 + 8 + (j * 3) % 5, 119 + j * 4, INK, 1.4, lit=0)
    cv.rect(349, 112, 354, 114, [(10, 30, 60), (30, 80, 150)], 2.4)
    obox(cv, 325, 139, 349, 171, [(60, 10, 10), (120, 20, 20), (180, 40, 36), (220, 80, 60), (240, 200, 160)], 2.6)   # menú de pizzeria
    cv.disc(337, 149, 7, 5, [(80, 40, 10), (170, 110, 40), (220, 170, 80)], 2.0)
    for (px, py) in ((334, 147), (339, 150), (336, 152)):
        cv.flat(px, py, (150, 30, 20))
    for j in range(3):
        cv.hline(329, 345, 159 + j * 3, SHEET, 4.4)
    cv.disc(320, 80, 4, 4, [(10, 30, 60), (30, 80, 150), (80, 140, 210)], 2.6)  # imant del congelador
    cv.disc(355, 83, 3, 3, [(40, 36, 6), (150, 120, 20), (240, 210, 70)], 2.8)
    # a dalt: una capsa de cereals, un paquet de paper de cuina i una caixa de tes
    obox(cv, 301, 45, 325, 66, [(40, 10, 10), (100, 30, 20), (180, 70, 30), (230, 140, 50), (250, 210, 120)], 2.6)
    cv.rect(305, 51, 320, 56, [(250, 230, 160)], 0)
    cv.disc(313, 61, 3, 2, [(80, 40, 10), (200, 150, 60)], 1.4)
    cv.rect(339, 45, 352, 66, SHEET, lambda x, y: 4.6 - abs(x - 343) * 0.26)
    cv.disc(345, 45, 7, 2, SHEET, 5.0)
    cv.disc(345, 45, 2, 1, CARD, 2.0)
    cv.rect(355, 56, 365, 66, [(20, 40, 10), (40, 80, 20), (70, 120, 40), (110, 160, 70)], 2.4)
    cv.hline(355, 365, 56, [(20, 40, 10), (40, 80, 20), (70, 120, 40), (110, 160, 70)], 3.4)
    # potes i ombra a la paret
    cv.rect(x0 + 3, y1 + 1, x0 + 7, y1 + 3, SLATE, 1.0)
    cv.rect(x1 - 7, y1 + 1, x1 - 3, y1 + 3, SLATE, 1.0)
    cv.darken(x1 + 1, y0 + 5, x1 + 8, FLOOR_Y, 0.5)
    cv.darken(x0 - 3, y1 + 1, x1 + 8, y1 + 7, 0.55)


def hatch(cv, frame=0):
    """El passaplats, tancat (com es veu des de l'estudi): dues portetes de vidre glaçat, una a sobre de
    l'altra, que deixen passar el resplendor cian de les pantalles de l'Iri. Obert: el prop passaplats_obert."""
    x0, y0, x1, y1 = HATCH
    mid = (y0 + y1) // 2
    for y in range(y0 + 3, y1 - 2):
        for x in range(x0 + 3, x1 - 2):
            d = math.hypot(x - x0 - 21, (y - y1 + 16) * 1.2) / 67          # les pantalles són avall a l'esquerra
            cv.put(x, y, CYANL, 2.6 - d * 1.6 + (hr(x // 2, y // 2) - 0.5) * 0.3 + (0.6 if (x - y) % 15 == 0 else 0), lit=0)
    cv.rect(x0 + 3, mid - 1, x1 - 3, mid + 1, WOOD, 3.0)                    # el travesser entre les portetes
    outline(cv, x0 + 3, mid - 1, x1 - 3, mid + 1, WOOD)
    for (a, b) in ((mid - 7, mid - 4), (mid + 4, mid + 7)):                  # les nanses
        cv.rect((x0 + x1) // 2 - 4, a, (x0 + x1) // 2 + 4, b, STEELB, 4.4)
        cv.hline((x0 + x1) // 2 - 4, (x0 + x1) // 2 + 4, b, STEELB, 1.6)
    # marc de fusta i ampit
    marc(cv, x0, y0, x1, y1, WOOD, 3.4)
    outline(cv, x0, y0, x1, y1, WOOD)
    obox(cv, x0 - 5, y1, x1 + 5, y1 + 4, WOOD, 3.6)
    cv.glow((x0 + x1) // 2, (y0 + y1) // 2, 61, (70, 200, 210), 0.10)
    # al cantó de l'ampit, el saler i el pebrer
    obox(cv, x1 - 11, y1 - 7, x1 - 5, y1, PORC, 4.2)
    cv.flat(x1 - 8, y1 - 6, (40, 40, 50))
    obox(cv, x1 - 19, y1 - 6, x1 - 14, y1, SLATE, 2.6)


def coats(cv):
    """Penjador amb la bomber de la Vet i una bossa; l'intèrfon i el clauer al costat de la porta."""
    obox(cv, 480, 88, 533, 92, WOOD, 3.0)
    for hx in (488, 507, 525):
        cv.rect(hx, 92, hx + 1, 96, STEELB, 4.4)
    # la bomber (verd oliva, amb el coll i els punys taronja), penjada pel coll: espatlles i mànigues avall
    body = [(493, 99), (509, 99), (520, 109), (519, 152), (484, 152), (483, 109)]
    cv.poly(body, BOMBER, lambda x, y: 3.2 + (0.7 if x < 489 else 0) - (1.0 if x > 513 else 0) + 0.5 * math.sin(y / 5 + x / 9))
    for (pts, lvl) in (([(483, 109), (488, 112), (487, 155), (480, 155)], 2.4), ([(520, 109), (515, 112), (516, 155), (523, 155)], 2.0)):
        cv.poly(pts, BOMBER, lvl)
        outline_poly(cv, pts, BOMBER)
    cv.rect(480, 155, 487, 158, RIB, 2.6)
    cv.rect(516, 155, 523, 158, RIB, 2.2)
    cv.rect(484, 149, 519, 153, RIB, 2.4)
    for x in range(485, 519, 2):                                                                   # el canalé
        cv.vline(x, 149, 153, RIB, 1.6)
    cv.poly([(493, 96), (509, 96), (512, 103), (501, 107), (491, 103)], RIB, 2.8)                  # coll
    cv.line(501, 107, 501, 149, SLATE, 1.2)                                                        # cremallera
    cv.flat(502, 110, STEELB[6])
    cv.rect(491, 125, 496, 128, BOMBER, 1.6)                                                       # butxaques
    cv.rect(507, 125, 512, 128, BOMBER, 1.6)
    cv.rect(486, 112, 491, 115, [(60, 50, 10), (160, 136, 30), (230, 200, 70)], 2.0)               # un pegat a la màniga
    outline_poly(cv, body, BOMBER)
    # bossa de roba
    cv.line(524, 93, 519, 109, CARD, 3.0)
    cv.line(527, 93, 532, 109, CARD, 3.0)
    cv.poly([(517, 109), (533, 109), (536, 139), (515, 139)], SHEET, lambda x, y: 3.0 - (0.8 if x > 531 else 0))
    cv.disc(525, 123, 4, 4, RED, 2.4)                                                     # el logo d'una llibreria
    cv.disc(525, 123, 1.5, 1.5, SHEET, 4.0)
    # intèrfon
    obox(cv, 539, 109, 549, 139, CREAM, 4.2)
    cv.rect(541, 113, 547, 119, SLATE, 1.6)
    for y in range(114, 119, 2):
        cv.hline(542, 546, y, SLATE, 0.6)
    cv.rect(541, 128, 547, 132, CREAM, 2.4)
    cv.line(540, 139, 540, 160, SLATE, 1.4)
    # el clauer: el ganxo és buit si la clau ja és a la butxaca de la Vet (no cal: sempre se l'endú en sortir)
    obox(cv, 536, 149, 549, 155, WOOD, 3.2)
    cv.rect(541, 155, 542, 160, YEL, 4.0)
    cv.disc(542, 163, 2.5, 2.5, YEL, 3.6)
    cv.flat(542, 163, WOOD[1])
    cv.rect(546, 155, 546, 157, STEELB, 4.0)                                              # un altre ganxo, buit
    # interruptor de la llum
    obox(cv, 539, 171, 547, 181, CREAM, 4.4)
    cv.rect(541, 173, 544, 178, CREAM, 3.2)


def door(cv):
    """La porta del pis: fusta envernissada, espiell, cadena, el pòsit «CLAUS» i l'estora."""
    x0, y0, x1, y1 = 557, 56, 621, FLOOR_Y
    obox(cv, x0 - 5, y0 - 5, x1 + 5, y1, CREAM, 3.2)                 # el marc
    obox(cv, x0, y0, x1, y1, WOOD, 3.0, top=0.4)
    for (a, b) in ((y0 + 8, 123), (131, y1 - 8)):                        # plafons
        cv.rect(x0 + 8, a, x1 - 8, b, WOOD, 2.5)
        cv.hline(x0 + 8, x1 - 8, a, WOOD, 1.2)
        cv.vline(x0 + 8, a, b, WOOD, 1.2)
        cv.hline(x0 + 8, x1 - 8, b, WOOD, 3.8)
        cv.vline(x1 - 8, a, b, WOOD, 3.8)
    # veta de la fusta
    for i in range(13):
        gx = x0 + 10 + int(hr(i, 2) * (x1 - x0 - 21))
        cv.line(gx, y0 + 10, gx + (1 if i % 2 else -1), y1 - 10, WOOD, 2.2)
    # pom i pany a l'esquerra (la frontissa és a la dreta)
    cv.disc(x0 + 7, 131, 3.2, 3.2, YEL, lambda nx, ny: 3.6 - nx - ny)
    cv.rect(x0 + 5, 139, x0 + 8, 143, YEL, 2.8)
    cv.vline(x0 + 6, 140, 141, [(20, 14, 6)], 0)
    for hy in (y0 + 12, y1 - 22):                                        # frontisses
        cv.rect(x1 - 1, hy, x1 + 1, hy + 7, YEL, 2.4)
    # cadena
    cv.rect(x0 + 3, 109, x0 + 8, 112, STEELB, 4.0)
    for i in range(7):
        cv.flat(x0 + 8 + i * 2, 112 + (i % 2), (150, 150, 160))
        cv.flat(x0 + 9 + i * 2, 112 + (i % 2), (90, 90, 100))
    obox(cv, x0 + 21, 111, x0 + 25, 115, STEELB, 4.0)
    # espiell
    cv.disc(589, 93, 2.2, 2.2, YEL, 4.0)
    cv.flat(589, 93, (10, 8, 8))
    # pòsit «CLAUS», escrit a mà
    obox(cv, 592, 102, 615, 116, YEL, 3.6)
    cv.hline(593, 614, 103, YEL, 4.4)
    text(cv, 'CLAUS', 594, 106, INK, 1.4, lit=0)
    cv.hline(594, 612, 112, INK, 0.8, lit=0)
    # ombra de la porta i estora
    cv.darken(x1 + 6, y0, x1 + 12, y1, 0.4)
    cv.poly([(552, 203), (627, 203), (635, 216), (544, 216)], [(20, 14, 10), (40, 30, 20), (64, 48, 30), (90, 70, 44), (120, 96, 60)],
            lambda x, y: 2.4 + (0.8 if (x + y) % 4 == 0 else 0))
    for k in range(5):
        cv.hline(549 + k, 629 - k, 205 + k * 2, [(20, 14, 10), (40, 30, 20), (64, 48, 30)], 1.0)
    cv.hline(544, 635, 217, [(10, 6, 4)], 0)


def lamp(cv):
    """Llum penjant: el fil, una pantalla de vidre ambre (de les de tota la vida) i la bombeta."""
    lx, ly = LAMP
    cv.vline(lx, 0, ly - 19, SLATE, 2.4, lit=0)
    cv.rect(lx - 3, ly - 20, lx + 3, ly - 17, STEELB, 3.0, lit=0)
    shade = [(lx - 5, ly - 17), (lx + 5, ly - 17), (lx + 16, ly - 4), (lx + 16, ly - 1), (lx - 16, ly - 1), (lx - 16, ly - 4)]
    cv.poly(shade, GLASSA, lambda x, y: 2.0 + (y - ly + 17) * 0.16 + (1.2 if x < lx - 4 else 0) + (0.6 if (x - lx) % 5 == 0 else 0), lit=0)
    outline_poly(cv, shade, GLASSA)
    cv.hline(lx - 15, lx + 15, ly - 1, LEMON, 5.0, lit=0)
    cv.disc(lx, ly + 1, 4, 3, LEMON, 5.6, lit=0)
    cv.glow(lx, ly + 3, 67, (255, 200, 120), 0.32)
    cv.glow(lx, ly + 3, 16, (255, 240, 200), 0.6)


def floor_things(cv):
    """El plat d'en Diu, el cubell d'escombraries amb pedal i una caixa de pizza vella."""
    # cubell, sota el passaplats
    cv.disc(424, 213, 13, 4, STEELB, 1.2)
    obox(cv, 411, 171, 437, 213, STEELB, 3.0, top=0.8)
    cv.rect(412, 172, 436, 176, STEELB, 4.2)
    cv.hline(412, 436, 177, STEELB, 1.2)
    cv.rect(421, 211, 427, 216, SLATE, 1.6)
    cv.vline(415, 178, 209, STEELB, 4.8)
    cv.vline(416, 178, 209, STEELB, 3.8)
    # el plat d'en Diu (vermell, amb la D)
    cv.disc(261, 229, 13, 5, RED, lambda nx, ny: 3.0 - ny * 1.2)
    cv.disc(261, 228, 8, 2.4, [(30, 20, 10), (60, 40, 20), (90, 64, 30)], 2.0)
    for (px, py) in ((258, 228), (263, 227), (265, 229)):
        cv.flat(px, py, (110, 80, 40))
    for (px, py) in ((259, 231), (259, 232), (259, 233), (260, 231), (261, 232), (260, 233)):   # la D, al cantell
        cv.flat(px, py, (240, 200, 180))
    cv.darken(247, 233, 276, 236, 0.5)
    # una caixa de pizza vella recolzada al costat del cubell (la paperera no tanca)
    cv.poly([(440, 187), (464, 184), (467, 216), (443, 216)], CARD, lambda x, y: 2.4 - (0.6 if x > 460 else 0))
    cv.disc(453, 200, 5, 5, RED, 1.4)
    cv.line(441, 188, 444, 215, CARD, 3.6)


def bg(cv):
    wall(cv)
    floor(cv)
    backsplash(cv)
    upper_cabinets(cv)
    window(cv)
    counter(cv)
    microwave(cv)
    cafetera(cv)
    sink(cv)
    fruit_bowl(cv)
    fridge(cv)
    hatch(cv)
    coats(cv)
    door(cv)
    floor_things(cv)
    lamp(cv)


# ─── Props ──────────────────────────────────────────────────────────────────

def cable_cafetera(cv):
    """La cafetera endollada: el cable fins a l'endoll i el llum vermell de la placa, encès."""
    cable(cv, [(112, 149), (117, 151), (123, 147), (127, 139)], [(4, 4, 8), (20, 20, 26), (40, 40, 50), (70, 70, 80)], 1.8, thick=2)
    cv.rect(125, 135, 131, 140, PLASTIC, 2.6)
    cv.rect(81, TOP_Y, 84, TOP_Y + 1, [(255, 60, 40)], 0, lit=0)
    cv.glow(82, TOP_Y, 8, (255, 60, 40), 0.6)


def nevera_oberta(cv):
    """L'interior de la nevera (la llum de dins) i la porta oberta cap a la dreta, amb les ampolles."""
    x0, y0, x1, y1 = 296, 99, 373, 208
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            d = math.hypot(x - 335, (y - 107) * 0.8) / 93
            cv.put(x, y, FRIDGE_IN, 5.2 - d * 2.6 - (0.8 if x > x1 - 5 else 0), lit=0)
    cv.rect(332, y0, 338, y0 + 2, [(255, 255, 240)], 0, lit=0)                                  # la bombeta de dins
    # prestatges de vidre
    for y in (127, 155, 181):
        cv.hline(x0, x1, y, FRIDGE_IN, 6.2, lit=0)
        cv.hline(x0, x1, y + 1, FRIDGE_IN, 2.6, lit=0)
    # calaix de la verdura
    cv.rect(x0 + 3, 187, x1 - 3, y1 - 1, [(40, 50, 44), (70, 90, 80), (110, 140, 120), (160, 190, 170)], 2.2, lit=0)
    cv.hline(x0 + 3, x1 - 3, 187, [(40, 50, 44), (70, 90, 80), (110, 140, 120), (160, 190, 170)], 3.4, lit=0)
    cv.disc(320, 197, 5, 4, [(20, 40, 10), (40, 80, 20), (80, 130, 40)], 2.0, lit=0)        # un enciam trist
    cv.disc(331, 199, 3, 2, [(60, 30, 6), (140, 80, 20), (210, 140, 50)], 2.0, lit=0)       # una pastanaga
    # el iogurt que ja vota (3r prestatge, a la dreta) i un pot de tomàquet
    obox(cv, 355, 165, 365, 180, PORC, 4.8, lit=0)
    cv.rect(355, 165, 365, 168, [(30, 60, 100), (60, 110, 180)], 1.4, lit=0)
    for (px, py) in ((360, 173), (361, 175), (359, 174)):                                      # floridura
        cv.flat(px, py, (120, 140, 60))
    obox(cv, 301, 165, 315, 180, RED, 3.4, lit=0)
    cv.rect(301, 163, 315, 165, STEELB, 4.0, lit=0)
    # la porta, oberta cap a la dreta, quasi de cantell
    pts = [(376, 96), (405, 88), (405, 216), (376, 211)]
    cv.poly(pts, FRIDGEB, lambda x, y: 3.0 + (x - 376) * 0.04)
    outline_poly(cv, pts, FRIDGEB)
    for y in (128, 160, 192):                                                                  # balconets
        cv.line(379, y, 403, y - 5, FRIDGEB, 5.0)
        cv.line(379, y + 1, 403, y - 4, FRIDGEB, 2.0)
    for k, (bx, by, col) in enumerate(((381, 112, [(10, 30, 10), (20, 70, 30), (40, 120, 60), (100, 180, 120)]),
                                       (389, 141, [(60, 50, 10), (130, 110, 20), (210, 190, 60)]),
                                       (384, 173, PORC))):
        cv.rect(bx, by, bx + 5, by + 17, col, 2.6, lit=0)
        cv.vline(bx + 1, by + 1, by + 16, col, 3.6, lit=0)
        cv.rect(bx + 1, by - 4, bx + 4, by - 1, col, 1.8, lit=0)
    cv.glow(335, 133, 80, (240, 250, 230), 0.25)


def pizza_nevera(cv):
    """La pizza de demà: una capsa de cartró al prestatge de dalt."""
    box = [(304, 112), (355, 109), (355, 120), (304, 123)]
    cv.poly(box, CARD, lambda x, y: 4.2 - (0.8 if y > 117 else 0), lit=0)
    cv.line(304, 117, 355, 115, CARD, 2.0, lit=0)
    outline_poly(cv, box, CARD)
    cv.disc(328, 115, 7, 3, RED, 3.4, lit=0)
    cv.hline(320, 336, 115, [(250, 240, 220)], 0, lit=0)


def tonyina(cv):
    """Pa de motlle i tres llaunes de tonyina (2n prestatge)."""
    cv.poly([(307, 136), (331, 133), (333, 152), (309, 152)], [(60, 40, 20), (120, 84, 40), (180, 136, 80), (220, 186, 130), (240, 224, 190)],
            lambda x, y: 3.2 - (0.6 if x > 327 else 0), lit=0)
    cv.rect(312, 139, 328, 144, [(30, 60, 120), (60, 110, 200), (140, 180, 240)], 1.8, lit=0)   # l'etiqueta de la bossa
    cv.line(310, 136, 314, 133, [(220, 180, 60)], 0, lit=0)                                    # la brida
    for k, (cx, cy) in enumerate(((341, 147), (352, 147), (347, 140))):
        cv.disc(cx, cy, 5, 2.6, STEELB, 5.0, lit=0)
        cv.rect(cx - 5, cy, cx + 5, cy + 4, [(20, 40, 80), (40, 80, 150), (220, 180, 60), (250, 230, 140)], 2.2 if k != 2 else 2.6, lit=0)
        cv.hline(cx - 5, cx + 5, cy + 1, [(220, 180, 60)], 0, lit=0)
        cv.flat(cx + 2, cy - 1, (250, 250, 255))


def passaplats_obert(cv):
    """El passaplats obert: les portetes de vidre, girades cap a la cuina, i per dins l'estudi (maó lila, la
    vora d'un monitor i el resplendor cian)."""
    x0, y0, x1, y1 = HATCH
    for y in range(y0 + 3, y1 - 2):
        for x in range(x0 + 3, x1 - 2):
            row = (y - y0) // 9
            off = 12 if row % 2 else 0
            mortar = (y - y0) % 9 == 8 or (x + off) % 24 == 0
            cv.put(x, y, BRICKL, (1.0 if mortar else 2.0) + (hr((x + off) // 24, row) - 0.5) * 0.6, lit=0)
    cv.rect(x0 + 8, y1 - 27, x0 + 29, y1 - 8, PLASTIC, 1.0, lit=0)
    cv.rect(x0 + 11, y1 - 24, x0 + 27, y1 - 11, SCREEN, 2.8, lit=0)
    for j in range(3):
        cv.hline(x0 + 13, x0 + 16 + (j * 5) % 9, y1 - 21 + j * 4, SCREEN, 4.6, lit=0)
    cv.rect(x0 + 17, y1 - 7, x0 + 19, y1 - 3, PLASTIC, 1.4, lit=0)                         # el peu del monitor
    cv.tint(x0 + 3, y0 + 3, x1 - 3, y1 - 3, (60, 200, 200), lambda x, y: 0.3 * max(0, 1 - math.hypot(x - x0 - 19, y - y1 + 13) / 53))
    # les portetes, obertes contra la paret (amb el vidre glaçat)
    for (a, b) in ((x0 - 16, x0 - 1), (x1 + 1, x1 + 16)):
        for (c, d) in ((y0 + 1, (y0 + y1) // 2 - 1), ((y0 + y1) // 2 + 1, y1 - 1)):
            obox(cv, a, c, b, d, WOOD, 3.0)
            cv.rect(a + 3, c + 3, b - 3, d - 3, CYANL, 1.8, lit=0)
    cv.glow((x0 + x1) // 2, y1 + 8, 53, (70, 200, 210), 0.12)


PROPS = {'passaplats_obert': passaplats_obert, 'cable_cafetera': cable_cafetera, 'nevera_oberta': nevera_oberta, 'pizza_nevera': pizza_nevera, 'tonyina': tonyina}


# ─── Animacions ─────────────────────────────────────────────────────────────

def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv.img


def _frames():
    base = _base()
    frames = []
    for i in range(8):
        cv = Canvas(light=LIGHT, img=base.copy())
        window(cv, rain=i)
        frames.append(_diff(cv.img, base))
    return frames


ANIMS = {'pluja': {'frames': _frames, 'frameDuration': 200}}


def _frames_tele():
    """A l'altra banda del pati, la tele del veí canvia de color amb els plans de la pel·lícula."""
    base = _base()
    frames = []
    box = (149, 64, 196, 108)                                        # només la tele i el seu halo
    for col, k in TV_SEQ:
        cv = Canvas(light=LIGHT, img=base.copy())
        window(cv, tv=None if (col, k) == TV_SEQ[0] else (col, k))
        d = _diff(cv.img, base)
        only = d.copy()
        only.paste((0, 0, 0, 0), (0, 0) + d.size)
        only.paste(d.crop(box), box[:2])
        frames.append(only)
    return frames


def _frames_rellotge():
    """El 00:00 del microones parpelleja (ningú l'ha posat en hora des de l'últim tall de llum)."""
    base = _base()
    cv = Canvas(light=LIGHT, img=base.copy())
    cv.rect(*CLOCK, [(8, 16, 10), (14, 26, 16)], 0.6, lit=0)
    return [_diff(base, base), _diff(cv.img, base)]


ANIMS['tele'] = {'frames': _frames_tele, 'frameDuration': 260}
ANIMS['rellotge'] = {'frames': _frames_rellotge, 'frameDuration': 550}


GEOMETRIA = {
    'things': {
        'cafetera': {'rect': (75, 115, 115, 158), 'walk': (107, 251)},
        'plats': {'rect': (139, 120, 240, 163), 'walk': (187, 251)},
        'nevera': {'rect': (293, 67, 376, 214), 'walk': (333, 251)},
        'pizza_nevera': {'rect': (304, 107, 355, 123), 'walk': (333, 251)},
        'tonyina': {'rect': (307, 133, 355, 153), 'walk': (333, 251)},
        'passaplats': {'rect': (400, 88, 470, 147), 'walk': (435, 251)},
        'porta': {'rect': (552, 51, 626, 214), 'walk': (589, 248)},
    },
    'spawns': {'vet': (240, 259)},
    'walkable': [(19, 236), (621, 236), (632, 271), (8, 271)],
}
