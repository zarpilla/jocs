"""
Prova de resolució: la caixa de cadenes de l'Arenga a 640×360 (la composició de hd/rooms/caixa_cadenes.py ×4/3,
dibuixada de nou amb el detall que hi cap). Mateixes rampes, mateix prop i mateixes animacions.

Escena 6, onze de la nit: fosca, estreta i rovellada. El buc es tanca cap a baix, la cadena de l'àncora baixa pel
tub de l'escobén i s'apila a l'esquerra; l'escotilla, oberta a dalt, deixa entrar la llum groga de coberta.
Prop: `manta` (la manta, el paper de l'entrepà i el rotllo de cap on seu la Juana).
Animacions: `pols` (motes al con de llum de l'escotilla) i `gota` (es forma al sostre, cau al bassal i hi fa rodones).
"""
import math

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from hd.pix import Canvas, Light, W, H, hr, mix, B4, RUST, PAPER
from hd.rooms.arenga import CAB, DARK, REDP, box, bolt, vpipe, glow
from hd.rooms.comu import _diff
from hd640.rooms.pallol_pla_comu import FLOOR_Y, BOTTOM, rust_streaks, floor_shadow

# Art a 2× (1280×720 per a una sala de 640×360): el mateix dibuix, amb les formes, el dither i la llum a la
# resolució real (hd1280/canvas2x.py); el motor el mostra a 1/2 (artScale al .room.json).
ART_SCALE = 2
from hd1280.canvas2x import Canvas2x as Canvas  # noqa: E402,F811
from hd.pix import Canvas as Canvas1x  # noqa: E402,F401  (llenços auxiliars en píxels de sala: figures, textos)

HX0, HX1 = 283, 357          # l'escotilla
FLOOR_END = BOTTOM + 15

LIGHT = Light(ambient=-0.9, vignette=(93, 27), floor_fade=None)
LIGHT.point(320, 32, r=267, k=2.9, squash=0.75, power=1.6)        # la llum de coberta, per l'escotilla
LIGHT.add(lambda x, y: 0.9 * max(0.0, 1 - abs(x - 320 - (y - 40) * 0.25) / (32 + y * 0.45))
          if 32 < y < 267 else 0.0)                                # el con de llum que baixa

# planxa nua: imprimació d'òxid vermell, rovellada
HULL = [(6, 4, 4), (12, 8, 7), (20, 12, 10), (30, 18, 14), (42, 26, 18), (56, 34, 22), (72, 44, 28),
        (92, 58, 36), (116, 76, 48), (142, 98, 64)]
CHAIN = [(8, 7, 7), (16, 13, 12), (28, 22, 18), (42, 32, 24), (60, 44, 30), (82, 58, 38), (108, 76, 50),
         (140, 104, 72)]
MUD = [(6, 6, 5), (12, 11, 9), (20, 18, 14), (30, 27, 20), (42, 38, 28), (56, 50, 36)]
WOOL = [(14, 14, 16), (26, 26, 30), (42, 42, 46), (62, 60, 62), (84, 82, 80), (108, 104, 98), (136, 130, 120)]
WOOD = [(10, 8, 6), (20, 15, 11), (34, 26, 18), (50, 38, 26), (68, 52, 34), (88, 68, 46), (110, 86, 58)]
NIGHT = [(2, 3, 8), (4, 6, 14), (8, 10, 22), (12, 16, 32), (20, 24, 44)]


def _sides(y):
    """Les vores del buc a l'alçada y: es tanquen cap a baix (la proa)."""
    yy = min(y, BOTTOM)
    return 53 + (yy / FLOOR_Y) * 37, W - 59 - (yy / FLOOR_Y) * 40


# ─── Parets ─────────────────────────────────────────────────────────────────

