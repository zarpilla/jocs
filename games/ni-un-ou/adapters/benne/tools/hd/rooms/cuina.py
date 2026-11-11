"""
La cuina de l'Arenga: petita, d'acer i rajola, amb tot lligat perquè no balli amb la mar. D'esquerra a dreta:
  - la porta de vaivé del menjador (amb l'ull de bou);
  - el muntacàrregues (porta de guillotina aixecada, la cabina i la botonera CUINA · REBOST · PONT); la seva
    safata és un prop (quan hi ha arribat alguna cosa, amb el pilot verd encès);
  - el passaplats al menjador i, al costat, la boca del tub de veu de llautó;
  - els fogons amb baranes i subjecta-olles, la campana i les olles penjades;
  - la porta de la cambra freda, l'armari de les olles (decorat `armari_obert`: obert, fosc a dins) i el forn,
    amb el pa d'en Tomàs; a la dreta, el marbre amb la pasta i la farina.
"""
import math

from hd.pix import Light, Canvas, W, H, hr, mix
from hd.rooms.arenga import CAB, DARK, WHITEP, REDP, YELL, BRASS, SEAG, FLOOR_Y, BOTTOM, box, rrect, bolt, hpipe, vpipe, glow
from hd.rooms.principal import (CREAM, TEAK, DOORP, CEIL_H, wall, ceiling, lamp, lamp_glow, lino, shine, unmask,
                                foot_shadow, floor_shadow, in_door, door_frame, sill, leaf, plaque, porthole, wear,
                                voice_tube, day_porthole)
from hd.rooms.comu import _diff, text, text_width

LAMPS = (96, 206, 330, 442)
STEEL = [(10, 12, 14), (22, 25, 28), (38, 42, 46), (58, 63, 68), (82, 88, 93), (110, 116, 120), (142, 148, 150),
         (180, 184, 186), (220, 222, 222)]
TILE = [(30, 32, 32), (64, 66, 64), (104, 106, 100), (146, 146, 138), (184, 182, 170), (212, 210, 196), (234, 232, 220)]
QUARRY = [(14, 6, 4), (28, 12, 8), (46, 20, 12), (66, 30, 18), (88, 42, 24), (112, 56, 32), (136, 72, 42),
          (160, 90, 54)]
INWARM = [(20, 12, 8), (40, 26, 16), (66, 44, 28), (96, 68, 42), (130, 96, 62), (168, 128, 86), (204, 164, 116),
          (232, 200, 150)]
FIRE = [(60, 14, 6), (140, 50, 10), (210, 110, 30), (250, 170, 70), (255, 220, 140), (255, 246, 210)]
BREAD = [(40, 20, 8), (84, 46, 16), (130, 78, 30), (176, 116, 50), (214, 158, 82), (238, 200, 130)]
FLOUR = [(90, 86, 78), (150, 146, 134), (200, 196, 182), (232, 230, 218), (248, 246, 238)]
COPPERP = [(40, 18, 14), (76, 34, 20), (118, 56, 30), (160, 84, 44), (200, 120, 66), (232, 162, 104), (250, 210, 160)]
ICE = [(20, 30, 40), (50, 70, 86), (100, 126, 140), (160, 186, 196), (210, 228, 234), (240, 248, 250)]

_OVEN_K = 0.0                         # el resplendor del forn (l'anima `forn`)
LIGHT = Light(ambient=-0.25, vignette=(44, 24), floor_fade=(188, 40))
for _x in LAMPS:
    LIGHT.point(_x, CEIL_H + 4, r=112, k=2.2, squash=1.1, down=True, power=1.5)
LIGHT.point(206, 62, r=46, k=0.8, power=2.0)                 # el llum de la campana
LIGHT.point(388, 118, r=30, k=0.5, power=2.0)                # el vidre del forn

D_PORTA = (10, 64, 48, FLOOR_Y)
MUNTA = (58, 48, 114, 128)          # el marc del muntacàrregues
CAB_IN = (64, 84, 98, 124)          # l'obertura de la cabina
CFREDA = (248, 46, 298, FLOOR_Y)
ARMARI = (308, 70, 352, FLOOR_Y)
FORN = (362, 86, 416, FLOOR_Y)
COUNTER_Y = 112                     # el marbre (altura de maluc)


# ─── Porta, muntacàrregues, passaplats i tub de veu ─────────────────────────

