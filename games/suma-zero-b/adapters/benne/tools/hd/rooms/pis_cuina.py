"""
La cuina del pis (Escena 1, la Vet), de nit. Art definitiu, amb l'estil de la sala de mostra (pis_estudi):
  - és la peça **càlida** del pis: un llum penjant groguenc, rajoles verdes de cuina de lloguer vella i
    terra de **mosaic hidràulic**;
  - la finestra dona al **pati de llums** (roba estesa, la finestra del veí amb la tele, pluja);
  - el **passaplats**, tancat com a l'estudi (vidre glaçat), deixa passar la llum cian de les pantalles de
    l'Iri (a l'estudi, al revés, hi passa la llum càlida de la cuina);
  - detalls: la llimona sola al fruiter, la bomber de la Vet al penjador (l'Escena 3), el plat d'en Diu i
    un pòsit «CLAUS» a la porta (la Vet sempre s'endú la clau de casa).
"""
import math

from hd.pix import Light, Canvas, W, H, hr
from hd.rooms.comu import (obox, outline, cable, _diff, PLASTIC, SCREEN, SKY, CITY, SHEET, GRAYC, YEL, CARD, RED)

FLOOR_Y = 150
TOP_Y = 114        # taulell: el cantell del darrere (contra la paret)
FRONT_Y = 121      # taulell: el cantell del davant

PLASTER = [(18, 10, 12), (30, 18, 18), (44, 28, 24), (60, 40, 30), (78, 54, 38), (98, 70, 46), (120, 88, 56), (144, 108, 68), (170, 132, 86)]
TILEW = [(10, 18, 18), (18, 30, 28), (30, 46, 40), (46, 64, 54), (64, 84, 70), (86, 106, 86), (112, 130, 104), (140, 154, 124), (172, 180, 150)]
CREAM = [(22, 18, 16), (40, 32, 26), (62, 52, 40), (88, 76, 58), (116, 102, 78), (146, 130, 100), (174, 158, 124), (200, 186, 148), (224, 212, 176)]
FRIDGEB = [(20, 20, 24), (38, 38, 42), (60, 60, 62), (88, 86, 84), (118, 114, 108), (150, 144, 134), (180, 174, 160), (206, 200, 186), (230, 226, 212), (246, 244, 232)]
WOOD = [(16, 8, 8), (30, 16, 14), (48, 26, 20), (68, 38, 26), (90, 52, 32), (114, 68, 40), (140, 88, 52), (168, 112, 68)]
STEELB = [(10, 12, 16), (20, 24, 30), (34, 38, 46), (50, 56, 66), (70, 78, 90), (96, 104, 116), (130, 138, 150), (176, 182, 190)]
PORC = [(30, 30, 40), (56, 56, 66), (90, 88, 96), (128, 126, 128), (168, 164, 160), (204, 200, 192), (236, 232, 222)]
COFFEE = [(10, 4, 4), (26, 12, 8), (46, 24, 14), (70, 38, 20)]
TILEF = [(14, 8, 8), (26, 16, 14), (40, 26, 20), (58, 40, 30), (78, 56, 42), (100, 74, 56), (124, 96, 72), (150, 120, 90)]
TERRA = [(20, 6, 6), (40, 12, 10), (64, 22, 16), (90, 34, 22), (118, 50, 30), (146, 70, 40)]
SLATE = [(6, 8, 10), (12, 14, 18), (20, 22, 28), (30, 32, 40), (42, 44, 54)]
GLASSA = [(30, 12, 4), (70, 32, 8), (120, 60, 14), (170, 96, 24), (214, 140, 40), (244, 190, 80), (255, 230, 150)]
LEMON = [(50, 40, 6), (100, 82, 10), (160, 136, 20), (210, 186, 40), (240, 222, 90), (254, 246, 170)]
BOMBER = [(10, 12, 6), (20, 24, 12), (34, 40, 20), (50, 58, 28), (68, 78, 38), (90, 100, 54), (116, 126, 72)]
RIB = [(40, 10, 6), (80, 22, 12), (130, 40, 20), (180, 70, 34), (220, 110, 56)]
CYANL = [(4, 20, 26), (8, 40, 50), (14, 70, 84), (24, 110, 124), (50, 160, 170), (120, 220, 220)]
BRICKL = [(16, 10, 24), (24, 16, 36), (34, 24, 50), (46, 32, 64), (60, 44, 80)]
COURT = [(10, 8, 14), (16, 14, 22), (24, 20, 30), (34, 28, 40), (46, 38, 52)]
CLOTH = ([(40, 10, 20), (90, 24, 40), (150, 50, 70), (200, 90, 110)], [(10, 24, 40), (20, 50, 80), (40, 90, 130), (90, 140, 180)],
         [(50, 50, 40), (110, 106, 90), (170, 166, 146), (220, 216, 196)], [(40, 36, 6), (100, 86, 16), (170, 150, 40), (220, 200, 90)])

LAMP = (205, 32)
HATCH = (300, 66, 352, 110)

LIGHT = Light(ambient=-0.5, vignette=(64, 36), floor_fade=(192, 26))
LIGHT.point(LAMP[0], LAMP[1], r=250, k=3.4, squash=1.05, down=True, power=1.5)   # el llum penjant
LIGHT.point(326, 92, r=50, k=0.5, squash=1.0, power=2.0)                          # passaplats (pantalles, a través del vidre)
LIGHT.point(141, 54, r=50, k=0.5, squash=1.0, power=2.0)                          # finestra


# ─── Paret i terra ──────────────────────────────────────────────────────────

