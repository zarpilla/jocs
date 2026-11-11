"""
Final · La fugida, a 640×360 (vegeu hd/rooms/final_llancadora.py, la de 480×270): la llançadora vella (la de
l'hangar, rovellada i apedaçada, amb el tub de ferro-9 nou que brilla al ventre) travessa la nit amb el motor encès,
d'un blau de ferro-9. A sota, la cara de nit de la Terra amb les ciutats enceses; a la dreta, el sol que surt per la
vora. Darrere, petita i llunyana, La Gavina, i l'estela que en surt. A la finestreta, la llum càlida de la cabina
(la Vet és a dins).
  - la mateixa composició ×4/3; la Terra de nit, calculada a 640 amb una octava més (costes i núvols més fins);
  - la llançadora, redibuixada: planxes de 23 píxels amb reblons, pedaços més grans, el tub de ferro-9 de 7 píxels
    de gruix, la Vet de 15×15 a la finestreta (a 480, d'11×11), el rètol «L-1» de 6 píxels;
  - la flama i l'estela, a la mida de 640.
Pantalla sencera (sense barra de verbs).
"""
import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

import math
import random
from functools import lru_cache

from hd.pix import Canvas, Light, B4, W, H, hr, mix, ramp, COPPER, RUST, TEAL, PAPER
from hd640.rooms.proleg_gavina import espai, gavina, vinyeta, Noise, OCEAN, LAND, CLOUD, ATMO
from hd.rooms.fabrica_moll import OLDHULL, F9

K = 4 / 3                           # 480 → 640

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)

CABIN = ramp((20, 10, 14), (46, 22, 22), (86, 42, 28), (140, 72, 36), (196, 116, 56), (240, 170, 90), n=7)
DAWN = ramp((40, 10, 20), (120, 36, 30), (210, 90, 40), (250, 160, 70), (255, 220, 150), (255, 250, 230), n=8)
FLAME = ramp((10, 20, 60), (24, 60, 140), (50, 120, 220), (110, 190, 255), (190, 236, 255), (250, 254, 255), n=8)
NIGHTSEA = ramp((2, 4, 12), (4, 8, 22), (8, 16, 36), (14, 26, 54), (24, 42, 78), n=6)

N_LAND, N_CLOUD, N_CITY = Noise(191), Noise(192), Noise(193)
NLAND = ramp((4, 6, 8), (10, 12, 14), (18, 20, 20), (30, 30, 28), (46, 44, 38), (66, 62, 50), n=6)

EX, EY, ER = 307, 960, 720          # la Terra (només se'n veu el casquet)
SX, SY = 581, 0                     # el sol: es calcula sobre la vora
SUN = (0.80, 0.42, -0.42)
_l = math.sqrt(sum(c * c for c in SUN))
SUN = tuple(c / _l for c in SUN)

NX, NY, ANG = 539, 76, -0.13        # morro de la llançadora i inclinació (puja cap a la dreta)
NY0 = NY
TAU = 2 * math.pi
_T = 0.0                            # temps del bucle d'animació (0..1); t=0 és el fons quiet
LEN, RAD = 200, 25
GVX, GVY = 72, 59                   # La Gavina, lluny


def blend(cv, x, y, col, a):
    """Barreja el píxel (x, y) cap a `col` (si és dins del llenç)."""
    x, y = round(x), round(y)
    if 0 <= x < cv.w and 0 <= y < cv.h and a > 0:
        cv.flat(x, y, mix(cv.get(x, y), col, min(1.0, a)))


def limb_y(x):
    return EY - math.sqrt(max(0.0, ER * ER - (x - EX) ** 2))


def _col(rmp, lvl, x, y):
    """El color que posaria `Canvas.put(x, y, rmp, lvl, 0)` (per desar-lo a la memòria cau)."""
    i = math.floor(lvl + B4[y & 3][x & 3] - 0.5)
    return rmp[max(0, min(len(rmp) - 1, i))]


