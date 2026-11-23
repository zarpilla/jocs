"""
L'Última Arrel — `zona_zero`, la Zona Zero (Escena 6, Iri; la Vet hi és, entre el públic). Dilluns, Festa Major, les
deu del matí. Sala «de lluny».

Un clar del bosc a mig desbrossar. El sol del matí entra per l'esquerra, baix i càlid: les ombres van cap a la dreta.
El bosc que queda (càlid, de tardor) envolta el clar; NaturaPlus hi ha plantat les seves coses, blanques i planes:

  - Al mig, l'**escenari** blanc (girat: se'n veuen la tapa, el davant i el costat), amb la cinta vermella per tallar
    entre dos pals i el faristol de tres quarts, amb el micro. Hi és la `pla`.
  - Darrere, la **pantalla** gegant sobre una bastida: «BOSC 2.0» en verd fluor i «LA NATURA, PERÒ MILLOR».
  - A la dreta, els **sensors** d'aire: tres columnes blanques amb la lectura verda «AIRE: / PUR / 100%» (decorat
    `sensors_vermells`: «AIRE: / PICANT / !!!» en vermell, amb el núvol de pol·len); i l'**altaveu** de la caseta,
    damunt d'una caixa de transport.
  - A l'esquerra, el **públic** del poble, d'esquena, mirant l'escenari (figures de fons, amb polseres de punts): una
    fila de darrere (al fons) i una de davant (capa del davant: la Vet i l'àvia hi queden entremig).
  - Les **soques** tallades, entre el públic i l'escenari, amb la gespa artificial a mig estendre.
  - Al fons, entre els arbres, la **formigonera**, amb el motor engegat (ANIMS: el bombo que gira i el fum).
  - El bassal (on és el `bufo`) i la `txell` amb el càmera (figura de fons) a la dreta.
  - Dalt de tot de la pantalla, just a sobre dels sensors, la **caseta de paper** que la Vet hi ha deixat a la 6a
    (l'amagatall de les fades); la `urtica`, petita, n'ha sortit i s'hi està asseguda al costat.
  - Primer pla (FRONT): una soca gran acabada de tallar a l'esquerra, falgueres amb la cinta d'obra a la dreta, i la
    perxa de so de la TV, que entra per dalt a la dreta i apunta a la Pla.
  - El públic té volum (`persona` de _comu_dia: llum rasant de l'esquerra, a tons plans com els fulls, ombres
    llargues, i cada figura amb la seva roba i complements: motxilles, bufandes, gorros, mòbils gravant).
"""
import functools
import math
import random

from PIL import Image

from hd.pix import Canvas, Light
from hd640.rooms._comu_dia import (
    W, H, RH, Terra, fbm, hr, boira_px, smooth, lletres, ample, arrel, falguera, ombra, capcada, tronc, persona,
    diferencia, mascara, HAZE, LEAVES, BARK, MOSS, EARTH, PLANK, IRONK, STONE, CREAM, PLASTIC, STEEL, NEON, SIGNK,
    CONE, REDL, YELLOWM, SKYD, DRYG, CLAY, GREENL, WATER, FERN, LEAF, CLOTH)

T = Terra(hor=112, h=140, f=500)
HOR = T.hor
SOL = (-80, 30)                                    # el sol del matí, baix a l'esquerra

LIGHT = Light(ambient=0.15, vignette=(70, 16), floor_fade=None)
LIGHT.width = W
LIGHT.point(SOL[0], SOL[1], r=760, k=1.3, squash=0.8, power=1.1)

BOIRA = (226, 214, 190)                            # la llum del matí, a l'aire del fons

# L'escenari: la tapa (4 cantons), i l'alçada del davant
ESC_TAPA = [(300, 180), (490, 173), (518, 189), (322, 198)]
ESC_H = 14
SENSORS = (527, 557, 587)                          # x del mig de cada columna
SENS_BASE, SENS_TOP, SENS_W = 206, 112, 13        # (mig ample)
ALTAVEU = (498, 186)                               # el peu de la caixa (damunt l'escenari, a la dreta)
CASETA = (548, 21)                                 # la caseta de paper: el mig de la base, damunt el marc de la pantalla


# ─── Cel i bosc ──────────────────────────────────────────────────────────────

def cel(cv):
    for y in range(0, HOR + 4):
        for x in range(W):
            d = math.hypot(x - SOL[0], (y - SOL[1]) * 1.4)
            lvl = 1.8 + 3.0 * (y / HOR) ** 1.4 + 2.6 * max(0.0, 1 - d / 420) ** 1.4
            c = fbm(x / 70, y / 16, 5)
            if c > 0.6 and y < 70:                                                  # uns núvols prims
                lvl += (c - 0.6) * 8
            cv.put(x, y, SKYD, lvl, lit=0)


