"""
Postcrèdits: el mòbil de la Vet en primer pla, de nit. Un missatge de la Juana («Tinc una altra mostra.
Mostra 8. No és al mar.») i una foto: una gradeta de tubs d'anàlisi de sang amb l'etiqueta «Galway — Punt 7».
La mà de la Vet el sosté; al fons, la finestra amb els llums del port, desenfocats. A sota queda lloc per al
text. La Juana encara escriu (els tres puntets, ANIMS).
"""
import math

from hd.pix import Light, Canvas, W, H, hr, mix
from hd.rooms.comu import _diff, text, text_width

PHONE = (184, 6, 296, 178)
SCR = (190, 16, 290, 168)

LIGHT = Light(ambient=0.0, vignette=(90, 50), floor_fade=None)
LIGHT.point(240, 92, r=150, k=2.2, squash=0.9, power=1.6)       # la llum de la pantalla

ROOM = [(4, 4, 8), (8, 8, 14), (12, 12, 20), (18, 18, 28), (26, 26, 38)]
BODY = [(4, 4, 6), (10, 10, 12), (18, 18, 22), (28, 28, 34), (42, 42, 50), (60, 60, 70)]
UI = [(14, 18, 24), (22, 28, 36), (32, 40, 50), (46, 56, 68), (66, 78, 92)]
BUB = [(40, 44, 50), (60, 66, 74), (84, 90, 98), (112, 118, 124)]
SKIN = [(40, 24, 22), (74, 44, 36), (112, 72, 56), (150, 104, 80), (186, 138, 108), (214, 172, 140)]
SLEEVE = [(30, 32, 40), (52, 56, 66), (84, 88, 100), (120, 124, 134), (160, 164, 172)]
CAPS = [[(40, 10, 50), (90, 30, 110), (140, 70, 170)], [(60, 8, 10), (130, 20, 24), (200, 50, 44)],
        [(10, 40, 20), (24, 90, 44), (60, 150, 80)]]


