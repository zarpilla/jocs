"""
Aigua Verne — `proleg_terra2` (L, cinemàtica): el primer pla del pròleg, Terra-2 de lluny.

És el mateix pla que la portada, sense el títol: «Comença» esvaeix el títol i hi entra amb un tall net. Cada frase
de rooms/proleg_terra2.json engega el seu tros d'animació amb una indicació d'escena (`{"prop": "pou", "anim":
"pou_on"}`), de fons i sense detall. Tot passa fora del quadre del text del narrador (el centre de la pantalla):

  - `pou_on` (bucle): la bomba de Verne del pou cabeceja, i a cada cabotada un glop d'aigua blava corre per la
    canonada de terra fins a la base de la Canonada;
  - `canonada_puja` (un cop) i `canonada_on` (bucle): l'aigua puja per la Canonada a polsos fins al dipòsit
    orbital, que s'il·lumina de blau cada vegada que n'arriba un;
  - `nau_apaga` (un cop): la Cantimplora tus pels motors, la cabina parpelleja i s'apaga, i després la rampa;
  - `germanes_surten` (un cop): l'Iri (coure i marró) i la Vet (monyo negre i blau) baixen per la rampa i se'n
    van pel corriol cap a la posta, cada cop més petites, fins que la pols se les empassa. En Diu surt a la
    rampa, s'hi asseu i les mira marxar.

Cada capa és la diferència amb el fons (portada.diff): com a la portada, es dibuixa sobre una còpia del fons.
"""
import functools
import math

import hd640  # noqa: F401  (abans de cap hd.rooms: posa la llibreria a 640×360)
from hd.pix import Canvas, Light, hr, mix
import hd640.rooms.portada as portada
from hd640.rooms.portada import CAN_X, HOR, TANK, SHIP, PUMP

LIGHT = Light(ambient=0.0, vignette=None, floor_fade=None)
ZT = 0.1                                   # segons per fotograma de les animacions del pròleg


def bg(cv):
    portada.scene(cv)


@functools.lru_cache(maxsize=None)
def _variant(**kw):
    cv = Canvas(light=LIGHT)
    portada.scene(cv, **kw)
    return cv.img.copy()


def _base():
    return portada.base_img()


def _empty():
    return [Canvas(light=LIGHT, transparent=True).img]


def _canvas(img=None):
    return Canvas(light=LIGHT, img=(img or _base()).copy())


def _blend(cv, x, y, col, a):
    x, y = int(round(x)), int(round(y))
    if 0 <= x < cv.w and 0 <= y < cv.h and a > 0.02:
        cv.flat(x, y, mix(cv.get(x, y), col, min(1.0, a)))


def _ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


# ─── La bomba del pou ───────────────────────────────────────────────────────

POU_N = 15                                  # una cabotada (1,5 s)
BLUE = (70, 150, 255)
BLUE_HI = (190, 226, 255)


def _pou_frame(f):
    cv = _canvas(_variant(pump=False))
    portada.bomba_verne(cv, (0.25 + f / POU_N) % 1.0)
    # el glop d'aigua per la canonada de terra, que s'alenteix de lluny
    u = 1 - (1 - f / POU_N) ** 1.4
    x, y = portada.pipe_xy(u)
    cv.glow(round(x), round(y), 7 - round(3 * u), (80, 160, 255), 0.6)
    for j in range(6):
        bx, by = portada.pipe_xy(max(0.0, u - j * 0.012))
        _blend(cv, bx, by, BLUE_HI if j < 2 else BLUE, 0.95 - j * 0.12)
        _blend(cv, bx, by + 1, BLUE, 0.6 - j * 0.08)
    return portada.diff(cv.img)


# ─── La Canonada ────────────────────────────────────────────────────────────
# Un pols surt de la base cada 1,5 s i triga 3 s a arribar al dipòsit (de lluny va més a poc a poc); quan hi
# arriba, el dipòsit fa una claror blava. `canonada_puja` comença sense cap pols (els primers 3 s) i acaba just on
# comença el bucle `canonada_on`.

C_GAP, C_TRIP, C_FLASH = 1.5, 3.0, 1.0
C_Y0, C_Y1 = TANK[1] + 8, HOR - 7


