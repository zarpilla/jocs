"""
Final 3 · «Correspondència» (hd/rooms/final_cargol.py) a 640×360: la mateixa composició ×4/3, dibuixada de nou.
Pla proper al moll de l'Estació d'Orís (final_estacio). En Cargol, vell i rovellat, amb la placa «CARGOL» que l'Iri
li va gravar al pit, allarga la pinça amb una carta plegada mil vegades, groguenca; la mà de la Vet hi arriba des de
fora de quadre. Al fons, el finestral amb la Terra enorme, un tros del rètol i la directora jove que s'ho mira. El
fons és més pàl·lid i suau (desenfocat), perquè el que importa és a primer pla.
Llums: el sol que entra pel finestral (de l'esquerra, càlid), la Terra (blava, per la dreta), els ulls d'en Cargol.
Pantalla sencera (sense barra de verbs).
En Cargol i la mà de la Vet són figures (FigK) amb les ordres de 480 dibuixades a ×4/3; els detalls de píxel solt
(els ulls, la reixeta de la boca, les ungles, el nom gravat) es dibuixen a part, en píxels reals.
"""
import hd640  # noqa: F401  (abans que cap hd.*: posa la llibreria de dibuix a 640×360)

import math
import random
from functools import lru_cache

import numpy as np
from PIL import Image, ImageOps

from hd.pix import Canvas, Light, B4, W, H, hr, mix, ramp
from hd640.rooms.proleg_gavina import espai, terra
from hd640.rooms.final_estacio import (WALLW, DECK, MINT, text5_px, text5_width, bulb_sign, planter,  # noqa: F401
                                       reflect, shadow, stamp, vinyeta, _person, K)
from hd640.draw_characters import (FigK, f, M, Mat, SCREEN, RUBBER, RUSTY, RUST_BRASS, LAMP_OLD, spiral_lvl,
                                   SKIN_VET, ORANGE, INK)

hr = lru_cache(maxsize=1 << 19)(hr)

LIGHT = Light(ambient=0.8, vignette=(80, 40), floor_fade=(320, 80))
LIGHT.point(80, 53, r=347, k=1.0)                                  # el sol pel finestral
LIGHT.point(573, 267, r=267, k=0.6)                                # la Terra

FLOOR_Y = 285
WIN = (-13, 88, 653, 272)
MULLIONS = (200, 440)
EARTH = (603, 448, 333)
SIGN_K = 20 / 3                    # 5 a 480: cada bombeta, de 6 o 7 píxels
HAZE = (214, 222, 236)


# ─── Fons (desenfocat: menys contrast, una boirina clara) ──────────────────

