"""
La casa del pare PLA, vista de cara (com era abans de passar-la a 3D): ara és la font de les textures de
granja_casa.py, que en projecta les parets, la llar de foc, la pica, els pots, la porta, el videotelèfon, el finestró
i la taula en perspectiva.

Una masia: parets de calç, el sostre de bigues, terra de rajola de terra cuita. D'esquerra a dreta: el foc a terra
(apagat) sota la campana; la pica de pedra i les tres lleixes de pots buits; la porta del pati; el videotelèfon, el
calendari i la marca del quadre de la mare; la taula del despatx; el finestró amb els porticons tancats.
Els decorats (`quadre`, `caixa_forta`, `caixa_oberta`, `quadre_apartat`) també es dibuixen aquí, plans.
"""
import math

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from PIL import Image

from hd.pix import Canvas, Light, W, H, hr, mix, B4
from hd.rooms.exterior import fbm, smooth
from hd640.rooms.terra2_comu import (
    RH, LIME, TERRA, PLANK, GREYW, STONE, BLACKT, IRONR, RUSTT, GLASSJ, CLOTH, PAPER, STRAW, WHITEP, BLUE, REDT,
    SHUT, WARN, ADOBE, text, text_width, outline, shadow, motes_frames, _diff)

# A 1×: és la font de les textures de granja_casa.py, que és a 1×.
from hd.pix import Canvas as Canvas1x  # noqa: E402,F401  (llenços auxiliars en píxels de sala: figures, textos)

FLOOR_Y = 206                     # on la paret toca a terra
CEIL_Y = 14                       # on la paret toca al sostre
VP = (320, 112)                   # el punt de fuga
DOOR = (292, 81, 352, FLOOR_Y)    # la porta del pati
WIN = (572, 50, 624, 128)         # el finestró del despatx
DESK = (430, 167, 562, 220)       # la taula del despatx (x0, dalt de la part de darrere, x1, peus del davant)
PIC = (464, 74, 512, 134)         # el quadre de la mare
SAFE = (474, 88, 502, 120)        # la caixa forta (a la paret, darrere el quadre)
HEARTH = (20, 144)                # la campana del foc a terra (x0, x1 de baix)
MANTEL_Y = 96
SINK = (156, 232)
SUN = (255, 214, 150)

BRASSY = [(40, 28, 10), (80, 58, 20), (130, 98, 36), (180, 142, 60), (220, 186, 96), (246, 222, 150)]
CREAM = [(60, 54, 44), (100, 92, 76), (142, 132, 110), (180, 170, 146), (210, 202, 178), (232, 226, 204)]
CRT = [(10, 16, 14), (18, 30, 26), (30, 48, 40), (50, 72, 60), (80, 104, 88)]
CHECK = [(40, 16, 18), (80, 30, 30), (130, 54, 46), (176, 90, 74), (214, 140, 120), (236, 196, 180)]
SAFEG = [(14, 18, 20), (26, 32, 34), (42, 50, 52), (62, 72, 72), (88, 98, 96), (118, 128, 124), (156, 164, 158)]
GILT = [(40, 26, 10), (78, 54, 20), (124, 92, 36), (170, 132, 56), (210, 174, 90), (240, 214, 140)]
SOOT = [(8, 6, 6), (16, 12, 12), (26, 20, 18), (38, 30, 26), (52, 42, 36)]
ASH = [(40, 38, 36), (70, 66, 62), (102, 98, 92), (136, 132, 124), (170, 166, 156)]
TILEB = [(30, 50, 80), (50, 84, 130), (90, 130, 180), (170, 196, 220), (226, 232, 236)]

LIGHT = Light(ambient=-0.2, vignette=(90, 30), floor_fade=(246, 30))
LIGHT.point(560, 150, r=260, k=1.6, squash=0.9, power=1.5)                # el sol del finestró, al despatx
LIGHT.point(322, 150, r=170, k=0.9, squash=0.8, power=1.6)                # la llum de les juntes de la porta
LIGHT.point(84, 170, r=120, k=0.5, power=1.8)                             # el sol que baixa per la xemeneia
LIGHT.add(lambda x, y: 0.6 * max(0.0, 1 - abs(x - 320) / 420))            # el centre, una mica més clar


def beam(x, y):
    """El raig de sol del finestró (0..1): de l'escletxa dels finestrons cap avall a l'esquerra, fins a terra."""
    # l'escletxa és a x≈598, y 56..122; el raig baixa amb pendent (cap a l'esquerra)
    if y < 56 or y > 252:
        return 0.0
    dy = y - 56
    cx = 598 - dy * 0.55
    hw = 4 + dy * 0.16
    d = abs(x - cx + (y - 89) * 0.0)
    top = y - 56
    if y < 122:
        hw = 3 + (y - 56) * 0.05 + dy * 0.12
    v = 1 - smooth(hw * 0.6, hw, d)
    return v * max(0.0, 1 - max(0, y - 238) / 14)


# ─── Sostre, paret, terra ───────────────────────────────────────────────────

def ceiling(cv):
    for y in range(0, CEIL_Y + 1):
        for x in range(W):
            cv.put(x, y, PLANK, 1.2 + (fbm(x / 9, y / 3, 3) - 0.5) * 0.8 - (0.6 if x % 23 == 0 else 0))
    for bx in range(-200, 860, 64):                                         # les bigues, cap al punt de fuga
        for y in range(0, CEIL_Y + 1):
            k = (VP[1] - y) / (VP[1] - CEIL_Y)
            x = VP[0] + (bx - VP[0]) * k
            w = 6 * k
            for xx in range(int(x - w / 2), int(x + w / 2) + 1):
                cv.put(xx, y, PLANK, 2.6 + (xx - x) / max(1, w) * 1.4 + (0.8 if y == CEIL_Y else 0))
    for x in range(W):                                                       # la jàssera, contra la paret
        cv.put(x, CEIL_Y + 1, PLANK, 3.4)
        cv.put(x, CEIL_Y + 2, PLANK, 1.0)