# ─── La Terra, de nit ───────────────────────────────────────────────────────

@lru_cache(maxsize=None)
def _terra_nit_ops():
    """La Terra de nit, desada: ('p', x, y, color) per als píxels fixos, ('c', x, y, color) per a les llums de ciutat
    que titil·len i les guspires de les ciutats grosses (que es dibuixen al final)."""
    ops, glows = [], []
    sx, sy = SX, limb_y(SX)
    HALO, RIM = 21, 16                                       # (16 i 12 a 480)
    for y in range(int(EY - ER) - HALO - 2, H):
        for x in range(W):
            nx, ny = (x - EX) / ER, (y - EY) / ER
            dd = nx * nx + ny * ny
            if dd > 1:
                d = (math.sqrt(dd) - 1) * ER
                if d < HALO:
                    ds = math.hypot(x - sx, y - sy)
                    sun = max(0.0, 1 - ds / 347)
                    a = (1 - d / HALO) ** 2.4 * (0.16 + 1.1 * sun ** 1.6)
                    if a > B4[y & 3][x & 3] * 0.8:
                        rmp = DAWN if sun > 0.55 and d < (5 + sun * 6) * K else ATMO
                        ops.append(('p', x, y, _col(rmp, 1.0 + a * 4.5 + sun * 1.5, x, y)))
                continue
            nz = math.sqrt(1 - dd)
            diff = nx * SUN[0] + ny * SUN[1] + nz * SUN[2]
            lon = math.atan2(nx, nz) * 9.0
            lat = math.asin(max(-1, min(1, ny))) * 9.0
            land = N_LAND.fbm(lon + 3.1, lat * 1.6 + 1.7, 6)
            cloud = N_CLOUD.fbm(lon * 1.3 + math.sin(lat * 3) * 0.6, lat * 4.0, 6)
            cloud = max(0.0, (cloud - 0.5) * 3.0)
            day = max(0.0, min(1.0, diff * 5.0 + 0.2))
            rim = (1 - math.sqrt(dd)) * ER                       # px fins a la vora
            sunk = max(0.0, 1 - math.hypot(x - sx, y - sy) / 373)
            moon = 0.5 + 0.7 * nz
            if land > 0.57:
                rmp, lvl = NLAND, 1.0 + moon * 0.9 + (land - 0.57) * 3
            else:
                rmp, lvl = NIGHTSEA, 1.2 + moon * 1.4 + (land - 0.5) * 2.5
                if land > 0.55:
                    lvl += 0.4                                   # la plataforma de la costa, una mica més clara
            c = cloud - 0.38 - (B4[y & 3][x & 3] - 0.5) * 0.35
            if c > 0:
                rmp, lvl = CLOUD, 0.6 + moon * 0.9 + min(cloud, 1.5) * 0.9
            if day > 0:
                if rmp is CLOUD:
                    if day < 0.7:
                        rmp, lvl = DAWN, 1.0 + day * 6
                    else:
                        lvl += day * 5.0
                elif rmp is NLAND:
                    rmp, lvl = LAND, lvl + day * 3.5
                else:
                    rmp, lvl = OCEAN, lvl + day * 3.5
            # vora: la boirina de l'atmosfera, blava, i daurada cap al sol
            if rim < RIM:
                k = (1 - rim / RIM) ** 1.6
                if k > B4[y & 3][x & 3] * 0.9:
                    if sunk > 0.45 and k > 0.55:
                        rmp, lvl = DAWN, 2.0 + k * 2.5 + sunk * 2.5
                    else:
                        rmp, lvl = ATMO, 0.6 + k * 1.6 + sunk * 3.0
            col = _col(rmp, lvl, x, y)
            # ciutats (al costat de nit): constel·lacions a les costes i als rius
            if day < 0.12 and rmp in (NLAND, NIGHTSEA) and land > 0.555:
                coast = max(0.0, 1 - (land - 0.57) * 7) if land > 0.57 else 0.5
                blob = N_CITY.fbm(lon * 2.2, lat * 4.4, 3)
                dens = max(0.0, blob - 0.52) * 3.2 * coast
                cc = hr(x, y, 5)
                if cc < dens * 0.55:
                    city = (255, 220, 140) if cc < dens * 0.14 else (214, 132, 60) if cc < dens * 0.35 else (130, 74, 46)
                    ops.append(('c' if hr(x, y, 8) < 0.35 else 'p', x, y, city))
                    if cc < dens * 0.04:
                        glows.append((x, y))
                    continue
            elif day < 0.12 and rmp is CLOUD and N_CITY.fbm(lon * 2.2, lat * 4.4, 3) > 0.6 and hr(x, y, 9) < 0.25:
                col = mix(col, (200, 130, 80), 0.4)              # ciutat sota el núvol
            ops.append(('p', x, y, col))
    # línia d'atmosfera a la vora, que s'encén cap al sol
    seen = set()
    for a in range(0, 4800):
        th = math.radians(a / 13.333)
        x, y = EX + math.cos(th) * (ER + 0.5), EY + math.sin(th) * (ER + 0.5)
        if 0 <= x < W and 0 <= y < H and (int(x), int(y)) not in seen:
            seen.add((int(x), int(y)))
            sun = max(0.0, 1 - math.hypot(x - sx, y - sy) / 400)
            ops.append(('p', int(x), int(y), mix(ATMO[2], (255, 200, 120) if sun > 0.6 else ATMO[5], min(1, 0.25 + sun * 1.2))))
    return tuple(ops), tuple(glows)


