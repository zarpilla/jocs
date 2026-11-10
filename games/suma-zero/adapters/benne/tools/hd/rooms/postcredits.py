"""
L'escena de després dels crèdits: l'estudi de l'Iri (pis_estudi), de nit i amb els llums apagats. Cinemàtica.
Es dibuixa damunt de l'estudi de l'Escena 1:
  - tot més fosc i blavós: la llum de la lluna i del fanal entra per la persiana i fa franges a terra;
  - la cuina, apagada (el passaplats, fosc);
  - les pantalles, encara enceses: les dels costats, amb el salvapantalles; la del mig, un terminal negre amb
    una línia nova, «ROBIN HOOD 3.0?», i el cursor que fa pampallugues (ANIMS);
  - el router, amb el cable de xarxa rosegat (els fils de coure a l'aire) i el llum vermell que parpelleja;
  - a terra, al costat del router, un tros de pizza (en Diu no: els personatges no són al fons).
"""

from hd.pix import Light, Canvas, W, H, hr, mix
from hd.rooms.comu import cable, text, _diff
from hd.rooms.pis_estudi import bg as estudi_bg, stripes, DESKB, FLOOR_Y

MOON = (90, 130, 210)
TERM = [(2, 8, 8), (4, 14, 14), (8, 26, 24), (16, 50, 44), (40, 120, 100), (110, 220, 180), (210, 255, 236)]
DIMSCR = [(2, 6, 12), (4, 12, 22), (8, 22, 38), (14, 40, 64), (30, 80, 120), (90, 160, 210)]
CHEESE = [(70, 44, 10), (140, 100, 24), (210, 166, 50), (246, 214, 110), (255, 240, 180)]
SAUCE = [(50, 8, 6), (110, 20, 12), (170, 40, 22)]
CRUST = [(50, 26, 10), (100, 58, 22), (156, 100, 44), (200, 146, 76)]
NETB = [(4, 4, 8), (20, 40, 70), (50, 100, 170), (110, 170, 230)]

# Llums apagats: només les pantalles i, per la finestra, la lluna i el fanal.
LIGHT = Light(ambient=-1.2, vignette=(80, 50), floor_fade=(186, 22))
LIGHT.point(283, 88, r=120, k=2.6, squash=1.2, power=1.8)        # les pantalles
LIGHT.point(79, 72, r=90, k=1.2, squash=0.9, power=1.8)          # la finestra

MAIN = (254, 62, 312, 107)   # la pantalla del mig (interior)


