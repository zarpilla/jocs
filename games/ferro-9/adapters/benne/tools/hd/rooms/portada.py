"""
Portada: la fàbrica de ferro-9 (el passat, a l'esquerra) i La Gavina en òrbita (el present, a la dreta), partides
per un tall en diagonal que brilla, i el títol «FERRO-9» en lletres de metall: el cel fred a dalt i el foc dels
forns reflectit a baix. A sota, al mig (x 165..315, y 196..246), hi van els botons de la GUI: aquella zona queda fosca.
Pantalla sencera (sense barra de verbs). Reutilitza els dos pròlegs.
"""
import math

from hd.pix import Canvas, Light, W, H, mix, ramp, STEEL
from hd.rooms import proleg_fabrica as fab
from hd.rooms.proleg_gavina import espai, terra, gavina, vinyeta, ambient_frames

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)

# El tall: de (SEAM_TOP, 0) a (SEAM_BOT, H)
SEAM_TOP, SEAM_BOT = 276, 204


def seam_x(y):
    return SEAM_TOP + (SEAM_BOT - SEAM_TOP) * y / (H - 1)


# Lletres de 5×7, totes d'angles rectes (les diagonals de room_designs.py es trencaven): l'arrodoniment el fan
# els xamfrans de les cantonades.
LLETRES = {
    'F': ['11111', '10000', '10000', '11110', '10000', '10000', '10000'],
    'E': ['11111', '10000', '10000', '11110', '10000', '10000', '11111'],
    # la R, a mitja mòdul: bucle tancat, cantonada de dalt-esquerra recta i una osca a la dreta abans de la cama
    'R': ['1111111100', '1111111110', '1100000011', '1100000011', '1100000011', '1100000011', '1111111110',
          '1111111100', '1100001100', '1100001110', '1100000111', '1100000011', '1100000011', '1100000011'],
    'O': ['11111', '10001', '10001', '10001', '10001', '10001', '11111'],
    '-': ['00000', '00000', '00000', '01110', '00000', '00000', '00000'],
    '9': ['11111', '10001', '10001', '11111', '00001', '00001', '11111'],
}

# Rampes del metall del títol: el cel (fred) a dalt, el foc (calent) a baix
CHROME = ramp((10, 14, 30), (34, 52, 86), (76, 104, 146), (130, 162, 200), (190, 214, 236), (236, 246, 255), (255, 255, 255), n=9)
EMBER = ramp((40, 16, 14), (96, 40, 22), (160, 76, 34), (214, 124, 56), (244, 178, 98), (255, 226, 160), n=7)


def title_mask(text, cx, y0, m):
    """Màscara del títol: mòduls de m×m amb les cantonades exteriors aixamfranades."""
    pix = set()
    width = len(text) * 6 * m - m
    x0 = round(cx - width / 2)
    for i, ch in enumerate(text):
        g = LLETRES[ch]
        if len(g[0]) == 10:                                         # lletra dibuixada a mig mòdul, sense xamfrans
            h = m // 2
            for r, row in enumerate(g):
                for c, b in enumerate(row):
                    if b == '1':
                        bx, by = x0 + i * 6 * m + c * h, y0 + r * h
                        pix.update((bx + u, by + v) for u in range(h) for v in range(h))
            continue
        on = lambda c, r: 0 <= r < 7 and 0 <= c < 5 and g[r][c] == '1'
        for r in range(7):
            for c in range(5):
                if not on(c, r):
                    continue
                bx, by = x0 + (i * 6 + c) * m, y0 + r * m
                for v in range(m):
                    for u in range(m):
                        # xamfrans: a les cantonades on no hi ha veí ni a dalt/baix ni al costat
                        ch_ = 3
                        if not on(c, r - 1) and not on(c - 1, r) and u + v < ch_:
                            continue
                        if not on(c, r - 1) and not on(c + 1, r) and (m - 1 - u) + v < ch_:
                            continue
                        if not on(c, r + 1) and not on(c - 1, r) and u + (m - 1 - v) < ch_:
                            continue
                        if not on(c, r + 1) and not on(c + 1, r) and (m - 1 - u) + (m - 1 - v) < ch_:
                            continue
                        pix.add((bx + u, by + v))
    return pix


def title(cv, text, cx, y0, m=7, depth=4):
    M = title_mask(text, cx, y0, m)
    ys = [p[1] for p in M]
    top, bot = min(ys), max(ys)
    # ombra caiguda, suau
    sh = {(x + depth + 3, y + depth + 4) for x, y in M}
    for x, y in sh:
        if 0 <= x < W and 0 <= y < H:
            cv.flat(x, y, mix(cv.get(x, y), (2, 2, 8), 0.55))
    # extrusió (gruix del metall), cap avall a la dreta
    ext = set()
    for k in range(1, depth + 1):
        for x, y in M:
            ext.add((x + k, y + k))
    ext -= M
    # contorn fosc al voltant de tot
    allp = M | ext
    for x, y in allp:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1)):
            q = (x + dx, y + dy)
            if q not in allp:
                cv.flat(*q, (6, 8, 18))
    for x, y in ext:
        # cara lateral: més clara on mira avall (la fàbrica la il·lumina)
        below = (x, y + 1) not in allp
        lvl = 2.0 + (1.0 if below else 0) + (y - top) / (bot - top) * 0.8
        cv.put(x, y, EMBER if below else STEEL, lvl - (0.8 if below else 0), 0)
    # cara frontal
    hor = top + (bot - top) * 0.52                                   # l'horitzó del reflex
    for x, y in M:
        up = (x, y - 1) not in M
        left = (x - 1, y) not in M
        down = (x, y + 1) not in M
        right = (x + 1, y) not in M
        t = (y - top) / (bot - top)
        ly = (y - top) % (7 * m + 0)
        if y < hor:
            # el cel: de blanc a blau acer, cap a l'horitzó
            lvl = 7.6 - ((y - top) / (hor - top)) ** 1.4 * 4.2
            rmp = CHROME
        else:
            # el foc: de fosc a l'horitzó a ataronjat a baix
            tt = (y - hor) / (bot - hor)
            lvl = 1.0 + tt * 3.8
            rmp = EMBER
        if up or left:
            rmp, lvl = CHROME, 8.0                                   # bisell il·luminat
        elif down or right:
            rmp, lvl = (EMBER, 1.6) if y >= hor else (CHROME, 2.4)
        cv.put(x, y, rmp, lvl, 0)
        if abs(y - hor) < 0.6 and not (up or left or down or right):
            cv.put(x, y, CHROME, 1.5, 0)                             # la línia fosca de l'horitzó
    return M


