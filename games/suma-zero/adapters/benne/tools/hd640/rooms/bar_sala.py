"""
El bar La Propina (hd/rooms/bar_sala.py) a 640×360: la mateixa composició ×4/3, dibuixada de nou.
Bar de carretera, dilluns de nit, a la sortida de l'autopista:
  - arrimador de fusta amb veta, paret groguenca de fum vell (més fosca a dalt), terratzo amb tovallons;
  - la llum: el fluorescent groguenc damunt la barra, la tele (blava), l'escurabutxaques i el neó magenta
    «LA PROPINA» a l'aparador, que des de dins es llegeix del revés;
  - el rètol del lema d'en Tomàs, pintat a mà amb pinzell: «AVUI NO ES FIA, DEMÀ SÍ» (Trencaclosques 2.2);
  - la cafetera exprés amb el vaporitzador (el tap, Trencaclosques 2.1), la cervesera, el pot de les propines,
    la caixa registradora i un pernil.
Animació: `bar` (el neó parpelleja, el futbol a la tele, els llums de l'escurabutxaques i els fars dels camions).
Capa del davant (FRONT): la barra tapa de cintura en avall qui hi ha al darrere.
"""
import math
from functools import lru_cache

from PIL import Image, ImageChops

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from hd.pix import Light, Canvas, W, H, hr
from hd.rooms.comu import (obox, outline, text, text_width, _glyph, PLASTIC, SKY, CITY, NEON, SHEET, CARD, RED)
from hd.rooms.pis_cuina import outline_poly
from hd.rooms.bar_sala import (WALLY, WOOD, FORMICA, STEELB, BRASS, TERRAZ, SLATE, PORC, HAM, ENAMEL,  # noqa: F401
                               TVB, PITCH, GLASSD, BOTTLES)

# Art a 2× (1280×720 per a una sala de 640×360): el mateix dibuix, amb les formes, el dither i la llum a la
# resolució real (hd1280/canvas2x.py); el motor el mostra a 1/2 (artScale al .room.json).
ART_SCALE = 2
from hd1280.canvas2x import Canvas2x as Canvas  # noqa: E402,F811

FLOOR_Y = 200
BAR_TOP = 149      # el taulell de la barra: cantell del darrere
BAR_FRONT = 160    # cantell del davant
BAR_X0, BAR_X1 = 133, 560

LAMP_Y = 77
LIGHT = Light(ambient=-0.5, vignette=(80, 45), floor_fade=(256, 35))
LIGHT.point(320, LAMP_Y, r=293, k=3.2, squash=1.3, power=1.5)        # el fluorescent del sostre, damunt la barra
LIGHT.point(487, 85, r=80, k=0.8, squash=1.0, power=2.0)              # la tele
LIGHT.point(111, 147, r=67, k=0.9, squash=1.0, power=2.0)             # l'escurabutxaques
LIGHT.point(145, 53, r=67, k=0.6, squash=1.0, power=2.0)              # el neó de l'aparador

INKP = [(40, 6, 8), (90, 14, 16), (140, 24, 24), (180, 40, 34)]


def fast_diff(frame, base, box=None):
    """Com comu._diff (només els píxels que canvien; la resta, transparent), però amb PIL. `box`: on es mira."""
    out = Image.new('RGBA', frame.size, (0, 0, 0, 0))
    if box is None:
        box = (0, 0) + frame.size
    else:
        s = frame.width // W                                   # la caixa és en píxels de sala (art a 2×)
        box = tuple(v * s for v in box)
    a, b = frame.crop(box), base.crop(box)
    d = ImageChops.difference(a.convert('RGB'), b.convert('RGB')).convert('L').point(lambda v: 255 if v else 0)
    out.paste(a, box[:2], d)
    return out


def paint_text(cv, s, x, y, ramp, lvl, k=2, seed=0, lit=1.0):
    """La font petita, pintada amb pinzell a ×k: cada punt és un toc de k×k amb la vora una mica irregular."""
    cx = x
    for ch in s:
        g, top = _glyph(ch)
        for j, row in enumerate(g, start=top):
            for i, bit in enumerate(row):
                if bit != '1':
                    continue
                for dy in range(k):
                    for dx in range(k):
                        if dx == k - 1 and dy == k - 1 and hr(cx + i, j, seed) > 0.7:
                            continue                           # on el pinzell no ha carregat prou
                        cv.put(cx + i * k + dx, y + j * k + dy, ramp, lvl + (0.5 if dy == 0 else 0), lit)
        cx += (len(g[0]) + 1) * k
    return (text_width(s) + 1) * k - k


def paint_width(s, k=2):
    return (text_width(s) + 1) * k - k


# ─── Paret i terra ──────────────────────────────────────────────────────────

