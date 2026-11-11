"""
Final · L'Anell de Baix: el carrer del barri pobre de l'anell, un congost de cases apilades sota la franja de
llum del sostre (el dia artificial, càlid). El terra de l'anell s'enfila al fons fins que es perd entre la
boirina daurada. Roba estesa d'una banda a l'altra, rètols, testos a les finestres, i els filtres d'aire que la
Vet hi va instal·lar girant a les façanes, amb claus angleses pintades al costat. Al mig del carrer, d'esquena,
la Vet hi torna caminant.
Pantalla sencera (sense barra de verbs). Es dibuixa amb un petit traçador de raigs: cada píxel sap a quina
paret, terra o sostre toca i a quina distància, i la boirina hi barreja l'or del fons.

A 640×360 (hd/rooms/final_anell.py a ×4/3): el mateix carrer i la mateixa càmera (focal ×4/3), traçat de nou a
la resolució gran, de manera que les juntes, les pales dels filtres, la roba i la gent llunyana hi guanyen
píxels. Els rètols (la pancarta, BAR, TALLER, PA) van amb la lletra de 4×7 de La Gavina, i la Vet és la de 640.
"""
import math
import random


import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from hd.pix import (Canvas, Light, B4, W, H, mix, ramp, STEEL, PANEL, RUST, TEAL, WARN, GRAY, SIL, IRON,
                    PAPER, WALNUT, RED, SUIT, SKIN)
from hd640.draw_characters import person, VET
from hd640.rooms.gavina_passadis import hr, diff, FONT7

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)
K4 = 4 / 3                      # 480 → 640

# Rampes pròpies (fosc → clar)
HAZE = ramp((70, 40, 40), (130, 80, 60), (190, 130, 80), (232, 178, 110), (250, 218, 160), (255, 242, 210), n=9)
SUNSTRIP = ramp((200, 150, 90), (250, 214, 150), (255, 240, 200), (255, 252, 240), n=4)
DECK = ramp((20, 14, 16), (38, 28, 26), (60, 44, 36), (86, 64, 48), (114, 88, 64), (146, 116, 84), (180, 150, 110),
            (214, 186, 140), n=8)
OCHRE = ramp((30, 18, 14), (64, 38, 22), (108, 68, 34), (150, 102, 50), (190, 140, 72), (222, 178, 104), (244, 214, 146), n=8)
PLASTER = ramp((34, 24, 26), (66, 50, 48), (104, 84, 74), (144, 122, 102), (184, 160, 132), (218, 198, 166), (242, 228, 200), n=8)
MINT = ramp((14, 26, 26), (26, 50, 46), (44, 78, 68), (68, 110, 92), (100, 144, 118), (144, 180, 150), (196, 220, 190), n=8)
ROSE = ramp((32, 14, 20), (64, 28, 34), (104, 48, 50), (146, 74, 68), (186, 106, 90), (218, 146, 120), (240, 190, 160), n=8)
BLUE = ramp((14, 20, 40), (26, 40, 72), (40, 64, 108), (62, 96, 146), (96, 134, 182), (146, 180, 214), (200, 222, 240), n=8)
WINLIT = ramp((90, 40, 20), (170, 90, 40), (230, 150, 70), (255, 206, 120), (255, 240, 190), n=5)
LEAF = ramp((10, 24, 14), (20, 46, 22), (36, 76, 32), (60, 110, 44), (100, 150, 60), (150, 190, 90), n=6)

HOUSE_RAMPS = [OCHRE, PLASTER, MINT, ROSE, RUST, PLASTER, OCHRE, TEAL]

# Càmera i geometria (metres)
CX, CY, F = 320, 133.5, 260 * K4  # punt de fuga i focal (els de 480, a ×4/3)
CH = 3.3                        # alçada de la càmera
WD = 8.0                        # mig ample del carrer
HC = 19.0                       # alçada del sostre
CURV = 1 / (2 * 300.0)          # curvatura de l'anell: el terra puja z²/(2R)
HAZE_Z = 95.0                   # distància característica de la boirina
STOREY = 3.0                    # alçada d'un pis
TAU = 2 * math.pi
_T = 0.0                        # temps del bucle d'animació (0..1); t=0 és el fons quiet


def _houses(seed):
    """Les cases d'una banda: [(z0, z1, pisos, rampa, llavor)]."""
    rnd = random.Random(seed)
    out, z = [], 2.0
    while z < 600:
        w = rnd.uniform(3.2, 6.5)
        out.append((z, z + w, rnd.randint(2, 5), rnd.choice(HOUSE_RAMPS), rnd.randint(0, 9999)))
        z += w
    return out


HOUSES = {-1: _houses(3), 1: _houses(8)}
RIB = 26.0                       # costelles de l'anell


def house_at(side, z):
    hs = HOUSES[side]
    lo, hi = 0, len(hs) - 1
    while lo < hi:
        m = (lo + hi) // 2
        if hs[m][1] < z:
            lo = m + 1
        else:
            hi = m
    return hs[lo]


# ─── El traçat: cada píxel → (superfície, coordenades) ─────────────────────

