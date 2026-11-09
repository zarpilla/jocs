"""
Passadís del mòdul C (La Gavina, Vet): el vestíbul de les cel·les i el passadís que s'enfonsa cap a l'hangar.
Llums: aplic de reixa sobre la cel·la 9, tira de llum sobre el cartell del somriure, fluorescents del passadís,
i el pilot vermell de la porta del fons.

Aquest mòdul també té els materials comuns de La Gavina (paret d'acer, terra de planxes, rètols, el somriure
de la corporació), que fan servir l'arxiu i la Sala de la Memòria.
"""
import math

from hd.pix import (Light, B4, W, H, hr, ramp, mix, STEEL, PANEL, CYAN, TEAL, WARN, ORANGE, RED, PAPER, IRON,
                    SPACE, GRAY, PINK)

# ─── Materials comuns de La Gavina ─────────────────────────────────────────

FLOOR_Y = 154            # primera fila de terra (la paret acaba a 153)
# Acer de les parets: ombres cap al blau-violeta, llums cap al blanc fred
HULL = ramp((7, 8, 16), (16, 20, 32), (30, 38, 54), (48, 60, 78), (72, 88, 106), (104, 122, 138), (146, 164, 176),
            (196, 210, 218), (236, 244, 248), n=11)
# Planxes del terra: més fosques i verdoses
DECK = ramp((6, 8, 12), (14, 18, 24), (26, 32, 40), (40, 48, 56), (58, 68, 76), (84, 96, 102), (120, 132, 136),
            (164, 176, 178), n=10)
# Llum blanca freda (tubs, aplics)
LAMPW = [(70, 100, 130), (120, 170, 210), (180, 225, 250), (230, 248, 255), (255, 255, 255)]
# Vermell d'alarma
ALARM = [(40, 6, 10), (90, 14, 16), (150, 24, 22), (210, 46, 36), (250, 100, 80), (255, 180, 160)]
# Verd de pilot
RUSTG = [(30, 16, 16), (60, 30, 24), (98, 50, 32), (136, 74, 42), (170, 104, 60)]   # rovell sobre acer
PILOT = [(10, 40, 20), (20, 90, 40), (60, 180, 90), (150, 250, 170)]
SIGN = [(70, 72, 70), (130, 134, 128), (186, 190, 182), (222, 224, 214), (244, 244, 236), (255, 255, 250)]
CORPG = [(10, 40, 30), (16, 70, 50), (30, 110, 74), (50, 150, 96), (90, 196, 130), (160, 236, 180)]   # verd corporatiu

# Lletres de 3×5 (files separades per «/»)
FONT = {k: v.replace('/', '') for k, v in {
    'A': '.#./#.#/###/#.#/#.#', 'B': '##./#.#/##./#.#/##.', 'C': '.##/#../#../#../.##', 'D': '##./#.#/#.#/#.#/##.',
    'E': '###/#../##./#../###', 'F': '###/#../##./#../#..', 'G': '.##/#../#.#/#.#/.##', 'H': '#.#/#.#/###/#.#/#.#',
    'I': '###/.#./.#./.#./###', 'J': '..#/..#/..#/#.#/.#.', 'K': '#.#/#.#/##./#.#/#.#', 'L': '#../#../#../#../###',
    'M': '#.#/###/###/#.#/#.#', 'N': '##./#.#/#.#/#.#/#.#', 'O': '.#./#.#/#.#/#.#/.#.', 'P': '##./#.#/##./#../#..',
    'Q': '.#./#.#/#.#/##./.##', 'R': '##./#.#/##./#.#/#.#', 'S': '.##/#../.#./..#/##.', 'T': '###/.#./.#./.#./.#.',
    'U': '#.#/#.#/#.#/#.#/###', 'V': '#.#/#.#/#.#/#.#/.#.', 'X': '#.#/#.#/.#./#.#/#.#', 'Y': '#.#/#.#/.#./.#./.#.',
    'Z': '###/..#/.#./#../###', '0': '###/#.#/#.#/#.#/###', '1': '.#./##./.#./.#./###', '2': '##./..#/.#./#../###',
    '3': '##./..#/.#./..#/##.', '4': '#.#/#.#/###/..#/..#', '5': '###/#../##./..#/##.', '6': '.##/#../###/#.#/###',
    '7': '###/..#/.#./.#./.#.', '8': '###/#.#/###/#.#/###', '9': '###/#.#/###/..#/###', '-': '.../.../###/.../...',
    '.': '.../.../.../.../.#.', ':': '.../.#./.../.#./...', '·': '.../.../.#./.../...', ' ': '.../.../.../.../...',
    "'": '.#./.#./.../.../...', '/': '..#/..#/.#./#../#..',
}.items()}


