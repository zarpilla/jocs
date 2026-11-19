"""
El campament de les Fades d'Ortiga (Escena 3, diumenge al matí, a les branques altes del roure gros). Art
definitiu, a 1×.

**Molt de prop**: la Vet és gran (≈1,15-1,2, gairebé el doble que a les sales de lluny) i les fades fan ≈30-35 px.
El sol del matí entra de dalt a l'esquerra, daurat, entre les fulles; tot és verd i or, amb raigs i pols a l'aire.
  - a l'esquerra, el **tronc** del roure, amb els **grafits** de suc de móra («FORA NATURAPLUS», «AIRE PUR? AIRE
    TEU!»), i la **branca** grossa que en surt cap a la dreta: és el terra on es camina, i se'n veu la caiguda (el
    bosc, molt avall);
  - l'**escala de corda** per on puja la Vet, penjada de la branca, a l'esquerra (sortida);
  - damunt la branca, el campament fet de coses robades a NaturaPlus: la **tenda** de cinta d'obra «PERILL», la
    **catapulta** d'aglans amb una pinça d'estendre, i penjada de la branca de dalt, la **diana** amb el logotip;
  - a la dreta, la branca s'acaba i en surt la **branca prima** (com un llapis), amb la **flor** de pebre a la punta
    (decorat a part: `flor`, i `flor_buida` quan ja s'ha collit el pol·len); just al costat, el **gronxador** de cinta
    rosa fluor, que penja de la branca de dalt;
  - primer pla: fulles de roure a contrallum a les cantonades (`FRONT`); la tenda i la catapulta també són capes del
    davant, amb la seva línia base: la Vet hi passa per darrere i per davant.
Animacions: la pols i les clapes de sol que bateguen (`llum`) i unes fulles que es mouen a la branca de dalt
(`fulles`).

Tot és pintat en pantalla (és un exterior orgànic); la perspectiva és la de la branca: la cara de dalt (on es camina)
es veu des de dalt, i s'eixampla cap a la càmera.
"""
import functools
import math
import random

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)

from hd.pix import Canvas, Light, W, H, mix
from hd.rooms.comu import text as text_petit
from hd640.rooms.arrel_comu import (BOTTOM, MOSS, LEAF, PLANK, IRONK, CREAM, GREEN, OAK, PLASTIC, NEON, PINKF,
                                    fbm, hr, arrel, fulla_roure, ombra, lletres, hud_negre, sense, _diff)

# ─── Llum ──────────────────────────────────────────────────────────────────
SUN = (70, -30)                                    # el sol, a dalt a l'esquerra (fora del quadre)


def _clapes(x, y):
    """Clapes de sol entre les fulles: la llum tamisada (nivells que se sumen o es resten)."""
    return (fbm(x / 26, y / 14, 77) - 0.5) * 1.6


LIGHT = Light(ambient=0.2, vignette=(30, 1), floor_fade=None)
LIGHT.width = W
LIGHT.point(SUN[0], SUN[1], r=520, k=1.6, squash=0.8, power=1.3)
LIGHT.add(_clapes)

SKYM = [(126, 160, 146), (170, 196, 172), (206, 220, 190), (232, 234, 204), (248, 242, 214), (255, 250, 230),
        (255, 253, 242)]
HAZE = (214, 222, 184)                             # el color de l'aire, al fons (perspectiva atmosfèrica)
GOLD = (255, 222, 140)
HAZEG = [mix(c, HAZE, 0.5) for c in GREEN]
DEEP = [mix(c, (60, 96, 92), 0.55) for c in GREEN]     # el bosc de sota, molt avall: blau verdós
OAKH = [mix(c, HAZE, 0.55) for c in OAK]
FLOR = [(60, 6, 8), (120, 12, 14), (186, 24, 22), (228, 52, 38), (250, 100, 70), (255, 170, 140)]
POLLEN = [(120, 80, 10), (200, 150, 20), (246, 206, 50), (255, 240, 130), (255, 252, 210)]
TAPE_W = [(150, 150, 146), (200, 200, 196), (236, 236, 230), (252, 252, 248)]
TAPE_R = [(90, 10, 10), (150, 20, 18), (206, 36, 30), (236, 70, 52)]

# ─── Geometria del dibuix ───────────────────────────────────────────────────
TRUNK_X = 116                                      # la vora dreta del tronc (a l'alçada de la branca)


def branca(x):
    """La branca grossa a la x de pantalla: (y del centre, radi). Surt del tronc (amb el coll eixamplat) i
    s'aprima cap a la dreta; a partir de x ≈ 460 s'aprima de pressa fins a la branca prima."""
    t = max(0.0, min(1.0, (x - 60) / 420))
    r = 34 - t * 15 + max(0, 130 - x) * 0.35
    if x > 450:
        r = max(3.0, r - (x - 450) * 0.42)
    return 222 - t * 16 + math.sin(x / 70) * 1.5 + max(0, x - 450) * 0.15, r


