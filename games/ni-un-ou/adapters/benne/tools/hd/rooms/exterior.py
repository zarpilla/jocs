"""
Exteriors de l'Arenga: cel i mar (de nit i de dia), l'Arenga de perfil, la plataforma que no surt als mapes,
gavines. Ho fan servir les cobertes (coberta_popa, coberta_proa) i les cinemàtiques (proleg_punt7, portada,
final_galway, credits).

Tot es dibuixa amb lit=0 per defecte (nivells fixos): el cel i el mar no reben la llum de la sala.
"""
import math

from hd.pix import W, H, hr, mix, B4

# ─── Rampes (fosc → clar) ───────────────────────────────────────────────────
NSKY = [(3, 5, 12), (5, 8, 18), (8, 12, 25), (11, 16, 32), (15, 21, 40), (20, 27, 49), (27, 35, 59),
        (36, 45, 70), (48, 58, 84), (66, 76, 100), (96, 104, 124)]
NSEA = [(2, 4, 8), (3, 7, 13), (5, 11, 19), (8, 16, 26), (12, 22, 34), (17, 30, 43), (25, 40, 54),
        (38, 56, 70), (60, 80, 94), (100, 120, 130), (160, 172, 176)]
DSKY = [(92, 110, 128), (112, 130, 146), (134, 150, 164), (156, 170, 180), (178, 188, 194), (198, 204, 206),
        (216, 218, 216), (232, 232, 226)]
DCLOUD = [(88, 94, 106), (110, 116, 126), (134, 138, 146), (160, 164, 168), (186, 188, 190), (210, 212, 210),
          (232, 232, 228)]
DSEA = [(18, 28, 36), (26, 38, 48), (36, 50, 60), (48, 64, 74), (62, 80, 88), (80, 98, 104), (102, 120, 124),
        (132, 148, 150), (176, 186, 184)]
TURBID = [(46, 44, 34), (64, 60, 46), (84, 78, 60), (104, 96, 74), (124, 114, 88), (146, 134, 104)]
HULLN = [(10, 13, 20), (16, 20, 30), (24, 30, 42), (36, 44, 58), (52, 62, 76), (72, 82, 96), (98, 106, 118),
         (130, 136, 144), (170, 174, 176), (210, 212, 208)]
REDH = [(24, 6, 8), (46, 10, 12), (76, 16, 18), (112, 26, 26), (150, 40, 34), (188, 64, 48), (220, 100, 76)]
STEELX = [(6, 8, 12), (12, 15, 20), (20, 24, 30), (30, 35, 42), (42, 48, 56), (58, 64, 72), (78, 84, 90),
          (104, 108, 112), (136, 138, 138)]
TAPE = [(40, 40, 42), (70, 70, 72), (104, 104, 104), (138, 138, 136), (170, 170, 166)]
LAMP = [(120, 90, 40), (200, 160, 80), (250, 220, 150), (255, 246, 220)]
WINDOW = [(40, 26, 10), (110, 74, 28), (190, 140, 60), (240, 200, 110), (255, 236, 180)]
GLOW_WARM = (255, 206, 120)
GLOW_MOON = (190, 205, 225)


# ─── Soroll suau ────────────────────────────────────────────────────────────

def _s(t):
    return t * t * (3 - 2 * t)


def vnoise(u, v, seed=0):
    """Soroll de valors suau (0..1) en una graella unitària."""
    x0, y0 = math.floor(u), math.floor(v)
    fx, fy = _s(u - x0), _s(v - y0)
    a, b = hr(x0, y0, seed), hr(x0 + 1, y0, seed)
    c, d = hr(x0, y0 + 1, seed), hr(x0 + 1, y0 + 1, seed)
    return a + (b - a) * fx + (c - a) * fy + (a - b - c + d) * fx * fy


def fbm(u, v, seed=0, octaves=3):
    s, amp, tot = 0.0, 1.0, 0.0
    for o in range(octaves):
        s += vnoise(u * 2 ** o, v * 2 ** o, seed + o * 17) * amp
        tot += amp
        amp *= 0.5
    return s / tot


def smooth(a, b, t):
    if t <= a:
        return 0.0
    if t >= b:
        return 1.0
    return _s((t - a) / (b - a))


# ─── Cel ────────────────────────────────────────────────────────────────────

