"""
El bar La Propina (Escena 2, la Vet), dilluns de nit, a la sortida de l'autopista. Art definitiu, amb l'estil de
la sala de mostra (pis_estudi):
  - bar de carretera: arrimador de fusta, paret groguenca de fum vell, terra de terratzo amb tovallons;
  - la llum: un fluorescent groguenc damunt la barra, la tele (blava), l'escurabutxaques (colors) i el neó
    magenta «LA PROPINA» a l'aparador, que des de dins es llegeix del revés;
  - el rètol del lema d'en Tomàs, pintat a mà: «AVUI NO ES FIA, DEMÀ SÍ» (la
    contrasenya del pany, Trencaclosques 2.2);
  - la cafetera exprés amb el vaporitzador (el tap, Trencaclosques 2.1), la cervesera, el pot de les propines,
    la caixa registradora i un pernil.
"""
import math

from hd.pix import Light, Canvas, W, H, hr
from hd.rooms.comu import (obox, outline, cable, text, text_width, _diff, PLASTIC, SCREEN, SKY, CITY, NEON, SHEET, GRAYC,
                           YEL, CARD, RED)
from hd.rooms.pis_cuina import outline_poly

FLOOR_Y = 150
BAR_TOP = 112      # el taulell de la barra: cantell del darrere
BAR_FRONT = 120    # cantell del davant

WALLY = [(20, 14, 8), (34, 24, 14), (50, 36, 20), (68, 50, 28), (88, 66, 36), (110, 84, 46), (132, 104, 58), (156, 126, 74), (180, 150, 92)]
WOOD = [(14, 6, 4), (26, 12, 8), (42, 20, 12), (60, 30, 16), (80, 42, 22), (102, 56, 28), (126, 72, 36), (152, 92, 48), (180, 116, 64)]
FORMICA = [(24, 10, 8), (48, 18, 14), (76, 28, 20), (104, 40, 26), (134, 54, 32), (162, 72, 40), (188, 96, 54)]
STEELB = [(10, 12, 16), (20, 24, 30), (34, 38, 46), (50, 56, 66), (70, 78, 90), (96, 104, 116), (130, 138, 150), (176, 182, 190), (220, 224, 228)]
BRASS = [(30, 20, 6), (64, 44, 12), (110, 80, 22), (160, 120, 40), (206, 166, 70), (240, 210, 120), (255, 240, 190)]
TERRAZ = [(12, 10, 10), (22, 20, 18), (36, 32, 28), (52, 48, 42), (70, 64, 56), (92, 84, 74), (116, 108, 96)]
SLATE = [(6, 8, 10), (12, 14, 18), (20, 22, 28), (30, 32, 40), (42, 44, 54)]
PORC = [(30, 30, 40), (56, 56, 66), (90, 88, 96), (128, 126, 128), (168, 164, 160), (204, 200, 192), (236, 232, 222)]
HAM = [(30, 8, 6), (60, 16, 10), (100, 30, 18), (140, 50, 30), (176, 84, 56), (206, 130, 96), (230, 180, 150)]
ENAMEL = [(40, 34, 24), (80, 72, 54), (130, 120, 92), (176, 166, 132), (214, 204, 168), (238, 230, 200)]
TVB = [(4, 8, 20), (8, 18, 40), (14, 32, 70), (24, 54, 110), (50, 90, 160), (120, 160, 220)]
PITCH = [(4, 16, 6), (10, 36, 12), (18, 62, 20), (30, 92, 30), (50, 122, 44), (90, 160, 70)]
GLASSD = [(4, 6, 12), (8, 10, 20), (12, 16, 30), (18, 22, 42), (26, 30, 56)]
BOTTLES = ([(4, 16, 6), (10, 40, 14), (20, 70, 26), (40, 110, 50), (90, 170, 100)],     # verd
           [(30, 12, 4), (70, 30, 8), (120, 60, 14), (170, 100, 30), (220, 160, 70)],  # ambre
           [(30, 30, 40), (70, 70, 90), (120, 120, 140), (180, 180, 200), (230, 230, 240)],  # transparent
           [(30, 4, 8), (70, 10, 18), (120, 20, 30), (170, 40, 50), (220, 90, 90)],    # vermell
           [(20, 14, 30), (40, 30, 70), (70, 56, 120), (110, 90, 170), (170, 150, 220)])  # blau

