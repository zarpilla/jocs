"""
Despatx del director (Acte 2, Iri) a 640×360: la composició de hd/rooms/fabrica_despatx.py ×4/3, dibuixada de nou.
Fusta, paper pintat verd, la nit de la ciutat-fàbrica a la finestra.
Llums: làmpada de banquer a l'escriptori, llum de llautó sobre el retrat, lluna (taca freda al terra).
Animació: `ambient` (el fum de les xemeneies, les estrelles que titil·len, els forns que respiren i la pols al raig
de la lluna). Els fotogrames només redibuixen la finestra i la pols damunt el fons quiet.

També hi ha `dust` i `ambient_frames`, que fan servir el magatzem i el moll.
"""
import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)

import math
import random
from functools import lru_cache

from PIL import Image, ImageChops

from hd640.rooms.fabrica_calderes_pla_comu import drift

from hd.pix import (Canvas, Light, B4, W, H, hr, mix, WALNUT, GREEN, FLOOR, GOLD, RED, NAVY, SKIN, GRAY, SUIT, PAPER,
                    MANILA, SKY, SIL, IRON, BLUEP, CYAN, LAMPG, COPPER, SMOKE, GLASS)

LIGHT = Light(vignette=(107, 61), floor_fade=(261, 48))
LIGHT.point(465, 139, r=213, k=2.7, squash=1.15, down=True)          # làmpada de banquer
LIGHT.add(lambda x, y: max(0.0, 1 - math.hypot(x - 309, (y - 45) * 0.75) / 64) ** 1.5 * 1.5 if y >= 40 else 0.0)  # llum del retrat

FLOOR_Y = 205
GX0, GY0, GX1, GY1 = 113, 33, 215, 132          # el vidre de la finestra
MOON = (136, 53)


def moon(x, y):
    """Taca de lluna al terra (amb l'ombra dels travessers de la finestra)."""
    if not 216 <= y <= 264:
        return 0.0
    t = (y - 216) / 48
    xl, xr = 144 + t * 59, 224 + t * 93
    if not xl <= x <= xr:
        return 0.0
    s = (x - xl) / (xr - xl)
    if abs(t - 0.33) < 0.035 or abs(t - 0.66) < 0.035:
        return 0.0
    if abs(s - 0.5) < 0.02:                                    # el muntant del mig
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
    s = (y - 133) / 107
    if not 0 <= s <= 1.1:
        return 0.0
    cx, half = 165 + s * 61, 45 + s * 13
    e = 1 - abs(x - cx) / half
    return max(0.0, min(1.0, e * 2.5)) * min(1.0, s * 6)


# ─── La sala ────────────────────────────────────────────────────────────────