BR_END = 490                                       # on s'acaba la branca grossa (i en surt la prima)
THIN = ((486, 210), (556, 202), (604, 158))        # la branca prima (bezier)
FLOR_XY = (608, 150)
DALT = ((60, 52), (340, 16), (660, 10))            # la branca de dalt (bezier), d'on pengen la diana i el gronxador
SWING = (520, 552, 154)                            # el gronxador: x de les dues cintes, y del seient
DIANA = (402, 96, 24)                              # la diana: centre i radi
TENDA = (196, 278, 197)                            # la tenda: x0, x1, y de la base
CATA = (318, 196)                                  # la catapulta: x, y de la base
ESCALA = (142, 166)                                # l'escala de corda: x de les dues cordes


def _bez(p, t):
    (x0, y0), (x1, y1), (x2, y2) = p
    a, b, c = (1 - t) ** 2, 2 * (1 - t) * t, t * t
    return a * x0 + b * x1 + c * x2, a * y0 + b * y1 + c * y2


def _dalt_y(x):
    """La y del centre de la branca de dalt a la x."""
    lo, hi = 0.0, 1.0
    for _ in range(30):
        m = (lo + hi) / 2
        if _bez(DALT, m)[0] < x:
            lo = m
        else:
            hi = m
    return _bez(DALT, (lo + hi) / 2)[1]


# ─── El fons ───────────────────────────────────────────────────────────────

def cel(cv):
    """El cel del matí entre les fulles, el fullatge llunyà (boirós, amb forats de cel) i, a sota de la branca, el
    bosc molt avall (a l'ombra, blau verdós)."""
    for y in range(0, BOTTOM + 1):
        for x in range(W):
            d = math.hypot(x - SUN[0], (y - SUN[1]) * 1.3) / 700
            cv.put(x, y, SKYM, 5.4 - d * 3.4 + (fbm(x / 30, y / 20, 5) - 0.5) * 0.6, lit=0)
    # el fullatge llunyà: fulles petites i boiroses, a mates (amb forats per on es veu el cel)
    rnd = random.Random(11)
    for capa, (n, mida, lvl, llindar) in enumerate(((4400, 7, 3.6, 0.5), (2400, 10, 2.4, 0.56))):
        ramp = [mix(c, HAZE, 0.6 - capa * 0.28) for c in GREEN]
        for _ in range(n):
            x, y = rnd.uniform(-10, W + 10), rnd.uniform(-10, 230)
            if fbm(x / 110 + capa * 3, y / 70, 12 + capa) < llindar:
                continue
            d = math.hypot(x - SUN[0], y - SUN[1]) / 700
            fulla_roure(cv, x, y, rnd.uniform(0, 2 * math.pi), mida * rnd.uniform(0.7, 1.3), ramp=ramp,
                        lvl=lvl + rnd.uniform(-0.8, 0.8) - d * 1.2, lit=0.5, seed=rnd.randint(0, 99), vores=False)
    # bokeh: discs de llum desenfocats, als forats del fullatge
    for _ in range(22):
        x, y = rnd.uniform(140, 640), rnd.uniform(0, 170)
        r = rnd.uniform(3, 8)
        k = rnd.uniform(0.12, 0.28)
        cv.tint(x - r, y - r, x + r, y + r, (255, 246, 210),
                lambda xx, yy, x=x, y=y, r=r, k=k: k if (xx - x) ** 2 + (yy - y) ** 2 <= r * r else 0)
    # branques llunyanes, boiroses
    for p0, p1, p2, r0, r1, sd in (((300, -4), (380, 70), (470, 120), 6, 3, 1),
                                   ((640, 40), (560, 70), (500, 140), 7, 3, 2),
                                   ((180, 120), (250, 90), (310, 84), 4, 1.5, 3)):
        arrel(cv, p0, p1, p2, r0, r1, ramp=OAKH, base=3.0, seed=sd, moss=False, lit=0.3)


def avall(cv):
    """A sota de la branca, molt avall: el sotabosc i les copes dels arbres petits, a l'ombra i amb boira."""
    rnd = random.Random(12)
    for y in range(150, BOTTOM + 1):
        for x in range(60, W):
            if y > branca(x)[0]:
                cv.put(x, y, DEEP, 1.6 + (fbm(x / 40, y / 20, 13) - 0.5) * 1.2, lit=0.2)
    for _ in range(2600):
        x, y = rnd.uniform(60, W + 10), rnd.uniform(180, BOTTOM + 8)
        if y < branca(min(W - 1, max(0, x)))[0] - 4:
            continue
        sol = fbm(x / 50, y / 24, 14)
        fulla_roure(cv, x, y, rnd.uniform(0, 2 * math.pi), rnd.uniform(8, 14), ramp=DEEP,
                    lvl=2.4 + (sol - 0.5) * 5.0 + rnd.uniform(-0.8, 0.8), lit=0.2, seed=rnd.randint(0, 99))
    cv.tint(60, 150, W - 1, BOTTOM, HAZE, lambda x, y: 0.18 if y > branca(x)[0] else 0)


