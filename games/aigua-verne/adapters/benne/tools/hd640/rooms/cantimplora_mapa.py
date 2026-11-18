"""
Aigua Verne — `cantimplora_mapa` (cinemàtica): la carta de navegació de la Cantimplora, a pantalla sencera.

És la taula de vidre del pont vista des de dalt, amb la càmera picada: la carta (el sistema de Vesper, el mateix cel
que als crèdits, amb la quadrícula i les òrbites puntejades) s'estira cap a nosaltres, i la quadrícula i les òrbites
fugen cap al fons, on es veu el marc de llautó de la taula i la penombra del pont. El costat de prop queda tallat per
la vora de baix. Els planetes, el palau i la nau són hologrames que suren damunt el vidre: es dibuixen drets (sense
aixafar) al punt de la carta que els toca, i els noms es posen a la pantalla perquè es llegeixin. L'estrella al cantó
de baix a l'esquerra; el mig queda lliure per al quadre del text. Es toca el planeta on es vol anar (vegeu GEOMETRIA).

Tot el que es mou és un sol prop, `nau` (la Cantimplora, petita), amb aquestes animacions:
  - `nau_<planeta>` (bucle): aparcada en òrbita, amb el llum de navegació que fa pampallugues;
  - `tremola_<planeta>` (bucle): els motors que tussen abans d'enlairar-se (la nau tremola i treu fum);
  - `vol_<origen>_<destí>` (un cop): el viatge, en un arc que s'allunya de l'estrella, amb l'estela dels motors;
    l'últim fotograma és el mateix que `nau_<destí>`.
Les tria rooms/cantimplora_mapa.json (en entrar, i en tocar un planeta).

Les rutes es calculen a la carta (pla) i es projecten a la pantalla amb la mateixa homografia que el vidre (`_m`).
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from hd.pix import Canvas, Light, W, H, hr, mix, GOLD
from hd.rooms.comu import _diff, text, text_width
from hd640.rooms.credits import space, planet, T2, AQ, FE, VE
from hd640.rooms.nau_comu import OLIVE, SAFETY, STEELN, DECKP
from hd640.tres_d import _homografia, _inversa

# Art a 2× (1280×720 per a una sala de 640×360): el mateix dibuix, amb les formes, el dither i la llum a la
# resolució real (hd1280/canvas2x.py); el motor el mostra a 1/2 (artScale al .room.json).
ART_SCALE = 2
from hd1280.canvas2x import Canvas2x as Canvas  # noqa: E402,F811
from hd.pix import Canvas as Canvas1x  # noqa: E402,F401  (llenços auxiliars en píxels de sala: figures, textos)

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)
STAR = (-30, 300)
ZT = 0.07                                   # segons per fotograma del vol

# nom, centre, radi, rampa, pluja? (la forma de credits.PLANETS), a la carta (pla)
PLANETS = (
    ('terra2', (92, 150), 30, T2, False),
    ('verdant', (215, 60), 17, VE, False),
    ('aqua', (420, 68), 24, AQ, False),
    ('ferrum', (562, 180), 33, FE, False),
)
LABELS = {'terra2': 'TERRA-2', 'verdant': 'VERDANT', 'aqua': 'AQUA', 'ferrum': 'FERRUM'}
# on queda aparcada la nau a cada planeta (el morro cap a la dreta), a la carta
PARK = {'terra2': (140, 116), 'verdant': (180, 34), 'aqua': (462, 44), 'ferrum': (574, 132)}
NAMES = tuple(PARK)

NAV = [(10, 30, 40), (20, 52, 66), (40, 90, 104), (80, 150, 160), (150, 214, 220), (220, 246, 248)]
GRID = (22, 30, 52)


# ─── La càmera: la carta (pla, 640×360) sobre el vidre, vista des de dalt ────
# El vidre és un trapezi: el costat del fons, més estret i més amunt; el de prop, més ample que la pantalla i tallat
# per la vora de baix. Una homografia (com les textures de tres_d) porta cada punt de la carta a la pantalla.

QUAD = ((52, 34), (588, 34), (668, 384), (-28, 384))       # els cantons del vidre a la pantalla (de dalt a l'esq.)
_M = _homografia(QUAD)
_MI = _inversa(_M)


def _m(x, y):
    """Un punt de la carta → la pantalla."""
    a, b, c, d, e, f, g, h, i = _M
    s, t = x / W, y / H
    w = g * s + h * t + i
    return (a * s + b * t + c) / w, (d * s + e * t + f) / w


def _carta(u, v):
    """Un punt de la pantalla → la carta."""
    a, b, c, d, e, f, g, h, i = _MI
    w = g * u + h * v + i
    return (a * u + b * v + c) / w * W, (d * u + e * v + f) / w * H


def _k(x, y):
    """Quants píxels de pantalla fa un píxel de la carta, en aquell punt."""
    u0, v0 = _m(x - 0.5, y)
    u1, v1 = _m(x + 0.5, y)
    return math.hypot(u1 - u0, v1 - v0)


def _ang(x, y, ang):
    """Un angle de la carta (una direcció a (x, y)) → l'angle a la pantalla."""
    u0, v0 = _m(x, y)
    u1, v1 = _m(x + math.cos(ang), y + math.sin(ang))
    return math.atan2(v1 - v0, u1 - u0)


