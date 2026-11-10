"""
El rebost i despatx d'en Tomàs (Escena 2, la Vet), al darrere del bar La Propina. Art definitiu:
  - un magatzem petit i brut: paret de maó emblanquinat amb humitats, terra de ciment amb una reixa;
  - la llum: una bombeta nua que penja del sostre (càlida, amb una arna que hi dona voltes) i la ratlla
    de llum del bar per sota la porta;
  - l'escriptori d'en Tomàs, vell i ple de factures, amb el calaix tancat per un **pany intel·ligent** de plàstic
    blanc que no hi lliga gens (Trencaclosques 2.2: llum vermell tancat, verd obert);
  - caixes de cervesa apilades sota un cartell de «PROHIBIT FUMAR» ple de cremades; una prestatgeria amb
    llaunes i una caixa de llimones (la llimonada!), un barril i la fregona.
"""
import math

from hd.pix import Light, Canvas, W, H, hr
from hd.rooms.comu import obox, outline, cable, text, text_width, _diff, PLASTIC, SHEET, CARD, RED, YEL, GRAYC
from hd.rooms.bar_sala import WOOD, STEELB, BRASS, ENAMEL, PORC, BOTTLES, SLATE
from hd.rooms.pis_cuina import outline_poly

FLOOR_Y = 150
BULB = (238, 26)
DESK_TOP = 116

BRICK = [(16, 8, 6), (32, 16, 12), (52, 28, 20), (74, 42, 30), (98, 60, 42), (122, 82, 58), (146, 108, 80), (170, 138, 108), (192, 166, 138)]
MORTAR = [(20, 18, 16), (38, 34, 30), (60, 54, 48), (86, 78, 68), (112, 104, 92), (140, 132, 118)]
CEMENT = [(10, 10, 10), (20, 20, 20), (32, 32, 30), (46, 44, 40), (62, 60, 54), (80, 78, 70), (100, 96, 86)]
DAMP = [(16, 18, 12), (30, 34, 22), (46, 50, 32)]
CRATE_Y = [(40, 26, 2), (90, 60, 6), (150, 104, 10), (204, 150, 24), (236, 196, 60), (252, 230, 130)]
CRATE_R = [(30, 6, 8), (64, 12, 14), (104, 22, 22), (146, 36, 30), (186, 58, 44), (220, 96, 72)]
LEMON = [(50, 40, 4), (110, 92, 10), (180, 160, 20), (230, 210, 50), (250, 240, 130)]
WHITEP = [(60, 60, 66), (110, 110, 118), (160, 160, 166), (200, 200, 204), (230, 230, 232), (248, 248, 250)]
GREEN = [(8, 30, 14), (16, 60, 26), (30, 100, 44), (60, 150, 70), (120, 200, 120)]
KEG = [(14, 16, 20), (30, 34, 40), (52, 58, 66), (80, 88, 98), (112, 120, 130), (150, 158, 166), (196, 202, 208), (236, 240, 244)]
INK = [(40, 6, 8), (120, 20, 20), (200, 40, 34)]

LIGHT = Light(ambient=-0.9, vignette=(70, 40), floor_fade=(190, 30))
LIGHT.point(BULB[0], BULB[1] + 4, r=210, k=3.6, squash=1.2, power=1.6)    # la bombeta
LIGHT.point(53, FLOOR_Y + 2, r=40, k=0.7, squash=2.0, power=2.0)           # la llum del bar per sota la porta


# ─── Paret i terra ──────────────────────────────────────────────────────────

