"""
**El dibuix pla de sempre** (font de les textures de la sala en 3D, diposit2.py).

Prova de resolució: el dipòsit d'aigua 2 de l'Arenga a 640×360 (la composició de hd/rooms/diposit2.py ×4/3,
dibuixada de nou amb el detall que hi cap). Mateixes rampes i mateixes animacions.

Escena 7: l'interior d'un dipòsit d'acer pintat de blanc epoxi, esquerdat i rovellat, amb la marca de l'aigua antiga,
reforços verticals i un bassal al fons; l'única llum baixa pel registre del sostre (obert, des del rebost); l'escala
de mà; la carcassa del filtre (FILTRE, amb el manòmetre); el cartell de 1984 «AIGUA NO POTABLE» amb la gota que somriu,
ara escrit amb la lletra gran de 640.
Animacions: `gota` (cau del sostre al bassal), `bassal` (el reflex del registre ondula) i `pols` (al feix de llum).
"""
import math

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from hd.pix import Canvas, Light, W, H, hr, mix, RUST
from hd.rooms.arenga import DARK, WHITEP, BRASS, WARM, box, rrect, bolt, hpipe, vpipe, glow
from hd.rooms.comu import _diff, text, text_width
from hd640.font import font640, draw_text, text_width as font_width
from hd640.rooms.pallol_pla_comu import FLOOR_Y, vladder, rust_streaks

from hd.pix import Canvas  # noqa: E402,F811  (a 1×: és la font de les textures de la sala en 3D)
Canvas1x = Canvas

HATCH = (296, 24)                       # el centre del registre, al sostre
CEIL = 32                               # on acaba el sostre
_PH = {'t': 0.0}                        # fase de l'aigua del bassal (animació `bassal`)
EPOXY = [(10, 12, 14), (20, 24, 26), (34, 38, 40), (52, 58, 58), (74, 80, 78), (100, 106, 102), (130, 134, 128),
         (164, 166, 158), (198, 198, 188)]
BOTTOMR = [(6, 7, 8), (12, 14, 15), (20, 23, 24), (30, 34, 34), (42, 47, 46), (58, 63, 60), (78, 82, 78)]
STAIN = (96, 70, 40)
WATER = [(4, 10, 12), (8, 18, 22), (14, 30, 34), (24, 46, 50), (40, 68, 70), (80, 110, 108)]
STEELF = [(14, 16, 20), (28, 32, 38), (44, 50, 58), (64, 72, 80), (90, 98, 106), (122, 130, 136), (160, 166, 170),
          (206, 210, 212)]
ENAMEL = [(70, 70, 64), (140, 138, 128), (200, 198, 184), (232, 230, 216), (248, 246, 236)]
ENRED = [(40, 10, 10), (110, 24, 22), (170, 40, 34), (210, 70, 56)]
DROPB = [(14, 40, 90), (30, 80, 160), (70, 140, 220), (150, 200, 250), (220, 240, 255)]

LIGHT = Light(ambient=-1.1, vignette=(147, 27), floor_fade=(245, 40))
LIGHT.point(HATCH[0], HATCH[1] + 40, r=200, k=2.9, squash=0.8, power=1.4)
LIGHT.point(HATCH[0], FLOOR_Y + 19, r=147, k=1.6, squash=2.4, power=1.6)          # la taca de llum a terra


def _beam(x, y):
    """El feix de llum que baixa del registre: un con que s'eixampla cap a terra."""
    t = (y - CEIL) / (FLOOR_Y + 27 - CEIL)
    if t < 0 or t > 1.1:
        return 0.0
    half = 27 + t * 61
    d = abs(x - HATCH[0]) / half
    return max(0.0, 1 - d) ** 1.4 * (1 - t * 0.4)


# ─── Parets, sostre i fons ────────────────────────────────────────────────

