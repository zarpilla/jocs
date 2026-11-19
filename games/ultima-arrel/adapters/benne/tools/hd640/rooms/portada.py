"""
L'Última Arrel — la portada (pantalla sencera de 640×360, sense HUD). El roure de la porta petita al capvespre
(vora_comu.py, mode 'portada': la vora del bosc sense la tanca), i a sota, un tall del terra, com en un diorama: les
arrels del roure que s'enfonsen, les d'altres arbres que hi arriben pels costats, i els fils turquesa de la Xarxa
Miceli que les lliguen, amb la centraleta del Miceli (una cova petita de llum càlida, amb l'escala de mà que puja a la
porta) sota el tronc.

  - El títol és la capa `titol` (ANIMS, quieta, per sobre de tot), a dalt, damunt de la capçada: lletres de fusta
    daurada amb arrels que en pengen, i les puntes turquesa.
  - Els botons de la GUI `portada` van a 220..420 × 224..328: allà hi ha el terra fosc del tall (els fils, prims).
  - ANIMS `pols`: polsos de llum que corren pels fils de sota terra.

També en surt la imatge per compartir el joc: `python3 hd640/rooms/portada.py` (des de adapters/benne/tools)
→ ultima-arrel/public/portada.png (1440×810, el fons i el títol).
"""
import functools
import math
import random
import sys
from pathlib import Path

import numpy as np
from PIL import Image

if __name__ == '__main__':
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import hd640  # noqa: F401,E402
from hd640.rooms.vora_comu import (Mode, Llenc, llum, cel, bosc_fons, terra, roure, porta, xarxa, arrel, filament,  # noqa: E402
                                   _halo, fbm, hr, EARTH, STONE, BARK, TURQ, GLOW_T, WARM, PLANK, GRASS, LEAF, MOSS,
                                   DOOR, TC, W)

OY = -40                       # el món 40..400: el roure a dalt, i a sota (des de y = 214) el tall del terra
CUT = 254                      # la y del món on comença el tall
M = Mode('portada')
LIGHT = llum(M)
CAVA = (178, 306, 30, 16)      # la centraleta: centre, mig ample, mig alt (al món)

# Els fils principals de la xarxa sota terra (beziers quadràtiques, al món): van d'arrel a arrel.
FILS = [((20, 300), (120, 360), (178, 318)), ((178, 318), (260, 380), (360, 340)), ((360, 340), (470, 300), (560, 330)),
        ((560, 330), (610, 360), (650, 320)), ((90, 280), (150, 290), (160, 300)), ((214, 290), (300, 300), (420, 290)),
        ((420, 290), (500, 270), (600, 290)), ((40, 370), (200, 400), (330, 380)), ((330, 380), (460, 410), (630, 380))]


def _bez(p, t):
    (x0, y0), (x1, y1), (x2, y2) = p
    a, b, c = (1 - t) ** 2, 2 * (1 - t) * t, t * t
    return a * x0 + b * x1 + c * x2, a * y0 + b * y1 + c * y2