def text(cv, x, y, s, rmp, lvl, lit=0.4, gap=1):
    """Lletres de 3×5 píxels (rètols)."""
    for ch in s.upper().replace('Ò', 'O').replace('À', 'A').replace('È', 'E').replace('É', 'E'):
        g = FONT.get(ch, FONT[' '])
        for j in range(5):
            for i in range(3):
                if g[j * 3 + i] == '#':
                    cv.put(x + i, y + j, rmp, lvl, lit)
        x += 3 + gap
    return x


def text_w(s, gap=1):
    return len(s) * (3 + gap) - gap


def smile(cv, cx, cy, r, lit=0.3, lvl=3.6):
    """El somriure de la corporació: cara groga, ulls i un somriure massa ample."""
    cv.disc(cx, cy, r, r, WARN, lambda nx, ny: lvl + 0.5 - (1.0 if nx * 0.6 + ny * 0.8 > 0.55 else 0) + (1.0 if nx + ny < -0.9 else 0), lit)
    ex = max(1, round(r * 0.36))
    ey = cy - round(r * 0.3)
    for s in (-1, 1):
        cv.put(cx + s * ex, ey, WARN, 0.0, 0)
        if r >= 6:
            cv.put(cx + s * ex, ey + 1, WARN, 0.0, 0)
    for a in range(10, 171, 6 if r >= 6 else 12):
        rr = r * 0.62
        cv.put(round(cx + math.cos(math.radians(a)) * rr), round(cy + math.sin(math.radians(a)) * rr * 0.9), WARN, 0.2, 0)


def rivet(cv, x, y, rmp=HULL, lvl=4.0):
    cv.put(x, y, rmp, lvl + 1.4)
    cv.put(x + 1, y, rmp, lvl)
    cv.put(x, y + 1, rmp, lvl - 0.4)
    cv.put(x + 1, y + 1, rmp, lvl - 2.0)


