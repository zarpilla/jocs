"""
**El dibuix pla de sempre** (font de les textures de aeroport_personal.py, que és en 3D), a 1×.

El racó de servei de l'aeroport (hd/rooms/aeroport_personal.py) a 640×360, la composició ×4/3 dibuixada de nou.
Escena 3, l'Iri, davant la porta de personal:
  - un passadís de servei: bloc de formigó pintat de verd hospital, linòleum gastat, un fluorescent que
    parpelleja;
  - el vidre cap a la terminal: es veuen els seients blaus i el rètol d'objectes perduts i, mentre vigila, l'agent
    Soler (decorat `soler_vidre`, fins que la Vet el distreu);
  - la porta de personal, metàl·lica, amb la franja vermella «NOMÉS PERSONAL», i el teclat de quatre xifres amb
    les tecles 2, 4, 6 i 8 gastades; el llum: vermell (tancada), parpelleig (`alarma`) o verd (`porta_oberta`);
  - un carro de la neteja, un extintor, el senyal de terra mullat, un radiador, taquilles i un tauler de torns.
Animacions: `fluorescent` (el tub parpelleja) i `avio` (per la vidriera del fons, un avió que s'acosta).
"""
import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)

from PIL import Image
from pixels import nearest

from hd.pix import Light, Canvas, W, H, hr
from hd.rooms.comu import obox, outline, text, text_width, _diff, SHEET, CARD, RED
from hd.rooms.bar_sala import STEELB, SLATE
from hd.rooms.pis_cuina import outline_poly
from hd.rooms.aeroport_terminal import CONC, TILE, CHROME, DESK, BLUE, YELS, DAWN
from hd.rooms.aeroport_personal import BLOCK, LINO, DOOR, REDB, GREENS, TROLLEY  # noqa: F401
from hd.personatges import NPCS
from hd640.draw_characters import person

Canvas1x = Canvas                                   # (a 1×, com la sala en 3D)

FLOOR_Y = 200

LIGHT = Light(ambient=-0.3, vignette=(80, 40), floor_fade=(253, 37))
LIGHT.point(267, 8, r=347, k=2.6, squash=0.8, power=1.3)             # el fluorescent del passadís
LIGHT.point(133, 100, r=133, k=0.5, squash=1.2, power=2.0)           # la claror de la terminal pel vidre
LIGHT.point(315, 148, r=35, k=0.4, squash=1.0, power=2.0)            # el llum del teclat

GLASS = (27, 40, 240, 160)
LED = (315, 148)
DOOR_BOX = (333, 59, 416, FLOOR_Y)
KEYPAD = (299, 112, 331, 152)
LOCKER = [(20, 30, 40), (34, 50, 64), (52, 74, 92), (74, 100, 120), (100, 128, 150), (140, 166, 184)]
WHITE = [(250, 244, 236)]


# ─── Paret, sostre, terra ──────────────────────────────────────────────────

