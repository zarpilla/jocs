"""
**El dibuix pla de sempre** (font de les textures de la sala en 3D, gavina_passadis.py).

Passadís del mòdul C (La Gavina, Vet), a 640×360 (hd/rooms/gavina_passadis.py redibuixat a ×4/3): el vestíbul de
les cel·les i el passadís que s'enfonsa cap a l'hangar.
Llums: aplic de reixa sobre la cel·la 9, tira de llum sobre el cartell del somriure, fluorescents del passadís,
i el pilot vermell de la porta del fons.

Aquest mòdul també té els materials comuns de La Gavina a 640 (paret d'acer, terra de planxes, rètols amb la
lletra de 4×7, el somriure de la corporació, la llum amb memòria), que fan servir l'arxiu, la Sala de la Memòria
i els finals.
"""
import math

from PIL import Image, ImageChops

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from hd.pix import (Canvas, Light, W, H, STEEL, PANEL, CYAN, TEAL, WARN, ORANGE, RED, PAPER, IRON,  # noqa: F401
                    SPACE, GRAY, PINK)
from hd.rooms.gavina_passadis import (HULL, DECK, LAMPW, ALARM, RUSTG, PILOT, SIGN, CORPG,  # noqa: F401
                                      FONT as FONT5)

# ─── Materials comuns de La Gavina ─────────────────────────────────────────

FLOOR_Y = 205            # primera fila de terra (la paret acaba a 204)
WALL_B = FLOOR_Y - 1


def hr(*a):
    """Soroll determinista (0..1) a partir d'enters, com hd.pix.hr però molt més ràpid (un hash d'enters en
    lloc d'un Random nou a cada crida): a 640 n'hi ha mig milió per fotograma."""
    h = 0x9E3779B9
    for v in a:
        h = ((h ^ (int(v) & 0xFFFFFFFF)) * 0x01000193) & 0xFFFFFFFF
        h ^= h >> 15
    h = (h * 0x2C1B3C6D) & 0xFFFFFFFF
    h ^= h >> 12
    h = (h * 0x297A2D39) & 0xFFFFFFFF
    h ^= h >> 15
    return h / 4294967296.0


class CachedLight(Light):
    """Una Light que recorda el que ha calculat a cada píxel: les animacions redibuixen la sala sencera moltes
    vegades i el camp de llum no canvia."""

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self._memo = {}

    def __call__(self, x, y):
        key = (x, y)
        v = self._memo.get(key)
        if v is None:
            v = self._memo[key] = Light.__call__(self, x, y)
        return v


# ─── Lletra dels rètols: 4×7 (M, T, V, W i Y més amples; I, 1 i signes més estrets) ──
# (la de 3×5 de 480 continua a FONT5, per a rètols petits o llunyans: text(..., small=True))
FONT7 = {k: v.split('/') for k, v in {
    'A': '.##./#..#/#..#/####/#..#/#..#/#..#', 'B': '###./#..#/#..#/###./#..#/#..#/###.',
    'C': '.###/#.../#.../#.../#.../#.../.###', 'D': '###./#..#/#..#/#..#/#..#/#..#/###.',
    'E': '####/#.../#.../###./#.../#.../####', 'F': '####/#.../#.../###./#.../#.../#...',
    'G': '.###/#.../#.../#.##/#..#/#..#/.###', 'H': '#..#/#..#/#..#/####/#..#/#..#/#..#',
    'I': '###/.#./.#./.#./.#./.#./###', 'J': '...#/...#/...#/...#/...#/#..#/.##.',
    'K': '#..#/#..#/#.#./##../#.#./#..#/#..#', 'L': '#.../#.../#.../#.../#.../#.../####',
    'M': '#...#/##.##/#.#.#/#.#.#/#...#/#...#/#...#', 'N': '#..#/##.#/##.#/#.##/#.##/#..#/#..#',
    'O': '.##./#..#/#..#/#..#/#..#/#..#/.##.', 'P': '###./#..#/#..#/###./#.../#.../#...',
    'Q': '.##./#..#/#..#/#..#/#..#/#.#./.#.#', 'R': '###./#..#/#..#/###./#.#./#..#/#..#',
    'S': '.###/#.../#.../.##./...#/...#/###.', 'T': '#####/..#../..#../..#../..#../..#../..#..',
    'U': '#..#/#..#/#..#/#..#/#..#/#..#/.##.', 'V': '#...#/#...#/#...#/#...#/.#.#./.#.#./..#..',
    'W': '#...#/#...#/#...#/#.#.#/#.#.#/##.##/#...#', 'X': '#..#/#..#/.##./.##./.##./#..#/#..#',
    'Y': '#...#/#...#/.#.#./..#../..#../..#../..#..', 'Z': '####/...#/..#./..#./.#../#.../####',
    '0': '.##./#..#/#.##/#..#/##.#/#..#/.##.', '1': '.#./##./.#./.#./.#./.#./###',
    '2': '.##./#..#/...#/..#./.#../#.../####', '3': '###./...#/...#/.##./...#/...#/###.',
    '4': '#..#/#..#/#..#/####/...#/...#/...#', '5': '####/#.../###./...#/...#/#..#/.##.',
    '6': '.##./#.../#.../###./#..#/#..#/.##.', '7': '####/...#/..#./..#./.#../.#../.#..',
    '8': '.##./#..#/#..#/.##./#..#/#..#/.##.', '9': '.##./#..#/#..#/.###/...#/...#/.##.',
    '-': '.../.../.../###/.../.../...', '.': '././././././#', ':': './#/./././#/.',
    '·': './././#/././.', ' ': '.../.../.../.../.../.../...', "'": '#/#/././././.', ',': './././././#/#',
    '/': '..#/..#/.#./.#./.#./#../#..', '!': '#/#/#/#/#/./#', '?': '.##./#..#/...#/..#./.#../..../.#..',
}.items()}
TEXT_H = 7
# accents (dibuixats dues files per sobre de la lletra) i la ce trencada (la cua, per sota)
_ACC = {'À': ('A', 'g'), 'È': ('E', 'g'), 'É': ('E', 'a'), 'Í': ('I', 'a'), 'Ò': ('O', 'g'), 'Ó': ('O', 'a'),
        'Ú': ('U', 'a'), 'Ï': ('I', 'd'), 'Ü': ('U', 'd'), 'Ç': ('C', 'c')}


def _glyph(ch, small):
    if small:
        g = FONT5.get(ch, FONT5[' '])
        return [g[j * 3:j * 3 + 3] for j in range(5)]
    return FONT7.get(ch, FONT7[' '])


def text(cv, x, y, s, rmp, lvl, lit=0.4, gap=1, small=False):
    """Rètols: lletres de 4×7 píxels (o les de 3×5 de 480 amb `small`). Torna la x on acaba.
    Amb la lletra gran, els accents (À È É Í Ò Ó Ú) ocupen les dues files de sobre i la cua de la Ç la de sota."""
    for ch in s.upper():
        base, acc = _ACC.get(ch, (ch, None))
        if small:
            acc = None
            base = {'À': 'A', 'È': 'E', 'É': 'E', 'Í': 'I', 'Ò': 'O', 'Ó': 'O', 'Ú': 'U', 'Ç': 'C'}.get(ch, base)
        g = _glyph(base, small)
        w = len(g[0])
        for j, row in enumerate(g):
            for i, c in enumerate(row):
                if c == '#':
                    cv.put(x + i, y + j, rmp, lvl, lit)
        m = w // 2
        if acc == 'g':
            cv.put(x + m - 1, y - 2, rmp, lvl, lit)
            cv.put(x + m, y - 1, rmp, lvl, lit)
        elif acc == 'a':
            cv.put(x + m + (1 if w > 3 else 0), y - 2, rmp, lvl, lit)
            cv.put(x + m - (0 if w > 3 else 1), y - 1, rmp, lvl, lit)
        elif acc == 'd':
            cv.put(x, y - 2, rmp, lvl, lit)
            cv.put(x + w - 1, y - 2, rmp, lvl, lit)
        elif acc == 'c':
            cv.put(x + m, y + 7, rmp, lvl, lit)
            cv.put(x + m - 1, y + 8, rmp, lvl, lit)
        x += w + gap
    return x


