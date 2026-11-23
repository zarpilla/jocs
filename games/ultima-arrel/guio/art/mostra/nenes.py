#!/usr/bin/env python3
"""
L'Última Arrel — l'Iri (11 anys) i la Vet (9), de mostra, per a les sales «de lluny».

La cara és la de sempre (la de Suma Zero: SKIN_IRI / SKIN_VET, iris, celles, pestanyes). La roba i els cabells són
nous (guió, «Protagonistes»):
  - **L'Iri**: cabell castany fosc amb la ratlla al mig i una cua baixa; jaqueta ocre amb un pegat verd, pantalons
    verds, botes, motxilla blava, el walkie a la corretja i la lupa de rellotger penjada al coll (com a la
    referència 1).
  - **La Vet**: gorra marró amb orelles d'os i dues trenes curtes; impermeable vermell, malles fosques i botes
    d'aigua grogues; el walkie a la mà.

**Provisional:** es fan amb el sistema de figures d'adult (hd/characters.py, 49×87) i se'n treuen files del tronc i
de les cames, de manera que el cap queda més gran respecte del cos, com el d'una nena. L'Iri fa ≈72 px i la Vet ≈66.
Les de debò (fase 5) necessiten una postura de nena al sistema de figures.

Ús: python3 nenes.py  →  nenes.png (fitxa ×4: de cara, de perfil i d'esquena)
"""
import math
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
GAMES = HERE.parents[3]
sys.path.insert(0, str(GAMES / 'ni-un-ou/adapters/benne/tools'))
from pixels import nearest  # noqa: E402

from hd.characters import M, person, SKIN_IRI, SKIN_VET, BOOT, BRASS, LENS  # noqa: E402

# ─── Materials ─────────────────────────────────────────────────────────────
OCHRE = M((40, 22, 10), (78, 46, 16), (122, 76, 24), (166, 110, 36), (204, 146, 52), (232, 184, 90), dith=0.0)
MOSS = M((12, 20, 12), (24, 38, 22), (38, 58, 32), (56, 80, 44), (78, 104, 58), (104, 130, 78), dith=0.0)
BAG = M((8, 18, 38), (16, 34, 70), (28, 56, 108), (44, 84, 146), (70, 118, 180), (120, 164, 214))
HAIR_DARK = M((10, 6, 8), (24, 14, 14), (40, 24, 22), (60, 38, 30), (84, 56, 42), (114, 80, 60))
BLACKM = M((6, 6, 8), (14, 14, 16), (26, 26, 28), (42, 42, 44), (64, 64, 66))
PATCHG = M((10, 34, 20), (20, 70, 40), (46, 120, 66), (110, 180, 120))

RAIN = M((40, 6, 10), (80, 14, 18), (130, 26, 26), (180, 44, 36), (218, 76, 56), (244, 124, 96), dith=0.0)
TIGHTS = M((10, 10, 20), (20, 20, 36), (32, 32, 54), (48, 48, 74), (68, 68, 96))
WELLY = M((70, 46, 6), (140, 100, 14), (204, 156, 30), (236, 198, 60), (252, 230, 130))
CAP = M((22, 12, 8), (44, 26, 16), (70, 44, 26), (98, 66, 40), (130, 92, 58), (162, 124, 84))
HAIR_VET = M((6, 4, 6), (14, 10, 12), (26, 18, 20), (40, 30, 30), (60, 46, 44), (84, 66, 60))
TOGGLE = M((60, 44, 30), (120, 96, 66), (190, 164, 120), (236, 220, 180))


# ─── Iri ───────────────────────────────────────────────────────────────────

def _strands(x, y):
    return 0.4 * math.sin(x * 1.6 + y * 0.3)


def iri_back(fg, p, spec):
    """La motxilla (de perfil, sobresurt per darrere) i la cua (de cara, es veu per sota de les orelles)."""
    b = p.bob
    if p.f == 'L':
        fg.ell(31.0, 39.0 + b, 5.2, 9.0, BAG, 2.4, amp=1.6, cont=(0.2, 0.8))
        fg.ell(31.6, 33.0 + b, 4.2, 2.4, BAG, 3.0, amp=1.2)
    elif p.f == 'D':
        for sx in (-1, 1):
            fg.ell(24.5 + sx * 9.6, 40.0 + b, 2.4, 7.0, BAG, 1.8, amp=1.2)            # la motxilla, pels costats
        hx, hy = p.head
        fg.ell(hx, hy + 5.0, 7.6, 5.0, HAIR_DARK, 1.8, amp=1.0, lvlfn=_strands)


