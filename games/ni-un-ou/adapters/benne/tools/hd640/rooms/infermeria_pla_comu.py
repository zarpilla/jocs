"""
**El dibuix pla de sempre** (font de les textures de la sala en 3D, infermeria.py).

Prova de resolució: la infermeria de l'Arenga a 640×360 (la composició de hd/rooms/infermeria.py ×4/3, dibuixada
de nou amb el detall que hi cap). Mateixes rampes, mateixos props, mateixa capa del davant i mateixes animacions.

  - la porta del passadís i la boca del tub de veu de llautó, amb la placa;
  - l'armari de medicaments: vitrina amb ampolles i capses etiquetades, la creu, la clau al pany;
  - l'escriptori amb l'arxivador de fitxes (portaetiquetes A-F, G-L...), el flexo, el walkie a carregar i la cadira;
  - la llitera de rescat de cistella (malla, travessers cargolats, corretges amb sivella, la placa RESCAT) sobre el
    bastidor; és FRONT: qui hi seu hi queda darrere;
  - el llum d'examen plegat, la làmina del rentat de mans, el marbre amb la pica, el mirall, la cafetera dolenta i
    la bombona d'oxigen.
"""
import math

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from hd.pix import Canvas, Light, W, H, hr, mix  # noqa: F401
from hd.rooms.arenga import CAB, DARK, WHITEP, REDP, YELL, BRASS, SEAG, box, rrect, bolt, hpipe, vpipe, glow
from hd.rooms.comu import _diff, text, text_width
from hd.rooms.principal import (CREAM, TEAK, NIGHT, DAYSKY, DAYSEA, sill, porthole, day_porthole, foot_shadow,
                                floor_shadow, wear)
from hd.rooms.infermeria import STEEL, MEDLINO, FILEG, ORANGE, PAD, GLASSC, COFFEE, OXY, BOXES, WOOLG, WOOLR
from hd640.rooms.laboratori_pla_comu import ceiling, lamp, lamp_glow, shine, door_frame
from hd640.rooms.menjador_pla_comu import wall, leaf

from hd.pix import Canvas  # noqa: E402,F811  (a 1×: és la font de les textures de la sala en 3D)
Canvas1x = Canvas

S = 4 / 3
CEIL_H = 24
FLOOR_Y = 203
BOTTOM = 260                          # per sota hi ha la barra de verbs
LAMP_Y = 27
LAMPS = (149, 395, 573)
VP = (320, 40)

LIGHT = Light(ambient=-0.25, vignette=(59, 32), floor_fade=(251, 53))
for _x in LAMPS:
    LIGHT.point(_x, LAMP_Y + 8, r=165, k=2.3, squash=1.1, down=True, power=1.5)

D_PORTA = (13, 85, 64, FLOOR_Y)
VOICE = (83, 101)                     # la boca del tub de veu
ARMARI = (109, 53, 179, FLOOR_Y - 1)
PORT = (237, 72, 12)                  # l'ull de bou: centre i radi del vidre
DESK = (192, 149, 285)                # x0, y del sobre, x1
FITXES = (203, 109, 267, 148)
LL_X0, LL_X1 = 301, 499               # la llitera
LL_TOP, LL_RAIL, LL_BOT = 155, 165, 184
CAFE = (557, 115, 600, 149)
COUNTER = (512, 619)
COUNTER_Y = 149
JUANA = (424, 200)                    # on seu la Juana (peus; el FRONT de la llitera li tapa les cames)
TRAV_X = [x for x in range(LL_X0 + 11, LL_X1 - 5, 21)]
TRAVESSER = TRAV_X[3]                 # el travesser que en Bastida s'emporta (decorat `sense_travesser`)
INK = (30, 26, 24)
_VT = {'chain': True}                 # la cadeneta del tub de veu (l'animació `cadeneta` la dibuixa a part)


def P(v):
    return round(v * S)


# ─── Terra ──────────────────────────────────────────────────────────────────

def lino(cv, lvl=4.2, tile=35, check=0.35, seed=4):
    """Linòleum gris verdós de rajoles en perspectiva, a escacs suaus. → màscara del terra."""
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
            cv.put(x, y, MEDLINO, lv)
            mask[y][x] = True
    cv.hline(0, W - 1, FLOOR_Y, MEDLINO, lvl - 1.6)
    return mask


# ─── Porta i tub de veu ─────────────────────────────────────────────────────

def door(cv):
    x0, y0, x1, y1 = D_PORTA
    leaf(cv, x0, y0, x1, y1 - 7, WHITEP, 3.7, handle='right', seed=8)
    door_frame(cv, x0, y0, x1, y1)
    sill(cv, x0, x1, y1, h=7)
    # un penjador amb un estetoscopi vell (de quan hi havia metge)
    hx, hy = x0 + 11, y0 + 12
    cv.rect(hx - 3, hy - 1, hx + 3, hy + 1, BRASS, 3.8)
    cv.put(hx + 3, hy - 2, BRASS, 5.0)
    # les olives, els dos tubs de metall que s'ajunten i el tub de goma que baixa fins a la campana
    cv.put(hx - 4, hy + 2, DARK, 1.2)
    cv.put(hx + 4, hy + 2, DARK, 1.2)
    cv.line(hx - 4, hy + 3, hx - 1, hy + 12, STEEL, 4.6)
    cv.line(hx + 4, hy + 3, hx + 1, hy + 12, STEEL, 4.2)
    for i in range(16):
        cv.put(hx + round(math.sin(i * 0.35) * 2), hy + 13 + i, DARK, 1.8)
    cv.disc(hx + 1, hy + 31, 2.5, 2.5, STEEL, lambda nx, ny: 5.0 - nx - ny)
    # el rètol de la porta
    box(cv, x0 + 8, y0 - 15, x1 - 8, y0 - 6, WHITEP, 4.2)
    text(cv, 'PASS', x0 + 18, y0 - 13, None, 0, flat=INK)


