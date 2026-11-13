"""
Aigua Verne — `verdant_jardi` (L, de lluny: persones de ≈83 px). Escena 5.

El jardí de la residència d'estiu del Magnat, a Verdant: el planeta dels rics, on tot és de plàstic. Cel blau
d'anunci amb núvols massa rodons, turons d'un verd impossible amb arbres de piruleta i viles blanques; la
**gespa artificial** perfecta, segada a franges; el parterre de **flors de plàstic** de colors que no existeixen; els
**aspersors**, que no reguen: fan boira de perfum. La **façana blanca** de la residència, amb columnes i or i la
porta de vidre (en Fidel s'hi posa al davant: és un sprite a part). Al costat, el **climatitzador**, que degota a
una **reixa** a terra (l'única aigua de veritat del jardí, i la llencen). A la dreta, el **cobert del jardiner**:
fusta pintada de verd, vella, humana. A l'esquerra, la **Cantimplora** (nau cisterna vella) amb la rampa abaixada, i
la **plataforma de la llançadora** dels jardiners. El **panell del preu** (64 ▲), polit, com tot aquí.

Decorat: `galleda_reixa` (la galleda d'en Nil sota el degoteig). ANIMS: `boira` (els aspersors), `degoteig`.
"""
import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

import math

from hd.pix import Canvas, Light, W, H, hr, mix
from hd.rooms.arenga import box
from hd.rooms.comu import _diff, text
from hd.rooms.exterior import fbm
from hd640.rooms.verdant_comu import (SKYV, CLOUDV, TURF, HILLV, WHITEV, MARBLE, GOLDV, GLASSV, FLOWERS, MAGENTA,
                                      CYANF, YELLOWF, VIOLETF, ORANGEF, PLANK, WOODG, SHEDG, ZINC, BLACKT, OLIVE, SAFETY,
                                      RUSTV, gota, panell_preu, flor, arbre_rodo, bola_boix, ombra, rotul, galleda)

RH = 260                    # la sala (per sota, la barra de verbs)
HOR = 140                   # l'horitzó (darrere els turons)
LAWN_Y = 180                # on comença la gespa (la base de la bardissa del fons)
SUN = (150, 20)

LIGHT = Light(ambient=0.9, vignette=None, floor_fade=None)
LIGHT.point(SUN[0], SUN[1] - 60, r=760, k=1.3, power=1.2)            # el sol, a dalt a l'esquerra

# la residència
RX0, RX1, RBASE = 240, 464, 198
DOOR = (334, 100, 370, 196)
# el cobert
SX0, SX1, SBASE, SAPEX = 506, 634, 204, (570, 94)
SDOOR = (550, 116, 590, 204)
# el climatitzador i la reixa
AC = (470, 146, 496, 178)
GRATE = (466, 203, 498, 210)
DRIP = (484, 195)            # on surt la gota del tub
# el parterre gran i els aspersors
BED = (196, 232, 80, 16)
SPRINK = ((524, 238), (608, 228))


# ─── Cel, turons i bardissa ────────────────────────────────────────────────

def nuvol(cv, cx, cy, s):
    """Un núvol de catàleg: boles perfectes, base plana, ombra blava a sota."""
    balls = ((-18, 2, 10), (-6, -6, 13), (9, -3, 11), (21, 3, 8), (2, 4, 10))
    for dx, dy, r in balls:
        r *= s
        cv.disc(cx + dx * s, cy + dy * s, r, r * 0.86, CLOUDV,
                lambda nx, ny: 4.4 - ny * 1.6 - nx * 0.6 + (0.8 if ny < -0.55 else 0), lit=0)
    cv.rect(cx - 26 * s, cy + 6 * s, cx + 28 * s, cy + 9 * s, CLOUDV, 2.4, lit=0)


def sky(cv):
    for y in range(0, HOR + 1):
        t = y / HOR
        for x in range(W):
            d = math.hypot(x - SUN[0], (y - SUN[1]) * 1.2)
            lvl = 1.2 + 5.6 * t ** 1.3 + 2.6 * max(0.0, 1 - d / 120) ** 2
            cv.put(x, y, SKYV, lvl, lit=0)
    nuvol(cv, 238, 26, 1.0)
    nuvol(cv, 540, 40, 1.25)
    nuvol(cv, 420, 14, 0.7)
    # el sol, amb els raigs d'anunci (massa perfectes)
    cv.glow(SUN[0], SUN[1], 44, (255, 255, 236), 0.9)
    for k in range(12):
        a = k * math.pi / 6 + 0.13
        for r in range(12, 28 if k % 2 else 22):
            if r % 2 == 0:
                cv.flat(SUN[0] + math.cos(a) * r, SUN[1] + math.sin(a) * r, (255, 252, 214))
    cv.disc(SUN[0], SUN[1], 8, 8, [(255, 236, 140), (255, 248, 190), (255, 255, 236), (255, 255, 255)],
            lambda nx, ny: 3.4 - nx * 0.6 - ny * 0.6, lit=0)


