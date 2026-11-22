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


# ─── Icones de Ni un ou (el mateix dibuix de volum que els personatges) ────

BLK = M((6, 6, 8), (14, 14, 18), (24, 24, 30), (38, 38, 46), (56, 56, 66), (80, 80, 92), (110, 110, 122))   # plàstic negre
LCD = M((14, 30, 22), (34, 70, 48), (70, 130, 88), (130, 190, 140), (196, 236, 190))
LED = M((90, 30, 6), (180, 70, 12), (240, 130, 40), (255, 200, 120))
BLUEC = M((8, 16, 44), (16, 32, 84), (28, 54, 128), (44, 80, 166), (76, 116, 200), (130, 168, 230))      # tapes del quadern
LOGB = M((10, 8, 8), (22, 18, 18), (36, 30, 30), (54, 46, 44), (76, 66, 62))                              # tela negra de la llibreta
GRIP = M((34, 4, 8), (76, 10, 16), (126, 20, 24), (176, 36, 34), (216, 66, 54), (244, 116, 96))          # mànecs de goma vermella
WIRE = M((20, 20, 24), (40, 40, 46), (64, 64, 70), (94, 94, 98), (130, 128, 128), (172, 170, 166), (214, 212, 206))   # cable d'acer
CABLE = M((6, 8, 10), (14, 16, 20), (26, 28, 34), (42, 46, 52), (64, 68, 76))                             # cable apantallat
USBB = M((6, 22, 50), (12, 44, 96), (24, 76, 150), (46, 116, 200), (100, 166, 236), (180, 216, 252))
GOLDK = M((48, 30, 6), (100, 70, 16), (160, 120, 30), (214, 172, 60), (244, 214, 110), (255, 244, 190))   # llautó
REDP = M((36, 8, 10), (80, 16, 18), (130, 30, 28), (176, 52, 40), (212, 86, 62))                            # pintura vermella
BAG = M((70, 80, 92), (116, 128, 140), (158, 170, 180), (196, 206, 214), (226, 232, 238), (248, 250, 252))  # bossa de plàstic
MUD = M((30, 30, 30), (52, 52, 50), (78, 78, 74), (106, 106, 100), (136, 134, 126))                         # fang gris
JAR = M((60, 76, 84), (100, 120, 128), (146, 166, 172), (190, 206, 210), (230, 240, 242))                   # vidre
PAPV = M((40, 50, 66), (96, 108, 126), (150, 162, 176), (198, 206, 214), (230, 234, 236), (248, 250, 250))  # receptari de la Vet, blanc blavós
CROSS = M((70, 10, 16), (140, 24, 30), (200, 44, 44), (236, 90, 80))


def walkie(f):
    """El walkie: negre, dret, amb l'antena de goma, la pantalleta verda, el pilot taronja i la reixeta."""
    f.limb((20, 1), (20, 7), 1.2, 1.4, BLK, 3.0, amp=1.6)                  # l'antena
    f.limb((26, 3), (26, 6), 1.2, 1.2, BLK, 3.4, amp=1.6)                  # el selector de canal
    S = f.P([(17, 7), (31, 7), (31, 25), (17, 25)]) - {(17, 7), (31, 7), (17, 25), (31, 25)}
    f.drop(S)
    f.fill(S, BLK, lambda x, y: 3.4 - (x - 17) * 0.08 - (y - 7) * 0.04, rim=(0.8, -1.2))
    f.rect(16, 11, 16, 17, BLK, 2.0)                                       # el botó de parlar
    f.rect(19, 9, 29, 13, BLK, 1.0)
    f.rect(20, 10, 28, 12, LCD, lambda x, y: 2.6 - (y - 10) * 0.4)        # la pantalleta: canal 9
    f.text(25, 10, '9', LCD, 0.6, font={'9': ('##', '##', '.#')})
    f.px(29, 8, LED, 3.4)                                                  # el pilot
    for y in range(16, 24, 2):                                             # la reixeta de l'altaveu
        f.rect(20, y, 28, y, BLK, 1.0)
        f.rect(20, y + 1, 28, y + 1, BLK, 4.0)


