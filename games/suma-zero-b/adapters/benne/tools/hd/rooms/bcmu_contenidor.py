"""
El carrer de darrere del BCMU (final de l'Acte 3, la Vet). Art definitiu:
  - la façana de darrere de l'edifici de 1958, sense maquillatge: sòcol de pedra encoixinada, formigó amb
    juntes, finestretes amb reixes, dues baixants, la porta de servei d'acer blau marí amb el seu llum, la placa
    discreta «BCMU» de llautó i una càmera de vigilància que mira la porta;
  - el conducte de les escombraries, de xapa, que baixa per la paret des del tercer pis i acaba just damunt
    del contenidor, amb la boca de cortina de goma;
  - el contenidor verd de paper, amb la tapa una mica oberta i paper triturat que en treu el nas (el que el banc
    vol oblidar), damunt de rodes;
  - a la dreta, la boca del carreró: el carrer de Ginebra, net i assolellat; la catenària i les vies del
    tramvia, i a l'altra banda un altre banc (pedra, columnes i lletres d'or) amb un aparador de rellotges;
  - migdia: el sol toca la part alta de la paret i el carrer; el carreró és a l'ombra.
"""
import math

from hd.pix import Canvas, Light, W, H, hr
from hd.rooms.comu import obox, outline, text, text_width, _diff, PLASTIC, SHEET, RED
from hd.rooms.pis_cuina import outline_poly
from hd.rooms.bcmu import NAVYB, BRASS, logo

FLOOR_Y = 150
STREET_X = 394                 # on acaba la paret del banc i comença la boca del carreró

STONEW = [(22, 20, 22), (38, 36, 36), (56, 52, 50), (78, 74, 68), (102, 96, 88), (128, 122, 110), (156, 148, 134), (184, 176, 160), (210, 204, 188)]
CONC = [(20, 22, 26), (34, 36, 40), (50, 52, 56), (68, 70, 72), (88, 90, 90), (110, 110, 108), (134, 132, 128), (160, 158, 150), (188, 186, 176)]
ASPH = [(14, 14, 18), (24, 24, 28), (36, 36, 40), (50, 50, 54), (66, 66, 68), (84, 84, 84), (104, 104, 102), (128, 126, 122)]
ZINC = [(18, 22, 26), (32, 38, 44), (50, 58, 66), (72, 82, 90), (98, 108, 116), (128, 138, 144), (162, 170, 174), (200, 206, 208), (232, 236, 236)]
BIN = [(6, 20, 12), (10, 34, 18), (16, 52, 26), (24, 72, 36), (34, 96, 46), (48, 122, 58), (68, 148, 74), (100, 176, 98)]
SHRED = [(120, 116, 104), (170, 166, 150), (210, 206, 190), (236, 234, 222), (250, 250, 244)]
SKYD = [(110, 150, 190), (136, 172, 206), (160, 192, 220), (186, 210, 230), (210, 226, 238)]
FACADE = [(70, 64, 56), (100, 92, 80), (130, 122, 106), (160, 150, 132), (188, 178, 158), (214, 206, 186), (234, 228, 210)]
GOLDS = [(80, 56, 14), (150, 110, 30), (210, 166, 60), (244, 210, 110), (255, 240, 180)]
WIN = [(16, 22, 30), (30, 42, 54), (50, 68, 84), (80, 104, 122), (130, 156, 172), (190, 210, 222)]
SHOP = [(60, 40, 20), (130, 92, 50), (200, 160, 100), (240, 214, 160), (255, 244, 210)]
TRAM = [(60, 10, 14), (110, 20, 24), (170, 36, 36), (210, 64, 52), (236, 110, 90)]
CARD = [(40, 26, 14), (74, 50, 28), (110, 80, 46), (146, 110, 68), (180, 142, 94)]
BAG = [(8, 10, 22), (16, 22, 46), (28, 38, 76), (44, 60, 110), (70, 90, 146)]

LIGHT = Light(ambient=-0.1, vignette=(56, 1), floor_fade=(194, 30))
LIGHT.point(450, 120, r=260, k=1.6, squash=0.9, power=1.3)             # la claror que entra del carrer
LIGHT.point(86, 82, r=60, k=0.8, squash=1.0, power=1.8)                # el llum de la porta de servei
LIGHT.add(lambda x, y: 1.3 * max(0.0, 1 - y / 46) ** 1.5)              # el sol a dalt de la paret

