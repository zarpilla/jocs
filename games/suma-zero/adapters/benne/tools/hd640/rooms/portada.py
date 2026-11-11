"""
La portada, a 640×360 (vegeu hd/rooms/portada.py, la de 480×270): «SUMA ZERO» damunt la ciutat de nit.
  - a primer terme, a l'esquerra, el bloc del pis: la finestra encesa de verd (l'Iri, l'ordinador i els cables
    que surten per la façana fins a l'antena parabòlica del terrat);
  - els terrats de la ciutat (dipòsits, antenes, finestres) i, a l'horitzó, la torre daurada del BCMU: l'antena
    de l'Iri l'apunta, i un pols de llum hi viatja (l'animació);
  - a baix a la dreta, el neó magenta de La Propina (fa una pampallugua);
  - el títol en lletres grosses (cel·les de 7 px en lloc de 5), verd blavós com els botons, amb bisell a cada
    cel·la, un reflex a dalt, vora fosca i ombra magenta.
Els botons de la GUI `portada` van a 220..420 × 261..328 (×4/3 de 165..315 × 196..246): allà només hi ha terrats.
Animació: `senyal`.
"""
import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

import math

from hd.pix import Light, Canvas, W, H, hr
from hd.rooms.comu import obox, outline, cable, text, text_width, _diff, NEON
from room_designs import LLETRES

SKYP = [(4, 2, 12), (8, 6, 22), (14, 10, 34), (22, 14, 46), (34, 18, 58), (50, 22, 70), (70, 28, 80), (96, 36, 88)]
ROOF = [(4, 3, 10), (8, 6, 16), (12, 10, 22), (18, 14, 30), (26, 20, 40)]
BLOCK = [(6, 5, 10), (12, 10, 18), (20, 16, 26), (30, 24, 36), (42, 34, 48), (58, 48, 62)]
WARM = [(60, 36, 10), (140, 90, 30), (220, 160, 70), (250, 214, 130)]
TEAL = [(4, 30, 34), (8, 60, 64), (14, 100, 100), (24, 144, 140), (60, 196, 170), (150, 240, 210), (230, 255, 244)]
GOLD = [(60, 40, 6), (130, 92, 16), (200, 150, 30), (240, 200, 70), (255, 236, 150)]
SHADOW = [(50, 6, 44), (70, 10, 60), (110, 20, 88), (140, 26, 108)]
EDGE = [(6, 10, 22)]
TITLE_Y = 40
S = 7                                     # mida del «píxel» de les lletres
DISH = (165, 117)
TOWER_TOP = (565, 149)
TOWER_X = (547, 584)
N = 12                                    # fotogrames del bucle (els 10 primers, el pols)

LIGHT = Light(ambient=0.0)


