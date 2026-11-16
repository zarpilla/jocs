#!/usr/bin/env python3
"""
Aigua Verne — personatges de mostra per a les sales «de lluny» (exteriors i sales grans).

Fa servir el sistema de figures amb volum de Suma Zero / Ni un ou (hd/characters.py) a la seva mida de disseny,
sense ampliar: una persona fa ≈83 px (fotograma de 49×87, peus a (25, 83)). A la resolució del joc (640×360) és
la mida «de lluny». Els personatges de Ni un ou a 640 fan ≈110 px (hd640/draw_characters.py, ×4/3): la mida «de
prop».

Aspecte nou (guió, «Protagonistes»); la cara és la de sempre (la de Suma Zero):
  - **L'Iri**, la pilot: cabell curt de color coure, tenyit, rapat d'un costat; jaqueta de vol marró amb coll de
    xai i pegats; pantalons de càrrega oliva, botes i guants sense dits.
  - **La Vet**, l'enginyera: cabell negre en un monyo alt amb una clau fixa clavada; ulleres de soldar al front;
    granota blava amb massa butxaques i les mànigues arremangades.

Ús: python3 personatges.py  →  personatges.png (fitxa ×4: de cara, de perfil i d'esquena)
"""
import math
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
GAMES = HERE.parents[3]
sys.path.insert(0, str(GAMES / 'ni-un-ou/adapters/benne/tools'))
from pixels import nearest  # noqa: E402

from hd.characters import M, person, SKIN_IRI, SKIN_VET, BOOT, STEELB, BRASS, LENS, HAIR_COPPER  # noqa: E402

# ─── Materials ─────────────────────────────────────────────────────────────
LEATHER = M((22, 12, 10), (44, 24, 16), (70, 40, 24), (98, 60, 34), (128, 84, 48), (160, 112, 70), dith=0.0)
SHEEP = M((92, 80, 66), (140, 126, 104), (184, 170, 144), (216, 204, 178), (238, 230, 208))
TEE = M((70, 66, 60), (120, 114, 104), (170, 164, 150), (208, 202, 186))
OLIVE = M((14, 16, 10), (28, 32, 18), (46, 52, 30), (66, 74, 44), (90, 98, 62), (118, 126, 86), dith=0.0)
GLOVE = M((8, 8, 8), (18, 18, 18), (32, 30, 30), (50, 48, 46))
PATCH_B = M((10, 20, 50), (24, 50, 110), (60, 110, 190), (130, 180, 240))
PATCH_R = M((50, 10, 10), (120, 26, 22), (190, 56, 40), (240, 120, 90))
PATCH_Y = M((60, 44, 6), (140, 104, 16), (214, 170, 40), (250, 224, 120))
PATCH_G = M((8, 36, 18), (20, 80, 40), (50, 140, 70), (120, 200, 130))

COVERALL = M((8, 14, 30), (14, 28, 56), (24, 46, 86), (38, 68, 116), (58, 94, 146), (88, 126, 176), dith=0.0)
HAIR_BLACK = M((4, 4, 6), (10, 8, 12), (20, 16, 22), (34, 28, 36), (54, 46, 56), (80, 72, 82))
STRAP = M((6, 6, 6), (16, 14, 14), (30, 26, 24), (46, 40, 36))
YELLOWH = M((70, 50, 6), (150, 110, 16), (220, 176, 40), (250, 226, 120))


def _stubble(fg, x, y, S):
    """Rapat: la pell, una mica més fosca i amb gra."""
    if fg.get(x, y) and fg.get(x, y)[0] is S:
        fg.shade(x, y, -0.7 - (0.4 if (int(x) + int(y)) % 2 else 0.0), S)


# ─── Iri ───────────────────────────────────────────────────────────────────

def _copper(x, y):
    return 0.45 * math.sin(x * 1.3 - y * 0.9) + 0.3 * math.sin(y * 2.1)


