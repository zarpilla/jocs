"""
La Conjura de l'Avet — peces comunes de les sales del claustre, la bugaderia i l'apotecaria (art definitiu, 1×).

Les rampes de la casa per al monestir (pedra de gres rosada i ocre, el blanc trencat del claustre, les columnes
fosques, la fusta fosca, la teula, la gespa), un soroll ràpid, la lletra petita, i les eines per fer decorats i capes
(el que canvia respecte del fons, la màscara d'una capa).
"""
import math
import random

import numpy as np
from PIL import Image

from hd.pix import B4
from hd.rooms.comu import _glyph

W, H = 640, 360
RH = 260                                          # l'escena es pinta fins aquí (a sota, el HUD)

# ─── Rampes (fosc → clar) ────────────────────────────────────────────────────
# El gres del país: rosat i ocre.
GRES = [(46, 30, 30), (72, 48, 42), (100, 68, 56), (128, 90, 70), (156, 114, 86), (182, 138, 104), (204, 164, 124),
        (224, 190, 150), (240, 214, 180)]
# El blanc trencat de les parets arrebossades del claustre.
BLANC = [(58, 52, 50), (88, 80, 74), (120, 110, 98), (152, 142, 126), (180, 170, 152), (204, 196, 178),
         (224, 218, 200), (240, 236, 222), (250, 248, 238)]
# Les columnes fosques (pedra negrosa, una mica verdosa).
COLUMNA = [(14, 14, 16), (24, 24, 26), (36, 36, 36), (50, 50, 48), (66, 66, 62), (86, 86, 80), (110, 108, 100)]
# Les lloses grises del terra de la galeria.
LLOSA = [(34, 32, 34), (52, 50, 50), (72, 70, 68), (94, 90, 86), (118, 112, 104), (142, 136, 124), (166, 160, 146),
         (192, 186, 170)]
# Fusta fosca (bigues, portes, taules).
FUSTA = [(14, 8, 6), (26, 16, 12), (40, 26, 18), (58, 38, 24), (78, 52, 32), (100, 68, 42), (124, 88, 54),
         (150, 110, 70), (178, 136, 90)]
# La teula.
TEULA = [(44, 22, 18), (70, 34, 24), (98, 48, 30), (126, 64, 38), (152, 82, 48), (176, 104, 62), (198, 130, 82)]
# La gespa mullada (verd fosc, acte 1) i la del matí.
GESPA = [(10, 22, 12), (16, 34, 16), (24, 48, 20), (34, 64, 24), (46, 82, 28), (62, 102, 34), (82, 122, 42),
         (108, 144, 56)]
# El cel blanc de després de la pluja.
CELB = [(150, 156, 164), (170, 176, 182), (190, 194, 198), (206, 210, 212), (222, 224, 224), (236, 236, 234)]
# El ferro (claus, frontisses, l'escalfador).
FERRO = [(10, 10, 12), (20, 20, 24), (34, 34, 38), (52, 52, 56), (74, 74, 78), (100, 100, 104), (132, 130, 132)]
# La cera vermella dels segells: l'únic vermell viu del joc.
CERA = [(70, 6, 10), (120, 10, 14), (170, 18, 20), (214, 30, 28), (240, 70, 56), (255, 140, 120)]
# Paper i pergamí.
PERGAMI = [(90, 74, 52), (130, 110, 80), (170, 148, 110), (204, 184, 140), (228, 212, 170), (244, 234, 200)]
# El foc i la llum de les espelmes.
FOC = [(70, 16, 8), (130, 36, 10), (190, 70, 16), (232, 116, 30), (250, 170, 60), (255, 220, 130), (255, 248, 210)]
# Teles de bugada (lli cru) i la roba negra.
LLI = [(60, 54, 46), (96, 88, 74), (132, 122, 102), (166, 156, 132), (196, 188, 162), (222, 216, 192),
       (240, 236, 218)]
NEGRE = [(8, 8, 12), (16, 16, 22), (26, 26, 32), (38, 38, 46), (54, 54, 62), (74, 74, 82)]
# Coure (la tina) i fang (gerres, pots).
COURE = [(40, 18, 12), (74, 34, 20), (112, 54, 30), (150, 78, 42), (186, 106, 58), (216, 140, 84), (240, 186, 130)]
FANG = [(42, 24, 16), (70, 40, 24), (100, 60, 34), (132, 82, 46), (162, 106, 62), (190, 134, 84), (214, 164, 112)]
# Vidre verd i ambre dels flascons.
VIDREV = [(10, 28, 20), (18, 48, 32), (30, 72, 46), (48, 100, 62), (80, 136, 86), (130, 180, 130), (200, 230, 200)]
VIDREA = [(40, 20, 8), (76, 40, 12), (116, 64, 18), (156, 94, 28), (196, 132, 46), (230, 176, 90), (250, 220, 160)]
# Herbes seques.
HERBA = [(28, 30, 14), (44, 48, 20), (62, 66, 28), (84, 86, 38), (108, 106, 52), (134, 128, 70), (160, 152, 92)]