def fullatge(cv, zona, n, mida, ramp, lvl, seed, lit=1.0):
    """Un munt de fulles de roure escampades per una el·lipse (cx, cy, rx, ry)."""
    cx, cy, rx, ry = zona
    rnd = random.Random(seed)
    for _ in range(n):
        a, r = rnd.uniform(0, 2 * math.pi), math.sqrt(rnd.random())
        x, y = cx + math.cos(a) * r * rx, cy + math.sin(a) * r * ry
        fulla_roure(cv, x, y, rnd.uniform(0, 2 * math.pi), mida * rnd.uniform(0.75, 1.2), ramp=ramp,
                    lvl=lvl + rnd.uniform(-0.6, 0.6) + (cy - y) / max(ry, 1) * 0.6, lit=lit, seed=rnd.randint(0, 99))


def tronc(cv):
    """El tronc del roure, a l'esquerra: escorça de roure (solcs verticals), il·luminat de cara pel sol del matí."""
    for y in range(0, BOTTOM + 1):
        right = TRUNK_X + 10 + math.sin(y / 40) * 4 - max(0, 140 - y) * 0.12
        if y > 170:
            right += (y - 170) * 0.25                                       # s'eixampla on neix la branca
        for x in range(0, int(right) + 1):
            u = x / right                                                   # 0 = la vora del quadre, 1 = la dreta
            solc = abs(math.sin(x / 6.0 + fbm(x / 20, y / 60, 21) * 5)) ** 0.4
            lvl = 4.9 - u ** 3 * 2.8 + solc * 1.8 - 1.4 + (fbm(x / 3, y / 10, 22) - 0.5) * 1.0
            if solc < 0.35:
                lvl -= 1.0                                                  # el fons del solc
            if fbm(x / 12, y / 18, 23) > 0.66 and u > 0.55:
                cv.put(x, y, MOSS, lvl + 0.6, lit=0.45)
            else:
                cv.put(x, y, OAK, lvl, lit=0.45)


def grafits(cv):
    """Els grafits de suc de móra al tronc, amb el traç gruixut (lletra fosca sobre escorça clara: es llegeix)."""
    for dx, col in ((1, (58, 12, 46)), (0, (112, 30, 88))):                     # (dues passades: el traç gruixut)
        lletres(cv, 'FORA', 18 + dx, 62, col, k=2, wobble=1.0, seed=1, shear=0.03, esp=1)
        lletres(cv, 'NATURAPLUS', 4 + dx, 86, col, k=1, wobble=0.8, seed=2, shear=0.04, esp=1)
        lletres(cv, 'AIRE PUR?', 8 + dx, 112, col, k=1, wobble=0.7, seed=3, shear=-0.02, esp=1)
        lletres(cv, 'AIRE TEU!', 14 + dx, 126, col, k=1, wobble=0.7, seed=4, shear=0.02, esp=1)


