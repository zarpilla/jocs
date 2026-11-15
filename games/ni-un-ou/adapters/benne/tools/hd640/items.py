"""
Icones d'inventari per a la prova de 640×360: els mateixos 14 objectes de hd/items.py, redibuixats a la
casella nova (65×36 en lloc de 49×27) amb el mateix sistema (Ic de hd/items.py: volum, rampes per material,
contorn fosc selectiu) i aprofitant els píxels de més (etiquetes, cargols, reflexos, textures).

No toca hd/items.py: en reaprofita els materials i les eines i només canvia la mida del llenç.
Ho fa servir hd640/draw_items.py.
"""
import math

from hd.characters import Fig
from hd.pix import hr
from hd.items import (Ic, paper, FONT, M, PAP_W, PAP_C, PAP_O, GRAPH, INKB, INKG, STAMP, RULE, CORPG, SUNY, ACER,
                      IRON, STEEL, CLOTH, DARK, BLK, LCD, LED, BLUEC, LOGB, GRIP, WIRE, CABLE, USBB, GOLDK, REDP,
                      BAG, MUD, JAR, PAPV, CROSS, WOOD)

W, H = 65, 36

PINKE = M((70, 26, 40), (130, 56, 72), (190, 96, 108), (230, 140, 146), (250, 190, 190))   # goma d'esborrar
# Lletres de 4×6, per a les etiquetes que ara hi caben
FONT46 = {
    '7': ('####', '...#', '..#.', '..#.', '.#..', '.#..'),
    'C': ('.###', '#...', '#...', '#...', '#...', '.###'),
    'H': ('#..#', '#..#', '####', '#..#', '#..#', '#..#'),
    '9': ('.##.', '#..#', '.###', '...#', '..#.', '.#..'),
}


class Ic640(Ic):
    """Llenç d'una icona de 640: el mateix Ic, a 65×36."""

    def __init__(self):
        Fig.__init__(self, W, H)


# ─── Els objectes ───────────────────────────────────────────────────────────

