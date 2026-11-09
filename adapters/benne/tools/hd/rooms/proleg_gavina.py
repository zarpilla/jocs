"""
Pròleg 1 · L'espai: la Terra enorme a baix a la dreta (amb la nit i les ciutats al costat fosc) i La Gavina en
òrbita, planant com una gavina: un cos central, dues ales de panells solars doblegades, el moll de càrrega a sota
i una sola finestra encesa. El sol ve de l'esquerra, fora de quadre.
Pantalla sencera (sense barra de verbs). `espai()` i `gavina()` es reutilitzen a la portada.
"""
import math
import random

from hd.pix import Canvas, Light, B4, W, H, hr, mix, ramp, STEEL, PANEL, WARN, GRAY

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)

# Rampes pròpies (fosc → clar)
OCEAN = ramp((4, 8, 24), (10, 26, 64), (20, 58, 120), (34, 96, 168), (70, 146, 206), (150, 206, 240), n=9)
LAND = ramp((10, 14, 14), (24, 38, 26), (48, 72, 40), (86, 104, 56), (138, 132, 80), (196, 182, 132), n=9)
DESERT = ramp((16, 12, 14), (52, 36, 28), (104, 76, 48), (160, 122, 76), (206, 170, 116), (238, 214, 168), n=9)
CLOUD = ramp((14, 18, 36), (46, 56, 90), (98, 116, 154), (160, 178, 208), (214, 226, 242), (250, 252, 255), n=9)
ATMO = ramp((10, 20, 50), (30, 70, 150), (70, 140, 230), (140, 200, 255), (210, 240, 255), n=7)
SOLAR = ramp((6, 8, 26), (14, 20, 56), (24, 38, 98), (40, 64, 140), (70, 100, 180), (130, 160, 220), (210, 222, 250), n=9)
VOID = ramp((1, 1, 6), (4, 5, 14), (8, 9, 24), (14, 14, 36), (24, 20, 50), (40, 30, 66), (64, 42, 80), n=9)


# ─── Soroll suau (value noise amb taula, ràpid) ─────────────────────────────

class Noise:
    def __init__(self, seed, n=64):
        rnd = random.Random(seed)
        self.n = n
        self.t = [[rnd.random() for _ in range(n)] for _ in range(n)]

    def __call__(self, x, y):
        n = self.n
        xi, yi = math.floor(x), math.floor(y)
        fx, fy = x - xi, y - yi
        fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
        t = self.t
        a, b = t[yi % n][xi % n], t[yi % n][(xi + 1) % n]
        c, d = t[(yi + 1) % n][xi % n], t[(yi + 1) % n][(xi + 1) % n]
        return a + (b - a) * fx + (c - a) * fy + (a - b - c + d) * fx * fy

    def fbm(self, x, y, octaves=4):
        v, amp, tot = 0.0, 1.0, 0.0
        for _ in range(octaves):
            v += self(x, y) * amp
            tot += amp
            x, y, amp = x * 2.03 + 17.1, y * 2.03 + 5.3, amp * 0.5
        return v / tot


N_LAND, N_CLOUD, N_SKY = Noise(91), Noise(92), Noise(93)

SUN = (-0.97, -0.1, -0.2)                                     # direcció del sol (normalitzada a sota)
_l = math.sqrt(sum(c * c for c in SUN))
SUN = tuple(c / _l for c in SUN)


# ─── Fons d'estrelles ───────────────────────────────────────────────────────

def _tw(t, *key):
    """Titil·leig: una ona de -1..1 que val 0 a t = 0 (el fons quiet) i fa bucle (harmònic 1..3, fase pròpia)."""
    if not t:
        return 0.0
    k = 1 + int(hr(*key, 1) * 3)
    p = hr(*key, 2) * 2 * math.pi
    return (math.sin(2 * math.pi * t * k + p) - math.sin(p)) / 2


