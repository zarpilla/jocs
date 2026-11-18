"""
**El dibuix pla de sempre** de la sala (font de les textures de bcmu_contenidor.py, que és en 3D).

El carrer de darrere del BCMU (final de l'Acte 3, la Vet) a 640×360: la composició de hd/rooms/bcmu_contenidor.py
×4/3, dibuixada de nou amb més detall.
  - la façana de darrere de l'edifici de 1958: sòcol de pedra encoixinada, formigó amb les marques de l'encofrat i
    els forats dels tensors, finestretes amb reixes, dues baixants, la porta de servei blau marí amb el seu llum,
    la placa discreta «BCMU» de llautó, l'intèrfon i una càmera de vigilància que mira la porta;
  - el conducte de les escombraries, de xapa a trams, amb brides i cargols, que acaba damunt del contenidor amb la
    boca de cortina de goma;
  - el contenidor verd de paper, amb la tapa una mica oberta i paper triturat que en treu el nas, damunt de rodes;
    al costat, una caixa de cartró i dues bosses de documents;
  - a la dreta, la boca del carreró: el carrer de Ginebra, assolellat; la catenària, les vies i el tramvia, i un
    altre banc (pedra, columnes, lletres d'or) amb un aparador de rellotges;
  - migdia: el sol toca la part alta de la paret i el carrer; el carreró és a l'ombra.
Animacions: `vent` (el paper triturat i la cortina de goma), `camera` (el llum vermell parpelleja) i `paperet` (una
ràfega arrossega un full pel carreró).
"""
import math

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from hd.pix import Canvas, Light, W, H, hr
from hd.rooms.comu import obox, outline, text, text_width, _diff, PLASTIC, SHEET
from hd.rooms.pis_cuina import outline_poly
from hd.rooms.bcmu_contenidor import (STONEW, CONC, ASPH, ZINC, BIN, SHRED, SKYD, FACADE, GOLDS, WIN, SHOP, TRAM,  # noqa: F401
                                      CARD, BAG, PAPER)
from hd640.rooms.bcmu import NAVYB, BRASS, logo

Canvas1x = Canvas                                   # (a 1×, com la sala en 3D)

FLOOR_Y = 200
STREET_X = 525                 # on acaba la paret del banc i comença la boca del carreró

LIGHT = Light(ambient=-0.1, vignette=(75, 1), floor_fade=(259, 40))
LIGHT.point(600, 160, r=347, k=1.6, squash=0.9, power=1.3)             # la claror que entra del carrer
LIGHT.point(115, 109, r=80, k=0.8, squash=1.0, power=1.8)              # el llum de la porta de servei
LIGHT.add(lambda x, y: 1.3 * max(0.0, 1 - y / 61) ** 1.5)              # el sol a dalt de la paret

CHUTE = (376, 403)             # el conducte: x de les dues cares
BIN_R = (320, 139, 459, 216)   # el contenidor (GEOMETRIA: contenidor)
CORNICE = 123                  # la cornisa entre la planta baixa i el primer pis


# ─── La paret del banc ─────────────────────────────────────────────────────

