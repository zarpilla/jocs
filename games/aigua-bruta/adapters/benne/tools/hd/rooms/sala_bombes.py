"""
La sala de bombes: neta, pintada i callada. S'hi baixa per una escotilla del sostre i una escala de mà. A la dreta,
les bombes (contraincendis, vermella, i dues de llast, verdes) amb els motors a sobre; a l'esquerra, el
col·lector de vàlvules. Props: el llibre de la Juana, obert de cara avall a terra, i la seva llanterna encesa.
ANIMS (la sala és callada: les bombes no van): `manometres` (les agulles tremolen amb la vibració del vaixell)
i `gota` (una gota que cau de tant en tant del col·lector a un tollet de terra).
"""
import math

from hd.pix import Canvas, Light, W, H, hr, mix, B4, PAPER
from hd.rooms.arenga import (WALL, ENG, ENG_LIGHT, DECK, CAB, DARK, WHITEP, YELL, REDP, SEAG, BRASS, WARM,
                             FLOOR_Y, BOTTOM, box, rrect, bolt, hpipe, vpipe, glow)
from hd.rooms import sota

LAMPS = (110, 372)

LIGHT = Light(ambient=-0.4, vignette=(46, 26), floor_fade=None)
LIGHT.point(110, 26, r=150, k=2.3, squash=1.05, down=True, power=1.5)
LIGHT.point(372, 26, r=160, k=2.4, squash=1.05, down=True, power=1.5)
LIGHT.point(230, 6, r=70, k=1.0, power=1.8)                        # la llum del passadís, per l'escotilla

# terra pintat (verd grisós, net i brillant)
FLOORP = [(6, 10, 10), (10, 17, 16), (16, 26, 24), (24, 37, 34), (34, 50, 45), (46, 65, 58), (62, 84, 74),
          (82, 106, 94)]
BOOK = [(10, 20, 26), (16, 36, 46), (24, 56, 70), (36, 80, 96), (56, 110, 124), (90, 146, 156)]
TORCH = YELL


# ─── Paret, sostre i escotilla ─────────────────────────────────────────────

def walls(cv):
    sota.plate_wall(cv, 0, W - 1, lvl=3.5, frames=64, frame0=40, seams=(60, 112), rust=0, seed=31)
    # franja pintada a mitja alçada (les sales de bombes ben cuidades en tenen)
    cv.rect(0, 112, W - 1, 114, SEAG, 3.4)
    sota.ceiling(cv, beam0=40)


def hatch(cv):
    """L'escotilla del sostre, oberta, amb la llum del passadís, i l'escala de mà que baixa a terra."""
    x0, x1 = 206, 254
    # el forat
    cv.rect(x0, 0, x1, 21, WALL, lambda x, y: 4.2 - y * 0.05, lit=0.5)
    cv.rect(x0 + 4, 0, x1 - 4, 8, WALL, 5.2, lit=0.4)
    box(cv, x0 - 5, 16, x1 + 5, 23, ENG, 3.2)                          # la brazola
    for bx in range(x0 - 3, x1 + 4, 6):
        bolt(cv, bx, 19, ENG, 3.4)
    # la tapa, oberta (es veu de cantó, plegada contra el sostre)
    box(cv, x1 + 6, 4, x1 + 40, 10, ENG, 2.8)
    box(cv, x1 + 2, 10, x1 + 8, 16, CAB, 3.4)                          # frontissa
    # l'escala de mà
    sota.vladder(cv, 216, 244, 26, FLOOR_Y - 2, ramp=CAB, lvl=3.6, step=10)
    vpipe(cv, 216, 16, FLOOR_Y + 1, 1, CAB, 3.8)
    vpipe(cv, 244, 16, FLOOR_Y + 1, 1, CAB, 3.2)
    # agafamans al cantó del forat
    for hx in (212, 248):
        cv.line(hx, 22, hx, 32, BRASS, 3.6)


# ─── El col·lector de vàlvules (esquerra) ──────────────────────────────────

def handwheel(cv, cx, cy, r, ramp):
    cv.ring(cx, cy, r, ramp, 3.8, step=4)
    cv.ring(cx, cy, r - 1, ramp, 2.6, step=4)
    for a in range(0, 360, 60):
        cv.line(cx, cy, cx + round(math.cos(math.radians(a + 15)) * (r - 1)), cy + round(math.sin(math.radians(a + 15)) * (r - 1)), ramp, 3.2)
    cv.disc(cx, cy, 2, 2, CAB, 4.0)


