#!/usr/bin/env python3
"""
La barra de verbs d'Aigua Verne a 640×360 (la franja de y=260 a 359, 640×100).

Estil: el tauler de comandament de la Cantimplora, la nau cisterna vella. Planxa verd oliva gastada, amb
reblons, ratllades que deixen veure el metall i regalims de rovell; una franja de seguretat taronja i negra
separa l'escena del tauler; els verbs són tecles de planxa amb text crema (taronja sota el ratolí); les caselles
de l'inventari són pantalletes verdes de fòsfor amb cantoneres de visor; el botó «Canvia» és una pantalla rodona
de radar amb la cara de l'altra protagonista; a baix a l'esquerra, el manòmetre del dipòsit (gairebé buit), i a
la dreta, l'etiqueta de la gota blava de Verne, mig arrencada.

Mateixa geometria i mateixos ids que la de Ni un ou (no es mou res): només canvia el dibuix.

    from hd640.gui import verb_bar
    img = verb_bar()                                  # Image RGBA 640×100, per enganxar a (0, 260)
    img = verb_bar({'hover': 'look', 'line': 'Mira la bomba de Verne'})

Les icones d'inventari són les de hd640/items.py. La cara de la pantalla rodona és el personatge de 640 de cara
(fotograma IdleD) de placeholder-art/<id>/ o, si encara no hi és, de hd640/characters/<id>/; si no n'hi ha cap,
hi surt una silueta de fòsfor (vegeu `face`).

`python3 hd640/gui.py <sortida.png>` desa la barra sola (×1 i ×3).
"""
import json
import math
import sys
from pathlib import Path

from PIL import Image

TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))

import hd640  # noqa: E402,F401  (posa la llibreria a 640×360)
from hd.pix import Canvas, hr, mix, RUST, IRON  # noqa: E402

GAME = TOOLS.parents[2] / 'aigua-verne/src/game'
ART = TOOLS.parent / 'placeholder-art'            # els personatges del joc (draw_characters.py)
W, Y0, BH = 640, 260, 100          # la barra: 640×100, a partir de y=260 de la pantalla

# ─── Paleta: el tauler de la Cantimplora ────────────────────────────────────
OLIVA = [(8, 9, 5), (15, 17, 9), (23, 26, 14), (33, 37, 20), (44, 49, 27), (57, 63, 35), (73, 79, 45),
         (93, 98, 59), (118, 121, 78)]                      # planxa pintada de verd oliva
TARONJA = [(48, 14, 6), (98, 34, 10), (160, 62, 14), (214, 98, 22), (244, 138, 44), (255, 184, 106),
           (255, 222, 170)]                                 # taronja de seguretat
FOSFOR = [(4, 10, 6), (7, 18, 9), (11, 30, 14), (18, 50, 22), (32, 84, 36), (60, 136, 60), (112, 196, 102),
          (182, 240, 160)]                                  # pantalles verdes de fòsfor
CREMA = [(36, 32, 20), (84, 76, 52), (142, 132, 100), (198, 188, 150), (232, 222, 186), (250, 244, 218)]
BLAU = [(8, 22, 58), (16, 46, 110), (30, 84, 170), (66, 130, 220), (150, 200, 245), (226, 242, 255)]  # la gota
ETIQ = [(70, 72, 64), (128, 130, 120), (184, 186, 176), (222, 222, 212), (244, 244, 236)]           # l'adhesiu blanc
NEGRE = [(6, 6, 4), (14, 14, 10), (24, 24, 18), (36, 36, 28)]
VIDRE = (6, 14, 8)                 # el negre verdós de les pantalles apagades
LINIA = (9, 21, 11)                # les línies d'escaneig

# Colors del text (els posa el motor; hd640/gui_rest.py els copia als .gui.json).
TEXT = '#e6dcb6'        # verb en repòs: crema
TEXT_HOVER = '#ff9a32'  # verb sota el ratolí: taronja de seguretat
TEXT_OUTLINE = '#070804'
VERB_LINE = '#d6e2b8'   # la frase «Mira la bomba de Verne»: crema verdós, com si fos de pantalla
OPTION = TEXT           # opcions de diàleg
OPTION_HOVER = TEXT_HOVER
TITLE = '#f0a446'       # títols dels menús: taronja
LABEL = TEXT
DISABLED = '#5f644a'

