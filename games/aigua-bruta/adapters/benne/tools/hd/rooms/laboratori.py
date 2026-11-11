"""
Laboratori de l'Arenga (coberta principal): un laboratori de biologia marina petit, pintat de crema sobre planxa.

  - la porta estanca del passadís a l'esquerra (oberta, amb el passadís fosc al darrere);
  - un ull de bou i la carta dels punts de mostreig (el 7, encerclat de vermell);
  - el taulell de laboratori (sobre d'epoxi fosc, calaixos crema) amb la lupa binocular, la gradeta de pots,
    el llibre de peixos, i els props `portatil` (el de la Juana) i `nota`;
  - el prestatge de pots de mostres, la nevera de mostres (porta de vidre, pots etiquetats, termòmetre verd)
    i la pica petita del racó;
  - el decorat `remenat`: calaixos mal tancats, papers girats, un pot tombat.

ANIMS: `mar` (l'ull de bou de nit: balanceig i ratlles d'onada), `ulls_dia_mar` (el mateix de dia, va amb el decorat
del mateix nom, damunt d'`ulls_dia`), `portatil` (el prop: el cursor de la contrasenya i el llum de repòs),
`nevera` (el visor de la temperatura i el pilot) i `bombolla` (un pot de la gradeta amb una mostra viva).

També hi ha les peces comunes de la coberta principal (paret crema, sostre, llums, porta estanca, ull de bou,
linòleum), que fa servir la cabina de la Capitana.
"""
import math

from hd.pix import Canvas, Light, W, H, hr, mix, B4  # noqa: F401
from hd.rooms.arenga import (box, rrect, bolt, hpipe, vpipe, glow, CAB, DARK, WHITEP, REDP, YELL, BRASS,
                             WARM, FLOOR_Y, BOTTOM)

from hd.rooms.principal import (CREAM, TEAK, LINO, DOORP, wall, ceiling as _ceiling, lamp as _lamp,
                               lamp_glow as _lamp_glow, lino, shine, foot_shadow, door_frame, sill,
                               porthole as _porthole, day_porthole, NIGHT, DAYSKY, DAYSEA)

# ─── Rampes (les de paret, fusta i terra vénen de principal.py, com la resta de la coberta) ─────
LINO_RED = LINO
SOCOL = [(12, 14, 14), (22, 26, 26), (34, 40, 38), (48, 56, 52), (64, 74, 68), (82, 94, 86), (102, 114, 104),
         (124, 136, 124)]
EPOXY = [(8, 10, 12), (14, 18, 20), (22, 28, 30), (32, 40, 42), (44, 54, 56), (60, 72, 72), (82, 96, 94)]
SEA = [(4, 8, 16), (8, 16, 30), (14, 26, 44), (22, 38, 60), (34, 54, 80), (52, 76, 104)]
GLASSB = [(10, 18, 22), (18, 30, 36), (28, 46, 52), (42, 66, 72), (62, 92, 96), (96, 130, 132), (150, 180, 180)]
PAPERC = [(70, 66, 58), (120, 114, 100), (170, 164, 146), (210, 204, 186), (236, 232, 216), (250, 248, 238)]
BLUEB = [(8, 14, 30), (14, 26, 54), (24, 42, 84), (38, 62, 116), (60, 90, 150), (100, 130, 186)]
GREENS = [(4, 26, 14), (10, 60, 30), (30, 120, 60), (80, 200, 110), (170, 250, 190)]
SKIN = [(56, 30, 30), (92, 52, 44), (132, 82, 62), (172, 118, 86)]

LAMPS = ((150, 22), (362, 22))

LIGHT = Light(ambient=0.5, vignette=(60, 26), floor_fade=None)
LIGHT.point(150, 26, r=170, k=2.4, squash=1.05, down=True, power=1.5)
LIGHT.point(362, 26, r=160, k=2.2, squash=1.05, down=True, power=1.5)
LIGHT.point(220, 100, r=60, k=0.5, power=2.0)                 # la pantalla del portàtil (poqueta)


# ─── Peces comunes de la coberta principal ─────────────────────────────────

def cream_wall(cv, dado=128, rail=108, seed=2):
    """La paret de la coberta principal (principal.wall): crema, quadernes, sòcol i passamans de teca."""
    if dado is not None and dado >= FLOOR_Y:
        dado, rail = None, None
    wall(cv, dado=dado, rail=rail, seed=seed)


def ceiling(cv):
    _ceiling(cv)


def lamps(cv, pos=LAMPS):
    for lx, _ in pos:
        _lamp(cv, lx)


def lamp_glow(cv, pos=LAMPS):
    for lx, _ in pos:
        _lamp_glow(cv, lx)


