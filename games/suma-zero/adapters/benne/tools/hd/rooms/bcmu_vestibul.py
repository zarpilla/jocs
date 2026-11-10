"""
El vestíbul del BCMU (Escena 4, la Vet), Ginebra, les nou del matí. Art definitiu:
  - marbre crema amb vetes fins al sostre, pilastres amb capitells de llautó, una cornisa de caoba i un sostre de
    cassetons; el terra, de marbre en escacs, tan polit que hi surt tot reflectit;
  - la porta gran de vidre i llautó (la sortida), amb el matí gris de Ginebra a fora;
  - dues plantes de plàstic en testos de llautó (`planta_retallada`: després d'un Dia de la Marmota, en falta una);
  - la font de marbre seca, amb el rètol «TANCADA PER ESTALVI DE COSTOS»;
  - quadres de banquers importants i el retrat del Director Bonfill amb en Rockefeller a la falda, amb la placa;
  - la pancarta «AQUÍ CONSTRUÏM EL FUTUR DE TOTHOM»;
  - la recepció buida, amb el cartellet «REUNIÓ DE BENESTAR LABORAL» i, al darrere, el logotip del banc;
  - l'estació del tub pneumàtic (la comuna, hd/rooms/bcmu.py);
  - la màquina d'entrepans de luxe (8,50 €; `maquina_forat`: en falta un);
  - l'ascensor de portes daurades, amb l'indicador de plantes d'agulla (animació `ascensor`).
  - la barra de sospita (`sospita` i un tros per cada 5: `sospita_5` … `sospita_95`): un HUD a dalt de tot, sense
    llum de sala, que només es veu mentre la Vet parla amb el Director.
"""
import math

from PIL import Image

from hd.pix import Light, Canvas, W, H, hr, mix
from hd.rooms.comu import obox, outline, text, text_width, _diff, PLASTIC, SHEET
from hd.rooms.pis_cuina import outline_poly
from hd.rooms.bcmu import MARBLE, VEIN, BRASS, MAHOG, NAVYB, CARPET, GLASSB, marble, logo, tub_station
from hd.characters import person
from hd.rooms.proleg_ginebra import BONFILL

FLOOR_Y = 150

CREAM = [(44, 38, 32), (80, 70, 60), (120, 108, 94), (158, 146, 128), (192, 180, 160), (218, 208, 188), (236, 228, 212), (250, 246, 234)]
DARKM = [(10, 10, 14), (20, 20, 26), (32, 32, 40), (46, 46, 56), (62, 62, 72), (80, 80, 92), (102, 102, 112)]
LEAF = [(4, 18, 10), (8, 34, 18), (16, 56, 28), (30, 84, 40), (52, 116, 56), (90, 152, 80), (140, 190, 110)]
DAY = [(60, 70, 84), (90, 102, 116), (124, 136, 150), (160, 172, 184), (196, 204, 212), (226, 232, 236)]
OIL = [(14, 10, 8), (30, 20, 14), (50, 34, 22), (74, 52, 32), (100, 72, 44), (130, 98, 62)]
DOG = [(60, 44, 30), (110, 84, 56), (160, 130, 92), (204, 178, 136), (236, 216, 180), (252, 242, 220)]
BREAD = [(70, 40, 16), (120, 76, 32), (170, 116, 56), (210, 160, 90), (238, 204, 140)]
HUD_INK = (250, 244, 230)

LIGHT = Light(ambient=0.1, vignette=(64, 30), floor_fade=(194, 30))
LIGHT.point(240, -40, r=300, k=2.0, squash=0.6, power=1.3)           # la claraboia (fora de quadre)
for _sx in (91, 178, 244, 375, 419):                                 # els apliques de les pilastres
    LIGHT.point(_sx, 66, r=46, k=0.9, squash=1.2, power=2.0)
LIGHT.point(30, 96, r=70, k=0.8, squash=1.0, power=2.0)              # el matí per la porta de vidre

PILASTERS = (88, 174, 240, 374, 416)


# ─── Paret, sostre, terra ──────────────────────────────────────────────────

