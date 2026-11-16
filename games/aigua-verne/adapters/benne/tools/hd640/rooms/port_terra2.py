"""
El port de Terra-2 (Escena 2). Sala «de lluny» (persones de ≈83 px).

Un port de naus de càrrega de terra batuda, mig buit, al migdia de pols:
  - a l'horitzó, els hangars del port i la **Canonada de Terra-2**, fins al cel;
  - una grua de port parada, amb el ganxo penjant; contenidors blancs amb la gota de Verne (i algun de rovellat);
  - el tauler d'anuncis de suro, ple de papers de Verne S.A.; el panell del preu (▲, sense xifres);
  - a la dreta, la **Cantimplora**: una nau cisterna panxuda, oliva i taronja, rovellada, amb nou dipòsits
    rodons a l'esquena (cinc darrere, quatre davant), els motors a popa i la rampa de la bodega abaixada;
  - el camí de la granja, que surt per l'esquerra, amb un pal indicador.
ANIMS: `pols` (la pols que passa), `llum_canonada` i `balisa` (el llum taronja de la Cantimplora).
"""
import math

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from PIL import Image

from hd.pix import Canvas, Light, W, H, hr, mix, B4
from hd.rooms.exterior import fbm, smooth
from hd640.rooms.terra2_comu import (
    RH, SKY, HILL, EARTH, STONE, PLANK, GREYW, WHITEP, COL, BLUE, BLACKT, IRONR, RUSTT, OLIVE, ORANGE, WARN, CORK,
    PAPER, LED, GRASS, text, text_width, gota, dust_sky, hills, canonada, panell_preu, cracks, shadow, outline,
    dust_wind_frames, llum_canonada_frames, _diff)

# Art a 2× (1280×720 per a una sala de 640×360): el mateix dibuix, amb les formes, el dither i la llum a la
# resolució real (hd1280/canvas2x.py); el motor el mostra a 1/2 (artScale al .room.json).
ART_SCALE = 2
from hd1280.canvas2x import Canvas2x as Canvas  # noqa: E402,F811
from hd.pix import Canvas as Canvas1x  # noqa: E402,F401  (llenços auxiliars en píxels de sala: figures, textos)

HOR = 122
CAN_X = 364
SUN = (556, 22)
GROUND_SHIP = 206                         # on reposen les potes de la nau
DOORB = (412, 120, 452, 186)              # la porta de la bodega (x0, y0, x1, y1)
RAMP = [(412, 186), (452, 186), (462, 224), (398, 224)]

LIGHT = Light(ambient=0.6, vignette=(70, 18), floor_fade=None)
LIGHT.point(580, -40, r=720, k=1.2, power=1.1)            # el sol, a dalt a la dreta

TANKC = [(46, 40, 30), (78, 70, 52), (112, 104, 80), (146, 138, 108), (178, 170, 136), (206, 198, 164),
         (228, 222, 190)]                                  # la pintura dels dipòsits, de color os
CRANE = [(40, 30, 10), (76, 58, 18), (116, 90, 30), (156, 124, 44), (192, 158, 64), (220, 190, 96)]
WARM = [(60, 30, 10), (120, 70, 24), (190, 120, 50), (240, 180, 90), (255, 226, 160)]


# ─── Fons: cel, horitzó, hangars ────────────────────────────────────────────

