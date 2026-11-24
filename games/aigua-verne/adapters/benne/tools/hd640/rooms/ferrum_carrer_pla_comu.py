"""
Aigua Verne — el carrer de Ferrum pla de sempre (de cara, a 1×): les textures de `ferrum_carrer` (en 3D).

D'esquerra a dreta: la Cantimplora aparcada amb la rampa de la bodega baixada; el local del sindicat; al fons del
carrer, les escombreres, el castellet de la mina i la Canonada; el piquet amb la pancarta, la foguera en un bidó i la
canalla asseguda en caixes; les cases dels miners, amb el panell del preu; la font de Verne; la pila de comptadors
arrencats; la fosa, freda, amb el portal gran mig obert; i el condensador vell de la mina.

Cada peça es pot dibuixar sola (en un llenç transparent) per fer-ne una textura o un sprite. Aquí també hi ha els
decorats (`barril_piquet`, `condensador_arreglat`) i les animacions de sempre (`_frames_foc`, `_smoke_loop`, ...),
dibuixats plans.
"""
import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

import functools
import math

from PIL import Image

from hd.pix import Canvas, Light, W, H, hr, mix, B4
from hd.rooms.comu import _diff, text, text_width
from hd.rooms.exterior import fbm
from hd640.rooms.ferrum_comu import (
    RH, SMOG, HAZE, SLAGF, SOOT, MORTAR, COB, COAL, IRONF, RUSTF, TIN, PLANKF, WHITEV, BLUEV, REDV, BLACKT, LED,
    FIREF, GLOWF, CLOTH, REDP, WATER, HELM, WARMG,
    smog_sky, canonada, far_skyline, brick_wall, brick_lvl, soot_top, window, cobbles, panell, font_verne,
    pila_comptadors, smoke_frames, chimney, qtext)
from hd640.rooms.ferrum_gent import persona_c

Canvas1x = Canvas                 # (llenços auxiliars en píxels de sala: figures, textos)

HOR = 150                       # l'horitzó, al fons del carrer
BASE = 192                      # on toquen a terra les façanes del fons
SUN = (150, 54)
BIDO = (252, 224)               # el bidó de la foguera (centre, base)
FONT = (372, 226)
COND = (572, 636, 230)          # el condensador (x0, x1, base)
OLIVE = [(18, 22, 12), (30, 36, 20), (44, 52, 28), (60, 70, 38), (78, 90, 50), (98, 110, 62), (120, 132, 78),
         (144, 154, 96)]
SAFE = [(60, 20, 6), (120, 44, 10), (190, 80, 16), (236, 120, 30), (252, 168, 70), (255, 210, 130)]
SLATE = [(14, 14, 18), (24, 24, 30), (36, 36, 42), (50, 50, 56), (66, 64, 70), (86, 82, 86)]
GREENL = [(10, 40, 16), (20, 90, 30), (40, 160, 60), (110, 230, 120), (210, 255, 210)]

LIGHT = Light(ambient=0.2, vignette=(70, 20), floor_fade=(246, 30))
LIGHT.point(SUN[0], SUN[1] + 40, r=520, k=1.3, power=1.2)              # el sol, apagat pel fum, a l'esquerra
LIGHT.point(BIDO[0], BIDO[1] - 26, r=90, k=1.4, power=1.6)             # la foguera del piquet


# ─── El fons del carrer ────────────────────────────────────────────────────

