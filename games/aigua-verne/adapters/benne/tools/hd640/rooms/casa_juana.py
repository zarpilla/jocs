"""
Aigua Verne — `casa_juana` (P), Escena 3: l'interior del casc bolcat on viu la Juana, al fons de l'antic mar.

El sostre és el fons de la barca: la quilla travessa la sala per dalt i les **costelles** de fusta baixen per la
paret com les d'una balena. Entre costella i costella, les taules del folre. A l'esquerra, la **porta**
entreoberta (fora, el blanc de la sal: entra una falca de llum freda i una mica de sorra). Una prestatgeria plena de
**llibres**, i llibres per tot arreu, en piles. L'**ull de bou** (la finestra) amb un raig de llum on balla la
pols. Els **mapes** del mar clavats a la paret: cartes amb les línies de nivell, marcades amb vermell any rere any,
cada vegada més avall, i un gràfic fet a mà on la línia només baixa. La taula de la Juana, amb la ràdio, papers i
una tassa; damunt, la **làmpada** de petroli penjada de la quilla. A la dreta, l'**aquari** buit, amb sorra seca i
un castellet, i el rètol «PER QUAN TORNIN». Al racó, l'estufa i el tub que surt pel casc.

Llum càlida de la làmpada i llum freda de fora (la porta i l'ull de bou).
ANIMS: `flama` (la làmpada), `pols` (la pols al raig de l'ull de bou).
"""
import math

import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

from hd.pix import Canvas, Light, W, H, hr, mix, WALNUT, FLOOR as FLOORW, PAPER, MANILA, GOLD, RED, GREEN, NAVY
from hd.rooms.comu import text, text_width
from hd.rooms.exterior import fbm, smooth
from hd640.rooms.aqua_comu import (RH, SKYA, SALT, SAND, STONEA, WOODG, PAINTW, RUSTA, OCHRE, STEELA, BLACKT,
                                   GLASSD, ROPEA, WICKER, BONE, WATERB, diff, amb_contorn)

# Art a 2× (1280×720 per a una sala de 640×360): el mateix dibuix, amb les formes, el dither i la llum a la
# resolució real (hd1280/canvas2x.py); el motor el mostra a 1/2 (artScale al .room.json).
ART_SCALE = 2
from hd1280.canvas2x import Canvas2x as Canvas  # noqa: E402,F811
from hd.pix import Canvas as Canvas1x  # noqa: E402,F401  (llenços auxiliars en píxels de sala: figures, textos)

FLOOR_Y = 224             # on comença el terra
SPRING = 72               # on les costelles comencen a corbar-se cap al sostre
RIBS = (14, 116, 238, 356, 482, 602)
DOOR = (40, 100, 104, 226)
PORT = (297, 104, 15)     # l'ull de bou (cx, cy, r)
LAMP = (342, 100)         # la làmpada (el vidre)
TABLE = (300, 178, 444)   # (x0, y del tauler, x1)
TANK = (502, 128, 598, 186)

WOODI = [(16, 10, 10), (30, 18, 14), (46, 28, 20), (64, 40, 26), (86, 56, 34), (110, 74, 44), (138, 96, 58),
         (166, 120, 76), (196, 150, 100), (224, 186, 132)]          # el folre de dins, fusta vella i càlida
RIB = [(12, 8, 8), (24, 14, 12), (38, 22, 16), (56, 34, 22), (78, 48, 30), (102, 66, 40), (128, 86, 52),
       (156, 110, 68)]
DAY = (226, 236, 246)

LIGHT = Light(ambient=-0.4, vignette=(70, 26), floor_fade=(246, 30))
LIGHT.point(LAMP[0], LAMP[1] + 6, r=330, k=3.0, squash=1.1, power=1.3)      # la làmpada
LIGHT.point(PORT[0], PORT[1] + 60, r=110, k=0.9, squash=0.8, power=1.5)     # l'ull de bou
LIGHT.point(78, 200, r=120, k=1.4, squash=0.9, power=1.4)                  # la porta


# ─── El casc: quilla, costelles, folre ─────────────────────────────────────

def _rib_geom(xr, y):
    """El centre i l'amplada d'una costella a l'alçada y: recta a baix, i a dalt es corba cap a nosaltres i
    s'eixampla (és més a prop)."""
    if y >= SPRING:
        return xr, 10
    s = (SPRING - y) / SPRING
    return xr + (xr - 320) * s * s * 0.45, 10 + s * s * 14


