"""
El pròleg (cinemàtica): Ginebra de nit, la seu del Banc Central Mundial Unificat. Art definitiu:
  - el llac Léman, negre i quiet, amb el raig d'aigua il·luminat i les muntanyes retallades contra el cel;
  - la seu del BCMU: una torre de vidre damunt d'un sòcol de pedra, amb «BCMU» daurat a dalt i les finestres
    de qui encara treballa; tot s'emmiralla al llac;
  - a la façana, una pantalla gegant: el Director Bonfill grava l'anunci («Al BCMU construïm el futur de
    tothom»), i somriu massa (anima la boca).
"""
import math

from PIL import Image

from hd.pix import Light, Canvas, W, H, hr
from hd.rooms.comu import obox, outline, text, text_width, _diff
from hd.characters import person, M, SKIN_PALE, WHITE, GRAY_SHOE, SUIT_D
from hd.personatges import hair_cap
from hd.characters import HAIR_PLAT

HORIZON = 150

NIGHT = [(2, 2, 8), (4, 6, 16), (8, 10, 26), (14, 16, 40), (22, 22, 56), (34, 30, 72), (50, 40, 88), (70, 54, 104)]
MOUNT = [(4, 4, 10), (8, 8, 18), (14, 14, 28), (20, 20, 38)]
WATER = [(1, 2, 6), (3, 5, 12), (6, 9, 20), (10, 14, 30), (16, 20, 40), (24, 28, 52)]
STONE = [(14, 12, 14), (26, 24, 26), (42, 38, 40), (60, 56, 56), (82, 76, 74), (106, 100, 96), (132, 126, 120)]
GLASSB = [(4, 8, 14), (8, 14, 24), (14, 22, 36), (22, 32, 50), (32, 44, 66), (46, 60, 84)]
WARM = [(60, 36, 10), (130, 84, 26), (210, 150, 60), (250, 210, 120), (255, 240, 190)]
GOLD = [(60, 40, 6), (130, 92, 16), (200, 150, 30), (240, 200, 70), (255, 236, 150)]
JET = [(30, 40, 60), (70, 90, 120), (130, 150, 180), (190, 206, 226), (240, 246, 255)]
TOWER = (190, 290)             # la torre: de x 190 a 290
BASE_Y = 120                   # el sòcol de pedra, de 120 a l'horitzó
SCREEN = (200, 50, 280, 112)   # la pantalla de la façana

LIGHT = Light(ambient=0.0)

BONFILL = {'skin': SKIN_PALE, 'legs': SUIT_D, 'top': SUIT_D, 'shoes': GRAY_SHOE, 'closed': True,
           'brow': (200, 200, 210), 'hooks': {'hair': hair_cap(HAIR_PLAT, fringe=0.4)}}


# ─── El cel, les muntanyes, el llac ────────────────────────────────────────

