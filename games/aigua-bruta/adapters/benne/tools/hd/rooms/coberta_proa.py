"""
La coberta de proa de l'Arenga. Mirem a estribord, com a popa: la popa és a l'esquerra, la proa a la dreta.
  - a l'esquerra, sota la coberta de botes, el pas lateral cap a popa i la porta estanca del passadís;
  - al mig, el molinet de l'àncora, amb la cadena que va cap a l'escobén de proa i, a terra, l'escotilla
    de la caixa de cadenes (decorat `cadenat`: un cadenat nou);
  - a la dreta, el contenidor blanc de la balsa salvavides damunt el seu bressol (a sota, el racó de la
    Juana), el pal de proa amb la campana, i la borda que s'enfila cap a la proa;
  - de nit per defecte; de dia (decorat `dia`, Escenes 2 i 3), amb el racó de la Juana sota la balsa: una caixa
    per seure-hi (hi seu, animació asseguda) amb la manta.
"""
import math

from hd.pix import Light, W, hr, mix
from hd.pix import GOLD
from hd.rooms.arenga import YELL, REDP
from hd.rooms.exterior import (night_sky, night_sea, day_sky, day_sea, deck_floor, bulwark, wt_door, deck_lamp,
                               lifebuoy, coil, bitts, smooth, fbm, HULLN, STEELX, CABX, DECKX, ORANGEB, ROPE,
                               LAMP, WINDOW, GLOW_WARM, REDH)

HOR = 86
RAIL = 106
FLOOR_Y = 152
HOUSE = (30, 112)                 # la caseta (porta del passadís)
DOOR = (46, 72, 88, 152)
HATCH = (222, 162, 282, 186)      # l'escotilla, a terra
BALSA = (316, 70, 402, 106)       # el contenidor de la balsa

LIGHT = Light(ambient=-0.1, vignette=(50, 24), floor_fade=(198, 30))
LIGHT.point(67, 60, r=170, k=2.8, squash=1.1, down=True, power=1.4)       # focus sobre la porta
LIGHT.point(428, 46, r=210, k=2.6, squash=0.9, down=True, power=1.4)      # focus del pal de proa
LIGHT.point(14, 30, r=46, k=1.0, power=1.8)                                # llum del pas lateral
LIGHT.point(240, 200, r=260, k=0.6, squash=2.5, power=1.2)

LIGHT_DAY = Light(ambient=3.4, vignette=(40, 18), floor_fade=(200, 40))
LIGHT_DAY.point(60, -40, r=420, k=1.3, power=1.2)
LIGHT_DAY.add(lambda x, y: -1.6 if (x < HOUSE[0] - 2 and 22 <= y < 160) else 0.0)
LIGHT_DAY.add(lambda x, y: -1.2 if (322 <= x <= 398 and 108 <= y < 160) else 0.0)   # ombra sota la balsa


def bow_rail(x):
    """La regala s'enfila cap a la proa (dreta)."""
    return RAIL - int(30 * smooth(0.0, 1.0, (x - 400) / 80) ** 1.6) if x > 400 else RAIL


# ─── Cel, mar i borda ──────────────────────────────────────────────────────

def sky_sea(cv, day):
    if day:
        day_sky(cv, 0, HOR, seed=14, sun=(30, 20))
        day_sea(cv, HOR, RAIL + 4, sun_x=50, seed=5)
    else:
        night_sky(cv, 0, HOR, moon=(196, 30), seed=6, clouds=0.55)
        night_sea(cv, HOR, RAIL + 4, moon_x=196, seed=5)