def quadern(f):
    """El quadern on apunten el que saben: tapes blaves, una goma vermella i una etiqueta."""
    S = f.R(14, 3, 34, 24)
    f.drop(S, -1.6, 2, 1)
    f.fill(S, BLUEC, lambda x, y: 3.6 - (x - 14) * 0.04 - (y - 3) * 0.04, rim=(0.8, -1.4))
    f.rect(14, 3, 16, 24, BLUEC, 2.0)                                      # el llom
    f.rect(35, 4, 35, 24, PAP_C, 3.2)                                      # el gruix de les fulles
    f.rect(20, 7, 30, 11, PAP_C, 4.4, rim=(0.4, -1.0))                    # l'etiqueta
    f.scrib(21, 29, 9, GRAPH, 1.4, seed=4)
    f.rect(31, 2, 31, 25, GRIP, 3.4)                                       # la goma
    f.rect(32, 2, 32, 25, GRIP, 2.0)


def llibreta(f):
    """La llibreta de màquines, oberta: hores de motor i consums en columnes, i un llapis."""
    L = f.P([(4, 7), (24, 5), (24, 24), (5, 25)])
    R = f.P([(24, 5), (44, 7), (43, 25), (24, 24)])
    f.drop(L | R, -1.4, 1, 2)
    f.fill(f.P([(3, 8), (24, 6), (45, 8), (44, 26), (24, 25), (4, 26)]), LOGB, 2.4, rim=(0.6, -1.0))   # les tapes
    f.fill(L, PAP_C, lambda x, y: 4.0 - (x - 4) * 0.02, rim=None)
    f.fill(R, PAP_C, lambda x, y: 3.6 + (x - 24) * 0.02, rim=None)
    for x in range(22, 25):                                                # el plec del mig
        for y in range(5, 25):
            f.shade(x, y, -0.8 + (x - 22) * 0.2)
    for y in range(10, 24, 3):                                             # les columnes de xifres
        f.scrib(7, 12, y, INKB, 1.6, seed=y, dens=0.9, tall=0)
        f.scrib(15, 20, y, INKB, 1.6, seed=y + 9, dens=0.9, tall=0)
        f.rect(27, y, 41, y, RULE, 1.4)
    for x in (14, 34):
        f.rect(x, 9, x, 23, STAMP, 2.0)                                    # les ratlles de columna
    f.scrib(27, 38, 11, GRAPH, 1.0, seed=7)                                # el gat d'en Diu, mal dibuixat
    f.limb((28, 21), (44, 14), 0.9, 0.9, SUNY, 3.4, amp=1.4)              # el llapis
    f.px(28, 21, GRAPH, 1.0)


def cisalla(f):
    """La cisalla: braços d'acer, mànecs de goma vermella i el cap amb les fulles curtes."""
    for (a, b) in (((3, 19), (16, 13)), ((5, 25), (18, 19))):              # mànecs
        f.limb(a, b, 1.6, 1.6, GRIP, 3.0, amp=2.0)
    for (a, b) in (((16, 13), (31, 9)), ((18, 19), (31, 13))):              # braços
        f.limb(a, b, 1.2, 1.2, ACER, 4.4, amp=2.2)
    S = f.E(32, 11, 3.6, 3.4)                                              # el cap
    f.drop(S)
    f.fill(S, ACER, lambda x, y: 4.6 - (x - 28) * 0.2 - (y - 8) * 0.2, rim=(0.8, -1.4))
    f.px(31, 10, ACER, 1.6)
    f.px(33, 12, ACER, 1.6)
    f.fill(f.P([(34, 8), (45, 5), (45, 7), (35, 11)]), ACER, 6.0, rim=(0.6, -1.2))   # les fulles
    f.fill(f.P([(35, 12), (45, 8), (45, 9), (35, 14)]), ACER, 4.4, rim=(0.4, -1.2))


def travesser(f):
    """El travesser de la llitera: un tub d'acer amb els caps aixafats i foradats."""
    f.limb((7, 19), (41, 8), 2.4, 2.4, STEEL, 4.0, amp=2.6)
    for (cx, cy) in ((6, 20), (42, 7)):                                    # caps aixafats
        S = f.E(cx, cy, 3.4, 2.6)
        f.fill(S, STEEL, lambda x, y: 4.6 - (y - cy) * 0.4, rim=(0.8, -1.2))
        f.px(cx, cy, DARK, 0.6)
    for t in (0.3, 0.55, 0.8):                                             # ratlletes de desgast
        x, y = 7 + 34 * t, 19 - 11 * t
        f.shade(x, y - 1, 1.2)


