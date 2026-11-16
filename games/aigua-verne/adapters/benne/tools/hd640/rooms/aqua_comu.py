"""
Aigua Verne — peces comunes de les sales d'Aqua (aqua_port, aqua_fons, casa_juana).

Aqua era un planeta oceànic i ara és un desert de sal: blancs de sal amb ombres blau pàl·lid, pedra calcària del
port, el fons del mar sec. Llum freda de migdia (el sol a dalt, gairebé a plom: ombres curtes, a sota de les coses).

Aquí hi ha les rampes (fosc → clar), el cel, la plana de sal, la Canonada d'Aqua, el panell del preu, la gota de
Verne, un «shader» per dibuixar coses girades (vaixells inclinats) sense trencar el dithering, i les eines per fer
els fotogrames de les animacions.
"""
import math

import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

from hd.pix import Canvas, W, H, hr, mix, B4
from hd.rooms.comu import text, text_width, GLYPHS
from hd.rooms.exterior import fbm, smooth

RH = 260                      # la sala (de 260 a 359, la barra de verbs: negre)

# ─── Rampes (fosc → clar) ───────────────────────────────────────────────────
SKYA = [(92, 124, 158), (112, 144, 176), (134, 164, 194), (156, 184, 210), (178, 202, 224), (198, 218, 234),
        (216, 230, 242), (232, 240, 248), (246, 249, 252)]
SALT = [(66, 80, 98), (94, 110, 128), (124, 140, 156), (154, 168, 182), (182, 194, 204), (206, 214, 222),
        (226, 232, 236), (242, 245, 246), (253, 253, 251)]
SAND = [(92, 86, 78), (122, 116, 104), (152, 146, 130), (182, 176, 158), (206, 200, 182), (226, 221, 204),
        (240, 236, 222), (250, 248, 238)]
STONEA = [(36, 40, 48), (56, 60, 68), (80, 84, 90), (106, 108, 112), (132, 134, 136), (158, 158, 158),
          (182, 182, 178), (204, 204, 198), (224, 224, 218), (240, 240, 234)]
ALGAS = [(34, 34, 30), (52, 52, 44), (72, 70, 58), (94, 90, 74), (116, 112, 92), (138, 134, 112)]
ALGA = [(26, 32, 30), (42, 50, 44), (60, 70, 58), (82, 90, 72), (106, 112, 90), (132, 134, 108)]
WOODG = [(30, 28, 30), (48, 46, 46), (70, 66, 62), (94, 88, 80), (120, 112, 100), (146, 138, 122),
         (172, 166, 148), (198, 192, 174)]
TEALH = [(14, 34, 40), (22, 52, 60), (34, 74, 82), (52, 98, 104), (76, 124, 126), (106, 150, 148), (144, 178, 172)]
REDF = [(46, 18, 20), (76, 30, 30), (108, 46, 42), (140, 66, 56), (168, 90, 74), (192, 120, 100), (214, 154, 134)]
PAINTW = [(70, 80, 92), (106, 116, 128), (142, 150, 160), (176, 182, 190), (204, 208, 214), (226, 229, 233),
          (244, 245, 247)]
RUSTA = [(34, 18, 14), (62, 32, 20), (96, 50, 28), (130, 72, 38), (162, 98, 54), (190, 128, 76), (214, 160, 108)]
OCHRE = [(48, 34, 14), (84, 62, 24), (124, 94, 38), (162, 126, 56), (194, 158, 80), (218, 188, 112),
         (236, 214, 150)]
OLIVEN = [(20, 24, 14), (34, 40, 22), (52, 60, 34), (72, 82, 48), (96, 106, 64), (122, 130, 84), (150, 156, 108)]
ORANGEN = [(56, 20, 8), (104, 40, 12), (156, 64, 18), (204, 96, 30), (234, 132, 52), (250, 174, 96)]
STEELA = [(14, 16, 22), (26, 30, 38), (40, 46, 56), (58, 66, 76), (80, 88, 98), (106, 114, 122), (136, 142, 148),
          (170, 174, 178)]