# ─── El fons ────────────────────────────────────────────────────────────────

def _grid(cv):
    """La quadrícula de la carta: línies molt fluixes cada 40 píxels, amb una creueta a cada encreuament."""
    for x in range(0, W, 40):
        for y in range(0, H):
            if y % 3 == 0:
                cv.flat(x, y, mix(cv.get(x, y), GRID, 0.45))
    for y in range(0, H, 40):
        for x in range(0, W):
            if x % 3 == 0:
                cv.flat(x, y, mix(cv.get(x, y), GRID, 0.45))
    for x in range(0, W, 40):
        for y in range(0, H, 40):
            for d in (-1, 0, 1):
                cv.flat(x + d, y, mix(cv.get(x + d, y), (60, 80, 120), 0.6))
                cv.flat(x, y + d, mix(cv.get(x, y + d), (60, 80, 120), 0.6))


def _label(cv, s, cx, y):
    w = text_width(s)
    x = round(cx - w / 2)
    for j in range(-1, 6):                                       # una placa fosca perquè es llegeixi damunt les òrbites
        for i in range(-2, w + 2):
            cv.flat(x + i, y + j, mix(cv.get(x + i, y + j), (4, 8, 16), 0.7))
    text(cv, s, x, y, NAV, 4.4, lit=0)


def _palau_carta():
    _, (cx, cy), r, _, _ = PLANETS[1]
    return cx + r + 9, cy - r + 2


def _pla(tw):
    """La carta plana (la que va damunt el vidre): l'espai, l'estrella, les òrbites i la quadrícula."""
    cv = Canvas1x(light=LIGHT)
    space(cv, tw, star=STAR, planets=PLANETS)
    _grid(cv)
    return cv.img


def _mapa_quad():
    """Per a cada píxel real de la pantalla: (X, Y, x, y de la carta)."""
    S = Canvas.S
    for Y in range(H * S):
        for X in range(W * S):
            x, y = _carta((X + 0.5) / S, (Y + 0.5) / S)
            yield X, Y, x, y


