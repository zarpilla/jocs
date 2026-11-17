"""
Personatges de Ni un ou, amb el sistema de figures amb volum de Suma Zero (hd/characters.py): una persona fa
≈83 px, fotograma de 49×87 i peus a (25, 83). L'aspecte és nou per a aquest joc (vegeu guio/art/mostra/):

  - **l'Iri**, la maquinista: pell bruna, cabell llarg i arrissat amb una diadema de tres ratlles, granota blau
    marí arremangada amb bandes reflectants i el walkie al pit;
  - **la Vet**, la metgessa: pigues, dues trenes rosses, bata blanca damunt del jersei de mariner que li va gran
    i el fonendoscopi (al final, sense bata);
  - **en Bastida**, el contramestre: cabell i barba blancs, jersei de punt cru i la pipa (de nit, amb pijama);
  - **la Capitana Roig**: cabell gris curt, folre polar blau marí amb el cercle vermell de Mar Obert;
  - **la Juana**, la biòloga: gorra de llana verda, ulleres i un anorac gris que li va gran;
  - **la Nadia**, la periodista: melena negra, impermeable vermell i el mòbil;
  - **el Marcel**, el mariner: pitet de pescar taronja damunt d'un jersei gris i gorra negra;
  - **en Tomàs**, el cuiner: jove i rodó, cabell negre arrissat, jaqueta blanca i davantal;
  - **en Diu**, el gat (el de sempre).
"""
import math

from PIL import Image
from pixels import nearest

from hd.characters import (M, Fig, person, SKIN_OLD, SKIN_PALE, SKIN_VET, SKIN_IRI, SKIN_RUDDY, BOOT, WHITE, HAIR_WHITE, HAIR_COPPER,
                           HAIR_BROWN, STEELB, TROUSER, DENIM, RED, ORANGE, NAVY_U, CREAM, GRAY_SHOE, SNEAKER)

# ─── Materials ─────────────────────────────────────────────────────────────
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
    'skin': SKIN_IRI, 'legs': BOILER, 'top': BOILER, 'forearm': SKIN_IRI, 'shoes': BOOT, 'lashes': True,
    'iris': (52, 38, 30), 'brow': (24, 16, 22), 'stoop': 0,   # la cara de l'Iri, la mateixa a tots els jocs
    'hooks': {'hair_back': iri_hair_back, 'hair': iri_hair, 'over': iri_over, 'arm': iri_arm,
              'leg_deco_side': iri_leg_side, 'leg_deco': iri_leg_front},
}


# ─── Vet ───────────────────────────────────────────────────────────────────

TIE = M((10, 14, 34), (20, 30, 70), (36, 54, 120), (70, 96, 170))


HAIR_CASTANY = M((20, 12, 12), (44, 28, 22), (72, 46, 32), (102, 68, 46), (134, 94, 64), (166, 124, 88))

# El cabell de la Vet: color, serrell, on és la clenxa ('mig' o 'costat'), gruix i llargada de les trenes.
VET_PEL = {'mat': HAIR_CASTANY, 'serrell': False, 'clenxa': 'costat', 'gruix': 1.9, 'llarg': 22.0}


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
    'skin': SKIN_VET, 'legs': TROUSER_V, 'top': WHITE, 'shoes': BOOT, 'lashes': True,
    'iris': (60, 36, 26), 'brow': (26, 14, 14), 'lip': (150, 40, 52), 'thin': 0.5,   # la cara de la Vet, la mateixa a tots els jocs
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
    s = getattr(fg, 'S', 1)                      # una figura a S× (hd640): els patrons, en píxels de 640
    for y in range(fg.h):
        for x in range(fg.w):
            v = fg.buf[y][x]
            if not v:
                continue
            m, l = v
            X, Y = x // s, y // s
            if m is JUMPER:
                if X % 4 == 0:
                    fg.buf[y][x] = (m, l - 0.7)
                elif X % 4 == 2 and Y % 3 == 0:
                    fg.buf[y][x] = (m, l + 0.6)
            elif m is PYJAMA and X % 3 == 0:
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


