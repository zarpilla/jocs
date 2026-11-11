"""
Prova a 640×360: la sala de bombes (vegeu hd/rooms/sala_bombes.py, la de 480×270). Mateixa composició ×4/3,
dibuixada de nou: neta, pintada i callada. L'escotilla del sostre amb l'escala de mà; a l'esquerra el col·lector
de vàlvules (amb les plaquetes llegibles i els manòmetres graduats); a la dreta les tres bombes (contraincendis
vermella i dues de llast verdes) amb els motors d'aletes, les plaques de característiques i les caixes de borns;
entre mig, l'armari d'arrencada amb els pilots apagats. Les peces de hd/rooms/sota.py amb mides de 480 són aquí
adaptades (paret de planxa, sostre amb safates, llums de gàbia).
Props: `llibre`, `llanterna`. ANIMS: `manometres` (les agulles tremolen) i `gota` (cau del col·lector a un tollet).
"""
import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

import math

from hd.pix import Canvas, Light, W, H, hr, mix, B4, PAPER, RUST
from hd.rooms.arenga import (WALL, ENG, ENG_LIGHT, CAB, DARK, WHITEP, YELL, REDP, SEAG, BRASS, WARM,
                             box, rrect, bolt, hpipe, vpipe, glow)
from hd.rooms.comu import _diff, text, text_width

K = 4 / 3
FLOOR_Y = 203
BOTTOM = 260
LAMPS = (147, 496)

LIGHT = Light(ambient=-0.4, vignette=(61, 35), floor_fade=None)
LIGHT.point(147, 35, r=200, k=2.3, squash=1.05, down=True, power=1.5)
LIGHT.point(496, 35, r=213, k=2.4, squash=1.05, down=True, power=1.5)
LIGHT.point(307, 8, r=93, k=1.0, power=1.8)                        # la llum del passadís, per l'escotilla

FLOORP = [(6, 10, 10), (10, 17, 16), (16, 26, 24), (24, 37, 34), (34, 50, 45), (46, 65, 58), (62, 84, 74),
          (82, 106, 94)]
BOOK = [(10, 20, 26), (16, 36, 46), (24, 56, 70), (36, 80, 96), (56, 110, 124), (90, 146, 156)]
TORCH = YELL
LAMPR = [(120, 90, 40), (200, 160, 80), (250, 220, 150), (255, 246, 220)]
INK = (20, 24, 28)


def s(v):
    return round(v * K)


def _label(cv, s_, x0, y0, ramp=WHITEP, lvl=4.0, ink=INK, pad=3):
    """Rètol: placa amb vora i el text (font de 5 px). → amplada."""
    w = text_width(s_)
    box(cv, x0, y0, x0 + w + 2 * pad, y0 + 10, ramp, lvl)
    cv.hline(x0 + 1, x0 + w + 2 * pad - 1, y0 + 9, ramp, lvl - 0.9)
    text(cv, s_, x0 + pad + 1, y0 + 3, None, 0, flat=ink)
    for bx in (x0 + 1, x0 + w + 2 * pad - 2):                    # cargolets
        cv.put(bx, y0 + 5, ramp, lvl - 1.4)
    return w + 2 * pad + 1


# ─── Paret, sostre i escotilla ─────────────────────────────────────────────