def _vidre(cv, pla):
    """La carta projectada al vidre; fora, el marc de llautó i la penombra del pont."""
    src = pla.load()
    P = cv.P
    for X, Y, x, y in _mapa_quad():
        if 0 <= x < W and 0 <= y < H:
            c = src[int(x), int(y)]
            # el fons, una mica més fosc i més blau (la llum del pont és a prop: el vidre de lluny la reflecteix menys)
            k = 0.82 + 0.18 * min(1.0, y / 200)
            P[X, Y] = (int(c[0] * k), int(c[1] * k), int(c[2] * k + (1 - k) * 30), 255)
            continue
        d = max(-x, x - W + 1, -y, y - H + 1)                    # a quanta distància del vidre (en unitats de carta)
        if d < 3:
            col = GOLD[2]                                         # el bisell fosc de dins
        elif d < 12:
            lit = 5.4 if (y < 0 and d < 6) else 4.2 if y < 0 else 3.6 - (0.8 if x > W else 0)
            col = GOLD[max(0, min(len(GOLD) - 1, round(lit - (d - 3) * 0.12 + (hr(X // 3, Y // 2, 7) - 0.5) * 0.6)))]
        elif d < 30:
            col = STEELN[max(0, min(len(STEELN) - 1, round(2.2 - (d - 12) * 0.05 + (hr(X, Y, 8) - 0.5) * 0.5)))]
        else:
            # la penombra del pont, més allà de la taula: el terra de xapa, que s'enfosqueix lluny de la taula
            v = 1.6 - min(1.4, (d - 30) / 60) + (0.6 if (int(x) // 6 + int(y) // 6) % 2 == 0 and d < 90 else 0)
            col = DECKP[max(0, min(len(DECKP) - 1, round(v + (hr(X // 2, Y // 2, 9) - 0.5) * 0.8)))]
        P[X, Y] = tuple(col[:3]) + (255,)


def _reflex(cv):
    """El reflex de les bombetes del pont al vidre: dues taques càlides allargades, molt fluixes, en diagonal."""
    for (x, y), r in (((480, 250), 36), ((150, 300), 26)):
        u, v = _m(x, y)
        cv.glow(round(u), round(v), r, (255, 200, 130), 0.08)
    for k in range(40):
        u, v = _m(500 + k * 2.2, 40 + k * 1.2)
        cv.flat(u, v, mix(cv.get(u, v), (200, 210, 230), 0.25))


def _planetes(cv):
    """Els planetes (hologrames drets, al punt de la carta), amb el nom, i el palau i el nom de l'estrella."""
    star = _m(*STAR)
    for name, c, r, ramp, rain in PLANETS:
        u, v = _m(*c)
        rr = r * _k(*c)
        cv.glow(round(u), round(v + rr * 0.9), round(rr * 0.9), (120, 170, 220), 0.12)   # la claror al vidre
        planet(cv, name, (u, v), rr, ramp, rain, star=star)
        _label(cv, LABELS[name], u, v + rr + 6)
    pu, pv = _m(*_palau_carta())
    cv.glow(round(pu), round(pv), 5, (255, 220, 120), 0.35)
    _label(cv, 'PALAU', pu + 16, pv - 2)
    vu, vv = _m(34, 214)
    _label(cv, 'VESPER', vu, vv)


def bg(cv):
    _vidre(cv, _pla(_ANIM['estrelles']))
    _planetes(cv)
    _reflex(cv)


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
# radians; 0 = el morro cap a la dreta) mostrejant cada píxel en les coordenades de la nau. Com els planetes, és un
# holograma: es dibuixa a la seva mida al punt de la pantalla on cau (x, y de la carta), girada com la ruta a la
# pantalla.

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


def _ship_pantalla(cv, x, y, ang, thrust=0.0, light=True, seed=0):
    """La nau centrada a (x, y) de la pantalla. `thrust` (0–1): la flama dels motors. `light`: el llum de navegació."""
    ca, sa = math.cos(ang), math.sin(ang)
    # (es mostreja a cada píxel real: a 2×, la nau girada surt amb el doble de detall)
    for X, Y, px, py in cv.pixels(int(x) - 12, int(y) - 12, int(x) + 12, int(y) + 12):
        dx, dy = px + 0.5 - x, py + 0.5 - y
        u, v = dx * ca + dy * sa, -dx * sa + dy * ca
        col = _ship_px(u, v)
        if col:
            cv.P[X, Y] = tuple(col[:3]) + (255,)
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


def ship(cv, x, y, ang, thrust=0.0, light=True, seed=0):
    """La nau al punt (x, y) de la carta, amb el morro cap a `ang` (a la carta)."""
    u, v = _m(x, y)
    _ship_pantalla(cv, u, v, _ang(x, y, ang), thrust, light, seed)


def _frame(draw):
    cv = Canvas(light=LIGHT, img=_base_img().copy())
    draw(cv)
    return _diff(cv.img, _base_img())


def _parked(name):
    x, y = PARK[name]
    return [_frame(lambda cv: ship(cv, x, y, 0.0, light=on)) for on in (True, False)]


def _puff(cv, x, y, age, seed):
    """Una bufada de fum que s'eixampla i s'esvaeix ((x, y): a la pantalla)."""
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
    u0, v0 = _m(x0 - 11, y0)
    out = []
    for f in range(N_TREMOLA):
        jx = round((hr(f, 11) - 0.5) * 2.4)
        jy = round((hr(f, 12) - 0.5) * 2.0)
        thrust = 0.35 + 0.5 * hr(f, 13)

        def draw(cv, f=f, jx=jx, jy=jy, thrust=thrust):
            for k in range(3):                                    # una bufada cada 3 fotogrames, que dura 9
                start = (f // 3 - k) * 3
                _puff(cv, u0, v0, ((f - start) % N_TREMOLA) * ZT, 40 + (start % N_TREMOLA))
            ship(cv, x0 + jx, y0 + jy, 0.0, thrust=thrust, seed=f)
        out.append(_frame(draw))
    return out


# ─── El vol ─────────────────────────────────────────────────────────────────
# Una corba de Bézier de l'aparcament d'origen al de destí, amb el punt de control apartat de l'estrella (un arc,
# com una òrbita de transferència), a la carta. Accelera, va de pressa pel mig i frena; en sortir es gira cap al camí i
# en arribar torna a posar el morro cap a la dreta. Deixa una estela taronja que s'apaga.

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
    # que no surti del vidre ni baixi a la llista d'opcions
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
    trail = []                                                    # (x, y) a la pantalla
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
        u, v = _m(x, y)
        sa = _ang(x, y, ang)
        trail.append((u - math.cos(sa) * 11, v - math.sin(sa) * 11))
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


# ─── Geometria (coordenades de pantalla: els planetes, on cauen) ─────────────

def _zona(name):
    """El rectangle que es pot tocar d'un planeta: el disc i el nom de sota."""
    _, c, r, _, _ = next(p for p in PLANETS if p[0] == name)
    u, v = _m(*c)
    rr = r * _k(*c)
    w = max(rr + 4, text_width(LABELS[name]) // 2 + 4)
    return (round(u - w), round(v - rr - 4), round(u + w), round(v + rr + 14))


def _amb_nau(name):
    """El planeta on som, amb la nau aparcada al costat (tocar-la també vol dir quedar-se)."""
    x0, y0, x1, y1 = _zona(name)
    pu, pv = _m(*PARK[name])
    return (min(x0, round(pu) - 14), min(y0, round(pv) - 10), max(x1, round(pu) + 14), max(y1, round(pv) + 10))


def _t(rect):
    return {'rect': rect, 'walk': ((rect[0] + rect[2]) // 2, 254)}


def _zona_palau():
    pu, pv = _m(*_palau_carta())
    return (round(pu) - 5, round(pv) - 8, round(pu) + 16 + text_width('PALAU') // 2 + 4, round(pv) + 8)


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