def tall(cv):
    """El tall del terra: capes de terra, pedres, les arrels i els fils de la xarxa, i la centraleta."""
    # la terra, en capes (més fosca com més avall)
    for y in range(CUT, cv.bot + 1):
        d = (y - CUT) / (cv.bot - CUT)
        for x in range(W):
            band = math.sin(y / 7 + fbm(x / 60, y / 30, 5) * 5) * 0.4
            lvl = 2.6 - d * 1.8 + band + (fbm(x / 9, y / 5, 8) - 0.5) * 1.2
            cv.put(x, y, EARTH, lvl, lit=0)
    # pedres i còdols
    rnd = random.Random(4)
    for _ in range(46):
        x, y, r = rnd.uniform(0, W), rnd.uniform(CUT + 8, cv.bot), rnd.uniform(2, 7)
        cv.disc(x, y, r, r * 0.7, STONE, lambda nx, ny: 2.4 - ny * 1.0 - nx * 0.4 - (y - CUT) / 120, lit=0)
    # la vora de dalt del tall: la capa d'humus, amb fulles i arrels petites que en pengen
    for x in range(W):
        top = CUT + math.sin(x / 13) * 1.2 + (fbm(x / 7, 3, 2) - 0.5) * 3
        for y in range(int(top) - 1, int(top) + 5):
            cv.put(x, y, EARTH, 1.6 + (y - top) * -0.1, lit=0)
        cv.put(x, top - 2, LEAF if hr(x, 1, 3) > 0.7 else GRASS, 2.6 + hr(x, 2, 3) * 2, lit=0.6)
        if hr(x, 5, 9) > 0.93:
            for j in range(int(3 + hr(x, 6, 9) * 9)):
                cv.put(x + math.sin(j / 3) * 0.8, top + 5 + j, BARK, 2.6 - j * 0.1, lit=0)
    # les arrels del roure, que s'enfonsen i s'obren
    for (p1, p2, r0, s) in (((150, 300), (60, 340), 12, 1), ((190, 320), (150, 400), 11, 2),
                            ((250, 320), (280, 410), 10, 3), ((290, 300), (400, 330), 11, 4),
                            ((120, 280), (10, 300), 8, 5), ((330, 280), (480, 300), 7, 6)):
        arrel(cv, (TC + (p2[0] - TC) * 0.2, CUT - 6), p1, p2, r0, 1.5, base=2.6, seed=s + 60, moss=False)
    # les d'altres arbres, que hi arriben pels costats
    for (p0, p1, p2, r0, s) in (((640, CUT), (590, 300), (520, 330), 8, 7), ((600, CUT), (620, 330), (600, 400), 7, 8),
                                ((-10, CUT + 20), (30, 330), (10, 400), 6, 9), ((470, CUT), (460, 290), (430, 300), 5, 10)):
        arrel(cv, p0, p1, p2, r0, 1.2, base=2.4, seed=s + 70, moss=False)
    # la centraleta: una cova petita, amb llum càlida, i l'escala de mà que puja a la porta
    cx, cy, rx, ry = CAVA
    for y in range(int(cy - ry), int(cy + ry) + 1):
        for x in range(int(cx - rx), int(cx + rx) + 1):
            nx, ny = (x - cx) / rx, (y - cy) / ry
            dd = nx * nx + ny * ny + (fbm(x / 5, y / 5, 31) - 0.5) * 0.25
            if dd <= 1:
                cv.put(x, y, WARM, 2.6 - dd * 1.6 + ny * 0.6, lit=0)
    cv.rect(cx - rx + 4, cy + ry - 4, cx + rx - 4, cy + ry - 2, PLANK, 1.6, lit=0)     # el terra de taulons
    tx = cx + 8                                                                       # el tauler, amb les rodes
    cv.rect(tx - 9, cy - 8, tx + 9, cy + 9, PLANK, lambda x, y: 1.8 - (y - cy) * 0.02, lit=0)
    for k, (wx, wy) in enumerate(((tx - 4, cy - 2), (tx + 4, cy - 2), (tx, cy + 4))):
        cv.ring(wx, wy, 2.4, BARK, 3.4, lit=0)
        cv.flat(wx, wy, (130, 230, 210) if k != 1 else (250, 220, 150))
    door_x = DOOR[0]
    y0, y1 = CUT + 6, int(cy + ry - 2)
    for i in range(y0, y1):                                                           # el pou i l'escala de mà
        t = (i - y0) / (y1 - y0)
        x = door_x - 4 - t * 30
        for k in range(-7, 8):
            if abs(k) < 6 or t > 0.5:
                cv.put(x + k, i, WARM, 0.8 + t * 1.0 - abs(k) * 0.05, lit=0)
        cv.put(x - 4, i, PLANK, 3.0, lit=0)
        cv.put(x + 4, i, PLANK, 3.0, lit=0)
        if i % 5 == 0:
            for k in range(-4, 5):
                cv.put(x + k, i, PLANK, 2.6, lit=0)
    _halo(cv, cx, cy, 70, (255, 160, 70), 0.35)
    # els fils de la xarxa: brillants, i amb nusos
    for k, p in enumerate(FILS):
        n = 160
        for i in range(n + 1):
            x, y = _bez(p, i / n)
            cv.put(x, y, TURQ, 5.2 - (0.8 if i % 7 == 0 else 0), lit=0)
            cv.put(x, y + 1, TURQ, 3.0, lit=0)
        cv.glow(*_bez(p, 0.5), 30, GLOW_T, 0.25)
        for t in (0.0, 1.0):
            x, y = _bez(p, t)
            cv.disc(x, y, 2.2, 2.2, TURQ, 6.6, lit=0)
            cv.glow(x, y, 12, GLOW_T, 0.6)
    rnd = random.Random(12)
    for k in range(26):                                                               # i els fils petits
        x, y = rnd.uniform(0, W), rnd.uniform(CUT + 10, cv.bot - 10)
        filament(cv, x, y, rnd.uniform(0, 2 * math.pi), rnd.uniform(30, 70), 100 + k, glow=0.8, branch=1, k=3.6,
                 sy=0.8)
    # la vora de dalt del tall, una mica de llum (la llum de l'aire, que no hi entra)
    cv.darken(0, CUT + 6, W - 1, cv.bot, lambda x, y: max(0.0, min(0.5, (y - CUT - 60) / 200)))


