#!/usr/bin/env python3
"""
Ni un ou — personatges de mostra, amb el sistema de figures amb volum de Suma Zero (hd/characters.py):
una persona fa ≈83 px, fotograma de 49×87 i peus a (25, 83).

Aspecte nou (no es reaprofita res de l'Iri i la Vet de Suma Zero, només el sistema):
  - **L'Iri**, la maquinista: pell bruna, cabell llarg i arrissat, deixat anar, amb una diadema de tres ratlles (vermell, groc i verd),
    granota blau marí amb les mànigues arremangades, banda reflectant a les cames i el walkie al pit.
  - **La Vet**, la metgessa: pell clara amb pigues, cabell ros amb la clenxa al costat i dues trenes, bata blanca oberta damunt
    del jersei de mariner blau marí que li va gran (els punys li surten per sota de la bata) i el fonendoscopi.
  - **En Bastida**, el contramestre: cabell i barba blancs, jersei de punt cru damunt del pijama i la pipa apagada.

Ús: python3 personatges.py  →  personatges.png (fitxa ×3: de cara, de perfil i d'esquena)
"""
import math
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
GAMES = HERE.parents[3]
sys.path.insert(0, str(GAMES / 'suma-zero/adapters/benne/tools'))

from hd.characters import M, person, SKIN_OLD, SKIN_PALE, BOOT, WHITE, HAIR_WHITE, HAIR_COPPER, STEELB  # noqa: E402

# ─── Materials ─────────────────────────────────────────────────────────────
SKIN_IRI_AB = M((40, 20, 22), (78, 44, 36), (118, 72, 52), (156, 104, 72), (190, 138, 98), (218, 174, 132))
HAIR_DARK = M((8, 6, 8), (18, 12, 14), (32, 22, 22), (50, 34, 30), (72, 52, 44), (98, 74, 60))
OCHRE = M((44, 22, 8), (88, 48, 14), (140, 80, 22), (184, 112, 32), (214, 146, 52), (238, 190, 100))
BOILER = M((6, 10, 22), (12, 20, 38), (20, 32, 58), (30, 48, 82), (44, 66, 106), (62, 88, 130), (88, 116, 156), dith=0.0)
WALKIE = M((6, 6, 8), (16, 16, 20), (30, 30, 36), (48, 48, 56))
HIVIS = M((90, 92, 96), (150, 152, 156), (210, 212, 214), (250, 250, 250))

NAVY_WOOL = M((6, 8, 18), (12, 16, 32), (20, 26, 50), (30, 38, 70), (44, 54, 92), (62, 74, 116), dith=0.0)
TROUSER_V = M((12, 12, 16), (24, 24, 30), (38, 38, 46), (56, 56, 64), (78, 78, 86), dith=0.0)
STETH = M((8, 8, 10), (20, 20, 24), (36, 36, 42), (56, 56, 64))

JUMPER = M((60, 50, 44), (104, 92, 78), (148, 134, 112), (186, 174, 148), (214, 204, 178), (236, 228, 206), dith=0.0)
PYJAMA = M((26, 32, 52), (46, 58, 86), (72, 88, 122), (104, 122, 156), (144, 160, 188), dith=0.0)
PIPEW = M((24, 12, 8), (52, 28, 16), (86, 50, 26), (122, 76, 40))


def _seg(a, b, t0, t1):
    return ((a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0), (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1))


# ─── Iri ───────────────────────────────────────────────────────────────────

BAND_R = M((60, 8, 12), (120, 20, 24), (180, 40, 36), (220, 70, 56), (246, 120, 96))
BAND_Y = M((80, 54, 8), (150, 108, 16), (214, 166, 30), (244, 208, 70), (255, 238, 150))
BAND_G = M((6, 40, 20), (14, 80, 38), (30, 128, 58), (60, 170, 86), (120, 210, 140))


def _headband3(fg, cx, cy, rx, ry, a0, a1, n=40):
    """Diadema de tres ratlles (vermell, groc i verd), en arc sobre el cap."""
    for k, (mat, lvl) in enumerate(((BAND_R, 2.8), (BAND_Y, 2.8), (BAND_G, 2.6))):
        for i in range(n + 1):
            a = math.radians(a0 + (a1 - a0) * i / n)
            fg.px(cx + math.cos(a) * (rx - k * 0.3), cy - math.sin(a) * (ry - k) , mat,
                  lvl + 0.8 * math.sin(a) - 0.4 * math.cos(a))


