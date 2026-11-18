"""
**El dibuix pla de sempre** (font de les textures de la sala en 3D, passadis_baix.py).

Prova de resolució: el passadís de la coberta de sota (hd/rooms/passadis_baix.py) a 640×360, la composició ×4/3
dibuixada de nou. Estret, verd i de ferro. D'esquerra a dreta: la porta del camarot de l'Iri, la porta estanca de
la sala de màquines, la del pallol (amb el cadenat obert), l'escotilla de la sala de bombes (a terra) i l'escala que
puja a la coberta principal.
Sota el tauler de suro, el repetidor d'alarmes de les màquines (tot en verd). Prop: `petjades` (Escena 1: les
petjades mullades d'en Diu, entre el camarot i la porta de màquines).
Animacions: `llum` (el llum de gàbia de la dreta fa mal contacte) i `gota` (condensació sota el tub de gasoil).
"""
import math
from functools import lru_cache

from PIL import Image

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from hd.pix import Canvas, Light, W, H, hr, mix, B4, WALNUT, PAPER
from hd.rooms.arenga import (WALL, ENG, DECK, CAB, DARK, WHITEP, YELL, REDP, SEAG, FUEL, BRASS,
                             box, rrect, bolt, hpipe, vpipe, glow)
from hd.rooms.comu import text, text_width
from hd.rooms.camarot_iri import PAINT
from hd640.rooms import sota
from hd640.rooms.sota import FLOOR_Y, BOTTOM

from hd.pix import Canvas  # noqa: E402,F811  (a 1×: és la font de les textures de la sala en 3D)
Canvas1x = Canvas

LAMPS = (200, 440)
LAMP_Y = 29

LIGHT = Light(ambient=-0.45, vignette=(64, 37), floor_fade=None)
LIGHT.point(200, 35, r=200, k=2.5, squash=1.05, down=True, power=1.5)
LIGHT.point(440, 35, r=200, k=2.4, squash=1.05, down=True, power=1.5)
LIGHT.point(595, 32, r=147, k=1.6, squash=0.9, power=1.6)        # la llum de la coberta principal, per l'escala

CAMAROT = (29, 85, 91, FLOOR_Y)
MAQUINES = (149, 83, 224, FLOOR_Y)
PALLOL = (283, 85, 344, FLOOR_Y)
HATCH = [(400, 224), (480, 224), (488, 248), (392, 248)]
CREAM = [(40, 36, 28), (80, 72, 56), (126, 114, 90), (170, 156, 124), (206, 192, 156), (232, 222, 190)]


# ─── Paret, sostre, tubs ────────────────────────────────────────────────────

def walls(cv):
    sota.plate_wall(cv, 0, W - 1, frames=85, frame0=-40, seams=(75, 149), rust=40, seed=11)
    sota.ceiling(cv, beam0=-40)
    # aigua de mar i gasoil, com a la sala de màquines (hi van a parar)
    hpipe(cv, 0, W - 1, 48, 4, SEAG, 3.0, bands=range(53, W, 69), band_ramp=WHITEP)
    hpipe(cv, 0, 539, 61, 3, FUEL, 3.0, bands=range(88, W, 69), band_ramp=YELL)
    for x in range(53, W, 69):                                        # fletxes del sentit
        for i in range(3):
            cv.vline(x + 4 + i, 46 + i, 50 - i, WHITEP, 4.4)
    for x in range(27, 540, 64):                                      # abraçadores
        cv.vline(x, 41, 65, CAB, 2.0)
        cv.vline(x + 1, 41, 65, CAB, 3.4)
        cv.put(x + 1, 43, CAB, 4.8)
    cv.disc(539, 61, 3, 3, FUEL, lambda nx, ny: 3.4 - nx - ny)           # el tap del gasoil
    # un tub que baixa fins a terra entre el pallol i l'escotilla, amb una vàlvula
    vpipe(cv, 373, 48, FLOOR_Y + 2, 3, SEAG, 2.8, bands=(107, 171), band_ramp=WHITEP)
    cv.disc(373, 48, 4, 4, SEAG, lambda nx, ny: 3.4 - nx - ny)
    box(cv, 369, 128, 377, 136, CAB, 3.2)
    cv.disc(373, 124, 6, 2, REDP, lambda nx, ny: 3.6 - nx - ny)          # el volant de la vàlvula
    cv.vline(373, 124, 128, CAB, 3.6)


