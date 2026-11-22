"""
La Conjura de l'Avet — el que comparteixen les dues sales de fora de l'acte I: la plaça de Sant Pol
(`placa_sant_pol.py`) i el Pont Vell (`pont_ter.py`). Rampes de la paleta del joc (el gres rosat del pont, la pedra
grisa i daurada de Sant Pol, la teula, la fusta fosca, la gespa, el vermell de la cera), el soroll, el cel (de
després de la pluja i del matí net), i les textures de pedra en coordenades del món o en dibuixos plans.

Tot es dibuixa a 1× (640×360; l'escena fins a y = 260).
"""
import math
import random

import numpy as np
from PIL import Image

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from hd.pix import B4, hr, mix  # noqa: F401
from hd.rooms.comu import _diff  # noqa: F401

BOTTOM = 259                                       # l'escena acaba aquí (a sota, la barra de verbs)

# ─── Rampes (fosc → clar) ───────────────────────────────────────────────────
PEDRA = [(30, 27, 26), (48, 44, 40), (68, 62, 54), (90, 82, 70), (114, 104, 86), (140, 128, 104), (166, 152, 122),
         (192, 176, 140), (216, 200, 160), (236, 222, 186)]                  # Sant Pol: grisa i daurada
GRES = [(36, 22, 24), (58, 36, 36), (82, 52, 48), (108, 70, 60), (134, 90, 74), (160, 112, 90), (186, 136, 108),
        (208, 160, 128), (228, 188, 154), (242, 212, 182)]                   # el Pont Vell: gres rosat i ocre
TOSCA = [(24, 22, 22), (40, 38, 36), (58, 54, 50), (78, 74, 66), (100, 94, 84), (124, 116, 102), (148, 140, 122),
         (174, 166, 146), (200, 192, 170)]                                    # paredat gris (murets, marges)
TEULA = [(44, 18, 14), (74, 32, 22), (108, 48, 30), (142, 66, 40), (172, 88, 54), (200, 114, 74), (222, 146, 104),
         (238, 178, 136)]
FUSTA = [(14, 9, 8), (28, 17, 12), (44, 27, 18), (62, 39, 24), (84, 54, 32), (108, 72, 42), (134, 94, 56),
         (160, 118, 74)]
FERRO = [(8, 8, 10), (18, 18, 22), (32, 32, 36), (50, 50, 54), (74, 72, 74), (104, 100, 98), (140, 136, 130)]
GESPA = [(10, 20, 10), (16, 32, 12), (24, 46, 16), (34, 62, 20), (46, 80, 26), (62, 100, 32), (82, 122, 40),
         (106, 146, 54), (136, 170, 76), (170, 196, 104)]
TERRA = [(18, 15, 14), (30, 26, 23), (44, 38, 32), (60, 52, 43), (78, 68, 55), (98, 86, 69), (120, 106, 85),
         (144, 128, 104), (170, 152, 126)]                                    # terra molla de la plaça
HORT = [(20, 14, 10), (34, 24, 16), (50, 36, 24), (68, 50, 32), (88, 66, 42), (110, 84, 54), (134, 104, 68),
        (158, 126, 86)]                                                       # la terra treballada dels horts
CEL = [(64, 92, 136), (80, 110, 154), (98, 130, 172), (120, 152, 190), (146, 176, 206), (174, 198, 220),
       (204, 220, 232), (230, 238, 242)]
NUVOL = [(70, 76, 92), (90, 96, 110), (112, 118, 130), (136, 140, 150), (162, 166, 172), (190, 192, 194),
         (216, 216, 214), (238, 236, 230)]
CEL_MATI = [(96, 136, 186), (116, 156, 204), (138, 176, 220), (162, 196, 232), (188, 214, 240), (214, 230, 244),
            (236, 240, 240), (252, 246, 230)]
LLUNY = [(70, 86, 98), (86, 102, 112), (104, 120, 126), (124, 138, 140), (146, 156, 156), (170, 178, 174)]
PAPER = [(70, 58, 42), (110, 94, 70), (152, 134, 102), (190, 172, 136), (220, 206, 170), (240, 230, 200)]
CERA = [(50, 6, 8), (96, 12, 14), (148, 22, 20), (196, 36, 28), (232, 64, 44), (252, 118, 90)]
AIGUA = [(12, 26, 24), (18, 38, 34), (26, 54, 46), (36, 70, 58), (48, 88, 70), (64, 108, 84), (84, 128, 100),
         (110, 150, 120), (144, 176, 148), (184, 206, 182), (222, 232, 214)]
