"""
El moll de càrrega del BCMU (Escena 4b, l'Iri). Art definitiu:
  - la part de servei de l'edifici: bloc de formigó pintat, bigues i fluorescents, terra de formigó amb línies
    grogues; la casa només s'hi nota en el rètol blau marí i or «MOLL DE CÀRREGA» i en el logo de les furgonetes;
  - a l'esquerra, la persiana del moll enrotllada: fora, el matí de Ginebra (cel clar, un edifici veí i el llac
    al fons), i dues furgonetes blindades recolzades al moll, de cul, amb el logo del BCMU;
  - al fons, tres tècnics de manteniment de la Rius amb granota, mirant el mòbil (subcontractats d'una
    subcontracta);
  - un toro aparcat amb un palet de caixes a les forques i el llum taronja giratori (l'animació);
  - el rellotge de fitxar amb el casiller de targetes;
  - la màquina de cafè vella, amb el cop de puny marcat al costat;
  - l'ascensor de servei d'acer, amb el lector de targetes i l'adhesiu «NOMÉS PERSONAL AUTORITZAT».
"""
import math

from PIL import Image
from pixels import nearest

from hd.pix import Light, Canvas, W, H, hr
from hd.rooms.comu import obox, outline, text, text_width, _diff, PLASTIC, SHEET, CARD, RED, YEL, GRAYC
from hd.rooms.pis_cuina import outline_poly
from hd.rooms.bcmu import CONCB, NAVYB, BRASS, LINOB, logo
from hd.characters import person, M, BOOT, GRAY_SHOE, SKIN_PALE, SKIN_VET, SKIN_RUDDY, HAIR_BROWN, HAIR_COPPER
from hd.personatges import hair_cap

FLOOR_Y = 150

BLOCKW = [(16, 18, 22), (28, 30, 36), (42, 46, 52), (58, 62, 68), (76, 80, 86), (96, 100, 104), (118, 122, 124), (142, 146, 146), (168, 170, 168)]
FLOORC = [(12, 12, 14), (22, 22, 24), (34, 34, 36), (48, 48, 50), (64, 62, 62), (82, 80, 78), (102, 100, 96), (124, 120, 114)]
STEEL = [(14, 16, 20), (26, 30, 36), (42, 48, 56), (60, 68, 78), (84, 92, 102), (110, 118, 128), (142, 150, 158), (180, 186, 192), (220, 224, 228)]
SKYD = [(110, 140, 170), (136, 166, 192), (160, 188, 210), (186, 208, 224), (210, 226, 236), (232, 240, 244)]
LAKE = [(40, 70, 96), (60, 96, 124), (84, 124, 150), (120, 156, 176)]
HILL = [(60, 80, 96), (80, 100, 114), (100, 120, 132)]
STONE = [(80, 78, 76), (110, 106, 100), (140, 134, 126), (170, 164, 154), (200, 194, 182)]
YELH = [(40, 30, 0), (100, 74, 4), (170, 128, 10), (220, 176, 30), (246, 214, 80)]
FORK = [(50, 26, 6), (100, 50, 10), (160, 86, 16), (210, 124, 26), (240, 166, 56), (252, 206, 120)]
COFFEE = [(24, 12, 10), (44, 22, 16), (68, 36, 24), (96, 54, 34), (126, 76, 46), (156, 100, 62), (186, 130, 86)]
PALLET = [(30, 18, 8), (56, 36, 16), (86, 58, 28), (116, 82, 42), (146, 108, 60), (176, 138, 84)]
BOXC = [(40, 26, 14), (70, 48, 26), (104, 74, 42), (138, 102, 60), (170, 132, 82), (198, 162, 108)]
TYRE = [(8, 8, 10), (18, 18, 22), (30, 30, 36), (44, 44, 50)]
OVERALL = M((14, 20, 30), (24, 34, 48), (38, 52, 70), (56, 74, 94), (80, 100, 120), (110, 130, 146), dith=0.0)
CAPM = M((40, 10, 6), (90, 26, 10), (150, 50, 14), (204, 84, 24), (236, 130, 50), dith=0.0)

LIGHT = Light(ambient=-0.25, vignette=(50, 30), floor_fade=(192, 28))
LIGHT.point(250, 4, r=200, k=2.2, squash=0.8, power=1.3)             # fluorescent del mig
LIGHT.point(420, 4, r=170, k=1.8, squash=0.8, power=1.4)             # fluorescent de l'ascensor
LIGHT.point(95, 110, r=170, k=1.6, squash=1.0, power=1.5)            # el dia, per la persiana

