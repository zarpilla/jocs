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
    'J': ('..#', '..#', '..#', '#.#', '.#.'), 'H': ('#.#', '#.#', '###', '#.#', '#.#'),
    '4': ('#.#', '#.#', '###', '..#', '..#'), '5': ('###', '#..', '##.', '..#', '##.'),
    '8': ('###', '#.#', '###', '#.#', '###'),
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
    """Els auriculars de diadema de l'Iri: la diadema negra i les dues copes vermelles."""
    for i in range(72):
        a = math.pi * i / 71
        f.px(24 - 12 * math.cos(a), 17 - 14 * math.sin(a), PLAST, 4.4)
        f.px(24 - 12 * math.cos(a), 18 - 14 * math.sin(a), PLAST, 2.6)
    for cx, sx in ((12, 1), (36, -1)):
        S = f.E(cx, 18, 4.6, 6.6)
        f.drop(S)
        f.fill(S, PLAST, 3.0, rim=(0.8, -1.2))
        f.fill(f.E(cx + sx * 1.2, 18, 3.0, 5.0), RED, lambda x, y: 4.8 - (y - 13) * 0.2, rim=(0.8, -1.0))


def auriculars_boto(f):
    """Dos auriculars de botó de recanvi, negres amb un punt vermell, units per un fil."""
    for x in range(17, 32):
        f.px(x, 20 + round(2.5 * math.sin(math.pi * (x - 17) / 14)), PLAST, 2.4)
    for cx in (14, 34):
        S = f.E(cx, 13, 4.2, 4.2)
        f.drop(S)
        f.fill(S, PLAST, lambda x, y: 3.6 - (y - 9) * 0.15, rim=(0.8, -1.2))
        f.fill(f.E(cx, 13, 1.6, 1.6), RED, 4.6, rim=None)
        for y in range(16, 21):
            f.px(cx + (2 if cx < 24 else -2), y, PLAST, 3.0)


# Materials de l'Acte 1
NETB = M((6, 20, 50), (12, 40, 96), (24, 70, 150), (46, 110, 200), (100, 160, 236), (180, 214, 252))   # cable de xarxa, blau
CLEAR = M((60, 70, 80), (120, 132, 140), (176, 186, 192), (216, 224, 228), (244, 248, 250))           # plàstic transparent
FOIL = M((40, 44, 52), (86, 92, 104), (136, 142, 152), (186, 190, 198), (226, 228, 232), (250, 250, 252))
BREAD = M((60, 30, 10), (112, 62, 22), (164, 104, 44), (206, 148, 76), (232, 190, 120), (248, 224, 170))
TUNA = M((70, 50, 40), (130, 100, 80), (184, 154, 126), (220, 196, 166))
GOLDK = M((48, 30, 6), (100, 70, 16), (160, 120, 30), (214, 172, 60), (244, 214, 110), (255, 244, 190))   # clau de llautó
NAPK = M((70, 70, 84), (140, 140, 150), (196, 196, 200), (230, 230, 230), (248, 248, 246), (255, 255, 255))
LEATHB = M((26, 12, 8), (54, 26, 14), (88, 46, 22), (124, 70, 34), (160, 98, 50), (196, 132, 74), (226, 170, 110))
BADGE = M((40, 44, 56), (100, 106, 120), (170, 176, 188), (220, 224, 230), (246, 248, 250), (255, 255, 255))
NAVY = M((6, 10, 24), (14, 22, 50), (26, 40, 84), (42, 62, 120), (70, 96, 160))