@lru_cache(maxsize=None)
def _static():
    """La part del fons que no es mou (abans de les jardineres): sostre, rètol, finestral i paret de sota."""
    cv = Canvas(light=LIGHT)
    X0, Y0, X1, Y1 = WIN
    # sostre i biga del rètol
    for y in range(0, Y0):
        for x in range(W):
            cv.put(x, y, WALLW, 5.0 - (0.0 if y > 5 else 1.2) + (hr(x // 80, 2) - 0.5) * 0.3, 0.4)
    # el rètol, de prop: «ESTACIÓ D'ORÍS» a escala gran (en surt un tros)
    txt = "ESTACIÓ D'ORÍS"
    w = text5_width(txt, SIGN_K)
    sx0 = 315 - w // 2 - 80
    for y in range(3, 77):
        for x in range(W):
            lvl = 5.6 - (y - 3) * 0.015
            if y == 3:
                lvl = 7.4
            elif y == 4:
                lvl = 6.6
            elif y >= 75:
                lvl = 2.0
            cv.put(x, y, WALLW, lvl, 0.3)
    cv.hline(0, W - 1, 72, MINT, 4.6, 0)
    cv.hline(0, W - 1, 73, MINT, 3.4, 0)
    bulb_sign(cv, txt, sx0, 24, SIGN_K, glow=False)
    pts, _ = text5_px(txt, sx0, 24, SIGN_K)
    for x, y, _a in pts[::2]:
        cv.glow(x + 3, y + 3, 15, (255, 220, 150), 0.18)
    cv.darken(0, 77, W - 1, 83, lambda x, y: 0.7 - (y - 77) * 0.13)
    # el finestral: l'espai i la Terra, enorme
    sky = Canvas()
    espai(sky, 0, W - 1, seed=23)
    terra(sky, EARTH[0], EARTH[1], EARTH[2])
    S = sky.P
    for y in range(Y0, Y1 + 1):
        for x in range(W):
            cv.flat(x, y, S[x, y])
    cv.tint(0, Y0, W - 1, Y1, (200, 230, 255), lambda x, y: 0.10 if (x + y * 0.6) % 187 < 21 else 0)
    # muntants i marc
    for mx in MULLIONS:
        for y in range(Y0 - 5, Y1 + 8):
            for x in range(mx - 9, mx + 9):
                u = (x - mx + 9) / 17
                cv.put(x, y, WALLW, 6.6 - u * 3.2 + (0.8 if x == mx - 8 else 0) - (0.6 if x == mx + 8 else 0))
    for y in range(Y0 - 5, Y0):
        for x in range(W):
            cv.put(x, y, WALLW, 6.6 - (y - Y0 + 5) * 0.72)
    for y in range(Y1, FLOOR_Y):
        for x in range(W):
            t = (y - Y1) / (FLOOR_Y - Y1)
            cv.put(x, y, WALLW, 7.0 - t * 2.6 if y < Y1 + 4 else 4.2 - t * 0.6)
    cv.hline(0, W - 1, FLOOR_Y - 4, MINT, 4.6)
    cv.hline(0, W - 1, FLOOR_Y - 3, MINT, 4.0)
    cv.hline(0, W - 1, FLOOR_Y - 2, MINT, 3.0)
    cv.hline(0, W - 1, FLOOR_Y - 1, MINT, 1.6)
    return cv.img


@lru_cache(maxsize=None)
def _floor():
    """El terra polit (amb el reflex del que hi ha a sobre i la clapa de sol): no es mou, el reflex és el del fons
    quiet."""
    above = _above().load()
    cv = Canvas(light=LIGHT, img=Image.new('RGBA', (W, H), (0, 0, 0, 0)))
    for y in range(FLOOR_Y, H):
        d = y - FLOOR_Y
        for x in range(W):
            u = (x - 320) / (d + 40) * 2.4
            fr = (u - math.floor(u)) * (d + 40) / 2.4
            lvl = 4.0 - d * 0.0075 + (hr(math.floor(u), 3) - 0.5) * 0.3
            if fr < 1:
                lvl -= 1.2
            elif fr < 2:
                lvl += 0.3
            if d in (12, 40):
                lvl -= 1.0
            elif d in (13, 41):
                lvl += 0.4
            cv.put(x, y, DECK, lvl)
            sy = FLOOR_Y - 1 - int(d * 1.2)
            k = 0.45 * max(0.0, 1 - d / 61) ** 1.3
            if sy > 0 and fr >= 1:
                cv.flat(x, y, mix(cv.get(x, y), above[x, sy], k))
    # la clapa de sol, càlida, que entra per l'esquerra
    for y in range(FLOOR_Y + 1, H):
        d = y - FLOOR_Y
        for x in range(W):
            for xa, xb in ((-27, 187), (213, 427)):
                a, b = xa + d * 1.0, xb + d * 1.3
                if a < x < b:
                    e = min(x - a, b - x)
                    k = 0.42 * max(0.0, 1 - d / 80) * min(1.0, e / 5)
                    if k > B4[y & 3][x & 3] * 0.3:
                        cv.flat(x, y, mix(cv.get(x, y), (255, 228, 170), k))
    return cv.img


@lru_cache(maxsize=None)
def _above():
    """El que es reflecteix al terra: el fons quiet amb les jardineres (t = 0)."""
    cv = Canvas(light=LIGHT, img=_static().copy())
    _planters(cv, 0.0)
    return cv.img


def _planters(cv, T):
    Y1 = WIN[3]
    planter(cv, 8, 187, Y1 - 8, seed=4, tall=40, time=T)
    planter(cv, 453, 635, Y1 - 8, seed=6, tall=45, time=(T * 2) % 1)


def _rays(T):
    """Els raigs de sol a l'aire (respiren a poc a poc, cadascun al seu ritme), com a capa: (alfa, color)."""
    X0, Y0, X1, Y1 = WIN
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    ty = (yy - Y0) / (FLOOR_Y - Y0)
    a = np.zeros((H, W))
    for j, (xa, xb) in enumerate(((0, 187), (213, 427))):
        lo, hi = xa + 13 + ty * 40, xb - 13 + ty * 27
        pulse = 1 + 0.6 * math.sin(2 * math.pi * (j + 1) * T)
        inside = (xx > lo) & (xx < hi) & (yy >= Y0) & (yy < FLOOR_Y)
        a += np.where(inside, 0.06 * (0.3 + ty) * pulse, 0.0)
    return a


def _mix_np(A, col, k):
    """mix() de pix, en bloc: A (h, w, 3) cap a `col` amb k (h, w)."""
    c = np.array(col, float)
    return np.round(A + (c - A) * k[..., None])


def background(cv, t=0.0):
    T = t
    cv.img.paste(_static())
    # jardineres al peu del finestral
    _planters(cv, T)
    # terra polit
    cv.img.alpha_composite(_floor())
    # raigs de sol a l'aire (els dos de 480 s'apliquen un darrere l'altre; aquí d'un cop, amb la suma)
    A = np.array(cv.img).astype(float)
    a = _rays(T)
    A[..., :3] = _mix_np(A[..., :3], (255, 228, 170), np.minimum(1, a))
    cv.img.paste(Image.fromarray(A.astype(np.uint8), 'RGBA'))
    # la directora jove, al fons a la dreta, que s'ho mira (una mica més lluny: més pàl·lida)
    img = _person('DIRECTORA_JOVE', 'L')
    reflect(cv, img, 565, 317, k=0.3)
    shadow(cv, 565, 317, 16, 4, 0.6)
    stamp(cv, img, 565, 317)
    # boirina del desenfocament
    A = np.array(cv.img).astype(float)
    y = np.arange(H, dtype=float)[:, None] * np.ones((1, W))
    k = np.where(y < FLOOR_Y, 0.16, 0.16 * np.maximum(0.0, 1 - (y - FLOOR_Y) / 53))
    A[..., :3] = _mix_np(A[..., :3], HAZE, k)
    cv.img.paste(Image.fromarray(A.astype(np.uint8), 'RGBA'))


# ─── En Cargol, de prop ─────────────────────────────────────────────────────

S = 3.0                                                         # escala respecte del fotograma de joc de 480 (55×63)
RUSTD = Mat(RUSTY.c, 0.7)
BRASSD = Mat(RUST_BRASS.c, 0.7)
RUBBERD = Mat(RUBBER.c, 0.5)
LAMPD = Mat(LAMP_OLD.c, 0.5)
SCREEND = Mat(SCREEN.c, 0.6)
PLATE = M((40, 26, 14), (96, 64, 26), (160, 116, 46), (210, 170, 80), (240, 214, 140), (255, 244, 200), dith=0.5)
ENGRAVE = (44, 26, 16)


def rust_lvl(seed, k=1.0):
    """Clapes de rovell i pols: soroll de dues escales (en coordenades de 480), i un gra fi de píxel real."""
    def fn(x, y):
        n = hr(int(x // 4), int(y // 4), seed) * 0.6 + hr(int(x // 2), int(y // 2), seed + 1) * 0.4
        v = 0.0
        if n > 0.72:
            v -= 1.0 * k
        elif n < 0.18:
            v += 0.5 * k
        g = hr(int(x * K), int(y * K), seed + 2)
        if g > 0.9:
            v -= 0.5 * k                                         # porus del rovell
        elif g < 0.05:
            v += 0.4 * k
        return v
    return fn


@lru_cache(maxsize=None)
def cargol_gran(blink=0):
    """En Cargol vell, de cara, a escala 3 de 480 (4 de 640): el braç dret (a la dreta de la imatge) allargat amb la
    pinça oberta, l'esquerre avall amb la clau anglesa; la placa amb el nom; els ulls somrient."""
    fw, fh = 230, 200
    fg = FigK(fw, fh)
    s = S
    F = fg.F
    P = lambda x, y: (x * s, y * s)  # noqa: E731

    # erugues
    def tracks(x0, x1):
        pts = [(x0 + 2, 50), (x1 - 2, 50), (x1, 53), (x1, 58), (x1 - 2, 60), (x0 + 2, 60), (x0, 58), (x0, 53)]
        fg.poly([P(*p) for p in pts], RUBBERD, 2.4, amp=1.4, normal=lambda x, y: (0, (y / s - 55) / 6, 0.8), cont=(0.3, 0.8),
                lvlfn=lambda x, y: (0.9 if (int(x // 3) % 3 == 0) else 0) if (y < 52 * s or y > 58.4 * s) else 0)
        for wx in (x0 + 2.4, (x0 + x1) / 2, x1 - 2.4):
            fg.ell(wx * s, 55 * s, 1.5 * s, 1.5 * s, RUSTD, 3.0, amp=1.6, lvlfn=rust_lvl(7))
            fg.ell(wx * s, 55 * s, 0.5 * s, 0.5 * s, RUSTD, 4.0, amp=0.6)
        for X in range(round(F(x0 * s)) + 3, round(F(x1 * s)) - 1, 5):                             # tacs
            fg.rshade(X, F(50 * s) + 1, 1.2, RUBBERD); fg.rshade(X + 1, F(50 * s) + 1, 0.6, RUBBERD)
            fg.rshade(X, F(60 * s) - 1, -0.8, RUBBERD); fg.rshade(X + 1, F(60 * s) - 1, -0.8, RUBBERD)
    tracks(9, 21)
    tracks(33, 45)
    # closca (darrere)
    fg.ell(*P(27, 27), 17 * s, 15.5 * s, BRASSD, 2.8, amp=1.6, cont=(0, 0.8),
           lvlfn=lambda x, y: spiral_lvl(27 * s, 27 * s, 5.0 * s)(x, y) + rust_lvl(3, 1.2)(x, y))
    # cos
    def edges(y):
        yy = y / s
        if yy < 22 or yy > 52:
            return None
        if yy <= 50:
            return ((17 - max(0, 25 - yy) * 1.2) * s, (37 + max(0, 25 - yy) * 1.2) * s)
        return (19 * s, 35 * s)
    fg.lathe(22 * s, 52 * s, edges, RUSTD, 3.0, amp=1.8, cont=(0.2, 1.0), lvlfn=rust_lvl(11))
    # pantalla (la cara), amb les línies d'escombrat
    fg.poly([P(19, 27.6), P(35, 27.6), P(35.4, 40.2), P(18.6, 40.2)], SCREEND, 1.4, cont=(1.0, -0.8),
            lvlfn=lambda x, y: (0.8 if (x + y) % 23 < 2 else 0) + (0.6 if y < 28.6 * s else 0)
            + (0.25 if int(y * K) % 3 == 0 else 0))
    # ulls que somriuen: arcs encesos (en píxels reals)
    for ex in (23.2, 30.8):
        cx, cy = F(ex * s), F(33.4 * s)
        hw = 2.3 * s * K
        n = int(hw * 2.4)
        if blink:                                                  # parpelleig: mig tancats o una ratlla
            for i in range(-n, n + 1):
                tt = i / n
                X = cx + tt * hw
                Y = cy + (0.9 if blink == 2 else 0.2) * s * K - (0 if blink == 2 else math.cos(tt * 1.25) * 0.6 * s * K)
                fg.rpx(X, Y, LAMPD, 3.2 - abs(tt) * 0.8)
                fg.rpx(X, Y + 1, LAMPD, 2.8 - abs(tt) * 0.8)
                if blink == 1:
                    fg.rpx(X, Y + 2, LAMPD, 2.4 - abs(tt) * 0.8)
            continue
        for i in range(-n, n + 1):
            tt = i / n
            X = cx + tt * hw
            Y = cy - math.cos(tt * 1.25) * 1.6 * s * K + 0.6 * s * K
            for w in range(4):
                fg.rpx(X, Y + w - 1, LAMPD, 3.6 + (0.9 if w == 0 else 0) - (0.4 if w == 3 else 0) - abs(tt) * 0.8)
    # boca de reixeta, encesa (parla)
    for X in range(round(F(22 * s)), round(F(33 * s)), 4):
        Y = round(F(37.6 * s))
        fg.rpx(X, Y, LAMPD, 2.8)
        fg.rpx(X + 1, Y, LAMPD, 2.6)
        fg.rpx(X + 2, Y, LAMPD, 2.0)
        fg.rpx(X, Y + 1, LAMPD, 2.0)
        fg.rpx(X + 1, Y + 1, LAMPD, 1.6)
    # junta del coll
    for X in range(round(F(17.5 * s)), round(F(37 * s))):
        Y = round(F(44 * s))
        fg.rshade(X, Y, -1.4, RUSTD)
        fg.rshade(X, Y + 1, -0.8, RUSTD)
        fg.rshade(X, Y + 2, 0.8, RUSTD)
        fg.rshade(X, Y + 3, 0.4, RUSTD)
    # reblons
    for (x, y) in ((19, 47.5), (35, 47.5), (19.4, 25), (34.6, 25), (19, 42), (35, 42)):
        fg.ell(x * s, y * s, 1.0, 1.0, RUSTD, 4.4, amp=1.2)
        fg.rpx(F(x * s) - 1, F(y * s) - 1, RUSTD, 5.6)
    # placa al pit: llautó, amb CARGOL gravat a mà
    px0, py0, px1, py1 = 20.4 * s, 45.6 * s, 33.6 * s, 50.4 * s
    fg.poly([(px0, py0), (px1, py0), (px1, py1), (px0, py1)], PLATE, 3.0, amp=1.0, cont=(0.6, 1.4),
            lvlfn=lambda x, y: (1.0 if y < py0 + 1.5 else 0) - (x - px0) / (px1 - px0) * 0.8)
    for (x, y) in ((px0 + 1.4, py0 + 1.6), (px1 - 1.6, py0 + 1.6), (px0 + 1.4, py1 - 1.8), (px1 - 1.6, py1 - 1.8)):
        fg.rpx(F(x), F(y), PLATE, 1.4)                                                         # els claus de la placa
        fg.rpx(F(x) - 1, F(y) - 1, PLATE, 5.0)
    # el braç esquerre, avall, amb la clau anglesa
    fg.limb(P(15.5, 31), P(12.4, 39.5), 2.0 * s, 1.7 * s, RUSTD, 2.6, amp=1.6, cont=(0.2, 0.8), lvlfn=rust_lvl(21))
    fg.ell(*P(12.4, 39.5), 2.1 * s, 2.1 * s, RUSTD, 2.6, amp=1.6)
    fg.limb(P(12.4, 39.5), P(13.2, 46), 1.6 * s, 1.4 * s, RUSTD, 2.4, amp=1.6, cont=(0.2, 0.8))
    fg.limb(P(13.0, 45), P(12.6, 53), 0.9 * s, 0.9 * s, RUSTD, 3.6, amp=1.6)                      # clau anglesa
    fg.ell(*P(12.6, 54.2), 2.0 * s, 1.6 * s, RUSTD, 3.2, amp=1.4)
    for k in range(6):                                                                          # la boca de la clau
        X, Y = round(F(12.6 * s) - 1 + k % 2), round(F(55.4 * s) - k // 2)
        fg.buf[Y][X] = None
    fg.ell(*P(13.2, 46), 1.8 * s, 1.5 * s, RUSTD, 2.8, amp=1.4)                                    # la mà que l'agafa
    # el braç dret, allargat cap a la Vet
    sh, el, wr = P(38.5, 31), P(47, 38.5), P(57.5, 37.5)
    fg.ell(*sh, 2.6 * s, 2.6 * s, RUSTD, 2.8, amp=1.6, cont=(0.2, 0.8))
    fg.limb(sh, el, 1.9 * s, 1.7 * s, RUSTD, 2.8, amp=1.6, cont=(0.2, 0.9), lvlfn=rust_lvl(31))
    fg.ell(*el, 2.1 * s, 2.1 * s, RUSTD, 2.6, amp=1.6, cont=(0.2, 0.8))
    fg.limb(el, wr, 1.6 * s, 1.4 * s, RUSTD, 3.0, amp=1.6, cont=(0.2, 0.9), lvlfn=rust_lvl(41))
    fg.ell(*wr, 1.9 * s, 1.9 * s, RUSTD, 2.8, amp=1.6)
    # pinça: dos dits que agafen la carta per la cantonada
    wx, wy = wr
    fg.limb((wx, wy), (wx + 3.8 * s, wy - 2.2 * s), 0.9 * s, 0.6 * s, RUSTD, 3.6, amp=1.6, cont=(0.2, 0.8))
    fg.limb((wx + 3.8 * s, wy - 2.2 * s), (wx + 6.6 * s, wy - 0.5 * s), 0.6 * s, 0.45 * s, RUSTD, 3.8, amp=1.6, cont=(0.2, 0.8))
    fg.limb((wx, wy), (wx + 3.8 * s, wy + 2.2 * s), 0.9 * s, 0.6 * s, RUSTD, 2.6, amp=1.6, cont=(0.2, 0.8))
    fg.limb((wx + 3.8 * s, wy + 2.2 * s), (wx + 6.6 * s, wy + 0.5 * s), 0.6 * s, 0.45 * s, RUSTD, 2.8, amp=1.6, cont=(0.2, 0.8))
    # antenes: l'esquerra una mica tòrcida (de vell)
    def antenna(bx, by, mx, my, tx, ty):
        fg.limb(P(bx, by), P(mx, my), 0.55 * s, 0.5 * s, RUSTD, 3.0, amp=1.6)
        fg.limb(P(mx, my), P(tx, ty + 2), 0.5 * s, 0.45 * s, RUSTD, 3.2, amp=1.6)
        fg.ell(*P(tx + 0.5, ty), 3.0 * s, 3.0 * s, RUSTD, 2.8, amp=1.6, cont=(0, 0.8), lvlfn=rust_lvl(51))
        fg.ell(*P(tx + 0.5, ty), 2.0 * s, 2.0 * s, LAMPD, 2.8, amp=1.4)
        fg.ell(*P(tx - 0.2, ty - 0.7), 0.6 * s, 0.6 * s, LAMPD, 4.6, amp=0.4)
    antenna(21, 22, 20, 15, 16.5, 9.5)
    antenna(33, 22, 34.4, 15, 35.4, 8.5)
    # abonyegadures, un cargol que hi falta i un pedaç reblat
    for (x, y) in ((24, 47), (25, 48), (31, 46.4), (20, 49), (36, 34), (37, 35)):
        fg.shade(x * s, y * s, -1.4)
        fg.shade(x * s + 1, y * s, -1.2)
        fg.shade(x * s, y * s + 1, -1.0)
    X0, Y0 = round(F(35 * s)), round(F(42 * s))
    for dx in range(3):
        for dy in range(3):
            fg.rpx(X0 + dx, Y0 + dy, INK, 0)                                                     # el cargol que hi falta
    fg.rshade(X0 + 3, Y0 + 3, 1.0, RUSTD)
    img = fg.render()
    # la placa: el nom gravat (ratlla fosca i la vora de llum de sota)
    Pi = img.load()
    pts, wtxt = text5_px('CARGOL', 0, 0)
    ox = int((F(px0) + F(px1)) / 2 - (wtxt + 1) / 2) + 1
    oy = int(F(py0)) + 6
    for x, y, _a in pts:
        Pi[ox + x, oy + y] = ENGRAVE + (255,)
    for x, y, _a in pts:
        if Pi[ox + x + 1, oy + y + 1][:3] != ENGRAVE:
            Pi[ox + x + 1, oy + y + 1] = (240, 214, 140, 255)
    return img


# ─── La carta i la mà de la Vet ─────────────────────────────────────────────

LETTER = ramp((60, 42, 28), (118, 90, 56), (170, 140, 92), (208, 180, 126), (230, 208, 156), (244, 228, 184), (252, 244, 214), n=9)


def letter(cv, x0, y0, w=45, h=32, tilt=-0.12):
    """La carta: plegada mil vegades, groguenca, amb les vores gastades i un plec que la travessa."""
    rnd = random.Random(5)
    folds_x = [w * 0.5, w * 0.25, w * 0.75]
    folds_y = [h * 0.5, h * 0.33]
    for j in range(h):
        for i in range(w):
            x = x0 + i
            y = y0 + j + i * tilt
            edge = i in (0, w - 1) or j in (0, h - 1)
            if edge and hr(i, j, 3) < 0.25:
                continue                                          # vores menjades
            lvl = 5.2 - j * 0.04 + (hr(i // 4, j // 3, 7) - 0.5) * 0.7 - i * 0.015 + (hr(i, j, 8) - 0.5) * 0.25
            for fx in folds_x:
                if abs(i - fx) < 0.6:
                    lvl -= 1.8
                elif 0.6 <= i - fx < 1.6:
                    lvl += 0.8
                elif 1.6 <= i - fx < 2.6:
                    lvl += 0.3
            for fy in folds_y:
                if abs(j - fy) < 0.6:
                    lvl -= 1.6
                elif 0.6 <= j - fy < 1.6:
                    lvl += 0.7
            if edge:
                lvl -= 1.0
            if hr(i // 6, j // 5, 13) > 0.85:
                lvl -= 0.9                                        # taques
            cv.put(x, y, LETTER, lvl)
    # escriptura de l'Iri, que es transparenta (unes ratlles de tinta esvaïda)
    for row in range(5, h - 4, 5):
        x = 4
        while x < w - 5:
            ln = rnd.randint(3, 8)
            for k in range(ln):
                if x + k < w - 4 and rnd.random() > 0.2:
                    cv.put(x0 + x + k, y0 + row + (x + k) * tilt + (1 if rnd.random() > 0.85 else 0),
                           [(150, 120, 104), (176, 146, 120)], 0.6)
            x += ln + rnd.randint(1, 3)
    # la V. del destinatari, ben visible
    for dx, dy in ((0, 0), (0, 1), (1, 2), (1, 3), (2, 4), (3, 3), (3, 2), (4, 1), (4, 0), (7, 4)):
        cv.flat(x0 + w - 14 + dx, round(y0 + 5 + dy + (w - 14 + dx) * tilt), (70, 44, 54))


@lru_cache(maxsize=None)
def vet_hand():
    """Avantbraç i mà de la Vet que entren per baix a la dreta: el palmell obert, cap amunt, per rebre la carta.
    La mà és a (30, 40) del fotograma de 480 (×4/3); el colze queda fora de quadre."""
    fg = FigK(240, 170)
    SK = Mat(SKIN_VET.c, 0.6)
    OR = Mat(ORANGE.c, 0.6)
    # màniga (la granota) i puny arromangat
    fg.limb((300, 230), (118, 104), 22, 17, OR, 2.6, amp=1.8, cont=(0.2, 0.9),
            lvlfn=lambda x, y: (-0.9 if (x * 0.8 + y) % 34 < 3 else 0) + (0.5 if 3 <= (x * 0.8 + y) % 34 < 5 else 0))
    fg.limb((132, 114), (106, 96), 17.4, 16.4, OR, 3.0, amp=1.8, cont=(0.3, 1.0),
            lvlfn=lambda x, y: -0.8 if abs((x - 120) * 0.6 + (y - 106) * 0.8) < 1.2 else 0)
    # avantbraç
    fg.limb((106, 94), (54, 56), 11.0, 8.6, SK, 2.7, amp=1.8, cont=(0.2, 0.8))
    # palmell, cap amunt i una mica de cantell
    fg.ell(40, 50, 14, 8.6, SK, 3.0, amp=1.6, cont=(0.2, 0.8))
    fg.ell(40, 48, 9.5, 4.0, SK, 2.2, amp=0.8)                                             # el clot del palmell
    for k in range(10):                                                                     # una ratlla de la mà
        fg.rshade(fg.F(33 + k * 1.1), fg.F(47.4 + k * 0.25), -0.5, SK)
    # dits, oberts cap a la carta, amb les puntes una mica aixecades
    for k, (y0, ln, lift) in enumerate(((42.5, 17, 2.2), (47, 19, 1.6), (51.5, 18, 1.2), (55.5, 14, 0.8))):
        a = (30, y0)
        m = (30 - ln * 0.6, y0 + 1.2)
        b = (30 - ln, y0 - lift)
        r = 3.0 - k * 0.15
        fg.limb(a, m, r, r - 0.2, SK, 3.0 - k * 0.3, amp=1.6, cont=(0.2, 0.8))
        fg.limb(m, b, r - 0.2, r - 0.6, SK, 3.2 - k * 0.3, amp=1.6, cont=(0.2, 0.8))
        for dx in range(3):                                                                 # ungla, amb llum
            fg.rpx(fg.F(b[0] + 1) + dx, fg.F(b[1] - 1.5), SK, 4.4 - dx * 0.3)
        fg.rpx(fg.F(b[0] + 1), fg.F(b[1] - 1.5) + 1, SK, 3.6)
        fg.rshade(fg.F(m[0]), fg.F(m[1]) - 1, -0.6, SK)                                         # el plec del nus
    # polze, a sobre, cap amunt
    fg.limb((44, 42), (34, 34), 4.0, 3.2, SK, 3.2, amp=1.6, cont=(0.2, 0.8))
    fg.limb((34, 34), (26, 32), 3.2, 2.8, SK, 3.4, amp=1.6, cont=(0.2, 0.8))
    for dx in range(3):
        fg.rpx(fg.F(27) + dx, fg.F(31), SK, 4.4 - dx * 0.4)
    return fg.render()


# ─── La pantalla ────────────────────────────────────────────────────────────

CX, CY = 3, 107                   # on va el fotograma d'en Cargol (2, 80 a 480)


def bg(cv, t=0.0):
    background(cv, t)
    # parpelleja un cop per bucle (fotogrames a t ≈ 0.5–0.62)
    ph = t % 1
    blink = 2 if 0.555 <= ph < 0.6 else (1 if 0.49 <= ph < 0.68 else 0)
    img = cargol_gran(blink)
    Fc = lambda u: f(u)  # noqa: E731     (coordenada de 480 dins el fotograma → píxel real)
    # reflex al terra i ombra
    fy = CY + round(Fc(60 * S))
    fl = ImageOps.flip(img)
    Pf = fl.load()
    for j in range(0, 80):
        y = fy + j
        if y >= H:
            break
        sj = fl.height - (fy - CY) - 1 + j
        for i in range(fl.width):
            c = Pf[i, sj] if 0 <= sj < fl.height else (0, 0, 0, 0)
            x = CX + i
            if c[3] and 0 <= x < W:
                k = 0.3 * max(0.0, 1 - j / 53)
                if k > B4[y & 3][x & 3] * 0.25:
                    cv.flat(x, y, mix(cv.get(x, y), c, k))
    shadow(cv, CX + Fc(27 * S), fy - 1, 80, 7, 0.8)
    cv.img.alpha_composite(img, (CX, CY))
    # la carta a la pinça (la pinça la tapa per la cantonada)
    wx, wy = CX + Fc(57.5 * S), CY + Fc(37.5 * S)
    # la carta tremola una mica a la pinça (tres cops per bucle)
    flutter = 1 if math.sin(2 * math.pi * 3 * t) > 0.8 else 0
    letter(cv, int(wx + 20), int(wy - 15) + flutter, w=45, h=32)
    # redibuixa la punta del dit de sobre de la pinça, per davant de la carta
    Pi = img.load()
    for j in range(int(wy - CY - 3.5 * S * K), int(wy - CY)):
        for i in range(int(wx - CX + 3 * S * K), min(img.width, int(wx - CX + 8 * S * K))):
            c = Pi[i, j]
            if c[3]:
                cv.flat(CX + i, CY + j, c)
    # la llum càlida dels ulls i la de la carta
    cv.glow(CX + Fc(27 * S), CY + Fc(33.4 * S), 35, (255, 210, 120), 0.18)
    cv.glow(wx + 35, wy + 5, 40, (255, 236, 190), 0.25)
    # els llums de les antenes respiren (un cop per bucle)
    breath = math.sin(math.pi * t) ** 2
    if breath > 0.02:
        for ax, ay in ((17.0, 9.5), (35.9, 8.5)):
            cv.glow(CX + Fc(ax * S), CY + Fc(ay * S), 16, (255, 214, 110), 0.45 * breath)
    # la mà de la Vet
    hand = vet_hand()
    hx, hy = int(wx + 85), int(wy - 35)
    cv.img.alpha_composite(hand, (hx, hy))
    # pols que brilla al raig de sol, al voltant de la carta
    rnd = random.Random(17)
    mv = random.Random(18)                                       # (a part, perquè t=0 sigui el fons quiet)
    for _ in range(46):
        x, y = rnd.gauss(wx + 40, 61), rnd.gauss(wy - 13, 45)
        ph1, ph2, m = mv.uniform(0, 6.3), mv.uniform(0, 6.3), mv.choice((1, 2, 3))
        x += 4 * (math.sin(2 * math.pi * t + ph1) - math.sin(ph1))
        y += 7 * (math.cos(2 * math.pi * t + ph2) - math.cos(ph2))
        if 0 <= x < W and 0 <= y < H:
            b = rnd.random()
            tw = 1 - 0.8 * math.sin(math.pi * m * t) ** 2
            cv.flat(x, y, mix(cv.get(x, y), (255, 240, 200), (0.5 + b * 0.5) * tw))
            if b > 0.85:
                cv.glow(x, y, 5, (255, 230, 170), 0.5)
    vinyeta(cv, 0.5)


PROPS = {}


def _ambient_frames(n=16):
    """Fotogrames de l'animació de fons: només els píxels que canvien respecte del fons quiet."""
    base = Canvas(light=LIGHT)
    bg(base)
    B = np.asarray(base.img)
    frames = []
    for i in range(n):
        cv = Canvas(light=LIGHT)
        bg(cv, t=i / n)
        A = np.array(cv.img)
        A[~(A[..., :3] != B[..., :3]).any(axis=2)] = 0
        frames.append(Image.fromarray(A, 'RGBA'))
    return frames


ANIMS = {'ambient': {'frames': _ambient_frames, 'frameDuration': 110}}