def _curls(x, y):
    """Textura de rínxols: bucles petits, clars i foscos."""
    return 0.9 * math.sin(x * 1.9 + math.sin(y * 1.3) * 2.2) * math.sin(y * 1.7 + x * 0.4)


def _band_on_head(fg, p, hx, hy):
    """La diadema de tres ratlles, damunt dels rínxols."""
    if p.f == 'D':
        _headband3(fg, hx, hy - 1.4, 7.6, 5.6, 12, 168)
    elif p.f == 'L':
        for k, (mat, lvl) in enumerate(((BAND_R, 3.0), (BAND_Y, 3.0), (BAND_G, 2.6))):   # del front a l'orella
            for i in range(25):
                t = i / 24
                fg.px(hx - 3.4 + 9.0 * t + k, hy - 7.6 + 7.0 * t ** 1.4, mat, lvl - t * 0.8)
    else:
        _headband3(fg, hx, hy - 1.2, 8.0, 5.8, 10, 170)


def iri_hair_back(fg, p, spec):
    """La mata de rínxols, per darrere del cap fins sota les espatlles."""
    hx, hy = p.head
    if p.f == 'D':
        fg.ell(hx, hy + 5.0, 9.2, 13.0, HAIR_DARK, 1.8, amp=1.4, cont=(0.2, 0.8), lvlfn=_curls)
    elif p.f == 'L':
        fg.ell(hx + 3.6, hy + 4.0, 7.8, 12.6, HAIR_DARK, 1.8, amp=1.4, cont=(0.2, 0.8), lvlfn=_curls)


def iri_hair(fg, p, spec):
    """Cabell llarg i arrissat, deixat anar, no gaire voluminós; la diadema l'aparta de la cara."""
    hx, hy = p.head
    H = HAIR_DARK
    if p.f == 'D':
        fg.ell(hx, hy - 1.6, 8.2, 7.6, H, 2.4, amp=1.6, cont=(0.2, 0.8), lvlfn=_curls,
               clip=lambda x, y: y <= hy - 3.4 + ((x - hx) / 8.0) ** 2 * 6.0)
        for sx in (-1, 1):                                                          # volum que cau per davant
            fg.ell(hx + sx * 7.4, hy + 6.0, 2.6, 9.6, H, 2.2 if sx < 0 else 1.8, amp=1.4, cont=(0.2, 0.8),
                   lvlfn=_curls)
    elif p.f == 'L':
        fg.ell(hx + 1.6, hy - 1.4, 8.0, 8.0, H, 2.4, amp=1.6, cont=(0.2, 0.8), lvlfn=_curls,
               clip=lambda x, y: (x >= hx - 1.6 or y <= hy - 4.4) and not (x < hx + 2.8 and y > hy - 0.6 and x < hx + 1.0))
        fg.ell(hx - 4.6, hy - 5.0, 2.8, 2.2, H, 2.8, amp=1.2, lvlfn=_curls)        # rínxols al front
        fg.ell(hx + 3.2, hy + 8.0, 2.8, 7.6, H, 2.2, amp=1.4, cont=(0.2, 0.8), lvlfn=_curls)
    else:
        fg.ell(hx, hy + 3.4, 9.2, 14.2, H, 2.2, amp=1.6, cont=(0.2, 0.8), lvlfn=_curls)
    _band_on_head(fg, p, hx, hy)


def iri_over(fg, p, spec):
    """Granota: cremallera, el walkie a la butxaca del pit i la cintura."""
    b = p.bob
    if p.f == 'L':
        for y in range(33 + b, 39 + b):
            for x in range(19, 22):
                fg.px(x, y, WALKIE, 2.4 if x == 19 else 1.6)
        fg.line(20, 33 + b, 20, 28 + b, WALKIE, 1.0)
        fg.px(21, 35 + b, (240, 120, 40), 0)
        for x in range(20, 31):
            fg.shade(x, 47 + b, -0.8, BOILER)
    elif p.f == 'D':
        for y in range(29 + b, 50 + b):
            fg.shade(24.5, y, -0.9, BOILER)
        for x in range(16, 33):
            fg.shade(x, 47 + b, -0.8, BOILER)
        for y in range(33 + b, 39 + b):                                             # el walkie, a l'esquerra
            for x in range(27, 30):
                fg.px(x, y, WALKIE, 2.4 if x == 27 else 1.6)
        fg.line(29, 33 + b, 29, 28 + b, WALKIE, 1.0)
        fg.px(28, 35 + b, (240, 120, 40), 0)
    else:
        for x in range(16, 33):
            fg.shade(x, 47 + b, -0.8, BOILER)


