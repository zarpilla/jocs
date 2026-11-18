"""
Peces comunes de les sales de Terra-2 (granja_pati, granja_casa, granja_graner, port_terra2, final_pluja).

Terra-2: pols ocre, cel groguenc sense núvols, sol dur a dalt a la dreta (les ombres cauen cap a l'esquerra).
Aquí hi ha les rampes (vénen de la mostra, guio/art/mostra/granja_pati.py), el cel de pols i el de pluja, els
turons, la Canonada, el panell del preu, la gota de Verne, el fang clivellat, les lletres petites i les
animacions comunes (la pols que passa, el llum de la Canonada, les volves de pols als raigs de llum).
"""
import math

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from PIL import Image

from hd.pix import Canvas, W, H, hr, mix, B4
from hd.rooms.exterior import fbm, smooth
from hd.rooms.comu import _diff, text, text_width, _glyph
from pixels import nearest

RH = 260                         # la sala (la barra de verbs va de 260 a 360)

# ─── Rampes (fosc → clar) ───────────────────────────────────────────────────
SKY = [(150, 128, 98), (174, 152, 118), (194, 174, 138), (212, 194, 156), (226, 210, 172), (238, 224, 188),
       (246, 236, 204), (252, 246, 222)]
RSKY = [(70, 74, 80), (88, 92, 98), (106, 110, 116), (124, 128, 132), (142, 146, 148), (160, 164, 164),
        (178, 180, 178), (196, 198, 194)]                                     # el cel de pluja
HILL = [(122, 98, 78), (140, 116, 92), (158, 134, 108), (174, 150, 122), (190, 168, 138), (204, 184, 154)]
RHILL = [(62, 64, 62), (76, 78, 74), (90, 92, 86), (104, 106, 98), (118, 120, 110), (132, 134, 124)]
FIELD = [(70, 48, 30), (96, 68, 42), (122, 90, 56), (148, 112, 72), (170, 134, 90), (192, 156, 110),
         (210, 178, 132), (226, 198, 154)]
EARTH = [(52, 34, 24), (78, 54, 36), (104, 74, 48), (130, 96, 62), (156, 118, 78), (180, 142, 96),
         (202, 166, 118), (220, 190, 142), (234, 210, 166)]
MUD = [(26, 20, 18), (40, 30, 24), (56, 42, 32), (72, 54, 40), (90, 68, 50), (108, 84, 62), (126, 100, 76),
       (146, 120, 92), (168, 142, 112)]                                       # la terra mullada
ADOBE = [(58, 40, 30), (90, 64, 44), (124, 92, 62), (156, 120, 82), (184, 148, 106), (206, 174, 132),
         (224, 198, 158), (238, 218, 182)]
STONE = [(40, 36, 34), (62, 56, 50), (88, 80, 70), (114, 104, 90), (140, 128, 110), (164, 152, 132),
         (188, 178, 156), (210, 202, 182)]
TILE = [(46, 18, 14), (74, 30, 20), (104, 44, 28), (134, 62, 38), (162, 82, 50), (188, 106, 66), (210, 134, 88)]
SHUT = [(20, 34, 26), (30, 52, 38), (44, 72, 52), (62, 94, 68), (84, 116, 86), (110, 138, 106)]
PLANK = [(36, 24, 18), (56, 38, 26), (78, 54, 36), (102, 72, 46), (126, 92, 58), (150, 114, 74), (172, 138, 94)]
GREYW = [(38, 34, 32), (58, 52, 48), (80, 72, 64), (104, 94, 84), (128, 118, 104), (152, 142, 126),
         (176, 166, 148), (198, 190, 172)]                                    # fusta vella, grisa de sol
WHITEP = [(84, 92, 104), (126, 134, 146), (166, 172, 182), (200, 204, 212), (226, 228, 234), (244, 245, 248),
          (254, 254, 255)]
