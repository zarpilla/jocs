"""
La Conjura de l'Avet — peces comunes de les sales de nit de dins el monestir (la porteria, la cuina i
l'scriptorium): les rampes de la pedra de gres, la fusta fosca, el ferro, el foc i la cera; el soroll ràpid; els
carreus i les lloses (en coordenades del món: s'empetiteixen sols cap al fons); flames i espelmes (en pantalla, per
a les animacions); i la llum de la sala sobre els personatges (`characterLights`) a partir dels llums del món.

Totes tres són de nit: la llum és només la del foc, les torxes i les espelmes (càlida), i els racons queden foscos.
L'únic vermell viu és la cera dels segells (aquí, la ratlla vermella de l'espelma de les hores).
"""
import math
import random

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)

from hd.pix import B4, mix  # noqa: F401
from hd.rooms.comu import _diff  # noqa: F401

W, H = 640, 360
BOTTOM = 259                   # la sala acaba aquí (a sota, el HUD)

# ─── Rampes (fosc → clar) ───────────────────────────────────────────────────
# La pedra de gres del monestir, rosada i ocre; de nit, als racons, gairebé negra.
PEDRA = [(10, 7, 9), (20, 13, 14), (32, 21, 20), (46, 31, 27), (62, 42, 34), (80, 55, 42), (100, 70, 51),
         (122, 87, 61), (146, 106, 73), (172, 128, 88), (198, 152, 106), (222, 180, 130), (240, 206, 158)]
# Les lloses del terra: una mica més grises i gastades.
LLOSA = [(9, 8, 9), (18, 15, 15), (29, 24, 22), (42, 35, 31), (57, 47, 40), (74, 61, 50), (93, 76, 60),
         (114, 93, 72), (138, 113, 86), (164, 135, 102), (190, 160, 122), (214, 186, 146)]
FUSTA = [(10, 6, 5), (20, 12, 8), (32, 20, 12), (46, 29, 17), (62, 40, 22), (80, 52, 28), (100, 66, 35),
         (122, 82, 44), (146, 100, 55), (172, 122, 70), (198, 148, 90)]
FERRO = [(6, 6, 8), (14, 13, 16), (24, 22, 26), (36, 33, 36), (52, 47, 48), (72, 64, 62), (96, 86, 80),
         (126, 112, 100), (160, 142, 124)]
COURE = [(22, 10, 6), (44, 20, 10), (70, 34, 16), (100, 52, 24), (132, 74, 34), (166, 100, 48), (200, 132, 70),
         (230, 170, 104), (250, 210, 150)]
FOC = [(60, 12, 6), (120, 30, 8), (184, 62, 12), (232, 108, 22), (252, 160, 48), (255, 212, 108), (255, 244, 200)]
BRASA = [(20, 6, 4), (50, 12, 6), (96, 22, 8), (150, 40, 10), (206, 74, 16), (246, 124, 34), (255, 184, 80)]
CENDRA = [(14, 12, 12), (26, 22, 22), (40, 34, 32), (58, 50, 46), (80, 70, 62)]
CERA = [(40, 30, 22), (78, 62, 44), (120, 98, 70), (162, 136, 100), (200, 176, 136), (228, 208, 168),
        (246, 232, 198), (255, 248, 226)]
VERMELL = [(30, 4, 6), (64, 8, 10), (110, 14, 14), (160, 24, 20), (204, 40, 28), (236, 72, 44), (255, 120, 80)]
PERGAMI = [(54, 40, 28), (96, 74, 50), (140, 112, 78), (180, 150, 108), (212, 184, 138), (234, 212, 168),
           (248, 234, 200)]
TINTA = [(8, 6, 8), (20, 16, 18), (38, 30, 30), (60, 48, 44)]
LLUNA = [(4, 6, 14), (8, 12, 26), (14, 20, 40), (22, 32, 58), (34, 48, 80), (52, 70, 106), (78, 98, 136),
         (114, 136, 170), (160, 180, 206)]
TELA = [(14, 10, 10), (26, 18, 16), (40, 30, 24), (58, 44, 34), (78, 60, 46), (100, 80, 60), (124, 102, 78)]
FANG = [(16, 8, 6), (32, 16, 10), (54, 28, 16), (80, 42, 24), (108, 60, 34), (138, 80, 46), (168, 104, 62),
        (196, 132, 84)]
VI = [(14, 2, 8), (30, 4, 14), (52, 8, 22), (78, 14, 30), (106, 24, 40)]

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
    return _h(int(a[0]) if a else 0, int(a[1]) if len(a) > 1 else 0, int(a[2]) if len(a) > 2 else 0)


# ─── Pedra: carreus i lloses (en unitats del món) ───────────────────────────

