"""
L'avantdespatx del Director (Acte 3, la Vet) a 640×360: la composició de hd/rooms/bcmu_avantdespatx.py ×4/3,
dibuixada de nou. La planta noble del BCMU, Ginebra, les onze i quart:
  - la planta noble: marbre crema a dalt, arrimador de caoba amb plafons i un filet de llautó, cornisa i sostre de
    cassetons com al vestíbul; una catifa vermella gruixuda, de paret a paret, amb la sanefa d'or;
  - l'ascensor de portes daurades (el mateix del vestíbul), amb l'agulla clavada a dalt de tot;
  - l'estació del tub pneumàtic (la comuna, hd640/rooms/bcmu.py);
  - quadres de cavalls amb marcs daurats: un pura sang sol damunt la cadira d'espera (dura, de fusta, que no fa
    servir ningú) i dos cavalls al galop damunt la taula de la senyora Pons;
  - la taula de la senyora Pons (vint anys guardant la porta): el llum de banquer verd, l'interfon, el portaplomes,
    la safata; i, ben a la vista, la factura de la perruqueria canina («Le Caniche d'Or») i la seva nòmina;
  - el diploma «EMPLEAT DEL MES · 2004», que ningú no ha tornat a donar;
  - la porta doble de caoba del Director, amb la placa de llautó «DIRECTOR», i un ficus al racó.
També exporta `wall`, `sconce` i `frame` (el marc daurat del vestíbul, a 640), que fa servir el despatx.
Animacions: `tub` (una càpsula puja pel tub), `agulla` (l'agulla de l'ascensor tremola) i `ficus` (les fulles,
a l'aire condicionat).
"""
import math

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from hd.pix import Light, W, H, hr, WALNUT
from hd.rooms.comu import obox, outline, text, text_width, SHEET
from hd.rooms.pis_cuina import outline_poly
from hd.rooms.bcmu_vestibul import CREAM, DARKM, LEAF
from hd640.rooms.bcmu import MARBLE, BRASS, MAHOG, CARPET, marble, logo, tub_station

FLOOR_Y = 200
WAINS = 139             # on comença l'arrimador de caoba
DESK_TOP = 157          # el tauler de la taula de la Pons
DESK = (240, 427)
SCONCES = (133, 248, 419, 496)
TUB = (106, 88, 132, 147)

HORSE = [(20, 10, 8), (44, 22, 14), (74, 40, 22), (108, 62, 32), (146, 90, 48), (184, 126, 72)]
GRASS = [(16, 22, 12), (28, 40, 20), (44, 60, 28), (64, 82, 38), (90, 106, 52), (122, 134, 74)]
SKYO = [(60, 62, 56), (96, 96, 82), (134, 130, 106), (172, 164, 130), (206, 194, 156)]
BANKG = [(4, 22, 14), (8, 40, 24), (14, 64, 38), (24, 94, 54), (44, 128, 74), (90, 176, 116)]
PAPERW = [(70, 66, 60), (130, 124, 112), (184, 178, 164), (220, 216, 202), (244, 240, 228), (255, 252, 244)]
PAYB = [(50, 60, 70), (96, 110, 120), (150, 166, 172), (192, 206, 206), (222, 232, 230), (244, 250, 246)]
INK = (40, 36, 44)

LIGHT = Light(ambient=-0.05, vignette=(80, 40), floor_fade=(253, 40))
for _sx in SCONCES:                                                  # els apliques
    LIGHT.point(_sx, 83, r=80, k=1.1, squash=1.1, power=1.8)
LIGHT.point(320, -40, r=347, k=1.4, squash=0.6, power=1.4)           # el llum de sostre (fora de quadre)
LIGHT.point(261, 133, r=53, k=0.8, squash=1.2, power=2.0, down=True)  # el llum de banquer


# ─── Paret, sostre, terra ──────────────────────────────────────────────────