def room(cv):
    """El fons: una habitació fosca i, a la finestra, els llums del port desenfocats."""
    for y in range(H):
        for x in range(W):
            cv.put(x, y, ROOM, 1.4 + (hr(x // 6, y // 6, 3) - 0.5) * 0.3)
    wx0, wy0, wx1, wy1 = 20, 20, 160, 150
    for y in range(wy0, wy1):
        for x in range(wx0, wx1):
            cv.put(x, y, [(6, 8, 18), (10, 14, 28), (14, 20, 40), (20, 28, 54)], 1.2 + (y - wy0) / 90, lit=0)
    for i in range(18):                                          # bokeh
        bx, by = wx0 + 8 + hr(i, 1) * (wx1 - wx0 - 16), wy0 + 50 + hr(i, 2) * 70
        col = (255, 196, 110) if hr(i, 3) > 0.35 else (120, 170, 255)
        r = 3 + hr(i, 4) * 6
        cv.glow(bx, by, r, col, 0.35 + hr(i, 5) * 0.3)
    for k in range(3):                                           # el marc i la creu de la finestra
        cv.rect(wx0 - 3, wy0 - 3, wx1 + 2, wy0 - 1, BODY, 1.6)
        cv.rect(wx0 - 3, wy1, wx1 + 2, wy1 + 3, BODY, 1.6)
        cv.rect(wx0 - 3, wy0, wx0 - 1, wy1, BODY, 1.6)
        cv.rect(wx1, wy0, wx1 + 2, wy1, BODY, 1.6)
    cv.rect((wx0 + wx1) // 2 - 1, wy0, (wx0 + wx1) // 2 + 1, wy1, BODY, 1.2)
    # gotes de pluja al vidre
    for i in range(40):
        gx, gy = int(wx0 + hr(i, 11) * (wx1 - wx0)), int(wy0 + hr(i, 12) * (wy1 - wy0))
        cv.flat(gx, gy, (60, 70, 96))
        cv.flat(gx, gy + 1, (30, 36, 56))


def phone(cv):
    x0, y0, x1, y1 = PHONE
    r = 10
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            dx = max(x0 + r - x, 0, x - (x1 - r))
            dy = max(y0 + r - y, 0, y - (y1 - r))
            if dx * dx + dy * dy <= r * r:
                edge = dx * dx + dy * dy > (r - 2) ** 2 or x in (x0, x1) or y in (y0, y1)
                cv.put(x, y, BODY, 2.6 if edge else 1.0, lit=0.4)
    cv.rect((x0 + x1) // 2 - 8, y0 + 4, (x0 + x1) // 2 + 8, y0 + 5, BODY, 2.6, lit=0)     # l'altaveu


def screen(cv, dots=0):
    x0, y0, x1, y1 = SCR
    cv.rect(x0, y0, x1, y1, UI, 1.0, lit=0)
    # la barra d'estat i la capçalera amb la Juana
    cv.rect(x0, y0, x1, y0 + 6, UI, 0.4, lit=0)
    text(cv, '04:12', x0 + 3, y0 + 1, [(200, 206, 214)], 0, lit=0, flat=(200, 206, 214))
    for k in range(4):
        cv.vline(x1 - 12 + k * 2, y0 + 5 - k, y0 + 5, [(200, 206, 214)], 0, lit=0)
    cv.rect(x0, y0 + 7, x1, y0 + 20, UI, 2.4, lit=0)
    cv.disc(x0 + 11, y0 + 13, 5, 5, [(150, 104, 80), (186, 138, 108)], lambda nx, ny: 1.0 - ny * 0.6, lit=0)
    cv.rect(x0 + 6, y0 + 8, x0 + 16, y0 + 10, [(24, 90, 44), (40, 120, 60)], 0.6, lit=0)  # la gorra verda
    text(cv, 'JUANA', x0 + 20, y0 + 11, [(236, 238, 240)], 0, lit=0, flat=(236, 238, 240))
    cv.hline(x0, x1, y0 + 20, UI, 3.4, lit=0)
    # el missatge
    lines = ['TINC UNA ALTRA', 'MOSTRA.', 'MOSTRA 8.', 'NO ÉS AL MAR.']
    bx0, by0 = x0 + 4, y0 + 26
    bw = max(text_width(s) for s in lines) + 8
    bh = len(lines) * 8 + 5
    bubble(cv, bx0, by0, bx0 + bw, by0 + bh)
    for i, s in enumerate(lines):
        text(cv, s, bx0 + 4, by0 + 4 + i * 8, [(232, 234, 236)], 0, lit=0, flat=(232, 234, 236))
    # la foto
    px0, py0, px1, py1 = x0 + 4, by0 + bh + 5, x0 + 84, by0 + bh + 66
    bubble(cv, px0, py0, px1, py1)
    photo(cv, px0 + 3, py0 + 3, px1 - 3, py1 - 3)
    # «escrivint...»
    if dots is not None:
        tx0, ty0 = x0 + 4, py1 + 5
        if ty0 + 9 <= y1:
            bubble(cv, tx0, ty0, tx0 + 22, ty0 + 9)
            for k in range(3):
                col = (230, 232, 236) if k == dots % 3 else (130, 136, 144)
                cv.rect(tx0 + 5 + k * 5, ty0 + 4, tx0 + 6 + k * 5, ty0 + 5, [col], 0, lit=0)
    cv.glow((x0 + x1) // 2, (y0 + y1) // 2, 120, (150, 180, 230), 0.06)


def bubble(cv, x0, y0, x1, y1):
    r = 3
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            dx = max(x0 + r - x, 0, x - (x1 - r))
            dy = max(y0 + r - y, 0, y - (y1 - r))
            if dx * dx + dy * dy <= r * r:
                cv.put(x, y, BUB, 1.0, lit=0)


def photo(cv, x0, y0, x1, y1):
    """La foto: una gradeta blanca amb sis tubs d'anàlisi i l'etiqueta «GALWAY - PUNT 7», sota un fluorescent."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, [(150, 156, 160), (180, 186, 188), (206, 210, 210), (226, 230, 228)],
                   2.4 - (y - y0) / 40 + (hr(x // 3, y // 3, 7) - 0.5) * 0.3, lit=0)
    # el taulell
    cv.rect(x0, y1 - 14, x1, y1, [(110, 116, 122), (140, 146, 150), (170, 174, 176)], 1.2, lit=0)
    # la gradeta
    gx0, gx1, gy = x0 + 8, x1 - 8, y1 - 26
    cv.rect(gx0, gy, gx1, gy + 4, [(200, 204, 206), (232, 236, 236)], 0.6, lit=0)
    cv.rect(gx0, gy + 14, gx1, gy + 18, [(170, 176, 178), (210, 214, 214)], 0.6, lit=0)
    cv.vline(gx0, gy, gy + 22, [(150, 156, 160)], 0, lit=0)
    cv.vline(gx1, gy, gy + 22, [(150, 156, 160)], 0, lit=0)
    n = 6
    for k in range(n):
        tx = gx0 + 5 + k * (gx1 - gx0 - 8) // (n - 1)
        cap = CAPS[0 if k < 3 else 1 if k < 5 else 2]
        cv.rect(tx - 2, gy - 12, tx + 1, gy + 16, [(160, 40, 40), (120, 20, 26)], 0.6, lit=0)   # la sang
        cv.rect(tx - 2, gy - 12, tx + 1, gy - 4, [(220, 224, 226)], 0, lit=0)                # l'etiqueta
        cv.hline(tx - 1, tx, gy - 9, [(80, 80, 90)], 0, lit=0)
        cv.rect(tx - 3, gy - 17, tx + 2, gy - 13, cap, 1.4, lit=0)
        cv.vline(tx + 1, gy - 12, gy + 16, [(250, 250, 250)], 0, lit=0)
    # l'etiqueta de la gradeta
    s = 'GALWAY - PUNT 7'
    w = text_width(s)
    lx = (x0 + x1) // 2 - w // 2
    cv.rect(lx - 2, y1 - 11, lx + w + 1, y1 - 4, [(236, 232, 210)], 0, lit=0)
    text(cv, s, lx, y1 - 10, [(30, 30, 40)], 0, lit=0, flat=(30, 30, 40))


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
    # el palmell, sota el mòbil: s'esvaeix (a quadres) cap a la foscor
    for y in range(y1 - 3, 226):
        k = (y - y1 + 3) / 50
        half = (x1 - x0) / 2 + 6 + k * 8 - max(0.0, k - 0.6) * 30
        cxm = (x0 + x1) / 2 + 2
        for x in range(int(cxm - half), int(cxm + half) + 1):
            if k > 0.45 and hr(x, y, 21) < (k - 0.45) / 0.55:
                continue
            cv.put(x, y, SKIN, 2.8 - k * 1.6 - abs(x - cxm) / 70)
    # el dors de la mà, que embolcalla el mòbil per la dreta (a l'ombra)
    cv.poly([(x1 - 1, 92), (x1 + 12, 98), (x1 + 16, y1 + 4), (x1 - 1, y1 + 2)], SKIN, lambda x, y: 1.4 + (y - 92) * 0.004)
    # els dits, a la dreta: les puntes sobresurten per sobre la vora del mòbil
    for k, fy in enumerate((98, 113, 128, 143)):
        capsule(cv, x1 + 12 - k, fy + 6, x1 - 4, fy + 1, 6.5 - k * 0.4, SKIN, 3.0 - k * 0.15, light=(0.4, -0.9))
        cv.put(x1 - 7, fy - 2, SKIN, 4.6)
        cv.put(x1 - 6, fy - 3, SKIN, 4.4)
    # el polze, per l'esquerra
    capsule(cv, x0 - 10, 196, x0 + 3, 150, 6, SKIN, 3.0)
    cv.put(x0 + 2, 145, SKIN, 4.6)
    cv.put(x0 + 3, 146, SKIN, 4.4)


def phone_bottom(cv):
    """La vora de sota del mòbil, per damunt del palmell."""
    x0, y0, x1, y1 = PHONE
    cv.rect(x0 + 6, y1 - 4, x1 - 6, y1, BODY, 2.0, lit=0.4)
    cv.hline(x0 + 6, x1 - 6, y1, BODY, 3.0, lit=0.4)


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