def iri_arm(fg, p, spec, i):
    """Mànigues arremangades: un puny gruixut al colze."""
    e = p.arms[i][1] if p.f == 'L' else p.elbow[i]
    fg.ell(e[0], e[1] - 0.5, 3.2, 2.0, BOILER, 3.2, amp=1.4, cont=(0.2, 0.8))


def iri_leg_side(fg, p, spec, leg, dl):
    h, k, a, pitch = leg
    p0, p1 = _seg(k, a, 0.55, 0.68)
    fg.limb(p0, p1, 3.0, 2.8, HIVIS, 2.4 + dl, amp=1.4)


def iri_leg_front(fg, p, spec, i):
    p0, p1 = _seg(p.knee[i], p.ankle[i], 0.55, 0.68)
    fg.limb(p0, p1, 3.0, 2.8, HIVIS, 2.4, amp=1.4)


IRI = {
    'skin': SKIN_IRI_AB, 'legs': BOILER, 'top': BOILER, 'forearm': SKIN_IRI_AB, 'shoes': BOOT,
    'iris': (40, 26, 20), 'brow': (14, 10, 12), 'lip': (120, 58, 54), 'stoop': 0,
    'hooks': {'hair_back': iri_hair_back, 'hair': iri_hair, 'over': iri_over, 'arm': iri_arm,
              'leg_deco_side': iri_leg_side, 'leg_deco': iri_leg_front},
}


# ─── Vet ───────────────────────────────────────────────────────────────────

TIE = M((10, 14, 34), (20, 30, 70), (36, 54, 120), (70, 96, 170))


HAIR_BLONDE = M((60, 40, 20), (110, 80, 40), (160, 124, 66), (200, 166, 98), (228, 202, 140), (246, 232, 186))

# El cabell de la Vet: color, serrell, on és la clenxa ('mig' o 'costat'), gruix i llargada de les trenes.
VET_PEL = {'mat': HAIR_BLONDE, 'serrell': False, 'clenxa': 'costat', 'gruix': 1.9, 'llarg': 22.0}


def _braid(fg, pts, lvl, H=HAIR_COPPER, r=1.9):
    """Trena: anelles en ziga-zaga al llarg d'una corba, acabada amb una goma i un floc."""
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) / (r + 0.3)))
        for i in range(n):
            t = i / n
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            side = r * 0.37 if (int(y / (r + 0.1))) % 2 else -r * 0.37
            fg.ell(x + side, y, r, r * 0.8, H, lvl, amp=1.4, cont=(0.1, 0.7))
    x, y = pts[-1]
    fg.ell(x, y + 0.8, r * 0.85, 0.8, TIE, 2.6, amp=1.0)
    fg.limb((x, y + 1.6), (x, y + 4.0), r * 0.75, 0.6, H, lvl - 0.2, amp=1.0)


def _parted(px):
    """Brins que surten de la clenxa (a x = px): més clar a cada banda de la ratlla."""
    def f(x, y):
        return 0.5 * math.sin((x - px) * 2.4 + y * 0.3) + (0.6 if abs(x - px) in (1, 2) else 0.0)
    return f


def _pel(spec):
    return dict(VET_PEL, **spec.get('pel', {}))


def _bpts(hx, hy, x0, x1, x2, o):
    """Els tres punts d'una trena, amb la llargada de `o`."""
    L = o['llarg']
    return [(hx + x0, hy + 3.5), (hx + x1, hy + 3.5 + (L - 3.5) * 0.4), (hx + x2, hy + L)]


def vet_hair_back(fg, p, spec):
    """De perfil, la trena de l'altra banda, que queda darrere."""
    hx, hy = p.head
    o = _pel(spec)
    if p.f == 'L':
        _braid(fg, _bpts(hx, hy, 5.0, 6.0, 5.4, o), 1.6, o['mat'], o['gruix'])