def wall(cv):
    """Maó emblanquinat fa molts anys: el blanc s'ha anat menjant, i a baix hi ha humitats."""
    for y in range(0, FLOOR_Y):
        row = y // 7
        for x in range(W):
            off = 9 if row % 2 else 0
            bx = (x + off) // 18
            joint = (y % 7 == 6) or ((x + off) % 18 == 17)
            n = (hr(bx, row) - 0.5) * 0.7 + (hr(x // 2, y // 2, 4) - 0.5) * 0.3
            lime = hr(x // 9, y // 6, 7)                   # on encara queda calç
            if joint:
                cv.put(x, y, MORTAR, 2.0 + n * 0.4)
            else:
                cv.put(x, y, BRICK, 2.8 + n * 0.6 + (1.2 if lime > 0.55 else 0))
            # humitat a la part de baix de la paret
            damp = (FLOOR_Y - y) < 18 + 10 * math.sin(x / 23) + 6 * hr(x // 7, 1)
            if damp:
                cv.tint(x, y, x, y, DAMP[1], 0.35)
    cv.rect(0, FLOOR_Y - 3, W - 1, FLOOR_Y - 1, CEMENT, 2.0)    # sòcol de ciment
    cv.hline(0, W - 1, FLOOR_Y, CEMENT, 0)
    # una canonada que travessa la paret, a dalt
    cv.rect(0, 8, W - 1, 11, STEELB, lambda x, y: 3.0 + (1.2 if y == 9 else 0) - (0.8 if y == 11 else 0))
    for bx in range(30, W, 90):
        cv.rect(bx, 7, bx + 2, 12, STEELB, 2.0)


def floor(cv):
    """Ciment amb taques, una reixa de desguàs i serradures."""
    for y in range(FLOOR_Y + 1, H):
        dep = (y - FLOOR_Y) / (H - FLOOR_Y)
        for x in range(W):
            u = (x - W / 2) / (1 + dep * 0.6) + W / 2
            n = (hr(x // 3, y // 2, 2) - 0.5) * 0.5 + (hr(int(u) // 30, (y - FLOOR_Y) // 9, 9) - 0.5) * 0.6
            cv.put(x, y, CEMENT, 3.0 + n)
    # taques d'oli i de cervesa
    for i, (cx, cy, rx, ry) in enumerate(((120, 176, 18, 4), (330, 186, 26, 5), (420, 168, 12, 3))):
        cv.disc(cx, cy, rx, ry, CEMENT, lambda nx, ny: 1.8 + (nx * nx + ny * ny) * 0.8)
    # la reixa del desguàs
    gx0, gy0 = 236, 182
    cv.rect(gx0, gy0, gx0 + 18, gy0 + 5, SLATE, 0.6)
    for i in range(0, 19, 3):
        cv.vline(gx0 + i, gy0, gy0 + 5, STEELB, 3.0)
    outline(cv, gx0 - 1, gy0 - 1, gx0 + 19, gy0 + 6, CEMENT)
    # la claror de la bombeta al terra
    cv.tint(140, 156, 340, 204, (255, 210, 140), lambda x, y: 0.10 * max(0, 1 - abs(x - BULB[0]) / 110) * max(0, 1 - (y - 156) / 50))


# ─── La porta, el penjador ─────────────────────────────────────────────────

def door(cv):
    """La porta del bar, vista des de dins: fusta pelada, una balda i la llum del bar per sota."""
    x0, y0, x1, y1 = 30, 50, 76, FLOOR_Y
    obox(cv, x0 - 4, y0 - 4, x1 + 4, y1, WOOD, 3.2)
    obox(cv, x0, y0, x1, y1, WOOD, 2.4, top=0.4)
    for i in range(x0 + 6, x1, 8):                                  # taulons
        cv.vline(i, y0 + 1, y1 - 1, WOOD, 1.4)
    cv.rect(x0 + 2, y0 + 20, x1 - 2, y0 + 23, WOOD, 3.2)            # travesser
    cv.rect(x0 + 2, y1 - 26, x1 - 2, y1 - 23, WOOD, 3.2)
    cv.disc(x1 - 7, 102, 2.2, 2.2, BRASS, lambda nx, ny: 3.6 - nx - ny)   # el pom
    obox(cv, x1 - 10, 92, x1 - 3, 95, STEELB, 3.8)                  # la balda
    cv.hline(x0, x1, y1, [(255, 224, 150)], 0, lit=0)                # la llum del bar
    cv.glow((x0 + x1) // 2, y1 + 2, 22, (255, 210, 130), 0.35)
    cv.darken(x1 + 5, y0, x1 + 8, y1, 0.4)


def hooks(cv):
    """El penjador al costat de la porta: la jaqueta d'en Tomàs i un davantal de recanvi."""
    cv.rect(86, 58, 128, 61, WOOD, 3.0)
    outline(cv, 86, 58, 128, 61, WOOD)
    for hx in (94, 118):
        cv.rect(hx, 61, hx + 1, 65, BRASS, 3.6)
    # la jaqueta de pana marró
    jack = [(86, 66), (102, 64), (106, 70), (104, 108), (84, 108), (84, 72)]
    cv.poly(jack, CARD, lambda x, y: 2.2 + (0.6 if (x % 3) == 0 else 0) - (y - 64) * 0.01)
    outline_poly(cv, jack, CARD)
    cv.line(95, 66, 95, 106, CARD, 1.0)
    # el davantal negre, penjat pel coll
    ap = [(112, 66), (124, 66), (126, 98), (110, 98)]
    cv.poly(ap, SLATE, lambda x, y: 2.6 + (0.6 if x == 112 else 0))
    outline_poly(cv, ap, SLATE)
    cv.line(112, 66, 118, 62, SLATE, 3.4)
    cv.line(124, 66, 118, 62, SLATE, 3.4)


def fusebox(cv):
    """El quadre elèctric, amb un cable pelat que fa por de mirar."""
    obox(cv, 140, 40, 158, 64, GRAYC, 3.0)
    cv.rect(143, 46, 155, 52, SLATE, 1.0)
    for i in range(4):
        cv.rect(144 + i * 3, 47, 145 + i * 3, 51, WHITEP, 3.6 if i != 2 else 2.0)
    cable(cv, [(150, 64), (152, 76), (146, 86), (150, 96)], SLATE, 1.6)
    cv.rect(148, 12, 151, 39, GRAYC, lambda x, y: 2.6 + (0.8 if x == 148 else 0) - (0.8 if x == 151 else 0))   # el tub fins a la canonada


# ─── L'escriptori ──────────────────────────────────────────────────────────

def calendar(cv):
    """Un calendari d'una marca de cervesa, a la paret de damunt l'escriptori, encara al mes de fa dos anys."""
    x0, y0, x1, y1 = 176, 44, 204, 86
    obox(cv, x0, y0, x1, y1, SHEET, 4.4)
    cv.rect(x0 + 2, y0 + 2, x1 - 2, y0 + 18, CRATE_Y, 2.8)            # la foto: un got de cervesa i espuma
    cv.rect(186, y0 + 6, 194, y0 + 17, CRATE_Y, 3.8)
    cv.rect(186, y0 + 4, 194, y0 + 6, WHITEP, 4.6)
    for j in range(4):
        for i in range(6):
            cv.flat(x0 + 3 + i * 4, y0 + 22 + j * 4, (110, 106, 120))
    cv.disc(x0 + 7, y0 + 26, 2.4, 2, RED, 2.6)                          # un dia encerclat
    cv.disc(190, y0 - 1, 1.2, 1.2, STEELB, 4.0)


def corkboard(cv):
    """Un suro amb factures clavades, un número de telèfon i una foto de l'equip de futbol."""
    x0, y0, x1, y1 = 212, 40, 280, 84
    obox(cv, x0 - 2, y0 - 2, x1 + 2, y1 + 2, WOOD, 3.4)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, CARD, 2.6 + (hr(x, y, 8) - 0.5) * 0.8)
    papers = ((216, 44, 232, 64, SHEET, 4.4, -1), (236, 46, 252, 60, YEL, 3.6, 1), (256, 44, 276, 70, SHEET, 4.0, 0),
              (220, 66, 240, 82, SHEET, 3.8, 1), (244, 64, 262, 80, PORC, 4.0, -1))
    for (a, b, c, d, ramp, lvl, tilt) in papers:
        pts = [(a, b + max(0, tilt)), (c, b + max(0, -tilt)), (c, d + max(0, -tilt)), (a, d + max(0, tilt))]
        cv.poly(pts, ramp, lvl)
        outline_poly(cv, pts, ramp)
        for ly in range(b + 4, d - 2, 3):
            cv.hline(a + 2, c - 3 - (ly * 7) % 5, ly, SLATE, 2.6)
        cv.disc((a + c) // 2, b + 1, 1, 1, RED, 3.4)
    # la foto de l'equip (verd i blau)
    cv.rect(246, 66, 260, 76, GREEN, 2.4)
    for i in range(5):
        cv.rect(247 + i * 3, 69, 248 + i * 3, 73, [(30, 30, 90), (60, 60, 160)], 1.0)


def desk(cv):
    """L'escriptori d'en Tomàs: fusta fosca rascada, el calaix del mig amb el pany intel·ligent."""
    x0, x1 = 160, 290
    # el taulell, una mica des de dalt
    cv.poly([(x0 + 2, DESK_TOP - 6), (x1 - 2, DESK_TOP - 6), (x1 + 2, DESK_TOP), (x0 - 2, DESK_TOP)], WOOD,
            lambda x, y: 4.2 + (y - DESK_TOP) * 0.08 + (0.5 if hr(x // 6, y, 2) > 0.8 else 0))
    cv.rect(x0 - 2, DESK_TOP, x1 + 2, DESK_TOP + 3, WOOD, 3.0)
    cv.hline(x0 - 2, x1 + 2, DESK_TOP + 3, WOOD, 0)
    # el frontal: dos calaixeres i el calaix del mig
    for (a, b) in ((x0, 196), (252, x1)):
        obox(cv, a, DESK_TOP + 4, b, FLOOR_Y + 8, WOOD, 2.2, top=0.2)
        for k in range(3):
            yy = DESK_TOP + 8 + k * 12
            obox(cv, a + 3, yy, b - 3, yy + 9, WOOD, 2.8, top=0.6)
            cv.rect((a + b) // 2 - 3, yy + 4, (a + b) // 2 + 3, yy + 5, BRASS, 3.4)
    # el forat de sota, fosc
    cv.rect(197, 137, 251, FLOOR_Y + 8, SLATE, 0.8)
    cv.darken(197, 137, 251, 142, 0.5)
    # la paperera al forat
    obox(cv, 230, 140, 246, FLOOR_Y + 8, GRAYC, 1.8)
    for i in range(3):
        cv.disc(234 + i * 4, 140, 2.2, 1.4, SHEET, 3.0 + i * 0.4)
    drawer(cv, open_=False)
    cv.darken(x0 - 3, FLOOR_Y + 9, x1 + 4, FLOOR_Y + 13, lambda x, y: 0.7 - (y - FLOOR_Y - 9) * 0.12)


def drawer(cv, open_=False):
    """El calaix del mig: fusta vella i, clavat amb quatre cargols, el pany intel·ligent de 19,99 €."""
    y0, y1 = (120, 136) if not open_ else (126, 146)
    if open_:
        # el calaix tret: es veu per dins (fons clar) i la servilleta de la recepta
        cv.poly([(196, 120), (252, 120), (254, 126), (194, 126)], WOOD, 1.2)
        cv.rect(198, 121, 250, 125, CARD, 2.0)
    obox(cv, 196, y0, 252, y1, WOOD, 3.0, top=0.8)
    cv.hline(198, 250, y0 + 2, WOOD, 3.8)
    # el pany: plàstic blanc lluent, molt més nou que tot el que l'envolta
    lx0, ly0 = 218, y0 + 2
    obox(cv, lx0, ly0, lx0 + 12, ly0 + 11, WHITEP, 4.0, top=1.2)
    cv.disc(lx0 + 6, ly0 + 6, 2.4, 2.4, WHITEP, lambda nx, ny: 2.8 - ny)
    led = (60, 230, 100) if open_ else (240, 40, 40)
    cv.flat(lx0 + 10, ly0 + 2, led)
    cv.glow(lx0 + 10, ly0 + 2, 5, led, 0.5)
    for (sx, sy) in ((lx0 + 1, ly0 + 1), (lx0 + 11, ly0 + 10)):
        cv.flat(sx, sy, (120, 120, 126))


def desk_things(cv):
    """Damunt l'escriptori: el cendrer ple, el punxó de factures, la calculadora, el marc i el flexo."""
    t = DESK_TOP - 3
    # el flexo, encorbat cap a les factures
    cv.disc(172, t, 6, 1.6, SLATE, 2.6)
    cv.line(172, t, 176, t - 18, STEELB, 3.0)
    cv.line(176, t - 18, 186, t - 24, STEELB, 3.0)
    cv.poly([(184, t - 26), (194, t - 24), (192, t - 18), (182, t - 21)], GREEN, 2.4)
    outline_poly(cv, [(184, t - 26), (194, t - 24), (192, t - 18), (182, t - 21)], GREEN)
    # el punxó amb factures
    cv.vline(204, t - 18, t, STEELB, 4.2)
    for i in range(6):
        y = t - 2 - i * 2
        cv.hline(198 + (i % 2), 210 - (i % 3), y, SHEET, 4.2 - i * 0.2)
        cv.hline(198 + (i % 2), 210 - (i % 3), y + 1, SHEET, 2.4)
    # la calculadora
    obox(cv, 214, t - 3, 230, t, PLASTIC, 2.4)
    cv.rect(216, t - 2, 222, t - 2, [(60, 80, 50), (120, 150, 90)], 1.0)
    # el cendrer ple de burilles (aquí dins sí que es fuma)
    cv.disc(240, t - 1, 6, 2.2, [(30, 40, 50), (70, 90, 110), (130, 160, 180), (190, 210, 220)], lambda nx, ny: 2.4 - ny)
    for i in range(4):
        cv.line(236 + i * 3, t - 2, 238 + i * 3, t - 4 - (i % 2), SHEET, 4.0)
        cv.flat(238 + i * 3, t - 4 - (i % 2), (200, 140, 90))
    # el marc: la foto de mostra que venia amb el marc («la seva dona»)
    obox(cv, 256, t - 18, 272, t, BRASS, 3.4)
    cv.rect(258, t - 16, 270, t - 2, [(60, 90, 120), (120, 160, 190), (190, 210, 230)], 1.4)
    cv.disc(264, t - 10, 2.6, 3, [(140, 90, 70), (210, 160, 130), (240, 200, 170)], 1.8)
    cv.rect(261, t - 6, 267, t - 2, RED, 2.6)
    cv.disc(264, t - 13, 3, 1.6, YEL, 2.8)                                # rossa, somrient, genèrica
    # una tassa amb bolígrafs
    obox(cv, 278, t - 8, 285, t, PORC, 4.0)
    for i, c in enumerate((RED, PLASTIC, YEL)):
        cv.line(279 + i * 2, t - 8, 278 + i * 3, t - 14 + i, c, 3.0)


def chair(cv):
    """La cadira de despatx, de skai rebentat, apartada a l'esquerra de l'escriptori."""
    cx = 144
    cv.rect(cx - 1, 138, cx + 1, 160, STEELB, 3.0)
    for dx in (-10, -4, 4, 10):
        cv.line(cx, 160, cx + dx, 164, STEELB, 2.6)
        cv.disc(cx + dx, 165, 1.4, 1, SLATE, 2.0)
    back = [(132, 98), (152, 96), (154, 130), (132, 132)]
    cv.poly(back, SLATE, lambda x, y: 2.0 + (0.8 if x < 136 else 0) + (0.4 if hr(x // 3, y // 3) > 0.85 else 0))
    outline_poly(cv, back, SLATE)
    cv.disc(142, 110, 3, 2, CARD, 3.6)                                    # l'escuma que surt pel forat
    seat = [(128, 130), (158, 128), (160, 138), (126, 140)]
    cv.poly(seat, SLATE, lambda x, y: 2.4 + (1.0 if y < 132 else 0))
    outline_poly(cv, seat, SLATE)
    cv.darken(132, 166, 158, 168, 0.6)


# ─── El magatzem ───────────────────────────────────────────────────────────

def no_smoking(cv):
    """«PROHIBIT FUMAR», ple de cremades de cigarreta."""
    x0, y0, x1, y1 = 330, 30, 380, 60
    obox(cv, x0, y0, x1, y1, ENAMEL, 4.6)
    cx, cy = 355, 38
    cv.ring(cx, cy, 8, RED, 3.4, step=1)
    cv.ring(cx, cy, 7, RED, 3.4, step=1)
    cv.rect(cx - 6, cy - 1, cx + 5, cy + 1, SHEET, 4.4)                     # la cigarreta
    cv.rect(cx + 3, cy - 1, cx + 5, cy + 1, [(200, 120, 60), (240, 160, 80)], 1.0)
    cv.line(cx - 5, cy + 5, cx + 5, cy - 5, RED, 3.4)
    cv.line(cx - 5, cy + 6, cx + 6, cy - 5, RED, 3.4)
    for k, word in enumerate(('PROHIBIT', 'FUMAR')):
        text(cv, word, (x0 + x1 - text_width(word)) // 2 + 1, y1 - 12 + k * 6, INK, 2.0)
    for (bx, by) in ((337, 36), (372, 48), (346, 52), (366, 34), (341, 45), (376, 38)):   # les cremades
        cv.disc(bx, by, 1.6, 1.4, [(20, 12, 6), (60, 40, 20), (110, 80, 40)], lambda nx, ny: 0.4 + (nx * nx + ny * ny) * 1.6)


def crate(cv, x0, y0, ramp, label=None):
    """Una caixa de cervesa de plàstic (36×20) amb els colls de les ampolles a dalt."""
    x1, y1 = x0 + 36, y0 + 20
    for i in range(6):                                                      # els colls
        bx = x0 + 4 + i * 5
        cv.rect(bx, y0 - 5, bx + 2, y0, BOTTLES[1], 2.4)
        cv.flat(bx + 1, y0 - 6, (200, 170, 60))
    obox(cv, x0, y0, x1, y1, ramp, 3.0, top=0.8)
    cv.rect(x0 + 4, y0 + 4, x1 - 4, y0 + 7, ramp, 1.2)                      # l'agafador
    for i in range(5):
        cv.vline(x0 + 5 + i * 7, y0 + 10, y1 - 2, ramp, 1.8)
    if label:
        text(cv, label, x0 + (36 - text_width(label)) // 2, y0 + 12, [(30, 6, 4), (240, 230, 200)], 1.0, flat=(250, 244, 220))


def crates(cv):
    """Les caixes de cervesa, apilades de qualsevol manera, i una caixa de tovallons."""
    crate(cv, 300, 130, CRATE_Y)
    crate(cv, 338, 130, CRATE_R)
    crate(cv, 376, 130, CRATE_Y)
    crate(cv, 318, 105, CRATE_R)
    crate(cv, 358, 104, CRATE_Y)
    crate(cv, 340, 79, CRATE_Y)
    # una capsa de cartró de tovallons, damunt de tot a la dreta
    w = text_width('TOVALLONS')
    obox(cv, 396 - w // 2 - 3, 92, 396 + w // 2 + 3, 124, CARD, 3.2, top=0.8)
    text(cv, 'TOVALLONS', 396 - w // 2, 102, [(30, 16, 8), (70, 40, 20)], 1.0)
    cv.hline(396 - w // 2 - 2, 396 + w // 2 + 2, 110, CARD, 4.4)
    cv.darken(298, FLOOR_Y + 1, 416, FLOOR_Y + 4, 0.5)


def shelves(cv):
    """Prestatgeria metàl·lica: llaunes, sacs de sucre, garrafes i la caixa de llimones."""
    x0, x1 = 424, 474
    for x in (x0, x1):
        cv.rect(x, 24, x + 1, FLOOR_Y + 4, STEELB, 3.2)
    for k, y in enumerate((44, 76, 108, 140)):
        cv.rect(x0, y, x1 + 1, y + 2, STEELB, 3.8)
        cv.hline(x0, x1 + 1, y + 3, STEELB, 0.8)
    # prestatge 1: llaunes de tomàquet i olives
    for i in range(6):
        obox(cv, x0 + 3 + i * 8, 34, x0 + 9 + i * 8, 44, [(30, 6, 6), (110, 20, 20), (180, 40, 30), (230, 220, 200)] if i % 2 else STEELB, 2.6)
    # prestatge 2: la caixa de llimones (la llimonada!)
    w = text_width('LLIMONES')
    obox(cv, x0 + 2, 62, x0 + w + 6, 76, CARD, 2.6)
    for i in range(7):
        cv.disc(x0 + 6 + i * 5, 61, 2.6, 2.2, LEMON, lambda nx, ny: 3.2 - ny - nx * 0.6)
    text(cv, 'LLIMONES', x0 + 4, 68, [(30, 16, 8), (90, 60, 20)], 1.0)
    obox(cv, x0 + w + 8, 62, x1 - 1, 76, SHEET, 3.6)                       # un sac de sucre
    # prestatge 3: garrafes d'aigua
    for i in range(2):
        cv.disc(x0 + 12 + i * 22, 96, 9, 11, [(30, 50, 70), (60, 100, 130), (120, 170, 200), (200, 230, 240)], lambda nx, ny: 1.6 + (1.6 if nx < -0.3 and ny < 0 else 0))
        cv.rect(x0 + 10 + i * 22, 82, x0 + 14 + i * 22, 86, [(10, 40, 110), (30, 80, 180)], 1.4)
    # prestatge 4: paquets de cafè
    for i in range(5):
        obox(cv, x0 + 3 + i * 9, 124, x0 + 10 + i * 9, 140, [(14, 8, 6), (40, 24, 16), (90, 30, 20), (200, 160, 80)], 1.6)


def keg_and_mop(cv):
    """Un barril de cervesa a terra i la fregona dins la galleda."""
    # el barril
    cx, top, bot = 448, 154, 184
    for y in range(top, bot + 1):
        for x in range(cx - 13, cx + 14):
            nx = (x - cx) / 13
            cv.put(x, y, KEG, 3.4 - nx * 1.6 + (1.6 if -0.5 < nx < -0.25 else 0) + (0.8 if (y - top) in (4, 26) else 0))
    cv.disc(cx, top, 13, 3, KEG, lambda nx, ny: 3.0 - ny)
    cv.disc(cx, top, 4, 1.4, SLATE, 1.6)
    for x in (cx - 13, cx + 13):
        cv.vline(x, top, bot, KEG, 0)
    cv.darken(cx - 14, bot + 1, cx + 16, bot + 4, 0.55)
    # la galleda i la fregona
    gx = 98
    cv.poly([(gx - 10, 160), (gx + 10, 160), (gx + 8, 176), (gx - 8, 176)], [(30, 10, 30), (80, 30, 90), (130, 60, 150), (180, 110, 200)], lambda x, y: 2.4 - (x - gx) * 0.06)
    outline_poly(cv, [(gx - 10, 160), (gx + 10, 160), (gx + 8, 176), (gx - 8, 176)], [(20, 6, 20)])
    cv.disc(gx, 160, 10, 2.4, [(20, 20, 26), (50, 50, 60), (90, 90, 100)], 1.4)
    cv.line(gx + 2, 160, gx + 14, 96, CARD, 3.4)
    cv.disc(gx + 1, 158, 6, 2, SHEET, lambda nx, ny: 2.6 - ny)
    cv.darken(gx - 9, 177, gx + 10, 179, 0.6)


def bulb(cv):
    """La bombeta nua, penjada del fil."""
    bx, by = BULB
    cv.vline(bx, 0, by - 5, SLATE, 1.4)
    obox(cv, bx - 2, by - 6, bx + 2, by - 3, BRASS, 3.0)
    cv.disc(bx, by, 4, 4.6, [(255, 220, 140)], 0, lit=0)
    cv.disc(bx - 1, by - 1, 2, 2, [(255, 250, 220)], 0, lit=0)
    cv.glow(bx, by, 40, (255, 200, 120), 0.45)


def bg(cv):
    wall(cv)
    floor(cv)
    fusebox(cv)
    hooks(cv)
    door(cv)
    calendar(cv)
    corkboard(cv)
    no_smoking(cv)
    shelves(cv)
    crates(cv)
    chair(cv)
    desk(cv)
    desk_things(cv)
    keg_and_mop(cv)
    bulb(cv)


# ─── Props ──────────────────────────────────────────────────────────────────

def calaix_obert(cv):
    """El calaix obert: el pany en verd i, a dins, la servilleta de la recepta."""
    cv.rect(194, 118, 254, 147, SLATE, 0.6)
    drawer(cv, open_=True)


def recepta_calaix(cv):
    """La servilleta amb la recepta, dins el calaix obert (fins que la Vet l'agafa)."""
    cv.poly([(208, 122), (226, 121), (228, 125), (206, 126)], SHEET, 5.0)
    cv.line(210, 123, 222, 122, INK, 1.4)
    cv.line(211, 124, 224, 124, INK, 1.4)


PROPS = {'calaix_obert': calaix_obert, 'recepta_calaix': recepta_calaix}


# ─── L'arna ─────────────────────────────────────────────────────────────────

def _frames():
    base = Canvas(light=LIGHT)
    bg(base)
    frames = []
    for i in range(12):
        cv = Canvas(light=LIGHT, img=base.img.copy())
        a = i / 12 * 2 * math.pi
        mx = BULB[0] + round(math.cos(a) * 11)
        my = BULB[1] + round(math.sin(a * 2) * 4) + 2
        wing = (90, 80, 70) if i % 2 else (150, 140, 120)
        cv.flat(mx, my, (40, 34, 30))
        cv.flat(mx - 1, my - (i % 2), wing)
        cv.flat(mx + 1, my - (i % 2), wing)
        frames.append(_diff(cv.img, base.img))
    return frames


ANIMS = {'arna': {'frames': _frames, 'frameDuration': 90}}


# ─── Animacions de més: la gota de la canonada i passos al bar ────────────

def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv.img


WATER = [(20, 26, 30), (50, 62, 70), (100, 116, 124), (160, 176, 184), (220, 230, 236)]
DRIP_X = 420                   # entre la pila de caixes i la prestatgeria


def _frames_gota():
    """La canonada del sostre goteja: la gota s'infla, cau arran de paret i esquitxa el terra."""
    base = _base()
    frames = []
    fall = (16, 34, 60, 92, 128)                                   # on és la gota a cada fotograma de caiguda
    for i in range(20):
        cv = Canvas(light=LIGHT, img=base.copy())
        if i < 10:                                                 # la gota es forma sota la canonada
            if i >= 3:
                cv.put(DRIP_X, 12, WATER, 3.0, lit=0)
            if i >= 7:
                cv.put(DRIP_X, 13, WATER, 2.4, lit=0)
                cv.flat(DRIP_X, 12, (190, 204, 210))
        elif i < 15:                                               # cau
            y = fall[i - 10]
            cv.put(DRIP_X, y, WATER, 3.4, lit=0)
            cv.put(DRIP_X, y - 1, WATER, 2.0, lit=0)
            if i > 11:
                cv.put(DRIP_X, y - 2, WATER, 1.2, lit=0)
        elif i < 17:                                               # esquitx
            cv.put(DRIP_X, 151, WATER, 3.0, lit=0)
            r = 1 + (i - 15)
            cv.put(DRIP_X - r - 1, 151 - (2 - (i - 15)), WATER, 2.6, lit=0)
            cv.put(DRIP_X + r + 1, 151 - (2 - (i - 15)), WATER, 2.6, lit=0)
        frames.append(_diff(cv.img, base))
    return frames


def _frames_passos():
    """Algú passa pel bar, a l'altra banda de la porta: l'ombra dels peus talla la ratlla de llum de sota."""
    base = _base()
    frames = []
    for i in range(22):
        cv = Canvas(light=LIGHT, img=base.copy())
        if i < 10:
            x = 22 + i * 6                                       # d'esquerra a dreta, dos peus
            for fx in (x, x + 9 - (4 if i % 2 else 0)):
                cv.darken(max(30, fx), 149, min(76, fx + 4), 151, 0.9, dither=False)
                cv.darken(max(30, fx - 1), 152, min(76, fx + 5), 153, 0.5)
        frames.append(_diff(cv.img, base))
    return frames


ANIMS['gota'] = {'frames': _frames_gota, 'frameDuration': 110}
ANIMS['passos'] = {'frames': _frames_passos, 'frameDuration': 120}
