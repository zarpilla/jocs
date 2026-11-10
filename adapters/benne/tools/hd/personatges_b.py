"""
Proposta B: personatges de Suma Zero **sense caricatura**, amb les proporcions i el dibuix de Ferro-9
(hd/characters.py: volum, llum i trama). Una persona fa ≈83 px; fotograma de 49×87, peus a (25, 83).
To urbà, de hacker i d'espies: colors apagats (grafit, negre, texà fosc) i un sol accent fort per
personatge (els auriculars vermells de l'Iri).
"""
import math

from hd.characters import (Fig, M, person, hair_lvl, front_normal, fold, SKIN_IRI, SNEAKER, BELT, HAIR_IRI)

# ─── Materials ─────────────────────────────────────────────────────────────
HOODIE = M((10, 12, 18), (20, 24, 32), (32, 38, 48), (46, 54, 66), (64, 74, 88), (88, 100, 114), (118, 130, 142), dith=0.0)
JEANS_BLACK = M((8, 8, 14), (16, 16, 24), (26, 26, 36), (38, 40, 52), (54, 58, 72), (76, 80, 94), dith=0.0)
PHONES = M((8, 8, 12), (18, 18, 24), (30, 30, 38), (46, 46, 56), (66, 66, 78))
PHONES_RED = M((50, 6, 14), (110, 16, 26), (170, 30, 36), (220, 60, 54), (250, 120, 100))
CORD = M((120, 120, 128), (170, 170, 176), (220, 220, 222), (250, 250, 250))
HAIR_SHORT = HAIR_IRI


# ─── Iri: ganxos sobre la persona de Ferro-9 ───────────────────────────────

def iri_hair(fg, p, spec):
    """Cabell negre curt i esbullat, amb un serrell que li cau als ulls."""
    hx, hy = p.head
    H = HAIR_SHORT
    tex = hair_lvl(hx - 0.5, hy - 2.0, 5.4, k=1.1, strands=0.5, freq=2.3)
    if p.f == 'D':
        line = lambda x, y: y <= hy - 3.0 + ((x - hx) / 6.6) ** 2 * 5.5 + (1.4 if int(x) % 3 == 0 else 0)
        fg.ell(hx, hy - 1.2, 7.6, 7.6, H, 1.8, amp=1.6, clip=line, lvlfn=tex)
        for sx, sy in ((-6.4, -6.4), (-2.5, -8.6), (2.6, -8.4), (6.0, -6.6)):       # puntes
            fg.ell(hx + sx, hy + sy, 1.6, 1.4, H, 2.0, amp=1.4)
        fg.ell(hx + 2.2, hy - 3.2, 2.6, 1.6, H, 2.2, amp=1.2)                      # floc del serrell
    elif p.f == 'L':
        line = lambda x, y: (x >= hx - 3.8 + max(0, y - (hy - 5)) * 0.3 or y <= hy - 4.8) and not (x < hx + 2.5 and y > hy - 1.5)
        fg.ell(hx + 1.4, hy - 1.0, 7.4, 7.8, H, 1.8, amp=1.6, clip=line, lvlfn=tex)
        for sx, sy in ((-4.0, -7.4), (0.5, -8.6), (4.8, -7.0), (7.4, -3.0)):
            fg.ell(hx + sx, hy + sy, 1.6, 1.4, H, 2.0, amp=1.4)
        fg.ell(hx - 4.6, hy - 3.2, 1.8, 1.4, H, 2.2, amp=1.2)
    else:
        fg.ell(hx, hy - 0.6, 7.6, 8.2, H, 1.8, amp=1.6, lvlfn=tex)
        for sx, sy in ((-6.0, -6.4), (-2.0, -8.6), (3.0, -8.2), (6.4, -5.2)):
            fg.ell(hx + sx, hy + sy, 1.6, 1.4, H, 2.0, amp=1.4)


def iri_hoodie(fg, p, spec):
    """Dessuadora ampla de grafit: butxaca de cangur, cordons blancs i la caputxa al clatell."""
    b = p.bob
    hx = 24.5
    O = HOODIE
    if p.f == 'D':
        for x in range(int(hx - 6), int(hx + 7)):                                 # butxaca
            fg.shade(x, 38 + b, -1.0, O)
        for y in range(38 + b, 46 + b):
            fg.shade(hx - 6, y, -0.9, O)
            fg.shade(hx + 6, y, -0.9, O)
        for y in range(29 + b, 36 + b):                                            # cordons
            fg.px(hx - 2, y, CORD, 2 if y < 34 + b else 1)
            fg.px(hx + 2, y, CORD, 2 if y < 35 + b else 1)
        for x in range(int(hx - 9), int(hx + 10)):                                 # cintura elàstica
            fg.shade(x, 46 + b, -1.0, O)
            fg.shade(x, 47 + b, 0.4, O)
        fg.shade(hx - 7, 33 + b, -0.6, O)
        fg.shade(hx + 7, 34 + b, -0.6, O)
    elif p.f == 'U':
        fg.ell(hx, 31 + b, 6.0, 4.6, O, 2.4, amp=1.6, cont=(0.2, 1.0))            # caputxa caiguda
        for x in range(int(hx - 4), int(hx + 5)):
            fg.shade(x, 33 + b, -0.8, O)
        for x in range(int(hx - 9), int(hx + 10)):
            fg.shade(x, 46 + b, -1.0, O)
    else:
        fg.ell(29.0, 30 + b, 3.6, 4.0, O, 2.4, amp=1.6, cont=(0.2, 1.0))          # caputxa al clatell
        for y in range(29 + b, 35 + b):
            fg.px(21.0, y, CORD, 2 if y < 33 + b else 1)
        for x in range(19, 33):
            fg.shade(x, 46 + b, -1.0, O)