def cast(px, py):
    """→ (tipus, z, a, b): 'floor' (a=x lateral), 'wall' (a=z, b=alçada, side), 'ceil' (a=x lateral)."""
    dx = (px - CX) / F
    dy = (CY - py) / F
    best = None
    # terra: CH + dy z - c z² = 0
    disc = dy * dy + 4 * CURV * CH
    zf = (dy + math.sqrt(disc)) / (2 * CURV)
    best = ('floor', zf)
    # sostre: CH + dy z - c z² = HC
    disc = dy * dy - 4 * CURV * (HC - CH)
    if disc >= 0 and dy > 0:
        zc = (dy - math.sqrt(disc)) / (2 * CURV)
        if zc < best[1]:
            best = ('ceil', zc)
    if abs(dx) > 1e-6:
        zw = WD / abs(dx)
        yw = CH + dy * zw - CURV * zw * zw
        if zw < best[1] and 0 <= yw <= HC:
            best = ('wall', zw)
    kind, z = best
    y = CH + dy * z - CURV * z * z
    return kind, z, dx * z, y


def proj(x, y, z):
    """Punt del món (lateral, alçada, distància) → píxel."""
    return CX + F * x / z, CY - F * (y - CH + CURV * z * z) / z


def floor_chalk(x, z):
    """Guix a terra: una xarranca i una clau anglesa (els nens del barri)."""
    col = None
    # xarranca: caselles d'1×1 m, a l'esquerra del carrer
    hx, hz = x + 4.6, z - 6.2
    rows = [(0, 1), (1, 1), (2, 2), (3, 1), (4, 2), (5, 1)]
    if -0.6 < hx < 1.6 and 0 <= hz < 6.6:
        r = int(hz)
        if r < len(rows):
            n = rows[r][1]
            w = 1.0
            x0 = 0.5 - n * w / 2
            fx, fz = (hx - x0), hz - r
            if 0 <= fx <= n * w + 0.05:
                e = 0.05 * max(1.0, z / 9.3)
                if fz < e or fx < e or (n * w - fx) < e or (n == 2 and abs(fx - 1.0) < e / 2):
                    col = (226, 220, 206)
        elif r == 6 and math.hypot(hx - 0.5, hz - 6.3) < 0.5 and abs(math.hypot(hx - 0.5, hz - 6.3) - 0.45) < 0.06:
            col = (226, 220, 206)
    # una clau anglesa feta amb guix groc
    du, dz = (x - 3.3) / 1.0, (z - 7.2) / 1.25
    if abs(du) < 1.4 and abs(dz) < 1.4:
        def wr(a, b):
            return wrench(b * 0.45 + a * 0.9, a * 0.45 - b * 0.9)
        e = 0.07 * max(1.0, z / 9.3)
        if wr(du, dz) and not (wr(du + e, dz) and wr(du - e, dz) and wr(du, dz + e) and wr(du, dz - e)):
            col = (240, 206, 110)
    if col and hr(int(x * 14), int(z * 14), 6) < 0.18:
        return None                                     # el guix, esborrat a trossos
    return col


# ─── Materials ──────────────────────────────────────────────────────────────