ESCUMA = [(110, 136, 120), (140, 164, 148), (172, 192, 176), (204, 218, 204), (228, 236, 226), (246, 250, 244)]
FULLA = [(8, 16, 10), (14, 28, 14), (22, 42, 18), (32, 58, 24), (46, 76, 30), (64, 96, 38), (88, 118, 48),
         (116, 142, 62)]                                                      # les capçades
SALZE = [(14, 20, 8), (24, 34, 12), (38, 52, 16), (56, 74, 22), (80, 100, 30), (110, 128, 40), (144, 160, 58),
         (180, 192, 84), (210, 220, 120)]                                     # el verd groc del salze
ESCORÇA = [(14, 11, 10), (26, 20, 16), (40, 31, 24), (56, 44, 34), (74, 60, 46), (94, 78, 60)]
CANEM = [(46, 36, 22), (78, 64, 40), (116, 98, 64), (156, 136, 94), (190, 172, 126)]
BRONZE = [(24, 18, 10), (48, 36, 18), (78, 58, 28), (112, 86, 40), (148, 118, 58), (186, 156, 88), (220, 196, 132)]
PELL = [(64, 38, 30), (104, 66, 50), (146, 100, 74), (184, 136, 102), (214, 172, 136)]
LLANA = [(48, 40, 34), (80, 70, 58), (118, 106, 88), (160, 148, 124), (200, 190, 164), (228, 220, 198)]
ROBA_BLAVA = [(20, 24, 36), (34, 42, 60), (52, 62, 84), (74, 86, 108), (100, 112, 132)]
ROBA_OCRE = [(40, 28, 14), (70, 50, 24), (104, 76, 36), (140, 106, 54), (176, 140, 78)]
ROBA_VERDA = [(18, 26, 16), (30, 42, 24), (46, 60, 34), (64, 80, 46), (86, 102, 62)]


# ─── Soroll ─────────────────────────────────────────────────────────────────

def _s(t):
    return t * t * (3 - 2 * t)


_RT = np.random.default_rng(7).random(256 * 256).astype(np.float32)


def vn(u, v, seed=0):
    """Soroll de valors suau (0..1)."""
    x0, y0 = math.floor(u), math.floor(v)
    fx, fy = _s(u - x0), _s(v - y0)

    def h(i, j):
        return float(_RT[((i * 73856093) ^ (j * 19349663) ^ (seed * 83492791)) & 0xFFFF])
    a, b, c, d = h(x0, y0), h(x0 + 1, y0), h(x0, y0 + 1), h(x0 + 1, y0 + 1)
    return a + (b - a) * fx + (c - a) * fy + (a - b - c + d) * fx * fy


def fbm(u, v, seed=0, octaves=3):
    s, amp, tot = 0.0, 1.0, 0.0
    for o in range(octaves):
        s += vn(u * 2 ** o, v * 2 ** o, seed + o * 17) * amp
        tot += amp
        amp *= 0.5
    return s / tot


def fbm_np(w, h, escala, seed=0, octaves=4):
    """Soroll fbm en una graella (h, w) amb numpy: per a superfícies grans (el terra, el riu)."""
    rng = np.random.default_rng(seed)
    out = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        cel = max(1.0, escala / 2 ** o)
        gw, gh = int(w / cel) + 3, int(h / cel) + 3
        g = rng.random((gh, gw)).astype(np.float32)
        ys = np.arange(h, dtype=np.float32) / cel
        xs = np.arange(w, dtype=np.float32) / cel
        y0, x0 = ys.astype(int), xs.astype(int)
        fy, fx = _s(ys - y0)[:, None], _s(xs - x0)[None, :]
        a = g[y0][:, x0]
        b = g[y0][:, x0 + 1]
        c = g[y0 + 1][:, x0]
        d = g[y0 + 1][:, x0 + 1]
        out += (a + (b - a) * fx + (c - a) * fy + (a - b - c + d) * fx * fy) * amp
        tot += amp
        amp *= 0.5
    return out / tot


