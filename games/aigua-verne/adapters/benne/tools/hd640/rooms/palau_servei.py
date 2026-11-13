"""
Aigua Verne — `palau_servei` (P): els passadissos de servei del palau orbital.

L'altra cara del palau: gris, funcional, llum de fluorescent. D'esquerra a dreta:
  - l'**ascensor de servei** (porta d'acer de dues fulles, l'indicador de pis i el lector de targetes vermell);
  - el **passaplats**, on els cambrers deixen les **safates** (prop `safates`: sempre, però a part);
  - el **carro** de flors de plàstic d'en Nil (colors massa vius);
  - un carro de neteja amb galleda i pal de fregar, i un ull de bou a l'espai;
  - a dalt, les **canonades** del palau (aigua «només per a piscines», vapor, aire).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from hd.pix import Canvas, Light, hr, mix
from hd.rooms.arenga import box, bolt, hpipe, vpipe
from hd640.rooms.palau_comu import (GRIS, CROM, BLANC, BLAU, VERMELL, VERD, LED, ORP, NEGRE, RH, _diff, lletres,
                                    lletres_c, espai, estrelles_frames, gota, ombra, negre_barra, fbm)

PERSONA = 100
CEIL = 24
FLOOR_Y = 226
LIFT = (96, 100, 196, FLOOR_Y)       # la porta de l'ascensor (x0, y0, x1, y1)
READER = (206, 146)
HATCH = (264, 118, 360, 180)         # el forat del passaplats
CART = (418, 470)                    # el carro de flors: x0, x1 de la plataforma
PORT = (572, 84, 17)                 # l'ull de bou

YELLOW = [(40, 30, 6), (90, 66, 10), (150, 112, 18), (206, 160, 30), (240, 200, 60), (255, 236, 140)]
PLAST = {'r': [(70, 6, 20), (150, 14, 40), (230, 40, 70), (255, 110, 130)],
         'g': [(4, 60, 20), (10, 130, 40), (40, 210, 70), (140, 255, 140)],
         'y': [(90, 70, 0), (190, 160, 0), (255, 230, 20), (255, 250, 160)],
         'm': [(70, 10, 70), (150, 30, 160), (230, 70, 230), (255, 170, 250)],
         'o': [(100, 30, 0), (200, 80, 10), (255, 140, 30), (255, 200, 120)],
         'b': [(10, 30, 90), (30, 80, 200), (70, 150, 255), (170, 210, 255)]}

LIGHT = Light(ambient=0.1, vignette=(60, 20), floor_fade=(240, 40))
for _x in (150, 470):
    LIGHT.point(_x, 14, r=260, k=2.2, squash=1.0, down=True, power=1.5)
LIGHT.point(312, 150, r=90, k=0.5, power=1.6)                       # la llum càlida de la cuina, pel passaplats


# ─── Sostre, paret, terra ───────────────────────────────────────────────────

def sostre(cv):
    cv.rect(0, 0, 639, CEIL, GRIS, lambda x, y: 3.0 + y * 0.03 - (1.0 if x % 64 == 0 else 0))
    cv.hline(0, 639, CEIL, GRIS, 1.4)
    # els fluorescents
    for x in (150, 470):
        cv.rect(x - 46, 6, x + 46, 13, GRIS, 3.4)
        cv.rect(x - 42, 8, x + 42, 11, [(200, 210, 210), (230, 240, 240), (250, 255, 255)], 1.4, lit=0)
        cv.hline(x - 42, x + 42, 12, GRIS, 5.0)
        cv.glow(x, 12, 50, (220, 240, 240), 0.25)


def paret(cv):
    for y in range(CEIL + 1, FLOOR_Y):
        for x in range(640):
            seam = x % 96
            v = 4.4 + (fbm(x / 60, y / 50, 3) - 0.5) * 0.4 + (hr(x // 3, y // 3) - 0.5) * 0.15
            if seam == 0:
                v -= 1.6
            elif seam == 1:
                v += 0.8
            if y > 188:
                v -= 0.9                                                    # el sòcol, més fosc
            cv.put(x, y, GRIS, v)
    for x in range(0, 640, 96):
        for y in range(CEIL + 40, FLOOR_Y - 4, 34):
            bolt(cv, x + 4, y, GRIS, 4.6)
            bolt(cv, x - 5, y, GRIS, 4.6)
    # el para-xocs dels carros (goma grisa) i el sòcol
    for y in range(184, 190):
        for x in range(640):
            cv.put(x, y, GRIS, 3.4 + (1.6 if y == 184 else -1.0 if y == 189 else 0))
    cv.hline(0, 639, FLOOR_Y - 1, GRIS, 1.4)
    # rètols de servei
    lletres(cv, 'NOMÉS PERSONAL DE SERVEI', 246, 68, (60, 62, 70))
    cv.rect(244, 77, 344, 78, YELLOW, 3.4)
    lletres(cv, 'MOLL DE CÀRREGA', 374, 110, (40, 40, 46))
    for k in range(4):                                                   # la fletxa →
        cv.hline(436, 444, 112, GRIS, 1.0)
        cv.vline(444 + k, 109 + k, 115 - k, GRIS, 1.0)
    # un cartell: «SOMRIU. EL SENYOR VERNE ET VEU.»
    box(cv, 18, 92, 72, 150, BLANC, 5.4)
    gota(cv, 45, 108, 14, lit=1)
    lletres_c(cv, 'SOMRIU', 45, 124, (40, 60, 120))
    lletres_c(cv, 'ET VEU', 45, 134, (40, 60, 120))
    for cx in (20, 70):
        cv.flat(cx, 94, (90, 90, 96))


def terra(cv):
    vx, vy = 320, -120
    for y in range(FLOOR_Y, RH):
        d = y - vy
        v = 30000 / d
        for x in range(640):
            u = vx + (x - vx) * 400 / d
            lvl = 3.4 + (y - FLOOR_Y) * 0.02 + (hr(int(u // 4), int(v), 7) - 0.5) * 0.3
            if int(u // 64) != int((vx + (x + 1 - vx) * 400 / d) // 64):
                lvl -= 1.0
            if int(v / 10) != int(30000 / (d + 1) / 10):
                lvl -= 0.8
            cv.put(x, y, GRIS, lvl)
    # la línia groga de seguretat, a un pam de la paret
    for x in range(640):
        for y in (FLOOR_Y + 4, FLOOR_Y + 5):
            cv.put(x, y, YELLOW, 3.0 + (0.6 if y == FLOOR_Y + 4 else 0))
    # unes taques de fregar (en forma d'arc)
    for k in range(3):
        cx, cy = 360 + k * 70, 246
        for a in range(0, 180, 3):
            x = cx + math.cos(math.radians(a)) * 30
            y = cy - math.sin(math.radians(a)) * 6
            cv.put(x, y, GRIS, 4.4)


# ─── Canonades ──────────────────────────────────────────────────────────────

def canonades(cv):
    """Tres tubs al llarg de la paret, sota el sostre, amb brides, una vàlvula i etiquetes."""
    tubs = ((34, 6, BLANC, 'AIGUA - NOMÉS PISCINES', BLAU), (48, 4, GRIS, 'VAPOR', VERMELL), (58, 3, CROM, 'AIRE', VERD))
    for yc, r, ramp, lab, band in tubs:
        hpipe(cv, 0, 639, yc, r, ramp, 4.4 if ramp is not CROM else 3.8)
        cv.hline(0, 639, yc + r + 1, GRIS, 2.0)
        for x in range(30, 640, 120):                                   # brides
            cv.rect(x, yc - r - 1, x + 3, yc + r + 1, ramp, lambda xx, yy: 4.0 + (1.0 if xx == x else -0.6))
        for x in range(80, 520, 240):                                   # etiquetes
            w = len(lab) * 4 + 4
            if r >= 4:
                cv.rect(x, yc - (5 if r >= 6 else 3), x + w, yc + 3, band, 2.4, lit=0.5)
                lletres(cv, lab, x + 3, yc - 2, (236, 240, 246))
    # la vàlvula de volant del tub de l'aigua, i el tub que baixa cap a l'ascensor (cap a la sala de control)
    vpipe(cv, 226, 40, 96, 5, BLANC, 4.2)
    cv.rect(219, 90, 233, 94, BLANC, lambda x, y: 5.6 - (x - 219) * 0.1)
    cv.rect(217, 95, 235, 97, GRIS, 2.0)
    cv.rect(220, 60, 232, 63, BLANC, 5.4)
    cv.disc(226, 70, 9, 9, VERMELL, lambda nx, ny: 3.8 - ny - nx * 0.4)
    cv.disc(226, 70, 6, 6, VERMELL, 1.4)
    for a in range(0, 360, 60):
        cv.line(226, 70, 226 + math.cos(math.radians(a)) * 7, 70 + math.sin(math.radians(a)) * 7, VERMELL, 4.0)
    cv.disc(226, 70, 2, 2, CROM, 5.0)
    # suports
    for x in range(64, 640, 128):
        cv.rect(x, CEIL + 1, x + 2, 62, GRIS, 2.4)


# ─── Ascensor ───────────────────────────────────────────────────────────────

def ascensor(cv):
    x0, y0, x1, y1 = LIFT
    # el marc d'acer i la llinda amb l'indicador
    cv.rect(x0 - 10, y0 - 22, x1 + 10, y1, GRIS, lambda x, y: 5.2 - (0.8 if x > x1 else 0))
    box(cv, x0 - 10, y0 - 22, x1 + 10, y0 - 1, GRIS, 5.6)
    cv.rect(x0 + 30, y0 - 18, x1 - 30, y0 - 6, NEGRE, 0.6, lit=0)
    lletres_c(cv, 'P-3', (x0 + x1) // 2 - 4, y0 - 14, LED[3])
    for k in range(4):                                                   # la fletxa ▼
        cv.hline((x0 + x1) // 2 + 8 - 3 + k, (x0 + x1) // 2 + 8 + 3 - k, y0 - 14 + k, LED, 3.0, lit=0)
    # les dues fulles d'acer raspallat
    mid = (x0 + x1) // 2
    for y in range(y0, y1):
        for x in range(x0, x1 + 1):
            brushed = (hr(x, y // 9, 5) - 0.5) * 0.25
            refl = 0.8 if 10 < (x - x0 - (y - y0) * 0.3) % 60 < 22 else 0
            v = 3.6 + brushed + refl - (y - y0) * 0.006
            if abs(x - mid) <= 0:
                v = 1.2
            elif x == mid + 1:
                v = 6.4
            cv.put(x, y, CROM, v)
    cv.rect(x0, y1 - 14, x1, y1 - 1, CROM, lambda x, y: 3.4 - (y - y1 + 14) * 0.05)    # sòcol de cops
    cv.hline(x0, x1, y1 - 14, CROM, 6.0)
    # el rètol
    cv.rect(mid - 24, y0 + 20, mid + 24, y0 + 30, BLANC, 6.4)
    lletres_c(cv, 'SERVEI', mid, y0 + 23, (40, 50, 70))
    # el lector de targetes: caixeta negra, ranura i llum vermella
    rx, ry = READER
    box(cv, rx - 6, ry - 14, rx + 6, ry + 14, NEGRE, 2.0)
    cv.rect(rx - 3, ry - 8, rx + 3, ry - 7, NEGRE, 0.2, lit=0)
    cv.disc(rx, ry + 4, 2.2, 2.2, VERMELL, 4.6, lit=0)
    cv.glow(rx, ry + 4, 6, (255, 60, 50), 0.5)
    cv.rect(rx - 4, ry + 9, rx + 4, ry + 10, GRIS, 4.0)
    # el botó de crida
    cv.disc(x0 - 6 + 0, 160, 0.1, 0.1, GRIS, 0)
    ombra(cv, mid, y1 + 2, 62, 3, 0.4)


# ─── Passaplats ─────────────────────────────────────────────────────────────

def passaplats(cv):
    x0, y0, x1, y1 = HATCH
    # el forat: a dins, la cuina (càlida i fosca, amb prestatges i vapor)
    for y in range(y0, y1):
        for x in range(x0, x1 + 1):
            v = 2.0 + (y - y0) * 0.012 + (0.6 if (y - y0) % 18 == 14 else 0)
            cv.put(x, y, [(20, 16, 12), (40, 32, 24), (70, 56, 40), (110, 88, 60), (160, 130, 90)], v)
    for sx in range(x0 + 8, x1 - 8, 14):                                 # olles al prestatge del fons
        cv.rect(sx, y0 + 6, sx + 9, y0 + 13, CROM, lambda x, y: 3.0 - (x - sx) * 0.15)
    cv.glow((x0 + x1) // 2, y0 + 20, 40, (255, 220, 160), 0.18)
    # el marc d'inox i la persiana enrotllada a dalt
    cv.rect(x0 - 6, y0 - 12, x1 + 6, y0 - 1, CROM, lambda x, y: 4.4 + (1.0 if (y - y0) % 3 == 0 else 0))
    cv.hline(x0 - 6, x1 + 6, y0 - 12, CROM, 6.4)
    for y in range(y0, y1):
        cv.put(x0 - 6, y, CROM, 6.0)
        cv.put(x0 - 5, y, CROM, 4.6)
        cv.put(x1 + 5, y, CROM, 3.0)
        cv.put(x1 + 6, y, CROM, 2.0)
        for k in range(4):
            cv.put(x0 - 4 + k, y, CROM, 4.0 - k * 0.4)
            cv.put(x1 + 1 + k, y, CROM, 3.6 - k * 0.3)
    # el taulell d'inox
    cv.rect(x0 - 10, y1, x1 + 10, y1 + 4, CROM, lambda x, y: 6.4 - (y - y1) * 0.9)
    cv.rect(x0 - 8, y1 + 5, x1 + 8, y1 + 7, CROM, 2.0)
    # el timbre (per a quan les safates són a punt)
    cv.disc(x1 + 2, y1 - 3, 3.5, 2.4, ORP, lambda nx, ny: 5 - ny * 1.6)
    cv.put(x1 + 2, y1 - 6, ORP, 6.0)
    lletres(cv, 'SAFATES', x0 + 4, y0 - 9, (40, 44, 52))


def safates(cv):
    """Les safates que deixen els cambrers: una pila d'argent i, al davant, una amb copes buides i tovallons."""
    x0, y0, x1, y1 = HATCH
    # la pila (cinc safates)
    for k in range(5):
        cy = y1 - 2 - k * 2
        cv.disc(x0 + 26, cy, 18, 3, CROM, lambda nx, ny: 6.0 - ny * 1.4 - nx * 0.6)
        cv.hline(x0 + 9, x0 + 43, cy + 2, CROM, 2.2)
    # la de les copes
    cx, cy = x0 + 66, y1 - 1
    cv.disc(cx, cy, 20, 3.4, CROM, lambda nx, ny: 6.4 - ny * 1.6 - nx * 0.6)
    cv.disc(cx, cy - 0.5, 17, 2.2, CROM, lambda nx, ny: 4.6 + ny * 0.8)
    for dx in (-12, -4, 6):
        x = cx + dx
        cv.hline(x - 2, x + 2, cy, CROM, 5.0)
        cv.vline(x, cy - 4, cy - 1, CROM, 6.0)
        for k in range(8):
            cv.put(x - 1, cy - 5 - k, CROM, 6.4)
            cv.put(x + 1, cy - 5 - k, CROM, 4.4)
        cv.put(x, cy - 5, ORP, 4.6)                                       # un culet de cava
    cv.poly([(cx + 10, cy - 2), (cx + 18, cy - 3), (cx + 16, cy + 1), (cx + 9, cy + 1)], BLANC, 6.0)   # tovalló