# De dia, en Bastida porta pantalons de feina; de nit (Escena 1), el pijama.
WORK = M((16, 18, 22), (30, 34, 40), (48, 54, 60), (70, 76, 82), (96, 102, 106), dith=0.0)
BASTIDA_ROBA = {'': dict(BASTIDA, legs=WORK), 'Pijama': BASTIDA}

# La Vet, al final (al bar de Galway), sense bata: el jersei de mariner.
VET_ROBA = {'': VET, 'SenseBata': dict(VET, top=NAVY_WOOL, hooks={k: v for k, v in VET['hooks'].items() if k != 'torso'})}


# ─── Secundaris ────────────────────────────────────────────────────────────

FLEECE = M((6, 10, 22), (12, 18, 38), (20, 30, 58), (32, 46, 82), (48, 66, 108), (70, 90, 136), dith=0.0)
HAIR_GREY = M((40, 40, 46), (74, 74, 80), (110, 110, 114), (146, 146, 148), (182, 182, 182), (214, 214, 212))
ANORAK = M((26, 30, 30), (46, 52, 52), (70, 78, 76), (98, 106, 102), (128, 136, 130), (160, 168, 160), dith=0.0)
WOOL_GREEN = M((10, 30, 16), (20, 56, 28), (34, 86, 42), (54, 118, 60), (84, 150, 86), (124, 184, 120))
RAIN_RED = M((40, 6, 10), (84, 14, 18), (138, 26, 28), (186, 44, 38), (222, 76, 58), (246, 124, 96), dith=0.0)
JERSEY_GREY = M((22, 22, 26), (40, 40, 46), (62, 62, 68), (88, 88, 92), (118, 118, 120), (150, 150, 150), dith=0.0)
BEANIE = M((8, 8, 10), (16, 16, 20), (28, 28, 34), (44, 44, 50), (64, 64, 70))
APRON_B = M((20, 26, 40), (36, 46, 66), (56, 70, 96), (80, 98, 126), (110, 130, 156))
CHECK = M((14, 14, 16), (40, 40, 44), (90, 90, 94), (150, 150, 150), (200, 200, 198))
HAIR_BLACK = M((6, 6, 8), (14, 12, 16), (24, 20, 26), (38, 32, 38), (56, 48, 54), (80, 70, 74))
LOGO_RED = (210, 40, 34)


def hair_cap(mat, top=-8.0, fringe=0.0, curls=False):
    """Cabell curt: un casc. Amb `curls`, rínxols."""
    lv = _curls if curls else None

    def hook(fg, p, spec):
        hx, hy = p.head
        kw = {'lvlfn': lv} if lv else {}
        if p.f == 'D':
            line = lambda x, y: y <= hy - 3.2 + fringe + ((x - hx) / 7) ** 2 * 4.0
            fg.ell(hx, hy - 1.0, 7.6 if curls else 7.4, 7.6 if curls else 7.4, mat, 2.4, amp=1.6, clip=line, **kw)
        elif p.f == 'L':
            line = lambda x, y: (x >= hx - 2.5 or y <= hy - 4.6) and not (x < hx + 2.5 and y > hy - 1.0)
            fg.ell(hx + 1.2, hy - 1.0, 7.4 if curls else 7.2, 7.8 if curls else 7.6, mat, 2.4, amp=1.6, clip=line, **kw)
        else:
            fg.ell(hx, hy - 0.6, 7.4, 8.0, mat, 2.4, amp=1.6, **kw)
    return hook


def beanie(mat, lvl=2.6):
    """Gorra de llana arrapada al cap, amb el doblec."""
    def hook(fg, p, spec):
        hx, hy = p.head
        cx = hx + (1.0 if p.f == 'L' else 0)
        fg.ell(cx, hy - 4.0, 7.8, 5.6, mat, lvl, amp=1.4, cont=(0.2, 0.9), clip=lambda x, y: y <= hy - 2.6,
               lvlfn=lambda x, y: -0.6 if int(x) % 2 == 0 else 0)
        fg.ell(cx, hy - 2.6, 7.9, 1.4, mat, lvl + 0.6, amp=1.0)
    return hook


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


def capitana_hair(fg, p, spec):
    """Cabell gris curt, pentinat enrere."""
    hair_cap(HAIR_GREY, fringe=-0.6)(fg, p, spec)


