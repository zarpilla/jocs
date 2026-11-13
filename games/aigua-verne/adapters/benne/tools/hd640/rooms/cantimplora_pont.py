"""
Aigua Verne — el pont de la Cantimplora (sala de prop, P: persones de ≈100 px).

La cabina de comandament d'una nau cisterna vella: planxa verd oliva amb reblons i rovell, franges taronja de
seguretat, dues bombetes de filament amb reixa. D'esquerra a dreta:
  - l'escala que baixa a la bodega (una porta sense fulla, amb els graons que s'enfonsen cap a la llum de baix);
  - la ràdio a la paret, amb el dial ambre i l'auricular penjat;
  - el finestral de quatre vidres i, a sota, la consola amb rellotges, interruptors, la pantalleta del radar i
    les dues palanques de potència; davant, els dos seients gastats (el de la dreta, el de la Capitana, amb un
    pegat de cinta americana i la placa de llautó);
  - la pantalla gran (apagada) i, a sota, el mapa de navegació: una taula de vidre amb el sistema de Vesper.

PROPS (decorats): `vista_terra2`, `vista_aqua`, `vista_ferrum`, `vista_verdant` (el que es veu pel finestral a cada
port) i `pantalla_verne` (la cara del Magnat a la pantalla, amb la claror blanca que fa a la paret).
ANIMS: `mapa_llums` (els planetes del mapa que fan pampallugues i l'estrella que batega), `consola_llums` (els
llums de la consola i l'escombrada del radar).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from hd.pix import Canvas, Light, W, H, hr, mix, GOLD, RUST
from hd.rooms.comu import _diff, text, text_width
from hd.rooms.exterior import fbm
from hd640.rooms.nau_comu import (OLIVE, SAFETY, STEELN, LEATHER, TAPE, AMBER, GLASSD, REDK, GREENK, WBLUE,
                                  BLACKT, PAPERN, INK, WARM, box, outline, rivet, vpipe, hpipe, hazard, stencil,
                                  plate_wall, deck, bulb, drop, vista, glass_reflex, cara_verne, _Clip)

FLOOR_Y = 200                          # on la paret es troba amb el terra
BOTTOM = 259                           # la sala acaba aquí (a sota, la barra de verbs)
WIN = (150, 26, 490, 122)              # el finestral (el marc de fora)
PANES = ((157, 233), (239, 315), (321, 397), (403, 483))
PANE_Y = (33, 115)
HOR = 92                               # l'horitzó que es veu pel finestral
LAMPS = ((232, 30), (414, 30))
DOOR = (12, 74, 78, FLOOR_Y)           # l'escala (la porta)
RADIO = (86, 98, 144, 146)
SCREEN = (506, 26, 630, 118)           # la pantalla gran (marc)
SCREEN_IN = (513, 33, 623, 111)
MAP = (566, 171)                       # el centre del vidre del mapa
SEATS = (240, 404)                     # el centre dels dos seients

_ANIM = {'mapa': None, 'consola': None}

LIGHT = Light(ambient=0.15, vignette=(70, 26), floor_fade=(232, 46))
for _x, _y in LAMPS:
    LIGHT.point(_x, _y + 4, r=240, k=1.8, squash=1.1, down=True, power=1.5)
LIGHT.point(320, 74, r=250, k=0.9, squash=1.3, power=1.3)           # la claror del finestral
LIGHT.point(45, 196, r=70, k=0.6, power=1.8)                        # la llum que puja de la bodega
LIGHT.point(MAP[0], MAP[1], r=80, k=0.8, power=1.7)                 # el vidre del mapa
LIGHT.point(RADIO[0] + 30, RADIO[1] + 14, r=40, k=0.4, power=1.8)   # el dial de la ràdio


# ─── Paret, sostre i terra ──────────────────────────────────────────────────

def walls(cv):
    plate_wall(cv, 0, 0, W - 1, FLOOR_Y - 1, lvl=3.2, pw=80, ph=50, seed=11, rust=0.5)
    # el sostre: planxa més fosca, el tub gros i la safata de cables
    cv.rect(0, 0, W - 1, 19, OLIVE, lambda x, y: 1.8 + (fbm_(x, y) - 0.5) * 0.6)
    for x in range(0, W, 40):
        cv.vline(x, 0, 19, OLIVE, 0.8)
    hpipe(cv, 0, W - 1, 8, 4, STEELN, 3.0, bands=tuple(range(60, W, 160)), band_ramp=SAFETY)
    cv.hline(0, W - 1, 15, BLACKT, 1.4)
    for x in range(0, W, 7):                                       # els cables de la safata
        cv.put(x, 16, BLACKT, 2.6)
        cv.put(x + 3, 17, REDK, 1.6)
    cv.hline(0, W - 1, 19, OLIVE, 4.6)
    cv.hline(0, W - 1, 20, OLIVE, 1.0)
    # les quadernes (costelles) pintades, amb el sòcol taronja de seguretat
    for x in (4, 146, 494, 634):
        cv.rect(x - 2, 21, x + 3, FLOOR_Y - 1, OLIVE, lambda xx, yy: 4.4 - abs(xx - x - 0.5) * 0.5)
        cv.vline(x - 3, 21, FLOOR_Y - 1, OLIVE, 1.0)
    cv.rect(0, FLOOR_Y - 9, W - 1, FLOOR_Y - 1, OLIVE, 2.4)
    hazard(cv, 0, FLOOR_Y - 8, W - 1, FLOOR_Y - 2, lvl=3.0, step=5)
    cv.hline(0, W - 1, FLOOR_Y - 9, OLIVE, 4.8)


def fbm_(x, y):
    return fbm(x / 30, y / 6, 13)


def floor(cv):
    deck(cv, 0, FLOOR_Y, W - 1, BOTTOM, lvl=3.0, seed=14)
    # la claror del finestral, reflectida al terra entre els seients
    cv.tint(150, FLOOR_Y + 1, 490, BOTTOM, (200, 190, 150),
            lambda x, y: 0.10 * max(0.0, 1 - abs(x - 320) / 170) * max(0.0, 1 - (y - FLOOR_Y) / 50))


# ─── L'escala que baixa a la bodega ─────────────────────────────────────────

def escala(cv):
    x0, y0, x1, y1 = DOOR
    cx = (x0 + x1) // 2
    # dins: el pou de l'escala, fosc a dalt i amb la llum càlida de la bodega a baix
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            t = (y - y0) / (y1 - y0)
            cv.put(x, y, OLIVE, 0.4 + t * 1.6, lit=0.4)
    vy = 162                                                       # on convergeixen els graons
    k = 0
    y = float(y1)
    gap = 9.0
    while y > vy + 1 and k < 12:
        yy = int(y)
        w = (x1 - x0 - 10) * (0.55 + 0.45 * (yy - vy) / (y1 - vy))
        a, b = int(cx - w / 2), int(cx + w / 2)
        warm = 1 - (yy - vy) / (y1 - vy)
        cv.hline(a, b, yy, STEELN, 4.0 + warm * 1.5, lit=0.5)       # el cantell del graó
        cv.hline(a, b, yy + 1, STEELN, 2.0 + warm, lit=0.3)
        for xx in range(a, b + 1, 3):
            cv.put(xx, yy, SAFETY, 3.4, lit=0.4)                     # el cantell pintat
        y -= gap
        gap *= 0.72
        k += 1
    cv.glow(cx, vy + 4, 26, (255, 190, 110), 0.55)                  # la llum de la bodega, al fons
    # les baranes: dos tubs que baixen cap al fons
    for side in (-1, 1):
        xa = cx + side * (x1 - x0) // 2 - side * 4
        xb = cx + side * 10
        cv.line(xa, y0 + 30, xb, vy - 6, STEELN, 4.4)
        cv.line(xa, y0 + 31, xb, vy - 5, STEELN, 2.0)
        cv.vline(xa, y0 + 30, y1, STEELN, 3.0)
    # el marc: planxa gruixuda amb els cantons de dalt rodons i les franges de perill als brancals
    for y in range(y0 - 7, y1 + 1):
        for x in range(x0 - 7, x1 + 8):
            inside = x0 <= x <= x1 and y >= y0
            r = 8
            dx = max(x0 + r - x, 0, x - (x1 - r))
            dy = max(y0 + r - y, 0)
            if inside and dx * dx + dy * dy <= r * r:
                continue
            ox = max(x0 - 7 + 12 - x, 0, x - (x1 + 7 - 12))
            oy = max(y0 - 7 + 12 - y, 0)
            if ox * ox + oy * oy > 144:
                continue
            edge = min(abs(x - (x0 - 7)), abs(x - (x1 + 7)), abs(y - (y0 - 7)))
            cv.put(x, y, OLIVE, 4.0 + (1.0 if edge == 0 else 0) - (1.2 if not inside and (
                abs(x - x0) <= 1 or abs(x - x1) <= 1 or abs(y - y0) <= 1) else 0))
    hazard(cv, x0 - 6, y0 + 40, x0 - 2, y1 - 9, lvl=3.4, step=4)
    hazard(cv, x1 + 2, y0 + 40, x1 + 6, y1 - 9, lvl=3.0, step=4)
    for y in range(y0 + 2, y1 - 8, 12):
        rivet(cv, x0 - 5, y, OLIVE, 4.0)
        rivet(cv, x1 + 4, y, OLIVE, 3.6)
    # el rètol, a dalt: «BODEGA» i una fletxa avall
    w = text_width('BODEGA')
    lx = cx - (w + 8) // 2
    box(cv, lx - 3, y0 - 19, lx + w + 9, y0 - 10, SAFETY, 3.6)
    text(cv, 'BODEGA', lx, y0 - 17, None, 0, flat=INK)
    ax = lx + w + 4
    for j, ww in enumerate((2, 2, 2, 2, 0)):
        cv.flat(ax, y0 - 17 + j, INK)
    cv.hline(ax - 2, ax + 2, y0 - 14, [INK], 0, lit=0)
    cv.hline(ax - 1, ax + 1, y0 - 13, [INK], 0, lit=0)
    # el llindar
    cv.rect(x0 - 7, y1 - 1, x1 + 7, y1 + 2, STEELN, 4.2)
    cv.hline(x0 - 7, x1 + 7, y1 - 1, STEELN, 5.6)


# ─── La ràdio ──────────────────────────────────────────────────────────────

def radio(cv, lights=0):
    x0, y0, x1, y1 = RADIO
    # el cable de l'antena, que puja al sostre
    for y in range(20, y0):
        cv.put(x0 + 8, y, BLACKT, 2.0)
        cv.put(x0 + 9, y, BLACKT, 1.0)
    # la caixa: gris verdós, amb la vora arrodonida i les potes de fixar-la a la paret
    cv.rect(x0 - 3, y1 + 1, x1 + 3, y1 + 4, STEELN, 3.6)
    cv.hline(x0 - 3, x1 + 3, y1 + 1, STEELN, 5.0)
    for bx in (x0 + 2, x1 - 4):
        cv.rect(bx, y1 + 5, bx + 2, y1 + 12, STEELN, 2.6)
        cv.line(bx + 1, y1 + 12, bx + 1 + (6 if bx < x0 + 10 else -6), y1 + 5, STEELN, 2.4)
    box(cv, x0, y0, x1, y1, STEELN, 3.4, grad=0.6)
    outline(cv, x0 - 1, y0 - 1, x1 + 1, y1 + 1, INK)
    # el dial, ambre, amb l'agulla i l'escala
    dx0, dy0, dx1, dy1 = x0 + 4, y0 + 5, x1 - 4, y0 + 17
    cv.rect(dx0, dy0, dx1, dy1, AMBER, lambda x, y: 4.2 - abs(y - (dy0 + dy1) / 2) * 0.25, lit=0.3)
    outline(cv, dx0 - 1, dy0 - 1, dx1 + 1, dy1 + 1, INK)
    for x in range(dx0 + 2, dx1 - 1, 3):
        cv.flat(x, dy0 + 2, AMBER[1])
        if (x - dx0) % 9 == 2:
            cv.flat(x, dy0 + 3, AMBER[1])
    text(cv, '7', dx0 + 3, dy0 + 6, None, 0, flat=AMBER[1])
    text(cv, '12', dx1 - 9, dy0 + 6, None, 0, flat=AMBER[1])
    nx = dx0 + 26
    cv.vline(nx, dy0 + 1, dy1 - 1, REDK, 3.6, lit=0)
    cv.glow((dx0 + dx1) // 2, (dy0 + dy1) // 2, 26, (255, 180, 80), 0.25)
    # els dos poms i l'interruptor
    for kx in (x0 + 11, x0 + 27):
        cv.disc(kx, y0 + 30, 5, 5, BLACKT, lambda a, b: 3.4 - a * 0.8 - b * 1.0)
        cv.flat(kx - 1, y0 + 26, STEELN[8])
    cv.rect(x0 + 37, y0 + 26, x0 + 39, y0 + 33, STEELN, 2.2)
    cv.rect(x0 + 37, y0 + 25, x0 + 39, y0 + 27, STEELN, 6.0)
    on = lights % 4 != 3
    cv.flat(x0 + 44, y0 + 28, (120, 255, 120) if on else (30, 80, 30))
    cv.flat(x0 + 45, y0 + 28, (80, 200, 90) if on else (30, 70, 30))
    # l'altaveu: una reixa de forats
    for y in range(y0 + 38, y1 - 2, 2):
        for x in range(x0 + 4, x1 - 30, 2):
            cv.put(x, y, STEELN, 1.0)
    text(cv, 'RADIO', x1 - 27, y1 - 8, None, 0, flat=STEELN[7])
    # l'auricular, penjat del ganxo a la dreta, amb el cable en espiral
    hx = x1 + 3
    cv.rect(hx, y0 + 10, hx + 2, y0 + 12, STEELN, 4.0)
    cv.rect(hx + 1, y0 + 12, hx + 5, y0 + 36, BLACKT, lambda x, y: 3.2 - (x - hx) * 0.3)
    cv.rect(hx, y0 + 12, hx + 6, y0 + 17, BLACKT, 3.6)
    cv.rect(hx, y0 + 31, hx + 6, y0 + 36, BLACKT, 3.0)
    for j in range(20):
        cv.put(hx + 3 + (1 if j % 3 else -1), y0 + 37 + j, BLACKT, 2.6 + (j % 2))
    for j in range(8):
        cv.put(x1 - 2 - j, y1 + 2 + int(4 * math.sin(j / 2)), BLACKT, 2.0)
    # el quadern de bitàcola damunt la lleixa
    cv.rect(x0 + 2, y1 - 1, x0 + 22, y1, [(40, 24, 18), (90, 50, 30), (130, 76, 44)], 1.6)


# ─── Coses de la paret ─────────────────────────────────────────────────────

def paret_detalls(cv):
    # el rellotge de bord, rodó, amb el marc de llautó
    cx, cy = 116, 62
    cv.disc(cx, cy, 13, 13, GOLD, lambda a, b: 4.0 - a * 0.8 - b * 0.8)
    cv.disc(cx, cy, 10, 10, PAPERN, lambda a, b: 4.6 - b * 0.4)
    for h in range(12):
        a = h * math.pi / 6
        cv.flat(cx + round(math.sin(a) * 8), cy - round(math.cos(a) * 8), INK)
    cv.line(cx, cy, cx + 4, cy - 3, [INK], 0, lit=0)
    cv.line(cx, cy, cx - 1, cy - 7, [INK], 0, lit=0)
    cv.flat(cx, cy, REDK[3])
    # una postal de Terra-2 enganxada amb cinta, i la fotografia de la nau quan era nova
    for (px, py, w, h, inside) in ((30, 20, 0, 0, None), (86, 30, 18, 13, 'post'), (498, 128, 14, 18, 'foto')):
        if not inside:
            continue
        cv.rect(px, py, px + w, py + h, PAPERN, 4.4)
        outline(cv, px - 1, py - 1, px + w + 1, py + h + 1, INK)
        if inside == 'post':
            cv.rect(px + 2, py + 2, px + w - 2, py + 7, [(190, 160, 110), (220, 196, 150)], 0.8, lit=0)
            cv.rect(px + 2, py + 8, px + w - 2, py + h - 2, [(150, 110, 70), (180, 140, 90)], 0.8, lit=0)
            cv.vline(px + 12, py + 3, py + 8, [(240, 240, 236)], 0, lit=0)
        else:
            cv.rect(px + 2, py + 2, px + w - 2, py + h - 5, [(90, 110, 130), (130, 150, 170)], 0.8, lit=0)
            cv.rect(px + 4, py + 7, px + w - 4, py + 10, OLIVE, 6.0, lit=0)
            cv.rect(px + 7, py + 10, px + 10, py + 12, SAFETY, 4.0, lit=0)
        cv.rect(px + w // 2 - 3, py - 2, px + w // 2 + 3, py + 1, TAPE, 4.0)
    # l'extintor, vermell, sota la ràdio
    ex = 96
    cv.rect(ex - 5, 164, ex + 5, 189, REDK, lambda x, y: 3.8 - (x - ex) * 0.25 - abs(x - ex) * 0.1)
    cv.disc(ex, 164, 5, 3, REDK, lambda a, b: 4.2 - a)
    cv.rect(ex - 2, 157, ex + 2, 161, BLACKT, 2.4)
    cv.line(ex + 2, 158, ex + 8, 166, BLACKT, 1.8)
    cv.rect(ex - 4, 172, ex + 4, 178, PAPERN, 4.4)
    text(cv, 'CO2', ex - 5, 173, None, 0, flat=INK)
    outline(cv, ex - 6, 162, ex + 6, 190, INK)
    cv.rect(ex - 7, 176, ex + 7, 177, STEELN, 3.0)


# ─── Finestral ─────────────────────────────────────────────────────────────

def finestral(cv):
    x0, y0, x1, y1 = WIN
    # el marc: planxa gruixuda amb cantons tallats
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            c = min(x - x0, x1 - x) + min(y - y0, y1 - y)
            if c < 6:
                continue
            cv.put(x, y, OLIVE, 4.2 - (y - y0) / (y1 - y0) * 0.6 + (0.6 if y == y0 + 1 else 0))
    cv.hline(x0 + 6, x1 - 6, y0, OLIVE, 1.0)
    cv.hline(x0 + 4, x1 - 4, y1, OLIVE, 1.0)
    # els vidres (aquí, la nit de l'hangar: els decorats `vista_*` hi posen el planeta)
    vistes_pane(None)(cv)
    for a, b in PANES:
        cv.hline(a - 1, b + 1, PANE_Y[0] - 1, OLIVE, 0.6)            # la goma del vidre
        cv.vline(a - 1, PANE_Y[0], PANE_Y[1], OLIVE, 1.0)
        cv.hline(a - 1, b + 1, PANE_Y[1] + 1, OLIVE, 5.4)
        cv.vline(b + 1, PANE_Y[0], PANE_Y[1], OLIVE, 4.8)
    # els muntants, amb reblons
    for a, b in zip([p[1] for p in PANES[:-1]], [p[0] for p in PANES[1:]]):
        for y in range(PANE_Y[0], PANE_Y[1] + 1, 7):
            rivet(cv, (a + b) // 2 - 1, y + 2, OLIVE, 4.2)
    for y in range(y0 + 3, y1 - 2, 9):
        rivet(cv, x0 + 3, y, OLIVE, 4.0)
        rivet(cv, x1 - 4, y, OLIVE, 3.6)
    # els eixugaparabrises, aturats
    for a, b in PANES[1:3]:
        cx = (a + b) // 2
        cv.line(cx - 22, PANE_Y[1] - 1, cx + 8, PANE_Y[1] - 30, BLACKT, 1.6)
        cv.rect(cx - 24, PANE_Y[1] - 1, cx - 21, PANE_Y[1] + 1, STEELN, 3.0)


def vistes_pane(planeta):
    """El paisatge de fora, sencer darrere els quatre vidres (es dibuixa d'una tirada i se'n copien els vidres)."""
    def fn(cv):
        tmp = Canvas(light=LIGHT)
        vista(tmp, planeta, (PANES[0][0], PANE_Y[0], PANES[-1][1], PANE_Y[1]), HOR, s=1.0, refl=False)
        src = tmp.img.load()
        for a, b in PANES:
            for y in range(PANE_Y[0], PANE_Y[1] + 1):
                for x in range(a, b + 1):
                    cv.P[x, y] = src[x, y]
            glass_reflex(cv, (a, PANE_Y[0], b, PANE_Y[1]))
    return fn


# ─── La consola ────────────────────────────────────────────────────────────

CON = (138, 126, 502, 156, FLOOR_Y)      # x0, y de dalt, x1, y del cantell, y de baix


def consola(cv, lights=0):
    x0, ytop, x1, yedge, ybot = CON
    # el davant: planxa vertical, plafons amb reixetes
    box(cv, x0 - 6, yedge, x1 + 6, ybot - 10, OLIVE, 3.0, grad=1.2)
    for px0 in range(x0 + 4, x1 - 40, 60):
        box(cv, px0, yedge + 8, px0 + 50, ybot - 18, OLIVE, 2.6, grad=0.6)
        for y in range(yedge + 13, ybot - 22, 3):
            cv.hline(px0 + 6, px0 + 44, y, OLIVE, 0.8)
        for bx, by in ((px0 + 2, yedge + 10), (px0 + 48, yedge + 10), (px0 + 2, ybot - 20), (px0 + 48, ybot - 20)):
            rivet(cv, bx, by, OLIVE, 3.0)
    # la tapa inclinada, més clara (li toca la llum del finestral)
    cv.poly([(x0, ytop), (x1, ytop), (x1 + 6, yedge), (x0 - 6, yedge)], STEELN,
            lambda x, y: 3.6 + (y - ytop) / (yedge - ytop) * 0.8)
    cv.hline(x0, x1, ytop, STEELN, 5.6)
    cv.hline(x0 - 6, x1 + 6, yedge, STEELN, 6.0)
    cv.hline(x0 - 6, x1 + 6, yedge + 1, BLACKT, 1.0)
    for y in range(ytop, yedge):                                   # els cantells laterals
        t = (y - ytop) / (yedge - ytop)
        cv.put(x0 - int(6 * t), y, STEELN, 2.0)
        cv.put(x1 + int(6 * t), y, STEELN, 5.0)
    # a l'esquerra: quatre rellotges i una filera d'interruptors
    for i, gx in enumerate((154, 174, 194, 214)):
        gy = 136
        cv.disc(gx, gy, 7, 6, BLACKT, 1.0)
        cv.disc(gx, gy, 6, 5, PAPERN, lambda a, b: 4.4 - b * 0.6)
        ang = -2.4 + hr(i, 3) * 2.6
        cv.line(gx, gy, gx + math.cos(ang) * 5, gy + math.sin(ang) * 4, REDK, 3.2)
        cv.flat(gx, gy, INK)
        for a in range(-200, 30, 40):
            cv.flat(gx + math.cos(math.radians(a)) * 5, gy + math.sin(math.radians(a)) * 4, INK)
    for i in range(10):
        tx = 152 + i * 7
        cv.rect(tx, 146, tx + 3, 150, BLACKT, 1.4)
        up = hr(i, 5) > 0.4
        cv.vline(tx + 1, 143 if up else 148, 147 if up else 152, STEELN, 6.0)
    # al mig: la pantalleta del radar (ambre) i les dues palanques de potència
    rx0, ry0, rx1, ry1 = 286, 130, 346, 152
    cv.rect(rx0 - 2, ry0 - 2, rx1 + 2, ry1 + 2, BLACKT, 1.6)
    cv.rect(rx0, ry0, rx1, ry1, AMBER, lambda x, y: 0.6 + (0.5 if (y - ry0) % 2 else 0), lit=0)
    cv.glow((rx0 + rx1) // 2, (ry0 + ry1) // 2, 34, (255, 170, 60), 0.18)
    ccx, ccy = (rx0 + rx1) // 2, ry1 - 1
    for r in (8, 15, 22):
        for a in range(180, 361, 4):
            cv.flat(ccx + math.cos(math.radians(a)) * r * 1.3, ccy + math.sin(math.radians(a)) * r * 0.9, AMBER[2])
    sweep = 200 + (lights * 22) % 140
    for r in range(1, 22):
        cv.flat(ccx + math.cos(math.radians(sweep)) * r * 1.3, ccy + math.sin(math.radians(sweep)) * r * 0.9,
                AMBER[5])
    for bx, by in ((304, 138), (330, 143)):                         # dos ecos
        cv.flat(bx, by, AMBER[4])
    # les palanques: dues, amb pom vermell, i la seva guia
    for i, lx in enumerate((362, 376)):
        cv.rect(lx - 2, 140, lx + 2, 152, BLACKT, 1.2)
        top = 112 + i * 4
        cv.line(lx, 146, lx - 2, top, STEELN, 5.4)
        cv.line(lx + 1, 146, lx - 1, top, STEELN, 3.0)
        cv.disc(lx - 2, top - 2, 3.2, 3.2, REDK, lambda a, b: 4.4 - a - b)
    text(cv, 'POTENCIA', 352, 151, None, 0, flat=BLACKT[2])
    # el timó: un volant petit d'avió, al mig
    cv.rect(256, 138, 266, 150, BLACKT, 2.0)
    for a in range(0, 360, 6):
        xx, yy = 261 + math.cos(math.radians(a)) * 13, 132 + math.sin(math.radians(a)) * 4
        if a < 200 or a > 340:
            cv.put(xx, yy, BLACKT, 3.0 - math.sin(math.radians(a)))
    cv.rect(246, 131, 276, 133, BLACKT, 2.6)
    cv.rect(244, 127, 248, 137, LEATHER, 3.0)
    cv.rect(274, 127, 278, 137, LEATHER, 2.4)
    # a la dreta: una graella de botons de colors (uns quants encesos) i un tassó de cafè
    cols = (REDK, GREENK, AMBER, GREENK, WBLUE)
    for j in range(3):
        for i in range(8):
            bx, by = 394 + i * 8, 132 + j * 7
            ramp = cols[(i + j * 3) % 5]
            lit_on = hr(i, j, lights // 2 + 1) > 0.55 if lights else hr(i, j, 0) > 0.55
            cv.rect(bx, by, bx + 4, by + 3, ramp, 4.4 if lit_on else 1.6, lit=0.3)
            cv.hline(bx, bx + 4, by + 4, BLACKT, 0.6)
            if lit_on:
                cv.glow(bx + 2, by + 1, 5, ramp[4], 0.3)
    for i, sx in enumerate((462, 474, 486)):                        # tres rodetes
        cv.disc(sx, 140, 3.5, 3, BLACKT, lambda a, b: 3.0 - b)
        cv.flat(sx, 138, STEELN[7])
    # el tassó de la Capitana, abonyegat
    cv.rect(460, 118, 470, 129, [(30, 50, 70), (50, 80, 110), (80, 120, 150), (140, 170, 190)],
            lambda x, y: 2.6 - (x - 460) * 0.15)
    cv.hline(460, 470, 118, BLACKT, 1.0)
    cv.ring(472, 123, 3, [(30, 50, 70), (80, 120, 150)], 1.4, step=20)
    # el cantell de la consola, gastat on s'hi recolzen les mans
    for x in range(x0 - 6, x1 + 7):
        if hr(x // 2, 91) > 0.75:
            cv.put(x, yedge, STEELN, 7.4)
    # el sòcol, negre, amb la franja
    cv.rect(x0 - 6, ybot - 10, x1 + 6, ybot - 1, BLACKT, 1.6)


# ─── Els seients ───────────────────────────────────────────────────────────

def seient(cv, cx, capitana=False):
    """Un seient de pilot vist d'esquena: respatller de cuir gastat i capitonat, reposacaps, braços i peu de
    columna. Mira el finestral, com qui s'hi asseu."""
    top, bot = 160, 199
    # el peu: la columna i la base, cargolada al terra
    cv.disc(cx, 225, 20, 3.5, BLACKT, 1.2)
    cv.rect(cx - 3, 204, cx + 3, 222, STEELN, lambda x, y: 4.2 - (x - cx) * 0.5)
    cv.rect(cx - 14, 220, cx + 14, 223, STEELN, lambda x, y: 3.2 - (y - 220) * 0.6)
    cv.hline(cx - 14, cx + 14, 220, STEELN, 5.2)
    for bx in (cx - 11, cx + 10):
        cv.flat(bx, 221, STEELN[8])
    # el coixí, que sobresurt pels costats del respatller
    cv.rect(cx - 21, 196, cx + 21, 205, LEATHER, lambda x, y: 3.2 - (y - 196) * 0.2 - (x - cx) * 0.03)
    cv.hline(cx - 20, cx + 20, 205, [INK], 0, lit=0)
    cv.vline(cx - 22, 197, 204, [INK], 0, lit=0)
    cv.vline(cx + 22, 197, 204, [INK], 0, lit=0)
    # els braços, amb el tub de suport
    for side in (-1, 1):
        ax = cx + side * 24
        cv.rect(ax - 3, 180, ax + 3, 184, LEATHER, 3.4 - side * 0.6)
        cv.hline(ax - 3, ax + 3, 180, LEATHER, 5.0)
        outline(cv, ax - 4, 179, ax + 4, 185, INK)
        cv.rect(ax - 1, 186, ax + 1, 197, STEELN, 3.2)
    # el respatller: més ample a les espatlles, rodó a dalt, amb el capitonat
    for y in range(top, bot + 1):
        t = (y - top) / (bot - top)
        hw = 18 - 2 * t
        for x in range(int(cx - hw), int(cx + hw) + 1):
            dx = max(cx - hw + 6 - x, 0, x - (cx + hw - 6))
            dy = max(top + 6 - y, 0)
            if dx * dx + dy * dy > 36:
                continue
            u = (x - cx) / hw
            v = 3.6 - u * 1.1 - u * u * 1.6 - t * 0.4 + (hr(x // 2, y // 3, cx) - 0.5) * 0.4
            if (y - top) % 10 == 5 or abs(x - cx) == 7:
                v -= 1.1                                           # les costures del capitonat
            cv.put(x, y, LEATHER, v)
        # el contorn
        for x in (int(cx - hw) - (1 if y > top + 5 else 0), int(cx + hw) + 1):
            if y > top + 3:
                cv.flat(x, y, INK)
    for x in range(cx - 13, cx + 14):
        cv.flat(x, top - 1, INK)
    # el cuir esquerdat: taques pelades, més clares
    for k in range(6):
        px, py = cx - 13 + int(hr(k, cx, 1) * 26), top + 4 + int(hr(k, cx, 2) * 30)
        cv.put(px, py, LEATHER, 6.0)
        cv.put(px + 1, py, LEATHER, 5.2)
    # el reposacaps, amb les dues barres
    for px in (cx - 5, cx + 4):
        cv.rect(px, top - 6, px + 1, top - 1, STEELN, 4.0 if px < cx else 2.6)
    cv.rect(cx - 10, top - 16, cx + 10, top - 7, LEATHER, lambda x, y: 3.6 - (x - cx) * 0.07 - (y - top + 16) * 0.06)
    cv.hline(cx - 9, cx + 9, top - 16, LEATHER, 5.2)
    outline(cv, cx - 11, top - 17, cx + 11, top - 6, INK)
    cv.flat(cx - 11, top - 17, cv.get(cx - 12, top - 17))
    cv.flat(cx + 11, top - 17, cv.get(cx + 12, top - 17))
    if capitana:
        # un pegat de cinta americana en creu, per tapar l'esquinç
        for j in range(-8, 9):
            for w in (0, 1, 2):
                cv.put(cx - 4 + j + w, top + 18 + j, TAPE, 3.4 - abs(j) * 0.05)
                cv.put(cx - 4 - j + w, top + 18 + j, TAPE, 2.8)
        # la placa de llautó del reposacaps: «CAPITANA»
        cv.rect(cx - 7, top - 13, cx + 7, top - 10, GOLD, 4.0)
        cv.hline(cx - 7, cx + 7, top - 13, GOLD, 5.4)
        for x in range(cx - 5, cx + 6, 2):
            cv.flat(x, top - 11, GOLD[1])
        # la gorra vella, penjada al reposacaps
        cv.disc(cx + 9, top - 15, 7, 4, [(8, 10, 22), (16, 20, 40), (28, 34, 62), (44, 52, 84)],
                lambda a, b: 2.4 - a * 0.6 - b * 0.8)
        cv.rect(cx + 2, top - 13, cx + 17, top - 12, [(6, 6, 12), (14, 16, 28)], 1.0)
        cv.flat(cx + 9, top - 17, GOLD[5])
        cv.flat(cx + 10, top - 17, GOLD[4])
    else:
        # el seient de la pilot: un pedaç de cuir cosit, d'un altre color
        cv.rect(cx + 3, top + 18, cx + 11, top + 27, [(30, 20, 14), (60, 40, 26), (92, 64, 40), (124, 90, 58)],
                2.4)
        for y in range(top + 18, top + 28, 2):
            cv.flat(cx + 2, y, INK)
            cv.flat(cx + 12, y, INK)


# ─── La pantalla gran ──────────────────────────────────────────────────────

def pantalla(cv):
    x0, y0, x1, y1 = SCREEN
    # els braços que la subjecten a la paret
    for by in (y0 + 18, y1 - 18):
        cv.rect(x0 - 6, by - 2, x0, by + 2, STEELN, 3.0)
        cv.rect(x1, by - 2, x1 + 4, by + 2, STEELN, 2.4)
    box(cv, x0, y0, x1, y1, BLACKT, 2.8)
    outline(cv, x0 - 1, y0 - 1, x1 + 1, y1 + 1, INK)
    for bx, by in ((x0 + 2, y0 + 2), (x1 - 3, y0 + 2), (x0 + 2, y1 - 3), (x1 - 3, y1 - 3)):
        rivet(cv, bx, by, STEELN, 3.0)
    a0, b0, a1, b1 = SCREEN_IN
    # apagada: vidre fosc i bombat, amb el reflex de la bombeta i del finestral
    cv.rect(a0, b0, a1, b1, GLASSD, lambda x, y: 1.4 + (1 - ((x - (a0 + a1) / 2) / ((a1 - a0) / 2)) ** 2) * 0.6
            + (1 - ((y - (b0 + b1) / 2) / ((b1 - b0) / 2)) ** 2) * 0.6, lit=0.25)
    for k in range(18):
        for j in range(3):
            cv.put(a0 + 8 + k + j, b0 + 4 + k, GLASSD, 4.2 - j * 0.6, lit=0)
    cv.put(a0 + 30, b0 + 6, GLASSD, 6.0, lit=0)
    cv.hline(a0, a1, b0, BLACKT, 0.0)
    cv.vline(a0, b0, b1, BLACKT, 0.0)
    # la placa del fabricant (el préstec de Verne la va pagar) i el llum vermell d'espera
    drop(cv, x0 + 8, y1 - 2, 2, WBLUE, 3.2)
    text(cv, 'VERNE', x0 + 13, y1 - 5, None, 0, flat=STEELN[5])
    cv.flat(x1 - 6, y1 - 3, (220, 40, 30))
    cv.glow(x1 - 6, y1 - 3, 3, (255, 60, 40), 0.4)


def pantalla_verne(cv):
    """La cara del Magnat i la claror blanca que la pantalla fa a la paret i a la consola (no al finestral)."""
    base = _base()
    on = Canvas(light=LIGHT)
    on.img.paste(base)
    on.P = on.img.load()
    cara_verne(on, SCREEN_IN)
    x0, y0, x1, y1 = SCREEN
    lx0, ly0, lx1, ly1 = WIN
    on.tint(x0 - 70, 0, W - 1, FLOOR_Y + 40, (214, 228, 246),
            lambda x, y: 0.0 if (SCREEN[0] - 1 <= x <= SCREEN[2] + 1 and SCREEN[1] - 1 <= y <= SCREEN[3] + 1) or
            (lx0 <= x <= lx1 and ly0 <= y <= ly1) else
            0.22 * max(0.0, 1 - math.hypot(x - (x0 + x1) / 2, (y - (y0 + y1) / 2) * 1.2) / 110))
    cv.img.alpha_composite(_diff(on.img, base))


# ─── El mapa de navegació ──────────────────────────────────────────────────

PLANETS = (('terra2', 18, 0.6, (190, 150, 90)), ('aqua', 30, 2.3, (190, 220, 240)), ('ferrum', 42, 4.0,
           (170, 90, 60)), ('verdant', 54, 5.3, (80, 230, 80)))


def mapa(cv, frame=None):
    cx, cy = MAP
    # el peu: una columna i quatre potes
    cv.rect(cx - 50, 190, cx + 50, 196, STEELN, 2.4)
    for lx in (cx - 54, cx + 50):
        cv.rect(lx, 184, lx + 4, 222, STEELN, lambda x, y: 3.8 - (x - lx) * 0.5)
        cv.disc(lx + 2, 222, 4, 1.5, BLACKT, 1.0)
    cv.rect(cx - 8, 192, cx + 8, 216, STEELN, lambda x, y: 3.2 - (x - cx) * 0.15)
    cv.disc(cx, 218, 14, 3, STEELN, 2.4)
    # el vidre: un trapezi en perspectiva, blau fosc, amb la graella
    back, front = 160, 182
    pts = [(cx - 54, back), (cx + 54, back), (cx + 66, front), (cx - 66, front)]
    cv.poly(pts, GLASSD, lambda x, y: 2.6 + (y - back) * 0.04, lit=0.2)
    for i in range(-6, 7):                                         # la graella
        for y in range(back, front + 1):
            t = (y - back) / (front - back)
            x = cx + i * (9 + 2 * t)
            if (y % 2 == 0) and abs(x - cx) < 54 + 12 * t:
                cv.put(x, y, GLASSD, 4.0, lit=0)
    for y in range(back + 4, front, 5):
        t = (y - back) / (front - back)
        for x in range(int(cx - 54 - 12 * t) + 2, int(cx + 54 + 12 * t) - 1, 2):
            cv.put(x, y, GLASSD, 4.0, lit=0)
    # les òrbites (el·lipses aixafades) i l'estrella de Vesper
    oy = cy
    for _, r, _, _ in PLANETS:
        for a in range(0, 360, 3):
            x = cx + math.cos(math.radians(a)) * r
            y = oy + math.sin(math.radians(a)) * r * 0.2
            cv.put(x, y, WBLUE, 4.2, lit=0)
    pulse = 0 if frame is None else frame % 4
    cv.glow(cx, oy, 14 + (2 if pulse in (1, 2) else 0), (255, 170, 60), 0.6)
    cv.disc(cx, oy, 3, 2, [(200, 90, 20), (250, 160, 40), (255, 230, 150)], 1.6 + (0.6 if pulse == 2 else 0),
            lit=0)
    for i, (name, r, ang, col) in enumerate(PLANETS):
        x = cx + math.cos(ang) * r
        y = oy + math.sin(ang) * r * 0.2
        blink = frame is not None and (frame + i * 2) % 6 == 0
        cv.disc(x, y, 2.2, 1.6, [tuple(int(c * 0.5) for c in col), col, mix(col, (255, 255, 255), 0.5)],
                2.2 if blink else 1.4, lit=0)
        cv.glow(x, y, 6, col, 0.5 if blink else 0.3)
    # el palau orbital, una espurna daurada, i els tres dipòsits, tres puntets blancs
    cv.flat(cx + 36, oy - 6, (250, 220, 120))
    for k, (dx, dy) in enumerate(((-30, -4), (12, 5), (40, -2))):
        cv.flat(cx + dx, oy + dy, (230, 236, 244))
    # el reflex de la llum al vidre i la vora de llautó
    cv.line(cx - 40, back + 2, cx - 20, back + 2, GLASSD, 6.0, lit=0)
    for x0_, x1_, y in ((cx - 54, cx + 54, back - 1), (cx - 66, cx + 66, front + 1)):
        cv.hline(x0_, x1_, y, GOLD, 4.4 if y == back - 1 else 3.4)
    cv.line(cx - 55, back, cx - 67, front, GOLD, 4.6)
    cv.line(cx + 55, back, cx + 67, front, GOLD, 3.0)
    cv.rect(cx - 66, front + 2, cx + 66, front + 6, GOLD, 2.2)
    cv.hline(cx - 66, cx + 66, front + 2, GOLD, 4.0)
    cv.glow(cx, (back + front) // 2, 70, (120, 170, 255), 0.12)


# ─── Composició ────────────────────────────────────────────────────────────

def bg(cv):
    walls(cv)
    floor(cv)
    paret_detalls(cv)
    finestral(cv)
    escala(cv)
    radio(cv, _ANIM['consola'] or 0)
    pantalla(cv)
    mapa(cv, _ANIM['mapa'])
    consola(cv, _ANIM['consola'] or 0)
    for lx, ly in LAMPS:
        bulb(cv, lx, ly, cable=10)
    seient(cv, SEATS[0])
    seient(cv, SEATS[1], capitana=True)
    # la barra de verbs: negre
    cv.rect(0, BOTTOM + 1, W - 1, H - 1, [(0, 0, 0)], 0, lit=0)


@functools.lru_cache(maxsize=None)
def _base_img():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv.img


def _base():
    return _base_img().copy()


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
    'vista_terra2': vistes_pane('terra2'),
    'vista_aqua': vistes_pane('aqua'),
    'vista_ferrum': vistes_pane('ferrum'),
    'vista_verdant': vistes_pane('verdant'),
    'pantalla_verne': pantalla_verne,
}

ANIMS = {
    'mapa_llums': {'frames': lambda: _frames('mapa', 12), 'frameDuration': 240},
    'consola_llums': {'frames': lambda: _frames('consola', 8), 'frameDuration': 300},
}


def _t(x0, y0, x1, y1, wx=None, wy=236):
    return {'rect': (x0, y0, x1, y1), 'walk': (wx if wx is not None else (x0 + x1) // 2, wy)}


GEOMETRIA = {
    'things': {
        'escala': _t(DOOR[0] - 6, DOOR[1] - 20, DOOR[2] + 6, FLOOR_Y, wx=45, wy=232),
        'radio': _t(RADIO[0] - 2, RADIO[1] - 2, RADIO[2] + 4, RADIO[3] + 12, wy=234),
        'finestral': _t(WIN[0], WIN[1], WIN[2], WIN[3], wx=320, wy=234),
        'pantalla': _t(SCREEN[0], SCREEN[1], SCREEN[2], SCREEN[3], wx=556, wy=236),
        'mapa': _t(MAP[0] - 68, 156, MAP[0] + 68, 224, wx=566, wy=238),
        'seient': _t(SEATS[1] - 28, 142, SEATS[1] + 28, 226, wx=SEATS[1] + 34, wy=236),
    },
    'spawns': {'capitana': (476, 240), 'iri': (300, 248), 'vet': (172, 250)},
    'walkable': [(8, 228), (632, 228), (636, 257), (4, 257)],
}