def voice_tube(cv, cx, y, top=0, label=True):
    """La boca del tub de veu (principal.voice_tube a 640): tub de llautó, colze, campana i la placa gravada.
    La cadeneta amb la tapa només hi és si _VT['chain'] (l'animació la dibuixa a part)."""
    vpipe(cv, cx, top, y - 5, 3, BRASS, 3.0)
    for by in range(top + 35, y - 11, 53):
        box(cv, cx - 4, by, cx + 4, by + 3, CAB, 3.4)
        cv.put(cx - 3, by + 1, CAB, 5.0)
    cv.disc(cx, y, 5, 5, BRASS, lambda nx, ny: 3.4 - nx * 1.2 - ny * 1.0)
    cv.disc(cx, y + 5, 9, 8, BRASS, lambda nx, ny: 3.7 - nx * 1.3 - ny * 1.2)
    cv.disc(cx, y + 5, 7, 6, BRASS, lambda nx, ny: 1.4 + nx * 0.6 + ny * 0.8)
    cv.disc(cx, y + 6, 4, 3, DARK, 0.6)
    cv.put(cx - 5, y + 1, BRASS, 5.6)                                # brillantor de la vora
    cv.put(cx - 4, y, BRASS, 5.2)
    if _VT['chain']:
        _chain(cv, cx, y, 0)
    if label:
        box(cv, cx - 10, y + 32, cx + 10, y + 37, BRASS, 3.0)
        cv.hline(cx - 9, cx + 9, y + 33, BRASS, 4.2)
        for x in range(cx - 8, cx + 9, 2):
            if hr(x, 3) > 0.25:
                cv.put(x, y + 35, BRASS, 1.2)
        cv.put(cx - 9, y + 34, BRASS, 5.0)
        cv.put(cx + 9, y + 34, BRASS, 5.0)


def _chain(cv, cx, y, ang):
    """La cadeneta i la tapa, penjades de (cx + 6, y + 14) i girades `ang` graus (+ cap a la dreta)."""
    px, py = cx + 6, y + 14
    a = math.radians(ang)

    def at(dx, dy):
        return px + dx * math.cos(a) - dy * math.sin(a), py + dx * math.sin(a) + dy * math.cos(a)
    for i in range(10):                                              # anelles: una clara, una fosca
        x, yy = at((i % 2) - 0.5, i)
        cv.put(round(x), round(yy), BRASS, 3.8 if i % 2 else 2.4)
    tx, ty = at(2, 13)
    cv.disc(tx, ty, 4, 2.5, BRASS, lambda nx, ny: 4.2 - nx - ny * 0.8)
    cv.put(round(tx - 2), round(ty - 1), BRASS, 5.6)


# ─── L'armari de medicaments ────────────────────────────────────────────────

