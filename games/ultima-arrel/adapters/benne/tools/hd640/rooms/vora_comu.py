"""
L'Última Arrel — la vora del bosc, comuna a les sales que la mostren: `vora_bosc` (Escena 1, capvespre, amb la tanca),
`bosc_obert` (Escena 7, una setmana després, de dia, sense la tanca), `credits` (el bosc obert de nit, amb tot el
turquesa encès) i `portada` (el roure al capvespre, amb un tall del terra on es veuen els fils de la xarxa).

Ve de la mostra d'estil (guio/art/mostra/vora_bosc.py i bosc.py), que segueix la referència 1
(guio/art/referencia/irivet-vora-bosc.png): càmera arran de terra, una mica contrapicada; el roure gegant a
l'esquerra amb la porta d'un metre; a la dreta, el que és de NaturaPlus (fred i pla); primer pla de falgueres en
silueta.

**Coordenades.** Tot es dibuixa en les coordenades de la mostra («món»: 640 d'ample, l'horitzó a y = 168, els peus
de la Iri a prop de la porta a y ≈ 250). Un `Llenc` és un Canvas de 640×360 amb un desplaçament vertical `oy`
(píxel de pantalla = món + oy): a les sales de joc oy = −28 (el món 28..288 omple l'escena, 0..259; a sota hi ha
el HUD), i a les pantalles senceres (crèdits, portada) se'n tria un altre i el cel, la capçada i el tronc continuen
cap amunt. `sala(y)` passa una y del món a la de la sala.

**Modes** (`Mode`): 'capvespre' (la tanca, l'obra, la xarxa apagada, el llum vermell), 'dia' (sense tanca ni res de
l'obra: els forats dels pals, ja amb herba, la taula de la soca, el bassal, la xarxa encesa, la porta oberta amb llum
turquesa; el sol del matí, baix i daurat, entra per la dreta, per la clariana on hi havia l'obra; flors al prat i
una branca amb fulles en primer pla, a dalt a la dreta) i 'nit' (el de dia, enfosquit i blau, amb el turquesa a tota força). L'escena es fa per capes
(`escena()`): el fons, la taula (capa del davant amb la seva línia base) i el primer pla (capa del davant que tapa
sempre).
"""
import functools
import math
import random

import numpy as np
from PIL import Image

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from hd.pix import Canvas, Light, B4, mix

W = 640
HOR = 168                      # l'horitzó (la càmera és baixa)
DY = 28                        # a les sales de joc, el món comença a y = 28 (oy = −28)
SALA_H = 260                   # l'escena acaba aquí: a sota, el HUD


def sala(y):
    """Una y del món → la y de la sala de joc."""
    return y - DY


# ─── Rampes (fosc → clar) ───────────────────────────────────────────────────
# El bosc viu: càlid.
DUSK = [(30, 24, 56), (46, 34, 74), (68, 44, 90), (98, 56, 98), (134, 72, 96), (172, 92, 88), (206, 120, 86),
        (232, 156, 98), (246, 194, 130), (252, 226, 172)]
HAZE = [(40, 24, 30), (62, 36, 34), (88, 50, 38), (118, 66, 42), (152, 88, 48), (188, 116, 58), (218, 148, 74),
        (240, 186, 106), (252, 220, 150)]
LEAVES = [(18, 14, 12), (34, 24, 16), (56, 36, 20), (84, 52, 24), (116, 72, 28), (150, 96, 34), (186, 124, 44),
          (218, 158, 62), (240, 194, 96)]
BARK = [(14, 10, 10), (26, 18, 14), (42, 28, 20), (60, 40, 28), (82, 56, 36), (106, 74, 46), (132, 94, 58),
        (160, 118, 74), (188, 146, 96)]
MOSS = [(10, 18, 10), (20, 32, 16), (32, 48, 22), (48, 68, 30), (68, 90, 38), (92, 114, 50), (122, 142, 66),
        (156, 170, 88)]
EARTH = [(16, 12, 10), (30, 22, 16), (48, 34, 24), (68, 48, 32), (90, 64, 40), (114, 82, 50), (140, 102, 62),
         (166, 124, 78), (192, 150, 98)]
LEAF = [(70, 26, 12), (116, 44, 18), (164, 72, 24), (206, 108, 38), (236, 150, 62), (250, 194, 110)]
PLANK = [(22, 12, 8), (40, 24, 14), (62, 38, 20), (88, 56, 28), (116, 76, 38), (144, 98, 50), (172, 124, 66),
         (200, 152, 88)]
IRONK = [(8, 8, 10), (18, 18, 22), (32, 30, 34), (50, 48, 52), (74, 70, 72)]
STONE = [(22, 20, 22), (38, 36, 36), (58, 54, 52), (80, 76, 70), (104, 98, 90), (130, 124, 112), (158, 152, 138)]
FERN = [(4, 6, 4), (8, 12, 8), (14, 20, 12), (22, 30, 16), (34, 42, 22), (52, 58, 30), (80, 76, 40)]
CREAM = [(70, 58, 50), (120, 104, 86), (170, 154, 128), (210, 196, 166), (236, 226, 198), (250, 244, 224)]
NOTE = [(80, 70, 56), (150, 136, 110), (210, 196, 166), (240, 232, 210)]
BRASS = [(60, 40, 10), (130, 96, 30), (200, 160, 60), (240, 210, 120)]
CLAY = [(40, 16, 10), (80, 34, 20), (124, 58, 32), (166, 88, 48), (204, 122, 70), (232, 164, 110)]
JAM = [(40, 6, 14), (80, 12, 26), (130, 22, 40), (180, 40, 56), (220, 80, 90)]
WARM = [(60, 30, 10), (130, 70, 20), (210, 130, 40), (250, 190, 90), (255, 230, 160), (255, 248, 220)]
# De dia: el cel, la boira daurada i verda entre els troncs, el verd de l'herba nova.
SKYD = [(60, 92, 150), (78, 112, 170), (100, 134, 186), (124, 156, 198), (150, 178, 208), (178, 198, 214),
        (204, 214, 214), (226, 226, 206), (244, 238, 204)]
HAZED = [(34, 40, 26), (50, 60, 34), (70, 82, 44), (94, 106, 56), (122, 132, 70), (152, 158, 86), (184, 184, 106),
         (214, 208, 134), (238, 230, 170)]
TRUNKD = [(40, 42, 40), (56, 58, 54), (74, 76, 68), (94, 96, 84), (118, 120, 102), (144, 144, 122), (172, 170, 144),
          (200, 198, 170), (224, 222, 198)]
TRUNKM = [(44, 36, 30), (62, 50, 40), (82, 68, 52), (104, 88, 66), (128, 108, 80), (154, 130, 96), (182, 156, 114),
          (208, 184, 138), (230, 210, 168)]                                        # els troncs, amb la llum del matí
GRASS = [(14, 22, 10), (24, 38, 14), (38, 58, 20), (56, 82, 28), (80, 108, 36), (108, 136, 48), (140, 164, 66),
         (176, 192, 92)]
# La xarxa: blau i turquesa bioluminescent.
TURQ = [(4, 20, 26), (6, 40, 48), (10, 70, 78), (20, 108, 112), (40, 150, 150), (80, 200, 192), (150, 240, 226),
        (220, 255, 248)]
GLOW_T = (110, 236, 220)
# NaturaPlus: fred, pla, artificial.
PLASTIC = [(60, 66, 80), (96, 104, 118), (136, 142, 156), (176, 182, 192), (210, 214, 222), (234, 236, 242),
           (250, 251, 253)]
STEEL = [(16, 18, 24), (30, 34, 42), (48, 54, 64), (70, 78, 90), (98, 106, 118), (130, 138, 148), (168, 174, 182),
         (206, 210, 216)]
NEON = [(8, 34, 10), (20, 80, 20), (50, 150, 40), (110, 220, 70), (180, 252, 130), (230, 255, 200)]
SIGNK = [(6, 8, 10), (12, 16, 18), (20, 26, 28), (30, 38, 40)]
CONE = [(60, 16, 6), (120, 36, 10), (190, 70, 20), (236, 116, 40), (252, 170, 90)]
YELLOWM = [(50, 36, 6), (100, 74, 10), (160, 120, 20), (214, 170, 36), (244, 210, 80), (255, 236, 150)]
REDL = [(40, 6, 4), (100, 16, 8), (180, 34, 14), (240, 70, 30), (255, 140, 90), (255, 210, 180)]
BACKING = [(12, 10, 8), (24, 20, 16), (40, 34, 26)]

# ─── Soroll de valors ràpid (taula precalculada) ────────────────────────────
_T = [random.Random(s).random() for s in range(256 * 256)]


def _h(i, j, seed):
    return _T[((i * 73 + seed * 151) & 255) * 256 + ((j * 37 + seed * 59) & 255)]


def vn(u, v, seed=0):
    x0, y0 = math.floor(u), math.floor(v)
    fx, fy = u - x0, v - y0
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a, b = _h(x0, y0, seed), _h(x0 + 1, y0, seed)
    c, d = _h(x0, y0 + 1, seed), _h(x0 + 1, y0 + 1, seed)
    return a + (b - a) * fx + (c - a) * fy + (a - b - c + d) * fx * fy


def fbm(u, v, seed=0, octaves=3):
    s, amp, tot = 0.0, 1.0, 0.0
    for o in range(octaves):
        s += vn(u * (1 << o), v * (1 << o), seed + o * 17) * amp
        tot += amp
        amp *= 0.5
    return s / tot


def hr(*a):
    """Soroll determinista (0..1) a partir d'enters."""
    return _h(a[0] if a else 0, a[1] if len(a) > 1 else 0, a[2] if len(a) > 2 else 0)


# ─── El llenç desplaçat ─────────────────────────────────────────────────────

