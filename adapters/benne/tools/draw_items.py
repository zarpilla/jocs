#!/usr/bin/env python3
"""
Icones provisionals dels objectes d'inventari de Ferro-9, en pixel art (dissenyades a 36×20 i
rasteritzades a l'escala del joc: la mida de la casella de l'inventari de Benne), amb el mateix contorn fosc que els personatges.

draw_placeholders.py les fa servir quan dibuixa el full d'inventari; els objectes que no tenen
icona aquí continuen sortint com una caixa amb el nom.

Ús directe (vista prèvia ampliada): python3 draw_items.py <sortida.png>
"""
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from draw_characters import Canvas  # noqa: E402

W, H = 36, 20

# Paleta
SILVER, SILVER2, SILVER3, SHINE = (206, 214, 224), (156, 166, 180), (110, 118, 132), (255, 255, 255)
BRASS, BRASS2, BRASS3 = (220, 172, 74), (176, 128, 48), (128, 90, 34)
PAPER, PAPER2, INK = (240, 232, 208), (206, 196, 168), (96, 92, 100)
RED, RED2 = (200, 52, 48), (150, 34, 34)
WOOD, WOOD2 = (150, 100, 58), (112, 72, 40)
PINK, PINK2 = (255, 120, 180), (210, 80, 140)
BLACK = (40, 36, 44)


def line(c, x0, y0, x1, y1, col):
    """Línia de píxels (Bresenham)."""
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err = dx + dy
    while True:
        c.px(x0, y0, col)
        if x0 == x1 and y0 == y1:
            return
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def sheet_of_paper(c, x0, y0, x1, y1, lines=True, fold=True):
    c.rect(x0, y0, x1, y1, PAPER)
    c.rect(x1, y0 + 1, x1, y1, PAPER2)
    c.rect(x0, y1, x1, y1, PAPER2)
    if fold:
        c.rect(x1 - 2, y0, x1, y0 + 2, (0, 0, 0, 0))
        c.px(x1 - 2, y0 + 2, PAPER2); c.px(x1 - 2, y0 + 1, PAPER2); c.px(x1 - 1, y0 + 2, PAPER2)
    if lines:
        for y in range(y0 + 5, y1 - 1, 2):
            c.rect(x0 + 2, y, x1 - 3, y, PAPER2)


def stamp_mark(c, cx, cy):
    c.ellipse(cx, cy, 2.5, 2.5, RED)
    c.ellipse(cx, cy, 1.2, 1.2, PAPER)
    c.px(cx, cy, RED)


def form_27b(c, x0, y0, stamped=False):
    """Formulari 27-B: capçalera vermella, ratlles i (si cal) un segell."""
    sheet_of_paper(c, x0, y0, x0 + 11, y0 + 15)
    c.rect(x0 + 2, y0 + 2, x0 + 7, y0 + 3, RED2)
    if stamped:
        stamp_mark(c, x0 + 7, y0 + 11)


# ─── Icones ──────────────────────────────────────────────────────────────────

