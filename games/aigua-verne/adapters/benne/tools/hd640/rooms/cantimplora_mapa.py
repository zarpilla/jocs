"""
Aigua Verne — `cantimplora_mapa` (cinemàtica): la carta de navegació de la Cantimplora, a pantalla sencera.

El sistema de Vesper (el mateix cel que als crèdits, sense la pluja del final): l'estrella al cantó de baix a
l'esquerra, les òrbites puntejades i els quatre planetes amb el seu nom, i el palau orbital, un punt daurat al
costat de Verdant. Damunt, una quadrícula de carta molt fluixa. Els planetes queden als cantons: el mig és per al
quadre del text. Es toca el planeta on es vol anar (vegeu GEOMETRIA).

Tot el que es mou és un sol prop, `nau` (la Cantimplora, petita), amb aquestes animacions:
  - `nau_<planeta>` (bucle): aparcada en òrbita, amb el llum de navegació que fa pampallugues;
  - `tremola_<planeta>` (bucle): els motors que tussen abans d'enlairar-se (la nau tremola i treu fum);
  - `vol_<origen>_<destí>` (un cop): el viatge, en un arc que s'allunya de l'estrella, amb l'estela dels motors;
    l'últim fotograma és el mateix que `nau_<destí>`.
Les tria rooms/cantimplora_mapa.json (en entrar, i en tocar un planeta).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from hd.pix import Canvas, Light, W, H, hr, mix
from hd.rooms.comu import _diff, text, text_width
from hd640.rooms.credits import space, planet, T2, AQ, FE, VE
from hd640.rooms.nau_comu import OLIVE, SAFETY

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)
STAR = (-30, 300)
ZT = 0.07                                   # segons per fotograma del vol

# nom, centre, radi, rampa, pluja? (la forma de credits.PLANETS)
PLANETS = (
    ('terra2', (92, 150), 30, T2, False),
    ('verdant', (215, 60), 17, VE, False),
    ('aqua', (420, 68), 24, AQ, False),
    ('ferrum', (562, 180), 33, FE, False),
)
LABELS = {'terra2': 'TERRA-2', 'verdant': 'VERDANT', 'aqua': 'AQUA', 'ferrum': 'FERRUM'}
# on queda aparcada la nau a cada planeta (el morro cap a la dreta)
PARK = {'terra2': (140, 116), 'verdant': (180, 34), 'aqua': (462, 44), 'ferrum': (574, 132)}
NAMES = tuple(PARK)

NAV = [(10, 30, 40), (20, 52, 66), (40, 90, 104), (80, 150, 160), (150, 214, 220), (220, 246, 248)]
GRID = (22, 30, 52)


# ─── El fons ────────────────────────────────────────────────────────────────

def _grid(cv):
    """La quadrícula de la carta: línies molt fluixes cada 40 píxels, amb una creueta a cada encreuament."""
    for x in range(0, W, 40):
        for y in range(0, H):
            if y % 3 == 0:
                cv.flat(x, y, mix(cv.get(x, y), GRID, 0.35))
    for y in range(0, H, 40):
        for x in range(0, W):
            if x % 3 == 0:
                cv.flat(x, y, mix(cv.get(x, y), GRID, 0.35))
    for x in range(0, W, 40):
        for y in range(0, H, 40):
            for d in (-1, 0, 1):
                cv.flat(x + d, y, mix(cv.get(x + d, y), (60, 80, 120), 0.5))
                cv.flat(x, y + d, mix(cv.get(x, y + d), (60, 80, 120), 0.5))


def _brackets(cv):
    """Els cantons de la carta, com una pantalla de navegació."""
    m, k = 6, 14
    col = (70, 120, 140)
    for (x, y, dx, dy) in ((m, m, 1, 1), (W - 1 - m, m, -1, 1), (m, 258, 1, -1), (W - 1 - m, 258, -1, -1)):
        for i in range(k):
            cv.flat(x + dx * i, y, col)
            cv.flat(x, y + dy * i, col)


def _label(cv, s, cx, y):
    w = text_width(s)
    x = round(cx - w / 2)
    for j in range(-1, 6):                                       # una placa fosca perquè es llegeixi damunt les òrbites
        for i in range(-2, w + 2):
            cv.flat(x + i, y + j, mix(cv.get(x + i, y + j), (4, 8, 16), 0.7))
    text(cv, s, x, y, NAV, 4.4, lit=0)


def _palau(cv):
    """El palau orbital, al costat de Verdant (el dibuixa `planet`), i el seu nom."""
    _, (cx, cy), r, _, _ = PLANETS[1]
    px, py = cx + r + 9, cy - r + 2
    cv.glow(px, py, 5, (255, 220, 120), 0.35)
    _label(cv, 'PALAU', px + 16, py - 2)


def bg(cv):
    space(cv, _ANIM['estrelles'], star=STAR, planets=PLANETS)
    _grid(cv)
    for name, c, r, ramp, rain in PLANETS:
        planet(cv, name, c, r, ramp, rain, star=STAR)
        _label(cv, LABELS[name], c[0], c[1] + r + 6)
    _palau(cv)
    _label(cv, 'VESPER', 34, 214)
    _brackets(cv)


_ANIM = {'estrelles': None}


@functools.lru_cache(maxsize=None)
def _base_img():
    cv = Canvas(light=LIGHT)
    bg(cv)
    return cv.img.copy()


def _estrelles():
    out = []
    for f in range(6):
        _ANIM['estrelles'] = f
        try:
            cv = Canvas(light=LIGHT)
            bg(cv)
        finally:
            _ANIM['estrelles'] = None
        out.append(_diff(cv.img, _base_img()))
    return out


# ─── La Cantimplora ─────────────────────────────────────────────────────────
# Una nau cisterna vista de dalt, de 17 píxels: el buc verd oliva i panxut, la franja taronja de seguretat, els
# tres dipòsits rodons al llom, la cabina ambre al morro i els motors al darrere. Es dibuixa girada (`ang`, en
# radians; 0 = el morro cap a la dreta) mostrejant cada píxel en les coordenades de la nau.

AMBER = (255, 196, 90)
ENGINE = (255, 150, 60)
SMOKE = (110, 104, 112)


def _ship_px(u, v):
    """Color del píxel (u al llarg, v de través) de la nau, o None. Il·luminada per l'esquerra (`v` < 0)."""
    for tu in (-5.6, -2.6, 2.6):                                  # els dipòsits, rodons, al llom
        dd = math.hypot(u - tu, v)
        if dd < 1.7:
            return OLIVE[6] if (u - tu) + v < -0.6 else OLIVE[5]
    if -8.5 <= u <= 8.5:
        half = 3.4 * math.sqrt(max(0.0, 1 - ((u - 0.5) / 9.0) ** 2))
        if u > 5:
            half *= max(0.3, 1 - (u - 5) / 5)                     # el morro, més prim
        if abs(v) <= half:
            if u > 5.2 and abs(v) <= 1.2:
                return AMBER                                      # la cabina
            if -0.6 <= u <= 0.8:
                return SAFETY[4]                                  # la franja
            edge = abs(v) > half - 0.9
            lvl = 6.2 - v * 0.4 - (1.2 if edge else 0)
            return OLIVE[max(0, min(len(OLIVE) - 1, round(lvl)))]
    if -10.5 <= u < -8.5 and abs(v) <= 1.6:
        return (60, 56, 52)                                       # les toveres
    return None


