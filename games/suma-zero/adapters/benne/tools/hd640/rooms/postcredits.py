"""
L'escena de després dels crèdits, a 640×360 (hd/rooms/postcredits.py ×4/3, dibuixada de nou): l'estudi de l'Iri
(hd640/rooms/pis_estudi), de nit i amb els llums apagats. Cinemàtica. Es dibuixa damunt de l'estudi de l'Escena 1:
  - tot més fosc i blavós: la llum de la lluna i del fanal entra per la persiana i fa franges a terra;
  - la cuina, apagada (el passaplats, fosc, amb el led del forn);
  - les pantalles, encara enceses: les dels costats, amb el salvapantalles d'estrelles; la del mig, un terminal
    negre amb una línia nova, «ROBIN HOOD 3.0?», i el cursor que fa pampallugues;
  - el router, amb el cable de xarxa rosegat (els fils de coure a l'aire) i el llum vermell que parpelleja;
  - a terra, al costat del router, un tros de pizza mossegat (en Diu no: els personatges no són al fons).
Animació: `cursor` (el cursor del terminal, el led vermell del router i les estrelles del salvapantalles).
"""

import hd640  # noqa: F401  (posa la llibreria de dibuix a 640×360)
from hd.pix import Light, Canvas, W, H, hr, mix
from hd.rooms.comu import cable, text, _diff
from hd.rooms.postcredits import MOON, TERM, DIMSCR, CHEESE, SAUCE, CRUST, NETB
from hd640.rooms.pis_estudi import _draw as estudi_bg, stripes, DESKB, FLOOR_Y, HATCH, PORTS

# Llums apagats: només les pantalles i, per la finestra, la lluna i el fanal.
LIGHT = Light(ambient=-1.2, vignette=(107, 67), floor_fade=(248, 29))
LIGHT.point(377, 117, r=160, k=2.6, squash=1.2, power=1.8)       # les pantalles
LIGHT.point(105, 96, r=120, k=1.2, squash=0.9, power=1.8)        # la finestra

MAIN = (339, 83, 416, 143)   # la pantalla del mig (interior)
SIDES = ((275, 99, 328, 147), (427, 99, 480, 147))