def _pulse(cv, age):
    k = 1 - (1 - age / C_TRIP) ** 1.5
    yc = C_Y1 - (C_Y1 - C_Y0) * k
    s = (yc - C_Y0) / (C_Y1 - C_Y0)                 # 1 a baix, 0 dalt
    w = 1.0 + 2.0 * (yc - (TANK[1] + 6)) / (HOR - 6 - TANK[1] - 6)
    bh = 4 + 8 * s
    cv.glow(CAN_X, round(yc), round(6 + 8 * s), (80, 160, 255), 0.55)
    for y in range(int(yc - bh), int(yc + bh) + 1):
        a = min(1.0, 1.3 * (1 - abs(y - yc) / (bh + 0.5)))
        for x in range(int(CAN_X - w), int(CAN_X + w) + 1):
            _blend(cv, x, y, BLUE_HI if x < CAN_X or abs(y - yc) < 1 else BLUE, a)


def _flash(cv, age):
    k = (1 - age / C_FLASH) ** 1.3
    cv.glow(TANK[0], TANK[1], 40, (110, 180, 255), 0.7 * k)
    cv.glow(TANK[0] - 11, TANK[1] + 1, 12, (170, 220, 255), 0.8 * k)
    cv.glow(CAN_X, TANK[1] + 9, 7, (150, 210, 255), 0.8 * k)


def _canonada_frame(t):
    cv = _canvas()
    starts = [i * C_GAP for i in range(int(t / C_GAP) + 1)]
    for s0 in starts:
        age = t - s0
        if age < C_TRIP:
            _pulse(cv, age)
        elif age < C_TRIP + C_FLASH:
            _flash(cv, age - C_TRIP)
    return portada.diff(cv.img)


def _canonada_puja():
    return [_canonada_frame(i * ZT) for i in range(round(C_TRIP / ZT))]


def _canonada_on():
    return [_canonada_frame(C_TRIP + i * ZT) for i in range(round(C_GAP / ZT))]


# ─── La Cantimplora s'apaga ─────────────────────────────────────────────────

X0, GY = SHIP
L_SHIP = 124
TOP, BOT = GY - 34, GY - 10
CY = (TOP + BOT) // 2
CABIN = (X0 + L_SHIP - 30, TOP - 18, X0 + L_SHIP - 4, TOP + 8)      # les finestres i la seva claror
NAV = (X0 + L_SHIP - 23, TOP - 20, X0 + L_SHIP - 11, TOP - 8)       # el llum de navegació (i la seva claror)
RAMP = (X0 + 12, BOT - 6, X0 + 24, BOT)
EXHAUST = (X0 - 6, CY)
COUGHS = (0.2, 1.0, 1.8)
N_APAGA = 44                               # fins que s'ha esvaït el fum de l'última tos
SMOKE = (118, 106, 104)


def _paste(img, src, box):
    x0, y0, x1, y1 = box
    img.paste(src.crop((x0, y0, x1 + 1, y1 + 1)), (x0, y0))


def _puff(cv, age, seed, big):
    life = 2.4 if big else 1.6
    if not 0 <= age < life:
        return
    q = age / life
    for j in range(6 if big else 4):
        bx = EXHAUST[0] - 1 - age * (6 + j) - j * 1.2 + hr(j, seed) * 2
        by = EXHAUST[1] - age * (4 + 1.5 * j) - hr(j, seed + 1) * 2
        r = (2.0 + age * (3.4 if big else 2.4)) * (0.7 + 0.5 * hr(j, seed + 2))
        alpha = (1.0 if big else 0.8) * (1 - q) ** 1.1
        for y in range(int(by - r), int(by + r) + 1):
            for x in range(int(bx - r), int(bx + r) + 1):
                d = math.hypot(x - bx, y - by) / max(0.5, r)
                if d < 1:
                    k = alpha * (1 - d * d)
                    if hr(x, y, seed, int(age * 10)) < k * 1.6:
                        _blend(cv, x, y, SMOKE if hr(x, y, seed + 3) > 0.3 else (70, 62, 64), 0.6 + 0.4 * k)


def _nau_frame(t):
    dark = _variant(ship_off=True)
    img = _base().copy()
    cabin_on = t < 0.9 or 1.1 <= t < 1.3
    ramp_on = t < 2.5 or 2.6 <= t < 2.7
    nav_on = t < 0.9
    if not cabin_on:
        _paste(img, dark, CABIN)
    if not nav_on:
        _paste(img, dark, NAV)
    if not ramp_on:
        _paste(img, dark, RAMP)
    cv = Canvas(light=LIGHT, img=img)
    flare = any(0 <= t - c < 0.2 for c in COUGHS)
    if flare:
        cv.flat(*EXHAUST, (255, 220, 150))
        cv.glow(*EXHAUST, 4, (255, 150, 60), 0.5)
    elif t >= COUGHS[-1]:
        cv.flat(*EXHAUST, (60, 46, 44))
    for i, c in enumerate(COUGHS):
        _puff(cv, t - c, 90 + i, big=i == len(COUGHS) - 1)
    return portada.diff(cv.img, force=() if nav_on else (NAV,))


