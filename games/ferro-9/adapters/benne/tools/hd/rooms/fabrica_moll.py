"""
Moll de càrrega de la fàbrica (Acte 2, Iri): maó, bigues de ferro, taulons; la llançadora nova a la badia,
amb la comporta tancada al fons (per sota s'escola la lluna). És el mateix lloc que l'hangar de La Gavina (gavina_hangar), cent
vint anys abans: el pilar 7, el conducte, les reixes del terra i la llançadora es dibuixen amb les mateixes
funcions a totes dues sales (aquí, nous; allà, envellits).
Llums: làmpada penjada sobre les bigues, la porta entreoberta de les calderes (foc), un aplic sobre el tauler
d'eines, el llum de servei de la badia i la lluna que s'escola per sota la comporta.
"""
import math
import random

from hd.pix import (Canvas, Light, B4, W, H, hr, mix, ramp, WALNUT, FLOOR, GOLD, COPPER, RUST, BRICK, IRON, FIRE,
                    GREEN, RED, PAPER, MANILA, SKY, SIL, SMOKE, CYAN, STEEL, GRAY)

# ─── Rampes pròpies ─────────────────────────────────────────────────────────
F9 = [(16, 22, 36), (30, 42, 62), (48, 66, 92), (70, 96, 126), (100, 132, 162), (140, 174, 200), (186, 214, 232), (232, 246, 252)]   # ferro-9: blau d'acer, net
ACER = [(22, 20, 24), (38, 36, 40), (56, 54, 58), (78, 76, 78), (104, 100, 100), (134, 130, 126), (170, 164, 156), (206, 200, 190)]  # acer comú
OLDHULL = [(14, 16, 22), (26, 28, 34), (42, 42, 46), (60, 58, 60), (82, 78, 76), (106, 100, 94), (132, 124, 114), (160, 152, 138), (190, 182, 166)]   # la mateixa, amb pols
HULL = [(20, 20, 28), (34, 36, 46), (52, 56, 66), (76, 80, 90), (104, 108, 116), (138, 142, 146), (176, 178, 178), (214, 214, 208), (244, 242, 232)]
PAINT = [(26, 14, 16), (50, 22, 22), (80, 32, 28), (112, 44, 34), (144, 60, 42), (176, 84, 56), (204, 116, 80)]    # pintura de fàbrica (mini)
MORTAR = [(20, 12, 14), (34, 22, 22), (52, 36, 32), (72, 52, 44), (96, 72, 58), (124, 96, 76)]
NIGHT = ramp((4, 6, 16), (14, 16, 38), (36, 30, 66), (80, 48, 78), (150, 84, 70), n=9)

FLOOR_Y = 153
VP = (240, 104)            # punt de fuga del terra (el mateix que fan servir les reixes)

LIGHT = Light(vignette=(70, 40), floor_fade=(200, 44))
LIGHT.point(150, 30, r=175, k=2.5, squash=0.95, down=True)        # làmpada penjada
LIGHT.point(44, 150, r=95, k=2.0, squash=1.25)                    # calderes: la porta entreoberta
LIGHT.point(304, 40, r=78, k=1.5, squash=1.0, down=True)          # aplic sobre el tauler d'eines


def _moon(x, y):
    """Llum freda que s'escola per sota la comporta tancada (terra de la badia i del davant)."""
    v = 0.0
    if x > 340 and y > 120:
        v += max(0.0, 1 - math.hypot((x - 407) / 70, (y - 146) / 16)) ** 1.4 * 1.0
    if y > FLOOR_Y and x > 300:                                   # taca al terra davant la badia
        t = (y - FLOOR_Y) / 50
        xl, xr = 334 - t * 40, 480
        if xl < x < xr and t < 1:
            v += (1 - t) * 0.9 * min(1, (x - xl) / 20)
    return v


LIGHT.add(_moon)
LIGHT.point(404, 16, r=120, k=1.7, squash=0.9, down=True)        # llum de servei de la badia


# ─── Peces compartides amb l'hangar ─────────────────────────────────────────

FONT = {
    'A': ['.#.', '#.#', '###', '#.#', '#.#'], 'C': ['.##', '#..', '#..', '#..', '.##'], 'D': ['##.', '#.#', '#.#', '#.#', '##.'],
    'E': ['###', '#..', '##.', '#..', '###'], 'F': ['###', '#..', '##.', '#..', '#..'], 'I': ['###', '.#.', '.#.', '.#.', '###'],
    'L': ['#..', '#..', '#..', '#..', '###'], 'M': ['#.#', '###', '###', '#.#', '#.#'], 'N': ['#.#', '###', '###', '###', '#.#'],
    'O': ['.#.', '#.#', '#.#', '#.#', '.#.'], 'R': ['##.', '#.#', '##.', '#.#', '#.#'], 'S': ['.##', '#..', '.#.', '..#', '##.'],
    'U': ['#.#', '#.#', '#.#', '#.#', '###'], 'V': ['#.#', '#.#', '#.#', '#.#', '.#.'], 'X': ['#.#', '#.#', '.#.', '#.#', '#.#'],
    'T': ['###', '.#.', '.#.', '.#.', '.#.'], 'P': ['##.', '#.#', '##.', '#..', '#..'], 'G': ['.##', '#..', '#.#', '#.#', '.##'],
    '1': ['.#.', '##.', '.#.', '.#.', '###'], '4': ['#.#', '#.#', '###', '..#', '..#'], '7': ['###', '..#', '.#.', '.#.', '.#.'],
    '9': ['###', '#.#', '###', '..#', '##.'], '-': ['...', '...', '###', '...', '...'], '.': ['...', '...', '...', '...', '.#.'],
    ' ': ['...', '...', '...', '...', '...'],
}


def text(cv, x, y, s, rmp, lvl, lit=0.5):
    """Lletres de 3×5 (rètols i plaques)."""
    for ch in s:
        for j, row in enumerate(FONT.get(ch, FONT[' '])):
            for i, c in enumerate(row):
                if c == '#':
                    cv.put(x + i, y + j, rmp, lvl, lit)
        x += 4
    return x


def cyl(u):
    """Ombrejat d'un cilindre vertical (u = -1..1, llum de l'esquerra)."""
    return -u * 1.1 - u * u * 1.3 + (0.9 if -0.62 < u < -0.38 else 0)


SEVEN = ['#####', '....#', '...#.', '...#.', '..#..', '..#..', '..#..']