def espai(cv, x0=0, x1=W - 1, seed=7, t=0.0):
    """Cel negre, una via làctia tènue en diagonal i estrelles (algunes amb creu).
    `t` (0..1): moment del bucle d'animació; algunes estrelles titil·len (amb t = 0, el fons quiet)."""
    for y in range(H):
        for x in range(x0, x1 + 1):
            # banda de la via làctia: de dalt a l'esquerra cap a la dreta, baixant
            d = (y - (30 + x * 0.32)) / 46
            band = math.exp(-d * d) * (0.3 + N_SKY.fbm(x / 40, y / 30, 4)) ** 1.5
            lvl = 1.2 + y / H * 0.8 + band * 3.4
            cv.put(x, y, VOID, lvl, 0)
    rnd = random.Random(seed)
    for _ in range(520):
        x, y = rnd.randint(x0, x1), rnd.randint(0, H - 1)
        d = (y - (30 + x * 0.32)) / 46
        if rnd.random() > 0.35 + math.exp(-d * d) * 0.6:
            continue
        b = rnd.random() ** 2.4
        warm = rnd.random() < 0.2                               # algunes estrelles càlides
        if t and b > 0.12 and hr(x, y, 41) < 0.55:
            b += 0.4 * _tw(t, x, y)                             # titil·la
        col = mix((70, 70, 110), (230, 236, 255), max(0.0, min(1.0, b)))
        if warm:
            col = mix(col, (255, 220, 170), 0.5)
        if b < 0:
            col = mix(cv.get(x, y), col, max(0.0, 1 + b * 3))   # gairebé s'apaga
        cv.flat(x, y, col)
    for _ in range(14):                                         # estrelles brillants amb creu
        x, y = rnd.randint(x0 + 4, x1 - 4), rnd.randint(4, H - 4)
        n = rnd.choice((1, 2, 2, 3))
        tw = _tw(t, x, y, 9)                                    # la creu s'allarga i s'escurça
        cv.flat(x, y, (255, 255, 255))
        for k in range(1, n + 2):
            f = max(0.0, min(1.0, n + 1 - k + tw * 1.3))
            if f <= 0:
                continue
            c = mix((255, 255, 255), (60, 70, 120), k / (n + 1))
            for dx, dy in ((k, 0), (-k, 0), (0, k), (0, -k)):
                if 0 <= x + dx < W and 0 <= y + dy < H:
                    cv.flat(x + dx, y + dy, c if f >= 1 else mix(cv.get(x + dx, y + dy), c, f))
        cv.glow(x, y, 4 + n, (150, 170, 255), 0.35 * (1 + tw * 0.4))


# ─── La Terra ───────────────────────────────────────────────────────────────

