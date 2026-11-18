"""
**El dibuix pla de sempre** de la sala (font de les textures de bcmu_escombraries.py, que és en 3D).

La sala d'escombraries del tercer pis del BCMU (Escenes 5 i 6, l'Iri) a 640×360: la composició de
hd/rooms/bcmu_escombraries.py ×4/3, dibuixada de nou. On van jubilar el Llibre Major.
  - el darrere de l'edifici de 1958 sense maquillatge: formigó pintat de gris amb brutícia, una franja de pintura
    verda d'hospital a baix, canonades al sostre i un fluorescent brut que fa la llum justa;
  - EL LLIBRE MAJOR: un mainframe gris de 1984, alt i ample com un armari, amb la placa «LLIBRE MAJOR · 1984»,
    una pantalla de fòsfor verd (la claror verda de tota la sala), una filera de llums, el teclat que pesa com una
    nevera i, a sota, el pany de llautó per a una clau grossa;
  - a l'esquerra, la porta del passadís; les bosses de paper triturat (confeti de secrets bancaris) i el conducte
    d'escombraries, amb la comporta;
  - a la dreta, l'estació del tub de 1958 (plena de pols) i el panell de control de NETA-3, amb la seva base de
    càrrega a terra.
Animacions: `llibre` (els llums del Llibre Major i el cursor), `fluorescent` (fa figa) i `gota` (de la canonada
vella a la taca d'humitat).
"""
import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)

import math

from hd.pix import Light, Canvas, W, H, hr
from hd.rooms.comu import obox, outline, cable, text, text_width, _diff, SHEET, CARD, YEL
from hd.rooms.bar_sala import STEELB, SLATE
from hd.rooms.pis_cuina import outline_poly
from hd.rooms.bcmu_escombraries import (WALLG, HOSP, MAIN, BEIGE, BAG, DOORG, REDL, AMBER, GREENL, STRIPE,  # noqa: F401
                                        DROP)
from hd640.rooms.bcmu import CONCB, DUST, BRASS, SCREENB, tub_station

Canvas1x = Canvas                                   # (a 1×, com la sala en 3D)

FLOOR_Y = 200
TUBE = (147, 5)              # el fluorescent brut
SCREEN = (336, 67, 432, 117)  # la pantalla del Llibre Major

LIGHT = Light(ambient=-0.7, vignette=(85, 48), floor_fade=(251, 37))
LIGHT.point(TUBE[0], TUBE[1] + 5, r=293, k=2.6, squash=0.9, power=1.5)  # el fluorescent brut
LIGHT.point(384, 93, r=200, k=1.8, squash=1.1, power=1.8)               # la pantalla del Llibre Major
LIGHT.point(547, 123, r=53, k=0.5, squash=1.0, power=2.0)               # el panell de NETA-3


def text2(cv, s, x, y, col):
    """La font petita a 2× (blocs de 2×2): els rètols, perquè a la sala en 3D, en escorç, encara es llegeixin."""
    from hd.rooms.comu import _glyph
    cx = x
    for ch in s:
        g, top = _glyph(ch)
        if ch == 'N':
            g = ['10001', '11001', '10101', '10011', '10001']   # (la N de 4 px, a 2× i en escorç, semblava una M)
        for j, row in enumerate(g, start=top):
            for i, bit in enumerate(row):
                if bit == '1':
                    for dx in (0, 1):
                        for dy in (0, 1):
                            cv.flat(cx + 2 * i + dx, y + 2 * j + dy, col)
        cx += 2 * (len(g[0]) + 1)
    return 2 * text_width(s) + 2 * s.count('N') + 1


def green_cast(x, y):
    """Quant tenyeix de verd la pantalla del Llibre Major (0..1)."""
    d = math.hypot((x - 384) / 1.3, y - 93)
    return max(0.0, 1 - d / 200) ** 2


# ─── Paret, sostre, terra ──────────────────────────────────────────────────

