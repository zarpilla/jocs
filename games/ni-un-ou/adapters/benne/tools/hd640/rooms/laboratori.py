"""
Prova de resolució: el laboratori de l'Arenga a 640×360 (la composició de hd/rooms/laboratori.py ×4/3, dibuixada
de nou amb el detall que hi cap). Mateixes rampes, mateixos props i mateixes animacions.

  - la porta estanca del passadís a l'esquerra (oberta), amb el rètol SORTIDA;
  - l'ull de bou, la bata i l'armilla salvavides penjades;
  - la carta dels punts de mostreig: costa, isòbates, rosa dels vents i els punts 1-7 (el 7, encerclat);
  - el prestatge de pots amb etiquetes i el taulell (lupa binocular, gradeta, llibre de peixos, `portatil`, `nota`);
  - la nevera de mostres (pots numerats per punt, el forat del 7, el visor) i la pica del racó.
"""
import math

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from hd.pix import Canvas, Light, W, H, hr, mix, B4  # noqa: F401
from hd.rooms.arenga import box, rrect, bolt, hpipe, vpipe, glow, CAB, DARK, WHITEP, REDP, YELL, BRASS, WARM
from hd.rooms.comu import _diff, text, text_width
from hd.rooms.principal import (CREAM, TEAK, LINO, DOORP, NIGHT, DAYSKY, DAYSEA, LAMP as LAMPR, in_door, sill,
                               porthole as _porthole, day_porthole, foot_shadow, floor_shadow)
from hd.rooms.laboratori import SOCOL, EPOXY, GLASSB, PAPERC, BLUEB, GREENS

S = 4 / 3
CEIL_H = 24
FLOOR_Y = 203
BOTTOM = 260                      # per sota hi ha la barra de verbs
LAMPS = ((200, 27), (483, 27))
VP = (320, 40)

LIGHT = Light(ambient=0.5, vignette=(80, 35), floor_fade=None)
LIGHT.point(200, 35, r=227, k=2.4, squash=1.05, down=True, power=1.5)
LIGHT.point(483, 35, r=213, k=2.2, squash=1.05, down=True, power=1.5)
LIGHT.point(293, 133, r=80, k=0.5, power=2.0)                  # la pantalla del portàtil (poqueta)

INK = (34, 30, 26)
TEAL = [(6, 22, 16), (10, 38, 28), (16, 58, 42), (26, 82, 58), (40, 108, 76), (62, 138, 98)]


# ─── Paret, sostre i terra (principal.py, a 640) ─────────────────────────────