# ─── Geometria (coordenades dins la barra, y=0 és la y=260 de la pantalla) ──
STRIP_H = 13                       # franja fosca de la frase
ROPE_Y = 13                        # la franja de seguretat, 4 px (on la de Ni un ou tenia la corda)
VERB_H = 21
VERB_COLS = ((65, 73), (141, 99), (244, 73))          # (x, amplada)
VERB_ROWS = (21, 47, 73)
VERB_IDS = (('give', 'pickUp', 'use'), ('open', 'talkTo', 'push'), ('close', 'look', 'pull'))
VERB_TEXT = {'give': 'Dona', 'pickUp': 'Agafa', 'use': 'Usa', 'open': 'Obre', 'talkTo': 'Parla',
             'push': 'Empeny', 'close': 'Tanca', 'look': 'Mira', 'pull': 'Estira'}
INV_X, INV_Y, SLOT_W, SLOT_H, GAP = 336, 20, 65, 36, 4
ARROWS = {'up': (320, 20), 'down': (320, 60)}          # 13×36
MENU = (36, 69, 25)
CANVIA = (4, 21, 57, 43)
PORT = (32, 42)                                         # centre de la pantalla rodona
SEAMS = (62, 614)
GAUGE = (19, 82, 10)                                    # el manòmetre del dipòsit: centre i radi


def slots():
    for r in range(2):
        for c in range(4):
            yield INV_X + c * (SLOT_W + GAP), INV_Y + r * (SLOT_H + GAP)


# ─── Font de 640: és a hd640/font.py ───────────────────────────────────────
from hd640.font import font640, text_width, draw_text as _draw_text  # noqa: E402


def draw_text(img, glyphs, s, x, y, color, outline=TEXT_OUTLINE, space=4):
    """Text de mapa de bits a (x, y) (dalt de la línia), amb la vora de baix a la dreta com al joc."""
    _draw_text(img, glyphs, s, x, y, color, outline=outline, space=space)


# ─── Eines (les fa servir també hd640/gui_rest.py) ─────────────────────────

def box(cv, x0, y0, x1, y1, ramp, lvl, edge=True):
    """Capsa plana: llum a dalt i a l'esquerra, ombra a baix i a la dreta."""
    cv.rect(x0, y0, x1, y1, ramp, lvl, lit=0)
    if edge:
        cv.hline(x0, x1, y0, ramp, lvl + 1.2, lit=0)
        cv.vline(x0, y0, y1, ramp, lvl + 0.7, lit=0)
        cv.hline(x0, x1, y1, ramp, lvl - 1.4, lit=0)
        cv.vline(x1, y0, y1, ramp, lvl - 1.0, lit=0)


def dark(cv, x, y, k):
    """Enfosqueix un píxel ja pintat cap al negre oliva."""
    if 0 <= x < cv.w and 0 <= y < cv.h:
        o = cv.P[x, y]
        if o[3]:
            cv.P[x, y] = mix(o, OLIVA[0], k) + (o[3],)


def rivet(cv, x, y, lvl=6.6):
    """Un rebló petit: punt clar i ombra a baix a la dreta."""
    cv.put(x, y, OLIVA, lvl, lit=0)
    cv.put(x + 1, y + 1, OLIVA, 1.0, lit=0)


