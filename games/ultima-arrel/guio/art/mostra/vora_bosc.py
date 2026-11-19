#!/usr/bin/env python3
"""
L'Última Arrel — mostra d'art de la sala 1, `vora_bosc` (Escena 1), al capvespre. Ve de la referència 1.

La càmera és baixa, arran de terra (una mica contrapicada): el roure és enorme i les falgueres del primer pla són
més altes que la Iri. A l'esquerra, el bosc viu i càlid, amb el sol que es pon entre els troncs. A la dreta, la tanca
de NaturaPlus, amb el que hi ha a darrere (la caseta d'obra, la gespa artificial, l'excavadora), en colors freds.

Al roure: la porta d'un metre, la campaneta, el fanalet vermell, la bústia i l'estaca de topògraf clavada davant
la porta. Al peu de la tanca, el cargol galvanitzat que brilla. Hi ha dues versions: amb la xarxa caiguda (Escena 1:
els bolets i els filaments, gairebé apagats) i amb la xarxa encesa (com seria l'epíleg, `bosc_obert`).

Ús: python3 vora_bosc.py  →  vora-bosc.png, vora-bosc-encesa.png (×2, amb la Iri), vora-bosc-sala.png (1×, sense)
"""
import math

from PIL import Image

from bosc import (W, H, Canvas, Light, nearest, fbm, hr, text, text_width, arrel, bolet, filament, falguera, ombra,
                  DUSK, HAZE, LEAVES, BARK, MOSS, EARTH, LEAF, PLANK, IRONK, STONE, FERN, TURQ, GLOW_T, PLASTIC,
                  STEEL, NEON, SIGNK, CONE, YELLOWM, REDL, HERE)
import nenes

HOR = 168                      # l'horitzó (la càmera és baixa)
SUN = (96, 150)                # on es pon el sol, entre els troncs

LIGHT = Light(ambient=-0.2, vignette=(70, 30), floor_fade=None)
LIGHT.width = W                # (la vinyeta, a 640 i no als 480 per defecte de la llibreria)
LIGHT.point(SUN[0], SUN[1], r=520, k=1.7, squash=0.8, power=1.3)
LIGHT.point(254, 198, r=40, k=0.7, power=1.6)                      # el fanalet vermell (una mica)

# ─── El roure ──────────────────────────────────────────────────────────────
TC, TBASE = 214, 246


def tronc_c(y):
    return TC + 6 * math.sin(y / 46) - 4


def tronc_w(y):
    return 44 + 60 * max(0.0, (y - 170) / 76) ** 2.2 - 4 * max(0.0, (120 - y) / 120)


DOOR = (222, 186, 238, 17)     # centre x, dalt, baix, mig ample


# ─── Cel, bosc del fons ────────────────────────────────────────────────────

def cel(cv):
    for y in range(0, HOR + 2):
        for x in range(W):
            d = math.hypot(x - SUN[0], (y - SUN[1]) * 1.6)
            lvl = 1.0 + 4.2 * (y / HOR) ** 1.4 + 3.6 * max(0.0, 1 - d / 330) ** 1.6
            lvl -= max(0.0, (x - 380) / 260) * 1.6                                  # a l'est, ja és de nit
            lvl += (fbm(x / 70, y / 14, 3) - 0.5) * 0.8
            cv.put(x, y, DUSK, lvl, lit=0)
    for (x, y) in ((560, 22), (604, 46), (512, 38), (628, 14), (470, 18)):          # els primers estels
        cv.flat(x, y, (230, 226, 250))
    cv.glow(SUN[0], SUN[1], 90, (255, 214, 150), 0.7)