def sky(cv):
    for y in range(0, HORIZON):
        for x in range(W):
            cv.put(x, y, NIGHT, 1.0 + y / 30 + (hr(x // 3, y // 3) - 0.5) * 0.2, lit=0)
    for i in range(70):                                                  # estrelles
        x, y = int(hr(i, 1) * W), int(hr(i, 2) * 90)
        cv.flat(x, y, (200, 200, 230) if hr(i, 3) > 0.7 else (110, 110, 150))
    # la lluna, petita i a un costat
    cv.disc(408, 30, 6, 6, [(200, 200, 190), (236, 234, 220), (250, 250, 240)], lambda nx, ny: 1.4 - nx * 0.8, lit=0)
    cv.glow(408, 30, 22, (180, 190, 230), 0.25)


def mountains(cv):
    """El Salève i companyia, retallats contra el cel; neu a les crestes."""
    for x in range(W):
        h1 = 112 + 10 * math.sin(x / 47) + 6 * math.sin(x / 13 + 1) + 4 * hr(x // 6, 4)
        h2 = 126 + 6 * math.sin(x / 31 + 2) + 3 * hr(x // 4, 5)
        for y in range(int(h1), HORIZON):
            snow = y - h1 < 2 and math.sin(x / 47) > 0.4
            cv.put(x, y, MOUNT if not snow else [(60, 66, 90), (100, 106, 130)], 1.4 if not snow else 0.6, lit=0)
        for y in range(int(h2), HORIZON):
            cv.put(x, y, MOUNT, 0.6, lit=0)


def city(cv):
    """Edificis baixos al moll, amb finestres, i els fanals de la riba."""
    x = 0
    i = 0
    while x < W:
        w = 16 + int(hr(i, 7) * 22)
        h = 8 + int(hr(i, 8) * 16)
        if not (TOWER[0] - 10 < x < TOWER[1] + 4):
            for yy in range(HORIZON - h, HORIZON):
                for xx in range(x, min(W, x + w - 1)):
                    cv.put(xx, yy, MOUNT, 2.2, lit=0)
            for wy in range(HORIZON - h + 3, HORIZON - 2, 4):
                for wx in range(x + 2, x + w - 3, 4):
                    if hr(wx, wy, 2) > 0.62:
                        cv.flat(wx, wy, (240, 190, 110) if hr(wx, wy, 3) > 0.3 else (160, 200, 240))
        x += w
        i += 1
    for lx in range(6, W, 22):                                           # fanals de la riba
        cv.flat(lx, HORIZON - 1, (255, 220, 150))
        cv.glow(lx, HORIZON - 1, 4, (255, 210, 140), 0.4)


def lake(cv):
    for y in range(HORIZON, H):
        for x in range(W):
            ripple = math.sin(x / 9 + y * 1.3) * 0.3
            cv.put(x, y, WATER, 2.0 - (y - HORIZON) / 50 + ripple * 0.5, lit=0)


def reflections(cv, frame=0):
    """Els llums s'emmirallen al llac, trencats per les ones."""
    src = cv.img.copy()
    S = src.load()
    for y in range(HORIZON + 1, H):
        d = y - HORIZON
        sy = HORIZON - d
        if sy < 0:
            break
        for x in range(W):
            wob = round(math.sin(y * 0.7 + frame * 0.8) * min(3, d / 12))
            sx = max(0, min(W - 1, x + wob))
            r, g, b, _ = S[sx, sy]
            if r + g + b > 260 and (y + x // 3) % 2 == 0:
                o = cv.get(x, y)
                k = 0.45 * max(0, 1 - d / 110)
                cv.flat(x, y, (int(o[0] + (r - o[0]) * k), int(o[1] + (g - o[1]) * k), int(o[2] + (b - o[2]) * k)))


def jet(cv, frame=0):
    """El raig d'aigua, il·luminat, a l'esquerra."""
    bx = 70
    top = 62
    for y in range(top, HORIZON):
        t = (y - top) / (HORIZON - top)
        wdt = 1 + t * 5 + (2 if y < top + 10 else 0)
        for x in range(int(bx - wdt), int(bx + wdt) + 1):
            if hr(x, y + frame * 3, 4) > 0.25 + t * 0.3:
                cv.put(x, y, JET, 3.6 - abs(x - bx) / max(1, wdt) * 1.6 - t * 0.8, lit=0)
    # la ploma que cau, a la dreta (el vent)
    for k in range(60):
        a = hr(k, frame, 5)
        x = bx + 2 + int(a * 18)
        y = top + int(a * a * 40) + int(hr(k, 6, 7) * 6)
        cv.flat(x, y, JET[2] if hr(k, 8) > 0.5 else JET[3])
    cv.glow(bx, top + 30, 30, (190, 210, 240), 0.12)


# ─── La seu del BCMU ───────────────────────────────────────────────────────

def bcmu(cv):
    x0, x1 = TOWER
    top = 22
    # la torre de vidre, amb els forjats i les finestres de qui encara treballa
    for y in range(top, BASE_Y):
        for x in range(x0, x1 + 1):
            floor = (y - top) % 6 == 0
            mull = (x - x0) % 8 == 0
            sheen = max(0, 1 - abs((x - x0) - 18 - (y - top) * 0.3) / 10) * 1.4    # el reflex de la lluna
            edge = 1.6 if x - x0 < 3 else (-0.8 if x1 - x < 3 else 0)
            lvl = 2.4 + (y - top) / 160 + sheen + edge + (1.0 if floor else 0) + (0.5 if mull else 0)
            cv.put(x, y, GLASSB, lvl, lit=0)
    for fy in range(top + 2, BASE_Y - 3, 6):
        for fx in range(x0 + 2, x1 - 4, 8):
            if hr(fx, fy, 9) > 0.72:
                cv.rect(fx, fy, fx + 5, fy + 2, WARM, 2.0 + hr(fx, fy, 1), lit=0)
    # el coronament i les lletres daurades
    cv.rect(x0 - 2, top - 6, x1 + 2, top - 1, STONE, 3.2, lit=0)
    word = 'BCMU'
    big = 2
    w = (text_width(word) + 1) * big
    tx = (x0 + x1) // 2 - w // 2
    tmp = Canvas(w=60, h=10, transparent=True)
    text(tmp, word, 0, 0, GOLD, 4, lit=0)
    sm = tmp.img.resize((tmp.img.width * big, tmp.img.height * big), Image.NEAREST)
    cv.img.alpha_composite(sm, (tx, top - 18))
    cv.glow((x0 + x1) // 2, top - 13, 26, (255, 210, 110), 0.3)
    # el sòcol de pedra, amb l'entrada i les columnes
    cv.rect(x0 - 24, BASE_Y, x1 + 24, HORIZON - 1, STONE, lambda x, y: 2.6 + (0.8 if (x - x0) % 16 < 3 else 0) - (y - BASE_Y) * 0.02, lit=0)
    cv.rect(x0 - 26, BASE_Y - 2, x1 + 26, BASE_Y, STONE, 4.2, lit=0)
    cv.rect(226, 132, 254, HORIZON - 1, WARM, 1.8, lit=0)              # el vestíbul, encès
    for cx in (230, 240, 250):
        cv.rect(cx, 132, cx + 1, HORIZON - 1, STONE, 1.2, lit=0)
    cv.glow(240, 142, 20, (255, 210, 130), 0.25)
    # una bandera que no es mou (no fa vent per als bancs)
    cv.vline(x1 + 18, BASE_Y - 26, BASE_Y - 2, STONE, 3.4, lit=0)
    cv.rect(x1 + 19, BASE_Y - 26, x1 + 28, BASE_Y - 20, GOLD, 2.4, lit=0)


def screen(cv, talk=False):
    """La pantalla de la façana: el Director Bonfill, de cara, amb corbata i somriure d'anunci."""
    x0, y0, x1, y1 = SCREEN
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            cv.put(x, y, [(10, 20, 50), (20, 40, 90), (40, 70, 140), (80, 120, 190)], 1.0 + (y - y0) / 20, lit=0)
    fig = person(BONFILL, 'D', talk=talk)
    P = fig.load()
    # camisa blanca i corbata vermella al coll
    for y in range(29, 40):
        for x in range(22, 28):
            if P[x, y][3]:
                P[x, y] = (230, 230, 236, 255) if abs(x - 24.5) > 1 else ((180, 30, 40, 255) if y > 30 else (210, 50, 50, 255))
    # el somriure: massa dents
    mouth_y = 21 if not talk else 22
    for x in (23, 24, 25, 26):
        P[x, mouth_y] = (250, 250, 250, 255)
    bust = fig.crop((8, 3, 41, 36)).resize((66, 66), Image.NEAREST)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    lay.alpha_composite(bust, ((x0 + x1) // 2 - 33, y1 - 62))
    cv.img.alpha_composite(lay.crop((x0, y0, x1 + 1, y1 + 1)), (x0, y0))
    # les línies de la pantalla i el marc
    for y in range(y0, y1 + 1, 2):
        cv.tint(x0, y, x1, y, (0, 0, 0), 0.18)
    cv.rect(x0, y1 - 6, x1, y1, [(240, 200, 70)], 0, lit=0)
    text(cv, 'BCMU', x0 + 3, y1 - 5, [(30, 20, 4)], 0, lit=0, flat=(40, 28, 6))
    outline(cv, x0 - 1, y0 - 1, x1 + 1, y1 + 1, [(4, 6, 10)])
    cv.glow((x0 + x1) // 2, (y0 + y1) // 2, 50, (120, 160, 230), 0.12)


def bg(cv, frame=0):
    sky(cv)
    mountains(cv)
    city(cv)
    bcmu(cv)
    screen(cv, talk=frame % 2 == 1)
    lake(cv)
    jet(cv, frame)
    reflections(cv, frame)


PROPS = {}


def _frames():
    base = Canvas(light=LIGHT)
    bg(base)
    frames = []
    for i in range(6):
        cv = Canvas(light=LIGHT)
        bg(cv, i)
        frames.append(_diff(cv.img, base.img))
    return frames


ANIMS = {'nit': {'frames': _frames, 'frameDuration': 260}}
