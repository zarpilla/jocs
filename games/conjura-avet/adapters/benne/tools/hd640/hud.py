#!/usr/bin/env python3
"""
La Conjura de l'Avet (com Aigua Verne i L'Última Arrel): la interfície sense barra de verbs (tàctil). Substitueix la
barra del joc original.

Escriu directament al projecte Benne (conjura-avet/src/game):

  guis/verbs/verbs.gui.json + assets/images/guis/verbs/   el HUD: es diu `verbs` perquè el pont compartit
                                                           (adapters/benne/runtime) la mostra i l'amaga, i hi
                                                           busca el botó «Canvia»
  guis/accions/accions.gui.json + assets/.../accions/     el menú d'accions (mantenir premut o clic dret)
  guis/controls/ + assets/.../controls/                   la targeta «Com es juga» (adapters/benne/tactil)

Els scripts (`verbs.gui.ts`, `accions.gui.ts`) són al projecte, escrits a mà. Les peces són les de la barra
(hd640/gui.py), però amb la paleta del monestir d'aquest joc: fusta fosca en lloc de la planxa oliva, una franja de
pedra amb l'escacat romànic (el de les impostes de Sant Pol) en lloc de la de seguretat, el **vermell de la cera dels
segells** com a color d'accent (cantoneres, fletxes i text sota el dit) en lloc del taronja, i la llum d'espelma en
lloc del fòsfor verd (aquí només, dins d'aquest procés: hd640/gui.py i gui_rest.py no canvien).

El botó «Canvia» (`CanviaBtn`): una placa de fusta amb una finestra rodona amb l'anella de llautó; a dins, la cara de
l'altra germana (`CaraIri`, `CaraVet`, als trams on es pot canviar) o la **lupa** de la pista (`caraPista`, als
seguits: `botoPista: 'mixt'` a joc.ts), de llautó amb el vidre clar. hud.ts decideix quina es veu.

Per provar-lo sense tocar el projecte: BENNE_GAME=<carpeta> python3 hd640/hud.py (i la làmina,
python3 ../../../guio/art/hud.py).

    python3 adapters/benne/tools/hd640/hud.py

Compte: `gui_rest.py` torna a fer la barra de verbs: no l'executis en aquest joc.
"""
import json
import math
import sys
from pathlib import Path

from PIL import Image

TOOLS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))

import hd640  # noqa: E402,F401
from hd.pix import Canvas, mix  # noqa: E402
import hd640.gui as vg  # noqa: E402
from hd640.gui import CREMA, TEXT, TEXT_OUTLINE, box, corners, well  # noqa: E402
import hd640.gui_rest as gr  # noqa: E402
from hd640.gui_rest import write_sheet, key_image, GAME  # noqa: E402

# ─── La paleta del monestir (La Conjura de l'Avet) ──────────────────────────
# Les peces de hd640/gui.py i hd640/gui_rest.py fan servir els noms de la seva paleta (OLIVA, TARONJA, FOSFOR...):
# aquí se'ls canvia el color, només en aquest procés.
FUSTA = [(9, 7, 6), (18, 13, 10), (29, 21, 16), (41, 30, 22), (55, 40, 29), (70, 52, 37), (88, 66, 47),
         (108, 82, 59), (130, 100, 73)]                     # fusta fosca (noguera vella)
CERA = [(36, 6, 8), (78, 10, 14), (128, 20, 22), (178, 34, 30), (214, 56, 42), (240, 100, 78),
        (255, 170, 148)]                                    # el vermell de la cera dels segells: l'accent
LLUM = [(10, 6, 3), (20, 12, 5), (34, 20, 8), (56, 32, 10), (92, 54, 14), (146, 92, 24), (212, 150, 52),
        (255, 214, 130)]                                    # la llum d'espelma (on la barra tenia fòsfor)
PEDRA = [(20, 18, 17), (36, 33, 30), (54, 50, 45), (74, 68, 61), (96, 89, 80), (120, 112, 100), (146, 137, 122),
         (174, 165, 148)]                                   # pedra grisa i daurada (Sant Pol)
LLAUTO = [(40, 24, 10), (84, 54, 20), (138, 96, 34), (190, 144, 54), (230, 192, 90), (252, 234, 160),
          (255, 252, 222)]
NEGRE_B = [(5, 4, 4), (12, 9, 8), (21, 16, 13), (32, 25, 20)]
GRIS_F = [(26, 22, 20), (44, 39, 35), (62, 56, 50), (82, 75, 67), (104, 96, 86)]   # desactivat: fusta apagada
for _m in (vg, gr):
    _m.OLIVA, _m.TARONJA, _m.FOSFOR, _m.NEGRE = FUSTA, CERA, LLUM, NEGRE_B
vg.VIDRE, vg.LINIA = (10, 7, 5), (16, 11, 8)
gr.GREY = GRIS_F
OLIVA, TARONJA, FOSFOR, NEGRE = FUSTA, CERA, LLUM, NEGRE_B
VERB_LINE = '#e6d8b2'                   # la frase: pergamí (en lloc del crema verdós de pantalla)
TEXT_HOVER = '#f2805f'                  # el text sota el dit: el vermell de la cera, clar (es llegeix sobre fosc)
TITLE = '#e8b45c'                       # els títols: llautó

