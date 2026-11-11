"""
La infermeria de l'Arenga: petita i ordenada, pintada de blanc, amb el linòleum gris verdós. D'esquerra a dreta:
  - la porta del passadís i, al costat, la boca del tub de veu de llautó (PONT · MÀQUINES · CUINA);
  - l'armari de medicaments (vidre a dalt, amb la creu vermella), l'escriptori amb l'arxivador de fitxes;
  - la llitera de rescat (una llitera de cistella, amb els travessers d'acer i les corretges taronja) muntada sobre
    un bastidor fix, amb el llum d'examen plegat a sobre; és FRONT: qui hi seu (en Bastida a l'Escena 3, la Juana a la 7)
    hi queda darrere;
  - el marbre amb la pica, el mirall i la cafetera dolenta (el pilot vermell encès), i una bombona d'oxigen.
"""
import math

from hd.pix import Canvas, Light, W, H, hr, mix
from hd.rooms.arenga import CAB, DARK, WHITEP, REDP, YELL, BRASS, SEAG, FLOOR_Y, BOTTOM, box, rrect, bolt, hpipe, vpipe, glow
from hd.rooms.principal import (CREAM, TEAK, DOORP, CEIL_H, wall, ceiling, lamp, lamp_glow, lino, shine, unmask,
                                foot_shadow, floor_shadow, in_door, door_frame, sill, leaf, plaque, porthole, wear,
                                voice_tube, day_porthole)
from hd.rooms.comu import _diff, text, text_width

LAMPS = (112, 296, 430)
STEEL = [(10, 12, 14), (22, 25, 28), (38, 42, 46), (58, 63, 68), (82, 88, 93), (110, 116, 120), (142, 148, 150),
         (180, 184, 186), (220, 222, 222)]
MEDLINO = [(8, 12, 12), (16, 22, 22), (26, 34, 33), (38, 48, 46), (52, 64, 60), (68, 82, 76), (86, 102, 94),
           (108, 124, 114), (132, 148, 136)]
FILEG = [(8, 16, 12), (14, 28, 22), (22, 42, 34), (32, 58, 46), (46, 76, 60), (64, 98, 78), (90, 124, 102),
         (124, 156, 132)]
ORANGE = [(48, 16, 6), (100, 36, 10), (160, 64, 16), (210, 100, 30), (240, 144, 60), (255, 190, 110)]
PAD = [(10, 24, 30), (16, 40, 50), (24, 60, 72), (36, 84, 98), (54, 110, 124), (80, 140, 150), (120, 176, 182)]
GLASSC = [(16, 22, 26), (30, 40, 46), (50, 64, 70), (76, 94, 100), (110, 130, 136), (160, 180, 184)]
COFFEE = [(12, 6, 4), (24, 12, 6), (40, 20, 10), (60, 32, 16)]
OXY = [(10, 30, 16), (16, 56, 30), (26, 90, 48), (44, 126, 70), (80, 166, 104), (140, 210, 160)]
BOXES = ([(40, 40, 40), (120, 120, 116), (200, 200, 192), (236, 236, 228)], [(10, 30, 60), (20, 60, 120), (60, 110, 180), (140, 180, 230)],
         [(60, 10, 10), (140, 30, 30), (210, 70, 60), (240, 140, 120)], [(50, 40, 6), (130, 100, 16), (210, 170, 40), (240, 220, 120)],
         [(70, 40, 10), (140, 80, 20), (200, 130, 50), (230, 180, 110)])

LIGHT = Light(ambient=-0.25, vignette=(44, 24), floor_fade=(188, 40))
for _x in LAMPS:
    LIGHT.point(_x, CEIL_H + 4, r=124, k=2.3, squash=1.1, down=True, power=1.5)

D_PORTA = (10, 64, 48, FLOOR_Y)
ARMARI = (82, 40, 134, FLOOR_Y - 1)
DESK = (144, 112, 214)                # x0, y del sobre, x1
FITXES = (152, 82, 200, 111)
LL_X0, LL_X1 = 226, 374               # la llitera
LL_TOP, LL_RAIL, LL_BOT = 116, 124, 138
CAFE = (418, 86, 450, 112)
COUNTER_Y = 112
JUANA = (318, 150)                    # on seu la Juana (peus; el FRONT de la llitera li tapa les cames)
TRAVESSER = LL_X0 + 8 + 16 * 3        # el travesser que en Bastida s'emporta (decorat `sense_travesser`)
WOOLG = [(18, 18, 16), (34, 34, 30), (54, 53, 47), (78, 76, 68), (104, 101, 90), (132, 128, 114), (162, 158, 142)]
WOOLR = [(30, 8, 8), (56, 16, 14), (88, 28, 22), (120, 42, 32), (152, 62, 44), (182, 90, 64), (210, 126, 94)]


