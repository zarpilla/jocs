"""
Personatges de Suma Zero (proposta B, la triada): **sense caricatura**, amb les proporcions i el dibuix de Ferro-9
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


# ─── Secundaris de l'Acte 1 (provisionals: el mateix dibuix, sense els detalls finals) ──────────────

from hd.characters import (SKIN_OLD, SKIN_RUDDY, SKIN_PALE, SKIN_VET, WHITE, TROUSER, GRAY_SHOE, BOOT, SUIT_D, TRENCH,  # noqa: E402
                           CREAM, NAVY_U, FELT, HAIR_WHITE, HAIR_BROWN, HAIR_COPPER, RED, BRASS, STEELB, DENIM)
from PIL import Image  # noqa: E402

APRON = M((10, 8, 12), (20, 18, 24), (34, 30, 38), (50, 46, 54), (70, 64, 72))


def hair_cap(mat, top=-8.0, sides=True, bald=False, fringe=0.0):
    """Cabell curt genèric: un casc (o només els costats, si és calb)."""
    def hook(fg, p, spec):
        hx, hy = p.head
        if bald:
            for sx in (-6.6, 6.6):
                if p.f == 'L' and sx < 0:
                    continue
                fg.ell(hx + sx * (0.4 if p.f == 'L' else 1), hy + 0.5, 1.8, 3.2, mat, 2.4, amp=1.4)
            if p.f == 'U':
                fg.ell(hx, hy + 2.5, 6.6, 3.4, mat, 2.4, amp=1.4)
            return
        if p.f == 'D':
            line = lambda x, y: y <= hy - 3.2 + fringe + ((x - hx) / 7) ** 2 * 4.0
            fg.ell(hx, hy - 1.0, 7.4, 7.4, mat, 2.4, amp=1.6, clip=line)
        elif p.f == 'L':
            line = lambda x, y: (x >= hx - 2.5 or y <= hy - 4.6) and not (x < hx + 2.5 and y > hy - 1.0)
            fg.ell(hx + 1.2, hy - 1.0, 7.2, 7.6, mat, 2.4, amp=1.6, clip=line)
        else:
            fg.ell(hx, hy - 0.6, 7.4, 8.0, mat, 2.4, amp=1.6)
    return hook


def moustache(fg, p, spec):
    hx, hy = p.head
    if p.f == 'D':
        fg.ell(hx - 2.0, hy + 3.6, 2.6, 1.2, HAIR_BROWN, 1.2, amp=1.0)
        fg.ell(hx + 2.0, hy + 3.6, 2.6, 1.2, HAIR_BROWN, 1.2, amp=1.0)
    elif p.f == 'L':
        fg.ell(hx - 4.4, hy + 3.4, 2.4, 1.2, HAIR_BROWN, 1.2, amp=1.0)


def apron(fg, p, spec):
    b = p.bob
    if p.f in ('D', 'L'):
        x0, x1 = (17, 32) if p.f == 'D' else (18, 26)
        fg.poly([(x0, 40 + b), (x1, 40 + b), (x1 + 1, 66 + b), (x0 - 1, 66 + b)], APRON, 2.2, cont=(0.2, 0.8))


def police_cap(fg, p, spec):
    hx, hy = p.head
    fg.ell(hx + (1.0 if p.f == 'L' else 0), hy - 6.2, 7.6, 3.4, NAVY_U, 2.6, amp=1.6, cont=(0.2, 1.0))
    fg.ell(hx - (3.0 if p.f == 'L' else 0), hy - 3.6, 7.8 if p.f != 'L' else 5.0, 1.4, FELT, 1.6, amp=1.0)
    if p.f == 'D':
        fg.ell(hx, hy - 6.4, 1.4, 1.2, BRASS, 3.4, amp=1.0)


def badge(fg, p, spec):
    if p.f == 'D':
        fg.ell(29, 34 + p.bob, 1.6, 1.4, BRASS, 3.4, amp=1.0)


def glasses(fg, p, spec):
    hx, hy = p.head
    if p.f == 'D':
        for gx in (hx - 3.0, hx + 3.0):
            fg.ell(gx, hy + 0.6, 2.2, 1.8, STEELB, 1.6, amp=0.6)
            fg.ell(gx, hy + 0.6, 1.4, 1.0, CREAM, 3.6, amp=0.4)
    elif p.f == 'L':
        fg.ell(hx - 4.0, hy + 0.6, 1.4, 1.8, STEELB, 1.6, amp=0.6)


def hooks(*fns):
    def run(fg, p, spec):
        for f in fns:
            f(fg, p, spec)
    return run


NPCS = {
    # en Marcel: gran, calb amb cabells blancs als costats, ulleres, jersei de punt marró i camisa crema.
    # Sempre assegut de costat en un tamboret de la barra (el maluc a l'alçada del seient).
    'marcel': {'skin': SKIN_OLD, 'legs': TROUSER, 'top': TRENCH, 'shoes': BOOT, 'brow': (190, 186, 190), 'stoop': 1,
               'seated': 49,
               'hooks': {'hair': hooks(hair_cap(HAIR_WHITE, bald=True), glasses)}},
    # en Tomàs: vermellós, bigoti, camisa blanca i davantal negre
    'tomas': {'skin': SKIN_RUDDY, 'legs': TROUSER, 'top': WHITE, 'shoes': BOOT, 'thin': -1,
             'hooks': {'hair': hooks(hair_cap(HAIR_BROWN, fringe=1.0), moustache), 'over': apron}},
    # l'agent Soler: uniforme blau marí, gorra i placa
    'soler': {'skin': SKIN_PALE, 'legs': NAVY_U, 'top': NAVY_U, 'shoes': GRAY_SHOE,
              'hooks': {'hair': hooks(hair_cap(HAIR_COPPER), police_cap), 'over': badge}},
    # l'empleat d'objectes perduts: vestit gris, cansat
    'empleat': {'skin': SKIN_VET, 'legs': SUIT_D, 'top': SUIT_D, 'shoes': GRAY_SHOE, 'closed': False, 'brow_dy': 1,
                'hooks': {'hair': hair_cap(HAIR_BROWN)}},
    # el nen: samarreta vermella (amb un dinosaure, en teoria) i texans
    'nen': {'skin': SKIN_PALE, 'legs': DENIM, 'top': RED, 'shoes': GRAY_SHOE,
            'hooks': {'hair': hair_cap(HAIR_COPPER, fringe=1.5)}},
}


def npc(cid, facing, talk=False):
    if NPCS[cid].get('seated') is not None and facing != 'L':
        # Assegut no es gira de cara ni d'esquena: mira a la dreta (el perfil, de l'altra banda; els peus a x = 25)
        side = person(NPCS[cid], 'L', talk=talk)
        out = Image.new('RGBA', side.size, (0, 0, 0, 0))
        out.alpha_composite(side.transpose(Image.FLIP_LEFT_RIGHT), (2, 0))
        return out
    img = person(NPCS[cid], facing, talk=talk)
    if cid == 'nen':
        # un nen de set anys: el mateix dibuix a mida petita, amb els peus al mateix lloc
        w, h = img.size
        small = img.resize((round(w * 0.62), round(h * 0.62)), Image.NEAREST)
        out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        out.alpha_composite(small, (25 - round(25 * 0.62), 83 - round(83 * 0.62)))
        return out
    return img


def diu_estat(estat, cua=0):
    """En Diu segons el que se li ha donat: dins la caixa, amb l'auricular o davant la pizza."""
    base = diu(cua=cua)
    fg = Fig(GW, GH)
    if estat == 'caixa':
        out = Image.new('RGBA', (GW, GH), (0, 0, 0, 0))
        out.alpha_composite(base, (0, -4))
        fg.poly([(2, 14), (26, 14), (26, 25), (2, 25)], M((40, 24, 14), (90, 60, 30), (146, 102, 58), (184, 136, 80), (216, 172, 108)), 2.6, cont=(0.2, 0.8))
        box = fg.render()
        out.alpha_composite(box)
        return out
    if estat == 'auricular':
        fg.ell(21, 21, 3.0, 3.6, M((50, 6, 14), (110, 16, 26), (170, 30, 36), (220, 60, 54)), 2.6, amp=1.4)
    if estat == 'pizza':
        fg.ell(22, 23, 6.0, 2.2, M((70, 30, 14), (150, 80, 30), (210, 130, 50), (240, 190, 90)), 2.8, amp=1.0)
    base.alpha_composite(fg.render())
    return base


