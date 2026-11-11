"""
El conducte de servei de la fàbrica (Iri), a 640×360: un revolt. Sempre el mateix, vist de cara: les parets de
planxa reblonada, la canonada de coure que hi corre, el terra de reixeta i tres passadissos (esquerra, recte i
dreta) que s'enfonsen a les fosques. Llum: una sola làmpada de gàbia al sostre.

L'escena es repeteix a cada un dels cinc revolts (guio/guio.md, Acte 3, «La ruta del conducte»), i només en
canvia un detall, un prop per revolt: el cartell (1r), el guant (2n), l'aixeta que degota (3r), la tassa (4t) i el
formulari 27-B denegat (5è).

La geometria (on es clica, on es camina) és a room_designs.py (`CONDUCTE`): els rectangles dels passadissos i dels
detalls coincideixen amb el que es dibuixa aquí (`R()` els passa a píxels de 640).
"""
import math

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from hd.pix import Canvas, Light, W, H, R, hr, IRON, COPPER, RUST, WARN, PAPER, RED, GRAY, WALNUT, MANILA, CYAN, B4  # noqa: F401
from hd640.rooms.gavina_passadis import text, text_w

# ─── Geometria (píxels de 640) ──────────────────────────────────────────────
FAR = (233, 62, 407, 204)            # la paret del fons (on s'obre el passadís de dret)
VP = (320, 133)                      # punt de fuga
LAMP = (320, 34)                     # la làmpada de gàbia
NEAR_BOT = 272                       # on les parets toquen el terra, a primer terme


def ytop(x):
    """Sostre de la paret esquerra a la x (simètrica a la dreta)."""
    x = min(x, W - 1 - x)
    return FAR[1] * x / FAR[0]


def ybot(x):
    """Peu de la paret esquerra a la x (simètrica a la dreta)."""
    x = min(x, W - 1 - x)
    return NEAR_BOT - (NEAR_BOT - FAR[3]) * x / FAR[0]


LEFT = (R(50, 30, 104, 134)[0], R(50, 30, 104, 134)[2])          # x on comença i acaba el passadís de l'esquerra
RIGHT = (W - 1 - LEFT[1], W - 1 - LEFT[0])
STRAIGHT = R(156, 50, 196, 112)
ENRERE = (R(8, 128, 48, 141)[2], R(8, 128, 48, 141)[3])   # cap a la reixa: la cantonada de baix a l'esquerra


def open_top(x):
    """La llinda dels passadissos laterals: una mica per sota del sostre."""
    return ytop(x) + (ybot(x) - ytop(x)) * 0.16


LIGHT = Light(ambient=-0.5, vignette=(110, 40), floor_fade=(300, 60))
LIGHT.point(*LAMP, r=300, k=2.6, squash=0.8, power=1.6)
LIGHT.point(VP[0], 150, r=90, k=0.5)


# ─── Fons ──────────────────────────────────────────────────────────────────