def walkie(f):
    """El walkie: negre, dret, antena de goma, selector de canal moleteat, pantalla verda (CH 9), pilot taronja,
    botó de parlar amb estries, reixeta de l'altaveu i la pinça del cinturó que treu el cap."""
    f.limb((27, 1), (27, 9), 1.6, 1.9, BLK, 3.0, amp=1.6)                  # l'antena
    for y in (3, 5, 7):
        f.shade(27, y, -0.8)
    f.limb((35, 4), (35, 8), 1.7, 1.7, BLK, 3.4, amp=1.6)                  # el selector de canal
    for y in (5, 7):
        f.px(34, y, BLK, 5.0)
    S = f.P([(23, 9), (42, 9), (42, 34), (23, 34)]) - {(23, 9), (24, 9), (23, 10), (42, 9), (41, 9), (42, 10),
                                                       (23, 34), (42, 34)}
    f.drop(S)
    f.fill(S, BLK, lambda x, y: 3.4 - (x - 23) * 0.06 - (y - 9) * 0.03, rim=(0.8, -1.2))
    f.rect(43, 13, 43, 26, BLK, 1.6)                                       # la pinça, de cantó
    f.rect(21, 14, 22, 24, BLK, 2.2, rim=(0.6, -0.8))                      # el botó de parlar, amb estries
    for y in (16, 19, 22):
        f.rect(21, y, 22, y, BLK, 1.0)
    f.rect(25, 12, 40, 20, BLK, 1.0)                                       # la pantalla: canal 9
    f.rect(26, 13, 39, 19, LCD, lambda x, y: 3.2 - (y - 13) * 0.2)
    f.text(27, 14, 'CH', LCD, 0.4, sp=1)
    f.text(35, 14, '9', LCD, 0.4)
    f.px(26, 13, LCD, 4.6)                                                 # el reflex del vidre
    f.px(27, 13, LCD, 4.2)
    f.px(39, 10, LED, 3.4)                                                 # el pilot
    f.px(40, 10, LED, 2.4)
    for y in range(23, 32, 2):                                             # la reixeta
        for x in range(27, 39):
            f.px(x, y, BLK, 0.8 if (x + y // 2) % 2 else 1.4)
        f.rect(27, y + 1, 38, y + 1, BLK, 4.0)
    for (x, y) in ((25, 32), (40, 32)):                                    # cargols
        f.px(x, y, ACER, 4.0)


def quadern(f):
    """El quadern on apunten el que saben: tapes blaves amb cantoneres, l'etiqueta escrita, la goma vermella i la
    cinta del punt de llibre que surt per sota."""
    S = f.R(19, 4, 45, 32)
    f.drop(S, -1.6, 2, 1)
    f.fill(S, BLUEC, lambda x, y: 3.6 - (x - 19) * 0.03 - (y - 4) * 0.03, rim=(0.8, -1.4))
    f.rect(19, 4, 22, 32, BLUEC, 2.0)                                      # el llom
    for y in (8, 28):
        f.rect(19, y, 22, y, BLUEC, 3.2)
    f.rect(46, 5, 46, 32, PAP_C, 3.2)                                      # el gruix de les fulles
    for y in range(6, 32, 2):
        f.px(46, y, PAP_C, 2.2)
    for (cx, cy) in ((44, 5), (44, 31)):                                   # cantoneres gastades
        f.px(cx, cy, BLUEC, 5.0)
    f.rect(26, 9, 40, 16, PAP_C, 4.4, rim=(0.4, -1.0))                    # l'etiqueta
    f.rect(26, 9, 40, 9, PAP_C, 3.2)
    f.scrib(28, 38, 12, GRAPH, 1.4, seed=4)
    f.scrib(28, 34, 14, GRAPH, 1.6, seed=5, dens=0.7)
    f.rect(41, 3, 41, 33, GRIP, 3.4)                                       # la goma
    f.rect(42, 3, 42, 33, GRIP, 2.0)
    f.rect(31, 33, 32, 35, CROSS, 2.6)                                     # la cinta del punt de llibre
    f.px(31, 35, CROSS, 1.4)


def llibreta(f):
    """La llibreta de màquines, oberta: columnes d'hores i consums amb les ratlles vermelles, el gat d'en Diu
    dibuixat al marge i un llapis amb goma."""
    L = f.P([(5, 9), (32, 7), (32, 32), (7, 33)])
    R = f.P([(32, 7), (59, 9), (57, 33), (32, 32)])
    f.drop(L | R, -1.4, 1, 2)
    f.fill(f.P([(4, 10), (32, 8), (60, 10), (59, 35), (32, 33), (5, 35)]), LOGB, 2.4, rim=(0.6, -1.0))
    f.fill(L, PAP_C, lambda x, y: 4.0 - (x - 5) * 0.015, rim=None)
    f.fill(R, PAP_C, lambda x, y: 3.6 + (x - 32) * 0.015, rim=None)
    for x in range(29, 33):                                                # el plec del mig
        for y in range(7, 33):
            f.shade(x, y, -0.9 + (x - 29) * 0.2)
    for x in range(33, 35):
        for y in range(7, 33):
            f.shade(x, y, -0.4)
    f.rect(8, 12, 27, 12, INKG, 2.0)                                       # capçalera de la pàgina
    for y in range(15, 31, 3):                                             # les columnes de xifres
        f.scrib(8, 15, y, INKB, 1.6, seed=y, dens=0.9, tall=0)
        f.scrib(20, 27, y, INKB, 1.6, seed=y + 9, dens=0.9, tall=0)
    for y in range(13, 32, 3):
        f.rect(36, y, 55, y, RULE, 1.4)
    for x in (18, 45):
        f.rect(x, 12, x, 31, STAMP, 2.0)                                   # les ratlles de columna
    for (x, y) in ((38, 15), (39, 14), (40, 15), (41, 14), (38, 16), (41, 16), (39, 17), (40, 17),   # el gat
                   (42, 17), (43, 16), (44, 15)):
        f.px(x, y, GRAPH, 1.2)
    f.scrib(36, 52, 22, GRAPH, 1.2, seed=7, dens=0.6)
    f.limb((37, 29), (57, 19), 1.2, 1.2, SUNY, 3.4, amp=1.4)              # el llapis
    f.px(37, 29, GRAPH, 1.0)
    f.px(38, 29, (200, 160, 110), 0)
    f.limb((57, 19), (59, 18), 1.2, 1.2, ACER, 4.2, amp=1.4)               # el capçal i la goma
    f.limb((60, 18), (61, 17), 1.2, 1.2, PINKE, 3.0, amp=1.4)


def cisalla(f):
    """La cisalla: mànecs de goma vermella amb estries, braços d'acer, el cap amb el cargol del pivot i les fulles
    curtes amb el tall esmolat."""
    for (a, b) in (((4, 25), (21, 17)), ((7, 33), (24, 25))):              # mànecs
        f.limb(a, b, 2.2, 2.0, GRIP, 3.0, amp=2.0)
        for t in (0.25, 0.45, 0.65):
            x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            f.shade(x, y - 1, -1.0)
            f.shade(x, y, -1.0)
    for (a, b) in (((21, 17), (41, 12)), ((24, 25), (41, 17))):            # braços
        f.limb(a, b, 1.6, 1.5, ACER, 4.4, amp=2.2)
    for (x, y) in ((22, 17), (25, 25)):                                    # virolles
        f.px(x, y, ACER, 6.0)
    S = f.E(43, 15, 4.8, 4.5)                                              # el cap
    f.drop(S)
    f.fill(S, ACER, lambda x, y: 4.6 - (x - 38) * 0.15 - (y - 10) * 0.15, rim=(0.8, -1.4))
    f.fill(f.E(43, 15, 1.6, 1.6), ACER, 6.0, rim=(0.4, -1.2))              # el cargol del pivot
    f.px(42, 15, ACER, 1.6)
    f.px(44, 15, ACER, 1.6)
    f.px(41, 12, ACER, 2.0)                                                # cargol d'ajust
    f.px(45, 18, ACER, 2.0)
    f.fill(f.P([(46, 11), (61, 7), (61, 9), (47, 14)]), ACER, 6.0, rim=(0.6, -1.2))   # les fulles
    f.fill(f.P([(47, 16), (61, 11), (61, 13), (47, 19)]), ACER, 4.4, rim=(0.4, -1.2))
    for x in range(50, 61, 3):                                             # el tall esmolat
        f.px(x, 10 - (x - 50) * 0.25, ACER, 7.4)


def maceta(f):
    """La maceta de goma de l'Iri: mànec de fusta amb dues voltes de cinta groga i el cap de goma negra."""
    f.limb((5, 31), (41, 17), 2.0, 2.4, WOOD, 4.2, amp=2.0)               # el mànec
    for t in (0.18, 0.3):                                                  # la cinta del puny
        x, y = 5 + 36 * t, 31 - 14 * t
        for k in (-1, 0, 1):
            f.px(x, y + k, SUNY, 3.4)
    f.fill(f.E(6, 31, 1.0, 1.0), DARK, 0.6, rim=None)                     # el forat del cordill
    S = f.P([(37, 7), (47, 3), (55, 23), (45, 27)])                       # el cap
    f.drop(S)
    f.fill(S, BLK, lambda x, y: 3.6 - (x - 37) * 0.08 - (y - 3) * 0.04, rim=(0.8, -1.4))
    for (a, b) in (((39, 8), (46, 5)), ((46, 25), (53, 22))):              # les cares de picar
        f.limb(a, b, 0.6, 0.6, BLK, 4.8, amp=0.6)
    for y in range(8, 22, 3):                                              # el reflex de la goma
        f.px(45 + (y - 8) * 0.38, y, BLK, 5.4)


def travesser(f):
    """El travesser de la llitera: tub d'acer amb els caps aixafats i foradats, ratlles de desgast i un cargol."""
    f.limb((9, 26), (55, 11), 3.2, 3.2, STEEL, 4.0, amp=2.6)
    for (cx, cy) in ((8, 27), (56, 10)):                                   # caps aixafats
        S = f.E(cx, cy, 4.5, 3.4)
        f.fill(S, STEEL, lambda x, y, cy=cy: 4.6 - (y - cy) * 0.35, rim=(0.8, -1.2))
        f.fill(f.E(cx, cy, 1.4, 1.4), DARK, 0.6, rim=None)
        f.px(cx - 1, cy - 1, STEEL, 2.0)
    for t in (0.22, 0.4, 0.62, 0.8):                                       # ratlletes de desgast
        x, y = 9 + 46 * t, 26 - 15 * t
        f.shade(x, y - 1.6, 1.4)
        f.shade(x + 1, y - 1.9, 1.0)
    f.px(30, 18, (120, 70, 40), 0)                                         # un punt de rovell
    f.px(31, 18, (90, 50, 30), 0)


def tram(f):
    """Un tram de cable de malla d'acer: trenat, amb dos talls nets (les fibres a la vista) i l'osca de la cisalla."""
    pts = [(7, 23), (19, 17), (32, 19), (45, 16), (57, 11)]
    for p0, p1 in zip(pts, pts[1:]):
        f.limb(p0, p1, 3.4, 3.4, WIRE, 3.6, amp=2.4)
    for i in range(80):                                                    # el trenat
        t = i / 79
        k = min(int(t * 4), 3)
        u = t * 4 - k
        (x0, y0), (x1, y1) = pts[k], pts[k + 1]
        x, y = x0 + (x1 - x0) * u, y0 + (y1 - y0) * u
        if i % 3 == 0:
            for d in (-3, -2, -1, 0, 1, 2, 3):
                f.shade(x + d * 0.6, y + d, -1.2)
        elif i % 3 == 1:
            f.shade(x - 1, y - 2, 0.8)
    for (cx, cy) in (pts[0], pts[-1]):                                     # els talls: les fibres
        f.fill(f.E(cx, cy, 2.4, 3.4), WIRE, 5.0, rim=None)
        for (dx, dy) in ((0, -2), (0, 0), (0, 2), (-1, -1), (-1, 1)):
            f.px(cx + dx, cy + dy, WIRE, 2.6)
    for (x, y) in ((32, 15), (33, 15), (32, 16)):                         # l'osca
        f.erase(x, y)
    f.px(32, 17, WIRE, 1.2)
    f.px(33, 16, WIRE, 6.0)


def cable_nou(f):
    """Un rotllo de cable apantallat lligat amb una brida, i un connector nou: rosca de llautó i cos d'acer."""
    for k, (cx, cy, rx, ry) in enumerate(((21, 17, 15, 11), (25, 19, 13.5, 9.5))):
        f.ring(cx, cy, rx, ry, CABLE, 3.4 - k * 0.4, th=2.4)
    for i in range(40):                                                    # la llum de dalt de les voltes
        a = math.pi * (1.1 + 0.8 * i / 39)
        f.px(round(21 + 15 * math.cos(a)), round(17 + 11 * math.sin(a)), CABLE, 4.6)
    f.rect(8, 15, 10, 21, LCD, 1.4, rim=(0.4, -0.8))                       # la brida (verda fosca)
    f.limb((36, 24), (45, 20), 1.5, 1.5, CABLE, 3.0, amp=1.6)
    f.hcyl(45, 51, 19, 4.2, GOLDK, 3.4)                                    # la rosca
    for x in range(45, 52, 2):
        for y in range(15, 24):
            f.shade(x, y, -0.8)
    f.hcyl(52, 60, 19, 5.0, ACER, 4.4)                                     # el cos del connector
    for x in (54, 57):
        f.rect(x, 15, x, 23, ACER, 2.6)
    f.rect(61, 16, 61, 22, DARK, 1.0)
    f.px(61, 19, GOLDK, 4.0)                                               # el pin del mig


def usb(f):
    """L'USB amb les dades de la Juana: plàstic blau amb l'anella, l'etiqueta escrita a mà i el connector."""
    f.ring(13, 17, 4.5, 4.5, ACER, 4.6, th=1.5)                            # l'anella
    S = f.P([(17, 11), (44, 11), (47, 13), (47, 23), (44, 25), (17, 25), (16, 23), (16, 13)])
    f.drop(S)
    f.fill(S, USBB, lambda x, y: 3.8 - (y - 11) * 0.15, rim=(0.8, -1.2))
    f.fill(f.E(20, 18, 1.7, 1.7), DARK, 1.0, rim=None)                     # el forat de l'anella
    f.rect(24, 14, 42, 22, PAP_W, 4.2, rim=(0.4, -1.0))                   # l'etiqueta
    f.text(26, 15, 'J', INKB, 1.2)
    f.scrib(30, 40, 17, INKB, 1.6, seed=21)
    f.scrib(26, 37, 20, INKB, 1.6, seed=22, dens=0.7)
    f.rect(17, 12, 43, 12, USBB, 5.0)                                      # el reflex del plàstic
    S = f.R(48, 13, 59, 23)                                                # el connector
    f.drop(S)
    f.fill(S, ACER, lambda x, y: 5.6 - (y - 13) * 0.18, rim=(0.8, -1.4))
    f.rect(52, 15, 54, 16, DARK, 0.6)
    f.rect(52, 20, 54, 20, DARK, 0.6)
    f.rect(48, 23, 59, 23, ACER, 2.6)


def _nota(f, mat, base, seed, head=None):
    """Un paper doblegat per la meitat i mig obert: la meitat de dalt de cara a la llum."""
    top = f.P([(16, 5), (48, 8), (49, 19), (15, 17)])
    bot = f.P([(15, 17), (49, 19), (47, 32), (17, 31)])
    f.drop(top | bot, -1.4, 1, 2)
    f.fill(bot, mat, lambda x, y: base - 0.6 - (y - 17) * 0.04, rim=(0.4, -1.0))
    f.fill(top, mat, lambda x, y: base + 0.4 - (x - 15) * 0.015, rim=(0.6, -1.0))
    for x in range(15, 50):                                                # el plec
        f.shade(x, 17 + (x - 15) / 17, -1.0)
        f.shade(x, 18 + (x - 15) / 17, -0.4)
    if head:
        head()
    ink = GRAPH if mat is PAP_C else INKB
    for y, s in ((10, 0), (12, 1), (14, 2)):
        f.scrib(20, 44, y, ink, 1.4, seed=seed + s)
    for y in (22, 25, 28):
        f.scrib(20, 42, y, ink, 1.6, seed=seed + y, dens=0.7)


def nota_iri(f):
    """El paper de l'Iri: un full de llibreta quadriculada, crema, escrit amb llapis, amb el marge vermell."""
    def head():
        for x in range(18, 48, 3):
            for y in range(7, 31):
                if f.get(x, y) and f.get(x, y)[0] is PAP_C:
                    f.shade(x, y, -0.5)
        for y in range(7, 31, 3):
            for x in range(17, 49):
                if f.get(x, y) and f.get(x, y)[0] is PAP_C:
                    f.shade(x, y, -0.3)
        for y in range(7, 31):
            if f.get(19, y) and f.get(19, y)[0] is PAP_C:
                f.px(19, y, STAMP, 3.4)
    _nota(f, PAP_C, 4.2, 30, head)


def nota_vet(f):
    """El paper de la Vet: un full del receptari, blanc, amb la creu vermella, la capçalera impresa i tinta blava."""
    def head():
        f.fill(f.R(19, 6, 22, 12) - {(19, 6), (22, 6), (19, 12), (22, 12)}, CROSS, 2.6, rim=None)
        f.rect(18, 8, 23, 10, CROSS, 2.6)
        f.rect(26, 8, 44, 8, INKG, 2.0)
        f.rect(26, 10, 38, 10, INKG, 2.6)
    _nota(f, PAPV, 4.4, 50, head)


def clau_tomas(f):
    """La clau antiga d'en Tomàs: llautó amb verdet, l'ull treballat, la tija llarga, el paletó dentat i una etiqueta
    de cartró lligada amb cordill (el que hi deia, esborrat)."""
    S = f.P([(40, 4), (56, 3), (59, 15), (43, 16)])                       # l'etiqueta
    f.drop(S)
    f.fill(S, PAP_O, lambda x, y: 3.6 - (x - 40) * 0.025, rim=(0.6, -1.0))
    f.ring(43, 9, 1.6, 1.6, PAP_O, 2.0, th=0.8)                           # el forat amb l'ullet
    f.fill(f.E(43, 9, 0.8, 0.8), DARK, 1.0, rim=None)
    f.scrib(46, 55, 8, INKG, 3.4, seed=11, dens=0.5)
    f.scrib(46, 53, 11, INKG, 3.6, seed=12, dens=0.4)
    f.line(42, 9, 30, 16, CLOTH, 3.2)                                     # el cordill
    f.line(42, 10, 31, 17, CLOTH, 2.2)
    f.ring(17, 20, 8.6, 8, GOLDK, 3.6, th=2.6)                            # l'ull
    f.fill(f.E(17, 20, 3, 2.7), GOLDK, 4.4, rim=(0.6, -1.0))              # el trèvol del mig
    for (x, y) in ((17, 14), (11, 20), (23, 20), (17, 26)):
        f.fill(f.E(x, y, 1.1, 1.1), GOLDK, 5.0, rim=None)
    f.hcyl(25, 56, 20, 2.1, GOLDK, 3.4)                                   # la tija
    f.rect(26, 17, 28, 23, GOLDK, 3.8, rim=(0.6, -1.0))                   # el coll
    f.rect(30, 18, 30, 22, GOLDK, 2.6)
    S = f.R(48, 23, 57, 30)                                               # el paletó
    f.drop(S)
    f.fill(S, GOLDK, lambda x, y: 3.4 - (y - 23) * 0.08, rim=(0.6, -1.2))
    for (x, y) in ((50, 25), (50, 26), (50, 27), (54, 28), (54, 29), (56, 26)):   # les osques del paletó
        f.px(x, y, DARK, 0.6)
    f.erase(54, 30)
    for (x, y) in ((33, 20), (41, 19), (14, 25), (22, 16), (52, 24)):     # verdet
        f.px(x, y, CORPG, 2.0)
    f.px(34, 20, CORPG, 1.4)


def clau_tubs(f):
    """La clau de tubs: mànec de ferro colat pintat de vermell (amb la pintura saltada), el cos, les mandíbules
    dentades, la femella moleteada i la marca de la mida."""
    f.limb((5, 27), (40, 23), 2.9, 3.7, REDP, 3.0, amp=2.2)               # el mànec
    for (x, y, w) in ((16, 24, 2), (28, 23, 3), (34, 22, 1)):             # pintura saltada
        for i in range(w):
            f.px(x + i, y, IRON, 3.0)
    f.fill(f.E(7, 27, 1.6, 1.3), DARK, 0.6, rim=None)                     # el forat per penjar-la
    S = f.P([(37, 16), (51, 15), (52, 29), (39, 31)])                      # el cos
    f.drop(S)
    f.fill(S, IRON, lambda x, y: 4.0 - (x - 37) * 0.05 - (y - 15) * 0.03, rim=(0.8, -1.4))
    f.text(41, 23, '18', IRON, 1.2, font=FONT)                             # la mida, en relleu
    for x in range(41, 48):
        f.shade(x, 22, 0.8)
    S = f.P([(51, 20), (61, 20), (61, 25), (51, 27)])                      # la mandíbula de baix
    f.drop(S)
    f.fill(S, IRON, 4.2, rim=(0.8, -1.4))
    f.rect(44, 3, 47, 17, ACER, lambda x, y: 4.6 - (x - 44) * 0.6)       # la tija de la mandíbula de dalt
    for y in range(5, 17, 2):
        f.px(47, y, ACER, 2.0)
    S = f.P([(41, 3), (61, 4), (61, 11), (48, 11)])                        # la mandíbula de dalt
    f.drop(S)
    f.fill(S, ACER, lambda x, y: 5.2 - (y - 3) * 0.25, rim=(0.8, -1.4))
    for x in range(50, 62, 2):                                             # les dents
        f.px(x, 11, ACER, 1.6)
        f.px(x, 20, IRON, 1.6)
    S = f.E(45, 14, 4.5, 2.4)                                              # la femella moleteada
    f.fill(S, ACER, 4.0, rim=(0.6, -1.2))
    for x in (42, 44, 46, 48):
        f.px(x, 13, ACER, 2.0)
        f.px(x, 15, ACER, 2.0)


def mostra7(f):
    """La Mostra 7: bossa de proves segellada (tancament vermell, banda d'escriure), i a dins el pot de fang gris
    amb la tapa negra i l'etiqueta del 7."""
    S = f.P([(12, 5), (52, 5), (53, 32), (11, 32)])
    f.drop(S)
    f.fill(S, BAG, lambda x, y: 3.0 + (1.6 if (x - y) % 15 == 0 else 0) - (y - 5) * 0.025, rim=(1.0, -1.0))
    f.rect(12, 6, 52, 8, STAMP, 3.0)                                       # el tancament de pressió
    f.rect(12, 9, 52, 9, BAG, 4.6)
    f.rect(13, 27, 51, 30, PAP_W, 3.6, rim=None)                           # la banda per escriure-hi
    f.scrib(15, 34, 28, INKB, 1.6, seed=71, dens=0.8)
    f.rect(38, 28, 49, 29, STAMP, 2.4)
    J = f.R(20, 13, 38, 26)                                                # el pot de vidre
    f.fill(J, JAR, lambda x, y: 3.0 - (x - 20) * 0.05, rim=(0.8, -1.2))
    f.rect(20, 11, 38, 13, BLK, 3.6, rim=(0.6, -1.0))                      # la tapa, amb estries
    for x in range(21, 38, 2):
        f.px(x, 12, BLK, 2.0)
    f.fill(f.R(21, 19, 37, 25), MUD, lambda x, y: 3.0 - (y - 19) * 0.15 + (hr(x, y, 5) - 0.5) * 0.8, rim=None)
    f.rect(21, 19, 37, 19, MUD, 4.0)                                       # la superfície del fang
    f.rect(21, 20, 37, 20, MUD, 3.4)
    f.rect(22, 14, 23, 25, JAR, 4.6)                                       # el reflex del vidre
    f.px(24, 15, JAR, 4.2)
    S = f.R(41, 13, 50, 25)                                                # l'etiqueta del 7
    f.fill(S, PAP_W, 4.4, rim=(0.4, -1.0))
    f.rect(41, 13, 50, 14, STAMP, 3.0)
    f.text(44, 16, '7', INKB, 1.0, font=FONT46)
    f.rect(42, 23, 49, 23, INKG, 2.0)
    for (x, y) in ((14, 10), (15, 11), (49, 31), (16, 30), (50, 12)):      # brillantor del plàstic
        f.px(x, y, BAG, 5.4)


def registre(f):
    """La pàgina impresa del registre de fundacions: escut, capçalera, el nom en negreta, la taula i la fila de
    «Patró únic: Skarn» subratllada amb retolador groc."""
    S = f.R(19, 2, 45, 34)
    S -= {(45, 2), (44, 2), (45, 3)}
    paper(f, S, PAP_W, 4.4, w=27, h=33)
    f.px(44, 3, PAP_W, 2.6)
    f.fill(f.E(23, 6, 2, 2.2), BLUEC, 3.0, rim=(0.4, -0.8))                 # l'escut del registre
    f.px(23, 6, SUNY, 4.0)
    f.rect(27, 4, 42, 4, INKG, 1.2)
    f.rect(27, 6, 38, 6, INKG, 2.0)
    f.rect(27, 8, 40, 8, INKG, 2.4)
    f.rect(21, 11, 43, 12, INKG, 0.6)                                      # el nom, en negreta
    f.rect(21, 14, 35, 14, INKG, 0.6)
    for y in range(17, 32, 2):                                             # la taula
        f.rect(21, y, 27, y, INKG, 2.2)
        f.rect(30, y, 43, y, INKG, 2.2 if y != 25 else 0.4)
    f.rect(28, 16, 28, 32, INKG, 3.0)
    f.rect(21, 16, 43, 16, INKG, 3.0)
    f.rect(30, 24, 43, 26, SUNY, lambda x, y: 3.4 - (y - 24) * 0.3)        # «Patró únic: Skarn», en groc
    f.rect(30, 25, 41, 25, INKG, 0.4)


SEAGP = M((12, 38, 26), (24, 70, 48), (40, 108, 74), (70, 148, 102), (124, 196, 152))      # el verd del plànol


def mapa(f):
    """El plànol d'emergència, plastificat (el de la paret del passadís): capçalera verda, les tres cobertes de
    l'Arenga vistes de dalt, la ruta d'evacuació en verd, el punt vermell i un reflex del plàstic."""
    S = f.R(11, 5, 53, 31)
    paper(f, S, PAPV, 4.4, w=43, h=27)
    f.rect(12, 6, 52, 9, SEAGP, 2.6)                                       # la capçalera
    f.rect(22, 7, 42, 8, PAPV, 4.8)                                        # el títol, en blanc
    for y0, y1, x1 in ((11, 14, 40), (16, 21, 48), (23, 28, 46)):          # les tres cobertes (casc i proa)
        f.rect(14, y0, x1, y0, INKG, 1.0)
        f.rect(14, y1, x1, y1, INKG, 1.0)
        f.rect(14, y0, 14, y1, INKG, 1.0)
        for y in range(y0, y1 + 1):                                        # la proa, en punta
            d = abs(y - (y0 + y1) / 2)
            f.px(x1 + round(((y1 - y0) / 2 - d) * 1.4), y, INKG, 1.0)
    for x in (20, 26, 33):                                                 # envans
        f.rect(x, 17, x, 20, INKG, 2.0)
        f.rect(x, 24, x, 27, INKG, 2.0)
    for x in range(16, 46, 3):                                             # la ruta d'evacuació
        f.px(x, 19, SEAGP, 3.2)
        f.px(x + 1, 19, SEAGP, 3.2)
    f.rect(28, 17, 29, 18, REDP, 4.0)                                      # «sou aquí»
    for i in range(9):                                                     # el reflex del plàstic
        f.shade(40 + i, 30 - i * 3, 1.2)
        f.shade(41 + i, 30 - i * 3, 0.8)


ICONS = {fn.__name__: fn for fn in (
    walkie, quadern, llibreta, maceta, cisalla, travesser, tram, cable_nou, usb, nota_iri, nota_vet,
    clau_tomas, clau_tubs, mostra7, registre, mapa,
)}


def render(item_id):
    """Imatge RGBA de 65×36 de l'objecte, o None si no en té."""
    fn = ICONS.get(item_id)
    if fn is None:
        return None
    f = Ic640()
    fn(f)
    return f.render()
