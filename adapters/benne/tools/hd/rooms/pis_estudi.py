"""
L'estudi de l'Iri (Escena 1), de nit. **Sala de mostra de l'art definitiu de Suma Zero.**

Habitació petita i atapeïda: paper pintat lila descolorit, parquet gastat, un matalàs a terra sota la
finestra (a fora, la ciutat de nit i el neó d'una pizzeria), un pòster, l'escriptori amb tres monitors
que fan de llum principal, el router damunt d'una caixa de fruita, la presa de la fibra, el passaplats de
la cuina (llum càlida de la Vet) i una pila de caixes de pizza. Cables per tot arreu.

Llums: els monitors (fred, verd blavós), el passaplats (càlid) i la finestra (blau i rosa del neó).
La geometria clicable és a room_designs.py (PIS_ESTUDI): el dibuix hi ha de coincidir.
"""
import math

from hd.pix import Light, Canvas, W, H, hr, mix

# ─── Rampes (fosc → clar) ──────────────────────────────────────────────────
WALL = [(22, 14, 34), (34, 22, 48), (48, 32, 62), (64, 44, 78), (82, 58, 94), (104, 76, 110), (130, 98, 126), (160, 124, 142)]
STRIPE = [(26, 16, 38), (40, 26, 54), (56, 38, 70), (74, 52, 86), (94, 68, 102), (118, 88, 118)]
WOOD = [(20, 10, 12), (36, 20, 18), (56, 32, 24), (80, 48, 32), (106, 66, 40), (134, 88, 52), (164, 112, 66), (196, 140, 84)]
DESK = [(14, 10, 18), (26, 18, 28), (40, 28, 38), (58, 40, 50), (78, 56, 64), (102, 74, 80), (128, 96, 98)]
PLASTIC = [(8, 8, 14), (16, 16, 24), (26, 26, 36), (40, 40, 52), (58, 58, 72), (82, 82, 98)]
SCREEN = [(6, 20, 26), (10, 40, 44), (16, 70, 66), (30, 110, 96), (60, 160, 130), (120, 220, 180), (200, 255, 230)]
SKY = [(6, 6, 20), (10, 12, 32), (16, 20, 48), (24, 30, 66), (36, 42, 86), (52, 56, 104)]
CITY = [(4, 4, 12), (10, 10, 24), (18, 16, 36), (28, 24, 50)]
NEON = [(60, 10, 40), (140, 20, 90), (220, 50, 150), (255, 120, 200), (255, 200, 240)]
WARM = [(40, 20, 10), (90, 46, 18), (150, 84, 30), (210, 130, 50), (246, 186, 96), (255, 230, 170)]
FABRIC = [(16, 20, 34), (26, 34, 54), (38, 50, 76), (54, 70, 100), (74, 94, 126), (100, 122, 152)]
SHEET = [(40, 36, 52), (70, 66, 84), (110, 106, 120), (150, 146, 156), (190, 186, 190), (222, 220, 218)]
CARD = [(40, 24, 14), (70, 44, 24), (106, 70, 38), (146, 102, 58), (184, 136, 80), (216, 172, 108), (240, 206, 146)]
RED = [(40, 6, 12), (80, 14, 20), (130, 26, 30), (180, 44, 40), (220, 80, 60), (246, 130, 100)]
GRAYC = [(12, 12, 18), (26, 26, 34), (44, 44, 54), (66, 66, 78), (94, 94, 106), (130, 130, 140)]
YEL = [(50, 36, 6), (110, 80, 10), (180, 136, 20), (230, 190, 50), (250, 230, 120)]

FLOOR_Y = 150

LIGHT = Light(ambient=-0.2, vignette=(60, 30), floor_fade=(196, 30))
LIGHT.point(280, 108, r=190, k=3.2, squash=1.2, power=1.5)       # monitors
LIGHT.point(455, 108, r=95, k=2.0, squash=1.0, power=1.8)        # passaplats (cuina)
LIGHT.point(79, 72, r=85, k=1.4, squash=0.9, power=1.8)          # finestra