# ─── Soroll ràpid (de valors, amb taula de permutació) ─────────────────────

_PERM = list(range(256))
random.Random(7).shuffle(_PERM)
_PERM += _PERM
_VAL = [random.Random(k * 31 + 5).random() for k in range(256)]


def _h(x, y, s):
    return _VAL[_PERM[(_PERM[(x + s * 57) & 255] + y) & 255]]


def nz(u, v, s=0):
    """Soroll de valors suau (0..1)."""
    x0, y0 = math.floor(u), math.floor(v)
    fx, fy = u - x0, v - y0
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a, b, c, d = _h(x0, y0, s), _h(x0 + 1, y0, s), _h(x0, y0 + 1, s), _h(x0 + 1, y0 + 1, s)
    return a + (b - a) * fx + (c - a) * fy + (a - b - c + d) * fx * fy


def fbm(u, v, s=0, oct=3):
    t, amp, tot = 0.0, 1.0, 0.0
    for o in range(oct):
        t += nz(u * 2 ** o, v * 2 ** o, s + o * 13) * amp
        tot += amp
        amp *= 0.5
    return t / tot


def hr(*a):
    """Soroll determinista (0..1) a partir d'enters."""
    return _VAL[_PERM[(_PERM[(_PERM[a[0] & 255] + (a[1] if len(a) > 1 else 0)) & 255] +
                       (a[2] if len(a) > 2 else 0)) & 255]]


def smooth(a, b, t):
    if a == b:
        return 1.0 if t >= b else 0.0
    if a > b:
        return 1.0 - smooth(b, a, t)
    if t <= a:
        return 0.0
    if t >= b:
        return 1.0
    x = (t - a) / (b - a)
    return x * x * (3 - 2 * x)


# ─── Lletra petita (la de la casa, a escala k) ─────────────────────────────

def lletres(cv, s, x, y, col, k=1, kx=None):
    """Escriu `s` amb la font de 3×5 de la casa, a escala k (kx: l'ample), amb el color pla `col`. → l'amplada."""
    kx = kx or k
    cx = x
    for ch in s:
        g, top = _glyph(ch)
        for j, row in enumerate(g, start=top):
            for i, bit in enumerate(row):
                if bit != '1':
                    continue
                for dy in range(k):
                    for dx in range(kx):
                        cv.flat(cx + i * kx + dx, y + j * k + dy, col)
        cx += (len(g[0]) + 1) * kx
    return cx - x - kx


def ample(s, k=1):
    return sum((len(_glyph(ch)[0][0]) + 1) * k for ch in s) - k


# ─── Capes ─────────────────────────────────────────────────────────────────

def diferencia(frame, base):
    """Només els píxels que canvien respecte del fons (la resta, transparent)."""
    a, b = np.asarray(frame.convert('RGBA')), np.asarray(base.convert('RGBA'))
    keep = (a != b).any(axis=2)
    return Image.fromarray(np.where(keep[..., None], a, 0).astype(np.uint8), 'RGBA')


def sense_hud(img):
    """Treu el que queda per sota de l'escena (la franja del HUD)."""
    a = np.asarray(img.convert('RGBA')).copy()
    a[RH:] = 0
    return Image.fromarray(a, 'RGBA')


def fosc_hud(img):
    a = np.asarray(img.convert('RGBA')).copy()
    a[RH:] = (0, 0, 0, 255)
    return Image.fromarray(a, 'RGBA')


def mascara_amo(e, ids):
    """→ fn(x, y): el píxel de sala l'ha pintat una de les superfícies `ids` de l'escena `e`."""
    ok = np.array([sid in ids for sid in e.ids], dtype=bool)
    m = ok[np.frombuffer(e.amo, dtype=np.uint16).reshape(e.cv.h, e.cv.w)]
    m[RH:] = False

    def fn(x, y):
        return bool(m[y, x])
    fn.array = m
    return fn