def capitana_over(fg, p, spec):
    """El folre polar amb cremallera i el cercle vermell de Mar Obert al pit."""
    b = p.bob
    if p.f == 'D':
        for y in range(29 + b, 50 + b):
            fg.shade(24.5, y, 0.8, FLEECE)
        fg.ell(28.5, 34 + b, 1.6, 1.6, M((80, 10, 10), (150, 24, 20), LOGO_RED, (240, 90, 70)), 2.4, amp=1.0)
        fg.ell(24.5, 28 + b, 4.6, 2.0, FLEECE, 3.0, amp=1.2)
    elif p.f == 'L':
        fg.ell(25.5, 28.4 + b, 4.0, 2.0, FLEECE, 3.0, amp=1.2)
        fg.ell(21.5, 34 + b, 1.4, 1.5, M((80, 10, 10), (150, 24, 20), LOGO_RED, (240, 90, 70)), 2.4, amp=1.0)


def juana_hair(fg, p, spec):
    """Cabell castany fins a les espatlles, sota la gorra verda; ulleres."""
    hx, hy = p.head
    if p.f == 'D':
        for sx in (-1, 1):
            fg.ell(hx + sx * 6.6, hy + 4.0, 2.4, 6.0, HAIR_BROWN, 2.2, amp=1.4)
    elif p.f == 'L':
        fg.ell(hx + 3.6, hy + 3.6, 3.4, 6.4, HAIR_BROWN, 2.2, amp=1.4)
    else:
        fg.ell(hx, hy + 3.0, 7.0, 7.4, HAIR_BROWN, 2.2, amp=1.4)
    beanie(WOOL_GREEN)(fg, p, spec)
    glasses(fg, p, spec)


def anorak_over(fg, p, spec):
    """L'anorac: cremallera i butxaques, i li va gran (més ample a baix)."""
    b = p.bob
    if p.f == 'D':
        for y in range(29 + b, 56 + b):
            fg.shade(24.5, y, -0.9, ANORAK)
        for x in range(16, 33):
            fg.shade(x, 55 + b, -0.6, ANORAK)
        fg.ell(24.5, 28 + b, 5.2, 2.4, ANORAK, 2.8, amp=1.2, cont=(0.2, 0.8))
    elif p.f == 'L':
        fg.ell(25.5, 28.4 + b, 4.6, 2.4, ANORAK, 2.8, amp=1.2, cont=(0.2, 0.8))


def nadia_hair(fg, p, spec):
    """Melena negra llisa, tallada a l'alçada de la barbeta, amb serrell."""
    hx, hy = p.head
    H = HAIR_BLACK
    if p.f == 'D':
        fg.ell(hx, hy - 1.2, 7.8, 7.6, H, 2.6, amp=1.6, clip=lambda x, y: y <= hy - 2.6 or abs(x - hx) > 5.4)
        for sx in (-1, 1):
            fg.ell(hx + sx * 6.8, hy + 2.8, 2.2, 5.6, H, 2.4, amp=1.4)
    elif p.f == 'L':
        fg.ell(hx + 1.6, hy - 1.0, 7.6, 7.8, H, 2.6, amp=1.6,
               clip=lambda x, y: (x >= hx - 1.8 or y <= hy - 3.0) and not (x < hx + 2.4 and y > hy - 0.8))
        fg.ell(hx + 3.0, hy + 3.4, 3.4, 4.0, H, 2.4, amp=1.4)
    else:
        fg.ell(hx, hy + 0.4, 8.0, 8.6, H, 2.6, amp=1.6)


def raincoat_over(fg, p, spec):
    """Impermeable vermell amb caputxa a l'esquena i el mòbil a la mà."""
    b = p.bob
    if p.f == 'D':
        for y in range(29 + b, 58 + b):
            fg.shade(24.5, y, -0.9, RAIN_RED)
        fg.ell(24.5, 28 + b, 5.6, 2.4, RAIN_RED, 3.0, amp=1.2)
    elif p.f == 'L':
        fg.ell(28.0, 29 + b, 4.6, 3.0, RAIN_RED, 2.2, amp=1.2)
    else:
        fg.ell(24.5, 29.5 + b, 6.0, 3.6, RAIN_RED, 2.4, amp=1.2)