def wall(cv):
    """Arrebossat pintat de color mostassa, vell: taques, una esquerda i el sòcol."""
    for y in range(0, FLOOR_Y):
        for x in range(W):
            n = (hr(x // 3, y // 3) - 0.5) * 0.35 + (hr(x // 11, y // 9, 7) - 0.5) * 0.4
            cv.put(x, y, PLASTER, 2.7 + n)
    # una esquerda que baixa del sostre (entre el llum i la nevera)
    x = 292
    for y in range(0, 40):
        x += (1 if hr(y, 3) > 0.62 else -1 if hr(y, 4) > 0.7 else 0)
        cv.put(x, y, PLASTER, 0.8)
    # sòcol de fusta
    cv.rect(0, FLOOR_Y - 6, W - 1, FLOOR_Y - 1, WOOD, 2.2)
    cv.hline(0, W - 1, FLOOR_Y - 6, WOOD, 3.4)
    cv.hline(0, W - 1, FLOOR_Y, WOOD, 0)


def floor(cv):
    """Mosaic hidràulic en perspectiva: rajola crema amb un cercle i quarts de cercle terracota."""
    for y in range(FLOOR_Y + 1, H):
        dep = (y - FLOOR_Y) / (H - FLOOR_Y)
        v = (y - FLOOR_Y) * 2.1 / (1 + dep * 0.6)
        for x in range(W):
            u = (x - W / 2) / (1 + dep * 0.6) + W / 2
            fu, fv = (u / 22) % 1.0, (v / 22) % 1.0
            if fu < 0.05 or fv < 0.07:
                cv.put(x, y, SLATE, 1.4)                          # junta
                continue
            dc = math.hypot(fu - 0.5, (fv - 0.5))
            dk = min(math.hypot(fu - a, fv - b) for a in (0, 1) for b in (0, 1))
            wear = (hr(int(u // 22), int(v // 22)) - 0.5) * 0.5
            if 0.24 < dc < 0.33:
                cv.put(x, y, TERRA, 2.0 + wear)
            elif dk < 0.2:
                cv.put(x, y, SLATE, 2.4 + wear)
            elif dc < 0.1:
                cv.put(x, y, TERRA, 1.8 + wear)
            else:
                cv.put(x, y, TILEF, 2.9 + wear)
    # la llum del passaplats al terra (cian) i el reflex del llum
    cv.tint(260, FLOOR_Y + 2, 400, 205, (60, 170, 180), lambda x, y: 0.07 * max(0, 1 - abs(x - 326) / 70) * max(0, 1 - (y - 156) / 40))


def backsplash(cv):
    """Rajoles verdes de 9×9 darrere el taulell (de 12 a 210)."""
    x0, x1, y0, y1 = 12, 210, 72, TOP_Y
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if (y - y0) % 9 == 8 or (x - x0) % 9 == 8:
                cv.put(x, y, TILEW, 1.6)
            else:
                tx, ty = (x - x0) // 9, (y - y0) // 9
                gloss = 0.9 if (x - x0) % 9 == 1 and (y - y0) % 9 < 4 else 0
                cv.put(x, y, TILEW, 3.0 + (hr(tx, ty) - 0.5) * 0.7 + gloss)
    cv.hline(x0, x1, y0 - 1, TILEW, 0.6)
    # l'endoll de la paret (el de la cafetera)
    obox(cv, 92, 98, 100, 108, CREAM, 4.6)
    cv.flat(95, 102, (20, 16, 14))
    cv.flat(97, 102, (20, 16, 14))


# ─── Mobles ─────────────────────────────────────────────────────────────────

def upper_cabinets(cv):
    for (x0, x1) in ((14, 56), (57, 100)):
        obox(cv, x0, 22, x1, 66, CREAM, 3.4, top=0.6)
        cv.rect(x0 + 3, 25, x1 - 3, 63, CREAM, 3.0)
        outline(cv, x0 + 3, 25, x1 - 3, 63, CREAM)
        hx = x1 - 6 if x0 == 14 else x0 + 5
        cv.rect(hx, 52, hx + 1, 60, STEELB, 5.0)
    cv.rect(14, 20, 100, 21, CREAM, 1.4)
    # ombra a les rajoles, a sota dels armaris
    cv.darken(14, 67, 100, 74, lambda x, y: 0.75 - (y - 67) * 0.1)
    # a sobre: un pot de galetes i una ampolla de vi buida
    obox(cv, 24, 8, 40, 20, RED, 2.6)
    cv.rect(26, 10, 38, 12, PORC, 4.0)
    cv.rect(80, 2, 85, 20, [(6, 16, 10), (14, 34, 20), (24, 56, 32), (40, 86, 50)], 2.0)
    cv.rect(81, 0, 84, 2, [(6, 16, 10), (14, 34, 20), (24, 56, 32), (40, 86, 50)], 1.6)
    cv.vline(81, 5, 18, [(6, 16, 10), (14, 34, 20), (24, 56, 32), (40, 86, 50)], 3.6)


def window(cv, rain=0, tv=None):
    """Finestra al pati de llums, damunt de l'aigüera."""
    x0, y0, x1, y1 = 110, 24, 172, 76
    for y in range(y0 + 3, y1 - 2):
        for x in range(x0 + 3, x1 - 2):
            cv.put(x, y, COURT, 1.4 + (hr(x // 4, y // 4) - 0.5) * 0.3, lit=0)
    # la paret del davant del pati: arrebossat fosc, un baixant i finestres petites de veïns
    for y in range(y0 + 3, y1 - 2):
        for x in range(x0 + 3, x1 - 2):
            cv.put(x, y, COURT, 2.0 + (hr(x // 3, y // 3) - 0.5) * 0.6 + (y - y0) * 0.02, lit=0)
    cv.rect(146, y0 + 3, 148, y1 - 3, COURT, 3.4, lit=0)                         # el baixant
    for yy in range(y0 + 8, y1 - 3, 12):
        cv.hline(145, 149, yy, COURT, 4.2, lit=0)
    tv_col, tv_k = tv or ((90, 130, 210), 0.35)                    # tv: (color, força del halo) de la tele del veí
    for (wx0, wy0, wx1, wy1, col) in ((118, 30, 128, 42, (210, 160, 90)), (156, 30, 166, 42, None), (124, 58, 134, 70, tv_col), (156, 58, 166, 70, None)):
        cv.rect(wx0 - 1, wy0 - 1, wx1 + 1, wy1 + 1, COURT, 0.6, lit=0)
        if col:
            for y in range(wy0, wy1 + 1):
                for x in range(wx0, wx1 + 1):
                    cv.flat(x, y, col if (x + y) % 5 else tuple(int(c * 0.75) for c in col))
            cv.vline((wx0 + wx1) // 2, wy0, wy1, COURT, 0.5, lit=0)
        else:
            cv.rect(wx0, wy0, wx1, wy1, COURT, 1.0, lit=0)
            for yy in range(wy0, wy1 + 1, 2):                                    # persiana de llibret, tancada
                cv.hline(wx0, wx1, yy, COURT, 1.8, lit=0)
    cv.glow(129, 64, 14, (90, 140, 220) if tv is None else tv_col, tv_k)               # el veí mira la tele
    cv.glow(123, 36, 12, (230, 170, 90), 0.3)
    # l'estenedor: una corda amb roba
    cv.line(x0 + 3, 46, x1 - 3, 49, GRAYC, 3.4, lit=0)
    for i, (cx, w, h) in enumerate(((116, 8, 10), (128, 9, 7), (138, 6, 12), (152, 9, 8))):
        cy = 46 + (cx - x0) * 3 // (x1 - x0)
        cv.rect(cx, cy + 1, cx + w, cy + h, CLOTH[i], 1.6, lit=0)
        cv.hline(cx, cx + w, cy + 1, CLOTH[i], 2.4, lit=0)
    # pluja: regalims al vidre
    for i in range(14):
        rx = x0 + 4 + int(hr(i, 9) * (x1 - x0 - 8))
        ry = y0 + 4 + int((hr(i, 3) * (y1 - y0) + rain * 6 + i * 3) % (y1 - y0 - 10))
        for d in range(2 + int(hr(i, 5) * 4)):
            cv.tint(rx, ry + d, rx, ry + d, (170, 200, 230), 0.45)
    # marc de fusta pintada de blanc (vell) i el travesser
    for (a, b, c, d) in ((x0, y0, x1, y0 + 2), (x0, y1 - 2, x1, y1), (x0, y0, x0 + 2, y1), (x1 - 2, y0, x1, y1)):
        cv.rect(a, b, c, d, CREAM, 3.6)
    cv.rect((x0 + x1) // 2 - 1, y0, (x0 + x1) // 2 + 1, y1, CREAM, 3.3)
    outline(cv, x0, y0, x1, y1, CREAM)
    obox(cv, x0 - 3, y1, x1 + 3, y1 + 3, CREAM, 4.0)              # ampit
    # un test amb una planta que ha vist dies millors
    obox(cv, 160, y1 - 7, 168, y1, TERRA, 3.0)
    for i in range(5):
        cv.line(164, y1 - 7, 160 + i * 2, y1 - 13 - (i % 2) * 3, [(20, 24, 8), (40, 50, 14), (70, 80, 20), (110, 110, 40)], 2.2)


def counter(cv):
    """Armaris de sota (formica crema), el taulell de fusta i el sòcol."""
    x0, x1 = 12, 208
    # el taulell, vist una mica des de dalt
    cv.poly([(x0, TOP_Y), (x1, TOP_Y), (x1 + 2, FRONT_Y), (x0 - 2, FRONT_Y)], WOOD, lambda x, y: 3.2 + (y - TOP_Y) * 0.12)
    cv.rect(x0 - 2, FRONT_Y, x1 + 2, FRONT_Y + 2, WOOD, 2.2)
    cv.hline(x0 - 2, x1 + 2, FRONT_Y, WOOD, 4.2)
    cv.hline(x0 - 2, x1 + 2, FRONT_Y + 3, WOOD, 0)
    # portes
    doors = [(12, 44), (45, 77), (78, 108), (109, 176), (177, 208)]
    for (a, b) in doors:
        obox(cv, a, FRONT_Y + 4, b, 158, CREAM, 3.0, top=0.5)
        if b - a > 40:                                             # sota l'aigüera: dues portes
            m = (a + b) // 2
            cv.vline(m, FRONT_Y + 5, 157, CREAM, 0.6)
            for hx in (m - 4, m + 3):
                cv.rect(hx, FRONT_Y + 10, hx + 1, FRONT_Y + 16, STEELB, 4.6)
        else:
            hx = b - 6 if a % 2 == 0 else a + 4
            cv.rect(hx, FRONT_Y + 10, hx + 1, FRONT_Y + 16, STEELB, 4.6)
    # calaixos del primer mòdul (els coberts)
    cv.hline(13, 43, FRONT_Y + 16, CREAM, 0.6)
    cv.rect(25, FRONT_Y + 9, 31, FRONT_Y + 10, STEELB, 4.6)
    # sòcol, enfonsat
    cv.rect(14, 159, 206, 164, SLATE, 0.8)
    cv.hline(14, 206, 159, SLATE, 0)
    # ombra al terra davant dels armaris
    cv.darken(10, 165, 212, 170, lambda x, y: 0.7 - (y - 165) * 0.13)


def microwave(cv):
    obox(cv, 16, 94, 50, TOP_Y + 2, PLASTIC, 2.4, top=0.8)
    cv.rect(19, 97, 39, TOP_Y - 1, SLATE, 1.6)
    outline(cv, 19, 97, 39, TOP_Y - 1, SLATE)
    cv.hline(21, 37, 99, SLATE, 3.0, lit=0)                         # el reflex del vidre
    cv.rect(42, 98, 47, 101, [(20, 40, 20), (40, 120, 60), (80, 220, 110)], 2.0, lit=0)   # 00:00
    for j in range(3):
        cv.hline(42, 47, 104 + j * 3, PLASTIC, 4.0)


def cafetera(cv):
    """Cafetera de goteig: dipòsit, filtre, gerra de vidre amb cafè."""
    x0, x1 = 58, 84
    obox(cv, x0, 88, x1, 96, PLASTIC, 2.6, top=1.0)                # tapa i dipòsit
    obox(cv, x0 + 2, 96, x0 + 8, TOP_Y + 2, PLASTIC, 2.0)          # columna
    obox(cv, x0, TOP_Y - 1, x1, TOP_Y + 3, PLASTIC, 2.4)           # base (placa)
    obox(cv, x0 + 10, 97, x1 - 2, 101, PLASTIC, 2.0)               # porta-filtres
    # la gerra
    cv.poly([(x0 + 11, 103), (x1 - 3, 103), (x1 - 1, TOP_Y - 2), (x0 + 9, TOP_Y - 2)], SHEET, 1.4)
    cv.rect(x0 + 10, 108, x1 - 2, TOP_Y - 3, COFFEE, 2.4)
    cv.vline(x0 + 12, 104, TOP_Y - 4, SHEET, 4.4)
    cv.line(x1 - 1, 104, x1 + 2, 108, PLASTIC, 2.0)
    cv.line(x1 + 2, 108, x1, 112, PLASTIC, 2.0)
    # el llum de la placa (apagat: s'encén al prop del cable)
    cv.rect(x0 + 3, TOP_Y, x0 + 5, TOP_Y + 1, [(30, 6, 6), (60, 12, 12)], 1.0, lit=0)
    # tasses a tocar
    for (cx, lvl) in ((90, 4.0),):
        obox(cv, cx, TOP_Y - 6, cx + 6, TOP_Y, PORC, lvl)
        cv.line(cx + 7, TOP_Y - 5, cx + 8, TOP_Y - 2, PORC, 3.4)


def sink(cv):
    """Aigüera d'acer, l'aixeta i la pila de plats de nou dies."""
    cv.rect(110, TOP_Y + 1, 172, FRONT_Y - 1, STEELB, 2.8)
    cv.rect(113, TOP_Y + 2, 169, FRONT_Y - 2, STEELB, 1.2)
    cv.vline(141, TOP_Y + 1, FRONT_Y - 1, STEELB, 3.4)
    # aixeta
    cv.rect(139, 104, 142, TOP_Y, STEELB, 4.2)
    cv.line(140, 104, 140, 98, STEELB, 4.6)
    cv.line(140, 98, 150, 98, STEELB, 4.6)
    cv.line(150, 98, 151, 102, STEELB, 4.4)
    # la pila: plats (el·lipses amb vora i ombra), del de baix al de dalt, una mica torts
    for i, (px, py, rx, sk) in enumerate(((124, 116, 13, 0), (126, 112, 12, 1), (123, 108, 12, -1), (127, 104, 11, 1),
                                          (125, 100, 10, 0), (156, 116, 12, 0), (154, 112, 11, -1))):
        cv.disc(px, py + 1, rx, 3, PORC, 1.6)                                    # el cantell, a l'ombra
        cv.disc(px + sk, py, rx, 2.6, PORC, lambda nx, ny: 4.6 - ny * 0.8 - nx * 0.4)
        cv.disc(px + sk, py, rx * 0.55, 1.3, PORC, 3.8)                          # el fons del plat
    # restes de menjar (tomàquet, formatge) als plats
    for (x, y, c) in ((127, 100, (160, 50, 30)), (122, 104, (150, 46, 28)), (156, 112, (200, 160, 60)), (129, 108, (150, 46, 28))):
        cv.flat(x, y, c)
        cv.flat(x + 1, y, c)
    # la paella, recolzada damunt dels plats, amb el mànec en l'aire
    cv.disc(158, 106, 9, 3, SLATE, lambda nx, ny: 2.6 - ny * 1.2)
    cv.disc(158, 106, 7, 2, SLATE, 1.2)
    cv.line(166, 105, 178, 96, SLATE, 3.0)
    cv.line(176, 97, 179, 95, WOOD, 3.4)
    # una tassa a dalt de tot, i una forquilla clavada
    obox(cv, 121, 92, 128, 99, RED, 3.0)
    cv.line(129, 93, 130, 96, RED, 2.6)
    cv.line(134, 93, 136, 100, STEELB, 5.0)


def fruit_bowl(cv):
    """El fruiter, amb una sola llimona (COMPTE, LLIMONA)."""
    cv.disc(193, TOP_Y - 3, 11, 4, PORC, lambda nx, ny: 3.8 - ny * 1.2)
    cv.rect(183, TOP_Y - 3, 203, TOP_Y - 2, PORC, 2.0)
    cv.disc(196, TOP_Y - 6, 4, 3, LEMON, lambda nx, ny: 3.6 - nx - ny)
    cv.flat(200, TOP_Y - 6, (110, 90, 14))


def fridge(cv):
    """Nevera combi vella, crema, amb imants. S'obre cap a la dreta (frontissa a la dreta)."""
    x0, y0, x1, y1 = 220, 50, 282, 158
    obox(cv, x0, y0, x1, y1, FRIDGEB, 3.6, top=0.6)
    cv.rect(x0 + 1, y0 + 1, x0 + 2, y1 - 1, FRIDGEB, 4.6)                     # cantell il·luminat
    cv.hline(x0 + 1, x1 - 1, 72, FRIDGEB, 1.0)                                 # congelador / nevera
    cv.hline(x0 + 1, x1 - 1, 73, FRIDGEB, 2.6)
    for (a, b) in ((56, 68), (80, 108)):                                       # nanses a l'esquerra
        cv.rect(x0 + 4, a, x0 + 5, b, FRIDGEB, 5.6)
        cv.vline(x0 + 6, a, b, FRIDGEB, 1.6)
    # imants i papers
    obox(cv, 236, 82, 252, 96, SHEET, 4.0)                                    # una foto de les dues
    cv.rect(238, 84, 250, 93, [(40, 30, 40), (80, 60, 70), (140, 100, 100), (200, 160, 140)], 2.0)
    cv.disc(242, 88, 2, 2, [(20, 10, 30), (54, 28, 76), (100, 60, 128)], 2.0)  # la Vet (lila)
    cv.disc(247, 88, 2, 2, [(4, 22, 26), (16, 66, 72), (50, 140, 140)], 2.0)   # l'Iri (verd)
    cv.rect(237, 79, 239, 81, RED, 3.0)
    obox(cv, 258, 86, 270, 98, YEL, 3.0)                                       # pòsit: «PLATS!!»
    for j in range(3):
        cv.hline(260, 260 + 6 + (j * 3) % 5, 89 + j * 3, [(60, 20, 20), (120, 30, 30)], 1.4, lit=0)
    obox(cv, 244, 104, 262, 128, [(60, 10, 10), (120, 20, 20), (180, 40, 36), (220, 80, 60), (240, 200, 160)], 2.6)   # menú de pizzeria
    cv.disc(253, 112, 5, 4, [(80, 40, 10), (170, 110, 40), (220, 170, 80)], 2.0)
    for j in range(3):
        cv.hline(247, 259, 119 + j * 2, SHEET, 4.4)
    cv.disc(240, 60, 3, 3, [(10, 30, 60), (30, 80, 150), (80, 140, 210)], 2.6)  # imant del congelador
    cv.disc(266, 62, 2, 2, [(40, 36, 6), (150, 120, 20), (240, 210, 70)], 2.8)
    # a dalt: una capsa de cereals i un paquet de paper de cuina
    obox(cv, 226, 34, 244, 49, [(40, 10, 10), (100, 30, 20), (180, 70, 30), (230, 140, 50), (250, 210, 120)], 2.6)
    cv.rect(229, 38, 240, 42, [(250, 230, 160)], 0)
    cv.rect(254, 34, 264, 49, SHEET, lambda x, y: 4.6 - abs(x - 257) * 0.35)
    cv.disc(259, 34, 5, 1.5, SHEET, 5.0)
    cv.disc(259, 34, 1.5, 0.8, CARD, 2.0)
    cv.rect(266, 42, 274, 49, [(20, 40, 10), (40, 80, 20), (70, 120, 40), (110, 160, 70)], 2.4)  # una caixa de tes
    # potes i ombra a la paret
    cv.rect(x0 + 2, y1 + 1, x0 + 5, y1 + 2, SLATE, 1.0)
    cv.rect(x1 - 5, y1 + 1, x1 - 2, y1 + 2, SLATE, 1.0)
    cv.darken(x1 + 1, y0 + 4, x1 + 6, FLOOR_Y, 0.5)
    cv.darken(x0 - 2, y1 + 1, x1 + 6, y1 + 5, 0.55)


def hatch(cv, frame=0):
    """El passaplats, tancat (com es veu des de l'estudi): dues portetes de vidre glaçat, una a sobre de
    l'altra, que deixen passar el resplendor cian de les pantalles de l'Iri. Obert: el prop passaplats_obert."""
    x0, y0, x1, y1 = HATCH
    mid = (y0 + y1) // 2
    flick = 0
    for y in range(y0 + 3, y1 - 2):
        for x in range(x0 + 3, x1 - 2):
            d = math.hypot(x - x0 - 16, (y - y1 + 12) * 1.2) / 50          # les pantalles són avall a l'esquerra
            cv.put(x, y, CYANL, 2.6 - d * 1.6 + flick + (hr(x // 2, y // 2) - 0.5) * 0.3 + (0.6 if (x - y) % 11 == 0 else 0), lit=0)
    cv.rect(x0 + 3, mid - 1, x1 - 3, mid + 1, WOOD, 3.0)                    # el travesser entre les portetes
    outline(cv, x0 + 3, mid - 1, x1 - 3, mid + 1, WOOD)
    for (a, b) in ((mid - 5, mid - 3), (mid + 3, mid + 5)):                  # les nanses
        cv.rect((x0 + x1) // 2 - 3, a, (x0 + x1) // 2 + 3, b, STEELB, 4.4)
    # marc de fusta i ampit
    for (a, b, c, d) in ((x0, y0, x1, y0 + 2), (x0, y1 - 2, x1, y1), (x0, y0, x0 + 2, y1), (x1 - 2, y0, x1, y1)):
        cv.rect(a, b, c, d, WOOD, 3.4)
    outline(cv, x0, y0, x1, y1, WOOD)
    obox(cv, x0 - 4, y1, x1 + 4, y1 + 3, WOOD, 3.6)
    cv.glow((x0 + x1) // 2, (y0 + y1) // 2, 46, (70, 200, 210), 0.10 + flick * 0.1)
    # al cantó de l'ampit, el saler
    obox(cv, x1 - 8, y1 - 5, x1 - 4, y1, PORC, 4.2)


def coats(cv):
    """Penjador amb la bomber de la Vet i una bossa; l'intèrfon i el clauer al costat de la porta."""
    obox(cv, 360, 66, 400, 69, WOOD, 3.0)
    for hx in (366, 380, 394):
        cv.rect(hx, 69, hx + 1, 72, STEELB, 4.4)
    # la bomber (verd oliva, amb el coll i els punys taronja), penjada pel coll: espatlles i mànigues avall
    body = [(370, 74), (382, 74), (390, 82), (389, 114), (363, 114), (362, 82)]
    cv.poly(body, BOMBER, lambda x, y: 3.2 + (0.7 if x < 367 else 0) - (1.0 if x > 385 else 0) + 0.5 * math.sin(y / 4 + x / 7))
    for (pts, lvl) in (([(362, 82), (366, 84), (365, 116), (360, 116)], 2.4), ([(390, 82), (386, 84), (387, 116), (392, 116)], 2.0)):
        cv.poly(pts, BOMBER, lvl)
    cv.rect(360, 116, 365, 118, RIB, 2.6)
    cv.rect(387, 116, 392, 118, RIB, 2.2)
    cv.rect(363, 112, 389, 115, RIB, 2.4)
    cv.poly([(370, 72), (382, 72), (384, 77), (376, 80), (368, 77)], RIB, 2.8)                     # coll
    cv.line(376, 80, 376, 112, SLATE, 1.2)                                                         # cremallera
    cv.rect(368, 94, 372, 96, BOMBER, 1.6)                                                         # butxaques
    cv.rect(380, 94, 384, 96, BOMBER, 1.6)
    outline_poly(cv, body, BOMBER)
    # bossa de roba
    cv.line(393, 70, 389, 82, CARD, 3.0)
    cv.line(395, 70, 399, 82, CARD, 3.0)
    cv.poly([(388, 82), (400, 82), (402, 104), (386, 104)], SHEET, lambda x, y: 3.0 - (0.8 if x > 398 else 0))
    cv.disc(394, 92, 3, 3, RED, 2.4)                                                      # el logo d'una llibreria
    # intèrfon
    obox(cv, 404, 82, 412, 104, CREAM, 4.2)
    cv.rect(406, 85, 410, 89, SLATE, 1.6)
    cv.rect(406, 96, 410, 99, CREAM, 2.4)
    cv.line(405, 104, 405, 120, SLATE, 1.4)
    # el clauer: el ganxo és buit si la clau ja és a la butxaca de la Vet (no cal: sempre se l'endú en sortir)
    obox(cv, 402, 112, 412, 116, WOOD, 3.2)
    cv.rect(406, 116, 407, 120, YEL, 4.0)
    cv.disc(407, 122, 2, 2, YEL, 3.6)
    # interruptor de la llum
    obox(cv, 404, 128, 410, 136, CREAM, 4.4)
    cv.rect(406, 130, 408, 133, CREAM, 3.2)


def outline_poly(cv, pts, ramp):
    for (xa, ya), (xb, yb) in zip(pts, pts[1:] + pts[:1]):
        n = max(abs(xb - xa), abs(yb - ya), 1)
        for i in range(int(n) + 1):
            t = i / n
            cv.flat(round(xa + (xb - xa) * t), round(ya + (yb - ya) * t), ramp[0])


def door(cv):
    """La porta del pis: fusta envernissada, espiell, cadena, el pòsit «CLAUS» i l'estora."""
    x0, y0, x1, y1 = 418, 42, 466, FLOOR_Y
    obox(cv, x0 - 4, y0 - 4, x1 + 4, y1, CREAM, 3.2)                 # el marc
    obox(cv, x0, y0, x1, y1, WOOD, 3.0, top=0.4)
    for (a, b) in ((y0 + 6, 92), (98, y1 - 6)):                          # plafons
        cv.rect(x0 + 6, a, x1 - 6, b, WOOD, 2.5)
        cv.hline(x0 + 6, x1 - 6, a, WOOD, 1.2)
        cv.vline(x0 + 6, a, b, WOOD, 1.2)
        cv.hline(x0 + 6, x1 - 6, b, WOOD, 3.8)
        cv.vline(x1 - 6, a, b, WOOD, 3.8)
    # veta de la fusta
    for i in range(10):
        gx = x0 + 8 + int(hr(i, 2) * (x1 - x0 - 16))
        cv.line(gx, y0 + 8, gx + (1 if i % 2 else -1), y1 - 8, WOOD, 2.2)
    # pom i pany a l'esquerra (la frontissa és a la dreta)
    cv.disc(x0 + 5, 98, 2.4, 2.4, YEL, lambda nx, ny: 3.6 - nx - ny)
    cv.rect(x0 + 4, 104, x0 + 6, 107, YEL, 2.8)
    cv.flat(x0 + 5, 105, (20, 14, 6))
    # cadena
    cv.rect(x0 + 2, 82, x0 + 6, 84, STEELB, 4.0)
    for i in range(6):
        cv.flat(x0 + 6 + i * 2, 84 + (i % 2), (150, 150, 160))
    obox(cv, x0 + 16, 83, x0 + 19, 86, STEELB, 4.0)
    # espiell
    cv.disc(442, 70, 1.6, 1.6, YEL, 4.0)
    cv.flat(442, 70, (10, 8, 8))
    # pòsit «CLAUS»
    obox(cv, 446, 78, 458, 88, YEL, 3.6)
    for k, gx in enumerate((448, 451, 454)):
        cv.vline(gx, 81, 85, [(60, 20, 20), (120, 30, 30)], 1.4, lit=0)
        cv.flat(gx + 1, 81 + k % 2 * 4, (120, 30, 30))
    # ombra de la porta i estora
    cv.darken(x1 + 5, y0, x1 + 9, y1, 0.4)
    cv.poly([(414, 152), (470, 152), (476, 162), (408, 162)], [(20, 14, 10), (40, 30, 20), (64, 48, 30), (90, 70, 44), (120, 96, 60)],
            lambda x, y: 2.4 + (0.8 if (x + y) % 4 == 0 else 0))
    for k in range(4):
        cv.hline(412 + k, 472 - k, 154 + k * 2, [(20, 14, 10), (40, 30, 20), (64, 48, 30)], 1.0)


def lamp(cv):
    """Llum penjant: el fil, una pantalla de vidre ambre (de les de tota la vida) i la bombeta."""
    lx, ly = LAMP
    cv.vline(lx, 0, ly - 14, SLATE, 2.4, lit=0)
    cv.rect(lx - 2, ly - 15, lx + 2, ly - 13, STEELB, 3.0, lit=0)
    cv.poly([(lx - 4, ly - 13), (lx + 4, ly - 13), (lx + 12, ly - 3), (lx + 12, ly - 1), (lx - 12, ly - 1), (lx - 12, ly - 3)],
            GLASSA, lambda x, y: 2.0 + (y - ly + 13) * 0.22 + (1.2 if x < lx - 3 else 0), lit=0)
    outline_poly(cv, [(lx - 4, ly - 13), (lx + 4, ly - 13), (lx + 12, ly - 3), (lx + 12, ly - 1), (lx - 12, ly - 1), (lx - 12, ly - 3)], GLASSA)
    cv.hline(lx - 11, lx + 11, ly - 1, LEMON, 5.0, lit=0)
    cv.disc(lx, ly + 1, 3, 2, LEMON, 5.6, lit=0)
    cv.glow(lx, ly + 2, 50, (255, 200, 120), 0.32)
    cv.glow(lx, ly + 2, 12, (255, 240, 200), 0.6)


def floor_things(cv):
    """El plat d'en Diu i el cubell d'escombraries amb pedal."""
    # cubell, sota el passaplats
    cv.disc(318, 160, 10, 3, STEELB, 1.2)
    obox(cv, 308, 128, 328, 160, STEELB, 3.0, top=0.8)
    cv.rect(309, 129, 327, 132, STEELB, 4.2)
    cv.rect(316, 158, 320, 162, SLATE, 1.6)
    cv.vline(311, 133, 157, STEELB, 4.8)
    # el plat d'en Diu (vermell, amb la D)
    cv.disc(196, 172, 10, 3.5, RED, lambda nx, ny: 3.0 - ny * 1.2)
    cv.disc(196, 171, 6, 1.8, [(30, 20, 10), (60, 40, 20), (90, 64, 30)], 2.0)
    cv.darken(185, 174, 207, 177, 0.5)
    # una caixa de pizza vella recolzada al costat del cubell (la paperera no tanca)
    cv.poly([(330, 140), (348, 138), (350, 162), (332, 162)], CARD, lambda x, y: 2.4 - (0.6 if x > 345 else 0))
    cv.disc(340, 150, 4, 4, RED, 1.4)


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
    cable(cv, [(84, 112), (88, 113), (92, 110), (95, 104)], [(4, 4, 8), (20, 20, 26), (40, 40, 50), (70, 70, 80)], 1.8, thick=1)
    cv.rect(94, 101, 98, 105, PLASTIC, 2.6)
    cv.rect(61, TOP_Y, 63, TOP_Y + 1, [(255, 60, 40)], 0, lit=0)
    cv.glow(62, TOP_Y, 6, (255, 60, 40), 0.6)


FRIDGE_IN = [(40, 44, 40), (70, 76, 70), (110, 116, 108), (150, 156, 146), (190, 196, 184), (224, 228, 216), (244, 248, 236)]


def nevera_oberta(cv):
    """L'interior de la nevera (la llum de dins) i la porta oberta cap a la dreta, amb les ampolles."""
    x0, y0, x1, y1 = 222, 74, 280, 156
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            d = math.hypot(x - 251, (y - 80) * 0.8) / 70
            cv.put(x, y, FRIDGE_IN, 5.2 - d * 2.6 - (0.8 if x > x1 - 4 else 0), lit=0)
    # prestatges de vidre
    for y in (95, 116, 136):
        cv.hline(x0, x1, y, FRIDGE_IN, 6.2, lit=0)
        cv.hline(x0, x1, y + 1, FRIDGE_IN, 2.6, lit=0)
    # calaix de la verdura
    cv.rect(x0 + 2, 140, x1 - 2, y1 - 1, [(40, 50, 44), (70, 90, 80), (110, 140, 120), (160, 190, 170)], 2.2, lit=0)
    cv.disc(240, 148, 4, 3, [(20, 40, 10), (40, 80, 20), (80, 130, 40)], 2.0, lit=0)        # un enciam trist
    # el iogurt que ja vota (3r prestatge, a la dreta) i un pot de tomàquet
    obox(cv, 266, 124, 274, 135, PORC, 4.8, lit=0)
    cv.rect(266, 124, 274, 126, [(30, 60, 100), (60, 110, 180)], 1.4, lit=0)
    cv.flat(270, 130, (120, 140, 60))                                                          # floridura
    cv.flat(271, 131, (100, 130, 50))
    obox(cv, 226, 124, 236, 135, RED, 3.4, lit=0)
    cv.rect(226, 122, 236, 124, STEELB, 4.0, lit=0)
    # la porta, oberta cap a la dreta, quasi de cantell
    pts = [(282, 72), (304, 66), (304, 162), (282, 158)]
    cv.poly(pts, FRIDGEB, lambda x, y: 3.0 + (x - 282) * 0.05)
    outline_poly(cv, pts, FRIDGEB)
    for y in (96, 120, 144):                                                                   # balconets
        cv.line(284, y, 302, y - 4, FRIDGEB, 5.0)
    for k, (bx, by, col) in enumerate(((286, 84, [(10, 30, 10), (20, 70, 30), (40, 120, 60), (100, 180, 120)]),
                                       (292, 106, [(60, 50, 10), (130, 110, 20), (210, 190, 60)]),
                                       (288, 130, PORC))):
        cv.rect(bx, by, bx + 4, by + 13, col, 2.6, lit=0)
        cv.rect(bx + 1, by - 3, bx + 3, by - 1, col, 1.8, lit=0)
    cv.glow(251, 100, 60, (240, 250, 230), 0.25)


def pizza_nevera(cv):
    """La pizza de demà: una capsa de cartró al prestatge de dalt."""
    cv.poly([(228, 84), (266, 82), (266, 90), (228, 92)], CARD, lambda x, y: 4.2 - (0.8 if y > 88 else 0), lit=0)
    cv.line(228, 88, 266, 86, CARD, 2.0, lit=0)
    outline_poly(cv, [(228, 84), (266, 82), (266, 90), (228, 92)], CARD)
    cv.disc(246, 86, 5, 2, RED, 3.4, lit=0)
    cv.hline(240, 252, 86, [(250, 240, 220)], 0, lit=0)


def tonyina(cv):
    """Pa de motlle i tres llaunes de tonyina (2n prestatge)."""
    cv.poly([(230, 102), (248, 100), (250, 114), (232, 114)], [(60, 40, 20), (120, 84, 40), (180, 136, 80), (220, 186, 130), (240, 224, 190)],
            lambda x, y: 3.2 - (0.6 if x > 245 else 0), lit=0)
    cv.rect(234, 104, 246, 108, [(30, 60, 120), (60, 110, 200), (140, 180, 240)], 1.8, lit=0)   # l'etiqueta de la bossa
    for k, (cx, cy) in enumerate(((256, 110), (264, 110), (260, 105))):
        cv.disc(cx, cy, 4, 2, STEELB, 5.0, lit=0)
        cv.rect(cx - 4, cy, cx + 4, cy + 3, [(20, 40, 80), (40, 80, 150), (220, 180, 60), (250, 230, 140)], 2.2 if k != 2 else 2.6, lit=0)
        cv.hline(cx - 4, cx + 4, cy + 1, [(220, 180, 60)], 0, lit=0)


def passaplats_obert(cv):
    """El passaplats obert: les portetes de vidre, girades cap a la cuina, i per dins l'estudi (maó lila, la
    vora d'un monitor i el resplendor cian)."""
    x0, y0, x1, y1 = HATCH
    for y in range(y0 + 3, y1 - 2):
        for x in range(x0 + 3, x1 - 2):
            row = (y - y0) // 7
            off = 9 if row % 2 else 0
            mortar = (y - y0) % 7 == 6 or (x + off) % 18 == 0
            cv.put(x, y, BRICKL, (1.0 if mortar else 2.0) + (hr((x + off) // 18, row) - 0.5) * 0.6, lit=0)
    cv.rect(x0 + 6, y1 - 20, x0 + 22, y1 - 6, PLASTIC, 1.0, lit=0)
    cv.rect(x0 + 8, y1 - 18, x0 + 20, y1 - 8, SCREEN, 2.8, lit=0)
    for j in range(3):
        cv.hline(x0 + 10, x0 + 12 + (j * 5) % 7, y1 - 16 + j * 3, SCREEN, 4.6, lit=0)
    cv.tint(x0 + 3, y0 + 3, x1 - 3, y1 - 3, (60, 200, 200), lambda x, y: 0.3 * max(0, 1 - math.hypot(x - x0 - 14, y - y1 + 10) / 40))
    # les portetes, obertes contra la paret (amb el vidre glaçat)
    for (a, b) in ((x0 - 12, x0 - 1), (x1 + 1, x1 + 12)):
        for (c, d) in ((y0 + 1, (y0 + y1) // 2 - 1), ((y0 + y1) // 2 + 1, y1 - 1)):
            obox(cv, a, c, b, d, WOOD, 3.0)
            cv.rect(a + 2, c + 2, b - 2, d - 2, CYANL, 1.8, lit=0)
    cv.glow((x0 + x1) // 2, y1 + 6, 40, (70, 200, 210), 0.12)


PROPS = {'passaplats_obert': passaplats_obert, 'cable_cafetera': cable_cafetera, 'nevera_oberta': nevera_oberta, 'pizza_nevera': pizza_nevera, 'tonyina': tonyina}


def _frames():
    base = Canvas(light=LIGHT)
    bg(base)
    frames = []
    for i in range(8):
        cv = Canvas(light=LIGHT, img=base.img.copy())
        window(cv, rain=i)
        frames.append(_diff(cv.img, base.img))
    return frames


ANIMS = {'pluja': {'frames': _frames, 'frameDuration': 200}}


# ─── Animacions de més: la tele del veí i el rellotge del microones ───────

def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv.img


# els canvis de pla de la tele del veí: (color, força del halo); el primer és el del fons
TV_SEQ = [((90, 130, 210), 0.35), ((90, 130, 210), 0.35), ((110, 150, 220), 0.42), ((70, 100, 170), 0.28),
          ((70, 100, 170), 0.28), ((150, 170, 200), 0.5), ((90, 130, 210), 0.35), ((80, 140, 150), 0.32),
          ((80, 140, 150), 0.32), ((80, 140, 150), 0.32), ((120, 110, 170), 0.38), ((90, 130, 210), 0.35)]


def _frames_tele():
    """A l'altra banda del pati, la tele del veí canvia de color amb els plans de la pel·lícula."""
    base = _base()
    frames = []
    for col, k in TV_SEQ:
        cv = Canvas(light=LIGHT, img=base.copy())
        window(cv, tv=None if (col, k) == TV_SEQ[0] else (col, k))
        d = _diff(cv.img, base)
        only = d.copy()
        only.paste((0, 0, 0, 0), (0, 0) + d.size)
        only.paste(d.crop((112, 48, 146, 80)), (112, 48))            # només la tele i el seu halo
        frames.append(only)
    return frames


def _frames_rellotge():
    """El 00:00 del microones parpelleja (ningú l'ha posat en hora des de l'últim tall de llum)."""
    base = _base()
    cv = Canvas(light=LIGHT, img=base.copy())
    cv.rect(42, 98, 47, 101, [(8, 16, 10), (14, 26, 16)], 0.6, lit=0)
    return [_diff(base, base), _diff(cv.img, base)]


ANIMS['tele'] = {'frames': _frames_tele, 'frameDuration': 260}
ANIMS['rellotge'] = {'frames': _frames_rellotge, 'frameDuration': 550}
