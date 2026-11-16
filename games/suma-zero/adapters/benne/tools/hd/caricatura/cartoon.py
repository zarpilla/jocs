"""
Pixel art caricaturesc de Suma Zero (personatges i icones), a l'estil dels LucasArts clàssics:
siluetes clares, **contorn fosc** del color de cada peça (no negre pur), i **dos o tres tons per
color** (ombra, base, llum), amb la llum que ve de dalt a l'esquerra. Sense degradats ni dithering:
això queda per als fons (hd/pix.py).

Una figura es fa amb peces (`Fig.ell`, `Fig.poly`, `Fig.rect`, `Fig.px`) que es pinten en ordre, cada
una amb un material (una rampa de `PAL`). En renderitzar:

  - cada peça s'ombreja sola: els píxels de la vora de baix a la dreta van a l'ombra, i els de la vora de
    dalt a l'esquerra, a la llum (si el material en té);
  - les peces amb `line=True` dibuixen el seu contorn per sobre de les que tapen (p. ex. el cabell sobre
    el front);
  - tota la silueta rep el contorn exterior, del to més fosc del material veí.

    f = Fig(48, 68)
    f.ell(24, 16, 11, 12, 'pell')
    f.poly([(15, 28), (33, 28), (35, 46), (13, 46)], 'iri_dessuadora')
    img = f.render()
"""
from PIL import Image
from pixels import nearest

# ─── Paleta ───────────────────────────────────────────────────────────────
# Cada material: [contorn, ombra, base, llum]. L'ombra tira cap al lila i la llum cap al groc, com al
# pixel art de cartró pintat dels LucasArts. Els fons (hd/pix.py) fan servir les mateixes famílies.
PAL = {
    # pells
    'pell': [(74, 34, 40), (186, 112, 92), (232, 158, 122), (250, 200, 160)],
    'pell_fosca': [(54, 26, 30), (122, 70, 56), (164, 104, 76), (198, 140, 102)],
    'pell_rosa': [(80, 36, 44), (200, 120, 110), (240, 170, 146), (252, 210, 186)],
    # cabells
    'cabell_negre': [(14, 10, 22), (30, 24, 44), (52, 42, 70), (84, 74, 108)],
    'cabell_castany': [(36, 18, 16), (84, 44, 30), (122, 70, 42), (164, 106, 64)],
    'cabell_pelroig': [(60, 18, 14), (150, 54, 30), (206, 94, 46), (240, 150, 84)],
    # roba de l'Iri: dessuadora verd petroli, texans, bambes
    'iri_dessuadora': [(16, 42, 46), (34, 92, 94), (52, 136, 128), (104, 186, 164)],
    'texans': [(18, 22, 46), (40, 52, 98), (60, 78, 138), (96, 118, 176)],
    'bamba': [(40, 36, 48), (180, 174, 176), (236, 232, 226), (255, 255, 250)],
    'bamba_sola': [(40, 36, 48), (120, 54, 60), (178, 74, 70), (220, 110, 96)],
    # auriculars: vermell
    'auricular': [(54, 12, 22), (150, 30, 40), (210, 56, 56), (246, 120, 100)],
    'negre_suau': [(10, 8, 16), (26, 22, 34), (44, 40, 54), (72, 68, 84)],
    # cara
    'blanc_ull': [(54, 50, 72), (200, 196, 210), (246, 244, 240), (255, 255, 255)],
    'pupil·la': [(10, 8, 16), (18, 14, 26), (24, 20, 34), (60, 56, 80)],
    'boca': [(60, 14, 24), (96, 24, 36), (140, 40, 50), (190, 80, 80)],
    'llengua': [(60, 14, 24), (170, 60, 70), (210, 90, 96), (236, 130, 130)],
    # gat
    'gat': [(30, 20, 26), (88, 72, 70), (134, 116, 104), (180, 162, 140)],
    'gat_clar': [(30, 20, 26), (196, 182, 160), (232, 222, 200), (252, 248, 236)],
    'gat_ull': [(20, 30, 10), (150, 180, 40), (206, 226, 70), (240, 250, 150)],
    'rosa_nas': [(80, 30, 40), (190, 100, 110), (230, 140, 150), (250, 190, 196)],
    # objectes
    'cartro': [(70, 40, 20), (156, 106, 56), (198, 146, 84), (232, 190, 124)],
    'cable_gris': [(20, 20, 28), (70, 72, 84), (118, 120, 132), (176, 178, 186)],
    'cable_blau': [(10, 24, 50), (30, 70, 140), (56, 116, 196), (120, 176, 240)],
    'cable_groc': [(60, 44, 6), (180, 140, 20), (232, 196, 50), (252, 236, 130)],
    'metall': [(30, 30, 40), (110, 114, 128), (164, 168, 180), (222, 226, 232)],
    'pizza_caixa': [(70, 44, 26), (176, 140, 92), (220, 190, 140), (246, 230, 190)],
    'pizza_massa': [(90, 46, 20), (190, 120, 50), (230, 170, 80), (250, 214, 130)],
    'tomaquet': [(80, 14, 14), (176, 40, 30), (220, 70, 46), (246, 120, 90)],
    'formatge': [(110, 70, 10), (230, 180, 60), (250, 220, 110), (255, 246, 190)],
    'verd_llum': [(10, 40, 20), (40, 160, 80), (90, 230, 120), (190, 255, 200)],
    'vermell_llum': [(50, 6, 10), (190, 30, 30), (250, 70, 60), (255, 170, 150)],
}