def wall(cv):
    def lvl(x, y):
        v = 3.6 + (fbm(x / 30, y / 22, 5) - 0.5) * 1.2 + (fbm(x / 6, y / 6, 9) - 0.5) * 0.5
        v -= 0.8 * smooth(0.6, 0.75, fbm(x / 18, y / 40, 17)) * (y / FLOOR_Y)   # les taques d'humitat (de fa anys)
        return v
    cv.rect(0, CEIL_Y + 3, W - 1, FLOOR_Y, LIME, lvl)
    # el sòcol pintat d'ocre, a baix
    cv.rect(0, FLOOR_Y - 22, W - 1, FLOOR_Y, ADOBE, lambda x, y: 3.0 + (fbm(x / 20, y / 8, 4) - 0.5) * 0.8)
    cv.rect(0, FLOOR_Y - 23, W - 1, FLOOR_Y - 23, ADOBE, 1.8)
    # el sostre fa ombra a dalt de la paret
    cv.darken(0, CEIL_Y + 3, W - 1, CEIL_Y + 8, lambda x, y: 0.7 - (y - CEIL_Y - 3) * 0.14)


def floor(cv):
    rows = [FLOOR_Y, 211, 217, 224, 232, 241, 251, 262]
    for y in range(FLOOR_Y + 1, RH):
        r = max(i for i, ry in enumerate(rows) if ry <= y)
        for x in range(W):
            k = (y - VP[1]) / (FLOOR_Y - VP[1])
            u = (x - VP[0]) / k                                              # x a la paret del fons
            col = math.floor(u / 26)
            fu = (u / 26) % 1
            joint = y in rows or fu < 0.06 / k * 2 or fu > 1 - 0.03
            lvl = 3.0 + (hr(col, r, 3) - 0.5) * 1.0 + (fbm(x / 18, y / 6, 21) - 0.5) * 0.6
            if (col + r) % 7 == 0:
                lvl -= 0.5                                                   # alguna rajola més fosca
            if hr(col, r, 9) > 0.92 and abs(fu - 0.5) < 0.05:
                lvl -= 1.4                                                   # una rajola esquerdada
            cv.put(x, y, TERRA, lvl - (1.8 if joint else 0))
    # la paret fa una mica d'ombra a terra
    cv.darken(0, FLOOR_Y + 1, W - 1, FLOOR_Y + 3, 0.45)


# ─── La cuina ───────────────────────────────────────────────────────────────