def _nau_apaga():
    return [_nau_frame(i * ZT) for i in range(N_APAGA)]


# ─── L'Iri i la Vet se'n van ────────────────────────────────────────────────
# Baixen per la rampa i agafen el corriol cap a la posta. Les veiem d'esquena, a contrallum: gairebé siluetes.

DUSK_SIL = (26, 18, 24)
IRI = {'hair': (186, 92, 44), 'top': (104, 64, 40), 'legs': (46, 34, 34), 'bun': False}
VET = {'hair': (22, 20, 24), 'top': (48, 78, 136), 'legs': (38, 60, 108), 'bun': True}
RAMP_TOP, RAMP_FOOT = (X0 + 18, BOT + 1), portada.path_xy(0)[:2]
WALK = {'iri': 0.3, 'vet': 1.1}            # quan comença a baixar cadascuna
RAMP_T = 1.0                               # el que triguen a baixar la rampa
V_PATH = 0.17


@functools.lru_cache(maxsize=None)
def _path_u():
    """u del corriol segons el temps (des del peu de la rampa): de lluny, a la pantalla, es mouen més a poc a poc."""
    us, u = [0.0], 0.0
    while u < 1.0:
        sc = portada.path_xy(u)[2]
        u += V_PATH * ZT * (0.18 + sc)
        us.append(min(1.0, u))
    return us


def _where(who, t):
    """→ (x, y, escala, pas, alfa) o None si encara no ha sortit / ja no hi és."""
    tau = t - WALK[who]
    if tau < 0:
        return None
    step = int(tau / 0.2) % 2
    side = -2 if who == 'vet' else 0
    if tau < RAMP_T:
        k = tau / RAMP_T
        x = RAMP_TOP[0] + (RAMP_FOOT[0] - RAMP_TOP[0]) * k + side
        y = RAMP_TOP[1] + (RAMP_FOOT[1] - RAMP_TOP[1]) * k
        return x, y, 1.0, step, min(1.0, tau / 0.3)
    us = _path_u()
    i = int((tau - RAMP_T) / ZT)
    if i >= len(us):
        return None
    u = us[i]
    x, y, sc = portada.path_xy(u)
    alpha = 1.0 if u < 0.85 else max(0.0, 1 - (u - 0.85) / 0.15)
    if alpha <= 0.05:
        return None
    return x + side * sc, y, sc, step, alpha


