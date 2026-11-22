"""
Icones d'inventari de Ferro-9 en pixel art HD: es dibuixen píxel a píxel a la mida real de la casella
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
    CONTORN_FOSC = True

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


# ─── Icones ─────────────────────────────────────────────────────────────────

def clau_anglesa(f):
    """Clau anglesa de ferro-9 (acer blavós reluent), amb el segell «Lot 1» gravat al mànec."""
    a, b = (6, 22), (33, 11)
    pix = f.limb(a, b, 2.3, 2.6, F9, 4.4, amp=2.6)
    f.shine(pix, 0.82, 1.6)
    # forat de penjar al cap del mànec
    f.erase(7, 21); f.px(8, 21, F9, 1.0); f.px(7, 20, F9, 1.6)
    # cap: disc amb la boca oberta en la direcció del mànec
    cx, cy = 38.5, 8.5
    ux, uy = (b[0] - a[0]), (b[1] - a[1])
    n = math.hypot(ux, uy)
    ux, uy = ux / n, uy / n
    head = {}
    for y in range(0, 17):
        for x in range(30, 48):
            dx, dy = x - cx, y - cy
            if (dx / 6.6) ** 2 + (dy / 6.2) ** 2 > 1:
                continue
            u, v = dx * ux + dy * uy, -dx * uy + dy * ux
            if u > -0.6 and abs(v) < 1.7:
                continue                                          # la boca
            nz = max(0.0, 1 - (dx / 6.6) ** 2 - (dy / 6.2) ** 2) ** 0.5
            head[(x, y)] = (dx / 6.6, dy / 6.2, nz)
    for (x, y), (nx, ny, nz) in head.items():
        l = 4.2 + 2.6 * (nx * LX + ny * LY + nz * LZ - 0.35)
        f.px(x, y, F9, l)
    f.shine(head, 0.78, 1.8)
    # vores de la boca (cares interiors)
    for (x, y) in head:
        dx, dy = x - cx, y - cy
        u, v = dx * ux + dy * uy, -dx * uy + dy * ux
        if u > -0.6 and 1.7 <= abs(v) < 2.7:
            f.shade(x, y, 1.2 if v < 0 else -1.6)
    # cargol sens fi (moleteig) sota la boca
    for i in range(5):
        x, y = round(34 + i * ux * 1.1 + 2.6 * -uy), round(12 + i * uy * 1.1 + 2.6 * ux)
        f.px(x, y, F9, 2.0 if i % 2 else 5.0)
    # segell gravat: puntets foscos al llarg del mànec
    for t in (0.34, 0.42, 0.5, 0.58):
        x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        f.px(round(x), round(y), F9, 2.2)


def formulari_27b(f):
    """Formulari 27-B en blanc: capçalera vermella, caselles buides."""
    form(f, 15, 2)


def formulari_segellat(f):
    """El 27-B amb un segell vermell gros, rodó, que sobresurt del full."""
    form(f, 13, 2)
    f.stamp(29, 18, 5.2, 2.6, seed=1)


def formulari_triplicat(f):
    """Tres còpies del 27-B ventallades, cadascuna amb el seu segell vermell a la part que es veu."""
    for i, (x, y) in enumerate(((3, 2), (14, 2), (26, 3))):
        form(f, x, y, w=19, h=21)
    for i, (x, y) in enumerate(((3, 2), (14, 2), (26, 3))):
        if i < 2:
            f.stamp(x + 6, y + 15, 3.4, 2.6, seed=i + 3)
        else:
            f.stamp(x + 11, y + 15, 4.2, 2.6, seed=i + 3)


def plomall(f):
    """Plomall de plomes d'estruç: mànec de fusta torneada, virolla de llautó i un plomall gros."""
    pix = f.limb((3, 16), (21, 13), 1.3, 1.5, WOOD, 4.0, amp=2.2)
    f.shine(pix, 0.85, 1.0)
    for x in (8, 14):
        f.shade(x, 15 - (x - 3) // 6, -1.2)
    f.rect(21, 11, 24, 15, BRASS, lambda x, y: 4.6 - (y - 11) * 0.5 - (x - 21) * 0.2, rim=(0.4, -1.0))
    f.px(22, 11, BRASS, 6.0)
    # plomall: bulb que s'eixampla, amb plomes que surten de la virolla
    OX, OY = 22, 13
    for y in range(2, 25):
        for x in range(24, 47):
            dx, dy = x - 34.5, (y - 13) / 1.05
            r = math.hypot(dx / 11.6, dy / 10.6)
            rr = 1 + (hr(x, y, 8) - 0.5) * 0.28
            if r > rr or x < 25 + abs(y - 13) * 0.55:
                continue
            ang = math.atan2(y - OY, x - OX)
            strand = math.sin(ang * 30 + hr(int(ang * 15), 3) * 3) * 0.7
            lvl = 3.6 - dy / 10.6 * 1.3 - (x - 34.5) / 12 * 0.5 + strand - r ** 3 * 0.9
            if hr(int(ang * 15), 11) > 0.78:
                lvl -= 1.3
            f.px(x, y, FEATH, lvl)
    # puntes soltes
    for x, y in ((46, 10), (46, 17), (43, 3), (44, 23)):
        if f.get(x - 1, y):
            f.px(x, y, FEATH, 2.6)


def segell(f):
    """Segell oficial: pom de fusta envernissada, coll de llautó, base de fusta amb placa i goma vermella."""
    SX = 24
    # empremta vermella al costat (de tant segellar)
    f.stamp(40, 19, 4.2, 2.2, seed=7)
    # base
    f.rect(SX - 10, 14, SX + 9, 21, WOOD, lambda x, y: 4.0 - (x - SX + 10) / 19 * 1.4 - (y - 14) * 0.1, rim=(0.8, -1.0))
    f.rect(SX - 10, 14, SX + 9, 14, WOOD, 5.2)
    f.rect(SX - 9, 22, SX + 8, 23, STAMP, lambda x, y: 3.0 - (y - 22) * 1.2)
    f.rect(SX - 7, 16, SX + 5, 19, BRASS, lambda x, y: 4.4 - (x - SX + 7) * 0.12, rim=(0.6, -1.0))
    for x in range(SX - 5, SX + 4, 2):
        f.px(x, 17 + (x // 2) % 2, BRASS, 2.0)
    # coll de llautó
    pix = f.limb((SX, 13), (SX, 9), 2.4, 2.0, BRASS, 4.0, amp=2.4)
    f.shine(pix, 0.8, 1.4)
    f.rect(SX - 3, 12, SX + 3, 13, BRASS, 2.6)
    # pom
    pix = f.ell(SX, 6, 5.0, 4.2, WOOD, 3.9, amp=2.6)
    f.shine(pix, 0.82, 2.0)


def clau_cambra(f):
    """Clau antiga de llautó, grossa: ull rodó amb lòbuls, canya llarga, paleta dentada i etiqueta de cartró."""
    # etiqueta penjada de l'ull amb un cordill
    f.line(8, 17, 12, 20, CLOTH, 2.8)
    T = f.P([(11, 19), (23, 19), (23, 25), (11, 25)])
    paper(f, T, MANI, 4.0)
    f.ring(13, 21.5, 0.9, 0.9, MANI, 1.2)
    f.rect(15, 21, 21, 21, STAMP, 2.4)
    f.rect(15, 23, 19, 23, INKG, 1.4)
    # ull: anella gruixuda amb tres lòbuls
    pix = f.ell(8, 10, 6.2, 6.2, BRASS, 3.8, amp=2.6)
    f.shine(pix, 0.8, 1.6)
    for p in f.E(8, 10, 2.6, 2.6):
        f.erase(*p)
    for (x, y) in f.E(8, 10, 3.6, 3.6) - f.E(8, 10, 2.6, 2.6):
        f.shade(x, y, 1.2 if x + y > 18 else -1.4)
    for (x, y) in ((8, 4), (2, 10), (8, 16)):
        f.shade(x, y, -1.4)
    # canya i collar
    pix = f.limb((14, 10), (40, 10), 1.8, 1.8, BRASS, 4.0, amp=2.4)
    f.shine(pix, 0.85, 1.6)
    for x in (16, 18):
        f.rect(x, 7, x, 13, BRASS, 5.0 if x == 16 else 2.2)
    # paleta amb les dents
    f.rect(35, 11, 43, 19, BRASS, lambda x, y: 4.2 - (x - 35) * 0.16 - (y - 11) * 0.12, rim=(0.6, -1.0))
    for x, y in ((37, 16), (37, 17), (37, 18), (37, 19), (38, 19), (40, 18), (40, 19), (42, 15), (43, 15), (43, 16)):
        f.erase(x, y)
    f.ell(42, 10, 2.2, 2.2, BRASS, 3.8, amp=2.0)


def llapis(f):
    """Llapis de fàbrica (pintat d'ocre) amb la punta afilada i el cul ben mossegat."""
    a, b = (5, 6), (34, 19)
    pix = f.limb(a, b, 2.2, 2.2, SUNY, 2.9, amp=2.0)
    f.shine(pix, 0.84, 1.0)
    # arestes de l'hexàgon: una ratlla clara i una de fosca al llarg
    for i in range(30):
        t = i / 29
        x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        f.shade(round(x + 0.6), round(y - 1.3), 0.8)
        f.shade(round(x - 0.4), round(y + 1.1), -0.6)
    # punta: fusta tallada i grafit
    tip = f.limb(b, (42, 23), 2.2, 0.6, PALE, 3.6, amp=1.6)
    for (x, y) in list(tip):
        if (x - b[0]) * 0.92 + (y - b[1]) * 0.4 > 1.3 * 0 and x >= 35 and (hr(x, y, 4) > 0.6):
            f.shade(x, y, -0.6)
    f.limb((40, 22), (44, 24), 0.9, 0.5, GRAPH, 2.0, amp=1.4)
    f.px(44, 24, GRAPH, 3.0)
    # cul mossegat: mossos i la fusta que queda al descobert
    for x, y in ((3, 5), (4, 3), (5, 3), (3, 7), (6, 4), (2, 6), (4, 8)):
        f.erase(x, y)
    for x, y in ((4, 4), (5, 4), (4, 5), (3, 6), (4, 7), (6, 5), (7, 4)):
        if f.get(x, y):
            f.px(x, y, PALE, 3.2 + hr(x, y) * 1.4)
    f.px(9, 6, SUNY, 1.2); f.px(11, 7, SUNY, 1.2); f.px(8, 9, SUNY, 1.2)   # marques de dents


def llibreta_torn(f):
    """Llibreta de torn de l'Iri: tapes de pell marró, cantell de fulls, goma vermella i etiqueta «TORN»."""
    x0, y0, x1, y1 = 13, 2, 35, 22
    # cantell dels fulls (gruix), a la dreta i a sota
    pages = f.R(x0 + 2, y0 + 2, x1 + 2, y1 + 2)
    f.fill(pages, PAP_C, lambda x, y: 3.4 - (0.9 if (x + y) % 2 and x > x1 else 0) - (0.9 if y > y1 and x % 2 else 0))
    f.rect(x1 + 2, y0 + 3, x1 + 2, y1 + 2, LEATH, 2.0)
    f.rect(x0 + 3, y1 + 2, x1 + 2, y1 + 2, LEATH, 2.0)
    # tapa
    C = f.R(x0, y0, x1, y1) - {(x0, y0), (x1, y0), (x0, y1), (x1, y1)}
    f.drop(C)
    f.fill(C, LEATH, lambda x, y: 3.6 - (x - x0) / 22 * 0.9 - (y - y0) / 22 * 0.9 + (hr(x, y, 2) - 0.5) * 0.5, rim=(0.9, -1.0))
    # llom
    f.rect(x0, y0 + 1, x0 + 2, y1 - 1, LEATH, lambda x, y: 2.4 + (0.9 if x == x0 + 1 else 0))
    # etiqueta
    f.rect(x0 + 6, y0 + 5, x0 + 18, y0 + 11, PAP_C, 4.4, rim=(0.4, -1.2))
    f.text(x0 + 7, y0 + 6, 'TORN', INKG, 0.6, sp=0)
    # goma elàstica vermella
    f.rect(x1 - 4, y0, x1 - 3, y1 + 2, RED, lambda x, y: 3.6 if x == x1 - 4 else 2.4)
    f.px(x1 - 4, y0, RED, 4.6)


def caixa_eines(f):
    """Caixa d'eines de fusta pintada de vermell, cantoneres de ferro, nansa i eines que sobresurten."""
    X0, X1, T, B = 5, 43, 11, 24
    # eines (darrere)
    f.rect(11, 4, 13, 11, WOOD, lambda x, y: 4.2 - (x - 11) * 0.8)                # mànec del martell
    f.rect(8, 3, 17, 5, F9, lambda x, y: 5.2 - (y - 3) * 0.8, rim=(0.6, -1.0))
    pix = f.limb((33, 10), (35, 4), 1.0, 1.0, F9, 4.0, amp=2.2)                    # clau anglesa
    f.ell(35.5, 3.6, 2.2, 1.6, F9, 4.2, amp=2.0)
    f.erase(36, 3)
    f.rect(38, 6, 42, 9, WOOD, lambda x, y: 4.0 - (x - 38) * 0.4, rim=(0.6, -1.0))  # mànec de serra
    f.erase(40, 7)
    # nansa de ferro
    for x in range(X0 + 4, X1 - 3):
        f.px(x, 7, IRON, 4.0)
        f.px(x, 8, IRON, 2.2)
    for xx in (X0 + 4, X1 - 4):
        f.rect(xx, 7, xx + 1, T - 1, IRON, lambda x, y: 3.6 if x == xx else 2.0)
    f.rect(19, 6, 29, 8, WOOD, lambda x, y: 4.4 - (y - 6) * 0.9, rim=(0.4, -0.8))
    # cos: taulons vermells
    S = f.R(X0, T, X1, B)
    f.drop(S)
    f.fill(S, RED, lambda x, y: 3.0 - (x - X0) / (X1 - X0) * 0.9 - (y - T) * 0.04 - (0.9 if (y - T) % 5 == 4 else 0)
           + (0.4 if (y - T) % 5 == 0 else 0) + (hr(x // 3, y // 2, 4) - 0.5) * 0.3, rim=(0.9, -1.1))
    # cantoneres de ferro
    for cx in (X0, X1 - 3):
        for cy in (T, B - 3):
            f.rect(cx, cy, cx + 3, cy + 3, IRON, lambda x, y: 4.0 - (y - cy) * 0.3 - (x - cx) * 0.2)
            f.px(cx + 1, cy + 1, IRON, 6.0)
    # placa de llautó
    f.rect(19, 15, 29, 19, BRASS, lambda x, y: 4.6 - (x - 19) * 0.12, rim=(0.6, -1.4))
    for x in range(21, 28, 2):
        f.px(x, 17, BRASS, 1.8)


def imant_ferro9(f):
    """Imant de ferradura vermell amb els pols de ferro-9, i el camp que espurneja."""
    cx, cy = 24, 12
    S = {}
    for y in range(2, 24):
        for x in range(10, 39):
            dx, dy = (x - cx), (y - cy)
            if dy <= 0:
                r = math.hypot(dx / 11.5, dy / 9.6)
                if 0.48 <= r <= 1:
                    S[(x, y)] = r
            elif 5.6 <= abs(dx) <= 11.5 and y <= 23:
                S[(x, y)] = abs(dx) / 11.5
    for (x, y), r in S.items():
        dx = x - cx
        if y <= cy:
            ang = math.atan2(y - cy, dx)
            nx, ny = math.cos(ang), math.sin(ang)
            t = (r - 0.48) / 0.52 * 2 - 1           # -1 dins, 1 fora
            l = 3.0 + 1.6 * (nx * LX * t + ny * LY * t) + (1 - t * t) * 0.8
        else:
            side = 1 if dx > 0 else -1
            t = (abs(dx) - 5.6) / 5.9 * 2 - 1
            l = 3.0 - 1.4 * t * side * (-LX) * side - (0.8 if dx > 0 else 0) + (1 - t * t) * 0.8
        mat = F9 if y >= 19 else RED
        if mat is F9:
            l += 1.8
        f.px(x, y, mat, l)
    # ratlla de separació entre el vermell i el ferro-9
    for x in range(10, 39):
        f.shade(x, 19, -1.2)
    # reflex
    for x, y in ((15, 6), (16, 5), (17, 4), (14, 7), (14, 9)):
        f.shade(x, y, 1.6)
    # espurnes del camp magnètic entre els pols
    for x, y in ((21, 23), (24, 24), (27, 23), (6, 22), (42, 22), (7, 19), (41, 19)):
        f.px(x, y, CYAN, 3.4)
    f.px(24, 22, CYAN, 4.4)


def nota_iri(f):
    """Full arrencat de la llibreta de l'Iri: crema, ratllat de blau, vora esquinçada i lletra de llapis."""
    S = torn(f.R(15, 2, 34, 24), 'l', seed=11, depth=1)
    paper(f, S, PAP_C, 4.0)
    for y in range(5, 24, 3):
        for x in range(17, 34):
            if (x, y) in S:
                f.px(x, y, RULE, 1.4)
    for y in range(3, 24):
        f.px(18, y, PINK, 2.6)                          # marge
    for i, y in enumerate(range(4, 19, 3)):
        f.scrib(20, 32 - (5 if i == 4 else 0), y, GRAPH, 1.0, seed=i + 20)
    f.text(27, 19, 'I.', GRAPH, 0.6, sp=0)
    f.rect(23, 21, 26, 21, GRAPH, 1.0)


def avis_reciclatge(f):
    """Avís oficial de la MARE: full blanc amb capçalera rosa i el cor, text imprès, un somriure i el «3»."""
    S = f.R(14, 2, 34, 24)
    paper(f, S, PAP_W, 4.2)
    f.rect(15, 3, 33, 7, PINK, lambda x, y: 3.2 + (0.8 if y == 3 else 0))
    for x, y in ((17, 4), (19, 4), (16, 5), (17, 5), (18, 5), (19, 5), (20, 5), (17, 6), (18, 6), (19, 6)):
        f.px(x, y, PAP_W, 6.0)
    f.rect(22, 5, 31, 5, PAP_W, 5.4)
    for y in (9, 11, 13):
        f.scrib(16, 32, y, INKG, 1.6, seed=y, dens=0.9, tall=0)
    # el «3» en rosa, gros, dins una caixa
    f.rect(16, 15, 23, 22, PINK, 1.6)
    f.rect(17, 16, 22, 21, PAP_W, 5.0)
    f.text(18, 16, '3', PINK, 1.4)
    f.px(21, 20, PINK, 1.4)
    # somriure imprès
    f.ell(28.5, 18.5, 3.8, 3.8, SUNY, 3.4, amp=1.4)
    f.dots(((27, 17), (30, 17), (26, 19), (27, 20), (28, 21), (29, 21), (30, 20), (31, 19)), SUNY, 0.6)


def llapis_ulls(f):
    """Llapis d'ulls d'en Mos: negre lluent, lletres platejades i caputxó rosa."""
    a, b = (5, 21), (29, 9)
    pix = f.limb(a, b, 1.7, 1.7, KOHL, 1.6, amp=1.8)
    f.shine(pix, 0.8, 1.6)
    for t in (0.35, 0.42, 0.49, 0.56):
        x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        f.px(round(x), round(y), STEEL, 6.0)
    f.limb((4, 21.5), (6, 20.5), 1.6, 1.6, STEEL, 4.0, amp=2.0)       # tap del cul
    # virolla i caputxó rosa
    f.limb((28.5, 9.2), (30.5, 8.2), 1.9, 1.9, STEEL, 4.4, amp=2.0)
    pix = f.limb((31.5, 7.7), (40, 3.6), 2.1, 2.1, PINK, 3.0, amp=2.0)
    f.shine(pix, 0.82, 1.4)
    f.px(35, 5, PINK, 5.4)
    # una ratlla de traç negre, de prova, a sota
    for x in range(14, 26):
        y = 23 + round(math.sin(x / 2.0) * 0.6)
        f.px(x, y, KOHL, 1.0 if hr(x, 4) > 0.2 else 2.0)


def nota_vet(f):
    """L'avís de reciclatge pel darrere: lletra grossa de llapis d'ulls, el cantó rosa girat i un «9»."""
    S = f.R(13, 2, 34, 24)
    S -= {(x, y) for (x, y) in S if (x - 28) + (y - 18) > 6 + 0}
    paper(f, S, PAP_W, 4.2)
    # cantó doblegat: es veu el rosa del davant
    F = {(x, y) for (x, y) in f.P([(28, 18), (35, 18), (28, 25)])}
    f.drop(F, -1.4, -1, -1)
    f.fill(F, PINK, lambda x, y: 3.0 - (y - 18) * 0.15, rim=(0.6, -0.8))
    # lletra de llapis d'ulls: traços gruixuts
    for i, y in enumerate((5, 9, 13)):
        f.scrib(15, 32 - i * 3, y, KOHL, 1.0, seed=40 + i, dens=0.95, tall=0.35)
        f.scrib(15, 31 - i * 3, y + 1, KOHL, 1.6, seed=50 + i, dens=0.5, tall=0)
    # el «9» de la signatura
    f.text(16, 17, '9', KOHL, 0.8)
    f.text(17, 17, '9', KOHL, 0.8)
    f.rect(21, 22, 25, 22, KOHL, 1.2)


def _aldaia_face(f, x, y):
    """Retrat petit del Director Aldaia (cabells grisos, vestit fosc, somriure)."""
    f.rect(x, y + 6, x + 7, y + 8, SUIT, lambda xx, yy: 2.8 - (xx - x) * 0.2)
    f.px(x + 3, y + 6, PAP_W, 5.0); f.px(x + 4, y + 6, RED, 3.0); f.px(x + 4, y + 7, RED, 2.4)
    f.ell(x + 3.5, y + 3, 2.6, 2.8, SKIN, 3.4, amp=1.6)
    f.rect(x + 1, y, x + 6, y + 1, HAIRG, lambda xx, yy: 3.6 - (xx - x) * 0.3)
    f.px(x + 1, y + 2, HAIRG, 2.6); f.px(x + 6, y + 2, HAIRG, 2.0)
    f.px(x + 2, y + 3, DARK, 1.0); f.px(x + 5, y + 3, DARK, 1.0)
    f.px(x + 3, y + 5, RED, 1.6); f.px(x + 4, y + 5, RED, 1.6)


def fullet_reeducacio(f):
    """Fullet tríptic lluent, mig obert en ziga-zaga: portada amb el Director, el cor de la MARE i franges de colors."""
    # tres panells en ziga-zaga (perspectiva: les arestes pugen i baixen)
    panels = [((5, 5), (17, 3), (17, 23), (5, 21), TEAL, 3.0),
              ((17, 3), (30, 6), (30, 24), (17, 23), PAP_W, 3.4),
              ((30, 6), (43, 3), (43, 23), (30, 24), PAP_W, 4.4)]
    for (a, b, c, d, mat, base) in panels:
        S = f.P([a, (b[0] + 1, b[1]), (c[0] + 1, c[1] + 1), (d[0], d[1] + 1)])
        f.fill(S, mat, base, rim=(0.6, -1.0))
    # panell esquerre (interior turquesa): text blanc i un cor
    for y in (9, 12, 15):
        f.scrib(7, 15, y + (17 - 7) * 0, PAP_W, 4.4, seed=y, dens=0.9, tall=0)
    # panell del mig (a l'ombra): franja rosa i ratlles
    f.fill(f.P([(18, 4), (31, 7), (31, 10), (18, 7)]), PINK, 2.6, rim=None)
    for k, y in enumerate((12, 15, 18)):
        for x in range(19, 29):
            f.px(x, y + round((x - 17) * 3 / 13), INKG, 2.0 if hr(x, y) > 0.2 else 3.0)
    # portada: el Director somrient, títol i el cor
    f.fill(f.P([(31, 7), (44, 4), (44, 8), (31, 11)]), TEAL, 2.8, rim=None)
    for x in range(33, 42):
        f.px(x, 8 - (x - 31) * 3 // 13 + 0, PAP_W, 5.0 if x % 3 else 3.6)
    _aldaia_face(f, 33, 11)
    for x, y in ((38 + 3, 17), (40 + 3, 17), (37 + 3, 18), (38 + 3, 18), (39 + 3, 18), (40 + 3, 18), (39 + 3, 19)):
        f.px(x, y, PINK, 3.6)
    f.px(41, 17, PINK, 5.0)
    # lluentor: una diagonal clara a la portada
    for i in range(6):
        f.shade(36 + i, 22 - i * 3, 0.8)


def nota_pany(f):
    """El fullet desplegat pel darrere: blanc, amb els plecs, i el pany M-3 dibuixat amb llapis d'ulls."""
    S = f.R(4, 3, 44, 23)
    paper(f, S, PAP_W, 4.0, w=40, h=20)
    # vores de colors del davant que es veuen al cantell
    f.rect(4, 3, 44, 3, TEAL, 3.4)
    f.rect(4, 23, 44, 23, PINK, 2.6)
    for x in (17, 31):                                              # plecs
        f.rect(x, 4, x, 22, PAP_W, 2.6)
        f.rect(x + 1, 4, x + 1, 22, PAP_W, 5.0)
    # el pany: arc, cos i forat
    K, L = KOHL, 1.0
    for x, y in ((19, 9), (19, 8), (20, 7), (21, 6), (22, 6), (23, 6), (24, 6), (25, 7), (26, 8), (26, 9)):
        f.px(x, y, K, L)
        f.px(x + (1 if x < 22 else -1 if x > 23 else 0), y + 1, K, L + 0.8)
    f.rect(16, 10, 29, 20, K, L)
    f.rect(17, 11, 28, 19, PAP_W, 4.4)
    f.text(18, 12, 'M-3', K, 1.2, sp=1)
    f.dots(((22, 17), (23, 17), (22, 18), (23, 18), (22, 19)), K, 1.2)
    # fletxa i interrogant
    f.scrib(6, 13, 8, K, 1.4, seed=2, dens=0.9, tall=0)
    f.scrib(6, 12, 11, K, 1.4, seed=3, dens=0.9, tall=0)
    f.scrib(6, 14, 14, K, 1.4, seed=4, dens=0.9, tall=0)
    f.scrib(33, 42, 8, K, 1.4, seed=5, dens=0.9, tall=0)
    f.scrib(33, 41, 11, K, 1.4, seed=6, dens=0.9, tall=0)
    f.dots(((36, 15), (37, 14), (38, 14), (39, 15), (39, 16), (38, 17), (38, 18), (38, 20)), K, 1.0)
    f.text(10, 18, 'V.', K, 1.0, sp=0)


def escarabat(f):
    """El Senyor Bigotis: escarabat marró lluent amb les antenes arrissades com un bigoti."""
    cx, cy = 29, 14
    # potes
    for k in (-6, 0, 6):
        f.line(cx + k, cy + 5, cx + k - 2, cy + 10, BEET, 1.4)
        f.line(cx + k, cy - 5, cx + k - 2, cy - 10, BEET, 1.8)
    pix = f.ell(cx, cy, 13, 8, BEET, 3.4, amp=2.6)
    f.shine(pix, 0.75, 1.8)
    for x in range(cx - 6, cx + 13):
        f.shade(x, cy, -1.4)                                     # separació dels èlitres
    f.shade(cx + 2, cy - 4, 1.0); f.shade(cx + 3, cy - 4, 1.0); f.shade(cx + 4, cy - 5, 0.8)
    # pronot i cap
    pix = f.ell(cx - 10, cy, 4.2, 5.4, BEET, 2.6, amp=2.2)
    f.shine(pix, 0.82, 1.4)
    pix = f.ell(cx - 15, cy, 2.8, 3.0, BEET, 2.2, amp=1.8)
    f.px(cx - 16, cy - 1, PAP_W, 6.0)
    # bigoti: dues antenes llargues i arrissades
    for sgn in (-1, 1):
        pts = [(cx - 17, cy + sgn * 2), (cx - 19, cy + sgn * 4), (cx - 21, cy + sgn * 6), (cx - 23, cy + sgn * 7),
               (cx - 25, cy + sgn * 7), (cx - 26, cy + sgn * 6), (cx - 26, cy + sgn * 5), (cx - 25, cy + sgn * 4)]
        for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
            f.line(xa, ya, xb, yb, BEET, 2.0)


def sopa(f):
    """Bol de plàstic de presó amb sopa de reinserció verda que fa bombolles soles, i la cullera."""
    cx = 22
    # cullera (darrere)
    f.limb((31, 12), (43, 4), 1.0, 1.2, PLAST, 4.2, amp=1.6)
    # cos del bol
    body = {}
    for y in range(11, 24):
        t = (y - 11) / 12
        half = 15.5 - t ** 1.6 * 8
        for x in range(round(cx - half), round(cx + half) + 1):
            u = (x - cx) / half
            body[(x, y)] = (u, 0.3, math.sqrt(max(0, 1 - u * u)))
    for (x, y), (nx, ny, nz) in body.items():
        f.px(x, y, PLAST, 3.6 + 2.0 * (nx * LX + ny * LY + nz * LZ - 0.35) - (y - 11) * 0.06)
    f.shine(body, 0.6, 0.9)
    f.rect(cx - 6, 24, cx + 6, 24, PLAST, 1.6)
    # vora i sopa
    f.ell(cx, 11, 15.5, 3.6, PLAST, 5.0, amp=0.8)
    f.ell(cx, 11.2, 13.6, 2.6, LIME, 3.0, amp=0.0, lvlfn=lambda x, y: (x - cx) * -0.04 + (y - 11) * 0.3)
    for x, y, r in ((cx - 6, 11, 1.4), (cx + 2, 10, 1.8), (cx + 7, 12, 1.0), (cx - 1, 12, 1.0)):
        f.ell(x, y, r, r * 0.8, LIME, 4.4, amp=1.0)
    # bombolles que pugen
    for x, y in ((cx - 3, 6), (cx + 4, 4)):
        f.ell(x, y, 1.6, 1.6, LIME, 3.6, amp=1.6)
        f.erase(x, y)
        f.px(x - 1, y - 1, LIME, 5.4)


def tros_cartell(f):
    """Tros arrencat del cartell del reciclatge: capçalera verda amb lletres, i mig somriure groc."""
    S = torn(f.P([(6, 3), (40, 2), (43, 22), (8, 24)]), 'lrtb', seed=3, depth=1)
    paper(f, S, SIGN, 4.0)
    head = {(x, y) for (x, y) in S if y <= 9 - (x - 6) * 0.03}
    f.fill(head, CORPG, 2.6, rim=(0.6, 0))
    f.text(9, 4, 'CICLA', SIGN, 5.0)
    # mig somriure groc, tallat per l'esquinçada de la dreta
    pix = {p: 0 for p in f.E(37, 17, 7, 7) if p in S}
    for (x, y) in pix:
        f.px(x, y, SUNY, 3.6 - (x - 37) * 0.1 - (y - 17) * 0.12)
    f.dots(((34, 14), (34, 15), (39, 14), (39, 15)), KOHL, 1.0)
    f.dots(((32, 18), (33, 19), (34, 20), (35, 21), (36, 21), (37, 21), (38, 21), (39, 20), (40, 19)), KOHL, 1.0)
    # vora verda de baix i un tros de cinta adhesiva
    f.rect(9, 12, 22, 13, SIGN, 2.6)
    f.rect(9, 16, 18, 16, SIGN, 2.6)


def nota_mida(f):
    """El tros de cartell pel darrere, amb la mida en gros: «6½» claus angleses, i una clau dibuixada."""
    S = torn(f.P([(6, 3), (40, 2), (43, 22), (8, 24)]), 'lrtb', seed=3, depth=1)
    scrap_cartell(f, S, 3)
    f.text(10, 6, '6', KOHL, 0.8, font=BIG)
    f.text(16, 6, '½', KOHL, 0.8, font=BIG)
    # x clau anglesa
    f.dots(((25, 10), (26, 10)), KOHL, 1.2)
    f.dots(((24, 9), (25, 11)), KOHL, 1.2)
    # clau anglesa dibuixada
    for x in range(28, 40):
        f.px(x, 16 - (x - 28) // 3, KOHL, 1.0)
    f.dots(((27, 16), (26, 15), (26, 17), (27, 18), (40, 12), (41, 11), (41, 13), (42, 12)), KOHL, 1.2)
    # fletxa de mida a sota
    for x in range(11, 40):
        f.px(x, 20, KOHL, 1.6)
    f.dots(((11, 19), (11, 21), (39, 19), (39, 21)), KOHL, 1.4)


# ─── Acte 2: bigues ─────────────────────────────────────────────────────────

def biga_acer(f):
    """Biga d'acer gris de dos metres, en I, amb marques de guix."""
    beam(f, 8, 46, 8, ACER, 3.7)
    for x in range(14, 46, 8):
        f.rect(x, 13, x, 15, PAP_F, 4.0)


def biga_ferro9(f):
    """Biga de ferro-9: el mateix perfil, d'acer blavós lluent, amb reflexos i l'etiqueta de la caldera."""
    beam(f, 8, 46, 6, F9, 4.0, sheen=0.35)
    for i in range(4):
        f.rect(12 + i * 9, 7, 16 + i * 9, 7, F9, 8.0)
        f.rect(13 + i * 9, 14, 15 + i * 9, 14, F9, 5.0)
    # etiqueta de cartró penjada amb un cordill
    f.line(26, 17, 27, 19, CLOTH, 3.0)
    T = f.R(22, 19, 34, 24)
    paper(f, T, MANI, 4.0)
    f.rect(24, 21, 32, 21, RED, 2.6)
    f.px(23, 20, IRON, 1.0)


def serra(f):
    """Serra de metall: arc de ferro, fulla dentada lluent i mànec de fusta."""
    # arc
    f.rect(4, 4, 36, 5, IRON, lambda x, y: 4.4 if y == 4 else 2.6)
    f.rect(4, 4, 6, 17, IRON, lambda x, y: 4.0 - (x - 4) * 0.8)
    f.rect(34, 4, 36, 15, IRON, lambda x, y: 3.6 - (x - 34) * 0.8)
    f.px(5, 17, IRON, 5.0)
    f.px(15, 3, IRON, 3.6); f.px(15, 2, IRON, 3.0)                    # tensor
    # fulla
    for x in range(6, 36):
        f.px(x, 14, ACER, 6.4)
        f.px(x, 15, ACER, 4.6)
        f.px(x, 16, ACER, 3.4 if x % 2 else 1.6)
        if x % 2 == 0:
            f.px(x, 17, ACER, 2.2)
    # mànec de pistola
    S = f.P([(34, 10), (42, 10), (46, 22), (40, 23), (36, 16), (34, 16)])
    f.drop(S)
    f.fill(S, WOOD, lambda x, y: 4.4 - (x - 34) * 0.18 - (y - 10) * 0.05, rim=(0.8, -1.0))
    for (x, y) in f.P([(38, 13), (41, 13), (42, 17), (40, 17)]):
        f.erase(x, y)
    f.px(37, 12, BRASS, 4.6); f.px(42, 20, BRASS, 4.6)




def tram_biga(f, n):
    """Un terç de biga: biga curta tallada, forats per cargolar-la i el número pintat."""
    holes = {1: 'r', 2: 'lr', 3: 'l'}[n]
    beam(f, 14, 40, 7, ACER, 3.5)
    for side in holes:
        x = 16 if side == 'l' else 38
        for y in (12, 14):
            f.px(x, y, DARK, 0.2)
            f.px(x + 1, y + 1, ACER, 5.0)
    # el número, pintat de groc a l'ànima, i una etiqueta amb els trossos (■ □ □)
    f.rect(23, 11, 29, 15, SUNY, 2.8, rim=(0.6, -0.8))
    f.text(25, 11, str(n), KOHL, 1.0)
    for i in range(3):
        on = (i + 1) == n
        f.rect(16 + i * 6, 20, 19 + i * 6, 23, ACER if not on else SUNY, (3.6 if not on else 3.8), rim=(0.8, -0.8))
        if not on:
            f.rect(17 + i * 6, 21, 18 + i * 6, 22, DARK, 0.6)


def tram_biga_1(f):
    tram_biga(f, 1)


def tram_biga_2(f):
    tram_biga(f, 2)


def tram_biga_3(f):
    tram_biga(f, 3)


def biga_muntada(f):
    """Tres trams cargolats: biga llarga amb dues juntes, platines i femelles."""
    beam(f, 8, 46, 8, ACER, 3.5)
    for jx in (20, 33):
        f.rect(jx, 8, jx, 18, DARK, 0.8)                      # la junta
        f.rect(jx - 3, 9, jx + 3, 17, ACER, lambda x, y: 5.0 - (x - jx + 3) * 0.3 - (y - 9) * 0.12, rim=(0.8, -1.4))
        for bx in (jx - 2, jx + 2):
            for by in (11, 15):
                f.px(bx, by, IRON, 5.6)
                f.px(bx + 1, by, IRON, 2.0)
                f.px(bx, by + 1, IRON, 1.6)
    for i, x in enumerate((13, 26, 39)):
        f.text(x, 20, str(i + 1), SUNY, 4.0)


# ─── Acte 2: eines i peces ──────────────────────────────────────────────────

def nota_amagatall(f):
    """Full de la llibreta de l'Iri, plegat en apaisat: un croquis amb el pilar 7, la reixa i una creu."""
    S = torn(f.R(5, 4, 43, 23), 't', seed=5, depth=1)
    paper(f, S, PAP_C, 4.0, w=38, h=20)
    for y in range(7, 23, 3):
        for x in range(6, 43):
            if (x, y) in S:
                f.px(x, y, RULE, 1.4)
    for y in range(5, 23):
        f.px(24, y, PAP_C, 2.6)                                  # plec
        f.px(25, y, PAP_C, 5.0)
    # pilar amb el 7
    f.rect(9, 6, 14, 21, GRAPH, 1.2)
    f.rect(10, 7, 13, 20, PAP_C, 4.2)
    f.text(10, 10, '7', GRAPH, 0.6)
    f.rect(8, 21, 15, 21, GRAPH, 1.0)
    # reixa al costat, amb la creu
    for x in range(17, 23):
        for y in range(17, 22):
            if x in (17, 22) or y in (17, 21) or x % 2 == 0:
                f.px(x, y, GRAPH, 1.0)
    f.dots(((18, 13), (19, 14), (20, 15), (21, 14), (22, 13)), GRAPH, 1.4)
    # lletra
    for i, y in enumerate((7, 10, 13)):
        f.scrib(28, 41 - i * 2, y, GRAPH, 1.0, seed=60 + i)
    f.text(37, 17, 'I.', GRAPH, 0.6, sp=0)


def pols_rovell(f):
    """Un pilot de pols de rovell, amb escates i un tros de l'ala de la biga que s'esmicola."""
    for y in range(8, 25):
        for x in range(3, 46):
            dx = (x - 24) / 21
            top = 23 - 13 * max(0, 1 - dx * dx) ** 1.3
            if y < top + (hr(x, 2) - 0.5) * 1.6:
                continue
            l = 3.4 - (y - top) * 0.15 - dx * 0.8 + (hr(x, y, 1) - 0.5) * 1.6
            if y >= 24:
                l -= 1.2
            f.px(x, y, RUST, l)
    # escates i grans clars
    for i in range(18):
        x, y = 8 + int(hr(i, 3) * 32), 13 + int(hr(i, 4) * 10)
        if f.get(x, y):
            f.px(x, y, RUST, 5.4 if i % 3 else 1.0)
    # tros de biga rovellat que treu el cap
    S = f.P([(26, 6), (38, 9), (37, 12), (25, 10)])
    f.fill(torn(S, 'r', seed=2, depth=1), RUST, lambda x, y: 3.6 - (y - 6) * 0.25 + (hr(x, y, 3) - 0.5) * 1.2, rim=(0.8, -1.0))
    f.dots(((31, 8), (34, 9)), RUST, 1.0)


def molla(f):
    """Molla de llitera (espiral d'acer lluent) amb una tira de tela taronja lligada: el missatge per a la I."""
    cy, ry, x0, pitch, turns = 12, 7.2, 7, 5.4, 6.4
    n = 1200
    pts = []
    for i in range(n + 1):
        t = i / n * turns * 2 * math.pi
        pts.append((x0 + pitch * t / (2 * math.pi) + 2.2 * math.cos(t), cy + ry * math.sin(t), math.cos(t), math.sin(t)))
    for x, y, c, sn in pts:                                      # fil de darrere
        if c <= 0:
            f.px(round(x), round(y), STEEL, 2.6 - sn * 0.7)
    for x, y, c, sn in pts:                                      # fil de davant, gruixut i lluent
        if c > 0:
            l = 5.2 - sn * 1.5 + c * 0.6
            f.px(round(x), round(y), STEEL, l)
            f.px(round(x) + 1, round(y), STEEL, l - 1.6)
    # ganxos als caps
    f.line(2, 5, 6, 5, STEEL, 4.8)
    f.line(2, 5, 2, 8, STEEL, 3.6)
    f.line(43, 19, 46, 19, STEEL, 3.4)
    f.line(46, 19, 46, 16, STEEL, 2.8)
    # la tira de tela taronja, lligada amb un nus i dues cues curtes
    S = f.R(23, 3, 25, 21)
    f.drop(S)
    f.fill(S, ORNG, lambda x, y: 3.9 - (x - 23) * 0.5, rim=(0.6, -1.0))
    f.ell(24, 12, 2.4, 2.0, ORNG, 3.6, amp=2.0)
    tails = f.P([(23, 13), (25, 13), (20, 21), (18, 20)]) | f.P([(23, 13), (25, 13), (29, 20), (27, 21)])
    f.fill(tails, ORNG, 3.0, rim=(0.6, -1.0))
    f.dots(((24, 5), (24, 7), (23, 8), (24, 16), (24, 18)), KOHL, 2.0)          # lletres a la tela


def llima(f):
    """Llima fina: fulla d'acer picada, coll de llautó i mànec de fusta."""
    a, b = (3, 20), (31, 9)
    # fulla picada: ratlles diagonals alternes
    for i in range(29):
        t = i / 28
        x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        w = 1 if i < 4 else 2
        for j in range(-w, w + 1):
            xx, yy = round(x + j * 0.35), round(y + j)
            l = 4.6 - j * 1.0 - (0.9 if (i + j) % 2 else 0)
            f.px(xx, yy, ACER, l)
    # coll i mànec
    f.limb((31, 9), (34, 8), 1.0, 1.0, ACER, 3.0, amp=1.4)
    f.limb((34, 7.8), (35.5, 7.2), 2.3, 2.3, BRASS, 4.0, amp=2.2)
    pix = f.limb((36.5, 6.8), (45, 3.5), 2.4, 2.0, WOOD, 4.2, amp=2.4)
    f.shine(pix, 0.84, 1.0)


def _fork(f, short=0, broken=False):
    """Diapasó de ferro-9 de costat: dues branques de testa plana, la corba i el peu."""
    ys = (7, 15)
    for k, y in enumerate(ys):
        x0 = 8 + short + (4 if broken and k == 1 else 0)
        for x in range(x0, 31):
            for j, l in ((-1, 6.0), (0, 4.6), (1, 2.6)):
                ll = l + (0.6 if (x - x0) % 9 == 3 and j == -1 else 0)
                f.px(x, y + j, F9, ll)
        f.px(x0, y - 1, F9, 6.6)
        if broken:
            f.rect(x0, y - 1, x0 + 1, y + 1, F9, 8.0)               # metall viu, llimat de més
            f.dots(((x0 + 3, y), (x0 + 6, y - 1), (x0 + 5, y + 1)), F9, 2.0)   # ratllades
    # corba en U
    for i in range(41):
        t = i / 40 * math.pi
        x = 30 + math.sin(t) * 5.0
        y = 11 - math.cos(t) * 4.0
        for r in (-1, 0, 1):
            px, py = x + math.sin(t) * r * 0.95, y - math.cos(t) * r * 0.95
            l = 4.4 - r * 1.2 - math.sin(t - 0.6) * 0.8
            f.px(round(px), round(py), F9, l)
    # peu i bola
    for x in range(36, 44):
        f.px(x, 10, F9, 5.8)
        f.px(x, 11, F9, 4.2)
        f.px(x, 12, F9, 2.4)
    pix = f.ell(44, 11, 2.2, 2.2, F9, 4.4, amp=2.6)
    f.shine(pix, 0.75, 2.0)


def diapaso(f):
    """Diapasó de ferro-9 net i afinat: brilla, i les ones de so surten suaus, blaves."""
    _fork(f)
    for k, r in enumerate((2.2, 4.4)):
        for a in range(-60, 61, 6):
            ang = math.radians(180 + a)
            x, y = 6 + math.cos(ang) * r * 0.55, 11 + math.sin(ang) * r * 2.0
            f.px(round(x) - k, round(y), CYAN, 3.6 - k * 0.8)
    for x, y in ((16, 6), (25, 14)):
        f.px(x, y, F9, 8.0)


def diapaso_espatllat(f):
    """Diapasó llimat de més: branques escurçades i desiguals, llimadures i un xiulet de tetera."""
    _fork(f, short=5, broken=True)
    for i in range(11):
        f.px(12 + int(hr(i, 1) * 16), 21 + int(hr(i, 2) * 3), F9, 6.4 if i % 2 else 3.0)
    # bufades de vapor que surten de les puntes
    for (cx, cy, r) in ((10, 6.5, 2.3), (7, 3.8, 1.8), (5, 8.8, 1.4), (14, 17.5, 1.8), (11, 20, 1.4)):
        f.ell(cx, cy, r, r, STEAM, 2.6, amp=1.4)
    # xiulet: ratlles grogues en ziga-zaga
    f.dots(((3, 11), (4, 12), (3, 13), (4, 14)), SUNY, 4.6)


def nota_pressio(f):
    """Tros de cartell amb un conducte i un manòmetre dibuixats amb llapis d'ulls, i la fletxa de pressió."""
    S = torn(f.P([(5, 5), (41, 3), (44, 23), (7, 22)]), 'lrtb', seed=9, depth=1)
    scrap_cartell(f, S, 9)
    K = KOHL
    # conducte: dues ratlles amb un colze
    for x in range(8, 30):
        f.px(x, 13, K, 1.0)
        f.px(x, 17, K, 1.0)
    for y in range(6, 14):
        f.px(26, y, K, 1.0)
        f.px(30, y, K, 1.2)
    f.rect(30, 14, 30, 17, K, 1.0)
    # manòmetre
    f.ring(36, 16, 4.0, 4.0, K, 1.0)
    f.line(36, 16, 38, 13, K, 1.2)
    f.px(36, 16, K, 0.6)
    # fletxes de pressió dins el conducte
    for x0 in (10, 18):
        f.dots(((x0, 15), (x0 + 1, 15), (x0 + 2, 15), (x0 + 3, 15), (x0 + 2, 14), (x0 + 2, 16)), K, 1.6)
    f.text(9, 6, 'P', K, 1.0)
    f.text(13, 6, '?', K, 1.0)


def nota_massa(f):
    """«MASSA!!!» en lletres grosses de llapis d'ulls, i l'aigua que regalima (el nivell de sota és una piscina)."""
    S = torn(f.P([(4, 3), (44, 4), (42, 23), (6, 22)]), 'lrtb', seed=13, depth=1)
    scrap_cartell(f, S, 13, curl=False)
    # lletres de 4×7, gruixudes
    BIGM = {'M': ('#...#', '##.##', '#.#.#', '#.#.#', '#...#', '#...#', '#...#'),
            'A': ('.###.', '#...#', '#...#', '#####', '#...#', '#...#', '#...#'),
            'S': ('.####', '#....', '#....', '.###.', '....#', '....#', '####.'),
            '!': ('#', '#', '#', '#', '#', '.', '#')}
    x = f.text(7, 6, 'MASSA', KOHL, 0.8, font=BIGM, sp=1)
    for i in range(3):
        f.text(x + i * 2, 6 - i, '!', KOHL, 0.8, font=BIGM)
    # subratllat doble
    for x in range(8, 38):
        f.px(x, 15 + (x // 7) % 2 * 0, KOHL, 1.4 if hr(x, 1) > 0.2 else 2.4)
    # aigua: taca blava i gotes
    for (x, y) in S:
        if y >= 18 and hr(x // 2, 5) > 0.3:
            f.px(x, y, WATER, 2.6 + (hr(x, y) - 0.5) + (y - 18) * 0.1)
    for x, y in ((12, 24), (25, 24), (34, 24)):
        f.px(x, y, WATER, 3.0)


def fitxa_mira(f):
    """Fitxa de personal de mania, molla: capçalera, foto en sépia de la Mira, línies a màquina i taques d'aigua."""
    S = f.R(4, 4, 44, 23) - {(4, 4), (44, 4), (4, 23), (44, 23)}
    paper(f, S, MANI, 4.0, w=40, h=20)
    f.rect(5, 5, 43, 8, LEATH, lambda x, y: 3.0 + (0.6 if y == 5 else 0))
    for x in range(7, 30, 2):
        f.px(x, 6, MANI, 4.6 if hr(x, 3) > 0.3 else 3.0)
        f.px(x + (1 if hr(x, 4) > 0.5 else 0), 7, MANI, 4.0)
    # foto amb clip
    f.rect(7, 10, 16, 21, SEPIA, 2.0)
    f.rect(8, 11, 15, 20, SEPIA, 3.8)
    f.ell(11.5, 15, 2.4, 2.8, SEPIA, 4.4, amp=1.4)
    f.rect(9, 18, 14, 20, SEPIA, 1.8)
    f.rect(9, 12, 14, 13, SEPIA, 1.2)
    f.px(9, 14, SEPIA, 1.2); f.px(14, 14, SEPIA, 1.2)
    f.rect(10, 9, 10, 12, STEEL, 5.0); f.px(11, 9, STEEL, 3.0)
    # línies a màquina
    for i, y in enumerate((11, 14, 17, 20)):
        f.scrib(19, 41 - (i % 2) * 6, y, INKG, 1.0, seed=70 + i, dens=0.95, tall=0)
    # taques d'aigua (està molla): anells més foscos
    for (cx, cy, r) in ((33, 18, 5.5), (23, 9, 3.4)):
        for (x, y) in S:
            d = math.hypot(x - cx, (y - cy) * 1.2)
            if d < r:
                f.shade(x, y, -0.7 if r - d < 1.2 else -0.25)


def planols(f):
    """Plànols originals de la cambra: cianotípia mig desenrotllada, amb el dibuix de la cambra en blanc."""
    # full desplegat
    S = f.R(10, 4, 45, 22)
    paper(f, S, BLUEP, 3.4, w=36, h=18)
    f.rect(12, 6, 43, 20, BLUEP, 3.6, rim=None)
    for (x, y) in f.R(12, 6, 43, 20):
        if x in (12, 43) or y in (6, 20):
            f.px(x, y, BLUEP, 5.6)
    # la cambra: cercle amb la bobina i el pal central
    f.ring(23, 13, 5.2, 5.2, BLUEP, 6.0)
    f.ring(23, 13, 2.6, 2.6, BLUEP, 5.0)
    f.px(23, 13, BLUEP, 6.0)
    for x in range(14, 33):
        if x % 2:
            f.px(x, 13, BLUEP, 4.8)
    # caixetí i cotes
    f.rect(33, 15, 42, 19, BLUEP, 5.4, rim=None)
    f.rect(34, 16, 41, 18, BLUEP, 3.6, rim=None)
    f.rect(35, 17, 39, 17, BLUEP, 5.6)
    for y in (8, 10):
        f.rect(33, y, 41, y, BLUEP, 5.0)
    # rotlle a l'esquerra
    pix = {}
    for y in range(3, 24):
        for x in range(4, 13):
            u = (x - 8) / 4.6
            if abs(u) <= 1:
                pix[(x, y)] = (u, 0.0, math.sqrt(1 - u * u))
    for (x, y), (nx, ny, nz) in pix.items():
        f.px(x, y, BLUEP, 3.6 + 2.2 * (nx * LX + nz * LZ - 0.35))
    f.shine(pix, 0.8, 1.0)
    f.ell(8, 3.5, 4.4, 1.6, BLUEP, 5.6, amp=0.4)
    f.ring(8, 3.5, 2.2, 0.8, BLUEP, 2.2)
    f.px(8, 3, BLUEP, 1.0)
    f.rect(4, 12, 12, 13, RED, lambda x, y: 3.6 if y == 12 else 2.4)          # cinta vermella


def carta_mos(f):
    """Sobre envellit per a la Nura, pel darrere: la solapa en V tancada amb un cor vermell."""
    S = f.R(5, 5, 43, 22)
    paper(f, S, PAP_O, 3.8, w=38, h=18)
    # solapa
    for x in range(5, 44):
        d = abs(x - 24)
        yy = 5 + (19 - d) * 9 // 19
        for y in range(5, yy + 1):
            f.px(x, y, PAP_O, 4.4 - (y - 5) * 0.04 + (0.5 if y == 5 else 0))
        f.px(x, yy, PAP_O, 2.0)
        f.px(x, yy + 1, PAP_O, 2.8)
    # plecs laterals
    for i in range(9):
        f.px(6 + i, 21 - i, PAP_O, 2.8)
        f.px(42 - i, 21 - i, PAP_O, 2.8)
    # cor de lacre
    for x, y in ((22, 12), (23, 12), (25, 12), (26, 12), (21, 13), (22, 13), (23, 13), (24, 13), (25, 13), (26, 13), (27, 13),
                 (21, 14), (22, 14), (23, 14), (24, 14), (25, 14), (26, 14), (27, 14), (22, 15), (23, 15), (24, 15), (25, 15), (26, 15),
                 (23, 16), (24, 16), (25, 16), (24, 17)):
        f.px(x, y, RED, 3.2 - (y - 12) * 0.2 + (1.8 if (x, y) in ((22, 13), (23, 12)) else 0))
    # taques d'antic a les vores
    for (x, y) in S:
        if (x < 8 or y > 20) and hr(x, y, 4) > 0.7:
            f.shade(x, y, -0.6)


def nota_vet_nom(f):
    """Tros de cartell amb el nom en gros: «VET», amb llapis d'ulls."""
    S = torn(f.P([(7, 4), (42, 3), (41, 23), (5, 22)]), 'lrtb', seed=17, depth=1)
    scrap_cartell(f, S, 17)
    x = f.text(9, 8, 'V', KOHL, 0.8, font=BIG)
    x = f.text(x + 1, 9, 'E', KOHL, 0.8, font=BIG)
    f.text(x + 1, 9, 'T', KOHL, 0.8, font=BIG)
    for x in range(10, 32):
        f.px(x, 18, KOHL, 1.6 if hr(x, 2) > 0.25 else 2.6)


def nota_iri_nom(f):
    """Mig full de la llibreta de l'Iri, esquinçat de través, amb el nom en gros: «IRI», amb llapis."""
    S = torn(f.P([(9, 3), (39, 3), (39, 17), (9, 23)]), 'b', seed=19, depth=1)
    paper(f, S, PAP_C, 4.0, w=30, h=20)
    for y in range(5, 24, 3):
        for x in range(10, 39):
            if (x, y) in S:
                f.px(x, y, RULE, 1.4)
    for y in range(3, 24):
        if (12, y) in S:
            f.px(12, y, PINK, 2.6)
    x = f.text(16, 6, 'I', GRAPH, 0.4, font=BIG)
    x = f.text(x + 2, 6, 'R', GRAPH, 0.4, font=BIG)
    f.text(x + 2, 6, 'I', GRAPH, 0.4, font=BIG)
    f.text(33, 7, '.', GRAPH, 0.4)
    f.scrib(15, 30, 15, GRAPH, 1.2, seed=3)


def fullet_memoria(f):
    """Fullet de la Sala de la Memòria: díptic de vellut vermell, marc daurat i la fàbrica en sépia."""
    # pàgina del darrere, que s'obre una mica a l'esquerra
    B = f.P([(7, 6), (17, 2), (17, 24), (7, 22)])
    f.fill(B, VELV, lambda x, y: 2.0 + (x - 7) * 0.05, rim=(0.6, -0.8))
    for y in range(8, 20, 3):
        for x in range(9, 16):
            f.px(x, y + (17 - x) * 0 , BRASS, 2.4 if hr(x, y) > 0.3 else 1.4)
    # portada
    C = f.R(17, 2, 38, 24)
    f.drop(C)
    f.fill(C, VELV, lambda x, y: 3.4 - (x - 17) * 0.04 - (y - 2) * 0.03, rim=(0.8, -1.0))
    for (x, y) in f.R(19, 4, 36, 22):
        if x in (19, 36) or y in (4, 22):
            f.px(x, y, BRASS, 4.0 - (y - 4) * 0.06)
    # vinyeta en sépia: les xemeneies de la fàbrica
    f.rect(21, 6, 34, 15, SEPIA, lambda x, y: 4.6 - (y - 6) * 0.15)
    for (x0, y0, x1) in ((23, 8, 24), (27, 7, 28), (31, 9, 32)):
        f.rect(x0, y0, x1, 15, SEPIA, 1.4)
        f.px(x0 + 1, y0 - 1, SEPIA, 2.6)
    f.rect(21, 12, 34, 15, SEPIA, 1.8)
    f.px(25, 6, SEPIA, 3.0); f.px(29, 6, SEPIA, 3.2)
    # títol daurat
    f.rect(21, 17, 34, 17, BRASS, 5.0)
    f.scrib(22, 33, 20, BRASS, 3.4, seed=4, dens=0.9, tall=0)


def mapa_fuga(f):
    """El fullet de la Memòria pel darrere, obert: la ruta de fuga amb llapis d'ulls, de la reixa al moll."""
    S = f.R(4, 3, 44, 23)
    paper(f, S, PAP_W, 4.0, w=40, h=20)
    f.rect(4, 3, 44, 3, VELV, 3.4)
    f.rect(4, 23, 44, 23, VELV, 2.8)
    f.rect(24, 4, 24, 22, PAP_W, 2.6); f.rect(25, 4, 25, 22, PAP_W, 5.0)     # plec
    K = KOHL
    # la reixa (inici)
    f.rect(7, 6, 13, 11, K, 1.0)
    f.rect(8, 7, 12, 10, PAP_W, 4.4)
    for x in (9, 11):
        f.rect(x, 7, x, 10, K, 1.4)
    # ruta de punts que baixa en ziga-zaga
    path = [(13, 9), (20, 9), (20, 16), (31, 16), (31, 9), (38, 9), (38, 15)]
    for (xa, ya), (xb, yb) in zip(path, path[1:]):
        n = max(abs(xb - xa), abs(yb - ya))
        for i in range(n + 1):
            if i % 2 == 0:
                f.px(xa + (xb - xa) * i // n, ya + (yb - ya) * i // n, K, 1.0)
    # la creu del moll i fletxa
    f.dots(((36, 17), (37, 18), (38, 19), (39, 20), (40, 21), (40, 17), (39, 18), (37, 20), (36, 21)), STAMP, 2.6)
    f.text(6, 16, 'PD', K, 1.2)
    f.scrib(6, 16, 21, K, 1.6, seed=8, dens=0.9, tall=0)


def tub_ferro9(f, x0=9):
    """Tub de vàlvula de ferro-9: cilindre lluent amb rosca als caps, buit per dins (es veu el forat)."""
    f.hcyl(x0, 43, 13, 5.0, F9, 4.6, amp=2.8, spec=1.8)
    # anelles de rosca
    for xr in (x0 + 1, x0 + 3, 38, 40):
        for y in range(8, 19):
            f.shade(xr, y, -1.2)
    # testa de la dreta i la boca oberta de l'esquerra
    f.ell(43, 13, 2.2, 5.0, F9, 3.0, amp=1.6)
    f.ell(43.4, 13, 1.0, 3.2, F9, 1.0, amp=0.6)
    f.ell(x0 - 0.5, 13, 2.4, 5.6, F9, 5.4, amp=1.2)
    f.ell(x0 - 0.8, 13, 1.4, 3.6, DARK, 0.6, amp=0.0)


def tub_amb_llibreta(f):
    """El tub de ferro-9 amb la llibreta de torn de l'Iri enrotllada a dins, que en treu el cap."""
    tub_ferro9(f, x0=17)
    # rotlle de fulls: tapa de pell per fora, fulls crema i l'espiral a la punta
    f.hcyl(6, 16, 13, 3.4, LEATH, 3.8, amp=2.2, spec=0.6)
    for x in range(6, 17):
        f.px(x, 16, PAP_C, 3.0)                                    # cantell dels fulls que sobresurt
    f.ell(5.5, 13, 2.2, 3.6, PAP_C, 4.4, amp=1.4)
    f.dots(((5, 12), (6, 13), (5, 14), (4, 13)), PAP_C, 2.2)       # espiral del paper
    f.px(5, 13, LEATH, 2.0)
    f.rect(11, 9, 11, 17, RED, 3.4)                                # la goma
    # llavi de la boca del tub, per davant del rotlle
    for (x, y) in f.E(16.5, 13, 2.4, 5.6) - f.E(16.8, 13, 1.2, 3.8):
        if x <= 17:
            f.px(x, y, F9, 5.6 - (y - 13) * 0.25)


def clau_vitrina(f):
    """Clau petita i plana d'acer, amb un clauer i una etiqueta de vellut on posa «MUSEU»."""
    # clau
    pix = f.ell(8, 9, 4.4, 4.4, STEEL, 4.4, amp=2.4)
    f.shine(pix, 0.8, 1.4)
    for p in f.E(7, 9, 1.4, 1.4):
        f.erase(*p)
    f.rect(12, 8, 25, 10, STEEL, lambda x, y: 5.2 - (y - 8) * 1.4, rim=None)
    for x, d in ((17, 2), (19, 3), (21, 1), (23, 2)):
        f.rect(x, 11, x + 1, 10 + d, STEEL, lambda xx, yy: 3.4 - (xx - x) * 0.8)
    f.px(25, 9, STEEL, 3.0)
    # clauer
    f.ring(10, 15.5, 2.6, 2.6, STEEL, 5.0)
    # etiqueta
    T = f.R(13, 15, 46, 23) - {(13, 15), (46, 15), (13, 23), (46, 23)}
    f.drop(T)
    f.fill(T, VELV, lambda x, y: 3.6 - (x - 13) * 0.04, rim=(0.8, -1.0))
    f.ring(15.5, 19, 1.0, 1.0, BRASS, 4.4)
    f.text(19, 17, 'MUSEU', BRASS, 4.6, sp=1)


def placa_cargol(f):
    """Placa d'identificació del robot: metall gastat, cargols, «C-1» en relleu i «CARGOL» gravat a mà."""
    S = f.R(5, 3, 43, 23) - {(5, 3), (43, 3), (5, 23), (43, 23)}
    f.drop(S)
    f.fill(S, IRON, lambda x, y: 4.6 - (x - 5) * 0.03 - (y - 3) * 0.06 + (hr(x, y, 5) - 0.5) * 0.6, rim=(1.0, -1.6))
    for (x, y) in ((7, 5), (41, 5), (7, 21), (41, 21)):
        f.px(x, y, IRON, 6.6); f.px(x + 1, y + 1, IRON, 1.6); f.px(x + 1, y, IRON, 3.0); f.px(x, y + 1, IRON, 3.0)
    # «C-1» en relleu (clar a dalt-esquerra, ombra a baix-dreta)
    def emboss(x, y, s, big=False):
        for ch in s:
            g = FONT[ch]
            for j, row in enumerate(g):
                for i, c in enumerate(row):
                    if c == '#':
                        f.px(x + i + 1, y + j + 1, IRON, 1.6)
            for j, row in enumerate(g):
                for i, c in enumerate(row):
                    if c == '#':
                        f.px(x + i, y + j, IRON, 6.6)
            x += 4
    emboss(17, 6, 'C-1')
    f.rect(9, 13, 39, 13, IRON, 2.4)
    f.rect(9, 14, 39, 14, IRON, 5.4)
    # «CARGOL» rascat amb una llima: traços clars i prims
    x = 12
    for ch in 'CARGOL':
        g = FONT[ch]
        for j, row in enumerate(g):
            for i, c in enumerate(row):
                if c == '#':
                    f.px(x + i, 16 + j, STEEL, 7.0 if hr(x + i, j) > 0.25 else 5.4)
        x += 4


def formulari_27be(f):
    """Formulari 27-B/E (carnet d'usuària exemplar): capçalera daurada, estrella grossa i la ratlla de signar, amb la creu."""
    form(f, 15, 2, head=BRASS, code='27BE', sig=True)
    # estrella daurada, amb vora fosca
    star = ('...#...', '..###..', '#######', '.#####.', '..###..', '.##.##.', '##...##')
    for j, row in enumerate(star):
        for i, c in enumerate(row):
            if c == '#':
                f.px(26 + i, 9 + j, BRASS, 5.0 - j * 0.35 - (1.4 if (i == 0 or row[i - 1] == '.' or i == 6 or row[i + 1] == '.') and j > 1 else 0))
    # ratlla de la signatura amb la «X»
    f.rect(17, 22, 32, 22, INKG, 1.2)
    f.dots(((17, 18), (18, 19), (19, 20), (20, 21), (20, 18), (19, 19), (18, 20), (17, 21)), STAMP, 2.6)


def formulari_27be_signat(f):
    """El 27-B/E signat pel capatàs: un gargot gran de tinta blava que travessa la ratlla, i un borrall."""
    formulari_27be(f)
    pts = [(16, 22), (18, 16), (19, 21), (21, 16), (22, 21), (24, 18), (25, 21), (28, 19), (31, 20), (34, 17)]
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        f.line(xa, ya, xb, yb, INKB, 2.6)
        f.line(xa + 1, ya, xb + 1, yb, INKB, 1.6)
    f.dots(((33, 22), (34, 23)), INKB, 2.2)


def carnet_exemplar(f):
    """Carnet plastificat d'usuària exemplar: foto de l'Iri, estrella daurada i la lluentor del plàstic."""
    S = f.R(5, 4, 43, 23) - {(5, 4), (43, 4), (5, 23), (43, 23), (6, 4), (5, 5), (42, 4), (43, 5), (5, 22), (6, 23), (42, 23), (43, 22)}
    f.drop(S)
    f.fill(S, PAP_W, lambda x, y: 4.6 - (y - 4) * 0.03, rim=(0.6, -1.6))
    inner = f.R(7, 6, 41, 21)
    f.rect(7, 6, 41, 9, RED, lambda x, y: 3.0 + (0.6 if y == 6 else 0))
    f.rect(19, 7, 37, 7, PAP_W, 5.2)
    f.rect(19, 8, 30, 8, PAP_W, 3.8)
    # foto de l'Iri
    f.rect(8, 8, 17, 20, CYAN, 3.4)
    f.rect(9, 17, 16, 20, SHIRT, 2.2)
    f.ell(12.5, 13.5, 2.8, 3.2, SKIN, 3.4, amp=1.6)
    f.rect(10, 9, 15, 11, HAIR, 2.6)
    f.px(9, 12, HAIR, 2.0); f.px(16, 12, HAIR, 1.6); f.px(16, 13, HAIR, 1.6); f.px(16, 14, HAIR, 1.6)
    f.px(11, 13, DARK, 1.0); f.px(14, 13, DARK, 1.0)
    # línies i estrella
    for y in (12, 15):
        f.scrib(20, 34, y, INKG, 1.2, seed=y, dens=0.95, tall=0)
    for x, y in ((37, 14), (36, 15), (37, 15), (38, 15), (35, 16), (36, 16), (37, 16), (38, 16), (39, 16), (36, 17), (38, 17)):
        f.px(x, y, BRASS, 4.6 if x <= 37 else 3.6)
    f.rect(20, 19, 31, 19, INKB, 1.8)
    # lluentor del plastificat: dues diagonals clares
    for i in range(16):
        for k, off in ((0, 0), (1, 3)):
            x, y = 22 + i - off, 22 - i
            if (x, y) in S:
                f.shade(x, y, 1.0 if k == 0 else 0.6)
        x, y = 23 + i, 22 - i
        if (x, y) in S:
            f.shade(x, y, 1.0)


def notes_perdudes(f):
    """Un feix de notes de molts anys: papers de colors i mides diferents, subjectats amb una pinça."""
    # nota groguenca de darrere, girada
    A = f.P([(5, 8), (21, 4), (24, 19), (8, 23)])
    paper(f, A, PAP_O, 3.6)
    for k in range(3):
        f.line(8 + k, 11 + k * 3, 19 + k, 8 + k * 3, INKG, 1.4)
    # tira blava ratllada
    B = torn(f.R(15, 9, 40, 16), 'r', seed=4, depth=1)
    paper(f, B, PAP_W, 4.2)
    for y in (11, 13, 15):
        f.rect(16, y, 38, y, RULE, 1.0)
    f.scrib(17, 34, 12, INKB, 1.6, seed=1)
    # paperet rosa
    C = f.P([(28, 3), (42, 5), (40, 15), (27, 13)])
    paper(f, C, PINK, 3.8)
    f.scrib(30, 39, 8, KOHL, 1.6, seed=3, dens=0.9)
    f.scrib(30, 37, 11, KOHL, 1.6, seed=4, dens=0.9)
    # quartilla de llibreta de davant
    D = torn(f.R(19, 15, 35, 24), 'b', seed=2, depth=1)
    paper(f, D, PAP_C, 4.0)
    f.scrib(21, 33, 18, GRAPH, 1.0, seed=6)
    f.scrib(21, 30, 21, GRAPH, 1.0, seed=7)
    # pinça de ferro
    f.rect(24, 3, 30, 5, IRON, lambda x, y: 4.6 - (y - 3) * 0.8, rim=(0.6, -1.0))
    f.rect(25, 6, 29, 9, IRON, lambda x, y: 3.4 - (x - 25) * 0.3, rim=(0.6, -1.0))
    f.ring(27, 3, 2.0, 1.2, IRON, 5.0)


def nota_mos(f):
    """Nota vella, groguenca, plegada en quatre: «M.» i un 9 de llapis d'ulls, i un rodal de taca."""
    S = f.R(12, 3, 36, 24) - {(12, 3), (36, 24)}
    paper(f, S, PAP_O, 4.0, w=24, h=21)
    # plecs en creu
    for y in range(3, 25):
        f.px(24, y, PAP_O, 2.4)
        f.px(25, y, PAP_O, 4.8)
    for x in range(12, 37):
        f.px(x, 13, PAP_O, 2.4)
        f.px(x, 14, PAP_O, 4.8)
    # rodal de taca (una tassa) i vores enfosquides
    f.ring(31, 19, 4.0, 3.6, PAP_O, 1.8, th=1.2)
    for (x, y) in S:
        if x in (12, 36) or y in (3, 24):
            f.shade(x, y, -0.8)
    # escriptura
    for i, y in enumerate((6, 9)):
        f.scrib(14, 22, y, KOHL, 1.2, seed=80 + i, dens=0.9)
        f.scrib(27, 34, y, KOHL, 1.2, seed=90 + i, dens=0.9)
    f.text(14, 17, 'M.', KOHL, 1.0, sp=0)
    f.text(19, 17, '9', KOHL, 1.0)


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
    """Imatge RGBA de 49×27 de l'objecte, o None si no en té."""
    fn = ICONS.get(item_id)
    if fn is None:
        return None
    f = Ic()
    fn(f)
    return f.render()
