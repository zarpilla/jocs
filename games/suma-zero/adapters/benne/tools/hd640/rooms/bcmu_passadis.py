"""
El passadís del tercer pis del BCMU (Escena 5, l'Iri), a 640×360 (hd/rooms/bcmu_passadis.py redibuixat a ×4/3):
  - un passadís d'oficines sobri: paret de pintura gris perla, arrimador de caoba amb plafons, sòcol fosc i catifa
    corporativa blau marí amb un rombe d'or; tres fluorescents al sostre de plaques;
  - a l'esquerra, la porta vella de l'escala (fusta de 1958, frontisses, pany antic de clau grossa, rètol ESCALA);
  - la càmera 1 al sostre, mirant la porta de neteja, amb l'adhesiu «ZONA NETEJA · NO ES GRAVA»;
  - la porta de servei de neteja (xapa grisa, rètol NETEJA), un quadre motivacional («EFICIÈNCIA»),
    el ganxo buit de l'extintor (amb la marca de pintura més neta on era), l'estació del tub;
  - la porta VIP de caoba i llautó amb la catifa vermella i el rètol «NOMÉS CLIENTS PREMIUM»;
  - l'ascensor de servei (xapa, botó i el «3»), i la càmera 2 al racó de dalt a la dreta.

Props: 'cartell', 'galleda', 'extintor' (es poden agafar: al fons només hi ha el lloc buit),
'camera1_tapada' (el cartell de neteja penjat davant la càmera 1), 'camera2_tapada' (la galleda de barret).
Animació: `cameres`, les dues càmeres escombren el passadís i el LED vermell parpelleja.
"""
import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from hd.pix import Light, Canvas, W, H, hr
from hd.rooms.comu import obox, outline, text, text_width, _diff, SHEET, YEL  # noqa: F401
from hd.rooms.pis_cuina import outline_poly
from hd.rooms.aeroport_terminal import CHROME, YELS, BLUE
from hd.rooms.aeroport_personal import REDB
from hd.rooms.bcmu_passadis import PAINT, DOORG, OLDWOOD, CAMB
from hd640.rooms.bcmu import MAHOG, BRASS, NAVYB, CARPET, CONCB, MARBLE, tub_station, logo, sign  # noqa: F401

# Art a 2× (1280×720 per a una sala de 640×360): el mateix dibuix, amb les formes, el dither i la llum a la
# resolució real (hd1280/canvas2x.py); el motor el mostra a 1/2 (artScale al .room.json).
ART_SCALE = 2
from hd1280.canvas2x import Canvas2x as Canvas  # noqa: E402,F811
from hd.pix import Canvas as Canvas1x  # noqa: E402,F401  (llenços auxiliars en píxels de sala: figures, textos)

FLOOR_Y = 200

LIGHT = Light(ambient=-0.25, vignette=(80, 40), floor_fade=(253, 40))
for _x in (120, 333, 547):
    LIGHT.point(_x, 5, r=200, k=1.6, squash=0.8, power=1.4)              # els fluorescents
LIGHT.point(477, 80, r=80, k=0.5, squash=1.0, power=2.0)                 # el llum càlid de sobre la porta VIP

TUBES = (120, 333, 547)
CAM1 = (161, 19)    # on penja la càmera 1 (el suport)
CAM2 = (609, 19)
CAM_ANGLES = [0, -1, -2, -3, -3, -2, -1, 0, 1, 2, 3, 3, 2, 1]


# ─── Paret, sostre, terra ──────────────────────────────────────────────────