def door(cv):
    x0, y0, x1, y1 = D_PORTA

    def mess(c, x, y):
        c.put(x, y, INWARM, 5.4 - math.hypot(x - 29, y - 84) * 0.28, lit=0)
    leaf(cv, x0, y0, x1, y1 - 5, DOORP, 3.8, louvre=False, handle='right', seed=7, window=(29, 86, 7, mess))
    box(cv, x0 + 3, y1 - 26, x1 - 3, y1 - 8, STEEL, 4.2)
    for x in range(x0 + 5, x1 - 4, 5):
        cv.put(x, y1 - 20, STEEL, 5.6)
    door_frame(cv, x0, y0, x1, y1)
    sill(cv, x0, x1, y1)
    plaque(cv, (x0 + x1) // 2, 50, 'MENJADOR')


def dumbwaiter(cv):
    """El muntacàrregues: marc d'acer, la porta de guillotina aixecada, la cabina i la botonera."""
    x0, y0, x1, y1 = MUNTA
    cx0, cy0, cx1, cy1 = CAB_IN
    # el moble de sota (el muntacàrregues és a l'altura del marbre)
    box(cv, x0, y1, x1, FLOOR_Y - 1, STEEL, 3.6, grad=0.8)
    cv.vline((x0 + x1) // 2, y1 + 3, FLOOR_Y - 3, STEEL, 2.0)
    for hx in ((x0 + x1) // 2 - 4, (x0 + x1) // 2 + 3):
        cv.rect(hx, y1 + 6, hx + 1, y1 + 10, STEEL, 5.4)
    # el marc
    box(cv, x0, y0, x1, y1, STEEL, 4.0, grad=0.6)
    for bx, by in ((x0 + 2, y0 + 2), (x1 - 3, y0 + 2), (x0 + 2, y1 - 3), (x1 - 3, y1 - 3)):
        bolt(cv, bx, by, STEEL, 4.4)
    # la cabina, fosca, amb la paret del fons i els carrils
    for y in range(cy0, cy1 + 1):
        for x in range(cx0, cx1 + 1):
            cv.put(x, y, STEEL, 1.4 + (y - cy0) * 0.02 - abs(x - (cx0 + cx1) / 2) * 0.02, lit=0.4)
    cv.vline(cx0 + 1, cy0, cy1, STEEL, 2.8, lit=0.4)
    cv.vline(cx1 - 1, cy0, cy1, STEEL, 2.4, lit=0.4)
    cv.rect(cx0, cy1 - 2, cx1, cy1, STEEL, 3.6)                         # el terra de la cabina
    cv.hline(cx0, cx1, cy1 - 2, STEEL, 5.0)
    # la porta de guillotina, aixecada (planxa amb nervis)
    gx0, gy0, gx1, gy1 = cx0 - 1, y0 + 4, cx1 + 1, cy0 - 2
    box(cv, gx0, gy0, gx1, gy1, STEEL, 4.6)
    for y in range(gy0 + 4, gy1 - 1, 5):
        cv.hline(gx0 + 2, gx1 - 2, y, STEEL, 3.4)
        cv.hline(gx0 + 2, gx1 - 2, y + 1, STEEL, 5.4)
    box(cv, (gx0 + gx1) // 2 - 6, gy1 - 4, (gx0 + gx1) // 2 + 6, gy1 - 2, STEEL, 6.0)  # la nansa
    cv.darken(cx0, cy0, cx1, cy0 + 4, lambda x, y: 0.7 - (y - cy0) * 0.15)
    # botonera: CUINA · REBOST · PONT
    px0, py0 = 102, 86
    box(cv, px0, py0, px0 + 9, py0 + 32, STEEL, 3.0)
    for i, col in enumerate((REDP, SEAG, SEAG)):
        by = py0 + 4 + i * 9
        cv.disc(px0 + 4.5, by + 2, 2, 2, col, lambda nx, ny: 3.6 - nx - ny)
        cv.hline(px0 + 2, px0 + 7, by + 6, WHITEP, 4.0)
    # el pilot d'arribada, apagat
    cv.disc(px0 + 4.5, py0 - 4, 2, 1.5, SEAG, 1.4)
    # el rètol del muntacàrregues
    box(cv, x0 + 6, y0 - 8, x1 - 6, y0 - 2, WHITEP, 4.2)
    text(cv, 'MUNTACÀRREGUES', x0 + 7 + ((x1 - x0 - 13) - text_width('MUNTACÀRREGUES')) // 2, y0 - 7, None, 0, flat=(30, 34, 40))


def tray(cv):
    """La safata, a la cabina del muntacàrregues, amb un paquet embolicat, i el pilot verd encès."""
    cx0, cy0, cx1, cy1 = CAB_IN
    ty = cy1 - 4
    # la safata (acer, amb vores)
    cv.poly([(cx0 + 4, ty - 3), (cx1 - 4, ty - 3), (cx1 - 2, ty), (cx0 + 2, ty)], STEEL, 5.0)
    cv.hline(cx0 + 2, cx1 - 2, ty + 1, STEEL, 3.0)
    cv.hline(cx0 + 4, cx1 - 4, ty - 4, STEEL, 6.0)
    # un paquet de paper d'estrassa, lligat
    box(cv, cx0 + 9, ty - 11, cx1 - 11, ty - 4, [(60, 44, 28), (110, 82, 48), (158, 126, 74), (198, 166, 102), (226, 198, 136)], 3.0)
    cv.vline((cx0 + cx1) // 2 - 1, ty - 11, ty - 4, WHITEP, 3.6)
    cv.hline(cx0 + 9, cx1 - 11, ty - 8, WHITEP, 3.6)
    # el pilot: ha arribat alguna cosa
    cv.flat(106, 82, (120, 255, 150))
    cv.flat(107, 82, (120, 255, 150))
    glow(cv, 106, 82, 7, (90, 255, 120), 0.7)


def hatch(cv):
    """El passaplats, de la banda de la cuina: a l'altra banda, el menjador (la banqueta vermella i la taula)."""
    x0, y0, x1, y1 = 120, 84, 148, COUNTER_Y - 2
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            v = 3.6 + 1.6 * math.exp(-((x - 134) / 12) ** 2) - (y - y0) * 0.015
            cv.put(x, y, CREAM, v, lit=0.3)
    cv.rect(x0, y0 + 10, x1, y1 - 6, [(40, 10, 10), (64, 16, 14), (92, 24, 20), (120, 34, 26), (148, 48, 34)], 2.6, lit=0.3)
    for bx in range(x0 + 8, x1, 14):
        cv.vline(bx, y0 + 11, y1 - 7, [(40, 10, 10), (64, 16, 14)], 0.6, lit=0)
    cv.rect(x0, y1 - 5, x1, y1 - 3, TEAK, 4.6, lit=0.3)                  # la taula
    cv.rect(x0, y1 - 2, x1, y1, TEAK, 2.0, lit=0.3)
    cv.disc(x0 + 10, y1 - 7, 2, 2, REDP, 3.6, lit=0.3)                   # una tassa
    cv.rect(x0 + 18, y0 + 1, x1 - 2, y0 + 8, WHITEP, 3.6, lit=0.3)       # el pòster, de lluny
    cv.rect(x0 + 19, y0 + 2, x1 - 3, y0 + 4, [(20, 50, 90), (40, 90, 140)], 1.4, lit=0)
    box(cv, x0 - 3, y0 - 9, x1 + 3, y0 - 1, STEEL, 3.2)                  # la persiana enrotllada
    for y in range(y0 - 8, y0 - 1, 2):
        cv.hline(x0 - 2, x1 + 2, y, STEEL, 4.6)
    cv.vline(x0 - 1, y0, y1, STEEL, 4.6)
    cv.vline(x0 - 2, y0, y1, STEEL, 3.0)
    cv.vline(x1 + 1, y0, y1, STEEL, 2.2)
    box(cv, x0 - 5, y1 + 1, x1 + 5, y1 + 4, STEEL, 4.8)                  # el taulell
    cv.darken(x0 - 4, y1 + 5, x1 + 4, y1 + 7, 0.6)


def tiles(cv, x0, y0, x1, y1, seed=0):
    """Rajola blanca de cuina, amb els junts i alguna esquerda."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            joint = (x - x0) % 8 == 0 or (y - y0) % 8 == 0
            v = 4.0 + (hr((x - x0) // 8, (y - y0) // 8, seed) - 0.5) * 0.4 - (1.2 if joint else 0)
            if (x - x0) % 8 == 1 and not joint:
                v += 0.5
            cv.put(x, y, TILE, v)


# ─── Fogons, campana i olles ────────────────────────────────────────────────

def stove(cv):
    """Fogons de vaixell: baranes de mar, subjecta-olles, dues olles i, a sobre, la campana amb les olles penjades."""
    x0, x1, top = 172, 240, COUNTER_Y - 4
    tiles(cv, x0 - 2, 40, x1 + 2, top, seed=3)
    # cos d'acer amb portetes i el forn petit
    box(cv, x0, top, x1, FLOOR_Y - 1, STEEL, 3.8, grad=1.0)
    box(cv, x0 + 4, top + 10, x1 - 4, FLOOR_Y - 6, STEEL, 3.4)
    cv.hline(x0 + 8, x1 - 8, top + 14, STEEL, 5.6)
    for i, kx in enumerate(range(x0 + 8, x1 - 4, 10)):                 # mànecs
        cv.disc(kx, top + 5, 2, 2, DARK, lambda nx, ny: 2.4 - nx - ny)
        cv.put(kx, top + 4, STEEL, 6.0)
    # el sobre i la barana de mar
    cv.rect(x0 - 2, top - 3, x1 + 2, top, STEEL, 2.6)
    cv.hline(x0 - 2, x1 + 2, top - 3, STEEL, 5.4)
    for px in (x0 - 2, x0 + 22, x0 + 44, x1 + 2):
        cv.vline(px, top - 12, top - 3, STEEL, 4.4)
    hpipe(cv, x0 - 2, x1 + 2, top - 12, 1, STEEL, 4.6)
    # l'olla gran (amb tapa) i la cafetera de llautó, subjectes amb barres
    ox = 192
    for y in range(top - 22, top - 3):
        for x in range(ox - 11, ox + 12):
            u = (x - ox) / 11.5
            cv.put(x, y, STEEL, 4.6 + 1.6 * (-0.3 - u) - 1.0 * u * u)
    cv.disc(ox, top - 22, 11, 2, STEEL, 5.6)
    cv.rect(ox - 2, top - 26, ox + 2, top - 24, DARK, 2.0)
    cv.rect(ox - 14, top - 15, ox - 11, top - 13, DARK, 1.6)
    cv.rect(ox + 11, top - 15, ox + 14, top - 13, DARK, 1.6)
    kx = 224
    cv.disc(kx, top - 9, 7, 6, COPPERP, lambda nx, ny: 3.6 - nx * 1.3 - ny * 1.0)
    cv.line(kx + 6, top - 10, kx + 11, top - 14, COPPERP, 3.4)
    cv.disc(kx, top - 15, 2, 1, DARK, 2.0)
    cv.line(x0 + 12, top - 8, x0 + 12, top - 5, DARK, 1.0)
    # (el vapor de l'olla és l'animació `vapor`)
    # la campana
    cv.poly([(x0 - 6, 52), (x1 + 6, 52), (x1 - 2, 40), (x0 + 2, 40)], STEEL, lambda x, y: 4.2 + (y - 40) * 0.06)
    cv.rect(x0 + 2, 26, x1 - 2, 39, STEEL, 3.4)
    for x in range(x0 + 6, x1 - 4, 4):
        cv.vline(x, 28, 37, STEEL, 2.6)
    cv.hline(x0 - 6, x1 + 6, 52, STEEL, 2.0)
    cv.rect(x0 + 24, 53, x1 - 24, 54, [(160, 140, 90), (255, 240, 190), (255, 252, 236)], 1.6, lit=0)
    glow(cv, (x0 + x1) // 2, 56, 18, (255, 236, 190), 0.4)
    # la barra amb les olles penjades
    hpipe(cv, x0 - 2, x1 + 2, 60, 1, STEEL, 4.8)
    hooks = ((x0 + 4, 'pan', 9), (x0 + 18, 'ladle', 0), (x0 + 26, 'pot', 7), (x0 + 40, 'pan', 7), (x0 + 52, 'ladle', 0),
             (x0 + 60, 'pot', 6))
    for hx, kind, r in hooks:
        cv.vline(hx, 61, 64, STEEL, 3.0)
        if kind == 'pan':
            cv.vline(hx, 64, 72, STEEL, 3.4)
            cv.disc(hx, 72 + r, r, r, COPPERP if r > 8 else STEEL, lambda nx, ny: 3.8 - nx * 1.2 - ny * 1.0)
            cv.disc(hx, 72 + r, r - 2, r - 2, COPPERP if r > 8 else STEEL, lambda nx, ny: 2.6 + nx * 0.6 + ny * 0.6)
        elif kind == 'ladle':
            cv.vline(hx, 64, 82, STEEL, 4.6)
            cv.disc(hx, 85, 3, 2.5, STEEL, lambda nx, ny: 4.0 - nx - ny)
        else:
            cv.line(hx - 4, 64, hx + 4, 64, STEEL, 3.0)
            for y in range(66, 66 + r * 2):
                for x in range(hx - r, hx + r + 1):
                    u = (x - hx) / (r + 0.5)
                    cv.put(x, y, COPPERP, 3.6 + 1.4 * (-0.3 - u) - 0.8 * u * u)
            cv.hline(hx - r - 2, hx - r, 68, COPPERP, 3.0)
            cv.hline(hx + r, hx + r + 2, 68, COPPERP, 2.4)


# ─── Cambra freda, armari i forn ────────────────────────────────────────────

def cold_room(cv):
    """La porta de la cambra freda: gruixuda, blanca, amb frontisses i tancador cromats i el termòmetre."""
    x0, y0, x1, y1 = CFREDA
    box(cv, x0 - 3, y0 - 3, x1 + 3, y1, STEEL, 3.6)
    box(cv, x0, y0, x1, y1 - 2, ICE, 4.2, grad=0.5)
    cv.vline(x0 + 1, y0 + 1, y1 - 3, ICE, 5.4)
    for y in range(y0 + 1, y1 - 2):
        if hr(x0, y // 3) > 0.5:
            cv.put(x1 - 1, y, ICE, 3.0)
    # junta de goma i frontisses
    for hy in (y0 + 12, y1 - 24):
        box(cv, x0 - 4, hy, x0 + 4, hy + 10, STEEL, 5.0)
        cv.vline(x0, hy + 1, hy + 9, STEEL, 3.0)
    # el tancador (palanca gran cromada)
    hx, hy = x1 - 10, 96
    box(cv, hx - 2, hy - 6, hx + 6, hy + 10, STEEL, 4.6)
    cv.rect(hx - 10, hy + 1, hx + 4, hy + 3, STEEL, 5.8)
    cv.hline(hx - 10, hx + 4, hy + 4, STEEL, 2.6)
    cv.disc(hx + 2, hy + 2, 2, 2, STEEL, 6.6)
    # el termòmetre digital, a sobre: +3
    box(cv, x0 + 14, y0 - 12, x1 - 14, y0 - 5, DARK, 2.0)
    text(cv, '3', x0 + 19, y0 - 10, None, 0, flat=(255, 80, 60))
    cv.flat(x0 + 23, y0 - 10, (255, 80, 60))
    glow(cv, x0 + 22, y0 - 8, 6, (255, 80, 60), 0.35)
    # gebre a baix i el rètol
    for x in range(x0 + 1, x1):
        for y in range(y1 - 8, y1 - 2):
            if hr(x // 2, y) > 0.55 + (y1 - y) * 0.05:
                cv.put(x, y, ICE, 5.2)
    box(cv, x0 + 8, 58, x1 - 8, 66, [(20, 40, 80), (30, 60, 120), (60, 100, 170), (120, 160, 220), (200, 220, 240)], 1.6)
    text(cv, 'FRED', (x0 + x1) // 2 - text_width('FRED') // 2, 60, None, 0, flat=(220, 236, 248))
    cv.darken(x0, y1 - 1, x1 + 3, y1 + 2, 0.6)


def cupboard(cv):
    """L'armari de les olles, de fusta, tancat, amb reixeta (l'escletxa per on es mira)."""
    x0, y0, x1, y1 = ARMARI
    box(cv, x0 - 2, y0 - 4, x1 + 2, y0, TEAK, 4.4)                       # cornisa
    box(cv, x0, y0, x1, y1 - 1, TEAK, 3.2, grad=0.6)
    _door(cv, x0 + 2, y0 + 2, x1 - 2, y1 - 4)
    foot_shadow(cv, x0 - 2, x1 + 2, FLOOR_Y + 1, 4, 0.7)
    # damunt: una cassola que sembla un casc i una pila de paelles
    cv.disc(x0 + 12, y0 - 9, 8, 5, STEEL, lambda nx, ny: 4.4 - nx * 1.2 - ny * 1.4)
    cv.hline(x0 + 3, x0 + 21, y0 - 5, STEEL, 3.2)
    for i in range(3):
        cv.rect(x1 - 20 + i, y0 - 6 - i * 2, x1 - 4 - i, y0 - 5 - i * 2, STEEL, 3.4 + i * 0.6)
    cv.hline(x1 - 26, x1 - 20, y0 - 6, STEEL, 2.6)


def _door(cv, x0, y0, x1, y1):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            v = 3.6 + (hr(x // 2, y // 11, 5) - 0.5) * 0.4 - (y - y0) * 0.006
            if x in (x0, x0 + 1):
                v += 1.0
            if x >= x1 - 1:
                v -= 1.0
            cv.put(x, y, TEAK, v)
    box(cv, x0 + 4, y0 + 4, x1 - 4, y0 + 34, TEAK, 3.2)
    box(cv, x0 + 4, y0 + 40, x1 - 4, y1 - 6, TEAK, 3.2)
    for y in range(y0 + 8, y0 + 30, 3):                                  # reixeta de ventilació
        cv.hline(x0 + 8, x1 - 8, y, TEAK, 1.4)
        cv.hline(x0 + 8, x1 - 8, y + 1, TEAK, 4.0)
    cv.rect(x1 - 7, y0 + 40, x1 - 6, y0 + 48, BRASS, 4.2)                # nansa i balda de mar
    cv.rect(x1 - 9, y0 + 50, x1 - 3, y0 + 51, BRASS, 3.4)


def cupboard_open(cv):
    """Decorat `armari_obert`: la porta oberta (de cantó) i, a dins, fosc, amb les olles a les prestatgeries."""
    x0, y0, x1, y1 = ARMARI
    ix0, iy0, ix1, iy1 = x0 + 2, y0 + 2, x1 - 2, y1 - 4
    for y in range(iy0, iy1 + 1):
        for x in range(ix0, ix1 + 1):
            cv.put(x, y, DARK, 1.6 + (x - ix0) * 0.02 - (y - iy0) * 0.004, lit=0.25)
    for sy in (iy0 + 26, iy0 + 52):                                       # prestatges
        cv.hline(ix0, ix1, sy, TEAK, 1.8, lit=0.3)
    for i, (px, py, r) in enumerate(((ix0 + 10, iy0 + 25, 7), (ix0 + 26, iy0 + 25, 5), (ix0 + 14, iy0 + 51, 9))):
        for y in range(py - r, py):
            for x in range(px - r, px + r + 1):
                cv.put(x, y, STEEL, 1.4 + (px - x) * 0.04, lit=0.25)
    cv.hline(ix0, ix1, iy1, TEAK, 1.2, lit=0.3)
    # la porta, oberta cap a la dreta, de cantó
    cv.poly([(x1 + 1, y0 + 1), (x1 + 8, y0 + 5), (x1 + 8, y1 - 2), (x1 + 1, y1 - 4)], TEAK, lambda x, y: 2.6 + (x - x1) * 0.12)
    cv.vline(x1 + 8, y0 + 5, y1 - 2, TEAK, 4.0)
    cv.rect(x1 + 6, y0 + 42, x1 + 7, y0 + 50, BRASS, 3.6)


def oven(cv):
    """El forn: acer, vidre amb el pa a dins (llum taronja), rellotge i mànecs, i el drap a la nansa."""
    x0, y0, x1, y1 = FORN
    box(cv, x0, y0, x1, y1 - 1, STEEL, 4.0, grad=1.0)
    cv.rect(x0 + 2, y0 + 2, x1 - 2, y0 + 12, STEEL, 2.6)                 # tauler de control
    for i, kx in enumerate(range(x0 + 8, x1 - 16, 9)):
        cv.disc(kx, y0 + 7, 3, 3, DARK, lambda nx, ny: 2.6 - nx - ny)
        cv.put(kx, y0 + 5, STEEL, 6.2)
    box(cv, x1 - 18, y0 + 4, x1 - 6, y0 + 10, DARK, 1.4)
    text(cv, '15', x1 - 16, y0 + 5, None, 0, flat=(255, 150, 60))
    # la porta amb el vidre
    box(cv, x0 + 3, y0 + 16, x1 - 3, y1 - 12, STEEL, 4.6)
    wx0, wy0, wx1, wy1 = x0 + 9, y0 + 24, x1 - 9, y1 - 22
    for y in range(wy0, wy1 + 1):
        for x in range(wx0, wx1 + 1):
            cv.put(x, y, FIRE, 2.6 + _OVEN_K - abs(y - (wy0 + wy1) / 2) * 0.12 - abs(x - (wx0 + wx1) / 2) * 0.04, lit=0)
    cv.hline(wx0, wx1, wy1 - 6, STEEL, 2.0, lit=0)                          # la reixa
    for bx in (wx0 + 6, wx0 + 20, wx0 + 32):                             # pans
        cv.disc(bx, wy1 - 10, 5, 3, BREAD, lambda nx, ny: 3.6 - ny * 1.2, lit=0)
        cv.line(bx - 2, wy1 - 11, bx + 1, wy1 - 12, BREAD, 4.8, lit=0)
    glow(cv, (wx0 + wx1) // 2, (wy0 + wy1) // 2, 26, (255, 170, 80), 0.35 + _OVEN_K * 0.2)
    hpipe(cv, x0 + 6, x1 - 6, y0 + 20, 1, STEEL, 6.0)                    # la nansa
    # el drap de cuina penjat (quadres blancs i vermells)
    for y in range(y0 + 21, y0 + 40):
        for x in range(x0 + 10, x0 + 20):
            ch = ((x - x0) // 3 + (y - y0) // 3) % 2
            cv.put(x, y, REDP if ch else WHITEP, 3.8 if ch else 4.2)
    cv.rect(x0 + 2, y1 - 9, x1 - 2, y1 - 2, STEEL, 2.6)
    foot_shadow(cv, x0 - 2, x1 + 2, FLOOR_Y + 1, 4, 0.7)


def bakery(cv):
    """El marbre d'en Tomàs: pasta de pa, farina, pans a refredar, el corró, un sac de farina i la prestatgeria."""
    x0, x1 = 422, W - 1
    tiles(cv, x0, 56, x1, COUNTER_Y - 4, seed=4)
    box(cv, x0, COUNTER_Y, x1 + 2, FLOOR_Y - 1, STEEL, 3.6, grad=0.8)
    box(cv, x0 + 4, COUNTER_Y + 8, x1 - 4, FLOOR_Y - 5, STEEL, 3.2)
    cv.rect(x0 - 2, COUNTER_Y - 4, x1, COUNTER_Y, [(40, 40, 42), (90, 90, 88), (150, 150, 146), (200, 200, 194), (230, 230, 226)], 3.4)
    cv.hline(x0 - 2, x1, COUNTER_Y - 4, [(40, 40, 42), (230, 230, 226)], 1.2)
    # la pasta, amb farina escampada
    cv.disc(440, COUNTER_Y - 7, 9, 4, FLOUR, lambda nx, ny: 3.4 - ny * 1.0 - nx * 0.4)
    for i in range(30):
        fx = 428 + int(hr(i, 3) * 40)
        fy = COUNTER_Y - 4 + int(hr(i, 4) * 3)
        cv.put(fx, fy, FLOUR, 4.4)
    # pans a refredar en una reixa
    cv.hline(454, 476, COUNTER_Y - 5, STEEL, 4.0)
    for bx in (459, 470):
        cv.disc(bx, COUNTER_Y - 9, 5, 4, BREAD, lambda nx, ny: 3.8 - ny * 1.4 - nx * 0.5)
        cv.line(bx - 2, COUNTER_Y - 11, bx + 2, COUNTER_Y - 12, BREAD, 5.2)
    # el corró
    hpipe(cv, 428, 446, COUNTER_Y - 13, 2, TEAK, 4.4)
    # el sac de farina, a terra
    cv.poly([(452, FLOOR_Y + 4), (470, FLOOR_Y + 4), (468, FLOOR_Y - 18), (454, FLOOR_Y - 18)], FLOUR, lambda x, y: 3.0 - (x - 452) * 0.05)
    cv.hline(453, 469, FLOOR_Y - 18, FLOUR, 2.0)
    text(cv, 'FARINA', 450, FLOOR_Y - 10, None, 0, flat=(110, 60, 30))
    floor_shadow(cv, 461, FLOOR_Y + 4, 12, 2, 0.6)
    # prestatge d'espècies i un ull de bou
    box(cv, x0 + 2, 48, x1, 50, TEAK, 4.0)
    for i, sx in enumerate(range(x0 + 4, x1 - 4, 6)):
        jar = (REDP, YELL, SEAG, TEAK, REDP, YELL, SEAG, TEAK, REDP)[i % 9]
        cv.rect(sx, 41, sx + 3, 47, [(30, 30, 30), (90, 90, 86), (170, 170, 160), (220, 220, 210)], 2.6)
        cv.rect(sx, 44, sx + 3, 47, jar, 3.4)
        cv.hline(sx, sx + 3, 41, DARK, 1.6)
    hpipe(cv, x0 + 2, x1, 46, 0, TEAK, 4.0)                               # barana del prestatge
    porthole(cv, 452, 82, 9, seed=3)


def floor_mat(cv):
    """La catifa de goma davant dels fogons."""
    x0, x1, y0, y1 = 166, 250, 158, 168
    cv.poly([(x0 + 2, y0), (x1 - 2, y0), (x1, y1), (x0, y1)], CAB, lambda x, y: 1.6 + (0.8 if (x // 3 + y // 2) % 2 else 0))
    cv.line(x0, y1, x1, y1, CAB, 0.6)
    cv.line(x0 + 2, y0, x1 - 2, y0, CAB, 3.0)


# ─── Muntatge ───────────────────────────────────────────────────────────────

def bg(cv):
    ceiling(cv)
    wall(cv, seed=3, rail=None, dado=None)
    wear(cv, 0, 30, W - 1, 140, 20, seed=3, k=0.22)
    door(cv)
    dumbwaiter(cv)
    hatch(cv)
    voice_tube(cv, 158, 76)
    stove(cv)
    cold_room(cv)
    cupboard(cv)
    oven(cv)
    bakery(cv)
    for lx in LAMPS:
        lamp(cv, lx)
    mask = lino(cv, QUARRY, lvl=3.8, tile=22, check=0.25, seed=3)
    foot_shadow(cv, 0, W - 1, FLOOR_Y + 1, 4, 0.45)
    shine(cv, mask, LAMPS, k=0.7, refl=0.12)
    floor_mat(cv)
    for lx in LAMPS:
        lamp_glow(cv, lx)


PROPS = {'safata': tray, 'armari_obert': cupboard_open,
         'ulls_dia': lambda cv: day_porthole(cv, 452, 82, 9, seed=3)}   # Escenes 2 i 3: de dia


# ─── Animacions ─────────────────────────────────────────────────────────────

def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv


def _frames_vapor():
    """El vapor de l'olla gran puja cap a la campana (cada fil torna a sortir quan s'esvaeix)."""
    base = _base()
    ox, lid = 192, COUNTER_Y - 4 - 26
    n, wisps = 48, 18
    frames = []
    for i in range(n):
        cv = Canvas(light=LIGHT, img=base.img.copy())
        t = i / n
        for p in range(wisps):
            age = (t * 2 + p / wisps) % 1
            y = lid - 1 - age * 26
            x = ox - 3 + (hr(p, 1) - 0.5) * 8 + 2 * math.sin(age * 8 + p * 2.1)
            a = 0.85 * (1 - age) * min(1.0, age * 5)
            xx, yy = round(x), round(y)
            for dx, dy, k in ((0, 0, 1.0), (1, 0, 0.7), (0, -1, 0.5)):        # una bufada de tres píxels
                cv.flat(xx + dx, yy + dy, mix(cv.get(xx + dx, yy + dy), (252, 252, 250), a * k))
        frames.append(_diff(cv.img, base.img))
    return frames


def _frames_forn():
    """El forn encès: la llum de dins tremola una mica."""
    global _OVEN_K
    base = _base()
    frames = []
    for k in (0.0, 0.2, 0.1, 0.3, 0.15, -0.1, 0.05, 0.25, 0.1, -0.05):
        _OVEN_K = k
        frames.append(_diff(_base().img, base.img))
    _OVEN_K = 0.0
    return frames


def _frames_fred():
    """Boira freda que s'escapa per sota la porta de la cambra i s'arrossega per terra."""
    base = _base()
    x0, _, x1, y1 = CFREDA
    n, wisps = 48, 16
    frames = []
    for i in range(n):
        cv = Canvas(light=LIGHT, img=base.img.copy())
        t = i / n
        for p in range(wisps):
            age = (t + p / wisps) % 1
            sx = x0 + 4 + hr(p, 3) * (x1 - x0 - 8)
            side = 1 if hr(p, 4) > 0.5 else -1
            x = sx + side * age * 20 + math.sin(age * 6 + p) * 1.5
            y = y1 + 1 + age * 8
            a = 0.7 * (1 - age) * min(1.0, age * 6)
            for dx, k in ((-1, 0.5), (0, 1.0), (1, 1.0), (2, 0.5)):
                xx, yy = round(x) + dx, round(y)
                if yy < H:
                    cv.flat(xx, yy, mix(cv.get(xx, yy), (214, 232, 244), a * k))
        frames.append(_diff(cv.img, base.img))
    return frames


ANIMS = {'vapor': {'frames': _frames_vapor, 'frameDuration': 100},
         'forn': {'frames': _frames_forn, 'frameDuration': 150},
         'fred': {'frames': _frames_fred, 'frameDuration': 110}}

GEOMETRIA = {
    'things': {
        'porta': {'rect': (6, 46, 52, FLOOR_Y), 'walk': (30, 176)},
        'munta': {'rect': (MUNTA[0], MUNTA[1] - 8, MUNTA[2], CAB_IN[1] + 20), 'walk': (86, 178)},
        'safata': {'rect': (CAB_IN[0], CAB_IN[1] + 22, CAB_IN[2], CAB_IN[3]), 'walk': (86, 178)},
        'boca': {'rect': (150, 70, 166, 104), 'walk': (158, 178)},
        'cambra_freda': {'rect': (CFREDA[0] - 3, CFREDA[1] - 12, CFREDA[2] + 3, FLOOR_Y), 'walk': (273, 178)},
        'armari': {'rect': (ARMARI[0] - 2, ARMARI[1] - 14, ARMARI[2] + 2, FLOOR_Y), 'walk': (330, 178)},
        'forn': {'rect': (FORN[0], FORN[1], FORN[2], FLOOR_Y), 'walk': (389, 178)},
    },
    'spawns': {'iri': (330, 194), 'vet': (150, 192), 'tomas': (446, 186), 'nadia': (276, 184)},
    'walkable': [(6, 168), (476, 168), (476, 197), (6, 197)],
}
