"""
La portada, a 640×360 (vegeu hd/rooms/portada.py, la de 480×270): «SUMA ZERO» damunt la ciutat de nit.
  - a primer terme, a l'esquerra, el bloc del pis: la finestra encesa de verd (l'Iri, l'ordinador i els cables
    que surten per la façana fins a l'antena parabòlica del terrat);
  - els terrats de la ciutat (dipòsits, antenes, finestres) i, a l'horitzó, la torre daurada del BCMU: l'antena
    de l'Iri l'apunta, i un pols de llum hi viatja (l'animació);
  - a baix a la dreta, el neó magenta de La Propina (fa una pampallugua);
  - el títol en lletres grosses (cel·les de 7 px en lloc de 5), verd blavós com els botons, amb bisell a cada
    cel·la, un reflex a dalt, vora fosca i ombra magenta.
Els botons de la GUI `portada` van a 220..420 × 261..328 (×4/3 de 165..315 × 196..246): allà només hi ha terrats.

Capes (com la portada de Ni un ou): el fons no té el títol, que és la capa `titol` («Comença» l'esvaeix i el pròleg
comença al mateix pla). `pis_vida` és el bucle d'espera: l'Iri tecleja (el codi corre al monitor), el neó de La
Propina fa pampallugues, la tele del veí, el led de la parabòlica, el llum de la torre i alguna estrella.
El pròleg (proleg_ginebra.py) fa servir aquest mateix pla, i les animacions que hi passen són aquí:
  - `senyal_va`: un pols de llum surt de la parabòlica i arriba a la torre del BCMU, que s'il·lumina;
  - `pis_porta`: el monitor fa un flaix, hi surt una porta oberta i l'Iri aixeca els braços; `pis_festa`, el bucle.
"""
import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

import functools
import math

from hd.pix import Light, Canvas, W, H, hr
from hd.rooms.comu import obox, outline, cable, text, text_width, _diff, NEON
from room_designs import LLETRES

# Art a 2× (1280×720 per a una sala de 640×360): el mateix dibuix, amb les formes, el dither i la llum a la
# resolució real (hd1280/canvas2x.py); el motor el mostra a 1/2 (artScale al .room.json).
ART_SCALE = 2
from hd1280.canvas2x import Canvas2x as Canvas  # noqa: E402,F811
from hd.pix import Canvas as Canvas1x  # noqa: E402,F401  (llenços auxiliars en píxels de sala: figures, textos)

SKYP = [(4, 2, 12), (8, 6, 22), (14, 10, 34), (22, 14, 46), (34, 18, 58), (50, 22, 70), (70, 28, 80), (96, 36, 88)]
ROOF = [(4, 3, 10), (8, 6, 16), (12, 10, 22), (18, 14, 30), (26, 20, 40)]
BLOCK = [(6, 5, 10), (12, 10, 18), (20, 16, 26), (30, 24, 36), (42, 34, 48), (58, 48, 62)]
WARM = [(60, 36, 10), (140, 90, 30), (220, 160, 70), (250, 214, 130)]
TEAL = [(4, 30, 34), (8, 60, 64), (14, 100, 100), (24, 144, 140), (60, 196, 170), (150, 240, 210), (230, 255, 244)]
GOLD = [(60, 40, 6), (130, 92, 16), (200, 150, 30), (240, 200, 70), (255, 236, 150)]
SHADOW = [(50, 6, 44), (70, 10, 60), (110, 20, 88), (140, 26, 108)]
EDGE = [(6, 10, 22)]
TITLE_Y = 40
S = 7                                     # mida del «píxel» de les lletres
DISH = (165, 117)
TOWER_TOP = (565, 149)
TOWER_X = (547, 584)
N = 12                                    # fotogrames del bucle (els 10 primers, el pols)

LIGHT = Light(ambient=0.0)


