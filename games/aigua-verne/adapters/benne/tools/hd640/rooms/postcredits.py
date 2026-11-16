"""
Aigua Verne — `postcredits` (L): la plaça de Ferrum, temps després. La font pública raja per a tothom.

Les cases de maó ennegrit al voltant de la plaça; el cel encara de fum, però més clar (ja ha plogut); al fons, pel
carrer que hi entra, el castellet de la mina i la Canonada. La font (la de Verne, blanca, amb el lector de targetes
tapat amb un cartró i cinta) raja; la pica plena i el terra mullat. Una cua de miners hi espera torn: figures de fons
(no són sprites ni es cliquen), la primera omplint una garrafa. A la paret, el panell nou: «AIGUA VESPER · 4 ▲».
Un rètol pintat a mà: AIGUA PER A TOTHOM, i una tira de banderetes de festa travessant la plaça.

Al final de la cua hi van, com a sprites, la Rosa i en Verne (amb en Dividend en braços): aquí no es dibuixen.
ANIMS: `aigua` (el raig de la font i les esquitxades a la pica), `fum` (les xemeneies).
"""
import hd640  # noqa: F401  (abans que cap hd.rooms: posa la llibreria a 640×360)

import functools
import math


from hd.pix import Canvas, Light, W, H, hr, mix, B4
from hd.rooms.comu import _diff, text, text_width
from hd.rooms.exterior import fbm
from hd640.rooms.ferrum_comu import (
    RH, SMOG, HAZE, SLAGF, SOOT, MORTAR, COB, COAL, IRONF, RUSTF, TIN, PLANKF, WHITEV, BLUEV, REDV, BLACKT, LED,
    GLOWF, CLOTH, REDP, WATER, HELM,
    smog_sky, canonada, far_skyline, brick_wall, soot_top, window, cobbles, font_verne, miner, miner_c, tri)
from hd640.rooms.ferrum_carrer import _smoke_loop

# Art a 2× (1280×720 per a una sala de 640×360): el mateix dibuix, amb les formes, el dither i la llum a la
# resolució real (hd1280/canvas2x.py); el motor el mostra a 1/2 (artScale al .room.json).
ART_SCALE = 2
from hd1280.canvas2x import Canvas2x as Canvas  # noqa: E402,F811
from hd.pix import Canvas as Canvas1x  # noqa: E402,F401  (llenços auxiliars en píxels de sala: figures, textos)

HOR = 140
BASE = 186                      # on toquen a terra les façanes
FONT = (186, 228)               # la font: centre x, base
SUN = (520, 46)
SLATE = [(14, 14, 18), (24, 24, 30), (36, 36, 42), (50, 50, 56), (66, 64, 70), (86, 82, 86)]
DOOR = [(14, 22, 22), (22, 36, 34), (32, 52, 48), (44, 70, 62), (60, 90, 78), (80, 112, 96)]
FLAGS = [REDP, [(50, 36, 6), (110, 80, 10), (180, 136, 20), (230, 190, 50), (250, 230, 120)], BLUEV, CLOTH]
CHIMNEYS = ((60, 52), (300, 66), (566, 58))

LIGHT = Light(ambient=0.35, vignette=(70, 20), floor_fade=(248, 30))
LIGHT.point(SUN[0], SUN[1] + 30, r=560, k=1.2, power=1.2)


# ─── Cel i fons ────────────────────────────────────────────────────────────

def cel(cv):
    smog_sky(cv, HOR, sun=SUN, seed=17, bright=0.8)
    far_skyline(cv, HOR, seed=19, headframes=((452, HOR - 2, 50),), chimneys=((520, HOR, 84, 3),))
    canonada(cv, 486, HOR - 1)