def _person(cv, p, x, y, sc, step, alpha):
    h = max(2, round(1 + 10 * sc))
    head = max(1, round(h * 0.24))
    torso = max(1, round(h * 0.36))
    legs = max(1, h - head - torso)
    tw = 3 if h >= 7 else 2 if h >= 4 else 1
    x = round(x)
    xl = x - tw // 2
    sil = lambda col, k=0.35: mix(col, DUSK_SIL, k)                        # noqa: E731
    # l'ombra llarga, cap a la càmera (el sol és davant seu)
    for j in range(1, max(2, round(h * 0.5))):
        _blend(cv, x + j // 2, y + j * 0.5, (20, 12, 14), 0.35 * alpha)
    yy = y - legs + 1
    for r in range(legs):                                                   # les cames, que fan passes
        last = r == legs - 1 and legs >= 3
        if tw < 2:
            _blend(cv, x, yy + r, sil(p['legs']), alpha)
            continue
        if not (last and step == 0):
            _blend(cv, xl, yy + r, sil(p['legs']), alpha)
        if not (last and step == 1):
            _blend(cv, xl + tw - 1, yy + r, sil(p['legs']), alpha)
    yt = yy - torso
    for r in range(torso):
        for c in range(tw):
            _blend(cv, xl + c, yt + r, sil(p['top'], 0.3 + 0.1 * c), alpha)
    hw = 2 if h >= 6 else 1
    yh = yt - head
    for r in range(head):
        for c in range(hw):
            _blend(cv, x - (hw // 2) + c, yh + r, sil(p['hair'], 0.25), alpha)
    if p['bun'] and h >= 6:
        _blend(cv, x, yh - 1, sil(p['hair'], 0.25), alpha)
    if h >= 7:                                                              # la vora que encén la posta
        _blend(cv, xl, yt, mix(p['top'], (255, 190, 120), 0.4), alpha * 0.8)
        _blend(cv, x - (hw // 2), yh, mix(p['hair'], (255, 200, 130), 0.4), alpha * 0.8)


CAT, CAT_HI, BIB = (92, 80, 76), (132, 118, 108), (226, 220, 208)
DIU_OUT, DIU_SIT = 3.0, 4.4
DIU_SPOT = (RAMP_TOP[0] + 9, RAMP_TOP[1] + 11)


def _diu(cv, t):
    """En Diu surt a la rampa, baixa i s'asseu al peu, de perfil, mirant cap on se'n van (la cua que va i ve)."""
    if t < DIU_OUT:
        return
    k = _ease((t - DIU_OUT) / (DIU_SIT - DIU_OUT))
    x = round(RAMP_TOP[0] + 4 + (DIU_SPOT[0] - RAMP_TOP[0] - 4) * k)
    y = round(RAMP_TOP[1] + (DIU_SPOT[1] - RAMP_TOP[1]) * k)
    if k < 1:                                                               # caminant, de perfil cap a l'esquerra
        for dx in range(1, 5):
            cv.flat(x + dx, y - 2, CAT)
        cv.flat(x + 2, y - 3, CAT_HI)
        cv.flat(x, y - 3, CAT)                                              # el cap
        cv.flat(x, y - 4, CAT)                                              # l'orella
        cv.flat(x - 1, y - 3, CAT)
        step = int(t / 0.2) % 2
        cv.flat(x + 1 + step, y - 1, CAT)
        cv.flat(x + 4 - step, y - 1, CAT)
        cv.flat(x + 5, y - 3, CAT)                                          # la cua, enlaire
        cv.flat(x + 5, y - 4, CAT)
        return
    for dy in range(1, 4):                                                  # assegut, de perfil
        cv.flat(x + 1, y - dy, CAT)
        cv.flat(x + 2, y - dy, CAT if dy > 1 else CAT_HI)
    cv.flat(x + 3, y - 1, CAT)
    cv.flat(x, y - 2, BIB)                                                  # el pitet blanc
    cv.flat(x, y - 4, CAT)                                                  # el cap
    cv.flat(x + 1, y - 4, CAT_HI)
    cv.flat(x, y - 5, CAT)                                                  # l'orella
    cv.flat(x - 1, y - 4, CAT)
    tail = int(t / 0.4) % 4                                                 # la cua, a terra, que es belluga
    cv.flat(x + 4, y - 1, CAT)
    cv.flat(x + 5, y - 1 - (1 if tail == 1 else 0), CAT)


def _germanes_frame(t):
    cv = _canvas(_variant(ship_off=True))
    people = [(w, _where(w, t)) for w in ('iri', 'vet')]
    people = [(w, s) for w, s in people if s]
    for w, (x, y, sc, step, alpha) in sorted(people, key=lambda p: p[1][1]):
        _person(cv, IRI if w == 'iri' else VET, x, y, sc, step, alpha)
    _diu(cv, t)
    # la nau ja és apagada (la capa «nau» de sota): aquí només hi van elles i en Diu
    return portada.diff(cv.img, base=_variant(ship_off=True))


def _germanes_surten():
    n = round((max(WALK.values()) + RAMP_T) / ZT) + len(_path_u()) + 5     # fins que la pols se les ha empassat
    return [_germanes_frame(i * ZT) for i in range(n)]


PROPS = {}

ANIMS = {
    'pols': portada.POLS,
    'llums': portada.LLUMS,
    'pou': {'frames': _empty, 'frameDuration': 1000, 'loop': False, 'zIndex': 2},
    'pou_on': {'frames': lambda: [_pou_frame(f) for f in range(POU_N)], 'frameDuration': round(ZT * 1000),
               'prop': 'pou'},
    'canonada': {'frames': _empty, 'frameDuration': 1000, 'loop': False, 'zIndex': 2},
    'canonada_puja': {'frames': _canonada_puja, 'frameDuration': round(ZT * 1000), 'loop': False,
                      'prop': 'canonada'},
    'canonada_on': {'frames': _canonada_on, 'frameDuration': round(ZT * 1000), 'prop': 'canonada'},
    'nau': {'frames': _empty, 'frameDuration': 1000, 'loop': False, 'zIndex': 2},
    'nau_apaga': {'frames': _nau_apaga, 'frameDuration': round(ZT * 1000), 'loop': False, 'prop': 'nau'},
    'germanes': {'frames': _empty, 'frameDuration': 1000, 'loop': False, 'zIndex': 3},
    'germanes_surten': {'frames': _germanes_surten, 'frameDuration': round(ZT * 1000), 'loop': False,
                        'prop': 'germanes'},
}

GEOMETRIA = {'things': {}, 'spawns': {}}
