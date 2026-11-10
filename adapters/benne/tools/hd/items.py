"""
Icones d'inventari en pixel art HD: es dibuixen píxel a píxel a la mida real de la casella
(49×27), amb volum (llum de dalt a l'esquerra), rampes per material i el contorn fosc selectiu dels
personatges (hd/characters.py: Fig.render).

Cada objecte té una funció `nom(f)` que pinta sobre una figura `Ic` (una Fig amb eines per a papers,
lletres, bigues, cilindres...). draw_items.py les fa servir a través de `ICONS` i `icon()`.
"""
import math

from hd.characters import Fig, Mat, LX, LY, LZ
from hd.pix import hr

W, H = 49, 27


def M(*cols, d=0.0):
    return Mat(cols, d)


# ─── Materials (fosc → clar, amb canvi de to) ───────────────────────────────
# Papers: cadascun té el seu color, per distingir-los d'una ullada.
PAP_W = M((44, 46, 70), (96, 100, 126), (152, 156, 176), (198, 202, 212), (230, 232, 234), (248, 248, 244), (255, 255, 252))   # paper d'oficina (La Gavina), blanc fred
PAP_F = M((58, 42, 44), (116, 100, 92), (170, 158, 138), (210, 200, 176), (234, 226, 204), (248, 244, 228), (255, 252, 242))   # formularis de la fàbrica, blanc trencat
PAP_C = M((60, 40, 40), (120, 96, 80), (178, 156, 124), (216, 198, 160), (238, 224, 188), (250, 242, 214))                     # llibreta de l'Iri, crema
PAP_O = M((52, 30, 26), (108, 72, 44), (160, 118, 70), (200, 160, 98), (224, 196, 134), (240, 220, 168))                       # paper vell, groguenc
MANI = M((46, 28, 22), (98, 66, 38), (150, 110, 58), (192, 152, 86), (222, 188, 118), (242, 216, 158))                        # cartolina mania
SIGN = M((52, 56, 56), (110, 116, 110), (170, 176, 166), (214, 218, 206), (238, 240, 230), (252, 252, 246))                    # cartell de la Gavina
BLUEP = M((8, 16, 44), (16, 36, 84), (28, 62, 130), (46, 92, 168), (78, 128, 198), (140, 186, 232), (214, 236, 252))          # plànol (cianotípia)
# Tintes
GRAPH = M((44, 44, 58), (78, 78, 92), (112, 112, 124), (150, 150, 160))      # llapis (grafit)
KOHL = M((10, 6, 16), (26, 18, 32), (50, 40, 58), (80, 70, 88))              # llapis d'ulls
INKB = M((14, 18, 46), (30, 40, 92), (56, 74, 140), (96, 116, 180))          # tinta de ploma
INKG = M((40, 40, 50), (88, 88, 98), (140, 140, 146), (186, 186, 186))       # text imprès, gris
STAMP = M((70, 10, 22), (130, 22, 32), (186, 40, 44), (222, 80, 70), (244, 130, 110))   # tinta de segell
RULE = M((96, 120, 160), (140, 164, 200), (176, 196, 222))          # ratllat de llibreta, blau pàl·lid
WATER = M((40, 70, 110), (70, 110, 160), (110, 160, 210), (170, 210, 240))
# Colors
RED = M((40, 8, 16), (86, 18, 24), (140, 32, 34), (188, 54, 46), (226, 92, 72), (250, 146, 116))
PINK = M((64, 16, 40), (122, 36, 76), (186, 64, 118), (230, 110, 164), (252, 166, 204), (255, 220, 236))
CORPG = M((8, 34, 26), (14, 62, 44), (26, 100, 68), (46, 140, 90), (84, 186, 124), (156, 230, 176))
TEAL = M((6, 30, 36), (12, 58, 66), (22, 96, 100), (40, 140, 138), (84, 190, 178), (164, 236, 220))
SUNY = M((70, 40, 10), (140, 92, 16), (206, 150, 30), (242, 200, 60), (255, 236, 130), (255, 250, 200))
VELV = M((24, 6, 14), (52, 12, 26), (86, 20, 38), (124, 34, 50), (160, 54, 64), (196, 90, 92))
ORNG = M((56, 16, 14), (104, 34, 20), (156, 60, 26), (206, 94, 36), (240, 140, 60), (255, 190, 120))
LIME = M((20, 36, 10), (44, 76, 18), (84, 128, 30), (134, 182, 56), (186, 226, 104), (232, 252, 180))
SEPIA = M((42, 26, 22), (82, 56, 40), (126, 92, 64), (168, 132, 96), (204, 172, 132), (232, 210, 172))
SKIN = M((64, 30, 42), (118, 62, 62), (170, 104, 86), (212, 146, 114), (238, 184, 148), (252, 216, 184))
HAIR = M((10, 6, 12), (28, 16, 22), (48, 28, 34), (72, 44, 46), (104, 70, 62))
HAIRG = M((60, 60, 76), (106, 106, 120), (156, 156, 166), (204, 204, 206), (236, 236, 236))
SHIRT = M((22, 28, 54), (38, 54, 92), (62, 88, 132), (94, 128, 170))
SUIT = M((10, 10, 18), (22, 22, 36), (38, 40, 58), (58, 62, 84), (84, 90, 114))
# Metalls i altres materials
F9 = M((16, 22, 36), (30, 42, 62), (48, 66, 92), (70, 96, 126), (100, 132, 162), (140, 174, 200), (186, 214, 232), (232, 246, 252), (255, 255, 255))  # ferro-9: acer blavós lluent
ACER = M((22, 20, 26), (38, 36, 42), (56, 54, 60), (78, 76, 80), (104, 100, 102), (134, 130, 128), (170, 164, 158), (206, 200, 192), (236, 232, 224))  # acer comú
IRON = M((14, 14, 20), (28, 28, 36), (44, 44, 54), (64, 64, 74), (90, 88, 98), (120, 118, 126), (156, 152, 156), (196, 192, 190))
STEEL = M((14, 18, 28), (28, 36, 50), (46, 56, 72), (70, 82, 100), (100, 114, 132), (138, 152, 168), (184, 196, 208), (230, 238, 244))   # acer de la Gavina
PLAST = M((20, 22, 30), (40, 44, 56), (66, 72, 86), (98, 106, 120), (136, 144, 156), (176, 182, 190), (216, 220, 224))   # plàstic gris de presó
BRASS = M((40, 24, 16), (84, 54, 22), (138, 96, 34), (190, 144, 54), (230, 192, 90), (252, 234, 160), (255, 252, 220))
COPPER = M((40, 18, 14), (76, 34, 20), (118, 56, 30), (160, 84, 44), (200, 120, 66), (232, 162, 104), (250, 210, 160))
WOOD = M((22, 12, 16), (44, 24, 22), (70, 40, 30), (100, 60, 38), (132, 84, 50), (168, 112, 66), (204, 146, 92))
PALE = M((60, 40, 30), (110, 78, 52), (160, 118, 78), (200, 158, 108), (228, 194, 142), (244, 222, 178))   # fusta clara (llapis tallat)
LEATH = M((22, 12, 12), (44, 24, 20), (70, 40, 30), (98, 58, 40), (128, 82, 54), (160, 110, 74))
RUST = M((30, 12, 10), (62, 26, 16), (100, 44, 22), (140, 66, 30), (178, 96, 44), (210, 132, 70), (236, 176, 112))
BEET = M((8, 6, 6), (28, 16, 14), (54, 32, 24), (90, 58, 40), (128, 90, 62), (170, 132, 98), (214, 186, 150))
FEATH = M((30, 22, 22), (62, 46, 40), (98, 76, 62), (138, 112, 88), (176, 150, 118), (210, 190, 156), (236, 222, 196))
CLOTH = M((60, 50, 44), (110, 100, 88), (160, 150, 132), (204, 196, 176), (232, 226, 208))   # tela, cordill
CYAN = M((14, 40, 70), (30, 90, 140), (70, 160, 210), (140, 220, 250), (220, 250, 255))
STEAM = M((120, 130, 150), (180, 188, 200), (226, 230, 236), (250, 252, 255))
DARK = M((6, 4, 10), (14, 10, 18), (26, 20, 30))