# ─── Dibuix pla: pedra ──────────────────────────────────────────────────────

def carreus(cv, x0, y0, x1, y1, rmp, lvl, fila=(12, 16), ample=(18, 34), junta=1.6, seed=1, lit=0, cantoneres=None,
            relleu=0.7):
    """Un parament de carreus (pedra tallada en filades) en un dibuix pla: cada pedra, el seu to; la junta, fosca; la
    vora de dalt i l'esquerra, una mica més clara (la llum ve de dalt). `cantoneres`: (x, ample) d'una cantonada amb
    pedres alternes més llargues."""
    rnd = random.Random(seed)
    y = y0
    fila_i = 0
    while y <= y1:
        h = rnd.randint(*fila)
        x = x0 - rnd.randint(0, ample[1])
        while x <= x1:
            w = rnd.randint(*ample)
            if cantoneres is not None:
                cx, cw = cantoneres
                if x < cx + cw and x + w > cx:
                    w = cw + (10 if fila_i % 2 else -4)
                    x = cx - (0 if fila_i % 2 else 0)
            tone = lvl + (rnd.random() - 0.5) * 1.3
            sx = rnd.random() * 9
            for yy in range(max(y0, int(y)), min(y1, int(y + h - 1)) + 1):
                for xx in range(max(x0, int(x)), min(x1, int(x + w - 1)) + 1):
                    v = tone + (fbm(xx * 0.18 + sx, yy * 0.18, seed) - 0.5) * 1.1
                    if yy == int(y) or xx == int(x):
                        v += relleu
                    elif yy == int(y + h - 2) or xx == int(x + w - 2):
                        v -= relleu * 0.8
                    if hr(xx, yy, seed) < 0.05:
                        v -= 0.9
                    cv.put(xx, yy, rmp, v, lit)
            for xx in range(max(x0, int(x)), min(x1, int(x + w - 1)) + 1):
                cv.put(xx, int(y + h - 1), rmp, lvl - junta, lit)
            for yy in range(max(y0, int(y)), min(y1, int(y + h - 1)) + 1):
                cv.put(int(x + w - 1), yy, rmp, lvl - junta, lit)
            x += w
        y += h
        fila_i += 1


def paredat(cv, x0, y0, x1, y1, rmp, lvl, mida=(5, 9), seed=2, lit=0):
    """Paredat (pedra sense tallar, petita i irregular) en un dibuix pla."""
    rnd = random.Random(seed)
    cv.rect(x0, y0, x1, y1, rmp, lvl - 1.8, lit)
    y = y0
    while y <= y1:
        h = rnd.randint(*mida)
        x = x0 - rnd.randint(0, 6)
        while x <= x1:
            w = rnd.randint(mida[0] + 1, mida[1] + 5)
            tone = lvl + (rnd.random() - 0.5) * 1.6
            cx, cy, rx, ry = x + w / 2, y + h / 2, w / 2 - 0.6, h / 2 - 0.6
            for yy in range(int(y), int(y + h)):
                for xx in range(int(x), int(x + w)):
                    if not (x0 <= xx <= x1 and y0 <= yy <= y1):
                        continue
                    nx, ny = (xx + 0.5 - cx) / rx, (yy + 0.5 - cy) / ry
                    d = nx ** 4 + ny ** 4
                    if d > 1:
                        continue
                    cv.put(xx, yy, rmp, tone - ny * 0.7 - (0.6 if d > 0.55 and ny > 0 else 0), lit)
            x += w
        y += h - 1


# ─── Superfícies procedurals (en coordenades del món) ───────────────────────