def _vial(cv, x, sy, kind, h, w, i):
    if kind == 0:                                                     # ampolla marró (iode), amb coll i etiqueta
        cv.rect(x, sy - h, x + w - 1, sy, [(30, 14, 6), (70, 34, 12), (120, 64, 24), (170, 110, 50)],
                lambda xx, yy: 2.6 - (xx - x) * 0.2)
        cv.rect(x + 1, sy - h - 3, x + w - 2, sy - h - 1, WHITEP, 3.8)
        cv.rect(x + 1, sy - h + 3, x + w - 2, sy - h + 6, WHITEP, 4.6)
        cv.vline(x + 1, sy - h, sy - 1, [(120, 64, 24), (220, 170, 110)], 1.4)
    elif kind == 1:                                                   # pot blanc amb tap blau
        cv.rect(x, sy - h + 3, x + w, sy, WHITEP, lambda xx, yy: 4.2 - (xx - x) * 0.15)
        cv.rect(x, sy - h + 1, x + w, sy - h + 3, BOXES[1], 2.6)
        cv.hline(x + 1, x + w - 1, sy - h // 2, REDP, 3.6)
    else:                                                             # capsa amb una franja i un text de ratlles
        b = BOXES[int(hr(i, kind, 9) * 5)]
        cv.rect(x, sy - h, x + w + 1, sy, b, 2.8)
        cv.vline(x, sy - h, sy, b, 3.6)
        cv.hline(x, x + w + 1, sy - h, b, 3.6)
        cv.hline(x + 1, x + w, sy - h + 3, WHITEP, 4.4)
        if w > 3:
            cv.put(x + 2, sy - h + 6, DARK, 1.6)
            cv.put(x + 4, sy - h + 6, DARK, 1.6)


def cabinet(cv):
    """Armari metàl·lic blanc: la creu al capdamunt, vitrina amb pots i capses, portes cegues amb etiquetes."""
    x0, y0, x1, y1 = ARMARI
    box(cv, x0, y0, x1, y1, WHITEP, 3.9, grad=0.6)
    cv.vline(x0 + 1, y0 + 1, y1 - 1, WHITEP, 4.8)
    cv.hline(x0 + 1, x1 - 1, y0 + 1, WHITEP, 5.0)
    cx = (x0 + x1) // 2
    # la creu vermella, amb un filet blanc
    cv.rect(cx - 3, y0 + 3, cx + 3, y0 + 17, REDP, 4.2)
    cv.rect(cx - 9, y0 + 7, cx + 9, y0 + 13, REDP, 4.2)
    cv.vline(cx - 3, y0 + 3, y0 + 17, REDP, 5.2)
    cv.hline(cx - 9, cx + 9, y0 + 7, REDP, 5.2)
    # vitrina
    vx0, vy0, vx1, vy1 = x0 + 4, y0 + 22, x1 - 4, y0 + 89
    for y in range(vy0, vy1 + 1):
        for x in range(vx0, vx1 + 1):
            cv.put(x, y, GLASSC, 2.0 + (vy1 - y) * 0.008)
    shelves = (vy0 + 22, vy0 + 44, vy1 - 1)
    for sy in shelves:
        cv.hline(vx0, vx1, sy, WHITEP, 3.6)
        cv.hline(vx0, vx1, sy + 1, WHITEP, 2.2)
    for row, sy in enumerate(s - 1 for s in shelves):
        x, i = vx0 + 2, 0
        while x < vx1 - 4:
            kind = int(hr(row, i, 6) * 4)
            h = 8 + int(hr(row, i, 7) * 9)
            w = 4 + int(hr(row, i, 8) * 4)
            if x + w > vx1 - 2:
                break
            if row == 2 and i < 2:                                    # gases i benes, rodons
                cv.disc(x + 4, sy - 4, 4, 4, WHITEP, lambda nx, ny: 4.4 - nx - ny)
                cv.ring(x + 4, sy - 4, 2, WHITEP, 3.0, step=30)
                x += 10
                i += 1
                continue
            _vial(cv, x, sy, kind, h, w, i)
            x += w + 3
            i += 1
    # marcs de les portes de vidre i reflexos
    cv.vline(cx, vy0, vy1, WHITEP, 3.4)
    cv.vline(cx + 1, vy0, vy1, WHITEP, 2.4)
    for x in (vx0, vx1):
        cv.vline(x, vy0, vy1, WHITEP, 3.6)
    cv.hline(vx0, vx1, vy0, WHITEP, 3.6)
    cv.hline(vx0, vx1, vy1, WHITEP, 3.6)
    for k in range(28):
        for gx0 in (vx0 + 7, cx + 7):
            for dx in (0, 1):
                xx, yy = gx0 + k // 2 + dx, vy0 + 3 + k
                if yy < vy1 - 3:
                    cv.flat(xx, yy, mix(cv.get(xx, yy), (220, 236, 240), 0.28))
    # nanses i el pany, amb la clau posada
    cv.rect(cx - 4, vy0 + 33, cx - 3, vy0 + 42, STEEL, 5.6)
    cv.rect(cx + 3, vy0 + 33, cx + 4, vy0 + 42, STEEL, 5.6)
    cv.disc(cx + 1, vy0 + 47, 1.5, 1.5, BRASS, 4.4)
    cv.rect(cx + 1, vy0 + 48, cx + 2, vy0 + 51, BRASS, 3.6)
    # a baix, portes cegues amb les etiquetes
    by0 = vy1 + 5
    box(cv, x0 + 4, by0, cx - 1, y1 - 5, WHITEP, 3.6)
    box(cv, cx + 2, by0, x1 - 4, y1 - 5, WHITEP, 3.4)
    cv.rect(cx - 5, by0 + 11, cx - 4, by0 + 19, STEEL, 5.6)
    cv.rect(cx + 5, by0 + 11, cx + 6, by0 + 19, STEEL, 5.6)
    for lx0, lab in ((x0 + 9, 'GASES'), (cx + 7, 'SERUM')):
        box(cv, lx0, by0 + 30, lx0 + text_width(lab) + 3, by0 + 38, WHITEP, 4.8, edge=False)
        text(cv, lab, lx0 + 2, by0 + 32, None, 0, flat=INK)
    foot_shadow(cv, x0 - 3, x1 + 3, FLOOR_Y + 1, 5, 0.7)


# ─── L'escriptori i les fitxes ──────────────────────────────────────────────

def desk(cv):
    x0, top, x1 = DESK
    box(cv, x1 - 32, top + 4, x1 - 3, FLOOR_Y - 1, STEEL, 3.4, grad=0.6)
    for i in range(3):
        dy = top + 8 + i * 16
        box(cv, x1 - 29, dy, x1 - 6, dy + 12, STEEL, 3.8)
        cv.rect(x1 - 21, dy + 4, x1 - 14, dy + 5, STEEL, 6.0)
        cv.hline(x1 - 21, x1 - 14, dy + 6, STEEL, 2.0)
    cv.rect(x0 + 3, top + 4, x0 + 5, FLOOR_Y - 1, STEEL, 3.0)
    cv.vline(x0 + 3, top + 4, FLOOR_Y - 1, STEEL, 4.4)
    cv.rect(x0, top, x1, top + 4, TEAK, 4.4)
    cv.hline(x0, x1, top, TEAK, 5.4)
    cv.hline(x0, x1, top + 4, TEAK, 2.0)
    for x in range(x0 + 4, x1 - 4, 7):                                 # la veta
        if hr(x, 5) > 0.5:
            cv.hline(x, x + 4, top + 2, TEAK, 3.6)
    cv.darken(x0 + 6, top + 5, x1 - 33, top + 9, 0.6)
    foot_shadow(cv, x0, x1, FLOOR_Y + 1, 5, 0.6)
    # la cadira, ficada sota l'escriptori: seient, pistó i la base de rodes
    box(cv, x0 + 18, top + 16, x0 + 53, top + 19, CAB, 3.2)
    cv.hline(x0 + 18, x0 + 53, top + 16, CAB, 4.4)
    vpipe(cv, x0 + 36, top + 20, FLOOR_Y - 6, 1, CAB, 2.6)
    cv.line(x0 + 36, FLOOR_Y - 5, x0 + 22, FLOOR_Y - 2, CAB, 2.6)
    cv.line(x0 + 36, FLOOR_Y - 5, x0 + 50, FLOOR_Y - 2, CAB, 2.6)
    for wx in (x0 + 22, x0 + 50):
        cv.disc(wx, FLOOR_Y - 1, 1.5, 1.5, DARK, 1.0)


def files(cv):
    """L'arxivador de fitxes: calaixera verda de quatre calaixos, amb portaetiquetes de llautó i les lletres."""
    x0, y0, x1, y1 = FITXES
    box(cv, x0, y0, x1, y1, FILEG, 3.6, grad=0.8)
    cv.hline(x0 + 1, x1 - 1, y0 + 1, FILEG, 5.0)
    labels = (('A-F', 'G-L'), ('M-R', 'S-Z'))
    for i in range(2):
        for j in range(2):
            dx0 = x0 + 4 + j * ((x1 - x0) // 2)
            dx1 = dx0 + (x1 - x0) // 2 - 7
            dy0 = y0 + 5 + i * 17
            box(cv, dx0, dy0, dx1, dy0 + 14, FILEG, 4.0)
            mx = (dx0 + dx1) // 2
            box(cv, mx - 8, dy0 + 2, mx + 8, dy0 + 8, BRASS, 3.6)
            cv.rect(mx - 7, dy0 + 3, mx + 7, dy0 + 7, WHITEP, 4.8)
            lab = labels[i][j]
            text(cv, lab, mx - text_width(lab) // 2, dy0 + 3, None, 0, flat=INK)
            cv.rect(mx - 4, dy0 + 10, mx + 4, dy0 + 11, BRASS, 4.0)
            cv.hline(mx - 4, mx + 4, dy0 + 12, BRASS, 1.6)
    # unes fitxes a sobre, un llapis i una tassa amb bolígrafs
    cv.poly([(x0 + 8, y0 - 1), (x0 + 27, y0 - 1), (x0 + 29, y0 - 4), (x0 + 10, y0 - 4)], WHITEP, 4.8)
    cv.poly([(x0 + 10, y0 - 4), (x0 + 28, y0 - 4), (x0 + 30, y0 - 6), (x0 + 12, y0 - 6)], WHITEP, 4.2)
    cv.hline(x0 + 13, x0 + 25, y0 - 3, DARK, 2.6)
    cv.line(x0 + 34, y0 - 2, x0 + 45, y0 - 5, YELL, 4.4)
    cv.put(x0 + 46, y0 - 5, [(60, 40, 30), (120, 90, 70)], 1.0)
    # el flexo
    lx = 277
    top = DESK[1]
    box(cv, lx - 5, top - 3, lx + 4, top - 1, CAB, 3.0)
    cv.line(lx, top - 3, lx - 2, top - 40, CAB, 3.4)                # el braç, alt: la pantalla queda sobre les fitxes
    cv.line(lx + 1, top - 3, lx - 1, top - 40, CAB, 2.2)
    cv.disc(lx - 2, top - 40, 1.5, 1.5, CAB, 4.4)
    cv.line(lx - 2, top - 40, lx - 11, top - 46, CAB, 3.4)
    cv.poly([(lx - 17, top - 46), (lx - 6, top - 51), (lx - 3, top - 43), (lx - 11, top - 40)], SEAG,
            lambda x, y: 3.6 - (y - top + 51) * 0.08)
    cv.hline(lx - 16, lx - 11, top - 41, [(40, 40, 30), (200, 190, 140)], 1.2, lit=0)
    # el walkie a carregar, a la seva base
    wx = x1 + 3
    box(cv, wx - 1, top - 3, wx + 8, top - 1, CAB, 2.2)
    box(cv, wx, top - 13, wx + 6, top - 3, CAB, 2.6)
    cv.vline(wx + 1, top - 19, top - 13, CAB, 2.0)
    cv.rect(wx + 1, top - 11, wx + 5, top - 9, [(10, 30, 20), (30, 80, 50)], 1.4)
    for gy in range(top - 7, top - 4, 2):
        cv.hline(wx + 1, wx + 5, gy, CAB, 1.2)
    cv.flat(wx + 7, top - 9, (90, 255, 120))


# ─── La llitera de rescat ───────────────────────────────────────────────────

def stretcher(cv):
    """Llitera de rescat de cistella (travessers d'acer, malla i corretges) sobre un bastidor fix."""
    x0, x1 = LL_X0, LL_X1
    for px in (x0 + 13, x1 - 13):
        vpipe(cv, px - 5, LL_BOT, FLOOR_Y + 7, 1, STEEL, 3.8)
        vpipe(cv, px + 5, LL_BOT, FLOOR_Y + 7, 1, STEEL, 3.2)
        hpipe(cv, px - 5, px + 5, FLOOR_Y - 10, 1, STEEL, 3.4)
        box(cv, px - 9, FLOOR_Y + 5, px + 9, FLOOR_Y + 8, STEEL, 3.0)
        for bx in (px - 7, px + 6):
            cv.put(bx, FLOOR_Y + 6, STEEL, 5.4)
    hpipe(cv, x0 + 13, x1 - 13, FLOOR_Y - 5, 1, STEEL, 3.4)
    floor_shadow(cv, (x0 + x1) // 2, FLOOR_Y + 9, (x1 - x0) // 2 + 5, 5, 0.75)
    # el matalasset, que sobresurt per dalt (perspectiva), amb el cosit
    cv.poly([(x0 + 8, LL_TOP), (x1 - 8, LL_TOP), (x1 - 3, LL_RAIL), (x0 + 3, LL_RAIL)], PAD,
            lambda x, y: 4.2 + (y - LL_TOP) * 0.06)
    cv.hline(x0 + 8, x1 - 8, LL_TOP, PAD, 5.4)
    for x in range(x0 + 12, x1 - 10, 3):
        cv.put(x, LL_TOP + 3, PAD, 3.4)
    # el coixí, amb un plec
    cv.disc(x0 + 27, LL_TOP + 1, 16, 5, WHITEP, lambda nx, ny: 4.6 - ny * 1.0 - nx * 0.3)
    cv.line(x0 + 20, LL_TOP, x0 + 30, LL_TOP + 2, WHITEP, 3.4)
    # la cistella: malla
    for y in range(LL_RAIL, LL_BOT + 1):
        for x in range(x0, x1 + 1):
            if (x + y) % 4 == 0 or (x - y) % 4 == 0:
                cv.put(x, y, STEEL, 3.4 - (y - LL_RAIL) * 0.05)
            else:
                cv.put(x, y, PAD, 2.2 - (y - LL_RAIL) * 0.04)
    hpipe(cv, x0, x1, LL_RAIL, 2, STEEL, 4.8)
    hpipe(cv, x0 + 5, x1 - 5, LL_BOT, 1, STEEL, 3.8)
    for tx in TRAV_X:
        vpipe(cv, tx, LL_RAIL + 3, LL_BOT, 1, STEEL, 4.4)
        bolt(cv, tx - 1, LL_RAIL + 1, STEEL, 5.0)
        cv.put(tx, LL_BOT - 1, STEEL, 5.6)
    # els caps, arrodonits
    for cx, s in ((x0, -1), (x1, 1)):
        for y in range(LL_RAIL - 1, LL_BOT + 1):
            t = (y - LL_RAIL) / (LL_BOT - LL_RAIL)
            xx = cx - s * round(5 * t * t)
            cv.put(xx, y, STEEL, 4.2)
            cv.put(xx + s, y, STEEL, 2.8)
            cv.put(xx - s, y, STEEL, 5.2)
    # corretges taronja amb sivella i el forat dels punts
    for sx in (x0 + 59, x0 + 123):
        cv.rect(sx, LL_TOP + 1, sx + 5, LL_BOT + 3, ORANGE, lambda x, y: 3.6 - (y - LL_TOP) * 0.03)
        cv.vline(sx, LL_TOP + 1, LL_BOT + 3, ORANGE, 4.6)
        box(cv, sx - 2, LL_RAIL + 5, sx + 7, LL_RAIL + 10, STEEL, 5.0)
        cv.rect(sx, LL_RAIL + 7, sx + 5, LL_RAIL + 8, ORANGE, 2.0)
        for hy in (LL_RAIL + 13, LL_RAIL + 16):
            cv.put(sx + 2, hy, ORANGE, 1.0)
    cv.rect(x1 - 24, LL_BOT + 3, x1 - 19, LL_BOT + 17, ORANGE, lambda x, y: 3.2 - (y - LL_BOT) * 0.05)   # la que penja
    box(cv, x1 - 26, LL_BOT + 15, x1 - 17, LL_BOT + 19, STEEL, 4.6)
    # la placa: «RESCAT»
    px0 = x0 + 155
    box(cv, px0, LL_BOT - 12, px0 + text_width('RESCAT') + 7, LL_BOT - 3, YELL, 4.0)
    cv.hline(px0 + 1, px0 + text_width('RESCAT') + 6, LL_BOT - 11, YELL, 5.0)
    text(cv, 'RESCAT', px0 + 4, LL_BOT - 10, None, 0, flat=(30, 24, 8))
    cv.put(px0 + 1, LL_BOT - 8, YELL, 1.6)
    cv.put(px0 + text_width('RESCAT') + 6, LL_BOT - 8, YELL, 1.6)


def sense_travesser(cv):
    """La llitera sense un dels travessers d'acer: la malla segueix, amb els dos forats dels cargols buits."""
    tx = TRAVESSER
    for y in range(LL_RAIL + 3, LL_BOT - 1):
        for x in range(tx - 1, tx + 2):
            if (x + y) % 4 == 0 or (x - y) % 4 == 0:
                cv.put(x, y, STEEL, 3.4 - (y - LL_RAIL) * 0.05)
            else:
                cv.put(x, y, PAD, 2.2 - (y - LL_RAIL) * 0.04)
    for x in range(tx - 2, tx + 3):
        for y in range(LL_RAIL - 2, LL_RAIL + 3):
            u = (y - LL_RAIL) / 2.5
            cv.put(x, y, STEEL, 4.8 + 1.4 * (0.35 - u) - 0.6 * u * u)
        cv.put(x, LL_BOT - 1, STEEL, 3.8)
    for y in (LL_RAIL + 1, LL_BOT):
        cv.put(tx - 1, y, STEEL, 6.4)
        cv.put(tx + 1, y, STEEL, 6.0)
        cv.put(tx, y, DARK, 0.4, lit=0)
    cv.put(tx, LL_RAIL + 2, STEEL, 6.2)
    cv.put(tx, LL_RAIL - 1, STEEL, 6.6)


def mantes(cv):
    """Escenes 7–8: dues mantes de llana sobre la llitera on seu la Juana (a la capa del davant, amb el FRONT):
    una de grisa estesa a la falda que penja per sobre del tub, i una de vermella per les espatlles."""
    sx, sy = JUANA
    top = LL_TOP

    def plecs(x, y, base):
        return base + 0.4 * math.sin(x * 0.42 + y * 0.09) + (hr(x // 2, y // 3, 5) - 0.5) * 0.3

    def hem(x):
        return LL_RAIL + 11 + round(2.5 * math.sin(x * 0.34) + 2 * math.sin(x * 0.1 + 1))

    def gris(x, y):
        if y < LL_RAIL:
            return 5.0 - (y - top) * 0.05 + 0.5 * math.sin(x * 0.3 + y * 0.4) + (hr(x // 2, y // 3, 5) - 0.5) * 0.3
        return 4.2 - (y - LL_RAIL) * 0.08 + 0.9 * math.sin(x * 0.34) + (hr(x // 2, y // 3, 6) - 0.5) * 0.3

    pts = [(sx - P(26), top + 1), (sx - P(16), sy - P(37)), (sx + P(2), sy - P(39)), (sx + P(16), top - 1),
           (sx + P(24), top + 2), (sx + P(26), LL_RAIL + 1)]
    pts += [(x, hem(x)) for x in range(sx + P(23), sx - P(30), -2)] + [(sx - P(29), LL_RAIL)]
    cv.poly(pts, WOOLG, gris)
    cv.hline(sx - P(25), sx + P(23), LL_RAIL - 1, WOOLG, 3.0)
    for x in range(sx - P(28), sx + P(24)):                          # les ratlles fosques de la vora i el serrell
        cv.put(x, hem(x) - 3, WOOLG, 2.2)
        cv.put(x, hem(x) - 5, WOOLG, 2.4)
        cv.put(x, hem(x) + 1, DARK, 1.0)
        if x % 2 == 0:
            cv.put(x, hem(x) + 2, WOOLG, 3.4)
    cv.line(sx + P(25), LL_RAIL + 1, sx + P(23), hem(sx + P(23)), WOOLG, 2.6)
    # la vermella: per les espatlles, tancada al davant fins a la falda
    pts = [(sx - P(5), sy - P(57)), (sx + P(1), sy - P(59)), (sx + P(7), sy - P(57)), (sx + P(10), sy - P(50)),
           (sx + P(11), sy - P(42)), (sx + P(13), sy - P(35)), (sx + P(4), sy - P(33)), (sx - P(8), sy - P(34)),
           (sx - P(14), sy - P(36)), (sx - P(14), sy - P(42)), (sx - P(10), sy - P(46)), (sx - P(7), sy - P(52))]
    cv.poly(pts, WOOLR, lambda x, y: plecs(x, y, 3.8 + (sx - x) * 0.04 - (y - sy + P(57)) * 0.025))
    for (xa, ya), (xb, yb) in ((pts[0], pts[11]), (pts[11], pts[10]), (pts[10], pts[9])):
        cv.line(xa, ya, xb, yb, WOOLR, 5.4)
    cv.line(sx - P(2), sy - P(50), sx - P(4), sy - P(38), WOOLR, 2.4)
    cv.line(sx + P(6), sy - P(48), sx + P(8), sy - P(37), WOOLR, 2.6)
    cv.line(sx + P(1), sy - P(46), sx + P(2), sy - P(36), WOOLR, 2.8)
    for x in range(sx - P(13), sx + P(13)):
        cv.put(x, sy - P(33), WOOLG, 1.8)
        cv.put(x, sy - P(33) + 1, WOOLG, 2.4)


def exam_lamp(cv):
    """Llum d'examen de braç, plegat contra la paret, sobre la llitera."""
    bx, by = 400, 61
    box(cv, bx - 5, by - 5, bx + 5, by + 5, WHITEP, 3.6)
    cv.disc(bx, by, 2, 2, STEEL, 4.6)
    for i in range(24):
        cv.put(bx + 5 + i, by + 2 + i // 3, WHITEP, 3.8)
        cv.put(bx + 5 + i, by + 3 + i // 3, WHITEP, 2.4)
    cv.disc(bx + 30, by + 10, 2, 2, STEEL, 4.4)
    for i in range(19):
        cv.put(bx + 29 - i, by + 11 + i, WHITEP, 3.6)
        cv.put(bx + 30 - i, by + 11 + i, WHITEP, 2.4)
    cv.disc(bx + 11, by + 32, 12, 5, WHITEP, lambda nx, ny: 4.4 - ny * 1.0 - nx * 0.4)
    cv.disc(bx + 11, by + 34, 8, 2.5, [(40, 40, 36), (120, 120, 110), (200, 200, 190)], 1.4)
    cv.rect(bx + 21, by + 29, bx + 25, by + 31, STEEL, 4.2)


def handwash(cv):
    """La làmina del rentat de mans: sis dibuixets de mans i una aixeta amb gotes."""
    x0, y0, x1, y1 = 448, 66, 485, 113
    box(cv, x0, y0, x1, y1, WHITEP, 4.6)
    cv.hline(x0 + 2, x1 - 2, y0 + 3, [(10, 30, 60), (30, 80, 150)], 1.6)
    cv.hline(x0 + 2, x1 - 2, y0 + 4, [(10, 30, 60), (30, 80, 150)], 1.4)
    SKIN = [(56, 30, 30), (132, 82, 62), (206, 154, 116), (232, 192, 156)]
    for i in range(6):
        hx, hy = x0 + 5 + (i % 2) * 16, y0 + 9 + (i // 2) * 13
        cv.disc(hx + 5, hy + 5, 4, 4, SKIN, lambda nx, ny: 2.6 - nx * 0.5 - ny * 0.6)
        cv.rect(hx + 2, hy, hx + 7, hy + 2, SKIN, 2.4)
        cv.put(hx + 9, hy + 3, [(20, 60, 120), (60, 120, 200)], 1.4)
        cv.put(hx + 10, hy + 6, [(20, 60, 120), (60, 120, 200)], 1.2)
        cv.flat(hx, hy + 1, (80, 80, 90))                              # el número del pas, un punt
        if i % 2 == 0:
            cv.flat(hx, hy + 3, (80, 80, 90))
    for pin in ((x0 + 1, y0 + 1), (x1 - 2, y0 + 1)):
        cv.flat(pin[0], pin[1], (200, 40, 30))


def counter(cv):
    """El marbre de la dreta: pica, mirall, sabó, la cafetera dolenta, un prestatge i la bombona d'oxigen."""
    x0, x1 = COUNTER
    box(cv, x0, COUNTER_Y, x1, FLOOR_Y - 1, WHITEP, 3.6, grad=0.8)
    for dx0, dx1 in ((x0 + 4, x0 + 51), (x0 + 56, x1 - 4)):
        box(cv, dx0, COUNTER_Y + 9, dx1, FLOOR_Y - 7, WHITEP, 3.4)
        cv.rect((dx0 + dx1) // 2 - 4, COUNTER_Y + 13, (dx0 + dx1) // 2 + 4, COUNTER_Y + 14, STEEL, 5.6)
        cv.hline((dx0 + dx1) // 2 - 4, (dx0 + dx1) // 2 + 4, COUNTER_Y + 15, STEEL, 2.0)
    cv.rect(x0 - 3, COUNTER_Y - 4, x1 + 3, COUNTER_Y, STEEL, 4.4)
    cv.hline(x0 - 3, x1 + 3, COUNTER_Y - 4, STEEL, 6.0)
    cv.hline(x0 - 3, x1 + 3, COUNTER_Y, STEEL, 2.4)
    foot_shadow(cv, x0, x1, FLOOR_Y + 1, 5, 0.6)
    # la pica i l'aixeta
    cv.rect(x0 + 8, COUNTER_Y - 4, x0 + 40, COUNTER_Y - 3, STEEL, 2.4)
    cv.disc(x0 + 24, COUNTER_Y - 3, 2, 1, DARK, 0.6)
    vpipe(cv, x0 + 24, COUNTER_Y - 19, COUNTER_Y - 5, 1, STEEL, 5.0)
    hpipe(cv, x0 + 24, x0 + 32, COUNTER_Y - 19, 1, STEEL, 5.0)
    cv.put(x0 + 32, COUNTER_Y - 17, STEEL, 5.6)
    for hx in (x0 + 18, x0 + 30):
        cv.rect(hx - 2, COUNTER_Y - 9, hx + 2, COUNTER_Y - 8, STEEL, 5.0)
    cv.flat(x0 + 18, COUNTER_Y - 10, (40, 80, 200))
    cv.flat(x0 + 30, COUNTER_Y - 10, (200, 50, 40))
    # mirall
    box(cv, x0 + 8, 75, x0 + 40, 117, STEEL, 4.0)
    for y in range(77, 116):
        for x in range(x0 + 10, x0 + 39):
            cv.put(x, y, GLASSC, 3.0 + (x - x0 - 10) * 0.025 - (y - 77) * 0.015)
    for k in range(16):
        for dx in (0, 1):
            xx, yy = x0 + 13 + k // 2 + dx, 80 + k
            cv.flat(xx, yy, mix(cv.get(xx, yy), (230, 240, 244), 0.4))
    # dosificador de sabó i un tovalloler amb tovallola
    box(cv, x0 + 45, 109, x0 + 53, 125, WHITEP, 4.2)
    cv.rect(x0 + 47, 116, x0 + 51, 122, [(40, 70, 40), (80, 150, 90), (140, 210, 150)], 2.0)
    cv.rect(x0 + 48, 125, x0 + 50, 127, WHITEP, 3.0)
    hpipe(cv, x0 + 6, x0 + 42, 128, 1, STEEL, 4.6)
    cv.rect(x0 + 14, 128, x0 + 30, 144, [(20, 40, 50), (40, 80, 100), (70, 120, 140), (120, 170, 180)],
            lambda x, y: 2.6 - (y - 128) * 0.03 + (0.5 if (x - x0) % 5 == 0 else 0))
    # la cafetera (de goteig, vella, amb la gerra de vidre i el pilot vermell)
    cx0, cy0, cx1, cy1 = CAFE
    box(cv, cx0 + 3, cy0, cx1 - 3, cy0 + 11, CAB, 2.6)
    cv.hline(cx0 + 4, cx1 - 4, cy0 + 1, CAB, 4.0)
    box(cv, cx1 - 11, cy0 + 11, cx1 - 3, cy1, CAB, 2.4)
    box(cv, cx0, cy1 - 4, cx1, cy1, CAB, 2.2)
    cv.rect(cx0 + 5, cy1 - 5, cx1 - 14, cy1 - 4, STEEL, 3.6)              # la placa calenta
    for y in range(cy0 + 16, cy1 - 5):
        for x in range(cx0 + 5, cx1 - 13):
            u = (x - (cx0 + cx1 - 8) / 2) / 10
            if y > cy0 + 23:
                cv.put(x, y, COFFEE, 2.4 - u)
            else:
                cv.put(x, y, GLASSC, 2.6 - u)
    cv.hline(cx0 + 5, cx1 - 13, cy0 + 16, GLASSC, 4.0)
    cv.hline(cx0 + 5, cx1 - 13, cy0 + 24, COFFEE, 3.4)
    cv.rect(cx1 - 14, cy0 + 19, cx1 - 12, cy0 + 27, DARK, 1.0)
    cv.vline(cx0 + 7, cy0 + 17, cy1 - 7, WHITEP, 4.4)
    cv.vline(cx0 + 8, cy0 + 18, cy0 + 22, WHITEP, 3.6)
    for k in range(3):                                                   # els botons
        cv.put(cx0 + 7 + k * 4, cy0 + 6, CAB, 4.6)
    cv.flat(cx1 - 7, cy0 + 5, (255, 60, 40))
    glow(cv, cx1 - 7, cy0 + 5, 7, (255, 60, 40), 0.6)
    # una tassa amb nansa i el pot de sucre
    cv.rect(cx0 - 13, cy1 - 8, cx0 - 6, cy1 - 1, WHITEP, lambda x, y: 4.2 - (x - cx0 + 13) * 0.1)
    cv.ring(cx0 - 5, cy1 - 5, 2, WHITEP, 3.4, step=40)
    cv.hline(cx0 - 12, cx0 - 7, cy1 - 8, COFFEE, 1.6)
    cv.rect(cx0 - 24, cy1 - 10, cx0 - 16, cy1 - 1, GLASSC, 3.2)
    cv.rect(cx0 - 24, cy1 - 6, cx0 - 16, cy1 - 1, WHITEP, 4.6)
    cv.rect(cx0 - 25, cy1 - 12, cx0 - 15, cy1 - 10, REDP, 3.4)
    # prestatge: cotó, depressors, guants, un termòmetre
    box(cv, x0 + 53, 88, x1 - 3, 91, WHITEP, 4.0)
    for bx in (x0 + 58, x1 - 10):
        cv.poly([(bx, 92), (bx + 4, 92), (bx + 4, 99)], STEEL, 3.0)
    box(cv, x0 + 58, 72, x0 + 74, 87, BOXES[1], 3.0)
    cv.hline(x0 + 59, x0 + 73, 76, WHITEP, 4.6)
    cv.rect(x0 + 65, 79, x0 + 67, 84, REDP, 4.0)
    cv.rect(x0 + 64, 80, x0 + 68, 82, REDP, 4.0)
    cv.rect(x0 + 79, 74, x0 + 87, 87, GLASSC, 3.2)
    cv.rect(x0 + 79, 77, x0 + 87, 87, WHITEP, 4.4)
    for k in range(4):
        cv.vline(x0 + 80 + k * 2, 70, 76, TEAK, 4.0)
    box(cv, x0 + 92, 77, x1 - 7, 87, BOXES[3], 3.2)
    cv.hline(x0 + 93, x1 - 8, 80, WHITEP, 4.2)
    cv.disc(x0 + 100, 76, 3, 2, [(200, 220, 230), (240, 250, 255)], 1.4)   # el guant que treu el cap
    # bombona d'oxigen, lligada a la paret, amb el manòmetre i l'etiqueta O2
    ox = 627
    for y in range(107, FLOOR_Y + 2):
        for x in range(ox - 7, ox + 8):
            u = (x - ox) / 7.5
            cv.put(x, y, OXY if y > 120 else WHITEP, 3.6 + 1.4 * (-0.3 - u) - 0.8 * u * u)
    cv.disc(ox, 107, 7, 4, WHITEP, 4.2)
    box(cv, ox - 3, 96, ox + 3, 104, STEEL, 4.2)
    cv.disc(ox + 5, 97, 3, 3, STEEL, 4.8)
    cv.disc(ox + 5, 97, 2, 2, WHITEP, 5.0)
    cv.put(ox + 5, 96, DARK, 0.4)
    box(cv, ox - 5, 145, ox + 5, 153, WHITEP, 4.6, edge=False)
    text(cv, 'O2', ox - 3, 147, None, 0, flat=(20, 60, 30))
    for sy in (133, 173):
        cv.hline(ox - 8, ox + 8, sy, CAB, 2.4)
        cv.hline(ox - 8, ox + 8, sy + 1, CAB, 3.4)
        cv.put(ox - 8, sy, CAB, 4.6)


# ─── Muntatge ───────────────────────────────────────────────────────────────

def bg(cv):
    ceiling(cv)
    wall(cv, lvl=5.2, seed=4)
    wear(cv, 0, 40, W - 1, 168, 22, seed=4, k=0.2)
    door(cv)
    voice_tube(cv, *VOICE)
    cabinet(cv)
    porthole(cv, *PORT, rim=4, seed=4)
    desk(cv)
    files(cv)
    exam_lamp(cv)
    handwash(cv)
    counter(cv)
    for lx in LAMPS:
        lamp(cv, lx, LAMP_Y)
    mask = lino(cv)
    foot_shadow(cv, 0, W - 1, FLOOR_Y + 1, 5, 0.4)
    foot_shadow(cv, D_PORTA[0] - 4, D_PORTA[2] + 4, FLOOR_Y + 1, 4, 0.5)
    shine(cv, mask, LAMPS, refl=0.2)
    stretcher(cv)
    for lx in LAMPS:
        lamp_glow(cv, lx, LAMP_Y)


PROPS = {'sense_travesser': sense_travesser, 'mantes': mantes,
         'ulls_dia': lambda cv: day_porthole(cv, *PORT, seed=4)}      # Escenes 2 i 3: de dia


# ─── Animacions ─────────────────────────────────────────────────────────────

def _base(day=False):
    cv = Canvas(light=LIGHT)
    bg(cv)
    if day:
        top = Canvas(light=LIGHT, transparent=True)
        PROPS['ulls_dia'](top)
        cv.img.alpha_composite(top.img)
    return cv


def _frames_cafe():
    """La cafetera dolenta, sempre encesa: el vapor puja per davant del mirall i cau una gota a la gerra."""
    base = _base()
    cx0, cy0, cx1, cy1 = CAFE
    gx, top, surf = (cx0 + cx1 - 8) // 2, cy0 + 12, cy0 + 24
    n, wisps = 64, 14
    frames = []
    for i in range(n):
        cv = Canvas(light=LIGHT, img=base.img.copy())
        t = i / n
        for p in range(wisps):
            age = (t * 2 + p / wisps) % 1
            y = cy0 + 13 - age * 53
            x = cx0 + 1 - age * 21 + 3 * math.sin(age * 9 + p * 1.7)
            a = 0.75 * (1 - age) * min(1.0, age * 5)
            for dx, k in ((0, 1.0), (1, 0.6), (-1, 0.3)):
                xx, yy = round(x) + dx, round(y)
                cv.flat(xx, yy, mix(cv.get(xx, yy), (236, 240, 240), a * k))
        k = i % 32
        if k < 5:
            cv.flat(gx, top, mix(cv.get(gx, top), (90, 50, 26), 0.4 + k * 0.12))
        elif k < 11:
            y = top + (k - 4) * 2
            if y < surf:
                cv.flat(gx, y, (70, 38, 18))
                cv.flat(gx, y - 1, mix(cv.get(gx, y - 1), (70, 38, 18), 0.5))
        elif k < 15:
            r = k - 10
            for dx in (-r - 1, r + 1):
                cv.flat(gx + dx, surf, mix(cv.get(gx + dx, surf), (120, 76, 44), 0.6))
        frames.append(_diff(cv.img, base.img))
    return frames


def _frames_walkie():
    """El walkie es carrega: el llum verd respira (s'encén i s'apaga a poc a poc)."""
    base = _base()
    x, y = FITXES[2] + 10, DESK[1] - 9
    frames = []
    for i in range(12):
        k = 0.5 - 0.5 * math.cos(i / 12 * 2 * math.pi)
        cv = Canvas(light=LIGHT, img=base.img.copy())
        cv.flat(x, y, mix((30, 80, 44), (170, 255, 180), k))
        if k > 0.15:
            cv.glow(x, y, 8, (90, 255, 120), 0.55 * k)
        frames.append(_diff(cv.img, base.img))
    return frames


def _frames_cadeneta():
    """La tapa del tub de veu es gronxa amb el balanceig."""
    base = _base()
    _VT['chain'] = False
    try:
        clean = Canvas(light=LIGHT)
        bg(clean)
    finally:
        _VT['chain'] = True
    frames = []
    for i in range(32):
        cv = Canvas(light=LIGHT, img=clean.img.copy())
        _chain(cv, *VOICE, 9 * math.sin(i / 32 * 2 * math.pi))
        frames.append(_diff(cv.img, base.img))
    return frames


def _glass(cv, t, day):
    """El vidre de l'ull de bou, amb `t` (0..1 del bucle): l'horitzó puja i baixa i les ratlles d'onada corren."""
    cx, cy, r = PORT
    ph = t * 2 * math.pi
    hz = cy + r * 0.15 + math.sin(ph) * 1.9
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if math.hypot(x - cx, y - cy) > r:
                continue
            crest = math.sin(x * 0.55 + y * 1.8 - ph * 2)
            if day:
                if y < hz:
                    cl = hr(int((x + 28) // 6), int(y // 3), 4)
                    cv.put(x, y, DAYSKY, 4.2 + (y - (cy - r)) / (r * 2.2) * 1.4 - (0.7 if cl > 0.75 else 0), lit=0.08)
                else:
                    cv.put(x, y, DAYSEA, 4.4 - (y - hz) / (r * 0.9) + (1.2 if crest > 0.8 else 0), lit=0.08)
            else:
                if y < hz:
                    cl = hr(int(x // 5), int(y // 3), 4)
                    cv.put(x, y, NIGHT, 2.6 + (hz - y) / (r * 2) + (1.2 if cl > 0.72 else 0), lit=0.1)
                else:
                    cv.put(x, y, NIGHT, 2.4 - (y - hz) / (r * 1.6) + (3.0 if crest > 0.75 else 0), lit=0.1)
    shine_c = (236, 240, 244) if day else (200, 210, 230)
    for i in range(-r // 2, r // 3):
        x, y = cx - r // 3 + i, cy - r // 2 - i // 2
        cv.flat(x, y, mix(cv.get(x, y), shine_c, 0.35))


def _frames_port(day):
    base = _base(day).img
    frames = []
    for i in range(12):
        cv = Canvas(light=LIGHT, img=base.copy())
        _glass(cv, i / 12, day)
        frames.append(_diff(cv.img, base))
    return frames


ANIMS = {'cafe': {'frames': _frames_cafe, 'frameDuration': 90},
         'walkie': {'frames': _frames_walkie, 'frameDuration': 150},
         'cadeneta': {'frames': _frames_cadeneta, 'frameDuration': 140},
         'mar': {'frames': lambda: _frames_port(False), 'frameDuration': 220},
         'ulls_dia_mar': {'frames': lambda: _frames_port(True), 'frameDuration': 220}}

# Qui seu a la llitera (la Juana, en Bastida) hi queda darrere; el travesser que falta i les mantes van a la
# mateixa capa (són damunt del que tapa).
FRONT = {'mask': lambda x, y: LL_X0 - 3 <= x <= LL_X1 + 3 and LL_TOP - 1 <= y <= FLOOR_Y + 9,
         'baseline': 213, 'zIndex': 20, 'props': ('sense_travesser', 'mantes')}