def bosc_fons(cv):
    """La paret de bosc que envolta el clar: càlid, de tardor, i més clar (calitja) com més lluny."""
    for x in range(W):
        top = HOR - 44 - 22 * fbm(x / 34, 0.5, 9) - 10 * fbm(x / 9, 1.5, 4) + 26 * smooth(140, 230, x) * smooth(300, 230, x)
        for y in range(int(top), HOR + 4):
            f = fbm(x / 7, y / 6, 6)
            fulla = fbm(x / 26, y / 16, 7)
            ramp = LEAF if fulla > 0.6 else LEAVES if fulla > 0.42 else GREENL
            lvl = 3.0 + (f - 0.5) * 2.2 - (y - top) * 0.03 + (1.2 if top + 2 > y else 0) - (0.6 if ramp is LEAF else 0)
            if fbm(x / 3, y / 12, 8) < 0.3:
                ramp, lvl = BARK, 2.6                                             # troncs entre les fulles
            cv.put(x, y, ramp, lvl, lit=0.6)
            boira_px(cv, x, y, BOIRA, 0.3)


def arbres_vora(cv):
    """Els arbres grossos de les vores: un roure a l'esquerra (amb les branques de dalt, on hi ha les fades) i un faig
    a la dreta."""
    tronc(cv, 34, -4, 206, 16, 26, 11, base=2.8, lit=0.6, molsa=0.7)
    tronc(cv, 640, -4, 214, 14, 22, 12, base=2.4, lit=0.5, molsa=0.75)
    for p0, p1, p2, r0, r1, s in (((40, 60), (110, 40), (200, 30), 7, 2, 21), ((40, 30), (90, 6), (170, -6), 8, 3, 22),
                                  ((630, 50), (590, 30), (520, 18), 6, 2, 23), ((36, 100), (70, 92), (96, 96), 3, 1, 24)):
        arrel(cv, p0, p1, p2, r0, r1, base=3.0, seed=s, lit=0.5, moss=False)

    def fe(x, y):
        return max(0.0, math.hypot((x + 10) / 250, (y + 30) / 110) - 0.7) * 1.4

    def fd(x, y):
        return max(0.0, math.hypot((x - 660) / 170, (y + 20) / 100) - 0.7) * 1.4
    capcada(cv, -10, 260, -4, 90, 31, ramp=LEAVES, ramp2=LEAF, base=3.2, edge=0.38, lit=0.6, sx=15, sy=10, forma=fe)
    capcada(cv, 470, W, -4, 90, 32, ramp=LEAVES, ramp2=GREENL, base=3.0, edge=0.38, lit=0.6, sx=15, sy=10, forma=fd)


def formigonera(cv):
    """La formigonera al fons, entre els arbres: la cabina blanca de NaturaPlus i el bombo a ratlles."""
    x0, base = 182, HOR + 6
    # el talús de terra remoguda i la cinta d'obra davant
    for x in range(150, 290):
        top = base - 2 - 9 * math.sin(math.pi * (x - 150) / 140) ** 0.7 - 3 * fbm(x / 10, 0.2, 3)
        for y in range(int(top), base + 3):
            cv.put(x, y, EARTH, 4.6 + (fbm(x / 4, y / 3, 4) - 0.5) * 1.4, lit=0.4)
    # el xassís i les rodes
    cv.rect(x0, base - 8, x0 + 62, base - 4, IRONK, 2.6, lit=0.2)
    for wx in (x0 + 8, x0 + 40, x0 + 54):
        cv.disc(wx, base - 3, 4, 4, IRONK, lambda nx, ny: 1.6 - ny * 0.6, lit=0)
        cv.flat(wx, base - 3, (120, 120, 124))
    # la cabina (a la dreta)
    cv.rect(x0 + 46, base - 26, x0 + 64, base - 8, PLASTIC, lambda x, y: 4.6 - (x - x0 - 46) * 0.06, lit=0.4)
    cv.rect(x0 + 50, base - 23, x0 + 62, base - 16, [(30, 50, 60), (60, 90, 110), (130, 170, 190)], 1.4, lit=0)
    cv.rect(x0 + 46, base - 12, x0 + 64, base - 11, NEON, 3.4, lit=0)
    _bombo(cv, 0)


BOMBO = (206, 102, 15, 8, -0.32)                    # centre, radis, inclinació


def _bombo(cv, fase):
    cx, cy, rx, ry, a = BOMBO
    c, s = math.cos(a), math.sin(a)
    for y in range(int(cy - 13), int(cy + 13)):
        for x in range(int(cx - 19), int(cx + 19)):
            dx, dy = x - cx, y - cy
            u, v = dx * c + dy * s, -dx * s + dy * c
            nu, nv = u / rx, v / ry
            if nu * nu + nv * nv > 1 and not (abs(nv) < 0.9 - max(0, nu - 0.6) and -1 < nu < 1.2):
                continue
            if abs(nu) > 1.15:
                continue
            ratlla = int(nu * 2.4 + nv * 1.0 + fase) % 2
            lvl = 4.4 - nv * 1.6 + (0.0 if ratlla else -0.4)
            cv.put(x, y, CONE if ratlla else PLASTIC, lvl if ratlla else lvl + 0.6, lit=0.3)
    cv.disc(cx + rx * c * 1.1, cy + rx * s * 1.1, 3, 5, IRONK, 2.4, lit=0)            # la boca