def linoleum(cv, ramp=LINO, lvl=4.0, tile=None, check=0.0, lamps=LAMPS, seed=2):
    """El linòleum de la coberta (principal.lino), amb l'ombra al peu de la paret i la brillantor dels llums."""
    mask = lino(cv, ramp, lvl=lvl, tile=tile, check=check, seed=seed)
    foot_shadow(cv, 0, W - 1, FLOOR_Y + 1, 4, 0.35)
    shine(cv, mask, [lx for lx, _ in lamps])
    return mask


def watertight_door(cv, x0=14, y0=66, x1=56, y1=FLOOR_Y, beyond=None, leaf_ramp=DOORP, leaf_lvl=3.6):
    """La porta del passadís, oberta: marc i llindar com les de principal.py, la fulla contra la paret i, a
    l'altra banda, el passadís (crema i linòleum vermell, amb un llum)."""
    if beyond:
        beyond(cv, x0, y0, x1, y1)
    else:
        cx = (x0 + x1) // 2
        for y in range(y0, y1):
            for x in range(x0, x1 + 1):
                cv.put(x, y, CREAM, 3.4 - abs(x - cx) / 24 - (y - y0) / 90, lit=0.25)
        cv.rect(x0, y1 - 18, x1, y1 - 12, TEAK, 2.6, lit=0.25)              # el sòcol de teca del passadís
        cv.rect(x0, y1 - 11, x1, y1 - 1, LINO, lambda x, y: 2.6 + (y - y1 + 11) * 0.12, lit=0.2)
        cv.disc(cx, y0 + 10, 4, 1.5, [(120, 100, 60), (220, 190, 130)], 1.4, lit=0)
        glow(cv, cx, y0 + 12, 14, (230, 200, 140), 0.35)
    door_frame(cv, x0, y0, x1, y1)
    sill(cv, x0, x1, y1)
    # la fulla, oberta contra la paret (de cantó)
    lx = x0 - 11
    cv.poly([(lx, y0 + 4), (x0 - 3, y0 - 1), (x0 - 3, y1 - 2), (lx, y1 - 4)], leaf_ramp,
            lambda x, y: leaf_lvl - (x - lx) * 0.06)
    cv.vline(lx, y0 + 4, y1 - 4, leaf_ramp, leaf_lvl - 1.4)
    box(cv, lx + 2, (y0 + y1) // 2, lx + 5, (y0 + y1) // 2 + 6, BRASS, 3.2)        # la maneta
    # rètol verd de sortida a sobre
    cx = (x0 + x1) // 2
    box(cv, cx - 12, y0 - 16, cx + 12, y0 - 10, [(6, 22, 16), (10, 38, 28), (16, 58, 42), (26, 82, 58), (40, 108, 76),
                                                 (62, 138, 98)], 3.4, edge=False)
    for x in range(cx - 10, cx + 10, 3):
        cv.put(x, y0 - 13, WHITEP, 4.0, lit=0)
        cv.put(x + 1, y0 - 13, WHITEP, 4.0, lit=0)


def porthole(cv, cx, cy, r=11, sea=None):
    """Ull de bou de llautó (principal.porthole), amb el mar de nit."""
    _porthole(cv, cx, cy, r, sea)


# ─── Laboratori ─────────────────────────────────────────────────────────────

def sample_chart(cv):
    """La carta dels punts de mostreig, clavada amb xinxetes: costa, punts 1-7, el 7 encerclat."""
    x0, y0, x1, y1 = 128, 30, 214, 70
    box(cv, x0, y0, x1, y1, PAPERC, 3.6)
    for y in range(y0 + 2, y1 - 1):
        for x in range(x0 + 2, x1 - 1):
            coast = 150 + 10 * math.sin(y * 0.25) + (y - y0) * 0.5
            if x < coast:
                cv.put(x, y, [(120, 110, 80), (170, 158, 120), (206, 196, 160)], 1.4)
            else:
                cv.put(x, y, [(90, 120, 140), (130, 160, 176), (176, 200, 210)], 1.6 + (0.4 if (x + y) % 9 == 0 else 0))
    for i, (px, py) in enumerate(((166, 38), (174, 44), (182, 40), (186, 50), (194, 46), (198, 58), (204, 62))):
        cv.flat(px, py, (30, 40, 60))
        if i == 6:
            cv.ring(px, py, 4, REDP, 5.0, step=20)
    cv.line(166, 38, 204, 62, [(60, 70, 90), (90, 100, 120)], 1.0)
    for x, y in ((x0 + 2, y0 + 2), (x1 - 2, y0 + 2), (x0 + 2, y1 - 2), (x1 - 2, y1 - 2)):
        cv.flat(x, y, (200, 40, 40))
    for x in range(x0 + 4, x0 + 20, 2):
        cv.put(x, y1 - 4, [(60, 50, 40), (100, 90, 70)], 0.6)


def jar(cv, x, y, h=9, w=5, liquid=(60, 90, 70), cap=REDP, lvl=3.0, label=True):
    """Un pot de mostres de vidre (x, y = cantó de baix a l'esquerra)."""
    top = y - h
    for yy in range(top + 2, y + 1):
        for xx in range(x, x + w):
            u = (xx - x) / max(1, w - 1)
            base = cv.get(xx, yy)[:3]
            col = mix(base, (170, 190, 186), 0.35 + 0.25 * (1 - u))
            if yy > top + 4:
                col = mix(col, liquid, 0.65)
            cv.flat(xx, yy, col)
    cv.vline(x, top + 2, y, GLASSB, 5.4)
    box(cv, x - 0, top, x + w - 1, top + 1, cap, lvl + 0.8, edge=False)
    if label and h >= 8:
        cv.rect(x + 1, y - 4, x + w - 2, y - 2, PAPERC, 4.0)


def shelf(cv):
    """Prestatge amb barana (perquè no caigui res amb mala mar), ple de pots."""
    x0, x1, y = 226, 340, 82
    box(cv, x0, y, x1, y + 3, TEAK, 4.4)
    for bx in (x0 + 4, x1 - 4):
        cv.poly([(bx - 1, y + 4), (bx + 1, y + 4), (bx + 1, y + 12), (bx - 1, y + 6)], CAB, 3.2)
    cv.hline(x0, x1, y - 6, BRASS, 3.6)                     # la barana
    for bx in range(x0 + 2, x1, 18):
        cv.vline(bx, y - 6, y - 1, BRASS, 3.0)
    liquids = [(70, 100, 80), (110, 100, 60), (60, 80, 100), (90, 110, 70), (120, 90, 60)]
    caps = [REDP, BLUEB, WHITEP, YELL]
    x = x0 + 5
    i = 0
    while x < x1 - 8:
        h = 8 + int(hr(i, 51) * 6)
        w = 5 + int(hr(i, 52) * 3)
        jar(cv, x, y - 1, h, w, liquids[i % 5], caps[int(hr(i, 53) * 4)], 3.0)
        x += w + 2 + int(hr(i, 54) * 2)
        i += 1
    # un fil de llum a la fusta
    cv.hline(x0 + 1, x1 - 1, y, TEAK, 6.0)


BENCH = (104, 106, 344, 160)      # x0, y_sobre (darrere), x1, y del sòcol


def bench(cv):
    """El taulell: sobre d'epoxi fosc i calaixos/armaris crema a sota."""
    x0, ytop, x1, ybot = BENCH
    # el sobre (es veu una mica en perspectiva)
    cv.poly([(x0 + 4, ytop), (x1 - 4, ytop), (x1, ytop + 7), (x0, ytop + 7)], EPOXY, lambda x, y: 3.2 + (y - ytop) * 0.12)
    cv.hline(x0 + 4, x1 - 4, ytop, EPOXY, 2.0)
    cv.rect(x0, ytop + 8, x1, ytop + 10, EPOXY, 4.6)
    cv.hline(x0, x1, ytop + 8, EPOXY, 5.6)
    cv.hline(x0, x1, ytop + 11, CREAM, 1.2)
    # el moble
    fy0 = ytop + 12
    box(cv, x0 + 2, fy0, x1 - 2, ybot - 4, CREAM, 5.0, grad=1.2)
    cv.rect(x0 + 4, ybot - 4, x1 - 4, ybot, SOCOL, 1.4)            # sòcol enretirat
    # calaixos (fila de dalt) i portes (a baix)
    n = 6
    cw = (x1 - x0 - 4) // n
    for i in range(n):
        cx0 = x0 + 2 + i * cw
        cx1 = cx0 + cw - 1
        box(cv, cx0 + 2, fy0 + 2, cx1 - 2, fy0 + 11, CREAM, 5.4)
        box(cv, (cx0 + cx1) // 2 - 4, fy0 + 6, (cx0 + cx1) // 2 + 4, fy0 + 7, CAB, 4.6)
        box(cv, cx0 + 2, fy0 + 14, cx1 - 2, ybot - 7, CREAM, 5.0, grad=0.8)
        hx = cx1 - 6 if i % 2 == 0 else cx0 + 5
        box(cv, hx, fy0 + 18, hx + 1, fy0 + 24, CAB, 4.6)
    # cops i ratllades a la vora de baix
    for i in range(14):
        x = x0 + 4 + int(hr(i, 61) * (x1 - x0 - 8))
        cv.put(x, ybot - 6, CREAM, 2.4)
        cv.put(x + 1, ybot - 6, CREAM, 3.0)


def magnifier(cv):
    """La lupa binocular: peu fosc, columna, capçal ivori amb dos oculars i la placa de Petri."""
    bx = 306
    box(cv, bx - 10, 107, bx + 16, 111, CAB, 3.2)                   # el peu
    vpipe(cv, bx + 12, 78, 107, 2, CAB, 4.2)                        # la columna
    box(cv, bx + 4, 82, bx + 14, 86, CAB, 3.6)                      # el braç
    rrect(cv, bx - 7, 80, bx + 7, 93, 3, WHITEP, lambda x, y: 4.6 - (x - bx) * 0.05 - (y - 80) * 0.05)
    cv.hline(bx - 5, bx + 5, 80, WHITEP, 5.6)
    vpipe(cv, bx, 94, 99, 3, CAB, 3.8)                              # l'objectiu
    for ox in (-4, 2):                                              # els oculars, cap a l'Iri
        for k in range(7):
            cv.put(bx + ox - k // 2, 79 - k, CAB, 2.6)
            cv.put(bx + ox + 1 - k // 2, 79 - k, CAB, 4.0)
            cv.put(bx + ox + 2 - k // 2, 79 - k, CAB, 3.2)
        cv.hline(bx + ox - 4, bx + ox, 72, CAB, 1.6)
    cv.disc(bx, 104, 7, 2, GLASSB, 3.6)                              # la placa de Petri
    cv.disc(bx, 104, 3, 1, [(40, 70, 50), (80, 120, 80)], 1.4)
    cv.disc(bx + 12, 90, 2, 2, CAB, 4.6)                             # la roda d'enfocar


def lab_coat(cv):
    """Una bata blanca i una armilla salvavides penjades d'uns ganxos, sota l'ull de bou."""
    for hx in (76, 94):
        box(cv, hx - 1, 98, hx + 1, 101, BRASS, 3.6)
    # la bata
    cv.poly([(72, 102), (80, 101), (84, 108), (86, 142), (66, 144), (68, 108)], WHITEP,
            lambda x, y: 4.2 - (x - 66) * 0.04 + (0.5 if (x + y // 3) % 7 == 0 else 0))
    cv.line(76, 103, 76, 143, WHITEP, 2.6)
    cv.line(70, 104, 67, 130, WHITEP, 3.0)
    for y in (114, 124, 134):
        cv.put(77, y, CAB, 3.0)
    cv.rect(79, 118, 83, 121, WHITEP, 3.0)                           # la butxaca, amb un bolígraf
    cv.vline(81, 115, 118, BLUEB, 3.6)
    # l'armilla salvavides (vermella, amb cinta reflectora)
    cv.poly([(89, 102), (99, 102), (102, 110), (101, 130), (87, 130), (86, 110)], REDP,
            lambda x, y: 4.4 - (x - 86) * 0.05)
    cv.vline(94, 104, 130, REDP, 2.6)
    for y in (114, 122):
        cv.hline(87, 101, y, [(120, 120, 110), (220, 220, 200), (250, 250, 240)], 1.8)


def jar_rack(cv):
    box(cv, 264, 104, 296, 111, TEAK, 4.0)
    for i, x in enumerate(range(266, 294, 6)):
        jar(cv, x, 104, 10, 4, [(70, 100, 80), (60, 80, 100), (110, 100, 60)][i % 3], [REDP, BLUEB, WHITEP][i % 3], 3.0,
            label=False)
    cv.hline(264, 296, 106, TEAK, 5.0)
    # un retolador i una pipeta
    cv.line(248, 111, 258, 110, BLUEB, 4.0)
    cv.line(176, 111, 190, 109, WHITEP, 4.2)


def fish_book(cv):
    """«Peixos de l'Atlàntic Nord»: un llibre gruixut, tancat, amb post-its que en surten."""
    x0, y0, x1, y1 = 140, 102, 176, 112
    cv.poly([(x0 + 3, y0), (x1 - 1, y0), (x1, y0 + 5), (x0, y0 + 5)], BLUEB, lambda x, y: 3.6 + (y - y0) * 0.1)
    cv.rect(x0, y0 + 6, x1, y1 - 1, PAPERC, lambda x, y: 3.2 + (0.6 if y % 2 else 0))
    cv.hline(x0, x1, y0 + 5, BLUEB, 2.2)
    cv.hline(x0, x1, y1, BLUEB, 2.0)
    cv.vline(x0, y0 + 5, y1, BLUEB, 2.6)
    # un peix a la tapa
    cv.hline(152, 162, y0 + 2, [(150, 170, 160), (200, 220, 200)], 1.4)
    cv.put(151, y0 + 1, [(150, 170, 160), (200, 220, 200)], 1.4)
    cv.put(151, y0 + 3, [(150, 170, 160), (200, 220, 200)], 1.4)
    # post-its
    for px, col in ((166, YELL), (171, REDP)):
        cv.rect(px, y0 - 3, px + 2, y0, col, 4.4)


def laptop(cv):
    """El portàtil de la Juana, obert, amb la pantalla de la contrasenya i adhesius de peixos."""
    x0, x1 = 198, 238
    # la tapa (pantalla)
    box(cv, x0 + 2, 84, x1 - 2, 105, CAB, 2.4)
    cv.rect(x0 + 4, 86, x1 - 4, 103, [(10, 20, 34), (20, 40, 64), (40, 70, 100), (90, 130, 170), (190, 220, 240)],
            lambda x, y: 1.4 + (103 - y) * 0.02, lit=0)
    cv.rect(212, 93, 224, 95, [(90, 130, 170), (220, 236, 250)], 1.4, lit=0)   # el camp de la contrasenya
    for x in range(214, 222, 2):
        cv.flat(x, 94, (30, 50, 80))
    cv.disc(218, 89, 2, 2, [(90, 130, 170), (200, 220, 240)], 1.2, lit=0)         # l'avatar
    glow(cv, 218, 95, 18, (120, 170, 220), 0.25)
    # adhesius a la vora
    cv.rect(x0 + 2, 99, x0 + 3, 101, YELL, 4.0)
    # la base, en perspectiva, amb el teclat
    cv.poly([(x0 + 2, 106), (x1 - 2, 106), (x1 + 1, 112), (x0 - 1, 112)], CAB, lambda x, y: 4.0 + (y - 106) * 0.1)
    for y in (107, 109):
        for x in range(x0 + 3, x1 - 2, 2):
            cv.put(x + (y - 107), y, CAB, 2.2)
    cv.hline(x0 - 1, x1 + 1, 112, CAB, 2.0)
    cv.flat(x1 - 2, 111, (90, 255, 120))


def note(cv):
    """La nota: un paper doblegat en forma de tenda, recolzat al costat del portàtil, amb lletra a mà."""
    x0, y0 = 242, 100
    cv.poly([(x0, 112), (x0 + 4, y0), (x0 + 14, y0), (x0 + 12, 112)], PAPERC, lambda x, y: 4.6 - (y - y0) * 0.03)
    cv.line(x0 + 4, y0, x0 + 14, y0, PAPERC, 5.6)
    for i, y in enumerate((103, 106, 109)):
        for x in range(x0 + 4 - i // 2, x0 + 11 - i):
            if hr(x, y, 7) > 0.35:
                cv.put(x, y, BLUEB, 2.0)
    cv.line(x0 + 1, 112, x0 + 13, 112, PAPERC, 2.0)


def fridge(cv):
    """La nevera de mostres: alta, blanca, amb porta de vidre, pots etiquetats per punts i el termòmetre."""
    x0, y0, x1, y1 = 362, 52, 440, FLOOR_Y + 6
    box(cv, x0, y0, x1, y1, WHITEP, 4.0, grad=0.8)
    box(cv, x0, y0, x1, y0 + 12, WHITEP, 4.4)                       # el capçal
    cv.rect(x0 + 50, y0 + 3, x0 + 66, y0 + 8, [(4, 14, 8), (8, 30, 16)], 1.0, lit=0)
    for i, ch in enumerate(('4', 'C')):                              # 4 °C, en verd
        cv.rect(x0 + 53 + i * 5, y0 + 4, x0 + 55 + i * 5, y0 + 7, GREENS, 3.0, lit=0)
    glow(cv, x0 + 58, y0 + 5, 7, (90, 255, 140), 0.4)
    cv.flat(x0 + 6, y0 + 6, (90, 255, 120))
    # la porta de vidre
    gx0, gy0, gx1, gy1 = x0 + 5, y0 + 16, x1 - 9, y1 - 14
    box(cv, gx0 - 2, gy0 - 2, gx1 + 2, gy1 + 2, CAB, 3.0)
    cv.rect(gx0, gy0, gx1, gy1, GLASSB, lambda x, y: 2.2 + (gy1 - y) * 0.01, lit=0.5)
    # els prestatges de dins, amb pots
    liquids = [(70, 100, 80), (110, 100, 60), (60, 80, 100), (90, 110, 70)]
    for k, sy in enumerate(range(gy0 + 18, gy1 + 1, 18)):
        cv.hline(gx0, gx1, sy, WHITEP, 3.6, lit=0.5)
        x = gx0 + 2
        i = 0
        while x < gx1 - 6:
            if not (k == 0 and i == 3):                              # el forat del 7
                jar(cv, x, sy - 1, 10, 6, liquids[(i + k) % 4], [REDP, BLUEB, WHITEP][(i + k) % 3], 2.6)
            x += 9
            i += 1
    # el fred: una mica de blau a dins i el reflex del vidre en diagonal
    cv.tint(gx0, gy0, gx1, gy1, (150, 200, 230), 0.12)
    for i in range(0, 60):
        for d in (0, 1, 6):
            px, py = gx0 + 6 + i // 2 + d, gy0 + i * 1.6
            if gy0 <= py <= gy1 and px <= gx1:
                cv.tint(px, int(py), px, int(py), (220, 240, 250), 0.25)
    # tirador i frontisses
    box(cv, x1 - 7, gy0 + 20, x1 - 5, gy0 + 50, CAB, 4.4)
    for hy in (gy0 + 4, gy1 - 6):
        box(cv, x0 + 1, hy, x0 + 3, hy + 4, CAB, 3.6)
    # reixa de baix
    for y in range(y1 - 11, y1 - 3, 2):
        cv.hline(x0 + 6, x1 - 6, y, WHITEP, 2.0)
    # un rètol: «MOSTRES - NO MENJAR»
    box(cv, x0 + 10, y0 + 14, x0 + 30, y0 + 18, YELL, 4.2, edge=False)


def sink(cv):
    """El racó: una pica petita d'acer amb l'aixeta i el rotllo de paper, i el rentaulls verd."""
    x0, x1 = 446, 479
    box(cv, x0, 110, x1, FLOOR_Y + 4, CREAM, 4.6, grad=1.0)
    box(cv, x0 - 2, 106, x1, 111, WHITEP, 4.6)
    cv.rect(x0 + 4, 107, x1 - 4, 109, CAB, 2.0)
    vpipe(cv, 458, 94, 106, 1, CAB, 5.0)                            # aixeta de coll de cigne
    for a in range(0, 181, 15):
        cv.put(462 - round(math.cos(math.radians(a)) * 4), 94 - round(math.sin(math.radians(a)) * 4), CAB, 5.2)
    cv.put(466, 96, CAB, 4.0)
    box(cv, 470, 100, 474, 104, REDP, 3.6)
    # el rotllo de paper
    box(cv, 452, 64, 474, 80, WHITEP, 4.0, grad=0.8)
    cv.rect(457, 81, 469, 88, PAPERC, 4.6)
    cv.hline(457, 469, 81, PAPERC, 2.4)
    # el cartell AIGUA NO POTABLE (ratlletes)
    box(cv, 450, 116, 474, 124, WHITEP, 4.2)
    cv.rect(452, 118, 472, 119, REDP, 3.6)
    for x in range(452, 472, 2):
        cv.put(x, 122, CAB, 1.6)
    cv.vline(x0 + 2, 128, FLOOR_Y, CREAM, 3.2)


def bg(cv):
    cream_wall(cv)
    ceiling(cv)
    # un tub d'aigua dolça (blau) i un de cables vora el sostre
    hpipe(cv, 0, W - 1, 27, 2, BLUEB, 3.4, bands=range(40, W, 64), band_ramp=WHITEP)
    watertight_door(cv)
    porthole(cv, 84, 76)
    lab_coat(cv)
    sample_chart(cv)
    shelf(cv)
    linoleum(cv)
    bench(cv)
    magnifier(cv)
    jar_rack(cv)
    fish_book(cv)
    fridge(cv)
    sink(cv)
    lamps(cv)
    # ombres de contacte a terra
    cv.darken(BENCH[0], BENCH[3] + 1, BENCH[2], BENCH[3] + 4, lambda x, y: 0.8 - (y - BENCH[3]) * 0.2)
    cv.darken(360, FLOOR_Y + 7, 479, FLOOR_Y + 10, lambda x, y: 0.7 - (y - FLOOR_Y - 7) * 0.2)
    lamp_glow(cv)


# ─── Props ──────────────────────────────────────────────────────────────────

def portatil(cv):
    laptop(cv)


def nota(cv):
    note(cv)


def remenat(cv):
    """Calaixos mal tancats, papers girats per terra i pel taulell, un pot tombat i la porta de l'armari entreoberta."""
    x0, ytop, x1, ybot = BENCH
    fy0 = ytop + 12
    cw = (x1 - x0 - 4) // 6
    for i in (0, 2, 3, 5):
        cx0 = x0 + 2 + i * cw
        cx1 = cx0 + cw - 1
        out = 5 + (i % 2) * 3
        # el calaix tret: el frontal baixa una mica (perspectiva) i es veu el fons fosc
        cv.rect(cx0 + 2, fy0 + 2, cx1 - 2, fy0 + 3, DARK, 1.0)
        box(cv, cx0 + 1, fy0 + 3 + out, cx1 - 1, fy0 + 12 + out, CREAM, 5.4)
        cv.rect(cx0 + 2, fy0 + 3, cx1 - 2, fy0 + 2 + out, CREAM, 2.0)
        cv.vline(cx0 + 1, fy0 + 3, fy0 + 2 + out, CREAM, 4.4)
        cv.vline(cx1 - 1, fy0 + 3, fy0 + 2 + out, CREAM, 3.6)
        box(cv, (cx0 + cx1) // 2 - 4, fy0 + 7 + out, (cx0 + cx1) // 2 + 4, fy0 + 8 + out, CAB, 4.6)
        # papers que en treuen el cap
        cv.rect(cx0 + 6, fy0 + 1, cx0 + 14, fy0 + 3, PAPERC, 4.6)
    # una porta d'armari entreoberta
    cx0 = x0 + 2 + 4 * cw
    cv.rect(cx0 + 3, fy0 + 15, cx0 + 10, ybot - 8, DARK, 0.8)
    cv.poly([(cx0 + 10, fy0 + 14), (cx0 + 18, fy0 + 12), (cx0 + 18, ybot - 4), (cx0 + 10, ybot - 7)], CREAM, 4.6)
    # papers girats damunt del taulell
    for px, py, w in ((116, 104, 12), (180, 103, 10), (252, 104, 9), (320, 105, 14)):
        cv.poly([(px, py + 6), (px + 3, py), (px + w + 3, py + 1), (px + w, py + 7)], PAPERC, 4.2)
        cv.hline(px + 3, px + w, py + 3, PAPERC, 3.0)
    # un pot tombat a la gradeta, amb el líquid vessat
    cv.rect(288, 108, 297, 111, GLASSB, 4.6)
    box(cv, 297, 108, 299, 111, REDP, 4.0, edge=False)
    cv.disc(282, 112, 7, 1.5, [(30, 50, 40), (60, 90, 70), (100, 130, 110)], 1.6)
    # papers per terra
    for i, (px, py) in enumerate(((150, 170), (196, 176), (230, 166), (300, 172), (126, 182), (338, 180))):
        a = hr(i, 71) * 0.6 - 0.3
        dx, dy = round(math.cos(a) * 11), round(math.sin(a) * 2)
        cv.poly([(px, py), (px + dx, py + dy), (px + dx + 3, py + dy + 5), (px + 3, py + 5)], PAPERC,
                lambda x, y: 3.6 + (hr(x, y) - 0.5) * 0.3)
        if i % 2:
            cv.hline(px + 2, px + dx, py + 2, BLUEB, 2.0)
    # una carpeta oberta, de cara a terra
    cv.poly([(258, 184), (282, 182), (286, 190), (262, 192)], [(40, 60, 30), (70, 100, 50), (110, 140, 70), (150, 180, 100)], 2.2)


PROPS = {'portatil': portatil, 'nota': nota, 'remenat': remenat,
         'ulls_dia': lambda cv: day_porthole(cv, 84, 76, 11)}            # Escenes 2 i 3: de dia


# ─── Animacions ────────────────────────────────────────────────────────────
from hd.rooms.comu import _diff  # noqa: E402

PORT = (84, 76, 11)              # l'ull de bou: centre i radi del vidre


def _glass(cv, t, day):
    """El vidre de l'ull de bou (com principal.night_sea / day_sea) amb `t` (0..1 del bucle): l'horitzó puja i baixa
    amb el balanceig i les ratlles d'onada corren (el mateix que a la cabina de la Capitana)."""
    cx, cy, r = PORT
    ph = t * 2 * math.pi
    hz = cy + r * 0.15 + math.sin(ph) * 1.6
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if math.hypot(x - cx, y - cy) > r:
                continue
            crest = math.sin(x * 0.7 + y * 2.3 - ph * 2)
            if day:
                if y < hz:
                    cl = hr(int(x // 5), int(y // 2), 0)
                    cv.put(x, y, DAYSKY, 4.2 + (y - (cy - r)) / (r * 2.2) * 1.4 - (0.7 if cl > 0.75 else 0), lit=0.08)
                else:
                    cv.put(x, y, DAYSEA, 4.4 - (y - hz) / (r * 0.9) + (1.2 if crest > 0.8 else 0), lit=0.08)
            else:
                if y < hz:
                    cl = hr(int(x // 4), int(y // 2), 0)
                    cv.put(x, y, NIGHT, 2.0 + (hz - y) / (r * 2) + (0.8 if cl > 0.72 else 0), lit=0.1)
                else:
                    cv.put(x, y, NIGHT, 1.6 - (y - hz) / (r * 1.6) + (1.6 if crest > 0.85 else 0), lit=0.1)
    shine = (236, 240, 244) if day else (200, 210, 230)                 # el reflex del vidre
    for i in range(-r // 2, r // 3):
        x, y = cx - r // 3 + i, cy - r // 2 - i // 2
        cv.flat(x, y, mix(cv.get(x, y), shine, 0.35))


def _base(day=False):
    cv = Canvas(light=LIGHT)
    bg(cv)
    if day:
        top = Canvas(light=LIGHT, transparent=True)
        PROPS['ulls_dia'](top)
        cv.img.alpha_composite(top.img)
    return cv.img


def _frames_port(day):
    base = _base(day)
    frames = []
    for i in range(12):
        cv = Canvas(light=LIGHT, img=base.copy())
        _glass(cv, i / 12, day)
        frames.append(_diff(cv.img, base))
    return frames


def _frames_portatil():
    """El prop sencer a cada fotograma: el cursor del camp de la contrasenya parpelleja i el llum de repòs respira."""
    frames = []
    for i in range(8):
        cv = Canvas(light=LIGHT, transparent=True)
        laptop(cv)
        if i < 4:
            cv.rect(222, 93, 222, 95, [(30, 50, 80)], 0, lit=0)
        led = 0.5 + 0.5 * math.cos(i / 8 * 2 * math.pi)
        cv.flat(236, 111, mix((20, 60, 34), (90, 255, 120), led))
        frames.append(cv.img)
    return frames


DIGITS = {'3': ['111', '011', '001', '111'], '4': ['101', '111', '001', '001'], 'C': ['111', '100', '100', '111']}


def _frames_nevera():
    """El visor de la nevera: 4 °C que de tant en tant baixa a 3 (el compressor) i el pilot verd que parpelleja."""
    base = _base()
    x0, y0 = 362, 52
    frames = []
    for i in range(16):
        cv = Canvas(light=LIGHT, img=base.copy())
        cv.rect(x0 + 51, y0 + 3, x0 + 65, y0 + 8, [(4, 14, 8), (8, 30, 16)], 1.0, lit=0)
        temp = '3' if 9 <= i <= 12 else '4'
        for dx, ch in ((53, temp), (59, 'C')):
            for j, row in enumerate(DIGITS[ch]):
                for m, bit in enumerate(row):
                    if bit == '1':
                        cv.put(x0 + dx + m, y0 + 4 + j, GREENS, 3.6, lit=0)
        cv.flat(x0 + 57, y0 + 4, GREENS[3])                           # el grau, entre la xifra i la C
        glow(cv, x0 + 58, y0 + 5, 8, (90, 255, 140), 0.45)
        if i % 8 < 1:                                                # el pilot, un cop cada dues voltes del visor
            cv.flat(x0 + 6, y0 + 6, (210, 255, 220))
            glow(cv, x0 + 6, y0 + 6, 4, (90, 255, 120), 0.6)
        else:
            cv.flat(x0 + 6, y0 + 6, (40, 140, 70))
        frames.append(_diff(cv.img, base))
    return frames


def _frames_bombolla():
    """Un pot de la gradeta amb una mostra viva: una bombolla puja pel líquid i esclata a la superfície."""
    base = _base()
    frames = []
    path = [(279, 103), (279, 102), (280, 101), (280, 100), (279, 99)]
    for i in range(14):
        cv = Canvas(light=LIGHT, img=base.copy())
        if i < len(path):
            x, y = path[i]
            cv.flat(x, y, mix(cv.get(x, y)[:3], (220, 236, 230), 0.7))
        elif i == len(path):
            cv.flat(279, 98, (200, 220, 214))
            cv.flat(281, 98, (200, 220, 214))
        frames.append(_diff(cv.img, base))
    return frames


ANIMS = {'mar': {'frames': lambda: _frames_port(False), 'frameDuration': 220},
         'ulls_dia_mar': {'frames': lambda: _frames_port(True), 'frameDuration': 220},
         'portatil': {'frames': _frames_portatil, 'frameDuration': 265},
         'nevera': {'frames': _frames_nevera, 'frameDuration': 250},
         'bombolla': {'frames': _frames_bombolla, 'frameDuration': 140}}


# ─── Geometria ──────────────────────────────────────────────────────────────

GEOMETRIA = {
    'things': {
        'porta': {'rect': (4, 50, 60, 152), 'walk': (36, 182)},
        'llibre': {'rect': (138, 98, 178, 113), 'walk': (158, 182)},
        'portatil': {'rect': (196, 83, 240, 113), 'walk': (218, 182)},
        'nota': {'rect': (241, 98, 257, 113), 'walk': (248, 182)},
        'taulell': {'rect': (104, 114, 344, 160), 'walk': (290, 182)},
        'nevera': {'rect': (362, 52, 440, 158), 'walk': (400, 182)},
    },
    'spawns': {'iri': (230, 190), 'vet': (300, 194), 'juana': (176, 180)},
    'walkable': [(12, 168), (468, 168), (476, 198), (4, 198)],
}