def manifold(cv):
    # el tub del col·lector, horitzontal, i les baixants
    hpipe(cv, 20, 190, 92, 5, SEAG, 3.0, bands=range(36, 190, 40), band_ramp=WHITEP)
    for i, vx in enumerate((40, 80, 120, 160)):
        vpipe(cv, vx, 92, FLOOR_Y + 3, 3, SEAG, 2.8)
        # cos de vàlvula i volant (vermells els de contraincendis, verds els de llast)
        ramp = REDP if i == 0 else SEAG
        box(cv, vx - 6, 112, vx + 6, 124, ramp, 3.4)
        for bx in (vx - 5, vx + 4):
            bolt(cv, bx, 113, ramp, 3.8)
            bolt(cv, bx, 122, ramp, 3.8)
        vpipe(cv, vx, 104, 112, 1, CAB, 4.0)
        handwheel(cv, vx, 102, 8, ramp)
        # plaquetes amb el nom
        box(cv, vx - 8, 128, vx + 8, 133, WHITEP, 3.8)
        for x in range(vx - 6, vx + 7, 2):
            cv.put(x, 130, DARK, 1.4)
        # brides a terra
        box(cv, vx - 6, FLOOR_Y - 2, vx + 6, FLOOR_Y + 2, SEAG, 3.0)
    for x in (20, 190):
        cv.disc(x, 92, 5, 6, SEAG, lambda nx, ny: 3.4 - nx - ny)
    # manòmetres al tub
    for gx in (60, 140):
        vpipe(cv, gx, 78, 86, 1, CAB, 3.4)
        cv.disc(gx, 74, 6, 6, CAB, 2.0)
        cv.disc(gx, 74, 5, 5, WHITEP, 4.6)
        cv.line(gx, 74, gx - 2, 77, DARK, 0)
    # el rètol
    sota.sign(cv, 52, 46, 'LLAST', ramp=SEAG, lvl=3.4, ink=(230, 236, 228))
    sota.sign(cv, 18, 46, 'C.I.', ramp=REDP, lvl=3.6, ink=(240, 230, 220))


# ─── Les bombes (dreta) ─────────────────────────────────────────────────────

def pump(cv, cx, body, motor=ENG_LIGHT):
    """Una bomba centrífuga vertical: bancada, cos (voluta), acoblament i motor elèctric amb aletes."""
    base_y = FLOOR_Y + 2
    box(cv, cx - 24, base_y - 8, cx + 24, base_y, CAB, 2.8)
    for bx in (cx - 20, cx + 18):
        bolt(cv, bx, base_y - 5, CAB, 3.4)
    # voluta (cos de la bomba)
    cv.disc(cx, base_y - 20, 17, 12, body, lambda nx, ny: 3.6 - nx * 1.2 - ny * 1.1)
    cv.disc(cx, base_y - 20, 8, 6, body, lambda nx, ny: 2.8 + nx * 0.6 + ny * 0.6)
    for a in range(0, 360, 40):
        bolt(cv, cx + round(math.cos(math.radians(a)) * 13), base_y - 20 + round(math.sin(math.radians(a)) * 9), body, 4.0)
    # brides d'entrada i sortida
    hpipe(cv, cx - 30, cx - 15, base_y - 20, 4, body, 3.0)
    box(cv, cx - 16, base_y - 26, cx - 14, base_y - 14, body, 3.8)
    # llanterna (suport) i acoblament
    box(cv, cx - 9, base_y - 52, cx + 9, base_y - 32, CAB, 2.8)
    cv.rect(cx - 5, base_y - 48, cx + 5, base_y - 36, DARK, 1.0)
    vpipe(cv, cx, base_y - 50, base_y - 34, 2, CAB, 4.6)
    box(cv, cx - 4, base_y - 44, cx + 4, base_y - 40, YELL, 3.8)       # protecció de l'acoblament
    # motor (cilindre vertical, aletes) i la tapa del ventilador
    for y in range(base_y - 96, base_y - 52):
        for x in range(cx - 14, cx + 15):
            u = (x - cx) / 14.5
            fin = (x - cx) % 3 == 0
            cv.put(x, y, motor, 3.6 + 1.4 * (-0.3 - u) - 0.8 * u * u + (0.5 if fin else 0))
    box(cv, cx - 16, base_y - 56, cx + 16, base_y - 52, motor, 3.2)
    cv.disc(cx, base_y - 98, 13, 4, motor, lambda nx, ny: 3.8 - nx - ny)
    for x in range(cx - 10, cx + 11, 3):
        cv.put(x, base_y - 98, DARK, 1.4)
    box(cv, cx + 13, base_y - 84, cx + 21, base_y - 70, motor, 3.0)    # caixa de borns
    vpipe(cv, cx + 17, 24, base_y - 85, 1, CAB, 2.6)                   # el cable, cap a la safata
    box(cv, cx - 8, base_y - 78, cx + 6, base_y - 72, WHITEP, 3.8)     # placa de característiques
    # la sortida, cap amunt
    vpipe(cv, cx + 30, 44, base_y - 18, 4, body, 2.8, bands=(60,), band_ramp=WHITEP)
    hpipe(cv, cx + 14, cx + 30, base_y - 20, 4, body, 3.0)
    cv.disc(cx + 30, base_y - 20, 4, 4, body, lambda nx, ny: 3.4 - nx - ny)


