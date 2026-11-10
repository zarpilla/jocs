"""
Despatx del director (Acte 2, Iri): fusta, paper pintat verd, la nit de la ciutat-fàbrica a la finestra.
Llums: làmpada de banquer a l'escriptori, llum de llautó sobre el retrat, lluna (taca freda al terra).
"""
import math
import random

from PIL import Image, ImageChops

from hd.rooms.fabrica_calderes import drift

from hd.pix import (Canvas, Light, B4, W, H, hr, mix, WALNUT, GREEN, FLOOR, GOLD, RED, NAVY, SKIN, GRAY, SUIT, PAPER,
                    MANILA, SKY, SIL, IRON, BLUEP, CYAN, LAMPG, COPPER, SMOKE, GLASS)

LIGHT = Light(vignette=(80, 46), floor_fade=(196, 36))
LIGHT.point(349, 104, r=160, k=2.7, squash=1.15, down=True)          # làmpada de banquer
LIGHT.add(lambda x, y: max(0.0, 1 - math.hypot(x - 232, (y - 34) * 0.75) / 48) ** 1.5 * 1.5 if y >= 30 else 0.0)  # llum del retrat


def moon(x, y):
    """Taca de lluna al terra (amb l'ombra dels travessers de la finestra)."""
    if not 162 <= y <= 198:
        return 0.0
    t = (y - 162) / 36
    xl, xr = 108 + t * 44, 168 + t * 70
    if not xl <= x <= xr:
        return 0.0
    s = (x - xl) / (xr - xl)
    if abs(t - 0.33) < 0.04 or abs(t - 0.66) < 0.04:
        return 0.0
    edge = min(s, 1 - s, t * 2, (1 - t) * 2)
    return min(1.0, edge * 6)


# ─── Animació de fons (també la fan servir el magatzem i el moll) ───────────
def dust(cv, tt, n, seed, box, col, k=0.5, mask=None, fall=(-3, 6), wander=2.0):
    """Pols que sura dins un feix de llum (moment tt = 0..1 del cicle). Cada mota fa un tram curt (fall = dx, dy
    al llarg del cicle), amb un balanceig lateral, i neix i s'apaga (sin(π·s)) quan el seu tram torna a començar:
    cada una en un moment diferent, i el bucle no es nota. `mask(x, y)` → 0..1: on hi ha llum per veure-la."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    for _ in range(n):
        bx, by = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        s0, m, fi = rnd.random(), rnd.choice((1, 2, 3)), rnd.uniform(0, 6.283)
        amp = rnd.uniform(0.4, 1.0) * wander
        sp = rnd.uniform(0.6, 1.0)
        s = (s0 + tt) % 1
        x = round(bx + fall[0] * sp * s + amp * math.sin(2 * math.pi * tt * m + fi))
        y = round(by + fall[1] * sp * s + amp * 0.5 * math.sin(2 * math.pi * tt * (4 - m) + fi * 1.7))
        if not (0 <= x < cv.w and 0 <= y < cv.h):
            continue
        a = k * math.sin(math.pi * s) * (mask(x, y) if mask else 1.0)
        if a > 0.06:
            o = cv.P[x, y]
            cv.P[x, y] = mix(o, col, min(1.0, a)) + (o[3],)


def ambient_frames(bg, light, n, box=None, draw=None):
    """Fotogrames de l'animació: bg(cv, t=i/n) menys el fons quiet (bg amb t = 0); només els píxels que canvien.
    `box` = (x0, y0, x1, y1): zona fora de la qual no es mou res. `draw(t)` → imatge: per no haver de redibuixar
    la sala sencera a cada fotograma quan l'animació és només una capa al damunt."""
    if draw is None:
        def draw(t):
            cv = Canvas(light=light)
            bg(cv, t=t)
            return cv.img.convert('RGB')
    base = draw(0.0)
    frames = []
    for i in range(n):
        img = draw(i / n)
        d = ImageChops.difference(base, img).split()
        m = ImageChops.lighter(ImageChops.lighter(d[0], d[1]), d[2]).point(lambda v: 255 if v else 0)
        if box:
            keep = Image.new('L', m.size, 0)
            keep.paste(255, box)
            m = ImageChops.multiply(m, keep)
        fr = Image.new('RGBA', base.size, (0, 0, 0, 0))
        fr.paste(img.convert('RGBA'), mask=m)
        frames.append(fr)
    return frames


def moon_beam(x, y):
    """El raig de lluna a l'aire, de l'ampit de la finestra a la taca del terra (0..1)."""
    s = (y - 100) / 80
    if not 0 <= s <= 1.1:
        return 0.0
    cx, half = 124 + s * 46, 34 + s * 10
    e = 1 - abs(x - cx) / half
    return max(0.0, min(1.0, e * 2.5)) * min(1.0, s * 6)


