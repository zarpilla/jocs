"""
Aigua Verne — `palau_galeria` (L): la galeria de les vint-i-tres piscines, al palau orbital del Magnat.

  - al fons, el finestral a l'espai entre columnes blanques: Terra-2 (la corba ocre del planeta, a baix) i un
    dels dipòsits orbitals de Verne (el cilindre blanc amb la gota blava);
  - les piscines buides en tres terrasses (10 + 7 + 5), de rajola turquesa, amb escales cromades, i al terra de
    la galeria la **piscina central** (la 23a), la gran, la que té la sala de control a sota;
  - a l'esquerra, la paret amb la porta del saló (blanca i or) i l'escala de marbre que puja a les terrasses;
  - a la dreta, l'**aquari** amb els trenta-tres peixos platejats i el rètol «LOT 12».

PROPS: `piscines_plenes` (cinemàtica final: aigua a totes). ANIMS: `peixos`, `estrelles`, `aigua` (el reflex de
l'aigua, per sobre de `piscines_plenes`).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from hd.pix import Canvas, Light, hr, mix
from hd640.rooms.palau_comu import (MARB, ORP, TURQ, CROM, NEGRE, gota, RH, _diff, lletres, lletres_c, espai,
                                    estrelles_frames, terra2, diposit, terra_marbre, columna, motllura, marc_or,
                                    vidre, piscina, escaleta, aigua_aquari, peixos, ombra, negre_barra, fbm)

PERSONA = 83
FLOOR_Y = 186                 # on el terra de la galeria toca la primera terrassa
WALL_TOP = 14
WIN_Y0, WIN_Y1 = 20, 80       # els vidres del finestral
BACK_Y = 84                   # on la terrassa de dalt toca la paret del fons
COLS = (112, 216, 424, 528)   # les columnes del finestral
PLANET = (322, 150, 104)      # Terra-2: centre i radi (només se'n veu la corba de dalt)
DEPOSIT = (478, 46, 0.5)

# les terrasses: (y de la plataforma, y on comença la paret del davant, y on acaba, x0, x1, piscines)
TIERS = ((BACK_Y, 99, 106, 118, 552, 10),
         (106, 127, 136, 118, 566, 7),
         (136, 170, FLOOR_Y, 118, 582, 5))
# la piscina central, enfonsada al terra de la galeria
CEN_TOP = (238, 402, 198)
CEN_BOT = (222, 418, 232)
CEN_DEPTH = 11
# l'aquari: el vidre (x0, y0, x1, y1), el capçal i el peu
AQ = (542, 96, 616, 186)
AQ_CAP = 86
AQ_FOOT = 214
DOOR = ((10, 132, 240), (52, 112, 202))      # la porta del saló, a la paret de l'esquerra: (x, y dalt, y baix)

_ST = {'aigua': False, 'fish_t': 0.0}

LIGHT = Light(ambient=0.35, vignette=(56, 14), floor_fade=(236, 40))
LIGHT.point(320, 10, r=420, k=1.0, squash=0.7, power=1.2)        # la claror del sostre
LIGHT.point(579, 140, r=90, k=0.6, power=1.8)                    # la llum blava de l'aquari


# ─── Sostre, paret del fons, finestral ──────────────────────────────────────

def sostre(cv):
    """Sostre de cassetons blancs amb filets d'or i llums encastats."""
    for y in range(0, WALL_TOP + 1):
        for x in range(640):
            cx = (x - 320) * (1 + (WALL_TOP - y) * 0.06)
            cell = int(cx // 46)
            inner = abs((cx % 46) - 23) < 18 and 2 < y < WALL_TOP - 3
            v = 4.6 + (0.9 if inner else 0) - (1.6 if (cx % 46) < 1.5 else 0)
            cv.put(x, y, MARB, v)
            if inner and abs((cx % 46) - 23) < 2.5 and y == 7 and cell % 2 == 0:
                cv.flat(x, y, (255, 248, 220))
    motllura(cv, 0, 639, WALL_TOP - 2, h=3)


def aranya(cv, x, y1=30):
    """Un llum d'aranya petit: una tija d'or, un anell i penjolls de vidre que brillen."""
    cv.vline(x, 0, y1 - 10, ORP, 4.0)
    cv.disc(x, y1 - 6, 16, 4, ORP, lambda nx, ny: 4.6 - ny * 1.4 - abs(nx) * 0.6)
    cv.disc(x, y1 - 7, 12, 2.4, ORP, 2.4)
    for k in range(-14, 15, 3):
        h = 6 + int(4 * math.cos(k / 14 * 1.4))
        yy = y1 - 6 + int(4 * math.sqrt(max(0.0, 1 - (k / 16) ** 2)))
        cv.vline(x + k, yy, yy + h, CROM, 5.6 if k % 2 else 4.2)
        cv.flat(x + k, yy + h, (255, 255, 240))
    cv.disc(x, y1 + 6, 3, 4, CROM, lambda nx, ny: 6.0 - nx - ny)
    cv.glow(x, y1, 26, (255, 246, 210), 0.3)


def finestral(cv):
    x0, x1 = 64, 576
    # la paret del fons (marbre) i, dins els marcs, l'espai
    cv.rect(x0, WALL_TOP + 1, x1, BACK_Y - 1, MARB, lambda x, y: 5.2 - (y - WALL_TOP) * 0.01)
    panes = []
    edges = (x0 + 6,) + COLS + (x1 - 6,)
    for a, b in zip(edges, edges[1:]):
        panes.append((a + 9, b - 9))
    bright = []
    for a, b in panes:
        bright += espai(cv, a, WIN_Y0, b, WIN_Y1, seed=3 + a)
    cx, cy, r = PLANET
    terra2(cv, cx, cy, r, mask=lambda x, y: any(a <= x <= b for a, b in panes) and WIN_Y0 <= y <= WIN_Y1)
    # el dipòsit, en un canvas a part i retallat als vidres
    dep = Canvas(transparent=True)
    diposit(dep, *DEPOSIT)
    D = dep.img.load()
    for y in range(WIN_Y0, WIN_Y1 + 1):
        for x in range(DEPOSIT[0] - 60, DEPOSIT[0] + 60):
            if D[x, y][3] and any(a <= x <= b for a, b in panes):
                cv.flat(x, y, D[x, y])
    for a, b in panes:
        vidre(cv, a, WIN_Y0, b, WIN_Y1, k=0.14, seed=a)
        marc_or(cv, a - 3, WIN_Y0 - 3, b + 3, WIN_Y1 + 3, t=3, lvl=4.2)
        # el travesser (un filet d'or) i els muntants prims
        cv.hline(a, b, WIN_Y0 + 20, ORP, 3.6)
        for mx in range(a + (b - a) // 3, b - 4, max(20, (b - a) // 3)):
            cv.vline(mx, WIN_Y0, WIN_Y1, ORP, 3.4)
    # les columnes del finestral
    for x in COLS:
        columna(cv, x, WALL_TOP + 1, BACK_Y - 1, r=6, base_h=8, cap_h=10)
    # pilastres als dos extrems
    for x in (x0 + 4, x1 - 4):
        columna(cv, x, WALL_TOP + 1, BACK_Y - 1, r=4, base_h=8, cap_h=10)
    for x in COLS[1:3]:
        aranya(cv, x, 34)
    return bright


# ─── Terrasses i piscines ───────────────────────────────────────────────────

def pools_tier(t):
    """Les piscines d'una terrassa: [(top, bot, depth)]."""
    py, ry0, ry1, x0, x1, n = TIERS[t]
    out = []
    gap = (6, 10, 14)[t]
    w = (x1 - x0 - 12 - gap * (n - 1)) / n
    ya, yb = py + (3, 4, 5)[t], ry0 - (3, 4, 6)[t]
    vx, vy = 320, 20                                                   # fuga: les vores del fons, més estretes
    k = (ya - vy) / (yb - vy)
    for i in range(n):
        a = x0 + 6 + i * (w + gap)
        b = a + w
        out.append(((round(vx + (a + 2 - vx) * k), round(vx + (b - 2 - vx) * k), ya), (round(a), round(b), yb),
                    (2, 3, 5)[t]))
    return out


def totes_piscines():
    return [p for t in range(3) for p in pools_tier(t)] + [(CEN_TOP, CEN_BOT, CEN_DEPTH)]


def terrasses(cv, plena=False):
    for t, (py, ry0, ry1, x0, x1, n) in enumerate(TIERS):
        # la plataforma (marbre vist de dalt)
        terra_marbre(cv, py, ry0 - 1, vp=(320, -40 - t * 30), base=6.4, tile=(30, 40, 52)[t], x0=x0, x1=x1, seed=7 + t)
        # la paret del davant de la terrassa: marbre, filet d'or a dalt i un sòcol
        cv.rect(x0, ry0, x1, ry1, MARB, lambda x, y: 4.6 - (y - ry0) * 0.12 + (fbm(x / 30, y / 10, 9 + t) - 0.5) * 0.5)
        motllura(cv, x0, x1, ry0, h=2, lvl=4.6)
        cv.hline(x0, x1, ry1, MARB, 2.6)
        for p in pools_tier(t):
            piscina(cv, p[0], p[1], p[2], plena=plena, lvl=4.2 + t * 0.2, tile=(4, 5, 6)[t], seed=p[0][0])
            if not plena and t >= 1:                                       # una escaleta cromada a cada piscina
                escaleta(cv, p[0][1] - (5, 9)[t - 1], p[0][2] - 1, (2, 4)[t - 1], s=(0.5, 0.7)[t - 1])
        # graons laterals de terrassa a terrassa (a la dreta)
        for k in range(3):
            cv.hline(x1 - 14 + k * 3, x1, ry0 + k * (ry1 - ry0) // 3, MARB, 6.6)


def escala_marbre(cv):
    """L'escala de marbre que puja de la galeria a la terrassa de dalt, amb barana cromada a cada banda."""
    x0, x1 = 66, 116
    cv.rect(64, BACK_Y, 118, FLOOR_Y + 2, MARB, lambda x, y: 3.6 + (fbm(x / 20, y / 20, 2) - 0.5) * 0.5)
    y = FLOOR_Y + 2
    steps = []
    k = 0
    while y > BACK_Y:
        h = max(2, int(2 + (y - BACK_Y) / 26))                           # els de baix, més alts
        steps.append((y - h, y))
        y -= h
        k += 1
    for i, (ya, yb) in enumerate(steps):
        f = (yb - BACK_Y) / (FLOOR_Y - BACK_Y)
        a = x0 + (1 - f) * 6
        b = x1 - (1 - f) * 2
        cv.rect(a, ya, b, yb, MARB, lambda x, yy: (7.6 if yy == ya else 5.4 - (yy - ya) * 0.4) - (x - a) * 0.006
                + (fbm(x / 16, yy / 6, 3) - 0.5) * 0.5)
        cv.hline(a, b, yb, MARB, 3.0)
    # les baranes: pals cromats i passamà
    for side, (xa, xb) in ((0, (x0 - 1, x0 + 6)), (1, (x1 + 1, x1 - 1))):
        cv.line(xa, FLOOR_Y - 14, xb, BACK_Y - 14, CROM, 6.0)
        cv.line(xa, FLOOR_Y - 13, xb, BACK_Y - 13, CROM, 3.2)
        for j in range(0, 9):
            t = j / 8
            px = round(xa + (xb - xa) * t)
            py = round(FLOOR_Y - 14 + (BACK_Y - FLOOR_Y) * t)
            cv.vline(px, py + 1, py + 14 - int(t * 4), CROM, 4.4)
        cv.disc(xa, FLOOR_Y - 14, 2, 2, ORP, lambda nx, ny: 5 - ny)        # pom d'or


def piscina_central(cv, plena=False):
    piscina(cv, CEN_TOP, CEN_BOT, CEN_DEPTH, plena=plena, lvl=4.4, tile=10, seed=23, vora=4)
    if not plena:
        # una gota de Verne de mosaic al fons, i les escales cromades
        gota(cv, 320, 220, 9, lit=1)
    for x in (CEN_TOP[0] + 14, CEN_TOP[1] - 22):
        escaleta(cv, x, CEN_TOP[2] - 2, 12 if not plena else 4, s=1.1)


# ─── Parets laterals i porta ────────────────────────────────────────────────

def paret_esq(cv):
    pts = [(0, 0), (64, WALL_TOP), (64, FLOOR_Y + 2), (0, 252)]
    cv.poly(pts, MARB, lambda x, y: 4.2 + x * 0.012 + (fbm(x / 20, y / 30, 31) - 0.5) * 0.6)
    # el sòcol d'or (la línia del terra) i la cornisa
    for k in range(3):
        cv.line(0, 252 - k * 6 - 6, 64, FLOOR_Y + 2 - k * 2 - 2, ORP if k == 0 else MARB, 4.0 + k)
    cv.line(0, 2, 64, WALL_TOP + 1, ORP, 4.4)
    cv.line(0, 3, 64, WALL_TOP + 2, ORP, 3.0)
    cv.vline(64, WALL_TOP, FLOOR_Y + 2, MARB, 2.4)
    # la porta del saló: dues fulles blanques, amb plafons i marc d'or (en perspectiva)
    (xa, ta, ba), (xb, tb, bb) = DOOR

    def top(x):
        return ta + (tb - ta) * (x - xa) / (xb - xa)

    def bot(x):
        return ba + (bb - ba) * (x - xa) / (xb - xa)
    # marc i frontó
    for x in range(xa - 5, xb + 4):
        f = (x - xa) / (xb - xa)
        for y in range(int(top(x)) - 14 + int(f * 3), int(bot(x)) + 1):
            if y < top(x) or x < xa or x >= xb:
                cv.put(x, y, ORP, 4.2 + (1.0 if x == xa - 5 or y == int(top(x)) - 14 + int(f * 3) else 0)
                       - (1.2 if y == int(top(x)) - 1 else 0))
    for x in range(xa, xb):
        f = (x - xa) / (xb - xa)
        t, b = top(x), bot(x)
        mid = xa + (xb - xa) * 0.52
        for y in range(int(t), int(b) + 1):
            fy = (y - t) / (b - t)
            leaf_x = (x - xa) if x < mid else (x - mid)
            lw = (mid - xa) if x < mid else (xb - mid)
            in_panel = 3 < leaf_x < lw - 3 and (0.06 < fy < 0.46 or 0.54 < fy < 0.94)
            v = 6.0 - f * 1.2 + (0.6 if in_panel else 0)
            if in_panel and (leaf_x < 4.5 or fy < 0.075 or 0.53 < fy < 0.545):
                v -= 1.4
            if abs(x - mid) < 1:
                v = 2.6
            cv.put(x, y, MARB, v)
            if in_panel and (abs(leaf_x - 3.5) < 0.6 or abs(leaf_x - (lw - 3.5)) < 0.6):
                cv.put(x, y, ORP, 4.0)
        # les manetes d'or
    for hx in (int(xa + (xb - xa) * 0.52) - 3, int(xa + (xb - xa) * 0.52) + 2):
        hy = int((top(hx) + bot(hx)) / 2) + 4
        cv.rect(hx, hy - 4, hx, hy + 4, ORP, 5.0)
    # rètol daurat damunt la porta
    lletres(cv, 'SALÓ', xa + 8, int(top(xa + 8)) - 10, (120, 82, 28))


def paret_dreta(cv):
    pts = [(640, 0), (576, WALL_TOP), (576, FLOOR_Y + 2), (640, 252)]
    cv.poly(pts, MARB, lambda x, y: 3.6 - (x - 576) * 0.01 + (fbm(x / 20, y / 30, 33) - 0.5) * 0.6)
    cv.line(640, 2, 576, WALL_TOP + 1, ORP, 4.0)
    cv.line(640, 3, 576, WALL_TOP + 2, ORP, 2.6)
    cv.line(640, 246, 576, FLOOR_Y, ORP, 3.6)
    cv.vline(576, WALL_TOP, FLOOR_Y + 2, MARB, 6.0)
    # un finestral estret a la paret de la dreta (en perspectiva), amb l'espai
    def top(x):
        return 30 - (x - 586) / 46 * 8

    def bot(x):
        return 150 + (x - 586) / 46 * 26
    espai(cv, 586, 20, 631, 178, seed=41, mask=lambda x, y: 586 <= x <= 631 and top(x) <= y < bot(x), dens=1.4)
    for x in range(583, 635):
        f = (x - 586) / 46
        for k in range(3):
            cv.put(x, int(top(x)) - 1 - k, ORP, 4.6 - k * 0.8)
            cv.put(x, int(bot(x)) + k, ORP, 3.4 - k * 0.6)
    for x, (a, b) in ((584, (top(584) - 3, bot(584) + 3)), (633, (top(633) - 3, bot(633) + 3))):
        for k in range(3):
            cv.vline(x + k - 1, int(a), int(b), ORP, 4.4 - k * 0.8)
    for y in range(int(top(608)), int(bot(608))):
        cv.put(608, y, ORP, 3.6)
    vidre(cv, 586, 22, 631, 176, k=0.12, seed=9)


# ─── L'aquari ───────────────────────────────────────────────────────────────

def vidre_aquari(cv):
    x0, y0, x1, y1 = AQ
    for y in range(y0 + 2, y1):
        for x in range(x0, x1 + 1):
            s = (x - x0) * 1.0 - (y - y0) * 0.35
            if 6 < s % 70 < 10 or 14 < s % 70 < 15:
                o = cv.get(x, y)
                cv.flat(x, y, mix(o, (230, 248, 255), 0.35))


def aquari(cv):
    x0, y0, x1, y1 = AQ
    ombra(cv, (x0 + x1) // 2 - 4, AQ_FOOT + 2, (x1 - x0) // 2 + 10, 5, 0.7)
    # el peu: marbre amb un plafó d'or i el rètol
    cv.rect(x0 - 4, y1 + 1, x1 + 4, AQ_FOOT, MARB, lambda x, y: 5.4 - (x - x0) * 0.02 - (1.2 if y == AQ_FOOT else 0))
    motllura(cv, x0 - 5, x1 + 5, y1 + 1, h=3)
    motllura(cv, x0 - 6, x1 + 6, AQ_FOOT - 3, h=3, lvl=3.8)
    px0, px1, py0, py1 = x0 + 10, x1 - 10, y1 + 7, y1 + 21
    cv.rect(px0, py0, px1, py1, ORP, lambda x, y: 4.8 - (y - py0) * 0.08)
    marc_or(cv, px0, py0, px1, py1, t=1, lvl=4.0)
    lletres_c(cv, 'LOT 12', (px0 + px1) // 2, py0 + 2, (70, 40, 14))
    lletres_c(cv, 'DARRERS', (px0 + px1) // 2, py0 + 8, (110, 72, 26))
    # el vidre i l'aigua amb els peixos
    aigua_aquari(cv, x0, y0, x1, y1, _ST['fish_t'])
    peixos(cv, x0, y0, x1, y1, _ST['fish_t'])
    vidre_aquari(cv)
    # els muntants d'or i el capçal
    for x in (x0 - 3, x1 + 1):
        cv.rect(x, AQ_CAP, x + 2, y1, ORP, lambda xx, yy: 4.6 + (1.0 if xx == x else -0.8 if xx == x + 2 else 0))
    cv.rect(x0 - 5, AQ_CAP, x1 + 5, y0 - 1, ORP, lambda x, y: 4.0 - (y - AQ_CAP) * 0.1)
    motllura(cv, x0 - 6, x1 + 6, AQ_CAP - 2, h=3, lvl=5.0)
    cv.glow((x0 + x1) // 2, (y0 + y1) // 2, 70, (120, 200, 255), 0.18)


# ─── Composició ─────────────────────────────────────────────────────────────

def bg(cv):
    sostre(cv)
    _ST['bright'] = finestral(cv)
    terrasses(cv)
    # el terra de la galeria: marbre blanc amb filets d'or, amb el reflex del finestral
    terra_marbre(cv, FLOOR_Y + 1, RH - 1, vp=(320, 30), base=6.0, tile=48,
                 refl=lambda x, y: -0.8 * max(0.0, 1 - (y - FLOOR_Y) / 26) if 120 < x < 520 else 0)
    paret_esq(cv)
    paret_dreta(cv)
    escala_marbre(cv)
    ombra(cv, 320, 236, 108, 5, 0.5)
    piscina_central(cv)
    aquari(cv)
    negre_barra(cv)


@functools.lru_cache(maxsize=None)
def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv.img


def piscines_plenes(cv):
    """Aigua a totes les piscines (la cinemàtica final)."""
    for t in range(3):
        for p in pools_tier(t):
            piscina(cv, p[0], p[1], p[2], plena=True, lvl=4.2, seed=p[0][0])
    piscina_central(cv, plena=True)
    _treu_aquari(cv)


def _treu_aquari(cv):
    """Les piscines de les terrasses passen per darrere l'aquari: esborra el que el tapa."""
    for y in range(AQ_CAP - 3, AQ_FOOT + 1):
        for x in range(AQ[0] - 7, AQ[2] + 8):
            cv.P[x, y] = (0, 0, 0, 0)


PROPS = {'piscines_plenes': piscines_plenes}


def _frames_peixos():
    return [_diff(f, _base()) for f in _aq_frames()]


def _aq_frames(n=24):
    out = []
    for i in range(n):
        _ST['fish_t'] = i / n
        try:
            cv = Canvas(light=LIGHT, img=_base().copy())
            aquari(cv)
        finally:
            _ST['fish_t'] = 0.0
        out.append(cv.img)
    return out


def _frames_estrelles():
    base = _base()
    _base_bright = []
    # les estrelles brillants que ha deixat el finestral (es recalculen pintant-lo en un llenç a part)
    tmp = Canvas(light=LIGHT)
    sostre(tmp)
    _base_bright = finestral(tmp)
    return estrelles_frames(base, _base_bright, n=10)


def _frames_aigua():
    """El reflex de l'aigua de les piscines plenes (va per sobre de `piscines_plenes`)."""
    frames = []
    for i in range(8):
        cv = Canvas(light=LIGHT, transparent=True)
        for t in range(3):
            for p in pools_tier(t):
                piscina(cv, p[0], p[1], p[2], plena=True, lvl=4.2, seed=p[0][0] + i * 0.8)
        piscina(cv, CEN_TOP, CEN_BOT, CEN_DEPTH, plena=True, lvl=4.4, tile=10, seed=23 + i * 0.8, vora=4)
        for x in (CEN_TOP[0] + 14, CEN_TOP[1] - 22):
            escaleta(cv, x, CEN_TOP[2] - 2, 4, s=1.1)
        _treu_aquari(cv)
        frames.append(cv.img)
    return frames


ANIMS = {'peixos': {'frames': _frames_peixos, 'frameDuration': 140},
         'estrelles': {'frames': _frames_estrelles, 'frameDuration': 300},
         'aigua': {'frames': _frames_aigua, 'frameDuration': 180}}


# ─── Geometria (640×360) ────────────────────────────────────────────────────

GEOMETRIA = {
    'things': {
        'porta_salo': {'rect': (6, 100, 56, 240), 'walk': (44, 236)},
        'finestral': {'rect': (70, 16, 570, 83), 'walk': (170, 214)},
        'piscines': {'rect': (118, 84, 582, 185), 'walk': (480, 206)},
        'escales': {'rect': (62, 84, 118, 190), 'walk': (96, 206)},
        'aquari': {'rect': (536, 84, 622, 214), 'walk': (560, 236)},
    },
    'spawns': {'iri': (130, 240), 'verne': (190, 214), 'dividend': (444, 214)},
    'walkable': [(4, 256), (26, 238), (66, 204), (66, 192), (222, 192), (208, 240), (432, 240), (418, 192),
                 (530, 192), (530, 220), (626, 220), (634, 256)],
}
