"""
**El dibuix pla de sempre** (font de les textures de la sala en 3D, fabrica_magatzem.py).

Magatzem d'eines (Iri) a 640×360: la composició de hd/rooms/fabrica_magatzem.py ×4/3, dibuixada de nou.
El regne del Cargol. Maó amb arrimador pintat, prestatgeria plena de material inventariat (de ferro-9), banc de
treball amb el tauler d'eines, la taquilla de la Mira.
Llums: el llum penjant del banc, la bombeta damunt la prestatgeria i el vidre glaçat del despatx.
Decorats: `plomall`, `caixa_eines`. Animació: `ambient` (la pols a la llum de les bombetes i una arna).
"""
import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)

import math
import random
from functools import lru_cache

from hd.pix import (Canvas, Light, W, H, hr, WALNUT, FLOOR, GOLD, COPPER, RUST, IRON, RED, GREEN, PAPER,
                    MANILA, GLASS, LAMPG)
from hd.rooms.fabrica_magatzem import F9, WOOD2, DADO
from hd640.rooms.fabrica_calderes_pla_comu import (STONE, ENAMEL, CORK, FLOOR_Y, text, text_w, brick_wall, contact_shadow,  # noqa: F401
                                          plank_door, pipe_h, bracket, ceiling, wall_plinth, outline)
from hd640.rooms.fabrica_despatx_pla_comu import dust, ambient_frames

LIGHT = Light(vignette=(93, 53), floor_fade=(264, 53))
LIGHT.point(517, 112, r=200, k=2.8, squash=1.1, down=True, power=1.8)    # llum penjant del banc
LIGHT.point(316, 27, r=200, k=2.5, squash=0.9, power=1.8)                # bombeta de la prestatgeria
LIGHT.point(116, 131, r=73, k=0.9, power=2.0)                            # vidre glaçat del despatx

LAMP_X = 517                       # el llum penjant del banc
BULB_X = 316                       # la bombeta de la prestatgeria



class _Ample:
    """Un canvas que dibuixa els píxels 1,5 vegades d'ample (a partir de x0): lletra eixamplada per als rètols de
    les parets que fugen, que l'escorç aprima."""
    def __init__(self, cv, x0, k=1.5):
        self.cv, self.x0, self.k = cv, x0, k

    def put(self, x, y, *a):
        i = x - self.x0
        for xx in range(self.x0 + int(i * self.k), self.x0 + int((i + 1) * self.k)):
            self.cv.put(xx, y, *a)