def wall(cv, lvl=4.6, frames=96, frame0=-13, seam=85, dado=171, rail=144, seed=2):
    for y in range(CEIL_H, FLOOR_Y):
        for x in range(W):
            cv.put(x, y, CREAM, lvl + (hr(x // 3, y // 5, seed) - 0.5) * 0.25)
    for fx in range(frame0, W, frames):
        for x in range(max(0, fx), min(W - 1, fx + 5) + 1):
            d = x - fx
            for y in range(CEIL_H, dado):
                cv.put(x, y, CREAM, lvl + (0.9 if d == 0 else 0.5 if d == 1 else -0.6 if d >= 4 else 0.1))
        for y in range(CEIL_H + 10, dado - 5, 14):
            if 0 <= fx + 2 <= W - 1:
                bolt(cv, fx + 2, y, CREAM, lvl + 0.2)
    for x in range(W):                                               # la soldadura
        cv.put(x, seam, CREAM, lvl - 1.1)
        cv.put(x, seam + 1, CREAM, lvl + 0.7 if hr(x // 2, seam) > 0.3 else lvl + 0.1)
    # taques de rovell a la soldadura
    for i in range(12):
        sx = int(hr(i, 81) * W)
        for k in range(2 + int(hr(i, 82) * 6)):
            cv.flat(sx, seam + 2 + k, mix(cv.get(sx, seam + 2 + k)[:3], (130, 80, 46), 0.35 - k * 0.04))
    # sòcol de fusta
    for y in range(dado, FLOOR_Y):
        for x in range(W):
            plank = (x + 9 * ((y - dado) // 8)) % 31
            v = 3.0 + (hr(x // 6, (y - dado) // 8, seed) - 0.5) * 0.6 - (0.9 if plank == 0 else 0)
            if (y - dado) % 8 == 0:
                v -= 0.8
            if hr(x // 2, y, 3) > 0.93:                                # la veta
                v += 0.5
            cv.put(x, y, TEAK, v)
    cv.hline(0, W - 1, dado, TEAK, 4.6)
    cv.hline(0, W - 1, dado + 1, TEAK, 3.8)
    cv.hline(0, W - 1, FLOOR_Y - 1, TEAK, 1.4)
    # el passamans
    hpipe(cv, 0, W - 1, rail, 3, TEAK, 3.8)
    for x in range(19, W, 75):
        cv.rect(x, rail + 4, x + 2, rail + 8, BRASS, 3.2)
        cv.rect(x - 1, rail + 8, x + 3, rail + 9, BRASS, 2.6)


def ceiling(cv):
    for y in range(0, CEIL_H + 1):
        for x in range(W):
            cv.put(x, y, CREAM, 3.0 + y * 0.03)
    for bx in range(-13, W, 96):
        box(cv, max(0, bx - 3), 0, min(W - 1, bx + 9), CEIL_H + 3, CREAM, 3.6, grad=0.6)
    # safata de cables
    cv.hline(0, W - 1, 5, CAB, 2.6)
    cv.hline(0, W - 1, 10, CAB, 1.8)
    for x in range(0, W, 8):
        cv.vline(x, 5, 10, CAB, 2.2)
    for x in range(W):
        if hr(x // 12, 4) > 0.4:
            cv.flat(x, 7, [(40, 36, 30), (70, 50, 34), (110, 40, 34), (30, 40, 60)][int(hr(x // 14, 5) * 4)])
        if hr(x // 9, 6) > 0.6:
            cv.flat(x, 8, [(50, 46, 40), (30, 40, 60), (90, 40, 34)][int(hr(x // 10, 7) * 3)])
    hpipe(cv, 0, W - 1, 15, 3, REDP, 3.6, bands=range(40, W, 120), band_ramp=WHITEP)        # contra incendis
    hpipe(cv, 0, W - 1, 21, 1, WHITEP, 3.4, bands=range(80, W, 120),
          band_ramp=[(10, 30, 70), (20, 60, 130), (60, 110, 190), (130, 170, 230)])
    for x in range(26, W, 120):                                      # abraçadores dels tubs
        cv.rect(x, 11, x + 2, 23, CAB, 3.0)
    cv.hline(0, W - 1, CEIL_H + 1, CREAM, 2.2)


def lamp(cv, lx, ly):
    box(cv, lx - 11, ly - 4, lx + 11, ly, CAB, 3.4)
    cv.hline(lx - 10, lx + 10, ly - 3, CAB, 4.6)
    cv.disc(lx, ly + 4, 9, 5, LAMPR, 2.6, lit=0)
    cv.disc(lx - 2, ly + 3, 4, 2, LAMPR, 3.4, lit=0)
    cv.hline(lx - 9, lx + 9, ly + 4, CAB, 2.4, lit=0)
    for gx in (-6, -3, 0, 3, 6):
        cv.vline(lx + gx, ly + 1, ly + 9, CAB, 2.4, lit=0)
    for bx in (lx - 9, lx + 8):
        cv.put(bx, ly - 2, CAB, 5.0)


def lamp_glow(cv, lx, ly):
    glow(cv, lx, ly + 5, 48, WARM, 0.5)
    glow(cv, lx, ly + 5, 16, (255, 240, 200), 0.6)


def lino(cv, lvl=4.0):
    mask = [[False] * W for _ in range(H)]
    for y in range(FLOOR_Y, H):
        d = y - VP[1]
        v = 3467 / d
        for x in range(W):
            u = VP[0] + (x - VP[0]) * 200 / d
            u2 = VP[0] + (x + 1 - VP[0]) * 200 / d
            lv = lvl + (hr(int(u // 4), int(v * 2), 2) - 0.5) * 0.45
            if int(u // 80) != int(u2 // 80):
                lv -= 1.0
            cv.put(x, y, LINO, lv)
            mask[y][x] = True
    cv.hline(0, W - 1, FLOOR_Y, LINO, lvl - 1.6)
    return mask


def shine(cv, mask, lamps, col=WARM, refl=0.22):
    src = cv.img.copy().load()
    for y in range(FLOOR_Y + 1, H):
        depth = (y - FLOOR_Y) / (BOTTOM - FLOOR_Y)
        sy = 2 * FLOOR_Y - y
        for x in range(W):
            if not mask[y][x]:
                continue
            c = cv.get(x, y)[:3]
            kk = refl * max(0.0, 1 - depth * 1.6)
            if kk > 0 and 0 <= sy < H:
                c = mix(c, src[x, sy][:3], kk)
            for lx in lamps:
                g = math.exp(-((x - lx) / (5 + depth * 13)) ** 2) * (1 - min(1, depth) * 0.7)
                if g > 0.05:
                    if g * 0.9 > B4[y & 3][x & 3]:
                        c = mix(c, col, min(0.5, 0.18 + g * 0.3))
                    else:
                        c = mix(c, col, g * 0.15)
            cv.flat(x, y, c)


def door_frame(cv, x0, y0, x1, y1, lvl=5.2, r=11):
    for t in range(4):
        for y in range(y0 - t, y1 + 1):
            for x in range(x0 - t, x1 + t + 1):
                if in_door(x, y, x0 - t, y0 - t, x1 + t, y1 + 1, r + t) and \
                        not in_door(x, y, x0 - t + 1, y0 - t + 1, x1 + t - 1, y1 + 1, r + t - 1):
                    cv.put(x, y, CREAM, lvl - t * 0.7 + (0.6 if y < y0 + r else 0))
    cv.darken(x0 - 5, y1 + 1, x1 + 5, y1 + 4, 0.5)


def watertight_door(cv, x0=19, y0=88, x1=75, y1=FLOOR_Y):
    """La porta del passadís, oberta: el passadís de crema i linòleum vermell, amb un llum i una porta al fons."""
    cx = (x0 + x1) // 2
    for y in range(y0, y1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, CREAM, 3.4 - abs(x - cx) / 32 - (y - y0) / 120, lit=0.25)
    # la porta del fons del passadís, tancada, i el passamans
    rrect(cv, cx - 9, y0 + 30, cx + 9, y1 - 22, 4, DOORP, 2.0)
    cv.vline(cx + 5, y0 + 60, y0 + 66, BRASS, 2.6, lit=0.25)
    hpipe(cv, x0, x1, y1 - 46, 1, TEAK, 2.6)
    cv.rect(x0, y1 - 24, x1, y1 - 16, TEAK, 2.6, lit=0.25)
    cv.rect(x0, y1 - 15, x1, y1 - 1, LINO, lambda x, y: 2.6 + (y - y1 + 15) * 0.09, lit=0.2)
    for x in range(x0, x1 + 1, 6):                                   # les juntes del linòleum, en fuga
        cv.line(x, y1 - 1, cx + (x - cx) * 0.4, y1 - 14, LINO, 2.0, lit=0.2)
    cv.disc(cx, y0 + 13, 5, 2, [(120, 100, 60), (220, 190, 130), (250, 230, 190)], 1.6, lit=0)
    glow(cv, cx, y0 + 15, 18, (230, 200, 140), 0.35)
    door_frame(cv, x0, y0, x1, y1)
    sill(cv, x0, x1, y1, h=7)
    for x in range(x0 + 4, x1 - 2, 9):                               # cargols del llindar
        cv.put(x, y1 - 4, DOORP, 4.6)
    # la fulla, oberta contra la paret (de cantó)
    lx = x0 - 15
    cv.poly([(lx, y0 + 5), (x0 - 4, y0 - 1), (x0 - 4, y1 - 3), (lx, y1 - 5)], DOORP,
            lambda x, y: 3.6 - (x - lx) * 0.05)
    cv.vline(lx, y0 + 5, y1 - 5, DOORP, 2.2)
    cv.vline(x0 - 4, y0, y1 - 3, DOORP, 5.0)
    for dy in (y0 + 18, y1 - 24):                                    # les palanques
        box(cv, lx + 2, dy, lx + 7, dy + 3, CAB, 3.4)
    box(cv, lx + 3, (y0 + y1) // 2, lx + 7, (y0 + y1) // 2 + 8, BRASS, 3.2)
    # el rètol verd de SORTIDA
    w = text_width('SORTIDA') + 8
    box(cv, cx - w // 2, y0 - 22, cx + w // 2, y0 - 13, TEAL, 3.4)
    text(cv, 'SORTIDA', cx - w // 2 + 4, y0 - 20, None, 0, flat=(230, 250, 236))
    glow(cv, cx, y0 - 17, 22, (80, 220, 140), 0.15)


# ─── Ull de bou, bata i armilla ──────────────────────────────────────────────

PORT = (112, 101, 15)


def porthole(cv):
    cx, cy, r = PORT
    _porthole(cv, cx, cy, r, None, rim=4)
    # la palanca d'obrir (llautó), a sota
    box(cv, cx - 2, cy + r + 5, cx + 2, cy + r + 9, BRASS, 3.2)
    cv.put(cx, cy + r + 10, BRASS, 4.6)


def lab_coat(cv):
    for hx in (101, 125):                                            # els ganxos
        box(cv, hx - 1, 130, hx + 2, 134, BRASS, 3.6)
        cv.put(hx + 1, 135, BRASS, 4.6)
    # la bata
    cv.poly([(96, 136), (107, 135), (112, 144), (115, 189), (88, 192), (91, 144)], WHITEP,
            lambda x, y: 4.2 - (x - 88) * 0.03 + (0.5 if (x + y // 3) % 9 == 0 else 0))
    cv.poly([(97, 136), (104, 136), (101, 146)], WHITEP, 2.6)        # el coll
    cv.line(101, 137, 101, 191, WHITEP, 2.6)
    cv.line(93, 139, 89, 173, WHITEP, 3.0)                           # la màniga
    cv.line(108, 141, 112, 170, WHITEP, 2.8)
    for y in (151, 164, 177):
        cv.put(102, y, CAB, 3.0)
        cv.put(103, y, CAB, 2.0)
    box(cv, 105, 157, 111, 162, WHITEP, 3.6)                         # la butxaca, amb un bolígraf i un retolador
    cv.vline(107, 153, 158, BLUEB, 3.6)
    cv.vline(109, 154, 158, REDP, 3.6)
    box(cv, 92, 147, 98, 151, [(150, 40, 40), (200, 70, 60), (230, 120, 100)], 1.6, edge=False)   # l'escut de Mar Obert
    cv.put(95, 149, WHITEP, 5.0)
    # l'armilla salvavides
    cv.poly([(119, 136), (132, 136), (136, 147), (135, 173), (116, 173), (115, 147)], REDP,
            lambda x, y: 4.4 - (x - 115) * 0.04)
    cv.poly([(122, 136), (129, 136), (126, 142)], WHITEP, 2.0)
    cv.vline(125, 140, 173, REDP, 2.6)
    for y in (152, 163):
        cv.hline(116, 135, y, [(120, 120, 110), (220, 220, 200), (250, 250, 240)], 1.8)
        cv.hline(116, 135, y + 1, [(120, 120, 110), (220, 220, 200), (250, 250, 240)], 1.2)
    box(cv, 123, 166, 128, 169, CAB, 3.4)                            # la sivella
    cv.disc(131, 141, 1.5, 1.5, [(30, 30, 30), (200, 200, 190)], 1.4)   # el xiulet


# ─── La carta dels punts de mostreig ─────────────────────────────────────────

CHART = (171, 40, 285, 93)
POINTS = ((222, 51), (232, 59), (243, 53), (248, 67), (259, 61), (264, 77), (272, 83))


def sample_chart(cv):
    x0, y0, x1, y1 = CHART
    box(cv, x0, y0, x1, y1, PAPERC, 3.6)
    for y in range(y0 + 2, y1 - 1):
        for x in range(x0 + 2, x1 - 1):
            coast = 200 + 13 * math.sin(y * 0.19) + (y - y0) * 0.5 + 3 * math.sin(y * 0.7)
            if x < coast:
                cv.put(x, y, [(120, 110, 80), (170, 158, 120), (206, 196, 160)], 1.4 + (0.3 if (x * 3 + y) % 11 == 0 else 0))
            else:
                dd = x - coast
                lv = 1.3 + min(0.6, dd / 60)
                if int(dd) in (6, 16, 30):                                # isòbates
                    lv -= 0.6
                cv.put(x, y, [(90, 120, 140), (130, 160, 176), (176, 200, 210)], lv)
    for y in range(y0 + 2, y1 - 1):                                  # el contorn de la costa
        coast = 200 + 13 * math.sin(y * 0.19) + (y - y0) * 0.5 + 3 * math.sin(y * 0.7)
        cv.flat(round(coast), y, (90, 80, 56))
    # la graella de coordenades
    for gx in range(x0 + 20, x1 - 2, 24):
        for y in range(y0 + 2, y1 - 1, 2):
            cv.flat(gx, y, mix(cv.get(gx, y)[:3], (110, 120, 130), 0.35))
    for gy in range(y0 + 14, y1 - 2, 16):
        for x in range(x0 + 2, x1 - 1, 2):
            cv.flat(x, gy, mix(cv.get(x, gy)[:3], (110, 120, 130), 0.35))
    # el rumb, els punts i el 7 encerclat
    for (ax, ay), (bx, by) in zip(POINTS, POINTS[1:]):
        n = max(abs(bx - ax), abs(by - ay))
        for i in range(0, n + 1):
            if i % 3 != 2:
                cv.flat(round(ax + (bx - ax) * i / n), round(ay + (by - ay) * i / n), (60, 70, 90))
    for i, (px, py) in enumerate(POINTS):
        cv.rect(px - 1, py - 1, px, py, [(20, 30, 50)], 0, lit=0)
        if i < 6:
            text(cv, str(i + 1), px + 2, py - 7, None, 0, flat=(50, 60, 80))
    px, py = POINTS[6]
    cv.ring(px, py, 6, REDP, 5.0, step=10)
    cv.ring(px, py, 5, REDP, 4.2, step=12)
    text(cv, '7', px - 10, py - 3, None, 0, flat=(170, 30, 30))
    # rosa dels vents
    rx, ry = x0 + 14, y0 + 12
    for dx, dy in ((0, -6), (0, 6), (-6, 0), (6, 0)):
        cv.line(rx, ry, rx + dx, ry + dy, [(60, 50, 40), (100, 90, 70)], 0.6)
    cv.put(rx, ry - 7, REDP, 4.0)
    # títol i escala
    text(cv, 'PUNTS', x0 + 6, y1 - 9, None, 0, flat=INK)
    for i, x in enumerate(range(x0 + 30, x0 + 54)):
        cv.flat(x, y1 - 5, INK if (i // 6) % 2 == 0 else (200, 196, 180))
    # xinxetes
    for x, y in ((x0 + 3, y0 + 3), (x1 - 3, y0 + 3), (x0 + 3, y1 - 3), (x1 - 3, y1 - 3)):
        cv.disc(x, y, 1.5, 1.5, [(120, 20, 20), (210, 50, 40), (250, 140, 120)], 1.4, lit=0.3)
    # l'ombra del paper a la paret
    cv.darken(x0 + 2, y1 + 1, x1 + 1, y1 + 2, 0.5)
    cv.darken(x1 + 1, y0 + 2, x1 + 2, y1 + 2, 0.5)


# ─── Pots, prestatge i taulell ───────────────────────────────────────────────

LIQUIDS = [(70, 100, 80), (110, 100, 60), (60, 80, 100), (90, 110, 70), (120, 90, 60)]


def jar(cv, x, y, h=12, w=7, liquid=(60, 90, 70), cap=REDP, lvl=3.0, label=True, fill=0.55, seed=0):
    """Pot de mostres (x, y = cantó de baix a l'esquerra): vidre, líquid amb sediment, tapa i etiqueta escrita."""
    top = y - h
    lt = top + 3 + round((h - 3) * (1 - fill))
    for yy in range(top + 2, y + 1):
        for xx in range(x, x + w):
            u = (xx - x) / max(1, w - 1)
            col = mix(cv.get(xx, yy)[:3], (170, 190, 186), 0.35 + 0.25 * (1 - u))
            if yy >= lt:
                col = mix(col, liquid, 0.65)
                if yy >= y - 1:                                       # el sediment
                    col = mix(col, (60, 50, 34), 0.5)
            cv.flat(xx, yy, col)
    for xx in range(x + 1, x + w - 1):                               # el menisc
        cv.flat(xx, lt, mix(cv.get(xx, lt)[:3], (210, 220, 210), 0.3))
    cv.vline(x, top + 2, y, GLASSB, 5.4)                             # la llum al vidre
    cv.vline(x + 1, top + 3, y - 2, GLASSB, 4.4)
    cv.vline(x + w - 1, top + 2, y, GLASSB, 1.6)
    box(cv, x, top, x + w - 1, top + 2, cap, lvl + 0.8, edge=False)
    cv.hline(x, x + w - 1, top, cap, lvl + 1.8)
    if label and h >= 10:
        ly0 = y - 6
        cv.rect(x + 1, ly0, x + w - 2, y - 2, PAPERC, 4.0)
        for xx in range(x + 2, x + w - 2):
            if hr(xx, seed, 5) > 0.4:
                cv.flat(xx, ly0 + 1, (60, 60, 80))
            if hr(xx, seed, 6) > 0.55:
                cv.flat(xx, ly0 + 3, (60, 60, 80))


def shelf(cv):
    x0, x1, y = 301, 453, 109
    box(cv, x0, y, x1, y + 4, TEAK, 4.4)
    cv.hline(x0 + 1, x1 - 1, y, TEAK, 6.0)
    for bx in (x0 + 5, x1 - 5):                                      # escaires
        cv.poly([(bx - 1, y + 5), (bx + 2, y + 5), (bx + 2, y + 16), (bx - 1, y + 8)], CAB, 3.2)
        cv.put(bx, y + 7, CAB, 5.0)
    cv.hline(x0, x1, y - 8, BRASS, 3.6)                              # la barana
    cv.hline(x0, x1, y - 7, BRASS, 2.0)
    for bx in range(x0 + 2, x1, 24):
        cv.vline(bx, y - 8, y - 1, BRASS, 3.0)
    caps = [REDP, BLUEB, WHITEP, YELL]
    x, i = x0 + 6, 0
    while x < x1 - 11:
        h = 11 + int(hr(i, 51) * 8)
        w = 7 + int(hr(i, 52) * 4)
        jar(cv, x, y - 1, h, w, LIQUIDS[i % 5], caps[int(hr(i, 53) * 4)], 3.0, fill=0.4 + hr(i, 55) * 0.5, seed=i)
        x += w + 2 + int(hr(i, 54) * 3)
        i += 1
    cv.darken(x0 + 2, y + 5, x1 - 2, y + 7, lambda xx, yy: 0.6 - (yy - y - 5) * 0.2)


BENCH = (139, 141, 459, 213)      # x0, y_sobre (darrere), x1, y del sòcol


def bench(cv):
    x0, ytop, x1, ybot = BENCH
    cv.poly([(x0 + 5, ytop), (x1 - 5, ytop), (x1, ytop + 9), (x0, ytop + 9)], EPOXY,
            lambda x, y: 3.2 + (y - ytop) * 0.09 + (hr(x // 3, y, 9) - 0.5) * 0.3)
    cv.hline(x0 + 5, x1 - 5, ytop, EPOXY, 2.0)
    cv.rect(x0, ytop + 10, x1, ytop + 13, EPOXY, 4.6)
    cv.hline(x0, x1, ytop + 10, EPOXY, 5.6)
    cv.hline(x0, x1, ytop + 14, CREAM, 1.2)
    fy0 = ytop + 15
    box(cv, x0 + 3, fy0, x1 - 3, ybot - 5, CREAM, 5.0, grad=1.2)
    cv.rect(x0 + 5, ybot - 5, x1 - 5, ybot, SOCOL, 1.4)
    n = 6
    cw = (x1 - x0 - 6) // n
    for i in range(n):
        cx0 = x0 + 3 + i * cw
        cx1 = cx0 + cw - 1
        box(cv, cx0 + 3, fy0 + 3, cx1 - 3, fy0 + 15, CREAM, 5.4)
        cv.hline(cx0 + 4, cx1 - 4, fy0 + 14, CREAM, 3.6)
        box(cv, (cx0 + cx1) // 2 - 6, fy0 + 8, (cx0 + cx1) // 2 + 6, fy0 + 9, CAB, 4.6)
        box(cv, (cx0 + cx1) // 2 - 4, fy0 + 4, (cx0 + cx1) // 2 + 4, fy0 + 6, WHITEP, 4.0, edge=False)   # etiqueta
        for xx in range((cx0 + cx1) // 2 - 3, (cx0 + cx1) // 2 + 4):
            if hr(xx, i, 11) > 0.45:
                cv.flat(xx, fy0 + 5, (70, 70, 80))
        box(cv, cx0 + 3, fy0 + 19, cx1 - 3, ybot - 9, CREAM, 5.0, grad=0.8)
        cv.hline(cx0 + 5, cx1 - 5, fy0 + 21, CREAM, 5.8)
        hx = cx1 - 8 if i % 2 == 0 else cx0 + 6
        box(cv, hx, fy0 + 24, hx + 2, fy0 + 33, CAB, 4.6)
        # la reixeta de ventilació de cada porta
        for yy in range(ybot - 18, ybot - 11, 2):
            cv.hline((cx0 + cx1) // 2 - 7, (cx0 + cx1) // 2 + 7, yy, CREAM, 3.4)
    for i in range(20):
        x = x0 + 5 + int(hr(i, 61) * (x1 - x0 - 10))
        cv.put(x, ybot - 7, CREAM, 2.4)
        cv.put(x + 1, ybot - 7, CREAM, 3.0)


def magnifier(cv):
    """La lupa binocular: peu, columna amb cremallera, capçal ivori, dos oculars, la llum de sota i la placa de Petri."""
    bx = 408
    box(cv, bx - 14, 143, bx + 21, 148, CAB, 3.2)
    cv.hline(bx - 13, bx + 20, 143, CAB, 4.6)
    cv.disc(bx, 143, 8, 1.5, [(60, 60, 50), (180, 180, 150), (250, 246, 210)], 2.0, lit=0)   # la llum de sota
    vpipe(cv, bx + 16, 104, 143, 2, CAB, 4.2)
    for y in range(108, 140, 2):
        cv.put(bx + 14, y, CAB, 1.6)
    box(cv, bx + 5, 109, bx + 19, 115, CAB, 3.6)
    rrect(cv, bx - 9, 106, bx + 9, 124, 4, WHITEP, lambda x, y: 4.6 - (x - bx) * 0.04 - (y - 106) * 0.04)
    cv.hline(bx - 6, bx + 6, 106, WHITEP, 5.6)
    cv.hline(bx - 7, bx + 7, 116, WHITEP, 3.0)
    vpipe(cv, bx, 125, 132, 4, CAB, 3.8)
    cv.hline(bx - 4, bx + 4, 130, CAB, 5.4)
    for ox in (-5, 3):
        for k in range(10):
            cv.put(bx + ox - k // 2, 105 - k, CAB, 2.6)
            cv.put(bx + ox + 1 - k // 2, 105 - k, CAB, 4.0)
            cv.put(bx + ox + 2 - k // 2, 105 - k, CAB, 3.2)
        cv.hline(bx + ox - 6, bx + ox - 1, 95, CAB, 1.4)
        cv.hline(bx + ox - 6, bx + ox - 1, 96, CAB, 4.6)
    cv.disc(bx, 139, 9, 2.5, GLASSB, 3.6)
    cv.disc(bx, 139, 5, 1.5, [(40, 70, 50), (80, 120, 80), (130, 160, 110)], 1.4)
    cv.put(bx - 2, 138, [(130, 160, 110)], 0)
    cv.disc(bx + 16, 120, 3, 3, CAB, lambda nx, ny: 4.6 - nx - ny)
    cv.disc(bx + 16, 128, 2, 2, CAB, lambda nx, ny: 4.2 - nx - ny)


RACK = (352, 395)


def jar_rack(cv):
    x0, x1 = RACK
    box(cv, x0, 139, x1, 148, TEAK, 4.0)
    for i, x in enumerate(range(x0 + 3, x1 - 4, 8)):
        jar(cv, x, 139, 13, 6, LIQUIDS[[0, 2, 1, 3, 4][i % 5]], [REDP, BLUEB, WHITEP][i % 3], 3.0, label=False,
            fill=0.7, seed=40 + i)
    cv.hline(x0, x1, 141, TEAK, 5.0)
    for x in range(x0 + 4, x1 - 2, 8):                               # els forats de la gradeta
        cv.hline(x, x + 4, 144, TEAK, 2.2)
    # un retolador, una pipeta i una placa de Petri buida
    cv.line(331, 148, 344, 146, BLUEB, 4.0)
    cv.put(344, 146, CAB, 2.0)
    cv.line(235, 148, 253, 145, WHITEP, 4.2)
    cv.disc(253, 145, 1.5, 1, REDP, 3.6)


def fish_book(cv):
    x0, y0, x1, y1 = 187, 136, 235, 149
    cv.poly([(x0 + 4, y0), (x1 - 1, y0), (x1, y0 + 6), (x0, y0 + 6)], BLUEB, lambda x, y: 3.6 + (y - y0) * 0.08)
    cv.rect(x0, y0 + 7, x1, y1 - 1, PAPERC, lambda x, y: 3.2 + (0.6 if y % 2 else 0))
    cv.hline(x0, x1, y0 + 6, BLUEB, 2.2)
    cv.hline(x0, x1, y1, BLUEB, 2.0)
    cv.vline(x0, y0 + 6, y1, BLUEB, 2.6)
    cv.vline(x0 + 1, y0 + 6, y1, BLUEB, 3.6)
    # el peix de la tapa (de perfil, amb la cua)
    fish = [(202, 2), (203, 1), (204, 1), (205, 1), (206, 1), (207, 1), (208, 2), (209, 2), (210, 3), (211, 2),
            (203, 3), (204, 3), (205, 3), (206, 3), (207, 3), (208, 3), (209, 4), (210, 1), (205, 2), (206, 2), (207, 2)]
    for fx, fy in fish:
        cv.put(fx, y0 + fy, [(120, 150, 140), (170, 200, 180), (220, 236, 220)], 1.6)
    cv.flat(203, y0 + 2, (20, 30, 60))
    for px, col in ((219, YELL), (224, REDP), (228, YELL)):          # post-its
        cv.rect(px, y0 - 4, px + 3, y0, col, 4.4)
        cv.hline(px, px + 3, y0 - 4, col, 5.2)


def laptop(cv):
    """El portàtil de la Juana, obert, amb la pantalla de la contrasenya i adhesius de peixos."""
    x0, x1 = 264, 317
    box(cv, x0 + 3, 112, x1 - 3, 140, CAB, 2.4)
    cv.hline(x0 + 4, x1 - 4, 113, CAB, 3.4)
    cv.rect(x0 + 6, 115, x1 - 6, 137, [(10, 20, 34), (20, 40, 64), (40, 70, 100), (90, 130, 170), (190, 220, 240)],
            lambda x, y: 1.4 + (137 - y) * 0.016, lit=0)
    cv.disc(290, 120, 3, 3, [(90, 130, 170), (200, 220, 240)], 1.2, lit=0)            # l'avatar
    cv.disc(290, 119, 1, 1, [(40, 70, 100), (90, 130, 170)], 0.6, lit=0)
    text(cv, 'JUANA', 281, 125, None, 0, flat=(170, 200, 228))
    cv.rect(282, 131, 299, 134, [(90, 130, 170), (220, 236, 250)], 1.4, lit=0)        # el camp de la contrasenya
    for x in range(284, 294, 2):
        cv.flat(x, 132, (30, 50, 80))
        cv.flat(x, 133, (30, 50, 80))
    glow(cv, 290, 127, 24, (120, 170, 220), 0.25)
    # adhesius: un peix groc i una balena blava
    cv.rect(x0 + 4, 131, x0 + 6, 133, YELL, 4.0)
    cv.put(x0 + 3, 132, YELL, 3.0)
    cv.rect(x1 - 7, 115, x1 - 5, 116, BLUEB, 4.4)
    # la base, en perspectiva, amb el teclat i el ratolí tàctil
    cv.poly([(x0 + 3, 141), (x1 - 3, 141), (x1 + 2, 149), (x0 - 2, 149)], CAB, lambda x, y: 4.0 + (y - 141) * 0.08)
    for r, y in enumerate((142, 144, 146)):
        for x in range(x0 + 4 + r, x1 - 4 + r, 3):
            cv.put(x, y, CAB, 2.0)
            cv.put(x + 1, y, CAB, 2.4)
    cv.rect(286, 147, 296, 148, CAB, 2.8)
    cv.hline(x0 - 2, x1 + 2, 149, CAB, 2.0)
    cv.flat(x1 - 3, 148, (90, 255, 120))


def note(cv):
    x0, y0 = 323, 133
    cv.poly([(x0, 149), (x0 + 5, y0), (x0 + 18, y0), (x0 + 16, 149)], PAPERC, lambda x, y: 4.6 - (y - y0) * 0.025)
    cv.line(x0 + 5, y0, x0 + 18, y0, PAPERC, 5.6)
    for i, y in enumerate((137, 140, 143, 146)):
        for x in range(x0 + 5 - i // 2, x0 + 15 - i):
            if hr(x, y, 7) > 0.35:
                cv.put(x, y, BLUEB, 2.0)
    cv.line(x0 + 1, 149, x0 + 17, 149, PAPERC, 2.0)


# ─── La nevera i la pica ─────────────────────────────────────────────────────

FRIDGE = (483, 69, 587, 211)


def fridge(cv):
    x0, y0, x1, y1 = FRIDGE
    box(cv, x0, y0, x1, y1, WHITEP, 4.0, grad=0.8)
    box(cv, x0, y0, x1, y0 + 16, WHITEP, 4.4)
    cv.hline(x0 + 1, x1 - 1, y0 + 1, WHITEP, 5.4)
    cv.rect(x0 + 66, y0 + 4, x0 + 88, y0 + 11, [(4, 14, 8), (8, 30, 16)], 1.0, lit=0)     # el visor
    _display(cv, '4')
    cv.flat(x0 + 8, y0 + 8, (40, 140, 70))                           # el pilot
    for i in range(3):                                               # botons
        cv.disc(x0 + 20 + i * 7, y0 + 8, 1.5, 1.5, WHITEP, 2.6)
    text(cv, 'MOSTRES', x0 + 6, y0 + 22, None, 0, flat=(80, 80, 86))
    # la porta de vidre
    gx0, gy0, gx1, gy1 = x0 + 7, y0 + 30, x1 - 12, y1 - 19
    box(cv, gx0 - 3, gy0 - 3, gx1 + 3, gy1 + 3, CAB, 3.0)
    cv.rect(gx0, gy0, gx1, gy1, GLASSB, lambda x, y: 2.2 + (gy1 - y) * 0.008, lit=0.5)
    shelves = list(range(gy0 + 23, gy1 + 1, 23))
    for k, sy in enumerate(shelves):
        cv.hline(gx0, gx1, sy, WHITEP, 3.6, lit=0.5)
        cv.hline(gx0, gx1, sy + 1, WHITEP, 2.0, lit=0.5)
        # l'etiqueta del punt, a l'esquerra de cada fila
        box(cv, gx0 + 1, sy - 9, gx0 + 9, sy - 3, WHITEP, 3.8, edge=False)
        text(cv, 'P' + str(k + 1), gx0 + 2, sy - 8, None, 0, flat=(40, 44, 50))
        x, i = gx0 + 12, 0
        while x < gx1 - 8:
            if not (k == 0 and i == 3):                              # el forat del 7
                jar(cv, x, sy - 1, 14, 8, LIQUIDS[(i + k) % 4], [REDP, BLUEB, WHITEP][(i + k) % 3], 2.6,
                    fill=0.6 + hr(i, k, 3) * 0.3, seed=k * 10 + i)
            else:
                cv.rect(x + 1, sy - 2, x + 6, sy - 1, [(20, 34, 40), (40, 60, 66)], 1.0, lit=0.5)   # la marca del pot
            x += 11
            i += 1
    cv.tint(gx0, gy0, gx1, gy1, (150, 200, 230), 0.12)
    for i in range(0, 80):                                           # el reflex del vidre
        for d in (0, 1, 2, 9):
            px, py = gx0 + 8 + i // 2 + d, gy0 + i * 1.6
            if gy0 <= py <= gy1 and px <= gx1:
                cv.tint(px, int(py), px, int(py), (220, 240, 250), 0.25)
    box(cv, x1 - 9, gy0 + 26, x1 - 6, gy0 + 66, CAB, 4.4)            # tirador
    cv.vline(x1 - 8, gy0 + 27, gy0 + 65, CAB, 5.6)
    for hy in (gy0 + 5, gy1 - 8):
        box(cv, x0 + 1, hy, x0 + 4, hy + 5, CAB, 3.6)
    for y in range(y1 - 15, y1 - 4, 2):                              # reixa de baix
        cv.hline(x0 + 8, x1 - 8, y, WHITEP, 2.0)
    # el rètol groc: NO MENJAR
    w = text_width('NO MENJAR') + 6
    box(cv, x1 - w - 6, y0 + 20, x1 - 6, y0 + 28, YELL, 4.2, edge=False)
    text(cv, 'NO MENJAR', x1 - w - 3, y0 + 22, None, 0, flat=(40, 30, 10))
    # el termòmetre de registre, penjat al costat
    box(cv, x1 + 2, 120, x1 + 6, 146, WHITEP, 4.2)
    cv.vline(x1 + 4, 124, 142, REDP, 3.6)


_DIG = {'3': '111001111001111', '4': '101101111001001', 'C': '111100100100111'}


def _display(cv, temp):
    """El visor de la nevera: «4°C» en verd (xifres de 3×5)."""
    x0, y0 = FRIDGE[0] + 69, FRIDGE[1] + 5
    cv.rect(x0 - 2, y0 - 1, x0 + 18, y0 + 6, [(4, 14, 8), (8, 30, 16)], 1.0, lit=0)
    for dx, ch in ((0, temp), (8, 'C')):
        bits = _DIG[ch]
        for j in range(5):
            for m in range(3):
                if bits[j * 3 + m] == '1':
                    cv.put(x0 + dx + m, y0 + j, GREENS, 3.6, lit=0)
    cv.rect(x0 + 4, y0, x0 + 5, y0 + 1, GREENS, 3.0, lit=0)          # el grau
    glow(cv, x0 + 7, y0 + 2, 11, (90, 255, 140), 0.4)


def sink(cv):
    x0, x1 = 595, 639
    box(cv, x0, 147, x1, FLOOR_Y + 5, CREAM, 4.6, grad=1.0)
    box(cv, x0 - 3, 141, x1, 148, WHITEP, 4.6)
    cv.rect(x0 + 5, 143, x1 - 5, 146, CAB, 2.0)
    cv.disc(x0 + 20, 145, 2, 1, DARK, 0.4)                           # el desguàs
    vpipe(cv, 611, 125, 141, 1, CAB, 5.0)
    for a in range(0, 181, 10):
        cv.put(616 - round(math.cos(math.radians(a)) * 5), 125 - round(math.sin(math.radians(a)) * 5), CAB, 5.2)
    cv.put(621, 128, CAB, 4.0)
    cv.put(621, 129, CAB, 3.0)
    box(cv, 626, 133, 631, 138, REDP, 3.6)
    box(cv, 602, 135, 606, 138, BLUEB, 3.6)
    # el rotllo de paper i el dispensador de sabó
    box(cv, 603, 85, 632, 107, WHITEP, 4.0, grad=0.8)
    cv.hline(604, 631, 86, WHITEP, 5.0)
    cv.rect(609, 108, 625, 118, PAPERC, 4.6)
    cv.hline(609, 625, 108, PAPERC, 2.4)
    for y in (110, 114):
        cv.hline(610, 624, y, PAPERC, 3.8)
    rrect(cv, 634, 104, 639, 120, 2, [(20, 50, 30), (40, 90, 50), (70, 130, 80), (110, 170, 120)], 2.6)
    # el cartell NO BEURE
    w = text_width('NO BEURE') + 6
    box(cv, x0 + 3, 155, x0 + 3 + w, 166, WHITEP, 4.2)
    cv.rect(x0 + 5, 157, x0 + 1 + w, 158, REDP, 3.6)
    text(cv, 'NO BEURE', x0 + 6, 160, None, 0, flat=(40, 40, 44))
    cv.vline(x0 + 3, 171, FLOOR_Y, CREAM, 3.2)
    box(cv, x0 + 10, 180, x0 + 14, 186, CAB, 3.0)                    # la clau de pas


def bg(cv):
    wall(cv)
    ceiling(cv)
    hpipe(cv, 0, W - 1, 36, 3, BLUEB, 3.4, bands=range(53, W, 85), band_ramp=WHITEP)   # aigua dolça
    for x in range(20, W, 85):
        cv.rect(x, 31, x + 2, 41, CAB, 3.0)
    watertight_door(cv)
    porthole(cv)
    lab_coat(cv)
    sample_chart(cv)
    shelf(cv)
    mask = lino(cv)
    foot_shadow(cv, 0, W - 1, FLOOR_Y + 1, 5, 0.35)
    shine(cv, mask, [lx for lx, _ in LAMPS])
    bench(cv)
    magnifier(cv)
    jar_rack(cv)
    fish_book(cv)
    fridge(cv)
    sink(cv)
    for lx, ly in LAMPS:
        lamp(cv, lx, ly)
    cv.darken(BENCH[0], BENCH[3] + 1, BENCH[2], BENCH[3] + 5, lambda x, y: 0.8 - (y - BENCH[3]) * 0.16)
    cv.darken(480, FLOOR_Y + 9, 639, FLOOR_Y + 13, lambda x, y: 0.7 - (y - FLOOR_Y - 9) * 0.16)
    floor_shadow(cv, 112, FLOOR_Y + 4, 14, 2, 0.3)                   # sota la bata
    for lx, ly in LAMPS:
        lamp_glow(cv, lx, ly)


# ─── Props ──────────────────────────────────────────────────────────────────

def portatil(cv):
    laptop(cv)


def nota(cv):
    note(cv)


def remenat(cv):
    """Calaixos mal tancats, papers girats per terra i pel taulell, un pot tombat i la porta de l'armari entreoberta."""
    x0, ytop, x1, ybot = BENCH
    fy0 = ytop + 15
    cw = (x1 - x0 - 6) // 6
    for i in (0, 2, 3, 5):
        cx0 = x0 + 3 + i * cw
        cx1 = cx0 + cw - 1
        out = 7 + (i % 2) * 4
        cv.rect(cx0 + 3, fy0 + 3, cx1 - 3, fy0 + 4, DARK, 1.0)
        box(cv, cx0 + 2, fy0 + 4 + out, cx1 - 2, fy0 + 16 + out, CREAM, 5.4)
        cv.rect(cx0 + 3, fy0 + 4, cx1 - 3, fy0 + 3 + out, CREAM, 2.0)
        cv.vline(cx0 + 2, fy0 + 4, fy0 + 3 + out, CREAM, 4.4)
        cv.vline(cx1 - 2, fy0 + 4, fy0 + 3 + out, CREAM, 3.6)
        box(cv, (cx0 + cx1) // 2 - 6, fy0 + 9 + out, (cx0 + cx1) // 2 + 6, fy0 + 10 + out, CAB, 4.6)
        cv.rect(cx0 + 8, fy0 + 1, cx0 + 19, fy0 + 4, PAPERC, 4.6)
        cv.hline(cx0 + 9, cx0 + 17, fy0 + 2, BLUEB, 2.4)
    cx0 = x0 + 3 + 4 * cw
    cv.rect(cx0 + 4, fy0 + 20, cx0 + 13, ybot - 10, DARK, 0.8)
    cv.poly([(cx0 + 13, fy0 + 19), (cx0 + 24, fy0 + 16), (cx0 + 24, ybot - 5), (cx0 + 13, ybot - 9)], CREAM, 4.6)
    for px, py, w in ((155, 139, 16), (240, 137, 13), (336, 139, 12), (427, 140, 18)):
        cv.poly([(px, py + 8), (px + 4, py), (px + w + 4, py + 1), (px + w, py + 9)], PAPERC, 4.2)
        cv.hline(px + 4, px + w, py + 3, PAPERC, 3.0)
        cv.hline(px + 3, px + w - 1, py + 5, BLUEB, 2.2)
    cv.rect(384, 144, 396, 148, GLASSB, 4.6)
    box(cv, 396, 144, 399, 148, REDP, 4.0, edge=False)
    cv.disc(376, 149, 9, 2, [(30, 50, 40), (60, 90, 70), (100, 130, 110)], 1.6)
    for i, (px, py) in enumerate(((200, 227), (261, 235), (307, 221), (400, 229), (168, 243), (451, 240))):
        a = hr(i, 71) * 0.6 - 0.3
        dx, dy = round(math.cos(a) * 15), round(math.sin(a) * 3)
        cv.poly([(px, py), (px + dx, py + dy), (px + dx + 4, py + dy + 7), (px + 4, py + 7)], PAPERC,
                lambda x, y: 3.6 + (hr(x, y) - 0.5) * 0.3)
        if i % 2:
            cv.hline(px + 3, px + dx, py + 3, BLUEB, 2.0)
            cv.hline(px + 4, px + dx, py + 5, BLUEB, 2.0)
    cv.poly([(344, 245), (376, 243), (381, 253), (349, 256)],
            [(40, 60, 30), (70, 100, 50), (110, 140, 70), (150, 180, 100)], 2.2)


PROPS = {'portatil': portatil, 'nota': nota, 'remenat': remenat,
         'ulls_dia': lambda cv: day_porthole(cv, *PORT)}


# ─── Animacions ────────────────────────────────────────────────────────────

def _glass(cv, t, day):
    cx, cy, r = PORT
    ph = t * 2 * math.pi
    hz = cy + r * 0.15 + math.sin(ph) * 2.2
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if math.hypot(x - cx, y - cy) > r:
                continue
            crest = math.sin(x * 0.55 + y * 1.8 - ph * 2)
            if day:
                if y < hz:
                    cl = hr(int(x // 6), int(y // 3), 0)
                    cv.put(x, y, DAYSKY, 4.2 + (y - (cy - r)) / (r * 2.2) * 1.4 - (0.7 if cl > 0.75 else 0), lit=0.08)
                else:
                    cv.put(x, y, DAYSEA, 4.4 - (y - hz) / (r * 0.9) + (1.2 if crest > 0.8 else 0), lit=0.08)
            else:
                if y < hz:
                    cl = hr(int(x // 5), int(y // 3), 0)
                    cv.put(x, y, NIGHT, 2.0 + (hz - y) / (r * 2) + (0.8 if cl > 0.72 else 0), lit=0.1)
                else:
                    cv.put(x, y, NIGHT, 1.6 - (y - hz) / (r * 1.6) + (1.6 if crest > 0.85 else 0), lit=0.1)
    shine = (236, 240, 244) if day else (200, 210, 230)
    for i in range(-r // 2, r // 3):
        x, y = cx - r // 3 + i, cy - r // 2 - i // 2
        cv.flat(x, y, mix(cv.get(x, y), shine, 0.35))


def _base(day=False):
    cv = Canvas(light=LIGHT)
    bg(cv)
    if day:
        top = Canvas(light=LIGHT, transparent=True)
        PROPS['ulls_dia'](top)
        cv.img.alpha_composite(top.img)
    return cv.img


def _frames_port(day):
    base = _base(day)
    frames = []
    for i in range(12):
        cv = Canvas(light=LIGHT, img=base.copy())
        _glass(cv, i / 12, day)
        frames.append(_diff(cv.img, base))
    return frames


def _frames_portatil():
    frames = []
    for i in range(8):
        cv = Canvas(light=LIGHT, transparent=True)
        laptop(cv)
        if i < 4:
            cv.rect(295, 132, 295, 133, [(30, 50, 80)], 0, lit=0)
        led = 0.5 + 0.5 * math.cos(i / 8 * 2 * math.pi)
        cv.flat(314, 148, mix((20, 60, 34), (90, 255, 120), led))
        frames.append(cv.img)
    return frames


def _frames_nevera():
    base = _base()
    x0, y0 = FRIDGE[:2]
    frames = []
    for i in range(16):
        cv = Canvas(light=LIGHT, img=base.copy())
        _display(cv, '3' if 9 <= i <= 12 else '4')
        if i % 8 < 1:
            cv.flat(x0 + 8, y0 + 8, (210, 255, 220))
            glow(cv, x0 + 8, y0 + 8, 5, (90, 255, 120), 0.6)
        else:
            cv.flat(x0 + 8, y0 + 8, (40, 140, 70))
        frames.append(_diff(cv.img, base))
    return frames


def _frames_bombolla():
    """El pot del mig de la gradeta: una bombolla puja pel líquid (de 2 px quan s'acosta a dalt) i esclata."""
    base = _base()
    jx = RACK[0] + 3 + 2 * 8                                         # el tercer pot
    path = [(jx + 3, 137), (jx + 3, 136), (jx + 2, 135), (jx + 2, 134), (jx + 3, 133), (jx + 3, 132), (jx + 2, 131)]
    frames = []
    for i in range(18):
        cv = Canvas(light=LIGHT, img=base.copy())
        if i < len(path):
            x, y = path[i]
            cv.flat(x, y, mix(cv.get(x, y)[:3], (220, 236, 230), 0.7))
            if i >= 4:
                cv.flat(x + 1, y, mix(cv.get(x + 1, y)[:3], (200, 220, 214), 0.5))
        elif i == len(path):
            for dx in (-1, 2):
                cv.flat(jx + 2 + dx, 129, (200, 220, 214))
        frames.append(_diff(cv.img, base))
    return frames


ANIMS = {'mar': {'frames': lambda: _frames_port(False), 'frameDuration': 220},
         'ulls_dia_mar': {'frames': lambda: _frames_port(True), 'frameDuration': 220},
         'portatil': {'frames': _frames_portatil, 'frameDuration': 265},
         'nevera': {'frames': _frames_nevera, 'frameDuration': 250},
         'bombolla': {'frames': _frames_bombolla, 'frameDuration': 140}}


# ─── Geometria (640×360) ────────────────────────────────────────────────────

GEOMETRIA = {
    'things': {
        'porta': {'rect': (5, 67, 80, 203), 'walk': (48, 243)},
        'llibre': {'rect': (184, 131, 237, 151), 'walk': (211, 243)},
        'portatil': {'rect': (261, 111, 320, 151), 'walk': (291, 243)},
        'nota': {'rect': (321, 131, 343, 151), 'walk': (331, 243)},
        'taulell': {'rect': (139, 152, 459, 213), 'walk': (387, 243)},
        'nevera': {'rect': (483, 69, 587, 211), 'walk': (533, 243)},
    },
    'spawns': {'iri': (307, 253), 'vet': (400, 259), 'juana': (235, 240)},
    'walkable': [(16, 224), (624, 224), (635, 264), (5, 264)],
}
