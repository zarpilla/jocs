"""
Sala de calderes (Acte 1-3, Iri): maó socarrimat, coure, vapor i el foc de la caldera gran.
Llums: la boca del foc (la gran font, taronja), el llum d'alarma vermell de la cambra i el llum
d'escriptori del capatàs.

També hi ha les peces comunes de les sales de la fàbrica (paret de maó, terres, portes, manòmetres,
vapor i lletres petites), que fa servir el magatzem.
"""
import math
import random

from hd.pix import (Canvas, Light, B4, W, H, hr, mix, WALNUT, FLOOR, GOLD, COPPER, RUST, BRICK, IRON, FIRE, RED,
                    PAPER, MANILA, SMOKE, LAMPG, WARN, GRAY, SIL)

# ─── Rampes pròpies de la fàbrica ───────────────────────────────────────────
STONE = [(14, 10, 16), (28, 22, 28), (44, 36, 40), (62, 52, 54), (84, 70, 68), (108, 92, 84), (136, 118, 102), (168, 148, 124)]
STEAM = [(64, 56, 66), (100, 92, 98), (138, 128, 130), (176, 168, 164), (212, 206, 198), (238, 234, 226)]
CORK = [(40, 24, 18), (72, 46, 30), (104, 72, 44), (138, 100, 62), (170, 130, 84), (200, 162, 110)]
COAL = [(8, 6, 10), (18, 14, 20), (30, 26, 32), (48, 42, 48), (74, 64, 66)]
ENAMEL = [(30, 34, 40), (70, 76, 80), (130, 132, 126), (186, 184, 170), (226, 222, 204), (246, 244, 232)]

FIRE_X, FIRE_Y = 128, 146



def make_light(alarm=False):
    lt = Light(vignette=(70, 40), floor_fade=(198, 40))
    lt.point(FIRE_X, FIRE_Y - 4, r=230, k=3.4, squash=0.95, power=2.0)     # la boca del foc
    if alarm:
        lt.point(447, 54, r=62, k=1.5, power=1.8)                           # alarma vermella
    lt.point(322, 116, r=70, k=1.7, squash=1.2, down=True)              # llum del capatàs
    return lt


# el fons té l'alarma apagada; el prop alarma_encesa hi posa el llum i el seu halo
LIGHT = make_light()
LIGHT_ALARM = make_light(alarm=True)

FLOOR_Y = 158


# ─── Lletres petites (3×5) per a rètols ─────────────────────────────────────
FONT = {
    'A': ['.#.', '#.#', '###', '#.#', '#.#'], 'B': ['##.', '#.#', '##.', '#.#', '##.'],
    'C': ['.##', '#..', '#..', '#..', '.##'], 'D': ['##.', '#.#', '#.#', '#.#', '##.'],
    'E': ['###', '#..', '##.', '#..', '###'], 'F': ['###', '#..', '##.', '#..', '#..'],
    'G': ['.##', '#..', '#.#', '#.#', '.##'], 'I': ['###', '.#.', '.#.', '.#.', '###'],
    'L': ['#..', '#..', '#..', '#..', '###'], 'M': ['#...#', '##.##', '#.#.#', '#...#', '#...#'], 'W': ['#...#', '#...#', '#.#.#', '##.##', '#...#'],
    'N': ['##.', '#.#', '#.#', '#.#', '#.#'], 'O': ['.#.', '#.#', '#.#', '#.#', '.#.'],
    'P': ['##.', '#.#', '##.', '#..', '#..'], 'R': ['##.', '#.#', '##.', '#.#', '#.#'],
    'S': ['.##', '#..', '.#.', '..#', '##.'], 'T': ['###', '.#.', '.#.', '.#.', '.#.'],
    'U': ['#.#', '#.#', '#.#', '#.#', '###'], 'Z': ['###', '..#', '.#.', '#..', '###'],
    'X': ['#.#', '#.#', '.#.', '#.#', '#.#'], 'H': ['#.#', '#.#', '###', '#.#', '#.#'],
    'V': ['#.#', '#.#', '#.#', '#.#', '.#.'], 'K': ['#.#', '#.#', '##.', '#.#', '#.#'], '2': ['##.', '..#', '.#.', '#..', '###'],
    '7': ['###', '..#', '.#.', '.#.', '.#.'], '9': ['.#.', '#.#', '.##', '..#', '.#.'],
    '1': ['.#.', '##.', '.#.', '.#.', '###'], '-': ['...', '...', '###', '...', '...'],
    '!': ['.#.', '.#.', '.#.', '...', '.#.'], ' ': ['...', '...', '...', '...', '...'],
    '.': ['...', '...', '...', '...', '.#.'], '«': ['...', '...', '...', '...', '...'],
}


def text(cv, x, y, s, ramp, lvl, lit=0.6):
    """Escriu en lletra de 3×5 (amb un píxel d'espai)."""
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
    """Paret de maó (14×6), amb llagues fosques, cantell superior clar i taques de sutge."""
    for y in range(y0, y1 + 1):
        row = (y - y0) // 6
        ry = (y - y0) % 6
        off = 7 if row % 2 else 0
        for x in range(x0, x1 + 1):
            bx = (x + off) // 14
            rx = (x + off) % 14
            if ry == 5 or rx == 13:
                lvl = base - 1.2                                    # llaga de morter
                if ry == 5 and rx == 13:
                    lvl -= 0.2
            else:
                n = hr(bx, row, seed)
                lvl = base + (n - 0.5) * 0.7
                if n > 0.93:
                    lvl -= 0.7                                      # maó cremat
                if ry == 0:
                    lvl += 0.45
                elif ry == 4:
                    lvl -= 0.3
                if rx == 0:
                    lvl += 0.2
                if hr(x, y, seed) > 0.97:
                    lvl -= 0.5                                      # porus
            if extra:
                lvl += extra(x, y)
            cv.put(x, y, BRICK, lvl)