def hills(cv):
    """Turons de gespa perfecta (corbes de sinus, ni un roc), arbres de piruleta i viles blanques amb piscina."""
    for x in range(W):
        h1 = HOR - 22 + 9 * math.sin(x / 70 + 0.6) + 4 * math.sin(x / 31)
        h2 = HOR - 6 + 6 * math.sin(x / 46 + 2.1)
        for y in range(int(h1), LAWN_Y):
            cv.put(x, y, HILLV, 4.2 - (y - h1) * 0.035 + (0.9 if y - h1 < 1.5 else 0), lit=0)
        for y in range(int(h2), LAWN_Y):
            cv.put(x, y, HILLV, 3.0 - (y - h2) * 0.02 + (1.0 if y - h2 < 1.5 else 0) +
                   (0.4 if (x // 6 + int(y)) % 2 else 0) * (y > h2 + 4), lit=0)
    # viles blanques llunyanes, amb la piscina blava al davant
    for vx in (120, 214, 476):
        vy = int(HOR - 22 + 9 * math.sin(vx / 70 + 0.6) + 4 * math.sin(vx / 31)) + 3
        cv.rect(vx - 6, vy - 7, vx + 6, vy, WHITEV, lambda x, y: 5.4 if x < vx + 3 else 4.0, lit=0)
        cv.rect(vx - 3, vy - 11, vx + 3, vy - 8, WHITEV, 5.2, lit=0)
        cv.hline(vx - 7, vx + 7, vy - 7, GOLDV, 4.6, lit=0)
        cv.hline(vx - 4, vx + 4, vy - 11, GOLDV, 4.6, lit=0)
        for wx in range(vx - 4, vx + 5, 3):
            cv.flat(wx, vy - 4, GLASSV[2])
        cv.rect(vx - 9, vy + 1, vx + 2, vy + 2, CYANF, lambda x, y: 3.4 if y == vy + 1 else 2.4, lit=0)
        cv.flat(vx - 7, vy + 1, CYANF[4])
    for tx, tb, r in ((86, 136, 4), (140, 140, 5), (166, 134, 3), (228, 138, 4), (482, 134, 4), (496, 137, 3),
                      (636, 128, 4)):
        arbre_rodo(cv, tx, tb, r, lit=0)


def bardissa(cv, x0, x1):
    """Bardissa retallada amb regle: un prisma verd perfecte."""
    top = 158
    cv.rect(x0, top, x1, LAWN_Y, TURF, lambda x, y: 2.8 + (hr(x // 2, y // 2, 3) - 0.5) * 0.7 -
            (y - top) * 0.02 - (1.0 if y > LAWN_Y - 3 else 0))
    cv.rect(x0, top - 5, x1, top - 1, TURF, lambda x, y: 4.6 + (hr(x // 2, y, 4) - 0.5) * 0.6)
    cv.hline(x0, x1, top - 5, TURF, 6.0)


# ─── La gespa ──────────────────────────────────────────────────────────────

def gespa(cv):
    """Gespa artificial a franges de segar, en perspectiva, sense una mala herba."""
    vx, vy = 330, 120
    for y in range(LAWN_Y, RH):
        t = (y - LAWN_Y) / (RH - LAWN_Y)
        for x in range(W):
            ang = math.atan2(x - vx, y - vy)
            band = int(math.floor(ang * 9 + 50)) % 2
            lvl = 4.1 + (0.75 if band else -0.15) - t * 0.4
            if hr(x, y, 9) > 0.86:
                lvl += 0.9                                             # els brins de plàstic, que brillen
            elif hr(x, y, 10) > 0.9:
                lvl -= 0.7
            cv.put(x, y, TURF, lvl)


def cami(cv):
    """El camí de marbre blanc de la porta fins a baix, en lloses."""
    for y in range(206, RH):
        t = (y - 206) / (RH - 206)
        hw = 24 + 30 * t
        cx = 352 + 6 * t
        row = int((y - 206) ** 0.82 / 4)
        for x in range(int(cx - hw), int(cx + hw) + 1):
            u = (x - cx) / hw
            joint = (abs(((u + 1) * 3 + (0.5 if row % 2 else 0)) % 1) < 0.04 + 0.02 * t) or \
                (int((y - 205) ** 0.82 / 4) != int((y - 206) ** 0.82 / 4))
            lvl = 4.8 - (1.8 if joint else 0) + (fbm(x / 9, y / 4, 61) - 0.5) * 0.5
            cv.put(x, y, MARBLE, lvl)
        cv.put(cx - hw - 1, y, TURF, 1.4)
        cv.put(cx + hw + 1, y, TURF, 1.4)


# ─── La Cantimplora (la rampa) ─────────────────────────────────────────────

def cantimplora(cv):
    """El morro de la nau cisterna: planxa verd oliva reblonada, franges taronja, rovell; la rampa abaixada."""
    def edge(y):
        return 70 + 10 * math.sin(min(1.0, y / 170) * math.pi * 0.9)
    for y in range(0, 176):
        e = edge(y)
        for x in range(0, int(e) + 1):
            u = x / e
            lvl = 3.0 + u * 1.4 - (1.6 if x > e - 3 else 0) + (fbm(x / 12, y / 20, 71) - 0.5) * 0.9
            if y % 34 == 0 or x % 28 == 27:
                lvl -= 1.4                                             # juntes de les planxes
            if (y % 34 in (3, 30)) and x % 6 == 2:
                lvl += 1.6                                             # reblons
            if fbm(x / 6, y / 30, 73) > 0.66 and y % 34 > 6:
                cv.put(x, y, RUSTV, 2.6 + (hr(x, y) - 0.5))           # regalims de rovell
                continue
            cv.put(x, y, OLIVE, lvl)
    # la franja de seguretat, taronja i negra en diagonal
    for y in range(92, 102):
        for x in range(0, int(edge(y)) - 1):
            cv.put(x, y, SAFETY if ((x + y) // 5) % 2 else BLACKT, 3.0 if ((x + y) // 5) % 2 else 2.0)
    text(cv, 'C-7', 10, 40, None, 0, flat=(220, 210, 160))
    # la boca de la bodega, fosca amb llum càlida al fons
    cv.rect(8, 112, 66, 170, BLACKT, lambda x, y: 0.6 + max(0.0, 1 - abs(x - 37) / 30) * 1.4, lit=0)
    cv.glow(37, 150, 26, (255, 196, 110), 0.35)
    box(cv, 6, 110, 68, 112, OLIVE, 4.0)
    # la rampa: una planxa amb estries, de la boca fins a la gespa
    ramp = [(8, 170), (66, 170), (106, 230), (30, 234)]
    cv.poly(ramp, OLIVE, lambda x, y: 3.4 + (y - 170) * 0.012 + (1.2 if (y - 170) % 6 == 0 else 0) -
            (0.6 if (y - 170) % 6 == 1 else 0))
    for i in range(64):                                               # les vores de seguretat
        t = i / 63
        for k in (0, 1, 2):
            x1 = 66 + (106 - 66) * t - k
            y1 = 170 + 60 * t
            cv.put(x1, y1, SAFETY if (i // 4) % 2 else BLACKT, 3.0)
            x2 = 8 + (30 - 8) * t + k
            cv.put(x2, 170 + 64 * t, SAFETY if (i // 4) % 2 else BLACKT, 2.4)
    cv.line(30, 234, 106, 230, OLIVE, 1.4)
    cv.line(31, 235, 106, 231, OLIVE, 0.6)
    # el pistó hidràulic
    cv.line(74, 150, 90, 206, ZINC, 4.0)
    cv.line(75, 150, 91, 206, ZINC, 2.4)
    cv.line(73, 150, 80, 172, BLACKT, 2.4)


# ─── La plataforma de la llançadora ────────────────────────────────────────

def llancadora(cv):
    cx, cy = 142, 196
    ombra(cv, cx + 6, cy + 3, 44, 7, 0.6)
    cv.disc(cx, cy + 2, 42, 8, WHITEV, 2.4)                           # el gruix
    cv.disc(cx, cy, 42, 8, MARBLE, lambda nx, ny: 4.4 - nx * 0.6 - ny * 0.4)
    for a in range(0, 360, 2):                                        # l'anella daurada (el·lipse)
        ra = math.radians(a)
        cv.put(cx + math.cos(ra) * 36, cy + math.sin(ra) * 6.6, GOLDV, 4.6)
    for a in range(0, 360, 30):                                       # els llums d'aterratge
        ra = math.radians(a)
        cv.flat(cx + math.cos(ra) * 40, cy + math.sin(ra) * 7.3, CYANF[3])
    # la J pintada al mig, de «jardiners»
    for x, y in ((cx + 4, cy - 3), (cx + 4, cy - 2), (cx + 4, cy - 1), (cx + 4, cy), (cx + 3, cy + 1),
                 (cx + 2, cy + 1), (cx + 1, cy + 1), (cx, cy)):
        cv.flat(x, y, (40, 150, 70))
        cv.flat(x + 1, y, (40, 150, 70))
    # el pal amb el rètol i l'horari
    px = 114
    cv.rect(px - 1, 132, px + 1, 192, ZINC, lambda x, y: 4.6 - (x - px + 1) * 1.1)
    box(cv, 94, 124, 142, 146, [(10, 40, 24), (16, 64, 36), (24, 96, 52), (40, 130, 72), (70, 170, 100)], 2.4)
    rotul(cv, 'LLANÇADORA', 118, 128, (236, 250, 236))
    rotul(cv, 'DIJOUS · 7H', 118, 137, (250, 230, 120))
    cv.flat(px, 120, (255, 80, 60))
    cv.glow(px, 120, 5, (255, 90, 60), 0.5)
    cv.rect(px, 121, px, 123, ZINC, 3.0)


# ─── La residència ─────────────────────────────────────────────────────────

def residencia(cv):
    # el cos, blanc, amb carreus marcats a la planta baixa
    def wall(x, y):
        lvl = 4.9 - (x - RX0) * 0.002
        if y > 100 and (y - 100) % 9 == 0:
            lvl -= 0.9
        return lvl
    cv.rect(RX0, 44, RX1, RBASE, WHITEV, wall)
    cv.vline(RX1, 44, RBASE, WHITEV, 3.0)
    cv.vline(RX1 - 1, 44, RBASE, WHITEV, 3.8)
    # l'ampit del terrat, la cornisa d'or i les gerres daurades
    cv.rect(RX0 - 4, 36, RX1 + 4, 43, WHITEV, lambda x, y: 5.6 if y == 36 else 4.4)
    cv.rect(RX0 - 6, 44, RX1 + 6, 48, GOLDV, lambda x, y: 5.2 - (y - 44) * 0.6 + (0.8 if x % 6 == 0 else 0))
    cv.hline(RX0 - 6, RX1 + 6, 49, WHITEV, 2.4)
    for gx in (RX0 + 4, RX0 + 60, RX1 - 60, RX1 - 4):
        cv.disc(gx, 30, 4, 5, GOLDV, lambda nx, ny: 4.4 - nx - ny * 0.8)
        cv.rect(gx - 2, 34, gx + 2, 35, GOLDV, 3.0)
        cv.rect(gx - 1, 23, gx + 1, 25, GOLDV, 4.6)
    cv.rect(RX0, 96, RX1, 98, WHITEV, lambda x, y: 6.0 if y == 96 else 3.4)   # la imposta entre pisos
    # les finestres del primer pis
    for wx in (254, 286, 400, 432):
        finestra(cv, wx, 58, 22, 28)
    # les finestres grans de la planta baixa, d'arc
    for wx in (254, 410):
        finestra(cv, wx, 112, 42, 64, arc=True)
    # els parterres de façana i les boles de boix
    for x0, x1 in ((RX0 + 2, 302), (402, RX1 - 2)):
        cv.rect(x0, 191, x1, 198, MARBLE, lambda x, y: 4.6 if y == 191 else 3.2)
        for x in range(x0 + 3, x1 - 2, 4):
            flor(cv, x, 189 - (x // 4) % 2, FLOWERS[(x // 4) % 5], size=1, lit=0.35)
    bola_boix(cv, 304, 206, 7)
    bola_boix(cv, 400, 206, 7)
    portic(cv)
    # la llum de reflex del sol a la façana: una diagonal blanca, d'anunci
    for i in range(140):
        x, y = RX0 + 10 + i, 50 + i * 0.4
        for k in range(3):
            if 0 <= y + k < RBASE and cv.get(x, y + k)[:3] != (0, 0, 0):
                cv.flat(x, y + k, mix(cv.get(x, y + k), (255, 255, 255), 0.25))


def finestra(cv, x0, y0, w, h, arc=False):
    """Vidre blau amb el cel reflectit, marc d'or, travesser blanc i el reflex en diagonal."""
    r = w / 2
    cx = x0 + r
    cv.rect(x0 - 3, y0 + h + 1, x0 + w + 3, y0 + h + 3, WHITEV, lambda x, y: 5.6 if y == y0 + h + 1 else 3.2)

    def inside(x, y, pad=0):
        if arc and y < y0 + r:
            return math.hypot(x - cx, y - (y0 + r)) <= r - pad
        return x0 + pad <= x <= x0 + w - pad and y <= y0 + h - pad
    for y in range(y0 - 2, y0 + h + 1):
        for x in range(x0 - 2, x0 + w + 3):
            if inside(x, y, 0):
                t = (y - y0) / h
                lvl = 4.4 - t * 2.4
                d = (x - x0) + (y - y0) * 0.6
                if 8 < d % 34 < 13 or 16 < d % 34 < 18:
                    lvl += 1.6                                         # el reflex
                cv.put(x, y, GLASSV, lvl)
            elif inside(x - 2, y, -2) or inside(x + 2, y, -2) or inside(x, y + 2, -2):
                cv.put(x, y, GOLDV, 4.4 if x < cx else 3.4)
    # travessers
    cv.vline(round(cx), y0 + (r if arc else 0), y0 + h, WHITEV, 5.0)
    cv.hline(x0, x0 + w, y0 + (r if arc else h // 2), WHITEV, 5.0)


def portic(cv):
    x0, x1 = 308, 396
    # el frontó amb el medalló daurat de la V
    cv.poly([(x0 - 4, 86), (352, 60), (x1 + 4, 86)], WHITEV, lambda x, y: 5.2 - (y - 60) * 0.02)
    cv.line(x0 - 4, 86, 352, 60, GOLDV, 5.0)
    cv.line(352, 60, x1 + 4, 86, GOLDV, 4.0)
    cv.disc(352, 76, 7, 7, GOLDV, lambda nx, ny: 4.6 - nx * 0.8 - ny * 0.8)
    cv.disc(352, 76, 5, 5, WHITEV, 5.6)
    for x, y in ((349, 73), (349, 74), (350, 75), (350, 76), (351, 77), (352, 78), (353, 77), (354, 76),
                 (354, 75), (355, 74), (355, 73)):
        cv.flat(x, y, GOLDV[3])
    cv.rect(x0 - 6, 86, x1 + 6, 93, WHITEV, lambda x, y: 5.8 if y == 86 else (3.2 if y == 93 else 4.6))
    cv.hline(x0 - 6, x1 + 6, 89, GOLDV, 5.0)
    # la porta de vidre: a dins, blanc i una aranya de llums
    dx0, dy0, dx1, dy1 = DOOR
    cv.rect(dx0 - 3, dy0 - 3, dx1 + 3, dy1, GOLDV, lambda x, y: 4.6 if x < 352 else 3.6)
    cv.rect(dx0, dy0, dx1, dy1, WHITEV, lambda x, y: 3.4 - (y - dy0) * 0.012 + (0.8 if (x - dx0 + (y - dy0) // 2) % 22 < 3 else 0))
    cv.glow(352, dy0 + 12, 14, (255, 236, 170), 0.6)
    cv.disc(352, dy0 + 12, 6, 3, GOLDV, 4.6)
    cv.vline(352, dy0, dy0 + 9, GOLDV, 3.0)
    cv.rect(dx0, dy0 + 60, dx1, dy1, MARBLE, 3.6)                      # el terra de dins
    cv.vline(352, dy0, dy1, GOLDV, 3.2)                               # les dues fulles
    cv.vline(351, dy0, dy1, GOLDV, 4.6)
    for hx in (348, 356):
        cv.rect(hx, 142, hx, 156, GOLDV, 5.0)                          # els poms
    # les columnes, amb capitell i base d'or
    for cx in (316, 388):
        for y in range(93, 197):
            for x in range(cx - 5, cx + 6):
                u = (x - cx) / 5.5
                flute = 0.7 if (x - cx) % 3 == 0 else 0
                cv.put(x, y, WHITEV, 5.0 - u * 1.8 - u * u * 0.8 - flute)
        cv.rect(cx - 7, 93, cx + 7, 97, GOLDV, lambda x, y: 4.8 - (y - 93) * 0.4)
        cv.rect(cx - 7, 192, cx + 7, 196, GOLDV, lambda x, y: 4.6 - (y - 192) * 0.4)
    # l'escalinata de marbre
    for i, (y0, y1, ex) in enumerate(((196, 199, 0), (200, 203, 4), (204, 207, 8))):
        cv.rect(x0 - 4 - ex, y0, x1 + 4 + ex, y1, MARBLE, lambda x, y, y0=y0: 5.6 if y == y0 else 3.4)


def climatitzador(cv):
    """El climatitzador (blanc, ventilador, la gota de Verne) i el tub que degota a la reixa."""
    x0, y0, x1, y1 = AC
    ombra(cv, (x0 + x1) / 2 + 6, 200, 18, 3, 0.7)
    for lx in (x0 + 3, x1 - 3):                                       # les potes
        cv.rect(lx - 1, y1, lx + 1, 199, WHITEV, lambda x, y, lx=lx: 4.4 - (x - lx + 1) * 1.0)
    box(cv, x0, y0, x1, y1, WHITEV, 4.6, grad=1.0)
    cy = (y0 + y1) // 2 + 1
    cv.disc(483, cy, 10, 10, WHITEV, 2.6)
    for r in (9, 7, 5):
        cv.ring(483, cy, r, WHITEV, 1.6 + (9 - r) * 0.3, step=8)
    for a in range(0, 360, 60):
        ra = math.radians(a)
        cv.line(483, cy, 483 + math.cos(ra) * 8, cy + math.sin(ra) * 8, WHITEV, 3.6)
    cv.disc(483, cy, 1.5, 1.5, GOLDV, 4.6)
    gota(cv, x0 + 4, y0 + 5, 0.6)
    # el tub de desguàs, que surt per baix i fa colze cap a la reixa
    cv.rect(DRIP[0] - 1, y1 + 1, DRIP[0] + 1, DRIP[1], ZINC, lambda x, y: 4.4 - (x - DRIP[0] + 1) * 0.9)
    cv.hline(DRIP[0] - 1, DRIP[0] + 1, DRIP[1], ZINC, 1.4)


def reixa(cv):
    x0, y0, x1, y1 = GRATE
    # la taca d'humitat: l'única gespa que està mullada de debò (i és de plàstic)
    cv.darken(x0 - 8, y0 - 3, x1 + 8, y1 + 5, lambda x, y: 0.5 if ((x - (x0 + x1) / 2) / 22) ** 2 +
              ((y - (y0 + y1) / 2) / 7) ** 2 <= 1 else 0)
    cv.rect(x0, y0, x1, y1, BLACKT, 0.6, lit=0)
    for x in range(x0 + 1, x1, 3):
        cv.vline(x, y0 + 1, y1 - 1, ZINC, 3.0)
    cv.hline(x0, x1, y0, ZINC, 4.2)
    cv.hline(x0, x1, y1, ZINC, 2.2)
    cv.vline(x0, y0, y1, ZINC, 3.6)
    cv.vline(x1, y0, y1, ZINC, 2.4)
    for x in range(x0 + 2, x1 - 1, 3):                               # l'aigua que brilla al fons
        if hr(x, 3) > 0.4:
            cv.flat(x, y1 - 1, (120, 190, 230))


# ─── El cobert del jardiner ────────────────────────────────────────────────

def cobert(cv):
    """Fusta de debò pintada de verd, amb la pintura que salta, la porta vella i la teulada de xapa."""
    ax, ay = SAPEX
    eave = 128
    ombra(cv, (SX0 + SX1) / 2 + 12, SBASE + 3, 72, 6, 0.7)

    def plank(x, y):
        lvl = 3.4 - (1.8 if (x - SX0) % 9 == 0 else 0) + (fbm(x / 5, y / 30, 81) - 0.5) * 1.0
        if (x - SX0) % 9 == 1:
            lvl += 0.8
        return lvl
    for y in range(ay + 4, SBASE + 1):
        for x in range(SX0, SX1 + 1):
            if y < eave and abs(x - ax) > (y - ay) * (ax - SX0) / (eave - ay):
                continue
            peel = fbm(x / 7, y / 9, 83)
            if peel > 0.66:                                            # la pintura saltada: fusta grisa
                cv.put(x, y, WOODG, 3.0 + (peel - 0.66) * 5 - (1.6 if (x - SX0) % 9 == 0 else 0))
            else:
                cv.put(x, y, SHEDG, plank(x, y))
    # el sòcol, terrós (l'únic fang de tot Verdant)
    cv.rect(SX0, SBASE - 4, SX1, SBASE, PLANK, lambda x, y: 2.0 + (hr(x // 2, y) - 0.5))
    # la teulada de xapa ondulada, rovellada
    for side in (-1, 1):
        for k in range(6):
            x_end = SX0 - 8 if side < 0 else SX1 + 8
            for i in range(0, 90):
                t = i / 89
                x = ax + (x_end - ax) * t
                y = ay - 1 + k + (eave + 2 - ay) * t
                lvl = 3.4 - k * 0.3 + (0.9 if int(t * 40) % 2 else -0.5) - (0.6 if side > 0 else 0)
                if fbm(x / 8, y / 8, 85) > 0.6:
                    cv.put(x, y, RUSTV, lvl)
                else:
                    cv.put(x, y, ZINC, lvl - 0.6)
    cv.line(SX0 - 8, eave + 2, ax, ay - 1, ZINC, 5.0)
    cv.line(ax, ay - 1, SX1 + 8, eave + 2, ZINC, 4.2)
    # la porta: taulons, travessers en Z, el baldó rovellat
    dx0, dy0, dx1, dy1 = SDOOR
    cv.rect(dx0 - 2, dy0 - 2, dx1 + 2, dy1, PLANK, 2.0)
    cv.rect(dx0, dy0, dx1, dy1, SHEDG, lambda x, y: 3.0 - (1.6 if (x - dx0) % 8 == 0 else 0) +
            (fbm(x / 6, y / 10, 87) - 0.5) * 1.2)
    for yy in (dy0 + 10, dy1 - 12):
        cv.rect(dx0 + 1, yy, dx1 - 1, yy + 3, SHEDG, lambda x, y: 4.0 if y == yy else 2.6)
    cv.line(dx0 + 2, dy1 - 13, dx1 - 2, dy0 + 14, SHEDG, 3.8)
    cv.line(dx0 + 3, dy1 - 13, dx1 - 1, dy0 + 14, SHEDG, 2.4)
    cv.disc(dx1 - 7, 162, 2, 2, RUSTV, 3.6)
    cv.rect(dx1 - 12, 160, dx1 - 9, 161, RUSTV, 3.0)
    # el rètol a mà, «NIL», i una ferradura
    box(cv, 556, 104, 584, 112, PLANK, 3.8)
    text(cv, 'NIL', 564, 106, None, 0, flat=(240, 236, 214))
    cv.ring(570, 99, 3, RUSTV, 3.0, step=30)
    # la finestreta, bruta
    box(cv, 602, 140, 624, 160, PLANK, 3.6)
    cv.rect(605, 143, 621, 157, GLASSV, lambda x, y: 1.6 + (0.6 if (x + y) % 9 < 2 else 0) +
            (fbm(x / 4, y / 4, 89) - 0.5) * 1.4)
    cv.vline(613, 143, 157, PLANK, 3.0)
    cv.hline(605, 621, 150, PLANK, 3.0)
    # la regadora vella, abonyegada, a la porta
    rx, ry = 528, 202
    cv.poly([(rx - 8, ry - 14), (rx + 8, ry - 14), (rx + 9, ry), (rx - 9, ry)], ZINC,
            lambda x, y: 4.0 - (x - rx) * 0.12 - (1.2 if y == ry - 10 else 0))
    cv.disc(rx, ry - 14, 8, 2, ZINC, 2.0)
    cv.line(rx + 8, ry - 6, rx + 18, ry - 18, ZINC, 3.4)
    cv.disc(rx + 19, ry - 19, 2, 2, ZINC, 4.2)
    for k in range(9):
        a = math.pi * k / 8
        cv.put(rx - math.cos(a) * 6, ry - 15 - math.sin(a) * 6, ZINC, 2.6)


# ─── El parterre i els aspersors ───────────────────────────────────────────

def parterre(cv):
    cx, cy, rx, ry = BED
    ombra(cv, cx + 4, cy + 3, rx + 3, ry + 2, 0.5)
    cv.disc(cx, cy + 2, rx + 3, ry + 3, MARBLE, 3.0)                  # la vorada de marbre
    cv.disc(cx, cy, rx + 3, ry + 3, MARBLE, lambda nx, ny: 5.0 - ny * 0.6)
    cv.disc(cx, cy, rx, ry, TURF, lambda nx, ny: 1.6 + (hr(int(nx * 40), int(ny * 20), 91) - 0.5) * 0.6)
    # anelles de flors, cada anella d'un color: de fora cap a dins
    rings = ((0.9, MAGENTA), (0.72, CYANF), (0.54, YELLOWF), (0.36, ORANGEF), (0.16, VIOLETF))
    pts = []
    for k, (f, ramp) in enumerate(rings):
        n = max(3, int(46 * f))
        for i in range(n):
            a = 2 * math.pi * i / n + k * 0.3
            pts.append((cy + math.sin(a) * ry * f, cx + math.cos(a) * rx * f, ramp))
    for y, x, ramp in sorted(pts):                                     # de darrere cap a davant
        s = 2 if y > cy - ry * 0.4 else 1
        tija_y = 4 if s == 2 else 2
        cv.vline(round(x), round(y) - tija_y + 1, round(y) + 1, TURF, 4.6)
        flor(cv, round(x), round(y) - tija_y, ramp, size=s, lit=0.35)


def aspersor(cv, x, y):
    ombra(cv, x + 2, y + 1, 5, 1.6, 0.6)
    cv.disc(x, y, 4, 1.8, WHITEV, 3.6)
    cv.rect(x - 1, y - 6, x + 1, y, WHITEV, lambda xx, yy: 5.4 - (xx - x + 1) * 1.1)
    cv.disc(x, y - 7, 2.5, 1.6, GOLDV, lambda nx, ny: 4.6 - nx - ny)
    cv.flat(x, y - 9, GOLDV[5])


def flamenc(cv, x, y):
    """Un flamenc de plàstic rosa, clavat a la gespa: el gust del Magnat."""
    P = MAGENTA
    ombra(cv, x + 5, y + 1, 6, 1.4, 0.6)
    cv.vline(x, y - 12, y, ZINC, 3.0)
    cv.vline(x + 2, y - 12, y - 2, ZINC, 2.4)
    cv.disc(x + 1, y - 16, 7, 4, P, lambda nx, ny: 3.6 - nx * 0.5 - ny * 1.0)
    cv.poly([(x + 6, y - 18), (x + 10, y - 19), (x + 8, y - 15)], P, 2.6)      # la cua
    for k in range(10):                                                   # el coll en essa
        cv.put(x - 5 + math.sin(k * 0.5) * 2, y - 18 - k, P, 3.8)
        cv.put(x - 4 + math.sin(k * 0.5) * 2, y - 18 - k, P, 3.0)
    cv.disc(x - 3, y - 29, 2.2, 2, P, 4.0)
    cv.flat(x - 3, y - 30, (20, 20, 20))
    cv.line(x - 5, y - 29, x - 7, y - 26, BLACKT, 2.0)
    cv.flat(x - 6, y - 29, (250, 236, 220))


def parterre_petit(cv):
    """Un tros de parterre a baix a la dreta, tallat pel marc."""
    cx, cy, rx, ry = 640, 254, 52, 12
    cv.disc(cx, cy, rx + 3, ry + 3, MARBLE, lambda nx, ny: 5.0 - ny * 0.6)
    cv.disc(cx, cy, rx, ry, TURF, 1.6)
    for j in range(60):
        a = math.pi * (0.5 + hr(j, 1, 2) * 1.0)
        f = 0.2 + 0.75 * hr(j, 3, 4)
        x, y = cx + math.cos(a) * rx * f, cy - abs(math.sin(a)) * ry * f
        if y < RH - 1:
            cv.vline(round(x), round(y) - 2, round(y) + 1, TURF, 4.6)
            flor(cv, round(x), round(y) - 3, FLOWERS[j % 5], size=2, lit=0.35)


# ─── Muntatge ───────────────────────────────────────────────────────────────

def bg(cv):
    sky(cv)
    hills(cv)
    bardissa(cv, 70, 640)
    gespa(cv)
    cami(cv)
    llancadora(cv)
    panell_preu(cv, 186, 112, '64', post=46, w=44)
    residencia(cv)
    climatitzador(cv)
    reixa(cv)
    cobert(cv)
    cantimplora(cv)
    parterre(cv)
    parterre_petit(cv)
    flamenc(cv, 446, 236)
    for x, y in SPRINK:
        aspersor(cv, x, y)
    # tot el que no és sala: negre (la barra de verbs)
    cv.rect(0, RH, W - 1, H - 1, BLACKT, 0, lit=0)
    for y in range(RH, H):
        for x in range(W):
            cv.flat(x, y, (0, 0, 0))


def galleda_reixa(cv):
    """La galleda d'en Nil sota el tub del climatitzador, damunt la reixa, recollint les gotes."""
    ombra(cv, DRIP[0] + 5, GRATE[3] + 1, 10, 2, 0.6)
    galleda(cv, DRIP[0], GRATE[3], s=0.62, plena=True)


PROPS = {'galleda_reixa': galleda_reixa}

GEOMETRIA = {
    'things': {
        'rampa': {'rect': (0, 104, 96, 236), 'walk': (92, 238)},
        'porta_residencia': {'rect': (330, 96, 374, 200), 'walk': (352, 214)},
        'porta_cobert': {'rect': (546, 100, 594, 206), 'walk': (570, 214)},
        'flors': {'rect': (114, 212, 280, 252), 'walk': (196, 254)},
        'aspersors': {'rect': (508, 214, 624, 246), 'walk': (566, 246)},
        'reixa': {'rect': (462, 142, 502, 214), 'walk': (482, 220)},
        'panell_preu': {'rect': (182, 108, 234, 186), 'walk': (214, 214)},
        'llancadora': {'rect': (98, 116, 190, 204), 'walk': (150, 212)},
    },
    'spawns': {
        'nil': (196, 238),
        'fidel': (352, 211),
        'iri': (292, 236),
        'vet': (110, 244),
    },
    'walkable': [(34, 238), (104, 232), (112, 208), (300, 210), (306, 214), (400, 214), (408, 210), (462, 212),
                 (500, 212), (636, 208), (636, 256), (4, 256), (4, 242)],
}


# ─── Animacions ────────────────────────────────────────────────────────────

PERFUM = [(255, 214, 240), (240, 200, 255), (255, 255, 255), (214, 240, 255)]


def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv.img


def _frames_boira():
    """Els aspersors no reguen: escombren el jardí amb un raig de perfum (gotetes rosades, liles i blanques) que
    va i ve, i deixen una boira a quadres que s'esvaeix."""
    base = _base()
    frames = []
    n = 16
    D = 30.0                                                          # l'abast del raig
    for i in range(n):
        cv = Canvas(light=LIGHT, img=base.copy())
        for k, (sx, sy) in enumerate(SPRINK):
            ph = 2 * math.pi * (i / n) + k * 2.2
            # la boira que queda: un núvol baix, a quadres, que respira
            for y in range(sy - 20, sy + 4):
                for x in range(sx - 30, sx + 31):
                    d = ((x - sx) / 30) ** 2 + ((y - sy + 6) / 11) ** 2
                    if d < 1 and (x + 2 * y + i) % 4 == 0 and hr(x // 3, y // 2, (i + k) // 3) > 0.35 + d * 0.5:
                        cv.flat(x, y, mix(cv.get(x, y), (255, 214, 244), 0.45 - d * 0.25))
            # el raig: una paràbola de gotetes que gira d'una banda a l'altra
            th = math.pi * (1.5 + 0.42 * math.sin(ph))                # cap amunt i escombrant
            dirx, diry = math.cos(th + math.pi / 2), 0.3
            for j in range(0, int(D), 2):
                d = j + (i % 2)
                x = sx + math.sin(ph) * d * 1.0
                y = sy - 9 - d * (1 - d / D) * 0.8 + d * 0.18 * math.cos(ph)
                col = PERFUM[(j // 2 + k) % 4]
                cv.flat(x, y, col)
                if j > D * 0.6 and hr(j, i, k) > 0.4:
                    cv.flat(x + 1, y + 1, PERFUM[(j + 1) % 4])
            # l'esquitx al final del raig
            ex = sx + math.sin(ph) * D
            ey = sy - 9 + D * 0.18 * math.cos(ph)
            for q in range(10):
                cv.flat(ex + (hr(q, i, k) - 0.5) * 8, ey + (hr(q, i, k + 5) - 0.5) * 4, PERFUM[q % 4])
        frames.append(_diff(cv.img, base))
    return frames


def _frames_degoteig():
    """La gota que cau del tub del climatitzador a la reixa (o a la galleda)."""
    base = _base()
    frames = []
    x, y0, y1 = DRIP[0], DRIP[1] + 1, GRATE[1] + 2
    n = 12
    for i in range(n):
        cv = Canvas(light=LIGHT, img=base.copy())
        if i < 5:                                                     # la gota s'infla
            if i >= 1:
                cv.flat(x, y0, (150, 210, 250))
            if i >= 3:
                cv.flat(x, y0 + 1, (200, 236, 255))
        elif i < 9:                                                   # cau
            yy = y0 + 2 + (i - 5) ** 2 * 1.4
            if yy < y1:
                cv.flat(x, yy, (200, 236, 255))
                cv.flat(x, yy - 1, (120, 190, 240))
        elif i == 9:                                                  # esquitx
            for dx, dy in ((-2, -1), (2, -1), (-1, -2), (1, -2)):
                cv.flat(x + dx, y1 + dy, (200, 236, 255))
        frames.append(_diff(cv.img, base))
    return frames


ANIMS = {'boira': {'frames': _frames_boira, 'frameDuration': 140},
         'degoteig': {'frames': _frames_degoteig, 'frameDuration': 160}}
