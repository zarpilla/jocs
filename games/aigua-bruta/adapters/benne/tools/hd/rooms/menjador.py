"""
El menjador de la tripulació de l'Arenga: càlid, de fusta i crema, quaranta anys de cafès, de cartes i de mapes.
  - a l'esquerra, la porta estanca de popa (a coberta, de nit); al fons, la porta de vaivé de la cuina i el
    passaplats (amb la boca del tub de veu a l'altra banda); a la dreta, la porta del passadís, oberta;
  - la taula llarga, fixada a terra, amb la barana de mar, la banqueta entapissada al darrere i el pòster de la
    «CIMERA DELS OCEANS · PORT HALLEN» patrocinada per Skarn (una balena somrient i un cotxe elèctric) a sobre;
  - dos ulls de bou amb la nit, l'aparador amb el bullidor del te, les tasses penjades i el baròmetre.
La taula és FRONT: qui seu a la banqueta (Escena 8) hi queda darrere, i la taula li tapa les cames.
"""
import math

from hd.pix import Light, W, H, hr, mix
from hd.rooms.arenga import CAB, DARK, WHITEP, REDP, YELL, BRASS, SEAG, FLOOR_Y, BOTTOM, box, rrect, bolt, hpipe, vpipe, glow
from hd.rooms.principal import (CREAM, TEAK, LINO, DOORP, NIGHT, CEIL_H, wall, ceiling, lamp, lamp_glow, lino, shine,
                                unmask, foot_shadow, floor_shadow, in_door, door_frame, sill, leaf, plaque, porthole,
                                sign_box, wear, voice_tube, day_porthole)
from hd.rooms.comu import text, text_width

LAMPS = (84, 196, 334, 434)
VINYL = [(20, 6, 6), (40, 10, 10), (64, 16, 14), (92, 24, 20), (120, 34, 26), (148, 48, 34), (176, 68, 48)]
STEEL = [(10, 12, 14), (22, 25, 28), (38, 42, 46), (58, 63, 68), (82, 88, 93), (110, 116, 120), (142, 148, 150),
         (180, 184, 186), (220, 222, 222)]
TILE = [(40, 40, 38), (80, 80, 76), (124, 122, 114), (166, 162, 150), (200, 196, 182), (226, 222, 206)]
INWARM = [(20, 12, 8), (40, 26, 16), (66, 44, 28), (96, 68, 42), (130, 96, 62), (168, 128, 86), (204, 164, 116),
          (232, 200, 150)]
SKYP = [(20, 50, 90), (40, 90, 140), (80, 140, 190), (140, 190, 225), (200, 230, 245)]
SEAP = [(6, 24, 50), (10, 44, 84), (20, 70, 120), (40, 104, 156), (80, 150, 196)]
WHALE = [(16, 22, 40), (30, 40, 66), (50, 64, 96), (76, 94, 128), (110, 130, 160), (160, 176, 200)]
CARG = [(10, 40, 20), (20, 80, 40), (40, 130, 66), (80, 180, 100), (150, 230, 160)]
MUGS = ([(30, 8, 8), (90, 20, 20), (160, 40, 34), (210, 90, 70)], [(10, 20, 40), (20, 50, 100), (50, 90, 160), (110, 150, 210)],
        [(40, 40, 40), (110, 110, 104), (190, 188, 176), (236, 234, 222)], [(40, 30, 6), (120, 90, 14), (200, 160, 40), (240, 210, 100)])

LIGHT = Light(ambient=-0.3, vignette=(46, 24), floor_fade=(188, 40))
for _x in LAMPS:
    LIGHT.point(_x, CEIL_H + 4, r=112, k=2.2, squash=1.1, down=True, power=1.5)
LIGHT.point(131, 100, r=40, k=0.5, power=2.0)                # la llum de la cuina, pel passaplats

