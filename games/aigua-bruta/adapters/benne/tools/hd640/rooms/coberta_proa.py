"""
Prova a 640×360: la coberta de proa de l'Arenga (vegeu hd/rooms/coberta_proa.py, la de 480×270).
Mateixa composició ×4/3, dibuixada de nou. El cel, el mar, la borda, la coberta, la porta estanca, els focus, les
bites i el rotllo de cap són els de hd640/rooms/coberta_popa.py. Hi ha detall que a 480 no hi cabia: rètols
(PASSADÍS, BALSA), la cadena amb baules de veritat, el barbotí amb dents i radis, el tambor amb el cap enrotllat,
els cargols de la caixa d'engranatges, la manta de quadres amb serrell.
Props: `dia` (amb el racó de la Juana) i `cadenat`. ANIMS: `mar` (de nit) i `dia_mar` (de dia, amb dues gavines);
totes dues amb el cap de la campana que es gronxa.
"""
import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

import math

from hd.pix import Canvas, Light, W, H, hr, mix, GOLD
from hd.rooms.arenga import REDP
from hd.rooms.comu import _diff, text
from hd.rooms.exterior import smooth, HULLN, REDH, STEELX, CABX, ORANGEB, ROPE, WINDOW, GLOW_WARM
from hd640.rooms.coberta_popa import (night_sky, day_sky, night_sea, day_sea, bulwark, deck_floor, bitts, coil,
                                      wt_door, deck_lamp, gull)

K = 4 / 3
HOR = 115
RAIL = 141
FLOOR_Y = 203
HOUSE = (40, 149)                 # la caseta (porta del passadís)
DOOR = (61, 96, 117, 203)
HATCH = (296, 216, 376, 248)      # l'escotilla, a terra
BALSA = (421, 93, 536, 141)       # el contenidor de la balsa
MOON = (261, 40)
SUN = (40, 27)
MX = 571                          # el pal de proa

LIGHT = Light(ambient=-0.1, vignette=(67, 32), floor_fade=(264, 40))
LIGHT.point(89, 80, r=227, k=2.8, squash=1.1, down=True, power=1.4)       # focus sobre la porta
LIGHT.point(571, 61, r=280, k=2.6, squash=0.9, down=True, power=1.4)      # focus del pal de proa
LIGHT.point(19, 40, r=61, k=1.0, power=1.8)                                # llum del pas lateral
LIGHT.point(320, 267, r=347, k=0.6, squash=2.5, power=1.2)

LIGHT_DAY = Light(ambient=3.4, vignette=(53, 24), floor_fade=(267, 53))
LIGHT_DAY.point(80, -53, r=560, k=1.3, power=1.2)
LIGHT_DAY.add(lambda x, y: -1.6 if (x < HOUSE[0] - 3 and 29 <= y < 213) else 0.0)
LIGHT_DAY.add(lambda x, y: -1.2 if (429 <= x <= 531 and 144 <= y < 213) else 0.0)   # ombra sota la balsa

CHAIN = [(20, 16, 14), (40, 30, 24), (64, 48, 34), (92, 70, 48), (122, 96, 68), (150, 126, 96)]
GR = [(6, 20, 14), (10, 34, 24), (16, 52, 36), (26, 74, 50), (40, 98, 66), (60, 126, 86), (90, 150, 110)]
STRAP = [(14, 24, 50), (24, 40, 80), (40, 64, 120), (64, 96, 160)]


def bow_rail(x):
    """La regala s'enfila cap a la proa (dreta)."""
    return RAIL - int(40 * smooth(0.0, 1.0, (x - 533) / 107) ** 1.6) if x > 533 else RAIL


# ─── Cel, mar i borda ──────────────────────────────────────────────────────

def sky_sea(cv, day, phase=0.0):
    if day:
        day_sky(cv, 0, HOR, SUN, seed=14)
        day_sea(cv, HOR, RAIL + 5, sun_x=67, seed=5, phase=phase)
    else:
        night_sky(cv, 0, HOR, MOON, seed=6, clouds=0.55)
        night_sea(cv, HOR, RAIL + 5, moon_x=MOON[0], seed=5, phase=phase)