def terra_nit(cv):
    ops, glows = _terra_nit_ops()
    P = cv.P
    for k, x, y, col in ops:
        if k == 'c' and _T:                                     # llumetes que titil·len
            m = 1 + int(hr(x, y, 9) * 3)
            col = mix(col, (12, 12, 16), 0.65 * math.sin(math.pi * m * _T) ** 2)
        P[x, y] = col + (255,)
    for x, y in glows:
        cv.glow(x, y, 5, (255, 170, 80), 0.3)


def sol(cv):
    """El sol que surt per la vora de la Terra: nucli blanc, halo càlid i un esclat al llarg de l'horitzó."""
    sx, sy = SX, limb_y(SX) - 1
    cv.glow(sx, sy, 200, (255, 130, 60), 0.18)
    cv.glow(sx, sy, 120, (255, 150, 70), 0.35)
    cv.glow(sx, sy, 53, (255, 200, 120), 0.6 + 0.12 * math.sin(TAU * _T))
    cv.glow(sx, sy, 19, (255, 250, 230), 1.0)
    # esclat horitzontal (seguint la tangent de la vora) i raigs curts
    tx = 1.0
    ty = (limb_y(sx + 1) - limb_y(sx - 1)) / 2
    tl = math.hypot(tx, ty)
    tx, ty = tx / tl, ty / tl
    for k in range(-160, 161):
        a = (1 - abs(k) / 160) ** 2.2
        x, y = sx + tx * k, sy + ty * k
        if a > 0.08:
            blend(cv, x, y, (255, 236, 200), a * 1.3)
        if a > 0.4:
            blend(cv, x, y - 1, (255, 200, 140), a * 0.5)
        if a > 0.7:
            blend(cv, x, y + 1, (255, 220, 170), a * 0.4)
    rl = (34 + 6 * math.sin(TAU * 2 * _T)) * K              # el centelleig: els raigs s'allarguen i s'escurcen
    for k in range(1, int(rl) + 1):
        a = (1 - k / rl) ** 2
        for dx, dy in ((0, -k), (k * 0.6, -k * 0.6), (-k * 0.6, -k * 0.6)):
            blend(cv, sx + dx, sy + dy, (255, 240, 210), a * 0.9)
            if k < 19:
                blend(cv, sx + dx + 1, sy + dy, (255, 220, 170), a * 0.4)
    for dx in range(-3, 4):
        for dy in range(-3, 1):
            if abs(dx) + abs(dy) < 4:
                cv.flat(sx + dx, sy + dy, (255, 255, 250))


