"""
Aigua Verne — `palau_salo` (L): el saló de la Gran Subhasta de l'Aigua, al palau orbital.

  - al fons, la **pantalla** gegant entre cortines de vellut granat (de base, el títol de la subhasta; els
    decorats `grafic_112`, `grafic_84`, `grafic_52`, `grafic_31` i `grafic_29` hi posen el gràfic del preu, amb la
    ratlla vermella «LLINDAR DEL BANC» a 30 i el número gran), i dos finestrals a l'espai;
  - l'**escenari** de marbre amb el faristol i el **martell** (a la dreta);
  - les cadires daurades amb els inversors asseguts, de silueta, mirant l'escenari (part del fons);
  - a la dreta, la taula de **cava** (copes en piràmide, la glaçonera) i la **safata** d'argent;
  - a l'esquerra, la porta de la galeria.
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from hd.pix import Canvas, Light, hr, mix
from hd640.rooms.palau_comu import (MARB, ORP, CROM, NEGRE, GRANAT, BLAU, LED, VERMELL, PLATA, RH, _diff, lletres,
                                    lletres_c, lletres_grans, triangle, espai, estrelles_frames, terra2, diposit, gota,
                                    terra_marbre, columna, motllura, marc_or, vidre, ombra, negre_barra, fbm)

# Art a 2× (1280×720 per a una sala de 640×360): el mateix dibuix, amb les formes, el dither i la llum a la
# resolució real (hd1280/canvas2x.py); el motor el mostra a 1/2 (artScale al .room.json).
ART_SCALE = 2
from hd1280.canvas2x import Canvas2x as Canvas  # noqa: E402,F811
from hd.pix import Canvas as Canvas1x  # noqa: E402,F401  (llenços auxiliars en píxels de sala: figures, textos)

PERSONA = 83
WALL_TOP = 12
FLOOR_BACK = 150             # on el terra toca la paret del fons
SCR = (212, 24, 428, 116)    # la pantalla (el vidre)
STAGE = (168, 472, 134, 158, 178)   # x0, x1, y del fons de l'escenari, y de la vora, y de terra
LECTERN = (424, 450)
WINS = ((84, 30, 152, 118), (488, 30, 556, 118))
TABLE = (528, 628, 204, 240)        # x0, x1, y del tauler, y de terra
TRAY = (544, 201)                   # la safata (centre)

_ST = {}

LIGHT = Light(ambient=0.15, vignette=(60, 14), floor_fade=(232, 40))
LIGHT.point(320, 8, r=380, k=1.2, squash=0.8, power=1.3)          # la claror del sostre
LIGHT.point(320, 90, r=200, k=0.7, squash=1.2, power=1.6)         # la pantalla
LIGHT.point(578, 120, r=120, k=0.6, power=1.6)                    # el llum de la taula del cava

SCREEN_BG = [(4, 8, 20), (8, 14, 34), (12, 22, 50), (18, 32, 70), (28, 46, 94)]


# ─── Sostre i parets ────────────────────────────────────────────────────────

def sostre(cv):
    for y in range(0, WALL_TOP + 1):
        for x in range(640):
            cx = (x - 320) * (1 + (WALL_TOP - y) * 0.07)
            v = 4.4 + (0.8 if abs((cx % 52) - 26) < 20 and 2 < y < WALL_TOP - 3 else 0) - (1.6 if (cx % 52) < 1.5 else 0)
            cv.put(x, y, MARB, v)
    motllura(cv, 0, 639, WALL_TOP - 2, h=3)


def paret_fons(cv):
    cv.rect(60, WALL_TOP + 1, 580, FLOOR_BACK, MARB, lambda x, y: 4.8 + (fbm(x / 40, y / 40, 2) - 0.5) * 0.6)
    # plafons de marbre amb filet d'or (entre finestrals i pantalla)
    for x0, x1 in ((66, 78), (160, 176), (464, 480), (562, 574)):
        marc_or(cv, x0, 26, x1, 136, t=1, lvl=3.6)
    motllura(cv, 60, 580, FLOOR_BACK - 8, MARB, 5.6, h=2)
    cv.rect(60, FLOOR_BACK - 6, 580, FLOOR_BACK, MARB, lambda x, y: 3.6 - (y - FLOOR_BACK + 6) * 0.1)
    motllura(cv, 60, 580, FLOOR_BACK - 6, ORP, 4.0, h=1)


def finestrals(cv):
    bright = []
    for i, (x0, y0, x1, y1) in enumerate(WINS):
        bright += espai(cv, x0, y0, x1, y1, seed=21 + i)
        if i == 0:
            terra2(cv, x0 + 6, y1 + 30, 58, mask=lambda x, y: x0 <= x <= x1 and y0 <= y <= y1, seed=3)
        else:
            dep = type(cv)(transparent=True)
            diposit(dep, 524, 62, 0.34)
            D = dep.img.load()
            for X, Y, _, _ in cv.pixels(x0, y0, x1, y1):                                  # (píxels reals)
                if D[X, Y][3]:
                    cv.P[X, Y] = D[X, Y][:3] + (255,)
        vidre(cv, x0, y0, x1, y1, k=0.12, seed=x0)
        cv.hline(x0, x1, y0 + 30, ORP, 3.4)
        cv.vline((x0 + x1) // 2, y0, y1, ORP, 3.4)
        marc_or(cv, x0 - 3, y0 - 3, x1 + 3, y1 + 3, t=3, lvl=4.4)
        cv.rect(x0 - 5, y1 + 4, x1 + 5, y1 + 6, MARB, lambda x, y: 6.6 - (y - y1 - 4))
    return bright


def paret_esq(cv):
    cv.poly([(0, 0), (60, WALL_TOP), (60, FLOOR_BACK), (0, 250)], MARB,
            lambda x, y: 3.8 + x * 0.012 + (fbm(x / 20, y / 30, 31) - 0.5) * 0.6)
    cv.line(0, 2, 60, WALL_TOP + 1, ORP, 4.4)
    cv.line(0, 246, 60, FLOOR_BACK - 2, ORP, 3.6)
    cv.vline(60, WALL_TOP, FLOOR_BACK, MARB, 2.4)
    # la porta de la galeria: blanca i or, en perspectiva
    xa, xb = 10, 50

    def top(x):
        return 118 - (x - xa) * 0.5

    def bot(x):
        return 234 - (x - xa) * 1.6
    for x in range(xa - 4, xb + 4):
        for y in range(int(top(x)) - 12, int(bot(x)) + 1):
            if y < top(x) or x < xa or x >= xb:
                cv.put(x, y, ORP, 4.0 + (1.0 if x == xa - 4 or y == int(top(x)) - 12 else 0))
    mid = (xa + xb) / 2
    for x in range(xa, xb):
        t, b = top(x), bot(x)
        for y in range(int(t), int(b) + 1):
            fy = (y - t) / (b - t)
            lx = (x - xa) if x < mid else (x - mid)
            lw = mid - xa
            panel = 3 < lx < lw - 3 and (0.06 < fy < 0.46 or 0.54 < fy < 0.94)
            v = 5.8 - (x - xa) * 0.03 + (0.6 if panel else 0)
            if panel and (lx < 4.5 or fy < 0.075 or 0.53 < fy < 0.545):
                v -= 1.4
            if abs(x - mid) < 1:
                v = 2.4
            cv.put(x, y, MARB, v)
    for hx in (int(mid) - 3, int(mid) + 2):
        hy = int((top(hx) + bot(hx)) / 2) + 4
        cv.rect(hx, hy - 4, hx, hy + 4, ORP, 5.0)
    lletres(cv, 'GALERIA', xa + 2, int(top(xa + 2)) - 9, (110, 72, 26))


def paret_dreta(cv):
    cv.poly([(640, 0), (580, WALL_TOP), (580, FLOOR_BACK), (640, 250)], MARB,
            lambda x, y: 3.4 - (x - 580) * 0.01 + (fbm(x / 20, y / 30, 33) - 0.5) * 0.6)
    cv.line(640, 2, 580, WALL_TOP + 1, ORP, 4.0)
    cv.line(640, 246, 580, FLOOR_BACK - 2, ORP, 3.2)
    cv.vline(580, WALL_TOP, FLOOR_BACK, MARB, 6.0)
    # un mirall amb marc d'or, en perspectiva (hi brilla la sala)
    for x in range(594, 628):
        f = (x - 594) / 34
        t, b = 40 - f * 7, 150 + f * 22
        for y in range(int(t), int(b)):
            cv.put(x, y, MARB, 3.0 + (1.6 if 8 < (x - y * 0.4) % 30 < 14 else 0) + (fbm(x / 6, y / 20, 3) - 0.5))
        for k in range(2):
            cv.put(x, int(t) - 1 - k, ORP, 4.6 - k)
            cv.put(x, int(b) + k, ORP, 3.2 - k)
    cv.vline(593, 38, 151, ORP, 4.4)
    cv.vline(628, 32, 173, ORP, 3.0)


# ─── Pantalla, cortines i escenari ──────────────────────────────────────────

def pantalla(cv):
    x0, y0, x1, y1 = SCR
    # el bastidor: negre, amb un filet d'or
    cv.rect(x0 - 6, y0 - 6, x1 + 6, y1 + 6, NEGRE, lambda x, y: 1.6 - (y - y0) * 0.004, lit=0)
    marc_or(cv, x0 - 8, y0 - 8, x1 + 8, y1 + 8, t=2, lvl=4.6)
    cv.rect(x0, y0, x1, y1, SCREEN_BG, lambda x, y: 1.4 + (y - y0) / (y1 - y0) * 1.4, lit=0)
    # base: el títol de la subhasta i la gota gran
    gota(cv, (x0 + x1) // 2, y0 + 30, 30)
    lletres_c(cv, 'GRAN SUBHASTA DE L\'AIGUA', (x0 + x1) // 2, y0 + 54, (220, 230, 246))
    lletres_c(cv, 'VERNE S.A.', (x0 + x1) // 2, y0 + 64, (120, 160, 220))
    lletres_c(cv, 'DEU ANYS D\'AIGUA DE VESPER', (x0 + x1) // 2, y0 + 78, (90, 110, 150))
    _scan(cv)


def _scan(cv):
    """Línies d'escombrat suaus (una pantalla gegant de debò) i una lluentor a la cantonada."""
    x0, y0, x1, y1 = SCR
    for y in range(y0, y1 + 1, 3):
        for x in range(x0, x1 + 1):
            o = cv.get(x, y)
            if o[3]:
                cv.flat(x, y, tuple(int(c * 0.86) for c in o[:3]))
    for y in range(y0, y0 + 26):
        for x in range(x1 - 40 + (y - y0), x1 - 30 + (y - y0)):
            if x <= x1:
                o = cv.get(x, y)
                if o[3]:
                    cv.flat(x, y, mix(o, (200, 220, 255), 0.08))