# ─── Vet ───────────────────────────────────────────────────────────────────
# 26 anys, cambrera i mentidera professional. Cabell castany fosc fins a les espatlles, amb clenxa al costat;
# llavis pintats. Canvia de roba a cada escena (guio/guio.md, «Vet — la cara dura»): el seu armari és d'un bar
# cutre, amb dessuadores i texans estripats, i el vestit d'auditora és l'única cosa seriosa que es posa.

HAIR_VET = M((10, 6, 8), (22, 14, 14), (36, 24, 22), (52, 36, 30), (72, 52, 42), (98, 74, 58))
TOP_BLACK = M((6, 6, 10), (14, 12, 18), (24, 22, 30), (36, 34, 44), (52, 50, 60))
HOOD_BLACK = M((6, 6, 10), (14, 14, 20), (24, 24, 32), (36, 36, 46), (52, 52, 64), (72, 72, 86), dith=0.0)
HOOD_PURPLE = M((18, 8, 28), (34, 16, 50), (54, 28, 76), (76, 42, 102), (100, 60, 128), (130, 86, 156), dith=0.0)
FLANNEL = M((40, 6, 10), (78, 12, 18), (120, 22, 26), (160, 36, 34), (196, 60, 50), (226, 100, 80), dith=0.0)
FLANNEL_DARK = M((8, 4, 6), (16, 8, 10), (26, 12, 14), (38, 18, 20), (52, 26, 26))
BOMBER = M((14, 18, 8), (28, 34, 16), (44, 52, 24), (62, 72, 34), (84, 94, 48), (110, 120, 66), dith=0.0)
BOMBER_RIB = M((50, 12, 8), (96, 26, 14), (150, 46, 22), (196, 76, 36), (230, 116, 60))
JEANS_WASHED = M((14, 18, 30), (26, 34, 54), (40, 52, 80), (58, 74, 106), (80, 98, 132), (110, 128, 160), dith=0.0)
SUIT_VET = M((8, 10, 18), (16, 20, 32), (26, 32, 48), (38, 46, 66), (54, 64, 88), (76, 88, 114), dith=0.0)
SHIRT = M((120, 118, 128), (170, 168, 176), (206, 204, 210), (230, 228, 232), (246, 244, 246))
FRAME = M((4, 4, 6), (12, 10, 12), (24, 20, 22), (40, 34, 36))
SHOE_BLACK = M((6, 6, 8), (14, 14, 18), (26, 26, 32), (44, 44, 52), (70, 70, 80))


def _with_hair(fn):
    """Els ganxos de cabell fan servir el material `HAIR_VET`."""
    def h(fg, p, spec):
        fn(fg, p, spec, HAIR_VET)
    return h


def vet_hair_back(fg, p, spec, H):
    """La melena per darrere del cap i de les espatlles."""
    hx, hy = p.head
    tex = hair_lvl(hx - 1, hy - 2, 5.4, k=1.1, strands=0.5, freq=1.9)
    if p.f == 'D':
        fg.poly([(hx - 8.0, hy - 1), (hx + 8.0, hy - 1), (hx + 9.0, hy + 11), (hx - 9.0, hy + 11)], H, 1.6, lvlfn=tex)
    elif p.f == 'L':
        fg.poly([(hx - 1, hy - 2), (hx + 8.0, hy - 2), (hx + 8.6, hy + 12), (hx + 1, hy + 11)], H, 1.8, lvlfn=tex)