def _plates(cv, x, y, side):
    """Planxa reblonada de les parets laterals: juntes verticals (en perspectiva) i horitzontals cap al punt de fuga."""
    xn = min(x, W - 1 - x)                     # distància a la vora de prop
    t = (y - ytop(x)) / max(1, ybot(x) - ytop(x))
    lvl = 2.3 + (hr(x // 3, y // 4, 7 + side) - 0.5) * 0.35
    # juntes verticals: més juntes com més lluny
    u = xn / FAR[0]
    depth = 1 / (1.0 - 0.72 * u)
    if int(depth * 6) != int((1 / (1.0 - 0.72 * max(0, u - 1 / FAR[0]))) * 6):
        lvl -= 1.3
    if abs(t - 0.5) < 0.012 or abs(t - 0.82) < 0.01:
        lvl -= 1.0
    if 0.24 < t < 0.33:                          # la canonada de coure hi passa per davant: aquí, la seva ombra
        lvl -= 0.6
    lvl -= 0.25 * (1 - t)                        # més fosc a dalt
    return lvl


def _floor(x, y):
    """Terra de reixeta: travessers cap al punt de fuga i barres de través que s'apropen amb la distància."""
    d = (y - FAR[3]) / (H - FAR[3])              # 0 al fons, 1 a baix de tot
    lvl = 1.8 + (hr(x // 2, y // 2, 13) - 0.5) * 0.3
    # travessers (convergeixen)
    k = (x - VP[0]) / max(1, y - VP[1])
    if abs((k * 4) - round(k * 4)) < 0.06:
        lvl += 0.8
    # barres de través
    z = 1 / max(0.04, d)
    if (z * 2.2) % 1 < 0.12:
        lvl -= 0.9
    # reixeta fina, a quadres, només a prop
    if d > 0.35 and (x + y) % 3 == 0 and y % 2 == 0:
        lvl -= 0.5
    return lvl


def _opening(cv, x0, x1, top, bottom, far_left):
    """
    Un passadís lateral que gira: el marc de planxa i, a dins, el terra de reixeta que s'hi endinsa i la paret del
    fons del passadís, que rep una mica de llum a la vora de prop i es perd a les fosques cap a dins.
    """
    for x in range(x0, x1 + 1):
        yt, yb = round(top(x)), round(bottom(x))
        u = (x - x0) / max(1, x1 - x0)
        if not far_left:
            u = 1 - u                          # u: 0 a la vora de prop, 1 a la de lluny
        floor_top = yb - (yb - yt) * (0.30 - 0.12 * u)
        for y in range(yt, yb + 1):
            if y >= floor_top:
                d = (y - floor_top) / max(1, yb - floor_top)
                lvl = 0.8 + 2.4 * (1 - u) ** 1.4 * (0.5 + 0.5 * d)
                if round(y * (1.6 - u)) % 6 == 0:
                    lvl -= 0.8                 # les barres de la reixeta
            else:
                v = (y - yt) / max(1, floor_top - yt)
                lvl = 0.3 + 2.8 * (1 - u) ** 1.8 - 0.4 * v
                if abs(v - 0.55) < 0.025:
                    lvl -= 0.6                 # una junta de la planxa
            cv.put(x, y, IRON, lvl, lit=0.5)
        cv.put(x, round(floor_top), IRON, 0.4 + 1.6 * (1 - u) ** 2)
    # marc: la vora de prop clara, la llinda fosca
    for x in range(x0, x1 + 1):
        cv.put(x, round(top(x)), IRON, 3.6)
        cv.put(x, round(top(x)) + 1, IRON, 2.4)
        cv.put(x, round(top(x)) + 2, IRON, 0.4)
    near = x0 if far_left else x1
    for y in range(round(top(near)), round(bottom(near)) + 1):
        cv.put(near, y, IRON, 4.0)
        cv.put(near + (1 if far_left else -1), y, IRON, 2.6)
        if y % 11 == 3:
            cv.put(near + (2 if far_left else -2), y, IRON, 4.6)        # reblons del marc


def _pipe(cv, side):
    """Canonada de coure al llarg d'una paret lateral, amb abraçadores, que es fica a la paret del fons."""
    for xn in range(0, FAR[0] + 1):
        x = xn if side == 0 else W - 1 - xn
        yt, yb = ytop(x), ybot(x)
        yc = yt + (yb - yt) * 0.26
        r = 7 * (1 - 0.62 * xn / FAR[0])
        if (LEFT[0] <= x <= LEFT[1]) or (RIGHT[0] <= x <= RIGHT[1]):
            continue                                                # el passadís talla la canonada
        for y in range(round(yc - r), round(yc + r) + 1):
            s = (y - yc) / max(1, r)
            lvl = 3.4 - 2.6 * s * s - 1.2 * s
            if xn % max(6, round(46 * (1 - 0.62 * xn / FAR[0]))) < 2:
                cv.put(x, y, IRON, lvl + 0.4)                      # abraçadores
            else:
                cv.put(x, y, COPPER, lvl)
        if hr(xn, 3, side) > 0.93:
            cv.put(x, round(yc + r * 0.4), COPPER, 0.6)           # verdet


def _lamp(cv, swing=0.0, power=1.0):
    """
    La làmpada de gàbia penjada del sostre, amb el cable. `swing`: quants píxels s'ha desplaçat la bombeta
    (es gronxa amb el corrent d'aire del conducte); `power`: la intensitat (parpelleja).
    """
    cx, cy = LAMP
    bx = cx + round(swing)
    cv.line(cx, 0, bx, cy - 9, IRON, 1.2, lit=0.3)
    cv.disc(bx, cy - 6, 9, 4, IRON, lambda nx, ny: 2.0 - ny, lit=0.3)
    cv.disc(bx, cy + 2, 6, 7, WARN, lambda nx, ny: 3.4 + 1.8 * power - (nx * nx + ny * ny) * 1.8, lit=0)
    for dx in (-6, -2, 2, 6):
        cv.line(bx + dx, cy - 3, bx + round(dx * 1.1), cy + 9, IRON, 1.0, lit=0.2)
    cv.hline(bx - 7, bx + 7, cy + 3, IRON, 1.4, lit=0.2)
    cv.glow(bx, cy + 2, 40, (255, 210, 130), 0.55 * power)


def _straight(cv):
    """El passadís de dret, a la paret del fons: un arc fosc que s'allarga amb una llumeta molt lluny."""
    x0, y0, x1, y1 = STRAIGHT
    cx = (x0 + x1) / 2
    rx = (x1 - x0) / 2
    arc_y = y0 + rx * 0.55
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if y < arc_y:
                ny = (arc_y - y) / (arc_y - y0)
                nx = (x - cx) / rx
                if nx * nx + ny * ny > 1:
                    continue
            d = math.hypot((x - cx) / rx, (y - (y0 + y1) / 2) / ((y1 - y0) / 2))
            cv.put(x, y, IRON, -0.8 + 0.9 * min(1, d), lit=0.2)
    # marc de l'arc
    for a in range(0, 181, 2):
        ra = math.radians(a)
        cv.put(round(cx + math.cos(ra) * (rx + 1)), round(arc_y - math.sin(ra) * (arc_y - y0 + 1)), IRON, 3.8)
    for y in range(round(arc_y), y1 + 1):
        cv.put(x0 - 1, y, IRON, 3.4)
        cv.put(x1 + 1, y, IRON, 2.2)
    cv.glow(cx, y0 + (y1 - y0) * 0.55, 10, (150, 110, 70), 0.35)          # una llum al fons de tot


def bg(cv, lamp=True):
    # sostre: planxa fosca
    for y in range(0, FAR[1] + 1):
        for x in range(0, W):
            if y <= ytop(x) or FAR[0] <= x <= FAR[2]:
                lvl = 1.0 + (hr(x // 4, y // 2, 3) - 0.5) * 0.3 - (0.6 if (x - VP[0]) % 53 == 0 else 0)
                cv.put(x, y, IRON, lvl)
    # parets laterals
    for x in range(0, W):
        if FAR[0] <= x <= FAR[2]:
            continue
        side = 0 if x < W / 2 else 1
        for y in range(math.floor(ytop(x)), math.ceil(ybot(x)) + 1):
            cv.put(x, y, IRON, _plates(cv, x, y, side))
    # paret del fons
    cv.rect(FAR[0], FAR[1], FAR[2], FAR[3], IRON, lambda x, y: 1.8 + (hr(x // 3, y // 3, 5) - 0.5) * 0.3
            - (1.0 if (x - FAR[0]) % 44 == 0 or (y - FAR[1]) % 36 == 0 else 0))
    for x in range(FAR[0] + 4, FAR[2], 11):
        cv.put(x, FAR[1] + 3, IRON, 4.2)
        cv.put(x, FAR[3] - 4, IRON, 3.6)
    # terra
    for y in range(FAR[3] + 1, H):
        for x in range(0, W):
            if y >= ybot(x) - 0.5:
                cv.put(x, y, IRON, _floor(x, y))
    # arestes: on les parets toquen el sostre i el terra
    cv.line(0, 0, FAR[0], FAR[1], IRON, 0.2)
    cv.line(W - 1, 0, FAR[2], FAR[1], IRON, 0.2)
    cv.line(0, NEAR_BOT, FAR[0], FAR[3], IRON, 0.0)
    cv.line(W - 1, NEAR_BOT, FAR[2], FAR[3], IRON, 0.0)
    cv.hline(FAR[0], FAR[2], FAR[3], IRON, 0.2)
    # els tres passadissos
    _opening(cv, LEFT[0], LEFT[1], open_top, ybot, far_left=False)
    _opening(cv, RIGHT[0], RIGHT[1], open_top, ybot, far_left=True)
    _straight(cv)
    _pipe(cv, 0)
    _pipe(cv, 1)
    if lamp:
        _lamp(cv)
    # la llum de la reixa de la cambra, que entra per darrere, a baix a l'esquerra: el camí de tornada
    ex, ey = ENRERE
    for y in range(ey - 60, H):
        for x in range(0, ex + 120):
            a = max(0.0, 1 - ((x - ex * 0.4) / 130) ** 2 - ((y - 262) / 60) ** 2) * 0.9
            if a > 0 and a > B4[y & 3][x & 3] * 0.5:
                o = cv.P[x, y]
                cv.P[x, y] = (min(255, int(o[0] + 70 * a)), min(255, int(o[1] + 52 * a)), min(255, int(o[2] + 34 * a)), 255)


# ─── Detalls: un per revolt ────────────────────────────────────────────────

def cartell(cv):
    """1r revolt: un rètol esmaltat, groc, cargolat a la paret del fons."""
    x0, y0, x1, y1 = R(132, 52, 152, 66)
    cv.rect(x0, y0, x1, y1, WARN, lambda x, y: 3.6 - (y - y0) * 0.04, lit=0.5)
    cv.rect(x0, y0, x1, y0, WARN, 4.6, lit=0.5)
    cv.rect(x0, y1, x1, y1, WARN, 1.6, lit=0.5)
    for x, y in ((x0 + 2, y0 + 2), (x1 - 2, y0 + 2), (x0 + 2, y1 - 2), (x1 - 2, y1 - 2)):
        cv.put(x, y, IRON, 1.0)
    w = text_w('NO', small=True)
    text(cv, (x0 + x1) // 2 - w // 2, y0 + 5, 'NO', IRON, 0.8, lit=0.2, small=True)
    w = text_w('FUMAR', small=True)
    text(cv, (x0 + x1) // 2 - w // 2, y0 + 13, 'FUMAR', IRON, 0.8, lit=0.2, small=True)
    cv.line(x0 + 3, y1 - 3, x1 - 3, y0 + 3, RED, 3.0, lit=0.3)


def guant(cv):
    """2n revolt: un guant de treball de pell, oblidat a terra."""
    x0, y0, x1, y1 = R(208, 125, 224, 133)
    rows = [
        '......aa.aa.....',
        '.....abbaabba...',
        '....abbbbbbba.a.',
        '...abbbbbbbbaaba',
        '..abbbbbbbbbbbba',
        '.abbbbbbbbbbbba.',
        'abbbbbbbbbbbba..',
        'acccccbbbbbba...',
        'accccccaaaaa....',
        '.aaaaaa.........',
    ]
    cv.sprite(rows, x0 + 2, y0 + 3, {'a': (WALNUT, 1.6), 'b': (MANILA, 2.6), 'c': (MANILA, 1.4)}, lit=0.6)
    cv.hline(x0 + 2, x0 + 16, y0 + 13, IRON, 0.2)                           # l'ombra


AIXETA = R(200, 56, 218, 92)
DRIP_X = (AIXETA[0] + AIXETA[2]) // 2 + 12          # on cau la gota (sota el broc)
DRIP_Y0 = AIXETA[1] + 46                            # surt del broc
PUDDLE = (DRIP_X, AIXETA[3] + 6)                    # el bassal


def _aixeta_fixa(cv):
    x0, y0, x1, y1 = AIXETA
    cx = (x0 + x1) // 2
    for y in range(y0, y0 + 40):
        for dx in range(-3, 4):
            cv.put(cx + dx, y, COPPER, 3.4 - abs(dx + 1) * 0.6)
    cv.rect(cx - 5, y0 + 40, cx + 5, y0 + 44, IRON, 2.6)                 # el cos de l'aixeta
    cv.rect(cx + 5, y0 + 41, cx + 12, y0 + 43, IRON, 2.2)                # el broc
    cv.vline(cx + 12, y0 + 43, y0 + 45, IRON, 1.8)
    cv.disc(cx, y0 + 36, 6, 2, RED, lambda nx, ny: 3.2 - ny, lit=0.5)    # el volant
    bx, by = PUDDLE
    cv.disc(bx, by, 14, 3, CYAN, lambda nx, ny: 0.9 - ny * 0.5, lit=0.4)   # el bassal
    cv.hline(bx - 5, bx + 2, by - 1, CYAN, 2.6, lit=0.3)


def aixeta(cv, f=None):
    """
    3r revolt: un tub de coure amb una aixeta que degota, i el bassal a sota. `f`: fotograma de l'animació de la
    gota (vegeu `_gota_frames`); sense, la gota penja del broc.
    """
    _aixeta_fixa(cv)
    bx, by = PUDDLE
    fall = by - 2 - DRIP_Y0
    if f is None or f < 4:                                       # la gota s'infla al broc
        r = 0 if f is None else f
        cv.put(DRIP_X, DRIP_Y0, CYAN, 3.0 + r * 0.3, lit=0.2)
        if r >= 2:
            cv.put(DRIP_X, DRIP_Y0 + 1, CYAN, 2.4, lit=0.2)
    elif f < 9:                                                  # cau, cada cop més de pressa
        t = ((f - 3) / 5) ** 2
        y = round(DRIP_Y0 + fall * t)
        cv.put(DRIP_X, y, CYAN, 3.8, lit=0.2)
        cv.put(DRIP_X, y - 1, CYAN, 2.6, lit=0.2)
        if f > 5:
            cv.put(DRIP_X, y - 2, CYAN, 1.8, lit=0.2)             # el rastre
    elif f < 14:                                                 # toca el bassal: esquitx i onades
        k = f - 9
        if k < 2:
            for dx, dy in ((-2, -2 - k), (2, -2 - k), (0, -3 - k)):
                cv.put(bx + dx, by + dy - 2, CYAN, 3.6 - k, lit=0.2)
        rx, ry = 3 + k * 2.6, 0.8 + k * 0.5
        for a in range(0, 360, 12):
            import math as _m
            cv.put(round(bx + _m.cos(_m.radians(a)) * rx), round(by + _m.sin(_m.radians(a)) * ry), CYAN, 3.2 - k * 0.5, lit=0.3)


def _gota_frames(n=18):
    """Una gota cada 1,8 s: s'infla al broc, cau, esquitxa i fa onades; després, quieta."""
    frames = []
    for f in range(n):
        pc = Canvas(light=LIGHT, transparent=True)
        aixeta(pc, f)
        frames.append(pc.img)
    return frames


def tassa(cv):
    """4t revolt: una tassa de llauna amb un dit de cafè, a terra."""
    x0, y0, x1, y1 = R(122, 123, 134, 132)
    cx = (x0 + x1) // 2
    top, bot = y0 + 3, y1 - 1
    for y in range(top, bot + 1):
        for x in range(cx - 7, cx + 8):
            s = (x - cx) / 7
            cv.put(x, y, GRAY, 3.4 - s * 1.6 - (0.6 if y == bot else 0), lit=0.6)
    cv.disc(cx, top, 7, 2, GRAY, 4.2, lit=0.4)
    cv.disc(cx, top, 6, 1.4, WALNUT, 1.2, lit=0.3)                       # el cafè
    cv.ring(cx + 9, (top + bot) // 2, 3.6, GRAY, 2.6, lit=0.5, step=10)   # la nansa
    cv.hline(cx - 8, cx + 10, bot + 1, IRON, 0.1)
    for x in range(cx - 7, cx + 8, 4):
        cv.put(x, top + 4 + (x % 3), RUST, 2.4, lit=0.4)                  # l'esmalt saltat


def formulari(cv):
    """5è revolt: un formulari 27-B clavat a la paret del fons, amb el segell vermell de DENEGAT."""
    x0, y0, x1, y1 = R(200, 50, 220, 74)
    cv.rect(x0, y0, x1, y1, PAPER, lambda x, y: 3.8 - (y - y0) * 0.02 - (0.4 if x == x1 else 0), lit=0.5)
    cv.disc((x0 + x1) // 2, y0 + 2, 1.5, 1.5, IRON, 1.0, lit=0.2)       # el clau
    text(cv, x0 + 3, y0 + 5, '27-B', IRON, 1.0, lit=0.2, small=True)
    for y in range(y0 + 13, y1 - 3, 3):
        cv.hline(x0 + 3, x1 - 4 - (y % 7), y, PAPER, 1.6, lit=0.3)
    sx, sy = x0 + 5, y1 - 14
    cv.rect(sx, sy, x1 - 3, sy + 8, RED, lambda x, y: 3.2 if x in (sx, x1 - 3) or y in (sy, sy + 8) else -9, lit=0.2)
    text(cv, sx + 2, sy + 2, 'NO', RED, 3.4, lit=0.2, small=True)
    cv.darken(x1 + 1, y0 + 2, x1 + 2, y1 + 1, 0.6)                        # l'ombra del paper


# ─── Animacions ────────────────────────────────────────────────────────────
# De fons: la làmpada es gronxa amb el corrent d'aire del conducte i parpelleja (sobretot una caiguda de tensió a
# mig cicle), la llum que fa a les parets la segueix, la pols sura dins el con de llum i la llumeta del fons del
# passadís de dret batega. Cada fotograma porta només el que canvia respecte del fons quiet.
# La gota de l'aixeta és l'animació del prop `aixeta` (3r revolt), amb el mateix nom: substitueix el dibuix quiet.

N_AMBIENT = 32


def _flicker(t):
    """Intensitat de la làmpada a t (0..1): un batec suau i, a mig cicle, dues caigudes de tensió."""
    p = 1.0 + 0.05 * math.sin(2 * math.pi * t * 3)
    for c, w, d in ((0.47, 0.025, 0.55), (0.56, 0.02, 0.35)):
        if abs(t - c) < w:
            p -= d
    return p


def frame_diff(base, img):
    """Imatge transparent amb només els píxels d'`img` que no són iguals a `base`."""
    from PIL import Image, ImageChops
    d = ImageChops.difference(base.convert('RGB'), img.convert('RGB')).convert('L').point(lambda v: 255 if v else 0)
    out = Image.new('RGBA', img.size, (0, 0, 0, 0))
    out.paste(img, (0, 0), d)
    return out


def _ambient_frames(n=N_AMBIENT):
    sense = Canvas(light=LIGHT)
    bg(sense, lamp=False)
    base = sense.img.copy()
    _lamp(Canvas(light=LIGHT, img=base))
    rnd = [(hr(i, 1, 41), hr(i, 2, 41), hr(i, 3, 41)) for i in range(14)]     # la pols: x, y, fase
    frames = []
    for i in range(n):
        t = i / n
        swing = 2.2 * math.sin(2 * math.pi * t)
        power = _flicker(t)
        cv = Canvas(light=LIGHT, img=sense.img.copy())
        # la llum a les parets i al sostre segueix la làmpada (només a prop: més lluny no es nota)
        lx = LAMP[0] + swing
        k = power - 1.0
        if abs(k) > 0.01 or abs(swing) > 0.3:
            def amt(x, y, lx=lx, k=k):
                d = math.hypot(x - lx, (y - LAMP[1]) * 1.3) / 150
                return max(0.0, 1 - d) ** 2 * k
            for y in range(0, 150):
                for x in range(round(lx) - 150, round(lx) + 151):
                    a = amt(x, y)
                    if a < -0.02 and -a > B4[y & 3][x & 3] * 0.6:
                        o = cv.P[x, y]
                        cv.P[x, y] = tuple(int(c * 0.78) for c in o[:3]) + (255,)
                    elif a > 0.02 and a > B4[y & 3][x & 3] * 0.6:
                        o = cv.P[x, y]
                        cv.P[x, y] = tuple(min(255, int(c * 1.12) + 2) for c in o[:3]) + (255,)
        _lamp(cv, swing, power)
        # la pols que sura dins el con de llum
        for px, py, ph in rnd:
            y = 50 + ((py + t * (0.25 + ph * 0.2)) % 1) * 110
            x = LAMP[0] - 60 + px * 120 + 4 * math.sin(2 * math.pi * (t + ph))
            if abs(x - lx) < (y - 30) * 0.6:
                cv.put(round(x), round(y), WARN, 2.6 + power, lit=0)
        # la llumeta del fons del passadís de dret
        x0, y0, x1, y1 = STRAIGHT
        cv.glow((x0 + x1) / 2, y0 + (y1 - y0) * 0.55, 10, (150, 110, 70), 0.2 * (1 + math.sin(2 * math.pi * t * 2)))
        frames.append(frame_diff(base, cv.img))
    return frames


ANIMS = {
    'ambient': {'frames': _ambient_frames, 'frameDuration': 110},
    'aixeta': {'frames': _gota_frames, 'frameDuration': 100},
}

PROPS = {'cartell': cartell, 'guant': guant, 'aixeta': aixeta, 'tassa': tassa, 'formulari': formulari}