def retalla(img, mask):
    """La imatge només on `mask` (fn amb `.array`) és cert."""
    a = np.asarray(img.convert('RGBA')).copy()
    a[~mask.array] = 0
    return Image.fromarray(a, 'RGBA')


def barreja(img, col, k_arr):
    """Barreja cap a `col` amb el factor (array H×W, 0..1)."""
    a = np.asarray(img.convert('RGBA')).astype(np.float32)
    k = np.clip(k_arr, 0, 1)[..., None]
    a[..., :3] = a[..., :3] * (1 - k) + np.array(col, np.float32) * k
    return Image.fromarray(a.clip(0, 255).astype(np.uint8), 'RGBA')


def bayer():
    """La matriu de Bayer 4×4 estesa a tota la pantalla (H×W)."""
    b = np.array(B4, np.float32)
    return np.tile(b, (H // 4 + 1, W // 4 + 1))[:H, :W]


def escala_v(cam, v):
    """L'escala d'un personatge amb els peus a la fila v de pantalla (al terra, y = 0, en la direcció on mira la
    càmera: amb el picat, l'escala només depèn de v)."""
    sx, cz = math.sin(cam.yaw), math.cos(cam.yaw)
    lo, hi = 1.0, 5000.0
    for _ in range(60):
        t = (lo + hi) / 2
        P = (cam.pos[0] + sx * t, 0, cam.pos[2] + cz * t)
        if cam.projecta(P)[1] > v:
            lo = t
        else:
            hi = t
    t = (lo + hi) / 2
    return round(cam.escala((cam.pos[0] + sx * t, 0, cam.pos[2] + cz * t)), 3)


def v_escala(cam, k):
    """La fila de pantalla on un personatge (amb els peus al terra) fa l'escala k: la inversa d'`escala_v`."""
    lo, hi = 0.0, float(H)
    for _ in range(40):
        v = (lo + hi) / 2
        if escala_v(cam, v) < k:
            lo = v
        else:
            hi = v
    return round((lo + hi) / 2)


# La pedra dels murs de dins (gris amb un punt d'ocre, poc saturada).
PEDRA = [(26, 24, 26), (42, 38, 38), (60, 55, 52), (80, 73, 66), (102, 93, 82), (124, 113, 98), (148, 136, 116),
         (174, 160, 136), (198, 186, 160)]


# ─── Pintar amb numpy (superfícies grans) ────────────────────────────────────

_BAY = np.array(B4, np.float32)


def pinta(cv, x0, y0, lvl, ramp, mask=None):
    """Pinta l'array de nivells `lvl` (h×w) amb la rampa, a partir de (x0, y0) del llenç, amb el dithering de la casa.
    `mask` (h×w bool): només on és cert."""
    h, w = lvl.shape
    ys, xs = np.mgrid[y0:y0 + h, x0:x0 + w]
    b = _BAY[ys & 3, xs & 3]
    idx = np.clip(np.floor(lvl + b - 0.5).astype(int), 0, len(ramp) - 1)
    cols = np.array(ramp, np.uint8)[idx]
    a = np.asarray(cv.img).copy()
    Y0, X0 = max(0, y0), max(0, x0)
    Y1, X1 = min(cv.h, y0 + h), min(cv.w, x0 + w)
    sub = cols[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
    m = np.ones(sub.shape[:2], bool) if mask is None else mask[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
    a[Y0:Y1, X0:X1, :3][m] = sub[m]
    a[Y0:Y1, X0:X1, 3][m] = 255
    cv.img.paste(Image.fromarray(a, 'RGBA'))
    cv.P = cv.img.load()


def soroll_np(w, h, escala, seed=0):
    """Soroll de valors suau (0..1) en una graella de w×h, amb cel·les d'`escala` píxels (numpy)."""
    rng = np.random.default_rng(seed)
    gw, gh = int(w / escala) + 2, int(h / escala) + 2
    g = rng.random((gh, gw)).astype(np.float32)
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32) / escala
    x0, y0 = xs.astype(int), ys.astype(int)
    fx, fy = xs - x0, ys - y0
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a, b = g[y0, x0], g[y0, x0 + 1]
    c, d = g[y0 + 1, x0], g[y0 + 1, x0 + 1]
    return a + (b - a) * fx + (c - a) * fy + (a - b - c + d) * fx * fy


def maconeria(w, h, seed=0, cel=(28, 18), junta=1.6):
    """Un mur de pedres irregulars (Voronoi): → (id de la pedra, distància a la vora, alçada relativa dins la pedra),
    arrays h×w. La vora < `junta` és el morter."""
    rng = np.random.default_rng(seed)
    cw, ch = cel
    gw, gh = w // cw + 3, h // ch + 3
    px = (np.arange(gw)[None, :] - 1 + 0.2 + rng.random((gh, gw)) * 0.6) * cw
    py = (np.arange(gh)[:, None] - 1 + 0.2 + rng.random((gh, gw)) * 0.6) * ch
    px = px + (np.arange(gh)[:, None] % 2) * cw * 0.5
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    ci, cj = (ys / ch).astype(int) + 1, (xs / cw).astype(int) + 1
    cj = np.clip(cj, 1, gw - 2)
    d1 = np.full((h, w), 1e9, np.float32)
    d2 = np.full((h, w), 1e9, np.float32)
    ids = np.zeros((h, w), np.int32)
    dyc = np.zeros((h, w), np.float32)
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            ii, jj = np.clip(ci + di, 0, gh - 1), np.clip(cj + dj, 0, gw - 1)
            qx, qy = px[ii, jj], py[ii, jj]
            # (pedres més amples que altes: la distància en y compta més)
            d = np.hypot((xs - qx) / cw, (ys - qy) / ch) * min(cw, ch)
            closer = d < d1
            d2 = np.where(closer, d1, np.minimum(d2, d))
            ids = np.where(closer, ii * gw + jj, ids)
            dyc = np.where(closer, (ys - qy) / ch, dyc)
            d1 = np.where(closer, d, d1)
    return ids, (d2 - d1) / 2, dyc


def mur_pedra(cv, x0, y0, w, h, base, seed, ramp=None, gres=0.15, cel=(36, 20)):
    """Pinta un mur de pedra irregular (de `ramp`, per defecte PEDRA, amb una part de pedres de GRES): cada pedra
    amb la llum per dalt i l'ombra per baix, i el morter clar i enfonsat entre pedra i pedra."""
    ramp = ramp or PEDRA
    ids, vora, dy = maconeria(w, h, seed, cel)
    rnd = np.random.default_rng(seed + 1).random(ids.max() + 1)
    n = soroll_np(w, h, 3, seed + 2)
    lvl = base + (rnd[ids] - 0.5) * 1.0 + (n - 0.5) * 0.8 - dy * 0.9
    lvl = lvl - np.clip(1.8 - vora, 0, 1) * np.where(dy > 0, 0.9, -0.3)   # la vora: clara a dalt, fosca a baix
    es_gres = rnd[ids] > 1 - gres
    morter = vora < 0.9
    pinta(cv, x0, y0, np.where(morter, base - 0.5 + (n - 0.5) * 0.6, lvl), ramp, mask=~es_gres | morter)
    pinta(cv, x0, y0, lvl - 1.1, GRES, mask=es_gres & ~morter)


def _dins_poly(p, poly):
    x, y = p
    c = False
    for (ax, ay), (bx, by) in zip(poly, poly[1:] + poly[:1]):
        if (ay > y) != (by > y) and x < ax + (y - ay) * (bx - ax) / (by - ay):
            c = not c
    return c


def ajusta_geometria(geo, marge=3):
    """Porta els punts on es camina (`walk` de cada cosa i els `spawns`) dins el terra on es camina (i fora dels
    forats), al punt més proper, amb `marge` píxels de marge."""
    poly, forats = geo['walkable'], geo.get('forats', [])

    def ok(p):
        return all(_dins_poly((p[0] + dx, p[1] + dy), poly) and not any(_dins_poly((p[0] + dx, p[1] + dy), f) for f in forats)
                   for dx, dy in ((0, 0), (marge, 0), (-marge, 0), (0, marge), (0, -marge)))

    def a_dins(p):
        if ok(p):
            return p
        for r in range(1, 200):
            best = None
            for dx in range(-r, r + 1):
                for dy in (-r, r):
                    for q in ((p[0] + dx, p[1] + dy), (p[0] + dy, p[1] + dx)):
                        if ok(q) and (best is None or math.hypot(q[0] - p[0], q[1] - p[1]) < best[0]):
                            best = (math.hypot(q[0] - p[0], q[1] - p[1]), q)
            if best:
                return best[1]
        return p
    for t in geo['things'].values():
        if 'walk' in t:
            t['walk'] = a_dins(tuple(t['walk']))
    geo['spawns'] = {k: a_dins(tuple(v)) for k, v in geo['spawns'].items()}
    return geo