def ship(cv, x, y, ang, thrust=0.0, light=True, seed=0):
    """La nau centrada a (x, y). `thrust` (0–1): la flama dels motors. `light`: el llum de navegació."""
    ca, sa = math.cos(ang), math.sin(ang)
    for py in range(int(y) - 12, int(y) + 13):
        for px in range(int(x) - 12, int(x) + 13):
            dx, dy = px + 0.5 - x, py + 0.5 - y
            u, v = dx * ca + dy * sa, -dx * sa + dy * ca
            col = _ship_px(u, v)
            if col:
                cv.flat(px, py, col)
    tail = (x - ca * 11, y - sa * 11)
    if thrust > 0:
        cv.glow(round(tail[0]), round(tail[1]), round(3 + 4 * thrust), ENGINE, 0.35 + 0.4 * thrust)
        for k in range(1, 1 + round(5 * thrust)):
            fx, fy = x - ca * (10 + k), y - sa * (10 + k)
            if hr(k, seed) < 1.1 - k / (6 * thrust + 1):
                cv.flat(round(fx), round(fy), (255, 236, 170) if k < 3 else ENGINE)
    if light:                                                     # el llum de navegació, al morro
        lx, ly = x + ca * 7 - sa * 2.6, y + sa * 7 + ca * 2.6
        cv.flat(round(lx), round(ly), (255, 90, 70))
        cv.glow(round(lx), round(ly), 2, (255, 90, 70), 0.4)