def tram(f):
    """Un tram de cable de malla d'acer: trenat, amb dos talls nets i una osca al mig."""
    pts = [(5, 17), (14, 13), (24, 14), (34, 12), (43, 8)]
    for p0, p1 in zip(pts, pts[1:]):
        f.limb(p0, p1, 2.6, 2.6, WIRE, 3.6, amp=2.4)
    # el trenat: ratlles en diagonal
    for i in range(46):
        t = i / 45
        k = min(int(t * 4), 3)
        u = t * 4 - k
        (x0, y0), (x1, y1) = pts[k], pts[k + 1]
        x, y = x0 + (x1 - x0) * u, y0 + (y1 - y0) * u
        if i % 3 == 0:
            for d in (-2, -1, 0, 1, 2):
                f.shade(x + d * 0.6, y + d, -1.2)
    for (cx, cy) in pts[0], pts[-1]:                                       # els talls: les fibres
        f.fill(f.E(cx, cy, 1.8, 2.6), WIRE, 5.0, rim=None)
        for (dx, dy) in ((0, -1), (0, 1), (-1, 0)):
            f.px(cx + dx, cy + dy, WIRE, 2.6)
    f.erase(24, 11)                                                        # l'osca
    f.erase(25, 11)
    f.px(24, 12, WIRE, 1.2)
    f.px(25, 12, WIRE, 6.0)


def cable_nou(f):
    """Un rotllo de cable apantallat i un connector nou, rodó, d'acer amb la rosca de llautó."""
    for k, (cx, cy, rx, ry) in enumerate(((16, 13, 11, 8), (19, 14, 10, 7))):
        f.ring(cx, cy, rx, ry, CABLE, 3.4 - k * 0.4, th=1.8)
    for i in range(30):
        a = math.pi * (1.1 + 0.8 * i / 29)
        f.px(round(16 + 11 * math.cos(a)), round(13 + 8 * math.sin(a)), CABLE, 4.6)
    f.limb((27, 18), (34, 15), 1.1, 1.1, CABLE, 3.0, amp=1.6)
    f.hcyl(34, 38, 14, 3.2, GOLDK, 3.4)                                    # la rosca
    for x in range(34, 39, 2):
        for y in range(11, 18):
            f.shade(x, y, -0.8)
    f.hcyl(39, 45, 14, 3.8, ACER, 4.4)                                     # el cos del connector
    f.rect(45, 12, 45, 16, DARK, 1.0)


def usb(f):
    """L'USB amb les dades de la Juana: plàstic blau, el connector i una anella."""
    f.ring(10, 13, 3.4, 3.4, ACER, 4.6, th=1.2)                           # l'anella
    S = f.P([(13, 8), (33, 8), (35, 10), (35, 17), (33, 19), (13, 19), (12, 17), (12, 10)])
    f.drop(S)
    f.fill(S, USBB, lambda x, y: 3.8 - (y - 8) * 0.18, rim=(0.8, -1.2))
    f.fill(f.E(15, 13.5, 1.3, 1.3), DARK, 1.0, rim=None)                  # el forat de l'anella
    f.rect(19, 11, 30, 16, PAP_W, 4.2, rim=(0.4, -1.0))                   # l'etiqueta, escrita a mà
    f.scrib(20, 29, 13, INKB, 1.6, seed=21)
    S = f.R(36, 10, 44, 17)                                               # el connector
    f.drop(S)
    f.fill(S, ACER, lambda x, y: 5.6 - (y - 10) * 0.2, rim=(0.8, -1.4))
    f.rect(39, 12, 40, 13, DARK, 0.6)
    f.rect(39, 15, 40, 15, DARK, 0.6)


def _nota(f, mat, base, seed, head=None):
    """Un paper doblegat per la meitat i mig obert: la meitat de dalt de cara a la llum."""
    top = f.P([(12, 4), (36, 6), (37, 14), (11, 13)])
    bot = f.P([(11, 13), (37, 14), (35, 24), (13, 23)])
    f.drop(top | bot, -1.4, 1, 2)
    f.fill(bot, mat, lambda x, y: base - 0.6 - (y - 13) * 0.05, rim=(0.4, -1.0))
    f.fill(top, mat, lambda x, y: base + 0.4 - (x - 11) * 0.02, rim=(0.6, -1.0))
    for x in range(11, 38):                                                # el plec
        f.shade(x, 13 + (x - 11) / 26, -1.0)
    if head:
        head()
    for y, s in ((8, 0), (10, 1)):
        f.scrib(15, 33, y, GRAPH if mat is PAP_C else INKB, 1.4, seed=seed + s)
    for y in (17, 20):
        f.scrib(15, 31, y, GRAPH if mat is PAP_C else INKB, 1.6, seed=seed + y, dens=0.7)


