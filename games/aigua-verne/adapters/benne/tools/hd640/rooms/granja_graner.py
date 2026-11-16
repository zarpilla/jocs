"""
El graner de la granja (Escena 1 i 2). Sala «de prop» (persones de ≈100 px).

Fusta vella, penombra i pols en els raigs de sol que entren per les escletxes de la teulada.
  - a l'esquerra, el banc de llavors del pare: quatre prestatges de sacs de tela ordenats, amb etiquetes a mà;
  - la porta gran, oberta al pati: fora, el sol, el camp sec i la Canonada a l'horitzó;
  - el clau on penja el reg gota a gota (el reg és un prop: es pot endur);
  - el tractor vermell de l'avi, el Brau 40, de perfil: rovellat, amb les rodes grosses rebentades;
  - el banc de treball, amb la caixa d'eines vermella; bales de palla, una forca, una lluerna d'oli.
Props: `reg` (el rotllo de tub negre i els goters, penjat), `tractor_obert` (el capó aixecat, sense l'injector),
`sacs_tres` (tres sacs a terra, a punt per carregar) i `sac_quart` (el quart sac, apartat).
ANIMS: `pols` (les volves de pols dins els raigs de sol).
"""
import math

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from PIL import Image

from hd.pix import Canvas, Light, W, H, hr, mix, B4
from hd.rooms.exterior import fbm, smooth
from hd640.rooms.terra2_comu import (
    RH, SKY, HILL, FIELD, EARTH, COL, PLANK, GREYW, STONE, BLACKT, IRONR, RUSTT, REDT, CLOTH, PAPER, STRAW,
    WHITEP, WARN, text, text_width, outline, shadow, motes_frames, _diff)

# Art a 2× (1280×720 per a una sala de 640×360): el mateix dibuix, amb les formes, el dither i la llum a la
# resolució real (hd1280/canvas2x.py); el motor el mostra a 1/2 (artScale al .room.json).
ART_SCALE = 2
from hd1280.canvas2x import Canvas2x as Canvas  # noqa: E402,F811
from hd.pix import Canvas as Canvas1x  # noqa: E402,F401  (llenços auxiliars en píxels de sala: figures, textos)

FLOOR_Y = 206
DOOR = (196, 70, 300, FLOOR_Y)             # el portal gran, obert al pati
TR_GROUND = 230                            # on toquen a terra les rodes del tractor
RW = (522, 196, 36)                        # la roda del darrere (x, y, radi)
FW = (408, 210, 20)                        # la roda del davant
SUN = (255, 222, 160)

WOOD = [(20, 14, 12), (34, 24, 18), (50, 36, 26), (68, 50, 34), (90, 66, 44), (114, 86, 56), (140, 108, 72),
        (166, 132, 92)]                                                     # la fusta de dins, fosca
DIRT = [(28, 20, 16), (44, 32, 24), (62, 46, 32), (82, 62, 42), (104, 80, 54), (128, 100, 68), (152, 122, 84),
        (176, 146, 104)]
TRED = [(34, 8, 8), (64, 14, 12), (100, 22, 18), (138, 32, 24), (174, 46, 32), (206, 70, 46), (230, 110, 76)]
TYRE = [(10, 10, 10), (20, 20, 20), (32, 30, 30), (46, 44, 42), (62, 60, 56)]
ENG = [(16, 16, 18), (30, 30, 34), (48, 48, 52), (70, 70, 74), (96, 96, 98), (128, 126, 124), (164, 160, 154)]
TAGS = [(200, 190, 160), (230, 222, 196), (246, 240, 220)]

LIGHT = Light(ambient=-0.4, vignette=(80, 30), floor_fade=(248, 30))
LIGHT.point(248, 150, r=240, k=2.4, squash=0.8, power=1.4)               # el sol del portal
LIGHT.point(450, 230, r=150, k=0.8, squash=1.6, power=1.6)               # els raigs, a terra
LIGHT.point(560, 120, r=120, k=0.5, power=1.6)

# els raigs de sol: (x a dalt, y a dalt, x a baix, y a baix, amplada a dalt, amplada a baix)
RAYS = [(486, 18, 404, 244, 3, 12), (512, 20, 440, 246, 2, 8), (590, 22, 520, 250, 3, 11), (150, 16, 92, 236, 2, 7)]


def rays(x, y):
    """Quant hi ha de raig de sol a (x, y): 0..1."""
    v = 0.0
    for xt, yt, xb, yb, wt, wb in RAYS:
        if yt <= y <= yb:
            t = (y - yt) / (yb - yt)
            cx = xt + (xb - xt) * t
            hw = wt + (wb - wt) * t
            d = abs(x - cx)
            v = max(v, (1 - smooth(hw * 0.5, hw, d)) * (1 - max(0.0, t - 0.92) / 0.08))
    return v


