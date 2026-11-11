"""
Prova a 640×360: els postcrèdits (vegeu hd/rooms/postcredits.py, la de 480×270). El mòbil de la Vet en primer
pla, de nit. Un missatge de la Juana («Tinc una altra mostra. Mostra 8. No és al mar.») i una foto: una gradeta
de tubs d'anàlisi de sang amb l'etiqueta «GALWAY - PUNT 7». La mà de la Vet el sosté; al fons, la finestra amb els
llums del port, desenfocats, i la pluja al vidre. A sota queda lloc per al text.
Mateixa composició ×4/3, dibuixada de nou: el missatge ja no va en majúscules de 5 px, sinó amb la lletra del joc
(hd640/font.py), en minúscules i llegible; la capçalera diu «Juana» i «en línia», les bombolles porten l'hora i
les marques de llegit, i la foto té més detall (els tubs amb etiqueta i tap, el fluorescent, el taulell).
Cinemàtica: no hi ha barra de verbs. ANIMS: `escrivint` (els tres puntets de la Juana).
"""
import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

import math

from hd.pix import Light, Canvas, W, H, hr
from hd.rooms.comu import _diff, text, text_width
from hd640.font import font640, text_width as fw, draw_text

PHONE = (245, 8, 395, 237)
SCR = (253, 21, 387, 224)

LIGHT = Light(ambient=0.0, vignette=(120, 67), floor_fade=None)
LIGHT.point(320, 123, r=200, k=2.2, squash=0.9, power=1.6)       # la llum de la pantalla

ROOM = [(4, 4, 8), (8, 8, 14), (12, 12, 20), (18, 18, 28), (26, 26, 38)]
BODY = [(4, 4, 6), (10, 10, 12), (18, 18, 22), (28, 28, 34), (42, 42, 50), (60, 60, 70)]
UI = [(14, 18, 24), (22, 28, 36), (32, 40, 50), (46, 56, 68), (66, 78, 92)]
BUB = [(40, 44, 50), (60, 66, 74), (84, 90, 98), (112, 118, 124)]
SKIN = [(40, 24, 22), (74, 44, 36), (112, 72, 56), (150, 104, 80), (186, 138, 108), (214, 172, 140), (232, 198, 170)]
NAIL = [(150, 110, 100), (196, 160, 150), (226, 200, 192)]
CAPS = [[(40, 10, 50), (90, 30, 110), (140, 70, 170), (180, 120, 210)],
        [(60, 8, 10), (130, 20, 24), (200, 50, 44), (230, 100, 80)],
        [(10, 40, 20), (24, 90, 44), (60, 150, 80), (110, 200, 120)]]
TXT = (232, 234, 236)
DIM = (150, 158, 168)