def iri_hair(fg, p, spec):
    """Curt i coure, tirat cap a l'esquerra amb un floc al front; el costat dret, rapat."""
    hx, hy = p.head
    H, S = HAIR_COPPER, spec['skin']
    if p.f == 'D':
        for y in range(int(hy - 6), int(hy + 2)):                                   # el costat rapat (dreta)
            for x in range(int(hx + 3), int(hx + 8)):
                _stubble(fg, x, y, S)
        fg.ell(hx - 0.8, hy - 2.2, 7.2, 6.6, H, 2.8, amp=1.6, cont=(0.2, 0.8), lvlfn=_copper,
               clip=lambda x, y: (y <= hy - 4.0 + ((x - hx + 1) / 7.0) ** 2 * 3.0) and (x <= hx + 3.5 or y <= hy - 5.5))
        fg.poly([(hx - 6.5, hy - 5.5), (hx - 1.0, hy - 6.5), (hx - 3.0, hy - 2.6), (hx - 6.8, hy - 1.0)], H, 3.2,
                lvlfn=_copper)                                                      # el floc
    elif p.f == 'L':
        for y in range(int(hy - 4), int(hy + 3)):                                   # rapat sobre l'orella i el clatell
            for x in range(int(hx - 1), int(hx + 8)):
                _stubble(fg, x, y, S)
        fg.ell(hx + 0.6, hy - 2.6, 7.4, 6.2, H, 2.8, amp=1.6, cont=(0.2, 0.8), lvlfn=_copper,
               clip=lambda x, y: y <= hy - 3.6 or (x < hx - 3 and y <= hy - 1.6))
        fg.poly([(hx - 7.2, hy - 6.0), (hx - 2.0, hy - 8.0), (hx - 4.0, hy - 2.6), (hx - 7.6, hy - 2.0)], H, 3.2,
                lvlfn=_copper)
    else:
        for y in range(int(hy - 4), int(hy + 6)):                                   # d'esquena, el rapat queda a la dreta
            for x in range(int(hx + 2), int(hx + 8)):
                _stubble(fg, x, y, S)
        fg.ell(hx - 0.4, hy - 0.6, 7.4, 8.0, H, 2.6, amp=1.6, cont=(0.2, 0.8), lvlfn=_copper,
               clip=lambda x, y: y <= hy - 4.0 or (x <= hx + 2 and y <= hy + 5.0))


def iri_collar(fg, p, spec):
    """El coll de xai de la jaqueta de vol."""
    b = p.bob
    if p.f == 'D':
        for sx in (-1, 1):
            fg.ell(24.5 + sx * 4.6, 29.0 + b, 3.6, 2.4, SHEEP, 3.0 if sx < 0 else 2.4, amp=1.2, cont=(0.2, 0.8))
    elif p.f == 'L':
        fg.ell(26.5, 28.6 + b, 4.4, 2.4, SHEEP, 2.8, amp=1.2, cont=(0.2, 0.8))
    else:
        fg.ell(24.5, 28.4 + b, 6.6, 2.4, SHEEP, 2.6, amp=1.2, cont=(0.2, 0.8))


def iri_over(fg, p, spec):
    """Jaqueta oberta: la samarreta al mig, la cintura de punt i els pegats."""
    b = p.bob
    if p.f == 'D':
        for y in range(31 + b, 47 + b):
            for x in range(23, 27):
                fg.px(x, y, TEE, 2.6 - (0.8 if x == 26 else 0))
            fg.px(22, y, LEATHER, 1.4)
            fg.px(27, y, LEATHER, 1.0)
        for y in (47 + b, 48 + b, 49 + b):                                          # cintura de punt
            for x in range(16, 33):
                fg.px(x, y, LEATHER, 1.2 + (0.6 if x % 2 else 0))
        for (x0, y0), mat in (((17, 34), PATCH_B), ((29, 33), PATCH_R)):          # pegats al pit
            for y in range(y0 + b, y0 + b + 3):
                for x in range(x0, x0 + 3):
                    fg.px(x, y, mat, 2.4 if (x, y - b) != (x0, y0) else 3.0)
    elif p.f == 'L':
        for y in range(31 + b, 47 + b):
            fg.px(19.6, y, TEE, 2.2)
        for y in (47 + b, 48 + b):
            for x in range(20, 32):
                fg.px(x, y, LEATHER, 1.2 + (0.6 if x % 2 else 0))
        for y in range(34 + b, 37 + b):
            for x in (22, 23, 24):
                fg.px(x, y, PATCH_R, 2.6)
    else:
        for y in (47 + b, 48 + b, 49 + b):
            for x in range(16, 33):
                fg.px(x, y, LEATHER, 1.2 + (0.6 if x % 2 else 0))
        for y in range(34 + b, 41 + b):                                             # el pegat gran de l'esquena
            for x in range(21, 28):
                fg.px(x, y, PATCH_Y if 35 + b <= y <= 39 + b and 22 <= x <= 26 else PATCH_B, 2.4)


