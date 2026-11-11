"""
Sala de calderes (Acte 1-3, Iri) a 640×360: la composició de hd/rooms/fabrica_calderes.py ×4/3, dibuixada de nou.
Maó socarrimat, coure, vapor i el foc de la caldera gran.
Llums: la boca del foc (la gran font, taronja), el llum d'alarma vermell de la cambra i el llum
d'escriptori del capatàs.

També hi ha les peces comunes de les sales de la fàbrica (paret de maó, terres, portes, manòmetres,
vapor i lletres petites), que fan servir el magatzem i el moll.
Decorats: `segell`, `alarma_encesa`. Animació: `ambient` (el foc respira, les guspires pugen i el vapor s'escampa).
"""
import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)

import math
import random
from functools import lru_cache

from PIL import Image, ImageChops

from hd.pix import (Canvas, Light, B4, W, H, hr, mix, WALNUT, GOLD, COPPER, RUST, BRICK, IRON, FIRE, RED,
                    PAPER, MANILA, LAMPG, WARN)
from hd.rooms.fabrica_calderes import STONE, STEAM, CORK, COAL, ENAMEL, NAVY_INK, PINK_HOT  # noqa: F401

FIRE_X, FIRE_Y = 171, 195


def make_light(alarm=False):
    lt = Light(vignette=(93, 53), floor_fade=(264, 53))
    lt.point(FIRE_X, FIRE_Y - 5, r=307, k=3.4, squash=0.95, power=2.0)     # la boca del foc
    if alarm:
        lt.point(596, 72, r=83, k=1.5, power=1.8)                           # alarma vermella
    lt.point(429, 155, r=93, k=1.7, squash=1.2, down=True)                  # llum del capatàs
    return lt


# el fons té l'alarma apagada; el prop alarma_encesa hi posa el llum i el seu halo
LIGHT = make_light()
LIGHT_ALARM = make_light(alarm=True)

FLOOR_Y = 211


# ─── Lletres petites (4×6) per a rètols ─────────────────────────────────────
FONT = {
    'A': ['.##.', '#..#', '#..#', '####', '#..#', '#..#'], 'B': ['###.', '#..#', '###.', '#..#', '#..#', '###.'],
    'C': ['.###', '#...', '#...', '#...', '#...', '.###'], 'D': ['###.', '#..#', '#..#', '#..#', '#..#', '###.'],
    'E': ['####', '#...', '###.', '#...', '#...', '####'], 'F': ['####', '#...', '###.', '#...', '#...', '#...'],
    'G': ['.###', '#...', '#.##', '#..#', '#..#', '.###'], 'H': ['#..#', '#..#', '####', '#..#', '#..#', '#..#'],
    'I': ['###', '.#.', '.#.', '.#.', '.#.', '###'], 'K': ['#..#', '#.#.', '##..', '#.#.', '#..#', '#..#'],
    'L': ['#...', '#...', '#...', '#...', '#...', '####'],
    'M': ['#...#', '##.##', '#.#.#', '#...#', '#...#', '#...#'], 'W': ['#...#', '#...#', '#...#', '#.#.#', '##.##', '#...#'],
    'N': ['#..#', '##.#', '#.##', '#..#', '#..#', '#..#'], 'O': ['.##.', '#..#', '#..#', '#..#', '#..#', '.##.'],
    'P': ['###.', '#..#', '#..#', '###.', '#...', '#...'], 'R': ['###.', '#..#', '#..#', '###.', '#.#.', '#..#'],
    'S': ['.###', '#...', '.##.', '...#', '...#', '###.'], 'T': ['###', '.#.', '.#.', '.#.', '.#.', '.#.'],
    'U': ['#..#', '#..#', '#..#', '#..#', '#..#', '.##.'], 'Z': ['####', '...#', '..#.', '.#..', '#...', '####'],
    'X': ['#..#', '#..#', '.##.', '.##.', '#..#', '#..#'], 'V': ['#...#', '#...#', '#...#', '.#.#.', '.#.#.', '..#..'],
    '2': ['.##.', '#..#', '..#.', '.#..', '#...', '####'], '7': ['####', '...#', '..#.', '.#..', '.#..', '.#..'],
    '9': ['.##.', '#..#', '#..#', '.###', '...#', '.##.'], '1': ['.#.', '##.', '.#.', '.#.', '.#.', '###'],
    '-': ['...', '...', '###', '...', '...', '...'], '!': ['#', '#', '#', '#', '.', '#'],
    ' ': ['..', '..', '..', '..', '..', '..'], '.': ['.', '.', '.', '.', '.', '#'],
}


def text(cv, x, y, s, ramp, lvl, lit=0.6):
    """Escriu en lletra de 4×6 (amb un píxel d'espai)."""
    for ch in s:
        g = FONT.get(ch, FONT[' '])
        for j, row in enumerate(g):
            for i, c in enumerate(row):
                if c == '#':
                    cv.put(x + i, y + j, ramp, lvl, lit)
        x += len(g[0]) + 1
    return x


def text_w(s):
    return sum(len(FONT.get(ch, FONT[' '])[0]) + 1 for ch in s) - 1


# ─── Peces comunes de la fàbrica ────────────────────────────────────────────

def outline(cv, x0, y0, x1, y1, col=(22, 12, 16), skip_below=None):
    """Contorn fosc al voltant d'un prop (en un llenç transparent), perquè se separi del fons."""
    P = cv.P
    pts = []
    for y in range(max(0, y0), min(cv.h, y1 + 1)):
        if skip_below is not None and y > skip_below:
            continue
        for x in range(max(0, x0), min(cv.w, x1 + 1)):
            if P[x, y][3]:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                xx, yy = x + dx, y + dy
                if 0 <= xx < cv.w and 0 <= yy < cv.h and P[xx, yy][3]:
                    pts.append((x, y))
                    break
    for x, y in pts:
        cv.flat(x, y, col)


