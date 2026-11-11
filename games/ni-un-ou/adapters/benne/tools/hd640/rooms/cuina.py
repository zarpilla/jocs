"""
Prova de resolució: la cuina de l'Arenga a 640×360 (la composició de hd/rooms/cuina.py ×4/3, dibuixada de nou
amb el detall que hi cap). Mateixes rampes, mateixos props (`safata`, `armari_obert`, `ulls_dia`) i mateixes
animacions (`vapor`, `forn`, `fred`). D'esquerra a dreta:
  - la porta de vaivé del menjador (amb l'ull de bou i la planxa de puntades);
  - el muntacàrregues (porta de guillotina aixecada, la cabina amb els carrils i la botonera CUINA · REBOST · PONT);
  - el passaplats al menjador i la boca del tub de veu de llautó;
  - els fogons amb baranes i subjecta-olles, la campana amb el filtre i les olles i cassons penjats;
  - la cambra freda, l'armari de les olles i el forn amb el pa d'en Tomàs;
  - a la dreta, el marbre amb la pasta, la farina, els pans a refredar, les espècies i un ull de bou.
"""
import math

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from hd.pix import Canvas, Light, W, H, hr, mix  # noqa: F401
from hd.rooms.arenga import CAB, DARK, WHITEP, REDP, YELL, BRASS, SEAG, box, rrect, bolt, hpipe, vpipe, glow
from hd.rooms.comu import _diff, text, text_width
from hd.rooms.principal import (CREAM, TEAK, DOORP, in_door, sill, porthole, day_porthole, plaque, floor_shadow,
                                foot_shadow, wear)
from hd.rooms.cuina import STEEL, TILE, QUARRY, INWARM, FIRE, BREAD, FLOUR, COPPERP, ICE
from hd640.rooms.laboratori import ceiling, lamp, lamp_glow, shine, door_frame
from hd640.rooms.menjador import leaf, sign_box

CEIL_H = 24
FLOOR_Y = 203
BOTTOM = 260                      # per sota hi ha la barra de verbs
LAMP_Y = 27
LAMPS = (128, 275, 440, 589)
VP = (320, 40)

_OVEN_K = 0.0                     # el resplendor del forn (l'anima `forn`)
LIGHT = Light(ambient=-0.25, vignette=(59, 32), floor_fade=(251, 53))
for _x in LAMPS:
    LIGHT.point(_x, CEIL_H + 5, r=149, k=2.2, squash=1.1, down=True, power=1.5)
LIGHT.point(275, 83, r=61, k=0.8, power=2.0)                 # el llum de la campana
LIGHT.point(517, 157, r=40, k=0.5, power=2.0)                # el vidre del forn

D_PORTA = (13, 85, 64, FLOOR_Y)
MUNTA = (77, 64, 152, 171)        # el marc del muntacàrregues
CAB_IN = (85, 112, 131, 165)      # l'obertura de la cabina
CFREDA = (331, 61, 397, FLOOR_Y)
ARMARI = (411, 93, 469, FLOOR_Y)
FORN = (483, 115, 555, FLOOR_Y)
COUNTER_Y = 149                   # el marbre (altura de maluc)
PORT = (603, 109, 12)


# ─── Paret i terra ──────────────────────────────────────────────────────────

