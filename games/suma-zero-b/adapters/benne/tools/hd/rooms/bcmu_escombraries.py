"""
La sala d'escombraries del tercer pis del BCMU (Escenes 5 i 6, l'Iri): on van jubilar el Llibre Major. Art definitiu:
  - el darrere de l'edifici de 1958 sense maquillatge: formigó pintat de gris amb brutícia, una franja de pintura
    verda d'hospital a baix, canonades al sostre i un fluorescent brut que fa la llum justa;
  - EL LLIBRE MAJOR: un mainframe gris de 1984, alt i ample com un armari, amb la placa «LLIBRE MAJOR · 1984»,
    una pantalla de fòsfor verd (la claror verda de tota la sala), una filera de llums, el teclat que pesa com una
    nevera i, a sota, el pany de llautó per a una clau grossa;
  - a l'esquerra, la porta del passadís; les bosses de paper triturat (confeti de secrets bancaris) i el conducte
    d'escombraries, amb la comporta;
  - a la dreta, l'estació del tub de 1958 (plena de pols) i el panell de control de NETA-3, amb la seva base de
    càrrega a terra.
"""
import math

from hd.pix import Light, Canvas, W, H, hr
from hd.rooms.comu import obox, outline, cable, text, text_width, _diff, PLASTIC, SHEET, CARD, YEL, GRAYC
from hd.rooms.bar_sala import STEELB, SLATE
from hd.rooms.pis_cuina import outline_poly
from hd.rooms.bcmu import CONCB, DUST, BRASS, LINOB, SCREENB, tub_station

FLOOR_Y = 150
TUBE = (110, 4)            # el fluorescent brut
SCREEN = (252, 50, 324, 88)  # la pantalla del Llibre Major

WALLG = [(14, 16, 16), (24, 28, 28), (36, 40, 40), (50, 56, 54), (66, 72, 70), (84, 92, 88), (104, 112, 106), (126, 134, 126)]
HOSP = [(8, 20, 16), (14, 34, 26), (22, 50, 38), (34, 68, 52), (50, 88, 68), (70, 110, 86)]
MAIN = [(12, 14, 18), (22, 26, 32), (34, 38, 46), (50, 56, 64), (68, 74, 84), (90, 96, 104), (114, 120, 126), (142, 146, 150), (176, 178, 178)]
BEIGE = [(30, 26, 20), (56, 50, 40), (86, 78, 62), (118, 108, 86), (150, 140, 112), (182, 172, 140), (208, 200, 170)]
BAG = [(6, 6, 8), (12, 12, 16), (20, 20, 26), (30, 30, 38), (44, 44, 54), (64, 64, 76)]
DOORG = [(12, 16, 18), (22, 28, 30), (34, 42, 44), (50, 60, 60), (68, 80, 78), (90, 102, 98), (116, 128, 122)]
REDL = [(60, 6, 6), (140, 20, 16), (220, 50, 36), (255, 120, 90)]
AMBER = [(60, 30, 4), (140, 80, 10), (220, 150, 30), (255, 210, 110)]
GREENL = [(4, 30, 12), (14, 90, 34), (40, 190, 80), (160, 255, 180)]
STRIPE = [(30, 22, 4), (90, 66, 8), (170, 128, 20), (230, 186, 40)]

LIGHT = Light(ambient=-0.7, vignette=(64, 36), floor_fade=(188, 28))
LIGHT.point(TUBE[0], TUBE[1] + 4, r=220, k=2.6, squash=0.9, power=1.5)   # el fluorescent brut
LIGHT.point(288, 70, r=150, k=1.8, squash=1.1, power=1.8)               # la pantalla del Llibre Major
LIGHT.point(410, 92, r=40, k=0.5, squash=1.0, power=2.0)                # el panell de NETA-3


def green_cast(x, y):
    """Quant tenyeix de verd la pantalla del Llibre Major (0..1)."""
    d = math.hypot((x - 288) / 1.3, y - 70)
    return max(0.0, 1 - d / 150) ** 2


# ─── Paret, sostre, terra ──────────────────────────────────────────────────

