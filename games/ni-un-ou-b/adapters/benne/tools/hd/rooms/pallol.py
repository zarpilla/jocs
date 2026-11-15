"""
El pallol: el magatzem del contramestre. Prestatges amb caps, cable apantallat i connectors, pintura i cinta;
el tauler dels cadenats (cinc, i un ganxo buit), l'inventari clavat damunt la porta, defenses, un salvavides i
un rotllo de cap d'amarrar. A l'Escena 6 el Marcel hi seu a terra amb en Diu (són sprites).
ANIMS: `defenses` (les defenses i el salvavides es gronxen amb el balanceig) i `pols` (pols a la llum del llum
de l'esquerra, damunt dels prestatges).
"""
import math

from hd.pix import Canvas, Light, W, H, hr, mix, B4, WALNUT, PAPER, ORANGE
from hd.rooms.arenga import (WALL, ENG, DECK, CAB, DARK, WHITEP, YELL, REDP, SEAG, FUEL, BRASS, WARM, FLOOR_Y,
                             BOTTOM, box, rrect, bolt, hpipe, vpipe, glow)
from hd.rooms import sota
from hd.rooms.comu import _diff

LAMPS = (170, 372)

LIGHT = Light(ambient=-0.5, vignette=(46, 28), floor_fade=None)
LIGHT.point(170, 26, r=160, k=2.6, squash=1.05, down=True, power=1.5)
LIGHT.point(372, 26, r=150, k=2.3, squash=1.05, down=True, power=1.5)

DOOR = (10, 66, 52, FLOOR_Y)
SHELF = (78, 34, 262, FLOOR_Y + 2)
ROPE = [(36, 28, 14), (78, 62, 32), (128, 104, 58), (176, 150, 92), (214, 192, 130), (238, 224, 170)]
ROPEW = [(40, 40, 40), (90, 90, 86), (140, 140, 132), (186, 186, 176), (220, 220, 210), (240, 240, 232)]
BLUE = [(8, 16, 36), (14, 30, 64), (22, 48, 98), (36, 70, 130), (60, 100, 166), (110, 150, 200)]
BLACKC = [(4, 4, 6), (10, 10, 14), (20, 20, 26), (34, 34, 42), (54, 54, 64), (80, 80, 92)]


# ─── Paret, porta i inventari ──────────────────────────────────────────────

def walls(cv):
    sota.plate_wall(cv, 0, W - 1, frames=64, frame0=60, seams=(58, 112), rust=26, seed=21)
    sota.ceiling(cv, beam0=60)
    hpipe(cv, 0, W - 1, 30, 2, SEAG, 3.0, bands=range(30, W, 60), band_ramp=WHITEP)
    for x in range(40, W, 60):
        cv.vline(x, 26, 34, CAB, 2.0)
        cv.vline(x + 1, 26, 34, CAB, 3.4)


def door(cv):
    """La porta del passadís, tancada (la veiem de dins)."""
    x0, y0, x1, y1 = DOOR
    sota.door_frame(cv, x0, y0, x1, y1, ramp=WALL, lvl=4.2, r=6)
    rrect(cv, x0, y0, x1, y1 - 7, 5, CAB, lambda x, y: 3.4 - (y - y0) * 0.006)
    for y in range(y0 + 8, y1 - 10, 6):
        cv.hline(x0 + 4, x1 - 4, y, CAB, 4.2)
        cv.hline(x0 + 4, x1 - 4, y + 1, CAB, 2.4)
    sota.sill(cv, x0, x1, y1)
    for hy in (y0 + 12, y1 - 22):                                       # frontisses
        box(cv, x1 - 2, hy, x1 + 2, hy + 8, CAB, 3.6)
    box(cv, x0 + 3, 102, x0 + 7, 112, BRASS, 3.6)                       # maneta
    cv.hline(x0 + 5, x0 + 12, 104, BRASS, 4.6)


