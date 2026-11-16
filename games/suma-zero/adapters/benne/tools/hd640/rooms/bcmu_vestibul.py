"""
El vestíbul del BCMU (Escena 4, la Vet), Ginebra, les nou del matí, a 640×360 (hd/rooms/bcmu_vestibul.py
redibuixat a ×4/3):
  - marbre crema amb vetes fins al sostre, pilastres amb capitells de llautó, una cornisa de caoba amb dentells i un
    sostre de cassetons amb roseta; el terra, de marbre en escacs, tan polit que hi surt tot reflectit;
  - la porta gran de vidre i llautó (la sortida), amb el matí gris de Ginebra a fora (edificis, un fanal, un tramvia
    aturat lluny);
  - dues plantes de plàstic en testos de llautó (`planta_retallada`: després d'un Dia de la Marmota, en falta una);
  - la font de marbre seca, amb tres caps de lleó i el rètol «TANCADA PER ESTALVI DE COSTOS»;
  - quadres de banquers importants i el retrat del Director Bonfill amb en Rockefeller a la falda, amb la placa;
  - la pancarta «AQUÍ CONSTRUÏM EL FUTUR DE TOTHOM», amb serrell d'or;
  - la recepció buida, amb el cartellet «REUNIÓ DE BENESTAR LABORAL» i, al darrere, el logotip del banc;
  - l'estació del tub pneumàtic (la comuna, hd640/rooms/bcmu.py);
  - la màquina d'entrepans de luxe (8,50 €; `maquina_forat`: en falta un);
  - l'ascensor de portes daurades, amb l'indicador de plantes d'agulla.
  - la barra de sospita (`sospita` i un tros per cada 5: `sospita_5` … `sospita_95`): un HUD a dalt de tot, sense
    llum de sala, que només es veu mentre la Vet parla amb el Director.
Animacions: `ascensor` (l'agulla puja i baixa, amb el «ding»), `planta` (el ficus a l'aire condicionat) i `maquina`
(el preu parpelleja).
"""
import math

from PIL import Image

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from hd.pix import Light, Canvas, W, H, hr, mix
from hd.rooms.comu import obox, outline, text, text_width, _diff, PLASTIC, SHEET
from hd.rooms.pis_cuina import outline_poly
from hd.rooms.bcmu_vestibul import CREAM, DARKM, LEAF, DAY, OIL, DOG, BREAD, HUD_INK  # noqa: F401
from hd.rooms.proleg_ginebra import BONFILL
from hd640.rooms.bcmu import MARBLE, VEIN, BRASS, MAHOG, NAVYB, CARPET, GLASSB, marble, logo, tub_station  # noqa: F401
from hd640.draw_characters import person

# Art a 2× (1280×720 per a una sala de 640×360): el mateix dibuix, amb les formes, el dither i la llum a la
# resolució real (hd1280/canvas2x.py); el motor el mostra a 1/2 (artScale al .room.json).
ART_SCALE = 2
from hd1280.canvas2x import Canvas2x as Canvas  # noqa: E402,F811
from hd.pix import Canvas as Canvas1x  # noqa: E402,F401  (llenços auxiliars en píxels de sala: figures, textos)

FLOOR_Y = 200

LIGHT = Light(ambient=0.1, vignette=(85, 40), floor_fade=(259, 40))
LIGHT.point(320, -53, r=400, k=2.0, squash=0.6, power=1.3)           # la claraboia (fora de quadre)
for _sx in (121, 236, 324, 503, 559):                                # els apliques de les pilastres
    LIGHT.point(_sx, 88, r=61, k=0.9, squash=1.2, power=2.0)
LIGHT.point(40, 128, r=93, k=0.8, squash=1.0, power=2.0)             # el matí per la porta de vidre

PILASTERS = (117, 232, 320, 499, 555)


# ─── Paret, sostre, terra ──────────────────────────────────────────────────

