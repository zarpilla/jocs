"""
Proposta B: personatges de Suma Zero **sense caricatura**, amb les proporcions i el dibuix de Ferro-9
(hd/characters.py: volum, llum i trama). Una persona fa ≈83 px; fotograma de 49×87, peus a (25, 83).
To urbà, de hacker i d'espies: colors apagats i un accent fort per personatge. L'Iri: dessuadora verd
petroli amb «</>» al pit, texans negres, auriculars vermells i cabell negre recollit en una cua.
"""
import math

from hd.characters import (Fig, M, Pose, person, hair_lvl, front_normal, fold, SKIN_IRI, SNEAKER, BELT, HAIR_IRI)

# ─── Materials ─────────────────────────────────────────────────────────────
HOODIE = M((6, 20, 24), (12, 36, 40), (20, 56, 58), (30, 80, 80), (46, 106, 102), (70, 136, 126), (106, 170, 156), dith=0.0)
JEANS_BLACK = M((8, 8, 14), (16, 16, 24), (26, 26, 36), (38, 40, 52), (54, 58, 72), (76, 80, 94), dith=0.0)
PHONES = M((8, 8, 12), (18, 18, 24), (30, 30, 38), (46, 46, 56), (66, 66, 78))
PHONES_RED = M((50, 6, 14), (110, 16, 26), (170, 30, 36), (220, 60, 54), (250, 120, 100))
CORD = M((120, 120, 128), (170, 170, 176), (220, 220, 222), (250, 250, 250))
HAIR_SHORT = HAIR_IRI
SCRUNCHIE = PHONES_RED


# ─── Iri: ganxos sobre la persona de Ferro-9 ───────────────────────────────

def ponytail(fg, p, pts, H):
    """Cua: segments que s'aprimen al llarg d'una corba, amb la goma vermella a dalt."""
    n = len(pts)
    for i, ((x0, y0), (x1, y1)) in enumerate(zip(pts, pts[1:])):
        r0, r1 = 2.4 - i * 1.6 / n, 2.4 - (i + 1) * 1.6 / n
        fg.limb((x0, y0), (x1, y1), r0, r1, H, 2.0, amp=1.6, cont=(0.2, 1.0),
                lvlfn=lambda x, y: 0.4 * math.sin(x * 2.0 + y * 0.6))
    x, y = pts[0]
    fg.ell(x, y, 1.8, 1.4, SCRUNCHIE, 2.6, amp=1.2)


def iri_hair_back(fg, p, spec):
    """La cua, darrere del cap (de cara i de perfil)."""
    hx, hy = p.head
    sway = 0.0 if p.walk is None else math.sin(2 * math.pi * p.walk / 6) * 1.2
    if p.f == 'D':
        ponytail(fg, p, [(hx + 5.0, hy - 5.5), (hx + 8.4, hy - 2.0), (hx + 9.2 + sway * 0.3, hy + 3.0), (hx + 8.4 + sway * 0.6, hy + 8.0)], HAIR_SHORT)
    elif p.f == 'L':
        ponytail(fg, p, [(hx + 6.4, hy - 4.6), (hx + 9.6, hy - 1.6), (hx + 10.6 + sway * 0.5, hy + 3.6), (hx + 10.0 + sway, hy + 8.6), (hx + 9.0 + sway * 1.4, hy + 12.0)], HAIR_SHORT)


def iri_hair(fg, p, spec):
    """Cabell negre recollit en una cua alta, amb un serrell lateral i dos blens solts a la cara."""
    hx, hy = p.head
    H = HAIR_SHORT
    tex = hair_lvl(hx - 0.5, hy - 2.0, 5.4, k=1.2, strands=0.45, freq=2.6)
    if p.f == 'D':
        line = lambda x, y: y <= hy - 3.4 + ((x - hx) / 6.8) ** 2 * 5.0
        fg.ell(hx, hy - 1.4, 7.5, 7.4, H, 1.8, amp=1.6, clip=line, lvlfn=tex)
        fg.poly([(hx - 6.6, hy - 4.0), (hx + 1.0, hy - 6.6), (hx - 1.0, hy - 2.6), (hx - 5.0, hy - 1.4)], H, 2.0)   # serrell
        fg.limb((hx - 6.8, hy - 2.0), (hx - 6.4, hy + 5.0), 1.0, 0.6, H, 1.8, amp=1.2)                       # blens solts
        fg.limb((hx + 6.8, hy - 2.0), (hx + 6.6, hy + 4.0), 1.0, 0.6, H, 1.6, amp=1.2)
    elif p.f == 'L':
        line = lambda x, y: (x >= hx - 3.4 + max(0, y - (hy - 5)) * 0.3 or y <= hy - 5.0) and not (x < hx + 2.5 and y > hy - 1.5)
        fg.ell(hx + 1.2, hy - 1.2, 7.3, 7.4, H, 1.8, amp=1.6, clip=line, lvlfn=tex)
        fg.poly([(hx - 5.6, hy - 4.4), (hx - 0.5, hy - 6.6), (hx - 2.0, hy - 2.4), (hx - 5.4, hy - 1.6)], H, 2.0)
        fg.limb((hx - 4.6, hy - 2.0), (hx - 4.4, hy + 4.6), 0.9, 0.6, H, 1.8, amp=1.2)
    else:
        fg.ell(hx, hy - 0.8, 7.5, 7.8, H, 1.8, amp=1.6, lvlfn=tex)
        for x in range(int(hx - 5), int(hx + 6), 2):                              # pentinat cap a la goma
            fg.shade(x, hy - 1 + abs(x - hx) * 0.3, -0.6, H)
        sway = 0.0 if p.walk is None else math.sin(2 * math.pi * p.walk / 6) * 1.2
        ponytail(fg, p, [(hx, hy - 3.6), (hx + 0.4, hy + 1.0), (hx + sway * 0.6, hy + 6.0), (hx + sway, hy + 11.0)], H)


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
        for y in range(28 + b, 30 + b):                                            # cordons
            fg.px(hx - 3, y, CORD, 1)
            fg.px(hx + 3, y, CORD, 1)
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
    'hooks': {'hair_back': iri_hair_back, 'hair': iri_hair, 'torso': iri_hoodie, 'collar': iri_collar, 'over': None},
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
    img = person(spec, facing, walk=walk, talk=talk)
    if facing == 'D':
        # «</>» estampat al pit: es posa píxel a píxel al final, sense volum, perquè es llegeixi
        b = Pose(facing, walk, talk, stoop=spec.get('stoop', 0)).bob
        P = img.load()
        for dx, dy in LOGO:
            P[19 + dx, 33 + b + dy] = (226, 236, 228, 255)
    return img


# «</>» de 11×5
LOGO = ((2, 0), (1, 1), (0, 2), (1, 3), (2, 4), (6, 0), (6, 1), (5, 2), (4, 3), (4, 4),
        (8, 0), (9, 1), (10, 2), (9, 3), (8, 4))


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
