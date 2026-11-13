"""
El pati de la granja (Escena 1), a Terra-2, un matí de secada. Sala «de lluny» (persones de ≈83 px).

Ve de la mostra aprovada (guio/art/mostra/granja_pati.py), redibuixada amb més detall:
  - el cel de pols, sense ni un núvol, i el sol dur a dalt a la dreta; els camps secs i la carretera;
  - la **Canonada de Terra-2** a l'horitzó, i la rasa recta que hi va des del pou, tapada de pressa;
  - el panell del preu a la carretera (AIGUA VERNE ▲, sense xifres: el preu es diu en mirar-lo);
  - la masia del pare, amb els finestrons tancats, l'arrebossat caigut i un test de geranis secs;
  - l'olivera morta; la tanca; el **pou** de pedra amb la politja i la galleda seca;
  - la **bomba de Verne**, blanca i neta, amb el tub ficat al pou;
  - el graner obert, amb el morro del tractor vermell a la penombra;
  - el camí cap al port, trepitjat, que surt per la dreta, amb un pal indicador.
Props: `bomba_oberta` (el panell de la bomba obert, amb l'etiqueta). ANIMS: `pols` (la pols que passa arran de
terra) i `llum_canonada`. La mateixa escena plovent és final_pluja.py (draw(cv, wet=True)).
"""
import math

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from PIL import Image

from hd.pix import Canvas, Light, W, H, hr, mix
from hd.rooms.exterior import fbm, smooth
from hd640.rooms.terra2_comu import (
    RH, SKY, FIELD, EARTH, MUD, ADOBE, STONE, TILE, SHUT, PLANK, GREYW, WHITEP, BLUE, BLACKT, LED, LEDG, GRASS,
    SPROUT, REDT, IRONR, RUSTT, WARN, WATER, RSKY, STRAW, PAPER,
    text, text_width, gota, dust_sky, rain_sky, hills, canonada, panell_preu, cracks, shadow,
    dust_wind_frames, llum_canonada_frames, _diff)

HOR = 118
CAN_X = 402                       # la Canonada
WX, WTOP, WBASE, WRX = 300, 174, 204, 26          # el pou
BX0, BX1, BY0, BY1 = 336, 364, 172, 208           # la cara del davant de la bomba
PANEL = (412, 124)                # el panell del preu (cantó de dalt a l'esquerra)

LIGHT = Light(ambient=0.6, vignette=(70, 18), floor_fade=None)
LIGHT.point(560, -40, r=700, k=1.2, power=1.1)            # el sol, a dalt a la dreta


# ─── Camps i carretera ──────────────────────────────────────────────────────

def _road_cx(t):
    return 430 + 90 * t


