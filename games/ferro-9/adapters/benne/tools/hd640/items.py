"""
Icones d'inventari de Ferro-9 a 640×360: els mateixos objectes de hd/items.py, redibuixats a la casella nova
(65×36 en lloc de 49×27) amb el mateix sistema (Ic de hd/items.py: volum, rampes per material, contorn fosc
selectiu) i aprofitant els píxels de més (lletres llegibles, segells, cargols, vetes, estries, reflexos).

No toca hd/items.py: en reaprofita els materials i les eines i només canvia la mida del llenç.
Ho fan servir draw_items.py (a 640) i hd640/draw_items.py (la comparativa amb les de 480).
"""
import hd640  # noqa: F401
import math

from hd.characters import Fig, LX, LY, LZ
from hd.pix import hr
from hd.items import (Ic, paper, torn, M, FONT, BIG, PAP_W, PAP_F, PAP_C, PAP_O, MANI, SIGN, BLUEP, GRAPH, KOHL,
                      INKB, INKG, STAMP, RULE, WATER, RED, PINK, CORPG, TEAL, SUNY, VELV, ORNG, LIME, SEPIA, SKIN,
                      HAIR, HAIRG, SHIRT, SUIT, F9, ACER, IRON, STEEL, PLAST, BRASS, COPPER, WOOD, PALE, LEATH,
                      RUST, BEET, FEATH, CLOTH, CYAN, STEAM, DARK)

W, H = 65, 36

# ─── Lletres de 4×6 (les etiquetes i els codis, que ara hi caben) ────────────
FONT46 = {
    'A': ('.##.', '#..#', '#..#', '####', '#..#', '#..#'), 'B': ('###.', '#..#', '###.', '#..#', '#..#', '###.'),
    'C': ('.###', '#...', '#...', '#...', '#...', '.###'), 'D': ('###.', '#..#', '#..#', '#..#', '#..#', '###.'),
    'E': ('####', '#...', '###.', '#...', '#...', '####'), 'F': ('####', '#...', '###.', '#...', '#...', '#...'),
    'G': ('.###', '#...', '#...', '#.##', '#..#', '.###'), 'H': ('#..#', '#..#', '####', '#..#', '#..#', '#..#'),
    'I': ('###', '.#.', '.#.', '.#.', '.#.', '###'), 'J': ('..##', '...#', '...#', '...#', '#..#', '.##.'),
    'K': ('#..#', '#.#.', '##..', '#.#.', '#..#', '#..#'), 'L': ('#...', '#...', '#...', '#...', '#...', '####'),
    'M': ('#...#', '##.##', '#.#.#', '#...#', '#...#', '#...#'), 'N': ('#..#', '##.#', '##.#', '#.##', '#.##', '#..#'),
    'O': ('.##.', '#..#', '#..#', '#..#', '#..#', '.##.'), 'P': ('###.', '#..#', '#..#', '###.', '#...', '#...'),
    'Q': ('.##.', '#..#', '#..#', '#..#', '#.#.', '.#.#'), 'R': ('###.', '#..#', '###.', '#.#.', '#..#', '#..#'),
    'S': ('.###', '#...', '.##.', '...#', '...#', '###.'), 'T': ('###', '.#.', '.#.', '.#.', '.#.', '.#.'),
    'U': ('#..#', '#..#', '#..#', '#..#', '#..#', '.##.'), 'V': ('#..#', '#..#', '#..#', '#..#', '.##.', '.##.'),
    'W': ('#...#', '#...#', '#...#', '#.#.#', '##.##', '#...#'), 'X': ('#..#', '#..#', '.##.', '.##.', '#..#', '#..#'),
    'Y': ('#.#', '#.#', '#.#', '.#.', '.#.', '.#.'), 'Z': ('####', '...#', '..#.', '.#..', '#...', '####'),
    '0': ('.##.', '#..#', '#.##', '##.#', '#..#', '.##.'), '1': ('.#.', '##.', '.#.', '.#.', '.#.', '###'),
    '2': ('.##.', '#..#', '..#.', '.#..', '#...', '####'), '3': ('###.', '...#', '.##.', '...#', '...#', '###.'),
    '4': ('#..#', '#..#', '####', '...#', '...#', '...#'), '5': ('####', '#...', '###.', '...#', '...#', '###.'),
    '6': ('.##.', '#...', '###.', '#..#', '#..#', '.##.'), '7': ('####', '...#', '..#.', '..#.', '.#..', '.#..'),
    '8': ('.##.', '#..#', '.##.', '#..#', '#..#', '.##.'), '9': ('.##.', '#..#', '.###', '...#', '..#.', '.#..'),
    '-': ('...', '...', '###', '...', '...', '...'), '.': ('.', '.', '.', '.', '.', '#'),
    '!': ('#', '#', '#', '#', '.', '#'), '?': ('###.', '...#', '..#.', '.#..', '....', '.#..'),
    ' ': ('..', '..', '..', '..', '..', '..'), '/': ('...#', '..#.', '..#.', '.#..', '.#..', '#...'),
}


class Ic640(Ic):
    """Llenç d'una icona de 640: el mateix Ic, a 65×36."""

    def __init__(self):
        Fig.__init__(self, W, H)


# ─── Peces comunes, a la mida nova ──────────────────────────────────────────

def text_w(s, font=FONT46, sp=1):
    """Amplada en píxels d'un text."""
    return sum(len(font[c][0]) + sp for c in s) - sp