def walls(cv):
    # el mamparo de col·lisió (al fons): planxa amb reforços verticals
    for y in range(0, FLOOR_Y):
        for x in range(W):
            lv = 3.2 + (hr(x // 3, y // 4, 41) - 0.5) * 0.5
            if hr(x // 9, y // 12, 42) > 0.82:
                lv += 0.5                                               # taques de rovell més clares
            if hr(x // 2, y // 2, 44) > 0.97:
                lv -= 0.8                                               # picat de l'òxid
            cv.put(x, y, HULL, lv)
    for sx in range(128, 533, 69):                                      # reforços, amb els reblons
        for x in range(sx, sx + 7):
            d = x - sx
            for y in range(0, FLOOR_Y):
                cv.put(x, y, HULL, 3.6 + (1.0 if d == 0 else 0.4 if d == 1 else -0.6 if d >= 4 else 0))
        for y in range(24, FLOOR_Y - 8, 14):
            bolt(cv, sx + 3, y, HULL, 4.0)
        cv.darken(sx + 7, 0, sx + 10, FLOOR_Y, lambda xx, yy, sx=sx: 0.5 - (xx - sx - 7) * 0.15)
    for sy in (64, 139):                                                # soldadures, amb el cordó
        for x in range(W):
            cv.put(x, sy, HULL, 1.8)
            cv.put(x, sy + 1, HULL, 4.0 if (x // 2) % 2 else 3.5)
    rust_streaks(cv, 0, 13, W - 1, FLOOR_Y, 40, k=0.35, seed=43, ramp=RUST)
    # els costats del buc, amb quadernes corbes, més foscos
    for y in range(0, FLOOR_END):
        lx, rx = _sides(y)
        for x in range(W):
            rib = 0.9 if int(y / 29) != int((y + 1) / 29) else 0
            if x < lx:
                cv.put(x, y, HULL, 1.6 + x / lx * 1.4 + rib)
            elif x > rx:
                cv.put(x, y, HULL, 1.3 + (W - 1 - x) / (W - 1 - rx) * 1.2 + rib)
    for y in range(0, FLOOR_END):
        lx, rx = _sides(y)
        cv.put(lx, y, HULL, 4.4)
        cv.put(lx + 1, y, HULL, 3.0)
        cv.put(lx + 2, y, HULL, 1.4)
        cv.put(rx, y, HULL, 3.8)
        cv.put(rx - 1, y, HULL, 1.4)
    # el sostre (la coberta per sota), baix, amb baos
    cv.rect(0, 0, W - 1, 16, DARK, 2.2)
    for bx in range(13, W, 69):
        box(cv, bx, 0, bx + 11, 19, HULL, 2.6, grad=0.6)
        cv.hline(bx + 1, bx + 10, 19, HULL, 1.2)


def hatch(cv):
    """L'escotilla, oberta: la nit, el pal de proa amb un llum groc, la brazola i la tapa."""
    x0, x1 = HX0, HX1
    for y in range(0, 27):
        for x in range(x0, x1 + 1):
            cv.put(x, y, NIGHT, 2.2 + y * 0.045 + (hr(x // 7, y // 4) - 0.5) * 0.4, lit=0)
    for x in range(x0, x1 + 1):                                         # un núvol clar
        yy = 8 + math.sin(x * 0.09) * 3
        cv.put(x, int(yy), NIGHT, 4.0, lit=0)
        if hr(x, 3) > 0.5:
            cv.put(x, int(yy) + 1, NIGHT, 3.4, lit=0)
    for sx, sy in ((294, 4), (303, 15), (348, 3)):                      # estrelles
        cv.flat(sx, sy, (150, 160, 190))
    cv.vline(330, 0, 22, NIGHT, 1.0, lit=0)                             # el pal de proa, a contrallum
    cv.vline(331, 0, 22, NIGHT, 0.6, lit=0)
    cv.disc(336, 11, 4, 3, [(160, 120, 40), (255, 210, 110), (255, 246, 200)], 2.0, lit=0)
    glow(cv, 336, 11, 21, (255, 200, 90), 0.8)
    # la brazola, amb cargols i la junta de goma
    box(cv, x0 - 8, 21, x1 + 8, 32, CAB, 3.4)
    cv.hline(x0 - 7, x1 + 7, 22, DARK, 1.0)
    for bx in range(x0 - 5, x1 + 6, 8):
        bolt(cv, bx, 27, CAB, 3.6)
    # la tapa, oberta enlaire (de cantó), amb la frontissa
    cv.poly([(x0 - 8, 21), (x0 - 3, 0), (x0 + 3, 0), (x0 - 3, 21)], CAB, 3.0)
    cv.line(x0 - 3, 0, x0 - 3, 21, CAB, 4.2)
    box(cv, x0 - 10, 18, x0 - 4, 23, CAB, 3.8)
    # els graons soldats al mamparo, de l'escotilla a terra
    for y in range(43, FLOOR_Y - 5, 15):
        box(cv, 307, y, 333, y + 3, CAB, 3.8)
        cv.hline(308, 332, y + 1, CAB, 4.6)
        for lx in (307, 333):
            cv.vline(lx, y + 4, y + 7, CAB, 2.0)
            cv.put(lx, y + 8, RUST, 3.0)
        cv.darken(308, y + 4, 332, y + 5, 0.4)
        rust_streaks(cv, 309, y + 4, 331, y + 13, 4, k=0.5, seed=y)


def haze(cv):
    """El con de llum de l'escotilla (pols a l'aire)."""
    for y in range(32, BOTTOM + 11):
        for x in range(W):
            c = 1 - abs(x - 320 - (y - 40) * 0.25) / (32 + y * 0.45)
            if c > 0:
                k = 0.16 * c * (1 - y / 347)
                if k > B4[y & 3][x & 3] * 0.35:
                    cv.flat(x, y, mix(cv.get(x, y), (255, 214, 130), k))
    for i in range(55):                                                 # motes de pols
        y = 40 + hr(i, 1) * 200
        x = 320 + (y - 40) * 0.25 + (hr(i, 2) - 0.5) * (32 + y * 0.45) * 1.6
        if 0 <= x < W:
            cv.flat(int(x), int(y), mix(cv.get(int(x), int(y)), (255, 230, 170), 0.5))


# ─── La cadena ──────────────────────────────────────────────────────────────

def link(cv, x, y, flat, lvl=3.2):
    """Una baula de cadena amb travesser: de cara (anella oval gruixuda, amb el pal) o de cantó (barra)."""
    if flat:
        for a in range(0, 360, 6):
            ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
            for r in (0, 1, 2):
                px = x + round(ca * (8 - r))
                py = y + round(sa * (5 - r * 0.8))
                cv.put(px, py, CHAIN, lvl + 0.8 - sa * 1.2 - ca * 0.5 - r * 0.6)
        cv.vline(x, y - 3, y + 3, CHAIN, lvl + 0.2)
        cv.put(x, y - 3, CHAIN, lvl + 1.4)
        cv.put(x - 1, y, CHAIN, lvl - 0.6)
    else:
        cv.rect(x - 8, y - 1, x + 8, y + 1, CHAIN, lvl)
        cv.hline(x - 7, x + 7, y - 2, CHAIN, lvl + 1.5)
        cv.hline(x - 7, x + 7, y + 2, CHAIN, lvl - 1.2)
        cv.put(x - 8, y, CHAIN, lvl - 0.6)
        cv.put(x + 8, y, CHAIN, lvl - 0.6)
        cv.put(x - 3, y - 2, CHAIN, lvl + 2.4)                          # una llum de fregament


def chain(cv):
    # el tub de l'escobén, que baixa del sostre, amb la brida
    vpipe(cv, 157, 0, 40, 12, HULL, 3.4)
    box(cv, 142, 14, 172, 18, HULL, 3.8)
    for bx in (145, 157, 169):
        cv.put(bx, 16, HULL, 5.0)
    cv.disc(157, 41, 13, 4, HULL, lambda nx, ny: 3.8 - ny)
    cv.disc(157, 41, 9, 3, DARK, 0.6)
    # la cadena que en penja (baules alternes, de cara i de cantó)
    for i, y in enumerate(range(48, 133, 9)):
        if i % 2 == 0:
            for a in range(0, 360, 8):
                ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
                for r in (0, 1, 2):
                    cv.put(157 + round(ca * (5 - r)), y + round(sa * (7 - r)), CHAIN, 4.2 - ca * 1.0 - r * 0.7)
            cv.hline(155, 159, y, CHAIN, 3.4)                           # el travesser
        else:
            cv.rect(155, y - 7, 159, y + 7, CHAIN, 3.4)
            cv.vline(155, y - 7, y + 7, CHAIN, 4.8)
            cv.vline(159, y - 7, y + 7, CHAIN, 2.2)
    # la pila: primer l'ombra del munt, després les baules, de les de sota (fosques) a les de dalt
    mound = [(69, 243)] + [(157 + u * 88, 240 - (1 - abs(u) ** 1.6) * 117) for u in [i / 20 - 1 for i in range(41)]] \
        + [(248, 243)]
    cv.poly(mound, CHAIN, 0.8)
    pts = []
    for i in range(520):
        u = hr(i, 1) * 2 - 1
        h = (1 - abs(u) ** 1.6) * 115
        x = 157 + u * 83
        y = 240 - hr(i, 2) ** 0.8 * h
        pts.append((y, x, i))
    pts.sort()
    for y, x, i in pts:
        depth = (240 - y) / 120
        link(cv, int(x), int(y), hr(i, 3) > 0.45, lvl=2.6 + depth * 1.6 + (hr(i, 4) - 0.5) * 0.8)
    # baules soltes que baixen per davant de la pila
    for k, (x, y) in enumerate(((229, 237), (243, 243), (221, 247))):
        link(cv, x, y, k % 2 == 0, lvl=3.4)


# ─── Terra ──────────────────────────────────────────────────────────────────

PUDDLE_C, PUDDLE_R = (243, 253), (43, 8)


def in_puddle(x, y):
    return ((x - PUDDLE_C[0]) / PUDDLE_R[0]) ** 2 + ((y - PUDDLE_C[1]) / PUDDLE_R[1]) ** 2 <= 1


def floor(cv):
    """El fons de la caixa: una reixa de fusta damunt del fang i l'aigua que s'hi escola."""
    for y in range(FLOOR_Y, FLOOR_END):
        lx, rx = _sides(y)
        for x in range(int(lx) + 1, int(rx)):
            cv.put(x, y, MUD, 2.4 + (hr(x // 3, y // 2, 51) - 0.5) * 0.8)
    vp = (320, 53)                                                      # llistons de la reixa (en perspectiva)
    for y in range(FLOOR_Y + 3, FLOOR_END):
        d = y - vp[1]
        lx, rx = _sides(y)
        for x in range(int(lx) + 3, int(rx) - 1):
            u = vp[0] + (x - vp[0]) * 200 / d
            if (u % 29) < 20:
                lv = 2.6 + (hr(int(u // 29), y // 5) - 0.5) * 0.6 - (0.7 if (u % 29) > 17.5 else 0)
                if (u % 29) < 1.5:
                    lv += 0.7                                           # la vora il·luminada del llistó
                if hr(int(u // 29), y // 3, 52) > 0.93:
                    lv -= 0.9                                           # un nus de la fusta
                cv.put(x, y, WOOD, lv)
    # un bassal amb el reflex de l'escotilla
    for y in range(PUDDLE_C[1] - PUDDLE_R[1], PUDDLE_C[1] + PUDDLE_R[1] + 1):
        for x in range(PUDDLE_C[0] - PUDDLE_R[0], PUDDLE_C[0] + PUDDLE_R[0] + 1):
            if in_puddle(x, y):
                cv.flat(x, y, mix(cv.get(x, y), (12, 14, 18), 0.6))
                if hr(x // 3, y) > 0.9:
                    cv.flat(x, y, mix(cv.get(x, y), (180, 150, 90), 0.35))


# ─── La manta (prop) ────────────────────────────────────────────────────────
# Hi va també el seient de la Juana: un rotllo de cap d'amarrar vell, gruixut, amb la manta als peus.

ROPE = [(10, 8, 6), (22, 17, 11), (38, 30, 19), (58, 46, 29), (80, 64, 40), (104, 86, 56), (130, 110, 74)]


def hawser(cv):
    """Un rotllo de cap d'amarrar, gruixut i vell, en perspectiva: el seient de la Juana (Escena 6)."""
    cx, base, top = 400, 237, 203
    floor_shadow(cv, cx, base + 1, 32, 5, 0.8)
    n = (base - top) // 4
    for k in range(n + 1):
        cy = base - k * 4
        rx, ry = 25 - k * 0.2, 6.7
        for a in range(0, 360, 1):
            sa = math.sin(math.radians(a))
            x = cx + math.cos(math.radians(a)) * rx
            y = cy + sa * ry
            if sa < -0.2 and k < n:                                     # la part de darrere la tapa la volta de dalt
                continue
            for t in range(4):
                cv.put(x, y - t, ROPE, (3.6 if sa > -0.2 else 2.4) + (0.8 if t == 3 else 0.3 if t == 2 else 0)
                       - (0.6 if (a // 6 + k + t // 2) % 2 else 0))
    cv.disc(cx, top, 13, 3.3, DARK, 1.0)                                # el forat del mig, a dalt
    for i in range(6):                                                  # fils trencats
        a = math.radians(30 + i * 52)
        cv.put(round(cx + math.cos(a) * 22), round(top + 6 + math.sin(a) * 4), ROPE, 4.6)


def blanket(cv):
    """La manta, plegada de qualsevol manera a terra, i el paper d'alumini de l'entrepà, rebregat."""
    floor_shadow(cv, 400, 245, 56, 5, 0.8)
    hawser(cv)
    body = [(349, 243), (365, 229), (400, 227), (440, 229), (456, 240), (448, 249), (400, 251), (357, 251)]
    cv.poly(body, WOOL, lambda x, y: 3.4 - (y - 227) * 0.03 + math.sin(x * 0.19 + y * 0.45) * 0.5)
    cv.line(365, 229, 440, 229, WOOL, 4.6)
    cv.line(366, 230, 439, 230, WOOL, 3.8)
    for x in range(355, 452):                                           # les ratlles de la manta
        for yy in (235, 236, 238):
            cv.put(x, yy + int(math.sin(x * 0.11) * 2), REDP, 2.8 if yy != 238 else 2.0)
    for x in range(357, 449, 3):                                        # serrell
        cv.put(x, 252, WOOL, 3.0)
        cv.put(x, 253, WOOL, 2.2)
    for x in range(372, 412):                                           # un plec
        cv.put(x, 244 + int(math.sin(x * 0.2)), WOOL, 1.8)
    # el paper de l'entrepà, una bola rebregada a terra
    FOIL = [(40, 40, 44), (90, 90, 96), (150, 150, 156), (200, 200, 206), (236, 236, 240)]
    cv.disc(461, 248, 7, 4, FOIL, lambda nx, ny: 2.8 - nx - ny + (hr(int(nx * 5), int(ny * 5)) - 0.5) * 1.6)
    for px, py in ((458, 246), (462, 247), (464, 250)):
        cv.put(px, py, FOIL, 4.8)
    cv.put(469, 252, PAPER, 4.0)                                        # una molla de pa
    cv.put(472, 251, PAPER, 3.2)


# ─── Muntatge ───────────────────────────────────────────────────────────────

def bg(cv):
    walls(cv)
    hatch(cv)
    floor(cv)
    chain(cv)
    haze(cv)
    glow(cv, 320, 29, 53, (255, 200, 110), 0.35)


PROPS = {'manta': blanket}


# ─── Animacions ─────────────────────────────────────────────────────────────

def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv


def _cone(y):
    """Centre i mitja amplada del con de llum de l'escotilla a l'alçada y."""
    return 320 + (y - 40) * 0.25, 32 + y * 0.45


def _frames_pols():
    """Pols que sura al con de llum (cada mota fa un llaç tancat: el bucle no salta)."""
    base = _base()
    motes = []
    for k in range(45):
        y = 45 + hr(k, 11) * 187
        cx, hw = _cone(y)
        motes.append((cx + (hr(k, 12) - 0.5) * hw * 1.4, y, 5 + hr(k, 13) * 11, 4 + hr(k, 14) * 9,
                      hr(k, 15), 1 + int(hr(k, 16) * 2)))
    n = 48
    frames = []
    for i in range(n):
        cv = Canvas(light=LIGHT, img=base.img.copy())
        t = i / n
        for (cx, cy, ax, ay, ph, fx) in motes:
            a = 2 * math.pi * (t + ph)
            x = round(cx + ax * math.sin(fx * a))
            y = round(cy + ay * math.sin(a + ph * 3))
            ccx, hw = _cone(y)
            inside = max(0.0, 1 - abs(x - ccx) / hw)                   # només es veu dins la llum
            tw = 0.5 + 0.5 * math.sin(a * 2 + ph * 7)                  # i fa pampallugues
            alpha = inside ** 0.7 * (0.35 + 0.45 * tw) * (1 - y / 347)
            if alpha > 0.08 and 0 <= x < W and 19 <= y < BOTTOM:
                cv.flat(x, y, mix(cv.get(x, y), (255, 232, 180), alpha))
        frames.append(_diff(cv.img, base.img))
    return frames


DRIP = (243, 20)       # on es forma la gota (sota el bao), just damunt del bassal
PUDDLE = PUDDLE_C
WATER = (196, 178, 132)
SPARK = (240, 226, 190)


def _frames_gota():
    """Una gota: es forma al sostre, cau, esquitxa al bassal i en surten dues rodones que s'esvaeixen."""
    base = _base()
    dx, dy = DRIP
    px, py = PUDDLE
    n = 40
    frames = []
    for i in range(n):
        cv = Canvas(light=LIGHT, img=base.img.copy())
        if i < 16:                                                      # la gota s'infla
            g = i / 15
            cv.flat(dx, dy, mix(cv.get(dx, dy), WATER, 0.4 + 0.4 * g))
            if g > 0.3:
                cv.flat(dx, dy + 1, mix(cv.get(dx, dy + 1), WATER, 0.3 + 0.6 * g))
            if g > 0.6:
                cv.flat(dx - 1, dy + 1, mix(cv.get(dx - 1, dy + 1), WATER, 0.4 * g))
                cv.flat(dx, dy + 2, mix(cv.get(dx, dy + 2), WATER, 0.5 * g))
            if g > 0.85:
                cv.flat(dx, dy + 3, mix(cv.get(dx, dy + 3), SPARK, 0.8))
        elif i < 22:                                                    # cau, cada cop més de pressa
            k = (i - 15) / 6
            y = round(dy + 3 + (py - 5 - dy - 3) * k * k)
            tail = 1 + int(k * 5)
            for j in range(tail):
                cv.flat(dx, y - j, mix(cv.get(dx, y - j), SPARK, 0.85 - j * 0.13))
        else:                                                           # l'esquitx i les rodones
            k = i - 22
            if k < 4:
                for sx, sy in ((-2, -3 - k), (2, -3 - k), (0, -4 - k), (-3, -1 - k // 2), (3, -1 - k // 2)):
                    x, y = px + sx * (1 + k // 2), py + sy
                    cv.flat(x, y, mix(cv.get(x, y), SPARK, 0.7 - k * 0.15))
            for r0 in (0, 5):
                r = (k - r0) * 1.9
                if 1 <= r <= 20:
                    fade = 1 - r / 21
                    for a in range(0, 360, 4):
                        x = round(px + math.cos(math.radians(a)) * r * 1.8)
                        y = round(py + math.sin(math.radians(a)) * r * 0.42)
                        if in_puddle(x, y) and hr(x, y, k) < 0.4 + fade * 0.6:
                            cv.flat(x, y, mix(cv.get(x, y), (200, 168, 104), 0.25 + 0.4 * fade))
        frames.append(_diff(cv.img, base.img))
    return frames


ANIMS = {'pols': {'frames': _frames_pols, 'frameDuration': 130},
         'gota': {'frames': _frames_gota, 'frameDuration': 80}}

GEOMETRIA = {
    'things': {
        'escotilla': {'rect': (272, 0, 368, 200), 'walk': (320, 224)},
        'cadenes': {'rect': (64, 0, 248, 243), 'walk': (261, 248)},
        'manta': {'rect': (347, 224, 475, 253), 'walk': (333, 256)},
    },
    'spawns': {'iri': (309, 253), 'vet': (261, 259), 'juana': (403, 243)},
    'walkable': [(251, 219), (536, 219), (557, 263), (219, 263), (243, 245)],
}
