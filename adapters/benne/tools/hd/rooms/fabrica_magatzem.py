"""
Magatzem d'eines (Iri): el regne del Cargol. Maó amb arrimador pintat, prestatgeria plena de material
inventariat (de ferro-9), banc de treball amb el tauler d'eines, la taquilla de la Mira.
Llums: el llum penjant del banc, la bombeta damunt la prestatgeria i el vidre glaçat del despatx.
"""
import math
import random

from hd.pix import (Light, B4, W, H, hr, mix, WALNUT, FLOOR, GOLD, COPPER, RUST, BRICK, IRON, RED, GREEN, PAPER,
                    MANILA, GLASS, CYAN, LAMPG, GRAY, TEAL, NAVY)
from hd.rooms.fabrica_calderes import (STONE, ENAMEL, CORK, text, text_w, brick_wall, contact_shadow, plank_door,
                                       pipe_h, pipe_v, bracket, ceiling, wall_plinth, gauge, outline)

# metall de ferro-9: acer blavós amb un reflex cian
F9 = [(14, 18, 28), (26, 34, 48), (40, 54, 72), (60, 80, 100), (90, 116, 136), (130, 160, 176), (180, 214, 222), (226, 248, 250)]
WOOD2 = [(22, 14, 16), (40, 26, 24), (62, 40, 30), (88, 58, 38), (116, 80, 48), (146, 104, 62), (178, 134, 82), (210, 170, 110)]
DADO = [(12, 20, 20), (20, 32, 30), (30, 46, 40), (44, 62, 52), (60, 80, 64), (80, 100, 78), (104, 122, 94)]

LIGHT = Light(vignette=(70, 40), floor_fade=(198, 40))
LIGHT.point(388, 84, r=150, k=2.8, squash=1.1, down=True, power=1.8)     # llum penjant del banc
LIGHT.point(237, 20, r=150, k=2.5, squash=0.9, power=1.8)                # bombeta de la prestatgeria
LIGHT.point(87, 98, r=55, k=0.9, power=2.0)                            # vidre glaçat del despatx

FLOOR_Y = 158