def form(f, x0, y0, head=RED, code='27-B', seed=0, w=27, h=31, sig=False):
    """Formulari: full amb capçalera de color i el codi (lletra de 4×6), caselles i ratlles per omplir."""
    S = f.R(x0, y0, x0 + w - 1, y0 + h - 1)
    S -= {(x0 + w - 1, y0), (x0 + w - 2, y0), (x0 + w - 3, y0), (x0 + w - 1, y0 + 1), (x0 + w - 2, y0 + 1),
          (x0 + w - 1, y0 + 2)}                                          # cantó doblegat
    paper(f, S, PAP_F, 4.2, w=w, h=h)
    f.dots([(x0 + w - 3, y0 + 1), (x0 + w - 2, y0 + 2)], PAP_F, 2.4)
    f.px(x0 + w - 3, y0 + 2, PAP_F, 3.0)
    f.rect(x0 + 1, y0 + 1, x0 + w - 4, y0 + 9, head,
           lambda x, y: 2.8 - (y - y0) * 0.1 + (0.8 if y == y0 + 1 else 0) - (0.6 if y == y0 + 9 else 0))
    f.text(x0 + 1 + (w - 4 - text_w(code)) // 2, y0 + 3, code, PAP_F, 5.6, font=FONT46)
    # camps: etiqueta impresa + ratlla o tres caselles
    for i, yy in enumerate(range(y0 + 13, y0 + h - (8 if sig else 2), 4)):
        f.rect(x0 + 2, yy, x0 + 5, yy, INKG, 1.4)
        f.px(x0 + 2, yy - 1, INKG, 2.0)
        if i % 2:
            for b in range(3):
                f.rect(x0 + 8 + b * 5, yy - 1, x0 + 11 + b * 5, yy + 1, INKG, 2.6)
                f.rect(x0 + 9 + b * 5, yy, x0 + 10 + b * 5, yy, PAP_F, 4.4)
        else:
            f.rect(x0 + 7, yy + 1, x0 + w - 3, yy + 1, INKG, 2.8)
    return S


def scrap_cartell(f, S, seed, back=True, curl=True):
    """Tros de cartell de la Gavina: per darrere blanc; al cantó, la vora verda de davant que es gira."""
    paper(f, S, SIGN, 4.0)
    if curl:
        xs = [p[0] for p in S]
        ys = [p[1] for p in S]
        x1, y0 = max(xs), min(ys)
        tri = {(x, y) for (x, y) in S if (x1 - x) + (y - y0) < 7}
        for p in tri:
            f.erase(*p)
        F = {(x1 - 6 + i, y0 + 1 + j) for i in range(7) for j in range(7) if i - j <= 0 and i + j <= 6}
        F = {(x, y) for (x, y) in F if (x, y) in S}
        f.drop(F, -1.2, -1, 1)
        f.fill(F, CORPG, 2.6, rim=(0.8, -0.6))
        for j in range(2, 6):                                            # la tinta del davant, que es transparenta
            f.shade(x1 - 6 + j // 2, y0 + 1 + j, -0.5)
    return S


BEAM_ROWS = [2.4, 1.9, 1.2, 0.4, -1.8, -1.5, -1.3, -1.1, -1.0, -0.9, -0.8, 1.0, 0.5, 0.0, -0.7]   # 15 files


def beam(f, x0, x1, y0, mat, base, end=True, sheen=0.0):
    """Biga en I vista de costat (ala de dalt, ànima enfonsada, ala de baix; 15 files) amb la secció en I al cap
    esquerre."""
    for x in range(x0, x1 + 1):
        g = (hr(x // 4, y0, 5) - 0.5) * 0.35 + (math.sin(x / 6) * sheen if sheen else 0)
        for j, r in enumerate(BEAM_ROWS):
            l = base + r + g
            if x == x1:
                l -= 1.2                       # testa de la dreta, a l'ombra
            f.px(x, y0 + j, mat, l)
    if end:
        # secció en I al cap de l'esquerra (la testa tallada, de cara a la llum)
        ex = x0 - 7
        for j in range(15):
            xs = range(ex, x0) if (j <= 3 or j >= 11) else range(ex + 3, ex + 5)
            for x in xs:
                l = base + 1.4 - j * 0.06
                if j in (3, 14):
                    l -= 0.8
                if x == ex or j in (0, 11):
                    l += 0.6
                f.px(x, y0 + j, mat, l)
        for j in range(4, 11):                 # buits de l'ànima a la testa (ombra de les ales)
            f.shade(ex + 5, y0 + j, -0.4)


# ─── Icones ─────────────────────────────────────────────────────────────────

def clau_anglesa(f):
    """Clau anglesa de ferro-9 (acer blavós reluent), amb el segell «Lot 1» gravat al mànec i el cargol sens fi."""
    a, b = (8, 29), (44, 15)
    pix = f.limb(a, b, 3.0, 3.4, F9, 4.4, amp=2.6)
    f.shine(pix, 0.82, 1.6)
    # forat de penjar al cap del mànec, amb el bisell
    for p in f.E(9.5, 28, 1.1, 1.1):
        f.erase(*p)
    f.dots([(11, 28), (10, 29)], F9, 1.0)
    f.dots([(9, 26), (8, 27)], F9, 2.0)
    # cap: disc amb la boca oberta en la direcció del mànec
    cx, cy = 51, 11.5
    ux, uy = (b[0] - a[0]), (b[1] - a[1])
    n = math.hypot(ux, uy)
    ux, uy = ux / n, uy / n
    head = {}
    for y in range(0, 23):
        for x in range(40, 64):
            dx, dy = x - cx, y - cy
            if (dx / 8.8) ** 2 + (dy / 8.3) ** 2 > 1:
                continue
            u, v = dx * ux + dy * uy, -dx * uy + dy * ux
            if u > -0.8 and abs(v) < 2.3:
                continue                                          # la boca
            nz = max(0.0, 1 - (dx / 8.8) ** 2 - (dy / 8.3) ** 2) ** 0.5
            head[(x, y)] = (dx / 8.8, dy / 8.3, nz)
    for (x, y), (nx, ny, nz) in head.items():
        f.px(x, y, F9, 4.2 + 2.6 * (nx * LX + ny * LY + nz * LZ - 0.35))
    f.shine(head, 0.78, 1.8)
    # vores de la boca (cares interiors)
    for (x, y) in head:
        dx, dy = x - cx, y - cy
        u, v = dx * ux + dy * uy, -dx * uy + dy * ux
        if u > -0.8 and 2.3 <= abs(v) < 3.5:
            f.shade(x, y, 1.2 if v < 0 else -1.6)
    # cargol sens fi (moleteig) sota la boca: dues files d'estries
    for i in range(7):
        for k, off in enumerate((3.3, 4.4)):
            x, y = round(45 + i * ux * 1.1 + off * -uy), round(16 + i * uy * 1.1 + off * ux)
            f.px(x, y, F9, (2.0 if i % 2 else 5.2) - k * 0.6)
    # segell gravat «LOT 1»: un rectangle de puntets foscos al llarg del mànec
    for t in (0.30, 0.36, 0.42, 0.48, 0.54, 0.60, 0.66):
        x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        f.px(round(x), round(y), F9, 2.2)
        if t in (0.30, 0.48, 0.66):
            f.px(round(x - uy), round(y + ux), F9, 2.6)


def formulari_27b(f):
    """Formulari 27-B en blanc: capçalera vermella, caselles buides."""
    form(f, 19, 2)


def formulari_segellat(f):
    """El 27-B amb un segell vermell gros, rodó, que sobresurt del full."""
    form(f, 17, 2)
    f.stamp(39, 24, 6.9, 2.6, seed=1)


def formulari_triplicat(f):
    """Tres còpies del 27-B ventallades, cadascuna amb el seu segell vermell a la part que es veu."""
    pos = ((4, 2), (19, 3), (35, 4))
    for x, y in pos:
        form(f, x, y, w=25, h=29)
    for i, (x, y) in enumerate(pos):
        if i < 2:
            f.stamp(x + 8, y + 21, 4.5, 2.6, seed=i + 3)
        else:
            f.stamp(x + 15, y + 20, 5.6, 2.6, seed=i + 3)


def plomall(f):
    """Plomall de plomes d'estruç: mànec de fusta torneada, virolla de llautó i un plomall gros."""
    pix = f.limb((4, 21), (28, 17), 1.7, 2.0, WOOD, 4.0, amp=2.2)
    f.shine(pix, 0.85, 1.0)
    for x in (10, 18):                                                   # les motllures del torn
        y = 21 - (x - 4) // 6
        f.shade(x, y, -1.2); f.shade(x, y + 1, -1.2); f.shade(x, y - 1, -1.0)
        f.shade(x + 1, y - 1, 0.8)
    f.ell(5, 21, 1.6, 1.6, WOOD, 3.4, amp=1.6)                           # el pomet del cul
    f.rect(28, 14, 32, 20, BRASS, lambda x, y: 4.6 - (y - 14) * 0.4 - (x - 28) * 0.15, rim=(0.4, -1.0))
    f.rect(28, 16, 32, 16, BRASS, 2.4)
    f.px(29, 14, BRASS, 6.0)
    # plomall: bulb que s'eixampla, amb plomes que surten de la virolla
    OX, OY = 29, 17
    for y in range(2, 34):
        for x in range(32, 64):
            dx, dy = x - 46, (y - 17.5) / 1.05
            r = math.hypot(dx / 15.4, dy / 14.1)
            rr = 1 + (hr(x, y, 8) - 0.5) * 0.24
            if r > rr or x < 33 + abs(y - 17.5) * 0.55:
                continue
            ang = math.atan2(y - OY, x - OX)
            strand = math.sin(ang * 40 + hr(int(ang * 20), 3) * 3) * 0.7
            lvl = 3.6 - dy / 14.1 * 1.3 - dx / 16 * 0.5 + strand - r ** 3 * 0.9
            if hr(int(ang * 20), 11) > 0.78:
                lvl -= 1.3
            if hr(x, y, 21) > 0.93:                                      # les barbes que brillen
                lvl += 1.0
            f.px(x, y, FEATH, lvl)
    # puntes soltes
    for x, y in ((62, 13), (62, 22), (58, 4), (59, 31), (63, 17), (52, 2)):
        if f.get(x - 1, y) or f.get(x, y + 1):
            f.px(x, y, FEATH, 2.6)


def segell(f):
    """Segell oficial: pom de fusta envernissada, coll de llautó, base de fusta amb placa gravada i goma vermella."""
    SX = 30
    f.stamp(54, 25, 5.6, 2.2, seed=7)                                    # empremta vermella al costat
    # base
    f.rect(SX - 13, 19, SX + 12, 28, WOOD,
           lambda x, y: 4.0 - (x - SX + 13) / 25 * 1.4 - (y - 19) * 0.08 + (hr(x // 4, y, 6) - 0.5) * 0.4,
           rim=(0.8, -1.0))
    f.rect(SX - 13, 19, SX + 12, 19, WOOD, 5.2)
    f.rect(SX - 12, 29, SX + 11, 31, STAMP, lambda x, y: 3.0 - (y - 29) * 0.8)
    f.rect(SX - 9, 21, SX + 7, 26, BRASS, lambda x, y: 4.4 - (x - SX + 9) * 0.1, rim=(0.6, -1.0))
    for x in range(SX - 7, SX + 6, 2):                                   # el gravat de la placa
        f.px(x, 23 + (x // 2) % 2, BRASS, 2.0)
    f.dots([(SX - 8, 22), (SX + 6, 22), (SX - 8, 25), (SX + 6, 25)], BRASS, 6.0)   # cargolets
    # coll de llautó
    pix = f.limb((SX, 17), (SX, 12), 3.2, 2.6, BRASS, 4.0, amp=2.4)
    f.shine(pix, 0.8, 1.4)
    f.rect(SX - 4, 16, SX + 4, 18, BRASS, lambda x, y: 3.2 - (y - 16) * 0.5)
    f.rect(SX - 4, 16, SX + 4, 16, BRASS, 4.6)
    # pom
    pix = f.ell(SX, 7, 6.6, 5.6, WOOD, 3.9, amp=2.6)
    f.shine(pix, 0.82, 2.0)
    for x, y in ((SX + 2, 4), (SX + 4, 7), (SX - 1, 10)):                 # la veta de la fusta
        f.shade(x, y, -0.5)


def clau_cambra(f):
    """Clau antiga de llautó, grossa: ull rodó amb lòbuls, canya llarga, paleta dentada i etiqueta de cartró."""
    # etiqueta penjada de l'ull amb un cordill
    f.line(11, 23, 16, 27, CLOTH, 2.8)
    f.line(12, 23, 17, 27, CLOTH, 1.8)
    T = f.P([(15, 25), (31, 25), (31, 33), (15, 33)])
    paper(f, T, MANI, 4.0)
    f.ring(17.5, 29, 1.2, 1.2, MANI, 1.2)
    f.rect(20, 27, 29, 27, STAMP, 2.4)
    f.text(20, 29, '9', INKG, 1.4)                                       # el número de la cambra
    f.rect(24, 31, 28, 31, INKG, 1.6)
    # ull: anella gruixuda amb tres lòbuls
    pix = f.ell(11, 13, 8.2, 8.2, BRASS, 3.8, amp=2.6)
    f.shine(pix, 0.8, 1.6)
    for p in f.E(11, 13, 3.5, 3.5):
        f.erase(*p)
    for (x, y) in f.E(11, 13, 4.8, 4.8) - f.E(11, 13, 3.5, 3.5):
        f.shade(x, y, 1.2 if x + y > 24 else -1.4)
    for (x, y) in ((11, 5), (11, 6), (3, 13), (4, 13), (11, 21), (11, 20)):
        f.shade(x, y, -1.4)
    # canya i collar
    pix = f.limb((19, 13), (53, 13), 2.4, 2.4, BRASS, 4.0, amp=2.4)
    f.shine(pix, 0.85, 1.6)
    for x, l in ((21, 5.0), (22, 3.6), (24, 2.2), (25, 3.6)):
        f.rect(x, 9, x, 17, BRASS, l)
    # paleta amb les dents
    f.rect(47, 15, 57, 25, BRASS, lambda x, y: 4.2 - (x - 47) * 0.13 - (y - 15) * 0.1, rim=(0.6, -1.0))
    for x, y in ((49, 21), (49, 22), (49, 23), (49, 24), (49, 25), (50, 25), (50, 24),
                 (53, 23), (53, 24), (53, 25), (54, 25), (56, 20), (57, 20), (57, 21), (56, 21)):
        f.erase(x, y)
    for x, y in ((48, 21), (52, 23), (55, 20)):
        f.shade(x, y, -1.0)
    f.ell(56, 13, 2.9, 2.9, BRASS, 3.8, amp=2.0)


def llapis(f):
    """Llapis de fàbrica (pintat d'ocre) amb la punta afilada, la marca impresa i el cul ben mossegat."""
    a, b = (7, 8), (45, 25)
    pix = f.limb(a, b, 2.9, 2.9, SUNY, 2.9, amp=2.0)
    f.shine(pix, 0.84, 1.0)
    # arestes de l'hexàgon: una ratlla clara i una de fosca al llarg
    for i in range(42):
        t = i / 41
        x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        f.shade(round(x + 0.8), round(y - 1.7), 0.8)
        f.shade(round(x - 0.5), round(y + 1.5), -0.6)
    # la marca impresa: dues ratlletes fosques al mig
    for t in (0.40, 0.44, 0.48, 0.56, 0.60):
        x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        f.px(round(x), round(y), SUNY, 1.2)
    # punta: fusta tallada i grafit
    tip = f.limb(b, (56, 31), 2.9, 0.8, PALE, 3.6, amp=1.6)
    for (x, y) in list(tip):
        if x >= 47 and hr(x, y, 4) > 0.6:
            f.shade(x, y, -0.6)
    f.limb((53, 29), (59, 32), 1.2, 0.6, GRAPH, 2.0, amp=1.4)
    f.px(59, 32, GRAPH, 3.0)
    # cul mossegat: mossos i la fusta que queda al descobert
    for x, y in ((4, 7), (5, 4), (6, 4), (7, 4), (4, 9), (8, 5), (3, 8), (5, 11), (4, 10)):
        f.erase(x, y)
    for x, y in ((5, 5), (6, 5), (7, 5), (5, 6), (4, 8), (5, 9), (5, 10), (8, 6), (9, 5), (6, 11)):
        if f.get(x, y):
            f.px(x, y, PALE, 3.2 + hr(x, y) * 1.4)
    for x, y in ((12, 8), (14, 9), (11, 12), (15, 12)):                  # marques de dents
        f.px(x, y, SUNY, 1.2)


def llibreta_torn(f):
    """Llibreta de torn de l'Iri: tapes de pell marró, cantell de fulls, goma vermella i etiqueta «TORN»."""
    x0, y0, x1, y1 = 17, 2, 46, 29
    pages = f.R(x0 + 3, y0 + 3, x1 + 3, y1 + 3)                          # cantell dels fulls (gruix)
    f.fill(pages, PAP_C, lambda x, y: 3.4 - (0.9 if (x + y) % 2 and x > x1 else 0) - (0.9 if y > y1 and x % 2 else 0))
    f.rect(x1 + 3, y0 + 4, x1 + 3, y1 + 3, LEATH, 2.0)
    f.rect(x0 + 4, y1 + 3, x1 + 3, y1 + 3, LEATH, 2.0)
    # tapa
    C = f.R(x0, y0, x1, y1) - {(x0, y0), (x1, y0), (x0, y1), (x1, y1)}
    f.drop(C)
    f.fill(C, LEATH, lambda x, y: 3.6 - (x - x0) / 29 * 0.9 - (y - y0) / 29 * 0.9 + (hr(x, y, 2) - 0.5) * 0.5,
           rim=(0.9, -1.0))
    for (x, y) in C:                                                     # el gra de la pell
        if hr(x, y, 31) > 0.9:
            f.shade(x, y, -0.5)
    # llom, amb el pespunt
    f.rect(x0, y0 + 1, x0 + 3, y1 - 1, LEATH, lambda x, y: 2.4 + (0.9 if x == x0 + 1 else 0))
    for y in range(y0 + 2, y1 - 1, 2):
        f.px(x0 + 3, y, CLOTH, 2.4)
    # etiqueta
    f.rect(x0 + 7, y0 + 6, x0 + 25, y0 + 15, PAP_C, 4.4, rim=(0.4, -1.2))
    f.text(x0 + 7 + (19 - text_w('TORN')) // 2, y0 + 8, 'TORN', INKG, 0.6, font=FONT46)
    f.rect(x0 + 9, y0 + 15 - 1, x0 + 23, y0 + 15 - 1, RULE, 1.4)
    # goma elàstica vermella
    f.rect(x1 - 6, y0, x1 - 5, y1 + 3, RED, lambda x, y: 3.6 if x == x1 - 6 else 2.4)
    f.px(x1 - 6, y0, RED, 4.6)
    f.shade(x1 - 4, y0 + 1, -1.0)


def caixa_eines(f):
    """Caixa d'eines de fusta pintada de vermell, cantoneres de ferro amb reblons, nansa i eines que sobresurten."""
    X0, X1, T, B = 7, 57, 15, 32
    # eines (darrere)
    f.rect(15, 5, 17, 15, WOOD, lambda x, y: 4.2 - (x - 15) * 0.8)                # mànec del martell
    f.rect(11, 3, 23, 6, F9, lambda x, y: 5.2 - (y - 3) * 0.7, rim=(0.6, -1.0))   # cap del martell
    f.rect(11, 3, 12, 4, F9, 3.2)                                                  # l'orella
    f.erase(11, 3)
    f.limb((44, 14), (47, 5), 1.3, 1.3, F9, 4.0, amp=2.2)                          # clau anglesa
    f.ell(47.5, 4.5, 2.9, 2.1, F9, 4.2, amp=2.0)
    f.erase(48, 3); f.erase(48, 4)
    f.rect(51, 8, 56, 12, WOOD, lambda x, y: 4.0 - (x - 51) * 0.35, rim=(0.6, -1.0))  # mànec de serra
    f.rect(53, 9, 54, 10, WOOD, 1.0)
    f.erase(53, 9); f.erase(54, 9)
    # nansa de ferro
    for x in range(X0 + 5, X1 - 4):
        f.px(x, 9, IRON, 4.0)
        f.px(x, 10, IRON, 2.2)
    for xx in (X0 + 5, X1 - 5):
        f.rect(xx, 9, xx + 1, T - 1, IRON, lambda x, y, xx=xx: 3.6 if x == xx else 2.0)
    f.rect(25, 8, 39, 11, WOOD, lambda x, y: 4.4 - (y - 8) * 0.7, rim=(0.4, -0.8))
    # cos: taulons vermells
    S = f.R(X0, T, X1, B)
    f.drop(S)
    f.fill(S, RED, lambda x, y: 3.0 - (x - X0) / (X1 - X0) * 0.9 - (y - T) * 0.03 - (0.9 if (y - T) % 6 == 5 else 0)
           + (0.4 if (y - T) % 6 == 0 else 0) + (hr(x // 4, y // 2, 4) - 0.5) * 0.3, rim=(0.9, -1.1))
    for (x, y) in S:                                                               # la pintura gastada
        if hr(x, y, 17) > 0.96:
            f.px(x, y, WOOD, 3.4)
    # cantoneres de ferro amb reblons
    for cx in (X0, X1 - 4):
        for cy in (T, B - 4):
            f.rect(cx, cy, cx + 4, cy + 4, IRON, lambda x, y, cx=cx, cy=cy: 4.0 - (y - cy) * 0.25 - (x - cx) * 0.15)
            f.px(cx + 2, cy + 2, IRON, 6.0)
            f.px(cx + 3, cy + 3, IRON, 1.6)
    # placa de llautó, amb dos cargols
    f.rect(25, 20, 39, 26, BRASS, lambda x, y: 4.6 - (x - 25) * 0.1, rim=(0.6, -1.4))
    for x in range(28, 37, 2):
        f.px(x, 23, BRASS, 1.8)
    f.dots([(26, 21), (38, 21)], BRASS, 6.0)


def imant_ferro9(f):
    """Imant de ferradura vermell amb els pols de ferro-9, i el camp que espurneja."""
    cx, cy = 32, 16
    RX, RY, RI = 15.3, 12.8, 0.48
    S = {}
    for y in range(2, 33):
        for x in range(13, 52):
            dx, dy = (x - cx), (y - cy)
            if dy <= 0:
                r = math.hypot(dx / RX, dy / RY)
                if RI <= r <= 1:
                    S[(x, y)] = r
            elif RX * RI <= abs(dx) <= RX and y <= 31:
                S[(x, y)] = abs(dx) / RX
    for (x, y), r in S.items():
        dx = x - cx
        if y <= cy:
            ang = math.atan2(y - cy, dx)
            nx, ny = math.cos(ang), math.sin(ang)
            t = (r - RI) / (1 - RI) * 2 - 1           # -1 dins, 1 fora
            l = 3.0 + 1.6 * (nx * LX * t + ny * LY * t) + (1 - t * t) * 0.8
        else:
            side = 1 if dx > 0 else -1
            t = (abs(dx) - RX * RI) / (RX * (1 - RI)) * 2 - 1
            l = 3.0 - 1.4 * t * side * (-LX) * side - (0.8 if dx > 0 else 0) + (1 - t * t) * 0.8
        mat = F9 if y >= 25 else RED
        if mat is F9:
            l += 1.8
            if y == 31:
                l -= 1.0                              # la cara dels pols
        f.px(x, y, mat, l)
    for x in range(13, 52):                           # ratlla de separació entre el vermell i el ferro-9
        f.shade(x, 25, -1.2)
        f.shade(x, 24, -0.4)
    # reflex
    for x, y in ((20, 8), (21, 7), (22, 6), (23, 5), (19, 9), (18, 11), (18, 12)):
        f.shade(x, y, 1.6)
    # espurnes del camp magnètic entre els pols
    for x, y in ((28, 31), (32, 32), (36, 31), (8, 29), (56, 29), (9, 25), (55, 25), (30, 34), (34, 34)):
        f.px(x, y, CYAN, 3.4)
    for x, y in ((32, 30), (7, 27), (57, 27)):
        f.px(x, y, CYAN, 4.4)


def nota_iri(f):
    """Full arrencat de la llibreta de l'Iri: crema, ratllat de blau, vora esquinçada i lletra de llapis."""
    S = torn(f.R(20, 2, 45, 33), 'l', seed=11, depth=2)
    paper(f, S, PAP_C, 4.0, w=26, h=32)
    for y in range(6, 33, 4):
        for x in range(22, 45):
            if (x, y) in S:
                f.px(x, y, RULE, 1.4)
    for y in range(3, 33):
        f.px(24, y, PINK, 2.6)                          # marge
    for i, y in enumerate(range(5, 25, 4)):
        f.scrib(26, 43 - (6 if i == 4 else 0), y, GRAPH, 1.0, seed=i + 20, tall=0.25)
    f.text(36, 25, 'I.', GRAPH, 0.6, font=FONT46)
    f.rect(30, 30, 35, 30, GRAPH, 1.0)
    f.px(36, 29, GRAPH, 1.0)


def avis_reciclatge(f):
    """Avís oficial de la MARE: full blanc amb capçalera rosa i el cor, text imprès, un somriure i el «3»."""
    S = f.R(19, 2, 45, 33)
    paper(f, S, PAP_W, 4.2, w=27, h=32)
    f.rect(20, 3, 44, 10, PINK, lambda x, y: 3.2 + (0.8 if y == 3 else 0) - (0.6 if y == 10 else 0))
    heart = ('.##.##.', '#######', '#######', '.#####.', '..###..', '...#...')
    for j, row in enumerate(heart):
        for i, c in enumerate(row):
            if c == '#':
                f.px(21 + i, 4 + j, PAP_W, 6.0)
    f.text(30, 5, 'MARE', PAP_W, 5.4)
    for y in (13, 16, 19):
        f.scrib(21, 43, y, INKG, 1.6, seed=y, dens=0.9, tall=0)
    # el «3» en rosa, gros, dins una caixa
    f.rect(21, 21, 31, 31, PINK, 1.6)
    f.rect(22, 22, 30, 30, PAP_W, 5.0)
    three = ('#####.', '#####.', '....##', '.####.', '.####.', '....##', '#####.', '####..')
    for j, row in enumerate(three):
        for i, c in enumerate(row):
            if c == '#':
                f.px(23 + i, 22 + j, PINK, 1.4)
    # somriure imprès
    f.ell(38, 26, 5.0, 5.0, SUNY, 3.4, amp=1.4)
    f.dots(((36, 24), (36, 25), (40, 24), (40, 25), (35, 27), (36, 28), (37, 29), (38, 29), (39, 29), (40, 28),
            (41, 27)), SUNY, 0.6)


# Lletres i xifres grosses de llapis d'ulls, a mà (la mida de la clau a nota_mida, «VET» a nota_vet_nom)
BIG640 = {
    '6': ('.####.', '##....', '##....', '#####.', '##..##', '##..##', '##..##', '##..##', '.####.'),
    '½': ('.#.....', '##....#', '.#...#.', '.#..#..', '...#...', '..#.##.', '.#...##', '#...##.', '....###'),
    'V': ('###...###', '###...###', '.##...##.', '.###.###.', '..##.##..', '..#####..', '...###...', '...###...',
          '....#....'),
    'E': ('#######', '###....', '###....', '######.', '###....', '###....', '###....', '#######'),
    'T': ('#########', '#########', '...###...', '...###...', '...###...', '...###...', '...###...', '...###...'),
}


def llapis_ulls(f):
    """Llapis d'ulls d'en Mos: negre lluent, lletres platejades, el clip i el caputxó rosa."""
    a, b = (8, 28), (39, 12)
    pix = f.limb(a, b, 2.3, 2.3, KOHL, 1.6, amp=1.8)
    f.shine(pix, 0.8, 1.6)
    for t in (0.30, 0.36, 0.42, 0.48, 0.54, 0.60):                   # la marca, en lletres platejades
        x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        f.px(round(x), round(y), STEEL, 6.0 if t != 0.48 else 4.6)
    f.limb((5, 29.5), (8, 28), 2.2, 2.2, STEEL, 4.0, amp=2.0)        # el tap del cul
    f.px(5, 28, STEEL, 6.4)
    f.limb((37.5, 12.4), (40.5, 10.9), 2.5, 2.5, STEEL, 4.4, amp=2.0)  # la virolla, amb dues estries
    f.shade(39, 11, -1.0)
    f.shade(39, 13, -1.0)
    pix = f.limb((42, 10.3), (53, 4.6), 2.8, 2.8, PINK, 3.0, amp=2.0)  # el caputxó rosa
    f.shine(pix, 0.82, 1.4)
    f.line(44, 12, 51, 8.5, STEEL, 5.0)                              # el clip
    f.px(52, 8, STEEL, 3.6)
    f.dots([(47, 6), (48, 6)], PINK, 5.4)
    for x in range(18, 36):                                          # una ratlla de prova, a sota
        y = 31 + round(math.sin(x / 2.6) * 0.8)
        f.px(x, y, KOHL, 1.0 if hr(x, 4) > 0.2 else 2.0)
        if x % 5 == 0:
            f.px(x, y + 1, KOHL, 1.8)


def nota_vet(f):
    """L'avís de reciclatge pel darrere: lletra grossa de llapis d'ulls, el cantó rosa girat i un «9»."""
    S = f.R(17, 2, 46, 32)
    S -= {(x, y) for (x, y) in S if (x - 37) + (y - 24) > 8}
    paper(f, S, PAP_W, 4.2, w=29, h=30)
    F = f.P([(37, 24), (47, 24), (37, 34)])                          # el cantó doblegat: el rosa del davant
    f.drop(F, -1.4, -1, -1)
    f.fill(F, PINK, lambda x, y: 3.0 - (y - 24) * 0.12, rim=(0.6, -0.8))
    for i, y in enumerate((6, 11, 16)):                               # la lletra de llapis d'ulls, gruixuda
        f.scrib(20, 43 - i * 4, y, KOHL, 1.0, seed=40 + i, dens=0.95, tall=0.35)
        f.scrib(20, 42 - i * 4, y + 1, KOHL, 1.4, seed=50 + i, dens=0.75, tall=0)
        f.scrib(20, 41 - i * 4, y + 2, KOHL, 2.2, seed=60 + i, dens=0.3, tall=0)
    f.text(21, 22, '9', KOHL, 0.8, font=FONT46)                       # el «9» de la signatura, repassat
    f.text(22, 22, '9', KOHL, 0.8, font=FONT46)
    f.rect(28, 29, 34, 29, KOHL, 1.2)
    f.px(35, 28, KOHL, 1.6)


def _aldaia_face640(f, x, y):
    """Retrat petit del Director Aldaia (cabells grisos pentinats, vestit fosc, corbata vermella, somriure)."""
    f.rect(x, y + 9, x + 10, y + 12, SUIT, lambda xx, yy: 2.8 - (xx - x) * 0.15)
    f.dots([(x + 4, y + 9), (x + 6, y + 9), (x + 4, y + 10)], PAP_W, 5.0)
    f.dots([(x + 5, y + 9), (x + 5, y + 10), (x + 5, y + 11)], RED, 3.0)
    f.ell(x + 5, y + 4.6, 3.4, 3.9, SKIN, 3.4, amp=1.6)
    f.rect(x + 2, y, x + 8, y + 1, HAIRG, lambda xx, yy: 3.8 - (xx - x) * 0.25)
    f.dots([(x + 1, y + 1), (x + 1, y + 2), (x + 1, y + 3)], HAIRG, 2.6)
    f.dots([(x + 9, y + 1), (x + 9, y + 2), (x + 9, y + 3)], HAIRG, 2.0)
    f.px(x + 4, y, HAIRG, 5.0)                                       # la clenxa
    f.dots([(x + 3, y + 4), (x + 7, y + 4)], DARK, 1.0)
    f.dots([(x + 3, y + 6), (x + 7, y + 6)], RED, 2.6)
    f.dots([(x + 4, y + 7), (x + 5, y + 7), (x + 6, y + 7)], RED, 1.6)


def fullet_reeducacio(f):
    """Fullet tríptic lluent, mig obert en ziga-zaga: portada amb el Director, el cor de la MARE i franges de colors."""
    panels = [((7, 7), (23, 4), (23, 31), (7, 28), TEAL, 3.0),
              ((23, 4), (40, 8), (40, 32), (23, 31), PAP_W, 3.4),
              ((40, 8), (57, 4), (57, 31), (40, 32), PAP_W, 4.4)]
    for (a, b, c, d, mat, base) in panels:
        S = f.P([a, (b[0] + 1, b[1]), (c[0] + 1, c[1] + 1), (d[0], d[1] + 1)])
        f.drop(S)
        f.fill(S, mat, base, rim=(0.6, -1.0))
    # panell esquerre (interior turquesa): un títol, text blanc i un cor
    f.rect(9, 9, 18, 10, PAP_W, 5.0)
    for y in (13, 16, 19, 22):
        f.scrib(9, 21, y, PAP_W, 4.4, seed=y, dens=0.9, tall=0)
    f.dots([(10, 25), (12, 25), (9, 26), (10, 26), (11, 26), (12, 26), (13, 26), (10, 27), (11, 27), (12, 27),
            (11, 28)], PINK, 3.8)
    # panell del mig (a l'ombra): franja rosa i ratlles
    f.fill(f.P([(24, 5), (41, 9), (41, 13), (24, 9)]), PINK, 2.6, rim=None)
    for y in (16, 20, 24, 28):
        for x in range(25, 39):
            f.px(x, y - 1 + round((x - 23) * 4 / 17), INKG, 2.0 if hr(x, y) > 0.2 else 3.0)
    # portada: franja amb el títol, el Director somrient i el cor
    f.fill(f.P([(41, 9), (58, 5), (58, 11), (41, 15)]), TEAL, 2.8, rim=None)
    for x in range(43, 56):
        f.px(x, 11 - round((x - 41) * 4 / 17), PAP_W, 5.0 if x % 4 else 3.6)
    _aldaia_face640(f, 43, 15)
    for x, y in ((53, 22), (55, 22), (52, 23), (53, 23), (54, 23), (55, 23), (56, 23), (53, 24), (54, 24), (55, 24),
                 (54, 25)):
        f.px(x, y, PINK, 3.6)
    f.px(53, 22, PINK, 5.0)
    for x in range(43, 56, 2):                                       # el peu de la portada
        f.px(x, 29 - round((x - 41) * 4 / 17), INKG, 2.6)
    for i in range(8):                                               # la lluentor del paper satinat
        f.shade(47 + i, 30 - i * 3, 0.8)


def nota_pany(f):
    """El fullet desplegat pel darrere: blanc, amb els plecs, i el pany M-3 dibuixat amb llapis d'ulls."""
    S = f.R(5, 4, 59, 31)
    paper(f, S, PAP_W, 4.0, w=54, h=27)
    f.rect(5, 4, 59, 4, TEAL, 3.4)                                   # les vores de colors del davant
    f.rect(5, 31, 59, 31, PINK, 2.6)
    for x in (23, 41):                                               # els plecs
        f.rect(x, 5, x, 30, PAP_W, 2.6)
        f.rect(x + 1, 5, x + 1, 30, PAP_W, 5.0)
    K, L = KOHL, 1.0
    for i in range(30):                                              # l'arc del pany
        a = math.pi * i / 29
        x, y = 30 - 5.5 * math.cos(a), 14 - 6 * math.sin(a)
        f.px(x, y, K, L)
        f.px(x + 0.8 * math.cos(a), y + 0.9 * math.sin(a), K, L + 0.8)
    f.rect(21, 14, 39, 28, K, L)                                     # el cos
    f.rect(22, 15, 38, 27, PAP_W, 4.4)
    f.text(25, 17, 'M-3', K, 1.2, font=FONT46, sp=1)
    f.dots(((29, 23), (30, 23), (29, 24), (30, 24), (29, 25), (30, 26), (29, 26)), K, 1.2)   # el forat de la clau
    for i, y in enumerate((9, 13, 17, 21)):                          # les notes del costat
        f.scrib(8, 19 - (i % 2) * 2, y, K, 1.4, seed=2 + i, dens=0.9, tall=0.2)
    for i, y in enumerate((9, 13)):
        f.scrib(44, 56 - i * 2, y, K, 1.4, seed=7 + i, dens=0.9, tall=0.2)
    f.text(48, 17, '?', K, 1.0, font=FONT46)                         # l'interrogant
    f.text(9, 24, 'V.', K, 1.0, font=FONT46, sp=0)


def escarabat(f):
    """El Senyor Bigotis: escarabat marró lluent amb les antenes arrissades com un bigoti."""
    cx, cy = 39, 18
    for k in (-8, 0, 8):                                             # les potes, amb el colze
        f.line(cx + k, cy + 6, cx + k - 2, cy + 11, BEET, 1.4)
        f.line(cx + k - 2, cy + 11, cx + k - 4, cy + 14, BEET, 1.0)
        f.line(cx + k, cy - 6, cx + k - 2, cy - 11, BEET, 1.8)
        f.line(cx + k - 2, cy - 11, cx + k - 4, cy - 14, BEET, 1.4)
    pix = f.ell(cx, cy, 17, 10.6, BEET, 3.4, amp=2.6)
    f.shine(pix, 0.75, 1.8)
    for x in range(cx - 8, cx + 17):
        f.shade(x, cy, -1.4)                                         # la separació dels èlitres
    for sgn in (-1, 1):                                              # les estries dels èlitres
        for x in range(cx - 4, cx + 14, 2):
            f.shade(x, cy + sgn * 5, -0.5)
    for (x, y) in ((cx + 2, cy - 6), (cx + 3, cy - 6), (cx + 4, cy - 6), (cx + 5, cy - 7), (cx + 6, cy - 7)):
        f.shade(x, y, 1.0)
    pix = f.ell(cx - 13, cy, 5.6, 7.2, BEET, 2.6, amp=2.2)            # el pronot
    f.shine(pix, 0.82, 1.4)
    f.ell(cx - 20, cy, 3.7, 4.0, BEET, 2.2, amp=1.8)                 # el cap
    f.dots([(cx - 22, cy - 2), (cx - 22, cy + 2)], PAP_W, 6.0)       # els ulls
    for sgn in (-1, 1):                                              # el bigoti: dues antenes arrissades
        pts = [(cx - 23, cy + sgn * 2), (cx - 25, cy + sgn * 5), (cx - 28, cy + sgn * 8), (cx - 31, cy + sgn * 9),
               (cx - 34, cy + sgn * 9), (cx - 35, cy + sgn * 8), (cx - 35, cy + sgn * 6), (cx - 33, cy + sgn * 5)]
        for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
            f.line(xa, ya, xb, yb, BEET, 2.0)


def sopa(f):
    """Bol de plàstic de presó amb sopa de reinserció verda que fa bombolles soles, i la cullera."""
    cx = 28
    f.limb((40, 16), (57, 5), 1.3, 1.6, PLAST, 4.2, amp=1.6)         # la cullera (darrere)
    body = {}
    for y in range(15, 32):
        t = (y - 15) / 16
        half = 20.6 - t ** 1.6 * 10.6
        for x in range(round(cx - half), round(cx + half) + 1):
            u = (x - cx) / half
            body[(x, y)] = (u, 0.3, math.sqrt(max(0, 1 - u * u)))
    f.drop(set(body))
    for (x, y), (nx, ny, nz) in body.items():
        f.px(x, y, PLAST, 3.6 + 2.0 * (nx * LX + ny * LY + nz * LZ - 0.35) - (y - 15) * 0.05)
    f.shine(body, 0.6, 0.9)
    for x in range(cx - 18, cx + 19):                                # el filet de sota la vora
        f.shade(x, 19 + round(abs(x - cx) / 20), -0.6)
    f.rect(cx - 8, 32, cx + 8, 32, PLAST, 1.6)                       # el peu
    f.ell(cx, 15, 20.6, 4.8, PLAST, 5.0, amp=0.8)                    # la vora i la sopa
    f.ell(cx, 15.3, 18.2, 3.5, LIME, 3.0, amp=0.0, lvlfn=lambda x, y: (x - cx) * -0.03 + (y - 15) * 0.3)
    for x, y, r in ((cx - 8, 15, 1.8), (cx + 3, 14, 2.4), (cx + 10, 16, 1.3), (cx - 1, 16, 1.3), (cx - 13, 14, 1.0)):
        f.ell(x, y, r, r * 0.8, LIME, 4.4, amp=1.0)
    f.limb((cx + 12, 14), (40, 16), 1.0, 1.3, PLAST, 4.6, amp=1.4)   # el mànec, que surt del bol
    for x, y, r in ((cx - 4, 8, 2.1), (cx + 5, 5, 1.8), (cx + 1, 1.5, 1.1)):   # les bombolles que pugen
        f.ell(x, y, r, r, LIME, 3.6, amp=1.6)
        if r > 1.5:
            f.erase(x, y)
        f.px(x - 1, y - 1, LIME, 5.4)


def _cartell_tros(seed=3):
    return torn(Ic640.P([(8, 4), (53, 3), (57, 29), (11, 32)]), 'lrtb', seed=seed, depth=1)


def tros_cartell(f):
    """Tros arrencat del cartell del reciclatge: capçalera verda amb lletres, i mig somriure groc."""
    S = _cartell_tros()
    paper(f, S, SIGN, 4.0, w=49, h=29)
    head = {(x, y) for (x, y) in S if y <= 12 - (x - 8) * 0.03}
    f.fill(head, CORPG, 2.6, rim=(0.6, 0))
    f.rect(9, 13, 55, 13, CORPG, 1.6)
    f.text(12, 5, 'CICLA', SIGN, 5.0, font=FONT46)
    pix = [p for p in f.E(49, 23, 9.3, 9.3) if p in S]                # mig somriure groc, tallat per l'esquinçada
    for (x, y) in pix:
        f.px(x, y, SUNY, 3.6 - (x - 49) * 0.08 - (y - 23) * 0.1 + (0.6 if (x - 44) ** 2 + (y - 18) ** 2 < 5 else 0))
    f.dots(((45, 19), (45, 20), (46, 19), (46, 20), (52, 19), (52, 20), (53, 19), (53, 20)), KOHL, 1.0)
    for i in range(13):
        a = math.pi * (0.15 + 0.7 * i / 12)
        f.px(round(49 - 6 * math.cos(a)), round(23 + 5 * math.sin(a)), KOHL, 1.0)
    f.rect(12, 17, 30, 18, SIGN, 2.6)                                # les ratlles de text del cartell
    f.rect(12, 21, 25, 21, SIGN, 2.6)
    f.rect(12, 24, 28, 24, SIGN, 2.8)
    f.rect(14, 27, 21, 28, PAP_W, 5.4, rim=(0.4, -0.6))              # un tros de cinta adhesiva


def nota_mida(f):
    """El tros de cartell pel darrere, amb la mida en gros: «6½» claus angleses, i una clau dibuixada."""
    S = _cartell_tros()
    scrap_cartell(f, S, 3)
    f.text(13, 7, '6', KOHL, 0.8, font=BIG640)
    f.text(21, 7, '½', KOHL, 0.8, font=BIG640)
    f.dots(((31, 13), (33, 13), (32, 14), (31, 15), (33, 15)), KOHL, 1.2)   # «×»
    for x in range(38, 53):                                          # la clau anglesa dibuixada
        y = 21 - (x - 38) * 0.35
        f.px(x, y, KOHL, 1.0)
        f.px(x, y + 1, KOHL, 1.8)
    f.dots(((36, 21), (35, 20), (35, 23), (36, 24), (37, 23)), KOHL, 1.2)
    f.dots(((54, 15), (55, 14), (55, 17), (56, 16), (53, 16)), KOHL, 1.2)
    for x in range(14, 53):                                          # la fletxa de mida, a sota
        f.px(x, 27, KOHL, 1.6)
    f.dots(((15, 26), (15, 28), (52, 26), (52, 28), (14, 25), (14, 29), (53, 25), (53, 29)), KOHL, 1.4)


# ─── Acte 2: bigues ─────────────────────────────────────────────────────────

def biga_acer(f):
    """Biga d'acer gris de dos metres, en I, amb marques de guix."""
    beam(f, 10, 61, 11, ACER, 3.7)
    for x in range(18, 61, 11):                                      # les marques de guix, cada mig metre
        f.rect(x, 16, x, 20, PAP_F, 4.0 - (0.6 if hr(x, 1) > 0.5 else 0))
        f.px(x + 1, 17, PAP_F, 2.8)


def biga_ferro9(f):
    """Biga de ferro-9: el mateix perfil, d'acer blavós lluent, amb reflexos i l'etiqueta de la caldera."""
    beam(f, 10, 61, 8, F9, 4.0, sheen=0.35)
    for i in range(4):
        f.rect(15 + i * 12, 9, 21 + i * 12, 9, F9, 8.0)
        f.rect(16 + i * 12, 18, 20 + i * 12, 18, F9, 5.0)
    f.line(35, 23, 36, 26, CLOTH, 3.0)                               # l'etiqueta de cartró, amb un cordill
    T = f.R(29, 26, 46, 33)
    paper(f, T, MANI, 4.0, w=17, h=7)
    f.fill(f.E(31, 28, 1.0, 1.0), IRON, 1.0, rim=None)
    f.rect(33, 28, 44, 28, RED, 2.6)
    f.scrib(33, 44, 31, INKB, 1.6, seed=21, dens=0.9, tall=0.3)


def serra(f):
    """Serra de metall: arc de ferro, fulla dentada lluent i mànec de fusta de pistola."""
    f.rect(5, 5, 48, 7, IRON, lambda x, y: (4.4, 3.4, 2.4)[y - 5])   # l'arc
    f.rect(5, 5, 8, 23, IRON, lambda x, y: 4.2 - (x - 5) * 0.7)
    f.rect(45, 5, 48, 20, IRON, lambda x, y: 3.6 - (x - 45) * 0.7)
    f.dots([(6, 23), (7, 23)], IRON, 5.0)
    f.rect(19, 3, 21, 4, IRON, 3.6)                                  # el tensor
    f.px(20, 2, IRON, 3.0)
    for x in (6, 46):                                                # els passadors de la fulla
        f.px(x + 1, 20, BRASS, 4.6)
    for x in range(8, 46):                                           # la fulla
        f.px(x, 19, ACER, 6.4)
        f.px(x, 20, ACER, 4.6)
        f.px(x, 21, ACER, 3.8)
        f.px(x, 22, ACER, 3.0 if x % 2 else 1.6)
        if x % 2 == 0:
            f.px(x, 23, ACER, 2.2)
    S = f.P([(45, 13), (56, 13), (61, 29), (53, 31), (48, 21), (45, 21)])   # el mànec de pistola
    f.drop(S)
    f.fill(S, WOOD, lambda x, y: 4.4 - (x - 45) * 0.14 - (y - 13) * 0.04 + (0.4 if (x + y * 3) % 7 == 0 else 0),
           rim=(0.8, -1.0))
    for (x, y) in f.P([(50, 17), (55, 17), (56, 24), (53, 24)]):
        f.erase(x, y)
    f.dots([(49, 16), (56, 27)], BRASS, 4.6)
    f.dots([(50, 16), (57, 27)], BRASS, 2.8)


def tram_biga(f, n):
    """Un terç de biga: biga curta tallada, forats per cargolar-la i el número pintat."""
    holes = {1: 'r', 2: 'lr', 3: 'l'}[n]
    beam(f, 19, 53, 8, ACER, 3.5)
    for side in holes:
        x = 21 if side == 'l' else 50
        for y in (13, 17):
            f.dots([(x, y), (x + 1, y), (x, y + 1)], DARK, 0.2)
            f.px(x + 1, y + 1, DARK, 1.0)
            f.px(x + 2, y + 2, ACER, 5.0)
    f.rect(32, 12, 40, 19, SUNY, 2.8, rim=(0.6, -0.8))               # el número, pintat de groc
    f.text(35 if n != 1 else 35, 13, str(n), KOHL, 1.0, font=FONT46)
    for i in range(3):                                               # l'etiqueta amb els trossos (■ □ □)
        on = (i + 1) == n
        x0 = 20 + i * 9
        f.rect(x0, 26, x0 + 5, 31, SUNY if on else ACER, 3.8 if on else 3.6, rim=(0.8, -0.8))
        if not on:
            f.rect(x0 + 1, 27, x0 + 4, 30, DARK, 0.6)


def tram_biga_1(f):
    tram_biga(f, 1)


def tram_biga_2(f):
    tram_biga(f, 2)


def tram_biga_3(f):
    tram_biga(f, 3)


def biga_muntada(f):
    """Tres trams cargolats: biga llarga amb dues juntes, platines i femelles."""
    beam(f, 10, 61, 8, ACER, 3.5)
    for jx in (27, 44):
        f.rect(jx, 8, jx, 22, DARK, 0.8)                             # la junta
        f.rect(jx - 4, 9, jx + 4, 21, ACER, lambda x, y, jx=jx: 5.0 - (x - jx + 4) * 0.22 - (y - 9) * 0.1,
               rim=(0.8, -1.4))
        for bx in (jx - 3, jx + 2):
            for by in (11, 17):
                f.rect(bx, by, bx + 1, by + 1, IRON, 3.0)
                f.px(bx, by, IRON, 5.6)
                f.px(bx + 1, by + 1, IRON, 1.4)
    for x, ch in ((14, '1'), (34, '2'), (51, '3')):
        f.text(x, 27, ch, SUNY, 4.0, font=FONT46)


def nota_amagatall(f):
    """Full de la llibreta de l'Iri, plegat en apaisat: un croquis amb el pilar 7, la reixa i una creu."""
    S = torn(f.R(7, 5, 58, 31), 't', seed=5, depth=1)
    paper(f, S, PAP_C, 4.0, w=51, h=26)
    for y in range(9, 31, 4):                                            # el ratllat
        for x in range(8, 58):
            if (x, y) in S:
                f.px(x, y, RULE, 1.4)
    for y in range(6, 31):
        f.px(32, y, PAP_C, 2.6)                                          # el plec
        f.px(33, y, PAP_C, 5.0)
    # el pilar amb el 7, i el capitell
    f.rect(12, 8, 19, 28, GRAPH, 1.2)
    f.rect(13, 9, 18, 27, PAP_C, 4.2)
    f.rect(11, 8, 20, 8, GRAPH, 1.0)
    f.text(14, 13, '7', GRAPH, 0.6, font=FONT46)
    for y in range(20, 27, 2):                                           # l'ombrejat del pilar, a ratlles
        f.px(17, y, GRAPH, 2.4)
        f.px(16, y + 1, GRAPH, 2.6)
    f.rect(10, 28, 21, 28, GRAPH, 1.0)
    # la reixa al costat, amb la creu a sobre
    for x in range(23, 30):
        for y in range(22, 29):
            if x in (23, 29) or y in (22, 28) or x % 2 == 1:
                f.px(x, y, GRAPH, 1.0)
    f.dots(((24, 15), (25, 16), (26, 17), (27, 18), (28, 17), (29, 16), (30, 15)), GRAPH, 1.4)   # la fletxa
    f.dots(((25, 18), (27, 16), (26, 19), (28, 19)), GRAPH, 2.2)
    f.dots(((26, 10), (27, 11), (28, 12), (28, 10), (26, 12)), STAMP, 1.6)                      # la creu, vermella
    # la lletra
    for i, y in enumerate((9, 13, 17, 21)):
        f.scrib(37, 55 - i * 3, y - 1, GRAPH, 1.0, seed=60 + i)
    f.text(48, 23, 'I.', GRAPH, 0.6, font=FONT46, sp=0)


def pols_rovell(f):
    """Un pilot de pols de rovell, amb escates i un tros de l'ala de la biga que s'esmicola."""
    for y in range(10, 33):
        for x in range(3, 62):
            dx = (x - 32) / 28
            top = 31 - 17 * max(0, 1 - dx * dx) ** 1.3
            if y < top + (hr(x, 2) - 0.5) * 2.0:
                continue
            l = 3.4 - (y - top) * 0.11 - dx * 0.8 + (hr(x, y, 1) - 0.5) * 1.6
            if y >= 32:
                l -= 1.2
            f.px(x, y, RUST, l)
    # escates i grans clars, i alguns de foscos
    for i in range(34):
        x, y = 10 + int(hr(i, 3) * 44), 17 + int(hr(i, 4) * 14)
        if f.get(x, y):
            f.px(x, y, RUST, 5.6 if i % 3 else 0.8)
            if i % 5 == 0 and f.get(x + 1, y):
                f.px(x + 1, y, RUST, 4.6)
    for i in range(6):                                                   # grans escampats al voltant
        f.px(4 + int(hr(i, 7) * 56), 33 + (i % 2), RUST, 3.0)
    # el tros de biga rovellat que treu el cap, amb la capa que s'aixeca
    S = f.P([(34, 7), (51, 11), (50, 16), (33, 13)])
    S = torn(S, 'r', seed=2, depth=2)
    f.drop(S)
    f.fill(S, RUST, lambda x, y: 3.6 - (y - 7) * 0.2 + (hr(x, y, 3) - 0.5) * 1.2, rim=(0.8, -1.0))
    f.dots(((41, 10), (45, 11), (39, 12), (47, 13)), RUST, 1.0)          # els forats
    f.dots(((36, 9), (37, 9), (43, 11)), RUST, 5.8)                      # la vora, que encara brilla
    f.dots(((52, 9), (53, 8), (54, 10)), RUST, 4.4)                      # escates que salten


def molla(f):
    """Molla de llitera (espiral d'acer lluent) amb una tira de tela taronja lligada: el missatge per a la I."""
    cy, ry, x0, pitch, turns = 16, 9.6, 9, 7.2, 6.4
    n = 2000
    pts = []
    for i in range(n + 1):
        t = i / n * turns * 2 * math.pi
        pts.append((x0 + pitch * t / (2 * math.pi) + 2.9 * math.cos(t), cy + ry * math.sin(t), math.cos(t), math.sin(t)))
    for x, y, c, sn in pts:                                              # el fil de darrere
        if c <= 0:
            f.px(round(x), round(y), STEEL, 2.4 - sn * 0.7)
    for x, y, c, sn in pts:                                              # el fil de davant, gruixut i lluent
        if c > 0:
            l = 5.2 - sn * 1.5 + c * 0.6
            f.px(round(x), round(y), STEEL, l)
            f.px(round(x) + 1, round(y), STEEL, l - 1.2)
            f.px(round(x) + 2, round(y), STEEL, l - 2.6)
    # els ganxos als caps
    f.line(3, 6, 8, 6, STEEL, 4.8)
    f.line(3, 7, 8, 7, STEEL, 3.2)
    f.line(2, 6, 2, 11, STEEL, 3.6)
    f.line(57, 25, 62, 25, STEEL, 3.4)
    f.line(62, 25, 62, 20, STEEL, 2.8)
    # la tira de tela taronja, lligada amb un nus i dues cues
    S = f.R(30, 3, 33, 29)
    f.drop(S)
    f.fill(S, ORNG, lambda x, y: 3.9 - (x - 30) * 0.4, rim=(0.6, -1.0))
    for y in range(4, 29, 5):                                            # els fils de la trama
        f.shade(31, y, -0.5)
    tails = f.P([(30, 17), (33, 17), (27, 29), (24, 28)]) | f.P([(31, 17), (34, 17), (39, 27), (36, 29)])
    f.drop(tails)
    f.fill(tails, ORNG, lambda x, y: 3.2 - (y - 17) * 0.05, rim=(0.6, -1.0))
    f.ell(32, 16, 3.0, 2.6, ORNG, 3.6, amp=2.0)
    f.px(31, 15, ORNG, 5.4)
    f.dots(((24, 28), (39, 27)), ORNG, 1.6)                              # les cues, esfilagarsades
    f.dots(((31, 5), (32, 6), (31, 8), (32, 9), (31, 10)), KOHL, 2.0)    # les lletres a la tela: «I»
    f.dots(((31, 21), (32, 22), (31, 23), (31, 25), (32, 26)), KOHL, 2.0)


def llima(f):
    """Llima fina: fulla d'acer picada, coll de llautó i mànec de fusta."""
    a, b = (3, 28), (41, 12)
    for i in range(41):                                                  # la fulla, picada en diagonal
        t = i / 40
        x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        w = 1 if i < 5 else 2
        for j in range(-w, w + 1):
            xx, yy = round(x + j * 0.42), round(y + j)
            l = 4.6 - j * 0.8 - (1.0 if (i + 2 * j) % 3 == 0 else 0)
            f.px(xx, yy, ACER, l)
        if i >= 5 and i % 2 == 0:
            f.px(round(x + 0.84), round(y + 2) + 1, ACER, 1.6)           # el cantell de sota, a l'ombra
    f.px(4, 27, ACER, 6.4)
    # el coll, la virola de llautó i el mànec
    f.limb((41, 12), (45, 10.6), 1.3, 1.3, ACER, 3.0, amp=1.4)
    pix = f.limb((45, 10.4), (48, 9.2), 3.0, 3.0, BRASS, 4.0, amp=2.2)
    f.shine(pix, 0.8, 1.2)
    f.line(47, 6.6, 48.6, 11.4, BRASS, 2.4)                              # l'estria de la virola
    pix = f.limb((49.5, 8.8), (60, 4.4), 3.2, 2.6, WOOD, 4.2, amp=2.4)
    f.shine(pix, 0.84, 1.0)
    for k in range(4):                                                   # la veta de la fusta
        x = 51 + k * 2.4
        f.px(x, 8.6 - k + (k % 2), WOOD, 3.0)
    f.px(61, 4, WOOD, 2.6)


def _fork640(f, short=0, broken=False):
    """Diapasó de ferro-9 de costat: dues branques de testa plana, la corba i el peu."""
    ys = (9, 21)
    for k, y in enumerate(ys):
        x0 = 10 + short + (5 if broken and k == 1 else 0)
        for x in range(x0, 41):
            for j, l in ((-1, 6.0), (0, 5.0), (1, 3.6), (2, 2.2)):
                ll = l + (0.7 if (x - x0) % 11 == 3 and j == -1 else 0)
                f.px(x, y + j, F9, ll)
        f.rect(x0, y - 1, x0, y + 2, F9, 6.6)                            # la testa plana
        if broken:
            f.rect(x0, y - 1, x0 + 1, y + 2, F9, 8.0)                    # metall viu, llimat de més
            f.dots(((x0 + 3, y), (x0 + 7, y - 1), (x0 + 6, y + 1), (x0 + 10, y)), F9, 2.0)   # ratllades
    # la corba en U
    for i in range(61):
        t = i / 60 * math.pi
        x = 40 + math.sin(t) * 6.6
        y = 15.5 - math.cos(t) * 5.5
        for r in (-1.5, -0.5, 0.5, 1.5):
            px, py = x + math.sin(t) * r * 0.95, y - math.cos(t) * r * 0.95
            l = 4.6 - r * 1.1 - math.sin(t - 0.6) * 0.8
            f.px(round(px), round(py), F9, l)
    # el peu i la bola
    for x in range(48, 58):
        f.px(x, 14, F9, 6.0)
        f.px(x, 15, F9, 4.6)
        f.px(x, 16, F9, 3.2)
        f.px(x, 17, F9, 2.0)
    f.rect(48, 13, 49, 18, F9, 4.4)                                      # el coll del peu
    pix = f.ell(59, 15.5, 3.0, 3.0, F9, 4.4, amp=2.6)
    f.shine(pix, 0.75, 2.0)


def diapaso(f):
    """Diapasó de ferro-9 net i afinat: brilla, i les ones de so surten suaus, blaves."""
    _fork640(f)
    for k, r in enumerate((2.6, 5.4)):
        for a in range(-60, 61, 4):
            ang = math.radians(180 + a)
            x, y = 7 + math.cos(ang) * r * 0.55, 15.5 + math.sin(ang) * r * 2.2
            f.px(round(x) - k, round(y), CYAN, 3.6 - k * 0.8)
    for x, y in ((20, 8), (33, 20), (21, 20)):                           # els reflexos
        f.px(x, y, F9, 8.0)
        f.px(x + 1, y, F9, 7.0)


def diapaso_espatllat(f):
    """Diapasó llimat de més: branques escurçades i desiguals, llimadures i un xiulet de tetera."""
    _fork640(f, short=7, broken=True)
    for i in range(18):                                                  # les llimadures
        f.px(16 + int(hr(i, 1) * 22), 28 + int(hr(i, 2) * 5), F9, 6.4 if i % 2 else 3.0)
    # les bufades de vapor que surten de les puntes
    for (cx, cy, r) in ((13, 8.5, 3.0), (9, 4.6, 2.4), (6, 11.5, 1.8), (19, 23, 2.4), (14, 26.5, 1.8)):
        f.ell(cx, cy, r, r, STEAM, 2.6, amp=1.4)
    # el xiulet: ratlles grogues en ziga-zaga
    f.dots(((3, 13), (4, 14), (3, 15), (4, 16), (3, 17), (4, 18)), SUNY, 4.6)
    f.dots(((1, 15), (1, 16)), SUNY, 3.4)


def nota_pressio(f):
    """Tros de cartell amb un conducte i un manòmetre dibuixats amb llapis d'ulls, i la fletxa de pressió."""
    S = torn(f.P([(7, 6), (55, 4), (59, 31), (9, 30)]), 'lrtb', seed=9, depth=1)
    scrap_cartell(f, S, 9)
    K = KOHL
    # el conducte: dues ratlles amb un colze
    for x in range(10, 40):
        f.px(x, 17, K, 1.0)
        f.px(x, 23, K, 1.0)
    for y in range(8, 18):
        f.px(35, y, K, 1.0)
        f.px(40, y, K, 1.2)
    f.rect(40, 18, 40, 23, K, 1.0)
    f.dots(((10, 18), (10, 22), (11, 20)), K, 1.8)                       # el tall del tub, a mà
    # el manòmetre, amb les marques i l'agulla al vermell
    f.ring(48, 21, 5.4, 5.4, K, 1.0)
    for a in (200, 250, 300, 350):
        r = math.radians(a)
        f.px(round(48 + 3.8 * math.cos(r)), round(21 + 3.8 * math.sin(r)), K, 1.6)
    f.line(48, 21, 51, 17, K, 1.2)
    f.px(48, 21, K, 0.6)
    f.rect(46, 27, 50, 27, K, 1.2)                                       # el peu del manòmetre
    # les fletxes de pressió dins el conducte
    for x0 in (13, 24):
        f.dots(((x0, 20), (x0 + 1, 20), (x0 + 2, 20), (x0 + 3, 20), (x0 + 4, 20), (x0 + 3, 19), (x0 + 3, 21),
                (x0 + 2, 18), (x0 + 2, 22)), K, 1.6)
    f.text(12, 8, 'P', K, 1.0, font=FONT46)
    f.text(18, 8, '?', K, 1.0, font=FONT46)
    f.text(23, 8, '?', K, 1.4, font=FONT46)


BIGM640 = {   # lletres de 6×9, gruixudes, a mà
    'M': ('##...##', '###.###', '##.#.##', '##.#.##', '##...##', '##...##', '##...##', '##...##', '##...##'),
    'A': ('.####.', '##..##', '##..##', '##..##', '######', '##..##', '##..##', '##..##', '##..##'),
    'S': ('.#####', '##....', '##....', '.####.', '....##', '....##', '....##', '##..##', '.####.'),
    '!': ('##', '##', '##', '##', '##', '##', '..', '##', '##'),
}


def nota_massa(f):
    """«MASSA!!!» en lletres grosses de llapis d'ulls, i l'aigua que regalima (el nivell de sota és una piscina)."""
    S = torn(f.P([(5, 4), (59, 5), (56, 31), (8, 30)]), 'lrtb', seed=13, depth=1)
    scrap_cartell(f, S, 13, curl=False)
    x = 8
    for i, ch in enumerate('MASSA'):                                     # la mà que tremola: cada lletra balla
        x = f.text(x, 7 + (1 if i % 2 else 0), ch, KOHL, 0.8, font=BIGM640, sp=1) + 0
    for i in range(3):
        f.text(x + i * 3, 7 - i, '!', KOHL, 0.8 + i * 0.3, font=BIGM640)
    # el subratllat doble
    for x in range(10, 52):
        f.px(x, 19, KOHL, 1.4 if hr(x, 1) > 0.2 else 2.4)
        if 13 < x < 48:
            f.px(x, 21 + (1 if x > 30 else 0), KOHL, 1.6 if hr(x, 3) > 0.3 else 2.6)
    # l'aigua: taca blava, gotes que regalimen
    for (x, y) in S:
        if y >= 24 and hr(x // 2, 5) > 0.3:
            f.px(x, y, WATER, 2.6 + (hr(x, y) - 0.5) + (y - 24) * 0.1)
    for x, y in ((16, 32), (33, 32), (45, 32), (33, 33), (45, 34)):
        f.px(x, y, WATER, 3.0)
    f.dots(((16, 33), (45, 33)), WATER, 3.8)


def fitxa_mira(f):
    """Fitxa de personal de mania, molla: capçalera, foto en sépia de la Mira, línies a màquina i taques d'aigua."""
    S = f.R(5, 5, 59, 31) - {(5, 5), (59, 5), (5, 31), (59, 31)}
    paper(f, S, MANI, 4.0, w=54, h=26)
    f.rect(6, 6, 58, 11, LEATH, lambda x, y: 3.0 + (0.6 if y == 6 else 0) - (0.4 if y == 11 else 0))
    f.text(8, 7, 'PERSONAL', MANI, 4.4)                     # el títol de la capçalera
    f.rect(46, 7, 56, 10, MANI, 2.4)                                     # la casella del número
    f.dots(((48, 8), (49, 8), (52, 8), (53, 8), (55, 8)), MANI, 4.4)
    # la foto, amb el clip
    f.rect(9, 13, 21, 28, SEPIA, 2.0)
    f.rect(10, 14, 20, 27, SEPIA, 3.8)
    f.rect(11, 23, 19, 27, SEPIA, 1.8)                                   # les espatlles
    f.rect(14, 22, 16, 23, SEPIA, 3.6)                                   # el coll
    f.ell(15, 19, 3.2, 3.8, SEPIA, 4.4, amp=1.4)                         # la cara
    f.rect(12, 15, 18, 16, SEPIA, 1.2)                                   # els cabells
    f.dots(((11, 17), (11, 18), (11, 19), (19, 17), (19, 18), (19, 19)), SEPIA, 1.2)
    f.dots(((14, 19), (16, 19)), SEPIA, 2.0)                             # els ulls
    f.rect(13, 12, 13, 16, STEEL, 5.0)
    f.dots(((14, 12), (14, 16)), STEEL, 3.0)
    # les línies a màquina: etiqueta i dada
    for i, y in enumerate((14, 18, 22, 26)):
        f.rect(25, y, 28, y, INKG, 2.0)
        f.scrib(31, 55 - (i % 2) * 8, y, INKG, 1.0, seed=70 + i, dens=0.95, tall=0)
    # les taques d'aigua (està molla): anells més foscos
    for (cx, cy, r) in ((44, 24, 7.3), (31, 12, 4.5)):
        for (x, y) in S:
            d = math.hypot(x - cx, (y - cy) * 1.2)
            if d < r:
                f.shade(x, y, -0.7 if r - d < 1.4 else -0.25)


def planols(f):
    """Plànols originals de la cambra: cianotípia mig desenrotllada, amb el dibuix de la cambra en blanc."""
    S = f.R(13, 5, 60, 30)                                               # el full desplegat
    paper(f, S, BLUEP, 3.4, w=48, h=25)
    f.rect(16, 8, 57, 27, BLUEP, 3.6, rim=None)
    for (x, y) in f.R(16, 8, 57, 27):
        if x in (16, 57) or y in (8, 27):
            f.px(x, y, BLUEP, 5.6)
    for x in range(17, 57, 4):                                           # la quadrícula, molt fluixa
        for y in range(9, 27):
            f.px(x, y, BLUEP, 3.9)
    # la cambra: cercle amb la bobina, els radis i el pal central
    f.ring(31, 17.5, 7.0, 7.0, BLUEP, 6.0)
    f.ring(31, 17.5, 3.4, 3.4, BLUEP, 5.0)
    f.rect(30, 17, 32, 18, BLUEP, 6.0)
    for a in range(0, 360, 45):
        r = math.radians(a)
        f.px(round(31 + 5.2 * math.cos(r)), round(17.5 + 5.2 * math.sin(r)), BLUEP, 5.4)
    for x in range(18, 44):
        if x % 2:
            f.px(x, 17, BLUEP, 4.8)
    # les cotes, amb les fletxetes
    f.rect(24, 10, 38, 10, BLUEP, 5.0)
    f.dots(((24, 9), (24, 11), (38, 9), (38, 11)), BLUEP, 5.0)
    # el caixetí
    f.rect(44, 20, 56, 26, BLUEP, 5.4, rim=None)
    f.rect(45, 21, 55, 25, BLUEP, 3.6, rim=None)
    f.rect(46, 22, 53, 22, BLUEP, 5.6)
    f.rect(46, 24, 50, 24, BLUEP, 5.0)
    for y in (11, 13, 15):
        f.rect(44, y, 55 - (y == 15) * 3, y, BLUEP, 5.0)
    # el rotlle a l'esquerra
    pix = {}
    for y in range(4, 32):
        for x in range(5, 17):
            u = (x - 10.5) / 6.0
            if abs(u) <= 1:
                pix[(x, y)] = (u, 0.0, math.sqrt(1 - u * u))
    for (x, y), (nx, ny, nz) in pix.items():
        f.px(x, y, BLUEP, 3.6 + 2.2 * (nx * LX + nz * LZ - 0.35))
    f.shine(pix, 0.8, 1.0)
    f.ell(10.5, 4.5, 5.8, 2.1, BLUEP, 5.6, amp=0.4)                      # la boca del rotlle, amb l'espiral
    f.ring(10.5, 4.5, 3.0, 1.1, BLUEP, 2.2)
    f.ring(10.5, 4.5, 1.4, 0.5, BLUEP, 3.0)
    f.rect(5, 16, 16, 18, RED, lambda x, y: 3.8 if y == 16 else 2.6 - (y - 17) * 0.6)   # la cinta vermella
    f.dots(((10, 19), (11, 20), (12, 20), (12, 21)), RED, 2.4)           # el cap de la cinta, que penja


def carta_mos(f):
    """Sobre envellit per a la Nura, pel darrere: la solapa en V tancada amb un cor vermell de lacre."""
    S = f.R(7, 6, 58, 30)
    paper(f, S, PAP_O, 3.8, w=51, h=24)
    # la solapa
    for x in range(7, 59):
        d = abs(x - 32.5)
        yy = 6 + round((25.5 - d) * 12 / 25.5)
        for y in range(6, yy + 1):
            f.px(x, y, PAP_O, 4.4 - (y - 6) * 0.04 + (0.5 if y == 6 else 0))
        f.px(x, yy, PAP_O, 2.0)
        f.px(x, yy + 1, PAP_O, 2.8)
    # els plecs laterals
    for i in range(12):
        f.px(8 + i, 29 - i, PAP_O, 2.8)
        f.px(57 - i, 29 - i, PAP_O, 2.8)
    # el cor de lacre, amb la vora vessada
    H = f.E(30.6, 16.5, 2.6, 2.4) | f.E(35.4, 16.5, 2.6, 2.4) | f.P([(28, 17), (38, 17), (33, 23)])
    W2 = {(x + dx, y + dy) for (x, y) in H for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))} - H
    f.fill(W2, RED, 2.2, rim=None)                                       # el lacre que s'escampa
    f.drop(W2 | H)
    f.fill(H, RED, lambda x, y: 3.6 - (y - 14) * 0.18, rim=(0.8, -1.0))
    f.dots(((30, 15), (29, 16)), RED, 5.6)
    f.px(33, 17, RED, 2.6)
    # les taques de vell a les vores
    for (x, y) in S:
        if (x < 11 or y > 27 or x > 56) and hr(x, y, 4) > 0.7:
            f.shade(x, y, -0.6)




def nota_vet_nom(f):
    """Tros de cartell amb el nom en gros: «VET», amb llapis d'ulls."""
    S = torn(f.P([(9, 5), (56, 4), (55, 31), (7, 30)]), 'lrtb', seed=17, depth=1)
    scrap_cartell(f, S, 17)
    x = f.text(12, 10, 'V', KOHL, 0.8, font=BIG640)
    x = f.text(x + 2, 11, 'E', KOHL, 0.8, font=BIG640)
    f.text(x + 2, 11, 'T', KOHL, 0.8, font=BIG640)
    for (xx, yy) in ((13, 10), (24, 11), (35, 11)):                      # on el llapis carrega més
        f.px(xx, yy, KOHL, 0.2)
    for x in range(13, 44):
        f.px(x, 23 + (1 if 26 < x < 34 else 0), KOHL, 1.6 if hr(x, 2) > 0.25 else 2.6)


# Lletres grosses de 8 files, a mà (el nom de l'Iri)
BIG8 = {
    'I': ('###', '.#.', '.#.', '.#.', '.#.', '.#.', '.#.', '###'),
    'R': ('#####.', '##..##', '##..##', '#####.', '###...', '##.##.', '##..##', '##..##'),
}
FONT35X = dict(FONT, X=('#.#', '#.#', '.#.', '#.#', '#.#'))   # la de 3×5, amb la X
STAR9 = ('....#....', '...###...', '...###...', '#########', '.#######.', '..#####..', '..##.##..', '.##...##.',
         '##.....##')


def _star(f, x0, y0, rows, mat, base):
    """Estrella daurada amb la vora de baix i dels costats més fosca."""
    for j, row in enumerate(rows):
        for i, c in enumerate(row):
            if c == '#':
                edge = (i == 0 or row[i - 1] == '.' or i == len(row) - 1 or row[i + 1] == '.') and j > 2
                f.px(x0 + i, y0 + j, mat, base - j * 0.25 - (1.4 if edge else 0))


def nota_iri_nom(f):
    """Mig full de la llibreta de l'Iri, esquinçat de través, amb el nom en gros: «IRI», amb llapis."""
    S = torn(f.P([(12, 4), (53, 4), (53, 23), (12, 31)]), 'b', seed=19, depth=1)
    paper(f, S, PAP_C, 4.0, w=41, h=27)
    for y in range(7, 32, 4):                                            # el ratllat
        for x in range(13, 53):
            if (x, y) in S:
                f.px(x, y, RULE, 1.4)
    for y in range(4, 32):                                               # el marge
        if (16, y) in S:
            f.px(16, y, PINK, 2.6)
    for (x, y) in ((14, 8), (14, 16), (14, 24)):                         # els forats de l'espiral
        if (x, y) in S:
            f.px(x, y, DARK, 1.0)
            f.px(x + 1, y + 1, PAP_C, 2.4)
    x = f.text(22, 8, 'I', GRAPH, 0.4, font=BIG8)
    x = f.text(x + 2, 8, 'R', GRAPH, 0.4, font=BIG8)
    x = f.text(x + 2, 8, 'I', GRAPH, 0.4, font=BIG8)
    f.dots([(x + 2, 14), (x + 3, 14), (x + 2, 15), (x + 3, 15)], GRAPH, 0.4)
    for xx in range(22, 42):                                             # el subratllat, a mà
        f.px(xx, 18 + (1 if xx > 34 else 0), GRAPH, 1.0)
    f.scrib(20, 40, 22, GRAPH, 1.2, seed=3)


def fullet_memoria(f):
    """Fullet de la Sala de la Memòria: díptic de vellut vermell, marc daurat i la fàbrica en sépia."""
    B = f.P([(9, 8), (23, 3), (23, 32), (9, 29)])                       # la pàgina del darrere, que s'obre
    f.fill(B, VELV, lambda x, y: 2.0 + (x - 9) * 0.04, rim=(0.6, -0.8))
    for y in range(11, 27, 4):
        for x in range(12, 21):
            f.px(x, y, BRASS, 2.4 if hr(x, y) > 0.3 else 1.4)
    C = f.R(23, 3, 51, 32)                                               # la portada
    f.drop(C)
    f.fill(C, VELV, lambda x, y: 3.4 - (x - 23) * 0.03 - (y - 3) * 0.025 + (hr(x, y, 2) - 0.5) * 0.3,
           rim=(0.8, -1.0))
    for (x, y) in f.R(25, 5, 49, 30):                                    # el marc daurat, doble
        if x in (25, 49) or y in (5, 30):
            f.px(x, y, BRASS, 4.2 - (y - 5) * 0.05)
        elif x in (27, 47) and 7 <= y <= 28 or y in (7, 28) and 27 <= x <= 47:
            f.px(x, y, BRASS, 2.8)
    for (x, y) in ((25, 5), (49, 5), (25, 30), (49, 30)):
        f.px(x, y, BRASS, 5.4)
    # la vinyeta en sépia: les xemeneies de la fàbrica, amb el fum
    f.rect(29, 9, 45, 20, SEPIA, lambda x, y: 4.6 - (y - 9) * 0.12)
    for (x0, y0) in ((31, 12), (36, 11), (41, 13)):
        f.rect(x0, y0, x0 + 1, 20, SEPIA, 1.4)
        f.rect(x0 - 1, y0, x0 + 2, y0, SEPIA, 1.8)
        f.dots([(x0 + 1, y0 - 1), (x0 + 2, y0 - 2), (x0 + 1, y0 - 3)], SEPIA, 3.0)
    f.rect(29, 16, 45, 20, SEPIA, 1.8)
    for x in range(30, 45, 3):                                           # les finestres de la nau
        f.px(x, 18, SEPIA, 3.4)
    f.text(31, 22, 'SALA', BRASS, 5.0)                                   # el títol daurat
    f.scrib(30, 44, 27, BRASS, 3.4, seed=4, dens=0.9, tall=0)


def mapa_fuga(f):
    """El fullet de la Memòria pel darrere, obert: la ruta de fuga amb llapis d'ulls, de la reixa al moll."""
    S = f.R(5, 4, 59, 31)
    paper(f, S, PAP_W, 4.0, w=54, h=27)
    f.rect(5, 4, 59, 4, VELV, 3.4)
    f.rect(5, 31, 59, 31, VELV, 2.8)
    f.rect(32, 5, 32, 30, PAP_W, 2.6)                                    # el plec
    f.rect(33, 5, 33, 30, PAP_W, 5.0)
    K = KOHL
    f.rect(9, 8, 18, 15, K, 1.0)                                         # la reixa (l'inici)
    f.rect(10, 9, 17, 14, PAP_W, 4.4)
    for x in (11, 13, 15):
        f.rect(x, 9, x, 14, K, 1.4)
    path = [(18, 12), (27, 12), (27, 22), (41, 22), (41, 12), (51, 12), (51, 20)]   # la ruta, de punts
    for (xa, ya), (xb, yb) in zip(path, path[1:]):
        n = max(abs(xb - xa), abs(yb - ya))
        for i in range(n + 1):
            if i % 2 == 0:
                f.px(xa + (xb - xa) * i // n, ya + (yb - ya) * i // n, K, 1.0)
    for i in range(6):                                                   # la creu del moll
        f.px(48 + i, 22 + i, STAMP, 2.6)
        f.px(53 - i, 22 + i, STAMP, 2.6)
        f.shade(49 + i, 22 + i, 0.6)
    f.text(8, 20, 'PD', K, 1.2, font=FONT46)
    f.scrib(8, 22, 28, K, 1.6, seed=8, dens=0.9, tall=0)
    f.scrib(36, 44, 27, K, 1.8, seed=9, dens=0.8, tall=0)


def tub_ferro9(f, x0=12):
    """Tub de vàlvula de ferro-9: cilindre lluent amb rosca als caps, buit per dins (es veu el forat)."""
    f.hcyl(x0, 57, 17, 6.6, F9, 4.6, amp=2.8, spec=1.8)
    for xr in (x0 + 1, x0 + 3, x0 + 5, 50, 52, 54):                      # les anelles de la rosca
        for y in range(10, 25):
            f.shade(xr, y, -1.2)
    for x in range(x0 + 9, 47, 7):                                       # la veta de l'estirat
        f.shade(x, 13, 0.6)
        f.shade(x + 1, 13, 0.6)
    f.ell(57, 17, 2.8, 6.6, F9, 3.0, amp=1.6)                            # la testa de la dreta
    f.ell(57.5, 17, 1.3, 4.2, F9, 1.0, amp=0.6)
    f.ell(x0 - 0.6, 17, 3.2, 7.4, F9, 5.4, amp=1.2)                      # la boca oberta de l'esquerra
    f.ell(x0 - 0.8, 17, 2.2, 5.4, DARK, 0.6, amp=0.0)
    f.px(x0 - 1, 13, F9, 1.2)                                            # el fons del forat
    f.px(x0 - 1, 21, F9, 1.0)


def tub_amb_llibreta(f):
    """El tub de ferro-9 amb la llibreta de torn de l'Iri enrotllada a dins, que en treu el cap."""
    tub_ferro9(f, x0=23)
    # el rotlle de fulls: tapa de pell per fora, fulls crema i l'espiral a la punta
    f.hcyl(8, 22, 17, 4.5, LEATH, 3.8, amp=2.2, spec=0.6)
    for x in range(8, 23):
        f.px(x, 21, PAP_C, 3.0)                                          # el cantell dels fulls que sobresurt
        f.px(x, 22, PAP_C, 2.2 if x % 3 else 3.4)
    f.ell(7.3, 17, 2.9, 4.8, PAP_C, 4.4, amp=1.4)
    f.dots(((7, 15), (8, 16), (8, 17), (7, 18), (6, 18), (5, 17), (6, 15)), PAP_C, 2.2)   # l'espiral del paper
    f.px(7, 17, LEATH, 2.0)
    f.rect(15, 12, 15, 22, RED, 3.4)                                     # la goma
    f.rect(16, 12, 16, 22, RED, 2.2)
    for (x, y) in f.E(22, 17, 3.2, 7.4) - f.E(22.4, 17, 1.6, 5.0):       # el llavi del tub, per davant
        if x <= 23:
            f.px(x, y, F9, 5.6 - (y - 17) * 0.2)


def clau_vitrina(f):
    """Clau petita i plana d'acer, amb un clauer i una etiqueta de vellut on posa «MUSEU»."""
    pix = f.ell(11, 12, 5.8, 5.8, STEEL, 4.4, amp=2.4)
    f.shine(pix, 0.8, 1.4)
    for p in f.E(9.5, 12, 1.9, 1.9):
        f.erase(*p)
    f.rect(16, 11, 33, 13, STEEL, lambda x, y: 5.2 - (y - 11) * 1.2, rim=None)
    f.rect(18, 12, 31, 12, STEEL, 3.2)                                   # la ranura
    for x, d in ((22, 3), (25, 4), (28, 2), (31, 3)):                    # les dents
        f.rect(x, 14, x + 1, 13 + d, STEEL, lambda xx, yy, x=x: 3.6 - (xx - x) * 0.8 - (yy - 14) * 0.2)
    f.px(33, 12, STEEL, 3.0)
    f.ring(13, 20.5, 3.4, 3.4, STEEL, 5.0)                               # el clauer
    T = f.R(17, 20, 61, 31) - {(17, 20), (61, 20), (17, 31), (61, 31)}   # l'etiqueta
    f.drop(T)
    f.fill(T, VELV, lambda x, y: 3.6 - (x - 17) * 0.03 + (hr(x, y, 4) - 0.5) * 0.3, rim=(0.8, -1.0))
    for x in range(19, 60):                                              # el pespunt
        if x % 2:
            f.px(x, 22, VELV, 4.8)
            f.px(x, 29, VELV, 2.0)
    f.ring(20.5, 25.5, 1.4, 1.4, BRASS, 4.4)
    f.text(29, 23, 'MUSEU', BRASS, 4.6, font=FONT46)


def placa_cargol(f):
    """Placa d'identificació del robot: metall gastat, cargols, «C-1» en relleu i «CARGOL» gravat a mà."""
    S = f.R(7, 4, 57, 31) - {(7, 4), (57, 4), (7, 31), (57, 31)}
    f.drop(S)
    f.fill(S, IRON, lambda x, y: 4.6 - (x - 7) * 0.025 - (y - 4) * 0.05 + (hr(x, y, 5) - 0.5) * 0.6, rim=(1.0, -1.6))
    for (x, y) in ((10, 7), (54, 7), (10, 28), (54, 28)):                # els cargols, amb el tall
        f.fill(f.R(x - 1, y - 1, x + 1, y + 1), IRON, 5.6, rim=(1.0, -2.4))
        f.dots([(x - 1, y + 1), (x, y), (x + 1, y - 1)], IRON, 1.8)
    for (x, y) in ((44, 9), (45, 10), (20, 26), (48, 24), (14, 15)):     # les ratllades
        f.shade(x, y, 1.0)

    def emboss(x, y, s):
        """Lletres en relleu: clares a dalt-esquerra, ombra a baix-dreta."""
        for ch in s:
            g = FONT46[ch]
            for j, row in enumerate(g):
                for i, c in enumerate(row):
                    if c == '#':
                        f.px(x + i + 1, y + j + 1, IRON, 1.6)
            for j, row in enumerate(g):
                for i, c in enumerate(row):
                    if c == '#':
                        f.px(x + i, y + j, IRON, 6.6)
            x += len(g[0]) + 2
    emboss(25, 7, 'C-1')
    f.rect(12, 16, 52, 16, IRON, 2.4)                                    # la ratlla
    f.rect(12, 17, 52, 17, IRON, 5.4)
    x = 17                                                               # «CARGOL», rascat amb una llima
    for ch in 'CARGOL':
        g = FONT46[ch]
        for j, row in enumerate(g):
            for i, c in enumerate(row):
                if c == '#':
                    f.px(x + i, 21 + j, STEEL, 7.0 if hr(x + i, j) > 0.25 else 5.4)
        x += len(g[0]) + 1


def formulari_27be(f):
    """Formulari 27-B/E (carnet d'usuària exemplar): capçalera daurada, estrella grossa i la ratlla de signar, amb la creu."""
    form(f, 19, 2, head=BRASS, code='27BE', sig=True)
    _star(f, 34, 13, STAR9, BRASS, 5.2)
    f.rect(21, 29, 43, 29, INKG, 1.2)                                    # la ratlla de la signatura, amb la «X»
    for i in range(5):
        f.px(21 + i, 23 + i, STAMP, 2.6)
        f.px(25 - i, 23 + i, STAMP, 2.6)


def formulari_27be_signat(f):
    """El 27-B/E signat pel capatàs: un gargot gran de tinta blava que travessa la ratlla, i un borrall."""
    formulari_27be(f)
    pts = [(21, 30), (24, 21), (26, 28), (28, 21), (30, 28), (32, 24), (34, 28), (37, 25), (41, 27), (45, 22)]
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        f.line(xa, ya, xb, yb, INKB, 2.6)
        f.line(xa + 1, ya, xb + 1, yb, INKB, 1.6)
    f.dots(((43, 30), (44, 30), (44, 31), (45, 31)), INKB, 2.2)         # el borrall
    f.px(43, 31, INKB, 1.4)


def carnet_exemplar(f):
    """Carnet plastificat d'usuària exemplar: foto de l'Iri, estrella daurada i la lluentor del plàstic."""
    S = f.R(7, 5, 57, 31)
    for (cx, cy, sx, sy) in ((7, 5, 1, 1), (57, 5, -1, 1), (7, 31, 1, -1), (57, 31, -1, -1)):   # cantons rodons
        S -= {(cx, cy), (cx + sx, cy), (cx, cy + sy)}
    f.drop(S)
    f.fill(S, PAP_W, lambda x, y: 4.6 - (y - 5) * 0.025, rim=(0.6, -1.6))
    f.rect(9, 7, 55, 12, RED, lambda x, y: 3.0 + (0.6 if y == 7 else 0) - (0.5 if y == 12 else 0))
    f.text(24, 8, 'EXEMPLAR', PAP_W, 5.2, font=FONT35X)
    # la foto de l'Iri
    f.rect(10, 10, 22, 27, CYAN, lambda x, y: 3.6 - (y - 10) * 0.05)
    f.rect(11, 23, 21, 27, SHIRT, 2.2)
    f.rect(15, 22, 17, 23, SKIN, 2.6)                                    # el coll
    f.ell(16, 17.5, 3.6, 4.2, SKIN, 3.4, amp=1.6)
    f.rect(12, 12, 20, 14, HAIR, 2.6)
    f.dots([(12, 15), (12, 16), (20, 15), (20, 16), (20, 17), (11, 14)], HAIR, 1.8)
    f.dots([(14, 17), (18, 17)], DARK, 1.0)
    f.dots([(15, 20), (16, 20), (17, 20)], SKIN, 1.8)
    # les dades, l'estrella i la signatura
    for y in (16, 19):
        f.scrib(26, 44, y, INKG, 1.2, seed=y, dens=0.95, tall=0)
    _star(f, 46, 16, ('...#...', '..###..', '#######', '.#####.', '..###..', '.##.##.', '##...##'), BRASS, 5.0)
    f.rect(26, 25, 41, 25, INKB, 1.8)
    f.dots([(30, 24), (34, 24), (38, 26)], INKB, 2.2)
    # la lluentor del plastificat: dues diagonals clares
    for i in range(22):
        for (dx, d) in ((0, 1.0), (1, 1.0), (5, 0.6)):
            x, y = 28 + i - dx, 30 - i
            if (x, y) in S:
                f.shade(x, y, d)


def notes_perdudes(f):
    """Un feix de notes de molts anys: papers de colors i mides diferents, subjectats amb una pinça."""
    A = f.P([(7, 11), (28, 5), (32, 25), (11, 31)])                      # la nota groguenca de darrere, girada
    paper(f, A, PAP_O, 3.6)
    for k in range(4):
        f.line(11 + k, 15 + k * 3, 25 + k, 11 + k * 3, INKG, 1.4)
    B = torn(f.R(20, 12, 53, 21), 'r', seed=4, depth=1)                  # la tira ratllada
    paper(f, B, PAP_W, 4.2)
    for y in (14, 17, 20):
        f.rect(21, y, 51, y, RULE, 1.0)
    f.scrib(22, 45, 16, INKB, 1.6, seed=1)
    f.scrib(22, 38, 19, INKB, 1.6, seed=2)
    C = f.P([(37, 4), (56, 7), (53, 20), (36, 17)])                      # el paperet rosa
    paper(f, C, PINK, 3.8)
    f.scrib(40, 52, 10, KOHL, 1.6, seed=3, dens=0.9)
    f.scrib(40, 50, 13, KOHL, 1.6, seed=4, dens=0.9)
    f.scrib(39, 47, 16, KOHL, 1.6, seed=5, dens=0.9)
    D = torn(f.R(25, 20, 47, 32), 'b', seed=2, depth=1)                  # la quartilla de llibreta de davant
    paper(f, D, PAP_C, 4.0)
    f.rect(28, 21, 28, 31, PINK, 2.6)
    f.scrib(30, 44, 24, GRAPH, 1.0, seed=6)
    f.scrib(30, 41, 28, GRAPH, 1.0, seed=7)
    # la pinça de ferro
    f.rect(32, 4, 40, 7, IRON, lambda x, y: 4.6 - (y - 4) * 0.6, rim=(0.6, -1.0))
    f.rect(33, 8, 39, 12, IRON, lambda x, y: 3.4 - (x - 33) * 0.22, rim=(0.6, -1.0))
    f.rect(33, 6, 39, 6, IRON, 2.2)
    f.ring(36, 3.5, 2.6, 1.6, IRON, 5.0)


def nota_mos(f):
    """Nota vella, groguenca, plegada en quatre: «M.» i un 9 de llapis d'ulls, i un rodal de taca."""
    S = f.R(16, 4, 48, 32) - {(16, 4), (17, 4), (16, 5), (48, 32), (47, 32), (48, 31)}
    paper(f, S, PAP_O, 4.0, w=32, h=28)
    for y in range(4, 33):                                               # els plecs en creu
        f.px(32, y, PAP_O, 2.4)
        f.px(33, y, PAP_O, 4.8)
    for x in range(16, 49):
        f.px(x, 18, PAP_O, 2.4)
        f.px(x, 19, PAP_O, 4.8)
    f.ring(41, 25, 5.3, 4.8, PAP_O, 1.8, th=1.4)                         # el rodal de la tassa
    f.ring(41.5, 25.5, 3.4, 3.0, PAP_O, 3.0, th=0.8)
    for (x, y) in S:                                                     # les vores, enfosquides i tacades
        if x in (16, 48) or y in (4, 32):
            f.shade(x, y, -0.8)
        elif hr(x, y, 31) > 0.93:
            f.shade(x, y, -0.6)
    for i, y in enumerate((8, 12)):                                      # l'escriptura
        f.scrib(19, 30, y, KOHL, 1.2, seed=80 + i, dens=0.9)
        f.scrib(36, 46, y, KOHL, 1.2, seed=90 + i, dens=0.9)
    f.scrib(19, 27, 15, KOHL, 1.2, seed=82, dens=0.9)
    x = f.text(19, 23, 'M', KOHL, 1.0, font=FONT46)
    f.px(x + 1, 28, KOHL, 1.0)
    f.text(x + 3, 23, '9', KOHL, 1.0, font=FONT46)


ICONS = {fn.__name__: fn for fn in (
    clau_anglesa, formulari_27b, formulari_segellat, formulari_triplicat, plomall, segell, clau_cambra,
    llapis, llibreta_torn, caixa_eines, imant_ferro9, nota_iri, avis_reciclatge, llapis_ulls, nota_vet,
    fullet_reeducacio, nota_pany, escarabat, sopa,
    tros_cartell, nota_mida, biga_acer, biga_ferro9, serra, tram_biga_1, tram_biga_2, tram_biga_3, biga_muntada,
    nota_amagatall, pols_rovell, molla, llima, diapaso, diapaso_espatllat, nota_pressio, nota_massa, fitxa_mira,
    planols, carta_mos, nota_vet_nom, nota_iri_nom, fullet_memoria,
    mapa_fuga, tub_ferro9, tub_amb_llibreta, clau_vitrina, placa_cargol,
    formulari_27be, formulari_27be_signat, carnet_exemplar, notes_perdudes, nota_mos,
)}


def render(item_id):
    """Imatge RGBA de 65×36 de l'objecte, o None si no en té."""
    fn = ICONS.get(item_id)
    if fn is None:
        return None
    f = Ic640()
    fn(f)
    return f.render()