def clau_anglesa(c):
    # Mànec en diagonal suau, boca oberta a la dreta i anella a l'esquerra. Metall reluent.
    for i in range(18):
        x, y = 8 + i, 12 - i // 6
        c.rect(x, y, x, y + 2, SILVER)
        c.px(x, y + 2, SILVER2)
    c.ellipse(6, 13, 3, 3, SILVER); c.ellipse(6, 13, 1.2, 1.2, (0, 0, 0, 0)); c.px(5, 11, SHINE)
    c.rect(26, 4, 30, 12, SILVER); c.rect(29, 7, 31, 9, (0, 0, 0, 0))  # boca
    c.rect(26, 11, 30, 12, SILVER2)
    for x in (12, 18, 24):
        c.px(x, 12 - (x - 8) // 6, SHINE)
    c.px(28, 5, SHINE)


def formulari_27b(c):
    form_27b(c, 12, 2)


def formulari_segellat(c):
    form_27b(c, 12, 2, stamped=True)


def formulari_triplicat(c):
    for k, (x, y) in enumerate(((7, 1), (12, 2), (17, 3))):
        form_27b(c, x, y, stamped=True)


def plomall(c):
    c.rect(3, 9, 18, 10, WOOD); c.rect(3, 10, 18, 10, WOOD2)  # mànec
    c.rect(18, 8, 20, 11, BRASS2)
    cols = [(240, 120, 80), (250, 200, 90), (120, 180, 220), (230, 90, 140), (250, 240, 220)]
    pts = [(24, 4), (27, 7), (29, 10), (27, 13), (24, 16), (22, 9), (25, 10), (23, 12), (26, 6), (28, 14)]
    for i, (x, y) in enumerate(pts):
        c.ellipse(x, y, 2.2, 1.6, cols[i % len(cols)])
    for x, y in ((31, 9), (31, 11), (30, 6), (30, 15)):
        c.px(x, y, cols[(x + y) % len(cols)])


def segell(c):
    c.rect(10, 13, 25, 17, WOOD); c.rect(10, 16, 25, 17, WOOD2)  # base
    c.rect(11, 18, 24, 18, RED2)                                 # goma entintada
    c.rect(16, 6, 19, 12, RED); c.rect(18, 6, 19, 12, RED2)      # mànec
    c.ellipse(17.5, 4, 3.5, 2.5, RED); c.px(16, 3, (240, 120, 110))


def clau_cambra(c):
    # Clau antiga de llautó amb una etiqueta.
    c.ellipse(8, 9, 4, 4, BRASS); c.ellipse(8, 9, 1.6, 1.6, (0, 0, 0, 0)); c.px(6, 6, (250, 220, 140))
    c.rect(12, 8, 27, 10, BRASS); c.rect(12, 10, 27, 10, BRASS2)
    c.rect(23, 11, 24, 14, BRASS); c.rect(26, 11, 27, 13, BRASS)  # dents
    c.rect(23, 14, 24, 14, BRASS2)
    line(c, 8, 13, 10, 16, (160, 150, 130))                       # cordill
    c.rect(9, 15, 15, 18, PAPER); c.rect(10, 16, 13, 16, RED2)    # etiqueta


def llapis(c):
    c.rect(6, 8, 25, 11, (240, 200, 60)); c.rect(6, 10, 25, 11, (210, 164, 40))
    c.rect(6, 9, 25, 9, (250, 222, 110))
    c.rect(3, 8, 5, 11, (240, 140, 150)); c.rect(5, 8, 5, 11, SILVER2)   # goma i virolla
    for x, top, bot in ((26, 8, 11), (27, 8, 11), (28, 9, 10), (29, 9, 10)):
        c.rect(x, top, x, bot, (228, 196, 150))
    c.rect(30, 9, 31, 10, (70, 70, 80))                                    # punta


def llibreta_torn(c):
    c.rect(9, 2, 26, 17, (92, 70, 54)); c.rect(25, 3, 26, 17, (70, 52, 40))
    c.rect(9, 17, 26, 17, (70, 52, 40))
    c.rect(11, 3, 11, 16, PAPER2)                         # llom de fulls
    c.rect(21, 2, 22, 17, RED)                            # goma elàstica
    c.rect(13, 6, 19, 9, PAPER); c.rect(14, 7, 18, 7, INK)  # etiqueta «TORN»


def caixa_eines(c):
    c.rect(6, 8, 29, 17, RED); c.rect(6, 15, 29, 17, RED2)
    c.rect(6, 10, 29, 10, RED2)                           # tapa
    c.rect(13, 3, 22, 4, BLACK); c.rect(13, 4, 13, 8, BLACK); c.rect(22, 4, 22, 8, BLACK)  # nansa
    c.rect(16, 11, 19, 12, SILVER)                        # tanca
    c.rect(26, 5, 27, 8, SILVER2)                         # mànec d'una eina que sobresurt


def imant_ferro9(c):
    # Imant de ferradura, amb els pols de ferro-9 brillants.
    c.ellipse(17.5, 8, 9, 7, RED)
    c.ellipse(17.5, 8, 4.5, 3.5, (0, 0, 0, 0))
    c.rect(13, 8, 13, 9, (0, 0, 0, 0))
    c.rect(8, 8, 13, 16, RED); c.rect(22, 8, 27, 16, RED)
    c.rect(14, 8, 21, 16, (0, 0, 0, 0))
    c.rect(8, 14, 13, 17, SILVER); c.rect(22, 14, 27, 17, SILVER)
    c.px(9, 15, SHINE); c.px(23, 15, SHINE)
    c.rect(8, 9, 9, 11, (236, 100, 90))
    for x, y in ((5, 18), (4, 15), (31, 18), (32, 15)):   # guspires magnètiques
        c.px(x, y, (130, 206, 224))


def nota_iri(c):
    # Paper doblegat amb lletra de llapis.
    sheet_of_paper(c, 10, 3, 25, 16, lines=False)
    c.rect(10, 9, 25, 9, PAPER2)                          # plec
    for y, (a, b) in zip((5, 7, 11, 13), ((12, 21), (12, 18), (12, 22), (12, 16))):
        for x in range(a, b, 2):
            c.px(x, y, INK); c.px(x + 1, y + (x % 3 == 0), INK)


def avis_reciclatge(c):
    # Avís oficial de la MARE: capçalera rosa amb el cor.
    sheet_of_paper(c, 11, 1, 24, 18, fold=False)
    c.rect(11, 1, 24, 5, PINK); c.rect(11, 5, 24, 5, PINK2)
    c.px(16, 2, PAPER); c.px(18, 2, PAPER); c.rect(16, 3, 18, 3, PAPER); c.px(17, 4, PAPER)  # cor
    c.rect(13, 13, 22, 15, (60, 60, 70)); c.rect(14, 14, 21, 14, PAPER)                     # «3 DIES»


def llapis_ulls(c):
    c.rect(5, 9, 22, 11, BLACK); c.rect(5, 9, 22, 9, (90, 86, 100))
    c.rect(23, 9, 29, 11, (220, 110, 170)); c.rect(23, 11, 29, 11, PINK2)  # caputxó
    c.rect(4, 10, 4, 10, (90, 86, 100))
    c.px(10, 10, (200, 200, 210)); c.px(11, 10, (200, 200, 210))           # lletres platejades


def nota_vet(c):
    # Escrita amb llapis d'ulls al darrere de l'avís: traços negres gruixuts i una vora rosa.
    sheet_of_paper(c, 10, 2, 25, 17, lines=False, fold=False)
    c.rect(10, 17, 25, 17, PINK2)
    for y, a, b in ((5, 12, 22), (8, 12, 20), (11, 12, 23)):
        c.rect(a, y, b, y + 1, BLACK)
        c.px(b, y - 1, BLACK)
    c.rect(19, 14, 23, 15, BLACK)                         # signatura «9»
    c.px(21, 13, BLACK)


def fullet_reeducacio(c):
    # Fullet triptic de colors, amb una cara somrient.
    c.rect(8, 3, 15, 16, (120, 200, 220)); c.rect(16, 2, 23, 17, (250, 220, 90)); c.rect(24, 3, 30, 16, (240, 140, 180))
    c.rect(15, 3, 15, 16, (90, 160, 180)); c.rect(23, 3, 23, 16, (210, 180, 60))
    c.ellipse(19.5, 8, 3, 3, (255, 255, 255))
    c.px(18, 7, BLACK); c.px(21, 7, BLACK); c.rect(18, 9, 21, 9, BLACK); c.px(17, 8, BLACK); c.px(22, 8, BLACK)
    for y in (13, 15):
        c.rect(17, y, 22, y, (200, 160, 50))
        c.rect(9, y - 2, 14, y - 2, (80, 150, 170))
        c.rect(25, y - 2, 29, y - 2, (200, 100, 140))


def nota_pany(c):
    # Paper amb el dibuix del pany fet amb llapis d'ulls.
    sheet_of_paper(c, 10, 2, 25, 17, lines=False, fold=False)
    c.rect(14, 5, 21, 6, BLACK); c.rect(14, 5, 14, 9, BLACK); c.rect(21, 5, 21, 9, BLACK)  # arc
    c.rect(13, 9, 22, 15, BLACK); c.rect(14, 10, 21, 14, PAPER)
    c.ellipse(17.5, 12, 1, 1, BLACK)
    c.px(23, 8, BLACK); c.px(24, 7, BLACK); c.px(23, 10, BLACK)                             # «?»


def escarabat(c):
    # El Senyor Bigotis: escarabat lluent amb antenes llargues com bigotis.
    shell, shell2, sh = (70, 110, 90), (44, 74, 60), (150, 200, 170)
    c.ellipse(18, 11, 7, 5, shell)
    c.rect(18, 6, 18, 16, shell2)                         # separació dels èlitres
    c.px(15, 8, sh); c.px(14, 9, sh); c.px(21, 8, sh)
    c.ellipse(10, 11, 2.5, 2.5, BLACK)                    # cap
    c.px(9, 10, (255, 255, 255))
    line(c, 8, 9, 3, 3, BLACK); line(c, 8, 12, 2, 16, BLACK)  # antenes-bigoti
    for x in (14, 18, 22):                                # potes
        c.px(x, 17, BLACK); c.px(x - 1, 18, BLACK)
        c.px(x, 5, BLACK); c.px(x - 1, 4, BLACK)


def sopa(c):
    # Bol de sopa de reinserció, verdosa i amb bombolles.
    c.ellipse(17.5, 9, 10, 3, (150, 170, 100))
    c.ellipse(17.5, 9, 10, 3, (150, 170, 100))
    for y in range(10, 18):
        w = int(10 - (y - 10) * 0.9)
        c.rect(int(17.5 - w), y, int(17.5 + w), y, (200, 206, 214) if y < 16 else (160, 166, 176))
    c.rect(12, 18, 23, 18, (140, 146, 156))
    for x, y in ((13, 8), (19, 9), (22, 8)):
        c.px(x, y, (210, 230, 160)); c.px(x, y - 1, (190, 214, 140))
    c.ellipse(16, 4, 1.2, 1.2, (210, 230, 160)); c.px(21, 2, (210, 230, 160))  # bombolles que s'escapen


# ─── Acte 2 ──────────────────────────────────────────────────────────────────

STEEL_B, STEEL_B2, F9, F9b = (150, 156, 164), (100, 106, 114), (170, 200, 230), (230, 245, 255)


def tros_cartell(c):
    c.rect(11, 4, 25, 16, (236, 236, 226)); c.rect(11, 15, 25, 16, (200, 200, 190))
    c.rect(11, 4, 14, 16, (60, 160, 90))                     # tros de la vora verda del cartell
    c.px(25, 4, (0, 0, 0, 0)); c.px(24, 4, (0, 0, 0, 0)); c.px(25, 5, (0, 0, 0, 0))  # estripat


def nota_mida(c):
    tros_cartell(c)
    c.rect(16, 7, 23, 8, BLACK); c.rect(16, 11, 21, 12, BLACK)   # «6 ½»
    c.px(23, 12, BLACK)


def biga(c, col, col2, hi):
    c.rect(2, 8, 33, 12, col); c.rect(2, 8, 33, 8, hi); c.rect(2, 12, 33, 12, col2)


def biga_acer(c):
    biga(c, STEEL_B, STEEL_B2, (196, 202, 210))


def biga_ferro9(c):
    biga(c, F9, (120, 150, 180), F9b)
    c.px(10, 9, SHINE); c.px(22, 9, SHINE)


def serra(c):
    c.rect(6, 9, 26, 11, (200, 206, 216))
    for x in range(6, 26, 2):
        c.px(x, 12, (150, 156, 166))
    c.rect(26, 7, 31, 14, (120, 60, 40)); c.rect(27, 9, 29, 12, (0, 0, 0, 0))


def tram(c, n):
    c.rect(8, 8, 27, 12, STEEL_B); c.rect(8, 8, 27, 8, (196, 202, 210)); c.rect(8, 12, 27, 12, STEEL_B2)
    for x in (10, 25):
        c.px(x, 10, BLACK)                                    # forats dels cargols
    for i in range(n):                                        # marques del número de tram
        c.px(16 + i * 2, 15, (230, 180, 40))


def tram_biga_1(c):
    tram(c, 1)


def tram_biga_2(c):
    tram(c, 2)


def tram_biga_3(c):
    tram(c, 3)


def biga_muntada(c):
    biga_acer(c)
    for x in (12, 23):
        c.rect(x, 7, x, 13, STEEL_B2); c.px(x, 10, BLACK)


def nota_amagatall(c):
    sheet_of_paper(c, 10, 3, 25, 16, lines=False)
    c.rect(16, 6, 19, 6, INK); c.rect(19, 6, 19, 11, INK); c.px(18, 8, INK); c.px(17, 10, INK)  # un 7
    for x in range(12, 23, 2):
        c.px(x, 13, INK)


def pols_rovell(c):
    c.ellipse(17.5, 12, 9, 4, (150, 80, 44))
    for x, y in ((12, 10), (16, 9), (21, 10), (24, 12), (14, 13), (19, 12)):
        c.px(x, y, (190, 110, 60))
    c.px(9, 15, (130, 70, 40)); c.px(27, 15, (130, 70, 40))



def molla(c):
    for i, x in enumerate(range(9, 27, 3)):
        c.ellipse(x + 1, 10, 1.6, 5, (180, 186, 196))
        c.ellipse(x + 1, 10, 0.6, 4, (0, 0, 0, 0))
    c.rect(5, 9, 8, 10, (180, 186, 196)); c.rect(28, 9, 31, 10, (180, 186, 196))


def llima(c):
    c.rect(6, 9, 24, 11, (170, 176, 186))
    for x in range(7, 24, 2):
        c.px(x, 10, (120, 126, 136))
    c.rect(24, 8, 31, 12, (120, 70, 40))


def diapaso(c):
    c.rect(8, 7, 22, 8, F9); c.rect(8, 12, 22, 13, F9)       # les dues branques
    c.rect(22, 7, 24, 13, F9)
    c.rect(24, 9, 31, 11, (120, 150, 180))                  # mànec
    c.px(12, 7, F9b); c.px(16, 12, F9b)


def diapaso_espatllat(c):
    diapaso(c)
    c.rect(8, 7, 11, 8, (0, 0, 0, 0)); c.rect(8, 12, 12, 13, (0, 0, 0, 0))  # puntes llimades de més
    for x, y in ((5, 5), (4, 9), (5, 15)):
        c.px(x, y, (255, 240, 120))                         # xiulet


ICONS = {f.__name__: f for f in (
    clau_anglesa, formulari_27b, formulari_segellat, formulari_triplicat, plomall, segell, clau_cambra,
    llapis, llibreta_torn, caixa_eines, imant_ferro9, nota_iri, avis_reciclatge, llapis_ulls, nota_vet,
    fullet_reeducacio, nota_pany, escarabat, sopa,
    tros_cartell, nota_mida, biga_acer, biga_ferro9, serra, tram_biga_1, tram_biga_2, tram_biga_3, biga_muntada,
    nota_amagatall, pols_rovell, molla, llima, diapaso, diapaso_espatllat,
)}


def icon(item_id):
    """Imatge de l'objecte a la mida de la casella, o None si encara no en té."""
    draw = ICONS.get(item_id)
    if draw is None:
        return None
    c = Canvas(W, H)
    draw(c)
    c.outline()
    return c.img


if __name__ == '__main__':
    scale, cols = 4, 5
    ids = list(ICONS)
    W, H = icon(ids[0]).size
    rows = (len(ids) + cols - 1) // cols
    out = Image.new('RGBA', (cols * (W + 4) * scale, rows * (H + 4) * scale), (27, 58, 92, 255))
    for i, iid in enumerate(ids):
        img = icon(iid).resize((W * scale, H * scale), Image.NEAREST)
        out.alpha_composite(img, ((i % cols) * (W + 4) * scale + 2 * scale, (i // cols) * (H + 4) * scale + 2 * scale))
    out.save(sys.argv[1] if len(sys.argv) > 1 else 'items.png')