CHUTE = (282, 302)             # el conducte: x de les dues cares
BIN_R = (240, 104, 344, 162)   # el contenidor (room_designs: contenidor)


# ─── La paret del banc ─────────────────────────────────────────────────────

def wall(cv):
    """Formigó amb juntes horitzontals (pis de dalt) i sòcol de pedra encoixinada (planta baixa)."""
    for y in range(0, FLOOR_Y):
        for x in range(STREET_X):
            n = (hr(x // 2, y // 2, 21) - 0.5) * 0.35
            if y < 96:
                joint = y % 24 == 23 or (x % 120 == 0)
                stain = max(0.0, 1 - abs((x % 120) - 60) / 60) * 0.25 * (y % 24) / 24     # regalims
                cv.put(x, y, CONC, (2.6 if joint else 4.2 + n - stain))
            else:
                row = (y - 96) // 14
                off = 22 if row % 2 else 0
                bx = (x + off) % 44
                by = (y - 96) % 14
                bev = 0.9 if (by == 0 or bx == 0) else (-0.9 if (by == 13 or bx == 43) else 0)
                nb = (hr((x + off) // 44, row, 5) - 0.5) * 0.5
                cv.put(x, y, STONEW, 4.0 + n + nb + bev)
    # la cornisa entre la planta baixa i el primer pis
    cv.rect(0, 92, STREET_X - 1, 95, STONEW, lambda x, y: 5.0 if y == 92 else (3.6 if y < 95 else 2.2))
    cv.darken(0, 96, STREET_X - 1, 98, 0.45)
    # la cantonada del banc, a la boca del carreró
    cv.rect(STREET_X - 6, 0, STREET_X - 1, FLOOR_Y - 1, STONEW, lambda x, y: 4.6 + (0.9 if x == STREET_X - 6 else 0) + (hr(x, y // 3) - 0.5) * 0.3)
    cv.vline(STREET_X - 1, 0, FLOOR_Y - 1, STONEW, 2.0)
    # la vorera de pedra al peu de la paret
    cv.rect(0, FLOOR_Y - 2, STREET_X - 1, FLOOR_Y, STONEW, lambda x, y: 2.2 if y == FLOOR_Y else 3.4)


def barred_window(cv, x0, y0, w, h):
    """Una finestreta amb vidre armat i reixa de ferro (pinta de 1958)."""
    obox(cv, x0 - 3, y0 - 3, x0 + w + 3, y0 + h + 3, STONEW, 4.4)
    for y in range(y0, y0 + h + 1):
        for x in range(x0, x0 + w + 1):
            ref = 1.0 if (x - x0) - (y - y0) * 0.6 in range(2, 5) else 0
            cv.put(x, y, WIN, 1.6 + (y - y0) / h * 0.6 + ref + ((x + y) % 4 == 0) * 0.3)
    for bx in range(x0 + 2, x0 + w, 4):                                 # els barrots
        cv.vline(bx, y0 - 1, y0 + h + 1, ZINC, 2.4)
        cv.flat(bx, y0 - 1, ZINC[1])
    cv.hline(x0, x0 + w, y0 + h // 2, ZINC, 2.2)
    cv.rect(x0 - 4, y0 + h + 3, x0 + w + 4, y0 + h + 4, STONEW, 5.2)        # l'ampit
    cv.darken(x0 - 4, y0 + h + 5, x0 + w + 4, y0 + h + 7, 0.4)


def windows(cv):
    for wx in (26, 120, 196, 338):
        barred_window(cv, wx, 32, 24, 30)
    # les finestretes del soterrani, arran de terra
    for wx in (150, 206, 358):
        barred_window(cv, wx, 128, 18, 10)


def drainpipe(cv, x, top=0):
    """Una baixant de zinc amb abraçadores i el peu de ferro colat."""
    cv.rect(x, top, x + 4, FLOOR_Y - 6, ZINC, lambda xx, y: 3.4 + (1.6 if xx == x + 1 else 0) - (1.2 if xx == x + 4 else 0))
    for y in range(top + 10, FLOOR_Y - 10, 26):
        cv.rect(x - 1, y, x + 5, y + 1, ZINC, 2.4)
    cv.rect(x - 1, FLOOR_Y - 8, x + 6, FLOOR_Y - 1, ZINC, lambda xx, y: 2.4 + (0.8 if xx == x else 0))
    cv.darken(x + 5, top, x + 7, FLOOR_Y - 2, 0.35)


def service_door(cv):
    """La porta de servei: acer pintat de blau marí, barra antipànic per dins, llum de reixeta i graó."""
    x0, y0, x1, y1 = 66, 100, 102, FLOOR_Y - 2
    obox(cv, x0 - 4, y0 - 4, x1 + 4, y1, CONC, 3.6)                     # el marc de formigó
    obox(cv, x0, y0, x1, y1, NAVYB, 3.0, top=0.6, side=-0.6)
    for py in (y0 + 6, y0 + 28):                                         # dos plafons premsats
        outline(cv, x0 + 4, py, x1 - 4, py + 16, NAVYB)
        cv.hline(x0 + 5, x1 - 5, py + 1, NAVYB, 4.0)
    cv.rect(x1 - 7, y0 + 24, x1 - 4, y0 + 26, ZINC, 5.0)               # la maneta
    cv.rect(x1 - 6, y0 + 27, x1 - 5, y0 + 30, ZINC, 3.0)               # el pany
    cv.vline(x0 + 1, y0 + 6, y0 + 14, ZINC, 3.0)                        # frontisses
    cv.vline(x0 + 1, y1 - 14, y1 - 6, ZINC, 3.0)
    for i in range(6):                                                   # rascades a baix
        sx = x0 + 3 + int(hr(i, 2) * 28)
        cv.hline(sx, sx + 4, y1 - 3 - int(hr(i, 3) * 6), NAVYB, 4.6)
    text(cv, 'SORTIDA', x0 + (x1 - x0 - text_width('SORTIDA')) // 2 + 1, y0 + 23, [(200, 190, 160)], 0, flat=(196, 186, 150))
    # el graó
    cv.rect(x0 - 8, y1 + 1, x1 + 8, FLOOR_Y + 3, STONEW, lambda x, y: 5.0 if y == y1 + 1 else 3.2)
    cv.darken(x0 - 8, FLOOR_Y + 4, x1 + 8, FLOOR_Y + 5, 0.5)
    # el llum de reixeta, damunt
    obox(cv, 79, 84, 89, 92, ZINC, 3.0)
    cv.rect(81, 86, 87, 90, [(255, 236, 190)], 0, lit=0)
    for xx in (82, 84, 86):
        cv.vline(xx, 86, 90, ZINC, 2.0)
    cv.glow(84, 90, 16, (255, 230, 180), 0.25)


def plate(cv):
    """La placa discreta de llautó: el logotip i «BCMU», res més."""
    x0, y0, x1, y1 = 112, 104, 144, 118
    obox(cv, x0, y0, x1, y1, BRASS, 3.6)
    cv.hline(x0 + 1, x1 - 1, y0 + 1, BRASS, 5.4)
    logo(cv, x0 + 6, y0 + 7, k=0.7, lvl=1.8)
    text(cv, 'BCMU', x0 + 13, y0 + 5, NAVYB, 1.6)
    for sx, sy in ((x0 + 1, y0 + 1), (x1 - 1, y0 + 1), (x0 + 1, y1 - 1), (x1 - 1, y1 - 1)):
        cv.flat(sx, sy, BRASS[2])
    cv.darken(x0 + 1, y1 + 1, x1 + 1, y1 + 2, 0.4)
    # un timbre amb intèrfon, al costat
    obox(cv, x0 + 6, y1 + 6, x0 + 16, y1 + 20, ZINC, 3.4)
    for k in range(3):
        cv.hline(x0 + 8, x0 + 14, y1 + 9 + k * 2, ZINC, 1.6)
    cv.disc(x0 + 11, y1 + 17, 1.4, 1.4, [(220, 200, 140)], 0, lit=0)


def camera(cv, led=True):
    """La càmera de vigilància, en un braç, apuntant cap a la porta de servei (llum vermell que parpelleja)."""
    bx, by = 262, 20
    obox(cv, bx, by - 4, bx + 6, by + 6, ZINC, 3.4)                     # la placa de la paret
    cv.line(bx, by + 1, bx - 8, by + 5, ZINC, 3.6)                       # el braç
    cv.line(bx, by + 2, bx - 8, by + 6, ZINC, 2.0)
    body = [(bx - 30, by + 12), (bx - 6, by + 2), (bx - 3, by + 8), (bx - 26, by + 18)]
    cv.poly(body, SHEET, lambda x, y: 4.6 - (y - by) * 0.12)
    outline_poly(cv, body, SHEET)
    cv.poly([(bx - 32, by + 10), (bx - 6, by), (bx - 5, by + 2), (bx - 30, by + 12)], SHEET, 5.2)   # la visera
    cv.disc(bx - 28, by + 15, 2.2, 2.2, PLASTIC, 1.0)                    # l'objectiu
    cv.flat(bx - 29, by + 14, (160, 200, 230))
    if led:
        cv.flat(bx - 10, by + 9, (240, 40, 36))
        cv.glow(bx - 10, by + 9, 4, (255, 50, 40), 0.5)
    else:
        cv.flat(bx - 10, by + 9, (90, 24, 24))
    cv.darken(bx - 28, by + 19, bx - 4, by + 23, 0.3)


def chute(cv, wind=0.0):
    """El conducte de les escombraries: xapa galvanitzada a trams, amb brides i abraçadores a la paret,
    que acaba amb una boca inclinada i una cortina de tires de goma just damunt del contenidor."""
    x0, x1 = CHUTE
    end = 88
    for y in range(0, end):
        for x in range(x0, x1 + 1):
            flange = y % 22 in (0, 1)
            lvl = 4.0 + (1.8 if x == x0 + 2 else 0) + (0.6 if x < x0 + 6 else 0) - (1.4 if x > x1 - 4 else 0)
            lvl += (hr(x // 2, y // 5, 13) - 0.5) * 0.4
            cv.put(x, y, ZINC, lvl + (1.2 if flange and y % 22 == 0 else (-0.6 if flange else 0)))
        if y % 22 == 0:                                                  # la brida sobresurt
            cv.rect(x0 - 1, y, x1 + 1, y + 1, ZINC, 4.6)
    for y in range(22, end, 22):                                         # els cargols de les brides
        for bxx in (x0 + 3, (x0 + x1) // 2, x1 - 3):
            cv.flat(bxx, y + 1, ZINC[1])
    for y in (14, 58):                                                   # les abraçadores a la paret
        cv.rect(x0 - 5, y, x0 - 1, y + 3, ZINC, 2.6)
        cv.rect(x1 + 1, y, x1 + 5, y + 3, ZINC, 2.6)
    outline(cv, x0, 0, x1, end - 1, ZINC)
    cv.darken(x1 + 1, 0, x1 + 5, end + 6, 0.4)                          # l'ombra a la paret
    # la boca: s'eixampla i s'inclina cap endavant
    mouth = [(x0 - 1, end), (x1 + 1, end), (x1 + 5, 98), (x0 - 5, 98)]
    cv.poly(mouth, ZINC, lambda x, y: 4.6 - (y - end) * 0.08 - (1.2 if x > x1 else 0))
    outline_poly(cv, mouth, ZINC)
    cv.rect(x0 - 5, 97, x1 + 5, 98, ZINC, 5.6)
    # la cortina de goma (tires negres): el vent en mou la punta
    for k, x in enumerate(range(x0 - 4, x1 + 5, 3)):
        ln = 4 + int(hr(k, 8) * 2)
        sway = math.sin(wind + k * 0.9)
        for j in range(ln + 1):
            dx = round(sway * 1.4 * j / ln)
            cv.rect(x + dx, 99 + j, x + 1 + dx, 99 + j, PLASTIC, 1.6 + (0.6 if k % 2 else 0))
    # una etiqueta groga d'avís, al conducte
    obox(cv, x0 + 4, 64, x1 - 4, 74, [(60, 40, 0), (150, 110, 10), (230, 190, 40), (250, 226, 110)], 2.6)
    cv.poly([(x0 + 10, 72), (x0 + 12, 66), (x0 + 14, 72)], [(30, 20, 0)], 0)
    # un esgarrinxat de sota: no fa gaire que algú ha llençat alguna cosa
    for k in range(3):
        cv.flat(x0 + 3 + k * 6, 103, SHRED[3])


# ─── El contenidor ─────────────────────────────────────────────────────────

def container(cv, wind=0.0):
    """El contenidor verd del paper, amb la tapa mig oberta i paper triturat que en surt."""
    x0, y0, x1, y1 = BIN_R
    lid_y1 = y0 + 9
    body_top, body_bot = lid_y1 + 1, y1 - 9
    # l'ombra al terra i a la paret
    cv.darken(x0 - 6, FLOOR_Y - 30, x0 - 1, FLOOR_Y, 0.35)
    cv.darken(x0 - 4, y1 - 2, x1 + 10, y1 + 4, lambda x, y: 0.75 - abs(y - y1 - 1) * 0.1)
    # el cos: s'estreny una mica cap avall
    def bx(y):
        t = (y - body_top) / (body_bot - body_top)
        return x0 + 2 + round(t * 3), x1 - 2 - round(t * 3)
    for y in range(body_top, body_bot + 1):
        a, b = bx(y)
        for x in range(a, b + 1):
            rib = (x - x0) % 16 == 8
            lvl = 4.2 - (y - body_top) * 0.03 + (0.9 if rib else 0) - (1.2 if x > b - 3 else 0) + (0.8 if x < a + 2 else 0)
            lvl += (hr(x // 3, y // 3, 17) - 0.5) * 0.3
            cv.put(x, y, BIN, lvl)
        cv.flat(a, y, BIN[0])
        cv.flat(b, y, BIN[0])
    cv.hline(bx(body_bot)[0], bx(body_bot)[1], body_bot, BIN, 0.6)
    # el reforç de la vora de dalt
    cv.rect(x0 + 1, body_top, x1 - 1, body_top + 3, BIN, lambda x, y: 5.0 if y == body_top else 3.4)
    outline(cv, x0 + 1, body_top, x1 - 1, body_top + 3, BIN)
    # els agafadors laterals
    for hx in (x0 - 1, x1 - 2):
        obox(cv, hx, body_top + 6, hx + 3, body_top + 10, BIN, 2.8)
    # l'adhesiu: «PAPIER · PAPER» i el símbol del reciclatge
    sx0, sy0, sx1, sy1 = 262, 124, 322, 142
    obox(cv, sx0, sy0, sx1, sy1, SHEET, 4.8)
    cv.rect(sx0 + 1, sy0 + 1, sx1 - 1, sy0 + 3, [(30, 110, 50)], 0)
    for k in range(3):                                                   # tres fletxes en triangle
        a = math.radians(k * 120 - 90)
        cx, cy = sx0 + 10 + round(math.cos(a) * 4), sy0 + 11 + round(math.sin(a) * 4)
        cv.disc(cx, cy, 1.6, 1.6, [(30, 110, 50)], 0)
    cv.ring(sx0 + 10, sy0 + 11, 4, [(30, 110, 50)], 0, step=24)
    text(cv, 'PAPIER', sx0 + 20, sy0 + 6, [(30, 40, 30)], 0, flat=(30, 40, 30))
    text(cv, 'PAPER', sx0 + 20, sy0 + 12, [(30, 110, 50)], 0, flat=(36, 110, 56))
    text(cv, 'GE', x1 - 14, body_top + 7, BIN, 6.4)
    # la tapa, una mica aixecada per davant
    lid = [(x0 - 2, y0 + 3), (x1 + 2, y0 + 3), (x1 + 3, lid_y1), (x0 - 3, lid_y1)]
    cv.poly([(x0, y0), (x1, y0), (x1 + 2, y0 + 3), (x0 - 2, y0 + 3)], BIN, 5.2)
    cv.poly(lid, BIN, lambda x, y: 4.0 - (y - y0) * 0.15 - (1.0 if x > x1 - 2 else 0))
    outline_poly(cv, [(x0, y0), (x1, y0), (x1 + 3, lid_y1), (x0 - 3, lid_y1)], BIN)
    cv.hline(x0 + 1, x1 - 1, y0 + 1, BIN, 6.4)
    # l'escletxa sota la tapa: fosc, i paper triturat que en penja
    cv.hline(x0 - 1, x1 + 1, lid_y1 + 1, BIN, 0.2)
    for k in range(26):
        sx = x0 + 6 + int(hr(k, 31) * (x1 - x0 - 12))
        ln = 2 + int(hr(k, 32) * 7)
        sway = math.sin(wind + hr(k, 35) * 6.28) * (0.6 + hr(k, 36))
        for j in range(ln):
            dx = (j // 3 if hr(k, 33) > 0.5 else -(j // 3)) + round(sway * j / 7)
            cv.put(sx + dx, lid_y1 + 1 + j, SHRED, 2.6 + hr(k, 34) * 1.6)
    # una tira llarga que penja fins a l'adhesiu (i que el vent fa onejar)
    for j in range(14):
        cv.put(300 + round(math.sin(j * 0.6 - wind) * (0.6 + j / 14)), lid_y1 + 1 + j, SHRED, 3.4)
    # les rodes
    for wx in (x0 + 8, x1 - 14):
        obox(cv, wx, body_bot + 1, wx + 6, body_bot + 3, ZINC, 2.6)
        cv.disc(wx + 3, y1 - 3, 3.4, 3.4, PLASTIC, lambda nx, ny: 2.4 - ny)
        cv.flat(wx + 3, y1 - 3, ZINC[5])


def litter(cv):
    """Al costat del contenidor: una caixa de cartró plegada i dues bosses de documents (blau marí, segellades)."""
    obox(cv, 348, 120, 376, 160, CARD, 3.4)
    cv.line(350, 124, 374, 156, CARD, 2.6)
    cv.hline(349, 375, 138, [(200, 180, 120), (230, 214, 160)], 0.6)   # cinta
    text(cv, 'BCMU', 352, 128, CARD, 1.4)
    cv.darken(346, 160, 380, 163, 0.5)
    for bxc, sq in ((228, 1.0), (384, 0.8)):                           # bosses d'escombraries, lligades
        lump = [(bxc - 9 * sq, 162), (bxc - 10 * sq, 154), (bxc - 6 * sq, 147), (bxc - 1, 145), (bxc + 6 * sq, 147),
                (bxc + 10 * sq, 153), (bxc + 9 * sq, 162)]
        cv.poly(lump, BAG, lambda x, y, c=bxc: 3.2 - (y - 145) * 0.06 - (x - c) * 0.1 + (hr(x // 3, y // 2, 7) - 0.5) * 0.6)
        outline_poly(cv, lump, BAG)
        cv.poly([(bxc - 3, 145), (bxc - 1, 139), (bxc + 1, 145)], BAG, 2.6)          # el nus
        cv.poly([(bxc, 144), (bxc + 4, 140), (bxc + 2, 145)], BAG, 3.2)
        cv.line(bxc - 4 * sq, 150, bxc - 2 * sq, 158, BAG, 4.2)                       # el plec que brilla
    cv.darken(216, 162, 240, 165, 0.45)
    cv.darken(374, 162, 394, 165, 0.45)


# ─── La boca del carreró: el carrer de Ginebra ─────────────────────────────

def street(cv):
    """Cel, l'altre banc (pedra, columnes, lletres d'or), l'aparador de rellotges, la catenària i el tramvia."""
    x0, x1 = STREET_X, W - 1
    for y in range(0, 22):
        for x in range(x0, x1 + 1):
            cv.put(x, y, SKYD, 4.4 - y / 12, lit=0)
    # l'altre banc, a l'altra banda del carrer
    for y in range(22, 134):
        for x in range(x0, x1 + 1):
            joint = (y - 22) % 8 == 7
            cv.put(x, y, FACADE, (3.4 if joint else 4.6) + (hr(x // 4, y // 8) - 0.5) * 0.3, lit=0)
    cv.rect(x0, 22, x1, 26, FACADE, lambda x, y: 6.0 if y == 22 else 4.0, lit=0)     # la cornisa
    cv.darken(x0, 27, x1, 28, 0.4)
    for wx in (402, 426, 450):                                           # finestres del pis
        cv.rect(wx, 36, wx + 12, 58, WIN, lambda x, y: 2.2 + (1.4 if x - wx == (y - 36) // 3 else 0), lit=0)
        cv.rect(wx - 2, 59, wx + 14, 60, FACADE, 6.0, lit=0)
        cv.rect(wx - 1, 33, wx + 13, 35, FACADE, 5.4, lit=0)
    # les lletres d'or sobre la planta baixa
    cv.rect(x0, 70, x1, 80, FACADE, 3.2, lit=0)
    s = 'BANQUE PRIVÉE'
    text(cv, s, x0 + (x1 - x0 - text_width(s)) // 2 + 1, 73, GOLDS, 3.2, lit=0)
    # les columnes i l'aparador de rellotges, encès
    for cx in (398, 436, 474):
        cv.rect(cx, 82, cx + 4, 134, FACADE, lambda x, y, cx=cx: 5.0 + (0.8 if x == cx + 1 else 0) - (1.2 if x == cx + 4 else 0), lit=0)
    for sx in (403, 441):
        cv.rect(sx, 86, sx + 32, 128, SHOP, lambda x, y: 1.6 + (y - 86) / 30, lit=0)
        cv.rect(sx, 86, sx + 32, 88, FACADE, 2.0, lit=0)
        for k in range(4):                                               # rellotges en coixinets
            wx, wy = sx + 5 + k * 7, 102 + (k % 2) * 8
            cv.disc(wx, wy, 2.4, 2.4, [(40, 30, 20), (220, 200, 160), (255, 250, 230)], 1.6, lit=0)
            cv.flat(wx, wy, (40, 30, 20))
        cv.rect(sx + 2, 120, sx + 30, 123, [(90, 20, 30), (140, 40, 50)], 0.6, lit=0)  # el vellut
        cv.glow(sx + 16, 106, 18, (255, 230, 170), 0.2)
    # la vorera de l'altra banda, la calçada i les vies
    cv.rect(x0, 134, x1, 137, FACADE, lambda x, y: 5.6 if y == 134 else 4.2, lit=0)
    for y in range(138, FLOOR_Y + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, ASPH, 4.6 + (hr(x // 2, y) - 0.5) * 0.4, lit=0)
    for ry in (142, 147):
        cv.hline(x0, x1, ry, ZINC, 7.0, lit=0)
    # el tramvia que passa (el morro vermell i blanc, que surt per la dreta)
    tram = [(452, 98), (x1, 98), (x1, 144), (444, 144), (444, 110)]
    cv.poly(tram, TRAM, lambda x, y: 3.4 - (0.8 if y > 130 else 0), lit=0)
    cv.rect(446, 112, x1, 116, [(240, 240, 236)], 0, lit=0)
    cv.rect(452, 100, x1, 110, WIN, lambda x, y: 3.6 - (y - 100) * 0.2, lit=0)
    cv.rect(446, 118, x1, 128, WIN, 2.6, lit=0)
    cv.flat(446, 136, (255, 240, 180))
    cv.glow(446, 136, 4, (255, 240, 180), 0.5)
    outline_poly(cv, tram, TRAM)
    cv.line(470, 98, 462, 88, ZINC, 2.0, lit=0)                          # el pantògraf
    cv.line(462, 88, 474, 84, ZINC, 2.0, lit=0)
    # la catenària
    cv.line(x0, 84, x1, 83, [(30, 34, 40)], 0, lit=0)
    cv.line(x0, 90, x1, 86, [(50, 54, 60)], 0, lit=0)
    # la vorera de davant (la nostra), assolellada
    cv.rect(x0, FLOOR_Y - 2, x1, FLOOR_Y + 1, STONEW, lambda x, y: 7.0 if y == FLOOR_Y - 2 else 5.4, lit=0)
    # una paperera de ciutat i un pal de senyal a la vorera
    cv.rect(400, 120, 401, FLOOR_Y - 2, ZINC, 3.0, lit=0)
    cv.disc(400, 116, 4, 4, [(250, 250, 250), (200, 40, 40)], lambda nx, ny: 1.0 if nx * nx + ny * ny > 0.4 else 0.0, lit=0)
    cv.hline(397, 403, 116, [(250, 250, 250)], 0, lit=0)


def ground(cv):
    """El terra del carreró: asfalt net, amb un rec de llambordes, una reixa de desguàs i el sol de la boca."""
    for y in range(FLOOR_Y + 1, H):
        for x in range(W):
            n = (hr(x // 2, y // 2, 41) - 0.5) * 0.45
            sun = max(0.0, (x - 300 - (y - FLOOR_Y) * 1.4) / 60) * 1.4
            cv.put(x, y, ASPH, 3.0 + n + min(sun, 2.2))
    # el rec de llambordes, al mig del carreró
    for y in range(206, 214):
        for x in range(W):
            bx = (x + (y // 4) * 3) % 7
            cv.put(x, y, STONEW, (2.4 if bx == 0 or y % 4 == 0 else 3.6) + max(0, (x - 360) / 60), lit=0.6)
    # la vorada sota la paret i la reixa
    cv.rect(0, FLOOR_Y + 1, STREET_X - 1, FLOOR_Y + 3, STONEW, lambda x, y: 4.2 if y == FLOOR_Y + 1 else 2.8)
    obox(cv, 196, 186, 222, 192, ZINC, 2.2)
    for gx in range(199, 221, 3):
        cv.vline(gx, 187, 191, ZINC, 0.6)
    # una tapa de registre rodona
    cv.disc(70, 176, 10, 3.2, ZINC, lambda nx, ny: 2.6 + (0.8 if int((nx + 1) * 6) % 2 else 0))
    # l'ombra de la paret de l'altra banda del carreró (fora del pla, a l'esquerra)
    cv.darken(0, FLOOR_Y + 1, 120, H - 1, lambda x, y: 0.35 * max(0, 1 - x / 120))


def bg(cv, wind=0.0, led=True):
    wall(cv)
    windows(cv)
    drainpipe(cv, 12)
    drainpipe(cv, 380)
    service_door(cv)
    plate(cv)
    camera(cv, led)
    street(cv)
    ground(cv)
    chute(cv, wind)
    litter(cv)
    container(cv, wind)


PROPS = {}


# ─── Animacions: el vent, el llum de la càmera i un full que vola ───────────

def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv.img


def _frames_vent():
    """El corrent del carreró mou el paper triturat i la cortina de goma del conducte."""
    base = _base()
    frames = []
    for i in range(8):
        cv = Canvas(light=LIGHT)
        bg(cv, wind=i * math.tau / 8)
        frames.append(_diff(cv.img, base))
    return frames


def _frames_camera():
    """El llum vermell de la càmera: encès, i un instant apagat."""
    base = _base()
    cv = Canvas(light=LIGHT)
    bg(cv, led=False)
    return [_diff(base, base), _diff(base, base), _diff(cv.img, base)]


# Les quatre posicions d'un full que dona voltes: pla, inclinat, de cantell, inclinat a l'altra banda.
SHEET_POSES = [
    ['11111111', '11111111', '01111110'],
    ['000111', '001111', '011110', '111100', '111000'],
    ['11', '11', '11', '11', '11'],
    ['111000', '111100', '011110', '001111', '000111'],
]
PAPER = [(90, 88, 80), (150, 146, 134), (200, 198, 186), (232, 230, 220), (250, 250, 244)]
FLY = 40                       # fotogrames que el full és a la vista
REST = 8                       # i fotogrames de calma fins a la ràfega següent


def _frames_paperet():
    """Una ràfega arrossega un full des del carrer cap a l'esquerra del carreró, fent tombarelles."""
    base = _base()
    frames = []
    for i in range(FLY + REST):
        if i >= FLY:
            frames.append(_diff(base, base))
            continue
        cv = Canvas(light=LIGHT, img=base.copy())
        t = i / (FLY - 1)
        x = round(486 - t * 500)
        floor = 176 + round(t * 18)                                      # va baixant cap al davant
        hop = abs(math.sin(i * 0.55)) * (9 - 5 * t)
        y = floor - round(hop)
        rows = SHEET_POSES[(i // 2) % 4]
        cv.darken(x - 1, floor + 1, x + 7, floor + 2, 0.5 if hop < 4 else 0.25, dither=False)   # l'ombra
        for j, row in enumerate(rows):
            for k, b in enumerate(row):
                if b == '1':
                    cv.put(x + k, y - len(rows) + j, PAPER, 3.6 - j * 0.4 + (0.6 if k == 0 else 0))
        frames.append(_diff(cv.img, base))
    return frames


ANIMS = {
    'vent': {'frames': _frames_vent, 'frameDuration': 170},
    'camera': {'frames': _frames_camera, 'frameDuration': 450},
    'paperet': {'frames': _frames_paperet, 'frameDuration': 70},
}