W, H = 640, 288                         # l'alçada mínima (20:9); la pantalla pot ser més alta (pantalla.py)
FRANJA = 260                            # a sota, la franja: la frase
FONT, BOLD = 'conjuraavet-regular', 'conjuraavet-negreta'
# el verb de la frase: el color de la frase, més apagat (el nom és el que compta)
VERB_DIM = '#' + ''.join(f'{round(int(VERB_LINE[i:i + 2], 16) * 0.6):02x}' for i in (1, 3, 5))

# ─── Disposició (ha de coincidir amb verbs.gui.ts i accions.gui.ts) ─────────

M = 4                                   # marge de la pantalla
CANVIA = (M, M)                         # 57×52: la pantalla rodona de la barra, en una placa més alta
CANVIA_H = 52                           # (tan alta com el menú i els punts petits l'un sobre l'altre: hud.ts)
MENU_BTN = (W - M - 25, M)              # 25×25
BOTO = 32                               # els botons de baix (bossa, punts), a les cantonades
PUNTS = (M, H - M - BOTO)
BOSSA = (W - M - BOTO, H - M - BOTO)
SLOT_W, SLOT_H, GAP, COLS = 65, 36, 4, 7
SAFATA = (52, FRANJA - 46, 532, 44)     # x, y, amplada, alçada: just a sobre de la franja
FLETXA_W = 13
# Pantalla alta (un monitor, fins a 360): la franja de sota l'escena (de 260 avall) és el tauler de comandaments, amb
# tot el HUD i l'inventari sempre a la vista. Coordenades a 360 d'alt; verbs.gui.ts les fa servir a partir de
# MODE_TAULER (si la pantalla és més baixa, es queda el HUD de mòbil, sobre l'escena).
H_MAX = 360
TAULER = (0, FRANJA, W, H_MAX - FRANJA)          # 640×100
COLS2, ROWS2 = 7, 2                     # 7 per fila: el tauler té a l'esquerra «Canvia», el menú i els punts
SAFATA2_W, SAFATA2_H = 520, 82
SAFATA2 = (94, H_MAX - 4 - SAFATA2_H)           # de la columna de l'esquerra (fins a x = 67) a la dreta
# Tauler baix (una finestra de navegador, d'uns 320–350 d'alt): una sola fila de 6, amb les fletxes als costats.
SAFATA3_W, SAFATA3_H = 529, 44
SAFATA3_X = 100                         # de la columna de l'esquerra (fins a x = 90) a la dreta
PETIT = 25                              # els punts petits del tauler baix (al costat de «Canvia», sota el menú)
KEY_W, KEY_H = 104, 22                  # botons del menú d'accions
ACCIONS_MAX = 6


def crop_bar(draw, x, y, w, h):
    """Un tros de la barra original (coordenades de la barra): la pantalla rodona, el botó del menú."""
    cv = Canvas(W, vg.BH, transparent=True)
    draw(cv)
    return cv.img.crop((x, y, x + w, y + h))


