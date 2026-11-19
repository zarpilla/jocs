"""
Final · L'Anell de Baix, EN PLA DE CINEMA (a 1×): el carrer del barri pobre de l'anell vist des del balcó d'un segon
pis, a la dreta del carrer, mirant avall i de biaix cap al fons on l'anell s'enfila i es perd entre la boirina
daurada (el dia artificial del sostre).

- **Contrast d'escala:** a la dreta, a tocar, la façana de la casa del balcó amb el filtre d'aire gros que la Vet hi
  va posar (la pala girant, la caixa i una clau anglesa pintada), en contrallum; a baix a la dreta, la barana i els
  testos del balcó, en silueta. La Vet, petita, al mig del carrer i d'esquena, camina cap al fons.
- **3/4:** la càmera és a un costat i girada: el carrer fuig en diagonal cap a un punt de fuga a la dreta del mig;
  de les cases de l'altra banda se'n veuen les façanes en escorç, de les caixes de la vorera el davant, el costat i
  la tapa, i les cordes de roba i les garlandes travessen el carrer en diagonal.
- **Línies que guien l'ull:** la canal del mig del carrer, les voreres i les cordes de roba porten de baix a la
  Vet i d'ella a la resplendor del fons; la roba estesa de la primera corda, gran i fosca, emmarca el quadre per dalt.
- **Llum:** la franja del sostre, càlida; la boirina daurada s'hi menja el fons (perspectiva atmosfèrica).

El quadre de text del final va al mig (≈145..495 × 155..222): la Vet és a sota i el rètol, a sobre.
Es dibuixa amb el traçador de raigs de sempre (final_anell_pla_comu.py: materials, cases, roba, rètols),
generalitzat a una càmera amb posició, gir (`YAW`) i picat (`PITCH`).
"""
import math
import random
from functools import lru_cache

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from PIL import Image
from hd.pix import Canvas, Light, B4, W, H, mix, STEEL, RUST, WARN, IRON, PAPER, WALNUT, RED, SUIT, SKIN
from hd640.draw_characters import person, VET
from hd640.rooms import final_anell_pla_comu as PL
from hd640.rooms.final_anell_pla_comu import (HAZE, ROSE, MINT, OCHRE, BLUE, LEAF, CLOTH, WD, HC, CURV, HAZE_Z,
                                              hr, diff, glyph_pixels, wrench, garment, mat_floor, mat_ceil)

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)
TAU = 2 * math.pi

# ─── La càmera ──────────────────────────────────────────────────────────────
# El món (metres): x de través (0 = el mig del carrer), y amunt (des del terra de l'anell, que puja z²/(2R)),
# z al llarg del carrer (0 = el balcó). Les parets de les cases són a x = ±WD.
EYE = (5.6, 4.2, 0.0)            # l'ull: al balcó d'un primer pis, a la dreta
YAW = -0.26                      # girada cap a l'esquerra (el carrer fuig cap a la dreta del mig)
PITCH = 0.10                     # mirant avall
F = 360.0                        # focal (píxels)
CX, CY = 320, 150                # centre òptic

_cy, _sy = math.cos(YAW), math.sin(YAW)
_cp, _sp = math.cos(PITCH), math.sin(PITCH)


def ray(px, py):
    """Direcció (unitària) del raig del píxel, al món."""
    x, y, z = (px - CX) / F, (CY - py) / F, 1.0
    y, z = y * _cp - z * _sp, y * _sp + z * _cp           # el picat
    x, z = x * _cy + z * _sy, -x * _sy + z * _cy          # el gir
    n = math.sqrt(x * x + y * y + z * z)
    return x / n, y / n, z / n


def vista(x, y, z):
    """Un punt del món (y des del terra) → coordenades de càmera."""
    dx, dy, dz = x - EYE[0], y + CURV * z * z - EYE[1], z - EYE[2]
    x1, z1 = dx * _cy - dz * _sy, dx * _sy + dz * _cy
    y2, z2 = dy * _cp + z1 * _sp, -dy * _sp + z1 * _cp
    return x1, y2, z2