def terra(cv, ex, ey, r, x0=0, x1=W - 1, t=0.0):
    """La Terra de centre (ex, ey) i radi r: oceans, continents, núvols, terminador i llums de ciutat.
    `t` (0..1): moment del bucle d'animació; les llums de ciutat fan pampallugues (amb t = 0, el fons quiet)."""
    tt = t                                                       # (més avall, `t` es fa servir per a altres coses)
    for y in range(max(0, int(ey - r - 12)), H):
        for x in range(max(x0, int(ex - r - 12)), min(x1, int(ex + r + 12)) + 1):
            nx, ny = (x - ex) / r, (y - ey) / r
            dd = nx * nx + ny * ny
            if dd > 1:
                # atmosfera: un halo blau que es fon, més fort al costat del sol
                d = (math.sqrt(dd) - 1) * r
                if d < 12:
                    sun = max(0.0, (nx * SUN[0] + ny * SUN[1]) / math.sqrt(dd))
                    a = (1 - d / 12) ** 2.2 * (0.25 + 0.95 * sun)
                    if a > B4[y & 3][x & 3] * 0.9:
                        o = cv.get(x, y)
                        cv.flat(x, y, mix(o, ATMO[min(6, int(1 + a * 5))], min(1, a * 1.1)))
                continue
            nz = math.sqrt(1 - dd)
            diff = nx * SUN[0] + ny * SUN[1] + nz * SUN[2]
            # coordenades de textura sobre l'esfera (rotades una mica)
            lon = math.atan2(nx, nz) + 0.4
            lat = math.asin(max(-1, min(1, ny)))
            u, v = lon * 2.2, lat * 2.6
            land = N_LAND.fbm(u + 3.1, v + 1.7, 5)
            dry = N_LAND.fbm(u * 1.7 + 9, v * 1.7, 3)
            cloud = N_CLOUD.fbm(u * 1.6 + math.sin(v * 5 + u) * 0.5, v * 6.0, 5)
            cloud = max(0.0, (cloud - 0.5) * 3.2)
            day = max(0.0, min(1.0, diff * 3.0 + 0.3))           # 0 de nit, 1 de dia (terminador suau)
            lvl = 0.5 + day * 3.6 + diff * 1.0
            limb = (1 - nz) ** 3                                  # boirina de l'atmosfera a la vora
            if land > 0.53:
                rmp = DESERT if dry > 0.6 else LAND
                lvl += (land - 0.53) * 3 - 0.3
            else:
                rmp = OCEAN
                lvl += (land - 0.5) * 2.4
                spec = max(0.0, 1 - math.hypot(nx + 0.7, ny + 0.45) / 0.3)   # reflex del sol a l'oceà
                lvl += spec ** 2 * 2.4
            if day < 0.2:                                         # de nit, tot és blau fosc
                rmp, lvl = OCEAN, 0.35 + (0.35 if land > 0.53 else 0) + day * 2
            c = cloud - 0.38 - (B4[y & 3][x & 3] - 0.5) * 0.35
            if c > 0:
                rmp = CLOUD
                lvl = 0.3 + day * 4.6 + diff * 1.4 + min(cloud, 1.5) * 0.9 * (0.25 + 0.75 * day)
            # vora: es renta cap al blau de l'atmosfera
            if limb * day > B4[y & 3][x & 3] * 0.5 + 0.18:
                rmp, lvl = ATMO, 1.6 + limb * 3.2 * day
            # terminador: una franja càlida molt fina
            if 0.12 < day < 0.3 and rmp is not OCEAN:
                lvl -= 0.3
            cv.put(x, y, rmp, lvl, 0)
            # ciutats al costat de nit
            if day < 0.25 and rmp is not CLOUD and land > 0.53:
                c = hr(x, y, 5)
                dens = max(0.0, N_CLOUD(u * 7, v * 7) - 0.55) * (1 - abs(land - 0.56) * 12)
                if c < dens * 1.0 and limb < 0.5:
                    col = (255, 196, 110) if c < 0.05 else (190, 120, 60)
                    if tt:
                        q = _tw(tt, x, y, 5)
                        col = mix(col, (255, 230, 170), q) if q > 0 else mix(col, (60, 34, 30), -q * 1.2)
                    cv.flat(x, y, col)
    # línia fina de llum a la vora il·luminada
    for a in range(0, 3600):
        t = math.radians(a / 10)
        nx, ny = math.cos(t), math.sin(t)
        sun = nx * SUN[0] + ny * SUN[1]
        if sun > 0.05:
            x, y = round(ex + nx * (r + 0.5)), round(ey + ny * (r + 0.5))
            if x0 <= x <= x1 and 0 <= y < H:
                cv.flat(x, y, mix(ATMO[3], ATMO[6], min(1, sun * 1.6)))


# ─── La Gavina ──────────────────────────────────────────────────────────────

