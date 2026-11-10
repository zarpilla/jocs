"""
La portada: «SUMA ZERO» damunt la ciutat de nit. Art definitiu:
  - a primer terme, a l'esquerra, el bloc del pis: la finestra encesa de verd (l'Iri, l'ordinador i els cables
    que surten per la façana fins a l'antena parabòlica del terrat);
  - els terrats de la ciutat (dipòsits, antenes, finestres) i, a l'horitzó, la torre daurada del BCMU: l'antena
    de l'Iri l'apunta, i un pols de llum hi viatja (l'animació);
  - a baix a la dreta, el neó magenta de La Propina;
  - el títol en lletres grosses, verd blavós com els botons, amb ombra magenta.
Els botons («Comença», «Carrega») són de la GUI `portada` (draw_placeholders.draw_cover_gui), a 165..315 × 196..246.
"""
import math

from PIL import Image

from hd.pix import Light, Canvas, W, H, hr
from hd.rooms.comu import obox, outline, cable, text, text_width, _diff, NEON
from room_designs import LLETRES

SKYP = [(4, 2, 12), (8, 6, 22), (14, 10, 34), (22, 14, 46), (34, 18, 58), (50, 22, 70), (70, 28, 80), (96, 36, 88)]
ROOF = [(4, 3, 10), (8, 6, 16), (12, 10, 22), (18, 14, 30), (26, 20, 40)]
BLOCK = [(6, 5, 10), (12, 10, 18), (20, 16, 26), (30, 24, 36), (42, 34, 48), (58, 48, 62)]
WARM = [(60, 36, 10), (140, 90, 30), (220, 160, 70), (250, 214, 130)]
TEAL = [(4, 30, 34), (8, 60, 64), (14, 100, 100), (24, 144, 140), (60, 196, 170), (150, 240, 210), (230, 255, 244)]
GOLD = [(60, 40, 6), (130, 92, 16), (200, 150, 30), (240, 200, 70), (255, 236, 150)]
TITLE_Y = 30
DISH = (124, 88)
TOWER_TOP = (424, 112)

LIGHT = Light(ambient=0.0)


