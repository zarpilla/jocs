"""
El passadís del tercer pis del BCMU (Escena 5, l'Iri). Art definitiu:
  - un passadís d'oficines sobri: paret de pintura gris perla, arrimador de caoba, sòcol fosc i catifa
    corporativa blau marí amb un rombe d'or; tres fluorescents al sostre;
  - a l'esquerra, la porta vella de l'escala (fusta de 1958, pany antic de clau grossa, rètol ESCALA);
  - la càmera 1 al sostre, mirant la porta de neteja, amb l'adhesiu «ZONA NETEJA · NO ES GRAVA»;
  - la porta de servei de neteja (xapa grisa, rètol NETEJA), un quadre motivacional («EFICIÈNCIA»),
    el ganxo buit de l'extintor, l'estació del tub;
  - la porta VIP de caoba i llautó amb la catifa vermella i el rètol «NOMÉS CLIENTS PREMIUM»;
  - l'ascensor de servei (xapa, botó i el «3»), i la càmera 2 al racó de dalt a la dreta.

Props: 'cartell', 'galleda', 'extintor' (es poden agafar: al fons només hi ha el lloc buit),
'camera1_tapada' (el cartell de neteja penjat davant la càmera 1), 'camera2_tapada' (la galleda de barret).
Animació: les dues càmeres escombren el passadís i el LED vermell parpelleja.
"""
from hd.pix import Light, Canvas, W, H, hr
from hd.rooms.comu import obox, outline, text, text_width, _diff, SHEET, YEL
from hd.rooms.pis_cuina import outline_poly
from hd.rooms.aeroport_terminal import CHROME, YELS, BLUE
from hd.rooms.aeroport_personal import REDB
from hd.rooms.bcmu import MAHOG, BRASS, NAVYB, CARPET, CONCB, MARBLE, tub_station, logo, sign

FLOOR_Y = 150

PAINT = [(20, 20, 24), (36, 36, 42), (54, 54, 60), (74, 74, 80), (96, 96, 100), (120, 118, 120), (146, 144, 142), (172, 170, 164), (198, 196, 188)]
DOORG = [(14, 18, 22), (26, 32, 38), (42, 50, 58), (60, 70, 78), (82, 92, 100), (108, 118, 124), (138, 146, 150)]
OLDWOOD = [(14, 8, 6), (28, 16, 10), (46, 28, 16), (66, 42, 24), (88, 58, 34), (112, 76, 44), (140, 98, 58)]
CAMB = [(10, 10, 14), (24, 24, 30), (42, 42, 50), (66, 66, 74), (96, 96, 102), (136, 134, 136), (180, 178, 176)]

LIGHT = Light(ambient=-0.25, vignette=(60, 30), floor_fade=(190, 30))
for _x in (90, 250, 410):
    LIGHT.point(_x, 4, r=150, k=1.6, squash=0.8, power=1.4)              # els fluorescents
LIGHT.point(358, 60, r=60, k=0.5, squash=1.0, power=2.0)                 # el llum càlid de sobre la porta VIP

CAM1 = (121, 14)    # on penja la càmera 1 (el suport)
CAM2 = (457, 14)
CAM_ANGLES = [0, -1, -2, -2, -1, 0, 1, 2, 2, 1]


# ─── Paret, sostre, terra ──────────────────────────────────────────────────