LIGHT_DIR = (-1, -1)   # la llum ve de dalt a l'esquerra
SHADE_DIR = (1, 1)


class Fig:
    """Figura de peces amb material. Coordenades enteres (píxels del fotograma)."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.mat = [[None] * w for _ in range(h)]    # material de cada píxel
        self.part = [[-1] * w for _ in range(h)]     # peça de cada píxel
        self.tone = [[None] * w for _ in range(h)]   # to forçat (0..3) o None
        self.parts = []                              # (píxels, material, opcions)
        self.dx = self.dy = 0                        # desplaçament (balanceig del cos)

    # ─── peces ───
    def _add(self, pix, mat, line=False, shade=True, light=True, tone=None, outline=True):
        pid = len(self.parts)
        pix = {(x + self.dx, y + self.dy) for x, y in pix}
        pix = {(x, y) for x, y in pix if 0 <= x < self.w and 0 <= y < self.h}
        self.parts.append((pix, mat, dict(line=line, shade=shade, light=light, tone=tone, outline=outline)))
        for x, y in pix:
            self.mat[y][x] = mat
            self.part[y][x] = pid
            self.tone[y][x] = tone
        return pix

    def ell(self, cx, cy, rx, ry, mat, **kw):
        """El·lipse plena (centre i radis poden ser mig píxel)."""
        pix = set()
        for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
            for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
                nx, ny = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
                if nx * nx + ny * ny <= 1.0:
                    pix.add((x, y))
        return self._add(pix, mat, **kw)

    def poly(self, pts, mat, **kw):
        """Polígon ple (regla parell-senar)."""
        pix = set()
        ys = [p[1] for p in pts]
        for y in range(int(min(ys)), int(max(ys)) + 1):
            xs = []
            for (xa, ya), (xb, yb) in zip(pts, pts[1:] + pts[:1]):
                if (ya <= y + 0.5 < yb) or (yb <= y + 0.5 < ya):
                    xs.append(xa + (y + 0.5 - ya) * (xb - xa) / (yb - ya))
            xs.sort()
            for a, b in zip(xs[::2], xs[1::2]):
                for x in range(round(a), round(b)):
                    pix.add((x, y))
        return self._add(pix, mat, **kw)

    def rect(self, x0, y0, x1, y1, mat, **kw):
        """Rectangle inclusiu."""
        return self._add({(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)}, mat, **kw)

    def px(self, pts, mat, tone=2, **kw):
        """Píxels solts amb un to fix (detalls: ulls, boca, costures)."""
        return self._add(set(pts), mat, shade=False, light=False, tone=tone, outline=False, **kw)

    def line(self, x0, y0, x1, y1, mat, tone=0, **kw):
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        pts = [(round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n)) for i in range(n + 1)]
        return self.px(pts, mat, tone=tone, **kw)

    # ─── render ───
    def render(self, outline=True):
        img = Image.new('RGBA', (self.w, self.h), (0, 0, 0, 0))
        P = img.load()
        for pid, (pix, mat, o) in enumerate(self.parts):
            ramp = PAL[mat]
            for x, y in pix:
                if self.part[y][x] != pid:
                    continue        # una peça posterior l'ha tapat
                t = self.tone[y][x]
                if t is None:
                    t = 2
                    if o['shade'] and (x + SHADE_DIR[0], y + SHADE_DIR[1]) not in pix:
                        t = 1
                    elif o['shade'] and (x + 2 * SHADE_DIR[0], y + 2 * SHADE_DIR[1]) not in pix and (x + y) % 2 == 0:
                        t = 1        # una mica de trama a la vora de l'ombra
                    elif o['light'] and (x + LIGHT_DIR[0], y + LIGHT_DIR[1]) not in pix and (x + LIGHT_DIR[0], y) not in pix:
                        t = 3
                    if o['line'] and any(
                        (x + ax, y + ay) not in pix and 0 <= x + ax < self.w and 0 <= y + ay < self.h
                        and self.part[y + ay][x + ax] not in (-1, pid) and self.part[y + ay][x + ax] < pid
                        for ax, ay in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                        t = 0        # contorn interior sobre la peça de sota
                P[x, y] = ramp[t] + (255,)
        if outline:
            out = []
            for y in range(self.h):
                for x in range(self.w):
                    if self.mat[y][x] is not None:
                        continue
                    best = None
                    for ax, ay in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        xx, yy = x + ax, y + ay
                        if 0 <= xx < self.w and 0 <= yy < self.h and self.mat[yy][xx] is not None:
                            pid = self.part[yy][xx]
                            if self.parts[pid][2]['outline']:
                                best = PAL[self.mat[yy][xx]][0]
                                break
                    if best:
                        out.append((x, y, best))
            for x, y, c in out:
                P[x, y] = c + (255,)
        return img


def flip(img):
    return img.transpose(Image.FLIP_LEFT_RIGHT)


def preview(frames, scale=4, cols=None, bg=(46, 40, 60)):
    """Full de prova ampliat (per mirar-lo, no per al joc)."""
    cols = cols or len(frames)
    w, h = frames[0].size
    rows = (len(frames) + cols - 1) // cols
    out = Image.new('RGBA', (cols * (w + 2) * scale, rows * (h + 2) * scale), bg + (255,))
    for i, f in enumerate(frames):
        out.alpha_composite(nearest(f, (w * scale, h * scale)),
                            ((i % cols) * (w + 2) * scale + scale, (i // cols) * (h + 2) * scale + scale))
    return out