def mat_floor(x, z):
    ax = abs(x)
    chalk = floor_chalk(x, z)
    if chalk:
        return 'paint', chalk
    if ax > WD - 1.6:                                   # voreres
        u = (z * 1.0) % 1.0
        lvl = 3.6 + (hr(int(z), int(x > 0), 2) - 0.5) * 0.4
        if u < 0.06 * min(1, 8 / z) + 0.03:
            lvl -= 0.9
        if WD - 1.6 <= ax < WD - 1.45:
            lvl += 1.3                                  # la vorada
        return PLASTER, lvl - 0.3
    u, v = (x + 0.5) % 2.0, z % 2.0
    lvl = 3.7 - ax * 0.1 + (hr(int((x + 0.5) // 2), int(z // 2), 5) - 0.5) * 0.5
    if u < 0.07 or v < 0.07 * max(1, z / 16):
        lvl -= 1.0
    if ax < 0.25:
        lvl -= 1.4                                      # canal del mig
    if (int(z * 3) + int(x * 3)) % 7 == 0:
        lvl += 0.3
    return DECK, lvl


def wrench(p, q):
    """Silueta d'una clau anglesa (coordenades locals: el mànec va de p=-1 a p=0.5, el cap a p≈0.75)."""
    if -0.95 < p < 0.55 and abs(q) < 0.11 + max(0.0, p - 0.35) * 0.4:
        return True
    d = math.hypot(p - 0.75, q)
    if d < 0.32 and not (d < 0.13 or (p > 0.74 and abs(q) < 0.13)):
        return True
    d = math.hypot(p + 1.0, q)
    return 0.07 < d < 0.18


# Filtres grossos (els del barri, a les façanes) i claus angleses pintades: (costat, z, alçada, radi)
FANS = [(-1, 11.4, 3.9, 1.35), (1, 10.4, 3.7, 1.2), (-1, 27.0, 8.6, 1.3), (1, 33.0, 10.2, 1.2)]
WRENCHES = [(-1, 11.4, 6.25, 0.95, 0.0, (246, 206, 90)), (1, 10.6, 5.9, 0.8, 3.14, (236, 236, 222)),
            (1, 21.0, 4.4, 1.1, -0.25, (246, 206, 90)), (-1, 19.0, 9.6, 1.2, 0.3, (236, 236, 222)),
            (-1, 40.0, 5.0, 1.4, 0.0, (246, 206, 90))]


def mat_fan(du, dv, r, z, spin=1):
    """Ventilador d'un filtre d'aire, girant (les pales, mogudes)."""
    d = math.hypot(du, dv)
    if d > r + 0.32 or max(abs(du), abs(dv)) > r + 0.3:
        return None
    if d > r:                                           # la caixa, amb cargols
        lvl = 3.4 + (dv / r) * 0.6
        if abs(abs(du) - (r + 0.12)) < 0.07 and abs(abs(dv) - (r + 0.12)) < 0.07:
            lvl += 2.0
        return STEEL, lvl
    if d > r - 0.12:
        return STEEL, 5.0 - (du + dv) * 0.8               # el cèrcol, lluent
    if d < 0.2:
        return STEEL, 4.6 + (0.8 if d < 0.08 else 0)
    if (d % 0.3) < 0.035 * max(1.0, z / 12):
        return STEEL, 3.2                               # la reixa
    a = math.atan2(dv, du)
    ph = (a * 3 / (2 * math.pi) + d * 0.5 + spin * 2 * _T) % 1     # dues pales per bucle
    blade = max(0.0, 1 - ph / 0.55)                     # pala nítida al davant, estela de moviment darrere
    return IRON, 1.0 + blade ** 1.5 * 3.2 + (0.4 if ph < 0.05 else 0)


def mat_wall(side, z, y):
    for i, (sd, zc, yc, r) in enumerate(FANS):
        if sd == side and abs(z - zc) < r + 0.4 and abs(y - yc) < r + 0.4:
            m = mat_fan(z - zc, y - yc, r, z, spin=1 if i % 2 else -1)
            if m:
                return m
    paint = None
    for sd, zc, yc, sc, ang, col in WRENCHES:
        if sd == side and abs(z - zc) < sc * 1.3 and abs(y - yc) < sc * 1.3:
            du, dv = (z - zc) / sc, (y - yc) / sc
            c, sn = math.cos(ang), math.sin(ang)
            if wrench(du * c + dv * sn, -du * sn + dv * c) and hr(int(z * 9), int(y * 9), 3) > 0.12:
                paint = col
    if paint:
        return 'paint', paint
    z0, z1, n, rmp, seed = house_at(side, z)
    u = z - z0
    w = z1 - z0
    top = n * STOREY
    rib = (z % RIB) < 1.0
    if rib:                                              # costella de l'anell (acer)
        return STEEL, 3.0 + (0.8 if (z % RIB) < 0.2 else 0) + (0.5 if int(y) % 3 == 0 else 0)
    if y > top:                                          # paret de l'anell, per sobre de les cases
        lvl = 1.8 + (hr(int(z // 4), int(y // 3), 6) - 0.5) * 0.5
        if (y % 3) < 0.12 or (z % 4) < 0.12:
            lvl -= 0.8
        if y > top and y < top + 0.25:
            lvl -= 0.8
        # canonades al llarg de la paret
        if abs(y - 13.2) < 0.18 or abs(y - 14.0) < 0.12:
            return RUST, 2.8 + (0.6 if y > 13.2 else 0)
        return PANEL, lvl + y * 0.06
    st = int(y // STOREY)
    v = y - st * STOREY
    lvl = 3.0 + (hr(seed, st, 1) - 0.5) * 0.6 + (hr(int(z * 2), int(y * 2), seed) - 0.5) * 0.35
    if u < 0.12 or w - u < 0.12:
        return rmp, lvl - 1.6                            # junta entre cases
    if v < 0.18 and st > 0:
        return rmp, lvl - 1.4                            # ombra sota la llosa
    if v > STOREY - 0.14:
        return rmp, lvl + 1.0                            # cantell de la llosa
    if abs(y - top) < 0.3:
        return rmp, lvl + 0.8                            # ampit del terrat
    rnd = hr(seed, st, 2)
    # finestres
    nwin = 1 if w < 4.6 else 2
    for k in range(nwin):
        wc = w * (k + 1) / (nwin + 1)
        if st == 0 and k == 0:
            # porta a la planta baixa
            if abs(u - wc) < 0.55 and v < 2.2:
                if abs(u - wc) > 0.45 or v > 2.1:
                    return WALNUT, 4.0
                return WALNUT, 1.6 + (0.6 if (u - wc) % 0.3 < 0.05 else 0)
            continue
        if abs(u - wc) < 0.55 and 1.0 < v < 2.2:
            lit = hr(seed, st, k, 4) < 0.55
            if abs(u - wc) > 0.47 or v > 2.12 or v < 1.08:
                return rmp, lvl + 1.6                    # marc
            if lit:
                return WINLIT, 2.4 + (v - 1.0) * 0.8 + (0.6 if abs(u - wc) < 0.04 else 0)
            return SIL, 2.0 + (v - 1.0) * 0.6
        if abs(u - wc) < 0.7 and 0.88 < v < 1.0:
            return rmp, lvl + 1.8                        # ampit
        if abs(u - wc) < 0.6 and 0.66 < v < 0.88 and hr(seed, st, k, 9) < 0.5:
            return LEAF, 2.6 + hr(int(z * 8), int(y * 8)) * 1.6     # test amb plantes
    # el filtre d'aire de la casa (una caixa amb un ventilador rodó)
    if hr(seed, st, 7) < 0.6:
        fu, fv = w - 0.75, 1.55
        d = math.hypot(u - fu, v - fv)
        if abs(u - fu) < 0.38 and abs(v - fv) < 0.38:
            if d < 0.27:
                return IRON, 1.6 + (1.4 if d < 0.06 else 0) + (0.8 if (math.atan2(v - fv, u - fu) * 3 / math.pi + 2 * _T) % 1 < 0.4 else 0)
            return GRAY, 3.2 - (v - fv) * 1.5
    return rmp, lvl


def mat_ceil(x, z):
    ax = abs(x)
    if ax < 1.4:
        return SUNSTRIP, 3.2 - ax * 0.5
    if ax < 1.7:
        return STEEL, 4.6
    if (z % RIB) < 1.2:
        return STEEL, 3.2
    lvl = 1.6 + (hr(int(x // 3), int(z // 3), 8) - 0.5) * 0.4
    if (x % 3) < 0.15 or (z % 3) < 0.15:
        lvl -= 0.6
    return PANEL, lvl + max(0.0, 1 - ax / 6) * 1.4


def hazeify(cv, px, py, z):
    """Boirina daurada: barreja en esglaons (amb trama) cap al color de l'aire del fons."""
    k = (1 - math.exp(-z / HAZE_Z)) * 0.92
    kq = math.floor(k * 7 + B4[py & 3][px & 3] - 0.5) / 7
    if kq > 0:
        hz = HAZE[min(8, max(0, int(4.6 + (CY - py) * 0.015 - abs(px - CX) * 0.003 + k * 2.4)))]
        cv.flat(px, py, mix(cv.get(px, py), hz, kq))


def wput(cv, zbuf, px, py, z, rmp, lvl=None):
    """Píxel d'un objecte del món a distància z: amagat si hi ha alguna cosa més a prop, i amb boirina."""
    px, py = int(round(px)), int(round(py))
    if not (0 <= px < W and 0 <= py < H) or z >= zbuf[py][px]:
        return
    if lvl is None:
        cv.flat(px, py, rmp)
    else:
        cv.put(px, py, rmp, lvl, 0)
    hazeify(cv, px, py, z)
    zbuf[py][px] = z


def billboard(cv, zbuf, x0, y1, w, h, z, fn):
    """Una cosa plana de cara a la càmera (x0..x0+w, de y1 cap avall h metres) a distància z.
    fn(u, v) amb u, v en metres (v cap avall) → (rampa, nivell), color RGB o None."""
    ax, ay = proj(x0, y1, z)
    bx, by = proj(x0 + w, y1 - h, z)
    k = F / z
    for py in range(math.floor(ay), math.ceil(by) + 1):
        for px in range(math.floor(ax), math.ceil(bx) + 1):
            u, v = (px + 0.5 - ax) / k, (py + 0.5 - ay) / k
            if 0 <= u <= w and 0 <= v <= h:
                m = fn(u, v)
                if m is None:
                    continue
                if isinstance(m[0], list):
                    wput(cv, zbuf, px, py, z, m[0], m[1])
                else:
                    wput(cv, zbuf, px, py, z, m)


_CAST = []


def _casts():
    """El traçat de tots els píxels (no canvia d'un fotograma a l'altre: es calcula un cop)."""
    if not _CAST:
        _CAST.extend([cast(px, py) for px in range(W)] for py in range(H))
    return _CAST


def scene(cv):
    zbuf = [[0.0] * W for _ in range(H)]
    casts = _casts()
    for py in range(H):
        row = casts[py]
        for px in range(W):
            kind, z, a, b = row[px]
            if kind == 'floor':
                rmp, lvl = mat_floor(a, z)
                if rmp != 'paint':
                    lvl += 0.8 * max(0.0, 1 - abs(a) / 7)          # la franja de sol del sostre
                    lvl -= 1.6 * max(0.0, 1 - (WD - abs(a)) / 0.7) ** 2   # ombra al peu de les parets
                    if abs(a) < 1.2:                                 # el terra polit hi fa un reflex
                        lvl += 0.5 * (1 - abs(a) / 1.2) * (hr(int(z * 2), 0, 3) > 0.3)
            elif kind == 'wall':
                rmp, lvl = mat_wall(-1 if a < 0 else 1, z, b)
                if rmp != 'paint':
                    lvl += 0.04 * b + (0.3 if a > 0 else 0)       # la llum del sostre: més clar a dalt
                    lvl -= 1.4 * max(0.0, 1 - b / 0.6) ** 2         # brutícia i ombra a peu de carrer
                    if rmp not in (STEEL, IRON, GRAY, WINLIT, SIL, LEAF) and 0.6 < b < 2.0:
                        if hr(int(z * 3), 1, 5) > 0.7:
                            lvl -= 0.35                              # regalims
            else:
                rmp, lvl = mat_ceil(a, z)
            zbuf[py][px] = z
            if rmp == 'paint':                                 # pintura a la paret (una mica gastada)
                cv.flat(px, py, mix(lvl, (120, 90, 70), 0.25 * hr(px // 2, py // 2, 4)))
            else:
                cv.put(px, py, rmp, lvl, 0)
            hazeify(cv, px, py, z)
    return zbuf


# ─── Coses del carrer ───────────────────────────────────────────────────────

CLOTH = [ROSE, MINT, PAPER, OCHRE, BLUE, PAPER, WARN, ROSE, BLUE]


def garment(kind, w, h, rmp, seed):
    def f(u, v):
        fold = 0.35 * math.sin(u * 22 + seed - TAU * 2 * _T) + (hr(seed, int(u * 30)) - 0.5) * 0.2
        base = 4.4 - v / h * 1.4 + fold
        if kind == 'shirt':
            body = abs(u - w / 2) < w * 0.3 and v < h
            sleeve = v < h * 0.34 + (0.0 if abs(u - w / 2) < w * 0.3 else -abs(abs(u - w / 2) - w * 0.3) * 0.5) and v < h * 0.4
            if body or sleeve:
                if v < 0.05:
                    return rmp, base + 0.8
                return rmp, base
            return None
        if kind == 'trousers':
            if v < h * 0.25 or (v < h and abs(u - w / 2) > w * 0.07):
                return rmp, base - (0.6 if abs(u - w / 2) < w * 0.12 else 0)
            return None
        if kind == 'socks':
            if (u < w * 0.4 or u > w * 0.6) and (v < h * 0.75 or (u % (w * 0.5)) > w * 0.12):
                return rmp, base
            return None
        # llençol: la vora de baix fa ones
        if v < h - 0.06 * (1 + math.sin(u * 9 + seed - TAU * _T)):
            return rmp, base + (0.5 if v < 0.05 else 0) - (0.5 if u < 0.04 or w - u < 0.04 else 0)
        return None
    return f


def cable_y(x, h, sag):
    return h - sag * (1 - (x / WD) ** 2)


def wire(cv, zbuf, z, h, sag, col=(46, 32, 34)):
    n = int(2 * WD * F / z * 1.5) + 4
    for i in range(n + 1):
        x = -WD + 2 * WD * i / n
        px, py = proj(x, cable_y(x, h, sag), z)
        wput(cv, zbuf, px, py, z, col)


def estesa(cv, zbuf, z, h, sag, seed, gap=0.0):
    """Una corda de roba estesa d'una paret a l'altra (sense roba a |x| < gap)."""
    rnd = random.Random(seed)
    wire(cv, zbuf, z, h, sag, (70, 56, 50))
    x = -WD + rnd.uniform(0.2, 1.2)
    while x < WD - 0.6:
        kind = rnd.choice(['shirt', 'shirt', 'sheet', 'trousers', 'socks', 'sheet'])
        w, hh = {'shirt': (0.7, 0.7), 'sheet': (rnd.uniform(0.9, 1.5), rnd.uniform(0.9, 1.4)), 'trousers': (0.5, 1.0),
                 'socks': (0.28, 0.3)}[kind]
        if x + w > WD - 0.3:
            break
        if rnd.random() < 0.82 and (x > gap or x + w < -gap):
            top = cable_y(x + w / 2, h, sag)
            rmp = rnd.choice(CLOTH)
            billboard(cv, zbuf, x, top + 0.02, w, hh, z - 0.01, garment(kind, w, hh, rmp, rnd.randint(0, 99)))
            for px_ in (x + 0.04, x + w - 0.06):                    # pinces
                qx, qy = proj(px_, cable_y(px_, h, sag) + 0.04, z - 0.02)
                wput(cv, zbuf, qx, qy, z - 0.02, (200, 170, 120))
        x += w + rnd.uniform(0.15, 0.9)


def garlanda(cv, zbuf, z, h, sag, seed):
    """Una tira de bombetes (festa al barri)."""
    rnd = random.Random(seed)
    wire(cv, zbuf, z, h, sag)
    n = 18
    glows = []
    for i in range(1, n):
        x = -WD + 2 * WD * i / n
        px, py = proj(x, cable_y(x, h, sag) - 0.12, z)
        col = rnd.choice([(255, 214, 120), (255, 170, 90), (255, 236, 180), (250, 130, 90)])
        if _T:                                           # parpellegen, cadascuna al seu ritme
            m = 1 + int(hr(seed, i, 3) * 3)
            col = mix(col, (110, 60, 40), 0.7 * math.sin(math.pi * (m * _T)) ** 2 * (hr(seed, i, 4) < 0.6))
        wput(cv, zbuf, px, py, z, col)
        if z < 40:
            wput(cv, zbuf, px, py + 1, z, mix(col, (120, 60, 40), 0.4))
        if z < 25:                                       # de prop, la bombeta fa 2 píxels d'ample i el portalàmpades
            wput(cv, zbuf, px + 1, py, z, mix(col, (120, 60, 40), 0.2))
            wput(cv, zbuf, px, py - 1, z, (60, 44, 40))
        glows.append((px, py, col))
    for px, py, col in glows:
        cv.glow(px, py, max(4, 80 / z), col, 0.45)


GLYPHS = {'X': '#...#/#...#/.#.#./..#../.#.#./#...#/#...#'.split('/')}     # una X de veritat, per als rètols


def glyph_pixels(text, x0, y0, k=1, gap=1, space=None):
    """Píxels (x, y) d'un text amb la lletra de 4×7 de La Gavina, a escala k (cada punt, k×k píxels).
    Torna (conjunt de píxels, amplada)."""
    pix, x = set(), x0
    for ch in text:
        g = GLYPHS.get(ch) or FONT7.get(ch, FONT7[' '])
        w = len(g[0]) if ch != ' ' or space is None else space
        for j, row in enumerate(g):
            for ii, c in enumerate(row):
                if c == '#':
                    for a in range(k):
                        for b in range(k):
                            pix.add((int(x + ii * k + a), int(y0 + j * k + b)))
        x += (w + gap) * k
    return pix, x - gap * k - x0


def pancarta(cv, zbuf):
    """La pancarta del barri, penjada d'una paret a l'altra: ANELL DE BAIX, entre dues claus angleses."""
    z, h, sag = 12.6, 7.45, 0.25
    wire(cv, zbuf, z + 0.01, h + 0.35, 0.5)
    text = 'ANELL DE BAIX'
    k = 3
    bw, bh = 10.4, 1.3
    x0 = -bw / 2
    ax, ay = proj(x0, h, z)
    s = F / z
    _, tw = glyph_pixels(text, 0, 0, k, space=4)
    rows, _ = glyph_pixels(text, ax + (bw * s - tw) / 2, 0, k, space=4)

    def f(u, v):
        sagv = 0.12 * math.sin(u / bw * math.pi)            # la tela s'arrossega una mica al mig
        vv = v - sagv
        if vv < 0 or vv > bh - 0.05 * math.sin(u * 5):
            return None
        px = int(ax + u * s)
        py = int(vv * s - (bh * s - 7 * k) / 2)
        lvl = 4.2 - vv * 0.8 + 0.3 * math.sin(u * 3.1 - TAU * _T) - (0.8 if u < 0.06 or bw - u < 0.06 else 0)
        if vv < 0.08:
            return PAPER, lvl + 0.6
        if (px, py) in rows:
            # pintura a mà: el traç és més fosc a les vores de cada lletra
            edge = not ((px - 1, py) in rows and (px + 1, py) in rows and (px, py - 1) in rows and (px, py + 1) in rows)
            return RED, 3.6 - vv * 0.6 - (0.5 if edge else 0) + (hr(px, py, 21) - 0.5) * 0.3
        if (px - 1, py - 1) in rows:
            return PAPER, lvl - 1.0                         # la pintura ha calat i fa ombra a la tela
        if abs(vv - (bh - 0.14)) < 0.03:
            if int(u * s) % 4 < 2:
                return PAPER, lvl - 0.7                     # el repunt de la vora
        # dues claus angleses als costats
        for cu in (0.75, bw - 0.75):
            du, dv = (u - cu) / 0.42, (vv - bh / 2) / 0.42
            if abs(du) < 1.4 and abs(dv) < 1.4 and wrench(du * 0.7 - dv * 0.7, du * 0.7 + dv * 0.7):
                return WARN, 3.6
        return PAPER, lvl
    billboard(cv, zbuf, x0, h + 0.15, bw, bh + 0.3, z, f)


def figura(cv, zbuf, x, z, top, legs=None, h=1.68, seed=0, hair=(40, 26, 26)):
    """Una persona llunyana, de cara o d'esquena (a aquesta distància no se sap): pocs píxels, ben posats."""
    legs = legs or SUIT
    s = h / 1.68

    def f(u, v):
        uu = (u - 0.35) / s
        vv = (h - v) / s                                    # alçada des de terra
        if vv < 0.82:                                       # cames
            if abs(abs(uu) - 0.09) < 0.075 + (0.02 if vv < 0.08 else 0):
                return legs, 2.0 + vv
            return None
        if vv < 1.42:                                       # tronc i braços
            half = 0.2 - (1.42 - vv) * 0.05
            if abs(uu) < half:
                return top, 2.6 + (vv - 0.82) * 2.2
            if half <= abs(uu) < half + 0.07 and vv > 0.9:
                return top, 2.0 + (vv - 0.82) * 1.6
            return None
        if vv < 1.47 and abs(uu) < 0.05:
            return SKIN, 2.4
        d = math.hypot(uu, (vv - 1.57) * 1.05)
        if d < 0.115:
            return (hair if vv > 1.56 else mix(hair, (120, 80, 60), 0.5))
        return None
    billboard(cv, zbuf, x - 0.35, h, 0.7, h, z, f)
    # ombra als peus
    for k in range(-2, 3):
        px, py = proj(x + k * 0.1, 0, z)
        if 0 <= int(px) < W and 0 <= int(py) < H and z < zbuf[int(py)][int(px)] + 0.5:
            cv.darken(px, py, px, py, 0.6)


def wbox(cv, zbuf, x0, x1, y0, y1, z0, z1, fn):
    """Una capsa del món (alineada amb el carrer). fn(cara, a, b) → (rampa, nivell);
    cares: 'front' (a=x, b=y), 'side' (a=z, b=y), 'top' (a=x, b=z)."""
    corners = [proj(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]
    pxs = [c[0] for c in corners]
    pys = [c[1] for c in corners]
    for py in range(max(0, math.floor(min(pys))), min(H, math.ceil(max(pys)) + 1)):
        for px in range(max(0, math.floor(min(pxs))), min(W, math.ceil(max(pxs)) + 1)):
            dx = (px + 0.5 - CX) / F
            dy = (CY - py - 0.5) / F
            # el raig, en coordenades del carrer: x = dx t, y = CH + dy t - c t², z = t
            lo, hi, face = z0, z1, 'front'
            if abs(dx) > 1e-9:
                ta, tb = sorted((x0 / dx, x1 / dx))
                if ta > lo:
                    lo, face = ta, 'side'
                hi = min(hi, tb)
            if lo > hi:
                continue
            hit = None
            n = 12
            for i in range(n + 1):
                t = lo + (hi - lo) * i / n
                y = CH + dy * t - CURV * t * t
                if y0 <= y <= y1:
                    hit = (t, face if i == 0 else 'top', y)
                    break
            if not hit:
                continue
            t, fc, y = hit
            if fc == 'front':
                m = fn('front', dx * t, y)
            elif fc == 'side':
                m = fn('side', t, y)
            else:
                m = fn('top', dx * t, t)
            if m:
                wput(cv, zbuf, px, py, t, m[0], m[1])


def caixes(cv, zbuf):
    """Caixes, testos i un banc a les voreres, davant de les cases de prop."""
    def crate(rmp):
        def f(face, a, b):
            base = {'front': 3.0, 'side': 2.4, 'top': 4.2}[face]
            g = (a if face != 'side' else a) * 6
            lvl = base + (0.4 if int(g) % 2 else 0) - (1.0 if (b * 6) % 1 < 0.15 and face != 'top' else 0)
            return rmp, lvl
        return f

    def pot(face, a, b):
        if b > 0.38 or face == 'top':
            return LEAF, 2.8 + hr(int(a * 20), int(b * 20), 4) * 2.2
        return RUST, {'front': 3.0, 'side': 2.2}[face] + (0.8 if b > 0.32 else 0)

    for x0, x1, y1, z0, z1, f in ((-7.8, -6.9, 0.7, 10.2, 11.0, crate(WALNUT)), (-7.7, -7.0, 1.25, 10.3, 10.9, crate(OCHRE)),
                                  (-7.9, -7.3, 0.6, 15.0, 15.5, pot), (-7.9, -7.4, 0.55, 16.0, 16.4, pot),
                                  (7.0, 7.8, 0.75, 9.0, 9.9, crate(WALNUT)), (7.3, 7.9, 0.55, 12.4, 12.9, pot),
                                  (7.4, 7.9, 0.5, 13.3, 13.7, pot), (-7.9, -7.35, 0.6, 9.4, 9.9, pot)):
        wbox(cv, zbuf, x0, x1, 0.0, y1, z0, z1, f)


def retol(cv, zbuf, side, z, y1, w, h, text, rmp, ink, glow=None):
    """Un rètol que surt de la façana (de cara a la càmera), penjat d'un braç de ferro."""
    x0 = side * WD - (w if side > 0 else 0) - side * 0.15
    ax, ay = proj(x0, y1, z)
    s = F / z
    _, tw = glyph_pixels(text, 0, 0)
    th = 7
    pix, _ = glyph_pixels(text, ax + (w * s - tw) / 2, ay + (h * s - th) / 2)
    shadow = {(x + 1, y + 1) for x, y in pix} - pix

    def f(u, v):
        px, py = int(ax + u * s), int(ay + v * s)
        if (px, py) in pix:
            return ink
        if (px, py) in shadow:
            return rmp, 1.4
        edge = u < 0.06 or w - u < 0.06 or v < 0.06 or h - v < 0.06
        return rmp, (4.2 if v < 0.06 else 2.2) if edge else 3.2 - v * 0.8
    # el braç
    bx0, by0 = proj(side * WD, y1 + 0.18, z)
    bx1, by1 = proj(x0 + (w if side < 0 else 0), y1 + 0.18, z)
    for k in range(int(abs(bx1 - bx0)) + 1):
        wput(cv, zbuf, bx0 + (bx1 - bx0) * k / max(1, abs(bx1 - bx0)), by0, z, IRON, 3.2)
        wput(cv, zbuf, bx0 + (bx1 - bx0) * k / max(1, abs(bx1 - bx0)), by0 + 1, z, IRON, 1.6)
    billboard(cv, zbuf, x0, y1, w, h, z, f)
    if glow:
        cv.glow(ax + w * s / 2, ay + h * s / 2, w * s * 0.9, glow, 0.25)


def carrer(cv, zbuf):
    """Tot el que hi ha penjat i el que passa pel carrer, de lluny a prop."""
    for z, h, sag, sd in ((78, 15.5, 1.2, 7), (60, 14.0, 1.1, 6), (46, 12.6, 1.0, 5)):
        estesa(cv, zbuf, z, h, sag, sd)
    garlanda(cv, zbuf, 36, 12.2, 1.4, 4)
    for x, z, top, hh, sd in ((-2.6, 64, ROSE, 1.68, 1), (1.6, 58, MINT, 1.68, 2), (2.3, 58, OCHRE, 1.05, 3),
                              (-5.4, 50, BLUE, 1.68, 4), (5.8, 44, PAPER, 1.6, 5), (-0.8, 40, OCHRE, 1.7, 6),
                              (-1.4, 40, ROSE, 1.0, 7), (4.0, 34, MINT, 1.65, 8), (-6.0, 32, WARN, 1.6, 9)):
        figura(cv, zbuf, x, z, top, h=hh, seed=sd)
    retol(cv, zbuf, 1, 24.0, 3.9, 1.6, 0.7, 'BAR', ROSE, (255, 230, 170), (255, 160, 110))
    retol(cv, zbuf, -1, 21.0, 3.6, 1.9, 0.7, 'TALLER', MINT, (255, 236, 190), (150, 255, 200))
    caixes(cv, zbuf)
    # una pilota vermella, al costat de la xarranca
    bx, by = proj(-1.7, 0.16, 7.6)
    cv.darken(bx - 7, by + 3, bx + 9, by + 8, lambda x, y: 0.9 - math.hypot((x - bx - 1.5) / 8, (y - by - 6) / 2.6))
    cv.disc(bx, by, 6.1, 6.1, ROSE, lambda nx, ny: 3.6 - nx * 1.0 - ny * 1.6 + (0.5 if abs(nx * 0.7 + ny * 0.7) < 0.12 else 0), 0)
    for dx, dy, c in ((-3, -3, (255, 236, 220)), (-2, -3, (255, 214, 196)), (-3, -2, (255, 214, 196))):
        cv.flat(round(bx) + dx, round(by) + dy, c)                  # la lluentor
    for a in range(-5, 6):                                          # la llum rebotada del terra, a sota
        x = round(bx + a * 0.9)
        y = round(by + 5.4 - abs(a) * 0.35)
        if abs(a) < 4:
            cv.put(x, y, ROSE, 2.6, 0)
    retol(cv, zbuf, -1, 13.6, 3.25, 1.3, 0.62, 'PA', RUST, (255, 236, 190), (255, 190, 120))
    estesa(cv, zbuf, 30, 11.0, 0.9, 3)
    garlanda(cv, zbuf, 22.0, 9.6, 1.2, 9)
    estesa(cv, zbuf, 16.5, 8.9, 0.7, 2, gap=3.5)
    pancarta(cv, zbuf)


def resplendor(cv, zbuf):
    """El fons del carrer, on l'anell s'enfila, brilla: l'aire hi és daurat."""
    for py in range(0, 173):
        for px in range(160, 480):
            z = zbuf[py][px]
            if z > 30:
                d = math.hypot((px - CX) / 147, (py - 83) / 80)
                k = max(0.0, 1 - d) ** 1.5 * 0.45 * min(1.0, (z - 30) / 30)
                if k > B4[py & 3][px & 3] * 0.3:
                    cv.flat(px, py, mix(cv.get(px, py), (255, 232, 180), k))
    # la franja de llum del sostre
    cv.glow(CX, 0, 40, (255, 240, 200), 0.6)


def bg(cv, t=0.0):
    global _T
    _T = t % 1.0
    zbuf = scene(cv)
    resplendor(cv, zbuf)
    carrer(cv, zbuf)
    # la Vet, d'esquena, caminant cap al fons
    vet = person(VET, 'U', walk=1)
    fx, fy = 320, 339
    cv.darken(fx - 21, fy - 5, fx + 21, fy + 5, lambda x, y: 1.4 * (1 - math.hypot((x - fx) / 21, (y - fy) / 5)), dither=False)
    cv.img.alpha_composite(vet, (fx - 34, fy - 111))


PROPS = {}


def _ambient_frames(n=16):
    global _T
    base = Canvas(light=LIGHT)
    bg(base)
    frames = []
    for i in range(n):
        cv = Canvas(light=LIGHT)
        bg(cv, t=i / n)
        frames.append(diff(cv.img, base.img))
    _T = 0.0                                        # deixa l'estat del mòdul com el del fons quiet
    return frames


ANIMS = {'ambient': {'frames': _ambient_frames, 'frameDuration': 110}}