def walls(cv):
    """Sostre, cornisa, paper pintat i arrimador."""
    cv.rect(0, 0, W - 1, 12, WALNUT, lambda x, y: 0.6 + (hr(x // 40) - 0.5) * 0.3 + (hr(x, y // 3, 2) - 0.5) * 0.12)
    for x in range(0, W, 40):                                  # bigues del sostre
        cv.vline(x, 0, 12, WALNUT, 0.0)
        cv.vline(x + 1, 0, 12, WALNUT, 1.2)
    cv.hline(0, W - 1, 13, WALNUT, 3.2)
    cv.hline(0, W - 1, 14, WALNUT, 2.0)
    cv.rect(0, 15, W - 1, 17, WALNUT, 2.6)
    for x in range(0, W, 5):                                   # dentellons
        cv.rect(x, 15, x + 1, 16, WALNUT, 3.4)
        cv.put(x + 1, 17, WALNUT, 1.6)
    cv.hline(0, W - 1, 18, WALNUT, 1.6)
    cv.hline(0, W - 1, 19, WALNUT, 0.4)

    def damask(x, y):
        u, v = x % 27, (y - 21) % 35
        if ((y - 21) // 35) % 2:
            u = (u + 13) % 27
        a = abs(u - 13) / 13
        b = abs(v - 17) / 17
        ring = a * 1.3 + b
        lvl = 2.0 + (hr(x // 2, y // 2, 33) - 0.5) * 0.12
        if 0.64 < ring < 0.77 or (a < 0.1 and b < 0.22) or (abs(a - b) < 0.05 and ring < 0.6):
            lvl += 0.9
        elif 0.6 < ring < 0.81:
            lvl += 0.35                                        # vora suau del dibuix
        if abs(x % 27) == 0 and hr(x // 27, y // 9, 34) > 0.85:
            lvl -= 0.4                                         # junta de les tires de paper
        lvl -= max(0, 1 - (y - 21) / 13) * 1.2                 # ombra de la cornisa
        return lvl

    cv.rect(0, 20, W - 1, 141, GREEN, damask)

    # Arrimador de fusta amb plafons en relleu
    cv.hline(0, W - 1, 142, WALNUT, 4.6)
    cv.hline(0, W - 1, 143, WALNUT, 3.8)
    cv.rect(0, 144, W - 1, 146, WALNUT, lambda x, y: 3.0 - (y - 144) * 0.2)
    cv.hline(0, W - 1, 147, WALNUT, 0.6)

    def wainscot(x, y):
        px = x % 59
        grain = (hr(x // 2, 9) - 0.5) * 0.35 + 0.12 * math.sin(y / 6 + hr(x // 59, 3) * 9 + x * 0.05)
        lvl = 2.3 + grain
        if 8 <= px <= 51 and 155 <= y <= 188:
            if px == 8 or y == 155:
                return 0.9                                     # ombra del marc
            if px == 51 or y == 188:
                return 3.8                                     # cantell il·luminat
            if px in (9, 10, 11) or y in (156, 157, 158):
                return 3.6 - (0.3 if px == 11 or y == 158 else 0)   # bisell superior
            if px in (48, 49, 50) or y in (185, 186, 187):
                return 1.4 + (0.3 if px == 48 or y == 185 else 0)
            return 2.7 + grain
        if px == 0:
            return 1.2
        if px == 1:
            return 3.0
        return lvl

    cv.rect(0, 148, W - 1, 193, WALNUT, wainscot)
    cv.hline(0, W - 1, 194, WALNUT, 3.6)
    cv.rect(0, 195, W - 1, 202, WALNUT, lambda x, y: 1.6 + (0.4 if y == 195 else 0) + (hr(x // 3, 11) - 0.5) * 0.2)
    cv.hline(0, W - 1, 203, WALNUT, 0.3)
    cv.hline(0, W - 1, 204, WALNUT, 0.0)


def floor(cv):
    """Terra de taulons encerats i la catifa, amb la taca de la lluna."""
    VPX, VPY = 320, -200
    for y in range(FLOOR_Y, H):
        dep = y - VPY
        pw = dep / 40
        for x in range(W):
            u = (x - VPX) / dep * 40
            pl = math.floor(u)
            fr = (u - pl) * pw
            r = hr(pl, 3)
            t = 4800 / dep
            seg = math.floor(t / 1.15 + r * 5)
            seg_up = math.floor(4800 / (dep - 1) / 1.15 + r * 5)
            lvl = 2.4 + (hr(pl, seg) - 0.5) * 0.8 + (0.35 if 1 <= fr < 2 else 0) + (0.25 if hr(pl, seg, int(fr)) > 0.8 else 0)
            lvl += 0.12 * math.sin(fr * 1.7 + t * 9 + r * 20)              # veta
            if fr < 1:
                lvl = 0.7
            elif seg != seg_up:
                lvl = 0.9
            if y < 215:
                lvl -= (215 - y) / 9 * 1.1                    # ombra de contacte amb la paret
            lvl += moon(x, y) * 1.4
            cv.put(x, y, FLOOR, lvl)

    # Catifa
    RUG_T, RUG_B = 224, 265

    def rug_x(y):
        t = (y - RUG_T) / (RUG_B - RUG_T)
        return 195 - t * 29, 435 + t * 29

    for y in range(RUG_T, RUG_B + 1):
        xl, xr = rug_x(y)
        t = (y - RUG_T) / (RUG_B - RUG_T)
        for x in range(math.ceil(xl), math.floor(xr) + 1):
            s = (x - xl) / (xr - xl)
            m = moon(x, y) * 1.0
            sx, ty = min(s, 1 - s) * 14, min(t, 1 - t) * 4.2
            bd = min(sx, ty)
            wear = -0.3 if hr(x // 3, y // 2, 17) > 0.9 else 0       # el pèl gastat
            if bd < 0.2:
                cv.put(x, y, RED, 1.2 + m)
            elif bd < 0.5:
                cv.put(x, y, GOLD, 2.4 + m + (0.4 if bd < 0.3 else 0))
            elif bd < 1.25:
                # sanefa: rombes petits
                k = (x + (y * 2)) % 8
                cv.put(x, y, NAVY if k < 4 else RED, (2.2 if k < 4 else 2.6) + m + wear)
            elif bd < 1.5:
                cv.put(x, y, GOLD, 2.0 + m)
            else:
                md = abs(s - 0.5) * 2.6 + abs(t - 0.5) * 2.0
                if md < 0.35:
                    cv.put(x, y, NAVY, 2.6 + m + (0.5 if (x + y) % 7 == 0 else 0))
                elif md < 0.45:
                    cv.put(x, y, GOLD, 2.8 + m)
                elif md < 0.6:
                    cv.put(x, y, RED, 3.4 + m)
                else:
                    pat = ((x // 4) + (y // 3)) % 5 == 0
                    cv.put(x, y, RED, (3.0 if pat else 2.5) + m + wear)
    for x in range(165, 467, 2):                               # serrell
        cv.put(x, RUG_B + 1, PAPER, 2.0 + moon(x, RUG_B) * 1.0)
        cv.put(x + 1, RUG_B + 2, PAPER, 1.6)
        if x % 4 == 1:
            cv.put(x, RUG_B + 3, PAPER, 1.2)


def door(cv):
    """Porta del magatzem (11..77 × 85..204), amb el vidre glaçat i les lletres al revés."""
    cv.rect(11, 85, 77, 204, WALNUT, lambda x, y: 3.0 + (0.8 if x in (12, 13) else 0) - (1.4 if x in (75, 76) else 0))
    cv.hline(9, 79, 83, WALNUT, 4.2)
    cv.hline(9, 79, 84, WALNUT, 3.6)
    cv.hline(10, 78, 85, WALNUT, 1.6)
    cv.rect(19, 93, 69, 204, WALNUT, 0.6)                         # obertura

    def leaf(x, y):
        g = (hr(x // 3, 77) - 0.5) * 0.3 + 0.1 * math.sin(y / 5 + x * 0.3)
        if 24 <= x <= 64 and 101 <= y <= 141:                  # vidre glaçat
            return None
        if 24 <= x <= 64 and 152 <= y <= 195:
            if x == 24 or y == 152:
                return 1.0
            if x == 64 or y == 195:
                return 3.6
            if x in (25, 26) or y in (153, 154):
                return 3.4
            if x in (62, 63) or y in (193, 194):
                return 1.8
            if 30 <= x <= 58 and 158 <= y <= 189:              # plafó interior en relleu
                if x == 30 or y == 158:
                    return 3.2
                if x == 58 or y == 189:
                    return 1.6
            return 2.6 + g
        return 2.2 + g + (0.6 if x == 20 else 0) - (0.8 if x == 68 else 0)

    for y in range(95, 205):
        for x in range(20, 69):
            v = leaf(x, y)
            if v is None:
                # vidre glaçat amb la llum groguenca del magatzem
                gv = 2.0 + (y - 101) / 40 * 1.0 + (hr(x // 2, y // 2) - 0.5) * 0.5 + (hr(x, y, 4) - 0.5) * 0.2 - abs(x - 44) / 40
                cv.put(x, y, GLASS, gv, 0.4)
            else:
                cv.put(x, y, WALNUT, v)
    cv.hline(23, 65, 100, WALNUT, 1.0)
    cv.rect(23, 142, 65, 144, WALNUT, lambda x, y: 3.6 - (y - 142) * 0.6)
    cv.vline(23, 100, 144, WALNUT, 1.0)
    cv.vline(65, 100, 144, WALNUT, 3.4)
    # lletres daurades al vidre («DIRECCIÓ» vist des de dins, al revés)
    for x in range(29, 60):
        if (x - 29) % 5 != 4:
            cv.put(x, 112, GOLD, 2.2, 0.3)
            if (x * 7) % 3:
                cv.put(x, 113, GOLD, 1.6, 0.3)
            if (x * 5) % 4 == 1:
                cv.put(x, 114, GOLD, 1.4, 0.3)
    cv.glow(44, 123, 29, (240, 200, 120), 0.18)
    # pom i placa de llautó
    cv.rect(58, 160, 62, 175, GOLD, lambda x, y: 2.8 - (x - 58) * 0.2)
    cv.vline(58, 160, 175, GOLD, 4.0)
    cv.disc(60.5, 164, 3, 3, GOLD, lambda nx, ny: 4.5 - nx - ny * 1.2)
    cv.put(59, 162, GOLD, 5.6)
    cv.vline(60, 170, 172, GOLD, 0.2)
    cv.put(60, 160, GOLD, 4.6); cv.put(60, 175, GOLD, 1.8)       # els cargols de la placa


def pipe(cv):
    """Canonada de coure amb manòmetre (entre la porta i la finestra)."""
    prof = [2.0, 3.0, 3.6, 3.2, 2.6, 1.8, 1.0]
    for y in range(20, 205):
        for x in range(84, 91):
            cv.put(x, y, COPPER, prof[x - 84] + (0.3 if hr(y // 4, 3) > 0.85 and x == 86 else 0))
        if y % 45 == 0:
            cv.rect(83, y, 91, y + 3, COPPER, lambda xx, yy: 2.0 + (1.6 if yy == y else 0) - (xx - 83) * 0.1)
            cv.put(83, y + 1, IRON, 4.0)
    cv.rect(85, 158, 89, 162, COPPER, 2.6)
    cv.disc(87, 168, 6.2, 6.2, GOLD, lambda nx, ny: 3.2 - nx - ny)
    cv.disc(87, 168, 4.6, 4.6, PAPER, lambda nx, ny: 4.0 - ny * 0.6)
    for a in range(-120, 121, 40):
        cv.put(round(87 + math.sin(math.radians(a)) * 3.6), round(168 - math.cos(math.radians(a)) * 3.6), PAPER, 1.6, 0.3)
    for i in range(5):
        cv.flat(87 + i // 2, 168 - i // 2, (170, 30, 30))
    cv.flat(87, 168, (40, 30, 30))
    cv.put(85, 165, PAPER, 6.0, 0)


def window_frame(cv):
    """El marc de la finestra (105..223 × 25..141) i l'ampit."""
    cv.rect(105, 25, 223, 141, WALNUT, lambda x, y: 2.8 + (0.9 if y < 29 or x < 109 else 0) - (1.2 if x > 219 else 0))
    cv.rect(111, 31, 217, 135, WALNUT, 0.8)
    # ampit
    cv.rect(101, 135, 227, 140, WALNUT, lambda x, y: [4.6, 4.2, 3.8, 3.2, 2.6, 1.2][y - 135])
    cv.hline(104, 224, 141, WALNUT, 0.2)


# perfil de la ciutat-fàbrica (fix: no depèn del moment de l'animació)
def _city():
    stars = random.Random(5)
    STARS = {(stars.randint(GX0, GX1), stars.randint(GY0, 88)) for _ in range(53)}
    sky_rnd = random.Random(11)
    skyline = [GY1] * (GX1 + 2)
    buildings = [(113, 131, 107), (129, 149, 99), (147, 168, 112), (165, 188, 93), (187, 203, 104), (201, 216, 96)]
    for bx0, bx1, top in buildings:
        for x in range(bx0, bx1 + 1):
            skyline[x] = min(skyline[x], top)
    for x in range(147, 169):                                  # teulada de dents de serra
        skyline[x] = min(skyline[x], 112 - ((x - 147) % 11))
    CHIMNEYS = [(135, 5, 59), (175, 7, 48), (193, 4, 69), (208, 5, 63)]
    for cx, cw, top in CHIMNEYS:
        for x in range(cx, cx + cw):
            skyline[x] = min(skyline[x], top)
    WINDOWS = set()
    for bx0, bx1, top in buildings:
        for x in range(bx0 + 2, bx1 - 1, 4):
            for y in range(top + 5, 129, 5):
                if sky_rnd.random() < 0.28:
                    WINDOWS.add((x, y))
    return STARS, skyline, CHIMNEYS, WINDOWS


STARS, SKYLINE, CHIMNEYS, WINDOWS = _city()


def window(cv, tt):
    """El vidre de la finestra al moment tt: el cel, la lluna, les estrelles, la ciutat i el fum; i el que hi ha
    al damunt (travessers, reflexos, cortines i galeria)."""
    ph = 2 * math.pi * tt
    PUFFS = []
    for ci, (cx, cw, top) in enumerate(CHIMNEYS):
        pr = random.Random(cx)
        col = [(cx + cw / 2 - k * 4.3 + pr.uniform(-1.3, 1.3), top - 3 - k * 4.8, 2.1 + k * 1.5, 1 - k / 7) for k in range(7)]
        PUFFS.extend(drift(col, (tt * (1, 1, 2, 1)[ci] + (0, 0.35, 0.2, 0.7)[ci]) % 1))   # el fum puja i s'escampa

    def smoke(x, y):
        v = 0.0
        for px_, py_, r, a in PUFFS:
            d = math.hypot(x - px_, (y - py_) * 1.2) / r
            if d < 1:
                v = max(v, a * (1 - d * d) * 0.9)
        return v

    bright = []
    for y in range(GY0, GY1 + 1):
        for x in range(GX0, GX1 + 1):
            sl = SKYLINE[x]
            if y >= sl:
                lvl = 1.2 + (0.0 if y > sl else 2.6)          # vora encesa pel foc dels forns
                if y == sl:                                    # (que respira, a cada edifici al seu ritme)
                    fi = hr(x // 8, 41) * 6.283
                    lvl += 0.7 * (math.sin(ph * (1 + (x // 8) % 3) + fi) - math.sin(fi))
                elif y == sl + 1:
                    lvl += 0.8
                if (x, y) in WINDOWS or (x - 1, y) in WINDOWS or (x, y - 1) in WINDOWS or (x - 1, y - 1) in WINDOWS:
                    cv.flat(x, y, (236, 170, 80) if hr(x, y) > 0.3 else (190, 110, 50))
                else:
                    cv.put(x, y, SIL, lvl + (hr(x // 2, y // 3, 6) - 0.5) * 0.3, 0)
                continue
            lvl = 0.6 + min(1, (y - GY0) / 80) ** 2.4 * 8.6
            dm = math.hypot(x - MOON[0], y - MOON[1])
            if dm < 29:
                lvl += (1 - dm / 29) ** 2 * 2.2
            cv.put(x, y, SKY, lvl, 0)
            s = smoke(x, y)
            if s > 0 and s > B4[y & 3][x & 3] * 0.7:
                cv.put(x, y, SMOKE, s * 3.6 + 0.4, 0)
            if (x, y) in STARS and dm > 12:
                si = 2 if hr(x, y, 1) > 0.5 else 1
                if hr(x, y, 2) > 0.45:                         # n'hi ha que titil·len
                    fi = hr(x, y, 3) * 6.283
                    si += round(1.2 * (math.sin(ph * (1 + int(hr(x, y, 4) * 3)) + fi) - math.sin(fi)))
                si = max(0, min(3, si))
                if si:
                    cv.flat(x, y, ((0, 0, 0), (140, 140, 190), (200, 200, 230), (244, 244, 255))[si])
                    if si == 3:
                        bright.append((x, y))
    for x, y in bright:                                        # les més brillants fan creueta
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            xx, yy = x + dx, y + dy
            if GX0 <= xx <= GX1 and GY0 <= yy < SKYLINE[xx] and (xx, yy) not in STARS:
                cv.flat(xx, yy, mix(cv.P[xx, yy], (170, 170, 210), 0.6))
    # la lluna, amb els mars
    cv.disc(MOON[0], MOON[1], 7.3, 7.3, PAPER, lambda nx, ny: 5.6 - nx * 1.2 - ny * 0.6, 0)
    for mx, my in ((134, 51), (138, 55), (137, 50), (133, 55), (139, 52)):
        cv.put(mx, my, PAPER, 3.6, 0)
    # travessers
    for x in (163, 164):
        cv.vline(x, GY0, GY1, WALNUT, 2.2 if x == 163 else 1.2)
    for y in (65, 66, 99, 100):
        cv.hline(GX0, GX1, y, WALNUT, 2.4 if y in (65, 99) else 1.2)
    # reflex al vidre
    for i in range(13):
        cv.put(120 + i, 80 - i, PAPER, 1.4, 0)
        cv.put(121 + i, 80 - i, PAPER, 0.8, 0)
        cv.put(171 + i, 128 - i, PAPER, 1.0, 0)
    curtains(cv)


def curtains(cv):
    """Cortines de vellut vermell, la galeria amb el serrell de borles i els lligacortines."""
    def curtain(x0, x1, tie_side):
        for y in range(19, 151):
            # el lligacortines les estreny: els plecs s'arrufen a l'alçada del cordó
            pinch = max(0.0, 1 - abs(y - 99) / 30) * 0.6
            for x in range(x0, x1 + 1):
                u = (x - x0) / (x1 - x0)
                fold = math.sin(u * math.pi * (3.2 + pinch) + (0.6 if tie_side else 0)) * 0.9
                lvl = 2.6 + fold - (y - 19) / 187 + (hr(x, y // 2, 19) - 0.5) * 0.12
                if y > 146:
                    lvl -= 0.5                                 # la vora de baix, a l'ombra
                cv.put(x, y, RED, lvl)

    curtain(92, 116, False)
    curtain(212, 236, True)
    # galeria de la cortina
    cv.rect(91, 13, 237, 23, RED, lambda x, y: 3.4 - (y - 13) * 0.2 + math.sin(x / 4.0) * 0.5)
    for x in range(91, 238, 7):                               # serrell de borles
        cv.vline(x, 24, 27, GOLD, 3.2)
        cv.vline(x + 1, 25, 27, GOLD, 2.2)
        cv.put(x, 28, GOLD, 4.0)
        cv.put(x + 1, 28, GOLD, 2.6)
    cv.hline(91, 237, 23, GOLD, 3.0)
    cv.hline(91, 237, 22, GOLD, 2.0)
    cv.rect(93, 10, 235, 12, GOLD, lambda x, y: 3.6 - (y - 10) * 0.6)
    cv.disc(93, 11, 2.7, 2.7, GOLD, lambda nx, ny: 4.6 - nx - ny)
    cv.disc(235, 11, 2.7, 2.7, GOLD, lambda nx, ny: 4.6 - nx - ny)
    # lligacortines
    for cx in (104, 224):
        cv.rect(cx - 12, 96, cx + 12, 99, GOLD, lambda x, y: 3.6 - (y - 96) * 0.6 + (0.4 if (x + y) % 3 == 0 else 0))
        cv.disc(cx, 102, 2.1, 2.7, GOLD, lambda nx, ny: 3.6 - nx - ny)
        cv.vline(cx, 105, 108, GOLD, 2.6)
        cv.put(cx - 1, 108, GOLD, 2.0); cv.put(cx + 1, 108, GOLD, 2.0)


def radiator(cv):
    """Radiador de ferro colat sota la finestra."""
    for x in range(123, 209):
        for y in range(163, 199):
            k = (x - 123) % 8
            if k in (6, 7):
                cv.put(x, y, IRON, 0.6 if k == 6 else 0.9)
            else:
                lvl = [2.4, 3.0, 3.4, 3.2, 2.8, 2.0][k] - (0.6 if y > 194 else 0)
                if y in (163, 164) or y in (179, 180):
                    lvl += 0.8
                if y == 163 and k in (0, 5):
                    continue                                   # els caps de les columnes, arrodonits
                cv.put(x, y, IRON, lvl + (hr(x, y, 23) - 0.5) * 0.2)
    cv.rect(120, 197, 211, 200, IRON, lambda x, y: 1.6 + (0.6 if y == 197 else 0))
    cv.rect(203, 200, 207, 204, IRON, 2.2)
    cv.rect(203, 203, 211, 204, IRON, 1.4)
    cv.disc(209, 202, 1.6, 1.6, GOLD, 3.0)                       # la clau de pas
    cv.rect(124, 166, 126, 168, GOLD, 3.0)                        # el purgador


def portrait(cv):
    """Retrat del director Aldaia (272..347 × 36..121), amb el llum de llautó i la placa."""
    FX0, FY0, FX1, FY1 = 272, 36, 347, 121
    for y in range(FY0, FY1 + 1):
        for x in range(FX0, FX1 + 1):
            d = min(x - FX0, FX1 - x, y - FY0, FY1 - y)
            if d > 7:
                continue
            lit_side = (x - FX0) < (FX1 - x) and (y - FY0) < (FY1 - y) * 3
            base = [1.6, 2.4, 3.0, 4.4, 4.0, 3.4, 2.4, 0.8][d]
            if d in (3, 4) and (x + y) % 4 == 0:
                base -= 0.9                                    # talla
            if d in (1, 2, 3, 4) and not lit_side and (x - FX0) > (FX1 - x):
                base -= 0.7
            if d in (1, 2, 3, 4) and (y - FY0) > (FY1 - y):
                base -= 0.5
            cv.put(x, y, GOLD, base)
    for cx, cy in ((FX0 + 3, FY0 + 3), (FX1 - 3, FY0 + 3), (FX0 + 3, FY1 - 3), (FX1 - 3, FY1 - 3)):
        cv.disc(cx, cy, 4, 4, GOLD, lambda nx, ny: 4.8 - nx - ny)
        cv.put(cx, cy, GOLD, 1.0)
        cv.put(cx - 1, cy - 1, GOLD, 5.6)
    cv.disc((FX0 + FX1) / 2, FY0 + 1, 7, 4, GOLD, lambda nx, ny: 4.6 - nx * 0.6 - ny)
    cv.put((FX0 + FX1) // 2, FY0 + 1, GOLD, 1.4)

    CX0, CY0, CX1, CY1 = FX0 + 8, FY0 + 8, FX1 - 8, FY1 - 8  # tela 280..339 × 44..113
    HCX, HCY = 309, 71

    for y in range(CY0, CY1 + 1):
        for x in range(CX0, CX1 + 1):
            d = math.hypot(x - 299, y - 59) / 53
            cv.put(x, y, SIL, 3.0 - d * 2.4 + (hr(x // 2, y // 2, 4) - 0.5) * 0.4 + (0.15 if (x + y * 3) % 5 == 0 else 0) + 0.8, 0.5)

    # espatlles i americana
    for y in range(85, CY1 + 1):
        half = min(12 + (y - 85) * 1.0, 29)
        for x in range(CX0, CX1 + 1):
            dx = x - HCX
            if abs(dx) <= half:
                lvl = 2.0 - dx / 29 * 1.2 - (y - 85) / 53
                if abs(dx) > half - 1:
                    lvl += 0.8
                cv.put(x, y, SUIT, lvl, 0.6)
    # solapes
    for y in range(88, CY1 + 1):
        w = (y - 88) // 2
        for s in (-1, 1):
            xx = HCX + s * (4 + w // 2)
            cv.put(xx, y, SUIT, 3.4 if s < 0 else 1.0, 0.6)
            cv.put(xx + s, y, SUIT, 2.6 if s < 0 else 0.6, 0.6)
    # coll alt i corbata
    for y in range(84, 93):
        for x in range(HCX - 7, HCX + 8):
            if abs(x - HCX) <= 7 - (y - 84) // 2:
                cv.put(x, y, PAPER, 4.2 - (x - HCX) * 0.2, 0.5)
    for y in range(88, 105):
        w = 1 if y < 93 else 2 - (y - 93) // 7
        for x in range(HCX - w, HCX + w + 1):
            cv.put(x, y, RED, 2.6 - (x - HCX) * 0.5, 0.5)
    cv.disc(HCX, 89, 1.6, 1.4, RED, 3.2, 0.5)                    # el nus
    cv.put(HCX, 96, GOLD, 4.4, 0.4)                               # l'agulla de corbata
    # insígnia de ferro-9
    cv.disc(HCX - 12, 99, 1.8, 1.8, CYAN, 3.4, 0)
    cv.put(HCX - 13, 98, CYAN, 5.0, 0)
    # coll (pell) i cap
    cv.rect(HCX - 4, 79, HCX + 4, 84, SKIN, lambda x, y: 2.0 - (x - HCX) * 0.25, 0.5)
    cv.disc(HCX, HCY, 11.3, 14, SKIN, lambda nx, ny: 3.6 - nx * 1.3 - ny * 0.5 - (nx * nx + ny * ny) * 0.6, 0.5)
    # orelles
    cv.disc(HCX - 12, 72, 1.8, 3.3, SKIN, 2.8, 0.5)
    cv.disc(HCX + 12, 72, 1.8, 3.3, SKIN, 1.6, 0.5)
    cv.put(HCX - 12, 72, SKIN, 1.6, 0.5)
    # cabells grisos, entrades i patilles
    for y in range(55, 67):
        for x in range(HCX - 12, HCX + 13):
            nx, ny = (x - HCX) / 12, (y - 68) / 14
            if nx * nx + ny * ny <= 1.02:
                bald = abs(x - HCX) < 7 - (y - 55) * 0.6 and y > 57
                if not bald:
                    cv.put(x, y, GRAY, 3.6 - (x - HCX) / 8 - (hr(x, y, 8) * 0.8) + (0.4 if (x + y) % 3 == 0 else 0), 0.5)
    for s in (-1, 1):
        for y in range(64, 78):
            cv.put(HCX + s * 11, y, GRAY, 3.0 if s < 0 else 1.8, 0.5)
            if y < 74:
                cv.put(HCX + s * 12, y, GRAY, 2.6 if s < 0 else 1.4, 0.5)
    # celles severes, ulls, nas, bigoti
    for i in range(5):
        cv.put(HCX - 8 + i, 67 + (1 if i == 0 else 0), GRAY, 1.0, 0)
        cv.put(HCX + 3 + i, 67 + (1 if i == 4 else 0), GRAY, 0.6, 0)
    for ex in (HCX - 5, HCX + 4):
        cv.put(ex, 70, SUIT, 0.0, 0)
        cv.put(ex + 1, 70, SUIT, 0.0, 0)
        cv.put(ex - 1, 71, SKIN, 1.6, 0)
        cv.put(ex + 2, 71, SKIN, 1.6, 0)
        cv.hline(ex - 1, ex + 2, 72, SKIN, 2.2, 0)             # la bossa de l'ull
    cv.put(HCX - 5, 70, PAPER, 2.0, 0)
    cv.vline(HCX + 1, 71, 76, SKIN, 1.6, 0)
    cv.put(HCX, 76, SKIN, 1.4, 0)
    cv.put(HCX - 1, 75, SKIN, 4.4, 0)
    cv.put(HCX + 2, 76, SKIN, 1.0, 0)
    for x in range(HCX - 8, HCX + 9):
        d = abs(x - HCX)
        cv.put(x, 78 + d // 4, GRAY, 3.2 - (x - HCX) / 6, 0.5)
        if d < 7:
            cv.put(x, 79 + d // 4, GRAY, 2.4 - (x - HCX) / 6, 0.5)
    cv.hline(HCX - 3, HCX + 3, 82, SKIN, 1.0, 0)
    # placa amb el nom
    cv.rect(299, 117, 320, 120, GOLD, lambda x, y: 4.2 - (y - 117) * 0.7)
    for x in range(301, 319, 2):
        cv.put(x, 119, GOLD, 1.4)
    # llum de quadre de llautó
    cv.rect(296, 29, 323, 33, GOLD, lambda x, y: 4.4 - (y - 29) * 0.7)
    cv.vline(309, 24, 28, GOLD, 3.0)
    cv.disc(309, 24, 1.5, 1.5, GOLD, 3.6)
    cv.hline(299, 320, 34, PAPER, 6)
    cv.glow(309, 40, 40, (255, 220, 150), 0.22)


def blueprint(cv):
    """Plànol d'una màquina, emmarcat (sobre l'escriptori)."""
    BX0, BY0, BX1, BY1 = 379, 48, 469, 109
    cv.rect(BX0, BY0, BX1, BY1, WALNUT, lambda x, y: 1.2 if (x >= BX1 - 2 or y >= BY1 - 2) else (3.4 if x == BX0 or y == BY0 else 2.8))
    cv.rect(BX0 + 4, BY0 + 4, BX1 - 4, BY1 - 4, BLUEP, lambda x, y: 2.0 + (0.4 if (x % 8 == 0 or y % 8 == 0) else 0) + (hr(x, y, 2) - 0.5) * 0.5, 0.6)
    cv.hline(BX0 + 4, BX1 - 4, BY0 + 4, BLUEP, 1.0, 0.6)          # l'ombra del marc

    def bp(x, y, lvl=5.0):
        cv.put(x, y, BLUEP, lvl, 0.3)

    def bp_circle(cx, cy, r, teeth=0):
        for a in range(0, 360, 3):
            rr = r + (1.5 if teeth and int(a / (360 / teeth / 2)) % 2 else 0)
            bp(round(cx + math.cos(math.radians(a)) * rr), round(cy + math.sin(math.radians(a)) * rr))

    bp_circle(405, 75, 14, teeth=12)
    bp_circle(405, 75, 5)
    bp_circle(437, 85, 9, teeth=8)
    bp_circle(437, 85, 3)
    for a in range(0, 360, 60):                               # radis de l'engranatge gran
        for i in range(6, 12, 2):
            bp(round(405 + math.cos(math.radians(a)) * i), round(75 + math.sin(math.radians(a)) * i), 4.4)
    for x in range(421, 461):
        bp(x, 61)
    for y in range(61, 101):
        bp(460, y, 4.6)
    for x in range(389, 424, 2):
        bp(x, 99, 4.4)
    for i in range(8):
        bp(443 + i * 2, 56, 4.4)
    for x in (389, 390, 391, 393, 394, 396, 397):
        bp(x, 56)
    for y in (95, 103):                                       # cota
        bp(389, y, 4.0); bp(424, y, 4.0)
    for x, y in ((BX0 + 5, BY0 + 5), (BX1 - 5, BY0 + 5)):
        cv.put(x, y, GOLD, 4.0)
        cv.put(x, y + 1, GOLD, 1.6)


def desk(cv):
    """L'escriptori, amb el calaix del pany M-3, l'expedient del Sic, el tinter i la làmpada de banquer."""
    DX0, DX1 = 355, 491
    TOP_BACK, TOP_FRONT = 151, 161
    # ombra al terra
    for y in range(FLOOR_Y, 217):
        for x in range(DX0 - 5, DX1 + 8):
            a = (1 - (y - FLOOR_Y) / 12) * (1 - max(0, abs(x - 423) - 59) / 16)
            if a > B4[y & 3][x & 3]:
                o = cv.P[x, y]
                cv.P[x, y] = tuple(int(c * 0.55) for c in o[:3]) + (255,)
    # cos: pedestals i calaix central (calaix: 378..459 × 174..197)
    cv.rect(DX0 + 2, 168, DX1 - 2, 204, WALNUT, lambda x, y: 2.4 + (hr(x // 2, 31) - 0.5) * 0.3)
    cv.rect(DX0 + 2, 200, DX1 - 2, 204, WALNUT, lambda x, y: 1.0 + (0.6 if y == 200 else 0))     # sòcol
    cv.vline(DX0 + 2, 168, 204, WALNUT, 3.4)
    cv.vline(DX1 - 2, 168, 204, WALNUT, 1.0)

    def drawer(x0, y0, x1, y1, handle=True):
        cv.rect(x0, y0, x1, y1, WALNUT, lambda x, y: 2.9 + (hr(x // 2, y0) - 0.5) * 0.3 + 0.1 * math.sin(x / 4 + y0))
        cv.hline(x0, x1, y0, WALNUT, 4.2)
        cv.vline(x0, y0, y1, WALNUT, 3.8)
        cv.hline(x0, x1, y1, WALNUT, 0.6)
        cv.vline(x1, y0, y1, WALNUT, 1.0)
        if handle:
            cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
            cv.rect(cx - 4, cy, cx + 4, cy + 1, GOLD, lambda x, y: 4.0 - (y - cy) * 1.6)
            cv.put(cx - 4, cy - 1, GOLD, 3.0); cv.put(cx + 4, cy - 1, GOLD, 3.0)

    for y0, y1 in ((172, 184), (187, 197)):
        drawer(360, y0, 375, y1)
        drawer(463, y0, 485, y1)
    # calaix central amb el pany M-3
    drawer(380, 175, 457, 196, handle=False)
    cv.rect(413, 180, 424, 191, IRON, lambda x, y: 3.0 - (x - 413) * 0.15 - (y - 180) * 0.12)
    cv.hline(413, 424, 180, IRON, 4.0)
    for px, py in ((414, 181), (423, 181), (414, 190), (423, 190)):
        cv.put(px, py, IRON, 4.6)
    cv.disc(418.5, 185.5, 3.5, 3.5, CYAN, lambda nx, ny: 3.4 - nx - ny, 0)
    cv.put(417, 184, CYAN, 5, 0)
    cv.put(418, 184, CYAN, 4.4, 0)
    cv.glow(418.5, 185.5, 19, (100, 200, 255), 0.55)
    # tauler: gruix frontal i superfície amb pell verda
    cv.rect(DX0, 161, DX1, 167, WALNUT, lambda x, y: [4.8, 4.4, 4.0, 3.4, 3.0, 2.2, 1.0][y - 161])
    for y in range(TOP_BACK, TOP_FRONT):
        t = (y - TOP_BACK) / (TOP_FRONT - TOP_BACK)
        xl, xr = DX0 + 5 - t * 5, DX1 - 5 + t * 5
        for x in range(round(xl), round(xr) + 1):
            inl = xl + 11 < x < xr - 11 and TOP_BACK + 1 < y < TOP_FRONT - 1
            edge = inl and not (xl + 12 < x < xr - 12 and TOP_BACK + 2 < y < TOP_FRONT - 2)
            if edge:
                cv.put(x, y, GOLD, 2.6 + t * 0.6)              # el filet daurat de la pell
            else:
                cv.put(x, y, LAMPG if inl else WALNUT, (1.4 + (hr(x // 2, y, 5) - 0.5) * 0.3 if inl else 3.6) + t * 0.6)
    cv.hline(DX0 + 5, DX1 - 5, TOP_BACK, WALNUT, 2.2)
    # potes torneades visibles als costats
    for x in (DX0 + 1, DX1 - 1):
        cv.vline(x, 168, 204, WALNUT, 1.6)

    # expedient del Sic (zona 385..452 × 141..163): carpeta de cartolina amb papers i cinta vermella
    for y in range(149, 161):
        t = (y - 149) / 11
        xl, xr = 392 - t * 4, 443 - t * 1
        for x in range(round(xl), round(xr) + 1):
            cv.put(x, y, MANILA, 3.2 + t * 0.4 - (0.8 if x > xr - 1 else 0) + (hr(x // 3, y, 7) - 0.5) * 0.15)
    for y in range(146, 156):                                   # fulls que sobresurten
        for x in range(397 - (y - 146) // 3, 435):
            if y < 149 or x > 429:
                cv.put(x, y, PAPER, 4.0 - (y - 146) * 0.12 - (0.6 if (x * 3 + y) % 11 == 0 else 0))
    cv.hline(395, 432, 145, PAPER, 3.0)
    cv.hline(388, 444, 161, MANILA, 1.2)
    for y in range(149, 162):                                   # cinta
        cv.put(413, y, RED, 3.4)
        cv.put(414, y, RED, 2.4)
    for x in range(389, 443):
        if x % 2 and 408 < x < 421:
            cv.put(x, 155, RED, 3.0)
    cv.disc(413.5, 155, 2, 1.5, RED, 3.6)                       # el llaç
    cv.rect(395, 151, 405, 153, RED, 3.2)                          # segell «confidencial»
    for x in (397, 399, 401, 403):
        cv.put(x, 152, MANILA, 4.4)

    # tinter i ploma
    cv.disc(373, 153, 4, 3.2, IRON, lambda nx, ny: 2.4 - nx - ny)
    cv.put(372, 151, PAPER, 4.0, 0)
    cv.hline(370, 376, 156, IRON, 0.6)
    for i in range(11):
        cv.put(375 + i // 2, 151 - i, PAPER, 3.4 - i * 0.1)
        cv.put(376 + i // 2, 151 - i, PAPER, 2.4)
    cv.put(376, 142, PAPER, 4.4)

    # làmpada de banquer
    cv.disc(465, 158, 9.3, 2.9, GOLD, lambda nx, ny: 3.8 - nx - ny)
    cv.vline(465, 139, 155, GOLD, 4.0)
    cv.vline(466, 139, 155, GOLD, 2.4)
    cv.rect(463, 147, 468, 148, GOLD, 3.4)                         # el nus de la tija
    cv.put(472, 152, GOLD, 3.0); cv.vline(472, 153, 156, GOLD, 2.0)   # la cadeneta
    for y in range(128, 139):
        t = (y - 128) / 10
        half = 13 + t * 5
        for x in range(round(465 - half), round(465 + half) + 1):
            u = (x - 465) / half
            cv.put(x, y, LAMPG, 3.2 - u * 1.6 - (1 - t) * 0.6 + (1.6 if y == 129 and u < 0 else 0), 0.3)
    cv.hline(447, 484, 139, [(255, 236, 170)], 0, 0)
    cv.hline(448, 483, 140, GOLD, 5.0, 0)
    cv.glow(465, 144, 45, (255, 226, 150), 0.45)


def lectern(cv):
    """Faristol amb el llibre d'inventari (523..583 × 141..179)."""
    # peu
    cv.disc(552, 224, 21, 4, WALNUT, lambda nx, ny: 1.8 - ny, 0.8)
    for i, x in enumerate((534, 552, 570)):                     # les tres potes
        cv.rect(x - 2, 222, x + 2, 225, WALNUT, 2.8 - i * 0.6)
    cv.rect(547, 173, 557, 221, WALNUT, lambda x, y: [3.8, 3.6, 3.4, 3.0, 2.6, 2.4, 2.0, 1.6, 1.2, 1.0, 0.8][x - 547]
            + (0.5 if y in (186, 187, 210, 211) else 0))           # anelles torneades
    cv.rect(544, 200, 560, 203, WALNUT, lambda x, y: 3.0 + (0.8 if y == 200 else 0))
    # tauler inclinat
    for y in range(144, 175):
        t = (y - 144) / 30
        xl, xr = 527 - t * 7, 580 + t * 7
        for x in range(round(xl), round(xr) + 1):
            cv.put(x, y, WALNUT, 2.6 + t * 0.8)
    cv.rect(519, 175, 588, 177, WALNUT, lambda x, y: [4.0, 2.8, 1.0][y - 175])
    # llibre obert: tapes vermelles i pàgines
    for y in range(144, 172):
        t = (y - 144) / 27
        xl, xr = 528 - t * 5, 579 + t * 5
        for x in range(round(xl), round(xr) + 1):
            cv.put(x, y, RED, 2.4 + t * 0.4)
    for y in range(143, 170):
        t = (y - 143) / 27
        xl, xr = 531 - t * 5, 576 + t * 5
        mid = 553
        for x in range(round(xl), round(xr) + 1):
            s = (x - mid) / ((xr - xl) / 2)
            curve = -abs(s) ** 0.5 * 0.3
            lvl = 4.4 + curve - (1.4 if abs(x - mid) < 1.5 else 0) - (0.6 if abs(x - mid) < 4 else 0)
            yy = y - round((1 - abs(s)) * 2)
            cv.put(x, yy, PAPER, lvl)
    # gruix de les pàgines a baix
    for x in range(527, 581):
        if abs(x - 553) > 1:
            cv.put(x, 170, PAPER, 2.6 if x % 2 else 3.2)
    # ratlles i anotacions de comptabilitat
    for row in range(5):
        y = 147 + row * 4
        for x in range(533 - row, 574 + row):
            if abs(x - 553) > 3:
                if hr(x // 3, row) > 0.3 and x % 3:
                    cv.put(x, y, PAPER, 2.2)
    for y in range(146, 166):                                  # el marge vermell de cada pàgina
        cv.put(540 - (y - 146) // 5, y, RED, 3.6)
        cv.put(566 + (y - 146) // 5, y, RED, 3.6)
    # cinta del punt de llibre
    for y in range(169, 187):
        cv.put(555 + (y - 169) // 8, y, RED, 3.6 - (y - 169) * 0.04)
        cv.put(556 + (y - 169) // 8, y, RED, 2.4)


def shelves(cv):
    """Prestatgeria (dreta) plena de llibres."""
    SX0, SX1 = 595, 639
    cv.rect(SX0 - 3, 35, SX1, 204, WALNUT, 1.0)
    cv.rect(SX0 - 4, 29, SX1, 34, WALNUT, lambda x, y: 3.8 - (y - 29) * 0.5)
    cv.hline(SX0 - 4, SX1, 29, WALNUT, 4.6)
    cv.vline(SX0 - 3, 35, 204, WALNUT, 3.0)
    cv.vline(SX0 - 2, 35, 204, WALNUT, 2.2)
    cv.vline(SX0 - 1, 35, 204, WALNUT, 1.4)
    top = 37
    book_rnd = random.Random(21)
    BOOK_RAMPS = [RED, LAMPG, NAVY, MANILA, WALNUT, COPPER]
    for sy in (69, 107, 144, 181):
        cv.rect(SX0, top, SX1, sy - 1, WALNUT, 0.4)
        x = SX0 + 1
        while x < SX1:
            bw = book_rnd.randint(3, 5)
            bh = book_rnd.randint(19, sy - top - 4)
            ramp = book_rnd.choice(BOOK_RAMPS)
            base = book_rnd.uniform(1.6, 2.8) + (1.0 if ramp in (NAVY,) else 0)
            if book_rnd.random() < 0.1 and x + 11 < SX1:
                # un llibre ajagut
                cv.rect(x, sy - 4, x + 10, sy - 1, ramp, lambda xx, yy: base + (0.8 if yy == sy - 4 else 0) - (0.6 if yy == sy - 1 else 0))
                x += 4
                continue
            for bx in range(x, min(SX1 + 1, x + bw)):
                for by in range(sy - bh, sy):
                    lvl = base + (0.8 if bx == x else 0) - (0.8 if bx == x + bw - 1 else 0)
                    if by in (sy - bh + 3, sy - 5) or (bw > 3 and by in (sy - bh + 4,) and bx == x + 1):
                        cv.put(bx, by, GOLD, 3.4)
                    elif by == sy - bh:
                        cv.put(bx, by, ramp, lvl + 0.8)
                    else:
                        cv.put(bx, by, ramp, lvl)
            x += bw
        cv.rect(SX0 - 1, sy, SX1, sy + 3, WALNUT, lambda x, y: [3.8, 3.2, 2.4, 1.2][y - sy])
        top = sy + 4
    cv.rect(SX0, 185, SX1, 204, WALNUT, lambda x, y: 2.2 if y > 188 else 1.0)
    cv.hline(SX0, SX1, 194, WALNUT, 1.2)


def static(cv):
    """Tota la sala, amb la finestra al moment 0 i sense la pols."""
    walls(cv)
    floor(cv)
    door(cv)
    pipe(cv)
    window_frame(cv)
    window(cv, 0.0)
    radiator(cv)
    portrait(cv)
    blueprint(cv)
    desk(cv)
    lectern(cv)
    shelves(cv)
    # tint fred de la lluna al terra
    cv.tint(0, 200, W - 1, 273, (150, 170, 230), lambda x, y: 0.22 * moon(x, y))


def beam_dust(cv, tt):
    """Pols que sura dins el raig de la lluna, de la finestra al terra."""
    dust(cv, tt, 30, 7, (128, 139, 267, 235), (206, 216, 248), 0.75, moon_beam, fall=(-4, 8), wander=2.7)


@lru_cache(maxsize=None)
def _static():
    cv = Canvas(light=LIGHT)
    static(cv)
    return cv.img


def _frame(t):
    cv = Canvas(light=LIGHT, img=_static().copy())
    if t:
        window(cv, t)                                          # (la finestra no toca res de la resta)
    beam_dust(cv, t)
    return cv.img


def bg(cv, t=0.0):
    cv.img.paste(_frame(t))


PROPS = {}

ANIMS = {'ambient': {'frames': lambda: ambient_frames(bg, LIGHT, 24, box=(107, 27, 333, 273),
                                                      draw=lambda t: _frame(t).convert('RGB')),
                     'frameDuration': 130}}