def vet_hair(fg, p, spec, H):
    """Cap de cabell amb clenxa al costat esquerre i un floc que li cau a la cara."""
    hx, hy = p.head
    tex = hair_lvl(hx - 1, hy - 2, 5.4, k=1.4, strands=0.5, freq=1.9)
    if p.f == 'D':
        line = lambda x, y: y <= hy - 3.0 + ((x - hx) / 7.2) ** 2 * 3.2 or abs(x - hx) > 5.6
        fg.ell(hx, hy - 0.6, 7.8, 8.2, H, 2.4, amp=1.6, clip=lambda x, y: line(x, y) and y <= hy + 9, lvlfn=tex)
        fg.poly([(hx - 3.0, hy - 7.6), (hx + 6.4, hy - 4.6), (hx + 5.6, hy + 1.0), (hx + 2.0, hy - 3.2)], H, 2.8, lvlfn=tex)
        fg.px(hx - 3, hy - 7, H, 0.6)                                               # la clenxa
    elif p.f == 'L':
        line = lambda x, y: (x >= hx - 3.0 + max(0, y - (hy - 5)) * 0.25 or y <= hy - 4.6) and not (x < hx + 2.0 and y > hy - 1.5)
        fg.ell(hx + 1.0, hy - 0.8, 7.6, 8.0, H, 2.4, amp=1.6, clip=line, lvlfn=tex)
        fg.poly([(hx - 5.4, hy - 4.6), (hx + 1.0, hy - 7.4), (hx - 1.0, hy - 2.0), (hx - 5.0, hy - 1.2)], H, 2.8)
    else:
        fg.ell(hx, hy - 0.4, 7.8, 8.4, H, 2.4, amp=1.6, lvlfn=tex)
        fg.poly([(hx - 8.0, hy + 2), (hx + 8.0, hy + 2), (hx + 8.6, hy + 12), (hx - 8.6, hy + 12)], H, 2.2, lvlfn=tex)


def vet_bun(fg, p, spec, H):
    """D'auditora: cabell estirat enrere i un monyo, sense el floc. Així no sembla ella."""
    hx, hy = p.head
    tex = hair_lvl(hx - 1, hy - 2, 5.4, k=1.4, strands=0.3, freq=2.4)
    if p.f == 'D':
        fg.ell(hx, hy - 9.0, 3.6, 2.8, H, 2.2, amp=1.6, cont=(0.2, 1.0))           # el monyo, que treu el cap per dalt
        line = lambda x, y: y <= hy - 3.6 + ((x - hx) / 7.0) ** 2 * 4.6
        fg.ell(hx, hy - 1.2, 7.5, 7.4, H, 2.4, amp=1.6, clip=line, lvlfn=tex)
        fg.px(hx - 2, hy - 7, H, 0.8)
    elif p.f == 'L':
        line = lambda x, y: (x >= hx - 3.0 or y <= hy - 4.8) and not (x < hx + 2.5 and y > hy - 1.5)
        fg.ell(hx + 1.0, hy - 1.0, 7.3, 7.4, H, 2.4, amp=1.6, clip=line, lvlfn=tex)
        fg.ell(hx + 7.6, hy - 4.4, 3.2, 3.0, H, 2.2, amp=1.6, cont=(0.2, 1.0))
    else:
        fg.ell(hx, hy - 0.6, 7.5, 7.8, H, 2.4, amp=1.6, lvlfn=tex)
        fg.ell(hx, hy - 4.0, 3.4, 3.0, H, 2.0, amp=1.6, cont=(0.2, 1.0))


def vet_glasses(fg, p, spec):
    """Les ulleres de pasta de la cafeteria de l'aeroport."""
    hx, hy = p.head
    if p.f == 'D':
        # una vora prima al voltant de cada ull (els ulls són a xl..xl+1 i xr..xr+1, files ey-1 i ey)
        xl, xr, ey = int(hx - 3.5), int(hx + 2.5), int(hy + 0.5)
        for x0 in (xl, xr):
            for x in range(x0 - 1, x0 + 3):
                fg.px(x, ey - 2, FRAME, 2.0)
                fg.px(x, ey + 1, FRAME, 1.2)
            for y in (ey - 1, ey):
                fg.px(x0 - 1, y, FRAME, 1.6)
                fg.px(x0 + 2, y, FRAME, 1.6)
        for x in range(xl + 3, xr - 1):
            fg.px(x, ey - 1, FRAME, 1.4)                                             # el pont
    elif p.f == 'L':
        for dx in range(-6, -1):
            fg.px(hx + dx, hy - 0.6, FRAME, 2.0)
        fg.px(hx - 6, hy + 0.4, FRAME, 1.6)
        fg.px(hx - 6, hy + 1.4, FRAME, 1.6)
        fg.px(hx - 2, hy + 0.4, FRAME, 1.6)
        for dx in range(-1, 4):
            fg.px(hx + dx, hy - 0.4, FRAME, 1.2)                                    # la patilla


def vet_hoodie(mat):
    """Una dessuadora com la de l'Iri (butxaca, cordons, caputxa), d'un altre color."""
    def torso(fg, p, spec):
        global HOODIE
        old, HOODIE = HOODIE, mat
        try:
            iri_hoodie(fg, p, spec)
        finally:
            HOODIE = old

    def collar(fg, p, spec):
        if p.f == 'D':
            fg.ell(24.5, 28.2 + p.bob, 6.4, 2.4, mat, 2.8, amp=1.4, cont=(0.2, 1.0))
    return torso, collar


def ripped(fg, p, spec, i):
    """Estrips als genolls (davant i esquena)."""
    if p.f == 'U':
        return
    kx, ky = p.knee[i]
    for dx in (-1, 0, 1):
        fg.px(kx + dx, ky, spec['skin'], 3.2 if dx else 3.6)
    fg.px(kx, ky + 1, spec['skin'], 2.8)


def ripped_side(fg, p, spec, leg, dl):
    h, k, a, pitch = leg
    if dl == 0:
        fg.px(k[0] - 1, k[1], spec['skin'], 3.4)
        fg.px(k[0] - 2, k[1], spec['skin'], 3.0)


def plaid(fg, p, spec):
    """Quadres: línies fosques cada 4 píxels a tot el que sigui de franel·la."""
    for y in range(fg.h):
        for x in range(fg.w):
            c = fg.buf[y][x]
            if c and c[0] is FLANNEL and (x % 4 == 0 or y % 4 == 1):
                fg.buf[y][x] = (FLANNEL_DARK, c[1] - (0.6 if (x % 4 == 0 and y % 4 == 1) else 0))


