"""
Portada, a 640×360 (vegeu hd/rooms/portada.py, la de 480×270): la fàbrica de ferro-9 (el passat, a l'esquerra) i
La Gavina en òrbita (el present, a la dreta), partides per un tall en diagonal que brilla, i el títol «FERRO-9» en
lletres de metall: el cel fred a dalt i el foc dels forns reflectit a baix.
  - la mateixa composició ×4/3, amb els dos pròlegs de 640;
  - el títol, amb mòduls d'11 píxels (8 a 480): xamfrans de 4, un segon bisell a dins, el metall raspallat a
    ratlles i el foc amb gra; l'extrusió, d'un píxel més;
  - els botons de la GUI `portada` van a 220..420 × 224..328 (×4/3 de 165..315 × 168..246): la zona fosca els
    cobreix tots tres (a 480 el de «Continua» quedava a la vora) i allà no s'hi anima res.
Pantalla sencera (sense barra de verbs). Reutilitza els dos pròlegs.
"""
import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

import math

from hd.pix import Canvas, Light, W, H, hr, mix, ramp, STEEL
from hd640.rooms import proleg_fabrica_pla_comu as fab
from hd640.rooms.proleg_gavina_pla_comu import espai, terra, gavina, vinyeta, ambient_frames

K = 4 / 3                                  # 480 → 640

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)

# El tall: de (SEAM_TOP, 0) a (SEAM_BOT, H)
SEAM_TOP, SEAM_BOT = 368, 272

# On van els botons de la GUI (x0, y0, x1, y1), i el rectangle on no s'hi anima res
BOTONS = (220, 224, 420, 328)
QUIET = (210, 214, 430, 338)


def seam_x(y):
    return SEAM_TOP + (SEAM_BOT - SEAM_TOP) * y / (H - 1)


# Lletres de 5×7, totes d'angles rectes: l'arrodoniment el fan els xamfrans de les cantonades.
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
    ch_ = round(3 * m / 8)                                          # el xamfrà (3 a 480, amb m = 8)
    for i, ch in enumerate(text):
        g = LLETRES[ch]
        if len(g[0]) == 10:                                         # lletra dibuixada a mig mòdul, sense xamfrans
            edge = lambda c: round(c * m / 2)                       # (amb m senar, els mig mòduls fan 5 i 6)
            for r, row in enumerate(g):
                for c, b in enumerate(row):
                    if b == '1':
                        bx, by = x0 + i * 6 * m, y0
                        pix.update((bx + u, by + v) for u in range(edge(c), edge(c + 1))
                                   for v in range(edge(r), edge(r + 1)))
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