def iri_arm(fg, p, spec, i):
    """Un pegat a la màniga i els guants sense dits."""
    if p.f == 'L':
        s, e, w = p.arms[i]
    else:
        s, e, w = p.sh[i], p.elbow[i], p.wrist[i]
    if i == 0 and p.f != 'U':
        mx, my = (s[0] + e[0]) / 2, (s[1] + e[1]) / 2
        fg.ell(mx, my, 1.4, 1.4, PATCH_G, 2.6, amp=0.8)
    fg.ell(w[0] - (0.4 if p.f == 'L' else 0), w[1] + 1.6, 2.2, 1.6, GLOVE, 2.4, amp=1.2)


IRI = {
    'skin': SKIN_IRI, 'legs': OLIVE, 'top': LEATHER, 'shoes': BOOT, 'lashes': True,
    'iris': (52, 38, 30), 'brow': (24, 16, 22),   # la cara de l'Iri, la mateixa a tots els jocs
    'hooks': {'hair': iri_hair, 'collar': iri_collar, 'over': iri_over, 'arm': iri_arm},
}


# ─── Vet ───────────────────────────────────────────────────────────────────

def _sleek(x, y):
    return 0.6 * math.sin(x * 0.5 + y * 1.8)


def _wrench(fg, x0, y0, x1, y1):
    fg.line(x0, y0, x1, y1, STEELB, 2.6)
    fg.px(x0, y0 - 1, STEELB, 3.4)
    fg.px(x0 - 1, y0, STEELB, 3.4)
    fg.px(x1 + 1, y1, STEELB, 1.6)


def vet_hair(fg, p, spec):
    """Negre, estirat enrere cap a un monyo alt, amb una clau fixa clavada; les ulleres de soldar al front."""
    hx, hy = p.head
    H = HAIR_BLACK
    if p.f == 'D':
        fg.ell(hx, hy - 1.4, 7.0, 7.2, H, 2.6, amp=1.6, cont=(0.2, 0.8), lvlfn=_sleek,
               clip=lambda x, y: y <= hy - 3.4 + ((x - hx) / 7.0) ** 2 * 4.6 or abs(x - hx) > 6.2)
        fg.ell(hx, hy - 9.6, 3.6, 3.0, H, 2.8, amp=1.6, cont=(0.2, 0.8), lvlfn=_sleek)
        _wrench(fg, hx - 5, hy - 12, hx + 4, hy - 8)
        fg.line(hx - 7, hy - 4, hx + 7, hy - 4, STRAP, 1.6)                         # ulleres
        for gx in (hx - 2.6, hx + 2.6):
            fg.ell(gx, hy - 4.6, 2.2, 1.8, BRASS, 2.6, amp=0.8)
            fg.ell(gx, hy - 4.6, 1.2, 1.0, LENS, 2.6, amp=0.6)
    elif p.f == 'L':
        fg.ell(hx + 1.0, hy - 1.4, 7.2, 7.2, H, 2.6, amp=1.6, cont=(0.2, 0.8), lvlfn=_sleek,
               clip=lambda x, y: (x >= hx - 1.0 or y <= hy - 4.6) and not (x < hx + 2.6 and y > hy - 1.0))
        fg.ell(hx + 2.4, hy - 9.4, 3.4, 3.0, H, 2.8, amp=1.6, cont=(0.2, 0.8), lvlfn=_sleek)
        _wrench(fg, hx - 2, hy - 12, hx + 6, hy - 8)
        fg.line(hx - 4, hy - 4, hx + 7, hy - 3, STRAP, 1.6)
        fg.ell(hx - 5.0, hy - 4.6, 1.6, 1.9, BRASS, 2.6, amp=0.8)
        fg.px(hx - 5.4, hy - 4.6, LENS, 2.8)
    else:
        fg.ell(hx, hy - 0.8, 7.4, 7.8, H, 2.6, amp=1.6, cont=(0.2, 0.8), lvlfn=_sleek)
        fg.ell(hx, hy - 9.4, 3.6, 3.0, H, 2.6, amp=1.6, cont=(0.2, 0.8), lvlfn=_sleek)
        _wrench(fg, hx + 4, hy - 12, hx - 5, hy - 8)
        fg.line(hx - 7, hy - 4, hx + 7, hy - 4, STRAP, 1.6)


