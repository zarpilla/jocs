"""
Icones d'inventari de Suma Zero a 640×360: els mateixos 24 objectes de hd/items.py, redibuixats a la casella
nova (65×36 en lloc de 49×27) amb el mateix sistema (Ic de hd/items.py: volum, rampes per material, contorn fosc
selectiu) i aprofitant els píxels de més (etiquetes, codis de barres, cargols, costures, reflexos, textures).

No toca hd/items.py: en reaprofita els materials i les eines i només canvia la mida del llenç.
Ho fan servir hd640/draw_items.py i draw_items.py (a 640).
"""
import hd640  # noqa: F401
import math

from hd.characters import Fig
from hd.items import (Ic, paper, torn, M, PAP_W, PAP_C, INKB, INKG, STAMP, RULE, RED, CORPG, SUNY, ORNG, SKIN, HAIR,
                      ACER, PLAST, BRASS, CYAN, DARK, MANI, NETB, CLEAR, FOIL, BREAD, TUNA, GOLDK, NAPK, LEATHB, BADGE,
                      NAVY, CHEESE, HAM, MORT, WRAP, BUCKET, WARNY, FIRE, CARDW)

W, H = 65, 36

# Lletres de 4×6, per a les etiquetes que ara hi caben
FONT46 = {
    'G': ('.###', '#...', '#...', '#.##', '#..#', '.###'), 'I': ('###', '.#.', '.#.', '.#.', '.#.', '###'),
    'N': ('#..#', '##.#', '##.#', '#.##', '#.##', '#..#'), 'E': ('####', '#...', '###.', '#...', '#...', '####'),
    'B': ('###.', '#..#', '###.', '#..#', '#..#', '###.'), 'R': ('###.', '#..#', '###.', '#.#.', '#..#', '#..#'),
    'A': ('.##.', '#..#', '#..#', '####', '#..#', '#..#'), '3': ('###.', '...#', '.##.', '...#', '...#', '###.'),
}


class Ic640(Ic):
    """Llenç d'una icona de 640: el mateix Ic, a 65×36."""

    def __init__(self):
        Fig.__init__(self, W, H)

    def line(self, x0, y0, x1, y1, mat, lvl):
        n = max(1, int(max(abs(x1 - x0), abs(y1 - y0))))
        for i in range(n + 1):
            self.px(round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n), mat, lvl)


# ─── Acte 1 ──────────────────────────────────────────────────────────────────