def tanca_lluny(cv):
    """A l'horitzó de la dreta, petita: la tanca nova de NaturaPlus, amb el cartell verd que s'encén (l'amenaça)."""
    from hd640.rooms.vora_comu import STEEL, NEON, SIGNK, text
    for x in range(452, W):
        base = 184 + (x - 452) * 0.05
        for y in range(int(base - 16), int(base)):
            if (x + y) % 4 == 0 or (x - y) % 4 == 0:
                cv.put(x, y, STEEL, 2.6, lit=0.2)
        cv.put(x, base - 16, STEEL, 3.4, lit=0.2)
        if (x - 452) % 22 == 0:
            for y in range(int(base - 18), int(base) + 1):
                cv.put(x, y, STEEL, 3.6, lit=0.2)
    sx, sy = 560, 150
    for x in (sx + 4, sx + 36):
        cv.rect(x, sy + 14, x, 172, STEEL, 3.0, lit=0)
    cv.rect(sx - 1, sy - 1, sx + 41, sy + 15, STEEL, 4.0, lit=0)
    cv.rect(sx, sy, sx + 40, sy + 14, SIGNK, 1.6, lit=0)
    text(cv, 'BOSC 2.0', sx + 5, sy + 5, (170, 255, 120))
    cv.glow(sx + 20, sy + 7, 34, (150, 255, 120), 0.3)


def mates(cv):
    """Mates de tardor al pla mitjà, a contrallum del sol (més petites i més color d'aire com més lluny)."""
    from hd640.rooms.vora_comu import LEAVES
    for i, (x, y, r) in enumerate(((36, 222, 16), (346, 232, 12), (430, 210, 9), (530, 236, 18), (610, 218, 13),
                                   (470, 192, 7), (590, 190, 6), (96, 196, 8))):
        rnd = random.Random(i)
        for k in range(14):
            a = rnd.uniform(math.pi, 2 * math.pi)
            rr = rnd.uniform(0, r * 0.8)
            bx, by = x + math.cos(a) * rr, y + math.sin(a) * rr * 0.7
            br = r * rnd.uniform(0.35, 0.55)
            cv.disc(bx, by, br, br * 0.85, LEAVES, lambda nx, ny, i=i, k=k: 3.4 - ny * 1.4 - nx * 0.8 +
                    (fbm(nx * 3 + k, ny * 3, i) - 0.5) * 1.6 - (y - 230) * -0.01, lit=0.8)
        cv.darken(x - r - 2, y - 1, x + r + 2, y + 2, 0.7)


@functools.lru_cache(maxsize=None)
def _fons():
    cv = Llenc(OY, LIGHT)
    cel(cv, M)
    bosc_fons(cv, M)
    tanca_lluny(cv)
    terra(cv, M)
    mates(cv)
    roure(cv, M)
    porta(cv, M)
    xarxa(cv, M)
    tall(cv)
    return cv.img


def bg(cv):
    cv.img.paste(_fons())
    cv.P = cv.img.load()


PROPS = {}

# ─── El títol ──────────────────────────────────────────────────────────────
LLETRES = {
    'L': ['10000', '10000', '10000', '10000', '10000', '10000', '11111'],
    "'": ['1', '1', '1', '0', '0', '0', '0'],
    'U': ['10001', '10001', '10001', '10001', '10001', '10001', '01110'],
    'T': ['11111', '00100', '00100', '00100', '00100', '00100', '00100'],
    'I': ['111', '010', '010', '010', '010', '010', '111'],
    'M': ['10001', '11011', '10101', '10101', '10001', '10001', '10001'],
    'A': ['01110', '10001', '10001', '11111', '10001', '10001', '10001'],
    'R': ['11110', '10001', '10001', '11110', '10100', '10010', '10001'],
    'E': ['11111', '10000', '10000', '11110', '10000', '10000', '11111'],
    ' ': ['00', '00', '00', '00', '00', '00', '00'],
}
S = 6                          # px per punt de lletra
TITLE_Y = 26                   # (de pantalla)
GOLD = [(30, 14, 8), (62, 32, 12), (104, 60, 22), (150, 94, 34), (196, 134, 52), (230, 174, 80), (248, 212, 128),
        (254, 238, 190)]


def _cells(word='L\'ULTIMA ARREL'):
    cols = [len(LLETRES[ch][0]) for ch in word]
    kern = [-1 if a == 'L' and b in 'T' else 0 for a, b in zip(word, word[1:] + ' ')]   # (la L i la T s'encaixen)
    width = sum(c + 1 + k for c, k in zip(cols, kern)) * S - S
    x0 = (W - width) // 2
    cells, acc, col = [], [], 0
    for ch, c, kk in zip(word, cols, kern):
        for r, bits in enumerate(LLETRES[ch]):
            for i, bit in enumerate(bits):
                if bit == '1':
                    cells.append((x0 + (col + i) * S, TITLE_Y + r * S))
        if ch == 'U' and not acc:                                                   # l'accent de la Ú
            acc.append((x0 + (col + 2) * S, x0 + (col + 3) * S))
        col += c + 1 + kk
    return cells, acc