def vet_hair(fg, p, spec):
    hx, hy = p.head
    o = _pel(spec)
    H = o['mat']
    S = spec['skin']
    px = hx if o['clenxa'] == 'mig' else hx - 3
    if p.f == 'D':
        for dx, dy in ((-5, 2), (-4, 3), (-3, 2), (3, 2), (4, 3), (2, 3), (0, 1)):     # pigues
            fg.shade(hx + dx, hy + dy, -0.9, S)
        line = lambda x, y: y <= hy - 3.0 + ((x - hx) / 7.0) ** 2 * 5.0 or abs(x - hx) > 6.0
        fg.ell(hx, hy - 1.0, 7.6, 7.8, H, 2.6, amp=1.6, lvlfn=_parted(px), clip=lambda x, y: line(x, y) and y <= hy + 4)
        if o['serrell']:
            for x in range(int(hx - 6), int(hx + 7)):
                bottom = hy - 2.6 + (1 if (x - int(hx)) % 3 == 0 else 0)
                for y in range(int(hy - 7), int(bottom) + 1):
                    fg.px(x, y, H, 2.8 + 0.5 * math.sin(x * 2.4) - (y - hy + 7) * 0.08)
        else:
            fg.px(px, hy - 8, H, 0.8)                                               # la clenxa
            fg.px(px, hy - 7, H, 1.0)
            if o['clenxa'] == 'costat':                                             # el floc gran cap a la dreta
                fg.poly([(px, hy - 8), (hx + 6.6, hy - 5), (hx + 6.2, hy - 1.4), (hx + 2.0, hy - 4.0)], H, 3.0,
                        lvlfn=_parted(px))
        for sx in (-1, 1):                                                          # les trenes, per davant
            _braid(fg, _bpts(hx, hy, sx * 6.4, sx * 8.4, sx * 7.6, o), 2.8 if sx < 0 else 2.2, H, o['gruix'])
    elif p.f == 'L':
        for dx, dy in ((-4, 2), (-3, 3), (-2, 2)):
            fg.shade(hx + dx, hy + dy, -0.9, S)
        line = lambda x, y: (x >= hx - 2.0 or y <= hy - 4.4) and not (x < hx + 2.6 and y > hy - 1.2)
        fg.ell(hx + 1.2, hy - 1.0, 7.4, 7.6, H, 2.6, amp=1.6, clip=line,
               lvlfn=lambda x, y: 0.5 * math.sin(x * 0.6 + y * 2.0))
        if o['serrell']:
            fg.poly([(hx - 6.4, hy - 6.0), (hx - 1.0, hy - 7.6), (hx - 1.0, hy - 2.2), (hx - 6.2, hy - 2.6)], H, 2.8)
        _braid(fg, _bpts(hx, hy, 3.6, 2.2, 1.6, o), 2.8, H, o['gruix'])
    else:
        bx = hx if o['clenxa'] == 'mig' else hx + 3                                # d'esquena, la clenxa s'emmiralla
        fg.ell(hx, hy - 0.4, 7.6, 8.0, H, 2.6, amp=1.6, lvlfn=_parted(bx))
        for y in range(int(hy - 8), int(hy - 2)):
            fg.px(bx, y, H, 0.8)
        for sx in (-1, 1):                                                          # d'esquena, per sobre de la bata
            _braid(fg, _bpts(hx, hy, sx * 4.6, sx * 6.8, sx * 6.2, o), 2.6 if sx < 0 else 2.2, H, o['gruix'])