def escacat(cv, x0, x1, y0, h):
    """La franja de pedra amb l'escacat romànic (dues fileres de daus alterns, com les impostes de Sant Pol), amb el
    cantell clar a dalt i l'ombra que fa a sota. Amb h < 4, una sola filera."""
    from hd.pix import hr
    rows = 2 if h >= 4 else 1
    for x in range(x0, x1 + 1):
        for y in range(y0, y0 + h):
            row = (y - y0) * rows // h
            dau = ((x - x0) // 3 + row) % 2
            v = (4.8 if dau else 2.2) - (y - y0) * 0.25 + (hr(x, y, 5) - 0.5) * 0.7
            if y == y0 and dau:
                v += 0.8
            cv.put(x, y, PEDRA, v, lit=0)
        if hr(x // 5, 31) > 0.9:                                           # la pedra rosegada, a trossos
            cv.put(x, y0, PEDRA, 1.6, lit=0)
    for x in range(x0, x1 + 1):
        vg.dark(cv, x, y0 + h, 0.5)


def lupa_icon(cv, cx, cy, hover=False, pressed=False, r=12.5):
    """La lupa de la pista: l'anella de llautó, el vidre clar (es veu la fusta de darrere, aclarida) amb el reflex i
    el mànec de fusta (cap avall a la dreta). Amb hover, el vidre s'encén i fa un halo d'espelma."""
    lift = 1.0 if hover else (-0.4 if pressed else 0.0)
    k_r = r / 12.5
    ang = math.radians(45)
    hx0, hy0 = cx + math.cos(ang) * (r + 1), cy + math.sin(ang) * (r + 1)
    for i in range(12):                                                   # el mànec
        t = i / 11
        x, y = hx0 + t * 9 * k_r, hy0 + t * 9 * k_r
        for k in range(-3, 4):
            cv.put(round(x - k * 0.6), round(y + k * 0.6), FUSTA, 8.0 - abs(k) * 1.0 - t * 1.0 + (0.8 if k < 0 else 0),
                   lit=0)
    cv.put(round(hx0 + 1), round(hy0 + 1), LLAUTO, 4.0, lit=0)             # la virolla
    cv.put(round(hx0 + 2), round(hy0 + 2), LLAUTO, 3.2, lit=0)
    cv.disc(cx + 0.6, cy + 1.0, r + 1.6, r + 1.6, NEGRE, 1.2, lit=0)        # l'ombra
    cv.disc(cx, cy, r + 1.2, r + 1.2, LLAUTO, lambda nx, ny: 3.6 + lift * 0.5 - nx * 1.0 - ny * 1.2, lit=0)
    cv.disc(cx, cy, r - 1.4, r - 1.4, LLAUTO, lambda nx, ny: 1.6 + nx * 0.8 + ny * 0.8, lit=0)   # el bisell
    rr = r - 2.4
    fosc, clar = (118, 128, 124), (196, 206, 198)                         # el vidre: gris clar, una mica verdós
    for yy in range(int(cy - rr) - 1, int(cy + rr) + 2):                  # el vidre
        for xx in range(int(cx - rr) - 1, int(cx + rr) + 2):
            d = math.hypot(xx - cx, yy - cy)
            if d <= rr:
                k = max(0.0, 1 - d / rr)
                c = mix(fosc, clar, k * 0.7 + ((cx - xx) + (cy - yy)) / rr * 0.15 + (0.2 if hover else 0))
                if hover:
                    c = mix(c, LLUM[7], 0.18)
                cv.flat(xx, yy, c)
    for i in range(int(rr * 1.2)):                                        # l'ombra de l'anella, dins el vidre
        a = math.radians(10 + i * 80 / (rr * 1.2))
        px, py = round(cx + math.cos(a) * (rr - 0.6)), round(cy + math.sin(a) * (rr - 0.6))
        cv.flat(px, py, mix(cv.P[px, py][:3], (40, 44, 42), 0.35))
    for (px, py, k) in ((cx - 6, cy - 7, 0.75), (cx - 5, cy - 8, 0.7), (cx - 7, cy - 6, 0.65), (cx - 4, cy - 8, 0.5),
                        (cx - 7, cy - 5, 0.5), (cx - 3, cy - 8, 0.3), (cx - 8, cy - 4, 0.3)):   # el reflex
        px, py = round(cx + (px - cx) * k_r), round(cy + (py - cy) * k_r)
        cv.flat(px, py, mix(cv.P[px, py][:3], (255, 255, 250), k))
    if hover:
        cv.glow(cx, cy, r + 8, LLUM[6], 0.3)


def lupa_sola():
    """La lupa sola, sense la placa (32×32): la icona de la pista a la targeta «Com es juga»."""
    cv = Canvas(32, 32, transparent=True)
    lupa_icon(cv, 13, 13)
    return cv.img


def lupa_boto(w, h, hover=False, pressed=False):
    """El botó de la pista sol (la làmina): una placa de fusta amb quatre clavilles i la lupa al mig."""
    cv = Canvas(w, h, transparent=True)
    face = 4.6 if hover else (3.4 if pressed else 4.0)
    box(cv, 0, 0, w - 1, h - 1, FUSTA, face)
    for y in range(2, h - 2, 3):                                          # la veta de la fusta
        for x in range(2, w - 2):
            if (x * 3 + y * 7 + int(math.sin(x * 0.3 + y) * 3)) % 11 == 0:
                cv.put(x, y, FUSTA, face - 0.8, lit=0)
    cv.hline(1, w - 2, 1, FUSTA, face + 1.2, lit=0)
    for bx, by in ((3, 3), (w - 5, 3), (3, h - 5), (w - 5, h - 5)):         # les clavilles
        cv.put(bx, by, FUSTA, 7.4, lit=0)
        cv.put(bx + 1, by, FUSTA, 6.6, lit=0)
        cv.put(bx, by + 1, FUSTA, 6.0, lit=0)
        cv.put(bx + 1, by + 1, FUSTA, 1.6, lit=0)
    if hover or pressed:
        corners(cv, 1, 1, w - 2, h - 2, n=5, ramp=CERA, lvl=4.2 if hover else 3.0)
    dy = 1 if pressed else 0
    lupa_icon(cv, w // 2 - 4, h // 2 - 4 + dy, hover, pressed)
    for (cx, cy) in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
        cv.P[cx, cy] = (0, 0, 0, 0)
    return cv.img


def lupa_mini():
    """La lupa dins la finestra rodona del botó (la mida de les cares): quan el botó fa de pista."""
    n = 2 * vg.FACE_R + 1
    cv = Canvas(n, n + 1, transparent=True)
    lupa_icon(cv, n // 2 - 3, n // 2 - 3, r=8.0)
    return cv.img


def retrat(who):
    """La cara de l'altra germana dins la finestra rodona: la de hd640/gui.py (face), però com un retrat a la llum
    d'espelma: el to, càlid i suau (face hi barreja FOSFOR[5]), i sense les línies d'escaneig de la pantalla."""
    llum = vg.FOSFOR
    try:
        vg.FOSFOR = llum[:5] + [(236, 204, 160)] + llum[6:]
        img = vg.face(who)
    finally:
        vg.FOSFOR = llum
    if vg._face_source(who) is None:
        return img
    P = img.load()
    for y in range(1, img.height, 2):       # face enfosqueix les files senars (×0,86): es desfà
        for x in range(img.width):
            r, g, b, a = P[x, y]
            if a:
                P[x, y] = tuple(min(255, round(v / 0.86)) for v in (r, g, b)) + (a,)
    return img


def placa_boto(w, h, hover=False, pressed=False):
    """El botó «Canvia»: la placa de fusta de la lupa, amb una finestra rodona fosca on surt la cara o la lupa."""
    cv = Canvas(w, h, transparent=True)
    face = 4.6 if hover else (3.4 if pressed else 4.0)
    box(cv, 0, 0, w - 1, h - 1, FUSTA, face)
    cv.hline(1, w - 2, 1, FUSTA, face + 1.2, lit=0)
    for bx, by in ((3, 3), (w - 5, 3), (3, h - 5), (w - 5, h - 5)):
        cv.put(bx, by, FUSTA, 7.4, lit=0)
        cv.put(bx + 1, by + 1, FUSTA, 1.6, lit=0)
    pcx, pcy = vg.PORT[0] - vg.CANVIA[0], (h - 1) // 2
    cv.disc(pcx, pcy, vg.FACE_R + 2.5, vg.FACE_R + 2.5, LLAUTO, lambda nx, ny: 3.4 - nx * 0.8 - ny * 1.0, lit=0)
    cv.disc(pcx, pcy, vg.FACE_R + 0.6, vg.FACE_R + 0.6, NEGRE_B, 1.4, lit=0)
    if hover or pressed:
        corners(cv, 1, 1, w - 2, h - 2, n=5, ramp=CERA, lvl=4.2 if hover else 3.0)
    for (cx, cy) in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
        cv.P[cx, cy] = (0, 0, 0, 0)
    return cv.img


def plate(w, h, hover=False, on=False):
    """Un botó quadrat de fusta fosca amb clavilles; amb hover o encès, cantoneres vermelles (de cera)."""
    cv = Canvas(w, h, transparent=True)
    face = 5.0 if hover else 4.2
    box(cv, 0, 0, w - 1, h - 1, OLIVA, face)
    cv.hline(1, w - 2, 1, OLIVA, face + 1.0, lit=0)
    for bx, by in ((3, 3), (w - 5, 3), (3, h - 5), (w - 5, h - 5)):
        cv.put(bx, by, OLIVA, face + 2.4, lit=0)
        cv.put(bx + 1, by + 1, OLIVA, face - 1.6, lit=0)
    if hover or on:
        corners(cv, 1, 1, w - 2, h - 2, n=6 if on else 4)
    for (cx, cy) in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
        cv.P[cx, cy] = (0, 0, 0, 0)
    return cv


def bossa_icon(cv, hover):
    """Una bossa de lli (l'inventari): cos crema, solapa, corretja i sivella de llautó."""
    lift = 0.6 if hover else 0.0
    cx, k = cv.w // 2, cv.w / 40
    q = lambda v: round(v * k)                                          # noqa: E731  (dibuixat a 40 px)
    for y in range(q(7), q(14)):                                        # la nansa
        for x in range(cx - q(9), cx + q(9) + 1):
            if abs(math.hypot(x - cx, y - q(14)) - q(7)) < 0.9:
                cv.put(x, y, CREMA, 2.0 + lift, lit=0)
    cv.rect(cx - q(12), q(13), cx + q(12), q(31), CREMA, 3.0 + lift, lit=0)    # el cos
    cv.hline(cx - q(12), cx + q(12), q(31), CREMA, 1.6, lit=0)
    cv.vline(cx + q(12), q(13), q(31), CREMA, 2.0, lit=0)
    cv.rect(cx - q(12), q(13), cx + q(12), q(19), CREMA, 4.0 + lift, lit=0)    # la solapa
    cv.hline(cx - q(12), cx + q(12), q(20), CREMA, 1.4, lit=0)
    cv.rect(cx - 2, q(17), cx + 2, q(23), LLAUTO, 3.4 + lift, lit=0)           # la sivella
    cv.put(cx, q(20), NEGRE, 1.0, lit=0)


def punts_icon(cv, hover):
    """«Què es pot tocar aquí?»: un forat fosc amb tres punts de llum d'espelma (sense línies de pantalla)."""
    cx = cy = cv.w // 2
    r = cv.w * 0.29
    cv.disc(cx, cy, r + 2, r + 2, NEGRE, 2.2, lit=0)
    for yy in range(cy - int(r) - 1, cy + int(r) + 2):
        for xx in range(cx - int(r) - 1, cx + int(r) + 2):
            d = math.hypot(xx - cx, yy - cy)
            if d <= r:
                cv.flat(xx, yy, mix(FOSFOR[1], FOSFOR[3], max(0, 1 - d / r) * 0.8 + (0.35 if hover else 0)))
    cv.ring(cx, cy, r + 1, LLAUTO, 2.6, lit=0, step=3)
    for (px, py) in ((cx - 4, cy - 3), (cx + 3, cy - 1), (cx - 1, cy + 5)):
        cv.disc(px, py, 1.6, 1.6, FOSFOR, 6.0, lit=0)
        cv.put(px, py, FOSFOR, 7.4, lit=0)
    if hover:
        cv.glow(cx, cy, r + 3, FOSFOR[6], 0.25)


def boto(icon, hover=False, on=False, mida=BOTO):
    cv = plate(mida, mida, hover, on)
    icon(cv, hover or on)
    return cv.img


def fletxa(up, hover):
    cv = Canvas(FLETXA_W, SLOT_H, transparent=True)
    if hover:
        box(cv, 0, 0, FLETXA_W - 1, SLOT_H - 1, OLIVA, 4.8)
    vg.arrow(cv, FLETXA_W // 2, SLOT_H // 2, up, hover, length=15)
    return cv.img


def safata_xy():
    sx, sy, sw, sh = SAFATA
    inner = COLS * SLOT_W + (COLS - 1) * GAP
    fx0 = sx + (sw - inner - 2 * FLETXA_W - 2 * 6) // 2       # fletxa d'amunt
    slots_x = fx0 + FLETXA_W + 6
    fx1 = slots_x + inner + 6                                  # fletxa d'avall
    return fx0, slots_x, fx1, sy + (sh - SLOT_H) // 2


def safata():
    """La safata de l'inventari: una planxa amb els forats de les caselles i, als costats, les fletxes."""
    sx, sy, sw, sh = SAFATA
    cv = Canvas(sw, sh, transparent=True)
    box(cv, 0, 0, sw - 1, sh - 1, OLIVA, 3.8)
    cv.hline(1, sw - 2, 1, OLIVA, 4.8, lit=0)
    escacat(cv, 0, sw - 1, 2, 2)                               # la vora de pedra escacada, a dalt
    fx0, slots_x, fx1, top = safata_xy()
    for i in range(COLS):
        x0 = slots_x - sx + i * (SLOT_W + GAP)
        well(cv, x0, top - sy, x0 + SLOT_W - 1, top - sy + SLOT_H - 1, brass=False)
    for x in (fx0 - sx, fx1 - sx):
        well(cv, x, top - sy, x + FLETXA_W - 1, top - sy + SLOT_H - 1, face=2.2, brass=False)
    for (cx, cy) in ((0, 0), (sw - 1, 0), (0, sh - 1), (sw - 1, sh - 1)):
        cv.P[cx, cy] = (0, 0, 0, 0)
    return cv.img


def safata2_xy():
    """La safata gran (2 files de 6): x de les caselles, y de dalt, x de les fletxes (una sobre l'altra, a la dreta)."""
    sx, sy = SAFATA2
    inner_w = COLS2 * SLOT_W + (COLS2 - 1) * GAP
    inner_h = ROWS2 * SLOT_H + (ROWS2 - 1) * GAP
    slots_x = sx + (SAFATA2_W - inner_w - FLETXA_W - 6) // 2
    top = sy + (SAFATA2_H - inner_h) // 2
    return slots_x, top, slots_x + inner_w + 6


def safata2():
    """La safata gran del tauler: els forats de 2×6 caselles i, a la dreta, les dues fletxes."""
    sx, sy = SAFATA2
    cv = Canvas(SAFATA2_W, SAFATA2_H, transparent=True)
    box(cv, 0, 0, SAFATA2_W - 1, SAFATA2_H - 1, OLIVA, 2.8)
    slots_x, top, fx = safata2_xy()
    for r in range(ROWS2):
        for i in range(COLS2):
            x0 = slots_x - sx + i * (SLOT_W + GAP)
            y0 = top - sy + r * (SLOT_H + GAP)
            well(cv, x0, y0, x0 + SLOT_W - 1, y0 + SLOT_H - 1, brass=False)
        y0 = top - sy + r * (SLOT_H + GAP)
        well(cv, fx - sx, y0, fx - sx + FLETXA_W - 1, y0 + SLOT_H - 1, face=2.2, brass=False)
    return cv.img


def safata3_xy():
    """La safata d'una fila del tauler baix: x de la fletxa d'amunt, de les caselles i de la d'avall."""
    inner = COLS2 * SLOT_W + (COLS2 - 1) * GAP
    fx0 = SAFATA3_X + (SAFATA3_W - inner - 2 * FLETXA_W - 12) // 2
    slots_x = fx0 + FLETXA_W + 6
    return fx0, slots_x, slots_x + inner + 6


def safata3():
    """La safata d'una fila (6 caselles) del tauler baix, amb les fletxes als costats."""
    cv = Canvas(SAFATA3_W, SAFATA3_H, transparent=True)
    box(cv, 0, 0, SAFATA3_W - 1, SAFATA3_H - 1, OLIVA, 2.8)
    fx0, slots_x, fx1 = safata3_xy()
    top = (SAFATA3_H - SLOT_H) // 2
    for i in range(COLS2):
        x0 = slots_x - SAFATA3_X + i * (SLOT_W + GAP)
        well(cv, x0, top, x0 + SLOT_W - 1, top + SLOT_H - 1, brass=False)
    for x in (fx0 - SAFATA3_X, fx1 - SAFATA3_X):
        well(cv, x, top, x + FLETXA_W - 1, top + SLOT_H - 1, face=2.2, brass=False)
    return cv.img


def tauler():
    """El tauler de la franja de sota l'escena: fusta fosca, la franja de pedra escacada a dalt i clavilles."""
    _, _, tw, th = TAULER
    cv = Canvas(tw, th, transparent=True)
    box(cv, 0, 0, tw - 1, th - 1, OLIVA, 3.4)
    escacat(cv, 0, tw - 1, 0, 4)                               # la franja de pedra escacada, a dalt
    cv.hline(0, tw - 1, 4, OLIVA, 1.2, lit=0)
    cv.hline(0, tw - 1, 5, OLIVA, 4.6, lit=0)
    for x in (6, tw - 8):
        for y in (10, th - 8):
            vg.rivet(cv, x, y)
    return cv.img


def text_outline():
    return {'enabled': True, 'color': TEXT_OUTLINE, 'sides': 'allSides'}


# ─── El HUD (`verbs`) ──────────────────────────────────────────────────────

def build_hud():
    cx, cy, cw, _ = vg.CANVIA
    ch = CANVIA_H
    port = (vg.PORT[0] - cx, (ch - 1) // 2)                    # la pantalla rodona, al mig de la placa

    # el botó «Canvia»: una placa amb una finestra rodona; a dins, la cara de l'altra germana (als trams oberts) o la
    # lupa de la pista (als seguits: `botoPista: 'mixt'`, el control `CaraPista`)
    canvia, canvia_h, canvia_p = placa_boto(cw, ch), placa_boto(cw, ch, hover=True), placa_boto(cw, ch, pressed=True)
    mx, my, ms = vg.MENU
    menu = crop_bar(vg.menu_button, mx, my, ms, ms)
    cara = {who: retrat(who) for who in ('iri', 'vet')}
    cara['pista'] = lupa_mini()
    frames = [
        (canvia, 'CanviaBtn'), (canvia_h, 'CanviaBtn-hover'), (canvia_p, 'CanviaBtn-pressed'), (menu, 'MenuBtn'),
        (boto(bossa_icon), 'BossaBtn'), (boto(bossa_icon, hover=True), 'BossaBtn-hover'),
        (boto(bossa_icon, on=True), 'BossaBtn-on'),
        (boto(punts_icon), 'PuntsBtn'), (boto(punts_icon, hover=True), 'PuntsBtn-hover'),
        (boto(punts_icon, mida=PETIT), 'PuntsPetitBtn'), (boto(punts_icon, hover=True, mida=PETIT), 'PuntsPetitBtn-hover'),
        (safata(), 'Safata'),
        (fletxa(True, False), 'UpBtn'), (fletxa(True, True), 'UpBtn-hover'),
        (fletxa(False, False), 'DownBtn'), (fletxa(False, True), 'DownBtn-hover'),
        (cara['iri'], 'CaraIri'), (cara['vet'], 'CaraVet'), (cara['pista'], 'CaraPista'),
        (tauler(), 'Tauler'), (safata2(), 'Safata2'), (safata3(), 'Safata3'),
    ]
    sheet_dir = GAME / 'assets/images/guis/verbs'
    write_sheet(sheet_dir, 'verbs', [(im, tag, (0, 0), im.size) for im, tag in frames])

    # la cara, al mig de la pantalla rodona (com a la barra: hd640/gui_rest.py, build_verbs)
    fx = CANVIA[0] + port[0] - cara['iri'].width // 2
    fy = CANVIA[1] + port[1] - cara['iri'].height // 2 - 1
    fx0, slots_x, fx1, top = safata_xy()

    def button(cid, xy, w, h, tag, states=None, visible=True):
        c = {'type': 'button', 'id': cid, 'x': xy[0], 'y': xy[1], 'width': w, 'height': h, 'backgroundAnchor': 'top-left',
             'text': '', 'font': BOLD, 'fontSize': 8, 'textColor': TEXT, 'textAlign': 'center', 'textOffsetX': 0,
             'textOffsetY': 0, 'backgroundTag': tag}
        if states:
            c['states'] = states
        if not visible:
            c['visible'] = False
        return c

    slots2_x, top2, fx2 = safata2_xy()
    s3_fx0, s3_slots, s3_fx1 = safata3_xy()
    s3_top = H - 4 - SAFATA3_H + (SAFATA3_H - SLOT_H) // 2
    d = H_MAX - H                                              # el tauler, dissenyat a 360 i enganxat a baix
    controls = [
        # el tauler de la franja (pantalla alta): a sota de tot
        # (sempre a y = 260, sota l'escena: si la franja és més baixa, el que sobra queda fora de la pantalla)
        {'type': 'image', 'id': 'Tauler', 'x': TAULER[0], 'y': TAULER[1], 'tag': 'Tauler', 'backgroundAnchor': 'top-left',
         'visible': False, 'clickable': False},
        # la frase: el nom del que hi ha sota el dit o el ratolí, o «Usa X amb...»
        {'type': 'text', 'id': 'verbLineText', 'x': W // 2, 'y': FRANJA + 9, 'text': '', 'font': FONT, 'fontSize': 8,
         'color': VERB_LINE, 'align': 'center', 'textOutline': text_outline(), 'zIndex': 5},
        # el verb del clic («Obre»), més apagat que el nom: hud.ts el posa a l'esquerra del nom i centra la frase
        {'type': 'text', 'id': 'verbLineVerb', 'x': W // 2, 'y': FRANJA + 9, 'text': '', 'font': FONT, 'fontSize': 8,
         'color': VERB_DIM, 'align': 'left', 'textOutline': text_outline(), 'zIndex': 5},
        button('CanviaBtn', CANVIA, cw, ch, 'CanviaBtn', {'hover': 'CanviaBtn-hover', 'pressed': 'CanviaBtn-pressed'}),
        {'type': 'image', 'id': 'CaraIri', 'x': fx, 'y': fy, 'tag': 'CaraIri', 'backgroundAnchor': 'top-left',
         'visible': False, 'clickable': False},
        {'type': 'image', 'id': 'CaraVet', 'x': fx, 'y': fy, 'tag': 'CaraVet', 'backgroundAnchor': 'top-left',
         'visible': False, 'clickable': False},
        {'type': 'image', 'id': 'caraPista', 'x': fx, 'y': fy, 'tag': 'CaraPista', 'backgroundAnchor': 'top-left',
         'visible': False, 'clickable': False},
        button('MenuBtn', MENU_BTN, ms, ms, 'MenuBtn'),
        button('PuntsBtn', PUNTS, BOTO, BOTO, 'PuntsBtn', {'hover': 'PuntsBtn-hover'}),
        # els punts petits del tauler baix (hud.ts els posa i els mostra)
        button('PuntsPetitBtn', PUNTS, PETIT, PETIT, 'PuntsPetitBtn', {'hover': 'PuntsPetitBtn-hover'}, visible=False),
        button('BossaBtn', BOSSA, BOTO, BOTO, 'BossaBtn', {'hover': 'BossaBtn-hover'}),
        # la safata, plegada: verbs.gui.ts la desplega amb la bossa
        {'type': 'image', 'id': 'Safata', 'x': SAFATA[0], 'y': SAFATA[1], 'tag': 'Safata', 'backgroundAnchor': 'top-left',
         'visible': False},
        {'type': 'inventoryPanel', 'id': 'inventoryPanel', 'x': slots_x, 'y': top, 'rows': 1, 'cols': COLS,
         'slotWidth': SLOT_W, 'slotHeight': SLOT_H, 'showEmptySlots': True, 'spacingX': GAP, 'spacingY': GAP,
         'scrollDirection': 'vertical', 'backButton': 'upBtn', 'forwardButton': 'downBtn', 'visible': False},
        button('upBtn', (fx0, top), FLETXA_W, SLOT_H, 'UpBtn', {'hover': 'UpBtn-hover'}, visible=False),
        button('downBtn', (fx1, top), FLETXA_W, SLOT_H, 'DownBtn', {'hover': 'DownBtn-hover'}, visible=False),
        # la safata gran del tauler (pantalla alta), sempre oberta
        {'type': 'image', 'id': 'Safata2', 'x': SAFATA2[0], 'y': SAFATA2[1] - d, 'tag': 'Safata2',
         'backgroundAnchor': 'top-left', 'visible': False, 'anchorY': 'bottom'},
        {'type': 'inventoryPanel', 'id': 'inventoryPanel2', 'x': slots2_x, 'y': top2 - d, 'rows': ROWS2, 'cols': COLS2,
         'slotWidth': SLOT_W, 'slotHeight': SLOT_H, 'showEmptySlots': True, 'spacingX': GAP, 'spacingY': GAP,
         'scrollDirection': 'vertical', 'backButton': 'upBtn2', 'forwardButton': 'downBtn2', 'visible': False,
         'anchorY': 'bottom'},
        {**button('upBtn2', (fx2, top2 - d), FLETXA_W, SLOT_H, 'UpBtn', {'hover': 'UpBtn-hover'}, visible=False),
         'anchorY': 'bottom'},
        {**button('downBtn2', (fx2, top2 - d + SLOT_H + GAP), FLETXA_W, SLOT_H, 'DownBtn', {'hover': 'DownBtn-hover'},
                  visible=False), 'anchorY': 'bottom'},
        # la safata d'una fila del tauler baix (a 4 px de baix de tot)
        {'type': 'image', 'id': 'Safata3', 'x': SAFATA3_X, 'y': H - 4 - SAFATA3_H, 'tag': 'Safata3',
         'backgroundAnchor': 'top-left', 'visible': False, 'anchorY': 'bottom'},
        {'type': 'inventoryPanel', 'id': 'inventoryPanel3', 'x': s3_slots, 'y': s3_top, 'rows': 1, 'cols': COLS2,
         'slotWidth': SLOT_W, 'slotHeight': SLOT_H, 'showEmptySlots': True, 'spacingX': GAP, 'spacingY': GAP,
         'scrollDirection': 'vertical', 'backButton': 'upBtn3', 'forwardButton': 'downBtn3', 'visible': False,
         'anchorY': 'bottom'},
        {**button('upBtn3', (s3_fx0, s3_top), FLETXA_W, SLOT_H, 'UpBtn', {'hover': 'UpBtn-hover'}, visible=False),
         'anchorY': 'bottom'},
        {**button('downBtn3', (s3_fx1, s3_top), FLETXA_W, SLOT_H, 'DownBtn', {'hover': 'DownBtn-hover'}, visible=False),
         'anchorY': 'bottom'},
    ]
    # Pantalla adaptable (dissenyada a 288 d'alt): el que és a baix va enganxat a baix. En un monitor (360) la safata,
    # la frase i els botons queden a la franja de sota l'escena.
    for c in controls:
        if c['id'] in ('verbLineText', 'verbLineVerb', 'PuntsBtn', 'BossaBtn', 'Safata', 'inventoryPanel', 'upBtn', 'downBtn'):
            c['anchorY'] = 'bottom'
    gui = {'id': 'verbs', 'name': 'HUD', 'description': "La Conjura de l'Avet: sense barra de verbs [hd640/hud.py]",
           'visible': True, 'display': {'aseprite': True}, 'controls': controls}
    out = GAME / 'guis/verbs/verbs.gui.json'
    out.write_text(json.dumps(gui, indent=2, ensure_ascii=False) + '\n')


# ─── El menú d'accions (`accions`) ─────────────────────────────────────────

def build_accions():
    items = []
    for st in ('', '-hover', '-pressed'):
        im = key_image(KEY_W, KEY_H, st)
        items.append((im, f'Accio{st}', (0, 0), im.size))
    write_sheet(GAME / 'assets/images/guis/accions', 'accions', items)
    controls = [
        # tot el fons: tocar fora del menú el tanca (accions.gui.ts el fa mig transparent)
        {'type': 'button', 'id': 'fons', 'x': 0, 'y': 0, 'width': W, 'height': H, 'backgroundAnchor': 'top-left',
         'text': '', 'font': FONT, 'fontSize': 8, 'textColor': '#ffffff', 'backgroundTag': '',
         'backgroundColor': '#000000', 'backgroundColorStates': {'hover': '#000000', 'pressed': '#000000'}, 'zIndex': 1,
         'anchorY': 'stretch'},
        {'type': 'text', 'id': 'titol', 'x': W // 2, 'y': 100, 'text': '', 'font': BOLD, 'fontSize': 8,
         'color': TEXT_HOVER, 'align': 'center', 'textOutline': text_outline(), 'zIndex': 3},
    ]
    for i in range(ACCIONS_MAX):
        controls.append({
            'type': 'button', 'id': f'accio{i}', 'x': 0, 'y': 0, 'width': KEY_W, 'height': KEY_H,
            'backgroundAnchor': 'top-left', 'text': '', 'font': BOLD, 'fontSize': 8, 'textColor': TEXT,
            'textAlign': 'center', 'textOffsetX': 0, 'textOffsetY': 0, 'backgroundTag': 'Accio',
            'states': {'hover': 'Accio-hover', 'pressed': 'Accio-pressed'}, 'textColorStates': {'hover': TEXT_HOVER},
            'textOutline': {'enabled': True, 'color': TEXT_OUTLINE, 'sides': 'bottomRight'}, 'zIndex': 2,
            'visible': False,
        })
    for i in range(ACCIONS_MAX):                 # el text de cada botó (el d'un botó no es pot canviar des de l'script)
        controls.append({'type': 'text', 'id': f'text{i}', 'x': 0, 'y': 0, 'text': '', 'font': BOLD, 'fontSize': 8,
                         'color': TEXT, 'align': 'center', 'zIndex': 3, 'visible': False,
                         'textOutline': {'enabled': True, 'color': TEXT_OUTLINE, 'sides': 'bottomRight'}})
    gui = {'id': 'accions', 'name': 'Accions', 'description': "La Conjura de l'Avet: el menú d'accions [hd640/hud.py]",
           'visible': False, 'display': {'aseprite': True}, 'modal': True, 'zIndex': 90, 'controls': controls}
    d = GAME / 'guis/accions'
    d.mkdir(parents=True, exist_ok=True)
    (d / 'accions.gui.json').write_text(json.dumps(gui, indent=2, ensure_ascii=False) + '\n')


def build_targeta():
    """La targeta «Com es juga» (GUI `controls`): compartida (adapters/benne/tactil/controls.py), amb les peces i els
    colors d'aquest joc."""
    sys.path.insert(0, str(TOOLS.parents[4] / 'adapters/benne/tactil'))
    from controls import build_controls

    def llauto(fn):
        """El marc de la targeta, de llautó (el vermell de la cera queda per al que s'assenyala)."""
        def f(*a, **k):
            gr.TARONJA = LLAUTO
            try:
                return fn(*a, **k)
            finally:
                gr.TARONJA = CERA
        return f

    build_controls(GAME, write_sheet=gr.write_sheet, nine_slice=llauto(gr.nine_slice),
                   nine_slices=llauto(gr.nine_slices),
                   checkbox=gr.checkbox, key_image=gr.key_image, punts=boto(punts_icon), pista=lupa_sola(),
                   font=FONT, bold=BOLD,
                   text=gr.LABEL, title=TITLE, outline=TEXT_OUTLINE, hover=TEXT_HOVER,
                   ink=gr.LABEL, accent=TEXT_HOVER, shadow=TEXT_OUTLINE)


if __name__ == '__main__':
    build_hud()
    build_accions()
    build_targeta()
    print(f'✔ HUD i menú d\'accions a {GAME}')