def iri_collar(fg, p, spec):
    """El coll de la caputxa, que tapa el coll (davant)."""
    if p.f == 'D':
        b = p.bob
        fg.ell(24.5, 28.2 + b, 6.4, 2.4, HOODIE, 2.8, amp=1.4, cont=(0.2, 1.0))


def iri_phones(fg, p, spec):
    """Auriculars grossos, negres i vermells: no se'ls treu mai."""
    hx, hy = p.head
    if p.f in ('D', 'U'):
        for i in range(17):
            a = math.pi * i / 16
            fg.px(hx - math.cos(a) * 8.6, hy - 0.5 - math.sin(a) * 9.2, PHONES, 2.4)
            fg.px(hx - math.cos(a) * 8.6, hy + 0.5 - math.sin(a) * 9.2, PHONES, 1.2)
        for sx in (-8.4, 8.4):
            fg.ell(hx + sx, hy + 1.2, 2.4, 3.4, PHONES, 2.2, amp=1.6, cont=(0.2, 1.0))
            fg.ell(hx + sx + (0.6 if sx < 0 else -0.6), hy + 1.2, 1.2, 2.4, PHONES_RED, 2.6, amp=1.4)
    else:
        for i in range(12):
            a = math.pi * (0.2 + 0.6 * i / 11)
            fg.px(hx + 1.4 + math.cos(a) * 2.5, hy - 0.5 - math.sin(a) * 9.2, PHONES, 2.4)
        fg.ell(hx + 1.6, hy + 1.2, 3.0, 3.8, PHONES, 2.2, amp=1.6, cont=(0.2, 1.0))
        fg.ell(hx + 1.2, hy + 1.2, 1.8, 2.8, PHONES_RED, 2.6, amp=1.4)


IRI = {
    'skin': SKIN_IRI, 'legs': JEANS_BLACK, 'top': HOODIE, 'shoes': SNEAKER, 'shoe_lvl': 3.4, 'lashes': True,
    'iris': (52, 38, 30), 'brow': (24, 16, 22), 'stoop': 1,
    'hooks': {'hair': iri_hair, 'torso': iri_hoodie, 'collar': iri_collar, 'over': None},
}


def iri(facing, walk=None, talk=False):
    spec = dict(IRI)
    hooks = dict(spec['hooks'])
    hair = hooks['hair']

    def hair_and_phones(fg, p, s):
        hair(fg, p, s)
        iri_phones(fg, p, s)
    hooks['hair'] = hair_and_phones
    del hooks['over']
    spec['hooks'] = hooks
    return person(spec, facing, walk=walk, talk=talk)


# ─── Diu, el gat (amb volum) ───────────────────────────────────────────────

CAT = M((14, 12, 16), (34, 30, 34), (58, 52, 54), (86, 78, 76), (116, 106, 100), (150, 140, 128))
CAT_WHITE = M((70, 66, 74), (130, 126, 128), (182, 178, 172), (220, 216, 206), (244, 240, 230))
CAT_EYE = M((20, 40, 10), (90, 130, 30), (160, 200, 60), (220, 240, 130))
GW, GH = 30, 26


def diu(cua=0, parpelleja=False):
    """Assegut de tres quarts, tigrat i amb el pitet blanc. Fotograma de 30×26."""
    fg = Fig(GW, GH)
    tx = [24, 26, 27, 26][cua % 4]
    fg.limb((19, 22), (tx, 14), 1.4, 1.2, CAT, 2.2, cont=(0.2, 0.8))
    fg.limb((tx, 14), (tx - 1, 10), 1.2, 1.1, CAT, 2.4, cont=(0.2, 0.8))
    fg.ell(14, 18, 7.5, 6.5, CAT, 2.6, amp=1.6, cont=(0.2, 1.0),
           lvlfn=lambda x, y: -0.8 if (int(x) + int(y) // 2) % 4 == 0 else 0)
    fg.ell(12, 19, 3.2, 4.4, CAT_WHITE, 2.8, amp=1.4)
    fg.ell(10, 24, 2.4, 1.4, CAT_WHITE, 2.8, amp=1.2)
    fg.ell(15, 24, 2.4, 1.4, CAT_WHITE, 2.4, amp=1.2)
    fg.ell(12, 9, 5.6, 5.0, CAT, 2.8, amp=1.6, cont=(0.2, 1.0),
           lvlfn=lambda x, y: -0.8 if int(y) in (5, 6) and int(x) % 3 == 0 else 0)
    fg.poly([(7, 6), (8, 1), (11, 4)], CAT, 2.6)
    fg.poly([(17, 6), (16, 1), (13, 4)], CAT, 2.2)
    fg.ell(12, 11.5, 2.4, 1.6, CAT_WHITE, 3.0, amp=1.0)
    for ex in (9.5, 14.5):
        if parpelleja:
            fg.px(ex - 1, 9, CAT, 0); fg.px(ex, 9, CAT, 0); fg.px(ex + 1, 9, CAT, 0)
        else:
            fg.ell(ex, 9, 1.4, 1.3, CAT_EYE, 2.6, amp=1.0)
            fg.px(ex, 9, CAT, 0)
    fg.px(12, 11, (190, 110, 120), 0)
    return fg.render()