OPEN = (12, 26, 178, FLOOR_Y)          # el forat de la persiana
BEACON = (274, 92)                     # el llum giratori del toro


# ─── Paret, sostre, terra ──────────────────────────────────────────────────

def wall(cv):
    """Bloc de formigó pintat de gris clar; a baix, sòcol fosc i franja de seguretat groga i negra."""
    for y in range(0, FLOOR_Y):
        row = y // 9
        for x in range(W):
            off = 12 if row % 2 else 0
            joint = (y % 9 == 8) or ((x + off) % 24 == 23)
            n = (hr(x // 2, y // 2, 11) - 0.5) * 0.3 + (hr((x + off) // 24, row, 3) - 0.5) * 0.25
            cv.put(x, y, BLOCKW, (3.0 if joint else 4.3 + n) - (0.6 if y > 128 else 0))
    # franja de perill a la base de la paret
    for y in range(132, 140):
        for x in range(W):
            stripe = ((x + y) // 6) % 2 == 0
            cv.put(x, y, YELH if stripe else TYRE, 3.0 if stripe else 2.0)
    cv.rect(0, 140, W - 1, FLOOR_Y - 1, CONCB, 2.0)
    cv.hline(0, W - 1, FLOOR_Y, CONCB, 0.6)


def ceiling(cv):
    """Bigues d'acer i canonades a la vista, amb dos fluorescents."""
    cv.rect(0, 0, W - 1, 8, CONCB, 2.6)
    for x in range(0, W, 80):
        cv.rect(x, 0, x + 5, 14, STEEL, lambda xx, yy: 3.0 + (1.0 if xx == x + 1 else 0) - (1.0 if xx >= x + 4 else 0))
    cv.rect(0, 9, W - 1, 11, STEEL, lambda x, y: 3.2 + (1.0 if y == 9 else 0))
    cv.rect(0, 16, W - 1, 18, NAVYB, lambda x, y: 3.0 + (1.2 if y == 16 else 0))     # canonada pintada de la casa
    for fx in (210, 380):
        tube(cv, fx)


def tube(cv, x0, on=True):
    obox(cv, x0 - 2, 20, x0 + 62, 24, STEEL, 3.4)
    col = (236, 246, 255) if on else (120, 128, 136)
    cv.hline(x0, x0 + 60, 23, [col], 0, lit=0)
    if on:
        cv.glow(x0 + 30, 25, 30, (220, 236, 255), 0.22)


def floor(cv):
    """Formigó amb taques d'oli, junts de dilatació i línies grogues de pas."""
    for y in range(FLOOR_Y + 1, H):
        for x in range(W):
            n = (hr(x // 3, y // 2, 7) - 0.5) * 0.45
            joint = (x - (y - FLOOR_Y) * 0.0) % 96 == 0
            cv.put(x, y, FLOORC, (2.2 if joint else 3.6 + n))
    for i in range(8):                                                   # taques d'oli
        cx = 40 + int(hr(i, 1) * 400)
        cy = 160 + int(hr(i, 2) * 36)
        cv.darken(cx - 8, cy - 2, cx + 8, cy + 2, lambda x, y, cx=cx, cy=cy: 0.5 * max(0, 1 - math.hypot((x - cx) / 8, (y - cy) / 2.4)))
    # la vora del moll (davant la persiana): franja groga i negra
    for y in range(FLOOR_Y + 1, FLOOR_Y + 5):
        for x in range(OPEN[0], OPEN[2] + 1):
            stripe = ((x - y) // 5) % 2 == 0
            cv.put(x, y, YELH if stripe else TYRE, 3.4 if stripe else 2.0)
    # línies grogues del passadís de vianants
    for y in (174, 204):
        cv.rect(0, y, W - 1, y + 1, YELH, 3.2)
    for x in range(200, W, 22):                                          # zebra davant l'ascensor
        cv.poly([(x, 158), (x + 8, 158), (x + 4, 170), (x - 4, 170)], YELH, 2.6)


# ─── La persiana oberta i les furgonetes ───────────────────────────────────

def outside(cv):
    """Fora: el matí de Ginebra (cel, un edifici de pedra, el llac i les muntanyes)."""
    x0, y0, x1, y1 = OPEN
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, SKYD, 5.2 - (y - y0) / 26, lit=0)
    for x in range(x0, x1 + 1):                                          # muntanyes
        h = 74 + int(math.sin(x * 0.05) * 5 + math.sin(x * 0.13) * 3)
        for y in range(h, 92):
            cv.put(x, y, HILL, 2.0 - (y - h) / 30, lit=0)
    cv.rect(x0, 92, x1, 102, LAKE, lambda x, y: 2.6 + (0.8 if (x + y * 3) % 17 == 0 else 0), lit=0)
    # l'edifici veí, de pedra, amb finestres
    obox(cv, 110, 44, x1, 104, STONE, 3.0, lit=0)
    for r in range(4):
        for c in range(5):
            wx, wy = 116 + c * 12, 50 + r * 13
            cv.rect(wx, wy, wx + 6, wy + 8, LAKE, 1.4, lit=0)
            cv.hline(wx, wx + 6, wy + 8, STONE, 4.4, lit=0)
    # el pati de fora (asfalt)
    for y in range(104, y1 + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, FLOORC, 3.2 + (hr(x // 2, y, 4) - 0.5) * 0.4, lit=0)


def shutter(cv):
    """El marc de la persiana i la persiana enrotllada a dalt."""
    x0, y0, x1, y1 = OPEN
    cv.rect(x0 - 6, y0 - 12, x1 + 6, y0 - 1, STEEL, lambda x, y: 3.2 + ((y - y0) % 3 == 0) * 0.8)   # el rotlle
    outline(cv, x0 - 6, y0 - 12, x1 + 6, y0 - 1, STEEL)
    for y in range(y0, y0 + 5):                                          # les últimes lamel·les penjant
        cv.hline(x0, x1, y, STEEL, 3.8 if y % 2 else 2.4)
    for sx in (x0 - 6, x1 + 1):                                          # les guies
        cv.rect(sx, y0 - 1, sx + 5, y1, STEEL, lambda x, y, sx=sx: 3.0 + (1.0 if x == sx + 1 else 0) - (0.8 if x == sx + 5 else 0))
    # bandes de perill a les guies
    for sx in (x0 - 6, x1 + 1):
        for y in range(y1 - 30, y1):
            if (y // 4) % 2 == 0:
                cv.rect(sx + 1, y, sx + 4, y, YELH, 3.2)


def van(cv, x0, y0, x1, y1):
    """Una furgoneta blindada vista de darrere: caixa blau marí, franja d'or, logo, portes i finestretes."""
    w = x1 - x0
    # el sostre i la caixa
    obox(cv, x0, y0, x1, y1 - 14, NAVYB, 3.4, top=1.2, side=-1.0)
    cv.rect(x0 + 1, y0 + 1, x1 - 1, y0 + 3, NAVYB, 4.8)
    # les dues portes del darrere
    mid = (x0 + x1) // 2
    cv.vline(mid, y0 + 6, y1 - 15, NAVYB, 0.6)
    for dx0, dx1 in ((x0 + 3, mid - 2), (mid + 2, x1 - 3)):
        outline(cv, dx0, y0 + 6, dx1, y1 - 18, NAVYB)
        obox(cv, dx0 + 3, y0 + 9, dx1 - 3, y0 + 18, [(10, 14, 22), (30, 40, 56), (70, 90, 110), (130, 150, 168)], 1.6)  # finestreta blindada
        cv.line(dx0 + 4, y0 + 10, dx0 + 8, y0 + 10, [(200, 220, 230)], 0)
    # la franja d'or i el logo
    cv.rect(x0 + 2, y0 + 24, x1 - 2, y0 + 26, BRASS, 4.0)
    cv.disc(mid, y0 + 35, 9, 9, NAVYB, 2.0)
    logo(cv, mid, y0 + 35, k=1.5, lvl=4.4)
    # maneta i pany
    cv.rect(mid - 5, y0 + 47, mid - 2, y0 + 48, STEEL, 5.0)
    cv.rect(mid + 2, y0 + 47, mid + 5, y0 + 48, STEEL, 5.0)
    # pilots
    for px in (x0 + 1, x1 - 4):
        cv.rect(px, y1 - 26, px + 3, y1 - 18, RED, 4.0)
        cv.glow(px + 1, y1 - 22, 5, (255, 60, 50), 0.3)
    # para-xocs, matrícula i rodes
    cv.rect(x0 - 1, y1 - 14, x1 + 1, y1 - 9, STEEL, lambda x, y: 2.6 + (1.0 if y == y1 - 14 else 0))
    obox(cv, mid - 9, y1 - 13, mid + 9, y1 - 9, SHEET, 4.8)
    text(cv, 'GE', mid - 7, y1 - 12, [(30, 30, 40)], 0, flat=(30, 30, 40))
    cv.rect(mid - 1, y1 - 12, mid + 7, y1 - 11, [(60, 60, 70)], 0)
    for wx in (x0 + 2, x1 - 11):
        cv.rect(wx, y1 - 9, wx + 9, y1, TYRE, lambda x, y: 1.6 + (0.8 if y == y1 - 9 else 0))
    cv.darken(x0 - 2, y1, x1 + 2, y1 + 3, 0.6)
    cv.darken(x0 + 3, y1 - 8, x1 - 3, y1, 0.4)


# ─── Els tècnics de la Rius ────────────────────────────────────────────────

def _tecnic(skin, hair, cap=True):
    hk = hair_cap(hair)
    if cap:
        def hook(fg, p, spec):
            hk(fg, p, spec)
            hx, hy = p.head
            fg.ell(hx + (1.0 if p.f == 'L' else 0), hy - 5.6, 7.4, 3.2, CAPM, 2.6, amp=1.6, cont=(0.2, 1.0))
            if p.f == 'L':
                fg.ell(hx - 5.0, hy - 3.4, 4.0, 1.2, CAPM, 1.8, amp=1.0)
        return {'skin': skin, 'legs': OVERALL, 'top': OVERALL, 'shoes': BOOT, 'hooks': {'hair': hook}}
    return {'skin': skin, 'legs': OVERALL, 'top': OVERALL, 'shoes': BOOT, 'hooks': {'hair': hk}}


TECNICS = [
    # (spec, direcció, peus x, mirall)
    (_tecnic(SKIN_RUDDY, HAIR_BROWN), 'U', 190, False),
    (_tecnic(SKIN_PALE, HAIR_COPPER, cap=False), 'L', 205, True),
    (_tecnic(SKIN_VET, HAIR_BROWN), 'L', 221, False),
]
TK = 0.66      # al fons: més petits
FEET_Y = 150


def tecnics(cv):
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for spec, f, fx, mirror in TECNICS:
        fig = person(spec, f)
        if mirror:
            fig = fig.transpose(Image.FLIP_LEFT_RIGHT)
        fig = nearest(fig, (round(fig.width * TK), round(fig.height * TK)))
        layer.alpha_composite(fig, (fx - round(25 * TK), FEET_Y - round(83 * TK)))
    # una mica més foscos: són al fons, lluny del fluorescent
    px = layer.load()
    for y in range(H):
        for x in range(W):
            r, g, b, a = px[x, y]
            if a:
                px[x, y] = (int(r * 0.82), int(g * 0.84), int(b * 0.9), a)
    for spec, f, fx, mirror in TECNICS:
        cv.darken(fx - 7, FEET_Y - 1, fx + 7, FEET_Y + 1, 0.5)
    cv.img.alpha_composite(layer)
    # els mòbils: tres rectangles de llum blavosa a les mans
    for mx, my in ((211, 124), (216, 124)):
        cv.rect(mx, my, mx + 1, my + 2, [(170, 220, 255)], 0, lit=0)
        cv.glow(mx, my + 1, 5, (150, 210, 255), 0.35)
    # una caixa d'eines vermella a terra, darrere d'ells
    obox(cv, 176, 143, 186, 150, RED, 3.0)
    cv.rect(179, 140, 183, 140, STEEL, 3.4)


# ─── El toro, el palet i el rellotge de fitxar ─────────────────────────────

def forklift(cv, beacon_on=0):
    """Un toro taronja aparcat de perfil (mirant a l'esquerra), amb un palet de caixes a les forques."""
    # el pal de les forques
    cv.rect(250, 86, 253, 148, STEEL, lambda x, y: 2.8 + (1.0 if x == 251 else 0))
    cv.rect(256, 86, 259, 148, STEEL, lambda x, y: 2.6 + (1.0 if x == 257 else 0))
    # les forques i el palet
    cv.rect(236, 146, 254, 148, STEEL, 3.4)
    obox(cv, 232, 140, 252, 145, PALLET, 3.2)
    for i, (bx0, by0, bx1, by1) in enumerate(((233, 122, 243, 139), (244, 124, 252, 139), (236, 108, 249, 121))):
        obox(cv, bx0, by0, bx1, by1, BOXC, 3.4 - i * 0.2)
        cv.hline(bx0 + 1, bx1 - 1, (by0 + by1) // 2, [(200, 180, 120), (230, 214, 160)], 0.6)   # cinta
    text(cv, 'BCMU', 237, 112, [(40, 30, 70)], 0, flat=(40, 30, 70))
    # el cos
    body = [(258, 108), (288, 108), (296, 120), (296, 142), (258, 142)]
    cv.poly(body, FORK, lambda x, y: 3.4 + (1.0 if y < 112 else 0) - (x - 258) * 0.02)
    outline_poly(cv, body, FORK)
    # la cabina (estructura de protecció i seient)
    for cx in (262, 292):
        cv.rect(cx, 84, cx + 2, 108, PLASTIC, 2.6)
    cv.rect(262, 82, 294, 85, PLASTIC, 2.8)
    obox(cv, 276, 96, 288, 108, PLASTIC, 2.0)                           # el seient
    cv.line(268, 104, 266, 92, PLASTIC, 2.6)                            # el volant
    cv.rect(262, 91, 270, 92, PLASTIC, 3.0)
    # el contrapès i les rodes
    obox(cv, 288, 118, 297, 142, FORK, 2.6)
    for wx, r in ((268, 7), (289, 6)):
        cv.disc(wx, 144, r, r, TYRE, lambda nx, ny: 2.2 - ny * 0.6)
        cv.disc(wx, 144, 2.4, 2.4, STEEL, 4.0)
    cv.darken(258, 150, 298, 153, 0.55)
    text(cv, 'NO TOCAR', 264, 124, [(40, 20, 6)], 0, flat=(40, 20, 6))
    # el llum giratori
    lx, ly = BEACON
    obox(cv, lx - 3, ly - 1, lx + 3, ly + 2, PLASTIC, 2.4)
    beacon(cv, beacon_on)


def beacon(cv, phase):
    """El llum taronja: la cúpula i, segons la fase, la llum que gira (cap a l'esquerra, de cara, a la dreta, d'esquena)."""
    lx, ly = BEACON
    on = phase in (0, 1, 2)
    cv.disc(lx, ly - 4, 3.2, 3.4, FORK, (5.0 if on else 3.4), lit=0)
    cv.flat(lx - 1, ly - 6, (255, 240, 200) if on else (240, 170, 80))
    if on:
        dx = (-1, 0, 1)[phase]
        cv.glow(lx + dx * 10, ly - 4, 16 if phase == 1 else 12, (255, 150, 40), 0.45 if phase == 1 else 0.3)


def time_clock(cv):
    """El rellotge de fitxar, amb el casiller de targetes al costat."""
    x0, y0 = 316, 34
    obox(cv, x0, y0, x0 + 18, y0 + 26, [(30, 26, 22), (70, 60, 48), (120, 106, 84), (170, 156, 128), (210, 198, 170)], 3.2)
    cv.disc(x0 + 9, y0 + 9, 6, 6, SHEET, 4.8)
    cv.ring(x0 + 9, y0 + 9, 6, SHEET, 1.6, step=12)
    cv.line(x0 + 9, y0 + 9, x0 + 9, y0 + 5, [(20, 20, 30)], 0)
    cv.line(x0 + 9, y0 + 9, x0 + 12, y0 + 10, [(20, 20, 30)], 0)
    cv.rect(x0 + 4, y0 + 19, x0 + 14, y0 + 21, PLASTIC, 1.0)          # la ranura
    # el casiller
    obox(cv, x0 + 22, y0 - 2, x0 + 44, y0 + 30, [(40, 44, 50), (70, 76, 84), (110, 116, 124), (150, 156, 162)], 2.6)
    for r in range(5):
        for c in range(3):
            cx, cy = x0 + 24 + c * 7, y0 + r * 6
            cv.rect(cx, cy, cx + 5, cy + 4, PLASTIC, 1.2)
            if hr(r, c, 9) > 0.35:
                cv.rect(cx + 1, cy - 2, cx + 4, cy + 3, SHEET, 4.4)
                cv.hline(cx + 1, cx + 4, cy - 1, RED if hr(r, c) > 0.5 else [(60, 90, 160)], 0)
    text(cv, 'FITXAR', x0 + 22, y0 + 35, [(30, 30, 36)], 0, flat=(36, 36, 42))


# ─── La màquina de cafè ────────────────────────────────────────────────────

def coffee_machine(cv):
    """Una expenedora de cafè dels noranta: marró i crema, una tassa pintada i el cop de puny al costat."""
    x0, y0, x1, y1 = 300, 70, 334, 150
    obox(cv, x0, y0, x1, y1, COFFEE, 3.2, side=-1.2)
    # el frontal: el rètol il·luminat
    obox(cv, x0 + 3, y0 + 3, x1 - 3, y0 + 26, [(60, 30, 10), (130, 70, 26), (200, 130, 60), (240, 190, 120), (255, 236, 190)], 2.8, lit=0)
    cv.disc(x0 + 15, y0 + 11, 5, 3.5, [(80, 40, 20), (140, 80, 40), (200, 150, 100), (250, 230, 200)], lambda nx, ny: 2.6 - ny, lit=0)
    cv.rect(x0 + 20, y0 + 9, x0 + 22, y0 + 12, [(80, 40, 20), (200, 150, 100)], 1.0, lit=0)   # la nansa
    for i in range(3):                                                   # el vapor
        cv.line(x0 + 12 + i * 3, y0 + 6, x0 + 13 + i * 3, y0 + 4, [(255, 250, 240)], 0, lit=0)
    text(cv, 'CAFÈ', x0 + 9, y0 + 19, [(60, 20, 6)], 0, lit=0, flat=(70, 26, 8))
    cv.glow(x0 + 16, y0 + 15, 20, (255, 200, 120), 0.2)
    # els botons
    for r in range(4):
        obox(cv, x0 + 4, y0 + 30 + r * 7, x0 + 18, y0 + 35 + r * 7, SHEET, 4.0)
        cv.rect(x0 + 6, y0 + 32 + r * 7, x0 + 13, y0 + 32 + r * 7, PLASTIC, 1.4)
    # el moneder i la pantalleta
    obox(cv, x0 + 22, y0 + 30, x1 - 4, y0 + 40, STEEL, 3.6)
    cv.rect(x0 + 25, y0 + 32, x1 - 7, y0 + 35, [(10, 30, 10), (60, 200, 80)], 0.6, lit=0)
    cv.rect(x0 + 26, y0 + 37, x1 - 8, y0 + 38, PLASTIC, 0.6)              # la ranura de les monedes
    obox(cv, x0 + 22, y0 + 44, x1 - 4, y0 + 50, STEEL, 3.0)               # el retorn de monedes
    # el forat de la tassa
    obox(cv, x0 + 7, y0 + 60, x1 - 7, y0 + 74, PLASTIC, 0.8)
    cv.rect(x0 + 14, y0 + 68, x0 + 20, y0 + 73, SHEET, 4.6)               # un got de plàstic oblidat
    # el cop de puny: una abonyegada al costat dret
    cx, cy = x1 - 1, y0 + 48
    for yy in range(cy - 6, cy + 7):
        for xx in range(x1 - 4, x1 + 1):
            d = math.hypot((xx - cx) / 3.5, (yy - cy) / 6)
            if d < 1:
                cv.put(xx, yy, COFFEE, 1.2 + d * 1.6)
    for k in range(4):                                                   # les marques dels nusos
        cv.flat(x1 - 2, cy - 3 + k * 2, COFFEE[1])
    cv.darken(x1 + 1, y0 + 2, x1 + 4, y1, 0.45)
    cv.darken(x0 - 1, y1 + 1, x1 + 3, y1 + 3, 0.5)


# ─── L'ascensor de servei ──────────────────────────────────────────────────

def elevator(cv):
    """L'ascensor de servei: marc d'acer, portes rascades, l'indicador de plantes, el lector i l'adhesiu."""
    x0, y0, x1, y1 = 400, 40, 460, FLOOR_Y
    obox(cv, x0, y0, x1, y1, STEEL, 3.0, top=0.8)
    # l'indicador de planta
    obox(cv, 410, y0 + 3, 450, y0 + 11, PLASTIC, 0.8)
    for i, ch in enumerate('S0123'):
        col = (255, 120, 40) if ch == 'S' else (90, 70, 50)
        text(cv, ch, 413 + i * 7, y0 + 5, [col], 0, lit=0, flat=col)
    cv.glow(414, y0 + 7, 6, (255, 120, 40), 0.4)
    # les portes
    for dx0, dx1 in ((404, 429), (431, 452)):
        cv.rect(dx0, y0 + 14, dx1, y1, STEEL, lambda x, y, d=dx0: 4.4 + (hr(x, y // 3, 4) - 0.5) * 0.4 + (0.8 if x == d else 0))
        outline(cv, dx0, y0 + 14, dx1, y1, STEEL)
    for i in range(7):                                                   # rascades de carros
        sy = 116 + int(hr(i, 5) * 26)
        sx = 406 + int(hr(i, 6) * 40)
        cv.hline(sx, sx + 6 + int(hr(i, 7) * 6), sy, STEEL, 2.6)
    cv.vline(430, y0 + 14, y1, STEEL, 1.0)
    # l'adhesiu groc
    obox(cv, 407, 72, 450, 92, YELH, 3.6)
    for k, word in enumerate(('NOMÉS', 'PERSONAL', 'AUTORITZAT')):
        text(cv, word, 429 - text_width(word) // 2, 75 + k * 6 - (1 if k == 0 else 0), [(30, 20, 0)], 0, flat=(30, 20, 0))
    # el lector de targetes, al muntant dret
    obox(cv, 453, 88, 459, 108, PLASTIC, 1.6)
    cv.rect(455, 91, 457, 96, [(10, 10, 14), (40, 40, 50)], 0.6)
    cv.disc(456, 102, 1.4, 1.4, [(230, 40, 36)], 0, lit=0)
    cv.glow(456, 102, 5, (255, 50, 40), 0.4)
    # el botó de crida
    obox(cv, 462, 96, 468, 108, STEEL, 3.4)
    cv.disc(465, 102, 1.6, 1.6, [(200, 200, 210)], 0)
    cv.darken(x1 + 1, y0, x1 + 3, y1, 0.4)


def house_sign(cv):
    """El rètol de la casa: blau marí i or, «MOLL DE CÀRREGA», amb el logo."""
    x0, y0, x1 = 196, 40, 300
    obox(cv, x0, y0, x1, y0 + 14, NAVYB, 3.0)
    cv.rect(x0 + 1, y0 + 1, x1 - 1, y0 + 1, BRASS, 4.4)
    cv.rect(x0 + 1, y0 + 13, x1 - 1, y0 + 13, BRASS, 3.6)
    logo(cv, x0 + 9, y0 + 7, k=0.9, lvl=4.4)
    s = 'MOLL DE CÀRREGA'
    text(cv, s, x0 + 18 + (x1 - x0 - 18 - text_width(s)) // 2, y0 + 5, BRASS, 5.0)
    # l'avís de sota
    s2 = 'ARMILLA OBLIGATÒRIA'
    text(cv, s2, (x0 + x1) // 2 - text_width(s2) // 2, y0 + 21, [(30, 30, 36)], 0, flat=(44, 44, 50))


def crates_right(cv):
    """Caixes apilades entre la màquina i l'ascensor, contra la paret (al fons, sense tapar la Rius)."""
    obox(cv, 372, 114, 396, 132, BOXC, 3.2)
    obox(cv, 376, 98, 394, 113, BOXC, 3.6)
    cv.hline(373, 395, 123, [(200, 180, 120), (230, 214, 160)], 0.6)
    text(cv, 'FRÀGIL', 377, 104, [(120, 20, 20)], 0, flat=(140, 30, 26))
    obox(cv, 368, 132, 398, 136, PALLET, 3.0)


def bg(cv, beacon_phase=0, tube_on=True):
    wall(cv)
    ceiling(cv)
    if not tube_on:
        tube(cv, 210, on=False)
        cv.darken(200, 18, 280, 30, 0.2)
    floor(cv)
    outside(cv)
    van(cv, 106, 76, 170, 150)
    van(cv, 22, 68, 96, 156)
    shutter(cv)
    house_sign(cv)
    tecnics(cv)
    time_clock(cv)
    forklift(cv, beacon_phase)
    coffee_machine(cv)
    crates_right(cv)
    elevator(cv)


PROPS = {}


# ─── El llum giratori del toro ─────────────────────────────────────────────

def _frames():
    base = Canvas(light=LIGHT)
    bg(base)
    frames = []
    for i in range(8):
        cv = Canvas(light=LIGHT)
        bg(cv, beacon_phase=i % 4, tube_on=(i != 5))
        frames.append(_diff(cv.img, base.img))
    return frames


ANIMS = {'llum_toro': {'frames': _frames, 'frameDuration': 180}}