def stone_floor(cv, y0, y1=H - 1, extra=None, vpx=240):
    """Terra de lloses grans en perspectiva."""
    VPY = -150
    for y in range(y0, y1 + 1):
        dep = y - VPY
        z = 3600 / dep
        row = math.floor(z / 1.9)
        row_up = math.floor(3600 / (dep - 1) / 1.9)
        for x in range(W):
            u = (x - vpx) / dep * 30 / 2.2 + (0.5 if row % 2 else 0)
            col = math.floor(u)
            fr = (u - col) * dep / 30 * 2.2
            n = hr(col, row, 5)
            lvl = 2.3 + (n - 0.5) * 0.7
            if hr(x // 3, y // 2, row) > 0.9:
                lvl -= 0.35                                        # taques
            if fr < 1:
                lvl = 0.9
            elif fr < 2:
                lvl += 0.35                                        # cantell il·luminat
            if row != row_up:
                lvl = 0.8
            if y < y0 + 6:
                lvl -= (y0 + 6 - y) / 6 * 1.2                       # ombra de contacte amb la paret
            if extra:
                lvl += extra(x, y)
            cv.put(x, y, STONE, lvl)


def contact_shadow(cv, x0, x1, y0, depth, k=1.0):
    """Ombra dithered sota un moble (decreix cap avall i als costats)."""
    cx, half = (x0 + x1) / 2, (x1 - x0) / 2
    for y in range(y0, y0 + depth):
        for x in range(int(x0 - 4), int(x1 + 5)):
            a = (1 - (y - y0) / depth) * min(1, 1 - (abs(x - cx) - half) / 5) * k
            if a > B4[y & 3][x & 3] and 0 <= x < W and 0 <= y < H:
                o = cv.P[x, y]
                if o[3]:
                    cv.P[x, y] = tuple(int(c * 0.55) for c in o[:3]) + (o[3],)


def plank_door(cv, x0, y0, x1, y1, ramp=WALNUT, knob=True, frame=4, base=2.4, braces=True, knob_x=None):
    """Porta de taulons verticals amb marc, travessers en Z i pom de llautó."""
    # marc
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            d = min(x - x0, x1 - x, y - y0)
            if d < frame:
                lvl = base + 0.6 + (0.8 if d == 0 and (y == y0 or x == x0) else 0) - (1.4 if x1 - x < frame and x1 - x < d + 1 else 0)
                if d == frame - 1:
                    lvl = base - 1.4                                # ombra interior
                cv.put(x, y, ramp, lvl)
    lx0, ly0, lx1 = x0 + frame, y0 + frame, x1 - frame
    for y in range(ly0, y1 + 1):
        for x in range(lx0, lx1 + 1):
            px = (x - lx0) % 7
            g = (hr(x // 1, 51, (x - lx0) // 7) - 0.5) * 0.25 + (hr((x - lx0) // 7, y // 9) - 0.5) * 0.25
            lvl = base + g
            if px == 0:
                lvl = base - 1.1
            elif px == 1:
                lvl += 0.4
            if hr(x, y, 3) > 0.985:
                lvl -= 0.6                                         # nus
            if y > y1 - 3:
                lvl -= 0.6
            cv.put(x, y, ramp, lvl)
    if braces:
        h = y1 - ly0
        for yb in (ly0 + 8, y1 - 12):
            cv.rect(lx0, yb, lx1, yb + 4, ramp, lambda x, y: base + 0.4 + (0.8 if y == yb else 0) - (1.3 if y == yb + 4 else 0))
        # travesser diagonal
        ya, yb = y1 - 12, ly0 + 13
        for x in range(lx0, lx1 + 1):
            t = (x - lx0) / (lx1 - lx0)
            yy = round(ya - t * (ya - yb))
            for k in range(5):
                cv.put(x, yy - k, ramp, base + 0.3 + (0.7 if k == 4 else 0) - (1.2 if k == 0 else 0))
        # claus de ferro
        for yb2 in (ly0 + 10, y1 - 10):
            for x in range(lx0 + 3, lx1 - 1, 7):
                cv.put(x, yb2, IRON, 4.0)
    if knob:
        kx = knob_x if knob_x is not None else lx1 - 5
        ky = (ly0 + y1) // 2 + 4
        cv.rect(kx - 1, ky - 5, kx + 2, ky + 6, GOLD, lambda x, y: 2.6 - (x - kx) * 0.5)
        cv.disc(kx + 0.5, ky - 1, 2.2, 2.2, GOLD, lambda nx, ny: 4.6 - nx - ny * 1.2)
        cv.put(kx, ky + 3, GOLD, 0.2)
        cv.put(kx, ky + 4, GOLD, 0.2)
    # ombra al terra davant la porta i escaló de pedra
    cv.rect(x0 - 1, y1 + 1, x1 + 1, y1 + 2, STONE, lambda x, y: 3.4 if y == y1 + 1 else 2.0)


def gauge(cv, cx, cy, r, ang, lit=0.6, red_zone=True):
    """Manòmetre: anell de llautó, esfera de paper, marques, zona vermella i agulla (ang en graus, 0 = amunt)."""
    cv.disc(cx, cy, r + 1.2, r + 1.2, GOLD, lambda nx, ny: 3.6 - nx * 1.2 - ny * 1.2)
    cv.disc(cx, cy, r - 0.3, r - 0.3, PAPER, lambda nx, ny: 4.2 - ny * 0.8 - nx * 0.3, lit)
    if r >= 5:
        for a in range(-120, 121, 30):
            rr = r - 1.5
            cv.put(round(cx + math.sin(math.radians(a)) * rr), round(cy - math.cos(math.radians(a)) * rr), PAPER, 1.0, 0.2)
    if red_zone and r >= 5:
        for a in range(70, 125, 8):
            rr = r - 1.2
            cv.flat(round(cx + math.sin(math.radians(a)) * rr), round(cy - math.cos(math.radians(a)) * rr), (176, 40, 34))
    n = max(2, int(r - 1))
    for i in range(n):
        cv.flat(round(cx + math.sin(math.radians(ang)) * i), round(cy - math.cos(math.radians(ang)) * i), (40, 20, 20))
    cv.flat(round(cx), round(cy), (30, 20, 20))


def drift(puffs, t):
    """Fa avançar un raig de vapor: cada bufada va cap a la posició de la següent (t = 0..1), en
    neix una de nova a l'inici i l'última s'esvaeix. Amb t = 0 i t = 1 surt el mateix: fa bucle."""
    if not t:
        return puffs
    lerp = lambda a, b: tuple(a[i] + (b[i] - a[i]) * t for i in range(4))
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
    """Canonada horitzontal de gruix th, amb brides."""
    prof = [base - 0.6 + 2.2 * math.sin(math.pi * (i + 0.5) / th) ** 0.6 - (i / th) * 1.2 for i in range(th)]
    prof[0] -= 0.4
    prof[-1] = base - 1.6
    for x in range(x0, x1 + 1):
        for i in range(th):
            cv.put(x, y + i, ramp, prof[i])
    if flange_every:
        for fx in range(x0 + flange_every // 2 + seed, x1 - 2, flange_every):
            cv.rect(fx, y - 1, fx + 2, y + th, ramp, lambda xx, yy: base + 1.2 - (xx - fx) * 0.8)
            cv.put(fx + 1, y - 1, ramp, base + 2.2)


def pipe_v(cv, x, y0, y1, th, ramp=COPPER, base=2.4, flange_every=0):
    prof = [base - 0.6 + 2.2 * math.sin(math.pi * (i + 0.5) / th) ** 0.6 - (i / th) * 1.4 for i in range(th)]
    prof[0] -= 0.3
    prof[-1] = base - 1.6
    for y in range(y0, y1 + 1):
        for i in range(th):
            cv.put(x + i, y, ramp, prof[i])
    if flange_every:
        for fy in range(y0 + flange_every // 2, y1 - 2, flange_every):
            cv.rect(x - 1, fy, x + th, fy + 2, ramp, lambda xx, yy: base + 1.4 - (yy - fy) * 0.8 - (xx - x) * 0.15)


def bracket(cv, x, y, w=3):
    """Abraçadora de ferro que aguanta una canonada contra la paret."""
    cv.rect(x, y, x + w - 1, y + 1, IRON, 2.6)
    cv.put(x + 1, y, IRON, 4.0)


def ceiling(cv, ramp=IRON, h=13):
    """Sostre: bigues de ferro reblades i fosc entre elles."""
    for y in range(0, h):
        for x in range(W):
            lvl = 0.5 + (hr(x // 40) - 0.5) * 0.3
            cv.put(x, y, ramp, lvl)
    for x in range(0, W, 60):                                  # bigues transversals
        cv.rect(x, 0, x + 5, h - 3, ramp, lambda xx, yy: 2.0 + (0.8 if xx == x else 0) - (0.8 if xx == x + 5 else 0))
    cv.rect(0, h - 3, W - 1, h - 1, ramp, lambda xx, yy: [2.8, 2.0, 0.8][yy - (h - 3)])
    for x in range(3, W, 8):
        cv.put(x, h - 2, ramp, 3.8)
    cv.hline(0, W - 1, h, ramp, 0.0)


def wall_plinth(cv, y0, y1, ramp=STONE):
    """Sòcol de pedra a peu de paret."""
    for y in range(y0, y1 + 1):
        for x in range(W):
            lvl = 2.0 + (hr(x // 22, 77) - 0.5) * 0.5
            if (x // 22) != ((x + 1) // 22):
                lvl = 0.9
            if y == y0:
                lvl = 3.3
            elif y == y0 + 1:
                lvl = 2.7
            elif y == y1:
                lvl = 0.6
            cv.put(x, y, ramp, lvl)


# ─── Sala de calderes ───────────────────────────────────────────────────────

def fire_tint(x, y):
    """Quant tenyeix el foc de taronja (0..1)."""
    d = math.hypot(x - FIRE_X, (y - FIRE_Y) * 1.1)
    return max(0.0, 1 - d / 230) ** 1.8


def nx_hot(x, y):
    """Els trossos de carbó de la banda del foc tenen el cantell vermellós."""
    return x > 84 and hr(int(x), int(y), 4) > 0.6


def soot(x, y):
    """Sutge damunt la caldera i a la part alta de la paret."""
    s = 0.0
    if y < 40:
        s -= (40 - y) / 40 * 0.7
    d = math.hypot((x - 128) / 1.4, y - 20)
    if d < 70:
        s -= (1 - d / 70) * 0.8
    return s


def bg(cv, alarm=False, t=0.0):
    """t (0..1): moment del cicle d'animació del foc i el vapor (0 = el fons quiet)."""
    tt = t                                   # (dins la funció, `t` es fa servir per a altres coses)
    ph = 2 * math.pi * tt
    # ─── Sostre i paret ───────────────────────────────────────────────────────
    ceiling(cv)
    brick_wall(cv, 0, 14, W - 1, 151, seed=11, base=1.5, extra=soot)
    wall_plinth(cv, 152, 157)
    stone_floor(cv, FLOOR_Y, extra=lambda x, y: -0.3)

    # canonades del sostre
    pipe_h(cv, 0, W - 1, 16, 5, COPPER, 2.2, flange_every=64)
    pipe_h(cv, 186, W - 1, 25, 4, IRON, 2.4, flange_every=48, seed=6)
    for x in range(20, W, 64):
        bracket(cv, x, 21)
    # gotera de rovell sota una brida
    for y in range(29, 70):
        if hr(y, 9) > 0.25:
            cv.put(258, y, RUST, 2.2 - (y - 29) / 30, 0.6)
        if y < 50 and hr(y, 7) > 0.5:
            cv.put(259, y, RUST, 1.6, 0.6)

    # ─── Porta del magatzem (8..58 × 65..155) ─────────────────────────────────
    # llinda de pedra
    cv.rect(5, 59, 61, 64, STONE, lambda x, y: [3.6, 3.0, 2.6, 2.4, 2.0, 0.8][y - 59])
    plank_door(cv, 8, 65, 58, 155, base=2.2)
    cv.rect(21, 74, 45, 82, ENAMEL, lambda x, y: 3.8 if 21 < x < 45 and 74 < y < 82 else 1.6, 0.6)
    text(cv, 22, 76, 'EINES', IRON, 1.0, 0)

    # ─── Caldera gran ────────────────────────────────────────────────────────
    CX, HALF = 128, 47
    BODY_T, BODY_B = 46, 128
    # tub de sortida cap al sostre
    pipe_v(cv, 122, 20, 34, 12, COPPER, 2.4, flange_every=0)
    cv.rect(119, 30, 136, 33, COPPER, lambda x, y: 3.8 - (y - 30) * 0.6 - (x - 119) * 0.05)
    cv.rect(119, 19, 136, 21, COPPER, lambda x, y: 3.6 - (y - 19) * 0.8)
    # cos cilíndric: llum clau des de l'esquerra-davant, cantó dret a l'ombra
    def cyl(nx):
        return 0.1 + 2.9 * max(0.0, math.cos((nx + 0.3) * 1.45)) ** 0.9

    BL = 0.42                                                  # quant li arriba la llum de la sala
    for y in range(BODY_T - 14, BODY_B + 1):
        for x in range(CX - HALF, CX + HALF + 1):
            nx = (x - CX) / HALF
            if y < BODY_T:
                ny = (y - BODY_T) / 14
                if nx * nx + ny * ny > 1:
                    continue
                lvl = cyl(nx) * 0.75 + (ny + 1) * 0.5 - 0.3
                if -0.5 < nx < -0.3 and ny > -0.6:
                    lvl += 0.7
            else:
                lvl = cyl(nx)
                if -0.46 < nx < -0.36:
                    lvl += 1.1                                       # reflex vertical
                elif -0.52 < nx < -0.3:
                    lvl += 0.45
                lvl += (y - BODY_T) / (BODY_B - BODY_T) * 0.5       # el foc il·lumina de baix
                if hr(x // 3, y // 4, 2) > 0.95:
                    lvl -= 0.7                                       # pàtina
                if abs(nx - 0.1) < 0.012 or abs(nx - 0.62) < 0.012:
                    lvl -= 0.9                                       # junta de planxes
            cv.put(x, y, COPPER, lvl, BL)
    # reblons a les juntes verticals
    for jx in (0.1, 0.62):
        x = round(CX + jx * HALF) + 2
        for y in range(BODY_T + 4, BODY_B - 2, 5):
            cv.put(x, y, COPPER, cyl(jx) + 1.4, BL)
            cv.put(x, y + 1, COPPER, cyl(jx) - 0.8, BL)
    # vora de la cúpula
    for x in range(CX - HALF, CX + HALF + 1):
        nx = (x - CX) / HALF
        yy = BODY_T + round(math.sqrt(max(0, 1 - nx * nx)) * 3)
        cv.put(x, yy, COPPER, cyl(nx) + 1.2, BL)
        cv.put(x, yy + 1, COPPER, cyl(nx) - 1.2, BL)
    # anelles reblades (corbes per la perspectiva)
    for by in (68, 92, 116):
        for x in range(CX - HALF, CX + HALF + 1):
            nx = (x - CX) / HALF
            yy = by + round(math.sqrt(max(0, 1 - nx * nx)) * 3)
            for k in range(4):
                cv.put(x, yy + k, COPPER, cyl(nx) + [1.1, 0.2, -0.3, -1.6][k], BL)
            if (x - CX + 200) % 5 == 0 and abs(nx) < 0.95:
                cv.put(x, yy + 1, COPPER, cyl(nx) + 1.8, BL)
                cv.put(x, yy + 2, COPPER, cyl(nx) - 1.0, BL)
    # vores fosques del cilindre (silueta)
    for y in range(BODY_T, BODY_B + 1):
        cv.put(CX - HALF, y, COPPER, 0.6, BL)
        cv.put(CX + HALF, y, COPPER, -1, 0)
        cv.put(CX + HALF - 1, y, COPPER, 0.2, BL)
    # placa del fabricant
    cv.rect(108, 100, 148, 109, GOLD, lambda x, y: 3.4 if 108 < x < 148 and 100 < y < 109 else 1.4)
    text(cv, 117, 102, 'ALDAIA', GOLD, 1.0, 0.4)
    # manòmetre gran al mig, amb l'agulla a tocar del vermell
    cv.rect(126, 72, 130, 78, COPPER, lambda x, y: 3.4 - (x - 126) * 0.5)
    gauge(cv, 128, 82, 10, 72)
    # nivell d'aigua: tub de vidre al costat
    for y in range(56, 96):
        for x in (156, 157, 158):
            if y > 74:
                cv.put(x, y, STEAM, 1.6 + (0.8 if x == 156 else 0), 0.4)          # aigua
            else:
                cv.put(x, y, STEAM, 0.6 + (1.8 if x == 156 else 0), 0.4)
        cv.put(155, y, GOLD, 2.0)
        cv.put(159, y, GOLD, 1.0)
    cv.rect(154, 54, 160, 56, GOLD, 3.4)
    cv.rect(154, 96, 160, 98, GOLD, 2.6)
    cv.hline(156, 158, 74, STEAM, 4.6, 0.3)
    # vàlvula de seguretat i xiulet, a dalt a la dreta
    pipe_v(cv, 150, 26, 40, 4, GOLD, 2.4)
    cv.rect(147, 24, 156, 27, GOLD, lambda x, y: 4.2 - (y - 24) * 0.8)
    cv.disc(152, 22, 3, 2, GOLD, lambda nx, ny: 4.0 - nx - ny)

    # ─── Fogar: base de maó refractari i la boca del foc ──────────────────────
    BX0, BX1, BT = 74, 182, 129
    cv.rect(BX0 - 2, BT, BX1 + 2, BT + 2, IRON, lambda x, y: [3.2, 2.2, 0.8][y - BT])
    brick_wall(cv, BX0, BT + 3, BX1, 157, seed=12, base=2.4,
               extra=lambda x, y: -0.9 * (abs(x - CX) / 54) ** 2)
    cv.vline(BX0, BT + 3, 157, BRICK, 1.0)
    cv.vline(BX1, BT + 3, 157, BRICK, 0.4)
    # placa de ferro colat al voltant de la boca, amb arc
    FX0, FX1, FY0, FY1 = 106, 150, 134, 155
    MCX = (FX0 + FX1) / 2

    def in_mouth(x, y, m=0):
        if not (FX0 - m <= x <= FX1 + m and FY0 - m <= y <= FY1):
            return False
        ay = FY0 + 7
        if y < ay:
            return ((x - MCX) / ((FX1 - FX0) / 2 + m)) ** 2 + ((y - ay) / (7 + m)) ** 2 <= 1
        return True

    for y in range(FY0 - 7, FY1 + 2):
        for x in range(FX0 - 7, FX1 + 8):
            if in_mouth(x, y, 6) and not in_mouth(x, y, 0):
                inner = in_mouth(x, y, 2)
                lvl = 2.2 + (1.4 if inner else 0) - (x - FX0) / 60
                if not in_mouth(x, y, 5):
                    lvl = 0.6
                cv.put(x, y, IRON, lvl, 0.35)
    for a in range(200, 341, 20):                              # reblons de l'arc
        cv.put(round(MCX + math.cos(math.radians(a)) * 26), round(FY0 + 7 + math.sin(math.radians(a)) * 12), IRON, 4.6, 0.3)
    # interior: brases a baix, flames que pugen
    for y in range(FY0, FY1 + 1):
        for x in range(FX0, FX1 + 1):
            if not in_mouth(x, y):
                continue
            t = (y - FY0) / (FY1 - FY0)                            # 0 dalt, 1 baix
            u = (x - FX0) / (FX1 - FX0)
            flame = math.sin(u * 19 + 1.3 - ph * 2) * 0.5 + math.sin(u * 7.3 + ph) * 0.6 + math.sin(u * 31 - ph * 3) * 0.25
            lvl = 0.6 + t * 4.4 + flame * (1 - t) * 1.8 - abs(u - 0.5) * 1.8
            if y >= FY1 - 3:
                lvl = 4.6 + (hr(x // 2, y) - 0.5) * 2.4 + 0.5 * (math.sin(ph + hr(x // 2, y, 5) * 6.3) - math.sin(hr(x // 2, y, 5) * 6.3))  # brases
                if hr(x // 3, 77) > 0.7 and y == FY1 - 3:
                    lvl -= 2.6                                         # carbó encara negre
            cv.put(x, y, FIRE, lvl, 0)
    # graella
    for x in range(FX0 + 3, FX1, 5):
        cv.vline(x, FY1 - 4, FY1 - 3, IRON, 0.8, 0)
    cv.hline(FX0, FX1, FY1 + 1, IRON, 1.2, 0.3)
    # resplendor
    cv.glow(MCX, FY1 - 4, 44, (255, 150, 60), 0.5 + 0.05 * math.sin(ph * 2))
    cv.glow(MCX, FY1 - 2, 22, (255, 210, 120), 0.45)
    # guspires
    sp = random.Random(9)
    for _ in range(14):
        x = sp.uniform(FX0 + 8, FX1 - 8)
        y = FY0 + 1 + (sp.uniform(0, 8) - tt * 8) % 8                    # pugen poc a poc
        cv.flat(x, y, (255, 220, 120) if sp.random() > 0.4 else (255, 150, 60))

    # ─── Pila de carbó al terra, davant la base, i la pala clavada ────────────
    coal = random.Random(3)
    for _ in range(230):
        t = coal.random()
        cx = 60 + t * 34 + coal.uniform(-1, 1)
        hgt = max(0.0, 1 - abs(t - 0.4) * 2.2) * 14
        cy = 166 - coal.random() * hgt - coal.random() * 2
        r = coal.uniform(1.3, 2.6)
        cv.disc(cx, cy, r, r * 0.75, COAL, lambda nx, ny: 1.6 - nx * 0.4 - ny * 1.0 + (1.6 if nx > 0.2 and ny < -0.2 else 0), 0.6)
        if nx_hot(cx, cy):
            cv.put(round(cx + r * 0.5), round(cy - r * 0.4), FIRE, 2.6, 0)
    # pala clavada al carbó
    for i in range(44):
        x, y = 86 + i * 0.25, 160 - i
        cv.put(round(x), round(y), WALNUT, 3.4, 0.6)
        cv.put(round(x) + 1, round(y), WALNUT, 1.8, 0.6)
    cv.rect(95, 114, 100, 116, WALNUT, 3.0, 0.6)
    cv.poly([(80, 158), (91, 158), (90, 166), (82, 166)], IRON, lambda x, y: 2.0 + (x - 80) * 0.12, 0.5)
    contact_shadow(cv, 58, 96, 166, 4, 0.8)

    # ─── Canonada amb vàlvula (entre la caldera i el tauler) ──────────────────
    pipe_v(cv, 186, 21, 120, 6, COPPER, 2.2, flange_every=38)
    for y in range(116, 124):                                     # colze cap a la caldera
        cv.rect(176, y, 191, y, COPPER, 2.4 - abs(y - 120) * 0.5)
    for yb in (40, 140):
        bracket(cv, 185, yb, 8)
    # volant de la vàlvula
    VX, VY = 189, 96
    cv.ring(VX, VY, 8, RED, 3.0, step=3)
    cv.ring(VX, VY, 7, RED, 2.0, step=3)
    for a in (0, 60, 120):
        for i in range(-7, 8):
            cv.put(round(VX + math.cos(math.radians(a)) * i), round(VY + math.sin(math.radians(a)) * i), RED, 2.6)
    cv.disc(VX, VY, 2, 2, IRON, 3.6)
    # manòmetre petit damunt
    gauge(cv, 189, 72, 6, -30)

    # ─── Tauler d'anuncis (199..281 × 32..87) ─────────────────────────────────
    TX0, TY0, TX1, TY1 = 200, 33, 280, 80
    cv.rect(TX0, TY0, TX1, TY1, WALNUT, lambda x, y: 3.4 if (x - TX0 < 2 or y - TY0 < 2) else (1.2 if (TX1 - x < 2 or TY1 - y < 2) else 2.6))
    cv.rect(TX0 + 3, TY0 + 3, TX1 - 3, TY1 - 3, CORK, lambda x, y: 2.6 + (hr(x, y, 4) - 0.5) * 0.9 - (0.8 if y == TY0 + 3 or x == TX0 + 3 else 0))
    contact_shadow(cv, TX0, TX1, TY1 + 1, 3, 0.8)

    def note(x0, y0, x1, y1, ramp=PAPER, lvl=3.6, lines=True, pin=(170, 36, 36), tilt=0):
        # ombra
        for y in range(y0 + 1, y1 + 2):
            for x in range(x0 + 1, x1 + 2):
                if cv.get(x, y)[3]:
                    o = cv.P[x, y]
                    cv.P[x, y] = tuple(int(c * 0.6) for c in o[:3]) + (255,)
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                l = lvl - (y - y0) / (y1 - y0 + 1) * 0.5
                if y == y1 and hr(x, 3) > 0.6:
                    l -= 0.8                                       # punta arrissada
                cv.put(x, y + (round((x - x0) * tilt)), ramp, l)
        if lines:
            r = random.Random(x0 * 7 + y0)
            for ly in range(y0 + 4, y1 - 1, 2):
                e = x1 - 2 - r.randint(0, 4)
                for x in range(x0 + 2, e):
                    if r.random() > 0.15:
                        cv.put(x, ly + round((x - x0) * tilt), ramp, lvl - 2.2)
        if pin:
            cx = (x0 + x1) // 2
            cv.flat(cx, y0 + 1, pin)
            cv.flat(cx + 1, y0 + 1, mix(pin, (255, 255, 255), 0.4))
            cv.flat(cx, y0 + 2, mix(pin, (0, 0, 0), 0.5))

    # avís gran: «RECORDEU ... 27-B»
    note(205, 37, 245, 61, PAPER, 4.0, lines=False)
    text(cv, 209, 41, 'RECORDEU', RED, 3.0, 0.4)
    for ly in (48, 51, 54):
        for x in range(208, 243):
            if hr(x // 3, ly) > 0.25 and x % 4 != 3:
                cv.put(x, ly, PAPER, 1.6)
    text(cv, 228, 56, '27-B', RED, 2.8, 0.4)
    note(249, 37, 263, 55, MANILA, 4.0)
    note(266, 39, 276, 50, PAPER, 3.6, tilt=0.1)
    note(205, 65, 222, 76, PAPER, 3.4, pin=(40, 90, 170))
    note(226, 64, 244, 75, (MANILA), 3.2, pin=(40, 140, 60))
    # retrat-cartell de «treballador del mes» (el Cargol, és clar)
    note(249, 59, 261, 74, PAPER, 3.8, lines=False, pin=(200, 160, 40))
    cv.rect(251, 62, 259, 69, IRON, 2.4, 0.4)
    cv.rect(253, 64, 257, 67, IRON, 4.0, 0.4)
    cv.flat(254, 65, (90, 220, 150)); cv.flat(256, 65, (90, 220, 150))
    cv.vline(252, 59, 61, IRON, 3.0, 0.4); cv.vline(258, 59, 61, IRON, 3.0, 0.4)
    for x in range(251, 260):
        if x % 2:
            cv.put(x, 72, PAPER, 1.8)
    # safata de filferro amb la pila de formularis 27-B
    for i in range(6):
        y = 78 - i
        cv.rect(264 + (i % 2), y, 279 + (i % 2), y, PAPER, 4.2 - (0.9 if i % 2 else 0), 0.5)
    cv.hline(264, 279, 79, PAPER, 2.0, 0.5)
    note(265, 62, 279, 69, MANILA, 4.2, lines=False, pin=None)
    text(cv, 266, 63, '27-B', IRON, 0.6, 0.2)
    cv.rect(262, 79, 282, 81, IRON, lambda x, y: 3.2 - (y - 79) * 0.8)
    cv.vline(262, 70, 81, IRON, 3.0)
    cv.vline(282, 70, 81, IRON, 1.6)

    # ─── Porta del moll de càrrega (207..275 × 84..155) ───────────────────────
    cv.rect(214, 86, 268, 94, ENAMEL, lambda x, y: 4.2 if 214 < x < 268 and 86 < y < 94 else 1.2, 0.6)
    tx = 241 - text_w('MOLL') // 2
    text(cv, tx, 88, 'MOLL', NAVY_INK, 0, 0)
    cv.put(216, 88, IRON, 1.0); cv.put(266, 88, IRON, 1.0)
    # porta doble, més ampla, de taulons amb ferros
    cv.rect(207, 96, 275, 99, STONE, lambda x, y: [3.6, 3.0, 2.4, 1.0][y - 96])
    plank_door(cv, 209, 100, 273, 155, base=2.0, knob=False, frame=3)
    cv.vline(241, 103, 155, WALNUT, 0.4)
    cv.vline(242, 103, 155, WALNUT, 3.2)
    for yb in (112, 142):
        cv.rect(212, yb, 270, yb + 2, IRON, lambda x, y: 3.0 - (y - yb) * 0.9)
        for x in range(214, 270, 6):
            cv.put(x, yb + 1, IRON, 4.4)
    # forrellat
    cv.rect(234, 124, 249, 126, IRON, lambda x, y: 3.6 - (y - 124))
    cv.rect(245, 122, 247, 128, IRON, 2.8)

    # ─── Rellotge de fàbrica, sobre l'escriptori (les 3 i 10 de la matinada) ──
    KX, KY = 312, 52
    cv.disc(KX, KY, 13, 13, WALNUT, lambda nx, ny: 3.2 - nx - ny)
    cv.disc(KX, KY, 10.5, 10.5, PAPER, lambda nx, ny: 4.0 - ny * 0.7, 0.6)
    for h in range(12):
        a = math.radians(h * 30)
        cv.put(round(KX + math.sin(a) * 9), round(KY - math.cos(a) * 9), IRON, 0.6 if h % 3 else 0.0, 0)
    for i in range(6):                                          # agulla de les hores (les 3)
        cv.flat(KX + i, KY, (30, 22, 26))
    for i in range(8):                                          # minutera (10)
        a = math.radians(60)
        cv.flat(round(KX + math.sin(a) * i), round(KY - math.cos(a) * i), (30, 22, 26))
    cv.flat(KX, KY, (150, 30, 30))
    cv.disc(KX - 4, KY - 5, 2, 1.2, PAPER, 6.0, 0)                # reflex del vidre
    cv.vline(KX, 26, 38, IRON, 2.0)

    # ─── Manòmetres de la línia de vapor (dreta) ──────────────────────────────
    for gx, ang in ((378, -40), (394, 20), (410, 95)):
        pipe_v(cv, gx - 1, 29, 38, 3, IRON, 2.6)
        gauge(cv, gx, 45, 6, ang)
    # fuita de vapor a la brida de la línia de ferro
    steam(cv, [(402, 30, 5, 0.9), (397, 24, 6, 0.7), (390, 19, 8, 0.5), (381, 16, 9, 0.3)], lit=0.5)

    # ─── Porta de la cambra de ressonància (422..472 × 65..155) ───────────────
    DX0, DY0, DX1, DY1 = 422, 66, 472, 155
    cv.rect(DX0, DY0, DX1, DY1, IRON, lambda x, y: 2.6 + (0.9 if x - DX0 < 2 or y - DY0 < 2 else 0) - (1.0 if DX1 - x < 2 else 0))
    # franja d'avís a la llinda
    for y in range(DY0 + 2, DY0 + 7):
        for x in range(DX0 + 2, DX1 - 1):
            if ((x + y) // 4) % 2:
                cv.put(x, y, WARN, 3.4)
            else:
                cv.put(x, y, IRON, 0.6)
    # fulla de la porta, de planxa reblada
    LX0, LY0, LX1 = DX0 + 5, DY0 + 9, DX1 - 5
    for y in range(LY0, DY1 + 1):
        for x in range(LX0, LX1 + 1):
            u = (x - LX0) / (LX1 - LX0)
            lvl = 2.6 - u * 0.8 + (hr(x // 4, y // 4, 8) - 0.5) * 0.3
            if hr(x // 2, y // 3, 11) > 0.93:
                cv.put(x, y, RUST, 2.4)
                continue
            cv.put(x, y, IRON, lvl)
    cv.vline(LX0, LY0, DY1, IRON, 0.4)
    cv.hline(LX0, LX1, LY0, IRON, 0.4)
    for yb in (LY0 + 14, LY0 + 46, DY1 - 12):
        cv.rect(LX0 + 1, yb, LX1 - 1, yb + 2, IRON, lambda x, y: 3.6 - (y - yb) * 1.1)
        for x in range(LX0 + 3, LX1 - 1, 5):
            cv.put(x, yb + 1, IRON, 5.0)
    for y in range(LY0 + 4, DY1 - 2, 6):
        cv.put(LX0 + 2, y, IRON, 4.6)
        cv.put(LX1 - 2, y, IRON, 3.6)
    # placa de llautó i forrellat amb pany
    cv.rect(432, 90, 462, 98, GOLD, lambda x, y: 3.4 if 432 < x < 462 and 90 < y < 98 else 1.4, 0.6)
    text(cv, 447 - text_w('CAMBRA') // 2, 92, 'CAMBRA', GOLD, 0.8, 0.3)
    cv.rect(454, 112, 462, 126, IRON, lambda x, y: 3.6 - (x - 454) * 0.25)
    cv.rect(445, 116, 456, 119, IRON, lambda x, y: 4.0 - (y - 116) * 0.8)
    cv.vline(458, 119, 122, IRON, 0.0)
    cv.put(458, 118, IRON, 0.0)
    # escaló de ferro
    cv.rect(DX0 - 2, DY1 + 1, DX1 + 2, DY1 + 3, IRON, lambda x, y: 3.4 - (y - DY1 - 1))

    # ─── Llum d'alarma vermell (433..461 × 38..65) ────────────────────────────
    AX, AY = 447, 52
    cv.rect(441, 61, 453, 64, IRON, lambda x, y: 3.0 - (y - 61) * 0.6)         # base
    cv.rect(445, 58, 449, 61, IRON, 2.4)
    if alarm:
        cv.disc(AX, AY, 8, 8, RED, lambda nx, ny: 5.2 - math.hypot(nx + 0.3, ny + 0.4) * 2.6, 0)
        cv.disc(AX - 2, AY - 3, 2.2, 1.6, PINK_HOT, 1, 0)
    else:                                                            # vidre vermell fosc, apagat
        cv.disc(AX, AY, 8, 8, RED, lambda nx, ny: 2.6 - math.hypot(nx + 0.3, ny + 0.4) * 1.6 - ny * 0.4, 0.4)
        cv.disc(AX - 3, AY - 4, 1.6, 1.2, RED, 3.6, 0.4)                      # reflex del foc al vidre
    for a in (-60, -20, 20, 60):                                     # gàbia
        for t in range(-8, 9):
            ang = math.radians(a)
            x = AX + math.sin(ang) * 8 * math.cos(t / 8 * 1.2)
            cv.put(round(x), AY + t, IRON, 1.2 if alarm else 1.0, 0 if alarm else 0.6)
    cv.hline(AX - 8, AX + 8, AY, IRON, 1.4 if alarm else 1.2, 0 if alarm else 0.6)
    cv.rect(AX - 3, AY - 11, AX + 3, AY - 8, IRON, lambda x, y: 3.0 - (y - AY + 11) * 0.5)
    if alarm:
        cv.glow(AX, AY, 42, (255, 60, 40), 0.55)
        cv.glow(AX, AY, 18, (255, 120, 90), 0.35)
    # cable de l'alarma que surt de la cambra
    for y in range(29, 41):
        cv.put(450, y, IRON, 1.6)

    # ─── Escriptori del capatàs (284..330), a tocar de la seva cadira ─────────
    QX0, QX1 = 283, 331
    contact_shadow(cv, QX0, QX1, 160, 12, 1.0)
    for x in (QX0 + 2, QX1 - 3):                                   # potes del darrere (més curtes)
        cv.rect(x + 3, 138, x + 4, 160, WALNUT, 1.2)
    for x in (QX0 + 1, QX1 - 3):                                   # potes del davant
        cv.rect(x, 138, x + 2, 168, WALNUT, lambda xx, yy: 2.8 - (xx - x) * 0.8)
    cv.rect(QX0 + 3, 138, QX1 - 3, 143, WALNUT, lambda x, y: 2.4 - (y - 138) * 0.2)    # faldó
    cv.hline(QX0 + 3, QX1 - 3, 143, WALNUT, 0.6)
    cv.rect(300, 139, 312, 141, WALNUT, 3.4)                                   # calaixet
    cv.put(306, 140, GOLD, 4.0)
    for y in range(130, 138):                                                 # tauler
        t = (y - 130) / 7
        for x in range(QX0 + 2 - round(t * 2), QX1 - 2 + round(t * 2) + 1):
            cv.put(x, y, WALNUT, 3.0 + t * 0.6 + (hr(x // 4, 61) - 0.5) * 0.4)
    cv.hline(QX0, QX1, 137, WALNUT, 4.4)
    cv.hline(QX0 + 2, QX1 - 2, 130, WALNUT, 2.0)
    # diari plegat
    for y in range(131, 135):
        for x in range(287 + (y - 131), 304 + (y - 131)):
            cv.put(x, y, PAPER, 3.6 - (0.9 if (x + y) % 5 == 0 else 0))
    cv.hline(288, 302, 131, PAPER, 4.6)
    # tassa de cafè (freda)
    cv.rect(306, 125, 311, 132, PAPER, lambda x, y: 4.2 - (x - 306) * 0.45)
    cv.hline(306, 311, 125, IRON, 1.0)
    cv.ring(313, 128, 2, PAPER, 3.0, step=30)
    cv.disc(308.5, 133, 4.5, 1, PAPER, 3.0)
    # llum de flexo de ferro amb pantalla verda
    cv.disc(322, 135, 5, 1.6, IRON, lambda nx, ny: 3.4 - nx - ny)
    for i in range(18):
        cv.put(322 + round(math.sin(i / 6) * 2), 134 - i, IRON, 3.0)
    for y in range(110, 117):
        t = (y - 110) / 6
        half = 4 + t * 5
        for x in range(round(321 - half), round(321 + half) + 1):
            u = (x - 321) / half
            cv.put(x, y, LAMPG, 3.0 - u * 1.4 - (1 - t) * 0.6, 0.3)
    cv.hline(313, 330, 117, [(255, 236, 170)], 0, 0)
    cv.glow(321, 121, 26, (255, 226, 150), 0.5)

    # ─── Vapor que s'escapa (vàlvula de seguretat, brida del tub) ─────────────
    steam(cv, drift([(157, 20, 4, 0.9), (162, 15, 6, 0.75), (170, 12, 8, 0.55), (181, 11, 10, 0.35)], tt), lit=0.6)
    steam(cv, drift([(193, 59, 3, 0.8), (199, 55, 5, 0.6), (207, 51, 6, 0.35)], tt), lit=0.6)

    # ─── Llum del foc: to taronja a tota la meitat esquerra ───────────────────
    cv.tint(0, 0, W - 1, 205, (255, 140, 60), lambda x, y: fire_tint(x, y) * 0.14)
    # reflex del foc al terra, davant la boca
    for y in range(FLOOR_Y, 200):
        for x in range(60, 200):
            d = math.hypot((x - FIRE_X) / 2.4, (y - FLOOR_Y) * 0.9)
            a = max(0, 1 - d / 36) ** 1.3 * (0.7 + 0.06 * math.sin(ph * 2))
            if a > B4[y & 3][x & 3] * 0.7:
                o = cv.P[x, y]
                cv.P[x, y] = mix(o, (255, 170, 80), a * 0.6) + (255,)


# tinta fosca per a rètols esmaltats
NAVY_INK = [(26, 26, 44)]
PINK_HOT = [(255, 170, 150), (255, 210, 190)]


def segell(cv):
    """El segell oficial, dret a terra (302..330 × 169..191): pom de fusta, coll de llautó i base amb goma vermella."""
    SX = 315
    # empremta vermella al terra, de quan ha caigut
    for y in range(186, 190):
        for x in range(322, 330):
            if (x in (322, 329) or y in (186, 189)) and hr(x, y, 2) > 0.2:
                cv.put(x, y, RED, 2.2, 0.3)
    cv.put(325, 188, RED, 2.0, 0.3); cv.put(326, 187, RED, 2.0, 0.3)
    contact_shadow(cv, SX - 9, SX + 7, 186, 4, 1.0)
    # base: bloc de fusta amb la goma vermella a sota
    for y in range(178, 186):
        for x in range(SX - 9, SX + 8):
            lvl = 2.8 - (x - SX + 9) / 16 * 1.4 + (0.9 if y == 178 else 0)
            cv.put(x, y, WALNUT, lvl, 0.5)
    cv.vline(SX - 9, 178, 185, WALNUT, 4.0, 0.5)
    cv.rect(SX - 9, 185, SX + 7, 187, RED, lambda x, y: 3.4 - (y - 185) * 0.9 - (x - SX + 9) * 0.05, 0.5)
    # placa de llautó del davant
    cv.rect(SX - 6, 180, SX + 4, 183, GOLD, lambda x, y: 3.8 - (x - SX + 6) * 0.15, 0.5)
    cv.put(SX - 4, 181, GOLD, 1.4, 0.3); cv.put(SX - 1, 181, GOLD, 1.4, 0.3); cv.put(SX + 2, 181, GOLD, 1.4, 0.3)
    # coll de llautó
    cv.rect(SX - 2, 174, SX + 1, 177, GOLD, lambda x, y: 4.2 - (x - SX + 2) * 0.8, 0.5)
    cv.hline(SX - 3, SX + 2, 177, GOLD, 2.0, 0.5)
    # pom de fusta envernissada
    cv.disc(SX - 0.5, 170.5, 4.2, 4.2, WALNUT, lambda nx, ny: 3.8 - nx * 1.6 - ny * 1.6, 0.5)
    cv.put(SX - 2, 168, PAPER, 4.0, 0.3)
    outline(cv, 300, 160, 332, 185)
    cv.glow(SX, 178, 14, (255, 220, 150), 0.1)


_ALARM = []


def alarma_encesa(cv):
    """El llum d'alarma encès: es renderitza la sala amb i sense alarma i es copia el que canvia
    al voltant del llum (vidre, gàbia, halo vermell i la paret que tenyeix)."""
    if not _ALARM:
        on, off = Canvas(light=LIGHT_ALARM), Canvas(light=LIGHT)
        bg(on, alarm=True)
        bg(off)
        _ALARM.append((on, off))
    on, off = _ALARM[0]
    for y in range(0, 120):
        for x in range(380, W):
            p = on.P[x, y]
            if p != off.P[x, y]:
                cv.P[x, y] = p


PROPS = {'segell': segell, 'alarma_encesa': alarma_encesa}


# Animació de fons: el foc respira, les guspires pugen i el vapor s'escampa. Cada fotograma només
# té els píxels que canvien respecte del fons quiet (t = 0).
def _ambient_frames(n=8):
    base = Canvas(light=LIGHT)
    bg(base)
    frames = []
    for i in range(n):
        cv = Canvas(light=LIGHT)
        bg(cv, t=i / n)
        fr = Canvas(light=LIGHT, transparent=True)
        for y in range(H):
            for x in range(W):
                p = cv.P[x, y]
                if p != base.P[x, y]:
                    fr.P[x, y] = p
        frames.append(fr.img)
    return frames


ANIMS = {'ambient': {'frames': _ambient_frames, 'frameDuration': 160}}