def sparkle(cv, x, y, n=3):
    cv.flat(x, y, (255, 255, 255))
    for k in range(1, n + 1):
        c = mix((255, 255, 255), (150, 190, 255), k / (n + 1))
        for dx, dy in ((k, 0), (-k, 0), (0, k), (0, -k)):
            cv.flat(x + dx, y + dy, c)
    for dx, dy in ((1, 1), (-1, -1), (1, -1), (-1, 1)):
        cv.flat(x + dx, y + dy, (200, 220, 255))
    cv.glow(x, y, 7, (200, 220, 255), 0.4)


def glint(cv, M, t):
    """Un destell que travessa el títol en diagonal, un sol cop per bucle (entre t = 0,3 i 0,62)."""
    a, b = 0.30, 0.62
    if not a <= t < b:
        return
    xs = [p[0] for p in M]
    ys = [p[1] for p in M]
    x0, top = min(xs), min(ys)
    span = max(xs) - x0 + (max(ys) - top) * 0.6 + 40
    c = -20 + (t - a) / (b - a) * span
    for x, y in M:
        d = abs((x - x0) + (y - top) * 0.6 - c)
        k = max(0.0, 1 - d / 6) * 0.75 + (0.25 if d < 1.5 else 0)
        if k > 0:
            cv.flat(x, y, mix(cv.get(x, y), (255, 255, 255), min(1.0, k)))


def bg(cv, t=0.0, titol=True):
    """`t` (0..1): moment del bucle de l'animació de fons (amb 0, el fons quiet). Amb `titol=False`, sense el títol
    ni la zona fosca dels botons (els crèdits)."""
    # el present: l'espai, la Terra i La Gavina
    espai(cv, x0=180, t=t)
    terra(cv, 500, 384, 186, x0=180, t=t)
    gavina(cv, 362, 130, 0.66, t=t)
    # el passat: la fàbrica (sense el rètol, que aquí el títol ja fa de rètol)
    f = Canvas(light=fab.LIGHT)
    fab.bg(f, retol=False, t=t)
    F = f.img.load()
    for y in range(H):
        sx = seam_x(y)
        for x in range(0, math.ceil(sx) + 1):
            if x < sx - 0.5:
                cv.flat(x, y, F[x, y])
    # el tall: una esquerda de llum entre els dos temps
    for y in range(H):
        sx = seam_x(y)
        cv.flat(round(sx), y, (236, 240, 255))
        cv.flat(round(sx) - 1, y, mix(cv.get(round(sx) - 1, y), (255, 190, 110), 0.6))
        cv.flat(round(sx) + 1, y, mix(cv.get(round(sx) + 1, y), (120, 200, 255), 0.6))
    for y in range(0, H, 3):
        sx = seam_x(y)
        cv.glow(sx - 3, y, 7, (255, 170, 90), 0.12)
        cv.glow(sx + 3, y, 7, (110, 190, 255), 0.12)

    if not titol:
        vinyeta(cv, 0.5)
        return
    # fosc a dalt (on va el títol) i a baix al mig (on van els botons)
    cv.darken(0, 0, W - 1, 90, lambda x, y: 0.45 * (1 - y / 90), dither=False)
    cv.darken(130, 180, 350, H - 1, lambda x, y: 0.5 * max(0.0, 1 - math.hypot((x - 240) / 110, (y - 222) / 44) ** 2), dither=False)

    # el títol
    M = title(cv, 'FERRO-9', W / 2, 14, m=8, depth=4)
    glint(cv, M, t)
    # les dues espurnes: la de l'esquerra s'encén quan el destell hi entra, la de la dreta quan en surt
    sparkle(cv, min(p[0] for p in M) + 3, 16, 5 if 0.29 <= t < 0.36 else 4)
    xs = [p[0] for p in M]
    sparkle(cv, max(xs) - 3, 40, 5 if 0.58 <= t < 0.62 else 4 if 0.62 <= t < 0.7 else 3)
    vinyeta(cv, 0.5)


PROPS = {}

# Res d'animació sota els botons de la GUI (x 165..315, y 196..246), amb marge
ANIMS = {'ambient': {'frames': lambda: ambient_frames(bg, LIGHT, mask=(158, 190, 322, 252)), 'frameDuration': 130}}