def pumps(cv):
    hpipe(cv, 290, W - 1, 44, 4, SEAG, 3.0, bands=range(300, W, 50), band_ramp=WHITEP)
    pump(cv, 308, REDP)
    pump(cv, 376, SEAG)
    pump(cv, 438, SEAG)
    # rètols
    sota.sign(cv, 292, 58, 'C.I.', ramp=REDP, lvl=3.6, ink=(240, 230, 220))
    sota.sign(cv, 350, 58, 'LLAST 1', ramp=WHITEP, lvl=3.8)
    sota.sign(cv, 412, 58, 'LLAST 2', ramp=WHITEP, lvl=3.8)


def panel(cv):
    """L'armari d'arrencada de les bombes, entre l'escala i les bombes: tots els pilots apagats (no va res)."""
    x0, y0, x1, y1 = 260, 70, 284, 128
    box(cv, x0, y0, x1, y1, CAB, 3.4, grad=0.8)
    for i, y in enumerate((78, 92, 106)):
        cv.disc(x0 + 7, y, 2, 2, [(40, 10, 10), (80, 20, 20)] if i == 0 else [(10, 30, 14), (20, 60, 26)], 1.2)
        cv.disc(x0 + 17, y, 3, 3, CAB, 1.6)
        cv.rect(x0 + 16, y - 2, x0 + 18, y, CAB, 4.4)
    cv.rect(x0 + 4, 116, x1 - 4, 120, WHITEP, 3.4)
    box(cv, x1 - 3, 96, x1 - 1, 104, CAB, 4.2)


# ─── Terra pintat, net i brillant ──────────────────────────────────────────