# ─── Carros ─────────────────────────────────────────────────────────────────

def roda(cv, x, y, r=4):
    cv.disc(x, y, r, r, NEGRE, lambda nx, ny: 1.6 - ny * 0.8)
    cv.disc(x, y, 1.4, 1.4, CROM, 4.0)


def flor(cv, x, y, col, s=1.0):
    ramp = PLAST[col]
    for a in range(5):
        ang = a / 5 * 2 * math.pi + x
        cv.disc(x + math.cos(ang) * 2.4 * s, y + math.sin(ang) * 2.0 * s, 1.8 * s, 1.6 * s, ramp, 2.4, lit=0.4)
    cv.disc(x, y, 1.2 * s, 1.2 * s, PLAST['y'] if col != 'y' else PLAST['o'], 3.0, lit=0)


def carro_flors(cv):
    x0, x1 = CART[0], CART[1] + 34
    base = FLOOR_Y + 8
    ombra(cv, (x0 + x1) // 2, base + 4, (x1 - x0) // 2 + 6, 4, 0.6)
    # el carro: dos pisos de reixa verda, nansa i rodes
    for yy in (base - 14, base - 50):
        cv.rect(x0, yy, x1, yy + 4, [(10, 30, 14), (20, 60, 28), (40, 100, 50), (70, 150, 80), (120, 200, 120)],
                lambda x, y: 2.6 + (1.0 if y == yy else 0) - (0.6 if (x - x0) % 6 == 0 else 0))
    for x in (x0 + 1, x1 - 1):
        cv.vline(x, base - 56, base - 8, CROM, 4.6)
    cv.line(x1 - 1, base - 56, x1 + 8, base - 76, CROM, 5.0)
    cv.hline(x1 + 4, x1 + 12, base - 77, [(20, 20, 20), (50, 50, 50), (90, 90, 90)], 1.4)
    for x in (x0 + 5, x1 - 5):
        roda(cv, x, base - 2)
    # galledes de flors de plàstic: dalt, plena; baix, dues capses
    for k, bx in enumerate((x0 + 6, x0 + 30, x0 + 54)):
        cv.poly([(bx, base - 66), (bx + 20, base - 66), (bx + 18, base - 51), (bx + 2, base - 51)], BLANC,
                lambda x, y: 5.0 - (x - bx) * 0.08)
        cv.hline(bx - 1, bx + 21, base - 67, BLANC, 6.6)
        cols = 'rmyobg'
        for j in range(9):
            fx = bx + 2 + int(hr(k, j, 1) * 16)
            fy = base - 70 - int(hr(k, j, 2) * 26)
            cv.line(fx, fy, bx + 10 + (fx - bx - 10) // 3, base - 66, PLAST['g'], 1.8, lit=0.4)
            if j % 3 == 0:
                cv.disc(fx + 2, fy + 6, 2.2, 1.0, PLAST['g'], 2.6, lit=0.4)        # una fulla
        for j in range(9):
            fx = bx + 2 + int(hr(k, j, 1) * 16)
            fy = base - 70 - int(hr(k, j, 2) * 26)
            flor(cv, fx, fy, cols[(j + k * 2) % 6], s=1.1)
    for bx in (x0 + 4, x0 + 40):                                         # capses d'«en Nil» a baix
        box(cv, bx, base - 34, bx + 32, base - 15, [(60, 40, 20), (100, 72, 40), (150, 112, 66), (196, 156, 100)], 2.6)
        flor(cv, bx + 8, base - 36, 'r')
        flor(cv, bx + 20, base - 37, 'y')
    lletres(cv, 'NIL', x0 + 10, base - 27, (60, 36, 16))


def carro_neteja(cv):
    x0 = 528
    base = FLOOR_Y + 6
    ombra(cv, x0 + 40, base + 3, 48, 4, 0.6)
    # el cubell groc amb l'escorredor
    cv.poly([(x0, base - 28), (x0 + 40, base - 28), (x0 + 37, base - 4), (x0 + 3, base - 4)], YELLOW,
            lambda x, y: 3.6 - (x - x0) * 0.04)
    cv.hline(x0 - 1, x0 + 41, base - 29, YELLOW, 5.0)
    cv.rect(x0 + 6, base - 40, x0 + 24, base - 29, GRIS, lambda x, y: 3.0 + (1.0 if y == base - 40 else 0))
    cv.rect(x0 + 2, base - 27, x0 + 38, base - 25, [(20, 50, 70), (40, 90, 110), (90, 150, 160)], 1.4)   # aigua bruta
    for x in (x0 + 4, x0 + 36):
        roda(cv, x, base - 1, 3)
    # el pal de fregar, recolzat a la paret
    cv.line(x0 + 30, base - 34, x0 + 46, base - 118, CROM, 3.0)
    cv.line(x0 + 31, base - 34, x0 + 47, base - 118, CROM, 5.0)
    cv.rect(x0 + 45, base - 124, x0 + 48, base - 117, BLAU, 2.6)
    for k in range(-5, 6):
        cv.line(x0 + 28, base - 36, x0 + 28 + k * 1.2, base - 28, BLANC, 3.6 + (k % 2))
    # la bossa d'escombraries i el carro de les tovalloles
    cv.rect(x0 + 50, base - 52, x0 + 96, base - 4, GRIS, lambda x, y: 3.2 - (x - x0 - 50) * 0.02)
    cv.disc(x0 + 73, base - 52, 22, 6, [(10, 10, 14), (24, 24, 30), (40, 40, 50), (70, 70, 84)],
            lambda nx, ny: 1.6 - ny - nx * 0.4)
    cv.rect(x0 + 50, base - 50, x0 + 96, base - 50, CROM, 5.6)
    for k in range(4):
        cv.rect(x0 + 54, base - 46 + k * 10, x0 + 92, base - 39 + k * 10, BLANC,
                lambda x, y: 6.0 - (y % 7) * 0.3 - (x - x0 - 54) * 0.02)
    for x in (x0 + 54, x0 + 92):
        roda(cv, x, base - 1, 3)


def ull_de_bou(cv):
    cx, cy, r = PORT
    bright = espai(cv, cx - r, cy - r, cx + r, cy + r, seed=61, mask=lambda x, y: (x - cx) ** 2 + (y - cy) ** 2 <= r * r,
                   dens=2.0)
    cv.ring(cx, cy, r + 1, CROM, 6.0, step=1)
    cv.ring(cx, cy, r + 2, CROM, 4.4, step=1)
    cv.ring(cx, cy, r + 3, CROM, 3.0, step=1)
    cv.ring(cx, cy, r + 4, GRIS, 2.0, step=1)
    for a in range(0, 360, 45):
        bolt(cv, round(cx + math.cos(math.radians(a)) * (r + 3)), round(cy + math.sin(math.radians(a)) * (r + 3)),
             CROM, 4.0)
    for k in range(6):                                                   # la lluentor del vidre
        cv.flat(cx - 9 + k, cy - 10 + k // 2, (120, 130, 160))
    return bright


# ─── Composició ─────────────────────────────────────────────────────────────

def bg(cv):
    sostre(cv)
    paret(cv)
    terra(cv)
    canonades(cv)
    _ST['bright'] = ull_de_bou(cv)
    ascensor(cv)
    passaplats(cv)
    carro_flors(cv)
    carro_neteja(cv)
    negre_barra(cv)


_ST = {}


@functools.lru_cache(maxsize=None)
def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv.img


def _frames_estrelles():
    tmp = Canvas(light=LIGHT)
    bright = ull_de_bou(tmp)
    return estrelles_frames(_base(), bright, n=10, seed=9)


PROPS = {'safates': safates}
ANIMS = {'estrelles': {'frames': _frames_estrelles, 'frameDuration': 300}}


# ─── Geometria (640×360) ────────────────────────────────────────────────────

GEOMETRIA = {
    'things': {
        'ascensor': {'rect': (86, 78, 214, FLOOR_Y), 'walk': (150, 240)},
        'safates': {'rect': (258, 150, 368, 188), 'walk': (312, 240)},
        'carro': {'rect': (414, 132, 508, 234), 'walk': (462, 246)},
        'canonades': {'rect': (0, 26, 639, 64), 'walk': (330, 238)},
    },
    'spawns': {'vet': (250, 250), 'lia': (384, 244), 'nil': (524, 250)},
    'walkable': [(6, 234), (634, 234), (634, 257), (6, 257)],
}