def blinds_floor(x, y):
    """Les franges de la persiana que la lluna projecta a terra, cap a la dreta."""
    if y <= FLOOR_Y or y > 204:
        return 0.0
    d = y - FLOOR_Y
    u = x - 40 - d * 1.5
    if not 0 <= u < 70 + d * 0.8:
        return 0.0
    band = int((u / (1 + d / 50)) // 5) % 2 == 0
    return (0.22 if band else 0.06) * max(0.0, 1 - d / 55)


def night_grade(cv):
    """Tot cap al blau fosc, menys el que brilla (pantalles, leds, neó)."""
    for y in range(H):
        for x in range(W):
            r, g, b, a = cv.P[x, y]
            lum = max(r, g, b)
            if lum > 150:                       # el que fa llum no es toca
                continue
            k = 0.35 if lum < 60 else 0.25
            cv.P[x, y] = mix((r, g, b), (r * 0.6 + 6, g * 0.7 + 10, b * 0.9 + 26), k) + (a,)
    cv.tint(0, 0, W - 1, FLOOR_Y + 14, (50, 80, 160), lambda x, y: 0.22 * stripes(x, y))   # el neó, més blau
    cv.tint(0, FLOOR_Y + 1, W - 1, 204, (150, 180, 240), blinds_floor)
    cv.glow(79, 70, 60, MOON, 0.18)


def hatch_dark(cv):
    """El passaplats, amb la cuina apagada."""
    x0, y0, x1, y1 = 436, 58, 474, 100
    for y in range(y0 + 3, y1 - 2):
        for x in range(x0 + 3, x1 - 2):
            cv.put(x, y, DIMSCR, 0.6 + (0.4 if y > 80 else 0), lit=0)
    cv.rect(x0 + 3, 80, x1 - 3, 81, DIMSCR, 0.2, lit=0)
    cv.flat(466, 90, (60, 220, 120))                                # el led verd del forn
    for (a, b, c, d) in ((x0, y0, x1, y0 + 2), (x0, y1 - 2, x1, y1), (x0, y0, x0 + 2, y1), (x1 - 2, y0, x1, y1)):
        cv.rect(a, b, c, d, DESKB, 1.6)


def side_screens(cv):
    """Les pantalles dels costats, amb un salvapantalles: estrelles fosques."""
    for (x0, y0, x1, y1) in ((206, 74, 246, 110), (320, 74, 360, 110)):
        sx0, sy0, sx1, sy1 = x0 + 2, y0 + 2, x1 - 2, y1 - 3
        for y in range(sy0, sy1 + 1):
            for x in range(sx0, sx1 + 1):
                cv.put(x, y, DIMSCR, 1.6 + (0.2 if y % 2 else 0), lit=0)
        for i in range(10):
            cv.flat(sx0 + int(hr(i, x0) * (sx1 - sx0)), sy0 + int(hr(x0, i) * (sy1 - sy0)), (140, 190, 230) if i % 3 else (220, 240, 255))


def question(cv, x, y, col):
    """L'interrogant (la font petita no en té)."""
    for j, row in enumerate(['110', '001', '010', '000', '010']):
        for i, bit in enumerate(row):
            if bit == '1':
                cv.flat(x + i, y + j, col)


def terminal(cv, cursor=True):
    """La pantalla del mig: un terminal negre, la feina vella apagada i una línia nova."""
    sx0, sy0, sx1, sy1 = MAIN
    for y in range(sy0, sy1 + 1):
        for x in range(sx0, sx1 + 1):
            cv.put(x, y, TERM, 1.0 + (0.3 if y % 2 else 0), lit=0)
    dim = (30, 90, 76)
    # línies velles, gairebé esborrades
    for k, row in enumerate(range(sy0 + 2, sy0 + 22, 4)):
        n = 12 + int(hr(k, 7) * 30)
        cv.flat(sx0 + 2, row, dim)
        for x in range(sx0 + 5, min(sx1 - 2, sx0 + 5 + n)):
            if hr(x // 3, k) > 0.3:
                cv.flat(x, row, dim)
    # la línia nova
    col = (180, 255, 220)
    cv.flat(sx0 + 2, 88, col)                                       # l'indicador «>»
    cv.flat(sx0 + 3, 89, col)
    cv.flat(sx0 + 2, 90, col)
    w = text(cv, 'ROBIN HOOD 3.0', sx0 + 6, 86, TERM, 0, lit=0, flat=col)
    question(cv, sx0 + 6 + w + 1, 86, col)
    if cursor:
        cv.rect(sx0 + 3, 94, sx0 + 5, 98, TERM, 6, lit=0)
    cv.glow((sx0 + sx1) // 2, 90, 34, (80, 220, 170), 0.10)


def router_chewed(cv, led=True):
    """El router, amb el cable de xarxa rosegat a mig camí i el llum vermell d'error."""
    for x in (385, 391, 397):
        cv.flat(x + 1, 117, (40, 26, 20))
    cv.flat(398, 117, (255, 60, 50) if led else (70, 20, 20))
    if led:
        cv.glow(398, 117, 7, (255, 60, 50), 0.5)
    # el tros que encara surt del router, penjant, acabat en fils
    cable(cv, [(386, 124), (384, 136), (378, 148), (372, 152)], NETB, 3.0, thick=2)
    # l'altre tros, a terra, que va cap a la torre
    cable(cv, [(362, 167), (330, 176), (280, 172), (236, 158)], NETB, 2.6, thick=2)
    # els fils de coure i de colors, a l'aire
    wires = ((230, 150, 70), (90, 200, 90), (250, 160, 60), (110, 150, 240), (240, 240, 240))
    for (dx, dy), c in zip(((-5, 1), (-4, 4), (-2, 6), (-6, -2), (-1, 7)), wires):
        cv.line(371, 154, 371 + dx, 154 + dy, [c], 0, lit=0)
    for (dx, dy), c in zip(((4, -3), (5, 0), (3, 3), (6, -1)), wires):
        cv.line(363, 167, 363 + dx, 167 + dy, [c], 0, lit=0)
    # trossets de plàstic blau rosegat
    for i in range(5):
        cv.flat(362 + int(hr(i, 3) * 10), 158 + int(hr(i, 4) * 8), NETB[2])


def pizza_slice(cv):
    """Un tros de pizza a terra, mossegat, al costat del moble del router."""
    pts = [(418, 172), (440, 166), (436, 178)]
    cv.poly(pts, CHEESE, lambda x, y: 2.4 + (hr(x // 2, y // 2) - 0.5) * 0.8)
    cv.line(440, 166, 436, 178, CRUST, 2.8)
    cv.line(441, 166, 437, 178, CRUST, 2.2)
    for (px, py) in ((426, 171), (432, 170), (433, 175)):
        cv.disc(px, py, 1.4, 1.2, SAUCE, 2.0)
    cv.disc(419, 171, 2, 2, [(10, 10, 14)], 0)                       # la mossegada
    cv.darken(418, 178, 440, 180, 0.5)


def bg(cv):
    estudi_bg(cv)
    hatch_dark(cv)
    night_grade(cv)
    side_screens(cv)
    terminal(cv)
    router_chewed(cv)
    pizza_slice(cv)


PROPS = {}


def _frames():
    base = Canvas(light=LIGHT)
    bg(base)
    frames = []
    for i in range(4):
        cv = Canvas(light=LIGHT, img=base.img.copy())
        terminal(cv, cursor=i % 2 == 0)
        router_chewed(cv, led=i in (0, 1, 3))
        frames.append(_diff(cv.img, base.img))
    return frames


ANIMS = {'cursor': {'frames': _frames, 'frameDuration': 500}}
