"""
Aigua Verne — `ferrum_sindicat` (P): el local del sindicat miner de Ferrum (el despatx d'en Bru).

Una sala baixa i fumada: paret de guix verd pàl·lid que es pela (a sota, el maó), arrambador de fusta, bigues al
sostre i una bombeta amb pantalla de llauna. A l'esquerra, la **porta** del carrer, amb el penjador de cascs. Els
**cartells** de vagues antigues; la **pissarra** amb els torns de l'aigua; el **bagul** de la colla de teatre de la
Festa Major de la Fosa, obert, amb la tapa recolzada a la paret; la prestatgeria dels **motlles** de fosa (models de
fusta, caixes de motlle); l'estufa de ferro colat amb el tub. Al mig, la taula llarga de les assemblees.

Decorat (PROPS): `vestit` (el vestit de reina de vellut granat amb lluentons de llautó i la corona d'engranatge, a
dalt de tot del bagul: es veu fins que l'Iri l'agafa). ANIMS: `estufa` (el foc de l'estufa, per la reixeta).
"""
import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

import math

from PIL import Image

from hd.pix import Canvas, Light, W, H, hr, mix, B4
from hd.rooms.comu import _diff, text, text_width
from hd.rooms.exterior import fbm
from hd640.rooms.ferrum_comu import (
    RH, SMOG, SOOT, MORTAR, COB, COAL, IRONF, RUSTF, TIN, PLANKF, WHITEV, BLACKT, FIREF, GLOWF, CLOTH, REDP, HELM,
    BLUEV, brick_lvl, qtext)

FLOOR = 214                     # on la paret del fons toca a terra
LAMP = (300, 30)
STOVE = (604, 220)              # l'estufa: centre x i base
CHEST = (376, 470, FLOOR + 12)  # el bagul: x0, x1, base
PLASTER = [(30, 38, 32), (46, 58, 48), (66, 80, 66), (88, 104, 86), (112, 128, 106), (138, 150, 126), (162, 172, 146),
           (186, 192, 166)]
WOOD = [(18, 10, 8), (32, 18, 12), (50, 30, 18), (70, 44, 26), (94, 60, 34), (120, 80, 46), (146, 102, 60),
        (172, 128, 80)]
BOARD = [(10, 16, 14), (16, 26, 22), (24, 36, 30), (32, 46, 38)]
CHALK = [(150, 156, 150), (196, 200, 192), (232, 234, 226)]
FLOORB = [(14, 10, 10), (26, 18, 16), (40, 28, 22), (56, 40, 30), (74, 54, 38), (96, 70, 48), (120, 90, 60)]
VELVET = [(24, 4, 10), (44, 8, 16), (70, 12, 24), (100, 18, 32), (132, 28, 42), (162, 46, 56), (192, 76, 80)]
BRASS = [(50, 34, 10), (96, 68, 20), (150, 112, 36), (200, 160, 60), (236, 204, 110), (255, 240, 180)]
PAPERY = [(60, 52, 40), (104, 92, 70), (146, 132, 102), (184, 170, 134), (214, 202, 166), (236, 228, 198)]

LIGHT = Light(ambient=-0.2, vignette=(80, 34), floor_fade=(250, 30))
LIGHT.point(LAMP[0], LAMP[1] + 14, r=360, k=2.6, squash=1.1, down=True, power=1.4)
LIGHT.point(STOVE[0], STOVE[1] - 30, r=110, k=1.2, power=1.6)


# ─── Paret, sostre, terra ──────────────────────────────────────────────────

def paret(cv):
    # el guix verd, amb taques de fum i humitat; on s'ha pelat, el maó
    for y in range(14, FLOOR - 56):
        for x in range(W):
            peel = fbm(x / 26, y / 18, 3)
            if peel > 0.73:
                cv.put(x, y, SOOT, brick_lvl(x, y, 0, 0, 10, 4, 3.6, 5))
            elif peel > 0.71:
                cv.put(x, y, PLASTER, 5.2)                                                # la vora del guix
            else:
                v = 3.8 + (fbm(x / 60, y / 40, 4) - 0.5) * 1.4 - max(0.0, 1 - (y - 14) / 50) * 1.2
                v -= 0.8 * fbm(x / 12, y / 50, 6) ** 3 * 3                                # regalims d'humitat
                cv.put(x, y, PLASTER, v)
    # l'arrambador de fusta (posts verticals) i la motllura
    for y in range(FLOOR - 56, FLOOR + 1):
        for x in range(W):
            v = 3.0 - (1.4 if x % 13 == 0 else 0) + (fbm(x / 4, y / 30, 7) - 0.5) * 1.0
            cv.put(x, y, WOOD, v)
    cv.rect(0, FLOOR - 58, W - 1, FLOOR - 55, WOOD, lambda x, y: 4.6 - (y - FLOOR + 58) * 0.6)
    cv.rect(0, FLOOR - 3, W - 1, FLOOR, WOOD, 2.0)
    # el sostre: bigues fosques
    cv.rect(0, 0, W - 1, 13, WOOD, lambda x, y: 1.0 + y * 0.06, lit=0)
    for bx in range(-10, W, 92):
        cv.rect(bx, 0, bx + 14, 18, WOOD, lambda x, y: 2.4 - (x - bx) * 0.05 + (0.8 if y == 18 else 0))
    cv.rect(0, 13, W - 1, 14, COAL, 1.0)


