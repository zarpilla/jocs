#!/usr/bin/env python3
"""
L'Última Arrel — mostra d'art de la sala 2, `centraleta` (Escena 2). La composició ve de la referència 2.

Una cova entre les arrels del roure. A dalt, un forat per on entra l'última llum del capvespre, i un raig que baixa
fins a terra. Al fons, el pas cap a les galeries, amb l'escala de mà recolzada al replà. Les parets són d'arrels,
amb els fils del Miceli: apagats (blau fosc) abans de reparar-los i encesos (turquesa) després. A la dreta, el
tauler de la centraleta: rodes de fusta, clavilles de bolet, el radar d'arrels (la pantalla rodona), el rètol
«MICELI» i el corn per escoltar. Al costat del tauler, les tres arrels del trencaclosques 2.2: només una és viva.
L'Espora, al tauler, i la Iri, a l'esquerra.

Ús: python3 centraleta.py  →  centraleta.png (xarxa caiguda), centraleta-encesa.png (×2, amb personatges)
"""
import math
import random

from bosc import (W, H, Canvas, Light, nearest, fbm, hr, text, text_width, arrel, bolet, filament, falguera, ombra,
                  HAZE, BARK, MOSS, EARTH, PLANK, IRONK, STONE, FERN, TURQ, GLOW_T, CREAM, LEAF, HERE)
import nenes

HOLE = (196, 0)
LIGHT = Light(ambient=-0.1, vignette=(40, 1), floor_fade=None)
LIGHT.width = W                # (la vinyeta, a 640 i no als 480 per defecte de la llibreria)
LIGHT.point(200, 40, r=300, k=2.0, squash=0.9, power=1.4)                         # el forat
LIGHT.point(250, 240, r=170, k=0.8, squash=1.6, power=1.5)                        # on toca el raig, a terra
LIGHT.point(520, 96, r=190, k=1.4, squash=1.0, power=1.4)                         # el llum de bolet del tauler

CLAY = [(14, 8, 8), (26, 16, 12), (42, 26, 18), (62, 40, 26), (86, 56, 34), (112, 76, 44), (140, 98, 58),
        (170, 124, 76), (204, 158, 104), (236, 200, 146)]
COPPER = [(40, 16, 10), (80, 34, 18), (124, 58, 30), (168, 88, 46), (210, 126, 70), (240, 172, 110)]
SKINE = [(60, 30, 30), (110, 60, 52), (160, 100, 78), (204, 140, 108), (232, 180, 146), (248, 214, 186)]
BEARD = [(20, 26, 16), (40, 52, 30), (64, 80, 46), (92, 108, 66), (124, 138, 92), (160, 170, 126)]
SCREEN = [(4, 14, 8), (8, 30, 16), (14, 60, 30), (30, 110, 50), (80, 190, 90), (170, 250, 170)]

LAMPW = [(80, 50, 20), (150, 100, 40), (210, 160, 80), (245, 210, 140), (255, 240, 200), (255, 252, 236)]

FLOOR_Y = 196                  # on comença el terra de davant (el replà del fons és més amunt)


# ─── La cova ───────────────────────────────────────────────────────────────

def parets(cv):
    """El fons: terra i arrels que baixen, més fosc a les vores; el pas cap a les galeries, al mig."""
    for y in range(0, H):
        for x in range(W):
            # les arrels de les parets, en bandes que baixen i es torcen
            # cada arrel és un tub (llum al mig, fosc a les juntures), d'amples diferents
            ph = x / 18 + math.sin(y / 46 + x / 110) * 1.6 + (fbm(x / 60, y / 80, 3) - 0.5) * 2.4
            f = ph % 1.0
            tub = math.sin(f * math.pi) ** 0.7
            lvl = 2.2 + tub * 2.0 + (fbm(x / 3, y / 9, 8) - 0.5) * 1.0 + (hr(int(ph), 0, 2) - 0.5) * 0.8
            cv.put(x, y, CLAY, lvl, lit=1.0)
    # el pas cap a les galeries: un arc fosc al fons, més fosc com més endins
    cx, cy, rx, ry = 380, 120, 70, 76
    for y in range(cy - ry, 176):
        for x in range(cx - rx, cx + rx + 1):
            nx, ny = (x - cx) / rx, (y - cy) / ry
            d = nx * nx + (min(ny, 0)) ** 2
            if d <= 1:
                lvl = 0.6 + d * 2.0 + (fbm(x / 6, y / 10, 12) - 0.5) * 0.8
                cv.put(x, y, CLAY, lvl, lit=0.3)
    # el forat de dalt: llum
    for y in range(0, 44):
        for x in range(140, 260):
            nx, ny = (x - HOLE[0]) / 56, (y - 6) / 34
            d = nx * nx + ny * ny
            if d <= 1:
                cv.put(x, y, CREAMSKY, 5.6 - d * 3.0, lit=0)
            elif d <= 1.35:
                cv.put(x, y, CLAY, 7.4 - (d - 1) * 8, lit=0)                        # la vora, encesa
    cv.glow(HOLE[0], 8, 80, (255, 226, 170), 0.6)