def wall(cv):
    """Formigó pintat de gris, a panells, amb regalims; a baix, una franja de verd d'hospital rascada."""
    for y in range(0, FLOOR_Y):
        for x in range(W):
            panel = x // 80
            joint = (x % 80 == 79) or (y % 67 == 66)
            lit_edge = 0.5 if (x % 80 == 0) or (y % 67 == 0) else 0          # el cantell del panell, a la llum
            n = (hr(x // 2, y // 2, 3) - 0.5) * 0.35 + (hr(panel, y // 67, 8) - 0.5) * 0.4 + (hr(x, y, 4) - 0.5) * 0.1
            drip = 0.5 if hr(x // 4, 11) > 0.92 and y > 27 + hr(x // 4, 12) * 53 else 0
            drip += 0.3 if hr(x // 4, 11) > 0.92 and hr(x // 4, 13) > 0.5 and (x % 4 == 1) else 0
            if y >= 149:
                scratch = 0.7 if hr(x // 6, y // 3, 21) > 0.93 else 0
                cv.put(x, y, HOSP, (1.8 if joint else 3.0 + n + lit_edge) + scratch)
            else:
                cv.put(x, y, WALLG, (2.4 if joint else 3.6 + n + lit_edge) - drip)
    for px in range(0, W, 80):                                         # els forats dels encofrats
        for py in (0, 67):
            for hx, hy in ((14, 16), (65, 16), (14, 50), (65, 50)):
                if hr(px, py, hx + hy, 22) > 0.35:
                    cv.flat(px + hx, py + hy, WALLG[1])
                    cv.flat(px + hx + 1, py + hy + 1, WALLG[5])
    cv.rect(0, 147, W - 1, 148, WALLG, 2.0)                             # el filet entre el gris i el verd
    cv.hline(0, W - 1, 146, WALLG, 4.2)
    cv.rect(0, FLOOR_Y - 4, W - 1, FLOOR_Y - 1, CONCB, 2.0)
    cv.hline(0, W - 1, FLOOR_Y - 4, CONCB, 2.8)
    cv.hline(0, W - 1, FLOOR_Y, CONCB, 0)


def ceiling(cv, tube=1.0):
    """Canonades i una safata de cables, i el fluorescent brut, amb mosques mortes a la tapa.

    `tube`: com d'encès és el fluorescent (1 = normal; per a l'animació `fluorescent`, que fa figa)."""
    cv.rect(0, 0, W - 1, 4, CONCB, 2.4)
    cv.rect(0, 19, W - 1, 24, STEELB, lambda x, y: 2.8 + (1.4 if y == 20 else 0) - (1.0 if y == 24 else 0))
    for x in range(0, W, 5):                                           # la safata és de reixeta
        cv.put(x, 22, STEELB, 1.6)
    for bx in range(27, W, 107):
        cv.rect(bx, 16, bx + 3, 25, STEELB, lambda x, y, bx=bx: 1.8 + (0.8 if x == bx else 0))
    cv.rect(0, 29, 307, 32, DUST, lambda x, y: 2.6 + (0.8 if y == 29 else 0) - (0.6 if y == 32 else 0))   # una canonada vella
    cv.rect(304, 29, 309, 45, DUST, lambda x, y: 2.4 + (0.6 if x == 304 else 0))
    cv.rect(302, 43, 311, 45, DUST, 2.8)                                # la brida
    for bx in (60, 180):                                                # les abraçadores i un tros d'òxid
        cv.rect(bx, 28, bx + 2, 33, STEELB, 2.4)
    cv.darken(282, 30, 296, 32, 0.3)                                    # l'humitat, on goteja
    # el fluorescent
    x0, x1 = TUBE[0] - 53, TUBE[0] + 53
    obox(cv, x0 - 5, 3, x1 + 5, 11, STEELB, 2.6)
    on = [tuple(round(c * (0.35 + 0.65 * tube)) for c in (214, 226, 200))]
    cv.hline(x0, x1, 8, on, 0, lit=0)
    cv.hline(x0 + 1, x1 - 1, 7, [tuple(round(c * 0.8) for c in on[0])], 0, lit=0)
    for ex in (x0 - 2, x1 + 2):
        cv.vline(ex, 6, 9, STEELB, 1.6)
    for i in range(7):
        fx = x0 + 10 + int(hr(i, 9) * 86)
        cv.flat(fx, 8, (60, 60, 50))                                    # mosques mortes
        if i % 2:
            cv.flat(fx + 1, 8, (80, 80, 66))
    if tube > 0.5:
        cv.glow(TUBE[0], 11, 40, (220, 232, 200), 0.22 * tube)


def floor(cv):
    """Ciment amb taques, paperets triturats escampats i un desguàs."""
    for y in range(FLOOR_Y + 1, H):
        dep = (y - FLOOR_Y) / (H - FLOOR_Y)
        for x in range(W):
            u = (x - W / 2) / (1 + dep * 0.6) + W / 2
            n = (hr(x // 3, y // 2, 5) - 0.5) * 0.5 + (hr(int(u) // 53, (y - FLOOR_Y) // 13, 6) - 0.5) * 0.5 \
                + (hr(x, y, 7) - 0.5) * 0.12
            cv.put(x, y, CONCB, 3.6 + n)
    for cx, cy, rx, ry in ((267, 229, 29, 5), (507, 253, 40, 7), (80, 261, 21, 4)):
        cv.disc(cx, cy, rx, ry, CONCB, lambda nx, ny: 2.4 + (nx * nx + ny * ny) * 0.8)
    cv.put(258, 228, CONCB, 4.6)                                        # la brillantor de l'aigua a la taca
    cv.put(259, 228, CONCB, 4.2)
    # confeti de paper triturat
    for i in range(95):
        x = 80 + int(hr(i, 31) * 267)
        y = FLOOR_Y + 5 + int(hr(i, 32) ** 1.6 * 53)
        cv.put(x, y, SHEET, 4.0 + hr(i, 33))
        if hr(i, 34) > 0.5:
            cv.put(x + 1, y, SHEET, 3.6)
        if hr(i, 35) > 0.8:
            cv.put(x + 2, y + 1, SHEET, 3.2)
    # el desguàs
    gx, gy = 267, 245
    cv.disc(gx, gy, 12, 4, SLATE, 0.8)
    for i in range(-8, 9, 4):
        cv.vline(gx + i, gy - 3, gy + 3, STEELB, 3.0)
        cv.put(gx + i, gy - 3, STEELB, 4.2)
    # la claror verda de la pantalla, estesa pel terra davant del Llibre Major
    cv.tint(267, 203, 507, 272, (60, 255, 140),
            lambda x, y: 0.12 * max(0, 1 - abs(x - 384) / 120) * max(0, 1 - (y - 203) / 67))


# ─── Esquerra: la porta, les bosses, el conducte ───────────────────────────

def door(cv):
    """La porta del passadís: xapa grisa, una finestreta amb reixeta i el rètol de NETEJA."""
    x0, y0, x1, y1 = 19, 67, 80, FLOOR_Y
    obox(cv, x0 - 5, y0 - 5, x1 + 5, y1, STEELB, 2.4)
    cv.hline(x0 - 4, x1 + 4, y0 - 4, STEELB, 3.4)
    obox(cv, x0, y0, x1, y1, DOORG, 3.4, top=0.6)
    cv.rect(x0 + 5, y1 - 29, x1 - 5, y1 - 5, DOORG, 2.8)                # la placa de les puntades de peu
    outline(cv, x0 + 5, y1 - 29, x1 - 5, y1 - 5, DOORG)
    for k in range(3):
        cv.line(x0 + 11 + k * 15, y1 - 24, x0 + 16 + k * 15, y1 - 13, DOORG, 1.8)
        cv.line(x0 + 12 + k * 15, y1 - 24, x0 + 17 + k * 15, y1 - 13, DOORG, 3.6)
    # la finestreta, amb vidre armat: la claror del passadís
    obox(cv, x0 + 16, y0 + 13, x1 - 16, y0 + 45, STEELB, 3.0)
    cv.rect(x0 + 18, y0 + 15, x1 - 18, y0 + 43, [(120, 140, 130), (170, 190, 176), (210, 226, 214)],
            lambda x, y: 1.2 - (y - y0 - 15) * 0.022 + (0.5 if (x - y) % 13 == 0 else 0), lit=0)
    for yy in range(y0 + 18, y0 + 43, 5):
        cv.hline(x0 + 18, x1 - 18, yy, STEELB, 2.4, lit=0)
    for xx in range(x0 + 21, x1 - 17, 5):
        cv.vline(xx, y0 + 15, y0 + 43, STEELB, 2.4, lit=0)
    # la maneta
    obox(cv, x1 - 8, 131, x1 - 3, 144, STEELB, 3.4)
    cv.rect(x1 - 16, 136, x1 - 3, 138, STEELB, lambda x, y: 4.2 + (0.8 if y == 136 else 0))
    cv.put(x1 - 6, 141, STEELB, 0.6)                                    # el forat del pany
    # les frontisses
    for hy in (y0 + 10, y1 - 24):
        cv.rect(x0 - 2, hy, x0, hy + 8, STEELB, 3.6)
    obox(cv, x0 + 8, y0 + 53, x1 - 8, y0 + 64, YEL, 3.0)
    w = text_width('NETEJA')
    text(cv, 'NETEJA', (x0 + x1) // 2 - w // 2, y0 + 56, [(30, 22, 6)], 0, flat=(30, 22, 6))
    cv.darken(x1 + 6, y0, x1 + 12, y1, 0.4)


def chute(cv):
    """El conducte d'escombraries: una boca d'acer encastada a la paret, amb la comporta abatible i el rètol."""
    x0, y0, x1, y1 = 213, 67, 280, 173
    # el tub que puja per la paret fins al sostre
    cv.rect(229, 25, 264, y0, STEELB, lambda x, y: 2.6 + (1.2 if x == 233 else 0) + (0.5 if x == 234 else 0) - (1.2 if x >= 261 else 0))
    for yy in (37, 53):
        cv.rect(227, yy, 266, yy + 3, STEELB, lambda x, y, yy=yy: 3.4 + (0.8 if y == yy else 0) - (0.8 if y == yy + 3 else 0))
        for rx in range(231, 264, 8):
            cv.put(rx, yy + 1, STEELB, 5.0)
    obox(cv, x0, y0, x1, y1, STEELB, 3.0, top=1.0)
    for (rx, ry) in ((x0 + 4, y0 + 4), (x1 - 4, y0 + 4), (x0 + 4, y1 - 4), (x1 - 4, y1 - 4),
                     ((x0 + x1) // 2, y1 - 4), (x0 + 4, (y0 + y1) // 2), (x1 - 4, (y0 + y1) // 2)):
        cv.flat(rx, ry, (190, 196, 200))
        cv.flat(rx + 1, ry + 1, (40, 44, 48))
    # la comporta, inclinada (la part de dalt més fosca, la de baix, el tirador)
    hx0, hy0, hx1, hy1 = x0 + 9, y0 + 24, x1 - 9, y1 - 19
    cv.rect(hx0, hy0, hx1, hy1, STEELB, lambda x, y: 2.0 + (y - hy0) / (hy1 - hy0) * 2.2)
    outline(cv, hx0, hy0, hx1, hy1, STEELB)
    cv.rect(hx0, hy0, hx1, hy0 + 2, STEELB, lambda x, y: 4.6 - (y - hy0) * 0.6)   # la frontissa
    for kx in range(hx0 + 4, hx1 - 2, 9):
        cv.vline(kx, hy0, hy0 + 2, STEELB, 1.6)
    hx = (hx0 + hx1) // 2
    obox(cv, hx - 12, hy1 - 8, hx + 12, hy1 - 4, STEELB, 4.2)
    cv.hline(hx - 11, hx + 11, hy1 - 5, STEELB, 2.4)
    # rascades i una taca de cafè que regalima
    for i in range(9):
        sx = hx0 + 4 + int(hr(i, 41) * (hx1 - hx0 - 9))
        sy = hy0 + 6 + int(hr(i, 42) * (hy1 - hy0 - 14))
        cv.line(sx, sy, sx + 5, sy + 1, STEELB, 4.4)
    cv.rect(x1 - 19, y1 - 2, x1 - 16, y1 + 10, CARD, lambda x, y: 1.6 + (0.4 if x == x1 - 19 else 0))
    cv.put(x1 - 18, y1 + 11, CARD, 1.4)
    cv.put(x1 - 17, y1 + 13, CARD, 1.2)
    # el rètol
    w = text_width('ESCOMBRARIES')
    cx = (x0 + x1) // 2
    obox(cv, cx - w // 2 - 5, y0 + 5, cx + w - w // 2 + 4, y0 + 17, YEL, 3.2)
    text(cv, 'ESCOMBRARIES', cx - w // 2, y0 + 8, [(30, 22, 6)], 0, flat=(30, 22, 6))
    cv.darken(x1 + 1, y0 + 3, x1 + 5, y1, 0.4)


def bags(cv):
    """Les bosses de paper triturat: negres, panxudes, una d'esventrada amb el confeti a fora."""
    def bag(cx, cy, rx, ry, seed, burst=False):
        cv.disc(cx, cy, rx, ry, BAG, lambda nx, ny: 2.8 - ny * 1.2 - nx * 0.5 + (0.9 if (nx * 3 + ny * 5 + seed) % 1.0 < 0.06 else 0))
        # els plecs del plàstic, que baixen del nus
        for k in (-1, 1):
            for t in range(ry):
                px = cx + k * round(t * 0.35 * rx / ry) + k * 2
                py = cy - ry + 2 + t
                cv.put(px, py, BAG, 1.6)
        # el nus, a dalt
        cv.poly([(cx - 4, cy - ry + 1), (cx + 4, cy - ry + 1), (cx + 1, cy - ry - 5), (cx - 1, cy - ry - 5)], BAG, 3.0)
        cv.line(cx - 2, cy - ry - 6, cx - 5, cy - ry - 11, BAG, 3.2)
        cv.line(cx + 1, cy - ry - 6, cx + 5, cy - ry - 9, BAG, 3.2)
        cv.put(cx - 5, cy - ry - 11, BAG, 4.4)
        for a in range(0, 360, 3):                                     # contorn
            px = round(cx + math.cos(math.radians(a)) * (rx + 0.5))
            py = round(cy + math.sin(math.radians(a)) * (ry + 0.5))
            cv.flat(px, py, BAG[0])
        # els reflexos del plàstic
        for i in range(5):
            hx = cx - rx // 2 + int(hr(seed, i, 1) * rx)
            hy = cy - ry // 2 + int(hr(seed, i, 2) * ry // 2)
            cv.line(hx, hy, hx + 3, hy + 4, BAG, 5.0)
            cv.put(hx, hy, BAG, 5.6)
        if burst:
            ox, oy = cx + rx // 3, cy + ry // 4                        # l'esquinç, i les tires de paper que en surten
            cv.disc(ox, oy, 5, 3.2, BAG, 0.4)
            for i in range(24):
                a = hr(seed, i, 7) * math.pi * 0.8
                ln = 3 + int(hr(seed, i, 8) * 9)
                x, y = ox + int((hr(seed, i, 9) - 0.5) * 8), oy
                for k in range(ln):
                    cv.put(x + round(math.cos(a) * k), y + round(math.sin(a) * k * 0.6) + k // 3, SHEET, 3.0 + hr(i, k) * 1.4)
                if hr(seed, i, 10) > 0.7:                              # alguna tira amb tinta
                    cv.put(x + round(math.cos(a) * (ln // 2)), y + round(math.sin(a) * (ln // 2) * 0.6) + ln // 6,
                           [(60, 70, 110)], 0)
    bag(112, 192, 19, 15, 1)
    bag(184, 195, 17, 13, 3)
    bag(147, 187, 23, 19, 2, burst=True)
    bag(128, 167, 15, 12, 4)
    bag(165, 165, 13, 12, 5)
    # el confeti escampat de la bossa esventrada
    for i in range(55):
        x = 149 + int((hr(i, 51) - 0.3) * 53)
        y = 200 + int(hr(i, 52) * 9)
        cv.put(x, y, SHEET, 4.2 + hr(i, 53))
    cv.darken(91, 203, 208, 209, 0.5)


# ─── El Llibre Major ───────────────────────────────────────────────────────

def ledger(cv):
    """El Llibre Major: un mainframe gris de 1984. La peça protagonista de la sala."""
    x0, y0, x1, y1 = 315, 48, 453, FLOOR_Y
    # l'ombra a terra i a la paret
    cv.darken(x1 + 1, y0 + 5, x1 + 9, y1, 0.45)
    cv.darken(x0 - 3, y1 + 1, x1 + 11, y1 + 5, 0.55)
    # el moble: un armari gris, amb el sòcol negre i els laterals més foscos
    obox(cv, x0, y0, x1, y1, MAIN, 5.0, top=1.2)
    cv.rect(x0 + 1, y0 + 17, x1 - 1, y0 + 19, [(20, 30, 70), (40, 60, 130), (70, 100, 180)], lambda x, y: 1.4 + (0.6 if y == y0 + 17 else 0))
    cv.rect(x0 + 1, y0 + 1, x0 + 5, y1 - 1, MAIN, lambda x, y: 3.0 + (0.6 if x == x0 + 1 else 0))
    cv.rect(x1 - 5, y0 + 1, x1 - 1, y1 - 1, MAIN, 2.6)
    cv.rect(x0 + 1, y1 - 7, x1 - 1, y1 - 1, MAIN, 1.2)
    cv.hline(x0 + 1, x1 - 1, y1 - 7, MAIN, 2.2)
    for fx in (x0 + 8, x1 - 8):                                        # els peus anivelladors
        cv.rect(fx - 2, y1 - 1, fx + 2, y1, MAIN, 0.6)
    # la placa de dalt: LLIBRE MAJOR · 1984, en llautó
    obox(cv, x0 + 11, y0 + 1, x1 - 11, y0 + 16, BRASS, 4.4)
    cv.hline(x0 + 12, x1 - 12, y0 + 2, BRASS, 5.4)
    s = 'LLIBRE MAJOR'
    text2(cv, s, (x0 + x1) // 2 - text_width(s), y0 + 4, (40, 26, 8))
    for rx in (x0 + 14, x1 - 14):
        cv.flat(rx, y0 + 7, BRASS[5])
        cv.flat(rx + 1, y0 + 8, BRASS[1])
    # la pantalla de fòsfor verd, amb el bisell beix
    sx0, sy0, sx1, sy1 = SCREEN
    obox(cv, sx0 - 8, sy0 - 6, sx1 + 8, sy1 + 7, BEIGE, 4.0, top=1.0)
    cv.rect(sx0 - 3, sy0 - 3, sx1 + 3, sy1 + 3, BEIGE, lambda x, y: 2.0 + (0.6 if y >= sy1 + 2 or x >= sx1 + 2 else 0))
    screen(cv)
    # els botons de la pantalla (lluminositat, contrast) i la reixeta de l'altaveu
    for i in range(2):
        cv.disc(sx1 + 3 - i * 9, sy1 + 5, 1.8, 1.8, MAIN, lambda nx, ny: 2.6 - nx - ny)
    for i in range(3):
        cv.hline(sx0, sx0 + 19, sy1 + 3 + i * 2, BEIGE, 2.2)
    cv.hline(sx0 + 24, sx0 + 40, sy1 + 5, BEIGE, 2.8)                   # el nom del model, gravat
    # la filera de llums d'estat
    leds(cv, frame=0)
    # el teclat que pesa com una nevera, sobre una lleixa que surt del moble
    ky0 = 141
    top = [(x0 - 3, ky0 + 5), (x1 + 3, ky0 + 5), (x1 - 3, ky0 - 3), (x0 + 3, ky0 - 3)]
    cv.poly(top, BEIGE, lambda x, y: 3.2 + (y - ky0 + 3) * 0.08)
    outline_poly(cv, top, BEIGE)
    cv.rect(x0 - 3, ky0 + 6, x1 + 3, ky0 + 12, BEIGE, lambda x, y: 2.2 + (0.6 if y == ky0 + 6 else 0))
    outline(cv, x0 - 3, ky0 + 6, x1 + 3, ky0 + 12, BEIGE)
    for row in range(4):                                               # les tecles, quatre files en perspectiva
        yy = ky0 - 2 + row * 2
        for i in range(30):
            kx = x0 + 8 + i * 4 + row
            if kx + 2 > x1 - 24:
                break
            special = (row == 3 and 8 <= i <= 18)
            if special:
                continue
            cv.hline(kx, kx + 2, yy, BEIGE, 5.0)
            cv.put(kx + 2, yy, BEIGE, 3.6)
    cv.rect(x0 + 48, ky0 + 4, x0 + 88, ky0 + 4, BEIGE, 5.2)            # la barra d'espai
    for i in range(3):                                                 # el teclat numèric, a part
        for j in range(4):
            cv.hline(x1 - 20 + i * 4, x1 - 19 + i * 4, ky0 - 2 + j * 2, MAIN, 4.0)
    cv.rect(x1 - 22, ky0 + 2, x1 - 11, ky0 + 4, [(120, 30, 26), (180, 50, 40), (230, 90, 70)],
            lambda x, y: 1.4 + (0.6 if y == ky0 + 2 else 0))           # la tecla vermella (EXECUTAR)
    # sota la lleixa: el panell de serveis, amb el pany de llautó per a la clau grossa
    px0, py0, px1, py1 = x0 + 13, ky0 + 19, x1 - 13, y1 - 12
    obox(cv, px0, py0, px1, py1, MAIN, 3.6, top=0.4)
    for rx, ry in ((px0 + 2, py0 + 2), (px1 - 2, py0 + 2), (px0 + 2, py1 - 2), (px1 - 2, py1 - 2)):
        cv.put(rx, ry, MAIN, 6.0)
    lock(cv, (x0 + x1) // 2, 172)
    # la reixeta de ventilació, a la dreta del pany
    side = px1 - 35
    for k in range(8):
        cv.hline(side, side + 27, py0 + 6 + k * 3, MAIN, 1.8)
        cv.hline(side, side + 27, py0 + 7 + k * 3, MAIN, 4.6)
    # un adhesiu groc vell de «NO TOCAR», amb les cantonades aixecades
    sx, sy = px0 + 7, py0 + 6
    obox(cv, sx, sy, sx + 31, sy + 17, YEL, 2.6)
    cv.put(sx + 31, sy, MAIN, 3.6)
    cv.put(sx + 30, sy + 1, YEL, 4.0)
    text(cv, 'NO', sx + 16 - text_width('NO') // 2, sy + 3, [(40, 26, 6)], 0, flat=(40, 26, 6))
    text(cv, 'TOCAR', sx + 16 - text_width('TOCAR') // 2, sy + 10, [(40, 26, 6)], 0, flat=(40, 26, 6))
    # el cable gruixut que surt de darrere i va a la paret
    cable(cv, [(x0 + 5, y1 - 4), (x0 - 11, y1 + 3), (x0 - 27, y1 - 1), (x0 - 32, 157)], SLATE, 1.6, thick=3)
    cv.rect(x0 - 36, 151, x0 - 28, 159, SLATE, 3.0)                     # l'endoll de la paret
    outline(cv, x0 - 36, 151, x0 - 28, 159, SLATE)
    # la pols damunt del moble
    for i in range(55):
        cv.put(x0 + 2 + int(hr(i, 61) * (x1 - x0 - 4)), y0 + 1 + int(hr(i, 62) * 3), DUST, 3.6)
    # el verd de la pantalla que tenyeix el frontal del moble
    cv.tint(x0, y0, x1, y1, (80, 255, 150), lambda x, y: 0.10 * green_cast(x, y))


def screen(cv, cursor=True, frame=0):
    """La pantalla: fòsfor verd amb línies d'escaneig; el menú del sistema i el cursor."""
    sx0, sy0, sx1, sy1 = SCREEN
    for y in range(sy0, sy1 + 1):
        for x in range(sx0, sx1 + 1):
            nx = (x - (sx0 + sx1) / 2) / ((sx1 - sx0) / 2)
            ny = (y - (sy0 + sy1) / 2) / ((sy1 - sy0) / 2)
            vig = (nx * nx + ny * ny) * 0.9
            cv.put(x, y, SCREENB, 1.6 - vig - (0.4 if y % 2 else 0), lit=0)
    ink = (150, 255, 170)
    lines = ['LLIBRE MAJOR', 'COMPTES:', '8.104.229.551', 'EN ESPERA', '>']
    for i, s in enumerate(lines):
        text(cv, s, sx0 + 4, sy0 + 4 + i * 9, [ink], 0, lit=0, flat=ink if i in (0, 3, 4) else (90, 210, 120))
    cv.hline(sx0 + 4, sx0 + 4 + text_width('LLIBRE MAJOR'), sy0 + 11, [ink], 0, lit=0)
    # la data, a la dreta de la capçalera
    text(cv, '1984', sx1 - 3 - text_width('1984'), sy0 + 4, [(70, 170, 100)], 0, lit=0, flat=(70, 170, 100))
    if cursor:
        cx, cy = CURSOR
        cv.rect(cx, cy, cx + 3, cy + 5, [ink], 0, lit=0)
    cv.glow((sx0 + sx1) // 2, (sy0 + sy1) // 2, 61, (80, 255, 140), 0.18)
    # el reflex corbat del vidre
    cv.tint(sx0 + 3, sy0 + 1, sx0 + 29, sy0 + 8, (220, 255, 230), 0.18)
    cv.tint(sx1 - 6, sy1 - 10, sx1 - 2, sy1 - 2, (220, 255, 230), 0.08)


CURSOR = (SCREEN[0] + 4 + text_width('>') + 2, SCREEN[1] + 4 + 4 * 9)
LED_X = list(range(333, 440, 8))
LED_COLS = [REDL, AMBER, GREENL]


def leds(cv, frame=0):
    """La filera de llums d'estat, sota la pantalla: la majoria verds, algun ambre, un vermell que no vol dir res."""
    y = 131
    cv.rect(LED_X[0] - 5, y - 4, LED_X[-1] + 7, y + 4, MAIN, 1.6)
    outline(cv, LED_X[0] - 5, y - 4, LED_X[-1] + 7, y + 4, MAIN)
    for i, x in enumerate(LED_X):
        kind = 2 if hr(i, 70) < 0.7 else (1 if hr(i, 71) < 0.7 else 0)
        on = hr(i, frame, 72) > (0.25 if kind == 2 else 0.5)
        ramp = LED_COLS[kind]
        cv.rect(x, y - 1, x + 3, y + 1, ramp, 2.6 if on else 0.6, lit=0)
        if on:
            cv.flat(x, y - 1, ramp[3])
            cv.flat(x + 1, y - 1, ramp[3])
            cv.glow(x + 1, y, 4, ramp[2], 0.2)


def lock(cv, cx, cy):
    """El pany: un escut de llautó gros, rodó, amb el forat d'una clau antiga (de les grosses)."""
    cv.disc(cx, cy, 11, 11, BRASS, lambda nx, ny: 4.0 - nx * 0.8 - ny * 1.2)
    cv.ring(cx, cy, 11, BRASS, 1.4, step=2)
    cv.disc(cx, cy, 8, 8, BRASS, lambda nx, ny: 3.0 + nx * 0.6 + ny * 0.6)
    cv.ring(cx, cy, 8, BRASS, 4.6, step=4)
    cv.disc(cx, cy - 3, 2.4, 2.4, [(6, 4, 2)], 0, lit=0)
    cv.poly([(cx - 1, cy - 2), (cx + 1, cy - 2), (cx + 3, cy + 5), (cx - 3, cy + 5)], [(6, 4, 2)], 0, lit=0)
    for (rx, ry) in ((cx - 8, cy - 8), (cx + 8, cy - 8), (cx - 8, cy + 8), (cx + 8, cy + 8)):
        cv.flat(rx, ry, BRASS[5])
        cv.flat(rx + 1, ry + 1, BRASS[1])
    cv.glow(cx - 3, cy - 4, 7, (255, 240, 180), 0.25)


# ─── Dreta: l'estació del tub i el panell de NETA-3 ────────────────────────

def neta_panel(cv):
    """El panell de control de NETA-3 a la paret: una caixa gris amb una pantalleta, botons i l'horari enganxat."""
    x0, y0, x1, y1 = 520, 93, 565, 147
    obox(cv, x0, y0, x1, y1, MAIN, 3.8, top=1.0)
    obox(cv, x0 + 3, y0 + 3, x1 - 3, y0 + 12, YEL, 3.0)
    w = text_width('NETA-3')
    text(cv, 'NETA-3', (x0 + x1) // 2 - w // 2, y0 + 5, [(30, 22, 6)], 0, flat=(30, 22, 6))
    # la pantalleta: «HORARI: SEMPRE»
    cv.rect(x0 + 4, y0 + 16, x1 - 4, y0 + 29, [(10, 30, 40), (30, 90, 110), (90, 200, 220)], 0.8, lit=0)
    outline(cv, x0 + 4, y0 + 16, x1 - 4, y0 + 29, MAIN)
    w = text_width('SEMPRE')
    text(cv, 'SEMPRE', (x0 + x1) // 2 - w // 2, y0 + 20, [(120, 230, 240)], 0, lit=0, flat=(120, 230, 240))
    cv.glow((x0 + x1) // 2, y0 + 22, 12, (90, 200, 220), 0.12)
    # el teclat petit
    for i in range(6):
        kx = x0 + 9 + (i % 3) * 9
        ky = y0 + 34 + (i // 3) * 8
        obox(cv, kx, ky, kx + 5, ky + 4, MAIN, 5.0)
    cv.flat(x1 - 5, y1 - 5, GREENL[3])
    cv.glow(x1 - 5, y1 - 5, 5, (120, 255, 160), 0.4)
    # el cable fins a la base de càrrega, a terra
    cable(cv, [(x1 - 8, y1), (x1 - 3, 171), (x1 + 19, 187), (584, 203)], SLATE, 1.6, thick=2)


def dock(cv):
    """La base de càrrega de NETA-3: una placa amb franges grogues i negres i dos contactes de coure."""
    x0, x1, y = 565, 627, 208
    plate = [(x0, y + 8), (x1, y + 8), (x1 - 5, y - 3), (x0 + 5, y - 3)]
    cv.poly(plate, STRIPE, lambda x, yy: 2.6 if ((x + yy) // 5) % 2 else 0.4)
    outline_poly(cv, plate, STRIPE)
    cv.rect(x0 + 2, y + 9, x1 - 2, y + 11, STRIPE, 0.6)
    obox(cv, 587, 187, 605, y - 3, MAIN, 3.2, top=0.8)                  # el pal dels contactes
    for cx in (592, 600):
        cv.rect(cx, 195, cx + 1, 200, [(80, 40, 20), (190, 110, 50), (240, 170, 100)], lambda x, yy, cx=cx: 1.6 + (0.8 if x == cx else 0))
    cv.flat(596, 191, GREENL[2])
    cv.glow(596, 191, 3, (120, 255, 160), 0.3)
    cv.darken(x0, y + 12, x1 + 3, y + 15, 0.5)


def boxes(cv):
    """Caixes d'arxiu velles apilades a la dreta del tot («ARXIU 1987-1991»), amb pols."""
    for i, (bx0, by0) in enumerate(((576, 144), (592, 115), (573, 85))):
        obox(cv, bx0, by0, bx0 + 53, by0 + 29, CARD, 3.0 - i * 0.2)
        cv.hline(bx0 + 1, bx0 + 52, by0 + 4, CARD, 2.4)                 # la tapa
        obox(cv, bx0 + 16, by0 + 9, bx0 + 37, by0 + 20, SHEET, 4.2)
        cv.rect(bx0 + 18, by0 + 12, bx0 + 35, by0 + 12, SLATE, 1.6)
        cv.rect(bx0 + 18, by0 + 15, bx0 + 29, by0 + 15, SLATE, 1.6)
        cv.rect(bx0 + 18, by0 + 17, bx0 + 32, by0 + 17, SLATE, 2.2)
        cv.rect(bx0 + 4, by0 + 21, bx0 + 9, by0 + 24, CARD, 1.2)          # la nansa
        for k in range(11):
            cv.put(bx0 + 2 + int(hr(i, k, 81) * 48), by0 + 1 + (k % 2), DUST, 3.8)
    cv.darken(573, 175, 632, 177, 0.5)


def wall_bits(cv):
    """El rètol de damunt les bosses (amb la fletxa avall) i un rellotge de paret que s'ha aturat a les deu i deu."""
    w = 2 * text_width('CONFIDENCIAL') + 1
    x0, y0 = 147 - w // 2 - 5, 92
    obox(cv, x0, y0, x0 + w + 9, y0 + 17, [(40, 6, 8), (90, 14, 16), (150, 26, 26), (196, 44, 38)], 2.8)
    text2(cv, 'CONFIDENCIAL', x0 + 5, y0 + 4, (250, 240, 230))
    y0 += 4
    for k in range(7):                                                 # la fletxa
        cv.hline(147 - k, 147 + k, y0 + 27 - k, [(90, 14, 16), (150, 26, 26), (196, 44, 38)], 1.6 + (0.6 if k == 6 else 0))
    cv.rect(145, y0 + 16, 149, y0 + 20, [(90, 14, 16), (150, 26, 26), (196, 44, 38)], 1.6)
    # el rellotge
    cx, cy = 147, 53
    cv.disc(cx, cy, 12, 12, STEELB, lambda nx, ny: 2.6 - nx * 0.4 - ny * 0.6)
    cv.disc(cx, cy, 10, 10, SHEET, lambda nx, ny: 4.4 - ny * 0.6)
    for a in range(0, 360, 30):
        r = 7 if a % 90 else 6
        cv.flat(round(cx + math.cos(math.radians(a)) * 8), round(cy + math.sin(math.radians(a)) * 8), SLATE[1])
        if not a % 90:
            cv.flat(round(cx + math.cos(math.radians(a)) * r), round(cy + math.sin(math.radians(a)) * r), SLATE[1])
    cv.line(cx, cy, cx - 4, cy - 5, SLATE, 0.6)                         # les deu
    cv.line(cx, cy, cx + 6, cy - 4, SLATE, 0.6)                         # i deu
    cv.flat(cx, cy, (160, 30, 26))
    cv.tint(cx - 7, cy - 8, cx - 2, cy - 4, (255, 255, 255), 0.25)      # el reflex del vidre
    cv.darken(cx + 11, cy - 8, cx + 13, cy + 12, 0.4)


def bg(cv, tube=1.0):
    wall(cv)
    ceiling(cv, tube)
    floor(cv)
    door(cv)
    wall_bits(cv)
    chute(cv)
    bags(cv)
    tub_station(cv, 469, 80, 496, 147, vell=True)
    boxes(cv)
    neta_panel(cv)
    dock(cv)
    ledger(cv)
    # la claror verda de la pantalla també toca les parets veïnes
    cv.tint(267, 27, 507, 200, (60, 255, 140), lambda x, y: 0.06 * green_cast(x, y))


PROPS = {}


# ─── Els llums del Llibre Major i el cursor ────────────────────────────────

def _frames():
    base = Canvas(light=LIGHT)
    bg(base)
    frames = []
    for i in range(12):
        cv = Canvas(light=LIGHT, img=base.img.copy())
        leds(cv, frame=i + 1)
        if i % 4 >= 2:                                                  # el cursor parpelleja
            cx, cy = CURSOR
            cv.rect(cx, cy, cx + 3, cy + 5, SCREENB, 1.4, lit=0)
        frames.append(_diff(cv.img, base.img))
    return frames


ANIMS = {'llibre': {'frames': _frames, 'frameDuration': 260}}


# ─── Animacions: el fluorescent que fa figa i la gota de la canonada ───────

def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv.img


def _frames_fluorescent():
    """El fluorescent brut aguanta una estona i de cop tartamudeja: s'apaga, torna, mig s'apaga i torna."""
    base = _base()
    empty = _diff(base, base)
    dims = {}
    frames = []
    for t in (1,) * 14 + (0.0, 1, 0.0, 0.6, 1, 0.6):
        if t == 1:
            frames.append(empty)
            continue
        if t not in dims:
            cv = Canvas(light=LIGHT)
            bg(cv, tube=t)
            f = _diff(cv.img, base)
            # sense el fluorescent la sala s'enfosqueix una mica al voltant (només el sostre i el capdamunt)
            c = Canvas(light=LIGHT, img=base.copy())
            c.img.alpha_composite(f)
            k = 0.3 if t == 0 else 0.15
            for X, Y, x, y in c.pixels(max(0, TUBE[0] - 133), 12, TUBE[0] + 133, 79):
                d = math.hypot((x - TUBE[0]) / 133, (y - 8) / 72)
                if d < 1:
                    o = c.P[X, Y]
                    m = 1 - k * (1 - d) ** 1.5
                    c.P[X, Y] = (round(o[0] * m), round(o[1] * m), round(o[2] * m), o[3])
            dims[t] = _diff(c.img, base)
        frames.append(dims[t])
    return frames


DRIP_X, DRIP_Y = 289, 33                 # sota la canonada vella; cau a la taca d'humitat del terra
DRIP_FLOOR = 231


def _frames_gota():
    """Una gota es forma sota la canonada vella, s'allarga, cau i esquitxa la taca d'humitat."""
    base = _base()
    empty = _diff(base, base)
    frames = [empty] * 6
    # la gota que es forma: (alçada en píxels; a partir de 3, s'eixampla)
    for h in (1, 1, 2, 2, 3, 4):
        cv = Canvas(light=LIGHT, img=base.copy())
        cv.vline(DRIP_X, DRIP_Y, DRIP_Y + h - 1, DROP, 1)
        if h >= 3:
            cv.put(DRIP_X - 1, DRIP_Y + h - 2, DROP, 0.6)
            cv.put(DRIP_X + 1, DRIP_Y + h - 2, DROP, 0.6)
        cv.flat(DRIP_X, DRIP_Y + h - 1, DROP[2])
        frames.append(_diff(cv.img, base))
    # la caiguda, cada cop més ràpida (y del cap de la gota i la llargada de l'estela)
    for y, ln in ((40, 3), (48, 3), (60, 4), (78, 5), (102, 6), (132, 7), (167, 8), (205, 8), (229, 6)):
        cv = Canvas(light=LIGHT, img=base.copy())
        cv.vline(DRIP_X, y - ln + 1, y - 1, DROP, 0.6)
        cv.flat(DRIP_X, y, DROP[2])
        frames.append(_diff(cv.img, base))
    # l'esquitx: unes gotetes que salten i una rodoneta a la taca
    for k in range(4):
        cv = Canvas(light=LIGHT, img=base.copy())
        if k < 3:
            hop = (2, 3, 1)[k]
            for s in (-1, 1):
                cv.flat(DRIP_X + s * (1 + k), DRIP_FLOOR - hop, DROP[1] if k < 2 else DROP[0])
            if k == 1:
                cv.flat(DRIP_X, DRIP_FLOOR - 4, DROP[2])
        r = 2 + k * 2                                                   # la rodoneta, aplanada: és a terra
        for a in range(0, 360, 8):
            cv.put(round(DRIP_X + math.cos(math.radians(a)) * r), round(DRIP_FLOOR + math.sin(math.radians(a)) * r * 0.35),
                   DROP, 1.0 - k * 0.3)
        frames.append(_diff(cv.img, base))
    frames += [empty] * 2
    return frames


ANIMS['fluorescent'] = {'frames': _frames_fluorescent, 'frameDuration': 110}
ANIMS['gota'] = {'frames': _frames_gota, 'frameDuration': 100}


GEOMETRIA = {
    'things': {
        'porta': {'rect': (19, 67, 80, 200), 'walk': (53, 248)},
        'bosses': {'rect': (93, 152, 203, 208), 'walk': (147, 253)},
        'conducte': {'rect': (213, 67, 280, 174), 'walk': (248, 248)},
        'llibre': {'rect': (315, 48, 453, 203), 'walk': (387, 251)},
        'tub': {'rect': (469, 80, 496, 147), 'walk': (483, 248)},
        'panell': {'rect': (520, 93, 565, 147), 'walk': (541, 248)},
    },
    'spawns': {'iri': (160, 261)},
    'walkable': [(19, 236), (621, 236), (632, 271), (8, 271)],
}