def bosc_fons(cv):
    """Troncs llunyans contra la boira daurada (com més lluny, més color d'aire), i el sotabosc."""
    for k, (x, w, lvl) in enumerate(((8, 7, 4.4), (46, 5, 5.4), (70, 9, 3.8), (132, 6, 5.0), (150, 11, 3.4),
                                     (300, 8, 4.0), (340, 12, 3.2), (372, 6, 4.6), (396, 9, 3.6), (28, 14, 2.6),
                                     (112, 4, 6.0), (270, 5, 5.2))):
        base = HOR + 14 - lvl * 2
        for y in range(0, int(base)):
            ww = w * (0.8 + 0.2 * y / base)
            for xx in range(int(x - ww), int(x + ww) + 1):
                u = (xx - x) / ww
                cv.put(xx, y, HAZE, lvl - 2.0 + u * 0.8 + (fbm(xx / 2, y / 20, k) - 0.5) * 0.8, lit=0.25)
    # el sotabosc, una franja de mates a contrallum
    for x in range(0, 420):
        top = HOR - 8 - 18 * fbm(x / 26, 0.5, 9) - 10 * fbm(x / 7, 1.5, 4)
        for y in range(int(top), HOR + 18):
            cv.put(x, y, HAZE, 2.4 + (y - top) * -0.02 + (fbm(x / 4, y / 4, 6) - 0.5) * 1.2, lit=0.6)
    # la capçada: fulles de tardor, amb forats per on passa la llum
    for y in range(0, 110):
        for x in range(0, 470):
            f = fbm(x / 34, y / 22, 21, 4)
            edge = 0.40 + y / 110 * 0.22 + max(0, x - 330) / 140 * 0.3
            if f > edge:
                lvl = 2.0 + (f - edge) * 9 + (fbm(x / 3, y / 3, 8) - 0.5) * 1.6
                cv.put(x, y, LEAVES, lvl, lit=0.8)


# ─── Darrere la tanca: l'obra ──────────────────────────────────────────────