def cable_xarxa(f):
    """El cable de xarxa blau, enrotllat, amb el connector transparent (i una mossegada d'en Diu)."""
    for k, (cx, cy, rx, ry) in enumerate(((20, 13, 11, 7.5), (25, 14, 10, 6.5))):   # dues voltes netes
        f.ring(cx, cy, rx, ry, NETB, 3.4 - k * 0.6, th=1.8)
    for i in range(40):                                                  # la llum de dalt a cada volta
        a = math.pi * (1.1 + 0.8 * i / 39)
        f.px(round(20 + 11 * math.cos(a)), round(13 + 7.5 * math.sin(a)), NETB, 4.8)
    f.limb((32, 16), (39, 20), 1.0, 1.0, NETB, 3.0, amp=1.6)           # la cua que en surt
    S = f.R(39, 17, 46, 23)                                              # el connector RJ45
    f.drop(S)
    f.fill(S, CLEAR, lambda x, y: 3.4 - (x - 39) * 0.15, rim=(0.8, -1.2))
    for x in range(41, 46, 1):
        f.px(x, 22, GOLDK, 4.0 if x % 2 else 2.4)                        # els contactes daurats
    f.rect(40, 16, 43, 16, CLEAR, 2.6)                                   # la pestanya
    f.dots([(13, 17), (14, 18), (12, 18)], DARK, 1.0)                    # les dents del gat