def sky(cv, frame=0):
    for y in range(0, 267):
        for x in range(W):
            cv.put(x, y, SKYP, 0.6 + y / 40 + (hr(x // 3, y // 3) - 0.5) * 0.2, lit=0)
    for i in range(160):
        x, y = int(hr(i, 11) * W), int(hr(i, 12) * 147)
        b = hr(i, 13)
        if b > 0.75 and hr(i, 14) > 0.6 and (frame + i) % N_VIDA in (3, 4):   # algunes fan pampallugues
            b = 0.5
        cv.flat(x, y, (210, 200, 240) if b > 0.75 else (110, 100, 150) if b > 0.3 else (70, 60, 104))
        if b > 0.96:
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                cv.flat(x + dx, y + dy, (96, 84, 136))


def tower(cv, frame=0, flash=0.0):
    """La torre del BCMU, petita i daurada, a l'horitzó. `flash`: el senyal de l'Iri hi acaba d'arribar."""
    x0, x1 = TOWER_X
    top = TOWER_TOP[1]
    for y in range(top, 253):
        for x in range(x0, x1 + 1):
            cv.put(x, y, GOLD, 1.0 + (0.8 if (y - top) % 7 == 0 else 0) + (1.2 if x - x0 < 3 else 0)
                   - (0.5 if x1 - x < 2 else 0) - (y - top) / 107, lit=0)
    for fy in range(top + 4, 248, 7):
        for fx in range(x0 + 4, x1 - 3, 6):
            if hr(fx, fy, 4) > 0.5:
                cv.rect(fx, fy, fx + 3, fy + 2, GOLD, 3.6, lit=0)
    cv.rect(x0 - 1, top - 3, x1 + 1, top - 1, GOLD, 2.6, lit=0)        # el coronament
    cx = (x0 + x1) // 2
    cv.vline(cx, top - 16, top - 4, GOLD, 2.0, lit=0)                    # l'antena
    cv.flat(cx, top - 17, (110, 30, 30) if frame % N_VIDA == 6 else (255, 90, 70))
    w = text_width('BCMU')
    text(cv, 'BCMU', cx - w // 2, top - 11, GOLD, 4, lit=0)
    cv.glow(cx, top + 27, 61, (255, 200, 90), 0.22)
    if flash:
        cv.glow(cx, top - 17, 6 + 10 * flash, (150, 255, 220), 0.9 * flash)
        cv.flat(cx, top - 17, (230, 255, 244))
        cv.glow(cx, top + 40, 40, (120, 255, 220), 0.25 * flash)


def roofs(cv):
    """Els terrats de la ciutat, en dos plans."""
    for plane, (base, hmin, hmax, lvl, seed) in enumerate(((248, 13, 45, 1.6, 3), (261, 21, 67, 0.8, 5))):
        x = 0
        i = 0
        while x < W:
            w = 24 + int(hr(i, seed) * 40)
            h = hmin + int(hr(i, seed + 1) * (hmax - hmin))
            top = base - h
            for yy in range(top, 275):
                for xx in range(x, min(W, x + w)):
                    cv.put(xx, yy, ROOF, lvl + (0.4 if yy == top else 0) - (0.3 if xx == x + w - 1 else 0), lit=0)
            # finestres
            for wy in range(top + 5, 267, 8):
                for wx in range(x + 4, x + w - 4, 7):
                    r = hr(wx, wy, seed + 2)
                    if r > 0.8:
                        cv.rect(wx, wy, wx + 2, wy + 3, WARM, lambda px, py: 1.6 + plane + (0.5 if py == wy else 0), lit=0)
                        if hr(wx, wy, seed + 9) > 0.6:                   # una cortina mig tirada
                            cv.rect(wx, wy, wx, wy + 3, WARM, 0.6 + plane, lit=0)
                    elif r > 0.77:
                        cv.rect(wx, wy, wx + 2, wy + 3, [(60, 90, 160), (120, 160, 230)], 1, lit=0)
            # un dipòsit d'aigua o una antena, de tant en tant
            if hr(i, seed + 3) > 0.6:
                cv.rect(x + 5, top - 9, x + 16, top - 2, ROOF, lambda px, py: lvl + 0.6 + (0.4 if px < x + 7 else 0), lit=0)
                cv.hline(x + 4, x + 17, top - 10, ROOF, lvl + 1.0, lit=0)   # la tapa
                cv.hline(x + 5, x + 16, top - 6, ROOF, lvl + 0.2, lit=0)    # el cèrcol
                for lx in (x + 6, x + 15):
                    cv.vline(lx, top - 2, top, ROOF, lvl + 0.6, lit=0)
            elif hr(i, seed + 4) > 0.6:
                ax = x + w // 2
                cv.vline(ax, top - 13, top, ROOF, lvl + 1.0, lit=0)
                cv.hline(ax - 4, ax + 4, top - 9, ROOF, lvl + 1.0, lit=0)
                cv.hline(ax - 2, ax + 2, top - 12, ROOF, lvl + 1.0, lit=0)
            x += w
            i += 1

WIN = (53, 187, 117, 243)                 # la finestra del pis
SIL = [(4, 10, 12)]
RAISE = (0, 0, 0, 0, 1, 2, 2, 2, 2, 2, 2, 2)   # 'porta': els braços (0 avall, 1 a mitges, 2 enlaire)


def door_icon(cv, on=True):
    """Al monitor: una porta oberta, amb llum a dins i la fulla girada cap a fora."""
    cv.rect(88, 203, 104, 213, TEAL, 5.0, lit=0)
    cv.rect(95, 204, 101, 213, TEAL, 1.0, lit=0)                         # el marc
    cv.rect(96, 205, 100, 213, [(230, 255, 244)] if on else TEAL, 0 if on else 5.6, lit=0)   # la llum de l'altra banda
    for x in range(90, 96):                                              # la fulla, oberta cap a nosaltres
        d = 95 - x
        cv.vline(x, 205 - d // 2, 213 + d // 3, TEAL, 2.0 + (0.6 if x == 90 else 0), lit=0)
    cv.flat(91, 209, TEAL[6])                                            # el pom
    if on:
        cv.line(100, 213, 104, 213, TEAL, 6.4, lit=0)                    # la llum que surt per terra


def window(cv, frame=0, mode='espera', k=0):
    """La finestra del pis: verd de pantalla, i l'Iri retallada a contrallum."""
    wx0, wy0, wx1, wy1 = WIN
    flash = (1.0, 0.6, 0.3, 0.15)[k] if mode == 'porta' and k < 4 else 0.0
    arms = 2 if mode == 'festa' else RAISE[min(k, len(RAISE) - 1)] if mode == 'porta' else 0
    lean = 1 if mode == 'porta' and 2 <= k < 4 else 0                    # se n'aparta, de la sorpresa
    for y in range(wy0, wy1 + 1):
        for x in range(wx0, wx1 + 1):
            cv.put(x, y, TEAL, 2.6 + flash * 2.2 + (1.2 * max(0, 1 - math.hypot(x - 93, y - 213) / 29)), lit=0)
    sil = SIL
    cv.rect(85, 200, 107, 216, TEAL, 6.0, lit=0)                         # el monitor
    if mode == 'espera':
        cv.rect(88, 203, 104, 213, TEAL, lambda x, y: 4.4 + (0.6 if (y - 203) % 3 == 0 else 0), lit=0)   # línies de codi
        for j in range(4):                                               # el codi corre, i l'última ratlla s'escriu
            n = int(hr(j + frame // 2, 21) * 12)
            if j == 3:
                n = n * (1 + frame % 2) // 2
            cv.hline(89, 89 + n, 204 + j * 3, TEAL, 6.0, lit=0)
    elif flash > 0.5:
        cv.rect(86, 201, 106, 215, [(230, 255, 244)], 0, lit=0)
    else:
        door_icon(cv, on=mode == 'festa' or k % 2 == 0 or k > 8)
    cv.rect(93, 216, 99, 221, sil, 0, lit=0)                             # el peu
    cv.rect(109, 208, 114, 221, TEAL, 3.6, lit=0)                        # el segon monitor, de cantó
    outline(cv, 109, 208, 114, 221, [(4, 10, 12)])
    hx, hy = 75 - lean, 208 - (1 if arms == 2 and (frame + k) % 2 else 0)
    cv.disc(hx, hy, 6.5, 8, sil, 0, lit=0)                               # el cap, amb la cua
    cv.line(hx - 7, hy, hx - 12, hy + 13, sil, 0, lit=0)
    cv.line(hx - 6, hy + 1, hx - 11, hy + 14, sil, 0, lit=0)
    cv.line(hx - 5, hy + 1, hx - 10, hy + 14, sil, 0, lit=0)
    cv.rect(65, 216, 84, wy1, sil, 0, lit=0)                             # les espatlles i la cadira
    cv.vline(64, 222, wy1, sil, 0, lit=0)
    if arms:                                                             # els braços enlaire, amb els punys
        up = arms == 2
        bob = (frame + k) % 2 if up and mode == 'festa' else 0
        for side, (sx, ex, ey) in enumerate(((66, 61 if up else 58, 199 if up else 209), (83, 89 if up else 92, 199 if up else 209))):
            ey += bob if side == 0 else 1 - bob if mode == 'festa' else 0
            for d in range(3):
                cv.line(sx + d - 1, 218, ex + d - 1, ey + 2, sil, 0, lit=0)
            cv.rect(ex - 1, ey - 1, ex + 2, ey + 2, sil, 0, lit=0)
    cv.disc(hx + 6, hy - 3, 2, 3, [(200, 30, 40)], 0, lit=0)             # l'auricular vermell
    cv.line(hx + 6, hy - 6, hx + 1, hy - 9, [(200, 30, 40)], 0, lit=0)   # la diadema de l'auricular
    for dx, col in enumerate(((220, 50, 50), (230, 200, 60), (60, 190, 90))):
        cv.flat(hx - 4 + dx * 2, hy - 8 + (1 if dx == 1 else 0), col)    # la diadema de l'Iri, de tres colors
    cv.rect(wx0, 228, wx1, 229, sil, 0, lit=0)                           # la taula
    cv.rect(88, 225, 102, 227, TEAL, 3.2, lit=0)                         # el teclat
    cv.rect(105, 222, 108, 227, [(8, 20, 22), (40, 60, 60)], 1, lit=0)   # la tassa
    cv.vline(85, 230, wy1, sil, 0, lit=0)                                # la pota de la taula
    for x in range(wx0, wx1 + 1, 2):                                     # el reflex al vidre
        cv.tint(x, wy0, x, wy0 + 1, (230, 255, 244), 0.15)
    cv.vline((wx0 + wx1) // 2 - 12, wy0, wy1, BLOCK, 1.0, lit=0)        # el muntant
    outline(cv, wx0 - 1, wy0 - 1, wx1 + 1, wy1 + 1, BLOCK)
    cv.rect(wx0 - 4, wy1 + 1, wx1 + 4, wy1 + 4, BLOCK, lambda x, y: 3.4 + (0.6 if y == wy1 + 1 else 0), lit=0)
    cv.glow(85, 213, 80, (60, 230, 190), 0.16 + 0.3 * flash)


def block(cv, frame=0, mode='espera', k=0):
    """El bloc del pis, a primer terme: la finestra encesa i els cables fins a la parabòlica.
    `mode`: 'espera' (l'Iri tecleja), 'porta' (fotograma `k` de la porta oberta) o 'festa' (els braços enlaire)."""
    x0, x1, top = 0, 187, 128
    for y in range(top, H):
        for x in range(x0, x1 + 1):
            row = y // 8
            brick = (y % 8 == 0) or ((x + (row % 2) * 9) % 18 == 0)
            cv.put(x, y, BLOCK, (2.0 if brick else 2.9) + (hr(x // 3, y // 3) - 0.5) * 0.3 - (x / 267) - max(0, (y - 267) / 80), lit=0)
    cv.rect(x0, top - 4, x1 + 3, top, BLOCK, lambda x, y: 3.2 + (0.6 if y == top - 4 else 0), lit=0)   # l'ampit del terrat
    cv.vline(x1 + 1, top + 1, H - 1, BLOCK, 1.2, lit=0)                 # el cantó, a l'ombra
    # les altres finestres, apagades o amb la tele
    for (wx, wy) in ((19, 149), (128, 149), (128, 267), (19, 267)):
        cv.rect(wx, wy, wx + 29, wy + 35, [(4, 4, 8), (10, 10, 18)], 0.6, lit=0)
        cv.vline(wx + 14, wy, wy + 35, BLOCK, 1.4, lit=0)                # el muntant
        outline(cv, wx - 1, wy - 1, wx + 30, wy + 36, BLOCK)
        cv.rect(wx - 3, wy + 36, wx + 32, wy + 38, BLOCK, lambda x, y: 3.4 if y == wy + 36 else 2.2, lit=0)   # l'ampit
    tv = (0.6, 0.6, 1.0, 0.6, 0.3, 0.6, 0.8, 0.6)[frame % N_VIDA]          # algú mira la tele, que fa pampallugues
    cv.rect(129, 268, 156, 300, [(20, 30, 70), (40, 60, 130)], tv, lit=0)
    cv.glow(140, 284, 14, (90, 120, 230), 0.15 + 0.15 * tv)
    cv.disc(147, 296, 4, 5, [(8, 10, 20)], 0, lit=0)                     # el cap de qui mira, a contrallum
    cv.vline(142, 268, 302, BLOCK, 1.4, lit=0)
    for j in range(4):                                                   # una persiana mig abaixada al pis de dalt
        cv.hline(129, 156, 150 + j * 3, BLOCK, 1.6, lit=0)
    wx0, wy0, wx1, wy1 = WIN
    window(cv, frame, mode, k)
    # els cables: surten per la finestra i pugen per la façana fins a la parabòlica
    for j, col in enumerate(([(20, 20, 26), (60, 60, 70)], [(60, 10, 14), (150, 30, 30)], [(10, 30, 50), (30, 80, 120)])):
        cable(cv, [(wx1 + 1, wy0 + 11 + j * 4), (wx1 + 40, wy0 + 27), (157 + j * 3, 173), (DISH[0] - 3 + j * 3, DISH[1] + 11)], col, 1.0)
    # la parabòlica, que apunta a la torre
    dx, dy = DISH
    cv.rect(dx - 1, dy + 3, dx + 1, top, ROOF, lambda x, y: 2.6 + (0.6 if x == dx - 1 else 0), lit=0)
    cv.line(dx - 6, top - 1, dx, dy + 8, ROOF, 2.2, lit=0)               # el puntal
    cv.disc(dx + 4, dy - 3, 11, 8, [(40, 44, 54), (90, 96, 110), (150, 156, 170), (200, 206, 214)], lambda nx, ny: 2.4 + nx - ny * 0.6, lit=0)
    for a in range(0, 360, 4):                                           # la vora del plat
        cv.put(round(dx + 4 + math.cos(math.radians(a)) * 11), round(dy - 3 + math.sin(math.radians(a)) * 8),
               [(40, 44, 54), (90, 96, 110)], 0.6, lit=0)
    cv.line(dx + 4, dy - 3, dx + 16, dy - 8, [(200, 206, 214)], 0, lit=0)
    cv.line(dx + 4, dy + 3, dx + 16, dy - 8, [(150, 156, 170)], 0, lit=0)   # el segon braç del LNB
    if frame % 4 == 0:                                                   # el led del LNB, que parpelleja
        cv.rect(dx + 15, dy - 9, dx + 17, dy - 7, [(90, 20, 20)], 0, lit=0)
    else:
        cv.rect(dx + 15, dy - 9, dx + 17, dy - 7, [(250, 60, 60)], 0, lit=0)
        cv.flat(dx + 16, dy - 8, (255, 160, 150))


def bar_sign(cv, on=True):
    """A baix a la dreta, el neó de La Propina en un local baix (ara sí, del dret)."""
    obox(cv, 453, 285, 637, H - 1, ROOF, 1.4, lit=0)
    cv.hline(453, 637, 290, ROOF, 2.6, lit=0)                            # la cornisa
    w = text_width('LA PROPINA')
    col = (255, 120, 200) if on else (110, 40, 90)
    tx = 545 - w // 2
    cv.rect(tx - 5, 295, tx + w + 4, 309, [(16, 6, 16)], 0, lit=0)      # el rètol, de fons fosc
    outline(cv, tx - 5, 295, tx + w + 4, 309, [(60, 20, 50)] if on else [(30, 10, 26)])
    text(cv, 'LA PROPINA', tx, 299, NEON, 0, lit=0, flat=col)
    if on:
        cv.glow(545, 302, 40, (255, 90, 200), 0.35)
    for ax in (469, 595):                                                # els aparadors
        cv.rect(ax, 315, ax + 27, H - 1, [(30, 14, 30), (60, 26, 50)], lambda x, y: 1.0 + (0.6 if (x - y) % 11 == 0 else 0), lit=0)
        outline(cv, ax - 1, 314, ax + 28, H, [(8, 4, 10)])
    cv.rect(528, 318, 562, H - 1, [(14, 6, 14), (40, 18, 36)], 0.6, lit=0)   # la porta
    outline(cv, 527, 317, 563, H, [(8, 4, 10)])
    cv.flat(558, 340, (200, 160, 80))                                    # el pom


def title(cv):
    """«SUMA ZERO»: lletres de 5×7 a cel·les de 7 px, cos verd blavós amb degradat i bisell, vora fosca i
    ombra magenta."""
    word = 'SUMA ZERO'
    width = len(word) * 6 * S - S
    x0 = (W - width) // 2
    cells = []
    for i, ch in enumerate(word):
        for r, bits in enumerate(LLETRES[ch]):
            for c, bit in enumerate(bits):
                if bit == '1':
                    cells.append((x0 + (i * 6 + c) * S, TITLE_Y + r * S))
    filled = set(cells)
    for x, y in cells:                                                   # l'ombra magenta
        cv.rect(x + 4, y + 4, x + S + 3, y + S + 3, SHADOW, lambda px, py: 3.4 - (py - TITLE_Y) / 40, lit=0)
    for x, y in cells:                                                   # la vora
        cv.rect(x - 1, y - 1, x + S, y + S, EDGE, 0, lit=0)
    hl = TITLE_Y + 2.2 * S                                               # la ratlla del reflex
    for x, y in cells:
        top_open = (x, y - S) not in filled
        bot_open = (x, y + S) not in filled
        left_open = (x - S, y) not in filled
        right_open = (x + S, y) not in filled
        for py in range(y, y + S):
            for px in range(x, x + S):
                lvl = 5.6 - (py - TITLE_Y) / 12
                if py == y and top_open:
                    lvl += 1.0
                if px == x and left_open:
                    lvl += 0.5
                if px == x + S - 1 and right_open:
                    lvl -= 0.8
                if py == y + S - 1 and bot_open:
                    lvl -= 0.7
                if py < hl - (px - x0) * 0.04:                           # el vidre de dalt, més clar
                    lvl += 0.5
                cv.put(px, py, TEAL, lvl, lit=0)
    for x, y in cells:                                                   # una espurna a algunes cantonades
        if (x, y - S) not in filled and (x - S, y) not in filled and hr(x, y, 41) > 0.6:
            cv.flat(x + 1, y + 1, TEAL[6])
    cv.glow(W // 2, TITLE_Y + 21, 200, (60, 220, 190), 0.06)


def signal(cv, frame):
    """El pols de llum que va de la parabòlica a la torre, amb una cueta."""
    ax, ay = DISH[0] + 16, DISH[1] - 8
    bx, by = TOWER_TOP[0] + 1, TOWER_TOP[1] - 17
    n = 10
    for k, (dt, a) in enumerate(((0, 1.0), (0.025, 0.5), (0.05, 0.25))):
        t = frame / n - dt
        if t < 0:
            continue
        px = ax + (bx - ax) * t
        py = ay + (by - ay) * t - math.sin(t * math.pi) * 40
        if k == 0:
            cv.glow(px, py, 8, (120, 255, 220), 0.7)
            cv.rect(px - 1, py, px + 1, py, [(220, 255, 240)], 0, lit=0)
            cv.flat(px, py - 1, (220, 255, 240))
            cv.flat(px, py + 1, (220, 255, 240))
        else:
            cv.glow(px, py, 5, (120, 255, 220), 0.5 * a)
            cv.flat(px, py, (120, 220, 200))


def bg(cv, frame=0, mode='espera', k=0, flash=0.0):
    """L'escena sense el títol (el títol és la capa `titol`; el pròleg fa servir aquest mateix fons)."""
    sky(cv, frame)
    tower(cv, frame, flash)
    roofs(cv)
    block(cv, frame, mode, k)
    bar_sign(cv, on=frame % N_VIDA != 5)


PROPS = {}

N_VIDA = 8                                # fotogrames del bucle d'espera
VIDA_MS = 220


@functools.lru_cache(maxsize=1)
def base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv.img


def _layer(**kw):
    """Un fotograma de capa: només el que canvia respecte del fons."""
    cv = Canvas(light=LIGHT)
    bg(cv, **kw)
    return _diff(cv.img, base())


def _empty():
    return Canvas(light=LIGHT, transparent=True).img


def _title_frames():
    cv = Canvas(light=LIGHT, transparent=True)
    title(cv)
    return [cv.img]


def _signal_frames():
    """El pols va de la parabòlica a la torre (10 fotogrames), la torre s'il·lumina i s'apaga; acaba buit."""
    frames = []
    for i in range(10):
        cv = Canvas(light=LIGHT)
        bg(cv)
        signal(cv, i)
        frames.append(_diff(cv.img, base()))
    frames += [_layer(flash=f) for f in (1.0, 0.8, 0.6, 0.4, 0.2)]
    return frames + [_empty()]


# Totes dues sales: `pis_vida` és la capa del bucle d'espera (a la portada, damunt del fons; al pròleg, damunt de la
# capa opaca `pis`), i les altres són etiquetes d'aquesta capa o de `senyal`, que les indicacions d'escena hi posen.
PIS_VIDA = {'frames': lambda: [_layer(frame=i) for i in range(N_VIDA)], 'frameDuration': VIDA_MS, 'zIndex': 6}
PIS_PORTA = {'frames': lambda: [_layer(frame=i % N_VIDA, mode='porta', k=i) for i in range(len(RAISE))],
             'frameDuration': 120, 'loop': False, 'prop': 'pis_vida'}
PIS_FESTA = {'frames': lambda: [_layer(frame=i, mode='festa') for i in range(2)], 'frameDuration': 260,
             'prop': 'pis_vida'}
SENYAL = {'frames': lambda: [_empty()], 'frameDuration': 1000, 'loop': False, 'zIndex': 6}
SENYAL_VA = {'frames': _signal_frames, 'frameDuration': 110, 'loop': False, 'prop': 'senyal'}

ANIMS = {
    'pis_vida': {**PIS_VIDA, 'zIndex': 1},
    'titol': {'frames': _title_frames, 'frameDuration': 1000, 'loop': False, 'zIndex': 3},
}

GEOMETRIA = {'things': {}, 'spawns': {}, 'walkable': [(200, 253), (267, 253), (267, 261), (200, 261)]}
