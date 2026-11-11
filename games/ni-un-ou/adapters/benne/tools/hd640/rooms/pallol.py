"""
Prova de resolució: el pallol de l'Arenga a 640×360 (la composició de hd/rooms/pallol.py ×4/3, dibuixada de nou
amb el detall que hi cap). Mateixes rampes, mateix prop i mateixes animacions.

  - la porta del passadís, tancada, amb l'inventari clavat damunt (ara s'hi llegeix PALLOL);
  - els prestatges: pintura, brotxes, cinta americana, la caixa de DRAPS; caps enrotllats; bobines de cable
    apantallat i capses de connectors amb etiqueta (BNC, PL, N, SMA); la caixa d'eines, galledes, un cap gruixut;
  - el tauler dels CADENATS (cinc, i un ganxo buit), les defenses, el salvavides ARENGA, el pal de fregar i el bidó;
  - a terra, el rotllo de cap d'amarrar i la caixa de peix on seu el Marcel (Escena 6).
Prop: `cadenat_sise`. Animacions: `defenses` (es gronxen amb el balanceig) i `pols` (a la llum de l'esquerra).

Al principi hi ha les peces de hd/rooms/sota.py adaptades a 640 (paret de planxa, sostre, llums de gàbia, terra
estriat, marcs de porta, rètols, escales de mà...): caixa_cadenes i diposit2 de 640 les importen d'aquí.
"""
import math

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from hd.pix import Canvas, Light, W, H, hr, mix, B4, RUST, WALNUT, PAPER, ORANGE
from hd.rooms.arenga import (WALL, ENG, DECK, CAB, DARK, WHITEP, YELL, REDP, SEAG, FUEL, BRASS, WARM,
                             box, rrect, bolt, hpipe, vpipe, glow)
from hd.rooms.comu import _diff, text, text_width

FLOOR_Y = 203                     # 152 × 4/3
BOTTOM = 260                      # per sota hi ha la barra de verbs
LAMPC = [(120, 90, 40), (200, 160, 80), (250, 220, 150), (255, 246, 220)]


# ═══ Peces de la coberta de sota, a 640 (com hd/rooms/sota.py) ═══════════════