def entrepa(f):
    """L'entrepà de tonyina: mitja barra embolicada en paper d'alumini, amb l'enciam que sobresurt."""
    S = f.P([(6, 15), (10, 9), (40, 7), (44, 12), (41, 19), (9, 21)])
    f.drop(S)
    f.fill(S, BREAD, lambda x, y: 4.2 - (y - 7) * 0.12 - (x - 6) * 0.01, rim=(0.6, -1.2))
    for x in range(12, 40, 6):                                           # els talls de la crosta
        f.px(x, 10 - (x // 20), BREAD, 2.0)
        f.px(x + 1, 11 - (x // 20), BREAD, 2.0)
    for x in range(8, 42):                                               # el farcit: enciam i tonyina
        y = 15 + round((x - 8) * -0.05)
        f.px(x, y, CORPG, 3.6 if x % 3 else 2.4)
        if x % 4 != 1:
            f.px(x, y + 1, TUNA, 3.0)
    S2 = f.P([(26, 6), (45, 9), (46, 17), (42, 22), (26, 22)])           # el paper d'alumini, mig obert
    f.fill(S2, FOIL, lambda x, y: 3.8 + (1.2 if (x + y * 2) % 7 == 0 else 0) - (x - 26) * 0.06, rim=(0.8, -1.2))
    for (x, y) in ((30, 10), (34, 14), (38, 11), (41, 18), (31, 18)):
        f.shade(x, y, 1.6)


def clau_casa(f):
    """La clau de casa, de llautó, amb l'anella i un clauer de plàstic groc amb una etiqueta."""
    f.ring(12, 13, 6.5, 6.5, ACER, 4.0, th=1.4)                        # l'anella
    S = f.E(24, 13, 5.5, 5.5)                                           # el cap de la clau
    f.drop(S)
    f.fill(S, GOLDK, lambda x, y: 4.2 - (x - 19) * 0.12 - (y - 8) * 0.12, rim=(0.8, -1.2))
    f.fill(f.E(23, 13, 1.6, 1.6), DARK, 0.6, rim=None)                  # el forat
    S = f.R(29, 12, 43, 15)                                              # la tija
    f.drop(S)
    f.fill(S, GOLDK, lambda x, y: 3.8 - (y - 12) * 0.4, rim=(0.6, -1.0))
    for (x, d) in ((33, 2), (35, 3), (37, 1), (39, 3), (41, 2)):         # les dents
        f.rect(x, 16, x + 1, 15 + d, GOLDK, 3.0)
    S = f.P([(4, 18), (10, 17), (12, 25), (5, 26)])                      # el clauer groc amb l'etiqueta
    f.drop(S)
    f.fill(S, SUNY, 3.8, rim=(0.6, -1.0))
    f.dots([(6, 21), (7, 21), (8, 21), (6, 23), (8, 23)], INKB, 2.0)


def tap(f):
    """El clauer d'en Tomàs: un tap vermell de la cervesera, amb l'anella i dues claus."""
    S = f.E(15, 14, 10, 8)
    f.drop(S)
    f.fill(S, RED, lambda x, y: 4.0 - (x - 5) * 0.1 - (y - 6) * 0.14, rim=(0.8, -1.2))
    for i in range(16):                                                  # l'estriat del tap
        a = i / 16 * 2 * math.pi
        f.px(round(15 + 9.4 * math.cos(a)), round(14 + 7.4 * math.sin(a)), RED, 1.6)
    S = f.E(15, 13, 4, 3.4)
    f.fill(S, BRASS, lambda x, y: 4.6 - (x - 11) * 0.2 - (y - 10) * 0.3, rim=(0.8, -1.0))   # el disc de llautó
    f.dots([(14, 12), (16, 12), (15, 14)], BRASS, 2.0)
    f.ring(29, 12, 4.5, 4.5, ACER, 4.2, th=1.2)                          # l'anella
    for k, (mat, y0) in enumerate(((ACER, 8), (GOLDK, 15))):             # les dues claus
        S = f.E(36, y0 + 2, 3, 3)
        f.drop(S)
        f.fill(S, mat, 4.0, rim=(0.8, -1.0))
        f.rect(38, y0 + 1, 46, y0 + 3, mat, 3.6, rim=(0.6, -1.0))
        f.rect(42, y0 + 4, 43, y0 + 5, mat, 2.6)
        f.rect(45, y0 + 4, 45, y0 + 5, mat, 2.6)


def recepta(f):
    """La recepta secreta: una servilleta de bar, plegada, escrita amb bolígraf vermell."""
    S = f.P([(11, 3), (37, 4), (38, 24), (12, 24)])
    f.drop(S)
    f.fill(S, NAPK, lambda x, y: 4.6 - (x - 11) * 0.03 - (y - 3) * 0.02, rim=(0.6, -1.0))
    for y in range(5, 24, 3):                                            # el gofrat de la servilleta
        for x in range(13, 37, 3):
            f.shade(x, y, -0.5)
    f.fill(f.P([(29, 18), (38, 18), (38, 24)]), NAPK, 3.0, rim=(0.4, -1.0))   # el cantó plegat
    f.text(15, 6, '1.', STAMP, 2.0)
    f.scrib(21, 33, 8, STAMP, 2.0, seed=3)
    f.text(15, 13, '2.', STAMP, 2.0)
    f.scrib(21, 30, 15, STAMP, 2.0, seed=5)
    f.scrib(15, 25, 20, STAMP, 2.2, seed=8, dens=0.9)                   # el subratllat


def comandament(f):
    """El comandament de la tele: negre, llarg, amb el botó vermell i la creueta."""
    S = f.P([(5, 10), (42, 7), (44, 15), (7, 19)])
    f.drop(S)
    f.fill(S, PLAST, lambda x, y: 2.4 - (y - 7) * 0.12, rim=(0.8, -1.2))
    f.fill(f.E(10, 13, 2, 2), RED, 4.2, rim=None)                       # el botó d'engegar
    for i in range(4):                                                   # el teclat numèric
        for j in range(2):
            f.px(16 + i * 3, 11 + j * 3, PLAST, 4.8)
    S = f.E(34, 11, 3, 2.6)                                              # la creueta
    f.fill(S, PLAST, 3.6, rim=(0.6, -0.8))
    f.px(34, 11, PLAST, 1.0)
    f.px(41, 10, RED, 3.0)                                               # el led de l'infraroig


def maleti(f):
    """El maletí de pell, amb la nansa, els tancaments i l'adhesiu groc."""
    S = f.R(6, 8, 42, 24)
    f.drop(S)
    f.fill(S, LEATHB, lambda x, y: 4.0 - (x - 6) * 0.04 - (y - 8) * 0.08, rim=(0.8, -1.4))
    f.rect(6, 12, 42, 12, LEATHB, 2.2)                                   # la tapa
    for x in range(18, 31):                                              # la nansa
        f.px(x, 4, LEATHB, 3.6)
        f.px(x, 5, LEATHB, 2.4)
    f.rect(18, 4, 18, 8, LEATHB, 3.0)
    f.rect(30, 4, 30, 8, LEATHB, 2.4)
    for x0 in (11, 35):                                                  # els tancaments
        f.rect(x0, 11, x0 + 2, 14, BRASS, 4.4, rim=(0.6, -1.0))
    S = f.R(14, 16, 24, 21)                                              # l'adhesiu «AGENDA 2019 — COMPTE, LLIMONA»
    f.fill(S, SUNY, 4.0, rim=(0.4, -0.8))
    f.scrib(15, 23, 18, INKG, 1.2, seed=2)
    f.scrib(15, 21, 20, INKG, 1.2, seed=4)
    for x in range(8, 41, 4):                                            # el pespunt
        f.px(x, 23, LEATHB, 5.0)


def ulleres(f):
    """Ulleres de pasta negra, gruixudes, sense graduació (però amb autoritat)."""
    for cx in (15, 33):
        S = f.E(cx, 14, 8, 6.5)
        f.drop(S)
        f.fill(S, DARK, 2.4, rim=(0.6, -0.4))
        f.fill(f.E(cx, 14, 4.6, 3.4), CYAN, lambda x, y, cx=cx: 1.6 + (1.8 if (x - cx) + (y - 14) < -3 else 0), rim=None)   # el vidre, amb un reflex
    f.rect(22, 11, 26, 12, DARK, 2.4)                                    # el pont
    f.rect(2, 10, 7, 11, DARK, 2.0)                                      # les potes
    f.rect(41, 10, 46, 11, DARK, 2.0)


def _badge(f, x0, y0, face, hair, lit=0.0):
    """Una acreditació plastificada del BCMU: la foto, el nom, la franja vermella de «manteniment»."""
    S = f.R(x0, y0, x0 + 17, y0 + 22)
    f.drop(S)
    f.fill(S, BADGE, lambda x, y: 4.6 + lit - (y - y0) * 0.03, rim=(0.8, -1.2))
    f.rect(x0 + 6, y0 - 2, x0 + 11, y0, ACER, 4.0, rim=(0.6, -1.0))      # la pinça
    f.rect(x0 + 1, y0 + 1, x0 + 16, y0 + 4, NAVY, 3.0)                   # la capçalera blava del banc
    f.dots([(x0 + 3 + i, y0 + 2) for i in range(0, 11, 2)], SUNY, 4.0)
    f.rect(x0 + 2, y0 + 6, x0 + 8, y0 + 13, CYAN, 3.4)                  # la foto
    f.fill(f.E(x0 + 5, y0 + 10, 2, 2.4), face, 3.6, rim=None)
    f.rect(x0 + 3, y0 + 7, x0 + 7, y0 + 8, hair, 2.0)
    for k in range(3):                                                   # el nom i el càrrec
        f.rect(x0 + 10, y0 + 7 + k * 2, x0 + 15 - k, y0 + 7 + k * 2, INKG, 1.4)
    f.rect(x0 + 1, y0 + 16, x0 + 16, y0 + 19, RED, 3.4)                  # la franja de manteniment
    f.dots([(x0 + 3 + i, y0 + 17) for i in range(0, 12, 3)], BADGE, 5.0)
    f.shade(x0 + 2, y0 + 1, 1.4)                                         # el reflex del plàstic
    f.shade(x0 + 3, y0 + 2, 1.0)


def acreditacions(f):
    """Les dues acreditacions, una damunt de l'altra (la de l'Iri i la de la Vet)."""
    _badge(f, 8, 4, SKIN, HAIR, lit=-0.4)
    _badge(f, 22, 3, SKIN, HAIR)


def acreditacio(f):
    """Una acreditació, penjada del cordó blau marí del banc."""
    for i in range(14):                                                  # el cordó
        f.px(8 + i, 2 + round(math.sin(i / 4) * 1.2), NAVY, 3.0)
        f.px(36 - i, 2 + round(math.sin(i / 4) * 1.2), NAVY, 2.4)
    _badge(f, 15, 4, SKIN, HAIR)


# ─── Acte 2: el BCMU ────────────────────────────────────────────────────────
CHEESE = M((70, 50, 10), (136, 104, 26), (196, 160, 50), (232, 204, 92), (248, 230, 150), (255, 246, 200))
HAM = M((70, 20, 30), (130, 44, 56), (186, 84, 92), (222, 130, 134), (244, 178, 176))
MORT = M((90, 40, 50), (150, 76, 86), (200, 120, 126), (230, 164, 166), (246, 204, 204))
WRAP = M((20, 30, 50), (40, 64, 104), (70, 110, 170), (120, 160, 214), (190, 216, 244))          # embolcall de màquina, blau
BUCKET = M((6, 22, 60), (12, 44, 110), (24, 76, 170), (50, 114, 220), (110, 166, 248), (190, 220, 255))
WARNY = M((60, 40, 6), (130, 92, 10), (200, 150, 20), (240, 196, 40), (255, 228, 100), (255, 248, 190))
FIRE = M((40, 6, 8), (90, 14, 16), (150, 24, 24), (200, 40, 36), (236, 76, 62), (252, 140, 120))
CARDW = M((40, 44, 56), (100, 106, 120), (170, 176, 188), (220, 224, 230), (246, 248, 250), (255, 255, 255))


def entrepa_suis(f):
    """L'entrepà de la màquina: mig sandvitx triangular de pa de motlle, de tres quarts: per dalt el pa amb la crosta,
    i al tall de davant les capes (pa, pernil, formatge amb forats, pa). Amb l'etiqueta del preu."""
    top = f.P([(6, 14), (30, 3), (42, 14)])                               # la cara de dalt
    cut = f.R(6, 15, 42, 22)                                              # el tall, de cara
    f.drop(top | cut)
    f.fill(top, PAP_C, lambda x, y: 4.6 - (y - 3) * 0.05, rim=None)
    for (x, y) in top:                                                    # la crosta
        if (x - 1, y) not in top or (x + 1, y) not in top or (x, y - 1) not in top:
            f.px(x, y, BREAD, 3.2)
    rows = [(BREAD, 3.0), (PAP_C, 4.2), (HAM, 3.8), (HAM, 3.0), (CHEESE, 4.4), (CHEESE, 3.6), (PAP_C, 3.8), (BREAD, 2.4)]
    for i, (mat, l) in enumerate(rows):
        f.rect(6, 15 + i, 42, 15 + i, mat, lambda x, y, l=l: l - (x - 6) * 0.03)
    for x in (13, 24, 34):                                                # els forats del formatge
        f.px(x, 19, CHEESE, 1.8)
        f.px(x + 1, 20, CHEESE, 2.2)
    f.rect(6, 15, 6, 22, BREAD, 2.0)
    f.rect(42, 15, 42, 22, BREAD, 1.6)
    S = f.R(30, 4, 46, 10)                                                # l'etiqueta del preu de la màquina
    f.drop(S)
    f.fill(S, WRAP, 3.0, rim=(0.6, -1.0))
    f.text(32, 5, '8.50', CARDW, 5.6)


def entrepa_ballester(f):
    """L'entrepà d'en Ballester: una barra embolicada en paper d'alumini, oberta per un cap (mortadel·la)."""
    S = f.P([(5, 12), (9, 7), (42, 6), (46, 11), (43, 20), (8, 21)])
    f.drop(S)
    f.fill(S, FOIL, lambda x, y: 4.6 - (y - 6) * 0.14 + (0.8 if y == 8 else 0), rim=(0.8, -1.4))
    for (a, b) in (((16, 8), (20, 19)), ((30, 7), (27, 20)), ((38, 8), (41, 18))):   # els plecs, en diagonal
        n = max(abs(b[0] - a[0]), abs(b[1] - a[1]))
        for i in range(n + 1):
            x = round(a[0] + (b[0] - a[0]) * i / n)
            y = round(a[1] + (b[1] - a[1]) * i / n)
            f.shade(x, y, -1.4)
            f.shade(x + 1, y, 1.2)
    S2 = f.E(9, 14, 4, 6.5)                                              # el cap obert: pa i mortadel·la
    f.fill(S2, BREAD, lambda x, y: 4.0 - (x - 5) * 0.1, rim=(0.6, -1.0))
    f.fill(f.E(9, 14, 2.4, 4.6), MORT, lambda x, y: 3.6 - (y - 10) * 0.1, rim=None)
    f.dots([(8, 12), (10, 15), (9, 17)], PAP_C, 4.6)                     # els daus de greix


def targeta(f):
    """La targeta de planta de la Rius: plàstic blanc, banda blau marí del banc, la foto (enfadada) i el xip."""
    S = f.P([(8, 6), (41, 4), (42, 22), (9, 24)])
    f.drop(S)
    f.fill(S, CARDW, lambda x, y: 4.6 - (x - 8) * 0.02 - (y - 4) * 0.03, rim=(0.8, -1.2))
    f.fill(f.P([(8, 7), (41, 5), (41, 9), (8, 11)]), NAVY, 3.0, rim=None)   # la banda
    f.dots([(12 + i, 8 - i // 9) for i in range(0, 26, 3)], SUNY, 4.2)
    f.rect(11, 13, 18, 21, CYAN, 3.4)                                    # la foto
    f.fill(f.E(14, 18, 2.2, 2.6), SKIN, 3.6, rim=None)
    f.rect(12, 14, 17, 15, HAIR, 2.4)
    f.dots([(13, 17), (15, 17)], DARK, 1.0)                              # les celles arrufades
    f.rect(13, 20, 15, 20, DARK, 1.6)
    f.rect(31, 13, 37, 18, GOLDK, 4.0, rim=(0.6, -1.0))                  # el xip
    f.rect(34, 13, 34, 18, GOLDK, 2.4)
    f.rect(31, 15, 37, 15, GOLDK, 2.4)
    for k in range(2):
        f.rect(21, 14 + k * 3, 28 - k * 2, 14 + k * 3, INKG, 1.4)
    f.text(21, 19, '3', RED, 3.4)                                        # el tercer pis
    f.shade(10, 12, 1.6)


def compte_nomines(f):
    """El compte de les nòmines: un full de llibreta arrencat, amb el número escrit a mà i subratllat dues vegades."""
    S = torn(f.P([(9, 3), (40, 5), (39, 25), (8, 23)]), 't', seed=4, depth=1)
    paper(f, S, PAP_C, 4.4, w=32, h=22)
    for y in range(8, 25, 3):                                            # el ratllat
        for x in range(10, 39):
            if (x, y) in S:
                f.px(x, y, RULE, 1.4)
    f.text(11, 7, 'ES76', INKB, 1.4)
    f.text(11, 13, '2100', INKB, 1.4)
    f.text(30, 13, '48', INKB, 1.4)
    f.text(11, 19, '0099', INKB, 1.4)
    f.text(28, 19, '!', STAMP, 2.0)
    f.scrib(11, 34, 25, INKB, 1.6, seed=6, dens=1.0, tall=0)
    f.fill(f.P([(33, 3), (40, 5), (38, 10)]), PAP_C, 2.6, rim=(0.4, -1.0))   # el cantó doblegat


def galleda(f):
    """La galleda blava de fregar: un tronc de con amb la nansa d'acer i l'escorredor."""
    S = f.P([(11, 8), (37, 8), (34, 25), (14, 25)])
    f.drop(S)
    f.fill(S, BUCKET, lambda x, y: 3.6 + 1.6 * math.cos((x - 19) / 11) - 1.0 - (y - 8) * 0.03, rim=(0.6, -1.4))
    f.fill(f.E(24, 8, 13.5, 2.6), BUCKET, 4.4, rim=(0.6, -0.8))           # la vora
    f.fill(f.E(24, 8, 11.5, 1.6), BUCKET, 1.4, rim=None)                  # per dins, fosc
    f.rect(12, 12, 36, 12, BUCKET, 2.4)                                   # les nervadures
    f.rect(14, 21, 34, 21, BUCKET, 2.4)
    for i in range(29):                                                   # la nansa
        x = 10 + i
        y = round(8 - 6 * math.sin(math.pi * i / 28))
        f.px(x, y, ACER, 4.4 if i < 14 else 3.2)
    f.dots([(10, 8), (38, 8)], ACER, 2.4)
    f.rect(32, 4, 40, 7, PLAST, 3.4, rim=(0.6, -1.0))                     # l'escorredor groc
    f.rect(33, 5, 39, 6, WARNY, 3.6)


def cartell(f):
    """El cartell de «Neteja en curs», plegat: dues ales grogues en forma de A, amb el ninot que rellisca."""
    L = f.P([(8, 24), (20, 3), (24, 3), (16, 24)])                       # l'ala del darrere
    f.fill(L, WARNY, lambda x, y: 2.6 - (y - 3) * 0.02, rim=(0.4, -1.0))
    S = f.P([(15, 25), (23, 2), (33, 2), (43, 25)])                      # l'ala del davant
    f.drop(S)
    f.fill(S, WARNY, lambda x, y: 4.4 - (x - 16) * 0.03, rim=(0.8, -1.4))
    f.rect(23, 1, 33, 2, PLAST, 2.6, rim=(0.6, -0.8))                    # la nansa
    f.fill(f.E(31, 7, 1.6, 1.6), DARK, 1.0, rim=None)                    # el ninot que rellisca, ben gros
    for a, b in (((30, 9), (27, 14)), ((27, 14), (31, 17)), ((31, 17), (34, 15)), ((27, 14), (23, 17)),
                 ((29, 11), (34, 10)), ((29, 11), (25, 10))):
        n = max(abs(b[0] - a[0]), abs(b[1] - a[1]))
        for i in range(n + 1):
            f.px(round(a[0] + (b[0] - a[0]) * i / n), round(a[1] + (b[1] - a[1]) * i / n), DARK, 1.0)
    f.rect(21, 19, 37, 19, DARK, 1.2)                                    # el terra mullat
    f.dots([(23, 21), (27, 21), (31, 21), (35, 21), (25, 22), (33, 22)], CYAN, 3.0)


def extintor(f):
    """L'extintor vermell, ajagut: el cos, la vàlvula d'acer amb la maneta i la mànega negra."""
    f.drop(f.R(8, 8, 37, 21))
    f.hcyl(10, 36, 14.5, 6.5, FIRE, 3.0, amp=2.6, spec=1.6)
    f.fill(f.E(9, 14.5, 2.4, 6.5), FIRE, 2.0, rim=None)                   # el cul arrodonit
    f.fill(f.E(37, 14.5, 2, 6.3), FIRE, 3.4, rim=None)
    f.rect(17, 10, 27, 18, CARDW, 4.2, rim=(0.4, -0.8))                   # l'etiqueta
    f.rect(18, 11, 26, 12, FIRE, 3.0)
    f.dots([(19 + i, 15) for i in range(0, 8, 2)] + [(19 + i, 17) for i in range(0, 6, 2)], INKG, 1.4)
    f.hcyl(39, 43, 14.5, 2.4, ACER, 4.0)                                  # la vàlvula
    f.rect(40, 9, 46, 10, ACER, 4.4, rim=(0.6, -1.0))                     # la maneta
    f.px(45, 11, ACER, 2.4)
    f.dots([(42, 12)], SUNY, 4.4)                                         # el passador groc
    for i in range(16):                                                   # la mànega
        f.px(42 - i, 20 + round(math.sin(i / 3) * 1.6), DARK, 2.6)
        f.px(42 - i, 21 + round(math.sin(i / 3) * 1.6), DARK, 1.6)


def clau_llibre(f):
    """La clau del Llibre Major: grossa, antiga, de llautó, amb l'ull treballat i la cadena del collaret."""
    for i in range(12):                                                   # la cadena
        x, y = 3 + i * 1.5, 3 + round(math.sin(i / 2.2) * 2) + i * 0.4
        f.ring(x, y, 1.2, 1.0, BRASS, 4.0 if i % 2 else 2.8, th=0.8)
    S = f.E(14, 14, 6.5, 6.5)                                             # l'ull
    f.drop(S)
    f.fill(S, GOLDK, lambda x, y: 4.4 - (x - 8) * 0.12 - (y - 8) * 0.12, rim=(0.8, -1.2))
    f.fill(f.E(14, 14, 3.4, 3.4), DARK, 0.4, rim=None)
    f.fill(f.E(14, 14, 1.4, 1.4), GOLDK, 3.6, rim=None)                   # el trèvol del mig
    for (x, y) in ((14, 10), (10, 14), (18, 14), (14, 18)):
        f.px(x, y, GOLDK, 2.4)
    S = f.R(20, 12, 44, 16)                                               # la tija, rodona
    f.drop(S)
    f.hcyl(20, 44, 14, 2.4, GOLDK, 3.4)
    f.rect(21, 11, 23, 17, GOLDK, 3.0, rim=(0.6, -1.0))                   # l'anell del coll
    S = f.R(36, 17, 44, 24)                                               # el paletó, amb les guardes
    f.drop(S)
    f.fill(S, GOLDK, lambda x, y: 3.6 - (y - 17) * 0.1, rim=(0.6, -1.2))
    for (x, y) in ((38, 19), (38, 20), (41, 22), (41, 23), (43, 19)):
        f.px(x, y, DARK, 0.6)


def clauer(f):
    """El clauer turístic «Visiteu Ginebra»: una anella sense cap clau i una placa d'esmalt amb la creu suïssa."""
    f.ring(10, 11, 6, 6, ACER, 4.2, th=1.4)                               # l'anella, buida
    f.limb((15, 14), (19, 15), 0.8, 0.8, ACER, 3.4, amp=1.4)             # la cadeneta
    S = f.R(19, 5, 47, 23)                                                # la placa
    f.drop(S)
    f.fill(S, NAVY, lambda x, y: 3.2 - (y - 5) * 0.04, rim=(0.8, -1.2))
    f.rect(20, 6, 46, 6, SUNY, 3.6)                                       # el filet daurat
    f.rect(20, 22, 46, 22, SUNY, 2.8)
    f.text(20, 8, 'GINEBRA', CARDW, 5.0)
    S = f.R(29, 14, 37, 20)                                               # l'escut vermell amb la creu
    f.fill(S, RED, 3.6, rim=(0.6, -0.8))
    f.rect(32, 15, 34, 19, CARDW, 5.0)
    f.rect(30, 16, 36, 18, CARDW, 5.0)
    f.shade(20, 7, 1.6)


ICONS = {fn.__name__: fn for fn in (
    caixa_cartro, cable_alimentacio, pizza, auricular, auriculars_boto,
    cable_xarxa, entrepa, clau_casa, tap, recepta, comandament, maleti, ulleres, acreditacions, acreditacio,
    entrepa_suis, entrepa_ballester, targeta, compte_nomines, galleda, cartell, extintor, clau_llibre, clauer,
)}
ICONS['auriculars'] = auricular   # l'objecte de l'Iri es diu «auriculars»


def render(item_id):
    """Imatge RGBA de 49×27 de l'objecte, o None si no en té."""
    fn = ICONS.get(item_id)
    if fn is None:
        return None
    f = Ic()
    fn(f)
    return f.render()