def walls(cv):
    for y in range(CEIL, FLOOR_Y):
        for x in range(W):
            cv.put(x, y, EPOXY, 3.2 + (hr(x // 4, y // 6, 31) - 0.5) * 0.4)
    # reforços verticals (perfils en T), amb ombra a la dreta i les soldadures
    for fx in range(24, W, 99):
        for x in range(fx, fx + 9):
            d = x - fx
            for y in range(CEIL, FLOOR_Y):
                cv.put(x, y, EPOXY, 3.6 + (1.0 if d == 0 else 0.5 if d < 4 else -0.4 if d >= 7 else 0))
        for y in range(CEIL + 2, FLOOR_Y, 3):                              # el cordó a peu del perfil
            cv.put(fx - 1, y, EPOXY, 2.4 if y % 2 else 3.0)
        cv.darken(fx + 9, CEIL, fx + 14, FLOOR_Y, lambda xx, yy, fx=fx: 0.6 - (xx - fx - 9) * 0.12)
    for sy in (93, 155):                                                 # soldadures horitzontals
        for x in range(W):
            cv.put(x, sy, EPOXY, 1.8)
            cv.put(x, sy + 1, EPOXY, 4.0 if (x // 2) % 2 else 3.4)
    # la marca de l'aigua antiga: tot el que hi ha a sota és més brut i marronós
    tide = 83
    for y in range(tide, FLOOR_Y):
        for x in range(W):
            k = 0.16 + 0.14 * (y - tide) / (FLOOR_Y - tide)
            if hr(x // 3, y // 4, 77) > 0.85:
                k += 0.12
            cv.flat(x, y, mix(cv.get(x, y), STAIN, k))
    for x in range(W):
        wob = round(math.sin(x * 0.05) * 1.6)
        for dy, k in ((0, 0.55), (1, 0.4), (2, 0.2)):
            cv.flat(x, tide + wob + dy, mix(cv.get(x, tide + wob + dy), (70, 52, 30), k))
    for x in range(W):                                                  # una segona marca, més vella i més avall
        wob = round(math.sin(x * 0.04 + 1.7) * 1.3)
        if hr(x // 5, 3) > 0.25:
            cv.flat(x, 126 + wob, mix(cv.get(x, 126 + wob), (70, 52, 30), 0.3))
    # l'epoxi esquerdat i saltat (taques de planxa rovellada)
    for i in range(34):
        cx = int(hr(i, 1, 5) * W)
        cy = 45 + int(hr(i, 2, 5) * (FLOOR_Y - 59))
        rx, ry = 2 + hr(i, 3) * 5.5, 1.3 + hr(i, 4) * 2.7
        for y in range(int(cy - ry), int(cy + ry) + 1):
            for x in range(int(cx - rx), int(cx + rx) + 1):
                e = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
                if e <= 1 and hr(x, y, i) > 0.35:
                    cv.flat(x, y, mix(cv.get(x, y), RUST[2 if e > 0.5 else 3], 0.55))
                elif 1 < e <= 1.5 and hr(x, y, i + 50) > 0.6:
                    cv.flat(x, y, mix(cv.get(x, y), (226, 224, 212), 0.3))   # la vora de l'epoxi aixecat
    for i in range(6):                                                  # esquerdes fines
        x, y = int(hr(i, 91) * W), 50 + int(hr(i, 92) * 120)
        for k in range(10 + int(hr(i, 93) * 14)):
            x += 1 if hr(i, k, 94) > 0.5 else 0
            y += 1
            cv.flat(x, y, mix(cv.get(x, y), (30, 26, 22), 0.5))
    rust_streaks(cv, 0, 40, W - 1, FLOOR_Y - 3, 90, k=0.45, seed=4)


def ceiling(cv):
    """El sostre del dipòsit (la coberta del rebost), vist de sota: planxa i bigues, amb el registre obert."""
    for y in range(0, CEIL):
        for x in range(W):
            cv.put(x, y, EPOXY, 1.6 + y * 0.04 + (hr(x // 5, y // 3, 9) - 0.5) * 0.3)
    for bx in range(24, W, 99):
        box(cv, bx - 1, 0, bx + 9, CEIL + 1, EPOXY, 2.6, grad=0.4)
        for y in (6, 18, 28):
            cv.put(bx + 4, y, EPOXY, 4.0)
    cv.hline(0, W - 1, CEIL, EPOXY, 1.0)
    cv.hline(0, W - 1, CEIL + 1, EPOXY, 0.6)
    # el registre obert: la boca (llum del rebost), la brida amb cargols i la tapa, oberta enlaire
    hx, hy = HATCH
    cv.disc(hx, hy - 5, 35, 12, EPOXY, lambda nx, ny: 1.4 - ny * 0.3)    # brida
    for a in range(0, 360, 24):
        bolt(cv, hx + round(math.cos(math.radians(a)) * 32), hy - 5 + round(math.sin(math.radians(a)) * 11), EPOXY, 3.8)
    for y in range(int(hy - 17), int(hy + 6)):
        for x in range(hx - 32, hx + 33):
            nx, ny = (x - hx) / 28, (y - (hy - 5)) / 9
            if nx * nx + ny * ny <= 1:
                cv.flat(x, y, mix((255, 226, 160), (255, 246, 220), max(0.0, 1 - abs(nx))))
            elif nx * nx + ny * ny <= 1.15:
                cv.flat(x, y, mix(cv.get(x, y), (230, 200, 140), 0.5))   # el cantell il·luminat de la boca
    cv.rect(hx - 19, 0, hx + 13, 5, [(120, 100, 70), (180, 156, 110)], 1.2, lit=0)  # el rebost, a dalt
    for x in range(hx - 17, hx + 12, 6):                                # les caixes del rebost, a contrallum
        cv.vline(x, 1, 5, [(80, 64, 44), (120, 100, 70)], 0.6, lit=0)
    # la tapa, oberta (es veu de cantó, a la dreta del forat), amb la nansa
    TAPA = [(14, 22, 40), (24, 40, 70), (40, 64, 100), (62, 92, 130)]
    cv.poly([(hx + 27, hy - 11), (hx + 45, hy - 24), (hx + 48, hy - 20), (hx + 29, hy - 5)], TAPA, 2.0)
    cv.line(hx + 27, hy - 11, hx + 45, hy - 24, TAPA, 3.4)
    cv.line(hx + 38, hy - 16, hx + 42, hy - 13, TAPA, 3.6)


def floor(cv):
    """El fons del dipòsit: planxa amb cordons de soldadura, molla i un bassal d'aigua estancada."""
    vp = (320, 40)
    for y in range(FLOOR_Y, H):
        d = y - vp[1]
        for x in range(W):
            u = vp[0] + (x - vp[0]) * 200 / d
            u2 = vp[0] + (x + 1 - vp[0]) * 200 / d
            lv = 2.4 + (hr(x // 4, y // 2, 12) - 0.5) * 0.4
            if int(u // 120) != int(u2 // 120):
                lv = 1.0
            elif y in (221, 248):
                lv = 3.6
            elif y in (222, 249):
                lv = 1.6
            if hr(x // 6, y // 2, 13) > 0.94:
                lv -= 0.8                                                 # llot
            cv.put(x, y, BOTTOMR, lv)
    # el bassal: una el·lipse d'aigua fosca amb la llum del registre reflectida
    pcx, pcy, prx, pry = 317, 240, 123, 15
    src, S = cv.img.copy().load(), cv.S                               # (src, en píxels reals)
    for y in range(pcy - pry - 3, pcy + pry + 4):
        for x in range(pcx - prx - 6, pcx + prx + 7):
            e = ((x - pcx) / (prx + hr(y, 1) * 8)) ** 2 + ((y - pcy) / pry) ** 2
            if e <= 1:
                c = mix(src[x * S, y * S][:3], WATER[2], 0.7)
                rx_ = 12 - abs(y - pcy) * 0.5
                wob = round(math.sin(y * 1.0 + _PH['t']) * 1.9)
                if abs(x - HATCH[0] - wob) < rx_ and (y % 2 == 0 or abs(x - HATCH[0] - wob) < 4):
                    c = mix(c, WARM, 0.45 * (1 - abs(x - HATCH[0]) / max(rx_, 1)))   # el registre, reflectit
                if math.sin(x * 0.22 + y * 1.6 - _PH['t']) > 0.94:
                    c = mix(c, (120, 150, 140), 0.25)
                if 0.86 < e:
                    c = mix(c, (60, 80, 78), 0.25)                          # la vora mullada, més clara
                cv.flat(x, y, c)


def beam(cv):
    """El feix de llum amb pols, per damunt de tot."""
    for y in range(CEIL, FLOOR_Y + 32):
        for x in range(HATCH[0] - 107, HATCH[0] + 108):
            b = _beam(x, y)
            if b > 0.02:
                k = 0.26 * b
                if hr(x, y, 55) > 0.996:
                    k = 0.6                                                # pols suspesa
                cv.flat(x, y, mix(cv.get(x, y), (255, 228, 170), k))


# ─── El cartell, el filtre ─────────────────────────────────────────────────

def sign(cv):
    """Cartell esmaltat de 1984: «AIGUA NO POTABLE» (amb la lletra gran) i una gota que somriu."""
    x0, y0, x1, y1 = 74, 96, 204, 141
    rrect(cv, x0, y0, x1, y1, 4, ENAMEL, lambda x, y: 3.4 - (y - y0) * 0.01)
    rrect(cv, x0 + 3, y0 + 3, x1 - 3, y1 - 3, 3, ENRED, 2.6)
    rrect(cv, x0 + 5, y0 + 5, x1 - 5, y1 - 5, 2, ENAMEL, 3.6)
    # la gota que somriu, a l'esquerra
    gx, gy = 99, 123
    cv.disc(gx, gy, 9, 9, DROPB, lambda nx, ny: 3.2 - nx * 0.8 - ny * 0.8)
    cv.poly([(gx - 7, gy - 6), (gx, gy - 18), (gx + 7, gy - 6)], DROPB, lambda x, y: 3.4 - (x - gx) * 0.08)
    for px, py in ((gx - 4, gy - 5), (gx - 3, gy - 7), (gx - 5, gy - 3), (gx - 2, gy - 9)):
        cv.put(px, py, DROPB, 4.8)                                       # la lluentor
    for ex in (gx - 3, gx + 3):                                          # els ulls
        cv.flat(ex, gy - 1, (10, 16, 30))
        cv.flat(ex, gy, (10, 16, 30))
    for dx in range(-4, 5):                                              # el somriure
        cv.flat(gx + dx, gy + 4 + (1 if -2 <= dx <= 2 else 0), (10, 16, 30))
    cv.flat(gx - 5, gy + 2, (220, 120, 140))                             # les galtes
    cv.flat(gx + 5, gy + 2, (220, 120, 140))
    # el text, en dues línies, amb la lletra de 640
    bold, reg = font640(True), font640(False)
    ink = (150, 30, 28)
    tx0, tw = 114, 84
    lay = Canvas1x(transparent=True)                                     # (la lletra és en píxels de sala)
    for glyphs, s, y in ((bold, 'AIGUA', 100), (reg, 'NO POTABLE', 115)):
        w = font_width(glyphs, s)
        draw_text(lay.img, glyphs, s, tx0 + (tw - w) // 2, y, ink, outline=None)
    cv.blit(lay.img)
    text(cv, '1984', x1 - 9 - text_width('1984'), y1 - 12, None, 0, flat=(160, 140, 120))
    # esmalt saltat i un cargol rovellat a cada cantó
    for (bx, by) in ((x0 + 3, y0 + 3), (x1 - 4, y0 + 3), (x0 + 3, y1 - 4), (x1 - 4, y1 - 4)):
        cv.disc(bx, by, 1.5, 1.5, RUST, 3.0)
        cv.put(bx + 1, by + 1, RUST, 1.4)
    for i in range(12):
        cx, cy = x0 + int(hr(i, 61) * (x1 - x0)), y0 + int(hr(i, 62) * (y1 - y0))
        if x0 + 7 < cx < x1 - 7 and y0 + 7 < cy < y1 - 7:
            continue                                                    # l'esmalt salta a les vores
        cv.put(cx, cy, DARK, 2.0)
        cv.put(cx + 1, cy, RUST, 2.4)
        if hr(i, 63) > 0.5:
            cv.put(cx, cy + 1, RUST, 1.8)
    for x in range(x0 + 8, x1 - 8):                                    # regalimades de rovell
        if hr(x, 71) > 0.9:
            for y in range(y1 + 1, y1 + 5 + int(hr(x, 72) * 11)):
                cv.flat(x, y, mix(cv.get(x, y), RUST[3], 0.5))


def filter_housing(cv):
    """La carcassa del filtre: un cilindre d'acer amb la tapa de cargols, entre els dos tubs, sobre un peu."""
    cx, x0, x1 = 445, 421, 469
    # els tubs, que entren i surten per la paret (amb les brides)
    hpipe(cv, 347, x0, 149, 4, STEELF, 3.0, bands=(365, 400), band_ramp=WHITEP)
    vpipe(cv, 349, CEIL, 149, 4, STEELF, 2.8)
    cv.disc(349, 149, 4, 4, STEELF, 3.2)
    hpipe(cv, x1, 560, 176, 4, STEELF, 3.0, bands=(507,), band_ramp=WHITEP)
    vpipe(cv, 560, 176, FLOOR_Y + 5, 4, STEELF, 2.8)
    cv.disc(560, 176, 4, 4, STEELF, 3.2)
    for fx, fy0, fy1 in ((349, 60, 63), (560, 194, 197)):                # brides als tubs verticals
        box(cv, fx - 6, fy0, fx + 6, fy1, STEELF, 3.4)
        cv.put(fx - 4, fy0 + 1, STEELF, 5.0)
        cv.put(fx + 4, fy0 + 1, STEELF, 5.0)
    for fx in (380, 530):                                                # brides als horitzontals
        y = 149 if fx < x0 else 176
        box(cv, fx, y - 6, fx + 3, y + 6, STEELF, 3.4)
    # el peu, amb els cargols d'ancoratge
    box(cv, 429, 187, 461, FLOOR_Y + 8, STEELF, 2.4)
    box(cv, x0, FLOOR_Y + 4, x1, FLOOR_Y + 9, STEELF, 2.0)
    for bx in (x0 + 3, x1 - 3):
        cv.put(bx, FLOOR_Y + 5, STEELF, 4.6)
    # el cos (cilindre), amb les costures
    for y in range(133, 189):
        for x in range(x0, x1 + 1):
            u = (x - cx) / ((x1 - x0) / 2 + 0.5)
            lv = 3.6 + 1.6 * (-0.3 - u) - 0.9 * u * u
            if y in (148, 174):
                lv -= 0.9
            cv.put(x, y, STEELF, lv)
    cv.disc(cx, 188, (x1 - x0) / 2, 4, STEELF, lambda nx, ny: 2.4 - nx)
    # la tapa (brida amb cargols), una mica desplaçada: algú l'ha oberta i tancada
    cv.disc(cx + 1, 131, (x1 - x0) / 2 + 4, 7, STEELF, lambda nx, ny: 4.4 - nx * 1.2 - ny * 1.4)
    cv.disc(cx + 1, 129, (x1 - x0) / 2 - 3, 4, STEELF, lambda nx, ny: 3.4 - nx - ny)
    for a in range(0, 360, 30):
        bolt(cv, cx + 1 + round(math.cos(math.radians(a)) * 25), 131 + round(math.sin(math.radians(a)) * 5), STEELF, 4.4)
    cv.hline(cx - 22, cx - 12, 133, STEELF, 5.2)                         # la marca brillant de la clau, recent
    box(cv, cx - 4, 119, cx + 6, 124, STEELF, 4.6)                       # la maneta de la tapa
    cv.vline(cx - 2, 124, 126, STEELF, 3.0)
    cv.vline(cx + 4, 124, 126, STEELF, 3.0)
    # placa i manòmetre
    box(cv, cx - 14, 152, cx + 14, 162, BRASS, 4.4)
    text(cv, 'FILTRE', cx - text_width('FILTRE') // 2, 155, None, 0, flat=(40, 24, 8))
    for bx in (cx - 12, cx + 12):
        cv.put(bx, 157, BRASS, 5.0)
    cv.disc(x1 + 11, 157, 6, 6, STEELF, 2.0)
    cv.disc(x1 + 11, 157, 4.5, 4.5, WHITEP, 4.4)
    for a in range(150, 391, 40):
        cv.put(x1 + 11 + round(math.cos(math.radians(a)) * 3.5), 157 + round(math.sin(math.radians(a)) * 3.5), DARK, 1.0)
    cv.line(x1 + 11, 157, x1 + 8, 160, DARK, 0)                          # a zero
    cv.put(x1 + 11, 157, DARK, 0)
    vpipe(cv, x1 + 11, 163, 173, 1, STEELF, 3.0)
    # rovell que regalima de la tapa
    rust_streaks(cv, x0 + 3, 133, x1 - 3, 187, 14, k=0.5, seed=8)


def ladder(cv):
    """L'escala de mà que baixa del registre fins al fons."""
    vladder(cv, HATCH[0] - 12, HATCH[0] + 12, 19, FLOOR_Y + 11, ramp=STEELF, lvl=3.4, step=13)
    cv.darken(HATCH[0] - 13, FLOOR_Y + 11, HATCH[0] + 16, FLOOR_Y + 16, 0.5)
    for y in (90, 170):                                                  # les grapes a la paret
        box(cv, HATCH[0] - 16, y, HATCH[0] - 11, y + 3, STEELF, 3.0)
        box(cv, HATCH[0] + 11, y, HATCH[0] + 16, y + 3, STEELF, 2.6)


# ─── Muntatge ─────────────────────────────────────────────────────────────

def _base(cv):
    walls(cv)
    ceiling(cv)
    sign(cv)
    floor(cv)
    filter_housing(cv)
    ladder(cv)
    beam(cv)
    glow(cv, HATCH[0], HATCH[1] - 5, 53, WARM, 0.45)


def bg(cv):
    _base(cv)


def _frames_gota():
    """Una gota que es forma al sostre, cau al bassal i hi fa una rodoneta."""
    base = Canvas(light=LIGHT)
    _base(base)
    gx, top, pool = 381, 35, 240
    seq = [('f', 0), ('f', 1), ('f', 2), ('f', 3)] + [('c', y) for y in range(top + 8, pool, 29)] \
        + [('r', 2), ('r', 4), ('r', 6), ('r', 8)] + [('n', 0)] * 30
    frames = []
    for kind, v in seq:
        cv = Canvas(light=LIGHT, img=base.img.copy())
        if kind == 'f':                                     # es forma
            for k in range(v + 1):
                cv.flat(gx, top + k, (150, 180, 180) if k < v else (200, 220, 220))
        elif kind == 'c':                                   # cau
            cv.flat(gx, v, (190, 210, 210))
            cv.flat(gx, v + 1, (160, 186, 186))
            cv.flat(gx, v - 1, (110, 140, 140))
        elif kind == 'r':                                   # rodoneta
            for a in range(0, 360, 15):
                x = gx + round(math.cos(math.radians(a)) * v * 1.6)
                y = pool + round(math.sin(math.radians(a)) * v * 0.4)
                cv.flat(x, y, mix(cv.get(x, y), (160, 190, 180), 0.5 - v * 0.04))
        frames.append(_diff(cv.img, base.img))
    return frames


def _frames_bassal():
    """L'aigua del bassal: el reflex del registre ondula i les ratlles de llum corren (bucle de 12)."""
    base = Canvas(light=LIGHT)
    _base(base)
    frames = []
    try:
        for i in range(12):
            _PH['t'] = 2 * math.pi * i / 12
            cv = Canvas(light=LIGHT)
            _base(cv)
            frames.append(_diff(cv.img, base.img))
    finally:
        _PH['t'] = 0.0
    return frames


def _frames_pols():
    """Motes de pols que suren lentament dins el feix del registre i fan pampallugues."""
    base = Canvas(light=LIGHT)
    _base(base)
    n, motes = 48, []
    for k in range(40):
        y = 45 + hr(k, 1, 88) * (FLOOR_Y - 40)
        t = (y - CEIL) / (FLOOR_Y + 27 - CEIL)
        x = HATCH[0] + (hr(k, 2, 88) - 0.5) * (40 + t * 93)
        motes.append((x, y, 3 + hr(k, 3, 88) * 7, 4 + hr(k, 4, 88) * 8, hr(k, 5, 88) * 6.283, 1 + int(hr(k, 6, 88) * 2)))
    frames = []
    for i in range(n):
        cv = Canvas(light=LIGHT, img=base.img.copy())
        a = 2 * math.pi * i / n
        for (x0, y0, ax, ay, ph, sp) in motes:
            x = round(x0 + math.sin(a * sp + ph) * ax)
            y = round(y0 + math.sin(a + ph * 1.7) * ay)
            b = _beam(x, y)
            tw = 0.5 + 0.5 * math.sin(a * 3 + ph * 2)
            if b > 0.15 and tw > 0.25:
                cv.flat(x, y, mix(cv.get(x, y), (255, 236, 190), min(0.75, 0.35 + b * 0.5 * tw)))
        frames.append(_diff(cv.img, base.img))
    return frames


ANIMS = {'gota': {'frames': _frames_gota, 'frameDuration': 90},
         'bassal': {'frames': _frames_bassal, 'frameDuration': 200},
         'pols': {'frames': _frames_pols, 'frameDuration': 130}}

PROPS = {}