def pillar(cv, cx, y0, y1, aged=False):
    """Pilar de ferro colat amb un 7 pintat: el mateix a les dues èpoques. cx = centre; y0 = sota la biga."""
    body = HULL if not aged else STEEL
    # capitell
    for y in range(y0, y0 + 8):
        hw = 11 - (y - y0) // 2 if y > y0 + 3 else 11
        for x in range(cx - hw, cx + hw + 1):
            cv.put(x, y, IRON, 3.2 + cyl((x - cx) / (hw + 0.5)) - (y - y0) * 0.12 + (1.2 if y == y0 else 0))
    cv.hline(cx - 11, cx + 11, y0 + 4, IRON, 1.0)
    # fust (al present, la pintura vermella esvaïda i clapes de rovell)
    for y in range(y0 + 8, y1 - 10):
        for x in range(cx - 7, cx + 8):
            u = (x - cx) / 7.5
            lvl = 2.6 + cyl(u)
            if aged:
                n = hr(x // 3, y // 4, 7) * 0.6 + hr(x // 2, y // 2, 8) * 0.4
                if n > 0.62:
                    cv.put(x, y, RUST, 2.2 + cyl(u) * 0.8 - (0.6 if n > 0.8 else 0))
                    continue
                lvl -= 0.5
            cv.put(x, y, PAINT, lvl)
    # anelles de reforç
    for yy in (y0 + 30, y1 - 34):
        for y in range(yy, yy + 4):
            for x in range(cx - 8, cx + 9):
                cv.put(x, y, IRON, 3.0 + cyl((x - cx) / 8.5) + (0.8 if y == yy else 0) - (1.2 if y == yy + 3 else 0))
    # base
    for y in range(y1 - 10, y1 + 1):
        hw = 8 + min(3, (y - (y1 - 10)) // 2)
        for x in range(cx - hw, cx + hw + 1):
            cv.put(x, y, IRON, 2.6 + cyl((x - cx) / (hw + 0.5)) - (1.0 if y == y1 else 0) + (0.8 if y == y1 - 10 else 0))
    if aged:
        # rovell que regalima i pintura que salta
        rnd = random.Random(cx * 3)
        for _ in range(9):
            x = rnd.randint(cx - 6, cx + 6)
            ya = rnd.randint(y0 + 12, y1 - 30)
            for y in range(ya, ya + rnd.randint(6, 22)):
                if hr(x, y, 3) > 0.25:
                    cv.put(x, y, RUST, 1.6 + cyl((x - cx) / 7.5) * 0.6)
        for _ in range(26):
            x, y = rnd.randint(cx - 6, cx + 6), rnd.randint(y0 + 10, y1 - 12)
            cv.put(x, y, RUST, 3.6)
            cv.put(x, y + 1, RUST, 0.8)
    # el 7, en blanc de plantilla, damunt d'una franja
    sy = y0 + 42
    for y in range(sy - 2, sy + 10):
        for x in range(cx - 6, cx + 7):
            cv.put(x, y, PAPER if not aged else MANILA, 1.6 + cyl((x - cx) / 7.5) * 0.8 + (0.6 if aged else 0))
    for j, row in enumerate(SEVEN):
        for i, ch in enumerate(row):
            if ch == '#':
                x, y = cx - 2 + i, sy + j
                if aged and hr(x, y, 41) < 0.15:
                    continue                                      # pintura esquerdada
                cv.put(x, y, PAINT, 1.4 if not aged else 1.0)


def carved_mark(cv, x, y, aged=False):
    """La marca de l'Iri: una I. i una clau anglesa, gravades. Nova: metall viu; vella: solc ple de rovell."""
    cut = (F9, 5.6) if not aged else (SIL, 0.6)
    lip = (F9, 3.2) if not aged else (RUST, 5.4)
    pts = [(x, y + i) for i in range(7)] + [(x + 2, y + 6)]                       # I.
    pts += [(x + 4 + i, y + 7 - i) for i in range(5)]                              # mànec de la clau
    pts += [(x + 8, y), (x + 9, y - 1), (x + 10, y), (x + 10, y + 2), (x + 9, y + 3)]  # boca de la clau
    pts += [(x + 7, y + 1), (x + 7, y - 1)]
    for px, py in pts:
        cv.put(px, py, cut[0], cut[1], 0.4)
        cv.put(px + 1, py + 1, lip[0], lip[1] - 1.8, 0.4)                          # ombra del solc


def grate(cv, xa, xb, aged=False, y0=173, y1=187):
    """Reixa de desguàs encastada al terra (en perspectiva cap a VP)."""
    vx, vy = VP
    k = (y0 - vy) / (y1 - vy)
    far = lambda x: vx + (x - vx) * k
    fr = IRON if not aged else STEEL
    # marc
    for y in range(y0, y1 + 1):
        t = (y - y0) / (y1 - y0)
        xl = far(xa) + (xa - far(xa)) * t
        xr = far(xb) + (xb - far(xb)) * t
        for x in range(round(xl), round(xr) + 1):
            inner = y0 + 1 < y < y1 - 1 and xl + 2.5 < x < xr - 2.5
            if inner:
                # forat amb barrots que fugen
                s = (x - xl) / (xr - xl)
                bar = (s * 10) % 1 < 0.28
                if bar:
                    cv.put(x, y, fr, 3.2 + (0.6 if y < y0 + 3 else 0) - t * 0.4)
                else:
                    cv.put(x, y, fr, 0.0 - t * 0.5, 0.3)
            else:
                edge = 4.2 if y == y0 else (1.4 if y == y1 else 2.6)
                cv.put(x, y, fr, edge)
    # travesser del mig
    ym = (y0 + y1) // 2
    t = (ym - y0) / (y1 - y0)
    xl = far(xa) + (xa - far(xa)) * t
    xr = far(xb) + (xb - far(xb)) * t
    cv.hline(round(xl) + 2, round(xr) - 2, ym, fr, 2.6)
    if aged:
        rnd = random.Random(xa)
        for _ in range(14):
            x = rnd.randint(xa, xb)
            y = rnd.randint(y0, y1)
            if cv.get(x, y)[3]:
                cv.put(x, y, RUST, 2.4)


def shuttle(cv, x0, cy, aged=False, L=130, R=24):
    """La llançadora de càrrega, de perfil (morro a l'esquerra). Nova al moll; vella i sense peces a l'hangar.
    Retorna (porta, pany): les caixes on van la porta i el pany sònic."""
    body = HULL if not aged else OLDHULL
    trim = GOLD if not aged else COPPER
    rnd = random.Random(7)

    def half(s):
        if s < 0.26:
            return R * math.sqrt(max(0.0, 1 - ((0.26 - s) / 0.26) ** 2)) ** 0.9
        if s > 0.86:
            return R * (1 - (s - 0.86) / 0.14 * 0.28)
        return R

    # aletes (darrere el cos)
    tail = x0 + L
    cv.poly([(tail - 30, cy - R + 2), (tail - 4, cy - R - 16), (tail + 3, cy - R - 16), (tail - 2, cy - R + 6)], body, lambda x, y: 3.4 - (y - cy) * 0.02)
    cv.poly([(tail - 30, cy + R - 2), (tail - 4, cy + R + 14), (tail + 3, cy + R + 14), (tail - 2, cy + R - 6)], body, 1.8)
    cv.line(tail - 4, cy - R - 16, tail + 3, cy - R - 16, trim, 4.0)
    cv.line(tail - 4, cy + R + 14, tail + 3, cy + R + 14, trim, 2.6)
    # cos
    for x in range(x0, tail + 1):
        s = (x - x0) / L
        h = half(s)
        for y in range(round(cy - h), round(cy + h) + 1):
            ny = (y - cy) / max(h, 1)
            lvl = 4.0 - ny * 1.6 - ny * ny * 1.6 + (1.3 if -0.72 < ny < -0.5 else 0) - (0.6 if s < 0.1 else 0)
            seam = (x - x0) % 17 == 0 and s > 0.2
            if seam:
                lvl -= 1.4
            if abs(ny - 0.42) < 0.05 and s > 0.24:
                lvl -= 1.2
            if aged:
                lvl -= 0.6 + (hr(x // 3, y // 2, 11) - 0.5) * 0.6
            cv.put(x, y, body, lvl)
            if seam and (y - cy) % 4 == 0:
                cv.put(x + 1, y, body, lvl + 2.4)                 # reblons
    # cap del morro, de llautó
    for x in range(x0, x0 + 9):
        h = half((x - x0) / L)
        for y in range(round(cy - h), round(cy + h) + 1):
            ny = (y - cy) / max(h, 1)
            cv.put(x, y, trim, 3.4 - ny * 1.4 - ny * ny + (1.0 if -0.6 < ny < -0.3 else 0))
    # cèrcol de popa
    for y in range(round(cy - half(0.9)), round(cy + half(0.9)) + 1):
        ny = (y - cy) / R
        for x in range(tail - 14, tail - 11):
            cv.put(x, y, trim, 3.2 - ny * 1.4 + (0.8 if x == tail - 14 else 0))
    # finestreta
    px_, py_ = x0 + 22, cy - 7
    cv.disc(px_, py_, 6.5, 6.5, trim, lambda nx, ny: 3.6 - nx - ny)
    glass = CYAN if not aged else STEEL
    cv.disc(px_, py_, 4.4, 4.4, glass, lambda nx, ny: (1.2 if not aged else 2.2) + ny * 0.6 - nx * 0.3, 0.3)
    cv.put(px_ - 2, py_ - 2, PAPER, 5.0, 0)
    cv.put(px_ - 1, py_ - 3, PAPER, 4.4, 0)
    # porta
    dx0, dx1, dy0, dy1 = x0 + 40, x0 + 58, cy - 17, cy + 19
    for y in range(dy0, dy1 + 1):
        for x in range(dx0, dx1 + 1):
            edge = x in (dx0, dx1) or y in (dy0, dy1)
            if edge:
                cv.put(x, y, body, 0.8 if x == dx1 or y == dy1 else 1.2)
    cv.vline(dx0 + 1, dy0 + 1, dy1 - 1, body, 5.0 if not aged else 4.0)
    cv.hline(dx0 + 1, dx1 - 1, dy0 + 1, body, 5.2 if not aged else 4.0)
    for hy in (dy0 + 6, dy1 - 6):                                   # frontisses
        cv.rect(dx0 - 2, hy, dx0, hy + 2, trim, 3.4)
    # pany sònic: un ressonador rodó, sense forat per a cap clau
    lx, ly = dx1 + 6, cy - 1
    cv.disc(lx, ly, 6, 6, trim, lambda nx, ny: 2.8 - nx * 0.8 - ny * 1.0)
    cv.ring(lx, ly, 4, trim, 1.2, step=6)
    cv.ring(lx, ly, 2, trim, 4.6, step=12)
    cv.put(lx, ly, trim, 1.0)
    cv.put(lx - 4, ly - 4, PAPER, 4.6, 0)
    # els tres components de ferro-9 (al moll hi són; a l'hangar, tres forats)
    for i, ox in enumerate((72, 87, 102)):
        hx, hy = x0 + ox, cy + 10
        if not aged:
            cv.rect(hx, hy, hx + 9, hy + 5, F9, lambda x, y: 4.6 - (y - hy) * 0.6)
            cv.hline(hx, hx + 9, hy, F9, 6.0)
            cv.put(hx + 1, hy + 2, F9, 7, 0)
        else:
            cv.rect(hx - 1, hy - 1, hx + 10, hy + 6, body, 4.0)
            cv.rect(hx, hy, hx + 9, hy + 5, SIL, 0.4, 0)
            cv.hline(hx, hx + 9, hy, SIL, 1.6, 0)
            for k in range(2):                                    # cables arrencats
                cv.put(hx + 2 + k * 4, hy + 6, COPPER, 3.2)
                cv.put(hx + 3 + k * 4, hy + 7, COPPER, 2.4)
    # inscripció pintada a la popa: «L-1»
    for x, y in ((x0 + 90, cy - 12), (x0 + 90, cy - 11), (x0 + 90, cy - 10), (x0 + 90, cy - 9), (x0 + 91, cy - 9),
                 (x0 + 93, cy - 11), (x0 + 94, cy - 11), (x0 + 96, cy - 12), (x0 + 96, cy - 11), (x0 + 96, cy - 10), (x0 + 96, cy - 9)):
        cv.put(x, y, RED if not aged else RUST, 3.0 if not aged else 1.8)
    if aged:
        # pols, regalims de rovell i taques de verdet
        for _ in range(60):
            x = rnd.randint(x0 + 6, tail - 2)
            h = half((x - x0) / L)
            y = rnd.randint(round(cy - h) + 1, round(cy - h * 0.2))
            cv.put(x, y, GRAY, 4.6)
        for _ in range(10):
            x = rnd.randint(x0 + 20, tail - 10)
            ya = cy + rnd.randint(-6, 12)
            for y in range(ya, min(ya + rnd.randint(6, 14), round(cy + half((x - x0) / L)))):
                cv.put(x, y, RUST, 2.4)
    # bressol (suports)
    for sx in (x0 + 30, x0 + 100):
        cv.rect(sx - 3, cy + R - 2, sx + 3, cy + R + 22, IRON, lambda x, y: 2.4 - (x - sx) * 0.35)
        cv.rect(sx - 8, cy + R + 20, sx + 8, cy + R + 23, IRON, lambda x, y: 3.0 - (y - cy - R - 20) * 0.6)
        cv.poly([(sx - 10, cy + R - 4), (sx + 10, cy + R - 4), (sx + 6, cy + R + 1), (sx - 6, cy + R + 1)], IRON, 2.6)
    return (dx0, dy0, dx1, dy1), (lx, ly)


# ─── Fons ───────────────────────────────────────────────────────────────────

def bricks(cv, x0, y0, x1, y1, base=2.0, rmp=BRICK, seed=0):
    for y in range(y0, y1 + 1):
        row = (y - y0) // 5
        off = 6 if row % 2 else 0
        for x in range(x0, x1 + 1):
            u = (x + off) % 12
            v = (y - y0) % 5
            if v == 4 or u == 11:
                cv.put(x, y, MORTAR, base + 0.4)
            else:
                b = hr((x + off) // 12, row, seed)
                lvl = base + (b - 0.5) * 1.0 + (0.5 if v == 0 else 0) - (0.3 if v == 3 else 0)
                if b > 0.93:
                    lvl -= 0.9                                    # maó cremat
                cv.put(x, y, rmp, lvl)


def floor_planks(cv):
    vx, vy = VP
    for y in range(FLOOR_Y, H):
        dep = y - vy
        for x in range(W):
            u = (x - vx) / dep * 4.2
            pl = math.floor(u)
            fr = (u - pl) * dep / 4.2
            t = 900 / dep
            r = hr(pl, 5)
            seg = math.floor(t / 3.2 + r * 4)
            seg_up = math.floor(900 / (dep - 1) / 3.2 + r * 4)
            lvl = 1.9 + (hr(pl, seg) - 0.5) * 0.7 + (0.25 if hr(pl, seg, x // 3) > 0.85 else 0)
            if fr < 1:
                lvl = 0.5
            elif fr < 2:
                lvl += 0.3
            elif seg != seg_up:
                lvl = 0.7
            if y < 160:
                lvl -= (160 - y) / 7 * 1.2                      # ombra de contacte amb la paret
            cv.put(x, y, FLOOR, lvl)


def lamp_cone(x, y):
    """El con de llum sota la làmpada penjada (0..1)."""
    if not 40 <= y <= 120:
        return 0.0
    half = 8 + (y - 40) * 0.55
    return max(0.0, min(1.0, (1 - abs(x - 150) / half) * 2.0)) * (1 - (y - 40) / 80) ** 0.7


def bg(cv, t=0.0):
    from hd.rooms.fabrica_despatx import dust
    tt = t
    ph = 2 * math.pi * tt
    # ─── Sostre: taulons foscos i una biga d'acer ──────────────────────────
    cv.rect(0, 0, W - 1, 12, WALNUT, lambda x, y: 0.4 + (0.5 if x % 24 in (0, 1) else 0) + (hr(x // 24, 3) - 0.5) * 0.4, 0.4)
    for x in range(0, W, 48):                                    # tirants de la cavallada
        cv.line(x, 12, x + 24, 0, IRON, 1.2, 0.4)
        cv.line(x + 24, 0, x + 48, 12, IRON, 1.0, 0.4)
    cv.rect(0, 13, W - 1, 20, IRON, lambda x, y: [3.0, 2.4, 1.6, 1.4, 1.4, 1.4, 1.0, 0.4][y - 13])
    for x in range(4, W, 10):
        cv.put(x, 14, IRON, 4.0)
        cv.put(x, 19, IRON, 2.6)

    # ─── Paret de maó ─────────────────────────────────────────────────────
    bricks(cv, 0, 21, W - 1, FLOOR_Y - 1, base=2.0, seed=51)
    cv.darken(0, 21, W - 1, 26, lambda x, y: (27 - y) / 7)          # ombra de la biga
    # sòcol de pedra
    cv.rect(0, FLOOR_Y - 5, W - 1, FLOOR_Y - 1, GRAY, lambda x, y: 1.4 + (0.8 if y == FLOOR_Y - 5 else 0) + (hr(x // 14, 2) - 0.5) * 0.4)

    # ─── Terra de taulons ────────────────────────────────────────────────
    floor_planks(cv)
    # carrils de la vagoneta: surten de la badia i fugen cap al davant
    vx, vy = VP
    for rx in (372, 436):
        for y in range(FLOOR_Y, H):
            x = vx + (rx - vx) * (y - vy) / (FLOOR_Y - vy)
            cv.put(x, y, IRON, 4.0)
            cv.put(x + 1, y, IRON, 2.6)
            cv.put(x + 2, y, IRON, 0.6)
        for y in range(FLOOR_Y + 3, H, 1):                       # travesses
            dep = y - vy
            if (1800 / dep) % 3 < 0.25:
                xa = vx + (rx - 10 - vx) * (y - vy) / (FLOOR_Y - vy)
                xb = vx + (rx + 12 - vx) * (y - vy) / (FLOOR_Y - vy)
                cv.hline(round(xa), round(xb), y, WALNUT, 1.0)

    # ─── Porta de les calderes, entreoberta (8..57 × 65..155) ─────────────
    # arc de maó
    for y in range(62, FLOOR_Y):
        for x in range(8, 58):
            if x < 13 or x > 52 or y < 70:
                d = min(x - 8, 57 - x, y - 62)
                cv.put(x, y, BRICK, 3.2 - (0.8 if (x + y) % 6 == 0 else 0) - (d == 0) * 1.4)
    cv.rect(8, 62, 57, 64, GRAY, lambda x, y: 3.2 - (y - 62) * 0.7)             # llinda de pedra
    # interior: el foc de les calderes
    for y in range(70, FLOOR_Y):
        for x in range(13, 53):
            fl = 0.0
            if x > 40:                                            # (la part que es veu) les flames que es mouen a la paret
                fl = 0.35 * math.sin(y * 0.29 + x * 0.21 + ph * 3) + 0.25 * math.sin(y * 0.13 - x * 0.37 + ph * 2 + 1.0) \
                    + 0.15 * math.sin(y * 0.5 + ph * 5 + 2.0)
            cv.put(x, y, FIRE, 1.4 + (y - 70) / 80 * 2.4 - abs(x - 46) / 20 + (hr(x // 2, y // 3) - 0.5) * 0.4 + fl, 0.2)
    # silueta d'una caldera al fons
    for y in range(84, FLOOR_Y):                                  # caldera: cos cilíndric reblonat
        for x in range(26, 51):
            u = (x - 38) / 12.5
            top = 84 + (1 - math.sqrt(max(0, 1 - u * u))) * 8
            if y >= top:
                lvl = 1.4 + u * 1.2 - u * u + (0.8 if (y - 84) % 14 == 0 else 0)
                cv.put(x, y, SIL, lvl + (1.6 if (y - 84) % 14 == 1 and x % 4 == 0 else 0), 0)
    cv.rect(35, 70, 40, 86, SIL, lambda x, y: 1.2 + (x - 35) * 0.2, 0)
    for y in range(124, 131):
        for x in range(30, 42):
            cv.put(x, y, FIRE, 5.4 - abs(x - 36) / 3 + (hr(x, y) - 0.5), 0)         # boca del forn
    # fulla de la porta (ferro reblonat), oberta cap a dins
    for y in range(70, FLOOR_Y):
        for x in range(13, 42):
            u = (x - 13) / 28
            lvl = 2.2 - u * 0.6 + (hr(x // 2, 31) - 0.5) * 0.2
            if (x - 13) % 14 in (0, 13) or (y - 70) % 20 in (0, 19):
                lvl -= 0.6
            cv.put(x, y, IRON, lvl)
            if ((x - 13) % 14 in (2, 11)) and (y - 70) % 20 in (3, 16):
                cv.put(x, y, IRON, lvl + 2.0)
    cv.vline(41, 70, FLOOR_Y - 1, IRON, 4.4)                     # cantell il·luminat pel foc
    cv.tint(40, 70, 42, FLOOR_Y - 1, (255, 150, 60), 0.4)
    cv.rect(36, 108, 39, 112, GOLD, 3.0)                          # maneta
    # placa esmaltada «CALDERES»
    cv.rect(14, 50, 51, 58, PAPER, lambda x, y: 3.8 - (y - 50) * 0.15)
    cv.rect(14, 50, 51, 50, PAPER, 5.0)
    cv.rect(15, 51, 50, 51, PAPER, 2.6)
    text(cv, 17, 52, 'CALDERES', [(30, 34, 70), (40, 46, 96)], 0.5, 0)
    cv.put(15, 57, IRON, 1.0); cv.put(50, 57, IRON, 1.0)
    # llum del foc: halo i taca al terra
    cv.glow(46, 120, 46, (255, 140, 60), 0.32 + 0.03 * math.sin(ph * 3) + 0.025 * (math.sin(ph * 5 + 1) - math.sin(1)))
    for y in range(FLOOR_Y, 200):
        t = (y - FLOOR_Y) / 47
        for x in range(int(14 - t * 20), int(58 + t * 26)):
            cv.tint(x, y, x, y, (255, 130, 50), 0.28 * (1 - t) * (1 - abs(x - 40 + t * 0) / (40 + t * 30)))

    # ─── Conducte de pressió: de les calderes cap al moll ─────────────────
    pipe(cv, aged=False)

    # ─── Bastidor de la paret (la biga de ferro-9 hi va al damunt) ────────
    for bx in (92, 194):
        cv.rect(bx - 2, 84, bx + 2, 100, IRON, lambda x, y: 3.0 - (x - bx) * 0.5)
        cv.rect(bx - 2, 84, bx + 12, 87, IRON, lambda x, y: 3.6 - (y - 84) * 0.6)
        cv.line(bx + 2, 99, bx + 11, 88, IRON, 2.0)
        cv.put(bx, 92, IRON, 4.6); cv.put(bx, 97, IRON, 4.6)
    # rètol pintat a la paret, sobre el bastidor
    # lletres pintades directament al maó
    cv.rect(118, 47, 172, 57, PAPER, lambda x, y: 1.6 + (hr(x // 3, y // 2) - 0.5) * 0.5)
    text(cv, 121, 50, 'MATERIAL', PAINT, 1.8, 0.8)
    text(cv, 155, 50, 'F-9', [(20, 40, 70), (30, 60, 100), (50, 90, 140)], 1.4, 0.4)
    cv.darken(118, 47, 172, 57, lambda x, y: 0.4 if hr(x // 2, y, 5) > 0.82 else 0)

    # ─── Cavallets (la biga d'acer hi va al damunt) ───────────────────────
    for tx in (100, 188):
        cv.darken(tx - 18, 157, tx + 18, 162, lambda x, y: 0.7 - abs(x - tx) / 30)
        for s in (-1, 1):
            cv.line(tx + s * 3, 136, tx + s * 13, 160, WALNUT, 4.6 if s < 0 else 3.4)
            cv.line(tx + s * 4, 136, tx + s * 14, 160, WALNUT, 3.2 if s < 0 else 2.2)
        cv.rect(tx - 12, 134, tx + 12, 137, WALNUT, lambda x, y: 4.6 - (y - 134) * 0.8)
        cv.line(tx - 9, 150, tx + 9, 150, WALNUT, 2.4)

    # ─── Pilar 7 ─────────────────────────────────────────────────────────
    pillar(cv, 257, 21, FLOOR_Y - 1)
    cv.darken(244, FLOOR_Y, 272, FLOOR_Y + 4, lambda x, y: 0.8 - abs(x - 257) / 20)

    # ─── Reixes de desguàs, noves (la del pilar 7 és la trapa) ────────────
    for xa, xb in ((24, 62), (100, 138), (170, 208)):
        grate(cv, round(xa * 480 / 352), round(xb * 480 / 352))

    # ─── Tauler d'eines (275..331 × 44..116) ──────────────────────────────
    cv.rect(274, 43, 332, 117, WALNUT, 1.0)
    for y in range(45, 116):
        for x in range(276, 331):
            lvl = 2.6 + (hr(x // 8, 13) - 0.5) * 0.4 - (0.7 if (x - 276) % 8 == 0 else 0)
            if (x % 6 == 3) and (y % 6 == 3):
                lvl = 0.6                                         # forats
            cv.put(x, y, WALNUT, lvl)
    cv.hline(274, 332, 43, WALNUT, 3.8)
    # siluetes pintades de les eines (on va cada cosa): serra, llima i la clau anglesa
    def outline(pts):
        for x, y in pts:
            cv.put(x, y, PAPER, 2.2, 0.6)
    outline([(x, 62) for x in range(292, 326)] + [(292, y) for y in range(58, 66)] + [(325, y) for y in range(58, 66)])
    outline([(322, y) for y in range(80, 106)] + [(318, y) for y in range(80, 106)])
    outline([(282 + i // 2, 80 + i) for i in range(24)] + [(281, 78), (283, 78), (280, 76), (284, 76)])
    # martell i unes tenalles, de debò
    cv.vline(299, 82, 104, WALNUT, 4.0); cv.vline(300, 82, 104, WALNUT, 2.6)
    cv.rect(294, 80, 305, 84, IRON, lambda x, y: 3.6 - (y - 80) * 0.5)
    for i in range(16):
        cv.put(307 + (i // 6), 84 + i, IRON, 3.4)
        cv.put(311 - (i // 6), 84 + i, IRON, 2.4)
    cv.disc(309, 86, 2, 2, IRON, 4.0)
    for hx, hy in ((299, 79), (309, 82), (304, 55), (322, 75)):  # ganxos
        cv.put(hx, hy, IRON, 4.0)
    # aplic de llum de paret
    cv.rect(301, 30, 307, 33, GOLD, 3.0)
    for y in range(34, 40):
        hw = 2 + (y - 34)
        for x in range(304 - hw, 305 + hw):
            cv.put(x, y, GREEN, 3.4 - (x - 304) / hw - (y - 34) * 0.1, 0.4)
    cv.hline(297, 311, 40, [(255, 236, 170)], 0, 0)
    cv.glow(304, 42, 22, (255, 220, 150), 0.35)

    # ─── La badia: la llançadora i, al fons, la comporta tancada ──────────
    BX0, BX1, BY0 = 334, 476, 9
    # marc d'acer de la badia
    cv.rect(BX0 - 3, 8, BX0, FLOOR_Y - 1, IRON, lambda x, y: [1.4, 3.6, 2.8, 1.8][x - BX0 + 3])
    cv.rect(BX1, 8, W - 1, FLOOR_Y - 1, IRON, lambda x, y: 1.6 + (0.8 if x == BX1 else 0))
    cv.rect(BX0 - 3, 6, W - 1, 8, IRON, lambda x, y: [3.8, 2.6, 1.0][y - 6])
    # interior de la badia: sostre, parets de maó i terra en perspectiva cap a la comporta
    FX0, FX1, FY0, FY1 = 352, 462, 22, 140
    for y in range(BY0, FLOOR_Y):
        for x in range(BX0 + 1, BX1):
            if FX0 <= x <= FX1 and FY0 <= y <= FY1:
                continue
            if y > FY1:                                           # terra de la badia
                cv.put(x, y, FLOOR, 1.2 + (y - FY1) / 12 - (0.6 if x % 9 == 0 else 0))
            elif y < FY0:                                         # sostre de la badia, amb una biga
                cv.put(x, y, IRON, 0.5 + (FY0 - y) / 12 + (1.2 if y == 14 else 0) - (0.6 if y == 15 else 0))
            else:                                                 # parets laterals
                v = (y - FY0) % 6 == 5 or (x + ((y - FY0) // 6) * 5) % 10 == 0
                cv.put(x, y, BRICK, 1.2 - (0.6 if v else 0) - (0.4 if x < FX0 else 0.1))
    # la comporta: planxes de ferro reblades sobre taulons, corredisses a banda i banda
    GX0, GX1 = FX0 + 5, FX1 - 5
    for y in range(FY0, FY1 + 1):
        for x in range(FX0, FX1 + 1):
            if x < GX0 or x > GX1:                                # guies de ferro (canal en U)
                u = x - FX0 if x < GX0 else FX1 - x
                cv.put(x, y, IRON, [0.6, 2.8, 1.6, 0.8, 0.3][u])
                continue
            band = (y - FY0) % 20
            if band < 4:                                          # fleixos de ferro horitzontals
                lvl = [3.2, 2.4, 2.0, 0.6][band]
                cv.put(x, y, IRON, lvl + (hr(x // 5, y, 81) - 0.5) * 0.3)
                if band == 1 and (x - GX0) % 9 == 4:
                    cv.put(x, y, IRON, 4.6)                       # reblons
                continue
            k = (x - GX0) % 11                                    # taulons verticals
            lvl = 1.8 + (hr((x - GX0) // 11, 81) - 0.5) * 0.6 + (hr(x, y // 3, 82) - 0.5) * 0.3
            if k == 0:
                lvl = 0.4
            elif k == 1:
                lvl += 0.7
            cv.put(x, y, WALNUT, lvl)
    # rovell que regalima dels fleixos
    for x in range(GX0, GX1, 3):
        if hr(x, 83) > 0.7:
            y0 = FY0 + 4 + int(hr(x, 84) * 5) * 20
            for y in range(y0, min(FY1 - 8, y0 + 3 + int(hr(x, 85) * 6))):
                cv.put(x, y, RUST, 1.8)
    # franges de perill a la vora de baix i l'escletxa de lluna per sota
    for x in range(GX0, GX1 + 1):
        for y in range(FY1 - 7, FY1 - 1):
            yel = ((x + y) // 5) % 2 == 0
            cv.put(x, y, GOLD if yel else IRON, (3.4 if yel else 0.8) - (y - FY1 + 7) * 0.15)
        cv.put(x, FY1 - 1, IRON, 0.2)
        if hr(x // 3, 86) > 0.15:                             # (la claror de l'escletxa tremola una mica)
            fi = hr(x // 4, 88) * 6.283
            cv.flat(x, FY1, mix((150, 170, 230), (230, 236, 255), min(1, max(0, hr(x, 87) + 0.3 * math.sin(ph * (1 + x // 4 % 3) + fi)))))
    # la lluna que s'escola per sota, tirada pel terra de la badia
    for y in range(FY1 + 1, FLOOR_Y):
        for x in range(GX0 - 4, GX1 + 5):
            a = (1 - (y - FY1) / (FLOOR_Y - FY1)) * 0.5
            if a > B4[y & 3][x & 3]:
                cv.P[x, y] = mix(cv.P[x, y], (150, 170, 230), 0.4) + (255,)
    # cadenes que pugen del cap de la comporta fins al tambor del sostre
    for cx_ in (GX0 + 10, GX1 - 10):
        cv.rect(cx_ - 2, FY0, cx_ + 2, FY0 + 2, IRON, 3.6)                  # orella
        for y in range(BY0 + 5, FY0):
            cv.put(cx_, y, IRON, 3.4 if y % 3 else 1.0)
            cv.put(cx_ + 1, y, IRON, 2.0 if y % 3 else 3.2)
    cv.rect(GX0 + 4, BY0 + 2, GX1 - 4, BY0 + 6, IRON, lambda x, y: [1.2, 3.4, 2.8, 1.8, 0.8][y - BY0 - 2])   # tambor
    # encaix de la palanca de dos metres, a la guia esquerra, amb la roda dentada i el retén
    cv.rect(FX0 - 1, 52, FX0 + 12, 70, IRON, lambda x, y: 3.0 - (x - FX0) * 0.12 - (y - 52) * 0.03)
    cv.hline(FX0 - 1, FX0 + 12, 52, IRON, 4.4)
    cv.disc(FX0 + 6, 58, 4.6, 4.6, IRON, lambda nx, ny: 4.0 - nx - ny)
    for a_ in range(0, 360, 30):
        cv.put(round(FX0 + 6 + math.cos(math.radians(a_)) * 5.6), round(58 + math.sin(math.radians(a_)) * 5.6), IRON, 3.0)
    cv.rect(FX0 + 4, 63, FX0 + 8, 69, SIL, 0.4, 0)                        # l'encaix (buit)
    cv.line(FX0 + 10, 53, FX0 + 13, 57, IRON, 4.0)                        # retén
    # carrils dins la badia
    for ry in (150, 146):
        cv.hline(BX0 + 1, BX1 - 1, ry, IRON, 3.4)
    # la llançadora, nova de trinca
    shuttle(cv, 338, 108)
    cv.darken(BX0 + 1, 147, BX1 - 1, 152, lambda x, y: 0.5)
    # llum de servei de la badia, engabiat al sostre
    cv.vline(404, BY0 + 6, 12, IRON, 1.4)
    cv.disc(404, 14, 3, 2, IRON, 2.6)
    cv.disc(404, 16, 2.2, 1.4, [(255, 236, 180)], 0, 0)
    cv.glow(404, 17, 26, (255, 220, 160), 0.35)
    # tint fred de la lluna que entra per sota la comporta
    cv.tint(BX0, FY1 - 20, BX1, FLOOR_Y + 30, (150, 170, 230), lambda x, y: 0.2 * min(1, _moon(x, y)))

    # ─── Làmpada penjada ──────────────────────────────────────────────────
    cv.vline(150, 20, 28, IRON, 1.4)
    for y in range(28, 35):
        hw = 2 + (y - 28) * 1.6
        for x in range(round(150 - hw), round(150 + hw) + 1):
            cv.put(x, y, GREEN, 3.0 - (x - 150) / hw * 1.2 - (y - 28) * 0.1, 0.3)
    cv.hline(139, 161, 35, [(255, 240, 190)], 0, 0)
    cv.disc(150, 36, 2.4, 1.6, PAPER, 6, 0)
    cv.glow(150, 38, 40, (255, 222, 150), 0.4)

    # pols que sura sota la làmpada i a la llum de la lluna que entra per sota la comporta
    dust(cv, tt, 18, 61, (126, 44, 174, 104), (255, 236, 190), 0.6, lamp_cone)
    dust(cv, tt, 16, 62, (336, 124, 474, 186), (206, 216, 248), 0.85, lambda x, y: min(1.0, _moon(x, y) * 1.4), fall=(-2, -5))

    # ─── Detalls: caixes i sacs a la vora de la porta ─────────────────────
    crate(cv, 60, 133, 20, 19)
    crate(cv, 64, 116, 14, 17, small=True)
    cv.darken(56, FLOOR_Y - 1, 84, FLOOR_Y + 5, lambda x, y: 0.7)


def crate(cv, x0, y0, w, h, small=False):
    """Caixa de fusta amb tires de ferro i «F-9» de plantilla."""
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            lvl = 2.6 + (hr(x // 4, y0) - 0.5) * 0.3 - (0.7 if (y - y0) % 5 == 4 else 0)
            if x in (x0, x0 + w - 1) or y in (y0, y0 + h - 1):
                lvl = 3.4 if (x == x0 or y == y0) else 1.2
            cv.put(x, y, WALNUT, lvl)
    cv.line(x0 + 1, y0 + h - 2, x0 + w - 2, y0 + 1, WALNUT, 3.4)
    if not small:
        cv.rect(x0 + 4, y0 + 6, x0 + w - 5, y0 + 10, MANILA, 2.6)
        for x in range(x0 + 5, x0 + w - 5, 2):
            cv.put(x, y0 + 8, IRON, 0.6)


def pipe(cv, aged=False, x=225, w=11, run_y=26, y_end=FLOOR_Y - 1, from_left=True):
    """El conducte de pressió: tram horitzontal sota la biga, colze i baixada fins a terra, amb vàlvula
    i manòmetre. Al passat, de coure lluent; al present, el mateix tub, rovellat."""
    rmp = COPPER if not aged else RUST
    lv = [1.6, 3.0, 4.2, 3.8, 3.2, 2.8, 2.4, 2.0, 1.6, 1.2, 0.6]
    # tram horitzontal
    if from_left:
        for xx in range(0, x + w):
            for i in range(w - 2):
                yy = run_y + i
                if xx < x + i:
                    cv.put(xx, yy, rmp, lv[i] + (0.3 if not aged else (hr(xx // 3, yy) - 0.5) * 0.6))
        for xx in range(30, x, 46):                              # brides i abraçadores
            cv.rect(xx, run_y - 1, xx + 2, run_y + w - 2, rmp, lambda a, b: 3.4 - (b - run_y) * 0.25)
    # baixada
    for yy in range(run_y, y_end + 1):
        for i in range(w):
            if yy >= run_y + (w - 2) - i or True:
                cv.put(x + i, yy, rmp, lv[i] + ((hr((x + i) // 2, yy // 3) - 0.5) * 0.6 if aged else 0))
    # colze
    cv.disc(x + 4, run_y + 4, 6, 6, rmp, lambda nx, ny: 3.0 - nx - ny * 0.8)
    for yy in range(run_y + 16, y_end, 34):                       # brides
        cv.rect(x - 1, yy, x + w, yy + 2, rmp, lambda a, b: 3.8 - (b - yy) * 0.8)
    cv.rect(x - 3, y_end - 3, x + w + 2, y_end, IRON, lambda a, b: 2.8 - (b - y_end + 3) * 0.4)
    # manòmetre
    mx, my = x + w + 5, 70
    cv.rect(x + w, my - 1, mx - 3, my + 1, rmp, 3.0)
    cv.disc(mx, my, 6, 6, GOLD if not aged else RUST, lambda nx, ny: 3.6 - nx - ny)
    cv.disc(mx, my, 4.5, 4.5, PAPER if not aged else GRAY, lambda nx, ny: (4.4 if not aged else 3.2) - ny * 0.4, 0.4)
    for a in range(200, 341, 35):
        cv.put(round(mx + math.cos(math.radians(a)) * 3.5), round(my + math.sin(math.radians(a)) * 3.5), IRON, 1.0, 0)
    ang = math.radians(300 if not aged else 205)                  # al present, l'agulla a zero
    for r in range(4):
        cv.flat(round(mx + math.cos(ang) * r), round(my + math.sin(ang) * r), (170, 30, 30))
    cv.flat(mx, my, (40, 30, 30))
    # vàlvula de volant
    vx, vy = x + w // 2, 108
    cv.rect(x - 2, vy - 6, x + w + 1, vy + 6, IRON if not aged else RUST, lambda a, b: 3.0 - (a - x) * 0.15)
    cv.rect(vx - 1, vy - 2, vx + 1, vy + 2, IRON, 4.0)
    wheel = RED if not aged else RUST
    for a in range(0, 360, 3):
        for rr in (8, 9):
            px = round(vx + math.cos(math.radians(a)) * rr)
            py = round(vy + math.sin(math.radians(a)) * rr * 0.9)
            cv.put(px, py, wheel, (4.4 if rr == 8 else 3.0) - math.sin(math.radians(a)) * 0.8)
    for a in (45, 135, 225, 315):
        for rr in range(2, 8):
            cv.put(round(vx + math.cos(math.radians(a)) * rr), round(vy + math.sin(math.radians(a)) * rr * 0.9), wheel, 3.6)


# ─── Props ──────────────────────────────────────────────────────────────────

def p_biga_acer(cv):
    """Biga d'acer de dos metres, damunt dels cavallets."""
    x0, x1, y0 = 80, 210, 124
    for x in range(x0, x1 + 1):
        g = (hr(x // 3, 61) - 0.5) * 0.4
        cv.put(x, y0, ACER, 5.2 + g)
        cv.put(x, y0 + 1, ACER, 4.0 + g)
        for y in range(y0 + 2, y0 + 8):
            cv.put(x, y, ACER, 2.0 + g - (y - y0 - 2) * 0.15 + (0.8 if y == y0 + 2 else 0))
        cv.put(x, y0 + 8, ACER, 3.4 + g)
        cv.put(x, y0 + 9, ACER, 1.4 + g)
    for xe in (x0, x1):                                          # testes tallades
        cv.vline(xe, y0, y0 + 9, ACER, 4.4 if xe == x0 else 1.0)
    for x in range(x0 + 6, x1, 23):                               # marques de guix
        cv.vline(x, y0 + 3, y0 + 6, PAPER, 3.0, 0.5)
    cv.darken(x0, y0 + 10, x1, y0 + 12, lambda x, y: 0.6)


def p_biga_ferro9(cv):
    """Biga de ferro-9 al bastidor, amb l'etiqueta de la caldera 4."""
    x0, x1, y0 = 80, 210, 73
    for x in range(x0, x1 + 1):
        sh = math.sin(x / 9.0) * 0.25
        cv.put(x, y0, F9, 6.4 + sh)
        cv.put(x, y0 + 1, F9, 5.2 + sh)
        for y in range(y0 + 2, y0 + 9):
            cv.put(x, y, F9, 3.0 + sh - (y - y0 - 2) * 0.18 + (1.0 if y == y0 + 2 else 0))
        cv.put(x, y0 + 9, F9, 4.6 + sh)
        cv.put(x, y0 + 10, F9, 2.4)
    cv.vline(x0, y0, y0 + 10, F9, 6.0)
    cv.vline(x1, y0, y0 + 10, F9, 2.0)
    for i in range(6):                                           # reflex llarg
        cv.hline(110 + i * 14, 116 + i * 14, y0 + 4, F9, 5.4)
    cv.glow(145, y0 + 5, 46, (150, 210, 255), 0.18)
    # etiqueta de cartró penjada amb un cordill
    cv.line(150, y0 + 10, 152, y0 + 13, PAPER, 2.4)
    cv.rect(146, y0 + 13, 162, y0 + 17 + 0, MANILA, lambda x, y: 4.2 - (y - y0 - 13) * 0.2)
    cv.hline(148, 160, y0 + 15, RED, 2.6)
    cv.put(147, y0 + 14, IRON, 1.0)


def p_serra(cv):
    """Serra de metall penjada al tauler (arc, fulla dentada i mànec)."""
    y = 62
    cv.hline(293, 324, y - 4, IRON, 3.8)
    cv.hline(293, 324, y - 3, IRON, 2.4)
    cv.rect(292, y - 4, 294, y + 4, IRON, 3.0)
    cv.rect(322, y - 4, 324, y + 4, IRON, 2.2)
    for x in range(294, 323):
        cv.put(x, y + 3, ACER, 5.4)
        cv.put(x, y + 4, ACER, 3.6 if x % 2 else 1.6)
    cv.put(304, y - 7, IRON, 3.6); cv.put(304, y - 6, IRON, 3.0); cv.put(304, y - 5, IRON, 2.4)
    for yy in range(y - 2, y + 8):                               # mànec de fusta
        for xx in range(325, 330):
            cv.put(xx, yy, WALNUT, 4.0 - (xx - 325) * 0.5 + (0.4 if yy < y else 0))
    cv.rect(326, y + 1, 328, y + 4, WALNUT, 0.8)


def p_llima(cv):
    """Llima fina penjada, amb el mànec de fusta a dalt."""
    for y in range(78, 88):
        cv.put(319, y, WALNUT, 4.2)
        cv.put(320, y, WALNUT, 3.2)
        cv.put(321, y, WALNUT, 1.8)
    cv.hline(318, 322, 88, GOLD, 4.0)
    for y in range(89, 108):
        w_ = 1 if y > 103 else 2
        for x in range(320 - w_ // 2, 321 + (w_ + 1) // 2):
            cv.put(x, y, ACER, (5.0 if x == 320 - w_ // 2 else 3.0) - (0.6 if y % 2 else 0))
    cv.put(320, 77, IRON, 3.0)


def p_marca(cv):
    carved_mark(cv, 252, 80)


# Animació de fons: el foc de les calderes es mou darrere la porta, la pols sura a la llum de la làmpada i de
# la lluna, i l'escletxa de sota la comporta tremola.
def _ambient_frames():
    from hd.rooms.fabrica_despatx import ambient_frames
    return ambient_frames(bg, LIGHT, 24, box=(0, 30, W - 1, 205))


ANIMS = {'ambient': {'frames': _ambient_frames, 'frameDuration': 130}}

PROPS = {
    'biga_acer': p_biga_acer,
    'biga_ferro9': p_biga_ferro9,
    'serra': p_serra,
    'llima': p_llima,
    'marca_pilar': p_marca,
}