def marcel_hair(fg, p, spec):
    """Cabell fosc curt sota una gorra negra de mariner."""
    hair_cap(HAIR_BROWN)(fg, p, spec)
    beanie(BEANIE, 2.0)(fg, p, spec)


def bib_over(fg, p, spec):
    """El pitet de pescar taronja, amb tirants, damunt del jersei gris."""
    b = p.bob
    if p.f == 'D':
        fg.poly([(18.5, 40 + b), (30.5, 40 + b), (31.5, 50 + b), (17.5, 50 + b)], ORANGE, 3.0, cont=(0.2, 0.8))
        for sx in (19.5, 29.5):
            fg.line(sx, 29 + b, sx, 40 + b, ORANGE, 2.6)
    elif p.f == 'L':
        fg.poly([(19.0, 40 + b), (29.5, 40 + b), (30.0, 50 + b), (19.0, 50 + b)], ORANGE, 2.8, cont=(0.2, 0.8))
        fg.line(25.0, 29 + b, 24.0, 40 + b, ORANGE, 2.4)
    else:
        for sx in (19.5, 29.5):
            fg.line(sx, 29 + b, 24.5 + (sx - 24.5) * 0.4, 44 + b, ORANGE, 2.6)


def tomas_over(fg, p, spec):
    """Jaqueta de cuiner, de doble botonadura, i el davantal blau."""
    b = p.bob
    if p.f == 'D':
        for y in (33, 38, 43):
            for x in (21, 28):
                fg.px(x, y + b, WHITE, 0.6)
        fg.poly([(17, 46 + b), (32, 46 + b), (33, 66 + b), (16, 66 + b)], APRON_B, 2.4, cont=(0.2, 0.8))
    elif p.f == 'L':
        fg.poly([(18, 46 + b), (27, 46 + b), (27, 66 + b), (17, 66 + b)], APRON_B, 2.4, cont=(0.2, 0.8))






NPCS = {
    'capitana': {'skin': SKIN_OLD, 'legs': TROUSER, 'top': FLEECE, 'shoes': BOOT, 'brow': (120, 120, 124), 'stoop': 0,
                 'iris': (60, 80, 110), 'lip': (150, 80, 80),
                 'hooks': {'hair': capitana_hair, 'over': capitana_over}},
    'juana': {'skin': SKIN_PALE, 'legs': DENIM, 'top': ANORAK, 'shoes': BOOT, 'thin': 0.6, 'brow': (90, 60, 40),
              'iris': (70, 100, 60), 'lip': (170, 90, 90),
              'hooks': {'hair': juana_hair, 'over': anorak_over}},
    'nadia': {'skin': SKIN_VET, 'legs': DENIM, 'top': RAIN_RED, 'shoes': SNEAKER, 'thin': 0.6, 'lashes': True,
              'iris': (40, 26, 20), 'brow': (14, 10, 12), 'lip': (140, 60, 70),
              'hooks': {'hair': nadia_hair, 'over': raincoat_over}},
    'marcel': {'skin': SKIN_RUDDY, 'legs': ORANGE, 'top': JERSEY_GREY, 'shoes': BOOT, 'thin': -0.6, 'stoop': 1,
               'brow': (60, 40, 30),
               'hooks': {'hair': marcel_hair, 'over': bib_over}},
    'tomas': {'skin': SKIN_VET, 'legs': CHECK, 'top': WHITE, 'shoes': GRAY_SHOE, 'thin': -1.4,
              'iris': (40, 26, 20), 'brow': (20, 14, 14),
              'hooks': {'hair': hair_cap(HAIR_BLACK, curls=True), 'over': tomas_over}},
}


def npc(cid, facing, talk=False, walk=None):
    return person(NPCS[cid], facing, walk=walk, talk=talk)


# ─── Diu, el gat ───────────────────────────────────────────────────────────

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