# ─── El terra del clar ───────────────────────────────────────────────────────

def _rodada(x, z):
    """Les rodades de les màquines al terra desbrossat (al món)."""
    d1 = abs(x - (-40 - (z - 600) * 0.25)) % 70
    return d1 < 6 or abs(d1 - 14) < 4


def terra(cv):
    for v in range(HOR + 3, RH):
        for u in range(W):
            x, z = T.mon(u, v)
            near = smooth(800, 360, z)
            # desbrossat (terra nua, rodades) cap a la dreta i al fons; herba i fulles a l'esquerra
            nu = fbm(x / 120, z / 160, 21) + (u - 260) / 500
            f = fbm(x / 40, z / 60, 12)
            if nu > 0.55:
                ramp = EARTH
                lvl = 4.4 + (f - 0.5) * 1.6
                if _rodada(x, z):
                    lvl -= 1.0
            else:
                ramp = GREENL if fbm(x / 30, z / 50, 22) > 0.45 else DRYG
                g = fbm(x / (5 + 3 * near), z / (9 + 6 * near), 14)
                lvl = 3.2 + (f - 0.5) * 1.8 + (0.9 if g > 0.6 else -0.6 if g < 0.36 else 0)
            s = 1 + int(near * 3)
            if hr(u // s, v // s, 5) > 0.95 and fbm(x / 50, z / 80, 77) > 0.45:       # fulles caigudes
                ramp, lvl = LEAF, 2.4 + hr(u // s, v // s, 6) * 3
            cv.put(u, v, ramp, lvl, lit=0.6)
            if v < HOR + 24:
                boira_px(cv, u, v, BOIRA, 0.35 * (1 - (v - HOR - 3) / 21))


def gespa(cv):
    """La gespa artificial a mig estendre: tires verd fluor davant l'escenari, amb el rotllo al cap."""
    for (x0, x1, y0, y1, rot) in ((300, 470, 214, 222, 470), (330, 520, 224, 232, None)):
        for y in range(y0, y1):
            for x in range(x0 + (y - y0), x1 + (y - y0) // 2):
                cv.put(x, y, NEON, 2.6 + (0.6 if (x + y * 3) % 4 == 0 else 0) - (y - y0) * 0.05, lit=0.4)
            cv.put(x0 + (y - y0) - 1, y, NEON, 1.4, lit=0.2)
        cv.rect(x0 + (y1 - y0), y1, x1 + (y1 - y0) // 2, y1, NEON, 1.0, lit=0)
        if rot:
            rx = rot + (y1 - y0) // 2
            cv.disc(rx, (y0 + y1) / 2, 4, 6, NEON, lambda nx, ny: 2.8 - ny + (0.8 if math.hypot(nx, ny) % 0.5 < 0.2 else 0), lit=0.4)


def soques(cv):
    """Les soques tallades: el tall clar amb els anells, l'escorça fosca; i un munt de troncs."""
    for (x, y, r, s) in ((254, 214, 12, 1), (284, 207, 9, 2), (232, 205, 7, 3), (306, 216, 6, 4), (488, 228, 8, 5)):
        ombra(cv, x + r * 0.9, y + 2, r * 1.4, 2.4)
        cv.rect(x - r, y - r * 0.6, x + r, y, BARK, lambda xx, yy: 2.6 - (xx - x) / r * 1.0 + (fbm(xx / 2, yy / 5, s) - 0.5),
                lit=0.6)
        cv.disc(x, y - r * 0.6, r, r * 0.32, PLANK,
                lambda nx, ny: 6.0 - (1.4 if abs(math.hypot(nx, ny) * 4 % 1 - 0.5) < 0.16 else 0) - ny * 0.6, lit=0.4)
        cv.disc(x - r - 1, y - 1, 3, 2, BARK, 2.0, lit=0.5)


def bassal(cv):
    cx, cy = 270, 238
    for v in range(cy - 6, cy + 7):
        for u in range(cx - 34, cx + 35):
            d = math.hypot((u - cx) / 32, (v - cy) / 5.5) + (fbm(u / 9, v / 3, 51) - 0.5) * 0.3
            if d > 1:
                continue
            lvl = 4.0 + (v - cy) * 0.25 + (1.6 if fbm(u / 10, v / 2, 52) > 0.62 else 0)
            cv.put(u, v, WATER, lvl if d < 0.88 else 2.0, lit=0.3)


# ─── NaturaPlus: l'escenari, la pantalla, els sensors i l'altaveu ───────────

def escenari(cv):
    a, b, c, d = ESC_TAPA
    h = ESC_H
    # l'ombra, cap a la dreta (el sol és a l'esquerra)
    cv.poly([(b[0], b[1] + h), (b[0] + 30, b[1] + h + 2), (c[0] + 34, c[1] + h + 6), (c[0], c[1] + h)], STONE, 1.0, lit=0)
    cv.darken(c[0], c[1], c[0] + 40, c[1] + h + 8, lambda x, y: 0.7 if y > c[1] + (x - c[0]) * 0.2 else 0)
    # el costat de l'esquerra (al sol)
    cv.poly([a, d, (d[0], d[1] + h), (a[0], a[1] + h)], PLASTIC, lambda x, y: 5.2, lit=0.3)
    # el davant (de cara al públic, a mitja ombra), amb la franja verda
    cv.poly([d, c, (c[0], c[1] + h), (d[0], d[1] + h)], PLASTIC,
            lambda x, y: 3.8 - (x - d[0]) * 0.004 - (1.2 if (x - d[0]) % 32 == 0 else 0), lit=0.3)
    for x in range(d[0], c[0]):
        t = (x - d[0]) / (c[0] - d[0])
        y = d[1] + (c[1] - d[1]) * t + 4
        cv.put(x, y, NEON, 3.6, lit=0)
        cv.put(x, y + 1, NEON, 2.8, lit=0)
    # la tapa
    cv.poly([a, b, c, d], PLASTIC, lambda x, y: 5.6 - (y - 173) * 0.03, lit=0.3)
    # l'escaleta, al costat de l'esquerra
    for k in range(3):
        cv.rect(d[0] - 10 - k * 4, d[1] + 2 + k * 4, d[0] - 1, d[1] + 5 + k * 4, PLASTIC, 5.0 - k * 0.2, lit=0.3)
        cv.rect(d[0] - 10 - k * 4, d[1] + 6 + k * 4, d[0] - 1, d[1] + 6 + k * 4, PLASTIC, 3.0, lit=0.3)
    # la cinta per tallar, entre dos pals de llautó, amb el llaç
    for px, py in ((346, 194), (392, 192)):
        cv.rect(px, py - 18, px + 1, py, YELLOWM, 4.4, lit=0.2)
        cv.disc(px + 0.5, py - 19, 1.5, 1.5, YELLOWM, 5.0, lit=0)
    for x in range(347, 392):
        y = 178 + (x - 347) * -0.04 + 2 * math.sin((x - 347) / 45 * math.pi)
        cv.put(x, y, REDL, 3.6, lit=0)
        cv.put(x, y + 1, REDL, 2.6, lit=0)
    cv.disc(369, 181, 3, 2, REDL, 3.4, lit=0)
    cv.disc(373, 181, 3, 2, REDL, 3.0, lit=0)
    faristol(cv)


def faristol(cv):
    """El faristol de la Pla, de tres quarts (la regla de les tres cares): el davant (al sol, amb la fulla de NaturaPlus),
    el costat de la dreta (a l'ombra), el tauló de dalt inclinat, i el micro de coll de cigne que va cap a ella."""
    fl, fr, br = (446, 190), (461, 193), (471, 188)                      # la base: davant esquerra, davant dreta, darrere
    tl, tr, tb, tk = (444, 165), (462, 168), (473, 162), (455, 159)      # dalt: davant esq., davant dreta, darrere dreta, darrere esq.
    ombra(cv, 470, 192, 14, 2.4, k=0.7)
    cv.poly([tr, tb, br, fr], PLASTIC, lambda x, y: 2.6 - (y - 165) * 0.01, lit=0.2)          # el costat, a l'ombra
    cv.poly([tl, tr, fr, fl], PLASTIC, lambda x, y: 4.8 - (x - 444) * 0.04, lit=0.3)         # el davant
    cv.poly([tk, tb, tr, tl], PLASTIC, 5.8, lit=0.3)                                         # el tauló de dalt
    for x in range(446, 462):                                                                # la franja verda
        y = 186 + (x - 446) * 0.2
        cv.put(x, y, NEON, 3.4, lit=0)
    cv.disc(453, 175, 3.4, 4.2, NEON, lambda nx, ny: 3.6 - nx * 0.6 - ny * 0.4, lit=0)        # la fulla
    cv.line(453, 178, 455, 181, NEON, 2.0, lit=0)
    for i in range(12):                                                                       # el coll de cigne
        t = i / 11
        cv.put(452 - t * 9, 160 - t * 9 + t * t * 4, IRONK, 2.4, lit=0)
    cv.disc(442, 154, 2.2, 1.8, IRONK, lambda nx, ny: 1.4 - nx * 0.4 - ny * 0.8, lit=0)       # la bola del micro


def pantalla(cv):
    """La pantalla gegant, sobre una bastida d'acer: «BOSC 2.0» i el lema."""
    x0, x1, y0, y1 = 384, 560, 24, 112
    # la bastida (darrere i les potes, fins a l'escenari)
    for x in (x0 + 8, x1 - 8):
        for k in (-3, 3):
            cv.rect(x + k, y1, x + k, 178, STEEL, 4.6 - (k > 0), lit=0.3)
        for y in range(y1, 178, 10):
            cv.line(x - 3, y, x + 3, y + 10, STEEL, 3.6, lit=0.3)
    cv.rect(x0 - 3, y0 - 3, x1 + 3, y1 + 3, STEEL, lambda x, y: 3.0 + (1.0 if y < y0 else 0), lit=0.3)
    # la pantalla: píxels de LED, fosca, amb un degradat verd
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            lvl = 1.4 + (y - y0) / (y1 - y0) * 1.4
            if x % 3 == 0 or y % 3 == 0:
                lvl -= 0.6
            cv.put(x, y, [(4, 20, 14), (8, 40, 24), (14, 66, 36), (24, 96, 50), (40, 130, 64)], lvl, lit=0)
    # l'arbre de plàstic que somriu (el logotip), a l'esquerra
    lx, ly = 412, 70
    cv.rect(lx - 1, ly, lx + 1, ly + 22, [(60, 40, 20), (120, 90, 50), (180, 140, 80)], 2.0, lit=0)
    cv.disc(lx, ly - 6, 15, 14, NEON, lambda nx, ny: 4.0 - ny * 0.8 + (0.6 if (nx * 7 + ny * 5) % 1 < 0.5 else 0), lit=0)
    cv.flat(lx - 5, ly - 9, (10, 30, 10))
    cv.flat(lx + 5, ly - 9, (10, 30, 10))
    for k in range(-5, 6):
        cv.flat(lx + k, ly - 3 - round(k * k * 0.08), (10, 30, 10))
    # «BOSC 2.0» i el lema
    t1 = 'BOSC 2.0'
    lletres(cv, t1, 440, 40, (190, 255, 140), k=4)
    cv.glow(500, 50, 70, (150, 255, 120), 0.25)
    t2 = 'LA NATURA, PERÒ MILLOR'
    lletres(cv, t2, 442 + (110 - ample(t2)) // 2, 76, (236, 246, 236))
    t3 = 'NATURAPLUS S.A.'
    lletres(cv, t3, 442 + (110 - ample(t3)) // 2, 92, (150, 220, 140))
    # els altaveus de la bastida
    for x in (x0 - 14, x1 + 6):
        cv.rect(x, 50, x + 8, 72, IRONK, 1.8, lit=0.2)
        cv.disc(x + 4, 58, 2.6, 2.6, IRONK, 0.8, lit=0)
        cv.disc(x + 4, 67, 2, 2, IRONK, 0.8, lit=0)


def _lectura(cv, x, y, linies, col, glow):
    for i, s in enumerate(linies):
        lletres(cv, s, x - ample(s) // 2, y + i * 8, col)
    cv.glow(x, y + 10, 18, glow, 0.25)


def sensors(cv):
    """Tres columnes blanques amb la pantalleta verda (AIRE: / PUR / 100%)."""
    for i, cx in enumerate(SENSORS):
        base = SENS_BASE - i * 2
        top = SENS_TOP + i * 3
        w = SENS_W
        ombra(cv, cx + 14, base + 1, 16, 2.6, k=0.7)
        for y in range(top, base):
            for x in range(cx - w, cx + w + 1):
                u = (x - cx) / w
                cv.put(x, y, PLASTIC, 5.6 - u * 1.6 - abs(u) ** 4 * 1.0, lit=0.2)
        cv.disc(cx, top, w, 3.6, PLASTIC, lambda nx, ny: 6.0 - nx * 1.2 - ny, lit=0.2)                 # la cúpula
        cv.disc(cx, top - 3, 2.6, 2.6, NEON, 4.6, lit=0)                                              # el piló
        for x in range(cx - w, cx + w + 1):                                                           # les reixetes
            for y in (top + 10, top + 12, top + 14):
                if x % 2 == 0:
                    cv.put(x, y, STEEL, 3.4, lit=0)
        # la pantalleta
        cv.rect(cx - w + 1, top + 20, cx + w - 1, top + 46, SIGNK, 1.6, lit=0)
        _lectura(cv, cx + 1, top + 23, ('AIRE:', 'PUR', '100%'), (170, 255, 130), (150, 255, 110))
        cv.rect(cx - w, base - 3, cx + w, base, STEEL, 3.0, lit=0.2)


def sensors_vermells(cv):
    """La lectura en vermell (AIRE: / PICANT / !!!) i el pol·len groc que encara volta per les columnes."""
    for i, cx in enumerate(SENSORS):
        top = SENS_TOP + i * 3
        w = SENS_W
        cv.rect(cx - w + 1, top + 20, cx + w - 1, top + 46, SIGNK, 1.6, lit=0)
        _lectura(cv, cx + 1, top + 23, ('AIRE:', 'PICANT', '!!!'),
                 (255, 90, 70), (255, 60, 40))
    rnd = random.Random(5)
    for _ in range(260):
        x = 557 + rnd.gauss(0, 30)
        y = 150 + rnd.gauss(0, 26)
        cv.flat(x, y, (250, 220, 90) if rnd.random() < 0.7 else (255, 244, 170))


def altaveu(cv):
    """L'altaveu gran de la caseta («Sons del Bosc — versió prèmium»), damunt la caixa de transport."""
    x, base = ALTAVEU
    ombra(cv, x + 10, base + 1, 20, 2.6, k=0.7)
    # la caixa de transport (gris acer, cantoneres)
    cv.rect(x - 16, base - 16, x + 16, base, STEEL, lambda xx, yy: 3.0 - (xx - x) * 0.03, lit=0.3)
    cv.rect(x - 16, base - 17, x + 16, base - 16, STEEL, 5.0, lit=0.3)
    for cx in (x - 16, x + 14):
        cv.rect(cx, base - 16, cx + 2, base - 13, PLASTIC, 4.0, lit=0)
    # l'altaveu (negre, dues boques, l'etiqueta i la ruleta)
    sx0, sx1, sy0, sy1 = x - 13, x + 13, base - 52, base - 17
    cv.rect(sx0, sy0, sx1, sy1, IRONK, lambda xx, yy: 2.6 - (xx - x) * 0.05, lit=0.3)
    cv.rect(sx0, sy0, sx1, sy0, IRONK, 4.0, lit=0.3)
    cv.disc(x, sy0 + 10, 6, 6, IRONK, lambda nx, ny: 0.6 + math.hypot(nx, ny) * 2.0, lit=0)
    cv.disc(x, sy0 + 25, 8, 8, IRONK, lambda nx, ny: 0.6 + math.hypot(nx, ny) * 2.0, lit=0)
    cv.rect(sx0 + 2, sy1 - 4, sx0 + 12, sy1 - 2, CREAM, 4.6, lit=0)                                 # l'etiqueta
    cv.disc(sx1 - 4, sy1 - 3, 1.6, 1.6, NEON, 4.0, lit=0)                                           # la ruleta


# ─── La gent ─────────────────────────────────────────────────────────────────

FILA_FONS = [(22, 200, 72, 1), (46, 199, 66, 2), (70, 201, 76, 3), (124, 200, 70, 5), (148, 198, 52, 6),
             (172, 200, 74, 7), (196, 199, 68, 8), (218, 201, 60, 9)]
FILA_DAVANT = [(14, 224, 82, 11), (40, 226, 64, 12), (126, 225, 80, 14), (176, 223, 76, 15), (206, 226, 58, 16)]
VET, AVIA = (150, 214), (90, 213)


def public_fons(cv):
    for (x, y, alt, s) in FILA_FONS:
        persona(cv, x, y, alt, s, cara=-1 if s % 3 else 1)
        ombra(cv, x + 6, y + 1, 8, 1.6, k=0.6)


def public_davant(cv):
    for (x, y, alt, s) in FILA_DAVANT:
        persona(cv, x, y, alt, s, cara=-1 if s % 4 else 1, gorra=s == 12)


def camera(cv):
    """El càmera de la TV Comarca (figura de fons), amb la càmera a l'espatlla."""
    x, y = 628, 242
    persona(cv, x, y, 84, 33, cara=1, polsera=False)
    cv.rect(x - 14, y - 70, x + 4, y - 60, IRONK, lambda xx, yy: 2.0 + (xx - x + 14) * 0.03, lit=0.3)
    cv.disc(x - 15, y - 65, 3, 4, IRONK, 3.2, lit=0)
    cv.flat(x - 16, y - 66, (160, 200, 240))
    cv.rect(x - 4, y - 74, x + 2, y - 71, IRONK, 2.0, lit=0)
    cv.flat(x + 3, y - 69, (240, 40, 30))                                                           # gravant
    lletres(cv, 'TV', x - 10, y - 68, (230, 230, 230))
    ombra(cv, x + 10, y + 1, 12, 2.2, k=0.7)


def branques(cv):
    """Les branques de dalt, a l'esquerra."""
    arrel(cv, (20, 58), (70, 48), (150, 56), 5, 2, base=3.0, seed=61, lit=0.5, moss=True)


def caseta_paper(cv):
    """La caseta de paper (el fullet de NaturaPlus doblegat en tres), dalt de la pantalla: blanca, amb la fulla verda
    fluor del logotip a fora, i a la porta, fosca, una cresta de fada que treu el cap."""
    cx, by = CASETA
    for yy in range(by - 10, by + 1):
        half = (yy - (by - 10)) * 0.9
        for xx in range(int(cx - half), int(cx + half) + 1):
            esquerra = xx < cx
            cv.put(xx, yy, PLASTIC, (5.2 if esquerra else 4.0) - (yy - by + 10) * 0.08, lit=0.4)
    for yy in range(by - 10, by + 1):                                                           # el plec del mig
        cv.put(cx, yy, PLASTIC, 2.8, lit=0.4)
    cv.disc(cx - 4, by - 4, 1.6, 1.4, NEON, 3.6, lit=0)                                         # el logotip
    cv.rect(cx + 2, by - 4, cx + 4, by, IRONK, 0.8, lit=0)                                      # la porta
    cv.flat(cx + 3, by - 5, (200, 210, 140))                                                    # una cresta de fada
    cv.flat(cx + 3, by - 6, (230, 236, 170))
    ombra(cv, cx + 3, by + 1, 9, 1, k=0.5)


# ─── Primer pla ──────────────────────────────────────────────────────────────

def primer_pla(cv):
    # a l'esquerra, la soca gran acabada de tallar (el tall, clar, amb els anells)
    x, y, r = 42, 262, 46
    cv.rect(x - r, y - 26, x + r, y + 4, BARK, lambda xx, yy: 1.8 - (xx - x) / r * 0.8 + (fbm(xx / 3, yy / 8, 71) - 0.5) * 1.4,
            lit=0)
    cv.disc(x, y - 26, r, 10, PLANK, lambda nx, ny: 4.6 - (1.4 if abs(math.hypot(nx, ny) * 7 % 1 - 0.5) < 0.14 else 0)
            - ny * 0.4 + nx * -0.6, lit=0)
    cv.disc(x + 10, y - 27, 4, 1.4, LEAF, 3.6, lit=0)                                               # una fulla
    # a la dreta: falgueres i la cinta d'obra, estripada
    for i, (fx, fy, a, l, sd) in enumerate(((600, 264, 1.9, 90, 1), (630, 262, 2.3, 100, 1), (650, 264, 2.6, 80, 1),
                                            (578, 266, 1.6, 60, -1))):
        falguera(cv, fx, fy, a, l, side=sd, lvl=1.8, rim=1, seed=30 + i)
    perxa(cv)
    for k in range(70):
        tx, ty = 566 + k, 230 + math.sin(k * 0.14) * 4 + k * 0.1
        on = (k // 5) % 2
        cv.flat(tx, ty, (230, 60, 40) if on else (240, 240, 236))
        cv.flat(tx, ty + 1, (170, 40, 30) if on else (190, 190, 190))


def perxa(cv):
    """La perxa de so de la TV Comarca, que entra pel cantó de dalt a la dreta (el tècnic és fora de quadre), molt a
    prop: un pal fosc que s'aprima cap al fons i el micro amb el pelut, que apunta a la Pla."""
    x0, y0, x1, y1 = 690, 54, 494, 118                      # (per sota dels rètols de la pantalla)
    n = 220
    for i in range(n + 1):
        t = i / n
        x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        r = 3.4 - t * 2.0
        for dy in range(-int(r) - 1, int(r) + 2):
            v = dy / max(r, 0.8)
            if abs(v) <= 1:
                cv.put(x, y + dy, IRONK, 1.6 - v * 1.4 + (0.8 if int(x) % 34 < 2 else 0), lit=0)
    # el pelut (el protector de vent), allargat en la direcció del pal: pèl gris clar, amb la vora encesa pel sol
    ang = math.atan2(y1 - y0, x1 - x0)
    ca, sa = math.cos(ang), math.sin(ang)
    cx, cy = x1 - ca * 6, y1 - sa * 6
    rnd = random.Random(91)
    for yy in range(int(cy - 12), int(cy + 13)):
        for xx in range(int(cx - 16), int(cx + 17)):
            u = ((xx - cx) * ca + (yy - cy) * sa) / 13
            v = (-(xx - cx) * sa + (yy - cy) * ca) / 6.0
            d = u * u + v * v
            if d <= 1 + (rnd.random() - 0.5) * 0.5:
                pel = 0.6 if (xx * 3 + yy * 5) % 4 == 0 else 0
                cv.put(xx, yy, STONE, 2.0 - v * 1.4 - u * 0.4 + pel + (1.6 if u < -0.5 and v < 0 else 0), lit=0)


# ─── Composició ─────────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _base():
    cv = Canvas(W, H, light=LIGHT)
    cel(cv)
    bosc_fons(cv)
    terra(cv)
    formigonera(cv)
    arbres_vora(cv)
    branques(cv)
    pantalla(cv)
    soques(cv)
    gespa(cv)
    escenari(cv)
    sensors(cv)
    altaveu(cv)
    bassal(cv)
    public_fons(cv)
    camera(cv)
    caseta_paper(cv)
    for y in range(RH, H):
        for x in range(W):
            cv.flat(x, y, (0, 0, 0))
    # les capes del davant
    fila = Canvas(W, H, light=LIGHT, transparent=True)
    public_davant(fila)
    pp = Canvas(W, H, light=LIGHT, transparent=True)
    primer_pla(pp)
    for c in (fila, pp):
        for y in range(RH, H):
            for x in range(W):
                c.P[x, y] = (0, 0, 0, 0)
        cv.img.alpha_composite(c.img)
    return cv.img, fila.img, pp.img


def bg(cv):
    img = _base()[0]
    cv.img.paste(img)
    cv.P = cv.img.load()


PROPS = {'sensors_vermells': sensors_vermells}


# ─── Animacions ──────────────────────────────────────────────────────────────

def _frames_formigonera():
    """El bombo que gira (les ratlles corren) i el fum del tub d'escapament."""
    base = _base()[0]
    out = []
    n = 8
    for i in range(n):
        cv = Canvas(W, H, light=LIGHT, img=base.copy())
        _bombo(cv, i / n * 2)
        rnd = random.Random(i)
        for k in range(3):
            t = ((i + k * n / 3) % n) / n
            fx, fy = 246 + t * 6, 84 - t * 16
            cv.disc(fx, fy, 2 + t * 3, 2 + t * 2.4, STONE, 5.6 - t * 1.4, lit=0)
        out.append(diferencia(cv.img, base))
    return out


ANIMS = {'formigonera': {'frames': _frames_formigonera, 'frameDuration': 110}}

FRONT = [
    # la fila de davant del públic: la Vet i l'àvia (a y ≈ 213) hi queden darrere; l'Iri hi passa per davant
    {'id': 'davant_public', 'mask': lambda x, y: mascara(_base()[1])(x, y), 'baseline': 222, 'zIndex': 20},
    {'id': 'davant', 'mask': lambda x, y: mascara(_base()[2])(x, y), 'baseline': 999, 'zIndex': 22},
]


# ─── Geometria ───────────────────────────────────────────────────────────────

# Els fulls dels personatges fan l'Iri de 68 px a escala 1 (la sala es va dibuixar pensant en 97): ×97/68.
K_FULLS = 97 / 68
ESCALA = (round(0.58 * K_FULLS, 3), round(0.77 * K_FULLS, 3))                              # a terra: a y = 198 i a y = 259 (l'Iri, de 56 a 75 px)

GEOMETRIA = {
    'things': {
        'soques': {'rect': (224, 192, 316, 222), 'walk': (270, 230)},
        'escenari': {'rect': (290, 172, 520, 212), 'walk': (400, 222)},
        'pantalla': {'rect': (380, 20, 564, 116), 'walk': (440, 222)},
        'sensors': {'rect': (512, 104, 602, 206), 'walk': (556, 226)},
        'altaveu': {'rect': (482, 132, 514, 188), 'walk': (500, 222)},
        'public': {'rect': (0, 160, 230, 226), 'walk': (150, 236)},
        'formigonera': {'rect': (170, 78, 256, 118), 'walk': (220, 232)},
    },
    'spawns': {'iri': (196, 246), 'vet': VET, 'avia': AVIA, 'pla': (424, 187), 'txell': (596, 246),
               'bufo': (306, 238), 'urtica': (532, 22)},
    'walkable': [(0, 236), (180, 232), (236, 230), (320, 218), (520, 216), (600, 222), (639, 230), (639, 256),
                 (0, 256)],
    # El sol del matí és baix a l'esquerra: l'ombra cau cap a la dreta, llarga.
    'floorSquash': 0.25,
    'characterShadow': {'enabled': True, 'color': '#2a1c10', 'alpha': 0.4, 'squash': 0.28, 'core': 0.6,
                        'light': {'x': 1, 'y': 0.15, 'direction': True, 'stretch': 0.7}},
    # La llum de la sala sobre els personatges: el matí de tardor (l'ambient, càlid) i el sol baix de l'esquerra, que
    # els toca pel costat esquerre i s'apaga cap a la dreta (cap als sensors i la caseta).
    'characterLights': {
        'ambient': '#c2b6a2',
        'lights': [{'x': SOL[0], 'y': SOL[1] + 120, 'radius': 700, 'color': '#ffd496', 'intensity': 0.55}],
    },
    'regions': [
        {'id': 'perspectiva', 'active': True, 'scaleEnabled': True, 'scaleWalkSpeed': True,
         'scaleTop': ESCALA[0], 'scaleBottom': ESCALA[1],
         'points': [(0, 198), (W - 1, 198), (W - 1, RH - 1), (0, RH - 1)]},
        # dalt l'escenari (la Pla): l'escala de la base de l'escenari, fixa
        {'id': 'escenari', 'active': True, 'scaleEnabled': True, 'scaleTop': round(0.57 * K_FULLS, 3), 'scaleBottom': round(0.57 * K_FULLS, 3),
         'points': [(300, 176), (490, 170), (518, 189), (322, 198)]},
        # dalt de la pantalla, al costat de la caseta de paper (la Urtica, de lluny)
        {'id': 'pantalla_dalt', 'active': True, 'scaleEnabled': True, 'scaleTop': 0.45, 'scaleBottom': 0.45,
         'points': [(500, 0), (600, 0), (600, 30), (500, 30)]},
    ],
}