def bow(cv, day):
    """La borda de proa, que s'aixeca: planxa blanca, regala vermella i, a la punta, l'asta."""
    for x in range(400, W):
        top = bow_rail(x)
        for y in range(top + 5, RAIL + 5):
            cv.put(x, y, HULLN, 2.8 + (hr(x // 4, y // 6, 5) - 0.5) * 0.25)
        for y in range(top, top + 5):
            cv.put(x, y, REDH, 3.4 + (1.4 if y == top else 0.6 if y == top + 1 else -0.8 if y == top + 4 else 0))
        cv.put(x, top + 5, HULLN, 1.2)
    # l'asta de proa
    for y in range(40, bow_rail(470)):
        cv.put(470, y, STEELX, 4.2)
        cv.put(471, y, STEELX, 2.6)
    cv.rect(468, 38, 473, 40, STEELX, 4.0)


def windlass(cv):
    """El molinet, vist de cantó: la bancada, la caixa d'engranatges verda, el barbotí (roda dentada) amb la
    cadena que hi passa per sobre, el tambor de maniobra i el volant del fre."""
    GR = [(6, 20, 14), (10, 34, 24), (16, 52, 36), (26, 74, 50), (40, 98, 66), (60, 126, 86), (90, 150, 110)]
    # bancada
    cv.rect(142, 152, 212, 160, STEELX, 2.2)
    cv.hline(142, 212, 152, STEELX, 3.8)
    for bx in range(145, 212, 7):
        cv.put(bx, 156, STEELX, 4.4)
    # la caixa d'engranatges (darrere), cantons rodons
    for y in range(118, 153):
        for x in range(150, 206):
            dx = max(158 - x, 0, x - 198)
            dy = max(126 - y, 0)
            if dx * dx + dy * dy <= 64:
                cv.put(x, y, GR, 2.8 - (y - 118) * 0.03 - (0.8 if x > 202 else 0) + (0.7 if y < 121 else 0))
    for yy in range(132, 150, 4):
        cv.hline(186, 200, yy, GR, 1.2)
    # el tambor de maniobra (a l'esquerra): cilindre amb vores
    for y in range(128, 150):
        for x in range(140, 152):
            u = (y - 139) / 11
            cv.put(x, y, STEELX, 3.6 - u * 1.6 - u * u)
    cv.rect(138, 126, 140, 151, STEELX, 4.4)
    cv.rect(152, 126, 154, 151, STEELX, 2.6)
    # el barbotí: roda amb dents, de cara
    cx, cy, r = 176, 134, 13
    for y in range(cy - r - 2, cy + r + 3):
        for x in range(cx - r - 2, cx + r + 3):
            d = math.hypot(x - cx, y - cy)
            a = math.atan2(y - cy, x - cx)
            tooth = r + (2 if math.cos(a * 7) > 0.4 else 0)
            if d <= tooth:
                lvl = 3.2 - (y - cy) / r * 0.9 - (x - cx) / r * 0.6
                if d < 4:
                    lvl = 4.6 if d < 2 else 1.6
                elif abs(d - 8) < 1:
                    lvl -= 1.2
                cv.put(x, y, STEELX, lvl)
    for k in range(5):                                           # radis
        a = k * 2 * math.pi / 5 + 0.3
        for t in range(4, 9):
            cv.put(cx + round(math.cos(a) * t), cy + round(math.sin(a) * t), STEELX, 1.4)
    # la cadena per damunt de la roda
    for a in range(200, 345, 9):
        x = cx + math.cos(math.radians(a)) * (r + 2)
        y = cy + math.sin(math.radians(a)) * (r + 2)
        cv.rect(x - 1, y - 1, x + 1, y, CHAIN, 3.2 + (0.8 if a % 18 else -0.4))
    # el fre: volant vermell de cara, damunt
    cv.rect(195, 110, 197, 124, STEELX, 3.0)
    for a in range(0, 360, 10):
        cv.put(196 + round(math.cos(math.radians(a)) * 6), 108 + round(math.sin(math.radians(a)) * 6), REDH, 5.4)
    for a in (0, 90, 180, 270):
        for t in range(1, 6):
            cv.put(196 + round(math.cos(math.radians(a)) * t), 108 + round(math.sin(math.radians(a)) * t), REDH, 4.2)


CHAIN = [(20, 16, 14), (40, 30, 24), (64, 48, 34), (92, 70, 48), (122, 96, 68), (150, 126, 96)]


def chain_run(cv):
    """La cadena: del barbotí cap a l'escobén de proa (dreta), estirada per la coberta."""
    x, y = 190, 124
    ex, ey = 458, 160
    n = ex - x
    for i in range(n):
        t = i / n
        cx = x + i
        cy = y + (ey - y) * min(1.0, t * 5) ** 0.6 if t < 0.2 else ey - 4 + 4 * t + math.sin(t * math.pi) * 2
        if i % 6 < 3:
            cv.rect(cx, cy - 1, cx + 2, cy + 1, CHAIN, 3.0)
            cv.put(cx + 1, cy, CHAIN, 0.6)
            cv.hline(cx, cx + 2, cy - 1, CHAIN, 4.4)
        else:
            cv.hline(cx, cx + 2, cy, CHAIN, 2.6)
    # l'escobén: una boca de ferro a la coberta, on la cadena desapareix
    cv.disc(462, 161, 8, 3, STEELX, lambda nx, ny: 3.6 - ny * 1.2)
    cv.disc(462, 161, 5, 2, STEELX, 0.6)
    # el tub que baixa del molinet a la caixa de cadenes (cap a l'escotilla)
    cv.disc(206, 158, 5, 2, STEELX, lambda nx, ny: 3.6 - ny)
    cv.disc(206, 158, 3, 1, STEELX, 0.4)


def hatch(cv):
    """L'escotilla de la caixa de cadenes, a terra en perspectiva, amb frontisses i la balda."""
    x0, y0, x1, y1 = HATCH
    # brocal (marc alçat)
    cv.poly([(x0 + 4, y0), (x1 - 4, y0), (x1, y1), (x0, y1)], STEELX, lambda x, y: 1.6)
    cv.poly([(x0 + 7, y0 + 2), (x1 - 7, y0 + 2), (x1 - 3, y1 - 3), (x0 + 3, y1 - 3)], STEELX,
            lambda x, y: 3.0 - (y - y0) * 0.02 + (hr(x // 3, y // 2, 81) - 0.5) * 0.3)
    # antilliscant en rombes
    for y in range(y0 + 4, y1 - 4, 3):
        for x in range(x0 + 8, x1 - 6, 6):
            off = 3 if (y // 3) % 2 else 0
            cv.put(x + off, y, STEELX, 4.0)
    cv.line(x0 + 4, y0, x1 - 4, y0, STEELX, 4.6)
    cv.line(x0, y1, x1, y1, STEELX, 0.8)
    cv.line(x0, y1 - 1, x1, y1 - 1, STEELX, 1.6)
    # frontisses al costat de dalt
    for hx in (x0 + 14, x1 - 20):
        cv.rect(hx, y0 - 1, hx + 6, y0 + 2, STEELX, 4.2)
        cv.put(hx + 3, y0, STEELX, 1.0)
    # la balda (on va el cadenat), al davant
    cv.rect(250, y1 - 6, 258, y1 - 2, STEELX, 4.4)
    cv.rect(252, y1 - 5, 256, y1 - 3, STEELX, 1.2)
    cv.rect(253, y1 - 2, 255, y1 + 1, STEELX, 3.8)
    # la nansa
    cv.hline(234, 242, y1 - 5, STEELX, 4.6)
    cv.put(233, y1 - 4, STEELX, 3.6)
    cv.put(243, y1 - 4, STEELX, 3.6)


def balsa(cv, day):
    """La balsa salvavides: contenidor blanc de dues meitats, amb cintes, damunt un bressol inclinat."""
    x0, y0, x1, y1 = BALSA
    cy = (y0 + y1) / 2
    r = (y1 - y0) / 2
    # el bressol: dos peus fins a la coberta i una rampa
    for lx in (330, 388):
        for y in range(y1 - 2, FLOOR_Y + 2):
            cv.put(lx, y, STEELX, 4.0)
            cv.put(lx + 1, y, STEELX, 3.0)
            cv.put(lx + 2, y, STEELX, 1.8)
        cv.rect(lx - 3, FLOOR_Y, lx + 5, FLOOR_Y + 2, STEELX, 2.6)
    cv.line(331, 130, 389, 116, STEELX, 2.6)                    # travesser en diagonal
    cv.rect(322, y1 - 2, 398, y1 + 1, STEELX, 3.0)
    cv.hline(322, 398, y1 - 2, STEELX, 4.6)
    # el cilindre
    for y in range(y0, y1 + 1):
        u = (y - cy) / (r + 0.5)
        for x in range(x0, x1 + 1):
            e = min(x - x0, x1 - x) / 6
            if e < 1 and (1 - e) ** 2 + u * u > 1:
                continue
            lvl = 4.4 - u * 1.8 - u * u * 1.4 - (0.6 if x > x1 - 4 else 0) + (0.5 if x < x0 + 3 else 0)
            cv.put(x, y, HULLN, lvl)
    # la junta del mig i les cintes
    for y in range(y0 + 1, y1):
        cv.put((x0 + x1) // 2, y, HULLN, 2.2)
        cv.put((x0 + x1) // 2 + 1, y, HULLN, 5.6)
    for bx in (334, 382):
        for y in range(y0 - 1, y1 + 2):
            u = (y - cy) / (r + 0.5)
            cv.put(bx, y, [(14, 24, 50), (24, 40, 80), (40, 64, 120), (64, 96, 160)], 2.2 - u * 1.2)
            cv.put(bx + 1, y, [(14, 24, 50), (24, 40, 80), (40, 64, 120), (64, 96, 160)], 1.8 - u * 1.2)
    # l'alliberador hidrostàtic i el cap de disparament
    cv.rect(356, y1 + 2, 362, y1 + 8, ORANGEB, 3.0)
    cv.line(359, y1 + 9, 352, 140, ROPE, 3.2)
    cv.line(352, 140, 346, 150, ROPE, 3.0)
    # una etiqueta vermella
    cv.rect(368, 80, 376, 86, REDH, 4.0)
    cv.hline(369, 375, 83, HULLN, 6.0)


def mast(cv, day):
    """El pal de proa: tub blanc, el focus de coberta, el llum de tope i la campana de llautó."""
    mx = 428
    for y in range(0, FLOOR_Y + 3):
        for x in range(mx - 3, mx + 4):
            u = (x - mx) / 3.5
            cv.put(x, y, HULLN, 4.0 - u * 1.6 - u * u)
    cv.rect(mx - 6, FLOOR_Y - 1, mx + 6, FLOOR_Y + 3, STEELX, 2.4)
    for y in (64, 110):
        cv.rect(mx - 4, y, mx + 4, y + 2, HULLN, 2.4)
    # la creueta i el focus
    cv.rect(mx - 14, 34, mx + 14, 36, HULLN, 3.4)
    cv.hline(mx - 14, mx + 14, 34, HULLN, 5.0)
    deck_lamp(cv, mx + 6, 44, on=not day)
    # el llum de tope (de nit, encès)
    cv.rect(mx - 2, 4, mx + 2, 9, CABX, 3.0)
    if not day:
        cv.glow(mx, 7, 10, (255, 250, 230), 0.7)
        cv.flat(mx, 7, (255, 252, 240))
    # la campana
    cv.rect(mx + 4, 78, mx + 12, 79, STEELX, 3.0)
    for y in range(80, 92):
        w = 2 + (y - 80) * 4 // 11
        for x in range(mx + 8 - w, mx + 9 + w):
            u = (x - (mx + 8)) / (w + 0.5)
            cv.put(x, y, GOLD, 3.6 - u * 1.6 - u * u)
    cv.hline(mx + 1, mx + 15, 92, GOLD, 2.6)
    cv.vline(mx + 8, 92, 98, ROPE, 3.0)
    cv.put(mx + 8, 99, ROPE, 2.0)


# ─── La caseta i el pas lateral (a l'esquerra) ─────────────────────────────

def house(cv, day):
    x0, x1 = HOUSE
    for y in range(22, FLOOR_Y):
        for x in range(x0, x1 + 1):
            lvl = 3.0 + (hr(x // 3, y // 5, 71) - 0.5) * 0.25 - (0.7 if y > FLOOR_Y - 10 else 0)
            if x >= x1 - 1:
                lvl -= 1.2
            cv.put(x, y, HULLN, lvl)
    for sy in (48, 112):
        cv.hline(x0, x1 - 2, sy, HULLN, 1.8)
        cv.hline(x0, x1 - 2, sy + 1, HULLN, 4.2)
    for bx in range(x0 + 4, x1 - 2, 12):
        cv.put(bx, 50, HULLN, 4.8)
        cv.put(bx, 114, HULLN, 4.8)
    cv.hline(x0, x1, FLOOR_Y - 10, HULLN, 1.4)
    cv.vline(x0, 22, FLOOR_Y - 1, HULLN, 4.6)
    cv.vline(x0 - 1, 22, FLOOR_Y - 1, HULLN, 1.4)
    for i in range(8):
        rx = x0 + 4 + int(hr(i, 72) * (x1 - x0 - 8))
        if DOOR[0] - 4 <= rx <= DOOR[2] + 4:
            continue
        for y in range(50, 50 + 4 + int(hr(i, 73) * 14)):
            cv.flat(rx, y, mix(cv.get(rx, y), (120, 70, 40), 0.3))
    wt_door(cv, DOOR[0], DOOR[1], DOOR[2], DOOR[3], base=3.4, warm=True)
    cv.rect(54, 62, 80, 67, HULLN, 1.6)
    for x in range(56, 79, 3):
        cv.put(x, 64, HULLN, 5.4)
        cv.put(x + 1, 64, HULLN, 5.4)
    deck_lamp(cv, 67, 56, on=not day)
    # ull de bou i un extintor
    cv.disc(100, 40, 6, 6, CABX, lambda nx, ny: 3.8 - nx - ny)
    if day:
        cv.disc(100, 40, 4, 4, STEELX, lambda nx, ny: 3.4 - ny + (1.6 if nx < -0.2 and ny < -0.2 else 0))
    else:
        cv.disc(100, 40, 4, 4, WINDOW, lambda nx, ny: 2.2 - ny * 0.6, lit=0)
        cv.glow(100, 40, 12, GLOW_WARM, 0.2)
    for y in range(110, 134):
        for x in range(96, 104):
            u = (x - 99.5) / 4
            cv.put(x, y, REDH, 4.0 - u * 1.4 - u * u)
    cv.rect(97, 106, 102, 109, STEELX, 3.6)
    cv.rect(96, 120, 103, 124, HULLN, 5.0)
    cv.line(103, 108, 106, 116, STEELX, 2.0)


def boat_deck(cv, day):
    x1 = HOUSE[1] + 6
    cv.rect(0, 14, x1, 22, HULLN, lambda x, y: 3.6 - (y - 14) * 0.25)
    cv.hline(0, x1, 14, HULLN, 5.0)
    cv.hline(0, x1, 22, HULLN, 1.0)
    cv.rect(0, 18, x1, 19, REDP, 2.6)
    for sx in range(4, x1, 14):
        cv.vline(sx, 0, 13, HULLN, 4.4)
        cv.vline(sx + 1, 0, 13, HULLN, 2.6)
    for ry in (2, 8):
        cv.hline(0, x1, ry, HULLN, 4.6)
        cv.hline(0, x1, ry + 1, HULLN, 2.4)


def side_passage(cv, day):
    x1 = HOUSE[0] - 2
    for y in range(23, 30):
        for x in range(0, x1 + 1):
            cv.put(x, y, HULLN, 1.4 - (y - 23) * 0.05)
    for y in range(22, FLOOR_Y + 2):
        cv.put(4, y, HULLN, 1.4)
        cv.put(5, y, HULLN, 2.8)
        cv.put(6, y, HULLN, 4.0)
    deck_lamp(cv, 16, 30, on=not day)
    cv.darken(0, 23, x1, FLOOR_Y + 30, lambda x, y: 0.8 if y < FLOOR_Y else 0.6 - (y - FLOOR_Y) / 50, dither=False)


def draw(cv, day):
    sky_sea(cv, day)
    bulwark(cv, 0, W - 1, RAIL, FLOOR_Y, base=2.6, scuppers=(130, 250))
    bow(cv, day)
    deck_floor(cv, FLOOR_Y, 206)
    hatch(cv)
    chain_run(cv)
    windlass(cv)
    bitts(cv, 276, FLOOR_Y + 2)
    balsa(cv, day)
    mast(cv, day)
    coil(cv, 128, 168, 12, 4)
    house(cv, day)
    boat_deck(cv, day)
    side_passage(cv, day)
    if not day:
        cv.glow(67, 172, 44, GLOW_WARM, 0.10)
        cv.glow(424, 168, 50, GLOW_WARM, 0.09)
    else:
        cv.darken(HOUSE[1], FLOOR_Y, HOUSE[1] + 26, FLOOR_Y + 8, lambda x, y: 0.5 if x < HOUSE[1] + 26 - (y - FLOOR_Y) * 3 else 0)


def manta(cv):
    """El racó de la Juana sota la balsa (de dia): una caixa de peix de fusta per seure, amb la manta de quadres
    doblegada al damunt i penjant pel davant, i un salvavides de coixí a terra."""
    BL = [(30, 14, 18), (60, 24, 30), (100, 38, 44), (140, 56, 56), (176, 84, 72)]
    WD = [(30, 20, 14), (54, 36, 22), (82, 56, 32), (110, 78, 44), (140, 102, 60), (170, 130, 82)]
    x0, x1, yt, yb = 358, 388, 135, 168
    cv.darken(x0 - 4, yb - 2, x1 + 6, yb + 3, 0.6)                   # l'ombra a la coberta
    # la caixa: posts horitzontals amb escletxes
    for i, py in enumerate(range(yt + 3, yb + 1, 7)):
        cv.rect(x0, py, x1, min(py + 5, yb), WD, lambda x, y: 2.4 - (y - py) * 0.15 - (x - x0) * 0.02)
        cv.hline(x0, x1, py, WD, 3.6)
        if py + 6 <= yb:
            cv.hline(x0 + 1, x1 - 1, py + 6, WD, 0.6)
    for x in (x0, x1 - 2):
        cv.rect(x, yt + 3, x + 2, yb, WD, 2.2)
    # la manta: doblegada damunt la caixa i penjant pel davant, amb la vora ondulada
    def bottom(x):
        return yt + 13 + round(math.sin(x * 0.5) * 1.5 + (2 if x0 + 8 < x < x1 - 6 else 0))
    for x in range(x0 - 2, x1 + 3):
        for y in range(yt - 2, bottom(x) + 1):
            top = y < yt + 2
            chk = (x // 4 + y // 3) % 2
            cv.put(x, y, BL, (3.4 if top else 2.6) + (0.9 if chk else 0) - (x - x0) * 0.02)
    for x in range(x0 + 2, x1, 7):                                   # plecs
        cv.line(x, yt + 3, x + 1, bottom(x + 1) - 1, BL, 1.0)
    cv.hline(x0 - 2, x1 + 2, yt - 2, BL, 4.4)
    # un salvavides de coixí, a terra al costat
    cv.rect(394, 159, 410, 166, ORANGEB, lambda x, y: 2.4 - (y - 159) * 0.12 - (x - 394) * 0.03)
    cv.hline(394, 410, 159, ORANGEB, 3.8)
    cv.hline(394, 410, 167, ORANGEB, 0.6)
    for x in (398, 406):                                             # les cintes
        cv.vline(x, 159, 166, [(120, 120, 116), (170, 170, 164), (210, 210, 200)], 1.2)


def bg(cv):
    draw(cv, False)


def dia(cv):
    keep = cv.light
    cv.light = LIGHT_DAY
    draw(cv, True)
    manta(cv)
    cv.light = keep


def cadenat(cv):
    """Un cadenat nou, de llautó lluent, a la balda de l'escotilla."""
    x, y = 254, HATCH[3] - 6
    for a in range(180, 361, 15):                                    # l'arc
        cv.put(x + round(math.cos(math.radians(a)) * 3), y - 1 + round(math.sin(math.radians(a)) * 3), STEELX, 5.4)
    cv.rect(x - 4, y, x + 4, y + 7, GOLD, lambda px, py: 4.2 - (px - x) * 0.2 - (py - y) * 0.1)
    cv.hline(x - 4, x + 4, y, GOLD, 5.6)
    cv.put(x, y + 4, GOLD, 0.6)
    cv.put(x, y + 5, GOLD, 0.6)
    cv.put(x - 3, y + 1, [(255, 250, 220)], 0, lit=0)


PROPS = {'dia': dia, 'cadenat': cadenat}

GEOMETRIA = {
    'things': {
        'popa': {'rect': (0, 24, 28, 168), 'walk': (12, 174)},
        'porta': {'rect': (44, 66, 90, 152), 'walk': (67, 168)},
        'balsa': {'rect': (312, 66, 406, 112), 'walk': (334, 172)},
        'molinet': {'rect': (144, 108, 210, 160), 'walk': (178, 174)},
        'escotilla': {'rect': (220, 160, 284, 188), 'walk': (252, 192)},
    },
    'spawns': {'iri': (296, 190), 'vet': (204, 192), 'juana': (372, 168)},
    'walkable': [(0, 166), (140, 162), (216, 162), (440, 160), (479, 166), (479, 196), (0, 196)],
}