def outline(cv, x0, y0, x1, y1, ramp):
    """Contorn fosc d'un rectangle (l'estil de dibuix animat de tot el joc)."""
    for x in range(x0, x1 + 1):
        cv.flat(x, y0, ramp[0])
        cv.flat(x, y1, ramp[0])
    for y in range(y0, y1 + 1):
        cv.flat(x0, y, ramp[0])
        cv.flat(x1, y, ramp[0])


def obox(cv, x0, y0, x1, y1, ramp, lvl, top=1.0, side=-0.8, lit=1.0):
    """Capsa plena amb llum a dalt, ombra a la dreta i contorn."""
    cv.rect(x0, y0, x1, y1, ramp, lambda x, y: lvl + (top if y == y0 + 1 else 0) + (side if x >= x1 - 1 else 0), lit)
    outline(cv, x0, y0, x1, y1, ramp)


def cable(cv, pts, ramp, lvl=2.0, thick=1):
    """Cable que penja: una corba de Bézier per punts de control."""
    n = 80
    for i in range(n + 1):
        t = i / n
        p = list(pts)
        while len(p) > 1:
            p = [((a[0] * (1 - t) + b[0] * t), (a[1] * (1 - t) + b[1] * t)) for a, b in zip(p, p[1:])]
        x, y = p[0]
        for d in range(thick):
            cv.put(round(x), round(y) + d, ramp, lvl + (0.6 if d == 0 else 0))
        cv.flat(round(x), round(y) + thick, ramp[0])


# ─── Fons ──────────────────────────────────────────────────────────────────

