#!/usr/bin/env python3
"""
Aigua bruta — art final de mostra: la sala de màquines de l'Arenga (Escena 1), a les quatre menys vint de la
matinada.

Fa servir les eines de pixel art HD de Suma Zero (llenç de 480×270, rampes, llums, dithering i personatges amb
volum), per provar com quedaria el tercer joc amb el mateix motor:

  - el motor principal parat, verd de sala de màquines, amb el col·lector d'escapament folrat on dorm en Diu;
  - dos dits d'aigua a terra, amb els reflexos dels llums de gàbia;
  - la vàlvula de presa de mar sense volant, el quadre amb la bomba de sentina lligada amb una brida,
    l'alarma desconnectada, el separador d'aigües oleoses i la vàlvula de tres vies (BORDA / SEPARADOR);
  - la boca del tub de veu de llautó i el cartell de «no abocar res al mar»;
  - l'Iri i en Bastida (personatges.py); la cara de la Vet, al botó «Canvia»;
  - una barra de verbs nàutica (mateixa geometria que la de Suma Zero) amb el botó «Canvia» amb la cara de la Vet.

Ús: python3 sala_maquines.py
Surt, al costat d'aquest fitxer:
  sala-maquines.png       el fons sol (480×270)
  sala-maquines-joc.png   la maqueta de pantalla de joc, ×2 (960×540)
"""
import math
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
GAMES = HERE.parents[3]
sys.path.insert(0, str(GAMES / 'suma-zero/adapters/benne/tools'))
sys.path.insert(0, str(GAMES / 'suma-zero/tools/font'))

from hd.pix import Canvas, Light, W, H, hr, mix, GOLD, RUST, B4  # noqa: E402
from hd.personatges import diu  # noqa: E402
import personatges  # noqa: E402
import suma_font  # noqa: E402

# ─── Rampes (fosc → clar) ───────────────────────────────────────────────────
WALL = [(5, 10, 11), (9, 18, 18), (14, 27, 26), (21, 38, 35), (30, 51, 46), (41, 66, 58), (55, 84, 72),
        (73, 104, 88), (96, 128, 108), (126, 154, 132)]
ENG = [(6, 10, 15), (11, 17, 25), (18, 26, 36), (27, 37, 49), (38, 51, 65), (52, 68, 84), (70, 89, 106),
       (93, 114, 130), (122, 142, 156), (160, 176, 186)]
ENG_LIGHT = [(10, 15, 22), (18, 26, 36), (27, 37, 50), (38, 51, 66), (52, 68, 86), (68, 88, 108),
             (88, 110, 130), (112, 134, 152), (142, 162, 176), (180, 194, 202)]
DECK = [(5, 7, 9), (10, 12, 16), (17, 20, 25), (26, 30, 36), (37, 42, 49), (51, 56, 64), (69, 74, 82),
        (92, 97, 104)]
CAB = [(8, 10, 12), (15, 17, 21), (24, 27, 32), (35, 39, 45), (49, 54, 60), (66, 71, 77), (88, 93, 98),
       (116, 120, 124), (150, 154, 156)]
LAG = [(36, 32, 30), (62, 56, 50), (94, 86, 74), (128, 118, 100), (162, 150, 126), (194, 182, 154),
       (222, 212, 186), (240, 234, 214)]
REDP = [(28, 6, 8), (56, 12, 14), (90, 20, 20), (130, 30, 28), (170, 48, 38), (206, 78, 56), (236, 122, 90)]
YELL = [(36, 28, 6), (78, 58, 10), (128, 96, 16), (178, 136, 24), (218, 174, 42), (244, 210, 88)]
SEAG = [(6, 22, 16), (10, 38, 28), (16, 58, 42), (26, 82, 58), (40, 108, 76), (62, 138, 98)]
FUEL = [(26, 14, 8), (48, 26, 12), (76, 42, 18), (106, 62, 26), (138, 86, 38), (170, 114, 56)]
SEP = [(30, 28, 18), (56, 52, 34), (88, 82, 54), (122, 114, 78), (156, 148, 104), (188, 180, 134),
       (216, 210, 168), (236, 232, 200)]
DARK = [(2, 3, 5), (5, 7, 10), (9, 12, 16), (14, 18, 23), (20, 25, 31), (28, 34, 41)]
WHITEP = [(40, 42, 46), (80, 84, 88), (130, 134, 136), (180, 182, 180), (214, 214, 208), (236, 236, 228)]
BRASS = GOLD
WARM = (255, 214, 140)
RED_GLOW = (255, 60, 40)

FLOOR_Y = 152          # on la paret es troba amb el terra
BOTTOM = 195           # per sota hi ha la franja de la frase i la barra de verbs
LAMPS = ((160, 22), (372, 22))

LIGHT = Light(ambient=-0.5, vignette=(56, 30), floor_fade=None)
LIGHT.point(160, 26, r=158, k=2.6, squash=1.05, down=True, power=1.5)
LIGHT.point(372, 26, r=146, k=2.4, squash=1.05, down=True, power=1.5)
LIGHT.point(36, 60, r=40, k=0.7, power=2.0)                 # llum d'emergència, sobre la porta
LIGHT.point(446, 120, r=40, k=0.5, power=2.0)               # el panell del separador


# ─── Ajudes ─────────────────────────────────────────────────────────────────

def box(cv, x0, y0, x1, y1, ramp, lvl, edge=True, grad=0.0):
    """Capsa plana amb vora: llum a dalt i a l'esquerra, ombra a baix i a la dreta."""
    cv.rect(x0, y0, x1, y1, ramp, lambda x, y: lvl - grad * (y - y0) / max(1, y1 - y0))
    if edge:
        cv.hline(x0, x1, y0, ramp, lvl + 1.2)
        cv.vline(x0, y0, y1, ramp, lvl + 0.7)
        cv.hline(x0, x1, y1, ramp, lvl - 1.4)
        cv.vline(x1, y0, y1, ramp, lvl - 1.0)