def corners(cv, x0, y0, x1, y1, n=4, ramp=None, lvl=4.0):
    """Cantoneres en L (de visor, si són de fòsfor; de seguretat, si són taronja)."""
    ramp = ramp or TARONJA
    for (cx, cy, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        for i in range(n):
            cv.put(cx + sx * i, cy, ramp, lvl if sy > 0 else lvl - 0.8, lit=0)
            cv.put(cx, cy + sy * i, ramp, lvl - 0.6 if sx > 0 else lvl - 1.2, lit=0)


def well(cv, x0, y0, x1, y1, face=1.6, brass=True):
    """Un buit fosc enfonsat a la planxa: ombra a dalt i a l'esquerra, llum a baix i a la dreta."""
    cv.rect(x0, y0, x1, y1, OLIVA, face, lit=0)
    cv.hline(x0, x1, y0, OLIVA, face - 1.2, lit=0)
    cv.vline(x0, y0, y1, OLIVA, face - 1.0, lit=0)
    cv.hline(x0 + 1, x1, y1, OLIVA, face + 3.2, lit=0)
    cv.vline(x1, y0 + 1, y1, OLIVA, face + 2.6, lit=0)
    if brass:
        corners(cv, x0 + 2, y0 + 2, x1 - 2, y1 - 2)


def screen(cv, x0, y0, x1, y1, glow=0.0):
    """Una pantalla de fòsfor apagada: negre verdós amb línies d'escaneig i un reflex al cantó de dalt."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            c = LINIA if (y - y0) % 2 else VIDRE
            if glow:
                c = mix(c, FOSFOR[3], glow)
            cv.flat(x, y, c)
    for i in range(5):                                  # el reflex del vidre
        cv.flat(x0 + 1 + i, y0 + 1, mix(VIDRE, FOSFOR[4], 0.55 - i * 0.1))
    for i in range(3):
        cv.flat(x0 + 1, y0 + 2 + i, mix(VIDRE, FOSFOR[4], 0.45 - i * 0.12))


def hazard(cv, x0, x1, y, h=4, period=10, worn=True):
    """Franja de seguretat: ratlles taronja i negres en diagonal, amb la pintura gastada a trossos."""
    for x in range(x0, x1 + 1):
        for dy in range(h):
            on = ((x + dy) // (period // 2)) % 2 == 0
            if on:
                v = 3.6 - dy * 0.25 + (hr(x // 3, y + dy) - 0.5) * 0.5
                if dy == 0:
                    v += 0.8
                cv.put(x, y + dy, TARONJA, v, lit=0)
            else:
                cv.put(x, y + dy, NEGRE, 2.0 - dy * 0.3, lit=0)
            if worn and on and hr(x // 2, dy, 77) > 0.9:        # la pintura saltada: el negre de sota
                cv.put(x, y + dy, NEGRE, 2.4, lit=0)
    for x in range(x0, x1 + 1):
        dark(cv, x, y + h, 0.55)
        if x % 3 == 0:
            dark(cv, x, y + h + 1, 0.25)


def arrow(cv, cx, cy, up, hover, length=13):
    """Fletxa crema (taronja en hover). cx = columna esquerra del centre."""
    ramp = TARONJA if hover else CREMA
    rows = [(cx - w // 2 + 1, cx + w // 2, i) for i, w in enumerate((2, 4, 6, 8))]
    rows += [(cx, cx + 1, i) for i in range(4, length)]
    y0 = cy - length // 2
    for a, b, i in rows:
        y = y0 + i if up else y0 + length - 1 - i
        for x in range(a, b + 1):
            v = 3.8 if x <= cx else 3.0
            if i == 0:
                v = 4.4
            cv.put(x, y, ramp, v - (0.2 * i if i < 4 else 0.6), lit=0)
        dark(cv, b + 1, y + 1, 0.6)
    if hover:
        cv.glow(cx + 0.5, cy, 9, TARONJA[3], 0.3)


# ─── Peces ─────────────────────────────────────────────────────────────────

def body(cv, y0, y1):
    """La planxa oliva: pintura vella amb gra, ratllades (metall nu), escates i taques de rovell."""
    for y in range(y0, y1 + 1):
        for x in range(W):
            cv.put(x, y, OLIVA, 3.2 - (y - y0) * 0.008 + (hr(x // 4, y // 5) - 0.5) * 0.35
                   + (hr(x // 23, y // 17, 3) - 0.5) * 0.4, lit=0)
    # ratllades: traços curts, una mica inclinats, que deixen veure el metall
    for i in range(26):
        x, y = int(hr(i, 11) * W), int(y0 + 8 + hr(i, 12) * (y1 - y0 - 12))
        n = 3 + int(hr(i, 13) * 7)
        for k in range(n):
            xx, yy = x + k, y + (k * (1 if hr(i, 14) > 0.5 else -1)) // 4
            cv.put(xx, yy, IRON, 4.2 - k * 0.15, lit=0)
            dark(cv, xx, yy + 1, 0.35)
    # escates de pintura i punts de rovell
    for i in range(70):
        x, y = int(hr(i, 1) * W), int(y0 + 6 + hr(i, 2) * (y1 - y0 - 8))
        if hr(i, 3) > 0.8:                                    # rovell: una taca de 2×2, fosca
            for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
                if hr(i, dx, dy) > 0.3:
                    cv.put(x + dx, y + dy, RUST, 1.4 + hr(i, 4, dx) * 1.2, lit=0)
        else:
            cv.put(x, y, OLIVA, 4.8, lit=0)


def rope(cv, y):
    """La franja de seguretat de dalt de tot (té el nom de la corda de Ni un ou per no trencar res)."""
    hazard(cv, 0, W - 1, y, h=4, period=12)


def rust_streak(cv, x, y, n=7, seed=0):
    """Un regalim de rovell que baixa des d'un rebló."""
    for k in range(n):
        if hr(x, y, k, seed) < 0.82 - k * 0.07:
            cv.put(x + (1 if hr(x, k, seed) > 0.85 else 0), y + k, RUST, 2.6 - k * 0.22, lit=0)


def big_rivet(cv, x, y, lvl=5.4):
    """Rebló de 2×2 amb ombra."""
    cv.put(x, y, OLIVA, lvl + 1.6, lit=0)
    cv.put(x + 1, y, OLIVA, lvl + 0.4, lit=0)
    cv.put(x, y + 1, OLIVA, lvl, lit=0)
    cv.put(x + 1, y + 1, OLIVA, lvl - 1.4, lit=0)
    cv.put(x + 2, y + 2, OLIVA, 0.6, lit=0)


def seam(cv, x, y0, y1):
    """Junta entre dues planxes, amb dues fileres de reblons (i el rovell que en regalima)."""
    for y in range(y0, y1 + 1):
        cv.put(x, y, OLIVA, 0.8, lit=0)
        cv.put(x + 1, y, OLIVA, 4.6, lit=0)
    for y in range(y0 + 5, y1 - 2, 12):
        big_rivet(cv, x - 4, y)
        big_rivet(cv, x + 3, y + 6)
        if hr(x, y) > 0.5:
            rust_streak(cv, x - 4, y + 3, 6, seed=y)


def plate(cv, x0, y0, x1, y1, face=4.4):
    """Tecla de planxa: capsa, bisell de 2 px i ombra de contacte."""
    box(cv, x0, y0, x1, y1, OLIVA, face)
    cv.hline(x0 + 1, x1 - 1, y0 + 1, OLIVA, face + 1.0, lit=0)
    for x in range(x0 + 1, x1 + 2):
        dark(cv, x, y1 + 1, 0.5)
    for y in range(y0 + 1, y1 + 1):
        dark(cv, x1 + 1, y, 0.35)


def verb_plate(cv, x0, y0, x1, y1, face=4.6):
    """Tecla de verb: placa bisellada amb quatre cargolets i una ratlleta taronja de seguretat a l'esquerra."""
    plate(cv, x0, y0, x1, y1, face)
    for y in range(y0 + 2, y1 - 1):                     # la cara, amb una mica de gra de pintura
        for x in range(x0 + 2, x1 - 1):
            if hr(x // 2, y, 41) > 0.9:
                cv.put(x, y, OLIVA, face + 0.4, lit=0)
    cv.hline(x0 + 2, x1 - 2, y0 + 2, OLIVA, face + 0.5, lit=0)
    cv.vline(x0 + 1, y0 + 2, y1 - 2, OLIVA, face + 0.6, lit=0)
    cv.hline(x0 + 2, x1 - 1, y1 - 1, OLIVA, face - 0.9, lit=0)
    for bx, by in ((x0 + 3, y0 + 3), (x1 - 4, y0 + 3), (x0 + 3, y1 - 4), (x1 - 4, y1 - 4)):
        cv.put(bx, by, OLIVA, face + 2.6, lit=0)
        cv.put(bx + 1, by + 1, OLIVA, face - 1.6, lit=0)
    # el desgast: on els dits la toquen, una mica de metall a la vora de baix
    for x in range(x0 + 8, x1 - 8):
        if hr(x, y1, 9) > 0.8:
            cv.put(x, y1 - 1, IRON, 3.4, lit=0)


def menu_button(cv):
    x, y, s = MENU
    box(cv, x, y, x + s - 1, y + s - 1, OLIVA, 4.2)
    cv.hline(x + 1, x + s - 2, y + 1, OLIVA, 5.2, lit=0)
    for yy in (y + 6, y + 11, y + 16):
        cv.hline(x + 5, x + s - 7, yy, CREMA, 3.8, lit=0)
        cv.hline(x + 5, x + s - 7, yy + 1, CREMA, 2.6, lit=0)
        cv.hline(x + 6, x + s - 6, yy + 2, OLIVA, 1.6, lit=0)
    corners(cv, x + 2, y + 2, x + s - 3, y + s - 3, n=3, lvl=3.6)


def porthole(cv, hover=False):
    """El botó «Canvia»: una placa amb una pantalla rodona de radar (anella taronja amb marques, fòsfor a dins,
    els cercles i la creu del radar i l'escombrada). La cara hi va a sobre, en un control a part."""
    x, y, w, h = CANVIA
    box(cv, x, y, x + w - 1, y + h - 1, OLIVA, 4.4 if hover else 3.8)
    cv.hline(x + 1, x + w - 2, y + 1, OLIVA, 5.2 if hover else 4.8, lit=0)
    for bx, by in ((x + 3, y + 3), (x + w - 5, y + 3), (x + 3, y + h - 5), (x + w - 5, y + h - 5)):
        big_rivet(cv, bx, by, 5.6)
    cx, cy = PORT
    lift = 1.3 if hover else 0.0
    cv.disc(cx + 0.5, cy + 0.8, 18.5, 18.5, OLIVA, 0.8, lit=0)                      # l'ombra de l'anella
    cv.disc(cx, cy, 17.5, 17.5, NEGRE, lambda nx, ny: 2.6 - nx * 0.6 - ny * 0.8, lit=0)   # el marc, de goma
    cv.disc(cx, cy, 16.0, 16.0, TARONJA, lambda nx, ny: 2.6 + lift - nx * 0.7 - ny, lit=0)  # l'anella pintada
    cv.disc(cx, cy, 14.5, 14.5, NEGRE, lambda nx, ny: 1.2 + nx + ny, lit=0)           # el bisell cap endins
    glow = 0.35 if hover else 0.0
    for yy in range(cy - 14, cy + 15):                                                # el vidre de fòsfor
        for xx in range(cx - 14, cx + 15):
            d = math.hypot(xx - cx, yy - cy)
            if d <= 13.5:
                c = mix(FOSFOR[1], FOSFOR[2], max(0, 1 - d / 13.5) * 0.9 + glow)
                if (yy - cy) % 2:
                    c = mix(c, VIDRE, 0.35)
                cv.flat(xx, yy, c)
    for r in (6, 11):                                                                 # els cercles del radar
        cv.ring(cx, cy, r, FOSFOR, 3.2 + lift, lit=0, step=4)
    for k in range(-12, 13, 2):                                                       # la creu, puntejada
        cv.put(cx + k, cy, FOSFOR, 3.0 + lift, lit=0)
        cv.put(cx, cy + k, FOSFOR, 3.0 + lift, lit=0)
    for i in range(1, 14):                                                            # l'escombrada
        for da in range(0, 28, 4):
            a = math.radians(-50 - da)
            cv.put(round(cx + math.cos(a) * i), round(cy + math.sin(a) * i), FOSFOR, 4.6 + lift - da * 0.07, lit=0)
    for a in range(0, 360, 30):                                                       # les marques de l'anella
        bx = cx + round(math.cos(math.radians(a)) * 15.2)
        by = cy + round(math.sin(math.radians(a)) * 15.2)
        cv.put(bx, by, NEGRE, 1.0, lit=0)
    for (px, py) in ((cx - 9, cy - 9), (cx - 8, cy - 10), (cx - 10, cy - 8), (cx - 7, cy - 11)):   # el reflex
        cv.flat(px, py, mix(cv.P[px, py][:3], (220, 255, 210), 0.35))
    if hover:
        cv.glow(cx, cy, 21, TARONJA[4], 0.3)


def gauge(cv):
    """El manòmetre del dipòsit d'aigua: esfera crema, la zona buida en taronja, l'agulla gairebé a zero i una
    gota blava petita a l'esfera."""
    cx, cy, r = GAUGE
    cv.disc(cx + 0.6, cy + 0.8, r + 1.5, r + 1.5, OLIVA, 0.6, lit=0)
    cv.disc(cx, cy, r + 1.0, r + 1.0, IRON, lambda nx, ny: 4.6 - nx - ny * 1.3, lit=0)   # l'anella d'acer
    cv.disc(cx, cy, r - 0.6, r - 0.6, CREMA, lambda nx, ny: 3.3 - ny * 0.4 - nx * 0.2, lit=0)
    for k in range(9):                                                   # escala: de -220° a +40°
        a = math.radians(140 + k * 32.5)
        for t in (r - 2.2, r - 3.2):
            cv.put(round(cx + math.cos(a) * t), round(cy + math.sin(a) * t), NEGRE, 2.0, lit=0)
    for k in range(10):                                                  # la zona buida, en taronja
        a = math.radians(140 + k * 5)
        cv.put(round(cx + math.cos(a) * (r - 2.0)), round(cy + math.sin(a) * (r - 2.0)), TARONJA, 3.4, lit=0)
    a = math.radians(150)                                                # l'agulla: gairebé a zero
    for i in range(0, r - 2):
        cv.put(round(cx + math.cos(a) * i), round(cy + math.sin(a) * i), TARONJA, 3.0 if i > 2 else 2.0, lit=0)
    cv.disc(cx, cy, 1.4, 1.4, NEGRE, 2.6, lit=0)
    for (dx, dy, v) in ((0, 3, 3.6), (0, 4, 3.0), (-1, 5, 3.2), (0, 5, 3.6), (1, 5, 2.6), (0, 6, 2.2)):   # la gota
        cv.put(cx + dx, cy + dy, BLAU, v, lit=0)
    cv.put(cx - 5, cy - 6, CREMA, 5.4, lit=0)                            # el reflex del vidre


def verne_label(cv, x0, y0, x1, y1):
    """L'adhesiu de Verne: blanc, amb la gota blava i dues ratlles de lletra, ratllat i amb un cantó arrencat."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            torn = (x - x0) + (y1 - y) < 4 + int(hr(x, y, 5) * 2)          # el cantó de baix, arrencat
            if torn:
                continue
            v = 3.5 - (y - y0) * 0.01 + (hr(x // 2, y // 3, 6) - 0.5) * 0.3
            cv.put(x, y, ETIQ, v, lit=0)
    cv.hline(x0, x1, y0, ETIQ, 4.0, lit=0)
    gx, gy = (x0 + x1) / 2, y0 + 8                                   # la gota
    for yy in range(y0 + 3, y0 + 13):
        for xx in range(x0 + 1, x1):
            t = (yy - (y0 + 3)) / 9
            half = 3.6 * math.sin(min(math.pi / 2, t * 2.2)) if t < 0.7 else 3.6 * math.sqrt(max(0, 1 - ((t - 0.7) / 0.32) ** 2))
            if abs(xx - gx) <= half:
                cv.put(xx, yy, BLAU, 3.4 - (xx - gx) * 0.25 - t * 0.6, lit=0)
    cv.put(gx - 1.5, gy - 1, BLAU, 5.2, lit=0)
    for yy in (y0 + 16, y0 + 19, y0 + 22):                          # «AIGUA VERNE», que ja no es llegeix
        for xx in range(x0 + 2, x1 - 1):
            if hr(xx, yy, 2) > 0.3:
                cv.put(xx, yy, BLAU, 2.0, lit=0)
    for k in range(9):                                               # dues ratllades de clau (el metall)
        cv.put(x0 + 2 + k * 0.6, y0 + 10 + k * 1.3, IRON, 5.0, lit=0)
        cv.put(x1 - 2 - k * 0.4, y0 + 22 + k * 1.1, IRON, 4.4, lit=0)
    for (xx, yy) in ((x0 + 3, y0 + 27), (x0 + 6, y0 + 31), (x0 + 2, y0 + 34)):   # brutícia i rovell
        cv.put(xx, yy, RUST, 3.0, lit=0)


FACE_R = 13                        # el radi del vidre on es veu la cara


def _face_source(who):
    """El fotograma IdleD del personatge de 640: placeholder-art/<id>/ o, si no, hd640/characters/<id>/."""
    for d in (ART / who, Path(__file__).resolve().parent / 'characters' / who):
        js, png = d / f'{who}.json', d / f'{who}.png'
        if js.exists() and png.exists():
            sheet = json.loads(js.read_text())
            tags = {t['name']: t['from'] for t in sheet['meta']['frameTags']}
            if 'IdleD' not in tags:
                continue
            fr = list(sheet['frames'].values())[tags['IdleD']]['frame']
            return Image.open(png).convert('RGBA').crop((fr['x'], fr['y'], fr['x'] + fr['w'], fr['y'] + fr['h']))
    return None


def _silhouette():
    """Si encara no hi ha personatge: una silueta de cap i espatlles en fòsfor (el radar no la reconeix)."""
    n = 2 * FACE_R + 1
    img = Image.new('RGBA', (n, n + 1), (0, 0, 0, 0))
    P = img.load()
    for y in range(n + 1):
        for x in range(n):
            dx, dy = x - FACE_R, y - FACE_R
            head = (dx / 5.5) ** 2 + ((dy + 3) / 6.5) ** 2 <= 1
            sh = dy > 4 and (dx / 11) ** 2 + ((dy - 14) / 9) ** 2 <= 1
            if (head or sh) and dx * dx + dy * dy <= FACE_R ** 2:
                P[x, y] = FOSFOR[4] + (255,) if (head and dx < -2) else FOSFOR[3] + (255,)
    return img


def face(who='vet'):
    """La cara de l'altra protagonista dins la pantalla rodona: el personatge de 640 de cara (IdleD), retallat
    en rodó al voltant del cap, una mica verdós, amb les línies d'escaneig i el reflex del vidre."""
    src = _face_source(who)
    if src is None:
        return _silhouette()
    A = src.load()
    rows = [y for y in range(src.height) if any(A[x, y][3] for x in range(src.width))]
    top = rows[0]
    width = {y: sum(1 for x in range(src.width) if A[x, y][3]) for y in range(top, min(src.height, top + 50))}
    # el coll: la fila més estreta entre el cap i les espatlles (on l'amplada torna a créixer de cop)
    shoulders = next((y for y in range(top + 12, top + 49) if width.get(y, 0) >= 24), top + 30)
    neck = min(range(top + 10, shoulders), key=lambda y: (width[y], -y)) if shoulders > top + 10 else top + 22
    xs = [x for y in range(neck - 14, neck - 4) for x in range(src.width) if A[x, y][3]]
    cxf = (min(xs) + max(xs)) / 2 if xs else src.width / 2
    cyf = neck - 8                            # la cara al mig del cercle, amb el coll i una mica d'espatlles
    n = 2 * FACE_R + 1
    out = Image.new('RGBA', (n, n + 1), (0, 0, 0, 0))
    P = out.load()
    x0, y0 = round(cxf - FACE_R), round(cyf - FACE_R)
    for y in range(n + 1):
        for x in range(n):
            if (x - FACE_R) ** 2 + (y - FACE_R) ** 2 <= FACE_R ** 2 and 0 <= y0 + y < src.height \
                    and 0 <= x0 + x < src.width:
                r, g, b, a = A[x0 + x, y0 + y]
                if a:
                    c = mix((r, g, b), FOSFOR[5], 0.18)
                    if y % 2:
                        c = tuple(int(v * 0.86) for v in c)
                    P[x, y] = c + (a,)
    for (x, y) in ((6, 9), (7, 8), (8, 7), (9, 6), (10, 5), (6, 11)):     # el reflex del vidre
        if P[x, y][3]:
            P[x, y] = mix(P[x, y], (220, 250, 220), 0.4) + (255,)
    return out


def inv_icons(ids):
    """Icones d'inventari de 640 (65×36, hd640/items.py)."""
    from hd640 import items
    return [items.render(i) for i in ids]


# ─── La barra ──────────────────────────────────────────────────────────────

def slot(cv, sx, sy):
    """Casella d'inventari: una pantalleta de fòsfor enfonsada al tauler, amb cantoneres de visor."""
    x1, y1 = sx + SLOT_W - 1, sy + SLOT_H - 1
    well(cv, sx, sy, x1, y1, face=1.2, brass=False)
    cv.rect(sx + 1, sy + 1, x1 - 1, sy + 1, NEGRE, 1.0, lit=0)
    cv.rect(sx + 1, sy + 1, sx + 1, y1 - 1, NEGRE, 1.0, lit=0)
    screen(cv, sx + 2, sy + 2, x1 - 2, y1 - 2)
    corners(cv, sx + 3, sy + 3, x1 - 3, y1 - 3, n=5, ramp=FOSFOR, lvl=3.6)


def background():
    cv = Canvas(W, BH, transparent=True)
    cv.rect(0, 0, W - 1, STRIP_H - 1, OLIVA, 0.5, lit=0)        # la franja fosca de la frase
    body(cv, ROPE_Y, BH - 1)
    rope(cv, ROPE_Y)
    for x in range(10, W, 53):                                   # reblons de la vora de baix
        big_rivet(cv, x, BH - 6, 4.6)
    for sx in SEAMS:
        seam(cv, sx, 20, BH - 4)
    # a la dreta: l'adhesiu de Verne, mig arrencat, entre dos reblons
    verne_label(cv, 620, 28, 632, 72)
    big_rivet(cv, 625, 80)
    big_rivet(cv, 625, 90)
    rust_streak(cv, 625, 83, 6, seed=3)
    # a baix a l'esquerra: el manòmetre del dipòsit
    gauge(cv)
    for row, vy in zip(VERB_IDS, VERB_ROWS):
        for (vx, vw), _vid in zip(VERB_COLS, row):
            verb_plate(cv, vx, vy, vx + vw - 1, vy + VERB_H - 1)
    for ax, ay in ARROWS.values():
        box(cv, ax, ay, ax + 12, ay + 35, OLIVA, 4.2)
        cv.hline(ax + 1, ax + 11, ay + 1, OLIVA, 5.2, lit=0)
    for sx, sy in slots():
        slot(cv, sx, sy)
    menu_button(cv)
    return cv


def verb_bar(state=None):
    """La barra completa (640×100). state: {'hover': id de verb o 'up'/'down'/'canvia', 'line': frase,
    'inv': [ids d'objecte], 'face': 'iri'|'vet'}."""
    st = {'hover': None, 'line': 'Mira la bomba de Verne', 'inv': ('comunicador', 'mosca', 'tornavis_flor'),
          'face': 'vet'}
    st.update(state or {})
    cv = background()
    for which, (ax, ay) in ARROWS.items():
        hot = st['hover'] == which
        if hot:
            box(cv, ax, ay, ax + 12, ay + 35, OLIVA, 5.0)
        arrow(cv, ax + 6, ay + 18, which == 'up', hot, length=15)
    porthole(cv, st['hover'] == 'canvia')
    img = cv.img
    f = face(st['face'])
    img.alpha_composite(f, (PORT[0] - f.width // 2, PORT[1] - f.height // 2 - 1))
    for ic, (sx, sy) in zip(inv_icons(st['inv']), slots()):
        if ic is not None:
            img.alpha_composite(ic, (sx, sy))
    bold, reg = font640(True), font640(False)
    for row, vy in zip(VERB_IDS, VERB_ROWS):
        for (vx, vw), vid in zip(VERB_COLS, row):
            s = VERB_TEXT[vid]
            tw = text_width(bold, s, 4)
            draw_text(img, bold, s, vx + (vw - tw) // 2, vy + 2, TEXT_HOVER if st['hover'] == vid else TEXT)
    tw = text_width(reg, st['line'], 4)
    draw_text(img, reg, st['line'], (W - tw) // 2, -2, VERB_LINE, outline=None)
    return img


# ─── La barra de 480 (només per a hd640/preview.py --res 480) ──────────────

def bar480(line='Mira la bomba de Verne', inv=(), hover=None):
    """La barra de 480 de hd/gui.py (la de Ni un ou), retallada a 480×75, amb els textos."""
    from hd import gui as g
    sys.path.insert(0, str(TOOLS.parents[2] / 'tools/font'))
    import aiguaverne_font as af
    img = Image.new('RGBA', (480, 270), (0, 0, 0, 0))
    for layer in (g.verbs_bg(), g.verbs_arrow('up', hover == 'up'), g.verbs_arrow('down', hover == 'down'),
                  g.menu_button(), g.canvia(False)):
        img.alpha_composite(layer)
    bold, reg = af.all_glyphs(True), af.all_glyphs(False)
    ids = ('give', 'pickUp', 'use', 'open', 'talkTo', 'push', 'close', 'look', 'pull')
    for (vx, vy, vw), vid in zip(g.VERBS, ids):
        s = VERB_TEXT[vid]
        tw = text_width(bold, s, af.SPACE_ADVANCE)
        draw_text(img, bold, s, vx + (vw - tw) // 2, vy + 2, TEXT_HOVER if hover == vid else TEXT, space=af.SPACE_ADVANCE)
    tw = text_width(reg, line, af.SPACE_ADVANCE)
    draw_text(img, reg, line, 240 - tw // 2, 192, VERB_LINE, outline=None, space=af.SPACE_ADVANCE)
    return img.crop((0, 195, 480, 270))


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('barra_640.png')
    out.parent.mkdir(parents=True, exist_ok=True)
    b = verb_bar({'hover': 'look'})
    b.save(out)
    b.resize((W * 3, BH * 3), Image.NEAREST).save(out.with_name(out.stem + '_x3.png'))
    print(f'✔ {out}')


if __name__ == '__main__':
    main()