def cabin_door(cv):
    """La porta del camarot: de planxa pintada, amb reixeta a baix, número de llautó i l'adhesiu d'un gat."""
    x0, y0, x1, y1 = CAMAROT
    sota.door_frame(cv, x0, y0, x1, y1, ramp=WALL, lvl=4.2, r=8)
    rrect(cv, x0, y0, x1, y1 - 1, 7, PAINT, lambda x, y: 3.6 - (y - y0) * 0.003)
    rrect(cv, x0 + 7, y0 + 8, x1 - 7, y0 + 59, 4, PAINT, 4.0)
    cv.hline(x0 + 9, x1 - 9, y0 + 8, PAINT, 5.0)
    cv.vline(x1 - 7, y0 + 11, y0 + 57, PAINT, 2.6)
    rrect(cv, x0 + 7, y1 - 37, x1 - 7, y1 - 7, 4, PAINT, 3.8)
    for i in range(7):                                                # reixeta de ventilació
        cv.hline(x0 + 12, x1 - 12, y1 - 32 + i * 4, PAINT, 1.6)
        cv.hline(x0 + 12, x1 - 12, y1 - 31 + i * 4, PAINT, 4.4)
    # frontisses i maneta
    for hy in (y0 + 14, y1 - 30):
        box(cv, x0 - 2, hy, x0 + 2, hy + 10, CAB, 3.6)
    box(cv, x1 - 12, 139, x1 - 8, 149, BRASS, 3.6)
    cv.hline(x1 - 19, x1 - 9, 141, BRASS, 4.6)
    cv.hline(x1 - 19, x1 - 9, 142, BRASS, 2.6)
    # la placa amb el número
    box(cv, x0 + 24, y0 + 18, x0 + 38, y0 + 26, BRASS, 3.6)
    text(cv, '4', x0 + 30, y0 + 20, None, 0, flat=(60, 40, 16))
    # un adhesiu d'un gat negre, posat torçat (de l'Iri)
    CAT = [(20, 20, 22), (50, 50, 54), (90, 90, 96)]
    cx, cy = x0 + 31, y0 + 43
    cv.disc(cx, cy, 6, 5, CAT, 1.6)
    cv.poly([(cx - 5, cy - 2), (cx - 5, cy - 8), (cx - 2, cy - 4)], CAT, 1.4)
    cv.poly([(cx + 4, cy - 3), (cx + 6, cy - 8), (cx + 1, cy - 4)], CAT, 1.4)
    for ex in (cx - 3, cx + 2):
        cv.put(ex, cy - 1, YELL, 4.6, lit=0)
        cv.put(ex + 1, cy - 1, YELL, 3.4, lit=0)
    cv.put(cx, cy + 1, REDP, 4.4, lit=0)
    for wx in (-1, 1):                                               # bigotis
        cv.put(cx + wx * 7, cy + 1, WHITEP, 3.0, lit=0)
        cv.put(cx + wx * 8, cy, WHITEP, 2.4, lit=0)
    cv.ring(cx, cy, 7, WHITEP, 3.4, step=8)                          # la vora blanca de l'adhesiu