def plank_floor(cv, y0):
    """Terra de taulons gastats, en perspectiva, amb la veta, els claus i les taques d'oli."""
    VPX, VPY = 320, -200
    for y in range(y0, H):
        dep = y - VPY
        pw = dep / 40
        for x in range(W):
            u = (x - VPX) / dep * 40 / 1.2
            pl = math.floor(u)
            fr = (u - pl) * pw * 1.2
            r = hr(pl, 7)
            seg = math.floor(4800 / dep / 1.6 + r * 5)
            seg_up = math.floor(4800 / (dep - 1) / 1.6 + r * 5)
            lvl = 2.0 + (hr(pl, seg) - 0.5) * 0.8 + (0.3 if 1 <= fr < 2 else 0)
            lvl += 0.15 * math.sin(x * 0.11 + hr(pl, seg, 3) * 9 + y * 0.02) * (fr > 2)   # veta
            if hr(x // 5, y // 3, pl) > 0.93:
                lvl -= 0.5                                         # taques d'oli
            if fr < 1:
                lvl = 0.6
            elif seg != seg_up:
                lvl = 0.8
            elif seg != math.floor(4800 / (dep - 3) / 1.6 + r * 5) and 2 < fr < 3.2:
                lvl = 3.4                                          # el cap del clau, a tocar de la junta
            if y < y0 + 8:
                lvl -= (y0 + 8 - y) / 8 * 1.2
            cv.put(x, y, FLOOR, lvl)


def lamp_cone(x, y):
    """El con de llum sota el llum penjant del banc (0..1)."""
    if not 107 <= y <= 149:
        return 0.0
    half = 12 + (y - 107) * 0.9
    return max(0.0, min(1.0, (1 - abs(x - LAMP_X) / half) * 2.2)) * (1 - (y - 107) / 53)


def bulb_halo(x, y):
    """La claror al voltant de la bombeta de la prestatgeria (0..1)."""
    return max(0.0, 1 - math.hypot(x - BULB_X, (y - 24) * 1.2) / 51) ** 0.8


def moth(cv, tt):
    """Una arna que volta el llum del banc: cos de dos píxels i les ales que baten."""
    ph = 2 * math.pi * tt
    x = LAMP_X + 20 * math.sin(ph) + 5 * math.sin(ph * 3 + 1.1)
    y = 99 + 7 * math.sin(ph * 2 + 0.5) + 3 * math.cos(ph * 5)
    x, y = round(x), round(y)
    up = math.sin(ph * 11) > 0                                     # aleteja
    body = (58, 46, 40)
    lit_side = math.cos(ph) < 0                                    # de cara al llum, més clara
    wing = (196, 176, 140) if lit_side else (120, 100, 80)
    wing2 = (150, 132, 104) if lit_side else (92, 76, 62)
    cv.flat(x, y, body)
    cv.flat(x, y + 1, body)
    if up:
        cv.flat(x - 1, y - 1, wing); cv.flat(x + 1, y - 1, wing)
        cv.flat(x - 2, y - 2, wing2); cv.flat(x + 2, y - 2, wing2)
    else:
        cv.flat(x - 1, y, wing); cv.flat(x + 1, y, wing)
        cv.flat(x - 2, y + 1, wing2); cv.flat(x + 2, y + 1, wing2)


PARTS = ('paret', 'portes', 'prestatgeria', 'tauler', 'banc', 'llum', 'taquilla', 'tint')


def room(cv, parts=PARTS):
    """La sala quieta (sense la capa animada). `parts`: els trossos que es dibuixen (la sala en 3D en treu les
    textures per separat)."""
    BX0, BX1 = 445, 587                                    # el banc de treball
    # ─── Sostre, paret de maó i arrimador pintat ──────────────────────────────
    if 'paret' in parts:
        ceiling(cv)
        brick_wall(cv, 0, 19, W - 1, 202, seed=21, base=1.5,
                   extra=lambda x, y: -(53 - y) / 53 * 0.6 if y < 53 else 0)
        # arrimador pintat de verd, amb la pintura saltada
        for y in range(139, 203):
            for x in range(W):
                chip = hr(x // 7, y // 5, 5) > 0.95 or (y < 144 and hr(x // 3, 1) > 0.7)
                if chip:
                    continue                                           # s'hi veu el maó
                lvl = 2.2 + (hr(x // 19, (y - 139) // 8) - 0.5) * 0.2 + (hr(x // 2, y // 3, 6) - 0.5) * 0.1
                if (y - 139) % 8 == 7:
                    lvl -= 0.5                                         # el relleu de les llagues sota la pintura
                elif (y - 139) % 8 == 0:
                    lvl += 0.15
                if hr(x // 7, y // 5, 5) > 0.92:
                    lvl -= 0.6                                         # la vora de la pintura que s'aixeca
                cv.put(x, y, DADO, lvl)
        cv.hline(0, W - 1, 137, DADO, 3.4)
        cv.hline(0, W - 1, 138, DADO, 1.0)
        wall_plinth(cv, 203, 210)
        plank_floor(cv, FLOOR_Y)
        pipe_h(cv, 0, W - 1, 21, 5, IRON, 2.4, flange_every=96)
        for x in range(40, W, 96):
            bracket(cv, x, 26)

    if 'portes' in parts:
        # ─── Porta de la sala de calderes (11..77 × 87..207) ──────────────────────
        cv.rect(7, 79, 81, 86, STONE, lambda x, y: [3.6, 3.2, 3.0, 2.6, 2.4, 2.2, 2.0, 0.8][y - 79] + (hr(x // 4, 79) - 0.5) * 0.3)
        for x in range(7, 82, 15):                                          # els junts de la llinda
            cv.vline(x, 80, 85, STONE, 1.2)
        plank_door(cv, 11, 87, 77, 207, base=2.2)
        s = 'CALDERES'
        cv.rect(21, 99, 67, 109, ENAMEL, lambda x, y: 3.8 if 21 < x < 67 and 99 < y < 109 else 1.6, 0.6)
        text(cv, 44 - text_w(s) // 2, 101, s, IRON, 1.0, 0)

        # ─── Porta del despatx del director (87..145 × 81..207) ───────────────────
        PX0, PY0, PX1 = 88, 83, 144
        cv.rect(PX0 - 1, PY0 - 2, PX1 + 1, 207, WALNUT, lambda x, y: 3.4 if y < PY0 + 1 else (3.0 if x < PX0 + 2 else (1.2 if x > PX1 - 2 else 2.4)))
        cv.hline(PX0 - 3, PX1 + 3, PY0 - 3, WALNUT, 4.0)                   # la cornisa del marc
        cv.hline(PX0 - 3, PX1 + 3, PY0 - 4, WALNUT, 2.8)
        cv.rect(PX0 + 4, PY0 + 4, PX1 - 4, 207, WALNUT, 0.6)
        LX0, LX1, LY0 = PX0 + 5, PX1 - 5, PY0 + 5
        GX0, GX1, GY0, GY1 = LX0 + 7, LX1 - 7, LY0 + 7, LY0 + 51         # el vidre glaçat
        PY = LY0 + 61                                                      # el plafó de sota

        def door(x, y):
            g = (hr(x // 4, 78) - 0.5) * 0.3 + 0.12 * math.sin(y * 0.3 + hr(x // 4, 79) * 6)
            if GX0 <= x <= GX1 and GY0 <= y <= GY1:
                return None
            if GX0 <= x <= GX1 and PY <= y <= 195:
                if x == GX0 or y == PY:
                    return 1.0
                if x == GX1 or y == 195:
                    return 3.4
                if x in (GX0 + 1, GX0 + 2) or y in (PY + 1, PY + 2):
                    return 3.2
                if x == GX1 - 1 or y == 194:
                    return 1.8
                return 2.5 + g
            return 2.1 + g + (0.6 if x == LX0 else 0) - (0.8 if x == LX1 else 0)

        for y in range(LY0, 208):
            for x in range(LX0, LX1 + 1):
                v = door(x, y)
                if v is None:
                    gv = 2.6 + (y - GY0) / 45 * 0.9 + (hr(x // 2, y // 2) - 0.5) * 0.5 + (hr(x, y, 3) - 0.5) * 0.2 - abs(x - 116) / 35
                    cv.put(x, y, GLASS, gv, 0.5)
                else:
                    cv.put(x, y, WALNUT, v)
        cv.hline(GX0 - 1, GX1 + 1, GY0 - 1, WALNUT, 1.0)                    # junquillo del vidre
        cv.vline(GX0 - 1, GY0 - 1, GY1 + 1, WALNUT, 1.2)
        cv.hline(GX0 - 1, GX1 + 1, GY1 + 1, WALNUT, 3.4)
        cv.vline(GX1 + 1, GY0 - 1, GY1 + 1, WALNUT, 3.0)
        # «DIRECCIÓ» en lletres daurades al vidre (de pal sec, amb l'ombra a sota)
        for x in range(103, 131):
            if (x - 103) % 4 != 3:
                cv.put(x, 105, GOLD, 4.2, 0.2)
                cv.put(x, 106, GOLD, 3.4 if hr(x, 5) > 0.3 else 2.6, 0.2)
                if hr(x, 6) > 0.6:
                    cv.put(x, 107, GOLD, 2.4, 0.2)
        for x in range(108, 126, 3):
            cv.put(x, 112, GOLD, 3.0, 0.2)
            cv.put(x + 1, 112, GOLD, 2.4, 0.2)
        cv.glow(116, 123, 32, (240, 200, 120), 0.2)
        # pom de llautó amb l'escut
        cv.rect(LX1 - 8, 149, LX1 - 4, 163, GOLD, lambda x, y: 2.8 - (x - LX1 + 8) * 0.3 + (0.6 if y == 149 else 0))
        cv.disc(LX1 - 6, 153, 2.7, 2.7, GOLD, lambda nx, ny: 4.5 - nx - ny)
        cv.put(LX1 - 7, 152, GOLD, 5.4)
        cv.vline(LX1 - 6, 158, 160, GOLD, 0.2)

        # Rètol de les normes del Cargol, damunt les portes
        # (la lletra, fosca i a 1,5 d'ample: a la paret de l'esquerra, en escorç, la vermella no es llegia)
        cv.rect(11, 37, 147, 67, ENAMEL, lambda x, y: (1.4 if x in (11, 147) or y in (37, 67) else 3.9) - (y - 37) * 0.015, 0.5)
        cv.rect(13, 39, 145, 65, ENAMEL, lambda x, y: 4.0 + (hr(x // 3, y // 3, 7) - 0.5) * 0.15 if not (x in (13, 145) or y in (39, 65)) else 2.6, 0.5)
        for s, y in (('SENSE FORMULARI', 44), ('NO HI HA MATERIAL', 55)):
            w = text_w(s) * 3 // 2
            text(_Ample(cv, 79 - w // 2), 79 - w // 2, y, s, RED, 0.9, 0.2)
        for cx, cy in ((16, 42), (142, 42), (16, 62), (142, 62)):
            cv.put(cx, cy, IRON, 1.0, 0.3)
            cv.put(cx + 1, cy + 1, ENAMEL, 2.0, 0.3)
        for x, y in ((40, 66), (41, 66), (112, 38), (135, 66)):           # l'esmalt saltat
            cv.put(x, y, IRON, 0.8, 0.3)

        # ─── Ganxo del plomall (el plomall és un prop) ───────────────────────────
        cv.rect(159, 80, 169, 83, IRON, lambda x, y: 3.2 - (y - 80) * 0.6)
        cv.put(161, 81, IRON, 4.4); cv.put(167, 81, IRON, 4.4)
        for i, (x, y) in enumerate(((164, 84), (164, 85), (164, 86), (164, 87), (165, 88), (166, 88), (167, 87), (167, 86))):
            cv.put(x, y, IRON, 3.4 if i < 4 else 2.4)

    if 'prestatgeria' in parts:
        # ─── Prestatgeria (203..429 × 29..200) ───────────────────────────────────
        SX0, SX1, ST, SB = 203, 429, 29, 200
        SHELVES = [63, 97, 132, 167]
        # fons fosc i ombra a la paret
        for y in range(ST, SB + 1):
            for x in range(SX0, SX1 + 1):
                cv.put(x, y, WOOD2, 0.7 + (hr(x // 8, 4) - 0.5) * 0.3 + (0.2 if x % 8 == 0 else 0))
        contact_shadow(cv, SX0, SX1, 201, 9, 1.0)
        rnd = random.Random(7)
        tops = [ST + 5] + [sy + 5 for sy in SHELVES]
        bottoms = SHELVES + [SB - 5]

        def crate(x, yb, w, h, lab=True, ramp=WOOD2, base=3.0):
            cv.rect(x, yb - h, x + w - 1, yb - 1, ramp, lambda xx, yy: base + (hr(xx // 2, yy // 5, x) - 0.5) * 0.4
                    - (0.8 if (yy - (yb - h)) % 7 == 6 else 0) - (1.2 if xx == x + w - 1 else 0) + (0.6 if xx == x else 0)
                    + 0.12 * math.sin(xx * 0.7 + yy * 0.05 + x))
            cv.hline(x, x + w - 1, yb - h, ramp, base + 1.2)
            for cx in (x + 1, x + w - 3):                              # els claus de les taules
                for yy in range(yb - h + 3, yb - 1, 7):
                    cv.put(cx, yy, IRON, 3.0)
            if lab and w > 11:
                lx = x + w // 2 - 4
                cv.rect(lx, yb - h + 4, lx + 8, yb - h + 8, PAPER, lambda xx, yy: 4.2 - (0.6 if yy == yb - h + 8 else 0))
                cv.hline(lx + 1, lx + 6, yb - h + 5, PAPER, 2.0)
                cv.hline(lx + 1, lx + 4, yb - h + 7, PAPER, 2.4)

        def jar(x, yb):
            # pot de vidre amb cargols de ferro-9
            cv.rect(x, yb - 15, x + 8, yb - 1, GLASS, lambda xx, yy: 1.2 + (1.6 if xx == x + 1 else 0) + (0.8 if xx == x + 2 else 0), 0.6)
            for yy in range(yb - 10, yb - 1):
                for xx in range(x + 1, x + 8):
                    if hr(xx, yy, 1) > 0.35:
                        cv.put(xx, yy, F9, 3.0 + hr(xx, yy, 2) * 1.6)
            cv.rect(x + 1, yb - 17, x + 7, yb - 15, RED, lambda xx, yy: 2.8 + (0.6 if yy == yb - 17 else 0))
            cv.vline(x + 1, yb - 13, yb - 11, PAPER, 4.4)                # reflex del vidre
            return 9

        def coil(x, yb):
            cv.disc(x + 7, yb - 7, 7, 7, COPPER, lambda nx, ny: 3.4 - nx - ny + (0.8 if int((nx + 1) * 8) % 2 else 0))
            cv.disc(x + 7, yb - 7, 2.5, 2.5, WOOD2, 0.6)
            return 15

        def magnet(x, yb):
            # imant de ferradura, vermell amb les puntes de ferro-9
            for yy in range(yb - 13, yb):
                for xx in range(x, x + 11):
                    nx, ny = (xx - x - 5) / 5.5, (yy - yb + 8) / 5.5
                    if ny < 0:
                        if 0.45 < math.hypot(nx, ny) < 1.0:
                            cv.put(xx, yy, RED, 3.4 - nx - ny)
                    elif 0.45 < abs(nx) < 1.0:
                        if yy >= yb - 4:
                            cv.put(xx, yy, F9, 4.6 - nx)
                        else:
                            cv.put(xx, yy, RED, 3.0 - nx)
            return 13

        def wrenches(x, yb):
            for i in range(3):
                xx = x + i * 4
                h = 19 + i * 3
                cv.vline(xx + 1, yb - h + 4, yb - 1, F9, 3.6)
                cv.vline(xx + 2, yb - h + 4, yb - 1, F9, 2.2)
                cv.rect(xx, yb - h, xx + 3, yb - h + 3, F9, lambda a, b: 4.0 - (b - yb + h) * 0.3)
                cv.put(xx + 1, yb - h, WOOD2, 0.4)
                cv.put(xx + 2, yb - h, WOOD2, 0.4)
            return 15

        def bin_(x, yb, w=19):
            # calaix-safata de xapa amb cargols i etiqueta
            cv.rect(x, yb - 9, x + w - 1, yb - 1, IRON, lambda xx, yy: 2.6 - (yy - yb + 9) * 0.1 + (0.8 if yy == yb - 9 else 0)
                    - (0.9 if xx == x + w - 1 else 0))
            for xx in range(x + 1, x + w - 1):
                if hr(xx, yb, 3) > 0.3:
                    cv.put(xx, yb - 10, F9, 3.4 + hr(xx, 1) * 1.6)
                if hr(xx, yb, 4) > 0.6:
                    cv.put(xx, yb - 11, F9, 3.0 + hr(xx, 2) * 1.6)
            cv.rect(x + 4, yb - 7, x + w - 5, yb - 4, PAPER, lambda xx, yy: 4.0 - (0.6 if yy == yb - 4 else 0))
            cv.hline(x + 5, x + w - 7, yb - 6, PAPER, 2.2)
            return w + 1

        for top, bot in zip(tops, bottoms):
            x = SX0 + 5
            while x < SX1 - 19:
                if abs(x - BULB_X) < 4:
                    x = BULB_X + 5
                    continue
                k = rnd.choice(['crate', 'crate', 'jar', 'coil', 'magnet', 'wrench', 'bin', 'bin', 'jar'])
                if k == 'crate':
                    w = rnd.randint(16, 24)
                    if x + w > SX1 - 4 or (x < BULB_X + 2 < x + w + 2):
                        x += 4
                        continue
                    crate(x, bot, w, rnd.randint(12, min(24, bot - top - 3)))
                elif k == 'jar':
                    w = jar(x, bot)
                elif k == 'coil':
                    w = coil(x, bot)
                elif k == 'magnet':
                    w = magnet(x, bot)
                elif k == 'wrench':
                    w = wrenches(x, bot)
                else:
                    w = bin_(x, bot)
                x += w + rnd.randint(1, 4)
        # muntants i lleixes
        for ux in (SX0, BULB_X - 1, SX1 - 4):
            cv.rect(ux, ST, ux + 4, SB, WOOD2, lambda xx, yy: ([3.6, 3.2, 2.8, 2.2, 1.2] if ux != SX1 - 4 else [3.0, 2.6, 2.0, 1.4, 0.6])[xx - ux]
                    + (hr(xx, yy // 6, ux) - 0.5) * 0.15)
        for sy in [ST] + SHELVES:
            cv.rect(SX0, sy, SX1, sy + 4, WOOD2, lambda xx, yy: [4.2, 3.6, 3.0, 2.6, 1.2][yy - sy] + (hr(xx // 4, sy) - 0.5) * 0.15)
            # etiquetes d'inventari al cantell de cada lleixa
            for lx in range(SX0 + 16, SX1 - 11, 37):
                cv.rect(lx, sy + 1, lx + 9, sy + 4, PAPER, lambda xx, yy: 4.0 - (0.5 if yy == sy + 4 else 0))
                cv.hline(lx + 1, lx + 6, sy + 2, PAPER, 2.4)
                cv.hline(lx + 1, lx + 4, sy + 3, PAPER, 2.8)
        cv.rect(SX0, SB - 4, SX1, SB, WOOD2, lambda xx, yy: [3.4, 3.0, 2.6, 2.0, 0.8][yy - SB + 4])
        for ux in (SX0, SX1 - 4):
            cv.rect(ux, SB + 1, ux + 4, SB + 5, WOOD2, 1.6)
        for ux in (SX0, BULB_X - 1, SX1 - 4):                          # cargols de les lleixes
            for sy in SHELVES:
                cv.put(ux + 2, sy + 2, IRON, 4.0)

        # Bombeta penjant damunt la prestatgeria
        for y in range(0, 13):
            cv.put(BULB_X, y, IRON, 2.0)
            cv.put(BULB_X + 1, y, IRON, 1.0)
        cv.rect(308, 13, 324, 16, IRON, lambda xx, yy: 3.0 - (xx - 308) * 0.12 + (0.6 if yy == 13 else 0))
        cv.rect(313, 11, 319, 12, IRON, 2.6)
        cv.disc(BULB_X, 19.5, 3.3, 3.3, [(255, 240, 200)], 0, 0)
        cv.put(BULB_X - 1, 18, [(255, 252, 236)], 0, 0)
        cv.glow(BULB_X, 20, 45, (255, 226, 160), 0.45)

    if 'tauler' in parts:
        # ─── Banc de treball (445..587) amb el tauler d'eines ─────────────────────
        # tauler d'eines (silueta pintada de cada eina: ho vol l'inventari)
        PB0, PB1, PT, PBt = 459, 576, 61, 131
        cv.rect(PB0, PT, PB1, PBt, CORK, lambda x, y: (3.2 if x < PB0 + 3 or y < PT + 3 else (1.0 if x > PB1 - 3 or y > PBt - 3 else 2.4))
                + (0.0 if (x - PB0) % 8 else -0.2) + (hr(x, y, 9) - 0.5) * 0.3)
        for y in range(PT + 5, PBt - 3, 7):                        # forats
            for x in range(PB0 + 5, PB1 - 3, 7):
                cv.put(x, y, CORK, 0.6)
                cv.put(x + 1, y + 1, CORK, 3.4)
        for x, y in ((PB0 + 2, PT + 2), (PB1 - 2, PT + 2), (PB0 + 2, PBt - 2), (PB1 - 2, PBt - 2)):
            cv.put(x, y, IRON, 4.0)
        contact_shadow(cv, PB0, PB1, PBt + 1, 4, 0.8)

        def shadowed(draw):
            """Dibuixa la silueta pintada (un píxel avall-dreta) i l'eina al damunt."""
            draw(1, 1, True)
            draw(0, 0, False)

        def hammer(ox, oy, sil):
            r, l = (PAPER, 2.2) if sil else (WALNUT, None)
            cv.rect(469 + ox, 72 + oy, 472 + ox, 101 + oy, r, l if sil else (lambda x, y: 3.8 - (x - 469 - ox) * 0.5))
            cv.rect(463 + ox, 68 + oy, 479 + ox, 72 + oy, PAPER if sil else F9, 2.2 if sil else (lambda x, y: 4.2 - (y - 68 - oy) * 0.4))
            if not sil:
                cv.rect(463, 68, 465, 72, F9, 2.6)                     # l'orella de treure claus

        def saw(ox, oy, sil):
            for y in range(69, 94):
                w = 5 + (y - 69) // 2
                for x in range(488, 488 + w):
                    cv.put(x + ox, y + oy, PAPER if sil else F9, 2.2 if sil else (4.0 if x == 488 + w - 1 else 3.0 + (0.6 if x == 488 else 0)))
            if not sil:
                for y in range(71, 94, 2):                             # les dents
                    cv.put(488 + 5 + (y - 69) // 2, y, F9, 5.0)
            cv.rect(485 + ox, 65 + oy, 493 + ox, 71 + oy, PAPER if sil else WALNUT, 2.2 if sil else 3.4)
            if not sil:
                cv.rect(487, 67, 491, 69, WALNUT, 0.8)

        def wrench_(x0, h):
            def f(ox, oy, sil):
                r = PAPER if sil else F9
                cv.rect(x0 + ox, 72 + oy, x0 + 1 + ox, 72 + h + oy, r, 2.2 if sil else (lambda x, y: 3.9 - (x - x0) * 0.6))
                cv.rect(x0 - 1 + ox, 69 + oy, x0 + 2 + ox, 72 + oy, r, 2.2 if sil else 4.2)
                cv.put(x0 + ox, 69 + oy, CORK, 1.0)
                cv.put(x0 + 1 + ox, 69 + oy, CORK, 1.0)
            return f

        def pliers(ox, oy, sil):
            r = PAPER if sil else F9
            for i in range(21):
                cv.put(549 + ox - i // 8, 73 + i + oy, r, 2.2 if sil else 3.6)
                cv.put(553 + ox + i // 8, 73 + i + oy, r, 2.2 if sil else 3.0)
            cv.rect(549 + ox, 69 + oy, 553 + ox, 73 + oy, r, 2.2 if sil else 4.0)
            if not sil:
                cv.put(551, 71, F9, 1.0)                               # el pern

        for d in (hammer, saw, wrench_(512, 27), wrench_(520, 21), wrench_(528, 16), pliers):
            shadowed(d)
        for x in range(563, 574, 4):                                # tornavisos
            shadowed(lambda ox, oy, sil, x=x: (cv.rect(x + ox, 69 + oy, x + 1 + ox, 77 + oy, PAPER if sil else RED, 2.2 if sil else 3.0),
                                               cv.vline(x + ox, 78 + oy, 93 + oy, PAPER if sil else F9, 2.2 if sil else 4.0)))
        # tira de rètol al tauler
        cv.rect(475, 109, 560, 123, ENAMEL, lambda x, y: 3.8 if 475 < x < 560 and 109 < y < 123 else 1.6, 0.5)
        s = 'INVENTARI'
        text(cv, 517 - text_w(s) // 2, 113, s, IRON, 0.6, 0)

    if 'banc' in parts:
        # banc: potes, travesser, tauler gruixut
        contact_shadow(cv, BX0, BX1, 211, 13, 1.0)
        for x in (BX0 + 11, BX1 - 15):                                   # potes del darrere
            cv.rect(x, 163, x + 2, 208, WOOD2, 1.4)
        for x in (BX0 + 4, BX1 - 8):                                     # potes del davant
            cv.rect(x, 163, x + 4, 219, WOOD2, lambda xx, yy: 3.0 - (xx - x) * 0.5 + (hr(xx, yy // 6, 2) - 0.5) * 0.2)
        cv.rect(BX0 + 8, 195, BX1 - 8, 198, WOOD2, lambda xx, yy: 2.6 - (yy - 195) * 0.6)
        # prestatge de sota amb un bidó d'oli i draps
        cv.rect(BX0 + 40, 176, BX0 + 59, 193, IRON, lambda xx, yy: 3.0 - (xx - BX0 - 40) * 0.1 - (0.8 if (yy - 176) % 7 == 6 else 0))
        cv.hline(BX0 + 40, BX0 + 59, 176, IRON, 4.2)
        cv.disc(BX0 + 45, 177, 1.6, 0.8, IRON, 1.0)                      # el tap
        cv.rect(BX0 + 44, 182, BX0 + 54, 187, RED, 2.4, 0.6)             # l'etiqueta
        cv.rect(BX0 + 67, 187, BX0 + 88, 193, PAPER, lambda xx, yy: 2.4 + hr(xx, yy) * 0.6 - (0.6 if (xx + yy) % 6 == 0 else 0))
        for y in range(147, 156):
            t = (y - 147) / 8
            for x in range(BX0 + 1 - round(t * 3), BX1 - 1 + round(t * 3) + 1):
                cv.put(x, y, WOOD2, 3.2 + t * 0.6 + (hr(x // 6, 31) - 0.5) * 0.5 - (0.8 if hr(x, y, 9) > 0.95 else 0)
                       + (0.3 if (x - BX0) % 24 == 0 else 0))
        cv.rect(BX0 - 3, 156, BX1 + 3, 161, WOOD2, lambda xx, yy: [4.4, 3.8, 3.4, 3.0, 2.4, 0.8][yy - 156])
        for x in range(BX0, BX1, 24):                                   # les testes dels taulons
            cv.vline(x, 157, 160, WOOD2, 1.6)
        # cargol de banc a l'esquerra
        cv.rect(BX0 + 5, 136, BX0 + 29, 146, F9, lambda xx, yy: 3.4 - (yy - 136) * 0.12 - (xx - BX0 - 5) * 0.04)
        cv.hline(BX0 + 5, BX0 + 29, 136, F9, 4.8)
        cv.vline(BX0 + 17, 137, 146, F9, 1.6)                           # les mordasses
        cv.rect(BX0 + 16, 129, BX0 + 19, 136, F9, lambda xx, yy: 3.0 - (xx - BX0 - 16) * 0.4)
        cv.rect(BX0 - 5, 140, BX0 + 5, 141, F9, lambda xx, yy: 4.0 - (yy - 140))
        cv.disc(BX0 - 7, 140.5, 2, 2, F9, lambda nx, ny: 3.6 - nx - ny)
        cv.disc(BX0 + 6, 140.5, 2, 2, F9, lambda nx, ny: 3.6 - nx - ny)
        for y in range(156, 174):
            cv.put(BX0 + 17, y, F9, 3.0)
            cv.put(BX0 + 18, y, F9, 1.6)
        # registre d'inventari obert i safata de cargols (la feina de la Mira)
        for y in range(141, 151):
            t = (y - 141) / 9
            for x in range(528 - round(t * 3), 560 + round(t * 3)):
                lvl = 4.2 - (1.2 if abs(x - 544) < 1 else 0) - (y - 141) * 0.04
                cv.put(x, y, PAPER, lvl)
        for ly in (143, 146, 149):
            for x in range(531, 557):
                if abs(x - 544) > 1 and hr(x // 2, ly) > 0.3:
                    cv.put(x, ly, PAPER, 2.0)
        cv.line(552, 141, 558, 137, RED, 2.8)                           # el llapis
        cv.rect(491, 141, 515, 148, IRON, lambda xx, yy: 2.4 + (1.0 if yy == 141 else 0) - (0.8 if xx == 515 else 0))
        for x in range(492, 515):
            cv.put(x, 140, F9, 3.4 + hr(x, 2) * 1.8)
            if hr(x, 5) > 0.5:
                cv.put(x, 139, F9, 4.0)
        # llauna d'oli amb broc
        cv.rect(568, 135, 576, 147, GOLD, lambda xx, yy: 3.6 - (xx - 568) * 0.3 + (0.5 if yy == 135 else 0))
        cv.hline(568, 576, 140, GOLD, 1.8)
        cv.line(576, 136, 583, 128, GOLD, 3.0)
        cv.line(576, 137, 583, 129, GOLD, 1.6)

    if 'llum' in parts:
        # Llum penjant d'esmalt sobre el banc
        LX = LAMP_X
        for y in range(0, 93):
            cv.put(LX, y, IRON, 1.8)
        cv.rect(LX - 2, 90, LX + 2, 93, IRON, 2.6)
        for y in range(93, 105):
            t = (y - 93) / 11
            half = 4 + t * 13
            for x in range(round(LX - half), round(LX + half) + 1):
                u = (x - LX) / half
                cv.put(x, y, LAMPG, 3.4 - u * 1.4 - (1 - t) * 0.6 + (1.4 if y == 95 and u < 0 else 0), 0.3)
        cv.hline(LX - 16, LX + 16, 105, [(255, 236, 170)], 0, 0)
        cv.disc(LX, 107, 4, 2, [(255, 246, 210)], 0, 0)
        cv.glow(LX, 112, 53, (255, 226, 150), 0.42)

    if 'taquilla' in parts:
        # ─── Taquilla de la Mira (595..632) ───────────────────────────────────────
        KX0, KX1, KT, KB = 595, 632, 75, 208
        contact_shadow(cv, KX0, KX1, 209, 7, 1.0)
        cv.rect(KX0, KT, KX1, KB, GREEN, lambda x, y: 2.4 + (0.9 if x == KX0 or y == KT else 0) - (1.2 if x >= KX1 - 1 else 0) + (hr(x // 4, y // 8, 4) - 0.5) * 0.2)
        cv.rect(KX0 + 4, KT + 4, KX1 - 4, KB - 5, GREEN, lambda x, y: 2.7 - (x - KX0) * 0.025)
        cv.vline(KX0 + 4, KT + 4, KB - 5, GREEN, 1.0)
        cv.hline(KX0 + 4, KX1 - 4, KT + 4, GREEN, 1.0)
        cv.vline(KX1 - 4, KT + 4, KB - 5, GREEN, 3.6)
        cv.hline(KX0 + 4, KX1 - 4, KB - 5, GREEN, 3.4)
        for y in range(KT + 11, KT + 32, 4):                          # reixeta de ventilació
            cv.hline(KX0 + 11, KX1 - 11, y, GREEN, 0.6)
            cv.hline(KX0 + 11, KX1 - 11, y + 1, GREEN, 3.4)
        for y in (KT + 10, KB - 12):                                  # les frontisses
            cv.rect(KX0 + 1, y, KX0 + 2, y + 5, IRON, 3.0)
        cv.rect(KX0 + 5, KT + 40, KX1 - 5, KT + 49, MANILA, lambda x, y: 4.0 if KX0 + 5 < x < KX1 - 5 and KT + 40 < y < KT + 49 else 2.0, 0.6)
        text(cv, (KX0 + KX1) // 2 - text_w('MIRA') // 2, KT + 42, 'MIRA', IRON, 0.6, 0)
        cv.rect(KX1 - 11, KT + 67, KX1 - 8, KT + 80, IRON, lambda x, y: 3.6 - (x - KX1 + 11) * 0.6)
        cv.disc(KX1 - 9.5, KT + 85, 1.5, 1.5, GOLD, 3.6)              # el cadenat
        for x in range(KX0 + 6, KX1 - 5, 3):
            if hr(x, 9) > 0.6:
                cv.put(x, KB - 8, RUST, 2.4)
                if hr(x, 10) > 0.5:
                    cv.put(x, KB - 7, RUST, 1.6)
        cv.hline(KX0 - 1, KX1 + 1, KT - 1, GREEN, 3.8)
        cv.hline(KX0 - 1, KX1 + 1, KT - 2, GREEN, 2.6)

    if 'tint' in parts:
        # tint càlid de les bombetes
        cv.tint(0, 0, W - 1, 273, (255, 190, 110),
                lambda x, y: max(0, 1 - math.hypot(x - LAMP_X, (y - 127) * 0.9) / 200) ** 2 * 0.15
                + max(0, 1 - math.hypot(x - BULB_X, (y - 40) * 0.9) / 187) ** 2 * 0.12)


def anim_layer(cv, tt):
    """Pols que sura a la llum de les dues bombetes, i una arna que volta el llum del banc (al damunt de tot)."""
    dust(cv, tt, 18, 31, (493, 112, 547, 139), (255, 236, 190), 0.7, lamp_cone, fall=(3, 7), wander=2.7)
    dust(cv, tt, 18, 32, (277, 27, 357, 69), (255, 232, 180), 0.6, bulb_halo, fall=(-3, 7), wander=2.7)
    moth(cv, tt)


@lru_cache(maxsize=None)
def _room():
    cv = Canvas(light=LIGHT)
    room(cv)
    return cv.img


def bg(cv, t=0.0):
    """t (0..1): moment del cicle de la capa animada (None: la sala sense la capa animada)."""
    cv.img.paste(_room())
    if t is not None:
        anim_layer(cv, t)


def plomall(cv):
    """El plomall, penjat del ganxo (148..181 × 80..181): mànec de fusta i un plomall gros de plomes d'estruç."""
    HX = 164
    # cordill
    cv.put(HX, 87, PAPER, 3.0); cv.put(HX - 1, 88, PAPER, 2.6); cv.put(HX + 1, 88, PAPER, 2.6)
    cv.put(HX - 1, 89, PAPER, 2.2); cv.put(HX + 1, 89, PAPER, 2.2)
    cv.put(HX - 1, 90, PAPER, 1.8); cv.put(HX + 1, 90, PAPER, 1.8)
    # mànec torneat
    for y in range(91, 139):
        cv.put(HX - 2, y, WALNUT, 3.6)
        cv.put(HX - 1, y, WALNUT, 4.2)
        cv.put(HX, y, WALNUT, 3.0)
        cv.put(HX + 1, y, WALNUT, 1.8)
        if y in (106, 107, 108, 122, 123):                          # els anells del torn
            cv.put(HX - 3, y, WALNUT, 3.4 if y != 108 else 2.2)
            cv.put(HX + 2, y, WALNUT, 1.4)
    cv.rect(HX - 3, 133, HX + 2, 139, GOLD, lambda x, y: 4.2 - (x - HX + 3) * 0.6 + (0.5 if y == 133 else 0))   # virolla
    cv.hline(HX - 3, HX + 2, 136, GOLD, 1.8)
    # plomes: un bulb que s'eixampla cap avall, amb les plomes que surten de la virolla
    FEATH = [(30, 22, 22), (62, 46, 40), (98, 76, 62), (138, 112, 88), (176, 150, 118), (210, 190, 156), (236, 222, 196)]
    OY = 135
    for y in range(139, 183):
        t = (y - 139) / 43
        half = 4 + 12.7 * math.sin(min(1.0, t * 1.25) * math.pi / 2) ** 0.8 - max(0, t - 0.8) * 29
        for x in range(round(HX - half - 1), round(HX + half + 2)):
            nx = (x - HX) / max(half, 1)
            if abs(nx) > 1 + (hr(x, y, 8) - 0.5) * 0.35:
                continue                                           # vora esfilagarsada
            ang = math.atan2(x - HX, y - OY)
            strand = math.sin(ang * 45 + hr(int(ang * 22), 3) * 3) * 0.7
            lvl = 3.4 - nx * 1.2 + strand - abs(nx) ** 3 * 0.8 + (0.4 if t < 0.15 else 0)
            if hr(int(ang * 22), 11) > 0.75:
                lvl -= 1.2                                         # plomes fosques barrejades
            if hr(x, y, 12) > 0.96:
                lvl += 0.8                                         # un fil de ploma que agafa la llum
            cv.put(x, y, FEATH, lvl)
    # puntes que pengen
    for i in range(12):
        x = HX - 8 + i * 1.5
        for j in range(hr(i, 4) > 0.5 and 4 or 2):
            cv.put(round(x), 180 + j, FEATH, 3.0 - j * 0.5)
    outline(cv, 144, 88, 185, 187)
    cv.glow(HX, 157, 16, (255, 230, 190), 0.08)


def caixa_eines(cv):
    """La caixa d'eines enorme, a terra (480..557 × 191..252): fusta amb cantoneres de ferro i la nansa."""
    X0, X1, T, B = 483, 553, 216, 248
    contact_shadow(cv, X0, X1, B + 1, 5, 1.0)
    # eines que sobresurten (darrere la nansa)
    cv.rect(495, 196, 499, 217, WALNUT, lambda x, y: 4.0 - (x - 495) * 0.6)          # mànec de martell
    cv.rect(488, 191, 507, 196, F9, lambda x, y: 4.6 - (y - 191) * 0.5)
    cv.rect(488, 191, 489, 196, F9, 2.0)
    cv.hline(488, 507, 191, F9, 5.2)
    for y in range(200, 217):                                                       # serra
        for x in range(531, 538 + (y - 200) // 3):
            cv.put(x, y, F9, 3.6 if x < 537 + (y - 200) // 3 else 5.0)
    cv.rect(528, 195, 539, 201, WALNUT, 3.0)
    cv.rect(530, 196, 537, 199, WALNUT, 0.6)
    cv.vline(512, 203, 217, F9, 4.0); cv.vline(513, 203, 217, F9, 2.4)             # clau anglesa
    cv.rect(511, 200, 515, 203, F9, 4.4)
    cv.put(513, 200, F9, 1.0)
    # cos: taulons pintats de vermell fosc
    for y in range(T, B + 1):
        for x in range(X0, X1 + 1):
            lvl = 2.6 + (hr(x // 4, (y - T) // 8) - 0.5) * 0.3 - (x - X0) / (X1 - X0) * 0.6
            if (y - T) % 11 == 10:
                lvl -= 0.9
            elif (y - T) % 11 == 0:
                lvl += 0.4
            if hr(x // 2, y // 2, 6) > 0.92:
                cv.put(x, y, WALNUT, 2.6 + (hr(x, y, 7) - 0.5) * 0.4)   # pintura gastada
                continue
            cv.put(x, y, RED, lvl)
    cv.hline(X0, X1, T, RED, 4.0)
    cv.vline(X0, T, B, RED, 3.6)
    cv.vline(X1, T, B, RED, 1.0)
    cv.hline(X0, X1, B, RED, 0.8)
    # cantoneres i franges de ferro
    for cx in (X0, X1 - 5):
        cv.rect(cx, T, cx + 5, T + 5, IRON, lambda x, y: 3.4 - (y - T) * 0.25)
        cv.rect(cx, B - 5, cx + 5, B, IRON, 2.6)
        cv.put(cx + 2, T + 2, IRON, 5.0); cv.put(cx + 3, T + 3, IRON, 1.4)
        cv.put(cx + 2, B - 3, IRON, 4.4); cv.put(cx + 3, B - 2, IRON, 1.2)
    # nansa de ferro de banda a banda
    for x in range(X0 + 5, X1 - 4):
        cv.put(x, 203, IRON, 3.6)
        cv.put(x, 204, IRON, 1.6)
    for xx in (X0 + 5, X1 - 6):
        cv.vline(xx, 203, T, IRON, 3.0)
        cv.vline(xx + 1, 203, T, IRON, 1.4)
    cv.rect(507, 201, 531, 205, WALNUT, lambda x, y: 3.8 - (y - 201) * 0.6)
    # placa de llautó amb el número d'inventari
    cv.rect(508, 228, 528, 237, GOLD, lambda x, y: 4.0 if 508 < x < 528 and 228 < y < 237 else 1.8)
    for x in range(511, 526):
        if x % 4:
            cv.put(x, 232, GOLD, 1.6, 0.3)
            cv.put(x, 233, GOLD, 2.2, 0.3)
    cv.put(510, 230, GOLD, 5.0); cv.put(526, 230, GOLD, 5.0)
    outline(cv, 473, 184, 563, B - 1)


PROPS = {'plomall': plomall, 'caixa_eines': caixa_eines}


def _ambient_frames(n=24):
    def draw(t):
        cv = Canvas(light=LIGHT, img=_room().copy())
        anim_layer(cv, t)
        return cv.img.convert('RGB')
    return ambient_frames(bg, LIGHT, n, box=(267, 13, 560, 160), draw=draw)


ANIMS = {'ambient': {'frames': _ambient_frames, 'frameDuration': 130}}