def sky(cv):
    for y in range(0, 267):
        for x in range(W):
            cv.put(x, y, SKYP, 0.6 + y / 40 + (hr(x // 3, y // 3) - 0.5) * 0.2, lit=0)
    for i in range(160):
        x, y = int(hr(i, 11) * W), int(hr(i, 12) * 147)
        b = hr(i, 13)
        cv.flat(x, y, (210, 200, 240) if b > 0.75 else (110, 100, 150) if b > 0.3 else (70, 60, 104))
        if b > 0.96:
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                cv.flat(x + dx, y + dy, (96, 84, 136))


def tower(cv):
    """La torre del BCMU, petita i daurada, a l'horitzó."""
    x0, x1 = TOWER_X
    top = TOWER_TOP[1]
    for y in range(top, 253):
        for x in range(x0, x1 + 1):
            cv.put(x, y, GOLD, 1.0 + (0.8 if (y - top) % 7 == 0 else 0) + (1.2 if x - x0 < 3 else 0)
                   - (0.5 if x1 - x < 2 else 0) - (y - top) / 107, lit=0)
    for fy in range(top + 4, 248, 7):
        for fx in range(x0 + 4, x1 - 3, 6):
            if hr(fx, fy, 4) > 0.5:
                cv.rect(fx, fy, fx + 3, fy + 2, GOLD, 3.6, lit=0)
    cv.rect(x0 - 1, top - 3, x1 + 1, top - 1, GOLD, 2.6, lit=0)        # el coronament
    cx = (x0 + x1) // 2
    cv.vline(cx, top - 16, top - 4, GOLD, 2.0, lit=0)                    # l'antena
    cv.flat(cx, top - 17, (255, 90, 70))
    w = text_width('BCMU')
    text(cv, 'BCMU', cx - w // 2, top - 11, GOLD, 4, lit=0)
    cv.glow(cx, top + 27, 61, (255, 200, 90), 0.22)


def roofs(cv):
    """Els terrats de la ciutat, en dos plans."""
    for plane, (base, hmin, hmax, lvl, seed) in enumerate(((248, 13, 45, 1.6, 3), (261, 21, 67, 0.8, 5))):
        x = 0
        i = 0
        while x < W:
            w = 24 + int(hr(i, seed) * 40)
            h = hmin + int(hr(i, seed + 1) * (hmax - hmin))
            top = base - h
            for yy in range(top, 275):
                for xx in range(x, min(W, x + w)):
                    cv.put(xx, yy, ROOF, lvl + (0.4 if yy == top else 0) - (0.3 if xx == x + w - 1 else 0), lit=0)
            # finestres
            for wy in range(top + 5, 267, 8):
                for wx in range(x + 4, x + w - 4, 7):
                    r = hr(wx, wy, seed + 2)
                    if r > 0.8:
                        cv.rect(wx, wy, wx + 2, wy + 3, WARM, lambda px, py: 1.6 + plane + (0.5 if py == wy else 0), lit=0)
                        if hr(wx, wy, seed + 9) > 0.6:                   # una cortina mig tirada
                            cv.rect(wx, wy, wx, wy + 3, WARM, 0.6 + plane, lit=0)
                    elif r > 0.77:
                        cv.rect(wx, wy, wx + 2, wy + 3, [(60, 90, 160), (120, 160, 230)], 1, lit=0)
            # un dipòsit d'aigua o una antena, de tant en tant
            if hr(i, seed + 3) > 0.6:
                cv.rect(x + 5, top - 9, x + 16, top - 2, ROOF, lambda px, py: lvl + 0.6 + (0.4 if px < x + 7 else 0), lit=0)
                cv.hline(x + 4, x + 17, top - 10, ROOF, lvl + 1.0, lit=0)   # la tapa
                cv.hline(x + 5, x + 16, top - 6, ROOF, lvl + 0.2, lit=0)    # el cèrcol
                for lx in (x + 6, x + 15):
                    cv.vline(lx, top - 2, top, ROOF, lvl + 0.6, lit=0)
            elif hr(i, seed + 4) > 0.6:
                ax = x + w // 2
                cv.vline(ax, top - 13, top, ROOF, lvl + 1.0, lit=0)
                cv.hline(ax - 4, ax + 4, top - 9, ROOF, lvl + 1.0, lit=0)
                cv.hline(ax - 2, ax + 2, top - 12, ROOF, lvl + 1.0, lit=0)
            x += w
            i += 1


def block(cv):
    """El bloc del pis, a primer terme: la finestra encesa i els cables fins a la parabòlica."""
    x0, x1, top = 0, 187, 128
    for y in range(top, H):
        for x in range(x0, x1 + 1):
            row = y // 8
            brick = (y % 8 == 0) or ((x + (row % 2) * 9) % 18 == 0)
            cv.put(x, y, BLOCK, (2.0 if brick else 2.9) + (hr(x // 3, y // 3) - 0.5) * 0.3 - (x / 267) - max(0, (y - 267) / 80), lit=0)
    cv.rect(x0, top - 4, x1 + 3, top, BLOCK, lambda x, y: 3.2 + (0.6 if y == top - 4 else 0), lit=0)   # l'ampit del terrat
    cv.vline(x1 + 1, top + 1, H - 1, BLOCK, 1.2, lit=0)                 # el cantó, a l'ombra
    # les altres finestres, apagades o amb la tele
    for (wx, wy) in ((19, 149), (128, 149), (128, 267), (19, 267)):
        cv.rect(wx, wy, wx + 29, wy + 35, [(4, 4, 8), (10, 10, 18)], 0.6, lit=0)
        cv.vline(wx + 14, wy, wy + 35, BLOCK, 1.4, lit=0)                # el muntant
        outline(cv, wx - 1, wy - 1, wx + 30, wy + 36, BLOCK)
        cv.rect(wx - 3, wy + 36, wx + 32, wy + 38, BLOCK, lambda x, y: 3.4 if y == wy + 36 else 2.2, lit=0)   # l'ampit
    cv.rect(129, 268, 156, 300, [(20, 30, 70), (40, 60, 130)], 0.6, lit=0)   # algú mira la tele
    cv.glow(140, 284, 14, (90, 120, 230), 0.25)
    cv.disc(147, 296, 4, 5, [(8, 10, 20)], 0, lit=0)                     # el cap de qui mira, a contrallum
    cv.vline(142, 268, 302, BLOCK, 1.4, lit=0)
    for k in range(4):                                                   # una persiana mig abaixada al pis de dalt
        cv.hline(129, 156, 150 + k * 3, BLOCK, 1.6, lit=0)
    # la finestra del pis: verd de pantalla, i l'Iri retallada a contrallum
    wx0, wy0, wx1, wy1 = 53, 187, 117, 243
    for y in range(wy0, wy1 + 1):
        for x in range(wx0, wx1 + 1):
            cv.put(x, y, TEAL, 2.6 + (1.2 * max(0, 1 - math.hypot(x - 93, y - 213) / 29)), lit=0)
    sil = [(4, 10, 12)]
    cv.rect(85, 200, 107, 216, TEAL, 6.0, lit=0)                         # el monitor
    cv.rect(88, 203, 104, 213, TEAL, lambda x, y: 4.4 + (0.6 if (y - 203) % 3 == 0 else 0), lit=0)   # línies de codi
    for k in range(4):
        cv.hline(89, 89 + int(hr(k, 21) * 12), 204 + k * 3, TEAL, 6.0, lit=0)
    cv.rect(93, 216, 99, 221, sil, 0, lit=0)                             # el peu
    cv.rect(109, 208, 114, 221, TEAL, 3.6, lit=0)                        # el segon monitor, de cantó
    outline(cv, 109, 208, 114, 221, [(4, 10, 12)])
    cv.disc(75, 208, 6.5, 8, sil, 0, lit=0)                              # el cap, amb la cua
    cv.line(68, 208, 63, 221, sil, 0, lit=0)
    cv.line(69, 209, 64, 222, sil, 0, lit=0)
    cv.line(70, 209, 65, 222, sil, 0, lit=0)
    cv.rect(65, 216, 84, wy1, sil, 0, lit=0)                             # les espatlles i la cadira
    cv.vline(64, 222, wy1, sil, 0, lit=0)
    cv.disc(81, 205, 2, 3, [(200, 30, 40)], 0, lit=0)                    # l'auricular vermell
    cv.line(81, 202, 76, 199, [(200, 30, 40)], 0, lit=0)                 # la diadema de l'auricular
    for k, (dx, col) in enumerate(((0, (220, 50, 50)), (1, (230, 200, 60)), (2, (60, 190, 90)))):
        cv.flat(71 + dx * 2, 200 + (1 if dx == 1 else 0), col)           # la diadema de l'Iri, de tres colors
    cv.rect(wx0, 228, wx1, 229, sil, 0, lit=0)                           # la taula
    cv.rect(88, 225, 102, 227, TEAL, 3.2, lit=0)                         # el teclat
    cv.rect(105, 222, 108, 227, [(8, 20, 22), (40, 60, 60)], 1, lit=0)   # la tassa
    cv.vline(85, 230, wy1, sil, 0, lit=0)                                # la pota de la taula
    for x in range(wx0, wx1 + 1, 2):                                     # el reflex al vidre
        cv.tint(x, wy0, x, wy0 + 1, (230, 255, 244), 0.15)
    cv.vline((wx0 + wx1) // 2 - 12, wy0, wy1, BLOCK, 1.0, lit=0)        # el muntant
    outline(cv, wx0 - 1, wy0 - 1, wx1 + 1, wy1 + 1, BLOCK)
    cv.rect(wx0 - 4, wy1 + 1, wx1 + 4, wy1 + 4, BLOCK, lambda x, y: 3.4 + (0.6 if y == wy1 + 1 else 0), lit=0)
    cv.glow(85, 213, 80, (60, 230, 190), 0.16)
    # els cables: surten per la finestra i pugen per la façana fins a la parabòlica
    for k, col in enumerate(([(20, 20, 26), (60, 60, 70)], [(60, 10, 14), (150, 30, 30)], [(10, 30, 50), (30, 80, 120)])):
        cable(cv, [(wx1 + 1, wy0 + 11 + k * 4), (wx1 + 40, wy0 + 27), (157 + k * 3, 173), (DISH[0] - 3 + k * 3, DISH[1] + 11)], col, 1.0)
    # la parabòlica, que apunta a la torre
    dx, dy = DISH
    cv.rect(dx - 1, dy + 3, dx + 1, top, ROOF, lambda x, y: 2.6 + (0.6 if x == dx - 1 else 0), lit=0)
    cv.line(dx - 6, top - 1, dx, dy + 8, ROOF, 2.2, lit=0)               # el puntal
    cv.disc(dx + 4, dy - 3, 11, 8, [(40, 44, 54), (90, 96, 110), (150, 156, 170), (200, 206, 214)], lambda nx, ny: 2.4 + nx - ny * 0.6, lit=0)
    for a in range(0, 360, 4):                                           # la vora del plat
        cv.put(round(dx + 4 + math.cos(math.radians(a)) * 11), round(dy - 3 + math.sin(math.radians(a)) * 8),
               [(40, 44, 54), (90, 96, 110)], 0.6, lit=0)
    cv.line(dx + 4, dy - 3, dx + 16, dy - 8, [(200, 206, 214)], 0, lit=0)
    cv.line(dx + 4, dy + 3, dx + 16, dy - 8, [(150, 156, 170)], 0, lit=0)   # el segon braç del LNB
    cv.rect(dx + 15, dy - 9, dx + 17, dy - 7, [(250, 60, 60)], 0, lit=0)
    cv.flat(dx + 16, dy - 8, (255, 160, 150))


def bar_sign(cv, on=True):
    """A baix a la dreta, el neó de La Propina en un local baix (ara sí, del dret)."""
    obox(cv, 453, 285, 637, H - 1, ROOF, 1.4, lit=0)
    cv.hline(453, 637, 290, ROOF, 2.6, lit=0)                            # la cornisa
    w = text_width('LA PROPINA')
    col = (255, 120, 200) if on else (110, 40, 90)
    tx = 545 - w // 2
    cv.rect(tx - 5, 295, tx + w + 4, 309, [(16, 6, 16)], 0, lit=0)      # el rètol, de fons fosc
    outline(cv, tx - 5, 295, tx + w + 4, 309, [(60, 20, 50)] if on else [(30, 10, 26)])
    text(cv, 'LA PROPINA', tx, 299, NEON, 0, lit=0, flat=col)
    if on:
        cv.glow(545, 302, 40, (255, 90, 200), 0.35)
    for ax in (469, 595):                                                # els aparadors
        cv.rect(ax, 315, ax + 27, H - 1, [(30, 14, 30), (60, 26, 50)], lambda x, y: 1.0 + (0.6 if (x - y) % 11 == 0 else 0), lit=0)
        outline(cv, ax - 1, 314, ax + 28, H, [(8, 4, 10)])
    cv.rect(528, 318, 562, H - 1, [(14, 6, 14), (40, 18, 36)], 0.6, lit=0)   # la porta
    outline(cv, 527, 317, 563, H, [(8, 4, 10)])
    cv.flat(558, 340, (200, 160, 80))                                    # el pom


def title(cv):
    """«SUMA ZERO»: lletres de 5×7 a cel·les de 7 px, cos verd blavós amb degradat i bisell, vora fosca i
    ombra magenta."""
    word = 'SUMA ZERO'
    width = len(word) * 6 * S - S
    x0 = (W - width) // 2
    cells = []
    for i, ch in enumerate(word):
        for r, bits in enumerate(LLETRES[ch]):
            for c, bit in enumerate(bits):
                if bit == '1':
                    cells.append((x0 + (i * 6 + c) * S, TITLE_Y + r * S))
    filled = set(cells)
    for x, y in cells:                                                   # l'ombra magenta
        cv.rect(x + 4, y + 4, x + S + 3, y + S + 3, SHADOW, lambda px, py: 3.4 - (py - TITLE_Y) / 40, lit=0)
    for x, y in cells:                                                   # la vora
        cv.rect(x - 1, y - 1, x + S, y + S, EDGE, 0, lit=0)
    hl = TITLE_Y + 2.2 * S                                               # la ratlla del reflex
    for x, y in cells:
        top_open = (x, y - S) not in filled
        bot_open = (x, y + S) not in filled
        left_open = (x - S, y) not in filled
        right_open = (x + S, y) not in filled
        for py in range(y, y + S):
            for px in range(x, x + S):
                lvl = 5.6 - (py - TITLE_Y) / 12
                if py == y and top_open:
                    lvl += 1.0
                if px == x and left_open:
                    lvl += 0.5
                if px == x + S - 1 and right_open:
                    lvl -= 0.8
                if py == y + S - 1 and bot_open:
                    lvl -= 0.7
                if py < hl - (px - x0) * 0.04:                           # el vidre de dalt, més clar
                    lvl += 0.5
                cv.put(px, py, TEAL, lvl, lit=0)
    for x, y in cells:                                                   # una espurna a algunes cantonades
        if (x, y - S) not in filled and (x - S, y) not in filled and hr(x, y, 41) > 0.6:
            cv.flat(x + 1, y + 1, TEAL[6])
    cv.glow(W // 2, TITLE_Y + 21, 200, (60, 220, 190), 0.06)


def signal(cv, frame):
    """El pols de llum que va de la parabòlica a la torre, amb una cueta."""
    ax, ay = DISH[0] + 16, DISH[1] - 8
    bx, by = TOWER_TOP[0] + 1, TOWER_TOP[1] - 17
    n = 10
    for k, (dt, a) in enumerate(((0, 1.0), (0.025, 0.5), (0.05, 0.25))):
        t = frame / n - dt
        if t < 0:
            continue
        px = ax + (bx - ax) * t
        py = ay + (by - ay) * t - math.sin(t * math.pi) * 40
        if k == 0:
            cv.glow(px, py, 8, (120, 255, 220), 0.7)
            cv.rect(px - 1, py, px + 1, py, [(220, 255, 240)], 0, lit=0)
            cv.flat(px, py - 1, (220, 255, 240))
            cv.flat(px, py + 1, (220, 255, 240))
        else:
            cv.glow(px, py, 5, (120, 255, 220), 0.5 * a)
            cv.flat(px, py, (120, 220, 200))


def bg(cv):
    sky(cv)
    tower(cv)
    roofs(cv)
    block(cv)
    bar_sign(cv)
    title(cv)


PROPS = {}


def _frames():
    base = Canvas(light=LIGHT)
    bg(base)
    frames = []
    for i in range(N):
        cv = Canvas(light=LIGHT, img=base.img.copy())
        if i < 10:
            signal(cv, i)
        if i == 7:
            bar_sign(cv, on=False)
        if i == 10:                                                      # la torre ha rebut el senyal: l'antena s'encén
            cx = sum(TOWER_X) // 2
            cv.glow(cx, TOWER_TOP[1] - 17, 7, (255, 120, 90), 0.8)
        if i % 4 == 0:
            cv.rect(DISH[0] + 15, DISH[1] - 9, DISH[0] + 17, DISH[1] - 7, [(90, 20, 20)], 0, lit=0)
        frames.append(_diff(cv.img, base.img))
    return frames


ANIMS = {'senyal': {'frames': _frames, 'frameDuration': 140}}

GEOMETRIA = {'things': {}, 'spawns': {}, 'walkable': [(200, 253), (267, 253), (267, 261), (200, 261)]}