def fields(cv, wet=False):
    """Camps secs, amb solcs que fugen cap a l'horitzó; la carretera a la dreta; la rasa del tub de Verne,
    recta com una regla, fins a l'estació de la Canonada. Si plou: fang fosc i brots verds als solcs."""
    vx, vy = 300, HOR - 60
    ramp = MUD if wet else FIELD
    for y in range(HOR + 1, 200):
        t = (y - HOR) / 82
        for x in range(W):
            ang = math.atan2(y - vy, x - vx)
            furrow = math.sin(ang * 90)
            lvl = 4.2 - t * 1.0 + furrow * 0.5 * t + (fbm(x / 30, y / 6, 11) - 0.5) * 1.0
            if wet:
                lvl = 3.6 - t * 0.6 + furrow * 0.7 * t + (fbm(x / 30, y / 6, 11) - 0.5) * 1.0
            cv.put(x, y, ramp, lvl)
            if wet and furrow > 0.6 and hr(x, y, 77) < 0.08 + 0.25 * t:            # els brots, a la carena dels solcs
                cv.put(x, y - 1, SPROUT, 2.4 + t * 1.6 + hr(x, y) * 1.2)
    # la carretera: de la dreta de baix fins a l'horitzó, amb les roderes
    for y in range(HOR + 1, 200):
        t = (y - HOR) / 82
        cx, hw = _road_cx(t), 1 + 22 * t
        for x in range(int(cx - hw), int(cx + hw) + 1):
            u = (x - cx) / max(1.0, hw)
            rut = abs(abs(u) - 0.5) < 0.12
            if wet:
                lvl = 4.0 - t * 0.4 + (hr(x // 3, y // 2) - 0.5) * 0.8 - (1.0 if rut else 0)
                cv.put(x, y, MUD, lvl + (2.6 if rut and hr(x, y, 3) > 0.5 else 0))   # aigua a les roderes
            else:
                cv.put(x, y, EARTH, 6.0 - t * 0.4 + (hr(x // 3, y // 2) - 0.5) * 0.8 - (0.7 if rut else 0))
    # la rasa: terra remoguda, més clara, i alguna pedra
    for y in range(HOR + 1, 200):
        t = (y - HOR) / 82
        cx = CAN_X + (t * 0.0)
        hw = 0.5 + 3.5 * t
        for x in range(int(cx - hw), int(cx + hw) + 1):
            if wet:
                cv.put(x, y, MUD, 2.6 + (hr(x, y, 8) - 0.5) * 1.6)
            else:
                cv.put(x, y, EARTH, 5.4 + (hr(x, y, 8) - 0.5) * 1.8)
        cv.put(cx - hw - 1, y, ramp, 1.4)
    # una masia en ruïnes, lluny, al turó de l'esquerra
    for x in range(250, 266):
        top = 108 if x < 258 else 110
        for y in range(top, 114):
            cv.put(x, y, (STONE if not wet else STONE), 3.0 + (0.8 if x > 258 else 0) - (1.4 if (x, y) in ((253, 110), (261, 111)) else 0), lit=0)
    cv.line(249, 108, 258, 104, TILE if not wet else STONE, 2.4, lit=0)


def panel(cv, wet=False):
    if wet:
        panell_preu(cv, PANEL[0], PANEL[1], up=False, brand='VESPER')
    else:
        panell_preu(cv, PANEL[0], PANEL[1], up=True)


# ─── La masia ──────────────────────────────────────────────────────────────

def masia(cv, wet=False):
    base = 184
    apex = (104, 34)
    left, right = (-6, 80), (214, 80)

    def wall_lvl(x, y):
        n = fbm(x / 14, y / 10, 21)
        lvl = 3.6 + (n - 0.5) * 1.4 - (0.6 if hr(x // 5, y // 3) > 0.93 else 0) + x * 0.002
        if fbm(x / 22, y / 16, 61) > 0.7 and 92 < y < base - 14:                    # l'arrebossat caigut: la pedra
            row = (y // 5)
            joint = y % 5 == 0 or (x + (row % 2) * 4) % 9 == 0
            lvl = 3.0 + (hr(x // 9, row) - 0.5) * 1.0 - (1.8 if joint else 0)
        if wet:
            lvl -= 0.9 + 0.6 * smooth(0.4, 0.7, fbm(x / 6, y / 30, 5))               # la façana xopa, a regalims
        return lvl

    cv.poly([(0, 82), apex, (208, 82), (208, base), (0, base)], ADOBE, wall_lvl)
    # teulada: la vora de teules a dues aigües
    tile = STONE if False else TILE
    for k in range(10):
        f = k / 9
        lvl = 3.4 - f * 1.4 - (0.8 if wet else 0)
        cv.line(left[0], left[1] + k * 0.4 - 6 + k, apex[0], apex[1] - 6 + k, tile, lvl - 0.4)
        cv.line(apex[0], apex[1] - 6 + k, right[0], right[1] - 6 + k + k * 0.4, tile, lvl + 0.2)
    for i in range(0, 108, 6):                                                      # els canals de les teules
        t = i / 107
        cv.put(left[0] + (apex[0] - left[0]) * t, left[1] - 5 + (apex[1] - left[1]) * t + 1, tile, 4.6)
        cv.put(apex[0] + (right[0] - apex[0]) * t, apex[1] - 5 + (right[1] - apex[1]) * t + 1, tile, 5.0)
    cv.darken(0, 82, 208, 92, lambda x, y: 0.55 if y < 82 + 6 * (1 - abs(x - 104) / 104) + 4 else 0)
    # el ràfec fa ombra a la façana, sota les teules
    cv.darken(0, 34, 208, 100, lambda x, y: 0.5 if 0 <= y - (34 + abs(x - 104) * 0.444) - 4 < 4 and y > 40 else 0)
    # sòcol de pedra
    cv.rect(0, base - 12, 208, base, STONE, lambda x, y: 3.2 + (0.8 if (x // 9 + y // 4) % 2 else 0) -
            (1.4 if x % 9 == 0 or y % 4 == 0 else 0) - (0.8 if wet else 0))
    # la porta d'arc de mig punt
    dx0, dx1, dtop = 82, 124, 128
    cx = (dx0 + dx1) / 2
    for y in range(dtop - 21, base):
        for x in range(dx0 - 4, dx1 + 5):
            r_in, r_out = (dx1 - dx0) / 2, (dx1 - dx0) / 2 + 4
            d = math.hypot(x - cx, (y - dtop) * 1.0) if y < dtop else abs(x - cx)
            if d <= r_in:
                plank = (x - dx0) % 7 == 0
                lvl = 3.0 - (1.4 if plank else 0) - (0.5 if x > cx else 0) + (fbm(x / 3, y / 20, 4) - 0.5) * 0.8
                cv.put(x, y, PLANK, lvl - (0.6 if wet else 0))
            elif d <= r_out and (y < dtop or x < dx0 or x > dx1):
                seg = int(math.atan2(y - dtop, x - cx) * 8) if y < dtop else (y // 7)
                cv.put(x, y, STONE, 4.2 - (1.4 if (hr(seg, 1) > 0.7 or (y >= dtop and y % 7 == 0)) else 0))
    for y in (136, 168):                                                            # les frontisses
        cv.rect(dx0 + 1, y, dx0 + 12, y + 1, IRONR, 2.0)
    cv.disc(116, 158, 1.6, 1.6, RUSTT, 4.0)                                         # la baula
    cv.put(116, 160, RUSTT, 2.4)
    cv.rect(dx0 - 4, base - 1, dx1 + 4, base, STONE, 5.0)                           # el graó
    # finestres amb els finestrons tancats
    for x0, y0, w, h in ((34, 92, 22, 28), (152, 92, 22, 28), (150, 138, 20, 22)):
        cv.rect(x0 - 2, y0 - 2, x0 + w + 1, y0 + h + 1, STONE, 4.4)
        cv.rect(x0, y0, x0 + w - 1, y0 + h - 1, SHUT, lambda x, y: 3.0 - (1.6 if (y - y0) % 4 == 3 else 0) -
                (1.2 if x == x0 + w // 2 else 0) + (fbm(x / 4, y / 9, 13) - 0.5) * 0.9 - (0.6 if wet else 0))
        cv.rect(x0 - 3, y0 + h + 2, x0 + w + 2, y0 + h + 3, STONE, 3.6)
        cv.darken(x0 - 3, y0 + h + 4, x0 + w + 2, y0 + h + 5, 0.6)                # l'ampit fa ombra
        cv.put(x0 + w // 2 + 2, y0 + h // 2, IRONR, 3.4)                           # la balda
    # l'ull de bou de les golfes
    cv.disc(104, 62, 7, 7, STONE, lambda nx, ny: 4.4 + nx * 0.6)
    cv.disc(104, 62, 5, 5, BLACKT, lambda nx, ny: 0.8 + ny * 0.6)
    # el banc de pedra
    cv.rect(140, 174, 178, 177, STONE, lambda x, y: 4.6 + (0.6 if y == 174 else 0))
    cv.rect(142, 178, 145, 184, STONE, 2.6)
    cv.rect(173, 178, 176, 184, STONE, 2.6)
    cv.darken(140, 178, 178, 184, 0.35)
    # el test de geranis secs, a l'esquerra de la porta
    cv.poly([(62, 174), (74, 174), (72, 184), (64, 184)], TILE, lambda x, y: 4.0 + (x - 62) * 0.08)
    cv.rect(61, 173, 75, 174, TILE, 5.0)
    for k, (dx, h) in enumerate(((-3, 8), (0, 11), (3, 7), (5, 9), (-5, 6))):
        col = SPROUT if wet and k < 2 else GRASS
        cv.line(68, 173, 68 + dx, 173 - h, col, 1.4 + (k % 2) * 0.8)
        cv.put(68 + dx, 172 - h, col if wet and k < 2 else PLANK, 3.0)
    # el canaló i el baixant, a la dreta
    cv.rect(203, 84, 205, base - 2, IRONR, lambda x, y: 2.4 + (x - 203) * 0.9)
    cv.rect(201, base - 3, 206, base - 1, IRONR, 3.4)


def cadira(cv):
    """La cadira de boga del pare, a la porta (final_pluja: hi seu en Quim)."""
    x0, base = 126, 196
    cv.rect(x0, base - 18, x0 + 1, base, PLANK, 3.2)                               # potes del darrere
    cv.rect(x0 + 13, base - 18, x0 + 14, base, PLANK, 3.6)
    for y in (base - 16, base - 12):
        cv.rect(x0 + 1, y, x0 + 12, y + 1, PLANK, 3.0)
    cv.rect(x0 - 1, base - 9, x0 + 15, base - 7, STRAW, lambda x, y: 3.0 + ((x + y) % 3 == 0) * 1.0)
    cv.rect(x0 + 1, base - 6, x0 + 2, base + 2, PLANK, 3.4)                         # potes del davant
    cv.rect(x0 + 12, base - 6, x0 + 13, base + 2, PLANK, 3.8)
    shadow(cv, x0 + 2, base + 2, 9, 2, 0.6)


def arbre(cv, x0=232, base=188, wet=False):
    """Una olivera morta: soca torta i branques nues."""
    ramp = GREYW

    def branch(x, y, a, l, w, depth):
        if depth == 0 or l < 3:
            return
        x1, y1 = x + math.cos(a) * l, y - math.sin(a) * l
        for k in range(int(w) + 1):
            cv.line(x + k * 0.5, y, x1 + k * 0.3, y1, ramp, 2.6 - k * 0.6 + depth * 0.25 - (0.8 if wet else 0))
        branch(x1, y1, a + 0.5 + (hr(depth, int(x)) - 0.5) * 0.4, l * 0.7, max(0, w - 1), depth - 1)
        branch(x1, y1, a - 0.45 + (hr(int(y), depth) - 0.5) * 0.4, l * 0.65, max(0, w - 1), depth - 1)
    for y in range(base - 46, base + 1):                                            # la soca, retorçada
        wob = math.sin(y * 0.15) * 3
        flare = max(0, y - base + 8) * 0.6
        for x in range(int(x0 - 5 - flare + wob), int(x0 + 5 + flare + wob)):
            u = (x - x0 - wob) / (5 + flare)
            groove = (x + y // 3) % 5 == 0
            cv.put(x, y, ramp, 3.0 + u * 1.4 - (1.2 if groove else 0) - (0.8 if wet else 0))
    branch(x0 + math.sin((base - 46) * 0.15) * 3, base - 46, 1.25, 26, 3, 5)
    branch(x0 + 2, base - 40, 0.35, 22, 2, 4)
    branch(x0 - 2, base - 30, 2.6, 18, 2, 4)
    cv.disc(x0 + 1, base - 22, 2, 3, BLACKT, 1.2)                                   # un forat a la soca
    if wet:                                                                         # un brot verd: no és morta del tot
        cv.put(x0 + 6, base - 34, SPROUT, 3.6)
        cv.put(x0 + 7, base - 35, SPROUT, 4.2)
        cv.put(x0 + 8, base - 35, SPROUT, 3.0)


# ─── El graner i el tractor ────────────────────────────────────────────────

def graner(cv, wet=False):
    x0, x1, top, base = 472, 640, 92, 190
    dw = 0.8 if wet else 0
    cv.poly([(x0 - 4, top + 2), (x0 + 60, top - 26), (x1 + 4, top - 8), (x1 + 4, top + 4)], RUSTT,
            lambda x, y: 3.2 - dw + (0.8 if x % 5 < 2 else -0.4) + (fbm(x / 9, y / 9, 5) - 0.5) * 1.6)   # xapa rovellada
    cv.line(x0 - 4, top + 2, x0 + 60, top - 26, RUSTT, 5.0 - dw)
    cv.rect(x0 - 4, top + 3, x1, top + 5, BLACKT, 1.4)                              # l'ombra del ràfec
    cv.rect(x0, top + 6, x1, base, GREYW, lambda x, y: 3.6 - dw - (1.8 if (x - x0) % 8 == 0 else 0) +
            (fbm(x / 6, y / 18, 41) - 0.5) * 1.2 - (0.8 if (x - x0) % 8 == 1 else 0))
    for (nx, ny) in ((x0 + 4, top + 20), (x0 + 4, base - 20), (x1 - 4, top + 20)):   # claus de les taules
        cv.put(nx, ny, IRONR, 2.0)
    # la porta gran, oberta: dins, la penombra, i el tractor vermell de l'avi
    dx0, dx1, dtop = 516, 600, 118
    cv.rect(dx0, dtop, dx1, base, BLACKT, lambda x, y: 0.3 + max(0.0, (y - dtop - 40) / 40) * 1.4, lit=0)
    for x in range(dx0, dx1 + 1, 9):                                                # les taules de la paret del fons
        cv.rect(x, dtop + 2, x, base - 30, BLACKT, 1.6, lit=0)
    cv.rect(dx0 + 4, dtop + 26, dx0 + 14, dtop + 46, STRAW, 0.8, lit=0)             # bales de palla al fons
    cv.rect(dx1 - 16, dtop + 30, dx1 - 2, dtop + 48, STRAW, 0.6, lit=0)
    # el sol entra per la porta: un trapezi de llum al terra de dins
    cv.poly([(dx0 + 2, base), (dx1, base), (dx1 - 6, base - 10), (dx0 + 14, base - 10)], EARTH,
            lambda x, y: 4.6 - (base - y) * 0.18, lit=0)
    tx = dx0 + 44
    for wx in (tx - 30, tx + 30):                                                   # les rodes grosses del darrere
        cv.disc(wx, 170, 13, 15, BLACKT, lambda nx, ny: 1.4 + (0.8 if int((nx * 3 + ny * 5) * 2) % 2 else 0) + nx * 0.4, lit=0)
        cv.disc(wx, 170, 5, 6, REDT, lambda nx, ny: 1.6 + nx * 0.6, lit=0)
    cv.rect(tx - 14, 140, tx + 14, 154, REDT, lambda x, y: 1.8 + (x - tx) * 0.03, lit=0)   # el seient i el volant
    cv.line(tx - 8, 140, tx + 8, 138, BLACKT, 2.4, lit=0)
    cv.rect(tx + 6, 124, tx + 8, 150, BLACKT, 2.0, lit=0)                          # el tub d'escapament
    cv.rect(tx + 5, 122, tx + 9, 124, BLACKT, 2.6, lit=0)
    cv.rect(tx - 18, 152, tx + 18, 176, REDT, lambda x, y: 3.0 + (x - tx) * 0.04 - (1.4 if y == 152 else 0) +
            (0.8 if y == 153 else 0), lit=0)                                        # el capó
    cv.rect(tx - 11, 157, tx + 11, 172, BLACKT, lambda x, y: 1.2 + (1.6 if (x - tx) % 3 == 0 else 0), lit=0)   # la graella
    for fx in (tx - 15, tx + 15):                                                   # els fars
        cv.disc(fx, 157, 2.4, 2.4, [(70, 60, 30), (150, 140, 80), (230, 220, 150), (255, 250, 210)],
                lambda nx, ny: 2.0 - nx - ny, lit=0)
    for wx in (tx - 15, tx + 15):                                                   # les rodes petites del davant
        cv.disc(wx, 182, 5, 7, BLACKT, lambda nx, ny: 1.8 + nx * 0.6, lit=0)
    cv.rect(tx - 6, 177, tx + 6, 179, IRONR, 2.0, lit=0)
    # el sol del terra rebota al morro del tractor
    cv.tint(dx0, 172, dx1, base, (200, 160, 110), lambda x, y: 0.25 * (y - 172) / 18)
    # la fulla de la porta, oberta cap enfora
    cv.poly([(dx0 - 2, dtop), (dx0 - 34, dtop + 8), (dx0 - 34, base + 6), (dx0 - 2, base)], GREYW,
            lambda x, y: 2.8 - dw - (1.6 if (x - dx0) % 7 == 0 else 0) + (fbm(x / 5, y / 14, 3) - 0.5) * 0.8)
    cv.line(dx0 - 30, dtop + 14, dx0 - 4, base - 6, GREYW, 1.4)                     # la Z de la porta
    cv.line(dx0 - 30, base - 4, dx0 - 4, dtop + 10, GREYW, 1.4)
    cv.line(dx0 - 31, dtop + 12, dx0 - 3, dtop + 8, GREYW, 4.0)
    cv.line(dx0 - 31, base + 1, dx0 - 3, base - 2, GREYW, 1.6)
    cv.rect(dx1 + 1, dtop, dx1 + 3, base, GREYW, 2.2)                              # el marc
    cv.rect(dx0 - 1, dtop - 3, dx1 + 3, dtop - 1, GREYW, 4.4)
    # la ferradura de la sort, damunt la porta, i una llanta vella penjada
    for a in range(200, 341, 12):
        cv.put(558 + math.cos(math.radians(a)) * 4, 108 - math.sin(math.radians(a)) * 4 - 4, IRONR, 4.0)
    cv.put(554, 104, IRONR, 3.0)
    cv.put(562, 104, IRONR, 3.0)
    cv.ring(616, 146, 9, RUSTT, 2.8, step=3)
    cv.ring(616, 146, 8, RUSTT, 4.0, step=3)
    cv.ring(616, 146, 3, RUSTT, 2.0, step=8)
    cv.rect(615, 134, 617, 136, IRONR, 2.0)
    # la forca, recolzada a la paret
    cv.line(498, 186, 504, 128, GREYW, 4.4)
    for k in (-2, 0, 2):
        cv.line(504 + k, 128, 504 + k * 1.4, 120, IRONR, 3.6)


def cami(cv, wet=False):
    """El pal indicador del camí del port, a la dreta, davant del graner."""
    x, base = 620, 202
    cv.rect(x, base - 32, x + 2, base, GREYW, lambda xx, y: 2.4 + (xx - x) * 0.8)
    cv.poly([(x - 14, base - 30), (x + 14, base - 30), (x + 19, base - 26), (x + 14, base - 22), (x - 14, base - 22)],
            GREYW, lambda xx, y: 4.2 - (0.8 if y == base - 22 else 0) - (0.8 if wet else 0))
    text(cv, 'PORT', x - 11, base - 28, BLACKT, 1.0, lit=0, flat=(60, 40, 30))
    cv.put(x + 1, base - 26, IRONR, 1.0)
    shadow(cv, x - 6, base + 1, 9, 2, 0.6)


# ─── Pou, bomba i tanca ────────────────────────────────────────────────────

def tanca(cv, wet=False):
    for x in range(250, 470, 26):
        lean = (hr(x, 3) - 0.5) * 2
        for y in range(160, 187):
            cv.put(x + lean * (186 - y) / 26, y, GREYW, 3.0 - (0.8 if wet else 0))
            cv.put(x + 1 + lean * (186 - y) / 26, y, GREYW, 4.0 - (0.8 if wet else 0))
            cv.put(x + 2 + lean * (186 - y) / 26, y, GREYW, 2.2)
        cv.put(x + 1 + lean, 159, GREYW, 4.6)
    for y in (166, 176):
        for x in range(250, 470):
            if not (x % 26 in (0, 1, 2)) and hr(x // 26, y) > 0.15:
                sag = math.sin(((x % 26) / 26) * math.pi) * 1.2
                cv.put(x, y + sag, GREYW, 4.0 - (0.8 if (x // 3) % 7 == 0 else 0) - (0.8 if wet else 0))
                cv.put(x, y + sag + 1, GREYW, 2.0)


def pou(cv, wet=False):
    """El pou de pedra: el cos cilíndric de carreus, la vora, els pals, la biga, la politja i la galleda.
    Sec, amb el forat negre; plovent, ple fins a dalt."""
    dw = 0.7 if wet else 0
    top_c, bot_c, ry = WTOP + 4, WBASE + 4, 7
    for x in range(WX - WRX, WX + WRX + 1):
        u = (x - WX) / WRX
        s = math.sqrt(max(0.0, 1 - u * u))
        ang = math.asin(max(-1.0, min(1.0, u)))
        for y in range(int(top_c + ry * s), int(bot_c + ry * s) + 1):
            yy = y - ry * s - top_c                                                  # alçada sobre la vora
            row = int(yy // 6)
            off = 0.5 if row % 2 else 0
            colf = ang * 5 + off
            joint = yy % 6 < 1 or abs(colf - round(colf)) < 0.09
            lvl = 3.4 + u * 1.6 - (1 - s) * 1.4 + (hr(row, round(colf)) - 0.5) * 1.0
            if joint:
                lvl -= 1.8
            if wet:
                lvl -= dw + (0.6 if yy < 8 else 0)
            cv.put(x, y, STONE, lvl)
    # la vora: carreus plans, i el forat (sec, o ple d'aigua)
    cv.disc(WX, top_c, WRX, ry, STONE, lambda nx, ny: 5.0 + nx * 0.6 - (1.6 if abs(math.atan2(ny, nx) * 4 % 1) < 0.12 else 0) - dw)
    if wet:
        cv.disc(WX, top_c, WRX - 4, 4.4, WATER, lambda nx, ny: 4.0 - ny * 1.2 + (1.6 if abs(ny + 0.2) < 0.15 and nx > -0.3 else 0), lit=0)
    else:
        cv.disc(WX, top_c, WRX - 4, 4.4, BLACKT, lambda nx, ny: 0.3 + ny * 0.9, lit=0)
    # els pals i la biga
    for px_ in (WX - 22, WX + 22):
        cv.rect(px_ - 2, 130, px_ + 1, top_c, GREYW, lambda x, y: 2.6 + (x - px_ + 2) * 0.7 - dw)
    cv.rect(WX - 27, 126, WX + 27, 130, GREYW, lambda x, y: 4.2 - (y - 126) * 0.7 - dw)
    cv.rect(WX - 27, 131, WX + 27, 131, BLACKT, 1.6)
    # la politja, la corda i la galleda
    cv.disc(WX, 137, 5, 5, IRONR, lambda nx, ny: 3.6 + nx - ny)
    cv.ring(WX, 137, 5, IRONR, 1.4, step=10)
    cv.disc(WX, 137, 1.4, 1.4, BLACKT, 1.0)
    cv.line(WX, 130, WX, 132, IRONR, 2.0)
    cv.line(WX - 5, 137, WX - 5, top_c + 1, PLANK, 3.6)                             # la corda que baixa al pou
    cv.line(WX + 5, 137, WX + 5, 149, PLANK, 3.6)
    gx = WX + 5
    cv.line(gx - 5, 151, gx, 148, IRONR, 2.4)                                       # la nansa
    cv.line(gx, 148, gx + 5, 151, IRONR, 2.4)
    cv.poly([(gx - 6, 151), (gx + 6, 151), (gx + 5, 162), (gx - 5, 162)], IRONR,
            lambda x, y: 3.0 + (x - gx) * 0.2 - (1.2 if y in (154, 159) else 0) - dw)
    cv.rect(gx - 6, 151, gx + 6, 151, IRONR, 4.6)


def bomba(cv, wet=False):
    """La bomba de Verne: una caixa blanca i neta, amb la gota blava, el panell de quatre cargols de cap de flor,
    el llum verd, el tub ficat al pou i la rasa que se'n va cap a la Canonada. Plovent: apagada, i amb el
    cartell del banc."""
    dw = 0.5 if wet else 0
    # la cara de dalt i el costat de l'esquerra (a l'ombra: el sol és a la dreta)
    cv.poly([(BX0, BY0), (BX1, BY0), (BX1 - 3, BY0 - 4), (BX0 - 4, BY0 - 4)], WHITEP, 5.6 - dw)
    cv.poly([(BX0 - 4, BY0 - 4), (BX0, BY0), (BX0, BY1), (BX0 - 4, BY1 - 3)], WHITEP, 2.6 - dw)
    cv.rect(BX0, BY0, BX1, BY1, WHITEP, lambda x, y: 4.4 + (x - BX0) * 0.03 - dw + (0.8 if y == BY0 else 0) -
            (1.2 if x == BX0 else 0))
    cv.rect(BX0, BY1 - 2, BX1, BY1, WHITEP, 2.2)                                    # el sòcol
    # el panell del davant, amb els quatre cargols de cap de flor
    px0, py0, px1, py1 = BX0 + 3, BY0 + 3, BX1 - 3, BY1 - 5
    cv.rect(px0, py0, px1, py0, WHITEP, 3.0)
    cv.rect(px0, py0, px0, py1, WHITEP, 3.0)
    cv.rect(px0, py1, px1, py1, WHITEP, 5.4)
    cv.rect(px1, py0, px1, py1, WHITEP, 5.4)
    for sx, sy in ((px0 + 2, py0 + 2), (px1 - 2, py0 + 2), (px0 + 2, py1 - 2), (px1 - 2, py1 - 2)):
        cv.flat(sx, sy, (120, 126, 140))
        cv.flat(sx - 1, sy, (180, 186, 196))
        cv.flat(sx + 1, sy, (180, 186, 196))
        cv.flat(sx, sy - 1, (180, 186, 196))
        cv.flat(sx, sy + 1, (180, 186, 196))
    gota(cv, (BX0 + BX1) // 2, BY0 + 12, 3)                                         # el logotip
    cv.rect(px0 + 3, BY0 + 20, px1 - 3, BY0 + 22, BLUE, 1.6, lit=0)                # la franja «VERNE»
    for x in range(px0 + 4, px1 - 3, 3):
        cv.flat(x, BY0 + 21, (210, 225, 245))
    cv.rect(px1 - 6, BY0 + 25, px1 - 3, BY0 + 27, WARN, 3.6, lit=0)                # perill
    cv.flat(px1 - 5, BY0 + 26, (40, 30, 6))
    # el llum d'estat: verd (xucla) o apagat
    if wet:
        cv.disc(px0 + 3, BY0 + 26, 1.2, 1.2, BLACKT, 2.4, lit=0)
    else:
        cv.disc(px0 + 3, BY0 + 26, 1.2, 1.2, LEDG, 3.4, lit=0)
        cv.glow(px0 + 3, BY0 + 26, 4, (120, 255, 140), 0.4)
    # el tub que va al pou, en arc, blanc i nou
    for i in range(48):
        t = i / 47
        x = BX0 - 4 - (BX0 - 4 - (WX + 15)) * t
        y = BY0 + 2 - math.sin(t * math.pi) * 14
        for k in range(3):
            cv.put(x, y + k, WHITEP, 5.0 - k * 1.2 - dw)
        if i in (6, 41):
            cv.put(x, y - 1, BLUE, 2.4, lit=0)
            cv.put(x, y + 3, BLUE, 2.0, lit=0)
    cv.rect(WX + 14, WTOP - 1, WX + 16, WTOP + 7, WHITEP, lambda x, y: 3.0 + (x - WX - 14) * 0.8 - dw)
    cv.rect(WX + 13, WTOP + 3, WX + 17, WTOP + 4, WHITEP, 5.0 - dw)                 # la brida
    # la rasa del tub de sota terra, cap a la Canonada: terra remoguda, tapada de pressa
    for i in range(80):
        t = i / 79
        x = BX1 + 2 + (CAN_X - BX1 - 2) * t
        y = BY1 - 1 - (BY1 - 1 - 188) * t
        ramp = MUD if wet else EARTH
        cv.put(x, y, ramp, 2.0)
        cv.put(x, y - 1, ramp, 6.6 - (2 if wet else 0))
        cv.put(x + 1, y - 1, ramp, 6.0 - (2 if wet else 0))
        if i % 9 == 0:
            cv.put(x, y - 2, WHITEP, 3.2 - dw)
    if wet:
        cartell_banc(cv)


def cartell_banc(cv):
    """El cartell de plàstic del banc, lligat amb filferro a la bomba: «BANC DE VESPER»."""
    x0, y0, x1, y1 = BX0 - 2, BY0 + 6, BX1 + 2, BY0 + 22
    cv.rect(x0, y0, x1, y1, PAPER, lambda x, y: 4.8 - (0.6 if y == y1 else 0) + (x - x0) * 0.02)
    for x in range(x0, x1 + 1):
        cv.flat(x, y0, (40, 70, 60))
    cv.rect(x0, y0 + 1, x1, y0 + 2, [(30, 60, 50), (50, 96, 80), (90, 140, 118)], 1.4, lit=0)
    text(cv, 'BANC DE', x0 + (x1 - x0 + 1 - text_width('BANC DE')) // 2, y0 + 4, BLACKT, 1.0, lit=0, flat=(40, 52, 50))
    text(cv, 'VESPER', x0 + (x1 - x0 + 1 - text_width('VESPER')) // 2, y0 + 10, BLACKT, 1.0, lit=0, flat=(30, 80, 64))
    for wx in (x0 + 1, x1 - 1):                                                     # el filferro
        cv.put(wx, y0 - 1, IRONR, 4.0)
        cv.put(wx, y0 - 2, IRONR, 3.0)
    cv.darken(x0 + 1, y1 + 1, x1 + 1, y1 + 2, 0.7)


def bomba_oberta(cv):
    """Decorat: el panell de la bomba obert (girat cap a l'esquerra) i, a dins, el motor i l'etiqueta."""
    px0, py0, px1, py1 = BX0 + 3, BY0 + 3, BX1 - 3, BY1 - 5
    cv.rect(px0, py0, px1, py1, BLACKT, lambda x, y: 0.6 + (y - py0) * 0.04, lit=0)    # el forat, fosc
    cv.disc(px0 + 9, py0 + 18, 7, 6, IRONR, lambda nx, ny: 3.4 - nx * 0.8 - ny * 0.8)  # el motor
    for k in range(-5, 6, 2):
        cv.line(px0 + 9 + k, py0 + 13, px0 + 9 + k, py0 + 23, IRONR, 1.8)
    cv.rect(px0 + 15, py0 + 10, px0 + 18, py1 - 1, WHITEP, lambda x, y: 3.4 + (x - px0 - 15) * 0.5)   # el tub de dins
    cv.rect(px0 + 2, py0 + 2, px1 - 2, py0 + 9, PAPER, 5.2, lit=0)                 # l'etiqueta: «ESTACIÓ 7.788»
    text(cv, '7.788', px0 + 3, py0 + 3, BLACKT, 1.0, lit=0, flat=(30, 30, 40))
    cv.put(px1 - 3, py0 + 3, BLUE, 2.4, lit=0)
    cv.put(px1 - 3, py0 + 4, BLUE, 2.4, lit=0)
    for x in (px0 + 3, px0 + 7, px0 + 11):
        cv.flat(x, py0 + 9, (120, 110, 100))
    cv.disc(px0 + 4, py1 - 4, 1.2, 1.2, LED, 3.2, lit=0)                            # un fusible
    # la porta del panell, oberta cap a la dreta, penjada de la frontissa: se'n veu la cara de dins
    hx = px1 + 1
    cv.poly([(hx, py0), (hx + 13, py0 - 3), (hx + 13, py1 + 5), (hx, py1)], WHITEP,
            lambda x, y: 3.6 - (x - hx) * 0.08)
    cv.line(hx + 13, py0 - 3, hx + 13, py1 + 5, WHITEP, 5.4)
    cv.line(hx, py0, hx + 13, py0 - 3, WHITEP, 5.0)
    cv.rect(hx + 3, py0 + 6, hx + 9, py0 + 14, PAPER, 3.0)                       # l'esquema, enganxat per dins
    for sx, sy in ((hx + 11, py0 + 1), (hx + 11, py1 + 2)):
        cv.flat(sx, sy, (120, 126, 140))
    cv.darken(hx - 4, BY1 + 1, hx + 12, BY1 + 4, 0.6)
    cv.rect(px0 + 1, BY1 + 2, px0 + 8, BY1 + 3, IRONR, 2.6)                         # els cargols, a terra
    cv.flat(px0 + 11, BY1 + 3, (150, 150, 160))
    cv.flat(px0 + 14, BY1 + 4, (150, 150, 160))


# ─── El terra del pati ─────────────────────────────────────────────────────

def _path(x, y):
    """El camí del port: una franja trepitjada que surt per la dreta. → 0..1"""
    if x < 360:
        return 0.0
    f = min(1.0, (x - 360) / 60)
    cy = 230 - (x - 360) * 0.06
    hw = 9 + (x - 360) * 0.035
    return f * (1 - smooth(hw - 3, hw + 3, abs(y - cy) + (fbm(x / 12, y / 6, 71) - 0.5) * 6))


def puddle(x, y):
    """Els bassals del final (0..1): on el pati fa clot."""
    v = 0.0
    for cx, cy, rx, ry in ((60, 222, 34, 6), (190, 244, 46, 7), (360, 230, 30, 5), (470, 250, 40, 6),
                           (560, 214, 26, 4), (262, 212, 18, 3)):
        d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
        v = max(v, 1 - d + (fbm(x / 14, y / 5, 91) - 0.5) * 0.9)
    return v


def terra(cv, wet=False):
    for y in range(184, RH):
        t = (y - 184) / (RH - 184)
        for x in range(W):
            c = cracks(x, int((y - 184) / (0.5 + t)) + 184, cell=11 + int(t * 8))
            lvl = 4.4 + t * 0.6 + (fbm(x / 40, y / 10, 17) - 0.5) * 1.4
            p = _path(x, y)
            if c < 1.0 + t * 0.6:
                lvl -= 2.4 * (1 - p * 0.8)
            elif c < 2.0 + t:
                lvl += 0.6 * (1 - p)
            lvl += p * 1.3 + (hr(x // 2, y) - 0.5) * 0.5 * p
            if wet:
                lvl -= 1.0
                if p > 0.3 and hr(x, y, 41) < 0.02:
                    lvl -= 1.5
                pd = puddle(x, y)
                if pd > 0:
                    # el bassal: el reflex del cel gris (més clar a dalt, on reflecteix el cel baix)
                    edge = pd < 0.18
                    refl = 3.2 + (fbm(x / 26, y / 2, 3) - 0.5) * 1.6 + (1.2 if fbm(x / 8, y, 5) > 0.68 else 0)
                    cv.put(x, y, RSKY if not edge else MUD, refl if not edge else 1.4, lit=0.3)
                    continue
                cv.put(x, y, MUD, lvl + 0.8)
            else:
                cv.put(x, y, EARTH, lvl)
    for x, y in ((40, 236), (120, 250), (470, 244), (600, 252), (210, 214), (330, 246)):  # pedres
        cv.disc(x, y, 3, 2, STONE, lambda nx, ny: 4.0 + nx - ny - (0.8 if wet else 0))
        cv.darken(x - 5, y + 1, x + 1, y + 3, 0.6)
    for x0, y0 in ((6, 186), (196, 188), (476, 192), (246, 190), (624, 196), (440, 200)):   # herba seca (o verda)
        for k in range(7):
            a = 1.2 + (k - 3) * 0.18
            col = SPROUT if wet and k % 2 else GRASS
            cv.line(x0 + k, y0, x0 + k + math.cos(a) * 7, y0 - math.sin(a) * 7, col, 2.0 + hr(k, x0) * 2)


def ombres(cv):
    """Ombres curtes cap a l'esquerra (el sol és a dalt a la dreta)."""
    shadow(cv, WX - 16, WBASE + 7, 32, 6)
    shadow(cv, BX0 - 4, BY1 + 2, 18, 4)
    shadow(cv, 222, 190, 16, 3)
    shadow(cv, 66, 185, 8, 2, 0.6)


# ─── Composició ────────────────────────────────────────────────────────────

def draw(cv, wet=False):
    if wet:
        rain_sky(cv, HOR)
    else:
        dust_sky(cv, HOR)
    hills(cv, HOR, wet)
    canonada(cv, CAN_X, HOR, haze=(150, 152, 150) if wet else (230, 214, 180))
    if wet:                                                                         # els núvols s'empassen la Canonada
        cv.tint(CAN_X - 8, 0, CAN_X + 8, 40, (150, 152, 152), lambda x, y: 0.9 - y / 50)
    fields(cv, wet)
    panel(cv, wet)
    terra(cv, wet)
    tanca(cv, wet)
    masia(cv, wet)
    arbre(cv, wet=wet)
    graner(cv, wet)
    cami(cv, wet)
    if not wet:
        ombres(cv)
    else:
        shadow(cv, WX, WBASE + 7, 30, 4, 0.5)
        shadow(cv, (BX0 + BX1) // 2, BY1 + 2, 16, 3, 0.5)
    pou(cv, wet)
    bomba(cv, wet)
    if not wet:
        cv.tint(0, 0, W - 1, RH - 1, (240, 200, 140), 0.06)                         # la calitja de pols
    else:
        cv.tint(0, 0, W - 1, RH - 1, (96, 104, 112), 0.16)                          # tot, més fred i apagat
        cv.tint(0, 0, W - 1, 190, (170, 176, 180), lambda x, y: 0.18 * (1 - y / 190))   # la cortina de pluja
    for y in range(RH, H):                                                          # la barra de verbs: negre
        for x in range(W):
            cv.flat(x, y, (0, 0, 0))


def bg(cv):
    draw(cv, wet=False)


PROPS = {'bomba_oberta': bomba_oberta}


# ─── Animacions ─────────────────────────────────────────────────────────────

_BASE = []


def _base():
    if not _BASE:
        cv = Canvas(light=LIGHT)
        bg(cv)
        _BASE.append(cv.img)
    return _BASE[0]


def _frames_pols():
    return dust_wind_frames(_base(), 150, 258, n=64, step=10, k=0.55)


def _frames_llum():
    return llum_canonada_frames(CAN_X)


ANIMS = {'pols': {'frames': _frames_pols, 'frameDuration': 110},
         'llum_canonada': {'frames': _frames_llum, 'frameDuration': 220}}


# ─── Geometria (coordenades de 640×360) ─────────────────────────────────────

GEOMETRIA = {
    'things': {
        'porta_casa': {'rect': (78, 104, 128, 185), 'walk': (104, 204)},
        'porta_graner': {'rect': (516, 116, 602, 191), 'walk': (556, 206)},
        'cami_port': {'rect': (606, 192, 639, 258), 'walk': (630, 224)},
        'pou': {'rect': (272, 124, 328, 214), 'walk': (296, 224)},
        'bomba': {'rect': (330, 166, 366, 210), 'walk': (354, 222)},
        'canonada': {'rect': (390, 0, 414, 117), 'walk': (402, 214)},
        'panell_preu': {'rect': (410, 122, 471, 158), 'walk': (444, 210)},
        'arbre': {'rect': (204, 112, 264, 190), 'walk': (236, 206)},
        'tanca': {'rect': (368, 159, 470, 189), 'walk': (420, 210)},
    },
    'spawns': {'iri': (442, 236), 'vet': (384, 242), 'diu': (284, 180)},
    'walkable': [(0, 198), (130, 197), (250, 199), (268, 214), (334, 216), (370, 211), (472, 198), (639, 199),
                 (639, 258), (0, 258)],
}
