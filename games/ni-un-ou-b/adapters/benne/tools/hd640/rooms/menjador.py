"""
Prova de resolució: el menjador de l'Arenga a 640×360 (la composició de hd/rooms/menjador.py ×4/3, dibuixada de
nou amb el detall que hi cap). Mateixes rampes, mateix prop (`ulls_dia`), mateixes animacions (`rellotge`, `tasses`)
i la mateixa capa del davant: la taula tapa les cames de qui seu a la banqueta (Escena 8).

  - a l'esquerra, la porta estanca de popa (COBERTA); la porta de vaivé de la CUINA i el passaplats;
  - la taula llarga amb la barana de mar, la banqueta capitonada i el pòster de la «CIMERA DELS OCEANS»;
  - el rellotge i el baròmetre, dos ulls de bou, l'aparador amb el bullidor i les tasses penjades;
  - a la dreta, la porta del passadís, oberta.
"""
import math

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from hd.pix import Canvas, Light, W, H, hr, mix, B4  # noqa: F401
from hd.rooms.arenga import CAB, DARK, WHITEP, REDP, YELL, BRASS, SEAG, WARM, box, rrect, bolt, hpipe, glow
from hd.rooms.comu import _diff, text, text_width
from hd.rooms.principal import (CREAM, TEAK, LINO, DOORP, in_door, sill, porthole, day_porthole, plaque,
                                floor_shadow, foot_shadow, second_hand, wear)
from hd.rooms.menjador import VINYL, STEEL, TILE, INWARM, SKYP, SEAP, WHALE, CARG, MUGS
from hd640.rooms.laboratori import ceiling, lamp, lamp_glow, shine, door_frame

CEIL_H = 24
FLOOR_Y = 203
BOTTOM = 260                      # per sota hi ha la barra de verbs
LAMP_Y = 27
LAMPS = (112, 261, 445, 579)
VP = (320, 40)

LIGHT = Light(ambient=-0.3, vignette=(61, 32), floor_fade=(251, 53))
for _x in LAMPS:
    LIGHT.point(_x, CEIL_H + 5, r=149, k=2.2, squash=1.1, down=True, power=1.5)
LIGHT.point(175, 133, r=53, k=0.5, power=2.0)                  # la llum de la cuina, pel passaplats

# la taula: cantell del darrere, cantell del davant i peu
T_X0, T_X1 = 200, 504
T_BACK, T_FRONT, T_FOOT = 163, 175, 224
D_POPA = (16, 83, 67, FLOOR_Y)
D_CUINA = (88, 85, 139, FLOOR_Y)
D_PASS = (579, 85, 627, FLOOR_Y)
PORTS = ((421, 72), (469, 72))
PORT_R = 11
CLOCK = (261, 61)
BARO = (288, 61)

_MUGS = {'on': True, 'dx': None}   # les tasses penjades (l'animació `tasses` les dibuixa a part)


# ─── Paret i terra (principal.py, a 640) ────────────────────────────────────