LAMP_Y = 58
LIGHT = Light(ambient=-0.5, vignette=(60, 34), floor_fade=(192, 26))
LIGHT.point(240, LAMP_Y, r=220, k=3.2, squash=1.3, power=1.5)        # el fluorescent del sostre, damunt la barra (fora de quadre)
LIGHT.point(365, 64, r=60, k=0.8, squash=1.0, power=2.0)              # la tele
LIGHT.point(83, 110, r=50, k=0.9, squash=1.0, power=2.0)              # l'escurabutxaques
LIGHT.point(109, 40, r=50, k=0.6, squash=1.0, power=2.0)              # el neó de l'aparador


# ─── Paret i terra ──────────────────────────────────────────────────────────

def wall(cv):
    """Paret de guix groguenca (el fum de quan es fumava a dins) i arrimador de fusta fins a mitja paret."""
    for y in range(0, FLOOR_Y):
        for x in range(W):
            n = (hr(x // 3, y // 3) - 0.5) * 0.3 + (hr(x // 13, y // 10, 5) - 0.5) * 0.5
            if y >= 98:
                plank = (x // 14)
                seam = x % 14 == 0
                cv.put(x, y, WOOD, (1.0 if seam else 2.6 + (hr(plank, 2) - 0.5) * 0.5) + (0.4 if y == 99 else 0))
            else:
                cv.put(x, y, WALLY, 2.4 + n)
    cv.rect(0, 95, W - 1, 97, WOOD, 3.4)                     # la motllura de l'arrimador
    cv.hline(0, W - 1, 95, WOOD, 4.6)
    cv.hline(0, W - 1, 98, WOOD, 0.6)
    cv.rect(0, FLOOR_Y - 4, W - 1, FLOOR_Y - 1, WOOD, 1.4)  # sòcol
    cv.hline(0, W - 1, FLOOR_Y, WOOD, 0)


def floor(cv):
    """Terratzo gris, gastat, amb tovallons de paper i escuradents."""
    for y in range(FLOOR_Y + 1, H):
        dep = (y - FLOOR_Y) / (H - FLOOR_Y)
        v = (y - FLOOR_Y) * 2.0 / (1 + dep * 0.6)
        for x in range(W):
            u = (x - W / 2) / (1 + dep * 0.6) + W / 2
            if (u % 40) < 0.9 or (v % 30) < 0.9:
                cv.put(x, y, TERRAZ, 1.2)
                continue
            chip = hr(x, y, 3)
            lvl = 2.8 + (hr(int(u // 40), int(v // 30)) - 0.5) * 0.4
            if chip > 0.93:
                lvl += 1.4
            elif chip < 0.06:
                lvl -= 1.2
            cv.put(x, y, TERRAZ, lvl)
    # tovallons arrugats i escuradents (sobretot davant de la barra)
    for i in range(16):
        x = 110 + int(hr(i, 11) * 300)
        y = 160 + int(hr(i, 12) * 38)
        if hr(i, 13) > 0.4:
            cv.disc(x, y, 2.4, 1.4, SHEET, lambda nx, ny: 4.2 - ny - nx * 0.5)
        else:
            cv.line(x, y, x + 4, y + (1 if i % 2 else -1), CARD, 4.0)
    # el reflex del fluorescent al terra
    cv.tint(140, 156, 340, 200, (230, 220, 160), lambda x, y: 0.08 * max(0, 1 - abs(x - 240) / 100) * max(0, 1 - (y - 156) / 44))


# ─── La paret del fons ─────────────────────────────────────────────────────

def window(cv, flick=0):
    """L'aparador: fora, la nit i l'autopista; el neó «LA PROPINA» es llegeix del revés."""
    x0, y0, x1, y1 = 78, 20, 140, 60
    for y in range(y0 + 2, y1 - 1):
        for x in range(x0 + 2, x1 - 1):
            cv.put(x, y, SKY, 0.8 + (y - y0) / 22, lit=0)
    # el talús de l'autopista i els fanals
    for x in range(x0 + 2, x1 - 1):
        top = 48 - int(3 * math.sin(x / 9))
        for y in range(top, y1 - 1):
            cv.put(x, y, CITY, 1.2, lit=0)
    for lx in (88, 112, 134):
        cv.vline(lx, 30, 47, CITY, 2.4, lit=0)
        cv.hline(lx, lx + 3, 30, CITY, 2.4, lit=0)
        cv.flat(lx + 3, 31, (250, 200, 120))
        cv.glow(lx + 3, 32, 6, (250, 190, 110), 0.4)
    # el neó (vist del revés, des de dins)
    w = text_width('LA PROPINA')
    on = (255, 120, 200) if flick != 1 else (140, 40, 100)
    text(cv, 'LA PROPINA', (x0 + x1 - w) // 2, 36, NEON, 0, lit=0, mirror=True, flat=on)
    if flick != 1:
        cv.glow((x0 + x1) // 2, 38, 26, (255, 90, 200), 0.35)
    # marc d'alumini
    for (a, b, c, d) in ((x0, y0, x1, y0 + 1), (x0, y1 - 1, x1, y1), (x0, y0, x0 + 1, y1), (x1 - 1, y0, x1, y1)):
        cv.rect(a, b, c, d, STEELB, 3.4)
    outline(cv, x0 - 1, y0 - 1, x1 + 1, y1 + 1, STEELB)


def sign(cv):
    """El rètol del lema, pintat a mà en una planxa esmaltada, una mica tort i amb dos claus."""
    x0, y0, x1, y1 = 152, 20, 308, 46
    pts = [(x0, y0 + 1), (x1, y0 - 1), (x1, y1 - 1), (x0, y1 + 1)]
    cv.poly(pts, ENAMEL, lambda x, y: 3.8 + (hr(x // 4, y // 4) - 0.5) * 0.5 - (0.8 if (x - x0) < 3 or (x1 - x) < 3 else 0))
    outline_poly(cv, pts, ENAMEL)
    for (x, y) in ((x0 + 5, y0 + 4), (x1 - 5, y0 + 2)):
        cv.disc(x, y, 1.3, 1.3, STEELB, 4.0)
    ink = [(40, 6, 8), (90, 14, 16), (140, 24, 24), (180, 40, 34)]
    l1, l2 = 'AVUI NO ES FIA,', 'DEMÀ SÍ'
    text(cv, l1, (x0 + x1 - text_width(l1)) // 2, y0 + 5, ink, 2.6)
    l2x = (x0 + x1 - text_width(l2)) // 2 + 6                            # una mica desplaçat: pintat a corre-cuita
    text(cv, l2, l2x, y0 + 17, ink, 2.0)
    cv.line(l2x - 2, y0 + 23, l2x + text_width(l2) + 2, y0 + 23, ink, 2.4)  # subratllat amb ràbia
    # taques de rovell als cantons
    for (x, y) in ((x0 + 2, y1 - 2), (x1 - 3, y1 - 3), (x1 - 2, y0 + 1)):
        cv.disc(x, y, 2, 1.5, [(40, 20, 8), (90, 50, 20), (130, 80, 30)], 1.6)


def shelves(cv):
    """Lleixes amb ampolles darrere la barra, amb un mirall vell al darrere."""
    x0, x1 = 156, 318
    # el mirall
    for y in range(54, 96):
        for x in range(x0, x1 + 1):
            cv.put(x, y, GLASSD, 2.2 + (0.8 if (x - y) % 23 < 2 else 0) + (hr(x // 5, y // 5) - 0.5) * 0.3)
    outline(cv, x0 - 1, 53, x1 + 1, 96, WOOD)
    # dues lleixes
    for sy in (72, 94):
        obox(cv, x0 - 3, sy, x1 + 3, sy + 2, WOOD, 3.4, top=1.0)
    k = 0
    for sy in (72, 94):
        x = x0 + 2
        while x < x1 - 6:
            r = BOTTLES[int(hr(x, sy) * len(BOTTLES))]
            h = 11 + int(hr(x, sy, 2) * 6)
            w = 4 + (1 if hr(x, sy, 3) > 0.6 else 0)
            cv.rect(x, sy - h + 4, x + w, sy - 1, r, lambda xx, yy: 2.2 + (1.2 if xx == x + 1 else 0) - (0.8 if xx == x + w else 0))
            cv.rect(x + 1, sy - h, x + w - 1, sy - h + 3, r, 2.0)
            if hr(x, sy, 4) > 0.5:
                cv.rect(x, sy - h + 7, x + w, sy - h + 10, ENAMEL, 3.6)  # etiqueta
            cv.put(x + 1, sy - h + 5, r, 4.4)
            x += w + 2 + (3 if hr(x, sy, 5) > 0.8 else 0)
            k += 1


def tv(cv, frame=0):
    """La tele, en un suport a la paret: futbol (els jugadors es mouen)."""
    x0, y0, x1, y1 = 326, 40, 404, 86
    cv.rect(360, 32, 370, 40, STEELB, 2.4)                        # suport
    obox(cv, x0, y0, x1, y1, PLASTIC, 1.6)
    sx0, sy0, sx1, sy1 = x0 + 3, y0 + 3, x1 - 3, y1 - 6
    for y in range(sy0, sy1 + 1):
        for x in range(sx0, sx1 + 1):
            stripe = ((x + y // 2) // 8) % 2
            cv.put(x, y, PITCH, 2.4 + stripe * 0.5 + (0.2 if (y + frame) % 2 else 0), lit=0)
    cv.vline((sx0 + sx1) // 2, sy0, sy1, PITCH, 5.0, lit=0)       # la línia del mig
    cv.ring((sx0 + sx1) // 2, (sy0 + sy1) // 2, 7, PITCH, 5.0, lit=0, step=10)
    for i in range(8):                                              # jugadors
        px = sx0 + 4 + int((hr(i, 1) * (sx1 - sx0 - 8) + math.sin(frame * 0.8 + i) * 3)) % (sx1 - sx0 - 8)
        py = sy0 + 4 + int(hr(i, 2) * (sy1 - sy0 - 8))
        col = (230, 40, 40) if i % 2 else (240, 240, 250)
        cv.flat(px, py, col)
        cv.flat(px, py + 1, col)
    bx = sx0 + 10 + (frame * 5) % (sx1 - sx0 - 20)
    cv.flat(bx, sy0 + 12 + (frame % 3), (255, 255, 255))
    cv.rect(sx0 + 1, sy0 + 1, sx0 + 18, sy0 + 4, SLATE, 1.0, lit=0)    # el marcador
    text(cv, '0-0', sx0 + 3, sy0, PITCH, 0, lit=0, flat=(240, 240, 240))
    cv.rect(x1 - 8, y1 - 4, x1 - 6, y1 - 3, [(40, 200, 80)], 0, lit=0)
    cv.glow((x0 + x1) // 2, (y0 + y1) // 2, 50, (80, 140, 200), 0.12)


def phone(cv):
    """El telèfon de paret, beix, amb el fil arrissat."""
    x0, y0, x1, y1 = 432, 70, 450, 98
    obox(cv, x0, y0, x1, y1, ENAMEL, 3.0)
    obox(cv, x0 + 2, y0 + 2, x0 + 7, y1 - 2, ENAMEL, 3.6)          # l'auricular penjat
    cv.disc(x0 + 4, y0 + 4, 2, 2, ENAMEL, 4.2)
    cv.disc(x0 + 4, y1 - 4, 2, 2, ENAMEL, 4.2)
    for j in range(3):
        for i in range(3):
            cv.rect(x0 + 10 + i * 3, y0 + 6 + j * 4, x0 + 11 + i * 3, y0 + 7 + j * 4, SLATE, 2.0)
    for k in range(12):                                              # el fil arrissat
        y = y1 + k * 2
        cv.put(x0 + 3 + (1 if k % 2 else -1), y, SLATE, 2.0)
        cv.put(x0 + 3, y + 1, SLATE, 2.6)
    cv.line(x0 + 3, y1 + 24, x0 + 2, y1 + 30, SLATE, 2.0)
    # un paper amb números de telèfon clavat al costat
    obox(cv, 416, 76, 427, 92, SHEET, 4.2)
    for j in range(4):
        cv.hline(418, 424 - j % 2, 79 + j * 3, [(30, 30, 60), (60, 60, 120)], 1.4)


def ham(cv):
    """Un pernil penjat del sostre, amb el con de plàstic per a les gotes."""
    cv.vline(426, 0, 10, SLATE, 2.2)
    cv.poly([(422, 10), (430, 10), (436, 36), (430, 44), (420, 40), (418, 24)], HAM,
            lambda x, y: 3.2 + (1.0 if x < 423 else 0) - (1.0 if x > 431 else 0) + (hr(x // 2, y // 2) - 0.5) * 0.5)
    cv.rect(424, 6, 428, 11, SLATE, 1.4)                            # la pota negra
    cv.poly([(421, 44), (433, 44), (427, 52)], SHEET, 3.6)          # el con
    outline_poly(cv, [(422, 10), (430, 10), (436, 36), (430, 44), (420, 40), (418, 24)], HAM)


def wall_stuff(cv):
    """Una bufanda de futbol, un calendari de pneumàtics i una foto signada (d'algú que no coneix ningú)."""
    # bufanda d'un equip que no existeix (groc i verd), sota l'aparador
    for i in range(56):
        x = 81 + i
        y = 64 + int(3 * math.sin(i / 9))
        cv.rect(x, y, x, y + 4, [(40, 36, 6), (100, 86, 16), (170, 150, 40), (220, 200, 90)] if (i // 6) % 2 else
                [(6, 26, 10), (14, 60, 24), (30, 100, 44), (70, 150, 80)], 2.6)
    for fx in (81, 136):                                                # serrells
        for k in range(4):
            cv.vline(fx + k - (2 if fx > 100 else 0), 69, 73, [(40, 36, 6), (170, 150, 40)], 1.6)
    # foto signada al costat de la porta del rebost
    obox(cv, 68, 66, 86, 88, ENAMEL, 4.0)
    cv.rect(70, 68, 84, 82, [(30, 24, 30), (70, 56, 60), (120, 100, 100), (170, 150, 140)], 2.0)
    cv.disc(77, 74, 3, 3, [(60, 40, 30), (120, 90, 70), (180, 140, 110)], 2.4)
    cv.line(71, 84, 83, 85, [(10, 10, 60), (20, 20, 120)], 1.4)


def rebost_door(cv):
    """La porta del rebost (i despatx d'en Tomàs), amb el cartell «PRIVAT»."""
    x0, y0, x1, y1 = 18, 54, 64, FLOOR_Y
    obox(cv, x0 - 3, y0 - 3, x1 + 3, y1, WOOD, 3.6)
    obox(cv, x0, y0, x1, y1, WOOD, 2.6, top=0.4)
    for (a, b) in ((y0 + 6, 96), (102, y1 - 6)):
        cv.rect(x0 + 5, a, x1 - 5, b, WOOD, 2.2)
        cv.hline(x0 + 5, x1 - 5, a, WOOD, 1.0)
        cv.vline(x1 - 5, a, b, WOOD, 3.4)
    cv.disc(x1 - 6, 100, 2.2, 2.2, BRASS, lambda nx, ny: 3.6 - nx - ny)
    obox(cv, 28, 64, 54, 72, ENAMEL, 4.2)
    text(cv, 'PRIVAT', 30, 66, [(40, 6, 8), (120, 20, 20), (180, 40, 34)], 2.0)
    cv.darken(x1 + 4, y0, x1 + 7, y1, 0.4)


def exit_door(cv, frame=0):
    """La sortida: porta de vidre amb marc d'alumini, i fora, els llums dels camions."""
    x0, y0, x1, y1 = 456, 48, 479, FLOOR_Y
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, SKY, 0.6 + (y - y0) / 40, lit=0)
    for y in range(y0 + 50, y1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, CITY, 1.0, lit=0)
    # un camió que passa (els fars), segons el fotograma
    fx = x0 + 2 + (frame * 4) % 30
    if fx < x1 - 1:
        cv.hline(fx, min(x1, fx + 3), 92, [(250, 230, 180)], 0, lit=0)
        cv.glow(fx + 1, 92, 6, (250, 220, 160), 0.5)
    for (a, b, c, d) in ((x0, y0, x1, y0 + 2), (x0, y0, x0 + 2, y1), (x0, 108, x1, 111)):
        cv.rect(a, b, c, d, STEELB, 3.4)
    cv.rect(x0 + 6, 96, x0 + 16, 100, [(10, 30, 60), (30, 80, 150), (200, 220, 240)], 1.6, lit=0)   # adhesiu de VISA
    cv.vline(x0 + 4, 112, 128, STEELB, 5.0)                          # la nansa


def slot_machine(cv, frame=0):
    """L'escurabutxaques, al costat del rebost: llums que fan pampallugues."""
    x0, y0, x1, y1 = 68, 94, 98, FLOOR_Y + 2
    obox(cv, x0, y0, x1, y1, FORMICA, 2.4, top=0.8)
    cv.rect(x0 + 2, y0 + 2, x1 - 2, y0 + 10, [(30, 10, 40), (80, 20, 100), (160, 50, 180), (230, 120, 240)], 2.6, lit=0)
    for i in range(6):
        on = (i + frame) % 3 == 0
        cols = [(255, 220, 60), (255, 80, 80), (80, 220, 255)]
        cv.flat(x0 + 4 + i * 4, y0 + 13, cols[i % 3] if on else (60, 40, 30))
    cv.rect(x0 + 4, y0 + 16, x1 - 4, y0 + 26, SHEET, 4.4, lit=0)     # els rodets
    for i, sym in enumerate((frame % 4, (frame + 1) % 4, (frame + 3) % 4)):
        cx = x0 + 7 + i * 8
        col = [(220, 40, 40), (240, 200, 40), (40, 160, 60), (120, 60, 200)][sym]
        cv.disc(cx, y0 + 21, 2, 2.4, [col], 0, lit=0)
    cv.vline(x0 + 13, y0 + 16, y0 + 26, SHEET, 2.0, lit=0)
    cv.vline(x0 + 21, y0 + 16, y0 + 26, SHEET, 2.0, lit=0)
    obox(cv, x0 + 3, y0 + 30, x1 - 3, y0 + 36, STEELB, 3.0)          # botons
    for i in range(3):
        cv.flat(x0 + 7 + i * 8, y0 + 33, (255, 200, 60) if (frame + i) % 2 else (200, 60, 40))
    cv.rect(x0 + 8, y1 - 14, x1 - 8, y1 - 8, SLATE, 0.8)             # la safata
    cv.line(x1 + 1, y0 + 14, x1 + 4, y0 + 8, STEELB, 3.0)           # la palanca
    cv.disc(x1 + 4, y0 + 7, 1.6, 1.6, RED, 3.4)
    cv.glow((x0 + x1) // 2, y0 + 20, 26, (200, 120, 240), 0.14)


# ─── La barra ──────────────────────────────────────────────────────────────

def back_counter(cv):
    """El taulell del darrere: la cafetera exprés (vaporitzador!), la cervesera i la caixa."""
    # la cafetera exprés, a l'esquerra del tap
    x0, x1 = 196, 240
    obox(cv, x0, 86, x1, BAR_TOP, STEELB, 3.4, top=1.0)
    cv.rect(x0 + 2, 88, x1 - 2, 92, RED, 2.6)                          # la franja vermella
    for gx in (206, 226):                                              # els dos grups
        obox(cv, gx - 3, 96, gx + 3, 101, STEELB, 4.4)
        cv.rect(gx - 5, 101, gx + 5, 103, BRASS, 3.6)
        cv.rect(gx - 1, 103, gx, 106, SLATE, 1.6)
    cv.line(x1 - 2, 94, x1 + 4, 104, STEELB, 5.0)                     # el vaporitzador
    cv.rect(x1 + 3, 104, x1 + 5, 108, STEELB, 4.0)
    for tx in range(x0 + 4, x1 - 4, 6):                               # tasses al damunt
        obox(cv, tx, 80, tx + 4, 85, PORC, 4.4)
    # la cervesera (columna amb dos sortidors)
    obox(cv, 168, 94, 180, BAR_TOP, STEELB, 4.4)
    for tx in (170, 177):
        cv.rect(tx, 86, tx + 2, 94, [(10, 10, 10), (40, 30, 20), (180, 30, 30), (220, 200, 160)], 2.4)
    cv.disc(174, 99, 3, 3, [(80, 10, 10), (180, 40, 30), (240, 200, 120)], 2.4)   # el logo de la cervesa
    # la caixa registradora
    obox(cv, 352, 96, 392, BAR_TOP, PLASTIC, 2.2, top=0.8)
    cv.rect(360, 90, 384, 96, PLASTIC, 2.0)
    cv.rect(362, 91, 382, 95, [(10, 30, 10), (20, 80, 30), (60, 200, 90)], 1.6, lit=0)
    text(cv, '9,20', 364, 91, PITCH, 0, lit=0, flat=(80, 230, 110))
    for j in range(2):
        for i in range(6):
            cv.flat(356 + i * 5, 100 + j * 4, (140, 140, 150))


def bar(cv):
    """La barra: fòrmica granat amb el cantell d'alumini, la barana de llautó per als peus, i tamborets."""
    x0, x1 = 100, 420
    # el taulell, una mica des de dalt
    cv.poly([(x0, BAR_TOP), (x1, BAR_TOP), (x1 + 2, BAR_FRONT), (x0 - 2, BAR_FRONT)], FORMICA,
            lambda x, y: 3.6 + (y - BAR_TOP) * 0.1 + (0.6 if (x * 3 + y) % 17 == 0 else 0))
    cv.rect(x0 - 2, BAR_FRONT, x1 + 2, BAR_FRONT + 2, STEELB, 4.4)
    cv.hline(x0 - 2, x1 + 2, BAR_FRONT + 3, STEELB, 0)
    # el frontal: plafons de fusta
    for x in range(x0, x1 + 1):
        for y in range(BAR_FRONT + 4, 152):
            panel = (x - x0) % 40
            if panel < 2:
                cv.put(x, y, WOOD, 1.2)
            else:
                cv.put(x, y, WOOD, 2.6 + (0.8 if panel < 5 else 0) - (0.6 if panel > 36 else 0) + (hr(x // 2, y // 6) - 0.5) * 0.4)
    cv.vline(x0, BAR_FRONT, 152, WOOD, 0)
    cv.vline(x1, BAR_FRONT, 152, WOOD, 0)
    # barana de llautó
    cv.rect(x0 + 4, 144, x1 - 4, 145, BRASS, 3.6)
    for bx in range(x0 + 20, x1, 60):
        cv.rect(bx, 145, bx + 1, 150, BRASS, 2.6)
    cv.darken(x0 - 2, 152, x1 + 4, 157, lambda x, y: 0.75 - (y - 152) * 0.12)
    # coses damunt la barra: el pot de les propines, el tovalloner, la tassa d'en Marcel
    cv.rect(226, 101, 236, BAR_TOP + 2, SHEET, lambda x, y: 1.8 + (1.6 if x == 227 else 0), lit=1.0)   # pot de vidre
    cv.rect(227, 108, 235, BAR_TOP + 1, BRASS, 3.0)                    # monedes
    obox(cv, 226, 99, 236, 101, SHEET, 3.0)
    obox(cv, 224, 93, 238, 99, ENAMEL, 4.0)                             # cartellet «POT»
    text(cv, 'POT', 226, 94, [(40, 6, 8), (120, 20, 20)], 1.6)
    obox(cv, 306, 104, 318, BAR_TOP + 1, STEELB, 4.0)                  # tovalloner
    cv.rect(308, 100, 316, 104, SHEET, 4.6)
    obox(cv, 140, 108, 148, BAR_TOP + 2, PORC, 4.4)                    # el cafè amb llet d'en Marcel
    cv.line(149, 109, 150, 112, PORC, 3.6)
    cv.disc(144, BAR_TOP + 3, 7, 1.6, PORC, 3.4)
    obox(cv, 404, 104, 412, BAR_TOP + 1, BOTTLES[0], 2.4)              # una ampolla de cervesa buida
    cv.rect(406, 98, 410, 104, BOTTLES[0], 2.0)


def stools(cv):
    """Tamborets de skai vermell, davant la barra."""
    for x in (132, 192, 312, 372):
        cv.rect(x - 1, 140, x + 1, 172, STEELB, 3.2)
        cv.disc(x, 172, 8, 2, STEELB, 2.6)
        cv.disc(x, 160, 6, 1.5, STEELB, 1.6)                          # el reposapeus
        cv.disc(x, 138, 10, 3.4, RED, lambda nx, ny: 3.4 - ny * 1.4 - nx * 0.4)
        cv.rect(x - 10, 138, x + 10, 141, RED, 1.8)
        cv.disc(x, 138, 10, 2.4, RED, lambda nx, ny: 3.8 - ny * 1.2 - nx * 0.5)
        cv.darken(x - 9, 173, x + 9, 176, 0.6)


def bg(cv):
    wall(cv)
    floor(cv)
    window(cv)
    sign(cv)
    shelves(cv)
    tv(cv)
    phone(cv)
    ham(cv)
    wall_stuff(cv)
    rebost_door(cv)
    exit_door(cv)
    slot_machine(cv)
    back_counter(cv)
    bar(cv)
    stools(cv)


# ─── Props ──────────────────────────────────────────────────────────────────

def tap_barra(cv):
    """El clauer d'en Tomàs: un tap de la cervesera amb l'anella i dues claus, damunt la barra."""
    cv.disc(257, 115, 5, 2.4, [(20, 10, 6), (60, 20, 12), (140, 30, 20), (210, 60, 40), (240, 140, 110)], lambda nx, ny: 3.2 - ny - nx * 0.5)
    cv.disc(257, 113, 2.4, 2, BRASS, 4.0)
    cv.ring(263, 113, 2, STEELB, 5.0, step=30)
    cv.line(264, 112, 266, 109, BRASS, 4.4)
    cv.line(265, 114, 266, 117, STEELB, 5.0)


def comandament_barra(cv):
    """El comandament de la tele, damunt la barra."""
    cv.poly([(282, 114), (300, 112), (301, 116), (283, 118)], PLASTIC, lambda x, y: 2.4 + (0.8 if y < 114 else 0))
    outline_poly(cv, [(282, 114), (300, 112), (301, 116), (283, 118)], PLASTIC)
    cv.flat(286, 115, (230, 40, 40))
    for i in range(4):
        cv.flat(290 + i * 2, 114 + (1 if i % 2 else 0), (120, 120, 130))


def tele_bassols(cv):
    """A la tele, «La Comissària Bassols»: la comissària de perfil, amb gavardina, i el rètol."""
    sx0, sy0, sx1, sy1 = 329, 43, 401, 80
    for y in range(sy0, sy1 + 1):
        for x in range(sx0, sx1 + 1):
            cv.put(x, y, TVB, 1.8 + (y - sy0) / 30 + (0.2 if y % 2 else 0), lit=0)
    # una finestra amb persiana al fons
    for y in range(sy0 + 4, sy0 + 20, 3):
        cv.hline(sx0 + 40, sx0 + 64, y, TVB, 4.2, lit=0)
    # la comissària: gavardina, cabell curt gris, perfil
    cv.poly([(350, 80), (352, 62), (362, 58), (372, 62), (376, 80)], [(30, 24, 14), (70, 56, 30), (120, 100, 60), (170, 150, 100)], 2.4, lit=0)
    cv.disc(362, 52, 6, 7, [(60, 30, 20), (130, 80, 60), (200, 150, 120), (230, 190, 160)], lambda nx, ny: 2.6 + nx, lit=0)
    cv.disc(360, 47, 7, 4, [(60, 60, 70), (130, 130, 140), (190, 190, 200)], 1.6, lit=0)
    cv.flat(367, 51, (20, 20, 20))
    cv.rect(366, 56, 372, 56, [(250, 250, 250)], 0, lit=0)             # una cigarreta (és de 1987)
    # el rètol del capítol
    cv.rect(sx0, sy1 - 10, sx1, sy1, SLATE, 1.2, lit=0)
    text(cv, 'EL VIOLÍ MUT', sx0 + 4, sy1 - 6, TVB, 0, lit=0, flat=(240, 220, 120))


def rebost_tancat(cv):
    """En Tomàs és al rebost discutint amb la seva dona inexistent: «NO MOLESTAR» i llum per sota la porta."""
    cv.line(34, 84, 41, 76, STEELB, 3.0)                                # penjat del pom? no: d'un clau
    cv.line(48, 84, 41, 76, STEELB, 3.0)
    cv.disc(41, 76, 1, 1, STEELB, 4.0)
    w = text_width('NO MOLESTAR')
    obox(cv, 41 - w // 2 - 2, 84, 41 + w // 2 + 2, 92, ENAMEL, 4.6)
    text(cv, 'NO MOLESTAR', 41 - w // 2, 86, [(40, 6, 8), (120, 20, 20), (200, 40, 34)], 2.4)
    cv.hline(19, 63, FLOOR_Y + 1, [(255, 220, 140)], 0, lit=0)
    cv.glow(41, FLOOR_Y + 2, 16, (255, 200, 120), 0.4)


PROPS = {'tap_barra': tap_barra, 'comandament_barra': comandament_barra, 'tele_bassols': tele_bassols,
         'rebost_tancat': rebost_tancat}


def _frames():
    base = Canvas(light=LIGHT)
    bg(base)
    frames = []
    for i in range(8):
        cv = Canvas(light=LIGHT, img=base.img.copy())
        window(cv, flick=1 if i == 5 else 0)
        tv(cv, i)
        slot_machine(cv, i)
        exit_door(cv, i)
        frames.append(_diff(cv.img, base.img))
    return frames


ANIMS = {'bar': {'frames': _frames, 'frameDuration': 220}}


# ─── La barra, per davant del cambrer ──────────────────────────────────────
# Qui és darrere la barra (peus per sobre de y 160) queda tapat de cintura en avall; qui és a la sala, no.
_DAVANT = [(98, 111, 424, 157),       # el taulell, el frontal i els tamborets
           (224, 93, 238, 113),       # el pot de les propines
           (306, 100, 318, 113),      # el tovalloner
           (140, 106, 151, 116),      # el cafè d'en Marcel
           (404, 97, 412, 113)]       # l'ampolla buida

FRONT = {'mask': lambda x, y: any(x0 <= x <= x1 and y0 <= y <= y1 for x0, y0, x1, y1 in _DAVANT),
         'baseline': 160, 'zIndex': 20, 'props': ('tap_barra', 'comandament_barra')}