def lvl_carreus(base, fila=16, ample=30, junta=1.7, seed=3, gra=0.9):
    """lvl(s, t, P) d'un parament de carreus sobre un quad (s cap a la dreta, t cap avall, en unitats del món)."""
    def L(s, t, P):
        r = int(t // fila)
        off = (hr(r, seed) * ample)
        c = int((s + off) // ample)
        a, b = (s + off) - c * ample, t - r * fila
        v = base + (hr(r, c, seed) - 0.5) * 1.2 + (vn(s * 0.2, t * 0.2, seed) - 0.5) * gra
        if a < 1.3 or b < 1.3:
            return v - junta
        if b < 3:
            v += 0.4
        return v
    return L


def lvl_paredat(base, mida=9, seed=4):
    def L(s, t, P):
        r = int(t // (mida * 0.7))
        off = hr(r, seed) * mida
        c = int((s + off) // mida)
        a, b = (s + off) - c * mida, t - r * mida * 0.7
        v = base + (hr(r, c, seed) - 0.5) * 1.6
        if a < 1.4 or b < 1.2:
            return v - 1.8
        return v + (0.4 if b < 2.4 else 0)
    return L


# ─── Cel ─────────────────────────────────────────────────────────────────────

def cel_trencat(cv, x0, x1, y0, y1, hor, seed=5, mati=False, sol=None):
    """El cel de després de la pluja: blau net entre núvols trencats que s'empetiteixen cap a l'horitzó (o, amb `mati`,
    el cel net del matí, quatre núvols prims). `sol`: (x, y) on el sol il·lumina la vora dels núvols."""
    rmp = CEL_MATI if mati else CEL
    for y in range(y0, y1 + 1):
        t = (y - y0) / max(1, hor - y0)
        for x in range(x0, x1 + 1):
            base = (2.2 + t * 4.4) if not mati else (2.6 + t * 4.6)
            # els núvols: soroll aixafat en vertical, més petits a prop de l'horitzó
            k = 1.0 + t * 2.2
            n = fbm(x * 0.012 * k, y * 0.034 * k, seed, 4)
            llindar = 0.56 if not mati else 0.7
            if n > llindar:
                a = (n - llindar) / (1 - llindar)
                dens = min(1.0, a * 3.2)
                v = 6.6 - (fbm(x * 0.03 * k, y * 0.05 * k, seed + 9, 3) - 0.4) * 5.0 * dens
                v -= dens * (1 - t) * 1.0
                if sol is not None:
                    v += max(0.0, 1 - math.hypot(x - sol[0], (y - sol[1]) * 1.6) / 380) * 1.6
                if mati:
                    v += 0.6
                if dens < 0.35 and B4[y & 3][x & 3] > dens / 0.35:
                    cv.put(x, y, rmp, base, lit=0)
                else:
                    cv.put(x, y, NUVOL, v, lit=0)
            else:
                cv.put(x, y, rmp, base, lit=0)


def silueta_muntanyes(cv, x0, x1, y_base, alt, rmp, lvl, seed=8, rug=0.012, y1=None):
    """Una carena llunyana (blava per l'aire), de y_base − alt·soroll fins a y1."""
    y1 = y1 if y1 is not None else y_base + 40
    for x in range(x0, x1 + 1):
        top = y_base - alt * fbm(x * rug, 0.5, seed, 4)
        for y in range(int(top), y1 + 1):
            cv.put(x, y, rmp, lvl - (y - top) * 0.02 + (fbm(x * 0.05, y * 0.05, seed + 3) - 0.5) * 0.8, lit=0)


# ─── Capçades i figures ─────────────────────────────────────────────────────

def capcada(cv, cx, cy, rx, ry, rmp, lvl, seed=1, llum=(0.6, -0.7), lit=0, forat=0.0):
    """Una capçada d'arbre (de fulla ampla): grumolls de fulles amb la llum d'un costat. En pantalla."""
    rnd = random.Random(seed)
    lx, ly = llum
    grums = [(cx + (rnd.random() - 0.5) * rx * 1.5, cy + (rnd.random() - 0.5) * ry * 1.3,
              rx * (0.32 + rnd.random() * 0.25), ry * (0.3 + rnd.random() * 0.25)) for _ in range(int(rx * ry / 90) + 6)]
    grums.sort(key=lambda g: g[1])
    for gx, gy, gr, gh in grums:
        for y in range(int(gy - gh - 1), int(gy + gh + 2)):
            for x in range(int(gx - gr - 1), int(gx + gr + 2)):
                nx, ny = (x - gx) / gr, (y - gy) / gh
                d = nx * nx + ny * ny
                vora = 1 + (fbm(x * 0.3, y * 0.3, seed) - 0.5) * 0.7
                if d > vora:
                    continue
                if forat and fbm(x * 0.16, y * 0.16, seed + 5) < forat:
                    continue
                v = lvl + (nx * lx + ny * ly) * 1.4 + (1 - d) * 0.5 + (fbm(x * 0.45, y * 0.45, seed + 2) - 0.5) * 1.6
                cv.put(x, y, rmp, v, lit)


# ─── Textures planes amb numpy (nivells → colors de la rampa, amb el tramat de Bayer) ───

_BAYER = np.array(B4, np.float32)


def tramat(lv, rmp, alpha=None):
    """Una graella de nivells (h, w) → imatge RGBA amb els colors de la rampa (tramat ordenat entre tons veïns).
    `alpha`: màscara booleana (fals = transparent)."""
    h, w = lv.shape
    b = np.tile(_BAYER, (h // 4 + 1, w // 4 + 1))[:h, :w]
    idx = np.clip(np.floor(lv + b - 0.5), 0, len(rmp) - 1).astype(int)
    pal = np.array(rmp, np.uint8)
    out = np.zeros((h, w, 4), np.uint8)
    out[..., :3] = pal[idx]
    out[..., 3] = 255 if alpha is None else np.where(alpha, 255, 0)
    return out


def enganxa(dst, src, mask=None):
    """Copia els píxels opacs de `src` (RGBA) damunt de `dst` (o només on `mask`)."""
    m = src[..., 3] > 0 if mask is None else (mask & (src[..., 3] > 0))
    dst[m] = src[m]


def nivells_carreus(w, h, base, fila=(12, 16), ample=(20, 36), junta=1.7, seed=1, relleu=0.6, gra=0.9, x_off=0):
    """→ (nivells (h, w), id de pedra (h, w)): un parament de carreus en filades, a 1 unitat = 1 px."""
    rnd = random.Random(seed)
    lv = np.zeros((h, w), np.float32)
    ids = np.zeros((h, w), np.int32)
    gr = fbm_np(w, h, 10, seed + 1, 3)
    n = 0
    y = 0
    while y < h:
        fh = rnd.randint(*fila)
        x = -rnd.randint(0, ample[1]) + x_off
        while x < w:
            bw = rnd.randint(*ample)
            n += 1
            x0, x1, y0, y1 = max(0, x), min(w, x + bw), y, min(h, y + fh)
            if x1 > x0:
                tone = base + (rnd.random() - 0.5) * 1.2
                lv[y0:y1, x0:x1] = tone
                ids[y0:y1, x0:x1] = n
                lv[y0:y0 + 1, x0:x1] += relleu
                lv[y0:y1, x0:x0 + 1] += relleu * 0.6
                lv[max(y0, y1 - 2):y1 - 1, x0:x1] -= relleu * 0.7
                lv[y1 - 1:y1, x0:x1] = base - junta
                if x + bw <= w:
                    lv[y0:y1, x1 - 1:x1] = base - junta
            x += bw
        y += fh
    lv += (gr - 0.5) * gra * 2
    speck = np.random.default_rng(seed + 7).random((h, w)) < 0.04
    lv[speck] -= 0.8
    return lv, ids


def nivells_paredat(w, h, base, mida=(5, 9), seed=2):
    """Paredat (pedres petites i irregulars, amb molt de morter)."""
    rnd = random.Random(seed)
    lv = np.full((h, w), base - 1.9, np.float32)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    y = -2
    while y < h:
        fh = rnd.randint(*mida)
        x = -rnd.randint(0, 6)
        while x < w:
            bw = rnd.randint(mida[0] + 2, mida[1] + 6)
            x0, x1, y0, y1 = max(0, x), min(w, x + bw), max(0, y), min(h, y + fh)
            if x1 > x0 and y1 > y0:
                cx, cy, rx, ry = x + bw / 2, y + fh / 2, bw / 2 - 0.5, fh / 2 - 0.5
                nx = (xx[y0:y1, x0:x1] + 0.5 - cx) / rx
                ny = (yy[y0:y1, x0:x1] + 0.5 - cy) / ry
                d = nx ** 4 + ny ** 4
                tone = base + (rnd.random() - 0.5) * 1.7
                sub = lv[y0:y1, x0:x1]
                m = d <= 1
                sub[m] = (tone - ny * 0.8 - np.where((d > 0.5) & (ny > 0), 0.6, 0))[m]
            x += bw
        y += fh - 1
    return lv