def title(cv, text, cx, y0, m=11, depth=5):
    M = title_mask(text, cx, y0, m)
    ys = [p[1] for p in M]
    top, bot = min(ys), max(ys)
    # ombra caiguda, suau
    sh = {(x + depth + 4, y + depth + 5) for x, y in M}
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
        if not below and (x + y) % 6 == 0:
            lvl += 0.5                                               # el raspallat de la cara lateral
        cv.put(x, y, EMBER if below else STEEL, lvl - (0.8 if below else 0), 0)
    # cara frontal
    hor = top + (bot - top) * 0.52                                   # l'horitzó del reflex
    for x, y in M:
        up = (x, y - 1) not in M
        left = (x - 1, y) not in M
        down = (x, y + 1) not in M
        right = (x + 1, y) not in M
        up2 = (x, y - 2) not in M
        left2 = (x - 2, y) not in M
        if y < hor:
            # el cel: de blanc a blau acer, cap a l'horitzó, raspallat a ratlles
            lvl = 7.6 - ((y - top) / (hor - top)) ** 1.4 * 4.2 + (hr(y, x // 37, 77) - 0.5) * 0.5
            rmp = CHROME
        else:
            # el foc: de fosc a l'horitzó a ataronjat a baix, amb gra
            tt = (y - hor) / (bot - hor)
            lvl = 1.0 + tt * 3.8 + (hr(x // 2, y, 78) - 0.5) * 0.35
            rmp = EMBER
        if up or left:
            rmp, lvl = CHROME, 8.0                                   # bisell il·luminat
        elif down or right:
            rmp, lvl = (EMBER, 1.6) if y >= hor else (CHROME, 2.4)
        elif up2 or left2:
            lvl += 0.9                                               # el segon bisell, més suau
        cv.put(x, y, rmp, lvl, 0)
        if abs(y - hor) < 0.6 and not (up or left or down or right):
            cv.put(x, y, CHROME, 1.5, 0)                             # la línia fosca de l'horitzó
        elif abs(y - hor - 1) < 0.6 and not (up or left or down or right):
            cv.put(x, y, EMBER, 0.6, 0)
    return M


def sparkle(cv, x, y, n=4):
    cv.flat(x, y, (255, 255, 255))
    for k in range(1, n + 1):
        c = mix((255, 255, 255), (150, 190, 255), k / (n + 1))
        for dx, dy in ((k, 0), (-k, 0), (0, k), (0, -k)):
            cv.flat(x + dx, y + dy, c)
    for dx, dy in ((1, 1), (-1, -1), (1, -1), (-1, 1)):
        cv.flat(x + dx, y + dy, (200, 220, 255))
    for dx, dy in ((2, 2), (-2, -2), (2, -2), (-2, 2)):
        cv.flat(x + dx, y + dy, mix(cv.get(x + dx, y + dy), (170, 200, 255), 0.5))
    cv.glow(x, y, 9, (200, 220, 255), 0.4)


def glint(cv, M, t):
    """Un destell que travessa el títol en diagonal, un sol cop per bucle (entre t = 0,3 i 0,62)."""
    a, b = 0.30, 0.62
    if not a <= t < b:
        return
    xs = [p[0] for p in M]
    ys = [p[1] for p in M]
    x0, top = min(xs), min(ys)
    span = max(xs) - x0 + (max(ys) - top) * 0.6 + 53
    c = -27 + (t - a) / (b - a) * span
    for x, y in M:
        d = abs((x - x0) + (y - top) * 0.6 - c)
        k = max(0.0, 1 - d / 8) * 0.75 + (0.25 if d < 2 else 0)
        if k > 0:
            cv.flat(x, y, mix(cv.get(x, y), (255, 255, 255), min(1.0, k)))


def bg(cv, t=0.0, titol=True):
    """`t` (0..1): moment del bucle de l'animació de fons (amb 0, el fons quiet). Amb `titol=False`, sense el títol
    ni la zona fosca dels botons (els crèdits)."""
    # el present: l'espai, la Terra i La Gavina
    espai(cv, x0=240, t=t)
    terra(cv, 667, 512, 248, x0=240, t=t)
    gavina(cv, 483, 173, 0.66 * K, t=t)
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
        cv.flat(round(sx) - 2, y, mix(cv.get(round(sx) - 2, y), (255, 170, 90), 0.25))
        cv.flat(round(sx) + 2, y, mix(cv.get(round(sx) + 2, y), (110, 190, 255), 0.25))
    for y in range(0, H, 4):
        sx = seam_x(y)
        cv.glow(sx - 4, y, 9, (255, 170, 90), 0.12)
        cv.glow(sx + 4, y, 9, (110, 190, 255), 0.12)

    if not titol:
        vinyeta(cv, 0.5)
        return
    # fosc a dalt (on va el títol) i a baix al mig (on van els botons)
    cv.darken(0, 0, W - 1, 120, lambda x, y: 0.45 * (1 - y / 120), dither=False)
    cv.darken(165, 200, 475, H - 1, lambda x, y: 0.5 * max(0.0, 1 - math.hypot((x - 320) / 150, (y - 276) / 70) ** 2), dither=False)

    # el títol
    M = title(cv, 'FERRO-9', W / 2, 19, m=11, depth=5)
    glint(cv, M, t)
    # les dues espurnes: la de l'esquerra s'encén quan el destell hi entra, la de la dreta quan en surt
    sparkle(cv, min(p[0] for p in M) + 4, 21, 6 if 0.29 <= t < 0.36 else 5)
    xs = [p[0] for p in M]
    sparkle(cv, max(xs) - 4, 53, 6 if 0.58 <= t < 0.62 else 5 if 0.62 <= t < 0.7 else 4)
    vinyeta(cv, 0.5)


PROPS = {}

# Res d'animació sota els botons de la GUI (220..420 × 224..328), amb marge
ANIMS = {'ambient': {'frames': lambda: ambient_frames(bg, LIGHT, mask=QUIET), 'frameDuration': 130}}