def cortines(cv):
    """Dues cortines de vellut granat, recollides amb cordons d'or, i la galeria de dalt."""
    for side in (0, 1):
        xa, xb = (176, 210) if side == 0 else (430, 464)
        for y in range(WALL_TOP + 1, STAGE[2] + 1):
            # es recull a l'alçada del cordó
            pinch = max(0.0, 1 - abs(y - 92) / 40) * 10
            a = xa + (pinch if side == 0 else 0)
            b = xb - (pinch if side == 1 else 0)
            for x in range(int(a), int(b) + 1):
                u = (x - a) / max(1, b - a)
                fold = math.sin(u * math.pi * 5 + (0.4 if side else 0))
                v = 3.2 + fold * 1.4 + (0.6 if y > 92 else 0) - (1.0 if side == 1 and u > 0.8 else 0)
                cv.put(x, y, GRANAT, v)
        cx = xa + 10 if side == 0 else xb - 10
        cv.disc(cx, 92, 4, 3, ORP, lambda nx, ny: 5 - ny * 1.5)              # el cordó
        for k in range(10):
            cv.put(cx + (k % 2), 95 + k, ORP, 4.6 - k * 0.2)
        cv.rect(cx - 2, 104, cx + 2, 110, ORP, lambda x, y: 4.4 - (y - 104) * 0.2)
    # la galeria (bambolina) per sobre de la pantalla
    for y in range(WALL_TOP + 1, WALL_TOP + 9):
        for x in range(170, 471):
            scallop = (y - WALL_TOP) > 5 + 2 * math.cos((x - 170) / 37 * 2 * math.pi)
            if not scallop:
                cv.put(x, y, GRANAT, 3.6 + math.sin((x - 170) / 37 * 2 * math.pi) * 0.8)
    motllura(cv, 170, 470, WALL_TOP + 1, ORP, 4.6, h=2)