def room(cv):
    """El fons: una habitació fosca i, a la finestra, els llums del port desenfocats i la pluja."""
    for y in range(H):
        for x in range(W):
            cv.put(x, y, ROOM, 1.4 + (hr(x // 8, y // 8, 3) - 0.5) * 0.3)
    wx0, wy0, wx1, wy1 = 27, 27, 213, 200
    for y in range(wy0, wy1):
        for x in range(wx0, wx1):
            cv.put(x, y, [(6, 8, 18), (10, 14, 28), (14, 20, 40), (20, 28, 54)], 1.2 + (y - wy0) / 120, lit=0)
    # l'altra riba: una ratlla de llums petits, i el reflex a l'aigua
    for i in range(30):
        lx = wx0 + 4 + int(hr(i, 31) * (wx1 - wx0 - 8))
        cv.flat(lx, wy0 + 92, (200, 160, 100) if hr(i, 32) > 0.4 else (120, 150, 220))
    for i in range(24):                                          # bokeh
        bx, by = wx0 + 10 + hr(i, 1) * (wx1 - wx0 - 20), wy0 + 66 + hr(i, 2) * 94
        col = (255, 196, 110) if hr(i, 3) > 0.35 else (120, 170, 255)
        r = 4 + hr(i, 4) * 8
        cv.glow(bx, by, r, col, 0.35 + hr(i, 5) * 0.3)
        if r > 8:                                                # la vora més clara dels discos grans
            for a in range(0, 360, 15):
                px, py = bx + math.cos(math.radians(a)) * (r * 0.55), by + math.sin(math.radians(a)) * (r * 0.55)
                if hr(int(px), int(py), 6) > 0.6:
                    o = cv.get(px, py)
                    cv.flat(px, py, tuple(min(255, c + 18) for c in o[:3]))
    # el marc i la creu de la finestra
    cv.rect(wx0 - 4, wy0 - 4, wx1 + 3, wy0 - 1, BODY, 1.6)
    cv.rect(wx0 - 4, wy1, wx1 + 3, wy1 + 4, BODY, 1.6)
    cv.hline(wx0 - 4, wx1 + 3, wy1, BODY, 2.6)
    cv.rect(wx0 - 4, wy0, wx0 - 1, wy1, BODY, 1.6)
    cv.rect(wx1, wy0, wx1 + 3, wy1, BODY, 1.6)
    cx = (wx0 + wx1) // 2
    cv.rect(cx - 1, wy0, cx + 1, wy1, BODY, 1.2)
    # gotes de pluja al vidre: el cap i un regalim
    for i in range(70):
        gx, gy = int(wx0 + hr(i, 11) * (wx1 - wx0)), int(wy0 + hr(i, 12) * (wy1 - wy0))
        cv.flat(gx, gy, (70, 80, 108))
        cv.flat(gx, gy + 1, (30, 36, 56))
        if hr(i, 13) > 0.7:
            for k in range(2, 2 + int(hr(i, 14) * 8)):
                if gy + k < wy1:
                    cv.flat(gx + (k // 5), gy + k, (40, 48, 72))


def _round(cv, x0, y0, x1, y1, r, ramp, lvl, lit=0.0, edge_lvl=None):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            dx = max(x0 + r - x, 0, x - (x1 - r))
            dy = max(y0 + r - y, 0, y - (y1 - r))
            if dx * dx + dy * dy <= r * r:
                edge = edge_lvl is not None and (dx * dx + dy * dy > (r - 2) ** 2 or x in (x0, x1) or y in (y0, y1))
                cv.put(x, y, ramp, edge_lvl if edge else lvl, lit=lit)


def phone(cv):
    x0, y0, x1, y1 = PHONE
    _round(cv, x0, y0, x1, y1, 13, BODY, 1.0, lit=0.4, edge_lvl=2.6)
    cv.vline(x0 + 1, y0 + 14, y1 - 14, BODY, 3.6, lit=0.4)         # la llum a la vora esquerra
    cx = (x0 + x1) // 2
    _round(cv, cx - 11, y0 + 5, cx + 11, y0 + 7, 1, BODY, 2.6)     # l'altaveu
    cv.disc(cx + 18, y0 + 6, 1.5, 1.5, [(10, 12, 20), (30, 34, 60), (60, 70, 120)], 1.6, lit=0)   # la càmera
    cv.vline(x0 - 1, y0 + 46, y0 + 66, BODY, 2.2, lit=0.4)         # els botons del volum
    cv.vline(x0 - 1, y0 + 72, y0 + 84, BODY, 2.2, lit=0.4)


def bubble(cv, x0, y0, x1, y1, ramp=BUB, lvl=1.0):
    _round(cv, x0, y0, x1, y1, 4, ramp, lvl)


def screen(cv, dots=0):
    x0, y0, x1, y1 = SCR
    cv.rect(x0, y0, x1, y1, UI, 1.0, lit=0)
    # fons del xat: un patró molt fluix
    for y in range(y0 + 30, y1):
        for x in range(x0, x1 + 1):
            if (x + y * 3) % 23 == 0 and hr(x, y, 40) > 0.5:
                cv.put(x, y, UI, 1.6, lit=0)
    # la barra d'estat: hora, cobertura i bateria
    cv.rect(x0, y0, x1, y0 + 8, UI, 0.4, lit=0)
    text(cv, '04:12', x0 + 4, y0 + 2, [TXT], 0, lit=0, flat=(200, 206, 214))
    for k in range(4):
        cv.vline(x1 - 22 + k * 2, y0 + 6 - k, y0 + 6, [(200, 206, 214)], 0, lit=0)
    cv.rect(x1 - 12, y0 + 2, x1 - 3, y0 + 6, [(200, 206, 214)], 0, lit=0)
    cv.rect(x1 - 11, y0 + 3, x1 - 8, y0 + 5, [(14, 18, 24)], 0, lit=0)
    cv.vline(x1 - 2, y0 + 3, y0 + 5, [(200, 206, 214)], 0, lit=0)
    # la capçalera: la fletxa enrere, la Juana (amb la gorra verda) i «en línia»
    cv.rect(x0, y0 + 9, x1, y0 + 30, UI, 2.4, lit=0)
    for k in range(4):
        cv.flat(x0 + 6 + k, y0 + 19 - k, (200, 206, 214))
        cv.flat(x0 + 6 + k, y0 + 19 + k, (200, 206, 214))
    ax, ay = x0 + 23, y0 + 20
    cv.disc(ax, ay, 7, 7, [(60, 60, 70), (90, 90, 100)], 1.0, lit=0)
    cv.disc(ax, ay + 1, 5, 5, [(112, 72, 56), (150, 104, 80), (186, 138, 108)], lambda nx, ny: 1.6 - ny * 0.6, lit=0)
    cv.rect(ax - 6, ay - 6, ax + 6, ay - 3, [(14, 60, 30), (24, 90, 44), (40, 120, 60)], 1.4, lit=0)   # la gorra
    cv.rect(ax - 4, ay - 1, ax + 4, ay, [(40, 40, 46)], 0, lit=0)                                    # les ulleres
    cv.flat(ax - 2, ay, (200, 220, 240))
    cv.flat(ax + 2, ay, (200, 220, 240))
    bold, reg = font640(True), font640(False)
    draw_text(cv.img, bold, 'Juana', x0 + 34, y0 + 7, TXT, outline=None)
    text(cv, 'EN LÍNIA', x0 + 35, y0 + 23, [(90, 200, 120)], 0, lit=0, flat=(90, 200, 120))
    cv.hline(x0, x1, y0 + 30, UI, 3.4, lit=0)
    # el missatge, en tres bombolles
    y = y0 + 36
    for lines, hour in ((('Tinc una altra', 'mostra.'), None), (('Mostra 8.',), None), (('No és al mar.',), '04:11')):
        bw = max(fw(reg, s) for s in lines) + 10
        if hour:
            bw = max(bw, fw(reg, lines[-1]) + 10 + text_width(hour) + 4)
        bh = len(lines) * 11 + 6
        bubble(cv, x0 + 5, y, x0 + 5 + bw, y + bh)
        for i, s in enumerate(lines):
            draw_text(cv.img, reg, s, x0 + 10, y - 2 + i * 11, TXT, outline=None)
        if hour:
            text(cv, hour, x0 + 5 + bw - text_width(hour) - 3, y + bh - 7, [DIM], 0, lit=0, flat=DIM)
        y += bh + 3
    # la foto
    px0, py0, px1, py1 = x0 + 5, y + 1, x0 + 113, y + 72
    bubble(cv, px0, py0, px1, py1)
    photo(cv, px0 + 3, py0 + 3, px1 - 3, py1 - 3)
    y = py1
    # «escrivint...»
    if dots is not None:
        tx0, ty0 = x0 + 5, y + 5
        if ty0 + 11 <= y1:
            bubble(cv, tx0, ty0, tx0 + 28, ty0 + 11)
            for k in range(3):
                col = (230, 232, 236) if k == dots % 3 else (120, 126, 134)
                cv.disc(tx0 + 8 + k * 6, ty0 + 5.5 - (1 if k == dots % 3 else 0), 1.5, 1.5, [col], 0, lit=0)
    cv.glow((x0 + x1) // 2, (y0 + y1) // 2, 160, (150, 180, 230), 0.06)


def photo(cv, x0, y0, x1, y1):
    """La foto: una gradeta blanca amb sis tubs d'anàlisi i l'etiqueta «GALWAY - PUNT 7», sota un fluorescent."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, [(150, 156, 160), (180, 186, 188), (206, 210, 210), (226, 230, 228)],
                   2.4 - (y - y0) / 50 + (hr(x // 4, y // 4, 7) - 0.5) * 0.3, lit=0)
    # el fluorescent, a dalt, i la rajola de la paret
    cv.rect(x0 + 10, y0 + 1, x1 - 10, y0 + 2, [(250, 252, 250)], 0, lit=0)
    for x in range(x0, x1 + 1, 12):
        cv.vline(x, y0 + 4, y1 - 18, [(170, 176, 178)], 0, lit=0)
    cv.hline(x0, x1, y0 + 16, [(170, 176, 178)], 0, lit=0)
    # el taulell
    cv.rect(x0, y1 - 18, x1, y1, [(110, 116, 122), (140, 146, 150), (170, 174, 176)], 1.2, lit=0)
    cv.hline(x0, x1, y1 - 18, [(190, 194, 196)], 0, lit=0)
    # la gradeta
    gx0, gx1, gy = x0 + 11, x1 - 11, y1 - 31
    cv.rect(gx0, gy, gx1, gy + 4, [(200, 204, 206), (232, 236, 236)], 0.6, lit=0)
    cv.rect(gx0, gy + 15, gx1, gy + 19, [(170, 176, 178), (210, 214, 214)], 0.6, lit=0)
    cv.vline(gx0, gy, gy + 26, [(150, 156, 160)], 0, lit=0)
    cv.vline(gx1, gy, gy + 26, [(150, 156, 160)], 0, lit=0)
    n = 6
    for k in range(n):
        tx = gx0 + 7 + k * (gx1 - gx0 - 11) // (n - 1)
        cap = CAPS[0 if k < 3 else 1 if k < 5 else 2]
        cv.rect(tx - 3, gy - 13, tx + 1, gy + 18, [(160, 40, 40), (120, 20, 26)], 0.6, lit=0)   # la sang
        cv.rect(tx - 3, gy - 13, tx + 1, gy - 4, [(220, 224, 226)], 0, lit=0)                # l'etiqueta
        cv.hline(tx - 2, tx, gy - 11, [(80, 80, 90)], 0, lit=0)
        cv.hline(tx - 2, tx - 1, gy - 8, [(80, 80, 90)], 0, lit=0)
        cv.rect(tx - 4, gy - 19, tx + 2, gy - 14, cap, lambda x, y: 2.6 - (x - tx + 4) * 0.3, lit=0)
        cv.vline(tx + 1, gy - 13, gy + 18, [(250, 250, 250)], 0, lit=0)
    # l'etiqueta de la gradeta
    s = 'GALWAY - PUNT 7'
    w = text_width(s)
    lx = (x0 + x1) // 2 - w // 2
    cv.rect(lx - 3, y1 - 13, lx + w + 2, y1 - 5, [(236, 232, 210)], 0, lit=0)
    text(cv, s, lx, y1 - 12, [(30, 30, 40)], 0, lit=0, flat=(30, 30, 40))


def capsule(cv, ax, ay, bx, by, r, ramp, lvl, light=(-0.6, -0.8)):
    """Un dit: càpsula de (ax, ay) a (bx, by), de radi r, amb volum."""
    L = math.hypot(bx - ax, by - ay) or 1
    for y in range(int(min(ay, by) - r - 1), int(max(ay, by) + r + 2)):
        for x in range(int(min(ax, bx) - r - 1), int(max(ax, bx) + r + 2)):
            t = max(0.0, min(1.0, ((x - ax) * (bx - ax) + (y - ay) * (by - ay)) / (L * L)))
            px, py = ax + (bx - ax) * t, ay + (by - ay) * t
            d = math.hypot(x - px, y - py)
            if d <= r:
                nx, ny = (x - px) / r, (y - py) / r
                cv.put(x, y, ramp, lvl + (nx * light[0] + ny * light[1]) * 1.4 - (d / r) ** 2 * 0.8)


def hand(cv):
    """La mà de la Vet: quatre dits que abracen el mòbil per la dreta, el polze per l'esquerra i el palmell a
    sota, que s'esvaeix a la foscor (a sota hi va el text)."""
    x0, y0, x1, y1 = PHONE
    for y in range(y1 - 4, 301):                                  # el palmell, que s'esvaeix a quadres
        k = (y - y1 + 4) / 67
        half = (x1 - x0) / 2 + 8 + k * 11 - max(0.0, k - 0.6) * 40
        cxm = (x0 + x1) / 2 + 3
        for x in range(int(cxm - half), int(cxm + half) + 1):
            if k > 0.45 and hr(x, y, 21) < (k - 0.45) / 0.55:
                continue
            cv.put(x, y, SKIN, 2.8 - k * 1.6 - abs(x - cxm) / 90)
    # el dors de la mà, que embolcalla el mòbil per la dreta (a l'ombra)
    cv.poly([(x1 - 1, 123), (x1 + 16, 131), (x1 + 21, y1 + 5), (x1 - 1, y1 + 3)], SKIN, lambda x, y: 1.4 + (y - 123) * 0.004)
    # els dits, a la dreta: les puntes sobresurten per sobre la vora del mòbil, amb l'ungla
    for k, fy in enumerate((131, 151, 171, 191)):
        r = 8.6 - k * 0.5
        capsule(cv, x1 + 16 - k, fy + 8, x1 - 5, fy + 1, r, SKIN, 3.0 - k * 0.15, light=(0.4, -0.9))
        tip = x1 - 5 - int(r) + 2
        cv.put(tip + 1, fy - 3, SKIN, 4.8)
        cv.put(tip + 2, fy - 4, SKIN, 4.6)
        for dx in range(3):                                       # l'ungla, de cantó
            cv.put(tip + dx, fy - 1, NAIL, 1.6 - dx * 0.4, lit=0.5)
        cv.put(x1 + 6 - k, fy + 7, SKIN, 1.4)                     # el plec del nus
    # el polze, per l'esquerra
    capsule(cv, x0 - 13, 261, x0 + 4, 200, 8, SKIN, 3.0)
    cv.put(x0 + 3, 193, SKIN, 4.8)
    cv.put(x0 + 4, 194, SKIN, 4.6)
    for dx in range(3):
        cv.put(x0 + 1 + dx, 197, NAIL, 1.8 - dx * 0.4, lit=0.5)


def bg(cv, dots=0):
    room(cv)
    phone(cv)
    screen(cv, dots)
    hand(cv)


PROPS = {}


def _frames():
    base = Canvas(light=LIGHT)
    bg(base)
    frames = []
    for i in range(3):
        cv = Canvas(light=LIGHT, img=base.img.copy())
        screen(cv, i)
        hand(cv)
        frames.append(_diff(cv.img, base.img))
    return frames


ANIMS = {'escrivint': {'frames': _frames, 'frameDuration': 380}}

GEOMETRIA = {'things': {}, 'spawns': {}}