# ─── Porta i tub de veu ─────────────────────────────────────────────────────

def door(cv):
    x0, y0, x1, y1 = D_PORTA
    leaf(cv, x0, y0, x1, y1 - 5, WHITEP, 3.7, handle='right', seed=8)
    door_frame(cv, x0, y0, x1, y1)
    sill(cv, x0, x1, y1)
    # un penjador amb la bata (de quan hi havia metge)
    cv.rect(x0 + 6, y0 + 8, x0 + 9, y0 + 10, BRASS, 3.8)


# ─── L'armari de medicaments ────────────────────────────────────────────────

def cabinet(cv):
    """Armari metàl·lic blanc: vitrina a dalt amb pots i capses, portes cegues a baix, la creu al capdamunt."""
    x0, y0, x1, y1 = ARMARI
    box(cv, x0, y0, x1, y1, WHITEP, 3.9, grad=0.6)
    cv.vline(x0 + 1, y0 + 1, y1 - 1, WHITEP, 4.8)
    # la creu vermella, a dalt
    cx = (x0 + x1) // 2
    cv.rect(cx - 2, y0 + 2, cx + 2, y0 + 12, REDP, 4.2)
    cv.rect(cx - 7, y0 + 5, cx + 7, y0 + 9, REDP, 4.2)
    # vitrina: dues portes de vidre
    vx0, vy0, vx1, vy1 = x0 + 3, y0 + 16, x1 - 3, y0 + 66
    for y in range(vy0, vy1 + 1):
        for x in range(vx0, vx1 + 1):
            cv.put(x, y, GLASSC, 2.0 + (vy1 - y) * 0.01)
    for sy in (vy0 + 16, vy0 + 33, vy1 - 1):                              # prestatges
        cv.hline(vx0, vx1, sy, WHITEP, 3.6)
        cv.hline(vx0, vx1, sy + 1, WHITEP, 2.2)
    for row, sy in enumerate((vy0 + 15, vy0 + 32, vy1 - 2)):
        x = vx0 + 2
        i = 0
        while x < vx1 - 3:
            kind = int(hr(row, i, 6) * 4)
            h = 5 + int(hr(row, i, 7) * 7)
            w = 3 + int(hr(row, i, 8) * 4)
            if x + w > vx1 - 1:
                break
            if kind == 0:                                                 # ampolla marró (iode)
                cv.rect(x, sy - h, x + w - 1, sy, [(30, 14, 6), (70, 34, 12), (120, 64, 24), (170, 110, 50)], 2.6)
                cv.rect(x + 1, sy - h - 2, x + w - 2, sy - h, WHITEP, 3.8)
            elif kind == 1:                                               # pot blanc
                cv.rect(x, sy - h + 2, x + w, sy, WHITEP, 3.8)
                cv.hline(x, x + w, sy - h + 2, BOXES[1], 2.4)
            else:                                                         # capses
                b = BOXES[int(hr(row, i, 9) * 5)]
                cv.rect(x, sy - h, x + w + 1, sy, b, 2.8)
                cv.vline(x, sy - h, sy, b, 3.4)
            x += w + 2
            i += 1
    # les gases i benes, a la fila de baix, rodons
    for bx in (vx0 + 4, vx0 + 10):
        cv.disc(bx, vy1 - 5, 3, 3, WHITEP, lambda nx, ny: 4.4 - nx - ny)
    # marcs de les portes de vidre i reflexos
    cv.vline(cx, vy0, vy1, WHITEP, 3.4)
    for x in (vx0, vx1):
        cv.vline(x, vy0, vy1, WHITEP, 3.6)
    cv.hline(vx0, vx1, vy0, WHITEP, 3.6)
    cv.hline(vx0, vx1, vy1, WHITEP, 3.6)
    for k in range(0, 20):
        for gx0 in (vx0 + 6, cx + 6):
            xx, yy = gx0 + k // 2, vy0 + 2 + k
            if yy < vy1 - 2:
                cv.flat(xx, yy, mix(cv.get(xx, yy), (220, 236, 240), 0.3))
    # nanses i pany
    cv.rect(cx - 3, vy0 + 26, cx - 2, vy0 + 32, STEEL, 5.6)
    cv.rect(cx + 2, vy0 + 26, cx + 3, vy0 + 32, STEEL, 5.6)
    # a baix, portes cegues
    by0 = vy1 + 4
    box(cv, x0 + 3, by0, cx - 1, y1 - 4, WHITEP, 3.6)
    box(cv, cx + 1, by0, x1 - 3, y1 - 4, WHITEP, 3.4)
    cv.rect(cx - 4, by0 + 8, cx - 3, by0 + 14, STEEL, 5.6)
    cv.rect(cx + 3, by0 + 8, cx + 4, by0 + 14, STEEL, 5.6)
    box(cv, x0 + 8, by0 + 24, x0 + 22, by0 + 29, WHITEP, 4.8, edge=False)     # una etiqueta
    for x in range(x0 + 9, x0 + 21, 2):
        cv.put(x, by0 + 26, DARK, 1.6)
    foot_shadow(cv, x0 - 2, x1 + 2, FLOOR_Y + 1, 4, 0.7)