def wall(cv):
    """Marbre crema fins a la cornisa; un sòcol de marbre fosc i, a dalt, la caoba i els cassetons."""
    marble(cv, 0, 16, W - 1, FLOOR_Y - 7, 4.4, seed=3)
    for x in range(0, W, 48):                                         # les juntes de les lloses
        cv.vline(x, 16, FLOOR_Y - 7, MARBLE, 3.2)
    for y in (58, 104):
        cv.hline(0, W - 1, y, MARBLE, 3.4)
    # el sòcol de marbre fosc
    cv.rect(0, FLOOR_Y - 6, W - 1, FLOOR_Y - 1, DARKM, lambda x, y: 3.0 + (1.2 if y == FLOOR_Y - 6 else 0))
    # la cornisa de caoba amb un filet de llautó
    cv.rect(0, 9, W - 1, 15, MAHOG, lambda x, y: 3.2 + (1.4 if y == 9 else 0) - (1.0 if y == 15 else 0))
    cv.hline(0, W - 1, 12, BRASS, 3.6)
    # el sostre de cassetons
    for y in range(0, 9):
        for x in range(W):
            cell = (x % 32 in (0, 1)) or y in (0, 8)
            cv.put(x, y, CREAM, (3.0 if cell else 4.6) - y * 0.05)
    # les pilastres
    for px in PILASTERS:
        pilaster(cv, px)


def pilaster(cv, x0):
    """Una pilastra de marbre amb el capitell de llautó i un aplic."""
    x1 = x0 + 6
    marble(cv, x0, 16, x1, FLOOR_Y - 7, 5.2, seed=x0)
    cv.vline(x0, 16, FLOOR_Y - 7, MARBLE, 3.0)
    cv.vline(x1, 16, FLOOR_Y - 7, MARBLE, 2.6)
    obox(cv, x0 - 1, 16, x1 + 1, 20, BRASS, 4.0)
    obox(cv, x0 - 1, FLOOR_Y - 10, x1 + 1, FLOOR_Y - 7, BRASS, 3.2)
    # l'aplic: un braç de llautó i una tulipa de vidre glaçat
    cx = x0 + 3
    cv.rect(cx, 66, cx, 70, BRASS, 4.0)
    cv.disc(cx, 64, 3, 2.4, [(200, 180, 140), (250, 236, 200), (255, 250, 236)], lambda nx, ny: 1.6 - ny, lit=0)
    cv.glow(cx, 63, 14, (255, 230, 170), 0.35)