# ─── L'estela i la llançadora ───────────────────────────────────────────────

def _axis():
    ax, ay = math.cos(ANG), math.sin(ANG)          # de la cua cap al morro (pantalla)
    return ax, ay, -ay, ax                         # i la perpendicular «avall» de la nau


def _to_screen(u, v):
    ax, ay, bx, by = _axis()
    return NX - ax * u + bx * v, NY - ay * u + by * v


def estela(cv):
    """Una estela tènue i puntejada des de La Gavina fins a la cua, i el plomall blau del motor."""
    tx, ty = _to_screen(LEN + 11, 0)
    n = 350
    for i in range(n):
        t = i / n
        # corba suau: surt cap avall de l'estació i s'endreça
        x = GVX + 8 + (tx - GVX - 8) * t
        y = GVY + 16 + (ty - GVY - 16) * t + math.sin(t * math.pi) * 35
        a = t ** 1.6
        if hr(i, 3) < 0.25 + a * 0.75:
            blend(cv, x, y, (110, 170, 240), 0.15 + a * 0.55)
        if t > 0.6 and hr(i, 4) < a * 0.5:
            blend(cv, x, y + 1, (70, 120, 210), a * 0.35)
        if t > 0.8 and hr(i, 5) < a * 0.3:
            blend(cv, x, y - 1, (70, 120, 210), a * 0.25)


def flama(cv):
    """El plomall del motor: un con de llum blava, blanc al cor, que tremola en anelles (diamants de xoc)."""
    ax, ay, bx, by = _axis()
    L0 = LEN + 12
    FL = 123
    for y in range(0, H):
        for x in range(0, 400):
            dx, dy = x - NX, y - NY
            u = -(dx * ax + dy * ay)                   # distància des del morro cap a la cua
            v = dx * bx + dy * by
            t = (u - L0) / FL
            if t < 0 or t > 1:
                continue
            half = (8.0 * (1 - t) ** 0.7 + 1.2 * math.sin(t * 9 - TAU * 2 * _T) * (1 - t)) \
                * (1 + 0.08 * math.sin(TAU * 3 * _T)) * K  # respira
            if abs(v) > half + 4:
                continue
            core = max(0.0, 1 - abs(v) / max(half, 0.5))
            lvl = core * 6.2 * (1 - t) ** 0.8 + (1 - t) * 1.6
            lvl += 0.9 * max(0.0, math.cos(t * 30 - TAU * 4 * _T)) * (1 - t) * core   # diamants, que corren
            lvl += (0.4 * math.sin(TAU * 5 * _T) + 0.25 * (math.cos(TAU * 3 * _T) - 1)) * core * (1 - t)   # parpelleig
            if abs(v) > half:
                lvl = (1 - (abs(v) - half) / 4) * 1.4 * (1 - t)
            if lvl > 0.4 + B4[y & 3][x & 3] * 0.6:
                cv.put(x, y, FLAME, lvl, 0)
    cx, cy = _to_screen(L0 + 5, 0)
    cv.glow(cx, cy, 61, (80, 150, 255), 0.45 + 0.07 * math.sin(TAU * 3 * _T))
    cv.glow(cx, cy, 21, (200, 236, 255), 0.7)


VET = ['.....hhhh......',
       '...hhhhhhh.....',
       '..hhhhhhhhh....',
       '..Hhhhhhsss....',
       '..HHhhhssss....',
       '..HHHhssssss...',
       '..HHHhsssss....',
       '...HHH.sss.....',
       '....HH.ss......',
       '......oooo.....',
       '....oooOOooo...',
       '..ooooOOOoooo..',
       '.oooooOOOooooo.',
       'ooooooOOOoooooo',
       'ooooooOOOoooooo']


