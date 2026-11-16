"""
El pròleg (cinemàtica), a 640×360 (vegeu hd/rooms/proleg_ginebra.py, la de 480×270): Ginebra de nit, la seu
del Banc Central Mundial Unificat.
  - el llac Léman, negre i quiet, amb el raig d'aigua il·luminat i les muntanyes retallades contra el cel;
  - la seu del BCMU: una torre de vidre damunt d'un sòcol de pedra, amb «BCMU» daurat a dalt, el llum vermell
    de l'antena i les finestres de qui encara treballa (algun fluorescent, alguna làmpada); tot s'emmiralla al llac;
  - a la façana, una pantalla gegant: de primer, el logotip del banc; després, el Director Bonfill grava l'anunci
    («Al BCMU construïm el futur de tothom»), i somriu massa.

És una cinemàtica que avança amb cada frase (vegeu rooms/proleg_ginebra.json), com la de Ni un ou. Comença al pla
de la portada (la capa opaca `pis`, de portada.py), que «Comença» deixa sense títol: el pols de llum surt de la
parabòlica de l'Iri cap a la torre (`senyal_va`) i el pla es fon en trama (`pis_fon`) cap a Ginebra. Les lletres
del BCMU fan una espurna (`lletres_brilla`). La pantalla s'encén (`pantalla_entra`), el Director parla
(`pantalla_parla`), perd el somriure i mira fora de camp (`pantalla_talla`, `pantalla_queixa`) i el torna a posar
(`pantalla_somriu`). «Lluny. Prou lluny»: torna el pla del pis (`pis_torna`), i al monitor s'obre una porta
(`pis_porta`, `pis_festa`).
Animació de fons: `nit` (el raig, els reflexos al llac i el llum de l'antena).
"""
import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

import functools
import math

import numpy as np
from PIL import Image
from pixels import nearest

from hd.pix import Light, Canvas, W, H, hr
from hd.rooms.comu import outline, text, text_width, _diff
from hd.characters import SKIN_PALE, GRAY_SHOE, SUIT_D, HAIR_PLAT
from hd.personatges import hair_cap
from hd640.draw_characters import person
import hd640.rooms.portada as portada

K = 4 / 3
HORIZON = 200

NIGHT = [(2, 2, 8), (4, 6, 16), (8, 10, 26), (14, 16, 40), (22, 22, 56), (34, 30, 72), (50, 40, 88), (70, 54, 104)]
MOUNT = [(4, 4, 10), (8, 8, 18), (14, 14, 28), (20, 20, 38)]
WATER = [(1, 2, 6), (3, 5, 12), (6, 9, 20), (10, 14, 30), (16, 20, 40), (24, 28, 52)]
STONE = [(14, 12, 14), (26, 24, 26), (42, 38, 40), (60, 56, 56), (82, 76, 74), (106, 100, 96), (132, 126, 120)]
GLASSB = [(4, 8, 14), (8, 14, 24), (14, 22, 36), (22, 32, 50), (32, 44, 66), (46, 60, 84)]
WARM = [(60, 36, 10), (130, 84, 26), (210, 150, 60), (250, 210, 120), (255, 240, 190)]
COOL = [(20, 40, 50), (60, 100, 120), (140, 190, 210), (210, 236, 244)]
GOLD = [(60, 40, 6), (130, 92, 16), (200, 150, 30), (240, 200, 70), (255, 236, 150)]
JET = [(30, 40, 60), (70, 90, 120), (130, 150, 180), (190, 206, 226), (240, 246, 255)]
TOWER = (253, 387)             # la torre: de x 253 a 387
TOP = 29                       # el capdamunt del vidre
BASE_Y = 160                   # el sòcol de pedra, de 160 a l'horitzó
SCREEN = (267, 67, 373, 149)   # la pantalla de la façana
FLOOR = 8                      # alçada d'un pis
BAY = 10                       # amplada d'una crugia (entre muntants)
MOON = (544, 40)
JET_X, JET_TOP = 93, 83