def wall(cv, lvl=4.6, frames=96, frame0=-13, seam=85, dado=171, seed=2):
    """Planxa pintada de crema: quadernes amb reblons, una soldadura i el sòcol de fusta (sense passamans)."""
    for y in range(CEIL_H, FLOOR_Y):
        for x in range(W):
            cv.put(x, y, CREAM, lvl + (hr(x // 3, y // 5, seed) - 0.5) * 0.25)
    for fx in range(frame0, W, frames):
        for x in range(max(0, fx), min(W - 1, fx + 5) + 1):
            d = x - fx
            for y in range(CEIL_H, dado):
                cv.put(x, y, CREAM, lvl + (0.9 if d == 0 else 0.5 if d == 1 else -0.6 if d >= 4 else 0.1))
        for y in range(CEIL_H + 10, dado - 5, 14):
            if 0 <= fx + 2 <= W - 1:
                bolt(cv, fx + 2, y, CREAM, lvl + 0.2)
    for x in range(W):
        cv.put(x, seam, CREAM, lvl - 1.1)
        cv.put(x, seam + 1, CREAM, lvl + 0.7 if hr(x // 2, seam) > 0.3 else lvl + 0.1)
    for y in range(dado, FLOOR_Y):
        for x in range(W):
            plank = (x + 9 * ((y - dado) // 8)) % 31
            v = 3.0 + (hr(x // 6, (y - dado) // 8, seed) - 0.5) * 0.6 - (0.9 if plank == 0 else 0)
            if (y - dado) % 8 == 0:
                v -= 0.8
            if hr(x // 2, y, 3) > 0.93:
                v += 0.5
            cv.put(x, y, TEAK, v)
    cv.hline(0, W - 1, dado, TEAK, 4.6)
    cv.hline(0, W - 1, dado + 1, TEAK, 3.8)
    cv.hline(0, W - 1, FLOOR_Y - 1, TEAK, 1.4)


def lino(cv, lvl=3.8, tile=45, check=0.5, seed=2):
    """Linòleum de rajoles en perspectiva, a escacs suaus. → màscara del terra."""
    mask = [[False] * W for _ in range(H)]
    for y in range(FLOOR_Y, H):
        d = y - VP[1]
        v = 3467 / d
        vn = 3467 / (d + 1)
        for x in range(W):
            u = VP[0] + (x - VP[0]) * 200 / d
            u2 = VP[0] + (x + 1 - VP[0]) * 200 / d
            lv = lvl + (hr(int(u // 4), int(v * 2), seed) - 0.5) * 0.45
            if (int(u // tile) + int(v * 2.0)) % 2:
                lv += check
            if int(u // tile) != int(u2 // tile):
                lv -= 0.9
            elif int(v * 2.0) != int(vn * 2.0):
                lv -= 0.7
            cv.put(x, y, LINO, lv)
            mask[y][x] = True
    cv.hline(0, W - 1, FLOOR_Y, LINO, lvl - 1.6)
    return mask


# ─── Portes ─────────────────────────────────────────────────────────────────

def leaf(cv, x0, y0, x1, y1, ramp=DOORP, lvl=3.6, r=9, handle='right', dogs=False, window=None, seed=0):
    """Fulla tancada (principal.leaf a 640): planxa amb plafó, maneta o palanques estanques i un ull de bou."""
    rrect(cv, x0, y0, x1, y1, r, ramp, lambda x, y: lvl - (y - y0) * 0.006 + (hr(x // 4, y // 7, seed) - 0.5) * 0.15)
    rrect(cv, x0 + 5, y0 + 5, x1 - 5, y1 - 5, max(2, r - 4), ramp, lambda x, y: lvl + 0.3 - (y - y0) * 0.006)
    cv.hline(x0 + 8, x1 - 8, y0 + 5, ramp, lvl + 1.3)
    cv.hline(x0 + 8, x1 - 8, y1 - 5, ramp, lvl - 1.1)
    cv.vline(x1 - 5, y0 + 10, y1 - 8, ramp, lvl - 0.8)
    cv.vline(x0 + 5, y0 + 10, y1 - 8, ramp, lvl + 0.8)
    cv.vline(x1, y0 + r, y1, ramp, lvl - 1.6)
    cv.vline(x0, y0 + r, y1, ramp, lvl + 0.6)
    # reblons del plafó
    for yy in range(y0 + 14, y1 - 8, 16):
        cv.put(x0 + 2, yy, ramp, lvl + 1.4)
        cv.put(x1 - 2, yy, ramp, lvl - 0.4)
    hx = x1 - 12 if handle == 'right' else x0 + 6
    my = (y0 + y1) // 2 + 6
    if dogs:
        for dy in (y0 + 16, my - 6, y1 - 26):
            box(cv, hx + 1, dy, hx + 6, dy + 12, CAB, 3.8)
            cv.vline(hx + 2, dy + 1, dy + 10, CAB, 5.2)
            cv.disc(hx + 3, dy + 6, 1.5, 1.5, CAB, 2.0)
        ox = x0 + 5 if handle == 'right' else x1 - 10
        for dy in (y0 + 16, y1 - 26):
            box(cv, ox, dy, ox + 4, dy + 9, CAB, 3.2)
            cv.put(ox + 2, dy + 4, CAB, 1.4)
    else:
        box(cv, hx, my - 5, hx + 4, my + 7, BRASS, 2.6)
        x_a, x_b = (hx - 8, hx + 3) if handle == 'right' else (hx + 1, hx + 12)
        cv.rect(x_a, my - 1, x_b, my + 1, BRASS, 4.2)
        cv.hline(x_a, x_b, my - 1, BRASS, 5.2)
        cv.hline(x_a, x_b, my + 2, BRASS, 1.6)
        cv.put(hx + 2, my + 4, DARK, 0.4)
    if window:
        cx, cy, wr, fn = window
        porthole(cv, cx, cy, wr, fn, rim=3)


def sign_box(cv, x0, y0, s, ramp, lvl, ink, pad=3):
    w = text_width(s)
    box(cv, x0, y0, x0 + w + pad * 2 + 1, y0 + 6 + pad * 2, ramp, lvl)
    cv.hline(x0 + 1, x0 + w + pad * 2, y0 + 1, ramp, lvl + 1.0)
    text(cv, s, x0 + pad + 1, y0 + pad + 2, None, 0, flat=ink)
    for bx in (x0 + 1, x0 + w + pad * 2):
        cv.put(bx, y0 + 6 + pad, ramp, lvl - 1.4)


def door_popa(cv):
    x0, y0, x1, y1 = D_POPA
    leaf(cv, x0, y0, x1, y1 - 8, CREAM, 4.4, dogs=True, handle='right', seed=5, window=(39, 115, 9, None))
    door_frame(cv, x0, y0, x1, y1, lvl=5.4)
    sill(cv, x0, x1, y1, CREAM, 3.6, h=8)
    for x in range(x0 + 4, x1 - 2, 9):
        cv.put(x, y1 - 5, CREAM, 5.0)
    sign_box(cv, x0 + 1, 59, 'COBERTA', SEAG, 3.4, (220, 236, 226))


def door_cuina(cv):
    """Porta de vaivé de la cuina, amb l'ull de bou (llum de dins) i la planxa de puntades a baix."""
    x0, y0, x1, y1 = D_CUINA

    def kitchen(c, x, y):
        c.put(x, y, INWARM, 6.4 - math.hypot(x - 112, y - 112) * 0.22, lit=0)
        if (x + y) % 7 == 0 and y > 115:                               # la rajola de dins, borrosa
            c.put(x, y, INWARM, 5.0, lit=0)
    leaf(cv, x0, y0, x1, y1 - 7, DOORP, 3.8, handle='left', seed=6, window=(114, 115, 9, kitchen))
    glow(cv, 114, 115, 16, (255, 200, 130), 0.18)
    box(cv, x0 + 4, y1 - 36, x1 - 4, y1 - 11, STEEL, 4.2)               # planxa de puntades
    for y in range(y1 - 32, y1 - 14, 4):
        for x in range(x0 + 7 + (y // 4) % 2 * 2, x1 - 5, 5):
            cv.put(x, y, STEEL, 5.8)
            cv.put(x + 1, y + 1, STEEL, 3.0)
    for bx in (x0 + 6, x1 - 6):
        for by in (y1 - 34, y1 - 13):
            cv.put(bx, by, STEEL, 6.4)
    # les rascades de les safates a l'altura de la mà
    for i in range(6):
        y = 150 + int(hr(i, 31) * 14)
        cv.hline(x0 + 8 + int(hr(i, 32) * 10), x0 + 18 + int(hr(i, 33) * 18), y, DOORP, 5.0)
    door_frame(cv, x0, y0, x1, y1)
    sill(cv, x0, x1, y1, h=7)
    plaque(cv, (x0 + x1) // 2, 64, 'CUINA')


def passaplats(cv):
    """El passaplats: finestreta a la cuina, amb el taulell d'acer, la persiana enrotllada i la boca del tub de veu."""
    x0, y0, x1, y1 = 152, 115, 200, 152
    for y in range(y0, y1):
        for x in range(x0, x1 + 1):
            tile = (x - x0) % 8 == 0 or (y - y0) % 8 == 0
            cv.put(x, y, TILE, 3.6 - (y - y0) * 0.022 - (1.0 if tile else 0) + 1.2 * math.exp(-((x - 176) / 18) ** 2), lit=0.4)
    # la barra dels estris i els cassons penjats a dins
    cv.hline(x0 + 2, x1 - 2, y0 + 2, STEEL, 4.6, lit=0.3)
    for i, hx in enumerate((162, 170, 186)):
        cv.vline(hx, y0 + 3, y0 + 8 + i * 3, STEEL, 3.0, lit=0.3)
        cv.disc(hx, y0 + 12 + i * 3, 3 + (i % 2), 3, STEEL, lambda nx, ny: 4.2 - nx - ny, lit=0.3)
        cv.put(hx - 1, y0 + 11 + i * 3, STEEL, 6.2, lit=0.3)
    cv.vline(178, y0 + 3, y0 + 14, STEEL, 3.6, lit=0.3)                 # el cullerot
    cv.disc(178, y0 + 16, 2, 2, STEEL, 4.0, lit=0.3)
    # la boca del tub de veu, a l'altra banda
    cv.vline(193, y0, 129, BRASS, 3.2, lit=0.5)
    cv.vline(194, y0, 129, BRASS, 2.0, lit=0.5)
    cv.disc(193, 133, 4, 4, BRASS, lambda nx, ny: 3.6 - nx - ny, lit=0.5)
    cv.disc(193, 133, 2, 2, DARK, 0.8, lit=0)
    # marc d'acer, persiana a dalt i taulell
    box(cv, x0 - 4, y0 - 4, x1 + 4, y0 - 1, STEEL, 4.4)
    box(cv, x0 - 4, y0 - 12, x1 + 4, y0 - 4, STEEL, 3.2)
    for y in range(y0 - 11, y0 - 4, 2):
        cv.hline(x0 - 3, x1 + 3, y, STEEL, 4.4)
    cv.rect(x1 - 8, y0 - 3, x1 - 6, y0, BRASS, 3.6)                     # el ganxo de la persiana
    cv.vline(x0 - 1, y0, y1, STEEL, 4.6)
    cv.vline(x0 - 2, y0, y1, STEEL, 3.0)
    cv.vline(x1 + 1, y0, y1, STEEL, 2.2)
    box(cv, x0 - 7, y1, x1 + 7, y1 + 4, STEEL, 4.8)
    cv.hline(x0 - 6, x1 + 6, y1 + 1, STEEL, 6.0)
    cv.darken(x0 - 6, y1 + 5, x1 + 6, y1 + 8, 0.6)
    for ex in (x0 - 1, x1 + 1):                                         # escaires
        cv.line(ex, y1 + 5, ex + (5 if ex < x1 else -5), y1 + 13, STEEL, 3.0)
        cv.vline(ex, y1 + 5, y1 + 13, STEEL, 3.4)
    # una safata amb dues tasses i un plat al taulell
    cv.rect(160, y1 - 2, 190, y1 - 1, STEEL, 5.4)
    for mx, m in ((164, MUGS[2]), (180, MUGS[0])):
        cv.rect(mx, y1 - 8, mx + 5, y1 - 3, m, lambda x, y, mx=mx: 3.6 - (x - mx) * 0.2)
        cv.vline(mx + 6, y1 - 7, y1 - 5, m, 2.6)
        cv.hline(mx, mx + 5, y1 - 8, m, 1.4)
    cv.disc(173, y1 - 3, 3, 1, WHITEP, 5.0)


def door_passadis(cv):
    """La porta del passadís, oberta: a l'altra banda, la paret crema, el passamans i el linòleum."""
    x0, y0, x1, y1 = D_PASS
    cx = (x0 + x1) // 2
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if in_door(x, y, x0, y0, x1, y1, 11):
                if y >= 171:
                    v = 1.8 if (y - 171) % 8 else 1.2
                    cv.put(x, y, TEAK, v + 0.6, lit=0.3)
                else:
                    v = 3.0 - (y - y0) / 160 + 0.6 * math.exp(-((x - cx) / 16) ** 2)
                    cv.put(x, y, CREAM, v + (0.6 if x % 24 == 4 else 0), lit=0.3)
    hpipe(cv, x0, x1, 144, 2, TEAK, 3.0)
    for x in range(x0 + 8, x1, 22):
        cv.rect(x, 147, x + 1, 150, BRASS, 2.6, lit=0.3)
    cv.disc(cx, 93, 5, 2, [(160, 120, 60), (255, 230, 170), (255, 250, 230)], 1.4, lit=0)
    glow(cv, cx, 96, 19, (255, 210, 140), 0.3)
    # la fulla, oberta contra la paret de la dreta (de cantó)
    cv.poly([(x1 + 4, y0 - 1), (x1 + 12, y0 + 5), (x1 + 12, y1 - 7), (x1 + 4, y1 - 3)], DOORP,
            lambda x, y: 2.4 + (x - x1) * 0.07)
    cv.vline(x1 + 12, y0 + 5, y1 - 7, DOORP, 1.2)
    for dy in (y0 + 22, y1 - 30):
        box(cv, x1 + 6, dy, x1 + 10, dy + 4, CAB, 3.0)
    door_frame(cv, x0, y0, x1, y1)
    sill(cv, x0, x1, y1, h=7)
    sign_box(cv, x0 + 4, 64, 'PASSADÍS', WHITEP, 4.2, (24, 28, 30))


# ─── El pòster, el rellotge, els ulls de bou i l'aparador ───────────────────

POSTER = (309, 32, 392, 101)


def poster(cv):
    """«CIMERA DELS OCEANS · PORT HALLEN», patrocinada per Skarn: una balena somrient i un cotxe elèctric."""
    x0, y0, x1, y1 = POSTER
    cv.darken(x0 + 3, y0 + 3, x1 + 3, y1 + 3, 0.7)
    box(cv, x0, y0, x1, y1, WHITEP, 4.8, edge=False)
    cv.hline(x0, x1, y1, WHITEP, 3.4)
    # capçalera blau marí amb el títol
    cv.rect(x0 + 3, y0 + 3, x1 - 3, y0 + 20, SEAP, 1.4)
    for i, s in enumerate(('CIMERA DELS', 'OCEANS')):
        text(cv, s, (x0 + x1 + 1) // 2 - text_width(s) // 2, y0 + 5 + i * 8, None, 0, flat=(240, 244, 248))
    # el dibuix: cel, mar, la balena i el cotxe
    ix0, iy0, ix1, iy1 = x0 + 3, y0 + 22, x1 - 3, y0 + 51
    hz = iy0 + 17
    for y in range(iy0, iy1 + 1):
        for x in range(ix0, ix1 + 1):
            if y < hz:
                cv.put(x, y, SKYP, 3.6 - (hz - y) * 0.09)
            else:
                cv.put(x, y, SEAP, 3.2 - (y - hz) * 0.11 + (0.8 if (x + y * 3) % 11 == 0 else 0))
    cv.disc(ix1 - 10, iy0 + 6, 4, 4, YELL, 5.0)                         # el sol, amb raigs
    for a in range(0, 360, 45):
        cv.put(ix1 - 10 + round(math.cos(math.radians(a)) * 6), iy0 + 6 + round(math.sin(math.radians(a)) * 6), YELL, 4.4)
    for nx in (ix0 + 6, ix0 + 30):                                      # dos núvols de dibuix
        cv.disc(nx, iy0 + 5, 5, 2, WHITEP, 5.2)
        cv.disc(nx + 4, iy0 + 4, 3, 2, WHITEP, 5.4)
    # la balena, que somriu
    wx, wy = x0 + 27, hz + 1
    cv.disc(wx, wy, 16, 8, WHALE, lambda nx, ny: 3.4 - ny * 1.4 - nx * 0.3)
    cv.disc(wx - 2, wy + 4, 11, 3, WHALE, 4.4)                           # la panxa, més clara, amb ratlles
    for k in range(-8, 8, 3):
        cv.put(wx + k, wy + 5, WHALE, 3.0)
    cv.poly([(wx + 13, wy - 1), (wx + 22, wy - 9), (wx + 21, wy)], WHALE, 3.0)      # cua
    cv.poly([(wx + 14, wy - 2), (wx + 23, wy + 3), (wx + 13, wy + 3)], WHALE, 2.6)
    cv.poly([(wx - 2, wy + 5), (wx + 4, wy + 10), (wx + 5, wy + 6)], WHALE, 2.2)    # l'aleta
    cv.flat(wx - 9, wy - 3, (240, 244, 248))                             # l'ull, amb brillantor
    cv.put(wx - 9, wy - 2, DARK, 0)
    cv.put(wx - 10, wy - 2, DARK, 0)
    for i in range(8):                                                  # el somriure
        cv.put(wx - 13 + i, wy + 1 + (1 if 1 <= i <= 6 else 0), DARK, 0.5)
    cv.put(wx - 13, wy, DARK, 0.5)
    for i in range(4):                                                  # el brollador
        cv.put(wx - 2 - i, wy - 9 - i, SKYP, 4.8)
        cv.put(wx + 1 + i, wy - 9 - i, SKYP, 4.8)
    cv.put(wx - 1, wy - 9, SKYP, 4.8)
    # el cotxe elèctric, verd, amb el cable i el llamp
    cx, cy = x1 - 31, hz
    cv.rect(cx, cy + 1, cx + 20, cy + 6, CARG, 3.4)
    cv.hline(cx, cx + 20, cy + 1, CARG, 4.2)
    cv.poly([(cx + 4, cy + 1), (cx + 7, cy - 4), (cx + 15, cy - 4), (cx + 17, cy + 1)], CARG, 3.8)
    cv.rect(cx + 8, cy - 3, cx + 11, cy, SKYP, 4.4)
    cv.rect(cx + 13, cy - 3, cx + 15, cy, SKYP, 4.4)
    cv.put(cx + 20, cy + 3, YELL, 5.0)                                  # el far
    for wxx in (cx + 4, cx + 16):
        cv.disc(wxx, cy + 6, 2.5, 2.5, DARK, 1.0)
        cv.put(wxx, cy + 6, WHITEP, 3.6)
    cv.line(cx + 20, cy + 4, cx + 24, cy + 9, DARK, 1.0)                # el cable, que va a parar al mar
    cv.line(cx + 24, cy + 9, cx + 26, cy + 12, DARK, 1.0)
    cv.poly([(cx + 10, cy - 13), (cx + 7, cy - 8), (cx + 11, cy - 8), (cx + 8, cy - 4)], YELL, 5.0)
    # peu: PORT HALLEN, la data i el logotip de Skarn
    text(cv, 'PORT HALLEN', x0 + 4, y1 - 17, None, 0, flat=(20, 50, 90))
    cv.hline(x0 + 4, x0 + 4 + text_width('PORT HALLEN'), y1 - 11, SEAP, 2.4)
    text(cv, '14-16', x0 + 4, y1 - 9, None, 0, flat=(90, 100, 110))
    sk = text_width('SKARN')
    text(cv, 'SKARN', x1 - 4 - sk, y1 - 9, None, 0, flat=(30, 110, 60))
    cv.poly([(x1 - 4 - sk - 8, y1 - 3), (x1 - 4 - sk - 5, y1 - 10), (x1 - 4 - sk - 2, y1 - 3)], CARG, 3.4)
    # xinxetes i un cantó despenjat
    for px, py in ((x0 + 2, y0 + 2), (x1 - 2, y0 + 2)):
        cv.disc(px, py, 2, 2, REDP, 4.6)
        cv.put(px - 1, py - 1, REDP, 6.0)
    cv.poly([(x1 - 6, y1), (x1, y1 - 6), (x1, y1)], CREAM, 4.4)
    cv.line(x1 - 6, y1, x1, y1 - 6, WHITEP, 3.0)


def clocks(cv):
    """El rellotge i el baròmetre de llautó, de bracet."""
    cx, cy = CLOCK
    cv.disc(cx, cy, 9, 9, BRASS, lambda nx, ny: 3.4 - nx - ny)
    cv.disc(cx, cy, 7, 7, WHITEP, 4.6)
    for a in range(0, 360, 30):
        cv.put(cx + round(math.sin(math.radians(a)) * 6), cy - round(math.cos(math.radians(a)) * 6), DARK, 0.6 if a % 90 else 0)
    cv.line(cx, cy, cx + 4, cy - 2, DARK, 0)                            # les deu i deu
    cv.line(cx, cy, cx, cy - 5, DARK, 0)
    cv.put(cx, cy, BRASS, 4.0)
    bx, by = BARO
    cv.disc(bx, by, 9, 9, BRASS, lambda nx, ny: 3.4 - nx - ny)
    cv.disc(bx, by, 7, 7, WHITEP, 4.6)
    for a in range(-120, 121, 20):                                      # l'escala, de pluja a bon temps
        r = math.radians(a)
        cv.put(bx + round(math.sin(r) * 6), by - round(math.cos(r) * 6), REDP if a < -40 else DARK, 2.6 if a < -40 else 0.8)
    cv.line(bx, by, bx - 4, by - 3, DARK, 0)                            # baixant: mal temps
    cv.line(bx, by, bx + 2, by - 4, BRASS, 4.4)                         # l'agulla de referència
    cv.put(bx, by, BRASS, 4.0)
    box(cv, cx + 9, cy - 1, bx - 9, cy + 1, TEAK, 3.6)                  # la tauleta de fusta que els aguanta
    box(cv, cx - 12, cy + 11, bx + 12, cy + 14, TEAK, 3.8)
    for px in (cx, bx):
        cv.vline(px, cy + 9, cy + 11, BRASS, 3.0)


def sideboard(cv):
    """L'aparador: el bullidor del te, el penjador de tasses, la prestatgeria."""
    x0, x1, top = 509, 568, 157
    mid = (x0 + x1) // 2
    box(cv, x0, top, x1, FLOOR_Y - 1, TEAK, 3.4, grad=0.8)
    cv.rect(x0 - 3, top - 4, x1 + 3, top, TEAK, 4.4)
    cv.hline(x0 - 3, x1 + 3, top - 4, TEAK, 5.4)
    cv.rect(x0 - 3, top - 8, x0 - 2, top - 4, TEAK, 4.0)                # barana de mar
    cv.rect(x1 + 2, top - 8, x1 + 3, top - 4, TEAK, 3.0)
    cv.hline(x0 - 3, x1 + 3, top - 8, TEAK, 4.6)
    cv.vline(mid, top + 5, FLOOR_Y - 5, TEAK, 1.6)
    for px0, px1 in ((x0 + 4, mid - 4), (mid + 4, x1 - 4)):
        box(cv, px0, top + 5, px1, FLOOR_Y - 7, TEAK, 3.0)
        rrect(cv, px0 + 4, top + 10, px1 - 4, FLOOR_Y - 12, 2, TEAK, 3.4)
    for hx in (mid - 6, mid + 4):
        cv.rect(hx, top + 18, hx + 2, top + 24, BRASS, 4.0)
        cv.put(hx, top + 18, BRASS, 5.6)
    # el bullidor (d'acer) amb l'aixeta, el nivell i el pilot vermell
    bx = 525
    for y in range(top - 32, top - 4):
        for x in range(bx - 9, bx + 10):
            u = (x - bx) / 9.5
            cv.put(x, y, STEEL, 5.6 + 1.8 * (-0.3 - u) - 1.0 * u * u)
    cv.disc(bx, top - 32, 9, 3, STEEL, 6.4)
    box(cv, bx - 3, top - 37, bx + 3, top - 33, CAB, 2.6)
    cv.hline(bx - 2, bx + 2, top - 36, CAB, 4.0)
    cv.rect(bx - 6, top - 28, bx - 5, top - 10, [(30, 30, 30), (90, 70, 40), (170, 130, 60)], 1.4)    # el nivell (vidre)
    cv.rect(bx - 6, top - 18, bx - 5, top - 10, [(30, 30, 30), (90, 70, 40), (170, 130, 60)], 2.4)
    cv.hline(bx - 2, bx + 3, top - 12, CAB, 3.0)
    cv.vline(bx - 2, top - 12, top - 9, CAB, 2.4)
    cv.rect(bx + 3, top - 11, bx + 4, top - 10, CAB, 4.0)
    cv.flat(bx + 6, top - 23, (255, 70, 40))
    glow(cv, bx + 6, top - 23, 6, (255, 80, 50), 0.5)
    cv.hline(bx - 9, bx + 9, top - 5, STEEL, 2.6)
    # tasses al costat, una amb la bossa de te
    for i, mx in enumerate((543, 553)):
        m = MUGS[(i + 1) % 4]
        cv.rect(mx, top - 9, mx + 5, top - 4, m, lambda x, y, mx=mx: 3.6 - (x - mx) * 0.2)
        cv.hline(mx, mx + 5, top - 9, m, 1.4)
        cv.vline(mx + 6, top - 8, top - 6, m, 2.6)
    cv.vline(545, top - 13, top - 9, WHITEP, 4.0)
    cv.rect(544, top - 15, 546, top - 13, YELL, 4.4)
    cv.disc(563, top - 5, 3, 1, WHITEP, 4.6)                            # el sucrer
    # el penjador de tasses: la barra i els ganxos (les tasses, a hanging_mugs)
    hpipe(cv, x0, x1, 107, 1, TEAK, 3.6)
    for i, mx in enumerate(range(x0 + 4, x1 - 4, 11)):
        cv.vline(mx + 3, 108, 110, BRASS, 3.2)
        cv.put(mx + 4, 111, BRASS, 4.0)
    if _MUGS['on']:
        hanging_mugs(cv, _MUGS['dx'])
    # prestatge: llibres, una ràdio de butxaca, jocs de taula
    box(cv, x0 - 3, 96, x1 + 3, 99, TEAK, 4.0)
    cv.hline(x0 - 3, x1 + 3, 96, TEAK, 5.2)
    cv.rect(x0 - 3, 88, x0 - 2, 96, TEAK, 3.0)
    cv.rect(x1 + 2, 88, x1 + 3, 96, TEAK, 3.0)
    cv.hline(x0 - 3, x1 + 3, 89, BRASS, 3.0)                           # la barana del prestatge
    books = ((SEAP, 9), (VINYL, 8), (CARG, 7), (MUGS[3], 10), (WHALE, 8), (VINYL, 7), (SEAP, 9))
    bx = x0 + 1
    for i, (ramp, h) in enumerate(books):
        cv.rect(bx, 95 - h - 4, bx + 3, 95, ramp, 2.8 + (0.6 if i % 2 else 0))
        cv.vline(bx, 95 - h - 4, 95, ramp, 3.8)
        cv.hline(bx + 1, bx + 2, 95 - h - 1, WHITEP, 3.0)
        bx += 5
    cv.poly([(bx, 95), (bx + 2, 95), (bx + 9, 86), (bx + 7, 85)], VINYL, 3.0)       # un llibre caigut de costat
    box(cv, bx + 10, 84, bx + 28, 95, VINYL, 3.2)                         # un joc de taula (capsa)
    cv.hline(bx + 12, bx + 26, 89, YELL, 3.6)
    box(cv, bx + 12, 78, bx + 26, 83, SEAP, 3.0)
    cv.rect(bx + 14, 80, bx + 17, 81, WHITEP, 4.0)


def hanging_mugs(cv, dx=None):
    """Les cinc tasses penjades del ganxo. `dx`: quant es gronxa cadascuna (llista) o res."""
    x0, x1 = 509, 568
    for i, mx in enumerate(range(x0 + 4, x1 - 4, 11)):
        m = MUGS[i % 4]
        d = dx[i] if dx else 0
        mx += d
        cv.rect(mx, 112, mx + 6, 119, m, lambda x, y, mx=mx: 3.4 - (x - mx) * 0.18)
        cv.hline(mx, mx + 6, 119, m, 1.6)
        cv.hline(mx + 1, mx + 5, 112, m, 4.2)
        cv.vline(mx + 7, 113, 116, m, 2.4)
        cv.put(mx + 3, 111, BRASS, 3.6)


# ─── La taula i la banqueta ─────────────────────────────────────────────────

def bench(cv):
    """La banqueta entapissada contra la paret, darrere la taula (només se'n veu el respatller)."""
    x0, x1, y0 = T_X0 + 8, T_X1 - 8, 139
    rrect(cv, x0, y0, x1, FLOOR_Y - 1, 4, VINYL, lambda x, y: 3.6 - (y - y0) * 0.015)
    for bx in range(x0 + 2, x1 - 4, 51):                               # capitonat
        cv.vline(bx + 48, y0 + 4, FLOOR_Y - 8, VINYL, 2.0)
        cv.vline(bx + 49, y0 + 4, FLOOR_Y - 8, VINYL, 4.2)
        for by in (y0 + 13, y0 + 30, y0 + 47):
            cv.put(bx + 24, by, VINYL, 1.6)
            cv.put(bx + 25, by, VINYL, 4.4)
            cv.line(bx + 20, by - 3, bx + 24, by, VINYL, 2.8)
            cv.line(bx + 29, by - 3, bx + 25, by, VINYL, 2.8)
    cv.hline(x0 + 4, x1 - 4, y0 + 1, VINYL, 5.0)
    for i in range(16):                                                 # esquerdes del vinil i un pedaç
        x = x0 + 8 + int(hr(i, 1) * (x1 - x0 - 16))
        y = y0 + 8 + int(hr(i, 2) * 38)
        cv.line(x, y, x + 3, y + 1 + (i % 2), VINYL, 2.0)
    box(cv, 300, y0 + 20, 312, y0 + 28, [(30, 10, 8), (60, 18, 14), (90, 30, 22), (120, 44, 30)], 2.4)
    for x in range(301, 312, 2):
        cv.put(x, y0 + 20, WHITEP, 2.6)
    box(cv, x0 - 3, y0 - 5, x1 + 3, y0, TEAK, 4.0)                       # el cantell de fusta de dalt
    cv.hline(x0 - 3, x1 + 3, y0 - 5, TEAK, 5.4)


def table(cv):
    """La taula llarga, fixada a terra, amb barana de mar i un faldó de fusta fins a terra."""
    floor_shadow(cv, (T_X0 + T_X1) // 2, T_FOOT + 1, (T_X1 - T_X0) // 2 + 10, 7, 0.8)
    for y in range(T_FRONT + 4, T_FOOT + 1):
        for x in range(T_X0 - 3, T_X1 + 4):
            panel = (x - T_X0 + 3) % 76
            v = 2.8 + (hr(x // 3, y // 10, 4) - 0.5) * 0.4 - (y - T_FRONT) * 0.009
            if hr(x // 2, y, 5) > 0.94:                                     # la veta
                v += 0.4
            if panel < 3:
                v = 1.6 if panel == 0 else 3.8 if panel == 1 else 3.2
            cv.put(x, y, TEAK, v)
    for px in range(T_X0 - 3, T_X1, 76):                                # motllura dels plafons
        rrect(cv, px + 8, T_FRONT + 10, px + 68, T_FOOT - 10, 2, TEAK, 3.1)
        cv.hline(px + 10, px + 66, T_FRONT + 10, TEAK, 1.8)
        cv.vline(px + 8, T_FRONT + 12, T_FOOT - 12, TEAK, 1.8)
        cv.hline(px + 10, px + 66, T_FOOT - 10, TEAK, 3.8)
    cv.hline(T_X0 - 3, T_X1 + 3, T_FOOT, TEAK, 1.0)
    cv.rect(T_X0 - 3, T_FOOT - 5, T_X1 + 3, T_FOOT - 1, TEAK, 2.0)       # sòcol
    # el sobre (perspectiva: el cantell del darrere és més curt)
    cv.poly([(T_X0 + 4, T_BACK), (T_X1 - 4, T_BACK), (T_X1 + 3, T_FRONT), (T_X0 - 3, T_FRONT)], TEAK,
            lambda x, y: 4.4 + (y - T_BACK) * 0.045 + (hr(x // 8, y // 3, 7) - 0.5) * 0.5)
    for i in range(20):                                                 # anelles de tasses i ratllades
        x = T_X0 + 12 + int(hr(i, 11) * (T_X1 - T_X0 - 24))
        y = T_BACK + 2 + int(hr(i, 12) * 8)
        cv.ring(x, y, 3, TEAK, 3.4, step=30) if i % 3 else cv.line(x, y, x + 6, y, TEAK, 3.6)
    cv.rect(T_X0 - 3, T_FRONT, T_X1 + 3, T_FRONT + 3, TEAK, 5.0)
    cv.hline(T_X0 - 3, T_X1 + 3, T_FRONT, TEAK, 6.0)
    cv.hline(T_X0 - 3, T_X1 + 3, T_FRONT + 4, TEAK, 1.2)
    cv.hline(T_X0 + 4, T_X1 - 4, T_BACK - 1, TEAK, 4.8)
    cv.hline(T_X0 + 4, T_X1 - 4, T_BACK - 2, TEAK, 3.4)
    for px in range(T_X0 + 4, T_X1 - 3, 38):                           # els puntals de la barana
        cv.vline(px, T_BACK - 2, T_BACK, TEAK, 2.6)


def table_things(cv):
    """Damunt la taula: la tetera, tasses, el sucrer, la baralla, la carta nàutica doblegada i un cendrer."""
    tx, ty = 344, 165
    cv.disc(tx, ty - 5, 8, 7, TEAK, lambda nx, ny: 4.4 - nx * 1.2 - ny * 1.2)
    cv.disc(tx - 3, ty - 8, 2, 2, TEAK, 5.6)
    cv.hline(tx - 7, tx + 7, ty - 4, [(40, 16, 10), (90, 40, 20), (140, 70, 36)], 1.6)   # la franja de la terrissa
    cv.disc(tx, ty - 12, 3, 1, TEAK, 5.0)
    cv.put(tx, ty - 14, TEAK, 5.6)
    cv.line(tx + 8, ty - 6, tx + 13, ty - 11, TEAK, 4.0)
    cv.line(tx + 8, ty - 5, tx + 13, ty - 10, TEAK, 2.6)
    cv.ring(tx - 9, ty - 5, 3, TEAK, 3.0, step=20)
    for i, (mx, my) in enumerate(((243, 168), (285, 165), (395, 168), (440, 165), (469, 169))):
        m = MUGS[i % 4]
        cv.rect(mx, my - 7, mx + 6, my, m, lambda x, y, mx=mx: 3.6 - (x - mx) * 0.2)
        cv.hline(mx, mx + 6, my - 7, m, 1.4)
        cv.hline(mx + 1, mx + 5, my - 6, [(30, 16, 8), (60, 34, 16)], 0.8)   # el te, a dins
        cv.vline(mx + 7, my - 6, my - 3, m, 2.6)
        cv.put(mx + 8, my - 5, m, 2.0)
    cv.disc(315, 164, 4, 4, WHITEP, lambda nx, ny: 4.4 - nx - ny)       # sucrer, amb la cullereta
    cv.line(316, 160, 320, 156, STEEL, 5.0)
    for i in range(4):                                                  # la baralla, mig escampada
        x = 409 + i * 5
        box(cv, x, 169 - i, x + 5, 172 - i, WHITEP, 4.6, edge=False)
        cv.put(x + 2, 170 - i, REDP if i % 2 else DARK, 2.0)
    # carta nàutica doblegada, amb un llapis
    cv.poly([(261, 172), (275, 166), (301, 168), (291, 173)],
            [(60, 70, 60), (140, 150, 130), (200, 206, 186), (230, 232, 214)], 2.8)
    cv.line(275, 166, 280, 172, SEAP, 3.0)
    cv.line(283, 169, 292, 168, SEAP, 2.4)
    cv.line(266, 170, 278, 168, YELL, 4.2)
    cv.disc(486, 168, 4, 2, STEEL, 4.0)                                 # el cendrer de llauna
    cv.disc(486, 168, 2, 1, DARK, 1.4)


_DAVANT = ((T_X0 - 4, T_BACK - 4, T_X1 + 4, T_FOOT + 1), (334, 149, 360, T_BACK), (237, 155, 492, T_BACK))
FRONT = {'mask': lambda x, y: any(x0 <= x <= x1 and y0 <= y <= y1 for x0, y0, x1, y1 in _DAVANT),
         'baseline': 216, 'zIndex': 20}


# ─── Muntatge ───────────────────────────────────────────────────────────────

def bg(cv):
    ceiling(cv)
    wall(cv)
    wear(cv, 0, 40, W - 1, 168, 32, seed=2, k=0.22)
    door_popa(cv)
    door_cuina(cv)
    passaplats(cv)
    door_passadis(cv)
    for i, (px, py) in enumerate(PORTS):
        porthole(cv, px, py, PORT_R, rim=4, seed=i + 1)
    poster(cv)
    clocks(cv)
    bench(cv)
    sideboard(cv)
    for lx in LAMPS:
        lamp(cv, lx, LAMP_Y)
    mask = lino(cv)
    for x0, _, x1, _ in (D_POPA, D_CUINA, D_PASS):
        foot_shadow(cv, x0 - 4, x1 + 4, FLOOR_Y + 1, 4, 0.5)
    foot_shadow(cv, 0, W - 1, FLOOR_Y + 1, 5, 0.35)
    foot_shadow(cv, 506, 571, FLOOR_Y + 1, 7, 0.6)
    shine(cv, mask, LAMPS)
    table(cv)
    table_things(cv)
    for lx in LAMPS:
        lamp_glow(cv, lx, LAMP_Y)


def ulls_dia(cv):
    """Escenes 2 i 3, de dia: els dos ulls de bou i el de la porta de coberta, clars."""
    for i, (px, py) in enumerate(PORTS):
        day_porthole(cv, px, py, PORT_R, seed=i + 1)
    day_porthole(cv, 39, 115, 9)


PROPS = {'ulls_dia': ulls_dia}


# ─── Animacions ─────────────────────────────────────────────────────────────

def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv


def _frames_rellotge():
    """El rellotge del menjador: l'agulla dels segons (un fotograma per segon)."""
    base = _base()
    frames = []
    for s in range(60):
        cv = Canvas(light=LIGHT, img=base.img.copy())
        second_hand(cv, CLOCK[0], CLOCK[1], s, r=6)
        frames.append(_diff(cv.img, base.img))
    return frames


def _frames_tasses():
    """Les tasses penjades es gronxen amb el balanceig, cadascuna una mica endarrerida respecte de l'anterior."""
    base = _base()
    _MUGS['on'] = False
    try:
        bare = _base()
    finally:
        _MUGS['on'] = True
    frames = []
    for i in range(24):
        t = 2 * math.pi * i / 24
        dx = [round(1.7 * math.sin(t - k * 0.35)) for k in range(5)]
        cv = Canvas(light=LIGHT, img=bare.img.copy())
        hanging_mugs(cv, dx)
        frames.append(_diff(cv.img, base.img))
    return frames


ANIMS = {'rellotge': {'frames': _frames_rellotge, 'frameDuration': 1000},
         'tasses': {'frames': _frames_tasses, 'frameDuration': 160}}


# ─── Geometria (640×360) ────────────────────────────────────────────────────

GEOMETRIA = {
    'things': {
        'porta_popa': {'rect': (8, 59, 72, FLOOR_Y), 'walk': (40, 235)},
        'porta_cuina': {'rect': (83, 61, 144, FLOOR_Y), 'walk': (113, 235)},
        'passaplats': {'rect': (144, 101, 208, 160), 'walk': (175, 237)},
        'poster': {'rect': POSTER, 'walk': (349, 248)},
        'taula': {'rect': (T_X0 - 3, T_BACK - 3, T_X1 + 3, T_FOOT), 'walk': (349, 248)},
        'porta_passadis': {'rect': (571, 61, 632, FLOOR_Y), 'walk': (600, 235)},
    },
    'spawns': {'iri': (560, 253), 'vet': (147, 256),
               'capitana': (235, 208), 'bastida': (280, 208), 'marcel': (325, 208), 'tomas': (373, 208),
               'juana': (419, 208), 'nadia': (464, 208)},
    'walkable': [(8, 221), (189, 221), (189, 232), (515, 232), (515, 221), (635, 221), (635, 263), (8, 263)],
}