def rrect(cv, x0, y0, x1, y1, r, ramp, lvl):
    """Rectangle de cantons rodons."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            dx = max(x0 + r - x, 0, x - (x1 - r))
            dy = max(y0 + r - y, 0, y - (y1 - r))
            if dx * dx + dy * dy <= r * r:
                cv.put(x, y, ramp, lvl(x, y) if callable(lvl) else lvl)


def bolt(cv, x, y, ramp, lvl):
    cv.put(x, y, ramp, lvl + 1.4)
    cv.put(x + 1, y + 1, ramp, lvl - 1.2)


def hpipe(cv, x0, x1, yc, r, ramp, lvl, bands=(), band_ramp=None):
    """Tub horitzontal amb volum (cilindre) i anelles de color."""
    for x in range(x0, x1 + 1):
        band = any(b <= x < b + 3 for b in bands)
        for y in range(yc - r, yc + r + 1):
            u = (y - yc) / (r + 0.5)
            shade = 1.4 * (0.35 - u) - 0.6 * u * u
            cv.put(x, y, band_ramp if band else ramp, lvl + shade)


def vpipe(cv, xc, y0, y1, r, ramp, lvl, bands=(), band_ramp=None):
    for y in range(y0, y1 + 1):
        band = any(b <= y < b + 3 for b in bands)
        for x in range(xc - r, xc + r + 1):
            u = (x - xc) / (r + 0.5)
            shade = 1.4 * (-0.2 - u) - 0.6 * u * u
            cv.put(x, y, band_ramp if band else ramp, lvl + shade)


def glow(cv, x, y, r, col, k):
    cv.glow(x, y, r, col, k)


# ─── La paret i el sostre ───────────────────────────────────────────────────

def wall(cv):
    for y in range(0, FLOOR_Y):
        for x in range(W):
            lvl = 3.1 + (hr(x // 3, y // 5) - 0.5) * 0.35
            if y >= 134:                                   # sòcol, més fosc i gastat
                lvl -= 0.9 + (0.3 if hr(x // 6, y // 3) > 0.8 else 0)
            cv.put(x, y, WALL, lvl)
    # costelles (quadernes) cada 64 px, amb reblons
    for fx in range(-8, W, 64):
        for x in range(fx, fx + 6):
            for y in range(20, FLOOR_Y):
                d = (x - fx)
                cv.put(x, y, WALL, 3.5 + (0.9 if d == 0 else 0.5 if d == 1 else -0.3 if d >= 4 else 0.1)
                       - (0.8 if y >= 134 else 0))
        for y in range(28, 132, 12):
            bolt(cv, fx + 2, y, WALL, 3.6)
    # soldadures horitzontals
    for sy in (64, 112):
        for x in range(W):
            cv.put(x, sy, WALL, 1.8)
            cv.put(x, sy + 1, WALL, 3.9 if hr(x // 2, sy) > 0.3 else 3.2)
    cv.hline(0, W - 1, 134, WALL, 4.0)
    cv.hline(0, W - 1, FLOOR_Y - 1, WALL, 1.0)
    # ratlles de rovell que baixen dels reblons i de les soldadures
    for i in range(26):
        x = int(hr(i, 7) * W)
        y0 = 66 if hr(i, 8) > 0.5 else 114
        n = 6 + int(hr(i, 9) * 18)
        for y in range(y0, min(FLOOR_Y - 2, y0 + n)):
            k = 0.55 * (1 - (y - y0) / n)
            if k > B4[y & 3][x & 3] * 0.6:
                o = cv.get(x, y)
                cv.flat(x, y, mix(o, RUST[3], k))


def ceiling(cv):
    cv.rect(0, 0, W - 1, 19, DARK, 2.0)
    for bx in range(-8, W, 64):                        # baos
        box(cv, bx - 2, 0, bx + 8, 21, ENG, 1.6, grad=0.6)
    for y in (6, 13):                                  # safates de cables
        cv.hline(0, W - 1, y, CAB, 2.8)
        cv.hline(0, W - 1, y + 4, CAB, 1.6)
        for x in range(0, W, 5):
            cv.vline(x, y, y + 4, CAB, 2.2)
        for x in range(W):
            if hr(x // 9, y) > 0.35:
                cv.flat(x, y + 2, [(20, 20, 24), (40, 36, 30), (70, 50, 34), (110, 40, 34)][int(hr(x // 11, y) * 4)])


def wall_pipes(cv):
    # aigua de mar (verd, amb anelles blanques) i gasoil (marró)
    hpipe(cv, 58, W - 1, 40, 3, SEAG, 3.0, bands=range(70, W, 46), band_ramp=WHITEP)
    hpipe(cv, 58, W - 1, 51, 2, FUEL, 3.0, bands=range(92, W, 46), band_ramp=YELL)
    for x in range(64, W, 48):                         # abraçadores
        cv.vline(x, 35, 45, CAB, 2.0)
        cv.vline(x + 1, 35, 45, CAB, 3.4)
        cv.vline(x, 48, 54, CAB, 2.0)
    vpipe(cv, 64, 40, FLOOR_Y + 2, 3, SEAG, 2.8, bands=(86, 126), band_ramp=WHITEP)
    hpipe(cv, 58, 64, 40, 3, SEAG, 3.0)


def lamps(cv):
    for lx, ly in LAMPS:
        box(cv, lx - 6, 16, lx + 6, 20, CAB, 3.0)
        cv.disc(lx, ly + 3, 6, 4, [(120, 90, 40), (200, 160, 80), (250, 220, 150), (255, 246, 220)], 2.6, lit=0)
        for gx in (-4, 0, 4):                          # la gàbia
            cv.vline(lx + gx, ly, ly + 7, CAB, 2.2, lit=0)
        cv.hline(lx - 6, lx + 6, ly + 4, CAB, 2.0, lit=0)


# ─── La porta estanca i el racó de l'esquerra ──────────────────────────────

def door(cv):
    x0, y0, x1, y1 = 14, 66, 56, FLOOR_Y
    # el passadís, fosc, amb un llum llunyà
    for y in range(y0, y1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, DARK, 1.6 - abs(x - 35) / 30 + (0.9 if y > 132 else 0) - (y - y0) / 120, lit=0.3)
    cv.disc(35, 76, 3, 1.5, [(80, 70, 50), (160, 140, 100)], 1.4, lit=0)
    glow(cv, 35, 78, 12, (140, 130, 100), 0.35)
    # marc (cantons rodons)
    r = 9
    for t in range(3):
        for y in range(y0 - t, y1 + 1):
            for x in range(x0 - t, x1 + t + 1):
                dx = max(x0 - t + r - x, 0, x - (x1 + t - r))
                dy = max(y0 - t + r - y, 0, 0)
                inside = dx * dx + dy * dy <= r * r
                inner = x0 - t + 1 <= x <= x1 + t - 1 and y >= y0 - t + 1
                ddx = max(x0 - t + 1 + r - x, 0, x - (x1 + t - 1 - r))
                ddy = max(y0 - t + 1 + r - y, 0)
                if inside and not (inner and ddx * ddx + ddy * ddy <= r * r):
                    cv.put(x, y, WALL, 4.2 - t * 0.9)
    cv.rect(x0 + 1, y1 - 6, x1 - 1, y1 - 1, WALL, 2.6)    # el llindar alt (no entra l'aigua)
    cv.hline(x0 + 1, x1 - 1, y1 - 6, WALL, 4.0)
    # la fulla, oberta contra la paret (de cantó)
    cv.poly([(4, y0 + 4), (12, y0 - 1), (12, y1 - 2), (4, y1 - 4)], ENG, lambda x, y: 2.8 - (x - 4) * 0.06)
    for y in range(y0 + 10, y1 - 8, 22):
        box(cv, 6, y, 10, y + 3, ENG, 3.6)
    # «dogs»: les palanques de tancament, al voltant del marc
    for dx, dy in ((x0 - 4, 84), (x0 - 4, 124), (x1 + 2, 84), (x1 + 2, 124)):
        box(cv, dx, dy, dx + 2, dy + 6, CAB, 3.4)
    # llum d'emergència, vermell
    box(cv, 29, 56, 41, 61, CAB, 2.6)
    cv.disc(35, 59, 5, 2.5, REDP, 4.6, lit=0)
    # cartell verd de sortida
    box(cv, 22, 46, 48, 52, SEAG, 3.4, edge=False)
    for x in range(24, 46, 3):
        cv.put(x, 49, WHITEP, 4.0, lit=0)
        cv.put(x + 1, 49, WHITEP, 4.0, lit=0)


def voice_tube(cv):
    """La boca del tub de veu: tub de llautó del sostre, campana i tapa amb cadeneta."""
    vpipe(cv, 100, 20, 104, 2, BRASS, 2.8)
    for y in (34, 74):
        box(cv, 97, y, 103, y + 2, CAB, 3.2)
    # colze i campana mirant endavant
    cv.disc(100, 108, 4, 4, BRASS, lambda nx, ny: 3.2 - nx * 1.2 - ny * 1.0)
    cv.disc(100, 112, 7, 6, BRASS, lambda nx, ny: 3.5 - nx * 1.3 - ny * 1.2)
    cv.disc(100, 112, 5, 4, BRASS, lambda nx, ny: 1.2 + nx * 0.6 + ny * 0.8)
    cv.disc(100, 112, 3, 2, DARK, 0.6)
    # la tapa penjant d'una cadeneta
    for i, y in enumerate(range(119, 127)):
        cv.put(104 + (i % 2), y, BRASS, 3.0)
    cv.disc(106, 129, 3, 2, BRASS, 3.6)
    # plaqueta
    box(cv, 92, 134, 108, 138, BRASS, 3.0)
    for x in range(94, 107, 2):
        cv.put(x, 136, BRASS, 1.4)


def marpol(cv):
    """Cartell: és prohibit abocar hidrocarburs al mar (el típic de les sales de màquines)."""
    x0, y0, x1, y1 = 70, 96, 90, 126
    box(cv, x0, y0, x1, y1, WHITEP, 4.0)
    cv.rect(x0 + 1, y0 + 1, x1 - 1, y0 + 6, [(20, 30, 70), (30, 50, 110), (50, 80, 150), (90, 120, 190)], 2.2)
    # un vaixell i una gota ratllada
    cv.disc(80, y0 + 13, 3, 3, REDP, 4.2)
    cv.disc(80, y0 + 13, 2, 2, WHITEP, 4.6)
    cv.disc(80, y0 + 13, 1, 1, DARK, 1.0)
    for i in range(-3, 4):
        cv.put(80 + i, y0 + 13 + i, REDP, 4.2)
    for y in range(y0 + 19, y1 - 1, 2):
        for x in range(x0 + 2, x1 - 1):
            if hr(x // 3, y) > 0.25:
                cv.put(x, y, WHITEP, 1.6)
    for x, y in ((x0 + 1, y0 + 1), (x1 - 1, y0 + 1), (x0 + 1, y1 - 1), (x1 - 1, y1 - 1)):
        cv.put(x, y, CAB, 2.0)


# ─── El motor principal ─────────────────────────────────────────────────────

def engine(cv, ENG=ENG_LIGHT):
    # bancada
    box(cv, 114, 140, 324, FLOOR_Y + 3, ENG, 2.0, grad=0.6)
    for x in range(120, 322, 14):
        bolt(cv, x, 144, ENG, 2.6)
    # càrter, amb portes d'inspecció
    box(cv, 124, 100, 314, 140, ENG, 3.0, grad=0.8)
    cv.hline(124, 314, 101, ENG, 4.1)
    for i in range(6):
        dx = 132 + i * 30
        rrect(cv, dx, 107, dx + 21, 131, 5, ENG, lambda x, y: 3.5 - (y - 107) * 0.03)
        rrect(cv, dx + 2, 109, dx + 19, 129, 4, ENG, lambda x, y: 2.9 - (y - 109) * 0.03)
        for bx, by in ((dx + 3, 110), (dx + 17, 110), (dx + 3, 127), (dx + 17, 127), (dx + 10, 108), (dx + 10, 129)):
            bolt(cv, bx, by, ENG, 3.4)
    # bloc de cilindres i culates
    box(cv, 128, 84, 302, 100, ENG, 3.3, grad=0.5)
    for i in range(6):
        dx = 131 + i * 28
        rrect(cv, dx, 72, dx + 23, 86, 4, ENG, lambda x, y: 4.1 - (y - 72) * 0.07)
        cv.hline(dx + 4, dx + 19, 73, ENG, 5.2)
        bolt(cv, dx + 4, 80, ENG, 3.8)
        bolt(cv, dx + 18, 80, ENG, 3.8)
        vpipe(cv, dx + 12, 86, 92, 1, ENG, 2.8)          # injectors
    # col·lector d'escapament folrat (on dorm en Diu) i la xemeneia cap al sostre
    hpipe(cv, 134, 300, 66, 4, LAG, 3.2, bands=range(150, 300, 26), band_ramp=CAB)
    vpipe(cv, 302, 20, 70, 6, LAG, 3.0, bands=range(28, 70, 14), band_ramp=CAB)
    cv.disc(302, 66, 6, 5, LAG, lambda nx, ny: 3.3 - nx - ny)
    # turbo (el cargol)
    cv.disc(314, 88, 13, 13, ENG, lambda nx, ny: 3.6 - nx * 1.4 - ny * 1.2)
    cv.disc(314, 88, 8, 8, ENG, lambda nx, ny: 2.6 + nx * 0.8 + ny * 0.8)
    cv.disc(314, 88, 3, 3, CAB, 4.6)
    # volant amb protecció ratllada groc i negre
    box(cv, 108, 100, 124, 146, ENG, 2.4)
    for y in range(102, 145):
        for x in range(110, 123):
            if ((x + y) // 4) % 2 == 0:
                cv.put(x, y, YELL, 3.6)
            else:
                cv.put(x, y, DARK, 3.0)
    # el panell local, amb tres manòmetres
    box(cv, 262, 104, 296, 126, CAB, 2.4)
    for gx in (270, 279, 288):
        cv.disc(gx, 113, 4, 4, CAB, 1.4)
        cv.disc(gx, 113, 3, 3, WHITEP, 4.6)
        cv.put(gx, 113, DARK, 0)
        cv.line(gx, 113, gx - 2, 115, DARK, 0)            # agulles a zero: el motor és parat
    for x in range(266, 294, 3):
        cv.put(x, 121, WHITEP, 3.0)
    # una placa de llautó
    box(cv, 196, 88, 228, 95, BRASS, 3.2)
    for x in range(199, 226, 2):
        cv.put(x, 91, BRASS, 1.6)


# ─── El quadre, l'alarma i el separador ─────────────────────────────────────

def panel(cv):
    x0, y0, x1, y1 = 334, 62, 410, FLOOR_Y + 2
    box(cv, x0, y0, x1, y1, CAB, 3.4, grad=1.0)
    cv.vline(372, y0 + 2, y1 - 2, CAB, 1.2)               # dues portes
    cv.vline(373, y0 + 2, y1 - 2, CAB, 4.4)
    box(cv, x0 - 2, y0 - 4, x1 + 2, y0, CAB, 3.8)
    # fila d'interruptors (generadors, enllumenat, bombes)
    for i, x in enumerate(range(340, 406, 8)):
        box(cv, x, 70, x + 5, 80, CAB, 2.0)
        cv.rect(x + 2, 72, x + 3, 75, DARK, 0.4)
        cv.put(x + 2, 72, CAB, 5.0)
        cv.rect(x, 82, x + 5, 83, WHITEP, 3.4)            # etiquetes
    # pilots: verds els generadors, un d'ambre
    for x, col in ((344, (90, 240, 120)), (352, (90, 240, 120)), (360, (255, 190, 60))):
        cv.flat(x, 88, col)
        cv.flat(x + 1, 88, col)
        glow(cv, x, 88, 5, col, 0.6)
    # amperímetre
    cv.disc(392, 94, 7, 7, CAB, 1.8)
    cv.disc(392, 94, 6, 6, WHITEP, 4.4)
    for a in range(200, 341, 20):
        cv.put(392 + round(math.cos(math.radians(a)) * 5), 94 + round(math.sin(math.radians(a)) * 5), DARK, 0)
    cv.line(392, 95, 395, 90, REDP, 4.0)
    # l'interruptor de la bomba de sentina, lligat amb una brida blanca (nus Bastida)
    box(cv, 350, 104, 366, 124, CAB, 2.6)
    cv.disc(358, 113, 5, 5, DARK, 1.6)
    cv.rect(357, 106, 359, 116, REDP, 4.2)               # la maneta, en posició OFF
    cv.rect(352, 126, 364, 129, WHITEP, 3.6)               # etiqueta «BOMBA SENTINA»
    for x in range(353, 364, 2):
        cv.put(x, 127, DARK, 1.0)
    BRIDA = [(70, 70, 66), (150, 150, 142), (214, 214, 204), (246, 246, 238)]
    for y in range(108, 117):
        cv.put(355, y, BRIDA, 2.6)
        cv.put(361, y, BRIDA, 2.2)
    cv.hline(355, 361, 108, BRIDA, 3.0)
    cv.hline(355, 368, 116, BRIDA, 2.6)
    for x in range(366, 370):                             # cap a la nansa de la porta
        cv.put(x, 115, BRIDA, 2.6)
    cv.disc(362, 117, 2, 1.5, BRIDA, 3.2)                 # el nus (amb una volta de més)
    cv.put(363, 119, BRIDA, 2.4)
    cv.put(364, 120, BRIDA, 2.0)
    # nanses i panys
    for hx in (368, 377):
        box(cv, hx, 112, hx + 2, 120, CAB, 4.4)
    # rètol groc d'alta tensió
    cv.poly([(391, 128), (397, 138), (385, 138)], YELL, 4.0)
    cv.vline(391, 131, 135, DARK, 0)
    # ventilació a baix
    for y in range(140, 150, 2):
        cv.hline(340, 366, y, CAB, 1.4)
        cv.hline(378, 404, y, CAB, 1.4)


def alarm(cv):
    """L'alarma de sentina, amb el cable del sensor desendollat penjant."""
    box(cv, 414, 70, 426, 84, CAB, 3.2)
    cv.disc(420, 68, 4, 3, REDP, lambda nx, ny: 2.0 - nx - ny)   # llum apagada
    cv.rect(416, 76, 424, 80, WHITEP, 3.0)
    # el cable: surt per baix i fa una panxa fins al connector, que penja
    pts = [(420, 85), (419, 92), (417, 100), (416, 108), (417, 115), (419, 120)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        cv.line(ax, ay, bx, by, DARK, 2.6)
        cv.line(ax + 1, ay, bx + 1, by, CAB, 2.6)
    box(cv, 417, 120, 421, 126, CAB, 3.4)
    cv.put(418, 126, BRASS, 4.0)
    cv.put(420, 126, BRASS, 4.0)
    # la presa, buida, més avall
    box(cv, 414, 136, 422, 142, CAB, 2.8)
    cv.put(417, 139, DARK, 0)
    cv.put(419, 139, DARK, 0)


def separator(cv):
    """El separador d'aigües oleoses: un dipòsit alt, amb visor, manòmetre i la caixa de control."""
    x0, x1, top = 432, 472, 72
    cx, rx = (x0 + x1) / 2, (x1 - x0) / 2
    for y in range(top, FLOOR_Y + 3):
        for x in range(x0, x1 + 1):
            u = (x - cx) / (rx + 0.5)
            cv.put(x, y, SEP, 3.2 + 1.5 * (-0.3 - u) - 0.9 * u * u)
    cv.disc(cx, top, rx, 6, SEP, lambda nx, ny: 3.6 - nx * 1.3 - ny * 1.5)
    for y in (96, 132):                                   # costures
        for x in range(x0, x1 + 1):
            cv.put(x, y, SEP, 1.6)
    # visor: oli marró a dalt, aigua a sota
    box(cv, 438, 84, 443, 126, CAB, 2.6)
    for y in range(86, 125):
        col = FUEL if y < 98 else [(14, 30, 34), (24, 50, 54), (44, 80, 82), (80, 120, 120)]
        cv.put(440, y, col, 3.4 if y < 98 else 2.6, lit=0.4)
        cv.put(441, y, col, 2.6 if y < 98 else 2.0, lit=0.4)
    cv.hline(440, 441, 98, YELL, 4.0, lit=0)
    # manòmetre i caixa de control amb el llum verd (treballa, a poc a poc)
    cv.disc(462, 88, 5, 5, CAB, 2.0)
    cv.disc(462, 88, 4, 4, WHITEP, 4.6)
    cv.line(462, 88, 464, 86, DARK, 0)
    box(cv, 450, 104, 470, 122, CAB, 2.8)
    cv.rect(453, 107, 467, 111, [(6, 30, 14), (12, 70, 30), (40, 150, 70), (120, 240, 140)], 1.6, lit=0)
    for x in range(454, 466, 2):
        cv.put(x, 109, [(6, 30, 14), (40, 150, 70), (160, 255, 180)], 2, lit=0)
    cv.flat(456, 116, (90, 255, 120))
    glow(cv, 456, 116, 6, (90, 255, 120), 0.6)
    cv.flat(462, 116, (60, 30, 20))
    # la canonada de descàrrega: puja de terra, passa per la vàlvula de tres vies i entra al separador
    hpipe(cv, 400, 431, 140, 2, CAB, 3.0)
    vpipe(cv, 404, 140, FLOOR_Y + 6, 2, CAB, 2.8)
    # la sortida a la borda, cap amunt i fora de la sala (la via tancada)
    vpipe(cv, 426, 92, 138, 2, CAB, 2.6)
    hpipe(cv, 426, W - 1, 60, 2, CAB, 2.6)
    vpipe(cv, 426, 60, 92, 2, CAB, 2.6)
    # vàlvula de tres vies, vermella, amb la maneta cap a SEPARADOR
    cv.disc(426, 140, 5, 5, REDP, lambda nx, ny: 3.8 - nx - ny)
    cv.line(426, 140, 432, 146, REDP, 4.6)
    cv.line(427, 140, 433, 146, REDP, 3.2)
    # plaques: BORDA (a dalt, apagada) i SEPARADOR (a la dreta)
    box(cv, 418, 124, 424, 128, WHITEP, 3.0)
    box(cv, 432, 134, 440, 138, YELL, 3.8)


# ─── El terra (planxa estriada), amb dos dits d'aigua ──────────────────────

VP = (240, 40)


def floor(cv):
    mask = [[False] * W for _ in range(H)]
    for y in range(FLOOR_Y, BOTTOM + 12):
        d = y - VP[1]
        for x in range(W):
            u = VP[0] + (x - VP[0]) * 150 / d
            u2 = VP[0] + (x + 1 - VP[0]) * 150 / d
            v = 2400 / d
            lvl = 2.5
            if int(u // 76) != int(u2 // 76):                        # junts entre planxes
                lvl = 1.0
            elif y in (158, 170, 187):
                lvl = 1.1
            elif y in (159, 171, 188):
                lvl = 3.3
            else:
                # estries en rombe
                a, b = int(u * 0.5) % 4, int(v * 1.0) % 4
                if (a == 0 and b in (0, 1)) or (a == 2 and b in (2, 3)):
                    lvl += 0.9
            cv.put(x, y, DECK, lvl)
            mask[y][x] = True
    return mask


def water(cv, mask):
    """Dos dits d'aigua: tint fosc i verdós, reflex de la paret, ones i les espurnes dels llums."""
    src = cv.img.copy().load()
    WC = (10, 34, 40)
    for y in range(FLOOR_Y, BOTTOM + 12):
        depth = (y - FLOOR_Y) / (BOTTOM - FLOOR_Y)
        for x in range(W):
            if not mask[y][x]:
                continue
            o = cv.get(x, y)
            c = mix(o, WC, 0.38)
            # reflex de la paret (mirall a FLOOR_Y, ondulat)
            sy = 2 * FLOOR_Y - y - 1
            sx = x + round(math.sin(y * 0.9 + x * 0.05) * 1.4)
            if 0 <= sy < FLOOR_Y and 0 <= sx < W:
                k = 0.55 * max(0.0, 1 - depth * 1.3)
                c = mix(c, src[sx, sy][:3], k)
            # ones: guions clars on hi arriba llum
            lit = LIGHT(x, y)
            if math.sin(x * 0.21 + y * 1.9 + math.sin(y * 0.37) * 4) > 0.93 and lit > 0.2 and hr(x // 4, y) > 0.3:
                c = mix(c, (140, 190, 180), min(0.5, 0.18 + lit * 0.12))
            cv.flat(x, y, c)
    # la línia de l'aigua contra la paret
    for x in range(W):
        if mask[FLOOR_Y][x] and hr(x // 5, 5) > 0.55:
            cv.flat(x, FLOOR_Y, mix(cv.get(x, FLOOR_Y), (150, 190, 180), 0.25))
    # els llums reflectits: guionets horitzontals escampats dins d'un con que s'eixampla cap a baix
    for lx, _ in LAMPS:
        for y in range(FLOOR_Y + 3, BOTTOM + 8):
            t = (y - FLOOR_Y) / 46
            wdt = 3 + t * 9
            for x in range(int(lx - wdt * 2), int(lx + wdt * 2) + 1):
                if not (0 <= x < W) or not mask[y][x]:
                    continue
                g = math.exp(-((x - lx) / wdt) ** 2) * (1 - t * 0.55)
                seg = hr(x // (2 + int(t * 4)), y, lx)       # cada guionet, encès o apagat sencer
                if seg < g * 0.55:
                    cv.flat(x, y, mix(cv.get(x, y), WARM, min(0.8, 0.35 + g * 0.5)))
                elif seg < g * 0.9:
                    cv.flat(x, y, mix(cv.get(x, y), WARM, 0.18))


def reflect_obj(cv, mask, x0, x1, top, base, k=0.4):
    """Reflex a l'aigua d'un objecte que toca a terra a `base` (només sobre el terra)."""
    src = cv.img.copy().load()
    for y in range(base + 1, min(BOTTOM + 12, base + (base - top) + 1)):
        sy = 2 * base - y
        f = k * (1 - (y - base) / (base - top + 1))
        for x in range(x0, x1 + 1):
            if not mask[y][x]:
                continue
            sx = x + round(math.sin(y * 0.9) * 1.2)
            if x0 <= sx <= x1 and top <= sy <= base:
                if src[sx, sy][3] and not _is_floor(mask, sx, sy):
                    cv.flat(x, y, mix(cv.get(x, y), src[sx, sy][:3], f))


def _is_floor(mask, x, y):
    return 0 <= y < H and 0 <= x < W and mask[y][x]


def unmask(mask, cv, x0, y0, x1, y1, before):
    """Treu del terra els píxels que ha pintat un objecte (comparant amb una còpia d'abans)."""
    a, b = before.load(), cv.img.load()
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if 0 <= x < W and 0 <= y < H and a[x, y] != b[x, y]:
                mask[y][x] = False


# ─── Objectes a terra ───────────────────────────────────────────────────────

def sea_valve(cv):
    """La vàlvula de presa de mar de popa: s'ha aixecat una planxa del terra. Sense volant."""
    # el forat de la planxa aixecada (fosc, amb aigua)
    cv.poly([(292, 172), (346, 172), (350, 186), (288, 186)], DARK, lambda x, y: 1.0 + (186 - y) * 0.04)
    cv.hline(292, 346, 172, DECK, 1.0)
    cv.line(288, 186, 350, 186, DECK, 4.0)
    for x in range(292, 347):
        if hr(x // 3, 1) > 0.4:
            cv.put(x, 180 + int(hr(x, 2) * 3), [(10, 40, 46), (40, 90, 90), (110, 160, 150)], 1.4)
    # la planxa, recolzada de cantó contra el motor
    cv.poly([(330, 142), (352, 140), (356, 176), (334, 178)], DECK, lambda x, y: 4.4 - (y - 140) * 0.03)
    for y in range(143, 176, 4):
        for x in range(332, 354, 4):
            cv.put(x + (y // 4) % 2 * 2, y, DECK, 5.6)
    cv.line(330, 142, 334, 178, DECK, 1.0)
    # el cos de la vàlvula (vermell), la tapa i l'eix pelat
    cv.disc(318, 178, 13, 6, REDP, lambda nx, ny: 3.4 - nx * 1.2 - ny * 1.4)
    for bx in range(308, 330, 5):
        bolt(cv, bx, 175, REDP, 4.0)
    box(cv, 313, 160, 323, 173, REDP, 3.6)
    cv.hline(311, 325, 160, REDP, 4.6)
    vpipe(cv, 318, 141, 160, 1, CAB, 4.6)
    box(cv, 316, 139, 320, 142, CAB, 5.0)                 # el quadradet on anava el volant


def bilge_pump(cv, ENG=ENG_LIGHT):
    """La bomba de sentina: motor elèctric blau i bomba vermella, amb el tub cap al separador."""
    # tub d'aspiració (de la sentina) i el que puja al separador
    vpipe(cv, 404, 150, 166, 2, CAB, 2.8)
    # bancada
    box(cv, 356, 176, 412, 182, ENG, 2.0)
    # motor (cilindre ajagut, amb aletes)
    for y in range(160, 177):
        u = (y - 168) / 9
        for x in range(360, 392):
            fin = (x % 3 == 0)
            cv.put(x, y, ENG, 3.4 + 1.5 * (-0.3 - u) - 0.8 * u * u + (0.6 if fin else 0))
    cv.disc(360, 168, 3, 8, ENG, 2.0)
    box(cv, 372, 156, 382, 161, CAB, 3.0)                 # caixa de borns
    # bomba
    cv.disc(400, 168, 9, 9, REDP, lambda nx, ny: 3.8 - nx * 1.2 - ny * 1.2)
    cv.disc(400, 168, 3, 3, REDP, 2.0)
    box(cv, 392, 166, 395, 170, CAB, 3.6)                 # acoblament


# ─── Els personatges (personatges.py; aquí només per a la maqueta) ────────

def iri_sprite():
    return personatges.iri('L')


def bastida_sprite():
    """De perfil mirant a la dreta (cap a l'Iri)."""
    return personatges.bastida('L', talk=True).transpose(Image.FLIP_LEFT_RIGHT)


vet_face = personatges.vet_face
WALKIE = personatges.WALKIE


# ─── Text (la font de Suma Zero) ────────────────────────────────────────────

GLYPHS = {False: suma_font.all_glyphs(), True: suma_font.all_glyphs(bold=True)}


def text_width(s, bold=True):
    g = GLYPHS[bold]
    w = 0
    for ch in s:
        w += suma_font.SPACE_ADVANCE if ch == ' ' else g[ch][1] + 1 if ch in g else 0
    return max(0, w - 1)


def draw_text(img, x, y, s, col, bold=True, outline=(3, 4, 10)):
    """Escriu `s` amb la part de dalt de la cel·la a y (les majúscules comencen a y + 3)."""
    g = GLYPHS[bold]
    P = img.load()
    pts = []
    cx = x
    for ch in s:
        if ch == ' ':
            cx += suma_font.SPACE_ADVANCE
            continue
        if ch not in g:
            continue
        pix, w = g[ch]
        pts += [(cx + px, y + py) for px, py in pix]
        cx += w + 1
    if outline:
        for px, py in pts:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if 0 <= px + dx < img.width and 0 <= py + dy < img.height:
                        P[px + dx, py + dy] = outline + (255,)
    for px, py in pts:
        if 0 <= px < img.width and 0 <= py < img.height:
            P[px, py] = col + (255,)


def wrap(s, width, bold=True):
    lines, cur = [], ''
    for word in s.split(' '):
        t = (cur + ' ' + word).strip()
        if text_width(t, bold) <= width or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = word
    return lines + [cur]


# ─── La barra de verbs (nàutica) ────────────────────────────────────────────

NAVYB = [(3, 6, 12), (6, 10, 20), (9, 15, 28), (13, 21, 38), (18, 29, 50), (25, 39, 64), (34, 51, 80),
         (46, 66, 98), (62, 86, 120)]
ROPE = [(40, 28, 16), (86, 64, 38), (140, 110, 70), (196, 166, 116), (232, 210, 166)]
VERBS = [('Dona', 49, 211, 55), ('Agafa', 106, 211, 74), ('Usa', 183, 211, 55),
         ('Obre', 49, 230, 55), ('Parla', 106, 230, 74), ('Empeny', 183, 230, 55),
         ('Tanca', 49, 250, 55), ('Mira', 106, 250, 74), ('Estira', 183, 250, 55)]
INV_X, INV_Y, SLOT_W, SLOT_H, GAP = 252, 210, 49, 27, 3
TEXT = (226, 214, 180)
TEXT_HOVER = (255, 150, 60)
VERB_LINE = (206, 230, 222)
BASTIDA_COL = (150, 200, 240)


def gui(cv):
    # franja fosca de la frase
    cv.rect(0, BOTTOM, W - 1, 204, NAVYB, 0.6, lit=0)
    # el cos: planxa pintada de blau marí, amb reblons
    for y in range(205, H):
        for x in range(W):
            cv.put(x, y, NAVYB, 3.0 - (y - 205) * 0.012 + (hr(x // 3, y // 4) - 0.5) * 0.3, lit=0)
    # la vora de dalt: una corda trenada
    for x in range(W):
        for dy in range(3):
            ph = (x + dy * 2) % 6
            cv.put(x, 205 + dy, ROPE, 3.4 - abs(ph - 2.5) * 0.6 - dy * 0.3, lit=0)
    for x in range(8, W, 40):
        cv.put(x, 266, NAVYB, 5.0, lit=0)
        cv.put(x + 1, 267, NAVYB, 1.0, lit=0)
    # verbs: plaques de planxa amb quatre reblons
    for name, x, y, w in VERBS:
        box(cv, x, y, x + w - 1, y + 15, NAVYB, 4.4)
        cv.hline(x + 1, x + w - 2, y + 1, NAVYB, 5.4)
        for bx, by in ((x + 2, y + 2), (x + w - 3, y + 2), (x + 2, y + 13), (x + w - 3, y + 13)):
            cv.put(bx, by, NAVYB, 6.6, lit=0)
    # fletxes de l'inventari
    for ay, up in ((210, True), (240, False)):
        box(cv, 240, ay, 249, ay + 26, NAVYB, 4.0)
        for i in range(4):                                   # punta
            yy = ay + 6 + i if up else ay + 20 - i
            cv.hline(244 - i, 245 + i, yy, ROPE, 3.8 - i * 0.2, lit=0)
        for yy in range(ay + 10, ay + 17) if up else range(ay + 10, ay + 17):
            cv.hline(244, 245, yy, ROPE, 3.2, lit=0)
    # caselles: buits foscos amb cantoneres de llautó
    for r in range(2):
        for c in range(4):
            x, y = INV_X + c * (SLOT_W + GAP), INV_Y + r * (SLOT_H + GAP)
            box(cv, x, y, x + SLOT_W - 1, y + SLOT_H - 1, NAVYB, 1.6)
            cv.hline(x + 1, x + SLOT_W - 2, y + 1, NAVYB, 0.6)
            for (cx, cy, sx, sy) in ((x + 1, y + 1, 1, 1), (x + SLOT_W - 2, y + 1, -1, 1),
                                     (x + 1, y + SLOT_H - 2, 1, -1), (x + SLOT_W - 2, y + SLOT_H - 2, -1, -1)):
                for i in range(4):
                    cv.put(cx + sx * i, cy, BRASS, 4.0, lit=0)
                    cv.put(cx, cy + sy * i, BRASS, 3.4, lit=0)
    # menú (tres ratlles)
    box(cv, 27, 247, 45, 265, NAVYB, 4.0)
    for yy in (251, 256, 261):
        cv.hline(31, 41, yy, ROPE, 3.8, lit=0)
    # «Canvia»: un ull de bou amb la cara de la Vet
    box(cv, 3, 211, 45, 243, NAVYB, 3.6)
    cv.disc(24, 227, 13, 13, BRASS, lambda nx, ny: 3.6 - nx - ny * 1.2, lit=0)
    cv.disc(24, 227, 10, 10, [(6, 14, 22), (10, 24, 36), (18, 40, 56), (30, 60, 80)], lambda nx, ny: 1.4 - ny, lit=0)
    for a in range(0, 360, 60):
        cv.put(24 + round(math.cos(math.radians(a)) * 11.5), 227 + round(math.sin(math.radians(a)) * 11.5), BRASS, 1.4, lit=0)


def items(cv):
    """Quatre objectes a l'inventari: el walkie, la cisalla, el quadern i la llanterna."""
    def slot(c, r):
        return INV_X + c * (SLOT_W + GAP) + SLOT_W // 2, INV_Y + r * (SLOT_H + GAP) + SLOT_H // 2

    # walkie (negre, pilot taronja)
    x, y = slot(0, 0)
    box(cv, x - 5, y - 6, x + 5, y + 9, [(6, 6, 8), (16, 16, 20), (30, 30, 36), (48, 48, 56), (70, 70, 80)], 2.6, edge=True)
    cv.vline(x + 3, y - 13, y - 6, [(6, 6, 8), (30, 30, 36), (70, 70, 80)], 1.6, lit=0)
    cv.rect(x - 3, y - 4, x + 3, y, [(20, 40, 30), (60, 110, 80), (120, 180, 140)], 1.2, lit=0)
    for yy in range(y + 2, y + 8, 2):
        cv.hline(x - 3, x + 3, yy, [(6, 6, 8), (40, 40, 48)], 0.6, lit=0)
    cv.flat(x - 3, y - 8, (255, 140, 40))
    # cisalla (mànecs vermells)
    x, y = slot(1, 0)
    cv.line(x - 14, y + 7, x + 2, y - 2, REDP, 4.0, lit=0)
    cv.line(x - 14, y + 8, x + 2, y - 1, REDP, 2.6, lit=0)
    cv.line(x - 12, y + 11, x + 2, y + 1, REDP, 3.6, lit=0)
    cv.line(x - 12, y + 12, x + 2, y + 2, REDP, 2.4, lit=0)
    cv.disc(x + 3, y, 2, 2, CAB, 4.0, lit=0)
    cv.line(x + 4, y - 1, x + 13, y - 7, CAB, 6.0, lit=0)
    cv.line(x + 4, y + 1, x + 14, y - 5, CAB, 4.4, lit=0)
    # quadern (tapes blaves, goma)
    x, y = slot(2, 0)
    box(cv, x - 9, y - 9, x + 9, y + 10, [(10, 20, 50), (20, 40, 90), (36, 64, 130), (70, 100, 170), (120, 150, 210)], 2.4)
    cv.vline(x + 5, y - 9, y + 10, [(20, 10, 10), (90, 30, 30), (160, 60, 50)], 1.6, lit=0)
    cv.rect(x - 7, y - 6, x + 1, y - 3, WHITEP, 3.8, lit=0)
    # llanterna (groga)
    x, y = slot(3, 0)
    for xx in range(x - 12, x + 7):
        for yy in range(y - 3, y + 4):
            u = (yy - y) / 3.5
            cv.put(xx, yy, YELL, 3.6 - u * 1.4 - u * u, lit=0)
    cv.rect(x + 7, y - 5, x + 11, y + 5, CAB, 4.0, lit=0)
    cv.vline(x + 12, y - 4, y + 4, [(120, 110, 80), (240, 230, 190)], 1, lit=0)
    cv.rect(x - 4, y - 1, x - 2, y + 1, DARK, 2.0, lit=0)


# ─── Muntatge ───────────────────────────────────────────────────────────────

def background():
    cv = Canvas(light=LIGHT)
    wall(cv)
    ceiling(cv)
    wall_pipes(cv)
    door(cv)
    voice_tube(cv)
    marpol(cv)
    engine(cv)
    panel(cv)
    alarm(cv)
    separator(cv)
    lamps(cv)
    mask = floor(cv)
    water(cv, mask)
    for fn, (x0, y0, x1, y1) in ((sea_valve, (286, 138, 358, 190)), (bilge_pump, (354, 148, 414, 184))):
        before = cv.img.copy()
        fn(cv)
        unmask(mask, cv, x0, y0, x1, y1, before)
        reflect_obj(cv, mask, x0, x1, y0, y1 - 4 if fn is sea_valve else y1 - 2)
    # resplendors
    for lx, ly in LAMPS:
        glow(cv, lx, ly + 4, 34, WARM, 0.55)
        glow(cv, lx, ly + 4, 12, (255, 240, 200), 0.6)
    glow(cv, 35, 59, 26, RED_GLOW, 0.55)
    return cv, mask


def place(scene, sprite, fx, fy, feet_x, shade=0.86, mask=None):
    """Enganxa un personatge amb els peus a (fx, fy), amb ombra i reflex a l'aigua."""
    s = sprite.copy()
    px = s.load()
    for y in range(s.height):
        for x in range(s.width):
            r, g, b, a = px[x, y]
            if a:
                px[x, y] = (int(r * shade), int(g * shade * 1.02), int(b * shade * 1.04), a)
    P = scene.load()
    # ombra als peus
    for y in range(fy - 2, fy + 3):
        for x in range(fx - 13, fx + 14):
            if ((x - fx) / 13) ** 2 + ((y - fy) / 2.6) ** 2 <= 1:
                o = P[x, y]
                P[x, y] = (int(o[0] * 0.6), int(o[1] * 0.6), int(o[2] * 0.6), 255)
    # reflex (cap per avall, fosc i ondulat)
    ref = s.transpose(Image.FLIP_TOP_BOTTOM)
    rp = ref.load()
    oy = fy - (s.height - 1 - 83) + 1
    for y in range(ref.height):
        ty = oy + y
        if ty <= fy or ty >= BOTTOM + 10:
            continue
        k = 0.42 * (1 - (ty - fy) / 34)
        if k <= 0:
            continue
        off = round(math.sin(ty * 0.9) * 1.3)
        for x in range(ref.width):
            r, g, b, a = rp[x, y]
            tx = fx - feet_x + x + off
            if a and 0 <= tx < W and (mask is None or mask[ty][tx]):
                o = P[tx, ty]
                c = mix(o[:3], (int(r * 0.7), int(g * 0.8), int(b * 0.85)), k)
                P[tx, ty] = c + (255,)
    scene.alpha_composite(s, (fx - feet_x, fy - 83))


def main():
    cv, mask = background()
    bg = cv.img.copy()
    bg.save(HERE / 'sala-maquines.png')

    scene = bg.copy()
    # en Diu, assegut damunt del col·lector calent, mirant en Bastida
    cat = diu(cua=1)
    scene.alpha_composite(cat, (196, 62 - 4 - 22))
    BX = 140
    place(scene, bastida_sprite(), BX, 188, 23, mask=mask)
    place(scene, iri_sprite(), 236, 190, 25, mask=mask)

    ui = Canvas(img=scene)
    gui(ui)
    items(ui)
    face = vet_face()
    scene.alpha_composite(_porthole(face), (12, 214))

    for name, x, y, w in VERBS:
        col = TEXT_HOVER if name == 'Mira' else TEXT
        draw_text(scene, x + (w - text_width(name)) // 2, y + 1, name, col)
    line = 'Mira vàlvula de presa de mar'
    draw_text(scene, (W - text_width(line, False)) // 2, BOTTOM - 1, line, VERB_LINE, bold=False)

    say = 'Amb tanta aigua, l’hauries pogut tirar per la borda. Ningú no ho hauria vist.'
    lines = wrap(say, 186)
    top = 188 - 83 - 6 - len(lines) * 10
    for i, ln in enumerate(lines):
        draw_text(scene, BX - text_width(ln) // 2, top + i * 10, ln, BASTIDA_COL)

    cursor(scene, 318, 150)
    scene.convert('RGB').resize((W * 2, H * 2), Image.NEAREST).save(HERE / 'sala-maquines-joc.png')
    print('✔', HERE / 'sala-maquines.png', '·', HERE / 'sala-maquines-joc.png')


def cursor(img, x, y):
    """El punter en creu, com el de Benne."""
    P = img.load()
    for d in range(2, 6):
        for dx, dy in ((d, 0), (-d, 0), (0, d), (0, -d)):
            for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                q = (x + dx + ox, y + dy + oy)
                if P[q][:3] != (255, 255, 255):
                    P[q] = (3, 4, 10, 255)
            P[x + dx, y + dy] = (255, 255, 255, 255)


def _porthole(face):
    """La cara de la Vet retallada en rodó per a l'ull de bou del botó «Canvia»."""
    out = Image.new('RGBA', (25, 26), (0, 0, 0, 0))
    src = face.load()
    P = out.load()
    for y in range(26):
        for x in range(25):
            if (x - 12) ** 2 + (y - 13) ** 2 <= 10 ** 2 and src[x, y + 2][3]:
                P[x, y] = src[x, y + 2]
    return out


if __name__ == '__main__':
    main()