def plate_wall(cv, x0, x1, ramp=WALL, lvl=3.1, y0=0, y1=FLOOR_Y, frames=85, frame0=-11, seams=(85, 149), socle=179,
               rust=36, seed=0):
    """Paret de planxa pintada: quadernes amb dues files de reblons, soldadures amb cordó, sòcol gastat i rovell."""
    for y in range(y0, y1):
        for x in range(x0, x1 + 1):
            v = lvl + (hr(x // 3, y // 5, seed) - 0.5) * 0.35
            if socle and y >= socle:
                v -= 0.9 + (0.3 if hr(x // 6, y // 3, seed) > 0.8 else 0)
            cv.put(x, y, ramp, v)
    if frames:
        for fx in range(frame0, x1 + 1, frames):
            for x in range(max(x0, fx), min(x1, fx + 7) + 1):
                d = x - fx
                for y in range(max(y0, 27), y1):
                    cv.put(x, y, ramp, lvl + 0.4 + (0.9 if d == 0 else 0.5 if d == 1 else -0.3 if d >= 6 else 0.1)
                           - (0.8 if socle and y >= socle else 0))
            for y in range(max(y0, 37), y1 - 24, 16):
                if x0 <= fx + 3 <= x1:
                    bolt(cv, fx + 3, y, ramp, lvl + 0.5)
                if x0 <= fx + 5 <= x1:
                    bolt(cv, fx + 5, y + 8, ramp, lvl + 0.3)
    for sy in seams:
        for x in range(x0, x1 + 1):
            cv.put(x, sy, ramp, lvl - 1.3)
            cv.put(x, sy + 1, ramp, lvl + 0.8 if (x // 2) % 2 else lvl + 0.3)       # el cordó de soldadura
    if socle:
        cv.hline(x0, x1, socle, ramp, lvl + 0.9)
        cv.hline(x0, x1, socle + 1, ramp, lvl - 0.6)
    cv.hline(x0, x1, y1 - 1, ramp, lvl - 2.1)
    for i in range(rust):
        x = x0 + int(hr(i, 7, seed) * (x1 - x0))
        ys = [s for s in seams] or [y0 + 40]
        sy = ys[int(hr(i, 8, seed) * len(ys))] + 2
        n = 7 + int(hr(i, 9, seed) * 21)
        for y in range(sy, min(y1 - 2, sy + n)):
            k = 0.5 * (1 - (y - sy) / n)
            for xx in (x, x + 1) if hr(i, 10, seed) > 0.6 else (x,):
                if k > B4[y & 3][xx & 3] * 0.6:
                    cv.flat(xx, y, mix(cv.get(xx, y), RUST[3], k))


def ceiling(cv, x0=0, x1=W - 1, h=25, beams=85, beam0=-11, trays=(8, 17)):
    """El sostre: baos i dues safates de cables, amb els cables de colors."""
    cv.rect(x0, 0, x1, h, DARK, 2.0)
    for bx in range(beam0, x1 + 1, beams):
        if bx + 11 >= x0:
            box(cv, max(x0, bx - 3), 0, min(x1, bx + 11), h + 3, ENG, 1.6, grad=0.6)
            for y in (4, 14, 23):
                cv.put(bx + 4, y, ENG, 3.2)
    for y in trays:
        cv.hline(x0, x1, y, CAB, 2.8)
        cv.hline(x0, x1, y + 5, CAB, 1.6)
        for x in range(x0, x1 + 1, 6):
            cv.vline(x, y, y + 5, CAB, 2.2)
        for x in range(x0, x1 + 1):
            for k in (2, 3):
                if hr(x // 12, y, k) > 0.35:
                    cv.flat(x, y + k, [(20, 20, 24), (40, 36, 30), (70, 50, 34), (110, 40, 34)][int(hr(x // 14, y, k) * 4)])


def cage_lamp(cv, lx, ly=29, top=21, on=True):
    """Llum de gàbia al sostre: base cargolada, globus i la reixa de quatre barres."""
    box(cv, lx - 8, top, lx + 8, top + 5, CAB, 3.0)
    for bx in (lx - 6, lx + 6):
        cv.put(bx, top + 2, CAB, 4.6)
    cv.disc(lx, ly + 4, 8, 5, LAMPC if on else CAB, (lambda nx, ny: 2.8 - ny * 0.4) if on else 2.0, lit=0)
    for gx in (-6, -2, 2, 6):
        cv.vline(lx + gx, ly, ly + 9, CAB, 2.2, lit=0)
    cv.hline(lx - 8, lx + 8, ly + 5, CAB, 2.0, lit=0)
    cv.hline(lx - 5, lx + 5, ly + 9, CAB, 2.4, lit=0)


def lamp_glow(cv, lx, ly=29):
    glow(cv, lx, ly + 5, 45, WARM, 0.55)
    glow(cv, lx, ly + 5, 16, (255, 240, 200), 0.6)


def checker_floor(cv, x0=0, x1=W - 1, y0=FLOOR_Y, y1=BOTTOM + 15, vp=(320, 53), ramp=DECK, lvl=2.5, plate=101,
                  seams=(211, 227, 249)):
    """Terra de planxa estriada en perspectiva. → màscara del terra."""
    mask = [[False] * W for _ in range(H)]
    for y in range(y0, min(H, y1 + 1)):
        d = y - vp[1]
        for x in range(x0, x1 + 1):
            u = vp[0] + (x - vp[0]) * 200 / d
            u2 = vp[0] + (x + 1 - vp[0]) * 200 / d
            v = 4267 / d
            lv = lvl
            if int(u // plate) != int(u2 // plate):
                lv = lvl - 1.5
            elif y in seams:
                lv = lvl - 1.4
            elif y - 1 in seams:
                lv = lvl + 0.8
            else:
                a, b = int(u * 0.5) % 4, int(v * 1.0) % 4
                if (a == 0 and b in (0, 1)) or (a == 2 and b in (2, 3)):
                    lv += 0.9
                elif (a == 1 and b == 1) or (a == 3 and b == 3):
                    lv += 0.35                                               # el bisell de l'estria
            cv.put(x, y, ramp, lv)
            mask[y][x] = True
    return mask


def door_frame(cv, x0, y0, x1, y1, ramp=WALL, lvl=4.2, r=12):
    """El marc d'una porta estanca (cantons rodons a dalt), de 4 px de gruix."""
    for t in range(4):
        for y in range(y0 - t, y1 + 1):
            for x in range(x0 - t, x1 + t + 1):
                dx = max(x0 - t + r - x, 0, x - (x1 + t - r))
                dy = max(y0 - t + r - y, 0)
                inside = dx * dx + dy * dy <= r * r
                inner = x0 - t + 1 <= x <= x1 + t - 1 and y >= y0 - t + 1
                ddx = max(x0 - t + 1 + r - x, 0, x - (x1 + t - 1 - r))
                ddy = max(y0 - t + 1 + r - y, 0)
                if inside and not (inner and ddx * ddx + ddy * ddy <= r * r):
                    cv.put(x, y, ramp, lvl - t * 0.7)


def sill(cv, x0, x1, y1, ramp=WALL, lvl=2.6):
    """El llindar alt de les portes de vaixell."""
    cv.rect(x0 + 1, y1 - 8, x1 - 1, y1 - 1, ramp, lvl)
    cv.hline(x0 + 1, x1 - 1, y1 - 8, ramp, lvl + 1.4)
    cv.hline(x0 + 1, x1 - 1, y1 - 7, ramp, lvl + 0.6)


def sign(cv, x0, y0, s, ramp=WHITEP, lvl=4.0, ink=None, pad=3):
    """Un rètol petit (planxa amb lletres de 5 px i dos cargols)."""
    w = text_width(s)
    x1, y1 = x0 + w + pad * 2 + 1, y0 + 5 + pad * 2
    box(cv, x0, y0, x1, y1, ramp, lvl)
    text(cv, s, x0 + pad + 1, y0 + pad + 1, None, 0, flat=ink or (20, 24, 28))
    for bx in (x0 + 1, x1 - 1):
        cv.put(bx, y0 + 1 + (y1 - y0) // 2, ramp, lvl - 1.6)
    return w + pad * 2 + 2


def rust_streaks(cv, x0, y0, x1, y1, n, k=0.5, seed=0, ramp=RUST):
    for i in range(n):
        x = x0 + int(hr(i, 1, seed) * (x1 - x0))
        sy = y0 + int(hr(i, 2, seed) * (y1 - y0) * 0.6)
        ln = 5 + int(hr(i, 3, seed) * 19)
        for y in range(sy, min(y1, sy + ln)):
            kk = k * (1 - (y - sy) / ln)
            if kk > B4[y & 3][x & 3] * 0.6:
                cv.flat(x, y, mix(cv.get(x, y), ramp[3], kk))


def floor_shadow(cv, cx, cy, rx, ry, k=0.6):
    """Ombra suau sota d'un objecte a terra."""
    cv.darken(cx - rx, cy - ry, cx + rx, cy + ry,
              lambda x, y: k * max(0.0, 1 - ((x - cx) / rx) ** 2 - ((y - cy) / ry) ** 2) * 1.6)


def vladder(cv, x0, x1, y0, y1, ramp=CAB, lvl=3.2, step=12, rail=2):
    """Escala de mà vertical: dos muntants i graons rodons amb el cordó de soldadura."""
    for y in range(y0, y1 + 1, step):
        hpipe(cv, x0 + rail, x1 - rail, y, 1, ramp, lvl)
        for xx in (x0 + rail + 1, x1 - rail - 1):
            cv.put(xx, y + 2, ramp, lvl - 1.2)
    vpipe(cv, x0 + 1, y0 - 3, y1, 2, ramp, lvl + 0.3)
    vpipe(cv, x1 - 1, y0 - 3, y1, 2, ramp, lvl - 0.2)


# ═══ El pallol ═══════════════════════════════════════════════════════════════

LAMPS = (227, 496)

LIGHT = Light(ambient=-0.5, vignette=(61, 37), floor_fade=None)
LIGHT.point(227, 35, r=213, k=2.6, squash=1.05, down=True, power=1.5)
LIGHT.point(496, 35, r=200, k=2.3, squash=1.05, down=True, power=1.5)

DOOR = (13, 88, 69, FLOOR_Y)
SHELF = (104, 45, 349, FLOOR_Y + 3)
ROPE = [(36, 28, 14), (78, 62, 32), (128, 104, 58), (176, 150, 92), (214, 192, 130), (238, 224, 170)]
ROPEW = [(40, 40, 40), (90, 90, 86), (140, 140, 132), (186, 186, 176), (220, 220, 210), (240, 240, 232)]
BLUE = [(8, 16, 36), (14, 30, 64), (22, 48, 98), (36, 70, 130), (60, 100, 166), (110, 150, 200)]
BLACKC = [(4, 4, 6), (10, 10, 14), (20, 20, 26), (34, 34, 42), (54, 54, 64), (80, 80, 92)]
CARD = [(40, 30, 14), (80, 60, 30), (130, 100, 54), (170, 136, 80), (200, 170, 112)]
BOXC = [(16, 20, 26), (30, 36, 46), (48, 56, 70), (70, 80, 96), (100, 110, 126)]
TAPE = [(40, 40, 44), (90, 90, 96), (140, 140, 146), (180, 180, 186), (214, 214, 218)]
YELLT = [(80, 60, 10), (160, 120, 20), (220, 180, 50), (250, 220, 120), (255, 240, 180)]


# ─── Paret, porta i inventari ──────────────────────────────────────────────

def walls(cv):
    plate_wall(cv, 0, W - 1, frames=85, frame0=80, seams=(77, 149), rust=36, seed=21)
    ceiling(cv, beam0=80)
    hpipe(cv, 0, W - 1, 40, 3, SEAG, 3.0, bands=range(40, W, 80), band_ramp=WHITEP)
    for x in range(53, W, 80):                                          # les abraçadores del tub
        cv.vline(x, 35, 45, CAB, 2.0)
        cv.vline(x + 1, 35, 45, CAB, 3.4)
        cv.vline(x + 2, 35, 45, CAB, 2.6)
        cv.put(x + 1, 34, CAB, 4.4)
    for x in range(0, W, 7):                                            # el sentit del flux, pintat
        if (x // 7) % 12 == 5:
            cv.line(x, 38, x + 4, 40, WHITEP, 3.4)
            cv.line(x, 42, x + 4, 40, WHITEP, 3.4)


def door(cv):
    """La porta del passadís, tancada (la veiem de dins)."""
    x0, y0, x1, y1 = DOOR
    door_frame(cv, x0, y0, x1, y1, ramp=WALL, lvl=4.2, r=8)
    rrect(cv, x0, y0, x1, y1 - 9, 7, CAB, lambda x, y: 3.4 - (y - y0) * 0.005)
    rrect(cv, x0 + 5, y0 + 5, x1 - 5, y1 - 14, 4, CAB, lambda x, y: 3.7 - (y - y0) * 0.005)
    for y in range(y0 + 11, y1 - 13, 8):                                # nervis
        cv.hline(x0 + 6, x1 - 6, y, CAB, 4.2)
        cv.hline(x0 + 6, x1 - 6, y + 1, CAB, 2.4)
    sill(cv, x0, x1, y1)
    for hy in (y0 + 16, y1 - 29):                                       # frontisses
        box(cv, x1 - 3, hy, x1 + 3, hy + 11, CAB, 3.6)
        cv.put(x1, hy + 3, CAB, 1.6)
        cv.put(x1, hy + 8, CAB, 1.6)
    box(cv, x0 + 4, 136, x0 + 9, 149, BRASS, 3.6)                       # maneta
    cv.hline(x0 + 7, x0 + 17, 139, BRASS, 4.6)
    cv.hline(x0 + 7, x0 + 17, 140, BRASS, 2.8)
    cv.put(x0 + 6, 145, DARK, 0.6)                                      # el pany
    cv.put(x0 + 6, 146, DARK, 0.6)
    for i in range(6):                                                  # la pintura gastada al voltant de la maneta
        cv.put(x0 + 10 + int(hr(i, 81) * 10), 133 + int(hr(i, 82) * 18), CAB, 4.6)


def inventory(cv):
    """L'inventari, clavat damunt la porta: capçalera PALLOL, una llista i una columna de xifres."""
    x0, y0, x1, y1 = 21, 46, 61, 80
    box(cv, x0, y0, x1, y1, PAPER, 4.2)
    cv.rect(x0 + 1, y0 + 1, x1 - 1, y0 + 8, PAPER, 3.0)
    text(cv, 'PALLOL', x0 + (x1 - x0 + 1 - text_width('PALLOL')) // 2, y0 + 3, None, 0, flat=(40, 34, 30))
    for i, y in enumerate(range(y0 + 11, y1 - 2, 3)):
        n = 12 + int(hr(i, 4) * 13)
        for x in range(x0 + 3, x0 + 3 + n):
            if hr(x, y, 5) > 0.15:
                cv.put(x, y, DARK, 2.0)
        cv.hline(x1 - 7, x1 - 4, y, DARK, 2.0)
        if i < 6:
            cv.put(x1 - 9, y, DARK, 2.6 if i % 2 else 1.4)                 # les marques de comprovat
    cv.hline(x1 - 8, x1 - 3, y0 + 17, REDP, 4.0)                        # la línia dels cadenats, repassada
    cv.hline(x1 - 8, x1 - 3, y0 + 18, REDP, 3.0)
    cv.put(x0 + 2, y0 + 2, CAB, 4.6)                                    # els claus, als cantons de dalt
    cv.put(x0 + 3, y0 + 3, CAB, 2.0)
    cv.put(x1 - 2, y0 + 2, CAB, 4.6)
    cv.put(x1 - 1, y0 + 3, CAB, 2.0)
    cv.poly([(x1 - 4, y1), (x1, y1 - 4), (x1, y1)], PAPER, 2.4)          # el cantó doblegat
    # un bolígraf lligat amb un cordill
    cv.line(x1 + 1, y0 + 3, x1 + 4, y0 + 24, WHITEP, 3.0)
    cv.line(x1 + 4, y0 + 24, x1 + 5, y0 + 35, BLUE, 3.6)
    cv.line(x1 + 5, y0 + 24, x1 + 6, y0 + 35, BLUE, 2.2)
    cv.put(x1 + 6, y0 + 36, CAB, 4.2)


# ─── Els prestatges ─────────────────────────────────────────────────────────

def coil(cv, cx, cy, rx, ry, ramp, lvl=3.0, turns=3):
    """Un rotllo de cap, vist de cara (anelles concèntriques) i trenat."""
    for y in range(int(cy - ry), int(cy + ry) + 1):
        for x in range(int(cx - rx), int(cx + rx) + 1):
            nx, ny = (x - cx) / rx, (y - cy) / ry
            d = math.hypot(nx, ny)
            if 0.28 <= d <= 1:
                ring = (d * turns * 2) % 2
                tw = ((x + y * 2) // 2) % 3 == 0
                cv.put(x, y, ramp, lvl + 1.2 * (1 - abs(ring - 1)) - nx * 0.6 - ny * 0.8 - (0.6 if tw else 0))
            elif d < 0.28:
                cv.put(x, y, DARK, 1.0 + (0.6 if ny < -0.1 else 0))
    # el cap que en penja, amb el nus de la punta
    ex, ey = cx + rx * 0.55, cy + ry * 0.8
    for k in range(5):
        cv.put(round(ex + k * 0.4), round(ey + k), ramp, lvl + 0.6 - k * 0.2)


def reel(cv, cx, cy, r, ramp=BLACKC):
    """Una bobina de cable vista de cara: el cable enrotllat, les galtes de fusta i el forat de l'eix."""
    cv.disc(cx, cy, r, r, WALNUT, lambda nx, ny: 3.4 - nx - ny)
    cv.disc(cx, cy, r - 3, r - 3, ramp, lambda nx, ny: 2.8 - nx * 0.8 - ny * 0.8)
    for rr in range(5, r - 3, 3):                                        # les voltes del cable
        for a in range(0, 360, 12):
            cv.put(cx + round(math.cos(math.radians(a)) * rr), cy + round(math.sin(math.radians(a)) * rr), ramp,
                   3.6 - math.sin(math.radians(a)) * 0.8)
    for a in range(0, 360, 45):                                          # els cargols de la galta
        cv.put(cx + round(math.cos(math.radians(a)) * (r - 1.5)), cy + round(math.sin(math.radians(a)) * (r - 1.5)),
               WALNUT, 1.6)
    cv.disc(cx, cy, 4, 4, WALNUT, 3.0)
    cv.disc(cx, cy, 1.5, 1.5, DARK, 0.5)
    # la punta del cable, que en surt
    cv.line(cx + r - 4, cy + 2, cx + r + 2, cy + r - 2, ramp, 3.2)


def can(cv, x0, y0, w, h, ramp, label=WHITEP, drip=None):
    """Un pot de pintura: tapa amb vora, nansa, etiqueta i regalims."""
    for y in range(y0, y0 + h + 1):
        for x in range(x0, x0 + w + 1):
            u = (x - x0 - w / 2) / (w / 2 + 0.5)
            cv.put(x, y, CAB if y < y0 + 3 else ramp, 3.4 + 1.4 * (-0.3 - u) - 0.8 * u * u)
    cv.hline(x0, x0 + w, y0, CAB, 4.8)
    cv.hline(x0, x0 + w, y0 + 2, CAB, 2.0)
    cv.line(x0 + 1, y0 + 1, x0 + w // 2, y0 - 3, CAB, 3.0)               # la nansa
    cv.line(x0 + w // 2, y0 - 3, x0 + w - 1, y0 + 1, CAB, 3.0)
    ly = y0 + h // 2 - 2
    cv.rect(x0 + 1, ly, x0 + w - 1, ly + 5, label, 3.6)
    cv.hline(x0 + 3, x0 + w - 3, ly + 2, DARK, 2.4 if label is not CAB else 1.0)
    if drip:
        for i, dx in enumerate((1, 4, w - 3)):
            cv.vline(x0 + dx, y0 + 3, y0 + 4 + i * 3, drip, 3.6)
            cv.put(x0 + dx, y0 + 5 + i * 3, drip, 2.6)


def shelves(cv):
    x0, y0, x1, y1 = SHELF
    levels = (75, 115, 157, 197)
    cv.darken(x0 + 4, y0, x1 - 4, y1, 0.25)                              # el fons de dins, més fosc
    for lx in (x0, (x0 + x1) // 2, x1 - 5):                              # muntants perforats
        box(cv, lx, y0, lx + 5, y1, CAB, 3.4)
        for y in range(y0 + 5, y1, 8):
            cv.put(lx + 2, y, DARK, 1.0)
            cv.put(lx + 3, y, DARK, 1.0)
            cv.put(lx + 2, y + 1, DARK, 1.0)
    for ly in levels:
        box(cv, x0, ly, x1, ly + 4, CAB, 3.8)
        cv.hline(x0, x1, ly + 5, DARK, 1.0)
        for bx in (x0 + 2, (x0 + x1) // 2 + 2, x1 - 3):                  # els cargols de la lleixa
            cv.put(bx, ly + 2, CAB, 5.2)
    box(cv, x0 - 3, y0 - 3, x1 + 3, y0 + 1, CAB, 3.4)
    # ─ lleixa de dalt: pintura (blanca, vermella de la borda, verda de sala de màquines) i brotxes
    can(cv, 115, 54, 16, 20, WHITEP, drip=WHITEP)
    can(cv, 135, 57, 16, 17, REDP, drip=REDP)
    can(cv, 155, 54, 16, 20, WHITEP)
    can(cv, 175, 60, 13, 14, SEAG, drip=SEAG)
    can(cv, 195, 62, 16, 12, CAB, label=CAB)
    for i in range(3):                                                  # brotxes dins el pot
        bx = 199 + i * 4
        cv.line(bx, 49, bx + 2, 62, WALNUT, 3.6)
        cv.rect(bx - 1, 49, bx + 1, 52, [(60, 50, 40), (140, 120, 90), (200, 180, 140)], 1.6)
    for sx, n, ramp in ((236, 3, TAPE), (252, 2, TAPE), (266, 1, YELLT)):   # rotllos de cinta, apilats
        for k in range(n):
            ty = 69 - k * 6
            for x in range(sx - 6, sx + 7):                              # el cantó del rotllo (cilindre)
                u = (x - sx) / 6.5
                for y in range(ty, ty + 4):
                    cv.put(x, y, ramp, 3.0 + 1.2 * (-0.3 - u) - 0.7 * u * u - (0.5 if y == ty + 3 else 0))
            cv.disc(sx, ty, 6, 2, ramp, lambda nx, ny: 3.8 - nx * 0.6)    # la cara de dalt
            cv.disc(sx, ty, 2.5, 1, DARK, 1.2)                           # el forat
    box(cv, 285, 53, 339, 73, CARD, 2.8)                                # la caixa de cartró
    cv.hline(285, 339, 62, [(60, 40, 20), (150, 120, 60), (200, 170, 110)], 2.2)
    cv.poly([(285, 53), (291, 48), (300, 48), (296, 53)], CARD, 3.6)     # una solapa aixecada
    sign(cv, 297, 57, 'DRAPS', ramp=PAPER, lvl=4.0, pad=2)
    cv.line(330, 53, 334, 47, WHITEP, 4.4)                               # un drap que en treu el cap
    cv.line(331, 53, 336, 49, WHITEP, 3.4)
    # ─ segona lleixa: caps enrotllats (blancs, grocs i blau)
    coil(cv, 131, 99, 17, 15, ROPEW)
    coil(cv, 167, 99, 17, 15, ROPE)
    coil(cv, 200, 101, 13, 12, BLUE)
    coil(cv, 240, 98, 19, 16, ROPEW, lvl=2.6)
    coil(cv, 280, 99, 17, 15, ORANGE)
    coil(cv, 317, 100, 16, 13, ROPE, lvl=2.6)
    # ─ tercera lleixa: bobines de cable apantallat i capses de connectors
    reel(cv, 133, 139, 17)
    reel(cv, 171, 141, 15, ramp=[(40, 18, 10), (90, 40, 20), (150, 70, 30), (200, 110, 60), (230, 160, 110),
                                (250, 200, 160)])
    reel(cv, 203, 144, 12)
    for i, lab in enumerate(('BNC', 'PL', 'N', 'SMA')):                  # capses de connectors, amb etiqueta
        bx = 229 + i * 29
        box(cv, bx, 131, bx + 25, 156, BOXC, 2.6)
        cv.hline(bx + 1, bx + 24, 133, BOXC, 3.6)
        cv.rect(bx + 3, 137, bx + 22, 145, PAPER, 3.8)
        text(cv, lab, bx + 3 + (20 - text_width(lab)) // 2, 139, None, 0, flat=(30, 30, 36))
        cv.hline(bx + 9, bx + 16, 131, BRASS, 3.6)                       # nansa
        cv.hline(bx + 9, bx + 16, 130, BRASS, 4.8)
        cv.put(bx + 2, 151, BOXC, 4.0)
        cv.put(bx + 23, 151, BOXC, 4.0)
    # ─ lleixa de baix: una caixa d'eines, galledes, un rotllo de cap gruixut
    box(cv, 115, 176, 168, 196, REDP, 3.2)
    cv.hline(115, 168, 181, REDP, 4.4)
    cv.hline(115, 168, 182, REDP, 2.2)
    box(cv, 133, 170, 149, 175, CAB, 3.6)                                # nansa
    for bx in (119, 162):                                                # tancaments
        box(cv, bx, 180, bx + 3, 185, CAB, 4.0)
    for gx in (184, 211):
        cv.poly([(gx, 171), (gx + 21, 171), (gx + 19, 196), (gx + 3, 196)], YELL, lambda x, y: 3.4 - (x - gx) * 0.05)
        cv.hline(gx, gx + 21, 171, YELL, 4.6)
        cv.hline(gx + 1, gx + 20, 172, YELL, 2.2)
        cv.hline(gx + 2, gx + 19, 184, YELL, 2.6)                        # la costella
        cv.line(gx + 1, 171, gx + 11, 163, CAB, 3.0)
        cv.line(gx + 11, 163, gx + 20, 171, CAB, 3.0)
    coil(cv, 280, 181, 37, 15, ROPE, lvl=2.8, turns=4)
    cv.darken(x0 + 4, y1 - 5, x1 - 4, y1, 0.4)


def padlocks(cv):
    """El tauler dels cadenats: sis ganxos i cinc cadenats. N'hi falta un."""
    x0, y0, x1, y1 = 360, 93, 416, 139
    box(cv, x0, y0, x1, y1, WALNUT, 3.0)
    for x in range(x0 + 4, x1 - 2, 5):                                   # tauler perforat
        for y in range(y0 + 4, y1 - 2, 5):
            cv.put(x, y, WALNUT, 1.4)
    for bx, by in ((x0 + 2, y0 + 2), (x1 - 2, y0 + 2), (x0 + 2, y1 - 2), (x1 - 2, y1 - 2)):
        cv.put(bx, by, CAB, 4.4)
    sign(cv, x0 + 6, y0 - 12, 'CADENATS', ramp=PAPER, lvl=3.8, pad=2)
    for i in range(6):
        hx, hy = hook(i)
        cv.vline(hx, hy, hy + 4, CAB, 4.4)
        cv.put(hx + 1, hy + 4, CAB, 3.6)
        cv.put(hx, hy - 1, CAB, 2.4)
        if i == 4:
            cv.darken(hx - 4, hy + 8, hx + 6, hy + 18, 0.35)              # la marca del que hi falta
            continue
        padlock(cv, hx, hy)


def hook(i):
    """On és el ganxo i del tauler (de 0 a 5)."""
    return 360 + 9 + (i % 3) * 19, 93 + 7 + (i // 3) * 21


def padlock(cv, hx, hy):
    """Un cadenat penjat d'un ganxo del tauler: arc d'acer, cos de llautó i el forat de la clau."""
    for a in range(180, 361, 12):
        for r in (3.4, 2.6):
            cv.put(hx + 1 + round(math.cos(math.radians(a)) * r), hy + 9 + round(math.sin(math.radians(a)) * r * 1.2),
                   WHITEP, 4.4 if r > 3 else 3.0)
    cv.vline(hx - 2, hy + 9, hy + 10, WHITEP, 4.0)
    cv.vline(hx + 4, hy + 9, hy + 10, WHITEP, 3.0)
    rrect(cv, hx - 4, hy + 10, hx + 6, hy + 18, 2, BRASS, lambda x, y: 4.0 - (x - hx + 4) * 0.12 - (y - hy - 10) * 0.05)
    cv.hline(hx - 3, hx + 5, hy + 10, BRASS, 5.0)
    cv.put(hx + 1, hy + 13, DARK, 1.0)
    cv.put(hx + 1, hy + 14, DARK, 1.0)
    cv.put(hx + 1, hy + 15, DARK, 1.6)


def cadenat_sise(cv):
    """El sisè cadenat, al seu ganxo (abans de l'Escena 4 no en falta cap)."""
    padlock(cv, *hook(4))


# ─── Defenses, salvavides, galledes, rotllo d'amarrar ──────────────────────

FENDERS = ((445, ORANGE), (477, WHITEP))
BUOY = (547, 112)
_SWING = {'a': 0.0}                       # angle (graus) del gronxament: el canvien els fotogrames de `defenses`


def _rot(x, y, px, py, deg):
    """Punt (x, y) girat `-deg` al voltant de (px, py): on cau dins l'objecte quiet."""
    c, s_ = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    dx, dy = x - px, y - py
    return px + dx * c + dy * s_, py - dx * s_ + dy * c


def _fender_px(cv, fx, col, deg):
    """Una defensa penjada del cap a (fx, 64), girada `deg` graus: cap trenat, ull, cos amb costelles i taca de port."""
    pad = 16
    for y in range(61, 160):
        for x in range(fx - pad - 10, fx + pad + 10):
            lx, ly = _rot(x, y, fx, 64, -deg)
            if ly < 64 or ly > 155.5:
                continue
            if 80 <= ly < 149:
                t = (ly - 80) / 69
                rx = 12 * math.sin(math.pi * min(1, max(0, t * 1.08 + 0.02))) ** 0.5
                if abs(lx - fx) <= rx + 0.5:
                    u = (lx - fx) / (rx + 0.5)
                    lv = 3.4 + 1.4 * (-0.3 - u) - 0.8 * u * u
                    if int(ly - 80) % 17 == 0 and 0.08 < t < 0.92:
                        lv -= 0.7                                       # costelles
                    if t > 0.7 and hr(int(lx), int(ly), 3) > 0.8:
                        lv -= 0.9                                       # el brut del moll
                    cv.put(x, y, col, lv)
            elif 149 <= ly <= 155.5 and abs(lx - fx) <= 2:
                cv.put(x, y, col, 2.2)                                  # el tap de baix
            elif 76 <= ly < 80 and abs(lx - fx) <= 3:
                cv.put(x, y, col, 2.6)                                  # l'ull de dalt
            elif abs(lx - fx) < 0.9:
                cv.put(x, y, ROPEW, (3.6 if int(ly) % 3 else 2.4) if ly < 76 else 3.0)


def _buoy_px(cv, deg):
    """El salvavides, penjat d'un cap del mateix bastidor, girat `deg` graus al voltant del nus de dalt."""
    cx0, cy0 = BUOY
    py = 64
    for y in range(py, cy0 + 29):
        for x in range(cx0 - 32, cx0 + 33):
            lx, ly = _rot(x, y, cx0, py, -deg)
            d = math.hypot(lx - cx0, ly - cy0)
            if 13.3 <= d <= 24.7:
                a = math.degrees(math.atan2(ly - cy0, lx - cx0)) % 90
                band = 35 <= a <= 55
                u = (d - 19) / 6
                cv.put(x, y, WHITEP if band else ORANGE, 3.6 - u * 1.2 - (ly - cy0) * 0.02 - u * u)
            elif 24.7 < d <= 26.2:
                a = math.degrees(math.atan2(ly - cy0, lx - cx0)) % 360
                if (int(a) // 45) % 2 == 0 and int(a) % 6 < 3:
                    cv.put(x, y, ROPEW, 3.6)
            elif 12.2 <= d < 13.3:
                cv.put(x, y, ORANGE, 1.4)                               # la vora de dins, a l'ombra
            elif abs(lx - cx0) < 0.9 and py <= ly < cy0 - 25:
                cv.put(x, y, ROPEW, 3.6 if int(ly) % 3 else 2.4)


def fenders(cv):
    """Dues defenses penjades d'un cap, i el salvavides (es gronxen amb el balanceig: vegeu _SWING)."""
    cv.hline(424, 627, 61, CAB, 3.6)
    cv.hline(424, 627, 62, CAB, 2.0)
    for bx in (424, 627):
        box(cv, bx - 2, 57, bx + 2, 66, CAB, 3.2)                       # els suports del bastidor
    a = _SWING['a']
    for i, (fx, col) in enumerate(FENDERS):
        _fender_px(cv, fx, col, a * (1.0 if i == 0 else 0.85))       # la blanca, més lleugera, va una mica enrere
    _buoy_px(cv, a * 0.5)                                               # el salvavides frega la paret: es mou menys
    sign(cv, 525, 144, 'ARENGA', ramp=WHITEP, lvl=3.8, pad=2)


def buckets(cv):
    """El pal de fregar i un bidó de plàstic, contra la paret de la dreta."""
    cv.line(603, 93, 595, FLOOR_Y + 3, WALNUT, 3.6)
    cv.line(604, 93, 596, FLOOR_Y + 3, WALNUT, 2.4)
    for i in range(10):                                                  # el fregall
        cv.line(595, FLOOR_Y - 10, 587 + i * 2, FLOOR_Y + 3, ROPEW, 2.6 + (i % 2) * 0.6)
    # bidó blau, amb la nansa i l'etiqueta
    rrect(cv, 608, 155, 635, FLOOR_Y + 3, 4, BLUE, lambda x, y: 3.4 - (x - 608) * 0.05)
    box(cv, 616, 149, 625, 155, BLUE, 3.0)
    cv.hline(610, 633, 160, BLUE, 4.2)
    cv.rect(611, 170, 632, 182, WHITEP, 3.4)
    for y, w in ((173, 16), (176, 12), (179, 14)):                      # l'etiqueta, gastada
        cv.hline(614, 614 + w, y, BLUE, 2.4)
    for y in (190, 196):
        cv.hline(610, 633, y, BLUE, 2.2)


def mooring_coil(cv):
    """Un rotllo de cap d'amarrar, gruixut, a terra (en perspectiva), amb la gassa per sobre."""
    floor_shadow(cv, 387, 219, 45, 7, 0.6)
    for k in range(5):
        cy = 216 - k * 4
        rx, ry = 43 - k * 3, 11 - k * 0.8
        for a in range(0, 360, 1):
            x = 387 + math.cos(math.radians(a)) * rx
            y = cy + math.sin(math.radians(a)) * ry
            front = math.sin(math.radians(a)) > -0.2
            for t in range(4):
                cv.put(x, y - t, ROPE, (3.4 if front else 2.0) + (0.9 if t == 3 else 0.3 if t == 2 else 0)
                       - (0.5 if (a // 6 + t) % 3 == 0 else 0))
    cv.disc(387, 200, 24, 4.7, DARK, 1.0)
    for i in range(14):                                                  # la gassa (l'ull), damunt del rotllo
        a = math.radians(200 + i * 10)
        cv.put(round(372 + math.cos(a) * 9), round(197 + math.sin(a) * 4), ROPE, 4.2)


def crate(cv):
    """Una caixa de fusta de peix, del revés, contra la paret: el seient del Marcel a l'Escena 6."""
    x0, x1, yt, yb = 519, 553, 200, 248
    floor_shadow(cv, (x0 + x1) // 2, yb + 1, 27, 5, 0.7)
    cv.poly([(x0 + 3, yt), (x1 + 3, yt), (x1, yt + 7), (x0, yt + 7)], WALNUT, lambda x, y: 5.4 - (y - yt) * 0.1)
    for x in range(x0 + 10, x1, 10):                                     # junts de les posts
        cv.line(x + 3, yt, x, yt + 7, WALNUT, 2.4)
    for i, py in enumerate(range(yt + 8, yb + 1, 10)):                   # la cara del davant: posts horitzontals
        box(cv, x0, py, x1, min(py + 8, yb), WALNUT, 4.4 - i * 0.2, grad=0.7)
        if py + 9 <= yb:
            cv.hline(x0 + 1, x1 - 1, py + 9, DARK, 1.0)
        for nx in (x0 + 5, x1 - 5):                                      # els claus
            cv.put(nx, py + 2, CAB, 4.0)
    for x in (x0, x1 - 3):                                               # els travessers dels cantons
        box(cv, x, yt + 7, x + 3, yb, WALNUT, 3.6)
    cv.hline(x0 + 8, x0 + 27, yt + 21, FUEL, 3.2)                       # una marca de pintura, mig esborrada
    cv.hline(x0 + 8, x0 + 22, yt + 22, FUEL, 2.6)
    for x in range(x0 + 8, x0 + 28, 3):
        cv.put(x, yt + 21, WALNUT, 3.4)


# ─── Muntatge ───────────────────────────────────────────────────────────────

def bg(cv):
    walls(cv)
    door(cv)
    inventory(cv)
    shelves(cv)
    padlocks(cv)
    fenders(cv)
    buckets(cv)
    checker_floor(cv)
    mooring_coil(cv)
    crate(cv)
    floor_shadow(cv, 227, FLOOR_Y + 4, 128, 4, 0.6)
    for lx in LAMPS:
        cage_lamp(cv, lx)
    for lx in LAMPS:
        lamp_glow(cv, lx)


PROPS = {'cadenat_sise': cadenat_sise}


# ─── Animacions ────────────────────────────────────────────────────────────

def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv


def _frames_defenses():
    """El balanceig: les defenses i el salvavides fan un vaivé lent (sinus: el bucle no salta)."""
    base = _base()
    frames = []
    n = 32
    for i in range(n):
        _SWING['a'] = 3.5 * math.sin(2 * math.pi * i / n)
        try:
            cv = _base()
        finally:
            _SWING['a'] = 0.0
        frames.append(_diff(cv.img, base.img))
    return frames


def _frames_pols():
    """Pols que sura a la llum del llum de l'esquerra (cada mota fa un llaç tancat: el bucle no salta)."""
    base = _base()
    lx = LAMPS[0]
    motes = [(lx + (hr(k, 7) - 0.5) * 107, 53 + hr(k, 8) * 120, 8 + hr(k, 9) * 13, 5 + hr(k, 10) * 11, hr(k, 11),
              1 + int(hr(k, 12) * 2)) for k in range(24)]
    n = 48
    frames = []
    for i in range(n):
        cv = Canvas(light=LIGHT, img=base.img.copy())
        t = i / n
        for (cx, cy, ax, ay, ph, fx) in motes:
            a = 2 * math.pi * (t + ph)
            x = round(cx + ax * math.sin(fx * a))
            y = round(cy + ay * math.sin(a + ph * 3))
            near = max(0.0, 1 - math.hypot(x - lx, (y - 35) * 0.9) / 173)
            alpha = near * (0.5 + 0.25 * (1 + math.sin(a * 2 + ph * 7)))
            if alpha > 0.08 and 0 <= x < W and 40 <= y < FLOOR_Y:
                cv.flat(x, y, mix(cv.get(x, y), (255, 236, 196), alpha))
        frames.append(_diff(cv.img, base.img))
    return frames


ANIMS = {'defenses': {'frames': _frames_defenses, 'frameDuration': 200},
         'pols': {'frames': _frames_pols, 'frameDuration': 130}}

GEOMETRIA = {
    'things': {
        'porta': {'rect': (8, 83, 75, 203), 'walk': (45, 224)},
        'prestatges': {'rect': (101, 43, 352, 205), 'walk': (227, 227)},
        'inventari': {'rect': (19, 45, 67, 83), 'walk': (53, 224)},
    },
    'spawns': {'iri': (267, 253), 'vet': (200, 259), 'marcel': (533, 248), 'diu': (505, 253)},
    'walkable': [(8, 219), (333, 219), (336, 235), (440, 235), (443, 219), (632, 219), (637, 263), (3, 263)],
}