def branca_gran(cv):
    """La branca grossa, on es camina: la cara de dalt (vista des de dalt), amb molsa i liquen, i el costat de
    davant, que cau a l'ombra."""
    for x in range(TRUNK_X - 40, BR_END + 1):
        c, r = branca(x)
        tip = 0.0                           # la punta, arrodonida
        for y in range(int(c - r), int(c + r) + 1):
            ny = (y - c) / r
            if tip and ny * ny + tip * tip > 1:
                continue
            if ny < 0.3:                                                    # la cara de dalt, al sol
                lvl = 5.0 - abs(ny + 0.25) * 1.2 - (1.6 if ny < -0.85 else 0)
            else:                                                           # el costat de davant, a l'ombra
                lvl = 3.4 - (ny - 0.3) * 2.6 + (0.9 if ny < 0.36 else 0)
            solc = abs(math.sin(y / 2.6 + fbm(x / 40, y / 8, 30) * 6)) ** 0.6
            lvl += (fbm(x / 34, y / 3, 31) - 0.5) * 1.0 + (fbm(x / 6, y / 2, 32) - 0.5) * 0.6 + (solc - 0.6) * 0.9
            if ny < 0.25 and fbm(x / 14, y / 6, 33) > 0.6:
                cv.put(x, y, MOSS, lvl + 0.8, lit=1.0)
            elif hr(x // 2, y // 2, 34) > 0.994:
                cv.put(x, y, CREAM, lvl, lit=0.8)                                # liquen
            else:
                cv.put(x, y, OAK, lvl, lit=1.0)
    # l'ombra de la branca de dalt, i la línia de la vora (fosca, perquè es llegeixi on s'acaba)
    for x in range(TRUNK_X - 40, BR_END):
        c, r = branca(x)
        cv.put(x, c + r, OAK, 0.6, lit=0)
    # la branca baixa també cap avall, a la dreta (la prima n'és només un brot)
    arrel(cv, (470, 214), (520, 236), (560, 280), 12, 9, ramp=OAK, base=2.6, seed=35, moss=True, lit=0.8)


def branca_dalt(cv):
    arrel(cv, DALT[0], DALT[1], DALT[2], 15, 8, ramp=OAK, base=3.6, seed=41, moss=True, lit=0.9)
    # un brot que surt del tronc, on seu una fada quan vol
    arrel(cv, (100, 128), (130, 122), (168, 118), 6, 3, ramp=OAK, base=3.8, seed=42, moss=True, lit=0.9)


def fullatge_mig(cv):
    """Les fulles del pla mitjà: a la branca de dalt i a la dreta, verdes i daurades al sol."""
    fullatge(cv, (250, 24, 90, 22), 70, 14, GREEN, 5.0, 1)
    fullatge(cv, (470, 18, 120, 22), 90, 15, GREEN, 5.2, 2)
    fullatge(cv, (610, 60, 50, 50), 60, 16, GREEN, 4.6, 3)
    fullatge(cv, (580, 210, 70, 30), 40, 14, GREEN, 3.4, 4)
    fullatge(cv, (170, 108, 18, 10), 8, 11, GREEN, 4.6, 5)
    # unes quantes fulles a la branca prima
    for i, t in enumerate((0.3, 0.55, 0.75)):
        x, y = _bez(THIN, t)
        fulla_roure(cv, x + 2, y - 7, -1.2 + i * 0.5, 14, ramp=GREEN, lvl=5.0, seed=60 + i)


# ─── El campament ─────────────────────────────────────────────────────────

def escala_corda(cv):
    """L'escala de corda: penja de la branca, per davant, fins a baix de tot."""
    xa, xb = ESCALA
    ya = branca(xa)[0] - branca(xa)[1] * 0.4
    for x in (xa, xb):
        for y in range(int(ya), BOTTOM + 1):
            xx = x + math.sin((y - ya) / 22) * 1.2
            cv.put(xx, y, CREAM, 3.6 - (y - ya) * 0.012, lit=0.7)
            cv.put(xx + 1, y, CREAM, 2.4 - (y - ya) * 0.012, lit=0.7)
        cv.disc(x, ya, 3, 2, CREAM, 3.4, lit=0.7)                                   # el nus a la branca
    c, r = branca(xa)
    for y in range(int(c + r * 0.4), BOTTOM + 1, 13):
        cv.rect(xa - 2, y, xb + 3, y + 2, PLANK, lambda X, Y, y=y: 4.4 - (Y - y) * 1.2, lit=0.8)


def tenda(cv):
    """La tenda de les fades: cinta d'obra (blanca i vermella) estesa sobre un pal entre dues forquilles."""
    x0, x1, yb = TENDA
    xm, top = (x0 + x1) / 2, yb - 52
    # les forquilles i el pal de dalt
    for x in (x0 + 10, x1 - 10):
        cv.line(x, yb, x + (2 if x < xm else -2), top - 2, PLANK, 3.2, lit=0.8)
    cv.line(x0 + 6, top, x1 - 6, top, PLANK, 4.0, lit=0.8)
    # les cintes: de dalt a baix, a banda i banda, en franges
    for k in range(9):
        t = k / 8
        xt = x0 + 14 + (x1 - x0 - 28) * t
        for side in (-1, 1):
            xbase = xt + side * 30
            for i in range(60):
                s = i / 59
                x = xt + (xbase - xt) * s
                y = top + (yb - top) * s
                stripe = int((i + k * 3) / 6) % 2
                ramp = TAPE_R if stripe else TAPE_W
                lv = 2.4 + (0.6 if side < 0 else -0.4)
                for w in range(4):
                    cv.put(x + w * 0.8 * side, y, ramp, lv - w * 0.15, lit=0.8)
    # l'entrada: un triangle fosc al davant
    for y in range(int(top + 14), yb):
        hw = (y - top - 14) * 0.42
        for x in range(int(xm - hw), int(xm + hw) + 1):
            cv.put(x, y, OAK, 0.8, lit=0)
    # una cinta travessera amb el rètol «PERILL» (lletra negra sobre blanc)
    yy = yb - 16
    cv.rect(x0 + 4, yy, x1 - 4, yy + 7, TAPE_W, 3.2, lit=0.6)
    for x in range(x0 + 4, x1 - 3, 12):
        cv.rect(x, yy, x + 3, yy + 7, TAPE_R, 2.6, lit=0.6)
    tw = 4 * 6 - 1
    cv.rect(xm - tw / 2 - 2, yy, xm + tw / 2 + 2, yy + 7, TAPE_W, 3.4, lit=0.4)
    text_petit(cv, 'PERILL', round(xm - tw / 2), yy + 1, IRONK, 0, lit=0, flat=(20, 18, 18))
    ombra(cv, xm + 6, yb + 2, 46, 4, k=0.7)


def catapulta(cv):
    """La catapulta d'aglans: una forquilla, un braç amb una cúpula d'aglà, i una pinça d'estendre de gallet."""
    x, yb = CATA
    ombra(cv, x + 10, yb + 2, 30, 4, k=0.6)
    for d in (0, 1, 2):                                                               # la forquilla, gruixuda
        cv.line(x - 4 + d, yb, x - 2 + d, yb - 22, PLANK, 3.8 - d * 0.8, lit=0.6)
        cv.line(x - 2 + d, yb - 22, x - 9 + d, yb - 32, PLANK, 4.0 - d * 0.8, lit=0.6)
        cv.line(x - 2 + d, yb - 22, x + 5 + d, yb - 33, PLANK, 3.4 - d * 0.8, lit=0.6)
    for i in range(36):                                                               # el braç, carregat
        t = i / 35
        xx, yy = x + 24 - t * 40, yb - 4 - t * 24
        cv.put(xx, yy, PLANK, 4.4, lit=0.9)
        cv.put(xx, yy + 1, PLANK, 3.0, lit=0.9)
    cv.disc(x - 17, yb - 29, 5, 3, PLANK, lambda nx, ny: 2.4 - ny * 1.6, lit=0.9)   # la cúpula, amb un aglà
    cv.disc(x - 17, yb - 33, 3.4, 4, LEAF, lambda nx, ny: 4.2 - nx * 0.8 - ny * 0.8, lit=0.9)
    # la pinça d'estendre (de fusta clara, amb la molla), que aguanta el braç
    cv.rect(x + 18, yb - 8, x + 36, yb - 5, PLANK, lambda X, Y: 6.4 - (Y - yb + 8) * 0.6, lit=0.8)
    cv.rect(x + 18, yb - 4, x + 36, yb - 1, PLANK, lambda X, Y: 5.6 - (Y - yb + 4) * 0.6, lit=0.8)
    cv.disc(x + 27, yb - 4, 2.2, 2.6, IRONK, 4.0, lit=0.4)
    # els aglans de munició
    for ax, ay in ((x + 44, yb - 2), (x + 51, yb - 1), (x + 47, yb - 7)):
        cv.disc(ax, ay - 2, 3.0, 3.6, LEAF, lambda nx, ny: 4.0 - nx * 0.8 - ny * 0.8, lit=0.9)
        cv.disc(ax, ay - 5, 3.4, 1.8, PLANK, 2.6, lit=0.9)


def diana(cv):
    """La diana: una placa rodona de NaturaPlus (plàstic blanc, el logotip de la fulla verda fluor), penjada d'un
    fil, amb dos aglans clavats."""
    cx, cy, r = DIANA
    top = _dalt_y(cx) + 6
    cv.line(cx, top, cx, cy - r, CREAM, 3.0, lit=0.4)
    ombra(cv, cx + 8, cy + 6, r, r, k=0.4)
    cv.disc(cx, cy, r + 2, r + 2, PLASTIC, 1.2, lit=0)
    for k, rr in enumerate((r, r * 0.74, r * 0.48)):
        cv.disc(cx, cy, rr, rr, PLASTIC if k % 2 == 0 else NEON, lambda nx, ny, k=k: (5.4 if k % 2 == 0 else 2.6)
                - ny * 0.6 - nx * 0.3, lit=0.3)
    # el logotip: una fulla verda fluor amb una «+»
    for yy in range(int(cy - 9), int(cy + 9)):
        for xx in range(int(cx - 9), int(cx + 9)):
            u, v = (xx - cx) / 9, (yy - cy) / 9
            if abs(u + v) < 1.0 and abs(u - v) * (1.6 - abs(u + v) * 0.6) < 0.9:
                cv.put(xx, yy, NEON, 3.6 - v * 0.6, lit=0)
    cv.rect(cx - 1, cy - 4, cx + 1, cy + 4, PLASTIC, 6.0, lit=0)
    cv.rect(cx - 4, cy - 1, cx + 4, cy + 1, PLASTIC, 6.0, lit=0)
    text_petit(cv, 'NATURAPLUS', cx - 19, cy + r - 9, IRONK, 0, lit=0, flat=(40, 120, 40))
    for ax, ay in ((cx - 12, cy - 8), (cx + 14, cy + 3)):                             # aglans clavats
        cv.disc(ax, ay, 2.6, 3, LEAF, lambda nx, ny: 3.8 - ny, lit=0.6)
        cv.disc(ax, ay - 2.4, 3, 1.6, PLANK, 2.6, lit=0.6)


def gronxador(cv):
    """El gronxador: dues cintes rosa fluor que pengen de la branca de dalt, i un seient de tap d'ampolla."""
    xa, xb, ys = SWING
    for x in (xa, xb):
        top = _dalt_y(x) + 4
        for y in range(int(top), ys):
            xx = x + (y - top) / (ys - top) * (3 if x == xa else -3)
            cv.put(xx, y, PINKF, 4.0, lit=0.3)
            cv.put(xx + 1, y, PINKF, 2.8, lit=0.3)
        cv.disc(x, top, 2.4, 2.4, PINKF, 3.6, lit=0.3)                                 # el nus
    # el seient: el tap blanc d'una ampolla d'«Aire Pur», de cantó
    cv.disc((xa + xb) / 2, ys + 2, (xb - xa) / 2 + 4, 4, PLASTIC, lambda nx, ny: 4.6 - ny * 1.8, lit=0.5)
    cv.disc((xa + xb) / 2, ys + 1, (xb - xa) / 2 + 2, 2.4, PLASTIC, 5.6, lit=0.5)
    cv.rect(xa + 2, ys + 4, xb - 2, ys + 5, NEON, 3.6, lit=0)


def branca_prima(cv):
    """La branca prima, com un llapis, que surt cap a la dreta i puja una mica; a la punta, el peu de la flor."""
    for i in range(140):
        t = i / 139
        x, y = _bez(THIN, t)
        r = 2.6 - t * 1.2
        for dy in range(-int(r) - 1, int(r) + 2):
            ny = dy / max(r, 0.8)
            if abs(ny) <= 1:
                cv.put(x, y + dy, OAK, 4.2 - ny * 1.6, lit=0.9)
    fx, fy = FLOR_XY
    for i in range(8):                                                               # la tija i el calze
        cv.put(fx - 4 + i * 0.5, fy + 8 - i, MOSS, 4.0, lit=0.6)
    cv.disc(fx, fy + 1, 3.2, 2.2, MOSS, 4.6, lit=0.6)


def _flor(cv, buida):
    """La flor de pebre: cinc pètals vermells i, al mig, el pol·len (si encara n'hi ha)."""
    fx, fy = FLOR_XY
    for k in range(5):
        a = -math.pi / 2 + k * 2 * math.pi / 5 + 0.2
        px, py = fx + math.cos(a) * 6, fy - 3 + math.sin(a) * 5
        cv.disc(px, py, 5 if not buida else 4, 4 if not buida else 3, FLOR,
                (lambda nx, ny: 4.4 - ny * 1.2 - nx * 0.4) if not buida else (lambda nx, ny: 2.6 - ny * 0.8), lit=0.6)
    if buida:
        cv.disc(fx, fy - 3, 2.6, 2.2, MOSS, 3.0, lit=0.6)
        for x, y in ((fx - 7, fy + 4), (fx + 6, fy + 5)):                           # pètals que pengen
            cv.put(x, y, FLOR, 2.4, lit=0.5)
            cv.put(x, y + 1, FLOR, 2.0, lit=0.5)
    else:
        cv.disc(fx, fy - 3, 3.4, 3.0, POLLEN, lambda nx, ny: 3.6 - ny, lit=0)
        for dx, dy in ((-2, -4), (1, -5), (3, -2), (-1, -1), (0, -3)):
            cv.flat(fx + dx, fy - 3 + dy, POLLEN[4])
        rnd = random.Random(8)
        for _ in range(10):                                                          # el pol·len que s'escapa
            cv.flat(fx + rnd.uniform(-10, 12), fy - 6 + rnd.uniform(-10, 6), POLLEN[3])
        cv.glow(fx, fy - 3, 16, (255, 220, 120), 0.35)


# ─── Raigs i primer pla ────────────────────────────────────────────────────

def raigs(cv):
    """Els raigs del sol del matí, en diagonal de dalt a l'esquerra, amb llum daurada."""
    def k(x, y):
        u = (x - SUN[0]) * 0.8 - (y - SUN[1]) * 0.6
        s = 0.5 + 0.5 * math.sin(u / 22 + fbm(u / 60, 0.3, 80) * 4)
        d = math.hypot(x - SUN[0], y - SUN[1])
        return max(0.0, s - 0.5) * 0.6 * max(0.0, 1 - d / 680)
    cv.tint(0, 0, W - 1, BOTTOM, GOLD, k)
    # i l'escalfor del sol, a dalt a l'esquerra
    cv.tint(0, 0, W - 1, BOTTOM, (255, 200, 110),
            lambda x, y: 0.14 * max(0.0, 1 - math.hypot(x - SUN[0], y - SUN[1]) / 520))


def primer_pla(cv):
    """Fulles de roure a contrallum a les cantonades (fosques, amb la vora daurada)."""
    def fosc(nx, ny):
        return -0.6 - ny * 0.4
    rnd = random.Random(90)
    for cx, cy, rx, ry, n in ((640, 0, 70, 50, 26), (650, 250, 70, 40, 22), (0, 262, 50, 30, 12),
                              (330, 266, 40, 14, 8)):
        for _ in range(n):
            a, r = rnd.uniform(0, 2 * math.pi), math.sqrt(rnd.random())
            fulla_roure(cv, cx + math.cos(a) * r * rx, cy + math.sin(a) * r * ry, rnd.uniform(0, 2 * math.pi),
                        rnd.uniform(26, 40), ramp=GREEN, lvl=1.6, lit=0, seed=rnd.randint(0, 99), llum=fosc)
    # una branqueta que entra per dalt a la dreta
    arrel(cv, (660, -10), (610, 18), (566, 14), 5, 2, ramp=OAK, base=1.4, seed=91, moss=False, lit=0)


@functools.lru_cache(maxsize=None)
def _davant():
    cv = Canvas(light=LIGHT, transparent=True)
    primer_pla(cv)
    img = cv.img
    a = img.load()
    for y in range(BOTTOM + 1, H):
        for x in range(W):
            a[x, y] = (0, 0, 0, 0)
    return img


# ─── Composició ────────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _render(estat=frozenset()):
    """Tota la sala amb un estat: 'flor' (la flor amb pol·len), 'buida' (la flor sense pol·len); 'sense_tenda' i
    'sense_catapulta' (per a les màscares de les capes del davant)."""
    cv = Canvas(light=LIGHT)
    cel(cv)
    avall(cv)
    branca_dalt(cv)
    fullatge_mig(cv)
    tronc(cv)
    grafits(cv)
    branca_gran(cv)
    branca_prima(cv)
    if 'flor' in estat:
        _flor(cv, False)
    if 'buida' in estat:
        _flor(cv, True)
    if 'sense_tenda' not in estat:
        tenda(cv)
    if 'sense_catapulta' not in estat:
        catapulta(cv)
    diana(cv)
    gronxador(cv)
    escala_corda(cv)
    raigs(cv)
    cv.img.alpha_composite(_davant())
    cv.P = cv.img.load()
    hud_negre(cv)
    return cv.img


def _base():
    return _render(frozenset())


def bg(cv):
    cv.img.paste(_base())
    cv.P = cv.img.load()


def _decorat(*estat):
    def draw(cv):
        img = _render(frozenset(estat))
        cv.img.alpha_composite(sense(_diff(img, _base()), _davant()))
        cv.P = cv.img.load()
    return draw


PROPS = {'flor': _decorat('flor'), 'flor_buida': _decorat('buida')}


# ─── Animacions ─────────────────────────────────────────────────────────────

def _frames_llum():
    """Pols daurada que sura als raigs, i els discs de llum del fons que bateguen (el bucle no salta)."""
    img = _base()
    davant = _davant().load()
    motes = [(hr(k, 1) * 600 + 20, hr(k, 2) * 200 + 20, 4 + hr(k, 3) * 10, 3 + hr(k, 4) * 8, hr(k, 5),
              1 + int(hr(k, 6) * 2)) for k in range(60)]
    n = 48
    frames = []
    for i in range(n):
        cv = Canvas(light=LIGHT, img=img.copy())
        t = i / n
        for (x0, y0, ax, ay, ph, fx) in motes:
            a = 2 * math.pi * (t + ph)
            x = round(x0 + ax * math.sin(fx * a))
            y = round(y0 + ay * math.sin(a + ph * 3))
            u = (x - SUN[0]) * 0.8 - (y - SUN[1]) * 0.6
            ray = 0.5 + 0.5 * math.sin(u / 22 + fbm(u / 60, 0.3, 80) * 4)
            tw = 0.5 + 0.5 * math.sin(a * 2 + ph * 7)
            alpha = max(0.0, ray - 0.45) * 1.6 * (0.4 + 0.6 * tw)
            if alpha > 0.1 and 0 <= x < W and 0 <= y < BOTTOM and not davant[x, y][3]:
                cv.flat(x, y, mix(cv.get(x, y), (255, 240, 190), min(0.9, alpha)))
        frames.append(_diff(cv.img, img))
    return frames


FULLES = [(222, 40, -0.6), (300, 36, 2.2), (452, 30, 1.0), (500, 34, -1.9)]


def _frames_fulles():
    """Unes fulles de la branca de dalt que es mouen amb l'aire del matí."""
    img = _base()
    n = 24
    frames = []
    for i in range(n):
        cv = Canvas(light=LIGHT, img=img.copy())
        t = i / n
        for k, (x, y, a) in enumerate(FULLES):
            da = math.sin(2 * math.pi * (t + k * 0.27)) * 0.35
            fulla_roure(cv, x, y + 6, a + da, 15, ramp=GREEN, lvl=5.0, seed=70 + k)
        frames.append(_diff(cv.img, img))
    return frames


ANIMS = {'llum': {'frames': _frames_llum, 'frameDuration': 120},
         'fulles': {'frames': _frames_fulles, 'frameDuration': 110}}


# ─── Capes del davant ─────────────────────────────────────────────────────

def _mask_davant(x, y):
    return _davant().getpixel((x, y))[3] > 0


@functools.lru_cache(maxsize=None)
def _mask_sense(que):
    """La màscara del que canvia en no pintar `que` ('tenda' o 'catapulta'): el moble, amb la seva ombra."""
    import numpy as np
    a = np.asarray(_base().convert('RGB'))
    b = np.asarray(_render(frozenset({f'sense_{que}'})).convert('RGB'))
    m = (a != b).any(axis=2)
    return lambda x, y: bool(m[y, x])


# La tenda i la catapulta, damunt la branca, amb la seva línia base: la Vet hi passa per darrere (si va per la vora
# de dalt de la branca) i per davant. I el primer pla, que tapa sempre.
FRONT = [{'id': 'davant_tenda', 'mask': lambda x, y: _mask_sense('tenda')(x, y), 'baseline': TENDA[2], 'zIndex': 20},
         {'id': 'davant_catapulta', 'mask': lambda x, y: _mask_sense('catapulta')(x, y), 'baseline': CATA[1],
          'zIndex': 20},
         {'id': 'davant', 'mask': _mask_davant, 'baseline': 999, 'zIndex': 20}]


# ─── Geometria (coordenades de sala) ─────────────────────────────────────────
# La Vet hi és gran: a la cara de dalt de la branca, de ≈1,1 (al fons) a 1,2 (a la vora de davant); a les sales de
# lluny va a ≈0,65-0,7. Per damunt de la branca (les fades a la tenda, a la diana o al brot del tronc), 1,1 fix.

def _el(cx, cy, rx, ry, n=10):
    return [(round(cx + rx * math.cos(2 * math.pi * i / n)), round(cy + ry * math.sin(2 * math.pi * i / n)))
            for i in range(n)]


def _walk():
    # (fins a prop de la vora de dalt de la branca: s'hi pot passar per darrere de la tenda i de la catapulta)
    top = [(x, round(branca(x)[0] - branca(x)[1] * 0.88)) for x in range(120, 441, 40)]
    bot = [(x, round(branca(x)[0] + branca(x)[1] * 0.3)) for x in range(440, 119, -40)]
    return top + [(452, round(branca(452)[0] - 2))] + bot


def _geometria():
    walk = _walk()
    v_top, v_bot = min(p[1] for p in walk), max(p[1] for p in walk)
    x0, x1, yb = TENDA
    cx, cy, r = DIANA
    xa, xb, ys = SWING
    fx, fy = FLOR_XY
    ea, eb = ESCALA
    c_e, r_e = branca(ea)
    cat_x, cat_y = CATA
    things = {
        'escala_corda': {'rect': (ea - 8, round(c_e - r_e * 0.5), eb + 8, BOTTOM), 'walk': (eb + 14, round(c_e - 4))},
        'tenda': {'rect': (x0, yb - 56, x1, yb + 2), 'walk': ((x0 + x1) // 2, yb + 10)},
        'catapulta': {'rect': (cat_x - 24, cat_y - 40, cat_x + 56, cat_y + 2), 'walk': (cat_x + 10, cat_y + 12)},
        'diana': {'rect': (cx - r - 3, cy - r - 3, cx + r + 3, cy + r + 3), 'walk': (cx, round(branca(cx)[0]))},
        'grafits': {'rect': (4, 58, 112, 140), 'walk': (150, round(branca(150)[0] - 8))},
        'gronxador': {'rect': (xa - 6, ys - 70, xb + 8, ys + 8), 'walk': (436, round(branca(436)[0] - 4))},
        'branca': {'rect': (BR_END - 30, 160, fx - 12, 220), 'walk': (440, round(branca(440)[0] - 2))},
        'flor': {'rect': (fx - 12, fy - 14, fx + 12, fy + 10), 'walk': (444, round(branca(444)[0] - 2))},
    }
    return {
        'things': things,
        'spawns': {'vet': (eb + 14, round(c_e - 4)), 'urtica': (cat_x + 38, min(cat_y - 1, v_top - 6)),  # vola damunt la catapulta: a l'escala de les fades
                   'pica': ((x0 + x1) // 2 + 2, yb - 53), 'card': (cx + 2, cy - r - 1)},
        'walkable': walk,
        # la tenda i la catapulta no es trepitgen: s'hi fa la volta (per davant o per la vora de dalt de la branca)
        'forats': [_el((x0 + x1) / 2, yb, (x1 - x0) / 2 - 4, 3), _el(cat_x + 6, cat_y, 18, 3)],
        'floorSquash': 0.45,
        'regions': [
            {'id': 'branques', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': False,
             'scaleTop': 0.87, 'scaleBottom': 0.87, 'points': [(0, 0), (W - 1, 0), (W - 1, v_top - 3), (0, v_top - 3)]},
            # A 1,65–1,8 (la sala es va pintar per a personatges de 97 px; els fulls en fan 68), cada píxel del
            # personatge era el doble que els del decorat. Mentre no hi ha una mida gran dels fulls, a ≈1,2 com màxim.
            {'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
             'scaleTop': 1.1, 'scaleBottom': 1.2,
             'points': [(0, v_top - 2), (W - 1, v_top - 2), (W - 1, v_bot + 2), (0, v_bot + 2)]},
        ],
        # L'ombra de contacte: el sol del matí, de dalt a l'esquerra (l'ombra cau cap a la dreta i endavant).
        'characterShadow': {'enabled': True, 'color': '#1a1408', 'alpha': 0.4, 'squash': 0.35, 'core': 0.6,
                            'light': {'x': 0.8, 'y': 0.3, 'direction': True}},
        'characterOutline': {'color': '#ffe3a0', 'alpha': 0.3},
        'characterLights': {
            'ambient': '#d8dcb4',
            'lights': [{'x': 60, 'y': 0, 'radius': 520, 'color': '#ffe2a0', 'intensity': 0.9}],
        },
    }


GEOMETRIA = _geometria()