def iri_hair(fg, p, spec):
    """Castany fosc, ratlla al mig, recollit en una cua baixa."""
    hx, hy = p.head
    H = HAIR_DARK
    if p.f == 'D':
        fg.ell(hx, hy - 1.6, 7.4, 7.2, H, 2.6, amp=1.6, cont=(0.2, 0.8), lvlfn=_strands,
               clip=lambda x, y: y <= hy - 3.0 + ((x - hx) / 7.0) ** 2 * 3.6 or abs(x - hx) > 5.6)
        for y in range(int(hy - 8), int(hy - 3)):                                   # la ratlla al mig
            fg.shade(hx, y, -1.0, H)
        for sx in (-1, 1):                                                          # els cabells que cauen pels costats
            fg.ell(hx + sx * 6.4, hy + 2.4, 1.8, 5.0, H, 2.0 if sx < 0 else 1.6, amp=0.8, lvlfn=_strands)
    elif p.f == 'L':
        fg.ell(hx + 0.8, hy - 1.6, 7.4, 7.0, H, 2.6, amp=1.6, cont=(0.2, 0.8), lvlfn=_strands,
               clip=lambda x, y: (x >= hx - 1.5 or y <= hy - 4.4) and not (x < hx + 2.4 and y > hy - 1.0))
        fg.ell(hx + 7.0, hy + 4.0, 2.2, 6.4, H, 2.2, amp=1.0, lvlfn=_strands)        # la cua
        fg.ell(hx + 6.4, hy + 0.2, 1.4, 1.2, OCHRE, 3.4, amp=0.6)                   # la goma
    else:
        fg.ell(hx, hy - 0.8, 7.4, 7.8, H, 2.6, amp=1.6, cont=(0.2, 0.8), lvlfn=_strands)
        fg.ell(hx, hy + 8.0, 2.4, 6.0, H, 2.4, amp=1.0, lvlfn=_strands)
        fg.ell(hx, hy + 3.4, 1.6, 1.0, OCHRE, 3.4, amp=0.6)


def iri_over(fg, p, spec):
    """La jaqueta oberta, les corretges de la motxilla, el walkie, la lupa i el pegat."""
    b = p.bob
    if p.f == 'D':
        for y in range(31 + b, 50 + b):
            fg.shade(24.5, y, -1.0, OCHRE)
        for sx in (-1, 1):                                                          # corretges
            for y in range(30 + b, 44 + b):
                fg.px(24.5 + sx * 6.0, y, BAG, 2.2)
        for y in range(34 + b, 39 + b):                                             # el walkie, a la corretja
            for x in (17, 18):
                fg.px(x, y, BLACKM, 2.0 + (1.0 if y == 34 + b else 0))
        fg.px(17, 32 + b, BLACKM, 2.6)                                              # l'antena
        fg.px(17, 33 + b, BLACKM, 2.6)
        fg.line(22, 30 + b, 24, 37 + b, BLACKM, 1.4)                                # el cordó de la lupa
        fg.line(27, 30 + b, 25, 37 + b, BLACKM, 1.4)
        fg.ell(24.5, 39.0 + b, 2.2, 2.2, BRASS, 3.0, amp=0.8)
        fg.ell(24.5, 39.0 + b, 1.2, 1.2, LENS, 3.0, amp=0.6)
        for y in range(42 + b, 45 + b):                                             # el pegat verd
            for x in (28, 29, 30):
                fg.px(x, y, PATCHG, 2.6)
    elif p.f == 'L':
        fg.line(25, 30 + b, 25, 44 + b, BAG, 2.0)
        fg.ell(21.0, 38.0 + b, 1.6, 1.6, BRASS, 3.0, amp=0.6)
    else:
        fg.ell(24.5, 39.0 + b, 7.4, 9.0, BAG, 2.6, amp=1.6, cont=(0.2, 0.8))        # la motxilla
        fg.ell(24.5, 42.0 + b, 5.0, 3.6, BAG, 2.0, amp=1.0)                         # la butxaca
        fg.ell(24.5, 31.2 + b, 4.6, 1.6, BAG, 3.2, amp=0.8)