def open_front(inner, w, hem=None):
    """Una peça oberta (camisa, bomber, americana): es veu la samarreta del mig."""
    def torso(fg, p, spec):
        b = p.bob
        hx = 24.5
        if p.f == 'D':
            for y in range(28 + b, (hem or 47) + b):
                for x in range(int(hx - w), int(hx + w + 1)):
                    fg.px(x, y, inner, 2.0 if abs(x - hx) < w - 0.5 else 1.2)
            if hem:
                for x in range(int(hx - 9), int(hx + 10)):
                    fg.shade(x, hem - 1 + b, -1.2, spec['top'])
                    fg.shade(x, hem + b, -0.6, spec['top'])
        elif p.f == 'L':
            for y in range(29 + b, (hem or 46) + b):
                fg.px(19.5, y, inner, 1.6)
                if w > 3:
                    fg.px(20.5, y, inner, 1.8)
    return torso


def bomber_collar(fg, p, spec):
    if p.f == 'D':
        fg.ell(24.5, 28.0 + p.bob, 6.0, 2.0, BOMBER_RIB, 2.2, amp=1.2, cont=(0.2, 1.0))


def suit_torso(fg, p, spec):
    """Americana tancada amb un botó, solapes i camisa blanca en V."""
    b = p.bob
    hx = 24.5
    if p.f == 'D':
        for y in range(28 + b, 37 + b):
            half = (37 + b - y) * 0.45
            for x in range(int(round(hx - half)), int(round(hx + half)) + 1):
                fg.px(x, y, SHIRT, 2.4 if abs(x - hx) < half - 0.5 else 1.6)
        for y in range(29 + b, 38 + b):                                               # solapes
            d = (38 + b - y) * 0.45 + 1
            fg.shade(hx - d, y, 1.0, SUIT_VET)
            fg.shade(hx + d, y, -0.8, SUIT_VET)
        fg.px(hx, 39 + b, SHOE_BLACK, 3.0)                                          # el botó
        for y in range(40 + b, 48 + b):
            fg.shade(hx, y, -1.0, SUIT_VET)
        for x in range(int(hx - 9), int(hx + 10)):
            fg.shade(x, 48 + b, -0.9, SUIT_VET)
    elif p.f == 'L':
        for y in range(28 + b, 33 + b):
            fg.px(19.5, y, SHIRT, 2.2)


# Estampats: es posen píxel a píxel al final, sense volum, perquè es llegeixin (com el «</>» de l'Iri).
SKULL = ('.XXXXX.', 'XXXXXXX', 'X..X..X', 'XXXXXXX', '.XX.XX.', '.X.X.X.')
ALIEN = ('.XXXXX.', 'XXXXXXX', 'X..X..X', 'X..X..X', '.XXXXX.', '..XXX..', '...X...')
BAND = ('XX.X.X.XX', 'X..XXX..X', 'XX.X.X.XX')
PATCH_A = ('XXX', 'X.X', 'XXX')
PATCH_B = ('.X.', 'XXX', '.X.')


def stamp(img, pattern, x0, y0, col):
    P = img.load()
    for dy, row in enumerate(pattern):
        for dx, ch in enumerate(row):
            if ch == 'X':
                P[x0 + dx, y0 + dy] = col


VET_BASE = {'skin': SKIN_VET, 'shoes': BOOT, 'lashes': True, 'lip': (150, 40, 52), 'iris': (60, 36, 26), 'brow': (26, 14, 14)}
HAIR_HOOKS = {'hair_back': _with_hair(vet_hair_back), 'hair': _with_hair(vet_hair)}
_skull_t, _skull_c = vet_hoodie(HOOD_BLACK)
_alien_t, _alien_c = vet_hoodie(HOOD_PURPLE)

# La roba de la Vet. La clau és el prefix de les etiquetes del sprite ('' = la normal); la tria
# `characters.json` (`outfit`) segons l'escena. «Ulleres» afegeix les ulleres a qualsevol roba.
VET_ROBA = {
    # a casa (Escena 1): dessuadora lila amb l'alien, texans negres
    '': (dict(VET_BASE, legs=JEANS_BLACK, top=HOOD_PURPLE, hooks=dict(HAIR_HOOKS, torso=_alien_t, collar=_alien_c)),
         [(ALIEN, 21, 31, (150, 230, 70, 255))]),
    # a la feina (Escena 2): franel·la vermella oberta, samarreta de grup, texans negres estripats
    'Franela': (dict(VET_BASE, legs=JEANS_BLACK, top=FLANNEL,
                     hooks=dict(HAIR_HOOKS, torso=open_front(TOP_BLACK, 4), over=plaid, leg_deco=ripped, leg_deco_side=ripped_side)),
                [(BAND, 20, 33, (210, 206, 196, 255))]),
    # de viatge (Escena 3): bomber verda amb pegats, texans rentats
    'Bomber': (dict(VET_BASE, legs=JEANS_WASHED, top=BOMBER,
                    hooks=dict(HAIR_HOOKS, torso=open_front(TOP_BLACK, 3, hem=46), collar=bomber_collar)),
               [(PATCH_A, 22, 33, (230, 200, 60, 255)), (PATCH_B, 17, 34, (220, 70, 60, 255))]),
    # d'auditora (Actes 2 i 3): vestit jaqueta blau marí, camisa blanca, monyo
    'Auditora': (dict(VET_BASE, legs=SUIT_VET, top=SUIT_VET, shoes=SHOE_BLACK,
                      hooks={'hair': _with_hair(vet_bun), 'torso': suit_torso}),
                 []),
    # de festa (el final, al bar): dessuadora negra amb la calavera, texans blaus estripats, bambes
    'Calavera': (dict(VET_BASE, legs=JEANS_WASHED, top=HOOD_BLACK, shoes=SNEAKER, shoe_lvl=3.4,
                      hooks=dict(HAIR_HOOKS, torso=_skull_t, collar=_skull_c, leg_deco=ripped, leg_deco_side=ripped_side)),
                 [(SKULL, 21, 32, (230, 226, 216, 255))]),
}
# les que poden dur les ulleres (l'aeroport i Ginebra)
VET_ULLERES = ('Bomber', 'Auditora')


