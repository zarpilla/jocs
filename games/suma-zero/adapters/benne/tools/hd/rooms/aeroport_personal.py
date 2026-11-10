"""
El racó de servei de l'aeroport (Escena 3, l'Iri), davant la porta de personal. Art definitiu:
  - un passadís de servei: bloc de formigó pintat de verd hospital, linòleum gastat, un fluorescent que
    parpelleja;
  - el vidre cap a la terminal: es veuen els seients blaus i el rètol d'objectes perduts i, mentre vigila, l'agent
    Soler (decorat `soler_vidre`, fins que la Vet el distreu);
  - la porta de personal, metàl·lica, amb la franja vermella «NOMÉS PERSONAL», i el teclat de quatre xifres amb
    les tecles 2, 4, 6 i 8 gastades; el llum: vermell (tancada), parpelleig (`alarma`) o verd (`porta_oberta`);
  - un carro de la neteja, un extintor, el senyal de terra mullat i un tauler de torns.
"""
import math

from PIL import Image

from hd.pix import Light, Canvas, W, H, hr
from hd.rooms.comu import obox, outline, text, text_width, _diff, PLASTIC, SHEET, CARD, RED, YEL, GRAYC
from hd.rooms.bar_sala import STEELB, SLATE
from hd.rooms.pis_cuina import outline_poly
from hd.rooms.aeroport_terminal import CONC, TILE, CHROME, DESK, BLUE, YELS, DAWN
from hd.characters import person
from hd.personatges import NPCS

FLOOR_Y = 150

BLOCK = [(10, 18, 16), (20, 32, 28), (32, 48, 42), (46, 66, 58), (62, 86, 76), (82, 108, 96), (104, 132, 118), (130, 156, 142), (160, 182, 168)]
LINO = [(14, 14, 18), (24, 24, 30), (36, 36, 44), (50, 50, 60), (66, 66, 78), (86, 86, 98), (108, 108, 120)]
DOOR = [(14, 18, 24), (26, 32, 42), (42, 50, 62), (60, 70, 84), (82, 94, 108), (108, 120, 134), (138, 150, 162), (172, 182, 192)]
REDB = [(40, 6, 8), (90, 14, 16), (150, 26, 26), (196, 44, 38), (230, 80, 64)]
GREENS = [(4, 30, 14), (10, 70, 30), (20, 120, 50), (60, 180, 90), (150, 240, 170)]
TROLLEY = [(20, 30, 60), (30, 50, 100), (46, 80, 150), (70, 110, 190), (120, 160, 220)]

LIGHT = Light(ambient=-0.3, vignette=(60, 30), floor_fade=(190, 28))
LIGHT.point(200, 6, r=260, k=2.6, squash=0.8, power=1.3)             # el fluorescent del passadís
LIGHT.point(100, 75, r=100, k=0.5, squash=1.2, power=2.0)            # la claror de la terminal pel vidre
LIGHT.point(236, 108, r=26, k=0.4, squash=1.0, power=2.0)            # el llum del teclat

GLASS = (20, 30, 180, 120)
LED = (236, 108)


# ─── Paret, sostre, terra ──────────────────────────────────────────────────