def walls(cv):
    lvl = 3.5
    for y in range(0, FLOOR_Y):
        for x in range(W):
            v = lvl + (hr(x // 3, y // 5, 31) - 0.5) * 0.3
            if y >= 179:
                v -= 0.9 + (0.3 if hr(x // 6, y // 3, 31) > 0.8 else 0)
            cv.put(x, y, WALL, v)
    for fx in range(53 - 85, W, 85):                                 # quadernes amb dues fileres de reblons
        for x in range(max(0, fx), min(W - 1, fx + 7) + 1):
            d = x - fx
            for y in range(27, FLOOR_Y):
                cv.put(x, y, WALL, lvl + 0.4 + (0.9 if d == 0 else 0.5 if d == 1 else -0.3 if d >= 5 else 0.1)
                       - (0.8 if y >= 179 else 0))
        for y in range(37, FLOOR_Y - 22, 16):
            if 0 <= fx + 3 < W:
                bolt(cv, fx + 3, y, WALL, lvl + 0.5)
                bolt(cv, fx + 5, y + 8, WALL, lvl + 0.3)
    for sy in (80, 149):                                             # soldadures, amb el cordó
        for x in range(W):
            cv.put(x, sy, WALL, lvl - 1.3)
            cv.put(x, sy + 1, WALL, lvl + (0.9 if (x // 2) % 2 else 0.4))
    cv.hline(0, W - 1, 179, WALL, lvl + 0.9)
    cv.hline(0, W - 1, FLOOR_Y - 1, WALL, lvl - 2.1)
    # la franja verda a mitja alçada (les sales de bombes ben cuidades en tenen), amb el filet blanc
    cv.rect(0, 151, W - 1, 154, SEAG, 3.4)
    cv.hline(0, W - 1, 151, SEAG, 4.4)
    cv.hline(0, W - 1, 155, WHITEP, 3.0)
    # una mica de rovell sota la soldadura de dalt (poc: la sala està cuidada)
    for i in range(8):
        x = int(hr(i, 7, 31) * W)
        n = 6 + int(hr(i, 9, 31) * 12)
        for y in range(82, 82 + n):
            k = 0.4 * (1 - (y - 82) / n)
            if k > B4[y & 3][x & 3] * 0.6:
                cv.flat(x, y, mix(cv.get(x, y), RUST[3], k))


def ceiling(cv):
    cv.rect(0, 0, W - 1, 25, DARK, 2.0)
    for bx in range(53 - 85, W, 85):
        box(cv, max(0, bx - 3), 0, min(W - 1, bx + 11), 28, ENG, 1.6, grad=0.6)
        if bx - 2 >= 0:
            cv.vline(bx - 2, 1, 27, ENG, 2.6)
    for y in (8, 17):                                                # safates de cables, amb cables de colors
        cv.hline(0, W - 1, y, CAB, 2.8)
        cv.hline(0, W - 1, y + 5, CAB, 1.6)
        for x in range(0, W, 6):
            cv.vline(x, y, y + 5, CAB, 2.2)
        for k, row in enumerate((y + 2, y + 3)):
            for x in range(W):
                if hr(x // 12, y, k) > 0.35:
                    cv.flat(x, row, [(20, 20, 24), (40, 36, 30), (70, 50, 34), (110, 40, 34), (30, 50, 80)]
                            [int(hr(x // 14, y, k + 3) * 5)])
        for x in range(30, W, 70):
            cv.vline(x, y - 1, y + 6, CAB, 3.6)


def hatch(cv):
    """L'escotilla del sostre, oberta, amb la llum del passadís, i l'escala de mà que baixa a terra."""
    x0, x1 = 275, 339
    cv.rect(x0, 0, x1, 28, WALL, lambda x, y: 4.2 - y * 0.04, lit=0.5)
    cv.rect(x0 + 5, 0, x1 - 5, 10, WALL, 5.2, lit=0.4)
    for x in range(x0 + 8, x1 - 7, 9):                               # el passadís de dalt: el sostre i un llum
        cv.vline(x, 0, 3, WALL, 3.4, lit=0.4)
    box(cv, x0 - 7, 21, x1 + 7, 31, ENG, 3.2)                        # la brazola
    cv.hline(x0 - 6, x1 + 6, 22, ENG, 4.6)
    for bx in range(x0 - 4, x1 + 6, 7):
        bolt(cv, bx, 26, ENG, 3.4)
    # la tapa, oberta i plegada contra el sostre, amb la frontissa i el passador
    box(cv, x1 + 8, 5, x1 + 53, 13, ENG, 2.8)
    cv.hline(x1 + 9, x1 + 52, 6, ENG, 4.0)
    for bx in range(x1 + 14, x1 + 50, 8):
        bolt(cv, bx, 9, ENG, 3.0)
    box(cv, x1 + 3, 13, x1 + 11, 21, CAB, 3.4)
    cv.disc(x1 + 7, 17, 2, 2, CAB, 4.6)
    # l'escala de mà, amb els graons estriats
    for y in range(35, FLOOR_Y - 1, 13):
        hpipe(cv, 290, 323, y, 1, CAB, 3.6)
        for x in range(292, 322, 3):
            cv.put(x, y - 1, CAB, 4.8)
    vpipe(cv, 288, 21, FLOOR_Y + 1, 2, CAB, 3.9)
    vpipe(cv, 325, 21, FLOOR_Y + 1, 2, CAB, 3.3)
    for yy in (FLOOR_Y - 3, FLOOR_Y - 2):                           # els peus de l'escala, soldats
        cv.hline(284, 292, yy, CAB, 2.6)
        cv.hline(321, 329, yy, CAB, 2.6)
    # agafamans al cantó del forat
    for hx in (283, 331):
        cv.line(hx, 29, hx, 43, BRASS, 3.6)
        cv.line(hx + 1, 29, hx + 1, 43, BRASS, 2.4)


# ─── El col·lector de vàlvules (esquerra) ──────────────────────────────────

def handwheel(cv, cx, cy, r, ramp):
    for a in range(0, 360, 3):
        rad = math.radians(a)
        lv = 3.8 + 0.9 * math.cos(rad + 2.3)
        cv.put(cx + round(math.cos(rad) * r), cy + round(math.sin(rad) * r), ramp, lv)
        cv.put(cx + round(math.cos(rad) * (r - 1)), cy + round(math.sin(rad) * (r - 1)), ramp, lv - 1.2)
    for a in range(0, 360, 60):
        cv.line(cx, cy, cx + round(math.cos(math.radians(a + 15)) * (r - 2)),
                cy + round(math.sin(math.radians(a + 15)) * (r - 2)), ramp, 3.2)
    cv.disc(cx, cy, 3, 3, CAB, lambda nx, ny: 4.0 - nx - ny)
    cv.put(cx, cy, CAB, 1.4)


GAUGES = (80, 187)
GAUGE_Y = 97


def gauge_face(cv, gx, gy, a):
    """Esfera del manòmetre: escala, sector vermell i l'agulla a l'angle `a` (radians)."""
    cv.disc(gx, gy, 7, 7, WHITEP, 4.6)
    for k in range(9):                                               # graduació (de 135° a 405°)
        ang = math.radians(135 + k * 33.75)
        cv.put(gx + round(math.cos(ang) * 6), gy + round(math.sin(ang) * 6), DARK, 1.0)
    for k in range(3):                                               # el sector vermell, al final
        ang = math.radians(135 + 236 + k * 12)
        cv.put(gx + round(math.cos(ang) * 6), gy + round(math.sin(ang) * 6), REDP, 3.8)
    cv.line(gx, gy, gx + round(math.cos(a) * 5), gy + round(math.sin(a) * 5), DARK, 0)
    cv.put(gx, gy, REDP, 2.4)


def gauge_angle(k, j=0.0):
    return math.atan2(3, -2) + j


def manifold(cv):
    hpipe(cv, 27, 253, 123, 7, SEAG, 3.0, bands=range(48, 253, 53), band_ramp=WHITEP)
    for x in range(51, 253, 53):                                     # fletxes del sentit, a les anelles
        for i in range(4):
            cv.vline(x + 4 + i, 123 - 3 + i, 123 + 3 - i, DARK, 1.6)
    for i, vx in enumerate((53, 107, 160, 213)):
        vpipe(cv, vx, 123, FLOOR_Y + 4, 4, SEAG, 2.8)
        ramp = REDP if i == 0 else SEAG
        # cos de vàlvula amb brides i el castell (husillo)
        box(cv, vx - 8, 149, vx + 8, 165, ramp, 3.4)
        cv.hline(vx - 7, vx + 7, 150, ramp, 4.6)
        for by in (147, 166):
            box(cv, vx - 10, by - 1, vx + 10, by + 1, ramp, 3.0)
        for bx in (vx - 7, vx + 6):
            bolt(cv, bx, 152, ramp, 3.8)
            bolt(cv, bx, 162, ramp, 3.8)
        vpipe(cv, vx, 139, 149, 1, CAB, 4.0)
        box(cv, vx - 3, 142, vx + 3, 145, CAB, 3.2)
        handwheel(cv, vx, 136, 11, ramp)
        # plaqueta amb el nom, llegible
        lab = ('C.I.', 'LL.1', 'LL.2', 'LL.3')[i]
        w = text_width(lab)
        _label(cv, lab, vx - (w + 6) // 2, 171, ramp=WHITEP, lvl=3.8)
        # brides a terra
        box(cv, vx - 8, FLOOR_Y - 3, vx + 8, FLOOR_Y + 3, SEAG, 3.0)
        for bx in (vx - 6, vx + 5):
            bolt(cv, bx, FLOOR_Y - 1, SEAG, 3.6)
    for x in (27, 253):                                              # els taps del col·lector
        cv.disc(x, 123, 7, 8, SEAG, lambda nx, ny: 3.4 - nx - ny)
        for a in range(0, 360, 60):
            bolt(cv, x + round(math.cos(math.radians(a)) * 5), 123 + round(math.sin(math.radians(a)) * 5), SEAG, 4.0)
    # abraçadores a la paret
    for x in (34, 246):
        cv.vline(x, 114, 132, CAB, 2.0)
        cv.vline(x + 1, 114, 132, CAB, 3.4)
    # manòmetres al tub
    for k, gx in enumerate(GAUGES):
        vpipe(cv, gx, 104, 116, 1, CAB, 3.4)
        box(cv, gx - 2, 108, gx + 2, 110, BRASS, 3.6)                # l'aixeta del manòmetre
        cv.disc(gx, GAUGE_Y, 9, 9, CAB, lambda nx, ny: 2.6 - nx * 0.6 - ny * 0.6)
        cv.ring(gx, GAUGE_Y, 9, BRASS, 3.6, step=6)
        gauge_face(cv, gx, GAUGE_Y, gauge_angle(k))
        cv.put(gx - 3, GAUGE_Y - 4, WHITEP, 5.6)                     # reflex del vidre
        cv.put(gx - 4, GAUGE_Y - 3, WHITEP, 5.2)
    # els rètols
    _label(cv, 'C.I.', 24, 59, ramp=REDP, lvl=3.6, ink=(240, 230, 220))
    _label(cv, 'LLAST', 69, 59, ramp=SEAG, lvl=3.4, ink=(230, 236, 228))
    # un cartell de seguretat: «VÀLVULES: TANCAR DESPRÉS D'ÚS»
    x0, x1 = 150, 228
    box(cv, x0, 50, x1, 82, WHITEP, 4.2)
    cv.rect(x0 + 1, 51, x1 - 1, 61, REDP, 3.6)
    for s_, y, ink in (('ATENCIÓ', 55, (244, 236, 224)), ('TANCAR DESPRÉS', 67, INK), ("D'ÚS", 76, INK)):
        text(cv, s_, (x0 + x1 + 1 - text_width(s_)) // 2, y, None, 0, flat=ink)


# ─── Les bombes (dreta) ─────────────────────────────────────────────────────

def pump(cv, cx, body, tag, motor=ENG_LIGHT):
    """Bomba centrífuga vertical: bancada, voluta, llanterna i acoblament, motor amb aletes i la sortida."""
    base_y = FLOOR_Y + 3
    box(cv, cx - 32, base_y - 11, cx + 32, base_y, CAB, 2.8)
    cv.hline(cx - 31, cx + 31, base_y - 10, CAB, 4.0)
    for bx in (cx - 27, cx - 15, cx + 13, cx + 25):
        bolt(cv, bx, base_y - 6, CAB, 3.4)
    # la voluta
    vy = base_y - 27
    cv.disc(cx, vy, 23, 16, body, lambda nx, ny: 3.6 - nx * 1.2 - ny * 1.1)
    cv.disc(cx, vy, 11, 8, body, lambda nx, ny: 2.8 + nx * 0.6 + ny * 0.6)
    cv.disc(cx, vy, 4, 3, CAB, lambda nx, ny: 3.6 - nx - ny)
    for a in range(0, 360, 30):
        bolt(cv, cx + round(math.cos(math.radians(a)) * 18), vy + round(math.sin(math.radians(a)) * 12), body, 4.0)
    cv.put(cx - 6, vy + 14, body, 1.2)                               # el tap de purga
    cv.put(cx - 6, vy + 15, CAB, 3.6)
    # brides d'entrada (esquerra)
    hpipe(cv, cx - 40, cx - 20, vy, 5, body, 3.0)
    box(cv, cx - 22, vy - 8, cx - 19, vy + 8, body, 3.8)
    box(cv, cx - 41, vy - 8, cx - 38, vy + 8, body, 3.8)
    # la llanterna (suport) amb la finestra, l'eix i la protecció groga de l'acoblament
    ly0, ly1 = base_y - 69, base_y - 43
    box(cv, cx - 12, ly0, cx + 12, ly1, CAB, 2.8)
    cv.rect(cx - 7, ly0 + 5, cx + 7, ly1 - 5, DARK, 1.0)
    vpipe(cv, cx, ly0 + 2, ly1 - 2, 3, CAB, 4.6)
    box(cv, cx - 6, ly0 + 8, cx + 6, ly0 + 13, YELL, 3.8)
    for x in range(cx - 5, cx + 6, 3):
        cv.vline(x, ly0 + 9, ly0 + 12, YELL, 2.4)
    # el motor: cilindre amb aletes, la tapa del ventilador amb reixeta
    my0, my1 = base_y - 128, base_y - 70
    for y in range(my0, my1):
        for x in range(cx - 19, cx + 20):
            u = (x - cx) / 19.5
            fin = (x - cx) % 3 == 0
            cv.put(x, y, motor, 3.6 + 1.4 * (-0.3 - u) - 0.8 * u * u + (0.5 if fin else 0))
    box(cv, cx - 21, my1 - 5, cx + 21, my1, motor, 3.2)
    for bx in (cx - 18, cx + 17):
        bolt(cv, bx, my1 - 3, motor, 4.0)
    cv.disc(cx, my0 - 2, 17, 5, motor, lambda nx, ny: 3.8 - nx - ny)
    for x in range(cx - 13, cx + 14, 3):
        cv.put(x, my0 - 2, DARK, 1.4)
        cv.put(x + 1, my0 - 3, DARK, 1.8)
    # caixa de borns amb el premsaestopes i el cable cap a la safata
    box(cv, cx + 18, my0 + 17, cx + 29, my0 + 37, motor, 3.0)
    cv.hline(cx + 19, cx + 28, my0 + 18, motor, 4.2)
    box(cv, cx + 21, my0 + 14, cx + 25, my0 + 17, CAB, 3.4)
    vpipe(cv, cx + 23, 32, my0 + 14, 1, CAB, 2.6)
    # la placa de característiques, amb el nom i unes ratlles
    box(cv, cx - 11, my0 + 22, cx + 9, my0 + 34, WHITEP, 3.8)
    w = text_width(tag)
    text(cv, tag, cx - 1 - w // 2, my0 + 24, None, 0, flat=INK)
    for yy in (my0 + 31,):
        for x in range(cx - 9, cx + 8, 2):
            cv.put(x, yy, DARK, 1.6)
    # el sentit de gir: fletxa pintada
    cv.line(cx - 8, my0 + 44, cx + 6, my0 + 44, REDP, 3.6)
    cv.line(cx + 6, my0 + 44, cx + 3, my0 + 41, REDP, 3.6)
    cv.line(cx + 6, my0 + 44, cx + 3, my0 + 47, REDP, 3.6)
    # la sortida, cap amunt, amb la vàlvula de retenció
    vpipe(cv, cx + 40, 59, vy + 2, 5, body, 2.8, bands=(80,), band_ramp=WHITEP)
    hpipe(cv, cx + 19, cx + 40, vy, 5, body, 3.0)
    cv.disc(cx + 40, vy, 5, 5, body, lambda nx, ny: 3.4 - nx - ny)
    box(cv, cx + 34, 122, cx + 46, 134, body, 3.2)
    for by in (122, 134):
        cv.hline(cx + 33, cx + 47, by, body, 4.2)
    cv.disc(cx + 40, 128, 2, 2, CAB, 3.8)


def pumps(cv):
    hpipe(cv, 387, W - 1, 59, 5, SEAG, 3.0, bands=range(400, W, 67), band_ramp=WHITEP)
    for x in (395, 470, 545, 620):                                    # abraçadores al sostre
        cv.vline(x, 28, 52, CAB, 2.2)
        cv.vline(x + 1, 28, 52, CAB, 3.4)
    pump(cv, 411, REDP, 'C.I.')
    pump(cv, 501, SEAG, 'LL1')
    pump(cv, 584, SEAG, 'LL2')
    _label(cv, 'C.I.', 389, 75, ramp=REDP, lvl=3.6, ink=(240, 230, 220))
    _label(cv, 'LLAST 1', 467, 75, ramp=WHITEP, lvl=3.8)
    _label(cv, 'LLAST 2', 549, 75, ramp=WHITEP, lvl=3.8)


def panel(cv):
    """L'armari d'arrencada de les bombes: tots els pilots apagats (no va res)."""
    x0, y0, x1, y1 = 347, 93, 379, 171
    box(cv, x0, y0, x1, y1, CAB, 3.4, grad=0.8)
    cv.rect(x0 + 2, y0 + 2, x1 - 2, y0 + 3, CAB, 4.4)
    for bx, by in ((x0 + 2, y0 + 5), (x1 - 3, y0 + 5), (x0 + 2, y1 - 4), (x1 - 3, y1 - 4)):
        cv.put(bx, by, CAB, 5.0)
    for i, (y, lab) in enumerate(zip((105, 124, 143), ('CI', 'L1', 'L2'))):
        led = [(40, 10, 10), (80, 20, 20), (110, 34, 30)] if i == 0 else [(10, 30, 14), (20, 60, 26), (30, 84, 40)]
        cv.disc(x0 + 8, y, 3, 3, CAB, 1.0)
        cv.disc(x0 + 8, y, 2, 2, led, lambda nx, ny: 1.2 - nx * 0.3 - ny * 0.3)
        cv.put(x0 + 7, y - 1, led, 2.4)
        cv.disc(x0 + 22, y, 4, 4, CAB, 1.6)                           # el polsador, enfonsat
        cv.rect(x0 + 21, y - 3, x0 + 23, y, CAB, 4.4)
        text(cv, lab, x0 + 4, y + 5, None, 0, flat=(160, 168, 170))
    box(cv, x0 + 5, 155, x1 - 5, 162, WHITEP, 3.4)
    text(cv, 'MAN', x0 + 8, 156, None, 0, flat=INK)
    box(cv, x1 - 4, 128, x1 - 1, 139, CAB, 4.2)                       # la maneta
    vpipe(cv, x0 + 16, y1, FLOOR_Y, 2, CAB, 2.6)                     # el tub dels cables, a terra


# ─── Terra pintat, net i brillant ──────────────────────────────────────────

def floor(cv):
    mask = [[False] * W for _ in range(H)]
    vp = (320, 53)
    for y in range(FLOOR_Y, BOTTOM + 12):
        d = y - vp[1]
        for x in range(W):
            u = vp[0] + (x - vp[0]) * 200 / d
            u2 = vp[0] + (x + 1 - vp[0]) * 200 / d
            lv = 3.0 + (hr(x // 4, y // 2, 7) - 0.5) * 0.25
            if int(u // 128) != int(u2 // 128):
                lv -= 1.0
            elif y in (219, 243):
                lv -= 0.9
            elif y in (220, 244):
                lv += 0.4
            cv.put(x, y, FLOORP, lv)
            mask[y][x] = True
    # la línia groga de seguretat davant de les bombes (a ratlles)
    for y in range(FLOOR_Y + 5, FLOOR_Y + 8):
        for x in range(376, W):
            if ((x // 8) % 2) == 0:
                cv.put(x, y, YELL, 3.4 + (0.6 if y == FLOOR_Y + 5 else 0))
    return mask


def gloss(cv, mask, k=0.22):
    """Reflex suau de la paret al terra (pintura brillant) i dels llums."""
    src = cv.img.copy().load()
    for y in range(FLOOR_Y + 1, BOTTOM + 12):
        f = k * max(0.0, 1 - (y - FLOOR_Y) / 40)
        for x in range(W):
            if not mask[y][x]:
                continue
            sy = 2 * FLOOR_Y - y
            if 0 <= sy < FLOOR_Y:
                cv.flat(x, y, mix(cv.get(x, y), src[x, sy][:3], f))
    for lx in LAMPS:
        for y in range(FLOOR_Y + 2, FLOOR_Y + 40):
            t = (y - FLOOR_Y) / 40
            wdt = 4 + t * 7
            for x in range(int(lx - wdt * 2), int(lx + wdt * 2) + 1):
                if 0 <= x < W and mask[y][x]:
                    g = math.exp(-((x - lx) / wdt) ** 2) * (1 - t)
                    if g * 0.6 > B4[y & 3][x & 3]:
                        cv.flat(x, y, mix(cv.get(x, y), WARM, 0.2))


def floor_shadow(cv, cx, cy, rx, ry, k=0.6):
    cv.darken(cx - rx, cy - ry, cx + rx, cy + ry,
              lambda x, y: k * max(0.0, 1 - ((x - cx) / rx) ** 2 - ((y - cy) / ry) ** 2) * 1.6)


def cage_lamp(cv, lx, ly=29, top=21):
    box(cv, lx - 8, top, lx + 8, top + 5, CAB, 3.0)
    cv.hline(lx - 7, lx + 7, top, CAB, 4.2)
    cv.disc(lx, ly + 4, 8, 5, LAMPR, 2.6, lit=0)
    for gx in (-5, 0, 5):
        cv.vline(lx + gx, ly, ly + 9, CAB, 2.2, lit=0)
    cv.hline(lx - 8, lx + 8, ly + 5, CAB, 2.0, lit=0)


def lamp_glow(cv, lx, ly=29):
    glow(cv, lx, ly + 5, 45, WARM, 0.55)
    glow(cv, lx, ly + 5, 16, (255, 240, 200), 0.6)


# ─── Props ──────────────────────────────────────────────────────────────────

def book(cv):
    """El llibre de la Juana, obert de cara avall a terra (fa de teulada)."""
    floor_shadow(cv, 224, 245, 27, 4, 0.8)
    cv.poly([(200, 245), (224, 232), (224, 243), (203, 249)], BOOK, lambda x, y: 3.6 - (y - 232) * 0.04)
    cv.poly([(224, 232), (248, 243), (245, 248), (224, 243)], BOOK, lambda x, y: 2.6 - (y - 232) * 0.03)
    cv.line(224, 232, 224, 243, BOOK, 1.2)                           # el llom
    cv.line(200, 245, 224, 232, BOOK, 4.6)
    cv.line(224, 232, 248, 243, BOOK, 3.4)
    # les fulles, que es veuen per sota
    cv.line(203, 249, 224, 244, PAPER, 4.4)
    cv.line(224, 244, 245, 249, PAPER, 3.6)
    cv.line(204, 248, 223, 243, PAPER, 3.0)
    cv.line(226, 243, 244, 247, PAPER, 2.6)
    # un peix a la tapa (de perfil) i el punt de llibre vermell que en surt
    for dx, dy in ((0, 0), (1, 0), (2, -1), (3, -1), (4, -1), (5, -1), (1, -1), (2, 0), (3, 0), (4, 0), (6, -2), (6, 0)):
        cv.put(209 + dx, 241 + dy, WHITEP, 4.2)
    cv.put(213, 240, BOOK, 1.0)
    cv.line(235, 248, 239, 254, REDP, 3.8)
    cv.line(236, 248, 240, 254, REDP, 2.8)


def torch_body(cv):
    """La llanterna groga, a terra, apuntant cap a les bombes."""
    floor_shadow(cv, 300, 248, 24, 3, 0.8)
    for x in range(283, 309):
        for y in range(237, 248):
            u = (y - 242.5) / 5.5
            cv.put(x, y, TORCH, 3.8 - u * 1.3 - u * u, lit=0.4)
    for x in range(286, 306, 4):                                      # l'estriat de goma
        cv.vline(x, 238, 247, TORCH, 2.2, lit=0.4)
    box(cv, 309, 235, 316, 249, CAB, 3.6)
    cv.vline(317, 236, 248, [(120, 110, 80), (250, 240, 200), (255, 255, 240)], 2.2, lit=0)
    cv.rect(292, 239, 297, 241, DARK, 1.6, lit=0)                     # l'interruptor
    cv.put(293, 239, REDP, 3.6, lit=0)
    cv.hline(283, 283, 242, CAB, 3.0)
    cv.line(277, 248, 283, 244, DARK, 2.0)                            # el cordó
    cv.line(272, 250, 277, 248, DARK, 2.0)


def torch_beam(cv):
    """El feix de llum: un con a terra cap a la dreta, i una taca a la bancada de la bomba vermella."""
    for y in range(213, 261):
        for x in range(318, 459):
            t = (x - 318) / 141
            half = 4 + t * 35
            dy = abs(y - 242 + t * 8)
            if dy < half:
                k = 0.55 * (1 - t) ** 0.7 * (1 - (dy / half) ** 2)
                if k > B4[y & 3][x & 3] * 0.5:
                    cv.flat(x, y, mix(cv.get(x, y), (255, 238, 170), min(0.75, k + 0.1)))
    glow(cv, 317, 242, 13, (255, 250, 220), 0.9)
    glow(cv, 400, 200, 24, (255, 238, 170), 0.35)


_BASE = {}


def _base_img():
    if 'img' not in _BASE:
        b = Canvas(light=LIGHT)
        bg(b)
        _BASE['img'] = b.img
    return _BASE['img']


def _frame_base():
    cv = Canvas(light=LIGHT)
    cv.img = _base_img().copy()
    cv.P = cv.img.load()
    return cv


def prop_llanterna(cv):
    var = _frame_base()
    base = var.img.copy()
    torch_beam(var)
    torch_body(var)
    cv.img.alpha_composite(_diff(var.img, base))


# ─── Muntatge ───────────────────────────────────────────────────────────────

DRIP = (133, 131)           # on es forma la gota: sota el tub del col·lector
SPLASH_Y = FLOOR_Y + 8      # on cau, a terra
WATER = (196, 222, 214)


def puddle(cv):
    """El tollet que fa la gota a terra: una mica més fosc, amb un reflex."""
    x0, y0 = DRIP[0], SPLASH_Y
    for y in range(y0 - 2, y0 + 3):
        for x in range(x0 - 8, x0 + 9):
            if ((x - x0) / 7.5) ** 2 + ((y - y0) / 2.2) ** 2 <= 1:
                cv.flat(x, y, mix(cv.get(x, y), (10, 16, 16), 0.35))
    for dx, k in ((-3, 0.35), (-2, 0.3), (-1, 0.2)):
        cv.flat(x0 + dx, y0 - 1, mix(cv.get(x0 + dx, y0 - 1), WATER, k))


def bg(cv):
    walls(cv)
    ceiling(cv)
    manifold(cv)
    pumps(cv)
    panel(cv)
    hatch(cv)
    mask = floor(cv)
    gloss(cv, mask)
    floor_shadow(cv, 501, FLOOR_Y + 5, 147, 4, 0.5)
    floor_shadow(cv, 133, FLOOR_Y + 4, 120, 3, 0.4)
    for lx in LAMPS:
        cage_lamp(cv, lx)
    for lx in LAMPS:
        lamp_glow(cv, lx)
    glow(cv, 307, 8, 40, (190, 220, 190), 0.3)
    puddle(cv)


PROPS = {'llibre': book, 'llanterna': prop_llanterna}


# ─── Animacions ────────────────────────────────────────────────────────────

def _frames_manometres():
    """Les agulles dels dos manòmetres tremolen una mica (el motor principal es nota a tot el vaixell)."""
    base = _base_img()
    jitter = (0.0, 0.14, -0.06, 0.1, -0.14, 0.04)
    frames = []
    for i, j in enumerate(jitter):
        cv = _frame_base()
        for k, gx in enumerate(GAUGES):
            jj = j if k == 0 else -jitter[(i + 2) % len(jitter)]
            gauge_face(cv, gx, GAUGE_Y, gauge_angle(k, jj))
            cv.put(gx - 3, GAUGE_Y - 4, WHITEP, 5.6)
            cv.put(gx - 4, GAUGE_Y - 3, WHITEP, 5.2)
        frames.append(_diff(cv.img, base))
    return frames


def _frames_gota():
    """Una gota que s'infla sota el tub, cau i esquitxa el tollet; després, una estona de res."""
    base = _base_img()
    x, y0 = DRIP
    frames = []
    for i in range(20):
        cv = _frame_base()

        def w(px, py, k):
            cv.flat(px, py, mix(cv.get(px, py), WATER, k))
        if 4 <= i <= 8:                                   # la gota que es forma
            w(x, y0, 0.55 + 0.08 * (i - 4))
            if i >= 6:
                w(x, y0 + 1, 0.65 + 0.1 * (i - 6))
                w(x - 1, y0 + 1, 0.3)
            if i == 8:
                w(x, y0 + 2, 0.8)
        elif i in (9, 10):                                # cau (s'estira)
            yy = (152, 186)[i - 9]
            for d in range(4 + (i - 9) * 3):
                w(x, yy - d, 0.9 - d * 0.13)
        elif i == 11:                                     # esquitx
            w(x, SPLASH_Y - 1, 0.8)
            for dx, dy in ((-2, -3), (2, -3), (-4, -1), (4, -1), (0, -4), (-3, -2), (3, -2)):
                w(x + dx, SPLASH_Y + dy, 0.6)
        elif i in (12, 13, 14):                           # l'anell que s'obre al tollet
            r = 3 + (i - 12) * 2
            for dx in range(-r, r + 1):
                if abs(dx) >= r - 1:
                    w(x + dx, SPLASH_Y, 0.5 - (i - 12) * 0.15)
            w(x - r + 1, SPLASH_Y - 1, 0.3 - (i - 12) * 0.08)
            w(x + r - 1, SPLASH_Y - 1, 0.3 - (i - 12) * 0.08)
            w(x - r + 1, SPLASH_Y + 1, 0.25 - (i - 12) * 0.07)
            w(x + r - 1, SPLASH_Y + 1, 0.25 - (i - 12) * 0.07)
        frames.append(_diff(cv.img, base))
    return frames


ANIMS = {'manometres': {'frames': _frames_manometres, 'frameDuration': 140},
         'gota': {'frames': _frames_gota, 'frameDuration': 110}}


def _s(*v):
    return tuple(round(c * K) for c in v)


GEOMETRIA = {
    'things': {
        'escotilla': {'rect': _s(200, 0, 260, 152), 'walk': _s(230, 168)},
        'llibre': {'rect': _s(148, 170, 188, 190), 'walk': _s(166, 194)},
        'llanterna': {'rect': _s(206, 172, 242, 190), 'walk': _s(224, 194)},
        'bombes': {'rect': _s(282, 40, 476, 156), 'walk': _s(376, 172)},
    },
    'spawns': {cid: _s(*p) for cid, p in {'iri': (300, 190), 'vet': (360, 194), 'bastida': (110, 188)}.items()},
    'walkable': [_s(*p) for p in [(6, 164), (474, 164), (478, 197), (2, 197)]],
}