# ─── Sostre, parets, terra ──────────────────────────────────────────────────

def walls(cv):
    def plank_lvl(x, y):
        p = (x + 3) // 13
        e = (x + 3) % 13
        v = 2.4 + (hr(p, 1) - 0.5) * 1.0 + (fbm(x / 4, y / 30, p) - 0.5) * 1.0
        if e == 0:
            v -= 1.6
        elif e == 1:
            v += 0.6
        if hr(p, y // 40) > 0.85 and e in (6, 7) and (y % 40) < 3:
            v -= 1.2                                                         # un nus
        return v
    cv.rect(0, 0, W - 1, FLOOR_Y, WOOD, plank_lvl)
    # les escletxes entre les taules, per on es veu el sol de fora
    for x in range(10, W, 13):
        if hr(x, 5) > 0.55:
            y0 = 30 + int(hr(x, 6) * 90)
            for y in range(y0, y0 + 12 + int(hr(x, 7) * 30)):
                cv.flat(x - 3, y, (236, 196, 130) if (y + x) % 5 else (255, 226, 170))
    # la travessa del mig de la paret (on es claven les coses) i la de baix
    for ty in (62, FLOOR_Y - 14):
        cv.rect(0, ty, W - 1, ty + 5, WOOD, lambda x, y: 3.4 - (y - ty) * 0.35 + (fbm(x / 9, y, 4) - 0.5) * 0.6)
        cv.rect(0, ty + 6, W - 1, ty + 6, BLACKT, 1.0)
    # l'encavallada de la teulada, a dalt
    cv.rect(0, 0, W - 1, 14, WOOD, lambda x, y: 1.0 + (fbm(x / 7, y / 3, 9) - 0.5) * 0.8)
    for sx in range(-40, W + 40, 90):
        for k in range(4):
            cv.line(sx + k, 0, sx + 50 + k, 14, WOOD, 2.6 - k * 0.4)
    cv.rect(0, 14, W - 1, 20, WOOD, lambda x, y: 3.8 - (y - 14) * 0.4)
    cv.rect(0, 21, W - 1, 22, BLACKT, 1.0)
    # forats a la teulada: el sol
    for xt, yt, xb, yb, wt, wb in RAYS:
        cv.rect(xt - wt + 1, 8, xt + wt - 1, 12, SKY, 6.4, lit=0)
        cv.rect(xt - wt + 1, 7, xt + wt - 1, 7, WOOD, 1.0)


def floor(cv):
    for y in range(FLOOR_Y + 1, RH):
        t = (y - FLOOR_Y) / (RH - FLOOR_Y)
        for x in range(W):
            lvl = 2.6 + t * 0.8 + (fbm(x / 26, y / 7, 31) - 0.5) * 1.2 + (hr(x // 2, y) - 0.5) * 0.5
            cv.put(x, y, DIRT, lvl)
    # palla escampada per terra
    for i in range(260):
        x, y = hr(i, 1) * W, FLOOR_Y + 2 + hr(i, 2) * (RH - FLOOR_Y - 3)
        a = hr(i, 3) * math.pi
        l = 2 + hr(i, 4) * 4
        cv.line(x, y, x + math.cos(a) * l, y + math.sin(a) * l * 0.4, STRAW, 2.4 + hr(i, 5) * 1.6)
    cv.darken(0, FLOOR_Y + 1, W - 1, FLOOR_Y + 4, lambda x, y: 0.6 - (y - FLOOR_Y) * 0.12)


# ─── La porta ───────────────────────────────────────────────────────────────

def doorway(cv):
    """El portal obert: fora, el sol del pati, el camp sec, els turons i la Canonada."""
    x0, y0, x1, y1 = DOOR
    hor = 150
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if y < hor - 6:
                cv.put(x, y, SKY, 3.6 + (y - y0) / (hor - y0) * 2.6 + (fbm(x / 40, y / 12, 31) - 0.5) * 0.6, lit=0)
            elif y < hor:
                cv.put(x, y, HILL, 4.4 + (fbm(x / 9, 0, 3) - 0.5), lit=0)
            elif y < 176:
                cv.put(x, y, FIELD, 4.2 + (y - hor) * 0.03 + math.sin((x - 248) / max(1, y - hor + 4) * 9) * 0.6, lit=0)
            else:
                cv.put(x, y, EARTH, 5.6 + (hr(x // 2, y) - 0.5) * 0.6 - (1.8 if hr(x // 5, y // 3) > 0.88 else 0), lit=0)
    for y in range(y0, hor):                                                 # la Canonada, lluny
        cv.put(272, y, COL, 3.6 if y % 9 else 5.0, lit=0)
        cv.put(273, y, COL, 4.6, lit=0)
    for x in range(x0, x1 + 1, 14):                                          # la tanca del pati, a contrallum
        cv.rect(x, 160, x + 1, 176, GREYW, 3.2, lit=0)
    cv.rect(x0, 165, x1, 165, GREYW, 3.4, lit=0)
    # el marc i les fulles de la porta, obertes cap endins
    cv.rect(x0 - 5, y0 - 6, x1 + 5, y0 - 1, WOOD, lambda x, y: 3.6 - (y - y0 + 6) * 0.3)
    for sx in (x0 - 5, x1 + 1):
        cv.rect(sx, y0 - 1, sx + 4, y1, WOOD, lambda x, y: 3.4 + (x - sx) * 0.2)
    for side, (a, b) in enumerate(((x0 - 5, x0 - 34), (x1 + 5, x1 + 34))):
        lo, hi = min(a, b), max(a, b)
        cv.poly([(a, y0 - 1), (b, y0 + 8), (b, y1 + 10), (a, y1)], WOOD,
                lambda x, y: (2.2 if side == 0 else 3.0) - (1.4 if (x - lo) % 7 == 0 else 0) + (fbm(x / 4, y / 20, 2) - 0.5) * 0.8)
        cv.line(a, y0 + 18, b, y0 + 26, WOOD, 4.0)
        cv.line(a, y1 - 18, b, y1 - 10, WOOD, 4.0)
        cv.line(a, y1 - 18, b, y0 + 26, WOOD, 3.6)
    # el sol que entra i cau a terra, davant del portal (cap a l'esquerra: el sol és a la dreta)
    for X, Y, x, y in cv.pixels(x0 + 4 - 40, FLOOR_Y + 1, x1 - 2, RH - 1):     # (píxel a píxel, a la resolució real)
        t = (y - FLOOR_Y) / (RH - FLOOR_Y)
        a, b = x0 + 4 - 40 * t, x1 - 2 - 22 * t
        e = min(x - a, b - x)
        k = 0.45 * min(1.0, e / 6)
        if k > B4[Y & 3][X & 3] * 0.6:
            cv.P[X, Y] = mix(cv.P[X, Y], SUN, k) + (255,)
    for xx in range(x0, x1 + 1):                                              # el llindar
        cv.put(xx, y1, WOOD, 4.0)


# ─── El banc de llavors ─────────────────────────────────────────────────────

def _sack(cv, cx, base, w, h, k, ramp=CLOTH, tag=True, lvl=3.4):
    """Un sac de tela, lligat a dalt, amb l'etiqueta escrita a mà."""
    for y in range(base - h, base + 1):
        t = (y - base + h) / h
        hw = w / 2 * (0.55 + 0.45 * math.sin(min(1.0, t * 1.3) * math.pi / 2)) - (1 if t > 0.96 else 0)
        for x in range(int(cx - hw), int(cx + hw) + 1):
            u = (x - cx) / max(1, hw)
            cv.put(x, y, ramp, lvl + u * 0.9 - t * 0.4 + ((x + y * 2) % 4 == 0) * 0.4 - (1.2 if abs(u) > 0.9 else 0))
    cv.rect(cx - 2, base - h - 4, cx + 2, base - h, ramp, lvl - 0.6)           # la boca lligada
    cv.rect(cx - 3, base - h + 1, cx + 3, base - h + 1, IRONR, 2.0)          # el cordill
    if tag:
        tx, ty = int(cx - 3 + (k % 3) - 1), base - h // 2
        cv.rect(tx, ty, tx + 6, ty + 4, TAGS, 1.6, lit=0.6)
        for i in range(1, 6, 2):
            cv.flat(tx + i, ty + 2, (60, 50, 50))
        if k % 2:
            cv.flat(tx + 2, ty + 1, (40, 60, 140))


def seeds(cv):
    """Els prestatges de llavors: quatre lleixes de sacs ben ordenats, amb etiquetes a mà."""
    x0, x1 = 14, 176
    cv.rect(x0, 30, x1, FLOOR_Y, BLACKT, lambda x, y: 0.8 + (fbm(x / 20, y / 20, 3) - 0.5) * 0.6)   # el fons, fosc
    shelves = (68, 110, 152, 194)
    for side in (x0, x1 - 5):
        cv.rect(side, 30, side + 5, FLOOR_Y, WOOD, lambda x, y: 3.6 + (x - side) * 0.15)
    n = 0
    for sy in shelves:
        x = x0 + 10
        while x < x1 - 14:
            w = 16 + int(hr(x, sy) * 6)
            h = 22 + int(hr(sy, x) * 10)
            _sack(cv, x + w // 2, sy - 1, w, min(h, 34), n, ramp=CLOTH, lvl=3.0 + hr(n, 2) * 0.8)
            n += 1
            x += w + 2
        cv.rect(x0, sy, x1, sy + 4, WOOD, lambda x, y: 4.2 - (y - sy) * 0.5)
        cv.rect(x0, sy + 5, x1, sy + 5, BLACKT, 1.0)
    # el rètol de dalt, pintat a mà
    cv.rect(x0 + 30, 32, x1 - 30, 44, PAPER, lambda x, y: 4.0 + (fbm(x / 4, y / 4, 8) - 0.5) * 0.8)
    s = 'LLAVORS'
    text(cv, s, (x0 + x1) // 2 - text_width(s) // 2, 35, BLACKT, 1.0, lit=0, flat=(70, 40, 30))


# ─── El tractor ─────────────────────────────────────────────────────────────

def _wheel(cv, cx, cy, r, tread=True, hub=TRED):
    """Una roda vista de perfil: el pneumàtic amb els tacs, la llanta vermella i el botó."""
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            d = math.hypot(x - cx, y - cy)
            if d <= r:
                a = math.atan2(y - cy, x - cx)
                if d > r * 0.62:
                    lug = tread and d > r - 4 and int((a + math.pi) / (2 * math.pi) * 28) % 2 == 0
                    lvl = 2.2 - (y - cy) / r * 0.8 + (x - cx) / r * 0.5 + (1.0 if lug else 0) - (1.0 if d > r - 1 else 0)
                    if hr(int(a * 6), 3) > 0.85 and d > r - 6:
                        lvl -= 1.2                                           # rebentat
                    cv.put(x, y, TYRE, lvl)
                elif d > r * 0.56:
                    cv.put(x, y, TYRE, 0.6)
                else:
                    lvl = 3.4 - (y - cy) / r * 1.2 + (x - cx) / r * 0.6
                    if abs(d - r * 0.3) < 1.2:
                        lvl -= 1.4
                    rust = fbm(x / 4, y / 4, 66) > 0.62
                    cv.put(x, y, RUSTT if rust else hub, lvl - (0.4 if rust else 0))
    for k in range(6):                                                       # els cargols de la llanta
        a = k * math.pi / 3
        cv.put(cx + math.cos(a) * r * 0.2, cy + math.sin(a) * r * 0.2, IRONR, 4.6)
    cv.disc(cx, cy, max(2, r * 0.1), max(2, r * 0.1), IRONR, 3.6)


def tractor(cv):
    """El Brau 40 de l'avi, de perfil (el morro a l'esquerra): capó llarg, el seient de ferro, el volant, el tub
    d'escapament, el guardafang de la roda grossa. Vermell, rovellat a clapes."""
    rx, ry, rr = RW
    fx, fy, fr = FW
    shadow(cv, 470, TR_GROUND + 2, 104, 6, 0.8)

    def paint(x, y, base):
        v = base + (fbm(x / 10, y / 10, 12) - 0.5) * 0.7
        if fbm(x / 6, y / 6, 77) > 0.64:
            return RUSTT, v - 0.4
        return TRED, v
    # el xassís, per sota
    cv.rect(fx - 6, 196, rx - 10, 204, ENG, lambda x, y: 2.0 + (0.8 if y == 196 else 0))
    # el capó: un bloc llarg arrodonit a davant
    hx0, hx1, ht, hb = fx - 22, rx - 34, 150, 192
    for y in range(ht, hb + 1):
        for x in range(hx0, hx1 + 1):
            if x < hx0 + 8 and math.hypot(x - hx0 - 8, y - ht - 8) > 8 and y < ht + 8:
                continue
            ramp, v = paint(x, y, 4.0 - (y - ht) * 0.045 + (1.0 if y < ht + 3 else 0))
            if (x - hx0) in (34, 35) or y == ht + 14:
                v -= 1.6                                                     # les juntes del capó
            cv.put(x, y, ramp, v)
    for k in range(5):                                                        # les reixetes del costat
        gx = hx0 + 46 + k * 6
        cv.rect(gx, ht + 20, gx + 2, ht + 34, ENG, lambda x, y: 1.4 + (x - gx) * 0.6)
    # la graella del davant (es veu de cantell)
    cv.rect(hx0 - 3, ht + 6, hx0, hb - 2, ENG, lambda x, y: 2.0 + (1.4 if y % 3 == 0 else 0))
    cv.disc(hx0 + 6, ht + 12, 4, 4, [(70, 60, 30), (150, 140, 80), (230, 220, 150), (255, 250, 210)],
            lambda nx, ny: 2.4 - nx - ny)                                     # el far
    cv.ring(hx0 + 6, ht + 12, 4, ENG, 3.0, step=12)
    # el motor, per sota del capó (a l'ombra)
    cv.rect(hx0 + 10, hb + 1, hx1 - 4, 200, ENG, lambda x, y: 1.6 + ((x // 4) % 2) * 0.6)
    # el tub d'escapament, vertical, al davant del capó
    ex = hx0 + 26
    cv.rect(ex, 112, ex + 3, ht, ENG, lambda x, y: 2.4 + (x - ex) * 0.6 - (0.8 if fbm(x, y / 5, 5) > 0.6 else 0))
    cv.rect(ex - 1, 110, ex + 4, 113, RUSTT, 2.6)
    cv.line(ex - 1, 109, ex + 4, 108, RUSTT, 3.4)                             # la tapeta
    # el tauler, el volant i el seient
    cv.poly([(hx1, ht - 4), (hx1 + 10, ht - 4), (hx1 + 14, hb + 4), (hx1, hb)], TRED, lambda x, y: 2.6 + (y - ht) * 0.01)
    cv.line(hx1 + 6, ht - 4, hx1 - 8, ht - 26, ENG, 2.6)                      # la columna del volant
    for k in range(-9, 10):
        cv.put(hx1 - 8 + k, ht - 26 - k * 0.35, ENG, 3.0 + (k > 0) * 0.6)
        cv.put(hx1 - 8 + k, ht - 25 - k * 0.35, ENG, 1.8)
    sx = rx - 8
    cv.line(sx, ht + 6, sx - 4, ht - 12, ENG, 2.4)                            # el seient de ferro, de forats
    cv.poly([(sx - 14, ht - 14), (sx + 6, ht - 14), (sx + 4, ht - 10), (sx - 12, ht - 10)], ENG,
            lambda x, y: 3.2 - (1.6 if (x % 3 == 0 and y == ht - 12) else 0))
    cv.poly([(sx + 4, ht - 30), (sx + 8, ht - 30), (sx + 6, ht - 12), (sx + 2, ht - 12)], ENG, 2.8)
    # la roda grossa, amb el guardafang
    _wheel(cv, rx, ry, rr)
    for a in range(180, 361):
        ar = math.radians(a)
        for k in range(5):
            cv.put(rx + math.cos(ar) * (rr + 3 + k * 0.6), ry + math.sin(ar) * (rr + 3 + k * 0.6) + (0 if a > 200 else 0), *paint(rx + math.cos(ar) * rr, ry + math.sin(ar) * rr, 3.6 - k * 0.3 + (1.0 if k == 4 else 0)))
    _wheel(cv, fx, fy, fr)
    # el ganxo de darrere i el número
    cv.rect(rx + rr - 2, ry + 4, rx + rr + 8, ry + 8, ENG, 2.6)
    text(cv, 'BRAU 40', hx0 + 44, ht + 4, TRED, 1.0, lit=0, flat=(230, 210, 170))


def workbench(cv):
    """El banc de treball de la dreta, amb un cargol de banc i les eines penjades a la paret."""
    x0, x1, top = 576, 640, 178
    cv.rect(x0, top, x1, top + 5, WOOD, lambda x, y: 4.4 - (y - top) * 0.4)
    cv.rect(x0, top + 6, x1, top + 6, BLACKT, 1.0)
    for lx in (x0 + 4, x1 - 6):
        cv.rect(lx, top + 6, lx + 4, FLOOR_Y + 8, WOOD, lambda x, y: 3.0 + (x - lx) * 0.2)
    cv.rect(x0 + 4, FLOOR_Y - 6, x1, FLOOR_Y - 4, WOOD, 2.4)
    shadow(cv, (x0 + x1) // 2, FLOOR_Y + 9, 34, 3, 0.6)
    # eines penjades: una serra, un martell, unes estenalles
    cv.poly([(584, 96), (612, 96), (612, 104), (590, 108)], IRONR, lambda x, y: 4.0 - (y - 96) * 0.2)
    cv.rect(612, 94, 620, 104, WOOD, 3.6)
    for x in range(590, 612, 2):
        cv.put(x, 107 - (x - 590) * 0.18, IRONR, 2.0)
    cv.rect(626, 90, 628, 120, WOOD, 3.8)
    cv.rect(622, 88, 632, 93, IRONR, 3.4)
    cv.line(590, 120, 596, 140, IRONR, 3.4)
    cv.line(598, 120, 594, 140, IRONR, 3.0)
    for (nx, ny) in ((598, 94), (627, 86), (594, 118)):
        cv.put(nx, ny, IRONR, 4.6)


def caixa_eines(cv):
    """La caixa d'eines: una caixa de ferro vermella amb nansa, damunt del banc, amb un tornavís que en surt."""
    x0, x1, y0, y1 = 588, 626, 162, 177
    cv.rect(x0, y0, x1, y1, TRED, lambda x, y: 3.6 - (y - y0) * 0.06 + (x - x0) * 0.01 + (0.8 if y == y0 else 0))
    outline(cv, x0, y0, x1, y1, TRED[0])
    cv.rect(x0, y0 + 5, x1, y0 + 5, TRED, 1.6)                               # la tapa
    cv.rect(x0 + 16, y0 + 7, x0 + 22, y0 + 9, IRONR, 4.0)                    # el tancament
    cv.line(x0 + 10, y0 - 1, x0 + 12, y0 - 6, IRONR, 3.0)                    # la nansa
    cv.line(x0 + 12, y0 - 6, x1 - 12, y0 - 6, IRONR, 3.6)
    cv.line(x1 - 12, y0 - 6, x1 - 10, y0 - 1, IRONR, 3.0)
    cv.line(x1 - 6, y0, x1 + 2, y0 - 10, WARN, 3.6)                          # un tornavís que en surt
    cv.line(x1 + 2, y0 - 10, x1 + 6, y0 - 15, IRONR, 4.4)
    for k in range(6):                                                       # el rovell de les cantonades
        cv.put(x0 + 1 + k, y1 - 1, RUSTT, 3.0)
    cv.darken(x0 - 2, y1 + 1, x1 + 2, y1 + 1, 0.6)


def clutter(cv):
    """Bales de palla, una forca, una lluerna d'oli, cordes."""
    # dues bales de palla al racó, entre la porta i el tractor
    for bx, by, w, h in ((306, FLOOR_Y + 8, 46, 22), (316, FLOOR_Y - 14, 34, 20)):
        cv.rect(bx, by - h, bx + w, by, STRAW, lambda x, y: 3.0 + (fbm(x / 3, y / 2, 5) - 0.5) * 1.6 -
                (y - by + h) * 0.02 + (x - bx) * 0.01)
        cv.rect(bx, by - h, bx + w, by - h, STRAW, 4.4)
        for k in (w // 3, 2 * w // 3):
            cv.rect(bx + k, by - h, bx + k, by, IRONR, 1.6)
        for i in range(10):
            sx = bx + hr(i, bx) * w
            cv.line(sx, by - h, sx + (hr(i, 9) - 0.5) * 6, by - h - 3, STRAW, 4.6)
    shadow(cv, 330, FLOOR_Y + 9, 28, 3, 0.7)
    # la forca, recolzada
    cv.line(366, FLOOR_Y + 2, 352, 120, WOOD, 4.0)
    cv.line(367, FLOOR_Y + 2, 353, 120, WOOD, 2.6)
    for k in (-3, 0, 3):
        cv.line(352 + k, 120, 351 + k * 1.3, 104, IRONR, 3.6)
    cv.line(349, 120, 356, 120, IRONR, 3.0)
    # la lluerna d'oli, penjada de la biga
    lx = 448
    cv.rect(lx, 22, lx, 44, IRONR, 2.0)
    cv.rect(lx - 4, 44, lx + 4, 46, IRONR, 3.0)
    cv.rect(lx - 3, 47, lx + 3, 56, [(60, 50, 30), (120, 104, 60), (190, 170, 110), (230, 214, 160)], 1.6)
    cv.rect(lx - 4, 57, lx + 4, 58, IRONR, 3.0)
    # un rotllo de corda penjat
    for r in (7, 6, 5):
        cv.ring(372, 78, r, STRAW, 2.6 + (7 - r) * 0.4, step=5)
    cv.rect(371, 68, 373, 70, IRONR, 3.0)
    # el clau del reg (el reg és un prop)
    cv.rect(331, 96, 333, 98, IRONR, 4.4)
    cv.put(331, 99, BLACKT, 1.0)


def rays_paint(cv):
    """Els raigs de sol que travessen la pols, i les taques que fan a terra."""
    for X, Y, x, y in cv.pixels(0, 14, W - 1, RH - 1):                      # (píxel a píxel, a la resolució real)
        b = rays(x, y)
        if b > 0:
            k = (0.16 if y < FLOOR_Y else 0.36) * b
            if k > B4[Y & 3][X & 3] * 0.3:
                cv.P[X, Y] = mix(cv.P[X, Y], SUN, k * 0.9 + 0.04) + (255,)


# ─── Composició ─────────────────────────────────────────────────────────────

def bg(cv):
    walls(cv)
    floor(cv)
    doorway(cv)
    seeds(cv)
    clutter(cv)
    workbench(cv)
    caixa_eines(cv)
    tractor(cv)
    rays_paint(cv)
    for y in range(RH, H):
        for x in range(W):
            cv.flat(x, y, (0, 0, 0))


# ─── Props ──────────────────────────────────────────────────────────────────

def reg(cv):
    """El reg gota a gota del pare: un rotllo de tub negre penjat del clau, i una bossa de goters."""
    cx, cy = 332, 118
    for r in range(18, 9, -1):
        for a in range(0, 360, 2):
            ar = math.radians(a)
            x, y = cx + math.cos(ar) * r, cy + math.sin(ar) * r * 0.86 + (r - 14) * 0.3
            lvl = 1.4 + (1.6 if math.sin(ar) < -0.3 and r % 2 else 0) + (0.8 if r % 3 == 0 else 0)
            cv.put(x, y, BLACKT, lvl)
    cv.line(cx - 1, 98, cx - 6, cy - 16, BLACKT, 2.4)                         # el tub del clau
    cv.line(cx + 1, 98, cx + 6, cy - 16, BLACKT, 2.4)
    for k in range(5):                                                       # els goters, de colors
        cv.put(cx - 12 + k * 6, cy + 14 - abs(k - 2), [(120, 30, 20), (200, 60, 40), (250, 120, 80)], 1.6, lit=0.5)
    cv.line(cx + 14, cy + 6, cx + 20, cy + 26, BLACKT, 2.0)                   # la punta que penja
    cv.rect(cx + 18, cy + 26, cx + 22, cy + 28, BLACKT, 2.6)
    # la bossa de goters, penjada al costat
    cv.poly([(cx - 22, cy - 4), (cx - 14, cy - 4), (cx - 13, cy + 10), (cx - 23, cy + 10)], CLOTH,
            lambda x, y: 3.0 + (x - cx + 22) * 0.1)
    cv.line(cx - 18, cy - 4, cx - 2, 98, IRONR, 2.0)


def tractor_obert(cv):
    """El capó del tractor aixecat (frontissa a dalt, a la banda del seient) i, a sota, el motor: el bloc, els
    tubs, la bomba d'injecció... i el forat on hi havia l'injector."""
    rx = RW[0]
    fx = FW[0]
    hx0, hx1, ht, hb = fx - 22, rx - 34, 150, 192
    # el motor, descobert
    cv.rect(hx0 + 2, ht + 2, hx1 - 2, hb - 6, BLACKT, 1.0)
    cv.rect(hx0 + 8, ht + 10, hx1 - 10, hb - 8, ENG, lambda x, y: 2.8 + (x - hx0) * 0.008 - (1.2 if (x - hx0) % 12 == 0 else 0) +
            (0.8 if y == ht + 10 else 0))                                     # el bloc
    for k in range(4):                                                       # les culates, amb els injectors
        ix = hx0 + 18 + k * 16
        cv.rect(ix, ht + 4, ix + 10, ht + 10, ENG, lambda x, y: 3.6 - (y - ht - 4) * 0.2)
        if k == 2:
            cv.disc(ix + 5, ht + 4, 2, 1.5, BLACKT, 0.4)                      # el forat de l'injector que falta
            cv.put(ix + 5, ht + 7, RUSTT, 3.0)
        else:
            cv.rect(ix + 4, ht - 2, ix + 6, ht + 4, ENG, lambda x, y: 4.4 + (x - ix - 4) * 0.4)
            cv.put(ix + 5, ht - 3, [(70, 60, 30), (150, 140, 80), (230, 220, 150)], 2.0)
    cv.line(hx0 + 23, ht - 2, hx0 + 23, ht - 6, ENG, 3.0)                     # els tubs de gasoil
    cv.line(hx0 + 23, ht - 6, hx1 - 6, ht - 6, ENG, 3.4)
    cv.line(hx0 + 39, ht - 2, hx0 + 39, ht - 6, ENG, 3.0)
    cv.line(hx0 + 71, ht - 2, hx0 + 71, ht - 6, ENG, 3.0)
    cv.rect(hx0 + 50, ht - 7, hx0 + 60, ht - 5, ENG, 1.4)                    # el tub tallat, sense res
    cv.disc(hx0 + 14, ht + 26, 6, 6, ENG, lambda nx, ny: 3.4 - nx - ny)       # el ventilador
    # el costat del capó, aixecat com una ala (la frontissa és a dalt): la planxa vermella, vista per dins
    pts = [(hx0 + 8, ht - 3), (hx1 - 2, ht - 3), (hx1 - 6, ht - 30), (hx0 + 18, ht - 38)]
    cv.poly(pts, TRED, lambda x, y: 1.8 + (y - ht + 38) * 0.04 + (fbm(x / 8, y / 8, 12) - 0.5) * 0.6)
    cv.line(hx0 + 18, ht - 38, hx1 - 6, ht - 30, TRED, 5.0)                   # la vora, al sol
    cv.line(hx0 + 18, ht - 37, hx1 - 6, ht - 29, TRED, 3.6)
    cv.line(hx0 + 8, ht - 3, hx0 + 18, ht - 38, TRED, 3.0)
    for k in range(4):                                                       # els reforços de dins
        bx = hx0 + 24 + k * 16
        cv.line(bx, ht - 6, bx + 3, ht - 33 + k * 1.6, TRED, 1.2)
    for k in range(5):                                                       # les reixetes, des de dins
        gx = hx0 + 40 + k * 6
        cv.rect(gx, ht - 26 + k, gx + 2, ht - 14 + k, BLACKT, 1.4)
    cv.line(hx1 - 26, ht - 4, hx1 - 24, ht - 31, ENG, 3.0)                    # la vareta que l'aguanta
    cv.darken(hx0 + 4, ht - 2, hx1, ht + 6, 0.5)                              # l'ombra del capó sobre el motor


def sacs_tres(cv):
    """Tres sacs de llavors a terra, davant dels prestatges, a punt per carregar."""
    for k, (cx, w, h) in enumerate(((44, 26, 30), (76, 28, 33), (110, 26, 29))):
        base = FLOOR_Y + 14 - (k % 2) * 3
        shadow(cv, cx - 4, base + 1, w // 2 + 4, 3, 0.7)
        _sack(cv, cx, base, w, h, k + 3, lvl=3.6)


def sac_quart(cv):
    """El quart sac, apartat dels altres («que es quedi a casa seva»)."""
    cx, base = 158, FLOOR_Y + 12
    shadow(cv, cx - 4, base + 1, 16, 3, 0.7)
    _sack(cv, cx, base, 26, 30, 1, lvl=3.8)


PROPS = {'reg': reg, 'tractor_obert': tractor_obert, 'sacs_tres': sacs_tres, 'sac_quart': sac_quart}


# ─── Animacions ─────────────────────────────────────────────────────────────

_BASE = []


def _base():
    if not _BASE:
        cv = Canvas(light=LIGHT)
        bg(cv)
        _BASE.append(cv.img)
    return _BASE[0]


def _frames_pols():
    def where(x, y):
        door = 0.0
        x0, y0, x1, y1 = DOOR
        if y > FLOOR_Y - 60 and y < RH - 6:                                  # la pols que aixeca el sol del portal
            t = max(0.0, (y - FLOOR_Y + 60) / 90)
            if x0 - 30 * t < x < x1 - 10:
                door = 0.5
        return max(rays(x, y), door if y > FLOOR_Y else 0.0)
    return motes_frames(_base(), where, n=48, count=70, seed=5)


ANIMS = {'pols': {'frames': _frames_pols, 'frameDuration': 140}}


# ─── Geometria (coordenades de 640×360) ─────────────────────────────────────

GEOMETRIA = {
    'things': {
        'porta': {'rect': (190, 64, 304, 206), 'walk': (248, 232)},
        'tractor': {'rect': (380, 100, 572, 232), 'walk': (470, 244)},
        'llavors': {'rect': (12, 30, 178, 196), 'walk': (100, 236)},
        'reg': {'rect': (306, 94, 358, 148), 'walk': (330, 234)},
        'caixa_eines': {'rect': (584, 146, 636, 178), 'walk': (604, 240)},
    },
    'spawns': {'iri': (160, 248), 'vet': (300, 252)},
    'walkable': [(8, 228), (374, 228), (384, 238), (566, 238), (578, 230), (632, 230), (638, 258), (2, 258)],
}