def sky(cv):
    for y in range(0, 200):
        for x in range(W):
            cv.put(x, y, SKYP, 0.6 + y / 30 + (hr(x // 3, y // 3) - 0.5) * 0.2, lit=0)
    for i in range(90):
        x, y = int(hr(i, 11) * W), int(hr(i, 12) * 110)
        cv.flat(x, y, (210, 200, 240) if hr(i, 13) > 0.75 else (110, 100, 150))


def tower(cv):
    """La torre del BCMU, petita i daurada, a l'horitzó."""
    x0, x1 = 410, 438
    top = TOWER_TOP[1]
    for y in range(top, 190):
        for x in range(x0, x1 + 1):
            cv.put(x, y, GOLD, 1.0 + (0.8 if (y - top) % 5 == 0 else 0) + (1.2 if x - x0 < 2 else 0) - (y - top) / 80, lit=0)
    for fy in range(top + 3, 186, 5):
        for fx in range(x0 + 3, x1 - 2, 5):
            if hr(fx, fy, 4) > 0.5:
                cv.rect(fx, fy, fx + 2, fy + 1, GOLD, 3.6, lit=0)
    cv.vline((x0 + x1) // 2, top - 12, top, GOLD, 2.0, lit=0)            # l'antena
    w = text_width('BCMU')
    text(cv, 'BCMU', (x0 + x1) // 2 - w // 2, top - 8 + 0, GOLD, 4, lit=0)
    cv.glow((x0 + x1) // 2, top + 20, 46, (255, 200, 90), 0.22)


def roofs(cv):
    """Els terrats de la ciutat, en tres plans."""
    for plane, (base, hmin, hmax, lvl, seed) in enumerate(((186, 10, 34, 1.6, 3), (196, 16, 50, 0.8, 5))):
        x = 0
        i = 0
        while x < W:
            w = 18 + int(hr(i, seed) * 30)
            h = hmin + int(hr(i, seed + 1) * (hmax - hmin))
            top = base - h
            for yy in range(top, 206):
                for xx in range(x, min(W, x + w)):
                    cv.put(xx, yy, ROOF, lvl, lit=0)
            # finestres
            for wy in range(top + 4, 200, 6):
                for wx in range(x + 3, x + w - 3, 5):
                    r = hr(wx, wy, seed + 2)
                    if r > 0.8:
                        cv.rect(wx, wy, wx + 1, wy + 2, WARM, 1.6 + plane, lit=0)
                    elif r > 0.77:
                        cv.rect(wx, wy, wx + 1, wy + 2, [(60, 90, 160), (120, 160, 230)], 1, lit=0)
            # un dipòsit d'aigua o una antena, de tant en tant
            if hr(i, seed + 3) > 0.6:
                cv.rect(x + 4, top - 7, x + 12, top - 1, ROOF, lvl + 0.6, lit=0)
                cv.vline(x + 5, top - 1, top, ROOF, lvl + 0.6, lit=0)
                cv.vline(x + 11, top - 1, top, ROOF, lvl + 0.6, lit=0)
            elif hr(i, seed + 4) > 0.6:
                cv.vline(x + w // 2, top - 10, top, ROOF, lvl + 1.0, lit=0)
                cv.hline(x + w // 2 - 3, x + w // 2 + 3, top - 7, ROOF, lvl + 1.0, lit=0)
            x += w
            i += 1


def block(cv):
    """El bloc del pis, a primer terme: la finestra encesa i els cables fins a la parabòlica."""
    x0, x1, top = 0, 140, 96
    for y in range(top, H):
        for x in range(x0, x1 + 1):
            row = y // 6
            brick = (y % 6 == 0) or ((x + (row % 2) * 7) % 14 == 0)
            cv.put(x, y, BLOCK, (2.0 if brick else 2.9) + (hr(x // 4, y // 4) - 0.5) * 0.3 - (x / 200) - max(0, (y - 200) / 60), lit=0)
    cv.rect(x0, top - 3, x1 + 2, top, BLOCK, 3.2, lit=0)                  # l'ampit del terrat
    # les altres finestres, apagades o amb la tele
    for (wx, wy) in ((14, 112), (96, 112), (96, 200), (14, 200)):
        cv.rect(wx, wy, wx + 22, wy + 26, [(4, 4, 8), (10, 10, 18)], 0.6, lit=0)
        outline(cv, wx - 1, wy - 1, wx + 23, wy + 27, BLOCK)
    cv.rect(97, 201, 117, 225, [(20, 30, 70), (40, 60, 130)], 0.6, lit=0)  # algú mira la tele
    # la finestra del pis: verd de pantalla, i l'Iri retallada a contrallum
    wx0, wy0, wx1, wy1 = 40, 140, 88, 182
    for y in range(wy0, wy1 + 1):
        for x in range(wx0, wx1 + 1):
            cv.put(x, y, TEAL, 2.6 + (1.2 * max(0, 1 - math.hypot(x - 70, y - 160) / 22)), lit=0)
    cv.rect(64, 150, 80, 162, TEAL, 6.0, lit=0)                           # el monitor
    cv.rect(66, 152, 78, 160, TEAL, 4.4, lit=0)
    cv.rect(70, 162, 74, 166, [(4, 10, 12)], 0, lit=0)
    sil = [(4, 10, 12)]
    cv.disc(56, 156, 5, 6, sil, 0, lit=0)                                 # el cap, amb la cua
    cv.line(51, 156, 47, 166, sil, 0, lit=0)
    cv.line(52, 157, 48, 167, sil, 0, lit=0)
    cv.rect(49, 162, 63, wy1, sil, 0, lit=0)                              # les espatlles i la cadira
    cv.disc(61, 154, 1.6, 2.4, [(200, 30, 40)], 0, lit=0)                 # l'auricular vermell
    cv.rect(wx0, 171, wx1, 172, [(4, 10, 12)], 0, lit=0)                  # la taula
    outline(cv, wx0 - 1, wy0 - 1, wx1 + 1, wy1 + 1, BLOCK)
    cv.rect(wx0 - 3, wy1 + 1, wx1 + 3, wy1 + 3, BLOCK, 3.4, lit=0)
    cv.glow(64, 160, 60, (60, 230, 190), 0.16)
    # els cables: surten per la finestra i pugen per la façana fins a la parabòlica
    for k, col in enumerate(([(20, 20, 26), (60, 60, 70)], [(60, 10, 14), (150, 30, 30)], [(10, 30, 50), (30, 80, 120)])):
        cable(cv, [(wx1 + 1, wy0 + 8 + k * 3), (wx1 + 30, wy0 + 20), (118 + k * 2, 130), (DISH[0] - 2 + k * 2, DISH[1] + 8)], col, 1.0)
    # la parabòlica, que apunta a la torre
    dx, dy = DISH
    cv.rect(dx - 1, dy + 2, dx + 1, top, ROOF, 2.6, lit=0)
    cv.disc(dx + 3, dy - 2, 8, 6, [(40, 44, 54), (90, 96, 110), (150, 156, 170), (200, 206, 214)], lambda nx, ny: 2.4 + nx - ny * 0.6, lit=0)
    cv.line(dx + 3, dy - 2, dx + 12, dy - 6, [(200, 206, 214)], 0, lit=0)
    cv.flat(dx + 12, dy - 6, (250, 60, 60))


def bar_sign(cv, on=True):
    """A baix a la dreta, el neó de La Propina en un local baix (ara sí, del dret)."""
    obox(cv, 340, 214, 478, H - 1, ROOF, 1.4, lit=0)
    w = text_width('LA PROPINA')
    col = (255, 120, 200) if on else (110, 40, 90)
    text(cv, 'LA PROPINA', 409 - w // 2, 224, NEON, 0, lit=0, flat=col)
    if on:
        cv.glow(409, 226, 30, (255, 90, 200), 0.35)
    cv.rect(352, 236, 372, H - 1, [(30, 14, 30), (60, 26, 50)], 1.0, lit=0)   # l'aparador
    cv.rect(446, 236, 466, H - 1, [(30, 14, 30), (60, 26, 50)], 1.0, lit=0)


def title(cv):
    """«SUMA ZERO»: lletres de 5×7 a escala 5, cos verd blavós amb degradat, vora fosca i ombra magenta."""
    s = 5
    word = 'SUMA ZERO'
    width = len(word) * 6 * s - s
    x0 = (W - width) // 2
    for pas in ('ombra', 'vora', 'cos'):
        for i, ch in enumerate(word):
            for r, bits in enumerate(LLETRES[ch]):
                for c, bit in enumerate(bits):
                    if bit != '1':
                        continue
                    x = x0 + (i * 6 + c) * s
                    y = TITLE_Y + r * s
                    if pas == 'ombra':
                        cv.rect(x + 3, y + 3, x + s + 2, y + s + 2, [(70, 10, 60), (130, 24, 100)], 1, lit=0)
                    elif pas == 'vora':
                        cv.rect(x - 1, y - 1, x + s, y + s, [(6, 10, 22)], 0, lit=0)
                    else:
                        cv.rect(x, y, x + s - 1, y + s - 1, TEAL,
                                lambda px, py: 5.6 - (py - TITLE_Y) / 9 + (0.8 if py == y else 0) - (0.6 if py == y + s - 1 else 0), lit=0)
    cv.glow(W // 2, TITLE_Y + 16, 150, (60, 220, 190), 0.06)


def signal(cv, frame):
    """El pols de llum que va de la parabòlica a la torre."""
    ax, ay = DISH[0] + 12, DISH[1] - 6
    bx, by = TOWER_TOP[0] + 14, TOWER_TOP[1] - 12
    n = 10
    t = frame / n
    px = ax + (bx - ax) * t
    py = ay + (by - ay) * t - math.sin(t * math.pi) * 30
    cv.glow(px, py, 6, (120, 255, 220), 0.7)
    cv.flat(px, py, (220, 255, 240))


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
    for i in range(12):
        cv = Canvas(light=LIGHT, img=base.img.copy())
        if i < 10:
            signal(cv, i)
        if i == 7:
            bar_sign(cv, on=False)
        if i % 4 == 0:
            cv.flat(DISH[0] + 12, DISH[1] - 6, (90, 20, 20))
        frames.append(_diff(cv.img, base.img))
    return frames


ANIMS = {'senyal': {'frames': _frames, 'frameDuration': 140}}