def brick_wall(cv, x0, y0, x1, y1, seed=1, base=2.0, extra=None):
    """Paret de maó (19×8): llagues fosques, cantell superior i esquerre clars, el de sota a l'ombra, gra de la
    terracota, porus, algun maó cremat i algun cantó escantonat."""
    for y in range(y0, y1 + 1):
        row = (y - y0) // 8
        ry = (y - y0) % 8
        off = 10 if row % 2 else 0
        for x in range(x0, x1 + 1):
            bx = (x + off) // 19
            rx = (x + off) % 19
            if ry == 7 or rx == 18:
                lvl = base - 1.2                                    # llaga de morter
                if ry == 7 and rx == 18:
                    lvl -= 0.2
                elif hr(x, y, seed + 9) > 0.9:
                    lvl += 0.4                                      # gra del morter
            else:
                n = hr(bx, row, seed)
                lvl = base + (n - 0.5) * 0.7 + (hr(x // 3, y // 2, seed + 3) - 0.5) * 0.18
                if n > 0.93:
                    lvl -= 0.7                                      # maó cremat
                if ry == 0:
                    lvl += 0.45
                elif ry == 1:
                    lvl += 0.15
                elif ry == 6:
                    lvl -= 0.35
                if rx == 0:
                    lvl += 0.2
                elif rx == 17:
                    lvl -= 0.15
                if hr(x, y, seed) > 0.97:
                    lvl -= 0.5                                      # porus
                if hr(bx, row, seed + 5) > 0.86 and ((rx < 2 and ry < 2) or (rx > 15 and ry > 4)):
                    lvl = base - 1.0                                # cantó escantonat
            if extra:
                lvl += extra(x, y)
            cv.put(x, y, BRICK, lvl)


def stone_floor(cv, y0, y1=H - 1, extra=None, vpx=320):
    """Terra de lloses grans en perspectiva, amb taques, esquerdes i el cantell il·luminat de cada llosa."""
    VPY = -200
    for y in range(y0, y1 + 1):
        dep = y - VPY
        z = 4800 / dep
        row = math.floor(z / 1.9)
        row_up = math.floor(4800 / (dep - 1) / 1.9)
        for x in range(W):
            u = (x - vpx) / dep * 40 / 2.2 + (0.5 if row % 2 else 0)
            col = math.floor(u)
            fr = (u - col) * dep / 40 * 2.2
            n = hr(col, row, 5)
            lvl = 2.3 + (n - 0.5) * 0.7 + (hr(x // 2, y, row) - 0.5) * 0.15
            if hr(x // 4, y // 2, row) > 0.9:
                lvl -= 0.35                                        # taques
            if hr(col, row, 9) > 0.8:                              # una esquerda que travessa la llosa
                if abs(fr - (4 + hr(col, row, 10) * 10) - (z % 1.9) * 9) < 0.6:
                    lvl -= 0.9
            if fr < 1:
                lvl = 0.9
            elif fr < 2:
                lvl += 0.35                                        # cantell il·luminat
            if row != row_up:
                lvl = 0.8
            if y < y0 + 8:
                lvl -= (y0 + 8 - y) / 8 * 1.2                       # ombra de contacte amb la paret
            if extra:
                lvl += extra(x, y)
            cv.put(x, y, STONE, lvl)


def contact_shadow(cv, x0, x1, y0, depth, k=1.0):
    """Ombra dithered sota un moble (decreix cap avall i als costats)."""
    cx, half = (x0 + x1) / 2, (x1 - x0) / 2
    for y in range(y0, y0 + depth):
        for x in range(int(x0 - 5), int(x1 + 7)):
            a = (1 - (y - y0) / depth) * min(1, 1 - (abs(x - cx) - half) / 7) * k
            if a > B4[y & 3][x & 3] and 0 <= x < W and 0 <= y < H:
                o = cv.P[x, y]
                if o[3]:
                    cv.P[x, y] = tuple(int(c * 0.55) for c in o[:3]) + (o[3],)


def plank_door(cv, x0, y0, x1, y1, ramp=WALNUT, knob=True, frame=5, base=2.4, braces=True, knob_x=None):
    """Porta de taulons verticals (de 9 px) amb marc, travessers en Z, claus i pom de llautó amb l'escut."""
    # marc
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            d = min(x - x0, x1 - x, y - y0)
            if d < frame:
                lvl = base + 0.6 + (0.8 if d == 0 and (y == y0 or x == x0) else 0) - (1.4 if x1 - x < frame and x1 - x < d + 1 else 0)
                lvl += (hr(x // 2, y // 5, 41) - 0.5) * 0.2
                if d == frame - 1:
                    lvl = base - 1.4                                # ombra interior
                cv.put(x, y, ramp, lvl)
    lx0, ly0, lx1 = x0 + frame, y0 + frame, x1 - frame
    for y in range(ly0, y1 + 1):
        for x in range(lx0, lx1 + 1):
            pl = (x - lx0) // 9
            px = (x - lx0) % 9
            g = (hr(x, 51, pl) - 0.5) * 0.22 + (hr(pl, y // 12) - 0.5) * 0.25
            g += 0.18 * math.sin((y + hr(pl, 7) * 40) / (5 + hr(pl, 8) * 4) + px * 0.7)   # veta
            lvl = base + g
            if px == 0:
                lvl = base - 1.1
            elif px == 1:
                lvl += 0.4
            elif px == 8:
                lvl -= 0.3
            if hr(x, y, 3) > 0.988:
                lvl -= 0.6                                         # nus
            if y > y1 - 4:
                lvl -= 0.6
            cv.put(x, y, ramp, lvl)
    if braces:
        for yb in (ly0 + 11, y1 - 16):
            cv.rect(lx0, yb, lx1, yb + 5, ramp, lambda x, y: base + 0.4 + (0.8 if y == yb else 0) - (1.3 if y == yb + 5 else 0)
                    + (hr(x // 3, yb) - 0.5) * 0.2)
        # travesser diagonal
        ya, yb = y1 - 16, ly0 + 17
        for x in range(lx0, lx1 + 1):
            t = (x - lx0) / (lx1 - lx0)
            yy = round(ya - t * (ya - yb))
            for k in range(6):
                cv.put(x, yy - k, ramp, base + 0.3 + (0.7 if k == 5 else 0) - (1.2 if k == 0 else 0))
        # claus de ferro (cap rodó, amb la llum per dalt)
        for yb2 in (ly0 + 13, y1 - 13):
            for x in range(lx0 + 4, lx1 - 1, 9):
                cv.put(x, yb2, IRON, 4.2)
                cv.put(x + 1, yb2 + 1, IRON, 1.0)
    if knob:
        kx = knob_x if knob_x is not None else lx1 - 7
        ky = (ly0 + y1) // 2 + 5
        cv.rect(kx - 2, ky - 7, kx + 3, ky + 8, GOLD, lambda x, y: 2.8 - (x - kx) * 0.4 + (0.6 if y == ky - 7 else 0))
        cv.disc(kx + 0.5, ky - 2, 3, 3, GOLD, lambda nx, ny: 4.6 - nx - ny * 1.2)
        cv.put(kx - 0.5, ky - 3, GOLD, 5.4)
        cv.rect(kx, ky + 3, kx + 1, ky + 3, GOLD, 0.2)              # el forat del pany
        cv.vline(kx, ky + 4, ky + 5, GOLD, 0.2)
    # escaló de pedra davant la porta
    cv.rect(x0 - 1, y1 + 1, x1 + 1, y1 + 3, STONE, lambda x, y: [3.4, 2.6, 1.8][y - y1 - 1] + (hr(x // 6, 3) - 0.5) * 0.3)


def gauge(cv, cx, cy, r, ang, lit=0.6, red_zone=True):
    """Manòmetre: anell de llautó, esfera de paper, marques, zona vermella, agulla (ang en graus, 0 = amunt)
    i el reflex del vidre."""
    cv.disc(cx, cy, r + 1.6, r + 1.6, GOLD, lambda nx, ny: 3.6 - nx * 1.2 - ny * 1.2)
    cv.ring(cx, cy, r + 0.7, GOLD, 1.4, step=4)
    cv.disc(cx, cy, r - 0.3, r - 0.3, PAPER, lambda nx, ny: 4.2 - ny * 0.8 - nx * 0.3, lit)
    if r >= 5:
        step = 15 if r >= 9 else 30
        for a in range(-120, 121, step):
            rr = r - 1.5
            major = a % 60 == 0
            cv.put(round(cx + math.sin(math.radians(a)) * rr), round(cy - math.cos(math.radians(a)) * rr), PAPER,
                   0.8 if major else 1.8, 0.2)
            if major and r >= 9:
                cv.put(round(cx + math.sin(math.radians(a)) * (rr - 1)), round(cy - math.cos(math.radians(a)) * (rr - 1)),
                       PAPER, 1.4, 0.2)
    if red_zone and r >= 5:
        for a in range(70, 125, 6):
            for rr in ((r - 1.2,) if r < 9 else (r - 1.2, r - 2.1)):
                cv.flat(round(cx + math.sin(math.radians(a)) * rr), round(cy - math.cos(math.radians(a)) * rr), (176, 40, 34))
    n = max(2, int(r - 1))
    for i in range(n):
        cv.flat(round(cx + math.sin(math.radians(ang)) * i), round(cy - math.cos(math.radians(ang)) * i), (40, 20, 20))
    if r >= 9:                                                     # la cua de l'agulla
        for i in (1, 2):
            cv.flat(round(cx - math.sin(math.radians(ang)) * i), round(cy + math.cos(math.radians(ang)) * i), (40, 20, 20))
    cv.flat(round(cx), round(cy), (30, 20, 20))
    if r >= 6:                                                     # reflex del vidre
        cv.put(round(cx - r * 0.45), round(cy - r * 0.55), PAPER, 6.0, 0)


def drift(puffs, t):
    """Fa avançar un raig de vapor: cada bufada va cap a la posició de la següent (t = 0..1), en
    neix una de nova a l'inici i l'última s'esvaeix. Amb t = 0 i t = 1 surt el mateix: fa bucle."""
    if not t:
        return puffs
    lerp = lambda a, b: tuple(a[i] + (b[i] - a[i]) * t for i in range(4))  # noqa: E731
    out = [(puffs[0][0], puffs[0][1], puffs[0][2], puffs[0][3] * t)]
    out += [lerp(a, b) for a, b in zip(puffs, puffs[1:])]
    last, prev = puffs[-1], puffs[-2]
    nxt = (2 * last[0] - prev[0], 2 * last[1] - prev[1], last[2] * 1.2, 0.0)
    out.append(lerp(last, nxt))
    return out


def steam(cv, puffs, lit=0.5, k=1.0):
    """Vapor: núvols suaus i dithered. puffs = [(cx, cy, r, densitat)]."""
    xs = [p[0] for p in puffs]
    ys = [p[1] for p in puffs]
    R_ = max(p[2] for p in puffs)
    for y in range(int(min(ys) - R_), int(max(ys) + R_) + 1):
        for x in range(int(min(xs) - R_), int(max(xs) + R_) + 1):
            v = 0.0
            for px_, py_, r, a in puffs:
                d = math.hypot(x - px_, (y - py_) * 1.15) / r
                if d < 1:
                    v = max(v, a * (1 - d * d))
            v *= k
            if v > 0.05 and v > B4[y & 3][x & 3] * 0.8:
                cv.put(x, y, STEAM, 0.8 + v * 3.6, lit)


def pipe_h(cv, x0, x1, y, th, ramp=COPPER, base=2.4, flange_every=0, seed=0):
    """Canonada horitzontal de gruix th, amb brides cargolades."""
    prof = [base - 0.6 + 2.2 * math.sin(math.pi * (i + 0.5) / th) ** 0.6 - (i / th) * 1.2 for i in range(th)]
    prof[0] -= 0.4
    prof[-1] = base - 1.6
    for x in range(x0, x1 + 1):
        for i in range(th):
            cv.put(x, y + i, ramp, prof[i] + (0.25 if hr(x // 5, i // 2, seed + 3) > 0.85 else 0))
    if flange_every:
        for fx in range(x0 + flange_every // 2 + seed, x1 - 3, flange_every):
            cv.rect(fx, y - 2, fx + 3, y + th + 1, ramp, lambda xx, yy: base + 1.2 - (xx - fx) * 0.6)
            cv.put(fx + 1, y - 2, ramp, base + 2.2)
            cv.put(fx + 1, y - 1, IRON, 4.0)                       # els cargols de la brida
            cv.put(fx + 1, y + th, IRON, 3.2)


def pipe_v(cv, x, y0, y1, th, ramp=COPPER, base=2.4, flange_every=0):
    prof = [base - 0.6 + 2.2 * math.sin(math.pi * (i + 0.5) / th) ** 0.6 - (i / th) * 1.4 for i in range(th)]
    prof[0] -= 0.3
    prof[-1] = base - 1.6
    for y in range(y0, y1 + 1):
        for i in range(th):
            cv.put(x + i, y, ramp, prof[i] + (0.25 if hr(i // 2, y // 5, 7) > 0.85 else 0))
    if flange_every:
        for fy in range(y0 + flange_every // 2, y1 - 3, flange_every):
            cv.rect(x - 2, fy, x + th + 1, fy + 3, ramp, lambda xx, yy: base + 1.4 - (yy - fy) * 0.6 - (xx - x) * 0.15)
            cv.put(x - 1, fy + 1, IRON, 4.0)
            cv.put(x + th, fy + 1, IRON, 3.0)


def bracket(cv, x, y, w=4):
    """Abraçadora de ferro que aguanta una canonada contra la paret."""
    cv.rect(x, y, x + w - 1, y + 2, IRON, lambda xx, yy: 3.0 - (yy - y) * 0.6)
    cv.put(x + 1, y, IRON, 4.2)
    cv.put(x + w - 2, y + 1, IRON, 1.4)


def ceiling(cv, ramp=IRON, h=18):
    """Sostre: bigues de ferro reblades i fosc entre elles."""
    for y in range(0, h):
        for x in range(W):
            lvl = 0.5 + (hr(x // 53) - 0.5) * 0.3 + (0.25 if (x // 3 + y) % 9 == 0 else 0) * (y < h - 4)
            cv.put(x, y, ramp, lvl)
    for x in range(0, W, 80):                                  # bigues transversals
        cv.rect(x, 0, x + 7, h - 4, ramp, lambda xx, yy: 2.0 + (0.8 if xx == x else 0) + (0.3 if xx == x + 1 else 0)
                - (0.8 if xx >= x + 6 else 0))
        for ry in range(3, h - 5, 5):
            cv.put(x + 3, ry, ramp, 4.0)
    cv.rect(0, h - 4, W - 1, h - 1, ramp, lambda xx, yy: [2.9, 2.4, 1.8, 0.8][yy - (h - 4)])
    for x in range(4, W, 11):
        cv.put(x, h - 3, ramp, 4.0)
        cv.put(x + 1, h - 2, ramp, 0.6)
    cv.hline(0, W - 1, h, ramp, 0.0)


def wall_plinth(cv, y0, y1, ramp=STONE):
    """Sòcol de pedra a peu de paret."""
    for y in range(y0, y1 + 1):
        for x in range(W):
            lvl = 2.0 + (hr(x // 29, 77) - 0.5) * 0.5 + (hr(x // 2, y, 78) - 0.5) * 0.2
            if (x // 29) != ((x + 1) // 29):
                lvl = 0.9
            if y == y0:
                lvl = 3.3
            elif y == y0 + 1:
                lvl = 2.8
            elif y == y1:
                lvl = 0.6
            cv.put(x, y, ramp, lvl)


def frame_diff(img, base, box=None):
    """Els píxels d'`img` que no són iguals que a `base` (i, si n'hi ha, dins `box`); la resta, transparent."""
    a, b = img.convert('RGB'), base.convert('RGB')
    d = ImageChops.difference(a, b).split()
    m = ImageChops.lighter(ImageChops.lighter(d[0], d[1]), d[2]).point(lambda v: 255 if v else 0)
    if box:
        keep = Image.new('L', m.size, 0)
        keep.paste(255, box)
        m = ImageChops.multiply(m, keep)
    fr = Image.new('RGBA', a.size, (0, 0, 0, 0))
    fr.paste(a.convert('RGBA'), mask=m)
    return fr


# ─── Sala de calderes ───────────────────────────────────────────────────────

def fire_tint(x, y):
    """Quant tenyeix el foc de taronja (0..1)."""
    d = math.hypot(x - FIRE_X, (y - FIRE_Y) * 1.1)
    return max(0.0, 1 - d / 307) ** 1.8


def nx_hot(x, y):
    """Els trossos de carbó de la banda del foc tenen el cantell vermellós."""
    return x > 112 and hr(int(x), int(y), 4) > 0.6


def soot(x, y):
    """Sutge damunt la caldera i a la part alta de la paret."""
    s = 0.0
    if y < 53:
        s -= (53 - y) / 53 * 0.7
    d = math.hypot((x - 171) / 1.4, y - 27)
    if d < 93:
        s -= (1 - d / 93) * 0.8
    return s


# Boca del foc: placa de ferro colat amb arc
FX0, FX1, FY0, FY1 = 141, 200, 179, 207
MCX = (FX0 + FX1) / 2
CX, HALF = 171, 63


def in_mouth(x, y, m=0):
    if not (FX0 - m <= x <= FX1 + m and FY0 - m <= y <= FY1):
        return False
    ay = FY0 + 9
    if y < ay:
        return ((x - MCX) / ((FX1 - FX0) / 2 + m)) ** 2 + ((y - ay) / (9 + m)) ** 2 <= 1
    return True


def back(cv):
    """El fons quiet que no canvia mai: sostre, paret, terra, la porta del magatzem i la caldera amb el fogar."""
    # ─── Sostre i paret ───────────────────────────────────────────────────────
    ceiling(cv)
    brick_wall(cv, 0, 19, W - 1, 202, seed=11, base=1.5, extra=soot)
    wall_plinth(cv, 203, 210)
    stone_floor(cv, FLOOR_Y, extra=lambda x, y: -0.3)

    # canonades del sostre
    pipe_h(cv, 0, W - 1, 21, 7, COPPER, 2.2, flange_every=85)
    pipe_h(cv, 248, W - 1, 33, 5, IRON, 2.4, flange_every=64, seed=8)
    for x in range(27, W, 85):
        bracket(cv, x, 28)
    # gotera de rovell sota una brida
    for y in range(39, 93):
        if hr(y, 9) > 0.25:
            cv.put(344, y, RUST, 2.2 - (y - 39) / 40, 0.6)
        if y < 67 and hr(y, 7) > 0.5:
            cv.put(345, y, RUST, 1.6, 0.6)
        if y < 50 and hr(y, 6) > 0.6:
            cv.put(343, y, RUST, 1.2, 0.6)
    cv.put(344, 93, RUST, 3.0, 0.6)                                       # la gota que penja

    # ─── Porta del magatzem (11..77 × 87..207) ────────────────────────────────
    cv.rect(7, 79, 81, 86, STONE, lambda x, y: [3.6, 3.2, 3.0, 2.6, 2.4, 2.2, 2.0, 0.8][y - 79] + (hr(x // 4, 79) - 0.5) * 0.3)
    for x in range(7, 82, 15):                                          # els junts de la llinda
        cv.vline(x, 80, 85, STONE, 1.2)
    plank_door(cv, 11, 87, 77, 207, base=2.2)
    cv.rect(28, 99, 60, 109, ENAMEL, lambda x, y: 3.8 if 28 < x < 60 and 99 < y < 109 else 1.6, 0.6)
    cv.put(30, 101, IRON, 1.0, 0.4); cv.put(58, 101, IRON, 1.0, 0.4)
    cv.put(30, 107, IRON, 1.0, 0.4); cv.put(58, 107, IRON, 1.0, 0.4)
    text(cv, 44 - text_w('EINES') // 2, 101, 'EINES', IRON, 1.0, 0)

    # ─── Caldera gran ────────────────────────────────────────────────────────
    BODY_T, BODY_B = 61, 171
    # tub de sortida cap al sostre
    pipe_v(cv, 163, 27, 45, 16, COPPER, 2.4, flange_every=0)
    cv.rect(159, 40, 181, 44, COPPER, lambda x, y: 3.8 - (y - 40) * 0.5 - (x - 159) * 0.04)
    cv.rect(159, 25, 181, 28, COPPER, lambda x, y: 3.6 - (y - 25) * 0.7)
    for x in range(161, 181, 5):
        cv.put(x, 42, IRON, 4.0)

    # cos cilíndric: llum clau des de l'esquerra-davant, cantó dret a l'ombra
    def cyl(nx):
        return 0.1 + 2.9 * max(0.0, math.cos((nx + 0.3) * 1.45)) ** 0.9

    BL = 0.42                                                  # quant li arriba la llum de la sala
    for y in range(BODY_T - 19, BODY_B + 1):
        for x in range(CX - HALF, CX + HALF + 1):
            nx = (x - CX) / HALF
            if y < BODY_T:
                ny = (y - BODY_T) / 19
                if nx * nx + ny * ny > 1:
                    continue
                lvl = cyl(nx) * 0.75 + (ny + 1) * 0.5 - 0.3
                if -0.5 < nx < -0.3 and ny > -0.6:
                    lvl += 0.7
            else:
                lvl = cyl(nx)
                if -0.45 < nx < -0.37:
                    lvl += 1.1                                       # reflex vertical
                elif -0.52 < nx < -0.3:
                    lvl += 0.45
                lvl += (y - BODY_T) / (BODY_B - BODY_T) * 0.5       # el foc il·lumina de baix
                if hr(x // 3, y // 4, 2) > 0.95:
                    lvl -= 0.7                                       # pàtina
                elif hr(x // 2, y // 3, 12) > 0.97:
                    lvl += 0.5                                       # un tros fregat
                if abs(nx - 0.1) < 0.009 or abs(nx - 0.62) < 0.009:
                    lvl -= 0.9                                       # junta de planxes
            cv.put(x, y, COPPER, lvl, BL)
    # verdet: una mica de pàtina verda que regalima sota les juntes
    for jx in (0.1, 0.62):
        x0 = round(CX + jx * HALF) + 1
        for y in range(BODY_T + 6, BODY_B - 4):
            if hr(y // 3, jx * 10, 4) > 0.82:
                cv.flat(x0, y, mix(cv.P[x0, y], (70, 120, 96), 0.35))
    # reblons a les juntes verticals
    for jx in (0.1, 0.62):
        x = round(CX + jx * HALF) + 3
        for y in range(BODY_T + 5, BODY_B - 3, 7):
            cv.put(x, y, COPPER, cyl(jx) + 1.6, BL)
            cv.put(x + 1, y, COPPER, cyl(jx) + 0.6, BL)
            cv.put(x, y + 1, COPPER, cyl(jx) - 0.8, BL)
            cv.put(x + 1, y + 1, COPPER, cyl(jx) - 1.2, BL)
    # vora de la cúpula
    for x in range(CX - HALF, CX + HALF + 1):
        nx = (x - CX) / HALF
        yy = BODY_T + round(math.sqrt(max(0, 1 - nx * nx)) * 4)
        cv.put(x, yy, COPPER, cyl(nx) + 1.2, BL)
        cv.put(x, yy + 1, COPPER, cyl(nx) + 0.3, BL)
        cv.put(x, yy + 2, COPPER, cyl(nx) - 1.2, BL)
    # anelles reblades (corbes per la perspectiva)
    for by in (91, 123, 155):
        for x in range(CX - HALF, CX + HALF + 1):
            nx = (x - CX) / HALF
            yy = by + round(math.sqrt(max(0, 1 - nx * nx)) * 4)
            for k in range(5):
                cv.put(x, yy + k, COPPER, cyl(nx) + [1.1, 0.5, 0.0, -0.4, -1.6][k], BL)
            if (x - CX + 200) % 6 == 0 and abs(nx) < 0.95:
                cv.put(x, yy + 2, COPPER, cyl(nx) + 1.8, BL)
                cv.put(x, yy + 3, COPPER, cyl(nx) - 1.0, BL)
    # vores fosques del cilindre (silueta)
    for y in range(BODY_T, BODY_B + 1):
        cv.put(CX - HALF, y, COPPER, 0.6, BL)
        cv.put(CX + HALF, y, COPPER, -1, 0)
        cv.put(CX + HALF - 1, y, COPPER, 0.2, BL)
    # placa del fabricant, amb quatre cargols
    cv.rect(144, 133, 197, 145, GOLD, lambda x, y: 3.4 + (0.4 if y == 134 else 0) if 144 < x < 197 and 133 < y < 145 else 1.4)
    for px, py in ((146, 135), (195, 135), (146, 143), (195, 143)):
        cv.put(px, py, GOLD, 5.0)
    text(cv, 171 - text_w('ALDAIA') // 2, 136, 'ALDAIA', GOLD, 1.0, 0.4)
    # manòmetre gran al mig, amb l'agulla a tocar del vermell
    cv.rect(168, 95, 174, 104, COPPER, lambda x, y: 3.4 - (x - 168) * 0.4)
    gauge(cv, 171, 109, 13, 72)
    # nivell d'aigua: tub de vidre al costat
    for y in range(75, 128):
        for x in (207, 208, 209, 210):
            if y > 99:
                cv.put(x, y, STEAM, 1.6 + (0.8 if x == 207 else 0) + (0.6 if x == 208 and y % 7 == 0 else 0), 0.4)   # aigua
            else:
                cv.put(x, y, STEAM, 0.6 + (1.8 if x == 207 else 0), 0.4)
        cv.put(206, y, GOLD, 2.0)
        cv.put(211, y, GOLD, 1.0)
    cv.rect(205, 72, 212, 75, GOLD, lambda x, y: 3.6 - (y - 72) * 0.3)
    cv.rect(205, 128, 212, 131, GOLD, lambda x, y: 2.8 - (y - 128) * 0.3)
    cv.hline(207, 210, 99, STEAM, 4.6, 0.3)
    cv.put(208, 103, STEAM, 4.0, 0.3)                                   # una bombolla
    # vàlvula de seguretat i xiulet, a dalt a la dreta
    pipe_v(cv, 200, 35, 53, 5, GOLD, 2.4)
    cv.rect(196, 32, 208, 36, GOLD, lambda x, y: 4.2 - (y - 32) * 0.7)
    cv.disc(203, 29, 4, 2.7, GOLD, lambda nx, ny: 4.0 - nx - ny)
    cv.put(201, 28, GOLD, 5.4)

    # ─── Fogar: base de maó refractari i la boca del foc ──────────────────────
    BX0, BX1, BT = 99, 243, 172
    cv.rect(BX0 - 3, BT, BX1 + 3, BT + 3, IRON, lambda x, y: [3.2, 2.6, 2.0, 0.8][y - BT])
    for x in range(BX0, BX1, 9):
        cv.put(x, BT + 1, IRON, 4.2)
    brick_wall(cv, BX0, BT + 4, BX1, 210, seed=12, base=2.4,
               extra=lambda x, y: -0.9 * (abs(x - CX) / 72) ** 2)
    cv.vline(BX0, BT + 4, 210, BRICK, 1.0)
    cv.vline(BX1, BT + 4, 210, BRICK, 0.4)
    # placa de ferro colat al voltant de la boca, amb arc
    for y in range(FY0 - 9, FY1 + 3):
        for x in range(FX0 - 9, FX1 + 10):
            if in_mouth(x, y, 8) and not in_mouth(x, y, 0):
                inner = in_mouth(x, y, 3)
                lvl = 2.2 + (1.4 if inner else 0) - (x - FX0) / 80 + (hr(x // 2, y // 2, 13) - 0.5) * 0.3
                if not in_mouth(x, y, 7):
                    lvl = 0.6
                elif not in_mouth(x, y, 6):
                    lvl += 0.5                                       # el cantell de la placa
                cv.put(x, y, IRON, lvl, 0.35)
    for a in range(195, 346, 15):                              # reblons de l'arc
        rx = round(MCX + math.cos(math.radians(a)) * 35)
        ry = round(FY0 + 9 + math.sin(math.radians(a)) * 16)
        cv.put(rx, ry, IRON, 4.8, 0.3)
        cv.put(rx + 1, ry + 1, IRON, 1.2, 0.3)


def fire(cv, tt):
    """La boca del foc al moment tt (0..1): flames, brases, la graella, la resplendor i les guspires."""
    ph = 2 * math.pi * tt
    for y in range(FY0, FY1 + 1):
        for x in range(FX0, FX1 + 1):
            if not in_mouth(x, y):
                continue
            t = (y - FY0) / (FY1 - FY0)                            # 0 dalt, 1 baix
            u = (x - FX0) / (FX1 - FX0)
            flame = math.sin(u * 19 + 1.3 - ph * 3) * 0.5 + math.sin(u * 7.3 + ph) * 0.6 + math.sin(u * 31 - ph * 5) * 0.25
            lvl = 0.6 + t * 4.4 + flame * (1 - t) * 1.8 - abs(u - 0.5) * 1.8
            lvl += (math.sin(u * 53 + y * 0.9 - ph * 4) * 0.2) * (1 - t)            # llengües primes
            if y >= FY1 - 4:
                lvl = 4.6 + (hr(x // 2, y) - 0.5) * 2.4 + 0.5 * (math.sin(ph + hr(x // 2, y, 5) * 6.3) - math.sin(hr(x // 2, y, 5) * 6.3))  # brases
                if hr(x // 3, 77) > 0.7 and y <= FY1 - 3:
                    lvl -= 2.6                                         # carbó encara negre
            cv.put(x, y, FIRE, lvl, 0)
    # graella
    for x in range(FX0 + 4, FX1, 7):
        cv.vline(x, FY1 - 5, FY1 - 4, IRON, 0.8, 0)
    cv.hline(FX0, FX1, FY1 + 1, IRON, 1.2, 0.3)
    cv.hline(FX0, FX1, FY1 + 2, IRON, 0.5, 0.3)
    # resplendor
    cv.glow(MCX, FY1 - 5, 59, (255, 150, 60), 0.5 + 0.03 * math.sin(ph * 3) + 0.03 * math.sin(ph * 5 + 1))
    cv.glow(MCX, FY1 - 3, 29, (255, 210, 120), 0.45)
    # guspires
    sp = random.Random(9)
    for _ in range(18):
        x = sp.uniform(FX0 + 10, FX1 - 10)
        y = FY0 + 1 + (sp.uniform(0, 11) - tt * 22) % 11                  # pugen poc a poc
        cv.flat(x, y, (255, 220, 120) if sp.random() > 0.4 else (255, 150, 60))


def coal_and_shovel(cv):
    """La pila de carbó al terra, davant la base, i la pala clavada."""
    coal = random.Random(3)
    for _ in range(300):
        t = coal.random()
        cx = 80 + t * 45 + coal.uniform(-1, 1)
        hgt = max(0.0, 1 - abs(t - 0.4) * 2.2) * 19
        cy = 221 - coal.random() * hgt - coal.random() * 3
        r = coal.uniform(1.7, 3.4)
        cv.disc(cx, cy, r, r * 0.75, COAL, lambda nx, ny: 1.6 - nx * 0.4 - ny * 1.0 + (1.6 if nx > 0.2 and ny < -0.2 else 0), 0.6)
        if r > 2.4 and coal.random() > 0.6:
            cv.put(round(cx - r * 0.3), round(cy - r * 0.4), COAL, 4.2, 0.4)           # la cara llisa que brilla
        if nx_hot(cx, cy):
            cv.put(round(cx + r * 0.5), round(cy - r * 0.4), FIRE, 2.6, 0)
    # trossets escampats per terra
    for i in range(14):
        x, y = 70 + hr(i, 31) * 70, 218 + hr(i, 32) * 7
        cv.disc(x, y, 1.2, 0.9, COAL, 1.6, 0.6)
    # pala clavada al carbó: mànec de fusta, puny i fulla de ferro
    for i in range(59):
        x, y = 115 + i * 0.25, 213 - i
        cv.put(round(x) - 1, round(y), WALNUT, 3.8, 0.6)
        cv.put(round(x), round(y), WALNUT, 2.8, 0.6)
        cv.put(round(x) + 1, round(y), WALNUT, 1.6, 0.6)
    cv.rect(126, 151, 134, 154, WALNUT, lambda x, y: 3.4 - (y - 151) * 0.5, 0.6)
    cv.rect(119, 205, 123, 209, IRON, 2.6, 0.5)                                      # el coll de la fulla
    cv.poly([(107, 210), (122, 210), (120, 221), (109, 221)], IRON, lambda x, y: 2.0 + (x - 107) * 0.1 + (0.6 if y == 210 else 0), 0.5)
    contact_shadow(cv, 77, 128, 221, 5, 0.8)


def front(cv, alarm=False):
    """El que hi ha de la caldera cap a la dreta: la vàlvula, el tauler, la porta del moll, el rellotge,
    els manòmetres, la porta de la cambra amb l'alarma i l'escriptori del capatàs."""
    # ─── Canonada amb vàlvula (entre la caldera i el tauler) ──────────────────
    pipe_v(cv, 248, 28, 160, 8, COPPER, 2.2, flange_every=51)
    for y in range(155, 166):                                     # colze cap a la caldera
        cv.rect(235, y, 255, y, COPPER, 2.4 - abs(y - 160) * 0.4 + (0.3 if y == 157 else 0))
    for yb in (53, 187):
        bracket(cv, 247, yb, 11)
    # volant de la vàlvula
    VX, VY = 252, 128
    cv.ring(VX, VY, 11, RED, 3.2, step=2)
    cv.ring(VX, VY, 10, RED, 2.4, step=2)
    cv.ring(VX, VY, 9, RED, 1.4, step=2)
    for a in (0, 60, 120):
        for i in range(-9, 10):
            cv.put(round(VX + math.cos(math.radians(a)) * i), round(VY + math.sin(math.radians(a)) * i), RED, 2.6)
    cv.disc(VX, VY, 2.7, 2.7, IRON, lambda nx, ny: 3.8 - nx - ny)
    # manòmetre petit damunt
    gauge(cv, 252, 96, 8, -30)

    # ─── Tauler d'anuncis (267..373 × 44..107) ────────────────────────────────
    TX0, TY0, TX1, TY1 = 267, 44, 373, 107
    cv.rect(TX0, TY0, TX1, TY1, WALNUT, lambda x, y: 3.4 if (x - TX0 < 3 or y - TY0 < 3) else (1.2 if (TX1 - x < 3 or TY1 - y < 3) else 2.6))
    cv.rect(TX0 + 4, TY0 + 4, TX1 - 4, TY1 - 4, CORK, lambda x, y: 2.6 + (hr(x, y, 4) - 0.5) * 0.9 - (0.8 if y == TY0 + 4 or x == TX0 + 4 else 0))
    for x, y in ((TX0 + 1, TY0 + 1), (TX1 - 1, TY0 + 1), (TX0 + 1, TY1 - 1), (TX1 - 1, TY1 - 1)):
        cv.put(x, y, GOLD, 4.0)
    # forats de xinxetes velles
    for i in range(12):
        cv.put(TX0 + 6 + int(hr(i, 61) * (TX1 - TX0 - 12)), TY0 + 6 + int(hr(i, 62) * (TY1 - TY0 - 12)), CORK, 0.4)
    contact_shadow(cv, TX0, TX1, TY1 + 1, 4, 0.8)

    def note(x0, y0, x1, y1, ramp=PAPER, lvl=3.6, lines=True, pin=(170, 36, 36), tilt=0):
        # ombra
        for y in range(y0 + 1, y1 + 3):
            for x in range(x0 + 1, x1 + 3):
                if cv.get(x, y)[3]:
                    o = cv.P[x, y]
                    cv.P[x, y] = tuple(int(c * 0.6) for c in o[:3]) + (255,)
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                l = lvl - (y - y0) / (y1 - y0 + 1) * 0.5
                if y == y1 and hr(x, 3) > 0.6:
                    l -= 0.8                                       # punta arrissada
                if x == x1 and hr(y, 4) > 0.7:
                    l -= 0.5
                cv.put(x, y + (round((x - x0) * tilt)), ramp, l)
        if lines:
            r = random.Random(x0 * 7 + y0)
            for ly in range(y0 + 5, y1 - 1, 3):
                e = x1 - 2 - r.randint(0, 6)
                for x in range(x0 + 2, e):
                    if r.random() > 0.15:
                        cv.put(x, ly + round((x - x0) * tilt), ramp, lvl - 2.2)
        if pin:
            cx = (x0 + x1) // 2
            cv.flat(cx, y0 + 1, pin)
            cv.flat(cx + 1, y0 + 1, mix(pin, (255, 255, 255), 0.4))
            cv.flat(cx, y0 + 2, mix(pin, (0, 0, 0), 0.5))
            cv.flat(cx + 1, y0 + 2, mix(pin, (0, 0, 0), 0.3))

    # avís gran: «RECORDEU ... 27-B»
    note(273, 49, 327, 81, PAPER, 4.0, lines=False)
    text(cv, 300 - text_w('RECORDEU') // 2, 54, 'RECORDEU', RED, 3.0, 0.4)
    for ly in (64, 68, 72):
        for x in range(277, 324):
            if hr(x // 3, ly) > 0.25 and x % 4 != 3:
                cv.put(x, ly, PAPER, 1.6)
    text(cv, 322 - text_w('27-B'), 74, '27-B', RED, 2.8, 0.4)
    note(332, 49, 351, 73, MANILA, 4.0)
    note(355, 52, 368, 67, PAPER, 3.6, tilt=0.1)
    note(273, 87, 296, 101, PAPER, 3.4, pin=(40, 90, 170))
    note(301, 85, 325, 100, MANILA, 3.2, pin=(40, 140, 60))
    # retrat-cartell de «treballador del mes» (el Cargol, és clar)
    note(332, 79, 348, 99, PAPER, 3.8, lines=False, pin=(200, 160, 40))
    cv.rect(335, 83, 345, 92, IRON, lambda x, y: 2.4 + (0.6 if y == 83 else 0), 0.4)
    cv.rect(337, 85, 343, 89, IRON, 4.0, 0.4)
    cv.flat(338, 86, (90, 220, 150)); cv.flat(342, 86, (90, 220, 150))
    cv.hline(339, 341, 88, IRON, 2.0, 0.4)
    cv.vline(336, 79, 82, IRON, 3.0, 0.4); cv.vline(344, 79, 82, IRON, 3.0, 0.4)
    cv.put(336, 79, IRON, 4.6, 0.4); cv.put(344, 79, IRON, 4.6, 0.4)
    for x in range(335, 346):
        if x % 2:
            cv.put(x, 96, PAPER, 1.8)
    # safata de filferro amb la pila de formularis 27-B
    for i in range(8):
        y = 104 - i
        cv.rect(352 + (i % 2), y, 372 + (i % 2), y, PAPER, 4.2 - (0.9 if i % 2 else 0), 0.5)
    cv.hline(352, 372, 105, PAPER, 2.0, 0.5)
    note(353, 83, 372, 92, MANILA, 4.2, lines=False, pin=None)
    text(cv, 355, 85, '27-B', IRON, 0.6, 0.2)
    cv.rect(349, 105, 376, 108, IRON, lambda x, y: 3.2 - (y - 105) * 0.7)
    cv.vline(349, 93, 108, IRON, 3.0)
    cv.vline(376, 93, 108, IRON, 1.6)
    cv.put(350, 98, IRON, 4.0); cv.put(375, 98, IRON, 2.4)          # els caps del filferro

    # ─── Porta del moll de càrrega (276..368 × 112..207) ──────────────────────
    cv.rect(285, 115, 357, 125, ENAMEL, lambda x, y: 4.2 if 285 < x < 357 and 115 < y < 125 else 1.2, 0.6)
    text(cv, 321 - text_w('MOLL') // 2, 117, 'MOLL', NAVY_INK, 0, 0)
    cv.put(288, 117, IRON, 1.0); cv.put(354, 117, IRON, 1.0)
    cv.put(288, 122, IRON, 1.0); cv.put(354, 122, IRON, 1.0)
    # porta doble, més ampla, de taulons amb ferros
    cv.rect(276, 128, 367, 132, STONE, lambda x, y: [3.6, 3.2, 2.8, 2.2, 1.0][y - 128] + (hr(x // 5, 128) - 0.5) * 0.3)
    plank_door(cv, 279, 133, 364, 207, base=2.0, knob=False, frame=4)
    cv.vline(321, 137, 207, WALNUT, 0.4)
    cv.vline(322, 137, 207, WALNUT, 3.2)
    for yb in (149, 189):
        cv.rect(283, yb, 360, yb + 3, IRON, lambda x, y: 3.0 - (y - yb) * 0.7 + (hr(x // 4, yb, 2) > 0.85) * -0.6)
        for x in range(286, 360, 8):
            cv.put(x, yb + 1, IRON, 4.6)
            cv.put(x, yb + 2, IRON, 1.2)
    # forrellat
    cv.rect(312, 165, 332, 168, IRON, lambda x, y: 3.6 - (y - 165) * 0.8)
    cv.rect(327, 162, 330, 171, IRON, lambda x, y: 2.8 + (0.8 if x == 327 else 0))
    cv.rect(309, 163, 311, 170, IRON, 2.2)
    cv.disc(333.5, 166.5, 1.6, 1.6, IRON, 4.0)

    # ─── Rellotge de fàbrica, sobre l'escriptori (les 3 i 10 de la matinada) ──
    KX, KY = 416, 69
    cv.vline(KX, 35, 51, IRON, 2.0)
    cv.vline(KX + 1, 35, 51, IRON, 1.0)
    cv.disc(KX, KY, 17, 17, WALNUT, lambda nx, ny: 3.2 - nx - ny)
    cv.ring(KX, KY, 15.5, WALNUT, 1.4, step=2)
    cv.disc(KX, KY, 14, 14, PAPER, lambda nx, ny: 4.0 - ny * 0.7, 0.6)
    for h in range(12):
        a = math.radians(h * 30)
        cv.put(round(KX + math.sin(a) * 12), round(KY - math.cos(a) * 12), IRON, 0.6 if h % 3 else 0.0, 0)
        if h % 3 == 0:
            cv.put(round(KX + math.sin(a) * 11), round(KY - math.cos(a) * 11), IRON, 0.0, 0)
    for m in range(60):                                         # els minuts
        if m % 5:
            a = math.radians(m * 6)
            cv.put(round(KX + math.sin(a) * 12.6), round(KY - math.cos(a) * 12.6), PAPER, 2.4, 0.3)
    for i in range(8):                                          # agulla de les hores (les 3)
        cv.flat(KX + i, KY, (30, 22, 26))
        if 2 < i < 6:
            cv.flat(KX + i, KY - 1, (30, 22, 26))
    for i in range(11):                                         # minutera (10)
        a = math.radians(60)
        cv.flat(round(KX + math.sin(a) * i), round(KY - math.cos(a) * i), (30, 22, 26))
    cv.flat(KX, KY, (150, 30, 30))
    cv.disc(KX - 5, KY - 7, 2.7, 1.6, PAPER, 6.0, 0)              # reflex del vidre

    # ─── Manòmetres de la línia de vapor (dreta) ──────────────────────────────
    for gx, ang in ((504, -40), (525, 20), (547, 95)):
        pipe_v(cv, gx - 2, 39, 51, 4, IRON, 2.6)
        cv.rect(gx - 3, 49, gx + 2, 51, IRON, 3.0)
        gauge(cv, gx, 60, 8, ang)
    # fuita de vapor a la brida de la línia de ferro
    steam(cv, [(536, 40, 7, 0.9), (529, 32, 8, 0.7), (520, 25, 11, 0.5), (508, 21, 12, 0.3)], lit=0.5)

    # ─── Porta de la cambra de ressonància (563..629 × 88..207) ───────────────
    DX0, DY0, DX1, DY1 = 563, 88, 629, 207
    cv.rect(DX0, DY0, DX1, DY1, IRON, lambda x, y: 2.6 + (0.9 if x - DX0 < 3 or y - DY0 < 3 else 0) - (1.0 if DX1 - x < 3 else 0))
    # franja d'avís a la llinda
    for y in range(DY0 + 3, DY0 + 10):
        for x in range(DX0 + 3, DX1 - 2):
            if ((x + y) // 5) % 2:
                cv.put(x, y, WARN, 3.4 - (0.5 if y == DY0 + 9 else 0) - (0.8 if hr(x // 2, y, 21) > 0.9 else 0))
            else:
                cv.put(x, y, IRON, 0.6)
    # fulla de la porta, de planxa reblada
    LX0, LY0, LX1 = DX0 + 7, DY0 + 12, DX1 - 7
    for y in range(LY0, DY1 + 1):
        for x in range(LX0, LX1 + 1):
            u = (x - LX0) / (LX1 - LX0)
            lvl = 2.6 - u * 0.8 + (hr(x // 5, y // 5, 8) - 0.5) * 0.3 + (hr(x, y, 9) - 0.5) * 0.12
            if hr(x // 2, y // 3, 11) > 0.93:
                cv.put(x, y, RUST, 2.4 - (0.6 if hr(x, y, 12) > 0.6 else 0))
                continue
            cv.put(x, y, IRON, lvl)
    cv.vline(LX0, LY0, DY1, IRON, 0.4)
    cv.hline(LX0, LX1, LY0, IRON, 0.4)
    cv.vline(LX1, LY0, DY1, IRON, 3.0)
    for yb in (LY0 + 19, LY0 + 61, DY1 - 16):
        cv.rect(LX0 + 1, yb, LX1 - 1, yb + 3, IRON, lambda x, y: 3.6 - (y - yb) * 0.9)
        for x in range(LX0 + 4, LX1 - 1, 7):
            cv.put(x, yb + 1, IRON, 5.0)
            cv.put(x, yb + 2, IRON, 1.6)
    for y in range(LY0 + 5, DY1 - 2, 8):
        cv.put(LX0 + 3, y, IRON, 4.6)
        cv.put(LX1 - 3, y, IRON, 3.6)
    # placa de llautó i forrellat amb pany
    cv.rect(576, 120, 616, 131, GOLD, lambda x, y: 3.4 if 576 < x < 616 and 120 < y < 131 else 1.4, 0.6)
    cv.put(578, 122, GOLD, 5.0, 0.4); cv.put(614, 122, GOLD, 5.0, 0.4)
    text(cv, 596 - text_w('CAMBRA') // 2, 123, 'CAMBRA', GOLD, 0.8, 0.3)
    cv.rect(605, 149, 616, 168, IRON, lambda x, y: 3.6 - (x - 605) * 0.2)
    cv.rect(593, 155, 608, 159, IRON, lambda x, y: 4.0 - (y - 155) * 0.7)
    cv.rect(590, 154, 592, 160, IRON, 2.4)
    cv.vline(611, 159, 163, IRON, 0.0)
    cv.disc(611, 158, 1.3, 1.3, IRON, 0.0)
    # escaló de ferro
    cv.rect(DX0 - 3, DY1 + 1, DX1 + 3, DY1 + 3, IRON, lambda x, y: 3.4 - (y - DY1 - 1))
    for x in range(DX0, DX1 + 1, 6):
        cv.put(x, DY1 + 2, IRON, 1.0)                               # l'estriat de la planxa

    # ─── Llum d'alarma vermell (578..615 × 50..88) ────────────────────────────
    AX, AY = 596, 69
    cv.rect(588, 81, 604, 85, IRON, lambda x, y: 3.0 - (y - 81) * 0.5)         # base
    cv.put(590, 83, IRON, 4.6); cv.put(602, 83, IRON, 4.6)
    cv.rect(593, 77, 599, 81, IRON, 2.4)
    if alarm:
        cv.disc(AX, AY, 11, 11, RED, lambda nx, ny: 5.2 - math.hypot(nx + 0.3, ny + 0.4) * 2.6, 0)
        cv.disc(AX - 3, AY - 4, 3, 2.2, PINK_HOT, lambda nx, ny: 1 - (nx * nx + ny * ny) * 0.8, 0)
    else:                                                            # vidre vermell fosc, apagat
        cv.disc(AX, AY, 11, 11, RED, lambda nx, ny: 2.6 - math.hypot(nx + 0.3, ny + 0.4) * 1.6 - ny * 0.4, 0.4)
        cv.disc(AX - 4, AY - 5, 2.2, 1.6, RED, 3.6, 0.4)                       # reflex del foc al vidre
    for a in (-60, -20, 20, 60):                                     # gàbia
        for t in range(-11, 12):
            ang = math.radians(a)
            x = AX + math.sin(ang) * 11 * math.cos(t / 11 * 1.2)
            cv.put(round(x), AY + t, IRON, 1.2 if alarm else 1.0, 0 if alarm else 0.6)
    cv.hline(AX - 11, AX + 11, AY, IRON, 1.4 if alarm else 1.2, 0 if alarm else 0.6)
    cv.hline(AX - 10, AX + 10, AY + 6, IRON, 1.2 if alarm else 1.0, 0 if alarm else 0.6)
    cv.rect(AX - 4, AY - 15, AX + 4, AY - 11, IRON, lambda x, y: 3.0 - (y - AY + 15) * 0.4)
    if alarm:
        cv.glow(AX, AY, 56, (255, 60, 40), 0.55)
        cv.glow(AX, AY, 24, (255, 120, 90), 0.35)
    # cable de l'alarma que surt de la cambra
    for y in range(39, 55):
        cv.put(600, y, IRON, 1.6)
        cv.put(601, y, IRON, 0.8)

    # ─── Escriptori del capatàs (377..441), a tocar de la seva cadira ─────────
    QX0, QX1 = 377, 441
    contact_shadow(cv, QX0, QX1, 213, 16, 1.0)
    for x in (QX0 + 3, QX1 - 4):                                   # potes del darrere (més curtes)
        cv.rect(x + 4, 184, x + 5, 213, WALNUT, 1.2)
    for x in (QX0 + 1, QX1 - 4):                                   # potes del davant
        cv.rect(x, 184, x + 3, 224, WALNUT, lambda xx, yy: 2.8 - (xx - x) * 0.6)
        cv.rect(x - 1, 222, x + 4, 224, WALNUT, 1.6)                   # el peu
    cv.rect(QX0 + 4, 184, QX1 - 4, 191, WALNUT, lambda x, y: 2.4 - (y - 184) * 0.15 + (hr(x // 3, 71) - 0.5) * 0.25)    # faldó
    cv.hline(QX0 + 4, QX1 - 4, 191, WALNUT, 0.6)
    cv.rect(400, 185, 416, 189, WALNUT, lambda x, y: 3.4 + (0.6 if y == 185 else 0) - (1.2 if y == 189 else 0))  # calaixet
    cv.rect(407, 186, 409, 187, GOLD, 4.0)
    for y in range(173, 184):                                                 # tauler
        t = (y - 173) / 10
        for x in range(QX0 + 3 - round(t * 3), QX1 - 3 + round(t * 3) + 1):
            cv.put(x, y, WALNUT, 3.0 + t * 0.6 + (hr(x // 5, 61) - 0.5) * 0.4 + (hr(x, y // 3, 62) - 0.5) * 0.15)
    cv.hline(QX0, QX1, 183, WALNUT, 4.4)
    cv.hline(QX0, QX1, 184, WALNUT, 3.0)
    cv.hline(QX0 + 3, QX1 - 3, 173, WALNUT, 2.0)
    # diari plegat, amb les columnes
    for y in range(175, 181):
        for x in range(383 + (y - 175), 405 + (y - 175)):
            cv.put(x, y, PAPER, 3.6 - (0.9 if (x + y) % 5 == 0 else 0))
    cv.hline(384, 403, 175, PAPER, 4.6)
    for x in range(386, 402, 2):
        cv.put(x + 2, 177, PAPER, 2.0)
    # tassa de cafè (freda)
    cv.rect(408, 167, 415, 176, PAPER, lambda x, y: 4.2 - (x - 408) * 0.35)
    cv.hline(408, 415, 167, IRON, 1.0)
    cv.hline(409, 414, 168, WALNUT, 0.6)                            # el cafè
    cv.ring(417.5, 171, 2.6, PAPER, 3.0, step=20)
    cv.disc(411.5, 177, 6, 1.4, PAPER, 3.0)
    # llum de flexo de ferro amb pantalla verda
    cv.disc(429, 180, 7, 2.2, IRON, lambda nx, ny: 3.4 - nx - ny)
    for i in range(24):
        cv.put(429 + round(math.sin(i / 8) * 3), 179 - i, IRON, 3.0)
        cv.put(430 + round(math.sin(i / 8) * 3), 179 - i, IRON, 1.6)
    for y in range(147, 156):
        t = (y - 147) / 8
        half = 5 + t * 7
        for x in range(round(428 - half), round(428 + half) + 1):
            u = (x - 428) / half
            cv.put(x, y, LAMPG, 3.0 - u * 1.4 - (1 - t) * 0.6 + (1.2 if y == 148 and u < -0.2 else 0), 0.3)
    cv.hline(417, 440, 156, [(255, 236, 170)], 0, 0)
    cv.glow(428, 161, 35, (255, 226, 150), 0.5)


def puffs(cv, tt):
    """El vapor que s'escapa (vàlvula de seguretat, brida del tub), al moment tt del cicle."""
    steam(cv, drift([(209, 27, 5, 0.9), (216, 20, 8, 0.75), (227, 16, 11, 0.55), (241, 15, 13, 0.35)], (tt * 2) % 1), lit=0.6)
    steam(cv, drift([(257, 79, 4, 0.8), (265, 73, 7, 0.6), (276, 68, 8, 0.35)], (tt * 2 + 0.5) % 1), lit=0.6)


def fire_light(cv, tt):
    """La llum del foc: to taronja a tota la meitat esquerra i el reflex al terra, davant la boca."""
    ph = 2 * math.pi * tt
    cv.tint(0, 0, W - 1, 273, (255, 140, 60), lambda x, y: fire_tint(x, y) * 0.14)
    for y in range(FLOOR_Y, 267):
        for x in range(80, 268):
            d = math.hypot((x - FIRE_X) / 2.4, (y - FLOOR_Y) * 0.9)
            a = max(0, 1 - d / 48) ** 1.3 * (0.7 + 0.04 * math.sin(ph * 3) + 0.03 * math.sin(ph * 5 + 1))
            if a > B4[y & 3][x & 3] * 0.7:
                o = cv.P[x, y]
                cv.P[x, y] = mix(o, (255, 170, 80), a * 0.6) + (255,)


def bg(cv, alarm=False, t=0.0):
    """t (0..1): moment del cicle d'animació del foc i el vapor (0 = el fons quiet)."""
    cv.img.paste(_room(alarm, t))


def _rest(cv, alarm, t):
    fire(cv, t)
    coal_and_shovel(cv)
    front(cv, alarm)
    puffs(cv, t)
    fire_light(cv, t)


@lru_cache(maxsize=None)
def _back(alarm=False):
    cv = Canvas(light=LIGHT_ALARM if alarm else LIGHT)
    back(cv)
    return cv.img


@lru_cache(maxsize=None)
def _room(alarm=False, t=0.0):
    """La sala sencera al moment t, a partir del fons quiet de darrere (que no es torna a dibuixar)."""
    lt = LIGHT_ALARM if alarm else LIGHT
    cv = Canvas(light=lt, img=_back(alarm).copy())
    _rest(cv, alarm, t)
    return cv.img


def segell(cv):
    """El segell oficial, dret a terra (403..440 × 225..255): pom de fusta, coll de llautó i base amb goma vermella."""
    SX = 420
    # empremta vermella al terra, de quan ha caigut
    for y in range(248, 254):
        for x in range(429, 441):
            if (x in (429, 440) or y in (248, 253)) and hr(x, y, 2) > 0.2:
                cv.put(x, y, RED, 2.2, 0.3)
    for x, y in ((433, 251), (434, 250), (436, 251), (437, 250)):
        cv.put(x, y, RED, 2.0, 0.3)
    contact_shadow(cv, SX - 12, SX + 9, 248, 5, 1.0)
    # base: bloc de fusta amb la goma vermella a sota
    for y in range(237, 247):
        for x in range(SX - 12, SX + 11):
            lvl = 2.8 - (x - SX + 12) / 22 * 1.4 + (0.9 if y == 237 else 0) + (hr(x // 2, 71) - 0.5) * 0.25
            cv.put(x, y, WALNUT, lvl, 0.5)
    cv.vline(SX - 12, 237, 246, WALNUT, 4.0, 0.5)
    cv.vline(SX + 10, 238, 246, WALNUT, 1.0, 0.5)
    cv.rect(SX - 12, 247, SX + 10, 249, RED, lambda x, y: 3.4 - (y - 247) * 0.9 - (x - SX + 12) * 0.04, 0.5)
    # placa de llautó del davant, amb el número gravat
    cv.rect(SX - 8, 240, SX + 6, 244, GOLD, lambda x, y: 3.8 - (x - SX + 8) * 0.12 + (0.6 if y == 240 else 0), 0.5)
    for x in range(SX - 6, SX + 5):
        if x % 3:
            cv.put(x, 242, GOLD, 1.4, 0.3)
    # coll de llautó
    cv.rect(SX - 3, 232, SX + 2, 236, GOLD, lambda x, y: 4.2 - (x - SX + 3) * 0.6, 0.5)
    cv.hline(SX - 4, SX + 3, 236, GOLD, 2.0, 0.5)
    cv.hline(SX - 3, SX + 2, 232, GOLD, 4.6, 0.5)
    # pom de fusta envernissada
    cv.disc(SX - 0.5, 227, 5.6, 5.6, WALNUT, lambda nx, ny: 3.8 - nx * 1.6 - ny * 1.6, 0.5)
    cv.put(SX - 3, 224, PAPER, 4.0, 0.3)
    cv.put(SX - 2, 224, PAPER, 3.0, 0.3)
    outline(cv, 400, 213, 443, 247)
    cv.glow(SX, 237, 19, (255, 220, 150), 0.1)


def alarma_encesa(cv):
    """El llum d'alarma encès: es renderitza la sala amb i sense alarma i es copia el que canvia
    al voltant del llum (vidre, gàbia, halo vermell i la paret que tenyeix)."""
    fr = frame_diff(_room(True), _room(False), (507, 0, W, 160))
    cv.img.alpha_composite(fr)


PROPS = {'segell': segell, 'alarma_encesa': alarma_encesa}


# Animació de fons: el foc respira, les guspires pugen i el vapor s'escampa. Cada fotograma només
# té els píxels que canvien respecte del fons quiet (t = 0).
def _ambient_frames(n=16):
    base = _room()
    return [frame_diff(_room(False, i / n), base) for i in range(n)]


ANIMS = {'ambient': {'frames': _ambient_frames, 'frameDuration': 110}}