def wall(cv):
    """Formigó pintat de gris, a panells, amb regalims; a baix, una franja de verd d'hospital rascada."""
    for y in range(0, FLOOR_Y):
        for x in range(W):
            panel = x // 60
            joint = (x % 60 == 59) or (y % 50 == 49)
            n = (hr(x // 2, y // 2, 3) - 0.5) * 0.35 + (hr(panel, y // 50, 8) - 0.5) * 0.4
            drip = 0.5 if hr(x // 3, 11) > 0.92 and y > 20 + hr(x // 3, 12) * 40 else 0
            if y >= 112:
                scratch = 0.7 if hr(x // 5, y // 2, 21) > 0.93 else 0
                cv.put(x, y, HOSP, (1.8 if joint else 3.0 + n) + scratch)
            else:
                cv.put(x, y, WALLG, (2.4 if joint else 3.6 + n) - drip)
    cv.rect(0, 110, W - 1, 111, WALLG, 2.0)                             # el filet entre el gris i el verd
    cv.rect(0, FLOOR_Y - 3, W - 1, FLOOR_Y - 1, CONCB, 2.0)
    cv.hline(0, W - 1, FLOOR_Y, CONCB, 0)


def ceiling(cv, tube=1.0):
    """Canonades i una safata de cables, i el fluorescent brut, amb mosques mortes a la tapa.

    `tube`: com d'encès és el fluorescent (1 = normal; per a l'animació `fluorescent`, que fa figa)."""
    cv.rect(0, 0, W - 1, 3, CONCB, 2.4)
    cv.rect(0, 14, W - 1, 18, STEELB, lambda x, y: 2.8 + (1.4 if y == 15 else 0) - (1.0 if y == 18 else 0))
    for bx in range(20, W, 80):
        cv.rect(bx, 12, bx + 2, 19, STEELB, 1.8)
    cv.rect(0, 22, 230, 24, DUST, lambda x, y: 2.6 + (0.8 if y == 22 else 0))   # una canonada vella
    cv.rect(228, 22, 232, 34, DUST, 2.4)
    # el fluorescent
    x0, x1 = TUBE[0] - 40, TUBE[0] + 40
    obox(cv, x0 - 4, 2, x1 + 4, 8, STEELB, 2.6)
    cv.hline(x0, x1, 6, [tuple(round(c * (0.35 + 0.65 * tube)) for c in (214, 226, 200))], 0, lit=0)
    for i in range(5):
        cv.flat(x0 + 8 + int(hr(i, 9) * 64), 6, (60, 60, 50))           # mosques mortes
    if tube > 0.5:
        cv.glow(TUBE[0], 8, 30, (220, 232, 200), 0.22 * tube)


def floor(cv):
    """Ciment amb taques, paperets triturats escampats i un desguàs."""
    for y in range(FLOOR_Y + 1, H):
        dep = (y - FLOOR_Y) / (H - FLOOR_Y)
        for x in range(W):
            u = (x - W / 2) / (1 + dep * 0.6) + W / 2
            n = (hr(x // 3, y // 2, 5) - 0.5) * 0.5 + (hr(int(u) // 40, (y - FLOOR_Y) // 10, 6) - 0.5) * 0.5
            cv.put(x, y, CONCB, 3.6 + n)
    for cx, cy, rx, ry in ((200, 172, 22, 4), (380, 190, 30, 5), (60, 196, 16, 3)):
        cv.disc(cx, cy, rx, ry, CONCB, lambda nx, ny: 2.4 + (nx * nx + ny * ny) * 0.8)
    # confeti de paper triturat
    for i in range(70):
        x = 60 + int(hr(i, 31) * 200)
        y = FLOOR_Y + 4 + int(hr(i, 32) ** 1.6 * 40)
        cv.put(x, y, SHEET, 4.0 + hr(i, 33))
        if hr(i, 34) > 0.5:
            cv.put(x + 1, y, SHEET, 3.6)
    # el desguàs
    gx, gy = 200, 184
    cv.disc(gx, gy, 9, 3, SLATE, 0.8)
    for i in range(-6, 7, 3):
        cv.vline(gx + i, gy - 2, gy + 2, STEELB, 3.0)
    # la claror verda de la pantalla, estesa pel terra davant del Llibre Major
    cv.tint(200, 152, 380, 204, (60, 255, 140), lambda x, y: 0.12 * max(0, 1 - abs(x - 288) / 90) * max(0, 1 - (y - 152) / 50))


# ─── Esquerra: la porta, les bosses, el conducte ───────────────────────────

def door(cv):
    """La porta del passadís: xapa grisa, una finestreta amb reixeta i el rètol de NETEJA."""
    x0, y0, x1, y1 = 14, 50, 60, FLOOR_Y
    obox(cv, x0 - 4, y0 - 4, x1 + 4, y1, STEELB, 2.4)
    obox(cv, x0, y0, x1, y1, DOORG, 3.4, top=0.6)
    cv.rect(x0 + 4, y1 - 22, x1 - 4, y1 - 4, DOORG, 2.8)                # la placa de les puntades de peu
    for k in range(3):
        cv.line(x0 + 8 + k * 11, y1 - 18, x0 + 12 + k * 11, y1 - 10, DOORG, 1.8)
    # la finestreta, amb vidre armat: la claror del passadís
    obox(cv, x0 + 12, y0 + 10, x1 - 12, y0 + 34, STEELB, 3.0)
    cv.rect(x0 + 14, y0 + 12, x1 - 14, y0 + 32, [(120, 140, 130), (170, 190, 176), (210, 226, 214)], lambda x, y: 1.2 - (y - y0 - 12) * 0.03, lit=0)
    for yy in range(y0 + 14, y0 + 32, 4):
        cv.hline(x0 + 14, x1 - 14, yy, STEELB, 2.4, lit=0)
    for xx in range(x0 + 16, x1 - 13, 4):
        cv.vline(xx, y0 + 12, y0 + 32, STEELB, 2.4, lit=0)
    obox(cv, x1 - 6, 98, x1 - 2, 108, STEELB, 3.4)                      # la maneta
    cv.rect(x1 - 12, 102, x1 - 2, 104, STEELB, 4.2)
    obox(cv, x0 + 6, y0 + 40, x1 - 6, y0 + 48, YEL, 3.0)
    w = text_width('NETEJA')
    text(cv, 'NETEJA', (x0 + x1) // 2 - w // 2, y0 + 42, [(30, 22, 6)], 0, flat=(30, 22, 6))
    cv.darken(x1 + 5, y0, x1 + 9, y1, 0.4)


def chute(cv):
    """El conducte d'escombraries: una boca d'acer encastada a la paret, amb la comporta abatible i el rètol."""
    x0, y0, x1, y1 = 160, 50, 210, 130
    # el tub que puja per la paret fins al sostre
    cv.rect(172, 19, 198, y0, STEELB, lambda x, y: 2.6 + (1.2 if x == 175 else 0) - (1.2 if x >= 196 else 0))
    for yy in (28, 40):
        cv.rect(170, yy, 200, yy + 2, STEELB, 3.4)
    obox(cv, x0, y0, x1, y1, STEELB, 3.0, top=1.0)
    for (rx, ry) in ((x0 + 3, y0 + 3), (x1 - 3, y0 + 3), (x0 + 3, y1 - 3), (x1 - 3, y1 - 3)):
        cv.flat(rx, ry, (190, 196, 200))
    # la comporta, inclinada (la part de dalt més fosca, la de baix, el tirador)
    hx0, hy0, hx1, hy1 = x0 + 7, y0 + 18, x1 - 7, y1 - 14
    cv.rect(hx0, hy0, hx1, hy1, STEELB, lambda x, y: 2.0 + (y - hy0) / (hy1 - hy0) * 2.2)
    outline(cv, hx0, hy0, hx1, hy1, STEELB)
    cv.rect(hx0, hy0, hx1, hy0 + 1, STEELB, 4.6)                        # la frontissa
    obox(cv, (hx0 + hx1) // 2 - 9, hy1 - 6, (hx0 + hx1) // 2 + 9, hy1 - 3, STEELB, 4.2)
    # rascades i una taca de cafè que regalima
    for i in range(6):
        sx = hx0 + 3 + int(hr(i, 41) * (hx1 - hx0 - 6))
        sy = hy0 + 4 + int(hr(i, 42) * (hy1 - hy0 - 10))
        cv.line(sx, sy, sx + 4, sy + 1, STEELB, 4.4)
    cv.rect(x1 - 14, y1 - 2, x1 - 12, y1 + 8, CARD, 1.6)
    # el rètol
    w = text_width('ESCOMBRARIES')
    cx = (x0 + x1) // 2
    obox(cv, cx - w // 2 - 4, y0 + 4, cx + w - w // 2 + 3, y0 + 13, YEL, 3.2)
    text(cv, 'ESCOMBRARIES', cx - w // 2, y0 + 6, [(30, 22, 6)], 0, flat=(30, 22, 6))
    cv.darken(x1 + 1, y0 + 2, x1 + 4, y1, 0.4)


def bags(cv):
    """Les bosses de paper triturat: negres, panxudes, una d'esventrada amb el confeti a fora."""
    def bag(cx, cy, rx, ry, seed, burst=False):
        cv.disc(cx, cy, rx, ry, BAG, lambda nx, ny: 2.8 - ny * 1.2 - nx * 0.5 + (0.9 if (nx * 3 + ny * 5 + seed) % 1.0 < 0.08 else 0))
        # el nus, a dalt
        cv.poly([(cx - 3, cy - ry + 1), (cx + 3, cy - ry + 1), (cx + 1, cy - ry - 4), (cx - 1, cy - ry - 4)], BAG, 3.0)
        cv.line(cx - 2, cy - ry - 5, cx - 4, cy - ry - 8, BAG, 3.2)
        cv.line(cx + 1, cy - ry - 5, cx + 4, cy - ry - 7, BAG, 3.2)
        for a in range(0, 360, 4):                                     # contorn
            px = round(cx + math.cos(math.radians(a)) * (rx + 0.5))
            py = round(cy + math.sin(math.radians(a)) * (ry + 0.5))
            cv.flat(px, py, BAG[0])
        # els reflexos del plàstic
        for i in range(4):
            hx = cx - rx // 2 + int(hr(seed, i, 1) * rx)
            hy = cy - ry // 2 + int(hr(seed, i, 2) * ry // 2)
            cv.line(hx, hy, hx + 2, hy + 3, BAG, 5.0)
        if burst:
            ox, oy = cx + rx // 3, cy + ry // 4                        # l'esquinç, i les tires de paper que en surten
            cv.disc(ox, oy, 4, 2.4, BAG, 0.4)
            for i in range(26):
                a = hr(seed, i, 7) * math.pi - math.pi * 0.1
                ln = 2 + int(hr(seed, i, 8) * 9)
                x, y = ox + int((hr(seed, i, 9) - 0.5) * 6), oy
                for k in range(ln):
                    cv.put(x + round(math.cos(a) * k), y + round(math.sin(a) * k * 0.6) + k // 3, SHEET, 3.6 + hr(i, k) * 1.4)
    bag(84, 144, 14, 11, 1)
    bag(138, 146, 13, 10, 3)
    bag(110, 140, 17, 14, 2, burst=True)
    bag(96, 125, 11, 9, 4)
    bag(124, 124, 10, 9, 5)
    # el confeti escampat de la bossa esventrada
    for i in range(40):
        x = 112 + int((hr(i, 51) - 0.3) * 40)
        y = 150 + int(hr(i, 52) * 7)
        cv.put(x, y, SHEET, 4.2 + hr(i, 53))
    cv.darken(68, 152, 156, 157, 0.5)


# ─── El Llibre Major ───────────────────────────────────────────────────────

def ledger(cv):
    """El Llibre Major: un mainframe gris de 1984. La peça protagonista de la sala."""
    x0, y0, x1, y1 = 236, 36, 340, FLOOR_Y
    # l'ombra a terra i a la paret
    cv.darken(x1 + 1, y0 + 4, x1 + 7, y1, 0.45)
    cv.darken(x0 - 2, y1 + 1, x1 + 8, y1 + 4, 0.55)
    # el moble: un armari gris, amb el sòcol negre i els laterals més foscos
    obox(cv, x0, y0, x1, y1, MAIN, 5.0, top=1.2)
    cv.rect(x0 + 1, y0 + 13, x1 - 1, y0 + 14, [(20, 30, 70), (40, 60, 130), (70, 100, 180)], 1.4)
    cv.rect(x0 + 1, y0 + 1, x0 + 4, y1 - 1, MAIN, 3.0)
    cv.rect(x1 - 4, y0 + 1, x1 - 1, y1 - 1, MAIN, 2.6)
    cv.rect(x0 + 1, y1 - 5, x1 - 1, y1 - 1, MAIN, 1.2)
    # la placa de dalt: LLIBRE MAJOR · 1984, en llautó
    obox(cv, x0 + 8, y0 + 3, x1 - 8, y0 + 11, BRASS, 4.4)
    s = 'LLIBRE MAJOR · 1984'
    text(cv, s, (x0 + x1) // 2 - text_width(s) // 2, y0 + 5, [(40, 26, 8)], 0, flat=(40, 26, 8))
    for rx in (x0 + 10, x1 - 10):
        cv.flat(rx, y0 + 7, BRASS[5])
    # la pantalla de fòsfor verd, amb el bisell beix
    sx0, sy0, sx1, sy1 = SCREEN
    obox(cv, sx0 - 6, sy0 - 5, sx1 + 6, sy1 + 5, BEIGE, 4.0, top=1.0)
    cv.rect(sx0 - 2, sy0 - 2, sx1 + 2, sy1 + 2, BEIGE, 2.0)
    screen(cv)
    # els botons de la pantalla (lluminositat, contrast) i la reixeta de l'altaveu
    for i in range(2):
        cv.disc(sx1 + 2 - i * 7, sy1 + 3, 1.4, 1.4, MAIN, 2.0)
    for i in range(5):
        cv.hline(sx0, sx0 + 14, sy1 + 2 + (i % 2), BEIGE, 2.4)
    # la filera de llums d'estat
    leds(cv, frame=0)
    # el teclat que pesa com una nevera, sobre una lleixa que surt del moble
    ky0 = 106
    cv.poly([(x0 - 2, ky0 + 4), (x1 + 2, ky0 + 4), (x1 - 2, ky0 - 2), (x0 + 2, ky0 - 2)], BEIGE, lambda x, y: 3.2 + (y - ky0 + 2) * 0.1)
    outline_poly(cv, [(x0 - 2, ky0 + 4), (x1 + 2, ky0 + 4), (x1 - 2, ky0 - 2), (x0 + 2, ky0 - 2)], BEIGE)
    cv.rect(x0 - 2, ky0 + 5, x1 + 2, ky0 + 9, BEIGE, 2.2)
    outline(cv, x0 - 2, ky0 + 5, x1 + 2, ky0 + 9, BEIGE)
    for row in range(3):                                               # les tecles, tres files en perspectiva
        yy = ky0 - 1 + row * 2
        for i in range(22):
            kx = x0 + 6 + i * 4 + row
            if kx + 2 > x1 - 6:
                break
            special = (row == 2 and 6 <= i <= 13)
            cv.hline(kx, kx + (2 if not special else 3), yy, BEIGE if not special else MAIN, 5.0 if not special else 4.0)
    cv.rect(x0 + 36, ky0 + 3, x0 + 66, ky0 + 3, BEIGE, 5.2)            # la barra d'espai
    cv.rect(x1 - 16, ky0 - 1, x1 - 8, ky0 + 3, [(120, 30, 26), (180, 50, 40), (230, 90, 70)], 1.4)   # la tecla vermella (EXECUTAR)
    # sota la lleixa: el panell de serveis, amb el pany de llautó per a la clau grossa
    px0, py0, px1, py1 = x0 + 10, ky0 + 14, x1 - 10, y1 - 9
    obox(cv, px0, py0, px1, py1, MAIN, 3.6, top=0.4)
    lock(cv, (x0 + x1) // 2, 129)
    # reixetes de ventilació a banda i banda del pany
    for side in (px1 - 26,):
        for k in range(6):
            cv.hline(side, side + 20, py0 + 5 + k * 3, MAIN, 1.8)
            cv.hline(side, side + 20, py0 + 6 + k * 3, MAIN, 4.6)
    # les cintes de la placa de característiques i un adhesiu groc vell de «NO DESENDOLLAR»
    sx, sy = px0 + 5, py0 + 4                                          # l'adhesiu vell, sobre la reixeta
    obox(cv, sx, sy, sx + 24, sy + 13, YEL, 2.6)
    text(cv, 'NO', sx + 12 - text_width('NO') // 2, sy + 2, [(40, 26, 6)], 0, flat=(40, 26, 6))
    text(cv, 'TOCAR', sx + 12 - text_width('TOCAR') // 2, sy + 8, [(40, 26, 6)], 0, flat=(40, 26, 6))
    # el cable gruixut que surt de darrere i va a la paret, i un altre al terra
    cable(cv, [(x0 + 4, y1 - 3), (x0 - 8, y1 + 2), (x0 - 20, y1 - 1), (x0 - 24, 118)], SLATE, 1.6, thick=2)
    # la pols damunt del moble
    for i in range(40):
        cv.put(x0 + 2 + int(hr(i, 61) * (x1 - x0 - 4)), y0 + 1 + int(hr(i, 62) * 2), DUST, 3.6)
    # el verd de la pantalla que tenyeix el frontal del moble
    cv.tint(x0, y0, x1, y1, (80, 255, 150), lambda x, y: 0.10 * green_cast(x, y))


def screen(cv, cursor=True, frame=0):
    """La pantalla: fòsfor verd amb línies d'escaneig; el menú del sistema i el cursor."""
    sx0, sy0, sx1, sy1 = SCREEN
    for y in range(sy0, sy1 + 1):
        for x in range(sx0, sx1 + 1):
            nx = (x - (sx0 + sx1) / 2) / ((sx1 - sx0) / 2)
            ny = (y - (sy0 + sy1) / 2) / ((sy1 - sy0) / 2)
            vig = (nx * nx + ny * ny) * 0.9
            cv.put(x, y, SCREENB, 1.6 - vig - (0.4 if y % 2 else 0), lit=0)
    ink = (150, 255, 170)
    lines = ['LLIBRE MAJOR', 'COMPTES:', '8.104.229.551', 'EN ESPERA', '>']
    for i, s in enumerate(lines):
        text(cv, s, sx0 + 3, sy0 + 3 + i * 7, [ink], 0, lit=0, flat=ink if i in (0, 3, 4) else (90, 210, 120))
    cv.hline(sx0 + 3, sx0 + 3 + text_width('LLIBRE MAJOR'), sy0 + 9, [ink], 0, lit=0)
    if cursor:
        cx, cy = CURSOR
        cv.rect(cx, cy, cx + 2, cy + 4, [ink], 0, lit=0)
    cv.glow((sx0 + sx1) // 2, (sy0 + sy1) // 2, 46, (80, 255, 140), 0.18)
    # el reflex corbat del vidre
    cv.tint(sx0 + 2, sy0 + 1, sx0 + 22, sy0 + 6, (220, 255, 230), 0.18)


CURSOR = (SCREEN[0] + 3 + 2 + 2, SCREEN[1] + 3 + 4 * 7)
LED_X = list(range(250, 330, 6))
LED_COLS = [REDL, AMBER, GREENL]


def leds(cv, frame=0):
    """La filera de llums d'estat, sota la pantalla: la majoria verds, algun ambre, un vermell que no vol dir res."""
    y = 98
    cv.rect(LED_X[0] - 4, y - 3, LED_X[-1] + 4, y + 3, MAIN, 1.6)
    outline(cv, LED_X[0] - 4, y - 3, LED_X[-1] + 4, y + 3, MAIN)
    for i, x in enumerate(LED_X):
        kind = 2 if hr(i, 70) < 0.7 else (1 if hr(i, 71) < 0.7 else 0)
        on = hr(i, frame, 72) > (0.25 if kind == 2 else 0.5)
        ramp = LED_COLS[kind]
        cv.rect(x, y - 1, x + 2, y, ramp, 2.6 if on else 0.6, lit=0)
        if on:
            cv.flat(x, y - 1, ramp[3])


def lock(cv, cx, cy):
    """El pany: un escut de llautó gros, rodó, amb el forat d'una clau antiga (de les grosses)."""
    cv.disc(cx, cy, 8, 8, BRASS, lambda nx, ny: 4.0 - nx * 0.8 - ny * 1.2)
    cv.ring(cx, cy, 8, BRASS, 1.4, step=3)
    cv.disc(cx, cy, 6, 6, BRASS, lambda nx, ny: 3.0 + nx * 0.6 + ny * 0.6)
    cv.disc(cx, cy - 2, 1.8, 1.8, [(6, 4, 2)], 0, lit=0)
    cv.poly([(cx - 1, cy - 1), (cx + 1, cy - 1), (cx + 2, cy + 4), (cx - 2, cy + 4)], [(6, 4, 2)], 0, lit=0)
    for (rx, ry) in ((cx - 6, cy - 6), (cx + 6, cy - 6), (cx - 6, cy + 6), (cx + 6, cy + 6)):
        cv.flat(rx, ry, BRASS[5])
    cv.glow(cx - 2, cy - 3, 5, (255, 240, 180), 0.25)


# ─── Dreta: l'estació del tub i el panell de NETA-3 ────────────────────────

def neta_panel(cv):
    """El panell de control de NETA-3 a la paret: una caixa gris amb una pantalleta, botons i l'horari enganxat."""
    x0, y0, x1, y1 = 390, 70, 424, 110
    obox(cv, x0, y0, x1, y1, MAIN, 3.8, top=1.0)
    obox(cv, x0 + 2, y0 + 2, x1 - 2, y0 + 9, YEL, 3.0)
    w = text_width('NETA-3')
    text(cv, 'NETA-3', (x0 + x1) // 2 - w // 2, y0 + 3, [(30, 22, 6)], 0, flat=(30, 22, 6))
    # la pantalleta: «HORARI: SEMPRE»
    cv.rect(x0 + 3, y0 + 12, x1 - 3, y0 + 22, [(10, 30, 40), (30, 90, 110), (90, 200, 220)], 0.8, lit=0)
    w = text_width('SEMPRE')
    text(cv, 'SEMPRE', (x0 + x1) // 2 - w // 2, y0 + 15, [(120, 230, 240)], 0, lit=0, flat=(120, 230, 240))
    # el teclat petit
    for i in range(6):
        kx = x0 + 7 + (i % 3) * 7
        ky = y0 + 26 + (i // 3) * 6
        obox(cv, kx, ky, kx + 4, ky + 3, MAIN, 5.0)
    cv.flat(x1 - 4, y1 - 4, GREENL[3])
    cv.glow(x1 - 4, y1 - 4, 4, (120, 255, 160), 0.4)
    # el cable fins a la base de càrrega, a terra
    cable(cv, [(x1 - 6, y1), (x1 - 2, 128), (x1 + 14, 140), (438, 152)], SLATE, 1.6)


def dock(cv):
    """La base de càrrega de NETA-3: una placa amb franges grogues i negres i dos contactes de coure."""
    x0, x1, y = 424, 470, 156
    cv.poly([(x0, y + 6), (x1, y + 6), (x1 - 4, y - 2), (x0 + 4, y - 2)], STRIPE, lambda x, yy: 2.6 if ((x + yy) // 4) % 2 else 0.4)
    outline_poly(cv, [(x0, y + 6), (x1, y + 6), (x1 - 4, y - 2), (x0 + 4, y - 2)], STRIPE)
    cv.rect(x0 + 2, y + 7, x1 - 2, y + 8, STRIPE, 0.6)
    obox(cv, 440, 140, 454, y - 2, MAIN, 3.2, top=0.8)                  # el pal dels contactes
    for cx in (444, 450):
        cv.rect(cx, 146, cx + 1, 150, [(80, 40, 20), (190, 110, 50), (240, 170, 100)], 1.6)
    cv.flat(447, 143, GREENL[2])
    cv.darken(x0, y + 9, x1 + 2, y + 11, 0.5)


def boxes(cv):
    """Caixes d'arxiu velles apilades a la dreta del tot («ARXIU 1987-1991»), amb pols."""
    for i, (bx0, by0) in enumerate(((432, 108), (444, 86), (430, 64))):
        obox(cv, bx0, by0, bx0 + 40, by0 + 22, CARD, 3.0 - i * 0.2)
        obox(cv, bx0 + 12, by0 + 7, bx0 + 28, by0 + 15, SHEET, 4.2)
        cv.rect(bx0 + 14, by0 + 10, bx0 + 26, by0 + 10, SLATE, 1.6)
        cv.rect(bx0 + 14, by0 + 12, bx0 + 22, by0 + 12, SLATE, 1.6)
        for k in range(8):
            cv.put(bx0 + 2 + int(hr(i, k, 81) * 36), by0 + 1, DUST, 3.8)
    cv.darken(430, 131, 474, 133, 0.5)


def wall_bits(cv):
    """El rètol de damunt les bosses (amb la fletxa avall) i un rellotge de paret que s'ha aturat a les deu i deu."""
    w = text_width('CONFIDENCIAL')
    x0, y0 = 110 - w // 2 - 4, 72
    obox(cv, x0, y0, x0 + w + 7, y0 + 10, [(40, 6, 8), (90, 14, 16), (150, 26, 26), (196, 44, 38)], 2.8)
    text(cv, 'CONFIDENCIAL', x0 + 4, y0 + 3, [(250, 240, 230)], 0, flat=(250, 240, 230))
    for k in range(5):                                                 # la fletxa
        cv.hline(110 - k, 110 + k, y0 + 20 - k, [(150, 26, 26), (196, 44, 38)], 1.0)
    cv.rect(109, y0 + 12, 111, y0 + 15, [(150, 26, 26), (196, 44, 38)], 1.0)
    # el rellotge
    cx, cy = 110, 40
    cv.disc(cx, cy, 9, 9, STEELB, 2.6)
    cv.disc(cx, cy, 7.5, 7.5, SHEET, lambda nx, ny: 4.4 - ny * 0.6)
    for a in range(0, 360, 30):
        cv.flat(round(cx + math.cos(math.radians(a)) * 6), round(cy + math.sin(math.radians(a)) * 6), SLATE[1])
    cv.line(cx, cy, cx - 3, cy - 4, SLATE, 0.6)                         # les deu
    cv.line(cx, cy, cx + 4, cy - 3, SLATE, 0.6)                         # i deu
    cv.darken(cx + 8, cy - 6, cx + 10, cy + 9, 0.4)


def bg(cv, tube=1.0):
    wall(cv)
    ceiling(cv, tube)
    floor(cv)
    door(cv)
    wall_bits(cv)
    chute(cv)
    bags(cv)
    tub_station(cv, 352, 60, 372, 110, vell=True)
    boxes(cv)
    neta_panel(cv)
    dock(cv)
    ledger(cv)
    # la claror verda de la pantalla també toca les parets veïnes
    cv.tint(200, 20, 380, 150, (60, 255, 140), lambda x, y: 0.06 * green_cast(x, y))


PROPS = {}


# ─── Els llums del Llibre Major i el cursor ────────────────────────────────

def _frames():
    base = Canvas(light=LIGHT)
    bg(base)
    frames = []
    for i in range(12):
        cv = Canvas(light=LIGHT, img=base.img.copy())
        leds(cv, frame=i + 1)
        if i % 4 >= 2:                                                  # el cursor parpelleja
            cx, cy = CURSOR
            cv.rect(cx, cy, cx + 2, cy + 4, SCREENB, 1.4, lit=0)
        frames.append(_diff(cv.img, base.img))
    return frames


ANIMS = {'llibre': {'frames': _frames, 'frameDuration': 260}}


# ─── Animacions: el fluorescent que fa figa i la gota de la canonada ───────

def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv.img


def _frames_fluorescent():
    """El fluorescent brut aguanta una estona i de cop tartamudeja: s'apaga, torna, mig s'apaga i torna."""
    base = _base()
    empty = _diff(base, base)
    dims = {}
    frames = []
    for t in (1,) * 14 + (0.0, 1, 0.0, 0.6, 1, 0.6):
        if t == 1:
            frames.append(empty)
            continue
        if t not in dims:
            cv = Canvas(light=LIGHT)
            bg(cv, tube=t)
            f = _diff(cv.img, base)
            # sense el fluorescent la sala s'enfosqueix una mica al voltant (només el sostre i el capdamunt)
            c = Canvas(light=LIGHT, img=base.copy())
            c.img.alpha_composite(f)
            k = 0.3 if t == 0 else 0.15
            for y in range(9, 60):
                for x in range(TUBE[0] - 100, TUBE[0] + 101):
                    d = math.hypot((x - TUBE[0]) / 100, (y - 6) / 54)
                    if d < 1:
                        o = c.P[x, y]
                        m = 1 - k * (1 - d) ** 1.5
                        c.P[x, y] = (round(o[0] * m), round(o[1] * m), round(o[2] * m), o[3])
            dims[t] = _diff(c.img, base)
        frames.append(dims[t])
    return frames


DRIP_X, DRIP_Y = 217, 25                 # sota la canonada vella; cau a la taca d'humitat del terra
DRIP_FLOOR = 173
DROP = [(70, 84, 82), (150, 170, 160), (200, 220, 206)]


def _frames_gota():
    """Una gota es forma sota la canonada vella, s'allarga, cau i esquitxa la taca d'humitat."""
    base = _base()
    empty = _diff(base, base)
    frames = [empty] * 6
    # la gota que es forma: (alçada en píxels)
    for h in (1, 1, 2, 2, 3):
        cv = Canvas(light=LIGHT, img=base.copy())
        cv.vline(DRIP_X, DRIP_Y, DRIP_Y + h - 1, DROP, 1)
        cv.flat(DRIP_X, DRIP_Y + h - 1, DROP[2])
        frames.append(_diff(cv.img, base))
    # la caiguda, cada cop més ràpida (y del cap de la gota i la llargada de l'estela)
    for y, ln in ((30, 2), (40, 3), (58, 4), (84, 5), (116, 6), (150, 6)):
        cv = Canvas(light=LIGHT, img=base.copy())
        cv.vline(DRIP_X, y - ln + 1, y - 1, DROP, 0.6)
        cv.flat(DRIP_X, y, DROP[2])
        frames.append(_diff(cv.img, base))
    # l'esquitx: dues gotetes que salten i una rodoneta a la taca
    for k in range(3):
        cv = Canvas(light=LIGHT, img=base.copy())
        if k < 2:
            cv.flat(DRIP_X - 1 - k, DRIP_FLOOR - 1 - (1 - k), DROP[1])
            cv.flat(DRIP_X + 1 + k, DRIP_FLOOR - 1 - (1 - k), DROP[1])
        r = 2 + k * 2                                                   # la rodoneta, aplanada: és a terra
        for a in range(0, 360, 10):
            cv.put(round(DRIP_X + math.cos(math.radians(a)) * r), round(DRIP_FLOOR + math.sin(math.radians(a)) * r * 0.35),
                   DROP, 1.0 - k * 0.4)
        frames.append(_diff(cv.img, base))
    frames += [empty] * 2
    return frames


ANIMS['fluorescent'] = {'frames': _frames_fluorescent, 'frameDuration': 110}
ANIMS['gota'] = {'frames': _frames_gota, 'frameDuration': 100}