def titol(cv):
    """«L'ÚLTIMA ARREL»: lletres de fusta daurada, amb vora fosca i ombra; de les de baix en pengen arrels amb la
    punta turquesa."""
    cells, acc = _cells()
    filled = set(cells)
    # l'accent: dues cel·les en diagonal, a sobre de la U
    (ax0, ax1), = acc
    extra = [(ax1, TITLE_Y - 2 * S), (ax0 + S // 2, TITLE_Y - S - 1)]
    allc = cells + extra
    for x, y in allc:
        cv.rect(x + 3, y + 4, x + S + 2, y + S + 3, [(6, 4, 10)], 0, lit=0)          # l'ombra
    for x, y in allc:
        cv.rect(x - 1, y - 1, x + S, y + S, [(20, 10, 8)], 0, lit=0)                  # la vora
    for x, y in allc:
        top_open = (x, y - S) not in filled
        right_open = (x + S, y) not in filled
        left_open = (x - S, y) not in filled
        for py in range(y, y + S):
            for px in range(x, x + S):
                t = (py - TITLE_Y) / (7 * S)
                lvl = 6.0 - t * 3.4
                lvl += math.sin(py / 2.2 + math.sin(px / 9) * 2) * 0.35                # la veta de la fusta
                if py == y and top_open:
                    lvl += 1.2
                if px == x and left_open:
                    lvl += 0.5
                if px == x + S - 1 and right_open:
                    lvl -= 1.0
                cv.put(px, py, GOLD, lvl, lit=0)
    # arrels que pengen de les lletres (a les cel·les de baix de tot)
    bottoms = {}
    for x, y in cells:
        bottoms[x] = max(bottoms.get(x, 0), y)
    for k, (x, y) in enumerate(sorted(bottoms.items())):
        if hr(k, 3, 17) < 0.45:
            continue
        px, py = x + S // 2 + int(hr(k, 4, 17) * 3) - 1, y + S
        n = 6 + int(hr(k, 5, 17) * 16)
        for j in range(n):
            px += math.sin(j / 3 + k) * 0.6
            cv.put(px, py + j, GOLD, 2.6 - j * 0.08, lit=0)
            if j < n * 0.4:
                cv.put(px + 1, py + j, GOLD, 1.6, lit=0)
        cv.flat(px, py + n, (220, 255, 248))
        cv.glow(px, py + n, 6, GLOW_T, 0.8)
    cv.glow(W // 2, TITLE_Y + 3 * S, 260, (255, 200, 120), 0.04)


def _titol_frames():
    cv = Llenc(0, None, transparent=True)
    titol(cv)
    return [cv.img]


# ─── Els polsos de llum pels fils ──────────────────────────────────────────

def _pols_frames(n=20):
    frames = []
    for i in range(n):
        a = np.zeros((360, W, 4), np.float32)
        for k, p in enumerate(FILS):
            t = (i / n + k * 0.37) % 1.0
            for back in range(14):
                tt = t - back * 0.008
                if tt < 0:
                    continue
                x, y = _bez(p, tt)
                X, Y = int(x), int(y) + OY
                al = (1 - back / 14) ** 1.5
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        if 0 <= X + dx < W and 0 <= Y + dy < 360:
                            v = al * (1.0 if dx == dy == 0 else 0.35)
                            if v > a[Y + dy, X + dx, 3] / 255:
                                a[Y + dy, X + dx] = (230, 255, 250, v * 255)
        frames.append(Image.fromarray(a.astype(np.uint8), 'RGBA'))
    return frames


ANIMS = {
    'pols': {'frames': _pols_frames, 'frameDuration': 110},
    'titol': {'frames': _titol_frames, 'frameDuration': 1000, 'loop': False, 'zIndex': 3},
}

GEOMETRIA = {'things': {}, 'spawns': {}}


def publica():
    """La imatge per compartir (Open Graph): el fons i el títol, a 1440×810 (com la de Ni un ou)."""
    from pixels import nearest
    img = _fons().copy()
    img.alpha_composite(_titol_frames()[0])
    out = Path(__file__).resolve().parents[5] / 'ultima-arrel' / 'public' / 'portada.png'
    out.parent.mkdir(parents=True, exist_ok=True)
    nearest(img.convert('RGB'), (1440, 810)).save(out)
    print(out)


if __name__ == '__main__':
    publica()
