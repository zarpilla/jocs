"""
El passadís de la coberta principal de l'Arenga. D'esquerra (popa) a dreta (proa):
  - la porta del menjador, oberta, amb la llum càlida de dins;
  - la porta de la infermeria (blanca, amb la creu), la del laboratori i la de la Capitana (de fusta, amb el
    paperet «TRUQUEU ABANS»), cadascuna amb la placa del nom;
  - l'escala del pont, que puja pel forat del sostre (llum blavosa de dalt), i el forat de l'escala de baix, amb
    la barana i la llum verda de la sala de màquines;
  - la porta estanca de coberta, cap a proa, amb l'ull de bou i la nit a fora.
Paret crema de planxa, passamans de fusta, sòcol envernissat i linòleum.
"""
import math

from hd.pix import Canvas, Light, W, H, hr, mix
from hd.rooms.arenga import CAB, DARK, WHITEP, REDP, YELL, BRASS, SEAG, FLOOR_Y, BOTTOM, box, bolt, hpipe, vpipe, glow
from hd.rooms.principal import (CREAM, TEAK, LINO, DOORP, NIGHT, CEIL_H, wall, ceiling, lamp, lamp_glow, lino, shine,
                                unmask, foot_shadow, in_door, door_frame, sill, leaf, plaque, porthole, extinguisher,
                                sign_box, wear, day_porthole, second_hand)
from hd.rooms.comu import _diff, text

LAMPS = (110, 246, 400)
BLUEL = [(6, 10, 18), (12, 20, 34), (20, 32, 52), (32, 48, 72), (48, 68, 96), (70, 92, 122), (100, 122, 150)]
INWARM = [(20, 12, 8), (40, 26, 16), (66, 44, 28), (96, 68, 42), (130, 96, 62), (168, 128, 86), (204, 164, 116),
          (232, 200, 150)]
_ENG_GLOW = 0.35                      # la llum verda de la sala de màquines (l'anima `maquines`)
ENGG = [(4, 10, 8), (8, 18, 14), (12, 28, 22), (18, 42, 32), (28, 60, 46), (42, 84, 64)]

LIGHT = Light(ambient=-0.35, vignette=(48, 24), floor_fade=(188, 40))
for _x in LAMPS:
    LIGHT.point(_x, CEIL_H + 4, r=126, k=2.3, squash=1.1, down=True, power=1.5)
LIGHT.point(30, 120, r=46, k=0.7, power=2.0)                 # la llum del menjador, per la porta
LIGHT.point(318, 10, r=50, k=0.5, power=2.0)                 # el forat del pont

# portes: (x0, y0, x1, y1)
D_MENJ = (12, 64, 50, FLOOR_Y)
D_INF = (84, 64, 124, FLOOR_Y)
D_LAB = (156, 64, 196, FLOOR_Y)
D_CAP = (222, 64, 262, FLOOR_Y)
D_PROA = (434, 62, 470, FLOOR_Y)


# ─── Portes ─────────────────────────────────────────────────────────────────