def llancadora(dst):
    cv = Canvas(dst.w, dst.h, transparent=True)
    ax, ay, bx, by = _axis()
    rnd = random.Random(9)

    def half(s):
        if s < 0.24:
            return RAD * math.sqrt(max(0.0, 1 - ((0.24 - s) / 0.24) ** 2)) ** 0.9
        if s > 0.86:
            return RAD * (1 - (s - 0.86) / 0.14 * 0.3)
        return RAD

    # llum: el sol baix a la dreta (vora de sota i morro, càlida) i la Terra (blau, per sota)
    def hull_lvl(s, nv, u):
        lvl = 3.3 - nv * nv * 1.8
        lvl += 2.2 * max(0.0, 1 - abs(nv + 0.5) / 0.2) * (1 - s * 0.6)         # reflex llarg al llom
        lvl += 1.6 * max(0.0, nv - 0.35) / 0.65 * (1.2 - s)                  # el sol, per sota i davant
        lvl += 0.9 * (1 - s) + 0.9
        return lvl

    patches = [(rnd.uniform(0.28, 0.8), rnd.uniform(-0.8, 0.5), rnd.randint(8, 15), rnd.randint(5, 9)) for _ in range(5)]
    x0, x1 = int(NX - LEN - 27), int(NX + 11)
    y0, y1 = int(NY - 67), int(NY + 93)
    pix = {}
    for y in range(y0, y1):
        for x in range(x0, x1):
            dx, dy = x - NX, y - NY
            u = -(dx * ax + dy * ay)
            v = dx * bx + dy * by
            s = u / LEN
            if not 0 <= s <= 1:
                continue
            h = half(s)
            if abs(v) > h or h < 0.5:
                continue
            nv = v / h
            lvl = hull_lvl(s, nv, u)
            rmp = OLDHULL
            # junts de planxa amb reblons
            seam = (u % 23) < 1 and s > 0.2
            if seam:
                lvl -= 1.3
                if round(v) % 5 == 0:
                    lvl += 2.6
            elif (u % 23) < 2 and s > 0.2:
                lvl += 0.4                                           # el cantell de la planxa, que sobresurt
            if abs(nv - 0.42) < 0.05 and s > 0.22:
                lvl -= 1.0
            if abs(nv) > 0.82:
                lvl -= 0.8                                           # el cilindre es tanca a les vores
            lvl += (hr(int(u) // 4, int(v) // 3, 11) - 0.5) * 0.4
            # pedaços soldats, d'un altre gris
            for ps, pv, pw, ph in patches:
                pu = ps * LEN
                if pu <= u <= pu + pw and pv * RAD <= v <= pv * RAD + ph:
                    lvl += 0.8 if (u - pu < 1 or v - pv * RAD < 1) else 0.4
                    if (u - pu) < 1 or (pu + pw - u) < 1:
                        lvl -= 1.4
                    if 1.5 < (u - pu) < 2.5 and round(v) % 3 == 0:
                        lvl += 1.4                                   # el cordó de soldadura
            # rovell: regalims cap avall i a les juntes
            rr = hr(int(u), 31)
            if rr > 0.93 and nv > -0.5 + hr(int(u), 32) * 0.4 and nv < 0.2 + hr(int(u), 33) * 0.6:
                rmp, lvl = RUST, 1.6 + (1 - abs(nv)) * 1.0 + (0.6 if hr(int(u), int(v), 34) > 0.8 else 0)
            # el morro de coure, amb verdet
            if s < 0.06:
                rmp = COPPER
                lvl = 2.6 - nv * 1.4 - nv * nv + (1.2 if -0.6 < nv < -0.3 else 0)
                if hr(int(u), int(v) // 3, 4) > 0.8:
                    rmp, lvl = TEAL, 2.6
            # cèrcol de popa
            if 0.86 < s < 0.885:
                rmp, lvl = COPPER, 2.4 - nv * 1.2 + (1.0 if s < 0.865 else 0)
            pix[(x, y)] = (rmp, lvl, s, nv, u, v)
    for (x, y), (rmp, lvl, s, nv, u, v) in pix.items():
        cv.put(x, y, rmp, lvl, 0)

    def P(u, v):
        return _to_screen(u, v)

    # aletes (dalt i baix, a la cua)
    for sign in (-1, 1):
        pts = [P(LEN - 43, sign * (RAD - 4)), P(LEN - 8, sign * (RAD + 21)), P(LEN + 3, sign * (RAD + 21)),
               P(LEN - 3, sign * (RAD - 8))]
        cv.poly(pts, OLDHULL, lambda x, y, sg=sign: (4.0 if sg < 0 else 2.8) + (hr(x // 4, y // 3, 8) - 0.5) * 0.5
                + 0.0225 * (x - NX + LEN))
        cv.line(*P(LEN - 8, sign * (RAD + 21)), *P(LEN + 3, sign * (RAD + 21)), COPPER, 3.4 if sign < 0 else 2.2)
        cv.line(*P(LEN - 40, sign * (RAD - 3)), *P(LEN - 8, sign * (RAD + 20)), OLDHULL, 4.0 if sign < 0 else 2.6)
        cv.line(*P(LEN - 24, sign * (RAD + 2)), *P(LEN - 4, sign * (RAD + 2)), OLDHULL, 1.6 if sign < 0 else 1.2)   # la costella
        for k in range(4):                                          # reblons al llarg de l'arrel
            rx, ry = P(LEN - 36 + k * 10, sign * (RAD - 1))
            cv.put(rx, ry, OLDHULL, 5.4 if sign < 0 else 4.0)
        rx, ry = P(LEN - 19, sign * (RAD + 8))
        cv.put(rx, ry, RUST, 2.2)
        cv.put(rx + 1, ry + 1, RUST, 1.6)
        cv.put(rx + 1, ry + 2, RUST, 1.2)
    # tobera
    for u in range(LEN, LEN + 13):
        r = 9 + (u - LEN) * 0.5
        for k in range(-int(r), int(r) + 1):
            x, y = P(u, k)
            nv = k / r
            if u >= LEN + 9:
                cv.put(round(x), round(y), FLAME, 4.6 - abs(nv) * 1.5, 0)      # la vora, blanca de calor
            else:
                cv.put(round(x), round(y), COPPER, 2.4 - nv * 1.2 - (u - LEN) * 0.09 + (0.8 if (u - LEN) % 4 == 0 else 0))
    # finestreta, amb la llum de la cabina (i la melena platí de la Vet)
    px_, py_ = round(P(33, -7)[0]), round(P(33, -7)[1])
    cv.disc(px_, py_, 11, 11, COPPER, lambda nx, ny: 3.0 - nx * 0.6 - ny * 1.4)
    cv.ring(px_, py_, 9.9, COPPER, 4.6, step=15)
    for k in range(8):                                              # els cargols del marc
        a = k * math.pi / 4 + 0.3
        cv.put(px_ + math.cos(a) * 9.6, py_ + math.sin(a) * 9.6, COPPER, 5.6 if math.sin(a) < 0 else 1.4)
    cv.disc(px_, py_, 8.3, 8.3, CABIN, lambda nx, ny: 3.2 - ny * 1.8 - math.hypot(nx - 0.3, ny + 0.4) * 1.2, 0)
    leg = {'h': (232, 226, 210), 'H': (162, 158, 166), 's': (108, 64, 50), 'o': (190, 84, 26), 'O': (140, 54, 18)}
    for j, row in enumerate(VET):
        for i, ch in enumerate(row):
            x, y = px_ - 7 + i, py_ - 7 + j
            if ch in leg and math.hypot(x - px_, y - py_) < 8.3:
                cv.flat(x, y, leg[ch])
    cv.flat(px_ + 2, py_ - 3, (40, 20, 24))                         # l'ull, mirant endavant
    cv.flat(px_ + 3, py_ - 4, (186, 180, 170))                      # la cella, platí
    cv.flat(px_ - 1, py_ - 5, (255, 250, 236))                      # un brill a la melena
    for k in range(4):                                              # reflex del vidre
        cv.flat(px_ - 6 + k, py_ - 2 - k, (255, 236, 200) if k not in (1, 2) else (255, 250, 230))
    cv.flat(px_ + 4, py_ + 4, (255, 220, 170))
    # porta i pany sònic
    for u in range(56, 81):
        for vv in (-20, 21):
            x, y = P(u, vv)
            cv.put(round(x), round(y), OLDHULL, 0.6)
    for vv in range(-20, 22):
        for u in (56, 80):
            x, y = P(u, vv)
            cv.put(round(x), round(y), OLDHULL, 0.6 if u == 80 else 3.8)
    for vv in (-14, 15):                                            # les frontisses
        for du in range(3):
            x, y = P(78 - du, vv)
            cv.put(round(x), round(y), COPPER, 2.8)
    lx, ly = P(89, -1)
    cv.disc(lx, ly, 6, 6, COPPER, lambda nx, ny: 2.6 - nx * 0.6 - ny * 1.2)
    cv.ring(lx, ly, 4, COPPER, 1.0, step=6)
    cv.put(lx, ly, COPPER, 4.4)
    cv.put(lx - 1, ly - 1, COPPER, 5.2)
    # el tub de ferro-9 nou, al ventre: net i lluent entre tant de rovell
    for u in range(96, 171):
        for k in range(0, 7):
            x, y = P(u, 15 + k)
            lvl = [5.6, 6.6, 6.8, 5.6, 4.4, 3.0, 2.0][k] + (0.8 if 128 < u < 136 else 0)
            cv.put(round(x), round(y), F9, lvl, 0)
    for u in (107, 139, 160):                                      # abraçadores
        for k in range(-1, 8):
            x, y = P(u, 15 + k)
            cv.put(round(x), round(y), COPPER, 3.4 - k * 0.3)
            x, y = P(u + 1, 15 + k)
            cv.put(round(x), round(y), COPPER, 2.4 - k * 0.2)
            x, y = P(u + 2, 15 + k)
            cv.put(round(x), round(y), COPPER, 1.4)
        x, y = P(u + 1, 14)
        cv.put(round(x), round(y), COPPER, 4.6)                     # el cargol de l'abraçadora
    tx_, ty_ = P(131, 16)
    # «L-1», pintat i esvaït a la popa
    glyphs = [(-9, dv) for dv in range(6)] + [(-8, 5), (-7, 5)] \
        + [(-5, 3), (-4, 3)] \
        + [(0, dv) for dv in range(6)] + [(1, 1), (1, 5), (-1, 5)]
    for du, dv in glyphs:
        x, y = P(128 + du, -17 + dv)
        cv.put(round(x), round(y), PAPER, 1.6 - (0.6 if hr(du, dv, 61) > 0.75 else 0))   # alguna escata saltada
    # vora encesa pel sol: el ventre i el morro, càlids; el llom, blavós de la Terra no (és a sota)
    for (x, y), (rmp, lvl, s, nv, u, v) in pix.items():
        if (x, y + 1) not in pix or (x + 1, y + 1) not in pix and nv > 0.4:
            o = cv.get(x, y)
            cv.flat(x, y, mix(o, (255, 190, 120), 0.55))
        elif nv > 0.55:
            cv.tint(x, y, x, y, (240, 140, 80), 0.18 * (nv - 0.55) / 0.45 * (1.4 - s))
        if (x, y - 1) not in pix and nv < -0.5 and s > 0.08:
            cv.flat(x, y, mix(cv.get(x, y), (130, 150, 190), 0.35))     # retall fred del llom
        if s < 0.2 and (x + 1, y) not in pix:
            o = cv.get(x, y)
            cv.flat(x, y, mix(o, (255, 210, 150), 0.5))
    dst.img.alpha_composite(cv.img)
    # reflex fort al tub (el sol)
    dst.glow(tx_, ty_ + 3, 9, (220, 240, 255), 0.6)
    dst.glow(px_, py_, 16, (255, 170, 90), 0.35)
    # antena doblegada al llom i un parell de toberes de maniobra
    ax0, ay0 = P(77, -RAD)
    ax1, ay1 = P(88, -RAD - 12)
    dst.line(round(ax0), round(ay0), round(ax1), round(ay1), OLDHULL, 4.4, 0)
    dst.line(round(ax1), round(ay1), round(ax1) + 5, round(ay1) - 1, OLDHULL, 3.6, 0)
    dst.rect(round(ax0) - 1, round(ay0), round(ax0) + 1, round(ay0) + 1, OLDHULL, 2.6, 0)   # la base de l'antena
    dst.flat(round(ax1) + 5, round(ay1) - 1, (200, 230, 255))
    for uu, vv in ((40, -RAD), (149, RAD)):
        qx, qy = P(uu, vv)
        dst.rect(round(qx) - 1, round(qy) - (2 if vv < 0 else 0), round(qx) + 2, round(qy) + (0 if vv < 0 else 2), COPPER, 2.4, 0)
        dst.put(round(qx), round(qy) + (-2 if vv < 0 else 2), COPPER, 1.0, 0)
    # llum de posició a l'aleta
    fx, fy = P(LEN - 5, -(RAD + 21))
    dst.flat(round(fx), round(fy) - 1, (255, 70, 60))
    dst.flat(round(fx) + 1, round(fy) - 1, (220, 50, 46))
    dst.glow(round(fx), round(fy) - 1, 8, (255, 70, 60), 0.6)


def titil(cv):
    """Estrelles que titil·len: s'apaguen una mica, cadascuna al seu ritme (a t=0, totes enceses)."""
    if not _T:
        return
    for y in range(H):
        for x in range(W):
            p = cv.P[x, y]
            if p[0] + p[1] + p[2] > 420 and hr(x, y, 21) < 0.6:
                m = 1 + int(hr(x, y, 22) * 3)
                cv.flat(x, y, mix(p, (20, 18, 40), 0.75 * math.sin(math.pi * m * _T) ** 2))


def bg(cv, t=0.0):
    global _T, NY
    _T = t % 1.0
    NY = NY0 + round(math.sin(TAU * _T) * 1.2 * K)  # la nau balanceja un píxel o dos
    espai(cv, seed=21)
    titil(cv)
    terra_nit(cv)
    sol(cv)
    gavina(cv, GVX, GVY, 0.26 * K)
    estela(cv)
    flama(cv)
    llancadora(cv)
    vinyeta(cv, 0.45)


PROPS = {}


def _ambient_frames(n=16):
    import numpy as np
    from PIL import Image
    base = Canvas(light=LIGHT)
    bg(base)
    B = np.asarray(base.img)
    frames = []
    for i in range(n):
        cv = Canvas(light=LIGHT)
        bg(cv, t=i / n)
        A = np.array(cv.img)
        A[~(A != B).any(axis=2)] = 0
        frames.append(Image.fromarray(A, 'RGBA'))
    bg(Canvas(light=LIGHT))                         # deixa l'estat del mòdul com el del fons quiet
    return frames


ANIMS = {'ambient': {'frames': _ambient_frames, 'frameDuration': 110}}