def hazard(cv, x0, y0, x1, y1, lit=1.0, lvl=3.4, w=4):
    """Franges de perill grogues i negres en diagonal."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if ((x + y) // w) % 2:
                cv.put(x, y, WARN, lvl - (0.6 if y == y1 else 0), lit)
            else:
                cv.put(x, y, HULL, 0.6, lit)


def wall(cv, x0, x1, y0=0, y1=153, rail=112, base=3.0, seed=0, pw=40):
    """Paret d'acer frontal: planxes reblades a dalt, passamà, sòcol de costelles i ombra de terra."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            px = (x + seed * 7) % pw
            row = 0 if y < 50 else 1
            g = (hr((x + seed * 7) // pw, row, seed) - 0.5) * 0.35 + (hr(x // 3, 5) - 0.5) * 0.12
            if y < rail - 3:
                # planxes grans: costura vertical, costura horitzontal a y=50
                if px == 0 or y == 50:
                    lvl = 0.8
                elif px == 1 or y == 51:
                    lvl = base + 1.1
                elif px == pw - 1 or y == 49:
                    lvl = base - 0.7
                else:
                    lvl = base + g - abs(px - pw / 2) / pw * 0.25
            elif y < rail + 3:
                lvl = [base + 1.8, base + 1.2, base + 0.6, base - 0.4, base - 1.0, base - 2.0][y - rail + 3]
            else:
                # sòcol: costelles verticals
                k = (x + seed) % 6
                lvl = base - 0.6 + [0.0, 0.7, 0.4, 0.1, -0.4, -1.0][k]
                if y >= y1 - 4:
                    lvl -= 0.5
            lvl -= max(0.0, 1 - (y - y0) / 14) * 1.0             # ombra del sostre
            cv.put(x, y, HULL, lvl)
        # (els reblons van a part)
    for xp in range(x0 - ((x0 + seed * 7) % pw), x1 + 1, pw):
        for xx in (xp + 4, xp + pw - 5):
            if x0 <= xx <= x1 - 1:
                for yy in (y0 + 18, 46, 56, rail - 8):
                    if y0 <= yy < rail - 4:
                        rivet(cv, xx, yy, HULL, base + 0.6)
    # ombra de contacte paret-terra
    cv.darken(x0, y1 - 2, x1, y1, 0.8)


def deck(cv, vx, vy, S, K, ou=0.0, ov=0.0, y0=FLOOR_Y, y1=H - 1, inside=None, base=2.5, wall_y=153, extra=None):
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
            # trama antilliscant suau
            if (x + 2 * y) % 5 == 0 and hr(x, y, 2) > 0.4:
                lvl += 0.35
            if fu < 1 or fv2 < 1:
                lvl = 0.5                                              # costura fosca
            elif fu < 2 or fv2 < 2:
                lvl += 0.6                                             # cantell il·luminat
            elif fu2 < 1.5 or fv < 1.2:
                lvl -= 0.5
            # cargols a les cantonades
            if 3 <= fu < 4.2 and 2.5 <= fv2 < 3.6 and d > 40:
                lvl += 1.4
            if y < wall_y + 8:
                lvl -= (wall_y + 8 - y) / 8 * 1.2                     # ombra de contacte amb la paret
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


def wall_lamp(cv, cx, cy, w=14):
    """Aplic de reixa: caixa d'acer amb el tub encès i una gàbia."""
    cv.rect(cx - w // 2 - 2, cy - 4, cx + w // 2 + 2, cy + 4, HULL, lambda x, y: 3.0 - (y - cy) * 0.3)
    cv.rect(cx - w // 2, cy - 2, cx + w // 2, cy + 2, LAMPW, lambda x, y: 4.2 - abs(y - cy) * 0.7, 0)
    for x in range(cx - w // 2, cx + w // 2 + 1, 3):
        cv.vline(x, cy - 3, cy + 3, HULL, 2.0, 0.3)
    cv.hline(cx - w // 2 - 2, cx + w // 2 + 2, cy + 5, HULL, 0.6)
    cv.glow(cx, cy, w + 14, (190, 230, 255), 0.55)


# ─── Passadís ──────────────────────────────────────────────────────────────

VX, VY = 292, 95                    # punt de fuga del passadís
OPEN_X0, OPEN_X1, OPEN_TOP = 150, 318, 24
FAR = 0.35                          # fondària de la paret del fons (escala)
FS, FK, FOU, FOV = 2.444, 435.6, -0.445, -0.445   # planxes del terra (la rajola: u −4..−3, v 4..5)


def cp(X, Y, f):
    """Punt del pla davanter (X, Y) portat a la fondària f (1 = davant, FAR = fons)."""
    return VX + (X - VX) * f, VY + (Y - VY) * f


FAR_L, FAR_T = cp(OPEN_X0, OPEN_TOP, FAR)
FAR_R, FAR_B = cp(OPEN_X1, 153, FAR)


def corridor_light(x, y):
    """Llum dels fluorescents del passadís: cau amb la fondària, més forta al terra del mig."""
    if not (OPEN_X0 - 30 <= x <= OPEN_X1 + 30):
        return 0.0
    v = 0.0
    if OPEN_X0 <= x <= OPEN_X1 and y >= 100:
        v += max(0.0, 1 - abs(x - 245) / 90) * 0.7
    return v


LIGHT = Light(vignette=(70, 34), floor_fade=(198, 34))
LIGHT.point(104, 26, r=130, k=2.6, squash=0.9, down=True)            # aplic sobre la cel·la 9
LIGHT.point(374, 30, r=120, k=2.3, squash=1.0, down=True)            # tira sobre el cartell
LIGHT.add(pool(104, 178, 110, 30, 2.4))
LIGHT.add(pool(374, 178, 100, 28, 2.1))
LIGHT.add(pool(250, 156, 64, 26, 1.2))                               # el passadís aboca llum al vestíbul
LIGHT.add(corridor_light)


def floor_inside(x, y):
    """Terra visible: tot per sota de 153, i dins del passadís fins a la paret del fons."""
    if y >= FLOOR_Y:
        return True
    if y <= FAR_B:
        return False
    f = (y - VY) / (153 - VY)
    xl, xr = VX + (OPEN_X0 - VX) * f, VX + (OPEN_X1 - VX) * f
    return xl <= x <= xr


def red_alarm(x, y):
    d = math.hypot(x - 272, (y - 72) * 1.1)
    return max(0.0, 1 - d / 70) ** 2


def bg(cv, t=0.0):
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
            cv.put(x, y, HULL, lvl, 0.3)
    # tubs fluorescents del sostre (barres que s'empetiteixen)
    for f in (0.86, 0.66, 0.5, 0.4):
        (xa, ya), (xb, _) = cp(205, OPEN_TOP, f), cp(275, OPEN_TOP, f)
        ya = round(VY + (OPEN_TOP + 10 - VY) * f)
        th = max(1, round(3 * f))
        off = tube_off and f == 0.66
        cv.rect(round(xa), ya, round(xb), ya + th - 1, LAMPW, 1.6 if off else 3.6, 0)
        cv.hline(round(xa) - 1, round(xb) + 1, ya + th, HULL, 0.6, 0)
        cv.glow((xa + xb) / 2, ya + 1, 26 * f, (180, 225, 255), 0.12 if off else 0.4)

    # parets laterals del passadís
    def side(x0, sgn):
        """Paret lateral: f a partir de x, coordenada vertical al pla davanter."""
        lo, hi = (math.floor(min(x0, FAR_L if sgn < 0 else FAR_R)), math.ceil(max(x0, FAR_L if sgn < 0 else FAR_R)))
        for x in range(lo, hi + 1):
            f = (x - VX) / (x0 - VX)
            if not FAR <= f <= 1.0001:
                continue
            yt, yb = VY + (OPEN_TOP - VY) * f, VY + (153 - VY) * f
            z = 1 / f
            for y in range(math.ceil(yt), math.floor(yb) + 1):
                Y = VY + (y - VY) / f                                  # al pla davanter
                lvl = 2.0 - (z - 1) * 0.5 + (0.3 if sgn < 0 else -0.2)
                pz = (z * 4.0) % 1
                if pz < 0.06 * z:
                    lvl = 0.7                                             # costures
                elif pz < 0.12 * z:
                    lvl += 0.8
                if 108 <= Y <= 113:
                    lvl += 0.9 if Y < 111 else -0.8                       # passamà
                if Y > 113:
                    lvl -= 0.4
                if Y > 148:
                    lvl -= 0.8
                if Y < OPEN_TOP + 10:
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
            yt, yb = VY + (56 - VY) * f, VY + (153 - VY) * f
            for y in range(round(yt), round(yb)):
                Y = VY + (y - VY) / f
                lvl = 2.4 - (1 / f - 1) * 0.5
                if x in (round(xa), round(xb)) or abs(y - round(yt)) < 1:
                    lvl = 0.6
                elif 64 <= Y <= 78 and 0.25 < (x - xa) / (xb - xa + 0.01) < 0.75:
                    lvl = 0.4 if (x % 2) else 1.6                       # finestreta amb barrots
                cv.put(x, y, HULL, lvl, 0.5)
        lx = round(xa + (xb - xa) * 0.8)
        ly = round(VY + (100 - VY) * (2 / (1 / f0 + 1 / f1)))
        cv.put(lx, ly, CYAN, 3.6, 0)
        cv.glow(lx, ly, 4, (90, 200, 255), 0.5)
        # número
        yy = round(VY + (48 - VY) * f0)
        cv.rect(round(xa) + 1, yy - 1, round(xa) + 8, yy + 5, SIGN, 2.0, 0.5)
        text(cv, round(xa) + 2, yy, num, HULL, 1.0, 0.2, gap=0)

    # canonada al llarg de la paret dreta del passadís
    for x in range(round(FAR_R), OPEN_X1 + 1):
        f = (x - VX) / (OPEN_X1 - VX)
        y = round(VY + (40 - VY) * f)
        th = max(1, round(5 * f))
        for k in range(th):
            cv.put(x, y + k, IRON, [3.4, 2.6, 2.0, 1.4, 0.8][min(4, k * 5 // th)], 0.5)

    # paret del fons amb la porta de l'hangar
    fl, ft, fr, fb = round(FAR_L), round(FAR_T), round(FAR_R), round(FAR_B)
    cv.rect(fl, ft, fr, fb, HULL, lambda x, y: 1.6 + (0.4 if (x - fl) % 14 == 0 else 0), 0.4)
    DX0, DX1, DT = 258, 287, 79
    cv.rect(DX0 - 2, DT - 2, DX1 + 2, fb, HULL, 0.4, 0)
    for y in range(DT, fb + 1):
        for x in range(DX0, DX1 + 1):
            mid = (DX0 + DX1) / 2
            lvl = 2.2 - abs(x - mid) / 16 + (0.8 if x in (DX0, round(mid) + 1) else 0) - (0.9 if x == round(mid) else 0)
            if 88 <= y <= 92:
                lvl = 3.2 if (x + y) // 2 % 2 else 0.6                  # franja de perill de la porta
            cv.put(x, y, HULL, lvl, 0.3)
    hazard(cv, DX0, 88, DX1, 91, lit=0.2, lvl=3.0, w=2)
    cv.rect(DX0 + 3, 98, DX0 + 6, 101, ORANGE, 3.0, 0)               # rètol de l'hangar
    # pilot vermell sobre la porta
    cv.rect(268, DT - 8, 276, DT - 4, HULL, 1.2, 0)
    cv.rect(269, DT - 7, 275, DT - 5, ALARM, 4.2 + 0.9 * al, 0)
    cv.hline(270, 274, DT - 7, ALARM, 5.0 + 0.6 * al, 0)
    cv.tint(fl, ft, fr, fb + 30, (255, 60, 50), lambda x, y: 0.42 * (1 + 0.3 * al) * red_alarm(x, y))
    cv.glow(272, DT - 6, 22, (255, 70, 60), 0.6)
    if al > 0:                                                         # el halo creix (barreja suau)
        cv.tint(250, DT - 28, 294, DT + 16, (255, 80, 64),
                lambda x, y: 0.22 * al * max(0.0, 1 - math.hypot(x - 272, y - DT + 6) / 22))

    # terra (vestíbul + passadís)
    def floor_extra(x, y):
        v = 0.0
        if y < FLOOR_Y:
            v -= (FLOOR_Y - y) / (FLOOR_Y - FAR_B) * 0.7
        return v

    deck(cv, VX, VY, FS, FK, FOU, FOV, y0=round(FAR_B) + 1, inside=floor_inside, extra=floor_extra, wall_y=FAR_B)
    cv.tint(OPEN_X0, round(FAR_B), OPEN_X1, 160, (255, 60, 50), lambda x, y: 0.3 * (1 + 0.3 * al) * red_alarm(x, y * 0.7 + 30))
    # línia groga de guia, cap a la porta del fons
    for y in range(round(FAR_B) + 1, H):
        d = y - VY
        for x in range(W):
            u = (x - 272) / d
            if -0.075 <= u <= 0.075 and floor_inside(x, y):
                lv = 2.4 + 0.6 * LIGHT(x, y) - (0.6 if y < FLOOR_Y else 0) - (0.5 if abs(u) > 0.06 else 0)
                cv.put(x, y, WARN, max(1.6, lv), 0)
    # ombra de contacte a l'entrada del passadís
    cv.darken(OPEN_X0 - 2, 150, OPEN_X0 + 6, 160, lambda x, y: 0.6 * (1 - (x - OPEN_X0 + 2) / 8))

    # ─── Parets davanteres ────────────────────────────────────────────────
    wall(cv, 0, OPEN_X0 - 1, seed=1)
    wall(cv, OPEN_X1 + 1, W - 1, seed=3)
    # cantonades de l'obertura (perfil gruixut)
    for x0, sgn in ((OPEN_X0 - 4, 1), (OPEN_X1 + 1, -1)):
        for i in range(4):
            cv.vline(x0 + i, OPEN_TOP, 153, HULL, [3.8, 3.0, 2.2, 1.0][i if sgn > 0 else 3 - i] + 0.3)
    # llinda i biga del sostre, amb franges de perill sobre l'obertura
    cv.rect(0, 0, W - 1, 9, HULL, lambda x, y: 0.8 + (0.6 if y in (7, 8) else 0) + (hr(x // 24, 3) - 0.5) * 0.2)
    cv.hline(0, W - 1, 10, HULL, 3.4)
    cv.hline(0, W - 1, 11, HULL, 1.0)
    cv.rect(OPEN_X0 - 4, OPEN_TOP - 12, OPEN_X1 + 4, OPEN_TOP - 1, HULL, lambda x, y: 2.8 - (y - OPEN_TOP + 12) * 0.12)
    hazard(cv, OPEN_X0 - 2, OPEN_TOP - 9, OPEN_X1 + 2, OPEN_TOP - 4, lvl=3.0, w=4)
    cv.hline(OPEN_X0 - 4, OPEN_X1 + 4, OPEN_TOP - 1, HULL, 0.4)
    # rètol del mòdul sobre l'obertura
    cv.rect(213, 3, 255, 10, SIGN, 3.0, 0.3)
    text(cv, 216, 4, 'MODUL C', HULL, 1.0, 0.1)
    # safata de cables al llarg del sostre
    for x in range(0, W):
        if OPEN_X0 - 4 <= x <= OPEN_X1 + 4:
            continue
        cv.put(x, 14, IRON, 2.6)
        cv.put(x, 15, IRON, 1.6)
        if x % 9 == 0:
            cv.vline(x, 12, 15, IRON, 3.0)
    for x in range(0, OPEN_X0 - 4):
        for k, (yy, rr) in enumerate(((16, ORANGE), (17, HULL), (18, TEAL))):
            if hr(x // 12, k) > 0.15:
                cv.put(x, yy + (1 if (x // 30) % 2 and k == 1 else 0), rr, 1.6 if rr is not HULL else 1.2)

    # ─── Porta de la cel·la 9 (8..65 × 46..155) ───────────────────────────
    CX0, CX1, CT = 12, 61, 58
    cv.rect(CX0 - 4, CT - 6, CX1 + 4, 153, HULL, lambda x, y: 1.0 if x in (CX0 - 4, CX1 + 4) else 3.0 - (0.8 if x > CX1 else 0))
    cv.rect(CX0 - 2, CT - 4, CX1 + 2, CT - 1, HULL, 3.8)
    for y in range(CT, 154):
        for x in range(CX0, CX1 + 1):
            u = (x - CX0) / (CX1 - CX0)
            lvl = 2.4 + math.sin(u * math.pi) * 0.6 - u * 0.4
            if (y - CT) in (34, 35) or (y - CT) in (70, 71):
                lvl += 1.0 if (y - CT) % 2 == 0 else -1.2           # costures horitzontals
            if x in (CX0, CX0 + 1):
                lvl += 1.0
            if x in (CX1, CX1 - 1):
                lvl -= 1.2
            # rovell a la part de baix
            if y > 132:
                lvl -= (y - 132) / 21 * 0.9                                 # brutícia de baix
            if y > 128 and hr(x, 11) > 0.84 and y - 128 < hr(x, 4) * 24:
                cv.put(x, y, RUSTG, 2.6 - (y - 128) / 20)                  # regalims de rovell
                continue
            cv.put(x, y, HULL, lvl)
    # finestreta amb barrots
    WX0, WX1, WY0, WY1 = 24, 49, 68, 86
    cv.rect(WX0 - 2, WY0 - 2, WX1 + 2, WY1 + 2, HULL, lambda x, y: 4.2 if y < WY0 or x < WX0 else 1.0)
    cv.rect(WX0, WY0, WX1, WY1, SPACE, lambda x, y: 1.4 + (y - WY0) / 20, 0)
    for x in range(WX0 + 2, WX1, 4):
        cv.vline(x, WY0, WY1, HULL, 3.4)
        cv.vline(x + 1, WY0, WY1, HULL, 1.6)
    # cartellet amb el 9
    cv.rect(27, 46, 46, 58, SIGN, lambda x, y: 4.2 - (y - 46) * 0.12, 0.4)
    cv.hline(27, 46, 58, HULL, 0.8)
    g = FONT['9']
    for j in range(5):
        for i in range(3):
            if g[j * 3 + i] == '#':
                cv.rect(32 + i * 2, 47 + j * 2, 33 + i * 2, 48 + j * 2, HULL, 0.6, 0)
    # pany magnètic M-3 (per fora, a l'esquerra)
    cv.rect(16, 100, 23, 114, HULL, lambda x, y: 1.4 if x == 23 or y == 114 else 3.2)
    cv.rect(17, 103, 22, 106, CYAN, lambda x, y: 3.6 - (y - 103) * 0.3, 0)
    cv.glow(19.5, 104.5, 10, (90, 200, 255), 0.6)
    cv.rect(18, 109, 21, 111, HULL, 0.6)
    # frontisses
    for y in (CT + 8, 140):
        cv.rect(CX1 - 1, y, CX1 + 2, y + 6, HULL, lambda x, y_: 4.0 - (x - CX1) * 0.8)
    # trapa del menjar
    cv.rect(26, 126, 47, 133, HULL, lambda x, y: 1.0 if y == 133 or x == 47 else (4.0 if y == 126 else 2.8))
    cv.hline(28, 45, 129, HULL, 0.8)
    cv.rect(35, 130, 38, 131, HULL, 4.2)
    # reblons del marc
    for y in range(CT + 2, 152, 12):
        cv.put(CX0 - 3, y, HULL, 4.6)
        cv.put(CX1 + 3, y, HULL, 2.6)
    # ratllades a la porta (palitos de comptar dies)
    for i in range(6):
        cv.vline(16 + i * 2, 118, 124, HULL, 4.4)
    cv.line(15, 123, 25, 119, HULL, 4.4)

    # ─── Aplic sobre la cel·la i quadre d'intèrfon ────────────────────────
    wall_lamp(cv, 104, 26, w=16)
    cv.rect(92, 74, 110, 98, HULL, lambda x, y: 1.0 if x == 110 or y == 98 else 3.4)
    cv.rect(94, 77, 108, 86, SPACE, 2.6, 0)
    for y in range(78, 86, 2):
        cv.hline(95, 95 + int(hr(y, 3) * 11), y, TEAL, 3.6, 0)
    if (tt * 4) % 1 >= 0.5:                                            # el cursor de l'intèrfon
        cv.rect(97 + int(hr(84, 3) * 11), 84, 98 + int(hr(84, 3) * 11), 84, TEAL, 5.0, 0)
    cv.glow(101, 81, 12, (90, 220, 200), 0.35)
    for i in range(3):
        cv.rect(95 + i * 5, 90, 97 + i * 5, 93, HULL, 2.2)
    cv.put(97 + 10, 91, PILOT, 3.0, 0)
    # extintor? no: caixa de mànega d'emergència vermella, tancada
    cv.rect(118, 98, 138, 132, RED, lambda x, y: 3.0 - (x - 118) * 0.04 - (0.9 if x == 138 or y == 132 else 0) + (0.8 if x == 118 or y == 98 else 0))
    cv.rect(121, 102, 135, 118, RED, 2.0)
    cv.rect(122, 104, 134, 116, SPACE, 3.6, 0.3)
    cv.ring(128, 110, 4, RED, 3.4, 0.3, step=20)
    cv.rect(134, 121, 136, 126, IRON, 3.0)
    cv.darken(119, 133, 139, 136, 0.5)

    # ─── Paret dreta: cartell, càmera, porta de la Sala de la Memòria ─────
    # tira de llum sobre el cartell
    cv.rect(346, 28, 402, 31, HULL, 1.6)
    cv.hline(348, 400, 31, LAMPW, 1.4 if strip_off else 3.8, 0)
    if not strip_off:
        cv.glow(374, 33, 40, (200, 235, 255), 0.35)

    # Cartell del reciclatge (324..425 × 38..77): somriure, fletxa cap al fons
    PX0, PY0, PX1, PY1 = 327, 39, 421, 74
    cv.rect(PX0 + 2, PY0 + 2, PX1 + 2, PY1 + 2, HULL, 0.6)                   # ombra
    for y in range(PY0, PY1 + 1):
        for x in range(PX0, PX1 + 1):
            lvl = 3.4 + (hr(x // 2, y // 3, 5) - 0.5) * 0.2
            if y >= PY1 - 1 or x >= PX1 - 1:
                lvl -= 0.6
            cv.put(x, y, SIGN, lvl, 0.4)
    cv.rect(PX0, PY0, PX1, PY0 + 7, CORPG, 2.5, 0)                            # capçalera verda
    text(cv, PX0 + 6, PY0 + 1, 'RECICLATGE', SIGN, 4.5, 0.0)
    smile(cv, 356, 59, 10)
    # fletxa gran cap a l'esquerra (cap al passadís)
    for y in range(52, 67):
        k = abs(y - 59)
        for x in range(374 + k, 392 + (0 if k <= 3 else -50)):
            if x < 392:
                cv.put(x, y, CORPG, 2.5 + (1 if y < 56 else 0), 0)
    for y in range(56, 63):
        for x in range(390, 414):
            cv.put(x, y, CORPG, 2.5 + (1 if y < 58 else 0), 0)
    text(cv, 380, 67, 'PER AQUI', HULL, 1.4, 0.2)
    # un tros arrencat? no: les puntes de cinta adhesiva
    for x, y in ((PX0 - 1, PY0 - 1), (PX1 - 2, PY0 - 1), (PX0 - 1, PY1 - 2), (PX1 - 2, PY1 - 2)):
        cv.rect(x, y, x + 3, y + 3, SIGN, 3.5, 0.3)
    # canto superior dret una mica despenjat
    cv.put(PX1, PY0, HULL, 2.0)
    if strip_off:                                                      # la tira parpelleja: el cartell s'enfosqueix
        cv.tint(PX0 - 1, PY0 - 1, PX1 + 2, PY1 + 2, (8, 10, 16), 0.3)

    # Càmera de vigilància (409..447 × 10..35)
    cv.rect(436, 12, 441, 20, HULL, lambda x, y: 3.0 - (x - 436) * 0.3)        # suport
    cv.rect(432, 10, 445, 13, HULL, 2.0)
    for y in range(18, 31):
        t = (y - 18) / 12                                                   # (tapa el `t` del cicle: fem servir `tt`)
        x0 = round(414 + t * 2)
        for x in range(x0, 444):
            lvl = 4.0 - t * 1.6 - (x - x0) / 60
            if y == 18:
                lvl += 0.8
            if y == 30:
                lvl = 1.0
            cv.put(x, y, PANEL, lvl)
    cv.rect(410, 20, 415, 28, HULL, lambda x, y: 1.0 + (y - 20) * 0.1)     # objectiu
    cv.disc(412, 24, 2, 3, SPACE, lambda nx, ny: 2.0 - nx - ny, 0)
    cv.put(411, 23, CYAN, 4.0, 0)
    if (tt * 3 + 0.2) % 1 < 0.75:                                      # el LED de la càmera fa pampallugues
        cv.put(438, 23, PILOT, 3.6, 0)
        cv.put(438, 22, PILOT, 2.6, 0)
        cv.glow(438, 23, 6, (90, 255, 120), 0.6)
    else:
        cv.put(438, 23, PILOT, 1.0, 0)
        cv.put(438, 22, PILOT, 0.6, 0)
    cv.line(441, 13, 470, 13, HULL, 0.6)                                    # cable
    cv.darken(414, 31, 444, 34, 0.35)

    # Porta de la Sala de la Memòria (354..403 × 76..153): porta enretirada amb rètol
    MX0, MX1, MT = 360, 397, 95
    cv.rect(354, 79, 403, 153, HULL, lambda x, y: 3.6 if x <= 356 else (1.2 if x >= 401 else 2.8))
    cv.rect(357, 93, 400, 153, HULL, 0.5, 0.4)                                  # bruna de l'obertura
    for x in range(357, 360):                                                  # brancal il·luminat (perspectiva)
        cv.vline(x, 93, 153, HULL, 2.6 - (x - 357) * 0.4)
    for y in range(MT, 154):
        for x in range(MX0, MX1 + 1):
            u = (x - MX0) / (MX1 - MX0)
            lvl = 3.0 + (0.4 if u < 0.5 else 0.1) - abs(u - 0.5) * 0.6
            if abs(x - (MX0 + MX1) / 2) < 0.6:
                lvl = 0.8                                                     # porta corredissa de dues fulles
            if 120 <= y <= 121:
                lvl += 0.8 if y == 120 else -0.6
            cv.put(x, y, PANEL, lvl, 0.6)
    # rètol lluminós «SALA DE LA MEMÒRIA» amb el somriure
    cv.rect(356, 78, 401, 92, SIGN, 4.2, 0.2)
    cv.rect(356, 79, 401, 79, SIGN, 5.0, 0)
    text(cv, 359, 80, 'SALA DE LA', CORPG, 1.6, 0.0, gap=0)
    text(cv, 359, 86, 'MEMORIA', CORPG, 1.6, 0.0, gap=1)
    smile(cv, 394, 88, 3, lit=0, lvl=3.8)
    cv.glow(378, 84, 20, (220, 250, 240), 0.3)
    # control d'accés (tancat: vermell)
    cv.rect(406, 112, 412, 124, HULL, lambda x, y: 1.0 if x == 412 else 3.2)
    cv.rect(407, 115, 411, 118, ALARM, 3.6, 0)
    cv.glow(409, 116, 6, (255, 80, 60), 0.4)
    # horari («visites de reeducació, els dimarts»)
    cv.rect(406, 96, 418, 108, SIGN, 3.0, 0.4)
    for y in range(98, 107, 2):
        cv.hline(408, 408 + int(hr(y, 7) * 8), y, HULL, 1.4, 0.2)

    # cartell vell, mig arrencat, a la paret (detall)
    cv.rect(440, 70, 466, 92, SIGN, lambda x, y: 2.4 + (hr(x // 2, y // 2, 8) - 0.5) * 0.3 - (0.8 if x > 460 and y > 84 else 0), 0.5)
    smile(cv, 450, 79, 4, lit=0.4, lvl=2.4)
    for x in range(441, 466):
        if hr(x, 3) > 0.5:
            cv.put(x, 92 - int(hr(x, 4) * 3), HULL, 2.0)
    for y in range(74, 90, 3):
        cv.hline(456, 463, y, HULL, 1.4, 0.4)

    # Ombres de contacte a la línia paret-terra, a tot arreu
    cv.darken(0, 154, W - 1, 158, lambda x, y: 0.6 - (y - 154) * 0.13 if not (OPEN_X0 <= x <= OPEN_X1) else 0)


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
    cv.poly([(ax, ay), (bx, by), (cx_, cy_), (dx, dy)], DECK, 0.1, 0)
    # la planxa, aixecada pel cantó de davant a la dreta
    lift = [(ax, ay - 1), (bx + 1, by - 3), (cx_ + 2, cy_ - 8), (dx + 1, dy - 2)]
    cv.poly(lift, DECK, lambda x, y: 3.4 + (x - dx) / 26 - (y - ay) / 30 + (hr(x // 3, y // 3, 4) - 0.5) * 0.3)
    # costures i cargols de la planxa
    cv.line(lift[0][0], lift[0][1], lift[1][0], lift[1][1], DECK, 4.6)
    cv.line(lift[0][0], lift[0][1], lift[3][0], lift[3][1], DECK, 4.0)
    # cantell gruixut de davant (es veu perquè està aixecada)
    for k in range(3):
        cv.line(lift[3][0], lift[3][1] + k, lift[2][0], lift[2][1] + k, DECK, [5.0, 2.6, 1.2][k])
    cv.line(lift[2][0], lift[2][1], lift[1][0], lift[1][1], DECK, 3.0)
    for (u, v) in ((0.15, 0.2), (0.85, 0.2), (0.15, 0.8)):
        x = lift[0][0] + (lift[1][0] - lift[0][0]) * u + (lift[3][0] - lift[0][0]) * v
        y = lift[0][1] + (lift[1][1] - lift[0][1]) * u + (lift[3][1] - lift[0][1]) * v
        cv.put(x, y, DECK, 5.4)
        cv.put(x + 1, y, DECK, 1.0)
    # el paper doblegat que treu el cap per l'escletxa
    px, py = round(cx_ - 9), round(cy_ - 3)
    cv.poly([(px - 5, py - 1), (px + 3, py - 3), (px + 6, py + 1), (px - 3, py + 2)], PAPER, 4.4, 0.5)
    cv.line(px - 4, py, px + 4, py - 2, PAPER, 2.8, 0.5)
    cv.put(px + 5, py + 1, PAPER, 2.4, 0.5)
    # cargols fora de lloc, al terra
    cv.put(round(cx_ + 5), round(cy_ - 2), DECK, 5.4)
    cv.put(round(cx_ + 6), round(cy_ - 2), DECK, 1.6)
    cv.put(round(cx_ + 3), round(cy_ + 2), DECK, 5.0)
    # ombra de la planxa
    cv.line(dx + 2, dy + 1, cx_ + 1, cy_ + 1, DECK, 0.0, 0)


def _ambient_frames(n=24):
    """N fotogrames transparents amb només els píxels que canvien respecte de bg(t=0)."""
    from hd.pix import Canvas
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


ANIMS = {'ambient': {'frames': _ambient_frames, 'frameDuration': 125}}

PROPS = {'rajola': rajola}