def nota_iri(f):
    """El paper de l'Iri: un full de llibreta quadriculada, crema, escrit amb llapis."""
    def head():
        for x in range(14, 36, 3):
            for y in range(6, 23):
                if f.get(x, y) and f.get(x, y)[0] is PAP_C:
                    f.shade(x, y, -0.5)
    _nota(f, PAP_C, 4.2, 30, head)


def nota_vet(f):
    """El paper de la Vet: un full del receptari, blanc, amb la creu vermella i tinta blava."""
    def head():
        f.fill(f.R(14, 5, 16, 9) - {(14, 5), (16, 5), (14, 9), (16, 9)}, CROSS, 2.6, rim=None)
        f.rect(13, 7, 17, 7, CROSS, 2.6)
        f.rect(19, 6, 33, 6, INKG, 2.0)
    _nota(f, PAPV, 4.4, 50, head)


def clau_tomas(f):
    """La clau antiga d'en Tomàs: llautó, l'ull treballat, la tija llarga i una etiqueta esborrada."""
    S = f.P([(30, 3), (42, 2), (44, 11), (32, 12)])                       # l'etiqueta de cartró
    f.drop(S)
    f.fill(S, PAP_O, lambda x, y: 3.6 - (x - 30) * 0.03, rim=(0.6, -1.0))
    f.fill(f.E(32, 7, 1, 1), DARK, 1.0, rim=None)
    f.scrib(34, 41, 6, INKG, 3.4, seed=11, dens=0.5)                      # el que hi deia, esborrat
    f.line(31, 7, 22, 12, CLOTH, 3.2)                                     # el cordill
    f.ring(13, 15, 6.5, 6, GOLDK, 3.6, th=2.0)                            # l'ull
    f.fill(f.E(13, 15, 2.2, 2.0), GOLDK, 4.4, rim=(0.6, -1.0))           # el trèvol del mig
    for (x, y) in ((13, 10), (8, 15), (18, 15), (13, 20)):
        f.px(x, y, GOLDK, 5.0)
    f.hcyl(19, 42, 15, 1.6, GOLDK, 3.4)                                   # la tija
    f.rect(20, 13, 21, 17, GOLDK, 3.8, rim=(0.6, -1.0))
    S = f.R(36, 17, 43, 22)                                               # el paletó
    f.drop(S)
    f.fill(S, GOLDK, lambda x, y: 3.4 - (y - 17) * 0.1, rim=(0.6, -1.2))
    for (x, y) in ((38, 19), (38, 20), (41, 21), (41, 22)):
        f.px(x, y, DARK, 0.6)
    for (x, y) in ((25, 15), (31, 14), (11, 19)):                         # verdet
        f.px(x, y, CORPG, 2.0)


def clau_tubs(f):
    """La clau de tubs: mànec de ferro colat pintat de vermell, el cos, les dues mandíbules dentades i la femella."""
    f.limb((4, 20), (30, 17), 2.2, 2.8, REDP, 3.0, amp=2.2)               # el mànec
    f.px(12, 18, IRON, 3.0)                                                # pintura saltada
    f.px(21, 17, IRON, 3.4)
    f.px(22, 17, IRON, 2.6)
    f.fill(f.E(5, 20, 1.2, 1.0), DARK, 0.6, rim=None)                     # el forat per penjar-la
    S = f.P([(28, 12), (38, 11), (39, 22), (29, 23)])                      # el cos
    f.drop(S)
    f.fill(S, IRON, lambda x, y: 4.0 - (x - 28) * 0.06 - (y - 11) * 0.04, rim=(0.8, -1.4))
    S = f.P([(38, 15), (46, 15), (46, 19), (38, 20)])                      # la mandíbula de baix
    f.drop(S)
    f.fill(S, IRON, 4.2, rim=(0.8, -1.4))
    f.rect(33, 2, 35, 13, ACER, lambda x, y: 4.6 - (x - 33) * 0.8)       # la tija de la mandíbula de dalt
    for y in range(4, 13, 2):
        f.px(35, y, ACER, 2.0)
    S = f.P([(31, 2), (46, 3), (46, 8), (36, 8)])                          # la mandíbula de dalt
    f.drop(S)
    f.fill(S, ACER, lambda x, y: 5.2 - (y - 2) * 0.3, rim=(0.8, -1.4))
    for x in range(38, 47, 2):                                             # les dents
        f.px(x, 8, ACER, 1.6)
        f.px(x, 15, IRON, 1.6)
    S = f.E(34, 10.5, 3.4, 1.8)                                            # la femella moleteada
    f.fill(S, ACER, 4.0, rim=(0.6, -1.2))
    for x in (32, 34, 36):
        f.px(x, 10, ACER, 2.0)
        f.px(x, 11, ACER, 2.0)