def text_w(s, gap=1, small=False):
    """Amplada en píxels d'un rètol escrit amb text()."""
    if not s:
        return 0
    n = 0
    for ch in s.upper():
        base = _ACC.get(ch, (ch, None))[0]
        n += len(_glyph(base, small)[0]) + gap
    return n - gap


def smile(cv, cx, cy, r, lit=0.3, lvl=3.6):
    """El somriure de la corporació: cara groga, ulls i un somriure massa ample (amb les comissures marcades)."""
    cv.disc(cx, cy, r, r, WARN, lambda nx, ny: lvl + 0.5 - (1.0 if nx * 0.6 + ny * 0.8 > 0.55 else 0) +
            (1.0 if nx + ny < -0.9 else 0) - (0.6 if nx * nx + ny * ny > 0.86 else 0), lit)
    ex = max(1, round(r * 0.36))
    ey = cy - round(r * 0.3)
    for s in (-1, 1):
        cv.put(cx + s * ex, ey, WARN, 0.0, 0)
        if r >= 5:
            cv.put(cx + s * ex, ey + 1, WARN, 0.0, 0)
        if r >= 9:
            cv.put(cx + s * ex - s, ey, WARN, 0.3, 0)
            cv.put(cx + s * ex - s, ey + 1, WARN, 0.3, 0)
            cv.put(cx + s * ex, ey - 1, WARN, 5.2, 0)                  # la lluentor de l'ull
    rr = r * 0.62
    step = 4 if r >= 9 else (6 if r >= 5 else 14)
    for a in range(10, 171, step):
        x = round(cx + math.cos(math.radians(a)) * rr)
        y = round(cy + math.sin(math.radians(a)) * rr * 0.9)
        cv.put(x, y, WARN, 0.2, 0)
        if r >= 9 and 40 < a < 140:
            cv.put(x, y + 1, WARN, 0.9, 0)                               # el llavi, més gruixut al mig
    if r >= 7:
        for s in (-1, 1):                                                 # comissures
            x = round(cx + s * rr * math.cos(math.radians(10)))
            cv.put(x + s, round(cy + rr * 0.9 * math.sin(math.radians(10))) - 1, WARN, 0.4, 0)


def rivet(cv, x, y, rmp=HULL, lvl=4.0):
    """Rebló de cap bombat, 3×3: lluu a dalt a l'esquerra, ombra a baix a la dreta."""
    cv.put(x + 1, y, rmp, lvl + 0.6)
    cv.put(x, y + 1, rmp, lvl + 0.6)
    cv.put(x + 1, y + 1, rmp, lvl + 1.4)
    cv.put(x + 2, y + 1, rmp, lvl - 0.6)
    cv.put(x + 1, y + 2, rmp, lvl - 1.0)
    cv.put(x + 2, y + 2, rmp, lvl - 2.2)