def wall(cv):
    """Marbre crema a dalt, arrimador de caoba a baix, cornisa i sostre de cassetons com al vestíbul."""
    marble(cv, 0, 21, W - 1, WAINS - 1, 4.2, seed=5)
    for x in range(0, W, 64):                                         # les juntes de les lloses
        cv.vline(x + 27, 21, WAINS - 1, MARBLE, 3.1)
        cv.vline(x + 28, 21, WAINS - 1, MARBLE, 4.6)
    cv.hline(0, W - 1, 80, MARBLE, 3.3)
    cv.hline(0, W - 1, 81, MARBLE, 4.6)
    # l'arrimador: plafons de caoba amb motllura doble
    for y in range(WAINS, FLOOR_Y - 7):
        for x in range(W):
            n = (hr(x, y // 7, 12) - 0.5) * 0.35 + math.sin(x * 0.3 + y * 0.0375) * 0.12 + (hr(x // 2, y, 13) - 0.5) * 0.1
            cv.put(x, y, MAHOG, 3.4 + n)
    for px in range(5, W, 53):
        x0, x1, y0, y1 = px, px + 43, WAINS + 8, FLOOR_Y - 15
        cv.hline(x0, x1, y0, MAHOG, 1.6)
        cv.vline(x0, y0, y1, MAHOG, 1.6)
        cv.hline(x0, x1, y1, MAHOG, 4.8)
        cv.vline(x1, y0, y1, MAHOG, 4.6)
        cv.hline(x0 + 3, x1 - 3, y0 + 3, MAHOG, 4.4)                 # el plafó de dins, en relleu
        cv.vline(x0 + 3, y0 + 3, y1 - 3, MAHOG, 4.2)
        cv.hline(x0 + 3, x1 - 3, y1 - 3, MAHOG, 2.2)
        cv.vline(x1 - 3, y0 + 3, y1 - 3, MAHOG, 2.2)
    cv.rect(0, WAINS - 3, W - 1, WAINS + 1, MAHOG, lambda x, y: 4.6 if y == WAINS - 3 else (2.2 if y == WAINS + 1 else 3.0))
    cv.hline(0, W - 1, WAINS - 1, BRASS, 4.0)
    # el sòcol
    cv.rect(0, FLOOR_Y - 7, W - 1, FLOOR_Y - 1, MAHOG,
            lambda x, y: 2.0 + (1.6 if y == FLOOR_Y - 7 else 0) + (0.6 if y == FLOOR_Y - 6 else 0))
    # la cornisa i el sostre
    cv.rect(0, 12, W - 1, 20, MAHOG, lambda x, y: 3.2 + (1.4 if y == 12 else 0) - (1.0 if y >= 19 else 0))
    cv.hline(0, W - 1, 16, BRASS, 3.6)
    cv.hline(0, W - 1, 15, BRASS, 4.4)
    for x in range(0, W, 4):                                          # les dents de la cornisa
        cv.put(x, 19, MAHOG, 1.4)
    for y in range(0, 12):
        for x in range(W):
            cell = (x % 43 in (0, 1)) or y in (0, 11)
            cv.put(x, y, CREAM, (3.0 if cell else 4.4 - (0.4 if x % 43 in (2, 3) or y == 1 else 0)) - y * 0.04)


def sconce(cv, cx):
    """Un aplic de llautó amb dues tulipes de vidre glaçat."""
    cv.disc(cx, 92, 2.6, 3.4, BRASS, lambda nx, ny: 4.0 - ny - nx * 0.4)   # la placa de la paret
    cv.rect(cx - 1, 83, cx + 1, 93, BRASS, lambda x, y: 4.2 if x == cx - 1 else 3.4)
    cv.hline(cx - 6, cx + 6, 88, BRASS, 4.2)
    cv.hline(cx - 5, cx + 5, 89, BRASS, 2.6)
    for dx in (-6, 6):
        cv.vline(cx + dx, 83, 88, BRASS, 3.8)
        cv.hline(cx + dx - 2, cx + dx + 2, 83, BRASS, 4.6)            # la copa
        cv.disc(cx + dx, 80, 3.0, 2.8, [(200, 180, 140), (250, 236, 200), (255, 250, 236)], lambda nx, ny: 1.6 - ny, lit=0)
    cv.glow(cx, 80, 21, (255, 226, 160), 0.35)


def floor(cv):
    """Catifa vermella gruixuda de paret a paret, amb una sanefa daurada i el pèl que fa aigües."""
    for y in range(FLOOR_Y, H):
        dep = (y - FLOOR_Y) / (H - FLOOR_Y)
        for x in range(W):
            u = (x - W / 2) / (0.55 + dep * 0.9) + W / 2
            n = (hr(x, y, 21) - 0.5) * 0.6 + (hr(x // 4, y // 3, 22) - 0.5) * 0.4
            v = (y - FLOOR_Y) * 1.7 / (1 + dep * 0.6)
            pile = math.sin(u * 0.06 + y * 0.225) * 0.15
            lattice = abs(((u + v * 1.6) % 37) - 18.5) < 0.9 or abs(((u - v * 1.6) % 37) - 18.5) < 0.9
            cv.put(x, y, CARPET, 3.4 + n + pile + dep * 0.3 - (0.7 if lattice and y > FLOOR_Y + 16 else 0))
    # la sanefa: dues línies d'or i un rombe repetit, tocant la paret
    for x in range(W):
        cv.put(x, FLOOR_Y + 4, BRASS, 2.8 + (hr(x, 4) - 0.5) * 0.6)
        cv.put(x, FLOOR_Y + 12, BRASS, 2.6 + (hr(x, 5) - 0.5) * 0.6)
    for mx in range(8, W, 16):
        for dy in (-2, -1, 0, 1, 2):
            w = 3 - abs(dy)
            cv.hline(mx - w, mx + w, FLOOR_Y + 8 + dy, BRASS, 2.4 + (0.6 if dy < 0 else 0))
        cv.put(mx, FLOOR_Y + 8, CARPET, 3.0)                          # l'ull del rombe
    # ombra de la paret sobre la catifa
    cv.darken(0, FLOOR_Y, W - 1, FLOOR_Y + 2, 0.5)


# ─── L'ascensor ────────────────────────────────────────────────────────────

def elevator(cv, needle=0):
    """Portes daurades art déco (com al vestíbul), amb l'indicador d'agulla al màxim: la planta noble.

    `needle`: quants graus recula l'agulla des del màxim (per a l'animació: tremola, però no baixa mai)."""
    x0, y0, x1, y1 = 23, 59, 84, FLOOR_Y - 1
    obox(cv, x0 - 4, y0 - 4, x1 + 4, y1, MARBLE, 3.0)
    cv.hline(x0 - 3, x1 + 3, y0 - 2, MARBLE, 4.6)
    for lx0, lx1 in ((x0, (x0 + x1) // 2), ((x0 + x1) // 2 + 1, x1)):
        cv.rect(lx0, y0, lx1, y1, BRASS, lambda x, y: 3.4 + (0.9 if (x + y) % 16 < 3 else 0) - (0.6 if x in (lx0, lx1) else 0))
        outline(cv, lx0 + 3, y0 + 3, lx1 - 3, y1 - 3, [BRASS[2]])     # el filet gravat
        mx = (lx0 + lx1) // 2
        for a in range(0, 181, 15):                                   # el sol ixent
            r = math.radians(a + 180)
            cv.line(mx, 117, round(mx + math.cos(r) * 11), round(117 + math.sin(r) * 11), BRASS, 5.0 if a % 30 == 0 else 4.2)
        cv.disc(mx, 117, 3.5, 3.5, BRASS, lambda nx, ny: 5.6 - ny * 0.6)
        cv.hline(mx - 12, mx + 12, 118, BRASS, 2.4)
        cv.rect(lx0 + 4, 136, lx1 - 4, 137, BRASS, 2.4)
        cv.rect(lx0 + 4, y1 - 14, lx1 - 4, y1 - 5, BRASS, lambda x, y: 2.8 + (1.2 if y == y1 - 14 else 0))   # el sòcol de puntades
    cv.vline((x0 + x1) // 2, y0, y1, BRASS, 1.0)
    outline(cv, x0, y0, x1, y1, BRASS)
    # l'indicador d'agulla, a dalt de tot
    cx, cy = (x0 + x1) // 2, 45
    cv.disc(cx, cy, 13, 11, BRASS, lambda nx, ny: 4.0 - ny * 0.6)
    cv.disc(cx, cy, 11, 8, [(30, 24, 16), (230, 222, 196), (248, 244, 228)], 1.6, lit=0)
    cv.rect(cx - 15, cy, cx + 15, cy + 8, MARBLE, 4.4)
    cv.hline(cx - 14, cx + 14, cy, BRASS, 3.6)
    cv.hline(cx - 14, cx + 14, cy + 1, BRASS, 2.4)
    for k in range(5):
        a = math.radians(180 + k * 45)
        cv.flat(round(cx + math.cos(a) * 8), round(cy + math.sin(a) * 6), (60, 40, 20))
    for k in range(4):                                                # les marques petites, entre les grosses
        a = math.radians(202.5 + k * 45)
        cv.flat(round(cx + math.cos(a) * 9), round(cy + math.sin(a) * 6.6), (120, 100, 70))
    a = math.radians(-needle)
    cv.line(cx, cy - 1, round(cx + math.cos(a) * 8), round(cy - 1 + math.sin(a) * 8), [(150, 20, 20)], 0, lit=0)
    cv.flat(cx, cy - 1, (40, 24, 16))
    # el botó
    obox(cv, x1 + 7, 125, x1 + 11, 141, BRASS, 3.4)
    cv.disc(x1 + 9, 133, 1.6, 1.6, [(255, 220, 140)], 0, lit=0)
    cv.darken(x0 - 4, FLOOR_Y, x1 + 4, FLOOR_Y + 3, 0.4)


# ─── Els quadres de cavalls ────────────────────────────────────────────────

def frame(cv, x0, y0, x1, y1):
    """Un marc daurat amb motllura (el del vestíbul, a 640): bisell de fora, filet de perles i bisell de dins."""
    obox(cv, x0, y0, x1, y1, BRASS, 4.0, top=1.2, side=-1.0)
    for x in range(x0 + 2, x1 - 1, 3):                                # el filet de perles
        cv.put(x, y0 + 1, BRASS, 5.2)
        cv.put(x, y1 - 1, BRASS, 3.4)
    for y in range(y0 + 2, y1 - 1, 3):
        cv.put(x0 + 1, y, BRASS, 4.8)
        cv.put(x1 - 1, y, BRASS, 3.0)
    obox(cv, x0 + 3, y0 + 3, x1 - 3, y1 - 3, BRASS, 2.8)
    for (a, b) in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):           # els cantons, amb un floró
        cv.flat(a, b, BRASS[6])
        cv.put(a + (1 if a == x0 else -1), b + (1 if b == y0 else -1), BRASS, 5.8)
    cv.darken(x1 + 1, y0 + 3, x1 + 3, y1 + 3, 0.5)
    cv.darken(x0 + 3, y1 + 1, x1, y1 + 2, 0.35)


def landscape(cv, x0, y0, x1, y1, seed, hz, tree=None):
    """Fons d'oli: cel de tempesta anglesa, un turó verd fosc, el terra d'herba i, si cal, un roure."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            n = (hr(x // 3, y // 2, seed) - 0.5) * 0.6
            if y < hz + math.sin(x * 0.0675 + seed) * 2.7:
                cloud = math.sin(x * 0.11 + seed) * math.sin(y * 0.3 + x * 0.04) * 0.5
                cv.put(x, y, SKYO, 3.0 - (y - y0) * 0.03 + n + cloud + math.sin(x * 0.15 + y * 0.225) * 0.2)
            else:
                cv.put(x, y, GRASS, 2.6 + (y - hz) * 0.0375 + n)
    for x in range(x0, x1 + 1):                                       # un turó llunyà
        top = hz - 4 - int(5.3 * math.sin((x - x0) * 0.045 + seed))
        for y in range(top, int(hz + 1)):
            cv.put(x, y, GRASS, 1.6 + (hr(x // 2, y, seed + 1) - 0.5) * 0.4)
    if tree is not None:                                              # un roure fosc, a la Stubbs
        tx = tree
        cv.line(tx, hz + 1, tx, hz - 9, HORSE, 0.6)
        for i in range(22):
            a = hr(i, seed + 20) * 2 * math.pi
            r = math.sqrt(hr(i, seed + 21))
            cv.disc(tx + math.cos(a) * r * 7, hz - 15 + math.sin(a) * r * 6, 2.4, 1.8, GRASS,
                    lambda nx, ny, v=1.4 - math.sin(a) * r * 0.5: v - ny * 0.4)


def horse(cv, x, y, s=1.0, d=1, gallop=False, coat=3.0, ramp=HORSE):
    """Un cavall de perfil a l'estil de Stubbs (x, y: el centre del cos; d=1 mira a la dreta)."""
    X = lambda v: round(x + v * s * d)
    Y = lambda v: round(y + v * s)
    lv = lambda nx, ny: coat - ny * 0.9 - nx * d * 0.2
    # les potes (de dues files, fosques de baix: calces negres), amb el peu
    if gallop:
        legs = ((-9, 2, -16, 7), (-7, 2, -12, 9), (7, 2, 14, 6), (9, 2, 15, 1))
    else:
        legs = ((-9, 2, -10, 11), (-6, 2, -6, 11), (7, 2, 7, 11), (9, 2, 10, 11))
    for k, (a, b, c, e) in enumerate(legs):
        far = k in (1, 2)
        for o in (0, 1):
            cv.line(X(a) + o, Y(b), X(c) + o, Y(e), ramp, coat - (1.8 if far else 0.8) - o * 0.6)
        cv.line(X(a + (c - a) * 0.7), Y(b + (e - b) * 0.7), X(c), Y(e), ramp, 0.6)   # la calça
        cv.hline(X(c), X(c) + 1, Y(e), ramp, 0.2)
        cv.flat(X(c) + (2 if d > 0 else -1), Y(e), ramp[0])           # el casc
    # el cos, el coll i el cap
    cv.disc(x, y, 11.5 * s, 5 * s, ramp, lv)
    cv.disc(X(-6), Y(-1), 4 * s, 3 * s, ramp, lambda nx, ny: coat + 0.3 - ny * 0.8)   # l'anca
    cv.poly([(X(5), Y(-3)), (X(10), Y(-12)), (X(15), Y(-11)), (X(12), Y(2))], ramp, lambda px, py: coat + 0.3 - (py - y) * 0.03)
    cv.poly([(X(10), Y(-12)), (X(14), Y(-15)), (X(20), Y(-8)), (X(19), Y(-6)), (X(16), Y(-6)), (X(13), Y(-9))], ramp, coat + 0.5)
    cv.line(X(-8), Y(-4), X(4), Y(-4.5), ramp, coat + 0.9)            # la llum del llom
    cv.flat(X(15), Y(-11), ramp[0])                                    # l'ull
    cv.flat(X(19), Y(-7), ramp[0])                                     # el morro
    cv.flat(X(18), Y(-8), ramp[1])
    cv.line(X(12), Y(-15), X(13), Y(-17), ramp, coat - 0.4)            # l'orella
    for k in range(13):                                                # la crinera
        cv.flat(X(10 - k * 0.35), Y(-12 + k * 0.9), ramp[0])
    tail = 6 if not gallop else 0
    for k, o in enumerate((-0.6, 0, 0.6)):                             # la cua, en tres flocs
        cv.line(X(-11), Y(-2), X(-15 - k * 0.5), Y(tail + o + k * 0.5), ramp, 0.3 + k * 0.25)


def paintings(cv):
    """Tres quadres de cavalls amb marc daurat: un pura sang sol, dos al galop i un cap de cavall."""
    # el pura sang, damunt la cadira d'espera
    frame(cv, 141, 43, 224, 107)
    landscape(cv, 146, 48, 219, 102, 3, 80, tree=157)
    horse(cv, 179, 80, 1.53, 1, coat=3.6)
    # dos cavalls al galop, damunt la taula de la Pons
    frame(cv, 272, 37, 389, 109)
    landscape(cv, 277, 42, 384, 104, 7, 77)
    horse(cv, 309, 85, 1.47, 1, gallop=True, coat=2.4)
    horse(cv, 349, 81, 1.53, 1, gallop=True, coat=3.8)
    jock = [(344, 72), (346, 67), (351, 66), (352, 72)]                # el genet, ajupit
    cv.poly(jock, [(150, 26, 26), (210, 56, 46)], lambda x, y: 1 if x < 349 else 0)
    cv.hline(346, 350, 69, [(240, 236, 220)], 0)                       # la faixa de la casaca
    cv.disc(349, 64.5, 1.6, 1.6, [(40, 30, 60)], 0)                    # la gorra
    cv.flat(351, 64, (40, 30, 60))
    cv.flat(345, 73, (230, 226, 210))
    cv.line(352, 70, 357, 71, [(30, 20, 14)], 0)                       # les regnes
    # un cap de cavall, al racó de la dreta: un bai fosc amb l'estrella blanca
    frame(cv, 605, 53, 635, 96)
    landscape(cv, 610, 58, 630, 91, 5, 83)
    pts = [(612, 91), (615, 77), (619, 67), (623, 61), (625, 61), (629, 71), (629, 75), (625, 73), (623, 71), (623, 80), (625, 91)]
    cv.poly(pts, HORSE, lambda x, y: 3.0 - (x - 612) * 0.06 + (0.8 if x < 617 else 0))
    cv.line(621, 60, 621, 57, HORSE, 2.4)                               # l'orella
    cv.line(622, 61, 622, 58, HORSE, 1.4)
    for k in range(9):                                                  # la crinera
        cv.flat(617 - k // 3, 65 + k * 2, HORSE[0])
    cv.flat(624, 65, HORSE[0])                                          # l'ull
    cv.flat(624, 64, HORSE[5])
    cv.line(625, 64, 628, 72, [(226, 216, 196)], 0)                     # l'estrella
    cv.flat(628, 75, HORSE[0])
    cv.line(623, 76, 627, 74, HORSE, 1.2)                               # la quixada
    # la placa del galop
    obox(cv, 315, 112, 347, 119, BRASS, 4.6)
    cv.hline(319, 343, 115, BRASS, 2.4)
    cv.hline(323, 339, 117, BRASS, 3.0)


# ─── El mobiliari de l'esquerra ────────────────────────────────────────────

def waiting_chair(cv):
    """Una cadira de fusta, de respatller recte, que no fa servir ningú: no s'hi fa esperar ningú."""
    x0, x1 = 149, 179
    for lx in (x0 + 1, x1 - 1):                                       # el respatller
        cv.rect(lx - 1, 131, lx + 1, 171, WALNUT, lambda x, y, l=lx: 5.4 + (0.4 if x == l - 1 else 0))
    for k in range(3):
        cv.rect(x0 + 1, 133 + k * 8, x1 - 1, 136 + k * 8, WALNUT, lambda x, y, k=k, b=133 + k * 8: 6.0 - k * 0.3 + (0.4 if y == b else 0))
    outline(cv, x0, 131, x1, 171, WALNUT)
    cv.rect(x0 - 3, 171, x1 + 3, 176, WALNUT, lambda x, y: 6.4 if y == 171 else 5.0)
    outline(cv, x0 - 3, 171, x1 + 3, 176, WALNUT)
    for lx in (x0 - 1, x0 + 3, x1 - 3, x1 + 1):                       # les potes
        cv.rect(lx, 177, lx + 1, 203, WALNUT, 4.6 if lx < x1 - 4 else 3.6)
    cv.hline(x0, x1, 191, WALNUT, 4.2)
    cv.hline(x0, x1, 192, WALNUT, 3.0)
    cv.darken(x0 - 5, 201, x1 + 8, 205, 0.5)


def ficus(cv, cx, top=128, sway=None):
    """Un ficus en un test de llautó: un tronc prim i una copa atapeïda de fulles.

    `sway`: fase (radiants) del corrent de l'aire condicionat que en gronxa les fulles (animació `ficus`)."""
    cv.line(cx, 179, cx - 1, top + 19, MAHOG, 3.0)
    cv.line(cx + 1, 179, cx, top + 24, MAHOG, 2.2)
    cv.line(cx - 1, top + 29, cx - 8, top + 19, MAHOG, 2.6)
    cv.line(cx, top + 24, cx + 7, top + 13, MAHOG, 2.6)
    for i in range(125):
        a = hr(i, 11) * 2 * math.pi
        r = math.sqrt(hr(i, 12))
        lx = cx + math.cos(a) * r * 15
        ly = top + 16 + math.sin(a) * r * 13
        if sway is not None:                                          # les de dalt es mouen més
            h = min(1.0, max(0.0, (top + 27 - ly) / 21))
            lx += h * (1.1 * math.sin(sway) + 0.35 * math.sin(2 * sway + i * 0.3))
            ly += h * 0.4 * math.cos(sway + i * 0.3)
        shade = 3.6 - math.sin(a) * r * 0.9 - (lx - cx) * 0.03 + (hr(i, 13) - 0.5) * 0.8
        cv.disc(lx, ly, 2.6, 1.8, LEAF, lambda nx, ny, v=shade: v - ny * 0.6)
        if hr(i, 14) > 0.75:                                          # el nervi brillant d'algunes fulles
            cv.put(round(lx) - 1, round(ly), LEAF, shade + 1.0)
    obox(cv, cx - 8, 179, cx + 8, 201, BRASS, 3.4)
    for yy in (185, 195):                                             # els anells del test
        cv.hline(cx - 7, cx + 7, yy, BRASS, 4.6)
    cv.rect(cx - 9, 177, cx + 9, 180, BRASS, lambda x, y: 5.2 if y == 177 else 4.0)
    outline(cv, cx - 9, 177, cx + 9, 180, BRASS)
    cv.darken(cx - 10, 201, cx + 12, 205, 0.45)


# ─── La taula de la senyora Pons ───────────────────────────────────────────

def desk(cv):
    """Una taula de secretària de caoba: tauler vist una mica de dalt, frontal de plafons i calaixos."""
    x0, x1 = DESK
    # el tauler (amb una mica de perspectiva) i el cantell
    for y in range(DESK_TOP - 12, DESK_TOP + 1):
        for x in range(x0 - 3, x1 + 4):
            n = (hr(x // 8, y, 31) - 0.5) * 0.3 + math.sin(x * 0.05 + y * 0.6) * 0.08
            cv.put(x, y, MAHOG, 4.4 + n + (y - DESK_TOP) * 0.045)
    cv.hline(x0 - 3, x1 + 3, DESK_TOP - 12, MAHOG, 5.4)
    cv.rect(x0 - 3, DESK_TOP + 1, x1 + 3, DESK_TOP + 4, MAHOG,
            lambda x, y: 5.6 if y == DESK_TOP + 1 else (2.6 if y == DESK_TOP + 4 else 3.6))
    outline(cv, x0 - 3, DESK_TOP - 12, x1 + 3, DESK_TOP + 4, MAHOG)
    # la pell verda del sobretaula (el cartapàs), amb el filet daurat
    cv.rect(275, DESK_TOP - 9, 363, DESK_TOP - 1, BANKG, lambda x, y: 2.4 + (hr(x, y, 2) - 0.5) * 0.4)
    outline(cv, 275, DESK_TOP - 9, 363, DESK_TOP - 1, BANKG)
    cv.hline(277, 361, DESK_TOP - 7, BRASS, 2.0)
    cv.hline(276, 362, DESK_TOP - 1, BRASS, 2.6)
    # el frontal: plafons i calaixos amb tiradors de llautó
    y0, y1 = DESK_TOP + 5, FLOOR_Y + 1
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            n = (hr(x, y // 5, 33) - 0.5) * 0.3 + math.sin(x * 0.225 + y * 0.03) * 0.1
            cv.put(x, y, MAHOG, 3.0 + n - (0.8 if x > x1 - 4 else 0))
    outline(cv, x0, y0, x1, y1, MAHOG)
    for (a, b) in ((x0 + 5, x0 + 48), (x1 - 48, x1 - 5)):              # les dues columnes de calaixos
        for k in range(3):
            cy0 = y0 + 3 + k * 12
            obox(cv, a, cy0, b, cy0 + 9, MAHOG, 3.6)
            m = (a + b) // 2
            cv.rect(m - 4, cy0 + 4, m + 4, cy0 + 5, BRASS, lambda x, y: 4.8 if y == cy0 + 4 else 3.4)
            cv.flat(m - 4, cy0 + 3, BRASS[4])
            cv.flat(m + 4, cy0 + 3, BRASS[4])
    obox(cv, x0 + 59, y0 + 3, x1 - 59, y1 - 5, MAHOG, 2.6)             # el plafó del mig
    obox(cv, x0 + 64, y0 + 7, x1 - 64, y1 - 9, MAHOG, 3.4)
    logo(cv, (x0 + x1) // 2, (y0 + y1) // 2 - 1, k=1.6, lvl=4.4)
    cv.darken(x0 - 3, FLOOR_Y + 2, x1 + 7, FLOOR_Y + 6, 0.5)


def bankers_lamp(cv):
    """El llum de banquer: peu de llautó i la pantalla de vidre verd encesa."""
    cx = 259
    cv.disc(cx, DESK_TOP - 7, 9, 2.7, BRASS, lambda nx, ny: 4.2 - ny)
    cv.rect(cx - 1, DESK_TOP - 24, cx, DESK_TOP - 8, BRASS, lambda x, y: 5.0 if x == cx - 1 else 3.8)
    cv.disc(cx, DESK_TOP - 15, 1.6, 1.0, BRASS, 4.6)                   # l'anella del peu
    pts = [(cx - 13, DESK_TOP - 24), (cx - 9, DESK_TOP - 32), (cx + 9, DESK_TOP - 32), (cx + 13, DESK_TOP - 24)]
    cv.poly(pts, BANKG, lambda x, y: 4.2 - (y - (DESK_TOP - 32)) * 0.22 - (0.6 if x > cx + 5 else 0) + (0.8 if x == cx - 6 else 0), lit=0.3)
    outline_poly(cv, pts, BANKG)
    cv.hline(cx - 8, cx + 8, DESK_TOP - 32, BRASS, 4.0)
    cv.hline(cx - 13, cx + 13, DESK_TOP - 23, [(255, 240, 190)], 0, lit=0)
    cv.glow(cx, DESK_TOP - 19, 24, (255, 232, 170), 0.4)
    cv.line(cx + 3, DESK_TOP - 23, cx + 3, DESK_TOP - 17, BRASS, 5.0)  # la cadeneta
    cv.flat(cx + 3, DESK_TOP - 16, BRASS[6])


def intercom(cv):
    """L'interfon amb el Director: una caixa negra amb botons i el llum vermell (que mai no s'encén)."""
    obox(cv, 373, DESK_TOP - 16, 400, DESK_TOP - 5, DARKM, 2.4)
    cv.rect(376, DESK_TOP - 13, 386, DESK_TOP - 8, DARKM, 1.0)        # la reixeta
    for k in range(3):
        cv.hline(376, 386, DESK_TOP - 13 + k * 2, DARKM, 3.0)
    for k in range(3):
        cv.rect(389 + k * 3, DESK_TOP - 13, 390 + k * 3, DESK_TOP - 11, MARBLE, 5.4)
    cv.flat(396, DESK_TOP - 8, (110, 20, 20))
    cv.flat(397, DESK_TOP - 8, (90, 16, 16))
    # el telèfon de disc, al costat
    body = [(403, DESK_TOP - 4), (405, DESK_TOP - 13), (419, DESK_TOP - 13), (421, DESK_TOP - 4)]
    cv.poly(body, DARKM, lambda x, y: 2.6 + (0.6 if x < 408 else 0))
    outline_poly(cv, body, DARKM)
    cv.rect(401, DESK_TOP - 17, 423, DESK_TOP - 14, DARKM, lambda x, y: 3.4 if y == DESK_TOP - 17 else 2.2)
    outline(cv, 401, DESK_TOP - 17, 423, DESK_TOP - 14, DARKM)
    cv.rect(400, DESK_TOP - 18, 403, DESK_TOP - 14, DARKM, 2.8)       # els dos auriculars
    cv.rect(421, DESK_TOP - 18, 424, DESK_TOP - 14, DARKM, 2.8)
    cv.disc(412, DESK_TOP - 8, 3.4, 3.0, [(230, 222, 196)], 0, lit=0.4)
    cv.ring(412, DESK_TOP - 8, 3.0, BRASS, 3.6, step=24)
    cv.flat(412, DESK_TOP - 8, (40, 36, 44))


def pen_holder(cv):
    """El portaplomes de llautó i una pila de carpetes ben quadrades."""
    obox(cv, 313, DESK_TOP - 22, 321, DESK_TOP - 10, BRASS, 3.6)
    cv.hline(314, 320, DESK_TOP - 16, BRASS, 2.4)
    for k, (dx, h, col) in enumerate(((315, 8, (30, 30, 50)), (317, 11, (150, 30, 30)), (319, 7, (40, 40, 40)))):
        cv.line(dx, DESK_TOP - 22, dx + (k - 1), DESK_TOP - 22 - h, [col], 0)
        cv.flat(dx + (k - 1), DESK_TOP - 22 - h, BRASS[5])
    # les carpetes
    for k, col in enumerate(((60, 70, 110), (150, 120, 70), (110, 40, 40))):
        y0 = DESK_TOP - 13 - k * 3
        cv.rect(359 - k, y0, 369 - k, y0 + 2, [col], 0)
        cv.hline(359 - k, 369 - k, y0 + 2, [tuple(c * 2 // 3 for c in col)], 0)
        cv.flat(369 - k, y0 + 1, (226, 220, 206))                     # el full que en surt


def _paper(cv, x0, x1, ramp):
    """Un full ajagut damunt la taula, vist de biaix (una mica més estret pel cantó del fons)."""
    y0, y1 = 147, DESK_TOP - 1
    pts = [(x0, y1), (x0 + 1, y0), (x1 - 1, y0), (x1, y1)]
    cv.poly(pts, ramp, lambda x, y: 4.6 - (y - y0) * 0.075)
    outline_poly(cv, pts, ramp)
    cv.darken(x0 + 1, y1 + 1, x1 + 1, y1 + 1, 0.6)


def factura(cv):
    """La factura de «Le Caniche d'Or»: el capçal amb un caniche daurat, ratlles i el total en vermell."""
    _paper(cv, 287, 308, PAPERW)
    cv.sprite(['.aa.', 'aaa.', 'aaaa', 'a..a'], 290, 148, {'a': (BRASS, 4.6)})   # el caniche
    cv.hline(295, 305, 149, [INK], 0)
    cv.hline(295, 301, 150, [(150, 120, 60)], 0)
    for k, w in enumerate((12, 10, 11)):
        cv.hline(291, 291 + w, 152 + k, [(130, 124, 120)], 0)
    cv.hline(299, 306, 155, [(200, 30, 30)], 0)                       # 4.200 €


def nomina(cv):
    """La nòmina de la Pons: paper verd clar del banc, el logotip, dues columnes i el net a pagar."""
    _paper(cv, 329, 351, PAYB)
    cv.sprite(['aa.', 'abb', 'ab.'], 332, 148, {'a': (BRASS, 4.4), 'b': (BRASS, 5.6)})
    cv.hline(337, 348, 149, [(40, 60, 80)], 0)
    for k in range(3):
        cv.hline(333, 340, 151 + k, [(110, 126, 134)], 0)
        cv.hline(344, 348, 151 + k, [(110, 126, 134)], 0)
    cv.hline(342, 348, 155, [(30, 40, 70)], 0)                        # 2.900 €


# ─── A la paret de la Pons ─────────────────────────────────────────────────

def employee(cv):
    """El diploma «EMPLEAT DEL MES · 2004»: un marc negre, una foto passada pel sol i les lletres."""
    x0, y0, x1, y1 = 429, 61, 483, 112
    obox(cv, x0, y0, x1, y1, DARKM, 2.0)
    cv.hline(x0 + 1, x1 - 1, y0 + 1, DARKM, 3.6)
    cv.rect(x0 + 3, y0 + 3, x1 - 3, y1 - 3, SHEET, lambda x, y: 4.8 - (0.3 if (x + y) % 7 == 0 else 0))
    outline(cv, x0 + 5, y0 + 5, x1 - 5, y1 - 5, [(200, 170, 110)])    # el filet daurat del paper
    cx = (x0 + x1) // 2
    cv.rect(cx - 9, y0 + 7, cx + 9, y0 + 22, [(150, 150, 160), (196, 190, 184)], lambda x, y: 0.5 + (y - y0) * 0.03)
    cv.disc(cx, y0 + 13, 4, 4.8, [(140, 110, 100), (176, 150, 136)], 0.6)   # la cara
    cv.rect(cx - 4, y0 + 8, cx + 4, y0 + 9, [(120, 100, 96)], 0)           # els cabells
    cv.rect(cx - 7, y0 + 18, cx + 7, y0 + 22, [(100, 100, 120)], 0)
    cv.hline(cx - 1, cx + 1, y0 + 18, [(200, 200, 210)], 0)                   # el coll de la camisa
    for k, word in enumerate(('EMPLEAT', 'DEL MES', '2004')):
        text(cv, word, (x0 + x1 + 1) // 2 - text_width(word) // 2, y0 + 26 + k * 7, [INK], 0,
             flat=(60, 50, 40) if k < 2 else (150, 110, 30))
    cv.darken(x1 + 1, y0 + 3, x1 + 3, y1 + 3, 0.5)


# ─── La porta del Director ─────────────────────────────────────────────────

def door(cv):
    """La porta doble de caoba: marc gruixut, plafons en relleu, poms de llautó i la placa «DIRECTOR»."""
    x0, y0, x1, y1 = 512, 59, 587, FLOOR_Y - 1
    # el marc amb el frontó
    obox(cv, x0 - 5, y0 - 5, x1 + 5, y1, MAHOG, 4.2, top=1.2)
    cv.vline(x0 - 3, y0 - 3, y1, MAHOG, 4.8)
    cv.vline(x1 + 3, y0 - 3, y1, MAHOG, 2.8)
    obox(cv, x0 - 8, 48, x1 + 8, y0 - 5, MAHOG, 4.0, top=1.4)
    cv.hline(x0 - 7, x1 + 7, 51, BRASS, 4.0)
    for x in range(x0 - 6, x1 + 7, 4):                                # les dents del frontó
        cv.put(x, 53, MAHOG, 2.0)
    # les dues fulles
    for lx0, lx1 in ((x0, (x0 + x1) // 2), ((x0 + x1) // 2 + 1, x1)):
        for y in range(y0, y1 + 1):
            for x in range(lx0, lx1 + 1):
                n = (hr(x, y // 8, 41) - 0.5) * 0.3 + math.sin(x * 0.375 + y * 0.0225) * 0.12
                cv.put(x, y, MAHOG, 3.4 + n)
        for (py0, py1) in ((y0 + 7, y0 + 61), (y0 + 69, y1 - 8)):
            a, b = lx0 + 5, lx1 - 5
            cv.rect(a, py0, b, py1, MAHOG, 3.8)
            cv.hline(a, b, py0, MAHOG, 1.4)
            cv.vline(a, py0, py1, MAHOG, 1.6)
            cv.hline(a, b, py1, MAHOG, 5.2)
            cv.vline(b, py0, py1, MAHOG, 5.0)
            cv.rect(a + 4, py0 + 4, b - 4, py1 - 4, MAHOG, 3.1)         # el plafó en relleu, amb bisell
            cv.hline(a + 4, b - 4, py0 + 4, MAHOG, 4.6)
            cv.vline(a + 4, py0 + 4, py1 - 4, MAHOG, 4.4)
            cv.hline(a + 4, b - 4, py1 - 4, MAHOG, 2.0)
            cv.vline(b - 4, py0 + 4, py1 - 4, MAHOG, 2.2)
        outline(cv, lx0, y0, lx1, y1, MAHOG)
    # els poms
    cx = (x0 + x1) // 2
    for px in (cx - 5, cx + 7):
        cv.disc(px, 133, 2.7, 2.7, BRASS, lambda nx, ny: 4.6 - ny - nx * 0.4)
        cv.flat(px - 1, 132, BRASS[6])
        cv.rect(px - 1, 137, px, 141, BRASS, 3.0)                     # el bocallave
        cv.flat(px, 139, MAHOG[0])
    # la placa
    s = 'DIRECTOR'
    w = text_width(s)
    obox(cv, cx - w // 2 - 7, 75, cx + w // 2 + 7, 88, BRASS, 4.4, top=1.0)
    for sx in (cx - w // 2 - 5, cx + w // 2 + 5):                     # els cargols
        cv.flat(sx, 81, BRASS[1])
    text(cv, s, cx - w // 2, 79, [(40, 26, 10)], 0, flat=(50, 32, 12))
    cv.darken(x0 - 5, FLOOR_Y, x1 + 8, FLOOR_Y + 4, 0.45)


# ─── Composició ────────────────────────────────────────────────────────────

def bg(cv, capsule=None, needle=0, sway=None):
    wall(cv)
    floor(cv)
    for sx in SCONCES:
        sconce(cv, sx)
    elevator(cv, needle)
    tub_station(cv, *TUB, capsule=capsule)
    paintings(cv)
    employee(cv)
    waiting_chair(cv)
    ficus(cv, 216, sway=sway)
    door(cv)
    ficus(cv, 616, top=123, sway=None if sway is None else sway + 2.2)
    desk(cv)
    bankers_lamp(cv)
    pen_holder(cv)
    intercom(cv)
    factura(cv)
    nomina(cv)


PROPS = {}


def _anim(states):
    """Fotogrames diferencials (només el que canvia respecte del fons) per a una llista d'arguments de `bg`;
    `None` és un fotograma buit."""
    from hd.pix import Canvas
    from hd.rooms.comu import _diff
    base = Canvas(light=LIGHT)
    bg(base)
    empty = None
    frames = []
    for kw in states:
        if kw is None:
            empty = empty or _diff(base.img, base.img)
            frames.append(empty)
        else:
            cv = Canvas(light=LIGHT)
            bg(cv, **kw)
            frames.append(_diff(cv.img, base.img))
    return frames


# ─── Animació: una càpsula que puja pel tub ───────────────────────────────
# El banc no para: de tant en tant, una càpsula surt disparada cap als pisos de dalt.
# (A 640, el doble de fotogrames a la meitat de temps: la mateixa pujada, més suau.)

ANIM_N = 60
CAPSULE = (88, 78, 67, 56, 45, 35, 24, 14, 3, -8, -19)    # la y de la càpsula als primers fotogrames; la resta, buit


def _frames():
    return _anim([{'capsule': CAPSULE[i]} if i < len(CAPSULE) else None for i in range(ANIM_N)])


ANIMS = {'tub': {'frames': _frames, 'frameDuration': 75}}


# ─── Animació: l'agulla de l'ascensor ─────────────────────────────────────
# Clavada a dalt de tot, però de tant en tant fa un tremolor (l'ascensor vol baixar i no el deixen).

NEEDLE = (0,) * 24 + (5, 9, 13, 16, 11, 6, 9, 12, 8, 3, 1, 0, 3, 5, 2, 0)   # graus que recula a cada fotograma


def _needle_frames():
    return _anim([{'needle': d} if d else None for d in NEEDLE])


ANIMS['agulla'] = {'frames': _needle_frames, 'frameDuration': 60}


# ─── Animació: els ficus, a l'aire condicionat ────────────────────────────
# L'únic que es mou a la planta noble quan no passa cap càpsula: les fulles dels dos ficus, cadascun al seu ritme.

def _ficus_frames():
    return _anim([{'sway': i * math.tau / 12} for i in range(12)])


ANIMS['ficus'] = {'frames': _ficus_frames, 'frameDuration': 153}


# ─── Geometria a 640 ───────────────────────────────────────────────────────

GEOMETRIA = {
    'things': {
        'ascensor': {'rect': (19, 31, 95, 200), 'walk': (53, 248)},
        'tub': {'rect': (106, 88, 138, 147), 'walk': (120, 248)},
        'factura': {'rect': (285, 145, 310, 158), 'walk': (296, 251)},
        'nomina': {'rect': (327, 145, 353, 158), 'walk': (341, 251)},
        'porta': {'rect': (504, 48, 595, 200), 'walk': (549, 248)},
    },
    'spawns': {'pons': (467, 245), 'vet': (200, 259)},
    'walkable': [(19, 236), (621, 236), (632, 271), (8, 271)],
}