# la taula: cantell del darrere, cantell del davant i peu
T_X0, T_X1 = 150, 378
T_BACK, T_FRONT, T_FOOT = 122, 131, 168
D_POPA = (12, 62, 50, FLOOR_Y)
D_CUINA = (66, 64, 104, FLOOR_Y)
D_PASS = (434, 64, 470, FLOOR_Y)


# ─── Portes i passaplats ────────────────────────────────────────────────────

def door_popa(cv):
    x0, y0, x1, y1 = D_POPA
    leaf(cv, x0, y0, x1, y1 - 6, CREAM, 4.4, dogs=True, louvre=False, handle='right', seed=5,
         window=((x0 + x1) // 2 - 2, 86, 7, None))
    door_frame(cv, x0, y0, x1, y1, lvl=5.4)
    sill(cv, x0, x1, y1, CREAM, 3.6, h=6)
    sign_box(cv, x0 + 1, 46, 'COBERTA', SEAG, 3.4, ink=(220, 236, 226))


def door_cuina(cv):
    """Porta de vaivé de la cuina, amb l'ull de bou (llum de dins) i la planxa d'acer a baix."""
    x0, y0, x1, y1 = D_CUINA

    def kitchen(c, x, y):
        c.put(x, y, INWARM, 6.4 - math.hypot(x - 84, y - 84) * 0.3, lit=0)
    leaf(cv, x0, y0, x1, y1 - 5, DOORP, 3.8, louvre=False, handle='left', seed=6, window=(85, 86, 7, kitchen))
    box(cv, x0 + 3, y1 - 26, x1 - 3, y1 - 8, STEEL, 4.2)                # planxa de puntades
    for x in range(x0 + 5, x1 - 4, 5):
        cv.put(x, y1 - 20, STEEL, 5.6)
    cv.darken(x1 - 7, y0 + 30, x1 - 2, y0 + 44, 0.0)
    door_frame(cv, x0, y0, x1, y1)
    sill(cv, x0, x1, y1)
    plaque(cv, (x0 + x1) // 2, 50, 'CUINA')


def passaplats(cv):
    """El passaplats: finestreta a la cuina, amb el taulell d'acer i la persiana enrotllada."""
    x0, y0, x1, y1 = 114, 86, 150, 114
    # a dins: la cuina, enrajolada i il·luminada
    for y in range(y0, y1):
        for x in range(x0, x1 + 1):
            tile = (x - x0) % 6 == 0 or (y - y0) % 6 == 0
            cv.put(x, y, TILE, 3.6 - (y - y0) * 0.03 - (1.0 if tile else 0) + 1.2 * math.exp(-((x - 132) / 14) ** 2), lit=0.4)
    # cassons penjats a dins
    for i, hx in enumerate((122, 128, 140)):
        cv.vline(hx, y0, y0 + 6 + i * 2, STEEL, 3.0, lit=0.3)
        cv.disc(hx, y0 + 9 + i * 2, 2 + (i % 2), 2, STEEL, lambda nx, ny: 4.0 - nx - ny, lit=0.3)
    # la boca del tub de veu, a l'altra banda, petita
    cv.disc(145, 100, 3, 3, BRASS, lambda nx, ny: 3.6 - nx - ny, lit=0.5)
    cv.disc(145, 100, 1.5, 1.5, DARK, 0.8, lit=0)
    cv.vline(145, y0, 97, BRASS, 3.2, lit=0.5)
    # marc d'acer, persiana a dalt i taulell
    box(cv, x0 - 3, y0 - 3, x1 + 3, y0 - 1, STEEL, 4.4)
    box(cv, x0 - 3, y0 - 9, x1 + 3, y0 - 3, STEEL, 3.2)
    for y in range(y0 - 8, y0 - 3, 2):
        cv.hline(x0 - 2, x1 + 2, y, STEEL, 4.4)
    cv.vline(x0 - 1, y0, y1, STEEL, 4.6)
    cv.vline(x0 - 2, y0, y1, STEEL, 3.0)
    cv.vline(x1 + 1, y0, y1, STEEL, 2.2)
    box(cv, x0 - 5, y1, x1 + 5, y1 + 3, STEEL, 4.8)
    cv.darken(x0 - 4, y1 + 4, x1 + 4, y1 + 6, 0.6)
    cv.vline(x0 - 1, y1 + 4, y1 + 10, STEEL, 3.0)                       # escaires
    cv.vline(x1 + 1, y1 + 4, y1 + 10, STEEL, 3.0)
    # una safata amb dues tasses al taulell
    cv.disc(126, y1 - 1, 3, 2, MUGS[2], lambda nx, ny: 3.4 - nx)
    cv.disc(138, y1 - 1, 3, 2, MUGS[0], lambda nx, ny: 2.8 - nx)


def door_passadis(cv):
    """La porta del passadís, oberta: a l'altra banda, la paret crema i el passamans."""
    x0, y0, x1, y1 = D_PASS
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if in_door(x, y, x0, y0, x1, y1):
                v = 3.0 - (y - y0) / 120 + 0.6 * math.exp(-((x - 452) / 12) ** 2)
                if y >= 128:
                    v = 1.8 if (y - 128) % 6 else 1.2
                    cv.put(x, y, TEAK, v + 0.6, lit=0.3)
                else:
                    cv.put(x, y, CREAM, v + (0.6 if x % 18 == 3 else 0), lit=0.3)
    hpipe(cv, x0, x1, 108, 1, TEAK, 3.0)
    cv.disc(452, 70, 4, 2, [(160, 120, 60), (255, 230, 170), (255, 250, 230)], 1.4, lit=0)
    glow(cv, 452, 72, 14, (255, 210, 140), 0.3)
    # la fulla, oberta contra la paret de la dreta (de cantó)
    cv.poly([(x1 + 3, y0 - 1), (x1 + 9, y0 + 4), (x1 + 9, y1 - 5), (x1 + 3, y1 - 2)], DOORP, lambda x, y: 2.4 + (x - x1) * 0.08)
    door_frame(cv, x0, y0, x1, y1)
    sill(cv, x0, x1, y1)


# ─── El pòster, els ulls de bou i l'aparador ────────────────────────────────

POSTER = (232, 24, 294, 76)


def poster(cv):
    """«CIMERA DELS OCEANS · PORT HALLEN», patrocinada per Skarn: una balena somrient i un cotxe elèctric."""
    x0, y0, x1, y1 = POSTER
    cv.darken(x0 + 2, y0 + 2, x1 + 2, y1 + 2, 0.7)
    box(cv, x0, y0, x1, y1, WHITEP, 4.8, edge=False)
    # capçalera blau marí amb el títol
    cv.rect(x0 + 2, y0 + 2, x1 - 2, y0 + 15, SEAP, 1.4)
    for i, s in enumerate(('CIMERA DELS', 'OCEANS')):
        text(cv, s, (x0 + x1 + 1) // 2 - text_width(s) // 2, y0 + 3 + i * 6, None, 0, flat=(240, 244, 248))
    # el dibuix: cel, mar, la balena i el cotxe
    ix0, iy0, ix1, iy1 = x0 + 2, y0 + 16, x1 - 2, y0 + 38
    for y in range(iy0, iy1 + 1):
        for x in range(ix0, ix1 + 1):
            if y < iy0 + 13:
                cv.put(x, y, SKYP, 3.6 - (iy0 + 13 - y) * 0.12)
            else:
                cv.put(x, y, SEAP, 3.2 - (y - iy0 - 13) * 0.15 + (0.8 if (x + y * 3) % 9 == 0 else 0))
    cv.disc(ix1 - 8, iy0 + 5, 3, 3, YELL, 5.0)                          # el sol
    # la balena, que somriu
    cv.disc(x0 + 20, iy0 + 13, 12, 6, WHALE, lambda nx, ny: 3.4 - ny * 1.4 - nx * 0.3)
    cv.poly([(x0 + 30, iy0 + 12), (x0 + 37, iy0 + 6), (x0 + 36, iy0 + 13)], WHALE, 3.0)    # cua
    cv.poly([(x0 + 31, iy0 + 11), (x0 + 37, iy0 + 15), (x0 + 30, iy0 + 15)], WHALE, 2.6)
    cv.put(x0 + 13, iy0 + 11, DARK, 0)                                  # l'ull
    for i in range(6):                                                  # el somriure
        cv.put(x0 + 10 + i, iy0 + 14 + (1 if 1 <= i <= 4 else 0), DARK, 0.5)
    for i in range(3):                                                  # el brollador
        cv.put(x0 + 19 - i, iy0 + 5 - i, SKYP, 4.8)
        cv.put(x0 + 21 + i, iy0 + 5 - i, SKYP, 4.8)
    # el cotxe elèctric, verd, amb el cable i el llamp
    cx = x1 - 22
    cv.rect(cx, iy0 + 9, cx + 15, iy0 + 13, CARG, 3.4)
    cv.rect(cx + 3, iy0 + 6, cx + 11, iy0 + 9, CARG, 3.8)
    cv.rect(cx + 5, iy0 + 7, cx + 9, iy0 + 8, SKYP, 4.4)
    for wx in (cx + 3, cx + 12):
        cv.disc(wx, iy0 + 13, 2, 2, DARK, 1.0)
    cv.line(cx + 15, iy0 + 11, cx + 18, iy0 + 15, DARK, 1.0)
    cv.poly([(cx + 7, iy0 + 1), (cx + 5, iy0 + 4), (cx + 8, iy0 + 4), (cx + 6, iy0 + 7)], YELL, 5.0)
    # peu: PORT HALLEN i el logotip de Skarn
    text(cv, 'PORT HALLEN', x0 + 3, y1 - 12, None, 0, flat=(20, 50, 90))
    cv.rect(x0 + 3, y1 - 5, x0 + 4, y1 - 3, CARG, 2.6)
    text(cv, 'SKARN', x1 - 3 - text_width('SKARN'), y1 - 7, None, 0, flat=(30, 110, 60))
    cv.poly([(x1 - 3 - text_width('SKARN') - 6, y1 - 2), (x1 - 3 - text_width('SKARN') - 4, y1 - 7),
             (x1 - 3 - text_width('SKARN') - 2, y1 - 2)], CARG, 3.4)
    # xinxetes
    for px, py in ((x0 + 1, y0 + 1), (x1 - 1, y0 + 1)):
        cv.disc(px, py, 1.5, 1.5, REDP, 4.6)


def sideboard(cv):
    """L'aparador: el bullidor del te, tasses penjades, la prestatgeria i el baròmetre."""
    x0, x1, top = 382, 426, 118
    # moble, de fusta, amb portes
    box(cv, x0, top, x1, FLOOR_Y - 1, TEAK, 3.4, grad=0.8)
    cv.rect(x0 - 2, top - 3, x1 + 2, top, TEAK, 4.4)
    cv.hline(x0 - 2, x1 + 2, top - 3, TEAK, 5.4)
    cv.rect(x0 - 2, top - 6, x0 - 1, top - 3, TEAK, 4.0)                # barana de mar
    cv.rect(x1 + 1, top - 6, x1 + 2, top - 3, TEAK, 3.0)
    cv.vline((x0 + x1) // 2, top + 4, FLOOR_Y - 4, TEAK, 1.6)
    for hx in ((x0 + x1) // 2 - 4, (x0 + x1) // 2 + 3):
        cv.rect(hx, top + 14, hx + 1, top + 18, BRASS, 4.0)
    for px0, px1 in ((x0 + 3, (x0 + x1) // 2 - 3), ((x0 + x1) // 2 + 3, x1 - 3)):
        box(cv, px0, top + 4, px1, FLOOR_Y - 5, TEAK, 3.0)
    # el bullidor (d'acer) amb l'aixeta i el pilot vermell
    bx = 394
    for y in range(top - 24, top - 3):
        for x in range(bx - 7, bx + 8):
            u = (x - bx) / 7.5
            cv.put(x, y, STEEL, 5.6 + 1.8 * (-0.3 - u) - 1.0 * u * u)
    cv.disc(bx, top - 24, 7, 2, STEEL, 6.4)
    box(cv, bx - 2, top - 28, bx + 2, top - 25, CAB, 2.6)
    cv.hline(bx - 1, bx + 2, top - 9, CAB, 3.0)
    cv.vline(bx - 1, top - 9, top - 7, CAB, 2.4)
    cv.flat(bx + 4, top - 17, (255, 70, 40))
    glow(cv, bx + 4, top - 17, 5, (255, 80, 50), 0.5)
    # tasses al costat
    for i, mx in enumerate((408, 415)):
        cv.rect(mx, top - 7, mx + 4, top - 3, MUGS[(i + 1) % 4], 3.4)
        cv.vline(mx + 5, top - 6, top - 4, MUGS[(i + 1) % 4], 2.6)
    # el penjador de tasses
    hpipe(cv, x0, x1, 80, 1, TEAK, 3.6)
    for i, mx in enumerate(range(x0 + 3, x1 - 3, 8)):
        cv.vline(mx + 2, 81, 83, BRASS, 3.2)
        m = MUGS[i % 4]
        cv.rect(mx, 84, mx + 4, 89, m, lambda x, y: 3.2 - (x - mx) * 0.2)
        cv.vline(mx + 5, 85, 87, m, 2.4)
    # prestatge: llibres, jocs de taula, una caixa de cartes
    box(cv, x0 - 2, 72, x1 + 2, 74, TEAK, 4.0)
    cv.rect(x0 - 2, 66, x0 - 1, 72, TEAK, 3.0)
    cv.rect(x1 + 1, 66, x1 + 2, 72, TEAK, 3.0)
    books = ((SEAP, 7), (VINYL, 6), (CARG, 5), (MUGS[3], 7), (WHALE, 6), (VINYL, 5))
    bx = x0 + 1
    for i, (ramp, h) in enumerate(books):
        cv.rect(bx, 72 - h - 4, bx + 2, 71, ramp, 2.8 + (0.6 if i % 2 else 0))
        cv.vline(bx, 72 - h - 4, 71, ramp, 3.8)
        bx += 4
    box(cv, bx + 2, 63, bx + 18, 71, VINYL, 3.2)                          # un joc de taula (capsa)
    box(cv, bx + 4, 58, bx + 16, 62, SEAP, 3.0)
    # el rellotge i el baròmetre, de llautó, a la paret del fons
    for cx, hand in ((196, (199, 44)), (216, (213, 41))):
        cv.disc(cx, 46, 7, 7, BRASS, lambda nx, ny: 3.4 - nx - ny)
        cv.disc(cx, 46, 5, 5, WHITEP, 4.6)
        cv.line(cx, 46, hand[0], hand[1], DARK, 0)
        cv.put(cx, 46, BRASS, 4.0)
    cv.line(196, 46, 196, 42, DARK, 0)


# ─── La taula i la banqueta ─────────────────────────────────────────────────

def bench(cv):
    """La banqueta entapissada contra la paret, darrere la taula (només se'n veu el respatller)."""
    x0, x1, y0 = T_X0 + 6, T_X1 - 6, 104
    rrect(cv, x0, y0, x1, FLOOR_Y - 1, 3, VINYL, lambda x, y: 3.6 - (y - y0) * 0.02)
    for bx in range(x0 + 2, x1 - 4, 38):                               # capitonat
        cv.vline(bx + 36, y0 + 3, FLOOR_Y - 6, VINYL, 2.0)
        cv.vline(bx + 37, y0 + 3, FLOOR_Y - 6, VINYL, 4.2)
        cv.put(bx + 18, y0 + 12, VINYL, 1.8)
        cv.put(bx + 18, y0 + 26, VINYL, 1.8)
    cv.hline(x0 + 3, x1 - 3, y0 + 1, VINYL, 5.0)
    for i in range(10):                                                 # esquerdes del vinil
        x = x0 + 6 + int(hr(i, 1) * (x1 - x0 - 12))
        y = y0 + 6 + int(hr(i, 2) * 30)
        cv.line(x, y, x + 2, y + 1 + (i % 2), VINYL, 2.0)
    box(cv, x0 - 2, y0 - 4, x1 + 2, y0, TEAK, 4.0)                       # el cantell de fusta de dalt


def table(cv):
    """La taula llarga, fixada a terra, amb barana de mar i un faldó de fusta fins a terra."""
    floor_shadow(cv, (T_X0 + T_X1) // 2, T_FOOT + 1, (T_X1 - T_X0) // 2 + 8, 5, 0.8)
    # faldó
    for y in range(T_FRONT + 3, T_FOOT + 1):
        for x in range(T_X0 - 2, T_X1 + 3):
            panel = (x - T_X0 + 2) % 57
            v = 2.8 + (hr(x // 3, y // 8, 4) - 0.5) * 0.4 - (y - T_FRONT) * 0.012
            if panel < 2:
                v = 1.6 if panel == 0 else 3.8
            cv.put(x, y, TEAK, v)
    cv.hline(T_X0 - 2, T_X1 + 2, T_FOOT, TEAK, 1.0)
    cv.rect(T_X0 - 2, T_FOOT - 4, T_X1 + 2, T_FOOT - 1, TEAK, 2.0)       # sòcol
    # el sobre (perspectiva: el cantell del darrere és més curt)
    cv.poly([(T_X0 + 3, T_BACK), (T_X1 - 3, T_BACK), (T_X1 + 2, T_FRONT), (T_X0 - 2, T_FRONT)], TEAK,
            lambda x, y: 4.4 + (y - T_BACK) * 0.06 + (hr(x // 6, y // 2, 7) - 0.5) * 0.5)
    for i in range(14):                                                 # anelles de tasses i ratllades
        x = T_X0 + 10 + int(hr(i, 11) * (T_X1 - T_X0 - 20))
        y = T_BACK + 2 + int(hr(i, 12) * 6)
        cv.ring(x, y, 2, TEAK, 3.4, step=40) if i % 3 else cv.line(x, y, x + 4, y, TEAK, 3.6)
    # cantell del davant i barana de mar (fusta, una mica alçada)
    cv.rect(T_X0 - 2, T_FRONT, T_X1 + 2, T_FRONT + 2, TEAK, 5.0)
    cv.hline(T_X0 - 2, T_X1 + 2, T_FRONT + 3, TEAK, 1.2)
    cv.hline(T_X0 + 3, T_X1 - 3, T_BACK - 1, TEAK, 4.8)
    cv.hline(T_X0 + 3, T_X1 - 3, T_BACK - 2, TEAK, 3.4)


def table_things(cv):
    """Damunt la taula: la tetera, tasses, el sucre, una baralla i una carta nàutica doblegada."""
    # tetera (de terrissa marró)
    tx, ty = 258, 124
    cv.disc(tx, ty - 4, 6, 5, TEAK, lambda nx, ny: 4.4 - nx * 1.2 - ny * 1.2)
    cv.disc(tx, ty - 9, 2, 1, TEAK, 5.0)
    cv.line(tx + 6, ty - 5, tx + 10, ty - 8, TEAK, 4.0)
    cv.ring(tx - 7, ty - 4, 2, TEAK, 3.0, step=30)
    # tasses
    for i, (mx, my) in enumerate(((182, 126), (214, 124), (296, 126), (330, 124), (352, 127))):
        m = MUGS[i % 4]
        cv.rect(mx, my - 5, mx + 4, my, m, lambda x, y: 3.6 - (x - mx) * 0.25)
        cv.hline(mx, mx + 4, my - 5, m, 1.4)
        cv.vline(mx + 5, my - 4, my - 2, m, 2.6)
    # sucrer
    cv.disc(236, 124, 3, 3, WHITEP, lambda nx, ny: 4.4 - nx - ny)
    # una baralla de cartes, mig escampada
    for i in range(3):
        box(cv, 310 + i * 4, 127 - i, 314 + i * 4, 129 - i, WHITEP, 4.6, edge=False)
    # carta nàutica doblegada
    cv.poly([(196, 129), (206, 125), (226, 126), (218, 130)], [(60, 70, 60), (140, 150, 130), (200, 206, 186), (230, 232, 214)], 2.8)
    cv.line(206, 125, 210, 129, SEAP, 3.0)


_DAVANT = ((T_X0 - 3, T_BACK - 3, T_X1 + 3, T_FOOT + 1), (252, 112, 270, T_BACK), (178, 118, 362, T_BACK))
FRONT = {'mask': lambda x, y: any(x0 <= x <= x1 and y0 <= y <= y1 for x0, y0, x1, y1 in _DAVANT),
         'baseline': 162, 'zIndex': 20}


# ─── Muntatge ───────────────────────────────────────────────────────────────

def bg(cv):
    ceiling(cv)
    wall(cv, seed=2, rail=None)
    wear(cv, 0, 30, W - 1, 126, 24, seed=2, k=0.22)
    door_popa(cv)
    door_cuina(cv)
    passaplats(cv)
    door_passadis(cv)
    porthole(cv, 316, 54, 8, seed=1)
    porthole(cv, 352, 54, 8, seed=2)
    poster(cv)
    bench(cv)
    sideboard(cv)
    for lx in LAMPS:
        lamp(cv, lx)
    mask = lino(cv, lvl=3.8, tile=34, check=0.5, seed=2)
    for x0, _, x1, _ in (D_POPA, D_CUINA, D_PASS):
        foot_shadow(cv, x0 - 3, x1 + 3, FLOOR_Y + 1, 3, 0.5)
    foot_shadow(cv, 0, W - 1, FLOOR_Y + 1, 4, 0.35)
    foot_shadow(cv, 380, 428, FLOOR_Y + 1, 5, 0.6)
    shine(cv, mask, LAMPS)
    table(cv)
    table_things(cv)
    for lx in LAMPS:
        lamp_glow(cv, lx)



def ulls_dia(cv):
    """Escenes 2 i 3, de dia: els dos ulls de bou i el de la porta de coberta, clars."""
    day_porthole(cv, 316, 54, 8, seed=1)
    day_porthole(cv, 352, 54, 8, seed=2)
    day_porthole(cv, (D_POPA[0] + D_POPA[2]) // 2 - 2, 86, 7)


PROPS = {'ulls_dia': ulls_dia}

GEOMETRIA = {
    'things': {
        'porta_popa': {'rect': (6, 44, 54, FLOOR_Y), 'walk': (30, 176)},
        'porta_cuina': {'rect': (62, 46, 108, FLOOR_Y), 'walk': (85, 176)},
        'passaplats': {'rect': (108, 76, 156, 120), 'walk': (131, 178)},
        'poster': {'rect': POSTER, 'walk': (262, 186)},
        'taula': {'rect': (T_X0 - 2, T_BACK - 2, T_X1 + 2, T_FOOT), 'walk': (262, 186)},
        'porta_passadis': {'rect': (428, 46, 474, FLOOR_Y), 'walk': (450, 176)},
    },
    'spawns': {'iri': (420, 190), 'vet': (110, 192),
               'capitana': (176, 156), 'bastida': (210, 156), 'marcel': (244, 156), 'tomas': (280, 156),
               'juana': (314, 156), 'nadia': (348, 156)},
    'walkable': [(6, 166), (142, 166), (142, 174), (386, 174), (386, 166), (476, 166), (476, 197), (6, 197)],
}