def escenari(cv):
    x0, x1, yb, yf, yg = STAGE
    # el damunt (fusta clara de marbre) i la paret del davant amb filet d'or
    terra_marbre(cv, yb, yf - 1, vp=(320, 40), base=6.6, tile=44, x0=x0, x1=x1, seed=11)
    cv.rect(x0, yf, x1, yg, MARB, lambda x, y: 4.6 - (y - yf) * 0.06 + (fbm(x / 26, y / 8, 5) - 0.5) * 0.6)
    motllura(cv, x0, x1, yf, ORP, 4.8, h=3)
    motllura(cv, x0, x1, yg - 3, ORP, 3.6, h=2)
    # plafons a la paret del davant
    for px in range(x0 + 10, x1 - 40, 52):
        marc_or(cv, px, yf + 6, px + 42, yg - 6, t=1, lvl=3.6)
    # els graons del mig
    for k in range(3):
        a, b = 290 - k * 4, 350 + k * 4
        y = yg + k * 4
        cv.rect(a, y, b, y + 3, MARB, lambda x, yy: 7.0 if yy == y else 5.0)
        cv.hline(a, b, y + 3, MARB, 2.6)
    # el faristol i el martell
    lx0, lx1 = LECTERN
    cv.poly([(lx0, yf - 2), (lx1, yf - 2), (lx1 - 3, yf - 36), (lx0 + 3, yf - 36)], MARB,
            lambda x, y: 5.6 - (x - lx0) * 0.06)
    marc_or(cv, lx0 + 5, yf - 32, lx1 - 5, yf - 8, t=1, lvl=4.0)
    gota(cv, (lx0 + lx1) // 2, yf - 20, 9, lit=1)
    cv.poly([(lx0 - 3, yf - 36), (lx1 + 3, yf - 36), (lx1 + 1, yf - 42), (lx0 - 1, yf - 42)], ORP,
            lambda x, y: 4.8 - (y - yf + 42) * 0.2)
    # el martell: mànec de fusta fosca i cap d'or, damunt la base rodona
    cv.disc(437, yf - 43, 5, 1.6, ORP, 3.2)
    cv.line(430, yf - 46, 444, yf - 50, [(30, 16, 10), (60, 34, 20), (96, 56, 32), (140, 90, 50)], 2.4)
    cv.rect(440, yf - 54, 446, yf - 47, ORP, lambda x, y: 5.0 - (x - 440) * 0.3)
    cv.hline(440, 446, yf - 54, ORP, 6.4)


# ─── Cadires i inversors ────────────────────────────────────────────────────

INV = [(30, 30, 40), (40, 40, 52), (56, 54, 66), (80, 76, 86)]
# la roba i el cabell dels inversors: foscos, però no tots iguals
ROBA = ([(14, 16, 28), (22, 26, 44), (34, 40, 64), (56, 64, 94)],          # blau marí
        [(20, 20, 22), (32, 32, 36), (48, 48, 54), (72, 72, 80)],          # gris marengo
        [(30, 10, 16), (50, 16, 26), (76, 26, 38), (110, 44, 54)],         # granat
        [(18, 26, 22), (28, 40, 34), (42, 58, 48), (64, 82, 68)])          # verd ampolla
CABELL = ([(14, 12, 12), (26, 22, 20), (40, 34, 30), (60, 52, 44)],
          [(70, 70, 74), (110, 110, 112), (150, 150, 150), (196, 196, 192)],
          [(40, 24, 14), (70, 44, 24), (100, 66, 36), (136, 96, 56)],
          [(150, 140, 120), (196, 186, 160), (226, 218, 196), (246, 240, 224)])


def cadira(cv, x, yfloor, s=1.0, ocupada=True, seed=0):
    """Una cadira daurada vista de darrere i, si està ocupada, un inversor assegut (silueta)."""
    h = int(40 * s)
    w = int(14 * s)
    top = yfloor - h
    # potes
    for lx in (x - w // 2, x + w // 2):
        cv.vline(lx, yfloor - int(16 * s), yfloor, ORP, 3.4)
    if ocupada:
        # l'inversor: espatlles, coll i cap (de vegades, un barret o un monyo)
        sh = yfloor - int(48 * s)
        kind = int(hr(seed, 3) * 7)
        roba = ROBA[int(hr(seed, 5) * 4)]
        cab = CABELL[int(hr(seed, 6) * 4)]
        cv.disc(x, sh + int(10 * s), 9.5 * s, int(10 * s), roba,
                lambda nx, ny: 1.2 - nx * 0.5 + (1.0 if ny < -0.75 else 0), lit=0.4)
        hx = x + int((hr(seed, 4) - 0.5) * 3)
        hy = sh - int(6 * s)
        cv.rect(hx - 2, hy + int(3 * s), hx + 2, sh + 2, [(40, 26, 24), (70, 46, 40), (110, 76, 62)], 0.8, lit=0)
        cv.disc(hx, hy, 5.0 * s, 6.0 * s, cab, lambda nx, ny: 1.4 - nx * 0.5 + (1.0 if ny < -0.6 else 0), lit=0.4)
        if kind == 0:                                                # barret de copa
            cv.rect(hx - int(5 * s), hy - int(15 * s), hx + int(5 * s), hy - int(5 * s), INV, 0.8, lit=0)
            cv.hline(hx - int(7 * s), hx + int(7 * s), hy - int(5 * s), INV, 1.6, lit=0)
            cv.hline(hx - int(5 * s), hx + int(5 * s), hy - int(7 * s), GRANAT, 3.0, lit=0)
        elif kind == 1:                                              # monyo
            cv.disc(hx, hy - int(6 * s), 3.2 * s, 3.0 * s, cab, 1.8, lit=0)
        elif kind == 2:                                              # collar de perles
            cv.hline(hx - 3, hx + 3, sh + 1, PLATA, 3.4, lit=0)
        elif kind == 3:                                              # calb, amb la llum al crani
            cv.disc(hx, hy, 4.8 * s, 5.8 * s, [(60, 40, 34), (100, 68, 56), (150, 110, 90), (196, 156, 130)],
                    lambda nx, ny: 1.2 - nx * 0.6 + (1.4 if ny < -0.5 and nx < 0.2 else 0), lit=0.3)
        # la llum de la pantalla, a la vora de dalt del cap
        cv.hline(hx - 1, hx + 1, hy - int(6 * s), cab, 3.0, lit=0)
    # el respatller: marc d'or amb barrots, i el seient
    cv.rect(x - w // 2, top, x + w // 2, top + 1, ORP, 5.0)
    cv.disc(x, top, w // 2, 2, ORP, lambda nx, ny: 5.4 - ny * 1.4)
    for k in range(-w // 2, w // 2 + 1, max(2, int(3 * s))):
        cv.vline(x + k, top + 1, top + int(18 * s), ORP, 4.0 if k < 0 else 3.2)
    cv.vline(x - w // 2, top, top + int(20 * s), ORP, 5.0)
    cv.vline(x + w // 2, top, top + int(20 * s), ORP, 3.0)
    cv.rect(x - w // 2 - 1, top + int(18 * s), x + w // 2 + 1, top + int(21 * s), GRANAT, lambda xx, yy: 4.0 - (yy - top) * 0.05)


def files(cv):
    rows = ((196, 0.9, 24), (214, 1.0, 27))
    for r, (yf, s, step) in enumerate(rows):
        for block in ((104 - r * 6, 292), (360 + r * 4, 548 - r * 30)):
            xs = list(range(block[0], block[1], step))
            for i, x in enumerate(xs):
                seed = r * 50 + i + block[0]
                ocu = hr(seed, 7) > (0.18 if r == 0 else 0.3)
                cadira(cv, x, yf, s, ocu, seed)


# ─── La taula del cava ──────────────────────────────────────────────────────

def copa(cv, x, y, s=1.0, plena=True):
    """Una copa de cava (flauta): peu, tija i calze amb el cava daurat."""
    cv.hline(x - 2, x + 2, y, CROM, 5.0)
    cv.vline(x, y - 4, y - 1, CROM, 6.0)
    for k in range(7):
        cv.put(x - 1, y - 5 - k, CROM, 6.4)
        cv.put(x + 1, y - 5 - k, CROM, 4.6)
        cv.put(x, y - 5 - k, ORP if plena and k < 5 else CROM, 5.8 if plena else 6.6)
    if plena:
        cv.flat(x, y - 9, (255, 250, 220))


def taula(cv):
    x0, x1, yt, yg = TABLE
    ombra(cv, (x0 + x1) // 2 - 6, yg + 2, (x1 - x0) // 2 + 6, 4, 0.6)
    # estovalles blanques fins a terra, amb plecs, i un tapet d'or
    cv.rect(x0, yt - 6, x1, yt, MARB, lambda x, y: 7.6 - (y - yt + 6) * 0.1)
    for y in range(yt, yg + 1):
        for x in range(x0, x1 + 1):
            fold = math.sin((x - x0) * 0.42) * (y - yt) / (yg - yt)
            cv.put(x, y, MARB, 6.6 + fold * 1.0 - (x - x0) * 0.008)
    cv.hline(x0, x1, yt, MARB, 4.8)
    for x in range(x0 + 4, x1 - 2, 8):                                   # garlanda d'or
        for k in range(8):
            cv.put(x + k, yt + 3 + int(math.sin(k / 7 * math.pi) * 3), ORP, 4.6)
    # la piràmide de copes (de cava)
    for row, n in enumerate((5, 4, 3, 2, 1)):
        for i in range(n):
            copa(cv, 576 + i * 6 - n * 3 + 3, yt - 7 - row * 11)
    # la glaçonera d'argent amb dues ampolles
    bx = 612
    for k, (dx, h) in enumerate(((-3, 26), (4, 24))):
        cv.rect(bx + dx - 2, yt - 6 - h, bx + dx + 2, yt - 14, [(10, 30, 16), (20, 50, 28), (34, 80, 44), (60, 120, 70)],
                lambda x, y: 2.0 - (x - bx - dx) * 0.4)
        cv.rect(bx + dx - 1, yt - 10 - h, bx + dx + 1, yt - 6 - h, ORP, 5.0)
    cv.poly([(bx - 9, yt - 20), (bx + 9, yt - 20), (bx + 7, yt - 7), (bx - 7, yt - 7)], CROM,
            lambda x, y: 6.0 - (x - bx + 9) * 0.22)
    cv.hline(bx - 10, bx + 10, yt - 21, CROM, 7.0)


def safata(cv):
    """La safata d'argent, a la punta de la taula, amb tres copes plenes (aquí hi deixarà les claus l'Iri)."""
    cx, cy = TRAY
    cv.disc(cx, cy, 14, 3.4, CROM, lambda nx, ny: 6.4 - ny * 1.6 - nx * 0.6)
    cv.disc(cx, cy - 0.5, 11.5, 2.2, CROM, lambda nx, ny: 4.6 + ny * 0.8)
    for dx in (-6, 0, 6):
        copa(cv, cx + dx, cy - 1 + (1 if dx == 0 else 0))


# ─── Gràfics de la pantalla ─────────────────────────────────────────────────

SERIE = [40, 41, 43, 44, 46, 48, 52, 60, 66, 75, 88, 100, 112]
CAIGUDA = {112: [], 84: [84], 52: [84, 52], 31: [84, 52, 31], 29: [84, 52, 31, 29]}


def grafic(cv, n):
    """La pantalla amb el gràfic del preu fins a `n`: eixos, la línia, la ratlla del LLINDAR a 30 i el número."""
    x0, y0, x1, y1 = SCR
    cv.rect(x0, y0, x1, y1, SCREEN_BG, lambda x, y: 1.2 + (y - y0) / (y1 - y0) * 1.0, lit=0)
    gx0, gx1, gy0, gy1 = x0 + 20, x1 - 70, y0 + 12, y1 - 12

    def Y(v):
        return gy1 - (v / 120) * (gy1 - gy0)
    # la graella i els eixos
    for v in (0, 30, 60, 90, 120):
        for x in range(gx0, gx1 + 1, 3):
            cv.flat(x, int(Y(v)), (24, 40, 70))
        lletres(cv, str(v), x0 + 3, int(Y(v)) - 2, (90, 110, 150))
    cv.vline(gx0, gy0, gy1, SCREEN_BG, 4.0, lit=0)
    cv.hline(gx0, gx1, gy1, SCREEN_BG, 4.0, lit=0)
    # la ratlla del LLINDAR DEL BANC, a 30
    yl = int(Y(30))
    for x in range(gx0, x1 - 3):
        if (x // 4) % 2 == 0:
            cv.flat(x, yl, (230, 50, 40))
            cv.flat(x, yl + 1, (150, 26, 24))
    lletres(cv, 'LLINDAR DEL BANC', gx0 + 4, yl + 4, (236, 80, 64))
    # la línia del preu
    vals = SERIE + CAIGUDA[n]
    m = len(SERIE) + 4
    pts = [(gx0 + 2 + i * (gx1 - gx0 - 4) / (m - 1), Y(v)) for i, v in enumerate(vals)]
    baixa = n != 112
    col = (250, 150, 50)
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        drop = yb > ya
        c = (240, 70, 56) if drop else col
        steps = int(max(abs(xb - xa), abs(yb - ya))) + 1
        for k in range(steps + 1):
            t = k / steps
            x, y = round(xa + (xb - xa) * t), round(ya + (yb - ya) * t)
            cv.flat(x, y, c)
            cv.flat(x, y + 1, tuple(v // 2 for v in c))
    lx, ly = pts[-1]
    cv.disc(lx, ly, 2, 2, [(255, 255, 255)], 0, lit=0)
    # el número gran, amb ▲ o ▼
    s = str(n)
    numc = (250, 150, 50) if not baixa else (240, 70, 56) if n < 30 else (255, 200, 120)
    tw = lletres_grans(cv, s, x1 - 62, y0 + 18, numc, k=3)
    lletres(cv, 'C', x1 - 62 + tw + 2, y0 + 30, numc)
    triangle(cv, x1 - 40, y0 + 46, 7, numc if not baixa else (240, 70, 56), amunt=not baixa)
    lletres(cv, 'PER LITRE', x1 - 64, y0 + 58, (120, 140, 180))
    if n == 29:
        lletres(cv, 'EXECUCIÓ', x1 - 64, y0 + 70, (240, 70, 56))
        lletres(cv, 'DEL BANC', x1 - 64, y0 + 77, (240, 70, 56))
    elif n == 31:
        lletres(cv, 'PER POC', x1 - 64, y0 + 70, (200, 180, 120))
    _scan(cv)


# ─── Composició ─────────────────────────────────────────────────────────────

def bg(cv):
    sostre(cv)
    paret_fons(cv)
    _ST['bright'] = finestrals(cv)
    pantalla(cv)
    cortines(cv)
    # el terra: marbre, amb una catifa granat pel passadís del mig
    terra_marbre(cv, FLOOR_BACK + 1, RH - 1, vp=(320, 20), base=5.8, tile=46)
    for y in range(STAGE[4] + 10, RH):
        f = (y - FLOOR_BACK) / (RH - FLOOR_BACK)
        a, b = 320 - 18 - f * 26, 320 + 18 + f * 26
        for x in range(int(a), int(b) + 1):
            edge = x - a < 2 or b - x < 2
            cv.put(x, y, ORP if edge else GRANAT, 4.4 if edge else 3.4 + (fbm(x / 6, y / 4, 8) - 0.5) * 0.6)
    paret_esq(cv)
    paret_dreta(cv)
    ombra(cv, 320, STAGE[4] + 2, 160, 5, 0.5)
    escenari(cv)
    files(cv)
    taula(cv)
    safata(cv)
    negre_barra(cv)


@functools.lru_cache(maxsize=None)
def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv.img


def _grafic(n):
    return lambda cv: grafic(cv, n)


PROPS = {f'grafic_{n}': _grafic(n) for n in (112, 84, 52, 31, 29)}


def _frames_estrelles():
    tmp = Canvas(light=LIGHT)
    bright = finestrals(tmp)
    return estrelles_frames(_base(), bright, n=10, seed=5)


ANIMS = {'estrelles': {'frames': _frames_estrelles, 'frameDuration': 300}}


# ─── Geometria (640×360) ────────────────────────────────────────────────────

GEOMETRIA = {
    'things': {
        'porta_galeria': {'rect': (6, 104, 54, 236), 'walk': (40, 236)},
        'pantalla': {'rect': SCR, 'walk': (320, 224)},
        'escenari': {'rect': (168, 130, 420, 190), 'walk': (320, 224)},
        'martell': {'rect': (422, 100, 454, 158), 'walk': (420, 222)},
        'safata': {'rect': (528, 188, 560, 206), 'walk': (528, 246)},
        'cava': {'rect': (562, 152, 628, 240), 'walk': (580, 248)},
    },
    'spawns': {'iri': (96, 246), 'verne': (320, 156), 'holm': (210, 236), 'kessel': (476, 240)},
    'walkable': [(4, 254), (28, 230), (74, 220), (522, 220), (522, 244), (634, 248), (634, 256), (4, 256)],
}