def diu_camina(k=0):
    """Caminant de perfil, cap a l'esquerra (el motor el gira per anar a la dreta). Sis fotogrames, 30×26."""
    fg = Fig(GW, GH)
    fase = k * math.pi / 3
    bob = 0.5 if k % 3 == 0 else 0
    # potes: les del costat de lluny, més fosques i per darrere
    for x0, ph, near in ((10, 0, False), (21, math.pi, False), (12, math.pi, True), (23, 0, True)):
        sw = math.sin(fase + ph)
        lift = max(0.0, math.cos(fase + ph)) * 1.2
        fg.limb((x0, 18 + bob), (x0 - 2.2 * sw, 24.5 - lift), 1.4, 1.1, CAT, 2.6 if near else 1.6, cont=(0.2, 0.8))
        fg.ell(x0 - 2.2 * sw - 0.4, 25 - lift, 1.3, 0.8, CAT_WHITE if near else CAT, 2.4 if near else 1.4, amp=1.0)
    # cua alta, que es gronxa
    tx = 29 + 0.8 * math.sin(fase)
    fg.limb((25, 15 + bob), (28, 10 + bob), 1.4, 1.2, CAT, 2.2, cont=(0.2, 0.8))
    fg.limb((28, 10 + bob), (tx, 5 + bob), 1.2, 1.0, CAT, 2.4, cont=(0.2, 0.8))
    # cos tigrat, amb el ventre i el pit blancs
    fg.ell(17, 16 + bob, 9.0, 4.6, CAT, 2.6, amp=1.6, cont=(0.2, 1.0),
           lvlfn=lambda x, y: -0.8 if (int(x) + int(y) // 2) % 4 == 0 else 0)
    fg.ell(16, 19 + bob, 6.0, 1.6, CAT_WHITE, 2.6, amp=1.2)
    fg.ell(9, 17 + bob, 2.6, 3.0, CAT_WHITE, 2.8, amp=1.4)
    # cap, de perfil
    hy = 11 + bob
    fg.ell(7, hy, 4.6, 4.2, CAT, 2.8, amp=1.6, cont=(0.2, 1.0),
           lvlfn=lambda x, y: -0.8 if int(y) == int(hy) - 3 and int(x) % 3 == 0 else 0)
    fg.poly([(5, hy - 3), (5, hy - 8), (8, hy - 4)], CAT, 2.6)
    fg.poly([(8, hy - 3), (10, hy - 7), (11, hy - 2)], CAT, 2.2)
    fg.ell(3.6, hy + 1.6, 2.0, 1.4, CAT_WHITE, 3.0, amp=1.0)
    fg.ell(5.5, hy - 0.5, 1.2, 1.2, CAT_EYE, 2.6, amp=1.0)
    fg.px(5, hy - 0.5, CAT, 0)
    fg.px(2.5, hy + 1, (190, 110, 120), 0)
    return fg.render()


# ─── Sprites ───────────────────────────────────────────────────────────────

def iri(facing='L', walk=None, talk=False, roba=''):
    return person(IRI, facing, walk=walk, talk=talk)


def vet(facing='D', walk=None, talk=False, roba=''):
    return person(VET_ROBA[roba], facing, walk=walk, talk=talk)


def bastida(facing='L', walk=None, talk=False, roba=''):
    return person(BASTIDA_ROBA[roba], facing, walk=walk, talk=talk)


def cara(fn):
    """La cara d'una protagonista (25×30), per al botó «Canvia»."""
    return fn('D').crop((12, 2, 37, 32))


def fitxa(out):
    """Fitxa de tot el repartiment: de cara, de perfil (a l'esquerra i a la dreta) i d'esquena, ×3."""
    rows = [iri, vet, bastida, lambda f: bastida(f, roba='Pijama')] + [lambda f, c=c: npc(c, f) for c in NPCS]
    cw, ch = 49, 87
    sheet = Image.new('RGBA', (cw * 4 + 10, ch * len(rows) + 6), (20, 30, 34, 255))
    for r, fn in enumerate(rows):
        frames = [fn('D'), fn('L'), fn('L').transpose(Image.FLIP_LEFT_RIGHT), fn('U')]
        for c, f in enumerate(frames):
            sheet.alpha_composite(f, (5 + c * cw, 3 + r * ch))
    nearest(sheet, (sheet.width * 3, sheet.height * 3)).save(out)
    print('✔', out)