def door_menjador(cv):
    x0, y0, x1, y1 = D_MENJ
    # a dins: la paret del menjador, càlida, amb el cantell de la taula i el llum
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if in_door(x, y, x0, y0, x1, y1):
                v = 4.0 - abs(x - 34) / 18 - (y - y0) / 80
                if y > 128:
                    v = 2.4 + (0.6 if (x + y) % 7 == 0 else 0)          # el terra de dins
                cv.put(x, y, INWARM, v, lit=0)
    cv.rect(x0, 112, x1, 115, TEAK, 4.2, lit=0.3)                      # la taula
    cv.rect(x0, 116, x1, 118, TEAK, 2.2, lit=0.3)
    for lx in (20, 42):
        cv.vline(lx, 118, 127, TEAK, 1.6, lit=0.3)
    cv.disc(30, 74, 4, 2, [(160, 120, 60), (255, 230, 170), (255, 250, 230)], 1.6, lit=0)
    glow(cv, 30, 76, 18, (255, 210, 140), 0.45)
    # la fulla, oberta contra la paret (de cantó)
    cv.poly([(x0 - 9, y0 + 4), (x0 - 3, y0 - 1), (x0 - 3, y1 - 2), (x0 - 9, y1 - 5)], DOORP, lambda x, y: 3.0 - (x0 - 3 - x) * 0.1)
    door_frame(cv, x0, y0, x1, y1)
    sill(cv, x0, x1, y1)
    plaque(cv, (x0 + x1) // 2, 50, 'MENJADOR')


def door_closed(cv, rect, ramp, lvl, label, cross=False, seed=0, handle='right'):
    x0, y0, x1, y1 = rect
    leaf(cv, x0, y0, x1, y1 - 5, ramp, lvl, handle=handle, seed=seed)
    door_frame(cv, x0, y0, x1, y1)
    sill(cv, x0, x1, y1)
    plaque(cv, (x0 + x1) // 2, 50, label, cross=cross)


def door_infermeria(cv):
    x0, y0, x1, y1 = D_INF
    door_closed(cv, D_INF, WHITEP, 3.7, 'INFERMERIA', seed=1)
    # la creu vermella a la fulla
    cx, cy = (x0 + x1) // 2 - 2, 84
    cv.rect(cx - 2, cy - 7, cx + 2, cy + 7, REDP, 4.2)
    cv.rect(cx - 7, cy - 2, cx + 7, cy + 2, REDP, 4.2)
    cv.hline(cx - 2, cx + 2, cy - 7, REDP, 5.2)
    cv.hline(cx - 7, cx + 7, cy - 2, REDP, 5.2)


def door_laboratori(cv):
    x0, y0, x1, y1 = D_LAB
    door_closed(cv, D_LAB, DOORP, 4.0, 'LABORATORI', seed=2)
    # adhesius: un peix i el de «risc biològic» (groc)
    cx, cy = (x0 + x1) // 2 - 2, 82
    cv.poly([(cx - 5, cy), (cx, cy - 5), (cx + 5, cy)], YELL, 4.2)
    cv.poly([(cx - 5, cy), (cx, cy + 5), (cx + 5, cy)], YELL, 4.2)
    cv.disc(cx, cy, 1.5, 1.5, DARK, 1.0)
    for i, (px, py) in enumerate(((cx - 6, cy + 14), )):
        cv.disc(px + 6, py, 6, 2.5, [(20, 50, 80), (40, 90, 130), (90, 150, 190), (160, 210, 230)], 2.4)
        cv.poly([(px + 12, py), (px + 16, py - 3), (px + 16, py + 3)], [(20, 50, 80), (40, 90, 130), (90, 150, 190)], 2.2)
        cv.put(px + 2, py - 1, DARK, 0)


def door_capitana(cv):
    x0, y0, x1, y1 = D_CAP
    # fulla de fusta envernissada (la Capitana té porta de fusta)
    leaf(cv, x0, y0, x1, y1 - 5, TEAK, 4.0, seed=3, louvre=False)
    for y in range(y0 + 6, y1 - 10):
        for x in range(x0 + 6, x1 - 6):
            if hr(x, y // 9, 3) > 0.86:
                cv.put(x, y, TEAK, 3.2)                              # veta
    box(cv, (x0 + x1) // 2 - 9, y1 - 22, (x0 + x1) // 2 + 7, y1 - 12, TEAK, 3.4)
    door_frame(cv, x0, y0, x1, y1)
    sill(cv, x0, x1, y1)
    plaque(cv, (x0 + x1) // 2, 50, 'CAPITANA')
    # el paperet: «TRUQUEU ABANS» i, a llapis, «I DESPRÉS NO ENTREU»
    px0, py0 = x0 + 9, 74
    box(cv, px0, py0, px0 + 20, py0 + 14, WHITEP, 4.6, edge=False)
    cv.darken(px0 + 1, py0 + 15, px0 + 21, py0 + 15, 0.6)
    for y, w, c in ((py0 + 3, 16, (40, 40, 48)), (py0 + 6, 12, (40, 40, 48)), (py0 + 10, 15, (110, 110, 120))):
        for x in range(px0 + 2, px0 + 2 + w):
            if hr(x, y) > 0.25:
                cv.flat(x, y, c)
    cv.rect(px0 + 7, py0 - 1, px0 + 12, py0, YELL, 4.6)              # cinta adhesiva


def door_proa(cv):
    x0, y0, x1, y1 = D_PROA
    leaf(cv, x0, y0, x1, y1 - 6, CREAM, 4.4, dogs=True, louvre=False, handle='left', seed=4,
         window=((x0 + x1) // 2 + 2, 86, 7, None))
    door_frame(cv, x0, y0, x1, y1, lvl=5.4)
    sill(cv, x0, x1, y1, CREAM, 3.6, h=6)
    # rètol de sortida i el cercle vermell de Mar Obert
    sign_box(cv, x0 + 1, 46, 'COBERTA', SEAG, 3.4, ink=(220, 236, 226))
    cv.disc(x0 + 26, 132, 5, 5, WHITEP, 4.6)
    cv.disc(x0 + 26, 132, 4, 4, REDP, 4.4)
    cv.disc(x0 + 26, 132, 2, 2, WHITEP, 4.6)


# ─── Les escales ────────────────────────────────────────────────────────────

def stairs_up(cv):
    """Escala de vaixell cap al pont: puja de dreta a esquerra i entra pel forat del sostre."""
    ax0, ax1 = 280, 346
    # el nínxol, més fosc
    for y in range(0, FLOOR_Y):
        for x in range(ax0, ax1 + 1):
            if y <= CEIL_H + 1 and 290 <= x <= 336:
                v = 3.2 + (CEIL_H - y) * 0.08
                cv.put(x, y, BLUEL, v, lit=0.2)                        # el pont, a dalt
            elif y > CEIL_H + 1:
                cv.put(x, y, CREAM, 3.4 + (hr(x // 3, y // 5, 9) - 0.5) * 0.25 - (0.7 if x < ax0 + 3 or x > ax1 - 3 else 0))
    cv.vline(ax0, CEIL_H, FLOOR_Y, CREAM, 5.4)
    cv.vline(ax1, CEIL_H, FLOOR_Y, CREAM, 2.0)
    cv.hline(290, 336, CEIL_H + 1, CREAM, 5.0)                        # el cantell del forat
    cv.hline(290, 336, CEIL_H + 2, CREAM, 1.8)
    for y in range(CEIL_H + 3, CEIL_H + 30):                          # llum de dalt
        for x in range(290, 337):
            k = 0.22 * (1 - (y - CEIL_H - 3) / 27)
            if k > 0:
                cv.flat(x, y, mix(cv.get(x, y), (150, 180, 220), k))
    # sòcol també al nínxol
    for y in range(128, FLOOR_Y):
        for x in range(ax0 + 1, ax1):
            cv.put(x, y, TEAK, 2.4 - (0.8 if (y - 128) % 6 == 0 else 0))
    def along(y):
        return 338 - (FLOOR_Y - y) * 0.28
    # la barana de l'altra banda, contra la paret (més fosca)
    for y in range(0, FLOOR_Y - 30):
        cv.put(round(along(y + 30)) - 15, y, CAB, 2.0)
        cv.put(round(along(y + 30)) - 14, y, CAB, 2.6)
    # el muntant del darrere
    for y in range(0, FLOOR_Y + 1):
        for dx in range(-17, -14):
            cv.put(round(along(y)) + dx, y, CAB, 2.0 + (0.6 if dx == -17 else 0))
    # graons: el pla de cada graó i el cantell groc antilliscant
    for y in range(FLOOR_Y - 9, 6, -11):
        x = round(along(y))
        cv.rect(x - 15, y, x, y + 1, CAB, 3.4)
        cv.hline(x - 15, x, y, CAB, 4.4)
        cv.rect(x - 3, y, x, y + 1, YELL, 4.2)
        cv.darken(x - 15, y + 2, x, y + 4, 0.55)
    # el muntant de davant (llisera), amb volum
    for y in range(0, FLOOR_Y + 1):
        x = round(along(y))
        for dx in range(0, 6):
            cv.put(x + dx, y, CAB, 3.6 + (1.1 if dx == 0 else 0.4 if dx == 1 else -0.8 if dx >= 4 else 0))
    # barana de davant (tub) amb els puntals
    for y in range(0, FLOOR_Y - 28):
        x = round(along(y + 30)) + 3
        cv.put(x, y, CAB, 4.6)
        cv.put(x + 1, y, CAB, 3.4)
        cv.put(x + 2, y, CAB, 2.0)
    for y in range(FLOOR_Y - 34, 0, -40):
        for t in range(0, 30):
            x = round(along(y + 30)) + 3 + round(t * 0.0)
            cv.put(round(along(y + t)) + 2, y + t, CAB, 4.0)
            cv.put(round(along(y + t)) + 3, y + t, CAB, 2.6)
    box(cv, round(along(FLOOR_Y)) - 2, FLOOR_Y - 3, round(along(FLOOR_Y)) + 8, FLOOR_Y + 1, CAB, 2.8)
    # placa
    plaque(cv, 302, 112, 'PONT')


def plan_board(cv):
    """El plànol d'emergència del vaixell, verd i blanc, emmarcat."""
    x0, y0, x1, y1 = 360, 52, 412, 88
    box(cv, x0, y0, x1, y1, CAB, 3.0)
    box(cv, x0 + 2, y0 + 2, x1 - 2, y1 - 2, WHITEP, 4.6, edge=False)
    # el casc del vaixell, de perfil
    cv.poly([(x0 + 6, y0 + 22), (x1 - 4, y0 + 22), (x1 - 10, y0 + 30), (x0 + 10, y0 + 30)], WHITEP, 3.4)
    cv.line(x0 + 6, y0 + 22, x1 - 4, y0 + 22, DARK, 1.0)
    cv.line(x1 - 4, y0 + 22, x1 - 10, y0 + 30, DARK, 1.0)
    cv.line(x0 + 6, y0 + 22, x0 + 10, y0 + 30, DARK, 1.0)
    cv.rect(x0 + 18, y0 + 14, x0 + 32, y0 + 21, WHITEP, 3.6)
    cv.hline(x0 + 18, x0 + 32, y0 + 14, DARK, 1.0)
    for x in range(x0 + 8, x1 - 8, 4):
        cv.put(x, y0 + 26, SEAG, 4.0)
    cv.rect(x0 + 34, y0 + 25, x0 + 36, y0 + 27, REDP, 4.4, lit=0.3)     # «sou aquí»
    text(cv, 'EMERGÈNCIA', x0 + 5, y0 + 6, None, 0, flat=(30, 110, 70))


def stairs_down(cv, mask):
    """El forat de l'escala de baix, arran de la paret, amb la barana i la llum verda de les màquines."""
    hx0, hx1, hy0, hy1 = 354, 414, 156, 172
    # el forat (trapezi en perspectiva)
    pts = [(hx0 + 4, hy0), (hx1 - 4, hy0), (hx1, hy1), (hx0, hy1)]
    cv.poly(pts, ENGG, lambda x, y: 1.0 + (y - hy0) * 0.06, lit=0)
    # graons que baixen (de cara), cada cop més foscos
    for i, y in enumerate(range(hy0 + 3, hy1 - 1, 4)):
        cv.hline(hx0 + 8 + i, hx1 - 8 - i, y, CAB, 2.6 - i * 0.4, lit=0.3)
        cv.hline(hx0 + 8 + i, hx1 - 8 - i, y, YELL, 2.0 - i * 0.5, lit=0.3)
    glow(cv, (hx0 + hx1) // 2, hy1 - 2, 18, (90, 200, 140), _ENG_GLOW)
    # el cantell (brazola) del forat
    cv.line(hx0, hy1, hx1, hy1, CAB, 4.0)
    cv.line(hx0, hy1 + 1, hx1, hy1 + 1, CAB, 2.0)
    cv.line(hx0 + 4, hy0, hx0, hy1, CAB, 3.2)
    cv.line(hx1 - 4, hy0, hx1, hy1, CAB, 2.6)
    # barana: puntals i dos tubs
    posts = ((hx0, hy1), (hx0 + 4, hy0), (hx1, hy1), (hx1 - 4, hy0))
    for px, py in posts:
        vpipe(cv, px, py - 30, py, 1, YELL, 3.6 if py == hy1 else 2.6)
    for dy in (30, 15):
        cv.line(hx0 + 4, hy0 - dy, hx0, hy1 - dy, YELL, 3.4)             # costats
        cv.line(hx1 - 4, hy0 - dy, hx1, hy1 - dy, YELL, 2.8)
        cv.line(hx0 + 4, hy0 - dy, hx1 - 4, hy0 - dy, YELL, 2.4)         # darrere
    hpipe(cv, hx0, hx1, hy1 - 30, 1, YELL, 3.8)                          # davant: groc
    hpipe(cv, hx0, hx1, hy1 - 15, 1, YELL, 3.2)
    for x in range(hx0 + 2, hx1 - 1, 10):                                 # ratlles negres al tub groc
        cv.rect(x, hy1 - 31, x + 3, hy1 - 29, DARK, 1.6)
    cv.darken(hx0 - 2, hy1 + 2, hx1 + 2, hy1 + 6, lambda x, y: 0.6 - (y - hy1 - 2) * 0.12)


# ─── Muntatge ───────────────────────────────────────────────────────────────

def bg(cv):
    ceiling(cv)
    wall(cv, seed=1)
    wear(cv, 0, 30, W - 1, 126, 30, seed=1, k=0.25)
    door_menjador(cv)
    extinguisher(cv, 62, 98)
    door_infermeria(cv)
    door_laboratori(cv)
    door_capitana(cv)
    stairs_up(cv)
    plan_board(cv)
    door_proa(cv)
    for lx in LAMPS:
        lamp(cv, lx)
    # un rellotge de vaixell, entre la porta del laboratori i la de la Capitana
    cv.disc(209, 80, 7, 7, BRASS, lambda nx, ny: 3.4 - nx - ny)
    cv.disc(209, 80, 5, 5, WHITEP, 4.6)
    cv.line(209, 80, 209, 76, DARK, 0)
    cv.line(209, 80, 212, 81, DARK, 0)
    mask = lino(cv, lvl=4.0, seed=1)
    for x0, _, x1, _ in (D_MENJ, D_INF, D_LAB, D_CAP, D_PROA):
        foot_shadow(cv, x0 - 3, x1 + 3, FLOOR_Y + 1, 3, 0.5)
    foot_shadow(cv, 0, W - 1, FLOOR_Y + 1, 4, 0.35)
    shine(cv, mask, LAMPS)
    before = cv.img.copy()
    stairs_down(cv, mask)
    unmask(mask, cv, 340, 120, 420, 180, before)
    for lx in LAMPS:
        lamp_glow(cv, lx)


# Escenes 2 i 3: de dia, l'ull de bou de la porta de coberta clar
PROPS = {'ulls_dia': lambda cv: day_porthole(cv, (D_PROA[0] + D_PROA[2]) // 2 + 2, 86, 7)}


# ─── Animacions ─────────────────────────────────────────────────────────────

def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv


def _frames_rellotge():
    """El rellotge del passadís: l'agulla dels segons (un fotograma per segon)."""
    base = _base()
    frames = []
    for s in range(60):
        cv = Canvas(light=LIGHT, img=base.img.copy())
        second_hand(cv, 209, 80, s)
        frames.append(_diff(cv.img, base.img))
    return frames


def _frames_maquines():
    """La llum verda de la sala de màquines, pel forat de l'escala, respira amb el motor."""
    global _ENG_GLOW
    base = _base()
    frames = []
    for i in range(12):
        _ENG_GLOW = 0.35 + 0.14 * math.sin(2 * math.pi * i / 12)
        frames.append(_diff(_base().img, base.img))
    _ENG_GLOW = 0.35
    return frames


ANIMS = {'rellotge': {'frames': _frames_rellotge, 'frameDuration': 1000},
         'maquines': {'frames': _frames_maquines, 'frameDuration': 200}}

GEOMETRIA = {
    'things': {
        'porta_menjador': {'rect': (8, 46, 54, FLOOR_Y), 'walk': (32, 178)},
        'porta_infermeria': {'rect': (80, 46, 128, FLOOR_Y), 'walk': (104, 178)},
        'porta_laboratori': {'rect': (152, 46, 200, FLOOR_Y), 'walk': (176, 178)},
        'porta_capitana': {'rect': (218, 46, 266, FLOOR_Y), 'walk': (242, 178)},
        'escala_amunt': {'rect': (282, 4, 344, FLOOR_Y), 'walk': (322, 178)},
        'escala_avall': {'rect': (350, 124, 418, 174), 'walk': (384, 184)},
        'porta_proa': {'rect': (430, 44, 474, FLOOR_Y), 'walk': (452, 178)},
    },
    'spawns': {'iri': (232, 188), 'vet': (290, 192)},
    'walkable': [(6, 168), (346, 168), (346, 178), (420, 178), (420, 168), (476, 168), (476, 197), (6, 197)],
}