def floor(cv):
    """Marbre en escacs (crema i gris fosc), en perspectiva."""
    for y in range(FLOOR_Y + 1, H):
        dep = (y - FLOOR_Y) / (H - FLOOR_Y)
        v = (y - FLOOR_Y) * 1.7 / (1 + dep * 0.6)
        for x in range(W):
            u = (x - W / 2) / (0.55 + dep * 0.9) + W / 2
            cu, cvv = int(u // 32), int(v // 14)
            dark = (cu + cvv) % 2 == 1
            seam = (u % 32) < 0.8 or (v % 14) < 0.7
            n = (hr(x // 3, y // 2, 7) - 0.5) * 0.3
            if dark:
                cv.put(x, y, DARKM, (3.4 if seam else 4.9 + n))
            else:
                cv.put(x, y, CREAM, (4.0 if seam else 5.2 + n))


def reflections(cv):
    """El terra polit: s'hi reflecteix tot el que hi ha a sobre, cada cop més esvaït."""
    P = cv.P
    for y in range(FLOOR_Y + 1, min(H, FLOOR_Y + 46)):
        sy = 2 * FLOOR_Y - y
        a = 0.34 * (1 - (y - FLOOR_Y) / 46) ** 1.4
        for x in range(W):
            o, s = P[x, y], P[x, sy]
            P[x, y] = mix(o, s, a) + (255,)
    # la claror del matí de la porta i la de la claraboia
    cv.tint(0, FLOOR_Y + 1, 90, 200, (230, 236, 240), lambda x, y: 0.12 * max(0, 1 - x / 90) * max(0, 1 - (y - 150) / 50))


# ─── La porta gran ─────────────────────────────────────────────────────────

def door(cv):
    """Dues fulles de vidre en un marc de llautó; a fora, el carrer gris de Ginebra."""
    x0, y0, x1, y1 = 6, 40, 56, FLOOR_Y - 1
    for y in range(y0, y1 + 1):                                       # a fora
        for x in range(x0, x1 + 1):
            cv.put(x, y, DAY, 4.2 - (y - y0) / 40, lit=0)
    for x in range(x0, x1 + 1):                                       # la vorera i un fanal
        for y in range(118, y1 + 1):
            cv.put(x, y, DAY, 1.6 + (hr(x // 4, 2) - 0.5) * 0.4, lit=0)
    cv.rect(18, 70, 19, 118, DAY, 0.4, lit=0)
    cv.rect(15, 68, 22, 70, DAY, 0.6, lit=0)
    for i in range(3):                                                # una silueta d'edificis
        bx = x0 + 2 + i * 17
        top = 52 + int(hr(i, 5) * 20)
        cv.rect(bx, top, bx + 12, 117, DAY, 2.6, lit=0)
        for wy in range(top + 3, 114, 6):
            for wx in range(bx + 2, bx + 11, 4):
                cv.flat(wx, wy, (150, 160, 172))
    # el vidre: reflex diagonal
    cv.tint(x0, y0, x1, y1, (240, 246, 250), lambda x, y: 0.22 if (x + y) % 40 < 4 else 0.05)
    # el marc i les barres d'empènyer
    for (a, b, c, d) in ((x0 - 3, y0 - 3, x1 + 3, y0), (x0 - 3, y0, x0, y1), (x1, y0, x1 + 3, y1), (30, y0, 32, y1)):
        cv.rect(a, b, c, d, BRASS, lambda x, y: 4.0 + (1.0 if x == a or y == b else 0))
    outline(cv, x0 - 4, y0 - 4, x1 + 4, y1, BRASS)
    for bx in (16, 40):
        cv.rect(bx, 96, bx + 10, 97, BRASS, 5.2)
    # el travesser de dalt, amb el nom del banc gravat
    obox(cv, x0 - 4, y0 - 14, x1 + 4, y0 - 4, MAHOG, 3.0)
    text(cv, 'BCMU', 31 - text_width('BCMU') // 2, y0 - 11, BRASS, 5.0)
    cv.darken(x0 - 4, y1 - 1, x1 + 4, y1 + 1, 0.4)


# ─── Plantes ───────────────────────────────────────────────────────────────

PLANTS = ((66, 0), (80, 1))   # (centre, varietat)


def plant(cv, cx, kind, sway=None):
    """Un test de llautó amb una planta de plàstic massa verda.

    `sway`: fase (radiants) del corrent de l'aire condicionat que gronxa les fulles del ficus (animació `planta`)."""
    obox(cv, cx - 5, 132, cx + 5, 149, BRASS, 3.4)
    cv.rect(cx - 6, 131, cx + 6, 133, BRASS, 5.0)
    if kind == 0:                                                     # una mena de ficus, alt
        for i in range(26):
            a = hr(i, 1) * math.pi - math.pi
            r = 3 + hr(i, 2) * 9
            lx = cx + math.cos(a) * r * 0.8
            ly = 116 - i * 0.6 + math.sin(a) * r * 0.5
            if sway is not None:                                      # les de dalt es mouen més
                h = min(1.0, max(0.0, (122 - ly) / 16))
                lx += h * (0.9 * math.sin(sway) + 0.25 * math.sin(2 * sway + i * 0.3))
                ly += h * 0.3 * math.cos(sway + i * 0.3)
            cv.disc(lx, ly, 2.6, 1.8, LEAF, lambda nx, ny, k=i: 3.4 - ny + (hr(k, 3) - 0.5))
        cv.line(cx, 130, cx, 104, MAHOG, 3.0)
    else:                                                             # una de fulles llargues (sansevièria)
        for i in range(7):
            bx = cx - 4 + i * 1.4
            h = 18 + hr(i, 4) * 12
            for t in range(int(h)):
                xx = round(bx + math.sin(t / 6 + i) * (t / h) * 2)
                cv.put(xx, 130 - t, LEAF, 3.0 + (t / h) * 1.8 + (0.6 if i % 2 else 0))
                cv.put(xx + 1, 130 - t, LEAF, 2.2 + (t / h) * 1.2)
    cv.darken(cx - 7, 149, cx + 7, 151, 0.4)


# ─── La font seca ──────────────────────────────────────────────────────────

def fountain(cv):
    """Una font de marbre: la pica, la columna amb tres caps de lleó (secs) i el rètol."""
    cx = 133
    # la columna i la tassa de dalt
    marble(cv, cx - 4, 108, cx + 4, 134, 5.0, seed=11)
    outline(cv, cx - 4, 108, cx + 4, 134, MARBLE)
    cv.poly([(cx - 16, 104), (cx + 16, 104), (cx + 10, 112), (cx - 10, 112)], MARBLE, lambda x, y: 5.4 - (y - 104) * 0.25)
    outline_poly(cv, [(cx - 16, 104), (cx + 16, 104), (cx + 10, 112), (cx - 10, 112)], MARBLE)
    cv.disc(cx, 101, 3, 3, BRASS, lambda nx, ny: 4.0 - ny)          # el pom
    for dx in (-7, 0, 7):                                             # els brocs, secs
        cv.disc(cx + dx, 116, 1.8, 1.8, BRASS, 3.4)
        cv.flat(cx + dx, 117, MAHOG[1])
    # la pica gran
    cv.poly([(97, 130), (169, 130), (165, 155), (101, 155)], MARBLE, lambda x, y: 4.6 + (1.2 if y < 133 else 0) - (x - 97) * 0.008)
    outline_poly(cv, [(97, 130), (169, 130), (165, 155), (101, 155)], MARBLE)
    cv.hline(98, 168, 133, MARBLE, 3.0)
    # el fons sec, amb tres monedes
    for k, mx in enumerate((112, 127, 151)):
        cv.flat(mx, 131 + k % 2, (200, 160, 60))
    # el rètol, penjat de la pica
    obox(cv, 98, 136, 168, 151, SHEET, 4.6)
    for k, word in enumerate(('TANCADA PER', 'ESTALVI DE COSTOS')):
        text(cv, word, 133 - text_width(word) // 2, 138 + k * 7, [(130, 20, 24)], 0, flat=(140, 24, 28))
    cv.darken(99, 155, 167, 157, 0.45)


# ─── Els quadres ───────────────────────────────────────────────────────────

def frame(cv, x0, y0, x1, y1):
    """Un marc daurat amb motllura."""
    obox(cv, x0, y0, x1, y1, BRASS, 4.0, top=1.2, side=-1.0)
    obox(cv, x0 + 2, y0 + 2, x1 - 2, y1 - 2, BRASS, 2.8)
    for (a, b) in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
        cv.flat(a, b, BRASS[6])
    cv.darken(x1 + 1, y0 + 2, x1 + 2, y1 + 2, 0.5)


def banker(cv, x0, y0, x1, y1, seed):
    """Un banquer important a l'oli: fons fosc, vestit negre, cara rosada i patilles."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, OIL, 2.4 + (hr(x // 3, y // 3, seed) - 0.5) * 0.5 + (y - y0) * 0.01)
    cx = (x0 + x1) // 2
    cy = y0 + (y1 - y0) // 3
    hw = (x1 - x0) // 2
    cv.poly([(cx - hw + 2, y1), (cx - 6, cy + 9), (cx + 6, cy + 9), (cx + hw - 2, y1)], NAVYB, lambda x, y: 1.6 + (0.8 if x < cx - 3 else 0))
    cv.poly([(cx - 3, cy + 9), (cx + 3, cy + 9), (cx, cy + 16)], [(220, 214, 200), (246, 242, 230)], 1)
    cv.disc(cx, cy + 2, 5, 6.5, [(90, 44, 36), (150, 88, 70), (200, 130, 100), (230, 170, 140)], lambda nx, ny: 2.6 - nx * 0.6 - ny * 0.3)
    hair = [(30, 26, 26), (80, 76, 74), (150, 146, 140), (210, 206, 196)]
    for s in (-1, 1):                                                 # patilles i calba
        cv.rect(cx + s * 5 - (1 if s > 0 else 0), cy - 1, cx + s * 5 + (1 if s > 0 else 0), cy + 5, hair, 2.4)
    cv.flat(cx - 2, cy + 1, (30, 20, 20))
    cv.flat(cx + 2, cy + 1, (30, 20, 20))
    cv.hline(cx - 1, cx + 1, cy + 5, [(120, 50, 50)], 0)
    if seed % 2:
        cv.rect(cx + 4, cy + 18, cx + 6, cy + 22, BRASS, 4.4)         # la cadena del rellotge


def portrait(cv):
    """El retrat del Director Bonfill amb en Rockefeller a la falda, amb la placa."""
    x0, y0, x1, y1 = 184, 26, 236, 82
    frame(cv, x0, y0, x1, y1)
    ix0, iy0, ix1, iy1 = x0 + 4, y0 + 4, x1 - 4, y1 - 4
    for y in range(iy0, iy1 + 1):                                     # fons de cortinatge granat
        for x in range(ix0, ix1 + 1):
            cv.put(x, y, CARPET, 2.2 + math.sin(x * 0.5) * 0.4 + (y - iy0) * 0.01)
    # el Director (el mateix sprite del pròleg), de mig cos
    fig = person(BONFILL, 'D')
    P = fig.load()
    for y in range(29, 40):
        for x in range(22, 28):
            if P[x, y][3]:
                P[x, y] = (230, 230, 236, 255) if abs(x - 24.5) > 1 else ((180, 30, 40, 255) if y > 30 else (210, 50, 50, 255))
    bust = fig.crop((0, 0, fig.width, 58))
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    layer.alpha_composite(bust, ((ix0 + ix1) // 2 - 25, iy0 + 2))
    layer = layer.crop((ix0, iy0, ix1 + 1, iy1 + 1))
    cv.img.alpha_composite(layer, (ix0, iy0))
    # en Rockefeller: un gos petit i pentinat, a la falda, amb llacet
    dx, dy = 210, 64
    cv.disc(dx, dy + 2, 9, 5, DOG, lambda nx, ny: 3.4 - ny * 0.8 + (hr(int(nx * 6), int(ny * 4), 2) - 0.5) * 0.6)
    cv.disc(dx + 6, dy - 3, 5, 4.4, DOG, lambda nx, ny: 3.8 - ny * 0.6 - nx * 0.3)
    cv.disc(dx + 2, dy - 4, 2.2, 3, DOG, 2.4)                         # l'orella
    cv.flat(dx + 7, dy - 4, (20, 14, 14))
    cv.flat(dx + 10, dy - 2, (40, 24, 24))
    cv.rect(dx + 3, dy - 1, dx + 5, dy, [(200, 30, 60), (250, 80, 120)], 1)
    # la placa
    obox(cv, 194, 84, 226, 91, BRASS, 4.6)
    for k in range(3):
        cv.hline(198 + k * 9, 203 + k * 9, 87, BRASS, 2.2)
        cv.hline(198 + k * 9, 201 + k * 9, 89, BRASS, 2.2)


# ─── La pancarta ───────────────────────────────────────────────────────────

def banner(cv):
    """La pancarta blau marí amb lletres d'or, penjada de la cornisa."""
    x0, y0, x1, y1 = 250, 18, 360, 34
    for bx in (254, 356):
        cv.vline(bx, 15, y0, BRASS, 3.6)
    cv.rect(x0, y0, x1, y1, NAVYB, lambda x, y: 3.0 + math.sin(x / 9) * 0.35 + (0.8 if y == y0 else 0))
    outline(cv, x0, y0, x1, y1, NAVYB)
    for k, line in enumerate(('AQUÍ CONSTRUÏM', 'EL FUTUR DE TOTHOM')):
        text(cv, line, 305 - text_width(line) // 2, y0 + 5 + k * 7 - (1 if k == 0 else 0), BRASS, 5.0)
    logo(cv, 262, 25, k=0.9, lvl=4.4)
    logo(cv, 348, 25, k=0.9, lvl=4.4)
    cv.darken(x0 + 2, y1 + 1, x1 + 2, y1 + 2, 0.4)


# ─── La recepció ───────────────────────────────────────────────────────────

def reception(cv):
    """El taulell de caoba amb sobre de marbre; la cadira buida, el cartellet, el timbre i el logotip a la paret."""
    # el logotip gran a la paret, damunt la recepció
    logo(cv, 306, 60, k=3.2, lvl=4.2)
    text(cv, 'B C M U', 306 - text_width('B C M U') // 2, 80, BRASS, 4.6)
    # la cadira buida, girada
    obox(cv, 316, 92, 334, 112, PLASTIC, 2.4)
    cv.rect(318, 94, 332, 110, PLASTIC, 3.0)
    # el taulell
    x0, y0, x1, y1 = 262, 112, 350, FLOOR_Y
    for y in range(y0 + 4, y1 + 1):
        for x in range(x0, x1 + 1):
            panel = (x - x0) % 22 in (0, 1)
            cv.put(x, y, MAHOG, (2.4 if panel else 3.6) + (hr(x, y // 4, 3) - 0.5) * 0.3 - (0.8 if x > x1 - 3 else 0))
    marble(cv, x0 - 3, y0, x1 + 3, y0 + 4, 5.4, seed=21)
    outline(cv, x0 - 3, y0, x1 + 3, y0 + 4, MARBLE)
    outline(cv, x0, y0 + 4, x1, y1, MAHOG)
    logo(cv, 306, 132, k=1.6, lvl=4.6)
    cv.rect(x0, y1 - 3, x1, y1, DARKM, 2.0)
    # el timbre i el cartellet
    cv.disc(270, 110, 3.4, 1.6, BRASS, lambda nx, ny: 4.6 - ny)
    cv.flat(270, 107, BRASS[6])
    obox(cv, 277, 96, 345, 112, SHEET, 5.0)
    for k, word in enumerate(('REUNIÓ DE', 'BENESTAR LABORAL')):
        text(cv, word, 311 - text_width(word) // 2, 101 + k * 6, [(30, 30, 50)], 0, flat=(30, 34, 60))


# ─── La màquina d'entrepans ────────────────────────────────────────────────

MACHINE = (380, 64, 414, 150)
SLOTS = [(386 + c * 9, 74 + r * 15) for r in range(4) for c in range(3)]
EMPTY = 4   # l'espiral que queda buida (fila 2, columna 2)


def machine(cv, empty=(), price=True):
    """Una màquina expenedora de luxe: blau marí i llautó, vitrina amb espirals d'entrepans triangulars i el preu."""
    x0, y0, x1, y1 = MACHINE
    obox(cv, x0, y0, x1, y1, NAVYB, 3.0, top=0.8)
    cv.rect(x0 + 2, y0 + 2, x1 - 2, y0 + 6, BRASS, 4.0)
    text(cv, 'DELI', x0 + 2 + (x1 - x0 - 4 - text_width('DELI')) // 2, y0 + 3, [(30, 20, 10)], 0, flat=(40, 26, 10))
    # la vitrina
    gx0, gy0, gx1, gy1 = x0 + 3, y0 + 8, x1 - 9, y1 - 22
    cv.rect(gx0, gy0, gx1, gy1, NAVYB, 1.2)
    for i, (sx, sy) in enumerate(SLOTS):
        cv.hline(sx - 1, sx + 7, sy + 9, [(160, 166, 176), (200, 206, 214)], 1)       # el prestatge
        for k in range(4):                                                         # l'espiral
            cv.flat(sx + k * 2, sy + 8, (190, 196, 206))
        if i not in empty:
            sandwich(cv, sx, sy)
    cv.tint(gx0, gy0, gx1, gy1, (220, 240, 255), lambda x, y: 0.2 if (x - y) % 26 < 3 else 0.04)
    outline(cv, gx0 - 1, gy0 - 1, gx1 + 1, gy1 + 1, BRASS)
    # el teclat, el preu, la ranura de les monedes
    kx = x1 - 7
    for r in range(5):
        cv.rect(kx, gy0 + 4 + r * 6, kx + 3, gy0 + 7 + r * 6, BRASS, 4.0)
    obox(cv, x0 + 4, y1 - 19, x1 - 4, y1 - 12, [(10, 10, 10), (20, 40, 20)], 0.6, lit=0)
    if price:                                                         # (l'animació `maquina` el fa parpellejar)
        text(cv, '8,50 €', x0 + 7, y1 - 17, [(120, 255, 140)], 0, lit=0, flat=(120, 255, 140))
    cv.rect(x0 + 6, y1 - 9, x1 - 6, y1 - 4, DARKM, 1.4)              # la boca
    cv.glow((x0 + x1) // 2, (gy0 + gy1) // 2, 20, (200, 220, 255), 0.12)
    cv.darken(x1 + 1, y0 + 3, x1 + 3, y1, 0.45)


def sandwich(cv, sx, sy):
    """Un entrepà triangular embolicat, amb una etiqueta daurada."""
    cv.poly([(sx, sy + 7), (sx + 6, sy + 1), (sx + 6, sy + 7)], BREAD, lambda x, y: 3.2 - (y - sy) * 0.1)
    cv.line(sx + 1, sy + 6, sx + 5, sy + 2, [(240, 240, 230)], 0)
    cv.flat(sx + 5, sy + 5, BRASS[5])


# ─── L'ascensor ────────────────────────────────────────────────────────────

ASC = (424, 38, 472, FLOOR_Y - 1)
DIAL = (448, 30)


def elevator(cv, needle=0.0):
    """Portes daurades art déco, amb l'indicador d'agulla a sobre i el botó."""
    x0, y0, x1, y1 = ASC
    obox(cv, x0 - 3, y0 - 3, x1 + 3, y1, MARBLE, 3.0)
    for lx0, lx1 in ((x0, (x0 + x1) // 2), ((x0 + x1) // 2 + 1, x1)):
        cv.rect(lx0, y0, lx1, y1, BRASS, lambda x, y: 3.4 + (0.9 if (x + y) % 12 < 2 else 0) - (0.6 if x in (lx0, lx1) else 0))
        mx = (lx0 + lx1) // 2                                          # el sol art déco
        for a in range(0, 180, 20):
            r = math.radians(a + 180)
            cv.line(mx, 86, round(mx + math.cos(r) * 9), round(86 + math.sin(r) * 9), BRASS, 5.0)
        cv.disc(mx, 86, 3, 3, BRASS, 5.4)
        cv.rect(lx0 + 3, 100, lx1 - 3, 101, BRASS, 2.4)
    cv.vline((x0 + x1) // 2, y0, y1, BRASS, 1.0)
    outline(cv, x0, y0, x1, y1, BRASS)
    dial(cv, needle)
    obox(cv, x1 + 4, 92, x1 + 7, 104, BRASS, 3.4)                     # el botó
    cv.disc(x1 + 5.5, 98, 1.2, 1.2, [(255, 220, 140)], 0, lit=0)


def dial(cv, needle):
    """L'indicador de plantes: un semicercle amb els números i una agulla (needle 0..1, de B a 4)."""
    cx, cy = DIAL
    cv.disc(cx, cy, 11, 9, BRASS, lambda nx, ny: 4.0 - ny * 0.6)
    cv.disc(cx, cy, 9, 7, [(30, 24, 16), (230, 222, 196), (248, 244, 228)], 1.6, lit=0)
    cv.rect(cx - 12, cy, cx + 12, cy + 8, MARBLE, 4.4)
    cv.hline(cx - 11, cx + 11, cy, BRASS, 3.6)
    for k in range(5):
        a = math.radians(180 + k * 45)
        cv.flat(round(cx + math.cos(a) * 7), round(cy + math.sin(a) * 5.4), (60, 40, 20))
    a = math.radians(180 + needle * 180)
    cv.line(cx, cy - 1, round(cx + math.cos(a) * 6), round(cy - 1 + math.sin(a) * 5), [(150, 20, 20)], 0, lit=0)


# ─── Composició ────────────────────────────────────────────────────────────

def bg(cv, plants=(0, 1), empty=(), sway=None, price=True):
    wall(cv)
    door(cv)
    frame(cv, 100, 30, 166, 88)                                       # un banquer gran, damunt la font
    banker(cv, 104, 34, 162, 84, 1)
    frame(cv, 382, 24, 412, 54)                                       # i un de petit, damunt la màquina
    banker(cv, 386, 28, 408, 50, 2)
    portrait(cv)
    banner(cv)
    tub_station(cv, 354, 70, 372, 112)
    elevator(cv)
    reception(cv)
    machine(cv, empty, price)
    floor(cv)
    reflections(cv)
    for i in plants:
        plant(cv, *PLANTS[i], sway=sway)
    fountain(cv)


def _variant(**kw):
    """Els píxels que canvien respecte del fons normal amb una variant de bg (una planta menys, un entrepà menys)."""
    base = Canvas(light=LIGHT)
    bg(base)
    var = Canvas(light=LIGHT)
    bg(var, **kw)
    return _diff(var.img, base.img)


def planta_retallada(cv):
    """Hi falta una planta: el test de les fulles llargues ja no hi és (el marbre de darrere, intacte)."""
    cv.img.alpha_composite(_variant(plants=(0,)))


def maquina_forat(cv):
    """A la màquina li falta un entrepà: una espiral buida."""
    cv.img.alpha_composite(_variant(empty=(EMPTY,)))


# ─── La barra de sospita (HUD) ─────────────────────────────────────────────

BAR = (186, 2, 294, 12)
TRACK = (220, 5, 291, 9)
STEP = 5                                                             # cada resposta mou la sospita de 5 en 5
QUARTS = (25, 50, 75)                                                # els gestos del Director


def _x(value):
    """On acaba la barra plena fins a `value` (0–100)."""
    tx0, _, tx1, _ = TRACK
    return tx0 + round((tx1 - tx0 + 1) * value / 100)


def _color(value):
    """Groc a baix, taronja al mig, vermell a prop del 100."""
    stops = ((0, (250, 210, 60)), (50, (246, 150, 40)), (100, (230, 50, 40)))
    for (v0, c0), (v1, c1) in zip(stops, stops[1:]):
        if value <= v1:
            t = (value - v0) / (v1 - v0)
            return tuple(round(a + (b - a) * t) for a, b in zip(c0, c1))
    return stops[-1][1]


def sospita(cv):
    """La barra buida: plaqueta fosca, l'etiqueta SOSPITA, la guia i les marques dels quarts."""
    x0, y0, x1, y1 = BAR
    cv.rect(x0, y0, x1, y1, [(14, 12, 22)], 0, lit=0)
    outline(cv, x0, y0, x1, y1, [(240, 200, 90)])
    text(cv, 'SOSPITA', x0 + 4, y0 + 3, [HUD_INK], 0, lit=0, flat=HUD_INK)
    tx0, ty0, tx1, ty1 = TRACK
    cv.rect(tx0, ty0, tx1, ty1, [(40, 36, 52)], 0, lit=0)
    outline(cv, tx0 - 1, ty0 - 1, tx1 + 1, ty1 + 1, [(120, 110, 130)])
    for q in QUARTS:
        cv.vline(_x(q) - 1, ty0, ty1, [(90, 84, 100)], 0, lit=0)
    cv.flat(tx1 - 1, ty0 + 2, (200, 40, 40))                         # el 100: el telèfon


def _seg(value):
    """El tros de barra entre `value - 5` i `value`. Als quarts hi deixa una ratlla fosca: s'hi veu el gest."""
    def draw(cv):
        a, b = _x(value - STEP), _x(value) - 1
        col = _color(value)
        tx0, ty0, tx1, ty1 = TRACK
        cv.rect(a, ty0, b, ty1, [col], 0, lit=0)
        cv.hline(a, b, ty0, [tuple(min(255, c + 50) for c in col)], 0, lit=0)
        cv.hline(a, b, ty1, [tuple(int(c * 0.6) for c in col)], 0, lit=0)
        if value in QUARTS:
            cv.vline(b, ty0, ty1, [tuple(int(c * 0.45) for c in col)], 0, lit=0)
    return draw


PROPS = {'sospita': sospita, **{f'sospita_{v}': _seg(v) for v in range(STEP, 100, STEP)},
         'planta_retallada': planta_retallada, 'maquina_forat': maquina_forat}


# ─── Animació: l'agulla de l'ascensor, que va pujant i baixant ────────────

def _frames():
    base = Canvas(light=LIGHT)
    bg(base)
    frames = []
    seq = [0.0, 0.0, 0.0, 0.1, 0.25, 0.5, 0.75, 1.0, 1.0, 1.0, 1.0, 0.9, 0.75, 0.5, 0.25, 0.1]
    for i, n in enumerate(seq):
        cv = Canvas(light=LIGHT, img=base.img.copy())
        dial(cv, n)
        if n in (0.0, 1.0) and i % 4 == 0:                            # «ding»: el botó s'encén un moment
            cv.glow(ASC[2] + 5, 98, 5, (255, 220, 140), 0.7)
        frames.append(_diff(cv.img, base.img))
    return frames


ANIMS = {'ascensor': {'frames': _frames, 'frameDuration': 260}}


# ─── Animacions: el ficus a l'aire condicionat i el preu que parpelleja ────
# No toquen cap píxel dels props (la planta que falta, l'entrepà que falta): els props hi van per sobre.

def _prop_mask():
    """Els píxels que cobreix algun prop de la sala (planta_retallada, maquina_forat)."""
    m = Image.new('L', (W, H), 0)
    for kw in ({'plants': (0,)}, {'empty': (EMPTY,)}):
        m.paste(255, mask=_variant(**kw).getchannel('A').point(lambda a: 255 if a else 0))
    return m


def _anim(variants):
    """Un fotograma per cada variant de bg (kw), amb només el que canvia i fora dels props."""
    base = Canvas(light=LIGHT)
    bg(base)
    hole = _prop_mask()
    frames, cache = [], {}
    for kw in variants:
        key = tuple(sorted(kw.items()))
        if key not in cache:
            cv = Canvas(light=LIGHT)
            bg(cv, **kw)
            f = _diff(cv.img, base.img)
            f.paste((0, 0, 0, 0), mask=hole)
            cache[key] = f
        frames.append(cache[key])
    return frames


def _frames_planta():
    """El corrent de l'aire condicionat gronxa les fulles de dalt del ficus."""
    return _anim([{'sway': i * math.tau / 8} for i in range(8)])


def _frames_maquina():
    """La pantalleta del preu de la màquina parpelleja (dos cops) per cridar l'atenció."""
    return _anim([{}] * 4 + [{'price': False}, {}, {'price': False}, {}])


ANIMS['planta'] = {'frames': _frames_planta, 'frameDuration': 220}
ANIMS['maquina'] = {'frames': _frames_maquina, 'frameDuration': 380}
