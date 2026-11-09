"""
Finals 2 i 3 · L'Estació d'Orís: el moll de l'hangar de La Gavina (gavina_hangar) en el món on no hi ha hagut mai
cap presó. Panells blancs i nets, plantes, el pilar 7 repintat, el rètol gran «ESTACIÓ D'ORÍS» (amb lletres de
bombetes, com el d'ALDAIA · FERRO-9 al pròleg) i un finestral a l'espai amb la Terra i la Lluna. Al moll, la
llançadora vella (ara amb els tres components); la directora jove (cabell coure, uniforme clar) espera la Vet, i
en Mos, sense granota de pres, descarrega caixes.
Llums: les franges del sostre (càlides), la Terra pel finestral (blava), les bombetes del rètol.
Pantalla sencera (sense barra de verbs). Les peces (rètol, plantes, terra) i els personatges es reutilitzen a final_cargol.
"""
import math
import random

from PIL import ImageOps

from hd.pix import (Canvas, Light, B4, W, H, hr, mix, ramp, TEAL, CYAN, PAPER, MANILA, WALNUT, GOLD, COPPER, BRICK,
                    IRON, STEEL, SIL, WARN)
from hd.rooms.proleg_gavina import espai, terra, lluna, vinyeta
from hd.rooms.fabrica_moll import shuttle, pillar, text, F9
from hd import characters as ch
from hd.characters import (M, Mat, person, hair_lvl, waist_band, redo_mouth, HAIR_COPPER, HAIR_WHITE, SKIN_PALE,
                           SKIN_OLD, GOLDPIN, STEELB, BELT, BOOT, CREAM, DENIM, GRAY_SHOE, VET, MOS, GUARDIA)

# ─── Rampes pròpies (fosc → clar) ───────────────────────────────────────────
WALLW = ramp((26, 30, 44), (58, 64, 82), (102, 110, 124), (150, 156, 164), (196, 198, 196), (226, 224, 214),
             (244, 240, 228), (255, 252, 242), n=10)                                   # panells blancs, càlids
DECK = ramp((22, 26, 38), (48, 54, 70), (84, 92, 106), (124, 130, 138), (164, 166, 166), (200, 198, 190),
            (228, 224, 212), (248, 244, 232), n=10)                                    # terra polit
MINT = ramp((8, 32, 34), (14, 62, 62), (26, 100, 96), (48, 142, 130), (92, 186, 166), (160, 226, 204), (220, 250, 236), n=8)
LEAF = ramp((8, 22, 20), (16, 44, 32), (30, 74, 44), (52, 108, 54), (88, 146, 66), (138, 186, 88), (196, 222, 132), n=8)
POT = ramp((40, 20, 18), (78, 38, 28), (124, 64, 40), (168, 96, 60), (206, 136, 90), (234, 184, 136), n=7)
BULB = [(110, 70, 40), (200, 140, 70), (250, 206, 120), (255, 236, 176), (255, 250, 226)]

FLOOR_Y = 187                      # on comença el terra
VP = (240, 120)                    # punt de fuga
WIN = (150, 58, 470, 176)          # el finestral
PILAR_CX = 120
SIGN_Y = 24                        # dalt de les lletres del rètol
EARTH = (466, 214, 152)            # la Terra (centre i radi, en coordenades de pantalla)
SHUTTLE = (266, 186)               # morro i eix de la llançadora

LIGHT = Light(ambient=0.9, vignette=(60, 26), floor_fade=(232, 60))
LIGHT.point(120, 8, r=200, k=1.2, squash=1.2)
LIGHT.point(370, 8, r=200, k=1.0, squash=1.2)
LIGHT.point(410, 150, r=170, k=0.8)                                # la Terra pel finestral
LIGHT.point(240, 34, r=130, k=0.9, squash=1.8)                     # el rètol


# ─── Lletres de 5×7 (i accents) ─────────────────────────────────────────────

FONT5 = {
    'E': ['#####', '#....', '#....', '####.', '#....', '#....', '#####'],
    'S': ['.####', '#....', '#....', '.###.', '....#', '....#', '####.'],
    'T': ['#####', '..#..', '..#..', '..#..', '..#..', '..#..', '..#..'],
    'A': ['.###.', '#...#', '#...#', '#####', '#...#', '#...#', '#...#'],
    'C': ['.####', '#....', '#....', '#....', '#....', '#....', '.####'],
    'I': ['###', '.#.', '.#.', '.#.', '.#.', '.#.', '###'],
    'O': ['.###.', '#...#', '#...#', '#...#', '#...#', '#...#', '.###.'],
    'D': ['####.', '#...#', '#...#', '#...#', '#...#', '#...#', '####.'],
    'R': ['####.', '#...#', '#...#', '####.', '#.#..', '#..#.', '#...#'],
    'G': ['.####', '#....', '#....', '#.###', '#...#', '#...#', '.###.'],
    'L': ['#....', '#....', '#....', '#....', '#....', '#....', '#####'],
    'M': ['#...#', '##.##', '#.#.#', '#.#.#', '#...#', '#...#', '#...#'],
    'N': ['#...#', '##..#', '#.#.#', '#..##', '#...#', '#...#', '#...#'],
    'B': ['####.', '#...#', '#...#', '####.', '#...#', '#...#', '####.'],
    'V': ['#...#', '#...#', '#...#', '#...#', '.#.#.', '.#.#.', '..#..'],
    'U': ['#...#', '#...#', '#...#', '#...#', '#...#', '#...#', '.###.'],
    '-': ['...', '...', '...', '###', '...', '...', '...'],
    '1': ['.#', '##', '.#', '.#', '.#', '.#', '.#'],
    "'": ['#', '#', '.', '.', '.', '.', '.'],
    ' ': ['..', '..', '..', '..', '..', '..', '..'],
}
ACUTE = {'Ó': 'O', 'Í': 'I'}