BLACKT = [(8, 9, 12), (18, 20, 24), (30, 32, 38), (46, 48, 54), (66, 68, 74)]
BLUEV = [(10, 30, 70), (20, 60, 130), (40, 100, 190), (90, 160, 230), (170, 210, 250)]
LEDO = [(30, 6, 4), (90, 24, 8), (180, 60, 16), (250, 130, 40), (255, 200, 120)]
COL = [(128, 136, 146), (156, 164, 172), (184, 190, 196), (206, 210, 214), (226, 229, 232), (242, 244, 246),
       (252, 252, 252)]
GLASSD = [(16, 24, 34), (28, 40, 54), (44, 60, 78), (66, 86, 106), (100, 122, 140), (150, 170, 184)]
WATERB = [(24, 52, 78), (38, 76, 108), (60, 104, 140), (92, 138, 172), (132, 172, 202), (180, 208, 228),
          (226, 240, 248)]
ROPEA = [(40, 34, 26), (70, 60, 44), (104, 92, 68), (140, 128, 98), (176, 166, 134), (206, 198, 170)]
WICKER = [(38, 28, 18), (64, 48, 28), (94, 72, 42), (126, 100, 60), (156, 128, 82), (186, 158, 108)]
BONE = [(96, 92, 84), (136, 132, 120), (176, 172, 158), (210, 206, 190), (234, 230, 216), (250, 248, 238)]
WARMW = [(255, 204, 120), (255, 226, 160), (255, 244, 210)]


# ─── Text ──────────────────────────────────────────────────────────────────

def text180(cv, s, x, y, ramp, lvl, lit=1.0):
    """El text girat de cap per avall (el nom d'un vaixell bolcat). (x, y): el cantó de dalt a l'esquerra."""
    w = text_width(s)
    cx = 0
    for ch in s:
        g = GLYPHS.get(ch, GLYPHS[' '])
        for j, row in enumerate(g):
            for i, bit in enumerate(row):
                if bit == '1':
                    cv.put(x + w - 1 - (cx + i), y + 4 - j, ramp, lvl, lit)
        cx += len(g[0]) + 1
    return w


# ─── El cel i la plana de sal ──────────────────────────────────────────────

def cel(cv, hor, x0=0, x1=W - 1, seed=5, top=0):
    """Cel fred de migdia: blau pàl·lid a dalt, gairebé blanc a l'horitzó (la calitja de sal), amb uns quants
    cirrus prims i plans."""
    for y in range(top, hor + 1):
        t = (y - top) / max(1, hor - top)
        for x in range(x0, x1 + 1):
            lvl = 2.2 + 5.6 * t ** 1.6
            c = fbm(x / 120, y / 7, seed)
            k = smooth(0.58, 0.72, c) * (1 - t) * 0.9
            if k > 0:
                streak = fbm(x / 26, y / 2.2, seed + 3)
                lvl += k * (1.4 + streak * 1.6)
            lvl += (fbm(x / 60, y / 20, seed + 7) - 0.5) * 0.3
            cv.put(x, y, SKYA, lvl, lit=0)


def _voronoi(gx, gy, seed=3):
    """(distància a la vora, id de la cel·la) d'una graella de Voronoi: les crostes poligonals de la sal."""
    ix, iy = math.floor(gx), math.floor(gy)
    best, second, cid = 9.0, 9.0, (0, 0)
    for j in (-1, 0, 1):
        for i in (-1, 0, 1):
            cx = ix + i + hr(ix + i, iy + j, seed)
            cy = iy + j + hr(ix + i, iy + j, seed + 1)
            d = math.hypot(gx - cx, gy - cy)
            if d < best:
                best, second, cid = d, best, (ix + i, iy + j)
            elif d < second:
                second = d
    return second - best, cid