CREAMSKY = [(120, 90, 70), (180, 140, 100), (220, 180, 130), (240, 210, 160), (250, 232, 196), (255, 246, 226)]


def replà(cv):
    """El replà del fons (més amunt) i el terra de davant, amb molsa; el graó entre tots dos."""
    for x in range(W):
        top = 150 + 8 * fbm(x / 40, 0, 4)
        for y in range(int(top), FLOOR_Y + 8):
            lvl = 3.6 + (fbm(x / 12, y / 4, 6) - 0.5) * 1.6
            mossy = fbm(x / 9, y / 4, 7) > 0.6
            cv.put(x, y, MOSS if mossy else EARTH, lvl + (0.2 if mossy else 0))
        # la cara del graó (vertical, a l'ombra)
        e = FLOOR_Y + 8 + 10 * fbm(x / 30, 3, 21)
        for y in range(FLOOR_Y + 8, int(e) + 6):
            cv.put(x, y, CLAY, 1.6 + (y - FLOOR_Y - 8) * 0.12 + (fbm(x / 4, y / 2, 9) - 0.5) * 1.2)
    for x in range(W):
      e = FLOOR_Y + 8 + 10 * fbm(x / 30, 3, 21)
      for y in range(int(e) + 6, H):
            t = (y - FLOOR_Y) / (H - FLOOR_Y)
            lvl = 3.2 + t * 0.6 + (fbm(x / (10 + 30 * t), y / (3 + 8 * t), 16) - 0.5) * 1.8
            mossy = fbm(x / 14, y / 6, 17) > 0.62
            cv.put(x, y, MOSS if mossy else EARTH, lvl + (0.1 if mossy else 0))


def raig(cv):
    """El raig de llum del forat fins a terra, amb pols que sura."""
    def k(x, y):
        if y > 250:
            return 0
        t = y / 250
        cx = 196 + t * 64
        hw = 40 + t * 36
        d = abs(x - cx) / hw
        return max(0.0, 1 - d) ** 1.5 * 0.22 * (1 - t * 0.4)
    cv.tint(120, 30, 340, 250, (255, 220, 160), k)
    rnd = random.Random(4)
    for _ in range(40):
        t = rnd.random()
        y = 40 + t * 200
        x = 196 + t * 64 + (rnd.random() - 0.5) * (60 + t * 60)
        cv.flat(x, y, (255, 236, 196))


def escala(cv):
    """L'escala de mà, recolzada al replà, que puja cap al forat."""
    x0, y0, x1, y1 = 300, 196, 330, 92
    for side in (0, 18):
        for i in range(140):
            t = i / 139
            x = x0 + side + (x1 - x0) * t
            y = y0 + (y1 - y0) * t
            for k in (0, 1):
                cv.put(x + k, y, PLANK, 3.6 - k * 1.0)
    for j in range(1, 7):
        t = j / 7
        y = y0 + (y1 - y0) * t
        x = x0 + (x1 - x0) * t
        cv.rect(x, y, x + 18, y + 1, PLANK, lambda xx, yy: 4.0 - (yy - y) * 1.4)


# ─── El tauler ─────────────────────────────────────────────────────────────

TX0, TY0, TX1, TY1 = 470, 110, 560, 198