def wall(cv):
    """Paret de guix groguenca (més fosca a dalt, del fum de quan es fumava a dins) i arrimador de fusta."""
    for y in range(0, FLOOR_Y):
        for x in range(W):
            if y >= 131:
                plank = x // 19
                seam = x % 19 == 0
                grain = math.sin(y * 0.9 + hr(plank, 7) * 6 + math.sin(x * 0.4) * 0.6) * 0.25
                knot = 0.6 if hr(plank, (y - 131) // 9, 8) > 0.97 else 0
                cv.put(x, y, WOOD, (1.0 if seam else 2.6 + (hr(plank, 2) - 0.5) * 0.5 + grain - knot)
                       + (0.5 if x % 19 == 1 else 0) + (0.4 if y == 132 else 0))
            else:
                n = (hr(x // 4, y // 4) - 0.5) * 0.3 + (hr(x // 17, y // 13, 5) - 0.5) * 0.5 + (hr(x, y, 6) - 0.5) * 0.12
                cv.put(x, y, WALLY, 2.4 + n - max(0, (40 - y) / 40) * 0.3)
    # una esquerda al guix, a la dreta del rètol
    px, py = 424, 6
    for i in range(22):
        nx, ny = px + (1 if hr(i, 31) > 0.5 else 0), py + 1
        cv.put(nx, ny, WALLY, 1.0)
        px, py = nx, ny
    cv.rect(0, 127, W - 1, 130, WOOD, 3.4)                   # la motllura de l'arrimador
    cv.hline(0, W - 1, 127, WOOD, 4.6)
    cv.hline(0, W - 1, 128, WOOD, 3.8)
    cv.hline(0, W - 1, 130, WOOD, 0.6)
    cv.hline(0, W - 1, 131, WOOD, 1.2)
    cv.rect(0, FLOOR_Y - 5, W - 1, FLOOR_Y - 1, WOOD, 1.4)  # sòcol
    cv.hline(0, W - 1, FLOOR_Y - 5, WOOD, 2.6)
    cv.hline(0, W - 1, FLOOR_Y, WOOD, 0)


def floor(cv):
    """Terratzo gris, gastat, amb tovallons de paper, escuradents i alguna closca de pipa."""
    for y in range(FLOOR_Y + 1, H):
        dep = (y - FLOOR_Y) / (H - FLOOR_Y)
        v = (y - FLOOR_Y) * 1.5 / (1 + dep * 0.6)
        for x in range(W):
            u = (x - W / 2) / (1 + dep * 0.6) + W / 2
            if (u % 53) < 0.9 or (v % 30) < 0.8:
                cv.put(x, y, TERRAZ, 1.2)
                continue
            chip = hr(x, y, 3)
            lvl = 2.8 + (hr(int(u // 53), int(v // 30)) - 0.5) * 0.4
            if chip > 0.94:
                lvl += 1.4
            elif chip < 0.05:
                lvl -= 1.2
            elif chip > 0.9:
                lvl += 0.6
            cv.put(x, y, TERRAZ, lvl)
    # tovallons arrugats, escuradents i pipes (sobretot davant de la barra)
    for i in range(24):
        x = 147 + int(hr(i, 11) * 400)
        y = 214 + int(hr(i, 12) * 44)
        k = hr(i, 13)
        if k > 0.45:
            cv.disc(x, y, 3.2, 1.8, SHEET, lambda nx, ny: 4.2 - ny - nx * 0.5)
            cv.put(x - 1, y, SHEET, 2.4)                         # el plec
            cv.put(x + 1, y - 1, SHEET, 2.6)
        elif k > 0.2:
            cv.line(x, y, x + 5, y + (1 if i % 2 else -1), CARD, 4.0)
        else:
            cv.put(x, y, SLATE, 3.4)
            cv.put(x + 1, y, SHEET, 3.0)
    # el reflex del fluorescent al terra
    cv.tint(187, 208, 453, 266, (230, 220, 160),
            lambda x, y: 0.08 * max(0, 1 - abs(x - 320) / 133) * max(0, 1 - (y - 208) / 58))


# ─── La paret del fons ─────────────────────────────────────────────────────

WIN = (104, 27, 187, 80)


def window(cv, flick=0):
    """L'aparador: fora, la nit i l'autopista; el neó «LA PROPINA» es llegeix del revés."""
    x0, y0, x1, y1 = WIN
    for y in range(y0 + 2, y1 - 1):
        for x in range(x0 + 2, x1 - 1):
            cv.put(x, y, SKY, 0.8 + (y - y0) / 29 + (0.6 if hr(x, y, 41) > 0.996 else 0), lit=0)
    # el talús de l'autopista, la tanca de seguretat i els fanals
    for x in range(x0 + 2, x1 - 1):
        top = 64 - int(4 * math.sin(x / 12))
        for y in range(top, y1 - 1):
            cv.put(x, y, CITY, 1.2 + (0.6 if y == top else 0), lit=0)
    cv.hline(x0 + 2, x1 - 2, 61, CITY, 3.0, lit=0)              # la bionda
    for gx in range(x0 + 4, x1 - 1, 7):
        cv.vline(gx, 61, 64, CITY, 2.4, lit=0)
    for lx in (117, 149, 179):
        cv.vline(lx, 40, 62, CITY, 2.4, lit=0)
        cv.hline(lx, lx + 4, 40, CITY, 2.4, lit=0)
        cv.flat(lx + 4, 41, (250, 200, 120))
        cv.flat(lx + 3, 41, (210, 160, 100))
        cv.glow(lx + 4, 43, 8, (250, 190, 110), 0.4)
    # el neó (vist del revés, des de dins): el tub i, si és encès, un halo ample
    w = text_width('LA PROPINA')
    tx = (x0 + x1 - w) // 2
    on = (255, 120, 200) if flick != 1 else (140, 40, 100)
    if flick != 1:
        cv.glow((x0 + x1) // 2, 50, 36, (255, 90, 200), 0.35)
    text(cv, 'LA PROPINA', tx, 48, NEON, 0, lit=0, mirror=True, flat=on)
    # els suports dels tubs i el transformador penjat
    cv.hline(tx - 2, tx + w + 1, 55, SLATE, 1.6, lit=0)
    cv.rect(tx + w // 2 - 3, 56, tx + w // 2 + 3, 59, SLATE, 1.8, lit=0)
    # marc d'alumini, amb el reflex del vidre
    cv.tint(x0 + 2, y0 + 2, x1 - 2, y1 - 2, (200, 200, 230),
            lambda x, y: 0.06 if 0 <= (x - x0) - (y1 - y) * 0.7 - 50 < 6 else 0)
    for (a, b, c, d) in ((x0, y0, x1, y0 + 2), (x0, y1 - 2, x1, y1), (x0, y0, x0 + 2, y1), (x1 - 2, y0, x1, y1)):
        cv.rect(a, b, c, d, STEELB, 3.4)
    cv.hline(x0, x1, y0, STEELB, 4.6)
    outline(cv, x0 - 1, y0 - 1, x1 + 1, y1 + 1, STEELB)


SIGN = (203, 25, 411, 63)


def sign(cv):
    """El rètol del lema, pintat a mà amb pinzell en una planxa esmaltada, una mica tort i amb dos claus."""
    x0, y0, x1, y1 = SIGN
    pts = [(x0, y0 + 1), (x1, y0 - 1), (x1, y1 - 1), (x0, y1 + 1)]
    cv.poly(pts, ENAMEL, lambda x, y: 3.8 + (hr(x // 5, y // 5) - 0.5) * 0.5 + (hr(x, y, 9) - 0.5) * 0.2
            - (0.8 if (x - x0) < 4 or (x1 - x) < 4 else 0))
    outline_poly(cv, pts, ENAMEL)
    for (x, y) in ((x0 + 7, y0 + 5), (x1 - 7, y0 + 3)):
        cv.disc(x, y, 1.8, 1.8, STEELB, lambda nx, ny: 4.4 - nx - ny)
        cv.put(x + 1, y + 2, WALLY, 0.6)                              # el rovell que regalima del clau
        cv.put(x + 1, y + 3, WALLY, 1.0)
    l1, l2 = 'AVUI NO ES FIA,', 'DEMÀ SÍ'
    paint_text(cv, l1, (x0 + x1 - paint_width(l1)) // 2, y0 + 5, INKP, 2.6, seed=1)
    l2x = (x0 + x1 - paint_width(l2)) // 2 + 8                        # una mica desplaçat: pintat a corre-cuita
    paint_text(cv, l2, l2x, y0 + 23, INKP, 2.0, seed=2)
    for t in range(2):                                                # subratllat amb ràbia (dues passades)
        cv.line(l2x - 3, y0 + 34 + t, l2x + paint_width(l2) + 3, y0 + 33 - t, INKP, 2.4 - t * 0.6)
    cv.put(l2x + paint_width(l2) + 6, y0 + 34, INKP, 2.0)            # una gota de pintura
    cv.put(l2x + paint_width(l2) + 6, y0 + 35, INKP, 1.6)
    # taques de rovell als cantons
    for (x, y) in ((x0 + 3, y1 - 3), (x1 - 4, y1 - 4), (x1 - 3, y0 + 1)):
        cv.disc(x, y, 2.6, 2, [(40, 20, 8), (90, 50, 20), (130, 80, 30)], lambda nx, ny: 1.0 + (nx * nx + ny * ny) * 1.4)


def bottle(cv, x, base, h, w, r, label):
    """Una ampolla: cos, espatlles, coll, tap i (potser) etiqueta, amb el reflex del fluorescent."""
    neck = max(4, h // 3)
    body_top = base - h + neck
    cv.rect(x, body_top, x + w, base - 1, r, lambda xx, yy: 2.2 + (1.2 if xx == x + 1 else 0) - (0.8 if xx == x + w else 0))
    cv.hline(x + 1, x + w - 1, body_top - 1, r, 2.0)                  # les espatlles
    cx = x + w // 2
    cv.rect(cx - 1, base - h + 1, cx + (1 if w > 5 else 0), body_top - 2, r, 2.0)
    cv.rect(cx - 1, base - h, cx + (1 if w > 5 else 0), base - h, [(30, 24, 14), (120, 100, 40), (200, 170, 80)],
            1.6 + hr(x, 5) * 1.2)                                    # el tap
    if label:
        ly = body_top + 3
        cv.rect(x, ly, x + w, ly + 4, ENAMEL, 3.6)
        cv.hline(x + 1, x + w - 1, ly + 2, r, 1.6)
    cv.put(x + 1, body_top + 1, r, 4.4)
    cv.put(x + 1, body_top + 2, r, 3.6)


def shelves(cv):
    """Lleixes amb ampolles darrere la barra, amb un mirall vell (amb la plata picada) al darrere."""
    x0, x1 = 208, 424
    for y in range(72, 128):
        for x in range(x0, x1 + 1):
            pit = 0.9 if hr(x, y, 17) > 0.985 else 0
            cv.put(x, y, GLASSD, 2.2 + (0.8 if (x - y) % 31 < 2 else 0) + (hr(x // 6, y // 6) - 0.5) * 0.3 - pit)
    outline(cv, x0 - 1, 71, x1 + 1, 128, WOOD)
    outline(cv, x0 - 2, 70, x1 + 2, 129, WOOD)
    # dues lleixes
    for sy in (96, 125):
        obox(cv, x0 - 4, sy, x1 + 4, sy + 3, WOOD, 3.4, top=1.0)
        for bx in (x0 + 10, x1 - 10):                                 # les escaires
            cv.poly([(bx - 2, sy + 4), (bx + 2, sy + 4), (bx, sy + 8)], STEELB, 2.4)
    for sy in (96, 125):
        x = x0 + 3
        while x < x1 - 8:
            r = BOTTLES[int(hr(x, sy) * len(BOTTLES))]
            h = 15 + int(hr(x, sy, 2) * 8)
            w = 5 + (1 if hr(x, sy, 3) > 0.6 else 0)
            bottle(cv, x, sy, h, w, r, hr(x, sy, 4) > 0.5)
            x += w + 3 + (4 if hr(x, sy, 5) > 0.8 else 0)
    # el reflex de les ampolles al mirall, a dalt, i el fluorescent que s'hi veu
    cv.tint(x0, 72, x1, 75, (240, 230, 180), lambda x, y: 0.12 * max(0, 1 - abs(x - 320) / 60))


def tv(cv, frame=0):
    """La tele, en un suport a la paret: futbol (els jugadors corren, la pilota va i ve)."""
    x0, y0, x1, y1 = 435, 53, 539, 115
    cv.rect(480, 43, 493, 53, STEELB, 2.4)                          # suport
    cv.hline(480, 493, 43, STEELB, 3.6)
    for sx in (482, 491):
        cv.put(sx, 46, STEELB, 4.6)
    obox(cv, x0, y0, x1, y1, PLASTIC, 1.6)
    cv.hline(x0 + 1, x1 - 1, y0 + 1, PLASTIC, 3.0)
    sx0, sy0, sx1, sy1 = x0 + 4, y0 + 4, x1 - 4, y1 - 8
    for y in range(sy0, sy1 + 1):
        for x in range(sx0, sx1 + 1):
            stripe = ((x + y // 2) // 11) % 2
            cv.put(x, y, PITCH, 2.4 + stripe * 0.5 + (0.2 if (y + frame) % 2 else 0), lit=0)
    mx, my = (sx0 + sx1) // 2, (sy0 + sy1) // 2
    cv.vline(mx, sy0, sy1, PITCH, 5.0, lit=0)                       # la línia del mig
    cv.ring(mx, my, 9, PITCH, 5.0, lit=0, step=8)
    for ax, d in ((sx0, 1), (sx1, -1)):                               # les àrees
        cv.vline(ax + d * 12, my - 12, my + 12, PITCH, 5.0, lit=0)
        cv.hline(min(ax, ax + d * 12), max(ax, ax + d * 12), my - 12, PITCH, 5.0, lit=0)
        cv.hline(min(ax, ax + d * 12), max(ax, ax + d * 12), my + 12, PITCH, 5.0, lit=0)
    for i in range(10):                                               # jugadors (cap i samarreta)
        px = sx0 + 5 + int((hr(i, 1) * (sx1 - sx0 - 10) + math.sin(frame * 0.4 + i) * 4)) % (sx1 - sx0 - 10)
        py = sy0 + 5 + int(hr(i, 2) * (sy1 - sy0 - 10) + math.cos(frame * 0.3 + i * 2) * 1.5)
        col = (230, 40, 40) if i % 2 else (240, 240, 250)
        cv.flat(px, py, (220, 170, 130))
        cv.flat(px, py + 1, col)
        cv.flat(px, py + 2, col)
        cv.flat(px - (frame + i) % 2, py + 3, (30, 30, 30))
    bx = sx0 + 13 + round((math.sin(frame * 0.39) * 0.5 + 0.5) * (sx1 - sx0 - 26))
    cv.flat(bx, sy0 + 16 + (frame % 4), (255, 255, 255))
    cv.rect(sx0 + 1, sy0 + 1, sx0 + 15, sy0 + 6, SLATE, 1.0, lit=0)    # el marcador
    text(cv, '0-0', sx0 + 3, sy0 + 1, PITCH, 0, lit=0, flat=(240, 240, 240))
    cv.rect(x1 - 11, y1 - 5, x1 - 8, y1 - 4, [(40, 200, 80)], 0, lit=0)
    for i in range(3):                                                # els botons de sota
        cv.rect(x0 + 6 + i * 6, y1 - 5, x0 + 9 + i * 6, y1 - 4, PLASTIC, 3.0)
    cv.glow((x0 + x1) // 2, (y0 + y1) // 2, 67, (80, 140, 200), 0.12)


def phone(cv):
    """El telèfon de paret, beix, amb el fil arrissat i la llibreta de números al costat."""
    x0, y0, x1, y1 = 576, 93, 600, 131
    obox(cv, x0, y0, x1, y1, ENAMEL, 3.0)
    cv.hline(x0 + 1, x1 - 1, y0 + 1, ENAMEL, 4.4)
    obox(cv, x0 + 3, y0 + 3, x0 + 9, y1 - 3, ENAMEL, 3.6)          # l'auricular penjat
    cv.disc(x0 + 6, y0 + 6, 3, 2.6, ENAMEL, lambda nx, ny: 4.4 - ny)
    cv.disc(x0 + 6, y1 - 6, 3, 2.6, ENAMEL, lambda nx, ny: 4.4 - ny)
    for j in range(4):                                               # el teclat
        for i in range(3):
            cv.rect(x0 + 13 + i * 3, y0 + 7 + j * 5, x0 + 14 + i * 3, y0 + 8 + j * 5, SLATE, 2.0)
            cv.put(x0 + 13 + i * 3, y0 + 7 + j * 5, SLATE, 3.2)
    cv.rect(x0 + 13, y1 - 7, x1 - 4, y1 - 5, SLATE, 1.6)            # la reixeta del timbre
    for k in range(16):                                               # el fil arrissat
        y = y1 + k * 2
        cv.put(x0 + 4 + (1 if k % 2 else -1), y, SLATE, 2.0)
        cv.put(x0 + 4, y + 1, SLATE, 2.6)
    cv.line(x0 + 4, y1 + 32, x0 + 2, y1 + 40, SLATE, 2.0)
    # un paper amb números de telèfon clavat al costat
    obox(cv, 555, 101, 569, 123, SHEET, 4.2)
    cv.disc(562, 102, 1, 1, RED, 3.6)
    for j in range(6):
        cv.hline(557, 566 - j % 3, 105 + j * 3, [(30, 30, 60), (60, 60, 120)], 1.4)


HAM_PTS = [(563, 13), (573, 13), (581, 48), (573, 59), (560, 53), (557, 32)]


def ham(cv):
    """Un pernil penjat del sostre, amb la cinta, la pota negra i el con de plàstic per a les gotes."""
    cv.vline(568, 0, 13, SLATE, 2.2)
    cv.poly(HAM_PTS, HAM, lambda x, y: 3.2 + (1.0 if x < 564 else 0) - (1.0 if x > 574 else 0)
            + (hr(x // 2, y // 2) - 0.5) * 0.5 + (0.5 if (x + y * 2) % 13 == 0 else 0))
    for (sx, sy) in ((566, 30), (570, 41), (564, 46)):                # el greix que brilla
        cv.put(sx, sy, HAM, 5.2)
        cv.put(sx + 1, sy, HAM, 4.4)
    cv.rect(565, 7, 571, 14, SLATE, 1.4)                             # la pota negra
    cv.put(566, 8, SLATE, 3.4)
    cv.hline(563, 573, 15, RED, 3.0)                                 # la cinta
    cv.poly([(561, 59), (577, 59), (569, 70)], SHEET, lambda x, y: 3.6 - (y - 59) * 0.05)    # el con
    outline_poly(cv, [(561, 59), (577, 59), (569, 70)], SHEET)
    outline_poly(cv, HAM_PTS, HAM)


def wall_stuff(cv):
    """Una bufanda de futbol i una foto signada (d'algú que no coneix ningú)."""
    # bufanda d'un equip que no existeix (groc i verd), sota l'aparador
    for i in range(75):
        x = 108 + i
        y = 85 + int(4 * math.sin(i / 12))
        yel = (i // 8) % 2
        cv.rect(x, y, x, y + 5, [(40, 36, 6), (100, 86, 16), (170, 150, 40), (220, 200, 90)] if yel else
                [(6, 26, 10), (14, 60, 24), (30, 100, 44), (70, 150, 80)], lambda xx, yy: 2.6 + (0.6 if yy == y else 0)
                - (0.6 if yy == y + 5 else 0) + (0.3 if (xx + yy) % 2 else 0))
    for fx in (108, 182):                                                # serrells
        for k in range(5):
            cv.vline(fx + k - (3 if fx > 140 else 0), 92, 98 - k % 2, [(40, 36, 6), (170, 150, 40)], 1.6)
    # foto signada al costat de la porta del rebost
    obox(cv, 91, 88, 115, 117, ENAMEL, 4.0)
    cv.rect(94, 91, 112, 109, [(30, 24, 30), (70, 56, 60), (120, 100, 100), (170, 150, 140)], 2.0)
    cv.disc(103, 99, 4, 4, [(60, 40, 30), (120, 90, 70), (180, 140, 110)], lambda nx, ny: 2.6 - nx * 0.5)
    cv.disc(103, 95, 4, 2, [(20, 16, 14), (50, 36, 30)], 1.4)       # el tupè
    cv.rect(98, 104, 108, 109, [(20, 20, 40), (40, 40, 80)], 1.6)    # la jaqueta
    cv.line(95, 111, 103, 113, [(10, 10, 60), (20, 20, 120)], 1.4)  # la signatura
    cv.line(103, 113, 110, 110, [(10, 10, 60), (20, 20, 120)], 1.4)


DOOR = (24, 72, 85, FLOOR_Y)


def rebost_door(cv):
    """La porta del rebost (i despatx d'en Tomàs), amb el cartell «PRIVAT»."""
    x0, y0, x1, y1 = DOOR
    obox(cv, x0 - 4, y0 - 4, x1 + 4, y1, WOOD, 3.6)
    obox(cv, x0, y0, x1, y1, WOOD, 2.6, top=0.4)
    for (a, b) in ((y0 + 8, 128), (136, y1 - 8)):
        cv.rect(x0 + 7, a, x1 - 7, b, WOOD, lambda x, y: 2.2 + (hr(x // 2, y // 7, 3) - 0.5) * 0.3)
        cv.hline(x0 + 7, x1 - 7, a, WOOD, 1.0)
        cv.vline(x0 + 7, a, b, WOOD, 1.2)
        cv.vline(x1 - 7, a, b, WOOD, 3.4)
        cv.hline(x0 + 7, x1 - 7, b, WOOD, 3.2)
    for hy in (y0 + 12, y1 - 20):                                     # frontisses
        cv.rect(x0 - 1, hy, x0 + 1, hy + 7, BRASS, 2.8)
    cv.disc(x1 - 8, 133, 3, 3, BRASS, lambda nx, ny: 3.6 - nx - ny)
    cv.rect(x1 - 9, 138, x1 - 7, 141, BRASS, 2.2)                     # el forat del pany
    cv.put(x1 - 8, 139, SLATE, 0.6)
    obox(cv, 37, 85, 72, 96, ENAMEL, 4.2)
    text(cv, 'PRIVAT', 55 - text_width('PRIVAT') // 2, 88, [(40, 6, 8), (120, 20, 20), (180, 40, 34)], 2.0)
    cv.darken(x1 + 5, y0, x1 + 9, y1, 0.4)


def exit_door(cv, frame=0):
    """La sortida: porta de vidre amb marc d'alumini, i fora, els fars dels camions que passen."""
    x0, y0, x1, y1 = 608, 64, 639, FLOOR_Y
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, SKY, 0.6 + (y - y0) / 53, lit=0)
    for y in range(y0 + 67, y1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, CITY, 1.0 + (0.6 if y == y0 + 67 else 0), lit=0)
    # un camió que passa (els fars i el llum de posició), segons el fotograma
    fx = x0 + 3 + (frame * 3) % 40
    if fx < x1 - 1:
        cv.hline(fx, min(x1, fx + 4), 123, [(250, 230, 180)], 0, lit=0)
        cv.glow(fx + 2, 123, 8, (250, 220, 160), 0.5)
        if fx - 12 > x0 + 2:
            cv.flat(fx - 12, 120, (230, 120, 40))
    for (a, b, c, d) in ((x0, y0, x1, y0 + 3), (x0, y0, x0 + 3, y1), (x0, 144, x1, 148)):
        cv.rect(a, b, c, d, STEELB, 3.4)
    cv.hline(x0, x1, y0, STEELB, 4.6)
    cv.vline(x0 + 3, y0 + 3, y1, STEELB, 1.6)
    cv.rect(x0 + 8, 128, x0 + 21, 133, [(10, 30, 60), (30, 80, 150), (200, 220, 240)], 1.6, lit=0)   # adhesiu de VISA
    cv.hline(x0 + 9, x0 + 20, 131, [(200, 160, 40)], 0, lit=0)
    cv.rect(x0 + 5, 149, x0 + 6, 171, STEELB, lambda x, y: 5.0 if x == x0 + 5 else 3.4)   # la nansa
    text(cv, 'TIBAR', x0 + 9, 156, STEELB, 0, lit=0, flat=(200, 200, 210))


def slot_machine(cv, frame=0):
    """L'escurabutxaques, al costat del rebost: llums que fan pampallugues i els rodets que giren."""
    x0, y0, x1, y1 = 91, 125, 131, FLOOR_Y + 3
    obox(cv, x0, y0, x1, y1, FORMICA, 2.4, top=0.8)
    cv.rect(x0 + 2, y0 + 2, x1 - 2, y0 + 13, [(30, 10, 40), (80, 20, 100), (160, 50, 180), (230, 120, 240)],
            lambda x, y: 2.6 + (0.6 if (x + frame) % 6 < 2 else 0), lit=0)
    cv.rect(x0 + 8, y0 + 4, x1 - 8, y0 + 10, SLATE, 1.0, lit=0)
    text(cv, 'BONUS', (x0 + x1 - text_width('BONUS')) // 2 + 1, y0 + 5, NEON, 0, lit=0,
         flat=(255, 240, 120) if frame % 2 else (255, 180, 60))
    cols = [(255, 220, 60), (255, 80, 80), (80, 220, 255)]
    for i in range(8):
        on = (i + frame) % 3 == 0
        cv.flat(x0 + 4 + i * 4, y0 + 17, cols[i % 3] if on else (60, 40, 30))
        cv.flat(x0 + 5 + i * 4, y0 + 17, cols[i % 3] if on else (40, 28, 22))
    cv.rect(x0 + 5, y0 + 21, x1 - 5, y0 + 35, SHEET, 4.4, lit=0)     # els rodets
    for i, sym in enumerate((frame % 4, (frame + 1) % 4, (frame + 3) % 4)):
        cx = x0 + 10 + i * 10
        col = [(220, 40, 40), (240, 200, 40), (40, 160, 60), (120, 60, 200)][sym]
        cv.disc(cx, y0 + 28, 2.6, 3.2, [col], 0, lit=0)
        cv.flat(cx - 1, y0 + 26, (255, 255, 255))
        cv.hline(cx - 3, cx + 3, y0 + 22, SHEET, 2.6, lit=0)          # la corba del rodet
        cv.hline(cx - 3, cx + 3, y0 + 34, SHEET, 2.6, lit=0)
    cv.vline(x0 + 15, y0 + 21, y0 + 35, SHEET, 2.0, lit=0)
    cv.vline(x0 + 25, y0 + 21, y0 + 35, SHEET, 2.0, lit=0)
    cv.hline(x0 + 5, x1 - 5, y0 + 28, RED, 3.0, lit=0)               # la línia de premi
    obox(cv, x0 + 4, y0 + 40, x1 - 4, y0 + 48, STEELB, 3.0)          # botons
    for i in range(3):
        c = (255, 200, 60) if (frame + i) % 2 else (200, 60, 40)
        cv.rect(x0 + 9 + i * 10, y0 + 43, x0 + 11 + i * 10, y0 + 45, [c], 0)
    cv.rect(x0 + 15, y0 + 52, x0 + 18, y0 + 56, SLATE, 0.6)          # la ranura de les monedes
    cv.vline(x0 + 16, y0 + 53, y0 + 55, STEELB, 4.0)
    cv.rect(x0 + 10, y1 - 19, x1 - 10, y1 - 10, SLATE, 0.8)          # la safata
    cv.hline(x0 + 10, x1 - 10, y1 - 19, SLATE, 2.6)
    cv.line(x1 + 1, y0 + 19, x1 + 5, y0 + 11, STEELB, 3.0)          # la palanca
    cv.line(x1 + 2, y0 + 19, x1 + 6, y0 + 11, STEELB, 4.2)
    cv.disc(x1 + 5, y0 + 9, 2.2, 2.2, RED, lambda nx, ny: 3.8 - nx - ny)
    cv.glow((x0 + x1) // 2, y0 + 27, 35, (200, 120, 240), 0.14)


# ─── La barra ──────────────────────────────────────────────────────────────

def back_counter(cv):
    """El taulell del darrere: la cafetera exprés (vaporitzador!), la cervesera i la caixa."""
    # la cafetera exprés, a l'esquerra del tap
    x0, x1 = 261, 320
    obox(cv, x0, 115, x1, BAR_TOP, STEELB, 3.4, top=1.0)
    cv.rect(x0 + 2, 117, x1 - 2, 123, RED, lambda x, y: 2.6 + (0.8 if y == 118 else 0))   # la franja vermella
    text(cv, 'GAGGIA', (x0 + x1 - text_width('GAGGIA')) // 2, 118, RED, 0, flat=(240, 220, 200))
    cv.disc(x0 + 8, 128, 3, 3, [(20, 20, 24), (200, 200, 200), (250, 250, 250)], lambda nx, ny: 2.0 - ny)  # manòmetre
    cv.line(x0 + 8, 128, x0 + 9, 126, [(200, 40, 30)], 0)
    for gx in (275, 301):                                              # els dos grups, amb el porta-filtres
        obox(cv, gx - 4, 128, gx + 4, 134, STEELB, 4.4)
        cv.rect(gx - 7, 134, gx + 7, 137, BRASS, lambda x, y: 3.6 + (0.8 if y == 134 else 0))
        cv.line(gx + 7, 136, gx + 13, 138, SLATE, 1.4)               # el mànec
        cv.rect(gx - 1, 137, gx + 1, 141, SLATE, 1.6)
        obox(cv, gx - 3, 142, gx + 3, 148, PORC, 4.4)                  # una tassa a sota
    cv.line(x1 - 3, 125, x1 + 5, 139, STEELB, 5.0)                    # el vaporitzador
    cv.line(x1 - 2, 125, x1 + 6, 139, STEELB, 3.4)
    cv.rect(x1 + 4, 139, x1 + 7, 144, STEELB, 4.0)
    cv.disc(x1 - 3, 125, 2, 2, BRASS, 4.0)                            # la clau del vapor
    for tx in range(x0 + 4, x1 - 5, 8):                               # tasses al damunt, escalfant-se
        obox(cv, tx, 107, tx + 5, 113, PORC, 4.4)
        cv.put(tx + 6, 109, PORC, 3.6)
    # la cervesera (columna amb dos sortidors)
    obox(cv, 224, 125, 240, BAR_TOP, STEELB, 4.4)
    cv.vline(226, 126, BAR_TOP - 1, STEELB, 6.0)
    for tx in (227, 236):
        cv.rect(tx, 113, tx + 2, 125, [(10, 10, 10), (40, 30, 20), (180, 30, 30), (220, 200, 160)], 2.4)
        cv.put(tx, 113, [(220, 200, 160)], 0)
    cv.disc(232, 132, 4, 4, [(80, 10, 10), (180, 40, 30), (240, 200, 120)], lambda nx, ny: 2.4 - ny * 0.4)   # el logo
    cv.ring(232, 132, 4, BRASS, 4.0, step=12)
    # la caixa registradora
    obox(cv, 469, 128, 523, BAR_TOP, PLASTIC, 2.2, top=0.8)
    cv.rect(480, 120, 512, 128, PLASTIC, 2.0)
    cv.rect(483, 121, 509, 127, [(6, 20, 8), (10, 30, 10), (20, 80, 30)], 1.2, lit=0)
    text(cv, '9,20', 489, 122, PITCH, 0, lit=0, flat=(80, 230, 110))
    for j in range(3):
        for i in range(8):
            cv.rect(474 + i * 6, 132 + j * 4, 475 + i * 6, 133 + j * 4, PLASTIC, 4.2 if j < 2 else 3.4)
    cv.rect(471, 145, 521, 148, PLASTIC, 1.4)                         # el calaix
    cv.hline(492, 500, 146, STEELB, 3.6)
    cv.rect(515, 116, 518, 128, SHEET, 4.0)                           # el tiquet que surt


def bar(cv):
    """La barra: fòrmica granat amb el cantell d'alumini, la barana de llautó per als peus i els plafons."""
    x0, x1 = BAR_X0, BAR_X1
    # el taulell, una mica des de dalt, amb el reflex del fluorescent
    cv.poly([(x0, BAR_TOP), (x1, BAR_TOP), (x1 + 3, BAR_FRONT), (x0 - 3, BAR_FRONT)], FORMICA,
            lambda x, y: 3.6 + (y - BAR_TOP) * 0.07 + (0.6 if (x * 3 + y) % 23 == 0 else 0)
            + 0.6 * max(0, 1 - abs(x - 320) / 90) * (1 if y < BAR_TOP + 4 else 0))
    for i in range(6):                                                 # les rodones dels gots
        rx = x0 + 30 + int(hr(i, 51) * (x1 - x0 - 60))
        cv.ring(rx, BAR_TOP + 6, 3, FORMICA, 3.0, step=30)
    cv.rect(x0 - 3, BAR_FRONT, x1 + 3, BAR_FRONT + 3, STEELB, lambda x, y: 4.4 + (0.8 if y == BAR_FRONT else 0))
    cv.hline(x0 - 3, x1 + 3, BAR_FRONT + 4, STEELB, 0)
    # el frontal: plafons de fusta amb motllura
    for x in range(x0, x1 + 1):
        for y in range(BAR_FRONT + 5, 203):
            panel = (x - x0) % 53
            if panel < 2:
                cv.put(x, y, WOOD, 1.2)
            else:
                cv.put(x, y, WOOD, 2.6 + (0.8 if panel < 6 else 0) - (0.6 if panel > 48 else 0)
                       + (hr(x // 2, y // 8) - 0.5) * 0.4 + math.sin(y * 0.7 + x * 0.05 + hr(x // 53, 3) * 9) * 0.15)
    for px in range(x0, x1 - 20, 53):                                   # la motllura de cada plafó
        a, b = px + 9, min(x1, px + 53) - 7
        outline(cv, a, 172, b, 186, WOOD)
        cv.hline(a + 1, b - 1, 173, WOOD, 3.6)
        cv.vline(a + 1, 173, 185, WOOD, 3.4)
    cv.vline(x0, BAR_FRONT, 203, WOOD, 0)
    cv.vline(x1, BAR_FRONT, 203, WOOD, 0)
    # barana de llautó
    cv.rect(x0 + 5, 192, x1 - 5, 194, BRASS, lambda x, y: 3.6 + (1.0 if y == 192 else -0.6 if y == 194 else 0))
    for bx in range(x0 + 27, x1, 80):
        cv.rect(bx, 194, bx + 1, 200, BRASS, 2.6)
        cv.rect(bx - 1, 199, bx + 2, 200, BRASS, 2.0)
    cv.darken(x0 - 3, 203, x1 + 5, 209, lambda x, y: 0.75 - (y - 203) * 0.1)
    # coses damunt la barra: el pot de les propines, el tovalloner, la tassa d'en Marcel, una ampolla buida
    cv.rect(301, 135, 315, BAR_TOP + 2, SHEET, lambda x, y: 1.8 + (1.6 if x == 302 else 0.8 if x == 303 else 0), lit=1.0)
    cv.rect(302, 144, 314, BAR_TOP + 1, BRASS, lambda x, y: 3.0 + (1.2 if hr(x, y, 61) > 0.7 else 0))   # monedes
    cv.rect(304, 141, 309, 143, [(40, 60, 30), (90, 120, 70), (150, 180, 120)], 2.0)   # un bitllet arrugat
    obox(cv, 301, 132, 315, 135, SHEET, 3.0)
    cv.rect(306, 133, 310, 133, SLATE, 0.4)                            # la ranura de la tapa
    obox(cv, 299, 124, 317, 132, ENAMEL, 4.0)                          # cartellet «POT»
    text(cv, 'POT', 308 - text_width('POT') // 2, 126, [(40, 6, 8), (120, 20, 20)], 1.6)
    obox(cv, 408, 139, 424, BAR_TOP + 1, STEELB, 4.0)                  # tovalloner
    for i in range(4):
        cv.hline(411, 421, 134 + i, SHEET, 4.8 - i * 0.3)
    cv.rect(411, 133, 421, 138, SHEET, lambda x, y: 4.6 - (0.6 if x % 3 == 0 else 0))
    obox(cv, 187, 144, 197, BAR_TOP + 2, PORC, 4.4)                    # el cafè amb llet d'en Marcel
    cv.hline(188, 196, 145, [(120, 80, 50), (170, 120, 80)], 1.6)
    cv.line(198, 145, 200, 149, PORC, 3.6)
    cv.disc(192, BAR_TOP + 4, 9, 2, PORC, lambda nx, ny: 3.4 - ny)
    cv.line(196, BAR_TOP + 3, 201, BAR_TOP + 2, STEELB, 4.4)          # la cullereta
    obox(cv, 539, 139, 549, BAR_TOP + 1, BOTTLES[0], 2.4)              # una ampolla de cervesa buida
    cv.rect(541, 131, 547, 139, BOTTLES[0], 2.0)
    cv.vline(540, 140, 147, BOTTLES[0], 4.0)
    cv.rect(539, 142, 549, 145, ENAMEL, 3.4)


STOOLS = (176, 256, 416, 496)


def stools(cv):
    """Tamborets de skai vermell, davant la barra (un amb el seient esquinçat i cinta americana)."""
    for k, x in enumerate(STOOLS):
        cv.rect(x - 1, 187, x + 1, 229, STEELB, lambda xx, yy: 3.2 + (1.0 if xx == x - 1 else 0))
        cv.disc(x, 229, 11, 3, STEELB, lambda nx, ny: 2.6 - ny * 0.8)
        cv.disc(x, 213, 8, 2, STEELB, 1.6)                            # el reposapeus
        cv.disc(x, 212, 8, 1.4, STEELB, 3.6)
        cv.disc(x, 213, 6, 1, STEELB, 1.0)
        cv.disc(x, 184, 13, 4.5, RED, lambda nx, ny: 3.4 - ny * 1.4 - nx * 0.4)
        cv.rect(x - 13, 184, x + 13, 188, RED, lambda xx, yy: 1.8 + (0.4 if yy == 184 else 0))
        cv.disc(x, 184, 13, 3.2, RED, lambda nx, ny: 3.8 - ny * 1.2 - nx * 0.5)
        cv.put(x - 6, 182, RED, 5.4)                                  # el reflex del skai
        cv.put(x - 5, 182, RED, 4.8)
        if k == 2:
            cv.rect(x + 2, 182, x + 8, 184, [(60, 60, 64), (110, 110, 116), (160, 160, 166)], 2.0)   # cinta americana
        cv.darken(x - 12, 230, x + 12, 234, 0.6)


def bg(cv):
    wall(cv)
    floor(cv)
    window(cv)
    sign(cv)
    shelves(cv)
    tv(cv)
    phone(cv)
    ham(cv)
    wall_stuff(cv)
    rebost_door(cv)
    exit_door(cv)
    slot_machine(cv)
    back_counter(cv)
    bar(cv)
    stools(cv)


# ─── Props ──────────────────────────────────────────────────────────────────

def tap_barra(cv):
    """El clauer d'en Tomàs: un tap de la cervesera amb l'anella i dues claus, damunt la barra."""
    cv.disc(343, 153, 7, 3, [(20, 10, 6), (60, 20, 12), (140, 30, 20), (210, 60, 40), (240, 140, 110)],
            lambda nx, ny: 3.2 - ny - nx * 0.5)
    cv.disc(343, 151, 3, 2.4, BRASS, lambda nx, ny: 4.4 - nx - ny)
    cv.put(342, 150, BRASS, 6.0)
    cv.ring(351, 151, 3, STEELB, 5.0, step=20)
    cv.line(352, 149, 355, 145, BRASS, 4.4)                           # una clau de llautó
    cv.put(355, 144, BRASS, 3.6)
    cv.put(356, 145, BRASS, 3.6)
    cv.line(353, 152, 355, 157, STEELB, 5.0)                          # i una d'acer
    cv.put(356, 156, STEELB, 4.0)


COMANDAMENT = [(376, 152), (400, 149), (401, 155), (377, 157)]


def comandament_barra(cv):
    """El comandament de la tele, damunt la barra."""
    cv.poly(COMANDAMENT, PLASTIC, lambda x, y: 2.4 + (0.8 if y < 152 else 0))
    outline_poly(cv, COMANDAMENT, PLASTIC)
    cv.rect(380, 153, 381, 154, [(230, 40, 40)], 0)
    for i in range(6):
        cv.flat(385 + i * 2, 153 + (1 if i % 2 else 0) - i // 3, (120, 120, 130))
    cv.flat(397, 151, (90, 90, 100))


def tele_bassols(cv):
    """A la tele, «La Comissària Bassols»: la comissària de perfil, amb gavardina i cigarreta, i el rètol."""
    sx0, sy0, sx1, sy1 = 439, 57, 535, 107
    for y in range(sy0, sy1 + 1):
        for x in range(sx0, sx1 + 1):
            cv.put(x, y, TVB, 1.8 + (y - sy0) / 40 + (0.2 if y % 2 else 0), lit=0)
    # una finestra amb persiana al fons, i la llum que hi entra
    for y in range(sy0 + 5, sy0 + 27, 3):
        cv.hline(sx0 + 53, sx0 + 85, y, TVB, 4.2, lit=0)
    cv.vline(sx0 + 69, sy0 + 5, sy0 + 26, TVB, 2.4, lit=0)
    # la comissària: gavardina amb solapes, cabell curt gris, perfil
    coat = [(30, 24, 14), (70, 56, 30), (120, 100, 60), (170, 150, 100)]
    cv.poly([(467, 107), (469, 83), (483, 77), (496, 83), (501, 107)], coat,
            lambda x, y: 2.4 + (0.6 if x < 474 else 0), lit=0)
    cv.line(478, 80, 483, 92, coat, 1.2, lit=0)                         # la solapa
    cv.line(488, 80, 484, 92, coat, 1.2, lit=0)
    cv.disc(483, 69, 8, 9, [(60, 30, 20), (130, 80, 60), (200, 150, 120), (230, 190, 160)],
            lambda nx, ny: 2.6 + nx, lit=0)
    cv.disc(480, 63, 9, 5, [(60, 60, 70), (130, 130, 140), (190, 190, 200)], lambda nx, ny: 1.6 - ny * 0.4, lit=0)
    cv.flat(489, 68, (20, 20, 20))
    cv.flat(490, 74, (110, 50, 44))
    cv.rect(489, 75, 497, 75, [(250, 250, 250)], 0, lit=0)             # una cigarreta (és de 1987)
    cv.flat(497, 75, (255, 140, 60))
    for i, (fx, fy) in enumerate(((499, 72), (500, 69), (499, 66))):   # el fum
        cv.put(fx, fy, TVB, 4.6 - i * 0.4, lit=0)
    # el rètol del capítol
    cv.rect(sx0, sy1 - 13, sx1, sy1, SLATE, 1.2, lit=0)
    cv.hline(sx0, sx1, sy1 - 13, [(240, 220, 120)], 0, lit=0)
    text(cv, 'EL VIOLÍ MUT', sx0 + 5, sy1 - 8, TVB, 0, lit=0, flat=(240, 220, 120))


def rebost_tancat(cv):
    """En Tomàs és al rebost discutint amb la seva dona inexistent: «NO MOLESTAR» i llum per sota la porta."""
    cv.line(45, 112, 55, 101, STEELB, 3.0)                              # penjat d'un clau
    cv.line(64, 112, 55, 101, STEELB, 3.0)
    cv.disc(55, 101, 1.4, 1.4, STEELB, 4.4)
    w = text_width('NO MOLESTAR')
    obox(cv, 55 - w // 2 - 3, 112, 55 + w // 2 + 3, 122, ENAMEL, 4.6)
    text(cv, 'NO MOLESTAR', 55 - w // 2, 115, [(40, 6, 8), (120, 20, 20), (200, 40, 34)], 2.4)
    cv.hline(25, 84, FLOOR_Y + 1, [(255, 220, 140)], 0, lit=0)
    cv.hline(27, 82, FLOOR_Y + 2, [(200, 160, 100)], 0, lit=0)
    cv.glow(55, FLOOR_Y + 3, 21, (255, 200, 120), 0.4)


PROPS = {'tap_barra': tap_barra, 'comandament_barra': comandament_barra, 'tele_bassols': tele_bassols,
         'rebost_tancat': rebost_tancat}


# ─── Animació ───────────────────────────────────────────────────────────────

@lru_cache(maxsize=None)
def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv.img


def _frames():
    """16 fotogrames: el neó fa un mal contacte (dos cops), el futbol, l'escurabutxaques i els camions."""
    base = _base()
    frames = []
    for i in range(16):
        cv = Canvas(light=LIGHT, img=base.copy())
        window(cv, flick=1 if i in (10, 12) else 0)
        tv(cv, i)
        slot_machine(cv, i)
        exit_door(cv, i)
        frames.append(fast_diff(cv.img, base, (80, 20, W, FLOOR_Y + 8)))
    return frames


ANIMS = {'bar': {'frames': _frames, 'frameDuration': 220}}


# ─── La barra, per davant del cambrer ──────────────────────────────────────
# Qui és darrere la barra (peus per sobre de y 213) queda tapat de cintura en avall; qui és a la sala, no.
_DAVANT = [(130, 148, 565, 209),      # el taulell, el frontal i la barana
           (299, 124, 317, 151),      # el pot de les propines
           (408, 132, 424, 151),      # el tovalloner
           (183, 141, 202, 155),      # el cafè d'en Marcel
           (539, 130, 549, 151)]      # l'ampolla buida

FRONT = {'mask': lambda x, y: any(x0 <= x <= x1 and y0 <= y <= y1 for x0, y0, x1, y1 in _DAVANT),
         'baseline': 213, 'zIndex': 20, 'props': ('tap_barra', 'comandament_barra')}


# ─── Geometria (coordenades de 640×360) ─────────────────────────────────────

GEOMETRIA = {
    'things': {
        'porta': {'rect': (608, 64, 639, 213), 'walk': (616, 248)},
        'porta_rebost': {'rect': (24, 72, 85, 200), 'walk': (56, 245)},
        'retol': {'rect': (200, 22, 414, 66), 'walk': (307, 248)},
        'tele': {'rect': (435, 53, 539, 115), 'walk': (480, 248)},
        'telefon': {'rect': (573, 91, 603, 134), 'walk': (587, 248)},
        'tap_barra': {'rect': (331, 143, 357, 160), 'walk': (341, 248)},
        'comandament_barra': {'rect': (373, 144, 403, 160), 'walk': (387, 248)},
    },
    'spawns': {'marcel': (176, 229), 'tomas': (400, 184), 'vet': (301, 261)},
    'walkable': [(19, 236), (621, 236), (632, 271), (8, 271)],
}