def casa(cv, x0, x1, top, seed, door=None, wins=(), lit=(), roof=True):
    """Una casa de miners: maó ennegrit, teulada de pissarra, porta i finestres."""
    if roof:
        cv.poly([(x0 - 3, top + 1), (x0 + 5, top - 16), (x1 - 5, top - 16), (x1 + 3, top + 1)], SLATE,
                lambda x, y: 3.0 + (y - top + 16) * 0.04 - (1.2 if (y - top) % 4 == 0 else 0) +
                (fbm(x / 9, y / 5, seed) - 0.5) * 0.8)
    brick_wall(cv, x0, top, x1, BASE, base=3.3, seed=seed, soot=soot_top(top, 46, 1.8, seed + 1))
    cv.rect(x0 - 3, top - 1, x1 + 2, top + 1, MORTAR, 3.4)
    cv.rect(x0, BASE - 7, x1, BASE, MORTAR, lambda x, y: 2.6 + (0.6 if (x // 8 + y // 3) % 2 else 0) -
            (1.4 if x % 8 == 0 else 0))
    for i, (wx, wy, ww, wh) in enumerate(wins):
        window(cv, wx, wy, ww, wh, lit=(i in lit), seed=seed + i)
    if door:
        dx0, dtop = door
        dx1 = dx0 + 26
        cv.rect(dx0 - 3, dtop - 4, dx1 + 3, dtop - 1, MORTAR, 3.6)
        cv.rect(dx0, dtop, dx1, BASE - 1, DOOR, lambda x, y: 2.6 - (1.2 if (x - dx0) % 7 == 0 else 0) +
                (fbm(x / 3, y / 14, dx0) - 0.5) * 0.8)
        cv.disc(dx1 - 4, (dtop + BASE) // 2, 1.2, 1.2, TIN, 4.0)


def cases(cv):
    for cx, ct in CHIMNEYS:
        brick_wall(cv, cx - 5, ct, cx + 5, ct + 30, base=3.0, seed=cx, bw=6, bh=3, soot=soot_top(ct, 10, 2.4, cx))
        cv.rect(cx - 6, ct - 2, cx + 6, ct, MORTAR, 2.6)
    casa(cv, -4, 132, 70, 31, door=(60, 116), wins=((14, 86, 16, 22), (96, 86, 16, 22), (14, 134, 18, 24),
                                                   (100, 134, 18, 24)), lit=(2,))
    casa(cv, 132, 252, 92, 33, door=(214, 124), wins=((146, 104, 14, 18), (186, 104, 14, 18), (226, 104, 14, 18)),
         lit=(1,))
    casa(cv, 252, 420, 80, 35, door=(330, 118), wins=((266, 96, 16, 20), (300, 96, 16, 20), (370, 96, 16, 20),
                                                     (266, 136, 18, 24), (380, 136, 18, 24)), lit=(0, 4))
    casa(cv, 500, 640, 74, 37, door=(588, 116), wins=((514, 90, 16, 22), (556, 90, 16, 22), (612, 90, 16, 22),
                                                     (520, 134, 18, 24)), lit=(1, 3))
    # el carrer que entra a la plaça (420-500), cap al fons: cases llunyanes
    for side in (-1, 1):
        for i in range(5):
            f = 1 - i / 5
            xa = 460 + side * (8 + 32 * f)
            xb = 460 + side * (8 + 32 * max(0.0, f - 0.2))
            top = HOR - 2 - 30 * f
            x0, x1 = sorted((xa, xb))
            for x in range(int(x0), int(x1) + 1):
                for y in range(int(top + hr(i, side) * 4), BASE):
                    lvl = 2.4 + f * 0.8 + (hr(x // 3, y // 3, i) - 0.5) * 0.5
                    if (y - int(top)) % max(2, int(9 * f)) == 1 and (x - int(x0)) % max(3, int(8 * f)) in (1, 2):
                        lvl -= 1.2
                    cv.put(x, y, HAZE if f < 0.5 else SOOT, lvl - (0 if f < 0.5 else 0.4), lit=0)
    cv.tint(420, 90, 500, BASE, (160, 124, 96), lambda x, y: 0.25 * max(0.0, 1 - (y - 110) / 80))


def retol(cv):
    """AIGUA PER A TOTHOM, pintat a mà a la paret, en blanc de calç."""
    s = 'AIGUA PER A TOTHOM'
    tw = text_width(s)
    x0, y0 = 336 - tw // 2, 85
    text(cv, s, x0, y0, CLOTH, 4.4)
    for dx in (3, 21, 40, 58):
        for k in range(1 + int(hr(dx, 4) * 3)):
            cv.put(x0 + dx, y0 + 5 + k, CLOTH, 3.6)


def panell_vesper(cv):
    """El panell nou: el mateix de Verne, amb el rètol canviat. AIGUA VESPER · 4 ▲."""
    s = 'AIGUA VESPER · 4'
    tw = text_width(s)
    w = tw + 22
    x0, y0, h = 540 - w // 2, 168 - 52, 13
    cv.rect(x0 - 1, y0 - 1, x0 + w, y0 + h, IRONF, 2.0)
    cv.rect(x0, y0, x0 + w - 1, y0 + h - 1, BLACKT, 1.0, lit=0)
    cv.rect(x0, y0, x0 + w - 1, y0, BLACKT, 3.0, lit=0)
    cv.disc(x0 + 5, y0 + 7, 2, 3, BLUEV, 3.0, lit=0)                                       # la gota
    cv.flat(x0 + 5, y0 + 3, BLUEV[3])
    text(cv, s, x0 + 11, y0 + 4, None, 0, flat=LED[3])
    tri(cv, x0 + 11 + tw + 2, y0 + 3, LED[3], up=True)
    cv.glow(x0 + w / 2, y0 + 7, w * 0.6, (250, 120, 40), 0.12)
    for bx in (x0 + 4, x0 + w - 6):                                                         # els suports
        cv.rect(bx, y0 + h, bx + 1, y0 + h + 3, IRONF, 3.0)


def banderetes(cv):
    """Una tira de banderetes de festa travessant la plaça (d'una finestra a l'altra)."""
    xa, ya, xb, yb = 118, 100, 520, 92
    for i in range(0, 401):
        t = i / 400
        x = xa + (xb - xa) * t
        y = ya + (yb - ya) * t + math.sin(t * math.pi) * 22
        cv.put(x, y, COAL, 1.4)
        if i % 14 == 7:
            ramp = FLAGS[(i // 14) % 4]
            for j in range(7):
                for k in range(-3 + j // 2, 4 - j // 2):
                    cv.put(x + k, y + 1 + j, ramp, 3.4 - j * 0.15 + (0.4 if k < 0 else 0))


# ─── Terra, font, cua ──────────────────────────────────────────────────────

def terra(cv):
    cobbles(cv, HOR, RH - 1, seed=29, base=3.2, vp=(460, HOR - 30))
    cv.rect(0, BASE, 640, BASE + 5, MORTAR, lambda x, y: 3.6 - (y - BASE) * 0.3 - (1.2 if x % 16 == 0 else 0))
    cv.rect(0, BASE + 6, 640, BASE + 6, COAL, 1.0)
    # el terra mullat al voltant de la font, amb reflexos
    fx, fb = FONT
    def wet(x, y):
        d = ((x - fx - 6) / 74) ** 2 + ((y - fb - 6) / 16) ** 2
        return 0.5 if d < 1 - fbm(x / 10, y / 4, 31) * 0.4 else 0
    cv.darken(fx - 90, fb - 12, fx + 90, fb + 24, wet, dither=False)
    cv.tint(fx - 90, fb - 12, fx + 90, fb + 24, (150, 120, 100),
            lambda x, y: 0.25 if wet(x, y) and (x + y * 3) % 5 == 0 else 0)            # el cel, reflectit
    for i in range(30):                                                                     # brillantors de l'aigua
        x = fx - 60 + hr(i, 1) * 130
        y = fb - 2 + hr(i, 2) * 20
        if wet(x, y):
            cv.put(x, y, WATER, 3.6)
            cv.put(x + 1, y, WATER, 2.6)
    # un rierol que baixa cap a la claveguera
    for k in range(80):
        x = fx + 20 + k * 1.5
        y = fb + 10 + k * 0.28 + math.sin(k * 0.3) * 1.2
        cv.put(x, y, WATER, 2.4 + (0.8 if k % 5 == 0 else 0))


def font(cv):
    x, base = FONT
    font_verne(cv, x, base, lector=True, tapat=True)
    # la pica, plena
    cv.disc(x, base - 14, 18, 3.2, WATER, lambda nx, ny: 2.8 + nx * 0.6 - ny * 0.8, lit=0)
    cv.put(x + 6, base - 15, WATER, 5.0, lit=0)
    cv.put(x - 9, base - 14, WATER, 4.4, lit=0)
    # el desguàs que vessa per un costat
    for y in range(base - 12, base):
        cv.put(x + 21 + (y - base + 12) * 0.2, y, WATER, 3.0, lit=0)


def cua(cv):
    """La cua de miners que esperen torn a la font: de la font cap a la dreta, i una mica cap a la càmera."""
    x0, base = FONT
    people = [
        # x, y peus, alçada, var, extra
        (x0 - 32, base + 4, 79, 1, dict(facing=1, hold='bidon', casc=False, cua=True)),   # la que omple la garrafa
        (x0 + 38, base + 2, 81, 0, dict(hold='bidon')),
        (x0 + 60, base + 3, 62, 3, dict(kid=True, lamp=False)),
        (x0 + 86, base + 4, 82, 2, dict(facing=1, casc=False)),                          # es gira a fer petar la xerrada
        (x0 + 108, base + 5, 78, 1, dict(lamp=False, casc=False, cua=True)),
        (x0 + 140, base + 5, 83, 4, dict(hold='bidon')),
        (x0 + 164, base + 6, 80, 0, dict(casc=False)),
        (x0 + 186, base + 7, 56, 2, dict(kid=True, lamp=False)),
        (x0 + 204, base + 7, 81, 3, dict(hold='bidon', lamp=False)),
        (x0 + 236, base + 8, 82, 5, dict(casc=False, cua=True, hold='bidon')),
        (x0 + 258, base + 9, 80, 6, dict()),
    ]
    for x, y, h, var, ex in sorted(people, key=lambda p: p[1]):
        kw = dict(facing=-1, light_from=1)
        kw.update(ex)
        cv.darken(x - 14 + 8, y - 2, x + 22, y + 2,
                  lambda xx, yy, x=x, y=y: 0.7 if ((xx - x - 6) / 15) ** 2 + ((yy - y) / 2.2) ** 2 <= 1 else 0)
        miner_c(cv, x, y, h=h, var=var, **kw)


# ─── Composició ────────────────────────────────────────────────────────────

def bg(cv):
    cel(cv)
    terra(cv)
    cases(cv)
    retol(cv)
    panell_vesper(cv)
    banderetes(cv)
    font(cv)
    cua(cv)
    for y in range(RH, H):
        for x in range(W):
            cv.flat(x, y, (0, 0, 0))


PROPS = {}


# ─── Animacions ─────────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def _base():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv.img


def _frames_aigua():
    """El raig de la font: un fil d'aigua que tremola, i les esquitxades i els cercles a la pica."""
    x, base = FONT
    y0, y1 = base - 30, base - 15
    frames = []
    n = 8
    for f in range(n):
        cv = Canvas(transparent=True)
        for y in range(y0, y1 + 1):
            t = (y - y0) / (y1 - y0)
            wob = math.sin(f * 0.8 + y * 0.9) * 0.4 * t
            for dx in (0, 1):
                xx = int(round(x - 0.5 + dx + wob))
                lvl = 2 + (1 if (y + f) % 4 == dx else 0) + (1 if dx == 0 else 0)
                cv.flat(xx, y, WATER[min(5, lvl + (1 if (y - f * 2) % 7 == 0 else 0))])
        # l'esquitx
        for k in range(5):
            s = ((f / n) + k / 5) % 1
            a = (k - 2) * 0.7
            sx = x + math.sin(a) * s * 8
            sy = y1 - math.sin(s * math.pi) * 4
            if s < 0.9:
                cv.flat(sx, sy, WATER[5 if s < 0.4 else 4])
        # els cercles a l'aigua de la pica
        r = 2 + (f % 4) * 3
        for a in range(0, 360, 24):
            px = x + math.cos(math.radians(a)) * r
            py = y1 + math.sin(math.radians(a)) * r * 0.2
            if ((px - x) / 18) ** 2 + ((py - base + 14) / 3.2) ** 2 < 1:
                cv.flat(px, py, WATER[4])
        frames.append(cv.img)
    return frames


def _frames_fum():
    return _smoke_loop(_base(), [(cx, ct - 4, 3, 30) for cx, ct in CHIMNEYS], 12)


ANIMS = {'aigua': {'frames': _frames_aigua, 'frameDuration': 90},
         'fum': {'frames': _frames_fum, 'frameDuration': 160}}


# ─── Geometria (640×360) ───────────────────────────────────────────────────

GEOMETRIA = {
    'things': {},
    'spawns': {'rosa': (478, 240), 'verne': (522, 244)},
    'walkable': [(0, 238), (640, 238), (640, 257), (0, 257)],
}