def vet_torso(fg, p, spec):
    """Bata blanca oberta: es veu el jersei blau marí del mig, i els faldons fins a mitja cuixa."""
    b = p.bob
    hx = 24.5
    if p.f == 'D':
        for y in range(28 + b, 50 + b):
            w = 3.2 + (y - 28 - b) * 0.06
            for x in range(int(hx - w), int(hx + w + 1)):
                fg.px(x, y, NAVY_WOOL, 2.2 if abs(x - hx) < w - 0.8 else 1.2)
        for y in range(50 + b, 68 + b):                                             # faldons
            for x in range(int(hx - 9.4 - (y - 50 - b) * 0.08), int(hx - 2)):
                fg.px(x, y, WHITE, 3.6 - (0.9 if x == int(hx - 3) else 0) - (y - 50 - b) * 0.03)
            for x in range(int(hx + 3), int(hx + 9.8 + (y - 50 - b) * 0.08)):
                fg.px(x, y, WHITE, 3.0 - (y - 50 - b) * 0.03)
        for x in range(int(hx - 9), int(hx - 2)):
            fg.px(x, 67 + b, WHITE, 2.0)
        for x in range(int(hx + 3), int(hx + 10)):
            fg.px(x, 67 + b, WHITE, 1.6)
        for y in (44, 50, 56):                                                      # butxaca amb un bolígraf
            pass
        for x in range(int(hx + 4), int(hx + 9)):
            fg.px(x, 55 + b, WHITE, 2.2)
        fg.px(hx + 5, 53 + b, (40, 60, 160), 0)
        fg.px(hx + 5, 54 + b, (40, 60, 160), 0)
    elif p.f == 'L':
        for y in range(29 + b, 48 + b):
            fg.px(19.5, y, NAVY_WOOL, 1.6)
            fg.px(20.5, y, NAVY_WOOL, 1.8)
        fg.poly([(19.0, 48 + b), (31.6, 48 + b), (33.0, 68 + b), (19.4, 68 + b)], WHITE, 3.0,
                lvlfn=lambda x, y: -0.6 if int(x) == 27 else 0.0)
        for x in range(20, 33):
            fg.px(x, 67 + b, WHITE, 1.8)
    else:
        fg.poly([(15.6, 48 + b), (33.4, 48 + b), (34.4, 68 + b), (14.6, 68 + b)], WHITE, 3.0,
                lvlfn=lambda x, y: -0.7 if int(x) == 24 else 0.0)
        for x in range(15, 35):
            fg.px(x, 67 + b, WHITE, 1.8)


def vet_collar(fg, p, spec):
    """Coll alt del jersei i el fonendoscopi penjat."""
    b = p.bob
    hx, hy = p.head
    if p.f == 'D':
        fg.ell(24.5, 28.0 + b, 4.4, 2.0, NAVY_WOOL, 2.6, amp=1.2, cont=(0.2, 0.8))
        for i in range(14):                                                         # el tub, en U
            t = i / 13
            x = 24.5 - 5.6 * math.cos(t * math.pi)
            y = 29.5 + b + 6.0 * math.sin(t * math.pi)
            fg.px(x, y, STETH, 2.0)
        fg.line(30.1, 29.5 + b, 29.4, 40 + b, STETH, 1.6)
        fg.ell(29.4, 41.2 + b, 1.6, 1.4, STEELB, 3.2, amp=1.0)
    elif p.f == 'L':
        fg.ell(25.5, 28.2 + b, 4.0, 2.0, NAVY_WOOL, 2.6, amp=1.2, cont=(0.2, 0.8))
        fg.line(21.5, 29.5 + b, 20.4, 39 + b, STETH, 1.6)
        fg.ell(20.4, 40.2 + b, 1.4, 1.4, STEELB, 3.2, amp=1.0)


def vet_arm(fg, p, spec, i):
    """El jersei li va gran: els punys li surten per sota de la bata."""
    w = p.arms[i][2] if p.f == 'L' else p.wrist[i]
    e = p.arms[i][1] if p.f == 'L' else p.elbow[i]
    a, b = _seg(e, w, 0.78, 1.0)
    fg.limb(a, b, 2.5, 2.5, NAVY_WOOL, 2.6, amp=1.2, cont=(0.2, 0.8))


VET = {
    'skin': SKIN_PALE, 'legs': TROUSER_V, 'top': WHITE, 'shoes': BOOT, 'lashes': True,
    'iris': (60, 90, 70), 'brow': (140, 104, 56), 'lip': (176, 76, 78), 'thin': 0.5,
    'hooks': {'hair_back': vet_hair_back, 'hair': vet_hair, 'torso': vet_torso, 'collar': vet_collar,
              'arm': vet_arm},
}


# ─── Bastida ───────────────────────────────────────────────────────────────