def hearth_boca(cv, x0, x1):
    """El fons de la boca del foc (per a la llar de foc en volum de granja_casa.py): la pedra negra de sutge, la
    cremallera amb l'olla i la cendra amb els tions i unes brases que encara fan caliu, entre x0 i x1."""
    def soot(x, y):
        row = y // 6
        joint = y % 6 == 0 or (x + (row % 2) * 5) % 11 == 0
        v = 2.0 + (hr(x // 11, row) - 0.5) * 1.2 + (y - MANTEL_Y) * 0.014 - (1.2 if joint else 0)
        v -= 1.0 * smooth(0.45, 0.7, fbm(x / 14, y / 20, 44))
        return v
    cv.rect(x0, MANTEL_Y - 20, x1, FLOOR_Y, STONE, soot)
    cv.darken(x0, MANTEL_Y - 20, x1, FLOOR_Y, lambda x, y: 0.7 * max(0.0, 1 - (y - MANTEL_Y + 20) / 90))
    cx = (x0 + x1) // 2
    for y in range(MANTEL_Y - 20, 160, 3):
        cv.put(cx, y, IRONR, 2.8)
        cv.put(cx + 1, y + 1, IRONR, 1.8)
    cv.disc(cx, 170, 13, 11, BLACKT, lambda nx, ny: 1.6 + nx * 0.8 - ny * 0.4)
    cv.rect(cx - 14, 160, cx + 14, 162, BLACKT, 2.8)
    cv.line(cx - 12, 160, cx, 152, IRONR, 2.6)
    cv.line(cx, 152, cx + 12, 160, IRONR, 2.6)
    # la claror de les brases, a baix, sobre la pedra i la panxa de l'olla
    cv.glow(cx, FLOOR_Y - 4, 30, (255, 120, 40), 0.35)


def hearth_lleixa(cv, x0, x1):
    """El que hi ha damunt la lleixa de la campana (dret, per fer-ne un sprite): plats, el llum d'oli, una ampolla.
    La base de tot és a y = MANTEL_Y − 4."""
    for px_, r in ((x0 + 20, 8), (x0 + 38, 7), (x1 - 34, 7)):
        cv.disc(px_, MANTEL_Y - 4 - r, r, r, CREAM, lambda nx, ny: 3.8 + nx * 0.6)
        cv.ring(px_, MANTEL_Y - 4 - r, r - 2, TILEB, 2.0, step=12)
        cv.disc(px_, MANTEL_Y - 4 - r, 2, 2, TILEB, 2.4)
    cv.rect(x0 + 60, MANTEL_Y - 12, x0 + 66, MANTEL_Y - 5, BRASSY, lambda x, y: 3.4 + (x - x0 - 60) * 0.2)
    cv.line(x0 + 66, MANTEL_Y - 11, x0 + 70, MANTEL_Y - 13, BRASSY, 4.0)
    cv.rect(x1 - 20, MANTEL_Y - 16, x1 - 16, MANTEL_Y - 5, GLASSJ, 2.6)


def hearth(cv):
    """El foc a terra, apagat, sota la campana."""
    x0, x1 = HEARTH
    # el fons del foc: pedra negra de sutge
    def soot(x, y):
        row = y // 6
        joint = y % 6 == 0 or (x + (row % 2) * 5) % 11 == 0
        v = 2.2 + (hr(x // 11, row) - 0.5) * 1.2 + (y - MANTEL_Y) * 0.014 - (1.2 if joint else 0)
        v -= 1.0 * smooth(0.45, 0.7, fbm(x / 14, y / 20, 44))               # el sutge, a clapes
        return v
    cv.rect(x0 + 4, MANTEL_Y + 6, x1 - 4, FLOOR_Y, STONE, soot)
    cv.darken(x0 + 4, MANTEL_Y + 3, x1 - 4, FLOOR_Y, lambda x, y: 0.55 * max(0.0, 1 - (y - MANTEL_Y) / 70))
    # els muntants de pedra
    for sx in (x0, x1 - 6):
        cv.rect(sx, MANTEL_Y + 2, sx + 6, FLOOR_Y, STONE, lambda x, y: 3.6 + (x - sx) * 0.15 - (1.4 if y % 9 == 0 else 0))
    # la campana: trapezi de calç, ennegrit a baix
    top_l, top_r = 46, 118
    cv.poly([(top_l, CEIL_Y + 3), (top_r, CEIL_Y + 3), (x1 + 4, MANTEL_Y - 4), (x0 - 4, MANTEL_Y - 4)], LIME,
            lambda x, y: 4.0 + (x - 82) * 0.008 + (fbm(x / 10, y / 10, 30) - 0.5) * 0.8 - 1.6 * smooth(50, 92, y) *
            (0.4 + 0.6 * fbm(x / 8, y / 30, 31)))
    cv.line(top_l, CEIL_Y + 3, x0 - 4, MANTEL_Y - 4, LIME, 2.2)
    cv.line(top_r, CEIL_Y + 3, x1 + 4, MANTEL_Y - 4, LIME, 5.0)
    # la lleixa de fusta de la campana, amb plats i un llum d'oli
    cv.rect(x0 - 8, MANTEL_Y - 4, x1 + 8, MANTEL_Y + 1, PLANK, lambda x, y: 3.4 - (y - MANTEL_Y + 4) * 0.4)
    cv.rect(x0 - 8, MANTEL_Y + 2, x1 + 8, MANTEL_Y + 2, BLACKT, 1.0)
    for px_, r in ((40, 8), (58, 7), (110, 7)):                              # plats drets, de ceràmica
        cv.disc(px_, MANTEL_Y - 4 - r, r, r, CREAM, lambda nx, ny: 3.8 + nx * 0.6)
        cv.ring(px_, MANTEL_Y - 4 - r, r - 2, TILEB, 2.0, step=12)
        cv.disc(px_, MANTEL_Y - 4 - r, 2, 2, TILEB, 2.4)
    cv.rect(80, MANTEL_Y - 12, 86, MANTEL_Y - 5, BRASSY, lambda x, y: 3.4 + (x - 80) * 0.2)   # el llum d'oli
    cv.line(86, MANTEL_Y - 11, 90, MANTEL_Y - 13, BRASSY, 4.0)
    cv.rect(124, MANTEL_Y - 16, 128, MANTEL_Y - 5, GLASSJ, 2.6)              # una ampolla
    # la cremallera i l'olla, penjada al mig
    cx = (x0 + x1) // 2
    for y in range(MANTEL_Y + 4, 160, 3):
        cv.put(cx, y, IRONR, 2.8)
        cv.put(cx + 1, y + 1, IRONR, 1.8)
    cv.disc(cx, 170, 13, 11, BLACKT, lambda nx, ny: 1.6 + nx * 0.8 - ny * 0.4)
    cv.rect(cx - 14, 160, cx + 14, 162, BLACKT, 2.8)
    cv.line(cx - 12, 160, cx, 152, IRONR, 2.6)
    cv.line(cx, 152, cx + 12, 160, IRONR, 2.6)
    # la cendra, els tions cremats i els capfoguers
    cv.disc(cx, FLOOR_Y - 1, 40, 6, ASH, lambda nx, ny: 2.4 - ny * 1.0 + (hr(int(nx * 20), int(ny * 6)) - 0.5) * 1.2)
    cv.line(cx - 26, FLOOR_Y - 4, cx + 10, FLOOR_Y - 8, SOOT, 3.2)
    cv.line(cx - 26, FLOOR_Y - 3, cx + 10, FLOOR_Y - 7, SOOT, 2.2)
    cv.line(cx - 6, FLOOR_Y - 9, cx + 28, FLOOR_Y - 4, SOOT, 3.6)
    cv.line(cx - 6, FLOOR_Y - 8, cx + 28, FLOOR_Y - 3, SOOT, 2.4)
    cv.put(cx + 28, FLOOR_Y - 4, ASH, 3.6)
    for fx in (cx - 30, cx + 26):
        cv.rect(fx, FLOOR_Y - 18, fx + 2, FLOOR_Y, IRONR, 2.6)
        cv.disc(fx + 1, FLOOR_Y - 19, 2, 2, IRONR, 3.4)
    # el sol que baixa per la xemeneia: una mica de llum damunt la cendra
    cv.tint(cx - 30, MANTEL_Y + 8, cx + 30, FLOOR_Y, SUN, lambda x, y: 0.12 * max(0.0, 1 - abs(x - cx) / 30) * (y - MANTEL_Y) / 110)


def sink(cv):
    """La pica de pedra, seca, amb l'aixeta, la cortineta de quadres i el sabó sec."""
    x0, x1 = SINK
    top = 158
    # les rajoles de València, darrere la pica
    for y in range(top - 32, top):
        for x in range(x0 + 2, x1 - 1):
            tx, ty = (x - x0 - 2) // 8, (y - top + 32) // 8
            if (x - x0 - 2) % 8 == 0 or (y - top + 32) % 8 == 0:
                cv.put(x, y, LIME, 2.6)
            else:
                lx, ly = (x - x0 - 2) % 8, (y - top + 32) % 8
                star = (lx in (3, 4) and ly in (2, 5)) or (ly in (3, 4) and lx in (2, 5)) or (lx in (3, 4) and ly in (3, 4))
                cv.put(x, y, TILEB, 2.0 if star else 4.0 + (0.4 if (tx + ty) % 2 else 0))
    # el marbre de la pica (la pedra) i la pica
    cv.rect(x0, top, x1, top + 6, STONE, lambda x, y: 5.0 - (y - top) * 0.3 + (0.6 if y == top else 0))
    cv.rect(x0 + 20, top + 1, x1 - 20, top + 4, STONE, lambda x, y: 2.0 + (y - top) * 0.3)   # el clot de la pica
    cv.rect(x0, top + 7, x1, top + 7, BLACKT, 1.4)
    # la cortineta de quadres, a sota
    cv.rect(x0 + 2, top + 8, x1 - 2, FLOOR_Y, CHECK, lambda x, y: 2.8 + (1.0 if ((x // 4) + (y // 4)) % 2 else 0) -
            (0.8 if (x - x0) % 10 in (0, 1) else 0) + (x - x0) * 0.004)
    cv.rect(x0 + 2, top + 8, x1 - 2, top + 9, CHECK, 1.6)
    # l'aixeta, de llautó, i el sabó sec
    ax = (x0 + x1) // 2
    cv.rect(ax - 1, top - 24, ax + 1, top - 10, BRASSY, lambda x, y: 3.4 + (x - ax) * 0.6)
    cv.rect(ax - 1, top - 12, ax + 8, top - 10, BRASSY, 3.6)
    cv.rect(ax + 7, top - 10, ax + 8, top - 7, BRASSY, 3.0)
    cv.rect(ax - 4, top - 25, ax + 4, top - 24, BRASSY, 4.4)
    cv.put(ax + 7, top - 6, BRASSY, 1.6)
    cv.rect(x0 + 6, top - 4, x0 + 13, top - 1, CREAM, 3.0)                   # el sabó, esquerdat
    cv.put(x0 + 9, top - 3, CREAM, 1.4)
    cv.line(x1 - 14, top - 1, x1 - 4, top - 3, CLOTH, 3.0)                   # el drap, sec i tibat
    cv.line(x1 - 14, top - 2, x1 - 5, top - 4, CLOTH, 4.0)


def _jar(cv, x, ybot, h, w, k):
    """Un pot de vidre buit, amb la tapa (de colors diferents)."""
    lids = [BRASSY, REDT, SHUT, IRONR]
    lid = lids[k % 4]
    cv.rect(x, ybot - h + 2, x + w - 1, ybot, GLASSJ, lambda xx, y: 1.6 + (1.8 if xx == x + 1 else 0) +
            (0.6 if xx == x + w - 2 else 0) - (0.6 if y == ybot else 0))
    cv.put(x + 1, ybot - h + 4, GLASSJ, 5.0)
    cv.rect(x, ybot - h, x + w - 1, ybot - h + 1, lid, lambda xx, y: 3.0 + (xx - x) * 0.2)


def jars(cv):
    """Les tres lleixes plenes de pots buits (setanta, contant els de la caixa) i la caixa de pots a terra."""
    x0, x1 = 152, 286
    n = 0
    for sy in (54, 84, 114):
        cv.rect(x0, sy, x1, sy + 3, PLANK, lambda x, y: 3.6 - (y - sy) * 0.6)    # la lleixa
        cv.rect(x0, sy + 4, x1, sy + 4, BLACKT, 1.4)
        cv.darken(x0, sy + 5, x1, sy + 7, 0.5)
        for bx in (x0 + 8, x1 - 8):                                            # les mènsules
            cv.rect(bx, sy + 4, bx + 1, sy + 10, IRONR, 2.6)
            cv.line(bx + 1, sy + 10, bx + 6, sy + 4, IRONR, 2.2)
        x = x0 + 2
        while x < x1 - 6:
            w = 5 if hr(x, sy) > 0.4 else 6
            h = 11 + int(hr(sy, x) * 7)
            if sy == 54:
                h = min(h, 14)
            _jar(cv, x, sy - 1, h, w, n)
            n += 1
            x += w + 1
    # la caixa de pots a terra, sota les lleixes
    cx0, cx1, cy = 240, 284, FLOOR_Y + 4
    for x in range(cx0 + 2, cx1 - 4, 6):
        _jar(cv, x, cy - 14, 9, 5, n)
        n += 1
    cv.rect(cx0, cy - 14, cx1, cy, PLANK, lambda x, y: 3.2 - (1.4 if (y - cy) % 5 == 0 else 0) + (x - cx0) * 0.01)
    text(cv, 'PER SI DE CAS', cx0 + 1, cy - 11, PLANK, 1.0, lit=0, flat=(60, 40, 28)) if False else None
    cv.rect(cx0 + 4, cy - 10, cx0 + 24, cy - 6, PAPER, 4.6)                  # una etiqueta
    for x in range(cx0 + 6, cx0 + 22, 2):
        cv.flat(x, cy - 8, (90, 80, 70))
    shadow(cv, cx0 + 18, cy + 1, 24, 2, 0.6)


def bol(cv):
    """El bol del gos, a terra davant del foc, amb el nom gravat: TITUS."""
    cx, cy = 150, 216
    shadow(cv, cx - 2, cy + 4, 13, 2, 0.7)
    cv.disc(cx, cy + 1, 11, 4, IRONR, lambda nx, ny: 3.6 + nx * 0.8 + ny * 0.4)
    cv.rect(cx - 10, cy - 2, cx + 10, cy + 2, IRONR, lambda x, y: 3.0 + (x - cx) * 0.06 - (y - cy) * 0.2)
    cv.disc(cx, cy - 2, 10, 3, IRONR, lambda nx, ny: 1.4 + ny * 0.8)
    cv.ring(cx, cy - 2, 10, IRONR, 5.0, step=8)
    for i, x in enumerate(range(cx - 7, cx + 8, 3)):                        # TITUS, gravat (es veu de prop)
        cv.put(x, cy + 1, IRONR, 1.4)
        cv.put(x + (1 if i % 2 else 0), cy, IRONR, 1.6)


# ─── La porta ───────────────────────────────────────────────────────────────

def door(cv):
    x0, y0, x1, y1 = DOOR
    cx = (x0 + x1) / 2
    r = (x1 - x0) / 2
    arc_y = y0 + r
    # el marc de pedra i el llindar
    for y in range(y0 - 6, y1 + 1):
        for x in range(x0 - 6, x1 + 7):
            d = math.hypot(x - cx, y - arc_y) if y < arc_y else abs(x - cx)
            if r < d <= r + 6 and (y < arc_y or x < x0 or x > x1):
                seg = int(math.atan2(y - arc_y, x - cx) * 7) if y < arc_y else y // 10
                cv.put(x, y, STONE, 4.4 - (1.4 if (y >= arc_y and y % 10 == 0) or hr(seg, 4) > 0.75 else 0) +
                       (x - cx) * 0.01)
    # les juntes, on s'escola el sol de fora
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            d = math.hypot(x - cx, y - arc_y) if y < arc_y else abs(x - cx)
            if d <= r:
                if d > r - 1 or y >= y1 - 1:
                    cv.flat(x, y, (255, 226, 160))
                else:
                    plank = (x - x0) % 9 == 0
                    lvl = 2.4 - (1.4 if plank else 0) + (fbm(x / 3, y / 24, 8) - 0.5) * 0.8
                    if (x - x0) % 9 == 0 and hr(x, 1) > 0.5 and y > arc_y and hr(x, y // 6) > 0.5:
                        cv.flat(x, y, (230, 190, 120))                     # una junta oberta
                    else:
                        cv.put(x, y, PLANK, lvl)
    # les travesses i la balda
    for ty in (arc_y + 8, y1 - 22):
        cv.rect(x0 + 1, ty, x1 - 1, ty + 4, PLANK, lambda x, y: 3.4 - (y - ty) * 0.4)
        for nx in range(x0 + 5, x1 - 2, 10):
            cv.put(nx, ty + 2, IRONR, 4.0)
    cv.rect(x1 - 14, 146, x1 - 4, 148, IRONR, lambda x, y: 3.6 - (y - 146) * 0.6)
    cv.disc(x1 - 4, 147, 2, 2, IRONR, 4.0)
    cv.rect(x1 - 10, 152, x1 - 8, 160, IRONR, 3.0)                           # el pany, amb la clau gran
    cv.put(x1 - 9, 154, BLACKT, 0.6)
    # la llum que entra per sota la porta, a terra
    cv.tint(x0 - 4, y1 + 1, x1 + 4, y1 + 5, SUN, lambda x, y: 0.4 - (y - y1) * 0.08)


# ─── El despatx ─────────────────────────────────────────────────────────────

def videotelefon(cv):
    """El videotelèfon vell: una caixa de plàstic crema groguenc, amb la pantalla de tub, el teclat i l'auricular
    penjat al costat amb el fil d'espiral."""
    x0, y0, x1, y1 = 370, 96, 406, 146
    cv.rect(x0 + 2, y0 + 2, x1 + 2, y1 + 2, BLACKT, 1.0)                     # l'ombra a la paret
    cv.darken(x0 + 2, y1 + 1, x1 + 3, y1 + 3, 0.6)
    cv.rect(x0, y0, x1, y1, CREAM, lambda x, y: 3.4 + (x - x0) * 0.02 + (0.8 if y == y0 else 0) - (1.0 if x == x1 else 0))
    outline(cv, x0, y0, x1, y1, CREAM[0])
    cv.rect(x0 + 4, y0 + 4, x1 - 4, y0 + 24, BLACKT, 1.4)                    # la pantalla
    cv.rect(x0 + 5, y0 + 5, x1 - 5, y0 + 23, CRT, lambda x, y: 1.4 + 0.8 * (1 - ((x - x0 - 18) / 14) ** 2 - ((y - y0 - 14) / 10) ** 2))
    cv.put(x0 + 7, y0 + 7, CRT, 4.4)
    cv.put(x0 + 8, y0 + 7, CRT, 3.6)
    for j in range(3):                                                       # el teclat
        for i in range(3):
            cv.rect(x0 + 6 + i * 6, y0 + 29 + j * 5, x0 + 9 + i * 6, y0 + 31 + j * 5, CREAM,
                    lambda x, y: 4.4 - (y - y0 - 29 - j * 5) * 0.6)
    cv.rect(x1 - 7, y0 + 29, x1 - 5, y0 + 31, REDT, 3.6)                    # el botó vermell
    text(cv, 'TELE', x0 + 6, y1 - 6, CREAM, 1.0, lit=0, flat=(110, 100, 84))
    # l'auricular, penjat a l'esquerra, i el fil d'espiral
    cv.rect(x0 - 7, y0 + 6, x0 - 2, y0 + 38, CREAM, lambda x, y: 3.6 + (x - x0 + 7) * 0.2)
    cv.rect(x0 - 8, y0 + 4, x0 - 2, y0 + 9, CREAM, 4.2)
    cv.rect(x0 - 8, y0 + 35, x0 - 2, y0 + 40, CREAM, 3.4)
    for i in range(30):
        t = i / 29
        cx = x0 - 5 + math.sin(t * 3) * 2
        cy = y0 + 41 + t * 30 - math.sin(t * math.pi) * 4
        cv.put(cx + (1 if i % 2 else -1), cy, BLACKT, 2.6)
    cv.put(x0 + 2, y1 + 3, BLACKT, 2.0)


def desk(cv):
    """La taula del despatx, contra la paret: el tauler vist una mica des de dalt, dos peus de calaixos plens
    (un calaix que no tanca, amb papers que en surten) i, al damunt, diaris vells, cartes i el cabdell de cordill."""
    x0, ytop, x1, yfeet = DESK
    yfront = ytop + 9                                                         # la vora del davant del tauler
    shadow(cv, (x0 + x1) // 2 - 10, yfeet, (x1 - x0) // 2 + 4, 4, 0.7)
    # el tauler
    cv.poly([(x0 + 4, ytop), (x1 - 4, ytop), (x1, yfront), (x0, yfront)], PLANK,
            lambda x, y: 3.8 + (y - ytop) * 0.08 + (fbm(x / 20, y / 2, 3) - 0.5) * 0.6)
    cv.rect(x0, yfront, x1, yfront + 3, PLANK, lambda x, y: 3.0 - (y - yfront) * 0.4)
    cv.rect(x0, yfront + 4, x1, yfront + 4, BLACKT, 1.0)
    # els dos peus de calaixos i el forat del mig
    for px0, px1 in ((x0 + 2, x0 + 40), (x1 - 40, x1 - 2)):
        cv.rect(px0, yfront + 5, px1, yfeet, PLANK, lambda x, y: 2.8 + (x - px0) * 0.01)
        outline(cv, px0, yfront + 5, px1, yfeet, PLANK[0])
        for k in range(3):
            dy0 = yfront + 7 + k * 11
            cv.rect(px0 + 2, dy0, px1 - 2, dy0 + 9, PLANK, lambda x, y: 3.4 - (0.8 if y == dy0 + 9 else 0) + (0.6 if y == dy0 else 0))
            cv.rect((px0 + px1) // 2 - 3, dy0 + 4, (px0 + px1) // 2 + 3, dy0 + 5, BRASSY, 3.8)
    cv.rect(x0 + 42, yfront + 5, x1 - 42, yfeet - 4, BLACKT, lambda x, y: 0.6 + (y - yfront) * 0.02)
    cv.rect(x0 + 42, yfront + 5, x1 - 42, yfront + 9, PLANK, 2.4)              # el calaix del mig
    # el calaix de dalt a la dreta, que no tanca: papers que en surten
    dy0 = yfront + 7
    cv.rect(x1 - 38, dy0 - 2, x1 - 4, dy0 + 7, PLANK, lambda x, y: 3.8 - (0.8 if y == dy0 + 7 else 0))
    for k, (dx, dh) in enumerate(((-34, 3), (-26, 4), (-18, 2), (-12, 5))):
        cv.rect(x1 + dx, dy0 - 2 - dh, x1 + dx + 7, dy0 - 1, PAPER, 4.4 - k * 0.3)
        cv.flat(x1 + dx + 1, dy0 - dh, (140, 130, 116))
    # al damunt: la pila de diaris vells, cartes, el cabdell de cordill, la làmpada
    for k in range(7):                                                       # diaris de fa trenta anys
        cv.rect(x0 + 10 - (k % 2), ytop - 2 - k * 2, x0 + 38 + (k % 3), ytop - 1 - k * 2, PAPER,
                lambda x, y: 3.6 - k * 0.1 + (0.8 if y == ytop - 2 - k * 2 else -0.6))
    for x in range(x0 + 12, x0 + 36, 2):
        cv.flat(x, ytop - 14, (90, 84, 76))
    cv.rect(x0 + 50, ytop + 1, x0 + 66, ytop + 5, PAPER, 4.8)                 # cartes obertes
    cv.rect(x0 + 58, ytop + 3, x0 + 74, ytop + 7, PAPER, 4.2)
    cv.flat(x0 + 66, ytop + 5, (160, 40, 40))
    cv.disc(x0 + 86, ytop - 1, 5, 4, CLOTH, lambda nx, ny: 4.0 + nx * 0.4 - ny * 0.4)   # el cabdell de cordill
    for k in range(-3, 4, 2):
        cv.line(x0 + 83 + k, ytop - 4, x0 + 89 + k, ytop + 2, CLOTH, 2.6)
    cv.line(x0 + 90, ytop + 2, x0 + 98, ytop + 6, CLOTH, 3.0)
    lx = x1 - 18                                                             # la làmpada de despatx
    cv.disc(lx, ytop + 1, 7, 2, BRASSY, 3.0)
    cv.rect(lx - 1, ytop - 24, lx + 1, ytop, BRASSY, lambda x, y: 3.4 + (x - lx))
    cv.poly([(lx - 10, ytop - 22), (lx + 10, ytop - 22), (lx + 6, ytop - 32), (lx - 6, ytop - 32)], SHUT,
            lambda x, y: 2.4 + (x - lx) * 0.08 + (0.6 if y == ytop - 32 else 0))
    cv.rect(lx - 10, ytop - 22, lx + 10, ytop - 22, SHUT, 1.6)


def wiring(cv):
    """La bombeta del sostre (apagada: s'estalvia) i el cable grapat a la paret fins al videotelèfon."""
    bx = 322
    cv.rect(bx, 0, bx, 34, BLACKT, 1.6)
    cv.rect(bx - 2, 34, bx + 2, 38, BLACKT, 2.6)
    cv.disc(bx, 42, 3, 4, GLASSJ, lambda nx, ny: 2.4 - nx - ny)
    cv.put(bx - 1, 41, GLASSJ, 5.0)
    for y in range(CEIL_Y + 3, 96):
        cv.put(388, y, CREAM, 2.0)
        if y % 14 == 0:
            cv.put(387, y, BLACKT, 1.6)
            cv.put(389, y, BLACKT, 1.6)
    cv.rect(385, 60, 391, 68, CREAM, lambda x, y: 4.0 - (x - 385) * 0.2)     # l'interruptor
    cv.put(388, 64, BLACKT, 1.0)


def mark(cv):
    """On penjava el quadre: la calç més blanca (no l'ha tocat el sol) i el clau."""
    x0, y0, x1, y1 = PIC
    cv.tint(x0 + 1, y0 + 1, x1 - 1, y1 - 1, (246, 242, 228), 0.35)
    cv.rect((x0 + x1) // 2, y0 - 8, (x0 + x1) // 2 + 1, y0 - 7, IRONR, 2.6)
    cv.line((x0 + x1) // 2, y0 - 7, x0 + 6, y0, BLACKT, 2.0) if False else None


def window(cv):
    """El finestró del despatx: els porticons tancats, i per l'escletxa del mig, el sol."""
    x0, y0, x1, y1 = WIN
    cv.rect(x0 - 4, y0 - 4, x1 + 4, y1 + 6, LIME, lambda x, y: 2.6 + (0.8 if y > y1 else 0))   # l'ampit fondo
    cv.rect(x0 - 5, y1 + 4, x1 + 5, y1 + 6, STONE, lambda x, y: 4.6 - (y - y1 - 4) * 0.8)
    cx = (x0 + x1) // 2
    for side, (a, b) in enumerate(((x0, cx - 2), (cx + 3, x1))):
        cv.rect(a, y0, b, y1, SHUT, lambda x, y: 2.6 + (0.6 if side else 0) - (1.4 if (y - y0) % 5 == 4 else 0) +
                (fbm(x / 4, y / 9, 13) - 0.5) * 0.8)
        outline(cv, a, y0, b, y1, SHUT[0])
    # l'escletxa entre els dos porticons: el sol de fora
    for y in range(y0, y1 + 1):
        for x in range(cx - 1, cx + 3):
            cv.flat(x, y, (255, 246, 210) if x in (cx, cx + 1) else (250, 210, 140))
    cv.glow(cx + 1, (y0 + y1) // 2, 26, (255, 220, 160), 0.5)
    cv.rect(cx - 3, (y0 + y1) // 2 - 2, cx + 4, (y0 + y1) // 2, IRONR, 3.6)    # la balda


def sunbeam(cv):
    """El raig de sol del finestró, que travessa la pols i fa una taca a terra."""
    for X, Y, x, y in cv.pixels(300, 56, W - 1, 251):                       # (píxel a píxel, a la resolució real)
        b = beam(x, y)
        if b > 0:
            k = 0.18 * b if y < FLOOR_Y else 0.34 * b
            if k > B4[Y & 3][X & 3] * 0.5:
                cv.P[X, Y] = mix(cv.P[X, Y], SUN, k + 0.12) + (255,)


def calendari(cv):
    """Un calendari de fa sis anys, amb un núvol dibuixat a mà sobre un dia."""
    x0, y0 = 420, 64
    cv.rect(x0, y0, x0 + 24, y0 + 34, PAPER, lambda x, y: 4.6 - (y - y0) * 0.01)
    cv.rect(x0, y0, x0 + 24, y0 + 12, BLUE, lambda x, y: 2.4 + (fbm(x / 4, y / 4, 2) - 0.5), lit=1.0)
    cv.disc(x0 + 12, y0 + 6, 4, 3, PAPER, 5.0)
    for j in range(4):
        for i in range(5):
            cv.flat(x0 + 3 + i * 4, y0 + 16 + j * 4, (110, 100, 90))
    cv.disc(x0 + 15, y0 + 24, 2, 1.4, BLUE, 2.8)
    cv.rect(x0 + 11, y0 - 3, x0 + 12, y0 - 1, IRONR, 2.4)


# ─── Composició ─────────────────────────────────────────────────────────────

def bg(cv):
    ceiling(cv)
    wall(cv)
    floor(cv)
    hearth(cv)
    jars(cv)
    sink(cv)
    bol(cv)
    door(cv)
    wiring(cv)
    videotelefon(cv)
    calendari(cv)
    mark(cv)
    window(cv)
    desk(cv)
    shadow(cv, 262, FLOOR_Y + 3, 30, 2, 0.5)
    sunbeam(cv)
    for y in range(RH, H):
        for x in range(W):
            cv.flat(x, y, (0, 0, 0))


# ─── Props ──────────────────────────────────────────────────────────────────

def quadre(cv):
    """El retrat de la mare: un marc daurat, el passe-partout ovalat i, a dins, una dona jove amb el cabell
    recollit i un mocador blau, davant d'un camp de blat verd (d'abans de la secada)."""
    x0, y0, x1, y1 = PIC
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    cv.line(cx, y0 - 7, x0 + 8, y0, BLACKT, 1.6)                              # el cordill del clau
    cv.line(cx, y0 - 7, x1 - 8, y0, BLACKT, 1.6)
    cv.rect(x0 + 3, y1 + 1, x1 + 3, y1 + 3, BLACKT, 1.0)                      # l'ombra a la paret
    cv.darken(x1 + 1, y0 + 3, x1 + 3, y1 + 3, 0.6)
    cv.rect(x0, y0, x1, y1, GILT, lambda x, y: 3.4 + (1.2 if (x - x0 < 2 or y - y0 < 2) else 0) -
            (1.2 if (x1 - x < 2 or y1 - y < 2) else 0) + (0.8 if (x + y) % 5 == 0 else 0))
    cv.rect(x0 + 4, y0 + 4, x1 - 4, y1 - 4, CREAM, 4.2)                       # el passe-partout
    rx, ry = (x1 - x0) / 2 - 7, (y1 - y0) / 2 - 7
    for y in range(int(y0 + 5), int(y1 - 4)):
        for x in range(int(x0 + 5), int(x1 - 4)):
            nx, ny = (x - cx) / rx, (y - cy) / ry
            if nx * nx + ny * ny <= 1:
                if ny < -0.1:
                    cv.put(x, y, [(110, 150, 190), (150, 190, 220), (196, 220, 236)], 1.4 - ny)   # cel blau
                else:
                    cv.put(x, y, [(40, 80, 30), (70, 120, 40), (110, 160, 60), (160, 196, 90)],
                           2.0 + ((x + y) % 3 == 0) * 0.8 - ny)                                  # el blat verd
    # la mare: cara, cabell recollit, mocador blau, coll de la brusa
    fx, fy = cx, cy - 2
    cv.poly([(fx - 11, y1 - 8), (fx + 11, y1 - 8), (fx + 8, fy + 10), (fx - 8, fy + 10)], [(200, 190, 170), (230, 222, 204), (250, 246, 236)],
            lambda x, y: 1.4 + (x - fx) * 0.06)                                # la brusa
    cv.poly([(fx - 4, fy + 9), (fx + 4, fy + 9), (fx, fy + 14)], BLUE, 2.6)  # el mocador
    cv.disc(fx, fy, 6, 8, [(120, 76, 56), (170, 116, 86), (208, 156, 118), (232, 190, 156)],
            lambda nx, ny: 2.4 + nx * 0.6 - ny * 0.2)                          # la cara
    HAIRM = [(30, 20, 16), (56, 36, 26), (86, 58, 40)]
    cv.disc(fx, fy - 6, 7, 5, HAIRM, lambda nx, ny: 1.4 + nx * 0.5)                                       # el cabell
    for sx in (fx - 7, fx - 6, fx + 6, fx + 7):
        cv.rect(sx, fy - 4, sx, fy + 3, HAIRM, 1.2)
    cv.disc(fx + 6, fy - 4, 3, 3, [(30, 20, 16), (56, 36, 26), (86, 58, 40)], 1.6)                         # el monyo
    cv.flat(fx - 2, fy, (50, 30, 26))
    cv.flat(fx + 2, fy, (50, 30, 26))
    cv.flat(fx - 1, fy + 4, (150, 70, 60))
    cv.flat(fx, fy + 4, (150, 70, 60))
    cv.put(x0 + 6, y0 + 6, GILT, 5.6)                                         # lluentor al marc


def caixa_forta(cv):
    """La caixa forta vella, encastada a la paret, amb el teclat de cinc lletres i la maneta."""
    x0, y0, x1, y1 = SAFE
    cv.rect(x0 - 2, y0 - 2, x1 + 2, y1 + 2, LIME, 1.8)                        # el forat a la paret
    cv.rect(x0, y0, x1, y1, SAFEG, lambda x, y: 3.4 + (x - x0) * 0.02 + (fbm(x / 3, y / 3, 6) - 0.5) * 0.6)
    outline(cv, x0, y0, x1, y1, SAFEG[0])
    cv.rect(x0 + 1, y0 + 1, x1 - 1, y0 + 1, SAFEG, 5.0)
    for nx, ny in ((x0 + 2, y0 + 2), (x1 - 2, y0 + 2), (x0 + 2, y1 - 2), (x1 - 2, y1 - 2)):
        cv.put(nx, ny, SAFEG, 5.4)
    # el teclat de lletres: cinc rodetes amb una lletra a la finestreta
    for i in range(5):
        kx = x0 + 4 + i * 4
        cv.rect(kx, y0 + 6, kx + 2, y0 + 12, BRASSY, lambda x, y: 3.4 + (x - kx) * 0.4 - (0.8 if y in (y0 + 6, y0 + 12) else 0))
        cv.flat(kx + 1, y0 + 9, (40, 30, 20))
    cv.disc((x0 + x1) // 2, y0 + 21, 4, 4, SAFEG, lambda nx, ny: 4.4 - nx - ny)   # la maneta
    cv.line((x0 + x1) // 2 - 4, y0 + 21, (x0 + x1) // 2 + 4, y0 + 21, SAFEG, 2.0)
    text(cv, 'ROCA', x0 + 6, y1 - 6, BRASSY, 4.0, lit=0, flat=(176, 140, 70))


def caixa_oberta(cv):
    """La porta de la caixa forta, oberta cap a l'esquerra: a dins, buida, un sobre vell."""
    x0, y0, x1, y1 = SAFE
    cv.rect(x0, y0, x1, y1, BLACKT, lambda x, y: 0.6 + (x - x0) * 0.04 + (y - y0) * 0.02)   # l'interior
    cv.rect(x0 + 1, y1 - 3, x1 - 1, y1 - 1, SAFEG, 2.0)                       # el fons de la caixa
    cv.rect(x0 + 6, y1 - 8, x0 + 18, y1 - 3, PAPER, 3.2)                      # un sobre que hi queda
    cv.line(x0 + 6, y1 - 8, x0 + 12, y1 - 5, PAPER, 2.0)
    cv.line(x0 + 12, y1 - 5, x0 + 18, y1 - 8, PAPER, 2.0)
    # la porta, girada: un gruix d'acer vist de cantell, i la cara de dins
    cv.poly([(x0, y0), (x0 - 14, y0 + 4), (x0 - 14, y1 + 4), (x0, y1)], SAFEG,
            lambda x, y: 2.6 + (x - x0 + 14) * 0.08)
    cv.rect(x0 - 16, y0 + 4, x0 - 14, y1 + 4, SAFEG, 4.6)
    for k in (8, 16, 24):                                                    # els forrellats
        cv.rect(x0 - 18, y0 + 2 + k, x0 - 15, y0 + 3 + k, SAFEG, 5.4)
    cv.darken(x0 - 15, y1 + 5, x0, y1 + 7, 0.6)


def quadre_apartat(cv):
    """El quadre de la mare, despenjat i recolzat a terra contra la paret, sota el finestró, de cara a la sala."""
    bx0, base = 572, FLOOR_Y + 6
    h, w = 54, 44
    top = base - h
    shadow(cv, bx0 + w // 2 - 4, base + 1, w // 2 + 4, 3, 0.7)
    pts = [(bx0 + 4, top), (bx0 + w + 4, top), (bx0 + w, base), (bx0, base)]
    cv.poly(pts, GILT, lambda x, y: 3.2 + (y - top) * 0.004)
    cv.poly([(bx0 + 8, top + 4), (bx0 + w, top + 4), (bx0 + w - 4, base - 4), (bx0 + 4, base - 4)], CREAM, 3.8)
    cx, cy = bx0 + w / 2 + 2, top + h / 2
    cv.disc(cx, cy, w / 2 - 8, h / 2 - 8, [(110, 150, 190), (150, 190, 220), (196, 220, 236)], lambda nx, ny: 1.4 - ny)
    cv.disc(cx, cy + 10, w / 2 - 9, 9, [(40, 80, 30), (70, 120, 40), (110, 160, 60)], 1.8)
    cv.disc(cx, cy + 6, w / 2 - 8, h / 2 - 8, [(40, 80, 30), (70, 120, 40), (110, 160, 60)],
            lambda nx, ny: -9 if ny < 0.3 else 1.8)
    cv.disc(cx, cy - 1, 6, 8, [(120, 76, 56), (170, 116, 86), (208, 156, 118), (232, 190, 156)], 2.4)
    cv.disc(cx, cy - 7, 7, 5, [(30, 20, 16), (56, 36, 26), (86, 58, 40)], 1.6)
    cv.poly([(cx - 10, cy + 18), (cx + 10, cy + 18), (cx + 7, cy + 9), (cx - 7, cy + 9)],
            [(200, 190, 170), (230, 222, 204), (250, 246, 236)], 1.4)
    cv.flat(cx - 2, cy - 1, (50, 30, 26))
    cv.flat(cx + 2, cy - 1, (50, 30, 26))
