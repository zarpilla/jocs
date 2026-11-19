"""
La bodega de la Cantimplora PLANA, vista de cara (com era abans de passar-la a 3D): ara és la font de les textures de
cantimplora_bodega.py, que en projecta les parets, els mobles i els objectes en perspectiva.

La panxa de la nau cisterna: planxa oliva rovellada, quadernes amb franges de perill, un carril de grua al sostre
amb la politja i tres bombetes de filament. D'esquerra a dreta:
  - l'escala de mà que puja al pont per la boca del sostre;
  - un dels dipòsits rodons (buit), amb la portella oberta: a dins, la manta d'en Diu;
  - a terra, davant del dipòsit, l'espai de càrrega pintat de groc;
  - la rampa, al fons, oberta: fora hi ha el planeta on és la nau (decorats `llum_*`);
  - l'últim barril, blau i abonyegat, fermat amb cadenes a les argolles del terra i de la paret, amb el rètol de la
    Vet: «NO. PER SI DE CAS.» (prop `barril`: el fons només té les argolles);
  - el panell del motor (la sala de màquines), el quadre elèctric amb els fusibles i el calaix de la Vet, amb tots
    els calaixos mig oberts i coses que en sobresurten;
  - la cuineta: el fogó amb la cafetera, la lleixa, la nevera petita i el tauler de suro amb paperets;
  - el banc d'en Tomàs, amb la carmanyola.

PROPS: `barril` · decorats `llum_terra2`, `llum_aqua`, `llum_ferrum`, `llum_verdant` (la rampa oberta al planeta i
la claror que entra pel terra), `motor_obert` (el panell obert: el motor, l'injector), `sacs_carregats` (els tres
sacs de llavors a l'espai de càrrega) i `diu_carmanyola` (en Diu assegut damunt la carmanyola).
ANIMS: `vapor` (la cafetera), `bombeta` (la bombeta del mig, que fa pampallugues de tant en tant).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from hd.pix import Canvas, Light, W, H, hr, mix, GOLD, RUST, COPPER
from hd.rooms.comu import _diff, text, text_width
from hd.rooms.exterior import fbm
from hd.personatges import diu
from hd640.rooms.nau_comu import (OLIVE, SAFETY, STEELN, DECKP, LEATHER, TAPE, AMBER, GLASSD, REDK, GREENK, WBLUE,
                                  BLACKT, PAPERN, CORK, CLOTH, WOODB, INK, WARM, box, outline, rivet, vpipe, hpipe,
                                  hazard, stencil, plate_wall, deck, bulb, drop, vista, glass_reflex)

# A 1×: és la font de les textures de cantimplora_bodega.py, que és a 1×.
from hd.pix import Canvas  # noqa: E402,F811
from hd.pix import Canvas as Canvas1x  # noqa: E402,F401  (llenços auxiliars en píxels de sala: figures, textos)

FLOOR_Y = 200
BOTTOM = 259
LADDER = (10, 54)                       # els dos muntants de l'escala de mà
TANK = (118, 126, 50)                   # el dipòsit: centre i radi
HATCH = (118, 140, 15)                  # la portella oberta
RAMP = (186, 74, 306, FLOOR_Y)          # l'obertura de la rampa
RAMP_HOR = 150                          # l'horitzó de fora
BARREL = (342, 150, 214)                # el barril: centre x, dalt, base
MOTOR = (382, 112, 434, 196)            # el panell del motor
FUSE = (450, 90, 476, 132)              # el quadre elèctric
DRAWERS = (448, 146, 490, FLOOR_Y)      # el calaix de la Vet
COUNTER = (496, 158, 538, FLOOR_Y)      # el fogó
FRIDGE = (541, 136, 577, FLOOR_Y)       # la nevera
BOARD = (498, 64, 572, 116)             # el tauler de suro
BENCH = (584, 174, 640, FLOOR_Y)        # el banc d'en Tomàs
LUNCH = (586, 164, 606, 174)            # la carmanyola
CARGO = (58, 203, 178, 222)             # l'espai de càrrega (a terra)
LAMPS = ((132, 30), (346, 30), (548, 30))
POT = (516, 140)                        # la cafetera (el centre de la base)
DRUM = [(8, 14, 22), (14, 26, 40), (22, 40, 62), (32, 58, 86), (46, 78, 110), (66, 102, 134), (96, 132, 160),
        (140, 170, 190)]

_ANIM = {'vapor': None, 'bombeta': None}

LIGHT = Light(ambient=0.05, vignette=(70, 30), floor_fade=(232, 46))
for _x, _y in LAMPS:
    LIGHT.point(_x, _y + 4, r=210, k=1.9, squash=1.1, down=True, power=1.5)
LIGHT.point(246, 150, r=150, k=1.0, squash=1.2, power=1.4)          # la claror de fora, per la rampa
LIGHT.point(32, 10, r=60, k=0.6, power=1.8)                         # la llum del pont, per la boca de dalt


# ─── Parets, sostre i terra ─────────────────────────────────────────────────

_GLIF_GROS = {'V': ('10001', '10001', '01010', '01010', '00100')}


def stencil_gros(cv, s, cx, y, k, ramp, lvl, flat=None, worn=0.06, seed=5):
    """Rètol amb la font petita ampliada ×k (blocs de k×k), centrat a `cx`: en escorç, a 1×, la font petita no es
    llegeix. Amb `flat`, de color pla (tinta); si no, pintura d'estergit gastada (falten alguns blocs). → l'amplada."""
    tmp = []

    class _Cap:
        def put(self, px, py, *a, **kw):
            tmp.append((px, py))

        def flat(self, px, py, col):
            tmp.append((px, py))
    w, cx_ = 0, 0
    for ch in s:                                   # (la V de la font petita, ampliada, sembla una U: una de 5)
        if ch in _GLIF_GROS:
            g = _GLIF_GROS[ch]
            tmp.extend((cx_ + i, j) for j, row in enumerate(g) for i, b in enumerate(row) if b == '1')
            cx_ += len(g[0]) + 1
        else:
            cx_ += text(_Cap(), ch, cx_, 0, None, 0) + 1
    w = cx_ - 1
    x0 = cx - (w * k) // 2
    for px, py in tmp:
        if flat is None and hr(px, py, seed) <= worn:
            continue
        for dy in range(k):
            for dx in range(k):
                if flat is None:
                    cv.put(x0 + px * k + dx, y + py * k + dy, ramp, lvl)
                else:
                    cv.flat(x0 + px * k + dx, y + py * k + dy, flat)
    return w * k


def walls(cv):
    plate_wall(cv, 0, 0, W - 1, FLOOR_Y - 1, lvl=3.0, pw=64, ph=44, seed=21, rust=0.5)
    # quadernes (les costelles de la nau), amb el peu pintat de franges
    for x in (62, 178, 314, 442, 580):
        cv.rect(x - 3, 24, x + 3, FLOOR_Y - 1, OLIVE, lambda xx, yy: 4.6 - abs(xx - x) * 0.45)
        cv.vline(x - 4, 24, FLOOR_Y - 1, OLIVE, 1.0)
        cv.vline(x + 4, 24, FLOOR_Y - 1, OLIVE, 1.6)
        hazard(cv, x - 3, FLOOR_Y - 26, x + 3, FLOOR_Y - 2, lvl=3.0, step=4)
        for y in range(30, FLOOR_Y - 30, 9):
            rivet(cv, x - 1, y, OLIVE, 4.4)
    # el sòcol
    cv.rect(0, FLOOR_Y - 5, W - 1, FLOOR_Y - 1, OLIVE, 2.0)
    cv.hline(0, W - 1, FLOOR_Y - 5, OLIVE, 4.2)


def ceiling(cv):
    cv.rect(0, 0, W - 1, 23, OLIVE, lambda x, y: 1.6 + (fbm(x / 30, y / 6, 23) - 0.5) * 0.6)
    for x in range(0, W, 32):
        cv.vline(x, 0, 23, OLIVE, 0.6)
    # el tub gros i el carril de la grua (una biga en I)
    hpipe(cv, 0, W - 1, 5, 3, STEELN, 2.6, bands=tuple(range(90, W, 180)), band_ramp=SAFETY)
    cv.rect(0, 13, W - 1, 14, STEELN, 4.6)
    cv.rect(0, 15, W - 1, 20, STEELN, lambda x, y: 2.6 - (y - 15) * 0.2)
    cv.rect(0, 21, W - 1, 22, STEELN, 3.6)
    cv.hline(0, W - 1, 23, BLACKT, 0.8)
    for x in range(8, W, 24):
        rivet(cv, x, 17, STEELN, 3.0)
    # la politja, aturada damunt l'espai de càrrega, amb la cadena i el ganxo
    px = 128
    cv.rect(px - 6, 22, px + 6, 32, SAFETY, lambda x, y: 3.6 - (x - px) * 0.15)
    outline(cv, px - 7, 21, px + 7, 33, INK)
    for y in range(34, 64):
        cv.put(px + (1 if (y // 2) % 2 else 0), y, STEELN, 4.0 if y % 2 else 2.0)
        cv.put(px - 4, y - 6, STEELN, 3.0 if y % 2 else 1.6)
    for a in range(0, 230, 12):
        cv.put(px + 1 + math.cos(math.radians(a)) * 4, 68 + math.sin(math.radians(a)) * 4, STEELN, 4.0)
    cv.rect(px - 1, 62, px + 3, 64, STEELN, 3.4)


def floor(cv):
    deck(cv, 0, FLOOR_Y, W - 1, BOTTOM, lvl=2.8, seed=24)
    # l'espai de càrrega: un rectangle pintat de groc a terra (ratlles a trossos), amb el rètol
    x0, y0, x1, y1 = CARGO
    for y in range(y0, y1 + 1):
        t = (y - y0) / (y1 - y0)
        a, b = x0 - 4 * t, x1 + 4 * t
        for x in range(int(a), int(b) + 1):
            edge = y in (y0, y1) or x - a < 2 or b - x < 2
            if edge and (x // 6 + (y > y0 + 2)) % 2 == 0 and hr(x, y, 31) > 0.12:
                cv.put(x, y, [(60, 46, 10), (130, 100, 20), (190, 150, 30), (230, 196, 60)], 2.2 - (1 - t) * 0.6)
    w = text_width('CARREGA')
    for (px, py) in [(x0 + (x1 - x0 - w) // 2, y0 + 7)]:
        stencil(cv, 'CARREGA', px, py, [(60, 46, 10), (130, 100, 20), (190, 150, 30), (230, 196, 60)], 2.0,
                worn=0.1)
    # taques de greix
    for cx, cy, rx in ((420, 236, 14), (180, 248, 10), (560, 230, 9)):
        cv.darken(cx - rx, cy - 3, cx + rx, cy + 3,
                  lambda x, y: 0.5 if ((x - cx) / rx) ** 2 + ((y - cy) / 3.2) ** 2 <= 1 else 0)


# ─── L'escala de mà ─────────────────────────────────────────────────────────

def escala(cv):
    a, b = LADDER
    # la boca del sostre: un forat amb la llum del pont i la tapa oberta
    cv.rect(a - 4, 0, b + 4, 23, OLIVE, 0.6, lit=0)
    cv.rect(a - 1, 0, b + 1, 20, [(40, 26, 14), (90, 60, 30), (160, 110, 56), (220, 170, 100)],
            lambda x, y: 1.0 + (20 - y) / 20 * 1.6, lit=0)
    cv.glow((a + b) // 2, 8, 30, (255, 196, 110), 0.35)
    cv.rect(a - 6, 21, b + 6, 25, OLIVE, 3.6)
    hazard(cv, a - 6, 22, b + 6, 24, lvl=3.6, step=4)
    # els muntants (taronja de seguretat) i els graons
    for x in (a, b):
        cv.rect(x - 2, 20, x + 2, FLOOR_Y + 4, SAFETY, lambda xx, yy: 3.4 - (xx - x) * 0.5 - (0.6 if x == b else 0))
        cv.vline(x - 3, 20, FLOOR_Y + 4, [INK], 0, lit=0)
        cv.vline(x + 3, 20, FLOOR_Y + 4, [INK], 0, lit=0)
    for y in range(30, FLOOR_Y, 11):
        cv.rect(a + 3, y, b - 3, y + 2, STEELN, lambda xx, yy: 4.6 - (yy - y) * 1.0)
        cv.hline(a + 3, b - 3, y + 3, BLACKT, 0.6)
    for y in (60, 150):                                             # les grapes a la paret
        for x in (a, b):
            cv.rect(x - 1, y, x + 1, y + 3, STEELN, 2.0)
    cv.disc((a + b) // 2, FLOOR_Y + 5, 26, 3, BLACKT, 0.8)


# ─── El dipòsit ─────────────────────────────────────────────────────────────

def diposit(cv):
    cx, cy, r = TANK
    # el bressol (dues potes de planxa) i l'ombra
    cv.disc(cx, FLOOR_Y + 3, r + 4, 4, BLACKT, 0.8)
    for side in (-1, 1):
        sx = cx + side * 30
        cv.poly([(sx - 8, cy + r - 14), (sx + 8, cy + r - 14), (sx + 10, FLOOR_Y + 1), (sx - 10, FLOOR_Y + 1)],
                OLIVE, lambda x, y: 2.6 - side * 0.3)
        cv.hline(sx - 10, sx + 10, FLOOR_Y + 1, [INK], 0, lit=0)
    # el fons del dipòsit: un disc amb volum (cúpula), planxa clara amb una costura
    cv.disc(cx, cy, r + 2, r + 2, BLACKT, 0.6)
    cv.disc(cx, cy, r, r, OLIVE, lambda nx, ny: 4.4 - nx * 0.9 - ny * 1.2 - (nx * nx + ny * ny) * 0.8 +
            (fbm(nx * 3, ny * 3, 25) - 0.5) * 0.8)
    for a in range(0, 360, 2):
        x, y = cx + math.cos(math.radians(a)) * (r - 6), cy + math.sin(math.radians(a)) * (r - 6)
        cv.put(x, y, OLIVE, 2.2)
        if a % 12 == 0:
            rivet(cv, x - 1, y - 1, OLIVE, 4.0)
    for a in range(0, 360, 2):                                     # el cèrcol de fora
        x, y = cx + math.cos(math.radians(a)) * (r - 1), cy + math.sin(math.radians(a)) * (r - 1)
        cv.put(x, y, OLIVE, 5.4 if 180 < a < 300 else 2.0)
    # el número d'estergit i un guix: «BUIT»
    for j, row in enumerate(['111', '100', '111', '001', '111']):        # el 5, gros (×3)
        for i, bit in enumerate(row):
            if bit == '1':
                cv.rect(cx - 30 + i * 3, cy - 30 + j * 3, cx - 28 + i * 3, cy - 28 + j * 3, SAFETY, 3.6)
    text(cv, 'BUIT', cx + 14, cy - 22, None, 0, flat=(226, 222, 206))
    cv.hline(cx + 13, cx + 30, cy - 15, [(226, 222, 206)], 0, lit=0)
    # el regalim de rovell sota la portella
    for j in range(30):
        if hr(j, 26) > 0.3:
            cv.put(cx + 6 + (j > 14), cy + 18 + j, RUST, 2.4 - j * 0.04)
    # la portella oberta: el forat fosc, la manta d'en Diu i la tapa girada a l'esquerra
    hx, hy, hr_ = HATCH
    cv.disc(hx, hy, hr_ + 3, hr_ + 3, STEELN, lambda nx, ny: 3.8 - nx * 0.8 - ny * 0.8)
    for a in range(0, 360, 30):
        cv.flat(hx + math.cos(math.radians(a)) * (hr_ + 1.5), hy + math.sin(math.radians(a)) * (hr_ + 1.5),
                STEELN[7])
    cv.disc(hx, hy, hr_, hr_, BLACKT, lambda nx, ny: 0.6 + ny * 0.8, lit=0.3)
    for y in range(hy + 3, hy + hr_ + 1):                          # la manta de quadres, arrugada
        for x in range(hx - hr_, hx + hr_ + 1):
            if (x - hx) ** 2 + (y - hy) ** 2 <= (hr_ - 1) ** 2 and y > hy + 4 + 2 * math.sin((x - hx) / 3):
                red = ((x - hx) // 3 + (y - hy) // 3) % 2
                cv.put(x, y, [(40, 8, 8), (90, 20, 16), (150, 36, 26), (190, 70, 50)] if red else
                       [(40, 34, 26), (90, 80, 64), (150, 140, 116), (200, 190, 160)], 1.8 + (y - hy) * 0.06)
    # la tapa, oberta: una el·lipse prima vista de cantell, amb la frontissa
    for y in range(hy - hr_ - 2, hy + hr_ + 3):
        t = (y - hy) / (hr_ + 2)
        w = 5 * math.sqrt(max(0.0, 1 - t * t))
        for x in range(int(hx - hr_ - 8 - w), int(hx - hr_ - 8 + w) + 1):
            cv.put(x, y, STEELN, 4.4 - (x - (hx - hr_ - 8)) * 0.4)
    cv.rect(hx - hr_ - 6, hy - 3, hx - hr_ - 1, hy + 3, STEELN, 2.4)
    cv.rect(hx - hr_ - 12, hy - 2, hx - hr_ - 10, hy + 2, STEELN, 6.0)  # la maneta de la tapa


# ─── La rampa ───────────────────────────────────────────────────────────────

def rampa_fora(cv, planeta):
    """El que es veu per la rampa oberta: el planeta, el llindar i els braços hidràulics."""
    x0, y0, x1, y1 = RAMP
    vista(cv, planeta, (x0, y0, x1, y1 - 1), RAMP_HOR, s=1.25, seed=7, refl=False)
    # la rampa abaixada: el cantell de la planxa i les ratlles antilliscants, que baixen cap a fora
    for y in range(y1 - 10, y1):
        t = (y - (y1 - 10)) / 10
        for x in range(x0, x1 + 1):
            stripe = (x + y) % 8 < 2
            cv.put(x, y, STEELN, 3.0 + t * 1.6 + (1.0 if stripe else 0), lit=0.4)
    for x in range(x0, x1 + 1, 16):
        cv.vline(x, y1 - 10, y1 - 1, SAFETY, 3.4, lit=0.3)
    cv.hline(x0, x1, y1 - 11, BLACKT, 1.0, lit=0)
    # els dos braços hidràulics, que surten dels cantons de dalt cap a la rampa
    for side, xa in ((-1, x0 + 5), (1, x1 - 5)):
        xb = xa + side * -12
        cv.line(xa, y0 + 6, xb, y1 - 12, STEELN, 2.6, lit=0.3)                  # el cilindre
        cv.line(xa + 1, y0 + 6, xb + 1, y1 - 12, STEELN, 1.2, lit=0.3)
        cv.line(xa - 1, y0 + 6, xb - 1, y1 - 12, BLACKT, 0.0, lit=0)
        cv.line(xa, y0 + 6, xa + side * -4, y0 + 36, STEELN, 7.0, lit=0)       # la tija brillant del pistó
        cv.rect(xa - 2, y0 + 2, xa + 2, y0 + 7, STEELN, 3.2, lit=0.3)


def rampa(cv):
    x0, y0, x1, y1 = RAMP
    rampa_fora(cv, None)
    # el marc: planxa gruixuda, amb franges de perill als brancals i a la llinda
    cv.rect(x0 - 8, y0 - 10, x1 + 8, y0 - 1, OLIVE, 3.8)
    hazard(cv, x0 - 8, y0 - 8, x1 + 8, y0 - 3, lvl=3.6, step=6)
    for xa in (x0 - 8, x1 + 1):
        cv.rect(xa, y0, xa + 7, y1, OLIVE, lambda x, y: 4.0 - (x - xa) * 0.15)
        hazard(cv, xa + 2, y0 + 4, xa + 5, y1 - 4, lvl=3.4, step=5)
    outline(cv, x0 - 9, y0 - 11, x1 + 9, y1, INK)
    cv.hline(x0 - 1, x1 + 1, y0 - 1, [INK], 0, lit=0)
    cv.vline(x0 - 1, y0, y1, [INK], 0, lit=0)
    cv.vline(x1 + 1, y0, y1, [INK], 0, lit=0)
    # el llum de rampa oberta (una caixa amb un focus taronja) i el botó
    cv.rect(x1 + 12, y0 + 30, x1 + 22, y0 + 50, STEELN, 3.0)
    outline(cv, x1 + 11, y0 + 29, x1 + 23, y0 + 51, INK)
    cv.disc(x1 + 17, y0 + 36, 3, 3, REDK, 3.0, lit=0)
    cv.disc(x1 + 17, y0 + 45, 3, 3, GREENK, 4.0, lit=0)
    cv.glow(x1 + 17, y0 + 45, 7, (120, 255, 120), 0.4)
    stencil_gros(cv, 'RAMPA', (x0 + x1) // 2, y0 - 29, 3, PAPERN, 3.4)            # (gros: en escorç s'ha de llegir)


def llum(planeta, col):
    """Decorat: la rampa oberta al planeta i la claror de color que entra i s'escampa pel terra."""
    def fn(cv):
        base = _base_img()
        on = Canvas(light=LIGHT)
        on.img.paste(base)
        on.P = on.img.load()
        x0, y0, x1, y1 = RAMP
        rampa_fora(on, planeta)
        # la claror al terra: un trapezi que s'eixampla cap a davant, més fort a prop de la rampa
        on.tint(x0 - 60, FLOOR_Y + 1, x1 + 60, BOTTOM, col, lambda x, y: _shaft(x, y, x0, x1, 0.38))
        # i una mica als brancals
        on.tint(x0 - 9, y0 - 10, x1 + 9, y1, col,
                lambda x, y: 0.0 if x0 <= x <= x1 else 0.25 * max(0.0, 1 - min(abs(x - x0), abs(x - x1)) / 9))
        cv.img.alpha_composite(_diff(on.img, base))
    return fn