def wall(cv):
    # paper pintat: ratlles verticals amb un motiu de rombes petits
    for y in range(0, FLOOR_Y):
        for x in range(W):
            band = (x // 12) % 2
            lvl = 2.6 + (0.25 if band else 0) + (hr(x // 3, y // 5) - 0.5) * 0.25
            if band and (x % 12 == 6) and (y % 14 in (4, 5, 6)) and abs((y % 14) - 5) + abs(0) <= 1:
                lvl += 0.6
            cv.put(x, y, WALL if not band else STRIPE, lvl)
    # taques d'humitat i paper esquinçat
    for (cx, cy, r) in ((24, 18, 16), (452, 130, 12), (200, 20, 10)):
        cv.darken(cx - r, cy - r, cx + r, cy + r, lambda x, y, cx=cx, cy=cy, r=r: max(0, 1 - math.hypot(x - cx, y - cy) / r) * 0.6)
    # sòcol
    cv.rect(0, FLOOR_Y - 6, W - 1, FLOOR_Y - 1, WOOD, 2.2)
    cv.hline(0, W - 1, FLOOR_Y - 6, WOOD, 3.6)
    cv.hline(0, W - 1, FLOOR_Y, WOOD, 0)


def floor(cv):
    # parquet en espiga, gastat, amb perspectiva lleugera
    for y in range(FLOOR_Y + 1, H):
        dep = (y - FLOOR_Y) / (H - FLOOR_Y)
        ph = 6 + dep * 6
        for x in range(W):
            u = (x - W / 2) / (1 + dep * 0.4) + W / 2
            col = math.floor(u / 22)
            row = math.floor((y - FLOOR_Y) / ph + (col % 2) * 0.5)
            lvl = 2.6 + (hr(col, row) - 0.5) * 0.9
            if (u % 22) < 1:
                lvl = 0.8
            elif abs(((y - FLOOR_Y) / ph + (col % 2) * 0.5) % 1) < 0.12:
                lvl = 1.1
            cv.put(x, y, WOOD, lvl)
    # catifa gastada davant l'escriptori
    for y in range(176, 204):
        for x in range(150, 400):
            nx, ny = (x - 275) / 128, (y - 190) / 15
            d = nx * nx + ny * ny
            if d <= 1:
                border = 0.9 if 0.72 < d < 0.82 else 0
                cv.put(x, y, RED, 1.8 + border + (0.3 if (x // 8) % 2 else 0))


def window(cv):
    x0, y0, x1, y1 = 34, 30, 124, 112
    # cel i ciutat
    for y in range(y0 + 3, y1 - 2):
        for x in range(x0 + 3, x1 - 2):
            cv.put(x, y, SKY, 1.0 + (y - y0) / 30, lit=0)
    for i, (bx, bw, bh) in enumerate(((37, 14, 46), (52, 10, 60), (63, 18, 40), (82, 12, 56), (95, 16, 34), (110, 12, 50))):
        top = y1 - 3 - bh
        cv.rect(bx, top, bx + bw, y1 - 3, CITY, 1.2, lit=0)
        for wy in range(top + 3, y1 - 6, 5):
            for wx in range(bx + 2, bx + bw - 1, 4):
                if hr(wx, wy, i) > 0.62:
                    cv.flat(wx, wy, (250, 210, 120) if hr(wy, wx) > 0.3 else (140, 200, 250))
                    cv.flat(wx + 1, wy, (210, 160, 90))
    # lluna petita
    cv.disc(112, 42, 4, 4, YEL, 4.0, lit=0)
    # marc, travesser i ampit
    obox(cv, x0, y0, x1, y0 + 3, WOOD, 3.4)
    obox(cv, x0, y1 - 3, x1, y1, WOOD, 3.0)
    obox(cv, x0, y0, x0 + 3, y1, WOOD, 3.0)
    obox(cv, x1 - 3, y0, x1, y1, WOOD, 2.4)
    obox(cv, x0, (y0 + y1) // 2 - 1, x1, (y0 + y1) // 2 + 1, WOOD, 3.0)
    obox(cv, (x0 + x1) // 2 - 1, y0, (x0 + x1) // 2 + 1, y1, WOOD, 3.0)
    obox(cv, x0 - 5, y1, x1 + 5, y1 + 4, WOOD, 3.6)
    # cortina caiguda (una sola, de cantó)
    cv.poly([(x0 - 6, y0 - 6), (x0 + 12, y0 - 6), (x0 + 6, y1 - 20), (x0 + 10, y1 + 2), (x0 - 6, y1 + 2)], FABRIC,
            lambda x, y: 2.4 + 0.8 * math.sin(x / 2.2))
    cv.hline(x0 - 10, x1 + 10, y0 - 7, GRAYC, 3.0)


def neon_sign(cv, on=True):
    """El neó de la pizzeria del davant, que es veu per la finestra: «PIZZA» en rosa."""
    lvl = 3.6 if on else 0.8
    letters = {'P': ['111', '101', '111', '100', '100'], 'I': ['1', '1', '1', '1', '1'],
               'Z': ['111', '001', '010', '100', '111'], 'A': ['010', '101', '111', '101', '101']}
    x = 70
    for ch in 'PIZZA':
        g = letters[ch]
        for j, row in enumerate(g):
            for i, b in enumerate(row):
                if b == '1':
                    cv.put(x + i, 86 + j, NEON, lvl, lit=0)
        x += len(g[0]) + 1
    if on:
        cv.glow(81, 88, 16, (255, 110, 200), 0.35)


def mattress(cv):
    # matalàs a terra amb un nòrdic arrugat i un coixí
    cv.poly([(18, 152), (146, 152), (152, 170), (12, 170)], SHEET, lambda x, y: 2.6 + (0.6 if y < 155 else 0))
    cv.rect(12, 170, 152, 175, SHEET, 1.4)
    cv.poly([(16, 146), (80, 140), (148, 150), (152, 166), (60, 168), (14, 166)], FABRIC,
            lambda x, y: 2.4 + 0.9 * math.sin(x / 7 + y / 4) + (0.8 if y < 147 else 0))
    cv.disc(32, 147, 16, 6, SHEET, lambda nx, ny: 3.2 - ny * 1.2)
    outline_poly = [(12, 175), (152, 175)]
    cv.hline(12, 152, 176, WOOD, 0)
    cv.line(*outline_poly[0], *outline_poly[1], WOOD, 0)


def poster(cv):
    x0, y0, x1, y1 = 150, 36, 190, 92
    obox(cv, x0, y0, x1, y1, SHEET, 3.4)
    # un gat amb ulleres de sol i el text «HANG IN THERE»... en versió hacker: un gat i «404»
    cv.rect(x0 + 3, y0 + 3, x1 - 3, y1 - 16, SKY, 2.6)
    cv.disc(170, 58, 9, 8, GRAYC, lambda nx, ny: 3.0 - ny)
    cv.poly([(162, 52), (163, 44), (168, 50)], GRAYC, 3.2)
    cv.poly([(178, 52), (177, 44), (172, 50)], GRAYC, 3.2)
    cv.rect(163, 56, 168, 58, PLASTIC, 0.5)
    cv.rect(172, 56, 177, 58, PLASTIC, 0.5)
    cv.hline(168, 172, 57, PLASTIC, 0.5)
    digits = {'4': ['101', '101', '111', '001', '001'], '0': ['111', '101', '101', '101', '111']}
    x = 159
    for ch in '404':
        for j, row in enumerate(digits[ch]):
            for i, b in enumerate(row):
                if b == '1':
                    cv.rect(x + i * 2, 78 + j * 2, x + i * 2 + 1, 78 + j * 2 + 1, RED, 3.2)
        x += 8
    # cinta adhesiva als cantons
    for cx, cy in ((x0, y0), (x1, y0)):
        cv.rect(cx - 3, cy - 1, cx + 3, cy + 2, YEL, 3.0)


DESK_Y = 132   # taulell de l'escriptori: a la cintura de l'Iri (personatges de 64 px amb cap gran)


def desk(cv):
    # escriptori llarg de taulell laminat, amb calaixera a l'esquerra
    obox(cv, 196, DESK_Y, 368, DESK_Y + 5, DESK, 3.2, top=1.4)
    obox(cv, 200, DESK_Y + 5, 234, 166, DESK, 2.0)
    for y in (DESK_Y + 13, DESK_Y + 22):
        cv.hline(203, 231, y, DESK, 0.5)
        cv.rect(213, y + 3, 221, y + 4, GRAYC, 3.0)
    obox(cv, 360, DESK_Y + 5, 365, 166, DESK, 1.6)


def chair(cv):
    # cadira d'oficina rebentada, mirant la pantalla
    cv.disc(300, 156, 18, 5, PLASTIC, lambda nx, ny: 2.2 - ny * 0.8)
    cv.rect(297, 160, 303, 170, GRAYC, 2.0)
    for dx in (-12, -5, 5, 12):
        cv.line(300, 170, 300 + dx, 176, GRAYC, 2.0)
        cv.disc(300 + dx, 177, 2, 1.5, PLASTIC, 1.0)
    cv.poly([(286, 122), (314, 122), (317, 152), (283, 152)], RED, lambda x, y: 2.2 + (0.8 if x < 288 else 0) - (0.8 if x > 312 else 0))
    cv.rect(292, 130, 297, 133, YEL, 2.0)                                   # un pegat de cinta americana
    outline(cv, 283, 122, 317, 152, RED)


def monitors(cv, frame=0):
    """Tres monitors. `frame` mou el codi de les pantalles (animació)."""
    specs = ((208, 98, 244, 125), (252, 86, 308, 125), (316, 98, 352, 125))
    for n, (x0, y0, x1, y1) in enumerate(specs):
        obox(cv, x0, y0, x1, y1, PLASTIC, 2.4)
        sx0, sy0, sx1, sy1 = x0 + 3, y0 + 3, x1 - 3, y1 - 4
        for y in range(sy0, sy1 + 1):
            for x in range(sx0, sx1 + 1):
                cv.put(x, y, SCREEN, 1.4 + (0.3 if (y + frame) % 2 == 0 else 0), lit=0)
        # línies de codi que pugen
        for row in range(sy0 + 1, sy1, 3):
            seed = (row - sy0) // 3 + frame + n * 7
            indent = int(hr(seed, 1) * 3) * 3
            length = int(4 + hr(seed, 2) * (sx1 - sx0 - 10))
            for x in range(sx0 + 2 + indent, min(sx1 - 1, sx0 + 2 + indent + length)):
                if hr(x // 3, seed) > 0.25:
                    cv.put(x, row, SCREEN, 4.4 if n != 1 or row % 9 else 5.4, lit=0)
        # peu
        mx = (x0 + x1) // 2
        obox(cv, mx - 2, y1, mx + 2, DESK_Y, PLASTIC, 2.0)
        obox(cv, mx - 8, DESK_Y - 2, mx + 8, DESK_Y, PLASTIC, 2.6)
    # a la del mig, una finestra amb el logo del BCMU (ella l'ha trobat)
    cv.rect(265, 93, 295, 105, SCREEN, 2.4, lit=0)
    outline(cv, 265, 93, 295, 105, SCREEN)
    font = {'B': ['110', '101', '110', '101', '110'], 'C': ['011', '100', '100', '100', '011'],
            'M': ['10001', '11011', '10101', '10001', '10001'], 'U': ['101', '101', '101', '101', '111']}
    x = 269
    for ch in 'BCMU':
        for j, row in enumerate(font[ch]):
            for i, b in enumerate(row):
                if b == '1':
                    cv.put(x + i, 97 + j, SCREEN, 5.4, lit=0)
        x += len(font[ch][0]) + 2
    cv.glow(280, 108, 56, (90, 220, 180), 0.12)


def desk_clutter(cv):
    # teclat, ratolí, llaunes, una tassa amb llapis
    obox(cv, 258, DESK_Y - 3, 300, DESK_Y, PLASTIC, 2.6)
    for x in range(260, 299, 3):
        cv.hline(x, x + 1, DESK_Y - 2, PLASTIC, 4.0)
    cv.disc(309, DESK_Y - 1, 3, 1.4, PLASTIC, 2.6)
    for i, x in enumerate((216, 222, 344)):
        obox(cv, x, DESK_Y - 10, x + 4, DESK_Y, RED if i != 1 else YEL, 3.0)
        cv.hline(x + 1, x + 3, DESK_Y - 10, GRAYC, 4.0)
    cv.line(332, DESK_Y, 338, DESK_Y - 5, GRAYC, 2.0)                          # una llauna tombada
    obox(cv, 236, DESK_Y - 8, 243, DESK_Y, SHEET, 3.0)                       # tassa amb llapis
    cv.line(238, DESK_Y - 8, 237, DESK_Y - 13, YEL, 3.0)
    cv.line(241, DESK_Y - 8, 243, DESK_Y - 12, RED, 3.0)


def router_shelf(cv):
    # caixa de fruita de fusta fent de tauleta, amb el router a sobre
    obox(cv, 372, 146, 410, 164, CARD, 2.6)
    cv.hline(373, 409, 155, CARD, 0.6)
    cv.rect(380, 149, 402, 152, CARD, 1.2)                                     # el forat de la nansa
    # router: caixa negra amb antenes i tres ports
    obox(cv, 376, 135, 406, 146, PLASTIC, 2.2, top=1.6)
    cv.line(380, 135, 377, 124, PLASTIC, 2.6)
    cv.line(402, 135, 405, 124, PLASTIC, 2.6)
    for x in (385, 391, 397):
        cv.rect(x, 141, x + 3, 144, PLASTIC, 0.4)
        cv.flat(x + 1, 138, (90, 30, 30))                                     # llums apagats
    # fibra: presa a la paret, a prop de terra, amb el cable enrotllat que penja
    obox(cv, 420, 132, 430, 145, SHEET, 3.4)
    cv.rect(423, 136, 427, 140, PLASTIC, 1.0)
    cable(cv, [(425, 145), (434, 162), (418, 168), (414, 154)], [(10, 10, 20), (180, 140, 20), (232, 196, 50), (252, 236, 130)], 1.8, thick=2)


def hatch(cv, lit_k=1.0):
    """El passaplats de la cuina: una finestreta amb porticons, oberta, amb llum càlida de l'altra banda."""
    x0, y0, x1, y1 = 436, 88, 474, 126
    for y in range(y0 + 3, y1 - 2):
        for x in range(x0 + 3, x1 - 2):
            cv.put(x, y, WARM, 2.6 + (y - y0) / 30 * lit_k, lit=0)
    # prestatge de la cuina i una cassola, a l'altra banda
    cv.rect(x0 + 3, 108, x1 - 3, 110, WARM, 1.2, lit=0)
    cv.disc(452, 105, 6, 3, GRAYC, 2.6, lit=0)
    obox(cv, x0, y0, x1, y0 + 3, WOOD, 3.4)
    obox(cv, x0, y1 - 3, x1 + 2, y1 + 1, WOOD, 3.6)
    obox(cv, x0, y0, x0 + 2, y1, WOOD, 3.0)
    obox(cv, x1 - 2, y0, x1, y1, WOOD, 2.6)
    # porticó obert, de cantell
    cv.poly([(x0 - 8, y0 + 2), (x0, y0), (x0, y1), (x0 - 8, y1 - 2)], WOOD, 2.4)
    outline(cv, x0 - 8, y0 + 2, x0, y1 - 2, WOOD)
    cv.glow(456, 118, 40, (255, 190, 110), 0.18)


def shelf(cv):
    """Prestatge damunt l'escriptori: llibres de programació, un disc dur desmuntat, un cactus mort i
    una figura de gat que fa adeu (la que el BCMU no podrà embargar)."""
    obox(cv, 214, 58, 350, 61, WOOD, 3.4)
    for x in (220, 344):
        cv.line(x, 62, x - 4, 68, WOOD, 2.0)
    books = ((222, 34, RED), (227, 30, FABRIC), (233, 36, YEL), (238, 28, GRAYC), (245, 33, FABRIC), (250, 31, RED))
    for x, top, ramp in books:
        obox(cv, x, top + 6, x + 4, 57, ramp, 2.8)
        cv.hline(x + 1, x + 3, top + 12, ramp, 4.2)
    cv.poly([(256, 57), (266, 44), (270, 46), (260, 57)], GRAYC, 2.6)            # un llibre tombat
    obox(cv, 276, 48, 296, 57, PLASTIC, 2.4)                                    # disc dur obert
    cv.disc(286, 52, 5, 3, GRAYC, lambda nx, ny: 4.0 - ny)
    obox(cv, 304, 48, 314, 57, CARD, 2.6)                                       # test amb un cactus mort
    cv.rect(307, 38, 311, 47, WOOD, 2.2)
    cv.line(306, 42, 304, 40, WOOD, 2.2)
    cv.disc(332, 50, 6, 7, YEL, lambda nx, ny: 3.6 - ny)                        # gat de la fortuna
    cv.rect(330, 49, 334, 50, RED, 2.0)
    cv.line(338, 44, 340, 39, YEL, 3.6)


def pizza_stack(cv):
    # pila de caixes de pizza, cadascuna una mica girada
    for i, (x0, y0, dx) in enumerate(((150, 166, 0), (152, 160, 3), (148, 154, -2), (151, 148, 2), (153, 142, -1))):
        cv.poly([(x0 + dx, y0), (x0 + dx + 38, y0), (x0 + 38, y0 + 6), (x0, y0 + 6)], CARD, 3.2 - (i % 2) * 0.4)
        cv.hline(x0, x0 + 38, y0 + 6, CARD, 0)
        outline(cv, min(x0, x0 + dx), y0, max(x0, x0 + dx) + 38, y0 + 6, CARD)
    # el logo de la pizzeria a la de dalt
    cv.disc(172, 145, 5, 2, RED, 3.0)


def floor_cables(cv):
    # cables pel terra, de l'escriptori a la paret i al router
    cable(cv, [(240, 162), (250, 190), (330, 176), (380, 196), (420, 168), (400, 160)], [(8, 8, 14), (40, 40, 54), (80, 80, 100), (130, 130, 150)], 1.8, thick=2)
    cable(cv, [(232, 160), (200, 200), (120, 180), (60, 194)], [(8, 8, 14), (30, 60, 120), (56, 116, 196), (120, 176, 240)], 1.8, thick=2)
    cable(cv, [(366, 160), (380, 182), (440, 186), (466, 160)], [(8, 8, 14), (110, 30, 30), (180, 50, 50), (230, 110, 100)], 1.8, thick=1)
    # una regleta d'endolls plena
    obox(cv, 330, 168, 358, 173, SHEET, 3.0)
    for x in (334, 341, 348):
        cv.rect(x, 169, x + 3, 171, PLASTIC, 1.0)


def bg(cv):
    wall(cv)
    floor(cv)
    window(cv)
    neon_sign(cv, on=True)
    poster(cv)
    shelf(cv)
    mattress(cv)
    pizza_stack(cv)
    desk(cv)
    monitors(cv, 0)
    chair(cv)
    desk_clutter(cv)
    router_shelf(cv)
    hatch(cv)
    floor_cables(cv)
    # ombres de contacte dels mobles al terra
    cv.darken(196, 160, 368, 166, 0.45)
    cv.darken(372, 158, 412, 164, 0.4)


# ─── Props (estats) ────────────────────────────────────────────────────────

def caixa(cv):
    """La caixa del router, oberta, a terra davant de l'escriptori."""
    x0, y0, x1, y1 = 300, 172, 338, 190
    cv.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], CARD, lambda x, y: 3.0 - (0.9 if x > x1 - 8 else 0))
    cv.poly([(x0, y0), (x0 + 6, y0 - 9), (x0 + 16, y0 - 7), (x0 + 12, y0)], CARD, 3.8)     # solapa
    cv.poly([(x1, y0), (x1 + 4, y0 - 8), (x1 - 10, y0 - 9), (x1 - 12, y0)], CARD, 2.6)
    cv.rect(x0 + 2, y0 + 1, x1 - 2, y0 + 3, CARD, 0.8)                                  # l'interior fosc
    outline(cv, x0, y0, x1, y1, CARD)
    cv.rect(x0 + 8, y0 + 8, x0 + 22, y0 + 12, SHEET, 3.4)                               # l'etiqueta
    cv.hline(x0 + 9, x0 + 20, y0 + 10, PLASTIC, 1.0)
    cv.darken(x0 - 2, y1, x1 + 3, y1 + 2, 0.5)


def router_connectat(cv):
    """Els tres llums del router, en verd (decorat: es veu quan està connectat)."""
    for x in (385, 391, 397):
        cv.flat(x + 1, 138, (120, 255, 150))
        cv.flat(x + 2, 138, (60, 200, 100))
    cv.glow(392, 138, 10, (120, 255, 160), 0.4)


PROPS = {'caixa': caixa, 'router_connectat': router_connectat}


# ─── Animacions de fons ────────────────────────────────────────────────────

def _diff(frame, base):
    """Només els píxels que canvien respecte del fons (la resta, transparent)."""
    out = frame.copy()
    a, b, o = frame.load(), base.load(), out.load()
    for y in range(H):
        for x in range(W):
            if a[x, y] == b[x, y]:
                o[x, y] = (0, 0, 0, 0)
    return out


def _frames_pantalles():
    base = Canvas(light=LIGHT)
    bg(base)
    frames = []
    for i in range(8):
        cv = Canvas(light=LIGHT, img=base.img.copy())
        monitors(cv, i)
        chair(cv)
        desk_clutter(cv)
        neon_sign(cv, on=i not in (5, 6))      # el neó fa pampallugues
        frames.append(_diff(cv.img, base.img))
    return frames


ANIMS = {'pantalles': {'frames': _frames_pantalles, 'frameDuration': 220}}