def terra(cv):
    """Terra de taulons gastats, amb pols de carbó a les juntes."""
    for y in range(FLOOR + 1, RH):
        t = (y - FLOOR) / (RH - FLOOR)
        for x in range(W):
            px = (x - 320) / (0.5 + t * 0.9) + 320
            plank = int(px // 24)
            joint = abs(px % 24) < 1.0 / (0.5 + t)
            v = 3.0 + t * 0.6 + (hr(plank, 1) - 0.5) * 0.8 + (fbm(px / 40, y / 3, plank) - 0.5) * 0.8
            cv.put(x, y, FLOORB, v - (1.8 if joint else 0))


def bombeta(cv):
    x, y = LAMP
    cv.line(x, 14, x, y, COAL, 1.0)
    cv.poly([(x - 4, y), (x + 4, y), (x + 13, y + 9), (x - 13, y + 9)], TIN, lambda xx, yy: 3.8 - (yy - y) * 0.15, lit=0)
    cv.rect(x - 13, y + 9, x + 13, y + 9, TIN, 2.4, lit=0)
    cv.disc(x, y + 11, 3, 2.5, GLOWF, 5.4, lit=0)
    cv.glow(x, y + 12, 26, (255, 220, 150), 0.6)


# ─── La porta ──────────────────────────────────────────────────────────────

def porta(cv):
    x0, x1, top = 26, 86, 88
    cv.rect(x0 - 6, top - 6, x1 + 6, FLOOR, WOOD, lambda x, y: 3.4 - (0.6 if x in (x0 - 6, x1 + 6) else 0))  # el marc
    cv.rect(x0 - 6, top - 6, x1 + 6, top - 5, WOOD, 4.6)
    for y in range(top, FLOOR + 1):
        for x in range(x0, x1 + 1):
            if top + 6 <= y <= top + 40 and x0 + 7 <= x <= x1 - 7:
                bar = (x - x0 - 7) % 16 == 15 or (y - top - 6) % 12 == 11
                if bar:
                    cv.put(x, y, WOOD, 2.6)
                else:
                    cv.put(x, y, SMOG, 5.0 - (y - top) * 0.04 + (fbm(x / 6, y / 5, 9) - 0.5) * 1.6, lit=0)   # el vidre
                continue
            panel = y in (top + 44, top + 45, top + 86, top + 87) or (x - x0) in (29, 30)
            v = 3.0 + (fbm(x / 3, y / 24, 11) - 0.5) * 1.0 - (1.2 if panel else 0) - (0.8 if x in (x0, x1) else 0)
            cv.put(x, y, WOOD, v)
    cv.disc(x1 - 7, 156, 2, 2, BRASS, lambda nx, ny: 4.2 - nx - ny)
    cv.rect(x1 - 9, 160, x1 - 6, 166, BRASS, 2.6)
    # el penjador de cascs, al costat
    cv.rect(96, 104, 118, 108, WOOD, lambda x, y: 4.2 - (y - 104) * 0.5)
    for hx, hy, lamp in ((101, 110, True), (114, 112, False)):
        cv.disc(hx, hy + 5, 6.5, 5, HELM, lambda nx, ny: 4.0 - nx * 0.8 - ny * 0.9)
        cv.rect(hx - 8, hy + 9, hx + 8, hy + 10, HELM, 2.4)
        if lamp:
            cv.rect(hx - 2, hy + 1, hx + 1, hy + 4, TIN, 4.4)
    cv.line(112, 108, 108, 140, COAL, 1.0)                                                # la corretja d'un casc


# ─── Cartells ──────────────────────────────────────────────────────────────

def _poster(cv, x0, y0, w, h, ramp, lvl, seed):
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            v = lvl + (fbm(x / 6, y / 6, seed) - 0.5) * 0.8 - (0.8 if hr(x, y, seed) > 0.97 else 0)
            if (x - x0) + (y0 + h - y) < 5 and hr(seed, 1) > 0.4:
                continue                                                                   # un cantó arrencat
            cv.put(x, y, ramp, v)
    for cx, cy in ((x0 + 1, y0 + 1), (x0 + w - 2, y0 + 1)):
        cv.flat(cx, cy, (40, 40, 44))                                                       # les xinxetes


def cartells(cv):
    # VAGA GENERAL, amb el puny
    x0, y0 = 124, 34
    _poster(cv, x0, y0, 44, 62, REDP, 3.2, 21)
    text(cv, 'VAGA', x0 + 14, y0 + 4, PAPERY, 5.0)
    # el pic i el martell, creuats
    cx, cy = x0 + 22, y0 + 30
    for k in range(-15, 16):
        for w in (0, 1):
            cv.put(cx + k * 0.75 + w, cy + k * 0.75, BLACKT, 1.0)                           # mànec del pic
            cv.put(cx - k * 0.75 + w, cy + k * 0.75, BLACKT, 1.0)                           # mànec del martell
    for i in range(-9, 10):                                                                 # el ferro del pic, corbat
        a = i / 9
        cv.put(cx - 11 + i * 0.75 + a * a * 3, cy - 11 - i * 0.75 + a * a * 3 - 3, BLACKT, 1.0)
        cv.put(cx - 11 + i * 0.75 + a * a * 3 + 1, cy - 11 - i * 0.75 + a * a * 3 - 3, BLACKT, 1.0)
    for i in range(-4, 5):                                                                  # el cap del martell
        for w in range(-2, 3):
            cv.put(cx + 11 + i * 0.75 + w * 0.75, cy - 11 + i * 0.75 - w * 0.75, BLACKT, 1.0)
    text(cv, 'GENERAL', x0 + 8, y0 + 50, PAPERY, 5.0)
    # PA I AIGUA, groguenc, amb una gota
    x1, y1 = 176, 46
    _poster(cv, x1, y1, 36, 46, PAPERY, 4.0, 22)
    qtext(cv, 'PA I', x1 + 9, y1 + 5, COAL, 1.0)
    qtext(cv, 'AIGUA', x1 + 8, y1 + 12, COAL, 1.0)
    cv.disc(x1 + 18, y1 + 32, 7, 8, BLUEV, lambda nx, ny: 2.8 - nx - ny * 0.6)
    cv.flat(x1 + 18, y1 + 22, BLUEV[2])
    cv.flat(x1 + 17, y1 + 23, BLUEV[2])
    # la foto en blanc i negre dels miners de 1987
    x2, y2 = 128, 104
    _poster(cv, x2, y2, 50, 30, PAPERY, 4.6, 23)
    cv.rect(x2 + 3, y2 + 3, x2 + 46, y2 + 22, [(30, 30, 28), (60, 58, 54), (100, 98, 90), (150, 146, 136)], 1.6)
    for i in range(7):
        hx = x2 + 7 + i * 6
        cv.disc(hx, y2 + 11, 2, 2.4, [(30, 30, 28), (70, 68, 62), (120, 116, 108)], 1.6)
        cv.rect(hx - 2, y2 + 14, hx + 2, y2 + 22, [(30, 30, 28), (50, 48, 44)], 0.8)
    text(cv, '1987', x2 + 17, y2 + 24, COAL, 1.0)
    # LA FOSA ES NOSTRA, estret
    x3, y3 = 186, 98
    _poster(cv, x3, y3, 30, 44, PAPERY, 3.4, 24)
    text(cv, 'LA', x3 + 11, y3 + 6, REDP, 2.6)
    text(cv, 'FOSA', x3 + 7, y3 + 13, REDP, 2.6)
    text(cv, 'ES', x3 + 11, y3 + 20, REDP, 2.6)
    text(cv, 'NOSTRA', x3 + 3, y3 + 27, REDP, 2.6)
    cv.rect(x3 + 4, y3 + 36, x3 + 25, y3 + 37, COAL, 1.4)


# ─── La pissarra ───────────────────────────────────────────────────────────

def pissarra(cv):
    x0, y0, x1, y1 = 252, 40, 354, 120
    cv.rect(x0 - 4, y0 - 4, x1 + 4, y1 + 4, WOOD, lambda x, y: 3.6 - (0.8 if y > y1 or x > x1 else 0))
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            smear = fbm(x / 14, y / 6, 31)
            cv.put(x, y, BOARD, 1.4 + (smear - 0.5) * 1.6 + (0.6 if smear > 0.66 else 0))
    # els torns de l'aigua, en guix
    text(cv, 'TORNS AIGUA', x0 + 6, y0 + 4, CHALK, 1.4, lit=0)
    cv.rect(x0 + 6, y0 + 10, x0 + 48, y0 + 10, CHALK, 0.6, lit=0)
    rows = ('DL ROSA', 'DM PERE', 'DC ANNA', 'DJ BRU', 'DV MARTA')
    for i, r in enumerate(rows):
        text(cv, r, x0 + 6, y0 + 15 + i * 9, CHALK, 1.0, lit=0)
        for k in range(1 + int(hr(i, 3) * 4)):                                             # palets de recompte
            cv.rect(x0 + 44 + k * 3, y0 + 15 + i * 9, x0 + 44 + k * 3, y0 + 19 + i * 9, CHALK, 0.4, lit=0)
    # a la dreta: una gota dibuixada amb guix, encerclada (sense xifres: el preu canvia durant el joc)
    for j in range(9):
        w = 0 if j < 3 else (j - 2) * 0.5 if j < 6 else 2.5 - (j - 6) * 0.5
        cv.put(x0 + 77 - w, y0 + 14 + j, CHALK, 1.6, lit=0)
        cv.put(x0 + 77 + w, y0 + 14 + j, CHALK, 1.6, lit=0)
    cv.ring(x0 + 77, y0 + 19, 9, CHALK, 0.6, lit=0, step=10)
    text(cv, 'LIA', x0 + 70, y0 + 40, CHALK, 1.0, lit=0)
    # el calaixó dels guixos
    cv.rect(x0 - 4, y1 + 4, x1 + 4, y1 + 7, WOOD, lambda x, y: 4.2 - (y - y1 - 4) * 0.6)
    cv.rect(x0 + 10, y1 + 2, x0 + 16, y1 + 3, CHALK, 2.4, lit=0)
    cv.rect(x0 + 24, y1 + 2, x0 + 32, y1 + 3, WOOD, 4.6)                                  # l'esborrador


# ─── El bagul ──────────────────────────────────────────────────────────────

TRUNK = [(8, 16, 20), (14, 28, 34), (22, 42, 48), (32, 58, 62), (44, 76, 78), (62, 96, 94), (86, 118, 112)]


def bagul(cv):
    """El bagul de la colla de teatre: fusta pintada de verd blavós, cantoneres de llautó, obert amb la tapa
    recolzada a la paret; dins, disfresses i trastos (una espasa de fusta, una ploma, una màscara)."""
    x0, x1, base = CHEST
    top = base - 34
    back = top - 8                                    # la vora de darrere de la boca (perspectiva)
    # la tapa, oberta cap enrere, recolzada a la paret
    lt = back - 36
    for y in range(lt, back + 1):
        t = (y - lt) / (back - lt)
        a, b = x0 + 5 - t * 3, x1 - 5 + t * 3
        for x in range(int(a), int(b) + 1):
            v = 2.6 + t * 0.8 + (fbm(x / 3, y / 10, 41) - 0.5) * 0.6 - (1.2 if (x - x0) % 31 in (0, 1) else 0)
            cv.put(x, y, TRUNK, v)
    cv.rect(x0 + 5, lt, x1 - 5, lt + 1, TRUNK, 4.4)
    for bx in (x0 + 5, x1 - 10):
        cv.rect(bx, lt, bx + 5, lt + 5, BRASS, 3.6)
    text(cv, 'FESTA MAJOR', (x0 + x1) // 2 - text_width('FESTA MAJOR') // 2, lt + 10, PAPERY, 4.2)
    text(cv, 'DE LA FOSA', (x0 + x1) // 2 - text_width('DE LA FOSA') // 2, lt + 18, PAPERY, 4.2)
    for i in range(5):                                                                    # estrelletes
        cv.put(x0 + 14 + i * 17, lt + 28, BRASS, 4.6)
    # la boca: l'interior fosc, amb trastos
    for y in range(back, top + 1):
        t = (y - back) / (top - back)
        a, b = x0 + 2 - t * 2, x1 - 2 + t * 2
        for x in range(int(a), int(b) + 1):
            edge = x - a < 2 or b - x < 2
            cv.put(x, y, TRUNK if edge else COAL, (3.8 if edge else 1.0 + t * 0.6))
    for k in range(2):
        cv.line(x1 - 18 + k, top - 1, x1 - 6 + k, back - 24, TIN, 4.4 - k * 1.6)          # l'espasa de fusta
    cv.rect(x1 - 21, top - 3, x1 - 13, top - 1, BRASS, 3.6)
    for i in range(14):                                                                   # la ploma
        cv.put(x0 + 10 - i * 0.6, back + 2 - i, [(20, 60, 50), (40, 110, 90), (80, 170, 140)], 2.0)
        cv.put(x0 + 11 - i * 0.6, back + 2 - i, [(20, 60, 50), (40, 110, 90), (80, 170, 140)], 1.0)
    for x in range(x0 + 20, x0 + 66):                                                     # una tela de ratlles
        cv.put(x, top - 2, CLOTH if (x // 4) % 2 else REDP, 3.6)
        cv.put(x, top - 1, CLOTH if (x // 4) % 2 else REDP, 2.6)
    # la caixa
    cv.rect(x0, top, x1, base, TRUNK, lambda x, y: 3.0 - (x - x0) * 0.008 + (fbm(x / 3, y / 12, 43) - 0.5) * 0.6 -
            (1.2 if (y - top) % 11 == 10 else 0))
    cv.rect(x0, top, x1, top + 1, TRUNK, 4.6)
    for by in (top + 4, base - 6):                                                        # els cèrcols
        cv.rect(x0, by, x1, by + 1, BRASS, 2.8)
    for cx in (x0, x1 - 5):                                                               # cantoneres
        cv.rect(cx, top, cx + 5, top + 6, BRASS, 3.6)
        cv.rect(cx, base - 6, cx + 5, base, BRASS, 3.0)
    mx = (x0 + x1) // 2
    cv.rect(mx - 4, top + 3, mx + 4, top + 11, BRASS, 3.8)                                  # el pany
    cv.rect(mx - 1, top + 6, mx, top + 8, COAL, 1.0)
    for hx in (x0 - 3, x1 + 1):                                                           # nanses
        cv.rect(hx, top + 12, hx + 2, top + 18, IRONF, 3.6)
    cv.rect(x0, base + 1, x1 + 4, base + 2, COAL, 1.0)



# ─── La prestatgeria dels motlles ─────────────────────────────────────────

def motlles(cv):
    x0, x1, top = 476, 568, 36
    # els muntants i els prestatges
    for px in (x0, x1 - 4):
        cv.rect(px, top, px + 4, FLOOR + 2, WOOD, lambda x, y: 3.2 - (x - px) * 0.3)
    shelves = (66, 108, 150, 192)
    cv.rect(x0 + 4, top, x1 - 5, FLOOR, WOOD, lambda x, y: 1.4 + (fbm(x / 8, y / 20, 51) - 0.5) * 0.6)   # el fons
    for sy in shelves:
        cv.rect(x0 + 1, sy, x1 - 1, sy + 3, WOOD, lambda x, y: 4.4 - (y - sy) * 0.8)
        cv.rect(x0 + 4, sy + 4, x1 - 5, sy + 5, COAL, 0.6)
    # prestatge 1: models de fusta (un engranatge, una roda, un colze de tub)
    sy = shelves[0]
    gx, gy = x0 + 18, sy - 12
    for a in range(0, 360, 4):
        an = math.radians(a)
        r = 10 + (2 if (a // 30) % 2 == 0 else 0)
        for d in range(4, r):
            cv.put(gx + math.cos(an) * d, gy + math.sin(an) * d, PAPERY, 4.0 - math.sin(an) * 0.8 - math.cos(an) * 0.4)
    cv.disc(gx, gy, 3, 3, WOOD, 1.4)
    cv.disc(x0 + 48, sy - 9, 9, 9, PAPERY, lambda nx, ny: 3.6 - nx * 0.6 - ny * 0.8)
    cv.disc(x0 + 48, sy - 9, 4, 4, WOOD, 1.6)
    for i in range(14):
        a = i / 13 * math.pi / 2
        cv.disc(x0 + 66 + math.cos(a) * 10, sy - 2 - math.sin(a) * 10, 2.6, 2.6, PAPERY, 3.4 - i * 0.04)
    # prestatge 2: caixes de motlle (ferro) apilades
    sy = shelves[1]
    for i, (bx, bw, bh) in enumerate(((x0 + 8, 28, 10), (x0 + 10, 24, 9), (x0 + 42, 36, 14))):
        by = sy - bh - (11 if i == 1 else 0)
        cv.rect(bx, by, bx + bw, by + bh, IRONF, lambda x, y: 3.4 - (y - by) * 0.1 - (x - bx) * 0.02)
        cv.rect(bx, by, bx + bw, by, IRONF, 5.0)
        cv.rect(bx + 2, by + 3, bx + bw - 2, by + 3, COAL, 1.0)
    # prestatge 3: el motlle de tres claus (una caixa amb una etiqueta) i models de claus
    sy = shelves[2]
    cv.rect(x0 + 8, sy - 14, x0 + 46, sy - 1, WOOD, lambda x, y: 3.8 - (x - x0) * 0.01)
    cv.rect(x0 + 14, sy - 11, x0 + 30, sy - 5, PAPERY, 4.6)
    text(cv, '3', x0 + 20, sy - 11, COAL, 1.0)
    for k in range(3):
        kx = x0 + 56 + k * 9
        cv.ring(kx, sy - 12, 2.5, PAPERY, 4.0, step=30)
        cv.rect(kx, sy - 9, kx, sy - 2, PAPERY, 4.0)
        cv.rect(kx + 1, sy - 4, kx + 2, sy - 3, PAPERY, 4.0)
    # prestatge 4: llibres de registre i una capsa de llauna
    sy = shelves[3]
    for i in range(8):
        bx = x0 + 6 + i * 6
        bh = 18 + int(hr(i, 5) * 6)
        col = (REDP, WOOD, PAPERY, BLACKT)[i % 4]
        cv.rect(bx, sy - bh, bx + 4, sy - 1, col, 3.0 - (0.8 if i % 2 else 0))
        cv.rect(bx + 1, sy - bh + 4, bx + 3, sy - bh + 5, BRASS, 3.4)
    cv.rect(x0 + 60, sy - 12, x0 + 82, sy - 1, TIN, lambda x, y: 3.8 - (x - x0 - 60) * 0.06)
    # a terra, sota: un sac i un model gran (mig engranatge)
    cv.rect(x0 + 8, FLOOR - 16, x0 + 40, FLOOR, PAPERY, lambda x, y: 3.0 - (y - FLOOR + 16) * 0.05)


# ─── L'estufa ──────────────────────────────────────────────────────────────

def estufa(cv):
    cx, base = STOVE
    # el tub, que puja i se'n va per la paret
    cv.rect(cx - 4, 44, cx + 4, base - 66, IRONF, lambda x, y: 3.4 - (x - cx) * 0.3 + (1.0 if y % 30 == 0 else 0))
    cv.rect(cx - 4, 36, W - 1, 44, IRONF, lambda x, y: 3.4 - (y - 36) * 0.25 + (1.0 if x % 30 == 0 else 0))
    cv.disc(cx, 40, 4, 4, IRONF, lambda nx, ny: 3.6 - nx - ny)
    # el cos panxut de ferro colat
    for y in range(base - 66, base - 10):
        t = (y - base + 66) / 56
        hw = 14 + 6 * math.sin(t * math.pi)
        for x in range(int(cx - hw), int(cx + hw) + 1):
            u = (x - cx) / hw
            v = 2.6 - u * 1.2 + (0.9 if abs(t - 0.5) < 0.04 or abs(t - 0.1) < 0.03 else 0) - abs(u) ** 6
            cv.put(x, y, IRONF, v)
    cv.disc(cx, base - 66, 15, 3, IRONF, lambda nx, ny: 4.0 - nx)
    cv.rect(cx - 10, base - 72, cx + 10, base - 68, IRONF, 3.6)
    # la porteta amb la reixeta (el foc, per dins)
    cv.rect(cx - 8, base - 34, cx + 8, base - 20, IRONF, 3.6)
    for x in range(cx - 6, cx + 7):
        if x % 3 != 0:
            for y in range(base - 32, base - 22):
                cv.put(x, y, FIREF, 3.6 + (base - 22 - y) * -0.1 + hr(x, y) * 1.2, lit=0)
    cv.rect(cx + 8, base - 29, cx + 11, base - 27, BRASS, 3.0)                              # el tancador
    # les potes i la planxa de terra
    for lx in (cx - 14, cx + 11):
        cv.rect(lx, base - 10, lx + 3, base, IRONF, 2.8)
    cv.disc(cx, base + 1, 26, 4, TIN, lambda nx, ny: 3.0 - nx * 0.6)
    cv.glow(cx, base - 27, 30, (255, 150, 60), 0.35)
    # la galleda del carbó
    cv.poly([(cx - 40, base - 16), (cx - 24, base - 16), (cx - 26, base), (cx - 38, base)], TIN,
            lambda x, y: 3.2 - (x - cx + 40) * 0.08)
    for i in range(10):
        cv.disc(cx - 38 + hr(i, 1) * 12, base - 17 - hr(i, 2) * 3, 2, 1.6, COAL, 3.0)


# ─── La taula llarga ───────────────────────────────────────────────────────

TABLE = (120, 334, 188, 204)      # x0, x1, y de darrere, y de davant


def taula(cv):
    x0, x1, yb, yf = TABLE
    # el banc de darrere (se'n veu el respatller)
    cv.rect(x0 + 10, yb - 18, x1 - 10, yb - 15, WOOD, lambda x, y: 3.6 - (y - yb + 18) * 0.4)
    for bx in range(x0 + 14, x1 - 10, 54):
        cv.rect(bx, yb - 15, bx + 2, yb, WOOD, 2.6)
    # el sobre, en perspectiva, i el cantell
    for y in range(yb, yf + 1):
        t = (y - yb) / (yf - yb)
        a, b = x0 + 6 * (1 - t), x1 - 6 * (1 - t)
        for x in range(int(a), int(b) + 1):
            v = 3.6 + t * 0.6 + (fbm(x / 20, y / 2, 61) - 0.5) * 0.6 - (0.8 if (y - yb) % 5 == 4 else 0)
            cv.put(x, y, WOOD, v)
    cv.rect(x0, yf + 1, x1, yf + 6, WOOD, lambda x, y: 2.6 - (y - yf) * 0.12)
    cv.rect(x0, yf + 7, x1, yf + 7, COAL, 1.0)
    # les potes (les de darrere, més curtes)
    for lx in (x0 + 4, x1 - 9):
        cv.rect(lx, yf + 7, lx + 5, 240, WOOD, lambda x, y: 3.0 - (x - lx) * 0.3)
    for lx in (x0 + 12, x1 - 16):
        cv.rect(lx, yf + 7, lx + 4, 226, WOOD, 1.8)
    cv.rect(x0 + 8, 226, x1 - 8, 228, WOOD, 1.6)                                          # el travesser
    # damunt: papers, la carta de la Juana no (encara), tasses, un cendrer, un casc i un llum d'oli
    for i, (px, py, w, h) in enumerate(((150, 192, 18, 7), (172, 194, 14, 6), (254, 191, 20, 8))):
        cv.rect(px, py, px + w, py + h, PAPERY, lambda x, y: 4.6 - (0.8 if (y - py) % 3 == 2 and x > px + 2 else 0))
    for mx in (204, 288):
        cv.rect(mx, 186, mx + 6, 194, TIN, lambda x, y: 4.0 - (x - mx) * 0.3)
        cv.rect(mx + 7, 188, mx + 8, 191, TIN, 2.6)
        cv.rect(mx + 1, 186, mx + 5, 186, COAL, 1.0)
    cv.disc(236, 196, 6, 2, IRONF, lambda nx, ny: 3.0 - ny)                                # el cendrer
    cv.rect(234, 194, 238, 195, PAPERY, 5.0)
    cv.disc(312, 192, 8, 6, HELM, lambda nx, ny: 4.0 - nx * 0.8 - ny)                      # un casc
    cv.rect(302, 196, 322, 197, HELM, 2.4)
    cv.rect(303, 189, 305, 192, TIN, 4.4)
    # l'ombra a terra
    cv.darken(x0 - 4, 234, x1 + 12, 246, lambda x, y: 0.7 if y < 240 + (x - x0) * 0.02 else 0.3)


# ─── Composició ────────────────────────────────────────────────────────────

def bg(cv):
    paret(cv)
    terra(cv)
    bombeta(cv)
    porta(cv)
    cartells(cv)
    pissarra(cv)
    bagul(cv)
    motlles(cv)
    estufa(cv)
    taula(cv)
    cv.darken(CHEST[0] - 4, CHEST[2] - 4, CHEST[1] + 16, CHEST[2] + 4, 0.6)
    for y in range(RH, H):
        for x in range(W):
            cv.flat(x, y, (0, 0, 0))


# ─── Decorat: el vestit de reina ───────────────────────────────────────────

def vestit(cv):
    """El vestit de reina de vellut granat, a dalt de tot del bagul: el cos (amb el coll de puntes i la rengla de
    llautó) estès a sobre, la faldilla que penja per davant amb plecs i lluentons, i la corona d'engranatge."""
    x0, x1, base = CHEST
    top = base - 34
    cx = x0 + 42
    # la faldilla, que penja per fora del bagul fins a mig davant, i s'eixampla
    for y in range(top - 2, top + 24):
        t = (y - top + 2) / 26
        hw = 18 + t * 10
        for x in range(int(cx - hw), int(cx + hw) + 1):
            hem = top + 21 + math.sin((x - cx) * 0.5) * 2
            if y > hem:
                continue
            u = (x - cx) / hw
            fold = math.sin((x - cx) * 0.7 + 0.5)
            v = 3.2 + fold * 1.0 - u * 0.6 - t * 0.5
            if y >= hem - 1:
                cv.put(x, y, BRASS, 3.6 + fold * 0.6)                                       # la vora de llautó
            elif hr(x, y, 3) > 0.965 and fold > 0:
                cv.put(x, y, BRASS, 5.0)                                                     # lluentons
            else:
                cv.put(x, y, VELVET, v)
    # el cos, estès a sobre de tot (dins el bagul obert)
    for y in range(top - 12, top):
        t = (y - top + 12) / 12
        hw = 12 - abs(t - 0.5) * 6
        for x in range(int(cx - hw), int(cx + hw) + 1):
            cv.put(x, y, VELVET, 4.0 - (x - cx) / hw * 0.8 - t * 0.6)
    # les mànigues, a banda i banda, buides
    for side in (-1, 1):
        for i in range(14):
            x = cx + side * (10 + i)
            y = top - 9 + i * 0.5
            for k in range(4):
                cv.put(x, y + k, VELVET, 3.4 - k * 0.5 - i * 0.04)
        cv.rect(cx + side * 24 - 1, top - 4, cx + side * 24 + 1, top - 1, CLOTH, 4.4)        # els punys de puntes
    # el coll de puntes en V i la rengla de llautó
    for i in range(7):
        cv.put(cx - 6 + i, top - 12 + i * 0.6, CLOTH, 5.0)
        cv.put(cx + 6 - i, top - 12 + i * 0.6, CLOTH, 5.0)
    for y in range(top - 7, top + 1, 2):
        cv.put(cx, y, BRASS, 5.0)
    # la corona d'engranatge, posada de cantó a la vora del bagul
    gx, gy = x1 - 16, top - 10
    for a in range(0, 360, 5):
        an = math.radians(a)
        tooth = (a // 30) % 2 == 0
        for d in range(5, 9 if tooth else 7):
            cv.put(gx + math.cos(an) * d, gy + math.sin(an) * d * 0.85, BRASS,
                   4.0 - math.sin(an) * 1.0 - math.cos(an) * 0.4)
    cv.disc(gx, gy - 3, 1.4, 1.4, [(60, 10, 14), (160, 30, 40), (240, 90, 100)], 2.0, lit=0)   # un vidre vermell
    cv.flat(gx + 4, gy - 5, BRASS[5])


PROPS = {'vestit': vestit}


# ─── Animació: l'estufa ────────────────────────────────────────────────────

def _frames_estufa():
    cx, base = STOVE
    frames = []
    n = 6
    for f in range(n):
        img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        cv = Canvas(light=LIGHT, img=img)
        for x in range(cx - 6, cx + 7):
            if x % 3 != 0:
                for y in range(base - 32, base - 22):
                    v = 3.4 + (base - 22 - y) * -0.08 + hr(x, y, f) * 1.6 + math.sin(f * 1.3 + x * 0.7) * 0.4
                    cv.put(x, y, FIREF, v, lit=0)
        frames.append(img)
    return frames


ANIMS = {'estufa': {'frames': _frames_estufa, 'frameDuration': 140}}


# ─── Geometria (640×360) ───────────────────────────────────────────────────

GEOMETRIA = {
    'things': {
        'porta': {'rect': (20, 82, 92, 214), 'walk': (56, 236)},
        'bagul': {'rect': (372, 146, 474, 230), 'walk': (424, 244)},
        'pissarra': {'rect': (248, 36, 358, 124), 'walk': (302, 250)},
        'motlles': {'rect': (474, 34, 570, 216), 'walk': (522, 236)},
        'cartells': {'rect': (120, 30, 220, 144), 'walk': (170, 250)},
    },
    'spawns': {'bru': (350, 238), 'iri': (256, 252), 'vet': (530, 250)},
    'walkable': [(8, 230), (112, 230), (112, 246), (370, 246), (370, 236), (480, 236), (480, 230), (632, 230),
                 (636, 257), (4, 257)],
}