def proj(x, y, z):
    """Punt del món → píxel."""
    a, b, c = vista(x, y, z)
    c = max(c, 1e-3)
    return CX + F * a / c, CY - F * b / c


def dist(x, y, z):
    a, b, c = vista(x, y, z)
    return math.sqrt(a * a + b * b + c * c)


def cast(px, py):
    """→ (tipus, distància, x, y, z) del primer que toca el raig: 'floor', 'wall' o 'ceil'."""
    dx, dy, dz = ray(px, py)
    ox, oy, oz = EYE
    best = None
    a = CURV * dz * dz
    if a > 1e-12:                                         # terra: oy + dy t = c (dz t)²
        t = (dy + math.sqrt(dy * dy + 4 * a * oy)) / (2 * a)
        best = ('floor', t)
        disc = dy * dy - 4 * a * (HC - oy)                # sostre: oy + dy t = HC + c (dz t)²
        if disc >= 0 and dy > 0:
            t = (dy - math.sqrt(disc)) / (2 * a)
            if 0 < t < best[1]:
                best = ('ceil', t)
    if abs(dx) > 1e-9:
        t = ((WD if dx > 0 else -WD) - ox) / dx
        z = oz + dz * t
        y = oy + dy * t - CURV * z * z
        if 0 < t < (best[1] if best else 1e9) and 0 <= y <= HC:
            best = ('wall', t)
    kind, t = best
    z = oz + dz * t
    return kind, t, ox + dx * t, oy + dy * t - CURV * z * z, z


# ─── El que s'hi afegeix: el filtre gros de la façana del balcó ─────────────

NEAR_FAN = (1, 7.2, 6.4, 1.55)          # costat, z, alçada, radi
NEAR_WRENCH = (1, 10.2, 7.5, 1.1, 2.6, (246, 206, 90))


def mat_wall(side, z, y):
    sd, zc, yc, r = NEAR_FAN
    if side == sd and abs(z - zc) < r + 0.4 and abs(y - yc) < r + 0.4:
        m = PL.mat_fan(z - zc, y - yc, r, z, spin=-1)
        if m:
            return m
    sd, zc, yc, sc, ang, col = NEAR_WRENCH
    if side == sd and abs(z - zc) < sc * 1.3 and abs(y - yc) < sc * 1.3:
        du, dv = (z - zc) / sc, (y - yc) / sc
        c, sn = math.cos(ang), math.sin(ang)
        if wrench(du * c + dv * sn, -du * sn + dv * c) and hr(int(z * 9), int(y * 9), 3) > 0.12:
            return 'paint', col
    return PL.mat_wall(side, z, y)


# ─── El traçat ──────────────────────────────────────────────────────────────

def hazeify(cv, px, py, d):
    """Boirina daurada: barreja en esglaons (amb trama) cap al color de l'aire del fons."""
    k = (1 - math.exp(-d / HAZE_Z)) * 0.92
    kq = math.floor(k * 7 + B4[py & 3][px & 3] - 0.5) / 7
    if kq > 0:
        hz = HAZE[min(8, max(0, int(4.6 + (VP[1] - py) * 0.015 - abs(px - VP[0]) * 0.003 + k * 2.4)))]
        cv.flat(px, py, mix(cv.get(px, py), hz, kq))


def wput(cv, zbuf, px, py, d, rmp, lvl=None):
    """Píxel d'un objecte del món a distància d: amagat si hi ha alguna cosa més a prop, i amb boirina."""
    px, py = int(round(px)), int(round(py))
    if not (0 <= px < W and 0 <= py < H) or d >= zbuf[py][px]:
        return
    if lvl is None:
        cv.flat(px, py, rmp)
    else:
        cv.put(px, py, rmp, lvl, 0)
    hazeify(cv, px, py, d)
    zbuf[py][px] = d