# ─── Lletres (3×5) ──────────────────────────────────────────────────────────
FONT = {
    '0': ('###', '#.#', '#.#', '#.#', '###'), '1': ('.#.', '##.', '.#.', '.#.', '###'),
    '2': ('##.', '..#', '.#.', '#..', '###'), '3': ('##.', '..#', '.#.', '..#', '##.'),
    '6': ('.##', '#..', '###', '#.#', '###'), '7': ('###', '..#', '.#.', '.#.', '.#.'),
    '9': ('###', '#.#', '###', '..#', '##.'), '-': ('...', '...', '###', '...', '...'),
    'A': ('.#.', '#.#', '###', '#.#', '#.#'), 'B': ('##.', '#.#', '##.', '#.#', '##.'),
    'C': ('.##', '#..', '#..', '#..', '.##'), 'E': ('###', '#..', '##.', '#..', '###'),
    'G': ('.##', '#..', '#.#', '#.#', '.##'), 'I': ('###', '.#.', '.#.', '.#.', '###'),
    'L': ('#..', '#..', '#..', '#..', '###'), 'M': ('#.#', '###', '###', '#.#', '#.#'),
    'N': ('#.#', '###', '###', '###', '#.#'), 'O': ('.#.', '#.#', '#.#', '#.#', '.#.'),
    'P': ('##.', '#.#', '##.', '#..', '#..'), 'R': ('##.', '#.#', '##.', '#.#', '#.#'),
    'S': ('.##', '#..', '.#.', '..#', '##.'), 'T': ('###', '.#.', '.#.', '.#.', '.#.'),
    'U': ('#.#', '#.#', '#.#', '#.#', '.#.'), 'V': ('#.#', '#.#', '#.#', '.#.', '.#.'),
    'D': ('##.', '#.#', '#.#', '#.#', '##.'), '?': ('##.', '..#', '.#.', '...', '.#.'),
    '!': ('#', '#', '#', '.', '#'), '.': ('.', '.', '.', '.', '#'), ' ': ('.', '.', '.', '.', '.'),
}
# Lletres grosses, a mà (per a les notes que són sobretot un nom o una xifra)
BIG = {
    'V': ('##...##', '##...##', '.##.##.', '.##.##.', '..###..', '..###..', '...#...'),
    'E': ('#####', '##...', '####.', '##...', '##...', '#####'),
    'T': ('######', '..##..', '..##..', '..##..', '..##..', '..##..'),
    'I': ('##', '##', '##', '##', '##', '##'),
    'R': ('####.', '##.##', '####.', '##.#.', '##.##', '##..#'),
    '6': ('.####', '##...', '####.', '##.##', '##.##', '.###.'),
    '½': ('#...#', '#..#.', '#.#..', '.#.##', '#...#', '...#.', '..###'),
}