# ─── L'escriptori i les fitxes ──────────────────────────────────────────────

def desk(cv):
    x0, top, x1 = DESK
    # escriptori metàl·lic amb calaixos a la dreta, fusta al sobre
    box(cv, x1 - 24, top + 3, x1 - 2, FLOOR_Y - 1, STEEL, 3.4, grad=0.6)
    for i in range(3):
        box(cv, x1 - 22, top + 6 + i * 12, x1 - 4, top + 15 + i * 12, STEEL, 3.8)
        cv.rect(x1 - 15, top + 9 + i * 12, x1 - 11, top + 10 + i * 12, STEEL, 6.0)
    cv.rect(x0 + 2, top + 3, x0 + 4, FLOOR_Y - 1, STEEL, 3.0)               # pota
    cv.rect(x0, top, x1, top + 3, TEAK, 4.4)
    cv.hline(x0, x1, top, TEAK, 5.4)
    cv.hline(x0, x1, top + 3, TEAK, 2.0)
    cv.darken(x0 + 5, top + 4, x1 - 25, top + 7, 0.6)
    foot_shadow(cv, x0, x1, FLOOR_Y + 1, 4, 0.6)
    # la cadira, ficada sota l'escriptori
    cv.rect(x0 + 14, top + 12, x0 + 40, top + 14, CAB, 3.2)
    cv.vline(x0 + 27, top + 15, FLOOR_Y - 4, CAB, 2.4)
    cv.hline(x0 + 18, x0 + 36, FLOOR_Y - 3, CAB, 2.6)