def _frame(draw):
    cv = Canvas(light=LIGHT, img=_base_img().copy())
    draw(cv)
    return _diff(cv.img, _base_img())


def _parked(name):
    x, y = PARK[name]
    return [_frame(lambda cv: ship(cv, x, y, 0.0, light=on)) for on in (True, False)]


def _puff(cv, x, y, age, seed):
    """Una bufada de fum que s'eixampla i s'esvaeix."""
    if age < 0 or age > 0.9:
        return
    r = 1.5 + age * 5
    a = (1 - age / 0.9) ** 1.2
    for j in range(5):
        bx = x - age * (8 + 3 * j) + hr(j, seed) * 3
        by = y + (hr(j, seed + 1) - 0.5) * (4 + age * 8)
        for py in range(int(by - r), int(by + r) + 1):
            for px in range(int(bx - r), int(bx + r) + 1):
                d = math.hypot(px - bx, py - by) / r
                if d < 1 and hr(px, py, seed + j) < a * (1 - d * d) * 1.4:
                    cv.flat(px, py, mix(cv.get(px, py), SMOKE, 0.75))


N_TREMOLA = 10


def _tremola(name):
    """Els motors que tussen: la nau tremola, la flama s'encén a batzegades i treu fum."""
    x0, y0 = PARK[name]
    out = []
    for f in range(N_TREMOLA):
        jx = round((hr(f, 11) - 0.5) * 2.4)
        jy = round((hr(f, 12) - 0.5) * 2.0)
        thrust = 0.35 + 0.5 * hr(f, 13)

        def draw(cv, f=f, jx=jx, jy=jy, thrust=thrust):
            for k in range(3):                                    # una bufada cada 3 fotogrames, que dura 9
                start = (f // 3 - k) * 3
                _puff(cv, x0 - 11, y0, ((f - start) % N_TREMOLA) * ZT, 40 + (start % N_TREMOLA))
            ship(cv, x0 + jx, y0 + jy, 0.0, thrust=thrust, seed=f)
        out.append(_frame(draw))
    return out


# ─── El vol ─────────────────────────────────────────────────────────────────
# Una corba de Bézier de l'aparcament d'origen al de destí, amb el punt de control apartat de l'estrella (un arc,
# com una òrbita de transferència). Accelera, va de pressa pel mig i frena; en sortir es gira cap al camí i en
# arribar torna a posar el morro cap a la dreta. Deixa una estela taronja que s'apaga.

def _route(a, b):
    (x0, y0), (x2, y2) = PARK[a], PARK[b]
    mx, my = (x0 + x2) / 2, (y0 + y2) / 2
    dx, dy = x2 - x0, y2 - y0
    d = math.hypot(dx, dy)
    nx, ny = -dy / d, dx / d
    if (mx + nx - STAR[0]) ** 2 + (my + ny - STAR[1]) ** 2 < (mx - STAR[0]) ** 2 + (my - STAR[1]) ** 2:
        nx, ny = -nx, -ny                                         # que s'allunyi de l'estrella
    bend = 0.14 * d
    cx, cy = mx + nx * bend, my + ny * bend
    # que no surti de la pantalla ni baixi a la llista d'opcions
    cx, cy = max(30, min(W - 30, cx)), max(14, min(236, cy))
    return (x0, y0), (cx, cy), (x2, y2), d


def _bez(p0, p1, p2, s):
    q = 1 - s
    return (q * q * p0[0] + 2 * q * s * p1[0] + s * s * p2[0], q * q * p0[1] + 2 * q * s * p1[1] + s * s * p2[1])


def _ease(t):
    t = max(0.0, min(1.0, t))
    return 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


def _lerp_ang(a, b, k):
    d = (b - a + math.pi) % (2 * math.pi) - math.pi
    return a + d * k


def _vol(a, b):
    p0, p1, p2, d = _route(a, b)
    dur = 2.2 + d / 260                                           # de 2,6 s a uns 4 s
    n = round(dur / ZT)
    trail = []                                                    # (x, y, edat en fotogrames)
    out = []
    for f in range(n + 1):
        t = f / n
        s = _ease(t)
        x, y = _bez(p0, p1, p2, s)
        hx, hy = _bez(p0, p1, p2, min(1.0, s + 0.01))
        if s >= 0.99:
            hx, hy = x + (x - _bez(p0, p1, p2, s - 0.01)[0]), y + (y - _bez(p0, p1, p2, s - 0.01)[1])
        path_ang = math.atan2(hy - y, hx - x)
        turn_in = min(1.0, t / 0.18)
        turn_out = min(1.0, (1 - t) / 0.15)
        ang = _lerp_ang(0.0, path_ang, _ease(turn_in) * _ease(turn_out))
        speed = 1 - abs(2 * t - 1)
        thrust = 0.0 if f == n else max(0.25, min(1.0, 0.3 + speed * 1.2)) if t < 0.85 else 0.3
        trail.append((x - math.cos(ang) * 11, y - math.sin(ang) * 11))
        trail = trail[-18:]

        def draw(cv, x=x, y=y, ang=ang, thrust=thrust, f=f, tr=list(trail)):
            if f < n:
                for i, (tx, ty) in enumerate(reversed(tr[:-1])):      # l'estela: de la més nova a la més vella
                    k = 1 - (i + 1) / len(tr)
                    if k <= 0:
                        continue
                    cv.glow(round(tx), round(ty), 3, ENGINE, 0.4 * k)
                    cv.flat(round(tx), round(ty), mix(cv.get(round(tx), round(ty)), (255, 200, 120), 0.8 * k))
            if f == n:
                ship(cv, x, y, 0.0)                               # aparcada: igual que `nau_<destí>`
            else:
                ship(cv, x, y, ang, thrust=thrust, light=(f // 5) % 2 == 0, seed=f)
        out.append(_frame(draw))
    return out


PROPS = {}

ANIMS = {
    'estrelles': {'frames': _estrelles, 'frameDuration': 400},
    'nau': {'frames': lambda: [Canvas(light=LIGHT, transparent=True).img], 'frameDuration': 1000, 'loop': False, 'zIndex': 3},
}
for _p in NAMES:
    ANIMS[f'nau_{_p}'] = {'frames': functools.partial(_parked, _p), 'frameDuration': 600, 'prop': 'nau'}
    ANIMS[f'tremola_{_p}'] = {'frames': functools.partial(_tremola, _p), 'frameDuration': round(ZT * 1000),
                              'prop': 'nau'}
    for _q in NAMES:
        if _q != _p:
            ANIMS[f'vol_{_p}_{_q}'] = {'frames': functools.partial(_vol, _p, _q), 'frameDuration': round(ZT * 1000),
                                       'loop': False, 'prop': 'nau'}


def _zona(name):
    """El rectangle que es pot tocar d'un planeta: el disc i el nom de sota."""
    _, (cx, cy), r, _, _ = next(p for p in PLANETS if p[0] == name)
    w = max(r + 4, text_width(LABELS[name]) // 2 + 4)
    return (cx - w, cy - r - 4, cx + w, cy + r + 14)


def _amb_nau(name):
    """El planeta on som, amb la nau aparcada al costat (tocar-la també vol dir quedar-se)."""
    x0, y0, x1, y1 = _zona(name)
    px, py = PARK[name]
    return (min(x0, px - 14), min(y0, py - 10), max(x1, px + 14), max(y1, py + 10))


def _t(rect):
    return {'rect': rect, 'walk': ((rect[0] + rect[2]) // 2, 254)}


def _zona_palau():
    _, (cx, cy), r, _, _ = PLANETS[1]
    px, py = cx + r + 9, cy - r + 2
    return (px - 5, py - 8, px + 16 + text_width('PALAU') // 2 + 4, py + 8)


# Cada planeta es toca per anar-hi (`<planeta>`: només si és obert i no hi som) o per quedar-se (`aqui_<planeta>`: el
# planeta on som); les condicions són a rooms/cantimplora_mapa.json. No hi ha protagonista: el passadís de sota és
# només perquè el motor tingui on posar els punts d'arribada.
GEOMETRIA = {
    'things': {
        **{n: _t(_zona(n)) for n in NAMES},
        **{f'aqui_{n}': _t(_amb_nau(n)) for n in NAMES},
        'palau': _t(_zona_palau()),
    },
    'spawns': {},
}