class Ic(Fig):
    """Llenç d'una icona: buffer (material, nivell) amb eines de dibuix."""

    def __init__(self):
        super().__init__(W, H)

    # ─── conjunts de píxels ───
    @staticmethod
    def R(x0, y0, x1, y1):
        return {(x, y) for y in range(int(y0), int(y1) + 1) for x in range(int(x0), int(x1) + 1)}

    @staticmethod
    def P(pts):
        """Polígon (centres dels píxels a coordenades enteres)."""
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        out = set()
        for y in range(math.floor(min(ys)), math.ceil(max(ys)) + 1):
            for x in range(math.floor(min(xs)), math.ceil(max(xs)) + 1):
                c = False
                for (xa, ya), (xb, yb) in zip(pts, pts[1:] + pts[:1]):
                    if (ya <= y < yb) or (yb <= y < ya):
                        if x < xa + (y - ya) * (xb - xa) / (yb - ya):
                            c = not c
                if c:
                    out.add((x, y))
        return out

    @staticmethod
    def E(cx, cy, rx, ry):
        return {(x, y) for y in range(math.floor(cy - ry), math.ceil(cy + ry) + 1)
                for x in range(math.floor(cx - rx), math.ceil(cx + rx) + 1)
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1}

    # ─── pintar ───
    def fill(self, S, mat, lvl, rim=(0.6, -0.9)):
        """Pinta un conjunt; la vora de dalt-esquerra s'aclareix i la de baix-dreta s'enfosqueix."""
        for (x, y) in S:
            l = lvl(x, y) if callable(lvl) else lvl
            if rim:
                if (x + 1, y) not in S or (x, y + 1) not in S:
                    l += rim[1]
                elif (x - 1, y) not in S or (x, y - 1) not in S:
                    l += rim[0]
            self.px(x, y, mat, l)
        return S

    def drop(self, S, d=-1.4, dx=1, dy=1):
        """Ombra que fa S damunt el que hi ha a sota (abans de pintar S o després, tant fa)."""
        for (x, y) in S:
            q = (x + dx, y + dy)
            if q not in S:
                self.shade(q[0], q[1], d)

    def rect(self, x0, y0, x1, y1, mat, lvl, rim=None):
        return self.fill(self.R(x0, y0, x1, y1), mat, lvl, rim)

    def dots(self, pts, mat, lvl):
        for x, y in pts:
            self.px(x, y, mat, lvl)

    def text(self, x, y, s, mat, lvl, font=FONT, sp=1):
        for ch in s:
            g = font[ch]
            for j, row in enumerate(g):
                for i, c in enumerate(row):
                    if c == '#':
                        self.px(x + i, y + j, mat, lvl)
            x += len(g[0]) + sp
        return x

    def scrib(self, x0, x1, y, mat, lvl, seed=0, dens=0.85, tall=0.18):
        """Ratlla d'escriptura a mà: paraules amb forats i algun traç que puja."""
        x, k = x0, 0
        while x <= x1:
            n = 2 + int(hr(seed, k, 1) * 4)
            for i in range(n):
                if x > x1:
                    break
                if hr(seed, x, y) < dens:
                    self.px(x, y, mat, lvl)
                if hr(seed, x, y, 3) < tall:
                    self.px(x, y - 1, mat, lvl)
                x += 1
            x += 1
            k += 1

    def ring(self, cx, cy, rx, ry, mat, lvl, th=1.0):
        """Anella (un segell): píxels a prop de la vora de l'el·lipse."""
        for y in range(math.floor(cy - ry - 1), math.ceil(cy + ry) + 2):
            for x in range(math.floor(cx - rx - 1), math.ceil(cx + rx) + 2):
                r = math.hypot((x - cx) / rx, (y - cy) / ry)
                if abs(r - 1) * min(rx, ry) < th * 0.62:
                    self.px(x, y, mat, lvl)

    def shine(self, pix, thr=0.8, d=1.6):
        """Reflex especular a les zones que miren de cara a la llum."""
        for (x, y), (nx, ny, nz) in pix.items():
            if nx * LX + ny * LY + nz * LZ > thr:
                self.shade(x, y, d)

    def hcyl(self, x0, x1, cy, r, mat, base, amp=2.4, spec=1.4):
        """Cilindre horitzontal (tub, mànec), amb ombreig vertical i reflex."""
        pix = {}
        for x in range(int(x0), int(x1) + 1):
            for y in range(math.floor(cy - r), math.ceil(cy + r) + 1):
                v = (y - cy) / (r + 0.5)
                if abs(v) <= 1:
                    pix[(x, y)] = (0.0, v, math.sqrt(1 - v * v))
        for (x, y), (nx, ny, nz) in pix.items():
            d = nx * LX + ny * LY + nz * LZ
            self.px(x, y, mat, base + amp * (d - 0.35) + (spec if d > 0.86 else 0))
        return pix

    def stamp(self, cx, cy, r=4.5, lvl=2.4, seed=0):
        """Segell de goma: anella vermella amb una estrella al mig i la tinta irregular."""
        for y in range(math.floor(cy - r - 1), math.ceil(cy + r) + 2):
            for x in range(math.floor(cx - r - 1), math.ceil(cx + r) + 2):
                d = math.hypot(x - cx, y - cy)
                on = abs(d - r) < 0.75 or (d < r - 2.2 and (abs(x - cx) < 0.6 or abs(y - cy) < 0.6 or abs(abs(x - cx) - abs(y - cy)) < 0.6) and d < r - 2.6)
                if on and hr(x, y, seed, 9) > 0.12:
                    self.px(x, y, STAMP, lvl + (hr(x, y, seed) - 0.5) * 1.2)