def bg(cv, t=0.0):
    tt = t                                   # (dins la funció, `t` es fa servir per a altres coses)
    ph = 2 * math.pi * tt
    # ─── Sostre, cornisa i paper pintat ───────────────────────────────────────
    FLOOR_Y = 154

    cv.rect(0, 0, W - 1, 9, WALNUT, lambda x, y: 0.6 + (hr(x // 30) - 0.5) * 0.3)
    for x in range(0, W, 30):                                  # bigues del sostre
        cv.vline(x, 0, 9, WALNUT, 0.0)
    cv.hline(0, W - 1, 10, WALNUT, 3.2)
    cv.hline(0, W - 1, 11, WALNUT, 2.0)
    cv.rect(0, 12, W - 1, 13, WALNUT, 2.6)
    for x in range(0, W, 4):                                   # dentellons
        cv.rect(x, 12, x + 1, 13, WALNUT, 3.4)
    cv.hline(0, W - 1, 14, WALNUT, 1.6)
    cv.hline(0, W - 1, 15, WALNUT, 0.4)


    def damask(x, y):
        u, v = x % 20, (y - 16) % 26
        if ((y - 16) // 26) % 2:
            u = (u + 10) % 20
        a = abs(u - 10) / 10
        b = abs(v - 13) / 13
        ring = a * 1.3 + b
        lvl = 2.0
        if 0.62 < ring < 0.78 or (a < 0.12 and b < 0.25) or (abs(a - b) < 0.06 and ring < 0.6):
            lvl += 0.9
        lvl -= max(0, 1 - (y - 16) / 10) * 1.2               # ombra de la cornisa
        return lvl


    cv.rect(0, 16, W - 1, 106, GREEN, damask)

    # Sòcol de fusta (arrimador) amb plafons en relleu
    cv.hline(0, W - 1, 107, WALNUT, 4.6)
    cv.hline(0, W - 1, 108, WALNUT, 3.8)
    cv.rect(0, 109, W - 1, 110, WALNUT, 3.0)
    cv.hline(0, W - 1, 111, WALNUT, 0.6)


    def wainscot(x, y):
        px = x % 44
        grain = (hr(x // 2, 9) - 0.5) * 0.35
        lvl = 2.3 + grain
        if 6 <= px <= 39 and 116 <= y <= 141:
            if px == 6 or y == 116:
                return 0.9                                     # ombra del marc
            if px == 39 or y == 141:
                return 3.8                                     # cantell il·luminat
            if px in (7, 8) or y in (117, 118):
                return 3.6                                     # bisell superior
            if px in (37, 38) or y in (139, 140):
                return 1.4
            return 2.7 + grain
        if px == 0:
            return 1.2
        return lvl


    cv.rect(0, 112, W - 1, 145, WALNUT, wainscot)
    cv.hline(0, W - 1, 146, WALNUT, 3.6)
    cv.rect(0, 147, W - 1, 152, WALNUT, 1.6)
    cv.hline(0, W - 1, 153, WALNUT, 0.3)


    # ─── Terra de taulons encerats ────────────────────────────────────────────
    VPX, VPY = 240, -150
    for y in range(FLOOR_Y, H):
        dep = y - VPY
        pw = dep / 30
        for x in range(W):
            u = (x - VPX) / dep * 30
            pl = math.floor(u)
            fr = (u - pl) * pw
            r = hr(pl, 3)
            t = 3600 / dep
            seg = math.floor(t / 1.15 + r * 5)
            seg_up = math.floor(3600 / (dep - 1) / 1.15 + r * 5)
            lvl = 2.4 + (hr(pl, seg) - 0.5) * 0.8 + (0.35 if 1 <= fr < 2 else 0) + (0.25 if hr(pl, seg, int(fr)) > 0.8 else 0)
            if fr < 1:
                lvl = 0.7
            elif seg != seg_up:
                lvl = 0.9
            if y < 161:
                lvl -= (161 - y) / 7 * 1.1                    # ombra de contacte amb la paret
            lvl += moon(x, y) * 1.4
            cv.put(x, y, FLOOR, lvl)

    # Catifa
    RUG_T, RUG_B = 168, 199


    def rug_x(y):
        t = (y - RUG_T) / (RUG_B - RUG_T)
        return 146 - t * 22, 326 + t * 22


    for y in range(RUG_T, RUG_B + 1):
        xl, xr = rug_x(y)
        t = (y - RUG_T) / (RUG_B - RUG_T)
        for x in range(math.ceil(xl), math.floor(xr) + 1):
            s = (x - xl) / (xr - xl)
            m = moon(x, y) * 1.0
            sx, ty = min(s, 1 - s) * 14, min(t, 1 - t) * 4.2
            bd = min(sx, ty)
            if bd < 0.25:
                cv.put(x, y, RED, 1.2 + m)
            elif bd < 0.55:
                cv.put(x, y, GOLD, 2.4 + m)
            elif bd < 1.25:
                # sanefa: rombes petits
                k = (x + (y * 2)) % 6
                cv.put(x, y, NAVY if k < 3 else RED, (2.2 if k < 3 else 2.6) + m)
            elif bd < 1.5:
                cv.put(x, y, GOLD, 2.0 + m)
            else:
                md = abs(s - 0.5) * 2.6 + abs(t - 0.5) * 2.0
                if md < 0.35:
                    cv.put(x, y, NAVY, 2.6 + m)
                elif md < 0.45:
                    cv.put(x, y, GOLD, 2.8 + m)
                elif md < 0.6:
                    cv.put(x, y, RED, 3.4 + m)
                else:
                    pat = ((x // 3) + (y // 2)) % 5 == 0
                    cv.put(x, y, RED, (3.0 if pat else 2.5) + m)
    for x in range(124, 350, 2):                               # serrell
        cv.put(x, RUG_B + 1, PAPER, 2.0)
        cv.put(x + 1, RUG_B + 2, PAPER, 1.6)


    # ─── Porta del magatzem (6..58 × 65..156) ─────────────────────────────────
    cv.rect(8, 64, 58, 153, WALNUT, lambda x, y: 3.0 + (0.8 if x in (9, 10) else 0) - (1.4 if x in (56, 57) else 0))
    cv.hline(7, 59, 63, WALNUT, 4.2)
    cv.hline(7, 59, 64, WALNUT, 3.6)
    cv.rect(14, 70, 52, 153, WALNUT, 0.6)                         # obertura


    def door(x, y):
        g = (hr(x // 3, 77) - 0.5) * 0.3
        if 18 <= x <= 48 and 76 <= y <= 106:                   # vidre glaçat
            return None
        if 18 <= x <= 48 and 114 <= y <= 146:
            if x == 18 or y == 114:
                return 1.0
            if x == 48 or y == 146:
                return 3.6
            if x in (19, 20) or y in (115, 116):
                return 3.4
            return 2.6 + g
        return 2.2 + g + (0.6 if x == 15 else 0) - (0.8 if x == 51 else 0)


    for y in range(71, 154):
        for x in range(15, 52):
            v = door(x, y)
            if v is None:
                # vidre glaçat amb la llum groguenca del magatzem
                gv = 2.0 + (y - 76) / 30 * 1.0 + (hr(x // 2, y // 2) - 0.5) * 0.5 - abs(x - 33) / 30
                cv.put(x, y, GLASS, gv, 0.4)
            else:
                cv.put(x, y, WALNUT, v)
    cv.rect(17, 75, 49, 75, WALNUT, 1.0)
    cv.rect(17, 107, 49, 108, WALNUT, 3.6)
    cv.vline(17, 75, 108, WALNUT, 1.0)
    cv.vline(49, 75, 108, WALNUT, 3.4)
    # lletres al revés al vidre («DIRECCIÓ» vist des de dins)
    for x in range(22, 45):                                    # lletres daurades vistes del revés
        if (x - 22) % 4 != 3:
            cv.put(x, 84, GOLD, 2.2, 0.3)
            if (x * 7) % 3:
                cv.put(x, 85, GOLD, 1.6, 0.3)
    cv.glow(33, 92, 22, (240, 200, 120), 0.18)
    # pom i placa de llautó
    cv.rect(44, 120, 47, 131, GOLD, 2.8)
    cv.vline(44, 120, 131, GOLD, 4.0)
    cv.disc(45.5, 123.5, 2.2, 2.2, GOLD, lambda nx, ny: 4.5 - nx - ny * 1.2)
    cv.put(45, 128, GOLD, 0.2)
    cv.put(45, 129, GOLD, 0.2)

    # Canonada de coure amb manòmetre (entre la porta i la finestra)
    for y in range(16, 154):
        for x in range(63, 68):
            cv.put(x, y, COPPER, [2.0, 3.6, 3.0, 2.2, 1.0][x - 63])
        if y % 34 == 0:
            cv.rect(62, y, 68, y + 2, COPPER, 2.0)
            cv.hline(62, 68, y, COPPER, 3.6)
    cv.disc(65, 126, 4.6, 4.6, GOLD, lambda nx, ny: 3.2 - nx - ny)
    cv.disc(65, 126, 3.4, 3.4, PAPER, lambda nx, ny: 4.0 - ny * 0.6)
    for a in range(0, 360, 45):
        pass
    for i in range(4):
        cv.flat(65 + i // 2, 126 - i // 2, (170, 30, 30))
    cv.flat(65, 126, (40, 30, 30))


    # ─── Finestra (79..167 × 19..107) amb cortines ────────────────────────────
    GX0, GY0, GX1, GY1 = 85, 25, 161, 99
    cv.rect(79, 19, 167, 106, WALNUT, lambda x, y: 2.8 + (0.9 if y < 22 or x < 82 else 0) - (1.2 if x > 164 else 0))
    cv.rect(83, 23, 163, 101, WALNUT, 0.8)

    stars = random.Random(5)
    STARS = {(stars.randint(GX0, GX1), stars.randint(GY0, 66)) for _ in range(40)}

    # perfil de la ciutat-fàbrica
    sky_rnd = random.Random(11)
    skyline = [99] * (GX1 + 2)
    buildings = [(85, 98, 80), (97, 112, 74), (110, 126, 84), (124, 141, 70), (140, 152, 78), (151, 162, 72)]
    for bx0, bx1, top in buildings:
        for x in range(bx0, bx1 + 1):
            skyline[x] = min(skyline[x], top)
    for x in range(110, 126):                                  # teulada de dents de serra
        skyline[x] = min(skyline[x], 84 - ((x - 110) % 8))
    CHIMNEYS = [(101, 4, 44), (131, 5, 36), (145, 3, 52), (156, 4, 47)]
    for cx, cw, top in CHIMNEYS:
        for x in range(cx, cx + cw):
            skyline[x] = min(skyline[x], top)
    WINDOWS = set()
    for bx0, bx1, top in buildings:
        for x in range(bx0 + 2, bx1 - 1, 3):
            for y in range(top + 4, 97, 4):
                if sky_rnd.random() < 0.28:
                    WINDOWS.add((x, y))


    PUFFS = []
    for ci, (cx, cw, top) in enumerate(CHIMNEYS):
        pr = random.Random(cx)
        col = [(cx + cw / 2 - k * 3.2 + pr.uniform(-1, 1), top - 2 - k * 3.6, 1.6 + k * 1.1, 1 - k / 7) for k in range(7)]
        PUFFS += drift(col, (tt * (1, 1, 2, 1)[ci] + (0, 0.35, 0.2, 0.7)[ci]) % 1)   # el fum puja i s'escampa


    def smoke(x, y):
        v = 0.0
        for px_, py_, r, a in PUFFS:
            d = math.hypot(x - px_, (y - py_) * 1.2) / r
            if d < 1:
                v = max(v, a * (1 - d * d) * 0.9)
        return v


    MOON = (102, 40)
    for y in range(GY0, GY1 + 1):
        for x in range(GX0, GX1 + 1):
            if y >= skyline[x]:
                lvl = 1.2 + (0.0 if y > skyline[x] else 2.6)  # vora encesa pel foc dels forns
                if y == skyline[x]:                            # (que respira, a cada edifici al seu ritme)
                    fi = hr(x // 6, 41) * 6.283
                    lvl += 0.7 * (math.sin(ph * (1 + (x // 6) % 3) + fi) - math.sin(fi))
                if (x, y) in WINDOWS or (x + 1, y) in WINDOWS:
                    cv.flat(x, y, (236, 170, 80) if hr(x, y) > 0.3 else (190, 110, 50))
                else:
                    cv.put(x, y, SIL, lvl, 0)
                continue
            t = (y - GY0) / (GY1 - GY0)
            lvl = 0.6 + min(1, (y - GY0) / 60) ** 2.4 * 8.6
            dm = math.hypot(x - MOON[0], y - MOON[1])
            if dm < 22:
                lvl += (1 - dm / 22) ** 2 * 2.2
            cv.put(x, y, SKY, lvl, 0)
            s = smoke(x, y)
            if s > 0:
                cv.put(x, y, SMOKE, s * 3.6 + 0.4, 0) if s > B4[y & 3][x & 3] * 0.7 else None
            if (x, y) in STARS and dm > 9:
                si = 2 if hr(x, y, 1) > 0.5 else 1
                if hr(x, y, 2) > 0.45:                         # n'hi ha que titil·len
                    fi = hr(x, y, 3) * 6.283
                    si += round(1.2 * (math.sin(ph * (1 + int(hr(x, y, 4) * 3)) + fi) - math.sin(fi)))
                si = max(0, min(3, si))
                if si:
                    cv.flat(x, y, ((0, 0, 0), (140, 140, 190), (200, 200, 230), (244, 244, 255))[si])
    cv.disc(MOON[0], MOON[1], 5.5, 5.5, PAPER, lambda nx, ny: 5.6 - nx * 1.2 - ny * 0.6, 0)
    cv.put(100, 38, PAPER, 3.6, 0); cv.put(104, 42, PAPER, 3.6, 0); cv.put(103, 37, PAPER, 4.0, 0)
    # travessers
    for x in (122, 123):
        cv.vline(x, GY0, GY1, WALNUT, 2.2 if x == 122 else 1.2)
    for y in (49, 50, 74, 75):
        cv.hline(GX0, GX1, y, WALNUT, 2.4 if y in (49, 74) else 1.2)
    # reflex al vidre
    for i in range(10):
        cv.put(90 + i, 60 - i, PAPER, 1.4, 0)
        cv.put(128 + i, 96 - i, PAPER, 1.0, 0)
    # ampit
    cv.rect(76, 101, 170, 105, WALNUT, lambda x, y: [4.6, 3.8, 3.2, 2.6, 1.2][y - 101])
    cv.hline(78, 168, 106, WALNUT, 0.2)


    def curtain(x0, x1, tie_side):
        for y in range(14, 113):
            for x in range(x0, x1 + 1):
                u = (x - x0) / (x1 - x0)
                fold = math.sin(u * math.pi * 3.2 + (0.6 if tie_side else 0)) * 0.9
                lvl = 2.6 + fold - (y - 14) / 140
                cv.put(x, y, RED, lvl)


    curtain(69, 87, False)
    curtain(159, 177, True)
    # galeria de la cortina
    cv.rect(68, 10, 178, 17, RED, lambda x, y: 3.4 - (y - 10) * 0.25 + math.sin(x / 3.0) * 0.5)
    for x in range(68, 179, 5):                               # serrell de borles
        cv.vline(x, 18, 20, GOLD, 3.2)
        cv.put(x, 21, GOLD, 4.0)
    cv.hline(68, 178, 17, GOLD, 3.0)
    cv.rect(70, 8, 176, 9, GOLD, 3.4)
    cv.disc(70, 8.5, 2, 2, GOLD, 4.2); cv.disc(176, 8.5, 2, 2, GOLD, 4.2)
    # lligacortines
    for cx in (78, 168):
        cv.rect(cx - 9, 72, cx + 9, 74, GOLD, lambda x, y: 3.6 - (y - 72) * 0.8)
        cv.disc(cx, 76, 1.6, 2, GOLD, 3.0)

    # Radiador de ferro colat sota la finestra
    for x in range(92, 157):
        for y in range(122, 150):
            k = (x - 92) % 6
            if k in (4, 5):
                cv.put(x, y, IRON, 0.6)
            else:
                lvl = [2.4, 3.4, 3.0, 2.2][k] - (0.6 if y > 146 else 0)
                if y in (122, 123) or y in (134, 135):
                    lvl += 0.8
                cv.put(x, y, IRON, lvl)
    cv.rect(90, 148, 158, 150, IRON, 1.6)
    cv.rect(152, 150, 155, 153, IRON, 2.2)
    cv.rect(152, 152, 158, 153, IRON, 1.4)


    # ─── Retrat del director Aldaia (204..260 × 27..91) ───────────────────────
    FX0, FY0, FX1, FY1 = 204, 27, 260, 91
    for y in range(FY0, FY1 + 1):
        for x in range(FX0, FX1 + 1):
            d = min(x - FX0, FX1 - x, y - FY0, FY1 - y)
            if d > 5:
                continue
            lit_side = (x - FX0) < (FX1 - x) and (y - FY0) < (FY1 - y) * 3
            base = [1.6, 3.0, 4.4, 3.4, 2.4, 0.8][d]
            if d == 2 and (x + y) % 3 == 0:
                base -= 0.9                                    # talla
            if d in (1, 2, 3) and not lit_side and (x - FX0) > (FX1 - x):
                base -= 0.7
            if d in (1, 2, 3) and (y - FY0) > (FY1 - y):
                base -= 0.5
            cv.put(x, y, GOLD, base)
    for cx, cy in ((FX0 + 2, FY0 + 2), (FX1 - 2, FY0 + 2), (FX0 + 2, FY1 - 2), (FX1 - 2, FY1 - 2)):
        cv.disc(cx, cy, 3, 3, GOLD, lambda nx, ny: 4.8 - nx - ny)
        cv.put(cx, cy, GOLD, 1.0)
    cv.disc((FX0 + FX1) / 2, FY0 + 1, 5, 3, GOLD, lambda nx, ny: 4.6 - nx * 0.6 - ny)

    CX0, CY0, CX1, CY1 = FX0 + 6, FY0 + 6, FX1 - 6, FY1 - 6  # tela 210..254 × 33..85
    HCX, HCY = 232, 53


    def canvas_bg(x, y):
        d = math.hypot(x - 224, y - 44) / 40
        return 3.0 - d * 2.4 + (hr(x // 2, y // 2, 4) - 0.5) * 0.4


    for y in range(CY0, CY1 + 1):
        for x in range(CX0, CX1 + 1):
            cv.put(x, y, SIL, canvas_bg(x, y) + 0.8, 0.5)

    # espatlles i americana
    for y in range(64, CY1 + 1):
        half = 9 + (y - 64) * 1.0
        half = min(half, 22)
        for x in range(CX0, CX1 + 1):
            dx = x - HCX
            if abs(dx) <= half:
                lvl = 2.0 - dx / 22 * 1.2 - (y - 64) / 40
                if abs(dx) > half - 1:
                    lvl += 0.8
                cv.put(x, y, SUIT, lvl, 0.6)
    # solapes
    for y in range(66, CY1 + 1):
        w = (y - 66) // 2
        for s in (-1, 1):
            xx = HCX + s * (3 + w // 2)
            cv.put(xx, y, SUIT, 3.4 if s < 0 else 1.0, 0.6)
    # coll alt i corbata
    for y in range(63, 70):
        for x in range(HCX - 5, HCX + 6):
            if abs(x - HCX) <= 5 - (y - 63) // 2:
                cv.put(x, y, PAPER, 4.2 - (x - HCX) * 0.25, 0.5)
    for y in range(66, 79):
        w = 1 if y < 70 else 2 - (y - 70) // 5
        for x in range(HCX - w, HCX + w + 1):
            cv.put(x, y, RED, 2.6 - (x - HCX) * 0.5, 0.5)
    # insígnia de ferro-9
    cv.disc(HCX - 9, 74, 1.4, 1.4, CYAN, 3.4, 0)
    # coll (pell) i cap
    cv.rect(HCX - 3, 59, HCX + 3, 63, SKIN, lambda x, y: 2.0 - (x - HCX) * 0.3, 0.5)
    cv.disc(HCX, HCY, 8.5, 10.5, SKIN, lambda nx, ny: 3.6 - nx * 1.3 - ny * 0.5 - (nx * nx + ny * ny) * 0.6, 0.5)
    # orelles
    cv.disc(HCX - 9, 54, 1.4, 2.5, SKIN, 2.8, 0.5)
    cv.disc(HCX + 9, 54, 1.4, 2.5, SKIN, 1.6, 0.5)
    # cabells grisos, entrades i patilles
    for y in range(41, 50):
        for x in range(HCX - 9, HCX + 10):
            nx, ny = (x - HCX) / 9, (y - 51) / 10.5
            if nx * nx + ny * ny <= 1.02:
                bald = abs(x - HCX) < 5 - (y - 41) * 0.6 and y > 43
                if not bald:
                    cv.put(x, y, GRAY, 3.6 - (x - HCX) / 6 - (hr(x, y, 8) * 0.8), 0.5)
    for s in (-1, 1):
        for y in range(48, 58):
            cv.put(HCX + s * 8, y, GRAY, 3.0 if s < 0 else 1.8, 0.5)
            if y < 55:
                cv.put(HCX + s * 9, y, GRAY, 2.6 if s < 0 else 1.4, 0.5)
    # celles severes, ulls, nas, bigoti
    for i in range(4):
        cv.put(HCX - 6 + i, 50 + (1 if i == 0 else 0), GRAY, 1.0, 0)
        cv.put(HCX + 2 + i, 50 + (1 if i == 3 else 0), GRAY, 0.6, 0)
    for ex in (HCX - 4, HCX + 3):
        cv.put(ex, 52, SUIT, 0.0, 0)
        cv.put(ex + 1, 52, SUIT, 0.0, 0)
        cv.put(ex - 1, 53, SKIN, 1.6, 0)
        cv.put(ex + 2, 53, SKIN, 1.6, 0)
    cv.put(HCX - 4, 52, PAPER, 2.0, 0)
    cv.vline(HCX + 1, 53, 57, SKIN, 1.6, 0)
    cv.put(HCX, 57, SKIN, 1.4, 0)
    cv.put(HCX - 1, 56, SKIN, 4.4, 0)
    for i, x in enumerate(range(HCX - 6, HCX + 7)):
        d = abs(x - HCX)
        cv.put(x, 59 + d // 4, GRAY, 3.2 - (x - HCX) / 5, 0.5)
        if d < 5:
            cv.put(x, 60 + d // 4, GRAY, 2.4 - (x - HCX) / 5, 0.5)
    cv.hline(HCX - 2, HCX + 2, 62, SKIN, 1.0, 0)
    # placa amb el nom
    cv.rect(224, 88, 240, 90, GOLD, lambda x, y: 4.2 - (y - 88) * 0.8)
    for x in range(226, 239, 2):
        cv.put(x, 89, GOLD, 1.4)
    # llum de quadre de llautó
    cv.rect(222, 22, 242, 25, GOLD, lambda x, y: 4.4 - (y - 22) * 0.9)
    cv.vline(232, 18, 21, GOLD, 3.0)
    cv.hline(224, 240, 26, PAPER, 6)
    cv.glow(232, 30, 30, (255, 220, 150), 0.22)


    # ─── Plànol d'una màquina, emmarcat (sobre l'escriptori) ──────────────────
    BX0, BY0, BX1, BY1 = 284, 36, 352, 82
    cv.rect(BX0, BY0, BX1, BY1, WALNUT, lambda x, y: 1.2 if (x in (BX1, BX1 - 1) or y in (BY1, BY1 - 1)) else 2.8)
    cv.rect(BX0 + 3, BY0 + 3, BX1 - 3, BY1 - 3, BLUEP, lambda x, y: 2.0 + (0.4 if (x % 6 == 0 or y % 6 == 0) else 0) + (hr(x, y, 2) - 0.5) * 0.5, 0.6)


    def bp(x, y, lvl=5.0):
        cv.put(x, y, BLUEP, lvl, 0.3)


    def bp_circle(cx, cy, r, teeth=0):
        for a in range(0, 360, 4):
            rr = r + (1 if teeth and (a // (360 // teeth // 2 * 2 // 2 or 1)) % 2 else 0)
            bp(round(cx + math.cos(math.radians(a)) * rr), round(cy + math.sin(math.radians(a)) * rr))


    bp_circle(304, 56, 11, teeth=12)
    bp_circle(304, 56, 4)
    bp_circle(328, 64, 7, teeth=8)
    bp_circle(328, 64, 2)
    for x in range(316, 346):
        bp(x, 46)
    for y in range(46, 76):
        bp(345, y, 4.6)
    for x in range(292, 318, 2):
        bp(x, 74, 4.4)
    for i in range(6):
        bp(332 + i * 2, 42, 4.4)
    bp(292, 42); bp(293, 42); bp(294, 42); bp(296, 42); bp(297, 42)
    cv.put(BX0 + 4, BY0 + 4, GOLD, 4.0); cv.put(BX1 - 4, BY0 + 4, GOLD, 4.0)


    # ─── Escriptori ───────────────────────────────────────────────────────────
    DX0, DX1 = 266, 368
    TOP_BACK, TOP_FRONT = 113, 121
    # ombra al terra
    for y in range(FLOOR_Y, 163):
        for x in range(DX0 - 4, DX1 + 6):
            a = (1 - (y - FLOOR_Y) / 9) * (1 - max(0, abs(x - 317) - 44) / 12)
            if a > B4[y & 3][x & 3]:
                o = cv.P[x, y]
                cv.P[x, y] = tuple(int(c * 0.55) for c in o[:3]) + (255,)
    # cos: pedestals i calaix central (calaix: 283..344 × 131..148)
    cv.rect(DX0 + 2, 126, DX1 - 2, 153, WALNUT, lambda x, y: 2.4 + (hr(x // 2, 31) - 0.5) * 0.3)
    cv.rect(DX0 + 2, 150, DX1 - 2, 153, WALNUT, 1.0)                # sòcol
    cv.vline(DX0 + 2, 126, 153, WALNUT, 3.4)
    cv.vline(DX1 - 2, 126, 153, WALNUT, 1.0)


    def drawer(x0, y0, x1, y1, handle=True):
        cv.rect(x0, y0, x1, y1, WALNUT, lambda x, y: 2.9 + (hr(x // 2, y0) - 0.5) * 0.3)
        cv.hline(x0, x1, y0, WALNUT, 4.2)
        cv.vline(x0, y0, y1, WALNUT, 3.8)
        cv.hline(x0, x1, y1, WALNUT, 0.6)
        cv.vline(x1, y0, y1, WALNUT, 1.0)
        if handle:
            cx = (x0 + x1) // 2
            cv.rect(cx - 3, (y0 + y1) // 2, cx + 3, (y0 + y1) // 2 + 1, GOLD, lambda x, y: 4.0 - (y - (y0 + y1) // 2) * 1.6)


    for y0, y1 in ((129, 138), (140, 148)):
        drawer(270, y0, 281, y1)
        drawer(347, y0, 364, y1)
    # calaix central amb el pany M-3
    drawer(285, 131, 343, 147, handle=False)
    cv.rect(310, 135, 318, 143, IRON, lambda x, y: 3.0 - (x - 310) * 0.2 - (y - 135) * 0.15)
    cv.disc(314, 139, 2.6, 2.6, CYAN, lambda nx, ny: 3.4 - nx - ny, 0)
    cv.put(313, 138, CYAN, 5, 0)
    cv.glow(314, 139, 14, (100, 200, 255), 0.55)
    # tauler: gruix frontal i superfície amb pell verda
    cv.rect(DX0, 121, DX1, 125, WALNUT, lambda x, y: [4.8, 4.0, 3.4, 3.0, 1.0][y - 121])
    for y in range(TOP_BACK, TOP_FRONT):
        t = (y - TOP_BACK) / (TOP_FRONT - TOP_BACK)
        xl, xr = DX0 + 4 - t * 4, DX1 - 4 + t * 4
        for x in range(round(xl), round(xr) + 1):
            inl = xl + 8 < x < xr - 8 and TOP_BACK + 1 < y < TOP_FRONT - 1
            cv.put(x, y, LAMPG if inl else WALNUT, (1.4 if inl else 3.6) + t * 0.6)
    cv.hline(DX0 + 4, DX1 - 4, TOP_BACK, WALNUT, 2.2)
    # potes torneades visibles als costats
    for x in (DX0 + 1, DX1 - 1):
        cv.vline(x, 126, 153, WALNUT, 1.6)

    # expedient del Sic (zona 289..339 × 106..122): carpeta de cartolina amb papers i cinta vermella
    for y in range(112, 121):
        t = (y - 112) / 8
        xl, xr = 294 - t * 3, 332 - t * 1
        for x in range(round(xl), round(xr) + 1):
            cv.put(x, y, MANILA, 3.2 + t * 0.4 - (0.8 if x > xr - 1 else 0))
    for y in range(110, 117):                                   # fulls que sobresurten
        for x in range(298 - (y - 110) // 3, 326):
            if y < 112 or (x > 322):
                cv.put(x, y, PAPER, 4.0 - (y - 110) * 0.15)
    cv.hline(296, 324, 109, PAPER, 3.0)
    cv.hline(291, 333, 121, MANILA, 1.2)
    for y in range(112, 122):                                   # cinta
        cv.put(310, y, RED, 3.4)
        cv.put(311, y, RED, 2.4)
    for x in range(292, 332):
        if x % 2:
            cv.put(x, 116, RED, 3.0) if 306 < x < 316 else None
    cv.rect(296, 113, 304, 115, RED, 3.2)                          # segell «confidencial»
    cv.put(298, 114, MANILA, 4.4); cv.put(300, 114, MANILA, 4.4); cv.put(302, 114, MANILA, 4.4)

    # tinter i ploma
    cv.disc(280, 115, 3, 2.4, IRON, lambda nx, ny: 2.4 - nx - ny)
    cv.put(279, 114, PAPER, 4.0, 0)
    for i in range(8):
        cv.put(281 + i // 2, 113 - i, PAPER, 3.4 - i * 0.1)
        cv.put(282 + i // 2, 113 - i, PAPER, 2.4)

    # làmpada de banquer
    cv.disc(349, 118.5, 7, 2.2, GOLD, lambda nx, ny: 3.8 - nx - ny)
    cv.vline(349, 104, 116, GOLD, 4.0)
    cv.vline(350, 104, 116, GOLD, 2.4)
    for y in range(96, 104):
        t = (y - 96) / 7
        half = 10 + t * 4
        for x in range(round(349 - half), round(349 + half) + 1):
            u = (x - 349) / half
            cv.put(x, y, LAMPG, 3.2 - u * 1.6 - (1 - t) * 0.6 + (1.6 if y == 96 + 1 and u < 0 else 0), 0.3)
    cv.hline(335, 363, 104, [(255, 236, 170)], 0, 0)
    cv.hline(336, 362, 105, GOLD, 5.0, 0)
    cv.glow(349, 108, 34, (255, 226, 150), 0.45)


    # ─── Faristol amb el llibre d'inventari (392..437 × 106..135) ─────────────
    # peu
    cv.disc(414, 168, 16, 3, WALNUT, lambda nx, ny: 1.8 - ny, 0.8)
    for y in range(166, 171):                                   # ombra
        pass
    cv.rect(410, 130, 418, 166, WALNUT, lambda x, y: [3.8, 3.4, 3.0, 2.6, 2.2, 1.8, 1.4, 1.0, 0.8][x - 410])
    cv.rect(408, 150, 420, 152, WALNUT, 3.0)
    # tauler inclinat
    for y in range(108, 131):
        t = (y - 108) / 22
        xl, xr = 395 - t * 5, 435 + t * 5
        for x in range(round(xl), round(xr) + 1):
            cv.put(x, y, WALNUT, 2.6 + t * 0.8)
    cv.rect(389, 131, 441, 133, WALNUT, lambda x, y: [4.0, 2.8, 1.0][y - 131])
    # llibre obert: tapes vermelles i pàgines
    for y in range(108, 129):
        t = (y - 108) / 20
        xl, xr = 396 - t * 4, 434 + t * 4
        for x in range(round(xl), round(xr) + 1):
            cv.put(x, y, RED, 2.4 + t * 0.4)
    for y in range(107, 128):
        t = (y - 107) / 20
        xl, xr = 398 - t * 4, 432 + t * 4
        mid = 415
        for x in range(round(xl), round(xr) + 1):
            s = (x - mid) / ((xr - xl) / 2)
            curve = -abs(s) ** 0.5 * 0.3
            lvl = 4.4 + curve - (1.4 if abs(x - mid) < 1.5 else 0) - (0.6 if abs(x - mid) < 3 else 0)
            yy = y - round((1 - abs(s)) * 1.5)
            cv.put(x, yy, PAPER, lvl)
    # ratlles i anotacions de comptabilitat
    for row in range(4):
        y = 111 + row * 4
        for x in range(400 - row, 431 + row):
            if abs(x - 415) > 2:
                if hr(x // 3, row) > 0.3 and x % 3:
                    cv.put(x, y, PAPER, 2.2)
    # cinta del punt de llibre
    for y in range(127, 140):
        cv.put(416 + (y - 127) // 6, y, RED, 3.6 - (y - 127) * 0.05)


    # ─── Prestatgeria (dreta) ─────────────────────────────────────────────────
    SX0, SX1 = 446, 479
    cv.rect(SX0 - 2, 26, SX1, 153, WALNUT, 1.0)
    cv.rect(SX0 - 3, 22, SX1, 26, WALNUT, lambda x, y: 3.8 - (y - 22) * 0.6)
    cv.vline(SX0 - 2, 26, 153, WALNUT, 3.0)
    cv.vline(SX0 - 1, 26, 153, WALNUT, 2.2)
    shelves = [52, 80, 108, 136]
    top = 28
    book_rnd = random.Random(21)
    BOOK_RAMPS = [RED, LAMPG, NAVY, MANILA, WALNUT, COPPER]
    for sy in shelves:
        cv.rect(SX0, top, SX1, sy - 1, WALNUT, 0.4)
        x = SX0 + 1
        while x < SX1:
            bw = book_rnd.randint(2, 4)
            bh = book_rnd.randint(14, sy - top - 3)
            ramp = book_rnd.choice(BOOK_RAMPS)
            base = book_rnd.uniform(1.6, 2.8) + (1.0 if ramp in (NAVY,) else 0)
            if book_rnd.random() < 0.1 and x + 8 < SX1:
                x += 3
                continue
            for bx in range(x, min(SX1, x + bw)):
                for by in range(sy - bh, sy):
                    lvl = base + (0.8 if bx == x else 0) - (0.8 if bx == x + bw - 1 else 0)
                    if by in (sy - bh + 2, sy - 4):
                        cv.put(bx, by, GOLD, 3.4)
                    else:
                        cv.put(bx, by, ramp, lvl)
            x += bw
        cv.rect(SX0 - 1, sy, SX1, sy + 2, WALNUT, lambda x, y: [3.8, 2.8, 1.2][y - sy])
        top = sy + 3
    cv.rect(SX0, 139, SX1, 153, WALNUT, lambda x, y: 2.2 if y > 141 else 1.0)


    # ─── Retocs finals: tint fred de la lluna ─────────────────────────────────
    cv.tint(0, 150, W - 1, 205, (150, 170, 230), lambda x, y: 0.22 * moon(x, y))
    # pols que sura dins el raig de la lluna, de la finestra al terra
    dust(cv, tt, 20, 7, (96, 104, 200, 176), (206, 216, 248), 0.75, moon_beam)


PROPS = {}

ANIMS = {'ambient': {'frames': lambda: ambient_frames(bg, LIGHT, 24, box=(80, 20, 250, 205)), 'frameDuration': 130}}