def hazard(cv, x0, y0, x1, y1, lit=1.0, lvl=3.4, w=5):
    """Franges de perill grogues i negres en diagonal, gastades a les vores."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if ((x + y) // w) % 2:
                worn = 0.7 if hr(x // 2, y, 91) > 0.93 else 0.0
                cv.put(x, y, WARN, lvl - (0.6 if y == y1 else 0) + (0.3 if y == y0 else 0) - worn, lit)
            else:
                cv.put(x, y, HULL, 0.6 + (0.3 if y == y0 else 0), lit)


def wall(cv, x0, x1, y0=0, y1=WALL_B, rail=149, base=3.0, seed=0, pw=53):
    """Paret d'acer frontal: planxes reblades a dalt, passamà, sòcol de costelles i ombra de terra."""
    seam = 67
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            px = (x + seed * 9) % pw
            row = 0 if y < seam else 1
            pid = (x + seed * 9) // pw
            g = (hr(pid, row, seed) - 0.5) * 0.35 + (hr(x // 4, 5) - 0.5) * 0.12 + (hr(x // 2, y // 5, 6) - 0.5) * 0.08
            if y < rail - 4:
                # planxes grans: costura vertical, costura horitzontal a y=67
                if px == 0 or y == seam:
                    lvl = 0.8
                elif px == 1 or y == seam + 1:
                    lvl = base + 1.1
                elif px == pw - 1 or y == seam - 1:
                    lvl = base - 0.7
                else:
                    lvl = base + g - abs(px - pw / 2) / pw * 0.25
                    # regalims de brutícia sota les costures
                    if hr(pid, x % pw, 17 + row) > 0.9 and 0 < (y - (seam + 2 if row else y0)) < 6 + hr(x, 3, seed) * 22:
                        lvl -= 0.35
            elif y < rail + 4:
                lvl = [base + 1.8, base + 1.5, base + 1.0, base + 0.5, base - 0.3, base - 0.8, base - 1.4, base - 2.0][y - rail + 4]
            else:
                # sòcol: costelles verticals
                k = (x + seed) % 8
                lvl = base - 0.6 + [0.0, 0.7, 0.5, 0.3, 0.1, -0.2, -0.6, -1.0][k]
                if y >= y1 - 5:
                    lvl -= 0.5
                if y == rail + 4:
                    lvl -= 0.6                                          # ombra del passamà
            lvl -= max(0.0, 1 - (y - y0) / 19) * 1.0                    # ombra del sostre
            cv.put(x, y, HULL, lvl)
    for xp in range(x0 - ((x0 + seed * 9) % pw), x1 + 1, pw):
        for xx in (xp + 5, xp + pw - 8):
            if x0 <= xx <= x1 - 2:
                for yy in (y0 + 24, seam - 6, seam + 7, rail - 12):
                    if y0 <= yy < rail - 6:
                        rivet(cv, xx, yy, HULL, base + 0.6)
    # ombra de contacte paret-terra
    cv.darken(x0, y1 - 3, x1, y1, 0.8)


def deck(cv, vx, vy, S, K, ou=0.0, ov=0.0, y0=FLOOR_Y, y1=H - 1, inside=None, base=2.5, wall_y=WALL_B, extra=None):
    """Terra de planxes d'acer en perspectiva (punt de fuga vx, vy). inside(x, y) → bool per retallar."""
    for y in range(y0, y1 + 1):
        d = y - vy
        if d <= 0:
            continue
        v = K / d + ov
        vi = math.floor(v)
        fv = (v - vi) * d * d / K                                     # distància en píxels a la costura
        fv2 = (vi + 1 - v) * d * d / K
        for x in range(W):
            if inside and not inside(x, y):
                continue
            u = (x - vx) / d * S + ou
            ui = math.floor(u)
            fu = (u - ui) * d / S
            fu2 = (ui + 1 - u) * d / S
            g = (hr(ui, vi, 31) - 0.5) * 0.5
            lvl = base + g
            # trama antilliscant: rombets en relleu
            if (x + 2 * y) % 6 == 0 and (x - 2 * y) % 9 < 3 and hr(x, y, 2) > 0.3:
                lvl += 0.4
            # rascades i taques de cada planxa
            if hr(ui, vi, x // 3, 5) > 0.985:
                lvl -= 0.4
            if fu < 1 or fv2 < 1:
                lvl = 0.5                                              # costura fosca
            elif fu < 2 or fv2 < 2:
                lvl += 0.6                                             # cantell il·luminat
            elif fu2 < 1.6 or fv < 1.4:
                lvl -= 0.5
            # cargols a les cantonades
            if d > 53 and 4 <= fu < 5.8 and 3.3 <= fv2 < 4.9:
                lvl += 1.4 if (fu < 5 and fv2 < 4.2) else 0.4
            if y < wall_y + 11:
                lvl -= (wall_y + 11 - y) / 11 * 1.2                   # ombra de contacte amb la paret
            if extra:
                lvl += extra(x, y)
            cv.put(x, y, DECK, lvl)


def pool(cx, cy, rx, ry, k, y0=FLOOR_Y):
    """Taca de llum el·líptica al terra."""
    def f(x, y):
        if y < y0:
            return 0.0
        d = math.hypot((x - cx) / rx, (y - cy) / ry)
        return k * max(0.0, 1 - d) ** 1.6 if d < 1 else 0.0
    return f


def wall_lamp(cv, cx, cy, w=19):
    """Aplic de reixa: caixa d'acer amb el tub encès, una gàbia i els cargols de la caixa."""
    cv.rect(cx - w // 2 - 3, cy - 5, cx + w // 2 + 3, cy + 5, HULL, lambda x, y: 3.0 - (y - cy) * 0.25)
    cv.hline(cx - w // 2 - 3, cx + w // 2 + 3, cy - 5, HULL, 4.4)
    cv.rect(cx - w // 2, cy - 3, cx + w // 2, cy + 3, LAMPW, lambda x, y: 4.2 - abs(y - cy) * 0.55, 0)
    for x in range(cx - w // 2, cx + w // 2 + 1, 4):
        cv.vline(x, cy - 4, cy + 4, HULL, 2.0, 0.3)
        cv.vline(x + 1, cy - 4, cy + 4, HULL, 1.0, 0.3)
    cv.hline(cx - w // 2 - 1, cx + w // 2 + 1, cy - 4, HULL, 2.2, 0.3)
    cv.hline(cx - w // 2 - 1, cx + w // 2 + 1, cy + 4, HULL, 2.2, 0.3)
    for sx in (cx - w // 2 - 2, cx + w // 2 + 2):
        cv.put(sx, cy - 3, HULL, 5.0)
        cv.put(sx, cy + 3, HULL, 4.4)
    cv.hline(cx - w // 2 - 3, cx + w // 2 + 3, cy + 6, HULL, 0.6)
    cv.glow(cx, cy, w + 19, (190, 230, 255), 0.55)


def diff(frame, base):
    """Només els píxels que canvien respecte del fons (la resta, transparent)."""
    d = ImageChops.difference(frame.convert('RGB'), base.convert('RGB'))
    r, g, b = d.split()
    mask = ImageChops.lighter(ImageChops.lighter(r, g), b).point(lambda v: 255 if v else 0)
    fr = Image.new('RGBA', frame.size, (0, 0, 0, 0))
    fr.paste(frame, mask=mask)
    return fr


def ambient_frames(bg_fn, light, n):
    """N fotogrames transparents amb només els píxels que canvien respecte de bg(t=0)."""
    base = Canvas(light=light)
    bg_fn(base)
    frames = []
    for i in range(n):
        cv = Canvas(light=light)
        bg_fn(cv, t=i / n)
        frames.append(diff(cv.img, base.img))
    return frames


# ─── Passadís ──────────────────────────────────────────────────────────────

VX, VY = 389, 127                   # punt de fuga del passadís
OPEN_X0, OPEN_X1, OPEN_TOP = 200, 424, 32
FAR = 0.35                          # fondària de la paret del fons (escala)
FS, FK, FOU, FOV = 2.444, 580.8, -0.445, -0.445   # planxes del terra (la rajola: u −4..−3, v 4..5)
DOOR_CX = 363                       # centre de la porta de l'hangar (la línia groga hi va a parar)


def cp(X, Y, f):
    """Punt del pla davanter (X, Y) portat a la fondària f (1 = davant, FAR = fons)."""
    return VX + (X - VX) * f, VY + (Y - VY) * f


FAR_L, FAR_T = cp(OPEN_X0, OPEN_TOP, FAR)
FAR_R, FAR_B = cp(OPEN_X1, WALL_B, FAR)


def corridor_light(x, y):
    """Llum dels fluorescents del passadís: cau amb la fondària, més forta al terra del mig."""
    if OPEN_X0 <= x <= OPEN_X1 and y >= 133:
        return max(0.0, 1 - abs(x - 327) / 120) * 0.7
    return 0.0


LIGHT = CachedLight(vignette=(93, 45), floor_fade=(264, 45))
LIGHT.point(139, 35, r=173, k=2.6, squash=0.9, down=True)            # aplic sobre la cel·la 9
LIGHT.point(499, 30, r=160, k=2.3, squash=1.0, down=True)            # tira sobre el cartell
LIGHT.add(pool(139, 237, 147, 40, 2.4))
LIGHT.add(pool(499, 237, 133, 37, 2.1))
LIGHT.add(pool(333, 208, 85, 35, 1.2))                               # el passadís aboca llum al vestíbul
LIGHT.add(corridor_light)


def floor_inside(x, y):
    """Terra visible: tot per sota de la paret, i dins del passadís fins a la paret del fons."""
    if y >= FLOOR_Y:
        return True
    if y <= FAR_B:
        return False
    f = (y - VY) / (WALL_B - VY)
    xl, xr = VX + (OPEN_X0 - VX) * f, VX + (OPEN_X1 - VX) * f
    return xl <= x <= xr


def red_alarm(x, y):
    d = math.hypot(x - DOOR_CX, (y - 96) * 1.1)
    return max(0.0, 1 - d / 93) ** 2


def bg(cv, t=0.0, arrencat=False):
    """`t` (0..1): moment del cicle de l'animació de fons (t = 0 és el fons quiet)."""
    tt = t                                   # (dins la funció, `t` es fa servir per a altres coses)
    ph = 2 * math.pi * tt
    al = math.sin(ph * 2)                    # l'alarma del fons polsa (dues vegades per cicle)
    tube_off = 0.40 <= tt < 0.44             # un tub del passadís parpelleja (un fotograma)
    strip_off = (0.79 <= tt < 0.83) or (0.875 <= tt < 0.915)   # la tira del cartell fa dues pampallugues
    # ─── Passadís (darrere de tot) ────────────────────────────────────────
    # sostre del passadís
    for y in range(OPEN_TOP, round(FAR_T) + 1):
        f = (VY - y) / (VY - OPEN_TOP)
        xl, xr = VX + (OPEN_X0 - VX) * f, VX + (OPEN_X1 - VX) * f
        z = 1 / f
        for x in range(math.floor(xl), math.ceil(xr) + 1):
            lvl = 1.2 - (z - 1) * 0.35
            zz = (z * 3.2) % 1
            if zz < 0.08 * z:
                lvl -= 0.6                                               # costelles del sostre
            elif zz < 0.12 * z:
                lvl += 0.3
            cv.put(x, y, HULL, lvl, 0.3)
    # tubs fluorescents del sostre (barres que s'empetiteixen)
    for f in (0.86, 0.66, 0.5, 0.4):
        (xa, _), (xb, _) = cp(273, OPEN_TOP, f), cp(367, OPEN_TOP, f)
        ya = round(VY + (OPEN_TOP + 13 - VY) * f)
        th = max(1, round(4 * f))
        off = tube_off and f == 0.66
        cv.rect(round(xa) - 1, ya - 1, round(xb) + 1, ya - 1, HULL, 1.6, 0)              # la caixa
        cv.rect(round(xa), ya, round(xb), ya + th - 1, LAMPW, 1.6 if off else 3.6, 0)
        if not off and th >= 3:
            cv.hline(round(xa) + 2, round(xb) - 2, ya + 1, LAMPW, 4.6, 0)              # el filament, més blanc
        for ex in (round(xa), round(xb)):
            cv.vline(ex, ya, ya + th - 1, HULL, 2.4, 0)                                  # els caps del tub
        cv.hline(round(xa) - 1, round(xb) + 1, ya + th, HULL, 0.6, 0)
        cv.glow((xa + xb) / 2, ya + 1, 35 * f, (180, 225, 255), 0.12 if off else 0.4)

    # parets laterals del passadís
    def side(x0, sgn):
        """Paret lateral: f a partir de x, coordenada vertical al pla davanter."""
        lo, hi = (math.floor(min(x0, FAR_L if sgn < 0 else FAR_R)), math.ceil(max(x0, FAR_L if sgn < 0 else FAR_R)))
        for x in range(lo, hi + 1):
            f = (x - VX) / (x0 - VX)
            if not FAR <= f <= 1.0001:
                continue
            yt, yb = VY + (OPEN_TOP - VY) * f, VY + (WALL_B - VY) * f
            z = 1 / f
            for y in range(math.ceil(yt), math.floor(yb) + 1):
                Y = VY + (y - VY) / f                                  # al pla davanter
                lvl = 2.0 - (z - 1) * 0.5 + (0.3 if sgn < 0 else -0.2)
                pz = (z * 4.0) % 1
                if pz < 0.06 * z:
                    lvl = 0.7                                             # costures
                elif pz < 0.12 * z:
                    lvl += 0.8
                if 144 <= Y <= 151:
                    lvl += 0.9 if Y < 148 else -0.8                       # passamà
                if Y > 151:
                    lvl -= 0.4
                    if int(Y) % 8 < 2 and f > 0.6:
                        lvl -= 0.3                                        # costelles del sòcol
                if Y > 197:
                    lvl -= 0.8
                if Y < OPEN_TOP + 13:
                    lvl -= 0.7
                cv.put(x, y, HULL, lvl, 0.5)

    side(OPEN_X0, -1)
    side(OPEN_X1, 1)

    # portes de les cel·les 10 i 11 a la paret esquerra del passadís
    for zc, num in ((1.28, '10'), (1.78, '11')):
        f0, f1 = 1 / zc, 1 / (zc + 0.18)
        xa, xb = VX + (OPEN_X0 - VX) * f0, VX + (OPEN_X0 - VX) * f1
        for x in range(round(xa), round(xb) + 1):
            f = (x - VX) / (OPEN_X0 - VX)
            yt, yb = VY + (75 - VY) * f, VY + (WALL_B - VY) * f
            for y in range(round(yt), round(yb)):
                Y = VY + (y - VY) / f
                lvl = 2.4 - (1 / f - 1) * 0.5
                if x in (round(xa), round(xb)) or abs(y - round(yt)) < 1:
                    lvl = 0.6
                elif x == round(xa) + 1:
                    lvl += 0.7                                            # cantell de la porta
                elif 85 <= Y <= 104 and 0.25 < (x - xa) / (xb - xa + 0.01) < 0.75:
                    lvl = 0.4 if (x % 2) else 1.6                       # finestreta amb barrots
                elif 165 <= Y <= 171 and 0.2 < (x - xa) / (xb - xa + 0.01) < 0.8:
                    lvl -= 0.6                                            # la trapa del menjar
                cv.put(x, y, HULL, lvl, 0.5)
        lx = round(xa + (xb - xa) * 0.8)
        ly = round(VY + (133 - VY) * (2 / (1 / f0 + 1 / f1)))
        cv.put(lx, ly, CYAN, 3.6, 0)
        cv.put(lx, ly + 1, CYAN, 2.6, 0)
        cv.glow(lx, ly, 5, (90, 200, 255), 0.5)
        # número
        yy = round(VY + (64 - VY) * f0)
        small = num == '11'                                          # la més llunyana, amb la lletra petita
        tw = text_w(num, 1, small)
        th = 5 if small else 7
        cv.rect(round(xa) + 1, yy - 2, round(xa) + tw + 4, yy + th + 1, SIGN, 2.0, 0.5)
        cv.hline(round(xa) + 1, round(xa) + tw + 4, yy + th + 1, SIGN, 1.2, 0.5)
        text(cv, round(xa) + 3, yy, num, HULL, 1.0, 0.2, gap=1, small=small)

    # canonada al llarg de la paret dreta del passadís, amb les abraçadores
    for x in range(round(FAR_R), OPEN_X1 + 1):
        f = (x - VX) / (OPEN_X1 - VX)
        y = round(VY + (53 - VY) * f)
        th = max(1, round(7 * f))
        clamp = ((1 / f) * 5) % 1 < 0.07 and f > 0.45
        for k in range(th):
            cv.put(x, y + k, IRON, [3.6, 3.0, 2.4, 1.8, 1.2, 0.8][min(5, k * 6 // th)] + (0.8 if clamp else 0), 0.5)
        if clamp:
            cv.vline(x, y + th, y + th + max(1, round(4 * f)), IRON, 1.4, 0.5)

    # paret del fons amb la porta de l'hangar
    fl, ft, fr, fb = round(FAR_L), round(FAR_T), round(FAR_R), round(FAR_B)
    cv.rect(fl, ft, fr, fb, HULL, lambda x, y: 1.6 + (0.4 if (x - fl) % 19 == 0 else 0) - (0.3 if y > fb - 4 else 0), 0.4)
    DX0, DX1, DT = 344, 383, 105
    cv.rect(DX0 - 3, DT - 3, DX1 + 3, fb, HULL, lambda x, y: 0.4 if x < DX0 - 1 or x > DX1 + 1 or y < DT - 1 else 1.2, 0)
    mid = (DX0 + DX1) / 2
    for y in range(DT, fb + 1):
        for x in range(DX0, DX1 + 1):
            lvl = 2.2 - abs(x - mid) / 21 + (0.8 if x in (DX0, round(mid) + 1) else 0) - (0.9 if x == round(mid) else 0)
            if (y - DT) % 9 == 0:
                lvl -= 0.3                                               # costelles de la porta
            cv.put(x, y, HULL, lvl, 0.3)
    hazard(cv, DX0, 117, DX1, 121, lit=0.2, lvl=3.0, w=3)               # franja de perill de la porta
    cv.rect(DX0 + 4, 131, DX0 + 9, 135, ORANGE, lambda x, y: 3.2 - (y - 131) * 0.15, 0)   # rètol de l'hangar
    cv.hline(DX0 + 5, DX0 + 8, 133, ORANGE, 1.4, 0)
    cv.rect(round(mid) - 3, 140, round(mid) - 2, 147, HULL, 3.0, 0.3)   # les nanses
    cv.rect(round(mid) + 3, 140, round(mid) + 4, 147, HULL, 2.6, 0.3)
    # pilot vermell sobre la porta
    cv.rect(357, DT - 11, 369, DT - 4, HULL, 1.2, 0)
    cv.rect(358, DT - 10, 368, DT - 5, ALARM, 4.2 + 0.9 * al, 0)
    cv.hline(360, 366, DT - 9, ALARM, 5.0 + 0.6 * al, 0)
    for x in range(359, 368, 3):
        cv.vline(x, DT - 10, DT - 5, ALARM, 2.6 + 0.6 * al, 0)            # la gàbia
    cv.tint(fl, ft, fr, fb + 40, (255, 60, 50), lambda x, y: 0.42 * (1 + 0.3 * al) * red_alarm(x, y))
    cv.glow(DOOR_CX, DT - 8, 29, (255, 70, 60), 0.6)
    if al > 0:                                                         # el halo creix (barreja suau)
        cv.tint(333, DT - 37, 392, DT + 21, (255, 80, 64),
                lambda x, y: 0.22 * al * max(0.0, 1 - math.hypot(x - DOOR_CX, y - DT + 8) / 29))

    # terra (vestíbul + passadís)
    def floor_extra(x, y):
        v = 0.0
        if y < FLOOR_Y:
            v -= (FLOOR_Y - y) / (FLOOR_Y - FAR_B) * 0.7
        return v

    deck(cv, VX, VY, FS, FK, FOU, FOV, y0=fb + 1, inside=floor_inside, extra=floor_extra, wall_y=FAR_B)
    cv.tint(OPEN_X0, fb, OPEN_X1, 213, (255, 60, 50), lambda x, y: 0.3 * (1 + 0.3 * al) * red_alarm(x, y * 0.7 + 40))
    # línia groga de guia, cap a la porta del fons (gastada on trepitja tothom)
    for y in range(fb + 1, H):
        d = y - VY
        for x in range(W):
            u = (x - DOOR_CX) / d
            if -0.075 <= u <= 0.075 and floor_inside(x, y):
                lv = 2.4 + 0.6 * LIGHT(x, y) - (0.6 if y < FLOOR_Y else 0) - (0.5 if abs(u) > 0.06 else 0)
                if y > FLOOR_Y + 20 and hr(x // 2, y // 2, 33) > 0.86:
                    lv -= 0.8
                cv.put(x, y, WARN, max(1.6, lv), 0)
    # ombra de contacte a l'entrada del passadís
    cv.darken(OPEN_X0 - 3, 200, OPEN_X0 + 8, 213, lambda x, y: 0.6 * (1 - (x - OPEN_X0 + 3) / 11))

    # ─── Parets davanteres ────────────────────────────────────────────────
    wall(cv, 0, OPEN_X0 - 1, seed=1)
    wall(cv, OPEN_X1 + 1, W - 1, seed=3)
    # cantonades de l'obertura (perfil gruixut)
    for x0, sgn in ((OPEN_X0 - 5, 1), (OPEN_X1 + 1, -1)):
        for i in range(5):
            cv.vline(x0 + i, OPEN_TOP, WALL_B, HULL, [3.8, 3.2, 2.6, 1.8, 1.0][i if sgn > 0 else 4 - i] + 0.3)
        for y in range(OPEN_TOP + 10, WALL_B - 6, 26):
            cv.put(x0 + 2, y, HULL, 5.2 if sgn > 0 else 3.6)              # cargols del perfil
    # llinda i biga del sostre, amb franges de perill sobre l'obertura
    cv.rect(0, 0, W - 1, 12, HULL, lambda x, y: 0.8 + (0.6 if y in (9, 10) else 0) + (hr(x // 32, 3) - 0.5) * 0.2)
    cv.hline(0, W - 1, 13, HULL, 3.4)
    cv.hline(0, W - 1, 14, HULL, 1.8)
    cv.hline(0, W - 1, 15, HULL, 1.0)
    cv.rect(OPEN_X0 - 5, OPEN_TOP - 16, OPEN_X1 + 5, OPEN_TOP - 1, HULL, lambda x, y: 2.8 - (y - OPEN_TOP + 16) * 0.09)
    cv.hline(OPEN_X0 - 5, OPEN_X1 + 5, OPEN_TOP - 16, HULL, 3.8)
    hazard(cv, OPEN_X0 - 3, OPEN_TOP - 12, OPEN_X1 + 3, OPEN_TOP - 5, lvl=3.0, w=5)
    cv.hline(OPEN_X0 - 5, OPEN_X1 + 5, OPEN_TOP - 1, HULL, 0.4)
    for x in range(OPEN_X0 + 6, OPEN_X1 - 4, 37):
        rivet(cv, x, OPEN_TOP - 4, HULL, 2.8)
    # rètol del mòdul sobre l'obertura
    s = 'MÒDUL C'
    tw = text_w(s)
    cv.rect(312 - tw // 2 - 5, 1, 312 + tw - tw // 2 + 4, 13, SIGN, lambda x, y: 3.0 - (y - 1) * 0.04, 0.3)
    cv.hline(312 - tw // 2 - 5, 312 + tw - tw // 2 + 4, 13, SIGN, 1.6, 0.3)
    for sx in (312 - tw // 2 - 3, 312 + tw - tw // 2 + 2):
        cv.put(sx, 3, SIGN, 1.4, 0.3)                                    # cargols del rètol
    text(cv, 312 - tw // 2, 5, s, HULL, 1.0, 0.1)
    # safata de cables al llarg del sostre
    for x in range(0, W):
        if OPEN_X0 - 5 <= x <= OPEN_X1 + 5:
            continue
        cv.put(x, 18, IRON, 3.2)
        cv.put(x, 19, IRON, 2.6)
        cv.put(x, 20, IRON, 1.6)
        if x % 12 == 0:
            cv.vline(x, 16, 20, IRON, 3.0)
            cv.vline(x + 1, 16, 20, IRON, 1.4)
    for x in range(0, OPEN_X0 - 5):
        for k, (yy, rr) in enumerate(((22, ORANGE), (23, HULL), (24, TEAL))):
            if hr(x // 16, k) > 0.15:
                sag = (1 if (x // 40) % 2 and k == 1 else 0) + (1 if k == 2 and (x % 40) in range(14, 26) else 0)
                cv.put(x, yy + sag, rr, 1.6 if rr is not HULL else 1.2)
                if k == 0:
                    cv.put(x, yy - 1, rr, 2.6)                           # el lluu del cable taronja
        if x % 40 == 20:
            cv.vline(x, 21, 25, IRON, 0.8)                              # brides

    # ─── Porta de la cel·la 9 (11..87 × 61..206) ──────────────────────────
    CX0, CX1, CT = 16, 81, 77
    cv.rect(CX0 - 5, CT - 8, CX1 + 5, WALL_B, HULL, lambda x, y: 1.0 if x in (CX0 - 5, CX1 + 5) else 3.0 - (0.8 if x > CX1 else 0))
    cv.rect(CX0 - 3, CT - 6, CX1 + 3, CT - 1, HULL, lambda x, y: 3.8 if y > CT - 6 else 4.6)
    for y in range(CT, FLOOR_Y):
        for x in range(CX0, CX1 + 1):
            u = (x - CX0) / (CX1 - CX0)
            lvl = 2.4 + math.sin(u * math.pi) * 0.6 - u * 0.4 + (hr(x // 3, y // 4, 12) - 0.5) * 0.12
            if (y - CT) in (45, 46) or (y - CT) in (93, 94):
                lvl += 1.0 if (y - CT) % 2 == 1 else -1.2               # costures horitzontals
            if x in (CX0, CX0 + 1, CX0 + 2):
                lvl += [1.2, 0.8, 0.3][x - CX0]
            if x in (CX1, CX1 - 1, CX1 - 2):
                lvl -= [1.4, 1.0, 0.4][CX1 - x]
            if y > 176:
                lvl -= (y - 176) / 28 * 0.9                                 # brutícia de baix
            if y > 171 and hr(x, 11) > 0.84 and y - 171 < hr(x, 4) * 32:
                cv.put(x, y, RUSTG, 2.6 - (y - 171) / 26 + (0.5 if hr(x, 13) > 0.5 else 0))   # regalims de rovell
                continue
            cv.put(x, y, HULL, lvl)
    for y in (CT + 45, CT + 93):                                          # reblons de les costures
        for x in range(CX0 + 6, CX1 - 4, 12):
            rivet(cv, x, y - 3, HULL, 3.0)
    # finestreta amb barrots
    WX0, WX1, WY0, WY1 = 32, 65, 91, 115
    cv.rect(WX0 - 3, WY0 - 3, WX1 + 3, WY1 + 3, HULL, lambda x, y: 4.2 if y < WY0 or x < WX0 else 1.0)
    cv.rect(WX0 - 2, WY0 - 2, WX1 + 2, WY1 + 2, HULL, lambda x, y: 3.4 if y < WY0 or x < WX0 else 1.6)
    cv.rect(WX0, WY0, WX1, WY1, SPACE, lambda x, y: 1.4 + (y - WY0) / 26, 0)
    cv.tint(WX0, WY0, WX1, WY1, (40, 60, 90), lambda x, y: 0.25 if x - WX0 + (y - WY0) * 0.5 < 10 else 0)   # reflex
    for x in range(WX0 + 3, WX1, 5):
        cv.vline(x, WY0, WY1, HULL, 4.0)
        cv.vline(x + 1, WY0, WY1, HULL, 2.8)
        cv.vline(x + 2, WY0, WY1, HULL, 1.4)
    # cartellet amb el 9
    cv.rect(36, 61, 61, 77, SIGN, lambda x, y: 4.2 - (y - 61) * 0.09, 0.4)
    cv.hline(36, 61, 77, HULL, 0.8)
    cv.vline(61, 61, 77, SIGN, 2.6, 0.4)
    for sx, sy in ((38, 63), (59, 63), (38, 75), (59, 75)):
        cv.put(sx, sy, SIGN, 1.4, 0.3)                                    # cargolets
    for j, row in enumerate(FONT7['9']):
        for i, c in enumerate(row):
            if c == '#':
                cv.rect(45 + i * 2, 63 + j * 2, 46 + i * 2, 64 + j * 2, HULL, 0.6, 0)
    # pany magnètic M-3 (per fora, a l'esquerra)
    cv.rect(21, 133, 31, 152, HULL, lambda x, y: 1.4 if x == 31 or y == 152 else (4.2 if x == 21 or y == 133 else 3.2))
    cv.rect(23, 137, 29, 141, CYAN, lambda x, y: 3.6 - (y - 137) * 0.3, 0)
    cv.hline(24, 28, 137, CYAN, 4.6, 0)
    cv.glow(26, 139, 13, (90, 200, 255), 0.6)
    cv.rect(24, 145, 28, 149, HULL, 0.6)
    cv.hline(24, 28, 147, HULL, 1.6)                                      # la ranura de la targeta
    text(cv, 22, 155, 'M-3', HULL, 3.6, 0.3, gap=1, small=True)
    # frontisses
    for y in (CT + 11, 187):
        cv.rect(CX1 - 1, y, CX1 + 3, y + 8, HULL, lambda x, y_: 4.0 - (x - CX1) * 0.7)
        cv.hline(CX1 - 1, CX1 + 3, y + 8, HULL, 0.8)
    # trapa del menjar
    cv.rect(35, 168, 63, 177, HULL, lambda x, y: 1.0 if y == 177 or x == 63 else (4.0 if y == 168 else 2.8))
    cv.hline(37, 61, 172, HULL, 0.8)
    cv.rect(47, 173, 51, 175, HULL, lambda x, y: 4.2 if y == 173 else 3.0)
    # reblons del marc
    for y in range(CT + 3, WALL_B - 2, 16):
        cv.put(CX0 - 4, y, HULL, 4.6)
        cv.put(CX0 - 4, y + 1, HULL, 2.6)
        cv.put(CX1 + 4, y, HULL, 2.6)
    # ratllades a la porta (palitos de comptar dies)
    for i in range(6):
        cv.vline(21 + i * 3, 157 + (i % 2), 166, HULL, 4.4)
    cv.line(19, 165, 38, 158, HULL, 4.4)
    cv.line(19, 166, 38, 159, HULL, 1.2)

    # ─── Aplic sobre la cel·la i quadre d'intèrfon ────────────────────────
    wall_lamp(cv, 139, 35, w=21)
    cv.rect(123, 99, 147, 131, HULL, lambda x, y: 1.0 if x == 147 or y == 131 else (4.2 if x == 123 or y == 99 else 3.4))
    cv.rect(125, 103, 144, 115, SPACE, 2.6, 0)
    cv.rect(125, 103, 144, 103, HULL, 1.0, 0)
    for y in range(105, 114, 3):
        cv.hline(127, 127 + int(hr(y, 3) * 14), y, TEAL, 3.6, 0)
    if (tt * 4) % 1 >= 0.5:                                            # el cursor de l'intèrfon
        cx_ = 130 + int(hr(112, 3) * 13)
        cv.rect(cx_, 111, cx_ + 1, 112, TEAL, 5.0, 0)
    cv.glow(135, 108, 16, (90, 220, 200), 0.35)
    for i in range(3):
        cv.rect(127 + i * 7, 120, 130 + i * 7, 124, HULL, lambda x, y: 3.0 if y == 120 else 2.2)
        cv.hline(127 + i * 7, 130 + i * 7, 125, HULL, 0.8)
    cv.put(141, 121, PILOT, 3.0, 0)
    cv.put(142, 121, PILOT, 2.4, 0)
    for y in range(127, 130):                                            # reixeta de l'altaveu
        for x in range(126, 140, 2):
            cv.put(x, y, HULL, 1.2)
    # caixa de mànega d'emergència vermella, tancada
    cv.rect(157, 131, 184, 176, RED, lambda x, y: 3.0 - (x - 157) * 0.03 - (0.9 if x == 184 or y == 176 else 0) + (0.8 if x == 157 or y == 131 else 0))
    cv.rect(161, 136, 180, 157, RED, lambda x, y: 2.0 + (0.6 if x == 161 or y == 136 else 0))
    cv.rect(163, 139, 179, 155, SPACE, 3.6, 0.3)
    cv.ring(171, 147, 5, RED, 3.4, 0.3, step=12)
    cv.ring(171, 147, 3, RED, 2.6, 0.3, step=20)
    for i in range(6):
        cv.put(165 + i, 141 + i // 2, SPACE, 5.4, 0.3)                     # reflex al vidre
    cv.rect(179, 161, 181, 168, IRON, lambda x, y: 3.6 - (x - 179) * 0.5)
    cv.rect(163, 161, 175, 165, PAPER, 3.6, 0.3)                           # etiqueta
    cv.hline(165, 173, 163, RED, 2.4, 0.3)
    cv.darken(159, 177, 185, 181, 0.5)

    # ─── Paret dreta: cartell, càmera, porta de la Sala de la Memòria ─────
    # tira de llum sobre el cartell
    cv.rect(461, 27, 536, 32, HULL, lambda x, y: 2.4 if y == 27 else 1.6)
    cv.hline(464, 533, 31, LAMPW, 1.4 if strip_off else 3.8, 0)
    cv.hline(464, 533, 32, LAMPW, 1.0 if strip_off else 2.6, 0)
    if not strip_off:
        cv.glow(499, 34, 53, (200, 235, 255), 0.35)

    # Cartell del reciclatge (432..547 × 36..88): somriure, fletxa cap al fons. Més amunt i més estret que abans, perquè
    # el rètol de la Sala de la Memòria hi càpiga a sota amb marc propi i no toqui la càmera.
    PX0, PY0, PX1, PY1 = 436, 38, 543, 85
    # Amb `arrencat` (decorat), la Vet n'ha arrencat un tros del marge: el cantó de baix a l'esquerra, amb l'esquinç
    # en ziga-zaga, i la cinta d'aquell cantó se n'ha anat amb el paper.
    def tros(x, y):
        return arrencat and (x - PX0) + (PY1 - y) * 1.5 + (hr(y, 41) - 0.5) * 3 + (2 if (x + y) % 5 == 0 else 0) < 21
    for y in range(PY0 + 3, PY1 + 4):                                         # ombra
        for x in range(PX0 + 3, PX1 + 4):
            if not tros(x - 3, y - 3):
                cv.put(x, y, HULL, 0.6)
    for y in range(PY0, PY1 + 1):
        for x in range(PX0, PX1 + 1):
            if tros(x, y):
                continue
            if tros(x - 1, y) or tros(x, y + 1):
                cv.put(x, y, SIGN, 4.4, 0.4)                                   # la vora esquinçada, més blanca
                continue
            lvl = 3.4 + (hr(x // 2, y // 3, 5) - 0.5) * 0.2 + (hr(x // 9, y // 7, 15) - 0.5) * 0.12
            if y >= PY1 - 1 or x >= PX1 - 1:
                lvl -= 0.6
            cv.put(x, y, SIGN, lvl, 0.4)
    cv.rect(PX0, PY0, PX1, PY0 + 10, CORPG, lambda x, y: 2.5 + (0.6 if y == PY0 else 0) - (0.5 if y == PY0 + 10 else 0), 0)
    text(cv, PX0 + 8, PY0 + 2, 'RECICLATGE', SIGN, 4.5, 0.0)
    smile(cv, 470, 65, 13)
    # fletxa gran cap a l'esquerra (cap al passadís)
    for y in range(59, 72):
        k = abs(y - 65)
        for x in range(491 + round(k * 1.7), 516):
            cv.put(x, y, CORPG, 2.5 + (1 if y < 63 else 0) - (0.6 if y == 71 else 0), 0)
    for y in range(61, 70):
        for x in range(512, 536):
            cv.put(x, y, CORPG, 2.5 + (1 if y < 64 else 0) - (0.6 if y == 69 else 0), 0)
    text(cv, 496, 75, 'PER AQUÍ', HULL, 1.4, 0.2)
    # les puntes de cinta adhesiva
    for x, y in ((PX0 - 1, PY0 - 1), (PX1 - 3, PY0 - 1), (PX0 - 1, PY1 - 3), (PX1 - 3, PY1 - 3)):
        if tros(x + 2, y + 2):
            continue
        cv.rect(x, y, x + 4, y + 4, SIGN, lambda xx, yy: 3.5 + (0.4 if (xx + yy) % 3 == 0 else 0), 0.3)
    # canto superior dret una mica despenjat
    cv.put(PX1, PY0, HULL, 2.0)
    cv.put(PX1 - 1, PY0, HULL, 2.0)
    cv.put(PX1, PY0 + 1, HULL, 2.0)
    if strip_off:                                                      # la tira parpelleja: el cartell s'enfosqueix
        cv.tint(PX0 - 1, PY0 - 1, PX1 + 3, PY1 + 3, (8, 10, 16), 0.3)

    # Càmera de vigilància (545..597 × 14..48)
    cv.rect(581, 16, 588, 27, HULL, lambda x, y: 3.0 - (x - 581) * 0.25)        # suport
    cv.rect(576, 13, 593, 17, HULL, lambda x, y: 2.6 if y == 13 else 2.0)
    for sx in (578, 591):
        cv.put(sx, 15, HULL, 4.4)
    for y in range(24, 41):
        t = (y - 24) / 16                                                   # (tapa el `t` del cicle: fem servir `tt`)
        x0 = round(552 + t * 3)
        for x in range(x0, 592):
            lvl = 4.0 - t * 1.6 - (x - x0) / 80
            if y == 24:
                lvl += 0.8
            if y == 40:
                lvl = 1.0
            if (x - x0) % 6 == 0 and 27 <= y <= 30 and x > 566:
                lvl -= 0.8                                                  # reixeta de ventilació
            cv.put(x, y, PANEL, lvl)
    cv.rect(552, 22, 588, 23, PANEL, lambda x, y: 4.4 if y == 22 else 3.4)      # visera
    cv.rect(547, 27, 553, 37, HULL, lambda x, y: 1.0 + (y - 27) * 0.08)     # objectiu
    cv.disc(549.5, 32, 2.6, 3.8, SPACE, lambda nx, ny: 2.0 - nx - ny, 0)
    cv.put(548, 30, CYAN, 4.0, 0)
    cv.put(549, 31, CYAN, 2.6, 0)
    if (tt * 3 + 0.2) % 1 < 0.75:                                      # el LED de la càmera fa pampallugues
        cv.put(584, 31, PILOT, 3.6, 0)
        cv.put(585, 31, PILOT, 3.0, 0)
        cv.put(584, 30, PILOT, 2.6, 0)
        cv.glow(584, 31, 8, (90, 255, 120), 0.6)
    else:
        cv.put(584, 31, PILOT, 1.0, 0)
        cv.put(585, 31, PILOT, 0.8, 0)
        cv.put(584, 30, PILOT, 0.6, 0)
    cv.line(588, 17, 627, 17, HULL, 0.6)                                    # cable
    cv.line(588, 18, 627, 18, HULL, 1.4)
    cv.darken(552, 41, 592, 45, 0.35)

    # Porta de la Sala de la Memòria (472..539 × 101..205): porta enretirada amb rètol
    MX0, MX1, MT = 480, 529, 127
    cv.rect(472, 117, 537, WALL_B, HULL, lambda x, y: 3.6 if x <= 475 else (1.2 if x >= 534 else 2.8))
    cv.rect(476, 124, 533, WALL_B, HULL, 0.5, 0.4)                              # bruna de l'obertura
    for x in range(476, 480):                                                  # brancal il·luminat (perspectiva)
        cv.vline(x, 124, WALL_B, HULL, 2.6 - (x - 476) * 0.35)
    for y in range(MT, FLOOR_Y):
        for x in range(MX0, MX1 + 1):
            u = (x - MX0) / (MX1 - MX0)
            lvl = 3.0 + (0.4 if u < 0.5 else 0.1) - abs(u - 0.5) * 0.6
            if abs(x - (MX0 + MX1) / 2) < 0.6:
                lvl = 0.8                                                     # porta corredissa de dues fulles
            elif abs(x - (MX0 + MX1) / 2 - 1) < 0.6:
                lvl += 0.6
            if 160 <= y <= 161:
                lvl += 0.8 if y == 160 else -0.6
            if y < MT + 2:
                lvl -= 0.8                                                    # ombra de la llinda
            cv.put(x, y, PANEL, lvl, 0.6)
    for hx in (501, 510):                                                     # nanses empotrades
        cv.rect(hx, 170, hx + 1, 182, PANEL, 1.2, 0.6)
    # rètol lluminós «SALA DE LA MEMÒRIA» amb el somriure
    # (caixa de llum pròpia, penjada a la paret per sobre del marc de la porta, amb dos suports)
    for sx in (482, 527):
        cv.rect(sx, 115, sx + 1, 117, HULL, 1.2)
    cv.rect(473, 88, 537, 115, HULL, lambda x, y: 1.0 if y == 115 or x == 537 else 2.0)
    cv.rect(475, 90, 535, 113, SIGN, 4.2, 0.2)
    cv.hline(475, 535, 90, SIGN, 5.0, 0)
    cv.hline(475, 535, 113, SIGN, 2.6, 0)
    text(cv, 479, 92, 'SALA DE LA', CORPG, 1.6, 0.0)
    text(cv, 479, 103, 'MEMÒRIA', CORPG, 1.6, 0.0)
    smile(cv, 526, 107, 4, lit=0, lvl=3.8)
    cv.glow(504, 102, 27, (220, 250, 240), 0.3)
    # control d'accés (tancat: vermell)
    cv.rect(541, 149, 549, 165, HULL, lambda x, y: 1.0 if x == 549 else (4.2 if x == 541 else 3.2))
    cv.rect(543, 153, 547, 157, ALARM, lambda x, y: 3.8 if y < 155 else 3.2, 0)
    for y in range(160, 164, 2):
        cv.hline(543, 547, y, HULL, 1.4)
    cv.glow(545, 155, 8, (255, 80, 60), 0.4)
    # horari («visites de reeducació, els dimarts»)
    cv.rect(541, 128, 557, 144, SIGN, lambda x, y: 3.0 - (0.5 if x == 557 or y == 144 else 0), 0.4)
    cv.hline(541, 557, 128, CORPG, 2.5, 0.3)
    cv.hline(541, 557, 129, CORPG, 2.0, 0.3)
    for y in range(132, 143, 2):
        cv.hline(543, 543 + int(hr(y, 7) * 11), y, HULL, 1.4, 0.2)

    # cartell vell, mig arrencat, a la paret (detall)
    cv.rect(587, 93, 621, 123, SIGN, lambda x, y: 2.4 + (hr(x // 2, y // 2, 8) - 0.5) * 0.3 - (0.8 if x > 613 and y > 112 else 0), 0.5)
    smile(cv, 600, 105, 5, lit=0.4, lvl=2.4)
    for x in range(588, 621):
        if hr(x, 3) > 0.5:
            cv.put(x, 123 - int(hr(x, 4) * 4), HULL, 2.0)
            cv.put(x, 124 - int(hr(x, 4) * 4), HULL, 1.0)
    for y in range(99, 120, 4):
        cv.hline(608, 617, y, HULL, 1.4, 0.4)
    cv.rect(588, 112, 597, 116, CORPG, 2.0, 0.4)                               # la franja verda, esvaïda

    # Ombres de contacte a la línia paret-terra, a tot arreu
    cv.darken(0, FLOOR_Y, W - 1, FLOOR_Y + 6,
              lambda x, y: 0.6 - (y - FLOOR_Y) * 0.1 if not (OPEN_X0 <= x <= OPEN_X1) else 0)


# ─── Rajola solta (prop): la planxa del terra mig aixecada, amb el paper a sota ──

def _tile_quad():
    """Cantonades de la planxa u −4..−3, v 4..5."""
    def pt(u, v):
        d = FK / (v - FOV)
        return VX + (u - FOU) * d / FS, VY + d
    return [pt(-4, 5), pt(-3, 5), pt(-3, 4), pt(-4, 4)]


def rajola(cv):
    (ax, ay), (bx, by), (cx_, cy_), (dx, dy) = _tile_quad()      # fons-esq, fons-dre, davant-dre, davant-esq
    # forat fosc on seu la planxa
    cv.poly([(ax, ay), (bx, by), (cx_, cy_), (dx, dy)], DECK, lambda x, y: 0.1 + (0.4 if y > cy_ - 3 else 0), 0)
    # la planxa, aixecada pel cantó de davant a la dreta
    lift = [(ax, ay - 1), (bx + 1, by - 4), (cx_ + 3, cy_ - 11), (dx + 1, dy - 3)]
    cv.poly(lift, DECK, lambda x, y: 3.4 + (x - dx) / 35 - (y - ay) / 40 + (hr(x // 3, y // 3, 4) - 0.5) * 0.3 +
            (0.4 if (x + 2 * y) % 6 == 0 and (x - 2 * y) % 9 < 3 else 0))
    # costures i cargols de la planxa
    cv.line(lift[0][0], lift[0][1], lift[1][0], lift[1][1], DECK, 4.6)
    cv.line(lift[0][0], lift[0][1], lift[3][0], lift[3][1], DECK, 4.0)
    # cantell gruixut de davant (es veu perquè està aixecada)
    for k in range(4):
        cv.line(lift[3][0], lift[3][1] + k, lift[2][0], lift[2][1] + k, DECK, [5.0, 3.4, 2.2, 1.2][k])
    for k in range(2):
        cv.line(lift[2][0] - k, lift[2][1] + k, lift[1][0] - k, lift[1][1] + k, DECK, [3.0, 1.8][k])
    for (u, v) in ((0.12, 0.18), (0.88, 0.18), (0.12, 0.82), (0.88, 0.82)):
        x = lift[0][0] + (lift[1][0] - lift[0][0]) * u + (lift[3][0] - lift[0][0]) * v
        y = lift[0][1] + (lift[1][1] - lift[0][1]) * u + (lift[3][1] - lift[0][1]) * v
        if (u, v) == (0.88, 0.82):
            cv.put(x, y, DECK, 0.4)                                        # aquest forat, sense cargol
            cv.put(x + 1, y, DECK, 0.4)
            continue
        cv.put(x, y, DECK, 5.4)
        cv.put(x + 1, y, DECK, 3.0)
        cv.put(x, y + 1, DECK, 2.4)
        cv.put(x + 1, y + 1, DECK, 1.0)
    # el paper doblegat que treu el cap per l'escletxa
    px, py = round(cx_ - 12), round(cy_ - 4)
    cv.poly([(px - 7, py - 1), (px + 4, py - 4), (px + 8, py + 1), (px - 4, py + 3)], PAPER, lambda x, y: 4.4 - (y - py) * 0.12, 0.5)
    cv.line(px - 5, py, px + 5, py - 3, PAPER, 2.8, 0.5)
    cv.line(px - 3, py + 2, px + 2, py + 1, PAPER, 3.0, 0.5)                # una ratlla escrita, que es veu
    cv.put(px + 7, py + 1, PAPER, 2.4, 0.5)
    cv.put(px + 6, py + 2, PAPER, 2.0, 0.5)
    # cargols fora de lloc, al terra
    for sx, sy, lv in ((cx_ + 7, cy_ - 3, 5.4), (cx_ + 4, cy_ + 3, 5.0)):
        cv.put(round(sx), round(sy), DECK, lv)
        cv.put(round(sx) + 1, round(sy), DECK, lv - 2.0)
        cv.put(round(sx) + 2, round(sy), DECK, 1.6)
    # ombra de la planxa
    cv.line(dx + 3, dy + 1, cx_ + 1, cy_ + 1, DECK, 0.0, 0)
    cv.line(dx + 4, dy + 2, cx_ + 1, cy_ + 2, DECK, 0.6, 0)


def _ambient_frames(n=24):
    return ambient_frames(bg, LIGHT, n)


ANIMS = {'ambient': {'frames': _ambient_frames, 'frameDuration': 125}}

PROPS = {'rajola': rajola}