def engine_door(cv):
    """La porta estanca de la sala de màquines, tancada, amb el rètol i el senyal d'orelleres."""
    x0, y0, x1, y1 = MAQUINES
    sota.door_frame(cv, x0, y0, x1, y1, ramp=WALL, lvl=4.4, r=12)
    sota.wt_leaf(cv, x0 + 1, y0 + 1, x1 - 1, y1 - 9, ramp=ENG, lvl=3.0, r=11)
    sota.sill(cv, x0, x1, y1)
    for dx, dy in ((x0 - 7, 112), (x0 - 7, 165), (x1 + 4, 112), (x1 + 4, 165)):   # palanques del marc
        box(cv, dx, dy, dx + 3, dy + 8, CAB, 3.4)
        cv.put(dx + 1, dy + 1, CAB, 5.0)
    sota.centered_sign(cv, (x0 + x1) // 2, 64, 'MÀQUINES', ramp=YELL, lvl=4.2)
    # senyal blau d'orelleres, a la fulla, i el de prohibit el pas sense autorització
    cx, cy = (x0 + x1) // 2, 112
    cv.disc(cx, cy, 8, 8, [(10, 20, 60), (20, 50, 120), (40, 80, 170), (90, 130, 210)], 2.6)
    cv.ring(cx, cy, 8, WHITEP, 4.6, step=8)
    for a in range(200, 341, 10):
        cv.put(cx + round(math.cos(math.radians(a)) * 5), cy + round(math.sin(math.radians(a)) * 5), WHITEP, 4.6)
    cv.rect(cx - 6, cy - 2, cx - 4, cy + 3, WHITEP, 4.6)
    cv.rect(cx + 4, cy - 2, cx + 6, cy + 3, WHITEP, 4.6)
    sota.centered_sign(cv, cx, 128, 'NOMÉS TRIP.', ramp=WHITEP, lvl=3.8, pad=2, screws=False)
    # una mica de llum per sota de la porta (a dins sempre hi ha llum)
    cv.hline(x0 + 8, x1 - 8, y1 - 9, YELL, 2.2, lit=0)
    cv.hline(x0 + 10, x1 - 10, y1 - 10, YELL, 1.2, lit=0)


def store_door(cv):
    """La porta del pallol: de planxa amb nervis, frontisses i la balda oberta amb el cadenat penjat."""
    x0, y0, x1, y1 = PALLOL
    sota.door_frame(cv, x0, y0, x1, y1, ramp=WALL, lvl=4.2, r=8)
    rrect(cv, x0, y0, x1, y1 - 9, 7, CAB, lambda x, y: 3.4 - (y - y0) * 0.005)
    for y in range(y0 + 11, y1 - 13, 8):                                # nervis horitzontals
        cv.hline(x0 + 5, x1 - 5, y, CAB, 4.2)
        cv.hline(x0 + 5, x1 - 5, y + 1, CAB, 2.4)
    sota.sill(cv, x0, x1, y1)
    for hy in (y0 + 16, y1 - 29):                                       # frontisses
        box(cv, x0 - 3, hy, x0 + 3, hy + 11, CAB, 4.0)
        cv.put(x0, hy + 2, CAB, 5.4)
        cv.put(x0, hy + 8, CAB, 5.4)
    # la balda, oberta, i el cadenat obert, penjat de la grapa: l'arc fora del cos (s'hi entra sense res)
    box(cv, x1 - 19, 131, x1 - 11, 139, CAB, 4.4)                       # la placa de la grapa
    cv.put(x1 - 17, 133, CAB, 2.0)
    cv.put(x1 - 13, 137, CAB, 2.0)
    cv.ring(x1 - 8, 135, 3, CAB, 4.6, step=20)                          # la grapa
    box(cv, x1 - 4, 128, x1 - 1, 149, CAB, 3.8)                         # la balda, girada avall
    cv.vline(x1 - 12, 137, 148, BRASS, 3.8)                             # l'arc: la pota llarga, dins el cos
    cv.vline(x1 - 11, 137, 148, BRASS, 2.4)
    cv.hline(x1 - 12, x1 - 8, 136, BRASS, 4.6)
    cv.vline(x1 - 7, 137, 141, BRASS, 4.2)                              # la pota curta, fora
    cv.put(x1 - 7, 142, BRASS, 2.6)
    rrect(cv, x1 - 15, 148, x1 - 5, 158, 2, BRASS, lambda x, y: 4.2 - (x - x1 + 15) * 0.1)
    cv.hline(x1 - 14, x1 - 6, 149, BRASS, 5.2)
    cv.put(x1 - 8, 148, DARK, 1.0)                                      # el forat de l'arc, buit
    cv.put(x1 - 10, 153, DARK, 1.0)                                     # el pany
    cv.put(x1 - 10, 154, DARK, 1.6)
    cv.put(x1 - 10, 155, DARK, 1.6)
    sota.centered_sign(cv, (x0 + x1) // 2, 67, 'PALLOL')


# ─── Detalls de paret ───────────────────────────────────────────────────────

def extinguisher(cv):
    x0 = 245
    box(cv, x0 - 3, 101, x0 + 19, 109, WHITEP, 4.0)                     # rètol de l'extintor
    cv.rect(x0, 103, x0 + 16, 107, REDP, 3.6)
    cv.poly([(x0 + 2, 106), (x0 + 5, 103), (x0 + 5, 106)], WHITEP, 4.6)
    for y in range(123, 176):
        for x in range(x0, x0 + 17):
            u = (x - x0 - 8) / 8.5
            cv.put(x, y, REDP, 3.6 + 1.5 * (-0.3 - u) - 0.9 * u * u)
    cv.disc(x0 + 8, 123, 8, 4, REDP, lambda nx, ny: 4.2 - nx - ny)
    box(cv, x0 + 4, 112, x0 + 12, 120, CAB, 3.6)
    cv.disc(x0 + 13, 115, 3, 3, [(40, 40, 40), (140, 140, 140), (220, 220, 220)], 2.6)   # el manòmetre
    cv.put(x0 + 13, 114, [(10, 120, 40), (40, 200, 80)], 1.4, lit=0)
    cv.line(x0 + 12, 113, x0 + 20, 110, CAB, 3.8)                       # la maneta
    cv.line(x0 + 4, 120, x0 - 3, 147, DARK, 2.6)                        # la mànega
    cv.line(x0 + 5, 120, x0 - 2, 147, DARK, 1.4)
    cv.rect(x0, 139, x0 + 16, 151, WHITEP, 3.8)                         # etiqueta
    text(cv, 'POLS', x0 + 1, 141, None, 0, flat=(40, 20, 20))
    cv.hline(x0 + 3, x0 + 13, 148, DARK, 1.6)
    box(cv, x0 - 1, 171, x0 + 17, 176, CAB, 3.0)                        # suport


def notice(cv):
    """El tauler de suro amb el torn de guàrdies, el plànol d'evacuació i un avís."""
    x0, y0, x1, y1 = 101, 93, 139, 144
    box(cv, x0, y0, x1, y1, WALNUT, 3.2)
    CORK = [(40, 34, 20), (80, 64, 40), (120, 98, 64), (150, 128, 90)]
    for y in range(y0 + 2, y1 - 1):
        for x in range(x0 + 2, x1 - 1):
            cv.put(x, y, CORK, 2.4 + (hr(x, y, 12) - 0.5) * 1.0)
    box(cv, x0 + 5, y0 + 5, x0 + 20, y0 + 27, PAPER, 4.0)              # guàrdies (una graella)
    for y in range(y0 + 9, y0 + 26, 3):
        cv.hline(x0 + 7, x0 + 18, y, PAPER, 1.6)
    cv.vline(x0 + 11, y0 + 8, y0 + 25, PAPER, 2.0)
    box(cv, x0 + 21, y0 + 8, x1 - 5, y0 + 32, [(14, 40, 20), (30, 80, 40), (60, 130, 70), (150, 200, 150)], 2.6)
    cv.rect(x0 + 24, y0 + 13, x1 - 8, y0 + 18, WHITEP, 3.6)             # plànol (verd, sortides)
    cv.line(x0 + 25, y0 + 27, x1 - 9, y0 + 27, WHITEP, 3.6)
    cv.put(x1 - 10, y0 + 22, REDP, 4.4, lit=0)                          # «sou aquí»
    box(cv, x0 + 8, y0 + 31, x0 + 27, y1 - 6, PAPER, 3.8)
    for y in range(y0 + 35, y1 - 7, 3):
        cv.hline(x0 + 10, x0 + 25 - (3 if hr(y, 3) > 0.6 else 0), y, PAPER, 1.6)
    for px, py in ((x0 + 12, y0 + 6), (x0 + 29, y0 + 9), (x0 + 17, y0 + 32)):
        cv.put(px, py, REDP, 4.4)
        cv.put(px + 1, py + 1, REDP, 2.0)


def ladder_sign(cv):
    """Rètol de sortida (verd) cap a l'escala, amb la fletxa."""
    box(cv, 483, 78, 533, 89, SEAG, 3.6)
    text(cv, 'SORTIDA', 487, 81, None, 0, flat=(220, 240, 226))
    cv.hline(518, 526, 83, WHITEP, 4.6, lit=0)                          # la fletxa, cap a l'escala
    for i in range(4):
        cv.vline(529 - i, 83 - i, 83 + i, WHITEP, 4.6, lit=0)
    glow(cv, 507, 83, 16, (90, 255, 140), 0.3)


def alarms(cv):
    """El repetidor d'alarmes de la sala de màquines, sota el tauler de suro: quatre llums, tots en verd."""
    x0, y0, x1, y1 = 101, 150, 139, 183
    box(cv, x0, y0, x1, y1, ENG, 3.0, grad=0.6)
    cv.hline(x0 + 1, x1 - 1, y0 + 1, ENG, 4.6)
    cv.rect(x0 + 3, y0 + 3, x1 - 3, y0 + 8, WHITEP, 3.4)                  # la placa del títol
    w = text_width('ALARMES')
    text(cv, 'ALARMES', (x0 + x1) // 2 - w // 2, y0 + 4, None, 0, flat=(40, 30, 30))
    for i in range(4):                                                  # sentina, incendi, gasoil, temperatura
        y = y0 + 13 + i * 5
        cv.flat(x0 + 6, y, (70, 230, 110))
        cv.flat(x0 + 7, y, (40, 190, 80))
        glow(cv, x0 + 6, y, 3, (80, 255, 130), 0.35)
        cv.hline(x0 + 11, x1 - 6 - (i % 2) * 5, y, WHITEP, 2.2)          # l'etiqueta de cada llum
    cv.disc(x1 - 7, y1 - 5, 2, 2, REDP, lambda nx, ny: 3.8 - nx - ny)     # el botó de prova
    cv.put(x1 - 7, y1 - 9, WHITEP, 3.0)
    for bx, by in ((x0 + 2, y0 + 2), (x1 - 2, y0 + 2), (x0 + 2, y1 - 2), (x1 - 2, y1 - 2)):
        cv.put(bx, by, ENG, 5.4)


def petjades(cv):
    """Escena 1: les petjades mullades d'en Diu, que van i vénen entre la porta del camarot i la de màquines."""
    def paw(x, y, k):
        # aigua damunt la planxa fosca: brilla amb la llum dels llums de gàbia
        for dx, dy in ((0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1), (-1, -2), (1, -3), (3, -2)):
            px, py = x + dx, y + dy
            cv.flat(px, py, mix(cv.get(px, py), (120, 156, 160), k))
        cv.flat(x + 1, y, mix(cv.get(x + 1, y), (200, 228, 228), k))
    for i in range(9):                                                   # anada (a prop de la paret)
        t = i / 8
        x = round(78 + (180 - 78) * t)
        paw(x + (0 if i % 2 else 3), 210 + (i % 2) * 3, 0.5 - t * 0.12)
    for i in range(8):                                                   # tornada (més endavant, més seca)
        t = i / 7
        x = round(176 - (176 - 84) * t)
        paw(x + (2 if i % 2 else 0), 218 + (i % 2) * 3, 0.42 - t * 0.14)


# ─── L'escala cap a la coberta principal ───────────────────────────────────

def stair(cv):
    """Escala de vaixell (inclinada, de graons plans i passamans) que puja per un forat del sostre."""
    cv.rect(533, 0, W - 1, 27, CREAM, lambda x, y: 2.6 + (27 - y) * 0.04, lit=0.6)
    for x in range(533, W):
        if x % 29 == 0:
            cv.vline(x, 0, 27, CREAM, 1.6, lit=0.4)
    cv.hline(533, W - 1, 27, CAB, 1.0)
    cv.hline(533, W - 1, 28, CAB, 3.4)
    box(cv, 528, 0, 536, 31, ENG, 2.6)                                  # la brazola del forat
    for y in (6, 18, 28):
        cv.put(532, y, ENG, 4.6)
    cv.darken(539, 29, W - 1, FLOOR_Y - 1, lambda x, y: 0.18)            # la paret de darrere, més fosca
    # zancs i graons
    bx0, by0, bx1, by1 = 539, FLOOR_Y + 3, 627, 13
    n = 17
    for i in range(1, n):
        t = i / n
        x = bx0 + (bx1 - bx0) * t
        y = by0 + (by1 - by0) * t
        box(cv, int(x) - 13, int(y) - 1, int(x) + 16, int(y) + 3, CAB, 3.4)
        for k in range(-11, 15, 3):                                    # antilliscant
            cv.put(int(x) + k, int(y), CAB, 4.6)
        cv.hline(int(x) - 12, int(x) + 15, int(y) + 3, CAB, 1.6)
        cv.hline(int(x) - 10, int(x) + 13, int(y) + 1, YELL, 3.0)       # la vora pintada de groc
    for off, lvl in ((-17, 3.6), (17, 4.2)):
        for w in range(4):
            cv.line(bx0 + off + w, by0, bx1 + off + w, by1, ENG, lvl + (1.0 if w == 0 else -0.6 if w == 3 else 0))
    # passamans, de tub
    for off in (-19, 20):
        cv.line(bx0 + off, by0 - 40, bx1 + off, by1 - 40, BRASS, 3.6)
        cv.line(bx0 + off, by0 - 39, bx1 + off, by1 - 39, BRASS, 2.0)
    for t in (0.12, 0.55):
        x = bx0 + (bx1 - bx0) * t
        y = by0 + (by1 - by0) * t
        for off in (-19, 20):
            cv.vline(int(x) + off, int(y) - 40, int(y), BRASS, 2.8)


# ─── L'escotilla de la sala de bombes ──────────────────────────────────────

def hatch(cv):
    cv.poly([(395, 221), (485, 221), (495, 252), (385, 252)], DARK, 1.2)
    for y in range(221, 253):
        t = (y - 221) / 31
        xa, xb = 395 - 10 * t, 485 + 10 * t
        for x in range(int(xa), int(xb) + 1):
            if ((x + y) // 5) % 2 == 0:
                cv.put(x, y, YELL, 3.2 - (0.8 if hr(x, y, 21) > 0.9 else 0))     # gastada pels peus
    # la tapa (planxa estriada, una mica més clara)
    cv.poly(HATCH, DECK, lambda x, y: 3.6 + (0.9 if ((x // 2 + y) % 4 == 0) else 0))
    cv.line(400, 224, 480, 224, DECK, 5.2)
    cv.line(392, 248, 488, 248, DECK, 1.0)
    for bx, by in ((403, 227), (477, 227), (397, 245), (483, 245)):      # cargols dels cantons
        cv.put(bx, by, DECK, 5.6)
    for hx in (411, 464):                                               # frontisses (a baix)
        box(cv, hx, 247, hx + 8, 251, CAB, 3.8)
        cv.put(hx + 4, 249, CAB, 1.4)
    rrect(cv, 432, 232, 448, 239, 2, CAB, 1.6)                          # la nansa encastada
    cv.hline(435, 445, 235, CAB, 4.4)
    cv.hline(435, 445, 236, CAB, 2.4)
    # el rètol a la paret, amb la fletxa avall
    sota.centered_sign(cv, 440, 157, 'BOMBES', ramp=WHITEP, lvl=4.0)
    cv.vline(440, 172, 184, WHITEP, 3.6)
    cv.vline(441, 172, 184, WHITEP, 2.4)
    cv.poly([(435, 183), (446, 183), (440, 189)], WHITEP, 3.6)


# ─── Muntatge ───────────────────────────────────────────────────────────────

def bg(cv):
    walls(cv)
    notice(cv)
    alarms(cv)
    cabin_door(cv)
    engine_door(cv)
    store_door(cv)
    extinguisher(cv)
    ladder_sign(cv)
    sota.checker_floor(cv)
    hatch(cv)
    stair(cv)
    for lx in LAMPS:
        sota.cage_lamp(cv, lx, LAMP_Y)
    for lx in LAMPS:
        sota.lamp_glow(cv, lx, LAMP_Y)
    glow(cv, 587, 16, 53, (255, 236, 190), 0.35)


PROPS = {'petjades': petjades}


# ─── Animacions ─────────────────────────────────────────────────────────────
# Totes dues fan servir sota.fast_diff i només calculen els fotogrames que canvien: la resta comparteixen
# la mateixa imatge buida.

@lru_cache(maxsize=None)
def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv.img


def _frames_llum():
    """El llum de gàbia de la dreta fa mal contacte: de tant en tant baixa dues vegades i torna."""
    base = _base()
    lx, ly = LAMPS[1], LAMP_Y + 5
    dims = {38: 0.55, 39: 0.25, 41: 0.6, 42: 0.35}              # fotograma → quant s'apaga
    area = (lx - 175, 0, min(W, lx + 175), FLOOR_Y + 45)
    empty = Image.new('RGBA', base.size, (0, 0, 0, 0))
    frames = []
    for i in range(48):
        k = dims.get(i, 0)
        if not k:
            frames.append(empty)
            continue
        cv = Canvas(light=LIGHT, img=base.copy())
        cv.darken(area[0], area[1], area[2] - 1, area[3] - 1,
                  lambda x, y: k * max(0.0, 1 - math.hypot(x - lx, (y - ly) * 1.1) / 173), dither=False)
        cv.darken(lx - 11, ly - 5, lx + 11, ly + 16, min(0.85, k * 1.4), dither=False)
        frames.append(sota.fast_diff(cv.img, base, area))
    return frames


def _frames_gota():
    """Una gota de condensació que es forma sota el tub de gasoil, cau a terra i hi fa una rodoneta."""
    base = _base()
    gx, top, ground = 389, 65, 211
    seq = [('f', 0)] * 3 + [('f', 1)] * 3 + [('f', 2)] * 2 + [('f', 3)] * 2
    y, v = top + 4, 1.3
    while y < ground:
        seq.append(('c', int(y)))
        y, v = y + v, v + 2.1
    seq += [('s', 0), ('r', 1), ('r', 2), ('r', 3), ('r', 4), ('r', 5)] + [('n', 0)] * 40
    area = (gx - 14, top - 1, gx + 15, ground + 6)
    empty = Image.new('RGBA', base.size, (0, 0, 0, 0))
    frames = []
    for kind, v in seq:
        if kind == 'n':
            frames.append(empty)
            continue
        cv = Canvas(light=LIGHT, img=base.copy())
        if kind == 'f':                                             # la gota s'infla sota el tub
            for k in range(v + 1):
                cv.flat(gx, top + k, mix(cv.get(gx, top + k), (150, 190, 185), 0.7))
            if v >= 2:
                cv.flat(gx - 1, top + v - 1, mix(cv.get(gx - 1, top + v - 1), (130, 170, 165), 0.4))
                cv.flat(gx + 1, top + v - 1, mix(cv.get(gx + 1, top + v - 1), (130, 170, 165), 0.4))
        elif kind == 'c':                                           # cau (amb una cua)
            cv.flat(gx, v, (190, 222, 216))
            cv.flat(gx, v + 1, (170, 205, 200))
            cv.flat(gx, v - 1, mix(cv.get(gx, v - 1), (130, 170, 165), 0.5))
            cv.flat(gx, v - 2, mix(cv.get(gx, v - 2), (130, 170, 165), 0.25))
        elif kind == 's':                                           # l'esquitx
            for dx, dy in ((-2, -2), (2, -2), (-3, -1), (3, -1), (0, -3)):
                cv.flat(gx + dx, ground + dy, (180, 215, 210))
        else:                                                       # la rodoneta que s'eixampla
            for a in range(0, 360, 18):
                x = gx + round(math.cos(math.radians(a)) * v * 2.4)
                yy = ground + round(math.sin(math.radians(a)) * v * 0.6)
                cv.flat(x, yy, mix(cv.get(x, yy), (150, 190, 185), 0.6 - v * 0.08))
        frames.append(sota.fast_diff(cv.img, base, area))
    return frames


ANIMS = {'llum': {'frames': _frames_llum, 'frameDuration': 110},
         'gota': {'frames': _frames_gota, 'frameDuration': 80}}


# ─── Geometria (coordenades de 640×360) ─────────────────────────────────────