def wall(cv):
    """Pintura gris perla a dalt, arrimador de caoba a baix, i el sostre de plaques."""
    for y in range(16, 108):
        for x in range(W):
            n = (hr(x // 3, y // 3, 7) - 0.5) * 0.25
            cv.put(x, y, PAINT, 5.0 + n)
    # pilastres suaus cada tram
    for px in (78, 206, 288, 318, 396):
        cv.rect(px, 16, px + 3, 107, PAINT, lambda x, y: 5.6 if x == px else (4.4 if x == px + 3 else 5.2))
    # arrimador
    cv.rect(0, 104, W - 1, 107, MAHOG, lambda x, y: 4.6 if y == 104 else 3.4)
    for y in range(108, FLOOR_Y - 4):
        for x in range(W):
            panel = (x % 40) in (0, 1) or y in (110, FLOOR_Y - 7)
            n = (hr(x, y // 2, 3) - 0.5) * 0.3
            cv.put(x, y, MAHOG, (2.0 if panel else 3.0) + n)
    cv.rect(0, FLOOR_Y - 4, W - 1, FLOOR_Y - 1, MAHOG, 1.4)              # sòcol
    cv.hline(0, W - 1, FLOOR_Y, MAHOG, 0)
    # sostre
    for y in range(0, 16):
        for x in range(W):
            seam = (x % 48 == 0) or y == 15
            cv.put(x, y, MARBLE, (2.2 if seam else 3.2) + (hr(x // 4, y // 4, 9) - 0.5) * 0.2)
    cv.hline(0, W - 1, 16, PAINT, 2.0)
    for fx in (90, 250, 410):
        tube(cv, fx)


def tube(cv, cx):
    obox(cv, cx - 26, 2, cx + 26, 7, CHROME, 3.4)
    cv.hline(cx - 23, cx + 23, 4, [(236, 246, 255)], 0, lit=0)
    cv.hline(cx - 23, cx + 23, 5, [(200, 220, 236)], 0, lit=0)
    cv.glow(cx, 7, 26, (230, 240, 255), 0.22)


def floor(cv):
    """Catifa blau marí amb el rombe d'or del banc, gastada pel mig."""
    for y in range(FLOOR_Y + 1, H):
        for x in range(W):
            n = (hr(x // 2, y // 2, 4) - 0.5) * 0.35
            # rombes en quadrícula, més estrets com més lluny
            gy = (y - FLOOR_Y)
            cell = 24
            u, v = (x + gy * 0.0) % cell, gy % 14
            d = abs(u - cell / 2) / (cell / 2) + abs(v - 7) / 7
            worn = max(0, 1 - abs(y - 186) / 18) * 0.5
            lvl = 3.2 + n + worn
            if 0.92 < d < 1.08:
                cv.put(x, y, BRASS, 2.0 + n)
            else:
                cv.put(x, y, NAVYB, lvl)
    cv.darken(0, FLOOR_Y + 1, W - 1, FLOOR_Y + 4, 0.5)


# ─── Portes ────────────────────────────────────────────────────────────────

def porta_escala(cv):
    """La porta vella de l'escala: fusta de 1958, plafons, i un pany de llautó per a una clau grossa."""
    x0, y0, x1, y1 = 14, 50, 60, FLOOR_Y
    obox(cv, x0 - 4, y0 - 4, x1 + 4, y1, MAHOG, 2.6)
    obox(cv, x0, y0, x1, y1, OLDWOOD, 3.0, top=0.4)
    for (a, b) in ((y0 + 6, y0 + 44), (y0 + 52, y1 - 8)):
        cv.rect(x0 + 5, a, x1 - 5, b, OLDWOOD, 2.6)
        cv.hline(x0 + 5, x1 - 5, a, OLDWOOD, 1.4)
        cv.vline(x0 + 5, a, b, OLDWOOD, 1.4)
        cv.hline(x0 + 5, x1 - 5, b, OLDWOOD, 4.2)
        cv.vline(x1 - 5, a, b, OLDWOOD, 4.0)
    # el pany: placa i el forat de la clau grossa
    obox(cv, x1 - 13, 94, x1 - 5, 112, BRASS, 3.4)
    cv.disc(x1 - 9, 100, 1.6, 1.6, [(8, 6, 4)], 0)
    cv.rect(x1 - 10, 101, x1 - 8, 105, [(8, 6, 4)], 0)
    cv.disc(x1 - 9, 109, 1.5, 1.5, BRASS, 5.0)                          # el pom
    # rètol
    sign(cv, 22, 34, 'ESCALA', NAVYB, 3.0, ink=(236, 210, 140))
    cv.darken(x1 + 5, y0, x1 + 8, y1, 0.35)


def porta_neteja(cv):
    """La porta de servei de la neteja: xapa grisa, una reixeta i la barra antipànic."""
    x0, y0, x1, y1 = 150, 56, 200, FLOOR_Y
    obox(cv, x0 - 3, y0 - 3, x1 + 3, y1, CHROME, 2.6)
    obox(cv, x0, y0, x1, y1, DOORG, 3.4, top=0.6)
    for k in range(5):                                                  # reixeta de ventilació
        cv.hline(x0 + 12, x1 - 12, y1 - 22 + k * 3, DOORG, 1.6)
        cv.hline(x0 + 12, x1 - 12, y1 - 21 + k * 3, DOORG, 4.6)
    cv.rect(x0 + 4, 104, x1 - 4, 107, CHROME, lambda x, y: 4.2 if y == 104 else 3.0)
    obox(cv, x1 - 9, 98, x1 - 4, 110, CHROME, 3.2)
    # rètol
    w = text_width('NETEJA')
    obox(cv, 175 - w // 2 - 4, 42, 175 + w // 2 + 4, 52, [(200, 210, 214), (230, 234, 236), (250, 252, 252)], 1.4)
    text(cv, 'NETEJA', 175 - w // 2, 45, [(30, 40, 50)], 0, flat=(30, 40, 50))
    # el rastre del robot: unes rodes que surten per sota
    cv.tint(x0 + 6, y1 + 1, x1 - 6, y1 + 30, (150, 170, 200), lambda x, y: 0.06 if (x - x0) % 12 in (0, 1) else 0)


def porta_vip(cv):
    """La porta VIP: dues fulles de caoba amb motllures de llautó, manetes daurades i la catifa vermella."""
    x0, y0, x1, y1 = 326, 46, 390, FLOOR_Y
    obox(cv, x0 - 5, y0 - 5, x1 + 5, y1, MARBLE, 4.2)                   # marc de marbre
    mid = (x0 + x1) // 2
    for a, b in ((x0, mid), (mid + 1, x1)):
        obox(cv, a, y0, b, y1, MAHOG, 3.6, top=0.6)
        obox(cv, a + 4, y0 + 6, b - 4, y0 + 48, BRASS, 2.2)
        cv.rect(a + 5, y0 + 7, b - 5, y0 + 47, MAHOG, 3.2)
        obox(cv, a + 4, y0 + 54, b - 4, y1 - 8, BRASS, 2.2)
        cv.rect(a + 5, y0 + 55, b - 5, y1 - 9, MAHOG, 3.2)
    for hx in (mid - 4, mid + 3):
        obox(cv, hx - 1, 96, hx + 1, 112, BRASS, 4.6)
    # rètol de llautó, dues línies
    obox(cv, 330, 20, 386, 38, BRASS, 3.6)
    for k, s in enumerate(('NOMÉS CLIENTS', 'PREMIUM')):
        text(cv, s, 358 - text_width(s) // 2, 24 + k * 7, [(40, 24, 8)], 0, flat=(40, 24, 8))
    # el llum càlid de sobre
    cv.glow(358, 40, 40, (255, 210, 140), 0.18)
    # la catifa vermella, amb el galó d'or
    pts = [(x0 - 2, FLOOR_Y + 1), (x1 + 2, FLOOR_Y + 1), (x1 + 14, 178), (x0 - 14, 178)]
    cv.poly(pts, CARPET, lambda x, y: 3.4 + (hr(x // 2, y, 5) - 0.5) * 0.4 - (y - FLOOR_Y) * 0.02)
    for (xa, ya), (xb, yb) in ((pts[0], pts[3]), (pts[1], pts[2])):
        cv.line(xa, ya, xb, yb, BRASS, 4.0)
        cv.line(xa + (1 if xa < 358 else -1), ya, xb + (1 if xb < 358 else -1), yb, BRASS, 2.6)
    cv.hline(x0 - 14, x1 + 14, 178, BRASS, 3.0)
    cv.darken(x0 - 14, 179, x1 + 14, 181, 0.45)
    # un pom de corda de vellut, a cada costat
    for px in (x0 - 12, x1 + 12):
        cv.rect(px - 1, 150, px + 1, 176, BRASS, lambda x, y: 4.6 if x == px - 1 else 3.2)
        cv.disc(px, 149, 2.4, 2.4, BRASS, lambda nx, ny: 4.6 - ny)
        cv.rect(px - 3, 176, px + 3, 177, BRASS, 3.0)


def ascensor(cv):
    """L'ascensor de servei: dues fulles d'acer raspallat, el botó i l'indicador de planta («3»)."""
    x0, y0, x1, y1 = 402, 50, 438, FLOOR_Y
    obox(cv, x0 - 4, y0 - 4, x1 + 4, y1, CHROME, 2.6)
    mid = (x0 + x1) // 2
    for a, b in ((x0, mid), (mid + 1, x1)):
        cv.rect(a, y0, b, y1, CHROME, lambda x, y: 2.8 + (0.5 if (x + y // 3) % 7 == 0 else 0) + (0.6 if x == a else 0) - (0.6 if x == b else 0))
    cv.vline(mid, y0, y1, CHROME, 0.6)
    obox(cv, mid - 7, y0 - 14, mid + 7, y0 - 6, [(6, 4, 4), (20, 8, 8)], 0.6, lit=0)
    text(cv, '3', mid - 1, y0 - 12, [(255, 120, 60)], 0, lit=0, flat=(255, 120, 60))
    cv.glow(mid, y0 - 10, 8, (255, 110, 50), 0.25)
    obox(cv, x1 + 7, 92, x1 + 13, 106, CHROME, 3.4)                     # el botó
    cv.disc(x1 + 10, 99, 1.6, 1.6, [(80, 200, 255)], 0, lit=0)


# ─── Parets: quadre, extintor, tub ─────────────────────────────────────────

def quadre(cv):
    """Un quadre motivacional: una muntanya, un sol i «EFICIÈNCIA»."""
    x0, y0, x1, y1 = 214, 36, 262, 80
    obox(cv, x0, y0, x1, y1, BRASS, 3.2)
    cv.rect(x0 + 3, y0 + 3, x1 - 3, y1 - 14, [(30, 50, 90), (60, 90, 140), (110, 150, 190), (180, 200, 220)], lambda x, y: 3.0 - (y - y0) * 0.06)
    cv.poly([(x0 + 3, y1 - 15), (x0 + 20, y0 + 12), (x0 + 30, y0 + 22), (x0 + 36, y0 + 16), (x1 - 3, y1 - 15)], [(20, 30, 40), (50, 60, 70), (90, 100, 110), (200, 210, 220)], lambda x, y: 1.4 + (1.6 if y < y0 + 16 else 0))
    cv.disc(x1 - 12, y0 + 10, 3, 3, [(250, 200, 100)], 0)
    cv.rect(x0 + 3, y1 - 13, x1 - 3, y1 - 3, [(10, 10, 14)], 0)
    w = text_width('EFICIÈNCIA')
    text(cv, 'EFICIÈNCIA', (x0 + x1) // 2 - w // 2, y1 - 10, [(230, 220, 190)], 0, flat=(230, 220, 190))
    cv.darken(x1 + 1, y0 + 2, x1 + 3, y1 + 2, 0.4)
    cv.darken(x0 + 2, y1 + 1, x1 + 3, y1 + 3, 0.4)


def extintor_buit(cv):
    """El lloc de l'extintor: el rètol vermell i el ganxo buit, amb el contorn més net on era."""
    obox(cv, 265, 82, 281, 92, REDB, 3.2)
    text(cv, 'FOC', 273 - text_width('FOC') // 2, 85, [(250, 244, 236)], 0, flat=(250, 244, 236))
    obox(cv, 270, 100, 276, 104, CHROME, 3.0)                            # el ganxo
    cv.rect(272, 104, 274, 108, CHROME, 3.8)


def adhesiu(cv):
    """L'adhesiu de sota la càmera 1: «ZONA NETEJA · NO ES GRAVA»."""
    x0, y0 = 98, 42
    obox(cv, x0, y0, x0 + 47, y0 + 16, YELS, 3.4)
    for k, s in enumerate(('ZONA NETEJA', 'NO ES GRAVA')):
        text(cv, s, x0 + 24 - text_width(s) // 2, y0 + 3 + k * 7, [(30, 22, 6)], 0, flat=(30, 22, 6))


# ─── Càmeres ───────────────────────────────────────────────────────────────

def camera(cv, at, angle=0, led=True, flip=False):
    """Una càmera de seguretat penjada del sostre: suport, braç i el cos que gira (angle -2..2)."""
    cx, top = at
    obox(cv, cx - 4, top + 2, cx + 4, top + 5, CAMB, 3.0)               # placa del sostre
    cv.rect(cx - 1, top + 6, cx + 1, top + 10, CAMB, 3.4)               # braç
    d = -1 if flip else 1
    a = angle * d
    # el cos: una capsa allargada que s'inclina segons l'angle (la lent cap a un costat o l'altre)
    bx0, bx1 = cx - 10 + a, cx + 10 + a
    by0, by1 = top + 10, top + 19
    cv.poly([(bx0 + 2, by0), (bx1, by0 + (1 if a < 0 else 0)), (bx1, by1), (bx0, by1 - (1 if a > 0 else 0)), (bx0, by0 + 2)],
            CAMB, lambda x, y: 5.4 - (y - by0) * 0.3 + (0.6 if y == by0 + 1 else 0))
    outline_poly(cv, [(bx0 + 2, by0), (bx1, by0 + (1 if a < 0 else 0)), (bx1, by1), (bx0, by1 - (1 if a > 0 else 0)), (bx0, by0 + 2)], CAMB)
    # la lent, mirant avall i cap a la porta (a l'esquerra per a la 1, a la dreta per a la 2 si flip)
    lx = (bx0 - 1) if not flip else (bx1 + 1)
    lx += a // 2
    cv.disc(lx, by1 - 3, 3.6, 3.6, [(4, 4, 8), (20, 24, 40), (60, 80, 120), (140, 170, 210)], lambda nx, ny: 1.2 - ny * 0.5 - nx * 0.4, lit=0)
    cv.flat(lx - 1, by1 - 4, (190, 210, 240))
    for k in range(3):                                                  # les ranures del cos
        cv.vline((bx0 + bx1) // 2 - 4 + k * 3 , by0 + 3, by1 - 3, CAMB, 3.0)
    # el LED
    lx2 = bx1 - 3 if not flip else bx0 + 3
    if led:
        cv.flat(lx2, by0 + 2, (255, 50, 40))
        cv.glow(lx2, by0 + 2, 4, (255, 40, 30), 0.5)
    else:
        cv.flat(lx2, by0 + 2, (80, 20, 20))


def cameres(cv, a1=0, a2=0, led=True):
    camera(cv, CAM1, a1, led, flip=True)      # mira a la dreta, cap a la porta de neteja
    camera(cv, CAM2, a2, led, flip=False)     # des del racó, mira a l'esquerra


def bg(cv, a1=0, a2=0, led=True):
    wall(cv)
    floor(cv)
    porta_escala(cv)
    adhesiu(cv)
    porta_neteja(cv)
    quadre(cv)
    extintor_buit(cv)
    tub_station(cv, 294, 70, 312, 112)
    porta_vip(cv)
    ascensor(cv)
    cameres(cv, a1, a2, led)


# ─── Props ──────────────────────────────────────────────────────────────────

def _cartell(cv, cx, base):
    """El cartell groc de terra «NETEJA EN CURS», en forma de A (vist de cara)."""
    top = base - 30
    pts = [(cx - 4, top), (cx + 4, top), (cx + 10, base), (cx - 10, base)]
    cv.poly(pts, YELS, lambda x, y: 3.6 - (x - cx) * 0.06 - (y - top) * 0.02)
    outline_poly(cv, pts, YELS)
    cv.rect(cx - 3, top - 2, cx + 3, top, YELS, 2.6)                    # l'agafador
    ink = (30, 22, 6)
    cv.rect(cx - 1, top + 4, cx + 1, top + 9, [ink], 0)                 # l'admiració
    cv.rect(cx - 1, top + 11, cx + 1, top + 12, [ink], 0)
    cv.disc(cx + 2, top + 17, 1.3, 1.3, [ink], 0)                       # el ninot que rellisca
    cv.line(cx + 1, top + 19, cx - 2, top + 23, [ink], 0)
    cv.line(cx - 2, top + 23, cx + 3, top + 25, [ink], 0)
    cv.line(cx - 1, top + 20, cx + 4, top + 19, [ink], 0)
    cv.line(cx - 6, top + 27, cx + 6, top + 27, [ink], 0)               # el terra moll
    cv.flat(cx - 4, top + 26, ink)
    cv.flat(cx + 5, top + 26, ink)
    cv.darken(cx - 12, base + 1, cx + 12, base + 3, 0.5)


def cartell(cv):
    _cartell(cv, 222, 151)


def galleda(cv, at=(247, 151)):
    """La galleda blava de fregar, amb la nansa."""
    cx, base = at
    pts = [(cx - 8, base - 15), (cx + 8, base - 15), (cx + 6, base), (cx - 6, base)]
    cv.poly(pts, BLUE, lambda x, y: 3.4 - (x - cx) * 0.12)
    outline_poly(cv, pts, BLUE)
    cv.hline(cx - 8, cx + 8, base - 15, BLUE, 5.0)
    cv.hline(cx - 7, cx + 7, base - 14, BLUE, 1.0)                     # l'interior
    cv.hline(cx - 7, cx + 7, base - 10, BLUE, 4.2)                     # el reforç
    for i in range(-7, 8):                                             # la nansa
        cv.put(cx + i, base - 16 - round(5 * (1 - (i / 7) ** 2)), CHROME, 3.6)
    cv.darken(cx - 8, base + 1, cx + 8, base + 2, 0.5)


def extintor(cv):
    """L'extintor vermell, penjat al ganxo."""
    cx = 273
    cv.disc(cx, 104, 4.6, 3, REDB, lambda nx, ny: 3.6 - ny)
    cv.rect(cx - 5, 104, cx + 5, 128, REDB, lambda x, y: 3.0 + (1.6 if x == cx - 3 else 0) - (0.9 if x >= cx + 4 else 0))
    outline(cv, cx - 5, 104, cx + 5, 128, REDB)
    obox(cv, cx - 2, 97, cx + 2, 101, CHROME, 3.0)                     # la vàlvula
    cv.line(cx + 2, 99, cx + 7, 104, CHROME, 3.6)                      # la maneta
    cv.line(cx - 3, 101, cx - 7, 116, CAMB, 1.6)                       # la mànega
    cv.rect(cx - 3, 112, cx + 3, 118, SHEET, 4.4)                      # l'etiqueta
    cv.hline(cx - 2, cx + 2, 114, REDB, 2.6)
    cv.darken(cx + 6, 102, cx + 8, 129, 0.35)


def camera1_tapada(cv):
    """El cartell de «NETEJA EN CURS» penjat davant la càmera 1, amb cinta adhesiva: la tapa sencera."""
    x0, y0, x1, y1 = 105, 17, 139, 47
    cv.poly([(x0, y0 + 2), (x1, y0), (x1 - 1, y1), (x0 + 1, y1 - 1)], YELS, lambda x, y: 3.6 - (x - x0) * 0.02)
    outline_poly(cv, [(x0, y0 + 2), (x1, y0), (x1 - 1, y1), (x0 + 1, y1 - 1)], YELS)
    for k, s in enumerate(('NETEJA', 'EN CURS')):
        text(cv, s, (x0 + x1) // 2 - text_width(s) // 2, y0 + 8 + k * 8, [(30, 22, 6)], 0, flat=(30, 22, 6))
    for (tx, ty) in ((x0 + 2, y0 + 1), (x1 - 6, y0 - 1)):               # la cinta
        cv.rect(tx, ty - 2, tx + 5, ty + 2, [(200, 196, 180), (230, 226, 210)], 1.0)
    cv.darken(x0 + 2, y1 + 1, x1, y1 + 2, 0.4)


def camera2_tapada(cv):
    """La galleda blava de barret a la càmera 2 (cap per avall, la nansa penjant)."""
    cx, top = CAM2[0], CAM2[1] + 4
    base = top + 22
    pts = [(cx - 15, top), (cx + 15, top), (cx + 18, base), (cx - 18, base)]
    cv.poly(pts, BLUE, lambda x, y: 3.4 - (x - cx) * 0.08 + (y - top) * 0.02)
    outline_poly(cv, pts, BLUE)
    cv.hline(cx - 18, cx + 18, base, BLUE, 5.0)
    cv.hline(cx - 17, cx + 17, base - 4, BLUE, 4.2)
    for i in range(-15, 16):                                           # la nansa, penjant per sota
        cv.put(cx + i, base + 1 + round(5 * (1 - (i / 15) ** 2)), CHROME, 3.6)


PROPS = {'cartell': cartell, 'galleda': galleda, 'extintor': extintor,
         'camera1_tapada': camera1_tapada, 'camera2_tapada': camera2_tapada}


# ─── Les càmeres que escombren ─────────────────────────────────────────────

def _frames():
    base = Canvas(light=LIGHT)
    bg(base)
    frames = []
    n = len(CAM_ANGLES)
    for i in range(n):
        cv = Canvas(light=LIGHT)
        bg(cv, CAM_ANGLES[i], CAM_ANGLES[(i + n // 2) % n], led=(i % 2 == 0))
        frames.append(_diff(cv.img, base.img))
    return frames


ANIMS = {'cameres': {'frames': _frames, 'frameDuration': 320}}