def vet(facing, walk=None, talk=False, roba='', ulleres=False):
    spec, prints = VET_ROBA[roba]
    spec = dict(spec)
    if ulleres:
        hk = dict(spec['hooks'])
        hair = hk['hair']
        hk['hair'] = lambda fg, p, s: (hair(fg, p, s), vet_glasses(fg, p, s))
        spec['hooks'] = hk
    img = person(spec, facing, walk=walk, talk=talk)
    if facing == 'D':
        b = Pose(facing, walk, talk, stoop=spec.get('stoop', 0)).bob
        for pattern, x, y, col in prints:
            stamp(img, pattern, x, y + b, col)
    return img


# ─── Secundaris de l'Acte 2: la seu del BCMU ───────────────────────────────
# Cada un té una espec de base i les variants d'estat (`appearance` a game/data/characters.json): el nom de
# l'etiqueta és el de la variant. Les postures (mòbil a la mà, mà a la corbata o a la ràdio) es fan amb el
# ganxo `pose` de `person`, que mou els braços abans de dibuixar.

from hd.characters import HAIR_PLAT, SKIN_PALE as _SKIN_PALE, EYE_W, MOUTH, front_face, side_face  # noqa: E402

PHONE = M((6, 6, 10), (16, 16, 22), (30, 30, 38), (48, 48, 58))
PHONE_LIT = (110, 210, 240)
TIE = M((30, 6, 12), (60, 12, 20), (96, 20, 28), (134, 32, 36), (170, 52, 48))
SUIT_DIR = M((6, 6, 12), (12, 12, 22), (20, 20, 34), (30, 30, 48), (44, 44, 64), (62, 62, 84), dith=0.0)
HIVIS = M((60, 70, 6), (120, 140, 10), (180, 210, 20), (220, 244, 60), (244, 255, 140), dith=0.0)
OVERALL = M((14, 22, 40), (24, 38, 64), (36, 56, 90), (52, 76, 116), (72, 100, 142), (98, 128, 166), dith=0.0)
RADIO = M((4, 4, 6), (12, 12, 16), (24, 24, 30), (40, 40, 48))
CHAIN = M((60, 40, 14), (120, 86, 28), (190, 148, 56), (240, 210, 120))


def _arm_front(p, i, elbow, wrist):
    """Mou el braç `i` de cara (0 = el de l'esquerra de la imatge)."""
    b = p.bob
    p.elbow[i] = (elbow[0], elbow[1] + b)
    p.wrist[i] = (wrist[0], wrist[1] + b)


def _arm_side(p, elbow, wrist):
    """Mou el braç del davant de perfil."""
    b = p.bob
    s = p.arms[0][0]
    p.arms[0] = (s, (elbow[0], elbow[1] + b), (wrist[0], wrist[1] + b))


def pose_phone(p):
    """El mòbil a la mà, davant del pit, mirant-lo."""
    if p.f == 'D':
        _arm_front(p, 1, (34.5, 42), (29.0, 41.5))
    elif p.f == 'L':
        _arm_side(p, (25.0, 41), (19.5, 38.5))


def pose_collar(p):
    """La mà a la corbata (o al coll)."""
    if p.f == 'D':
        _arm_front(p, 1, (33.5, 39), (26.5, 31.5))
    elif p.f == 'L':
        _arm_side(p, (24.0, 39), (20.0, 31.0))


def pose_radio(p):
    """La mà a la ràdio de l'espatlla (l'esquerra de la imatge, de cara; la del davant, de perfil)."""
    if p.f == 'D':
        _arm_front(p, 0, (12.0, 38), (16.5, 30.0))
    elif p.f == 'L':
        _arm_side(p, (23.0, 38), (25.0, 29.0))


def phone_in_hand(fg, p, spec):
    """El mòbil, a la mà moguda per `pose_phone`, amb la pantalla encesa (la llum li puja a la cara de qui el mira)."""
    if p.f == 'D':
        wx, wy = p.wrist[1]
        x0, y0 = round(wx - 3), round(wy - 4)
        fg.poly([(x0, y0), (x0 + 5, y0), (x0 + 5, y0 + 8), (x0, y0 + 8)], PHONE, 1.2)
        for y in range(y0 + 1, y0 + 6):
            for x in range(x0 + 1, x0 + 4):
                fg.px(x, y, PHONE_LIT if (x + y) % 3 else (200, 240, 255), 0)
        fg.ell(wx - 0.5, wy + 4.0, 2.2, 1.8, spec['skin'], 2.8, amp=1.4)        # els dits, a sota
    elif p.f == 'L':
        wx, wy = p.arms[0][2]
        x0, y0 = round(wx - 4), round(wy - 4)
        fg.poly([(x0, y0), (x0 + 3, y0), (x0 + 3, y0 + 7), (x0, y0 + 7)], PHONE, 1.2)
        for y in range(y0 + 1, y0 + 5):
            fg.px(x0 + 1, y, PHONE_LIT, 0)
        fg.ell(wx - 0.4, wy + 2.4, 2.0, 2.0, spec['skin'], 2.8, amp=1.4)


def brow_raised(fg, p, spec):
    """Una cella arquejada (la de la dreta de la imatge): la cella ben amunt i l'ull, obert de cop."""
    hx, hy = p.head
    ey = int(hy + 0.5)
    brow = (120, 116, 126)
    S = spec['skin']
    if p.f == 'D':
        xr = int(hx + 2.5)
        for x in (xr - 1, xr, xr + 1, xr + 2):
            fg.px(x, ey - 3, S, 3.0)
        fg.px(xr - 1, ey - 4, brow, 0); fg.px(xr, ey - 5, brow, 0); fg.px(xr + 1, ey - 5, brow, 0); fg.px(xr + 2, ey - 4, brow, 0)
        fg.px(xr, ey - 1, (34, 22, 30), 0); fg.px(xr + 1, ey - 1, (34, 22, 30), 0)
        fg.px(xr, ey, (70, 90, 120), 0); fg.px(xr + 1, ey, EYE_W, 0)
    elif p.f == 'L':
        ex = int(hx - 3.5)
        fg.px(ex - 1, ey - 3, S, 3.0); fg.px(ex, ey - 3, S, 3.0)
        fg.px(ex - 1, ey - 4, brow, 0); fg.px(ex, ey - 5, brow, 0); fg.px(ex + 1, ey - 4, brow, 0)
        fg.px(ex, ey, (70, 90, 120), 0); fg.px(ex - 1, ey, EYE_W, 0)