def wall(cv):
    """Marbre crema fins a la cornisa; un sòcol de marbre fosc i, a dalt, la caoba amb dentells i els cassetons."""
    marble(cv, 0, 21, W - 1, FLOOR_Y - 9, 4.4, seed=3)
    for x in range(0, W, 64):                                         # les juntes de les lloses
        cv.vline(x, 21, FLOOR_Y - 9, MARBLE, 3.2)
        cv.vline(x + 1, 21, FLOOR_Y - 9, MARBLE, 4.9)                 # el cantell que agafa llum
    for y in (77, 139):
        cv.hline(0, W - 1, y, MARBLE, 3.4)
        cv.hline(0, W - 1, y + 1, MARBLE, 4.9)
    # el sòcol de marbre fosc, amb una motllura
    cv.rect(0, FLOOR_Y - 8, W - 1, FLOOR_Y - 1, DARKM,
            lambda x, y: 3.0 + (1.4 if y == FLOOR_Y - 8 else 0) + (0.6 if y == FLOOR_Y - 7 else 0) + (hr(x // 4, y, 31) - 0.5) * 0.3)
    cv.hline(0, W - 1, FLOOR_Y - 5, DARKM, 2.2)
    # la cornisa de caoba amb un filet de llautó i, a sota, els dentells
    cv.rect(0, 12, W - 1, 20, MAHOG, lambda x, y: 3.2 + (1.4 if y == 12 else 0) - (1.0 if y == 20 else 0)
            + (hr(x // 6, y, 17) - 0.5) * 0.25)
    cv.hline(0, W - 1, 16, BRASS, 3.6)
    cv.hline(0, W - 1, 17, BRASS, 2.4)
    for x in range(0, W, 8):
        cv.rect(x, 21, x + 4, 23, MAHOG, lambda xx, yy: 3.0 - (0.9 if xx == x + 4 else 0) - (yy - 21) * 0.3)
    # el sostre de cassetons, amb una roseta a cada un
    for y in range(0, 12):
        for x in range(W):
            u = x % 43
            cell = u in (0, 1, 2) or y in (0, 11)
            lvl = (3.0 if cell else 4.6) - y * 0.04 + (0.5 if u == 3 or y == 1 else 0) - (0.5 if u == 42 or y == 10 else 0)
            cv.put(x, y, CREAM, lvl)
    for x in range(22, W, 43):
        cv.disc(x, 6, 2.2, 2.2, BRASS, lambda nx, ny: 4.2 - ny - nx * 0.4)
    # les pilastres
    for px in PILASTERS:
        pilaster(cv, px)


def pilaster(cv, x0):
    """Una pilastra de marbre amb estries, el capitell i la base de llautó i un aplic."""
    x1 = x0 + 8
    marble(cv, x0, 21, x1, FLOOR_Y - 9, 5.2, seed=x0)
    cv.vline(x0, 21, FLOOR_Y - 9, MARBLE, 3.0)
    cv.vline(x0 + 1, 21, FLOOR_Y - 9, MARBLE, 5.8)
    cv.vline(x1, 21, FLOOR_Y - 9, MARBLE, 2.6)
    for sx in (x0 + 3, x0 + 5):                                       # dues estries
        cv.vline(sx, 32, FLOOR_Y - 20, MARBLE, 4.2)
    obox(cv, x0 - 2, 21, x1 + 2, 27, BRASS, 4.0)
    cv.hline(x0 - 1, x1 + 1, 25, BRASS, 2.8)
    obox(cv, x0 - 1, 28, x1 + 1, 30, BRASS, 3.4)
    obox(cv, x0 - 2, FLOOR_Y - 13, x1 + 2, FLOOR_Y - 9, BRASS, 3.2)
    # l'aplic: una placa, un braç de llautó i una tulipa de vidre glaçat
    cx = x0 + 4
    cv.rect(cx - 1, 92, cx + 1, 97, BRASS, lambda x, y: 4.4 if x == cx - 1 else 3.2)
    cv.disc(cx, 98, 2, 1.4, BRASS, 3.6)
    cv.disc(cx, 86, 4, 4, [(200, 180, 140), (250, 236, 200), (255, 250, 236)], lambda nx, ny: 1.6 - ny, lit=0)
    cv.hline(cx - 3, cx + 3, 90, BRASS, 4.0)
    cv.glow(cx, 84, 19, (255, 230, 170), 0.35)


def floor(cv):
    """Marbre en escacs (crema i gris fosc), en perspectiva, amb vetes fines."""
    for y in range(FLOOR_Y + 1, H):
        dep = (y - FLOOR_Y) / (H - FLOOR_Y)
        v = (y - FLOOR_Y) * 1.7 / (1 + dep * 0.6)
        for x in range(W):
            u = (x - W / 2) / (0.55 + dep * 0.9) + W / 2
            cu, cvv = int(u // 42.67), int(v // 18.67)
            dark = (cu + cvv) % 2 == 1
            seam = (u % 42.67) < 0.8 or (v % 18.67) < 0.7
            n = (hr(x // 4, y // 3, 7) - 0.5) * 0.3 + (hr(x, y, 9) - 0.5) * 0.08
            vein = 0.6 if abs(math.sin(u * 0.05 + v * 0.11 + math.sin(v * 0.06 + cu) * 1.8)) < 0.035 else 0
            if dark:
                cv.put(x, y, DARKM, (3.4 if seam else 4.9 + n + vein * 0.6))
            else:
                cv.put(x, y, CREAM, (4.0 if seam else 5.2 + n - vein))


def reflections(cv):
    """El terra polit: s'hi reflecteix tot el que hi ha a sobre, cada cop més esvaït."""
    P = cv.P
    for y in range(FLOOR_Y + 1, min(H, FLOOR_Y + 61)):
        sy = 2 * FLOOR_Y - y
        a = 0.34 * (1 - (y - FLOOR_Y) / 61) ** 1.4
        for x in range(W):
            o, s = P[x, y], P[x, sy]
            P[x, y] = mix(o, s, a) + (255,)
    # la claror del matí de la porta
    cv.tint(0, FLOOR_Y + 1, 120, 267, (230, 236, 240),
            lambda x, y: 0.12 * max(0, 1 - x / 120) * max(0, 1 - (y - FLOOR_Y) / 67))


# ─── La porta gran ─────────────────────────────────────────────────────────

def door(cv):
    """Dues fulles de vidre en un marc de llautó; a fora, el carrer gris de Ginebra."""
    x0, y0, x1, y1 = 8, 53, 75, FLOOR_Y - 1
    for y in range(y0, y1 + 1):                                       # a fora
        for x in range(x0, x1 + 1):
            cv.put(x, y, DAY, 4.2 - (y - y0) / 53, lit=0)
    for i in range(3):                                                # una silueta d'edificis
        bx = x0 + 3 + i * 23
        top = 69 + int(hr(i, 5) * 27)
        cv.rect(bx, top, bx + 16, 156, DAY, 2.6, lit=0)
        cv.hline(bx, bx + 16, top, DAY, 3.2, lit=0)
        for wy in range(top + 4, 150, 8):
            for wx in range(bx + 3, bx + 14, 5):
                lit_w = hr(wx, wy, 6) > 0.8
                cv.rect(wx, wy, wx + 1, wy + 2, [(150, 160, 172), (220, 200, 150)], 1 if lit_w else 0, lit=0)
    # un tramvia aturat, lluny, i la catenària
    cv.hline(x0, x1, 128, DAY, 1.2, lit=0)
    cv.rect(46, 142, 73, 155, [(40, 70, 110), (70, 110, 150), (130, 160, 190)], 1, lit=0)
    for wx in range(48, 72, 5):
        cv.rect(wx, 144, wx + 3, 148, DAY, 4.0, lit=0)
    cv.line(60, 141, 64, 128, DAY, 0.8, lit=0)
    for x in range(x0, x1 + 1):                                       # la vorera i el carrer
        for y in range(157, y1 + 1):
            cv.put(x, y, DAY, 1.6 + (hr(x // 5, 2) - 0.5) * 0.4 + (0.6 if y == 157 else 0), lit=0)
    cv.rect(24, 93, 25, 157, DAY, 0.4, lit=0)                         # el fanal
    cv.rect(20, 91, 29, 93, DAY, 0.6, lit=0)
    cv.rect(21, 94, 28, 94, [(230, 226, 200)], 0, lit=0)
    # el vidre: reflex diagonal
    cv.tint(x0, y0, x1, y1, (240, 246, 250), lambda x, y: 0.22 if (x + y) % 53 < 5 else (0.1 if (x + y) % 53 == 7 else 0.05))
    # el marc i les barres d'empènyer
    for (a, b, c, d) in ((x0 - 4, y0 - 4, x1 + 4, y0), (x0 - 4, y0, x0, y1), (x1, y0, x1 + 4, y1), (40, y0, 43, y1)):
        cv.rect(a, b, c, d, BRASS, lambda x, y: 4.0 + (1.0 if x == a or y == b else 0) - (0.8 if x == c else 0))
    outline(cv, x0 - 5, y0 - 5, x1 + 5, y1, BRASS)
    for bx in (21, 53):
        cv.disc(bx, 128.5, 1.4, 2, BRASS, 3.0)
        cv.disc(bx + 14, 128.5, 1.4, 2, BRASS, 3.0)
        cv.rect(bx, 128, bx + 14, 129, BRASS, lambda x, y: 5.2 if y == 128 else 3.8)
    # el travesser de dalt, amb el nom del banc gravat
    obox(cv, x0 - 5, y0 - 19, x1 + 5, y0 - 5, MAHOG, 3.0)
    cv.hline(x0 - 3, x1 + 3, y0 - 17, BRASS, 3.0)
    cv.hline(x0 - 3, x1 + 3, y0 - 7, BRASS, 2.4)
    text(cv, 'BCMU', 42 - text_width('BCMU') // 2, y0 - 14, BRASS, 5.0)
    cv.darken(x0 - 5, y1 - 1, x1 + 5, y1 + 1, 0.4)


# ─── Plantes ───────────────────────────────────────────────────────────────

PLANTS = ((88, 0), (107, 1))   # (centre, varietat)


def plant(cv, cx, kind, sway=None):
    """Un test de llautó amb una planta de plàstic massa verda.

    `sway`: fase (radiants) del corrent de l'aire condicionat que gronxa les fulles del ficus (animació `planta`)."""
    obox(cv, cx - 7, 176, cx + 7, 199, BRASS, 3.4)
    cv.rect(cx - 8, 175, cx + 8, 177, BRASS, lambda x, y: 5.0 if y == 175 else 4.2)
    cv.hline(cx - 6, cx + 6, 190, BRASS, 2.6)                          # una franja gravada
    cv.vline(cx - 5, 179, 197, BRASS, 4.8)
    if kind == 0:                                                     # una mena de ficus, alt
        cv.line(cx, 173, cx, 139, MAHOG, 3.0)
        cv.line(cx + 1, 160, cx + 6, 150, MAHOG, 2.6)
        for i in range(40):
            a = hr(i, 1) * math.pi - math.pi
            r = 4 + hr(i, 2) * 12
            lx = cx + math.cos(a) * r * 0.8
            ly = 155 - i * 0.52 + math.sin(a) * r * 0.5
            if sway is not None:                                      # les de dalt es mouen més
                h = min(1.0, max(0.0, (163 - ly) / 21))
                lx += h * (1.2 * math.sin(sway) + 0.35 * math.sin(2 * sway + i * 0.3))
                ly += h * 0.4 * math.cos(sway + i * 0.3)
            cv.disc(lx, ly, 3.4, 2.3, LEAF, lambda nx, ny, k=i: 3.4 - ny + (hr(k, 3) - 0.5) + (0.8 if abs(ny) < 0.2 and nx < 0 else 0))
    else:                                                             # una de fulles llargues (sansevièria)
        for i in range(9):
            bx = cx - 5 + i * 1.3
            h = 24 + hr(i, 4) * 16
            for t in range(int(h)):
                xx = round(bx + math.sin(t / 8 + i) * (t / h) * 2.7)
                band = 0.5 if (t + i * 3) % 9 < 2 else 0                # les franges de la sansevièria
                cv.put(xx, 173 - t, LEAF, 3.0 + (t / h) * 1.8 + (0.6 if i % 2 else 0) - band)
                cv.put(xx + 1, 173 - t, LEAF, 2.2 + (t / h) * 1.2)
    cv.darken(cx - 9, 199, cx + 9, 201, 0.4)


# ─── La font seca ──────────────────────────────────────────────────────────

def fountain(cv):
    """Una font de marbre: la pica, la columna amb tres caps de lleó (secs) i el rètol."""
    cx = 177
    # la columna i la tassa de dalt
    marble(cv, cx - 5, 144, cx + 5, 179, 5.0, seed=11)
    cv.vline(cx - 4, 145, 178, MARBLE, 5.8)
    outline(cv, cx - 5, 144, cx + 5, 179, MARBLE)
    cup = [(cx - 21, 139), (cx + 21, 139), (cx + 13, 149), (cx - 13, 149)]
    cv.poly(cup, MARBLE, lambda x, y: 5.4 - (y - 139) * 0.19)
    outline_poly(cv, cup, MARBLE)
    cv.hline(cx - 20, cx + 20, 140, MARBLE, 6.2)
    cv.disc(cx, 134, 4, 4, BRASS, lambda nx, ny: 4.0 - ny - nx * 0.3)  # el pom
    cv.flat(cx - 1, 132, BRASS[6])
    for dx in (-9, 0, 9):                                             # els caps de lleó, secs
        cv.disc(cx + dx, 155, 3, 3, BRASS, lambda nx, ny: 3.6 - ny * 0.8 - nx * 0.3)
        cv.flat(cx + dx - 1, 154, MAHOG[1])
        cv.flat(cx + dx + 1, 154, MAHOG[1])
        cv.rect(cx + dx - 1, 157, cx + dx + 1, 157, [MAHOG[1]], 0)
        cv.line(cx + dx, 158, cx + dx, 160, [(120, 108, 80)], 0)        # la taca de calç
    # la pica gran
    basin = [(129, 173), (225, 173), (220, 207), (135, 207)]
    cv.poly(basin, MARBLE, lambda x, y: 4.6 + (1.2 if y < 177 else 0) - (x - 129) * 0.006)
    outline_poly(cv, basin, MARBLE)
    cv.hline(130, 224, 177, MARBLE, 3.0)
    cv.hline(130, 224, 174, MARBLE, 6.0)
    # el fons sec, amb tres monedes
    for k, mx in enumerate((149, 169, 201)):
        cv.flat(mx, 175 + k % 2, (200, 160, 60))
        cv.flat(mx + 1, 175 + k % 2, (150, 110, 40))
    # el rètol, penjat de la pica
    obox(cv, 131, 181, 224, 201, SHEET, 4.6)
    for tx in (134, 221):                                             # els trossos de cinta
        cv.rect(tx - 2, 180, tx + 2, 183, [(200, 196, 180), (230, 226, 210)], 1.0)
    for k, word in enumerate(('TANCADA PER', 'ESTALVI DE COSTOS')):
        text(cv, word, 177 - text_width(word) // 2, 184 + k * 9, [(130, 20, 24)], 0, flat=(140, 24, 28))
    cv.darken(132, 207, 223, 209, 0.45)


# ─── Els quadres ───────────────────────────────────────────────────────────

def frame(cv, x0, y0, x1, y1):
    """Un marc daurat amb motllura (a 640: cinc píxels, amb un filet fosc a dins)."""
    obox(cv, x0, y0, x1, y1, BRASS, 4.0, top=1.2, side=-1.0)
    obox(cv, x0 + 2, y0 + 2, x1 - 2, y1 - 2, BRASS, 2.8)
    cv.rect(x0 + 3, y0 + 3, x1 - 3, y0 + 3, BRASS, 4.6)
    outline(cv, x0 + 4, y0 + 4, x1 - 4, y1 - 4, BRASS)
    for (a, b) in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
        cv.flat(a, b, BRASS[6])
    cv.darken(x1 + 1, y0 + 3, x1 + 3, y1 + 3, 0.5)
    cv.darken(x0 + 3, y1 + 1, x1, y1 + 2, 0.35)


def banker(cv, x0, y0, x1, y1, seed):
    """Un banquer important a l'oli: fons fosc, vestit negre, cara rosada i patilles."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, OIL, 2.4 + (hr(x // 4, y // 4, seed) - 0.5) * 0.5 + (hr(x, y, seed + 3) - 0.5) * 0.15 + (y - y0) * 0.008)
    cx = (x0 + x1) // 2
    cy = y0 + (y1 - y0) // 3
    hw = (x1 - x0) // 2
    cv.glow(cx, cy, hw, (120, 80, 50), 0.12)                           # el clarobscur
    cv.poly([(cx - hw + 3, y1), (cx - 8, cy + 12), (cx + 8, cy + 12), (cx + hw - 3, y1)], NAVYB,
            lambda x, y: 1.6 + (0.8 if x < cx - 4 else 0))
    cv.poly([(cx - 4, cy + 12), (cx + 4, cy + 12), (cx, min(y1, cy + 21))], [(220, 214, 200), (246, 242, 230)], 1)
    cv.line(cx, cy + 13, cx, min(y1, cy + 19), [(90, 20, 26)], 0)       # la corbata, fosca
    cv.disc(cx, cy + 3, 6.7, 8.7, [(90, 44, 36), (150, 88, 70), (200, 130, 100), (230, 170, 140)],
            lambda nx, ny: 2.6 - nx * 0.6 - ny * 0.3)
    cv.flat(cx - 3, cy - 4, (240, 190, 160))                          # la llum a la calba
    hair = [(30, 26, 26), (80, 76, 74), (150, 146, 140), (210, 206, 196)]
    for s in (-1, 1):                                                 # patilles
        for k in range(9):
            xx = cx + s * 7 - (0 if s < 0 else 1)
            cv.put(xx, cy - 1 + k, hair, 2.4 + (0.4 if k % 2 else 0))
            cv.put(xx + 1, cy - 1 + k, hair, 1.8 + (0.4 if k % 2 else 0))
    for ex in (cx - 3, cx + 2):
        cv.flat(ex, cy + 2, (30, 20, 20))
        cv.flat(ex + 1, cy + 2, (30, 20, 20))
        cv.flat(ex, cy, (80, 50, 40))
        cv.flat(ex + 1, cy, (80, 50, 40))
    cv.flat(cx, cy + 4, (150, 80, 60))                                # el nas
    cv.hline(cx - 2, cx + 1, cy + 7, [(120, 50, 50)], 0)
    if seed % 2:
        cv.line(cx + 5, cy + 24, cx + 8, cy + 28, BRASS, 4.4)           # la cadena del rellotge
        cv.line(cx + 5, cy + 25, cx + 8, cy + 29, BRASS, 3.0)


def _f(u):
    """Coordenada de la figura de 480 (49×87) → de la de 640."""
    return (u + 0.5) * 4 / 3 - 0.5


def portrait(cv):
    """El retrat del Director Bonfill amb en Rockefeller a la falda, amb la placa."""
    x0, y0, x1, y1 = 245, 35, 315, 109
    frame(cv, x0, y0, x1, y1)
    ix0, iy0, ix1, iy1 = x0 + 5, y0 + 5, x1 - 5, y1 - 5
    for y in range(iy0, iy1 + 1):                                     # fons de cortinatge granat
        for x in range(ix0, ix1 + 1):
            cv.put(x, y, CARPET, 2.2 + math.sin(x * 0.375) * 0.4 + (y - iy0) * 0.008 + (hr(x, y // 3, 4) - 0.5) * 0.15)
    # el Director (el mateix sprite del pròleg), de mig cos, amb camisa blanca i corbata vermella
    fig = person(BONFILL, 'D')
    P = fig.load()
    xa, xb, ya, yb = math.ceil(_f(21.5)), math.floor(_f(27.5)), math.ceil(_f(28.5)), math.floor(_f(39.5))
    mid = _f(24.5)
    for y in range(ya, yb + 1):
        for x in range(xa, xb + 1):
            if P[x, y][3]:
                P[x, y] = (230, 230, 236, 255) if abs(x - mid) > 1.4 else ((180, 30, 40, 255) if y > _f(30) else (210, 50, 50, 255))
    bust = fig.crop((0, 0, fig.width, 77))
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    layer.alpha_composite(bust, ((ix0 + ix1) // 2 - 33, iy0 + 3))
    layer = layer.crop((ix0, iy0, ix1 + 1, iy1 + 1))
    cv.blit(layer, (ix0, iy0))
    # en Rockefeller: un gos petit i pentinat, a la falda, amb llacet
    dx, dy = 280, 85
    cv.disc(dx, dy + 3, 12, 6.7, DOG, lambda nx, ny: 3.4 - ny * 0.8 + (hr(int(nx * 9), int(ny * 6), 2) - 0.5) * 0.7)
    cv.disc(dx - 12, dy, 2.4, 2.4, DOG, lambda nx, ny: 3.6 - ny)       # la cua, un pompó
    cv.disc(dx + 8, dy - 4, 6.7, 5.9, DOG, lambda nx, ny: 3.8 - ny * 0.6 - nx * 0.3 + (hr(int(nx * 7), int(ny * 6), 5) - 0.5) * 0.5)
    cv.disc(dx + 3, dy - 5, 2.9, 4, DOG, lambda nx, ny: 2.4 - ny * 0.4)  # l'orella
    cv.flat(dx + 9, dy - 5, (20, 14, 14))
    cv.flat(dx + 9, dy - 6, (240, 230, 220))
    cv.flat(dx + 13, dy - 3, (40, 24, 24))
    cv.flat(dx + 14, dy - 3, (40, 24, 24))
    cv.rect(dx + 4, dy - 1, dx + 7, dy + 1, [(200, 30, 60), (250, 80, 120)], lambda x, y: 1 if x in (dx + 4, dx + 7) else 0)
    # la placa, amb el nom
    obox(cv, 259, 112, 301, 122, BRASS, 4.6)
    s = 'BONFILL'
    text(cv, s, 280 - text_width(s) // 2, 115, [(70, 48, 18)], 0, flat=(70, 48, 18))
    for (rx, ry) in ((261, 117), (299, 117)):
        cv.flat(rx, ry, BRASS[2])


# ─── La pancarta ───────────────────────────────────────────────────────────

def banner(cv):
    """La pancarta blau marí amb lletres d'or i serrell, penjada de la cornisa."""
    x0, y0, x1, y1 = 333, 24, 477, 49
    for bx in (339, 471):
        cv.vline(bx, 20, y0, BRASS, 3.6)
        cv.vline(bx + 1, 20, y0, BRASS, 2.4)
    cv.rect(x0, y0, x1, y1, NAVYB, lambda x, y: 3.0 + math.sin(x / 12) * 0.35 + (0.8 if y == y0 + 1 else 0))
    outline(cv, x0, y0, x1, y1, NAVYB)
    cv.hline(x0 + 2, x1 - 2, y0 + 2, BRASS, 3.0)
    cv.hline(x0 + 2, x1 - 2, y1 - 2, BRASS, 3.0)
    for k, line in enumerate(('AQUÍ CONSTRUÏM', 'EL FUTUR DE TOTHOM')):
        text(cv, line, 405 - text_width(line) // 2, y0 + 7 + k * 9, BRASS, 5.0)
    logo(cv, 349, 37, k=1.2, lvl=4.4)
    logo(cv, 461, 37, k=1.2, lvl=4.4)
    for x in range(x0 + 1, x1, 2):                                    # el serrell
        cv.put(x, y1 + 1, BRASS, 3.6 + (0.6 if x % 4 == 1 else 0))
        if x % 4 == 1:
            cv.put(x, y1 + 2, BRASS, 2.8)
    cv.darken(x0 + 2, y1 + 3, x1 + 2, y1 + 4, 0.4)


# ─── La recepció ───────────────────────────────────────────────────────────

def reception(cv):
    """El taulell de caoba amb sobre de marbre; la cadira buida, el cartellet, el timbre i el logotip a la paret."""
    # el logotip gran a la paret, damunt la recepció
    logo(cv, 408, 80, k=4.27, lvl=4.2)
    text(cv, 'B C M U', 408 - text_width('B C M U') // 2, 106, BRASS, 4.6)
    # la cadira buida, girada
    obox(cv, 421, 123, 445, 149, PLASTIC, 2.4)
    cv.rect(424, 126, 442, 147, PLASTIC, lambda x, y: 3.0 + (0.5 if x == 424 else 0) - (0.6 if x > 440 else 0))
    cv.vline(433, 127, 146, PLASTIC, 2.4)                             # la costura
    # el taulell
    x0, y0, x1, y1 = 349, 149, 467, FLOOR_Y
    for y in range(y0 + 5, y1 + 1):
        for x in range(x0, x1 + 1):
            u = (x - x0) % 29
            panel = u in (0, 1)
            cv.put(x, y, MAHOG, (2.4 if panel else 3.6) + (0.5 if u == 2 else 0) + (hr(x, y // 5, 3) - 0.5) * 0.3
                   + (hr(x // 2, y // 9, 8) - 0.5) * 0.15 - (0.8 if x > x1 - 4 else 0))
    marble(cv, x0 - 4, y0, x1 + 4, y0 + 5, 5.4, seed=21)
    cv.hline(x0 - 3, x1 + 3, y0 + 1, MARBLE, 6.2)
    outline(cv, x0 - 4, y0, x1 + 4, y0 + 5, MARBLE)
    outline(cv, x0, y0 + 5, x1, y1, MAHOG)
    logo(cv, 408, 176, k=2.13, lvl=4.6)
    cv.rect(x0, y1 - 4, x1, y1, DARKM, lambda x, y: 2.0 + (0.8 if y == y1 - 4 else 0))
    # el timbre i el cartellet
    cv.disc(360, 146, 4.5, 2.1, BRASS, lambda nx, ny: 4.6 - ny - nx * 0.4)
    cv.rect(359, 142, 360, 143, BRASS, 5.4)
    cv.flat(358, 145, BRASS[6])
    obox(cv, 369, 128, 460, 149, SHEET, 5.0)
    cv.hline(370, 459, 148, SHEET, 3.6)
    for k, word in enumerate(('REUNIÓ DE', 'BENESTAR LABORAL')):
        text(cv, word, 414 - text_width(word) // 2, 134 + k * 8, [(30, 30, 50)], 0, flat=(30, 34, 60))


# ─── La màquina d'entrepans ────────────────────────────────────────────────

MACHINE = (507, 85, 552, 200)
SLOTS = [(513 + c * 10, 98 + r * 18) for r in range(4) for c in range(3)]
EMPTY = 4   # l'espiral que queda buida (fila 2, columna 2)


def machine(cv, empty=(), price=True):
    """Una màquina expenedora de luxe: blau marí i llautó, vitrina amb espirals d'entrepans triangulars i el preu."""
    x0, y0, x1, y1 = MACHINE
    obox(cv, x0, y0, x1, y1, NAVYB, 3.0, top=0.8)
    cv.vline(x0 + 1, y0 + 2, y1 - 1, NAVYB, 4.0)
    cv.rect(x0 + 3, y0 + 3, x1 - 3, y0 + 9, BRASS, lambda x, y: 4.0 + (0.8 if y == y0 + 3 else 0))
    text(cv, 'DELI', x0 + 3 + (x1 - x0 - 6 - text_width('DELI')) // 2, y0 + 4, [(30, 20, 10)], 0, flat=(40, 26, 10))
    # la vitrina
    gx0, gy0, gx1, gy1 = x0 + 4, y0 + 11, x1 - 12, y1 - 29
    cv.rect(gx0, gy0, gx1, gy1, NAVYB, lambda x, y: 1.2 + (0.4 if y < gy0 + 3 else 0))
    for i, (sx, sy) in enumerate(SLOTS):
        cv.hline(sx - 1, sx + 9, sy + 11, [(160, 166, 176), (200, 206, 214)], 1)      # el prestatge
        cv.hline(sx - 1, sx + 9, sy + 12, [(60, 64, 76)], 0)
        for k in range(5):                                                         # l'espiral
            cv.flat(sx + k * 2, sy + 10, (190, 196, 206))
            cv.flat(sx + k * 2 + 1, sy + 9, (120, 126, 140))
        if i not in empty:
            sandwich(cv, sx, sy)
    cv.tint(gx0, gy0, gx1, gy1, (220, 240, 255), lambda x, y: 0.2 if (x - y) % 35 < 4 else 0.04)
    outline(cv, gx0 - 1, gy0 - 1, gx1 + 1, gy1 + 1, BRASS)
    # el teclat, la ranura de les monedes, el preu, la boca
    kx = x1 - 9
    for r in range(6):
        cv.rect(kx, gy0 + 4 + r * 7, kx + 4, gy0 + 7 + r * 7, BRASS, lambda x, y: 4.6 if y == gy0 + 4 + r * 7 else 3.6)
    cv.rect(kx + 1, gy1 - 12, kx + 3, gy1 - 4, [(10, 10, 12)], 0)
    outline(cv, kx, gy1 - 13, kx + 4, gy1 - 3, BRASS)
    obox(cv, x0 + 5, y1 - 25, x1 - 5, y1 - 15, [(10, 10, 10), (20, 40, 20)], 0.6, lit=0)
    if price:                                                         # (l'animació `maquina` el fa parpellejar)
        text(cv, '8,50 €', x0 + 9, y1 - 22, [(120, 255, 140)], 0, lit=0, flat=(120, 255, 140))
        cv.glow((x0 + x1) // 2, y1 - 20, 10, (120, 255, 140), 0.12)
    cv.rect(x0 + 8, y1 - 12, x1 - 8, y1 - 5, DARKM, lambda x, y: 1.4 - (0.6 if y == y1 - 12 else 0))   # la boca
    cv.hline(x0 + 8, x1 - 8, y1 - 13, BRASS, 4.0)
    cv.glow((x0 + x1) // 2, (gy0 + gy1) // 2, 27, (200, 220, 255), 0.12)
    cv.darken(x1 + 1, y0 + 4, x1 + 4, y1, 0.45)


def sandwich(cv, sx, sy):
    """Un entrepà triangular embolicat, amb una etiqueta daurada."""
    cv.poly([(sx, sy + 9), (sx + 8, sy + 1), (sx + 8, sy + 9)], BREAD, lambda x, y: 3.2 - (y - sy) * 0.08)
    cv.line(sx + 1, sy + 8, sx + 7, sy + 2, [(240, 240, 230)], 0)
    cv.hline(sx + 4, sx + 7, sy + 7, [(230, 90, 70)], 0)              # el tomàquet
    cv.flat(sx + 7, sy + 6, BRASS[5])
    cv.flat(sx + 6, sy + 6, BRASS[4])


# ─── L'ascensor ────────────────────────────────────────────────────────────

ASC = (565, 51, 629, FLOOR_Y - 1)
DIAL = (597, 40)


def elevator(cv, needle=0.0):
    """Portes daurades art déco, amb l'indicador d'agulla a sobre i el botó."""
    x0, y0, x1, y1 = ASC
    obox(cv, x0 - 4, y0 - 4, x1 + 4, y1, MARBLE, 3.0)
    for lx0, lx1 in ((x0, (x0 + x1) // 2), ((x0 + x1) // 2 + 1, x1)):
        cv.rect(lx0, y0, lx1, y1, BRASS,
                lambda x, y: 3.4 + (0.9 if (x + y) % 16 < 3 else 0) - (0.6 if x in (lx0, lx1) else 0) + (0.5 if x == lx0 + 1 else 0))
        mx = (lx0 + lx1) // 2                                          # el sol art déco
        for a in range(0, 181, 15):
            r = math.radians(a + 180)
            cv.line(mx, 115, round(mx + math.cos(r) * 12), round(115 + math.sin(r) * 12), BRASS, 4.6 if a % 30 == 0 else 3.8)
        cv.disc(mx, 115, 4, 4, BRASS, lambda nx, ny: 5.4 - ny * 0.6)
        cv.rect(lx0 + 4, 133, lx1 - 4, 134, BRASS, 2.4)
        cv.rect(lx0 + 4, 64, lx1 - 4, 64, BRASS, 2.6)
        outline(cv, lx0 + 4, 150, lx1 - 4, y1 - 8, BRASS)               # un plafó a baix
    cv.vline((x0 + x1) // 2, y0, y1, BRASS, 1.0)
    outline(cv, x0, y0, x1, y1, BRASS)
    dial(cv, needle)
    obox(cv, x1 + 5, 123, x1 + 9, 139, BRASS, 3.4)                    # el botó
    cv.disc(x1 + 7, 131, 1.5, 1.5, [(255, 220, 140)], 0, lit=0)


def dial(cv, needle):
    """L'indicador de plantes: un semicercle amb els números i una agulla (needle 0..1, de B a 4)."""
    cx, cy = DIAL
    cv.disc(cx, cy, 15, 12, BRASS, lambda nx, ny: 4.0 - ny * 0.6)
    cv.disc(cx, cy, 12, 9.3, [(30, 24, 16), (230, 222, 196), (248, 244, 228)], 1.6, lit=0)
    cv.rect(cx - 16, cy, cx + 16, cy + 11, MARBLE, 4.4)
    cv.hline(cx - 15, cx + 15, cy, BRASS, 3.6)
    cv.hline(cx - 15, cx + 15, cy + 1, BRASS, 2.4)
    for k in range(5):
        a = math.radians(180 + k * 45)
        tx, ty = cx + math.cos(a) * 9.5, cy + math.sin(a) * 7.4
        cv.flat(round(tx), round(ty), (60, 40, 20))
        cv.flat(round(cx + math.cos(a) * 8.2), round(cy + math.sin(a) * 6.3), (110, 90, 60))
    a = math.radians(180 + needle * 180)
    cv.line(cx, cy - 1, round(cx + math.cos(a) * 8), round(cy - 1 + math.sin(a) * 6.7), [(150, 20, 20)], 0, lit=0)
    cv.disc(cx, cy - 1, 1.2, 1.2, [(40, 30, 20)], 0, lit=0)


# ─── Composició ────────────────────────────────────────────────────────────

def bg(cv, plants=(0, 1), empty=(), sway=None, price=True):
    wall(cv)
    door(cv)
    frame(cv, 133, 40, 221, 117)                                      # un banquer gran, damunt la font
    banker(cv, 138, 45, 216, 112, 1)
    frame(cv, 509, 32, 549, 72)                                       # i un de petit, damunt la màquina
    banker(cv, 514, 37, 544, 67, 2)
    portrait(cv)
    banner(cv)
    tub_station(cv, 472, 93, 497, 150)
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

BAR = (248, 3, 392, 17)
TRACK = (BAR[0] + 6 + text_width('SOSPITA') + 6, 7, BAR[2] - 4, 13)
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
    outline(cv, x0 + 1, y0 + 1, x1 - 1, y1 - 1, [(70, 58, 40)])
    text(cv, 'SOSPITA', x0 + 6, y0 + 5, [HUD_INK], 0, lit=0, flat=HUD_INK)
    tx0, ty0, tx1, ty1 = TRACK
    cv.rect(tx0, ty0, tx1, ty1, [(40, 36, 52)], 0, lit=0)
    cv.hline(tx0, tx1, ty0, [(30, 26, 40)], 0, lit=0)
    outline(cv, tx0 - 1, ty0 - 1, tx1 + 1, ty1 + 1, [(120, 110, 130)])
    for q in QUARTS:
        cv.vline(_x(q) - 1, ty0, ty1, [(90, 84, 100)], 0, lit=0)
    cv.rect(tx1 - 2, ty0 + 2, tx1 - 1, ty0 + 3, [(200, 40, 40)], 0, lit=0)   # el 100: el telèfon


def _seg(value):
    """El tros de barra entre `value - 5` i `value`. Als quarts hi deixa una ratlla fosca: s'hi veu el gest."""
    def draw(cv):
        a, b = _x(value - STEP), _x(value) - 1
        col = _color(value)
        tx0, ty0, tx1, ty1 = TRACK
        cv.rect(a, ty0, b, ty1, [col], 0, lit=0)
        cv.hline(a, b, ty0, [tuple(min(255, c + 50) for c in col)], 0, lit=0)
        cv.hline(a, b, ty0 + 1, [tuple(min(255, c + 22) for c in col)], 0, lit=0)
        cv.hline(a, b, ty1, [tuple(int(c * 0.6) for c in col)], 0, lit=0)
        if value in QUARTS:
            cv.vline(b, ty0, ty1, [tuple(int(c * 0.45) for c in col)], 0, lit=0)
    return draw


PROPS = {'sospita': sospita, **{f'sospita_{v}': _seg(v) for v in range(STEP, 100, STEP)},
         'planta_retallada': planta_retallada, 'maquina_forat': maquina_forat}


# ─── Animació: l'agulla de l'ascensor, que va pujant i baixant ────────────

def _ease(t):
    return t * t * (3 - 2 * t)


def _frames():
    base = Canvas(light=LIGHT)
    bg(base)
    # quieta a baix, puja (amb una mica d'inèrcia), quieta a dalt, baixa
    seq = [0.0] * 5 + [_ease(i / 9) for i in range(1, 10)] + [1.0] * 5 + [1 - _ease(i / 9) for i in range(1, 10)]
    frames = []
    for i, n in enumerate(seq):
        cv = Canvas(light=LIGHT, img=base.img.copy())
        dial(cv, n)
        if i in (0, 1, 14, 15):                                       # «ding»: el botó s'encén un moment
            cv.glow(ASC[2] + 7, 131, 7, (255, 220, 140), 0.7 if i in (0, 14) else 0.35)
        frames.append(_diff(cv.img, base.img))
    return frames


ANIMS = {'ascensor': {'frames': _frames, 'frameDuration': 150}}


# ─── Animacions: el ficus a l'aire condicionat i el preu que parpelleja ────
# No toquen cap píxel dels props (la planta que falta, l'entrepà que falta): els props hi van per sobre.

def _prop_mask():
    """Els píxels que cobreix algun prop de la sala (planta_retallada, maquina_forat)."""
    m = None
    for kw in ({'plants': (0,)}, {'empty': (EMPTY,)}):
        v = _variant(**kw)
        m = m or Image.new('L', v.size, 0)                     # (a la mida de l'art: 2× amb ART_SCALE)
        m.paste(255, mask=v.getchannel('A').point(lambda a: 255 if a else 0))
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
    return _anim([{'sway': i * math.tau / 12} for i in range(12)])


def _frames_maquina():
    """La pantalleta del preu de la màquina parpelleja (dos cops) per cridar l'atenció."""
    return _anim([{}] * 4 + [{'price': False}, {}, {'price': False}, {}])


ANIMS['planta'] = {'frames': _frames_planta, 'frameDuration': 147}
ANIMS['maquina'] = {'frames': _frames_maquina, 'frameDuration': 380}


# ─── Geometria (640×360) ───────────────────────────────────────────────────

GEOMETRIA = {
    'things': {
        'sortida': {'rect': (3, 34, 80, 200), 'walk': (53, 248)},
        'plantes': {'rect': (79, 131, 117, 200), 'walk': (99, 248)},
        'font': {'rect': (128, 131, 227, 208), 'walk': (179, 253)},
        'retrat': {'rect': (245, 35, 315, 122), 'walk': (280, 248)},
        'cartell': {'rect': (333, 20, 477, 51), 'walk': (405, 248)},
        'recepcio': {'rect': (345, 128, 471, 200), 'walk': (408, 251)},
        'tub': {'rect': (472, 93, 497, 150), 'walk': (484, 248)},
        'maquina': {'rect': (507, 85, 552, 200), 'walk': (528, 251)},
        'ascensor': {'rect': (561, 28, 638, 200), 'walk': (597, 248)},
    },
    'spawns': {'vet': (200, 259), 'bonfill': (315, 243), 'recepcionista': (333, 245)},
    'walkable': [(19, 236), (621, 236), (632, 271), (8, 271)],
}