@lru_cache(maxsize=None)
def _casts():
    return tuple(tuple(cast(px, py) for px in range(W)) for py in range(H))


VP = proj(0.0, 3.0, 70.0)                  # (aprox.) on fuig el carrer: d'allà ve la claror


def scene(cv):
    zbuf = [[0.0] * W for _ in range(H)]
    casts = _casts()
    for py in range(H):
        row = casts[py]
        for px in range(W):
            kind, d, a, b, z = row[px]
            if kind == 'floor':
                rmp, lvl = mat_floor(a, z)
                if rmp != 'paint':
                    lvl += 0.8 * max(0.0, 1 - abs(a) / 7)          # la franja de sol del sostre
                    lvl -= 1.6 * max(0.0, 1 - (WD - abs(a)) / 0.7) ** 2   # ombra al peu de les parets
                    if abs(a) < 1.2:                                 # el terra polit hi fa un reflex
                        lvl += 0.5 * (1 - abs(a) / 1.2) * (hr(int(z * 2), 0, 3) > 0.3)
            elif kind == 'wall':
                side = -1 if a < 0 else 1
                rmp, lvl = mat_wall(side, z, b)
                if rmp != 'paint':
                    lvl += 0.04 * b + (0.3 if side < 0 else -0.5)  # la façana de l'esquerra mira la llum
                    lvl -= 1.4 * max(0.0, 1 - b / 0.6) ** 2         # brutícia i ombra a peu de carrer
                    if rmp not in (STEEL, IRON, PL.GRAY, PL.WINLIT, PL.SIL, LEAF) and 0.6 < b < 2.0:
                        if hr(int(z * 3), 1, 5) > 0.7:
                            lvl -= 0.35                              # regalims
                    if side > 0:                                      # la de la dreta, de prop: a contrallum
                        lvl -= 1.6 * max(0.0, 1 - (z - 5) / 12)
            else:
                rmp, lvl = mat_ceil(a, z)
            zbuf[py][px] = d
            if rmp == 'paint':
                cv.flat(px, py, mix(lvl, (120, 90, 70), 0.25 * hr(px // 2, py // 2, 4)))
            else:
                cv.put(px, py, rmp, lvl, 0)
            hazeify(cv, px, py, d)
    return zbuf


# ─── Coses del carrer (plans de z constant, travessant el carrer) ─────────

def billboard(cv, zbuf, x0, y1, w, h, z, fn):
    """Una cosa plana al pla z (x0..x0+w, de y1 cap avall h metres). fn(u, v) amb u, v en metres (v cap avall) →
    (rampa, nivell), color RGB o None."""
    pts = [proj(x, y, z) for x in (x0, x0 + w) for y in (y1, y1 - h)]
    us, vs = [p[0] for p in pts], [p[1] for p in pts]
    ox, oy, oz = EYE
    lift = CURV * z * z
    for py in range(max(0, math.floor(min(vs))), min(H, math.ceil(max(vs)) + 1)):
        for px in range(max(0, math.floor(min(us))), min(W, math.ceil(max(us)) + 1)):
            dx, dy, dz = ray(px + 0.5, py + 0.5)
            if dz <= 1e-6:
                continue
            t = (z - oz) / dz
            u, v = ox + dx * t - x0, y1 - (oy + dy * t - lift)
            if 0 <= u <= w and 0 <= v <= h:
                m = fn(u, v)
                if m is None:
                    continue
                if isinstance(m[0], list):
                    wput(cv, zbuf, px, py, t, m[0], m[1])
                else:
                    wput(cv, zbuf, px, py, t, m)


def cable_y(x, h, sag):
    return h - sag * (1 - (x / WD) ** 2)


def wire(cv, zbuf, z, h, sag, col=(46, 32, 34), gruix=1):
    a, b = proj(-WD, h, z), proj(WD, h, z)
    n = int(math.hypot(b[0] - a[0], b[1] - a[1]) * 1.5) + 4
    for i in range(n + 1):
        x = -WD + 2 * WD * i / n
        y = cable_y(x, h, sag)
        px, py = proj(x, y, z)
        d = dist(x, y, z)
        for k in range(gruix):
            wput(cv, zbuf, px, py + k, d, col)


def estesa(cv, zbuf, z, h, sag, seed, gap=0.0, fosc=0.0):
    """Una corda de roba estesa d'una paret a l'altra (sense roba a |x| < gap). `fosc`: nivells de menys
    (la de prop, a contrallum)."""
    rnd = random.Random(seed)
    wire(cv, zbuf, z, h, sag, (70, 56, 50), gruix=2 if z < 10 else 1)
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
            g = garment(kind, w, hh, rmp, rnd.randint(0, 99))
            fn = g if not fosc else (lambda u, v, g=g: (lambda m: m if m is None else (m[0], m[1] - fosc))(g(u, v)))
            billboard(cv, zbuf, x, top + 0.02, w, hh, z - 0.01, fn)
            for px_ in (x + 0.04, x + w - 0.06):                    # pinces
                y = cable_y(px_, h, sag) + 0.04
                qx, qy = proj(px_, y, z - 0.02)
                wput(cv, zbuf, qx, qy, dist(px_, y, z) - 0.02, (200, 170, 120) if not fosc else (90, 70, 50))
        x += w + rnd.uniform(0.15, 0.9)


def garlanda(cv, zbuf, z, h, sag, seed):
    """Una tira de bombetes (festa al barri)."""
    rnd = random.Random(seed)
    wire(cv, zbuf, z, h, sag)
    n = 18
    glows = []
    for i in range(1, n):
        x = -WD + 2 * WD * i / n
        y = cable_y(x, h, sag) - 0.12
        px, py = proj(x, y, z)
        d = dist(x, y, z)
        col = rnd.choice([(255, 214, 120), (255, 170, 90), (255, 236, 180), (250, 130, 90)])
        if PL._T:                                        # parpellegen, cadascuna al seu ritme
            m = 1 + int(hr(seed, i, 3) * 3)
            col = mix(col, (110, 60, 40), 0.7 * math.sin(math.pi * (m * PL._T)) ** 2 * (hr(seed, i, 4) < 0.6))
        wput(cv, zbuf, px, py, d, col)
        if d < 40:
            wput(cv, zbuf, px, py + 1, d, mix(col, (120, 60, 40), 0.4))
        if d < 25:
            wput(cv, zbuf, px + 1, py, d, mix(col, (120, 60, 40), 0.2))
            wput(cv, zbuf, px, py - 1, d, (60, 44, 40))
        glows.append((px, py, col, d))
    for px, py, col, d in glows:
        if 0 <= int(px) < W and 0 <= int(py) < H and zbuf[int(py)][int(px)] >= d - 0.5:
            cv.glow(px, py, max(4, 80 / d), col, 0.45)


def pancarta(cv, zbuf):
    """La pancarta del barri, penjada d'una paret a l'altra: ANELL DE BAIX, entre dues claus angleses."""
    z, h = 20.0, 7.9
    wire(cv, zbuf, z + 0.01, h + 0.35, 0.5)
    text = 'ANELL DE BAIX'
    k = 3
    bw, bh = 10.4, 1.3
    x0 = -bw / 2
    _, tw = glyph_pixels(text, 0, 0, k, space=4)
    rows, _ = glyph_pixels(text, (bw * 40 - tw) / 2, 0, k, space=4)    # (la lletra en una graella de 40 px/m)

    def f(u, v):
        sagv = 0.12 * math.sin(u / bw * math.pi)
        vv = v - sagv
        if vv < 0 or vv > bh - 0.05 * math.sin(u * 5):
            return None
        gx = int(u * 40)
        gy = int(vv * 40 - (bh * 40 - 7 * k) / 2)
        lvl = 4.2 - vv * 0.8 + 0.3 * math.sin(u * 3.1 - TAU * PL._T) - (0.8 if u < 0.06 or bw - u < 0.06 else 0)
        if vv < 0.08:
            return PAPER, lvl + 0.6
        if (gx, gy) in rows:
            edge = not ((gx - 1, gy) in rows and (gx + 1, gy) in rows and (gx, gy - 1) in rows and (gx, gy + 1) in rows)
            return RED, 3.6 - vv * 0.6 - (0.5 if edge else 0) + (hr(gx, gy, 21) - 0.5) * 0.3
        if (gx - 1, gy - 1) in rows:
            return PAPER, lvl - 1.0
        if abs(vv - (bh - 0.14)) < 0.03 and gx % 4 < 2:
            return PAPER, lvl - 0.7
        for cu in (0.75, bw - 0.75):
            du, dv = (u - cu) / 0.42, (vv - bh / 2) / 0.42
            if abs(du) < 1.4 and abs(dv) < 1.4 and wrench(du * 0.7 - dv * 0.7, du * 0.7 + dv * 0.7):
                return WARN, 3.6
        return PAPER, lvl
    billboard(cv, zbuf, x0, h + 0.15, bw, bh + 0.3, z, f)


def figura(cv, zbuf, x, z, top, legs=None, h=1.68, seed=0, hair=(40, 26, 26)):
    """Una persona llunyana: pocs píxels, ben posats."""
    legs = legs or SUIT
    s = h / 1.68

    def f(u, v):
        uu = (u - 0.35) / s
        vv = (h - v) / s
        if vv < 0.82:
            if abs(abs(uu) - 0.09) < 0.075 + (0.02 if vv < 0.08 else 0):
                return legs, 2.0 + vv
            return None
        if vv < 1.42:
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
    for k in range(-2, 3):
        px, py = proj(x + k * 0.1, 0, z)
        if 0 <= int(px) < W and 0 <= int(py) < H and dist(x, 0, z) < zbuf[int(py)][int(px)] + 0.5:
            cv.darken(px, py, px, py, 0.6)


def wbox(cv, zbuf, x0, x1, y0, y1, z0, z1, fn):
    """Una capsa del món (alineada amb el carrer; el terra, pla a la seva z). fn(cara, a, b) → (rampa, nivell);
    cares: 'front' (a=x, b=y), 'side' (a=z, b=y), 'top' (a=x, b=z)."""
    lift = CURV * ((z0 + z1) / 2) ** 2
    corners = [proj(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]
    pxs = [c[0] for c in corners]
    pys = [c[1] for c in corners]
    ox, oy, oz = EYE
    for py in range(max(0, math.floor(min(pys))), min(H, math.ceil(max(pys)) + 1)):
        for px in range(max(0, math.floor(min(pxs))), min(W, math.ceil(max(pxs)) + 1)):
            d = ray(px + 0.5, py + 0.5)
            lo, hi, face = 0.0, 1e9, None
            for axis, (a0, a1), o, nm in ((0, (x0, x1), ox, 'side'), (1, (y0 + lift, y1 + lift), oy, 'top'),
                                          (2, (z0, z1), oz, 'front')):
                if abs(d[axis]) < 1e-9:
                    if not a0 <= o <= a1:
                        lo = hi + 1
                    continue
                ta, tb = sorted(((a0 - o) / d[axis], (a1 - o) / d[axis]))
                if ta > lo:
                    lo, face = ta, nm
                hi = min(hi, tb)
            if lo > hi or face is None:
                continue
            X, Y, Z = ox + d[0] * lo, oy + d[1] * lo - lift, oz + d[2] * lo
            m = fn(face, X if face != 'side' else Z, Y if face != 'top' else Z)
            if m:
                wput(cv, zbuf, px, py, lo, m[0], m[1])


def caixes(cv, zbuf):
    """Caixes, testos i un banc a les voreres."""
    def crate(rmp):
        def f(face, a, b):
            base = {'front': 2.6, 'side': 3.4, 'top': 4.2}[face]
            lvl = base + (0.4 if int(a * 6) % 2 else 0) - (1.0 if (b * 6) % 1 < 0.15 and face != 'top' else 0)
            return rmp, lvl
        return f

    def pot(face, a, b):
        if b > 0.38 or face == 'top':
            return LEAF, 2.8 + hr(int(a * 20), int(b * 20), 4) * 2.2
        return RUST, {'front': 2.4, 'side': 3.0}[face] + (0.8 if b > 0.32 else 0)

    for x0, x1, y1, z0, z1, f in ((-7.8, -6.9, 0.7, 10.2, 11.0, crate(WALNUT)), (-7.7, -7.0, 1.25, 10.3, 10.9, crate(OCHRE)),
                                  (-7.9, -7.3, 0.6, 15.0, 15.5, pot), (-7.9, -7.4, 0.55, 16.0, 16.4, pot),
                                  (-7.9, -7.35, 0.6, 9.4, 9.9, pot), (-7.8, -6.8, 0.8, 22.0, 23.2, crate(WALNUT)),
                                  (6.9, 7.8, 0.75, 13.0, 13.9, crate(WALNUT)), (7.3, 7.9, 0.55, 16.4, 16.9, pot),
                                  (7.4, 7.9, 0.5, 17.3, 17.7, pot), (7.0, 7.8, 1.1, 24.0, 24.8, crate(OCHRE))):
        wbox(cv, zbuf, x0, x1, 0.0, y1, z0, z1, f)


def retol(cv, zbuf, side, z, y1, w, h, text, rmp, ink, glow=None):
    """Un rètol que surt de la façana (al pla z), penjat d'un braç de ferro. La lletra, en una graella de 40 px/m."""
    x0 = side * WD - (w if side > 0 else 0) - side * 0.15
    G = 40
    _, tw = glyph_pixels(text, 0, 0)
    pix, _ = glyph_pixels(text, (w * G - tw) / 2, (h * G - 7) / 2)
    shadow = {(x + 1, y + 1) for x, y in pix} - pix

    def f(u, v):
        gx, gy = int(u * G), int(v * G)
        if (gx, gy) in pix:
            return ink
        if (gx, gy) in shadow:
            return rmp, 1.4
        edge = u < 0.06 or w - u < 0.06 or v < 0.06 or h - v < 0.06
        return rmp, (4.2 if v < 0.06 else 2.2) if edge else 3.2 - v * 0.8
    a, b = proj(side * WD, y1 + 0.18, z), proj(x0 + (w if side < 0 else 0), y1 + 0.18, z)
    n = int(math.hypot(b[0] - a[0], b[1] - a[1])) + 1
    d = dist(side * WD, y1, z)
    for k in range(n + 1):
        wput(cv, zbuf, a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n, d, IRON, 3.2)
        wput(cv, zbuf, a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n + 1, d, IRON, 1.6)
    billboard(cv, zbuf, x0, y1, w, h, z, f)
    if glow:
        gx, gy = proj(x0 + w / 2, y1 - h / 2, z)
        cv.glow(gx, gy, w * F / d * 0.9, glow, 0.25)


def carrer(cv, zbuf):
    """Tot el que hi ha penjat i el que passa pel carrer, de lluny a prop."""
    for z, h, sag, sd in ((78, 15.5, 1.2, 7), (60, 14.0, 1.1, 6), (46, 12.6, 1.0, 5)):
        estesa(cv, zbuf, z, h, sag, sd)
    garlanda(cv, zbuf, 36, 12.2, 1.4, 4)
    for x, z, top, hh, sd in ((-2.6, 64, ROSE, 1.68, 1), (1.6, 58, MINT, 1.68, 2), (2.3, 58, OCHRE, 1.05, 3),
                              (-5.4, 50, BLUE, 1.68, 4), (5.8, 44, PAPER, 1.6, 5), (-0.8, 40, OCHRE, 1.7, 6),
                              (-1.4, 40, ROSE, 1.0, 7), (4.0, 34, MINT, 1.65, 8), (-6.0, 32, WARN, 1.6, 9)):
        figura(cv, zbuf, x, z, top, h=hh, seed=sd)
    retol(cv, zbuf, 1, 28.0, 3.9, 1.6, 0.7, 'BAR', ROSE, (255, 230, 170), (255, 160, 110))
    retol(cv, zbuf, -1, 25.0, 3.6, 1.9, 0.7, 'TALLER', MINT, (255, 236, 190), (150, 255, 200))
    retol(cv, zbuf, -1, 16.6, 3.25, 1.3, 0.62, 'PA', RUST, (255, 236, 190), (255, 190, 120))
    caixes(cv, zbuf)
    estesa(cv, zbuf, 30, 11.0, 0.9, 3)
    garlanda(cv, zbuf, 22.0, 10.4, 1.2, 9)
    pancarta(cv, zbuf)


def pilota(cv, zbuf):
    """Una pilota vermella, a la vora de la xarranca."""
    x, z, r = -2.6, 12.4, 0.16
    bx, by = proj(x, r, z)
    R = r * F / dist(x, r, z)
    cv.darken(bx - R * 1.2, by + R * 0.5, bx + R * 1.8, by + R * 1.4,
              lambda X, Y: 0.9 - math.hypot((X - bx - R * 0.3) / (R * 1.4), (Y - by - R) / (R * 0.45)))
    cv.disc(bx, by, R, R, ROSE, lambda nx, ny: 3.6 - nx * 1.0 - ny * 1.6, 0)
    cv.flat(round(bx - R * 0.4), round(by - R * 0.4), (255, 230, 214))


def resplendor(cv, zbuf):
    """El fons del carrer, on l'anell s'enfila, brilla: l'aire hi és daurat."""
    vx, vy = VP
    for py in range(0, H):
        for px in range(0, W):
            d = zbuf[py][px]
            if d > 30:
                q = math.hypot((px - vx) / 150, (py - vy + 40) / 90)
                k = max(0.0, 1 - q) ** 1.5 * 0.45 * min(1.0, (d - 30) / 30)
                if k > B4[py & 3][px & 3] * 0.3:
                    cv.flat(px, py, mix(cv.get(px, py), (255, 232, 180), k))


# ─── El primer pla: la roba de la corda del balcó i la barana ──────────────

def balco(cv, zbuf):
    """El balcó d'on mirem: la llosa, la barana de ferro i dos testos, a baix a la dreta, en silueta."""
    def rail(face, a, b):
        return IRON, {'front': 0.8, 'side': 1.2, 'top': 1.5}[face]

    def slab(face, a, b):
        return PL.PLASTER, {'front': 1.0, 'side': 0.8, 'top': 1.6}[face]
    y0 = EYE[1] - 1.55                                    # el terra del balcó
    wbox(cv, zbuf, 6.18, 6.32, y0 + 0.92, y0 + 1.04, 0.6, 3.2, rail)
    wbox(cv, zbuf, 6.2, 8.0, y0 + 0.92, y0 + 1.04, 3.1, 3.22, rail)
    for zz in (1.4, 2.2, 3.0):                                      # els barrots
        wbox(cv, zbuf, 6.22, 6.28, y0, y0 + 1.0, zz, zz + 0.05, rail)
    for x in (6.7, 7.3):
        wbox(cv, zbuf, x - 0.03, x + 0.03, y0, y0 + 1.0, 3.12, 3.2, rail)

    def pot(face, a, b):
        if b > y0 + 0.36 or face == 'top':
            return LEAF, 1.0 + hr(int(a * 30), int(b * 30), 4) * 1.4
        return RUST, {'front': 1.2, 'side': 1.6}[face]
    wbox(cv, zbuf, 6.5, 6.9, y0, y0 + 0.4, 2.5, 2.9, pot)
    # les fulles del test, que sobresurten de la barana
    rnd = random.Random(31)
    for _ in range(140):
        a, L = rnd.uniform(0.6, 2.5), rnd.uniform(0.25, 0.7)
        bx, bz = 6.7 + rnd.uniform(-0.15, 0.15), 2.7 + rnd.uniform(-0.1, 0.1)
        for k in range(10):
            s = k / 9 * L
            X, Y, Z = bx + math.cos(a) * s * 0.5, y0 + 0.4 + math.sin(a) * s, bz - math.cos(a) * s * 0.6
            px, py = proj(X, Y, Z)
            wput(cv, zbuf, px, py, dist(X, Y, Z), LEAF, 0.8 + k * 0.2)
            wput(cv, zbuf, px + 1, py, dist(X, Y, Z), LEAF, 0.6 + k * 0.15)


def roba_de_prop(cv, zbuf):
    """La corda del balcó, de la nostra façana a la de l'altra banda: roba gran, a contrallum."""
    estesa(cv, zbuf, 6.0, 6.7, 0.7, 12, fosc=1.6)


# ─── La Vet ─────────────────────────────────────────────────────────────────

VET_AT = (0.3, 6.6)                    # x, z: al mig del carrer, una mica a l'esquerra de la canal


@lru_cache(maxsize=None)
def _vet():
    img = person(VET, 'U', walk=1)
    x, z = VET_AT
    k = 1.66 * F / dist(x, 0.8, z) / 106
    w, h = max(1, round(img.width * k)), max(1, round(img.height * k))
    return img.resize((w, h), Image.Resampling.BOX), k


def vet(cv, zbuf):
    img, k = _vet()
    x, z = VET_AT
    fx, fy = proj(x, 0, z)
    # l'ombra: la franja del sostre és just a sobre; una taca curta i rodona
    rx, ry = 20 * k, 5 * k
    cv.darken(fx - rx, fy - ry, fx + rx, fy + ry, lambda X, Y: 1.4 * (1 - math.hypot((X - fx) / rx, (Y - fy) / ry)),
              dither=False)
    ox, oy = round(fx - 33 * k), round(fy - 113 * k)
    cv.img.alpha_composite(img, (ox, oy))
    cv.P = cv.img.load()
    d = dist(x, 0.8, z)
    for j in range(img.height):                                          # (la boirina, poca, també a ella)
        for i in range(img.width):
            if img.getpixel((i, j))[3] > 128 and 0 <= ox + i < W and 0 <= oy + j < H:
                zbuf[oy + j][ox + i] = d


def bg(cv, t=0.0):
    PL._T = t % 1.0
    zbuf = scene(cv)
    resplendor(cv, zbuf)
    carrer(cv, zbuf)
    pilota(cv, zbuf)
    vet(cv, zbuf)
    roba_de_prop(cv, zbuf)
    balco(cv, zbuf)
    # la claror de la franja del sostre, a dalt, i una vinyeta suau als cantons
    gx, gy = proj(0.0, HC, 40.0)
    cv.glow(gx, max(0, gy), 60, (255, 240, 200), 0.35)
    P = cv.P
    for y in range(H):
        for x in range(W):
            q = math.hypot((x - 330) / 420, (y - 200) / 260)
            k = max(0.0, q - 0.62) * 1.3
            if k > 0:
                o = P[x, y]
                m = max(0.0, 1 - k)
                P[x, y] = (int(o[0] * m), int(o[1] * m), int(o[2] * m), 255)


PROPS = {}


@lru_cache(maxsize=None)
def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv.img


def _ambient_frames(n=16):
    base = _base()
    frames = []
    for i in range(n):
        cv = Canvas(light=LIGHT)
        bg(cv, t=i / n)
        frames.append(diff(cv.img, base))
    PL._T = 0.0                                     # deixa l'estat com el del fons quiet
    return frames


ANIMS = {'ambient': {'frames': _ambient_frames, 'frameDuration': 110}}