def _shaft(x, y, x0, x1, k):
    t = (y - FLOOR_Y) / (BOTTOM - FLOOR_Y)
    a, b = x0 - 40 * t, x1 + 40 * t
    if not a <= x <= b:
        return 0.0
    edge = min(x - a, b - x) / 10
    return k * min(1.0, edge) * (1 - t * 0.7)


# ─── L'últim barril ─────────────────────────────────────────────────────────

def argolles(cv):
    """Les argolles del terra i de la paret, on es fermen les cadenes (es queden quan el barril ja no hi és)."""
    cx, top, base = BARREL
    for x, y in ((cx - 30, 140), (cx + 30, 140)):
        cv.rect(x - 2, y - 2, x + 2, y + 2, STEELN, 3.0)
        cv.ring(x, y + 5, 3, STEELN, 4.6, step=20)
    for x, y in ((cx - 34, base + 1), (cx + 34, base + 1)):
        cv.disc(x, y, 4, 1.6, STEELN, 3.4)
        cv.ring(x, y - 2, 2.6, STEELN, 5.0, step=24)


def _chain(cv, xa, ya, xb, yb, lvl=4.0):
    """Una cadena de baules de 3 px, alternant de cara i de cantell, amb el contorn fosc."""
    L = math.hypot(xb - xa, yb - ya)
    n = int(L / 3)
    for i in range(n + 1):
        t = i / max(1, n)
        sag = math.sin(t * math.pi) * min(3.0, L / 20)
        x, y = round(xa + (xb - xa) * t), round(ya + (yb - ya) * t + sag)
        for dx, dy in ((-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)):
            if cv.get(x + dx, y + dy)[3] == 0 or True:
                pass
        if i % 2:
            cv.put(x, y - 1, STEELN, lvl + 1.6)
            cv.put(x, y, STEELN, lvl)
            cv.put(x, y + 1, STEELN, lvl - 1.4)
        else:
            cv.put(x - 1, y, STEELN, lvl + 1.0)
            cv.put(x + 1, y, STEELN, lvl - 0.8)
            cv.put(x, y - 1, STEELN, lvl + 1.4)
            cv.put(x, y + 1, STEELN, lvl - 1.6)
            cv.flat(x, y, BLACKT[0])