LIGHT = Light(ambient=0.0)

BONFILL = {'skin': SKIN_PALE, 'legs': SUIT_D, 'top': SUIT_D, 'shoes': GRAY_SHOE, 'closed': True,
           'brow': (200, 200, 210), 'hooks': {'hair': hair_cap(HAIR_PLAT, fringe=0.4)}}


# ─── El cel, les muntanyes, el llac ────────────────────────────────────────

def sky(cv):
    for y in range(0, HORIZON):
        for x in range(W):
            cv.put(x, y, NIGHT, 1.0 + y / 40 + (hr(x // 3, y // 3) - 0.5) * 0.2, lit=0)
    for i in range(130):                                                 # estrelles
        x, y = int(hr(i, 1) * W), int(hr(i, 2) * 120)
        b = hr(i, 3)
        cv.flat(x, y, (200, 200, 230) if b > 0.7 else (110, 110, 150) if b > 0.25 else (70, 70, 110))
        if b > 0.95:                                                     # les més brillants fan creueta
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                cv.flat(x + dx, y + dy, (90, 90, 130))
    # la lluna, petita i a un costat, amb taques
    mx, my = MOON
    cv.glow(mx, my, 30, (180, 190, 230), 0.25)
    cv.disc(mx, my, 8, 8, [(200, 200, 190), (236, 234, 220), (250, 250, 240)], lambda nx, ny: 1.4 - nx * 0.8, lit=0)
    for dx, dy, r in ((-3, -2, 1.6), (2, 2, 1.2), (-1, 4, 1.0), (3, -4, 0.8)):
        cv.disc(mx + dx, my + dy, r, r, [(186, 184, 176), (214, 212, 200)], 0.4 + dx * 0.1, lit=0)


def mountains(cv):
    """El Salève i companyia, retallats contra el cel; neu a les crestes."""
    for x in range(W):
        u = x / K
        h1 = K * (112 + 10 * math.sin(u / 47) + 6 * math.sin(u / 13 + 1) + 4 * hr(x // 8, 4)) + math.sin(x / 3.3) * 0.7
        h2 = K * (126 + 6 * math.sin(u / 31 + 2) + 3 * hr(x // 5, 5))
        for y in range(int(h1), HORIZON):
            depth = y - h1
            snow = depth < 2.6 + math.sin(x / 5) and math.sin(u / 47) > 0.4
            if snow:
                cv.put(x, y, [(40, 46, 70), (60, 66, 90), (100, 106, 130)], 1.2 - depth * 0.3 + (0.4 if x % 7 < 3 else 0), lit=0)
            else:
                cv.put(x, y, MOUNT, 1.4 + (0.3 if hr(x // 4, y // 6, 9) > 0.8 else 0), lit=0)
        for y in range(int(h2), HORIZON):
            cv.put(x, y, MOUNT, 0.6, lit=0)


def city(cv):
    """Edificis baixos al moll, amb teulades, finestres i els fanals de la riba."""
    x = 0
    i = 0
    while x < W:
        w = 21 + int(hr(i, 7) * 29)
        h = 11 + int(hr(i, 8) * 21)
        if not (TOWER[0] - 13 < x < TOWER[1] + 5):
            top = HORIZON - h
            roof = hr(i, 10)
            for yy in range(top, HORIZON):
                for xx in range(x, min(W, x + w - 1)):
                    cv.put(xx, yy, MOUNT, 2.2 - (0.4 if xx == x + w - 2 else 0), lit=0)
            if roof > 0.55:                                              # teulada de mansarda
                for k in range(4):
                    cv.hline(x + k + 1, x + w - 3 - k, top - 1 - k, MOUNT, 2.0, lit=0)
            elif roof > 0.3:                                             # xemeneies
                cv.rect(x + 4, top - 4, x + 6, top - 1, MOUNT, 2.0, lit=0)
            for wy in range(top + 4, HORIZON - 3, 5):
                for wx in range(x + 3, x + w - 4, 5):
                    r = hr(wx, wy, 2)
                    if r > 0.62:
                        col = (240, 190, 110) if hr(wx, wy, 3) > 0.3 else (160, 200, 240)
                        cv.flat(wx, wy, col)
                        cv.flat(wx, wy + 1, tuple(c * 3 // 4 for c in col))
                        if r > 0.9:
                            cv.flat(wx + 1, wy, col)
                            cv.flat(wx + 1, wy + 1, tuple(c * 3 // 4 for c in col))
        x += w
        i += 1
    cv.hline(0, W - 1, HORIZON - 1, STONE, 1.0, lit=0)                  # el moll
    for lx in range(8, W, 29):                                           # fanals de la riba
        if TOWER[0] - 34 < lx < TOWER[1] + 34:
            continue
        cv.vline(lx, HORIZON - 5, HORIZON - 2, STONE, 1.6, lit=0)
        cv.flat(lx, HORIZON - 6, (255, 220, 150))
        cv.glow(lx, HORIZON - 6, 6, (255, 210, 140), 0.4)


def lake(cv):
    for y in range(HORIZON, H):
        for x in range(W):
            ripple = math.sin(x / 12 + y * 0.97) * 0.3
            cv.put(x, y, WATER, 2.0 - (y - HORIZON) / 66 + ripple * 0.5, lit=0)


def reflections(cv, frame=0):
    """Els llums s'emmirallen al llac, trencats per les ones."""
    src = cv.img.copy()
    S = src.load()
    for y in range(HORIZON + 1, H):
        d = y - HORIZON
        sy = HORIZON - d
        if sy < 0:
            break
        for x in range(W):
            wob = round(math.sin(y * 0.52 + frame * 0.8) * min(4, d / 12))
            sx = max(0, min(W - 1, x + wob))
            r, g, b, _ = S[sx, sy]
            if r + g + b > 260 and (y + x // 4) % 2 == 0:
                o = cv.get(x, y)
                k = 0.45 * max(0, 1 - d / 146)
                cv.flat(x, y, (int(o[0] + (r - o[0]) * k), int(o[1] + (g - o[1]) * k), int(o[2] + (b - o[2]) * k)))


def jet(cv, frame=0):
    """El raig d'aigua, il·luminat, a l'esquerra."""
    bx, top = JET_X, JET_TOP
    for y in range(top, HORIZON):
        t = (y - top) / (HORIZON - top)
        wdt = 1 + t * 6.5 + (2.6 if y < top + 13 else 0)
        for x in range(int(bx - wdt), int(bx + wdt) + 1):
            if hr(x, y + frame * 4, 4) > 0.25 + t * 0.3:
                cv.put(x, y, JET, 3.6 - abs(x - bx) / max(1, wdt) * 1.6 - t * 0.8, lit=0)
    # la ploma que cau, a la dreta (el vent)
    for k in range(100):
        a = hr(k, frame, 5)
        x = bx + 3 + int(a * 24)
        y = top + int(a * a * 53) + int(hr(k, 6, 7) * 8)
        cv.flat(x, y, JET[2] if hr(k, 8) > 0.5 else JET[3])
    # l'escuma a la base, i el moll d'on surt
    for k in range(30):
        x = bx + int((hr(k, frame, 11) - 0.5) * 18)
        cv.flat(x, HORIZON - 1 - int(hr(k, 12) * 3), JET[3])
    cv.glow(bx, top + 40, 40, (190, 210, 240), 0.12)


# ─── La seu del BCMU ───────────────────────────────────────────────────────

def big_word(cv, word, cx, y, big):
    """Lletres daurades grosses (les petites ×`big`), amb bisell: llum a dalt, ombra a baix."""
    w = (text_width(word) + 1) * big
    tmp = Canvas(w=60, h=10, transparent=True)
    text(tmp, word, 0, 0, GOLD, 4, lit=0)
    sm = nearest(tmp.img, (tmp.img.width * big, tmp.img.height * big))
    SM = sm.load()
    out = sm.copy()
    O = out.load()
    for yy in range(sm.height):
        for xx in range(sm.width):
            if SM[xx, yy][3]:
                above = yy > 0 and SM[xx, yy - 1][3]
                below = yy < sm.height - 1 and SM[xx, yy + 1][3]
                if not above:
                    O[xx, yy] = GOLD[4] + (255,)
                elif not below:
                    O[xx, yy] = GOLD[2] + (255,)
    cv.img.alpha_composite(out, (cx - w // 2, y))
    return cx - w // 2, w


def bcmu(cv, antenna=True):
    x0, x1 = TOWER
    top = TOP
    # la torre de vidre, amb els forjats i els muntants
    for y in range(top, BASE_Y):
        for x in range(x0, x1 + 1):
            floor = (y - top) % FLOOR == 0
            mull = (x - x0) % BAY == 0
            sheen = max(0, 1 - abs((x - x0) - 24 - (y - top) * 0.3) / 13) * 1.4    # el reflex de la lluna
            edge = 1.6 if x - x0 < 4 else (-0.8 if x1 - x < 4 else 0)
            lvl = 2.4 + (y - top) / 213 + sheen + edge + (1.0 if floor else 0) + (0.5 if mull else 0)
            cv.put(x, y, GLASSB, lvl, lit=0)
    # les finestres de qui encara treballa: làmpades càlides i algun fluorescent fred
    for fy in range(top + 2, BASE_Y - 4, FLOOR):
        for fx in range(x0 + 2, x1 - 6, BAY):
            r = hr(fx, fy, 9)
            if r > 0.72:
                ramp = COOL if hr(fx, fy, 2) > 0.8 else WARM
                cv.rect(fx, fy + 1, fx + 7, fy + 5, ramp, lambda px, py: 2.0 + hr(fx, fy, 1) - (py - fy) * 0.15, lit=0)
                if hr(fx, fy, 3) > 0.5:                                  # algú a la taula, a contrallum
                    sx = fx + 2 + int(hr(fx, fy, 4) * 3)
                    cv.rect(sx, fy + 3, sx + 1, fy + 5, [(20, 14, 10)], 0, lit=0)
                    cv.flat(sx, fy + 2, (20, 14, 10))
                elif hr(fx, fy, 5) > 0.5:                                # una persiana mig abaixada
                    for py in range(fy + 1, fy + 3):
                        cv.tint(fx, py, fx + 7, py, (20, 16, 20), 0.5 if py % 2 else 0.3)
    # el coronament i les lletres daurades
    cv.rect(x0 - 3, top - 8, x1 + 3, top - 1, STONE, lambda x, y: 3.2 + (0.8 if y == top - 8 else 0) - (0.6 if y == top - 1 else 0), lit=0)
    for x in range(x0 - 1, x1 + 2, 6):                                  # les juntes de la pedra
        cv.vline(x, top - 6, top - 2, STONE, 2.4, lit=0)
    big_word(cv, 'BCMU', (x0 + x1) // 2, top - 25, 3)
    cv.glow((x0 + x1) // 2, top - 17, 35, (255, 210, 110), 0.3)
    # l'antena del terrat, amb el llum vermell
    ax = x1 - 14
    cv.vline(ax, top - 24, top - 9, STONE, 3.0, lit=0)
    for y in range(top - 21, top - 9, 5):
        cv.hline(ax - 1, ax + 1, y, STONE, 2.4, lit=0)
    cv.rect(ax - 1, top - 26, ax + 1, top - 25, [(90, 20, 20), (255, 60, 50)], 1 if antenna else 0, lit=0)
    if antenna:
        cv.glow(ax, top - 25, 8, (255, 60, 50), 0.4)
    # el sòcol de pedra, amb l'entrada i les columnes
    cv.rect(x0 - 32, BASE_Y, x1 + 32, HORIZON - 1, STONE,
            lambda x, y: 2.6 + (0.8 if (x - x0) % 21 < 4 else 0) - (y - BASE_Y) * 0.015 + (0.3 if (y - BASE_Y) % 7 == 0 else 0), lit=0)
    cv.rect(x0 - 35, BASE_Y - 3, x1 + 35, BASE_Y, STONE, lambda x, y: 4.2 + (0.6 if y == BASE_Y - 3 else 0), lit=0)
    cv.rect(301, 176, 339, HORIZON - 1, WARM, lambda x, y: 1.8 + (0.4 if y > 192 else 0), lit=0)   # el vestíbul, encès
    cv.rect(316, 182, 324, 186, GOLD, 2.6, lit=0)                        # el logotip del vestíbul
    cv.flat(312, 194, (30, 20, 10))                                      # el vigilant, d'esquena
    cv.rect(311, 195, 313, HORIZON - 2, [(30, 20, 10)], 0, lit=0)
    for cx in (307, 320, 333):
        cv.rect(cx, 176, cx + 1, HORIZON - 1, STONE, 1.2, lit=0)
    cv.hline(299, 341, 175, STONE, 4.6, lit=0)
    cv.glow(320, 189, 27, (255, 210, 130), 0.25)
    # una bandera que no es mou (no fa vent per als bancs)
    fx = x1 + 24
    cv.vline(fx, BASE_Y - 35, BASE_Y - 3, STONE, 3.4, lit=0)
    cv.flat(fx, BASE_Y - 36, GOLD[3])
    cv.rect(fx + 1, BASE_Y - 35, fx + 13, BASE_Y - 27, GOLD, lambda x, y: 2.4 + (0.6 if y == BASE_Y - 35 else 0) - (0.5 if y == BASE_Y - 27 else 0), lit=0)
    cv.rect(fx + 5, BASE_Y - 33, fx + 8, BASE_Y - 30, GOLD, 1.2, lit=0)   # l'emblema


def _bust(talk, smile=True, look=False):
    """El bust del Director per a la pantalla: camisa blanca, corbata vermella, i el somriure amb massa dents.
    Sense `smile`, la boca de sempre; amb `look`, obre els ulls i mira fora de camp (a la dreta)."""
    fig = person(BONFILL, 'D', talk=talk)
    P = fig.load()
    # camisa blanca i corbata vermella al coll (en V, sota la nou)
    for y in range(39, 54):
        half = min(4, 1 + (y - 39) * 0.6)
        for x in range(29, 38):
            if P[x, y][3] and abs(x - 33) <= half:
                tie = abs(x - 33) <= (0 if y < 42 else 1)
                P[x, y] = (230, 230, 236, 255) if not tie else ((180, 30, 40, 255) if y > 41 else (210, 50, 50, 255))
        if 39 < y < 48 and P[33 - int(half) - 1, y][3]:
            P[33 - int(half) - 1, y] = (150, 150, 160, 255)                 # l'ombra del coll de la camisa
    if smile:                                                            # massa dents, i les comissures amunt
        for x in range(30, 34):
            P[x, 29] = (250, 250, 250, 255)
        P[29, 29] = P[34, 29] = (150, 66, 70, 255)
        P[29, 28] = P[34, 28] = (178, 110, 100, 255)
    if look:                                                             # els ulls oberts, mirant a la dreta
        for ex in (27, 35):
            P[ex, 22] = P[ex + 1, 22] = (236, 236, 240, 255)
            P[ex + 2, 22] = (30, 30, 40, 255)
            P[ex, 21] = P[ex + 1, 21] = P[ex + 2, 21] = (150, 100, 90, 255)       # la parpella, ben amunt
        for x in (34, 35, 36, 37, 38):                                   # una cella aixecada
            P[x, 19] = (200, 200, 210, 255)
    return nearest(fig.crop((11, 4, 55, 48)), (88, 88))


SCREENB = [(10, 20, 50), (20, 40, 90), (40, 70, 140), (80, 120, 190)]


def screen(cv, state='logo', talk=False, smile=True, look=False, fx=None):
    """La pantalla de la façana. `state`: 'logo' (el logotip del banc, en espera) o 'director' (el Director Bonfill,
    de cara, amb corbata i somriure d'anunci). `fx`: el soroll d'encendre-la ('glitch', 'soroll', 'ratlla',
    'mig', 'flaix')."""
    x0, y0, x1, y1 = SCREEN
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, SCREENB, 1.0 + (y - y0) / 27, lit=0)
    if state == 'logo':
        cv.glow((x0 + x1) // 2, y0 + 36, 40, (240, 200, 90), 0.2)
        big_word(cv, 'BCMU', (x0 + x1) // 2, y0 + 22, 4)
        slogan = 'EL FUTUR DE TOTHOM'
        text(cv, slogan, (x0 + x1) // 2 - text_width(slogan) // 2, y0 + 52, [(250, 230, 160)], 0, lit=0, flat=(250, 230, 160))
        cv.hline(x0 + 22, x1 - 22, y0 + 47, GOLD, 2.6, lit=0)
    else:
        # el fons de l'estudi: el logotip del banc, desenfocat
        cv.glow(x0 + 20, y0 + 18, 16, (200, 170, 80), 0.25)
        cv.glow(x1 - 16, y0 + 30, 22, (120, 170, 240), 0.2)
        bust = _bust(talk, smile, look)
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        lay.alpha_composite(bust, ((x0 + x1) // 2 - 44, y1 - 83))
        cv.img.alpha_composite(lay.crop((x0, y0, x1 + 1, y1 + 1)), (x0, y0))
        cv.rect(x0, y1 - 8, x1, y1, [(240, 200, 70)], 0, lit=0)          # el rètol de baix
        cv.hline(x0, x1, y1 - 8, [(255, 230, 130)], 0, lit=0)
        text(cv, 'BCMU', x0 + 4, y1 - 6, [(30, 20, 4)], 0, lit=0, flat=(40, 28, 6))
        s = 'EN DIRECTE'
        cv.rect(x1 - text_width(s) - 6, y0 + 3, x1 - 3, y0 + 10, [(150, 20, 30)], 0, lit=0)
        text(cv, s, x1 - text_width(s) - 4, y0 + 5, [(250, 230, 230)], 0, lit=0, flat=(250, 230, 230))
    _screen_fx(cv, fx)
    for y in range(y0, y1 + 1, 2):                                       # les línies de la pantalla
        cv.tint(x0, y, x1, y, (0, 0, 0), 0.18)
    outline(cv, x0 - 1, y0 - 1, x1 + 1, y1 + 1, [(4, 6, 10)])
    outline(cv, x0 - 2, y0 - 2, x1 + 2, y1 + 2, [(30, 34, 40)])
    cv.glow((x0 + x1) // 2, (y0 + y1) // 2, 67, (120, 160, 230), 0.12)


def _screen_fx(cv, fx):
    x0, y0, x1, y1 = SCREEN
    if fx is None:
        return
    if fx == 'glitch':                                                   # unes franges que es desplacen
        for a, b, dx in ((y0 + 9, y0 + 17, 7), (y0 + 30, y0 + 33, -11), (y0 + 50, y0 + 61, 5)):
            band = cv.img.crop((x0, a, x1 + 1, b))
            cv.img.paste(band, (x0 + dx, a))
            cv.img.paste(band.crop((band.width - dx, 0, band.width, b - a)) if dx > 0 else band.crop((0, 0, -dx, b - a)),
                         (x0, a) if dx > 0 else (x1 + 1 + dx, a))
    elif fx in ('soroll', 'soroll2'):                                    # neu de televisor
        seed = 7 if fx == 'soroll' else 8
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                v = int(hr(x, y, seed) * 200) + 30
                cv.flat(x, y, (v, v, min(255, v + 20)))
        for y in range(y0 + (20 if seed == 7 else 52), y0 + (26 if seed == 7 else 57)):   # la franja que roda
            cv.tint(x0, y, x1, y, (255, 255, 255), 0.4)
    elif fx == 'ratlla':                                                 # negre, i una ratlla al mig
        cv.rect(x0, y0, x1, y1, [(4, 6, 12)], 0, lit=0)
        my = (y0 + y1) // 2
        cv.rect(x0 + 8, my - 1, x1 - 8, my + 1, [(200, 220, 255)], 0, lit=0)
        cv.hline(x0 + 20, x1 - 20, my, [(255, 255, 255)], 0, lit=0)
    elif fx == 'mig':                                                    # la imatge s'obre des del mig
        my = (y0 + y1) // 2
        cv.rect(x0, y0, x1, my - 22, [(4, 6, 12)], 0, lit=0)
        cv.rect(x0, my + 22, x1, y1, [(4, 6, 12)], 0, lit=0)
    elif fx == 'flaix':
        cv.tint(x0, y0, x1, y1, (230, 240, 255), 0.35)


def bg(cv, frame=0):
    sky(cv)
    mountains(cv)
    city(cv)
    bcmu(cv, antenna=frame % 3 != 2)
    screen(cv)
    lake(cv)
    jet(cv, frame)
    reflections(cv, frame)


PROPS = {}


@functools.lru_cache(maxsize=1)
def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv.img


def _frames():
    frames = []
    for i in range(6):
        cv = Canvas(light=LIGHT)
        bg(cv, i)
        frames.append(_diff(cv.img, _base()))
    return frames


def _empty():
    return Canvas(light=LIGHT, transparent=True).img


@functools.lru_cache(maxsize=1)
def _top_base():
    """Només el que hi ha sobre l'horitzó (per a les capes de la pantalla i les lletres: el llac no hi entra, que
    el reflex quiet desentonaria amb les ones)."""
    cv = Canvas(light=LIGHT)
    _top(cv)
    return cv.img


def _top(cv, **screen_kw):
    sky(cv)
    mountains(cv)
    city(cv)
    bcmu(cv)
    screen(cv, **screen_kw)


def _screen(**kw):
    cv = Canvas(light=LIGHT)
    _top(cv, **kw)
    d = _diff(cv.img, _top_base())
    a = np.array(d)
    a[HORIZON:, :, 3] = 0
    return Image.fromarray(a)


D = {'state': 'director'}


def _screen_clip(steps):
    return lambda: [_screen(**k) if k is not None else _empty() for k in steps]


PANTALLA = {
    'pantalla': {'frames': lambda: [_empty()], 'frameDuration': 1000, 'loop': False, 'zIndex': 2},
    'pantalla_entra': {'frames': _screen_clip([{'fx': 'glitch'}, {'fx': 'soroll'}, {'fx': 'soroll2'}, {'fx': 'ratlla'},
                                               {**D, 'fx': 'mig'}, {**D, 'fx': 'flaix'}, {**D}]),
                       'frameDuration': 100, 'loop': False, 'prop': 'pantalla'},
    'pantalla_parla': {'frames': _screen_clip([{**D}, {**D, 'talk': True}]), 'frameDuration': 170, 'prop': 'pantalla'},
    'pantalla_quiet': {'frames': _screen_clip([{**D}]), 'frameDuration': 1000, 'loop': False, 'prop': 'pantalla'},
    'pantalla_talla': {'frames': _screen_clip([{**D}, {**D, 'smile': False}, {**D, 'smile': False}, {**D, 'smile': False, 'look': True}]),
                       'frameDuration': 140, 'loop': False, 'prop': 'pantalla'},
    'pantalla_queixa': {'frames': _screen_clip([{**D, 'smile': False, 'look': True},
                                                {**D, 'smile': False, 'look': True, 'talk': True}]),
                        'frameDuration': 170, 'prop': 'pantalla'},
    'pantalla_somriu': {'frames': _screen_clip([{**D, 'smile': False, 'look': True}, {**D, 'smile': False}, {**D}]),
                        'frameDuration': 160, 'loop': False, 'prop': 'pantalla'},
}


# ─── L'espurna de les lletres ──────────────────────────────────────────────

def _glint_frames():
    """Una espurna travessa en diagonal les lletres daurades del capdamunt (i acaba buida)."""
    base = _top_base()
    a0 = np.array(base).astype(int)
    x0, x1 = TOWER
    ys, ye = TOP - 26, TOP - 8
    gold = (a0[:, :, 0] > 170) & (a0[:, :, 2] < 140)
    frames = []
    for i in range(12):
        p = x0 - 6 + (x1 - x0 + 12) * i / 11
        out = np.zeros_like(a0)
        for y in range(ys, ye):
            for x in range(x0 - 4, x1 + 5):
                if not gold[y, x]:
                    continue
                d = abs(x + (y - ys) * 0.7 - p)
                k = 1.0 if d < 2 else 0.5 if d < 4 else 0
                if k:
                    c = a0[y, x, :3] + (np.array([255, 252, 230]) - a0[y, x, :3]) * k
                    out[y, x] = [*c, 255]
        if i == 6:                                                       # i una estrelleta al mig
            cx, cy = (x0 + x1) // 2 + 14, ys - 1
            for dx, dy in ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-2, 0), (2, 0), (0, -2), (0, 2)):
                out[cy + dy, cx + dx] = [255, 255, 240, 255] if abs(dx) + abs(dy) < 2 else [250, 220, 140, 255]
        frames.append(Image.fromarray(out.astype(np.uint8)))
    return frames + [_empty()]


LLETRES = {
    'lletres': {'frames': lambda: [_empty()], 'frameDuration': 1000, 'loop': False, 'zIndex': 2},
    'lletres_brilla': {'frames': _glint_frames, 'frameDuration': 70, 'loop': False, 'prop': 'lletres'},
}


# ─── El pla del pis (la portada sense títol), damunt de Ginebra ────────────
# `pis` és el fons de la portada, opac, damunt de tot; `pis_fon` el fon en trama (quadrets de 2 px, ordre de Bayer)
# i `pis_torna` el torna a posar. `pis_vida` i `senyal` són les capes de la portada (vegeu portada.py).

BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]])
FON = 8


def _dissolve(k):
    """La portada amb una part `k`/FON dels quadrets ja fosa (0: sencera; FON: res)."""
    a = np.array(portada.base()).copy()
    yy, xx = np.mgrid[0:H, 0:W]
    t = BAYER[(yy // 2) % 4, (xx // 2) % 4]
    a[t < k * 16 / FON, 3] = 0
    return Image.fromarray(a)


PIS = {
    'pis': {'frames': lambda: [_dissolve(0)], 'frameDuration': 1000, 'loop': False, 'zIndex': 5},
    'pis_fon': {'frames': lambda: [_dissolve(k) for k in range(1, FON + 1)], 'frameDuration': 80, 'loop': False,
                'prop': 'pis'},
    'pis_torna': {'frames': lambda: [_dissolve(k) for k in range(FON - 1, -1, -1)], 'frameDuration': 80,
                  'loop': False, 'prop': 'pis'},
    'pis_vida': portada.PIS_VIDA,
    'pis_porta': portada.PIS_PORTA,
    'pis_festa': portada.PIS_FESTA,
    'senyal': portada.SENYAL,
    'senyal_va': portada.SENYAL_VA,
}

# L'ordre compta: cada capa abans de les seves etiquetes (draw_placeholders les hi afegeix).
ANIMS = {
    'nit': {'frames': _frames, 'frameDuration': 260},
    **PANTALLA,
    **LLETRES,
    **PIS,
}

# La veu del Director (personatge invisible): sota la pantalla, perquè el text li surti a sobre.
GEOMETRIA = {'things': {}, 'spawns': {'bonfill': (320, 236)}, 'walkable': [(200, 253), (267, 253), (267, 261), (200, 261)]}