COL = [(150, 150, 150), (176, 176, 174), (198, 196, 192), (216, 214, 208), (232, 230, 224), (244, 242, 236)]
BLUE = [(10, 30, 70), (20, 60, 130), (40, 100, 190), (90, 160, 230), (170, 210, 250)]
BLACKT = [(10, 10, 12), (22, 22, 24), (36, 36, 38), (54, 54, 56), (76, 76, 78)]
LED = [(30, 6, 4), (90, 20, 10), (180, 50, 20), (250, 120, 40), (255, 200, 120)]
LEDG = [(4, 24, 10), (10, 70, 30), (30, 150, 60), (110, 230, 120), (200, 255, 200)]
GRASS = [(70, 58, 30), (100, 86, 44), (132, 116, 62), (164, 146, 84), (194, 176, 110)]
SPROUT = [(20, 40, 18), (36, 70, 28), (60, 104, 40), (96, 140, 60), (140, 180, 90)]
REDT = [(30, 8, 8), (60, 14, 12), (96, 24, 18), (136, 36, 26), (172, 52, 34), (204, 78, 50), (228, 116, 80)]
IRONR = [(20, 16, 16), (36, 30, 28), (54, 46, 42), (76, 66, 60), (100, 90, 82), (128, 118, 108), (160, 150, 138)]
RUSTT = [(30, 14, 12), (58, 26, 18), (92, 42, 24), (128, 62, 32), (164, 88, 44), (196, 122, 64), (220, 156, 96)]
OLIVE = [(22, 26, 14), (36, 42, 22), (52, 60, 32), (70, 80, 44), (90, 102, 58), (112, 124, 74), (138, 150, 96),
         (166, 176, 124)]
ORANGE = [(48, 16, 10), (92, 32, 14), (140, 54, 18), (190, 84, 26), (230, 122, 40), (250, 168, 80),
          (255, 214, 150)]
WARN = [(40, 28, 6), (90, 64, 10), (150, 110, 16), (210, 160, 30), (246, 206, 70), (255, 240, 160)]
CORK = [(56, 34, 20), (92, 60, 34), (128, 88, 52), (160, 116, 70), (188, 144, 92), (210, 170, 116)]
PAPER = [(64, 56, 54), (112, 100, 90), (162, 150, 130), (200, 190, 164), (228, 220, 196), (246, 242, 224),
         (255, 252, 240)]
WATER = [(16, 22, 30), (26, 36, 46), (40, 52, 62), (58, 72, 82), (80, 96, 104), (110, 124, 130),
         (150, 162, 166), (196, 204, 204)]
GLASSJ = [(40, 52, 50), (70, 90, 86), (110, 134, 128), (156, 178, 170), (200, 218, 210), (236, 246, 240)]
CLOTH = [(54, 44, 30), (86, 72, 50), (120, 104, 76), (156, 140, 106), (188, 174, 140), (214, 204, 172),
         (232, 226, 200)]                                                     # tela de sac
STRAW = [(70, 52, 20), (110, 84, 34), (150, 120, 52), (190, 158, 74), (220, 192, 104), (240, 220, 140)]
LIME = [(70, 62, 54), (104, 94, 82), (138, 128, 112), (168, 158, 140), (196, 186, 166), (216, 208, 188),
        (232, 226, 208), (244, 240, 226)]                                     # la calç de les parets de dins
TERRA = [(40, 18, 12), (66, 30, 18), (96, 46, 28), (126, 64, 38), (154, 84, 50), (178, 106, 66), (200, 130, 86),
         (220, 156, 110)]                                                     # rajola de terra cuita

DUST = (236, 214, 168)                   # el color de la pols al sol
SUN = (540, 26)                          # el sol (exteriors)


# ─── Lletres ────────────────────────────────────────────────────────────────

DIG = {
    '0': '111101101101111', '1': '010110010010111', '2': '111001111100111', '3': '111001111001111',
    '4': '101101111001001', '5': '111100111001111', '6': '111100111101111', '7': '111001010010010',
    '8': '111101111101111', '9': '111101111001111',
}


def text2(cv, s, x, y, col):
    """Xifres quadrades a ×2 (les del panell del preu, com una pantalla de LED)."""
    cx = x
    for ch in s:
        if ch in DIG:
            g, top = [DIG[ch][k:k + 3] for k in range(0, 15, 3)], 0
        else:
            g, top = _glyph(ch)
        for j, row in enumerate(g, start=top):
            for i, bit in enumerate(row):
                if bit == '1':
                    for dy in (0, 1):
                        for dx in (0, 1):
                            cv.flat(cx + i * 2 + dx, y + j * 2 + dy, col)
        cx += (len(g[0]) + 1) * 2
    return cx - x - 2


def arrow(cv, x, y, col, up=True, s=1):
    """El triangle del panell (▲ o ▼), de 2·s+1 d'alt."""
    for j in range(2 * s + 1):
        w = j if up else 2 * s - j
        for i in range(-w, w + 1):
            cv.flat(x + i, y + j, col)