def floor(cv):
    mask = [[False] * W for _ in range(H)]
    vp = (240, 40)
    for y in range(FLOOR_Y, BOTTOM + 12):
        d = y - vp[1]
        for x in range(W):
            u = vp[0] + (x - vp[0]) * 150 / d
            u2 = vp[0] + (x + 1 - vp[0]) * 150 / d
            lv = 3.0 + (hr(x // 4, y // 2, 7) - 0.5) * 0.25
            if int(u // 96) != int(u2 // 96):
                lv -= 1.0
            elif y in (164, 182):
                lv -= 0.9
            cv.put(x, y, FLOORP, lv)
            mask[y][x] = True
    # la línia groga de seguretat davant de les bombes
    for y in range(FLOOR_Y + 4, FLOOR_Y + 6):
        for x in range(282, W):
            if ((x // 6) % 2) == 0:
                cv.put(x, y, YELL, 3.4)
    return mask


def gloss(cv, mask, k=0.22):
    """Reflex suau de la paret al terra (pintura brillant)."""
    src = cv.img.copy().load()
    for y in range(FLOOR_Y + 1, BOTTOM + 12):
        f = k * max(0.0, 1 - (y - FLOOR_Y) / 30)
        for x in range(W):
            if not mask[y][x]:
                continue
            sy = 2 * FLOOR_Y - y
            if 0 <= sy < FLOOR_Y:
                cv.flat(x, y, mix(cv.get(x, y), src[x, sy][:3], f))
    for lx in LAMPS:
        for y in range(FLOOR_Y + 2, FLOOR_Y + 30):
            t = (y - FLOOR_Y) / 30
            wdt = 3 + t * 5
            for x in range(int(lx - wdt * 2), int(lx + wdt * 2) + 1):
                if 0 <= x < W and mask[y][x]:
                    g = math.exp(-((x - lx) / wdt) ** 2) * (1 - t)
                    if g * 0.6 > B4[y & 3][x & 3]:
                        cv.flat(x, y, mix(cv.get(x, y), WARM, 0.2))


# ─── Props ──────────────────────────────────────────────────────────────────

def book(cv):
    """El llibre de la Juana, obert de cara avall a terra (fa de teulada)."""
    sota.floor_shadow(cv, 168, 184, 20, 3, 0.8)
    # les dues tapes, en forma de teulada baixa
    cv.poly([(150, 184), (168, 174), (168, 182), (152, 187)], BOOK, lambda x, y: 3.6 - (y - 174) * 0.05)
    cv.poly([(168, 174), (186, 182), (184, 186), (168, 182)], BOOK, lambda x, y: 2.6 - (y - 174) * 0.04)
    cv.line(168, 174, 168, 182, BOOK, 1.2)                              # el llom
    cv.line(150, 184, 168, 174, BOOK, 4.6)
    cv.line(168, 174, 186, 182, BOOK, 3.4)
    # les fulles, que es veuen per sota
    cv.line(152, 187, 168, 183, PAPER, 4.4)
    cv.line(168, 183, 184, 187, PAPER, 3.6)
    cv.line(153, 186, 167, 182, PAPER, 3.0)
    # un peix al llom i un punt de llibre vermell que en surt
    cv.put(160, 179, WHITEP, 4.4)
    cv.put(161, 179, WHITEP, 4.0)
    cv.put(162, 178, WHITEP, 3.6)
    cv.line(176, 186, 179, 190, REDP, 3.8)


def torch_body(cv):
    """La llanterna groga, a terra, apuntant cap a les bombes."""
    sota.floor_shadow(cv, 225, 186, 18, 2, 0.8)
    for x in range(212, 232):
        for y in range(178, 186):
            u = (y - 182) / 4
            cv.put(x, y, TORCH, 3.8 - u * 1.3 - u * u, lit=0.4)
    box(cv, 232, 176, 237, 187, CAB, 3.6)
    cv.vline(238, 177, 186, [(120, 110, 80), (250, 240, 200), (255, 255, 240)], 2.2, lit=0)
    cv.rect(219, 180, 222, 181, DARK, 1.6, lit=0)
    cv.hline(212, 212, 182, CAB, 3.0)
    cv.line(208, 186, 212, 183, DARK, 2.0)                              # el cordó


def torch_beam(cv):
    """El feix de llum: un con a terra cap a la dreta, i una taca a la bancada de la bomba vermella."""
    for y in range(160, 196):
        for x in range(239, 344):
            t = (x - 239) / 105
            half = 3 + t * 26
            dy = abs(y - 182 + t * 6)
            if dy < half:
                k = 0.55 * (1 - t) ** 0.7 * (1 - (dy / half) ** 2)
                if k > B4[y & 3][x & 3] * 0.5:
                    cv.flat(x, y, mix(cv.get(x, y), (255, 238, 170), min(0.75, k + 0.1)))
    glow(cv, 238, 182, 10, (255, 250, 220), 0.9)
    glow(cv, 300, 150, 18, (255, 238, 170), 0.35)


_BASE = {}


def _base(cv):
    if 'img' not in _BASE:
        b = Canvas(light=LIGHT)
        bg(b)
        _BASE['img'] = b.img
    cv.img = _BASE['img'].copy()
    cv.P = cv.img.load()


def prop_llanterna(cv):
    from hd.rooms.comu import _diff
    var = Canvas(light=LIGHT)
    _base(var)
    base = var.img.copy()
    torch_beam(var)
    torch_body(var)
    cv.img.alpha_composite(_diff(var.img, base))


# ─── Muntatge ───────────────────────────────────────────────────────────────

def bg(cv):
    walls(cv)
    manifold(cv)
    pumps(cv)
    panel(cv)
    hatch(cv)
    mask = floor(cv)
    gloss(cv, mask)
    sota.floor_shadow(cv, 376, FLOOR_Y + 4, 110, 3, 0.5)
    for lx in LAMPS:
        sota.cage_lamp(cv, lx)
    for lx in LAMPS:
        sota.lamp_glow(cv, lx)
    glow(cv, 230, 6, 30, (190, 220, 190), 0.3)
    puddle(cv)


DRIP = (100, 98)            # on es forma la gota: sota el tub del col·lector
SPLASH_Y = FLOOR_Y + 6      # on cau, a terra
WATER = (196, 222, 214)


def puddle(cv):
    """El tollet que fa la gota a terra: una mica més fosc i amb un reflex."""
    x0, y0 = DRIP[0], SPLASH_Y
    for y in range(y0 - 1, y0 + 2):
        for x in range(x0 - 5, x0 + 6):
            if ((x - x0) / 5.5) ** 2 + ((y - y0) / 1.6) ** 2 <= 1:
                cv.flat(x, y, mix(cv.get(x, y), (10, 16, 16), 0.35))
    cv.flat(x0 - 2, y0, mix(cv.get(x0 - 2, y0), WATER, 0.35))
    cv.flat(x0 - 1, y0, mix(cv.get(x0 - 1, y0), WATER, 0.25))


PROPS = {'llibre': book, 'llanterna': prop_llanterna}

# ─── Animacions ────────────────────────────────────────────────────────────

def _frame_base():
    cv = Canvas(light=LIGHT)
    _base(cv)
    return cv


def _frames_manometres():
    """Les agulles dels dos manòmetres tremolen una mica (el motor principal es nota a tot el vaixell)."""
    from hd.rooms.comu import _diff
    base = _frame_base().img
    jitter = (0.0, 0.14, -0.06, 0.1, -0.14, 0.04)
    frames = []
    for i, j in enumerate(jitter):
        cv = _frame_base()
        for k, gx in enumerate((60, 140)):
            a = math.atan2(3, -2) + (j if k == 0 else -jitter[(i + 2) % len(jitter)])
            cv.disc(gx, 74, 5, 5, WHITEP, 4.6)
            cv.line(gx, 74, gx + round(math.cos(a) * 3.8), 74 + round(math.sin(a) * 3.8), DARK, 0)
        frames.append(_diff(cv.img, base))
    return frames


def _frames_gota():
    """Una gota que s'infla sota el tub, cau i esquitxa el tollet; després, una estona de res."""
    from hd.rooms.comu import _diff
    base = _frame_base().img
    x, y0 = DRIP
    frames = []
    for i in range(20):
        cv = _frame_base()

        def w(px, py, k):
            cv.flat(px, py, mix(cv.get(px, py), WATER, k))
        if 4 <= i <= 8:                                   # la gota que es forma
            w(x, y0, 0.55 + 0.08 * (i - 4))
            if i >= 6:
                w(x, y0 + 1, 0.65 + 0.1 * (i - 6))
        elif i in (9, 10):                                # cau (s'estira)
            yy = (112, 134)[i - 9]
            for d in range(3 + (i - 9) * 2):
                w(x, yy - d, 0.9 - d * 0.18)
        elif i == 11:                                     # esquitx
            w(x, SPLASH_Y - 1, 0.8)
            for dx, dy in ((-2, -2), (2, -2), (-3, -1), (3, -1), (0, -3)):
                w(x + dx, SPLASH_Y + dy, 0.6)
        elif i in (12, 13):                               # l'anell que s'obre al tollet
            r = 3 + (i - 12) * 2
            for dx in range(-r, r + 1):
                if abs(dx) >= r - 1:
                    w(x + dx, SPLASH_Y, 0.5 - (i - 12) * 0.2)
            w(x - r + 1, SPLASH_Y - 1, 0.3)
            w(x + r - 1, SPLASH_Y - 1, 0.3)
        frames.append(_diff(cv.img, base))
    return frames


ANIMS = {'manometres': {'frames': _frames_manometres, 'frameDuration': 140},
         'gota': {'frames': _frames_gota, 'frameDuration': 110}}


GEOMETRIA = {
    'things': {
        'escotilla': {'rect': (200, 0, 260, 152), 'walk': (230, 168)},
        'llibre': {'rect': (148, 170, 188, 190), 'walk': (166, 194)},
        'llanterna': {'rect': (206, 172, 242, 190), 'walk': (224, 194)},
        'bombes': {'rect': (282, 40, 476, 156), 'walk': (376, 172)},
    },
    'spawns': {'iri': (300, 190), 'vet': (360, 194), 'bastida': (110, 188)},
    'walkable': [(6, 164), (474, 164), (478, 197), (2, 197)],
}