def caixa_cartro(f):
    """La caixa del router, oberta, amb les solapes enlaire, l'etiqueta amb codi de barres, les fletxes de «cap
    amunt» i la cinta d'embalar arrencada."""
    S = f.R(13, 13, 49, 32)
    f.drop(S)
    f.fill(S, MANI, lambda x, y: 3.0 - (x - 13) / 36 * 1.2 - (0.8 if y == 13 else 0), rim=(0.6, -1.0))
    f.fill(f.P([(13, 13), (8, 4), (25, 5), (28, 13)]), MANI, lambda x, y: 4.2 - (y - 4) * 0.1)
    f.fill(f.P([(49, 13), (56, 5), (39, 4), (36, 13)]), MANI, lambda x, y: 2.6 - (y - 4) * 0.08)
    for x in range(10, 26, 3):                                           # les ondes del cartró, al cantell
        f.shade(x, 5 + (x - 8) // 6, -0.6)
    f.rect(14, 14, 48, 16, MANI, 0.6)                                    # l'interior, fosc
    f.rect(14, 17, 48, 17, MANI, 1.4)
    S = f.R(19, 20, 34, 27)                                              # l'etiqueta
    f.fill(S, PAP_W, 4.4, rim=(0.4, -1.2))
    f.rect(21, 21, 30, 21, INKG, 1.4)
    f.rect(21, 23, 27, 23, INKG, 2.0)
    for x in range(21, 33):                                              # el codi de barres
        if x % 3 != 1 or x in (21, 32):
            f.rect(x, 25, x, 26, DARK, 1.0)
    for x0 in (23, 28):                                                  # les fletxes «cap amunt», impreses
        f.px(x0 + 1, 29, DARK, 1.6)
        f.dots([(x0, 30), (x0 + 1, 30), (x0 + 2, 30), (x0 + 1, 31)], DARK, 1.6)
    f.rect(39, 18, 45, 30, MANI, 2.0)                                    # la cinta d'embalar arrencada
    for y in range(18, 31, 2):
        f.px(39 + (y // 2) % 2, y, MANI, 3.0)
    f.rect(40, 18, 45, 18, MANI, 3.2)
    f.shade(14, 18, 1.0)


def cable_alimentacio(f):
    """El cable de la cafetera: l'endoll amb les dues potes, el cable enrotllat i el connector (amb els tres forats)."""
    pts = [(19, 19), (25, 27), (32, 12), (39, 27), (45, 17)]
    for p0, p1 in zip(pts, pts[1:]):
        f.limb(p0, p1, 1.4, 1.4, PLAST, 2.8, amp=2.0)
    S = f.R(7, 12, 18, 25)
    f.drop(S)
    f.fill(S, PLAST, lambda x, y: 3.6 - (x - 7) * 0.15, rim=(0.6, -1.2))
    for x in (13, 15, 17):                                               # les estries de l'endoll
        f.rect(x, 14, x, 23, PLAST, 1.6)
    f.rect(1, 15, 6, 16, ACER, 5.2)                                      # les potes
    f.rect(1, 21, 6, 22, ACER, 4.6)
    f.dots([(2, 15), (2, 21)], ACER, 6.4)
    f.rect(18, 17, 19, 20, PLAST, 2.0)                                   # el protector del cable
    S = f.R(45, 12, 58, 24)
    f.drop(S)
    f.fill(S, PLAST, lambda x, y: 3.2 - (x - 45) * 0.15, rim=(0.6, -1.2))
    f.rect(48, 15, 55, 21, DARK, 1.0)
    for x in (50, 53):
        f.rect(x, 17, x, 19, ACER, 3.6)
    f.dots([(51, 20), (52, 20)], ACER, 2.6)
    f.rect(44, 17, 45, 19, PLAST, 2.0)


def pizza(f):
    """La pizza de demà: quatre talls, tomàquet, formatge fos que s'estira, olives i alfàbrega, en el seu cartró."""
    S = f.E(32, 19, 20, 13)
    f.drop(S)
    f.fill(S, MANI, lambda x, y: 3.6 - (y - 6) * 0.06, rim=(0.6, -1.0))
    f.fill(f.E(32, 17, 16.5, 11.5), ORNG, lambda x, y: 4.4 - abs(y - 17) * 0.08)
    for (x, y) in f.E(32, 17, 16.5, 11.5) - f.E(32, 17, 14.5, 9.6):        # les bombolles torrades de la crosta
        if (x * 7 + y * 3) % 11 == 0:
            f.px(x, y, ORNG, 2.4)
    f.fill(f.E(32, 17, 14, 9), RED, 3.4, rim=None)
    for cx, cy, rx, ry in ((27, 15, 4.6, 3.0), (37, 20, 5.3, 3.2), (33, 13, 3.3, 2.1), (24, 20, 3.7, 2.4), (40, 13, 2.6, 1.8)):
        f.fill(f.E(cx, cy, rx, ry), SUNY, lambda x, y, cy=cy: 4.2 - (y - cy) * 0.35, rim=None)
    for x in range(19, 46):
        f.px(x, 17, ORNG, 1.4)
    for y in range(8, 28):
        f.px(32, y, ORNG, 1.4)
    for (x, y) in ((29, 21), (36, 12), (22, 14)):                        # les olives
        f.dots([(x, y), (x + 1, y)], DARK, 1.6)
        f.px(x, y - 1, DARK, 2.4)
    f.dots([(40, 18), (41, 18), (41, 17), (23, 17), (24, 16), (34, 23), (35, 23)], CORPG, 3.0)
    f.dots([(41, 18), (24, 17), (35, 24)], CORPG, 1.8)


def auricular(f):
    """Els auriculars de diadema de l'Iri: la diadema negra encoixinada, els lliscadors d'acer i les copes vermelles."""
    for i in range(110):
        a = math.pi * i / 109
        f.px(32 - 16 * math.cos(a), 23 - 19 * math.sin(a), PLAST, 4.4)
        f.px(32 - 16 * math.cos(a), 24 - 19 * math.sin(a), PLAST, 3.0)
        f.px(32 - 15.2 * math.cos(a), 25 - 18.4 * math.sin(a), PLAST, 1.8)
    for i in range(8, 102, 6):                                           # el coixí de la diadema, amb costures
        a = math.pi * i / 109
        f.shade(32 - 16 * math.cos(a), 24 - 19 * math.sin(a), -1.2)
    for cx, sx in ((16, 1), (48, -1)):
        f.rect(cx - 1, 11, cx + 1, 15, ACER, 4.0, rim=(0.6, -1.0))       # el lliscador
        S = f.E(cx, 24, 6.1, 8.8)
        f.drop(S)
        f.fill(S, PLAST, 3.0, rim=(0.8, -1.2))
        f.fill(f.E(cx + sx * 1.6, 24, 4.0, 6.6), RED, lambda x, y: 4.8 - (y - 17) * 0.15, rim=(0.8, -1.0))
        f.fill(f.E(cx + sx * 1.6, 24, 1.6, 3.0), RED, 2.4, rim=None)        # la reixeta de l'altaveu
        f.px(cx + sx * 1.6 - 1, 20, RED, 6.0)


def auriculars_boto(f):
    """Dos auriculars de botó de recanvi, negres amb un punt vermell i la reixeta, units per un fil amb el micro."""
    for x in range(23, 43):
        f.px(x, 27 + round(3.3 * math.sin(math.pi * (x - 23) / 19)), PLAST, 2.4)
    f.rect(31, 29, 34, 31, PLAST, 3.2, rim=(0.6, -1.0))                  # el micro del fil
    f.px(32, 30, ACER, 4.0)
    for cx in (19, 45):
        S = f.E(cx, 17, 5.6, 5.6)
        f.drop(S)
        f.fill(S, PLAST, lambda x, y: 3.6 - (y - 12) * 0.12, rim=(0.8, -1.2))
        f.fill(f.E(cx, 17, 2.2, 2.2), RED, 4.6, rim=None)
        f.px(cx - 1, 16, RED, 6.0)
        d = 3 if cx < 32 else -3
        for y in range(22, 28):
            f.px(cx + d, y, PLAST, 3.0)
            f.px(cx + d + (1 if d > 0 else -1), y, PLAST, 1.8)
        f.shade(cx - 3, 14, 1.6)


def cable_xarxa(f):
    """El cable de xarxa blau, enrotllat, amb el connector transparent (els vuit contactes i la pestanya) i una
    mossegada d'en Diu."""
    for k, (cx, cy, rx, ry) in enumerate(((27, 17, 14.7, 10), (33, 19, 13.3, 8.7))):
        f.ring(cx, cy, rx, ry, NETB, 3.4 - k * 0.6, th=2.4)
    for i in range(60):
        a = math.pi * (1.1 + 0.8 * i / 59)
        f.px(round(27 + 14.7 * math.cos(a)), round(17 + 10 * math.sin(a)), NETB, 4.8)
    f.limb((43, 21), (52, 27), 1.3, 1.3, NETB, 3.0, amp=1.6)
    f.rect(50, 24, 53, 28, CLEAR, 2.8, rim=(0.4, -0.8))                 # la funda del connector
    S = f.R(53, 22, 62, 31)
    f.drop(S)
    f.fill(S, CLEAR, lambda x, y: 3.4 - (x - 53) * 0.12, rim=(0.8, -1.2))
    for x in range(54, 62):
        f.px(x, 30, GOLDK, 4.2 if x % 2 else 2.4)
        f.px(x, 29, NETB, 2.6 if x % 3 else 3.4)                         # els fils de colors, a dins
    f.rect(54, 20, 58, 21, CLEAR, 2.6)                                   # la pestanya
    f.px(55, 23, CLEAR, 5.0)
    f.dots([(17, 23), (18, 24), (16, 24), (19, 25), (17, 25)], DARK, 1.0)   # les dents del gat
    f.dots([(18, 23), (16, 25)], NETB, 1.6)


def entrepa(f):
    """L'entrepà de tonyina: mitja barra embolicada en paper d'alumini arrugat, amb l'enciam i la tonyina."""
    S = f.P([(8, 20), (13, 12), (53, 9), (59, 16), (55, 25), (12, 28)])
    f.drop(S)
    f.fill(S, BREAD, lambda x, y: 4.2 - (y - 9) * 0.1 - (x - 8) * 0.008, rim=(0.6, -1.2))
    for x in range(16, 52, 8):                                           # els talls de la crosta
        y = 13 - x // 27
        f.dots([(x, y), (x + 1, y), (x + 2, y + 1)], BREAD, 2.0)
        f.px(x + 1, y + 1, BREAD, 5.0)
    for (x, y) in ((22, 17), (30, 15), (40, 14), (18, 22)):              # la farina
        f.px(x, y, BREAD, 5.4)
    for x in range(11, 56):                                              # el farcit: enciam i tonyina
        y = 20 + round((x - 11) * -0.05)
        f.px(x, y, CORPG, 3.6 if x % 3 else 2.4)
        if x % 4 == 0:
            f.px(x, y - 1, CORPG, 4.2)
        if x % 5 != 1:
            f.px(x, y + 1, TUNA, 3.0 if x % 2 else 2.4)
    S2 = f.P([(35, 8), (60, 12), (61, 23), (56, 29), (35, 29)])
    f.fill(S2, FOIL, lambda x, y: 3.8 + (1.2 if (x + y * 2) % 9 == 0 else 0) - (x - 35) * 0.05, rim=(0.8, -1.2))
    for (a, b) in (((39, 10), (42, 27)), ((47, 11), (45, 28)), ((54, 13), (58, 23))):   # les arrugues
        f.line(a[0], a[1], b[0], b[1], FOIL, 2.4)
    for (x, y) in ((40, 13), (45, 19), (51, 15), (55, 24), (41, 24), (49, 25)):
        f.shade(x, y, 1.6)
        f.shade(x + 1, y, 0.8)


def clau_casa(f):
    """La clau de casa, de llautó, amb l'anella i un clauer de plàstic groc amb una etiqueta escrita."""
    f.ring(16, 17, 8.6, 8.6, ACER, 4.0, th=1.8)
    S = f.E(32, 17, 7.3, 7.3)
    f.drop(S)
    f.fill(S, GOLDK, lambda x, y: 4.2 - (x - 25) * 0.1 - (y - 10) * 0.1, rim=(0.8, -1.2))
    f.ring(32, 17, 5.2, 5.2, GOLDK, 2.6, th=0.8)                         # el relleu del cap
    f.fill(f.E(30, 17, 2.1, 2.1), DARK, 0.6, rim=None)
    S = f.R(39, 15, 58, 20)
    f.drop(S)
    f.fill(S, GOLDK, lambda x, y: 3.8 - (y - 15) * 0.3, rim=(0.6, -1.0))
    f.rect(40, 17, 57, 17, GOLDK, 2.4)                                   # la ranura
    for (x, d) in ((44, 3), (47, 4), (50, 2), (53, 4), (56, 3)):         # les dents
        f.rect(x, 21, x + 1, 20 + d, GOLDK, 3.0)
    S = f.P([(5, 24), (13, 22), (16, 33), (7, 35)])
    f.drop(S)
    f.fill(S, SUNY, 3.8, rim=(0.6, -1.0))
    f.fill(f.E(9, 25, 1.0, 1.0), DARK, 1.0, rim=None)                    # el forat de l'etiqueta
    f.scrib(8, 13, 28, INKB, 2.0, seed=1, dens=0.95, tall=0)
    f.scrib(8, 12, 31, INKB, 2.0, seed=2, dens=0.95, tall=0)


def tap(f):
    """El clauer d'en Tomàs: un tap vermell de la cervesera (amb l'estrella de llautó), l'anella i dues claus."""
    S = f.E(20, 19, 13, 10.6)
    f.drop(S)
    f.fill(S, RED, lambda x, y: 4.0 - (x - 7) * 0.08 - (y - 8) * 0.1, rim=(0.8, -1.2))
    for i in range(24):                                                  # l'estriat del tap
        a = i / 24 * 2 * math.pi
        f.px(round(20 + 12.3 * math.cos(a)), round(19 + 9.8 * math.sin(a)), RED, 1.6)
    S = f.E(20, 17, 5.3, 4.5)
    f.fill(S, BRASS, lambda x, y: 4.6 - (x - 15) * 0.15 - (y - 13) * 0.25, rim=(0.8, -1.0))
    for (x, y) in ((20, 14), (18, 16), (19, 16), (21, 16), (22, 16), (19, 17), (21, 17), (18, 19), (22, 19)):
        f.px(x, y, BRASS, 2.0)                                           # l'estrella
    f.ring(39, 16, 6, 6, ACER, 4.2, th=1.6)
    for k, (mat, y0) in enumerate(((ACER, 10), (GOLDK, 20))):
        S = f.E(48, y0 + 3, 4, 4)
        f.drop(S)
        f.fill(S, mat, 4.0, rim=(0.8, -1.0))
        f.fill(f.E(47, y0 + 3, 1.0, 1.0), DARK, 1.0, rim=None)
        f.rect(51, y0 + 1, 62, y0 + 4, mat, 3.6, rim=(0.6, -1.0))
        f.rect(53, y0 + 2, 61, y0 + 2, mat, 2.6)
        f.rect(56, y0 + 5, 57, y0 + 7, mat, 2.6)
        f.rect(60, y0 + 5, 60, y0 + 6, mat, 2.6)


def recepta(f):
    """La recepta secreta: una servilleta de bar gofrada, plegada, escrita amb bolígraf vermell, amb una taca de cafè."""
    S = f.P([(15, 4), (49, 5), (51, 32), (16, 32)])
    f.drop(S)
    f.fill(S, NAPK, lambda x, y: 4.6 - (x - 15) * 0.02 - (y - 4) * 0.02, rim=(0.6, -1.0))
    for y in range(6, 32, 3):
        for x in range(17, 49, 3):
            f.shade(x, y, -0.5)
    for (x, y) in f.E(43, 10, 3.6, 2.6) - f.E(43, 10, 2.6, 1.6):         # l'anella de cafè
        f.shade(x, y, -1.0)
    f.fill(f.P([(39, 24), (51, 24), (51, 32)]), NAPK, 3.0, rim=(0.4, -1.0))
    f.text(19, 8, '1.', STAMP, 2.0)
    f.scrib(26, 40, 10, STAMP, 2.0, seed=3)
    f.scrib(26, 36, 13, STAMP, 2.0, seed=4)
    f.text(19, 17, '2.', STAMP, 2.0)
    f.scrib(26, 38, 19, STAMP, 2.0, seed=5)
    f.scrib(19, 33, 26, STAMP, 2.2, seed=8, dens=0.9)
    f.scrib(19, 31, 28, STAMP, 2.2, seed=9, dens=1.0, tall=0)            # subratllat dues vegades


def comandament(f):
    """El comandament de la tele: negre, llarg, amb el botó vermell, el teclat, la creueta i els botons de volum."""
    S = f.P([(7, 13), (56, 9), (59, 20), (9, 25)])
    f.drop(S)
    f.fill(S, PLAST, lambda x, y: 2.4 - (y - 9) * 0.1, rim=(0.8, -1.2))
    f.fill(f.E(13, 17, 2.6, 2.6), RED, 4.2, rim=None)
    f.px(12, 16, RED, 5.6)
    for i in range(4):
        for j in range(3):
            f.rect(20 + i * 4, 13 + j * 3, 21 + i * 4, 13 + j * 3, PLAST, 4.8)
    S = f.E(45, 15, 4, 3.4)
    f.fill(S, PLAST, 3.6, rim=(0.6, -0.8))
    f.dots([(45, 13), (43, 15), (47, 15), (45, 17)], PLAST, 5.0)
    f.px(45, 15, PLAST, 1.0)
    f.rect(51, 13, 52, 19, PLAST, 3.4, rim=(0.6, -0.8))                  # el volum
    f.px(55, 13, RED, 3.0)
    f.px(56, 13, RED, 4.0)


def maleti(f):
    """El maletí de pell, amb la nansa, els tancaments amb pany, el pespunt i l'adhesiu groc."""
    S = f.R(8, 10, 56, 32)
    f.drop(S)
    f.fill(S, LEATHB, lambda x, y: 4.0 - (x - 8) * 0.03 - (y - 10) * 0.06, rim=(0.8, -1.4))
    f.rect(8, 16, 56, 16, LEATHB, 2.2)
    f.rect(8, 17, 56, 17, LEATHB, 4.4)
    for x in range(24, 41):
        f.px(x, 5, LEATHB, 3.6)
        f.px(x, 6, LEATHB, 2.4)
    f.rect(24, 5, 24, 10, LEATHB, 3.0)
    f.rect(40, 5, 40, 10, LEATHB, 2.4)
    for x0 in (22, 39):
        f.rect(x0, 9, x0 + 2, 10, BRASS, 4.0)                            # les anelles de la nansa
    for x0 in (14, 46):
        f.rect(x0, 14, x0 + 3, 19, BRASS, 4.4, rim=(0.6, -1.0))
        f.px(x0 + 1, 17, DARK, 1.0)                                      # el pany
    S = f.R(19, 21, 33, 28)
    f.fill(S, SUNY, 4.0, rim=(0.4, -0.8))
    f.scrib(20, 31, 23, INKG, 1.2, seed=2)
    f.scrib(20, 28, 25, INKG, 1.2, seed=4)
    f.scrib(20, 30, 27, STAMP, 1.6, seed=6, dens=1.0, tall=0)
    for x in range(10, 55, 3):
        f.px(x, 30, LEATHB, 5.0)
    for y in range(19, 30, 3):
        f.px(10, y, LEATHB, 5.0)
        f.px(54, y, LEATHB, 4.4)


def ulleres(f):
    """Ulleres de pasta negra, gruixudes, sense graduació (però amb autoritat): els vidres amb reflex i els cargols."""
    for cx in (20, 44):
        S = f.E(cx, 18, 10.6, 8.6)
        f.drop(S)
        f.fill(S, DARK, 2.4, rim=(0.6, -0.4))
        f.fill(f.E(cx, 18, 6.6, 4.8), CYAN, lambda x, y, cx=cx: 1.6 + (1.8 if (x - cx) + (y - 18) < -4 else 0), rim=None)
        for i in range(4):                                               # el reflex, en diagonal
            f.px(cx - 4 + i, 16 - i, CYAN, 4.4)
    f.rect(30, 14, 34, 16, DARK, 2.4)
    f.rect(31, 14, 33, 14, DARK, 3.4)
    f.rect(2, 13, 9, 14, DARK, 2.0)
    f.rect(55, 13, 62, 14, DARK, 2.0)
    f.dots([(10, 13), (54, 13)], ACER, 4.6)                              # els cargols de les frontisses


def _badge(f, x0, y0, face, hair, lit=0.0):
    """Una acreditació plastificada del BCMU: la foto, el nom, el codi de barres i la franja vermella de «manteniment»."""
    S = f.R(x0, y0, x0 + 23, y0 + 29)
    f.drop(S)
    f.fill(S, BADGE, lambda x, y: 4.6 + lit - (y - y0) * 0.02, rim=(0.8, -1.2))
    f.rect(x0 + 8, y0 - 3, x0 + 15, y0, ACER, 4.0, rim=(0.6, -1.0))      # la pinça
    f.rect(x0 + 10, y0 - 2, x0 + 13, y0 - 2, DARK, 1.0)
    f.rect(x0 + 1, y0 + 1, x0 + 22, y0 + 5, NAVY, 3.0)
    f.dots([(x0 + 3 + i, y0 + 3) for i in range(0, 16, 2)], SUNY, 4.0)
    f.rect(x0 + 2, y0 + 8, x0 + 10, y0 + 17, CYAN, 3.4)                  # la foto
    f.fill(f.E(x0 + 6, y0 + 13, 2.6, 3.2), face, 3.6, rim=None)
    f.rect(x0 + 4, y0 + 9, x0 + 8, y0 + 10, hair, 2.0)
    f.rect(x0 + 3, y0 + 16, x0 + 9, y0 + 17, NAVY, 2.6)                  # les espatlles
    for k in range(3):
        f.rect(x0 + 12, y0 + 9 + k * 3, x0 + 20 - k * 2, y0 + 9 + k * 2 + k, INKG, 1.4)
    for x in range(x0 + 12, x0 + 21):                                    # el codi de barres
        if x % 3:
            f.px(x, y0 + 17, DARK, 1.2)
    f.rect(x0 + 1, y0 + 21, x0 + 22, y0 + 25, RED, 3.4)
    f.dots([(x0 + 3 + i, y0 + 23) for i in range(0, 17, 3)], BADGE, 5.0)
    f.shade(x0 + 2, y0 + 1, 1.4)
    f.shade(x0 + 3, y0 + 2, 1.0)
    f.shade(x0 + 4, y0 + 3, 0.6)


def acreditacions(f):
    """Les dues acreditacions, una damunt de l'altra (la de l'Iri i la de la Vet)."""
    _badge(f, 11, 5, SKIN, HAIR, lit=-0.4)
    _badge(f, 29, 4, SKIN, HAIR)


def acreditacio(f):
    """Una acreditació, penjada del cordó blau marí del banc (amb el mosquetó)."""
    for i in range(19):
        f.px(11 + i, 2 + round(math.sin(i / 5) * 1.6), NAVY, 3.0)
        f.px(11 + i, 3 + round(math.sin(i / 5) * 1.6), NAVY, 2.0)
        f.px(48 - i, 2 + round(math.sin(i / 5) * 1.6), NAVY, 2.4)
        f.px(48 - i, 3 + round(math.sin(i / 5) * 1.6), NAVY, 1.6)
    _badge(f, 20, 5, SKIN, HAIR)


# ─── Acte 2: el BCMU ────────────────────────────────────────────────────────

def entrepa_suis(f):
    """L'entrepà de la màquina: mig sandvitx triangular de pa de motlle, de tres quarts, amb les capes (pa, pernil,
    formatge amb forats, pa) i l'etiqueta del preu."""
    top = f.P([(8, 19), (40, 4), (56, 19)])
    cut = f.R(8, 20, 56, 30)
    f.drop(top | cut)
    f.fill(top, PAP_C, lambda x, y: 4.6 - (y - 4) * 0.04, rim=None)
    for (x, y) in top:
        if (x - 1, y) not in top or (x + 1, y) not in top or (x, y - 1) not in top:
            f.px(x, y, BREAD, 3.2)
    for (x, y) in ((24, 14), (33, 11), (44, 16), (30, 17)):              # la mica de la molla
        f.shade(x, y, -0.5)
    rows = [(BREAD, 3.0), (PAP_C, 4.2), (PAP_C, 3.8), (HAM, 3.8), (HAM, 3.0), (CHEESE, 4.4), (CHEESE, 3.8),
            (CHEESE, 3.4), (PAP_C, 4.0), (PAP_C, 3.6), (BREAD, 2.4)]
    for i, (mat, l) in enumerate(rows):
        f.rect(8, 20 + i, 56, 20 + i, mat, lambda x, y, l=l: l - (x - 8) * 0.025)
    for x in range(10, 56, 3):                                           # la vora del pernil
        f.px(x, 23, HAM, 4.6)
    for x in (16, 30, 45):
        f.dots([(x, 26), (x + 1, 26), (x + 1, 27)], CHEESE, 2.0)
    f.rect(8, 20, 8, 30, BREAD, 2.0)
    f.rect(56, 20, 56, 30, BREAD, 1.6)
    S = f.R(40, 5, 62, 13)
    f.drop(S)
    f.fill(S, WRAP, 3.0, rim=(0.6, -1.0))
    f.text(43, 7, '8.50', CARDW, 5.6)


def entrepa_ballester(f):
    """L'entrepà d'en Ballester: una barra embolicada en paper d'alumini arrugat, oberta per un cap (mortadel·la)."""
    S = f.P([(7, 16), (12, 9), (56, 8), (61, 15), (57, 27), (11, 28)])
    f.drop(S)
    f.fill(S, FOIL, lambda x, y: 4.6 - (y - 8) * 0.1 + (0.8 if y == 11 else 0), rim=(0.8, -1.4))
    for (a, b) in (((21, 11), (27, 25)), ((40, 9), (36, 27)), ((51, 11), (55, 24)), ((30, 10), (31, 18))):
        n = max(abs(b[0] - a[0]), abs(b[1] - a[1]))
        for i in range(n + 1):
            x = round(a[0] + (b[0] - a[0]) * i / n)
            y = round(a[1] + (b[1] - a[1]) * i / n)
            f.shade(x, y, -1.4)
            f.shade(x + 1, y, 1.2)
    for (x, y) in ((25, 15), (45, 20), (16, 22)):
        f.shade(x, y, 1.8)
    S2 = f.E(12, 19, 5.3, 8.6)
    f.fill(S2, BREAD, lambda x, y: 4.0 - (x - 7) * 0.08, rim=(0.6, -1.0))
    f.fill(f.E(12, 19, 3.2, 6.1), MORT, lambda x, y: 3.6 - (y - 13) * 0.08, rim=None)
    f.dots([(11, 16), (13, 19), (12, 22), (11, 20), (13, 15)], PAP_C, 4.6)


def targeta(f):
    """La targeta de planta de la Rius: plàstic blanc, banda blau marí, la foto (enfadada), el xip i el pis 3."""
    S = f.P([(11, 8), (55, 5), (56, 29), (12, 32)])
    f.drop(S)
    f.fill(S, CARDW, lambda x, y: 4.6 - (x - 11) * 0.015 - (y - 5) * 0.025, rim=(0.8, -1.2))
    f.fill(f.P([(11, 9), (55, 6), (55, 12), (11, 15)]), NAVY, 3.0, rim=None)
    f.dots([(15 + i, 11 - i // 12) for i in range(0, 36, 3)], SUNY, 4.2)
    f.rect(15, 17, 24, 28, CYAN, 3.4)
    f.fill(f.E(19, 23, 2.9, 3.5), SKIN, 3.6, rim=None)
    f.rect(16, 18, 23, 20, HAIR, 2.4)
    f.dots([(17, 22), (18, 23), (21, 23), (22, 22)], DARK, 1.0)          # les celles arrufades
    f.rect(18, 26, 20, 26, DARK, 1.6)
    f.rect(17, 28, 22, 28, NAVY, 2.4)
    f.rect(41, 17, 49, 24, GOLDK, 4.0, rim=(0.6, -1.0))
    f.rect(45, 17, 45, 24, GOLDK, 2.4)
    f.rect(41, 20, 49, 20, GOLDK, 2.4)
    f.rect(41, 22, 44, 22, GOLDK, 2.4)
    for k in range(2):
        f.rect(28, 18 + k * 3, 37 - k * 3, 18 + k * 3, INKG, 1.4)
    f.text(28, 23, '3', RED, 3.4, font=FONT46)
    f.shade(13, 16, 1.6)
    f.shade(14, 16, 1.0)


def compte_nomines(f):
    """El compte de les nòmines: un full de llibreta arrencat, amb el marge vermell i el número escrit a mà."""
    S = torn(f.P([(12, 3), (53, 6), (52, 33), (11, 31)]), 't', seed=4, depth=1)
    paper(f, S, PAP_C, 4.4, w=42, h=30)
    for y in range(9, 33, 4):
        for x in range(13, 52):
            if (x, y) in S:
                f.px(x, y, RULE, 1.4)
    for y in range(5, 33):                                               # el marge
        if (14, y) in S:
            f.px(14, y, STAMP, 3.6)
    f.text(16, 10, 'ES76', INKB, 1.4)
    f.text(16, 18, '2100', INKB, 1.4)
    f.text(33, 18, '48', INKB, 1.4)
    f.text(16, 26, '0099', INKB, 1.4)
    f.text(33, 26, '!', STAMP, 2.0)
    f.text(36, 26, '!', STAMP, 2.0)
    f.scrib(16, 45, 32, INKB, 1.6, seed=6, dens=1.0, tall=0)
    f.scrib(17, 44, 33, INKB, 1.6, seed=7, dens=1.0, tall=0)
    f.fill(f.P([(44, 4), (53, 6), (51, 13)]), PAP_C, 2.6, rim=(0.4, -1.0))


def galleda(f):
    """La galleda blava de fregar: un tronc de con amb nervadures, la nansa d'acer i l'escorredor groc."""
    S = f.P([(15, 11), (49, 11), (45, 33), (19, 33)])
    f.drop(S)
    f.fill(S, BUCKET, lambda x, y: 3.6 + 1.6 * math.cos((x - 25) / 14) - 1.0 - (y - 11) * 0.025, rim=(0.6, -1.4))
    f.fill(f.E(32, 11, 18, 3.4), BUCKET, 4.4, rim=(0.6, -0.8))
    f.fill(f.E(32, 11, 15.3, 2.1), BUCKET, 1.4, rim=None)
    f.fill(f.E(32, 11.5, 12, 1.2), CYAN, 2.4, rim=None)                 # l'aigua bruta, a dins
    for y in (16, 28):
        f.rect(17, y, 47, y, BUCKET, 2.4)
        f.rect(17, y + 1, 47, y + 1, BUCKET, 4.0)
    for i in range(39):
        x = 13 + i
        y = round(11 - 8 * math.sin(math.pi * i / 38))
        f.px(x, y, ACER, 4.4 if i < 19 else 3.2)
    f.dots([(13, 11), (51, 11)], ACER, 2.4)
    f.rect(42, 5, 53, 9, PLAST, 3.4, rim=(0.6, -1.0))
    f.rect(43, 6, 52, 8, WARNY, 3.6)
    for x in range(44, 52, 2):
        f.px(x, 7, WARNY, 2.4)


def cartell(f):
    """El cartell de «Neteja en curs», plegat: dues ales grogues en forma de A, amb el ninot que rellisca."""
    L = f.P([(11, 32), (27, 4), (32, 4), (21, 32)])
    f.fill(L, WARNY, lambda x, y: 2.6 - (y - 4) * 0.015, rim=(0.4, -1.0))
    S = f.P([(20, 33), (31, 3), (44, 3), (57, 33)])
    f.drop(S)
    f.fill(S, WARNY, lambda x, y: 4.4 - (x - 21) * 0.025, rim=(0.8, -1.4))
    f.rect(31, 1, 44, 3, PLAST, 2.6, rim=(0.6, -0.8))
    f.fill(f.E(41, 9, 2.1, 2.1), DARK, 1.0, rim=None)
    for a, b in (((40, 12), (36, 19)), ((36, 19), (41, 23)), ((41, 23), (45, 20)), ((36, 19), (31, 23)),
                 ((39, 15), (45, 13)), ((39, 15), (33, 13))):
        f.line(a[0], a[1], b[0], b[1], DARK, 1.0)
    f.line(37, 13, 37, 19, DARK, 1.0)                                    # el cos, més gruixut
    f.rect(28, 25, 49, 25, DARK, 1.2)
    f.dots([(30, 27), (35, 27), (41, 27), (46, 27), (33, 28), (44, 28), (38, 29)], CYAN, 3.0)


def extintor(f):
    """L'extintor vermell, ajagut: el cos, l'etiqueta, el manòmetre, la vàlvula amb la maneta i la mànega."""
    f.drop(f.R(11, 11, 49, 28))
    f.hcyl(13, 48, 19.5, 8.6, FIRE, 3.0, amp=2.6, spec=1.6)
    f.fill(f.E(12, 19.5, 3.2, 8.6), FIRE, 2.0, rim=None)
    f.fill(f.E(49, 19.5, 2.7, 8.4), FIRE, 3.4, rim=None)
    f.rect(22, 13, 36, 24, CARDW, 4.2, rim=(0.4, -0.8))
    f.rect(23, 14, 35, 16, FIRE, 3.0)
    f.dots([(25 + i, 19) for i in range(0, 10, 2)] + [(25 + i, 21) for i in range(0, 8, 2)] +
           [(25 + i, 23) for i in range(0, 6, 2)], INKG, 1.4)
    f.hcyl(52, 57, 19.5, 3.2, ACER, 4.0)
    S = f.E(54, 11, 2.6, 2.6)                                            # el manòmetre
    f.fill(S, ACER, 4.0, rim=(0.6, -1.0))
    f.fill(f.E(54, 11, 1.6, 1.6), CARDW, 4.6, rim=None)
    f.px(55, 10, RED, 3.0)
    f.rect(53, 12, 62, 13, ACER, 4.4, rim=(0.6, -1.0))
    f.px(60, 14, ACER, 2.4)
    f.dots([(56, 16), (57, 16)], SUNY, 4.4)
    for i in range(22):
        f.px(56 - i, 27 + round(math.sin(i / 4) * 2), DARK, 2.6)
        f.px(56 - i, 28 + round(math.sin(i / 4) * 2), DARK, 1.6)
    f.rect(33, 28, 35, 30, DARK, 3.0)                                    # el broquet


def clau_llibre(f):
    """La clau del Llibre Major: grossa, antiga, de llautó, amb l'ull treballat i la cadena del collaret."""
    for i in range(14):
        x, y = 4 + i * 1.7, 4 + round(math.sin(i / 2.4) * 2.4) + i * 0.5
        f.ring(x, y, 1.5, 1.2, BRASS, 4.0 if i % 2 else 2.8, th=0.8)
    S = f.E(19, 19, 8.6, 8.6)
    f.drop(S)
    f.fill(S, GOLDK, lambda x, y: 4.4 - (x - 11) * 0.1 - (y - 11) * 0.1, rim=(0.8, -1.2))
    f.fill(f.E(19, 19, 4.6, 4.6), DARK, 0.4, rim=None)
    f.fill(f.E(19, 19, 1.8, 1.8), GOLDK, 3.6, rim=None)
    for (x, y) in ((19, 14), (19, 15), (14, 19), (15, 19), (23, 19), (24, 19), (19, 23), (19, 24)):
        f.px(x, y, GOLDK, 2.4)
    for a in range(0, 360, 45):                                          # el gravat de la vora
        f.px(round(19 + 6.8 * math.cos(math.radians(a))), round(19 + 6.8 * math.sin(math.radians(a))), GOLDK, 2.4)
    S = f.R(27, 16, 59, 22)
    f.drop(S)
    f.hcyl(27, 59, 19, 3.2, GOLDK, 3.4)
    f.rect(28, 15, 31, 23, GOLDK, 3.0, rim=(0.6, -1.0))
    f.rect(33, 16, 33, 22, GOLDK, 2.4)
    S = f.R(48, 23, 59, 32)
    f.drop(S)
    f.fill(S, GOLDK, lambda x, y: 3.6 - (y - 23) * 0.08, rim=(0.6, -1.2))
    for (x, y) in ((51, 25), (51, 26), (51, 27), (55, 29), (55, 30), (55, 31), (58, 25), (58, 26)):
        f.px(x, y, DARK, 0.6)


def clauer(f):
    """El clauer turístic «Visiteu Ginebra»: una anella sense cap clau i una placa d'esmalt amb la creu suïssa."""
    f.ring(13, 15, 8, 8, ACER, 4.2, th=1.8)
    f.limb((20, 19), (25, 20), 1.0, 1.0, ACER, 3.4, amp=1.4)
    S = f.R(25, 6, 63, 31)
    f.drop(S)
    f.fill(S, NAVY, lambda x, y: 3.2 - (y - 6) * 0.03, rim=(0.8, -1.2))
    f.fill(f.E(27, 9, 1.0, 1.0), DARK, 0.6, rim=None)                    # el forat de la cadeneta
    f.rect(27, 7, 61, 7, SUNY, 3.6)
    f.rect(27, 30, 61, 30, SUNY, 2.8)
    f.rect(26, 8, 26, 29, SUNY, 3.2)
    f.rect(62, 8, 62, 29, SUNY, 2.4)
    x = 29
    for ch in 'GINEBRA':
        x = f.text(x, 10, ch, CARDW, 5.0, font=FONT46, sp=0) + 1
    S = f.R(39, 18, 49, 28)
    f.fill(S, RED, 3.6, rim=(0.6, -0.8))
    f.rect(43, 20, 45, 26, CARDW, 5.0)
    f.rect(41, 22, 47, 24, CARDW, 5.0)
    f.shade(27, 9, 1.6)
    f.shade(28, 10, 1.0)


ICONS = {fn.__name__: fn for fn in (
    caixa_cartro, cable_alimentacio, pizza, auricular, auriculars_boto,
    cable_xarxa, entrepa, clau_casa, tap, recepta, comandament, maleti, ulleres, acreditacions, acreditacio,
    entrepa_suis, entrepa_ballester, targeta, compte_nomines, galleda, cartell, extintor, clau_llibre, clauer,
)}
ICONS['auriculars'] = auricular   # l'objecte de l'Iri es diu «auriculars»


def render(item_id):
    """Imatge RGBA de 65×36 de l'objecte, o None si no en té."""
    fn = ICONS.get(item_id)
    if fn is None:
        return None
    f = Ic640()
    fn(f)
    return f.render()