class Llenc(Canvas):
    """Un Canvas de 640×360 que rep coordenades del món: el píxel (x, y) del món va a (x, y + oy) de la imatge.
    La llum i el tramat es calculen amb les coordenades del món (així el mateix dibuix és igual amb qualsevol oy)."""

    def __init__(self, oy=-DY, light=None, transparent=False, h=360, img=None):
        super().__init__(W, h, light, transparent, img)
        self.oy = oy
        self.top = -oy                  # la y del món de la fila 0
        self.bot = h - 1 - oy           # la y del món de l'última fila

    def put(self, x, y, ramp, lvl, lit=1.0):
        x, y = math.floor(x), math.floor(y)
        Y = y + self.oy
        if 0 <= x < self.w and 0 <= Y < self.h:
            v = lvl + (lit * self.light(x, y) if lit else 0)
            i = math.floor(v + B4[y & 3][x & 3] - 0.5)
            self.P[x, Y] = ramp[max(0, min(len(ramp) - 1, i))] + (255,)

    def flat(self, x, y, col):
        x, y = math.floor(x), math.floor(y) + self.oy
        if 0 <= x < self.w and 0 <= y < self.h:
            self.P[x, y] = tuple(col[:3]) + (255,)

    def get(self, x, y):
        return self.P[int(x), int(y) + self.oy]

    def glow(self, cx, cy, r, col, strength):
        super().glow(cx, cy + self.oy, r, col, strength)

    def _w(self, f):
        return (lambda x, y: f(x, y - self.oy)) if callable(f) else f

    def tint(self, x0, y0, x1, y1, col, k, mask=None):
        super().tint(x0, y0 + self.oy, x1, y1 + self.oy, col, self._w(k), self._w(mask) if mask else None)

    def darken(self, x0, y0, x1, y1, amount, dither=True):
        super().darken(x0, y0 + self.oy, x1, y1 + self.oy, self._w(amount), dither)


def _halo(cv, cx, cy, r, col, k):
    """Un halo additiu suau (sense tramat), per a la llum que surt d'una cosa: llums, bolets, la porta."""
    a = np.asarray(cv.img).astype(np.float32)
    Y0, Y1 = max(0, int(cy + cv.oy - r)), min(cv.h, int(cy + cv.oy + r) + 1)
    X0, X1 = max(0, int(cx - r)), min(cv.w, int(cx + r) + 1)
    if Y0 >= Y1 or X0 >= X1:
        return
    yy, xx = np.mgrid[Y0:Y1, X0:X1]
    d = np.hypot(xx - cx, yy - (cy + cv.oy)) / r
    f = (np.clip(1 - d, 0, 1) ** 2 * k)[..., None]
    sub = a[Y0:Y1, X0:X1]
    sub[..., :3] = np.minimum(255, sub[..., :3] + f * np.array(col, np.float32))
    a[Y0:Y1, X0:X1] = sub
    cv.img.paste(Image.fromarray(a.astype(np.uint8), 'RGBA'))
    cv.P = cv.img.load()


# ─── Lletres de 3×5 (rètols) ────────────────────────────────────────────────
GLYPH = {
    'A': '010101111101101', 'B': '110101110101110', 'C': '011100100100011', 'D': '110101101101110',
    'E': '111100110100111', 'G': '011100101101011', 'I': '111010010010111', 'L': '100100100100111',
    'M': '101111111101101', 'N': '110101101101101', 'O': '010101101101010', 'P': '110101110100100',
    'R': '110101110101101', 'S': '011100010001110', 'T': '111010010010010', 'U': '101101101101111',
    '0': '010101101101010', '2': '110001010100111', '.': '000000000000010', ':': '000010000010000',
    ' ': '000000000000000', '+': '000010111010000', 'Ó': '010101101101010',
}


def text(cv, s, x, y, col, k=1, shear=0.0):
    """Escriu `s` a (x, y) amb lletres de 3×5 a escala k; `shear`: px de y per px de x (rètols en escorç)."""
    x0 = x
    for ch in s:
        g = GLYPH[ch]
        for j in range(5):
            for i in range(3):
                if g[j * 3 + i] == '1':
                    for dy in range(k):
                        for dx in range(k):
                            px = x + i * k + dx
                            cv.flat(px, y + j * k + dy + round((px - x0) * shear), col)
        if ch == 'Ó':                                    # l'accent, a sobre (rètols: una ratlleta inclinada)
            for dy in range(k):
                for dx in range(k):
                    px = x + 2 * k + dx
                    cv.flat(px, y - 2 * k + dy + round((px - x0) * shear), col)
        x += 4 * k
    return x


def text_width(s, k=1):
    return len(s) * 4 * k - k


# ─── Peces del bosc ─────────────────────────────────────────────────────────

def bezier(p0, p1, p2, t):
    a = (1 - t) ** 2
    b = 2 * (1 - t) * t
    c = t * t
    return a * p0[0] + b * p1[0] + c * p2[0], a * p0[1] + b * p1[1] + c * p2[1]


def arrel(cv, p0, p1, p2, r0, r1, ramp=BARK, base=3.6, seed=0, moss=True):
    """Una arrel (o una branca): un tub que s'aprima de r0 a r1 seguint una corba, amb el llom il·luminat."""
    n = int(math.hypot(p2[0] - p0[0], p2[1] - p0[1]) * 1.2) + 4
    for i in range(n + 1):
        t = i / n
        x, y = bezier(p0, p1, p2, t)
        r = r0 + (r1 - r0) * t
        for yy in range(int(y - r - 1), int(y + r + 2)):
            for xx in range(int(x - r - 1), int(x + r + 2)):
                nx, ny = (xx - x) / max(r, 0.6), (yy - y) / max(r, 0.6)
                if nx * nx + ny * ny <= 1:
                    lvl = base - ny * 1.6 - nx * 0.5 + (fbm(xx / 3, yy / 7, seed) - 0.5) * 1.4
                    if moss and ny < -0.2 and fbm(xx / 9, yy / 9, seed + 5) > 0.56:
                        cv.put(xx, yy, MOSS, lvl + 0.4)
                    else:
                        cv.put(xx, yy, ramp, lvl)