def _quad_wing(cv, s, root, tip, chord_root, chord_tip, cells, base, sheen, lit_edge, ox, oy):
    """Un tram d'ala: panell solar entre una vora d'atac (root→tip) i una de sortida (la mateixa, més avall).
    root/tip en coordenades locals; extrems verticals. `cells` = (n al llarg, n de través)."""
    (ax, ay), (bx, by) = root, tip
    X0, X1 = ox + ax * s, ox + bx * s
    lo, hi = (X0, X1) if X0 < X1 else (X1, X0)
    nu, nv = cells
    for x in range(math.floor(lo), math.ceil(hi) + 1):
        t = (x - X0) / (X1 - X0)
        if not 0 <= t <= 1:
            continue
        top = oy + (ay + (by - ay) * t) * s
        ch = (chord_root + (chord_tip - chord_root) * t) * s
        bot = top + ch
        for y in range(math.floor(top), math.ceil(bot) + 1):
            v = (y - top) / ch
            if not -0.02 <= v <= 1.02:
                continue
            cu = t * nu
            cvv = v * nv
            span_px = abs(X1 - X0) / nu
            on_u = (cu % 1) * span_px < 1
            on_v = (cvv % 1) * (ch / nv) < 0.9
            edge = y <= top + 0.6 or y >= bot - 0.6 or t < 0.02 or t > 0.98
            if edge:
                lvl = lit_edge if y <= top + 0.6 else lit_edge - 2.6
                cv.put(x, y, STEEL, lvl, 0)
            elif on_u or on_v:
                cv.put(x, y, STEEL, base + 0.6, 0)
            else:
                cell = (hr(int(cu), int(cvv), int(ax)) - 0.5) * 0.5
                lvl = base + 2.2 + sheen(t, v) + cell - v * 0.8
                cv.put(x, y, SOLAR, lvl, 0)