def wall(cv, lvl=4.6, frames=96, frame0=-13, seam=85, seed=3):
    """Planxa pintada de crema fins a terra (a la cuina no hi ha sòcol de fusta), amb quadernes i reblons."""
    for y in range(CEIL_H, FLOOR_Y):
        for x in range(W):
            cv.put(x, y, CREAM, lvl + (hr(x // 3, y // 5, seed) - 0.5) * 0.25)
    for fx in range(frame0, W, frames):
        for x in range(max(0, fx), min(W - 1, fx + 5) + 1):
            d = x - fx
            for y in range(CEIL_H, FLOOR_Y - 6):
                cv.put(x, y, CREAM, lvl + (0.9 if d == 0 else 0.5 if d == 1 else -0.6 if d >= 4 else 0.1))
        for y in range(CEIL_H + 10, FLOOR_Y - 10, 14):
            if 0 <= fx + 2 <= W - 1:
                bolt(cv, fx + 2, y, CREAM, lvl + 0.2)
    for x in range(W):
        cv.put(x, seam, CREAM, lvl - 1.1)
        cv.put(x, seam + 1, CREAM, lvl + 0.7 if hr(x // 2, seam) > 0.3 else lvl + 0.1)
    # el sòcol d'acer (es neteja a raig)
    for y in range(FLOOR_Y - 6, FLOOR_Y):
        for x in range(W):
            cv.put(x, y, STEEL, 3.6 - (y - FLOOR_Y + 6) * 0.25 + (hr(x // 5, y, 9) - 0.5) * 0.3)
    cv.hline(0, W - 1, FLOOR_Y - 6, STEEL, 5.4)


def quarry(cv, lvl=3.8, tile=29, check=0.25, seed=3):
    """Rajola de terrissa (vermella) en perspectiva, a escacs suaus. → màscara del terra."""
    mask = [[False] * W for _ in range(H)]
    for y in range(FLOOR_Y, H):
        d = y - VP[1]
        v = 3467 / d
        vn = 3467 / (d + 1)
        for x in range(W):
            u = VP[0] + (x - VP[0]) * 200 / d
            u2 = VP[0] + (x + 1 - VP[0]) * 200 / d
            lv = lvl + (hr(int(u // 4), int(v * 3), seed) - 0.5) * 0.5
            if (int(u // tile) + int(v * 2.6)) % 2:
                lv += check
            if int(u // tile) != int(u2 // tile):
                lv -= 1.1
            elif int(v * 2.6) != int(vn * 2.6):
                lv -= 0.9
            cv.put(x, y, QUARRY, lv)
            mask[y][x] = True
    cv.hline(0, W - 1, FLOOR_Y, QUARRY, lvl - 1.8)
    return mask


def tiles(cv, x0, y0, x1, y1, seed=0, size=10):
    """Rajola blanca de cuina: junts, bisell a dalt i a l'esquerra, alguna esquerda i greix a prop dels fogons."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            tx, ty = (x - x0) % size, (y - y0) % size
            tid = ((x - x0) // size, (y - y0) // size)
            if tx == 0 or ty == 0:
                v = 2.6
            else:
                v = 4.2 + (hr(*tid, seed) - 0.5) * 0.5
                if tx == 1 or ty == 1:
                    v += 0.7
                elif tx == size - 1 or ty == size - 1:
                    v -= 0.4
            cv.put(x, y, TILE, v)
    # unes esquerdes, en diagonal dins d'una rajola
    for i in range(3):
        tx = x0 + size * int(hr(i, 11, seed) * ((x1 - x0) // size)) + 2
        ty = y0 + size * int(hr(i, 12, seed) * ((y1 - y0) // size)) + 2
        for k in range(size - 4):
            cv.put(tx + k, ty + k // 2 + (k % 3 == 0), TILE, 2.4)


# ─── Porta, muntacàrregues, passaplats i tub de veu ─────────────────────────

def door(cv):
    """La porta de vaivé del menjador: ull de bou (el menjador càlid a l'altra banda) i planxa de puntades."""
    x0, y0, x1, y1 = D_PORTA

    def mess(c, x, y):
        c.put(x, y, INWARM, 5.6 - math.hypot(x - 39, y - 113) * 0.24 - (0.8 if y > 116 else 0), lit=0)
    leaf(cv, x0, y0, x1, y1 - 7, DOORP, 3.8, handle='right', seed=7, window=(39, 113, 9, mess))
    glow(cv, 39, 113, 15, (255, 200, 130), 0.15)
    box(cv, x0 + 4, y1 - 36, x1 - 4, y1 - 11, STEEL, 4.2)                # planxa de puntades
    for y in range(y1 - 32, y1 - 14, 4):
        for x in range(x0 + 7 + (y // 4) % 2 * 2, x1 - 5, 5):
            cv.put(x, y, STEEL, 5.8)
            cv.put(x + 1, y + 1, STEEL, 3.0)
    for i in range(5):                                                   # les rascades de les safates
        y = 150 + int(hr(i, 41) * 14)
        cv.hline(x0 + 8 + int(hr(i, 42) * 10), x0 + 16 + int(hr(i, 43) * 16), y, DOORP, 5.0)
    door_frame(cv, x0, y0, x1, y1)
    sill(cv, x0, x1, y1, h=7)
    plaque(cv, (x0 + x1) // 2, 69, 'MENJADOR')


def dumbwaiter(cv):
    """El muntacàrregues: marc d'acer reblonat, la porta de guillotina aixecada, la cabina i la botonera."""
    x0, y0, x1, y1 = MUNTA
    cx0, cy0, cx1, cy1 = CAB_IN
    # el moble de sota, amb dues portetes
    box(cv, x0, y1, x1, FLOOR_Y - 1, STEEL, 3.6, grad=0.8)
    mx = (x0 + x1) // 2
    cv.vline(mx, y1 + 4, FLOOR_Y - 4, STEEL, 2.0)
    cv.vline(mx + 1, y1 + 4, FLOOR_Y - 4, STEEL, 4.6)
    for hx in (mx - 6, mx + 5):
        cv.rect(hx, y1 + 8, hx + 1, y1 + 14, STEEL, 5.6)
    for y in range(y1 + 20, FLOOR_Y - 6, 3):                             # reixeta de ventilació
        cv.hline(x0 + 6, mx - 5, y, STEEL, 2.2)
    foot_shadow(cv, x0 - 2, x1 + 2, FLOOR_Y + 1, 5, 0.7)
    # el marc
    box(cv, x0, y0, x1, y1, STEEL, 4.0, grad=0.6)
    cv.hline(x0 + 1, x1 - 1, y0 + 1, STEEL, 5.6)
    for bx in range(x0 + 3, x1 - 1, 9):
        bolt(cv, bx, y0 + 3, STEEL, 4.4)
        bolt(cv, bx, y1 - 4, STEEL, 4.4)
    # la cabina, fosca, amb la paret del fons, els carrils i els cables
    for y in range(cy0, cy1 + 1):
        for x in range(cx0, cx1 + 1):
            cv.put(x, y, STEEL, 1.4 + (y - cy0) * 0.018 - abs(x - (cx0 + cx1) / 2) * 0.015, lit=0.4)
    for rx in (cx0 + 1, cx1 - 1):
        cv.vline(rx, cy0, cy1, STEEL, 3.0 if rx == cx0 + 1 else 2.4, lit=0.4)
        cv.vline(rx + (1 if rx == cx0 + 1 else -1), cy0, cy1, STEEL, 1.6, lit=0.4)
        for y in range(cy0 + 4, cy1, 9):
            cv.put(rx, y, STEEL, 4.8, lit=0.4)
    for kx in ((cx0 + cx1) // 2 - 3, (cx0 + cx1) // 2 + 3):              # els cables de la cabina
        cv.vline(kx, cy0, cy0 + 12, CAB, 2.6, lit=0.4)
    cv.rect(cx0, cy1 - 3, cx1, cy1, STEEL, 3.6)                          # el terra de la cabina
    cv.hline(cx0, cx1, cy1 - 3, STEEL, 5.0)
    # la porta de guillotina, aixecada (planxa amb nervis)
    gx0, gy0, gx1, gy1 = cx0 - 1, y0 + 6, cx1 + 1, cy0 - 3
    box(cv, gx0, gy0, gx1, gy1, STEEL, 4.6)
    for y in range(gy0 + 5, gy1 - 2, 6):
        cv.hline(gx0 + 2, gx1 - 2, y, STEEL, 3.4)
        cv.hline(gx0 + 2, gx1 - 2, y + 1, STEEL, 5.6)
    box(cv, (gx0 + gx1) // 2 - 8, gy1 - 6, (gx0 + gx1) // 2 + 8, gy1 - 3, STEEL, 6.0)  # la nansa
    cv.darken(cx0, cy0, cx1, cy0 + 6, lambda x, y: 0.7 - (y - cy0) * 0.11)
    # botonera: CUINA · REBOST · PONT
    px0, py0 = 136, 115
    box(cv, px0, py0, px0 + 12, py0 + 43, STEEL, 3.0)
    cv.hline(px0 + 1, px0 + 11, py0 + 1, STEEL, 4.4)
    for i, (col, lab) in enumerate(((REDP, 'C'), (SEAG, 'R'), (SEAG, 'P'))):
        by = py0 + 4 + i * 13
        cv.disc(px0 + 6, by + 3, 3, 3, DARK, 1.0)
        cv.disc(px0 + 6, by + 3, 2.4, 2.4, col, lambda nx, ny: 3.8 - nx - ny)
        text(cv, lab, px0 + 5, by + 7, None, 0, flat=(220, 222, 222))
    # el pilot d'arribada, apagat
    cv.disc(px0 + 6, py0 - 5, 2.5, 2, SEAG, 1.4)
    cv.disc(px0 + 6, py0 - 5, 3.5, 3, STEEL, 2.6)
    cv.disc(px0 + 6, py0 - 5, 2.5, 2, SEAG, 1.4)
    # el rètol del muntacàrregues
    s = 'MUNTACÀRREGUES'
    sx0, sx1 = x0 + 6, x1 - 6
    box(cv, sx0, y0 - 12, sx1, y0 - 3, WHITEP, 4.2)
    cv.hline(sx0 + 1, sx1 - 1, y0 - 11, WHITEP, 5.2)
    text(cv, s, sx0 + 1 + ((sx1 - sx0 - 1) - text_width(s)) // 2, y0 - 9, None, 0, flat=(30, 34, 40))


def tray(cv):
    """La safata, a la cabina del muntacàrregues, amb un paquet de paper d'estrassa lligat, i el pilot verd encès."""
    cx0, cy0, cx1, cy1 = CAB_IN
    ty = cy1 - 5
    cv.poly([(cx0 + 5, ty - 4), (cx1 - 5, ty - 4), (cx1 - 2, ty), (cx0 + 2, ty)], STEEL, 5.0)
    cv.hline(cx0 + 2, cx1 - 2, ty + 1, STEEL, 3.0)
    cv.hline(cx0 + 5, cx1 - 5, ty - 5, STEEL, 6.2)
    KRAFT = [(60, 44, 28), (110, 82, 48), (158, 126, 74), (198, 166, 102), (226, 198, 136)]
    px0, px1 = cx0 + 11, cx1 - 13
    box(cv, px0, ty - 15, px1, ty - 5, KRAFT, 3.0)
    cv.hline(px0 + 1, px1 - 1, ty - 14, KRAFT, 4.2)
    for i in range(6):                                                    # arrugues del paper
        cv.put(px0 + 3 + int(hr(i, 51) * (px1 - px0 - 6)), ty - 12 + int(hr(i, 52) * 6), KRAFT, 1.8)
    mid = (px0 + px1) // 2
    cv.vline(mid, ty - 15, ty - 5, WHITEP, 3.8)
    cv.hline(px0, px1, ty - 10, WHITEP, 3.8)
    cv.disc(mid, ty - 16, 2, 1, WHITEP, 4.4)                              # el nus
    cv.line(mid, ty - 16, mid + 4, ty - 19, WHITEP, 3.6)
    # el pilot: ha arribat alguna cosa
    for dx in (-1, 0, 1):
        cv.flat(142 + dx, 110, (120, 255, 150))
    cv.flat(142, 109, (200, 255, 210))
    glow(cv, 142, 110, 9, (90, 255, 120), 0.7)


def hatch(cv):
    """El passaplats, de la banda de la cuina: a l'altra banda, el menjador (la banqueta vermella i la taula)."""
    x0, y0, x1, y1 = 160, 112, 197, COUNTER_Y - 3
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            v = 3.6 + 1.6 * math.exp(-((x - 179) / 15) ** 2) - (y - y0) * 0.012
            cv.put(x, y, CREAM, v, lit=0.3)
    # la paret del menjador: el pòster de lluny, un llum
    cv.rect(x0 + 22, y0 + 2, x1 - 3, y0 + 11, WHITEP, 3.6, lit=0.3)
    cv.rect(x0 + 23, y0 + 3, x1 - 4, y0 + 5, [(20, 50, 90), (40, 90, 140)], 1.4, lit=0)
    cv.rect(x0 + 24, y0 + 7, x0 + 28, y0 + 9, [(40, 50, 70), (90, 100, 120)], 1.4, lit=0)
    # la banqueta vermella capitonada i la taula de teca
    BENCH = [(40, 10, 10), (64, 16, 14), (92, 24, 20), (120, 34, 26), (148, 48, 34)]
    cv.rect(x0, y0 + 14, x1, y1 - 8, BENCH, 2.6, lit=0.3)
    for bx in range(x0 + 5, x1, 9):
        for by in range(y0 + 17, y1 - 9, 6):
            cv.put(bx, by, BENCH, 0.6, lit=0)
    cv.rect(x0, y1 - 7, x1, y1 - 4, TEAK, 4.6, lit=0.3)
    cv.rect(x0, y1 - 3, x1, y1, TEAK, 2.0, lit=0.3)
    cv.rect(x0 + 10, y1 - 12, x0 + 13, y1 - 8, REDP, 3.6, lit=0.3)       # una tassa i un salser
    cv.put(x0 + 14, y1 - 10, REDP, 2.6, lit=0.3)
    cv.rect(x0 + 24, y1 - 9, x0 + 29, y1 - 8, WHITEP, 4.4, lit=0.3)
    # la persiana enrotllada i el marc
    box(cv, x0 - 4, y0 - 12, x1 + 4, y0 - 1, STEEL, 3.2)
    for y in range(y0 - 11, y0 - 1, 2):
        cv.hline(x0 - 3, x1 + 3, y, STEEL, 4.6)
    cv.rect(x1 - 9, y0 - 1, x1 - 7, y0 + 2, BRASS, 3.6)                 # el ganxo de la persiana
    cv.vline(x0 - 1, y0, y1, STEEL, 4.6)
    cv.vline(x0 - 2, y0, y1, STEEL, 3.0)
    cv.vline(x1 + 1, y0, y1, STEEL, 2.2)
    cv.vline(x1 + 2, y0, y1, STEEL, 3.4)
    box(cv, x0 - 7, y1 + 1, x1 + 7, y1 + 5, STEEL, 4.8)                  # el taulell
    cv.hline(x0 - 6, x1 + 6, y1 + 2, STEEL, 6.0)
    cv.darken(x0 - 6, y1 + 6, x1 + 6, y1 + 9, 0.6)


def voice_tube(cv, cx, y):
    """La boca del tub de veu (principal.voice_tube a 640): tub de llautó, colze, campana amb tapa i cadeneta."""
    vpipe(cv, cx, 0, y - 5, 3, BRASS, 3.0)
    for by in range(36, y - 10, 46):
        box(cv, cx - 5, by, cx + 5, by + 3, CAB, 3.4)
        cv.put(cx, by + 1, CAB, 5.2)
    cv.disc(cx, y, 5, 5, BRASS, lambda nx, ny: 3.4 - nx * 1.2 - ny * 1.0)
    cv.disc(cx, y + 6, 9, 8, BRASS, lambda nx, ny: 3.7 - nx * 1.3 - ny * 1.2)
    cv.disc(cx, y + 6, 7, 6, BRASS, lambda nx, ny: 1.4 + nx * 0.6 + ny * 0.8)
    cv.disc(cx, y + 6, 4, 3, DARK, 0.6)
    cv.disc(cx - 2, y + 2, 2, 1, BRASS, 5.4)
    for i, yy in enumerate(range(y + 15, y + 25)):
        cv.put(cx + 6 + (i % 2), yy, BRASS, 3.0 + (i % 2) * 0.8)
    cv.disc(cx + 8, y + 27, 4, 3, BRASS, lambda nx, ny: 4.0 - nx - ny)
    box(cv, cx - 10, y + 32, cx + 10, y + 37, BRASS, 3.0)                 # la placa: PONT
    text(cv, 'PONT', cx - 7, y + 33, None, 0, flat=(34, 22, 12))


# ─── Fogons, campana i olles ────────────────────────────────────────────────

STOVE = (229, 320)


def stove(cv):
    """Fogons de vaixell: baranes de mar, subjecta-olles, l'olla gran i la cafetera; a sobre, la campana i les olles."""
    x0, x1 = STOVE
    top = COUNTER_Y - 5
    tiles(cv, x0 - 3, 53, x1 + 3, top, seed=3)
    for y in range(90, top):                                             # greix a la rajola de sobre els fogons
        for x in range(x0, x1):
            if hr(x // 3, y // 3, 17) > 0.86 - (y - 90) * 0.004:
                cv.flat(x, y, mix(cv.get(x, y), (150, 120, 70), 0.18))
    # el cos d'acer: tauler de mànecs, porta del forn petit amb vidre i un calaix
    box(cv, x0, top, x1, FLOOR_Y - 1, STEEL, 3.8, grad=1.0)
    for i, kx in enumerate(range(x0 + 10, x1 - 6, 13)):                 # mànecs
        cv.disc(kx, top + 7, 3, 3, DARK, lambda nx, ny: 2.4 - nx - ny)
        cv.put(kx, top + 5, STEEL, 6.0)
        cv.put(kx + 1, top + 5, STEEL, 5.0)
    box(cv, x0 + 5, top + 14, x1 - 5, FLOOR_Y - 18, STEEL, 3.4)
    hpipe(cv, x0 + 10, x1 - 10, top + 18, 1, STEEL, 6.0)
    for y in range(top + 24, FLOOR_Y - 26):                               # el vidre del forn petit, fosc
        for x in range(x0 + 16, x1 - 16):
            cv.put(x, y, DARK, 1.6 + (0.9 if (x - y) % 23 < 2 else 0), lit=0.3)
    box(cv, x0 + 5, FLOOR_Y - 15, x1 - 5, FLOOR_Y - 5, STEEL, 3.2)
    hpipe(cv, (x0 + x1) // 2 - 9, (x0 + x1) // 2 + 9, FLOOR_Y - 10, 0, STEEL, 5.4)
    foot_shadow(cv, x0 - 2, x1 + 2, FLOOR_Y + 1, 5, 0.7)
    # el sobre i la barana de mar
    cv.rect(x0 - 3, top - 4, x1 + 3, top, STEEL, 2.6)
    cv.hline(x0 - 3, x1 + 3, top - 4, STEEL, 5.4)
    for px in (x0 - 3, x0 + 29, x0 + 59, x1 + 3):
        cv.vline(px, top - 16, top - 4, STEEL, 4.4)
        cv.vline(px + 1, top - 16, top - 4, STEEL, 2.6)
    hpipe(cv, x0 - 3, x1 + 3, top - 16, 1, STEEL, 4.6)
    # l'olla gran (amb tapa i nanses) i la cafetera de coure, subjectes amb barres
    ox = 256
    for y in range(top - 29, top - 4):
        for x in range(ox - 15, ox + 16):
            u = (x - ox) / 15.5
            cv.put(x, y, STEEL, 4.6 + 1.6 * (-0.3 - u) - 1.0 * u * u)
    for y in (top - 24, top - 10):                                         # els anells de l'olla
        cv.hline(ox - 14, ox + 14, y, STEEL, 3.2)
    cv.disc(ox, top - 29, 15, 3, STEEL, lambda nx, ny: 5.6 - ny * 0.8)
    cv.disc(ox, top - 29, 12, 2, STEEL, 4.4)
    cv.rect(ox - 3, top - 35, ox + 3, top - 32, DARK, 2.0)               # el pom de la tapa
    cv.hline(ox - 2, ox + 2, top - 35, DARK, 3.4)
    for sx in (-1, 1):
        cv.rect(ox + sx * 15 + min(0, sx * 4), top - 21, ox + sx * 15 + max(0, sx * 4), top - 18, DARK, 1.6)
    cv.hline(ox - 20, ox + 20, top - 12, STEEL, 5.6)                      # la barra que la subjecta
    kx = 299
    cv.disc(kx, top - 12, 9, 8, COPPERP, lambda nx, ny: 3.6 - nx * 1.3 - ny * 1.0)
    cv.disc(kx - 3, top - 15, 2, 2, COPPERP, 6.0)
    cv.line(kx + 8, top - 13, kx + 15, top - 19, COPPERP, 3.4)            # el broc
    cv.line(kx + 8, top - 12, kx + 15, top - 18, COPPERP, 2.0)
    cv.disc(kx, top - 20, 3, 1.5, DARK, 2.0)
    cv.line(kx - 9, top - 14, kx - 13, top - 8, DARK, 1.4)                # la nansa
    cv.line(x0 + 16, top - 11, x0 + 16, top - 6, DARK, 1.0)
    # (el vapor de l'olla és l'animació `vapor`)
    # la campana, amb el filtre de làmines i el llum
    cv.poly([(x0 - 8, 69), (x1 + 8, 69), (x1 - 3, 53), (x0 + 3, 53)], STEEL, lambda x, y: 4.2 + (y - 53) * 0.05)
    cv.hline(x0 - 6, x1 + 6, 66, STEEL, 5.8)
    cv.rect(x0 + 3, 35, x1 - 3, 52, STEEL, 3.4)
    cv.vline(x0 + 3, 35, 52, STEEL, 4.6)
    cv.vline(x1 - 3, 35, 52, STEEL, 2.4)
    for x in range(x0 + 8, x1 - 5, 5):
        cv.vline(x, 38, 49, STEEL, 2.4)
        cv.vline(x + 1, 38, 49, STEEL, 4.4)
    for bx in (x0 + 5, x1 - 5):
        bolt(cv, bx, 37, STEEL, 4.8)
    cv.hline(x0 - 8, x1 + 8, 69, STEEL, 2.0)
    cv.rect(x0 + 32, 70, x1 - 32, 71, [(160, 140, 90), (255, 240, 190), (255, 252, 236)], 1.6, lit=0)
    glow(cv, (x0 + x1) // 2, 74, 24, (255, 236, 190), 0.4)
    # la barra amb les olles, els cassons i els cullerots penjats
    hpipe(cv, x0 - 3, x1 + 3, 80, 1, STEEL, 4.8)
    for hx in (x0 - 1, x1 + 1):
        cv.vline(hx, 70, 80, STEEL, 3.6)
    hooks = ((x0 + 6, 'pan', 12), (x0 + 24, 'ladle', 0), (x0 + 35, 'pot', 9), (x0 + 53, 'pan', 9),
             (x0 + 68, 'whisk', 0), (x0 + 80, 'pot', 7))
    for hx, kind, r in hooks:
        cv.vline(hx, 81, 85, STEEL, 3.0)
        cv.put(hx + 1, 85, STEEL, 3.0)
        if kind == 'pan':
            cv.vline(hx, 86, 96, STEEL, 3.4)
            cv.vline(hx + 1, 86, 96, STEEL, 2.2)
            ramp = COPPERP if r > 10 else STEEL
            cv.disc(hx, 96 + r, r, r, ramp, lambda nx, ny: 3.8 - nx * 1.2 - ny * 1.0)
            cv.disc(hx, 96 + r, r - 3, r - 3, ramp, lambda nx, ny: 2.6 + nx * 0.6 + ny * 0.6)
            cv.disc(hx - r // 3, 96 + r // 2 + 1, 2, 1, ramp, 6.0)
        elif kind == 'ladle':
            cv.vline(hx, 86, 109, STEEL, 4.6)
            cv.vline(hx + 1, 86, 109, STEEL, 3.0)
            cv.disc(hx, 113, 4, 3.5, STEEL, lambda nx, ny: 4.0 - nx - ny)
            cv.disc(hx - 1, 112, 2, 1, STEEL, 2.2)
        elif kind == 'whisk':
            cv.vline(hx, 86, 96, TEAK, 3.6)
            for dx in (-3, -1, 1, 3):
                for y in range(97, 109):
                    cv.put(hx + round(dx * math.sin((y - 96) / 13 * math.pi)), y, STEEL, 4.6 - abs(dx) * 0.3)
        else:
            cv.line(hx - 5, 86, hx + 5, 86, STEEL, 3.0)
            for y in range(88, 88 + r * 2):
                for x in range(hx - r, hx + r + 1):
                    u = (x - hx) / (r + 0.5)
                    cv.put(x, y, COPPERP, 3.6 + 1.4 * (-0.3 - u) - 0.8 * u * u)
            cv.hline(hx - r, hx + r, 88, COPPERP, 5.0)
            cv.hline(hx - r - 3, hx - r, 91, COPPERP, 3.0)
            cv.hline(hx + r, hx + r + 3, 91, COPPERP, 2.4)


# ─── Cambra freda, armari i forn ────────────────────────────────────────────

def cold_room(cv):
    """La porta de la cambra freda: gruixuda, blanca, amb frontisses i tancador cromats, el termòmetre i gebre."""
    x0, y0, x1, y1 = CFREDA
    box(cv, x0 - 4, y0 - 4, x1 + 4, y1, STEEL, 3.6)
    cv.hline(x0 - 3, x1 + 3, y0 - 3, STEEL, 5.2)
    box(cv, x0, y0, x1, y1 - 3, ICE, 4.2, grad=0.5)
    cv.vline(x0 + 1, y0 + 1, y1 - 4, ICE, 5.4)
    cv.vline(x0 + 2, y0 + 1, y1 - 4, ICE, 4.8)
    for y in range(y0 + 1, y1 - 3):                                      # la junta de goma
        cv.put(x1 - 1, y, ICE, 3.0 if hr(x0, y // 4) > 0.5 else 2.4)
    box(cv, x0 + 8, y0 + 32, x1 - 8, y1 - 34, ICE, 4.0)                  # el plafó
    cv.hline(x0 + 9, x1 - 9, y0 + 33, ICE, 5.2)
    # frontisses
    for hy in (y0 + 16, y1 - 32):
        box(cv, x0 - 5, hy, x0 + 5, hy + 13, STEEL, 5.0)
        cv.vline(x0, hy + 1, hy + 12, STEEL, 3.0)
        for by in (hy + 3, hy + 10):
            cv.put(x0 + 3, by, STEEL, 6.4)
    # el tancador (palanca gran cromada)
    hx, hy = x1 - 13, 128
    box(cv, hx - 3, hy - 8, hx + 8, hy + 13, STEEL, 4.6)
    cv.vline(hx - 2, hy - 7, hy + 12, STEEL, 6.0)
    cv.rect(hx - 14, hy + 1, hx + 5, hy + 4, STEEL, 5.8)
    cv.hline(hx - 14, hx + 5, hy + 1, STEEL, 7.0)
    cv.hline(hx - 14, hx + 5, hy + 5, STEEL, 2.6)
    cv.disc(hx + 3, hy + 2, 3, 3, STEEL, lambda nx, ny: 6.6 - nx - ny)
    cv.disc(hx - 15, hy + 2, 2, 2.5, STEEL, 5.0)
    # el termòmetre digital, a sobre: +3
    box(cv, x0 + 19, y0 - 17, x1 - 19, y0 - 7, DARK, 2.0)
    cv.hline(x0 + 20, x1 - 20, y0 - 16, DARK, 3.4)
    red = (255, 80, 60)
    for dx in range(5):                                                  # el «+» (la font petita no en té)
        cv.flat(x0 + 23 + dx, y0 - 12, red)
    for dy in range(-2, 3):
        cv.flat(x0 + 25, y0 - 12 + dy, red)
    text(cv, '3', x0 + 30, y0 - 14, None, 0, flat=red)
    cv.flat(x0 + 35, y0 - 14, red)                                       # el grau
    glow(cv, x0 + 29, y0 - 12, 8, (255, 80, 60), 0.35)
    # gebre a baix, una gota de condensació al plafó i el rètol
    for x in range(x0 + 1, x1):
        for y in range(y1 - 11, y1 - 3):
            if hr(x // 2, y) > 0.55 + (y1 - y) * 0.04:
                cv.put(x, y, ICE, 5.2)
    for gx, gy in ((x0 + 14, y0 + 60), (x1 - 18, y0 + 84)):
        cv.vline(gx, gy, gy + 6, ICE, 5.6)
        cv.put(gx, gy + 7, ICE, 2.6)
    BLUEP = [(20, 40, 80), (30, 60, 120), (60, 100, 170), (120, 160, 220), (200, 220, 240)]
    box(cv, x0 + 11, 77, x1 - 11, 88, BLUEP, 1.6)
    cv.hline(x0 + 12, x1 - 12, 78, BLUEP, 2.8)
    text(cv, 'FRED', (x0 + x1) // 2 - text_width('FRED') // 2, 80, None, 0, flat=(220, 236, 248))
    box(cv, x0 + 15, 92, x1 - 15, 99, YELL, 3.6, edge=False)             # avís: TANCA LA PORTA
    text(cv, 'TANCA', (x0 + x1) // 2 - text_width('TANCA') // 2, 93, None, 0, flat=(40, 30, 10))
    cv.darken(x0, y1 - 2, x1 + 4, y1 + 2, 0.6)


def cupboard(cv):
    """L'armari de les olles, de fusta, tancat, amb reixeta (l'escletxa per on es mira) i la balda de mar."""
    x0, y0, x1, y1 = ARMARI
    box(cv, x0 - 3, y0 - 5, x1 + 3, y0, TEAK, 4.4)                       # cornisa
    cv.hline(x0 - 2, x1 + 2, y0 - 4, TEAK, 5.6)
    box(cv, x0, y0, x1, y1 - 1, TEAK, 3.2, grad=0.6)
    _door(cv, x0 + 3, y0 + 3, x1 - 3, y1 - 5)
    foot_shadow(cv, x0 - 3, x1 + 3, FLOOR_Y + 1, 5, 0.7)
    # damunt: una cassola que sembla un casc, una pila de paelles i un colador
    cv.disc(x0 + 15, y0 - 12, 11, 7, STEEL, lambda nx, ny: 4.4 - nx * 1.2 - ny * 1.4)
    cv.hline(x0 + 3, x0 + 27, y0 - 6, STEEL, 3.2)
    cv.disc(x0 + 11, y0 - 15, 3, 1.5, STEEL, 6.4)
    for i in range(4):
        cv.rect(x1 - 26 + i, y0 - 7 - i * 2, x1 - 5 - i, y0 - 6 - i * 2, STEEL, 3.4 + i * 0.6)
    cv.hline(x1 - 34, x1 - 26, y0 - 7, STEEL, 2.6)


def _door(cv, x0, y0, x1, y1):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            v = 3.6 + (hr(x // 2, y // 15, 5) - 0.5) * 0.4 - (y - y0) * 0.005
            if x in (x0, x0 + 1):
                v += 1.0
            if x >= x1 - 1:
                v -= 1.0
            cv.put(x, y, TEAK, v)
    for y in range(y0, y1 + 1):                                          # la veta de la fusta
        for x in range(x0 + 2, x1 - 2):
            if math.sin(x * 0.9 + math.sin(y * 0.05 + x * 0.2) * 2.4) > 0.94:
                cv.put(x, y, TEAK, 2.6)
    box(cv, x0 + 5, y0 + 5, x1 - 5, y0 + 45, TEAK, 3.2)
    box(cv, x0 + 5, y0 + 53, x1 - 5, y1 - 8, TEAK, 3.2)
    for y in range(y0 + 10, y0 + 40, 4):                                 # reixeta de ventilació
        cv.hline(x0 + 10, x1 - 10, y, TEAK, 1.2)
        cv.hline(x0 + 10, x1 - 10, y + 1, TEAK, 4.2)
    cv.rect(x1 - 9, y0 + 53, x1 - 7, y0 + 64, BRASS, 4.2)                # nansa i balda de mar
    cv.vline(x1 - 9, y0 + 53, y0 + 64, BRASS, 5.4)
    cv.rect(x1 - 12, y0 + 67, x1 - 3, y0 + 69, BRASS, 3.4)
    cv.put(x1 - 4, y0 + 68, BRASS, 5.6)


def cupboard_open(cv):
    """Decorat `armari_obert`: la porta oberta (de cantó) i, a dins, fosc, amb les olles a les prestatgeries."""
    x0, y0, x1, y1 = ARMARI
    ix0, iy0, ix1, iy1 = x0 + 3, y0 + 3, x1 - 3, y1 - 5
    for y in range(iy0, iy1 + 1):
        for x in range(ix0, ix1 + 1):
            cv.put(x, y, DARK, 1.6 + (x - ix0) * 0.016 - (y - iy0) * 0.003, lit=0.25)
    for sy in (iy0 + 35, iy0 + 69):                                       # prestatges
        cv.hline(ix0, ix1, sy, TEAK, 1.8, lit=0.3)
        cv.hline(ix0, ix1, sy + 1, TEAK, 1.0, lit=0.3)
    for px, py, r in ((ix0 + 13, iy0 + 34, 9), (ix0 + 35, iy0 + 34, 7), (ix0 + 19, iy0 + 68, 12), (ix0 + 42, iy0 + 68, 5)):
        for y in range(py - r, py):
            for x in range(px - r, px + r + 1):
                cv.put(x, y, STEEL, 1.4 + (px - x) * 0.03, lit=0.25)
        cv.hline(px - r, px + r, py - r, STEEL, 2.4, lit=0.25)
    cv.hline(ix0, ix1, iy1, TEAK, 1.2, lit=0.3)
    # la porta, oberta cap a la dreta, de cantó
    cv.poly([(x1 + 1, y0 + 1), (x1 + 11, y0 + 7), (x1 + 11, y1 - 3), (x1 + 1, y1 - 5)], TEAK,
            lambda x, y: 2.6 + (x - x1) * 0.09)
    cv.vline(x1 + 11, y0 + 7, y1 - 3, TEAK, 4.0)
    cv.rect(x1 + 8, y0 + 56, x1 + 9, y0 + 67, BRASS, 3.6)


def oven(cv):
    """El forn: acer, vidre amb el pa a dins (llum taronja), rellotge i mànecs, i el drap a la nansa."""
    x0, y0, x1, y1 = FORN
    box(cv, x0, y0, x1, y1 - 1, STEEL, 4.0, grad=1.0)
    cv.rect(x0 + 3, y0 + 3, x1 - 3, y0 + 16, STEEL, 2.6)                 # tauler de control
    cv.hline(x0 + 3, x1 - 3, y0 + 16, STEEL, 4.8)
    for i, kx in enumerate(range(x0 + 10, x1 - 22, 12)):
        cv.disc(kx, y0 + 9, 4, 4, DARK, lambda nx, ny: 2.6 - nx - ny)
        cv.line(kx, y0 + 9, kx + 2, y0 + 6, STEEL, 6.2)
        for a in range(-60, 241, 60):
            cv.put(kx + round(math.cos(math.radians(a)) * 6), y0 + 9 - round(math.sin(math.radians(a)) * 6), STEEL, 4.6)
    box(cv, x1 - 27, y0 + 5, x1 - 5, y0 + 13, DARK, 1.4)
    text(cv, '15', x1 - 25, y0 + 7, None, 0, flat=(255, 150, 60))
    cv.flat(x1 - 17, y0 + 8, (255, 150, 60))                             # els dos punts del rellotge
    cv.flat(x1 - 17, y0 + 10, (255, 150, 60))
    text(cv, '00', x1 - 15, y0 + 7, None, 0, flat=(255, 150, 60))
    # la porta amb el vidre
    box(cv, x0 + 4, y0 + 21, x1 - 4, y1 - 16, STEEL, 4.6)
    cv.hline(x0 + 5, x1 - 5, y0 + 22, STEEL, 5.8)
    wx0, wy0, wx1, wy1 = x0 + 12, y0 + 32, x1 - 12, y1 - 29
    for y in range(wy0, wy1 + 1):
        for x in range(wx0, wx1 + 1):
            cv.put(x, y, FIRE, 2.6 + _OVEN_K - abs(y - (wy0 + wy1) / 2) * 0.09 - abs(x - (wx0 + wx1) / 2) * 0.03, lit=0)
    cv.rect(wx0, wy0, wx1, wy0 + 1, STEEL, 2.6, lit=0)                   # el marc del vidre, a l'ombra
    cv.hline(wx0, wx1, wy0 + 5, FIRE, 1.4, lit=0)                         # la resistència de dalt
    cv.hline(wx0, wx1, wy1 - 8, STEEL, 2.0, lit=0)                         # la reixa
    for bx in range(wx0 + 2, wx1, 5):
        cv.put(bx, wy1 - 7, STEEL, 1.6, lit=0)
    for bx in (wx0 + 8, wx0 + 24, wx0 + 40):                              # pans, amb el tall a sobre
        cv.disc(bx, wy1 - 13, 7, 4, BREAD, lambda nx, ny: 3.6 - ny * 1.2, lit=0)
        cv.line(bx - 3, wy1 - 15, bx + 2, wy1 - 16, BREAD, 4.8, lit=0)
        cv.line(bx - 1, wy1 - 13, bx + 4, wy1 - 14, BREAD, 4.6, lit=0)
    for i in range(-6, 8):                                               # reflex al vidre
        cv.flat(wx0 + 6 + i, wy0 + 4 - i // 2 + 6, mix(cv.get(wx0 + 6 + i, wy0 + 10 - i // 2), (255, 236, 200), 0.25))
    glow(cv, (wx0 + wx1) // 2, (wy0 + wy1) // 2, 35, (255, 170, 80), 0.35 + _OVEN_K * 0.2)
    hpipe(cv, x0 + 8, x1 - 8, y0 + 26, 1, STEEL, 6.0)                    # la nansa
    for hx in (x0 + 8, x1 - 8):
        cv.rect(hx - 1, y0 + 24, hx + 1, y0 + 28, STEEL, 4.0)
    # el drap de cuina penjat (quadres blancs i vermells, amb el plec)
    for y in range(y0 + 28, y0 + 54):
        for x in range(x0 + 13, x0 + 27):
            ch = ((x - x0) // 4 + (y - y0) // 4) % 2
            v = (3.8 if ch else 4.2) - (0.8 if x == x0 + 20 else 0) - (y - y0 - 28) * 0.02
            cv.put(x, y, REDP if ch else WHITEP, v)
    for x in range(x0 + 13, x0 + 27, 2):                                  # serrell
        cv.put(x, y0 + 54, WHITEP, 3.4)
    box(cv, x0 + 3, y1 - 12, x1 - 3, y1 - 3, STEEL, 2.6)                  # el calaix de les safates
    hpipe(cv, (x0 + x1) // 2 - 10, (x0 + x1) // 2 + 10, y1 - 8, 0, STEEL, 5.2)
    foot_shadow(cv, x0 - 3, x1 + 3, FLOOR_Y + 1, 5, 0.7)


def bakery(cv):
    """El marbre d'en Tomàs: pasta, farina, pans a refredar, el corró, el sac de farina, les espècies i l'ull de bou."""
    x0, x1 = 563, W - 1
    tiles(cv, x0, 75, x1, COUNTER_Y - 5, seed=4)
    box(cv, x0, COUNTER_Y, x1 + 2, FLOOR_Y - 1, STEEL, 3.6, grad=0.8)
    box(cv, x0 + 5, COUNTER_Y + 10, x1 - 5, FLOOR_Y - 6, STEEL, 3.2)
    hpipe(cv, x0 + 14, x0 + 34, COUNTER_Y + 16, 0, STEEL, 5.6)
    foot_shadow(cv, x0 - 2, x1, FLOOR_Y + 1, 5, 0.7)
    MARBLE = [(40, 40, 42), (90, 90, 88), (150, 150, 146), (200, 200, 194), (230, 230, 226)]
    cv.rect(x0 - 3, COUNTER_Y - 5, x1, COUNTER_Y, MARBLE, lambda x, y: 3.4 + (0.5 if math.sin(x * 0.3 + y) > 0.9 else 0))
    cv.hline(x0 - 3, x1, COUNTER_Y - 5, MARBLE, 4.6)
    cv.hline(x0 - 3, x1, COUNTER_Y, MARBLE, 1.4)
    # la pasta, amb farina escampada i la marca dels dits
    cv.disc(587, COUNTER_Y - 9, 12, 5, FLOUR, lambda nx, ny: 3.4 - ny * 1.0 - nx * 0.4)
    for dx in (-4, 0, 4):
        cv.put(587 + dx, COUNTER_Y - 11, FLOUR, 1.8)
    for i in range(46):
        fx = 571 + int(hr(i, 3) * 54)
        fy = COUNTER_Y - 5 + int(hr(i, 4) * 4)
        cv.put(fx, fy, FLOUR, 4.4)
    # pans a refredar en una reixa
    cv.hline(605, 635, COUNTER_Y - 6, STEEL, 4.0)
    for rx in range(606, 635, 4):
        cv.put(rx, COUNTER_Y - 5, STEEL, 2.4)
    for bx in (612, 627):
        cv.disc(bx, COUNTER_Y - 11, 7, 5, BREAD, lambda nx, ny: 3.8 - ny * 1.4 - nx * 0.5)
        cv.line(bx - 3, COUNTER_Y - 14, bx + 2, COUNTER_Y - 15, BREAD, 5.2)
        cv.line(bx - 1, COUNTER_Y - 12, bx + 4, COUNTER_Y - 13, BREAD, 5.0)
    # el corró
    hpipe(cv, 571, 595, COUNTER_Y - 17, 2, TEAK, 4.4)
    for hx in (566, 600):
        hpipe(cv, hx, hx + 4, COUNTER_Y - 17, 1, TEAK, 3.6)
    # el sac de farina, a terra
    cv.poly([(603, FLOOR_Y + 5), (627, FLOOR_Y + 5), (624, FLOOR_Y - 24), (606, FLOOR_Y - 24)], FLOUR,
            lambda x, y: 3.0 - (x - 603) * 0.04)
    cv.hline(605, 625, FLOOR_Y - 24, FLOUR, 2.0)
    for gx in (608, 612, 616, 620):                                       # el lligat de dalt
        cv.put(gx, FLOOR_Y - 26, FLOUR, 2.6)
    text(cv, 'FARINA', 603, FLOOR_Y - 13, None, 0, flat=(110, 60, 30))
    floor_shadow(cv, 615, FLOOR_Y + 5, 16, 3, 0.6)
    # prestatge d'espècies, amb la barana de mar
    box(cv, x0 + 3, 64, x1, 67, TEAK, 4.0)
    for i, sx in enumerate(range(x0 + 5, x1 - 5, 8)):
        jar = (REDP, YELL, SEAG, TEAK, REDP, YELL, SEAG, TEAK, REDP)[i % 9]
        cv.rect(sx, 54, sx + 4, 63, [(30, 30, 30), (90, 90, 86), (170, 170, 160), (220, 220, 210)], 2.6)
        cv.rect(sx, 58, sx + 4, 63, jar, 3.4)
        cv.vline(sx + 1, 55, 62, [(170, 170, 160), (240, 240, 236)], 1.6)
        cv.hline(sx, sx + 4, 54, DARK, 1.6)
        cv.hline(sx + 1, sx + 3, 60, WHITEP, 4.4)
    hpipe(cv, x0 + 3, x1, 61, 0, TEAK, 4.0)
    porthole(cv, PORT[0], PORT[1], PORT[2], rim=4, seed=3)


def floor_mat(cv):
    """La catifa de goma davant dels fogons."""
    x0, x1, y0, y1 = 221, 333, 211, 224
    cv.poly([(x0 + 3, y0), (x1 - 3, y0), (x1, y1), (x0, y1)], CAB,
            lambda x, y: 1.6 + (0.8 if (x // 4 + y // 3) % 2 else 0))
    cv.line(x0, y1, x1, y1, CAB, 0.6)
    cv.line(x0 + 3, y0, x1 - 3, y0, CAB, 3.0)


# ─── Muntatge ───────────────────────────────────────────────────────────────

def bg(cv):
    ceiling(cv)
    wall(cv)
    wear(cv, 0, 40, W - 1, 187, 27, seed=3, k=0.22)
    door(cv)
    dumbwaiter(cv)
    hatch(cv)
    voice_tube(cv, 211, 101)
    stove(cv)
    cold_room(cv)
    cupboard(cv)
    oven(cv)
    bakery(cv)
    for lx in LAMPS:
        lamp(cv, lx, LAMP_Y)
    mask = quarry(cv)
    foot_shadow(cv, 0, W - 1, FLOOR_Y + 1, 5, 0.45)
    shine(cv, mask, LAMPS, refl=0.12)
    floor_mat(cv)
    for lx in LAMPS:
        lamp_glow(cv, lx, LAMP_Y)


PROPS = {'safata': tray, 'armari_obert': cupboard_open,
         'ulls_dia': lambda cv: day_porthole(cv, PORT[0], PORT[1], PORT[2], seed=3)}   # Escenes 2 i 3: de dia


# ─── Animacions ─────────────────────────────────────────────────────────────

def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv


def _frames_vapor():
    """El vapor de l'olla gran puja cap a la campana (cada fil torna a sortir quan s'esvaeix)."""
    base = _base()
    ox, lid = 256, COUNTER_Y - 5 - 36
    n, wisps = 48, 30
    frames = []
    for i in range(n):
        cv = Canvas(light=LIGHT, img=base.img.copy())
        t = i / n
        for p in range(wisps):
            age = (t * 2 + p / wisps) % 1
            y = lid - 1 - age * 34
            x = ox - 4 + (hr(p, 1) - 0.5) * 11 + 3 * math.sin(age * 8 + p * 2.1)
            a = 0.95 * (1 - age) * min(1.0, age * 5)
            xx, yy = round(x), round(y)
            grow = 1 + int(age * 2.5)                                    # la bufada s'eixampla en pujar
            for dx in range(-1, grow + 1):
                for dy in (0, -1):
                    k = (1.0 if 0 <= dx < grow else 0.5) * (1.0 if dy == 0 else 0.6)
                    c = cv.get(xx + dx, yy + dy)
                    # sobre la rajola clara, el vapor es veu per la vora més blanca i una ombra grisa a sota
                    cv.flat(xx + dx, yy + dy, mix(c, (255, 255, 255), a * k))
                cv.flat(xx + dx, yy + 1, mix(cv.get(xx + dx, yy + 1), (150, 150, 146), a * 0.25))
        frames.append(_diff(cv.img, base.img))
    return frames


def _frames_forn():
    """El forn encès: la llum de dins tremola una mica."""
    global _OVEN_K
    base = _base()
    frames = []
    for k in (0.0, 0.2, 0.1, 0.3, 0.15, -0.1, 0.05, 0.25, 0.1, -0.05):
        _OVEN_K = k
        frames.append(_diff(_base().img, base.img))
    _OVEN_K = 0.0
    return frames


def _frames_fred():
    """Boira freda que s'escapa per sota la porta de la cambra i s'arrossega per terra."""
    base = _base()
    x0, _, x1, y1 = CFREDA
    n, wisps = 48, 30
    frames = []
    for i in range(n):
        cv = Canvas(light=LIGHT, img=base.img.copy())
        t = i / n
        for p in range(wisps):
            age = (t + p / wisps) % 1
            sx = x0 + 5 + hr(p, 3) * (x1 - x0 - 10)
            side = 1 if hr(p, 4) > 0.5 else -1
            x = sx + side * age * 27 + math.sin(age * 6 + p) * 2
            y = y1 + 1 + age * 11
            a = 0.8 * (1 - age) * min(1.0, age * 6)
            for dx, k in ((-2, 0.4), (-1, 0.7), (0, 1.0), (1, 1.0), (2, 0.9), (3, 0.6), (4, 0.3)):
                for dy, kk in ((0, 1.0), (-1, 0.5)):
                    xx, yy = round(x) + dx, round(y) + dy
                    if yy < H:
                        cv.flat(xx, yy, mix(cv.get(xx, yy), (214, 232, 244), a * k * kk))
        frames.append(_diff(cv.img, base.img))
    return frames


ANIMS = {'vapor': {'frames': _frames_vapor, 'frameDuration': 100},
         'forn': {'frames': _frames_forn, 'frameDuration': 150},
         'fred': {'frames': _frames_fred, 'frameDuration': 110}}

GEOMETRIA = {
    'things': {
        'porta': {'rect': (8, 61, 69, FLOOR_Y), 'walk': (40, 235)},
        'munta': {'rect': (MUNTA[0], MUNTA[1] - 11, MUNTA[2], CAB_IN[1] + 27), 'walk': (115, 237)},
        'safata': {'rect': (CAB_IN[0], CAB_IN[1] + 29, CAB_IN[2], CAB_IN[3]), 'walk': (115, 237)},
        'boca': {'rect': (200, 93, 221, 139), 'walk': (211, 237)},
        'cambra_freda': {'rect': (CFREDA[0] - 4, CFREDA[1] - 16, CFREDA[2] + 4, FLOOR_Y), 'walk': (364, 237)},
        'armari': {'rect': (ARMARI[0] - 3, ARMARI[1] - 19, ARMARI[2] + 3, FLOOR_Y), 'walk': (440, 237)},
        'forn': {'rect': (FORN[0], FORN[1], FORN[2], FLOOR_Y), 'walk': (519, 237)},
    },
    'spawns': {'iri': (440, 259), 'vet': (200, 256), 'tomas': (595, 248), 'nadia': (368, 245)},
    'walkable': [(8, 224), (635, 224), (635, 263), (8, 263)],
}