def inventory(cv):
    """L'inventari, clavat damunt la porta: un full amb una llista i una columna de xifres."""
    x0, y0, x1, y1 = 16, 36, 46, 60
    box(cv, x0, y0, x1, y1, PAPER, 4.2)
    cv.rect(x0 + 1, y0 + 1, x1 - 1, y0 + 3, PAPER, 3.0)
    for i, y in enumerate(range(y0 + 6, y1 - 2, 3)):
        n = 10 + int(hr(i, 4) * 10)
        cv.hline(x0 + 3, x0 + 3 + n, y, DARK, 2.0)
        cv.hline(x1 - 6, x1 - 4, y, DARK, 2.0)
    cv.hline(x1 - 6, x1 - 4, y0 + 12, REDP, 4.0)                        # la línia dels cadenats, repassada
    cv.put(x0 + 15, y0 + 1, CAB, 4.6)                                   # el clau
    cv.put(x0 + 15, y0, CAB, 2.6)
    # un bolígraf lligat amb un cordill
    cv.line(x1 + 1, y0 + 2, x1 + 3, y0 + 18, WHITEP, 3.0)
    cv.line(x1 + 3, y0 + 18, x1 + 4, y0 + 26, BLUE, 3.6)


# ─── Els prestatges ─────────────────────────────────────────────────────────