def carreus(s, t, alt=30.0, ample=(46.0, 70.0), seed=1, base=2.6, junta=1.6):
    """El nivell d'un parament de carreus a (s, t) (unitats del món, t cap avall): filades de `alt`, cada carreu
    d'un ample diferent; la junta de morter fosca, la vora de dalt i la de l'esquerra del carreu, un to més clara
    (la pedra picada fa bisell), i cada carreu amb el seu to i les seves taques."""
    fila = int(t // alt)
    ft = t - fila * alt
    # l'ample de cada carreu: es desplaça a cada filada (com un mur de debò)
    off = hr(fila, 3, seed) * ample[1]
    ss = s + off
    w = ample[0] + (ample[1] - ample[0]) * hr(int(ss // ample[1]), fila, seed + 1)
    col = int(ss // w)
    fs = ss - col * w
    v = base + (hr(col, fila, seed + 2) - 0.5) * 0.9 + (fbm(s / 9, t / 7, seed + 3) - 0.5) * 0.9
    v += (fbm(s / 2.5, t / 2.5, seed + 4) - 0.5) * 0.5
    if ft < 1.6 or fs < 1.6:
        return v - junta
    if ft < 3.2 or fs < 3.2:
        v += 0.5
    if ft > alt - 3.0:
        v -= 0.5                                                    # la vora de baix, a l'ombra
    if fbm(s / 14 + col, t / 10, seed + 5) > 0.72:
        v -= 0.5                                                    # taques d'humitat i de fum
    return v


def lloses(x, z, mida=(52.0, 44.0), seed=11, base=2.4):
    """El nivell d'un terra de lloses a (x, z) del món: lloses grosses i desiguals, juntes fosques, gastades al mig."""
    fila = int(z // mida[1])
    fz = z - fila * mida[1]
    off = hr(fila, 1, seed) * mida[0]
    xx = x + off
    w = mida[0] * (0.8 + 0.5 * hr(int(xx // mida[0]), fila, seed + 1))
    col = int(xx // w)
    fx = xx - col * w
    v = base + (hr(col, fila, seed + 2) - 0.5) * 0.8 + (fbm(x / 16, z / 16, seed + 3) - 0.5) * 0.9
    v += (fbm(x / 3, z / 3, seed + 4) - 0.5) * 0.45
    if fz < 1.8 or fx < 1.8:
        return v - 1.5
    if fz < 3.5:
        v += 0.35
    if hr(int(x / 5), int(z / 5), seed + 5) > 0.985:
        v -= 0.8                                                    # una esquerda, un forat
    return v


def taulons(s, t, ample=14.0, seed=21, base=3.0):
    """Fusta de taulons verticals (una porta, un armari): la veta llarga, les juntes fosques."""
    k = int(s // ample)
    fs = s - k * ample
    v = base + (hr(k, 0, seed) - 0.5) * 0.7 + (fbm(s / 2, t / 22, seed + 1) - 0.5) * 1.1
    if fs < 1.2:
        return v - 1.6
    if fs > ample - 1.5:
        v -= 0.4
    return v


def veta(s, t, seed=31, base=3.0):
    """Fusta llisa amb veta (una taula, un banc): la veta va al llarg de `s`."""
    return base + (fbm(s / 30, t / 2.2, seed) - 0.5) * 1.3 + (fbm(s / 4, t / 1.2, seed + 1) - 0.5) * 0.5


# ─── Foc, flames i espelmes (en pantalla) ───────────────────────────────────

def flama(cv, x, y, h, w, fase, seed=0, ramp=FOC, k=1.0):
    """Una flama dreta de base (x, y), alta `h` i ampla `w` a la base; `fase` (0..1) la fa bellugar (en bucle).
    Més clara al cor, vermellosa a les vores i a la punta."""
    a = 2 * math.pi * fase
    sway = math.sin(a + seed) * 0.18 + math.sin(2 * a + seed * 1.7) * 0.08
    hh = h * (0.9 + 0.12 * math.sin(3 * a + seed * 2.3))
    for j in range(int(hh) + 1):
        tt = j / max(1, hh)                                          # 0 a la base, 1 a la punta
        half = w * 0.5 * (1 - tt) ** 0.8 * (0.75 + 0.5 * math.sin(math.pi * min(1, tt * 1.6 + 0.2)))
        cx = x + sway * h * tt * tt + math.sin(tt * 7 + a * 2 + seed) * w * 0.08 * tt
        yy = y - j
        for i in range(int(cx - half - 1), int(cx + half + 2)):
            d = abs(i + 0.5 - cx) / max(0.6, half)
            if d > 1:
                continue
            lvl = (6.4 - tt * 3.2 - d * 2.4) * k
            cv.put(i, yy, ramp, lvl, lit=0)


def espelma(cv, x, y, h, gruix=3, lvl=4.0, ramp=CERA):
    """Una espelma dreta (en pantalla): de base (x, y), alta `h`; el cos de cera i el ble fosc a dalt."""
    for j in range(h):
        for i in range(gruix):
            cv.put(x - gruix // 2 + i, y - j, ramp, lvl + (0.8 if i == 0 else -0.6 if i == gruix - 1 else 0), lit=0)
    cv.put(x, y - h, TINTA, 1.0, lit=0)
    # la cera que regalima
    cv.put(x - gruix // 2, y - h + 2, ramp, lvl + 1.4, lit=0)


def flameta(cv, x, y, fase, seed=0, alt=7, ample=3.0):
    """La flama d'una espelma: petita, groga i blanca al cor."""
    flama(cv, x, y, alt, ample, fase, seed=seed, ramp=FOC, k=1.12)


def resplendor(cv, x, y, r, col, k):
    """Un halo de llum (dithered) sobre el que ja hi ha pintat: el que fa una flama a l'aire."""
    cv.glow(x, y, r, col, k)


# ─── Ombres, decorats, HUD ─────────────────────────────────────────────────

def ombra(cv, cx, cy, rx, ry, k=0.85):
    cv.darken(cx - rx - 2, cy - ry - 2, cx + rx + 2, cy + ry + 2,
              lambda x, y: k if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1 else 0)


def hud_negre(cv):
    """A sota de la sala, el HUD: negre."""
    cv.rect(0, BOTTOM + 1, cv.w - 1, cv.h - 1, [(0, 0, 0)], 0, lit=0)


def sense(img, mask_img):
    """`img` sense els píxels que `mask_img` (RGBA) té pintats: el que canvia un decorat no ha de tapar el primer pla."""
    import numpy as np
    from PIL import Image
    a = np.asarray(img.convert('RGBA')).copy()
    m = np.asarray(mask_img.convert('RGBA'))[..., 3] > 0
    a[m] = 0
    return Image.fromarray(a, 'RGBA')


def sense_hud(img):
    """Treu el que hi hagi per sota de la sala (la franja del HUD)."""
    a = img.load()
    for y in range(BOTTOM + 1, img.height):
        for x in range(img.width):
            a[x, y] = (0, 0, 0, 0)
    return img


def mascara(img):
    """→ fn(x, y): si la imatge RGBA hi té alguna cosa pintada (per a les capes del davant)."""
    a = img.load()
    w, h = img.size
    return lambda x, y: 0 <= x < w and 0 <= y < h and a[x, y][3] > 0


# ─── La llum de la sala sobre els personatges ────────────────────────────────

def hexa(col):
    return '#%02x%02x%02x' % tuple(max(0, min(255, int(c))) for c in col)


def llum_personatge(cam, pos, radi_mon, color, intensitat, pit=60.0):
    """Un llum de `characterLights` a partir d'un llum del món: el punt de terra sota el llum, alçat fins al pit d'un
    personatge (`pit`), projectat amb la càmera; el radi del món passat a píxels de sala a aquella distància."""
    x, y, z = pos
    u, v, _ = cam.projecta((x, min(y, pit), z))
    r = radi_mon * cam.escala((x, 0, z))
    return {'x': round(u), 'y': round(v), 'radius': round(r), 'color': hexa(color), 'intensity': round(intensitat, 2)}


def rect_de(*pts, pad=0, bottom=BOTTOM):
    us, vs = [p[0] for p in pts], [p[1] for p in pts]
    return (max(0, round(min(us)) - pad), max(0, round(min(vs)) - pad), min(W - 1, round(max(us)) + pad),
            min(bottom, round(max(vs)) + pad))


def ombra_terra(e, llum, pts, k=0.6, vora=0.25, sid='ombra'):
    """L'ombra a terra d'un rectangle del món (`pts`: quatre punts per sobre de terra, P0..P3) amb un llum puntual
    (`llum`: (x, y, z), més alt que els punts): es projecten des del llum fins a terra i s'enfosqueix el quadrilàter,
    més suau cap a les vores (`vora`: fracció)."""
    lx, ly, lz = llum
    out = []
    for x, y, z in pts:
        if y >= ly - 1:
            return
        f = ly / (ly - y)
        out.append((lx + (x - lx) * f, 0.25, lz + (z - lz) * f))
    P0, P1, P2, P3 = out
    L1 = math.dist(P0, P1) or 1
    L3 = math.dist(P0, P3) or 1

    def suau(s, t):
        a = min(s, L1 - s) / (L1 * vora)
        b = min(t, L3 - t) / (L3 * vora)
        return k * max(0.0, min(1.0, a, b))
    e.foscor(sid, P0, P1, P2, P3, suau)


def marca(e, sid, dibuix):
    """Executa `dibuix()` (que pinta en pantalla, damunt el llenç de l'escena) i fa que els píxels que ha canviat
    siguin de la superfície `sid` (per a les màscares de les capes del davant: la gerra damunt la taula, la llenya)."""
    import numpy as np
    cv = e.cv
    abans = np.asarray(cv.img).copy()
    dibuix()
    cv.P = cv.img.load()
    canvi = (np.asarray(cv.img) != abans).any(axis=2)
    idx = e._idx_de(sid)
    ys, xs = np.nonzero(canvi)
    W_ = cv.w
    for y, x in zip(ys.tolist(), xs.tolist()):
        e.amo[y * W_ + x] = idx