def wide_smile(fg, p, spec):
    """El somriure del Director: massa ample, amb dents."""
    hx, hy = p.head
    my = int(hy + 0.5) + 5
    nx = int(hx)
    if p.f == 'D':
        for x in range(nx - 3, nx + 4):
            fg.px(x, my, EYE_W if abs(x - nx) < 3 else MOUTH, 0)
        fg.px(nx - 3, my - 1, MOUTH, 0); fg.px(nx + 3, my - 1, MOUTH, 0)
        fg.px(nx - 2, my + 1, MOUTH, 0); fg.px(nx + 2, my + 1, MOUTH, 0)
        for x in range(nx - 1, nx + 2):
            fg.px(x, my + 1, MOUTH, 0)
    elif p.f == 'L':
        mx = int(hx - 5.5)
        fg.px(mx, my, EYE_W, 0); fg.px(mx + 1, my, EYE_W, 0); fg.px(mx + 2, my - 1, MOUTH, 0)
        fg.px(mx, my + 1, MOUTH, 0); fg.px(mx + 1, my + 1, MOUTH, 0)


def frown(fg, p, spec):
    """Celles avall cap al nas (mal humor) i la boca tensa."""
    hx, hy = p.head
    ey = int(hy + 0.5)
    brow = spec.get('brow', (40, 24, 28))
    S = spec['skin']
    if p.f == 'D':
        xl, xr = int(hx - 3.5), int(hx + 2.5)
        for x, y in ((xl - 1, ey - 3), (xl, ey - 3), (xl + 1, ey - 2), (xr, ey - 2), (xr + 1, ey - 3), (xr + 2, ey - 3)):
            fg.px(x, y, brow, 0)
        fg.px(xl - 1, ey - 2, S, 3.0); fg.px(xr + 2, ey - 2, S, 3.0)
        if not p.talk:
            nx = int(hx)
            for x in (nx - 1, nx, nx + 1):
                fg.px(x, ey + 5, MOUTH, 0)
    elif p.f == 'L':
        ex = int(hx - 3.5)
        fg.px(ex - 1, ey - 2, brow, 0); fg.px(ex, ey - 3, brow, 0); fg.px(ex + 1, ey - 3, brow, 0)


def smile(fg, p, spec):
    hx, hy = p.head
    my = int(hy + 0.5) + 5
    nx = int(hx)
    if p.f == 'D' and not p.talk:
        fg.px(nx - 2, my - 1, MOUTH, 0); fg.px(nx + 2, my - 1, MOUTH, 0)
        for x in (nx - 1, nx, nx + 1):
            fg.px(x, my, MOUTH, 0)
    elif p.f == 'L' and not p.talk:
        mx = int(hx - 5.5)
        fg.px(mx, my, MOUTH, 0); fg.px(mx + 1, my, MOUTH, 0); fg.px(mx + 2, my - 1, MOUTH, 0)


def dir_torso(fg, p, spec):
    """L'americana del Director: camisa blanca, corbata granat i un pin d'or a la solapa."""
    b = p.bob
    hx = 24.5
    if p.f == 'D':
        for y in range(28 + b, 37 + b):
            half = (37 + b - y) * 0.45
            for x in range(int(round(hx - half)), int(round(hx + half)) + 1):
                fg.px(x, y, SHIRT, 2.6 if abs(x - hx) < half - 0.5 else 1.8)
        for y in range(29 + b, 38 + b):
            d = (38 + b - y) * 0.45 + 1
            fg.shade(hx - d, y, 1.0, SUIT_DIR)
            fg.shade(hx + d, y, -0.8, SUIT_DIR)
        fg.px(hx - 0.5, 28 + b, TIE, 3.0); fg.px(hx + 0.5, 28 + b, TIE, 2.4)
        for y in range(29 + b, 37 + b):
            fg.px(hx, y, TIE, 2.6 if y < 34 + b else 2.0)
        fg.px(hx - 6, 32 + b, (230, 190, 80), 0)                                  # el pin del banc
        fg.px(hx, 39 + b, SHOE_BLACK, 3.0)
        for y in range(40 + b, 48 + b):
            fg.shade(hx, y, -1.0, SUIT_DIR)
    elif p.f == 'L':
        for y in range(28 + b, 33 + b):
            fg.px(19.5, y, SHIRT, 2.4)
        fg.px(19.5, 30 + b, TIE, 2.4); fg.px(19.5, 31 + b, TIE, 2.4)


def slick_hair(fg, p, spec):
    """Cabell platí pentinat enrere, amb brillantina (una franja de llum)."""
    hair_cap(HAIR_PLAT, fringe=0.4)(fg, p, spec)
    hx, hy = p.head
    if p.f == 'D':
        for x in range(int(hx - 4), int(hx + 3)):
            fg.shade(x, hy - 6.5 + abs(x - hx) * 0.2, 1.2, HAIR_PLAT)
    elif p.f == 'L':
        for x in range(int(hx - 3), int(hx + 5)):
            fg.shade(x, hy - 6.8, 1.2, HAIR_PLAT)


def _director(extra=None, pose=None, over=None):
    hk = {'hair': hooks(slick_hair, wide_smile, *([extra] if extra else [])), 'torso': dir_torso}
    if over:
        hk['over'] = over
    spec = {'skin': _SKIN_PALE, 'legs': SUIT_DIR, 'top': SUIT_DIR, 'shoes': SHOE_BLACK, 'closed': True,
            'brow': (150, 148, 160), 'hooks': hk}
    if pose:
        spec['pose'] = pose
    return spec


def rius_vest(fg, p, spec):
    """L'armilla reflectant de la subcontracta: les dues franges grises i el logotip a l'esquena."""
    b = p.bob
    if p.f in ('D', 'U'):
        for y in (40 + b, 45 + b):
            for x in range(15, 35):
                fg.shade(x, y, 2.2, HIVIS)
                fg.shade(x, y + 1, 2.2, HIVIS)
        if p.f == 'D':
            for y in range(28 + b, 50 + b):
                fg.shade(24.5, y, -1.6, HIVIS)                                     # la cremallera
    elif p.f == 'L':
        for y in (40 + b, 45 + b):
            for x in range(19, 32):
                fg.shade(x, y, 2.2, HIVIS)