def files(cv):
    """L'arxivador de fitxes: una calaixera verda de dos calaixos, amb portaetiquetes de llautó."""
    x0, y0, x1, y1 = FITXES
    box(cv, x0, y0, x1, y1, FILEG, 3.6, grad=0.8)
    cv.hline(x0 + 1, x1 - 1, y0 + 1, FILEG, 5.0)
    for i in range(2):
        for j in range(2):
            dx0 = x0 + 3 + j * ((x1 - x0) // 2)
            dx1 = dx0 + (x1 - x0) // 2 - 5
            dy0 = y0 + 4 + i * 13
            box(cv, dx0, dy0, dx1, dy0 + 10, FILEG, 4.0)
            mx = (dx0 + dx1) // 2
            box(cv, mx - 5, dy0 + 2, mx + 5, dy0 + 5, BRASS, 3.6)
            cv.hline(mx - 4, mx + 4, dy0 + 3, WHITEP, 4.6)
            cv.rect(mx - 3, dy0 + 7, mx + 3, dy0 + 8, BRASS, 4.0)
    # una fitxa a sobre, i un llapis
    cv.poly([(x0 + 6, y0 - 1), (x0 + 20, y0 - 1), (x0 + 22, y0 - 3), (x0 + 8, y0 - 3)], WHITEP, 4.8)
    cv.line(x0 + 26, y0 - 2, x0 + 34, y0 - 4, YELL, 4.4)
    # el flexo
    lx = 208
    cv.rect(lx - 4, DESK[1] - 2, lx + 3, DESK[1] - 1, CAB, 3.0)
    cv.line(lx, DESK[1] - 2, lx - 3, DESK[1] - 18, CAB, 3.4)
    cv.line(lx - 3, DESK[1] - 18, lx - 10, DESK[1] - 24, CAB, 3.4)
    cv.poly([(lx - 14, DESK[1] - 24), (lx - 6, DESK[1] - 28), (lx - 4, DESK[1] - 22), (lx - 10, DESK[1] - 20)], SEAG, 3.4)
    # el walkie a carregar, al costat
    box(cv, x1 + 2, DESK[1] - 9, x1 + 6, DESK[1] - 1, CAB, 2.6)
    cv.vline(x1 + 3, DESK[1] - 13, DESK[1] - 9, CAB, 2.0)
    cv.flat(x1 + 5, DESK[1] - 7, (90, 255, 120))


# ─── La llitera de rescat ───────────────────────────────────────────────────

def stretcher(cv):
    """Llitera de rescat de cistella (travessers d'acer, malla i corretges) sobre un bastidor fix."""
    x0, x1 = LL_X0, LL_X1
    # bastidor: dues potes en H a cada punta i una barra baixa
    for px in (x0 + 10, x1 - 10):
        vpipe(cv, px - 4, LL_BOT, FLOOR_Y + 5, 1, STEEL, 3.8)
        vpipe(cv, px + 4, LL_BOT, FLOOR_Y + 5, 1, STEEL, 3.2)
        box(cv, px - 7, FLOOR_Y + 4, px + 7, FLOOR_Y + 6, STEEL, 3.0)
    hpipe(cv, x0 + 10, x1 - 10, FLOOR_Y - 4, 1, STEEL, 3.4)
    floor_shadow(cv, (x0 + x1) // 2, FLOOR_Y + 7, (x1 - x0) // 2 + 4, 4, 0.75)
    # el matalasset, que sobresurt per dalt (perspectiva)
    cv.poly([(x0 + 6, LL_TOP), (x1 - 6, LL_TOP), (x1 - 2, LL_RAIL), (x0 + 2, LL_RAIL)], PAD,
            lambda x, y: 4.2 + (y - LL_TOP) * 0.08)
    cv.hline(x0 + 6, x1 - 6, LL_TOP, PAD, 5.4)
    # el coixí
    cv.disc(x0 + 20, LL_TOP + 1, 12, 4, WHITEP, lambda nx, ny: 4.6 - ny * 1.0 - nx * 0.3)
    # el costat de la cistella: malla
    for y in range(LL_RAIL, LL_BOT + 1):
        for x in range(x0, x1 + 1):
            if (x + y) % 3 == 0 or (x - y) % 3 == 0:
                cv.put(x, y, STEEL, 3.4 - (y - LL_RAIL) * 0.06)
            else:
                cv.put(x, y, PAD, 2.2 - (y - LL_RAIL) * 0.05)
    # els tubs de dalt i de baix i els travessers
    hpipe(cv, x0, x1, LL_RAIL, 2, STEEL, 4.8)
    hpipe(cv, x0 + 4, x1 - 4, LL_BOT, 1, STEEL, 3.8)
    for tx in range(x0 + 8, x1 - 4, 16):
        vpipe(cv, tx, LL_RAIL + 2, LL_BOT, 1, STEEL, 4.4)
        bolt(cv, tx - 1, LL_RAIL + 1, STEEL, 5.0)
    # els caps, arrodonits
    for cx, s in ((x0, -1), (x1, 1)):
        for y in range(LL_RAIL - 1, LL_BOT + 1):
            t = (y - LL_RAIL) / (LL_BOT - LL_RAIL)
            xx = cx - s * round(4 * t * t)
            cv.put(xx, y, STEEL, 4.2)
            cv.put(xx + s, y, STEEL, 2.8)
    # corretges taronja amb sivelles
    for sx in (x0 + 44, x0 + 92):
        cv.rect(sx, LL_TOP + 1, sx + 4, LL_BOT + 2, ORANGE, lambda x, y: 3.6 - (y - LL_TOP) * 0.04)
        box(cv, sx - 1, LL_RAIL + 4, sx + 5, LL_RAIL + 7, STEEL, 5.0)
    cv.rect(x1 - 18, LL_BOT + 2, x1 - 14, LL_BOT + 12, ORANGE, 3.2)          # una que penja
    # la placa: «RESCAT»
    box(cv, x0 + 120, LL_BOT - 9, x0 + 120 + text_width('RESCAT') + 5, LL_BOT - 2, YELL, 4.0)
    text(cv, 'RESCAT', x0 + 123, LL_BOT - 8, None, 0, flat=(30, 24, 8))


def sense_travesser(cv):
    """La llitera sense un dels travessers d'acer: la malla segueix, amb els dos forats dels cargols buits."""
    tx = TRAVESSER
    for y in range(LL_RAIL + 3, LL_BOT - 1):
        for x in range(tx - 1, tx + 2):
            if (x + y) % 3 == 0 or (x - y) % 3 == 0:
                cv.put(x, y, STEEL, 3.4 - (y - LL_RAIL) * 0.06)
            else:
                cv.put(x, y, PAD, 2.2 - (y - LL_RAIL) * 0.05)
    # els tubs de dalt i de baix, refets on hi havia el cargol i el peu del travesser
    for x in range(tx - 2, tx + 3):
        for y in range(LL_RAIL - 2, LL_RAIL + 3):
            u = (y - LL_RAIL) / 2.5
            cv.put(x, y, STEEL, 4.8 + 1.4 * (0.35 - u) - 0.6 * u * u)
    # els forats buits i l'acer net, més clar, on hi havia les abraçadores
    for y in (LL_RAIL + 1, LL_BOT):
        cv.put(tx - 1, y, STEEL, 6.4)
        cv.put(tx + 1, y, STEEL, 6.0)
        cv.put(tx, y, DARK, 0.4, lit=0)
    cv.put(tx, LL_RAIL + 2, STEEL, 6.2)


def mantes(cv):
    """Escenes 7–8: dues mantes de llana sobre la llitera on seu la Juana (a la capa del davant, amb el FRONT):
    una de grisa estesa a la falda que penja per sobre del tub, i una de vermella per les espatlles."""
    sx, sy = JUANA
    top = LL_TOP

    def plecs(x, y, base):
        return base + 0.4 * math.sin(x * 0.55 + y * 0.12) + (hr(x // 2, y // 3, 5) - 0.5) * 0.3

    # la grisa: estesa al matalasset al voltant de la falda i caient per davant, amb la vora ondulada
    hem = lambda x: LL_RAIL + 8 + round(2 * math.sin(x * 0.45) + 1.5 * math.sin(x * 0.13 + 1))

    def gris(x, y):
        if y < LL_RAIL:                                                 # damunt del matalasset, de pla: clara
            return 5.0 - (y - top) * 0.06 + 0.5 * math.sin(x * 0.4 + y * 0.5) + (hr(x // 2, y // 3, 5) - 0.5) * 0.3
        return 4.2 - (y - LL_RAIL) * 0.1 + 0.9 * math.sin(x * 0.45) + (hr(x // 2, y // 3, 6) - 0.5) * 0.3   # plecs que cauen

    pts = [(sx - 26, top + 1), (sx - 16, sy - 37), (sx + 2, sy - 39), (sx + 16, top - 1), (sx + 24, top + 2)]
    pts += [(sx + 26, LL_RAIL + 1)] + [(x, hem(x)) for x in range(sx + 23, sx - 30, -2)] + [(sx - 29, LL_RAIL)]
    cv.poly(pts, WOOLG, gris)
    cv.hline(sx - 25, sx + 23, LL_RAIL - 1, WOOLG, 3.0)                 # el caire del tub, a sota
    for x in range(sx - 28, sx + 24):                                  # les dues ratlles fosques de la vora
        cv.put(x, hem(x) - 2, WOOLG, 2.2)
        cv.put(x, hem(x) - 4, WOOLG, 2.4)
        cv.put(x, hem(x) + 1, DARK, 1.0)
    cv.line(sx + 25, LL_RAIL + 1, sx + 23, hem(sx + 23), WOOLG, 2.6)      # la caiguda del cantó
    # la vermella: per les espatlles, tancada al davant (la Juana mira a l'esquerra) fins a la falda
    pts = [(sx - 5, sy - 57), (sx + 1, sy - 59), (sx + 7, sy - 57), (sx + 10, sy - 50), (sx + 11, sy - 42),
           (sx + 13, sy - 35), (sx + 4, sy - 33), (sx - 8, sy - 34), (sx - 14, sy - 36), (sx - 14, sy - 42),
           (sx - 10, sy - 46), (sx - 7, sy - 52)]
    cv.poly(pts, WOOLR, lambda x, y: plecs(x, y, 3.8 + (sx - x) * 0.05 - (y - sy + 57) * 0.03))
    for (xa, ya), (xb, yb) in ((pts[0], pts[11]), (pts[11], pts[10]), (pts[10], pts[9])):   # la vora del davant
        cv.line(xa, ya, xb, yb, WOOLR, 5.4)
    cv.line(sx - 2, sy - 50, sx - 4, sy - 38, WOOLR, 2.4)              # un plec
    cv.line(sx + 6, sy - 48, sx + 8, sy - 37, WOOLR, 2.6)
    for x in range(sx - 13, sx + 13):                                  # l'ombra damunt la grisa
        cv.put(x, sy - 33, WOOLG, 1.8)


def exam_lamp(cv):
    """Llum d'examen de braç, plegat contra la paret, sobre la llitera."""
    bx, by = 300, 46
    box(cv, bx - 4, by - 4, bx + 4, by + 4, WHITEP, 3.6)
    for i in range(18):
        cv.put(bx + 4 + i, by + 2 + i // 3, WHITEP, 3.8)
        cv.put(bx + 4 + i, by + 3 + i // 3, WHITEP, 2.4)
    for i in range(14):
        cv.put(bx + 22 - i, by + 8 + i, WHITEP, 3.6)
        cv.put(bx + 23 - i, by + 8 + i, WHITEP, 2.4)
    cv.disc(bx + 8, by + 24, 9, 4, WHITEP, lambda nx, ny: 4.4 - ny * 1.0 - nx * 0.4)
    cv.disc(bx + 8, by + 26, 6, 2, [(40, 40, 36), (120, 120, 110), (200, 200, 190)], 1.4)


def counter(cv):
    """El marbre de la dreta: pica, mirall, sabó, la cafetera dolenta, i la bombona d'oxigen."""
    x0, x1 = 384, 464
    box(cv, x0, COUNTER_Y, x1, FLOOR_Y - 1, WHITEP, 3.6, grad=0.8)
    for dx0, dx1 in ((x0 + 3, x0 + 38), (x0 + 42, x1 - 3)):
        box(cv, dx0, COUNTER_Y + 7, dx1, FLOOR_Y - 5, WHITEP, 3.4)
        cv.rect((dx0 + dx1) // 2 - 3, COUNTER_Y + 10, (dx0 + dx1) // 2 + 3, COUNTER_Y + 11, STEEL, 5.6)
    cv.rect(x0 - 2, COUNTER_Y - 3, x1 + 2, COUNTER_Y, STEEL, 4.4)
    cv.hline(x0 - 2, x1 + 2, COUNTER_Y - 3, STEEL, 6.0)
    foot_shadow(cv, x0, x1, FLOOR_Y + 1, 4, 0.6)
    # la pica i l'aixeta
    cv.rect(x0 + 6, COUNTER_Y - 3, x0 + 30, COUNTER_Y - 2, STEEL, 2.4)
    vpipe(cv, x0 + 18, COUNTER_Y - 14, COUNTER_Y - 4, 1, STEEL, 5.0)
    hpipe(cv, x0 + 18, x0 + 24, COUNTER_Y - 14, 1, STEEL, 5.0)
    cv.rect(x0 + 15, COUNTER_Y - 9, x0 + 21, COUNTER_Y - 8, STEEL, 5.0)
    # mirall
    box(cv, x0 + 6, 56, x0 + 30, 88, STEEL, 4.0)
    for y in range(58, 87):
        for x in range(x0 + 8, x0 + 29):
            cv.put(x, y, GLASSC, 3.0 + (x - x0 - 8) * 0.03 - (y - 58) * 0.02)
    for k in range(12):
        cv.flat(x0 + 10 + k // 2, 60 + k, mix(cv.get(x0 + 10 + k // 2, 60 + k), (230, 240, 244), 0.4))
    # dosificador de sabó
    box(cv, x0 + 34, 82, x0 + 40, 94, WHITEP, 4.2)
    cv.rect(x0 + 35, 88, x0 + 39, 92, [(40, 70, 40), (80, 150, 90), (140, 210, 150)], 2.0)
    # la cafetera (de goteig, vella, amb la gerra de vidre i el pilot vermell)
    cx0, cy0, cx1, cy1 = CAFE
    box(cv, cx0 + 2, cy0, cx1 - 2, cy0 + 8, CAB, 2.6)                       # cap
    box(cv, cx1 - 8, cy0 + 8, cx1 - 2, cy1, CAB, 2.4)                       # columna
    box(cv, cx0, cy1 - 3, cx1, cy1, CAB, 2.2)                               # base
    for y in range(cy0 + 12, cy1 - 3):                                      # la gerra
        for x in range(cx0 + 4, cx1 - 10):
            u = (x - (cx0 + cx1 - 6) / 2) / 8
            if y > cy0 + 17:
                cv.put(x, y, COFFEE, 2.4 - u)
            else:
                cv.put(x, y, GLASSC, 2.6 - u)
    cv.hline(cx0 + 4, cx1 - 10, cy0 + 12, GLASSC, 4.0)
    cv.rect(cx1 - 11, cy0 + 14, cx1 - 9, cy0 + 20, DARK, 1.0)               # nansa
    cv.vline(cx0 + 6, cy0 + 13, cy1 - 5, WHITEP, 4.4)                        # reflex
    cv.flat(cx1 - 5, cy0 + 4, (255, 60, 40))
    glow(cv, cx1 - 5, cy0 + 4, 5, (255, 60, 40), 0.6)
    # una tassa i un pot de sucre
    cv.rect(cx0 - 10, cy1 - 6, cx0 - 5, cy1 - 1, WHITEP, 4.0)
    cv.vline(cx0 - 4, cy1 - 5, cy1 - 3, WHITEP, 3.4)
    # prestatge: cotó, depressors, una capsa de guants
    box(cv, x0 + 40, 66, x1 - 2, 68, WHITEP, 4.0)
    box(cv, x0 + 44, 54, x0 + 56, 65, BOXES[1], 3.0)
    cv.rect(x0 + 60, 56, x0 + 66, 65, GLASSC, 3.2)
    cv.rect(x0 + 60, 58, x0 + 66, 65, WHITEP, 4.4)
    box(cv, x0 + 70, 58, x1 - 6, 65, BOXES[3], 3.2)
    # bombona d'oxigen, lligada a la paret
    ox = 470
    for y in range(80, FLOOR_Y + 2):
        for x in range(ox - 5, ox + 6):
            u = (x - ox) / 5.5
            cv.put(x, y, OXY if y > 90 else WHITEP, 3.6 + 1.4 * (-0.3 - u) - 0.8 * u * u)
    cv.disc(ox, 80, 5, 3, WHITEP, 4.2)
    box(cv, ox - 2, 72, ox + 2, 78, STEEL, 4.2)
    cv.disc(ox + 3, 73, 2, 2, STEEL, 4.8)
    for sy in (100, 130):
        cv.hline(ox - 6, ox + 6, sy, CAB, 2.4)
        cv.hline(ox - 6, ox + 6, sy + 1, CAB, 3.4)


# ─── Muntatge ───────────────────────────────────────────────────────────────

def bg(cv):
    ceiling(cv)
    wall(cv, ramp=CREAM, lvl=5.2, seed=4, rail=None)
    wear(cv, 0, 30, W - 1, 126, 16, seed=4, k=0.2)
    door(cv)
    voice_tube(cv, 62, 76)
    cabinet(cv)
    porthole(cv, 178, 54, 9, seed=4)
    desk(cv)
    files(cv)
    exam_lamp(cv)
    counter(cv)
    # una làmina: el rentat de mans (dibuixets de mans, sense text)
    box(cv, 338, 52, 362, 84, WHITEP, 4.6)
    for i in range(4):
        hx, hy = 342 + (i % 2) * 10, 57 + (i // 2) * 13
        cv.disc(hx + 3, hy + 4, 3, 4, [(56, 30, 30), (132, 82, 62), (206, 154, 116), (232, 192, 156)], 2.4)
        cv.rect(hx + 1, hy - 1, hx + 5, hy + 1, [(56, 30, 30), (132, 82, 62), (206, 154, 116), (232, 192, 156)], 2.2)
        cv.put(hx + 7, hy + 2, [(20, 60, 120), (60, 120, 200)], 1.4)
    for lx in LAMPS:
        lamp(cv, lx)
    mask = lino(cv, MEDLINO, lvl=4.2, tile=26, check=0.35, seed=4)
    foot_shadow(cv, 0, W - 1, FLOOR_Y + 1, 4, 0.4)
    foot_shadow(cv, D_PORTA[0] - 3, D_PORTA[2] + 3, FLOOR_Y + 1, 3, 0.5)
    shine(cv, mask, LAMPS, refl=0.2)
    stretcher(cv)
    for lx in LAMPS:
        lamp_glow(cv, lx)


PROPS = {'sense_travesser': sense_travesser, 'mantes': mantes,
         'ulls_dia': lambda cv: day_porthole(cv, 178, 54, 9, seed=4)}  # Escenes 2 i 3: de dia


# ─── Animacions ─────────────────────────────────────────────────────────────

def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv


def _frames_cafe():
    """La cafetera dolenta, sempre encesa: el vapor puja per davant del mirall i cau una gota a la gerra."""
    base = _base()
    cx0, cy0, cx1, cy1 = CAFE
    gx, top, surf = (cx0 + cx1 - 6) // 2, cy0 + 9, cy0 + 18                # on goteja i on és el cafè
    n, wisps = 64, 12
    frames = []
    for i in range(n):
        cv = Canvas(light=LIGHT, img=base.img.copy())
        t = i / n
        for p in range(wisps):                                             # cada fil de vapor torna a sortir quan s'esvaeix
            age = (t * 2 + p / wisps) % 1
            y = cy0 + 10 - age * 40
            x = cx0 + 1 - age * 16 + 2.2 * math.sin(age * 9 + p * 1.7)
            a = 0.75 * (1 - age) * min(1.0, age * 5)
            for dx in (0, 1):
                xx, yy = round(x) + dx, round(y)
                cv.flat(xx, yy, mix(cv.get(xx, yy), (236, 240, 240), a * (1 if dx == 0 else 0.6)))
        k = i % 32                                                         # la gota: es forma, cau i fa una rodoneta
        if k < 4:
            cv.flat(gx, top, mix(cv.get(gx, top), (90, 50, 26), 0.4 + k * 0.15))
        elif k < 9:
            y = top + (k - 3) * 2
            if y < surf:
                cv.flat(gx, y, (70, 38, 18))
        elif k < 12:
            r = k - 8
            for dx in (-r - 1, r + 1):
                cv.flat(gx + dx, surf, mix(cv.get(gx + dx, surf), (120, 76, 44), 0.6))
        frames.append(_diff(cv.img, base.img))
    return frames


def _frames_walkie():
    """El walkie es carrega: el llum verd fa pampallugues."""
    base = _base()
    x, y = FITXES[2] + 5, DESK[1] - 7
    frames = []
    for on in (True, False):
        cv = Canvas(light=LIGHT, img=base.img.copy())
        if on:
            cv.glow(x, y, 3, (90, 255, 120), 0.6)
        else:
            cv.flat(x, y, (30, 80, 44))
        frames.append(_diff(cv.img, base.img))
    return frames


ANIMS = {'cafe': {'frames': _frames_cafe, 'frameDuration': 90},
         'walkie': {'frames': _frames_walkie, 'frameDuration': 800}}

# Qui seu a la llitera (la Juana, en Bastida) hi queda darrere; el travesser que falta i les mantes van a la
# mateixa capa (són damunt del que tapa).
FRONT = {'mask': lambda x, y: LL_X0 - 2 <= x <= LL_X1 + 2 and LL_TOP - 1 <= y <= FLOOR_Y + 7,
         'baseline': 160, 'zIndex': 20, 'props': ('sense_travesser', 'mantes')}

GEOMETRIA = {
    'things': {
        'porta': {'rect': (6, 46, 52, FLOOR_Y), 'walk': (30, 178)},
        'boca': {'rect': (54, 70, 72, 104), 'walk': (64, 178)},
        'armari': {'rect': ARMARI, 'walk': (108, 178)},
        'fitxes': {'rect': (FITXES[0], FITXES[1] - 4, FITXES[2], FITXES[3]), 'walk': (176, 178)},
        'llitera': {'rect': (LL_X0 - 2, LL_TOP - 4, LL_X1 + 2, FLOOR_Y + 6), 'walk': (300, 184)},
        'cafetera': {'rect': (CAFE[0] - 2, CAFE[1] - 2, CAFE[2] + 2, CAFE[3]), 'walk': (434, 178)},
    },
    'spawns': {'iri': (424, 194), 'vet': (172, 192),
               'capitana': (300, 184), 'tomas': (300, 184), 'nadia': (300, 184), 'marcel': (300, 184),
               'bastida': (338, 150), 'juana': JUANA},
    'walkable': [(6, 168), (476, 168), (476, 197), (6, 197)],
}