IRI = {
    'skin': SKIN_IRI, 'legs': MOSS, 'top': OCHRE, 'shoes': BOOT, 'lashes': True, 'thin': 0.4,
    'iris': (52, 38, 30), 'brow': (24, 16, 22),   # la cara de l'Iri, la de sempre
    'hooks': {'hair_back': iri_back, 'hair': iri_hair, 'over': iri_over},
}


# ─── Vet ───────────────────────────────────────────────────────────────────

def vet_hair(fg, p, spec):
    """La gorra amb orelles d'os i dues trenes curtes que en surten per sota."""
    hx, hy = p.head
    if p.f == 'D':
        for sx in (-1, 1):                                                          # trenes
            for k in range(4):
                fg.ell(hx + sx * 7.2, hy + 1.0 + k * 2.2, 1.6, 1.3, HAIR_VET, 2.6 - k * 0.2, amp=0.8)
        fg.ell(hx, hy - 3.0, 7.8, 5.6, CAP, 2.8, amp=1.6, cont=(0.2, 0.8),
               clip=lambda x, y: y <= hy - 3.2 + ((x - hx) / 7.6) ** 2 * 2.6)
        for x in range(int(hx - 7), int(hx + 8)):                                   # la vora de la gorra
            fg.px(x, hy - 3 + ((x - hx) / 7.6) ** 2 * 2.6, CAP, 1.6)
        for sx in (-1, 1):                                                          # orelles
            fg.ell(hx + sx * 5.6, hy - 8.4, 2.4, 2.2, CAP, 2.8, amp=1.0, cont=(0.2, 0.8))
            fg.ell(hx + sx * 5.6, hy - 8.2, 1.0, 1.0, CAP, 1.4, amp=0.4)
    elif p.f == 'L':
        for k in range(4):
            fg.ell(hx + 5.4, hy + 1.4 + k * 2.2, 1.6, 1.3, HAIR_VET, 2.4 - k * 0.2, amp=0.8)
        fg.ell(hx + 0.6, hy - 3.0, 7.8, 5.6, CAP, 2.8, amp=1.6, cont=(0.2, 0.8),
               clip=lambda x, y: y <= hy - 2.6)
        fg.ell(hx - 5.6, hy - 2.8, 3.0, 1.0, CAP, 2.2, amp=0.6)                     # la visera
        fg.ell(hx + 2.0, hy - 9.0, 2.4, 2.2, CAP, 2.8, amp=1.0, cont=(0.2, 0.8))
    else:
        for sx in (-1, 1):
            for k in range(4):
                fg.ell(hx + sx * 5.0, hy + 3.0 + k * 2.2, 1.6, 1.3, HAIR_VET, 2.4 - k * 0.2, amp=0.8)
        fg.ell(hx, hy - 1.6, 7.8, 6.6, CAP, 2.6, amp=1.6, cont=(0.2, 0.8))
        for sx in (-1, 1):
            fg.ell(hx + sx * 5.6, hy - 8.4, 2.4, 2.2, CAP, 2.6, amp=1.0, cont=(0.2, 0.8))


def vet_collar(fg, p, spec):
    """La caputxa de l'impermeable, plegada darrere el coll."""
    b = p.bob
    if p.f == 'L':
        fg.ell(29.0, 29.0 + b, 3.6, 2.6, RAIN, 2.2, amp=1.0, cont=(0.2, 0.8))
    else:
        fg.ell(24.5, 28.6 + b, 6.4, 2.2, RAIN, 2.0 if p.f == 'D' else 2.8, amp=1.0, cont=(0.2, 0.8))


def vet_over(fg, p, spec):
    """L'impermeable: botons de fusta, i més llarg (tapa el maluc)."""
    b = p.bob
    if p.f == 'D':
        for y in range(31 + b, 54 + b):
            fg.shade(24.5, y, -0.8, RAIN)
        for y in (35, 41, 47):
            fg.px(23, y + b, TOGGLE, 2.6)
            fg.px(26, y + b, TOGGLE, 2.6)
        for x in range(17, 33):                                                     # la vora de baix
            fg.px(x, 54 + b, RAIN, 1.4)
            fg.px(x, 53 + b, RAIN, 2.4)
    elif p.f == 'L':
        for x in range(19, 31):
            fg.px(x, 53 + b, RAIN, 2.2)
            fg.px(x, 54 + b, RAIN, 1.2)
        for y in (35, 41, 47):
            fg.px(19, y + b, TOGGLE, 2.6)
    else:
        for x in range(17, 33):
            fg.px(x, 53 + b, RAIN, 2.2)
            fg.px(x, 54 + b, RAIN, 1.2)