def wall(cv):
    """Bloc de formigó pintat de verd pàl·lid; a baix, una franja més fosca de cops de carro."""
    for y in range(0, FLOOR_Y):
        row = y * 3 // 40
        ry = y - (row * 40 + 2) // 3                                    # la fila del bloc (13 o 14 px)
        for x in range(W):
            off = 20 if row % 2 else 0
            joint = ((y + 1) * 3 // 40 != row) or ((x + off) % 40 == 39)
            n = (hr(x // 2, y // 2, 5) - 0.5) * 0.3 + (hr(x, y, 8) - 0.5) * 0.12 + (hr((x + off) // 40, row, 2) - 0.5) * 0.3
            lvl = 2.8 if joint else 4.2 + n + (0.4 if ry == 0 else 0)
            if y > 157:
                lvl -= 0.9
            cv.put(x, y, BLOCK, lvl)
    cv.rect(0, 156, W - 1, 157, BLOCK, 2.4)
    for i in range(14):                                                 # els cops dels carros
        x = 20 + int(hr(i, 21) * 600)
        cv.hline(x, x + 3 + int(hr(i, 22) * 8), 170 + int(hr(i, 23) * 20), BLOCK, 2.0)
    cv.rect(0, FLOOR_Y - 5, W - 1, FLOOR_Y - 1, LINO, 2.0)
    cv.hline(0, W - 1, FLOOR_Y - 5, LINO, 3.0)
    cv.hline(0, W - 1, FLOOR_Y, LINO, 0)
    # el sostre baix, amb canonades i la safata de cables
    cv.rect(0, 0, W - 1, 8, CONC, 3.0)
    cv.rect(0, 12, W - 1, 16, CHROME, lambda x, y: 2.4 + (1.4 if y == 13 else 0) - (0.6 if y == 16 else 0))
    for x in range(0, W, 8):                                            # la reixeta de la safata
        cv.vline(x, 13, 15, CHROME, 1.6)
    cv.rect(0, 18, W - 1, 21, REDB, lambda x, y: 2.4 + (1.0 if y == 19 else 0) - (0.8 if y == 21 else 0))   # la canonada dels bombers
    for x in range(40, W, 107):                                         # les abraçadores
        cv.rect(x, 17, x + 2, 22, CHROME, 3.4)
        cv.vline(x + 1, 9, 17, CHROME, 2.4)
    tube(cv, on=True)


def tube(cv, on=True):
    """El fluorescent del passadís."""
    x0, x1, y = 213, 320, 4
    obox(cv, x0 - 5, y - 3, x1 + 5, y + 4, CHROME, 3.0)
    col = (230, 244, 255) if on else (120, 130, 140)
    cv.hline(x0, x1, y + 1, [col], 0, lit=0)
    cv.hline(x0, x1, y + 2, [col if on else (100, 108, 118)], 0, lit=0)
    cv.rect(x0 - 2, y + 1, x0 - 1, y + 2, CHROME, 4.0)                 # els capçals
    cv.rect(x1 + 1, y + 1, x1 + 2, y + 2, CHROME, 4.0)
    if on:
        cv.glow((x0 + x1) // 2, y + 3, 45, (220, 236, 255), 0.25)


def floor(cv):
    """Linòleum gris, gastat al camí de la porta, amb rascades de rodes."""
    for y in range(FLOOR_Y + 1, H):
        for x in range(W):
            n = (hr(x // 2, y, 4) - 0.5) * 0.4 + (hr(x // 6, y // 3, 6) - 0.5) * 0.15
            worn = max(0, 1 - abs(x - 373) / 93) * max(0, 1 - (y - FLOOR_Y) / 53) * 0.8
            cv.put(x, y, LINO, 3.4 + n + worn)
    for i in range(13):                                                  # rascades
        x = 53 + int(hr(i, 7) * 533)
        y = 211 + int(hr(i, 8) * 53)
        cv.line(x, y, x + 13 + int(hr(i, 9) * 19), y + (1 if i % 2 else 0), LINO, 1.8)
    for k in range(2):                                                   # el camí de les rodes del carro
        cv.hline(452 + k * 70, 470 + k * 70, 224 + k, LINO, 2.0)
    cv.tint(187, 203, 400, 253, (220, 236, 255), lambda x, y: 0.08 * max(0, 1 - abs(x - 267) / 107) * max(0, 1 - (y - 203) / 51))


# ─── El vidre cap a la terminal ────────────────────────────────────────────

def terminal_view(cv):
    """Pel vidre: la terminal, una mica més avall i més lluny (seients blaus, el rètol groc, la vidriera de l'alba)."""
    x0, y0, x1, y1 = GLASS
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, CONC, 3.6 + (hr(x // 40, 1) - 0.5) * 0.3 - (0.6 if (x % 40) == 0 else 0), lit=0)
    cv.hline(x0, x1, 85, BLUE, 2.6, lit=0)                               # la franja blava de la terminal
    # la vidriera gran de la terminal, al fons a l'esquerra, amb l'alba
    for y in range(48, 94):
        for x in range(35, 120):
            cv.put(x, y, DAWN, 1.0 + (y - 48) / 8.0, lit=0)
    for x in range(35, 120):                                             # l'horitzó
        top = 86 - int(2 * hr(x // 4, 3))
        for y in range(top, 94):
            cv.put(x, y, [(8, 10, 16), (16, 18, 26)], 0.6, lit=0)
    for lx in range(38, 120, 9):
        cv.flat(lx, 88, (120, 200, 255) if lx % 2 else (250, 200, 90))
    cv.rect(76, 48, 77, 93, CHROME, 3.0, lit=0)
    outline(cv, 33, 47, 120, 94, CONC)
    # el panell de sortides, penjat
    obox(cv, 138, 49, 157, 57, [(4, 4, 6), (14, 14, 20)], 0.8, lit=0)
    for k in range(3):
        cv.hline(141, 148 + (k % 2) * 5, 51 + k * 2, [(250, 190, 50)], 0, lit=0)
    # el rètol d'objectes perduts, a la dreta
    obox(cv, 160, 59, 229, 69, YELS, 3.2, lit=0)
    w = text_width('PERDUTS')
    text(cv, 'PERDUTS', 195 - w // 2, 62, [(30, 22, 6)], 0, lit=0, flat=(30, 22, 6))
    cv.rect(163, 70, 227, 101, CONC, 2.6, lit=0)
    for yy in (82, 96):                                                  # els prestatges, endevinats
        cv.hline(164, 226, yy, [(60, 34, 16), (96, 58, 28)], 1.0, lit=0)
    for k in range(5):
        bx = 168 + k * 12
        cv.rect(bx, 89 - (k % 3) * 2, bx + 7, 95, [[(30, 50, 100)], [(120, 30, 30)], [(90, 60, 30)]][k % 3], 0, lit=0)
    # el terra de la terminal i els seients
    for y in range(107, y1 + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, TILE, 4.2 + ((y - 107) / 27) - (0.8 if (x + (y - 107) // 2) % 36 == 0 else 0), lit=0)
    for i in range(4):
        sx = 45 + i * 21
        obox(cv, sx, 99, sx + 17, 112, BLUE, 2.6, lit=0)
        cv.rect(sx - 1, 112, sx + 19, 116, BLUE, lambda x, y: 3.4 - (y - 112) * 0.2, lit=0)
    cv.rect(40, 117, 133, 118, CHROME, 3.0, lit=0)
    for lx in (46, 126):
        cv.vline(lx, 119, 124, CHROME, 2.4, lit=0)


SOLER_AT = (157, 160)   # on té els peus en Soler, vist pel vidre (amagats pel marc de baix)


def soler(cv):
    """L'agent Soler, de cara a la porta de personal (és a dir, mirant cap aquí)."""
    fig = person(NPCS['soler'], 'D')
    k = 0.82
    fig = nearest(fig, (round(fig.width * k), round(fig.height * k)))
    fx, fy = SOLER_AT
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    layer.alpha_composite(fig, (fx - round(34 * k), fy - round(111 * k)))
    x0, y0, x1, y1 = GLASS
    layer = layer.crop((x0 + 3, y0 + 3, x1 - 2, y1 - 2))
    cv.blit(layer, (x0 + 3, y0 + 3))


def glass_frame(cv):
    """El marc d'alumini i els reflexos del passadís al vidre."""
    x0, y0, x1, y1 = GLASS
    cv.tint(x0, y0, x1, y1, (200, 230, 220), lambda x, y: 0.14 if (x + y) % 61 < 7 else (0.09 if (x + y) % 61 < 10 else 0.06))
    for (a, b, c, d) in ((x0, y0, x1, y0 + 3), (x0, y1 - 3, x1, y1), (x0, y0, x0 + 3, y1), (x1 - 3, y0, x1, y1), (132, y0, 135, y1)):
        cv.rect(a, b, c, d, CHROME, lambda x, y, a=a, b=b: 3.2 + (0.8 if x == a or y == b else 0))
    outline(cv, x0 - 1, y0 - 1, x1 + 1, y1 + 1, BLOCK)
    cv.rect(x0 - 4, y1 + 1, x1 + 4, y1 + 4, CHROME, lambda x, y: 4.0 + (0.8 if y == y1 + 1 else 0))   # l'ampit
    cv.darken(x0 - 4, y1 + 5, x1 + 4, y1 + 6, 0.5)


# ─── La porta i el teclat ──────────────────────────────────────────────────

def door(cv):
    """La porta de personal: xapa grisa, la franja vermella, la barra i les frontisses."""
    x0, y0, x1, y1 = DOOR_BOX
    obox(cv, x0 - 5, y0 - 5, x1 + 5, y1, CHROME, 2.6)
    door_leaf(cv)
    cv.darken(x1 + 7, y0, x1 + 12, y1, 0.4)


def door_leaf(cv):
    x0, y0, x1, y1 = DOOR_BOX
    obox(cv, x0, y0, x1, y1, DOOR, 3.6, top=0.6)
    for yy in (y0 + 8, y1 - 40):
        cv.rect(x0 + 5, yy, x1 - 5, yy + 29, DOOR, 3.2)
        cv.hline(x0 + 5, x1 - 5, yy, DOOR, 2.0)
        cv.vline(x0 + 5, yy, yy + 29, DOOR, 2.4)
        cv.hline(x0 + 5, x1 - 5, yy + 29, DOOR, 4.6)
        cv.vline(x1 - 5, yy, yy + 29, DOOR, 4.2)
    cv.rect(x0 + 1, y1 - 8, x1 - 1, y1 - 1, DOOR, lambda x, y: 4.4 + (0.6 if y == y1 - 8 else 0) - (0.4 if (x + y) % 7 == 0 else 0))   # la xapa de cops
    # la franja vermella amb el text
    obox(cv, 344, 71, 405, 93, REDB, 3.0)
    cv.hline(346, 403, 73, REDB, 3.8)
    for k, word in enumerate(('NOMÉS', 'PERSONAL')):
        text(cv, word, 375 - text_width(word) // 2, 76 + k * 8, WHITE, 0, flat=WHITE[0])
    # la maneta i la placa
    obox(cv, 339, 133, 344, 149, CHROME, 3.6)
    cv.rect(339, 139, 355, 141, CHROME, lambda x, y: 4.6 + (0.6 if y == 139 else 0))
    cv.disc(341, 145, 1.2, 1.4, SLATE, 0.6)                              # el pany
    for hy in (72, 181):                                                 # frontisses, a la dreta
        cv.rect(x1 - 1, hy, x1 + 1, hy + 8, CHROME, 3.2)
        cv.flat(x1, hy + 1, CHROME[4])
    # el braç tancaportes, dalt
    obox(cv, x0 + 8, y0 + 2, x0 + 30, y0 + 6, CHROME, 3.0)
    cv.line(x0 + 30, y0 + 4, x0 + 48, y0 + 2, CHROME, 3.6)


def keypad(cv, led='vermell'):
    """El teclat: caixa d'alumini, dotze tecles (2, 4, 6 i 8 gastades), una pantalleta i el llum."""
    x0, y0, x1, y1 = KEYPAD
    obox(cv, x0, y0, x1, y1, CHROME, 2.8, top=1.0)
    cv.rect(x0 + 4, y0 + 3, x1 - 4, y0 + 7, [(10, 20, 14), (30, 60, 40)], 1.0, lit=0)
    cv.hline(x0 + 6, x0 + 9, y0 + 5, [(60, 120, 80)], 0, lit=0)
    keys = '123456789*0#'
    for i, kch in enumerate(keys):
        kx = x0 + 5 + (i % 3) * 8
        ky = y0 + 10 + (i // 3) * 6
        worn = kch in '2468'
        cv.rect(kx, ky, kx + 4, ky + 4, CHROME, 4.6 if worn else 3.4)
        cv.hline(kx + 1, kx + 4, ky + 4, CHROME, 1.6)
        cv.vline(kx + 4, ky + 1, ky + 4, CHROME, 1.6)
        if worn:
            cv.rect(kx + 1, ky + 1, kx + 2, ky + 2, [(232, 230, 220)], 0)
        else:
            cv.flat(kx + 2, ky + 2, CHROME[1])                           # el número, encara llegible
    for sx, sy in ((x0 + 2, y0 + 2), (x1 - 2, y0 + 2), (x0 + 2, y1 - 2), (x1 - 2, y1 - 2)):
        cv.flat(sx, sy, CHROME[1])                                       # els cargols
    led_at(cv, led)


def led_at(cv, led):
    lx, ly = LED
    col = {'vermell': (230, 40, 36), 'verd': (60, 230, 100), 'alarma': (255, 70, 40)}[led]
    cv.disc(lx, ly, 3, 2.2, [col], 0, lit=0)
    cv.flat(lx - 1, ly - 1, tuple(min(255, c + 60) for c in col))
    cv.glow(lx, ly, 8 if led != 'alarma' else 27, col, 0.45 if led != 'alarma' else 0.7)


# ─── El passadís ───────────────────────────────────────────────────────────

def extinguisher(cv):
    """Un extintor penjat i el seu cartell."""
    obox(cv, 261, 85, 277, 96, REDB, 3.4)
    cv.rect(265, 88, 273, 93, WHITE, 0)
    cv.rect(268, 89, 270, 92, [(200, 40, 40)], 0)
    cv.rect(263, 143, 275, 145, SLATE, 1.6)                              # el suport
    cv.disc(269, 131, 6, 4, REDB, lambda nx, ny: 3.4 - ny)
    cv.rect(264, 131, 275, 160, REDB, lambda x, y: 3.0 + (1.6 if x == 267 else 0) - (0.8 if x >= 274 else 0))
    cv.hline(264, 275, 160, REDB, 1.6)
    obox(cv, 267, 123, 272, 127, SLATE, 2.6)
    cv.disc(272, 121, 1.6, 1.6, [(30, 30, 30), (200, 200, 190)], 1.0)    # el manòmetre
    cv.flat(272, 121, (60, 200, 90))
    cv.line(272, 125, 280, 139, SLATE, 1.6)
    cv.line(280, 139, 278, 146, SLATE, 1.6)
    cv.disc(269, 149, 4, 2.4, WHITE, 0)
    cv.hline(267, 271, 149, [(200, 40, 40)], 0)


def running_man(cv, x, y, col):
    """L'home que corre del senyal de sortida (6×9)."""
    rows = ['...x..',
            '..xx..',
            '.xxxx.',
            'x.xx.x',
            '..xx..',
            '..x.x.',
            '.x...x',
            'x.....',
            '......']
    cv.sprite(rows, x, y, {'x': col}, lit=0)


def emergency_sign(cv):
    """El senyal verd de sortida, damunt la porta."""
    obox(cv, 355, 35, 395, 48, GREENS, 2.6, lit=0)
    cv.rect(358, 37, 367, 46, [(240, 255, 240)], 0, lit=0)              # la porta blanca
    running_man(cv, 360, 38, GREENS[1])
    wt = (240, 255, 240)
    cv.line(371, 41, 390, 41, [wt], 0, lit=0)
    cv.line(386, 38, 390, 41, [wt], 0, lit=0)
    cv.line(386, 44, 390, 41, [wt], 0, lit=0)
    cv.glow(375, 41, 24, (120, 255, 150), 0.18)


def notice_board(cv):
    """El tauler de torns, amb fulls de colors i una nota amb caràcter."""
    x0, y0, x1, y1 = 448, 69, 531, 133
    obox(cv, x0, y0, x1, y1, CARD, 2.6)
    for k in range(40):                                                  # el suro
        cv.flat(x0 + 2 + int(hr(k, 31) * (x1 - x0 - 4)), y0 + 2 + int(hr(k, 32) * (y1 - y0 - 4)), CARD[1])
    obox(cv, x0 + 4, y0 + 4, x1 - 4, y0 + 12, SHEET, 4.6)
    text(cv, 'TORNS', x0 + (x1 - x0 - text_width('TORNS')) // 2, y0 + 6, [(20, 20, 30)], 0, flat=(30, 30, 40))
    obox(cv, x0 + 4, y0 + 14, x1 - 27, y0 + 44, SHEET, 4.4)
    for j in range(6):                                                   # la graella
        yy = y0 + 16 + j * 5
        cv.hline(x0 + 5, x1 - 28, yy, SHEET, 3.4)
        for i in range(6):
            if hr(i, j, 3) > 0.5:
                cv.rect(x0 + 7 + i * 8, yy + 1, x0 + 11 + i * 8, yy + 3, [[(60, 100, 200)], [(220, 70, 60)]][(i + j) % 2], 0)
    obox(cv, x1 - 24, y0 + 17, x1 - 5, y0 + 35, YELS, 4.2)               # un pòsit
    for k in range(3):
        cv.line(x1 - 21, y0 + 22 + k * 4, x1 - 9 - (k % 2) * 3, y0 + 21 + k * 4, [(40, 40, 120)], 0)
    obox(cv, x0 + 8, y0 + 46, x0 + 40, y1 - 5, [(40, 60, 90), (90, 130, 170), (170, 200, 230), (220, 236, 248)], 3.0)
    for k in range(3):
        cv.hline(x0 + 12, x0 + 35 - k * 5, y0 + 51 + k * 4, SLATE, 1.6)
    obox(cv, x0 + 46, y0 + 48, x1 - 6, y1 - 7, [(80, 30, 50), (200, 120, 150), (240, 200, 210)], 2.0)   # un full rosa de vacances
    for k in range(2):
        cv.hline(x0 + 49, x1 - 10 - k * 6, y0 + 52 + k * 3, SLATE, 1.6)
    for (px, py) in ((x0 + 7, y0 + 3), (x1 - 7, y0 + 3), (x1 - 15, y0 + 16), (x0 + 24, y0 + 45), (x0 + 60, y0 + 47)):
        cv.disc(px, py, 1.4, 1.4, RED, 3.4)


def lockers(cv):
    """Tres taquilles del personal, una amb la porta mal tancada."""
    for i in range(3):
        x0 = 547 + i * 29
        obox(cv, x0, 67, x0 + 27, FLOOR_Y, LOCKER, 2.8, top=0.6)
        for k in range(5):
            cv.hline(x0 + 7, x0 + 20, 75 + k * 3, SLATE, 1.0)
            cv.hline(x0 + 7, x0 + 20, 76 + k * 3, LOCKER, 4.0)
        cv.rect(x0 + 20, 128, x0 + 21, 139, CHROME, lambda x, y, x0=x0: 4.0 + (0.8 if x == x0 + 20 else 0))
        obox(cv, x0 + 8, 92, x0 + 19, 100, SHEET, 4.6)                   # la plaqueta del número
        text(cv, str(i + 7), x0 + 14 - text_width(str(i + 7)) // 2, 94, [(20, 20, 30)], 0, flat=(30, 30, 40))
        cv.rect(x0 + 4, 186, x0 + 23, 188, LOCKER, 1.8)                  # la reixeta de baix
    cv.darken(603, 68, 605, FLOOR_Y - 1, 0.6)                            # l'escletxa de la mal tancada
    cv.line(608, 93, 607, 99, [(220, 70, 60)], 0)                        # una màniga que en surt
    cv.flat(609, 93, (220, 70, 60))


def trolley(cv):
    """El carro de la neteja amb la galleda, el pal de la fregona i les bosses."""
    x0, x1 = 448, 528
    cv.rect(x0, 171, x1, 176, TROLLEY, lambda x, y: 3.0 + (0.8 if y == 171 else 0))
    cv.rect(x0 + 3, 176, x0 + 4, 213, CHROME, 3.0)
    cv.rect(x1 - 4, 176, x1 - 3, 213, CHROME, 3.0)
    cv.rect(x0, 200, x1, 203, TROLLEY, 2.6)
    for wx in (x0 + 4, x1 - 4):
        cv.disc(wx, 216, 3, 3, SLATE, lambda nx, ny: 1.8 - ny * 0.6)
        cv.flat(wx, 216, CHROME[3])
    # la bossa groga d'escombraries penjada
    bag = [(x0 + 3, 139), (x0 + 29, 139), (x0 + 32, 171), (x0, 171)]
    cv.poly(bag, YELS, lambda x, y: 2.6 + (0.6 if x < x0 + 8 else 0) + (0.5 if (x - x0 - 14) % 9 == 0 and y > 145 else 0))
    outline_poly(cv, bag, YELS)
    cv.rect(x0 + 10, 136, x0 + 22, 139, YELS, 3.6)                       # el nus
    # els esprais i la galleda blava
    for i, c in enumerate(([(10, 60, 30), (30, 140, 70), (100, 220, 140)], [(80, 10, 60), (170, 40, 140), (240, 120, 220)])):
        sx = x0 + 40 + i * 11
        obox(cv, sx, 155, sx + 7, 171, c, 1.6)
        cv.rect(sx + 2, 150, sx + 5, 154, SLATE, 2.0)                    # el gallet
        cv.rect(sx + 2, 160, sx + 5, 165, WHITE, 0)
    cv.poly([(x0 + 61, 181), (x1 - 3, 181), (x1 - 5, 200), (x0 + 64, 200)], TROLLEY, 2.4)
    cv.hline(x0 + 61, x1 - 3, 181, TROLLEY, 3.8)
    cv.hline(x0 + 63, x1 - 5, 183, [(60, 70, 90), (110, 120, 140)], 1.0)  # l'aigua grisa
    cv.line(x0 + 69, 181, x0 + 77, 139, CARD, 3.0)
    cv.line(x0 + 70, 181, x0 + 78, 139, CARD, 2.0)
    cv.darken(x0 - 3, 219, x1 + 3, 223, 0.55)


def wet_floor(cv):
    """El senyal groc de terra mullat (en tres idiomes, en teoria; aquí només el ninot que cau)."""
    cx = 139
    cone = [(cx - 11, 248), (cx - 4, 208), (cx + 4, 208), (cx + 11, 248)]
    cv.poly(cone, YELS, lambda x, y: 3.4 - (x - cx) * 0.06)
    outline_poly(cv, cone, YELS)
    ink = [(20, 16, 6)]
    cv.disc(cx, 221, 1.6, 1.6, ink, 0)
    cv.line(cx, 223, cx - 3, 230, ink, 0)
    cv.line(cx - 1, 225, cx + 3, 223, ink, 0)
    cv.line(cx - 3, 230, cx + 3, 234, ink, 0)
    cv.line(cx - 3, 230, cx - 6, 233, ink, 0)
    cv.line(cx - 6, 236, cx + 5, 236, ink, 0)
    cv.hline(cx - 7, cx + 7, 242, ink, 0)                                # el text, il·legible
    cv.darken(cx - 12, 249, cx + 12, 252, 0.5)
    # el bassal, amb el reflex del fluorescent
    cv.tint(cx - 40, 238, cx + 30, 256, (150, 170, 190),
            lambda x, y: 0.10 if ((x - cx + 5) / 35) ** 2 + ((y - 247) / 8) ** 2 < 1 else 0)
    cv.hline(cx - 20, cx - 8, 244, LINO, 5.4)


def radiator(cv):
    """Un radiador sota el vidre."""
    for i in range(14):
        x = 53 + i * 8
        cv.rect(x, 168, x + 5, 192, SHEET, lambda xx, yy, x=x: 3.6 + (0.8 if xx == x else 0) - (0.8 if xx == x + 5 else 0))
        cv.disc(x + 2.5, 168, 2.5, 1, SHEET, 4.2)
    cv.rect(51, 192, 165, 193, SHEET, 2.4)
    cv.rect(165, 186, 171, 188, CHROME, 3.0)                             # la clau
    cv.disc(172, 187, 2, 2, CHROME, 3.6)
    cv.vline(168, 189, 199, CHROME, 2.4)


def bg(cv, soler_hi=False):
    wall(cv)
    floor(cv)
    terminal_view(cv)
    if soler_hi:
        soler(cv)
    glass_frame(cv)
    radiator(cv)
    extinguisher(cv)
    emergency_sign(cv)
    door(cv)
    keypad(cv)
    notice_board(cv)
    lockers(cv)
    trolley(cv)
    wet_floor(cv)


_BASE = {}


def _base():
    if 'img' not in _BASE:
        cv = Canvas(light=LIGHT)
        bg(cv)
        _BASE['img'] = cv.img
    return _BASE['img']


# ─── Props ──────────────────────────────────────────────────────────────────

def soler_vidre(cv):
    """En Soler, vigilant, vist pel vidre (fins que la Vet el distreu)."""
    var = Canvas(light=LIGHT)
    bg(var, soler_hi=True)
    cv.img.alpha_composite(_diff(var.img, _base()))


def porta_oberta(cv):
    """La porta oberta cap endins: es veu l'oficina (llum fluorescent, un arxivador) i el llum verd."""
    x0, y0, x1, y1 = DOOR_BOX
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, CONC if y < 160 else TILE, (3.2 if y < 160 else 3.6) - (x1 - x) * 0.015 + (hr(x, y, 17) - 0.5) * 0.2)
    cv.rect(x0, 159, x1, 160, CONC, 1.6)
    obox(cv, 381, 93, 408, 187, DESK, 3.0)                               # un arxivador
    for k in range(3):
        obox(cv, 384, 97 + k * 30, 405, 123 + k * 30, DESK, 3.4, top=0.6)
        cv.rect(389, 104 + k * 30, 400, 105 + k * 30, CHROME, 4.0)
    cv.darken(381, 188, 410, 190, 0.5)
    obox(cv, 352, 100, 370, 124, [(40, 36, 30), (110, 104, 90), (190, 184, 166)], 1.8)   # un racó del pòster de la companyia
    cv.rect(354, 102, 368, 116, BLUE, 2.8)
    cv.rect(347, 64, 400, 65, [(230, 244, 255)], 0, lit=0)               # el fluorescent de l'oficina
    cv.glow(373, 67, 27, (220, 236, 255), 0.3)
    # el cantell de la porta, oberta cap endins (a l'esquerra)
    leaf = [(x0, y0), (x0 + 11, y0 + 5), (x0 + 11, y1 - 3), (x0, y1)]
    cv.poly(leaf, DOOR, lambda x, y: 4.0 - (x - x0) * 0.15)
    outline_poly(cv, leaf, DOOR)
    cv.rect(x0 + 6, 139, x0 + 8, 147, CHROME, 3.6)                       # la maneta, de cantell
    led_at(cv, 'verd')


def alarma(cv):
    """La porta xiula: el llum vermell encès de debò, que tenyeix el teclat i la porta."""
    base = _base()
    var = Canvas(light=LIGHT, img=base.copy())
    led_at(var, 'alarma')
    var.glow(LED[0], LED[1], 61, (255, 40, 30), 0.55)
    var.disc(LED[0], LED[1], 4, 3.2, [(255, 120, 90)], 0, lit=0)
    var.flat(LED[0] - 1, LED[1] - 1, (255, 220, 200))
    cv.img.alpha_composite(_diff(var.img, base))


PROPS = {'soler_vidre': soler_vidre, 'porta_oberta': porta_oberta, 'alarma': alarma}


# ─── El fluorescent que parpelleja ─────────────────────────────────────────

def _frames():
    base = _base()
    frames = []
    for i in range(16):
        cv = Canvas(light=LIGHT, img=base.copy())
        if i in (5, 7, 12):
            tube(cv, on=False)
            cv.darken(200, 0, 333, 19, 0.25)
        elif i in (6, 13):                                               # mig encès: només brillen els extrems
            tube(cv, on=False)
            for ex in (213, 316):
                cv.hline(ex, ex + 4, 5, [(200, 220, 240)], 0, lit=0)
        frames.append(_diff(cv.img, base))
    return frames


def _frames_avio():
    """Per la vidriera del fons de la terminal, un avió que s'acosta de cara: el far fix i el llum vermell que parpelleja."""
    base = _base()
    frames = []
    for i in range(10):
        cv = Canvas(light=LIGHT, img=base.copy())
        cv.flat(55, 63, (250, 240, 220))                                 # el far d'aterratge
        cv.glow(55, 63, 3, (255, 236, 200), 0.35)
        if i in (0, 5):
            cv.flat(57, 61, (255, 70, 60))                               # el llum anticol·lisió
            cv.glow(57, 61, 4, (255, 60, 60), 0.5)
        if i == 2:
            cv.flat(51, 63, (255, 255, 255))                             # el flaix blanc de la punta d'ala
            cv.flat(59, 63, (255, 255, 255))
        frames.append(_diff(cv.img, base))
    return frames


ANIMS = {'fluorescent': {'frames': _frames, 'frameDuration': 120},
         'avio': {'frames': _frames_avio, 'frameDuration': 140}}