def gavina(dst, cx, cy, s=1.0, light=True, t=0.0):
    """La Gavina centrada a (cx, cy), escala s. Sol des de l'esquerra; la Terra la il·lumina de blau per sota.
    `t` (0..1): moment del bucle d'animació: les llums de navegació parpellegen per torns (vermell, verd), la balisa
    de l'antena batega i la finestra encesa tremola una mica. Amb t = 0, el fons quiet (tot encès)."""
    tt = t
    ph = 2 * math.pi * tt
    fr = (tt * 24) % 12                                           # (en fotogrames d'un bucle de 24)
    cv = Canvas(dst.w, dst.h, transparent=True)
    halos = []
    P = lambda dx, dy: (cx + dx * s, cy + dy * s)

    # ── Les ales: tram interior (puja fins al colze) i tram exterior (baixa fins a la punta) ──
    # Les ales tenen dos dits de gruix: biga d'acer a dalt i panells a sota.
    for sign in (-1, 1):
        root, elbow, tip = (sign * 22, -6), (sign * 86, -40), (sign * 158, -14)
        left = sign < 0
        # tram interior: mira cap amunt i al sol si és l'ala esquerra
        b_in = 2.2 if left else 0.6
        b_out = 1.4 if left else 0.0
        sheen_in = (lambda t, v, l=left: (2.6 * max(0, 1 - abs(t - 0.55) * 2.6) ** 1.5) if l else 0.4 * (1 - t))
        sheen_out = (lambda t, v, l=left: (0.8 * max(0, 1 - abs(t - 0.3) * 3)) if l else 0.6 * max(0, 1 - abs(t - 0.7) * 3))
        _quad_wing(cv, s, root, elbow, 18, 13, (9, 3), b_in, sheen_in, 6.6 if left else 5.0, cx, cy)
        _quad_wing(cv, s, elbow, tip, 13, 8, (11, 2), b_out, sheen_out, 6.0 if left else 4.4, cx, cy)
        # biga (gelosia) al llarg de la vora d'atac
        for (ax, ay), (bx, by) in ((root, elbow), (elbow, tip)):
            n = max(2, int(abs(bx - ax) * s / 4))
            for i in range(n + 1):
                t = i / n
                x, y = cx + (ax + (bx - ax) * t) * s, cy + (ay + (by - ay) * t) * s
                cv.put(x, y - 2, STEEL, 6.2 if left else 4.6, 0)
                if i % 2 == 0:
                    cv.put(x, y - 1, STEEL, 3.0, 0)
            cv.line(cx + ax * s, cy + ay * s - 2, cx + bx * s, cy + by * s - 2, STEEL, 5.6 if left else 4.0, 0)
        # el colze: una articulació (el canell de la gavina)
        ex, ey = P(*elbow)
        cv.disc(ex, ey - 1, 3.2 * s + 0.6, 3.2 * s + 0.6, STEEL, lambda nx, ny: 5.6 - nx * 1.6 - ny * 1.4, 0)
        cv.put(ex - 1, ey - 2, STEEL, 9, 0)
        # llums de navegació a les puntes (vermell a babord, verd a estribord)
        tx, ty = P(*tip)
        col = (255, 60, 50) if left else (70, 255, 120)
        off = (2.5 <= fr < 4.5) if left else (8.5 <= fr < 10.5)  # s'apaguen per torns, dos cops per bucle
        if off:
            cv.flat(tx, ty - 1, mix(col, (20, 24, 40), 0.65))
            halos.append((tx, ty - 1, 3 * s + 2, col, 0.25))
        else:
            cv.flat(tx, ty - 1, col)
            halos.append((tx, ty - 1, 6 * s + 2, col, 0.8))
        # puntal de la biga fins al cos (l'espatlla)
        rx, ry = P(*root)
        cv.disc(rx, ry + 2, 4 * s + 0.5, 5 * s + 0.5, STEEL, lambda nx, ny: 4.6 - nx * 1.6 - ny * 1.6, 0)

    s = s * 1.3                                                   # el cos, una mica més gros que a escala

    # ── El moll de càrrega a sota: una tija i una plataforma amb ratlles d'avís ──
    sx, sy = P(0, 14)
    for y in range(int(sy), int(cy + 34 * s)):
        for x in range(int(cx - 3 * s), int(cx + 3 * s) + 1):
            u = (x - cx) / (3 * s)
            cv.put(x, y, STEEL, 4.0 - u * 2.0 - (y - sy) / 30 + (0.8 if (y - int(sy)) % 5 == 0 else 0), 0)
    px0, px1 = cx - 16 * s, cx + 16 * s
    py0, py1 = cy + 33 * s, cy + 39 * s
    for y in range(int(py0), int(py1) + 1):
        for x in range(int(px0), int(px1) + 1):
            u = (x - px0) / (px1 - px0)
            if y == int(py0):
                cv.put(x, y, STEEL, 7.4 - u * 3, 0)
            elif y >= int(py1) - 1:
                stripe = ((x + y) // 2) % 2 == 0
                cv.put(x, y, WARN if stripe else STEEL, (3.2 - u) if stripe else 1.0, 0)
            else:
                cv.put(x, y, STEEL, 4.6 - u * 2.6, 0)
    for xx in (px0 + 2, cx, px1 - 2):                            # llums de guia
        cv.flat(xx, py0 + 2, (120, 255, 170))
    halos.append((cx, py0 + 3, 9 * s, (120, 255, 170), 0.3))

    # ── El cos central: un tambor amb costelles, un con a sota i una cúpula a dalt ──
    RX, TOP, BOT, CAP = 22 * s, cy - 6 * s, cy + 8 * s, 5 * s

    def drum_lvl(u):
        lvl = 2.8 + 3.4 * max(0.0, 1 - abs(u + 0.4) / 0.85) - 1.6 * max(0.0, u) ** 1.5
        if abs(u + 0.55) < 0.05:
            lvl += 2.2                                             # reflex especular
        return lvl

    # con de sota (cap a la tija del moll)
    CB = cy + 17 * s
    for y in range(int(BOT), int(CB) + 1):
        t = (y - BOT) / (CB - BOT)
        half = RX * (1 - t) + 6 * s * t
        for x in range(math.floor(cx - half), math.ceil(cx + half) + 1):
            u = (x - cx) / half
            if abs(u) <= 1:
                cv.put(x, y, STEEL, drum_lvl(u) - 1.4 - t * 0.8, 0)
    # costat del tambor
    for y in range(int(TOP), int(BOT) + 1):
        for x in range(math.floor(cx - RX), math.ceil(cx + RX) + 1):
            u = (x - cx) / RX
            if abs(u) > 1:
                continue
            lvl = drum_lvl(u)
            th = math.asin(u)
            if (th / (math.pi / 14)) % 1 < 0.18 * (1 + abs(u) * 2):   # costelles verticals
                lvl -= 1.4
            if y in (int(TOP) + 1, int(BOT) - 1):
                lvl -= 1.0
            cv.put(x, y, STEEL, lvl, 0)
    # el ventre corbat: la vora inferior del tambor és una el·lipse
    for x in range(math.floor(cx - RX), math.ceil(cx + RX) + 1):
        u = (x - cx) / RX
        if abs(u) <= 1:
            yb = BOT + math.sqrt(1 - u * u) * CAP * 0.6
            for y in range(int(BOT), int(yb) + 1):
                cv.put(x, y, STEEL, drum_lvl(u) - 0.6, 0)
            cv.put(x, int(yb) + 1, STEEL, 1.0, 0)
    # tapa de dalt (la veiem una mica des de dalt)
    cv.disc(cx, TOP, RX, CAP, STEEL, lambda nx, ny: 6.2 - nx * 1.8 + ny * 0.6, 0)
    for k in range(0, 360, 3):                                     # vora de la tapa
        t = math.radians(k)
        x, y = cx + math.cos(t) * RX, TOP + math.sin(t) * CAP
        if math.sin(t) > -0.2:
            cv.put(x, y, STEEL, 7.6 - math.cos(t) * 2.6, 0)
    # cúpula
    DR = 11 * s
    for y in range(int(TOP - 11 * s), int(TOP) + 1):
        for x in range(math.floor(cx - DR), math.ceil(cx + DR) + 1):
            nx, ny = (x - cx) / DR, (y - TOP) / (11 * s)
            if nx * nx + ny * ny <= 1:
                lvl = 6.0 - nx * 2.4 + ny * 1.6
                if math.hypot(nx + 0.4, ny + 0.6) < 0.28:
                    lvl += 1.4
                if abs(ny + 0.35) < 0.06:
                    lvl -= 1.6                                     # junta
                cv.put(x, y, STEEL, lvl, 0)
    # ulls de bou de la cúpula (fosc: tothom dorm)
    for i in (-1, 0, 1):
        cv.flat(cx + i * 5 * s, TOP - 5 * s, (16, 22, 36))
        cv.flat(cx + i * 5 * s + 1, TOP - 5 * s, (16, 22, 36))
    # anell de finestres (fosques) i una sola d'encesa
    wy = round(cy + 1 * s)
    lit_x = round(cx + 10 * s)
    for i in range(-14, 15):
        th = (i + 0.5) * math.pi / 14
        if abs(th) > 1.35:
            continue
        x = round(cx + math.sin(th) * RX)
        if abs(x - lit_x) < 3:
            continue
        u = (x - cx) / RX
        cv.flat(x, wy, mix((10, 14, 24), (44, 56, 78), max(0, -u)))
        cv.flat(x, wy + 1, (6, 8, 16))
    cv.flat(lit_x, wy, (255, 240, 180))
    cv.flat(lit_x + 1, wy, (255, 214, 130))
    cv.flat(lit_x, wy + 1, (246, 176, 86))
    cv.flat(lit_x + 1, wy + 1, (206, 126, 56))
    # antena i plat de comunicacions
    mx = round(cx + 5 * s)
    cv.vline(mx, round(cy - 30 * s), round(TOP - 6 * s), STEEL, 5.0, 0)
    cv.flat(mx, round(cy - 31 * s), (255, 255, 255))
    halos.append((mx, cy - 31 * s, 5 * s + 1, (220, 230, 255), 0.6 + 0.25 * (math.cos(ph * 3) - 1)))
    dx_, dy_ = cx - 12 * s, cy - 22 * s
    cv.line(dx_ + 1, dy_ + 1, cx - 6 * s, TOP - 5 * s, STEEL, 3.6, 0)
    cv.disc(dx_, dy_, 4 * s, 2.4 * s, STEEL, lambda nx, ny: 7.0 - nx * 2 + ny * 1.4, 0)
    # el «cap»: una resclosa curta al davant, cap al sol
    hx, hy = cx - RX - 3 * s, cy + 1 * s
    cv.rect(hx, hy - 3 * s, cx - RX + 1, hy + 3 * s, STEEL, lambda x, y: 6.6 - (y - hy) / (3 * s) * 1.6, 0)
    cv.disc(hx, hy, 1.6 * s, 3.4 * s, STEEL, lambda nx, ny: 3.6 - ny, 0)
    cv.flat(hx - 1, hy, (180, 230, 255))
    # cua: aletes radiadores per darrere (a la dreta, a l'ombra)
    for k in range(3):
        y0 = cy + (-3 + k * 4) * s
        cv.line(cx + RX + 1, y0, cx + RX + 9 * s, y0 + 2 * s, PANEL, 3.0 - k * 0.6, 0)

    # llum de la Terra per sota: tint blau a la meitat de baix del conjunt
    cv.tint(cx - 165 * s, cy + 4 * s, cx + 165 * s, cy + 40 * s, (60, 120, 220),
            lambda x, y: 0.22 * min(1, (y - (cy + 4 * s)) / (12 * s)),
            mask=lambda x, y: 1.0 if cv.get(x, y)[3] else 0.0)
    dst.img.alpha_composite(cv.img)
    if light:
        fl = 0.07 * (math.sin(ph * 5 + 1) - math.sin(1)) + 0.04 * (math.sin(ph * 2) - 0)
        halos.append((lit_x + 0.5, wy + 0.5, 10 * s + 2, (255, 190, 110), 0.5 + fl))
    for h in halos:
        dst.glow(*h)


# ─── La pantalla ────────────────────────────────────────────────────────────

GX, GY = 188, 98              # on és La Gavina
EX, EY, ER = 410, 368, 196    # la Terra


def vinyeta(cv, k=0.55):
    cv.darken(0, 0, W - 1, H - 1, lambda x, y: k * max(0.0, (math.hypot((x - W / 2) / (W / 2), (y - H / 2) / (H / 2)) - 0.8) * 1.4), dither=False)


def lluna(cv, x, y, r):
    """La Lluna, petita i lluny, il·luminada per l'esquerra."""
    for yy in range(int(y - r - 1), int(y + r + 2)):
        for xx in range(int(x - r - 1), int(x + r + 2)):
            nx, ny = (xx - x) / r, (yy - y) / r
            if nx * nx + ny * ny <= 1:
                nz = math.sqrt(1 - nx * nx - ny * ny)
                d = nx * SUN[0] + ny * SUN[1] + nz * SUN[2]
                mar = N_LAND.fbm(nx * 2 + 30, ny * 2, 3) > 0.55
                lvl = -0.6 + max(0, d) ** 0.7 * 6.0 - (0.9 if mar else 0)
                if lvl > 0.2:
                    cv.put(xx, yy, GRAY, lvl, 0)
                else:
                    cv.flat(xx, yy, mix(cv.get(xx, yy), (8, 8, 18), 0.7))   # la cara fosca tapa les estrelles


def bg(cv, t=0.0):
    espai(cv, t=t)
    lluna(cv, 418, 46, 9)
    terra(cv, EX, EY, ER, t=t)
    gavina(cv, GX, GY, 1.12, t=t)
    vinyeta(cv)


PROPS = {}


# ─── Animació de fons ───────────────────────────────────────────────────────

def ambient_frames(bg_fn, light, n=24, mask=None):
    """Fotogrames d'una animació de fons: la sala en n moments del bucle, i de cada un només els píxels que canvien
    respecte del fons quiet (t = 0). `mask(x0, y0, x1, y1)`: rectangle on no s'hi anima res (opcional)."""
    import numpy as np
    from PIL import Image
    base = Canvas(light=light)
    bg_fn(base)
    B = np.asarray(base.img)
    frames = []
    for i in range(n):
        cv = Canvas(light=light)
        bg_fn(cv, t=i / n)
        A = np.array(cv.img)
        ch = (A[..., :3] != B[..., :3]).any(axis=2)
        if mask:
            x0, y0, x1, y1 = mask
            ch[y0:y1 + 1, x0:x1 + 1] = False
        A[~ch] = 0
        frames.append(Image.fromarray(A, 'RGBA'))
    return frames


ANIMS = {'ambient': {'frames': lambda: ambient_frames(bg, LIGHT), 'frameDuration': 130}}