def bolet(cv, x, y, h, r, glow=1.0, cap=TURQ, stem=CREAM, halo=True):
    """Un bolet: el peu i el barret; amb `glow` > 0, bioluminescent (el barret és llum, no s'il·lumina)."""
    for yy in range(int(y - h), int(y) + 1):
        w = max(0.6, r * 0.28 * (1 + (y - yy) / max(h, 1) * 0.2))
        for xx in range(int(x - w), int(x + w) + 1):
            cv.put(xx, yy, stem, 2.6 - (xx - x) / max(w, 1) * 0.8 + glow * 1.2, lit=0.4)
    for yy in range(int(y - h - r * 0.7), int(y - h + 1) + 1):
        for xx in range(int(x - r), int(x + r) + 1):
            nx, ny = (xx - x) / r, (yy - (y - h)) / (r * 0.7)
            if nx * nx + ny * ny <= 1 and ny <= 0.25:
                lvl = 2.6 + glow * 2.6 - nx * 0.6 - ny * 1.2
                if ny > 0.05:                            # la vora de sota del barret, una mica més fosca
                    lvl -= 0.8
                cv.put(xx, yy, cap, lvl, lit=0 if glow > 0.5 else 0.6)
    # els punts del barret (més clars)
    for k in range(int(r // 3) + 1):
        px, py = x - r * 0.4 + k * r * 0.45, y - h - r * 0.35 + (k % 2)
        cv.put(px, py, cap, 3.6 + glow * 3, lit=0)
    if glow > 0.5 and halo:
        cv.glow(x, y - h - r * 0.2, r * 4.0, GLOW_T, 0.55 * glow)


def filament(cv, x, y, ang, length, seed, glow=1.0, branch=2, k=3.4, dim=False, sy=0.6):
    """Un filament del Miceli: una línia que serpenteja i es ramifica, de llum turquesa (apagat: blau fosc)."""
    rnd = random.Random(seed)
    for i in range(int(length)):
        ang += (rnd.random() - 0.5) * 0.55
        x += math.cos(ang)
        y += math.sin(ang) * sy
        lvl = (k if not dim else 1.6) - i / length * 1.2
        cv.put(x, y, TURQ, lvl, lit=0)
        if glow and not dim and i % 9 == 0 and rnd.random() < 0.5:
            cv.glow(x, y, 5, GLOW_T, 0.35 * glow)
        if branch and rnd.random() < 0.035:
            filament(cv, x, y, ang + rnd.choice((-1, 1)) * 0.8, length * 0.4, seed * 7 + i, glow, branch - 1, k, dim,
                     sy)


def falguera(cv, x, y, ang, length, side=1, ramp=FERN, lvl=2.2, rim=None, seed=0):
    """Una fulla de falguera: un raquis corbat amb pínnules a banda i banda (per als primers plans foscos)."""
    rnd = random.Random(seed)
    px, py = x, y
    for i in range(int(length)):
        t = i / length
        a = ang + side * t * 0.9
        px += math.cos(a)
        py -= math.sin(a)
        cv.put(px, py, ramp, lvl)
        if i % 3 == 0:
            pl = (1 - t) * length * 0.22 + 2
            for s in (-1, 1):
                pa = a + s * 1.1
                for k in range(int(pl)):
                    qx = px + math.cos(pa) * k
                    qy = py - math.sin(pa) * k + k * k * 0.03
                    cv.put(qx, qy, ramp, lvl + (1.8 if rim and s == rim and k > pl * 0.4 else 0) - k * 0.05)
                    cv.put(qx, qy + 1, ramp, lvl - 0.4)
        if rnd.random() < 0.02:
            ang += (rnd.random() - 0.5) * 0.2


def ombra(cv, cx, cy, rx, ry, k=0.85):
    cv.darken(cx - rx - 2, cy - ry - 2, cx + rx + 2, cy + ry + 2,
              lambda x, y: k if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1 else 0)


# ═══════════════════════════════════════════════════════════════════════════
#  Els modes i la llum
# ═══════════════════════════════════════════════════════════════════════════

SUN = (96, 150)                # al capvespre, el sol es pon entre els troncs
SUN_D = (40, 40)               # de nit (crèdits), la llum ve de dalt a l'esquerra
SUN_M = (618, 140)             # de dia (el bosc obert), el sol del matí, baix a la dreta: entra per la clariana
GOLD = (255, 206, 120)         # la llum daurada del matí
LAMP = (253, 198)              # el fanalet (vermell al capvespre, turquesa al bosc obert)


class Mode:
    def __init__(self, nom):
        self.nom = nom
        self.dia = nom in ('dia', 'nit')                 # la disposició del bosc obert (sense tanca)
        self.tanca = nom == 'capvespre'
        self.glow = {'capvespre': 0.22, 'dia': 0.8, 'nit': 1.0, 'portada': 0.7}[nom]
        self.sky = SKYD if nom == 'dia' else DUSK
        self.haze = HAZED if nom in ('dia', 'nit') else HAZE
        self.trunk = TRUNKM if nom == 'dia' else TRUNKD if nom == 'nit' else HAZE


def llum(m):
    if m.nom in ('dia', 'nit'):
        L = Light(ambient=0.5 if m.nom == 'dia' else 0.2, vignette=(70, 20), floor_fade=None)
        L.width = W
        sx, sy = SUN_M if m.nom == 'dia' else SUN_D
        L.point(sx, sy, r=640, k=1.2, squash=0.9, power=1.2)
        return L
    L = Light(ambient=-0.2, vignette=(70, 30), floor_fade=None)
    L.width = W                # (la vinyeta, a 640 i no als 480 per defecte de la llibreria)
    L.point(SUN[0], SUN[1], r=520, k=1.7, squash=0.8, power=1.3)
    L.point(LAMP[0], LAMP[1], r=40, k=0.7, power=1.6)                  # el fanalet (una mica)
    return L


# ═══════════════════════════════════════════════════════════════════════════
#  Cel i bosc del fons
# ═══════════════════════════════════════════════════════════════════════════

def cel(cv, m):
    y0 = cv.top
    if m.nom == 'dia':
        for y in range(y0, HOR + 2):
            for x in range(W):
                t = (y - y0) / (HOR - y0)
                lvl = 1.0 + 6.0 * t ** 1.2 + (fbm(x / 90, y / 18, 3) - 0.5) * 0.7
                d = math.hypot(x - SUN_M[0], (y - SUN_M[1]) * 1.4)
                lvl += 3.0 * max(0.0, 1 - d / 360) ** 1.6
                cv.put(x, y, SKYD, lvl, lit=0)
        # núvols blancs i alts (es veuen entre la capçada i a la dreta)
        for y in range(y0, HOR - 30):
            for x in range(300, W):
                c = fbm(x / 60, y / 14, 61, 4) - 0.56 + (y - y0) / (HOR - y0) * 0.1
                if c > 0:
                    cv.put(x, y, SKYD, 6.5 + c * 8 - (fbm(x / 9, y / 5, 62) - 0.5), lit=0)
        cv.glow(SUN_M[0], SUN_M[1], 190, GOLD, 0.75)                               # el sol, darrere els troncs
        cv.glow(SUN_M[0], SUN_M[1], 40, (255, 246, 214), 0.9)
        return
    for y in range(y0, HOR + 2):
        for x in range(W):
            d = math.hypot(x - SUN[0], (y - SUN[1]) * 1.6)
            lvl = 1.0 + 4.2 * max(0.0, y / HOR) ** 1.4 + 3.6 * max(0.0, 1 - d / 330) ** 1.6
            lvl -= max(0.0, (x - 380) / 260) * 1.6                                  # a l'est, ja és de nit
            lvl += (fbm(x / 70, y / 14, 3) - 0.5) * 0.8
            cv.put(x, y, DUSK, lvl, lit=0)
    # uns núvols llargs i prims, encesos per sota
    for y in range(max(y0, 70), 140):
        for x in range(0, W):
            c = fbm(x / 80, y / 6, 71, 3) - 0.6
            if c > 0:
                cv.put(x, y, DUSK, cv_sky_lvl(x, y) + 1.2 + c * 6, lit=0)
    for (x, y) in ((560, 22), (604, 46), (512, 38), (628, 14), (470, 18), (590, 8), (540, 60)):   # els primers estels
        cv.flat(x, y, (230, 226, 250))
    cv.glow(SUN[0], SUN[1], 90, (255, 214, 150), 0.7)


def cv_sky_lvl(x, y):
    d = math.hypot(x - SUN[0], (y - SUN[1]) * 1.6)
    return 1.0 + 4.2 * (y / HOR) ** 1.4 + 3.6 * max(0.0, 1 - d / 330) ** 1.6 - max(0.0, (x - 380) / 260) * 1.6


def bosc_fons(cv, m):
    """Troncs llunyans contra la boira (com més lluny, més color d'aire), el sotabosc i la capçada."""
    xmax = W if m.dia or m.nom == 'portada' else 420
    trunks = [(8, 7, 4.4), (46, 5, 5.4), (70, 9, 3.8), (132, 6, 5.0), (150, 11, 3.4), (300, 8, 4.0), (340, 12, 3.2),
              (372, 6, 4.6), (396, 9, 3.6), (28, 14, 2.6), (112, 4, 6.0), (270, 5, 5.2)]
    if xmax == W:                                        # sense l'obra, el bosc continua cap a la dreta
        trunks += [(436, 7, 4.6), (470, 4, 5.8), (506, 10, 3.6), (548, 5, 5.2), (584, 8, 4.2), (626, 12, 3.0),
                   (602, 4, 6.0), (452, 12, 3.0)]
    for k, (x, w, lvl) in enumerate(trunks):
        base = HOR + 14 - lvl * 2
        for y in range(cv.top, int(base)):
            ww = w * (0.8 + 0.2 * max(0, y) / base)
            for xx in range(int(x - ww), int(x + ww) + 1):
                u = (xx - x) / ww
                cv.put(xx, y, m.trunk, lvl - 2.0 + u * 0.8 + (fbm(xx / 2, y / 20, k) - 0.5) * 0.8 + (0.6 if m.dia else 0),
                       lit=0.25)
    # el sotabosc, una franja de mates a contrallum
    for x in range(0, xmax):
        top = HOR - 8 - 18 * fbm(x / 26, 0.5, 9) - 10 * fbm(x / 7, 1.5, 4)
        for y in range(int(top), HOR + 18):
            cv.put(x, y, m.haze, 2.4 + (y - top) * -0.02 + (fbm(x / 4, y / 4, 6) - 0.5) * 1.2, lit=0.6)
    # la capçada: fulles de tardor, amb forats per on passa la llum
    cx1 = 470                                                        # el cel de la dreta queda obert (de dia, hi surt el sol)
    for y in range(cv.top, 110):
        for x in range(0, cx1):
            f = fbm(x / 34, y / 22, 21, 4)
            edge = 0.40 + max(0, y) / 110 * 0.22 + max(0, x - 330) / 140 * 0.3
            if f > edge:
                lvl = 2.0 + (f - edge) * 9 + (fbm(x / 3, y / 3, 8) - 0.5) * 1.6 + (1.4 if m.dia else 0)
                cv.put(x, y, LEAVES, lvl, lit=0.8)


# ═══════════════════════════════════════════════════════════════════════════
#  La tanca i l'obra (capvespre)
# ═══════════════════════════════════════════════════════════════════════════
# La tanca fuig cap al fons, a l'esquerra: comença a x = 392 (lluny) i surt per la dreta (a prop).

def _fence_t(x):
    return (x - 392) / 268


def fence_base(x):
    return 198 + _fence_t(x) * 70


def _fence_h(x):
    return 62 + _fence_t(x) * 96


POSTS = (0.0, 0.18, 0.38, 0.6, 0.84)
GATE_T = 0.6                   # la porta de la tanca, amb el cadenat de codi QR


def obra(cv):
    # el terra remogut, fred
    for x in range(372, W):
        for y in range(HOR - 2, int(fence_base(max(x, 392))) + 1):
            lvl = 2.2 + (y - HOR) * 0.012 + (fbm(x / 20, y / 5, 31) - 0.5) * 1.2
            if (x * 3 + y * 7) % 23 == 0:                                           # rodades de l'excavadora
                lvl -= 0.6
            cv.put(x, y, STONE, lvl, lit=0)
    # arbres tallats: soques
    for x, y, r in ((396, 178, 7), (530, 184, 5), (634, 190, 6)):
        cv.disc(x, y, r, r * 0.35, PLANK, lambda nx, ny: 4.6 - (1.4 if abs(math.hypot(nx, ny) - 0.5) < 0.12 else 0),
                lit=0)
        cv.rect(x - r, y, x + r, y + 5, BARK, lambda xx, yy: 2.0 - abs(xx - x) / r, lit=0)
    # la caseta d'obra: un contenidor blanc, finestres de fluorescent
    x0, x1, y0, y1 = 548, 626, 140, 186
    cv.rect(x0, y0, x1, y1, PLASTIC, lambda x, y: 3.0 - (0.9 if (x - x0) % 8 == 0 else 0) - (y - y0) * 0.012, lit=0)
    cv.rect(x0 - 2, y0 - 3, x1 + 2, y0, PLASTIC, 4.2, lit=0)
    cv.rect(x0, y1 - 2, x1, y1, STEEL, 2.0, lit=0)
    cv.rect(x1 + 1, y0 - 1, x1 + 7, y1, PLASTIC, lambda x, y: 1.6 - (0.6 if (y - y0) % 7 == 0 else 0), lit=0)
    for wx in (556, 582):
        cv.rect(wx, 150, wx + 18, 163, [(150, 200, 196), (210, 244, 236), (240, 255, 250)], 1.2, lit=0)
        cv.rect(wx + 9, 150, wx + 9, 163, PLASTIC, 1.0, lit=0)
        cv.glow(wx + 9, 156, 22, (200, 250, 240), 0.35)
    cv.rect(608, 150, 620, 186, STEEL, 2.6, lit=0)                                 # la porta
    cv.disc(566, 145, 3, 2.4, NEON, 3.0, lit=0)                                     # el logotip (una fulla)
    cv.rect(606, 186, 622, 188, STEEL, 2.4, lit=0)                                 # l'escaleta
    cv.rect(608, 189, 620, 191, STEEL, 2.0, lit=0)
    # l'excavadora: groc, a contrallum del cel violeta; el braç alçat, amb la pala
    ex = 486
    cv.poly([(ex - 18, 194), (ex - 18, 168), (ex + 6, 160), (ex + 30, 162), (ex + 36, 194)], YELLOWM,
            lambda x, y: 2.8 - (y - 160) * 0.02 - (0.8 if x > ex + 22 else 0), lit=0)
    cv.rect(ex - 10, 166, ex + 4, 180, [(40, 50, 60), (70, 90, 100), (110, 140, 150)], 1.0, lit=0)   # la cabina
    cv.rect(ex - 10, 166, ex + 4, 166, YELLOWM, 4.0, lit=0)
    cv.rect(ex - 24, 192, ex + 42, 204, IRONK, lambda x, y: 1.6 + (0.8 if (x // 4) % 2 else 0), lit=0)   # l'eruga
    for x in range(ex - 22, ex + 41, 9):
        cv.disc(x, 198, 2.6, 2.6, IRONK, 3.2, lit=0)
    cv.rect(ex - 24, 203, ex + 42, 204, EARTH, 3.0, lit=0)                         # fang a les erugues
    for i in range(60):                                                             # el braç
        t = i / 59
        x, y = ex + 4 - t * 50, 164 - math.sin(t * 2.4) * 34 + t * 12
        for k in range(-3, 4):
            cv.put(x + k * 0.3, y + k, YELLOWM, 3.6 - abs(k) * 0.5 - (1.2 if k == 3 else 0), lit=0)
    cv.poly([(ex - 52, 166), (ex - 40, 160), (ex - 38, 178), (ex - 54, 176)], IRONK, 2.2, lit=0)  # la pala
    for i in range(5):
        cv.flat(ex - 53 + i * 3, 177, (40, 36, 40))
    # cons
    for x, y in ((448, 208), (530, 210), (588, 204)):
        cv.poly([(x - 5, y), (x, y - 13), (x + 5, y)], CONE, lambda xx, yy, x=x, y=y: 3.0 - (xx - x) * 0.2 +
                (1.6 if (y - yy) in (5, 6) else 0), lit=0)
        cv.rect(x - 6, y, x + 6, y + 1, CONE, 1.4, lit=0)
    # rotllos de gespa artificial, de fons (els que encara no han desenrotllat)
    for x, y in ((414, 190), (436, 193)):
        cv.disc(x, y, 11, 6, NEON, lambda nx, ny: 1.8 - ny * 0.8 + (0.6 if int((nx + 1) * 6) % 2 else 0), lit=0)


def tanca(cv):
    # la malla (de rombes, que s'engrandeixen a prop)
    for x in range(392, W):
        t = _fence_t(x)
        base, h = fence_base(x), _fence_h(x)
        cell = 6 + 6 * t
        u = (x - 392) / (6 + 3 * t)
        for y in range(int(base - h), int(base)):
            v = (base - y) / cell
            th = 0.5 - 0.09 - 0.05 * t
            if abs(((u + v) % 1.0) - 0.5) > th or abs(((u - v) % 1.0) - 0.5) > th:
                cv.put(x, y, STEEL, 3.0 + t * 1.6 - (base - y) / h * 0.6, lit=0.3)
        for yy, lv in ((base - h, 5.0), (base - h + 1, 3.4), (base - 1, 3.0)):     # el tub de dalt i el de baix
            cv.put(x, yy, STEEL, lv + t, lit=0.3)
    # els pals, amb el dau de formigó
    for t in POSTS:
        x = 392 + t * 268
        base, h = fence_base(x), _fence_h(x)
        r = 1.2 + 2.6 * t
        for y in range(int(base - h - 4), int(base + 2)):
            for xx in range(int(x - r), int(x + r) + 1):
                cv.put(xx, y, STEEL, 4.6 - (xx - x) / r * 1.6 + t, lit=0.3)
        cv.rect(x - r - 1, base - h - 6, x + r + 1, base - h - 4, STEEL, 6.0, lit=0)
        cv.rect(x - r - 3, base, x + r + 3, base + 2 + t * 3, STONE, lambda xx, yy: 3.0 - (yy - base) * 0.2, lit=0.4)
    # la porta de la tanca: un marc de tub, i el cadenat amb el codi QR
    xg = 392 + GATE_T * 268
    bg_, hg = fence_base(xg), _fence_h(xg)
    for xx in range(int(xg + 6), int(xg + 40)):
        tt = _fence_t(xx)
        cv.put(xx, fence_base(xx) - _fence_h(xx) + 6, STEEL, 5.0 + tt, lit=0.3)
        cv.put(xx, fence_base(xx) - 6, STEEL, 4.6 + tt, lit=0.3)
    cy = bg_ - hg * 0.48
    cv.rect(xg - 4, cy - 2, xg + 6, cy + 1, IRONK, 3.4, lit=0)                      # la cadena
    cv.ring(xg + 1, cy + 4, 2.5, IRONK, 3.0, lit=0)
    cv.rect(xg - 3, cy + 6, xg + 5, cy + 16, STEEL, lambda x, y: 5.6 - (y - cy) * 0.08, lit=0)   # el cadenat
    for j in range(3):                                                              # el codi QR
        for i in range(3):
            if (i * 5 + j * 3) % 4:
                cv.flat(xg - 1 + i * 2, cy + 8 + j * 2, (20, 22, 26))
    # rètol petit al costat: «PROHIBIT EL PAS»
    cv.rect(xg + 14, cy - 4, xg + 32, cy + 6, PLASTIC, 4.6, lit=0)
    cv.rect(xg + 15, cy - 3, xg + 31, cy - 1, NEON, 3.0, lit=0)
    cartell(cv)


def cartell(cv):
    """El cartell lluminós: «BOSC 2.0» en verd fluor, la fulla de NaturaPlus i el compte enrere."""
    xl, xr = 488, 616

    def top(x):
        return 74 - (x - xl) * 0.10

    def bot(x):
        return 132 + (x - xl) * 0.08
    for x in (500, 604):                                                            # els suports
        cv.rect(x - 1, bot(x) + 4, x + 1, fence_base(x) - _fence_h(x), STEEL, 3.2, lit=0)
    for x in range(xl - 3, xr + 4):                                                 # el marc, blanc
        for y in range(int(top(x)) - 3, int(bot(x)) + 4):
            cv.put(x, y, PLASTIC, 3.6 - (0.8 if x > xr else 0), lit=0)
    for x in range(xl, xr + 1):
        for y in range(int(top(x)), int(bot(x)) + 1):
            cv.put(x, y, SIGNK, 1.6 + (y - top(x)) / (bot(x) - top(x)) * 0.8, lit=0)
    sh = -0.10
    cv.glow(552, 98, 80, (150, 255, 120), 0.25)
    t1 = 'BOSC 2.0'
    x1 = 552 - text_width(t1, 3) // 2
    text(cv, t1, x1, int(top(x1)) + 8, (170, 255, 120), k=3, shear=sh)
    t2 = 'NATURAPLUS S.A.'
    x2 = 552 - text_width(t2) // 2 + 4
    text(cv, t2, x2, int(top(x2)) + 30, (230, 236, 240), shear=sh)
    cv.disc(x2 - 6, int(top(x2)) + 32, 2.4, 3, NEON, 4.0, lit=0)                    # la fulla
    t3 = 'INAUGURACIÓ: 2 DIES'
    x3 = 552 - text_width(t3) // 2
    text(cv, t3, x3, int(top(x3)) + 42, (250, 206, 90), shear=sh)
    for x in range(xl + 4, xr - 3):                                                 # la línia de neó de sota
        cv.put(x, top(x) + 52, NEON, 4.6, lit=0)


# ═══════════════════════════════════════════════════════════════════════════
#  El bosc obert (dia i nit): la clariana on hi havia l'obra
# ═══════════════════════════════════════════════════════════════════════════

def clariana(cv, m):
    """On hi havia l'obra: terra que es recupera (herba nova, plançons), les soques, i el bosc que continua."""
    for x, y, r in ((404, 178, 7), (448, 184, 5), (612, 186, 6)):                    # les soques, amb brots
        cv.disc(x, y, r, r * 0.35, PLANK, lambda nx, ny: 4.6 - (1.4 if abs(math.hypot(nx, ny) - 0.5) < 0.12 else 0),
                lit=0.4)
        cv.rect(x - r, y, x + r, y + 5, BARK, lambda xx, yy, x=x, r=r: 2.4 - abs(xx - x) / r, lit=0.6)
        for k in range(3):
            sx = x - r + 2 + k * r * 0.8
            for j in range(4):
                cv.put(sx + (j % 2), y - 1 - j, GRASS, 5.0 - j * 0.3, lit=0.4)
    # plançons: arbrets nous plantats, amb el tutor de canya
    for x, y, s in ((470, 190, 1.0), (530, 194, 1.1), (580, 182, 0.8)):
        cv.rect(x + 3, y - 22 * s, x + 3, y, PLANK, 4.0, lit=0.5)
        cv.rect(x, y - 18 * s, x, y, BARK, 3.0, lit=0.5)
        for i in range(26):
            a = i * 2.4
            rr = (i / 26) ** 0.5 * 7 * s
            cv.disc(x + math.cos(a) * rr, y - 20 * s + math.sin(a) * rr * 0.8, 2.2, 1.8, GRASS,
                    lambda nx, ny: 4.6 - ny - nx * 0.3, lit=0.6)


def gespa(cv, m):
    """La gespa artificial en rotllos, al peu de la tanca (o, al bosc obert, enrotllada i lligada per endur-se-la)."""
    rolls = ((398, 228, 9, 34), (440, 234, 10, 36), (480, 240, 8, 28))
    for cx, cy, r, L in rolls:
        x0 = cx - L // 2
        # el cos: un cilindre ajagut, de gespa de plàstic (brins curts, massa iguals) i la junta de la tira
        for y in range(int(cy - r), int(cy + r) + 1):
            ny = (y - cy) / r
            for x in range(int(x0), int(x0 + L)):
                lvl = 2.5 - ny * 1.3 - abs(ny) ** 4 * 1.0 + (0.7 if hr(x, y, 9) > 0.62 else 0) - (hr(x, y, 10) > 0.85) * 0.7
                if abs(x - x0 - L * 0.55 - ny * 3) < 0.6:
                    lvl -= 1.0
                cv.put(x, y, NEON, lvl, lit=0.2)
        # la vora de dalt, amb els brins de plàstic que sobresurten
        for x in range(int(x0), int(x0 + L)):
            if hr(x, int(cy), 7) > 0.45:
                cv.put(x, cy - r - 1, NEON, 3.4, lit=0)
        # el cap del rotllo: l'espiral (la gespa i la tela negra de sota)
        for y in range(int(cy - r), int(cy + r) + 1):
            for x in range(int(x0 - r * 0.55), int(x0 + r * 0.55) + 1):
                nx, ny = (x - x0) / (r * 0.55), (y - cy) / r
                d = math.hypot(nx, ny)
                if d <= 1:
                    a = math.atan2(ny, nx)
                    sp = (d * 3.2 + a / (2 * math.pi)) % 1.0
                    if d > 0.9:
                        cv.put(x, y, NEON, 3.2 - ny, lit=0.2)
                    elif sp < 0.5:
                        cv.put(x, y, NEON, 2.8 - d * 0.6 - ny * 0.5, lit=0.2)
                    else:
                        cv.put(x, y, BACKING, 2.0 - d, lit=0)
        if m.dia:                                                                    # lligat amb una corda
            for xr in (x0 + L * 0.25, x0 + L * 0.72):
                for y in range(int(cy - r - 1), int(cy + r) + 1):
                    cv.put(xr, y, CREAM, 2.6 - (y - cy) / r * 0.8, lit=0.6)
        ombra(cv, cx + 2, cy + r + 1, L * 0.55, 2.5, 0.8)


def forats(cv, m):
    """Els forats on hi havia els pals de la tanca: terra remoguda, un trosset de formigó, i ja hi creix alguna herba."""
    for i, t in enumerate(POSTS):
        x = 392 + t * 268
        y = fence_base(x) + 1
        rx, ry = 4 + 5 * t, 1.6 + 2.0 * t
        cv.disc(x, y, rx + 3, ry + 1.6, EARTH, lambda nx, ny: 4.0 - ny * 0.8 + (fbm(nx * 3, ny * 3, i) - 0.5) * 1.6,
                lit=0.6)
        cv.disc(x, y, rx, ry, EARTH, lambda nx, ny: 0.4 + ny * 0.9, lit=0)
        if i % 2:
            cv.disc(x + rx + 4, y + 1, 2 + t * 2, 1.2 + t, STONE, lambda nx, ny: 3.4 - ny, lit=0.4)
        for k in range(2 + i):
            gx = x - rx - 2 + hr(i, k, 3) * (rx * 2 + 4)
            for j in range(int(2 + 3 * t)):
                cv.put(gx, y - ry - 1 - j, GRASS, 4.4 - j * 0.3, lit=0.5)


FLOR_LILA = [(40, 22, 56), (78, 46, 104), (122, 84, 160), (170, 132, 210), (214, 190, 240), (240, 228, 252)]
FLOR_BLANCA = [(90, 86, 70), (150, 146, 126), (206, 202, 182), (238, 236, 220), (252, 252, 244)]
_GRASS = set(GRASS)


def flors(cv, m):
    """Al bosc obert, el prat ha florit: margarides, safrà de tardor (lila) i botons d'or, a clapes. Més grosses a prop;
    només damunt l'herba (no al camí ni a la terra nua)."""
    rnd = random.Random(17)
    for _ in range(1400):
        x = rnd.uniform(0, W)
        y = rnd.uniform(HOR + 10, 284)
        t = (y - HOR) / (288 - HOR)
        if fbm(x / 50, y / 14, 88) < 0.5 - max(0, x - 300) / 2000:                 # a clapes
            continue
        if (x - TC) ** 2 / 90 ** 2 + (y - TBASE) ** 2 / 14 ** 2 < 1:                # no a les arrels del roure
            continue
        if cv.get(x, y)[:3] not in _GRASS:
            continue
        kind = rnd.random()
        ramp, core = ((FLOR_BLANCA, YELLOWM) if kind < 0.45 else (FLOR_LILA, YELLOWM) if kind < 0.8
                      else (YELLOWM, YELLOWM))
        h = int(1 + t * 5 + rnd.random() * 2)
        for j in range(1, h + 1):                                                   # la tija
            cv.put(x, y - j, GRASS, 3.4 - j * 0.1, lit=0.5)
        fy = y - h - 1
        if t < 0.45:                                                                # lluny: un punt
            cv.put(x, fy, ramp, 3.6 + rnd.random(), lit=0.6)
        else:                                                                       # a prop: la corol·la
            r = 1.2 + t * 1.4
            cv.disc(x, fy, r, r * 0.7, ramp, lambda nx, ny: 3.6 - ny * 0.8 - nx * 0.3, lit=0.6)
            if ramp is not YELLOWM:
                cv.put(x, fy, core, 4.2, lit=0.4)


def bassal(cv, m):
    """El bassal, al davant a la dreta (hi ha el Registrador): reflecteix el cel."""
    cx, cy, rx, ry = BASSAL
    for y in range(int(cy - ry - 2), int(cy + ry + 3)):
        for x in range(int(cx - rx - 4), int(cx + rx + 5)):
            nx, ny = (x - cx) / rx, (y - cy) / ry
            d = nx * nx + ny * ny + (fbm(x / 6, y / 2, 44) - 0.5) * 0.5
            if d <= 1:
                if m.nom == 'dia':
                    lvl = 4.2 + ny * 1.6 + (0.8 if (y + x // 6) % 3 == 0 else 0)
                    cv.put(x, y, SKYD, lvl, lit=0)
                else:
                    cv.put(x, y, SKYD, 1.0 + ny * 0.8, lit=0)
            elif d <= 1.35:
                cv.put(x, y, EARTH, 2.0, lit=0.6)
    for k in range(5):                                                              # joncs a la vora
        jx = cx + rx * (0.5 + k * 0.12)
        for j in range(8 + k * 2):
            cv.put(jx + j * 0.15, cy - 2 - j, GRASS, 3.6 - j * 0.1, lit=0.6)


BASSAL = (478, 276, 34, 7)
TAULA = (350, 246, 30, 8, 15)  # centre x, y del pla de dalt, mig ample, mig alt de l'el·lipse, alçada


def taula(cv, m):
    """La taula feta d'una soca, amb les tasses de te de menta, la tetera i el pot de melmelada de la Vet."""
    cx, cy, rx, ry, h = TAULA
    # el cos de la soca, amb l'escorça i dues arrels que s'enfonsen
    for y in range(int(cy), int(cy + h + ry) + 1):
        for x in range(int(cx - rx - 1), int(cx + rx + 2)):
            nx = (x - cx) / rx
            if abs(nx) > 1.02:
                continue
            ybot = cy + h + ry * math.sqrt(max(0.0, 1 - nx * nx))
            if y > ybot:
                continue
            lvl = 3.2 - nx * 1.3 - abs(nx) ** 5 * 1.4 + (fbm(nx * 8 + 2, y / 5, 51) - 0.5) * 1.8
            cv.put(x, y, BARK, lvl, lit=0.8)
    for s in (-1, 1):
        arrel(cv, (cx + s * rx * 0.8, cy + h), (cx + s * (rx + 8), cy + h + ry + 2), (cx + s * (rx + 18), cy + h + ry + 4),
              5, 1.5, base=3.0, seed=52 + s, moss=False)
    # el pla de dalt: fusta tallada, amb els anells
    cv.disc(cx, cy, rx, ry, PLANK, lambda nx, ny: 5.0 - ny * 0.6 - nx * 0.4 -
            (1.2 if (math.hypot(nx, ny * 1.0) * 6) % 1.0 < 0.18 else 0), lit=0.6)
    # les tasses (de fang), la tetera i el pot de melmelada
    for k, (tx, ty) in enumerate(((cx - 18, cy - 1), (cx - 6, cy + 3), (cx + 10, cy + 2), (cx + 20, cy - 2))):
        cv.rect(tx - 2, ty - 5, tx + 2, ty, CLAY, lambda x, y, tx=tx: 4.0 - (x - tx) * 0.4, lit=0.6)
        cv.rect(tx - 1, ty - 5, tx + 1, ty - 5, GRASS, 4.6, lit=0)                    # el te de menta
        cv.put(tx + 3, ty - 3, CLAY, 3.0, lit=0.6)                                    # la nansa
        cv.put(tx + 3, ty - 2, CLAY, 2.6, lit=0.6)
    tx, ty = cx + 2, cy - 4                                                          # la tetera
    cv.disc(tx, ty - 4, 5, 4.4, CLAY, lambda nx, ny: 4.4 - nx * 0.8 - ny * 1.0, lit=0.6)
    cv.rect(tx - 1, ty - 10, tx + 1, ty - 9, CLAY, 3.4, lit=0.6)
    for i in range(4):
        cv.put(tx + 5 + i, ty - 4 - i * 0.6, CLAY, 3.4, lit=0.6)
    jx, jy = cx - 14, cy - 5                                                         # la melmelada
    cv.rect(jx - 2, jy - 5, jx + 2, jy, JAM, lambda x, y: 3.4 - (x - jx) * 0.4, lit=0.5)
    cv.rect(jx - 2, jy - 6, jx + 2, jy - 6, CREAM, 3.0, lit=0.5)
    cv.flat(jx - 1, jy - 3, (250, 170, 170))


# ═══════════════════════════════════════════════════════════════════════════
#  El terra
# ═══════════════════════════════════════════════════════════════════════════

# El camí: ve de l'esquerra (la sortida) i arriba a les pedres de davant la porta.
CAMI = [(-20, 262), (60, 266), (140, 262), (200, 254), (226, 246)]


def _dist_cami(x, y):
    best = 1e9
    for (ax, ay), (bx, by) in zip(CAMI, CAMI[1:]):
        dx, dy = bx - ax, (by - ay) * 2.6
        px, py = x - ax, (y - ay) * 2.6
        t = max(0.0, min(1.0, (px * dx + py * dy) / (dx * dx + dy * dy)))
        best = min(best, math.hypot(px - t * dx, py - t * dy))
    return best


def terra(cv, m):
    for y in range(HOR + 6, cv.bot + 1):
        t = (y - HOR) / (288 - HOR)
        for x in range(0, W):
            if m.tanca and x >= 392 and y < fence_base(x):
                continue                                                            # darrere la tanca: l'obra
            lvl = 2.7 + t * 2.0 + (fbm(x / (14 + 40 * t), y / (3 + 12 * t), 12) - 0.5) * 1.6
            dc = _dist_cami(x, y)
            wc = 10 + (y - HOR) * 0.35
            if dc < wc:                                                             # el camí, de terra més clara
                lvl += 1.1 * min(1.0, (wc - dc) / 4) - (0.6 if hr(x // 2, y, 15) > 0.93 else 0)
            ramp = EARTH
            if m.dia and dc > wc + 2:                                               # al bosc obert, herba nova
                g = fbm(x / (5 + 18 * t), y / (2 + 5 * t), 19) + fbm(x / 40, y / 10, 23) * 0.5 - 0.25
                if g > 0.52 - max(0, x - 300) / 1600 - max(0, 210 - y) / 200:
                    ramp = GRASS
                    lvl += 0.2 + (0.8 if hr(x, y, 21) > 0.8 else 0)
            cv.put(x, y, ramp, lvl, lit=0.9)
            # fulles caigudes: més grosses a prop
            s = 1 + int(t * 3)
            if hr(x // s, y // s, 5) > 0.99 - t * 0.04 and fbm(x / 40, y / 12, 77) > 0.48:
                cv.put(x, y, LEAF, 2.0 + hr(x // s, y // s, 6) * 3, lit=0.7)
    # les pedres planes del caminet, davant la porta
    for k, (px, py, r) in enumerate(((214, 247, 6), (198, 252, 7), (178, 257, 8), (156, 262, 9))):
        cv.disc(px, py, r, r * 0.32, STONE, lambda nx, ny, k=k: 4.0 - ny * 1.2 - nx * 0.4 +
                (fbm(nx * 3, ny * 3, k) - 0.5), lit=0.8)
        cv.darken(px - r, py + r * 0.3, px + r, py + r * 0.3 + 1, 0.6)


# ═══════════════════════════════════════════════════════════════════════════
#  El roure, la porta i el que hi ha al voltant
# ═══════════════════════════════════════════════════════════════════════════
TC, TBASE = 214, 246


def tronc_c(y):
    return TC + 6 * math.sin(y / 46) - 4


def tronc_w(y):
    return 44 + 60 * max(0.0, (y - 170) / 76) ** 2.2 - 4 * max(0.0, min(120, 120 - y) / 120)


DOOR = (222, 186, 238, 17)     # centre x, dalt, baix, mig ample (la porta fa un metre: l'espatlla de la Iri)
BELL = (193, 200)              # la campaneta, a l'esquerra de la porta
BUSTIA = (276, 214)            # la bústia, en un pal, a la dreta
ESTACA = (243, 224, 250)       # x, dalt, baix: clavada just davant el cantell de la porta (que s'obre cap enfora)
CARGOL = (512, 233)            # al peu de la tanca, entre el fang


def roure(cv, m):
    # les branques grosses, que surten del quadre
    for p0, p1, p2, r0, r1, s in (((200, 70), (120, 30), (-20, 10), 20, 9, 3),
                                  ((228, 60), (300, 20), (420, -10), 16, 6, 4),
                                  ((190, 110), (110, 90), (40, 70), 9, 3, 5),
                                  ((236, 96), (290, 76), (340, 56), 8, 3, 6)):
        arrel(cv, p0, p1, p2, r0, r1, base=3.0, seed=s)
    if cv.top < 0:                                                                  # a pantalla sencera: més branques
        for p0, p1, p2, r0, r1, s in (((206, 0), (180, -40), (120, -80), 18, 8, 7),
                                      ((222, 10), (280, -30), (340, -70), 12, 5, 8)):
            arrel(cv, p0, p1, p2, r0, r1, base=3.0, seed=s)
    # el tronc
    for y in range(cv.top, TBASE + 6):
        c, w = tronc_c(y), tronc_w(y)
        for x in range(int(c - w), int(c + w) + 1):
            u = (x - c) / w
            fis = fbm(u * 9 + 3, y / 34, 41, 3)
            lvl = 3.6 - u * 1.3 - abs(u) ** 6 * 1.8 + (fis - 0.5) * 2.4
            if fis < 0.36:
                lvl -= 1.6                                                          # les esquerdes de l'escorça
            if u < -0.15 and fbm(x / 8, y / 10, 44) > 0.62 + u * 0.25:
                cv.put(x, y, MOSS, lvl + 0.6, lit=0.9)
            else:
                cv.put(x, y, BARK, lvl, lit=0.9)
    # les arrels per terra
    for p1, p2, r0, s in (((120, 246), (30, 262), 15, 11), ((150, 262), (96, 286), 13, 12),
                          ((290, 262), (330, 282), 12, 13), ((300, 244), (382, 252), 11, 14),
                          ((176, 258), (186, 290), 10, 15), ((80, 232), (10, 238), 8, 16)):
        arrel(cv, (TC + (p2[0] - TC) * 0.15, TBASE - 8), p1, p2, r0, 2, base=3.4, seed=s)
    # heura que s'enfila pel tronc (a la banda del sol)
    rnd = random.Random(9)
    for k in range(3):
        x, y = TC - 30 + k * 9, TBASE - 10
        for i in range(70 + k * 20):
            x += math.sin(i / 7 + k) * 0.7
            y -= 1
            cv.put(x, y, MOSS, 3.0, lit=0.8)
            if i % 4 == 0:
                s = rnd.choice((-1, 1))
                cv.disc(x + s * 2, y, 1.8, 1.3, MOSS, lambda nx, ny: 4.0 - ny - nx * 0.4, lit=0.8)


def porta(cv, m, ences=True):
    """La porta tancada, el marc d'escorça i el graó; la campaneta, el fanalet i la bústia."""
    cx, top, bot, hw = DOOR
    for y in range(top - 4, bot + 1):
        for x in range(cx - hw - 4, cx + hw + 5):
            d = math.hypot(x - cx, (y - (top + hw)) * 1.0) if y < top + hw else abs(x - cx)
            if d <= hw:
                plank = (x - cx + hw) % 6 == 0
                lvl = 3.6 - (1.6 if plank else 0) - (y - top) * 0.012 + (x - cx) / hw * -0.4 + (fbm(x / 2, y / 9, 7) - 0.5)
                cv.put(x, y, PLANK, lvl, lit=0.7)
            elif d <= hw + 4:
                cv.put(x, y, BARK, 1.4 + (d - hw) * 0.3, lit=0.6)
    for yy in (top + 18, bot - 12):                                                  # frontisses
        cv.rect(cx - hw, yy, cx - hw + 12, yy + 2, IRONK, lambda x, y: 2.6 - (x - cx + hw) * 0.08, lit=0.5)
    cv.disc(cx + hw - 6, top + 32, 2, 2, IRONK, lambda nx, ny: 3.0 - ny, lit=0.5)    # la baula
    cv.disc(cx, top + 12, 3.4, 3.4, IRONK, 1.0, lit=0)                              # l'espiell, rodó
    cv.disc(cx, top + 12, 2.4, 2.4, WARM if m.nom == 'capvespre' else TURQ, 1.6, lit=0)
    cv.rect(cx - hw - 6, bot, cx + hw + 6, bot + 3, STONE, lambda x, y: 3.6 - (1.2 if x % 7 == 0 else 0), lit=0.8)
    # la campaneta, penjada d'un ganxo de ferro
    bx, by = BELL
    cv.rect(bx - 1, by - 8, bx + 6, by - 7, IRONK, 2.4)
    cv.rect(bx, by - 7, bx, by - 5, IRONK, 2.4)
    cv.disc(bx, by - 1, 3.8, 4.2, BRASS, lambda nx, ny: 2.4 - nx - ny * 0.4)
    cv.rect(bx - 4, by + 2, bx + 4, by + 3, BRASS, 2.0)
    cv.flat(bx, by + 4, (90, 60, 20))
    for y in range(by + 4, by + 13):                                                # el cordill
        cv.put(bx + 1, y, CREAM, 2.0)
    # el fanalet (vermell, o turquesa al bosc obert), penjat d'una escarpia
    lx, ly = LAMP
    cv.rect(lx - 7, ly - 10, lx + 1, ly - 9, IRONK, 2.4)
    cv.rect(lx - 4, ly - 7, lx + 4, ly + 6, IRONK, 1.6)
    cv.rect(lx - 5, ly - 8, lx + 5, ly - 7, IRONK, 2.4)
    cv.rect(lx - 2, ly + 6, lx + 2, ly + 7, IRONK, 2.4)
    llum_fanal(cv, m, ences)
    # la bústia, en un pal, amb la nota que sobresurt
    mx, my = BUSTIA
    cv.rect(mx, my + 10, mx + 2, bot + 6, PLANK, 2.4, lit=0.7)
    cv.rect(mx - 7, my, mx + 9, my + 10, PLANK, lambda x, y: 3.4 - (y - my) * 0.1 - (1.4 if y == my + 3 else 0), lit=0.7)
    cv.rect(mx - 8, my - 2, mx + 10, my - 1, PLANK, 4.0, lit=0.7)                   # la teulada
    cv.rect(mx - 3, my - 4, mx + 3, my - 1, NOTE, 3.0, lit=0.6)
    cv.rect(mx + 9, my + 2, mx + 10, my + 6, CONE, 2.6, lit=0.4)                    # la banderola
    ombra(cv, mx + 4, bot + 6, 7, 1.6)


def llum_fanal(cv, m, ences):
    lx, ly = LAMP
    if m.nom == 'capvespre':
        if ences:
            cv.rect(lx - 3, ly - 5, lx + 3, ly + 4, REDL, lambda x, y: 3.6 - abs(x - lx) * 0.3 - abs(y - ly) * 0.2, lit=0)
            cv.glow(lx, ly, 26, (255, 70, 40), 0.6)
        else:
            cv.rect(lx - 3, ly - 5, lx + 3, ly + 4, REDL, lambda x, y: 1.4 - abs(x - lx) * 0.2, lit=0)
    else:
        cv.rect(lx - 3, ly - 5, lx + 3, ly + 4, TURQ, lambda x, y: 5.6 - abs(x - lx) * 0.3 - abs(y - ly) * 0.2, lit=0)
        cv.glow(lx, ly, 26, GLOW_T, 0.5)


def porta_oberta(cv, m):
    """La porta oberta cap enfora (frontisses a l'esquerra): el forat amb llum a dins (càlida al capvespre, turquesa
    al bosc obert), l'escaleta que baixa i el full de la porta, vist de cantell."""
    cx, top, bot, hw = DOOR
    calid = m.nom == 'capvespre'
    ramp = WARM if calid else TURQ
    for y in range(top, bot + 1):
        for x in range(cx - hw, cx + hw + 1):
            d = math.hypot(x - cx, y - (top + hw)) if y < top + hw else abs(x - cx)
            if d <= hw:
                # la llum surt de baix (de la centraleta): més clara a baix i al mig
                v = (y - top) / (bot - top)
                lvl = 0.6 + v * 3.0 - abs(x - cx) / hw * 1.2 + (0 if calid else 0.4)
                cv.put(x, y, ramp, lvl, lit=0)
    # l'escala de mà que baixa (dos muntants i tres graons, a contrallum)
    for sx in (cx - 7, cx + 7):
        cv.rect(sx, bot - 22, sx + 1, bot, PLANK, 1.0, lit=0)
    for k in range(4):
        cv.rect(cx - 7, bot - 20 + k * 6, cx + 8, bot - 20 + k * 6, PLANK, 1.4, lit=0)
    # el full de la porta, obert cap a la càmera: un trapezi estret a l'esquerra del marc
    x0 = cx - hw - 2
    for y in range(top + 2, bot + 1):
        w = 13
        dy = (y - top) / (bot - top)
        for x in range(x0 - w, x0 + 1):
            u = (x - (x0 - w)) / w
            yy = y + (1 - u) * 6                                                    # el cantell de prop baixa una mica
            lvl = 3.2 + u * 1.0 - (1.0 if (x - x0) % 4 == 0 else 0) + (fbm(x / 2, yy / 9, 7) - 0.5)
            if m.nom == 'nit':
                lvl = 0.6 + u * 0.8 + (1.6 if x == x0 else 0)                       # de nit, a contrallum
            if yy <= bot + 5:
                cv.put(x, yy, PLANK, lvl, lit=0.7 if m.nom != 'nit' else 0)
        cv.put(x0 - w - 1, y + 6, PLANK, 1.0, lit=0)
    cv.rect(x0 - 8, top + 20, x0 - 3, top + 22, IRONK, 2.4, lit=0.4)               # la frontissa, vista de costat
    _halo(cv, cx, bot - 8, 46, (255, 170, 80) if calid else GLOW_T, 0.55 if calid else 0.6)
    # la llum que surt i s'estén pel terra, davant la porta
    cv.tint(cx - 40, bot, cx + 40, bot + 18, (255, 190, 110) if calid else GLOW_T,
            lambda x, y: 0.45 * max(0.0, 1 - math.hypot((x - cx) / 40, (y - bot) / 18)))


def estaca(cv):
    """L'estaca de topògraf, clavada davant el cantell de la porta, amb la cinta de NaturaPlus i la punta pintada."""
    x, y0, y1 = ESTACA
    for y in range(y0, y1):
        for xx in range(x - 2, x + 2):
            cv.put(xx, y, PLANK, 4.6 - (xx - x + 0.5) * 0.9 - (0.8 if (y - y0) % 7 == 0 else 0), lit=0.8)
    cv.rect(x - 1, y0, x + 1, y0 + 4, CONE, 3.8, lit=0.3)                           # la punta pintada
    cv.rect(x - 1, y0 + 9, x + 1, y0 + 10, PLASTIC, 4.0, lit=0)                     # l'etiqueta blanca
    for i in range(18):                                                             # la cinta, que voleia
        tx, ty = x + 1 + i, y0 + 5 + math.sin(i * 0.6) * 2 + i * 0.3
        cv.put(tx, ty, NEON, 3.8 - (i % 4 == 0) * 1.2, lit=0.3)
        cv.put(tx, ty + 1, NEON, 2.8, lit=0.3)
    for k in range(4):                                                              # terra remoguda al peu
        cv.put(x - 3 + k * 2, y1 - 1, EARTH, 4.6, lit=0.6)
    ombra(cv, x + 8, y1, 9, 1.6)


def cargol(cv):
    """El cargol galvanitzat, mig enfangat: brilla massa per ser del bosc."""
    x, y = CARGOL
    cv.disc(x + 1, y + 1, 9, 2.6, EARTH, lambda nx, ny: 1.6 + (fbm(nx * 4, ny * 4, 81) - 0.5) * 1.2, lit=0.5)
    cv.rect(x - 2, y - 1, x + 4, y, STEEL, lambda xx, yy: 6.6 - (yy - y + 1) * 1.6, lit=0)
    cv.rect(x + 5, y - 2, x + 6, y + 1, STEEL, 6.0, lit=0)                          # el cap
    for k in range(3):
        cv.flat(x - 1 + k * 2, y, (120, 126, 136))                                  # la rosca
    cv.flat(x + 1, y - 1, (250, 252, 255))
    cv.glow(x + 2, y - 1, 7, (230, 240, 255), 0.75)


# ═══════════════════════════════════════════════════════════════════════════
#  La xarxa: bolets i filaments
# ═══════════════════════════════════════════════════════════════════════════
# Els bolets clicables (`bolets`): la colla de l'arrel de l'esquerra del roure.
BOLETS = ((148, 216, 7, 7), (160, 210, 5, 5), (137, 224, 4, 4), (170, 220, 3, 3), (126, 218, 3, 3))
BOLETS_ALTRES = ((268, 194, 5, 5), (277, 202, 3, 3), (60, 236, 7, 7), (72, 240, 4, 4), (318, 256, 4, 4),
                 (106, 254, 5, 5), (182, 162, 4, 4), (174, 168, 3, 3))
BOLETS_NOUS = ((300, 246, 4, 4), (390, 262, 5, 5), (402, 266, 3, 3), (520, 252, 4, 4), (240, 272, 5, 5),
               (560, 238, 3, 3), (36, 252, 4, 4), (196, 140, 3, 3))       # al bosc obert, n'han sortit més


def xarxa(cv, m):
    g = m.glow
    dim = g < 0.5
    for seed, (x, y, a, l) in enumerate(((150, 252, 3.0, 120), (110, 270, 2.6, 110), (290, 266, 0.2, 90),
                                         (230, 282, 3.4, 80), (340, 252, 0.0, 60), (60, 248, 3.3, 70))):
        filament(cv, x, y, a, l, seed + 3, glow=g, dim=dim)
    if m.dia:                                                                       # fins on hi havia la tanca
        for seed, (x, y, a, l) in enumerate(((360, 258, 0.1, 140), (420, 280, -0.2, 120), (300, 236, -0.3, 120))):
            filament(cv, x, y, a, l, seed + 20, glow=g, dim=dim)
    if m.dia:                                                                       # i pugen pel tronc
        for seed, (x, y, l) in enumerate(((176, 236, 120), (250, 238, 100), (200, 230, 80), (238, 120, 70))):
            filament(cv, x, y, -math.pi / 2 + (seed - 1.5) * 0.15, l, seed + 40, glow=g * 0.8, branch=1, k=3.8,
                     sy=1.0)
    bolets = BOLETS + BOLETS_ALTRES + (BOLETS_NOUS if m.dia else ())
    for x, y, h, r in bolets:
        bolet(cv, x, y, h, r, glow=g)


# ═══════════════════════════════════════════════════════════════════════════
#  Primer pla
# ═══════════════════════════════════════════════════════════════════════════

def primer_pla(cv, m):
    rim = 1 if m.nom != 'nit' else None
    # falgueres a l'esquerra, a contrallum (la vora de dalt, càlida)
    for i, (x, y, a, l, s) in enumerate(((-6, 300, 1.15, 110, -1), (14, 298, 0.8, 120, -1), (46, 300, 1.45, 90, 1),
                                          (-10, 268, 0.45, 96, -1), (84, 300, 1.85, 70, 1), (24, 300, 1.7, 100, 1))):
        falguera(cv, x, y, a, l, side=s, lvl=1.5 + i * 0.1, rim=rim, seed=i)
    # una arrel gruixuda que surt de la cantonada de baix a l'esquerra
    arrel(cv, (-10, 296), (40, 280), (120, 300), 10, 5, base=2.0, seed=33, moss=True)
    # bolets en silueta, entre les falgueres
    for x, y, h, r in ((70, 296, 9, 8), (82, 298, 6, 5)):
        bolet(cv, x, y, h, r, glow=m.glow, halo=False)
    # una pedra i falgueres a la dreta
    cv.disc(612, 296, 46, 26, STONE, lambda nx, ny: 2.0 - ny * 1.4 - nx * 0.6 + (fbm(nx * 4, ny * 4, 3) - 0.5) * 1.6)
    cv.disc(612, 296, 46, 26, MOSS, lambda nx, ny: 1.0 if ny < -0.55 and fbm(nx * 5, 1, 9) > 0.5 else -9)
    for i, (x, y, a, l, s) in enumerate(((556, 300, 1.7, 80, 1), (596, 296, 2.1, 100, 1), (646, 300, 2.4, 90, 1))):
        falguera(cv, x, y, a, l, side=s, lvl=1.6, seed=10 + i)
    if m.nom == 'dia':
        branca_davant(cv)


def branca_davant(cv):
    """De dia: una branca de roure que entra per dalt a la dreta, molt a prop, a contrallum del sol del matí (la vora
    de les fulles, daurada). Emmarca el quadre per dalt, on a la vora del bosc hi havia el cartell."""
    p0, p1, p2 = (700, 18), (600, 58), (452, 36)
    arrel(cv, p0, p1, p2, 9, 2, base=1.4, seed=61, moss=True)
    arrel(cv, bezier(p0, p1, p2, 0.45), (560, 84), (520, 96), 3, 1, base=1.4, seed=62, moss=False)
    # el fullatge: una massa amb forats (com la capçada del fons), que penja de la branca; a contrallum, fosc, amb la
    # vora de cara al sol encesa i alguna fulla que la llum travessa
    pts = [bezier(p0, p1, p2, i / 60) for i in range(61)] + [bezier((590, 66), (560, 84), (520, 96), i / 20)
                                                              for i in range(21)]
    sx, sy = SUN_M

    def dens(x, y):
        best = 1e9
        for px, py in pts:
            dy = y - py
            dy = dy * 0.45 if dy > 0 else dy * 1.4                                 # penja cap avall
            best = min(best, math.hypot(x - px, dy))
        return fbm(x / 10, y / 7, 65, 4) - best / 34

    E = 0.26
    for y in range(cv.top, 150):
        for x in range(420, W):
            f = dens(x, y)
            if f < E:
                continue
            # com la capçada del fons, però més a prop: més fosca a dins i la vora encesa
            lvl = 1.6 + (f - E) * 7 + (fbm(x / 3, y / 3, 66) - 0.5) * 1.4
            edge = min(dens(x + dx, y + dy) for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)))
            if edge < E:
                ux, uy = sx - x, sy - y
                n = math.hypot(ux, uy)
                lvl += 2.0 + (2.4 if dens(x + ux / n * 2, y + uy / n * 2) < E else 0)
            if fbm(x / 5, y / 5, 68) > 0.64:                                        # fulles que la llum travessa
                cv.put(x, y, LEAF, 2.4 + (f - E) * 6, lit=0)
            else:
                cv.put(x, y, LEAVES, lvl, lit=0)


# ═══════════════════════════════════════════════════════════════════════════
#  La nit: enfosquir i tornar blau (el turquesa es pinta després)
# ═══════════════════════════════════════════════════════════════════════════

def nit(img, k=1.0):
    a = np.asarray(img).astype(np.float32)
    lum = a[..., :3] @ np.array([0.3, 0.55, 0.15], np.float32)
    rgb = a[..., :3] * np.array([0.22, 0.26, 0.40], np.float32) + lum[..., None] * np.array([0.04, 0.06, 0.12]) \
        + np.array([3, 5, 14], np.float32)
    a[..., :3] = np.clip(rgb, 0, 255)
    return Image.fromarray(a.astype(np.uint8), 'RGBA')


def cel_nit(cv):
    """El cel de nit: blau fosc, estels i la lluna a la dreta (on hi havia el cartell)."""
    rnd = random.Random(5)
    for y in range(cv.top, HOR + 2):
        for x in range(W):
            t = (y - cv.top) / (HOR - cv.top)
            v = 6 + 30 * t ** 1.6 + (fbm(x / 80, y / 16, 3) - 0.5) * 6
            cv.flat(x, y, (int(v * 0.35), int(v * 0.55), int(v * 1.2 + 10)))
    for i in range(160):
        x, y = rnd.randrange(W), rnd.randrange(cv.top, HOR - 10)
        b = rnd.random()
        cv.flat(x, y, (int(150 + 100 * b), int(160 + 90 * b), 255))
        if b > 0.85:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                cv.flat(x + dx, y + dy, (90, 110, 160))
    mx, my = MOON
    cv.disc(mx, my, 12, 12, [(150, 160, 170), (200, 206, 210), (236, 238, 232), (252, 252, 244)],
            lambda nx, ny: 3.2 - nx * 0.6 - ny * 0.4 - (1.0 if fbm(nx * 2 + 5, ny * 2, 8) > 0.6 else 0), lit=0)
    cv.glow(mx, my, 60, (140, 170, 220), 0.35)


MOON = (560, 36)


# ═══════════════════════════════════════════════════════════════════════════
#  L'escena, per capes
# ═══════════════════════════════════════════════════════════════════════════

@functools.lru_cache(maxsize=None)
def escena(nom, oy=-DY, llum_ences=True):
    """→ (fons RGBA, taula RGBA o None, primer pla RGBA): el fons ja porta la taula i el primer pla a sobre; les capes
    soles serveixen per a les màscares de FRONT."""
    m = Mode(nom)
    L = llum(m)
    cv = Llenc(oy, L)
    if m.nom == 'nit':
        cel_nit(cv)
        sky = cv.img.copy()
    cel(cv, m if m.nom != 'nit' else Mode('dia'))
    after_sky = cv.img.copy()
    bosc_fons(cv, m)
    if m.nom == 'dia':                                                              # la boira daurada del matí
        cv.glow(SUN_M[0], SUN_M[1] + 10, 300, GOLD, 0.45)
    if m.tanca:
        obra(cv)
    terra(cv, m)
    if m.dia:
        clariana(cv, m)
        flors(cv, m)
    if m.tanca:
        tanca(cv)
    if m.dia:
        forats(cv, m)
        bassal(cv, m)
    else:
        gespa(cv, m)
    roure(cv, m)
    porta(cv, m, llum_ences)
    if m.dia and m.nom == 'dia':
        raigs(cv)
        matinada(cv)
    if m.nom == 'nit':
        # la nit: tot més fosc i blau, menys el cel (que ja és de nit) i el que fa llum
        a0, a1 = np.asarray(after_sky), np.asarray(cv.img)
        same = (a0 == a1).all(axis=2)
        dark = nit(cv.img)
        out = np.where(same[..., None], np.asarray(sky), np.asarray(dark))
        cv.img.paste(Image.fromarray(out.astype(np.uint8), 'RGBA'))
        cv.P = cv.img.load()
        llum_fanal(cv, m, True)
    if m.dia:
        porta_oberta(cv, m)
    xarxa(cv, m)
    if m.nom == 'nit':
        for x, y, h, r in BOLETS + BOLETS_ALTRES + BOLETS_NOUS:
            _halo(cv, x, y - h, r * 5, GLOW_T, 0.18)
    # les capes del davant
    tl = None
    if m.dia:
        tc = Llenc(oy, L, transparent=True)
        taula(tc, m)
        tl = tc.img if m.nom != 'nit' else nit(tc.img)
        cv.img.alpha_composite(tl)
    pc = Llenc(oy, L, transparent=True)
    primer_pla(pc, m)
    front = pc.img if m.nom != 'nit' else nit(pc.img, 1.0)
    cv.img.alpha_composite(front)
    cv.P = cv.img.load()
    return cv.img, tl, front


def matinada(cv):
    """De dia: tot el quadre, cap a l'or del matí; més a prop del sol i al fons (l'aire en té), menys al davant."""
    a = np.asarray(cv.img).astype(np.float32)
    h, w = a.shape[:2]
    Y, X = np.mgrid[0:h, 0:w].astype(np.float32)
    Y -= cv.oy                                                                      # (en y del món)
    d = np.hypot(X - SUN_M[0], (Y - SUN_M[1]) * 1.3)
    near = np.clip(1 - d / 520, 0, 1) ** 1.3
    deep = np.clip(1 - np.abs(Y - HOR) / 90, 0, 1)                                  # l'aire, a l'alçada de l'horitzó
    k = (0.28 + 0.4 * near + 0.18 * deep)[..., None]
    warm = a[..., :3] * np.array([1.10, 0.98, 0.74], np.float32) + np.array([20, 12, 0], np.float32)
    haze = np.array(GOLD, np.float32)
    out = a[..., :3] * (1 - k) + warm * k
    kh = (0.32 * near * deep + 0.12 * near)[..., None]
    out = out * (1 - kh) + haze * kh
    a[..., :3] = np.clip(out, 0, 255)
    cv.img.paste(Image.fromarray(a.astype(np.uint8), 'RGBA'))
    cv.P = cv.img.load()


def raigs(cv):
    """De dia: els raigs del sol del matí, que entren baixos per la clariana de la dreta i travessen el prat."""
    def k(x, y):
        if y < HOR - 40:
            return 0
        a = math.atan2(y - SUN_M[1], x - SUN_M[0])
        b = math.sin(a * 23) * 0.5 + 0.5
        b *= fbm(a * 9, 0.5, 91)
        far = min(1.0, math.hypot(x - SUN_M[0], y - SUN_M[1]) / 600)
        return max(0.0, b - 0.5) * 0.7 * (1 - far * 0.6)
    cv.tint(0, HOR - 60, W - 1, 290, GOLD, k)


def mascara(img):
    """fn(x, y) → bool per a FRONT: els píxels no transparents d'una capa (en píxels de la imatge)."""
    a = np.asarray(img)[..., 3] > 0
    return lambda x, y: bool(a[y, x])


def fons_sala(img, cv):
    """Posa el fons d'una sala de joc al Canvas de render.py (a sota de y = 260, negre: el HUD)."""
    cv.img.paste(img)
    cv.P = cv.img.load()
    for y in range(SALA_H, cv.h):
        for x in range(cv.w):
            cv.P[x, y] = (0, 0, 0, 255)


# ═══════════════════════════════════════════════════════════════════════════
#  Animacions
# ═══════════════════════════════════════════════════════════════════════════

def fulles_frames(oy=-DY, n=24, seed=3, leaves=7, ramp=LEAF, area=(40, 460, 20, 250), nit_=False):
    """Fulles de tardor que cauen de la capçada, gronxant-se (cada una amb la seva fase: el bucle no es nota)."""
    rnd = random.Random(seed)
    specs = [(rnd.uniform(area[0], area[1]), rnd.random(), rnd.uniform(0.6, 1.4), rnd.uniform(14, 30))
             for _ in range(leaves)]
    frames = []
    for i in range(n):
        cv = Llenc(oy, None, transparent=True)
        for x0, ph, sp, sw in specs:
            t = (i / n + ph) % 1.0
            y = area[2] + t * (area[3] - area[2])
            x = x0 + math.sin(t * math.pi * 4 * sp) * sw
            flip = math.cos(t * math.pi * 4 * sp)
            c = 2.5 + flip * 1.5
            cv.put(x, y, ramp, c, lit=0)
            cv.put(x + 1, y, ramp, c - 0.6, lit=0)
            if abs(flip) > 0.4:
                cv.put(x, y + 1, ramp, c - 1, lit=0)
                cv.put(x + 1, y - 1, ramp, c + 0.4, lit=0)
        frames.append(nit(cv.img) if nit_ else cv.img)
    return frames


def espores_frames(oy=-DY, n=24, seed=7, count=18, area=(20, 620, 120, 280), k=1.0):
    """Espores (o cuques de llum) turquesa que pugen a poc a poc i parpellegen."""
    rnd = random.Random(seed)
    specs = [(rnd.uniform(area[0], area[1]), rnd.uniform(area[2], area[3]), rnd.random(), rnd.uniform(6, 22),
              rnd.uniform(0.5, 1.5)) for _ in range(count)]
    frames = []
    for i in range(n):
        cv = Llenc(oy, None, transparent=True)
        a = np.zeros((cv.h, cv.w, 4), np.float32)
        for x0, y0, ph, rise, sp in specs:
            t = (i / n + ph) % 1.0
            x = x0 + math.sin(t * math.pi * 2 * sp + ph * 6) * 4
            y = y0 - t * rise + oy
            br = math.sin(t * math.pi) ** 1.5 * k
            if br < 0.08:
                continue
            X, Y = int(x), int(y)
            for dy in range(-3, 4):
                for dx in range(-3, 4):
                    if 0 <= X + dx < cv.w and 0 <= Y + dy < cv.h:
                        d = math.hypot(dx, dy)
                        al = br * (1.0 if d < 0.5 else max(0.0, 0.5 - d / 7))
                        if al > a[Y + dy, X + dx, 3] / 255:
                            col = (230, 255, 250) if d < 0.5 else GLOW_T
                            a[Y + dy, X + dx] = (*col, al * 255)
        frames.append(Image.fromarray(a.astype(np.uint8), 'RGBA'))
    return frames