def plana(cv, hor, y1, x0=0, x1=W - 1, seed=3, mask=None):
    """La plana de sal fins a l'horitzó: crostes poligonals en perspectiva (les vores, una mica aixecades i més
    blanques), taques de fang gris del fons del mar, rierols secs, i la calitja blanca a tocar de l'horitzó."""
    for y in range(hor + 1, y1 + 1):
        dz = (y - hor) + 1.5
        z = 1.0 / dz                       # profunditat: lluny a dalt
        near = smooth(4, 60, y - hor)
        for x in range(x0, x1 + 1):
            if mask and not mask(x, y):
                continue
            gx = (x - 320) * z * 2.7
            gy = 930 * z
            lvl = 5.6 + near * 0.6
            mud = fbm(gx * 0.12 + 3, gy * 0.05, seed + 9)
            lvl -= smooth(0.52, 0.72, mud) * 1.8
            riu = abs(fbm(gx * 0.05 + 7, gy * 0.012, seed + 4) - 0.5)                  # un rierol sec
            if riu < 0.018 + 0.01 * near:
                lvl -= 1.4
            elif riu < 0.03 + 0.012 * near:
                lvl += 0.5
            edge, cid = _voronoi(gx, gy, seed)
            if near > 0.05:
                if edge < 0.05:
                    lvl += 0.9 * near
                elif edge < 0.11:
                    lvl -= 0.6 * near
                lvl += (hr(*cid, seed) - 0.5) * 0.6 * near
            lvl += (hr(x, y, seed + 5) - 0.5) * 0.3
            haze = 1 - smooth(0, 10, y - hor)
            lvl = lvl * (1 - haze) + 6.6 * haze
            if y - hor <= 2 and hr(x // 6, y, seed + 6) > 0.3:
                lvl = 4.6 + (y - hor) * 0.6                                       # la ratlla blavosa de l'horitzó
            cv.put(x, y, SALT, lvl)


# ─── La Canonada d'Aqua ─────────────────────────────────────────────────────

def canonada(cv, x, hor, top=0, w0=2.4, w1=5.0, base=True, light_y=24):
    """La columna blanca de Verne, de l'horitzó fins més amunt del cel: anelles, el costat a l'ombra blavós i la
    boira de sal a la base. El llum vermell del cim és una animació (vegeu `canonada_llum`)."""
    for y in range(top, hor + 1):
        tt = (y - top) / max(1, hor - top)
        w = w0 + (w1 - w0) * tt
        for xx in range(int(x - w), int(x + w) + 1):
            u = (xx - x) / max(1.0, w)
            lvl = 4.2 - u * 1.6 - u * u * 0.8 + (0.9 if y % 15 == 0 else 0) - (0.7 if y % 15 == 1 else 0)
            cv.put(xx, y, COL, lvl, lit=0)
    cv.tint(x - 9, top, x + 9, hor, (236, 242, 246), lambda xx, yy: 0.45 * ((yy - top) / max(1, hor - top)) ** 2)
    if base:
        bw = int(w1 * 2.6)
        cv.rect(x - bw, hor - 6, x + bw, hor, COL, lambda xx, yy: 3.0 - (0.8 if xx > x + bw - 3 else 0), lit=0)
        cv.rect(x - bw, hor - 7, x + bw, hor - 7, COL, 5.2, lit=0)
        cv.tint(x - bw - 6, hor - 9, x + bw + 6, hor, (232, 238, 244), 0.35)
    cv.flat(x, light_y, (110, 30, 30))


def canonada_llum(x, y, on=True, C=Canvas):
    """Un fotograma del llum vermell del cim de la Canonada (transparent). `C`: el Canvas de la sala (1× o 2×)."""
    cv = C(transparent=True)
    if on:
        cv.flat(x, y, (255, 70, 50))
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            for X, Y, _, _ in cv.pixels(x + dx, y + dy, x + dx, y + dy):
                cv.P[X, Y] = (255, 110, 90, 150)
    return cv.img


# ─── Verne: la gota i el panell del preu ───────────────────────────────────

def gota(cv, cx, cy, r=3, lit=0):
    """La gota blava de Verne (punta a dalt). (cx, cy): el centre de la part rodona."""
    cv.disc(cx, cy, r, r, BLUEV, lambda nx, ny: 2.6 - nx * 0.8 - ny * 0.6, lit=lit)
    for k in range(1, r + 2):
        hw = r * (1 - k / (r + 2))
        for xx in range(int(round(cx - hw)), int(round(cx + hw)) + 1):
            cv.put(xx, cy - r + 1 - k, BLUEV, 2.8 - (xx - cx) * 0.4, lit=lit)
    cv.put(cx - max(1, r // 2), cy - 1, BLUEV, 4.4, lit=lit)


def panell(cv, x0, y0, post_to=None, w=46, h=22):
    """El panell del preu: pantalla negra amb marc de llauna, la gota blava i VERNE, la fletxa ▲ taronja i una
    barra de nivell. Sense xifra: el preu canvia durant el joc i es diu en mirar-lo."""
    x1, y1 = x0 + w, y0 + h
    if post_to:
        cx = (x0 + x1) // 2
        cv.rect(cx - 1, y1, cx + 1, post_to, STEELA, lambda x, y: 4.4 - (x - cx + 1) * 1.0)
        cv.rect(cx - 4, post_to - 2, cx + 4, post_to, STONEA, 4.0)
    cv.rect(x0 - 1, y0 - 1, x1 + 1, y1 + 1, STEELA, lambda x, y: 5.0 if y == y0 - 1 else 3.0)
    cv.rect(x0, y0, x1, y1, BLACKT, lambda x, y: 1.2 + (0.6 if (x + y) % 7 == 0 else 0), lit=0)
    cv.hline(x0, x1, y0, BLACKT, 3.2, lit=0)                          # reflex del sol al vidre
    gota(cv, x0 + 6, y0 + 8, 2)
    text(cv, 'VERNE', x0 + 11, y0 + 3, None, 0, flat=(206, 220, 238))
    for i in range(x0 + 5, x1 - 10):                                  # la barra de nivell, en taronja
        lit_ = i < x0 + 5 + (x1 - 15 - x0) * 0.7
        for j in range(y0 + 12, y0 + 16):
            cv.flat(i, j, LEDO[3] if lit_ and (i % 2 == 0 or j % 2 == 0) else LEDO[1])
    xx = x1 - 7
    for j in range(3):                                                # ▲
        for i in range(-j, j + 1):
            cv.flat(xx + i, y0 + 12 + j, LEDO[3])
    for x in range(x0 + 1, x1):                                       # línies de la pantalla
        if hr(x, 3) > 0.6:
            cv.flat(x, y1 - 1, (24, 26, 30))
    cv.rect(x1 + 2, y0 + 2, x1 + 2, y1 + 1, BLACKT, 1.0, lit=0)       # l'ombra curta del panell


# ─── Coses girades sense trencar el dithering ──────────────────────────────

def shade(cv, bbox, cx, cy, ang, fn, lit=1.0):
    """Dibuixa una cosa descrita en coordenades locals (u, v), girada `ang` radians al voltant de (cx, cy) de la
    pantalla. `fn(u, v)` → (rampa, nivell) o None. Es pinta píxel a píxel a la pantalla: el dithering queda net."""
    ca, sa = math.cos(ang), math.sin(ang)
    x0, y0, x1, y1 = bbox
    for y in range(int(y0), int(y1) + 1):
        for x in range(int(x0), int(x1) + 1):
            dx, dy = x - cx, y - cy
            u = dx * ca + dy * sa
            v = -dx * sa + dy * ca
            r = fn(u, v)
            if r:
                cv.put(x, y, r[0], r[1], lit)


def to_screen(u, v, cx, cy, ang):
    ca, sa = math.cos(ang), math.sin(ang)
    return cx + u * ca - v * sa, cy + u * sa + v * ca


# ─── Animacions ────────────────────────────────────────────────────────────

def diff(frame, base):
    """Només els píxels que canvien respecte del fons (la resta, transparent)."""
    out = frame.copy()
    a, b, o = frame.load(), base.load(), out.load()
    for y in range(frame.height):
        for x in range(frame.width):
            if a[x, y] == b[x, y]:
                o[x, y] = (0, 0, 0, 0)
    return out


def calitja_frames(base, x0, x1, y0, y1, n=8, amp=1.0, seed=0):
    """La calitja de la sal a l'horitzó: les files tremolen un píxel a banda i banda. → fotogrames transparents.
    (x0, x1, y0, y1): en coordenades de sala; `base` pot ser l'art a 2× (llavors cada fila de sala en són S)."""
    S = base.width // W
    src = base.load()
    frames = []
    for i in range(n):
        out = base.copy()
        o = out.load()
        for Y in range(y0 * S, (y1 + 1) * S):
            y = Y // S
            off = round(amp * math.sin(i / n * 2 * math.pi + y * 1.7 + seed) * (0.6 + 0.4 * hr(y, seed))) * S
            if off == 0:
                continue
            for X in range(x0 * S, (x1 + 1) * S):
                sx = min((x1 + 1) * S - 1, max(x0 * S, X - off))
                o[X, Y] = src[sx, Y]
        frames.append(diff(out, base))
    return frames


def pols_frames(n, parts, area, seed=0, col=(250, 252, 252), C=Canvas):
    """Pols de sal que passa amb el vent: punts blancs, de vegades parelles, que travessen `area` d'esquerra a
    dreta. El bucle tanca: cada gra fa una o dues voltes senceres en `n` fotogrames. Transparents. `C`: el Canvas
    de la sala (1× o 2×)."""
    x0, y0, x1, y1 = area
    w = x1 - x0
    frames = []
    for i in range(n):
        cv = C(transparent=True)
        for k in range(parts):
            sx = hr(k, seed) * w
            sy = y0 + hr(k, seed + 1) * (y1 - y0)
            sp = 1 if hr(k, seed + 2) < 0.7 else 2
            x = x0 + (sx + i * w / n * sp) % w
            y = sy + math.sin(i / n * 2 * math.pi * sp + k) * 2
            a = int(110 + 130 * hr(k, seed + 3))
            if 0 <= int(y) < H:
                for X, Y, _, _ in cv.pixels(int(x), int(y), int(x), int(y)):
                    cv.P[X, Y] = col + (a,)
                if hr(k, seed + 4) > 0.6 and int(x) + 1 < W:
                    for X, Y, _, _ in cv.pixels(int(x) + 1, int(y), int(x) + 1, int(y)):
                        cv.P[X, Y] = col + (a // 2,)
        frames.append(cv.img)
    return frames


# ─── Contorn ───────────────────────────────────────────────────────────────

def amb_contorn(cv, draw, k=0.42, diag=False):
    """Dibuixa amb `draw(canvas)` en un llenç a part i hi posa el contorn fosc d'1 px (el color del veí, enfosquit)
    abans d'enganxar-ho a `cv`. L'estil de dibuix animat de la casa. A 2×, el contorn fa S píxels reals (1 de sala)."""
    S = cv.S
    tmp = type(cv)(cv.w // S, cv.h // S, light=cv.light, transparent=True)
    draw(tmp)
    src = tmp.img
    bbox = src.getbbox()
    if not bbox:
        return
    px = src.load()
    out = src.copy()
    o = out.load()
    nb = ((-1, 0), (1, 0), (0, -1), (0, 1)) + (((-1, -1), (1, -1), (-1, 1), (1, 1)) if diag else ())
    nb = tuple((dx * k, dy * k) for k in range(1, S + 1) for dx, dy in nb)
    for y in range(max(0, bbox[1] - S), min(cv.h, bbox[3] + S)):
        for x in range(max(0, bbox[0] - S), min(cv.w, bbox[2] + S)):
            if px[x, y][3]:
                continue
            for dx, dy in nb:
                xx, yy = x + dx, y + dy
                if 0 <= xx < cv.w and 0 <= yy < cv.h and px[xx, yy][3]:
                    c = px[xx, yy]
                    o[x, y] = (int(c[0] * k), int(c[1] * k), int(c[2] * k), 255)
                    break
    cv.img.alpha_composite(out)
    cv.P = cv.img.load()