def casc(cv):
    # el folre: a la paret, traques horitzontals una mica corbades; al sostre, taules que s'obren cap a nosaltres
    for y in range(0, FLOOR_Y + 1):
        for x in range(W):
            if y >= SPRING:
                yy = y + ((x - 320) / 320) ** 2 * 6
                p = (yy - SPRING) / 13
                pf = p % 1
                lvl = 3.4 + (hr(int(p), x // 70, 3) - 0.5) * 0.8 + (fbm(x / 30, y / 6, 4) - 0.5) * 0.8
                if pf < 0.09:
                    lvl -= 1.8
                elif pf < 0.2:
                    lvl += 0.6
                if (x + int(p) * 37) % 140 < 2:
                    lvl -= 1.4                                                   # els empalmes de les taules
                if (x + int(p) * 37) % 140 in (6, 7) and int(pf * 13) in (4, 8):
                    lvl += 1.4                                                   # claus de coure
            else:
                s = (SPRING - y) / SPRING
                p = s ** 0.62 * 9
                pf = p % 1
                lvl = 3.0 + (hr(int(p), x // 90, 5) - 0.5) * 0.8 + (fbm(x / 40, y / 8, 6) - 0.5) * 0.6 - s * 0.6
                if pf < 0.08 + s * 0.04:
                    lvl -= 1.8
                elif pf < 0.22:
                    lvl += 0.5
            cv.put(x, y, WOODI, lvl)
    # les costelles
    for xr in RIBS:
        for y in range(0, FLOOR_Y + 1):
            cx, w = _rib_geom(xr, y)
            for x in range(int(cx - w / 2), int(cx + w / 2) + 1):
                u = (x - cx) / (w / 2)
                lvl = 3.4 - u * 1.2 - u * u * 1.0 + (fbm(x / 4, y / 14, 7) - 0.5) * 0.8
                if abs(u) > 0.86:
                    lvl -= 1.4
                cv.put(x, y, RIB, lvl)
            cv.put(int(cx + w / 2) + 1, y, WOODI, 0.6)                           # l'ombra de la costella al folre
            cv.put(int(cx + w / 2) + 2, y, WOODI, 1.4)
    # la quilla, que travessa per dalt
    for y in range(0, 12):
        for x in range(W):
            lvl = 2.4 + (y / 12) * 1.6 + (fbm(x / 20, y / 3, 8) - 0.5) * 0.6 + (1.4 if y == 11 else 0)
            if x % 160 == 80:
                lvl -= 1.6
            cv.put(x, y, RIB, lvl)
    for x in range(8, W, 32):                                                    # els perns de la quilla
        cv.put(x, 6, RUSTA, 3.0)


# ─── La porta i la llum de fora ────────────────────────────────────────────

def porta(cv):
    """La porta, entreoberta cap a dins: fora, la sorra blanca, la paret del moll lluny i el cel pàl·lid."""
    x0, y0, x1, y1 = DOOR
    # marc
    cv.rect(x0 - 5, y0 - 5, x1 + 5, y1, RIB, lambda x, y: 3.8 - (1.0 if x > x1 else 0) + (0.8 if y < y0 - 3 else 0))
    # el que es veu de fora
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if y < 168:
                cv.put(x, y, SKYA, 5.0 + (y - y0) / 68 * 2.6, lit=0)
            elif y < 172:
                cv.put(x, y, STONEA, 5.0, lit=0)                                 # la paret del moll, lluny
            else:
                cv.put(x, y, SAND, 6.6 + (0.6 if math.sin(y * 1.4 + x * 0.1) > 0.7 else 0) - (y - 172) * 0.01, lit=0)
    cv.disc(x0 + 46, 186, 3, 3, [(140, 40, 30), (200, 70, 44), (240, 150, 120)], 1.4, lit=0)
    cv.vline(x0 + 46, 189, 200, WOODG, 4.0, lit=0)
    # la fulla de la porta, oberta cap a dins (en escorç, a l'esquerra)
    lx0, lx1 = x0 - 24, x0 + 6

    def leaf(x, y):
        t = (x - lx0) / (lx1 - lx0)
        return 3.0 + t * 1.2 - (1.4 if int(t * 5) != int((x + 1 - lx0) / (lx1 - lx0) * 5) else 0)
    cv.poly([(lx0, y0 - 10), (lx1, y0), (lx1, y1), (lx0, y1 + 8)], WOODI, leaf)
    cv.line(lx0, y0 - 10, lx0, y1 + 8, WOODI, 1.2)
    cv.line(lx1, y0, lx1, y1, WOODI, 6.0)                                        # el cantell, a la llum de fora
    for yy in (y0 + 12, y1 - 18):                                                # travessers
        cv.line(lx0 + 1, yy - 7, lx1 - 1, yy, WOODI, 4.6)
    cv.disc(lx0 + 6, (y0 + y1) / 2 + 4, 1.8, 1.8, OCHRE, 4.8)
    # la llum que entra: una falca freda al terra, i sorra que hi ha entrat
    cv.tint(x0 - 6, FLOOR_Y, x1 + 70, RH - 1, DAY,
            lambda x, y: 0.32 * smooth(0, 1, 1 - abs((x - (x0 + (x1 - x0) / 2) - (y - FLOOR_Y) * 0.9) / (34 + (y - FLOOR_Y) * 0.8))))
    for k in range(60):
        sx = x0 + hr(k, 1) * 90
        sy = FLOOR_Y + 2 + hr(k, 2) * 22
        if hr(k, 3) > 0.3:
            cv.put(sx, sy, SAND, 6.0)


def ull_de_bou(cv):
    """L'ull de bou: anell de bronze, el vidre ple de llum de fora (sorra i cel), i el raig que entra de biaix."""
    cx, cy, r = PORT
    BRONZE = [(40, 26, 14), (74, 50, 24), (112, 80, 40), (152, 114, 60), (190, 152, 90), (222, 190, 130)]
    cv.disc(cx, cy, r + 4, r + 4, BRONZE, lambda nx, ny: 3.4 - nx * 0.6 - ny * 1.2 + (nx * nx + ny * ny) * 0.6)
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                if y < cy + 3:
                    cv.put(x, y, SKYA, 6.0 + (y - cy + r) / r * 1.4, lit=0)
                else:
                    cv.put(x, y, SAND, 7.0, lit=0)
    cv.ring(cx, cy, r + 0.5, BRONZE, 1.2, step=4)
    for a in range(0, 360, 45):
        cv.put(cx + math.cos(math.radians(a)) * (r + 2.5), cy + math.sin(math.radians(a)) * (r + 2.5), BRONZE, 5.6)
    cv.line(cx - r + 4, cy - r + 6, cx - 4, cy - r + 2, [(240, 246, 250), (255, 255, 255)], 0.6, lit=0)   # reflex
    cv.glow(cx, cy, r + 14, DAY, 0.3)


def raig(cv):
    """El raig de llum de l'ull de bou, que baixa de biaix fins al terra."""
    cx, cy, r = PORT

    def k(x, y):
        t = (y - cy) / (FLOOR_Y + 20 - cy)
        if t < 0 or t > 1:
            return 0
        c = cx + t * 60
        w = r * (1 + t * 0.5)
        d = abs(x - c) / w
        return 0.17 * (1 - d) * (1 - t * 0.5) if d < 1 else 0
    cv.tint(cx - r - 4, cy, cx + 90, FLOOR_Y + 30, DAY, k)


# ─── Llibres ───────────────────────────────────────────────────────────────

BOOKS = [NAVY + [(80, 90, 120)], RED, GREEN, MANILA, [(40, 20, 14), (70, 40, 24), (110, 66, 36), (150, 96, 52)],
         [(20, 34, 40), (34, 60, 70), (56, 92, 104), (90, 130, 140)], PAPER]


def llibre(cv, x, y_base, w, h, seed, lean=0):
    """Un llom de llibre dret: color, una ratlla daurada, una etiqueta."""
    ramp = BOOKS[int(hr(seed, 1) * len(BOOKS))]
    for yy in range(y_base - h, y_base):
        for xx in range(x, x + w):
            u = (xx - x) / max(1, w - 1)
            ox = int((y_base - yy) * lean)
            cv.put(xx + ox, yy, ramp, 2.2 - abs(u - 0.4) * 1.6 + (0.6 if xx == x else 0))
    if h > 10 and hr(seed, 2) > 0.3:
        gy = y_base - h + 3
        cv.hline(x, x + w - 1, gy, GOLD, 3.6)
        if hr(seed, 3) > 0.5:
            cv.hline(x, x + w - 1, y_base - 4, GOLD, 3.0)
    if w > 4 and hr(seed, 4) > 0.6:
        cv.rect(x + 1, y_base - h // 2 - 2, x + w - 2, y_base - h // 2 + 1, PAPER, 3.8)


def prestatgeria(cv):
    """La prestatgeria, feta entre dues costelles: quatre lleixes plenes, llibres drets, tombats i en pila."""
    x0, x1 = 126, 228
    shelves = (64, 106, 148, 190)
    cv.rect(x0, 30, x1, FLOOR_Y, WOODI, lambda x, y: 1.4 + (fbm(x / 9, y / 9, 9) - 0.5) * 0.6)   # el fons, fosc
    for k, sy in enumerate(shelves):
        x = x0 + 2
        seed = k * 100
        top = (30 if k == 0 else shelves[k - 1]) + 3
        while x < x1 - 4:
            seed += 1
            r = hr(seed, 9)
            if r < 0.12 and x < x1 - 20:                                       # una pila de llibres tombats
                yy = sy
                for j in range(int(2 + hr(seed, 10) * 4)):
                    bw = 14 + int(hr(seed, j, 11) * 6)
                    bh = 4 + int(hr(seed, j, 12) * 2)
                    ramp = BOOKS[int(hr(seed, j, 13) * len(BOOKS))]
                    cv.rect(x, yy - bh, x + bw, yy - 1, ramp, lambda xx, y_, yy=yy, bh=bh: 2.4 - (y_ - yy + bh) * 0.2)
                    cv.hline(x + 1, x + bw - 1, yy - bh, PAPER, 4.4)
                    yy -= bh
                x += 22
                continue
            if r < 0.18:
                x += 3
                continue
            w = 3 + int(hr(seed, 5) * 4)
            h = min(sy - top - 2, 24 + int(hr(seed, 6) * 12))
            lean = 0.25 if hr(seed, 7) > 0.92 else 0
            llibre(cv, x, sy, w, h, seed, lean)
            x += w + (1 if lean else 0)
        # la lleixa
        cv.rect(x0 - 2, sy, x1 + 2, sy + 3, RIB, lambda x, y: 5.0 - (y - sy) * 0.9)
        cv.darken(x0, sy + 4, x1, sy + 6, lambda x, y: 0.9 - (y - sy - 4) * 0.3)
    # muntants
    for x in (x0 - 4, x1 + 1):
        cv.rect(x, 26, x + 3, FLOOR_Y, RIB, lambda xx, y: 4.0 - (xx - x) * 0.6)


def piles(cv):
    """Piles de llibres a terra, i un parell de llibres oberts."""
    for px, base, n, seed in ((132, 236, 7, 1), (176, 230, 5, 2), (250, 232, 9, 3), (470, 228, 4, 4),
                              (612, 240, 8, 5), (10, 246, 5, 6)):
        yy = base
        cv.darken(px - 2, base, px + 26, base + 2, 0.8)
        for j in range(n):
            bw = 18 + int(hr(seed, j, 1) * 8)
            bh = 4 + int(hr(seed, j, 2) * 3)
            ox = int((hr(seed, j, 3) - 0.5) * 6)
            ramp = BOOKS[int(hr(seed, j, 4) * len(BOOKS))]
            cv.rect(px + ox, yy - bh, px + ox + bw, yy - 1, ramp, lambda x, y, yy=yy, bh=bh: 2.6 - (y - yy + bh) * 0.25)
            cv.hline(px + ox + 1, px + ox + bw - 1, yy - bh, PAPER, 4.6)
            cv.vline(px + ox + bw, yy - bh + 1, yy - 2, PAPER, 3.4)
            yy -= bh
    # un llibre obert a terra
    bx, by = 330, 244
    cv.poly([(bx, by), (bx + 14, by - 3), (bx + 28, by), (bx + 14, by + 4)], PAPER, lambda x, y: 4.6 - abs(x - bx - 14) * 0.04)
    for k in range(3):
        cv.line(bx + 3, by - 0 + k, bx + 12, by - 2 + k, PAPER, 2.8)
        cv.line(bx + 16, by - 2 + k, bx + 25, by + k, PAPER, 2.8)


# ─── Els mapes ─────────────────────────────────────────────────────────────

def mapes(cv):
    """Cartes del mar clavades a la paret: línies de nivell (isòbates) blaves, la costa d'abans, i les ratlles
    vermelles de la Juana, cada any més endins; i un gràfic fet a mà on la línia només baixa."""
    CH = [(70, 64, 52), (120, 112, 92), (170, 162, 136), (206, 198, 170), (226, 220, 194), (240, 236, 214)]
    INK = [(30, 50, 90), (50, 80, 130)]
    REDI = [(130, 30, 26), (190, 50, 40)]
    # la carta gran
    x0, y0, x1, y1 = 364, 40, 452, 104
    cv.darken(x0 + 2, y0 + 2, x1 + 2, y1 + 2, 0.8)
    cv.rect(x0, y0, x1, y1, CH, lambda x, y: 3.6 + (fbm(x / 10, y / 10, 70) - 0.5) * 0.8 - (0.6 if (x - x0) % 30 == 0 else 0))
    cx, cy = x0 + 34, y0 + 36
    for k in range(6):                                                             # isòbates
        for a in range(0, 360, 3):
            rr = 6 + k * 5 + fbm(a / 40, k, 71) * 6
            px = cx + math.cos(math.radians(a)) * rr * 1.4
            py = cy + math.sin(math.radians(a)) * rr * 0.8
            if x0 + 2 <= px <= x1 - 2 and y0 + 2 <= py <= y1 - 2:
                cv.put(px, py, INK, 1.0 if k < 5 else 0.0)
    for k in range(4):                                                             # les ratlles vermelles
        for a in range(0, 360, 4):
            rr = 34 - k * 6 + fbm(a / 40, 5, 71) * 6 - 3
            px = cx + math.cos(math.radians(a)) * rr * 1.4
            py = cy + math.sin(math.radians(a)) * rr * 0.8
            if x0 + 2 <= px <= x1 - 2 and y0 + 2 <= py <= y1 - 2 and (a // 4) % 3:
                cv.put(px, py, REDI, 1.0)
    text(cv, 'AQUA', x0 + 4, y0 + 4, INK, 0.0)
    for px_, py_ in ((x0 + 1, y0 + 1), (x1 - 1, y0 + 1), (x0 + 1, y1 - 1), (x1 - 1, y1 - 1)):
        cv.flat(px_, py_, (200, 40, 40))
    # el gràfic del nivell: una línia que només baixa
    gx0, gy0, gx1, gy1 = 382, 110, 452, 144
    cv.darken(gx0 + 2, gy0 + 2, gx1 + 2, gy1 + 2, 0.8)
    cv.rect(gx0, gy0, gx1, gy1, PAPER, lambda x, y: 4.6 - (0.8 if (x - gx0) % 8 == 0 or (y - gy0) % 6 == 0 else 0))
    cv.vline(gx0 + 4, gy0 + 3, gy1 - 3, INK, 0.0)
    cv.hline(gx0 + 4, gx1 - 3, gy1 - 4, INK, 0.0)
    prev = None
    for i in range(0, 60):
        x = gx0 + 6 + i
        y = gy0 + 5 + i * 0.4 + (i / 60) ** 2 * 6 + math.sin(i * 0.9) * 0.6
        if prev:
            cv.line(*prev, x, y, REDI, 1.0)
        prev = (x, y)
    cv.flat(gx0 + 2, gy0 + 1, (200, 40, 40))
    # una carta petita, de la badia, una mica tòrcida
    sx0, sy0 = 460, 58
    cv.darken(sx0 + 2, sy0 + 2, sx0 + 22, sy0 + 34, 0.8)
    cv.poly([(sx0, sy0 + 1), (sx0 + 20, sy0 - 1), (sx0 + 21, sy0 + 31), (sx0 + 1, sy0 + 33)], CH, 3.4)
    for k in range(5):
        cv.line(sx0 + 3, sy0 + 6 + k * 5, sx0 + 18, sy0 + 4 + k * 5 + (k % 2), INK if k < 3 else REDI, 0.8)
    cv.flat(sx0 + 10, sy0 + 1, (200, 40, 40))


# ─── La taula, la làmpada, la ràdio ────────────────────────────────────────

def taula(cv):
    x0, ty, x1 = TABLE
    cv.darken(x0 - 4, FLOOR_Y + 4, x1 + 6, FLOOR_Y + 10, lambda x, y: 0.85 if abs(x - (x0 + x1) / 2) < (x1 - x0) / 2 + 4 - (y - FLOOR_Y - 4) * 2 else 0)
    for lx in (x0 + 6, x1 - 10):
        cv.rect(lx, ty + 5, lx + 4, FLOOR_Y + 6, RIB, lambda x, y: 4.4 - (x - lx) * 0.6)
    cv.rect(x0, ty, x1, ty + 5, WOODI, lambda x, y: 6.0 - (y - ty) * 0.6 + (fbm(x / 8, y, 80) - 0.5) * 0.6)
    cv.hline(x0, x1, ty, WOODI, 7.4)
    cv.rect(x0 + 2, ty + 6, x1 - 2, ty + 8, RIB, 2.2)
    # papers, una llibreta, una tassa, una brúixola
    for px, py, w, ang in ((x0 + 50, ty - 2, 22, 0.1), (x0 + 66, ty - 3, 18, -0.05)):
        cv.poly([(px, py + 2), (px + w, py), (px + w + 2, py + 2), (px + 2, py + 3)], PAPER, 4.8)
    cv.rect(x0 + 14, ty - 3, x0 + 30, ty - 1, RED, 2.6)
    cv.hline(x0 + 15, x0 + 29, ty - 3, PAPER, 4.6)
    cv.rect(x1 - 26, ty - 8, x1 - 20, ty - 1, PAINTW, lambda x, y: 4.6 - (x - x1 + 26) * 0.3)
    cv.ring(x1 - 18, ty - 5, 2, PAINTW, 3.4, step=40)
    cv.hline(x1 - 25, x1 - 21, ty - 8, [(40, 20, 10), (70, 40, 20)], 1.0)
    cv.disc(x1 - 40, ty - 1, 4, 1.6, GOLD, lambda nx, ny: 4.0 - ny * 1.2)
    # la ràdio
    rx0, rx1, ry0 = x0 + 92, x0 + 122, ty - 22
    cv.rect(rx0, ry0, rx1, ty - 1, WOODI, lambda x, y: 4.6 - (x - rx0) * 0.03 + (0.8 if y == ry0 else 0) - (1.0 if x == rx1 else 0))
    cv.rect(rx0 + 3, ry0 + 4, rx0 + 15, ry0 + 16, PAPER, lambda x, y: 3.0 + ((x + y) % 2) * 0.6)    # l'altaveu, de tela
    cv.rect(rx0 + 18, ry0 + 4, rx1 - 3, ry0 + 9, [(60, 40, 10), (200, 150, 60), (250, 220, 140)], 1.6, lit=0.5)   # el dial
    cv.vline(rx0 + 22, ry0 + 4, ry0 + 9, RED, 4.0, lit=0)
    for kx in (rx0 + 20, rx1 - 6):
        cv.disc(kx, ry0 + 14, 2.2, 2.2, BLACKT, lambda nx, ny: 2.8 - ny - nx)
    cv.line(rx1 - 3, ry0, rx1 + 4, ry0 - 12, STEELA, 4.6)                         # l'antena
    # la cadira (un tamboret de bot)
    sx = x1 + 14
    cv.rect(sx, 206, sx + 22, 209, WOODI, lambda x, y: 5.6 - (y - 206) * 0.6)
    for lx in (sx + 2, sx + 18):
        cv.rect(lx, 210, lx + 2, FLOOR_Y + 8, RIB, 3.4)


def lampada(cv):
    """La làmpada de petroli penjada de la quilla: la cadena, el capell de llautó i el vidre amb la flama."""
    x, y = LAMP
    for yy in range(10, y - 12, 3):
        cv.put(x, yy, GOLD, 3.0)
        cv.put(x, yy + 1, GOLD, 4.6)
    cv.poly([(x - 9, y - 8), (x, y - 13), (x + 9, y - 8)], GOLD, lambda xx, yy: 4.6 - (yy - y + 13) * 0.2 - (xx - x) * 0.08)
    cv.rect(x - 9, y - 8, x + 9, y - 7, GOLD, 3.4)
    # el vidre
    for yy in range(y - 6, y + 9):
        t = (yy - y + 6) / 15
        hw = 4 + math.sin(t * math.pi) * 3
        for xx in range(int(x - hw), int(x + hw) + 1):
            cv.put(xx, yy, [(120, 80, 30), (210, 160, 80), (250, 214, 140), (255, 240, 200)], 2.0 + (1 - abs(xx - x) / hw) * 1.2, lit=0)
    cv.rect(x - 5, y + 9, x + 5, y + 13, GOLD, lambda xx, yy: 3.8 - (yy - y - 9) * 0.3 - (xx - x) * 0.1)
    cv.glow(x, y, 60, (255, 210, 130), 0.35)


# ─── L'aquari, l'estufa, el terra ──────────────────────────────────────────

def aquari(cv):
    """L'aquari buit damunt d'un moble: el vidre amb reflexos, sorra seca al fons, un castellet de ceràmica, una
    planta seca, i el rètol de paper: PER QUAN TORNIN."""
    x0, y0, x1, y1 = TANK
    # el moble
    cv.darken(x0 - 4, FLOOR_Y + 2, x1 + 6, FLOOR_Y + 6, 0.85)
    cv.rect(x0 - 2, y1 + 1, x1 + 2, FLOOR_Y + 2, WOODI, lambda x, y: 3.8 - (1.4 if x > x1 - 1 else 0) + (0.8 if y == y1 + 1 else 0))
    cv.rect(x0 + 4, y1 + 8, (x0 + x1) // 2 - 2, FLOOR_Y - 4, WOODI, 2.8)
    cv.rect((x0 + x1) // 2 + 2, y1 + 8, x1 - 4, FLOOR_Y - 4, WOODI, 2.8)
    for kx in ((x0 + x1) // 2 - 6, (x0 + x1) // 2 + 6):
        cv.put(kx, y1 + 22, GOLD, 4.6)
    # dins: la paret del darrere vista a través del vidre (verdosa), sorra, castell, planta
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            o = cv.get(x, y)
            cv.flat(x, y, mix(o, (150, 180, 170), 0.18))
    for y in range(y1 - 9, y1):
        for x in range(x0 + 1, x1):
            hh = y1 - 9 + math.sin(x * 0.12) * 1.5
            if y >= hh:
                cv.put(x, y, SAND, 4.6 + (y - hh) * 0.1 + (hr(x, y) - 0.5) * 0.6)
    cx = x0 + 62
    cv.rect(cx, y1 - 22, cx + 12, y1 - 8, PAINTW, lambda x, y: 4.0 - (x - cx) * 0.12)
    for k in range(4):
        cv.rect(cx + k * 4, y1 - 25, cx + k * 4 + 1, y1 - 23, PAINTW, 4.4)
    cv.rect(cx + 4, y1 - 14, cx + 7, y1 - 8, BLACKT, 1.0)
    for i in range(5):                                                           # la planta seca
        a = 1.2 + (i - 2) * 0.3
        cv.line(x0 + 22, y1 - 8, x0 + 22 + math.cos(a) * 14, y1 - 8 - math.sin(a) * 18, MANILA, 2.2)
    # el vidre: marc, reflexos
    cv.rect(x0 - 1, y0 - 2, x1 + 1, y0, STEELA, 4.4)
    cv.rect(x0 - 1, y1, x1 + 1, y1 + 1, STEELA, 3.4)
    for x in (x0 - 1, x0, x1, x1 + 1):
        cv.vline(x, y0, y1, STEELA, 3.6)
    for k in range(3):
        cv.line(x0 + 8 + k * 3, y0 + 4, x0 + 26 + k * 3, y1 - 12, [(200, 220, 220), (240, 250, 250)], 0.4, lit=0) if k != 1 else None
    cv.line(x1 - 16, y0 + 3, x1 - 6, y0 + 22, [(200, 220, 220), (240, 250, 250)], 0.6, lit=0)
    # el rètol, enganxat al vidre amb cinta
    s = 'PER QUAN TORNIN'
    w = text_width(s)
    rx = (x0 + x1) // 2 - w // 2 - 3
    ry = y0 + 14
    cv.darken(rx + 1, ry + 1, rx + w + 7, ry + 11, 0.8)
    cv.rect(rx, ry, rx + w + 5, ry + 10, PAPER, lambda x, y: 4.8 - (fbm(x / 6, y / 4, 90) - 0.5))
    text(cv, s, rx + 3, ry + 3, [(30, 40, 80), (50, 70, 130)], 0.6)
    for tx in (rx + 2, rx + w + 1):
        cv.rect(tx, ry - 2, tx + 3, ry + 1, MANILA, 4.8)


def estufa(cv):
    """L'estufa de llenya al racó, amb el tub que puja i surt pel casc."""
    x0, x1 = 608, 636
    cv.darken(x0 - 4, FLOOR_Y + 6, x1 + 2, FLOOR_Y + 10, 0.85)
    cv.rect(x0, 178, x1, FLOOR_Y + 8, BLACKT, lambda x, y: 2.6 - (x - x0) * 0.04 + (1.2 if y == 178 else 0))
    cv.rect(x0 + 5, 192, x1 - 5, 208, BLACKT, 1.0)
    cv.rect(x0 + 7, 200, x1 - 7, 207, [(60, 16, 8), (140, 50, 14), (220, 110, 30), (250, 180, 80)],
            lambda x, y: 1.0 + hr(x, y) * 1.6, lit=0)                            # les brases
    cv.rect(x0 + 10, 60, x0 + 16, 177, STEELA, lambda x, y: 3.6 - (x - x0 - 10) * 0.4)
    for y in range(64, 177, 28):
        cv.hline(x0 + 9, x0 + 17, y, STEELA, 4.6)
    cv.rect(x0 + 6, 174, x0 + 20, 177, STEELA, 3.0)
    # una cafetera damunt
    cv.rect(x0 + 2, 168, x0 + 8, 177, PAINTW, lambda x, y: 4.2 - (x - x0 - 2) * 0.3)


def terra(cv):
    """El terra: taules de pi velles en perspectiva, una catifa de drap gastada, i sorra a les juntes."""
    VPX, VPY = 320, 90
    for y in range(FLOOR_Y, RH):
        t = (y - FLOOR_Y) / (RH - FLOOR_Y)
        for x in range(W):
            gx = (x - VPX) / (y - VPY) * 14
            pf = gx % 1
            lvl = 3.4 + t * 0.4 + (hr(int(math.floor(gx)), 4) - 0.5) * 0.8 + (fbm(x / 20, y / 3, 81) - 0.5) * 0.6
            if pf < 0.07 + 0.03 * (1 - t):
                lvl -= 1.8
            cv.put(x, y, WOODI, lvl)
    cv.darken(0, FLOOR_Y, W - 1, FLOOR_Y + 2, lambda x, y: 0.9 - (y - FLOOR_Y) * 0.3)
    # la catifa de drap (ratlles de colors esvaïts)
    RUG = [[(40, 20, 20), (90, 40, 34), (140, 70, 52), (180, 110, 80)],
           [(20, 30, 46), (40, 60, 90), (70, 96, 130), (110, 140, 170)],
           [(60, 50, 30), (120, 100, 60), (170, 150, 100), (210, 190, 140)]]
    cv.poly([(214, 232), (468, 232), (500, 256), (186, 256)], RUG[0],
            lambda x, y: 0)  # base (es repinta)
    for y in range(232, 257):
        t = (y - 232) / 24
        xa, xb = 214 - 28 * t, 468 + 32 * t
        for x in range(int(xa), int(xb) + 1):
            band = int((x - xa) / (xb - xa) * 14) % 3
            lvl = 2.2 + (0.8 if (x + y) % 2 else 0) + (fbm(x / 9, y / 3, 82) - 0.5) * 0.8
            cv.put(x, y, RUG[band], lvl)
        cv.put(xa, y, RUG[2], 3.4)
        cv.put(xb, y, RUG[2], 3.4)
    for x in range(214, 469, 3):                                                    # els serrells
        cv.vline(x, 230, 231, RUG[2], 3.0)


# ─── Composició ────────────────────────────────────────────────────────────

def bg(cv):
    casc(cv)
    terra(cv)
    porta(cv)
    ull_de_bou(cv)
    prestatgeria(cv)
    mapes(cv)
    aquari(cv)
    estufa(cv)
    taula(cv)
    piles(cv)
    lampada(cv)
    raig(cv)
    for X, Y, _, _ in cv.pixels(0, RH, W - 1, H - 1):                            # la barra de verbs: negre
        cv.P[X, Y] = (0, 0, 0, 255)


PROPS = {}


# ─── Animacions ────────────────────────────────────────────────────────────

def _frames_flama():
    """La flama de la làmpada: el cor del vidre i el halo tremolen."""
    x, y = LAMP
    out = []
    for i in range(8):
        cv = Canvas(transparent=True)
        k = 0.5 + 0.5 * math.sin(i / 8 * 2 * math.pi * 2 + hr(i, 1)) * (0.5 + 0.5 * hr(i, 2))
        fh = 4 + int(k * 3)
        for yy in range(y + 4 - fh, y + 5):
            hw = 1.6 * (1 - (y + 4 - yy) / (fh + 1)) + 0.4
            for xx in range(int(x - hw), int(x + hw) + 1):
                for X, Y, _, _ in cv.pixels(xx, yy, xx, yy):
                    cv.P[X, Y] = (255, 250, 220, 255) if abs(xx - x) < 1 else (255, 200, 90, 255)
        for yy in range(y - 30, y + 30):
            for xx in range(x - 30, x + 30):
                d = math.hypot(xx - x, yy - y) / 30
                if 0.3 < d < 1 and hr(xx, yy, i) < (1 - d) * 0.22 * k:
                    for X, Y, _, _ in cv.pixels(xx, yy, xx, yy):
                        cv.P[X, Y] = (255, 214, 140, 70)
        out.append(cv.img)
    return out


def _frames_pols():
    """La pols que balla al raig de l'ull de bou."""
    cx, cy, r = PORT
    out = []
    n = 16
    for i in range(n):
        cv = Canvas(transparent=True)
        for k in range(26):
            t = (hr(k, 1) + i / n * (0.3 + hr(k, 4) * 0.2) * (1 if k % 2 else -1)) % 1
            yy = cy + 4 + t * (FLOOR_Y - cy)
            xx = cx + t * 60 + (hr(k, 2) - 0.5) * 2 * r * (1 + t * 0.5) + math.sin(i / n * 2 * math.pi + k) * 2
            a = int(160 * (1 - abs(hr(k, 2) - 0.5) * 2) * (1 - t * 0.6))
            for X, Y, _, _ in cv.pixels(int(xx), int(yy), int(xx), int(yy)):
                cv.P[X, Y] = (255, 250, 230, a)
        out.append(cv.img)
    return out


ANIMS = {'flama': {'frames': _frames_flama, 'frameDuration': 120},
         'pols': {'frames': _frames_pols, 'frameDuration': 140}}


GEOMETRIA = {
    'things': {
        'porta': {'rect': (14, 94, 110, 228), 'walk': (76, 238)},
        'mapes': {'rect': (360, 36, 484, 148), 'walk': (418, 238)},
        'llibres': {'rect': (120, 26, 234, 226), 'walk': (180, 240)},
        'aquari': {'rect': (498, 118, 604, 226), 'walk': (550, 240)},
        'finestra': {'rect': (276, 84, 318, 124), 'walk': (296, 238)},
    },
    'spawns': {'juana': (466, 236), 'iri': (214, 246), 'vet': (276, 252)},
    'walkable': [(10, 230), (600, 230), (636, 257), (2, 257)],
}