def hangars(cv):
    """Els hangars del port, lluny, a l'horitzó de l'esquerra: naus de xapa amb sostre de volta."""
    for x0, w, h in ((-6, 56, 22), (54, 70, 26), (130, 40, 16)):
        top = HOR - h
        for x in range(x0, x0 + w):
            u = (x - x0) / w
            arch = top - math.sin(u * math.pi) * 6
            for y in range(int(arch), HOR + 1):
                lvl = 3.2 + u * 0.8 - (0.8 if (x - x0) % 4 == 0 else 0) - (1.0 if y < arch + 2 else 0)
                cv.put(x, y, COL if x0 != 54 else STONE, lvl - (0 if x0 != 54 else -1.0), lit=0)
        cv.rect(x0 + w // 2 - 8, HOR - 12, x0 + w // 2 + 8, HOR, BLACKT, 2.0, lit=0)   # la porta, oberta
    cv.rect(64, HOR - 24, 112, HOR - 19, WHITEP, 4.0, lit=0)                     # el rètol de Verne
    gota(cv, 68, HOR - 22, 1)
    text(cv, 'VERNE SA', 73, HOR - 24, BLUE, 1.0, lit=0, flat=BLUE[1])
    # la torre de control
    tx = 176
    cv.rect(tx, HOR - 40, tx + 3, HOR, COL, lambda x, y: 2.6 + (x - tx) * 0.5, lit=0)
    cv.rect(tx - 5, HOR - 48, tx + 8, HOR - 40, COL, 3.6, lit=0)
    cv.rect(tx - 4, HOR - 46, tx + 7, HOR - 43, BLACKT, 2.4, lit=0)
    cv.rect(tx + 1, HOR - 54, tx + 1, HOR - 48, IRONR, 2.0, lit=0)
    # una nau de càrrega aparcada, lluny, a la dreta de la Canonada (de Verne, blanca)
    for x in range(262, 330):
        u = (x - 262) / 68
        top = HOR - 10 - math.sin(min(1, u * 1.4) * math.pi / 2) * 6
        for y in range(int(top), HOR - 2):
            cv.put(x, y, COL, 3.6 + (y - top) * -0.1 + u * 0.6, lit=0)
    cv.rect(272, HOR - 7, 318, HOR - 6, BLUE, 2.0, lit=0)
    for lx in (270, 300, 322):
        cv.rect(lx, HOR - 3, lx, HOR, IRONR, 2.0, lit=0)


def ground(cv):
    """Terra batuda: compactada per les naus, amb roderes, taques d'oli i un cercle d'aterratge esborrat."""
    for y in range(HOR + 1, RH):
        t = (y - HOR) / (RH - HOR)
        for x in range(W):
            lvl = 4.6 + t * 0.8 + (fbm(x / 50, y / 8, 17) - 0.5) * 1.3 + (hr(x // 2, y) - 0.5) * 0.4
            c = cracks(x, int((y - HOR) / (0.3 + t)) + HOR, cell=14 + int(t * 10))
            if c < 0.8 + t * 0.5 and fbm(x / 60, y / 20, 3) > 0.5:
                lvl -= 1.6                                                   # clivelles, només a clapes
            # roderes: dues bandes que vénen del camí de l'esquerra cap a la nau
            for cy, k in ((228 - (x - 0) * 0.04, 1.0), (238 - x * 0.05, 1.0)):
                if abs(y - cy) < 1.2 + t:
                    lvl -= 0.7 * k
            cv.put(x, y, EARTH, lvl)
    # el cercle d'aterratge, pintat i mig esborrat (en perspectiva)
    cx, cy, rx, ry = 520, 214, 120, 16
    for a in range(0, 360):
        ar = math.radians(a)
        for dr in (0, 1, 2):
            x = cx + math.cos(ar) * (rx - dr * 2)
            y = cy + math.sin(ar) * (ry - dr * 0.3)
            if hr(int(x // 3), int(y), 5) > 0.35:
                cv.put(x, y, EARTH, 7.6)
    # les taques d'oli
    for ox, oy, rx_, ry_ in ((300, 232, 14, 3), (156, 214, 10, 2), (470, 246, 20, 4), (590, 236, 12, 3)):
        cv.darken(ox - rx_, oy - ry_, ox + rx_, oy + ry_,
                  lambda x, y: 0.5 * (1 - ((x - ox) / rx_) ** 2 - ((y - oy) / ry_) ** 2) + 0.2 * fbm(x / 4, y / 2, ox))
    # herba seca a les vores
    for x0, y0 in ((4, 204), (140, 200), (250, 196), (360, 254), (24, 250)):
        for k in range(6):
            a = 1.2 + (k - 3) * 0.2
            cv.line(x0 + k, y0, x0 + k + math.cos(a) * 6, y0 - math.sin(a) * 6, GRASS, 2.0 + hr(k, x0) * 2)


# ─── La grua i els contenidors ──────────────────────────────────────────────

def crane(cv):
    """La grua de port, parada: una torre de gelosia sobre un pòrtic de quatre potes, la cabina i el braç cap a
    l'esquerra, amb el ganxo penjant sobre els contenidors."""
    bx, base, top = 236, 170, 48
    # les potes del pòrtic
    for lx in (bx - 24, bx + 20):
        cv.rect(lx, top + 70, lx + 4, base, CRANE, lambda x, y: 2.6 + (x - lx) * 0.4)
        cv.rect(lx - 2, base - 2, lx + 6, base, IRONR, 2.0)
    cv.rect(bx - 24, top + 66, bx + 24, top + 72, CRANE, lambda x, y: 3.4 - (y - top - 66) * 0.2)
    cv.line(bx - 20, top + 72, bx + 20, base - 4, CRANE, 1.6)
    cv.line(bx + 20, top + 72, bx - 20, base - 4, CRANE, 1.4)
    # la torre de gelosia
    for y in range(top, top + 67):
        cv.put(bx - 7, y, CRANE, 2.4)
        cv.put(bx - 6, y, CRANE, 2.0)
        cv.put(bx + 6, y, CRANE, 4.0)
        cv.put(bx + 7, y, CRANE, 3.4)
    for y in range(top, top + 66, 8):
        cv.line(bx - 6, y, bx + 6, y + 8, CRANE, 2.4)
        cv.line(bx - 6, y + 8, bx + 6, y, CRANE, 2.0)
    # el braç, cap a l'esquerra, i el contrapès a la dreta
    jy = top - 18
    for x in range(bx - 150, bx + 40):
        yy = jy + (x - bx) * 0.1
        cv.put(x, yy, CRANE, 4.0)
        cv.put(x, yy + 4, CRANE, 2.4)
        if (x - bx) % 9 == 0:
            cv.line(x, yy, x + 4, yy + 4, CRANE, 2.0)
    cv.rect(bx + 26, jy + 6, bx + 44, jy + 18, IRONR, lambda x, y: 2.4 + (x - bx - 26) * 0.08)   # el contrapès
    cv.line(bx, top - 14, bx, jy - 14, CRANE, 3.0)                           # el pal i els tirants
    cv.line(bx, jy - 14, bx - 146, jy - 14, IRONR, 1.6)
    cv.line(bx, jy - 14, bx + 40, jy + 4, IRONR, 1.6)
    # la cabina
    cv.rect(bx - 10, top - 14, bx + 12, top, CRANE, lambda x, y: 3.6 + (x - bx) * 0.04)
    cv.rect(bx - 8, top - 11, bx - 1, top - 5, BLACKT, 2.4)
    cv.put(bx - 2, top - 10, SKY, 5.0)
    outline(cv, bx - 10, top - 14, bx + 12, top, CRANE[0])
    # el carro i el ganxo
    hx = bx - 92
    hy0 = int(jy - 92 * 0.1) + 5
    cv.rect(hx - 4, hy0, hx + 4, hy0 + 3, IRONR, 2.6)
    for y in range(hy0 + 4, 118):
        cv.put(hx - 1, y, IRONR, 1.8)
        cv.put(hx + 1, y, IRONR, 1.8)
    cv.rect(hx - 4, 118, hx + 4, 123, WARN, lambda x, y: 3.4 - (y - 118) * 0.2)
    for k in range(5):
        cv.put(hx + math.sin(k * 0.7) * 3, 124 + k, IRONR, 3.4)


def container(cv, x0, base, w, h, kind, lvl=3.6):
    """Un contenidor: de Verne (blanc, la gota blava i la franja) o vell (rovell)."""
    y0 = base - h
    ramp = WHITEP if kind == 'verne' else (RUSTT if kind == 'rovell' else OLIVE)

    def l(x, y):
        v = lvl + (0.6 if (x - x0) % 4 == 0 else -0.2) - (y - y0) * 0.01
        if kind != 'verne':
            v += (fbm(x / 6, y / 6, x0) - 0.5) * 1.2
        else:
            v -= 0.8 * smooth(0.62, 0.8, fbm(x / 5, y / 14, 3))              # brutícia i regalims
        return v
    cv.rect(x0, y0, x0 + w, base, ramp, l)
    outline(cv, x0, y0, x0 + w, base, ramp[0])
    cv.rect(x0 + 1, y0 + 1, x0 + w - 1, y0 + 1, ramp, lvl + 1.4)
    if kind == 'verne':
        cv.rect(x0 + 2, base - 7, x0 + w - 2, base - 5, BLUE, 1.8, lit=0)
        gota(cv, x0 + w // 2, y0 + h // 2 - 2, 4)
    # les portes del cap (a la dreta) i les tanques
    cv.rect(x0 + w - 8, y0 + 2, x0 + w - 8, base - 2, ramp, 1.2)
    for k in (x0 + w - 6, x0 + w - 3):
        cv.rect(k, y0 + 3, k, base - 3, IRONR, 2.8)


def containers(cv):
    base = 178
    container(cv, 140, base, 58, 26, 'verne')
    container(cv, 200, base, 58, 26, 'verne', 3.2)
    container(cv, 162, base - 27, 58, 26, 'verne', 4.0)
    container(cv, 268, base - 2, 52, 24, 'rovell')
    shadow(cv, 200, base + 2, 74, 3, 0.7)
    # un tractor d'arrossegament, petit, aparcat davant
    cv.rect(326, base - 4, 340, base + 4, ORANGE, lambda x, y: 3.6 - (y - base + 4) * 0.1)
    cv.rect(328, base - 10, 336, base - 4, BLACKT, 2.4)
    cv.disc(330, base + 5, 3, 3, BLACKT, 1.8)
    cv.disc(338, base + 5, 3, 3, BLACKT, 1.8)
    shadow(cv, 330, base + 8, 10, 2, 0.7)


# ─── El tauler, el panell, el camí ──────────────────────────────────────────

def tauler(cv):
    """El tauler d'anuncis de suro, amb una teuladeta, ple de papers de Verne S.A."""
    x0, x1, y0, y1, base = 48, 124, 108, 156, 204
    for px_ in (x0 + 6, x1 - 8):                                             # els pals
        cv.rect(px_, y0 - 6, px_ + 2, base, GREYW, lambda x, y: 2.8 + (x - px_) * 0.7)
    cv.poly([(x0 - 6, y0 - 4), (x1 + 6, y0 - 4), (x1 + 2, y0 - 12), (x0 - 2, y0 - 12)], RUSTT,
            lambda x, y: 3.4 + (0.8 if x % 4 < 2 else -0.4))                 # la teuladeta de xapa
    cv.rect(x0 - 6, y0 - 4, x1 + 6, y0 - 3, BLACKT, 1.2)
    cv.rect(x0 - 2, y0 - 1, x1 + 2, y1 + 2, PLANK, lambda x, y: 3.0 + (x - x0) * 0.004)   # el marc
    cv.rect(x0, y0 + 1, x1, y1, CORK, lambda x, y: 3.0 + (hr(x, y) - 0.5) * 1.2 + (fbm(x / 9, y / 9, 2) - 0.5) * 0.6)
    cv.darken(x0, y0 + 1, x1, y0 + 4, 0.6)
    # els papers: tots de Verne (la franja blava i la gota), menys un, escrit a mà
    papers = [(52, 113, 18, 22, 'v'), (72, 111, 16, 18, 'v'), (90, 115, 15, 20, 'v'), (107, 112, 14, 16, 'v'),
              (54, 137, 14, 15, 'v'), (70, 132, 18, 20, 'v'), (90, 138, 14, 14, 'm'), (106, 131, 15, 20, 'v')]
    for k, (px0, py0, w, h, kind) in enumerate(papers):
        tilt = (hr(k, 4) - 0.5) * 2
        cv.rect(px0 + 1, py0 + 1, px0 + w + 1, py0 + h + 1, BLACKT, 1.6)       # l'ombra
        for y in range(py0, py0 + h):
            for x in range(px0, px0 + w):
                xx = x + round(tilt * (y - py0) / h)
                cv.put(xx, y, PAPER, 4.6 - k * 0.05 - (0.8 if x == px0 + w - 1 else 0))
        if kind == 'v':
            cv.rect(px0 + 1, py0 + 1, px0 + w - 2, py0 + 3, BLUE, 2.0, lit=0)
            cv.flat(px0 + 2, py0 + 2, (220, 236, 250))
            for ly in range(py0 + 6, py0 + h - 2, 2):
                ll = int(w * (0.4 + 0.5 * hr(k, ly)))
                cv.rect(px0 + 2, ly, px0 + 1 + ll, ly, PAPER, 1.6)
        else:
            for ly in range(py0 + 3, py0 + h - 2, 3):
                for x in range(px0 + 2, px0 + w - 2):
                    if hr(x, ly) > 0.35:
                        cv.flat(x, ly + (x % 3 == 0), (60, 60, 120))
        cv.put(px0 + w // 2, py0 + 1, [(120, 20, 20), (200, 40, 40), (250, 100, 90)], 1.6, lit=0)   # la xinxeta
    text(cv, 'FEINES', x0 + 24, y1 + 4, PLANK, 1.0, lit=0, flat=(60, 40, 28)) if False else None
    shadow(cv, (x0 + x1) // 2 - 10, base + 1, 46, 3, 0.7)


def cami(cv):
    """El camí de la granja, que surt per l'esquerra, i el pal indicador."""
    for y in range(204, RH):
        t = (y - 204) / (RH - 204)
        for x in range(0, 70):
            f = 1 - smooth(10, 70, x + (fbm(x / 10, y / 5, 9) - 0.5) * 20)
            cy = 230
            if abs(y - cy) < 14 + t * 6:
                k = f * (1 - smooth(10, 16, abs(y - cy)))
                if k > B4[y & 3][x & 3] * 0.8:
                    cv.put(x, y, EARTH, 6.2 + (hr(x // 2, y) - 0.5) * 0.8)
    x, base = 22, 206
    cv.rect(x, base - 30, x + 2, base, GREYW, lambda xx, y: 2.4 + (xx - x) * 0.8)
    cv.poly([(x - 18, base - 28), (x + 16, base - 28), (x + 16, base - 20), (x - 18, base - 20), (x - 22, base - 24)],
            GREYW, lambda xx, y: 4.2 - (0.8 if y == base - 20 else 0))
    text(cv, 'GRANJA', x - 14, base - 26, BLACKT, 1.0, lit=0, flat=(60, 40, 30))
    shadow(cv, x - 6, base + 1, 9, 2, 0.6)


def barrels(cv):
    """Bidons buits, apilats a la vora de la grua."""
    for k, (x, base) in enumerate(((132, 192), (142, 194), (137, 184))):
        ramp = ORANGE if k == 1 else (OLIVE if k == 0 else RUSTT)
        cv.rect(x - 4, base - 9, x + 4, base, ramp, lambda xx, y: 3.0 + (xx - x) * 0.2 - (1.2 if y in (base - 6, base - 3) else 0))
        cv.disc(x, base - 9, 4, 1.4, ramp, 4.4)
    shadow(cv, 132, 195, 14, 2, 0.7)


# ─── La Cantimplora ─────────────────────────────────────────────────────────

HX0 = 396                        # la popa


def _hull_s(x):
    t = (x - HX0) / 250
    return math.sin(min(1.0, max(0.0, t) * 1.5) * math.pi / 2)


def _hull_top(x):
    """El llom del buc: baix a popa i panxut cap al mig."""
    return 64 + 32 * (1 - _hull_s(x)) ** 1.4


def _hull_bot(x):
    return 192 - 8 * (1 - _hull_s(x)) ** 2


def _hull_cap(y):
    """La popa és arrodonida: on comença el buc a cada alçada."""
    top, bot = _hull_top(HX0), _hull_bot(HX0)
    mid, half = (top + bot) / 2, (bot - top) / 2
    v = (y - mid) / half
    return HX0 + 10 * v * v


def _tank(cv, cx, cy, r, lvl=0.0):
    """Un dipòsit esfèric, color os, amb la franja taronja i rovell; la tapa a dalt."""
    def l(nx, ny):
        v = 3.8 + nx * 0.9 - ny * 1.4 + lvl
        if abs(ny - 0.15) < 0.12:
            return v
        return v
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            nx, ny = (x - cx) / r, (y - cy) / r
            d = nx * nx + ny * ny
            if d <= 1:
                v = 3.8 + nx * 0.9 - ny * 1.4 + lvl - (1.2 if d > 0.88 else 0)
                band = abs(ny + 0.05 - nx * 0.1) < 0.1
                if band:
                    cv.put(x, y, ORANGE, v - 0.4)
                elif fbm(x / 3, y / 9, int(cx)) > 0.7 and ny > 0.0:
                    cv.put(x, y, RUSTT, v - 0.6)                             # regalims de rovell
                else:
                    cv.put(x, y, TANKC, v)
    cv.rect(cx - 3, cy - r - 2, cx + 3, cy - r + 1, IRONR, lambda x, y: 3.6 + (x - cx) * 0.2)   # la tapa
    cv.put(cx + r * 0.4, cy - r * 0.55, TANKC, 6.6)                           # la lluentor


def cantimplora(cv):
    # l'ombra de la nau a terra (cap a l'esquerra)
    shadow(cv, 500, GROUND_SHIP + 4, 150, 12, 0.9)
    # les potes
    for lx in (436, 532, 624):
        foot = lx - 10
        cv.line(lx, _hull_bot(lx) - 4, foot, GROUND_SHIP - 2, IRONR, 3.0)
        cv.line(lx + 1, _hull_bot(lx) - 4, foot + 1, GROUND_SHIP - 2, IRONR, 4.4)
        cv.line(lx + 2, _hull_bot(lx) - 4, foot + 2, GROUND_SHIP - 2, IRONR, 2.2)
        cv.rect(foot - 4, GROUND_SHIP - 4, foot + 6, GROUND_SHIP, IRONR, lambda x, y: 3.6 - (y - GROUND_SHIP + 4) * 0.4)
        cv.rect(foot - 1, _hull_bot(lx) + 2, foot + 3, _hull_bot(lx) + 8, WARN, 3.0)
    # els dipòsits de darrere (cinc), i després els del davant (quatre)
    for k, cx in enumerate((420, 470, 520, 570, 620)):
        _tank(cv, cx, _hull_top(cx) - 6, 22, lvl=-0.6)
    # el buc
    for x in range(HX0, W):
        top, bot = _hull_top(x), _hull_bot(x)
        hcy, hh = (top + bot) / 2, (bot - top) / 2
        for y in range(int(top), int(bot) + 1):
            if x < _hull_cap(y):
                continue
            v = (y - hcy) / hh
            pv = (v + 1) * 3.5
            plate_r = int(pv)
            plate_c = (x - HX0 + (plate_r % 2) * 20) // 40
            seam = abs(pv % 1) < 0.05 or (x - HX0 + (plate_r % 2) * 20) % 40 == 0
            lvl = 3.7 - v * 2.0 - max(0.0, v) ** 2 * 1.6 - max(0.0, -v - 0.8) * 4 + (hr(plate_c, plate_r) - 0.5) * 0.6
            lvl += (fbm(x / 30, y / 10, 8) - 0.5) * 0.6
            ramp = OLIVE
            if 0.18 < v < 0.34:
                ramp = ORANGE                                                # la franja de seguretat
                lvl -= 0.6
            if fbm(x / 3, y / 22, 21) > 0.68 and v > -0.5:
                ramp, lvl = RUSTT, lvl - 0.2                                 # regalims de rovell
            if seam:
                lvl -= 0.9
            elif (x - HX0 + (plate_r % 2) * 20) % 40 in (3, 37) and int(y) % 4 == 0:
                lvl += 1.0                                                   # els reblons
            cv.put(x, y, ramp, lvl)
        cv.put(x, top, OLIVE, 6.0)
        cv.put(x, bot, OLIVE, 0.6)
    # els dipòsits del davant
    for cx in (446, 496, 546, 596):
        _tank(cv, cx, _hull_top(cx) + 2, 25)
    # la popa: la vora i els dos motors
    for y in range(int(_hull_top(HX0)), int(_hull_bot(HX0)) + 1):
        cx_ = _hull_cap(y)
        cv.put(cx_, y, OLIVE, 1.0)
        cv.put(cx_ + 1, y, OLIVE, 2.0)
    for ny, r in ((120, 12), (164, 14)):
        for x in range(HX0 - 18, HX0 + 1):
            t = (HX0 - x) / 18
            rr = r * (0.7 + 0.3 * t)
            for y in range(int(ny - rr), int(ny + rr) + 1):
                u = (y - ny) / rr
                inner = x < HX0 - 16 and abs(u) < 0.8
                cv.put(x, y, BLACKT if inner else IRONR, (0.4 + abs(u)) if inner else (3.0 - u * 1.4 - t * 0.6))
        cv.rect(HX0 - 20, int(ny - r) + 1, HX0 - 18, int(ny + r) - 1, IRONR, 4.0)
        cv.darken(HX0 - 20, int(ny + r) - 3, HX0 - 6, int(ny + r) + 6, 0.5)   # el sutge
    # el pont, al morro (a la dreta): el finestral
    for x in range(588, W):
        y0 = _hull_top(x) + 18
        for y in range(int(y0), int(y0) + 9):
            glass = (x - 588) % 12 not in (0, 1)
            cv.put(x, y, BLACKT if glass else OLIVE, (2.0 + (1.6 if (y - y0) < 3 else 0) - (0.4 if (x + y) % 5 else 0)) if glass else 1.6, lit=0)
        cv.put(x, y0 - 1, OLIVE, 1.0)
        cv.put(x, y0 + 9, OLIVE, 5.0)
    # els ulls de bou de la bodega
    for px_ in (480, 512, 544):
        py_ = 118
        cv.disc(px_, py_, 5, 5, IRONR, lambda nx, ny: 3.6 + nx - ny)
        cv.disc(px_, py_, 3, 3, BLACKT, lambda nx, ny: 1.6 - ny, lit=0)
        cv.put(px_ - 1, py_ - 1, SKY, 5.0, lit=0)
    # el nom, pintat amb plantilla, i la matrícula
    text(cv, 'CANTIMPLORA', 486, 146, OLIVE, 1.0, lit=0, flat=(226, 220, 190))
    text(cv, 'T2-0447', 560, 158, OLIVE, 1.0, lit=0, flat=(190, 186, 160))
    # la balisa de dalt (apagada: l'encén l'animació)
    cv.rect(520, int(_hull_top(520)) - 30, 522, int(_hull_top(520)) - 26, IRONR, 2.0)
    # la porta de la bodega, oberta: a dins, la llum càlida de filament
    x0, y0, x1, y1 = DOORB
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            d = math.hypot((x - (x0 + x1) / 2) / 20, (y - y0 - 14) / 30)
            cv.put(x, y, WARM, 2.2 - d * 1.6 + (y - y0) * 0.006, lit=0)
    cv.rect(x0 + 6, y0 + 28, x0 + 22, y1, BLACKT, lambda x, y: 1.0 + (0.6 if x % 4 == 0 else 0), lit=0)   # dipòsits a dins
    cv.disc(x1 - 10, y1 - 14, 8, 12, WARM, lambda nx, ny: 0.4 + nx * 0.6, lit=0)   # l'últim barril, a contrallum
    for k in (x0 + 10, x1 - 10):
        cv.disc(k, y0 + 3, 1.4, 1.4, WARM, 4.6, lit=0)                        # els llums de filament
    # el marc de la porta, amb la banda de perill
    for y in range(y0 - 4, y1 + 1):
        for x in (x0 - 4, x0 - 3, x0 - 2, x0 - 1, x1 + 1, x1 + 2, x1 + 3, x1 + 4):
            cv.put(x, y, WARN if (y + x) // 3 % 2 else BLACKT, 3.4 if (y + x) // 3 % 2 else 2.0)
    for x in range(x0 - 4, x1 + 5):
        for y in (y0 - 4, y0 - 3, y0 - 2, y0 - 1):
            cv.put(x, y, WARN if (y + x) // 3 % 2 else BLACKT, 3.4 if (y + x) // 3 % 2 else 2.0)
    # la rampa, abaixada fins a terra
    cv.poly(RAMP, IRONR, lambda x, y: 3.4 + (y - 188) * 0.03 - (1.4 if (y - 188) % 4 == 0 else 0) +
            (fbm(x / 6, y / 6, 4) - 0.5) * 0.6)
    cv.line(RAMP[0][0], RAMP[0][1], RAMP[3][0], RAMP[3][1], WARN, 3.6)
    cv.line(RAMP[1][0], RAMP[1][1], RAMP[2][0], RAMP[2][1], WARN, 3.0)
    cv.line(RAMP[3][0], RAMP[3][1], RAMP[2][0], RAMP[2][1], IRONR, 1.6)
    for k in (RAMP[0][0] + 6, RAMP[1][0] - 6):                               # els pistons
        cv.line(k, 184, k + (6 if k > 430 else -6), 196, IRONR, 4.4)
    # la llum de dins es vessa per la rampa
    cv.tint(398, 187, 462, 224, (255, 214, 150), lambda x, y: 0.22 * max(0.0, 1 - (y - 187) / 36))
    shadow(cv, 430, 226, 34, 3, 0.7)


# ─── Composició ─────────────────────────────────────────────────────────────

def bg(cv):
    dust_sky(cv, HOR, sun=SUN)
    hills(cv, HOR)
    canonada(cv, CAN_X, HOR)
    hangars(cv)
    ground(cv)
    cami(cv)
    crane(cv)
    containers(cv)
    barrels(cv)
    panell_preu(cv, 286, 120, post=54)
    shadow(cv, 308, 176, 20, 2, 0.6)
    tauler(cv)
    cantimplora(cv)
    cv.tint(0, 0, W - 1, RH - 1, (240, 200, 140), 0.06)                       # la calitja de pols
    for y in range(RH, H):
        for x in range(W):
            cv.flat(x, y, (0, 0, 0))


PROPS = {}


# ─── Animacions ─────────────────────────────────────────────────────────────

_BASE = []


def _base():
    if not _BASE:
        cv = Canvas(light=LIGHT)
        bg(cv)
        _BASE.append(cv.img)
    return _BASE[0]


def _frames_pols():
    return dust_wind_frames(_base(), 150, 258, n=64, step=10, k=0.55, seed=53)


def _frames_llum():
    return llum_canonada_frames(CAN_X, s=Canvas.S)


def _frames_balisa():
    """La balisa taronja de dalt de la Cantimplora: gira (s'encén i s'apaga a poc a poc)."""
    x, y = 521, int(_hull_top(520)) - 32
    frames = []
    for i in range(10):
        img = Image.new('RGBA', (W * Canvas.S, H * Canvas.S), (0, 0, 0, 0))   # (a la mida de l'art)
        k = max(0.0, math.cos(i / 10 * 2 * math.pi))
        if k > 0.1:
            cv = Canvas(img=img)
            col = mix((150, 70, 20), (255, 190, 80), k)
            for dx in (-1, 0, 1):
                cv.flat(x + dx, y, col)
                cv.flat(x + dx, y + 1, col)
            if k > 0.6:
                for dx, dy in ((-2, 0), (2, 0), (0, -1), (-3, 1), (3, 1)):
                    cv.flat(x + dx, y + dy, (240, 150, 70))
        frames.append(img)
    return frames


ANIMS = {'pols': {'frames': _frames_pols, 'frameDuration': 110},
         'llum_canonada': {'frames': _frames_llum, 'frameDuration': 220},
         'balisa': {'frames': _frames_balisa, 'frameDuration': 120}}


# ─── Geometria (coordenades de 640×360) ─────────────────────────────────────

GEOMETRIA = {
    'things': {
        'cami_granja': {'rect': (0, 198, 40, 258), 'walk': (14, 230)},
        'rampa': {'rect': (396, 116, 464, 226), 'walk': (428, 232)},
        'tauler': {'rect': (42, 94, 130, 205), 'walk': (88, 216)},
        'panell_preu': {'rect': (283, 117, 346, 170), 'walk': (312, 212)},
        'canonada': {'rect': (353, 0, 375, 121), 'walk': (360, 212)},
    },
    'spawns': {'iri': (246, 232), 'vet': (190, 238)},
    'walkable': [(0, 200), (140, 206), (360, 206), (392, 226), (470, 228), (639, 224), (639, 258), (0, 258)],
}