def coil(cv, cx, cy, rx, ry, ramp, lvl=3.0, turns=3):
    """Un rotllo de cap, vist de cara (anelles concèntriques) i trenat."""
    for y in range(int(cy - ry), int(cy + ry) + 1):
        for x in range(int(cx - rx), int(cx + rx) + 1):
            nx, ny = (x - cx) / rx, (y - cy) / ry
            d = math.hypot(nx, ny)
            if d <= 1 and d >= 0.28:
                ring = (d * turns * 2) % 2
                tw = ((x + y * 2) // 2) % 3 == 0
                cv.put(x, y, ramp, lvl + 1.2 * (1 - abs(ring - 1)) - nx * 0.6 - ny * 0.8 - (0.6 if tw else 0))
            elif d < 0.28:
                cv.put(x, y, DARK, 1.0)


def reel(cv, cx, cy, r, w, ramp=BLACKC):
    """Una bobina de cable vista de cara: el cable enrotllat i les dues galtes de fusta."""
    cv.disc(cx, cy, r, r, WALNUT, lambda nx, ny: 3.4 - nx - ny)
    cv.disc(cx, cy, r - 2, r - 2, ramp, lambda nx, ny: 2.8 - nx * 0.8 - ny * 0.8)
    for a in range(0, 360, 30):
        cv.put(cx + round(math.cos(math.radians(a)) * (r - 4)), cy + round(math.sin(math.radians(a)) * (r - 4)), ramp, 4.4)
    cv.disc(cx, cy, 3, 3, WALNUT, 3.0)
    cv.put(cx, cy, DARK, 0.5)


def can(cv, x0, y0, w, h, ramp, label=WHITEP, drip=None):
    """Un pot de pintura."""
    for y in range(y0, y0 + h + 1):
        for x in range(x0, x0 + w + 1):
            u = (x - x0 - w / 2) / (w / 2 + 0.5)
            cv.put(x, y, CAB if y < y0 + 2 else ramp, 3.4 + 1.4 * (-0.3 - u) - 0.8 * u * u)
    cv.hline(x0, x0 + w, y0, CAB, 4.8)
    cv.rect(x0 + 1, y0 + h // 2 - 1, x0 + w - 1, y0 + h // 2 + 2, label, 3.6)
    if drip:
        for i, dx in enumerate((1, 3, w - 2)):
            cv.vline(x0 + dx, y0 + 2, y0 + 3 + i * 2, drip, 3.6)


def shelves(cv):
    x0, y0, x1, y1 = SHELF
    # muntants i lleixes (de planxa gris, cargolada)
    levels = (56, 86, 118, 148)
    cv.darken(x0 + 3, y0, x1 - 3, y1, 0.25)                             # el fons de dins, més fosc
    for lx in (x0, (x0 + x1) // 2, x1 - 4):
        box(cv, lx, y0, lx + 4, y1, CAB, 3.4)
        for y in range(y0 + 4, y1, 6):
            cv.put(lx + 2, y, DARK, 1.0)
    for ly in levels:
        box(cv, x0, ly, x1, ly + 3, CAB, 3.8)
        cv.hline(x0, x1, ly + 4, DARK, 1.0)
    box(cv, x0 - 2, y0 - 2, x1 + 2, y0 + 1, CAB, 3.4)
    # ─ lleixa de dalt: pintura (blanca, vermella de la borda, verda de sala de màquines) i brotxes
    can(cv, 86, 40, 12, 15, WHITEP, drip=WHITEP)
    can(cv, 101, 42, 12, 13, REDP, drip=REDP)
    can(cv, 116, 40, 12, 15, WHITEP)
    can(cv, 131, 44, 10, 11, SEAG, drip=SEAG)
    for i in range(3):                                                  # brotxes dins un pot
        cv.line(150 + i * 3, 38, 152 + i * 2, 48, WALNUT, 3.6)
    can(cv, 146, 46, 12, 9, CAB, label=CAB)
    for i in range(4):                                                  # rotllos de cinta americana
        cv.disc(176 + i * 9, 51, 4, 4, [(40, 40, 44), (90, 90, 96), (140, 140, 146), (180, 180, 186)],
                lambda nx, ny: 2.8 - nx - ny)
        cv.disc(176 + i * 9, 51, 1.5, 1.5, DARK, 1.0)
    box(cv, 214, 40, 254, 55, [(40, 30, 14), (80, 60, 30), (130, 100, 54), (170, 136, 80)], 2.8)   # caixa de cartró
    cv.hline(214, 254, 47, [(60, 40, 20), (150, 120, 60), (200, 170, 110)], 2.2)
    sota.sign(cv, 222, 42, 'DRAPS', ramp=PAPER, lvl=4.0, pad=1)
    # ─ segona lleixa: caps enrotllats (blancs, grocs i blau)
    coil(cv, 98, 74, 13, 11, ROPEW)
    coil(cv, 125, 74, 13, 11, ROPE)
    coil(cv, 150, 76, 10, 9, BLUE)
    coil(cv, 180, 73, 14, 12, ROPEW, lvl=2.6)
    coil(cv, 210, 74, 13, 11, ORANGE)
    coil(cv, 238, 75, 12, 10, ROPE, lvl=2.6)
    # ─ tercera lleixa: bobines de cable apantallat i capses de connectors
    reel(cv, 100, 104, 13, 4)
    reel(cv, 128, 106, 11, 4, ramp=[(40, 18, 10), (90, 40, 20), (150, 70, 30), (200, 110, 60), (230, 160, 110), (250, 200, 160)])
    reel(cv, 152, 108, 9, 4)
    for i in range(4):                                                  # capses de connectors, amb etiqueta
        bx = 172 + i * 21
        box(cv, bx, 98, bx + 18, 117, [(16, 20, 26), (30, 36, 46), (48, 56, 70), (70, 80, 96), (100, 110, 126)], 2.6)
        cv.rect(bx + 3, 103, bx + 15, 107, PAPER, 3.6)
        cv.hline(bx + 4, bx + 4 + 3 + i * 2, 105, DARK, 1.6)
        cv.hline(bx + 7, bx + 11, 98, BRASS, 3.6)                       # nansa
    # ─ lleixa de baix: una caixa d'eines, galledes, un rotllo de cap gruixut
    box(cv, 86, 132, 126, 147, REDP, 3.2)
    cv.hline(86, 126, 136, REDP, 4.4)
    box(cv, 100, 128, 112, 131, CAB, 3.6)
    for gx in (138, 158):
        cv.poly([(gx, 128), (gx + 16, 128), (gx + 14, 147), (gx + 2, 147)], YELL, lambda x, y: 3.4 - (x - gx) * 0.06)
        cv.hline(gx, gx + 16, 128, YELL, 4.6)
        cv.line(gx + 1, 128, gx + 8, 122, CAB, 3.0)
        cv.line(gx + 8, 122, gx + 15, 128, CAB, 3.0)
    coil(cv, 210, 136, 28, 11, ROPE, lvl=2.8, turns=4)
    cv.darken(x0 + 3, y1 - 4, x1 - 3, y1, 0.4)


def padlocks(cv):
    """El tauler dels cadenats: sis ganxos i cinc cadenats. N'hi falta un."""
    x0, y0, x1, y1 = 270, 70, 312, 104
    box(cv, x0, y0, x1, y1, WALNUT, 3.0)
    for x in range(x0 + 3, x1 - 2, 4):
        for y in range(y0 + 3, y1 - 2, 4):
            cv.put(x, y, WALNUT, 1.4)
    sota.sign(cv, x0 + 6, y0 - 9, 'CADENATS', ramp=PAPER, lvl=3.8, pad=1)
    for i in range(6):
        hx, hy = hook(i)
        cv.vline(hx, hy, hy + 3, CAB, 4.4)
        cv.put(hx + 1, hy + 3, CAB, 3.6)
        if i == 4:
            continue                                                    # el ganxo buit (el sisè és un prop)
        padlock(cv, hx, hy)


def hook(i):
    """On és el ganxo i del tauler (de 0 a 5)."""
    return 270 + 6 + (i % 3) * 14, 70 + 5 + (i // 3) * 16


def padlock(cv, hx, hy):
    """Un cadenat penjat d'un ganxo del tauler."""
    cv.ring(hx + 1, hy + 6, 2.5, WHITEP, 4.4, step=20)
    rrect(cv, hx - 3, hy + 7, hx + 5, hy + 13, 1, BRASS, lambda x, y: 4.0 - (x - hx + 3) * 0.12)
    cv.put(hx + 1, hy + 10, DARK, 1.0)


def cadenat_sise(cv):
    """El sisè cadenat, al seu ganxo (abans de l'Escena 4 no en falta cap)."""
    padlock(cv, *hook(4))


# ─── Defenses, salvavides, galledes, rotllo d'amarrar ──────────────────────

FENDERS = ((334, ORANGE), (358, WHITEP))
BUOY = (410, 84)
_SWING = {'a': 0.0}                       # angle (graus) del gronxament: el canvien els fotogrames de `defenses`


def _rot(x, y, px, py, deg):
    """Punt (x, y) girat `-deg` al voltant de (px, py): on cau dins l'objecte quiet."""
    c, s_ = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    dx, dy = x - px, y - py
    return px + dx * c + dy * s_, py - dx * s_ + dy * c


def _fender_px(cv, fx, col, deg):
    """Una defensa penjada del cap a (fx, 48), girada `deg` graus (positiu: el peu cap a la dreta)."""
    pad = 12
    for y in range(46, 120):
        for x in range(fx - pad - 8, fx + pad + 8):
            lx, ly = _rot(x, y, fx, 48, -deg)
            if ly < 48 or ly > 116.5:
                continue
            if 60 <= ly < 112:
                t = (ly - 60) / 52
                rx = 9 * math.sin(math.pi * min(1, max(0, t * 1.08 + 0.02))) ** 0.5
                if abs(lx - fx) <= rx + 0.5:
                    u = (lx - fx) / (rx + 0.5)
                    cv.put(x, y, col, 3.4 + 1.4 * (-0.3 - u) - 0.8 * u * u)
            elif abs(lx - fx) < 0.6:
                cv.put(x, y, ROPEW, 3.4 if ly < 60 else 3.0)


def _buoy_px(cv, deg):
    """El salvavides, penjat d'un cap del mateix bastidor, girat `deg` graus al voltant del nus de dalt."""
    cx0, cy0 = BUOY
    py = 48
    for y in range(py, cy0 + 22):
        for x in range(cx0 - 24, cx0 + 25):
            lx, ly = _rot(x, y, cx0, py, -deg)
            d = math.hypot(lx - cx0, ly - cy0)
            if 10 <= d <= 18.5:
                a = math.degrees(math.atan2(ly - cy0, lx - cx0)) % 90
                band = 35 <= a <= 55
                u = (d - 14.25) / 4.5
                cv.put(x, y, WHITEP if band else ORANGE, 3.6 - u * 1.2 - (ly - cy0) * 0.03 - u * u)
            elif 18.5 < d <= 19.5:
                a = math.degrees(math.atan2(ly - cy0, lx - cx0)) % 360
                if (int(a) // 45) % 2 == 0 and int(a) % 6 < 2:
                    cv.put(x, y, ROPEW, 3.6)
            elif abs(lx - cx0) < 0.6 and py <= ly < cy0 - 19:
                cv.put(x, y, ROPEW, 3.0)


def fenders(cv):
    """Dues defenses penjades d'un cap, i el salvavides (es gronxen amb el balanceig: vegeu _SWING)."""
    cv.hline(318, 470, 46, CAB, 3.6)
    cv.hline(318, 470, 47, CAB, 2.0)
    a = _SWING['a']
    for i, (fx, col) in enumerate(FENDERS):
        _fender_px(cv, fx, col, a * (1.0 if i == 0 else 0.85))       # la blanca, més lleugera, va una mica enrere
    _buoy_px(cv, a * 0.5)                                               # el salvavides frega la paret: es mou menys
    sota.sign(cv, 394, 108, 'ARENGA', ramp=WHITEP, lvl=3.8, pad=1)


def buckets(cv):
    """Una galleda i un pal de fregar, i un bidó de plàstic, contra la paret de la dreta."""
    cv.line(452, 70, 446, FLOOR_Y + 2, WALNUT, 3.6)
    cv.line(453, 70, 447, FLOOR_Y + 2, WALNUT, 2.4)
    for i in range(7):
        cv.line(446, FLOOR_Y - 8, 440 + i * 2, FLOOR_Y + 2, ROPEW, 2.6 + (i % 2) * 0.6)
    # bidó blau
    rrect(cv, 456, 116, 476, FLOOR_Y + 2, 3, BLUE, lambda x, y: 3.4 - (x - 456) * 0.07)
    box(cv, 462, 112, 468, 116, BLUE, 3.0)
    cv.rect(458, 128, 474, 136, WHITEP, 3.4)


def mooring_coil(cv):
    """Un rotllo de cap d'amarrar, gruixut, a terra (en perspectiva)."""
    sota.floor_shadow(cv, 290, 164, 34, 5, 0.6)
    for k in range(5):
        cy = 162 - k * 3
        rx, ry = 32 - k * 2, 8 - k * 0.6
        for a in range(0, 360, 2):
            x = 290 + math.cos(math.radians(a)) * rx
            y = cy + math.sin(math.radians(a)) * ry
            front = math.sin(math.radians(a)) > -0.2
            for t in range(3):
                cv.put(x, y - t, ROPE, (3.4 if front else 2.0) + (0.9 if t == 2 else 0) - (0.5 if (a // 8) % 2 else 0))
    cv.disc(290, 150, 18, 3.5, DARK, 1.0)


def crate(cv):
    """Una caixa de fusta de peix, del revés, contra la paret: el seient del Marcel a l'Escena 6."""
    x0, x1, yt, yb = 389, 415, 150, 186
    sota.floor_shadow(cv, (x0 + x1) // 2, yb + 1, 20, 4, 0.7)
    # la cara de dalt (el fons de la caixa), vista una mica des de dalt
    cv.poly([(x0 + 2, yt), (x1 + 2, yt), (x1, yt + 5), (x0, yt + 5)], WALNUT, lambda x, y: 5.4 - (y - yt) * 0.12)
    for x in range(x0 + 8, x1, 8):                                      # junts de les posts
        cv.line(x + 2, yt, x, yt + 5, WALNUT, 2.4)
    # la cara del davant: posts horitzontals, amb llum entre post i post
    for i, py in enumerate(range(yt + 6, yb + 1, 8)):
        box(cv, x0, py, x1, min(py + 6, yb), WALNUT, 4.4 - i * 0.2, grad=0.7)
        if py + 7 <= yb:
            cv.hline(x0 + 1, x1 - 1, py + 7, DARK, 1.0)
    for x in (x0, x1 - 2):                                              # els travessers dels cantons
        box(cv, x, yt + 5, x + 2, yb, WALNUT, 3.6)
    cv.hline(x0 + 6, x0 + 20, yt + 16, FUEL, 3.2)                       # una marca de pintura, mig esborrada
    for x in range(x0 + 6, x0 + 21, 3):
        cv.put(x, yt + 16, WALNUT, 3.4)


# ─── Muntatge ───────────────────────────────────────────────────────────────

def bg(cv):
    walls(cv)
    door(cv)
    inventory(cv)
    shelves(cv)
    padlocks(cv)
    fenders(cv)
    buckets(cv)
    sota.checker_floor(cv)
    mooring_coil(cv)
    crate(cv)
    sota.floor_shadow(cv, 170, FLOOR_Y + 3, 96, 3, 0.6)
    for lx in LAMPS:
        sota.cage_lamp(cv, lx)
    for lx in LAMPS:
        sota.lamp_glow(cv, lx)


PROPS = {'cadenat_sise': cadenat_sise}


# ─── Animacions ────────────────────────────────────────────────────────────

def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv


def _frames_defenses():
    """El balanceig: les defenses i el salvavides fan un vaivé lent (sinus: el bucle no salta)."""
    base = _base()
    frames = []
    n = 32
    for i in range(n):
        _SWING['a'] = 3.5 * math.sin(2 * math.pi * i / n)
        try:
            cv = _base()
        finally:
            _SWING['a'] = 0.0
        frames.append(_diff(cv.img, base.img))
    return frames


def _frames_pols():
    """Pols que sura a la llum del llum de l'esquerra (cada mota fa un llaç tancat: el bucle no salta)."""
    base = _base()
    lx = LAMPS[0]
    motes = [(lx + (hr(k, 7) - 0.5) * 80, 40 + hr(k, 8) * 90, 6 + hr(k, 9) * 10, 4 + hr(k, 10) * 8, hr(k, 11),
              1 + int(hr(k, 12) * 2)) for k in range(18)]
    n = 48
    frames = []
    for i in range(n):
        cv = Canvas(light=LIGHT, img=base.img.copy())
        t = i / n
        for (cx, cy, ax, ay, ph, fx) in motes:
            a = 2 * math.pi * (t + ph)
            x = round(cx + ax * math.sin(fx * a))
            y = round(cy + ay * math.sin(a + ph * 3))
            near = max(0.0, 1 - math.hypot(x - lx, (y - 26) * 0.9) / 130)
            alpha = near * (0.5 + 0.25 * (1 + math.sin(a * 2 + ph * 7)))
            if alpha > 0.08 and 0 <= x < W and 30 <= y < FLOOR_Y:
                cv.flat(x, y, mix(cv.get(x, y), (255, 236, 196), alpha))
        frames.append(_diff(cv.img, base.img))
    return frames


ANIMS = {'defenses': {'frames': _frames_defenses, 'frameDuration': 200},
         'pols': {'frames': _frames_pols, 'frameDuration': 130}}

GEOMETRIA = {
    'things': {
        'porta': {'rect': (6, 62, 56, 152), 'walk': (34, 168)},
        'prestatges': {'rect': (76, 32, 264, 154), 'walk': (170, 170)},
        'inventari': {'rect': (14, 34, 50, 62), 'walk': (40, 168)},
    },
    'spawns': {'iri': (200, 190), 'vet': (150, 194), 'marcel': (400, 186), 'diu': (379, 190)},
    'walkable': [(6, 164), (250, 164), (252, 176), (330, 176), (332, 164), (474, 164), (478, 197), (2, 197)],
}