def sky_and_far(cv):
    """El cel i el fons del carrer (pla)."""
    smog_sky(cv, HOR, sun=SUN, seed=3)
    far_skyline(cv, HOR, seed=7, headframes=((232, HOR - 2, 52),), chimneys=((170, HOR, 74, 3), (330, HOR, 86, 4),
                                                                              (348, HOR, 92, 3)))
    canonada(cv, 266, HOR - 1)
    # cases llunyanes al fons del carrer (perspectiva): dues fileres que fugen cap a (248, HOR)
    for side in (-1, 1):
        for i in range(7):
            f = 1 - i / 7
            xa = 248 + side * (6 + 50 * f ** 1.4)
            xb = 248 + side * (6 + 50 * (f - 1 / 7) ** 1.4 if f > 1 / 7 else 6)
            top = HOR - 4 - 34 * f ** 1.4
            base = HOR + 40 * f ** 1.4
            x0, x1 = sorted((xa, xb))
            for x in range(int(x0), int(x1) + 1):
                tt = top + (hr(i, side) * 5) * f
                for y in range(int(tt), int(base)):
                    lvl = 2.4 + f * 0.8 + (hr(int(x) // 3, y // 3, i) - 0.5) * 0.5
                    if (y - int(tt)) % max(2, int(9 * f)) == 1 and (x - int(x0)) % max(3, int(8 * f)) in (1, 2):
                        lvl -= 1.2                                                        # finestres fosques
                    cv.put(x, y, HAZE if f < 0.5 else SOOT, lvl - (0 if f < 0.5 else 0.4), lit=0)
    cv.tint(200, 90, 296, BASE, (150, 110, 84), lambda x, y: 0.28 * max(0.0, 1 - (y - 120) / 70))   # boira de fum


# ─── La Cantimplora i la rampa ─────────────────────────────────────────────

def _hull_edge(y):
    """El perfil de la popa de la nau (x de la vora dreta a l'alçada y): panxuda, com una cisterna."""
    return 34 + 22 * math.sin(min(1.0, max(0.0, (y + 30) / 220)) * math.pi) ** 0.7


def nau(cv):
    """La popa de la Cantimplora, aparcada a l'esquerra, amb la rampa de la bodega baixada fins al carrer."""
    def hull_lvl(x, y):
        e = _hull_edge(y)
        u = x / e                                                                       # 0 a la vora, 1 al cantell
        v = 3.0 + (0.9 if u > 0.55 else 0) - (1.6 * (u - 0.88) / 0.12 if u > 0.88 else 0)
        v += (fbm(x / 10, y / 14, 61) - 0.5) * 0.9
        if (y - 6) % 28 == 0:
            v -= 1.6                                                                   # juntes de planxa
        elif (y - 6) % 28 == 1:
            v += 0.6
        if (y - 6) % 28 == 3 and x % 5 == 2:
            v += 1.4                                                                   # reblons
        return v
    pts = [(0, 0)] + [(_hull_edge(y), y) for y in range(0, 182, 4)] + [(0, 182)]
    cv.poly(pts, OLIVE, hull_lvl)
    for y in range(0, 182):                                                            # contorn
        cv.put(_hull_edge(y), y, COAL, 1.0)
    for y in range(86, 94):                                                            # la franja de seguretat
        for x in range(0, int(_hull_edge(y))):
            on = ((x + y) // 4) % 2 == 0
            cv.put(x, y, SAFE if on else COAL, (3.0 if on else 1.8) + (0.6 if x / _hull_edge(y) > 0.55 else 0))
    cv.tint(0, 0, 60, 182, (120, 64, 30), lambda x, y: 0.4 * fbm(x / 5, y / 9, 63) ** 2)   # rovell
    cv.disc(22, 54, 7, 7, IRONF, lambda nx, ny: 4.0 - nx - ny)                         # un ull de bou
    cv.disc(22, 54, 5, 5, GLOWF, lambda nx, ny: 2.6 - ny * 0.8, lit=0)
    # la boca de la bodega, oberta, il·luminada per dins (llums de filament)
    cv.poly([(0, 116), (40, 118), (44, 168), (0, 172)], PLANKF, lambda x, y: 1.4 + (y - 116) * 0.02, lit=0)
    cv.tint(0, 116, 44, 172, (255, 196, 110), lambda x, y: 0.4 * max(0.0, 1 - x / 46))
    cv.rect(0, 150, 30, 168, PLANKF, lambda x, y: 2.2 - (1.0 if (x // 6) % 2 else 0), lit=0)   # caixes, dins
    cv.glow(14, 124, 12, (255, 220, 150), 0.6)
    cv.rect(12, 121, 15, 124, GLOWF, 5.0, lit=0)
    cv.rect(0, 114, 42, 116, OLIVE, 4.2)                                               # el marc de la boca
    cv.line(42, 116, 46, 168, OLIVE, 1.6)
    # la rampa: un pla inclinat de xapa antilliscant, amb les vores de franges taronja
    def ramp_lvl(x, y):
        v = 1.0 + (y - 166) * 0.012
        if (x + y * 2) % 7 == 0:
            v += 0.9
        return v
    cv.poly([(0, 170), (44, 168), (82, 246), (0, 252)], TIN, ramp_lvl)
    for t in range(0, 100):                                                            # les vores
        f = t / 99
        x, y = 44 + 38 * f, 168 + 78 * f
        on = (t // 6) % 2 == 0
        for k in range(3):
            cv.put(x - k, y, SAFE if on else COAL, 3.4 if on else 1.4)
    cv.line(45, 169, 83, 247, COAL, 0.6)
    cv.rect(0, 166, 46, 169, IRONF, lambda x, y: 4.0 - (y - 166) * 0.6)                # la frontissa
    for hx in (8, 22, 36):
        cv.disc(hx, 167, 2, 2, IRONF, 4.8)


# ─── El sindicat ───────────────────────────────────────────────────────────

SIND = (62, 204, 58)            # x0, x1, top


def sindicat(cv):
    x0, x1, top = SIND
    brick_wall(cv, x0, top, x1, BASE, base=3.6, seed=11, soot=soot_top(top, 44, 2.2, 12))
    # la cornisa i el ràfec
    cv.rect(x0 - 3, top - 4, x1 + 3, top, MORTAR, lambda x, y: 4.0 - (y - top + 4) * 0.5)
    cv.rect(x0 - 3, top + 1, x1 + 3, top + 2, COAL, 1.4)
    # el sòcol de pedra
    cv.rect(x0, BASE - 9, x1, BASE, MORTAR, lambda x, y: 3.0 + (0.6 if (x // 8 + y // 3) % 2 else 0) -
            (1.4 if x % 8 == 0 else 0))
    # finestres de dalt (una encesa) i la de baix, al costat de la porta
    for i, wx in enumerate((76, 128, 176)):
        window(cv, wx, 70, 16, 22, lit=(i == 1), seed=i)
    window(cv, 166, 128, 22, 26, lit=True, seed=9)
    # la porta del sindicat: fusta verda vella amb un vidre a dalt
    dx0, dx1, dtop = 112, 146, 106
    cv.rect(dx0 - 4, dtop - 5, dx1 + 4, dtop - 1, MORTAR, 4.0)                          # la llinda
    for y in range(dtop, BASE + 1):
        for x in range(dx0, dx1 + 1):
            if x in (dx0, dx1) or y == dtop:
                cv.put(x, y, PLANKF, 1.6)
                continue
            if dtop + 4 <= y <= dtop + 20 and dx0 + 5 <= x <= dx1 - 5:
                cv.put(x, y, GLOWF, 2.4 + (fbm(x / 3, y / 3, 3) - 0.5) * 1.4 - (y - dtop) * 0.03, lit=0)   # el vidre
                continue
            panel = (y - dtop - 24) % 32 in (0, 1) or (x - dx0) in (16, 17, 18)
            v = 2.6 + (fbm(x / 3, y / 20, 5) - 0.5) * 1.0 - (1.0 if panel else 0) - (0.5 if x > (dx0 + dx1) / 2 else 0)
            cv.put(x, y, OLIVE, v)
    cv.rect(dx0 + 5, dtop + 12, dx1 - 5, dtop + 12, PLANKF, 1.4)
    cv.disc(dx1 - 6, 156, 1.5, 1.5, TIN, 4.6)                                          # el pom
    cv.rect(dx0 - 1, BASE - 1, dx1 + 1, BASE, MORTAR, 4.2)                              # el graó
    # el rètol: una post pintada a mà
    s = 'SINDICAT MINER'
    tw = text_width(s)
    bx0, by0 = (dx0 + dx1) // 2 - tw // 2 - 4, 92
    cv.rect(bx0, by0, bx0 + tw + 7, by0 + 9, PLANKF, lambda x, y: 4.2 - (y - by0) * 0.15 + (hr(x // 6, 1) - 0.5) * 0.6)
    cv.rect(bx0, by0 + 10, bx0 + tw + 7, by0 + 10, COAL, 1.0)
    text(cv, s, bx0 + 4, by0 + 2, CLOTH, 3.8)
    # una pancarta vella penjada de les finestres de dalt (d'una vaga d'abans), estripada
    s2 = 'LA MINA ES NOSTRA'
    tw2 = text_width(s2)
    px0, py0 = 164, 96
    for x in range(px0, px0 + 34):
        sag = math.sin((x - px0) / 33 * math.pi) * 2
        for y in range(int(py0 + sag), int(py0 + sag + 10)):
            if not (x > px0 + 26 and y > py0 + sag + 6):                                # estripada
                cv.put(x, y, CLOTH, 3.0 + (fbm(x / 5, y / 4, 8) - 0.5) * 1.2 - (0.6 if (x - px0) % 11 == 0 else 0))
    text(cv, 'VAGA', px0 + 9, py0 + 3, REDP, 2.4)
    # el canaló de baixada
    cv.rect(x1 - 4, top + 2, x1 - 2, BASE - 2, IRONF, lambda x, y: 3.0 - (x - x1 + 4) * 0.6 +
            (1.0 if (y - top) % 22 == 0 else 0))


# ─── Les cases dels miners ─────────────────────────────────────────────────

HOUSES = (292, 458, 86)          # x0, x1, alçada de la cornisa
CHIMNEYS = ((316, 58), (378, 54), (440, 60))


def cases(cv):
    x0, x1, top = HOUSES
    # la teulada de pissarra, a una aigua, i les xemeneies
    cv.poly([(x0 - 3, top + 1), (x0 + 6, top - 20), (x1 - 2, top - 20), (x1 + 2, top + 1)], SLATE,
            lambda x, y: 3.0 + (y - top + 20) * 0.04 - (1.2 if (y - top) % 4 == 0 else 0) -
            (0.8 if (x + (y // 4) * 3) % 7 == 0 else 0) + (fbm(x / 9, y / 5, 21) - 0.5) * 0.8)
    for cx, ct in CHIMNEYS:
        brick_wall(cv, cx - 5, ct, cx + 5, top - 12, base=3.0, seed=cx, bw=6, bh=3,
                   soot=soot_top(ct, 10, 2.4, cx))
        cv.rect(cx - 6, ct - 2, cx + 6, ct, MORTAR, 2.6)
        cv.rect(cx - 2, ct - 5, cx + 1, ct - 2, RUSTF, 2.4)                           # l'olla del fum
    # la façana: dues cases iguals (una paret mitgera al mig)
    brick_wall(cv, x0, top, x1, BASE, base=3.2, seed=21, soot=soot_top(top, 50, 1.8, 22))
    cv.rect(x0 - 3, top - 1, x1 + 2, top + 1, MORTAR, 3.4)
    cv.rect(374, top + 2, 376, BASE, MORTAR, lambda x, y: 2.0 + (x - 374) * 0.6)       # la mitgera
    cv.rect(x0, BASE - 8, x1, BASE, MORTAR, lambda x, y: 2.6 + (0.6 if (x // 8 + y // 3) % 2 else 0) -
            (1.4 if x % 8 == 0 else 0))
    # finestres i portes
    window(cv, 304, 132, 18, 24, lit=False, seed=2)
    window(cv, 432, 132, 18, 24, lit=True, seed=4)
    for i, wx in enumerate((302, 352, 396, 430)):
        window(cv, wx, 96, 14, 18, lit=(i == 2), seed=10 + i)
    for dx0 in (338, 392):
        dx1, dtop = dx0 + 26, 118
        cv.rect(dx0 - 3, dtop - 4, dx1 + 3, dtop - 1, MORTAR, 3.6)
        cv.rect(dx0, dtop, dx1, BASE - 1, PLANKF, lambda x, y: 2.4 - (1.2 if (x - dx0) % 6 == 0 else 0) +
                (fbm(x / 3, y / 14, dx0) - 0.5) * 0.8 - (y - dtop) * 0.004)
        cv.disc(dx1 - 4, 160, 1.2, 1.2, TIN, 4.0)
        # la marca on hi havia el comptador de Verne: el forat a la paret i dos tubs tallats
        mx = dx1 + 8
        cv.rect(mx, 166, mx + 7, 174, COAL, 1.0)
        cv.rect(mx + 1, 174, mx + 2, 180, RUSTF, 3.0)
        cv.rect(mx + 5, 174, mx + 6, 177, RUSTF, 3.0)
        cv.flat(mx + 5, 178, RUSTF[5])
    # els fils de la roba d'una finestra a l'altra, amb una samarreta
    for x in range(318, 352):
        y = 117 + math.sin((x - 318) / 34 * math.pi) * 3
        cv.put(x, y, COAL, 1.0)
    cv.rect(330, 119, 336, 126, CLOTH, lambda x, y: 3.6 - (x - 330) * 0.15)
    cv.rect(328, 119, 338, 121, CLOTH, 3.6)


# ─── La foneria ───────────────────────────────────────────────────────────────

FOSA = (458, 640, 26)


def fosa(cv, xemeneia=True):
    x0, x1, top = FOSA
    # la xemeneia gran (freda: la foneria està aturada)
    cx = 616
    if xemeneia:
        brick_wall(cv, cx - 9, 0, cx + 9, top + 4, base=2.8, seed=31, bw=7, bh=3, soot=soot_top(0, 40, 2.4, 31))
        for y in (8, 9):
            cv.rect(cx - 10, y, cx + 10, y, IRONF, 3.0)
    # el frontó de la nau i el cos
    cv.poly([(x0, top + 22), (x0 + 70, top - 4), (x1 + 4, top - 4), (x1 + 4, top + 22)], SOOT,
            lambda x, y: brick_lvl(x, y, x0, 0, 11, 4, 3.0, 33, soot_top(top - 4, 30, 2.6, 33)))
    cv.line(x0 - 2, top + 22, x0 + 70, top - 5, MORTAR, 3.6)
    cv.line(x0 + 70, top - 5, x1 + 4, top - 5, MORTAR, 3.6)
    brick_wall(cv, x0, top + 22, x1, BASE, base=3.4, seed=35, soot=soot_top(top + 22, 60, 1.6, 36))
    # el pilar de l'esquerra (maó més fosc) i el sòcol
    brick_wall(cv, x0, top + 22, x0 + 12, BASE, base=2.4, seed=37, bw=6)
    cv.rect(x0, BASE - 10, x1, BASE, MORTAR, lambda x, y: 2.4 + (0.6 if (x // 9 + y // 3) % 2 else 0) -
            (1.4 if x % 9 == 0 else 0))
    # les finestres altes, d'arc, amb vidres trencats
    for wx in (472, 584):
        for y in range(56, 84):
            for x in range(wx, wx + 22):
                r = math.hypot(x - wx - 10.5, (y - 64) * 1.0)
                if y < 64 and r > 11:
                    continue
                bar = (x - wx) % 6 == 5 or (y - 56) % 7 == 6
                broken = hr((x - wx) // 6, (y - 56) // 7, wx) > 0.78
                if bar:
                    cv.put(x, y, IRONF, 2.2)
                elif broken:
                    cv.put(x, y, COAL, 0.6, lit=0)
                else:
                    cv.put(x, y, SMOG, 3.4 + (fbm(x / 5, y / 5, wx) - 0.5) * 2.0, lit=0)
        for y in range(52, 58):
            for x in range(wx - 3, wx + 25):
                r = math.hypot(x - wx - 10.5, (y - 64) * 1.0)
                if 11 <= r <= 14:
                    cv.put(x, y, MORTAR, 3.8)
    # FONERIA, en lletres grosses de llauna clavades a la paret (n'hi falta una mica)
    s = 'FONERIA'
    sx = 530 - (text_width(s) * 3) // 2
    big = Canvas1x(40, 8, transparent=True)
    text(big, s, 0, 0, CLOTH, 4.0, lit=0)
    bp = big.img.load()
    for y in range(5):
        for x in range(text_width(s)):
            if bp[x, y][3]:
                for j in range(3):
                    for i in range(3):
                        if not (x == 25 and y > 2):                                      # la A, mig caiguda
                            cv.put(sx + x * 3 + i, 34 + y * 3 + j, TIN, 4.4 - j * 0.5 - i * 0.2)
                cv.put(sx + x * 3 + 3, 34 + y * 3 + 3, COAL, 0.6)
    # el portal gran: arc rebaixat, porta de ferro corredissa mig oberta, dins fosc
    px0, px1, ptop = 488, 574, 96
    cxa = (px0 + px1) / 2
    for y in range(ptop - 12, BASE + 1):
        for x in range(px0 - 6, px1 + 7):
            ay = ptop - 10 * math.sqrt(max(0.0, 1 - ((x - cxa) / ((px1 - px0) / 2 + 6)) ** 2))
            if y < ay:
                continue
            inner = px0 <= x <= px1 and y >= ptop - 9 * math.sqrt(max(0.0, 1 - ((x - cxa) / ((px1 - px0) / 2)) ** 2)) + 3
            if not inner:
                if y < ptop + 2 or x < px0 or x > px1:
                    k = int(math.atan2(y - ptop - 20, x - cxa) * 9)
                    cv.put(x, y, MORTAR, 3.4 + (hr(k, 3) - 0.5) * 1.2 - (1.2 if hr(k, 4) > 0.8 else 0))
                continue
            d = (y - ptop) / (BASE - ptop)
            cv.put(x, y, COAL, 1.2 + d * 0.6 + (fbm(x / 8, y / 8, 41) - 0.5) * 0.8, lit=0)
    # dins: el forn apagat, que s'endevina, i el pont grua
    cv.rect(520, 132, 546, BASE, SLAGF, lambda x, y: 1.6 - (x - 520) * 0.02, lit=0)
    cv.disc(533, 132, 13, 5, SLAGF, 1.8, lit=0)
    cv.rect(526, 166, 540, 180, COAL, 0.4, lit=0)
    cv.rect(px0 + 2, 110, px1 - 2, 112, SLAGF, 2.0, lit=0)
    # la porta corredissa, de planxa, tapant mig portal
    def door_lvl(x, y):
        v = 3.0 + (fbm(x / 7, y / 10, 43) - 0.5) * 1.2
        if (x - px0) % 14 == 0:
            v -= 1.4
        if (y - ptop) % 30 == 0:
            v += 0.8
        return v
    cv.rect(px0, ptop + 4, 516, BASE, IRONF, door_lvl)
    cv.tint(px0, ptop + 4, 516, BASE, (130, 60, 30), lambda x, y: 0.5 * fbm(x / 6, y / 7, 44) ** 1.5)   # rovell
    cv.rect(px0 - 4, ptop + 1, px1 + 4, ptop + 3, IRONF, 4.0)                          # el carril
    for x in (px0 + 4, 512):
        cv.disc(x, ptop + 5, 2, 2, IRONF, 4.6)
    cv.line(515, ptop + 5, 517, BASE - 1, COAL, 1.0)
    # cartell d'aturada a la porta
    cv.rect(494, 140, 512, 156, CLOTH, lambda x, y: 3.6 - (y - 140) * 0.05)
    text(cv, 'TANCAT', 494 + 1, 142, REDP, 2.6) if False else None
    text(cv, 'VAGA', 497, 143, REDP, 2.8)
    cv.rect(496, 150, 510, 150, REDP, 2.4)
    cv.rect(496, 152, 506, 152, COAL, 2.0)
    # el carril de les vagonetes que surt del portal
    for k, xa in enumerate((520, 544)):
        for y in range(BASE, RH):
            t = (y - BASE) / (RH - BASE)
            x = xa + (xa - 532) * t * 1.2 - t * 30
            cv.put(x, y, IRONF, 4.6 - t * 0.4)
            cv.put(x + 1, y, IRONF, 2.6)


# ─── El condensador vell ───────────────────────────────────────────────────

def condensador(cv):
    x0, x1, base = COND
    # les potes i el dipòsit de sota
    for lx in (x0 + 4, x1 - 6):
        cv.rect(lx, base - 18, lx + 2, base, IRONF, lambda x, y: 3.0 - (x - lx) * 0.6)
    cv.rect(x0 + 2, base - 30, x1 - 2, base - 16, RUSTF, lambda x, y: 3.4 - (x - x0) * 0.02 +
            (fbm(x / 4, y / 4, 51) - 0.5) * 1.4 + (0.8 if y == base - 30 else 0))
    cv.rect(x0 + 2, base - 17, x1 - 2, base - 16, COAL, 1.4)
    # el cos de llauna, amb les aletes (verticals) a la dreta i el ventilador rodó a l'esquerra
    bx0, bx1, btop = x0, x1, base - 74
    cv.rect(bx0, btop, bx1, base - 31, TIN, lambda x, y: 3.6 - (x - bx0) * 0.02 + (fbm(x / 6, y / 6, 53) - 0.5) * 1.0)
    cv.rect(bx0, btop, bx1, btop + 1, TIN, 5.4)
    cv.rect(bx1 - 1, btop, bx1, base - 31, TIN, 2.0)
    for x in range(bx0 + 30, bx1 - 3, 3):                                              # les aletes
        cv.rect(x, btop + 6, x, base - 36, TIN, 5.0)
        cv.rect(x + 1, btop + 6, x + 1, base - 36, TIN, 2.0)
    cx, cy, r = bx0 + 15, btop + 22, 11
    cv.disc(cx, cy, r + 1, r + 1, IRONF, 2.6)
    cv.disc(cx, cy, r, r, COAL, lambda nx, ny: 1.4 + ny * 0.4)
    for a in range(3):                                                                 # les pales, aturades
        an = a * 2.094 + 0.4
        for d in range(2, r - 1):
            cv.put(cx + math.cos(an) * d, cy + math.sin(an) * d, TIN, 3.4)
            cv.put(cx + math.cos(an + 0.2) * d, cy + math.sin(an + 0.2) * d, TIN, 2.4)
    for d in range(-r, r + 1, 3):                                                      # la reixa
        for e in range(-r, r + 1):
            if d * d + e * e <= r * r:
                cv.put(cx + d, cy + e, IRONF, 3.6)
    cv.disc(cx, cy, 2, 2, TIN, 4.2)
    # el rovell que regalima i la placa
    cv.tint(bx0, btop, bx1, base - 31, (130, 64, 30), lambda x, y: 0.55 * fbm(x / 4, y / 10, 55) ** 2.2)
    cv.rect(bx0 + 6, base - 42, bx0 + 24, base - 36, TIN, 5.0)
    text(cv, 'MINA 3', bx0 + 7, base - 41, COAL, 1.0) if False else None
    for i in range(4):
        cv.rect(bx0 + 8 + i * 4, base - 40, bx0 + 9 + i * 4, base - 38, COAL, 1.6)
    # l'aixeta (seca) i el llum (apagat)
    cv.rect(bx0 + 12, base - 18, bx0 + 16, base - 15, TIN, 4.6)
    cv.rect(bx0 + 12, base - 15, bx0 + 13, base - 12, TIN, 3.4)
    cv.rect(bx0 + 10, base - 22, bx0 + 18, base - 20, REDV, 3.0)                       # el volant de l'aixeta
    cv.disc(bx1 - 8, btop + 6, 2, 2, IRONF, 2.4)
    cv.disc(bx1 - 8, btop + 6, 1, 1, GREENL, 0.6, lit=0)
    # la corretja que hi falta: les politges, nues
    cv.disc(bx0 + 4, base - 34, 3, 3, IRONF, 3.4)
    cv.disc(bx0 + 4, base - 50, 2, 2, IRONF, 3.4)
    # el tub que entra a la paret de la fosa
    cv.rect(bx1 - 12, btop - 22, bx1 - 9, btop, IRONF, lambda x, y: 4.0 - (x - bx1 + 12) * 0.6)
    cv.rect(bx1 - 12, btop - 24, x1 + 4, btop - 21, IRONF, lambda x, y: 4.0 - (y - btop + 24) * 0.6)
    lector_condensador(cv)


LECTOR = (2, 8, 50, 38)         # el lector de targetes de Verne, cargolat al costat: x des de COND x1, y des de la base


def lector_condensador(cv, engegat=False):
    """El lector de targetes nou de trinca que Verne ha cargolat al costat del condensador: vermell, amb la
    pantalleta, la ranura i el llum (vermell; `engegat`: verd, amb la targeta blava de la Mosca a la ranura)."""
    x0, x1, base = COND
    lx0, lx1, ly0, ly1 = x1 + LECTOR[0], x1 + LECTOR[1], base - LECTOR[2], base - LECTOR[3]
    if not engegat:
        cv.rect(lx0, ly0, lx1, ly1, REDV, lambda x, y: 3.4 - (x - lx0) * 0.2 + (1.0 if y == ly0 else 0))
        cv.rect(lx0 + 1, ly0 + 2, lx1 - 1, ly0 + 4, BLACKT, 1.4, lit=0)                  # la pantalleta
        cv.rect(lx0 + 1, ly0 + 7, lx1 - 1, ly0 + 7, BLACKT, 0.4, lit=0)                  # la ranura
        for y in (ly0 + 1, ly1 - 1):                                                     # els cargols
            cv.flat(lx0, y, TIN[4])
    led = (120, 255, 140) if engegat else (255, 70, 50)
    cv.flat(lx1 - 1, ly1 - 2, led)
    cv.flat(lx0 + 2, ly0 + 3, (110, 230, 120) if engegat else (255, 60, 40))
    if engegat:
        cv.rect(lx0 + 1, ly0 + 7, lx1 - 1, ly0 + 10, BLUEV, lambda x, y: 2.8 + (1.0 if y == ly0 + 7 else 0), lit=0)
        cv.flat(lx1 - 2, ly0 + 9, WHITEV[5])                                             # (la targeta, a la ranura)


# ─── El piquet ─────────────────────────────────────────────────────────────

BANNER = (202, 304, 136, 164)


def pancarta(cv):
    x0, x1, y0, y1 = BANNER
    # els pals, clavats en dues galledes de sorra
    for px in (x0 - 2, x1 + 2):
        cv.rect(px - 1, y0 - 6, px + 1, 214, PLANKF, lambda x, y: 4.0 - (x - px + 1) * 0.9)
        cv.poly([(px - 6, 202), (px + 6, 202), (px + 5, 216), (px - 5, 216)], TIN,
                lambda x, y: 3.6 - (x - px) * 0.15 - (1.4 if y == 202 else 0))
        cv.disc(px, 203, 5.5, 1.5, COB, 3.0)
    # el llençol, amb arrugues i una mica de panxa
    for x in range(x0, x1 + 1):
        sag = math.sin((x - x0) / (x1 - x0) * math.pi) * 3
        for y in range(int(y0 + sag * 0.3), int(y1 + sag)):
            wr = math.sin((x - x0) * 0.35 + (y - y0) * 0.1) * 0.5
            cv.put(x, y, CLOTH, 4.0 + wr + (fbm(x / 6, y / 5, 71) - 0.5) * 0.8 - (0.8 if x in (x0, x1) else 0))
    cv.hline(x0, x1, y0, COAL, 1.6)
    # el lema de Verne, ratllat, i a sota el dels miners
    l1, l2 = 'QUI NO TREBALLA NO BEU', 'QUI NO BEU NO TREBALLA'
    w1, w2 = text_width(l1), text_width(l2)
    cx = (x0 + x1) // 2
    tx = cx - w1 // 2
    qtext(cv, l1, tx, y0 + 4, COAL, 1.2)
    for x in range(tx - 3, tx + w1 + 3):                                               # la ratlla, a pinzell
        yy = y0 + 6 + round(math.sin(x * 0.2) * 0.6 + (x - tx) * -0.012)
        if hr(x, 5) > 0.08:
            cv.put(x, yy, REDP, 3.4)
    tx2 = cx - w2 // 2
    qtext(cv, l2, tx2, y0 + 15, REDP, 3.2)
    # els degotalls de la pintura vermella
    for dx in (6, 31, 58, 77):
        for k in range(2 + int(hr(dx, 2) * 3)):
            cv.put(tx2 + dx, y0 + 20 + k, REDP, 3.0)


def bido(cv):
    """El bidó de la foguera: ferro rovellat, foradat, amb brases."""
    cx, base = BIDO
    for y in range(base - 24, base + 1):
        for x in range(cx - 9, cx + 10):
            u = (x - cx) / 9.5
            v = 3.0 - u * 1.0 + (fbm(x / 3, y / 5, 81) - 0.5) * 1.6 - abs(u) ** 4 * 1.4
            if (y - base + 24) in (5, 16):
                v += 1.0
            cv.put(x, y, RUSTF, v)
    for hx, hy in ((cx - 4, base - 10), (cx + 3, base - 12), (cx - 1, base - 6), (cx + 6, base - 7)):
        cv.rect(hx, hy, hx + 1, hy, FIREF, 4.8, lit=0)                                  # forats amb brasa
        cv.flat(hx + (1 if hx % 2 else 0), hy + 1, FIREF[3])
    cv.disc(cx, base - 24, 9.5, 2.5, COAL, 1.0, lit=0)
    for i in range(14):
        a = hr(i, 82) * 6.28
        cv.put(cx + math.cos(a) * 7 * hr(i, 83), base - 24 + math.sin(a) * 1.8 * hr(i, 84), FIREF, 3.6 + hr(i, 85) * 2,
               lit=0)
    cv.glow(cx, base - 26, 44, (255, 150, 60), 0.35)


def caixa(cv, x0, y0, x1, y1, seed=0):
    """Una caixa de fusta (de fruita, o de dinamita) per seure."""
    cv.rect(x0, y0, x1, y1, PLANKF, lambda x, y: 3.6 - (x - x0) * 0.03 - (1.4 if (y - y0) % 4 == 3 else 0) +
            (hr(x // 3, y // 4, seed) - 0.5) * 0.6)
    cv.rect(x0, y0, x1, y0, PLANKF, 5.2)
    cv.vline(x1, y0, y1, PLANKF, 1.6)


def canalla(cv):
    """La canalla del piquet, asseguda vora el foc (figures de fons)."""
    # criatures de 8–10 anys a la mida dels personatges (un adult fa ≈98): ≈0,7 d'alt, el cap gran i el cos prim
    kw = dict(cap=4.6, ample=0.085)
    caixa(cv, 214, 209, 234, 226, 1)
    persona_c(cv, 220, 226, h=68, facing=1, var=1, tipus='nen', seated=True, light_from=1, **kw)
    caixa(cv, 272, 211, 292, 228, 2)
    persona_c(cv, 286, 228, h=66, facing=-1, var=3, tipus='nena', seated=True, light_from=-1, hold='got', **kw)
    # una nena dreta, amb una garrafa buida, mirant la font (al carrer en 3D és a l'altra banda de la font, i la mira
    # cap a l'esquerra: així no tapa la pantalla)
    persona_c(cv, 308, 222, h=72, facing=-1, var=2, tipus='nena', light_from=-1, hold='bidon', **kw)


# ─── El terra, les ombres ──────────────────────────────────────────────────

def terra(cv):
    cobbles(cv, HOR, RH - 1, seed=5, base=3.0, vp=(248, HOR - 30))
    # la vorera de les façanes
    cv.rect(56, BASE, 640, BASE + 5, MORTAR, lambda x, y: 3.6 - (y - BASE) * 0.3 - (1.2 if x % 16 == 0 else 0))
    cv.rect(56, BASE + 6, 640, BASE + 6, COAL, 1.0)
    # pols de carbó i un toll sec
    cv.darken(0, 196, W - 1, RH - 1, lambda x, y: 0.4 if fbm(x / 26, y / 8, 91) > 0.62 else 0)
    # escombraries: paper, una llauna
    cv.rect(160, 238, 165, 240, CLOTH, 4.0)
    cv.disc(484, 246, 2, 1.5, TIN, 4.0)


def shadow(cv, cx, cy, rx, ry, k=0.85, skew=0.0):
    def f(x, y):
        nx = (x - cx - (cy - y) * skew) / rx
        ny = (y - cy) / ry
        return k if nx * nx + ny * ny <= 1 else 0
    cv.darken(cx - rx - 20, cy - ry - 2, cx + rx + 20, cy + ry + 2, f)


def ombres(cv):
    """Ombres llargues cap a la dreta: el sol és baix, a l'esquerra."""
    shadow(cv, FONT[0] + 18, FONT[1] + 1, 26, 4)
    shadow(cv, 438, 231, 28, 4)
    shadow(cv, 616, 231, 30, 4)
    shadow(cv, BIDO[0] + 12, BIDO[1] + 1, 16, 3)
    shadow(cv, 240, 228, 18, 3)
    shadow(cv, 292, 229, 18, 3)
    shadow(cv, 316, 223, 14, 2.5)
    shadow(cv, 214, 216, 12, 2.5)
    shadow(cv, 312, 216, 12, 2.5)


# ─── Composició ────────────────────────────────────────────────────────────

def bg(cv):
    sky_and_far(cv)
    terra(cv)
    sindicat(cv)
    cases(cv)
    fosa(cv)
    nau(cv)
    ombres(cv)
    pancarta(cv)
    panell(cv, 330, 100, 'VERNE', '▲')
    font_verne(cv, *FONT, alt=88, pantalla=True)
    pila_comptadors(cv, 402, 456, 230, 26, seed=3)
    bido(cv)
    canalla(cv)
    condensador(cv)
    cv.rect(0, RH, W - 1, H - 1, BLACKT, 0, lit=0)
    for y in range(RH, H):
        for x in range(W):
            cv.flat(x, y, (0, 0, 0))


# ─── Decorats ──────────────────────────────────────────────────────────────

def barril_piquet(cv):
    """L'últim barril de la Cantimplora, al piquet, amb gots de llauna a sobre."""
    cx, base = 322, 232
    shadow_k = Canvas(light=LIGHT, transparent=True)
    for y in range(base - 26, base + 1):
        for x in range(cx - 10, cx + 11):
            u = (x - cx) / 10.5
            bulge = 1 - ((y - base + 13) / 14) ** 2 * 0.08
            if abs(u) > bulge:
                continue
            v = 3.4 - u * 1.4 - abs(u) ** 4 * 1.2
            if (y - base + 26) in (3, 4, 22, 23):
                v = 4.4 - u * 1.2                                                      # els cèrcols
            cv.put(x, y, SAFE if (y - base + 26) in (11, 12, 13) else [(20, 24, 14)] + OLIVE[1:], v)
    cv.disc(cx, base - 26, 10, 2.5, OLIVE, lambda nx, ny: 4.2 - nx)
    cv.disc(cx + 3, base - 26, 1.6, 1, COAL, 1.0)                                       # el tap
    for gx in (cx - 6, cx - 1):                                                         # els gots
        cv.rect(gx, base - 32, gx + 3, base - 27, TIN, lambda x, y: 4.6 - (x - gx) * 0.5)
        cv.rect(gx, base - 32, gx + 3, base - 32, WATER, 3.6, lit=0)
    cv.rect(cx + 6, base - 13, cx + 9, base - 10, TIN, 4.4)                            # l'aixeta del barril
    text(cv, 'C', cx - 6, base - 20, COAL, 1.0)
    # l'ombra cap a la dreta
    for y in range(base - 1, base + 3):
        for x in range(cx - 6, cx + 30):
            if ((x - cx - 10) / 22) ** 2 + ((y - base - 1) / 2.5) ** 2 <= 1 and not cv.get(x, y)[3]:
                if 0.85 > B4[y & 3][x & 3]:
                    cv.flat(x, y, (30, 24, 24))


def condensador_arreglat(cv):
    """El condensador arreglat: el llum verd encès, la corretja posada i un toll sota l'aixeta."""
    x0, x1, base = COND
    btop = base - 74
    cv.disc(x1 - 8, btop + 6, 1.4, 1.4, GREENL, 4.4, lit=0)
    cv.flat(x1 - 9, btop + 5, GREENL[4])
    cv.glow(x1 - 8, btop + 6, 6, (120, 255, 140), 0.0)
    for y in range(btop + 2, btop + 11):                                                 # el halo, a mà
        for x in range(x1 - 13, x1 - 2):
            d = math.hypot(x - x1 + 8, y - btop - 6)
            if 2 < d < 5 and (x + y) % 2 == 0:
                cv.flat(x, y, (120, 200, 120))
    # la corretja nova (la de la font)
    cv.line(x0 + 1, base - 34, x0 + 2, base - 50, COAL, 1.0)
    cv.line(x0 + 7, base - 34, x0 + 6, base - 50, COAL, 1.0)
    # el lector, en verd, amb la targeta de la Mosca
    lector_condensador(cv, engegat=True)
    # l'aixeta oberta i el toll
    cv.rect(x0 + 12, base - 12, x0 + 13, base - 10, WATER, 3.4, lit=0)
    cv.disc(x0 + 13, base + 1, 7, 1.6, WATER, lambda nx, ny: 2.2 + nx * 0.6 - ny, lit=0)
    cv.flat(x0 + 10, base, WATER[4])


PROPS = {'barril_piquet': barril_piquet, 'condensador_arreglat': condensador_arreglat}


# ─── Animacions ─────────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv.img


def _frames_foc():
    """La foguera del bidó: flames que ballen i guspires que pugen."""
    cx, base = BIDO
    top = base - 24
    frames = []
    n = 8
    for f in range(n):
        img = Image.new('RGBA', (W * Canvas.S, H * Canvas.S), (0, 0, 0, 0))
        cv = Canvas(light=LIGHT, img=img)
        ph = f / n * 2 * math.pi
        for y in range(top - 22, top + 1):
            t = (top - y) / 22                                                          # 0 a baix, 1 a dalt
            for x in range(cx - 9, cx + 10):
                u = (x - cx) / 8.5
                sway = math.sin(ph + t * 4) * t * 0.35
                tongues = 0.55 + 0.45 * math.sin((u + sway) * 7 + ph * 2 + hr(f, 3))
                hgt = (1 - abs(u + sway) ** 1.6) * (0.55 + 0.5 * tongues)
                if t < hgt:
                    lvl = 6.4 - t / max(0.05, hgt) * 4.6 - abs(u) * 1.2
                    cv.put(x, y, FIREF, lvl, lit=0)
        for k in range(3):                                                             # guspires
            s = (f / n + k / 3) % 1
            sx = cx + math.sin(k * 2.1 + s * 6) * 5 + s * 8
            sy = top - 18 - s * 34
            cv.flat(sx, sy, FIREF[5] if s < 0.5 else FIREF[3])
        frames.append(img)
    return frames


def _frames_fum():
    """El fum de les xemeneies de les cases (estufes de carbó): puja i el vent l'estira cap a la dreta."""
    base = _base()
    src = [(cx, ct - 6, 3, 34) for cx, ct in CHIMNEYS]
    return _smoke_loop(base, src, 12)


def _smoke_loop(base, sources, n):
    """Fum en bucle: cada fotograma barreja dues fases del soroll perquè l'últim encaixi amb el primer."""
    frames = []
    S = base.load()
    s = base.width // W                                     # píxels reals per píxel de sala (l'art pot ser a 2×)
    for f in range(n):
        img = Image.new('RGBA', base.size, (0, 0, 0, 0))
        P = img.load()
        ph = f / n
        for sx, sy, sw, sh in sources:
            for Y in range(max(0, int(sy - sh)) * s, (int(sy) + 1) * s):
                y = (Y + 0.5) / s - 0.5                                                # coordenada de sala
                t = (sy - y) / sh
                if t > 1:                                                              # (a 2×, la fila de dalt de tot)
                    continue
                drift = t * t * sh * 0.8
                for X in range(int(sx - sw - 3) * s, int(sx + sw + drift + 12) * s):
                    if not (0 <= X < W * s and 0 <= Y < RH * s):
                        continue
                    x = (X + 0.5) / s - 0.5
                    u = (x - sx - drift) / (sw * (1 + t * 2.4))
                    if abs(u) > 1.2:
                        continue
                    shape = (1 - t) ** 1.1 * max(0.0, 1 - u * u)
                    na = fbm((x - drift * 0.4) / 6, (y + ph * 24) / 5, int(sx))
                    nb = fbm((x - drift * 0.4) / 6, (y + (ph - 1) * 24) / 5, int(sx))
                    nz = na * (1 - ph) + nb * ph
                    dens = shape * (0.4 + nz * 1.2)
                    if dens > 0.3 + B4[Y & 3][X & 3] * 0.45:
                        o = S[X, Y]
                        k = min(0.8, dens)
                        col = mix(o[:3], HAZE[min(len(HAZE) - 1, int(1 + nz * 4))], k)
                        P[X, Y] = col + (255,)
        frames.append(img)
    return frames


def _frames_goteig():
    """La gota de l'aixeta del condensador arreglat."""
    x0, x1, base = COND
    gx, gy = x0 + 12, base - 10
    frames = []
    n = 10
    for f in range(n):
        cv = Canvas(transparent=True)
        if f < 5:
            cv.flat(gx, gy + 1, WATER[3])
            if f >= 3:
                cv.flat(gx, gy + 2, WATER[4])
        elif f < 8:
            y = gy + 2 + (f - 4) ** 2 * 2
            if y < base:
                cv.flat(gx, y, WATER[4])
                cv.flat(gx, y - 1, WATER[2])
        else:
            for dx in (-2, 2) if f == 8 else (-3, 3):
                cv.flat(gx + dx, base, WATER[5])
        frames.append(cv.img)
    return frames


ANIMS = {'foc': {'frames': _frames_foc, 'frameDuration': 110},
         'fum': {'frames': _frames_fum, 'frameDuration': 160},
         'goteig': {'frames': _frames_goteig, 'frameDuration': 120}}