def _rius(contenta=False):
    face = smile if contenta else frown
    return {'skin': SKIN_VET, 'legs': OVERALL, 'top': HIVIS, 'sleeve': OVERALL, 'shoes': BOOT, 'thin': 1,
            'pose': pose_phone,
            'hooks': {'hair': hooks(hair_cap(HAIR_BROWN, fringe=1.4), face), 'torso': rius_vest, 'over': phone_in_hand}}


def shoulder_radio(fg, p, spec):
    """La ràdio a l'espatlla (l'esquerra de la imatge), amb l'antena."""
    b = p.bob
    if p.f == 'D':
        fg.poly([(14, 27 + b), (18, 27 + b), (18, 32 + b), (14, 32 + b)], RADIO, 1.6, cont=(0.2, 0.6))
        fg.line(15, 26 + b, 15, 22 + b, RADIO, 1.0)
        fg.px(17, 28 + b, (220, 40, 40), 0)
    elif p.f == 'L':
        fg.poly([(24, 27 + b), (28, 27 + b), (28, 32 + b), (24, 32 + b)], RADIO, 1.6, cont=(0.2, 0.6))
        fg.line(27, 26 + b, 27, 22 + b, RADIO, 1.0)
    elif p.f == 'U':
        fg.poly([(31, 27 + b), (35, 27 + b), (35, 32 + b), (31, 32 + b)], RADIO, 1.6, cont=(0.2, 0.6))


def key_collar(fg, p, spec):
    """El collaret: una cadena de llautó i la clau grossa del Llibre Major al pit."""
    b = p.bob
    hx = 24.5
    if p.f == 'D':
        for t in range(0, 13):
            a = math.pi * t / 12
            fg.px(hx - 5.5 * math.cos(a), 28 + b + 7 * math.sin(a), CHAIN, 2.6 if t % 2 else 1.8)
        kx, ky = hx, 36 + b
        fg.ell(kx, ky, 1.8, 1.8, CHAIN, 2.8, amp=1.2)
        fg.px(kx, ky, CHAIN, 0.6)
        for y in range(ky + 2, ky + 7):
            fg.px(kx, y, CHAIN, 2.6)
        fg.px(kx + 1, ky + 5, CHAIN, 2.2); fg.px(kx + 1, ky + 6, CHAIN, 2.2)
    elif p.f == 'L':
        for y in range(29 + b, 36 + b):
            fg.px(19.0, y, CHAIN, 2.4 if y % 2 else 1.6)
        fg.ell(18.5, 37 + b, 1.4, 1.6, CHAIN, 2.8, amp=1.0)


def big_jaw(fg, p, spec):
    """Mandíbula ampla i el clatell rapat (en Ballester)."""
    hx, hy = p.head
    S = spec['skin']
    if p.f == 'D':
        fg.ell(hx, hy + 5.0, 6.0, 3.6, S, 3.0, amp=1.4)
        front_face(fg, p, spec)
    elif p.f == 'L':
        fg.ell(hx - 1.0, hy + 5.0, 5.0, 3.4, S, 3.0, amp=1.4)
        side_face(fg, p, spec)


def _ballester(estat=''):
    over = [shoulder_radio, phone_in_hand]
    if estat != 'SenseCollaret':
        over.insert(0, key_collar)
    face = [big_jaw, hair_cap(HAIR_BROWN, top=-9, fringe=-1.5)]
    if estat == 'Relaxat':
        face.append(smile)
    if estat == 'Alerta':
        face.append(frown)
        over = [o for o in over if o is not phone_in_hand]
    spec = {'skin': SKIN_RUDDY, 'legs': NAVY_U, 'top': NAVY_U, 'shoes': BOOT, 'thin': -2.6, 'brow_dy': 1,
            'pose': pose_radio if estat == 'Alerta' else pose_phone,
            'hooks': {'hair': hooks(*face), 'over': hooks(*over), 'torso': badge}}
    return spec


# Tots els de l'Acte 2: id → {variant: espec}; la variant '' és la normal.
NPCS2 = {
    'bonfill': {'': _director(), 'Cella': _director(extra=brow_raised), 'Corbata': _director(pose=pose_collar),
                'Telefon': _director(pose=pose_phone, over=phone_in_hand)},
    'rius': {'': _rius(), 'Contenta': _rius(contenta=True)},
    'ballester': {'': _ballester(), 'Relaxat': _ballester('Relaxat'), 'Alerta': _ballester('Alerta'),
                  'SenseCollaret': _ballester('SenseCollaret')},
}
# en Ballester és enorme: el mateix dibuix, ampliat (i el fotograma, més gran)
BIG = {'ballester': 1.14}


def npc2(cid, facing, talk=False, variant=''):
    spec = NPCS2[cid][variant]
    img = person(spec, facing, talk=talk)
    k = BIG.get(cid)
    if not k:
        return img
    w, h = img.size
    big = img.resize((round(w * k), round(h * k)), Image.NEAREST)
    W2, H2 = big2_size(cid)
    out = Image.new('RGBA', (W2, H2), (0, 0, 0, 0))
    fx, fy = big2_feet(cid)
    out.alpha_composite(big, (fx - round(25 * k), fy - round(83 * k)))
    return out


def big2_size(cid):
    k = BIG[cid]
    return (round(49 * k) + 2, round(87 * k) + 1)