def obra(cv):
    # el terra remogut, fred
    for x in range(372, W):
        for y in range(HOR - 2, int(_fence_base(max(x, 392))) + 1):
            lvl = 2.2 + (y - HOR) * 0.012 + (fbm(x / 20, y / 5, 31) - 0.5) * 1.2
            if (x * 3 + y * 7) % 23 == 0:                                           # rodades de l'excavadora
                lvl -= 0.6
            cv.put(x, y, STONE, lvl, lit=0)
    # arbres tallats: soques
    for x, y, r in ((404, 178, 7), (448, 184, 5), (582, 182, 6)):
        cv.disc(x, y, r, r * 0.35, PLANK, lambda nx, ny: 4.6 - (1.4 if abs(math.hypot(nx, ny) - 0.5) < 0.12 else 0), lit=0)
        cv.rect(x - r, y, x + r, y + 5, BARK, lambda xx, yy: 2.0 - abs(xx - x) / r, lit=0)
    # la caseta d'obra: un contenidor blanc, finestres de fluorescent
    x0, x1, y0, y1 = 458, 552, 134, 184
    cv.rect(x0, y0, x1, y1, PLASTIC, lambda x, y: 3.0 - (0.9 if (x - x0) % 8 == 0 else 0) - (y - y0) * 0.012, lit=0)
    cv.rect(x0 - 2, y0 - 3, x1 + 2, y0, PLASTIC, 4.2, lit=0)
    cv.rect(x0, y1 - 2, x1, y1, STEEL, 2.0, lit=0)
    for wx in (468, 502):
        cv.rect(wx, 146, wx + 20, 160, [(150, 200, 196), (210, 244, 236), (240, 255, 250)], 1.2, lit=0)
        cv.rect(wx + 10, 146, wx + 10, 160, PLASTIC, 1.0, lit=0)
        cv.glow(wx + 10, 153, 22, (200, 250, 240), 0.35)
    cv.rect(532, 146, 546, 184, STEEL, 2.6, lit=0)                                 # la porta
    cv.disc(486, 140, 3, 3, NEON, 3.0, lit=0)                                       # el logotip (una fulla)
    for x in range(474, 478):
        cv.flat(x, 186, (60, 64, 72))
    # l'escaleta
    cv.rect(530, 184, 548, 186, STEEL, 2.4, lit=0)
    cv.rect(532, 187, 546, 189, STEEL, 2.0, lit=0)
    # l'excavadora: groc, a contrallum del cel violeta
    cv.poly([(574, 186), (574, 160), (600, 154), (626, 156), (630, 186)], YELLOWM, lambda x, y: 2.6 - (y - 154) * 0.02, lit=0)
    cv.rect(584, 160, 598, 172, [(40, 50, 60), (70, 90, 100), (110, 140, 150)], 1.0, lit=0)
    cv.rect(570, 184, 636, 194, IRONK, lambda x, y: 1.6 + (0.8 if (x // 4) % 2 else 0), lit=0)
    for i in range(48):                                                             # el braç
        t = i / 47
        x, y = 600 - t * 40, 156 - math.sin(t * 2.6) * 52
        for k in range(-2, 3):
            cv.put(x + k * 0.3, y + k, YELLOWM, 2.8 - abs(k) * 0.4, lit=0)
    cv.poly([(556, 150), (566, 146), (568, 162), (554, 160)], IRONK, 2.0, lit=0)   # la pala
    # la gespa artificial, en rotllos: verd fluor
    for x, y in ((392, 196), (418, 200), (444, 196)):
        cv.disc(x, y, 12, 7, NEON, lambda nx, ny: 2.2 - ny * 0.8 + (0.6 if int((nx + 1) * 6) % 2 else 0), lit=0)
        cv.disc(x + 12, y, 3, 7, NEON, lambda nx, ny: 1.4 + (0.8 if math.hypot(nx, ny) % 0.5 < 0.2 else 0), lit=0)
    # cons
    for x, y in ((488, 204), (520, 198)):
        cv.poly([(x - 5, y), (x, y - 13), (x + 5, y)], CONE, lambda xx, yy: 3.0 - (xx - x) * 0.2 +
                (1.6 if (y - yy) in (5, 6) else 0), lit=0)
        cv.rect(x - 6, y, x + 6, y + 1, CONE, 1.4, lit=0)


# ─── El terra ──────────────────────────────────────────────────────────────

def terra(cv):
    for y in range(HOR + 6, H):
        t = (y - HOR) / (H - HOR)
        for x in range(0, W):
            if x >= 392 and y < _fence_base(x):
                continue                                                            # darrere la tanca: l'obra
            lvl = 2.2 + t * 2.2 + (fbm(x / (14 + 40 * t), y / (3 + 12 * t), 12) - 0.5) * 1.6
            # el camí, de terra més clara, del primer pla a la porta
            cxp = 300 - (y - HOR) * 0.4
            if abs(x - cxp) < 18 + t * 70:
                lvl += 0.6
            cv.put(x, y, EARTH, lvl, lit=0.9)
            # fulles caigudes: més grosses a prop
            s = 1 + int(t * 3)
            if hr(x // s, y // s, 5) > 0.955 and fbm(x / 40, y / 12, 77) > 0.48:
                cv.put(x, y, LEAF, 2.0 + hr(x // s, y // s, 6) * 3, lit=0.7)


def _tanca_x(y):
    """La x de la base de la tanca a l'alçada y del terra (la tanca fuig cap al fons, a l'esquerra)."""
    return 392 + (y - 198) / 70 * 268


# ─── La tanca i el cartell ─────────────────────────────────────────────────

def _fence_t(x):
    return (x - 392) / 268


def _fence_base(x):
    return 198 + _fence_t(x) * 70


def _fence_h(x):
    return 62 + _fence_t(x) * 96


def tanca(cv):
    # la malla (de rombes, que s'engrandeixen a prop)
    for x in range(392, W):
        t = _fence_t(x)
        base, h = _fence_base(x), _fence_h(x)
        cell = 6 + 6 * t
        u = (x - 392) / (6 + 3 * t)
        for y in range(int(base - h), int(base)):
            v = (base - y) / cell
            if abs(((u + v) % 1.0) - 0.5) > 0.5 - 0.09 - 0.05 * t or abs(((u - v) % 1.0) - 0.5) > 0.5 - 0.09 - 0.05 * t:
                cv.put(x, y, STEEL, 3.0 + t * 1.6 - (base - y) / h * 0.6, lit=0.3)
        # el tub de dalt i el de baix
        for yy, lv in ((base - h, 5.0), (base - h + 1, 3.4), (base - 1, 3.0)):
            cv.put(x, yy, STEEL, lv + t, lit=0.3)
    # els pals
    for t in (0.0, 0.18, 0.38, 0.6, 0.84):
        x = 392 + t * 268
        base, h = _fence_base(x), _fence_h(x)
        r = 1.2 + 2.6 * t
        for y in range(int(base - h - 4), int(base + 2)):
            for xx in range(int(x - r), int(x + r) + 1):
                cv.put(xx, y, STEEL, 4.6 - (xx - x) / r * 1.6 + t, lit=0.3)
        cv.rect(x - r - 1, base - h - 6, x + r + 1, base - h - 4, STEEL, 6.0, lit=0)
        cv.rect(x - r - 2, base, x + r + 2, base + 2 + t * 3, STONE, 3.0, lit=0.4)   # el dau de formigó
    # la porta de la tanca, amb el cadenat
    xp = 392 + 0.6 * 268
    cv.rect(xp - 3, _fence_base(xp) - 56, xp + 1, _fence_base(xp) - 50, IRONK, 3.0, lit=0)
    cv.rect(xp - 2, _fence_base(xp) - 50, xp, _fence_base(xp) - 47, IRONK, 2.0, lit=0)
    cartell(cv)


def cartell(cv):
    """El cartell lluminós: «BOSC 2.0» en verd fluor, la fulla de NaturaPlus i el compte enrere."""
    xl, xr = 488, 616
    def top(x):
        return 74 - (x - xl) * 0.10
    def bot(x):
        return 132 + (x - xl) * 0.08
    for x in range(xl - 3, xr + 4):                                                 # el marc, blanc
        for y in range(int(top(x)) - 3, int(bot(x)) + 4):
            cv.put(x, y, PLASTIC, 3.6 - (0.8 if x > xr else 0), lit=0)
    for x in range(xl, xr + 1):
        for y in range(int(top(x)), int(bot(x)) + 1):
            cv.put(x, y, SIGNK, 1.6 + (y - top(x)) / (bot(x) - top(x)) * 0.8, lit=0)
    sh = -0.10
    cv.glow(552, 98, 70, (150, 255, 120), 0.25)
    t1 = 'BOSC 2.0'
    text(cv, t1, 552 - text_width(t1, 3) // 2, int(top(552 - text_width(t1, 3) // 2)) + 8, (170, 255, 120), k=3, shear=sh)
    t2 = 'NATURAPLUS S.A.'
    x2 = 552 - text_width(t2) // 2 + 4
    text(cv, t2, x2, int(top(x2)) + 30, (230, 236, 240), shear=sh)
    cv.disc(x2 - 6, int(top(x2)) + 32, 2.4, 3, NEON, 4.0, lit=0)                    # la fulla
    t3 = 'INAUGURACIO: 2 DIES'
    x3 = 552 - text_width(t3) // 2
    text(cv, t3, x3, int(top(x3)) + 42, (250, 206, 90), shear=sh)
    for x in range(xl + 4, xr - 3):                                                 # la línia de neó de sota
        cv.put(x, top(x) + 52 + (x - xl) * 0.0, NEON, 4.6, lit=0)
    # els suports
    for x in (500, 604):
        cv.rect(x - 1, bot(x) + 4, x + 1, _fence_base(x) - _fence_h(x), STEEL, 3.2, lit=0)


# ─── El roure ──────────────────────────────────────────────────────────────

def roure(cv):
    # les branques grosses, que surten del quadre
    for p0, p1, p2, r0, r1, s in (((200, 70), (120, 30), (-20, 10), 20, 9, 3),
                                  ((228, 60), (300, 20), (420, -10), 16, 6, 4),
                                  ((190, 110), (110, 90), (40, 70), 9, 3, 5),
                                  ((236, 96), (290, 76), (330, 50), 7, 2, 6)):
        arrel(cv, p0, p1, p2, r0, r1, base=3.0, seed=s)
    # el tronc
    for y in range(0, TBASE + 6):
        c, w = tronc_c(y), tronc_w(y)
        for x in range(int(c - w), int(c + w) + 1):
            u = (x - c) / w
            fis = fbm(u * 9 + 3, y / 34, 41, 3)
            lvl = 3.6 - u * 1.3 - abs(u) ** 6 * 1.8 + (fis - 0.5) * 2.4
            if fis < 0.36:
                lvl -= 1.6                                                          # les esquerdes de l'escorça
            if u < -0.15 and fbm(x / 8, y / 10, 44) > 0.62 + u * 0.25:
                cv.put(x, y, MOSS, lvl + 0.6, lit=0.9)
            else:
                cv.put(x, y, BARK, lvl, lit=0.9)
    # les arrels per terra
    for p1, p2, r0, s in (((120, 246), (30, 262), 15, 11), ((150, 262), (96, 286), 13, 12),
                          ((290, 262), (330, 282), 12, 13), ((300, 244), (382, 252), 11, 14),
                          ((176, 258), (186, 290), 10, 15), ((80, 232), (10, 238), 8, 16)):
        arrel(cv, (TC + (p2[0] - TC) * 0.15, TBASE - 8), p1, p2, r0, 2, base=3.4, seed=s)
    porta(cv)


def porta(cv):
    cx, top, bot, hw = DOOR
    # el forat de la porta, una mica enfonsat, i el marc d'escorça
    for y in range(top - 4, bot + 1):
        for x in range(cx - hw - 4, cx + hw + 5):
            d = math.hypot(x - cx, (y - (top + hw)) * 1.0) if y < top + hw else abs(x - cx)
            if d <= hw:
                plank = (x - cx + hw) % 6 == 0
                lvl = 3.6 - (1.6 if plank else 0) - (y - top) * 0.012 + (x - cx) / hw * -0.4 + (fbm(x / 2, y / 9, 7) - 0.5)
                cv.put(x, y, PLANK, lvl, lit=0.7)
            elif d <= hw + 4:
                cv.put(x, y, BARK, 1.4 + (d - hw) * 0.3, lit=0.6)
    for yy in (top + 18, bot - 12):                                                  # frontisses
        cv.rect(cx - hw, yy, cx - hw + 12, yy + 2, IRONK, lambda x, y: 2.6 - (x - cx + hw) * 0.08, lit=0.5)
    cv.disc(cx + hw - 6, top + 32, 2, 2, IRONK, lambda nx, ny: 3.0 - ny, lit=0.5)    # la baula
    cv.rect(cx - hw - 6, bot, cx + hw + 6, bot + 3, STONE, lambda x, y: 3.6 - (1.2 if x % 7 == 0 else 0), lit=0.8)   # el graó
    # la campaneta (a l'esquerra) i el fanalet vermell (a la dreta)
    bx, by = cx - hw - 12, top + 14
    cv.rect(bx - 1, by - 8, bx + 6, by - 7, IRONK, 2.4)
    cv.disc(bx, by - 2, 3.4, 4, [(60, 40, 10), (130, 96, 30), (200, 160, 60), (240, 210, 120)],
            lambda nx, ny: 2.4 - nx - ny * 0.4)
    lx, ly = cx + hw + 14, top + 12
    cv.rect(lx - 7, ly - 10, lx + 1, ly - 9, IRONK, 2.4)
    cv.rect(lx - 4, ly - 7, lx + 4, ly + 6, IRONK, 1.6)
    cv.rect(lx - 3, ly - 5, lx + 3, ly + 4, REDL, lambda x, y: 3.6 - abs(x - lx) * 0.3 - abs(y - ly) * 0.2, lit=0)
    cv.glow(lx, ly, 26, (255, 70, 40), 0.6)
    # la bústia, en un pal, amb la nota
    mx, my = cx + hw + 22, bot - 26
    cv.rect(mx, my + 10, mx + 2, bot + 1, PLANK, 2.4, lit=0.7)
    cv.rect(mx - 6, my, mx + 8, my + 10, PLANK, lambda x, y: 3.4 - (y - my) * 0.1 - (1.4 if y == my + 3 else 0), lit=0.7)
    cv.rect(mx - 3, my - 3, mx + 3, my, CREAM_NOTE, 3.0, lit=0.6)


CREAM_NOTE = [(80, 70, 56), (150, 136, 110), (210, 196, 166), (240, 232, 210)]


def estaca(cv):
    """L'estaca de topògraf, clavada davant la porta, amb la cinta de NaturaPlus."""
    x, y0, y1 = DOOR[0] + 10, 224, 250
    for y in range(y0, y1):
        for xx in range(x - 1, x + 2):
            cv.put(xx, y, PLANK, 4.0 - (xx - x) * 0.8, lit=0.8)
    cv.rect(x - 1, y0, x + 1, y0 + 3, CONE, 3.6, lit=0.4)                           # la punta pintada
    for i in range(16):                                                             # la cinta, que voleia
        tx, ty = x + 1 + i, y0 + 5 + math.sin(i * 0.6) * 2 + i * 0.25
        cv.put(tx, ty, NEON, 3.6 - (i % 4 == 0) * 1.2, lit=0.4)
        cv.put(tx, ty + 1, NEON, 2.6, lit=0.4)
    ombra(cv, x + 7, y1, 9, 2)


def cargol(cv):
    x, y = 470, 246
    cv.rect(x, y, x + 3, y, STEEL, 6.0, lit=0)
    cv.flat(x + 1, y - 1, (240, 244, 250))
    cv.glow(x + 1, y, 5, (230, 240, 255), 0.6)


# ─── La xarxa: bolets i filaments ──────────────────────────────────────────

def xarxa(cv, glow):
    dim = glow < 0.5
    for seed, (x, y, a, l) in enumerate(((150, 252, 3.0, 120), (110, 270, 2.6, 110), (290, 266, 0.2, 90),
                                         (230, 282, 3.4, 80), (340, 252, 0.0, 60), (60, 248, 3.3, 70))):
        filament(cv, x, y, a, l, seed + 3, glow=glow, dim=dim)
    for x, y, h, r in ((150, 214, 6, 6), (161, 208, 4, 4), (140, 222, 3, 3), (268, 196, 5, 5), (276, 204, 3, 3),
                       (60, 236, 7, 7), (72, 240, 4, 4), (318, 254, 4, 4), (106, 254, 5, 5), (182, 160, 4, 4),
                       (174, 166, 3, 3)):
        bolet(cv, x, y, h, r, glow=glow)


# ─── Primer pla ────────────────────────────────────────────────────────────

def primer_pla(cv):
    # falgueres a l'esquerra, a contrallum (la vora de dalt, càlida)
    for i, (x, y, a, l, s) in enumerate(((-6, 300, 1.15, 150, -1), (14, 298, 0.8, 170, -1), (46, 300, 1.45, 120, 1),
                                          (-10, 262, 0.45, 120, -1), (84, 300, 1.85, 90, 1), (24, 300, 1.7, 140, 1))):
        falguera(cv, x, y, a, l, side=s, lvl=1.5 + i * 0.1, rim=1, seed=i)
    # una pedra i falgueres a la dreta
    cv.disc(612, 290, 46, 26, STONE, lambda nx, ny: 2.0 - ny * 1.4 - nx * 0.6 + (fbm(nx * 4, ny * 4, 3) - 0.5) * 1.6)
    cv.disc(612, 290, 46, 26, MOSS, lambda nx, ny: 1.0 if ny < -0.55 and fbm(nx * 5, 1, 9) > 0.5 else -9)
    for i, (x, y, a, l, s) in enumerate(((556, 300, 1.7, 110, 1), (596, 296, 2.1, 130, 1), (646, 300, 2.4, 110, 1))):
        falguera(cv, x, y, a, l, side=s, lvl=1.6, seed=10 + i)
    # una arrel gruixuda que passa pel davant, a baix
    arrel(cv, (180, 300), (240, 282), (330, 300), 9, 6, base=2.2, seed=31, moss=True)


# ─── Composició ────────────────────────────────────────────────────────────

IRI_PEUS = (354, 266)


def fons(glow):
    cv = Canvas(W, H, light=LIGHT)
    cel(cv)
    bosc_fons(cv)
    obra(cv)
    terra(cv)
    tanca(cv)
    roure(cv)
    estaca(cv)
    cargol(cv)
    xarxa(cv, glow)
    ombra(cv, IRI_PEUS[0] + 8, IRI_PEUS[1] + 1, 14, 3)
    return cv


def main():
    for nom, glow in (('vora-bosc', 0.25), ('vora-bosc-encesa', 1.0)):
        cv = fons(glow)
        sala = cv.img.copy()
        iri = nenes.nena(nenes.IRI, 'DL', 'iri')
        cv.img.alpha_composite(iri, (IRI_PEUS[0] - 25, IRI_PEUS[1] - 83))
        cv.P = cv.img.load()
        primer_pla(cv)
        if nom == 'vora-bosc':
            sala2 = Canvas(W, H, light=LIGHT, img=sala)
            primer_pla(sala2)
            sala2.img.save(HERE / 'vora-bosc-sala.png')
        nearest(cv.img, (W * 2, H * 2)).save(HERE / f'{nom}.png')
        print(f'{nom}.png')


if __name__ == '__main__':
    main()