def wall(cv):
    """Formigó amb juntes i encofrat (pisos de dalt) i sòcol de pedra encoixinada (planta baixa)."""
    for y in range(0, FLOOR_Y):
        for x in range(STREET_X):
            n = (hr(x // 2, y // 2, 21) - 0.5) * 0.3 + (hr(x, y, 22) - 0.5) * 0.12
            if y < CORNICE + 5:
                joint = y % 32 == 31 or x % 160 == 0
                board = y % 32 in (10, 21) and hr(x // 9, y, 23) > 0.35   # les taules de l'encofrat
                stain = max(0.0, 1 - abs((x % 160) - 80) / 80) * 0.28 * (y % 32) / 32     # regalims
                tie = (x % 40 == 20) and (y % 32 == 16)                   # els forats dels tensors
                lvl = 2.6 if joint else (4.2 + n - stain - (0.25 if board else 0) - (1.4 if tie else 0))
                if x % 160 == 1 and not joint:
                    lvl += 0.5
                cv.put(x, y, CONC, lvl)
            else:
                row = (y - CORNICE - 5) // 18
                off = 29 if row % 2 else 0
                bx = (x + off) % 58
                by = (y - CORNICE - 5) % 18
                bev = 0.9 if (by == 0 or bx == 0) else (-0.9 if (by == 17 or bx == 57) else 0)
                bev += 0.35 if (by == 1 or bx == 1) else (-0.35 if (by == 16 or bx == 56) else 0)
                nb = (hr((x + off) // 58, row, 5) - 0.5) * 0.5
                cv.put(x, y, STONEW, 4.0 + n + nb + bev)
    # la cornisa entre la planta baixa i el primer pis
    cv.rect(0, CORNICE - 1, STREET_X - 1, CORNICE + 4, STONEW,
            lambda x, y: 5.2 if y == CORNICE - 1 else (4.4 if y == CORNICE else (3.6 if y < CORNICE + 4 else 2.2)))
    cv.darken(0, CORNICE + 5, STREET_X - 1, CORNICE + 8, lambda x, y: 0.55 - (y - CORNICE - 5) * 0.12)
    # la cantonada del banc, a la boca del carreró (carreus alternats)
    for y in range(0, FLOOR_Y):
        q = (y // 16) % 2
        for x in range(STREET_X - 8 - q * 3, STREET_X):
            edge = x == STREET_X - 8 - q * 3 or y % 16 == 0
            cv.put(x, y, STONEW, 4.6 + (0.9 if edge else 0) + (hr(x, y // 3) - 0.5) * 0.3)
    cv.vline(STREET_X - 1, 0, FLOOR_Y - 1, STONEW, 2.0)
    # la vorera de pedra al peu de la paret
    cv.rect(0, FLOOR_Y - 3, STREET_X - 1, FLOOR_Y, STONEW, lambda x, y: 2.2 if y == FLOOR_Y else (4.0 if y == FLOOR_Y - 3 else 3.4))


def barred_window(cv, x0, y0, w, h):
    """Una finestreta amb vidre armat i reixa de ferro (pinta de 1958)."""
    obox(cv, x0 - 4, y0 - 4, x0 + w + 4, y0 + h + 4, STONEW, 4.4)
    cv.hline(x0 - 3, x0 + w + 3, y0 - 3, STONEW, 5.4)
    for y in range(y0, y0 + h + 1):
        for x in range(x0, x0 + w + 1):
            ref = 1.0 if (x - x0) - (y - y0) * 0.6 in range(3, 7) else 0
            wire = (x - x0) % 5 == 0 or (y - y0) % 5 == 0                 # la malla del vidre armat
            cv.put(x, y, WIN, 1.6 + (y - y0) / h * 0.6 + ref + (0.3 if wire else 0))
    cv.darken(x0, y0, x0 + w, y0 + 2, 0.5)
    for bx in range(x0 + 3, x0 + w, 5):                                 # els barrots
        cv.vline(bx, y0 - 2, y0 + h + 2, ZINC, 2.4)
        cv.put(bx - 1, y0 + 1, ZINC, 1.0)
        cv.flat(bx, y0 - 2, ZINC[1])
        if hr(bx, y0, 9) > 0.6:                                         # rovell
            cv.put(bx, y0 + h - 3, [(70, 40, 20), (110, 60, 30)], 1.0)
    for yy in (y0 + h // 3, y0 + 2 * h // 3) if h > 20 else (y0 + h // 2,):
        cv.hline(x0, x0 + w, yy, ZINC, 2.2)
    cv.rect(x0 - 5, y0 + h + 4, x0 + w + 5, y0 + h + 5, STONEW, lambda x, y: 5.4 if y == y0 + h + 4 else 4.2)   # l'ampit
    cv.darken(x0 - 5, y0 + h + 6, x0 + w + 5, y0 + h + 9, lambda x, y: 0.5 - (y - y0 - h - 6) * 0.12)


def windows(cv):
    for wx in (35, 160, 261, 451):
        barred_window(cv, wx, 43, 32, 40)
    # les finestretes del soterrani, arran de terra
    for wx in (200, 275, 477):
        barred_window(cv, wx, 171, 24, 13)


def drainpipe(cv, x, top=0):
    """Una baixant de zinc amb abraçadores, una junta i el peu de ferro colat."""
    cv.rect(x, top, x + 5, FLOOR_Y - 8, ZINC,
            lambda xx, y: 3.4 + (1.6 if xx == x + 1 else (0.6 if xx == x + 2 else 0)) - (1.2 if xx == x + 5 else 0))
    for y in range(top + 13, FLOOR_Y - 13, 35):
        cv.rect(x - 1, y, x + 6, y + 2, ZINC, lambda xx, yy: 3.0 if yy == y else 2.2)
        cv.flat(x - 2, y + 1, ZINC[1])
        cv.flat(x + 7, y + 1, ZINC[1])
    for y in range(top + 30, FLOOR_Y - 13, 70):                        # les juntes dels trams
        cv.hline(x, x + 5, y, ZINC, 1.6)
    cv.rect(x - 1, FLOOR_Y - 11, x + 7, FLOOR_Y - 1, ZINC, lambda xx, y: 2.4 + (0.8 if xx == x else 0) - (0.6 if y > FLOOR_Y - 4 else 0))
    cv.hline(x - 1, x + 7, FLOOR_Y - 11, ZINC, 3.6)
    cv.darken(x + 6, top, x + 9, FLOOR_Y - 2, 0.35)


def service_door(cv):
    """La porta de servei: acer pintat de blau marí, plafons premsats, llum de reixeta i graó."""
    x0, y0, x1, y1 = 88, 133, 136, FLOOR_Y - 3
    obox(cv, x0 - 5, y0 - 5, x1 + 5, y1, CONC, 3.6)                     # el marc de formigó
    cv.hline(x0 - 4, x1 + 4, y0 - 4, CONC, 4.8)
    obox(cv, x0, y0, x1, y1, NAVYB, 3.0, top=0.6, side=-0.6)
    for py in (y0 + 8, y0 + 37):                                         # dos plafons premsats
        outline(cv, x0 + 5, py, x1 - 5, py + 21, NAVYB)
        cv.hline(x0 + 6, x1 - 6, py + 1, NAVYB, 4.0)
        cv.vline(x0 + 6, py + 1, py + 20, NAVYB, 3.6)
        cv.hline(x0 + 6, x1 - 6, py + 22, NAVYB, 4.2)
    cv.rect(x1 - 9, y0 + 32, x1 - 5, y0 + 34, ZINC, 5.0)               # la maneta
    cv.flat(x1 - 9, y0 + 32, ZINC[7])
    cv.rect(x1 - 8, y0 + 36, x1 - 6, y0 + 40, ZINC, 3.0)               # el pany
    cv.flat(x1 - 7, y0 + 38, ZINC[0])
    for hy in (y0 + 8, y1 - 19):                                        # frontisses
        cv.vline(x0 + 1, hy, hy + 11, ZINC, 3.0)
        cv.flat(x0 + 1, hy, ZINC[6])
    for i in range(9):                                                   # rascades a baix
        sx = x0 + 4 + int(hr(i, 2) * 37)
        cv.hline(sx, sx + 3 + int(hr(i, 4) * 4), y1 - 3 - int(hr(i, 3) * 9), NAVYB, 4.6)
    text(cv, 'SORTIDA', x0 + (x1 - x0 - text_width('SORTIDA')) // 2 - 2, y0 + 29, [(200, 190, 160)], 0, flat=(196, 186, 150))
    # el graó
    cv.rect(x0 - 11, y1 + 1, x1 + 11, FLOOR_Y + 4, STONEW, lambda x, y: 5.0 if y == y1 + 1 else (4.0 if y == y1 + 2 else 3.2))
    cv.darken(x0 - 11, FLOOR_Y + 5, x1 + 11, FLOOR_Y + 7, 0.5)
    # el llum de reixeta, damunt, amb el seu tub
    cv.vline(112, 100, 111, ZINC, 2.0)
    obox(cv, 105, 111, 119, 122, ZINC, 3.0)
    cv.rect(107, 113, 117, 120, [(255, 236, 190)], 0, lit=0)
    for xx in (109, 112, 115):
        cv.vline(xx, 113, 120, ZINC, 2.0)
    cv.hline(107, 117, 116, ZINC, 2.4)
    cv.glow(112, 120, 22, (255, 230, 180), 0.25)


def plate(cv):
    """La placa discreta de llautó: el logotip i «BCMU», res més; i l'intèrfon."""
    x0, y0, x1, y1 = 149, 139, 192, 157
    obox(cv, x0, y0, x1, y1, BRASS, 3.6)
    cv.hline(x0 + 1, x1 - 1, y0 + 1, BRASS, 5.4)
    cv.vline(x0 + 1, y0 + 2, y1 - 1, BRASS, 4.4)
    logo(cv, x0 + 9, y0 + 9, k=0.93, lvl=1.8)
    text(cv, 'BCMU', x0 + 18, y0 + 7, NAVYB, 1.6)
    for sx, sy in ((x0 + 2, y0 + 2), (x1 - 2, y0 + 2), (x0 + 2, y1 - 2), (x1 - 2, y1 - 2)):   # els cargols
        cv.flat(sx, sy, BRASS[2])
        cv.flat(sx + 1, sy, BRASS[4] if len(BRASS) > 4 else BRASS[-1])
    cv.darken(x0 + 1, y1 + 1, x1 + 1, y1 + 3, 0.4)
    # un timbre amb intèrfon, al costat
    ix0, iy0 = x0 + 8, y1 + 8
    obox(cv, ix0, iy0, ix0 + 13, iy0 + 19, ZINC, 3.4)
    cv.hline(ix0 + 1, ix0 + 12, iy0 + 1, ZINC, 4.6)
    for k in range(4):
        cv.hline(ix0 + 3, ix0 + 10, iy0 + 4 + k * 2, ZINC, 1.6)
    cv.disc(ix0 + 6.5, iy0 + 15, 2, 2, [(150, 130, 80), (220, 200, 140), (250, 236, 190)], lambda nx, ny: 1.6 - nx - ny, lit=0)
    cv.darken(ix0 + 1, iy0 + 20, ix0 + 14, iy0 + 21, 0.4)


def camera(cv, led=True):
    """La càmera de vigilància, en un braç, apuntant cap a la porta de servei (llum vermell que parpelleja)."""
    bx, by = 349, 27
    obox(cv, bx, by - 5, bx + 8, by + 8, ZINC, 3.4)                     # la placa de la paret
    for sy in (by - 3, by + 6):
        cv.flat(bx + 4, sy, ZINC[1])
    cv.line(bx, by + 1, bx - 11, by + 7, ZINC, 3.6)                      # el braç
    cv.line(bx, by + 2, bx - 11, by + 8, ZINC, 2.0)
    cv.disc(bx - 11, by + 8, 1.6, 1.6, ZINC, 2.6)                        # la ròtula
    body = [(bx - 40, by + 16), (bx - 8, by + 3), (bx - 4, by + 11), (bx - 35, by + 24)]
    cv.poly(body, SHEET, lambda x, y: 4.6 - (y - by) * 0.09)
    outline_poly(cv, body, SHEET)
    cv.line(bx - 37, by + 20, bx - 7, by + 8, SHEET, 5.4)                # el cantell que brilla
    cv.poly([(bx - 43, by + 13), (bx - 8, by), (bx - 7, by + 3), (bx - 40, by + 16)], SHEET, 5.2)   # la visera
    cv.line(bx - 43, by + 13, bx - 8, by, SHEET, 6.0)
    cv.disc(bx - 37, by + 20, 3, 3, PLASTIC, lambda nx, ny: 0.6 + ny * 0.6)                          # l'objectiu
    cv.ring(bx - 37, by + 20, 3, SHEET, 2.4, step=20)
    cv.flat(bx - 38, by + 19, (160, 200, 230))
    cv.flat(bx - 37, by + 21, (60, 90, 120))
    for k in range(3):                                                  # la reixeta de ventilació del darrere
        cv.line(bx - 14 + k * 2, by + 7, bx - 12 + k * 2, by + 11, SHEET, 3.2)
    if led:
        cv.flat(bx - 16, by + 13, (240, 40, 36))
        cv.flat(bx - 15, by + 13, (255, 120, 100))
        cv.glow(bx - 16, by + 13, 5, (255, 50, 40), 0.5)
    else:
        cv.flat(bx - 16, by + 13, (90, 24, 24))
        cv.flat(bx - 15, by + 13, (70, 24, 24))
    cv.line(bx + 4, by + 8, bx + 4, by + 30, PLASTIC, 1.2)              # el cable, grapat a la paret
    cv.darken(bx - 37, by + 25, bx - 5, by + 30, 0.3)


def chute(cv, wind=0.0):
    """El conducte de les escombraries: xapa galvanitzada a trams, amb brides i abraçadores a la paret,
    que acaba amb una boca inclinada i una cortina de tires de goma just damunt del contenidor."""
    x0, x1 = CHUTE
    end = 117
    for y in range(0, end):
        fy = y % 29
        for x in range(x0, x1 + 1):
            lvl = 4.0 + (1.8 if x == x0 + 3 else (0.8 if x == x0 + 4 else 0)) + (0.6 if x < x0 + 8 else 0) - (1.4 if x > x1 - 5 else 0)
            lvl += (hr(x // 2, y // 6, 13) - 0.5) * 0.4
            if fy == 0:
                lvl += 1.2
            elif fy in (1, 2):
                lvl -= 0.6
            cv.put(x, y, ZINC, lvl)
        if fy == 0:                                                     # la brida sobresurt
            cv.rect(x0 - 1, y, x1 + 1, y + 1, ZINC, lambda xx, yy: 4.6 if yy == y else 3.2)
    for y in range(29, end, 29):                                        # els cargols de les brides
        for bxx in (x0 + 4, (x0 + x1) // 2 - 4, (x0 + x1) // 2 + 4, x1 - 4):
            cv.flat(bxx, y + 1, ZINC[1])
            cv.flat(bxx, y, ZINC[6])
    for y in range(8, end, 29):                                         # una costura vertical a cada tram
        cv.vline(x0 + 17, y, y + 18, ZINC, 2.8)
    for y in (19, 77):                                                  # les abraçadores a la paret
        cv.rect(x0 - 7, y, x0 - 1, y + 4, ZINC, lambda xx, yy: 3.4 if yy == y else 2.6)
        cv.rect(x1 + 1, y, x1 + 7, y + 4, ZINC, lambda xx, yy: 3.4 if yy == y else 2.6)
        cv.flat(x0 - 5, y + 2, ZINC[1])
        cv.flat(x1 + 5, y + 2, ZINC[1])
    outline(cv, x0, 0, x1, end - 1, ZINC)
    cv.darken(x1 + 1, 0, x1 + 7, end + 8, 0.4)                          # l'ombra a la paret
    # la boca: s'eixampla i s'inclina cap endavant
    mouth = [(x0 - 1, end), (x1 + 1, end), (x1 + 7, 130), (x0 - 7, 130)]
    cv.poly(mouth, ZINC, lambda x, y: 4.6 - (y - end) * 0.06 - (1.2 if x > x1 else 0) + (0.6 if x < x0 else 0))
    outline_poly(cv, mouth, ZINC)
    cv.rect(x0 - 7, 129, x1 + 7, 131, ZINC, lambda x, y: 5.6 if y == 129 else 4.2)
    for rx in range(x0 - 4, x1 + 6, 6):                                 # els reblons de la vora
        cv.flat(rx, 130, ZINC[2])
    # la cortina de goma (tires negres): el vent en mou la punta
    for k, x in enumerate(range(x0 - 6, x1 + 6, 4)):
        ln = 6 + int(hr(k, 8) * 3)
        sway = math.sin(wind + k * 0.9)
        for j in range(ln + 1):
            dx = round(sway * 1.8 * j / ln)
            cv.rect(x + dx, 132 + j, x + 2 + dx, 132 + j, PLASTIC, 1.6 + (0.6 if k % 2 else 0) + (0.5 if j == 0 else 0))
            cv.put(x + dx, 132 + j, PLASTIC, 2.6 + (0.6 if k % 2 else 0))
    # una etiqueta groga d'avís, al conducte
    YELW = [(60, 40, 0), (150, 110, 10), (230, 190, 40), (250, 226, 110)]
    obox(cv, x0 + 5, 85, x1 - 5, 99, YELW, 2.6)
    cv.poly([(x0 + 13, 96), (x0 + 16, 88), (x0 + 19, 96)], [(30, 20, 0)], 0)
    cv.flat(x0 + 16, 92, YELW[3])
    cv.hline(x1 - 12, x1 - 7, 89, [(30, 20, 0)], 0)
    cv.hline(x1 - 12, x1 - 8, 92, [(30, 20, 0)], 0)
    cv.hline(x1 - 12, x1 - 7, 95, [(30, 20, 0)], 0)
    # un esgarrinxat de sota: no fa gaire que algú ha llençat alguna cosa
    for k in range(4):
        cv.flat(x0 + 3 + k * 7, 137 + (k % 2), SHRED[3])


# ─── El contenidor ─────────────────────────────────────────────────────────

def container(cv, wind=0.0):
    """El contenidor verd del paper, amb la tapa mig oberta i paper triturat que en surt."""
    x0, y0, x1, y1 = BIN_R
    lid_y1 = y0 + 12
    body_top, body_bot = lid_y1 + 1, y1 - 12
    # l'ombra al terra i a la paret
    cv.darken(x0 - 8, FLOOR_Y - 40, x0 - 1, FLOOR_Y, 0.35)
    cv.darken(x0 - 5, y1 - 3, x1 + 13, y1 + 5, lambda x, y: 0.75 - abs(y - y1 - 1) * 0.08)

    def bx(y):                                                           # el cos: s'estreny una mica cap avall
        t = (y - body_top) / (body_bot - body_top)
        return x0 + 3 + round(t * 4), x1 - 3 - round(t * 4)
    for y in range(body_top, body_bot + 1):
        a, b = bx(y)
        for x in range(a, b + 1):
            rib = (x - x0) % 21 == 11
            lvl = 4.2 - (y - body_top) * 0.022 + (0.9 if rib else (-0.5 if (x - x0) % 21 == 12 else 0))
            lvl += -(1.2 if x > b - 4 else 0) + (0.8 if x < a + 3 else 0)
            lvl += (hr(x // 3, y // 3, 17) - 0.5) * 0.3 + (hr(x, y, 18) - 0.5) * 0.1
            cv.put(x, y, BIN, lvl)
        cv.flat(a, y, BIN[0])
        cv.flat(b, y, BIN[0])
    cv.hline(bx(body_bot)[0], bx(body_bot)[1], body_bot, BIN, 0.6)
    for i in range(14):                                                  # rascades i cops a la pintura
        sx = x0 + 10 + int(hr(i, 40) * (x1 - x0 - 20))
        sy = body_top + 8 + int(hr(i, 41) * (body_bot - body_top - 12))
        cv.hline(sx, sx + 1 + int(hr(i, 42) * 4), sy, BIN, 5.4 if i % 3 else 1.4)
    # el reforç de la vora de dalt
    cv.rect(x0 + 1, body_top, x1 - 1, body_top + 4, BIN, lambda x, y: 5.0 if y == body_top else (4.0 if y == body_top + 1 else 3.4))
    outline(cv, x0 + 1, body_top, x1 - 1, body_top + 4, BIN)
    # els agafadors laterals
    for hx in (x0 - 1, x1 - 3):
        obox(cv, hx, body_top + 8, hx + 4, body_top + 14, BIN, 2.8)
        cv.vline(hx + 1, body_top + 9, body_top + 13, BIN, 4.4)
    # l'adhesiu: «PAPIER · PAPER» i el símbol del reciclatge
    sx0, sy0, sx1, sy1 = 349, 165, 429, 189
    GR = [(30, 110, 50)]
    obox(cv, sx0, sy0, sx1, sy1, SHEET, 4.8)
    cv.rect(sx0 + 1, sy0 + 1, sx1 - 1, sy0 + 4, GR, 0)
    cv.rect(sx0 + 1, sy1 - 3, sx1 - 1, sy1 - 1, GR, 0)
    cx, cy = sx0 + 13, sy0 + 14
    cv.ring(cx, cy, 5.5, GR, 0, step=8)
    cv.ring(cx, cy, 4.5, GR, 0, step=8)
    for k in range(3):                                                   # tres fletxes en triangle
        a = math.radians(k * 120 - 90)
        hx, hy = cx + round(math.cos(a) * 5), cy + round(math.sin(a) * 5)
        cv.disc(hx, hy, 2, 2, GR, 0)
        cv.flat(cx + round(math.cos(a) * 2.5), cy + round(math.sin(a) * 2.5), (230, 236, 230))
    text(cv, 'PAPIER', sx0 + 26, sy0 + 7, [(30, 40, 30)], 0, flat=(30, 40, 30))
    text(cv, 'PAPER', sx0 + 26, sy0 + 14, [(30, 110, 50)], 0, flat=(36, 110, 56))
    text(cv, 'GE', x1 - 19, body_top + 9, BIN, 6.4)
    cv.rect(x1 - 19, body_top + 16, x1 - 8, body_top + 17, [(160, 30, 30), (220, 60, 50)], 0.6)   # l'escut de Ginebra, de mentida
    # la tapa, una mica aixecada per davant
    lid = [(x0 - 3, y0 + 4), (x1 + 3, y0 + 4), (x1 + 4, lid_y1), (x0 - 4, lid_y1)]
    cv.poly([(x0, y0), (x1, y0), (x1 + 3, y0 + 4), (x0 - 3, y0 + 4)], BIN, 5.2)
    cv.poly(lid, BIN, lambda x, y: 4.0 - (y - y0) * 0.11 - (1.0 if x > x1 - 3 else 0) + (hr(x // 4, y, 19) - 0.5) * 0.25)
    outline_poly(cv, [(x0, y0), (x1, y0), (x1 + 4, lid_y1), (x0 - 4, lid_y1)], BIN)
    cv.hline(x0 + 1, x1 - 1, y0 + 1, BIN, 6.4)
    cv.hline(x0 - 2, x1 + 2, y0 + 5, BIN, 3.0)
    for hx in (x0 + 24, x1 - 24):                                        # les frontisses de la tapa
        cv.rect(hx, y0 + 1, hx + 6, y0 + 3, BIN, 2.2)
    # l'escletxa sota la tapa: fosc, i paper triturat que en penja
    cv.hline(x0 - 2, x1 + 2, lid_y1 + 1, BIN, 0.2)
    cv.hline(x0 + 2, x1 - 2, lid_y1 + 2, BIN, 1.0)
    for k in range(40):
        sx = x0 + 8 + int(hr(k, 31) * (x1 - x0 - 16))
        ln = 3 + int(hr(k, 32) * 9)
        sway = math.sin(wind + hr(k, 35) * 6.28) * (0.8 + hr(k, 36) * 1.3)
        for j in range(ln):
            dx = (j // 4 if hr(k, 33) > 0.5 else -(j // 4)) + round(sway * j / 9)
            cv.put(sx + dx, lid_y1 + 1 + j, SHRED, 2.6 + hr(k, 34) * 1.6 + (0.4 if j == 0 else 0))
    # una tira llarga que penja fins a l'adhesiu (i que el vent fa onejar)
    for j in range(19):
        cv.put(400 + round(math.sin(j * 0.45 - wind) * (0.8 + j / 14)), lid_y1 + 1 + j, SHRED, 3.4)
    # les rodes
    for wx in (x0 + 11, x1 - 19):
        obox(cv, wx, body_bot + 1, wx + 8, body_bot + 4, ZINC, 2.6)
        cv.disc(wx + 4, y1 - 4, 4.5, 4.5, PLASTIC, lambda nx, ny: 2.4 - ny - nx * 0.3)
        cv.disc(wx + 4, y1 - 4, 1.5, 1.5, ZINC, 4.4)
        cv.flat(wx + 4, y1 - 4, ZINC[2])


def litter(cv):
    """Al costat del contenidor: una caixa de cartró plegada i dues bosses de documents (blau marí, segellades)."""
    x0, y0, x1, y1 = 464, 160, 501, 213
    obox(cv, x0, y0, x1, y1, CARD, 3.4)
    cv.line(x0 + 3, y0 + 5, x1 - 3, y1 - 5, CARD, 2.6)                   # el plec
    cv.line(x0 + 3, y0 + 6, x1 - 3, y1 - 4, CARD, 4.0)
    cv.hline(x0 + 1, x1 - 1, 184, [(200, 180, 120), (230, 214, 160)], 0.6)   # cinta
    cv.hline(x0 + 1, x1 - 1, 185, [(170, 150, 100), (200, 180, 120)], 0.6)
    text(cv, 'BCMU', 469, 170, CARD, 1.4)
    cv.rect(x0 + 6, 194, x0 + 14, 198, CARD, 1.6)                        # una fletxa «aquest costat amunt»
    cv.vline(x0 + 10, 189, 193, CARD, 1.6)
    cv.hline(x0 + 8, x0 + 12, 190, CARD, 1.6)
    cv.darken(461, y1, 507, y1 + 4, 0.5)
    for bxc, sq in ((304, 1.0), (512, 0.8)):                           # bosses d'escombraries, lligades
        s = sq * 4 / 3
        lump = [(bxc - 9 * s, 216), (bxc - 10 * s, 205), (bxc - 7 * s, 197), (bxc - 3 * s, 194), (bxc - 1, 193),
                (bxc + 4 * s, 194), (bxc + 7 * s, 197), (bxc + 10 * s, 204), (bxc + 9 * s, 216)]
        cv.poly(lump, BAG, lambda x, y, c=bxc: 3.2 - (y - 193) * 0.045 - (x - c) * 0.075 + (hr(x // 3, y // 2, 7) - 0.5) * 0.6)
        outline_poly(cv, lump, BAG)
        cv.poly([(bxc - 4, 194), (bxc - 1, 186), (bxc + 1, 194)], BAG, 2.6)          # el nus
        cv.poly([(bxc, 193), (bxc + 5, 187), (bxc + 3, 194)], BAG, 3.2)
        cv.line(bxc - 5 * s, 200, bxc - 3 * s, 211, BAG, 4.2)                         # el plec que brilla
        cv.line(bxc + 3 * s, 202, bxc + 5 * s, 208, BAG, 1.6)
        cv.rect(bxc - 1, 194, bxc + 1, 195, [(160, 150, 120), (220, 210, 180)], 0.6)  # el precinte, al nus
    cv.darken(288, 216, 320, 220, 0.45)
    cv.darken(499, 216, 525, 220, 0.45)


# ─── La boca del carreró: el carrer de Ginebra ─────────────────────────────

def street(cv, tram=True):
    """Cel, l'altre banc (pedra, columnes, lletres d'or), l'aparador de rellotges, la catenària i el tramvia
    (`tram`: si hi és; la sala en 3D el fa a part)."""
    x0, x1 = STREET_X, W - 1
    for y in range(0, 29):
        for x in range(x0, x1 + 1):
            cv.put(x, y, SKYD, 4.4 - y / 16 + (hr(x // 6, y // 3, 50) - 0.5) * 0.3, lit=0)
    # l'altre banc, a l'altra banda del carrer
    for y in range(29, 179):
        for x in range(x0, x1 + 1):
            joint = (y - 29) % 11 == 10 or ((x + ((y - 29) // 11) * 17) % 34 == 0 and y < 93)
            cv.put(x, y, FACADE, (3.4 if joint else 4.6) + (hr(x // 4, y // 8) - 0.5) * 0.3, lit=0)
    cv.rect(x0, 29, x1, 35, FACADE, lambda x, y: 6.0 if y == 29 else (5.0 if y == 30 else 4.0), lit=0)     # la cornisa
    for dx in range(x0 + 2, x1, 6):                                      # dentells
        cv.rect(dx, 36, dx + 2, 37, FACADE, 5.0, lit=0)
    cv.darken(x0, 38, x1, 39, 0.4)
    for wx in (536, 568, 600):                                           # finestres del pis
        cv.rect(wx - 2, 44, wx + 18, 47, FACADE, lambda x, y: 6.0 if y == 44 else 5.2, lit=0)
        cv.rect(wx, 48, wx + 16, 77, WIN, lambda x, y, wx=wx: 2.2 + (1.4 if x - wx == (y - 48) // 3 else 0), lit=0)
        cv.vline(wx + 8, 48, 77, FACADE, 4.6, lit=0)
        cv.hline(wx, wx + 16, 60, FACADE, 4.6, lit=0)
        cv.rect(wx - 3, 78, wx + 19, 80, FACADE, lambda x, y: 6.0 if y == 78 else 4.6, lit=0)
        for bx in range(wx - 1, wx + 18, 3):                             # la barana de ferro
            cv.vline(bx, 81, 85, [(40, 40, 44)], 0, lit=0)
        cv.hline(wx - 2, wx + 18, 81, [(40, 40, 44)], 0, lit=0)
    # les lletres d'or sobre la planta baixa
    cv.rect(x0, 93, x1, 107, FACADE, lambda x, y: 3.6 if y in (93, 107) else 3.2, lit=0)
    s = 'BANQUE PRIVÉE'
    text(cv, s, x0 + (x1 - x0 - text_width(s)) // 2 + 1, 98, GOLDS, 3.2, lit=0)
    # les columnes i l'aparador de rellotges, encès
    for sx in (537, 588):
        cv.rect(sx, 115, sx + 42, 171, SHOP, lambda x, y: 1.6 + (y - 115) / 40, lit=0)
        cv.rect(sx, 115, sx + 42, 117, FACADE, 2.0, lit=0)
        for k in range(5):                                               # rellotges en coixinets
            wx, wy = sx + 6 + k * 8, 136 + (k % 2) * 11
            cv.rect(wx - 3, wy - 1, wx + 3, wy + 6, [(70, 30, 30), (110, 50, 50)], 0.6, lit=0)   # el coixinet
            cv.disc(wx, wy, 3, 3, [(120, 90, 40), (200, 166, 80), (240, 214, 130)], lambda nx, ny: 1.4 - ny, lit=0)
            cv.disc(wx, wy, 2, 2, [(220, 200, 160), (255, 250, 230)], 0.8, lit=0)
            cv.flat(wx, wy, (40, 30, 20))
            cv.flat(wx, wy - 1, (40, 30, 20))
        cv.rect(sx + 2, 160, sx + 40, 164, [(90, 20, 30), (140, 40, 50)], 0.6, lit=0)  # el vellut
        cv.tint(sx + 1, 118, sx + 41, 159, (255, 250, 230), lambda x, y, sx=sx: 0.25 if 0 <= (x - sx) - (y - 118) * 0.25 - 3 < 2 else 0)   # un reflex al vidre
        cv.glow(sx + 21, 141, 24, (255, 230, 170), 0.2)
    for cx in (531, 581, 632):
        cv.rect(cx, 109, cx + 5, 178, FACADE, lambda x, y, cx=cx: 5.0 + (0.8 if x == cx + 1 else 0) - (1.2 if x == cx + 5 else 0), lit=0)
        cv.rect(cx - 1, 109, cx + 6, 111, FACADE, 6.0, lit=0)            # el capitell
    # la vorera de l'altra banda, la calçada i les vies
    cv.rect(x0, 179, x1, 183, FACADE, lambda x, y: 5.6 if y == 179 else 4.2, lit=0)
    for y in range(184, FLOOR_Y + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, ASPH, 4.6 + (hr(x // 2, y) - 0.5) * 0.4, lit=0)
    for ry in (189, 196):
        cv.hline(x0, x1, ry, ZINC, 7.0, lit=0)
        cv.hline(x0, x1, ry + 1, ASPH, 3.2, lit=0)
    if tram:
        _tram(cv, x1)
    # la catenària
    cv.line(x0, 112, x1, 111, [(30, 34, 40)], 0, lit=0)
    cv.line(x0, 120, x1, 115, [(50, 54, 60)], 0, lit=0)
    for hx in (556, 604):                                                # les penjoles
        cv.vline(hx, 112, 119 - (hx - x0) * 5 // 115, [(50, 54, 60)], 0, lit=0)
    # la vorera de davant (la nostra), assolellada
    cv.rect(x0, FLOOR_Y - 3, x1, FLOOR_Y + 1, STONEW, lambda x, y: 7.0 if y == FLOOR_Y - 3 else 5.4, lit=0)
    # una paperera de ciutat i un pal de senyal a la vorera
    cv.rect(533, 160, 534, FLOOR_Y - 3, ZINC, 3.0, lit=0)
    cv.disc(533, 155, 5.4, 5.4, [(250, 250, 250), (200, 40, 40)], lambda nx, ny: 1.0 if nx * nx + ny * ny > 0.45 else 0.0, lit=0)
    cv.hline(529, 537, 155, [(250, 250, 250)], 0, lit=0)
    cv.hline(529, 537, 156, [(250, 250, 250)], 0, lit=0)


def _tram(cv, x1):
    """El tramvia que passa (el morro vermell i blanc, que surt per la dreta)."""
    tram = [(603, 131), (x1, 131), (x1, 192), (592, 192), (592, 147)]
    cv.poly(tram, TRAM, lambda x, y: 3.4 - (0.8 if y > 173 else 0) + (0.6 if x < 596 else 0), lit=0)
    cv.rect(595, 149, x1, 154, [(240, 240, 236)], 0, lit=0)
    cv.rect(603, 133, x1, 146, WIN, lambda x, y: 3.6 - (y - 133) * 0.15, lit=0)
    cv.vline(622, 133, 146, TRAM, 2.6, lit=0)
    cv.rect(595, 157, x1, 170, WIN, 2.6, lit=0)
    cv.vline(615, 157, 170, TRAM, 2.6, lit=0)
    text(cv, '12', 624, 160, [(255, 220, 120)], 0, lit=0, flat=(255, 220, 120))   # el número de línia
    cv.flat(595, 181, (255, 240, 180))
    cv.flat(596, 181, (255, 250, 220))
    cv.glow(595, 181, 5, (255, 240, 180), 0.5)
    outline_poly(cv, tram, TRAM)
    cv.line(627, 131, 616, 117, ZINC, 2.0, lit=0)                        # el pantògraf
    cv.line(616, 117, 632, 112, ZINC, 2.0, lit=0)


def ground(cv):
    """El terra del carreró: asfalt net, amb un rec de llambordes, una reixa de desguàs i el sol de la boca."""
    for y in range(FLOOR_Y + 1, H):
        for x in range(W):
            n = (hr(x // 2, y // 2, 41) - 0.5) * 0.4 + (hr(x, y, 42) - 0.5) * 0.15
            sun = max(0.0, (x - 400 - (y - FLOOR_Y) * 1.4) / 80) * 1.4
            crack = 0.9 if (abs((x - 140) - (y - 230) * 2.2 - math.sin(y * 0.4) * 2) < 0.6 and 226 < y < 250) else 0
            cv.put(x, y, ASPH, 3.0 + n + min(sun, 2.2) - crack)
    # el rec de llambordes, al mig del carreró
    for y in range(275, 286):
        for x in range(W):
            bx = (x + ((y - 275) // 5) * 4) % 9
            by = (y - 275) % 5
            cv.put(x, y, STONEW, (2.4 if bx == 0 or by == 0 else 3.6 + (0.4 if by == 1 else 0)) + max(0, (x - 480) / 80), lit=0.6)
    # la vorada sota la paret i la reixa
    cv.rect(0, FLOOR_Y + 1, STREET_X - 1, FLOOR_Y + 4, STONEW, lambda x, y: 4.2 if y == FLOOR_Y + 1 else 2.8)
    obox(cv, 261, 248, 296, 256, ZINC, 2.2)
    for gx in range(264, 294, 4):
        cv.vline(gx, 249, 255, ZINC, 0.6)
        cv.vline(gx + 1, 249, 255, ZINC, 1.2)
    # una tapa de registre rodona
    cv.disc(93, 235, 13, 4.3, ZINC, lambda nx, ny: 2.6 + (0.8 if int((nx + 1) * 8) % 2 else 0) - ny * 0.3)
    # una llauna aixafada i una burilla
    cv.rect(212, 262, 216, 263, [(120, 30, 30), (190, 60, 50), (220, 210, 200)], 1.4)
    cv.flat(216, 262, (220, 220, 220))
    cv.hline(352, 354, 244, [(230, 220, 200)], 0)
    cv.flat(355, 244, (200, 120, 60))
    # l'ombra de la paret de l'altra banda del carreró (fora del pla, a l'esquerra)
    cv.darken(0, FLOOR_Y + 1, 160, H - 1, lambda x, y: 0.35 * max(0, 1 - x / 160))


def bg(cv, wind=0.0, led=True):
    wall(cv)
    windows(cv)
    drainpipe(cv, 16)
    drainpipe(cv, 507)
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

_BASE = {}


def _base():
    if 'img' not in _BASE:
        cv = Canvas(light=LIGHT)
        bg(cv)
        _BASE['img'] = cv.img
    return _BASE['img']


def _frames_vent():
    """El corrent del carreró mou el paper triturat i la cortina de goma del conducte."""
    base = _base()
    frames = []
    for i in range(12):
        cv = Canvas(light=LIGHT)
        bg(cv, wind=i * math.tau / 12)
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
    ['11111111111', '11111111111', '11111111111', '01111111110'],
    ['00000111', '00001111', '00011110', '00111100', '01111000', '11110000', '11100000'],
    ['11', '11', '11', '11', '11', '11', '11'],
    ['11100000', '11110000', '01111000', '00111100', '00011110', '00001111', '00000111'],
]
FLY = 54                       # fotogrames que el full és a la vista
REST = 11                      # i fotogrames de calma fins a la ràfega següent


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
        x = round(648 - t * 667)
        floor = 235 + round(t * 24)                                      # va baixant cap al davant
        hop = abs(math.sin(i * 0.41)) * (12 - 7 * t)
        y = floor - round(hop)
        rows = SHEET_POSES[(i // 2) % 4]
        cv.darken(x - 1, floor + 1, x + 10, floor + 2, 0.5 if hop < 5 else 0.25, dither=False)   # l'ombra
        for j, row in enumerate(rows):
            for k, b in enumerate(row):
                if b == '1':
                    cv.put(x + k, y - len(rows) + j, PAPER, 3.6 - j * 0.3 + (0.6 if k == 0 else 0))
        if rows is SHEET_POSES[0]:                                       # unes ratlles d'escrit
            cv.hline(x + 2, x + 7, y - 3, PAPER, 1.6)
        frames.append(_diff(cv.img, base))
    return frames


ANIMS = {
    'vent': {'frames': _frames_vent, 'frameDuration': 170},
    'camera': {'frames': _frames_camera, 'frameDuration': 450},
    'paperet': {'frames': _frames_paperet, 'frameDuration': 52},
}