def wall(cv):
    """Bloc de formigó pintat de verd pàl·lid; a baix, una franja més fosca de cops de carro."""
    for y in range(0, FLOOR_Y):
        row = y // 10
        for x in range(W):
            off = 15 if row % 2 else 0
            joint = (y % 10 == 9) or ((x + off) % 30 == 29)
            n = (hr(x // 2, y // 2, 5) - 0.5) * 0.3 + (hr((x + off) // 30, row, 2) - 0.5) * 0.3
            lvl = (2.8 if joint else 4.2 + n)
            if y > 118:
                lvl -= 0.9
            cv.put(x, y, BLOCK, lvl)
    cv.rect(0, 117, W - 1, 118, BLOCK, 2.4)
    cv.rect(0, FLOOR_Y - 4, W - 1, FLOOR_Y - 1, LINO, 2.0)
    cv.hline(0, W - 1, FLOOR_Y, LINO, 0)
    # el sostre baix, amb canonades i la safata de cables
    cv.rect(0, 0, W - 1, 6, CONC, 3.0)
    cv.rect(0, 9, W - 1, 12, CHROME, lambda x, y: 2.4 + (1.4 if y == 10 else 0))
    cv.rect(0, 14, W - 1, 15, REDB, 2.4)                                 # la canonada dels bombers
    # el fluorescent
    tube(cv, on=True)


def tube(cv, on=True):
    x0, x1, y = 160, 240, 3
    obox(cv, x0 - 4, y - 2, x1 + 4, y + 3, CHROME, 3.0)
    col = (230, 244, 255) if on else (120, 130, 140)
    cv.hline(x0, x1, y + 1, [col], 0, lit=0)
    if on:
        cv.glow((x0 + x1) // 2, y + 2, 34, (220, 236, 255), 0.25)


def floor(cv):
    """Linòleum gris, gastat al camí de la porta, amb rascades de rodes."""
    for y in range(FLOOR_Y + 1, H):
        dep = (y - FLOOR_Y) / (H - FLOOR_Y)
        for x in range(W):
            n = (hr(x // 2, y, 4) - 0.5) * 0.4
            worn = max(0, 1 - abs(x - 280) / 70) * max(0, 1 - (y - FLOOR_Y) / 40) * 0.8
            cv.put(x, y, LINO, 3.4 + n + worn)
    for i in range(10):                                                  # rascades
        x = 40 + int(hr(i, 7) * 400)
        y = 158 + int(hr(i, 8) * 40)
        cv.line(x, y, x + 10 + int(hr(i, 9) * 14), y + (1 if i % 2 else 0), LINO, 1.8)
    cv.tint(140, 152, 300, 190, (220, 236, 255), lambda x, y: 0.08 * max(0, 1 - abs(x - 200) / 80) * max(0, 1 - (y - 152) / 38))


# ─── El vidre cap a la terminal ────────────────────────────────────────────

def terminal_view(cv):
    """Pel vidre: la terminal, una mica més avall i més lluny (seients blaus, el rètol groc, la vidriera de l'alba)."""
    x0, y0, x1, y1 = GLASS
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, CONC, 3.6 + (hr(x // 30, 1) - 0.5) * 0.3 - (0.6 if (x % 30) == 0 else 0), lit=0)
    # la vidriera gran de la terminal, al fons a l'esquerra, amb l'alba
    for y in range(36, 70):
        for x in range(26, 90):
            cv.put(x, y, DAWN, 1.0 + (y - 36) / 6.0, lit=0)
    cv.rect(57, 36, 58, 70, CHROME, 3.0, lit=0)
    outline(cv, 25, 35, 90, 70, CONC)
    # el rètol d'objectes perduts, a la dreta
    obox(cv, 120, 44, 172, 52, YELS, 3.2, lit=0)
    w = text_width('PERDUTS')
    text(cv, 'PERDUTS', 146 - w // 2, 46, [(30, 22, 6)], 0, lit=0, flat=(30, 22, 6))
    cv.rect(122, 53, 170, 76, CONC, 2.6, lit=0)
    # el terra de la terminal i els seients
    for y in range(80, y1 + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, TILE, 4.2 + ((y - 80) / 20), lit=0)
    for i in range(4):
        sx = 34 + i * 16
        obox(cv, sx, 74, sx + 13, 84, BLUE, 2.6, lit=0)
        cv.rect(sx - 1, 84, sx + 14, 87, BLUE, 3.4, lit=0)
    cv.rect(30, 88, 100, 89, CHROME, 3.0, lit=0)


SOLER_AT = (118, 120)   # on té els peus en Soler, vist pel vidre (amagats pel marc de baix)


def soler(cv):
    """L'agent Soler, de cara a la porta de personal (és a dir, mirant cap aquí)."""
    fig = person(NPCS['soler'], 'D')
    k = 0.82
    fig = fig.resize((round(fig.width * k), round(fig.height * k)), Image.NEAREST)
    fx, fy = SOLER_AT
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    layer.alpha_composite(fig, (fx - round(25 * k), fy - round(83 * k)))
    x0, y0, x1, y1 = GLASS
    layer = layer.crop((x0 + 2, y0 + 2, x1 - 1, y1 - 1))
    cv.img.alpha_composite(layer, (x0 + 2, y0 + 2))


def glass_frame(cv):
    """El marc d'alumini i els reflexos del passadís al vidre."""
    x0, y0, x1, y1 = GLASS
    cv.tint(x0, y0, x1, y1, (200, 230, 220), lambda x, y: 0.14 if (x + y) % 46 < 5 else 0.06)
    for (a, b, c, d) in ((x0, y0, x1, y0 + 2), (x0, y1 - 2, x1, y1), (x0, y0, x0 + 2, y1), (x1 - 2, y0, x1, y1), (99, y0, 101, y1)):
        cv.rect(a, b, c, d, CHROME, 3.2)
    outline(cv, x0 - 1, y0 - 1, x1 + 1, y1 + 1, BLOCK)
    cv.rect(x0 - 3, y1 + 1, x1 + 3, y1 + 3, CHROME, 4.0)                # l'ampit


# ─── La porta i el teclat ──────────────────────────────────────────────────

def door(cv):
    """La porta de personal: xapa grisa, la franja vermella, la barra i les frontisses."""
    x0, y0, x1, y1 = 250, 44, 312, FLOOR_Y
    obox(cv, x0 - 4, y0 - 4, x1 + 4, y1, CHROME, 2.6)
    door_leaf(cv)
    cv.darken(x1 + 5, y0, x1 + 9, y1, 0.4)


def door_leaf(cv):
    x0, y0, x1, y1 = 250, 44, 312, FLOOR_Y
    obox(cv, x0, y0, x1, y1, DOOR, 3.6, top=0.6)
    for yy in (y0 + 6, y1 - 30):
        cv.rect(x0 + 4, yy, x1 - 4, yy + 22, DOOR, 3.2)
        cv.hline(x0 + 4, x1 - 4, yy, DOOR, 2.0)
        cv.hline(x0 + 4, x1 - 4, yy + 22, DOOR, 4.6)
    # la franja vermella amb el text
    obox(cv, 258, 53, 304, 70, REDB, 3.0)
    for k, word in enumerate(('NOMÉS', 'PERSONAL')):
        text(cv, word, 281 - text_width(word) // 2, 57 + k * 6, [(250, 244, 236)], 0, flat=(250, 244, 236))
    # la maneta i la placa
    obox(cv, 254, 100, 258, 112, CHROME, 3.6)
    cv.rect(254, 104, 266, 106, CHROME, 4.6)
    for hy in (54, 136):                                                 # frontisses, a la dreta
        cv.rect(x1 - 1, hy, x1 + 1, hy + 6, CHROME, 3.2)


def keypad(cv, led='vermell'):
    """El teclat: caixa d'alumini, dotze tecles (2, 4, 6 i 8 gastades), una pantalleta i el llum."""
    x0, y0, x1, y1 = 224, 84, 248, 114
    obox(cv, x0, y0, x1, y1, CHROME, 2.8, top=1.0)
    cv.rect(x0 + 3, y0 + 2, x1 - 3, y0 + 5, [(10, 20, 14), (30, 60, 40)], 1.0, lit=0)
    keys = '123456789*0#'
    for i, kch in enumerate(keys):
        kx = x0 + 4 + (i % 3) * 6
        ky = y0 + 7 + (i // 3) * 5
        worn = kch in '2468'
        cv.rect(kx, ky, kx + 3, ky + 3, CHROME, 4.6 if worn else 3.4)
        cv.flat(kx + 3, ky + 3, CHROME[1])
        if worn:
            cv.flat(kx + 1, ky + 1, (232, 230, 220))
    led_at(cv, led)


def led_at(cv, led):
    lx, ly = LED
    col = {'vermell': (230, 40, 36), 'verd': (60, 230, 100), 'alarma': (255, 70, 40)}[led]
    cv.disc(lx, ly, 2.2, 1.6, [col], 0, lit=0)
    cv.flat(lx - 1, ly - 1, tuple(min(255, c + 60) for c in col))
    cv.glow(lx, ly, 6 if led != 'alarma' else 20, col, 0.45 if led != 'alarma' else 0.7)


# ─── El passadís ───────────────────────────────────────────────────────────

def extinguisher(cv):
    """Un extintor penjat i el seu cartell."""
    obox(cv, 196, 64, 208, 72, REDB, 3.4)
    cv.rect(199, 66, 205, 70, [(250, 244, 236)], 0)
    cv.disc(202, 98, 4.4, 3, REDB, lambda nx, ny: 3.4 - ny)
    cv.rect(198, 98, 206, 120, REDB, lambda x, y: 3.0 + (1.6 if x == 200 else 0) - (0.8 if x == 206 else 0))
    obox(cv, 200, 92, 204, 95, SLATE, 2.6)
    cv.line(204, 94, 210, 104, SLATE, 1.6)
    cv.disc(202, 112, 3, 1.8, [(250, 244, 236)], 0)


def emergency_sign(cv):
    """El senyal verd de sortida, damunt la porta."""
    obox(cv, 266, 26, 296, 36, GREENS, 2.6, lit=0)
    cv.rect(270, 28, 274, 34, [(240, 255, 240)], 0, lit=0)               # l'home que corre (més o menys)
    cv.line(277, 31, 292, 31, [(240, 255, 240)], 0, lit=0)
    cv.line(289, 29, 292, 31, [(240, 255, 240)], 0, lit=0)
    cv.line(289, 33, 292, 31, [(240, 255, 240)], 0, lit=0)
    cv.glow(281, 31, 18, (120, 255, 150), 0.18)


def notice_board(cv):
    """El tauler de torns, amb fulls de colors i una nota amb caràcter."""
    x0, y0, x1, y1 = 336, 52, 398, 100
    obox(cv, x0, y0, x1, y1, CARD, 2.6)
    obox(cv, x0 + 3, y0 + 3, x1 - 3, y0 + 9, SHEET, 4.6)
    text(cv, 'TORNS', x0 + (x1 - x0 - text_width('TORNS')) // 2, y0 + 4, [(20, 20, 30)], 0, flat=(30, 30, 40))
    for j in range(5):                                                   # la graella
        yy = y0 + 12 + j * 4
        cv.hline(x0 + 4, x1 - 22, yy, SHEET, 4.2)
        for i in range(6):
            if hr(i, j, 3) > 0.5:
                cv.rect(x0 + 5 + i * 6, yy + 1, x0 + 8 + i * 6, yy + 2, [[(60, 100, 200)], [(220, 70, 60)]][(i + j) % 2], 0)
    obox(cv, x1 - 18, y0 + 13, x1 - 4, y0 + 26, YELS, 4.2)               # un pòsit
    obox(cv, x0 + 6, y0 + 34, x0 + 30, y1 - 4, [(40, 60, 90), (90, 130, 170), (170, 200, 230), (220, 236, 248)], 3.0)
    for k in range(3):
        cv.hline(x0 + 9, x0 + 26 - k * 4, y0 + 38 + k * 3, SLATE, 1.6)
    for (px, py) in ((x0 + 5, y0 + 2), (x1 - 5, y0 + 2), (x1 - 11, y0 + 12), (x0 + 18, y0 + 33)):
        cv.disc(px, py, 1, 1, RED, 3.4)


def lockers(cv):
    """Tres taquilles del personal, una amb la porta mal tancada."""
    for i in range(3):
        x0 = 410 + i * 22
        obox(cv, x0, 50, x0 + 20, FLOOR_Y, [(20, 30, 40), (34, 50, 64), (52, 74, 92), (74, 100, 120), (100, 128, 150), (140, 166, 184)], 2.8, top=0.6)
        for k in range(4):
            cv.hline(x0 + 5, x0 + 15, 56 + k * 2, SLATE, 1.0)
        cv.rect(x0 + 15, 96, x0 + 16, 104, CHROME, 4.0)
    cv.darken(452, 51, 454, FLOOR_Y - 1, 0.6)                           # l'escletxa de la mal tancada
    cv.line(456, 70, 455, 74, [(220, 70, 60)], 0)                        # una màniga que en surt


def trolley(cv):
    """El carro de la neteja amb la galleda, el pal de la fregona i les bosses."""
    x0, x1 = 336, 396
    cv.rect(x0, 128, x1, 132, TROLLEY, 3.0)
    cv.rect(x0 + 2, 132, x0 + 3, 160, CHROME, 3.0)
    cv.rect(x1 - 3, 132, x1 - 2, 160, CHROME, 3.0)
    cv.rect(x0, 150, x1, 152, TROLLEY, 2.6)
    for wx in (x0 + 3, x1 - 3):
        cv.disc(wx, 162, 2.2, 2.2, SLATE, 1.8)
    # la bossa groga d'escombraries penjada
    cv.poly([(x0 + 2, 104), (x0 + 22, 104), (x0 + 24, 128), (x0, 128)], YELS, lambda x, y: 2.6 + (0.6 if x < x0 + 6 else 0))
    outline_poly(cv, [(x0 + 2, 104), (x0 + 22, 104), (x0 + 24, 128), (x0, 128)], YELS)
    # els esprais i la galleda blava
    for i, c in enumerate(([(10, 60, 30), (30, 140, 70), (100, 220, 140)], [(80, 10, 60), (170, 40, 140), (240, 120, 220)])):
        obox(cv, x0 + 30 + i * 8, 116, x0 + 35 + i * 8, 128, c, 1.6)
    cv.poly([(x0 + 46, 136), (x1 - 2, 136), (x1 - 4, 150), (x0 + 48, 150)], TROLLEY, 2.4)
    cv.line(x0 + 52, 136, x0 + 58, 104, CARD, 3.0)
    cv.darken(x0 - 2, 164, x1 + 2, 167, 0.55)


def wet_floor(cv):
    """El senyal groc de terra mullat (en tres idiomes, en teoria; aquí només el ninot que cau)."""
    cx = 104
    cv.poly([(cx - 8, 186), (cx - 3, 156), (cx + 3, 156), (cx + 8, 186)], YELS, lambda x, y: 3.4 - (x - cx) * 0.08)
    outline_poly(cv, [(cx - 8, 186), (cx - 3, 156), (cx + 3, 156), (cx + 8, 186)], YELS)
    cv.disc(cx, 166, 1.2, 1.2, [(20, 16, 6)], 0)
    cv.line(cx, 168, cx - 2, 173, [(20, 16, 6)], 0)
    cv.line(cx - 2, 173, cx + 2, 176, [(20, 16, 6)], 0)
    cv.line(cx - 4, 177, cx + 3, 177, [(20, 16, 6)], 0)
    cv.darken(cx - 9, 187, cx + 9, 189, 0.5)


def radiator(cv):
    """Un radiador sota el vidre."""
    for i in range(14):
        x = 40 + i * 6
        cv.rect(x, 126, x + 4, 144, SHEET, lambda xx, yy: 3.6 + (0.8 if xx == x else 0) - (0.8 if xx == x + 4 else 0))
    cv.rect(38, 144, 124, 145, SHEET, 2.4)


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


# ─── Props ──────────────────────────────────────────────────────────────────

def soler_vidre(cv):
    """En Soler, vigilant, vist pel vidre (fins que la Vet el distreu)."""
    base = Canvas(light=LIGHT)
    bg(base)
    var = Canvas(light=LIGHT)
    bg(var, soler_hi=True)
    cv.img.alpha_composite(_diff(var.img, base.img))


def porta_oberta(cv):
    """La porta oberta cap endins: es veu l'oficina (llum fluorescent, un arxivador) i el llum verd."""
    x0, y0, x1, y1 = 250, 44, 312, FLOOR_Y
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, CONC if y < 120 else TILE, (3.2 if y < 120 else 3.6) - (x1 - x) * 0.02)
    cv.rect(x0, 119, x1, 120, CONC, 1.6)
    obox(cv, 286, 70, 306, 140, DESK, 3.0)                               # un arxivador
    for k in range(3):
        cv.rect(292, 78 + k * 20, 300, 79 + k * 20, CHROME, 4.0)
    cv.rect(260, 48, 300, 49, [(230, 244, 255)], 0, lit=0)               # el fluorescent de l'oficina
    cv.glow(280, 50, 20, (220, 236, 255), 0.3)
    # el cantell de la porta, oberta cap endins (a l'esquerra)
    cv.poly([(x0, y0), (x0 + 8, y0 + 4), (x0 + 8, y1 - 2), (x0, y1)], DOOR, lambda x, y: 4.0 - (x - x0) * 0.2)
    outline_poly(cv, [(x0, y0), (x0 + 8, y0 + 4), (x0 + 8, y1 - 2), (x0, y1)], DOOR)
    led_at(cv, 'verd')


def alarma(cv):
    """La porta xiula: el llum vermell encès de debò, que tenyeix el teclat i la porta."""
    base = Canvas(light=LIGHT)
    bg(base)
    var = Canvas(light=LIGHT, img=base.img.copy())
    led_at(var, 'alarma')
    var.glow(LED[0], LED[1], 46, (255, 40, 30), 0.55)
    var.disc(LED[0], LED[1], 3, 2.4, [(255, 120, 90)], 0, lit=0)
    cv.img.alpha_composite(_diff(var.img, base.img))


PROPS = {'soler_vidre': soler_vidre, 'porta_oberta': porta_oberta, 'alarma': alarma}


# ─── El fluorescent que parpelleja ─────────────────────────────────────────

def _frames():
    base = Canvas(light=LIGHT)
    bg(base)
    frames = []
    for i in range(16):
        cv = Canvas(light=LIGHT, img=base.img.copy())
        if i in (5, 7, 12):
            tube(cv, on=False)
            cv.darken(150, 0, 250, 14, 0.25)
        frames.append(_diff(cv.img, base.img))
    return frames


def _frames_avio():
    """Per la vidriera del fons de la terminal, un avió que s'acosta de cara: el far fix i el llum vermell que parpelleja."""
    base = Canvas(light=LIGHT)
    bg(base)
    frames = []
    for i in range(10):
        cv = Canvas(light=LIGHT, img=base.img.copy())
        cv.flat(41, 47, (250, 240, 220))                                 # el far d'aterratge
        cv.glow(41, 47, 2, (255, 236, 200), 0.35)
        if i in (0, 5):
            cv.flat(43, 46, (255, 70, 60))                               # el llum anticol·lisió
            cv.glow(43, 46, 3, (255, 60, 60), 0.5)
        if i == 2:
            cv.flat(39, 47, (255, 255, 255))                             # el flaix blanc de la punta d'ala
        frames.append(_diff(cv.img, base.img))
    return frames


ANIMS = {'fluorescent': {'frames': _frames, 'frameDuration': 120},
         'avio': {'frames': _frames_avio, 'frameDuration': 140}}