def bow(cv, day):
    """La borda de proa, que s'aixeca: planxa blanca, regala vermella i, a la punta, l'asta."""
    for x in range(534, W):
        top = bow_rail(x)
        for y in range(top + 7, RAIL + 7):
            cv.put(x, y, HULLN, 2.8 + (hr(x // 4, y // 6, 5) - 0.5) * 0.25 - (y - top) * 0.004)
        for y in range(top, top + 7):
            cv.put(x, y, REDH, 3.4 + {0: 1.4, 1: 1.0, 2: 0.4, 5: -0.4, 6: -0.9}.get(y - top, 0))
        cv.put(x, top + 7, HULLN, 1.2)
    for x in range(540, W, 35):                                          # cartel·les que pugen amb la borda
        top = bow_rail(x)
        for y in range(top + 8, RAIL + 7):
            cv.put(x, y, HULLN, 3.8)
            cv.put(x + 1, y, HULLN, 2.0)
        cv.put(x + 1, top + 11, HULLN, 4.8)
    # l'asta de proa, amb la drissa
    top = bow_rail(627)
    for y in range(53, top):
        cv.put(626, y, STEELX, 4.6)
        cv.put(627, y, STEELX, 3.4)
        cv.put(628, y, STEELX, 2.0)
    cv.rect(624, 50, 630, 53, STEELX, 4.0)
    cv.hline(624, 630, 50, STEELX, 5.2)
    for y in range(55, top, 2):                                          # la drissa
        cv.put(630, y, ROPE, 2.6)
    cv.rect(623, top - 4, 631, top, STEELX, 2.8)                         # la brida a la regala


# ─── El molinet i la cadena ────────────────────────────────────────────────

def windlass(cv):
    """El molinet, vist de cantó: bancada, caixa d'engranatges verda, el barbotí (roda dentada) amb la cadena,
    el tambor de maniobra amb el cap enrotllat i el volant del fre."""
    cv.rect(189, 203, 283, 213, STEELX, 2.2)                             # bancada
    cv.hline(189, 283, 203, STEELX, 4.0)
    cv.hline(189, 283, 213, STEELX, 0.8)
    for bx in range(193, 283, 9):
        cv.put(bx, 208, STEELX, 4.6)
        cv.put(bx + 1, 209, STEELX, 1.4)
    # la caixa d'engranatges (darrere), cantons rodons
    for y in range(157, 204):
        for x in range(200, 276):
            dx = max(211 - x, 0, x - 264)
            dy = max(168 - y, 0)
            if dx * dx + dy * dy <= 121:
                cv.put(x, y, GR, 2.8 - (y - 157) * 0.022 - (0.9 if x > 271 else 0) + (0.8 if y < 161 else 0)
                       + (0.4 if x < 204 else 0))
    for yy in range(176, 200, 5):                                         # aletes de refrigeració
        cv.hline(248, 268, yy, GR, 1.2)
        cv.hline(248, 268, yy + 1, GR, 3.6)
    for bx, by in ((206, 165), (269, 165), (206, 198), (269, 198)):       # cargols de la tapa
        cv.put(bx, by, GR, 5.2)
        cv.put(bx + 1, by + 1, GR, 1.0)
    cv.rect(252, 160, 260, 164, GR, 4.2)                                  # el tap de l'oli
    cv.hline(252, 260, 160, GR, 5.4)
    # el tambor de maniobra (a l'esquerra), amb el cap enrotllat
    for y in range(171, 201):
        u = (y - 185.5) / 15
        for x in range(187, 203):
            lvl = 2.2 - u * 1.4 - u * u
            if (x + y) % 5 in (0, 1):                                    # les voltes del cap
                cv.put(x, y, ROPE, lvl + (0.9 if (x + y) % 5 == 0 else 0))
            else:
                cv.put(x, y, ROPE, lvl - 1.6)
    cv.rect(184, 168, 187, 202, STEELX, 4.4)
    cv.vline(184, 168, 202, STEELX, 5.4)
    cv.rect(203, 168, 206, 202, STEELX, 2.6)
    # el barbotí: roda amb dents, de cara
    cx, cy, r = 235, 179, 17
    for y in range(cy - r - 3, cy + r + 4):
        for x in range(cx - r - 3, cx + r + 4):
            d = math.hypot(x - cx, y - cy)
            a = math.atan2(y - cy, x - cx)
            tooth = r + (3 if math.cos(a * 7) > 0.4 else 0)
            if d <= tooth:
                lvl = 3.2 - (y - cy) / r * 0.9 - (x - cx) / r * 0.6
                if d < 5:
                    lvl = 4.8 if d < 2.5 else 1.6
                elif abs(d - 11) < 1:
                    lvl -= 1.2
                elif d > r + 0.5:
                    lvl += 0.6                                           # la cara de la dent
                cv.put(x, y, STEELX, lvl)
    for k in range(5):                                                   # radis
        a = k * 2 * math.pi / 5 + 0.3
        for t in range(5, 11):
            cv.put(cx + round(math.cos(a) * t), cy + round(math.sin(a) * t), STEELX, 1.4)
            cv.put(cx + round(math.cos(a) * t) + 1, cy + round(math.sin(a) * t), STEELX, 4.0)
    # la cadena per damunt de la roda: baules alternes (de cara i de cantó)
    for i, a in enumerate(range(195, 350, 8)):
        x = cx + math.cos(math.radians(a)) * (r + 3)
        y = cy + math.sin(math.radians(a)) * (r + 3)
        if i % 2:
            cv.rect(x - 2, y - 1, x + 2, y + 1, CHAIN, 3.4)
            cv.put(x, y, CHAIN, 0.6)
        else:
            cv.rect(x - 2, y, x + 2, y, CHAIN, 2.4)
    # el fre: volant vermell de cara, damunt
    cv.rect(259, 147, 262, 165, STEELX, 3.0)
    cv.vline(259, 147, 165, STEELX, 4.2)
    for a in range(0, 360, 6):
        cv.put(261 + round(math.cos(math.radians(a)) * 8), 144 + round(math.sin(math.radians(a)) * 8), REDH,
               5.4 - (0.8 if 0 < a < 180 else 0))
    for a in (0, 90, 180, 270):
        for t in range(1, 8):
            cv.put(261 + round(math.cos(math.radians(a)) * t), 144 + round(math.sin(math.radians(a)) * t), REDH, 4.2)
    cv.disc(261, 144, 1.6, 1.6, STEELX, 4.6)


def chain_run(cv):
    """La cadena: del barbotí cap a l'escobén de proa (dreta), estirada per la coberta, baula a baula."""
    x, y = 253, 165
    ex, ey = 611, 213
    n = ex - x
    for i in range(0, n, 4):
        t = i / n
        cx = x + i
        cy = y + (ey - y) * min(1.0, t * 5) ** 0.6 if t < 0.2 else ey - 5 + 5 * t + math.sin(t * math.pi) * 3
        cy = round(cy)
        if (i // 4) % 2 == 0:                                            # baula de cantó: un anell amb forat
            cv.rect(cx, cy - 2, cx + 4, cy + 1, CHAIN, 3.0)
            cv.hline(cx, cx + 4, cy - 2, CHAIN, 4.6)
            cv.hline(cx + 1, cx + 3, cy, CHAIN, 0.6)
            cv.hline(cx, cx + 4, cy + 1, CHAIN, 1.6)
        else:                                                            # baula plana
            cv.hline(cx, cx + 4, cy - 1, CHAIN, 3.8)
            cv.hline(cx, cx + 4, cy, CHAIN, 2.2)
        if hr(i, 5) > 0.8:                                               # rovell
            cv.put(cx + 2, cy - 1, [(60, 30, 18), (110, 58, 30)], 1.0)
    # l'escobén: una boca de ferro a la coberta, on la cadena desapareix
    cv.disc(616, 215, 11, 4, STEELX, lambda nx, ny: 3.6 - ny * 1.2)
    cv.disc(616, 215, 7, 2.5, STEELX, 0.6)
    cv.hline(607, 625, 211, STEELX, 4.8)
    # el tub que baixa del molinet a la caixa de cadenes
    cv.disc(275, 211, 7, 3, STEELX, lambda nx, ny: 3.6 - ny)
    cv.disc(275, 211, 4, 1.5, STEELX, 0.4)


def hatch(cv):
    """L'escotilla de la caixa de cadenes, a terra en perspectiva, amb frontisses, la balda i la nansa."""
    x0, y0, x1, y1 = HATCH
    cv.poly([(x0 + 5, y0), (x1 - 5, y0), (x1, y1), (x0, y1)], STEELX, lambda x, y: 1.6)       # brocal
    cv.poly([(x0 + 9, y0 + 3), (x1 - 9, y0 + 3), (x1 - 4, y1 - 4), (x0 + 4, y1 - 4)], STEELX,
            lambda x, y: 3.0 - (y - y0) * 0.015 + (hr(x // 3, y // 2, 81) - 0.5) * 0.3)
    for y in range(y0 + 6, y1 - 5, 4):                                   # antilliscant en rombes
        for x in range(x0 + 11, x1 - 8, 8):
            off = 4 if (y // 4) % 2 else 0
            cv.put(x + off, y, STEELX, 4.2)
            cv.put(x + off + 1, y, STEELX, 3.6)
            cv.put(x + off, y + 1, STEELX, 1.8)
    cv.line(x0 + 5, y0, x1 - 5, y0, STEELX, 4.6)
    cv.line(x0, y1, x1, y1, STEELX, 0.8)
    cv.line(x0, y1 - 1, x1, y1 - 1, STEELX, 1.6)
    for hx in (x0 + 19, x1 - 27):                                        # frontisses
        cv.rect(hx, y0 - 1, hx + 8, y0 + 3, STEELX, 4.2)
        cv.hline(hx, hx + 8, y0 - 1, STEELX, 5.2)
        cv.vline(hx + 4, y0 - 1, y0 + 3, STEELX, 1.0)
    cv.rect(333, y1 - 8, 344, y1 - 3, STEELX, 4.4)                       # la balda
    cv.rect(336, y1 - 7, 341, y1 - 4, STEELX, 1.2)
    cv.rect(337, y1 - 3, 340, y1 + 1, STEELX, 3.8)
    cv.hline(312, 323, y1 - 7, STEELX, 4.6)                              # la nansa
    cv.hline(312, 323, y1 - 6, STEELX, 1.8)
    cv.rect(310, y1 - 6, 311, y1 - 4, STEELX, 3.6)
    cv.rect(324, y1 - 6, 325, y1 - 4, STEELX, 3.6)


# ─── La balsa i el pal de proa ─────────────────────────────────────────────

def balsa(cv, day):
    """La balsa salvavides: contenidor blanc de dues meitats, amb cintes, damunt un bressol inclinat."""
    x0, y0, x1, y1 = BALSA
    cy = (y0 + y1) / 2
    r = (y1 - y0) / 2
    for lx in (440, 517):                                                # el bressol: dos peus i un travesser
        for y in range(y1 - 3, FLOOR_Y + 3):
            cv.put(lx, y, STEELX, 4.2)
            cv.put(lx + 1, y, STEELX, 3.2)
            cv.put(lx + 2, y, STEELX, 2.2)
            cv.put(lx + 3, y, STEELX, 1.4)
        cv.rect(lx - 4, FLOOR_Y, lx + 7, FLOOR_Y + 3, STEELX, 2.6)
        cv.hline(lx - 4, lx + 7, FLOOR_Y, STEELX, 4.0)
        cv.put(lx - 2, FLOOR_Y + 1, STEELX, 4.8)
        cv.put(lx + 5, FLOOR_Y + 1, STEELX, 4.8)
    cv.line(441, 173, 519, 155, STEELX, 2.6)
    cv.line(441, 174, 519, 156, STEELX, 1.4)
    cv.rect(429, y1 - 3, 531, y1 + 1, STEELX, 3.0)
    cv.hline(429, 531, y1 - 3, STEELX, 4.6)
    # el cilindre
    for y in range(y0, y1 + 1):
        u = (y - cy) / (r + 0.5)
        for x in range(x0, x1 + 1):
            e = min(x - x0, x1 - x) / 8
            if e < 1 and (1 - e) ** 2 + u * u > 1:
                continue
            lvl = 4.4 - u * 1.8 - u * u * 1.4 - (0.6 if x > x1 - 5 else 0) + (0.5 if x < x0 + 4 else 0)
            lvl += (hr(x // 6, y // 4, 33) - 0.5) * 0.15
            cv.put(x, y, HULLN, lvl)
    for y in range(y0 + 1, y1):                                          # la junta del mig
        cv.put((x0 + x1) // 2, y, HULLN, 2.2)
        cv.put((x0 + x1) // 2 + 1, y, HULLN, 5.6)
    for i in range(6):                                                   # cargols de la junta
        cv.put((x0 + x1) // 2 - 1, y0 + 6 + i * 7, HULLN, 1.4)
    for bx in (445, 509):                                                # les cintes
        for y in range(y0 - 1, y1 + 2):
            u = (y - cy) / (r + 0.5)
            cv.put(bx, y, STRAP, 2.6 - u * 1.2)
            cv.put(bx + 1, y, STRAP, 2.2 - u * 1.2)
            cv.put(bx + 2, y, STRAP, 1.6 - u * 1.2)
        cv.rect(bx - 1, y1 - 1, bx + 3, y1 + 2, STEELX, 4.0)             # la tensora
    # el rètol
    cv.rect(482, 104, 504, 112, REDH, 3.6)
    cv.hline(482, 504, 104, REDH, 4.8)
    text(cv, 'BALSA', 484, 106, HULLN, 6.0)
    cv.rect(486, 116, 500, 117, HULLN, 2.4)                              # instruccions (illegibles)
    cv.rect(486, 119, 497, 120, HULLN, 2.4)
    # l'alliberador hidrostàtic i el cap de disparament
    cv.rect(475, y1 + 3, 483, y1 + 11, ORANGEB, 3.0)
    cv.hline(475, 483, y1 + 3, ORANGEB, 4.4)
    cv.put(479, y1 + 7, ORANGEB, 0.8)
    cv.line(479, y1 + 12, 469, 187, ROPE, 3.2)
    cv.line(469, 187, 461, 200, ROPE, 3.0)
    cv.line(461, 200, 463, 202, ROPE, 2.4)


_SWING = {'dx': 0}


def mast(cv, day):
    """El pal de proa: tub blanc, la creueta amb el focus, el llum de tope i la campana de llautó."""
    mx = MX
    for y in range(0, FLOOR_Y + 4):
        for x in range(mx - 4, mx + 5):
            u = (x - mx) / 4.5
            cv.put(x, y, HULLN, 4.0 - u * 1.6 - u * u)
    cv.rect(mx - 8, FLOOR_Y - 1, mx + 8, FLOOR_Y + 4, STEELX, 2.4)
    cv.hline(mx - 8, mx + 8, FLOOR_Y - 1, STEELX, 4.0)
    for y in (85, 147):                                                  # collars
        cv.rect(mx - 5, y, mx + 5, y + 3, HULLN, 2.4)
        cv.hline(mx - 5, mx + 5, y, HULLN, 4.4)
    for y in range(10, FLOOR_Y, 3):                                      # el cable del llum, enganxat al pal
        cv.put(mx - 5, y, CABX, 2.2)
    # la creueta i el focus
    cv.rect(mx - 19, 45, mx + 19, 48, HULLN, 3.4)
    cv.hline(mx - 19, mx + 19, 45, HULLN, 5.0)
    cv.hline(mx - 19, mx + 19, 48, HULLN, 1.6)
    for sx in (mx - 17, mx + 15):
        cv.line(sx + 1, 49, mx + (-4 if sx < mx else 4), 60, HULLN, 2.6)
    deck_lamp(cv, mx + 8, 59, on=not day)
    # el llum de tope
    cv.rect(mx - 3, 5, mx + 3, 12, CABX, 3.0)
    cv.hline(mx - 3, mx + 3, 5, CABX, 4.4)
    if not day:
        cv.glow(mx, 9, 13, (255, 250, 230), 0.7)
        cv.rect(mx - 1, 8, mx + 1, 10, [(255, 252, 240)], 0, lit=0)
    else:
        cv.rect(mx - 2, 8, mx + 2, 10, [(200, 200, 196), (236, 236, 230)], 1.0, lit=0)
    # la campana
    cv.rect(mx + 5, 103, mx + 16, 105, STEELX, 3.0)
    cv.hline(mx + 5, mx + 16, 103, STEELX, 4.4)
    cv.rect(mx + 9, 106, mx + 13, 107, GOLD, 2.6)
    for y in range(107, 123):
        w = 3 + (y - 107) * 6 // 15
        for x in range(mx + 11 - w, mx + 12 + w):
            u = (x - (mx + 11)) / (w + 0.5)
            cv.put(x, y, GOLD, 3.6 - u * 1.6 - u * u + (0.8 if y == 112 or y == 113 else 0))
    cv.hline(mx + 1, mx + 21, 123, GOLD, 2.6)
    cv.hline(mx + 2, mx + 20, 124, GOLD, 1.2)
    cv.put(mx + 7, 110, [(255, 246, 200)], 0, lit=0)                    # la lluentor
    sw = _SWING['dx']                                                    # el cap del batall, que es gronxa
    for y in range(125, 134):
        cv.put(mx + 11 + round(sw * (y - 125) / 9), y, ROPE, 3.0)
    for dy in (0, 1):
        cv.put(mx + 11 + sw, 134 + dy, ROPE, 2.0)
        cv.put(mx + 12 + sw, 134 + dy, ROPE, 1.4)


# ─── La caseta i el pas lateral (a l'esquerra) ─────────────────────────────

def house(cv, day):
    x0, x1 = HOUSE
    for y in range(29, FLOOR_Y):
        for x in range(x0, x1 + 1):
            lvl = 3.0 + (hr(x // 3, y // 5, 71) - 0.5) * 0.25 - (0.7 if y > FLOOR_Y - 13 else 0)
            if x >= x1 - 2:
                lvl -= 1.2
            cv.put(x, y, HULLN, lvl)
    for sy in (64, 149):                                                 # juntes de planxa amb reblons
        cv.hline(x0, x1 - 3, sy, HULLN, 1.8)
        cv.hline(x0, x1 - 3, sy + 1, HULLN, 4.2)
        for bx in range(x0 + 5, x1 - 3, 11):
            cv.put(bx, sy + 3, HULLN, 4.8)
            cv.put(bx + 1, sy + 4, HULLN, 1.8)
    cv.hline(x0, x1, FLOOR_Y - 13, HULLN, 1.4)
    cv.vline(x0, 29, FLOOR_Y - 1, HULLN, 4.6)                             # aresta de la cantonada
    cv.vline(x0 - 1, 29, FLOOR_Y - 1, HULLN, 1.4)
    for i in range(11):                                                  # ratlles de rovell
        rx = x0 + 5 + int(hr(i, 72) * (x1 - x0 - 10))
        if DOOR[0] - 6 <= rx <= DOOR[2] + 6:
            continue
        for y in range(67, 67 + 5 + int(hr(i, 73) * 20)):
            cv.flat(rx, y, mix(cv.get(rx, y), (120, 70, 40), 0.3 * (1 - (y - 67) / 30)))
    wt_door(cv, *DOOR)
    cv.rect(69, 81, 109, 90, HULLN, 1.6)                                 # rètol
    cv.hline(69, 109, 81, HULLN, 2.8)
    text(cv, 'PASSADÍS', 73, 84, HULLN, 5.6)
    deck_lamp(cv, 89, 75, on=not day)
    cv.disc(133, 53, 8, 8, CABX, lambda nx, ny: 3.8 - nx - ny)           # ull de bou
    for a in range(0, 360, 60):
        cv.put(133 + round(math.cos(math.radians(a)) * 7), 53 + round(math.sin(math.radians(a)) * 7), CABX, 5.0)
    if day:
        cv.disc(133, 53, 5.5, 5.5, STEELX, lambda nx, ny: 3.4 - ny + (1.6 if nx < -0.2 and ny < -0.2 else 0))
    else:
        cv.disc(133, 53, 5.5, 5.5, WINDOW, lambda nx, ny: 2.2 - ny * 0.6, lit=0)
        cv.glow(133, 53, 16, GLOW_WARM, 0.2)
    # l'extintor, a la seva brida
    for y in range(147, 179):
        for x in range(128, 139):
            u = (x - 133) / 5.5
            cv.put(x, y, REDH, 4.0 - u * 1.4 - u * u)
    cv.disc(133, 147, 5, 2, REDH, 4.6)
    cv.rect(130, 141, 136, 145, STEELX, 3.6)
    cv.hline(130, 136, 141, STEELX, 4.8)
    cv.rect(128, 158, 138, 165, HULLN, 5.0)                              # l'etiqueta
    for yy in (160, 162):
        cv.hline(130, 136, yy, HULLN, 2.6)
    cv.line(137, 144, 141, 155, STEELX, 2.0)                             # la mànega
    cv.line(141, 155, 139, 170, STEELX, 1.8)
    cv.rect(126, 166, 140, 168, CABX, 2.8)                               # la brida


def boat_deck(cv, day):
    x1 = HOUSE[1] + 8
    cv.rect(0, 19, x1, 29, HULLN, lambda x, y: 3.6 - (y - 19) * 0.2)
    cv.hline(0, x1, 19, HULLN, 5.0)
    cv.hline(0, x1, 29, HULLN, 1.0)
    cv.rect(0, 24, x1, 25, REDP, 2.6)
    for x in range(4, x1, 12):
        cv.put(x, 21, HULLN, 5.4)
    for sx in range(5, x1, 19):                                          # barana
        cv.vline(sx, 0, 18, HULLN, 4.4)
        cv.vline(sx + 1, 0, 18, HULLN, 2.6)
    for ry in (3, 11):
        cv.hline(0, x1, ry, HULLN, 4.6)
        cv.hline(0, x1, ry + 1, HULLN, 2.4)


def side_passage(cv, day):
    x1 = HOUSE[0] - 3
    for y in range(31, 40):
        for x in range(0, x1 + 1):
            cv.put(x, y, HULLN, 1.4 - (y - 31) * 0.05)
    for y in range(29, FLOOR_Y + 3):                                     # el puntal de la coberta de botes
        for x, l in ((5, 1.4), (6, 2.4), (7, 3.4), (8, 4.2)):
            cv.put(x, y, HULLN, l)
    deck_lamp(cv, 22, 40, on=not day)
    cv.darken(0, 31, x1, FLOOR_Y + 40, lambda x, y: 0.8 if y < FLOOR_Y else 0.6 - (y - FLOOR_Y) / 67, dither=False)


def draw(cv, day, phase=0.0):
    sky_sea(cv, day, phase)
    bulwark(cv, 0, W - 1, RAIL, FLOOR_Y, base=2.6, scuppers=(173, 333))
    bow(cv, day)
    deck_floor(cv, FLOOR_Y, H - 1)
    hatch(cv)
    chain_run(cv)
    windlass(cv)
    bitts(cv, 368, FLOOR_Y + 3)
    balsa(cv, day)
    mast(cv, day)
    coil(cv, 171, 224, 16, 5)
    house(cv, day)
    boat_deck(cv, day)
    side_passage(cv, day)
    if not day:
        cv.glow(89, 229, 59, GLOW_WARM, 0.10)
        cv.glow(565, 224, 67, GLOW_WARM, 0.09)
    else:
        cv.darken(HOUSE[1], FLOOR_Y, HOUSE[1] + 35, FLOOR_Y + 11,
                  lambda x, y: 0.5 if x < HOUSE[1] + 35 - (y - FLOOR_Y) * 4 else 0)


def manta(cv):
    """El racó de la Juana sota la balsa (de dia): una caixa de peix de fusta per seure, amb la manta de quadres
    doblegada al damunt i penjant pel davant, i un salvavides de coixí a terra."""
    BL = [(30, 14, 18), (60, 24, 30), (100, 38, 44), (140, 56, 56), (176, 84, 72), (206, 120, 96)]
    WD = [(30, 20, 14), (54, 36, 22), (82, 56, 32), (110, 78, 44), (140, 102, 60), (170, 130, 82)]
    x0, x1, yt, yb = 477, 517, 180, 224
    cv.darken(x0 - 5, yb - 3, x1 + 8, yb + 4, 0.6)
    for py in range(yt + 4, yb + 1, 9):                                  # la caixa: posts amb escletxes
        cv.rect(x0, py, x1, min(py + 7, yb), WD, lambda x, y: 2.4 - (y - py) * 0.12 - (x - x0) * 0.015)
        cv.hline(x0, x1, py, WD, 3.6)
        if py + 8 <= yb:
            cv.hline(x0 + 1, x1 - 1, py + 8, WD, 0.6)
        for nx in (x0 + 4, x1 - 4):                                      # claus
            cv.put(nx, py + 3, STEELX, 4.0)
    for x in (x0, x1 - 3):
        cv.rect(x, yt + 4, x + 3, yb, WD, 2.2)

    def bottom(x):
        return yt + 17 + round(math.sin(x * 0.38) * 2 + (3 if x0 + 11 < x < x1 - 8 else 0))
    for x in range(x0 - 3, x1 + 4):
        for y in range(yt - 3, bottom(x) + 1):
            top = y < yt + 3
            chk = (x // 5 + y // 4) % 2
            line = x % 5 == 0 or y % 4 == 0
            cv.put(x, y, BL, (3.4 if top else 2.6) + (0.9 if chk else 0) + (0.5 if line and chk else 0) - (x - x0) * 0.015)
        if x % 2 == 0:                                                   # el serrell
            cv.put(x, bottom(x) + 1, BL, 3.6)
            cv.put(x, bottom(x) + 2, BL, 2.6)
    for x in range(x0 + 3, x1, 9):                                       # plecs
        cv.line(x, yt + 4, x + 1, bottom(x + 1) - 1, BL, 1.0)
    cv.hline(x0 - 3, x1 + 3, yt - 3, BL, 4.6)
    # un salvavides de coixí, a terra al costat
    cv.rect(525, 212, 547, 221, ORANGEB, lambda x, y: 2.4 - (y - 212) * 0.1 - (x - 525) * 0.02)
    cv.hline(525, 547, 212, ORANGEB, 3.8)
    cv.hline(525, 547, 222, ORANGEB, 0.6)
    for x in (531, 541):
        cv.vline(x, 212, 221, [(120, 120, 116), (170, 170, 164), (210, 210, 200)], 1.2)


def bg(cv):
    draw(cv, False)


def dia(cv):
    keep = cv.light
    cv.light = LIGHT_DAY
    draw(cv, True)
    manta(cv)
    cv.light = keep


def cadenat(cv):
    """Un cadenat nou, de llautó lluent, a la balda de l'escotilla."""
    x, y = 339, HATCH[3] - 8
    for a in range(180, 361, 10):                                        # l'arc
        px = x + round(math.cos(math.radians(a)) * 4)
        py = y - 1 + round(math.sin(math.radians(a)) * 4)
        cv.put(px, py, STEELX, 5.4)
        cv.put(px, py + 1, STEELX, 3.0)
    cv.rect(x - 5, y, x + 5, y + 9, GOLD, lambda px, py: 4.2 - (px - x) * 0.16 - (py - y) * 0.08)
    cv.hline(x - 5, x + 5, y, GOLD, 5.6)
    cv.hline(x - 5, x + 5, y + 9, GOLD, 2.0)
    cv.rect(x, y + 4, x, y + 6, GOLD, 0.6)
    cv.put(x - 1, y + 4, GOLD, 0.6)
    cv.put(x - 4, y + 1, [(255, 250, 220)], 0, lit=0)
    cv.put(x - 3, y + 1, [(255, 250, 220)], 0, lit=0)


PROPS = {'dia': dia, 'cadenat': cadenat}


# ─── Animacions ────────────────────────────────────────────────────────────
# Com a 480: el mar es mou amb `phase` (els darrers SEA_FADE fotogrames es fonen amb el principi) i el cap de la
# campana es gronxa; aquí, fins a dos píxels.
SEA_N, SEA_FADE, SEA_STEP = 12, 4, 0.32
SWING = (0, 1, 1, 2, 1, 1, 0, -1, -1, -2, -1, -1)
ROPE_BOX = (577, 120, 590, 137)                                          # el mar del darrere del cap no es toca


def _scene(day, dx):
    _SWING['dx'] = dx
    try:
        cv = Canvas(light=LIGHT)
        dia(cv) if day else bg(cv)
    finally:
        _SWING['dx'] = 0
    return cv.img


def _frames(day):
    if day:
        def sea(cv, ph):
            day_sea(cv, HOR, RAIL + 5, sun_x=67, seed=5, phase=ph)
    else:
        def sea(cv, ph):
            night_sea(cv, HOR, RAIL + 5, moon_x=MOON[0], seed=5, phase=ph)
    scenes = {dx: _scene(day, dx) for dx in set(SWING)}
    base = scenes[0]
    ref = Canvas(light=LIGHT)
    sea(ref, 0.0)
    rp, bp = ref.img.load(), base.load()
    bx0, by0, bx1, by1 = ROPE_BOX
    open_ = [(x, y) for y in range(HOR + 1, RAIL + 6) for x in range(W)
             if bp[x, y] == rp[x, y] and not (bx0 <= x <= bx1 and by0 <= y <= by1)]
    frames = []
    for i in range(SEA_N):
        a, b = Canvas(light=LIGHT), Canvas(light=LIGHT)
        sea(a, i * SEA_STEP)
        sea(b, (i - SEA_N) * SEA_STEP)
        w = max(0, i - (SEA_N - SEA_FADE)) / SEA_FADE
        out = scenes[SWING[i]].copy()
        o, ap, bpp = out.load(), a.img.load(), b.img.load()
        for x, y in open_:
            o[x, y] = bpp[x, y] if hr(x, y, 90) < w else ap[x, y]
        if day:                                                          # dues gavines que planen en cercle, lluny
            t = i / SEA_N * 2 * math.pi
            cv = Canvas(light=LIGHT, img=out)
            gull(cv, round(349 + math.cos(t) * 19), round(59 + math.sin(t) * 5), (1, 2, 1, 0)[i % 4])
            gull(cv, round(389 - math.cos(t + 1.3) * 13), round(45 + math.sin(t + 1.3) * 4), (0, 1, 2, 1)[i % 4],
                 (214, 216, 212))
        frames.append(_diff(out, base))
    return frames


ANIMS = {'mar': {'frames': lambda: _frames(False), 'frameDuration': 260},
         'dia_mar': {'frames': lambda: _frames(True), 'frameDuration': 260}}


def _s(*v):
    return tuple(round(c * K) for c in v)


GEOMETRIA = {
    'things': {
        'popa': {'rect': _s(0, 24, 28, 168), 'walk': _s(12, 174)},
        'porta': {'rect': _s(44, 66, 90, 152), 'walk': _s(67, 168)},
        'balsa': {'rect': _s(312, 66, 406, 112), 'walk': _s(334, 172)},
        'molinet': {'rect': _s(144, 108, 210, 160), 'walk': _s(178, 174)},
        'escotilla': {'rect': _s(220, 160, 284, 188), 'walk': _s(252, 192)},
    },
    'spawns': {cid: _s(*p) for cid, p in {'iri': (296, 190), 'vet': (204, 192), 'juana': (372, 168)}.items()},
    'walkable': [_s(*p) for p in [(0, 166), (140, 162), (216, 162), (440, 160), (479, 166), (479, 196), (0, 196)]],
}