def big2_feet(cid):
    w, h = big2_size(cid)
    return (w // 2, h - 4)


# ─── NETA-3, el robot de neteja ────────────────────────────────────────────
# Un cilindre baixet de plàstic blanc amb faldilla grisa, dos raspalls rodons a sota, un braç amb un
# raspallet i una pantalleta-cara a dalt. Fotograma de 40×44, «peus» (el terra) a (20, 42).

NW, NH = 40, 44
ROBO = M((60, 64, 78), (110, 114, 126), (160, 164, 172), (204, 206, 210), (232, 232, 234), (250, 250, 250))
ROBO_D = M((14, 16, 22), (30, 32, 40), (50, 54, 62), (76, 80, 88), (104, 108, 116))
BRUSH = M((40, 30, 10), (90, 70, 20), (150, 120, 40), (210, 180, 80))
HAZ = M((50, 36, 4), (130, 100, 10), (210, 170, 30), (250, 220, 90))
SCR_ON = (90, 230, 240)
SCR_DIM = (30, 90, 100)


def neta(facing='D', talk=False, estat='', k=0):
    """`estat`: '' (fent la volta), 'descansa' (abaixat, llums baixos) o 'molles' (ajupit, netejant). `k`: fotograma."""
    fg = Fig(NW, NH)
    low = 4 if estat == 'descansa' else 0
    lean = estat == 'molles'
    gy = 42                                                    # el terra
    # raspalls rodons de sota (giren: el pèl canvia de lloc a cada fotograma)
    for bx in ((12, 28) if facing != 'L' else (14, 26)):
        fg.ell(bx, gy - 1, 5, 1.6, BRUSH, 2.0, amp=1.0,
               lvlfn=lambda x, y, k=k: 0.8 if (x + k) % 3 == 0 else 0)
    # la faldilla grisa i el cos blanc
    top = 14 + low
    fg.lathe(gy - 8, gy - 3, lambda y: (6, 34), ROBO_D, 2.6, amp=1.4, cont=(0.2, 0.8))
    def body(y):
        t = (y - top) / (gy - 8 - top)
        half = 11 + 2.5 * t
        if lean:
            c = 20 - 2 * (1 - t) if facing == 'L' else 20
        else:
            c = 20
        return (c - half, c + half)
    fg.lathe(top + 4, gy - 8, body, ROBO, 3.0, amp=1.6, cont=(0.3, 1.0))
    fg.ell(20 - (2 if lean and facing == 'L' else 0), top + 4, 11, 4, ROBO, 3.6, amp=1.6, cont=(0.2, 0.8))   # la tapa
    if facing in ('D', 'U'):
        for x in range(10, 31):                                 # franja de perill
            for y in (gy - 12, gy - 11):
                fg.px(x, y, HAZ, 2.4 if (x + y) % 4 < 2 else 0.6)
    else:
        for x in range(8, 33):
            for y in (gy - 12, gy - 11):
                fg.px(x, y, HAZ, 2.4 if (x + y) % 4 < 2 else 0.6)
    # el cap: una pantalleta en un coll curt
    hx = 20 - (4 if lean and facing == 'L' else 0)
    hy = top - 3 + (3 if lean else 0)
    fg.limb((20, top + 2), (hx, hy + 3), 2.0, 2.0, ROBO_D, 2.2)
    if facing == 'L':
        fg.poly([(hx - 7, hy - 4), (hx + 4, hy - 4), (hx + 4, hy + 4), (hx - 7, hy + 4)], ROBO, 3.0, cont=(0.2, 0.8))
        fg.poly([(hx - 7, hy - 3), (hx - 4, hy - 3), (hx - 4, hy + 3), (hx - 7, hy + 3)], ROBO_D, 1.0)
        on = SCR_DIM if estat == 'descansa' else SCR_ON
        fg.px(hx - 6, hy - 1, on, 0)
        if talk:
            fg.px(hx - 6, hy + 1, on, 0); fg.px(hx - 5, hy + 1, on, 0)
    else:
        fg.poly([(hx - 7, hy - 4), (hx + 7, hy - 4), (hx + 7, hy + 4), (hx - 7, hy + 4)], ROBO, 3.0, cont=(0.2, 0.8))
        if facing == 'D':
            fg.poly([(hx - 5, hy - 3), (hx + 5, hy - 3), (hx + 5, hy + 3), (hx - 5, hy + 3)], ROBO_D, 0.6)
            on = SCR_DIM if estat == 'descansa' else SCR_ON
            if estat == 'descansa':
                for x in (hx - 3, hx - 2, hx + 2, hx + 3):          # ulls tancats: dues ratlletes
                    fg.px(x, hy, on, 0)
            else:
                blink = k == 5
                for ex in (hx - 3, hx + 2):
                    fg.px(ex, hy - 1, on, 0); fg.px(ex + 1, hy - 1, on, 0)
                    if not blink:
                        fg.px(ex, hy, on, 0); fg.px(ex + 1, hy, on, 0)
            if talk:
                for x in range(int(hx - 2), int(hx + 3)):
                    fg.px(x, hy + 2, on, 0)
                fg.px(hx - 1, hy + 1, on, 0); fg.px(hx + 1, hy + 1, on, 0)
            elif estat != 'descansa':
                fg.px(hx - 1, hy + 2, on, 0); fg.px(hx, hy + 2, on, 0); fg.px(hx + 1, hy + 2, on, 0)
        else:                                                   # d'esquena: la reixeta de ventilació
            for y in range(int(hy - 2), int(hy + 3), 2):
                fg.line(hx - 4, y, hx + 4, y, ROBO_D, 1.6)
    # l'antena amb el llum (parpelleja)
    led = (240, 80, 60) if k % 4 < 2 else (120, 30, 30)
    if estat == 'descansa':
        led = (90, 40, 40)
    fg.line(hx + 4, hy - 4, hx + 5, hy - 8, ROBO_D, 2.0)
    fg.px(hx + 5, hy - 9, led, 0)
    # el braç, amb el raspallet
    if facing == 'U':
        return fg.render()
    sx = 9 if facing == 'D' else 13
    sy = top + 10
    if estat == 'molles':
        ex, ey = sx - 4, sy + 8
        wx, wy = sx - 6 + (k % 2), gy - 4
    elif estat == 'descansa':
        ex, ey = sx - 1, sy + 7
        wx, wy = sx, sy + 13
    else:
        ex, ey = sx - 4, sy + 4
        wx, wy = sx - 5, sy + 10 - (1 if talk else 0)
    fg.limb((sx, sy), (ex, ey), 1.4, 1.3, ROBO_D, 2.4)
    fg.limb((ex, ey), (wx, wy), 1.3, 1.2, ROBO_D, 2.4)
    fg.ell(wx, wy + 1.5, 2.6, 1.6, BRUSH, 2.4, amp=1.0)
    img = fg.render()
    if estat == 'molles':                                       # les molles, a terra
        P = img.load()
        for i, (mx, my) in enumerate(((2, 42), (5, 43), (8, 42), (3, 41), (34, 43), (37, 42))):
            if (i + k) % 3 != 0:
                P[mx, my] = (214, 170, 100, 255)
    return img