def _pocket(fg, x0, y0, x1, y1, lvl=2.6):
    for y in range(int(y0), int(y1) + 1):
        for x in range(int(x0), int(x1) + 1):
            edge = x in (int(x0), int(x1)) or y == int(y1)
            fg.px(x, y, COVERALL, lvl - (0.9 if edge else 0) + (0.5 if y == int(y0) else 0))


def vet_over(fg, p, spec):
    """Granota: cremallera, dues butxaques al pit (en una, un tornavís), el cinturó."""
    b = p.bob
    if p.f == 'D':
        for y in range(29 + b, 49 + b):
            fg.shade(24.5, y, -0.9, COVERALL)
        _pocket(fg, 17, 33 + b, 21, 38 + b)
        _pocket(fg, 27, 33 + b, 31, 38 + b)
        fg.px(28, 31 + b, YELLOWH, 2.6); fg.px(28, 32 + b, YELLOWH, 2.0)            # el tornavís
        for x in range(16, 33):
            fg.px(x, 47 + b, STRAP, 2.0)
        fg.px(24, 47 + b, BRASS, 3.0); fg.px(25, 47 + b, BRASS, 2.4)
    elif p.f == 'L':
        _pocket(fg, 20, 33 + b, 23, 38 + b)
        fg.px(21, 31 + b, YELLOWH, 2.6); fg.px(21, 32 + b, YELLOWH, 2.0)
        for x in range(20, 32):
            fg.px(x, 47 + b, STRAP, 2.0)
    else:
        for x in range(16, 33):
            fg.px(x, 47 + b, STRAP, 2.0)


def vet_arm(fg, p, spec, i):
    """Mànigues arremangades: el puny gruixut al colze."""
    e = p.arms[i][1] if p.f == 'L' else p.elbow[i]
    fg.ell(e[0], e[1] - 0.5, 3.2, 2.0, COVERALL, 3.2, amp=1.4, cont=(0.2, 0.8))


def vet_leg(fg, p, spec, i):
    """Butxaca de cama, a cada cuixa."""
    h, k = p.hip[i], p.knee[i]
    x = (h[0] + k[0]) / 2 + (-1.5 if i == 0 else 1.5)
    y = (h[1] + k[1]) / 2
    _pocket(fg, x - 1.5, y - 2, x + 1.5, y + 2, 2.4)


def vet_leg_side(fg, p, spec, leg, dl):
    h, k, a, pitch = leg
    if dl == 0:
        x, y = (h[0] + k[0]) / 2, (h[1] + k[1]) / 2
        _pocket(fg, x - 1.5, y - 2, x + 1.5, y + 2, 2.4)


VET = {
    'skin': SKIN_VET, 'legs': COVERALL, 'top': COVERALL, 'forearm': SKIN_VET, 'shoes': BOOT, 'lashes': True,
    'iris': (60, 36, 26), 'brow': (26, 14, 14), 'lip': (150, 40, 52), 'thin': 0.5,   # la cara de la Vet, la de sempre
    'hooks': {'hair': vet_hair, 'over': vet_over, 'arm': vet_arm, 'leg_deco': vet_leg,
              'leg_deco_side': vet_leg_side},
}


def figura(spec, facing, talk=False, walk=None):
    """Una figura 49×87 (peus a (25, 83)). `facing` 'D', 'U', 'L' o 'R' (la R és la L girada)."""
    img = person(spec, 'L' if facing == 'R' else facing, walk=walk, talk=talk)
    return img.transpose(Image.FLIP_LEFT_RIGHT) if facing == 'R' else img


def main():
    S = 4
    cols = [(IRI, f) for f in 'DLU'] + [(VET, f) for f in 'DLU']
    sheet = Image.new('RGBA', (49 * len(cols) * S, 87 * S), (196, 176, 140, 255))
    for i, (spec, f) in enumerate(cols):
        img = nearest(figura(spec, f), (49 * S, 87 * S))
        sheet.alpha_composite(img, (i * 49 * S, 0))
    sheet.save(HERE / 'personatges.png')
    print('personatges.png')


if __name__ == '__main__':
    main()