# ─── Peces comunes ──────────────────────────────────────────────────────────

def paper(f, S, mat, base, grad=0.7, x0=None, y0=None, w=20, h=24):
    """Full: pla, una mica més clar a dalt-esquerra."""
    if x0 is None:
        x0 = min(p[0] for p in S)
        y0 = min(p[1] for p in S)
    f.drop(S)
    return f.fill(S, mat, lambda x, y: base + grad * (0.5 - (x - x0) / w * 0.5 - (y - y0) / h * 0.5))


def torn(S, edges, seed, depth=1, k=0.5):
    """Esquinça vores: treu píxels a l'atzar de les vores indicades ('l', 'r', 't', 'b')."""
    xs, ys = [p[0] for p in S], [p[1] for p in S]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    out = set(S)
    for (x, y) in S:
        for e in edges:
            if e == 'l':
                t, n = x - x0, y
            elif e == 'r':
                t, n = x1 - x, y
            elif e == 't':
                t, n = y - y0, x
            else:
                t, n = y1 - y, x
            # perfil irregular: bosses de 0..depth píxels
            ei = 'lrtb'.index(e)                  # (hr amb enters: determinista)
            prof = int((hr(seed, ei, n // 2) * 0.7 + hr(seed, ei, n, 7) * 0.3) * (depth + 1))
            if t < prof:
                out.discard((x, y))
    return out


def form(f, x0, y0, head=RED, code='27-B', seed=0, w=20, h=23, sig=False):
    """Formulari: full amb capçalera de color i el codi, caselles i ratlles per omplir."""
    S = f.R(x0, y0, x0 + w - 1, y0 + h - 1)
    S -= {(x0 + w - 1, y0), (x0 + w - 2, y0), (x0 + w - 1, y0 + 1)}   # cantó doblegat
    paper(f, S, PAP_F, 4.2, w=w, h=h)
    f.px(x0 + w - 2, y0 + 1, PAP_F, 2.4)
    f.rect(x0 + 1, y0 + 1, x0 + w - 3, y0 + 7, head, lambda x, y: 2.8 - (y - y0) * 0.12 + (0.8 if y == y0 + 1 else 0))
    tw = sum(len(FONT[c][0]) + 1 for c in code) - 1
    f.text(x0 + 1 + (w - 3 - tw) // 2, y0 + 2, code, PAP_F, 5.6)
    # camps: etiqueta impresa + ratlla o casella
    for i, yy in enumerate(range(y0 + 10, y0 + h - (6 if sig else 2), 3)):
        f.rect(x0 + 2, yy, x0 + 4, yy, INKG, 1.4)
        if i % 2:
            for b in range(3):
                f.rect(x0 + 7 + b * 4, yy - 1, x0 + 9 + b * 4, yy + 1, INKG, 2.6)
                f.px(x0 + 8 + b * 4, yy, PAP_F, 4.4)
        else:
            f.rect(x0 + 6, yy + 1, x0 + w - 3, yy + 1, INKG, 2.8)
    return S


def scrap_cartell(f, S, seed, back=True, curl=True):
    """Tros de cartell de la Gavina: per darrere blanc; al cantó, la vora verda de davant que es gira."""
    paper(f, S, SIGN, 4.0)
    if curl:
        xs = [p[0] for p in S]
        ys = [p[1] for p in S]
        x1, y0 = max(xs), min(ys)
        # cantó de dalt a la dreta girat: es veu el verd del davant
        tri = {(x, y) for (x, y) in S if (x1 - x) + (y - y0) < 5}
        for p in tri:
            f.erase(*p)
        F = {(x1 - 4 + i, y0 + 1 + j) for i in range(5) for j in range(5) if i - j <= 0 and i + j <= 4}
        F = {(x, y) for (x, y) in F if (x, y) in S}
        f.drop(F, -1.2, -1, 1)
        f.fill(F, CORPG, 2.6, rim=(0.8, -0.6))
    return S


def beam(f, x0, x1, y0, mat, base, end=True, sheen=0.0):
    """Biga en I vista de costat (ala de dalt, ànima enfonsada, ala de baix) amb la secció en I al cap esquerre."""
    rows = [2.4, 1.8, 0.9, 0.3, -1.7, -1.3, -1.0, -0.8, 1.0, 0.2, -0.7]
    for x in range(x0, x1 + 1):
        g = (hr(x // 3, y0, 5) - 0.5) * 0.35 + (math.sin(x / 4.5) * sheen if sheen else 0)
        for j, r in enumerate(rows):
            l = base + r + g
            if x == x1:
                l -= 1.2                       # testa de la dreta, a l'ombra
            f.px(x, y0 + j, mat, l)
    if end:
        # secció en I al cap de l'esquerra (la testa tallada, de cara a la llum)
        ex = x0 - 5
        for j in range(11):
            if j <= 2 or j >= 8:
                xs = range(ex, x0)
            else:
                xs = range(ex + 2, ex + 4)
            for x in xs:
                l = base + 1.4 - j * 0.08
                if j in (2, 10):
                    l -= 0.8
                if x == ex or j in (0, 8):
                    l += 0.6
                f.px(x, y0 + j, mat, l)
        # buits de l'ànima a la testa (ombra de les ales)
        for j in range(3, 8):
            f.shade(ex + 4, y0 + j, -0.4)


def finish(f):
    return f.render()


# ─── Icones de Suma Zero (el mateix dibuix de volum que els personatges) ─────

def caixa_cartro(f):
    """La caixa del router, oberta, amb les solapes enlaire i l'etiqueta."""
    S = f.R(10, 10, 37, 24)
    f.drop(S)
    f.fill(S, MANI, lambda x, y: 3.0 - (x - 10) / 27 * 1.2 - (0.8 if y == 10 else 0), rim=(0.6, -1.0))
    f.fill(f.P([(10, 10), (6, 3), (19, 4), (21, 10)]), MANI, lambda x, y: 4.2 - (y - 3) * 0.12)
    f.fill(f.P([(37, 10), (42, 4), (29, 3), (27, 10)]), MANI, lambda x, y: 2.6 - (y - 3) * 0.1)
    f.rect(11, 11, 36, 12, MANI, 0.6)
    f.rect(15, 15, 26, 19, PAP_W, 4.4, rim=(0.4, -1.2))
    f.rect(17, 17, 24, 17, INKG, 1.4)
    f.rect(29, 14, 34, 22, MANI, 2.0)                                   # cinta d'embalar arrencada


def cable_alimentacio(f):
    """El cable de la cafetera: l'endoll, el cable enrotllat i el connector."""
    pts = [(14, 14), (19, 20), (24, 9), (29, 20), (34, 13)]
    for p0, p1 in zip(pts, pts[1:]):
        f.limb(p0, p1, 1.1, 1.1, PLAST, 2.8, amp=2.0)
    S = f.R(5, 9, 13, 19)
    f.drop(S)
    f.fill(S, PLAST, lambda x, y: 3.6 - (x - 5) * 0.2, rim=(0.6, -1.2))
    f.rect(1, 11, 4, 12, ACER, 5.2)
    f.rect(1, 16, 4, 17, ACER, 4.6)
    S = f.R(34, 9, 43, 18)
    f.drop(S)
    f.fill(S, PLAST, lambda x, y: 3.2 - (x - 34) * 0.2, rim=(0.6, -1.2))
    f.rect(37, 12, 40, 15, DARK, 1.0)


def pizza(f):
    """La pizza de demà: quatre talls, tomàquet, formatge fos i alfàbrega."""
    S = f.E(24, 14, 15, 10)
    f.drop(S)
    f.fill(S, MANI, lambda x, y: 3.6 - (y - 4) * 0.08, rim=(0.6, -1.0))          # el cartró
    f.fill(f.E(24, 13, 12.5, 8.5), ORNG, lambda x, y: 4.4 - abs(y - 13) * 0.1)    # la crosta
    f.fill(f.E(24, 13, 10.5, 6.8), RED, 3.4, rim=None)
    for cx, cy, rx, ry in ((20, 11, 3.5, 2.2), (28, 15, 4, 2.4), (25, 10, 2.5, 1.6), (18, 15, 2.8, 1.8)):
        f.fill(f.E(cx, cy, rx, ry), SUNY, lambda x, y: 4.2 - (y - cy) * 0.4, rim=None)
    for x in range(14, 35):
        f.px(x, 13, ORNG, 1.4)
    for y in range(6, 21):
        f.px(24, y, ORNG, 1.4)
    f.dots([(30, 10), (31, 10), (17, 12)], CORPG, 3.0)


def auricular(f):
    """L'auricular esquerre de l'Iri: la copa vermella i un tros de diadema."""
    for i in range(14):
        a = math.pi * (0.45 + 0.5 * i / 13)
        f.px(30 + 13 * math.cos(a), 20 - 15 * math.sin(a), PLAST, 4.4)
        f.px(30 + 13 * math.cos(a), 21 - 15 * math.sin(a), PLAST, 2.6)
    S = f.E(19, 15, 7.5, 10)
    f.drop(S)
    f.fill(S, PLAST, 3.0, rim=(0.8, -1.2))
    f.fill(f.E(20, 15, 5.6, 8.4), RED, lambda x, y: 4.8 - (x - 15) * 0.25 - (y - 7) * 0.08, rim=(0.8, -1.0))
    f.fill(f.E(17.6, 15, 2.4, 5.0), DARK, 2.0, rim=None)


ICONS = {fn.__name__: fn for fn in (
    caixa_cartro, cable_alimentacio, pizza, auricular,
)}


def render(item_id):
    """Imatge RGBA de 49×27 de l'objecte, o None si no en té."""
    fn = ICONS.get(item_id)
    if fn is None:
        return None
    f = Ic()
    fn(f)
    return f.render()