def mostra7(f):
    """La Mostra 7: una bossa segellada i, a dins, un pot de fang gris amb l'etiqueta."""
    S = f.P([(9, 4), (39, 4), (40, 24), (8, 24)])
    f.drop(S)
    f.fill(S, BAG, lambda x, y: 3.0 + (1.6 if (x - y) % 13 == 0 else 0) - (y - 4) * 0.03, rim=(1.0, -1.0))
    f.rect(9, 5, 39, 6, STAMP, 3.0)                                        # el tancament de pressió
    f.rect(9, 7, 39, 7, BAG, 4.6)
    J = f.R(15, 10, 30, 22)                                                # el pot de vidre
    f.fill(J, JAR, lambda x, y: 3.0 - (x - 15) * 0.06, rim=(0.8, -1.2))
    f.rect(15, 9, 30, 10, BLK, 3.6, rim=(0.6, -1.0))                       # la tapa
    f.fill(f.R(16, 15, 29, 21), MUD, lambda x, y: 3.0 - (y - 15) * 0.18 + (hr(x, y, 5) - 0.5) * 0.8, rim=None)
    f.rect(16, 15, 29, 15, MUD, 4.0)                                       # la superfície del fang
    f.rect(17, 11, 18, 21, JAR, 4.6)                                       # el reflex del vidre
    S = f.R(32, 11, 38, 21)                                                # l'etiqueta: «7»
    f.fill(S, PAP_W, 4.4, rim=(0.4, -1.0))
    f.text(34, 13, '7', INKB, 1.0)
    f.rect(33, 19, 37, 19, INKG, 2.0)
    for (x, y) in ((11, 8), (12, 9), (36, 22), (13, 21)):                 # brillantor del plàstic
        f.px(x, y, BAG, 5.4)


def registre(f):
    """La pàgina impresa del registre de fundacions: capçalera, el nom de la fundació i una taula."""
    S = f.R(14, 2, 34, 25)
    S -= {(34, 2), (33, 2), (34, 3)}
    paper(f, S, PAP_W, 4.4, w=21, h=24)
    f.px(33, 3, PAP_W, 2.6)
    f.rect(16, 4, 19, 6, BLUEC, 3.0)                                       # l'escut del registre
    f.rect(21, 4, 31, 4, INKG, 1.2)
    f.rect(21, 6, 28, 6, INKG, 2.0)
    f.rect(16, 9, 32, 9, INKG, 0.6)                                        # el nom, en negreta
    f.rect(16, 10, 26, 10, INKG, 0.6)
    for y in range(13, 23, 2):                                             # la taula
        f.rect(16, y, 20, y, INKG, 2.2)
        f.rect(22, y, 32, y, INKG, 2.2 if y != 19 else 0.4)
    f.rect(21, 12, 21, 23, INKG, 3.0)
    f.rect(22, 19, 32, 19, SUNY, 3.4)                                      # «Patró únic: Skarn», subratllat
    f.rect(22, 20, 32, 20, SUNY, 2.6)


ICONS = {fn.__name__: fn for fn in (
    walkie, quadern, llibreta, cisalla, travesser, tram, cable_nou, usb, nota_iri, nota_vet,
    clau_tomas, clau_tubs, mostra7, registre,
)}


def render(item_id):
    """Imatge RGBA de 49×27 de l'objecte, o None si no en té."""
    fn = ICONS.get(item_id)
    if fn is None:
        return None
    f = Ic()
    fn(f)
    return f.render()