def blinds_floor(x, y):
    """Les franges de la persiana que la lluna projecta a terra, cap a la dreta."""
    if y <= FLOOR_Y or y > 272:
        return 0.0
    d = y - FLOOR_Y
    u = x - 53 - d * 1.5
    if not 0 <= u < 93 + d * 0.8:
        return 0.0
    band = int((u / (1 + d / 67)) // 7) % 2 == 0
    return (0.22 if band else 0.06) * max(0.0, 1 - d / 73)


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
    cv.tint(0, 0, W - 1, FLOOR_Y + 19, (50, 80, 160), lambda x, y: 0.22 * stripes(x, y))   # el neó, més blau
    cv.tint(0, FLOOR_Y + 1, W - 1, 272, (150, 180, 240), blinds_floor)
    cv.glow(105, 93, 80, MOON, 0.18)


def hatch_dark(cv):
    """El passaplats, amb la cuina apagada."""
    x0, y0, x1, y1 = HATCH
    for y in range(y0 + 3, y1 - 2):
        for x in range(x0 + 3, x1 - 2):
            cv.put(x, y, DIMSCR, 0.6 + (0.4 if y > 107 else 0) + (0.3 if (x - y) % 13 == 0 else 0), lit=0)
    cv.rect(x0 + 3, 106, x1 - 3, 108, DIMSCR, 0.2, lit=0)
    cv.flat(621, 120, (60, 220, 120))                               # el led verd del forn
    cv.flat(622, 120, (40, 160, 90))
    for (a, b, c, d) in ((x0, y0, x1, y0 + 2), (x0, y1 - 2, x1, y1), (x0, y0, x0 + 2, y1), (x1 - 2, y0, x1, y1)):
        cv.rect(a, b, c, d, DESKB, 1.6)


def side_screens(cv, t=0):
    """Les pantalles dels costats, amb un salvapantalles: estrelles fosques (algunes parpellegen amb t)."""
    for (x0, y0, x1, y1) in SIDES:
        sx0, sy0, sx1, sy1 = x0 + 3, y0 + 3, x1 - 3, y1 - 4
        for y in range(sy0, sy1 + 1):
            for x in range(sx0, sx1 + 1):
                cv.put(x, y, DIMSCR, 1.6 + (0.2 if y % 2 else 0), lit=0)
        for i in range(18):
            px, py = sx0 + 1 + int(hr(i, x0) * (sx1 - sx0 - 2)), sy0 + 1 + int(hr(x0, i) * (sy1 - sy0 - 2))
            if hr(i, x0, t) > 0.85:
                cv.flat(px, py, (60, 90, 130))
                continue
            col = (140, 190, 230) if i % 3 else (220, 240, 255)
            cv.flat(px, py, col)
            if i % 5 == 0:                                          # les grosses, en creu
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    cv.flat(px + dx, py + dy, (70, 110, 160))


def question(cv, x, y, col):
    """L'interrogant (la font petita no en té)."""
    for j, row in enumerate(['110', '001', '010', '000', '010']):
        for i, bit in enumerate(row):
            if bit == '1':
                cv.flat(x + i, y + j, col)


def prompt(cv, x, y, col):
    """L'indicador «>»."""
    cv.flat(x, y, col)
    cv.flat(x + 1, y + 1, col)
    cv.flat(x + 2, y + 2, col)
    cv.flat(x + 1, y + 3, col)
    cv.flat(x, y + 4, col)


def terminal(cv, cursor=True):
    """La pantalla del mig: un terminal negre, la feina vella apagada i una línia nova."""
    sx0, sy0, sx1, sy1 = MAIN
    for y in range(sy0, sy1 + 1):
        for x in range(sx0, sx1 + 1):
            cv.put(x, y, TERM, 1.0 + (0.3 if y % 2 else 0), lit=0)
    dim = (30, 90, 76)
    # línies velles, gairebé esborrades
    for k, row in enumerate(range(sy0 + 3, sy0 + 30, 5)):
        n = 16 + int(hr(k, 7) * 40)
        cv.flat(sx0 + 3, row, dim)
        for x in range(sx0 + 7, min(sx1 - 3, sx0 + 7 + n)):
            if hr(x // 4, k) > 0.3 and (x + 1) % 4:
                cv.flat(x, row, dim)
    # la línia nova
    col = (180, 255, 220)
    prompt(cv, sx0 + 3, 115, col)
    w = text(cv, 'ROBIN HOOD 3.0', sx0 + 9, 115, TERM, 0, lit=0, flat=col)
    question(cv, sx0 + 9 + w + 1, 115, col)
    prompt(cv, sx0 + 3, 125, (90, 170, 140))
    if cursor:
        cv.rect(sx0 + 9, 125, sx0 + 12, 130, TERM, 6, lit=0)
    cv.glow((sx0 + sx1) // 2, 120, 45, (80, 220, 170), 0.10)


def router_chewed(cv, led=True):
    """El router, amb el cable de xarxa rosegat a mig camí i el llum vermell d'error."""
    for x in PORTS[:2]:
        cv.flat(x + 1, 156, (40, 26, 20))
        cv.flat(x + 2, 156, (40, 26, 20))
    cv.flat(530, 156, (255, 60, 50) if led else (70, 20, 20))
    cv.flat(531, 156, (220, 40, 36) if led else (60, 16, 16))
    if led:
        cv.glow(530, 156, 9, (255, 60, 50), 0.5)
    # el tros que encara surt del router, penjant, acabat en fils
    cable(cv, [(515, 165), (512, 181), (504, 197), (496, 203)], NETB, 3.0, thick=2)
    cv.rect(513, 163, 517, 166, NETB, 2.6)
    # l'altre tros, a terra, que va cap a la torre
    cable(cv, [(483, 223), (440, 235), (373, 229), (315, 211)], NETB, 2.6, thick=2)
    # els fils de coure i de colors, a l'aire
    wires = ((230, 150, 70), (90, 200, 90), (250, 160, 60), (110, 150, 240), (240, 240, 240))
    for (dx, dy), c in zip(((-7, 1), (-5, 5), (-3, 8), (-8, -3), (-1, 9)), wires):
        cv.line(495, 205, 495 + dx, 205 + dy, [c], 0, lit=0)
    for (dx, dy), c in zip(((5, -4), (7, 0), (4, 4), (8, -1)), wires):
        cv.line(484, 223, 484 + dx, 223 + dy, [c], 0, lit=0)
    # trossets de plàstic blau rosegat
    for i in range(8):
        cv.flat(483 + int(hr(i, 3) * 13), 211 + int(hr(i, 4) * 11), NETB[2])


def pizza_slice(cv):
    """Un tros de pizza a terra, mossegat, al costat del moble del router."""
    pts = [(557, 229), (587, 221), (581, 237)]
    cv.poly(pts, CHEESE, lambda x, y: 2.4 + (hr(x // 2, y // 2) - 0.5) * 0.8)
    cv.line(587, 221, 581, 237, CRUST, 2.8)
    cv.line(588, 221, 582, 237, CRUST, 2.2)
    cv.line(589, 222, 583, 237, CRUST, 1.4)
    for (px, py) in ((568, 228), (576, 227), (577, 233)):
        cv.disc(px, py, 2, 1.6, SAUCE, 2.0)
        cv.flat(px - 1, py - 1, SAUCE[2])
    cv.flat(572, 231, (40, 30, 20))                                 # una oliva
    cv.flat(571, 226, (40, 30, 20))
    cv.disc(559, 228, 3, 3, [(10, 10, 14)], 0)                       # la mossegada
    cv.flat(592, 236, CRUST[2])                                     # una engruna
    cv.darken(557, 237, 588, 240, 0.5)


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
        side_screens(cv, t=i)
        terminal(cv, cursor=i % 2 == 0)
        router_chewed(cv, led=i in (0, 1, 3))
        frames.append(_diff(cv.img, base.img))
    return frames


ANIMS = {'cursor': {'frames': _frames, 'frameDuration': 500}}


GEOMETRIA = {
    'things': {},
    'spawns': {},
    'walkable': [(200, 253), (267, 253), (267, 261), (200, 261)],
}