def vet_arm(fg, p, spec, i):
    """El walkie a la mà dreta (la de la pantalla, l'esquerra de la Vet)."""
    if i != 1 or p.f == 'U':
        return
    w = p.arms[0][2] if p.f == 'L' else p.wrist[1]
    for y in range(int(w[1]) + 1, int(w[1]) + 6):
        fg.px(w[0], y, BLACKM, 2.2)
        fg.px(w[0] + 1, y, BLACKM, 1.6)
    fg.px(w[0], w[1] - 1, BLACKM, 2.6)
    fg.px(w[0], w[1] - 2, BLACKM, 2.6)


def vet_boot(fg, p, spec, i):
    """Les botes d'aigua: la canya, groga, fins a mitja cama."""
    k, a = p.knee[i], p.ankle[i]
    for t in (0.45, 0.6, 0.75, 0.9, 1.0):
        x, y = k[0] + (a[0] - k[0]) * t, k[1] + (a[1] - k[1]) * t
        fg.ell(x, y, 3.0, 1.2, WELLY, 2.8 - (0.3 if i else 0), amp=1.0)


def vet_boot_side(fg, p, spec, leg, dl):
    h, k, a, pitch = leg
    for t in (0.45, 0.6, 0.75, 0.9, 1.0):
        x, y = k[0] + (a[0] - k[0]) * t, k[1] + (a[1] - k[1]) * t
        fg.ell(x, y, 2.8, 1.2, WELLY, 2.8 + dl, amp=1.0)


VET = {
    'skin': SKIN_VET, 'legs': TIGHTS, 'top': RAIN, 'shoes': WELLY, 'lashes': True, 'thin': 0.6,
    'iris': (60, 36, 26), 'brow': (26, 14, 14), 'lip': (150, 40, 52),   # la cara de la Vet, la de sempre
    'hooks': {'hair': vet_hair, 'collar': vet_collar, 'over': vet_over, 'arm': vet_arm,
              'leg_deco': vet_boot, 'leg_deco_side': vet_boot_side},
}


# ─── De persona gran a nena ────────────────────────────────────────────────

# (fila de, fila fins a, cada quantes files se'n treu una): el tronc, una mica; les cames, més
ESCURÇA = {'iri': ((31, 48, 6), (54, 80, 3)), 'vet': ((31, 48, 4), (54, 80, 2))}


def nena(spec, facing, qui, talk=False, walk=None):
    """Una figura 49×87 amb els peus a (25, 83), com les de persona gran, però més baixa: s'hi treuen files."""
    img = person(spec, 'L' if facing == 'R' else facing, walk=walk, talk=talk)
    if facing == 'R':
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    treu = set()
    for y0, y1, n in ESCURÇA[qui]:
        treu |= {y for y in range(y0, y1) if (y - y0) % n == n - 1}
    files = [y for y in range(img.height) if y not in treu]
    out = Image.new('RGBA', img.size, (0, 0, 0, 0))
    dy = img.height - len(files)
    for i, y in enumerate(files):
        out.paste(img.crop((0, y, img.width, y + 1)), (0, dy + i))
    return out


def alcada(img):
    bb = img.getbbox()
    return bb[3] - bb[1] if bb else 0


def main():
    S = 4
    cols = [(IRI, 'iri', f) for f in 'DLU'] + [(VET, 'vet', f) for f in 'DLU']
    sheet = Image.new('RGBA', (49 * len(cols) * S, 87 * S), (150, 128, 100, 255))
    for i, (spec, qui, f) in enumerate(cols):
        img = nena(spec, f, qui)
        sheet.alpha_composite(nearest(img, (49 * S, 87 * S)), (i * 49 * S, 0))
    sheet.save(HERE / 'nenes.png')
    print('nenes.png', 'iri', alcada(nena(IRI, 'D', 'iri')), 'vet', alcada(nena(VET, 'D', 'vet')))


if __name__ == '__main__':
    main()