def text5_px(s, x0, y0, k=1):
    """Píxels (x, y, és_accent) d'un text en lletra de 5×7 a escala k; els accents van per sobre de y0."""
    out = []
    x = x0
    for c in s:
        base = ACUTE.get(c, c)
        g = FONT5[base]
        w = len(g[0])
        for j, row in enumerate(g):
            for i, b in enumerate(row):
                if b == '#':
                    out.append((x + i * k, y0 + j * k, False))
        if c in ACUTE:
            mx = x + (w // 2) * k
            out.append((mx + k, y0 - 3 * k, True))
            out.append((mx, y0 - 2 * k, True))
        x += (w + 1) * k
    return out, x - k


def text5_width(s, k=1):
    return text5_px(s, 0, 0, k)[1] + 1


def bulb_sign(cv, s, x0, y0, k=3, glow=True, chase=None, band=None):
    """Lletres de bombetes (com el rètol del pròleg): cada punt de la lletra és una bombeta de k×k.
    `chase`: x on passa una onada de llum (les bombetes de prop s'encenen més), d'amplada `band`."""
    pts, _ = text5_px(s, x0, y0, k)
    band = band or 4 * k
    for x, y, acc in pts:
        boost = max(0.0, 1 - abs(x - chase) / band) if chase is not None else 0.0
        for dy in range(k):
            for dx in range(k):
                edge = dx == k - 1 or dy == k - 1
                c = BULB[2] if edge else (BULB[4] if (dx, dy) == (0, 0) else BULB[3])
                if (x // k + y // k) % 2 and not edge:
                    c = mix(c, (255, 214, 140), 0.35)
                if boost > 0:
                    c = mix(c, (255, 255, 250) if not edge else BULB[4], min(1.0, boost * 1.3))
                cv.flat(x + dx, y + dy, c)
    if chase is not None and x0 - band < chase < x0 + _ + band:
        cv.glow(chase, y0 + 7 * k // 2, band * 2.4, (255, 236, 180), 0.5)
    if glow:
        for x, y, acc in pts[::3]:
            cv.glow(x + 1, y + 1, 7, (255, 220, 150), 0.22)


GULL = [(-5, 0), (-4, -1), (-3, -2), (-2, -2), (-1, -1), (0, 0), (1, -1), (2, -2), (3, -2), (4, -1), (5, 0)]


# ─── Peces ──────────────────────────────────────────────────────────────────

def ceiling(cv):
    """Sostre de panells blancs amb dues franges de llum càlida."""
    for y in range(0, 16):
        for x in range(W):
            lvl = 4.4 + y * 0.12 + (hr(x // 40, 1) - 0.5) * 0.3
            if x % 40 == 0:
                lvl -= 1.4
            cv.put(x, y, WALLW, lvl, 0.4)
    for x0, x1 in ((12, 228), (252, 468)):
        cv.hline(x0, x1, 5, WALLW, 2.6, 0)
        cv.hline(x0, x1, 6, [(255, 250, 236)], 0, 0)
        cv.hline(x0, x1, 7, [(255, 236, 196)], 0, 0)
        cv.hline(x0, x1, 8, WALLW, 3.0, 0)
        for x in range(x0, x1, 10):
            cv.glow(x, 8, 16, (255, 236, 200), 0.4)
        cv.hline(x0, x1, 6, [(255, 252, 244)], 0, 0)
        cv.hline(x0, x1, 7, [(255, 240, 206)], 0, 0)
    cv.hline(0, W - 1, 15, WALLW, 2.0, 0.4)
    cv.hline(0, W - 1, 16, WALLW, 6.4, 0.3)


def wall(cv, x0, x1, y0, y1):
    """Panells blancs arrodonits, amb juntes suaus i un sòcol de color menta."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            u, v = x % 44, (y - y0) % 42
            lvl = 4.6 + (hr(x // 44, (y - y0) // 42, 6) - 0.5) * 0.3 - v * 0.012
            if u == 0 or v == 0:
                lvl -= 1.6
            elif u == 1 or v == 1:
                lvl += 0.9
            cv.put(x, y, WALLW, lvl)
    # sòcol menta amb una línia de llum
    for y in range(y1 - 6, y1 + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, MINT, [5.6, 4.2, 3.6, 3.4, 3.2, 3.0, 1.8][y - y1 + 6])


def sign(cv, t=0.0):
    """El rètol: «ESTACIÓ D'ORÍS» en bombetes sobre una biga blanca, i una gavina a cada banda."""
    k = 3
    txt = "ESTACIÓ D'ORÍS"
    w = text5_width(txt, k)
    x0 = (W - w) // 2
    # biga que fa de suport
    by0, by1 = SIGN_Y - 9, SIGN_Y + 7 * k + 5
    for y in range(by0, by1 + 1):
        for x in range(x0 - 26, x0 + w + 26):
            lvl = 5.4 - (y - by0) * 0.03
            if y == by0:
                lvl = 7.2
            elif y == by1:
                lvl = 2.2
            elif y == by1 - 1:
                lvl = 3.6
            cv.put(x, y, WALLW, lvl, 0.3)
    for x in (x0 - 26, x0 + w + 25):
        cv.vline(x, by0, by1, WALLW, 2.6, 0.3)
    cv.darken(x0 - 26, by1 + 1, x0 + w + 25, by1 + 4, lambda x, y: 0.7 - (y - by1) * 0.18)
    # franja menta a sota
    cv.hline(x0 - 22, x0 + w + 21, by1 - 3, MINT, 4.6, 0)
    # les lletres, amb una ombra suau al panell
    pts, _ = text5_px(txt, x0, SIGN_Y, k)
    for x, y, _a in pts:
        cv.darken(x + 1, y + 2, x + k, y + k + 1, 0.35)
    # una onada de llum recorre les bombetes d'esquerra a dreta (a t=0 és fora del rètol)
    bulb_sign(cv, txt, x0, SIGN_Y, k, chase=x0 - 30 + (t % 1) * (w + 60), band=14)
    # gavines (l'emblema de l'estació) a cada banda
    for gx, flip in ((x0 - 16, False), (x0 + w + 15, True)):
        gull(cv, gx - 1, SIGN_Y + 11, flip, k=2)


def gull(cv, cx, cy, flip=False, k=1):
    """Una gavina estilitzada, en menta (l'emblema de l'estació: el nom de La Gavina hi és, però és una altra)."""
    if k > 1:
        for dx, dy in GULL:
            for a in range(k):
                for b in range(k + 1):
                    cv.put(cx + dx * k + a, cy + dy * k + b, MINT, 3.6 if b < k else 1.8, 0)
        return
    pts = [(-7, 0), (-6, -1), (-5, -2), (-4, -2), (-3, -1), (-2, 0), (-1, 1), (0, 1), (1, 0), (2, -1), (3, -2),
           (4, -2), (5, -1), (6, 0), (7, 0)]
    for dx, dy in pts:
        cv.put(cx + dx, cy + dy, MINT, 3.4, 0)
        cv.put(cx + dx, cy + dy + 1, MINT, 2.0, 0)
    cv.put(cx, cy + 2, MINT, 2.4, 0)


def window(cv):
    """El finestral: l'espai, la Terra i la Lluna, amb marc blanc arrodonit i muntants."""
    X0, Y0, X1, Y1 = WIN
    sky = Canvas()
    espai(sky, X0, X1, seed=11)
    lluna(sky, 206, 84, 7)
    terra(sky, EARTH[0], EARTH[1], EARTH[2], X0, X1)
    S = sky.P
    for y in range(Y0, Y1 + 1):
        for x in range(X0, X1 + 1):
            cv.flat(x, y, S[x, y])
    # reflexos al vidre: unes ratlles en diagonal, molt fluixes
    cv.tint(X0, Y0, X1, Y1, (200, 230, 255), lambda x, y: 0.10 if (x + y * 0.6) % 90 < 10 else (0.05 if (x + y * 0.6) % 90 < 16 else 0))
    # muntants (amb la cantonada arrodonida)
    MUL = [X0, 232, 314, 396, X1]
    for i, mx in enumerate(MUL):
        a, b = (mx - 4, mx + 3)
        for y in range(Y0 - 4, Y1 + 5):
            for x in range(a, b + 1):
                u = (x - a) / (b - a)
                cv.put(x, y, WALLW, 6.4 - u * 3.0 + (0.6 if x == a + 1 else 0))
    for y0_, y1_, top in ((Y0 - 6, Y0 - 1, True), (Y1 + 1, Y1 + 8, False)):
        for y in range(y0_, y1_ + 1):
            for x in range(X0 - 4, X1 + 4):
                t = (y - y0_) / (y1_ - y0_)
                lvl = (6.6 - t * 3.4) if top else (7.0 - t * 4.2)
                cv.put(x, y, WALLW, lvl)
    # cantonades arrodonides dins de cada vidre
    for i in range(len(MUL) - 1):
        xa, xb = MUL[i] + 4, MUL[i + 1] - 5
        for (cx, cy, sx, sy) in ((xa, Y0, 1, 1), (xb, Y0, -1, 1), (xa, Y1, 1, -1), (xb, Y1, -1, -1)):
            for dy in range(4):
                for dx in range(4):
                    if math.hypot(3.5 - dx, 3.5 - dy) > 3.6:
                        cv.put(cx + dx * sx, cy + dy * sy, WALLW, 5.6)
    cv.darken(X0, Y0, X1, Y0 + 2, 0.5)
    # cargols del marc i un ampit on reposen les plantes
    for mx in MUL:
        for y in (Y0 + 10, Y1 - 10):
            cv.put(mx, y, WALLW, 7.6)


def planter(cv, x0, x1, ytop, seed=0, tall=26, time=0.0):
    """Jardinera llarga amb plantes de fulla (sota el finestral)."""
    rnd = random.Random(seed)
    # mates de fulla rodona
    for _ in range((x1 - x0) // 16):
        bx, r = rnd.uniform(x0 + 8, x1 - 8), rnd.uniform(6, 9)
        by = ytop - r * 0.6
        for y in range(int(by - r), ytop + 1):
            for x in range(int(bx - r - 1), int(bx + r + 2)):
                nx, ny = (x - bx) / r, (y - by) / r
                d = nx * nx + ny * ny
                if d <= 1 + (hr(x // 2, y // 2, seed) - 0.5) * 0.5:
                    lvl = 3.2 - nx * 1.0 - ny * 1.2 + (hr(x // 2, y // 2, 9) - 0.5) * 1.6
                    cv.put(x, y, LEAF, lvl)
    # fulles, darrere la jardinera
    for _ in range((x1 - x0) // 3):
        bx = rnd.uniform(x0 + 2, x1 - 2)
        hgt = rnd.uniform(tall * 0.5, tall)
        lean = rnd.uniform(-0.5, 0.5)
        for i in range(int(hgt)):
            t = i / hgt
            x = bx + lean * i + math.sin(t * 3 + bx) * 1.2
            x += 1.1 * t * t * (math.sin(2 * math.pi * time + bx * 0.4) - math.sin(bx * 0.4))   # es gronxen
            y = ytop - i
            wdt = 1.6 * math.sin(t * math.pi) + 0.4
            for dx in range(-int(wdt), int(wdt) + 1):
                lvl = 2.6 + t * 2.6 - (0.9 if dx > 0 else 0) + (hr(int(x) + dx, y, 4) - 0.5) * 0.6
                cv.put(x + dx, y, LEAF, lvl)
    # flors petites
    for _ in range((x1 - x0) // 14):
        fx, fy = rnd.randint(x0 + 4, x1 - 4), ytop - rnd.randint(int(tall * 0.4), tall)
        col = rnd.choice(((255, 210, 120), (255, 160, 170), (250, 250, 240)))
        cv.flat(fx, fy, col); cv.flat(fx + 1, fy, mix(col, (120, 60, 60), 0.3)); cv.flat(fx, fy + 1, mix(col, (120, 60, 60), 0.3))
    # jardinera
    for y in range(ytop, ytop + 12):
        for x in range(x0, x1 + 1):
            lvl = 4.4 - (y - ytop) * 0.15 - (x - x0) / (x1 - x0) * 0.4
            if y == ytop:
                lvl = 6.6
            elif y == ytop + 1:
                lvl = 3.4
            cv.put(x, y, WALLW, lvl)
    cv.hline(x0 + 3, x1 - 3, ytop + 6, MINT, 4.0)
    for y in range(ytop + 2, ytop + 4):                               # la terra
        for x in range(x0 + 2, x1 - 1):
            if hr(x, y, 2) > 0.5:
                cv.put(x, y, POT, 1.0)


def big_plant(cv, cx, base, seed=3, h=72):
    """Una planta gran en test de terrissa: fulles llargues que cauen (com una kentia)."""
    rnd = random.Random(seed)
    # test
    for y in range(base - 22, base + 1):
        t = (y - base + 22) / 22
        hw = 11 - t * 3
        for x in range(math.floor(cx - hw), math.ceil(cx + hw) + 1):
            u = (x - cx) / hw
            lvl = 3.6 - u * 1.4 - u * u * 1.0 - t * 0.6
            if y < base - 19:
                lvl += 1.4
            cv.put(x, y, POT, lvl)
    cv.hline(cx - 12, cx + 12, base - 22, POT, 5.0)
    # tiges i fulles en arc
    fronds = []
    for i in range(9):
        ang = -math.pi / 2 + (i - 4) * 0.34 + rnd.uniform(-0.12, 0.12)
        ln = h * rnd.uniform(0.6, 1.0)
        fronds.append((ang, ln, i))
    fronds.sort(key=lambda f: -abs(f[0] + math.pi / 2))
    for ang, ln, i in fronds:
        x, y = cx, base - 22
        dx, dy = math.cos(ang), math.sin(ang)
        n = int(ln)
        for s in range(n):
            t = s / n
            x += dx
            y += dy
            dy += 0.028                                              # cau pel pes
            cv.put(x, y, LEAF, 2.4 + t * 1.2)
            if t > 0.12:
                for side in (-1, 1):                                 # folíols
                    lf = (1 - t) * 7 + 2
                    for k in range(1, int(lf)):
                        px = x - dy * side * k * 0.7 + dx * k * 0.5
                        py = y + dx * side * k * 0.7 + dy * k * 0.5 + k * 0.25
                        if (s + (1 if side > 0 else 0)) % 2 == 0:
                            lvl = 3.0 + t * 1.8 + (0.9 if side < 0 else -0.6) - k * 0.1
                            cv.put(px, py, LEAF, lvl)


def door(cv):
    """Porta corredissa cap a l'estació, amb un vidre que deixa veure un passadís lluminós."""
    x0, x1, y0, y1 = 16, 76, 98, FLOOR_Y - 1
    for y in range(y0 - 4, y1 + 1):
        for x in range(x0 - 4, x1 + 5):
            inside = x0 <= x <= x1 and y >= y0
            if not inside:
                cv.put(x, y, WALLW, 3.0 + (2.4 if x < x0 or y < y0 - 2 else 0) - (1.2 if x > x1 else 0))
    mid = (x0 + x1) // 2
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            lvl = 5.4 - (x - x0) * 0.012 - (y - y0) * 0.004
            if x in (mid, mid + 1):
                lvl = 2.2 if x == mid else 6.2
            cv.put(x, y, WALLW, lvl)
    # vidres amb el passadís de darrere (llum càlida)
    for gx in (x0 + 7, mid + 7):
        for y in range(y0 + 10, y0 + 46):
            for x in range(gx, gx + 16):
                d = (y - y0 - 10) / 36
                lvl = 4.6 - d * 1.2 + (1.2 if (x - gx) < 3 else 0)
                if 22 < y - y0 < 34 and (x - gx) % 7 == 3:
                    lvl -= 1.6
                cv.put(x, y, GOLD, lvl - 0.4, 0)
        cv.hline(gx, gx + 15, y0 + 10, WALLW, 2.0)
    # franja menta i nansa
    cv.hline(x0, x1, y0 + 56, MINT, 4.2)
    cv.hline(x0, x1, y0 + 57, MINT, 2.6)
    for hx in (mid - 4, mid + 5):
        cv.vline(hx, y0 + 60, y0 + 70, STEEL, 6.4)
    # rètol del moll damunt la porta
    cv.rect(x0 + 4, y0 - 15, x1 - 4, y0 - 5, MINT, 2.6, 0.3)
    cv.hline(x0 + 4, x1 - 4, y0 - 15, MINT, 4.4, 0.3)
    for x, y, _a in text5_px('MOLL L-1', x0 + 7, y0 - 13)[0]:
        cv.flat(x, y, (232, 252, 242))
    # pilot verd
    cv.flat(x1 + 8, y0 + 40, (150, 255, 190))
    cv.glow(x1 + 8, y0 + 40, 6, (120, 255, 170), 0.5)


def floor_deck(cv):
    """Terra de planxes clares i polides, en perspectiva: hi brilla el que hi ha a sobre (la paret, el finestral)
    i hi cauen les clapes de sol que entren pels vidres."""
    vx, vy = VP
    X0, Y0, X1, Y1 = WIN
    above = cv.img.copy().load()
    for y in range(FLOOR_Y, H):
        dep = y - vy
        for x in range(W):
            u = (x - vx) / dep * 3.0
            pl = math.floor(u)
            fr = (u - pl) * dep / 3.0
            t = 1100 / dep
            seg = math.floor(t / 2.4)
            seg_up = math.floor(1100 / (dep - 1) / 2.4)
            lvl = 3.5 + (hr(pl, seg, 2) - 0.5) * 0.35 - (y - FLOOR_Y) * 0.006
            if fr < 1:
                lvl -= 1.4
            elif seg != seg_up:
                lvl -= 1.2
            cv.put(x, y, DECK, lvl)
            # reflex de la paret: es fon a mesura que s'allunya de la vora
            d = y - FLOOR_Y
            sy = FLOOR_Y - 1 - int(d * 1.1)
            k = 0.42 * max(0.0, 1 - d / 52) ** 1.4
            if sy > 17 and k > 0.02 and fr >= 1:
                cv.flat(x, y, mix(cv.get(x, y), above[x, sy], k))
    sun_patches(cv)
    # línia menta de guia, cap a la porta
    for y in range(FLOOR_Y + 8, FLOOR_Y + 11):
        for x in range(0, W):
            if ((x - y * 2) // 8) % 2 == 0:
                cv.put(x, y, MINT, 4.6 - (y - FLOOR_Y - 8) * 0.6)
    cv.hline(0, W - 1, FLOOR_Y, WALLW, 2.0, 0.3)


PANES = [(154, 228), (236, 310), (318, 392), (400, 466)]
SUN_DX = 1.05                      # el sol entra de l'esquerra: les clapes es desplacen a la dreta


def sun_patches(cv, air=True):
    """Clapes de sol al terra (la forma dels vidres, estirada cap a nosaltres) i raigs suaus a l'aire."""
    X0, Y0, X1, Y1 = WIN
    warm = (255, 228, 170)
    for xa, xb in PANES:
        for y in range(FLOOR_Y + 3, FLOOR_Y + 66):
            d = y - FLOOR_Y - 3
            off = d * SUN_DX + 6
            grow = d * 0.28
            a, b = xa + off - grow * 0.2, xb + off + grow
            fade = max(0.0, 1 - d / 63)
            for x in range(max(0, int(a)), min(W - 1, int(b)) + 1):
                e = min(x - a, b - x)
                k = 0.55 * fade * min(1.0, e / 3)
                if k > B4[y & 3][x & 3] * 0.3:
                    cv.flat(x, y, mix(cv.get(x, y), warm, k))
        if air:
            # raig a l'aire: del vidre fins a la clapa
            for y in range(Y0 + 6, FLOOR_Y + 3):
                t = (y - Y0) / (FLOOR_Y + 3 - Y0)
                a = xa + 10 + t * 8
                b = xb - 6 + t * 10
                for x in range(max(0, int(a)), min(W - 1, int(b)) + 1):
                    k = 0.07 * (0.3 + t) * (0.6 + 0.4 * math.sin((x - y * 0.4) / 9))
                    if k > 0:
                        cv.flat(x, y, mix(cv.get(x, y), warm, k))


def reflect(cv, img, fx, fy, k=0.28, flip=False):
    """Reflex d'un fotograma al terra polit (de cap per avall, a sota dels peus, que es fon)."""
    from PIL import Image
    if flip:
        img = ImageOps.mirror(img)
        fx -= 48 - 2 * 25
    f = ImageOps.flip(img)
    P = f.load()
    ox, oy = int(fx - 25), int(fy)
    h = f.height
    for j in range(h - 84 + 1, h):
        y = oy + (j - (h - 84)) - 1
        jj = j
        for i in range(f.width):
            c = P[i, jj]
            if c[3] and 0 <= ox + i < W and FLOOR_Y < y < H:
                d = y - fy
                kk = k * max(0.0, 1 - d / 40)
                if kk > B4[y & 3][(ox + i) & 3] * 0.25:
                    cv.flat(ox + i, y, mix(cv.get(ox + i, y), c, kk))


def components(cv, x0, cy):
    """Els tres components de ferro-9, al seu lloc a la llançadora vella."""
    for i, ox in enumerate((72, 87, 102)):
        hx, hy = x0 + ox, cy + 10
        cv.rect(hx, hy, hx + 9, hy + 5, F9, lambda x, y: 4.6 - (y - hy) * 0.6)
        cv.hline(hx, hx + 9, hy, F9, 6.0)
        cv.put(hx + 1, hy + 2, F9, 7, 0)
        cv.glow(hx + 5, hy + 3, 6, (160, 210, 255), 0.25)


def crate(cv, x0, y0, w, h, label=True, seed=0):
    """Caixa de càrrega de l'estació (fusta clara, amb cantoneres menta)."""
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            lvl = 4.6 + (hr(x // 5, seed) - 0.5) * 0.4 - (0.9 if (y - y0) % 7 == 6 else 0) - (x - x0) / w * 0.6
            if y < y0 + 2:
                lvl = 6.0
            if x in (x0, x0 + w - 1):
                lvl = 5.6 if x == x0 else 3.0
            cv.put(x, y, WALNUT, lvl)
    for cx, cy in ((x0, y0), (x0 + w - 3, y0), (x0, y0 + h - 3), (x0 + w - 3, y0 + h - 3)):
        cv.rect(cx, cy, cx + 2, cy + 2, MINT, 3.8)
    if label:
        cv.rect(x0 + w // 2 - 6, y0 + h // 2 - 3, x0 + w // 2 + 5, y0 + h // 2 + 2, PAPER, 5.0)
        gull(cv, x0 + w // 2, y0 + h // 2 - 1)
    cv.darken(x0 - 1, y0 + h, x0 + w + 3, y0 + h + 2, lambda x, y: 0.7)


# ─── Personatges ────────────────────────────────────────────────────────────

LIGHTUNI = M((60, 66, 84), (112, 120, 134), (168, 174, 180), (210, 212, 210), (236, 234, 226), (250, 248, 240), (255, 255, 250))
WORK = M((22, 40, 44), (36, 66, 70), (54, 96, 98), (78, 128, 124), (110, 160, 150), (150, 192, 178))


def directora_jove_hair(fg, p, spec):
    """El cabell coure de les Orís, recollit en una cua baixa (sense gorra)."""
    hx, hy = p.head
    Hm = HAIR_COPPER
    tex = hair_lvl(hx - 1, hy - 2, 5.0, k=1.1, strands=0.3, freq=2.0)
    if p.f == 'D':
        fg.ell(hx, hy - 1.0, 7.2, 7.8, Hm, 2.8, amp=1.6, lvlfn=tex, clip=lambda x, y: y <= hy - 3 + ((x - hx) / 6.4) ** 2 * 7)
        fg.line(hx - 1, hy - 8, hx - 3, hy - 3.6, Hm, 1.6)                                       # clenxa
    elif p.f == 'L':
        fg.ell(hx + 1.2, hy - 0.8, 7.2, 7.8, Hm, 2.8, amp=1.6, lvlfn=tex,
               clip=lambda x, y: (x >= hx - 4.0 or y <= hy - 4.6) and not (x < hx + 2.4 and y > hy - 2.6))
        fg.limb((hx + 6.6, hy + 0.5), (hx + 7.6, hy + 11), 2.2, 1.4, Hm, 2.6, amp=1.6, cont=(0, 0.8),
                lvlfn=lambda x, y: 0.6 * math.sin(y * 1.3))                                       # cua
        fg.ell(hx + 6.4, hy + 0.6, 1.4, 1.0, GOLDPIN, 2.4, amp=1.0)                               # agulla
    else:
        fg.ell(hx, hy - 0.4, 7.2, 8.0, Hm, 2.8, amp=1.6, lvlfn=tex)
        fg.limb((hx, hy + 3), (hx + 0.4, hy + 13), 2.2, 1.4, Hm, 2.6, amp=1.6, cont=(0, 0.8))


def directora_jove_uniform(fg, p, spec):
    """Uniforme clar de l'estació: jaqueta creuada, coll menta, el pin de la gavina d'or."""
    b = p.bob
    hx = 24.5
    U = spec['top']
    TR = M((10, 50, 50), (26, 100, 96), (60, 160, 140), (130, 220, 196))
    if p.f == 'D':
        fg.poly([(hx - 3.2, 26.5 + b), (hx + 3.2, 26.5 + b), (hx, 31 + b)], TR, 2.2)
        for y in range(29 + b, 46 + b):
            fg.shade(hx + 2 - (y - 29 - b) * 0.12, y, -1.0, U)
        for y in (33, 38, 43):
            fg.px(hx + 3, y + b, GOLDPIN, 2)
        fg.px(hx - 5, 33 + b, GOLDPIN, 3); fg.px(hx - 4, 33 + b, GOLDPIN, 2); fg.px(hx - 6, 32 + b, GOLDPIN, 2)
    elif p.f == 'L':
        fg.poly([(20.0, 26.5 + b), (23.4, 26.5 + b), (21.0, 30.5 + b)], TR, 2.2)
        fg.px(21, 33 + b, GOLDPIN, 3); fg.px(20, 33 + b, GOLDPIN, 2)
        for y in range(29 + b, 46 + b):
            fg.shade(19.6, y, -0.6, U)
    for x in range(12, 38):
        g = fg.get(x, 46 + b)
        if g and g[0] in (U, spec['legs']):
            fg.px(x, 46 + b, TR, 1.6 if x < 24 else 1.2)


DIRECTORA_JOVE = dict(GUARDIA)
DIRECTORA_JOVE.update({
    'top': LIGHTUNI, 'legs': LIGHTUNI, 'sleeve': LIGHTUNI, 'shoes': BELT, 'shoe_lvl': 2.6,
    'hooks': {'hair': directora_jove_hair, 'torso': directora_jove_uniform},
})


def mos_feina(fg, p, spec):
    """En Mos amb granota de feina de l'estació (sense número): cremallera, cinturó i una gavina a la màniga."""
    b = p.bob
    O = spec['top']
    hx = 24.5
    if p.f == 'D':
        for y in range(29 + b, 45 + b):
            fg.shade(hx, y, -0.8, O)
        fg.poly([(hx - 2.4, 26.5 + b), (hx + 2.6, 26.5 + b), (hx + 0.5, 31 + b)], spec['skin'], 1.8)
    elif p.f == 'L':
        fg.poly([(20.0, 26.5 + b), (22.6, 26.5 + b), (20.6, 30 + b)], spec['skin'], 1.8)
    waist_band(fg, p, O, 45, col=BELT)


MOS_FEINA = dict(MOS)
MOS_FEINA.update({'legs': WORK, 'top': WORK, 'shoes': BOOT, 'hooks': {'hair': ch.mos_hair, 'torso': mos_feina}})


def stamp(cv, img, fx, fy, flip=False):
    """Enganxa un fotograma de persona amb els peus a (fx, fy) (els peus són a (25, 83) del fotograma)."""
    if flip:
        img = ImageOps.mirror(img)
        fx -= 48 - 2 * 25
    cv.img.alpha_composite(img, (int(fx - 25), int(fy - 83)))


def shadow(cv, cx, cy, rx, ry=3, k=0.6):
    cv.darken(cx - rx, cy - ry, cx + rx, cy + ry,
              lambda x, y: k * max(0.0, 1 - math.hypot((x - cx) / rx, (y - cy) / ry)) * 1.6, dither=True)


def held_crate(cv, x0, y0, w=20, h=14):
    """La caixa que porta en Mos, agafada per sota."""
    crate(cv, x0, y0, w, h, label=False, seed=4)
    gull(cv, x0 + w // 2, y0 + h // 2)


# ─── La pantalla ────────────────────────────────────────────────────────────

def estacio(cv, people=True, t=0.0):
    ceiling(cv)
    wall(cv, 0, W - 1, 17, FLOOR_Y - 1)
    window(cv)
    twinkle(cv, t)
    door(cv)
    # el pilar 7, repintat de nou: el de la fàbrica, que ara és la columna d'honor de l'estació
    pillar(cv, PILAR_CX, 17, FLOOR_Y - 1, aged=False)
    cv.rect(PILAR_CX - 9, 128, PILAR_CX + 9, 134, GOLD, lambda x, y: 4.2 - (y - 128) * 0.3)    # placa de llautó
    for x in range(PILAR_CX - 7, PILAR_CX + 8, 2):
        cv.put(x, 131, GOLD, 1.6)
    sign(cv, t)
    floor_deck(cv)
    cv.darken(PILAR_CX - 16, FLOOR_Y, PILAR_CX + 16, FLOOR_Y + 5, lambda x, y: 0.7 - abs(x - PILAR_CX) / 24)
    # jardineres sota el finestral, i plantes grans
    planter(cv, 158, 268, 175, seed=1, tall=22, time=t)
    planter(cv, 404, 466, 175, seed=2, tall=24, time=(t * 2) % 1)
    big_plant(cv, 96, 200, seed=5, h=60)
    # cistella penjant amb una heura, a l'esquerra
    hang_ivy(cv, 46, 22, t)
    # la llançadora vella, aterrada, amb els tres components al lloc
    sx, sy = SHUTTLE
    shadow(cv, sx + 66, sy + 46, 80, 5, 0.45)
    shuttle(cv, sx, sy, aged=True)
    components(cv, sx, sy)
    beacon(cv, sx, sy, t)
    # caixes descarregades al costat de la cua
    crate(cv, 404, 212, 30, 22, seed=1)
    crate(cv, 410, 192, 24, 20, seed=2)
    crate(cv, 372, 226, 26, 18, seed=3)
    if people:
        # la directora espera a la porta; la Vet hi va, girada cap a ella; en Mos descarrega
        for spec, f, x, y, flip, talk in ((DIRECTORA_JOVE, 'L', 66, 250, True, True), (VET, 'L', 206, 258, False, False),
                                           (MOS_FEINA, 'L', 452, 262, False, False)):
            img = person(spec, f, talk=talk)
            reflect(cv, img, x, y, flip=flip)
            shadow(cv, x, y, 13, 3, 0.7)
            stamp(cv, img, x, y, flip=flip)
        held_crate(cv, 438, 223, 18, 13)


def hang_ivy(cv, cx, top, t=0.0):
    """Una test penjat amb heura que cau."""
    cv.vline(cx - 6, top, top + 24, STEEL, 5.0)
    cv.vline(cx + 6, top, top + 24, STEEL, 5.0)
    cv.disc(cx, top + 28, 9, 5, POT, lambda nx, ny: 3.6 - nx - ny * 0.6)
    rnd = random.Random(8)
    for i in range(7):
        x = cx - 9 + i * 3 + rnd.uniform(-1, 1)
        ln = rnd.randint(14, 44)
        for s in range(ln):
            xx = x + math.sin(s / 5 + i) * 1.5
            xx += 1.4 * (s / 44) ** 1.5 * (math.sin(2 * math.pi * t - s / 14 + i * 0.3) - math.sin(-s / 14 + i * 0.3))
            yy = top + 28 + s
            if s % 3 == 0:
                cv.put(xx - 1, yy, LEAF, 3.6 - s * 0.02)
                cv.put(xx + 1, yy + 1, LEAF, 2.4)
            cv.put(xx, yy, LEAF, 2.8 + (s % 3 == 1) * 1.0)


# ─── Animació de fons ──────────────────────────────────────────────────────
# Tot és funció de t ∈ [0, 1) i fa bucle (t=1 ≡ t=0); a t=0 cap efecte no canvia el fons quiet.

def twinkle(cv, t):
    """Algunes estrelles del finestral parpellegen, cadascuna al seu ritme."""
    if not t:
        return
    X0, Y0, X1, Y1 = WIN
    rnd = random.Random(31)
    for _ in range(400):
        x, y = rnd.randint(X0 + 5, X1 - 5), rnd.randint(Y0 + 3, Y1 - 3)
        m = rnd.randint(1, 3)
        c = cv.get(x, y)
        if sum(c[:3]) > 330 and sum(cv.get(x + 2, y)[:3]) < 150 and sum(cv.get(x - 2, y)[:3]) < 150:
            k = 0.75 * abs(math.sin(math.pi * m * t))
            cv.flat(x, y, mix(c, (20, 18, 40), k))


def dust(cv, t):
    """Pols que sura dins els raigs de sol: baixa a poc a poc i s'encén i s'apaga."""
    if not t:
        return
    X0, Y0, X1, Y1 = WIN
    rnd = random.Random(44)
    for xa, xb in PANES:
        for _ in range(9):
            u, v = rnd.random(), rnd.random()
            m = rnd.choice((1, 2, 3))
            b = math.sin(math.pi * (m * t)) ** 2 * rnd.uniform(0.5, 1.0)
            vv = (v + t) % 1                                         # baixa (una volta per bucle)
            y = Y0 + 10 + vv * (162 - Y0 - 10)
            tt = (y - Y0) / (FLOOR_Y + 3 - Y0)
            x = xa + 14 + tt * 8 + u * (xb - xa - 26) + 2 * math.sin(2 * math.pi * (t + u))
            if b > 0.15 and 0 <= x < W:
                cv.flat(x, y, mix(cv.get(x, y), (255, 240, 200), min(1.0, b)))


def beacon(cv, sx, sy, t):
    """Una llumeta verda a l'aleta de la llançadora: dos cops per bucle (apagada a t=0)."""
    on = 0.25 <= t % 0.5 < 0.30
    if on:
        x, y = sx + 130 - 1, sy - 24 - 15
        cv.flat(x, y, (170, 255, 190)); cv.flat(x + 1, y, (120, 230, 160))
        cv.glow(x + 0.5, y, 7, (130, 255, 170), 0.6)


def _ambient_frames(n=16):
    """Fotogrames de l'animació de fons: només els píxels que canvien respecte del fons quiet."""
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


def grade(cv):
    """Color de conjunt: càlid a dalt (les franges del sostre) i blavós a prop de la Terra."""
    cv.tint(0, 0, W - 1, H - 1, (255, 214, 160), lambda x, y: 0.10 * max(0.0, 1 - y / 200))
    ex, ey, er = EARTH
    cv.tint(300, 60, W - 1, H - 1, (90, 150, 255), lambda x, y: 0.10 * max(0.0, 1 - math.hypot(x - ex, y - ey - 30) / 200))


def bg(cv, t=0.0):
    estacio(cv, t=t)
    dust(cv, t)
    grade(cv)
    vinyeta(cv, 0.45)


PROPS = {}
ANIMS = {'ambient': {'frames': _ambient_frames, 'frameDuration': 110}}