def barril(cv):
    cx, top, base = BARREL
    rx = 22
    # l'ombra al terra
    cv.darken(cx - rx - 8, base - 3, cx + rx + 10, base + 4,
              lambda x, y: 0.9 if ((x - cx - 2) / (rx + 7)) ** 2 + ((y - base) / 3.6) ** 2 <= 1 else 0)
    # el cos: blau (aigua), descolorit, amb cèrcols i bonys
    for y in range(top + 4, base + 1):
        for x in range(cx - rx, cx + rx + 1):
            u = (x - cx) / rx
            v = 3.8 - u * 1.5 - u * u * 1.6 + (fbm(x / 8, y / 10, 27) - 0.5) * 0.4
            if (y - top) in (14, 15, 44, 45):
                v += 1.2 if (y - top) % 2 == 0 else -1.4             # els cèrcols
            if y > base - 3:
                v -= 0.8
            cv.put(x, y, DRUM, v)
    for x in range(cx - rx, cx + rx + 1):                           # la vora de baix, corbada
        u = (x - cx) / rx
        yb = base + int(2.6 * math.sqrt(max(0.0, 1 - u * u)))
        for y in range(base, yb + 1):
            cv.put(x, y, DRUM, 1.4)
        cv.flat(x, yb + 1, INK)
    # bonys i rovell
    for bx, by in ((cx - 12, top + 30), (cx + 9, top + 22)):
        cv.disc(bx, by, 4, 3, DRUM, lambda nx, ny: 3.0 + nx * 0.8 + ny * 0.8)
    for k in range(14):
        rx_, ry_ = cx - rx + 2 + int(hr(k, 28) * (2 * rx - 4)), top + 6 + int(hr(k, 29) * (base - top - 10))
        cv.put(rx_, ry_, RUST, 2.6)
        if hr(k, 30) > 0.5:
            cv.put(rx_, ry_ + 1, RUST, 1.8)
    # la tapa: una el·lipse amb el tap
    cv.disc(cx, top + 4, rx, 4.6, DRUM, lambda nx, ny: 4.8 - ny * 0.8 - nx * 0.4)
    for a in range(0, 360, 4):
        cv.put(cx + math.cos(math.radians(a)) * rx, top + 4 + math.sin(math.radians(a)) * 4.6, DRUM,
               6.0 if a > 180 else 2.0)
    cv.disc(cx + 8, top + 3, 3, 1.4, STEELN, 3.6)
    cv.flat(cx + 8, top + 2, STEELN[8])
    for y in range(top + 4, base + 2):
        cv.flat(cx - rx - 1, y, INK)
        cv.flat(cx + rx + 1, y, INK)
    # les cadenes: dues en creu, de les argolles de la paret a les del terra, i una que l'abraça
    _chain(cv, cx - 30, 146, cx - rx + 4, top + 3, 4.2)              # de les argolles de la paret a la tapa
    _chain(cv, cx + 30, 146, cx + rx - 4, top + 3, 3.6)
    _chain(cv, cx - rx + 1, base - 8, cx - 34, base - 1, 4.2)         # dels costats a les argolles del terra
    _chain(cv, cx + rx - 1, base - 8, cx + 34, base - 1, 3.6)
    _chain(cv, cx - rx - 1, top + 20, cx + rx + 1, top + 20, 4.4)    # i una que l'abraça
    # el cadenat, de llautó
    cv.rect(cx - 3, top + 22, cx + 3, top + 28, GOLD, lambda x, y: 4.4 - (x - cx) * 0.3)
    cv.ring(cx, top + 21, 2.4, STEELN, 5.0, step=30)
    cv.flat(cx, top + 25, INK)
    # el rètol de la Vet: cartró penjat d'un cordill, «NO.» en vermell i «PER SI DE CAS.»
    sx0, sy0, sx1, sy1 = cx - 21, top + 30, cx + 19, base - 4
    cv.line(sx0 + 6, sy0, cx - 4, top + 20, [(120, 100, 70), (170, 150, 110)], 1.0)
    cv.line(sx1 - 6, sy0, cx + 4, top + 20, [(120, 100, 70), (170, 150, 110)], 1.0)
    cv.poly([(sx0, sy0 + 1), (sx1, sy0), (sx1 + 1, sy1), (sx0 + 1, sy1 + 1)], CLOTH,
            lambda x, y: 5.0 - (y - sy0) * 0.02 + (hr(x // 3, y // 2, 32) - 0.5) * 0.5)
    for y in range(sy0, sy1 + 2):
        cv.flat(sx0 + (1 if y > (sy0 + sy1) / 2 else 0) - 1, y, INK)
        cv.flat(sx1 + (1 if y > (sy0 + sy1) / 2 else 0) + 1, y, INK)
    cv.hline(sx0, sx1, sy0 - 1, [INK], 0, lit=0)
    cv.hline(sx0 + 1, sx1 + 1, sy1 + 2, [INK], 0, lit=0)
    red = (190, 30, 24)
    ink = (24, 24, 40)
    # «NO.», a doble mida, retolador vermell
    gx = sx0 + 6
    for ch in 'NO.':
        from hd.rooms.comu import _glyph
        g, _ = _glyph(ch)
        for j, row in enumerate(g):
            for i, bit in enumerate(row):
                if bit == '1':
                    cv.rect(gx + i * 2, sy0 + 3 + j * 2, gx + i * 2 + 1, sy0 + 4 + j * 2, [red], 0, lit=0)
        gx += len(g[0]) * 2 + 2
    for x in range(sx0 + 5, gx - 2):                                # el subratllat
        cv.flat(x, sy0 + 15 + (1 if x % 7 == 3 else 0), red)
    text(cv, 'PER SI', sx0 + 3, sy0 + 18, None, 0, flat=ink)
    text(cv, 'DE CAS.', sx0 + 6, sy0 + 25, None, 0, flat=ink)


# ─── El motor, els fusibles i el calaix de la Vet ───────────────────────────

def motor(cv):
    x0, y0, x1, y1 = MOTOR
    cv.rect(x0 - 3, y0 - 3, x1 + 3, y1 + 1, OLIVE, 2.0)
    outline(cv, x0 - 4, y0 - 4, x1 + 4, y1 + 2, INK)
    motor_tancat(cv)
    stencil_gros(cv, 'MOTOR', (x0 + x1) // 2, y0 - 21, 3, PAPERN, 3.4)


def motor_tancat(cv):
    x0, y0, x1, y1 = MOTOR
    box(cv, x0, y0, x1, y1, OLIVE, 3.8, grad=0.8)
    for y in range(y0 + 34, y1 - 10, 4):                            # les reixetes
        cv.hline(x0 + 8, x1 - 8, y, OLIVE, 1.0)
        cv.hline(x0 + 8, x1 - 8, y + 1, OLIVE, 5.0)
    # el triangle de perill
    tx, ty = (x0 + x1) // 2, y0 + 8
    for j in range(13):
        cv.hline(tx - j // 1.6, tx + j // 1.6, ty + j, SAFETY, 4.4 if j < 12 else 2.0)
    cv.vline(tx, ty + 4, ty + 8, [INK], 0, lit=0)
    cv.flat(tx, ty + 10, INK)
    for bx, by in ((x0 + 3, y0 + 3), (x1 - 4, y0 + 3), (x0 + 3, y1 - 4), (x1 - 4, y1 - 4)):
        rivet(cv, bx, by, OLIVE, 3.6)
    cv.rect(x0 + 3, (y0 + y1) // 2 - 6, x0 + 6, (y0 + y1) // 2 + 6, STEELN, 4.0)   # la maneta


def motor_obert(cv):
    """Decorat: el panell obert (la tapa girada a la dreta) i, a dins, el motor amb l'injector, que fa calor."""
    base = _base_img()
    on = Canvas(light=LIGHT)
    on.img.paste(base)
    on.P = on.img.load()
    x0, y0, x1, y1 = MOTOR
    # dins: fosc, amb la claror taronja del motor
    on.rect(x0, y0, x1, y1, BLACKT, lambda x, y: 0.6 + (y - y0) / (y1 - y0) * 0.6, lit=0)
    # els cilindres i les tapes de balancins
    for i, cxx in enumerate((x0 + 13, x0 + 26, x0 + 39)):
        on.rect(cxx - 5, y0 + 30, cxx + 5, y0 + 64, STEELN, lambda x, y: 3.6 - (x - cxx) * 0.25, lit=0.3)
        for y in range(y0 + 32, y0 + 64, 3):
            on.hline(cxx - 5, cxx + 5, y, STEELN, 1.6, lit=0.2)          # les aletes
        on.rect(cxx - 6, y0 + 24, cxx + 6, y0 + 30, REDK, 3.4, lit=0.3)
    # el col·lector, de coure, i els tubs
    on.rect(x0 + 4, y0 + 16, x1 - 4, y0 + 21, COPPER, lambda x, y: 4.0 - (y - y0 - 16) * 0.4, lit=0.3)
    for cxx in (x0 + 13, x0 + 26, x0 + 39):
        on.vline(cxx, y0 + 21, y0 + 24, COPPER, 3.0, lit=0.3)
    on.rect(x0 + 6, y0 + 68, x1 - 6, y1 - 6, STEELN, 2.2, lit=0.3)
    # l'injector, de llautó, al mig (el que cal canviar)
    on.rect(x0 + 24, y0 + 6, x0 + 28, y0 + 16, GOLD, lambda x, y: 4.6 - (x - x0 - 24) * 0.4, lit=0.3)
    on.rect(x0 + 22, y0 + 5, x0 + 30, y0 + 7, GOLD, 5.2, lit=0.3)
    # cables, i la calor
    for k, col in enumerate((REDK, (40, 40, 160), AMBER)):
        for y in range(y0 + 40, y1 - 8):
            ramp = col if isinstance(col, list) else [tuple(int(c * f) for c in col) for f in (0.3, 0.6, 1.0)]
            on.put(x1 - 6 - k * 2 + int(math.sin(y / 5 + k) * 1.5), y, ramp, 2.0, lit=0.2)
    on.glow((x0 + x1) // 2, y1 - 20, 30, (255, 120, 40), 0.35)
    # la tapa, oberta cap a fora (girada sobre la frontissa de la dreta): un trapezi estret, en perspectiva
    dw = 13
    door = [(x1 + 1, y0 - 1), (x1 + dw, y0 - 6), (x1 + dw, y1 + 6), (x1 + 1, y1 + 1)]
    on.poly(door, OLIVE, lambda x, y: 4.4 + (x - x1) * 0.08 - (1.4 if (y - y0) % 4 == 0 and y > y0 + 30 else 0))
    on.line(x1 + 1, y0 - 1, x1 + dw, y0 - 6, [INK], 0, lit=0)
    on.line(x1 + 1, y1 + 1, x1 + dw, y1 + 6, [INK], 0, lit=0)
    on.vline(x1 + dw + 1, y0 - 6, y1 + 6, [INK], 0, lit=0)
    on.vline(x1 + 1, y0, y1, OLIVE, 6.0)
    on.tint(x1 + 12, y0, x1 + 70, FLOOR_Y + 20, (255, 140, 60),
            lambda x, y: 0.12 * max(0.0, 1 - math.hypot(x - x1, y - y1 + 20) / 60))
    cv.img.alpha_composite(_diff(on.img, base))


def fusibles(cv):
    x0, y0, x1, y1 = FUSE
    # el tub dels cables, que puja al sostre
    vpipe(cv, x0 + 8, 24, y0 - 1, 2, STEELN, 3.0)
    vpipe(cv, x1 - 6, 24, y0 - 1, 1, BLACKT, 3.0)
    box(cv, x0, y0, x1, y1, STEELN, 3.2)
    outline(cv, x0 - 1, y0 - 1, x1 + 1, y1 + 1, INK)
    # la porta oberta, a l'esquerra, amb el llamp groc
    cv.poly([(x0 - 1, y0), (x0 - 9, y0 + 3), (x0 - 9, y1 - 3), (x0 - 1, y1)], STEELN, 4.2)
    for j, dx in enumerate((0, -1, -2, -1, 0, 1, 0, -1)):
        cv.flat(x0 - 5 + dx, y0 + 12 + j, (240, 200, 40))
    # dins: tres files de fusibles de porcellana, un que hi falta
    cv.rect(x0 + 2, y0 + 2, x1 - 2, y1 - 2, BLACKT, 1.6)
    for j in range(3):
        for i in range(3):
            fx, fy = x0 + 4 + i * 7, y0 + 5 + j * 12
            if (i, j) == (2, 1):
                cv.rect(fx + 1, fy + 2, fx + 3, fy + 7, BLACKT, 0.6)       # el que hi falta
                continue
            cv.rect(fx, fy, fx + 4, fy + 9, PAPERN, lambda x, y: 5.0 - (x - fx) * 0.4)
            cv.hline(fx, fx + 4, fy, GOLD, 4.4)
            cv.hline(fx, fx + 4, fy + 9, GOLD, 3.0)
    cv.flat(x1 - 3, y0 + 3, (255, 60, 40))


def calaix(cv):
    x0, y0, x1, y1 = DRAWERS
    box(cv, x0, y0, x1, y1 - 1, OLIVE, 4.2, grad=0.8)
    outline(cv, x0 - 1, y0 - 1, x1 + 1, y1, INK)
    # quatre calaixos, tots mig oberts, i el que en sobresurt
    things = ('corda', 'cables', 'mitjo', 'cinta')
    for k in range(4):
        dy0 = y0 + 4 + k * 12
        pull = 2 + (k % 2) * 2
        cv.rect(x0 + 2, dy0, x1 - 2, dy0 + 10, OLIVE, 3.6)
        cv.rect(x0 + 2 - pull, dy0 - 1, x1 - 2 + pull, dy0 + 9 - 1, OLIVE, 4.6 - k * 0.1)
        outline(cv, x0 + 1 - pull, dy0 - 2, x1 - 1 + pull, dy0 + 9, INK)
        cv.rect((x0 + x1) // 2 - 4, dy0 + 3, (x0 + x1) // 2 + 4, dy0 + 4, STEELN, 5.4)
        what = things[k]
        if what == 'corda':                                        # un cabdell de cordill que penja
            for j in range(10):
                cv.put(x0 + 8 + int(math.sin(j * 0.8) * 2), dy0 + 8 + j, CLOTH, 4.0)
            cv.disc(x0 + 10, dy0 - 3, 4, 2.4, CLOTH, 3.4)
        elif what == 'cables':                                     # cables de colors
            for c, col in enumerate(((200, 40, 30), (40, 80, 200), (230, 200, 40))):
                for j in range(7):
                    cv.flat(x1 - 12 + c * 3 + int(math.sin(j + c) * 1.4), dy0 + 8 + j, col)
        elif what == 'mitjo':                                      # un mitjó de llana
            cv.rect(x1 - 2, dy0 + 2, x1 + 6, dy0 + 5, [(60, 20, 20), (140, 50, 40), (200, 90, 70)], 1.6)
            cv.rect(x1 + 4, dy0 + 5, x1 + 7, dy0 + 10, [(60, 20, 20), (140, 50, 40), (200, 90, 70)], 1.4)
        else:                                                      # un rotlle de cinta i un tornavís
            cv.disc(x0 + 12, dy0 - 2, 4, 2, TAPE, 3.4)
            cv.disc(x0 + 12, dy0 - 2, 1.6, 1, BLACKT, 1.0)
            cv.line(x1 - 14, dy0 - 3, x1 - 4, dy0 - 6, [(200, 60, 30), (240, 120, 60)], 1.0)
            cv.line(x1 - 4, dy0 - 6, x1 + 2, dy0 - 8, STEELN, 6.0)
    # damunt: una caixa d'eines, una llauna i el paper enganxat amb cinta: «VET · NO TOCAR»
    cv.rect(x0 + 4, y0 - 9, x0 + 22, y0 - 1, REDK, lambda x, y: 3.6 - (y - y0 + 9) * 0.1)
    cv.rect(x0 + 10, y0 - 12, x0 + 16, y0 - 10, BLACKT, 2.4)
    outline(cv, x0 + 3, y0 - 10, x0 + 23, y0 - 1, INK)
    cv.rect(x1 - 12, y0 - 10, x1 - 4, y0 - 1, STEELN, lambda x, y: 4.6 - (x - x1 + 12) * 0.3)
    cv.rect(x0 + 6, y0 + 52, x0 + 6, y0 + 52, PAPERN, 5.0)
    # (el paper, gros, damunt els dos calaixos de baix: a 1×, en escorç, la font petita no es llegeix)
    w = (text_width('VET') + 2) * 3
    cx = (x0 + x1) // 2
    cv.rect(cx - w // 2 - 4, y1 - 26, cx + w // 2 + 4, y1 - 5, PAPERN, lambda x, y: 5.0 - (0.4 if (x + y) % 7 == 0 else 0))
    outline(cv, cx - w // 2 - 5, y1 - 27, cx + w // 2 + 5, y1 - 4, INK)
    cv.rect(cx - 4, y1 - 29, cx + 4, y1 - 25, TAPE, 4.0)                    # la cinta
    stencil_gros(cv, 'VET', cx, y1 - 23, 3, None, 0, flat=(30, 40, 120))


# ─── La cuineta ─────────────────────────────────────────────────────────────

def tauler(cv):
    x0, y0, x1, y1 = BOARD
    cv.rect(x0 - 3, y0 - 3, x1 + 3, y1 + 3, WOODB, lambda x, y: 4.4 - (y - y0) * 0.01)
    outline(cv, x0 - 4, y0 - 4, x1 + 4, y1 + 4, INK)
    cv.rect(x0, y0, x1, y1, CORK, lambda x, y: 2.6 + (hr(x, y, 33) - 0.5) * 1.2)
    # paperets (llistes, un horari, un dibuix d'en Tomàs, una foto), amb xinxetes de colors i cinta
    notes = ((x0 + 3, y0 + 3, 18, 22, PAPERN, 'MISSIONS'), (x0 + 24, y0 + 5, 14, 12, [(80, 70, 20), (170, 150, 50),
             (230, 214, 110), (250, 240, 170)], None), (x0 + 42, y0 + 2, 16, 20, PAPERN, None),
             (x0 + 24, y0 + 22, 16, 22, PAPERN, None), (x0 + 60, y0 + 6, 12, 15, [(40, 60, 70), (90, 120, 130),
             (150, 180, 186)], 'foto'), (x0 + 44, y0 + 27, 24, 20, [(60, 80, 60), (130, 170, 130), (190, 226, 180),
             (220, 246, 210)], None), (x0 + 4, y0 + 30, 16, 18, PAPERN, None))
    for k, (nx, ny, w, h, ramp, kind) in enumerate(notes):
        tilt = (hr(k, 34) - 0.5) * 0.12
        pts = [(nx, ny + tilt * w * 10), (nx + w, ny - tilt * w * 10 + 0), (nx + w + tilt * 10, ny + h),
               (nx + tilt * 10, ny + h)]
        cv.poly(pts, ramp, lambda x, y: (len(ramp) - 1.6) - (y - ny) * 0.02)
        if kind == 'foto':
            cv.rect(nx + 2, ny + 2, nx + w - 2, ny + h - 4, [(90, 110, 140), (140, 160, 180)], 0.8, lit=0)
            cv.rect(nx + 4, ny + 7, nx + w - 4, ny + 10, OLIVE, 6.0)
        else:
            for j in range(ny + 4, ny + h - 2, 3):                 # ratlletes d'escriptura
                L = int(w * (0.4 + hr(k, j, 35) * 0.5))
                for x in range(nx + 2, nx + 2 + L):
                    if hr(x, j, 36) > 0.25:
                        cv.flat(x, j, (60, 60, 90))
        pin = ((220, 40, 30), (40, 120, 220), (240, 200, 40), (40, 170, 70))[k % 4]
        cv.flat(nx + w // 2, ny + 1, pin)
        cv.flat(nx + w // 2 + 1, ny + 2, tuple(c // 2 for c in pin))
    cv.flat(x0 + 10, y0 + 6, INK)


def cuina(cv, steam=None):
    x0, y0, x1, y1 = COUNTER
    # la lleixa, amb tassons, el pot de sal i l'ampolla d'oli
    sy = 128
    cv.rect(x0 - 2, sy, FRIDGE[2] + 2, sy + 3, WOODB, lambda x, y: 4.6 - (y - sy) * 0.8)
    outline(cv, x0 - 3, sy - 1, FRIDGE[2] + 3, sy + 4, INK)
    for bx in (x0 + 4, FRIDGE[2] - 4):
        cv.line(bx, sy + 4, bx + 6, sy + 12, STEELN, 2.4)
    for k, mx in enumerate((x0 + 2, x0 + 10, x0 + 18)):            # tres tassons de colors, desaparellats
        ramp = (REDK, [(20, 40, 60), (40, 80, 120), (80, 130, 170), (140, 180, 210)], PAPERN)[k]
        cv.rect(mx, sy - 7, mx + 5, sy - 1, ramp, lambda x, y: 3.2 - (x - mx) * 0.2)
        cv.ring(mx + 7, sy - 4, 1.6, ramp, 2.4, step=40)
    ox = x0 + 30                                                    # l'oli: una ampolla groga
    cv.rect(ox, sy - 14, ox + 5, sy - 1, [(60, 40, 6), (140, 100, 14), (210, 170, 40), (240, 214, 110)],
            lambda x, y: 2.8 - (x - ox) * 0.25 - (0 if y > sy - 11 else 1.0))
    cv.rect(ox + 1, sy - 17, ox + 4, sy - 15, REDK, 3.0)
    text(cv, 'OLI', ox - 1, sy - 9, None, 0, flat=(60, 30, 10)) if False else None
    cv.rect(ox + 9, sy - 9, ox + 14, sy - 1, PAPERN, 4.0)          # la sal
    cv.rect(ox + 9, sy - 11, ox + 14, sy - 10, WBLUE, 3.0)
    # el moble: portes de fusta pintada, i el taulell d'alumini
    box(cv, x0, y0 + 4, x1, y1 - 1, OLIVE, 4.0, grad=0.6)
    outline(cv, x0 - 1, y0 + 3, x1 + 1, y1, INK)
    cv.vline((x0 + x1) // 2, y0 + 8, y1 - 4, OLIVE, 1.6)
    for hx in ((x0 + x1) // 2 - 4, (x0 + x1) // 2 + 3):
        cv.rect(hx, y0 + 16, hx + 1, y0 + 22, STEELN, 5.0)
    cv.rect(x0 - 2, y0, x1 + 2, y0 + 3, STEELN, lambda x, y: 5.6 - (y - y0) * 0.8)
    # el fogó: dos focs, un d'encès (blau) sota la cafetera
    cv.rect(x0 + 2, y0 - 3, x1 - 2, y0, BLACKT, 2.2)
    for fx in (x0 + 10, x0 + 30):
        cv.disc(fx, y0 - 3, 7, 1.6, BLACKT, 3.4)
    for i in range(-5, 6, 2):
        cv.flat(POT[0] + i, y0 - 4, (80, 140, 255))
    cv.glow(POT[0], y0 - 4, 7, (90, 150, 255), 0.4)
    # la cafetera italiana: cos de vuit cares, cintura, broc i mànec negre
    px, py = POT
    for y in range(py, y0 - 4):
        t = (y - py) / (y0 - 4 - py)
        w = 5 if t > 0.5 else 4 + t * 2
        if abs(t - 0.5) < 0.08:
            w = 3.6
        for x in range(int(px - w), int(px + w) + 1):
            u = (x - px) / w
            cv.put(x, y, STEELN, 6.4 - u * 2.0 - (1.4 if abs(u) > 0.8 else 0) + (0.8 if abs(u + 0.4) < 0.2 else 0))
    cv.rect(px - 3, py - 2, px + 3, py, STEELN, 6.0)               # la tapa
    cv.flat(px, py - 3, BLACKT[2])
    cv.line(px + 5, py + 2, px + 8, py - 1, STEELN, 5.0)           # el broc
    cv.rect(px - 9, py + 2, px - 6, py + 9, BLACKT, 2.0)           # el mànec
    cv.hline(px - 8, px - 5, py + 2, BLACKT, 2.4)
    for y in range(py - 1, y0 - 4):
        cv.flat(px - 6 + (0 if y < py + 10 else 1), y, INK) if False else None
    # el vapor (animació): petites volutes que pugen del broc
    if steam is not None:
        for k in range(4):
            ph = (steam + k * 3) % 12
            yy = py - 3 - ph * 2
            xx = px + 9 + int(math.sin((ph + k) * 0.8) * 2) + ph // 4
            a = 1 - ph / 12
            if a > 0.15:
                cv.flat(xx, yy, mix(cv.get(xx, yy), (230, 230, 226), 0.7 * a))
                cv.flat(xx + 1, yy - 1, mix(cv.get(xx + 1, yy - 1), (230, 230, 226), 0.5 * a))


def nevera(cv):
    x0, y0, x1, y1 = FRIDGE
    cream = [(60, 54, 44), (110, 102, 84), (160, 152, 128), (196, 188, 162), (222, 216, 192), (240, 236, 216)]
    for y in range(y0, y1):
        for x in range(x0, x1 + 1):
            dx = max(x0 + 4 - x, 0, x - (x1 - 4))
            dy = max(y0 + 4 - y, 0)
            if dx * dx + dy * dy > 16:
                continue
            u = (x - x0) / (x1 - x0)
            cv.put(x, y, cream, 3.8 - u * 1.4 - (y - y0) * 0.008)
    for y in range(y0 + 4, y1):
        cv.flat(x0 - 1, y, INK)
        cv.flat(x1 + 1, y, INK)
    cv.hline(x0 + 3, x1 - 3, y0 - 1, [INK], 0, lit=0)
    cv.hline(x0, x1, y0 + 18, cream, 1.6)                          # el congelador
    cv.rect(x1 - 6, y0 + 22, x1 - 4, y0 + 40, STEELN, lambda x, y: 6.4 - (x - x1 + 6) * 1.0)   # la maneta
    cv.rect(x1 - 6, y0 + 8, x1 - 4, y0 + 14, STEELN, 6.0)
    cv.rect(x0 + 2, y1 - 6, x1 - 2, y1 - 1, BLACKT, 2.0)           # la reixeta de baix
    for x in range(x0 + 3, x1 - 2, 2):
        cv.flat(x, y1 - 4, BLACKT[4])
    # un imant amb la gota de Verne (de propaganda) i un paper: «LLET»
    drop(cv, x0 + 8, y0 + 30, 2, WBLUE, 3.4, lit=1)
    cv.rect(x0 + 5, y0 + 40, x0 + 22, y0 + 50, PAPERN, 5.0)
    text(cv, 'LLET', x0 + 6, y0 + 42, None, 0, flat=(160, 30, 30))
    cv.flat(x0 + 13, y0 + 39, (240, 200, 40))
    cv.disc(x0 + 12, y0 + 60, 3, 2, cream, 2.4)                    # un bony


def granota(cv):
    """El penja-robes de la paret, damunt el banc."""
    x0, y0, x1, y1 = BENCH
    # el penja-robes: la granota de recanvi d'en Tomàs (taronja, massa gran) i el seu mocador vermell
    hx = x0 + 28
    cv.rect(hx - 1, 96, hx + 1, 99, STEELN, 4.0)
    cv.line(hx, 99, hx - 10, 106, STEELN, 3.0)
    cv.line(hx, 99, hx + 10, 106, STEELN, 3.0)
    body = [(hx - 10, 106), (hx + 10, 106), (hx + 9, 150), (hx + 1, 150), (hx, 128), (hx - 1, 150), (hx - 9, 150)]
    cv.poly(body, SAFETY, lambda x, y: 3.2 - (x - hx) * 0.06 - (y - 106) * 0.008)
    for side in (-1, 1):                                           # les mànigues, penjant
        cv.poly([(hx + side * 10, 106), (hx + side * 13, 109), (hx + side * 13, 140), (hx + side * 10, 140)],
                SAFETY, 2.4)
        cv.vline(hx + side * 10, 110, 140, SAFETY, 1.2)
    cv.vline(hx, 108, 127, BLACKT, 2.0)                            # la cremallera
    cv.rect(hx - 6, 116, hx - 2, 120, SAFETY, 1.8)                 # la butxaca
    for y in range(106, 151):
        for x in range(hx - 15, hx + 16):
            if cv.get(x, y)[:3] in [tuple(c) for c in SAFETY] and cv.get(x - 1, y)[:3] not in \
                    [tuple(c) for c in SAFETY]:
                cv.flat(x - 1, y, INK)
    cv.poly([(hx - 5, 104), (hx + 5, 104), (hx + 2, 112), (hx - 2, 112)], REDK, 3.4)    # el mocador
    cv.line(hx + 2, 110, hx + 4, 118, REDK, 2.6)


def banc(cv):
    granota(cv)
    banc_sol(cv)


def banc_sol(cv):
    x0, y0, x1, y1 = BENCH
    # el banc: un tauló sobre dues potes
    cv.rect(x0, y0, x1, y0 + 4, WOODB, lambda x, y: 4.6 - (y - y0) * 0.6 + (hr(x // 6, 37) - 0.5) * 0.6)
    outline(cv, x0 - 1, y0 - 1, x1 + 1, y0 + 5, INK)
    for lx in (x0 + 4, x1 - 8):
        cv.rect(lx, y0 + 5, lx + 3, y1, WOODB, 2.8)
        cv.vline(lx + 4, y0 + 5, y1, [INK], 0, lit=0)
    cv.disc((x0 + x1) // 2, y1 + 3, 30, 2.5, BLACKT, 0.6)
    # la carmanyola: una capsa de llauna vermella, amb nansa i abonyegada
    lx0, ly0, lx1, ly1 = LUNCH
    cv.rect(lx0, ly0, lx1, ly1, REDK, lambda x, y: 3.8 - (x - lx0) * 0.06 - (y - ly0) * 0.1)
    cv.hline(lx0, lx1, ly0 + 3, REDK, 2.0)
    cv.hline(lx0, lx1, ly0, REDK, 5.0)
    outline(cv, lx0 - 1, ly0 - 1, lx1 + 1, ly1 + 1, INK)
    for x in range(lx0 + 6, lx1 - 5):
        cv.put(x, ly0 - 4 + (0 if lx0 + 8 <= x <= lx1 - 8 else 1), STEELN, 5.0)
    cv.rect(lx0 + 9, ly0 + 4, lx0 + 12, ly0 + 6, STEELN, 6.0)      # el tancament
    cv.flat(lx1 - 3, ly0 + 7, REDK[1])                             # un bony
    # un drap i una clau anglesa gran, al costat
    cv.rect(x0 + 26, y0 - 2, x0 + 36, y0 - 1, CLOTH, 3.0)
    cv.line(x1 - 14, y0 - 1, x1 - 2, y0 - 3, STEELN, 5.2)
    cv.disc(x1 - 2, y0 - 3, 2, 1.4, STEELN, 4.0)


def diu_carmanyola(cv):
    """Decorat: en Diu, assegut damunt la carmanyola d'en Tomàs."""
    gat = diu()
    lx0, ly0, lx1, ly1 = LUNCH
    cv.blit(gat, ((lx0 + lx1) // 2 - 13, ly0 - 25))


def sacs_carregats(cv):
    """Decorat: els tres sacs de llavors del pare, de tela, lligats i amb l'etiqueta escrita a mà."""
    x0, y0, x1, y1 = CARGO
    for k, (sx, base) in enumerate(((76, 217), (108, 219), (142, 216))):
        h, w = 30 + (k % 2) * 3, 14
        top = base - h
        cv.darken(sx - w - 2, base - 2, sx + w + 6, base + 3,
                  lambda x, y: 0.8 if ((x - sx - 2) / (w + 4)) ** 2 + ((y - base) / 2.8) ** 2 <= 1 else 0)
        for y in range(top, base + 1):
            t = (y - top) / h
            hw = w * (0.55 + 0.45 * math.sin(min(1.0, t * 1.3 + 0.15) * math.pi * 0.62)) if t > 0.18 else \
                4 + t * 10
            for x in range(int(sx - hw), int(sx + hw) + 1):
                u = (x - sx) / max(1, hw)
                v = 4.2 - u * 1.4 - u * u * 1.0 - (0.6 if (x + y) % 3 == 0 else 0)   # la trama de la tela
                cv.put(x, y, CLOTH, v)
            cv.flat(int(sx - hw) - 1, y, INK)
            cv.flat(int(sx + hw) + 1, y, INK)
        cv.hline(sx - 4, sx + 4, top - 1, [INK], 0, lit=0)
        cv.rect(sx - 5, top + 5, sx + 5, top + 6, [(80, 40, 20), (140, 80, 40)], 1.0)   # el cordill
        for x in range(sx - 4, sx + 5):                                                 # les orelles de dalt
            if (x - sx) % 3 == 0:
                cv.put(x, top - 2, CLOTH, 4.4)
        # l'etiqueta de paper amb lletra del pare
        cv.rect(sx - 6, top + 14, sx + 5, top + 21, PAPERN, 5.0)
        for j in (top + 16, top + 19):
            for x in range(sx - 5, sx + 4):
                if hr(x, j, k) > 0.3:
                    cv.flat(x, j, (60, 50, 90))


# ─── Composició ─────────────────────────────────────────────────────────────

def bg(cv):
    walls(cv)
    ceiling(cv)
    floor(cv)
    escala(cv)
    rampa(cv)
    diposit(cv)
    argolles(cv)
    motor(cv)
    fusibles(cv)
    calaix(cv)
    tauler(cv)
    cuina(cv, _ANIM['vapor'])
    nevera(cv)
    banc(cv)
    for i, (lx, ly) in enumerate(LAMPS):
        flicker = _ANIM['bombeta']
        on = not (i == 1 and flicker is not None and flicker in (5, 7))
        bulb(cv, lx, ly, cable=10, on=on)
        if not on:
            cv.darken(lx - 50, ly, lx + 50, ly + 70, lambda x, y: 0.25 * max(0.0, 1 - math.hypot(x - lx, y - ly) / 60))
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)


@functools.lru_cache(maxsize=None)
def _base_img():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv.img.copy()


def _frames(key, n):
    out = []
    for f in range(n):
        _ANIM[key] = f
        try:
            cv = Canvas(light=LIGHT)
            bg(cv)
        finally:
            _ANIM[key] = None
        out.append(_diff(cv.img, _base_img()))
    return out


PROPS = {
    'barril': barril,
    'llum_terra2': llum('terra2', (236, 200, 140)),
    'llum_aqua': llum('aqua', (220, 236, 250)),
    'llum_ferrum': llum('ferrum', (240, 140, 70)),
    'llum_verdant': llum('verdant', (190, 250, 170)),
    'motor_obert': motor_obert,
    'sacs_carregats': sacs_carregats,
    'diu_carmanyola': diu_carmanyola,
}

ANIMS = {
    'vapor': {'frames': lambda: _frames('vapor', 12), 'frameDuration': 140},
    'bombeta': {'frames': lambda: _frames('bombeta', 24), 'frameDuration': 160},
}


def _t(x0, y0, x1, y1, wx=None, wy=236):
    return {'rect': (x0, y0, x1, y1), 'walk': (wx if wx is not None else (x0 + x1) // 2, wy)}


GEOMETRIA = {
    'things': {
        'escala': _t(4, 0, 60, FLOOR_Y + 4, wx=34, wy=232),
        'diposit': _t(TANK[0] - TANK[2] - 2, TANK[1] - TANK[2] - 2, TANK[0] + TANK[2] + 2, FLOOR_Y, wy=232),
        'carrega': _t(CARGO[0] - 4, CARGO[1], CARGO[2] + 4, CARGO[3] + 2, wx=118, wy=238),
        'rampa': _t(RAMP[0], RAMP[1], RAMP[2], RAMP[3], wx=246, wy=230),
        'barril': _t(BARREL[0] - 24, BARREL[1] - 2, BARREL[0] + 24, BARREL[2] + 4, wy=234),
        'motor': _t(MOTOR[0] - 4, MOTOR[1] - 14, MOTOR[2] + 4, MOTOR[3] + 2, wx=408, wy=232),
        'fusibles': _t(FUSE[0] - 10, FUSE[1] - 1, FUSE[2] + 1, FUSE[3] + 1, wx=463, wy=232),
        'calaix': _t(DRAWERS[0] - 4, DRAWERS[1] - 12, DRAWERS[2] + 7, DRAWERS[3], wx=469, wy=232),
        'tauler': _t(BOARD[0] - 4, BOARD[1] - 4, BOARD[2] + 4, BOARD[3] + 4, wx=535, wy=232),
        'cafetera': _t(POT[0] - 10, POT[1] - 6, POT[0] + 12, COUNTER[1] - 2, wx=516, wy=232),
        'nevera': _t(FRIDGE[0] - 1, FRIDGE[1], FRIDGE[2] + 1, FRIDGE[3], wx=559, wy=232),
        'carmanyola': _t(LUNCH[0] - 2, LUNCH[1] - 6, LUNCH[2] + 2, LUNCH[3] + 2, wx=596, wy=234),
    },
    'spawns': {'tomas': (592, 246), 'diu': (HATCH[0], HATCH[1] + 14), 'iri': (250, 244), 'vet': (418, 250)},
    'walkable': [(8, 226), (632, 226), (636, 257), (4, 257)],
}