def gota(cv, cx, cy, r, lit=0, lvl=2.6):
    """La gota blava de Verne: un cercle amb punta a dalt."""
    cv.disc(cx, cy, r, r, BLUE, lambda nx, ny: lvl - nx * 0.6 - ny * 0.6, lit=lit)
    for k in range(1, int(r * 1.4) + 1):
        w = max(0, int(r * (1 - k / (r * 1.4))) - 0)
        for i in range(-w, w + 1):
            cv.put(cx + i, cy - r + 1 - k, BLUE, lvl + 0.2 - i * 0.3, lit=lit)
    cv.put(cx - max(1, r // 2), cy - max(0, r // 3), BLUE, 4.4, lit=lit)          # la lluentor


# ─── Cel, turons, Canonada ─────────────────────────────────────────────────

def dust_sky(cv, hor, sun=SUN, seed=31):
    """Cel de pols, groguenc, sense ni un núvol; el sol, dur, a dalt a la dreta."""
    for y in range(0, hor + 1):
        t = y / hor
        for x in range(cv.w // cv.S):
            d = math.hypot(x - sun[0], (y - sun[1]) * 1.3)
            lvl = 2.0 + 3.6 * t ** 0.8 + 2.4 * max(0.0, 1 - d / 160) ** 2
            lvl += (fbm(x / 140, y / 18, seed) - 0.5) * 0.7                         # pols en suspensió
            cv.put(x, y, SKY, lvl, lit=0)
    cv.glow(sun[0], sun[1], 30, (255, 250, 228), 0.9)
    cv.disc(sun[0], sun[1], 7, 7, SKY, 7.6, lit=0)


def rain_sky(cv, hor, seed=33):
    """Cel tapat de pluja: núvols baixos i grisos, a bandes, i la cortina de pluja que esborra el fons."""
    for y in range(0, hor + 1):
        t = y / hor
        for x in range(cv.w // cv.S):
            c = fbm(x / 120, y / 14, seed)
            c2 = fbm(x / 40, y / 6, seed + 3)
            lvl = 1.6 + 3.2 * t ** 0.9 + (c - 0.5) * 2.6 + (c2 - 0.5) * 0.9
            lvl += 0.8 * smooth(0.55, 0.75, fbm((x + y * 0.8) / 30, 0, seed + 7)) * t   # les cortines
            cv.put(x, y, RSKY, lvl, lit=0)


def hills(cv, hor, wet=False):
    ramp = RHILL if wet else HILL
    for x in range(cv.w // cv.S):
        h1 = hor - 6 - 12 * fbm(x / 90, 0.3, 7)
        h2 = hor - 2 - 7 * fbm(x / 50, 1.7, 9)
        for y in range(int(h1), hor + 1):
            cv.put(x, y, ramp, 4.4 - (y - h1) * 0.03, lit=0)
        for y in range(int(h2), hor + 1):
            cv.put(x, y, ramp, 3.4 + (fbm(x / 8, y / 4, 3) - 0.5), lit=0)


def canonada(cv, x, hor, wmax=4.4, haze=(230, 214, 180), top=0, station=11):
    """La Canonada de Verne: una columna blanca de l'horitzó fins més amunt del cel, amb anelles i, a dalt,
    un llum vermell (apagat: l'encén l'animació `llum_canonada`)."""
    for y in range(top, hor):
        w = wmax * 0.5 + wmax * 0.5 * (y / hor)
        for xx in range(int(x - w), int(x + w) + 1):
            u = (xx - x) / max(1.0, w)
            lvl = 3.0 + u * 1.5 + (0.9 if y % 13 == 0 else 0) - (0.6 if y % 13 == 1 else 0)   # el sol, a la dreta
            cv.put(xx, y, COL, lvl, lit=0)
    cv.tint(x - 6, top, x + 6, hor, haze, lambda xx, yy: 0.35 - 0.2 * yy / hor)       # la boira de pols
    if station:
        s = station
        cv.rect(x - s, hor - 7, x + s, hor, COL, lambda xx, yy: 2.4 + (xx - x) * 0.06, lit=0)   # l'estació
        cv.rect(x - s, hor - 8, x + s, hor - 8, COL, 4.4, lit=0)
        for k in range(-s + 3, s - 1, 4):
            cv.rect(x + k, hor - 5, x + k + 1, hor - 4, BLACKT, 3.0, lit=0)
    cv.flat(x - 1, 22, (120, 40, 34))


def llum_canonada_frames(x, y=22, n=12, s=1, w=W):
    """El llum d'aviació de dalt de la Canonada: fa pampallugues (dos cops seguits, i espera).
    `s`: píxels de l'art per píxel de sala (Canvas.S de la sala); el llum es dibuixa a 1× i s'amplia. `w`: l'amplada
    de la sala, si és més ampla que la pantalla."""
    frames = []
    for i in range(n):
        img = Image.new('RGBA', (w, H), (0, 0, 0, 0))
        if i in (0, 2):
            p = img.load()
            p[x - 1, y] = (255, 90, 64, 255)                                          # el llum, encès
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):                        # i el halo, en creu
                p[x - 1 + dx, y + dy] = (236, 120, 96, 255)
        frames.append(img if s == 1 else nearest(img, (w * s, H * s)))
    return frames


# ─── El panell del preu ────────────────────────────────────────────────────

def panell_preu(cv, x0, y0, post=22, up=True, brand='VERNE', lit=1.0, w=58):
    """El panell del preu a la vora del camí: una pantalla negra amb la marca a dalt, un gràfic de barres i
    la fletxa (▲) en taronja. Sense xifres: el preu canvia durant el joc i es diu en mirar el panell.
    `brand`: 'VERNE' (la gota blava) o 'VESPER' (el banc, al final: en verd i ▼)."""
    h = 24
    x1, y1 = x0 + w - 1, y0 + h - 1
    cx = (x0 + x1) // 2
    for px_ in (cx - 10, cx + 9):                                                    # els dos peus
        cv.rect(px_, y1 + 1, px_ + 1, y1 + post, IRONR, lambda x, y: 2.4 + (x - px_) * 1.2, lit)
    cv.rect(x0 - 1, y0 - 1, x1 + 1, y1 + 1, IRONR, 1.6, lit)                         # el marc
    cv.rect(x0 - 1, y0 - 1, x1 + 1, y0 - 1, IRONR, 4.0, lit)
    cv.rect(x0, y0, x1, y1, BLACKT, lambda x, y: 1.0 + (0.6 if (x + y) % 7 == 0 else 0), lit=0)
    if brand == 'VERNE':
        cv.rect(x0, y0, x1, y0 + 7, WHITEP, 4.6, lit=0)                              # la franja de la marca
        gota(cv, x0 + 4, y0 + 4, 2)
        text(cv, 'AIGUA VERNE', x0 + 9, y0 + 2, BLUE, 1.0, lit=0, flat=BLUE[1])
        col = LED[3]
    else:
        cv.rect(x0, y0, x1, y0 + 7, [(30, 60, 50), (50, 96, 80), (90, 140, 118), (150, 190, 170)], 1.4, lit=0)
        text(cv, 'AIGUA VESPER', x0 + (w - text_width('AIGUA VESPER')) // 2, y0 + 2, BLUE, 1.0, lit=0, flat=(220, 236, 226))
        col = LEDG[3]
    # sense xifres (el preu canvia durant el joc i es diu en mirar-lo): un gràfic de barres i la fletxa
    n = 7
    bw = 3
    gx = x0 + 6
    for i in range(n):
        f = (i + 1) / n if up else (n - i) / n
        bh = 2 + round(f * 9)
        bx = gx + i * (bw + 1)
        for y in range(y1 - 2 - bh, y1 - 1):
            for x in range(bx, bx + bw):
                cv.flat(x, y, col if i == n - 1 else mix(col, (0, 0, 0), 0.35))
    arrow(cv, x1 - 10, y0 + 11 if up else y0 + 12, col, up=up, s=4)
    for x in range(x0, x1 + 1):                                                      # les línies de la pantalla
        if x % 2 == 0:
            for y in range(y0 + 9, y1, 3):
                o = cv.get(x, y)
                if o[3]:
                    cv.flat(x, y, mix(o, (0, 0, 0), 0.3))
    return (x0 - 1, y0 - 1, x1 + 1, y1 + post)


# ─── Terra ──────────────────────────────────────────────────────────────────

def cracks(x, y, cell=13):
    """Distància a la vora d'una cel·la de Voronoi: el fang sec, clivellat."""
    gx, gy = x // cell, y // cell
    d = []
    for j in (-1, 0, 1):
        for i in (-1, 0, 1):
            cx = (gx + i + hr(gx + i, gy + j, 1)) * cell
            cy = (gy + j + hr(gx + i, gy + j, 2)) * cell
            d.append(math.hypot(x - cx, (y - cy) * 1.8))
    d.sort()
    return d[1] - d[0]


def shadow(cv, cx, cy, rx, ry, k=0.85):
    """Ombra el·líptica, a quadres a les vores."""
    cv.darken(cx - rx - 2, cy - ry - 2, cx + rx + 2, cy + ry + 2,
              lambda x, y: k * min(1.0, 1.6 * (1 - ((x - cx) / rx) ** 2 - ((y - cy) / ry) ** 2))
              if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1 else 0)


def outline(cv, x0, y0, x1, y1, col):
    for x in range(x0, x1 + 1):
        cv.flat(x, y0, col)
        cv.flat(x, y1, col)
    for y in range(y0, y1 + 1):
        cv.flat(x0, y, col)
        cv.flat(x1, y, col)


# ─── Animacions comunes ────────────────────────────────────────────────────

def dust_wind_frames(base, y0, y1, n=64, step=10, seed=51, k=0.5):
    """La pols que passa arran de terra: vels de pols (soroll) que corren cap a l'esquerra, a quadres
    (dithering), sobre el fons `base`. El patró es repeteix cada n·step píxels: el bucle no salta.
    `base` pot ser a la mida de l'art (2×): el dither es fa per píxel real."""
    period = n * step
    s = base.height // H
    BW = base.width // s                                                            # l'amplada de la sala
    src = base.load()
    # el camp de densitat, periòdic en x (soroll mostrejat sobre un cercle), es calcula una sola vegada
    dens = {}
    for y in range(y0, y1):
        fy = (y - y0) / (y1 - y0)
        env = math.sin(math.pi * fy) ** 1.5
        row = []
        for u in range(period):
            a = u / period * 2 * math.pi
            c = fbm(3 + math.cos(a) * 2.2, y / 9 + math.sin(a) * 2.2, seed)
            row.append(smooth(0.52, 0.72, c) * env * k)
        dens[y] = row
    frames = []
    for i in range(n):
        img = Image.new('RGBA', (BW * s, H * s), (0, 0, 0, 0))
        p = img.load()
        off = i * step
        for Y in range(y0 * s, y1 * s):
            row = dens[Y // s]
            b = B4[Y & 3]
            for X in range(BW * s):
                d = row[(X // s + off) % period]
                if d > b[X & 3]:
                    p[X, Y] = mix(src[X, Y], DUST, 0.32 + 0.2 * d) + (255,)
        frames.append(img)
    return frames


def motes_frames(base, beams, n=40, count=60, seed=7, col=(255, 240, 200)):
    """Volves de pols que suren dins els raigs de llum. `beams`: funció (x, y) → 0..1 (dins el raig).
    Cada volva fa una petita òrbita tancada: el bucle no salta. Amb `base` a 2×, cada volva és un bloc de 2×2."""
    s = base.height // H
    BW = base.width // s                                                            # l'amplada de la sala
    src = base.load()
    pts = []
    rnd = 0
    while len(pts) < count and rnd < count * 200:
        rnd += 1
        x, y = hr(seed, rnd, 1) * BW, hr(seed, rnd, 2) * RH
        if beams(x, y) > 0.3:
            pts.append((x, y, hr(seed, rnd, 3) * 2 * math.pi, 3 + hr(seed, rnd, 4) * 8, 2 + hr(seed, rnd, 5) * 5))
    frames = []
    for i in range(n):
        img = Image.new('RGBA', (BW * s, H * s), (0, 0, 0, 0))
        p = img.load()
        a = 2 * math.pi * i / n
        for x0, y0, ph, rx, ry in pts:
            x = round(x0 + math.cos(a + ph) * rx)
            y = round(y0 + math.sin(a * 2 + ph) * ry * 0.5 + math.sin(a + ph) * ry * 0.5)
            if 0 <= x < BW and 0 <= y < RH:
                b = beams(x, y)
                if b > 0.15:
                    for Y in range(y * s, y * s + s):
                        for X in range(x * s, x * s + s):
                            p[X, Y] = mix(src[X, Y], col, 0.35 + 0.45 * b) + (255,)
        frames.append(img)
    return frames