def tauler(cv, encesa):
    # l'arrel gruixuda on és clavat, a la dreta
    for y in range(0, H):
        c = 600 + math.sin(y / 50) * 8
        w = 46 + max(0, y - 180) * 0.4
        for x in range(int(c - w), W):
            u = (x - c) / w
            lvl = 4.2 - u * 0.8 - max(0, -u) ** 6 * 1.6 + (fbm(u * 8, y / 30, 51) - 0.5) * 2.0
            cv.put(x, y, BARK, lvl, lit=0.8)
    # el tauler de fusta, una mica girat (la vora dreta, més a prop)
    for x in range(TX0, TX1 + 1):
        t = (x - TX0) / (TX1 - TX0)
        top, bot = TY0 + 4 - t * 6, TY1 + t * 4
        for y in range(int(top), int(bot) + 1):
            plank = (y - int(top)) % 11 == 0
            cv.put(x, y, PLANK, 3.8 - t * 0.6 - (1.4 if plank else 0) + (fbm(x / 2, y / 12, 3) - 0.5) * 0.8, lit=0.6)
        cv.put(x, top - 1, PLANK, 5.4, lit=0.4)
    for x in range(TX0 - 6, TX1 + 6):                                                # el taulell (una lleixa)
        t = (x - TX0) / (TX1 - TX0)
        y = TY1 - 30 + t * 2
        cv.put(x, y, PLANK, 5.4, lit=0.4)
        for k in range(1, 5):
            cv.put(x, y + k, PLANK, 2.6 - k * 0.3, lit=0.4)
    # les rodes de fusta i coure
    for x, y, r in ((482, 126, 6), (500, 124, 5), (484, 146, 4), (548, 120, 4), (552, 140, 5)):
        cv.disc(x, y, r, r, COPPER, lambda nx, ny: 3.4 - nx * 0.8 - ny * 1.2, lit=0.5)
        cv.disc(x, y, r * 0.4, r * 0.4, COPPER, lambda nx, ny: 1.6, lit=0.5)
        cv.line(x, y, x + r * 0.7, y - r * 0.7, IRONK, 3.0, lit=0)
    # el radar d'arrels: una pantalla rodona de mica
    rx, ry, rr = 522, 140, 14
    cv.disc(rx, ry, rr + 3, rr + 3, COPPER, lambda nx, ny: 3.0 - ny * 1.4, lit=0.5)
    if encesa:
        cv.disc(rx, ry, rr, rr, SCREEN, lambda nx, ny: 2.0 + (1.6 if abs(math.hypot(nx, ny) % 0.33) < 0.06 else 0)
                + (2.4 if abs(nx + ny * 0.4) < 0.08 and nx > 0 else 0), lit=0)
        for px, py in ((rx - 6, ry - 3), (rx + 4, ry + 6), (rx - 2, ry + 8)):
            cv.flat(px, py, (200, 255, 200))
        cv.glow(rx, ry, 30, (120, 240, 140), 0.3)
    else:
        cv.disc(rx, ry, rr, rr, SCREEN, lambda nx, ny: 0.6 - ny * 0.4 + (0.6 if nx < -0.3 and ny < -0.3 else 0), lit=0)
    # les clavilles: bolets petits clavats al taulell, amb cables
    for i, x in enumerate(range(478, 556, 9)):
        y = TY1 - 36 + (x - TX0) * 0.02
        cv.rect(x, y, x + 1, y + 4, CREAM, 3.0, lit=0.5)
        cv.disc(x + 0.5, y, 3, 1.8, TURQ if encesa and i % 3 != 1 else LEAF, (4.4 if encesa else 1.6), lit=0 if encesa else 0.6)
        if encesa and i % 3 != 1:
            cv.glow(x + 0.5, y, 6, GLOW_T, 0.3)
    # el llum: un bolet gros que penja d'una arrel, sobre el tauler
    cv.line(516, 60, 516, 84, BARK, 2.0, lit=0.3)
    bolet(cv, 516, 96, 4, 9, glow=0.0, cap=LAMPW, stem=CREAM)
    cv.disc(516, 93, 8, 3, LAMPW, 5.0, lit=0)
    cv.glow(516, 96, 46, (255, 210, 140), 0.45)
    # el rètol «MICELI», en un tros de fusta clavat a l'arrel
    sx, sy = 566, 150
    cv.rect(sx, sy, sx + 40, sy + 12, PLANK, lambda x, y: 4.4 - (y - sy) * 0.1, lit=0.6)
    cv.rect(sx, sy + 12, sx + 40, sy + 13, PLANK, 1.8, lit=0.6)
    text(cv, 'MICELI', sx + 20 - text_width('MICELI') // 2, sy + 4, (40, 24, 14))
    # el corn per escoltar, de fusta, que surt de l'arrel
    for i in range(30):
        t = i / 29
        x, y = 602 - t * 26, 96 + t * 10
        r = 2 + t * 6
        cv.disc(x, y, r * 0.5, r, PLANK, lambda nx, ny: 4.0 - ny * 1.4 - nx * 0.4, lit=0.6)
    cv.disc(576, 106, 3, 8, IRONK, lambda nx, ny: 0.6 + nx * 0.6, lit=0)
    # el fil de saba, que penja del tauler (fluix) o lligat a l'arrel viva (encès)
    if encesa:
        for i in range(60):
            t = i / 59
            x, y = 470 - t * 22, 170 + math.sin(t * math.pi) * 14 - t * 30
            cv.put(x, y, TURQ, 6.0, lit=0)
            cv.put(x, y + 1, TURQ, 4.0, lit=0)
        cv.glow(458, 166, 12, GLOW_T, 0.5)
    else:
        for i in range(40):
            t = i / 39
            x, y = 470 - t * 6, 170 + t * 30 + math.sin(t * 4) * 2
            cv.put(x, y, TURQ, 3.0, lit=0)


def arrels_trencaclosques(cv, encesa):
    """Tres arrels a la paret, a l'esquerra del tauler: només la del mig és viva."""
    for i, (x, seed) in enumerate(((432, 61), (448, 62), (462, 63))):
        viva = i == 1
        arrel(cv, (x, 60), (x - 6, 110), (x + 2, 196), 4, 3, base=3.2 if viva else 2.6, seed=seed, moss=False)
        if encesa and viva:
            for y in range(70, 196, 2):
                xx = x - 3 + math.sin(y / 20) * 2
                cv.put(xx, y, TURQ, 5.4, lit=0)
            cv.glow(x, 130, 26, GLOW_T, 0.3)


# ─── La xarxa a les parets ─────────────────────────────────────────────────

def fils(cv, encesa):
    starts = [(30, 200, -1.7, 160), (70, 196, -1.4, 150), (110, 198, -1.9, 130), (8, 150, -1.2, 110),
              (150, 190, -1.6, 90), (424, 160, -2.0, 120), (640, 200, -2.3, 140), (620, 120, -2.6, 100),
              (260, 160, -1.5, 70), (340, 150, -1.8, 60)]
    for i, (x, y, a, l) in enumerate(starts):
        filament(cv, x, y, a, l, 40 + i, glow=1.0 if encesa else 0, branch=3, k=5.0 if encesa else 3.0,
                 dim=not encesa)
    # bolets: uns quants de bioluminescents a les parets, i de marrons per terra
    for x, y, h, r in ((40, 168, 5, 6), (52, 172, 3, 4), (116, 178, 4, 5), (600, 196, 6, 7), (612, 190, 3, 4),
                       (420, 190, 4, 4)):
        bolet(cv, x, y, h, r, glow=1.0 if encesa else 0.15)
    for x, y, h, r in ((206, 252, 5, 6), (216, 256, 3, 4), (380, 270, 4, 5), (560, 262, 5, 6), (90, 230, 4, 5),
                       (100, 236, 3, 3)):
        bolet(cv, x, y, h, r, glow=0, cap=LEAF, stem=CREAM)


# ─── L'Espora ──────────────────────────────────────────────────────────────

def espora(cv, fx, fy):
    """Un gnom micòleg d'un pam i mig (≈36 px): bata de fulles seques, ulleres gruixudes, barba de molsa."""
    ombra(cv, fx + 3, fy + 1, 10, 2)
    # botes
    for bx in (fx - 4, fx + 2):
        cv.rect(bx, fy - 3, bx + 3, fy, IRONK, lambda x, y: 2.6 - (y - fy + 3) * 0.2, lit=0.6)
    # la bata de fulles seques (amb la vora de baix en dents de serra)
    for y in range(fy - 24, fy - 2):
        t = (y - (fy - 24)) / 22
        hw = 5 + t * 4
        for x in range(int(fx - hw), int(fx + hw) + 1):
            if y > fy - 5 and (x + y) % 3 == 0:
                continue
            leaf = (x // 3 + y // 3) % 2
            cv.put(x, y, LEAF, 2.6 + leaf * 0.8 - (x - fx) / hw * 0.8 + (hr(x, y, 3) - 0.5) * 0.8, lit=0.7)
    # el braç, cap al tauler (la mà sobre una clavilla)
    for i in range(10):
        cv.put(fx + 5 + i, fy - 18 - i * 0.4, LEAF, 2.4, lit=0.6)
        cv.put(fx + 5 + i, fy - 17 - i * 0.4, LEAF, 1.8, lit=0.6)
    cv.disc(fx + 15, fy - 22, 1.6, 1.6, SKINE, 3.4, lit=0.6)
    # el cap: gran, amb el nas rodó
    hx, hy = fx, fy - 30
    cv.disc(hx, hy, 6, 6.4, SKINE, lambda nx, ny: 3.4 - nx * 0.6 - ny * 0.8, lit=0.7)
    # la barba de molsa, que tapa el pit
    for y in range(int(hy), fy - 12):
        t = (y - hy) / (fy - 12 - hy)
        hw = 6.4 - t * 3.6
        for x in range(int(hx - hw), int(hx + hw) + 1):
            if y > hy + 2 or abs(x - hx) > 2:
                cv.put(x, y, BEARD, 3.0 - t * 0.8 + (hr(x, y, 9) - 0.5) * 1.4 - (x - hx) / 7 * 0.6, lit=0.7)
    # els cabells: un floc de molsa al cim i pels costats
    for x, y, r in ((hx - 2, hy - 6, 2.4), (hx + 1, hy - 7, 2), (hx - 6, hy - 1, 2), (hx + 6, hy - 1, 2)):
        cv.disc(x, y, r, r, BEARD, lambda nx, ny: 3.2 - ny, lit=0.7)
    cv.disc(hx + 1, hy + 2, 1.8, 1.6, SKINE, 4.2, lit=0.6)                          # el nas
    for gx in (hx - 3, hx + 3):                                                     # les ulleres, gruixudes
        cv.ring(gx, hy - 1, 2.2, IRONK, 1.6, lit=0, step=20)
        cv.disc(gx, hy - 1, 1.4, 1.4, [(140, 200, 210), (200, 240, 246), (240, 255, 255)], 1.0, lit=0)
        cv.flat(gx - 1, hy - 2, (255, 255, 255))
    cv.flat(hx, hy - 1, (20, 20, 22))


# ─── Primer pla ────────────────────────────────────────────────────────────

def primer_pla(cv):
    # arrels gruixudes que emmarquen per dalt i per les vores
    arrel(cv, (-20, 20), (60, 70), (40, 300), 22, 14, base=1.2, seed=81, moss=False)
    arrel(cv, (-10, -10), (180, 30), (300, -20), 18, 8, base=1.6, seed=82, moss=False)
    arrel(cv, (660, 300), (620, 250), (560, 300), 16, 12, base=1.8, seed=83, moss=True)
    for i, (x, y, a, l, s) in enumerate(((-4, 300, 1.1, 120, -1), (30, 300, 1.5, 90, 1), (90, 300, 1.8, 70, 1),
                                          (520, 300, 1.9, 90, 1), (600, 296, 2.3, 110, 1))):
        falguera(cv, x, y, a, l, side=s, lvl=1.4, rim=1, seed=20 + i)


# ─── Composició ────────────────────────────────────────────────────────────

IRI_PEUS = (262, 254)
ESPORA_PEUS = (494, 204)


def fons(encesa):
    cv = Canvas(W, H, light=LIGHT)
    parets(cv)
    replà(cv)
    escala(cv)
    fils(cv, encesa)
    arrels_trencaclosques(cv, encesa)
    tauler(cv, encesa)
    raig(cv)
    if encesa:                                                                      # la cova, tenyida de turquesa
        cv.tint(0, 0, W, H, (60, 200, 190), lambda x, y: 0.03 + 0.05 * max(0, 1 - abs(x - 500) / 200))
    return cv


def main():
    for nom, encesa in (('centraleta', False), ('centraleta-encesa', True)):
        cv = fons(encesa)
        espora(cv, *ESPORA_PEUS)
        ombra(cv, IRI_PEUS[0] + 4, IRI_PEUS[1] + 1, 14, 3)
        iri = nenes.nena(nenes.IRI, 'R', 'iri')
        cv.img.alpha_composite(iri, (IRI_PEUS[0] - 25, IRI_PEUS[1] - 83))
        cv.P = cv.img.load()
        primer_pla(cv)
        nearest(cv.img, (W * 2, H * 2)).save(HERE / f'{nom}.png')
        print(f'{nom}.png')


if __name__ == '__main__':
    main()