def night_sky(cv, y0, hor, moon=None, seed=1, clouds=0.5, stars=True, x0=0, x1=W - 1):
    """Cel de febrer de nit: degradat, bandes de núvols (vores il·luminades per la lluna) i estrelles."""
    for y in range(y0, hor + 1):
        t = (y - y0) / max(1, hor - y0)
        for x in range(x0, x1 + 1):
            lvl = 1.0 + 3.0 * t ** 1.4
            near = 0.0
            if moon:
                near = max(0.0, 1 - math.hypot(x - moon[0], (y - moon[1]) * 1.3) / 110)
                lvl += 2.0 * near ** 2
            c = fbm(x / 70, y / 16, seed)
            k = smooth(1 - clouds, 1 - clouds + 0.16, c) * (0.5 + 0.5 * t)
            if k > 0:
                up = fbm(x / 70, (y - 3) / 16, seed)
                rim = smooth(1 - clouds, 1 - clouds + 0.12, c) - smooth(1 - clouds, 1 - clouds + 0.12, up)
                body = 2.2 + 2.6 * t + 1.8 * near ** 1.5
                body += 2.6 * max(0.0, rim) * (0.4 + 1.6 * near)
                body += (fbm(x / 14, y / 6, seed + 5) - 0.5) * 0.8
                lvl = lvl * (1 - k) + body * k
            cv.put(x, y, NSKY, lvl, lit=0)
            if stars and k < 0.05 and t < 0.8 and hr(x, y, seed + 99) > 0.9975:
                cv.flat(x, y, (200, 210, 230) if hr(x, y, seed + 3) > 0.6 else (110, 120, 150))
    if moon:
        mx, my = moon
        cv.glow(mx, my, 26, GLOW_MOON, 0.35)
        cv.disc(mx, my, 5, 5, [(150, 156, 168), (196, 200, 208), (226, 228, 230), (244, 244, 240)],
                lambda nx, ny: 2.6 - nx * 0.9 - ny * 0.6, lit=0)
        cv.put(mx + 1, my - 1, [(150, 156, 168), (196, 200, 208)], 0.0, lit=0)
        cv.put(mx - 2, my + 1, [(150, 156, 168), (196, 200, 208)], 0.4, lit=0)
        # un núvol prim que hi passa per davant
        for x in range(mx - 14, mx + 15):
            for y in (my + 1, my + 2):
                if hr(x // 3, y) > 0.35:
                    cv.flat(x, y, mix(cv.get(x, y), (60, 66, 86), 0.55))


def day_sky(cv, y0, hor, seed=11, x0=0, x1=W - 1, sun=None):
    """Cel pàl·lid de febrer: blau gris a dalt, blanquinós a l'horitzó, núvols baixos i plans."""
    for y in range(y0, hor + 1):
        t = (y - y0) / max(1, hor - y0)
        for x in range(x0, x1 + 1):
            lvl = 1.2 + 5.0 * t ** 1.1
            if sun:
                lvl += 1.6 * max(0.0, 1 - math.hypot(x - sun[0], y - sun[1]) / 120) ** 2
            c = fbm(x / 80, y / 12, seed)
            k = smooth(0.55, 0.7, c) * (0.3 + 0.7 * t)
            if k > 0:
                up = fbm(x / 80, (y - 2) / 12, seed)
                top = max(0.0, smooth(0.55, 0.7, c) - smooth(0.55, 0.7, up))
                body = 3.2 + 1.6 * t - 0.8 * (1 - top) + 2.0 * top
                cv.put(x, y, DCLOUD, lvl * (1 - k) * 0.85 + body * k + (fbm(x / 10, y / 5, seed + 4) - 0.5) * 0.6, lit=0)
            else:
                cv.put(x, y, DSKY, lvl, lit=0)


# ─── Mar ────────────────────────────────────────────────────────────────────

def _wave(x, y, hor, seed, phase=0.0):
    d = y - hor + 1
    dd = min(d, 70)
    sx = 2.5 + dd * 0.3
    sy = 0.5 + dd * 0.045
    return vnoise((x + phase * sx * 0.6) / sx, (y - hor) / sy, seed)


def night_sea(cv, hor, y1, moon_x=None, seed=2, x0=0, x1=W - 1, phase=0.0, calm=1.0):
    """Mar de nit: fosc, més clar a l'horitzó, ratlles d'onada i el camí de la lluna."""
    for y in range(hor, y1 + 1):
        d = y - hor
        for x in range(x0, x1 + 1):
            lvl = 3.4 - min(2.0, d * 0.045)
            n = _wave(x, y, hor, seed, phase)
            lvl += (n - 0.5) * 1.6 * calm
            if n > 0.78:
                lvl += 1.2 * calm
            if moon_x is not None:
                wdt = 6 + d * 0.9
                m = max(0.0, 1 - abs(x - moon_x) / wdt)
                if m > 0:
                    lvl += m * 1.2
                    if n > 0.62 and hr(x // 2, y, seed) > 0.25:
                        lvl += 3.6 * m
            cv.put(x, y, NSEA, lvl, lit=0)
    for x in range(x0, x1 + 1):                    # la línia de l'horitzó, una mica més clara
        cv.put(x, hor, NSEA, 4.0, lit=0)


def day_sea(cv, hor, y1, seed=3, x0=0, x1=W - 1, sun_x=None, phase=0.0):
    """Mar de dia, gris de febrer: reflex pàl·lid a l'horitzó, ratlles d'onada i espurnes."""
    for y in range(hor, y1 + 1):
        d = y - hor
        for x in range(x0, x1 + 1):
            lvl = 5.4 - min(3.2, d * 0.07)
            n = _wave(x, y, hor, seed, phase)
            lvl += (n - 0.5) * 1.8
            if n > 0.8:
                lvl += 1.4
            if sun_x is not None:
                wdt = 10 + d * 1.2
                m = max(0.0, 1 - abs(x - sun_x) / wdt)
                if m > 0 and n > 0.6 and hr(x // 2, y, seed) > 0.3:
                    lvl += 3.0 * m
            cv.put(x, y, DSEA, lvl, lit=0)
    for x in range(x0, x1 + 1):
        cv.put(x, hor, DSEA, 6.4, lit=0)


# ─── L'Arenga, de perfil ────────────────────────────────────────────────────

def sheer(m):
    """Alçada de la borda (m) sobre la línia de flotació, a m metres de la popa."""
    return 3.3 + 1.7 * max(0.0, (m - 27) / 13) ** 2


def arenga(cv, xs, ywl, s, mode='night', facing=1, crane=True, zodiac=True, under=0.0):
    """L'Arenga de perfil: xs = x de la popa, ywl = y de la línia de flotació, s = píxels per metre.
    mode: 'night' (finestres enceses, llums de navegació) o 'dawn' (llum freda, sense llums).
    `under`: fins on es dibuixa el buc per sota de la flotació (m)."""
    night = mode == 'night'
    base = 4.8 if night else 7.2

    def X(m):
        return xs + m * s * facing

    def Y(m):
        return ywl - m * s

    def poly(pts, ramp, lvl):
        cv.poly([(X(a), Y(b)) for a, b in pts], ramp, lvl, lit=0)

    def box(m0, h0, m1, h1, ramp, lvl):
        xa, xb = sorted((X(m0), X(m1)))
        cv.rect(round(xa), round(Y(h1)), round(xb), round(Y(h0)), ramp, lvl, lit=0)

    # buc: de la popa (0) a la proa (40), amb la proa llançada
    top = [(m, sheer(m)) for m in [0.4 + i * 0.5 for i in range(80)] if m <= 40.2]
    hull = [(0.9, -under), (0.0, 3.4)] + top + [(40.8, sheer(40.2) + 0.1), (37.8, 0.0), (37.0, -under)]
    lo = Y(-under)

    def hull_lvl(x, y):
        h = (ywl - y) / s
        v = base - 0.9 + h * 0.25 - (0.6 if h < 0.6 else 0)
        return v + (hr(x // 3, y // 2) - 0.5) * 0.2
    cv.poly([(X(a), Y(b)) for a, b in hull], HULLN, hull_lvl, lit=0)
    # sota la flotació, l'antiincrustant fosc
    cv.poly([(X(a), Y(b)) for a, b in [(0.9, -under - 0.2), (0.15, 0.4), (37.9, 0.4), (37.0, -under - 0.2)]], REDH,
            lambda x, y: 1.0 if night else 2.0, lit=0)
    if s >= 5:
        for m in range(4, 38, 4):                                  # juntes de planxa
            for h10 in range(4, int(sheer(m) * 10) - 6):
                cv.put(X(m), Y(h10 / 10), HULLN, base - 1.4, lit=0)
        for i in range(14):                                        # regalims de rovell
            m = 2 + hr(i, 51) * 34
            h0 = 1.6 + hr(i, 52) * 1.2
            for k in range(int(s * (0.6 + hr(i, 53)))):
                xx, yy = round(X(m)), round(Y(h0)) + k
                cv.flat(xx, yy, mix(cv.get(xx, yy), (110, 60, 36), 0.4 * (1 - k / (s * 1.6))))
        for x in range(round(min(X(0), X(38))), round(max(X(0), X(38)))):   # vora clara sota la regala
            m = (x - xs) / (s * facing)
            if 0 <= m <= 38:
                cv.put(x, Y(sheer(m) - 0.9), HULLN, base + 1.0, lit=0)
    # la línia vermella de la borda
    for i in range(len(top) - 1):
        (ma, ha), (mb, hb) = top[i], top[i + 1]
        cv.poly([(X(ma), Y(ha - 0.25)), (X(mb), Y(hb - 0.25)), (X(mb), Y(hb - 0.75)), (X(ma), Y(ha - 0.75))],
                REDH, 3.6 if night else 4.6, lit=0)
    # regala de la borda (vora clara)
    for m, h in top:
        cv.put(X(m), Y(h), HULLN, base + 1.2, lit=0)
    # ulls de bou
    for m in range(8, 33, 3):
        if 13 <= m <= 15:
            continue
        on = night and hr(m, 4) > 0.45
        r = max(0.6, 0.22 * s)
        cv.disc(X(m), Y(1.9), r, r, WINDOW if on else HULLN, (3.4 if on else base - 2.6), lit=0)
        if on and s >= 3:
            cv.glow(X(m), Y(1.9), 3 + s * 0.6, GLOW_WARM, 0.25)
    # Mar Obert, a la proa: el cercle vermell
    if s >= 3:
        cv.disc(X(35.5), Y(2.4), 0.55 * s, 0.55 * s, REDH, 4.2 if night else 5.0, lit=0)
        cv.disc(X(35.5), Y(2.4), 0.3 * s, 0.3 * s, HULLN, base + 0.6, lit=0)

    # la superestructura: la caseta, el pont, la xemeneia, el pal
    sh = sheer(14)
    poly([(13, sh), (13, 5.9), (31, 5.9), (31.5, sh)], HULLN, base - 0.2)
    for m in range(14, 31, 2):                                     # finestres de la caseta
        on = night and hr(m, 9) > 0.3
        box(m, 4.3, m + max(1 / s, 0.7), 4.9, WINDOW if on else HULLN, 3.2 if on else base - 2.4)
        if on and s >= 3:
            cv.glow(X(m) + 0.35 * s * facing, Y(4.6), 2 + s * 0.8, GLOW_WARM, 0.22)
    poly([(13, 5.9), (13, 6.15), (31.2, 6.15), (31.2, 5.9)], HULLN, base + 1.0)
    poly([(21, 6.1), (21, 8.6), (30.2, 8.6), (31.4, 6.1)], HULLN, base + 0.2)      # el pont
    poly([(21.5, 7.3), (21.5, 8.0), (30.4, 8.0), (30.7, 7.3)], STEELX, 1.4)        # vidres del pont
    if night:
        for m in (23, 25.5, 28):
            box(m, 7.3, m + 1.4, 8.0, [(10, 40, 34), (20, 70, 60), (40, 110, 90)], 1.0)
    poly([(20.6, 8.6), (20.6, 8.85), (31.0, 8.85), (31.0, 8.6)], HULLN, base + 1.3)
    poly([(16.2, 6.1), (16.6, 9.6), (19.6, 9.6), (19.4, 6.1)], HULLN, base + 0.6)  # la xemeneia
    poly([(16.55, 9.2), (16.6, 9.6), (19.6, 9.6), (19.55, 9.2)], STEELX, 1.0)
    if s >= 2.5:
        cv.disc(X(18), Y(7.8), 0.65 * s, 0.65 * s, REDH, 4.4 if night else 5.2, lit=0)
        cv.disc(X(18), Y(7.8), 0.36 * s, 0.36 * s, HULLN, base + 0.6, lit=0)
    # pal: radar i llums
    cv.line(X(27), Y(8.8), X(27), Y(16), STEELX, 4.0 if night else 5.6, lit=0)
    if s >= 3:
        cv.line(X(27) + 1, Y(8.8), X(27) + 1, Y(14), STEELX, 2.6 if night else 4.2, lit=0)
    cv.line(X(25.5), Y(13.5), X(28.5), Y(13.5), STEELX, 4.0 if night else 5.6, lit=0)   # creueta
    cv.line(X(25.8), Y(11.6), X(28.2), Y(11.6), STEELX, 3.2 if night else 4.8, lit=0)   # el radar
    cv.line(X(36.5), Y(sheer(36.5)), X(36.5), Y(9.6), STEELX, 3.4 if night else 5.0, lit=0)  # pal de proa
    cv.line(X(27), Y(15.6), X(40.4), Y(sheer(40.2) + 0.2), STEELX, 2.4 if night else 3.6, lit=0)  # estai
    cv.line(X(27), Y(15.6), X(2), Y(7.6), STEELX, 2.0 if night else 3.2, lit=0)
    # la grua de popa amb la zòdiac
    if crane:
        cv.line(X(3.2), Y(sheer(3)), X(3.2), Y(5.8), STEELX, 4.4 if night else 6.0, lit=0)
        cv.line(X(3.2), Y(5.8), X(0.2), Y(7.6), [(60, 46, 10), (130, 100, 20), (200, 160, 40), (236, 200, 80)],
                1.8 if night else 2.8, lit=0)
        if zodiac:
            cv.line(X(0.4), Y(7.5), X(0.4), Y(5.3), STEELX, 3.0, lit=0)
            cv.poly([(X(-1.4), Y(5.3)), (X(2.4), Y(5.3)), (X(2.0), Y(4.5)), (X(-1.0), Y(4.5))],
                    [(30, 30, 34), (52, 52, 56), (80, 80, 82), (110, 110, 110)], 1.6 if night else 2.8, lit=0)
    # llums
    if night:
        cv.glow(X(27), Y(15.6), 6, (255, 250, 230), 0.7)
        cv.flat(X(27), Y(15.6), (255, 250, 230))
        cv.glow(X(36.5), Y(9.6), 4, (255, 250, 230), 0.6)
        cv.flat(X(36.5), Y(9.6), (255, 250, 230))
        cv.glow(X(30.6), Y(7.0), 5, (60, 255, 120), 0.7)
        cv.flat(X(30.6), Y(7.0), (120, 255, 160))
        cv.glow(X(0.2), Y(3.8), 5, (255, 250, 230), 0.5)
        cv.flat(X(0.2), Y(3.8), (255, 250, 230))
        cv.glow(X(3.5), Y(5.8), 3 + s, GLOW_WARM, 0.25)                         # focus de coberta a popa
    return X, Y


def reflection(cv, x0, x1, ywl, depth, k=0.5, seed=7, waves=True):
    """Reflex de tot el que hi ha per sobre de ywl (entre x0 i x1) al mar, ondulat i trencat."""
    src = cv.img.copy().load()
    for y in range(ywl + 1, min(H, ywl + depth)):
        dy = y - ywl
        for x in range(max(0, x0), min(W, x1 + 1)):
            sx = x + round(math.sin(y * 0.8 + seed) * (0.6 + dy * 0.05))
            sy = ywl - dy
            if not (0 <= sx < W and 0 <= sy < H):
                continue
            if waves and hr(x // 3, y, seed) < 0.18 + dy / depth * 0.4:
                continue
            o = cv.get(x, y)
            kk = k * (1 - dy / depth)
            if kk > B4[y & 3][x & 3] * 0.6:
                cv.flat(x, y, mix(o, src[sx, sy][:3], kk))


# ─── La plataforma ──────────────────────────────────────────────────────────

def platform(cv, cx, ywl, s, mode='day', watcher=False):
    """La plataforma que no surt als mapes: quatre potes, la coberta, el mòdul amb el logotip tapat amb cinta
    americana, una grua i una torre. cx = centre, ywl = flotació, s = píxels per metre."""
    night = mode == 'night'
    b = 2.0 if night else 4.0

    def X(m):
        return cx + m * s

    def Y(m):
        return ywl - m * s

    def r(a, bb, c, d, ramp, lvl):
        cv.rect(round(X(a)), round(Y(d)), round(X(c)), round(Y(bb)), ramp, lvl, lit=0)

    # potes amb travessers
    for m in (-13, -5, 5, 13):
        r(m - 0.9, -0.5, m + 0.9, 9, STEELX, b)
        r(m - 0.9, -0.5, m - 0.3, 9, STEELX, b + 0.8)
        r(m - 0.9, -0.5, m + 0.9, 0.6, TURBID if not night else STEELX, b - 0.6)
    for k in range(2):
        y0, y1 = 2 + k * 3.5, 5.5 + k * 3.5
        cv.line(X(-13), Y(y0), X(-5), Y(y1), STEELX, b - 0.6, lit=0)
        cv.line(X(5), Y(y1), X(13), Y(y0), STEELX, b - 0.6, lit=0)
    # coberta
    r(-16, 9, 16, 11.5, STEELX, b + 0.4)
    r(-16, 11.2, 16, 11.5, STEELX, b + 1.6)
    # el mòdul (casetes) i el logotip tapat
    r(-12, 11.5, 6, 18, STEELX if night else DCLOUD, 1.4 if night else 2.6)
    r(-12, 17.5, 6, 18, STEELX if night else DCLOUD, 2.4 if night else 3.8)
    if s >= 1.5:
        for i, m in enumerate(range(-11, 6, 2)):
            if -7 <= m <= 1:
                continue
            on = night and hr(i, 3) > 0.4
            r(m, 13, m + 0.8, 14, WINDOW if on else STEELX, 3.0 if on else b - 1.2)
    # cinta americana damunt del logotip: tires grises en creu
    lx0, lx1, ly0, ly1 = -6.5, 0.5, 12.3, 17.0
    r(lx0, ly0, lx1, ly1, STEELX, b - 1.0)
    for k in range(3):
        yy = ly0 + 0.8 + k * (ly1 - ly0 - 1.6) / 2
        r(lx0 - 0.3, yy - 0.35, lx1 + 0.3, yy + 0.35, TAPE, 2.4 if night else 3.8)
    cv.line(X(lx0), Y(ly0), X(lx1), Y(ly1), TAPE, 2.0 if night else 3.0, lit=0)
    cv.line(X(lx0), Y(ly1), X(lx1), Y(ly0), TAPE, 2.0 if night else 3.0, lit=0)
    # una mica de vermell que se n'escapa
    cv.put(X(lx1) - 1, Y(ly0) - 1, REDH, 3.0, lit=0)
    # torre de gelosia
    for m in (8, 12):
        cv.line(X(m), Y(11.5), X(m + 1.6 if m == 8 else m - 1.6), Y(30), STEELX, b + 0.4, lit=0)
    for k in range(6):
        ya, yb = 11.5 + k * 3.1, 11.5 + (k + 1) * 3.1
        fa, fb = 8 + 1.6 * (ya - 11.5) / 18.5, 8 + 1.6 * (yb - 11.5) / 18.5
        ga, gb = 12 - 1.6 * (ya - 11.5) / 18.5, 12 - 1.6 * (yb - 11.5) / 18.5
        cv.line(X(fa), Y(ya), X(gb), Y(yb), STEELX, b - 0.4, lit=0)
        cv.line(X(ga), Y(ya), X(fb), Y(yb), STEELX, b - 0.4, lit=0)
    # la grua
    cv.line(X(-14), Y(11.5), X(-14), Y(16), STEELX, b + 0.6, lit=0)
    cv.line(X(-14), Y(16), X(-22), Y(23), [(60, 46, 10), (130, 100, 20), (200, 160, 40), (236, 200, 80)],
            1.4 if night else 2.4, lit=0)
    cv.line(X(-22), Y(23), X(-22), Y(17), STEELX, b - 0.6, lit=0)
    if night:
        cv.glow(X(10), Y(30), 4, (255, 40, 30), 0.8)
        cv.flat(X(10), Y(30), (255, 80, 60))
        for m in (-15, 15):
            cv.glow(X(m), Y(11.6), 5, GLOW_WARM, 0.5)
            cv.flat(X(m), Y(11.6), (255, 230, 170))
        cv.glow(X(-3), Y(11.6), 5 + s, (230, 236, 255), 0.3)
    if watcher:
        # una silueta amb prismàtics, a la barana, a contrallum
        fx = X(3.5)
        fy = Y(11.5)
        h = max(6, round(1.75 * s))
        cv.rect(fx - 1, fy - h, fx + 1, fy - 1, [(4, 5, 8)], 0, lit=0)
        cv.rect(fx - 2, fy - h + 2, fx + 2, fy - h // 2, [(4, 5, 8)], 0, lit=0)
        cv.disc(fx, fy - h - 1, 1.6, 1.6, [(4, 5, 8)], 0, lit=0)
        cv.rect(fx - 4, fy - h, fx - 2, fy - h + 1, [(4, 5, 8)], 0, lit=0)        # els prismàtics
        cv.flat(fx - 4, fy - h, (180, 200, 220))
        # el focus de darrere, que el retalla
        cv.rect(fx + 3, fy - h - 2, fx + 5, fy - h, [(255, 250, 230)], 0, lit=0)
        cv.glow(fx + 4, fy - h - 1, h * 2 + 4, (220, 226, 255), 0.45)
        cv.rect(fx - 1, fy - h, fx + 1, fy - 1, [(4, 5, 8)], 0, lit=0)
        cv.rect(fx - 2, fy - h + 2, fx + 2, fy - h // 2, [(4, 5, 8)], 0, lit=0)
        cv.disc(fx, fy - h - 1, 1.6, 1.6, [(4, 5, 8)], 0, lit=0)
        cv.rect(fx - 4, fy - h, fx - 2, fy - h + 1, [(4, 5, 8)], 0, lit=0)
        cv.flat(fx - 4, fy - h, (180, 200, 220))


def stain(cv, cx, ywl, rx, ry, k=0.6, seed=21):
    """La taca d'aigua tèrbola al voltant de la plataforma (de dia)."""
    for y in range(int(ywl - ry), int(ywl + ry) + 1):
        for x in range(int(cx - rx), int(cx + rx) + 1):
            if not (0 <= x < W and 0 <= y < H):
                continue
            nx, ny = (x - cx) / rx, (y - ywl) / ry
            d = nx * nx + ny * ny + (fbm(x / 9, y / 2, seed) - 0.5) * 0.9
            a = k * smooth(0.0, 0.45, 1 - d)
            if a > B4[y & 3][x & 3] * 0.9:
                o = cv.get(x, y)
                cv.flat(x, y, mix(o, TURBID[3 if hr(x // 4, y) > 0.3 else 4], min(0.6, a)))


def gull(cv, x, y, col=(230, 232, 228), wing=1):
    """Una gavina llunyana: una «v» de tres o quatre píxels."""
    cv.flat(x, y, col)
    cv.flat(x - 1, y - wing, col)
    cv.flat(x + 1, y - wing, col)
    cv.flat(x - 2, y - wing, mix(col, (120, 120, 120), 0.4))
    cv.flat(x + 2, y - wing, mix(col, (120, 120, 120), 0.4))


# ─── Peces de coberta (les fan servir coberta_popa i coberta_proa) ─────────
DECKX = [(8, 10, 10), (14, 17, 17), (22, 26, 25), (32, 37, 35), (44, 50, 47), (58, 65, 60), (76, 83, 76),
         (98, 104, 95), (124, 128, 118), (152, 154, 142)]
ORANGEB = [(40, 12, 6), (84, 26, 10), (140, 48, 16), (196, 80, 26), (232, 118, 44), (250, 164, 90)]
ROPE = [(30, 24, 16), (60, 48, 30), (98, 82, 54), (140, 122, 86), (182, 166, 124), (214, 202, 164)]
VP = (240, 40)


def deck_floor(cv, y0=152, y1=206, base=2.4, x0=0, x1=W - 1):
    """La coberta: planxa pintada de verd grisós amb antilliscant, juntes en perspectiva i camins gastats."""
    for y in range(y0, y1 + 1):
        d = y - VP[1]
        for x in range(x0, x1 + 1):
            u = VP[0] + (x - VP[0]) * 150 / d
            u2 = VP[0] + (x + 1 - VP[0]) * 150 / d
            lvl = base + (hr(x, y, 41) - 0.5) * 0.7
            if int(u // 90) != int(u2 // 90):
                lvl -= 1.3
            elif y in (163, 181):
                lvl -= 1.2
            elif y in (164, 182):
                lvl += 0.6
            if y < y0 + 5:                                   # el canal d'aigua al peu de la borda
                lvl -= 1.0 - (y - y0) * 0.15
            # camí gastat (més clar, la pintura se'n va)
            if 168 <= y <= 190 and fbm(x / 30, y / 6, 43) > 0.55:
                lvl += 0.5
            cv.put(x, y, DECKX, lvl)
            # rovell als junts i escates de pintura
            if hr(x // 2, y, 44) > 0.997:
                cv.put(x, y, [(30, 22, 16), (52, 36, 24), (74, 50, 32)], 0.6 + base * 0.2)


def bulwark(cv, x0, x1, ytop=106, ybot=152, base=2.8, scuppers=(), seed=5):
    """La borda per dins: planxa blanca amb cartel·les, la regala vermella a dalt i els frisos (escopidors)."""
    for y in range(ytop + 5, ybot):
        for x in range(x0, x1 + 1):
            lvl = base + (hr(x // 4, y // 6, seed) - 0.5) * 0.25 - (y - ytop) * 0.008
            cv.put(x, y, HULLN, lvl)
    for sx in range(x0 - x0 % 26 + 10, x1, 26):                     # cartel·les (reforços)
        if sx < x0 + 2 or sx > x1 - 4:
            continue
        for y in range(ytop + 5, ybot):
            w = 2 + (y - ytop - 5) * 4 // (ybot - ytop - 5)
            for dx in range(w):
                cv.put(sx + dx, y, HULLN, base + (0.9 if dx == 0 else -0.6 if dx == w - 1 else 0.2))
    for sx in scuppers:                                          # escopidors: forats al peu, amb el mar a fora
        for y in range(ybot - 7, ybot):
            for x in range(sx, sx + 14):
                cv.put(x, y, NSEA if cv.light(x, y) < 3 else DSEA, 1.6 + hr(x, y, 3) * 1.4, lit=0.4)
        cv.hline(sx - 1, sx + 14, ybot - 8, HULLN, base + 1.2)
        cv.vline(sx - 1, ybot - 7, ybot - 1, HULLN, base - 1.0)
        for i in range(8):                                       # rovell que en baixa
            rx = sx + int(hr(sx, i) * 14)
            for y in range(ybot - 9 - int(hr(i, sx) * 6), ybot - 7):
                cv.flat(rx, y, mix(cv.get(rx, y), RUST_[2], 0.35))
    # regala (vermella, l'únic vermell de la coberta)
    cv.rect(x0, ytop, x1, ytop + 4, REDH, lambda x, y: 3.4 + (1.4 if y == ytop else 0.6 if y == ytop + 1 else -0.8 if y == ytop + 4 else 0))
    cv.hline(x0, x1, ytop + 5, HULLN, base - 1.6)
    # taques de rovell sota la regala
    for i in range(int((x1 - x0) / 9)):
        rx = x0 + int(hr(i, seed, 7) * (x1 - x0))
        n = 3 + int(hr(i, seed, 8) * 12)
        for y in range(ytop + 6, ytop + 6 + n):
            k = 0.4 * (1 - (y - ytop - 6) / n)
            if k > B4[y & 3][rx & 3] * 0.5:
                cv.flat(rx, y, mix(cv.get(rx, y), RUST_[3], k))


RUST_ = [(30, 14, 12), (58, 26, 18), (92, 42, 24), (128, 62, 32), (164, 88, 44), (196, 122, 64)]


def rrect_frame(cv, x0, y0, x1, y1, r, ramp, lvl, t=3):
    """Marc de porta estanca de cantons rodons (t píxels de gruix, cap a fora)."""
    for k in range(t):
        for y in range(y0 - k, y1 + 1):
            for x in range(x0 - k, x1 + k + 1):
                dx = max(x0 - k + r - x, 0, x - (x1 + k - r))
                dy = max(y0 - k + r - y, 0)
                inside = dx * dx + dy * dy <= r * r
                ddx = max(x0 - k + 1 + r - x, 0, x - (x1 + k - 1 - r))
                ddy = max(y0 - k + 1 + r - y, 0)
                inner = x0 - k + 1 <= x <= x1 + k - 1 and y >= y0 - k + 1 and ddx * ddx + ddy * ddy <= r * r
                if inside and not inner:
                    cv.put(x, y, ramp, lvl - k * 0.8 + (0.6 if y < y0 + r else 0))


def wt_door(cv, x0, y0, x1, y1, ramp=HULLN, base=3.0, window=True, warm=True):
    """Porta estanca tancada: fulla de cantons rodons, ull de bou, sis palanques i el llindar alt."""
    r = 8
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            dx = max(x0 + r - x, 0, x - (x1 - r))
            dy = max(y0 + r - y, 0)
            if dx * dx + dy * dy <= r * r:
                lvl = base - 0.5 + (0.5 if x < x0 + 3 else -0.6 if x > x1 - 3 else 0) + (hr(x // 3, y // 4) - 0.5) * 0.2
                cv.put(x, y, ramp, lvl)
    # costelles de la fulla
    for yy in (y0 + 30, y0 + 56):
        if yy < y1 - 8:
            cv.hline(x0 + 4, x1 - 4, yy, ramp, base + 0.8)
            cv.hline(x0 + 4, x1 - 4, yy + 1, ramp, base - 1.2)
    rrect_frame(cv, x0, y0, x1, y1, r, ramp, base + 1.0)
    # palanques («dogs»)
    for dy in (14, (y1 - y0) // 2, y1 - y0 - 18):
        for xx, d in ((x0 + 1, 1), (x1 - 4, -1)):
            cv.rect(xx, y0 + dy, xx + 3, y0 + dy + 2, CABX, 3.6)
            cv.put(xx + (3 if d > 0 else 0), y0 + dy + 3, CABX, 2.4)
    # maneta central
    cv.rect((x0 + x1) // 2 + 6, y0 + (y1 - y0) // 2 - 2, (x0 + x1) // 2 + 12, y0 + (y1 - y0) // 2, CABX, 3.4)
    if window:
        cx, cy = (x0 + x1) // 2, y0 + 18
        cv.disc(cx, cy, 7, 7, CABX, lambda nx, ny: 3.8 - nx - ny)
        if warm:
            cv.disc(cx, cy, 5, 5, WINDOW, lambda nx, ny: 2.6 - ny * 0.8 + (0.8 if nx < -0.2 and ny < -0.2 else 0), lit=0)
            cv.glow(cx, cy, 14, GLOW_WARM, 0.25)
        else:
            cv.disc(cx, cy, 5, 5, STEELX, lambda nx, ny: 1.6 - ny * 0.6, lit=0.5)
        cv.put(cx - 2, cy - 2, [(255, 250, 230)], 0, lit=0)
    # el llindar alt
    cv.rect(x0 - 2, y1 - 5, x1 + 2, y1, ramp, base - 0.6)
    cv.hline(x0 - 2, x1 + 2, y1 - 5, ramp, base + 1.4)


CABX = [(8, 10, 12), (15, 17, 21), (24, 27, 32), (35, 39, 45), (49, 54, 60), (66, 71, 77), (88, 93, 98),
        (116, 120, 124), (150, 154, 156)]


def deck_lamp(cv, x, y, on=True):
    """Focus de coberta: caixa amb reixeta, mirant avall."""
    cv.rect(x - 6, y - 4, x + 6, y, CABX, 3.0)
    cv.hline(x - 6, x + 6, y - 4, CABX, 4.4)
    cv.rect(x - 2, y - 7, x + 2, y - 5, CABX, 2.2)
    if on:
        cv.rect(x - 5, y + 1, x + 5, y + 2, LAMP, 2.6, lit=0)
        cv.glow(x, y + 3, 16, GLOW_WARM, 0.45)
        cv.glow(x, y + 3, 6, (255, 240, 200), 0.6)
    else:
        cv.rect(x - 5, y + 1, x + 5, y + 2, CABX, 4.0)


def lifebuoy(cv, cx, cy, r=8):
    """Salvavides taronja i blanc penjat d'un suport."""
    for y in range(cy - r - 1, cy + r + 2):
        for x in range(cx - r - 1, cx + r + 2):
            d = math.hypot(x - cx, y - cy)
            if r * 0.5 <= d <= r:
                a = math.degrees(math.atan2(y - cy, x - cx)) % 360
                band = int((a + 22) // 45) % 2
                u = (d - r * 0.75) / (r * 0.25)
                lvl = 3.4 - u * 0.8 - (y - cy) / r * 0.8
                cv.put(x, y, HULLN if band else ORANGEB, lvl + (3.0 if band else 0))
    cv.rect(cx - 1, cy - r - 4, cx + 1, cy - r, CABX, 3.0)
    for a in range(0, 360, 30):                                  # el cap que l'envolta
        cv.put(cx + round(math.cos(math.radians(a)) * (r * 0.78)), cy + round(math.sin(math.radians(a)) * (r * 0.78)),
               ROPE, 3.4)


def coil(cv, cx, cy, rx=12, ry=4):
    """Un rotllo de cap a coberta: voltes concèntriques, amb el forat al mig."""
    cv.disc(cx, cy + 1, rx + 1, ry + 1, DECKX, 0.6)                    # ombra
    for k in range(5):
        r1, r2 = rx - k * 2, ry - k * 0.7
        for a in range(0, 360, 3):
            x = cx + math.cos(math.radians(a)) * r1
            y = cy - 1 - k * 0.4 + math.sin(math.radians(a)) * r2
            cv.put(round(x), round(y), ROPE, 3.0 - math.sin(math.radians(a)) * 0.9 + (0.6 if k % 2 else 0))
    cv.disc(cx, cy - 3, 3, 1, DECKX, 1.0)
    cv.line(cx + rx - 1, cy, cx + rx + 6, cy + 3, ROPE, 2.8)               # el xicot que en surt


def bitts(cv, x, ybase, base=2.6):
    """Bita doble per amarrar (dues columnes amb volum)."""
    cv.rect(x - 2, ybase - 2, x + 22, ybase + 1, HULLN, base - 1.4)
    for bx in (x + 2, x + 15):
        for yy in range(ybase - 18, ybase - 1):
            for dx in range(6):
                u = (dx - 2.5) / 3
                cv.put(bx + dx, yy, STEELX, base + 1.6 - u * 1.4 - u * u)
        cv.disc(bx + 2.5, ybase - 18, 3.5, 1.3, STEELX, base + 2.6)