def plank_floor(cv, y0):
    """Terra de taulons gastats, en perspectiva."""
    VPX, VPY = 240, -150
    for y in range(y0, H):
        dep = y - VPY
        pw = dep / 30
        for x in range(W):
            u = (x - VPX) / dep * 30 / 1.2
            pl = math.floor(u)
            fr = (u - pl) * pw * 1.2
            r = hr(pl, 7)
            seg = math.floor(3600 / dep / 1.6 + r * 5)
            seg_up = math.floor(3600 / (dep - 1) / 1.6 + r * 5)
            lvl = 2.0 + (hr(pl, seg) - 0.5) * 0.8 + (0.3 if 1 <= fr < 2 else 0)
            if hr(x // 4, y // 2, pl) > 0.93:
                lvl -= 0.5                                         # taques d'oli
            if fr < 1:
                lvl = 0.6
            elif seg != seg_up:
                lvl = 0.8
            if y < y0 + 6:
                lvl -= (y0 + 6 - y) / 6 * 1.2
            cv.put(x, y, FLOOR, lvl)


def bg(cv):
    # ─── Sostre, paret de maó i arrimador pintat ──────────────────────────────
    ceiling(cv)
    brick_wall(cv, 0, 14, W - 1, 151, seed=21, base=1.5,
               extra=lambda x, y: -(40 - y) / 40 * 0.6 if y < 40 else 0)
    # arrimador pintat de verd, amb la pintura saltada
    for y in range(104, 152):
        for x in range(W):
            chip = hr(x // 5, y // 4, 5) > 0.95 or (y < 108 and hr(x // 2, 1) > 0.7)
            if chip:
                continue                                           # s'hi veu el maó
            lvl = 2.2 + (hr(x // 14, (y - 104) // 6) - 0.5) * 0.2
            if (y - 104) % 6 == 5:
                lvl -= 0.5                                         # el relleu de les llagues sota la pintura
            cv.put(x, y, DADO, lvl)
    cv.hline(0, W - 1, 103, DADO, 3.4)
    cv.hline(0, W - 1, 104, DADO, 1.0)
    wall_plinth(cv, 152, 157)
    plank_floor(cv, FLOOR_Y)
    pipe_h(cv, 0, W - 1, 16, 4, IRON, 2.4, flange_every=72)
    for x in range(30, W, 72):
        bracket(cv, x, 20)

    # ─── Porta de la sala de calderes (8..58 × 65..155) ───────────────────────
    cv.rect(5, 59, 61, 64, STONE, lambda x, y: [3.6, 3.0, 2.6, 2.4, 2.0, 0.8][y - 59])
    plank_door(cv, 8, 65, 58, 155, base=2.2)
    s = 'CALDERES'
    cv.rect(16, 74, 50, 82, ENAMEL, lambda x, y: 3.8 if 16 < x < 50 and 74 < y < 82 else 1.6, 0.6)
    text(cv, 33 - text_w(s) // 2, 76, s, IRON, 1.0, 0)

    # ─── Porta del despatx del director (65..109 × 60..155) ───────────────────
    PX0, PY0, PX1 = 66, 62, 108
    cv.rect(PX0 - 1, PY0 - 2, PX1 + 1, 155, WALNUT, lambda x, y: 3.4 if y < PY0 + 1 else (3.0 if x < PX0 + 2 else (1.2 if x > PX1 - 2 else 2.4)))
    cv.rect(PX0 + 3, PY0 + 3, PX1 - 3, 155, WALNUT, 0.6)
    LX0, LX1, LY0 = PX0 + 4, PX1 - 4, PY0 + 4

    def door(x, y):
        g = (hr(x // 3, 78) - 0.5) * 0.3
        if LX0 + 5 <= x <= LX1 - 5 and LY0 + 5 <= y <= LY0 + 38:
            return None
        if LX0 + 5 <= x <= LX1 - 5 and LY0 + 46 <= y <= 146:
            if x == LX0 + 5 or y == LY0 + 46:
                return 1.0
            if x == LX1 - 5 or y == 146:
                return 3.4
            if x == LX0 + 6 or y == LY0 + 47:
                return 3.2
            return 2.5 + g
        return 2.1 + g + (0.6 if x == LX0 else 0) - (0.8 if x == LX1 else 0)

    for y in range(LY0, 155):
        for x in range(LX0, LX1 + 1):
            v = door(x, y)
            if v is None:
                gv = 2.6 + (y - LY0) / 34 * 0.9 + (hr(x // 2, y // 2) - 0.5) * 0.5 - abs(x - 87) / 26
                cv.put(x, y, GLASS, gv, 0.5)
            else:
                cv.put(x, y, WALNUT, v)
    cv.hline(LX0 + 4, LX1 - 4, LY0 + 4, WALNUT, 1.0)
    cv.hline(LX0 + 4, LX1 - 4, LY0 + 39, WALNUT, 3.4)
    # «DIRECCIÓ» en lletres daurades al vidre
    for x in range(77, 98):                                    # lletres daurades («DIRECCIÓ»)
        if (x - 77) % 3 != 2:
            cv.put(x, 79, GOLD, 4.0, 0.2)
            if hr(x, 5) > 0.4:
                cv.put(x, 80, GOLD, 3.2, 0.2)
    for x in range(81, 94, 2):
        cv.put(x, 84, GOLD, 3.0, 0.2)
    cv.glow(87, 92, 24, (240, 200, 120), 0.2)
    # pom de llautó
    cv.rect(LX1 - 6, 112, LX1 - 3, 122, GOLD, 2.6)
    cv.disc(LX1 - 4.5, 115, 2, 2, GOLD, lambda nx, ny: 4.5 - nx - ny)
    cv.put(LX1 - 5, 119, GOLD, 0.2)

    # Rètol de les normes del Cargol, damunt les portes
    cv.rect(14, 28, 104, 50, ENAMEL, lambda x, y: (1.4 if x in (14, 104) or y in (28, 50) else 3.9) - (y - 28) * 0.02, 0.5)
    cv.rect(16, 30, 102, 48, ENAMEL, lambda x, y: 4.0 if not (x in (16, 102) or y in (30, 48)) else 2.6, 0.5)
    for s, y in (('SENSE FORMULARI', 33), ('NO HI HA MATERIAL', 41)):
        text(cv, 59 - text_w(s) // 2, y, s, RED, 2.6, 0.3)
    for cx, cy in ((18, 32), (100, 32), (18, 46), (100, 46)):
        cv.put(cx, cy, IRON, 1.0, 0.3)

    # ─── Ganxo del plomall (el plomall és un prop) ───────────────────────────
    cv.rect(119, 60, 127, 62, IRON, lambda x, y: 3.2 - (y - 60) * 0.8)
    cv.put(120, 61, IRON, 4.2); cv.put(126, 61, IRON, 4.2)
    for i, (x, y) in enumerate(((123, 63), (123, 64), (123, 65), (124, 66), (125, 66), (126, 65))):
        cv.put(x, y, IRON, 3.4 if i < 3 else 2.4)

    # ─── Prestatgeria (152..322 × 21..150) ───────────────────────────────────
    SX0, SX1, ST, SB = 152, 322, 22, 150
    SHELVES = [47, 73, 99, 125]
    # fons fosc i ombra a la paret
    for y in range(ST, SB + 1):
        for x in range(SX0, SX1 + 1):
            cv.put(x, y, WOOD2, 0.7 + (hr(x // 6, 4) - 0.5) * 0.3)
    contact_shadow(cv, SX0, SX1, 151, 7, 1.0)
    rnd = random.Random(7)
    tops = [ST + 4] + [sy + 4 for sy in SHELVES]
    bottoms = SHELVES + [SB - 4]

    def crate(x, yb, w, h, lab=True, ramp=WOOD2, base=3.0):
        cv.rect(x, yb - h, x + w - 1, yb - 1, ramp, lambda xx, yy: base + (hr(xx // 2, yy // 4, x) - 0.5) * 0.4
                - (0.8 if (yy - (yb - h)) % 5 == 4 else 0) - (1.2 if xx == x + w - 1 else 0) + (0.6 if xx == x else 0))
        cv.hline(x, x + w - 1, yb - h, ramp, base + 1.2)
        if lab and w > 8:
            lx = x + w // 2 - 3
            cv.rect(lx, yb - h + 3, lx + 6, yb - h + 6, PAPER, 4.2)
            cv.hline(lx + 1, lx + 5, yb - h + 4, PAPER, 2.0)

    def jar(x, yb):
        # pot de vidre amb cargols de ferro-9
        cv.rect(x, yb - 11, x + 6, yb - 1, GLASS, lambda xx, yy: 1.2 + (1.6 if xx == x + 1 else 0), 0.6)
        for yy in range(yb - 7, yb - 1):
            for xx in range(x + 1, x + 6):
                if hr(xx, yy, 1) > 0.35:
                    cv.put(xx, yy, F9, 3.0 + hr(xx, yy, 2) * 1.6)
        cv.rect(x + 1, yb - 13, x + 5, yb - 12, RED, 2.6)
        cv.put(x + 1, yb - 9, PAPER, 4.0)

    def coil(x, yb):
        cv.disc(x + 5, yb - 5, 5, 5, COPPER, lambda nx, ny: 3.4 - nx - ny + (0.8 if int((nx + 1) * 6) % 2 else 0))
        cv.disc(x + 5, yb - 5, 1.8, 1.8, WOOD2, 0.6)
        return 11

    def magnet(x, yb):
        # imant de ferradura, vermell amb les puntes de ferro-9
        for yy in range(yb - 10, yb):
            for xx in range(x, x + 8):
                nx, ny = (xx - x - 3.5) / 4, (yy - yb + 6) / 4
                d = math.hypot(nx, min(ny, 0) if ny < 0 else 0) if True else 0
                if ny < 0:
                    if 0.45 < math.hypot(nx, ny) < 1.0:
                        cv.put(xx, yy, RED, 3.4 - nx - ny)
                elif abs(nx) > 0.45 and abs(nx) < 1.0:
                    if yy >= yb - 3:
                        cv.put(xx, yy, F9, 4.6 - nx)
                    else:
                        cv.put(xx, yy, RED, 3.0 - nx)
        return 10

    def wrenches(x, yb):
        for i in range(3):
            xx = x + i * 3
            h = 14 + i * 2
            cv.vline(xx + 1, yb - h + 3, yb - 1, F9, 3.6)
            cv.vline(xx + 2, yb - h + 3, yb - 1, F9, 2.2)
            cv.rect(xx, yb - h, xx + 3, yb - h + 2, F9, 4.0)
            cv.put(xx + 1, yb - h, WOOD2, 0.4)
        return 11

    def bin_(x, yb, w=14):
        # calaix-safata de xapa amb cargols i etiqueta
        cv.rect(x, yb - 7, x + w - 1, yb - 1, IRON, lambda xx, yy: 2.6 - (yy - yb + 7) * 0.1 + (0.8 if yy == yb - 7 else 0))
        for xx in range(x + 1, x + w - 1):
            if hr(xx, yb, 3) > 0.3:
                cv.put(xx, yb - 8, F9, 3.4 + hr(xx, 1) * 1.6)
        cv.rect(x + 3, yb - 5, x + w - 4, yb - 3, PAPER, 4.0)
        return w + 1

    for si, (top, bot) in enumerate(zip(tops, bottoms)):
        x = SX0 + 4
        while x < SX1 - 14:
            if abs(x - 237) < 3:
                x = 240
                continue
            k = rnd.choice(['crate', 'crate', 'jar', 'coil', 'magnet', 'wrench', 'bin', 'bin', 'jar'])
            if k == 'crate':
                w = rnd.randint(12, 18)
                if x + w > SX1 - 3 or (x < 237 < x + w):
                    x += 3
                    continue
                crate(x, bot, w, rnd.randint(9, min(18, bot - top - 2)))
            elif k == 'jar':
                w = 8
                jar(x, bot)
            elif k == 'coil':
                w = coil(x, bot)
            elif k == 'magnet':
                w = magnet(x, bot)
            elif k == 'wrench':
                w = wrenches(x, bot)
            else:
                w = bin_(x, bot)
            x += w + rnd.randint(1, 3)
    # muntants i lleixes
    for ux in (SX0, 236, SX1 - 3):
        cv.rect(ux, ST, ux + 3, SB, WOOD2, lambda xx, yy: [3.6, 3.0, 2.4, 1.2][xx - ux] if ux != SX1 - 3 else [3.0, 2.4, 1.6, 0.6][xx - ux])
    for sy in [ST] + SHELVES:
        cv.rect(SX0, sy, SX1, sy + 3, WOOD2, lambda xx, yy: [4.2, 3.4, 2.8, 1.2][yy - sy])
        # etiquetes d'inventari al cantell de cada lleixa
        for lx in range(SX0 + 12, SX1 - 8, 28):
            cv.rect(lx, sy + 1, lx + 7, sy + 3, PAPER, 4.0)
            cv.hline(lx + 1, lx + 5, sy + 2, PAPER, 2.4)
    cv.rect(SX0, SB - 3, SX1, SB, WOOD2, lambda xx, yy: [3.4, 2.6, 2.0, 0.8][yy - SB + 3])
    for ux in (SX0, SX1 - 3):
        cv.rect(ux, SB + 1, ux + 3, SB + 4, WOOD2, 1.6)

    # Bombeta penjant damunt la prestatgeria
    for y in range(0, 10):
        cv.put(237, y, IRON, 2.0)
    cv.rect(231, 10, 243, 12, IRON, lambda xx, yy: 3.0 - (xx - 231) * 0.15)
    cv.disc(237, 14.5, 2.5, 2.5, [(255, 240, 200)], 0, 0)
    cv.glow(237, 15, 34, (255, 226, 160), 0.45)

    # ─── Banc de treball (336..440) amb el tauler d'eines ─────────────────────
    BX0, BX1 = 334, 440
    # tauler d'eines (silueta pintada de cada eina: ho vol l'inventari)
    PB0, PB1, PT, PBt = 344, 432, 46, 98
    cv.rect(PB0, PT, PB1, PBt, CORK, lambda x, y: (3.2 if x < PB0 + 2 or y < PT + 2 else (1.0 if x > PB1 - 2 or y > PBt - 2 else 2.4)) + (0.0 if (x - PB0) % 6 else -0.2))
    for y in range(PT + 4, PBt - 2, 5):                        # forats
        for x in range(PB0 + 4, PB1 - 2, 5):
            cv.put(x, y, CORK, 0.6)
    contact_shadow(cv, PB0, PB1, PBt + 1, 3, 0.8)

    def shadowed(draw):
        """Dibuixa la silueta pintada (un píxel avall-dreta) i l'eina al damunt."""
        draw(1, 1, True)
        draw(0, 0, False)

    def hammer(ox, oy, sil):
        r, l = (PAPER, 2.2) if sil else (WALNUT, 3.4)
        cv.rect(352 + ox, 54 + oy, 354 + ox, 76 + oy, r, l)
        cv.rect(347 + ox, 51 + oy, 359 + ox, 54 + oy, PAPER if sil else F9, 2.2 if sil else 3.8)

    def saw(ox, oy, sil):
        for y in range(52, 70):
            w = 4 + (y - 52) // 2
            for x in range(366, 366 + w):
                cv.put(x + ox, y + oy, PAPER if sil else F9, 2.2 if sil else (4.0 if x == 366 + w - 1 else 3.0))
        cv.rect(364 + ox, 49 + oy, 370 + ox, 53 + oy, PAPER if sil else WALNUT, 2.2 if sil else 3.4)

    def wrench_(x0, h):
        def f(ox, oy, sil):
            r = PAPER if sil else F9
            cv.rect(x0 + ox, 54 + oy, x0 + 1 + ox, 54 + h + oy, r, 2.2 if sil else 3.6)
            cv.rect(x0 - 1 + ox, 52 + oy, x0 + 2 + ox, 54 + oy, r, 2.2 if sil else 4.2)
            cv.put(x0 + ox, 52 + oy, CORK, 1.0)
        return f

    def pliers(ox, oy, sil):
        r = PAPER if sil else F9
        for i in range(16):
            cv.put(412 + ox - i // 6, 55 + i + oy, r, 2.2 if sil else 3.6)
            cv.put(415 + ox + i // 6, 55 + i + oy, r, 2.2 if sil else 3.0)
        cv.rect(412 + ox, 52 + oy, 415 + ox, 55 + oy, r, 2.2 if sil else 4.0)

    for d in (hammer, saw, wrench_(384, 20), wrench_(390, 16), wrench_(396, 12), pliers):
        shadowed(d)
    for x in range(422, 430, 3):                                # tornavisos
        shadowed(lambda ox, oy, sil, x=x: (cv.rect(x + ox, 52 + oy, x + 1 + ox, 58 + oy, PAPER if sil else RED, 2.2 if sil else 3.0),
                                           cv.vline(x + ox, 59 + oy, 70 + oy, PAPER if sil else F9, 2.2 if sil else 4.0)))
    # tira de rètol al tauler
    cv.rect(356, 82, 420, 92, ENAMEL, lambda x, y: 3.8 if 356 < x < 420 and 82 < y < 92 else 1.6, 0.5)
    s = 'INVENTARI'
    text(cv, 388 - text_w(s) // 2, 85, s, IRON, 0.6, 0)

    # banc: potes, travesser, tauler gruixut
    contact_shadow(cv, BX0, BX1, 158, 10, 1.0)
    for x in (BX0 + 3, BX1 - 6):
        cv.rect(x, 122, x + 3, 164, WOOD2, lambda xx, yy: 3.0 - (xx - x) * 0.6)
    for x in (BX0 + 8, BX1 - 11):
        cv.rect(x, 122, x + 2, 156, WOOD2, 1.4)
    cv.rect(BX0 + 6, 146, BX1 - 6, 148, WOOD2, lambda xx, yy: 2.6 - (yy - 146) * 0.8)
    # prestatge de sota amb un bidó d'oli i draps
    cv.rect(BX0 + 30, 132, BX0 + 44, 145, IRON, lambda xx, yy: 3.0 - (xx - BX0 - 30) * 0.12 - (0.8 if (yy - 132) % 5 == 4 else 0))
    cv.hline(BX0 + 30, BX0 + 44, 132, IRON, 4.2)
    cv.rect(BX0 + 50, 140, BX0 + 66, 145, PAPER, lambda xx, yy: 2.4 + hr(xx, yy) * 0.6)
    for y in range(110, 117):
        t = (y - 110) / 6
        for x in range(BX0 + 1 - round(t * 2), BX1 - 1 + round(t * 2) + 1):
            cv.put(x, y, WOOD2, 3.2 + t * 0.6 + (hr(x // 5, 31) - 0.5) * 0.5 - (0.8 if hr(x, y, 9) > 0.95 else 0))
    cv.rect(BX0 - 2, 117, BX1 + 2, 121, WOOD2, lambda xx, yy: [4.4, 3.6, 3.0, 2.4, 0.8][yy - 117])
    # cargol de banc a l'esquerra
    cv.rect(BX0 + 4, 102, BX0 + 22, 110, F9, lambda xx, yy: 3.4 - (yy - 102) * 0.15 - (xx - BX0 - 4) * 0.05)
    cv.hline(BX0 + 4, BX0 + 22, 102, F9, 4.8)
    cv.rect(BX0 + 12, 97, BX0 + 14, 102, F9, 2.6)
    cv.rect(BX0 - 4, 105, BX0 + 4, 106, F9, 4.0)
    cv.disc(BX0 - 5, 105.5, 1.5, 1.5, F9, 3.0)
    for y in range(117, 130):
        cv.put(BX0 + 13, y, F9, 3.0)
    # registre d'inventari obert i safata de cargols (la feina de la Mira)
    for y in range(106, 113):
        t = (y - 106) / 6
        for x in range(396 - round(t * 2), 420 + round(t * 2)):
            mid = 408
            lvl = 4.2 - (1.2 if abs(x - mid) < 1 else 0) - (y - 106) * 0.05
            cv.put(x, y, PAPER, lvl)
    for ly in (107, 109, 111):
        for x in range(398, 418):
            if abs(x - 408) > 1 and hr(x // 2, ly) > 0.3:
                cv.put(x, ly, PAPER, 2.0)
    cv.rect(368, 106, 386, 111, IRON, lambda xx, yy: 2.4 + (1.0 if yy == 106 else 0))
    for x in range(369, 386):
        cv.put(x, 105, F9, 3.4 + hr(x, 2) * 1.8)
        if hr(x, 5) > 0.5:
            cv.put(x, 104, F9, 4.0)
    # llauna d'oli amb broc
    cv.rect(426, 101, 432, 110, GOLD, lambda xx, yy: 3.6 - (xx - 426) * 0.4)
    cv.line(432, 102, 437, 96, GOLD, 3.0)

    # Llum penjant d'esmalt sobre el banc
    LX = 388
    for y in range(0, 70):
        cv.put(LX, y, IRON, 1.8)
    for y in range(70, 79):
        t = (y - 70) / 8
        half = 3 + t * 10
        for x in range(round(LX - half), round(LX + half) + 1):
            u = (x - LX) / half
            cv.put(x, y, LAMPG, 3.4 - u * 1.4 - (1 - t) * 0.6 + (1.4 if y == 71 and u < 0 else 0), 0.3)
    cv.hline(LX - 12, LX + 12, 79, [(255, 236, 170)], 0, 0)
    cv.disc(LX, 80, 3, 1.5, [(255, 246, 210)], 0, 0)
    cv.glow(LX, 84, 40, (255, 226, 150), 0.42)

    # ─── Taquilla de la Mira (444..474) ───────────────────────────────────────
    KX0, KX1, KT, KB = 446, 474, 56, 156
    contact_shadow(cv, KX0, KX1, 157, 5, 1.0)
    cv.rect(KX0, KT, KX1, KB, GREEN, lambda x, y: 2.4 + (0.9 if x == KX0 or y == KT else 0) - (1.2 if x >= KX1 - 1 else 0) + (hr(x // 3, y // 6, 4) - 0.5) * 0.2)
    cv.rect(KX0 + 3, KT + 3, KX1 - 3, KB - 4, GREEN, lambda x, y: 2.7 - (x - KX0) * 0.03)
    cv.vline(KX0 + 3, KT + 3, KB - 4, GREEN, 1.0)
    cv.hline(KX0 + 3, KX1 - 3, KT + 3, GREEN, 1.0)
    cv.vline(KX1 - 3, KT + 3, KB - 4, GREEN, 3.6)
    for y in range(KT + 8, KT + 24, 3):                          # reixeta de ventilació
        cv.hline(KX0 + 8, KX1 - 8, y, GREEN, 0.6)
        cv.hline(KX0 + 8, KX1 - 8, y + 1, GREEN, 3.4)
    cv.rect(KX0 + 4, KT + 30, KX1 - 4, KT + 37, MANILA, lambda x, y: 4.0 if KX0 + 4 < x < KX1 - 4 and KT + 30 < y < KT + 37 else 2.0, 0.6)
    text(cv, (KX0 + KX1) // 2 - text_w('MIRA') // 2, KT + 32, 'MIRA', IRON, 0.6, 0)
    cv.rect(KX1 - 8, KT + 50, KX1 - 6, KT + 60, IRON, lambda x, y: 3.6 - (x - KX1 + 8) * 0.8)
    for x in range(KX0 + 5, KX1 - 4, 4):
        if hr(x, 9) > 0.6:
            cv.put(x, KB - 6, RUST, 2.4)
    cv.hline(KX0 - 1, KX1 + 1, KT - 1, GREEN, 3.8)

    # tint càlid de les bombetes
    cv.tint(0, 0, W - 1, 205, (255, 190, 110),
            lambda x, y: max(0, 1 - math.hypot(x - 388, (y - 95) * 0.9) / 150) ** 2 * 0.15
            + max(0, 1 - math.hypot(x - 237, (y - 30) * 0.9) / 140) ** 2 * 0.12)


def plomall(cv):
    """El plomall, penjat del ganxo (111..136 × 60..136): mànec de fusta i un plomall gros de plomes d'estruç."""
    HX = 123
    # cordill
    cv.put(HX, 65, PAPER, 3.0); cv.put(HX - 1, 66, PAPER, 2.6); cv.put(HX + 1, 66, PAPER, 2.6)
    cv.put(HX - 1, 67, PAPER, 2.2); cv.put(HX + 1, 67, PAPER, 2.2)
    # mànec torneat
    for y in range(68, 104):
        cv.put(HX - 1, y, WALNUT, 4.2)
        cv.put(HX, y, WALNUT, 3.2)
        cv.put(HX + 1, y, WALNUT, 1.8)
        if y in (80, 81, 92):
            cv.put(HX - 2, y, WALNUT, 3.4)
            cv.put(HX + 2, y, WALNUT, 1.4)
    cv.rect(HX - 2, 100, HX + 2, 104, GOLD, lambda x, y: 4.2 - (x - HX + 2) * 0.7)          # virolla
    # plomes: un bulb que s'eixampla cap avall, amb les plomes que surten de la virolla
    FEATH = [(30, 22, 22), (62, 46, 40), (98, 76, 62), (138, 112, 88), (176, 150, 118), (210, 190, 156), (236, 222, 196)]
    OY = 101
    for y in range(104, 137):
        t = (y - 104) / 32
        half = 3 + 9.5 * math.sin(min(1.0, t * 1.25) * math.pi / 2) ** 0.8 - max(0, t - 0.8) * 22
        for x in range(round(HX - half - 1), round(HX + half + 2)):
            nx = (x - HX) / max(half, 1)
            if abs(nx) > 1 + (hr(x, y, 8) - 0.5) * 0.35:
                continue                                           # vora esfilagarsada
            ang = math.atan2(x - HX, y - OY)
            strand = math.sin(ang * 34 + hr(int(ang * 17), 3) * 3) * 0.7
            lvl = 3.4 - nx * 1.2 + strand - abs(nx) ** 3 * 0.8 + (0.4 if t < 0.15 else 0)
            if hr(int(ang * 17), 11) > 0.75:
                lvl -= 1.2                                         # plomes fosques barrejades
            cv.put(x, y, FEATH, lvl)
    # puntes que pengen
    for i in range(9):
        x = HX - 6 + i * 1.5
        for j in range(hr(i, 4) > 0.5 and 3 or 2):
            cv.put(round(x), 135 + j, FEATH, 3.0 - j * 0.5)
    outline(cv, 108, 66, 139, 140)
    cv.glow(HX, 118, 12, (255, 230, 190), 0.08)


def caixa_eines(cv):
    """La caixa d'eines enorme, a terra (360..417 × 152..188): fusta amb cantoneres de ferro i el nansa."""
    X0, X1, T, B = 362, 415, 162, 186
    contact_shadow(cv, X0, X1, B + 1, 4, 1.0)
    # eines que sobresurten (darrere la nansa)
    cv.rect(371, 147, 374, 163, WALNUT, lambda x, y: 4.0 - (x - 371) * 0.8)          # mànec de martell
    cv.rect(366, 143, 380, 147, F9, lambda x, y: 4.6 - (y - 143) * 0.6)
    cv.rect(366, 143, 367, 147, F9, 2.0)
    for y in range(150, 163):                                                       # serra
        for x in range(398, 403 + (y - 150) // 3):
            cv.put(x, y, F9, 3.6 if x < 402 + (y - 150) // 3 else 5.0)
    cv.rect(396, 146, 404, 151, WALNUT, 3.0)
    cv.rect(397, 147, 403, 149, WALNUT, 0.6)
    cv.vline(384, 152, 163, F9, 4.0); cv.vline(385, 152, 163, F9, 2.4)             # clau anglesa
    cv.rect(383, 150, 386, 152, F9, 4.4)
    # cos: taulons pintats de vermell fosc
    for y in range(T, B + 1):
        for x in range(X0, X1 + 1):
            lvl = 2.6 + (hr(x // 3, (y - T) // 6) - 0.5) * 0.3 - (x - X0) / (X1 - X0) * 0.6
            if (y - T) % 8 == 7:
                lvl -= 0.9
            elif (y - T) % 8 == 0:
                lvl += 0.4
            if hr(x // 2, y // 2, 6) > 0.92:
                cv.put(x, y, WALNUT, 2.6)                          # pintura gastada
                continue
            cv.put(x, y, RED, lvl)
    cv.hline(X0, X1, T, RED, 4.0)
    cv.vline(X0, T, B, RED, 3.6)
    cv.vline(X1, T, B, RED, 1.0)
    cv.hline(X0, X1, B, RED, 0.8)
    # cantoneres i franges de ferro
    for cx in (X0, X1 - 4):
        cv.rect(cx, T, cx + 4, T + 4, IRON, lambda x, y: 3.4 - (y - T) * 0.3)
        cv.rect(cx, B - 4, cx + 4, B, IRON, 2.6)
        cv.put(cx + 2, T + 2, IRON, 5.0); cv.put(cx + 2, B - 2, IRON, 4.4)
    # nansa de ferro de banda a banda
    for x in range(X0 + 4, X1 - 3):
        cv.put(x, 152, IRON, 3.6)
        cv.put(x, 153, IRON, 1.6)
    for xx in (X0 + 4, X1 - 4):
        cv.vline(xx, 152, T, IRON, 3.0)
        cv.vline(xx + 1, 152, T, IRON, 1.4)
    cv.rect(380, 151, 398, 154, WALNUT, lambda x, y: 3.8 - (y - 151) * 0.7)
    # placa de llautó amb el número d'inventari
    cv.rect(381, 171, 396, 178, GOLD, lambda x, y: 4.0 if 381 < x < 396 and 171 < y < 178 else 1.8)
    for x in range(384, 394):
        if x % 3:
            cv.put(x, 174, GOLD, 1.6, 0.3)
    cv.put(382, 172, GOLD, 5.0); cv.put(395, 172, GOLD, 5.0)
    outline(cv, 355, 138, 422, B - 1)


PROPS = {'plomall': plomall, 'caixa_eines': caixa_eines}