def wall(cv):
    """Pintura gris perla a dalt, arrimador de caoba amb plafons a baix, i el sostre de plaques."""
    for y in range(21, 144):
        for x in range(W):
            n = (hr(x // 4, y // 4, 7) - 0.5) * 0.25 + (hr(x, y, 8) - 0.5) * 0.08
            cv.put(x, y, PAINT, 5.0 + n)
    # pilastres suaus cada tram
    for px in (104, 275, 384, 424, 528):
        cv.rect(px, 21, px + 4, 143, PAINT, lambda x, y: 5.6 if x == px else (4.4 if x == px + 4 else 5.2))
    # arrimador: el passamà i els plafons
    cv.rect(0, 139, W - 1, 143, MAHOG, lambda x, y: 4.6 if y == 139 else (3.8 if y == 140 else 3.4) - (0.8 if y == 143 else 0))
    for y in range(144, FLOOR_Y - 5):
        for x in range(W):
            u = x % 53
            panel = u in (0, 1) or y in (147, FLOOR_Y - 9)
            hi = u == 2 or y == 148
            n = (hr(x, y // 3, 3) - 0.5) * 0.3 + (hr(x // 2, y // 11, 5) - 0.5) * 0.15
            cv.put(x, y, MAHOG, (2.0 if panel else 3.0) + (0.6 if hi else 0) + n)
    cv.rect(0, FLOOR_Y - 5, W - 1, FLOOR_Y - 1, MAHOG, lambda x, y: 1.4 + (0.6 if y == FLOOR_Y - 5 else 0))   # sòcol
    cv.hline(0, W - 1, FLOOR_Y, MAHOG, 0)
    # sostre de plaques, amb els forats de les plaques acústiques
    for y in range(0, 21):
        for x in range(W):
            seam = (x % 64 == 0) or y == 20 or y == 10
            dot = (x % 4 == 2 and y % 4 == 1) and hr(x, y, 12) > 0.4
            cv.put(x, y, MARBLE, (2.2 if seam else 3.2) + (hr(x // 5, y // 5, 9) - 0.5) * 0.2 - (0.3 if dot else 0))
    cv.hline(0, W - 1, 21, PAINT, 2.0)
    cv.hline(0, W - 1, 22, PAINT, 3.8)
    for fx in TUBES:
        tube(cv, fx)


def tube(cv, cx):
    """Un fluorescent de sostre: caixa cromada, dos tubs encesos i el difusor."""
    obox(cv, cx - 35, 2, cx + 35, 10, CHROME, 3.4)
    cv.hline(cx - 32, cx + 32, 5, [(236, 246, 255)], 0, lit=0)
    cv.hline(cx - 32, cx + 32, 6, [(214, 230, 244)], 0, lit=0)
    cv.hline(cx - 32, cx + 32, 7, [(236, 246, 255)], 0, lit=0)
    cv.hline(cx - 32, cx + 32, 8, [(190, 210, 228)], 0, lit=0)
    for x in range(cx - 24, cx + 25, 16):                              # les pinces dels tubs
        cv.vline(x, 4, 9, CHROME, 4.0)
    for ex in (cx - 34, cx + 33):
        cv.rect(ex, 4, ex + 1, 8, CHROME, 2.0)
    cv.glow(cx, 9, 35, (230, 240, 255), 0.22)


def floor(cv):
    """Catifa blau marí amb el rombe d'or del banc, gastada pel mig."""
    for y in range(FLOOR_Y + 1, H):
        gy = y - FLOOR_Y
        for x in range(W):
            n = (hr(x // 2, y // 2, 4) - 0.5) * 0.35 + (hr(x, y, 6) - 0.5) * 0.1
            u, v = x % 32, gy % 18.67
            d = abs(u - 16) / 16 + abs(v - 9.33) / 9.33
            worn = max(0, 1 - abs(y - 248) / 24) * 0.5
            lvl = 3.2 + n + worn
            if 0.93 < d < 1.07:
                cv.put(x, y, BRASS, 2.0 + n)
            elif d < 0.12:
                cv.put(x, y, BRASS, 1.6 + n)                            # un punt d'or al mig
            else:
                cv.put(x, y, NAVYB, lvl)
    cv.darken(0, FLOOR_Y + 1, W - 1, FLOOR_Y + 5, 0.5)


# ─── Portes ────────────────────────────────────────────────────────────────

def porta_escala(cv):
    """La porta vella de l'escala: fusta de 1958, plafons, frontisses i un pany de llautó per a una clau grossa."""
    x0, y0, x1, y1 = 19, 67, 80, FLOOR_Y
    obox(cv, x0 - 5, y0 - 5, x1 + 5, y1, MAHOG, 2.6)
    cv.hline(x0 - 4, x1 + 4, y0 - 4, MAHOG, 3.6)
    obox(cv, x0, y0, x1, y1, OLDWOOD, 3.0, top=0.4)
    for y in range(y0 + 1, y1):                                        # la veta de la fusta, vella
        for x in range(x0 + 1, x1):
            if hr(x, y // 7, 21) > 0.86:
                cv.put(x, y, OLDWOOD, 2.5)
    for (a, b) in ((y0 + 8, y0 + 59), (y0 + 69, y1 - 11)):
        cv.rect(x0 + 7, a, x1 - 7, b, OLDWOOD, lambda x, y: 2.6 + (hr(x, y // 6, 22) - 0.5) * 0.3)
        cv.hline(x0 + 7, x1 - 7, a, OLDWOOD, 1.4)
        cv.vline(x0 + 7, a, b, OLDWOOD, 1.4)
        cv.hline(x0 + 7, x1 - 7, b, OLDWOOD, 4.2)
        cv.vline(x1 - 7, a, b, OLDWOOD, 4.0)
    for hy in (y0 + 10, y1 - 22):                                      # les frontisses
        obox(cv, x0 - 1, hy, x0 + 2, hy + 9, BRASS, 2.4)
    # el pany: placa amb reblons, el forat de la clau grossa i el pom
    obox(cv, x1 - 17, 125, x1 - 7, 149, BRASS, 3.4)
    for ry in (127, 147):
        cv.flat(x1 - 12, ry, BRASS[6])
    cv.disc(x1 - 12, 133, 2.1, 2.1, [(8, 6, 4)], 0)
    cv.rect(x1 - 13, 135, x1 - 11, 140, [(8, 6, 4)], 0)
    cv.disc(x1 - 12, 145, 2, 2, BRASS, lambda nx, ny: 5.0 - ny - nx * 0.5)
    # rètol
    sign(cv, 33, 45, 'ESCALA', NAVYB, 3.0, ink=(236, 210, 140))
    cv.darken(x1 + 6, y0, x1 + 10, y1, 0.35)


def porta_neteja(cv):
    """La porta de servei de la neteja: xapa grisa, una reixeta, el tancaportes i la barra antipànic."""
    x0, y0, x1, y1 = 200, 75, 267, FLOOR_Y
    obox(cv, x0 - 4, y0 - 4, x1 + 4, y1, CHROME, 2.6)
    obox(cv, x0, y0, x1, y1, DOORG, 3.4, top=0.6)
    for k in range(6):                                                  # reixeta de ventilació
        cv.hline(x0 + 16, x1 - 16, y1 - 31 + k * 4, DOORG, 1.6)
        cv.hline(x0 + 16, x1 - 16, y1 - 30 + k * 4, DOORG, 4.6)
    outline(cv, x0 + 15, y1 - 32, x1 - 15, y1 - 8, DOORG)
    cv.rect(x0 + 5, 139, x1 - 5, 143, CHROME, lambda x, y: 4.2 if y == 139 else 3.0)
    obox(cv, x1 - 12, 131, x1 - 5, 147, CHROME, 3.2)
    # el tancaportes, a dalt
    obox(cv, x0 + 6, y0 + 3, x0 + 26, y0 + 8, CHROME, 3.0)
    cv.line(x0 + 26, y0 + 5, x0 + 40, y0 + 2, CHROME, 3.6)
    # rètol
    w = text_width('NETEJA')
    obox(cv, 233 - w // 2 - 6, 54, 233 + w // 2 + 6, 68, [(200, 210, 214), (230, 234, 236), (250, 252, 252)], 1.4)
    text(cv, 'NETEJA', 233 - w // 2, 59, [(30, 40, 50)], 0, flat=(30, 40, 50))
    # el rastre del robot: unes rodes que surten per sota
    cv.tint(x0 + 8, y1 + 1, x1 - 8, y1 + 40, (150, 170, 200), lambda x, y: 0.06 if (x - x0) % 16 in (0, 1) else 0)


def porta_vip(cv):
    """La porta VIP: dues fulles de caoba amb motllures de llautó, manetes daurades i la catifa vermella."""
    x0, y0, x1, y1 = 435, 61, 520, FLOOR_Y
    obox(cv, x0 - 7, y0 - 7, x1 + 7, y1, MARBLE, 4.2)                   # marc de marbre
    cv.hline(x0 - 6, x1 + 6, y0 - 6, MARBLE, 5.6)
    mid = (x0 + x1) // 2
    for a, b in ((x0, mid), (mid + 1, x1)):
        obox(cv, a, y0, b, y1, MAHOG, 3.6, top=0.6)
        obox(cv, a + 5, y0 + 8, b - 5, y0 + 64, BRASS, 2.2)
        cv.rect(a + 6, y0 + 9, b - 6, y0 + 63, MAHOG, lambda x, y: 3.2 + (hr(x, y // 5, 13) - 0.5) * 0.3)
        cv.hline(a + 6, b - 6, y0 + 9, MAHOG, 2.0)
        obox(cv, a + 5, y0 + 72, b - 5, y1 - 11, BRASS, 2.2)
        cv.rect(a + 6, y0 + 73, b - 6, y1 - 12, MAHOG, lambda x, y: 3.2 + (hr(x, y // 5, 14) - 0.5) * 0.3)
        cv.hline(a + 6, b - 6, y0 + 73, MAHOG, 2.0)
    for hx in (mid - 5, mid + 4):
        obox(cv, hx - 1, 128, hx + 1, 149, BRASS, 4.6)
    # rètol de llautó, dues línies
    obox(cv, 440, 27, 515, 51, BRASS, 3.6)
    outline(cv, 442, 29, 513, 49, BRASS)
    for k, s in enumerate(('NOMÉS CLIENTS', 'PREMIUM')):
        text(cv, s, 477 - text_width(s) // 2, 33 + k * 9, [(40, 24, 8)], 0, flat=(40, 24, 8))
    # el llum càlid de sobre
    cv.glow(477, 53, 53, (255, 210, 140), 0.18)
    # la catifa vermella, amb el galó d'or
    pts = [(x0 - 3, FLOOR_Y + 1), (x1 + 3, FLOOR_Y + 1), (x1 + 19, 237), (x0 - 19, 237)]
    cv.poly(pts, CARPET, lambda x, y: 3.4 + (hr(x // 2, y, 5) - 0.5) * 0.4 - (y - FLOOR_Y) * 0.015)
    for (xa, ya), (xb, yb) in ((pts[0], pts[3]), (pts[1], pts[2])):
        cv.line(xa, ya, xb, yb, BRASS, 4.0)
        cv.line(xa + (1 if xa < 477 else -1), ya, xb + (1 if xb < 477 else -1), yb, BRASS, 2.6)
        cv.line(xa + (3 if xa < 477 else -3), ya, xb + (3 if xb < 477 else -3), yb, BRASS, 3.0)
    cv.hline(x0 - 19, x1 + 19, 237, BRASS, 3.0)
    cv.darken(x0 - 19, 238, x1 + 19, 241, 0.45)
    # un pom de corda de vellut, a cada costat
    for px in (x0 - 16, x1 + 16):
        cv.rect(px - 1, 200, px + 1, 235, BRASS, lambda x, y: 4.6 if x == px - 1 else 3.2)
        cv.disc(px, 198, 3.2, 3.2, BRASS, lambda nx, ny: 4.6 - ny - nx * 0.4)
        cv.rect(px - 4, 235, px + 4, 236, BRASS, 3.0)
        cv.darken(px - 5, 237, px + 5, 238, 0.4)


def ascensor(cv):
    """L'ascensor de servei: dues fulles d'acer raspallat, el botó i l'indicador de planta («3»)."""
    x0, y0, x1, y1 = 536, 67, 584, FLOOR_Y
    obox(cv, x0 - 5, y0 - 5, x1 + 5, y1, CHROME, 2.6)
    mid = (x0 + x1) // 2
    for a, b in ((x0, mid), (mid + 1, x1)):
        cv.rect(a, y0, b, y1, CHROME,
                lambda x, y: 2.8 + (0.5 if (x + y // 4) % 9 == 0 else 0) + (0.6 if x == a else 0) - (0.6 if x == b else 0))
    cv.vline(mid, y0, y1, CHROME, 0.6)
    cv.rect(x0, y1 - 3, x1, y1, CHROME, 1.6)                            # el llindar
    obox(cv, mid - 9, y0 - 19, mid + 9, y0 - 8, [(6, 4, 4), (20, 8, 8)], 0.6, lit=0)
    text(cv, '3', mid - 1, y0 - 16, [(255, 120, 60)], 0, lit=0, flat=(255, 120, 60))
    cv.glow(mid, y0 - 13, 11, (255, 110, 50), 0.25)
    obox(cv, x1 + 9, 123, x1 + 17, 141, CHROME, 3.4)                    # el botó
    cv.disc(x1 + 13, 132, 2.1, 2.1, [(80, 200, 255)], 0, lit=0)
    cv.flat(x1 + 12, 131, (200, 240, 255))


# ─── Parets: quadre, extintor, tub ─────────────────────────────────────────

def quadre(cv):
    """Un quadre motivacional: una muntanya amb una banderola al cim, un sol i «EFICIÈNCIA»."""
    x0, y0, x1, y1 = 285, 48, 349, 107
    obox(cv, x0, y0, x1, y1, BRASS, 3.2)
    cv.rect(x0 + 4, y0 + 4, x1 - 4, y1 - 19, [(30, 50, 90), (60, 90, 140), (110, 150, 190), (180, 200, 220)],
            lambda x, y: 3.0 - (y - y0) * 0.045)
    cv.disc(x1 - 16, y0 + 13, 4, 4, [(250, 200, 100)], 0)
    cv.glow(x1 - 16, y0 + 13, 9, (255, 220, 150), 0.25)
    cv.poly([(x0 + 4, y1 - 20), (x0 + 27, y0 + 16), (x0 + 40, y0 + 29), (x0 + 48, y0 + 21), (x1 - 4, y1 - 20)],
            [(20, 30, 40), (50, 60, 70), (90, 100, 110), (200, 210, 220)], lambda x, y: 1.4 + (1.6 if y < y0 + 21 else 0))
    cv.vline(x0 + 27, y0 + 10, y0 + 16, [(30, 30, 30)], 0)              # la banderola del cim
    cv.rect(x0 + 28, y0 + 10, x0 + 30, y0 + 11, [(220, 40, 40)], 0)
    cv.rect(x0 + 4, y1 - 17, x1 - 4, y1 - 4, [(10, 10, 14)], 0)
    w = text_width('EFICIÈNCIA')
    text(cv, 'EFICIÈNCIA', (x0 + x1) // 2 - w // 2, y1 - 12, [(230, 220, 190)], 0, flat=(230, 220, 190))
    cv.darken(x1 + 1, y0 + 3, x1 + 4, y1 + 3, 0.4)
    cv.darken(x0 + 3, y1 + 1, x1 + 4, y1 + 4, 0.4)


def extintor_buit(cv):
    """El lloc de l'extintor: el rètol vermell i el ganxo buit, amb el contorn més net on era."""
    cv.tint(357, 132, 371, 138, (220, 218, 210), 0.06)                  # la pintura més neta
    obox(cv, 353, 109, 375, 123, REDB, 3.2)
    text(cv, 'FOC', 364 - text_width('FOC') // 2, 113, [(250, 244, 236)], 0, flat=(250, 244, 236))
    obox(cv, 360, 133, 368, 139, CHROME, 3.0)                            # el ganxo
    cv.rect(362, 139, 366, 144, CHROME, 3.8)
    cv.flat(364, 136, CHROME[1])


def adhesiu(cv):
    """L'adhesiu de sota la càmera 1: «ZONA NETEJA · NO ES GRAVA»."""
    x0, y0 = 131, 56
    obox(cv, x0, y0, x0 + 63, y0 + 21, YELS, 3.4)
    cv.hline(x0 + 1, x0 + 62, y0 + 1, YELS, 4.4)
    for k, s in enumerate(('ZONA NETEJA', 'NO ES GRAVA')):
        text(cv, s, x0 + 32 - text_width(s) // 2, y0 + 4 + k * 9, [(30, 22, 6)], 0, flat=(30, 22, 6))
    cv.flat(x0 + 63, y0 + 21, PAINT[5])                                 # una punta que es desenganxa
    cv.flat(x0 + 62, y0 + 21, YELS[1])


# ─── Càmeres ───────────────────────────────────────────────────────────────

def camera(cv, at, angle=0, led=True, flip=False):
    """Una càmera de seguretat penjada del sostre: suport, braç i el cos que gira (angle -3..3)."""
    cx, top = at
    obox(cv, cx - 5, top + 3, cx + 5, top + 7, CAMB, 3.0)               # placa del sostre
    cv.flat(cx - 3, top + 5, CAMB[5])
    cv.flat(cx + 3, top + 5, CAMB[5])
    cv.rect(cx - 1, top + 8, cx + 1, top + 13, CAMB, lambda x, y: 4.2 if x == cx - 1 else 3.2)   # braç
    d = -1 if flip else 1
    a = angle * d
    # el cos: una capsa allargada que s'inclina segons l'angle (la lent cap a un costat o l'altre)
    bx0, bx1 = cx - 13 + a, cx + 13 + a
    by0, by1 = top + 13, top + 25
    sl = 1 if abs(a) >= 2 else 0
    pts = [(bx0 + 3, by0), (bx1, by0 + (sl if a < 0 else 0)), (bx1, by1), (bx0, by1 - (sl if a > 0 else 0)), (bx0, by0 + 3)]
    cv.poly(pts, CAMB, lambda x, y: 5.4 - (y - by0) * 0.22 + (0.6 if y == by0 + 1 else 0))
    outline_poly(cv, pts, CAMB)
    # la visera
    cv.hline(bx0 + 3, bx1 - 1, by0 + 1, CAMB, 6.0)
    # la lent, mirant avall i cap a la porta
    lx = (bx0 - 1) if not flip else (bx1 + 1)
    lx += a // 2
    cv.disc(lx, by1 - 4, 4.8, 4.8, [(4, 4, 8), (20, 24, 40), (60, 80, 120), (140, 170, 210)],
            lambda nx, ny: 1.2 - ny * 0.5 - nx * 0.4, lit=0)
    cv.disc(lx, by1 - 4, 2, 2, [(4, 4, 8), (20, 24, 40)], 0, lit=0)
    cv.flat(lx - 2, by1 - 6, (190, 210, 240))
    cv.flat(lx - 1, by1 - 6, (150, 170, 210))
    for k in range(4):                                                  # les ranures del cos
        cv.vline((bx0 + bx1) // 2 - 5 + k * 3, by0 + 4, by1 - 3, CAMB, 3.0)
    # el LED
    lx2 = bx1 - 4 if not flip else bx0 + 4
    if led:
        cv.flat(lx2, by0 + 3, (255, 50, 40))
        cv.glow(lx2, by0 + 3, 5, (255, 40, 30), 0.5)
    else:
        cv.flat(lx2, by0 + 3, (80, 20, 20))


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
    tub_station(cv, 392, 93, 417, 150)
    porta_vip(cv)
    ascensor(cv)
    cameres(cv, a1, a2, led)


# ─── Props ──────────────────────────────────────────────────────────────────

def _cartell(cv, cx, base):
    """El cartell groc de terra «NETEJA EN CURS», en forma de A (vist de cara)."""
    top = base - 40
    pts = [(cx - 5, top), (cx + 5, top), (cx + 13, base), (cx - 13, base)]
    cv.poly(pts, YELS, lambda x, y: 3.6 - (x - cx) * 0.045 - (y - top) * 0.015)
    outline_poly(cv, pts, YELS)
    cv.line(cx - 4, top + 1, cx - 11, base - 1, YELS, 4.4)              # el cantell que agafa llum
    cv.rect(cx - 4, top - 3, cx + 4, top, YELS, lambda x, y: 2.6 + (0.8 if y == top - 3 else 0))   # l'agafador
    cv.rect(cx - 2, top - 2, cx + 2, top - 1, [(30, 22, 6)], 0)
    ink = (30, 22, 6)
    cv.poly([(cx - 2, top + 5), (cx + 3, top + 5), (cx + 2, top + 12), (cx - 1, top + 12)], [ink], 0)   # l'admiració
    cv.rect(cx - 1, top + 14, cx + 2, top + 16, [ink], 0)
    cv.disc(cx + 3, top + 22, 1.8, 1.8, [ink], 0)                       # el ninot que rellisca
    cv.line(cx + 1, top + 25, cx - 3, top + 31, [ink], 0)
    cv.line(cx - 3, top + 31, cx + 4, top + 33, [ink], 0)
    cv.line(cx - 3, top + 32, cx - 6, top + 34, [ink], 0)
    cv.line(cx, top + 26, cx + 6, top + 24, [ink], 0)
    cv.line(cx, top + 26, cx - 4, top + 23, [ink], 0)
    cv.line(cx - 8, top + 36, cx + 8, top + 36, [ink], 0)               # el terra moll
    for dx in (-6, 7):
        cv.flat(cx + dx, top + 35, ink)
        cv.flat(cx + dx, top + 34, ink)
    cv.darken(cx - 16, base + 1, cx + 16, base + 4, 0.5)


def cartell(cv):
    _cartell(cv, 296, 201)


def galleda(cv, at=(329, 201)):
    """La galleda blava de fregar, amb la nansa."""
    cx, base = at
    pts = [(cx - 11, base - 20), (cx + 11, base - 20), (cx + 8, base), (cx - 8, base)]
    cv.poly(pts, BLUE, lambda x, y: 3.4 - (x - cx) * 0.09)
    outline_poly(cv, pts, BLUE)
    cv.hline(cx - 11, cx + 11, base - 20, BLUE, 5.0)
    cv.hline(cx - 10, cx + 10, base - 19, BLUE, 1.0)                    # l'interior
    cv.hline(cx - 8, cx + 6, base - 18, [(60, 90, 110), (90, 130, 150)], 1, lit=0)   # l'aigua bruta
    cv.hline(cx - 9, cx + 9, base - 13, BLUE, 4.2)                      # el reforç
    cv.hline(cx - 9, cx + 9, base - 12, BLUE, 2.4)
    cv.vline(cx - 6, base - 11, base - 2, BLUE, 4.6)                    # la llum
    for i in range(-10, 11):                                            # la nansa
        cv.put(cx + i, base - 21 - round(7 * (1 - (i / 10) ** 2)), CHROME, 3.6)
    for s in (-1, 1):
        cv.disc(cx + s * 10, base - 19, 1.2, 1.2, CHROME, 3.0)
    cv.darken(cx - 11, base + 1, cx + 11, base + 3, 0.5)


def extintor(cv):
    """L'extintor vermell, penjat al ganxo."""
    cx = 364
    cv.disc(cx, 139, 6.1, 4, REDB, lambda nx, ny: 3.6 - ny - nx * 0.3)
    cv.rect(cx - 7, 139, cx + 7, 171, REDB,
            lambda x, y: 3.0 + (1.6 if x == cx - 4 else (0.8 if x == cx - 5 else 0)) - (0.9 if x >= cx + 5 else 0))
    outline(cv, cx - 7, 139, cx + 7, 171, REDB)
    obox(cv, cx - 3, 129, cx + 3, 135, CHROME, 3.0)                     # la vàlvula
    cv.rect(cx - 1, 135, cx + 1, 136, CHROME, 2.4)
    cv.line(cx + 3, 131, cx + 9, 137, CHROME, 3.6)                      # la maneta
    cv.line(cx + 3, 132, cx + 9, 138, CHROME, 2.4)
    cv.line(cx - 4, 134, cx - 9, 154, CAMB, 1.6)                        # la mànega
    cv.line(cx - 5, 134, cx - 10, 154, CAMB, 1.0)
    cv.rect(cx - 10, 154, cx - 8, 157, CAMB, 2.4)
    cv.rect(cx - 4, 149, cx + 4, 157, SHEET, 4.4)                       # l'etiqueta
    cv.hline(cx - 3, cx + 3, 151, REDB, 2.6)
    cv.hline(cx - 3, cx + 1, 154, SHEET, 2.6)
    cv.darken(cx + 8, 136, cx + 11, 172, 0.35)


def camera1_tapada(cv):
    """El cartell de «NETEJA EN CURS» penjat davant la càmera 1, amb cinta adhesiva: la tapa sencera."""
    x0, y0, x1, y1 = 140, 23, 185, 63
    pts = [(x0, y0 + 3), (x1, y0), (x1 - 1, y1), (x0 + 1, y1 - 1)]
    cv.poly(pts, YELS, lambda x, y: 3.6 - (x - x0) * 0.015)
    outline_poly(cv, pts, YELS)
    for k, s in enumerate(('NETEJA', 'EN CURS')):
        text(cv, s, (x0 + x1) // 2 - text_width(s) // 2, y0 + 11 + k * 10, [(30, 22, 6)], 0, flat=(30, 22, 6))
    for (tx, ty) in ((x0 + 3, y0 + 1), (x1 - 8, y0 - 1)):               # la cinta
        cv.rect(tx, ty - 3, tx + 6, ty + 2, [(200, 196, 180), (230, 226, 210)], lambda x, y: 1.0 if (x + y) % 3 else 0.6)
    cv.darken(x0 + 3, y1 + 1, x1, y1 + 3, 0.4)


def camera2_tapada(cv):
    """La galleda blava de barret a la càmera 2 (cap per avall, la nansa penjant)."""
    cx, top = CAM2[0], CAM2[1] + 5
    base = top + 29
    pts = [(cx - 20, top), (cx + 20, top), (cx + 24, base), (cx - 24, base)]
    cv.poly(pts, BLUE, lambda x, y: 3.4 - (x - cx) * 0.06 + (y - top) * 0.015)
    outline_poly(cv, pts, BLUE)
    cv.hline(cx - 24, cx + 24, base, BLUE, 5.0)
    cv.hline(cx - 23, cx + 23, base - 5, BLUE, 4.2)
    cv.hline(cx - 23, cx + 23, base - 4, BLUE, 2.4)
    cv.line(cx - 12, top + 2, cx - 15, base - 7, BLUE, 4.6)              # la llum
    for i in range(-20, 21):                                            # la nansa, penjant per sota
        cv.put(cx + i, base + 1 + round(7 * (1 - (i / 20) ** 2)), CHROME, 3.6)


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
        bg(cv, CAM_ANGLES[i], CAM_ANGLES[(i + n // 2) % n], led=(i % 4 < 2))
        frames.append(_diff(cv.img, base.img))
    return frames


ANIMS = {'cameres': {'frames': _frames, 'frameDuration': 230}}


# ─── Geometria (640×360) ───────────────────────────────────────────────────

GEOMETRIA = {
    'things': {
        'porta_escala': {'rect': (14, 62, 85, 200), 'walk': (51, 248)},
        'camera1': {'rect': (142, 22, 182, 51), 'walk': (163, 248)},
        'porta_neteja': {'rect': (196, 71, 271, 200), 'walk': (235, 248)},
        'cartell': {'rect': (281, 157, 311, 203), 'walk': (296, 251)},
        'galleda': {'rect': (316, 173, 342, 204), 'walk': (331, 253)},
        'extintor': {'rect': (353, 127, 375, 174), 'walk': (365, 248)},
        'tub': {'rect': (392, 93, 417, 150), 'walk': (405, 248)},
        'porta_vip': {'rect': (428, 54, 527, 200), 'walk': (477, 251)},
        'ascensor': {'rect': (531, 62, 589, 200), 'walk': (560, 248)},
        'camera2': {'rect': (592, 22, 626, 51), 'walk': (603, 248)},
    },
    'spawns': {'iri': (133, 261), 'neta': (261, 253)},
    'walkable': [(19, 236), (621, 236), (632, 271), (8, 271)],
}