def bastida_hair(fg, p, spec):
    """Cabell blanc curt i barba blanca retallada; la pipa apagada a la boca."""
    hx, hy = p.head
    if p.f == 'L':
        line = lambda x, y: (x >= hx - 2.0 or y <= hy - 4.8) and not (x < hx + 2.6 and y > hy - 1.2)
        fg.ell(hx + 1.4, hy - 1.4, 7.2, 7.2, HAIR_WHITE, 2.6, amp=1.6, clip=line)
        fg.poly([(hx + 2.6, hy + 1.0), (hx + 2.4, hy + 6.0), (hx - 1.0, hy + 9.0), (hx - 5.8, hy + 8.4),
                 (hx - 6.6, hy + 6.2), (hx - 3.0, hy + 5.4), (hx - 0.4, hy + 2.6)], HAIR_WHITE, 2.2,
                lvlfn=lambda x, y: 0.5 * math.sin(x * 2.1 + y * 1.3))
        fg.px(hx - 5.5, hy + 4.0, HAIR_WHITE, 3.0)
        fg.px(hx - 4.5, hy + 4.0, HAIR_WHITE, 2.6)
        fg.line(hx - 6.0, hy + 5.0, hx - 9.0, hy + 6.0, PIPEW, 1.0)
        fg.ell(hx - 10.4, hy + 5.0, 1.6, 2.2, PIPEW, 2.6, amp=1.2)
        fg.px(hx - 10.4, hy + 3.0, PIPEW, 0.4)
    elif p.f == 'D':
        line = lambda x, y: y <= hy - 3.2 + ((x - hx) / 7) ** 2 * 4.0
        fg.ell(hx, hy - 1.0, 7.4, 7.4, HAIR_WHITE, 2.6, amp=1.6, clip=line)
        fg.ell(hx, hy + 6.0, 5.6, 3.6, HAIR_WHITE, 2.2, amp=1.2, clip=lambda x, y: y >= hy + 4.4)
        fg.ell(hx - 2.0, hy + 3.8, 2.4, 1.0, HAIR_WHITE, 2.6, amp=1.0)
        fg.ell(hx + 2.0, hy + 3.8, 2.4, 1.0, HAIR_WHITE, 2.4, amp=1.0)
        fg.line(hx + 1.5, hy + 5.0, hx + 4.0, hy + 7.0, PIPEW, 1.0)
        fg.ell(hx + 4.6, hy + 7.0, 1.6, 2.0, PIPEW, 2.6, amp=1.2)
    else:
        fg.ell(hx, hy - 0.6, 7.4, 8.0, HAIR_WHITE, 2.6, amp=1.6)


def bastida_over(fg, p, spec):
    """Jersei de punt (trenes) i ratlles de pijama a les cames."""
    for y in range(fg.h):
        for x in range(fg.w):
            v = fg.buf[y][x]
            if not v:
                continue
            m, l = v
            if m is JUMPER:
                if x % 4 == 0:
                    fg.buf[y][x] = (m, l - 0.7)
                elif x % 4 == 2 and y % 3 == 0:
                    fg.buf[y][x] = (m, l + 0.6)
            elif m is PYJAMA and x % 3 == 0:
                fg.buf[y][x] = (m, l + 1.2)
    b = p.bob
    if p.f == 'L':
        fg.ell(26, 28 + b, 4.2, 2.2, JUMPER, 2.6, amp=1.2, cont=(0.2, 0.8))
    elif p.f == 'D':
        fg.ell(24.5, 28 + b, 5.0, 2.2, JUMPER, 2.6, amp=1.2, cont=(0.2, 0.8))


BASTIDA = {
    'skin': SKIN_OLD, 'legs': PYJAMA, 'top': JUMPER, 'shoes': BOOT, 'brow': (200, 196, 196), 'stoop': 2,
    'thin': -1,
    'hooks': {'hair': bastida_hair, 'over': bastida_over},
}


# ─── Sprites ───────────────────────────────────────────────────────────────

def iri(facing='L', talk=False):
    return person(IRI, facing, talk=talk)


def vet(facing='D', talk=False):
    return person(VET, facing, talk=talk)


def bastida(facing='L', talk=False):
    return person(BASTIDA, facing, talk=talk)


def vet_face():
    """La cara de la Vet (25×30) per al botó «Canvia»."""
    return vet('D').crop((12, 2, 37, 32))


def fitxa():
    """Fitxa: cada personatge de cara, de perfil (a l'esquerra i a la dreta) i d'esquena, ×3."""
    rows = [('iri', iri), ('vet', vet), ('bastida', bastida)]
    cw, ch = 49, 87
    sheet = Image.new('RGBA', (cw * 4 + 10, ch * len(rows) + 6), (20, 30, 34, 255))
    for r, (_, fn) in enumerate(rows):
        frames = [fn('D'), fn('L'), fn('L').transpose(Image.FLIP_LEFT_RIGHT), fn('U')]
        for c, f in enumerate(frames):
            sheet.alpha_composite(f, (5 + c * cw, 3 + r * ch))
    out = HERE / 'personatges.png'
    sheet.resize((sheet.width * 3, sheet.height * 3), Image.NEAREST).save(out)
    print('✔', out)


if __name__ == '__main__':
    fitxa()
